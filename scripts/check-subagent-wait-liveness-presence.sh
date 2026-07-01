#!/usr/bin/env bash
# CFP-2549 / ADR-139 INV-L1~L4 — background-wait liveness gate presence lint (general subagent-wait)
# ADR-061 §결정 1 — thin wrapper (scripts/lib/check_subagent_wait_liveness_presence.py SSOT)
#
# 검사: orchestrator playbook 의 background-wait liveness 규약 발화(run_in_background | bg spawn)가
#       항상 runnable option-first `timeout --kill-after=<K> <N>` wall-clock 가드로 감싸졌는지
#       + 발화 건수 ≥1 (hollow-gate I-3 차단) + playbook 부재 시 consumer no-op.
# Usage / exit code / semantics 상세: scripts/lib/check_subagent_wait_liveness_presence.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_subagent_wait_liveness_presence.py" "$@"
