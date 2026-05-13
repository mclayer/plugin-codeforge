#!/usr/bin/env bash
# test_check_evidence_registry_naming.sh
# CFP-508 — check-evidence-registry-naming.sh 단위 테스트 (3 test case)
#
# Test case:
#   1. OK case: 정상 registry state (현재 repo HEAD) → exit 0
#   2. missing workflow file case: 가짜 workflow path 추가 temp yaml → exit 1
#   3. --help case: --help flag → exit 0 + header 출력
#
# Usage:
#   bash tests/scripts/test_check_evidence_registry_naming.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT=$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/../..")
HELPER="$REPO_ROOT/scripts/check-evidence-registry-naming.sh"
REGISTRY="$REPO_ROOT/docs/evidence-checks-registry.yaml"

# Color output (TERM-aware)
if [[ -t 1 ]]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  NC='\033[0m'
else
  RED=''
  GREEN=''
  NC=''
fi

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

assert_true() {
  local desc="$1"
  local condition="$2"

  TESTS_RUN=$((TESTS_RUN + 1))
  if eval "$condition"; then
    echo -e "${GREEN}PASS${NC} $desc"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}FAIL${NC} $desc"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

echo "==================================================================="
echo "CFP-508 — check-evidence-registry-naming.sh 단위 테스트"
echo "Target: $HELPER"
echo "==================================================================="
echo ""

# Pre-flight — helper file 존재 확인
if [[ ! -f "$HELPER" ]]; then
  echo -e "${RED}FATAL${NC} helper script 부재: $HELPER"
  exit 2
fi

if [[ ! -f "$REGISTRY" ]]; then
  echo -e "${RED}FATAL${NC} registry file 부재: $REGISTRY"
  exit 2
fi

# ─── temp file 관리 ────────────────────────────────────────────────────────

TMPFILES=()
cleanup() {
  for f in "${TMPFILES[@]:-}"; do
    if [[ -d "$f" ]]; then
      rm -rf "$f"
    elif [[ -f "$f" ]]; then
      rm -f "$f"
    fi
  done
}
trap cleanup EXIT

# ─── [1/3] OK case: 현재 repo HEAD 정상 registry → exit 0 ────────────────

echo "[1/3] OK case — 현재 repo HEAD registry 정상 검증 → exit 0"
echo "-------------------------------------------------------------------"

TMPOUT_OK="$(mktemp /tmp/test_ev_naming_ok_XXXXXX.txt)"
TMPFILES+=("$TMPOUT_OK")
set +e
(cd "$REPO_ROOT" && bash "$HELPER") > "$TMPOUT_OK" 2>&1
EXIT_OK=$?
set -e
OUTPUT_OK="$(cat "$TMPOUT_OK")"

assert_true "(1a) exit code = 0 (PASS)" \
  "[ $EXIT_OK -eq 0 ]"

assert_true "(1b) stdout non-empty" \
  "[ -n \"$OUTPUT_OK\" ]"

assert_true "(1c) 'PASS' or 'OK' keyword 존재" \
  "echo \"\$OUTPUT_OK\" | grep -qiE '(PASS|OK)'"

assert_true "(1d) 'VIOLATION' 없음" \
  "! echo \"\$OUTPUT_OK\" | grep -qi 'VIOLATION'"

echo ""

# ─── [2/3] missing workflow file case → exit 1 ──────────────────────────

echo "[2/3] missing workflow file case — 가짜 workflow path entry → exit 1"
echo "-------------------------------------------------------------------"

# 현재 registry yaml 에 가짜 workflow path entry 를 append 한 temp file 생성
TEMP_REGISTRY="$(mktemp /tmp/test_evidence_registry_naming_XXXXXX.yaml)"
TMPFILES+=("$TEMP_REGISTRY")

# 실제 registry 복사 후 가짜 entry append
cp "$REGISTRY" "$TEMP_REGISTRY"
cat >> "$TEMP_REGISTRY" << 'YAML_APPEND'

  # TEST-ONLY: 가짜 workflow path entry (check-evidence-registry-naming.sh 테스트용)
  - name: test-fake-entry-for-naming-test
    description: |
      테스트 전용 가짜 entry — workflow file 부재 케이스 검증 (CFP-508 test).
    detect_command: bash scripts/check-nonexistent-fake-script.sh
    workflow: templates/github-workflows/nonexistent-fake-workflow-9999.yml
    current_tier: warning
    bypass_label: hotfix-bypass:test-fake
    promotion_criteria:
      pr_cumulative_min: 20
      failure_threshold: 0
      sibling_dependencies: []
      evidence_artifacts:
        - github_actions_run_history_url
    introduced_by: TEST-ONLY
    introduced_date: 2026-01-01
    owner_adr: ADR-060
    carrier_adr: ADR-060
    recurrence:
      count: 0
      promotion_trigger: none
    status: Active
YAML_APPEND

# REGISTRY_PATH 를 temp 로 교체하여 실행 (python3 heredoc 안에서 REGISTRY_PATH 는 고정이므로
# 환경 변수나 symlink 교체 전략 필요 — script 가 cwd 기준 docs/evidence-checks-registry.yaml 을
# 직접 읽으므로 임시 디렉토리에서 실행)

TMPDIR_TEST="$(mktemp -d /tmp/test_evidence_naming_XXXXXX)"
TMPFILES+=("$TMPDIR_TEST/docs/evidence-checks-registry.yaml")

# temp dir 안에 필요한 디렉토리 구조 생성 (symlink)
mkdir -p "$TMPDIR_TEST/docs"
mkdir -p "$TMPDIR_TEST/scripts"
mkdir -p "$TMPDIR_TEST/templates/github-workflows"
mkdir -p "$TMPDIR_TEST/.github/workflows"

# registry yaml → temp (가짜 entry 포함)
cp "$TEMP_REGISTRY" "$TMPDIR_TEST/docs/evidence-checks-registry.yaml"

# scripts/ 심볼릭 링크 (helper 접근 필요)
# templates/github-workflows/ → 실제 파일들 (기존 workflow 존재 검증용)
# 실제 workflow 파일들 복사 (파일 존재 검증 PASS 위해)
cp -r "$REPO_ROOT/templates/github-workflows/"*.yml "$TMPDIR_TEST/templates/github-workflows/" 2>/dev/null || true
cp -r "$REPO_ROOT/.github/workflows/"*.yml "$TMPDIR_TEST/.github/workflows/" 2>/dev/null || true

# check-evidence-registry-naming.sh 를 temp dir 에서 실행
# script 가 `cd "$(dirname "$0")/.."` 로 repo root 를 설정하므로
# scripts/ 아래에 helper copy 후 temp dir 를 작업 디렉토리로 사용
mkdir -p "$TMPDIR_TEST/scripts"
cp "$HELPER" "$TMPDIR_TEST/scripts/check-evidence-registry-naming.sh"

# exit code 와 output 을 분리 캡처 (set -euo pipefail 환경에서 || true 로 exit code 보존)
TMPOUT_MISSING="$(mktemp /tmp/test_ev_naming_out_XXXXXX.txt)"
TMPFILES+=("$TMPOUT_MISSING")
set +e
(cd "$TMPDIR_TEST" && bash "$TMPDIR_TEST/scripts/check-evidence-registry-naming.sh") > "$TMPOUT_MISSING" 2>&1
EXIT_MISSING=$?
set -e
OUTPUT_MISSING="$(cat "$TMPOUT_MISSING")"

# temp dir 정리
rm -rf "$TMPDIR_TEST"

assert_true "(2a) exit code = 1 (violation — missing workflow file)" \
  "[ $EXIT_MISSING -eq 1 ]"

assert_true "(2b) stderr/output 에 'VIOLATION' 또는 'violation' 포함" \
  "echo \"\$OUTPUT_MISSING\" | grep -qiE '(VIOLATION|violation|부재)'"

assert_true "(2c) 가짜 entry name 'test-fake-entry-for-naming-test' 언급" \
  "echo \"\$OUTPUT_MISSING\" | grep -q 'test-fake-entry-for-naming-test'"

echo ""

# ─── [3/3] --help case → exit 0 + header 출력 ──────────────────────────

echo "[3/3] --help case — header 출력 + exit 0"
echo "-------------------------------------------------------------------"

TMPOUT_HELP="$(mktemp /tmp/test_ev_naming_help_XXXXXX.txt)"
TMPFILES+=("$TMPOUT_HELP")
set +e
bash "$HELPER" --help > "$TMPOUT_HELP" 2>&1
EXIT_HELP=$?
set -e
OUTPUT_HELP="$(cat "$TMPOUT_HELP")"

assert_true "(3a) exit code = 0 (--help)" \
  "[ $EXIT_HELP -eq 0 ]"

assert_true "(3b) output non-empty" \
  "[ -n \"$OUTPUT_HELP\" ]"

assert_true "(3c) 'CFP-508' keyword 존재 (header)" \
  "echo \"\$OUTPUT_HELP\" | grep -q 'CFP-508'"

assert_true "(3d) 'ADR-060' keyword 존재 (carrier reference)" \
  "echo \"\$OUTPUT_HELP\" | grep -q 'ADR-060'"

echo ""
echo "==================================================================="
echo "Test summary: $TESTS_PASSED / $TESTS_RUN passed, $TESTS_FAILED failed"
echo "==================================================================="

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi

exit 0
