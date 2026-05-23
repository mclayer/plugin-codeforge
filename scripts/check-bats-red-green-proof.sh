#!/usr/bin/env bash
# CFP-1334 §결정 1 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — external .py split.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python "${SCRIPT_DIR}/lib/check_bats_red_green_proof.py" "$@"
