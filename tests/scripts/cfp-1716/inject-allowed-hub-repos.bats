#!/usr/bin/env bats
# CFP-1716: ALLOWED_HUB_REPOS consumer 확장 주입 메커니즘
# Test: inject-allowed-hub-repos.sh idempotent 후처리

setup() {
  TEST_TEMP_DIR="$(mktemp -d)"
  REPO_ROOT="${TEST_TEMP_DIR}/consumer-repo"
  WORKFLOWS_DIR="${REPO_ROOT}/.github/workflows"
  OVERLAY_DIR="${REPO_ROOT}/.claude/_overlay"

  mkdir -p "$WORKFLOWS_DIR" "$OVERLAY_DIR"

  # Test fixture: phase-gate-mergeable.yml (template default)
  cat > "${WORKFLOWS_DIR}/phase-gate-mergeable.yml" << 'EOF'
name: phase-gate-mergeable
on: [pull_request]
env:
  ALLOWED_HUB_REPOS: "github.com/mclayer/codeforge-internal-docs"
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
EOF

  # Test fixture: phase-gate-auto-cleanup.yml (template default)
  cat > "${WORKFLOWS_DIR}/phase-gate-auto-cleanup.yml" << 'EOF'
name: phase-gate-auto-cleanup
on: [schedule]
env:
  ALLOWED_HUB_REPOS: "github.com/mclayer/codeforge-internal-docs"
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
EOF
}

teardown() {
  rm -rf "$TEST_TEMP_DIR"
}

# Test 1: project.yaml 부재 → no-op exit 0
@test "project.yaml 부재 시 no-op" {
  bash "${BATS_TEST_DIRNAME}/../../../scripts/inject-allowed-hub-repos.sh" \
    --repo "$REPO_ROOT" \
    --dry-run

  # Workflows 값이 변경되지 않았는지 확인
  grep -q 'ALLOWED_HUB_REPOS: "github.com/mclayer/codeforge-internal-docs"' \
    "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"
}

# Test 2: project.yaml 존재, phase_gate 블록 없음 → no-op exit 0
@test "project.yaml phase_gate 블록 없음 시 no-op" {
  cat > "${OVERLAY_DIR}/project.yaml" << 'EOF'
project:
  name: test-project
github:
  org: mclayer
  repo: test-repo
  default_branch: main
EOF

  bash "${BATS_TEST_DIRNAME}/../../../scripts/inject-allowed-hub-repos.sh" \
    --repo "$REPO_ROOT" \
    --dry-run

  # Workflows 값이 변경되지 않았는지 확인
  grep -q 'ALLOWED_HUB_REPOS: "github.com/mclayer/codeforge-internal-docs"' \
    "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"
}

# Test 3: project.yaml 존재, allowed_hub_repos 선언 → 값 확장
@test "project.yaml allowed_hub_repos 확장 시 값 주입" {
  cat > "${OVERLAY_DIR}/project.yaml" << 'EOF'
project:
  name: test-project
github:
  org: mclayer
  repo: test-repo
  default_branch: main
phase_gate:
  allowed_hub_repos:
    - "github.com/mclayer/mctrader-hub"
    - "github.com/internal/internal-hub"
EOF

  # Dry-run (실제 파일 수정 안 함)
  output=$(bash "${BATS_TEST_DIRNAME}/../../../scripts/inject-allowed-hub-repos.sh" \
    --repo "$REPO_ROOT" \
    --dry-run 2>&1)

  # Dry-run 출력에 merged value 포함되는지 확인
  echo "$output" | grep -q "github.com/mclayer/codeforge-internal-docs"
  echo "$output" | grep -q "github.com/mclayer/mctrader-hub"
  echo "$output" | grep -q "github.com/internal/internal-hub"
}

# Test 4: 실제 파일 수정 (non-dry-run)
@test "실제 파일 수정 (allowed_hub_repos 확장)" {
  cat > "${OVERLAY_DIR}/project.yaml" << 'EOF'
project:
  name: test-project
github:
  org: mclayer
  repo: test-repo
  default_branch: main
phase_gate:
  allowed_hub_repos:
    - "github.com/mclayer/mctrader-hub"
EOF

  # 실행 (dry-run 아님)
  bash "${BATS_TEST_DIRNAME}/../../../scripts/inject-allowed-hub-repos.sh" \
    --repo "$REPO_ROOT"

  # phase-gate-mergeable.yml 값이 확장되었는지 확인
  grep -q 'ALLOWED_HUB_REPOS: "github.com/mclayer/codeforge-internal-docs,github.com/mclayer/mctrader-hub"' \
    "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"

  # phase-gate-auto-cleanup.yml 값도 확장되었는지 확인
  grep -q 'ALLOWED_HUB_REPOS: "github.com/mclayer/codeforge-internal-docs,github.com/mclayer/mctrader-hub"' \
    "${WORKFLOWS_DIR}/phase-gate-auto-cleanup.yml"
}

# Test 5: Idempotent (2회 실행 = 동일 결과)
@test "Idempotent (2회 실행 동일)" {
  cat > "${OVERLAY_DIR}/project.yaml" << 'EOF'
project:
  name: test-project
github:
  org: mclayer
  repo: test-repo
  default_branch: main
phase_gate:
  allowed_hub_repos:
    - "github.com/mclayer/mctrader-hub"
EOF

  # 1차 실행
  bash "${BATS_TEST_DIRNAME}/../../../scripts/inject-allowed-hub-repos.sh" \
    --repo "$REPO_ROOT"

  # 1차 결과 저장
  result1=$(cat "${WORKFLOWS_DIR}/phase-gate-mergeable.yml")

  # 2차 실행
  bash "${BATS_TEST_DIRNAME}/../../../scripts/inject-allowed-hub-repos.sh" \
    --repo "$REPO_ROOT"

  # 2차 결과 저장
  result2=$(cat "${WORKFLOWS_DIR}/phase-gate-mergeable.yml")

  # 결과 동일 확인 (idempotent)
  [ "$result1" = "$result2" ]
}

# Test 6: Never-reduce (기존 default 보존)
@test "Never-reduce (기본값 축소 불가)" {
  cat > "${OVERLAY_DIR}/project.yaml" << 'EOF'
project:
  name: test-project
github:
  org: mclayer
  repo: test-repo
  default_branch: main
phase_gate:
  allowed_hub_repos:
    - "github.com/mclayer/mctrader-hub"
EOF

  bash "${BATS_TEST_DIRNAME}/../../../scripts/inject-allowed-hub-repos.sh" \
    --repo "$REPO_ROOT"

  # 기본값이 보존되었는지 확인
  grep -q "github.com/mclayer/codeforge-internal-docs" \
    "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"

  # 추가값도 포함되었는지 확인
  grep -q "github.com/mclayer/mctrader-hub" \
    "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"
}

# Test 7: Dedup (중복 entry 제거)
@test "Dedup (중복 entry 제거)" {
  cat > "${OVERLAY_DIR}/project.yaml" << 'EOF'
project:
  name: test-project
github:
  org: mclayer
  repo: test-repo
  default_branch: main
phase_gate:
  allowed_hub_repos:
    - "github.com/mclayer/mctrader-hub"
    - "github.com/mclayer/mctrader-hub"
    - "github.com/mclayer/codeforge-internal-docs"
EOF

  bash "${BATS_TEST_DIRNAME}/../../../scripts/inject-allowed-hub-repos.sh" \
    --repo "$REPO_ROOT"

  # 결과 확인: 중복 제거되어야 함 (단, order 보존)
  # Expected: "github.com/mclayer/codeforge-internal-docs,github.com/mclayer/mctrader-hub"
  grep -q 'ALLOWED_HUB_REPOS: "github.com/mclayer/codeforge-internal-docs,github.com/mclayer/mctrader-hub"' \
    "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"
}

# Test 8: 부적합 entry skip (format validation)
@test "부적합 entry skip (format validation)" {
  cat > "${OVERLAY_DIR}/project.yaml" << 'EOF'
project:
  name: test-project
github:
  org: mclayer
  repo: test-repo
  default_branch: main
phase_gate:
  allowed_hub_repos:
    - "invalid-format"
    - "github.com/mclayer/mctrader-hub"
    - "http://bad.url"
EOF

  output=$(bash "${BATS_TEST_DIRNAME}/../../../scripts/inject-allowed-hub-repos.sh" \
    --repo "$REPO_ROOT" 2>&1)

  # 부적합 entry에 대한 warn 발생 확인
  echo "$output" | grep -q "Invalid repo entry format"

  # 적합한 entry만 주입됨
  grep -q "github.com/mclayer/mctrader-hub" \
    "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"
}

# Test 9: mixed-quote 회귀 — mismatch 파일이 먼저 와도 정상 파일 주입 보장
@test "mixed-quote mismatch 앞에 와도 정상 워크플로 주입 계속됨 (F-CR-1716-1 회귀)" {
  cat > "${OVERLAY_DIR}/project.yaml" << 'YAML'
project:
  name: test-project
github:
  org: mclayer
  repo: test-repo
  default_branch: main
phase_gate:
  allowed_hub_repos:
    - "github.com/mclayer/mctrader-hub"
YAML

  # aaa-mismatch.yml: ALLOWED_HUB_REPOS 값에 single-quote (quote style mismatch)
  # 파일명이 a 로 시작 → find 정렬상 먼저 처리됨
  cat > "${WORKFLOWS_DIR}/aaa-mismatch.yml" << 'FIXTURE'
name: aaa-mismatch
on: [pull_request]
env:
  ALLOWED_HUB_REPOS: 'github.com/mclayer/codeforge-internal-docs'
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
FIXTURE

  # 기존 phase-gate-mergeable.yml = double-quote (정상)

  # 단언 (a): 스크립트가 abort 없이 정상 종료
  run bash "${BATS_TEST_DIRNAME}/../../../scripts/inject-allowed-hub-repos.sh" \
    --repo "$REPO_ROOT"
  [ "$status" -eq 0 ]

  # 단언 (b): 정상 파일(phase-gate-mergeable.yml)에 값이 실제로 주입됨 (누락 아님)
  grep -q 'ALLOWED_HUB_REPOS: "github.com/mclayer/codeforge-internal-docs,github.com/mclayer/mctrader-hub"' \
    "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"

  # 단언 (c): mismatch 파일은 변경 없음 (single-quote 그대로)
  grep -q "ALLOWED_HUB_REPOS: 'github.com/mclayer/codeforge-internal-docs'" \
    "${WORKFLOWS_DIR}/aaa-mismatch.yml"
}
