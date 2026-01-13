def on_vault_apply(vault_output, *, glyph_renderer):
    if glyph_renderer is None:
        raise RuntimeError('glyph_renderer implementation is required')
    if vault_output is None:
        raise RuntimeError('vault_output is required')

    glyphs = glyph_renderer(vault_output)
    if glyphs is None:
        raise RuntimeError('glyph_renderer returned no glyphs')

    vault_output['trace'] = glyphs
    return vault_output


def generate_glyphs(output):
    raise RuntimeError('generate_glyphs must be implemented with a real renderer')