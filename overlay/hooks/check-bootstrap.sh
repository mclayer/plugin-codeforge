#!/usr/bin/env bash
# check-bootstrap.sh — Consumer 환경 부트스트랩 정합 진단 (non-blocking).
#
# CFP-11 end-to-end 실증에서 발견된 환경 drift 자동 검출:
#   1. org-level "Workflow permissions" 설정 — workflow의 PR auto-create에 필요
#   2. 18 plugin label 존재 — Issue Form 제출에 필요
#
# Non-blocking: 발견된 drift는 WARN으로만 출력. SessionStart hook을 fail시키지 않음.
# Manual run으로도 사용 가능: bash overlay/hooks/check-bootstrap.sh
#
# Skip 조건:
#   - gh CLI 미설치 (CLAUDE.md 필수 의존성, regen-agents.sh가 별도로 안내)
#   - gh auth status 실패 (DocsAgent도 막히므로 별도 안내)
#   - .claude/_overlay/project.yaml 없음 (consumer 초기 설정 단계)

set -u

# 위치별 OVERLAY_PROJECT_YAML — regen-agents.sh와 동일한 resolution
OVERLAY_PROJECT_YAML="${OVERLAY_PROJECT_YAML:-.claude/_overlay/project.yaml}"

# Fail-fast on missing prereqs (silent — 다른 hook이 안내)
if ! command -v gh >/dev/null 2>&1; then
    exit 0
fi

if ! gh auth status >/dev/null 2>&1; then
    exit 0
fi

if [ ! -f "$OVERLAY_PROJECT_YAML" ]; then
    exit 0
fi

# Python + PyYAML로 org/repo 추출 (validate_config.py와 동일 의존)
ORG_REPO=$(python3 - "$OVERLAY_PROJECT_YAML" <<'PYEOF' 2>/dev/null
import sys, yaml
try:
    with open(sys.argv[1]) as f:
        data = yaml.safe_load(f) or {}
    gh = data.get("github", {})
    print(f"{gh.get('org', '')}|{gh.get('repo', '')}")
except Exception:
    pass
PYEOF
)
ORG="${ORG_REPO%%|*}"
REPO="${ORG_REPO##*|}"

if [ -z "$ORG" ] || [ -z "$REPO" ]; then
    exit 0
fi

WARN_COUNT=0
WARN_MESSAGES=()

# Check 1: Workflow permissions (repo-level effective setting)
PERM_JSON=$(gh api "repos/$ORG/$REPO/actions/permissions/workflow" 2>/dev/null || echo "")
if [ -n "$PERM_JSON" ]; then
    DEFAULT_PERM=$(echo "$PERM_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin).get('default_workflow_permissions', ''))" 2>/dev/null)
    CAN_APPROVE=$(echo "$PERM_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin).get('can_approve_pull_request_reviews', False))" 2>/dev/null)

    if [ "$DEFAULT_PERM" != "write" ] || [ "$CAN_APPROVE" != "True" ]; then
        WARN_COUNT=$((WARN_COUNT + 1))
        WARN_MESSAGES+=("[bootstrap] WARN: Workflow permissions 미설정 (default=$DEFAULT_PERM, can_approve=$CAN_APPROVE)")
        WARN_MESSAGES+=("           → consumer-guide §2f 참조: 'Allow GitHub Actions to create and approve pull requests' 활성화")
        WARN_MESSAGES+=("           → 미해결 시 story-init.yml의 PR auto-create step이 fail")
    fi
fi

# Check 2: Plugin 18 label 존재
EXISTING_LABELS=$(gh label list --limit 100 --repo "$ORG/$REPO" --json name -q '[.[].name] | sort | unique' 2>/dev/null || echo "[]")
REQUIRED_LABELS=(
    "type:epic" "type:story" "type:bug" "impl-manifest"
    "phase:요구사항" "phase:설계" "phase:설계-리뷰" "phase:구현"
    "phase:구현-리뷰" "phase:구현-테스트" "phase:보안-테스트"
    "gate:design-review-pass" "gate:security-test-pass"
    "fix:설계-리뷰-retry" "fix:구현-리뷰-retry"
    "fix:구현-테스트-retry" "fix:보안-테스트-retry"
    "audit:post-hotfix"
)

MISSING_LABELS=()
for lbl in "${REQUIRED_LABELS[@]}"; do
    if ! echo "$EXISTING_LABELS" | grep -Fq "\"$lbl\""; then
        MISSING_LABELS+=("$lbl")
    fi
done

if [ ${#MISSING_LABELS[@]} -gt 0 ]; then
    WARN_COUNT=$((WARN_COUNT + 1))
    WARN_MESSAGES+=("[bootstrap] WARN: ${#MISSING_LABELS[@]}/18 plugin label 부재")
    if [ ${#MISSING_LABELS[@]} -le 5 ]; then
        WARN_MESSAGES+=("           누락: ${MISSING_LABELS[*]}")
    else
        WARN_MESSAGES+=("           누락 상위 5: ${MISSING_LABELS[*]:0:5} ...")
    fi
    WARN_MESSAGES+=("           → 'bash scripts/bootstrap-labels.sh' 1회 실행 (또는 consumer-guide §2d 참조)")
    WARN_MESSAGES+=("           → 미해결 시 Issue Form 제출 시 'label not found' 에러")
fi

# Check 3: workflow_distribution.mode=degraded 시 missing_workflows 안내 (CFP-95 / CFP-89 활성화)
WORKFLOW_DIST=$(python3 - "$OVERLAY_PROJECT_YAML" <<'PYEOF' 2>/dev/null
import sys, yaml
try:
    with open(sys.argv[1]) as f:
        data = yaml.safe_load(f) or {}
    wd = data.get("workflow_distribution", {})
    mode = wd.get("mode", "full")
    missing = wd.get("missing_workflows", []) or []
    print(f"{mode}|{','.join(missing)}")
except Exception:
    pass
PYEOF
)
WD_MODE="${WORKFLOW_DIST%%|*}"
WD_MISSING="${WORKFLOW_DIST##*|}"

if [ "$WD_MODE" = "degraded" ]; then
    WARN_COUNT=$((WARN_COUNT + 1))
    WARN_MESSAGES+=("[bootstrap] WARN: workflow_distribution.mode=degraded (CFP-86 Path B)")
    if [ -n "$WD_MISSING" ]; then
        WARN_MESSAGES+=("           Missing workflows: $WD_MISSING")
    fi
    WARN_MESSAGES+=("           → consumer-guide §2c 'Path A vs Path B' 표 manual compensating check 의무")
    WARN_MESSAGES+=("           → Path B 사용 사례: mctrader-hub (story-init / fix-ledger-sync / subissue-from-impl-manifest / story-section-1-immutable 부재)")
    WARN_MESSAGES+=("           → Path A upgrade: 'cp \${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/<missing>.yml .github/workflows/'")
fi

# 결과 출력
if [ $WARN_COUNT -gt 0 ]; then
    {
        echo ""
        echo "[check-bootstrap] $WARN_COUNT 부트스트랩 drift 발견 (non-blocking):"
        printf '%s\n' "${WARN_MESSAGES[@]}"
        echo ""
    } >&2
fi

exit 0
