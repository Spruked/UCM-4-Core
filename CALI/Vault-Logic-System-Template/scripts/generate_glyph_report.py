import json
import sys


def generate_glyph_report(trace_file, *, renderer):
    if renderer is None:
        raise RuntimeError("renderer implementation is required to generate glyph report")

    with open(trace_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rendered = renderer(data)
    if rendered is None:
        raise RuntimeError("renderer returned no output")

    return rendered


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python generate_glyph_report.py <trace_file>")

    def _stdout_renderer(payload):
        print(json.dumps(payload, indent=2))
        return payload

    generate_glyph_report(sys.argv[1], renderer=_stdout_renderer)