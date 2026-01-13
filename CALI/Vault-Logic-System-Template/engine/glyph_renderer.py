import hashlib
from typing import Dict, Any


def generate_glyphs(trace: Dict[str, Any]) -> Dict[str, Any]:
    if not trace:
        raise RuntimeError("Glyph: empty trace")
    seed = hashlib.sha256(str(trace).encode()).hexdigest()[:16]
    return {
        "glyph_id": seed,
        "shape": "sigil",
        "encoding": seed,
    }
