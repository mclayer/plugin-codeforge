#!/usr/bin/env bash
# CFP-60 / label-registry-v1.1 — debut-audit 9 신규 label bootstrap
# Idempotent (label 존재 시 skip).
#
# Usage: bash scripts/bootstrap-debut-audit-labels.sh [<owner/repo>]
#   default: mclayer/plugin-codeforge

set -euo pipefail
REPO="${1:-mclayer/plugin-codeforge}"

declare -a labels=(
  "audit:debut-eval|fbca04|데뷔 평가 (consumer 첫 사용 사례) 발견 사항"
  "audit:from-mctrader-debut|fef2c0|mctrader 데뷔 평가에서 발견된 codeforge gap (첫 사례)"
  "category:lane-progression|0e8a16|#1 — 7 lane 통과 / 막힘 (owner: PMOAgent)"
  "category:agent-gap|d93f0b|#2 — phase 별 gap + 과부하 (owner: ArchitectPL, ADR-021 R1-R4)"
  "category:decision-table|1d76db|#3 — 원인 판정 row 모호 / 신규 (owner: wrapper Orchestrator)"
  "category:deputy-mandate|5319e7|#4 — 6 deputy mandate 부족 (owner: ArchitectPL)"
  "category:workflow-invariant|bfd4f2|#5 — GitHub Actions 강제 누락 (owner: wrapper Orchestrator)"
  "category:template|c5def5|#6 — Story / Change Plan / ADR 필드 부족 (owner: per-template)"
  "category:contract-schema|bfdadc|#7 — inter-plugin contract schema 부족 (owner: producer lane plugin)"
)

for entry in "${labels[@]}"; do
  IFS='|' read -r name color description <<< "$entry"
  if gh label list --repo "$REPO" --search "$name" --json name --jq '.[].name' 2>/dev/null | grep -qFx "$name"; then
    echo "  - $name (already exists, skip)"
  else
    gh label create "$name" --repo "$REPO" --color "$color" --description "$description" 2>&1 | head -1
    echo "  + $name (created)"
  fi
done

echo "✅ debut-audit labels bootstrap complete on $REPO"
