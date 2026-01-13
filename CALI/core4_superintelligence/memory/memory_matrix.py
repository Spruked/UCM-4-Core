# memory_matrix.py
import numpy as np
from typing import List, Dict

class MemoryMatrix:
    """Unified memory accessible by all four cores"""
    
    def __init__(self, dim: int = 512, max_entries: int = 10000):
        self.dim = dim
        self.max_entries = max_entries
        self.entries: List[Dict] = []
        self.attention_heads = 8

    def update(self, context: np.ndarray, verdict: Dict, attention_weights: np.ndarray) -> Dict:
        """Store new memory with provided attention weights. No placeholders."""

        if context is None or not isinstance(context, np.ndarray):
            raise RuntimeError("context is required for memory update")
        if context.shape[0] != self.dim:
            raise RuntimeError(f"context must have dim={self.dim}, got {context.shape}")
        if not np.isfinite(context).all():
            raise RuntimeError("context contains non-finite values")

        if verdict is None:
            raise RuntimeError("verdict is required for memory update")

        if attention_weights is None or not isinstance(attention_weights, np.ndarray):
            raise RuntimeError("attention_weights are required for memory update")
        if attention_weights.size == 0:
            raise RuntimeError("attention_weights cannot be empty")
        if np.any(~np.isfinite(attention_weights)):
            raise RuntimeError("attention_weights contain non-finite values")
        if attention_weights.sum() == 0:
            raise RuntimeError("attention_weights sum to zero")

        context_f64 = np.asarray(context, dtype=np.float64)

        entry = {
            'timestamp': len(self.entries),
            'context': context_f64.tobytes(),
            'verdict_hash': hash(str(verdict)),
            'attention_weights': attention_weights.astype(float).tolist(),
        }

        if len(self.entries) >= self.max_entries:
            self.entries.pop(0)

        self.entries.append(entry)

        return {
            'memory_id': len(self.entries) - 1,
            'stored': True,
            'attention_weights': entry['attention_weights']
        }

    def retrieve(self, query: np.ndarray, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant memories; requires valid query."""
        if not self.entries:
            return []

        if query is None or not isinstance(query, np.ndarray):
            raise RuntimeError("query vector is required for retrieval")
        if query.shape[0] != self.dim:
            raise RuntimeError(f"query must have dim={self.dim}, got {query.shape}")
        if not np.isfinite(query).all():
            raise RuntimeError("query contains non-finite values")

        scores = []
        for idx, entry in enumerate(self.entries):
            context_vec = np.frombuffer(entry['context'], dtype=np.float64)
            denom = (np.linalg.norm(query) * np.linalg.norm(context_vec))
            if denom == 0:
                continue
            score = float(np.dot(query, context_vec) / denom)
            scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in scores[:top_k]]

        return [self.entries[i] for i in top_indices]