#!/usr/bin/env bash
# scripts/check-retro-batch-adr-draft-pre-publish.sh
# CFP-1632 / ADR-045 Amendment 10 — retro batch §6 ADR draft pre-publish 8-tuple verify thin wrapper
#
# ADR-061 thin wrapper convention:
#   bash script = POSIX dispatch only → Python SSOT 호출
#   multi-line logic 금지 (5줄 초과 = external .py 의무)
#
# Usage:
#   bash scripts/check-retro-batch-adr-draft-pre-publish.sh --retro-file=<path>
#   bash scripts/check-retro-batch-adr-draft-pre-publish.sh --mode=audit --retro-file=<path>
#
# BYPASS:
#   BYPASS_RETRO_BATCH_ADR_DRAFT_PRE_PUBLISH=1 — unconditional skip (hotfix-bypass family)
#
# Evidence-checks-registry entry: retro-batch-adr-draft-pre-publish (ADR-045 Amendment 10)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_retro_batch_adr_draft_pre_publish.py"

if [ ! -f "${PYTHON_SSOT}" ]; then
  echo "[check-retro-batch-adr-draft-pre-publish] ERROR: Python SSOT not found: ${PYTHON_SSOT}" >&2
  exit 2
fi

exec python3 "${PYTHON_SSOT}" "$@"
