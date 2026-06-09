#!/usr/bin/env bats
# tests/scripts/cfp-2061-s6/collect-changed-files-helper.bats
# CFP-2061-S6 파트3 — collect_changed_files.sh helper 추출 TDD
# RED→GREEN stash proof pattern (CFP-1334 §8.4 / Change Plan §8 T3-1~5)
#
# 설계 참고: 명시 인수 모드는 이미 필터된 파일 목록을 받는 것으로 설계됨
# (Change Plan §3.2 verbatim: raw_files=("$@") — 별도 grep 없음).
# FILTER_REGEX 는 git diff 모드(인수 0개)에서만 적용.
# 명시 인수 시 POST_FILTER_FN 만 적용 가능.
#
# TC 목록:
#   T3-1a: git diff 모드 — FILTER_REGEX suffix-anchored 적용 확인 (git stub)
#   T3-1b: git diff 모드 — FILTER_REGEX path-anchored 적용 확인 (git stub)
#   T3-2:  POST_FILTER_FN hook — is_skip_listed 류 함수로 특정 파일 제외 + stderr 메시지 보존
#   T3-3a: path-anchored regex 회귀 — ^docs/adr/ADR-[0-9].*\.md$ (slot-reservation 패턴)
#   T3-3b: path-anchored regex 회귀 — ^docs/stories/.*\.md$ (drift-detection 패턴)
#   T3-4a: suffix-anchored regex — check-spawn-prompt-head-pin 패턴
#   T3-4b: suffix-anchored regex — check-amendment-number-stale 패턴
#   T3-4c: suffix-anchored regex — check-wrapper-managed-block 패턴
#   T3-5a: empty-guard — 매칭 파일 0건 시 출력 없음 (exit 0)
#   T3-5b: git 미설치 분기 exit 2 (GITHUB_BASE_REF unset, PATH 에 git 제거)
#   T3-6:  POST_FILTER_FN 미정의 시 no-op (전부 통과)
#   T3-7:  빈 파일명 입력 무시 (empty-guard)
#
# 3-layer defense (always-pass pattern_count 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — positive + negative 2-assertion per TC
#   Layer 3 — 임시 fixture 사용 (실제 repo git diff 의존 금지)
#
# Framework: bats (codeforge convention)
# SSOT: CFP-2061-S6 Change Plan §3.2 + §8 T3-1~5

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"
HELPER_SCRIPT="${WORKTREE_ROOT}/scripts/lib/collect_changed_files.sh"

# ─────────────────────────────────── sandbox setup ───────────────────────────

setup() {
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
  export SCRIPT_NAME="[test-collect-changed-files]"
  unset GITHUB_BASE_REF
  unset POST_FILTER_FN
}

teardown() {
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-2061-s6-unused}"
  unset POST_FILTER_FN
  unset SCRIPT_NAME
}

# ─────────────────────────────────── T3-1a: git diff 모드 + suffix-anchored ──

@test "T3-1a: git diff 모드 suffix-anchored regex — .md/.yaml 매칭, .sh 제외" {
  local filter='\.(md|yaml)$'
  local stub_dir="${TEST_TMP}/stub_bin"
  mkdir -p "${stub_dir}"

  cat > "${stub_dir}/git" << 'STUB'
#!/usr/bin/env bash
if [[ "$*" == *"--name-only"* ]]; then
  echo "archive/adr/ADR-001-test.md"
  echo "docs/test.yaml"
  echo "scripts/check-foo.sh"
  echo "README.txt"
fi
exit 0
STUB
  chmod +x "${stub_dir}/git"

  result="$(GITHUB_BASE_REF=main PATH="${stub_dir}:${PATH}" bash -c "
    source '${HELPER_SCRIPT}'
    collect_changed_files '\.(md|yaml)\$'
  ")"

  echo "$result" | grep -q 'archive/adr/ADR-001-test.md'
  echo "$result" | grep -q 'docs/test.yaml'
  ! echo "$result" | grep -q 'scripts/check-foo.sh'
  ! echo "$result" | grep -q 'README.txt'
}

# ─────────────────────────────────── T3-1b: git diff 모드 + path-anchored ────

@test "T3-1b: git diff 모드 path-anchored regex — ^docs/adr/ADR 매칭, 비대상 제외" {
  local stub_dir="${TEST_TMP}/stub_bin"
  mkdir -p "${stub_dir}"

  cat > "${stub_dir}/git" << 'STUB'
#!/usr/bin/env bash
if [[ "$*" == *"--name-only"* ]]; then
  echo "docs/adr/ADR-001-test.md"
  echo "docs/adr/ADR-099-foo.md"
  echo "archive/adr/ADR-001.md"
  echo "docs/stories/CFP-1234.md"
fi
exit 0
STUB
  chmod +x "${stub_dir}/git"

  result="$(GITHUB_BASE_REF=main PATH="${stub_dir}:${PATH}" bash -c "
    source '${HELPER_SCRIPT}'
    collect_changed_files '^docs/adr/ADR-[0-9].*\.md\$'
  ")"

  echo "$result" | grep -q '^docs/adr/ADR-001-test.md$'
  echo "$result" | grep -q '^docs/adr/ADR-099-foo.md$'
  ! echo "$result" | grep -q 'archive/adr/ADR-001.md'
  ! echo "$result" | grep -q 'docs/stories/CFP-1234.md'
}

# ─────────────────────────────────── T3-2: POST_FILTER_FN hook ───────────────

@test "T3-2: POST_FILTER_FN — skip 파일 제외 + stderr 메시지 출력 보존" {
  # 명시 인수 모드 사용 (git stub 불필요)
  local stderr_file="${TEST_TMP}/stderr_t3_2.txt"

  result_out="$(bash -c "
    source '${HELPER_SCRIPT}'
    my_skip_fn() {
      local f=\"\$1\"
      if [[ \"\$f\" == 'skip_target.md' ]]; then
        echo \"SKIP (self-referential): \$f\" >&2
        return 0  # 제외 신호
      fi
      return 1  # 통과
    }
    POST_FILTER_FN=my_skip_fn collect_changed_files '\.(md|yaml)\$' 'keep_this.md' 'skip_target.md' 'also_keep.yaml'
  " 2>"${stderr_file}")"

  echo "$result_out" | grep -q 'keep_this.md'
  echo "$result_out" | grep -q 'also_keep.yaml'
  ! echo "$result_out" | grep -q 'skip_target.md'
  grep -q 'SKIP (self-referential): skip_target.md' "${stderr_file}"
}

# ─────────────────────────────────── T3-3a: path-anchored ^docs/adr/ 회귀 ────

@test "T3-3a: slot-reservation 패턴 ^docs/adr/ADR-[0-9].*\\.md$ 회귀 (git diff 모드)" {
  local stub_dir="${TEST_TMP}/stub_bin"
  mkdir -p "${stub_dir}"

  cat > "${stub_dir}/git" << 'STUB'
#!/usr/bin/env bash
if [[ "$*" == *"--name-only"* ]]; then
  echo "docs/adr/ADR-001-some-decision.md"
  echo "docs/adr/ADR-082-something.md"
  echo "docs/stories/CFP-2061-S6.md"
  echo "scripts/check-something.sh"
fi
exit 0
STUB
  chmod +x "${stub_dir}/git"

  result="$(GITHUB_BASE_REF=main PATH="${stub_dir}:${PATH}" bash -c "
    source '${HELPER_SCRIPT}'
    collect_changed_files '^docs/adr/ADR-[0-9].*\.md\$'
  ")"

  echo "$result" | grep -q 'docs/adr/ADR-001-some-decision.md'
  echo "$result" | grep -q 'docs/adr/ADR-082-something.md'
  ! echo "$result" | grep -q 'docs/stories/CFP-2061-S6.md'
  ! echo "$result" | grep -q 'scripts/check-something.sh'
}

# ─────────────────────────────────── T3-3b: path-anchored ^docs/stories/ 회귀 ─

@test "T3-3b: drift-detection 패턴 ^docs/stories/.*\\.md$ 회귀 (git diff 모드)" {
  local stub_dir="${TEST_TMP}/stub_bin"
  mkdir -p "${stub_dir}"

  cat > "${stub_dir}/git" << 'STUB'
#!/usr/bin/env bash
if [[ "$*" == *"--name-only"* ]]; then
  echo "docs/stories/CFP-2061-S6.md"
  echo "docs/stories/CFP-1000.md"
  echo "docs/adr/ADR-001.md"
  echo "archive/adr/ADR-002.md"
fi
exit 0
STUB
  chmod +x "${stub_dir}/git"

  result="$(GITHUB_BASE_REF=main PATH="${stub_dir}:${PATH}" bash -c "
    source '${HELPER_SCRIPT}'
    collect_changed_files '^docs/stories/.*\.md\$'
  ")"

  echo "$result" | grep -q 'docs/stories/CFP-2061-S6.md'
  echo "$result" | grep -q 'docs/stories/CFP-1000.md'
  ! echo "$result" | grep -q 'docs/adr/ADR-001.md'
  ! echo "$result" | grep -q 'archive/adr/ADR-002.md'
}

# ─────────────────────────────────── T3-4: suffix-anchored 3 caller 회귀 ─────

@test "T3-4a: check-spawn-prompt-head-pin 패턴 \\.(md|yaml|yml|txt|log)\$ 회귀" {
  local stub_dir="${TEST_TMP}/stub_bin"
  mkdir -p "${stub_dir}"

  cat > "${stub_dir}/git" << 'STUB'
#!/usr/bin/env bash
if [[ "$*" == *"--name-only"* ]]; then
  echo "docs/test.md"
  echo "config.yaml"
  echo "workflow.yml"
  echo "notes.txt"
  echo "debug.log"
  echo "script.sh"
  echo "code.py"
fi
exit 0
STUB
  chmod +x "${stub_dir}/git"

  result="$(GITHUB_BASE_REF=main PATH="${stub_dir}:${PATH}" bash -c "
    source '${HELPER_SCRIPT}'
    collect_changed_files '\.(md|yaml|yml|txt|log)\$'
  ")"

  echo "$result" | grep -q 'docs/test.md'
  echo "$result" | grep -q 'config.yaml'
  echo "$result" | grep -q 'workflow.yml'
  echo "$result" | grep -q 'notes.txt'
  echo "$result" | grep -q 'debug.log'
  ! echo "$result" | grep -q 'script.sh'
  ! echo "$result" | grep -q 'code.py'
}

@test "T3-4b: check-amendment-number-stale 패턴 \\.(md|yaml|yml)\$ 회귀" {
  local stub_dir="${TEST_TMP}/stub_bin"
  mkdir -p "${stub_dir}"

  cat > "${stub_dir}/git" << 'STUB'
#!/usr/bin/env bash
if [[ "$*" == *"--name-only"* ]]; then
  echo "docs/test.md"
  echo "config.yaml"
  echo "workflow.yml"
  echo "notes.txt"
  echo "script.sh"
fi
exit 0
STUB
  chmod +x "${stub_dir}/git"

  result="$(GITHUB_BASE_REF=main PATH="${stub_dir}:${PATH}" bash -c "
    source '${HELPER_SCRIPT}'
    collect_changed_files '\.(md|yaml|yml)\$'
  ")"

  echo "$result" | grep -q 'docs/test.md'
  echo "$result" | grep -q 'config.yaml'
  echo "$result" | grep -q 'workflow.yml'
  ! echo "$result" | grep -q 'notes.txt'
  ! echo "$result" | grep -q 'script.sh'
}

@test "T3-4c: check-wrapper-managed-block 패턴 \\.(yml|yaml|sh|md)\$ 회귀" {
  local stub_dir="${TEST_TMP}/stub_bin"
  mkdir -p "${stub_dir}"

  cat > "${stub_dir}/git" << 'STUB'
#!/usr/bin/env bash
if [[ "$*" == *"--name-only"* ]]; then
  echo "workflow.yml"
  echo "config.yaml"
  echo "script.sh"
  echo "README.md"
  echo "notes.txt"
  echo "code.py"
fi
exit 0
STUB
  chmod +x "${stub_dir}/git"

  result="$(GITHUB_BASE_REF=main PATH="${stub_dir}:${PATH}" bash -c "
    source '${HELPER_SCRIPT}'
    collect_changed_files '\.(yml|yaml|sh|md)\$'
  ")"

  echo "$result" | grep -q 'workflow.yml'
  echo "$result" | grep -q 'config.yaml'
  echo "$result" | grep -q 'script.sh'
  echo "$result" | grep -q 'README.md'
  ! echo "$result" | grep -q 'notes.txt'
  ! echo "$result" | grep -q 'code.py'
}

# ─────────────────────────────────── T3-5a: empty-guard ──────────────────────

@test "T3-5a: 매칭 파일 0건 — 출력 없음 (git diff 모드, stub 빈 목록)" {
  local stub_dir="${TEST_TMP}/stub_bin"
  mkdir -p "${stub_dir}"

  cat > "${stub_dir}/git" << 'STUB'
#!/usr/bin/env bash
if [[ "$*" == *"--name-only"* ]]; then
  echo "script.sh"
  echo "code.py"
fi
exit 0
STUB
  chmod +x "${stub_dir}/git"

  result="$(GITHUB_BASE_REF=main PATH="${stub_dir}:${PATH}" bash -c "
    source '${HELPER_SCRIPT}'
    collect_changed_files '\.(md|yaml)\$'
  ")"

  [[ -z "$result" ]]
}

# ─────────────────────────────────── T3-5b: git 미설치 exit 2 ────────────────

@test "T3-5b: git 미설치 + 인수 없음 — exit 2 (환경 오류)" {
  local empty_dir="${TEST_TMP}/empty_bin"
  mkdir -p "${empty_dir}"
  # PATH 에서 git 완전 제거 (empty_dir 만 남김)

  run bash -c "
    source '${HELPER_SCRIPT}'
    PATH='${empty_dir}' collect_changed_files '\.(md|yaml)\$'
  "
  [[ "$status" -eq 2 ]]
}

# ─────────────────────────────────── T3-6: POST_FILTER_FN 미정의 no-op ───────

@test "T3-6: POST_FILTER_FN 미정의 시 명시 인수 전부 통과 (no-op)" {
  # 명시 인수 모드: POST_FILTER_FN 없으면 모두 출력
  result="$(bash -c "
    source '${HELPER_SCRIPT}'
    unset POST_FILTER_FN
    collect_changed_files '\.(md|yaml)\$' 'file1.md' 'file2.yaml' 'file3.sh'
  ")"

  # 명시 인수는 grep 없이 그대로 통과 (설계 §3.2)
  echo "$result" | grep -q 'file1.md'
  echo "$result" | grep -q 'file2.yaml'
  echo "$result" | grep -q 'file3.sh'
}

# ─────────────────────────────────── T3-7: 빈 파일명 입력 무시 ──────────────

@test "T3-7: 빈 문자열 인수 무시 (empty-guard)" {
  result="$(bash -c "
    source '${HELPER_SCRIPT}'
    collect_changed_files '\.(md|yaml)\$' '' 'valid.md' '' 'other.yaml'
  ")"

  echo "$result" | grep -q 'valid.md'
  echo "$result" | grep -q 'other.yaml'
  # 빈 줄 없음
  ! echo "$result" | grep -q '^[[:space:]]*$'
}
