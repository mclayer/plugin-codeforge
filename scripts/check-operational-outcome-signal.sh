#!/usr/bin/env bash
# CFP-2361 PS4 — Operational outcome-signal schema enforcement (warning-tier, non-blocking).
#
# ADR-014 Amendment 7 §7.4.7 + ADR-015 Amendment 1 §8.5.1 compliance check:
# - Presence check: Story 의 §7.4.7 outcome-signal 3요소 (terminal downstream sink /
#   monotone progress metric / 발현조건 임계) 선언 부재 → warning emit.
# - Soak derivation check: Story 의 §8.5.1 에 accumulation/lifetime-class 기재되었는데
#   soak 구동 종점 (manifestation-derived 또는 duration floor) 도출 부재 → warning emit.
#
# **검사 방식 (literal-term presence heuristic)**: 휴리스틱 grep 검사로 문자 존재만 확인.
# 정상 Story (3요소 + soak 도출 완비) 가 해당 용어 포함 시 false-positive 0 목표.
# wrapper-self: operational:true Story 0개 가능 (declarative-only) → graceful exit 0.
#
# Exit code: 0 (always — warning-tier, non-blocking)
# Output: ::warning:: marker to GitHub Actions (no output outside CI).
#
# Usage:
#   bash scripts/check-operational-outcome-signal.sh
#   bash scripts/check-operational-outcome-signal.sh --regen  # (reserved for future markdown regen)
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${1:-.}"
cd "$REPO_ROOT"

# Early guard: docs/stories 디렉터리 부재 시 (wrapper-self or non-consumer) exit 0
[ -d docs/stories ] || {
  exit 0
}

# Find all Story files with operational:true label (no cap — check all)
STORY_FILES=$(find docs/stories -name "*.md" 2>/dev/null || true)
[ -z "$STORY_FILES" ] && {
  # No Story files found, skip gracefully
  exit 0
}

WARNINGS=0

for story_file in $STORY_FILES; do
  # Check if Story has operational:true label/declare in frontmatter or body
  if ! grep -q "operational:\s*true" "$story_file" 2>/dev/null; then
    continue  # Non-operational Story, skip
  fi

  # ① outcome-signal presence check (§7.4.7):
  # Check for all 3 elements in §7.4.7 section
  if ! grep -q "terminal downstream sink" "$story_file" 2>/dev/null && \
     ! grep -q "sink 경로" "$story_file" 2>/dev/null; then
    echo "::warning file=$story_file::§7.4.7 outcome-signal ① terminal downstream sink 미선언 (operational:true Story 필수)"
    WARNINGS=$((WARNINGS+1))
  fi

  if ! grep -q "monotone progress metric" "$story_file" 2>/dev/null && \
     ! grep -q "단조 증가 metric" "$story_file" 2>/dev/null; then
    echo "::warning file=$story_file::§7.4.7 outcome-signal ② monotone progress metric 미선언 (operational:true Story 필수)"
    WARNINGS=$((WARNINGS+1))
  fi

  if ! grep -q "발현조건 임계" "$story_file" 2>/dev/null && \
     ! grep -q "manifestation-derived" "$story_file" 2>/dev/null; then
    echo "::warning file=$story_file::§7.4.7 outcome-signal ③ 발현조건 임계 미선언 (operational:true Story 필수)"
    WARNINGS=$((WARNINGS+1))
  fi

  # ② soak derivation check (§8.5.1):
  # If §8.5 mentions accumulation/lifetime-class, must declare soak derivation
  if grep -q "accumulation" "$story_file" 2>/dev/null || \
     grep -q "lifetime-class" "$story_file" 2>/dev/null || \
     grep -q "장기-수명" "$story_file" 2>/dev/null; then

    # Check for soak manifestation-derived or duration floor
    if ! grep -q "manifestation-derived" "$story_file" 2>/dev/null && \
       ! grep -q "발현조건 기반 도출" "$story_file" 2>/dev/null && \
       ! grep -q "duration floor" "$story_file" 2>/dev/null && \
       ! grep -q "최소 지속" "$story_file" 2>/dev/null; then
      echo "::warning file=$story_file::§8.5.1 soak 구동 종점 (manifestation-derived 또는 duration floor) 도출 부재 (accumulation/lifetime-class 기재 시 필수)"
      WARNINGS=$((WARNINGS+1))
    fi
  fi
done

# Exit 0 always (warning-tier, non-blocking)
exit 0
