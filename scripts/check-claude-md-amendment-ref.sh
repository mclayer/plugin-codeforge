#!/usr/bin/env bash
# scripts/check-claude-md-amendment-ref.sh
# CFP-708 / ADR-074 — CLAUDE.md Amendment ref drift detection lint
#
# Scope: PR-time, warning tier (ADR-060 §결정 5 default)
# Trigger: pull_request paths: [CLAUDE.md, docs/adr/**]
#
# Exit codes:
#   0 = clean (no drift)
#   1 = drift detected (amendment claim > ADR frontmatter amendment_log length)
#   2 = setup error (python3 없음, ADR file 부재, YAML parse error)
#
# Usage:
#   bash scripts/check-claude-md-amendment-ref.sh
#   bash scripts/check-claude-md-amendment-ref.sh --claude-md CLAUDE.md --adr-dir docs/adr
#
# bypass: hotfix-bypass:claude-md-amendment-ref label (workflow level)
# ADR-061 §결정 1: Python 외부 파일 분리 (로직 25+ lines)

set -uo pipefail

# 스크립트 디렉토리 기준 경로 결정 (worktree 호환)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PY_SCRIPT="$SCRIPT_DIR/lib/check_claude_md_amendment_ref.py"

# 기본값
CLAUDE_MD_PATH="${CLAUDE_MD_PATH:-$REPO_ROOT/CLAUDE.md}"
ADR_DIR_PATH="${ADR_DIR_PATH:-$REPO_ROOT/docs/adr}"

# CLI 인수 파싱 (--claude-md, --adr-dir 옵션)
while [[ $# -gt 0 ]]; do
    case "$1" in
        --claude-md)
            CLAUDE_MD_PATH="$2"
            shift 2
            ;;
        --adr-dir)
            ADR_DIR_PATH="$2"
            shift 2
            ;;
        *)
            echo "[ERROR] Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

# python3 필수 확인
if ! command -v python3 &>/dev/null; then
    echo "[SETUP-ERROR] python3 not found — required for CLAUDE.md amendment ref check" >&2
    echo "Install python3 or skip with hotfix-bypass:claude-md-amendment-ref label." >&2
    exit 2
fi

# Python 구현 파일 존재 확인
if [[ ! -f "$PY_SCRIPT" ]]; then
    echo "[SETUP-ERROR] Python implementation not found: $PY_SCRIPT" >&2
    exit 2
fi

# 실제 검사 실행 (Python 위임)
python3 "$PY_SCRIPT" --claude-md "$CLAUDE_MD_PATH" --adr-dir "$ADR_DIR_PATH"
exit $?
