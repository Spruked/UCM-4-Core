from typing import Protocol, Dict, Any
import numpy as np


class ASRProvider(Protocol):
    def transcribe(self, audio: bytes, sample_rate: int) -> Dict[str, Any]:
        """Must return {'source': str, 'content': str} or raise."""
        ...


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> np.ndarray:
        """Must return finite vector (non-zero) or raise."""
        ...
