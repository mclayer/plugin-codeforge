#!/usr/bin/env bats
# tests/scripts/test-check-increment-justification.bats
# CFP-2061-S1 / ADR-060 §결정 30
#
# 정당화 순증 게이트 unit tests (TDD RED→GREEN)
# Change Plan §8 Test Contract: TC-1~10
#
# Test cases:
#   TC-1 (happy):     신규 검사 + marker(why + blocks-or-replaces) 존재 -> exit 0 PASS
#   TC-2 (RED core):  신규 검사 + marker 부재 -> exit 1 WARNING  [discriminating core]
#   TC-3 (요소 누락): marker 존재하나 blocks-or-replaces 누락 -> exit 1 WARNING
#   TC-4 (분산 우회): registry append + 신규 workflow 동시, marker 부재 -> exit 1 WARNING
#   TC-5 (ADR):       신규 adr_number ADR, marker 부재 -> exit 1 WARNING
#   TC-6 (Amendment): 기존 ADR Amendment append (신규 adr_number 아님) -> exit 0 PASS
#   TC-7 (chore):     doc-only PR (trigger-path 0건) -> exit 0 PASS
#   TC-8 (exempt):    보안/whitelist tag 검사 추가, marker 부재 -> exit 0 PASS
#   TC-9 (self-meta): self-exempt label 부착 -> exit 0 PASS
#   TC-10 (base 부재): base-ref 부재 (신규 repo) -> exit 0 PASS
#
# Mock env vars:
#   CIJ_MOCK_DIFF_FILES   — newline-delimited "STATUS\tPATH" (e.g. "A\tscripts/check-foo.sh")
#   CIJ_MOCK_PR_BODY      — PR body text
#   CIJ_MOCK_PR_LABELS    — comma-separated label names
#   CIJ_MOCK_BASE_ABSENT  — "1" 이면 base-ref 부재 시뮬레이션
#   CIJ_MOCK_EXEMPT_PATHS — newline-delimited exempt paths (검사 파일 경로)

SCRIPT="$(dirname "$BATS_TEST_FILENAME")/../../scripts/check-increment-justification.sh"

# ------------------------------------------------------------------ setup/teardown
setup() {
  if ! command -v python3 &>/dev/null; then
    skip "python3 not available"
  fi
}

teardown() {
  true
}

# ------------------------------------------------------------------ TC-1: happy path (marker 존재 -> PASS)
@test "TC-1: 신규 검사 + marker(why + blocks-or-replaces) 존재 -> exit 0 PASS" {
  # fixture: with_marker_pr_body.txt (Change Plan §8 RED proof discriminating fixture)
  run env \
    CIJ_MOCK_DIFF_FILES="A	scripts/check-foo.sh" \
    CIJ_MOCK_PR_BODY="$(cat tests/fixtures/cfp-2061-s1/with_marker_pr_body.txt)" \
    CIJ_MOCK_PR_LABELS="" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --pr-number 9001

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-2: RED core (marker 부재 -> WARNING)
@test "TC-2: 신규 검사 + marker 부재 -> exit 1 WARNING [discriminating core]" {
  # fixture: without_marker_pr_body.txt (Change Plan §8 RED proof discriminating fixture)
  run env \
    CIJ_MOCK_DIFF_FILES="A	scripts/check-foo.sh" \
    CIJ_MOCK_PR_BODY="$(cat tests/fixtures/cfp-2061-s1/without_marker_pr_body.txt)" \
    CIJ_MOCK_PR_LABELS="" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --pr-number 9002

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 1 ]
  [[ "$output" == *"WARNING"* ]] || [[ "$output" == *"marker"* ]]
}

# ------------------------------------------------------------------ TC-3: 요소 누락 (blocks-or-replaces 없음 -> WARNING)
@test "TC-3: marker 존재하나 blocks-or-replaces 누락 -> exit 1 WARNING" {
  # fixture: only_why_pr_body.txt (why= 만 존재, blocks-or-replaces= 누락)
  run env \
    CIJ_MOCK_DIFF_FILES="A	scripts/check-bar.sh" \
    CIJ_MOCK_PR_BODY="$(cat tests/fixtures/cfp-2061-s1/only_why_pr_body.txt)" \
    CIJ_MOCK_PR_LABELS="" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --pr-number 9003

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 1 ]
  [[ "$output" == *"WARNING"* ]] || [[ "$output" == *"marker"* ]]
}

# ------------------------------------------------------------------ TC-4: 분산 우회 (registry + workflow, marker 부재 -> WARNING)
@test "TC-4: registry append + 신규 workflow 동시, marker 부재 -> exit 1 WARNING" {
  # 실 patch fixture 기반 (F-CR-2 fix — CIJ_MOCK_REGISTRY_PATCH 로 실 hunk 주입, mock flag 제거)
  DIFF="A	.github/workflows/foo.yml
M	docs/evidence-checks-registry.yaml"
  run env \
    CIJ_MOCK_DIFF_FILES="$DIFF" \
    CIJ_MOCK_REGISTRY_PATCH="$(cat tests/fixtures/cfp-2061-s1/registry_append_patch.txt)" \
    CIJ_MOCK_PR_BODY="" \
    CIJ_MOCK_PR_LABELS="" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --pr-number 9004

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 1 ]
  [[ "$output" == *"WARNING"* ]] || [[ "$output" == *"marker"* ]]
  # registry-append trigger 가 실 patch 파싱으로 감지되는지 확인 (F-CR-2 discriminating assertion)
  [[ "$output" == *"registry-append"* ]]
}

# ------------------------------------------------------------------ TC-5: 신규 ADR, marker 부재 -> WARNING
@test "TC-5: 신규 adr_number ADR, marker 부재 -> exit 1 WARNING" {
  run env \
    CIJ_MOCK_DIFF_FILES="A	archive/adr/ADR-999-new-decision.md" \
    CIJ_MOCK_PR_BODY="" \
    CIJ_MOCK_PR_LABELS="" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --pr-number 9005

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 1 ]
  [[ "$output" == *"WARNING"* ]] || [[ "$output" == *"marker"* ]]
}

# ------------------------------------------------------------------ TC-6: Amendment 제외 (기존 ADR 수정 -> PASS)
@test "TC-6: 기존 ADR Amendment append (신규 adr_number 아님) -> exit 0 PASS" {
  # 기존 ADR 파일 수정 (A=added 아닌 M=modified)
  run env \
    CIJ_MOCK_DIFF_FILES="M	archive/adr/ADR-060-evidence-enforceable-promotion-framework.md" \
    CIJ_MOCK_PR_BODY="" \
    CIJ_MOCK_PR_LABELS="" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --pr-number 9006

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # Amendment (modified existing ADR) = trigger-path 아님 -> PASS
  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-7: chore fast-path (doc-only -> PASS)
@test "TC-7: doc-only PR (trigger-path 0건) -> exit 0 PASS (chore fast-path)" {
  run env \
    CIJ_MOCK_DIFF_FILES="M	docs/foo.md" \
    CIJ_MOCK_PR_BODY="" \
    CIJ_MOCK_PR_LABELS="" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --pr-number 9007

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-8: exempt (보안/whitelist tag -> PASS)
@test "TC-8: exempt path 검사 추가, marker 부재 -> exit 0 PASS (AC-4 exempt)" {
  run env \
    CIJ_MOCK_DIFF_FILES="A	scripts/check-security-foo.sh" \
    CIJ_MOCK_PR_BODY="" \
    CIJ_MOCK_PR_LABELS="" \
    CIJ_MOCK_EXEMPT_PATHS="scripts/check-security-foo.sh" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --pr-number 9008

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-9: self-meta (hotfix-bypass label -> PASS)
@test "TC-9: hotfix-bypass:increment-justification label -> exit 0 PASS (EC-5 self-meta)" {
  run env \
    CIJ_MOCK_DIFF_FILES="A	scripts/check-baz.sh" \
    CIJ_MOCK_PR_BODY="" \
    CIJ_MOCK_PR_LABELS="hotfix-bypass:increment-justification" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --pr-number 9009

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-10: base 부재 (신규 repo -> PASS)
@test "TC-10: base-ref 부재 (신규 repo) -> exit 0 PASS" {
  run env \
    CIJ_MOCK_DIFF_FILES="A	scripts/check-new.sh" \
    CIJ_MOCK_PR_BODY="" \
    CIJ_MOCK_PR_LABELS="" \
    CIJ_MOCK_BASE_ABSENT="1" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --pr-number 9010

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  [ "$status" -eq 0 ]
  [[ "$output" == *"PASS"* ]]
}

# ------------------------------------------------------------------ TC-11: production full-word status (F-CR-NEW-1 discriminating)
@test "TC-11: GitHub REST full-word status('added'/'modified') -> trigger 정상 감지 -> exit 1 WARNING [F-CR-NEW-1 discriminating]" {
  # 목적: production 경로 (GitHub REST API) 가 반환하는 풀워드 status 가
  #       normalize 를 거쳐 trigger-path 로 정상 감지되는지 검증.
  # 본 TC 가 없으면 단문자 mock 만으로는 production no-op 결함 재포착 불가 (위양성 차단).
  #
  # BEFORE FIX (normalize 없음):
  #   CIJ_MOCK_DIFF_FILES="added\tscripts/check-full-word.py" → triggers=0 → exit 0 (no-op, WRONG)
  # AFTER FIX (normalize 적용):
  #   same input → triggers=1 → exit 1 WARNING (CORRECT)
  run env \
    CIJ_MOCK_DIFF_FILES="added	scripts/check-full-word.py" \
    CIJ_MOCK_PR_BODY="" \
    CIJ_MOCK_PR_LABELS="" \
    bash "$SCRIPT" --repo mclayer/plugin-codeforge --pr-number 9011

  echo "# status: $status" >&3
  echo "# output: $output" >&3

  # normalize 후 'added' -> 'A' -> trigger 감지 -> WARNING
  [ "$status" -eq 1 ]
  [[ "$output" == *"WARNING"* ]] || [[ "$output" == *"marker"* ]]
  [[ "$output" == *"new-check-script"* ]]
}
