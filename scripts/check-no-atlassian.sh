#!/usr/bin/env bash
# Atlassian-allow lint — allowlist 외 평문 Atlassian 참조 감지 (warning tier)
# ADR-099 §결정 1/2/3 — check-no-atlassian.sh 역전 (v0.7→v0.8 Atlassian 제거 reversal)
#
# Layer 2 (lint grep 평문 참조 governance):
#   - grep 패턴 = atlassian|Confluence|Jira (평문만 — mcp__atlassian 제거)
#   - allowlist 외 발견 = exit 1 (warning tier, CI 미wire)
#   - Layer 1 (mcp__atlassian permission deny) 은 settings.json SSOT — 본 script 범위 외
set -euo pipefail

cd "$(dirname "$0")/.."

# ── 기존 11-file allowlist (v0.8 Atlassian 제거 history 파일) ─────────────────
ALLOWLIST_FILES=(
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

# ── Epic-A 5-slot governance ADR prefix allowlist (ADR-099 §결정 2) ───────────
# ADR-099~103 파일은 Atlassian 재결합 governance ADR 자체 → 평문 참조 허용
ALLOWLIST_ADR_PREFIXES=(
  "docs/adr/ADR-099"
  "docs/adr/ADR-100"
  "docs/adr/ADR-101"
  "docs/adr/ADR-102"
  "docs/adr/ADR-103"
)

# ── 추가 허용 파일 (Epic-A governance 참조 포함) ──────────────────────────────
# ADR-RESERVATION.md: ADR-099~103 row 기록 (atlassian reversal row 포함)
# ADR-060: check-no-atlassian ADR-060 L860 등록 보류 해소 언급 포함
# docs/evidence-checks-registry.yaml: check-atlassian-allow entry 포함 (본 registry 자체)
ALLOWLIST_EXTRA_FILES=(
  "docs/adr/ADR-RESERVATION.md"
  "docs/adr/ADR-060-evidence-enforceable-promotion-framework.md"
  "docs/evidence-checks-registry.yaml"
)

# ── 평문 atlassian|Confluence|Jira grep (mcp__atlassian 토큰 제거 — Layer 2 only) ─
# Layer 1 (mcp__atlassian permission deny) 은 settings.json 책임
HITS=$(grep -rEn 'atlassian|Confluence|Jira' \
  --include='*.md' --include='*.yml' --include='*.yaml' --include='*.json' \
  --exclude-dir='.git' --exclude-dir='node_modules' --exclude-dir='.venv' \
  . 2>/dev/null || true)

if [[ -z "$HITS" ]]; then
  echo "✓ Atlassian-allow: 평문 참조 없음 (OK)"
  exit 0
fi

# ── allowlist 필터 ────────────────────────────────────────────────────────────
FILTERED=$(echo "$HITS" | while IFS= read -r line; do
  file="${line%%:*}"
  file="${file#./}"
  ALLOWED=false

  # file-by-file allowlist 검사 (기존 11 file)
  for allow_file in "${ALLOWLIST_FILES[@]}"; do
    if [[ "$file" == "$allow_file" ]]; then
      ALLOWED=true
      break
    fi
  done

  # prefix/glob 패턴 allowlist 검사 (Epic-A governance ADR — ADR-099~103)
  if ! $ALLOWED; then
    for prefix in "${ALLOWLIST_ADR_PREFIXES[@]}"; do
      if [[ "$file" == "${prefix}"* ]]; then
        ALLOWED=true
        break
      fi
    done
  fi

  # 추가 allowlist 파일 검사 (Epic-A governance 참조 포함 파일)
  if ! $ALLOWED; then
    for extra_file in "${ALLOWLIST_EXTRA_FILES[@]}"; do
      if [[ "$file" == "$extra_file" ]]; then
        ALLOWED=true
        break
      fi
    done
  fi

  if ! $ALLOWED; then echo "$line"; fi
done)

if [[ -z "$FILTERED" ]]; then
  echo "✓ Atlassian-allow: 평문 참조는 allowlist 영역에만 존재 (OK)"
  exit 0
fi

echo "⚠ Atlassian-allow warning: allowlist 외 평문 Atlassian 참조 발견 (warning tier — ADR-099 §결정 1/3)"
echo "  → 정식 sync 채널 (ADR-100 이후) 또는 allowlist 추가 검토 필요"
echo "$FILTERED"
exit 1
