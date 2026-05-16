#!/usr/bin/env bash
# test_cfp750_treaty_invariance.sh — INV-T2 advisory helper (CFP-750 / ADR-064 Amendment 5)
#
# 목적: Phase 2 `박제` sweep 이 docs/inter-plugin-contracts/ 영역에서 prose 층만
#       변경하고 schema 층 (yaml frontmatter / markdown 표 row / fenced code block)
#       + contract version 은 불변임을 advisory 로 검증.
#
# 근거: Change Plan §4.2 R6 (contract semantic 의도 미보존) + §8.0 INV-T2 + §8.1 #6.
#       parallel-dispatch-protocol-v1 / reconcile-protocol-v1 / review-verdict-v4 등은
#       prose 층 치환만 허용 — schema 변경 시 sibling sync drift (ADR-010) /
#       contract version bump 오발 (ADR-008) risk.
#
# Exit code: 0 = invariant 충족 (prose hunk only) 또는 contract 영역 변경 0,
#            1 = schema 층 변경 감지 (advisory warning — PR 차단 안 함, warning tier)
#
# 측정 base: git merge-base 기준 HEAD diff (Phase 2 PR 전체 변경 surface).
#            base 산정 불가 시 origin/main fallback → HEAD~1 fallback.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT" || { echo "repo root cd 실패: $REPO_ROOT" >&2; exit 1; }

CONTRACT_DIR="docs/inter-plugin-contracts"

if [ ! -d "$CONTRACT_DIR" ]; then
  echo "treaty-invariance: $CONTRACT_DIR 없음 — 검증 대상 0, exit 0"
  exit 0
fi

# diff base 산정 (Phase 2 PR 전체 sweep surface).
BASE=""
if git rev-parse --verify --quiet origin/main >/dev/null 2>&1; then
  BASE="$(git merge-base origin/main HEAD 2>/dev/null || echo "")"
fi
if [ -z "$BASE" ]; then
  BASE="$(git rev-parse --verify --quiet HEAD~1 2>/dev/null || echo "")"
fi
if [ -z "$BASE" ]; then
  echo "treaty-invariance: diff base 산정 불가 (shallow / initial commit) — advisory skip, exit 0"
  exit 0
fi

# contract 영역 변경 hunk 추출 (unified diff, working tree + staged + committed 포함).
DIFF="$(git diff "$BASE" -- "$CONTRACT_DIR" 2>/dev/null; git diff --cached "$BASE" -- "$CONTRACT_DIR" 2>/dev/null)"

if [ -z "$DIFF" ]; then
  echo "treaty-invariance: $CONTRACT_DIR 변경 0 — INV-T2 충족 (prose hunk only, vacuously), exit 0"
  exit 0
fi

# schema 층 변경 감지 (Change Plan §6.4 verbatim — "contract field name / enum value /
# invariant 절 row 변경 0", NOT every table-row prose edit):
#   (a) yaml frontmatter version 키 (schema_version: / version:) 추가/삭제
#   (b) fenced code block delimiter (^[+-]\s*```) 추가/삭제 (코드 블록 hunk)
#   (c) 표 row 의 first-cell 식별자 (field/enum/invariant 명) 집합 변경
#       — first cell = 첫 `|` 와 둘째 `|` 사이 token. prose-only 치환은 first cell 불변
#         이므로 set diff = 0 (description cell 내부 어휘 치환 = prose-layer, 허용).

# (a) + (b): version key / fenced delimiter
SCHEMA_AB="$(printf '%s\n' "$DIFF" \
  | grep -E '^[+-]' \
  | grep -Ev '^(\+\+\+|---)' \
  | grep -E '^[+-][[:space:]]*(schema_version:|version:|```)' \
  || true)"

# (c): 표 row first-cell 식별자 집합 비교 (removed vs added).
#   각 표 row 의 첫 cell 만 추출 (선두 [+-] 제거 후 '|' split 의 첫 non-empty field).
#   awk 로 '|' literal split (regex-special `+`/`-` sign 문제 회피).
extract_first_cells() {
  local sign="$1"   # '+' 또는 '-' (literal char, awk substr 비교 — regex 미사용)
  printf '%s\n' "$DIFF" \
    | awk -v s="$sign" '
        substr($0,1,1)==s {
          body=substr($0,2)                 # 선두 부호 제거
          sub(/^[ \t]+/,"",body)            # 선행 공백 trim
          if (substr(body,1,1)!="|") next   # 표 row 아님
          n=split(body,parts,"|")           # | literal split
          if (n<2) next
          cell=parts[2]                     # 첫 cell (parts[1]=빈 문자열)
          gsub(/^[ \t]+|[ \t]+$/,"",cell)
          if (cell=="" || cell ~ /^[ \t:|-]+$/) next  # 빈 cell / 구분선 row 제외
          print cell
        }' \
    | sort
}
REMOVED_CELLS="$(extract_first_cells '-')"
ADDED_CELLS="$(extract_first_cells '+')"
TABLE_IDENT_DIFF="$(comm -3 <(printf '%s\n' "$REMOVED_CELLS") <(printf '%s\n' "$ADDED_CELLS") 2>/dev/null | grep -v '^[[:space:]]*$' || true)"

if [ -n "$SCHEMA_AB" ] || [ -n "$TABLE_IDENT_DIFF" ]; then
  echo "WARNING [treaty-invariance / INV-T2]: $CONTRACT_DIR 영역에 schema 층 변경 감지 (prose hunk only invariant 위반):" >&2
  [ -n "$SCHEMA_AB" ] && { echo "  [version key / fenced code block]" >&2; printf '%s\n' "$SCHEMA_AB" | sed 's/^/    /' >&2; }
  [ -n "$TABLE_IDENT_DIFF" ] && { echo "  [표 row first-cell 식별자 변경 (field/enum/invariant 명)]" >&2; printf '%s\n' "$TABLE_IDENT_DIFF" | sed 's/^/    /' >&2; }
  echo "" >&2
  echo "ADR-064 Amendment 5 §결정 5 의미 보존 sweep — schema (field/enum/invariant/version) 무변경 의무." >&2
  echo "표 description cell 내부 prose 어휘 치환은 허용 (first-cell 식별자 불변 시 INV-T2 충족)." >&2
  echo "contract version bump 필요 시 ADR-008 §2 + sibling sync ADR-010 §결정 2 검토 요망." >&2
  exit 1
fi

echo "treaty-invariance: $CONTRACT_DIR 변경 = prose hunk only — INV-T2 충족, exit 0"
exit 0
