from typing import Dict, List
import numpy as np

REQUIRED_CORES = ["ucm_core", "kaygee", "caleon", "cali_x"]
DIM = 512


class CoreEmissionError(RuntimeError):
    pass


def _validate_core_payload(v: Dict) -> None:
    # Required keys
    for k in ("core", "verdict", "confidence", "competency_vector", "recommended_path"):
        if k not in v:
            raise CoreEmissionError(f"Missing field: {k}")

    if v["core"] not in REQUIRED_CORES:
        raise CoreEmissionError(f"Unknown core: {v['core']}")

    if not isinstance(v["verdict"], str) or not v["verdict"].strip():
        raise CoreEmissionError("verdict must be non-empty string")

    conf = float(v["confidence"])
    if not (0.0 <= conf <= 1.0) or not np.isfinite(conf):
        raise CoreEmissionError("confidence must be finite in [0,1]")

    vec = np.asarray(v["competency_vector"], dtype=float).reshape(-1)
    if vec.shape[0] != DIM or not np.isfinite(vec).all() or np.linalg.norm(vec) == 0:
        raise CoreEmissionError("competency_vector invalid (dim/finite/non-zero)")

    if not isinstance(v["recommended_path"], str) or not v["recommended_path"].strip():
        raise CoreEmissionError("recommended_path must be non-empty string")


def collect_and_emit(core_outputs: List[Dict]) -> List[Dict]:
    """
    Collects exactly four core verdicts, validates, and returns the payload.
    Aborts the cycle if any core is missing or invalid.
    """
    if not isinstance(core_outputs, list):
        raise CoreEmissionError("core_outputs must be a list")

    seen = {}
    for v in core_outputs:
        _validate_core_payload(v)
        seen[v["core"]] = v

    missing = set(REQUIRED_CORES) - set(seen.keys())
    if missing:
        raise CoreEmissionError(f"Missing cores: {sorted(missing)}")

    # Deterministic order
    return [seen[c] for c in REQUIRED_CORES]
