#!/usr/bin/env bash
# CFP-841 / ADR-082 Amendment 1 §결정 6 scope(d) — cross-plugin ownership verify thin bash wrapper
# ADR-061: multi-line Python 외부 .py 로 위임 (thin bash wrapper 역할만)
# Usage: bash scripts/check-cross-plugin-ownership-verify.sh [--check-4way-sync] [file ...]
# Exit: 0=PASS, 1=violation, 2=error

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/check-cross-plugin-ownership-verify.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: check-cross-plugin-ownership-verify.py 를 찾을 수 없습니다: $PYTHON_SCRIPT" >&2
    exit 2
fi

python3 "$PYTHON_SCRIPT" "$@"
