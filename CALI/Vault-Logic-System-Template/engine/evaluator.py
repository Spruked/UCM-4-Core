from typing import Dict, Any
import numpy as np


def query_memory(memory, embedding, top_k: int = 5):
    if memory is None or embedding is None:
        raise RuntimeError("Evaluator: missing memory or embedding")
    return memory.retrieve(embedding, top_k=top_k)


def compute_drift(attn_weights: Dict[str, Any]):
    if not attn_weights:
        raise RuntimeError("Evaluator: missing attention weights")
    arr = np.asarray(list(attn_weights.values()), dtype=float)
    if not np.isfinite(arr).all():
        raise RuntimeError("Evaluator: non-finite weights")
    return float(arr.std())