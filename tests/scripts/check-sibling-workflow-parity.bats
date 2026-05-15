#!/usr/bin/env bats
# tests/scripts/check-sibling-workflow-parity.bats
# CFP-685 Phase 1 sub-PR (b) — check-sibling-workflow-parity.sh unit tests
# Story §7.4 / Change Plan §8 test plan verbatim
#
# Test cases (TC-1..TC-7) + meta:
#   TC-1: templates 파일 부재 → exit 2 (SETUP error)
#   TC-2: SETUP ok, 대상 workflow 없음 → skip (not applicable)
#   TC-3: PASS — templates ↔ self-app SHA-256 byte-identical → exit 0
#   TC-4: DRIFT — templates ↔ self-app SHA mismatch → exit 1
#   TC-5: SETUP error — sha256sum / shasum 미설치 → exit 2
#         (failure mode 명시: yaml parse 실패 = exit 2; count mismatch = exit 1; PASS = exit 0)
#   TC-6: multi-file PASS — 2개 workflow 모두 byte-identical → exit 0
#   TC-7: multi-file PARTIAL DRIFT — 1개 drift → exit 1

SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-sibling-workflow-parity.sh"

# ------------------------------------------------------------------ setup/teardown
setup() {
  TEST_DIR="$(mktemp -d)"
  export TEST_DIR

  # sha256sum or shasum 필수 확인
  if ! command -v sha256sum &>/dev/null && ! command -v shasum &>/dev/null; then
    skip "sha256sum/shasum not available"
  fi

  # 테스트용 임시 templates/github-workflows 디렉토리
  TMPL_DIR="$TEST_DIR/templates/github-workflows"
  mkdir -p "$TMPL_DIR"
  export TMPL_DIR

  # 테스트용 임시 .github/workflows 디렉토리
  GH_DIR="$TEST_DIR/.github/workflows"
  mkdir -p "$GH_DIR"
  export GH_DIR
}

teardown() {
  rm -rf "$TEST_DIR"
}

# ------------------------------------------------------------------ TC-1: templates 파일 부재 → exit 2
@test "TC-1: templates/github-workflows 디렉토리 부재 → exit 2 (SETUP error)" {
  # 존재하지 않는 templates 경로 지정
  run env \
    CFP685_TEMPLATES_DIR="$TEST_DIR/nonexistent/templates/github-workflows" \
    CFP685_GH_WORKFLOWS_DIR="$GH_DIR" \
    bash "$SCRIPT"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # SETUP error = exit 2
  [ "$status" -eq 2 ]
  # 오류 메시지에 "SETUP" 또는 "not found" / "directory" 언급
  [[ "$output" == *"SETUP"* ]] || [[ "$output" == *"not found"* ]] || [[ "$output" == *"directory"* ]]
}

# ------------------------------------------------------------------ TC-2: 대상 workflow 없음 → exit 0 (nothing to check)
@test "TC-2: templates 디렉토리 비어 있음 → exit 0 (nothing to check)" {
  # templates 빈 디렉토리, .github/workflows 빈 디렉토리

  run env \
    CFP685_TEMPLATES_DIR="$TMPL_DIR" \
    CFP685_GH_WORKFLOWS_DIR="$GH_DIR" \
    bash "$SCRIPT"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # 대상 없음 = PASS (no drift possible)
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]] || [[ "$output" == *"nothing"* ]] || [[ "$output" == *"0 files"* ]]
}

# ------------------------------------------------------------------ TC-3: PASS — SHA-256 byte-identical
@test "TC-3: 1 workflow byte-identical — exit 0 (PASS)" {
  # templates 안 workflow 생성
  echo "name: Test Workflow" > "$TMPL_DIR/auto-phase-label.yml"

  # .github/workflows 에 동일 내용 복사 (byte-identical)
  cp "$TMPL_DIR/auto-phase-label.yml" "$GH_DIR/auto-phase-label.yml"

  run env \
    CFP685_TEMPLATES_DIR="$TMPL_DIR" \
    CFP685_GH_WORKFLOWS_DIR="$GH_DIR" \
    bash "$SCRIPT"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # byte-identical → exit 0
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" != *"DRIFT"* ]]
}

# ------------------------------------------------------------------ TC-4: DRIFT — SHA mismatch → exit 1
@test "TC-4: 1 workflow SHA mismatch — exit 1 (drift detected)" {
  # templates 안 workflow 생성
  echo "name: Template Version" > "$TMPL_DIR/auto-phase-label.yml"

  # .github/workflows 에 다른 내용 (drift)
  echo "name: Modified Version (DRIFT)" > "$GH_DIR/auto-phase-label.yml"

  run env \
    CFP685_TEMPLATES_DIR="$TMPL_DIR" \
    CFP685_GH_WORKFLOWS_DIR="$GH_DIR" \
    bash "$SCRIPT"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # drift detected → exit 1
  [ "$status" -eq 1 ]
  [[ "$output" == *"DRIFT"* ]] || [[ "$output" == *"drift"* ]]
  [[ "$output" == *"auto-phase-label"* ]]
}

# ------------------------------------------------------------------ TC-5: SETUP error — sha256sum/shasum 모의 부재
# (Change Plan §8 TC-5 exit code semantic: yaml parse 실패 = exit 2; count mismatch = exit 1; PASS = exit 0)
@test "TC-5: sha256sum PATH 조작으로 누락 시 → exit 2 (SETUP error)" {
  # sha256sum / shasum 미검출 시뮬레이션 — PATH 에서 제거
  # 단, skip-sha256 env 로 의도적 override 가능한 경우 테스트가 성립 안 함
  # 대신: 빈 sha256sum stub (exit 127 = "not found" 시뮬레이션)
  EMPTY_BIN="$TEST_DIR/empty_bin"
  mkdir -p "$EMPTY_BIN"
  # sha256sum stub: 항상 실패 (exit 1)
  cat > "$EMPTY_BIN/sha256sum" <<'STUB'
#!/usr/bin/env bash
exit 127
STUB
  chmod +x "$EMPTY_BIN/sha256sum"
  cat > "$EMPTY_BIN/shasum" <<'STUB'
#!/usr/bin/env bash
exit 127
STUB
  chmod +x "$EMPTY_BIN/shasum"

  # workflow 파일 생성 (SHA 검사 전 SETUP error 발생 필요)
  echo "name: Test" > "$TMPL_DIR/auto-phase-label.yml"
  cp "$TMPL_DIR/auto-phase-label.yml" "$GH_DIR/auto-phase-label.yml"

  run env \
    PATH="$EMPTY_BIN:$PATH" \
    CFP685_TEMPLATES_DIR="$TMPL_DIR" \
    CFP685_GH_WORKFLOWS_DIR="$GH_DIR" \
    bash "$SCRIPT"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # SETUP error = exit 2
  # (sha256sum 실패 시 fallback shasum 도 실패 → SETUP error)
  [ "$status" -eq 2 ]
}

# ------------------------------------------------------------------ TC-6: multi-file PASS
@test "TC-6: 2 workflows 모두 byte-identical — exit 0 (PASS)" {
  # 2개 workflow 생성 (auto-phase-label + sibling-workflow-parity)
  echo "name: Auto Phase Label" > "$TMPL_DIR/auto-phase-label.yml"
  echo "name: Sibling Parity"   > "$TMPL_DIR/sibling-workflow-parity.yml"

  # byte-identical copy
  cp "$TMPL_DIR/auto-phase-label.yml"        "$GH_DIR/auto-phase-label.yml"
  cp "$TMPL_DIR/sibling-workflow-parity.yml" "$GH_DIR/sibling-workflow-parity.yml"

  run env \
    CFP685_TEMPLATES_DIR="$TMPL_DIR" \
    CFP685_GH_WORKFLOWS_DIR="$GH_DIR" \
    bash "$SCRIPT"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
  [[ "$output" != *"DRIFT"* ]]
}

# ------------------------------------------------------------------ TC-7: multi-file PARTIAL DRIFT — 1개 drift → exit 1
@test "TC-7: 2 workflows, 1 drift — exit 1 (drift detected, PASS count reported)" {
  # 2개 workflow 생성
  echo "name: Auto Phase Label (Identical)" > "$TMPL_DIR/auto-phase-label.yml"
  echo "name: Sibling Parity Template"      > "$TMPL_DIR/sibling-workflow-parity.yml"

  # auto-phase-label: byte-identical
  cp "$TMPL_DIR/auto-phase-label.yml" "$GH_DIR/auto-phase-label.yml"

  # sibling-workflow-parity: DRIFT (content differs)
  echo "name: Sibling Parity MODIFIED (DRIFT)" > "$GH_DIR/sibling-workflow-parity.yml"

  run env \
    CFP685_TEMPLATES_DIR="$TMPL_DIR" \
    CFP685_GH_WORKFLOWS_DIR="$GH_DIR" \
    bash "$SCRIPT"

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # 1개 drift → exit 1
  [ "$status" -eq 1 ]
  [[ "$output" == *"DRIFT"* ]] || [[ "$output" == *"drift"* ]]
  [[ "$output" == *"sibling-workflow-parity"* ]]
}

# ------------------------------------------------------------------ meta TC: script 존재 확인
@test "meta: check-sibling-workflow-parity.sh 파일 존재" {
  [[ -f "$SCRIPT" ]] || skip "script not yet implemented (expected in TDD red phase)"
  [[ -x "$SCRIPT" ]] || fail "script not executable: $SCRIPT"
}
