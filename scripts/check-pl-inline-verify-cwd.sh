#!/usr/bin/env bash
# CFP-1341 / CFP-1316 retro F1 Mandatory carrier
# ADR-040 Amendment 6 §결정 7.J PL inline scope mechanical enforcement gap closure
# ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_pl_inline_verify_cwd.py SSOT)
# ADR-060 §결정 5 — warning-tier (exit 0 always for warnings, PR merge 미차단)
#
# pl-inline-verify-cwd-mandate-lint — Lane PL spawn prompt 안 inline 명령
# cwd directive enforcement mechanical lint (warning-tier).
#
# Bypass channel: HOTFIX_BYPASS_PL_INLINE_VERIFY_CWD_MANDATE=1 env
#   → 즉시 exit 0 (hotfix-bypass:pl-inline-verify-cwd-mandate label 부착 시
#     workflow 에서 주입)
#
# Detection scope:
#   변경된 Story file (docs/stories/**/*.md) §14 Lane Evidence 안에서
#   Lane PL spawn marker 발견 시 ±20 line window 안 cwd directive (3 forms)
#   presence 검사. 3 form 모두 부재 → [WARN-CWD-DIRECTIVE-ABSENT].
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier — exit 0 always)
#   1 — genuinely malformed (현재 0건 가능)
#   2 — setup error (python3 미설치 등)
set -euo pipefail

SCRIPT_NAME="[pl-inline-verify-cwd-mandate-lint]"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS="${HOTFIX_BYPASS_PL_INLINE_VERIFY_CWD_MANDATE:-}"
if [[ "$BYPASS" == "1" ]]; then
  echo "$SCRIPT_NAME BYPASS=1 — skip" >&2
  exit 0
fi

# ── python3 presence ─────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "$SCRIPT_NAME ERROR: python3 미설치 (환경 오류)" >&2
  exit 2
fi

# ── delegate to Python SSOT ──────────────────────────────────────────────────
PY_LIB="$SCRIPT_DIR/lib/check_pl_inline_verify_cwd.py"
if [[ ! -f "$PY_LIB" ]]; then
  echo "$SCRIPT_NAME ERROR: SSOT script not found ($PY_LIB)" >&2
  exit 2
fi

exec python3 "$PY_LIB" "$@"
