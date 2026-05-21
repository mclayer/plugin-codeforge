#!/usr/bin/env bash
# scripts/check-schema-7-principles.sh
# CFP-1059-S6 §3.3 — ADR-089 7 원칙 self-check (ADR-068 I-5 dimensional grounding)
#
# ADR-089 §결정 1 7 원칙:
#   원칙 1: backward-compatible 우선 (additive 우선, drop 후속)
#   원칙 2: 단방향 변경 (한 PR 안 add+drop 동시 금지)
#   원칙 3: compatibility window 유지 (bidirectional-smoke 분담)
#   원칙 4: fail-loud (silent fallback 차단)
#   원칙 5: rollback path 명시
#   원칙 6: empirical evidence (ADR-068 I-5)
#   원칙 7: hard limit 명시 (column 100+ / row 1억+ / lock 5분+ / depth 7+)
#
# ADR-061: multi-line Python 로직 = 외부 .py 의무
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_PY="${SCRIPT_DIR}/check_schema_7_principles.py"

echo "=== check-schema-7-principles.sh ==="
echo "ADR-089 §결정 1 + ADR-068 I-5 dimensional grounding"

if [[ -f "${CHECK_PY}" ]]; then
  PYTHONUTF8=1 python3 "${CHECK_PY}" "$@"
else
  echo "[ERROR] check_schema_7_principles.py 부재 — ADR-061 Python 로직 파일 필요" >&2
  exit 1
fi
