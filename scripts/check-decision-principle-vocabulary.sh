#!/usr/bin/env bash
# CFP-449 / ADR-060 / ADR-064 — Decision principle forbid-list vocabulary mechanical lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_decision_principle_vocabulary.py SSOT)
#
# 검증 대상: 8 forbid-list 어휘 detection in 5 scope 영역
# Usage / exit code / semantics 상세: scripts/lib/check_decision_principle_vocabulary.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."

if ! command -v python3 >/dev/null 2>&1; then
    echo "check-decision-principle-vocabulary: python3 미설치 (meta-error)" >&2
    exit 2
fi

exec python3 "$SCRIPT_DIR/lib/check_decision_principle_vocabulary.py" "$@"
