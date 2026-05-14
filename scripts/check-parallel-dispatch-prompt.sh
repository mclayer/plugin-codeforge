#!/usr/bin/env bash
# scripts/check-parallel-dispatch-prompt.sh — parallel-dispatch-protocol-v1 §8 mechanical enforcement
# ADR-064 Amendment 1 §결정 4 carrier — ADR-060 warning tier entry `parallel-dispatch-prompt-check`
# Shim ≤ 5 lines per ADR-061 convention; real logic in scripts/check_parallel_dispatch_prompt.py.
set -euo pipefail
exec python3 "$(dirname "$0")/check_parallel_dispatch_prompt.py" "$@"
