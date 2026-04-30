#!/usr/bin/env bash
# CFP-E — Test harness for check-inter-plugin-drift.sh
#
# 8 test cases (T-1 ~ T-8 per CFP-E spec §8). Each case:
#   1. Build canonical fixture from current sibling state (baseline = drift 0)
#   2. Apply test-specific mutation (to sibling file or fixture)
#   3. Run lint with CFP_E_TEST_FIXTURE_DIR=<tmp>
#   4. Assert expected exit code
#   5. Restore sibling files (git checkout)
#
# Usage: bash scripts/test-check-inter-plugin-drift.sh
# Exit: 0 if all pass, 1 if any fail.

set -uo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
LINT_SCRIPT="$REPO_ROOT/scripts/check-inter-plugin-drift.sh"

PASS=0
FAIL=0
# Windows/Git Bash: /tmp/ POSIX path 가 Python 에서 안 보일 수 있음 — repo-relative 경로 사용
TOP_TMP="./.test-fixtures-cfp-e-$$"
mkdir -p "$TOP_TMP"
trap "rm -rf '$TOP_TMP'" EXIT

# 정상 fixture 생성 — 5 active contract canonical 을 sibling 본문에서
# 정규화 결과와 동일한 형태로 만듦 (drift 0 baseline).
# 정규화 함수와 동일 로직 사용 (frontmatter 유지 + sibling-only meta 도 그대로 둠)
# 실행 시 양쪽 normalize() 가 적용되므로 fixture 가 sibling raw 와 동일해도 OK.
build_baseline_fixture() {
  local fix_dir="$1"
  python3 <<PYEOF
import pathlib, yaml
fix_dir = pathlib.Path("$fix_dir")
manifest = yaml.safe_load(pathlib.Path("docs/inter-plugin-contracts/MANIFEST.yaml").read_text(encoding="utf-8"))
for contract in (manifest or {}).get("contracts", []):
    repo = contract.get("canonical_repo", "")
    repo_basename = repo.split("/")[-1]
    for fent in contract.get("files", []):
        fname = fent.get("file", "")
        status = fent.get("status", "")
        if status != "Active":
            continue
        sibling = pathlib.Path("docs/inter-plugin-contracts") / fname
        if not sibling.exists():
            continue
        # canonical fixture = sibling raw content (양쪽 normalize 가 동일 적용되므로 drift 0)
        target_dir = fix_dir / repo_basename
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / fname).write_text(sibling.read_text(encoding="utf-8"), encoding="utf-8")
PYEOF
}

# Reset all sibling files to git HEAD
restore_siblings() {
  git checkout -- docs/inter-plugin-contracts/ 2>/dev/null || true
}

# Run lint with given fixture dir and capture exit
run_lint() {
  local fix_dir="$1"
  PYTHONIOENCODING=utf-8 CFP_E_TEST_FIXTURE_DIR="$fix_dir" bash "$LINT_SCRIPT" >/dev/null 2>&1
}

assert_exit() {
  local name="$1"
  local expected="$2"
  local actual="$3"
  if [ "$actual" = "$expected" ]; then
    echo "✓ $name (exit $actual)"
    PASS=$((PASS+1))
  else
    echo "✗ $name (expected exit $expected, got $actual)"
    FAIL=$((FAIL+1))
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# T-1: positive — drift 없는 정합 상태
test_t1() {
  local fix="$TOP_TMP/t1"
  build_baseline_fixture "$fix"
  local rc=0
  run_lint "$fix" || rc=$?
  restore_siblings
  assert_exit "T-1 정합 상태 (no drift)" 0 "$rc"
}

# T-2: negative — sibling 본문 의미 변경
test_t2() {
  local fix="$TOP_TMP/t2"
  build_baseline_fixture "$fix"
  python3 -c "
import pathlib
p = pathlib.Path('docs/inter-plugin-contracts/requirements-output-v1.md')
text = p.read_text(encoding='utf-8')
text = text.replace('## 1. 흐름 개요', '## 1. 흐름 개요 (DRIFT)', 1)
p.write_text(text, encoding='utf-8')
"
  local rc=0
  run_lint "$fix" || rc=$?
  restore_siblings
  assert_exit "T-2 sibling 본문 drift (의미 변경)" 1 "$rc"
}

# T-3: negative — canonical fixture 변경
test_t3() {
  local fix="$TOP_TMP/t3"
  build_baseline_fixture "$fix"
  local target="$fix/plugin-codeforge-requirements/requirements-output-v1.md"
  python3 -c "
import pathlib
p = pathlib.Path('$target')
text = p.read_text(encoding='utf-8')
text = text.replace('## 1. 흐름 개요', '## 1. 흐름 개요 (CANONICAL DRIFT)', 1)
p.write_text(text, encoding='utf-8')
"
  local rc=0
  run_lint "$fix" || rc=$?
  restore_siblings
  assert_exit "T-3 canonical fixture drift" 1 "$rc"
}

# T-4: positive — sibling 의 **상위 SSOT 위치** section 변경 (양쪽 strip 후 무관)
test_t4() {
  local fix="$TOP_TMP/t4"
  build_baseline_fixture "$fix"
  python3 -c "
import pathlib
p = pathlib.Path('docs/inter-plugin-contracts/requirements-output-v1.md')
text = p.read_text(encoding='utf-8')
text = text.replace('**상위 SSOT 위치**:', '**상위 SSOT 위치 (변경됨)**:', 1)
p.write_text(text, encoding='utf-8')
"
  local rc=0
  run_lint "$fix" || rc=$?
  restore_siblings
  assert_exit "T-4 sibling meta section 변경 (정규화 무시)" 0 "$rc"
}

# T-5: positive — line ending CRLF (정규화 후 동일)
test_t5() {
  local fix="$TOP_TMP/t5"
  build_baseline_fixture "$fix"
  python3 -c "
import pathlib
p = pathlib.Path('docs/inter-plugin-contracts/requirements-output-v1.md')
text = p.read_text(encoding='utf-8')
text_crlf = text.replace('\n', '\r\n')
with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(text_crlf)
"
  local rc=0
  run_lint "$fix" || rc=$?
  restore_siblings
  assert_exit "T-5 line ending CRLF (정규화 후 동일)" 0 "$rc"
}

# T-6: positive — Archived entry 자동 skip (review_verdict v1)
# baseline state 자체에 review_verdict v1 (Archived) 가 포함되어 있으므로
# T-1 과 동일한 검증 (skip count 1 확인은 stdout grep 으로 별도 가능 — 본 case 는 exit 0 만 확인)
test_t6() {
  local fix="$TOP_TMP/t6"
  build_baseline_fixture "$fix"
  local rc=0
  run_lint "$fix" || rc=$?
  restore_siblings
  assert_exit "T-6 Archived entry 자동 skip" 0 "$rc"
}

# T-7: negative — Active canonical 404 (fixture 삭제로 mock)
test_t7() {
  local fix="$TOP_TMP/t7"
  build_baseline_fixture "$fix"
  rm "$fix/plugin-codeforge-requirements/requirements-output-v1.md"
  local rc=0
  run_lint "$fix" || rc=$?
  restore_siblings
  assert_exit "T-7 Active canonical 404" 1 "$rc"
}

# T-8: positive — trailing whitespace 차이 (정규화 후 동일)
test_t8() {
  local fix="$TOP_TMP/t8"
  build_baseline_fixture "$fix"
  python3 -c "
import pathlib
p = pathlib.Path('docs/inter-plugin-contracts/requirements-output-v1.md')
text = p.read_text(encoding='utf-8')
text_ws = '\n'.join(line + '   ' for line in text.split('\n'))
p.write_text(text_ws, encoding='utf-8')
"
  local rc=0
  run_lint "$fix" || rc=$?
  restore_siblings
  assert_exit "T-8 trailing whitespace (정규화 후 동일)" 0 "$rc"
}

# Run all tests
test_t1
test_t2
test_t3
test_t4
test_t5
test_t6
test_t7
test_t8

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" = "0" ]
