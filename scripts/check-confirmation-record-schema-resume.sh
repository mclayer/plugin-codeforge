#!/usr/bin/env bash
# CFP-2725 Phase 2 / Change Plan §8 RTM AC-7 — 확정 기록 schema + 세션 재개 복원 presence lint
#   (advisory/warning tier, wrapper-self 전용). ADR-061 §결정 1 — thin wrapper
#   (scripts/lib/check_confirmation_record_schema_resume.py SSOT).
#
# 검사 (2 target): templates/story-page-structure.md (`확정 발화 verbatim` + `양채널 mirror`) +
#       skills/session-recovery/SKILL.md (`확정 상태 복원` + `미해소 질문 목록`) presence.
# target-existence guard (부재=exit 1, vacuous PASS 금지) + hollow-gate guard 상세 = Python header.
# advisory ceiling: presence 는 testable, user actually confirmed 는 NOT testable (over-claim 금지).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command -v python3 >/dev/null 2>&1 || {
  echo "::error::check-confirmation-record-schema-resume: python3 미설치 (setup-error, exit 2)"
  exit 2
}
exec python3 "$SCRIPT_DIR/lib/check_confirmation_record_schema_resume.py" "$@"
