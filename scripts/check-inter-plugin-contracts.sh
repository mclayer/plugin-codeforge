#!/usr/bin/env bash
# CFP-33 (ζ arc F2) — Inter-plugin contract validator
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_inter_plugin_contracts.py SSOT)
#
# 검사: docs/inter-plugin-contracts/** 에서 kind: contract 파일의 frontmatter + 본문 sanity
# Usage / exit code / semantics 상세: scripts/lib/check_inter_plugin_contracts.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_inter_plugin_contracts.py" "$@"
