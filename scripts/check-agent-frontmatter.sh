#!/usr/bin/env bash
# 검사: 24 agent md의 frontmatter `permissions:` 블록에 atlassian MCP 도구가 0건인가
set -euo pipefail

cd "$(dirname "$0")/.."

FAIL=0
for f in agents/*.md; do
  # frontmatter 추출 (첫 ---와 두 번째 --- 사이)
  fm=$(awk '/^---$/{c++; next} c==1' "$f" 2>/dev/null || true)
  if echo "$fm" | grep -qE 'mcp__atlassian__'; then
    echo "✗ $f frontmatter에 atlassian MCP 도구 있음:"
    echo "$fm" | grep -E 'mcp__atlassian__' | sed 's/^/    /'
    FAIL=1
  fi
done

if [[ $FAIL -eq 0 ]]; then
  echo "✓ 모든 agent frontmatter에서 atlassian MCP 도구 0건"
fi
exit $FAIL
