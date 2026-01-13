"""
Entry point to run the Core4Bridge FastAPI app with real providers.
All dependencies are required; absence will raise immediately.

Environment variables (authoritative):
  CORE4_ASR_PROVIDER      -> "module.submod:factory_callable" returning ASRProvider instance
  CORE4_EMBEDDER_PROVIDER -> "module.submod:factory_callable" returning EmbeddingProvider instance
  CORE4_EMBED_DIM         -> integer dimension of embedding vectors
  CORE4_POM_PROVIDER      -> optional "module.submod:factory_callable" returning UvulaController

Example run (PowerShell):
  $env:CORE4_ASR_PROVIDER="my_asr.whisper:build"
  $env:CORE4_EMBEDDER_PROVIDER="my_embedder.local:build"
  $env:CORE4_EMBED_DIM="512"
  uvicorn core4_superintelligence.start_bridge:app --host 0.0.0.0 --port 8000
"""

import importlib
import os
from typing import Callable

from .bridge.core4_bridge import Core4Bridge


def _load_callable(path: str) -> Callable:
    if ":" not in path:
        raise RuntimeError(f"Provider path must be module:callable, got {path}")
    module_name, func_name = path.split(":", 1)
    module = importlib.import_module(module_name)
    factory = getattr(module, func_name)
    if not callable(factory):
        raise RuntimeError(f"Provider factory {path} is not callable")
    return factory


def _require_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Missing required env var: {key}")
    return val


# Load required providers
asr_factory = _load_callable(_require_env("CORE4_ASR_PROVIDER"))
embed_factory = _load_callable(_require_env("CORE4_EMBEDDER_PROVIDER"))
embed_dim = int(_require_env("CORE4_EMBED_DIM"))

asr_provider = asr_factory()
embedder_provider = embed_factory()

bridge = Core4Bridge(asr_provider, embedder_provider, embed_dim)

# Optional POM binding
pom_path = os.getenv("CORE4_POM_PROVIDER")
if pom_path:
    pom_factory = _load_callable(pom_path)
    pom_instance = pom_factory()
    bridge.uvula_controller = pom_instance

app = bridge.app
