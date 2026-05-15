#!/usr/bin/env bash
# CFP-295 / Issue #313 — domain-knowledge frontmatter + section schema enforcement
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_domain_knowledge_schema.py SSOT)
# Usage / exit code / semantics 상세: scripts/lib/check_domain_knowledge_schema.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_domain_knowledge_schema.py" "$@"
