#!/usr/bin/env bash
# CFP-34 (ζ arc F3) — Workflow yaml syntax + regex fixture tests
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_workflow_yaml.py SSOT)
#
# 검사: 3 핵심 workflow의 yaml syntax + 핵심 regex 패턴 존재 + Python re-impl fixture 검증
# Usage / exit code / semantics 상세: scripts/lib/check_workflow_yaml.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_workflow_yaml.py" "$@"
