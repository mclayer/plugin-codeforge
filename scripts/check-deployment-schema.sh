#!/usr/bin/env bash
# check-deployment-schema.sh — thin bash wrapper for check_deployment_schema.py
# CFP-1059-S5: consumer overlay deploy.* schema validation
#
# ADR-061: multi-line validation logic = external .py (this script = orchestration only)
# Usage: bash scripts/check-deployment-schema.sh [<project.yaml>]
#
# exit codes (ADR-060 §결정 15):
#   0 = PASS (or skip: file/deploy block absent)
#   1 = FAIL (schema violation)
#   2 = lint-internal-error

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="${SCRIPT_DIR}/check_deployment_schema.py"

# Resolve overlay path: arg1 > env OVERLAY_PATH > default .claude/_overlay/project.yaml
if [[ $# -ge 1 ]]; then
  OVERLAY_PATH="$1"
else
  OVERLAY_PATH="${OVERLAY_PATH:-.claude/_overlay/project.yaml}"
fi

# Opt-in PASS: overlay absent (consumer has not configured deploy block)
if [[ ! -f "${OVERLAY_PATH}" ]]; then
  echo "[INFO] Overlay not found: ${OVERLAY_PATH} - skipping (opt-in PASS)"
  exit 0
fi

# Delegate to Python script (ADR-061: logic > 5 lines = external .py)
python3 "${PY_SCRIPT}" "${OVERLAY_PATH}"
exit $?
