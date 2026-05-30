#!/usr/bin/env bash
# check-orchestrator-spawn-prompt-fact-verify.sh
# CFP-1844 / ADR-082 Amendment 34 sub-scope 1-W + ADR-073 Amendment 18 paired sibling.
# Wave 2 mechanical wire — Orchestrator spawn-prompt-fact verify warning lint (warning-tier).
#
# Thin bash wrapper. SSOT logic = scripts/lib/check_orchestrator_spawn_prompt_fact_verify.py
# (ADR-061 Amendment 3 §결정 11 — Python SSOT for multi-line text parsing, ReDoS-safe).
#
# Usage:
#   bash scripts/check-orchestrator-spawn-prompt-fact-verify.sh --input <file|->
#   echo "<text>" | bash scripts/check-orchestrator-spawn-prompt-fact-verify.sh --input -
#
# Exit codes (delegated to Python SSOT):
#   0  PASS or FAIL-as-warning (warning-tier per ADR-060 §결정 5 default)
#   2  usage error (input unreadable)
set -euo pipefail
exec python3 "$(dirname "$0")/lib/check_orchestrator_spawn_prompt_fact_verify.py" "$@"
