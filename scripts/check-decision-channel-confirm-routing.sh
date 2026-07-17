#!/usr/bin/env bash
# CFP-2725 Phase 2 / Change Plan §8 RTM AC-6 — 원격 결정 채널 최종 확정 routing presence lint
#   (advisory/warning tier, wrapper-self 전용). ADR-061 §결정 1 — thin wrapper
#   (scripts/lib/check_decision_channel_confirm_routing.py SSOT).
#
# 검사: skills/jira-decision-channel/SKILL.md 에 design-entry 확정 payload + terminal routing 배선
#       (`최종 확정 payload` + `user-final-confirmation-driven`) presence.
# target-existence guard (부재=exit 1, vacuous PASS 금지) + hollow-gate guard 상세 = Python header.
# advisory ceiling: presence 는 testable, user actually confirmed 는 NOT testable (over-claim 금지).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command -v python3 >/dev/null 2>&1 || {
  echo "::error::check-decision-channel-confirm-routing: python3 미설치 (setup-error, exit 2)"
  exit 2
}
exec python3 "$SCRIPT_DIR/lib/check_decision_channel_confirm_routing.py" "$@"
