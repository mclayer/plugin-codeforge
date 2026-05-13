#!/usr/bin/env bats
# tests/scripts/test_check_workflow_yaml_parse.bats
# CFP-583 / ADR-060 Amendment 9 §결정 22 — workflow yaml parse check unit tests
# Change Plan §8.1 — 6 TC

setup() {
  # 임시 테스트 디렉토리 생성
  TEST_DIR="$(mktemp -d)"
  export GITHUB_WORKSPACE="$TEST_DIR"
  mkdir -p "$TEST_DIR/.github/workflows"
  mkdir -p "$TEST_DIR/templates/github-workflows"

  # 정상 workflow fixture
  VALID_WORKFLOW="$TEST_DIR/.github/workflows/valid.yml"
  cat > "$VALID_WORKFLOW" <<'YAML'
name: valid test workflow
on:
  pull_request:
    types: [opened, synchronize]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run test
        run: echo "hello"
YAML

  # broken workflow fixture (BODY heredoc anti-pattern — §2.1 evidence)
  BROKEN_WORKFLOW="$TEST_DIR/.github/workflows/broken.yml"
  cat > "$BROKEN_WORKFLOW" <<'YAML'
name: broken test workflow
on:
  pull_request:
    types: [opened]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Post comment
        run: |
          HEADER="## test header"
          FOOTER="test footer"
          LINT_OUT="lint output"
          BODY="${HEADER}

```
${LINT_OUT}
```

${FOOTER}"
          echo "$BODY"
YAML
}

teardown() {
  rm -rf "$TEST_DIR"
}

# TC-1: 정상 workflow yml fixture → exit 0 + stdout PASS message
@test "TC-1: valid workflow yml — exit 0 + PASS message" {
  # broken.yml은 제거하고 valid만 남기기
  rm -f "$TEST_DIR/.github/workflows/broken.yml"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-workflow-yaml-parse.sh"
  [ "$status" -eq 0 ]
  [[ "$output" == *"workflow-yaml-parse PASS"* ]]
}

# TC-2: broken yaml fixture (multi-line BODY heredoc anti-pattern) → exit 1 + stderr error annotation
@test "TC-2: broken yaml (BODY heredoc anti-pattern) — exit 1 + error annotation" {
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-workflow-yaml-parse.sh"
  [ "$status" -eq 1 ]
  [[ "$output" == *"::error::workflow yaml parse FAIL"* ]]
}

# TC-3: actionlint warning fixture — exit 1 + actionlint error annotation (actionlint available only)
@test "TC-3: actionlint warning fixture — skip if actionlint not installed" {
  if ! command -v actionlint >/dev/null 2>&1; then
    skip "actionlint not installed — IT-1 self-loop verify covers this"
  fi

  # actionlint deprecated action fixture
  rm -f "$TEST_DIR/.github/workflows/broken.yml"
  ACTIONLINT_FIXTURE="$TEST_DIR/.github/workflows/actionlint_warn.yml"
  cat > "$ACTIONLINT_FIXTURE" <<'YAML'
name: actionlint deprecated action test
on:
  pull_request:
    types: [opened]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0
YAML

  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-workflow-yaml-parse.sh"
  [ "$status" -eq 1 ]
  [[ "$output" == *"::error::actionlint FAIL"* ]]
}

# TC-4: PyYAML 미설치 → exit 2 + meta-error annotation
@test "TC-4: PyYAML missing — exit 2 + meta-error" {
  # PYTHON을 존재하지 않는 binary로 override
  PYTHON="/nonexistent/python_binary" run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-workflow-yaml-parse.sh"
  [ "$status" -eq 2 ]
  [[ "$output" == *"meta-error"* ]]
}

# TC-5: .github/workflows/ 디렉토리 없음 → exit 0 (graceful skip, glob match 0)
@test "TC-5: no workflow directory — exit 0 graceful skip" {
  rm -rf "$TEST_DIR/.github" "$TEST_DIR/templates"
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-workflow-yaml-parse.sh"
  [ "$status" -eq 0 ]
  [[ "$output" == *"workflow-yaml-parse PASS"* ]]
}

# TC-6: *.yaml 확장자 파일 — glob *.yml only, skip
@test "TC-6: *.yaml extension — exempt from glob (*.yml only)" {
  rm -f "$TEST_DIR/.github/workflows/broken.yml"
  # .yaml 확장자로 broken fixture 생성 — 감지 안 되어야 함
  cat > "$TEST_DIR/.github/workflows/broken.yaml" <<'YAML'
name: broken yaml extension test
on:
  pull_request:
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: broken
        run: |
          BODY="${HEADER}

```
${LINT_OUT}
```"
          echo "$BODY"
YAML
  run bash "$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-workflow-yaml-parse.sh"
  # *.yaml는 glob 미포함이라 PASS
  [ "$status" -eq 0 ]
  [[ "$output" == *"workflow-yaml-parse PASS"* ]]
}

# IT-1: workflow-yaml-parse.yml self-fire (Phase 2 PR self-loop verify — CI only)
# Note: IT-1 은 GitHub Actions 환경에서만 실행 가능 — local bats 에서는 skip
@test "IT-1: self-loop verify — CI environment only" {
  skip "IT-1 self-loop verify = Phase 2 PR gh pr checks verify (GitHub Actions 환경 only)"
}

# IT-2: hotfix-bypass:workflow-yaml-parse label conditional skip (CI only)
@test "IT-2: bypass label conditional skip — CI environment only" {
  skip "IT-2 bypass label verify = GitHub API interaction (CI environment only)"
}

# IT-3: PR statusCheckRollup attach (CI only)
@test "IT-3: statusCheckRollup attach — CI environment only" {
  skip "IT-3 statusCheckRollup = gh pr checks verify (GitHub Actions 환경 only)"
}
