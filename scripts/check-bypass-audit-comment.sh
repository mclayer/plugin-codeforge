#!/usr/bin/env bash
# CFP-389 / ADR-060 §결정 8 / ADR-024 Amendment 3 — bypass audit comment assertion lint
#
# 검증 대상:
#   hotfix-bypass:<entry-name> label 부착 PR 에 대해 GitHub Actions bot 가 발의한
#   audit comment 1개 이상 존재 여부 검증. 부재 시 PR block (workflow level conditional).
#
# Comment schema (ADR-060 §결정 8 verbatim):
#   [hotfix-bypass-audit] PR=<number> label_applied_by=<user> reason=<bypass_reason_textbox>
#   ADR_files=<comma-separated-paths> timestamp=<ISO8601>
#
# 환경 변수:
#   GITHUB_TOKEN (필수)        — gh CLI 인증
#   PR_NUMBER     (필수)       — 검증 대상 PR number
#   PR_LABELS     (선택)       — comma-separated labels (workflow 가 주입). 부재 시 gh api 로 조회.
#   BYPASS_LABEL_PREFIX (선택)  — bypass label namespace (default `hotfix-bypass:`)
#
# Exit code:
#   0 — bypass label 미부착 (검증 대상 아님) OR bypass label 부착 + audit comment 1+ 존재
#   1 — bypass label 부착 + audit comment 부재 (PR block)
#
# 사용 모드:
#   GitHub Actions workflow step 호출.
#   현재 (CFP-389) = adr-sunset-criteria.yml workflow 내 conditional step 으로 호출.
#
# carrier: ADR-060 §결정 8, ADR-024 Amendment 3 §결정 6.C
set -euo pipefail
cd "$(dirname "$0")/.."

BYPASS_PREFIX="${BYPASS_LABEL_PREFIX:-hotfix-bypass:}"
AUDIT_TAG="[hotfix-bypass-audit]"

if [ -z "${PR_NUMBER:-}" ]; then
    echo "⚠ PR_NUMBER 미설정 — workflow 외 직접 호출 불가 (skip)"
    exit 0
fi

# Labels 추출
if [ -n "${PR_LABELS:-}" ]; then
    labels="$PR_LABELS"
else
    if ! command -v gh >/dev/null 2>&1; then
        echo "⚠ gh CLI 미설치 — PR_LABELS env 주입 필수 (skip)" >&2
        exit 0
    fi
    labels=$(gh pr view "$PR_NUMBER" --json labels --jq '[.labels[].name] | join(",")' 2>/dev/null || echo "")
fi

# bypass label 부착 여부 검사
bypass_attached=false
IFS=',' read -ra LBL_ARR <<< "$labels"
for lbl in "${LBL_ARR[@]}"; do
    lbl_trimmed=$(echo "$lbl" | sed 's/^ *//;s/ *$//')
    case "$lbl_trimmed" in
        ${BYPASS_PREFIX}*)
            bypass_attached=true
            ;;
    esac
done

if [ "$bypass_attached" = "false" ]; then
    echo "✓ PR=#${PR_NUMBER}: bypass label 미부착 — audit assertion 대상 외 (PASS)"
    exit 0
fi

# bypass label 부착 PR — audit comment 1+ 검증
if ! command -v gh >/dev/null 2>&1; then
    echo "⚠ gh CLI 미설치 — audit comment 조회 불가 — bypass label 부착 PR 의 검증 fail-closed (FAIL)" >&2
    exit 1
fi

audit_count=$(gh pr view "$PR_NUMBER" --json comments \
    --jq "[.comments[] | select(.body | startswith(\"${AUDIT_TAG}\"))] | length" 2>/dev/null || echo "0")

if [ "$audit_count" -ge 1 ]; then
    echo "✓ PR=#${PR_NUMBER}: bypass label 부착 + audit comment ${audit_count}건 존재 (PASS)"
    exit 0
else
    echo "⚠ PR=#${PR_NUMBER}: bypass label 부착 but audit comment 부재 (ADR-060 §결정 8 violation)" >&2
    echo "  ADR-024 Amendment 3 §결정 6.C — audit trail 3중 안전망 1차 (audit comment 자동 발의) 미충족" >&2
    exit 1
fi
