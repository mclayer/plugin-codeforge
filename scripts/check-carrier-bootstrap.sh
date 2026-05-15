#!/usr/bin/env bash
# CFP-407 / ADR-062 — carrier Story bootstrap dependency mechanical lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_carrier_bootstrap.py SSOT)
# Usage / exit code / semantics 상세: scripts/lib/check_carrier_bootstrap.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 인자 있을 시 호출자 cwd 기준 경로 해석.
# 인자 없을 시 codeforge repo root 로 이동 후 docs/stories/ glob.
if [ "$#" -eq 0 ]; then
    cd "$SCRIPT_DIR/.."
fi
exec python3 "$SCRIPT_DIR/lib/check_carrier_bootstrap.py" "$@"
