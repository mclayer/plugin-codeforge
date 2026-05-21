#!/usr/bin/env bash
# CFP-1117-S3 / ADR-091 §결정 5 + §결정 6 — Bounded Context presence mechanical lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_bounded_context_presence.py SSOT)
#
# scope: document-level bounded_context 명시 검증 (ddd-pattern-frontmatter-check 와 disjoint axis).
#        Story file §ubiquitous_language + Change Plan + ADR (DDD 영역 touching) 안 bounded_context
#        declaration presence. wrapper-local 자족 (별 repo 의존 0).
# Usage / exit code / semantics 상세: scripts/lib/check_bounded_context_presence.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_bounded_context_presence.py" "$@"
