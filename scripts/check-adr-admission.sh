#!/usr/bin/env bash
# CFP-2985 / ADR-181 §결정 5 ③-dt — ADR admission test (warning-first)
# thin wrapper (scripts/lib/check_adr_admission.py SSOT). Usage/exit/semantics 상세 = lib header.
#
# 수용 기준 = ADR-181 §결정 5 ③-dt (iv) 결정표 전 행 (verdict, exit 사유) 전건 재현.
# 재현 산출 = scripts/lib/adr181_table_reproducer.py (--self-test 로 위임).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."

export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"

if [ "${1:-}" = "--self-test" ]; then
  shift
  exec python3 "$SCRIPT_DIR/lib/adr181_table_reproducer.py" "$@"
fi

exec python3 "$SCRIPT_DIR/lib/check_adr_admission.py" "$@"
