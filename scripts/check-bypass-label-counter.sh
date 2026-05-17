#!/usr/bin/env bash
# check-bypass-label-counter.sh
# CFP-825 / ADR-024 Amendment 6 §결정 6.A.2
#
# Thin bash wrapper — ADR-061 정합 (Python entry-point + thin wrapper 분리).
# CFP-583 BODY heredoc anti-pattern 차단 (script body = exec python3 단일 호출).
#
# Usage: bash scripts/check-bypass-label-counter.sh [--dry-run] [--repo OWNER/REPO]
set -euo pipefail
exec python3 "$(dirname "$0")/check-bypass-label-counter.py" "$@"
