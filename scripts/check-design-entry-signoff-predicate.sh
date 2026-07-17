#!/usr/bin/env bash
# CFP-2725 Phase 2 / Change Plan §8 RTM AC-5 — design-entry sign-off predicate presence lint
#   (advisory/warning tier, wrapper-self 전용). ADR-061 §결정 1 — thin wrapper
#   (scripts/lib/check_design_entry_signoff_predicate.py SSOT).
#
# 검사: docs/orchestrator-playbook.md 에 설계 진입 preflight 확정 predicate 배선
#       (`user-final-sign-off-resolved` + `advisory ceiling`) presence.
# target-existence guard (부재=exit 1, vacuous PASS 금지) + hollow-gate guard 상세 = Python header.
# advisory ceiling: presence 는 testable, user actually confirmed 는 NOT testable (over-claim 금지).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command -v python3 >/dev/null 2>&1 || {
  echo "::error::check-design-entry-signoff-predicate: python3 미설치 (setup-error, exit 2)"
  exit 2
}
exec python3 "$SCRIPT_DIR/lib/check_design_entry_signoff_predicate.py" "$@"
