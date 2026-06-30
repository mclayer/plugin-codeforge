#!/usr/bin/env bash
# CFP-2491 / Epic CFP-2481 E3b / ADR-133 §결정4·§결정6 — ADR-RESERVATION slot-level stale claim 회수
# ADR-061 §결정6 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/adr-reservation-stale-reclaim.py SSOT)
# FIX (구현리뷰 P0 carry F1): inline heredoc Python 추출 — 들여쓰기 fragility 제거 + 테스트 가능.
# Usage / 인터페이스 / 정책 상세: scripts/lib/adr-reservation-stale-reclaim.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/lib/adr-reservation-stale-reclaim.py" "$@"
