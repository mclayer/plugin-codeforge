#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# scripts/gen-impl-manifest.sh — Story §8.7 Impl Manifest 수치 **기계 생성·대조**
#
# 계기: §8.7 의 `N files changed / M insertions` · 파일별 행수 · 테스트 수집 수 ·
#   스위트 결과가 **수기 사본**이라 커밋마다 stale 이 됐다(구현리뷰 iter3 F-A →
#   iter5 F-CR5-01, 3회차 발현). 수기 사본을 유지하겠다는 결정 자체가 결함원이므로
#   수치를 기계가 생성하고, 기재와 불일치하면 테스트가 RED 가 되게 한다.
#
# 사용:
#   bash scripts/gen-impl-manifest.sh generate              # canonical TSV
#   bash scripts/gen-impl-manifest.sh generate --markdown   # §8.7 붙여넣기용 선언 줄
#   bash scripts/gen-impl-manifest.sh generate --with-suite # 스위트 실행 축 포함(느림)
#   bash scripts/gen-impl-manifest.sh check --story <path>  # §8.7 기재 대조
#   CFP2949_STORY_FILE=<path> bash scripts/gen-impl-manifest.sh check
#
# Exit: 0 = 일치(또는 generate 성공) / 1 = 불일치 / 2 = Story 경로 미주입·부재
#
# ★ Story 경로는 **하드코딩하지 않는다** — Story(§8.7 보유 문서)는 별 repo
#   (codeforge-internal-docs)에 있으므로 인자 또는 CFP2949_STORY_FILE 로 주입한다.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

PY="${PYTHON_BIN:-python}"
command -v "$PY" >/dev/null 2>&1 || PY=python3

exec "$PY" "${SCRIPT_DIR}/lib/impl_manifest.py" "$@" --repo-root "${REPO_ROOT}"
