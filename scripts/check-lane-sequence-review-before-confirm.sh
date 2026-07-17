#!/usr/bin/env bash
# CFP-2725 Phase 2 / Change Plan §8 RTM AC-21 — lane 시퀀스 + review-pass-before-confirm presence lint
#   (advisory/warning tier, wrapper-self 전용). ADR-061 §결정 1 — thin wrapper
#   (scripts/lib/check_lane_sequence_review_before_confirm.py SSOT).
#
# 검사 (2 target): docs/orchestrator-playbook.md (`phase:요구사항-리뷰` + `user-final-sign-off-resolved`) +
#       archive/adr/ADR-159-requirements-lane-enrichment-and-design-entry-signoff.md (`design-entry`) presence.
# target-existence guard (부재=exit 1, vacuous PASS 금지) + hollow-gate guard 상세 = Python header.
# advisory ceiling: presence 는 testable, user actually confirmed 는 NOT testable (over-claim 금지).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command -v python3 >/dev/null 2>&1 || {
  echo "::error::check-lane-sequence-review-before-confirm: python3 미설치 (setup-error, exit 2)"
  exit 2
}
exec python3 "$SCRIPT_DIR/lib/check_lane_sequence_review_before_confirm.py" "$@"
