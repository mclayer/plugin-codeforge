#!/usr/bin/env bash
# bootstrap-codeforge-family.sh — 7 codeforge family repo 의 label set 일괄 bootstrap (CFP-120).
#
# 사용 사례: codeforge family 신규 setup 또는 lane plugin label drift 발견 시.
#
# 본 스크립트는 wrapper 의 bootstrap-labels.sh 를 7 repo (wrapper + 6 lane) 에 차례로 호출.
# 각 호출은 idempotent — 기존 라벨은 skip.
#
# Usage:
#   gh auth login   # 사전 인증 필요
#   bash scripts/bootstrap-codeforge-family.sh                      # 기본 mclayer org
#   bash scripts/bootstrap-codeforge-family.sh --org <other-org>    # 다른 org (fork 등)
#   bash scripts/bootstrap-codeforge-family.sh --dry-run            # gh 미호출, 호출 명령 stdout 출력만
#
# Exit code: 0 (모두 성공) / 1 (gh 미설치 또는 인증 실패) / 2 (개별 repo 실패 — 로그 확인)

set -u

ORG="mclayer"
DRY_RUN=0

while [ $# -gt 0 ]; do
    case "$1" in
        --org) ORG="$2"; shift 2 ;;
        --dry-run) DRY_RUN=1; shift ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

if [ $DRY_RUN -eq 0 ] && ! command -v gh >/dev/null 2>&1; then
    echo "gh CLI not installed" >&2
    exit 1
fi
if [ $DRY_RUN -eq 0 ] && ! gh auth status >/dev/null 2>&1; then
    echo "gh CLI not authenticated — run 'gh auth login'" >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LABELS_SCRIPT="$SCRIPT_DIR/bootstrap-labels.sh"
if [ ! -f "$LABELS_SCRIPT" ]; then
    echo "bootstrap-labels.sh not found at $LABELS_SCRIPT" >&2
    exit 1
fi

REPOS=(
    "plugin-codeforge"
    "plugin-codeforge-requirements"
    "plugin-codeforge-design"
    "plugin-codeforge-review"
    "plugin-codeforge-develop"
    "plugin-codeforge-test"
    "plugin-codeforge-pmo"
)

FAILED=()
for repo in "${REPOS[@]}"; do
    full="$ORG/$repo"
    echo "=== bootstrap labels for $full ==="
    if [ $DRY_RUN -eq 1 ]; then
        echo "  (dry-run) bash $LABELS_SCRIPT $full"
    else
        if bash "$LABELS_SCRIPT" "$full"; then
            echo "  ✅ $full done"
        else
            echo "  ❌ $full failed (exit $?)"
            FAILED+=("$full")
        fi
    fi
done

echo ""
if [ ${#FAILED[@]} -gt 0 ]; then
    echo "FAILED ${#FAILED[@]} repo(s):"
    printf '  %s\n' "${FAILED[@]}"
    exit 2
fi
echo "ALL DONE — 7 codeforge family repos label-bootstrapped (org: $ORG)"
exit 0
