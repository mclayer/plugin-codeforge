#!/usr/bin/env bash
# CFP-1117-S3 / ADR-091 §결정 4 + §결정 6 — Ubiquitous Language drift mechanical lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_ubiquitous_language.py SSOT)
#
# scope: docs/glossary.md (codeforge governance BC Published Language SSOT) term presence verify
#        + Story file §ubiquitous_language ddd_terms enumeration ↔ glossary anchor drift detection.
#        glossary 외 미정의 DDD term 사용 = warning. wrapper-local 자족.
# Usage / exit code / semantics 상세: scripts/lib/check_ubiquitous_language.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_ubiquitous_language.py" "$@"
