#!/usr/bin/env bash
# CFP-2966 Phase 2 / ADR-178 §결정 7 — negative-control presence lint (금지 form 재유입 검사) thin wrapper.
# ADR-061 §결정 1 — thin wrapper (scripts/lib/check_adr178_forbidden_form_presence.py SSOT)
#
# 검사: archive/adr/ADR-178-subagent-progress-commit-preservation.md 의
#       progress-commit-normative-region 안(forbidden-form-quotation 블록 제외)에
#       ADR 인용 절이 선언한 FORBIDDEN_TOKENS(closed set 4 리터럴)가 재유입됐는지 검사.
# Usage / exit code / 정직 한계 상세: scripts/lib/check_adr178_forbidden_form_presence.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_adr178_forbidden_form_presence.py" "$@"
