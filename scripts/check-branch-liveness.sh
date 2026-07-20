#!/usr/bin/env bash
# scripts/check-branch-liveness.sh — external watchdog thin wrapper (ADR-061)
#
# CFP-2772 Phase 2 (D2 external watchdog) / ADR-164 §결정 2/4/7 — per-branch heartbeat
# stale 감지 cron poller. Jira read-only relay 코멘트를 파싱해 monotonic seq + watchdog-own-clock
# 기반 3-state 판정(fresh/stalled/unknown) + meta-observer Tier-2 last-run marker.
#
# ADR-061 §결정 1: Python SSOT 엔진 + bash thin wrapper(로직 0, exec forward만).
#
# Usage:
#   bash scripts/check-branch-liveness.sh --comments <file|-> --cursor <path>
#     [--now <iso8601>] [--lane-thresholds <file>] [--marker-out <file>] [--json]
#
# Arguments:
#   --comments FILE|'-'         Jira relay 코멘트 본문 JSON array/JSONL (stdin='-')
#   --cursor PATH               durable ack cursor (JSON, 이 경로에서 read + in-place update)
#   --now ISO8601               watchdog own-clock(default=UTC now). F-5 타임스탬프 스큐 방지.
#   --lane-thresholds FILE      lane→임계(분) 오버라이드 JSON {lane:minutes}(optional, builtin PROPOSAL 상속)
#   --marker-out FILE           meta-observer Tier-2 last-run marker 경로 (§결정 7, optional)
#   --json                      JSON verdict stdout (default=human-readable summary)
#
# Exit code:
#   0 = record-only (항상 성공 — workflow 가 verdict 해석)
#   2 = usage 또는 env 오류
#
# Verdict:
#   {
#     "verdict": "ok"|"stalled-detected"|"inconclusive",
#     "summary": {"fresh": N, "stalled": N, "unknown": N},
#     "branches": {
#       "BRANCH": {
#         "verdict": "fresh"|"stalled"|"unknown",
#         "reason": "heartbeat-present", // or seq-advanced|seq-unchanged|heartbeat-absent|malformed…
#         "seq": N,
#         "elapsed_min": F,
#         "threshold_min": N
#       },
#       …
#     }
#   }

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── 사전 조건 확인 ──────────────────────────────────────────────────────────
command -v python3 >/dev/null 2>&1 || {
  echo "[check-branch-liveness] error: python3 not installed" >&2
  exit 2
}

# ── exec forward ──────────────────────────────────────────────────────────
# 로직은 Python SSOT에 전부 위임. 이 wrapper는 환경 제어만.
exec python3 "$SCRIPT_DIR/lib/check_branch_liveness.py" "$@"
