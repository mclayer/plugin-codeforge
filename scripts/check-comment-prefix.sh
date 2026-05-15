#!/usr/bin/env bash
# CFP-33 (ζ arc F2) — Comment prefix registry self-validation
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_comment_prefix.py SSOT)
#
# 검사: comment-prefix-registry-v1.md 의 yaml block 유효성
# Usage / exit code / semantics 상세: scripts/lib/check_comment_prefix.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_comment_prefix.py" "$@"
