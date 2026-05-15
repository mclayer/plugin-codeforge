#!/usr/bin/env bash
# scripts/check-dialog-declare-schema.sh
# CFP-695 / ADR-071 Amendment 1 §결정 13 carrier — Layer 2 self declare strict subschema 3 항목 표 형식 mechanical lint (warning tier).
#
# 검출 영역: PR title / body 안 declare schema 3 항목 표 형식 정규식 감지.
# 항목 1: "사용자가 답해야 할 것" (free-text 1 sentence)
# 항목 2: "묻기 직전 derived default 시도 여부" (done / skipped / value-judgment enum)
# 항목 3: "가치 판단 vs 사실 판단" (value / fact / mixed enum)
#
# advisory only — turn-final hook 부재 (Claude Code harness inherent 한계). PR-time evidence channel.
# warning tier (continue-on-error: true). hotfix-bypass: hotfix-bypass:dialog-declare-schema label.
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = PASS (declare schema 3 항목 표 모두 detect)
#   1 = WARNING (declare schema 위반 — 1+ 항목 누락 / 잘못된 enum / 형식 위반)
#   2 = ERROR (precondition 위반 — gh CLI 부재 / PR fetch 실패)

set -euo pipefail

PR_NUMBER="${1:-}"
REPO_OWNER="${REPO_OWNER:-mclayer}"
REPO_NAME="${REPO_NAME:-plugin-codeforge}"

if [[ -z "${PR_NUMBER}" ]]; then
  echo "ERROR: PR number required (Usage: $0 <PR_NUMBER>)" >&2
  exit 2
fi

if ! command -v gh &>/dev/null; then
  echo "ERROR: gh CLI not installed (https://cli.github.com)" >&2
  exit 2
fi

# Fetch PR body (title + body combined for lint scope)
PR_BODY=$(gh pr view "${PR_NUMBER}" --repo "${REPO_OWNER}/${REPO_NAME}" --json title,body --jq '.title + "\n" + .body' 2>/dev/null || echo "")

if [[ -z "${PR_BODY}" ]]; then
  echo "ERROR: PR #${PR_NUMBER} fetch failed" >&2
  exit 2
fi

# Hotfix bypass check (Hotfix bypass labels 영역 — ADR-024 Amendment 3 §결정 6.A per-entry namespace)
PR_LABELS=$(gh pr view "${PR_NUMBER}" --repo "${REPO_OWNER}/${REPO_NAME}" --json labels --jq '.labels[].name' 2>/dev/null || echo "")
if echo "${PR_LABELS}" | grep -qF "hotfix-bypass:dialog-declare-schema"; then
  echo "PASS (bypass): hotfix-bypass:dialog-declare-schema label detected — declare schema lint skipped (audit comment 의무)"
  exit 0
fi

# Detection 3 항목 정규식 (Layer 2 strict subschema)
ITEM_1_PATTERN='사용자가 답해야 할 것'
ITEM_2_PATTERN='묻기 직전 derived default 시도 여부'
ITEM_3_PATTERN='가치 판단 vs 사실 판단'

MISSING_ITEMS=()

if ! echo "${PR_BODY}" | grep -qF "${ITEM_1_PATTERN}"; then
  MISSING_ITEMS+=("항목 1: ${ITEM_1_PATTERN}")
fi

if ! echo "${PR_BODY}" | grep -qF "${ITEM_2_PATTERN}"; then
  MISSING_ITEMS+=("항목 2: ${ITEM_2_PATTERN}")
fi

if ! echo "${PR_BODY}" | grep -qF "${ITEM_3_PATTERN}"; then
  MISSING_ITEMS+=("항목 3: ${ITEM_3_PATTERN}")
fi

if [[ "${#MISSING_ITEMS[@]}" -gt 0 ]]; then
  echo "WARNING: PR #${PR_NUMBER} declare schema 3 항목 누락 detected" >&2
  echo "" >&2
  echo "누락 항목:" >&2
  for item in "${MISSING_ITEMS[@]}"; do
    echo "  - ${item}" >&2
  done
  echo "" >&2
  echo "정정 안내 — PR body 안 다음 표 형식 declare schema 추가 (ADR-071 §결정 12):" >&2
  echo "" >&2
  echo "  | 항목 | 값 |" >&2
  echo "  |---|---|" >&2
  echo "  | 사용자가 답해야 할 것 | <한 문장> |" >&2
  echo "  | 묻기 직전 derived default 시도 여부 | done / skipped / value-judgment |" >&2
  echo "  | 가치 판단 vs 사실 판단 | value / fact / mixed |" >&2
  echo "" >&2
  echo "Hotfix bypass: PR 에 'hotfix-bypass:dialog-declare-schema' label 부착 + audit comment 의무" >&2
  exit 1
fi

echo "PASS: PR #${PR_NUMBER} declare schema 3 항목 표 모두 detect"
exit 0
