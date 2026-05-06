#!/usr/bin/env bash
# check-bootstrap.sh — Consumer 환경 부트스트랩 정합 진단 (default non-blocking).
#
# CFP-103 (Phase 2a of CFP-96 Epic) — Python core thin wrapper.
# CFP-127 (Phase 2 of CFP-124 Epic) — strict mode opt-in flag passthrough.
# Implementation SSOT: check_bootstrap.py (cross-platform).
#
# Usage:
#   bash check-bootstrap.sh            # default non-blocking (exit 0)
#   bash check-bootstrap.sh --strict   # CFP-127 ADR-032 strict mode opt-in (exit 1 if strict-eligible drift)
#   bash check-bootstrap.sh --quiet    # suppress non-strict warnings
#
# Exit code passthrough from Python core:
#   Default mode: 0 (advisory only)
#   Strict mode + strict-eligible drift 부재: 0
#   Strict mode + 1+ strict-eligible drift: 1 (CFP-127 / ADR-032)
#
# Skip 조건 (silent):
#   - python3 부재
#   - check_bootstrap.py 부재
#   - .claude/_overlay/project.yaml 부재 (default mode silent skip / strict mode → exit 1)

set -u

if ! command -v python3 >/dev/null 2>&1; then
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_CORE="$SCRIPT_DIR/check_bootstrap.py"

if [ ! -f "$PYTHON_CORE" ]; then
    exit 0
fi

# CFP-127 — pass through CLI args (--strict / --quiet) to Python core.
# Default mode (no args) = non-blocking exit 0 (ADR-027 §결정 2 정합).
# Strict mode = Python core 가 exit code 결정 (passthrough).
python3 "$PYTHON_CORE" "$@"
exit $?
