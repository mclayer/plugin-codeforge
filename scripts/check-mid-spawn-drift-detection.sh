#!/usr/bin/env bash
# CFP-1500 / Wave 2-B of CFP-1389 (Sub-CFP B CFP-1436 mechanical wire)
# ADR-082 Amendment 16 §결정 1 layer 1 sub-scope (1-F) spawn-internal periodic
# origin re-pin protocol + ADR-073 Amendment 12 paired sibling
# ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper
# (scripts/lib/check_mid_spawn_drift_detection.py SSOT)
# ADR-060 §결정 5 — warning-tier (exit 0 항상 for warnings, PR merge 미차단)
#
# Mid-spawn drift detection mechanical lint.
# Detection scope:
#   Check (a) — agent spawn entry mid-spawn drift directive presence (PRIMARY):
#     same entry block 안 `mid_spawn_drift_check_executed: <bool>` field OR
#     `drift_check_directive_present: true` marker presence 검증
#     → 부재 시 [WARN-DIRECTIVE-ABSENT]
#   Check (b) — long-duration spawn (≥ 5 min) `drift_detected:` return packet flag presence
#     → 누락 시 [WARN-RETURN-PAYLOAD-INCOMPLETE]
#
# Bypass channel: HOTFIX_BYPASS_MID_SPAWN_DRIFT_DETECTION=1 env
#   → 즉시 exit 0 (hotfix-bypass:mid-spawn-drift-detection label 부착 시 workflow 에서 주입)
#
# 검증 대상 file 수집 (check-amendment-slot-reservation.sh collect_files 패턴 답습):
#   CI: GITHUB_BASE_REF 환경변수 기반 git diff --name-only origin/${base}...HEAD
#   로컬: staged (--cached) + unstaged (HEAD) 합산 후 sort -u
#   명시 인수: 인수 목록 그대로 사용
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier)
#   1 — malformed 감지 (genuine lint error, currently unused)
#   2 — setup error (git 미설치 등)
set -euo pipefail

SCRIPT_NAME="[mid-spawn-drift-detection-lint]"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS="${HOTFIX_BYPASS_MID_SPAWN_DRIFT_DETECTION:-}"
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
  mapfile -t files < <(collect_changed_files '^docs/stories/.*\.md$' "$@")

  if [[ "${#files[@]}" -eq 0 ]]; then
    echo "$SCRIPT_NAME INFO: 검증 대상 Story file 없음 (변경 없음 또는 docs/stories/**/*.md 미포함)" >&2
    exit 0
  fi

  # Python SSOT 위임 (exit-code passthrough)
  exec python3 "$SCRIPT_DIR/lib/check_mid_spawn_drift_detection.py" "${files[@]}"
}

main "$@"
