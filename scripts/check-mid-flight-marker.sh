#!/usr/bin/env bash
# scripts/check-mid-flight-marker.sh — mid-flight marker ownership/freshness PR-time lint thin wrapper
#
# CFP-2761 §5.2 / ADR-085 §결정10 — 작업 중(mid-flight) 산출물의 소유/신선도 마커 stale 상태를
#   PR 시점에 좌향 노출한다. 타입 1(마커 stale) / 타입 2(N/A 선언 without status=final) /
#   타입 3(dispatch placeholder) / 타입 5(ADR-RESERVATION 예약 row proxy). warning tier (PR 무차단).
# ADR-061 §결정 1: Python entry-point + thin bash wrapper (python3 exec forward, 로직 0).
#
# Usage / exit code / semantics 상세: scripts/lib/check_mid_flight_marker.py header.
#   bash scripts/check-mid-flight-marker.sh --repo-root DIR [--files F1 F2 ...] [--stale-days N]
#     0 = clean / warning finding / zero-target honest no-op (advisory)
#     2 = usage error OR TC-UNKNOWN (closed-set 밖 status)
#     3 = born-hollow (repo-root 부재/dir 아님)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-mid-flight-marker-infra-error] check-mid-flight-marker: python3 not installed" >&2
  exit 2
}

exec python3 "$SCRIPT_DIR/lib/check_mid_flight_marker.py" "$@"
