#!/usr/bin/env bash
# check-increment-justification.sh
# CFP-2061-S1 / ADR-060 §결정 30
#
# Thin bash wrapper — ADR-061 정합 (Python entry-point + thin wrapper 분리).
# 정당화 순증 게이트 — 검사·ADR·스크립트 신규 추가 PR 에 실효 정당화 강제.
#
# Usage: bash scripts/check-increment-justification.sh [--repo OWNER/REPO] [--pr-number N]
#                                                      [--base-ref REF] [--dry-run]
set -euo pipefail
exec python3 "$(dirname "$0")/lib/check_increment_justification.py" "$@"
