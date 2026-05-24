#!/usr/bin/env bash
# CFP-1367 / ADR-107 Amendment 1 §결정 1 — F1 plugin-declarative-seed-byte-parity-check
# ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_plugin_declarative_seed_byte_parity.py SSOT)
# ADR-060 §결정 5 — warning-tier (exit 0 항상 for warnings, PR merge 미차단)
#
# Usage:
#   bash scripts/check-plugin-declarative-seed-byte-parity.sh [--ssot-file <path>] [--plugin-file <path>]
#   인수 생략 시 Wave 1 default mapping:
#     SSOT:   docs/project-config-schema.md
#     plugin: templates/deploy-mechanism.md (codeforge-deploy local clone)
#
# Bypass channel: HOTFIX_BYPASS_PLUGIN_DECLARATIVE_SEED_BYTE_PARITY=1 env
#   → 즉시 exit 0 (hotfix-bypass:plugin-declarative-seed-byte-parity label 부착 시 workflow 에서 주입)
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier)
#   1 — malformed 감지 (genuine lint error)
#   2 — setup error (파일 없음 등)
set -euo pipefail

SCRIPT_NAME="[plugin-seed-parity-lint]"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS="${HOTFIX_BYPASS_PLUGIN_DECLARATIVE_SEED_BYTE_PARITY:-}"
if [[ "$BYPASS" == "1" ]]; then
  echo "$SCRIPT_NAME BYPASS=1 — skip" >&2
  exit 0
fi

# ── Python SSOT 위임 (exit-code passthrough) ─────────────────────────────────
exec python3 "$SCRIPT_DIR/lib/check_plugin_declarative_seed_byte_parity.py" "$@"
