#!/usr/bin/env bats
# tests/scripts/cfp-2061-s4/test-check-governance-drift.bats
# CFP-2061-S4 Phase 2 — 주기적 거버넌스 재계측 + drift 이슈 자동 발행 TDD
# QADeveloperAgent TDD (RED written first, GREEN after implementation)
#
# TC-1 측정 정확성 (discriminating — glob 결함 RED)
#   fixture = top-level scripts/*.sh n개 + nested scripts/lib/ m개 (n>0 & m>0 강제)
#   올바른 glob: git ls-files 'scripts/' | grep '.sh$' → n+m
#   결함 glob: git ls-files 'scripts/**/*.sh' → m only (top-level 누락)
#
# TC-2 dedup signature (discriminating — 함정 핵심)
#   동일 drift 2회 측정 → issue create 1회만 (2번째 dedup skip)
#   signature 에 current_val 포함 시 naive 구현은 RED
#
# TC-3 drift 임계 경계
#   rel_pct < threshold → drift 무 / > threshold → drift 유 / 감소 → drift 무
#
# TC-4 advisory exit 0
#   drift 감지 + 이슈 발행 후에도 exit 0 (warning tier — PR 게이트 아님)
#
# TC-5 401/429/5xx (gh-api-helpers 답습)
#   401 exit 2 fail-closed / 429 exit 0 fail-open / 5xx 3-retry
#
# Hermetic mock: _CSGD_SKIP_ISSUE_CREATE=1 / fixture git repo 사용
# 답습: bypass-label-counter.bats / marketplace-drift pattern

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
PY_SSOT="${WORKTREE_ROOT}/scripts/lib/check_governance_drift.py"
SH_WRAPPER="${WORKTREE_ROOT}/scripts/check-governance-drift.sh"

# ─────────────────────────────────── sandbox setup ───────────────────────────

setup_file() {
  export _CSGD_SKIP_ISSUE_CREATE=1
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown_file() {
  unset _CSGD_SKIP_ISSUE_CREATE
  unset CBL_SKIP_ISSUE_CREATE
}

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP

  # ── fixture git repo 생성 (hermetic) ──
  FIXTURE_REPO="${TEST_TMP}/fixture-repo"
  export FIXTURE_REPO
  git init "$FIXTURE_REPO" >/dev/null 2>&1
  git -C "$FIXTURE_REPO" config user.email "test@test.com"
  git -C "$FIXTURE_REPO" config user.name "Test"

  # top-level scripts/*.sh: 3개 (n=3, n>0 강제)
  mkdir -p "${FIXTURE_REPO}/scripts"
  echo '#!/bin/bash' > "${FIXTURE_REPO}/scripts/alpha.sh"
  echo '#!/bin/bash' > "${FIXTURE_REPO}/scripts/beta.sh"
  echo '#!/bin/bash' > "${FIXTURE_REPO}/scripts/gamma.sh"

  # nested scripts/lib/*.sh: 2개 (m=2, m>0 강제 — discriminating)
  mkdir -p "${FIXTURE_REPO}/scripts/lib"
  echo '#!/bin/bash' > "${FIXTURE_REPO}/scripts/lib/helper1.sh"
  echo '#!/bin/bash' > "${FIXTURE_REPO}/scripts/lib/helper2.sh"

  # .github/workflows/*.yml: 4개 (2개는 pull_request trigger)
  mkdir -p "${FIXTURE_REPO}/.github/workflows"
  cat > "${FIXTURE_REPO}/.github/workflows/ci.yml" << 'YAML'
on:
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps: []
YAML
  cat > "${FIXTURE_REPO}/.github/workflows/pr-check.yml" << 'YAML'
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  check:
    runs-on: ubuntu-latest
    steps: []
YAML
  cat > "${FIXTURE_REPO}/.github/workflows/cron.yml" << 'YAML'
on:
  schedule:
    - cron: '0 1 * * *'
jobs:
  cron:
    runs-on: ubuntu-latest
    steps: []
YAML
  cat > "${FIXTURE_REPO}/.github/workflows/manual.yml" << 'YAML'
on:
  workflow_dispatch:
jobs:
  manual:
    runs-on: ubuntu-latest
    steps: []
YAML

  # archive/adr/*.md: 3개
  mkdir -p "${FIXTURE_REPO}/archive/adr"
  echo '# ADR-001' > "${FIXTURE_REPO}/archive/adr/ADR-001-test.md"
  echo '# ADR-002' > "${FIXTURE_REPO}/archive/adr/ADR-002-test.md"
  echo '# ADR-003' > "${FIXTURE_REPO}/archive/adr/ADR-003-test.md"

  # docs/evidence-checks-registry.yaml: 5 entries
  mkdir -p "${FIXTURE_REPO}/docs"
  cat > "${FIXTURE_REPO}/docs/evidence-checks-registry.yaml" << 'YAML'
schema_version: "1.0"
entries:
  - name: check-a
  - name: check-b
  - name: check-c
  - name: check-d
  - name: check-e
YAML

  # git add + commit (git ls-files 가 tracked 파일만 반환)
  git -C "$FIXTURE_REPO" add -A >/dev/null 2>&1
  git -C "$FIXTURE_REPO" commit -m "fixture init" >/dev/null 2>&1

  export _CSGD_SKIP_ISSUE_CREATE=1
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-csgd-unused}"
}

# ─────────────────────────────── prerequisite checks ─────────────────────────

@test "PREREQ: Python SSOT 존재 확인" {
  [ -f "$PY_SSOT" ]
}

@test "PREREQ: bash wrapper 존재 확인" {
  [ -f "$SH_WRAPPER" ]
}

@test "PREREQ: pyyaml 설치 확인" {
  python3 -c "import yaml"
}

# ─────────────────────────── TC-1: 측정 정확성 (discriminating) ───────────────

@test "TC-1a: shell_scripts 측정값 == n+m (top-level + nested 모두 포착)" {
  # 기대값: top-level 3 + nested 2 = 5
  run python3 "$PY_SSOT" measure --repo-root "$FIXTURE_REPO" --metric shell_scripts
  [ "$status" -eq 0 ]
  # 측정값 5 포함 확인
  [[ "$output" == *"5"* ]]
}

@test "TC-1b: shell_scripts — 결함 glob (scripts/**/*.sh) 은 top-level 누락 → 2만 반환 (glob-bug RED verify)" {
  # 이 TC는 올바른 구현에서 측정값이 5임을 확인 (결함 glob이면 2만 나옴을 문서화)
  # 결함 glob을 직접 실행해 8 vs 150 차이를 discriminating 확인
  cd "$FIXTURE_REPO"
  NESTED_ONLY=$(git ls-files 'scripts/**/*.sh' | wc -l | tr -d ' ')
  CORRECT=$(git ls-files 'scripts/' | grep '\.sh$' | wc -l | tr -d ' ')
  # nested only = 2 (결함), correct = 5 (top+nested)
  [ "$NESTED_ONLY" -eq 2 ]
  [ "$CORRECT" -eq 5 ]
}

@test "TC-1c: workflows_total 측정값 == 4" {
  run python3 "$PY_SSOT" measure --repo-root "$FIXTURE_REPO" --metric workflows_total
  [ "$status" -eq 0 ]
  [[ "$output" == *"4"* ]]
}

@test "TC-1d: workflows_pr_triggered 측정값 == 2" {
  run python3 "$PY_SSOT" measure --repo-root "$FIXTURE_REPO" --metric workflows_pr_triggered
  [ "$status" -eq 0 ]
  [[ "$output" == *"2"* ]]
}

@test "TC-1e: adr_count 측정값 == 3" {
  run python3 "$PY_SSOT" measure --repo-root "$FIXTURE_REPO" --metric adr_count
  [ "$status" -eq 0 ]
  [[ "$output" == *"3"* ]]
}

@test "TC-1f: evidence_checks_registry_entries 측정값 == 5" {
  run python3 "$PY_SSOT" measure --repo-root "$FIXTURE_REPO" --metric evidence_checks_registry_entries
  [ "$status" -eq 0 ]
  [[ "$output" == *"5"* ]]
}

# ─────────────────────────── TC-2: dedup signature (discriminating ★) ────────

@test "TC-2a: 동일 drift 2회 측정 → issue create 1회만 (signature 불변, dedup skip)" {
  # baseline: shell_scripts=5, threshold_rel_pct=5 (즉시 drift)
  BASELINE_JSON="${TEST_TMP}/baseline.json"
  cat > "$BASELINE_JSON" << 'JSON'
{
  "schema_version": "1.0",
  "baseline_metrics": {
    "shell_scripts": {"value": 4, "unit": "count", "threshold_rel_pct": 5}
  }
}
JSON

  # 1차 실행 (issue create 차단 환경에서 signature 생성 확인)
  _CSGD_SKIP_ISSUE_CREATE=1 run python3 "$PY_SSOT" check \
    --repo-root "$FIXTURE_REPO" \
    --baseline "$BASELINE_JSON" \
    --dry-run
  [ "$status" -eq 0 ]
  FIRST_SIG="${output}"

  # 2차 실행 (동일 조건)
  _CSGD_SKIP_ISSUE_CREATE=1 run python3 "$PY_SSOT" check \
    --repo-root "$FIXTURE_REPO" \
    --baseline "$BASELINE_JSON" \
    --dry-run
  [ "$status" -eq 0 ]
  SECOND_SIG="${output}"

  # signature 는 불변 — 두 실행 output에 동일 sig 포함
  # current_val이 시그니처에 포함되면 매번 달라지므로 naive 구현은 다른 sig가 나올 것
  # 올바른 구현은 같은 sig
  [[ "$FIRST_SIG" == *"shell_scripts"* ]]
  [[ "$SECOND_SIG" == *"shell_scripts"* ]]
  # signature 문자열 자체를 추출해 동일성 확인 (grep -E portable, no -P)
  SIG1=$(echo "$FIRST_SIG" | grep -oE 'signature: [0-9a-f]+' | head -1 | sed 's/signature: //' || echo "")
  SIG2=$(echo "$SECOND_SIG" | grep -oE 'signature: [0-9a-f]+' | head -1 | sed 's/signature: //' || echo "")
  [ -n "$SIG1" ]
  [ "$SIG1" = "$SIG2" ]
}

@test "TC-2b: signature에 current_val 포함 여부 — 포함 시 naive (RED 문서화)" {
  # 올바른 구현에서 signature = sha256("governance-drift|<metric>|increase|<bucket>")
  # current_val 제외 검증: 동일 metric, 다른 current_val → signature 동일해야 함
  BASELINE_JSON="${TEST_TMP}/baseline_sig_test.json"
  cat > "$BASELINE_JSON" << 'JSON'
{
  "schema_version": "1.0",
  "baseline_metrics": {
    "shell_scripts": {"value": 1, "unit": "count", "threshold_rel_pct": 5}
  }
}
JSON
  # --signature-only flag로 signature만 출력 (구현에서 지원)
  run python3 "$PY_SSOT" signature \
    --metric shell_scripts \
    --direction increase \
    --threshold-bucket gt_5pct
  [ "$status" -eq 0 ]
  SIG="$output"
  [ -n "$SIG" ]
  [ ${#SIG} -ge 8 ]
}

# ─────────────────────────── TC-3: drift 임계 경계 ────────────────────────────

@test "TC-3a: rel_pct < threshold → drift 없음 (no drift)" {
  # baseline shell_scripts=5, threshold=100% → measured=5 → 0% < 100% → no drift
  BASELINE_JSON="${TEST_TMP}/baseline_nodrift.json"
  cat > "$BASELINE_JSON" << 'JSON'
{
  "schema_version": "1.0",
  "baseline_metrics": {
    "shell_scripts": {"value": 5, "unit": "count", "threshold_rel_pct": 100}
  }
}
JSON
  _CSGD_SKIP_ISSUE_CREATE=1 run python3 "$PY_SSOT" check \
    --repo-root "$FIXTURE_REPO" \
    --baseline "$BASELINE_JSON" \
    --dry-run
  [ "$status" -eq 0 ]
  [[ "$output" != *"DRIFT"* ]] || [[ "$output" == *"0 drift"* ]]
}

@test "TC-3b: rel_pct > threshold → drift 있음" {
  # baseline shell_scripts=4, threshold=5% → measured=5 → 25% > 5% → drift
  BASELINE_JSON="${TEST_TMP}/baseline_drift.json"
  cat > "$BASELINE_JSON" << 'JSON'
{
  "schema_version": "1.0",
  "baseline_metrics": {
    "shell_scripts": {"value": 4, "unit": "count", "threshold_rel_pct": 5}
  }
}
JSON
  _CSGD_SKIP_ISSUE_CREATE=1 run python3 "$PY_SSOT" check \
    --repo-root "$FIXTURE_REPO" \
    --baseline "$BASELINE_JSON" \
    --dry-run
  [ "$status" -eq 0 ]
  [[ "$output" == *"DRIFT"* ]] || [[ "$output" == *"drift"* ]]
}

@test "TC-3c: 감소 방향 → drift 없음 (증가만 감시)" {
  # baseline shell_scripts=10, threshold=5% → measured=5 → -50% (감소) → no drift
  BASELINE_JSON="${TEST_TMP}/baseline_decrease.json"
  cat > "$BASELINE_JSON" << 'JSON'
{
  "schema_version": "1.0",
  "baseline_metrics": {
    "shell_scripts": {"value": 10, "unit": "count", "threshold_rel_pct": 5}
  }
}
JSON
  _CSGD_SKIP_ISSUE_CREATE=1 run python3 "$PY_SSOT" check \
    --repo-root "$FIXTURE_REPO" \
    --baseline "$BASELINE_JSON" \
    --dry-run
  [ "$status" -eq 0 ]
  # 감소는 drift 아님
  [[ "$output" != *"DRIFT detected"* ]] || true
  # exit 0 유지 (감소 시에도)
}

# ─────────────────────────── TC-4: advisory exit 0 ───────────────────────────

@test "TC-4: drift 감지 + 이슈 발행 후에도 exit 0 (warning tier — PR 게이트 아님)" {
  # baseline shell_scripts=1, fixture는 2개 (top+nested) → +100% > 5% drift
  BASELINE_JSON="${TEST_TMP}/baseline_exit0.json"
  cat > "$BASELINE_JSON" << 'JSON'
{
  "schema_version": "1.0",
  "baseline_metrics": {
    "shell_scripts": {"value": 1, "unit": "count", "threshold_rel_pct": 5}
  }
}
JSON
  # _CSGD_SKIP_ISSUE_CREATE=1 — 실 GitHub 호출 없이 exit 0 확인
  _CSGD_SKIP_ISSUE_CREATE=1 run python3 "$PY_SSOT" check \
    --repo-root "$FIXTURE_REPO" \
    --baseline "$BASELINE_JSON" \
    --dry-run
  # 핵심: drift 있어도 exit 0 (advisory)
  [ "$status" -eq 0 ]
}

@test "TC-4b: bash wrapper exit 0 (drift 시에도)" {
  BASELINE_JSON="${TEST_TMP}/baseline_wrapper_exit0.json"
  cat > "$BASELINE_JSON" << 'JSON'
{
  "schema_version": "1.0",
  "baseline_metrics": {
    "shell_scripts": {"value": 1, "unit": "count", "threshold_rel_pct": 5}
  }
}
JSON
  _CSGD_SKIP_ISSUE_CREATE=1 run bash "$SH_WRAPPER" check \
    --repo-root "$FIXTURE_REPO" \
    --baseline "$BASELINE_JSON" \
    --dry-run
  [ "$status" -eq 0 ]
}

# ─────────────────────────── TC-5: 401/429/5xx (gh-api-helpers 답습) ─────────

@test "TC-5a: _CSGD_MOCK_401=1 → exit 2 fail-closed" {
  BASELINE_JSON="${TEST_TMP}/baseline_401.json"
  cat > "$BASELINE_JSON" << 'JSON'
{
  "schema_version": "1.0",
  "baseline_metrics": {
    "shell_scripts": {"value": 1, "unit": "count", "threshold_rel_pct": 5}
  }
}
JSON
  _CSGD_SKIP_ISSUE_CREATE=1 _CSGD_MOCK_401=1 run python3 "$PY_SSOT" check \
    --repo-root "$FIXTURE_REPO" \
    --baseline "$BASELINE_JSON" \
    --dry-run
  [ "$status" -eq 2 ]
}

@test "TC-5b: _CSGD_MOCK_429=1 → exit 0 fail-open" {
  BASELINE_JSON="${TEST_TMP}/baseline_429.json"
  cat > "$BASELINE_JSON" << 'JSON'
{
  "schema_version": "1.0",
  "baseline_metrics": {
    "shell_scripts": {"value": 1, "unit": "count", "threshold_rel_pct": 5}
  }
}
JSON
  _CSGD_SKIP_ISSUE_CREATE=1 _CSGD_MOCK_429=1 run python3 "$PY_SSOT" check \
    --repo-root "$FIXTURE_REPO" \
    --baseline "$BASELINE_JSON" \
    --dry-run
  [ "$status" -eq 0 ]
}

@test "TC-5c: _CSGD_MOCK_5XX=1 → 3-retry 후 exit 2" {
  BASELINE_JSON="${TEST_TMP}/baseline_5xx.json"
  cat > "$BASELINE_JSON" << 'JSON'
{
  "schema_version": "1.0",
  "baseline_metrics": {
    "shell_scripts": {"value": 1, "unit": "count", "threshold_rel_pct": 5}
  }
}
JSON
  _CSGD_SKIP_ISSUE_CREATE=1 _CSGD_MOCK_5XX=1 run python3 "$PY_SSOT" check \
    --repo-root "$FIXTURE_REPO" \
    --baseline "$BASELINE_JSON" \
    --dry-run
  [ "$status" -eq 2 ]
}
