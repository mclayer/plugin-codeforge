#!/usr/bin/env bash
# scripts/check-wording-ssot.sh — ADR-068 §결정 5 wording SSOT mechanical lint
# Story §3/§7 enum identifier · method name 추출 → impl source ripgrep 매칭
# Warning-tier evidence-enforceable (ADR-060). Hotfix bypass: hotfix-bypass:boundary-wording.
# Usage: bash scripts/check-wording-ssot.sh <story-file-path>
# Exit codes: 0=PASS or SKIP / 1=WARNING (enum mismatch found, advisory only)
set -euo pipefail

STORY_FILE="${1:-}"
if [[ -z "$STORY_FILE" || ! -f "$STORY_FILE" ]]; then
  echo "[wording-ssot-lint] Story file not provided or not found — skip"
  exit 0
fi

# Extract enum-like identifiers (UPPER_SNAKE_CASE, 4+ chars) from §3/§7
# awk 로 §3 / §7 섹션 범위 추출 후 UPPER_SNAKE_CASE 패턴 grep
ENUMS=$(awk '/^## §3 /,/^## §[0-9]/ { print }; /^## §7 /,/^## §[0-9]/ { print }' "$STORY_FILE" \
  | grep -oE '\b[A-Z][A-Z0-9_]{3,}\b' | sort -u || true)

if [[ -z "$ENUMS" ]]; then
  echo "[wording-ssot-lint] no enum-like identifier found in §3/§7 — skip"
  exit 0
fi

IDENTIFIER_COUNT=$(echo "$ENUMS" | wc -l | tr -d ' ')
MISSING=()

for token in $ENUMS; do
  if ! git grep -q -- "$token" -- 'src/' 'scripts/' 2>/dev/null; then
    MISSING+=("$token")
  fi
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo "[wording-ssot-lint] WARNING — enum/method identifier present in Story §3/§7 but not in source (src/ scripts/):"
  printf '  - %s\n' "${MISSING[@]}"
  echo "[wording-ssot-lint] Tier: warning (advisory only — continue-on-error: true)"
  echo "[wording-ssot-lint] Hotfix bypass label: hotfix-bypass:boundary-wording"
  echo "[wording-ssot-lint] ADR ref: ADR-068 §결정 5 (wording SSOT invariant I-4)"
  exit 1
fi

echo "[wording-ssot-lint] PASS — ${IDENTIFIER_COUNT} identifiers verified across §3/§7 ↔ source"
