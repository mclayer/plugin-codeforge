#!/usr/bin/env bash
# CFP-1497 / Wave 2-C of CFP-1389 (Sub-CFP C CFP-1435 mechanical wire)
# ADR-082 Amendment 17 §결정 1 layer 1 sub-scope (1-G) amendment-slot pre-reservation
# strict claim mandate + ADR-050 §결정 1 ADR-RESERVATION carrier cross-ref
# ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_amendment_slot_reservation.py SSOT)
# ADR-060 §결정 5 — warning-tier (exit 0 항상 for warnings, PR merge 미차단)
#
# Amendment-slot reservation mechanical lint.
# Detection scope:
#   Check (a) — Amendment append (frontmatter amendment_id N entry) without matching
#     `amendments_reserved[]` row in ADR-RESERVATION.md → [WARN-MISSING-RESERVATION]
#   Check (b) — Concurrent reservation conflict (same (adr_number, amendment_id) slot
#     reserved 2+ times in same PR) → [WARN-CONCURRENT-CONFLICT]
#
# Bypass channel: HOTFIX_BYPASS_AMENDMENT_SLOT_RESERVATION=1 env
#   → 즉시 exit 0 (hotfix-bypass:amendment-slot-reservation label 부착 시 workflow 에서 주입)
#
# 검증 대상 file 수집 (check-spawn-prompt-head-pin.sh collect_files 패턴 답습):
#   CI: GITHUB_BASE_REF 환경변수 기반 git diff --name-only origin/${base}...HEAD
#   로컬: staged (--cached) + unstaged (HEAD) 합산 후 sort -u
#   명시 인수: 인수 목록 그대로 사용
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier)
#   1 — malformed 감지 (genuine lint error)
#   2 — setup error (git 미설치 등)
set -euo pipefail

SCRIPT_NAME="[amendment-slot-reservation-lint]"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS="${HOTFIX_BYPASS_AMENDMENT_SLOT_RESERVATION:-}"
if [[ "$BYPASS" == "1" ]]; then
  echo "$SCRIPT_NAME BYPASS=1 — skip" >&2
  exit 0
fi

# ── 공유 helper source (CFP-2061-S6) ─────────────────────────────────────────
# shellcheck source=lib/collect_changed_files.sh
source "${SCRIPT_DIR}/lib/collect_changed_files.sh"

# ── 메인: 파일 수집 후 Python SSOT 호출 ──────────────────────────────────────
main() {
  local files=()
  mapfile -t files < <(collect_changed_files '^docs/adr/ADR-[0-9].*\.md$' "$@")

  if [[ "${#files[@]}" -eq 0 ]]; then
    echo "$SCRIPT_NAME INFO: 검증 대상 ADR file 없음 (변경 없음 또는 docs/adr/ADR-*.md 미포함)" >&2
    exit 0
  fi

  # Python SSOT 위임 (exit-code passthrough)
  exec python3 "$SCRIPT_DIR/lib/check_amendment_slot_reservation.py" "${files[@]}"
}

main "$@"
