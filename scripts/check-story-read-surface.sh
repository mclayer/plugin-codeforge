#!/usr/bin/env bash
# CFP-2986 / ADR-180 — Story 읽기면 게이트 (thin wrapper)
# ADR-061 §결정 1 + Amendment 1 §결정 6.A — 로직 0 · heredoc 0, SSOT = scripts/lib/check_story_read_surface.py
#
# Exit code:
#   0  PASS
#   1  FAIL          — fail-closed 불변식 위반 (정보 손실 축)
#   2  USAGE
#   3  UNDETERMINED  — 판정 불가 (커버리지 미달 / deferred 정의역 / before-ref 부재). GREEN 아님.
#
# Usage / 옵션 / 판정 술어 상세: scripts/lib/check_story_read_surface.py --help
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."   # CFP-1408 — always cd (msys2 absolute POSIX→Windows path 변환 회피, relative path 전달)
exec python3 "scripts/lib/check_story_read_surface.py" "$@"
