#!/usr/bin/env bash
# CFP-1117-S3 / ADR-091 §결정 5 + §결정 6 — DDD pattern frontmatter mechanical lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_ddd_pattern_frontmatter.py SSOT)
#
# scope: ArchitectLane agent file (codeforge-design plugin = 별 repo) frontmatter 의
#        `bounded_context` + `ddd_pattern` field presence + enum membership 검증.
#        design plugin CI 또는 wrapper-가-design-clone 시 path-parameterized 호출.
# Usage / exit code / semantics 상세: scripts/lib/check_ddd_pattern_frontmatter.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 인자 미제공 시 default = sibling design plugin clone agents/ (wrapper repo 옆 clone 가정)
if [ "$#" -eq 0 ]; then
  cd "$SCRIPT_DIR/.."
fi
exec python3 "$SCRIPT_DIR/lib/check_ddd_pattern_frontmatter.py" "$@"
