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
#   ⇒ **이 `.sh` wrapper 자신**을 호출하는 workflow 는 **wrapper `.github/` 정의역 안에 0건**이다
#     [실측 wrapper `794d11423`: 추적 132 파일 전역에서 문자열 `check-story-read-surface`
#      매치 3건 — 전건 주석행이고 비주석 호출 0].
#     ★ **엔진은 별개 축이다.** internal-docs 는 이 wrapper 를 거치지 않고 엔진
#       `scripts/lib/check_story_read_surface.py` 를 **직접** 호출한다. 그러므로 "어떤 workflow
#       에도 호출되지 않는다" 는 서술은 **엔진 기준으로 거짓**이고 이 wrapper 기준으로만 참이다
#       — 주어를 밝히지 않은 미배선 선언은 게이트 전반의 미배선으로 오독된다
#       [실측 internal-docs `53c1cb734`: 추적 11 파일 전역에서 엔진 문자열 매치 7건 중 비주석 2건.
#        실호출 문면 = `.github/workflows/story-read-surface-check.yml` 안
#        `ENGINE=scripts/lib/check_story_read_surface.py` → `python3 "$ENGINE" $ENGINE_ARGS`
#        (측정 시점 :257 / :318 — 줄번호는 파생이고 정본 앵커는 이 문면이다)].
#       ★ 두 사본의 byte-identical 여부는 **여기 고정 수치(sha256·바이트 크기)로 적지 않는다** —
#         가변 축의 신원을 상수로 박으면 stale 되고, 그 고장은 404 가 아니라 **GREEN 인 채 drift
#         생존** 형태로 온다(본 Story 에서 같은 기전 2회 재발). 신원 정본 = 재현 규칙이며
#         소유자는 internal-docs `scripts/lib/compare_story_read_surface_parity.py` (drift-guard)
#         이다 — 본 파일은 그 판정을 복제하지 않는다.
#     ⇒ 따라서 "미배선" 은 **이 wrapper 의 호출 경로**에 한정된 사실이다. 다만 rc 축은 호출
#       경로와 무관하게 동일 엔진의 판정이므로, 이 상태로 required 승격하면 7일-green 창을
#       구조적으로 채울 수 없다 (internal-docs workflow **실행**의 rc 는 본 주석에서 미측정 —
#       위 rc=3 은 엔진을 정본 코퍼스에 직접 돌린 firsthand 값이다).
#       승격 사전조건 4건 전문 = `.github/workflows/story-read-surface-test.yml` 헤더.
#
# Usage / 옵션 / 판정 술어 상세: scripts/lib/check_story_read_surface.py --help
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."   # CFP-1408 — always cd (msys2 absolute POSIX→Windows path 변환 회피, relative path 전달)
exec python3 "scripts/lib/check_story_read_surface.py" "$@"
