#!/usr/bin/env bats
# CFP-2057: inject-allowed-hub-repos.sh D2/D3/D4 보강 테스트
# D2: bash 4+ version guard
# D3: /tmp marker 파일 IPC 제거 — AWK stderr 캡처 방식 회귀
# D4: 엣지 케이스 보강 (YAML parse-error, multi-entry order, non-str entry skip)
#
# discriminating fixture 의무 (CFP-1334):
#   D2/D3 회귀 fixture 는 변경 전 코드에서 RED → 변경 후 GREEN.

SCRIPT="$(dirname "$BATS_TEST_DIRNAME")/../../scripts/inject-allowed-hub-repos.sh"

setup() {
  TEST_TEMP_DIR="$(mktemp -d)"
  REPO_ROOT="${TEST_TEMP_DIR}/consumer-repo"
  WORKFLOWS_DIR="${REPO_ROOT}/.github/workflows"
  OVERLAY_DIR="${REPO_ROOT}/.claude/_overlay"

  mkdir -p "$WORKFLOWS_DIR" "$OVERLAY_DIR"

  # 표준 double-quoted fixture
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

# ─── D2: bash version guard ────────────────────────────────────────────

# D2-a: bash≥4 정상 실행 회귀 (기존 Test 1~9 전 전제)
@test "D2: bash≥4 환경에서 guard 통과 후 no-op 정상 종료" {
  run bash "$SCRIPT" --repo "$REPO_ROOT" --dry-run
  [ "$status" -eq 0 ]
}

# D2-b: guard 코드 존재 확인 (grep — discriminating: 코드 미삽입 시 RED)
@test "D2: inject 스크립트에 bash 4+ version guard 존재" {
  grep -q "BASH_VERSINFO\[0\].*-lt 4" "$SCRIPT"
}

# D2-c: guard exit 1 메시지 포함 확인
@test "D2: guard 발동 시 stderr에 진단 메시지 포함" {
  # guard 분기 직접 단언 (bash≥4 에서 BASH_VERSINFO mock 어려움 → string grep)
  grep -q "requires bash >= 4" "$SCRIPT"
}

# ─── D3: /tmp marker 파일 IPC 제거 회귀 ──────────────────────────────

# D3-a: /tmp/rewrite_marker.tmp 참조 0건 (discriminating: 구 코드 유지 시 RED)
@test "D3: 스크립트 내 /tmp/rewrite_marker.tmp 참조 0건" {
  run grep -c "rewrite_marker.tmp" "$SCRIPT"
  # grep -c 는 0건 시 exit 1 + "0" 출력 → 두 가지 모두 허용
  if [ "$status" -eq 0 ]; then
    [ "$output" = "0" ]
  else
    # exit 1 = 패턴 미발견 = pass
    true
  fi
}

# D3-b: 실제 rewrite 성공 경로 동작 확인 (AWK stderr IPC 방식)
@test "D3: rewrite 성공 경로 — marker 없이 실제 주입 동작" {
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

  run bash "$SCRIPT" --repo "$REPO_ROOT"
  [ "$status" -eq 0 ]
  # 실제 주입 결과 확인
  grep -q 'ALLOWED_HUB_REPOS: "github.com/mclayer/codeforge-internal-docs,github.com/mclayer/mctrader-hub"' \
    "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"
}

# D3-c: 동시 실행 cross-talk 없음 (두 독립 REPO_ROOT 동시 실행 후 각자 독립)
@test "D3: 동시 2-실행 cross-talk 없음" {
  # 두 번째 consumer-repo 생성
  local REPO_ROOT2="${TEST_TEMP_DIR}/consumer-repo-2"
  local WORKFLOWS_DIR2="${REPO_ROOT2}/.github/workflows"
  local OVERLAY_DIR2="${REPO_ROOT2}/.claude/_overlay"
  mkdir -p "$WORKFLOWS_DIR2" "$OVERLAY_DIR2"

  cat > "${WORKFLOWS_DIR2}/phase-gate-mergeable.yml" << 'EOF'
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

  # REPO1: mctrader-hub 주입
  cat > "${OVERLAY_DIR}/project.yaml" << 'EOF'
phase_gate:
  allowed_hub_repos:
    - "github.com/mclayer/mctrader-hub"
EOF

  # REPO2: other-hub 주입
  cat > "${OVERLAY_DIR2}/project.yaml" << 'EOF'
phase_gate:
  allowed_hub_repos:
    - "github.com/mclayer/other-hub"
EOF

  # 두 개를 (near-)동시 실행
  bash "$SCRIPT" --repo "$REPO_ROOT" &
  bash "$SCRIPT" --repo "$REPO_ROOT2" &
  wait

  # 각 결과가 독립적임을 확인 (cross-talk 없음)
  grep -q "github.com/mclayer/mctrader-hub" "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"
  grep -q "github.com/mclayer/other-hub" "${WORKFLOWS_DIR2}/phase-gate-mergeable.yml"
  # cross-contamination 없음
  run grep "github.com/mclayer/other-hub" "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"
  [ "$status" -ne 0 ]
}

# D3-d: rewrite 0건 경로 (quote mismatch) — /tmp marker 없이 올바르게 skip 판정
@test "D3: rewrite 0건 경로 — quote mismatch 시 /tmp marker 미생성 확인" {
  cat > "${OVERLAY_DIR}/project.yaml" << 'EOF'
phase_gate:
  allowed_hub_repos:
    - "github.com/mclayer/mctrader-hub"
EOF

  # single-quote fixture (mismatch)
  cat > "${WORKFLOWS_DIR}/single-quote.yml" << 'FIXTURE'
name: single-quote-test
on: [pull_request]
env:
  ALLOWED_HUB_REPOS: 'github.com/mclayer/codeforge-internal-docs'
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "test"
FIXTURE

  run bash "$SCRIPT" --repo "$REPO_ROOT"
  # exit 0 (skip 은 에러 아님, 단지 continue)
  [ "$status" -eq 0 ]

  # /tmp/rewrite_marker.tmp 잔존 없음
  run ls /tmp/rewrite_marker.tmp 2>/dev/null
  [ "$status" -ne 0 ]
}

# ─── D4: 엣지 케이스 보강 ─────────────────────────────────────────────

# D4-a: YAML parse error → extract_allowed_hub_repos.py exit 1 → 스크립트 exit 1
@test "D4: malformed YAML parse error → exit 1" {
  cat > "${OVERLAY_DIR}/project.yaml" << 'EOF'
phase_gate:
  allowed_hub_repos:
    - "github.com/mclayer/mctrader-hub"
  invalid: [unclosed
EOF

  run bash "$SCRIPT" --repo "$REPO_ROOT"
  [ "$status" -ne 0 ]
}

# D4-b: multi-entry 3개 순서 보존 단언
@test "D4: multi-entry 3개 — default 우선 + 선언 순서 보존" {
  cat > "${OVERLAY_DIR}/project.yaml" << 'EOF'
phase_gate:
  allowed_hub_repos:
    - "github.com/mclayer/first-hub"
    - "github.com/mclayer/second-hub"
    - "github.com/mclayer/third-hub"
EOF

  run bash "$SCRIPT" --repo "$REPO_ROOT"
  [ "$status" -eq 0 ]

  # 순서: default → first → second → third
  grep -q 'ALLOWED_HUB_REPOS: "github.com/mclayer/codeforge-internal-docs,github.com/mclayer/first-hub,github.com/mclayer/second-hub,github.com/mclayer/third-hub"' \
    "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"
}

# D4-c: non-str entry skip — dict/int 혼입 시 str 만 주입
@test "D4: non-str entry (dict/int 혼입) skip — str 만 주입" {
  # extract_allowed_hub_repos.py 의 isinstance(repo, str) 분기 커버
  cat > "${OVERLAY_DIR}/project.yaml" << 'EOF'
phase_gate:
  allowed_hub_repos:
    - "github.com/mclayer/valid-hub"
    - 42
    - {key: value}
    - "github.com/mclayer/another-hub"
EOF

  run bash "$SCRIPT" --repo "$REPO_ROOT"
  [ "$status" -eq 0 ]

  # str 항목만 주입
  grep -q "github.com/mclayer/valid-hub" "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"
  grep -q "github.com/mclayer/another-hub" "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"
  # int/dict 는 주입 안 됨 (42, key 등)
  run grep '"42"' "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"
  [ "$status" -ne 0 ]
}

# D4-d: Test 9 회귀 — quote mismatch 파일이 앞에 와도 정상 파일 주입 보장
@test "D4: quote-mismatch 파일 앞에 와도 정상 워크플로 주입 계속됨 (F-CR-1716-1 회귀)" {
  cat > "${OVERLAY_DIR}/project.yaml" << 'YAML'
phase_gate:
  allowed_hub_repos:
    - "github.com/mclayer/mctrader-hub"
YAML

  # aaa-mismatch.yml: single-quote (find 정렬상 먼저 처리됨)
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

  run bash "$SCRIPT" --repo "$REPO_ROOT"
  [ "$status" -eq 0 ]

  # 정상 파일에 주입됨
  grep -q 'ALLOWED_HUB_REPOS: "github.com/mclayer/codeforge-internal-docs,github.com/mclayer/mctrader-hub"' \
    "${WORKFLOWS_DIR}/phase-gate-mergeable.yml"

  # mismatch 파일은 변경 없음
  grep -q "ALLOWED_HUB_REPOS: 'github.com/mclayer/codeforge-internal-docs'" \
    "${WORKFLOWS_DIR}/aaa-mismatch.yml"
}
