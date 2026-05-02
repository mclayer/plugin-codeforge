#!/usr/bin/env bash
# CFP-60 ADR-021 — debut-audit phase-gap measurable signal detection
# Mechanical detection of 4 rules (R1-R4) for #2 카테고리 (agent-gap).
#
# Usage: bash scripts/check-debut-audit-signals.sh <story-file-path> [<change-plan-path>] [<repo-root>]
#   story-file-path: Story file path (relative or absolute)
#   change-plan-path: Change Plan file path (optional, R2 detection 용)
#   repo-root: optional repo root override (default: pwd)
#
# Output: per-rule line (PASS / WARN / FAIL) + exit code
#   exit 0 = all PASS or WARN only
#   exit 1 = at least 1 FAIL detected

set -euo pipefail

STORY_FILE="${1:-}"
CHANGE_PLAN_FILE="${2:-}"
REPO_ROOT="${3:-$(pwd)}"

if [[ -z "$STORY_FILE" ]]; then
  echo "Usage: $0 <story-file> [<change-plan-file>] [<repo-root>]" >&2
  exit 2
fi

cd "$REPO_ROOT"

FAIL_COUNT=0

# R1 — Missing agent: Story §10 같은 카테고리 finding 반복
r1_check() {
  if [[ ! -f "$STORY_FILE" ]]; then
    echo "R1: SKIP (Story file not found: $STORY_FILE)"
    return 0
  fi
  # Story §10 FIX Ledger 의 트리거 컬럼 (5번째 |) 추출 + 빈도
  local count
  count=$( { grep -E '^\| [0-9]+\s+\|' "$STORY_FILE" 2>/dev/null \
    | awk -F'|' '{print $5}' \
    | sed 's/^ *//; s/ *$//' \
    | sort | uniq -c | sort -rn | head -1 | awk '{print $1}'; } || true)
  count="${count:-0}"
  [[ -z "$count" ]] && count=0
  if [[ "$count" -ge 5 ]]; then
    echo "R1: FAIL ($count 회 반복 — same trigger ≥5)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  elif [[ "$count" -ge 3 ]]; then
    echo "R1: WARN ($count 회 반복 — same trigger ≥3)"
  else
    echo "R1: PASS ($count 회)"
  fi
}

# R2 — Overload: Change Plan §3 / §7 / §11 의 본문 시작 author HTML comment + Story §10 FIX iteration
# ADR-021 결정 6: "§3 / §7 / §11 의 본문 시작 부분에 <!-- author: <agent-name> --> HTML comment"
r2_check() {
  if [[ -z "$CHANGE_PLAN_FILE" || ! -f "$CHANGE_PLAN_FILE" ]]; then
    echo "R2: SKIP (Change Plan not provided)"
    return 0
  fi

  # Extract first author HTML comment within each of §3 / §7 / §11 sections only
  set +e
  section_first_author() {
    local sec_num="$1"
    awk -v sec="^## §${sec_num}( |\$)" '
      $0 ~ sec {found=1; next}
      found && /^## §/ {exit}
      found
    ' "$CHANGE_PLAN_FILE" 2>/dev/null | grep -oE '<!-- author: [^ ]+ -->' | head -1
  }
  local s3_author s7_author s11_author
  s3_author=$(section_first_author 3)
  s7_author=$(section_first_author 7)
  s11_author=$(section_first_author 11)
  set -e

  # Build author occurrence map across §3 / §7 / §11 only
  local -A author_counts=()
  for a in "$s3_author" "$s7_author" "$s11_author"; do
    [[ -n "$a" ]] && author_counts["$a"]=$((${author_counts["$a"]:-0} + 1))
  done

  if [[ "${#author_counts[@]}" -eq 0 ]]; then
    echo "R2: SKIP (no author meta in §3/§7/§11)"
    return 0
  fi

  # Max occurrence count = "1 agent multi-section count"
  local max_sub_per_author=0
  for v in "${author_counts[@]}"; do
    [[ "$v" -gt "$max_sub_per_author" ]] && max_sub_per_author="$v"
  done

  # Story §10 FIX iteration count
  local fix_count
  fix_count=$(grep -cE '^\| [1-9][0-9]*\s+\|' "$STORY_FILE" 2>/dev/null || echo 0)
  fix_count=$(echo "$fix_count" | tr -d '[:space:]')
  [[ -z "$fix_count" ]] && fix_count=0

  if [[ "$max_sub_per_author" -ge 3 && "$fix_count" -ge 3 ]]; then
    echo "R2: FAIL ($max_sub_per_author sub + FIX $fix_count)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  elif [[ "$max_sub_per_author" -ge 2 && "$fix_count" -ge 2 ]]; then
    echo "R2: WARN ($max_sub_per_author sub + FIX $fix_count)"
  else
    echo "R2: PASS ($max_sub_per_author sub + FIX $fix_count)"
  fi
}

# R3 — Phase gap: 동일 finding 이 review→test→security 로 propagate
r3_check() {
  if [[ ! -f "$STORY_FILE" ]]; then
    echo "R3: SKIP"
    return 0
  fi
  # Simple detection: count "[propagate-from-review]" markers in Story
  local propagate
  propagate=$(grep -cE '^- \[propagate-from-review\]' "$STORY_FILE" 2>/dev/null || echo 0)
  propagate="${propagate:-0}"
  # Strip any whitespace/newlines (grep -c can include trailing newline on some platforms)
  propagate=$(echo "$propagate" | tr -d '[:space:]')
  [[ -z "$propagate" ]] && propagate=0
  if [[ "$propagate" -ge 2 ]]; then
    echo "R3: FAIL ($propagate 회 propagate)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  elif [[ "$propagate" -ge 1 ]]; then
    echo "R3: WARN ($propagate 회 propagate)"
  else
    echo "R3: PASS"
  fi
}

# R4 — Responsibility leak: CLAUDE.md 책임 매트릭스 ✅ 0 또는 ≥2 row
r4_check() {
  local claude_md="${REPO_ROOT}/CLAUDE.md"
  if [[ ! -f "$claude_md" ]]; then
    echo "R4: SKIP (CLAUDE.md not found)"
    return 0
  fi
  # disable set -e inside awk pipe loop (grep no-match exits 1)
  set +e
  local leak_count=0
  local matrix_rows
  matrix_rows=$(awk '/^\| 체크 항목/,/^[^|]/' "$claude_md")
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    # header / separator 제외
    case "$line" in
      "| 체크 항목"*|"|---"*) continue ;;
    esac
    # pipe ≥4 검증
    local pipe_count
    pipe_count=$(echo "$line" | tr -cd '|' | wc -c | tr -d ' ')
    [[ "$pipe_count" -lt 4 ]] && continue
    # ✅ count
    local check_count
    check_count=$(echo "$line" | grep -o '✅' | wc -l | tr -d ' ')
    check_count="${check_count:-0}"
    if [[ "$check_count" -eq 0 || "$check_count" -ge 2 ]]; then
      leak_count=$((leak_count + 1))
    fi
  done <<< "$matrix_rows"
  set -e

  if [[ "$leak_count" -ge 2 ]]; then
    echo "R4: FAIL ($leak_count leak rows)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  elif [[ "$leak_count" -ge 1 ]]; then
    echo "R4: WARN ($leak_count leak row)"
  else
    echo "R4: PASS"
  fi
}

# Run all 4 rules
echo "=== CFP-60 debut-audit signals ==="
r1_check
r2_check
r3_check
r4_check
echo "=================================="

if [[ "$FAIL_COUNT" -gt 0 ]]; then
  echo "❌ FAIL ($FAIL_COUNT rule(s))"
  exit 1
else
  echo "✅ PASS (no FAIL)"
  exit 0
fi
