import hashlib
import json


def consolidate(entries):
    if not entries:
        raise RuntimeError("Consolidation: no entries")
    blob = json.dumps(entries, sort_keys=True, default=str).encode()
    return {"hash": hashlib.sha256(blob).hexdigest(), "count": len(entries)}