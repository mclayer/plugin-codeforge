#!/usr/bin/env bash
# test-cfp-478-regression.sh — CFP-478 Phase 2 regression test runner
# ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/test_cfp_478_regression.py SSOT)
#
# 검사: 19 candidate 각각의 thin wrapper + lib SSOT 동작 확인
# Usage / exit code / semantics 상세: scripts/lib/test_cfp_478_regression.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/test_cfp_478_regression.py" "$@"
