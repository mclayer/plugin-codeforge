#!/usr/bin/env bash
# check-bootstrap.sh — Consumer 환경 부트스트랩 정합 진단 (non-blocking).
#
# CFP-103 (Phase 2a of CFP-96 Epic) — Python core thin wrapper.
# Implementation SSOT: check_bootstrap.py (cross-platform).
# 기존 4 check (CFP-11/86/89/97) + 신규 4 check (CFP-103) 모두 Python 측 처리.
#
# Skip 조건 (silent):
#   - python3 부재
#   - check_bootstrap.py 부재
#   - .claude/_overlay/project.yaml 부재 (Python 측에서 자체 처리)

set -u

if ! command -v python3 >/dev/null 2>&1; then
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CORE="$SCRIPT_DIR/check_bootstrap.py"

if [ ! -f "$PYTHON_CORE" ]; then
    exit 0
fi

python3 "$PYTHON_CORE"
exit 0  # always non-blocking
