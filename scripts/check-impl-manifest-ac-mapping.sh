#!/usr/bin/env bash
# check-impl-manifest-ac-mapping.sh
# CFP-491 — AC mapping cross-ref lint (ADR-060 Amendment 6, 5번째 warning-tier entry)
#
# Carrier ADR: ADR-060 (evidence-enforceable promotion framework)
# CFP:        CFP-491 (F-001 Option C systematization — CFP-451 retro follow-up)
# Scope:      Story file §8.5 Impl Manifest 의 AC id 인용 ↔ §5.1 AC 정의 cross-reference 검증
#             1차 단순화 = §8.5 → §5.1 only (2-way drift detection)
#             3-way (Change Plan §1.3/§3.5/§8.1) = follow-up CFP scope
#
# Exit code 3-tier (ADR-060 Amendment 2 §결정 15):
#   0  PASS  — drift 0건 (또는 기본 mode advisory)
#   1  violation — drift 발견 (--strict mode 또는 향후 enforce)
#   2  meta-error — file 부재 / parsing 실패
#
# Usage:
#   bash scripts/check-impl-manifest-ac-mapping.sh [--strict] [--help|-h] <story-file>...
#
# Examples:
#   bash scripts/check-impl-manifest-ac-mapping.sh docs/stories/CFP-491.md
#   bash scripts/check-impl-manifest-ac-mapping.sh --strict docs/stories/*.md
#
# Bypass:
#   PR에 `hotfix-bypass:ac-mapping` label 부착 + PR description 에 아래 섹션 추가:
#     ### Bypass reason
#     <사유 설명>
#   CI workflow (ac-mapping-cross-ref-check.yml) 가 bypass label 감지 시
#   check-bypass-audit-comment.sh 를 호출해 감사 trail 을 남깁니다.

set -euo pipefail

export LC_ALL=${LC_ALL:-C.UTF-8} 2>/dev/null || true

# ─── argument parsing ────────────────────────────────────────────────────────

STRICT=false
FILES=()

for arg in "$@"; do
  case "$arg" in
    --strict)
      STRICT=true
      ;;
    --help|-h)
      # Print header comment and exit
      sed -n '2,/^set -euo pipefail/{ /^set -euo pipefail/q; s/^# \{0,1\}//p }' "$0"
      exit 0
      ;;
    -*)
      echo "ERROR unknown flag: $arg" >&2
      exit 2
      ;;
    *)
      FILES+=("$arg")
      ;;
  esac
done

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "ERROR no Story file(s) provided." >&2
  echo "Usage: bash $0 [--strict] <story-file>..." >&2
  exit 2
fi

# ─── helper functions ────────────────────────────────────────────────────────

# extract_section_5 <file>
# §5 섹션 전체 본문 추출 (§5.N sub-heading 포함, §6 이상 heading 에서 종료)
# 로직: §5 heading 진입 → §5.N 은 sub-section 으로 계속 포함 → §4 이하 or §6 이상 heading 에서 종료
extract_section_5() {
  local file="$1"
  awk '
    /^#+[[:space:]]/ {
      heading = $0
      sub(/^#+[[:space:]]+/, "", heading)

      if (in_section) {
        # §5.N 은 계속 포함 (sub-section)
        if (heading ~ /^§5[.][0-9]/) {
          print
          next
        }
        # §5 이외 heading → 종료
        exit
      }

      # §5 heading 진입 (§5 / §5.1 등)
      if (heading ~ /^§5([.][0-9]+)?[[:space:]]/ || heading ~ /^§5([.][0-9]+)?$/) {
        in_section = 1
        next
      }
      next
    }
    in_section { print }
  ' "$file"
}

# extract_section_85 <file>
# §8.5 본문 추출 (다음 같은-레벨 heading 에서 종료)
extract_section_85() {
  local file="$1"
  awk '
    /^#+[[:space:]]/ {
      if (in_section) { exit }
      heading = $0
      sub(/^#+[[:space:]]+/, "", heading)
      if (heading ~ /^§8[.][[:space:]]*5[[:space:]]/ || heading ~ /^§8[.][[:space:]]*5$/) {
        in_section = 1
      }
      next
    }
    in_section { print }
  ' "$file"
}

# normalize_ac_ids: stdin 에서 AC id 추출 + normalize (AC-N 형식, 대문자)
normalize_ac_ids() {
  grep -oE '[Aa][Cc][-[:space:]][0-9]+' | \
    sed 's/[[:space:]]/-/g' | \
    tr 'a-z' 'A-Z' | \
    sort -u || true
}

# ─── main loop ───────────────────────────────────────────────────────────────

OVERALL_DRIFT=0

for file in "${FILES[@]}"; do
  # meta-error: file 부재
  if [[ ! -f "$file" ]]; then
    echo "ERROR file not found: $file" >&2
    exit 2
  fi

  # §5 / §5.1 본문 추출
  sec5_text="$(extract_section_5 "$file")"

  # §8.5 본문 추출
  sec85_text="$(extract_section_85 "$file")"

  # AC id 추출 + normalize
  ac_defined="$(echo "$sec5_text" | normalize_ac_ids || true)"
  ac_cited="$(echo "$sec85_text" | normalize_ac_ids || true)"

  # 둘 다 비어있으면 AC 참조 없는 Story → PASS
  if [[ -z "$ac_defined" && -z "$ac_cited" ]]; then
    echo "OK §8.5 → §5.1 AC mapping drift 0건 — PASS (AC 참조 없음): $file"
    continue
  fi

  # §8.5 에 AC 참조 없으면 drift 없음
  if [[ -z "$ac_cited" ]]; then
    echo "OK §8.5 → §5.1 AC mapping drift 0건 — PASS (§8.5 AC 참조 없음): $file"
    continue
  fi

  # comm -23: ac_cited 에 있지만 ac_defined 에 없는 항목 (drift)
  # defined 가 비어있으면 all cited = drift
  drift_ids="$(comm -23 \
    <(echo "$ac_cited") \
    <(echo "${ac_defined:-}") \
    2>/dev/null || true)"

  if [[ -n "$drift_ids" ]]; then
    drift_count="$(echo "$drift_ids" | grep -c '[^[:space:]]' || true)"
    echo "WARN drift ${drift_count} AC(s) cited in §8.5 but undefined in §5.1: $file" >&2
    while IFS= read -r ac_id; do
      [[ -n "$ac_id" ]] && echo "  $ac_id" >&2
    done <<< "$drift_ids"
    echo "" >&2
    echo "  Bypass: PR label 'hotfix-bypass:ac-mapping' + PR description '### Bypass reason'" >&2
    OVERALL_DRIFT=$((OVERALL_DRIFT + drift_count))
  else
    echo "OK §8.5 → §5.1 AC mapping drift 0건 — PASS: $file"
  fi
done

# ─── summary & exit ──────────────────────────────────────────────────────────

if [[ $OVERALL_DRIFT -gt 0 ]]; then
  if [[ "$STRICT" == "true" ]]; then
    echo "FAIL total drift ${OVERALL_DRIFT} AC(s) — --strict mode exit 1" >&2
    exit 1
  else
    # 기본 mode = LLM trust — advisory stderr + exit 0
    echo "ADVISORY total drift ${OVERALL_DRIFT} AC(s) — 기본 mode exit 0 (LLM trust). --strict 사용 시 exit 1." >&2
    exit 0
  fi
fi

echo "OK §8.5 → §5.1 AC mapping drift 0건 — PASS"
exit 0
