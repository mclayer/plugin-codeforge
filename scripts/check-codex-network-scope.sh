#!/usr/bin/env bash
# check-codex-network-scope.sh
# CFP-963 / ADR-081 Amendment 4 §결정 D1.D / ADR-060 Amendment 14 §결정 28
#
# Thin bash wrapper — ADR-061 §결정 1 정합 (Python entry-point + thin wrapper 분리).
# CFP-583 BODY heredoc anti-pattern 차단 (script body = exec python3 단일 호출).
#
# Lints Codex worker spawn-prompt body for network_scope: <4-tier enum> field.
# warning tier (continue-on-error) — exit 1 does NOT block PR merge.
#
# Usage: bash scripts/check-codex-network-scope.sh <prompt-file> [--carrier-story CFP-NNN]
#
# SecurityArch TH-2: set +x guard — no PAT/secret echoed to stdout/stderr.
# Exit codes (ADR-060 §결정 15 3-tier): 0=PASS | 1=WARNING | 2=META-ERROR
set +x  # SecurityArch TH-2: no debug trace (PAT guard)
set -euo pipefail
exec python3 "$(dirname "$0")/lib/check_codex_network_scope.py" "$@"
