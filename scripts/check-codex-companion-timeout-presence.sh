#!/usr/bin/env bash
# CFP-2545 / ADR-081 Amendment 12 §결정 D14 — Codex companion 브로커 경로 wall-clock 가드 presence lint
# ADR-061 §결정 1 — thin wrapper (scripts/lib/check_codex_companion_timeout_presence.py SSOT)
#
# 검사: codeforge 소유 codex companion dispatch 발화(node ... adversarial-review | task --write)가
#       항상 `timeout <N> --kill-after=<K>` wall-clock 가드로 감싸졌는지 + 발화 건수 ≥1 (hollow-gate 차단).
# Usage / exit code / semantics 상세: scripts/lib/check_codex_companion_timeout_presence.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_codex_companion_timeout_presence.py" "$@"
