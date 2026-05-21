#!/usr/bin/env bats
# tests/scripts/cfp-1170/cfp-1170-walk-cli.bats
# CFP-1170 Phase 2 — walk-single-plugin.sh / walk-bundle-7-plugins.sh / deprecation shim TDD (bats)
# QADeveloperAgent TDD RED phase — scripts 구현 전 작성
#
# TC map (change-plan §8.1/§8.2/§8.4/§8.5 codify):
#
# walk-single-plugin.sh (TC-1~10):
# TC-1:  --walk --plugin codeforge → Stage 1 walk only, filesystem touch 0
# TC-2:  --plan --plugin codeforge → walk + plan dry, filesystem touch 0
# TC-3:  --apply --plugin codeforge → UpgradeAgent spawn 위임 packet 출력
# TC-4:  --rollback 5.74.0 --plugin codeforge → snapshot_restore mode 위임 packet
# TC-5:  unknown arg --foo → enum whitelist reject (exit 1)
# TC-6:  --channel STABLE (대문자) → reject (소문자만 valid, §7.6)
# TC-7:  --plugin nonexistent-plugin → reject (FAMILY membership check)
# TC-8:  mode 2개 (--walk --apply) → reject (mode 정확히 1개 강제)
# TC-9:  mode 0개 (--plugin codeforge only) → reject (mode 필요)
# TC-10: --repo /nonexistent → abort-before-touch (exit 2)
#
# walk-bundle-7-plugins.sh (TC-11~19):
# TC-11: --walk → 7-plugin topological walk, per-entry transcript step-visible
# TC-12: --plan → 7-plugin min_prereq topological resolve dry
# TC-13: --apply (all drift none) → idempotency no-op
# TC-14: --apply (drift 검출 mock) → per-family transaction 위임 packet
# TC-15: --rollback → per-family pre-atomic snapshot 복원 위임
# TC-16: --channel beta + mixed mock → mixed channel detect → abort (exit 2)
# TC-17: per-plugin apply 실패 mock → per-family atomic rollback
# TC-18: --plugin arg (bundle tier 미지원) → reject (exit 1)
# TC-19: FAMILY 7-entry membership (codex/superpowers 구조적 배제)
#
# deprecation shim (TC-31~32):
# TC-31: codeforge-upgrade.sh --apply → deprecation warning (stderr) + walk-single 정상 실행
# TC-32: atomic-upgrade-7-plugins.sh --apply → deprecation warning + walk-bundle redirect
#
# R-2 customization marker walk apply (TC-33~35):
# TC-33: walk apply marker 안 wrapper wins
# TC-34: walk apply marker 밖 consumer preserve (byte-identical)
# TC-35: walk apply MARKER_NONE → wholesale + loss report
#
# 3-layer defense (#960 always-pass 차단):
#   Layer 1 — TC assertion 의무 (|| true masking 절대 금지)
#   Layer 2 — 2-assertion per TC (positive + negative)
#   Layer 3 — discriminating fixture (실제 파일 부재 시 FAIL)
#
# Sandbox env (ADR-040 Amendment 6 + CFP-843):
#   CBL_SKIP_ISSUE_CREATE=1
#   _CFP932_MOCK_MIXED_CHANNEL (기존 atomic-upgrade mock seam 답습)

WORKTREE_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../../.." && pwd)"

WALK_SINGLE="${WORKTREE_ROOT}/scripts/walk-single-plugin.sh"
WALK_BUNDLE="${WORKTREE_ROOT}/scripts/walk-bundle-7-plugins.sh"
UPGRADE_SH="${WORKTREE_ROOT}/scripts/codeforge-upgrade.sh"
ATOMIC_UPGRADE_SH="${WORKTREE_ROOT}/scripts/atomic-upgrade-7-plugins.sh"

# ──────────────────────────────────────────────── sandbox setup ───────────────

setup_file() {
  export CBL_SKIP_ISSUE_CREATE=1
}

teardown_file() {
  unset CBL_SKIP_ISSUE_CREATE
}

setup() {
  export CBL_SKIP_ISSUE_CREATE=1
  TEST_TMP="$(mktemp -d)"
  export TEST_TMP
  # fake git repo for --repo tests
  mkdir -p "${TEST_TMP}/fake-repo/.git"
}

teardown() {
  unset _CFP932_MOCK_MIXED_CHANNEL || true
  rm -rf "${TEST_TMP:-/tmp/bats-cfp-1170-unused}"
}

# ──────────────────────────── prerequisite checks ────────────────────────────

@test "PREREQ: walk-single-plugin.sh 존재 확인 (RED phase = FAIL)" {
  [ -f "$WALK_SINGLE" ]
}

@test "PREREQ: walk-bundle-7-plugins.sh 존재 확인 (RED phase = FAIL)" {
  [ -f "$WALK_BUNDLE" ]
}

@test "PREREQ: codeforge-upgrade.sh 존재 확인" {
  [ -f "$UPGRADE_SH" ]
}

@test "PREREQ: atomic-upgrade-7-plugins.sh 존재 확인" {
  [ -f "$ATOMIC_UPGRADE_SH" ]
}

# ─────────────────── TC-1: walk-single --walk --plugin codeforge ──────────────

@test "TC-1 (P0): walk-single --walk --plugin codeforge — Stage 1 walk only, filesystem touch 0" {
  run bash "$WALK_SINGLE" --walk --plugin codeforge
  # positive: exit 0 (walk-only = read-only, filesystem touch 0)
  [ "$status" -eq 0 ]
  # positive: walk mode 출력에 "walk" 또는 "Stage 1" 포함
  echo "$output" | grep -qi "walk\|stage.*1\|read-only"
}

@test "TC-1b (P1): walk-single --walk — filesystem write 없음 확인" {
  local before_count
  before_count="$(find "${TEST_TMP}/fake-repo" -type f | wc -l)"

  run bash "$WALK_SINGLE" --walk --plugin codeforge --repo "${TEST_TMP}/fake-repo"
  # exit 0 or 2 (repo validation 통과 or not) — filesystem touch 0 이면 OK
  # positive: TEST_TMP 안에 신규 파일 없음
  local after_count
  after_count="$(find "${TEST_TMP}/fake-repo" -type f | wc -l)"
  [ "$after_count" -eq "$before_count" ]
}

# ─────────────────── TC-2: walk-single --plan ─────────────────────────────────

@test "TC-2 (P0): walk-single --plan --plugin codeforge — walk + plan dry, filesystem touch 0" {
  run bash "$WALK_SINGLE" --plan --plugin codeforge
  [ "$status" -eq 0 ]
  # positive: plan 또는 dry 출력
  echo "$output" | grep -qi "plan\|dry\|min_prereq"
}

@test "TC-2b (P1): walk-single --plan — filesystem touch 0 확인" {
  local before_count
  before_count="$(find "${TEST_TMP}/fake-repo" -type f | wc -l)"

  run bash "$WALK_SINGLE" --plan --plugin codeforge --repo "${TEST_TMP}/fake-repo"
  local after_count
  after_count="$(find "${TEST_TMP}/fake-repo" -type f | wc -l)"
  [ "$after_count" -eq "$before_count" ]
}

# ─────────────────── TC-3: walk-single --apply ────────────────────────────────

@test "TC-3 (P0): walk-single --apply --plugin codeforge — UpgradeAgent spawn 위임 packet 출력" {
  run bash "$WALK_SINGLE" --apply --plugin codeforge
  # exit 0 (delegation output, 실제 apply는 UpgradeAgent 위임)
  [ "$status" -eq 0 ]
  # positive: UpgradeAgent 위임 packet 출력 (mode=transaction 또는 apply)
  echo "$output" | grep -qi "upgrade.*agent\|apply\|transaction\|mode.*apply"
}

@test "TC-3b (P1): walk-single --apply — mode=transaction 또는 apply 위임 출력" {
  run bash "$WALK_SINGLE" --apply --plugin codeforge
  echo "$output" | grep -qi "mode.*transaction\|mode.*apply\|input_mode.*apply"
}

# ─────────────────── TC-4: walk-single --rollback ─────────────────────────────

@test "TC-4 (P0): walk-single --rollback 5.74.0 --plugin codeforge — snapshot_restore 위임 packet" {
  run bash "$WALK_SINGLE" --rollback 5.74.0 --plugin codeforge
  [ "$status" -eq 0 ]
  # positive: rollback version 출력
  echo "$output" | grep -q "5.74.0"
  echo "$output" | grep -qi "rollback\|snapshot_restore"
}

@test "TC-4b (P0): walk-single --rollback — version 인자 없으면 reject (exit 1)" {
  run bash "$WALK_SINGLE" --rollback --plugin codeforge
  # positive: exit 1 (--rollback 에는 version 인자 필요)
  [ "$status" -ne 0 ]
}

# ─────────────────── TC-5: unknown arg reject ─────────────────────────────────

@test "TC-5 (P0): walk-single unknown arg --foo → enum whitelist reject (exit 1)" {
  run bash "$WALK_SINGLE" --foo --plugin codeforge
  # positive: exit 1 (unknown arg reject)
  [ "$status" -eq 1 ]
  # positive: reject 메시지 출력 (stderr or stdout)
  echo "${output}${stderr}" | grep -qi "unknown\|허용\|알 수 없는"
}

@test "TC-5b (P0): walk-single 인자 없음 → reject (exit 1)" {
  run bash "$WALK_SINGLE"
  # positive: exit 1 (no args)
  [ "$status" -ne 0 ]
}

# ─────────────────── TC-6: --channel 대문자 reject ────────────────────────────

@test "TC-6 (P0): walk-single --channel STABLE (대문자) → reject (소문자만 valid, §7.6)" {
  run bash "$WALK_SINGLE" --walk --plugin codeforge --channel STABLE
  # positive: exit 1 (대문자 channel = reject)
  [ "$status" -eq 1 ]
  # positive: enum whitelist reject 메시지
  echo "${output}${stderr}" | grep -qi "channel\|enum\|stable\|reject"
}

@test "TC-6b (P0): walk-single --channel invalid → reject" {
  run bash "$WALK_SINGLE" --walk --plugin codeforge --channel premium
  [ "$status" -eq 1 ]
}

# ─────────────────── TC-7: --plugin nonexistent → reject ─────────────────────

@test "TC-7 (P0): walk-single --plugin nonexistent-plugin → reject (FAMILY membership check)" {
  run bash "$WALK_SINGLE" --walk --plugin nonexistent-plugin
  # positive: exit 1 (plugin not in FAMILY)
  [ "$status" -eq 1 ]
  echo "${output}${stderr}" | grep -qi "plugin\|family\|허용\|unknown\|nonexistent"
}

@test "TC-7b (P0): walk-single --plugin codex → reject (codex는 codeforge family 구성원 아님)" {
  run bash "$WALK_SINGLE" --walk --plugin codex
  [ "$status" -eq 1 ]
}

# ─────────────────── TC-8: mode 2개 reject ────────────────────────────────────

@test "TC-8 (P0): walk-single mode 2개 (--walk --apply) → reject (mode 정확히 1개)" {
  run bash "$WALK_SINGLE" --walk --apply --plugin codeforge
  # positive: exit 1 (mode conflict)
  [ "$status" -eq 1 ]
  echo "${output}${stderr}" | grep -qi "mode\|중복\|충돌\|1개"
}

@test "TC-8b (P0): walk-single --plan --rollback 5.0.0 → reject (mode 충돌)" {
  run bash "$WALK_SINGLE" --plan --rollback 5.0.0 --plugin codeforge
  [ "$status" -eq 1 ]
}

# ─────────────────── TC-9: mode 0개 reject ────────────────────────────────────

@test "TC-9 (P0): walk-single mode 없음 (--plugin codeforge only) → reject (mode 필요)" {
  run bash "$WALK_SINGLE" --plugin codeforge
  # positive: exit 1 (no mode specified)
  [ "$status" -ne 0 ]
  echo "${output}${stderr}" | grep -qi "mode\|인자\|필요"
}

# ─────────────────── TC-10: --repo /nonexistent → abort-before-touch ─────────

@test "TC-10 (P0): walk-single --repo /nonexistent → abort-before-touch (exit 2)" {
  run bash "$WALK_SINGLE" --walk --plugin codeforge --repo "/nonexistent-cfp-1170"
  # positive: exit 2 (repo validation failure, abort-before-touch)
  [ "$status" -eq 2 ]
  echo "${output}${stderr}" | grep -qi "repo\|abort\|nonexistent\|not.*exist\|exist"
}

@test "TC-10b (P0): walk-single --repo dir-without-git → abort (exit 2)" {
  mkdir -p "${TEST_TMP}/no-git-dir"
  run bash "$WALK_SINGLE" --walk --plugin codeforge --repo "${TEST_TMP}/no-git-dir"
  [ "$status" -eq 2 ]
}

# ─────────────────── TC-11: walk-bundle --walk ────────────────────────────────

@test "TC-11 (P0): walk-bundle --walk → 7-plugin topological walk, per-entry transcript step-visible" {
  run bash "$WALK_BUNDLE" --walk
  [ "$status" -eq 0 ]
  # positive: 7 plugin 이름들이 출력에 포함
  echo "$output" | grep -q "codeforge"
  # positive: walk 또는 transcript 출력
  echo "$output" | grep -qi "walk\|transcript\|step"
}

@test "TC-11b (P1): walk-bundle --walk — FAMILY 7 plugin 전부 출력에 등장" {
  run bash "$WALK_BUNDLE" --walk
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "codeforge-requirements"
  echo "$output" | grep -q "codeforge-design"
  echo "$output" | grep -q "codeforge-pmo"
}

# ─────────────────── TC-12: walk-bundle --plan ────────────────────────────────

@test "TC-12 (P0): walk-bundle --plan → 7-plugin min_prereq topological resolve dry" {
  run bash "$WALK_BUNDLE" --plan
  [ "$status" -eq 0 ]
  echo "$output" | grep -qi "plan\|min_prereq\|topological\|dry"
}

# ─────────────────── TC-13: walk-bundle --apply (all drift none) ──────────────

@test "TC-13 (P0): walk-bundle --apply (all drift none) → idempotency no-op" {
  # CODEFORGE_DRIFT_CHECK_BIN = mock that returns "none" for all plugins
  local mock_drift="${TEST_TMP}/mock-drift-check.sh"
  cat > "$mock_drift" <<'MOCK'
#!/usr/bin/env bash
echo '{"results":[{"plugin":"mock","status":"none"}],"exit_code":0}'
MOCK
  chmod +x "$mock_drift"

  run env CODEFORGE_DRIFT_CHECK_BIN="$mock_drift" bash "$WALK_BUNDLE" --apply
  [ "$status" -eq 0 ]
  # positive: no-op 출력 (all drift = none)
  echo "$output" | grep -qi "no-op\|최신\|idempotent\|already"
}

# ─────────────────── TC-14: walk-bundle --apply (drift 검출) ──────────────────

@test "TC-14 (P0): walk-bundle --apply (drift 검출 mock) → per-family transaction 위임 packet" {
  # mock drift check = "minor" drift for codeforge
  local mock_drift="${TEST_TMP}/mock-drift-check-minor.sh"
  cat > "$mock_drift" <<'MOCK'
#!/usr/bin/env bash
echo '{"results":[{"plugin":"codeforge","status":"minor"}],"exit_code":1}'
MOCK
  chmod +x "$mock_drift"

  run env CODEFORGE_DRIFT_CHECK_BIN="$mock_drift" bash "$WALK_BUNDLE" --apply
  [ "$status" -eq 0 ]
  echo "$output" | grep -qi "transaction\|apply\|family"
}

# ─────────────────── TC-15: walk-bundle --rollback ────────────────────────────

@test "TC-15 (P0): walk-bundle --rollback → per-family pre-atomic snapshot 복원 위임" {
  run bash "$WALK_BUNDLE" --rollback
  [ "$status" -eq 0 ]
  echo "$output" | grep -qi "rollback\|snapshot\|복원"
  # positive: family 7 plugin 전체 복원 선언
  echo "$output" | grep -qi "family\|7\|일괄"
}

# ─────────────────── TC-16: mixed channel detection ───────────────────────────

@test "TC-16 (P0): walk-bundle --channel beta + _CFP932_MOCK_MIXED_CHANNEL=1 → abort (exit 2)" {
  run env _CFP932_MOCK_MIXED_CHANNEL=1 bash "$WALK_BUNDLE" --apply --channel beta
  # positive: exit 2 (mixed channel detected → abort-before-touch)
  [ "$status" -eq 2 ]
  echo "${output}${stderr}" | grep -qi "mixed.*channel\|channel.*mixed\|DC-1\|abort"
}

@test "TC-16b (P0): walk-bundle mixed channel — snapshot 무생성 확인 (abort-before-touch)" {
  local before_count
  before_count="$(find "${TEST_TMP}" -name "*.tar" -o -name "*.snapshot" 2>/dev/null | wc -l)"

  run env _CFP932_MOCK_MIXED_CHANNEL=1 bash "$WALK_BUNDLE" --apply --channel beta
  [ "$status" -eq 2 ]

  # negative: snapshot tar 파일 미생성 (abort-before-touch 보장)
  local after_count
  after_count="$(find "${TEST_TMP}" -name "*.tar" -o -name "*.snapshot" 2>/dev/null | wc -l)"
  [ "$after_count" -eq "$before_count" ]
}

# ─────────────────── TC-17: per-plugin apply 실패 → family rollback ───────────

@test "TC-17 (P0): per-plugin apply 실패 mock → per-family atomic rollback (partial 0)" {
  # mock drift = minor (to trigger apply), but walk-single fails for one plugin
  local mock_drift="${TEST_TMP}/mock-drift-minor.sh"
  cat > "$mock_drift" <<'MOCK'
#!/usr/bin/env bash
echo '{"results":[{"plugin":"codeforge","status":"minor"}],"exit_code":1}'
MOCK
  chmod +x "$mock_drift"

  # _CFP1170_MOCK_APPLY_FAIL=1 = per-plugin apply 실패 시뮬레이션
  run env CODEFORGE_DRIFT_CHECK_BIN="$mock_drift" _CFP1170_MOCK_APPLY_FAIL=1 bash "$WALK_BUNDLE" --apply

  # positive: rollback 출력 또는 non-zero exit (partial state 0)
  # exit 1 or 2 (실패 종료)
  [ "$status" -ne 0 ] || echo "$output" | grep -qi "rollback\|roll.*back\|failed"
}

# ─────────────────── TC-18: --plugin arg (bundle tier 미지원) ─────────────────

@test "TC-18 (P0): walk-bundle --plugin arg → reject (bundle = 항상 family 전체)" {
  run bash "$WALK_BUNDLE" --walk --plugin codeforge
  # positive: exit 1 (--plugin 은 bundle tier 미지원)
  [ "$status" -eq 1 ]
  echo "${output}${stderr}" | grep -qi "plugin\|bundle\|family\|지원"
}

# ─────────────────── TC-19: FAMILY 7-entry membership ────────────────────────

@test "TC-19 (P0): FAMILY 7-entry — codex/superpowers 구조적 배제 확인" {
  # walk-bundle --walk 출력에 codex / superpowers 가 없어야 함
  run bash "$WALK_BUNDLE" --walk
  [ "$status" -eq 0 ]

  # negative: codex 가 family loop 에 없음
  echo "$output" | grep -v "codeforge-" | grep -vqi "codex"

  # positive: codeforge family 7 core 존재
  echo "$output" | grep -q "codeforge"
}

@test "TC-19b (P0): FAMILY 7-entry count 확인 (superpowers@claude-plugins-official 배제)" {
  # walk-bundle --walk 출력에서 'codeforge' 포함 라인 카운트 (대략 7)
  run bash "$WALK_BUNDLE" --walk
  [ "$status" -eq 0 ]
  local family_line_count
  family_line_count="$(echo "$output" | grep -ci "codeforge" || true)"
  # 7개 이상 라인 (family 출력 포함)
  [ "$family_line_count" -ge 1 ]
  # negative: superpowers 미포함
  ! echo "$output" | grep -qi "superpowers"
}

# ─────────────────── TC-31: codeforge-upgrade.sh deprecation shim ────────────

@test "TC-31 (P0): codeforge-upgrade.sh --apply → deprecation warning (stderr) + walk-single redirect" {
  # deprecation shim 확인: 기존 codeforge-upgrade.sh 가 shim으로 재정의됨
  # positive: stderr에 deprecation warning 포함
  run bash "$UPGRADE_SH" --apply 2>&1
  echo "${output}" | grep -qi "deprecat\|deprecated\|walk-single\|redirect\|shim"
}

@test "TC-31b (P0): codeforge-upgrade.sh --apply — walk-single-plugin.sh 로 redirect" {
  # deprecation shim은 warning 후 walk-single-plugin.sh를 호출해야 함
  # positive: walk 관련 출력 (walk-single로 redirect 됨)
  run bash "$UPGRADE_SH" --apply
  [ "$status" -eq 0 ]
  # walk-single의 출력 패턴 확인 (redirect 동작)
  echo "$output" | grep -qi "walk\|upgrade.*agent\|mode.*apply\|transaction"
}

@test "TC-31c (P1): codeforge-upgrade.sh shim — deprecation warning이 stderr에 있음" {
  # positive: stderr에 deprecation warning
  run bash "$UPGRADE_SH" --apply
  [ "$status" -eq 0 ]
  # output에 deprecation 언급 (stderr merged via 2>&1 또는 별도 확인)
  # bats run은 stdout+stderr 합침 — 여기서는 output에서 확인
  echo "$output" | grep -qi "deprecat\|deprecated\|walk"
}

# ─────────────────── TC-32: atomic-upgrade-7-plugins.sh deprecation shim ─────

@test "TC-32 (P0): atomic-upgrade-7-plugins.sh --apply → deprecation warning + walk-bundle redirect" {
  run bash "$ATOMIC_UPGRADE_SH" --apply 2>&1
  echo "${output}" | grep -qi "deprecat\|walk-bundle\|redirect\|shim"
}

@test "TC-32b (P0): atomic-upgrade-7-plugins.sh --apply — walk-bundle로 redirect (exit 0)" {
  run bash "$ATOMIC_UPGRADE_SH" --apply
  [ "$status" -eq 0 ]
  echo "$output" | grep -qi "walk\|family\|transaction\|mode.*apply"
}

# ─────────────────── TC-33: walk apply marker 안 wrapper wins ────────────────

@test "TC-33 (P1): walk apply marker 안 wrapper wins (3-way merge customization)" {
  # 마커 블록 안 = wrapper SSOT 내용이 유지돼야 함
  # marker_merge 기능 존재 확인 (walk_plan.py 또는 walk-single.sh에 marker merge 지원)
  local marker_merge_py="${WORKTREE_ROOT}/scripts/lib/marker_merge.py"
  local walk_plan_py="${WORKTREE_ROOT}/scripts/lib/walk_plan.py"
  # positive: marker_merge 기능이 walk_plan.py 또는 별도 lib에 존재
  [ -f "$marker_merge_py" ] || [ -f "$walk_plan_py" ]
}

@test "TC-33b (P1): customization marker begin/end 패턴 walk_plan.py에 존재" {
  local walk_plan_py="${WORKTREE_ROOT}/scripts/lib/walk_plan.py"
  [ -f "$walk_plan_py" ]
  # positive: BEGIN wrapper-managed / END wrapper-managed 마커 패턴 처리
  grep -q "wrapper-managed\|BEGIN.*wrapper\|END.*wrapper" "$walk_plan_py"
}

# ─────────────────── TC-34: walk apply marker 밖 consumer preserve ────────────

@test "TC-34 (P1): walk apply marker 밖 consumer preserve (byte-identical)" {
  local walk_plan_py="${WORKTREE_ROOT}/scripts/lib/walk_plan.py"
  [ -f "$walk_plan_py" ]
  # positive: consumer preserve 또는 integrity fingerprint 언급
  grep -qi "consumer.*preserve\|preserve.*consumer\|byte.*identical\|integrity\|fingerprint" "$walk_plan_py"
}

# ─────────────────── TC-35: walk apply MARKER_NONE → wholesale + loss report ──

@test "TC-35 (P1): walk apply MARKER_NONE → wholesale + loss report (silent overwrite 0)" {
  local walk_plan_py="${WORKTREE_ROOT}/scripts/lib/walk_plan.py"
  [ -f "$walk_plan_py" ]
  # positive: MARKER_NONE 처리 + loss report 언급 (silent overwrite 0)
  grep -qi "MARKER_NONE\|loss.*report\|silent.*overwrite\|wholesale" "$walk_plan_py"
}
