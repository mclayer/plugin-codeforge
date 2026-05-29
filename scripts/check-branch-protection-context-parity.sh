#!/usr/bin/env bash
# check-branch-protection-context-parity.sh
# CFP-1807 / ADR-024 §결정 6.A — cross-repo branch protection contexts parity warning lint.
# See scripts/lib/check_branch_protection_context_parity.py for SSOT logic.
#
# Tier: warning (ADR-060 §결정 5 default, exit 0 on drift)
# Bypass: hotfix-bypass:branch-protection-context-parity label
# Requires: gh CLI authenticated (GH_TOKEN env in CI)
#
# Usage:
#   bash scripts/check-branch-protection-context-parity.sh [--repo-root <path>]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/lib/check_branch_protection_context_parity.py" "$@"
