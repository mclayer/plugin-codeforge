#!/usr/bin/env bash
# check-cross-repo-bypass-counter.sh
# CFP-845 / ADR-024 Amendment 8 §결정 6.A.5
#
# Thin bash wrapper — ADR-061 정합 (Python entry-point + thin wrapper 분리).
#
# Usage: bash scripts/check-cross-repo-bypass-counter.sh [--dry-run]
#                                                        [--threshold N]
#                                                        [--repos REPO1,REPO2,REPO3]
set -euo pipefail
exec python3 "$(dirname "$0")/check-cross-repo-bypass-counter.py" "$@"
