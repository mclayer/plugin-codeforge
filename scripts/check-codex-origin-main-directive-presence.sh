#!/usr/bin/env bash
# check-codex-origin-main-directive-presence.sh
# CFP-1412 / ADR-081 Amendment 8 §결정 D9 / ADR-060 §결정 28
#
# Thin bash wrapper — ADR-061 §결정 1 정합 (Python entry-point + thin wrapper 분리).
# CFP-583 BODY heredoc anti-pattern 차단 (script body = exec python3 단일 호출).
#
# Lints Codex worker spawn-prompt body for [ORIGIN-MAIN-DIRECTIVE] block presence.
# warning tier (continue-on-error) — exit 1 does NOT block PR merge.
#
# Usage: bash scripts/check-codex-origin-main-directive-presence.sh <prompt-file>
#
# Fallback marker closed-set 3 enum (ADR-081 Amendment 8 D9 SSOT):
#   [origin-main-directive-fallback: network_scope_offline]
#   [origin-main-directive-fallback: legacy_prompt_format]
#   [origin-main-directive-fallback: intentional_working_tree_verify]
#
# SecurityArch TH-2: set +x guard — no PAT/secret echoed to stdout/stderr.
# Exit codes (ADR-060 §결정 15 3-tier): 0=PASS | 1=WARNING | 2=META-ERROR
#
# Bypass: BYPASS_CODEX_ORIGIN_MAIN_DIRECTIVE=1 env → silent skip + audit trail
set +x  # SecurityArch TH-2: no debug trace (PAT guard)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/lib/check_codex_origin_main_directive_presence.py" "$@"
