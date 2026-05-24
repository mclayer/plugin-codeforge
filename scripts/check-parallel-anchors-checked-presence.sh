#!/usr/bin/env bash
# check-parallel-anchors-checked-presence.sh
# CFP-1306 / ADR-060 Amendment 15 §결정 29 / ADR-068 I-2 cross-module propagation completeness
#
# Thin bash wrapper — ADR-061 §결정 1 정합 (Python entry-point + thin wrapper 분리).
# CFP-583 BODY heredoc anti-pattern 차단 (script body = exec python3 단일 호출).
#
# Lints review-verdict-v4 packet body files for findings[].parallel_anchors_checked[] field.
# Wave 3 mechanical enforcement (Wave 1=CFP-1291 prose, Wave 2=CFP-1303 schema).
#
# 3-state semantic:
#   absent      → exit 1 (WARNING) — field missing, emit advisory
#   present+clean → exit 0 (PASS) — all matched: false, evidence of completeness
#   present+matched → exit 0 (PASS) — matched: true found, advisory
#
# warning tier (continue-on-error) — exit 1 does NOT block PR merge.
#
# Usage: bash scripts/check-parallel-anchors-checked-presence.sh <file> [...]
#
# SecurityArch TH-2: set +x guard — no PAT/secret echoed to stdout/stderr.
# Exit codes (ADR-060 §결정 15 3-tier): 0=PASS | 1=WARNING | 2=META-ERROR
set +x  # SecurityArch TH-2: no debug trace (PAT guard)
set -euo pipefail
exec python3 "$(dirname "$0")/lib/check_parallel_anchors_checked_presence.py" "$@"
