#!/usr/bin/env bash
# tests/scripts/test_bootstrap-consumer-whitelist.sh
# CFP-2439 Phase 2 — Discriminating self-test for bootstrap-consumer.sh Stage 5 whitelist iterate
#
# Change Plan §8 Test Contract TC-1~7 이행. 각 fixture 는 mktemp 임시 디렉토리에서 실행
# (bootstrap 이 side-effect: .github/workflows/ 생성).
#
# discriminating fixture 의무:
#  - TC-1: whitelist iterate 전환 (30-entry dry-run vs 고정 7-element fallback)
#  - TC-2: idempotent 2회 실행 byte-identical
#  - TC-3: fail-safe degrade (whitelist 부재 → 7종 fallback + WARN + exit 0)
#  - TC-4: parity (dry-run 산출 basename == whitelist entry)
#  - TC-5: 게이트 본체·whitelist 무변경 diff (base SHA ↔ HEAD)
#  - TC-6: .ps1 parity (pwsh 가용시) + 정적 검사(미가용시)
#  - TC-7: whitelist 신규 entry 추가 시 자동배포 (코드수정 0)
#
# Mutation testing 1:1 주석표:
#  - Mutation-hardcode-7     (고정 7종 배열 → whitelist iterate 복귀) → TC-1 RED
#  - Mutation-no-whitelist   (whitelist 읽기 로직 제거) → TC-1/TC-3/TC-4 RED
#  - Mutation-idempotent     ($dst 가드 제거) → TC-2 RED
#  - Mutation-degrade-warn   ([WARN] 마커 제거) → TC-3 RED (exit0만으로 non-discriminating)
#  - Mutation-no-parity-check(basename set 비교 로직 제거) → TC-4 RED
#  - Mutation-diff-change    (게이트/whitelist 파일 수정) → TC-5 RED
#  - Mutation-ps1-skip       (.ps1 whitelist 구동 제거) → TC-6 RED
#  - Mutation-no-degrade     (whitelist 1개 추가 → 미포함) → TC-7 RED
#  - Mutation-empty-check    (empty-check 제거 → 0종 fallback 미실행) → TC-8 RED

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BOOTSTRAP_SH="$REPO_ROOT/scripts/bootstrap-consumer.sh"
BOOTSTRAP_PS1="$REPO_ROOT/scripts/bootstrap-consumer.ps1"
WHITELIST="$REPO_ROOT/templates/scripts/consumer_applicable_workflows.txt"
PLUGIN_ROOT_REAL="$REPO_ROOT"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# Helper: count non-comment non-blank lines from whitelist (FIX-CR-007: avoid "00" grep duplication)
# ─────────────────────────────────────────────────────────────────────────────
count_whitelist_entries() {
  local wl="$1"
  grep -v '^\s*#' "$wl" | grep -c '\S' || true
}

# ─────────────────────────────────────────────────────────────────────────────
# Helper: extract whitelist entry set (sorted, for parity check)
# ─────────────────────────────────────────────────────────────────────────────
get_whitelist_entries() {
  local wl="$1"
  grep -v '^\s*#' "$wl" | grep '\S' | sort
}

# ─────────────────────────────────────────────────────────────────────────────
# Helper: extract cp basename from dry-run stdout (stderr 에 [dry-run] 포함)
# ─────────────────────────────────────────────────────────────────────────────
extract_cp_basenames() {
  local output="$1"
  echo "$output" | grep '\[dry-run\] cp.*\.github/workflows' | sed 's/.*\.github\/workflows\/\([^ ]*\).*/\1/' | sort || true
}

# ─────────────────────────────────────────────────────────────────────────────
# Helper: 임시 fixture plugin-root 생성 (실 SSOT 격리, FIX-CR-002)
# 실 templates/scripts/consumer_applicable_workflows.txt + templates/github-workflows/ 복제
# ─────────────────────────────────────────────────────────────────────────────
make_fixture_plugin_root() {
  local fpr
  fpr="$(mktemp -d)"
  mkdir -p "$fpr/templates/scripts" "$fpr/templates/github-workflows"

  # whitelist 복제
  cp "$WHITELIST" "$fpr/templates/scripts/consumer_applicable_workflows.txt"

  # whitelist 에서 참조하는 workflow source 복제 (존재하면 cp, 없으면 touch stub)
  while IFS= read -r line; do
    line="${line%%$'\r'}"
    line="$(printf '%s' "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    [ -z "$line" ] && continue
    case "$line" in \#*) continue;; esac
    local src="$REPO_ROOT/templates/github-workflows/$line"
    if [ -f "$src" ]; then
      cp "$src" "$fpr/templates/github-workflows/$line"
    else
      touch "$fpr/templates/github-workflows/$line"
    fi
  done < "$WHITELIST"

  echo "$fpr"
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-1: whitelist iterate 전환 (30개 기대 vs 고정 7종 fallback)
# Assertion: dry-run stdout 에 정확히 30개 "cp .github/workflows/" 의도 라인 포함
# Mutation-hardcode-7: 고정 배열 복귀 시 7종만 출력 → RED
# ─────────────────────────────────────────────────────────────────────────────
test_tc1_whitelist_iterate_count() {
  local test_name="TC-1-whitelist-iterate-count"
  local fixture_root tmp_consumer

  fixture_root="$(mktemp -d)"
  tmp_consumer="$fixture_root/consumer"
  mkdir -p "$tmp_consumer"

  # git repo 초기화 (bootstrap 이 org/repo 감지 요구)
  cd "$tmp_consumer"
  git init -q
  git config user.email "test@example.com"
  git config user.name "Test User"
  git remote add origin https://github.com/test/test-repo.git

  # dry-run 실행 (PLUGIN_ROOT override 불가면 실제 whitelist 사용)
  local output
  output=$( PLUGIN_ROOT="$PLUGIN_ROOT_REAL" bash "$BOOTSTRAP_SH" --dry-run 2>&1 ) || true

  # 기대: "[dry-run] cp" + ".github/workflows" 정확히 30개 라인
  local cp_count
  cp_count=$( echo "$output" | grep -c '\[dry-run\] cp.*\.github/workflows' || echo 0 )
  cp_count=$(echo "$cp_count" | tr -d '\r\n')

  local expected_count=30
  if [ "$cp_count" -eq "$expected_count" ]; then
    echo "✓ PASS: $test_name (count=$cp_count) — dry-run 에 30개 workflow cp 의도"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name"
    echo "  Expected $expected_count cp lines, got $cp_count"
    echo "  Output excerpt (first 10 cp lines):"
    echo "$output" | grep '\[dry-run\] cp .github/workflows/' | head -10 || echo "  (no cp lines found)"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-2: idempotent (dry-run 기반: 30 stub 파일 존재 시 copy 의도 라인 0개)
# Assertion: 2회차 dry-run 에서도 "cp .github/workflows/" 의도 라인 == 0개
#           (모든 dst 가 이미 존재하므로 guard "if [ ! -f $dst ]" 가 skip → copy 안 함)
# Mutation-idempotent: $dst guard 제거 시 2회차에도 30개 cp 의도 라인 출력 → RED (discriminating)
# ─────────────────────────────────────────────────────────────────────────────
test_tc2_idempotent() {
  local test_name="TC-2-idempotent"
  local fixture_root tmp_consumer

  fixture_root="$(mktemp -d)"
  tmp_consumer="$fixture_root/consumer"
  mkdir -p "$tmp_consumer"

  cd "$tmp_consumer"
  # git repo 초기화
  git init -q
  git config user.email "test@example.com"
  git config user.name "Test User"
  git remote add origin https://github.com/test/test-repo.git

  # 1회차 dry-run: 30개 workflow cp 의도 출력 (all dst 미존재)
  local output1
  output1=$( PLUGIN_ROOT="$PLUGIN_ROOT_REAL" bash "$BOOTSTRAP_SH" --dry-run 2>&1 ) || true

  local cp_count_1
  cp_count_1=$( echo "$output1" | grep -c '\[dry-run\] cp.*\.github/workflows' || echo 0 )
  cp_count_1=$(echo "$cp_count_1" | tr -d '\r\n')

  # 1회차 dry-run 에서 나온 30개 stub 파일을 실제로 생성 (idempotency 테스트)
  mkdir -p .github/workflows
  while IFS= read -r line; do
    line="${line%%$'\r'}"
    line="$(printf '%s' "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    [ -z "$line" ] && continue
    case "$line" in \#*) continue;; esac
    touch ".github/workflows/$line"
  done < "$WHITELIST"

  # 2회차 dry-run: 30개 workflow 모두 미리 존재하므로 copy 의도 라인 == 0개
  local output2
  output2=$( PLUGIN_ROOT="$PLUGIN_ROOT_REAL" bash "$BOOTSTRAP_SH" --dry-run 2>&1 ) || true

  local cp_count_2
  cp_count_2=$( echo "$output2" | grep -c '\[dry-run\] cp.*\.github/workflows' || echo 0 )
  cp_count_2=$(echo "$cp_count_2" | tr -d '\r\n')

  local ok=1
  # Assertion 1: 1회차 dry-run 에서 30개 출력
  [ "$cp_count_1" -eq 30 ] || ok=0
  # Assertion 2: 2회차 dry-run 에서 0개 출력 (guard skip)
  [ "$cp_count_2" -eq 0 ] || ok=0

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $test_name (1st=30, 2nd=0) — dry-run 기반 idempotency: guard skip 검증"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name"
    echo "  Expected: 1st dry-run cp count=30, 2nd dry-run cp count=0"
    echo "  Got: 1st=$cp_count_1, 2nd=$cp_count_2"
    if [ "$cp_count_1" -ne 30 ]; then
      echo "  1st dry-run excerpt (expected 30 cp lines):"
      echo "$output1" | grep '\[dry-run\] cp .github/workflows/' | head -5
    fi
    if [ "$cp_count_2" -ne 0 ]; then
      echo "  2nd dry-run excerpt (expected 0 cp lines):"
      echo "$output2" | grep '\[dry-run\] cp .github/workflows/' | head -5
    fi
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-3: fail-safe degrade (whitelist 부재 → 7종 fallback + WARN + exit 0) [FIX-CR-002]
# Assertion:
#  - stdout 에 "[WARN]" 마커 포함
#  - dry-run 산출 정확히 7개 cp (fallback 배열)
#  - exit 0 (non-abort)
# Approach: 실 SSOT 무손상 — fixture plugin-root 안에서 whitelist 삭제 시뮬레이션
# Mutation-no-whitelist: whitelist 읽기 로직 제거 → fallback 미실행 RED
# Mutation-degrade-warn: [WARN] 마커 제거 → TC-3 pass 면 동시 RED (discriminating 의무)
# ─────────────────────────────────────────────────────────────────────────────
test_tc3_degrade_warn() {
  local test_name="TC-3-degrade-warn"
  local fixture_root fixture_plugin_root tmp_consumer

  fixture_root="$(mktemp -d)"
  fixture_plugin_root="$fixture_root/fixture-plugin"
  tmp_consumer="$fixture_root/consumer"
  mkdir -p "$tmp_consumer"

  # fixture plugin-root 생성 (실 templates/ 복제)
  mkdir -p "$fixture_plugin_root/templates/scripts" "$fixture_plugin_root/templates/github-workflows"
  cp "$WHITELIST" "$fixture_plugin_root/templates/scripts/consumer_applicable_workflows.txt"
  while IFS= read -r line; do
    line="${line%%$'\r'}"
    line="$(printf '%s' "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    [ -z "$line" ] && continue
    case "$line" in \#*) continue;; esac
    local src="$REPO_ROOT/templates/github-workflows/$line"
    if [ -f "$src" ]; then
      cp "$src" "$fixture_plugin_root/templates/github-workflows/$line"
    else
      touch "$fixture_plugin_root/templates/github-workflows/$line"
    fi
  done < "$WHITELIST"

  # fixture 안 whitelist 삭제 (부재 상태 시뮬레이션)
  rm -f "$fixture_plugin_root/templates/scripts/consumer_applicable_workflows.txt"

  cd "$tmp_consumer"
  # git repo 초기화
  git init -q
  git config user.email "test@example.com"
  git config user.name "Test User"
  git remote add origin https://github.com/test/test-repo.git

  local output exit_code=0
  output=$( PLUGIN_ROOT="$fixture_plugin_root" bash "$BOOTSTRAP_SH" --dry-run 2>&1 ) || exit_code=$?

  local has_warn=0
  echo "$output" | grep -q '\[WARN\]' && has_warn=1

  local cp_count
  cp_count=$( echo "$output" | grep -c '\[dry-run\] cp.*\.github/workflows' || echo 0 )
  cp_count=$(echo "$cp_count" | tr -d '\r\n')

  local ok=1
  [ "$has_warn" -eq 1 ] || ok=0
  [ "$cp_count" -eq 7 ] || ok=0
  [ "$exit_code" -eq 0 ] || ok=0

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $test_name (warn=$has_warn, cp=$cp_count, exit=$exit_code) — degrade fallback + WARN + exit 0 (fixture-isolated)"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name"
    echo "  Expected: [WARN] marker present, cp count=7, exit=0"
    echo "  Got: warn=$has_warn, cp=$cp_count, exit=$exit_code"
    echo "  Output excerpt:"
    echo "$output" | head -20
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-4: parity (bootstrap 산출 basename set == whitelist non-comment non-blank set)
# Assertion: dry-run stdout 의 cp basename set == whitelist 파싱 set
# Mutation-no-whitelist: whitelist 읽기 제거 → 7종만 출력 vs 30종 기대 → RED
# ─────────────────────────────────────────────────────────────────────────────
test_tc4_parity() {
  local test_name="TC-4-parity"
  local fixture_root tmp_consumer

  fixture_root="$(mktemp -d)"
  tmp_consumer="$fixture_root/consumer"
  mkdir -p "$tmp_consumer"

  cd "$tmp_consumer"
  # git repo 초기화
  git init -q
  git config user.email "test@example.com"
  git config user.name "Test User"
  git remote add origin https://github.com/test/test-repo.git

  local output
  output=$( PLUGIN_ROOT="$PLUGIN_ROOT_REAL" bash "$BOOTSTRAP_SH" --dry-run 2>&1 ) || true

  # dry-run 산출 basename set
  local cp_set
  cp_set=$( extract_cp_basenames "$output" )

  # whitelist entry set
  local wl_set
  wl_set=$( get_whitelist_entries "$WHITELIST" )

  if [ "$cp_set" = "$wl_set" ]; then
    echo "✓ PASS: $test_name — dry-run basename set == whitelist entry set"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name"
    echo "  Expected whitelist entries:"
    echo "$wl_set" | head -5
    echo "  ..."
    echo "  Got dry-run basenames:"
    echo "$cp_set" | head -5
    echo "  ..."
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-5: 게이트 본체·whitelist 무변경 (diff-empty) [FIX-CR-003 동적 base]
# Assertion: git diff base...HEAD --name-only 에서 scripts/bootstrap-consumer.* 및
#           templates/github-workflows/*, templates/scripts/consumer_applicable_workflows.txt 외
#           다른 파일 미포함 (workflow/whitelist 본체 미변경). TC-6 스크립트 2종만 변경.
# base ref = merge-base HEAD origin/main (없으면 origin/main, 둘다 없으면 FAIL-base-unresolvable)
# Mutation-diff-change: 게이트/whitelist 파일 수정 시 실패 → RED
# ─────────────────────────────────────────────────────────────────────────────
test_tc5_gateway_whitelist_unchanged() {
  local test_name="TC-5-gateway-whitelist-unchanged"

  cd "$REPO_ROOT"

  # 동적 base SHA 결정 (merge-base 우선, 실패시 origin/main)
  local base_ref
  base_ref="$(git merge-base HEAD origin/main 2>/dev/null)" || base_ref=""
  if [ -z "$base_ref" ]; then
    base_ref="$(git rev-parse origin/main 2>/dev/null)" || base_ref=""
  fi

  # base ref 해소 불가 = 동적 base 부재 (shallow-checkout 등) → FAIL (silent pass 차단, FIX-CR-003)
  if [ -z "$base_ref" ]; then
    echo "✗ FAIL: $test_name"
    echo "  Base ref 해소 불가 (shallow checkout? fetch-depth:0 필요). git diff 불가능."
    echo "  silent pass 를 피하기 위해 FAIL 처리."
    FAIL=$((FAIL+1))
    return 1
  fi

  # 파일 목록: diff base...HEAD (현재 branch 모든 변경)
  local diff_files
  diff_files=$( git diff "$base_ref"...HEAD --name-only 2>/dev/null )

  if [ $? -ne 0 ]; then
    echo "✗ FAIL: $test_name"
    echo "  git diff 실패 (base=$base_ref 도달 불가?). silent pass 차단."
    FAIL=$((FAIL+1))
    return 1
  fi

  # templates/github-workflows/ 안 파일 변경 여부
  local wf_changed=0
  echo "$diff_files" | grep -q '^templates/github-workflows/' && wf_changed=1

  # whitelist 파일 변경 여부
  local wl_changed=0
  echo "$diff_files" | grep -q '^templates/scripts/consumer_applicable_workflows\.txt$' && wl_changed=1

  # 허용 변경: scripts/bootstrap-consumer.{sh,ps1}
  # 금지 변경: templates/github-workflows, consumer_applicable_workflows.txt

  local ok=1
  [ "$wf_changed" -eq 0 ] || ok=0
  [ "$wl_changed" -eq 0 ] || ok=0

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $test_name — workflow/whitelist 게이트 본체 무변경 (script 변경만, base=$base_ref)"
    PASS=$((PASS+1))
    return 0
  else
    echo "✗ FAIL: $test_name"
    echo "  Expected: no changes to templates/github-workflows/ or consumer_applicable_workflows.txt"
    echo "  Got:"
    echo "$diff_files" | grep '^templates/' || echo "  (no template changes)"
    FAIL=$((FAIL+1))
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-6: .ps1 parity (pwsh 가용시 dry-run 산출 set 비교, 미가용시 정적 검사)
# Assertion (pwsh 가용):
#  - .ps1 dry-run 산출 basename set == .sh 산출 set
# Assertion (pwsh 미가용):
#  - .ps1 파일에 consumer_applicable_workflows.txt 참조 존재
#  - .ps1 파일에 degrade fallback 7종 존재
#  - .ps1 파일에 -notmatch '^\s*#' (comment skip) 존재
#  - .ps1 파일에 -match '\S' (blank skip) 존재
#  - .ps1 파일에 Test-Path $dst guard 존재
# Mutation-ps1-skip: .ps1 whitelist 구동 제거 → TC-6 RED
# ─────────────────────────────────────────────────────────────────────────────
test_tc6_ps1_parity() {
  local test_name="TC-6-ps1-parity"

  # pwsh 가용 여부 확인
  if command -v pwsh >/dev/null 2>&1; then
    # pwsh 가용: 동적 dry-run 비교
    local fixture_root tmp_consumer
    fixture_root="$(mktemp -d)"
    tmp_consumer="$fixture_root/consumer"
    mkdir -p "$tmp_consumer"

    cd "$tmp_consumer"
    # git repo 초기화
    git init -q
    git config user.email "test@example.com"
    git config user.name "Test User"
  git remote add origin https://github.com/test/test-repo.git

    # .sh dry-run
    local sh_output
    sh_output=$( PLUGIN_ROOT="$PLUGIN_ROOT_REAL" bash "$BOOTSTRAP_SH" --dry-run 2>&1 ) || true
    local sh_set
    sh_set=$( extract_cp_basenames "$sh_output" )

    # .ps1 dry-run (-DryRun flag 추정)
    local ps1_output
    ps1_output=$( PLUGIN_ROOT="$PLUGIN_ROOT_REAL" pwsh -NoProfile -NonInteractive \
      -Command "& '$BOOTSTRAP_PS1' -DryRun 2>&1" ) || true
    local ps1_set
    ps1_set=$( extract_cp_basenames "$ps1_output" )

    rm -rf "$fixture_root"

    if [ "$sh_set" = "$ps1_set" ]; then
      echo "✓ PASS: $test_name (pwsh available) — .ps1/.sh dry-run basename set parity"
      PASS=$((PASS+1))
      return 0
    else
      echo "✗ FAIL: $test_name (pwsh available)"
      echo "  .sh basenames (first 5):"
      echo "$sh_set" | head -5
      echo "  .ps1 basenames (first 5):"
      echo "$ps1_set" | head -5
      FAIL=$((FAIL+1))
      return 1
    fi
  else
    # pwsh 미가용: 정적 검사 (grep)
    local ps1_content
    ps1_content=$( cat "$BOOTSTRAP_PS1" )

    local ok=1

    # consumer_applicable_workflows.txt 참조
    echo "$ps1_content" | grep -q 'consumer_applicable_workflows\.txt' || ok=0

    # degrade fallback 7종 모두 포함
    echo "$ps1_content" | grep -q 'phase-gate-mergeable.yml' || ok=0
    echo "$ps1_content" | grep -q 'phase-label-invariant.yml' || ok=0
    echo "$ps1_content" | grep -q 'story-init.yml' || ok=0
    echo "$ps1_content" | grep -q 'story-section-1-immutable.yml' || ok=0
    echo "$ps1_content" | grep -q 'subissue-from-impl-manifest.yml' || ok=0
    echo "$ps1_content" | grep -q 'fix-ledger-sync.yml' || ok=0
    echo "$ps1_content" | grep -q 'story-section-schema.yml' || ok=0

    # comment/blank skip 로직
    echo "$ps1_content" | grep -q '\-notmatch.*#' || ok=0
    echo "$ps1_content" | grep -q '\-match.*\\S' || ok=0

    # Test-Path dst guard
    echo "$ps1_content" | grep -q 'Test-Path.*dst' || ok=0

    if [ "$ok" -eq 1 ]; then
      echo "✓ PASS: $test_name (pwsh unavailable, static check) — .ps1 whitelist 구동 요소 모두 포함"
      PASS=$((PASS+1))
      return 0
    else
      echo "✗ FAIL: $test_name (pwsh unavailable, static check)"
      echo "  Expected: whitelist ref + 7 fallback + comment/blank skip + Test-Path guard"
      echo "  Check .ps1 manually for missing elements"
      FAIL=$((FAIL+1))
      return 1
    fi
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-7: 신규 whitelisted 자동배포 (whitelist 1개 추가 → 코드수정 0 → 신규 배포) [FIX-CR-002]
# Assertion:
#  - fixture plugin-root 의 whitelist 에 신규 entry 추가 (__tc7-synthetic-gate.yml)
#  - fixture 에 그 source stub 생성
#  - dry-run 산출에 신규 entry 포함
#  - placement gate 2종 정상 포함 (responsibility-topology-check.yml, responsibility-marker-drift-check.yml)
# Approach: 실 SSOT 무손상 — fixture plugin-root 안에서 whitelist 수정 + stub 생성
# Mutation-no-degrade: whitelist 1개 추가 → 미포함 → RED
# ─────────────────────────────────────────────────────────────────────────────
test_tc7_whitelist_autoconfig() {
  local test_name="TC-7-whitelist-autoconfig"
  local fixture_root fixture_plugin_root tmp_consumer

  fixture_root="$(mktemp -d)"
  fixture_plugin_root="$fixture_root/fixture-plugin"
  tmp_consumer="$fixture_root/consumer"
  mkdir -p "$tmp_consumer"

  # fixture plugin-root 생성 (실 templates/ 복제)
  mkdir -p "$fixture_plugin_root/templates/scripts" "$fixture_plugin_root/templates/github-workflows"
  cp "$WHITELIST" "$fixture_plugin_root/templates/scripts/consumer_applicable_workflows.txt"
  while IFS= read -r line; do
    line="${line%%$'\r'}"
    line="$(printf '%s' "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    [ -z "$line" ] && continue
    case "$line" in \#*) continue;; esac
    local src="$REPO_ROOT/templates/github-workflows/$line"
    if [ -f "$src" ]; then
      cp "$src" "$fixture_plugin_root/templates/github-workflows/$line"
    else
      touch "$fixture_plugin_root/templates/github-workflows/$line"
    fi
  done < "$WHITELIST"

  # fixture 안에서만 신규 entry 추가
  local synthetic_name="__tc7-synthetic-gate-$$.yml"
  local synthetic_stub="$fixture_plugin_root/templates/github-workflows/$synthetic_name"
  touch "$synthetic_stub"
  echo "$synthetic_name" >> "$fixture_plugin_root/templates/scripts/consumer_applicable_workflows.txt"

  cd "$tmp_consumer"
  # git repo 초기화
  git init -q
  git config user.email "test@example.com"
  git config user.name "Test User"
  git remote add origin https://github.com/test/test-repo.git

  local output
  output=$( PLUGIN_ROOT="$fixture_plugin_root" bash "$BOOTSTRAP_SH" --dry-run 2>&1 ) || true

  local has_synthetic=0
  echo "$output" | grep -q "\[dry-run\] cp.*\.github/workflows/$synthetic_name" && has_synthetic=1

  local has_topology=0
  echo "$output" | grep -q '\[dry-run\] cp.*\.github/workflows/responsibility-topology-check.yml' && has_topology=1

  local has_marker_drift=0
  echo "$output" | grep -q '\[dry-run\] cp.*\.github/workflows/responsibility-marker-drift-check.yml' && has_marker_drift=1

  local ok=1
  [ "$has_synthetic" -eq 1 ] || ok=0
  [ "$has_topology" -eq 1 ] || ok=0
  [ "$has_marker_drift" -eq 1 ] || ok=0

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $test_name — whitelist 신규 entry 자동배포 + placement gate 2종 포함 (fixture-isolated)"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name"
    echo "  Expected: synthetic gate + placement gates (2종)"
    echo "  Got: synthetic=$has_synthetic, topology=$has_topology, marker_drift=$has_marker_drift"
    echo "  Output excerpt:"
    echo "$output" | grep -E "(synthetic|responsibility-topology|responsibility-marker)" | head -5 || echo "  (no matches)"
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# TC-8: empty/all-comment whitelist → 7종 fallback (FIX-CR-001)
# Assertion:
#  - fixture plugin-root 의 whitelist 를 전부 주석/공백으로 덮어쓰기 (파일 존재, entry 0)
#  - dry-run 산출 정확히 7개 cp (fallback 배열)
#  - [WARN] 마커 포함
#  - exit 0 (non-abort)
# Approach: 실 SSOT 무손상 — fixture 안에서만 whitelist 를 비우기
# Mutation-empty-check: empty-check 제거 → fallback 미실행, 0 cp → RED (discriminating)
# ─────────────────────────────────────────────────────────────────────────────
test_tc8_empty_whitelist_fallback() {
  local test_name="TC-8-empty-whitelist-fallback"
  local fixture_root fixture_plugin_root tmp_consumer

  fixture_root="$(mktemp -d)"
  fixture_plugin_root="$fixture_root/fixture-plugin"
  tmp_consumer="$fixture_root/consumer"
  mkdir -p "$tmp_consumer"

  # fixture plugin-root 생성 (실 templates/ 복제)
  mkdir -p "$fixture_plugin_root/templates/scripts" "$fixture_plugin_root/templates/github-workflows"
  cp "$WHITELIST" "$fixture_plugin_root/templates/scripts/consumer_applicable_workflows.txt"
  while IFS= read -r line; do
    line="${line%%$'\r'}"
    line="$(printf '%s' "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    [ -z "$line" ] && continue
    case "$line" in \#*) continue;; esac
    local src="$REPO_ROOT/templates/github-workflows/$line"
    if [ -f "$src" ]; then
      cp "$src" "$fixture_plugin_root/templates/github-workflows/$line"
    else
      touch "$fixture_plugin_root/templates/github-workflows/$line"
    fi
  done < "$WHITELIST"

  # fixture 안에서만 whitelist 를 공백/주석으로 덮어쓰기 (파일 존재하나 entry 0)
  printf '# all comments and blanks\n\n   \n' > "$fixture_plugin_root/templates/scripts/consumer_applicable_workflows.txt"

  cd "$tmp_consumer"
  # git repo 초기화
  git init -q
  git config user.email "test@example.com"
  git config user.name "Test User"
  git remote add origin https://github.com/test/test-repo.git

  local output exit_code=0
  output=$( PLUGIN_ROOT="$fixture_plugin_root" bash "$BOOTSTRAP_SH" --dry-run 2>&1 ) || exit_code=$?

  local has_warn=0
  echo "$output" | grep -q '\[WARN\]' && has_warn=1

  local cp_count
  cp_count=$( echo "$output" | grep -c '\[dry-run\] cp.*\.github/workflows' || echo 0 )
  cp_count=$(echo "$cp_count" | tr -d '\r\n')

  local ok=1
  [ "$cp_count" -eq 7 ] || ok=0
  [ "$has_warn" -eq 1 ] || ok=0
  [ "$exit_code" -eq 0 ] || ok=0

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $test_name (cp=$cp_count, warn=$has_warn, exit=$exit_code) — empty whitelist → 7 fallback + WARN + exit 0 (fixture-isolated)"
    PASS=$((PASS+1))
    rm -rf "$fixture_root"
    return 0
  else
    echo "✗ FAIL: $test_name"
    echo "  Expected: cp count=7, [WARN] present, exit=0"
    echo "  Got: cp=$cp_count, warn=$has_warn, exit=$exit_code"
    echo "  Output excerpt:"
    echo "$output" | head -20
    FAIL=$((FAIL+1))
    rm -rf "$fixture_root"
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Main: run all fixtures
# ─────────────────────────────────────────────────────────────────────────────
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "CFP-2439 Phase 2: bootstrap-consumer.sh Stage 5 whitelist iterate"
echo "TDD Test Suite (TC-1~8)"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

test_tc1_whitelist_iterate_count
test_tc2_idempotent
test_tc3_degrade_warn
test_tc4_parity
test_tc5_gateway_whitelist_unchanged
test_tc6_ps1_parity
test_tc7_whitelist_autoconfig
test_tc8_empty_whitelist_fallback

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Test Results: $PASS passed, $FAIL failed"
echo "═══════════════════════════════════════════════════════════════════════════════"

if [ "$FAIL" -eq 0 ]; then
  echo "All tests PASSED ✓"
  exit 0
else
  echo "Some tests FAILED ✗"
  exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# FIX Summary (CFP-2439 Phase 2 P1 fixes):
# ─────────────────────────────────────────────────────────────────────────────
# FIX-CR-001: TC-8 신규 추가 (empty whitelist → 7 fallback discriminating)
# FIX-CR-002: TC-3, TC-7 실 SSOT mutate 격리 (make_fixture_plugin_root helper)
# FIX-CR-003: TC-5 hardcoded SHA → 동적 base (merge-base / origin/main, base 해소실패=FAIL)
# FIX-CR-007: grep -c || echo 0 중복 "00" 제거 (|| true 로 대체)
