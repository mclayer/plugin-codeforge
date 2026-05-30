#!/usr/bin/env bash
# check-branch-protection-context-name-strict-match.sh
# CFP-1849 / ADR-024 §결정 6.A + ADR-060 — branch-protection-context-name-strict-match warning lint.
# Wave 2 mechanical wire — main branch protection required check context name 이 actual
# workflow job 표시명과 strict match 검증 (warning-tier).
#
# Thin bash wrapper. SSOT logic = scripts/lib/check_branch_protection_context_name_strict_match.py
# (ADR-061 Amendment 3 §결정 11 — Python SSOT, PyYAML primary + ReDoS-safe fallback).
#
# Background (CFP-1807 retro F-001):
#   CFP-1808 (어제) 작업이 main branch protection 의 6번째 required check context name
#   으로 `deploy-lane-presence` 등록했으나, 실제 workflow job 표시명은
#   "Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)" → mismatch → 모든
#   후속 PR pending/BLOCKED 가짜 CLEAN 상태. CFP-1807 PR #1827 에서 admin gh CLI 로
#   context name 정합 정정해서 catch. 본 lint = 동형 사고 자동 감지 mechanism.
#
# Usage:
#   bash scripts/check-branch-protection-context-name-strict-match.sh [--repo <slug>]
#
# Exit codes (delegated to Python SSOT):
#   0  PASS or FAIL-as-warning (warning-tier per ADR-060 §결정 5 default)
#   2  usage error (workflow dir missing)
set -euo pipefail
exec python3 "$(dirname "$0")/lib/check_branch_protection_context_name_strict_match.py" "$@"
