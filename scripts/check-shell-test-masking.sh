#!/usr/bin/env bash
# scripts/check-shell-test-masking.sh — shell-test exit-masking + mock-seam-무assert lint thin wrapper
#
# CFP-2635 / ADR-060 Amendment 22 (20번째 warning-tier entry) — codeforge 거버넌스 shell self-test
#   코퍼스(scripts/test-*.sh + tests/scripts/*.sh)의 raw `cmd || true` exit-masking + mock-seam env
#   export 후 동반 assertion 부재(false-coverage)를 정적 스캔한다. 정당 `|| true` 3종(+heredoc/comment)
#   오탐 0 (anti-hollow-gate 1급 요건). ADR-119 게이트=ground-truth 정합.
# ADR-061 §결정 1: Python entry-point + thin bash wrapper (python3 exec forward, 로직 0).
#
# Usage / exit code / semantics 상세: scripts/lib/check_shell_test_masking.py header.
#   bash scripts/check-shell-test-masking.sh [--repo-root DIR]
#     0 = PASS (위반 0 또는 대상 부재 no-op) / 1 = FLAG 1+ (warning) / 2 = usage error.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-shell-test-masking-infra-error] check-shell-test-masking: python3 not installed" >&2
  exit 2
}

exec python3 "$SCRIPT_DIR/lib/check_shell_test_masking.py" "$@"
