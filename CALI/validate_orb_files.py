#!/usr/bin/env python3
"""Validator for Floating Assistant Orb file integrity."""
import sys
from pathlib import Path


def validate_orb_files() -> bool:
    """Ensure orb exists at canonical path and exposes required methods."""
    project_root = Path(__file__).parent.resolve()

    orb_path = project_root / "Orb_Assistant" / "Orb" / "floating_assistant_orb.py"

    if not orb_path.exists():
        print(f"ERROR: Orb not found at {orb_path}", file=sys.stderr)
        return False

    try:
        sys.path.insert(0, str(project_root))
        from Orb_Assistant.Orb.floating_assistant_orb import CALIFloatingOrb  # type: ignore

        required_methods = ["start", "stop", "get_status"]
        missing = [m for m in required_methods if not hasattr(CALIFloatingOrb, m)]
        if missing:
            print(f"ERROR: Missing required method(s): {', '.join(missing)}", file=sys.stderr)
            return False

        print(f"✓ Orb validated at {orb_path}")
        return True
    except Exception as exc:  # pragma: no cover - defensive
        print(f"ERROR: Failed to import orb: {exc}", file=sys.stderr)
        return False


if __name__ == "__main__":
    sys.exit(0 if validate_orb_files() else 1)
