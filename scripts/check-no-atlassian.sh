#!/usr/bin/env bash
# 검사: atlassian 잔재가 코드베이스에 남아 있는가
# 허용 위치 (allowlist): CHANGELOG / migration-guide / 본 마이그레이션 spec·plan·script 자체
set -euo pipefail

cd "$(dirname "$0")/.."

ALLOWLIST=(
  "CHANGELOG.md"
  "docs/migration-guide.md"
  "docs/orchestrator-playbook.md"
  "docs/superpowers/specs/2026-04-25-atlassian-to-github-migration-design.md"
  "docs/superpowers/plans/2026-04-25-atlassian-to-github-migration.md"
  "docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md"
  "docs/superpowers/plans/2026-04-28-cfp-26-phase-0a-write-permission-redistribution.md"
  "docs/superpowers/plans/2026-04-28-cfp-27-phase-0b-lint-strengthening-and-ci-integration.md"
  "docs/superpowers/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md"
  "docs/superpowers/plans/2026-04-28-cfp-29-phase-1-codeforge-review-extract.md"
  "docs/superpowers/plans/2026-04-29-cfp-32-foundation-invariant-ssot.md"
  "scripts/check-no-atlassian.sh"
)

# atlassian|Confluence|Jira|mcp__atlassian 패턴 grep
HITS=$(grep -rEn 'atlassian|Confluence|Jira|mcp__atlassian' \
  --include='*.md' --include='*.yml' --include='*.yaml' --include='*.json' \
  --exclude-dir='.git' --exclude-dir='node_modules' --exclude-dir='.venv' \
  . 2>/dev/null || true)

if [[ -z "$HITS" ]]; then
  echo "✓ atlassian 잔재 없음"
  exit 0
fi

# allowlist 필터
FILTERED=$(echo "$HITS" | while IFS= read -r line; do
  file="${line%%:*}"
  file="${file#./}"
  ALLOWED=false
  for allow in "${ALLOWLIST[@]}"; do
    if [[ "$file" == "$allow" ]]; then ALLOWED=true; break; fi
  done
  if ! $ALLOWED; then echo "$line"; fi
done)

if [[ -z "$FILTERED" ]]; then
  echo "✓ atlassian 잔재는 allowlist 파일에만 존재"
  exit 0
fi

echo "✗ atlassian 잔재 발견 (allowlist 외):"
echo "$FILTERED"
exit 1
