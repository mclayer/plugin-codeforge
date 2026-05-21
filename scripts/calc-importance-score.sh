#!/usr/bin/env bash
# scripts/calc-importance-score.sh — CFP-1173 Phase 2
# blast-radius importance_score 계산 Bash thin wrapper
#
# 책임: importance_score.py 호출 (ADR-061 Python SSOT)
#   walk plan stage importance_score 계산 (brainstorming 결정 4)
#
# 사용법:
#   bash scripts/calc-importance-score.sh --touched-lanes <N> --breaking <true|false> --contract-major <M>
#
# 옵션:
#   --touched-lanes <N>    영향받는 lane 수 (0~7, 필수)
#   --breaking <true|false>  BREAKING CHANGE 마커 여부 (필수)
#   --contract-major <M>   inter-plugin contract MAJOR bump 수 (기본 0)
#
# 출력: importance_score (수치, stdout)
# Exit: 0=성공 / 1=입력 오류 / 2=Python 실행 오류
#
# SSOT: docs/change-plans/cfp-1173-blast-radius-parallel.md §3
# ADR-061 정합 — Python SSOT = importance_score.py (외부 .py 파일)
# Sandbox: CBL_SKIP_ISSUE_CREATE=1
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
# Windows 경로 변환 (Git Bash /c/... → C:/... 형식, Python 호환)
REPO_ROOT_WIN="$(cygpath -w "${REPO_ROOT}" 2>/dev/null || echo "${REPO_ROOT}")"
IMPORTANCE_PY="${REPO_ROOT}/scripts/lib/importance_score.py"

# ─────────────────────── 인자 파싱 ───────────────────────────────────────────

TOUCHED_LANES=""
BREAKING=""
CONTRACT_MAJOR="0"

usage() {
    cat >&2 <<'EOF'
사용법: calc-importance-score.sh --touched-lanes <N> --breaking <true|false> [--contract-major <M>]

옵션:
  --touched-lanes <N>      영향받는 lane 수 (0~7, 필수)
  --breaking <true|false>  BREAKING CHANGE 마커 여부 (필수)
  --contract-major <M>     contract MAJOR bump 수 (기본: 0)

예시:
  bash scripts/calc-importance-score.sh --touched-lanes 3 --breaking true --contract-major 1
EOF
    exit 1
}

if [[ $# -eq 0 ]]; then
    echo "오류: 인자가 필요합니다." >&2
    usage
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        --touched-lanes)
            TOUCHED_LANES="${2:-}"
            shift 2
            ;;
        --breaking)
            BREAKING="${2:-}"
            shift 2
            ;;
        --contract-major)
            CONTRACT_MAJOR="${2:-0}"
            shift 2
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo "오류: 알 수 없는 인자 '$1'" >&2
            usage
            ;;
    esac
done

# ─────────────────────── 필수 인자 검증 ──────────────────────────────────────

if [[ -z "${TOUCHED_LANES}" ]]; then
    echo "오류: --touched-lanes 인자가 필요합니다." >&2
    usage
fi

if [[ -z "${BREAKING}" ]]; then
    echo "오류: --breaking 인자가 필요합니다." >&2
    usage
fi

# breaking 값 정규화
case "${BREAKING}" in
    true|True|TRUE|1|yes)
        BREAKING_BOOL="True"
        ;;
    false|False|FALSE|0|no)
        BREAKING_BOOL="False"
        ;;
    *)
        echo "오류: --breaking 값은 true/false 이어야 합니다: '${BREAKING}'" >&2
        exit 1
        ;;
esac

# ─────────────────────── Python SSOT 직접 호출 (ADR-061) ─────────────────────

if [[ ! -f "${IMPORTANCE_PY}" ]]; then
    echo "오류: importance_score.py 미존재: ${IMPORTANCE_PY}" >&2
    exit 2
fi

# ADR-061: 외부 .py 파일 직접 실행
# Windows 환경 경로 문제 회피: importance_score.py 를 직접 python3에 전달
# lib/ 디렉토리를 PYTHONPATH 로 주입
LIB_DIR_WIN="${REPO_ROOT_WIN}\\scripts\\lib"
PYTHONPATH="${LIB_DIR_WIN}" PYTHONIOENCODING=utf-8 python3 - \
    "${TOUCHED_LANES}" "${BREAKING_BOOL}" "${CONTRACT_MAJOR}" \
    "${REPO_ROOT_WIN}" <<'PYEOF'
import sys
import os

touched_lanes = int(sys.argv[1])
breaking_bool = sys.argv[2] == "True"
contract_major = int(sys.argv[3])
repo_root = sys.argv[4]

# lib 경로 등록 (PYTHONPATH 보완)
lib_path = os.path.join(repo_root, "scripts", "lib")
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

try:
    from importance_score import BlastRadiusTuple, calc_importance_score
    entry = BlastRadiusTuple(
        touched_lanes_count=touched_lanes,
        breaking_change_marker=breaking_bool,
        contract_major_bump=contract_major,
    )
    score = calc_importance_score(entry)
    print(score)
except (ValueError, TypeError) as e:
    print(f"오류: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF
