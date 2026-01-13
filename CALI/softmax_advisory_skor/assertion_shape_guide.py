#!/usr/bin/env python3
"""
Assertion Shape Guide (guiderail, not gatekeeper)

Purpose: Make assertion shape visible without blocking or repairing it.
Behavior:
- Never mutates payloads
- Never coerces missing fields
- Returns a visibility summary so callers can log/learn

Contract (minimal):
  required: assertion (string), confidence (float 0..1)
  optional: core_name (string), assertion_id (string), timestamp (ISO-8601), metadata (dict)

If required fields are absent, the guide reports a non-conforming assertion;
callers may skip ingestion but should log the reason for learning/attribution.
"""

from typing import Any, Dict, Optional, Tuple


def observe_assertion_shape(payload: Any) -> Tuple[bool, str, Dict[str, Any]]:
    """Inspect payload shape and return (is_conforming, reason, hints).

    This is a guiderail: it surfaces divergence; it never blocks or repairs.
    """

    hints: Dict[str, Any] = {}

    if not isinstance(payload, dict):
        return False, "non_conforming assertion: not a JSON object", hints

    assertion_present = _has_string(payload, "assertion") or _has_string(payload, "verdict") or _has_string(payload, "status") or _has_string(payload, "response")
    confidence_present = _has_number(payload, "confidence") or _has_number(payload.get("final_verdict", {}), "confidence") or _has_number(payload.get("final_verdict", {}), "probability") or _has_number(payload.get("final_verdict", {}).get("meta", {}), "confidence")

    if not assertion_present and not confidence_present:
        return False, "non_conforming assertion: missing assertion and confidence", hints
    if not assertion_present:
        return False, "non_conforming assertion: missing assertion", hints
    if not confidence_present:
        return False, "non_conforming assertion: missing confidence", hints

    # Optional visibility hints
    for key in ("core_name", "assertion_id", "timestamp"):
        if key in payload:
            hints[key] = payload[key]

    return True, "conforming assertion", hints


def _has_string(obj: Any, key: str) -> bool:
    try:
        val = obj.get(key)
        return isinstance(val, str) and val.strip() != ""
    except Exception:
        return False


def _has_number(obj: Any, key: str) -> bool:
    try:
        val = obj.get(key)
        float(val)
        return True
    except Exception:
        return False
