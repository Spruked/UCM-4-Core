#!/usr/bin/env bash
set -euo pipefail

# Prevent modifications to locked files and run audit
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

LOCKED_FILES=(
  "Orb_Assistant/Orb/floating_assistant_orb.py"
  "Orb_Assistant/electron/src/orb_skg_manager.py"
)

# Get staged file list (relative to repo root)
STAGED_LIST=$(git diff --cached --name-only --relative)

for file in "${LOCKED_FILES[@]}"; do
  if grep -Fxq "$file" <<< "$STAGED_LIST"; then
    echo "❌ ERROR: Cannot modify locked file: $file"
    echo "Unlock first (if intentional): sudo chattr -i $file && chmod u+w $file"
    exit 1
  fi
done

# Validate orb presence and syntax
ORB_FILE="$PROJECT_ROOT/Orb_Assistant/Orb/floating_assistant_orb.py"

if [[ ! -f "$ORB_FILE" ]]; then
  echo "❌ ERROR: Orb file not found at $ORB_FILE" >&2
  exit 1
fi

python3 -m py_compile "$ORB_FILE"
python3 "$PROJECT_ROOT/validate_orb_files.py"

if [[ -x "./audit_system.sh" ]]; then
  ./audit_system.sh
else
  echo "ℹ️  NOTE: ./audit_system.sh not found or not executable. Skipping audit step."
fi

echo "✅ Pre-commit checks passed"
exit 0
