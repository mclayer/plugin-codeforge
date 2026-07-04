#!/usr/bin/env bash
# CFP-2574 / ADR-143 §결정 3 — KST render-line 시각원 thin wrapper (UTC+9 고정 산술)
#
# Agent 액션 렌더 줄 프리픽스 `[에이전트명] MM/DD HH:MM - 내용` 의 컴팩트 KST 시각을 stdout 1줄로 산출.
# 시각원 pin (ADR-143 §결정 3):
#   - primary (GNU date): `date -u -d '+9 hours' '+%m/%d %H:%M'` — UTC read 후 +9시간 산술 (tzdata 무의존).
#   - fallback (Python SSOT): scripts/lib/kst_render_stamp.py (GNU `-d` 미지원 BSD date 등 환경).
#   - machine-local `date`·`TZ=Asia/Seoul` 금지 — Windows Git Bash 는 TZ=Asia/Seoul 무시하고 +0000 반환.
#     Korea 고정 offset·DST 영구 부재 invariant 로 UTC+9 고정 산술만 채택.
# Usage: bash scripts/kst-render-stamp.sh   → stdout `MM/DD HH:MM`
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# primary: GNU date UTC+9 고정 산술 (offset·연도·초·KST 라벨 미표기 — ADR-143 §결정 2 컴팩트)
if STAMP="$(date -u -d '+9 hours' '+%m/%d %H:%M' 2>/dev/null)" && [ -n "$STAMP" ]; then
  printf '%s\n' "$STAMP"
  exit 0
fi

# fallback: Python SSOT (동일 UTC+9 고정 산술, portable)
PY=""
if command -v python3 >/dev/null 2>&1; then
  PY="python3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
fi
if [ -n "$PY" ]; then
  exec "$PY" "$SCRIPT_DIR/lib/kst_render_stamp.py"
fi

echo "[kst-render-stamp] ERROR: neither GNU date (-d) nor python available" >&2
exit 1
