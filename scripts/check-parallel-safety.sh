#!/usr/bin/env bash
# scripts/check-parallel-safety.sh — CFP-1173 Phase 2
# 병렬 판정 이중 메커니즘 Bash thin wrapper
#
# 책임: parallel_safety.py 호출 (ADR-061 Python SSOT)
#   plan entry batch 병렬 안전성 판정 (brainstorming 결정 5)
#
# 사용법:
#   bash scripts/check-parallel-safety.sh --json '<JSON>'
#
# 입력 JSON 형식:
#   {"entries": [
#     {"id": "A", "touched_files": ["path/a.sh"], "parallel_safe_with": []},
#     {"id": "B", "touched_files": ["path/b.sh"]}
#   ]}
#
# 출력:
#   - all_safe=true → stdout + exit 0
#   - all_safe=false → stdout + exit 1 (unsafe_pairs 목록 포함)
#
# Exit: 0=all_safe / 1=unsafe pair 존재 / 2=입력 오류 / 3=Python 실행 오류
#
# SSOT: docs/change-plans/cfp-1173-blast-radius-parallel.md §3 병렬 이중 algorithm
# ADR-061 정합 — Python SSOT = parallel_safety.py (heredoc-python 0)
# Sandbox: CBL_SKIP_ISSUE_CREATE=1
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PARALLEL_PY="${REPO_ROOT}/scripts/lib/parallel_safety.py"
# Windows 경로 변환 (Git Bash /c/... → Windows 형식, Python 호환)
REPO_ROOT_WIN="$(cygpath -w "${REPO_ROOT}" 2>/dev/null || echo "${REPO_ROOT}")"
LIB_DIR_WIN="${REPO_ROOT_WIN}\\scripts\\lib"

# ─────────────────────── 인자 파싱 ───────────────────────────────────────────

INPUT_JSON=""

usage() {
    cat >&2 <<'EOF'
사용법: check-parallel-safety.sh --json '<JSON>'

입력 JSON 형식:
  {"entries": [
    {"id": "A", "touched_files": ["scripts/a.sh"]},
    {"id": "B", "touched_files": ["scripts/b.sh"], "parallel_safe_with": ["A"]}
  ]}

Exit 코드:
  0 = all_safe (모든 pair 병렬 안전)
  1 = unsafe pair 존재 (순차 필요)
  2 = 입력 오류
  3 = Python 실행 오류
EOF
    exit 2
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json)
            INPUT_JSON="${2:-}"
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

# ─────────────────────── Python SSOT 호출 ────────────────────────────────────

if [[ ! -f "${PARALLEL_PY}" ]]; then
    echo "오류: parallel_safety.py 미존재: ${PARALLEL_PY}" >&2
    exit 3
fi

# INPUT_JSON 이스케이핑을 위해 임시 파일 사용 (ADR-061: heredoc-python 0)
TMPFILE="$(mktemp)"
trap 'rm -f "${TMPFILE}"' EXIT
echo "${INPUT_JSON}" > "${TMPFILE}"

PYTHONPATH="${LIB_DIR_WIN}" PYTHONIOENCODING=utf-8 python3 - "${TMPFILE}" "${REPO_ROOT_WIN}" <<'PYEOF'
import sys
import json
import os

# PYTHONPATH (LIB_DIR_WIN) 보완 + repo_root argv 주입
json_file = sys.argv[1] if len(sys.argv) > 1 else None
repo_root = sys.argv[2] if len(sys.argv) > 2 else None

if repo_root:
    lib_path = os.path.join(repo_root, "scripts", "lib")
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)

try:
    from parallel_safety import PlanEntry, check_batch_safety
except ImportError as e:
    print(f"오류: parallel_safety.py import 실패: {e}", file=sys.stderr)
    sys.exit(3)

# JSON 입력 읽기 (임시 파일)
if not json_file:
    print("오류: JSON 파일 경로 누락", file=sys.stderr)
    sys.exit(2)

try:
    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    # 빈 JSON = 빈 entries 취급
    raw = open(json_file).read().strip()
    if not raw:
        data = {"entries": []}
    else:
        print(f"오류: JSON 파싱 실패: {e}", file=sys.stderr)
        sys.exit(2)

entries_raw = data.get("entries", [])
entries = []
for item in entries_raw:
    entry = PlanEntry(
        entry_id=item.get("id", item.get("entry_id", "")),
        touched_files=item.get("touched_files", []),
        parallel_safe_with=item.get("parallel_safe_with", []),
    )
    entries.append(entry)

result = check_batch_safety(entries)

if result.all_safe:
    print(f"all_safe: true")
    print(f"safe_pairs: {len(result.safe_pairs)}")
    print(f"parallel_safe: true")
    sys.exit(0)
else:
    print(f"all_safe: false")
    print(f"parallel_safe: false")
    print(f"unsafe_pairs: {len(result.unsafe_pairs)}")
    for pair in result.unsafe_pairs:
        print(f"  - {pair.entry_a_id} x {pair.entry_b_id}: {pair.overlap_paths}")
    sys.exit(1)
PYEOF
# shellcheck disable=SC2319
EXIT_CODE=$?

# Python exit code 그대로 전파 (exit 0/1/2/3 시맨틱 유지)
exit ${EXIT_CODE}
