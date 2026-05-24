#!/usr/bin/env bash
# scripts/check-issue-design-content-confluence-link.sh
# CFP-1421 / ADR-111 §결정 5 — Issue body design content Confluence anchor link 의무 lint
#
# Scope: PR open / Issue create 시 GitHub body 안 design doc 4 mirror 대상
#        (ADR / Living Architecture / Change Plan / Domain Knowledge) 참조 시
#        Confluence anchor link 동반 grep-presence 검증.
# Tier: warning (ADR-060 §결정 5 — 첫 도입 = warning mode)
# Bypass: hotfix-bypass:issue-design-content-confluence-link label (ADR-024 Amendment 3 §결정 6.A)
#
# Detection regex:
#   - Design content inline indicator: (?:ADR-\d+|docs/architecture|docs/change-plans|docs/domain-knowledge)
#   - Confluence link presence: mclayer\.atlassian\.net|atlassian\.net/wiki
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = clean OR warning detected (warning-tier — PR merge 미차단)
#   1 = genuinely malformed input (json parse error 등)
#   2 = setup error (python3 부재 등)
#
# Usage:
#   bash scripts/check-issue-design-content-confluence-link.sh                 # GH_TOKEN + ISSUE_NUMBER env mode
#   bash scripts/check-issue-design-content-confluence-link.sh --body-file FILE  # local file mode
#   bash scripts/check-issue-design-content-confluence-link.sh --help
#
# Env:
#   GH_TOKEN         - gh CLI 인증 (필수, GH API mode)
#   ISSUE_NUMBER     - Issue / PR number (필수, GH API mode)
#   GH_REPO          - org/repo (optional, gh CLI default fallback)
#
# ADR-061 §결정 1: Python 외부 파일 분리 (로직 25+ lines, heredoc 회피)

set -uo pipefail

# 스크립트 디렉토리 기준 경로 결정 (worktree 호환, CFP-1408 cd + relative path pattern)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PY_SCRIPT="$SCRIPT_DIR/lib/check_issue_design_content_confluence_link.py"

# python3 필수 확인
if ! command -v python3 >/dev/null 2>&1; then
    echo "[SETUP-ERROR] python3 not found — required for issue-design-content-confluence-link check" >&2
    echo "Install python3 or skip with hotfix-bypass:issue-design-content-confluence-link label." >&2
    exit 2
fi

# Python 구현 파일 존재 확인
if [[ ! -f "$PY_SCRIPT" ]]; then
    echo "[SETUP-ERROR] Python implementation not found: $PY_SCRIPT" >&2
    exit 2
fi

cd "$REPO_ROOT"
exec python3 "$PY_SCRIPT" "$@"
