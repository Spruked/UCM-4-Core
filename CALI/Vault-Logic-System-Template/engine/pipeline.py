from .evaluator import query_memory, compute_drift
from .glyph_renderer import generate_glyphs
from ..memory.consolidation import consolidate


def run_pipeline(memory, embedding, attention_weights, trace):
    memories = query_memory(memory, embedding)
    drift = compute_drift(attention_weights)
    glyph = generate_glyphs(trace)
    pack = consolidate(memories)
    return {"memories": memories, "drift": drift, "glyph": glyph, "pack": pack}
