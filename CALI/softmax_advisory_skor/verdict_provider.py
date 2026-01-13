#!/usr/bin/env python3
"""
Core 4 assertion provider (HTTP-driven, no mock data).

This module discovers per-sibling endpoints (via env or config file) and
retrieves assertions for SoftMax aggregation. It intentionally does **not**
invent data: if an endpoint is unreachable or returns unusable payloads,
it simply omits that sibling from the assertion list.

Minimum accepted payload (anything less is ignored, never repaired):
{
    "core_name": "string",
    "assertion": "string",
    "confidence": 0.0-1.0,
    "assertion_id": "string (optional)",
    "timestamp": "ISO-8601 (optional)",
    "metadata": { ... passthrough ... }
}

Silence (no response) and unavailability (failed request) remain distinct.
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import error, request

from softmax_advisory_skor.consensus_advisor import Core4Verdict
from softmax_advisory_skor.assertion_shape_guide import observe_assertion_shape

logger = logging.getLogger("softmax.verdict_provider")


@dataclass
class EndpointConfig:
    core_name: str
    url: str
    method: str = "POST"
    payload_key: str = "query"


def _read_json_file(path: Path) -> Optional[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to read endpoint config %s: %s", path, exc)
        return None


def _load_endpoint_configs(base_path: Optional[Path] = None) -> List[EndpointConfig]:
    """Discover endpoint configs from env or optional config file.

    Priority:
      1) CORE4_VERDICT_ENDPOINTS (JSON string)
      2) CORE4_VERDICT_ENDPOINTS_FILE (path to JSON file)
      3) softmax_core4_endpoints.json in base_path or base_path/CALI
      4) Built-in sane default for ECM (port 8002)
    """

    raw_cfg = os.getenv("CORE4_VERDICT_ENDPOINTS")
    if raw_cfg:
        try:
            data = json.loads(raw_cfg)
            return _parse_config_list(data)
        except Exception as exc:
            logger.warning("Invalid CORE4_VERDICT_ENDPOINTS JSON: %s", exc)

    cfg_file_env = os.getenv("CORE4_VERDICT_ENDPOINTS_FILE")
    if cfg_file_env:
        path = Path(cfg_file_env)
        if path.exists():
            data = _read_json_file(path)
            if data:
                return _parse_config_list(data)

    search_roots = []
    if base_path:
        search_roots.append(Path(base_path))
        search_roots.append(Path(base_path) / "CALI")

    for root in search_roots:
        candidate = root / "softmax_core4_endpoints.json"
        if candidate.exists():
            data = _read_json_file(candidate)
            if data:
                return _parse_config_list(data)

    # Built-in minimal default: ECM FastAPI (see UCM_Core _ECM/main.py)
    default = EndpointConfig(
        core_name="UMC_Core_ECM",
        url=os.getenv("ECM_ENDPOINT", "http://localhost:8002/api/adjudicate"),
        method="POST",
        payload_key="query",
    )
    return [default]


def _parse_config_list(data: Any) -> List[EndpointConfig]:
    configs: List[EndpointConfig] = []
    if not isinstance(data, list):
        logger.warning("Endpoint config must be a list; got %s", type(data))
        return configs
    for item in data:
        try:
            cfg = EndpointConfig(
                core_name=item["core_name"],
                url=item["url"],
                method=item.get("method", "POST").upper(),
                payload_key=item.get("payload_key", "query"),
            )
            configs.append(cfg)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Skipping invalid endpoint config %s: %s", item, exc)
    return configs


def _extract_verdict(core_name: str, payload: Any) -> Optional[Core4Verdict]:
    """Parse an assertion payload without inventing defaults.

    Required: assertion/verdict (string), confidence (0..1). If missing, skip.
    Uses a guiderail observer to surface shape divergence (logged) without repair.
    """

    if not isinstance(payload, dict):
        return None

    chosen_core = str(payload.get("core_name") or core_name)

    is_ok, reason, hints = observe_assertion_shape(payload)
    if not is_ok:
        logger.info("Assertion skipped (%s) from %s", reason, hints.get("core_name", chosen_core))
        return None

    # Attempt to locate assertion/confidence in common shapes
    assertion_value: Optional[str] = None
    confidence_value: Optional[float] = None
    metadata: Dict[str, Any] = {}

    if "assertion" in payload:
        assertion_value = _coerce_string(payload.get("assertion"))
        confidence_value = _coerce_confidence(payload.get("confidence"))
    elif isinstance(payload.get("final_verdict"), dict):
        fv = payload["final_verdict"]
        assertion_value = _coerce_string(
            fv.get("status") or fv.get("verdict") or fv.get("decision")
        )
        confidence_value = _coerce_confidence(
            fv.get("inevitability")
            or fv.get("confidence")
            or fv.get("probability")
            or fv.get("meta", {}).get("confidence")
        )
        metadata["final_verdict"] = fv
    elif "verdict" in payload and "confidence" in payload:
        assertion_value = _coerce_string(payload.get("verdict"))
        confidence_value = _coerce_confidence(payload.get("confidence"))
    elif "status" in payload and "confidence" in payload:
        assertion_value = _coerce_string(payload.get("status"))
        confidence_value = _coerce_confidence(payload.get("confidence"))
    elif "response" in payload and "confidence" in payload:
        assertion_value = _coerce_string(payload.get("response"))
        confidence_value = _coerce_confidence(payload.get("confidence"))

    if assertion_value is None or confidence_value is None:
        return None

    # Preserve optional identifiers/timestamps in metadata without alteration
    for key in ("assertion_id", "timestamp", "metadata"):
        if key in payload:
            metadata[key] = payload[key]

    return Core4Verdict(core_name=chosen_core, verdict=assertion_value, confidence=confidence_value, metadata=metadata)


def _coerce_confidence(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        num = float(value)
        return max(0.0, min(1.0, num))
    except Exception:
        return None


def _coerce_string(value: Any) -> Optional[str]:
    if value is None:
        return None
    try:
        text = str(value).strip()
        return text if text else None
    except Exception:
        return None


def _http_json_request(url: str, method: str, payload: Dict[str, Any], timeout_s: float) -> Optional[Any]:
    data = json.dumps(payload).encode("utf-8") if method != "GET" else None
    req = request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read()
            if not raw:
                return None
            return json.loads(raw.decode("utf-8"))
    except error.URLError as exc:
        logger.warning("Endpoint %s unreachable: %s", url, exc)
        return None
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Endpoint %s returned invalid data: %s", url, exc)
        return None


def http_verdict_provider(decision_context: str, timeout_ms: int = 5000, base_path: Optional[Path] = None) -> List[Core4Verdict]:
    """Collect verdicts from configured HTTP endpoints.

    - Honors timeouts per call
    - Skips endpoints that fail or return unusable payloads
    - Never fabricates verdicts
    """

    endpoints = _load_endpoint_configs(base_path)
    timeout_s = max(0.1, timeout_ms / 1000.0)
    verdicts: List[Core4Verdict] = []

    for ep in endpoints:
        payload = {ep.payload_key: decision_context}
        response = _http_json_request(ep.url, ep.method, payload, timeout_s)
        if response is None:
            continue
        verdict_obj = _extract_verdict(ep.core_name, response)
        if verdict_obj:
            verdicts.append(verdict_obj)

    return verdicts
