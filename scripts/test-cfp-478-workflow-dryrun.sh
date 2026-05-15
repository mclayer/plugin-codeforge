#!/usr/bin/env bash
# scripts/test-cfp-478-workflow-dryrun.sh
# CFP-478 Phase 2 sub-PR b — workflow dry-run runner (thin wrapper)
# Invokes scripts/lib/test_cfp_478_workflow_dryrun.py
# ADR-061 Amendment 1 §결정 1.B — shell wrapper delegates to external .py
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "${REPO_ROOT}/scripts/lib/test_cfp_478_workflow_dryrun.py" "$@"
