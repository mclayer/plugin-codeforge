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
# 정직 상한 — **현 시점 정본 코퍼스 실행의 기대 rc 는 3 이다** (0 아님).
#   firsthand 2026-08-16: 엔진 wrapper `a3d7c56bb` × 코퍼스 internal-docs `8f317f7ce`
#   → `scanned_count=3 violations=0 deferred=6`, rc=3.
#   내역 = SELF/BASE/AUTHOR/LEGC 4정의역 `status: deferred` 4건 + `--before-ref` 부재 INV-S1/S2 2건.
#   해소 = ADR-180 해소 기준 3(전 정의역 `enforced` 실체화) — 본 Story 범위 밖(설계 결정 사항).
#   ⇒ 본 게이트는 아직 어떤 workflow 에도 호출되지 않으며(실측: `.github/` 매치 0),
#     이 상태로 required 승격하면 7일-green 창을 구조적으로 채울 수 없다.
#     승격 사전조건 4건 전문 = `.github/workflows/story-read-surface-test.yml` 헤더.
#
# Usage / 옵션 / 판정 술어 상세: scripts/lib/check_story_read_surface.py --help
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."   # CFP-1408 — always cd (msys2 absolute POSIX→Windows path 변환 회피, relative path 전달)
exec python3 "scripts/lib/check_story_read_surface.py" "$@"
