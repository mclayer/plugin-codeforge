#!/usr/bin/env bash
# CFP-1346 / ADR-108 §결정 3 — label-registry-v2 description text count parity lint
# Thin wrapper per ADR-061 (Python SSOT, bash 5-line cap)
set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
python3 "$REPO_ROOT/scripts/lib/check_label_registry_frozen_baseline_count_parity.py" "$@"
