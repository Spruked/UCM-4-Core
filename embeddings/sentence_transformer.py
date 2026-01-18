import numpy as np
from sentence_transformers import SentenceTransformer


class LocalEmbedder:
    def __init__(self, model="all-mpnet-base-v2"):
        self.model = SentenceTransformer(model)

    def embed(self, text: str) -> np.ndarray:
        vec = self.model.encode(text, normalize_embeddings=True)
        if not np.isfinite(vec).all():
            raise RuntimeError("Embedding contains non-finite values")
        return vec


def build_embedder():
    return LocalEmbedder()
