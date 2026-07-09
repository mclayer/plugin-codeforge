#!/usr/bin/env bash
# tests/scripts/test_spawn_description_prefix.sh
# CFP-2574 Phase 2 (QADev — §8 Test Contract 이행) — Discriminating suite for
#   ADR-143 Agent 수행 액션 렌더 줄 프리픽스 규약 (`[에이전트명] MM/DD HH:MM - 내용`).
#
# 대상 Dev 스크립트 인터페이스 (계약 고정):
#   A. scripts/lib/kst_render_stamp.py            — `--epoch <s>` → stdout `MM/DD HH:MM\n`, stderr 빈, exit 0. UTC+9 고정 산술.
#   B. scripts/lib/check_spawn_description_prefix.py — `--description-stdin` → stdout JSON
#        {"description_prefix_conformant":<bool>,"empty":<bool>,...}, exit 0 ALWAYS.
#        conformant regex = ^\[[^\]]{1,64}\] \d{2}/\d{2} \d{2}:\d{2} - .
#   D. scripts/lib/check_kst_timestamp.py (기존, 무편집) — KST_TS_RE (full-zoned only).
#
# 3 spec invariant ↔ assertion 1:1 매핑:
#   INV-1 (exit-0-always)  : T-1 — detector 는 어떤 description 에도 exit 0 (advisory, non-blocking).
#   INV-2 (tz-invariance)  : T-2 — 동일 epoch 를 TZ 3환경에서 실행 → 3 출력 동일 (anti-`TZ=Asia/Seoul` 회귀).
#   INV-3 (lint-inert)     : T-4 — 컴팩트 `MM/DD HH:MM` 은 KST_TS_RE 미매칭 (문서 예시 자유 배치).
#
# distinct-marker 규율 (agent §외부 script subprocess fork): 각 fork 판정은 도메인 exit code
#   단독이 아니라 도메인 고유 stdout sentinel (JSON 필드 / 정확 stamp 문자열 / 'T4-*-OK') 을
#   병행 assert — 미 fork 시 interpreter exit(2 "can't open file") 와 우연 일치하는 silent
#   false-positive 를 차단한다.
#
# ─── §8.NOT — 테스트-불가 영역 정직 명시 (검사연극 금지, ADR-143 §결정 4 / ADR-119 §결정 6) ───
#   · 범위② leaf 도구호출 description = model-authored + ephemeral(scan target 파일 부재)
#       → NO mechanical test 가능. 강제 상한 = prompt-mandate + 리마인더 advisory (본 suite 대상 아님).
#   · agent actual-time-acquisition(실시계 HH:MM 원천) = untestable — harness 는 날짜만 주입
#       [anthropics/claude-code #34530 Closed "not planned"]. 본 suite 는 KST 산술 helper 의
#       정확성/TZ-invariance 만 검증하지 exact per-call wall-clock 을 검증하지 않는다.
#   · TodoWrite absence = structural exclusion — PreToolUse(Agent) matcher 가 TodoWrite 에
#       미발화(ADR-038 §결정 2 Amd5 native status 채널). "프리픽스 부재" 는 구조적 제외지 결함 아님 → 테스트 대상 아님.
#   · §8.5 stateful (long-running invariant / restart recovery / idempotency replay) = false N/A —
#       본 규약은 순수 표시 sub-layer(ephemeral, zero persist path), stateful 표면 0.
#
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS, FAIL>0 이면 exit 1.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PREFIX="$REPO_ROOT/scripts/lib/check_spawn_description_prefix.py"
KST="$REPO_ROOT/scripts/lib/kst_render_stamp.py"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# T-1: spawn-header description-format DETECT + exit-0-always (INV-1)
#   detector 에 fixture 를 stdin 으로 주고 JSON `description_prefix_conformant` +
#   exit code(항상 0) 를 assert. distinct-marker = JSON 필드 값 (미 fork 시 파싱 실패 → PARSE_ERR).
# ─────────────────────────────────────────────────────────────────────────────
run_prefix_case() {
  local name="$1" fixture="$2" expected_conformant="$3" description="$4"
  local exit_code=0 raw parsed
  raw=$(printf '%s' "$fixture" | python3 "$PREFIX" --description-stdin 2>/dev/null) || exit_code=$?
  parsed=$(printf '%s' "$raw" | python3 -c "import json,sys;print(json.load(sys.stdin)['description_prefix_conformant'])" 2>/dev/null) || parsed="PARSE_ERR"
  # INV-1: exit MUST be 0 always (advisory) AND conformant field must match (distinct-marker).
  if [ "$exit_code" -eq 0 ] && [ "$parsed" = "$expected_conformant" ]; then
    echo "✓ PASS: $name (exit 0, conformant=$parsed) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit 0 ∧ conformant=$expected_conformant, got exit=$exit_code conformant=$parsed"
    echo "  Raw: $raw"
    FAIL=$((FAIL+1))
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2574 / ADR-143 — T-1: spawn description-format DETECT + exit-0-always (INV-1)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# 1: CONFORMANT — 정식 형식 (bracket + MM/DD HH:MM + ' - ' + 내용)
run_prefix_case "T1-1: CONFORMANT 정식 형식" \
  '[ArchitectAgent] 07/05 14:30 - Change Plan 통합' \
  "True" "정식 '[에이전트명] MM/DD HH:MM - 내용' → conformant=true, exit 0"

# 2: nonconformant — missing-bracket ([...] 부재)
run_prefix_case "T1-2: nonconformant missing-bracket" \
  'ArchitectAgent 07/05 14:30 - x' \
  "False" "대괄호 프리픽스 부재 → conformant=false, exit 0 (INV-1)"

# 3: nonconformant — missing-time (HH:MM 부재)
run_prefix_case "T1-3: nonconformant missing-time" \
  '[ArchitectAgent] 07/05 - x' \
  "False" "HH:MM 시각 부재 → conformant=false, exit 0 (INV-1)"

# 4: nonconformant — date-sep-hyphen (날짜 구분자 '/' 아닌 '-')
run_prefix_case "T1-4: nonconformant date-sep-hyphen" \
  '[ArchitectAgent] 07-05 14:30 - x' \
  "False" "날짜 구분자 '-' (정식 '/' 위반) → conformant=false, exit 0 (INV-1)"

# 5: nonconformant — offset-present (컴팩트 규약 위반, offset 부착)
run_prefix_case "T1-5: nonconformant offset-present" \
  '[ArchitectAgent] 07/05 14:30+09:00 - x' \
  "False" "offset(+09:00) 부착 (컴팩트 offset-less 위반) → conformant=false, exit 0 (INV-1)"

# 6: nonconformant — double-space (시각 뒤 이중 공백)
run_prefix_case "T1-6: nonconformant double-space" \
  '[ArchitectAgent] 07/05 14:30  - x' \
  "False" "시각 뒤 이중 공백 (정식 ' - ' 위반) → conformant=false, exit 0 (INV-1)"

# 7: nonconformant — wrong-sep-colon (구분자 ' - ' 아닌 ':')
run_prefix_case "T1-7: nonconformant wrong-sep-colon" \
  '[ArchitectAgent] 07/05 14:30: x' \
  "False" "구분자 ':' (정식 ' - ' 위반) → conformant=false, exit 0 (INV-1)"

# 8: empty description → empty=true ∧ conformant=true, exit 0 (빈 description 은 위반 아님)
empty_exit=0
empty_raw=$(printf '%s' "" | python3 "$PREFIX" --description-stdin 2>/dev/null) || empty_exit=$?
empty_empty=$(printf '%s' "$empty_raw" | python3 -c "import json,sys;print(json.load(sys.stdin)['empty'])" 2>/dev/null) || empty_empty="PARSE_ERR"
empty_conf=$(printf '%s' "$empty_raw" | python3 -c "import json,sys;print(json.load(sys.stdin)['description_prefix_conformant'])" 2>/dev/null) || empty_conf="PARSE_ERR"
if [ "$empty_exit" -eq 0 ] && [ "$empty_empty" = "True" ] && [ "$empty_conf" = "True" ]; then
  echo "✓ PASS: T1-8: empty description (empty=$empty_empty conformant=$empty_conf, exit 0) — 빈 description 은 위반 아님 (INV-1)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T1-8: empty description"
  echo "  Expected exit 0 ∧ empty=True ∧ conformant=True, got exit=$empty_exit empty=$empty_empty conformant=$empty_conf"
  echo "  Raw: $empty_raw"
  FAIL=$((FAIL+1))
fi

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " T-2: KST helper UTC+9 산술 + TZ-invariance (INV-2) + non-deprecated API"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# TZ-invariance: 동일 epoch 를 TZ 3환경에서 실행 → 3 출력 동일 (anti-`TZ=Asia/Seoul` 회귀, INV-2).
run_tz_invariance() {
  local name="$1" epoch="$2"
  local e1=0 e2=0 e3=0 o_utc o_ny o_seoul
  o_utc=$(TZ=UTC python3 "$KST" --epoch "$epoch" 2>/dev/null) || e1=$?
  o_ny=$(TZ=America/New_York python3 "$KST" --epoch "$epoch" 2>/dev/null) || e2=$?
  o_seoul=$(TZ=Asia/Seoul python3 "$KST" --epoch "$epoch" 2>/dev/null) || e3=$?
  if [ "$e1" -eq 0 ] && [ "$e2" -eq 0 ] && [ "$e3" -eq 0 ] \
     && [ -n "$o_utc" ] && [ "$o_utc" = "$o_ny" ] && [ "$o_ny" = "$o_seoul" ]; then
    echo "✓ PASS: $name (epoch=$epoch, UTC=NY=Seoul='$o_utc') — INV-2 tz-invariance"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  utc='$o_utc'(e$e1) ny='$o_ny'(e$e2) seoul='$o_seoul'(e$e3) — INV-2 위반 (TZ-dependent 산술 회귀)"
    FAIL=$((FAIL+1))
  fi
}

# T2-1/T2-2: TZ-invariance (연/월/일 rollover epoch + epoch 0) — 3환경 동일 산출.
run_tz_invariance "T2-1: TZ-invariance (2024-12-31T20:00Z rollover)" 1735675200
run_tz_invariance "T2-2: TZ-invariance (epoch 0)" 0

# 정확성 (hand-verified fixtures) — distinct-marker = 정확 stamp 문자열.
run_kst_exact() {
  local name="$1" epoch="$2" expected="$3" description="$4"
  local exit_code=0 out
  out=$(python3 "$KST" --epoch "$epoch" 2>/dev/null) || exit_code=$?
  if [ "$exit_code" -eq 0 ] && [ "$out" = "$expected" ]; then
    echo "✓ PASS: $name (epoch=$epoch → '$out') — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected '$expected' exit 0, got '$out' exit=$exit_code"
    FAIL=$((FAIL+1))
  fi
}

# T2-3: epoch 0 = 1970-01-01T00:00Z, +9h → 01/01 09:00.
run_kst_exact "T2-3: epoch 0 → 01/01 09:00" 0 "01/01 09:00" "1970-01-01T00:00Z +9h = 09:00 (동일자)"
# T2-4: epoch 72000 = 1970-01-01T20:00Z, +9h → 01/02 05:00 (일자 rollover).
run_kst_exact "T2-4: epoch 72000 → 01/02 05:00 (일자 rollover)" 72000 "01/02 05:00" "1970-01-01T20:00Z +9h = 다음날 05:00"
# T2-5: epoch 1735675200 = 2024-12-31T20:00Z, +9h → 01/01 05:00 (연/월/일 rollover).
run_kst_exact "T2-5: epoch 1735675200 → 01/01 05:00 (연/월/일 rollover)" 1735675200 "01/01 05:00" "2024-12-31T20:00Z +9h = 2025-01-01T05:00 KST"

# non-deprecated API + stderr 격리: `-W error` 로 DeprecationWarning→error 승격.
#   utcnow()(deprecated) 사용이면 warning→error→exit≠0 & stderr 비어있지 않음 → RED.
#   now(timezone.utc)/fromtimestamp(epoch,tz=utc) 사용이면 warning 0 → exit 0 & stderr 빈.
run_kst_no_deprecation() {
  local name="$1"
  local exit_code=0 out errfile err_content
  errfile=$(mktemp)
  # shellcheck disable=SC2064
  trap "rm -f '$errfile'" RETURN
  out=$(python3 -W error "$KST" --epoch 0 2>"$errfile") || exit_code=$?
  err_content=$(cat "$errfile")
  if [ "$exit_code" -eq 0 ] && [ -z "$err_content" ] && [ "$out" = "01/01 09:00" ]; then
    echo "✓ PASS: $name (exit 0, stderr 빈, out '$out') — non-deprecated API (utcnow→DeprecationWarning 회귀 방지)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit 0 ∧ stderr 빈 ∧ out '01/01 09:00', got exit=$exit_code out='$out'"
    echo "  stderr: $err_content"
    FAIL=$((FAIL+1))
  fi
}
run_kst_no_deprecation "T2-6: non-deprecated API (-W error, stderr 격리)"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " T-4: lint-safe example regression (INV-3) — 기존 check_kst_timestamp.py 무편집 import"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# T4-1: 컴팩트 `MM/DD HH:MM` 예시는 KST_TS_RE 에 미매칭 (문서 예시 자유 배치, lint-inert).
#   distinct-marker = 'T4-compact-OK' (assert 통과 시에만 방출).
t4a_exit=0
# lib dir 를 argv[1] 로 전달 (script-arg 는 MSYS 가 POSIX→Windows 경로 변환 — sys.path 문자열
# 리터럴은 미변환이라 native Windows Python 에서 import 실패, Linux CI 는 무영향. cross-platform 안전).
t4a_out=$(python3 -c "import sys; sys.path.insert(0, sys.argv[1]); import check_kst_timestamp as k; assert k.KST_TS_RE.search('[ArchitectAgent] 07/05 14:30 - x') is None; print('T4-compact-OK')" "$REPO_ROOT/scripts/lib" 2>/dev/null) || t4a_exit=$?
if [ "$t4a_exit" -eq 0 ] && [ "$t4a_out" = "T4-compact-OK" ]; then
  echo "✓ PASS: T4-1: 컴팩트 MM/DD HH:MM 미매칭 (lint-inert, INV-3) — $t4a_out"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T4-1: 컴팩트 MM/DD HH:MM 이 KST_TS_RE 에 매칭됨 (INV-3 위반)"
  echo "  exit=$t4a_exit out='$t4a_out'"
  FAIL=$((FAIL+1))
fi

# T4-2: 대조 sanity — full-zoned 비-KST(`-07:00`)는 KST_TS_RE 에 매칭됨.
#   컴팩트가 특별히 면제(비매칭)됨을 대조적으로 입증 (regex 자체 sanity).
t4b_exit=0
t4b_out=$(python3 -c "import sys; sys.path.insert(0, sys.argv[1]); import check_kst_timestamp as k; assert k.KST_TS_RE.search('2026-07-05T14:30:00-07:00') is not None; print('T4-zoned-OK')" "$REPO_ROOT/scripts/lib" 2>/dev/null) || t4b_exit=$?
if [ "$t4b_exit" -eq 0 ] && [ "$t4b_out" = "T4-zoned-OK" ]; then
  echo "✓ PASS: T4-2: full-zoned 비-KST(-07:00) 매칭 (대조 sanity, INV-3 대조군) — $t4b_out"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T4-2: full-zoned 비-KST 가 KST_TS_RE 에 미매칭 (regex sanity 실패 — 컴팩트 면제 대조 무효)"
  echo "  exit=$t4b_exit out='$t4b_out'"
  FAIL=$((FAIL+1))
fi

# ═════════════════════════════════════════════════════════════════════════════
# CFP-2574 구현리뷰 FIX-1 (QADev, same-lane first FIX) — 런타임 경로 2개 커버리지 0 봉인:
#   Block A = T-3 hook↔detector 통합 seam (§7.3 계약 축인데 §8 이 amendment 없이 drop →
#             신규 hook 통합코드 auto-커버 0 이던 것 봉인. hook 을 실 JSON stdin 으로 fork).
#   Block B = no-epoch production smoke (kst_render_stamp 실사용 default 분기
#             now(timezone.utc) 를 전 케이스가 --epoch 주입으로 미실행 → 봉인).
#   Block C = empty-content nonconformant (dev RE_PREFIX `- \S` tighten 정합, P3-b).
# distinct-marker 규율 상속: 각 fork 판정 = exit code 단독 아닌 도메인 고유 stdout/stderr
#   sentinel 병행 assert (interpreter/shell 표준 exit 우연일치 silent false-positive 차단).
# ═════════════════════════════════════════════════════════════════════════════

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " T-3: hook↔detector 통합 seam (PreToolUse(Agent) 실 JSON payload fork) — §7.3 계약"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

HOOK="$REPO_ROOT/hooks/pretooluse-agent-spawn-gate"

# run_hook_case: hook 을 JSON stdin payload 로 실 fork. assert 3축 (CFP-2587 injection-era) —
#   (a) INV-1: 항상 exit 0 (spawn 무차단, deny 비활성).
#   (b) injection: stdout `updatedInput` 존재 여부가 expect_inject 와 일치 (nonconformant→주입,
#       conformant/empty→idempotent skip). 구 detect-only stderr WARN 은 injection 으로 supersede
#       (ADR-143 Amendment 1) — 더 이상 'nonconformant' WARN 발화 안 함.
#   (c) §7.3 LOAD-BEARING: stdout `additionalContext`(story-transition-autonomy) 는 injected
#       skip 여부와 무관하게 항상 present — reminder 회귀 가드(distinct-marker).
# CLAUDE_PLUGIN_ROOT="$REPO_ROOT" 주입 → inject/reminder helper 경로가 cwd 무관 resolve.
run_hook_case() {
  local name="$1" payload="$2" expect_inject="$3" description="$4"
  local exit_code=0 out errfile inj_present ctx_present
  errfile="$(mktemp)"
  out="$(printf '%s' "$payload" | CLAUDE_PLUGIN_ROOT="$REPO_ROOT" bash "$HOOK" 2>"$errfile")" || exit_code=$?
  rm -f "$errfile"
  # (b) injection: stdout 에 updatedInput 방출 여부
  if printf '%s' "$out" | grep -q '"updatedInput"'; then
    inj_present="yes"
  else
    inj_present="no"
  fi
  # (c) §7.3 LOAD-BEARING distinct-marker: additionalContext reminder 항상 present
  if printf '%s' "$out" | grep -q 'story-transition-autonomy'; then
    ctx_present="yes"
  else
    ctx_present="no"
  fi
  if [ "$exit_code" -eq 0 ] && [ "$inj_present" = "$expect_inject" ] && [ "$ctx_present" = "yes" ]; then
    echo "✓ PASS: $name (exit 0, updatedInput=$inj_present, additionalContext=yes) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit 0 ∧ updatedInput=$expect_inject ∧ additionalContext=yes, got exit=$exit_code updatedInput=$inj_present ctx=$ctx_present"
    echo "  stdout: $out"
    FAIL=$((FAIL+1))
  fi
}

# T3-conformant: 이미 정식 프리픽스 → idempotent skip(updatedInput 無) ∧ reminder present, exit 0.
run_hook_case "T3-conformant: 정식 프리픽스 (idempotent skip)" \
  '{"tool_input":{"subagent_type":"ArchitectAgent","description":"[ArchitectAgent] 07/05 14:30 - Change Plan","prompt":"x"}}' \
  "no" "conformant description → build_injected_description=None → 재주입 skip(updatedInput 無), reminder 여전히 present, exit 0 (AC-11/§7.3)"

# T3-nonconformant: 프리픽스 위반 → mechanical injection(updatedInput 방출) ∧ reminder present, exit 0.
run_hook_case "T3-nonconformant: 프리픽스 위반 (기계 주입)" \
  '{"tool_input":{"subagent_type":"ArchitectAgent","description":"bad desc","prompt":"x"}}' \
  "yes" "nonconformant description → ADR-143 Amendment 1 mechanical injection(updatedInput 프리픽스 주입) + reminder 병합, exit 0 (INV-1)"

# T3-empty: 빈 description → 주입 skip(빈 필드=위반 아님, AC-10) ∧ reminder present, exit 0.
run_hook_case "T3-empty: 빈 description (skip)" \
  '{"tool_input":{"subagent_type":"ArchitectAgent","description":"","prompt":"x"}}' \
  "no" "빈 description → build_injected_description=None(빈 필드 skip) → updatedInput 無, reminder present, exit 0 (INV-1)"

# T3-empty-prompt: prompt 키 부재 → injection(subagent_type present + nonconformant desc) ∧ reminder 무조건 (F1/§7.3 회귀가드).
#   run_hook_case 는 additionalContext=yes 를 항상 요구하므로 빈 prompt 시 reminder 소실(구 early-exit 회귀)이면 FAIL.
run_hook_case "T3-empty-prompt: prompt 키 부재 (§7.3 reminder 무조건)" \
  '{"tool_input":{"subagent_type":"ArchitectAgent","description":"bad desc"}}' \
  "yes" "prompt 키 부재여도 injection(subagent_type present) + reminder 무조건 emit (F1/§7.3 회귀가드)"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " B: no-epoch production smoke (kst_render_stamp 실사용 default 분기 now(timezone.utc))"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# distinct-marker = RENDER_RE 매칭(도메인 stamp 형상 sentinel) — 단순 exit 아님.
RENDER_RE='^[0-9][0-9]/[0-9][0-9] [0-9][0-9]:[0-9][0-9]$'

# B-1: python SSOT 무 --epoch → now(timezone.utc) default 분기 실행 (전 케이스 --epoch 주입으로 미커버였던 경로).
b1_exit=0
b1_out="$(python3 "$KST" 2>/dev/null)" || b1_exit=$?
if [ "$b1_exit" -eq 0 ] && printf '%s' "$b1_out" | grep -Eq "$RENDER_RE"; then
  echo "✓ PASS: B-1: python SSOT 무-epoch (exit 0, out '$b1_out' RENDER_RE 매칭) — now(timezone.utc) default 분기 실행"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: B-1: python SSOT 무-epoch"
  echo "  Expected exit 0 ∧ out RENDER_RE(MM/DD HH:MM) 매칭, got exit=$b1_exit out='$b1_out'"
  FAIL=$((FAIL+1))
fi

# B-2: bash wrapper 무인자 → GNU date primary(or python fallback), 동일 RENDER_RE (production wrapper 경로).
b2_exit=0
b2_out="$(bash "$REPO_ROOT/scripts/kst-render-stamp.sh" 2>/dev/null)" || b2_exit=$?
if [ "$b2_exit" -eq 0 ] && printf '%s' "$b2_out" | grep -Eq "$RENDER_RE"; then
  echo "✓ PASS: B-2: bash wrapper 무인자 (exit 0, out '$b2_out' RENDER_RE 매칭) — production wrapper 경로 실행"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: B-2: bash wrapper 무인자"
  echo "  Expected exit 0 ∧ out RENDER_RE 매칭, got exit=$b2_exit out='$b2_out'"
  FAIL=$((FAIL+1))
fi

# B-3: python SSOT 무 --epoch + `-W error` → now(timezone.utc) 는 non-deprecated 이라 무경고.
#   utcnow() 회귀 시 DeprecationWarning→error→exit≠0 & stderr 비어있지않음 → RED (discriminating).
b3_exit=0
b3_errfile="$(mktemp)"
b3_out="$(python3 -W error "$KST" 2>"$b3_errfile")" || b3_exit=$?
b3_err="$(cat "$b3_errfile")"
rm -f "$b3_errfile"
if [ "$b3_exit" -eq 0 ] && [ -z "$b3_err" ] && printf '%s' "$b3_out" | grep -Eq "$RENDER_RE"; then
  echo "✓ PASS: B-3: 무-epoch -W error (exit 0, stderr 빈, out '$b3_out' 매칭) — now(timezone.utc) 무경고(utcnow 회귀 방지)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: B-3: 무-epoch -W error"
  echo "  Expected exit 0 ∧ stderr 빈 ∧ out RENDER_RE 매칭, got exit=$b3_exit out='$b3_out'"
  echo "  stderr: $b3_err"
  FAIL=$((FAIL+1))
fi

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " C: empty-content nonconformant (RE_PREFIX '- \\S' tighten 정합, P3-b)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# run_prefix_full_case: detector JSON 의 conformant + empty 두 필드 + exit 0 동시 assert (T-1 detector 호출 재사용).
run_prefix_full_case() {
  local name="$1" fixture="$2" exp_conf="$3" exp_empty="$4" description="$5"
  local exit_code=0 raw conf empty
  raw="$(printf '%s' "$fixture" | python3 "$PREFIX" --description-stdin 2>/dev/null)" || exit_code=$?
  conf="$(printf '%s' "$raw" | python3 -c "import json,sys;print(json.load(sys.stdin)['description_prefix_conformant'])" 2>/dev/null)" || conf="PARSE_ERR"
  empty="$(printf '%s' "$raw" | python3 -c "import json,sys;print(json.load(sys.stdin)['empty'])" 2>/dev/null)" || empty="PARSE_ERR"
  if [ "$exit_code" -eq 0 ] && [ "$conf" = "$exp_conf" ] && [ "$empty" = "$exp_empty" ]; then
    echo "✓ PASS: $name (exit 0, conformant=$conf empty=$empty) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit 0 ∧ conformant=$exp_conf ∧ empty=$exp_empty, got exit=$exit_code conformant=$conf empty=$empty"
    echo "  Raw: $raw"
    FAIL=$((FAIL+1))
  fi
}

# C-1: 프리픽스 존재하나 내용 빈(' - ' 뒤 non-\S) → conformant=false ∧ empty=false ∧ exit 0.
#   dev RE_PREFIX `- \S` tighten 정합. (tighten 전 regex 는 empty-content 를 conformant 판정 → 일시 RED,
#   dev 착지 후 GREEN. 현 worktree RE_PREFIX = '...- \S' → GREEN 예상.)
run_prefix_full_case "C-1: empty-content nonconformant" \
  '[ArchitectAgent] 07/05 14:30 - ' \
  "False" "False" "프리픽스 존재+내용 빈 → '- \\S' 미매칭 → conformant=false, empty=false (P3-b tighten)"

# C-2: 빈 필드(프리픽스 자체 부재, strip='') → empty=true ∧ conformant=true (세만틱 보존 대조 — T1-8 동형 명시적 대조군).
run_prefix_full_case "C-2: 빈 필드 세만틱 보존 대조" \
  '' \
  "True" "True" "빈 description(strip='') → empty=true, conformant=true (leaf 빈 필드는 위반 아님, AC-10)"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " T-7: inject-pipeline TZ-invariance (CFP-2587 AC-13) — kst_render_stamp → --inject 동일 결과"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# T-7 (AC-13): 동일 --epoch 을 3 TZ(UTC/NY/Seoul)에서 kst_render_stamp → --inject 파이프라인 실행 →
#   updatedInput.description 3개가 genuine 기대값(subject+stamp+original)과 정확 일치.
#   .sh T-2(위)는 stamp 자체의 TZ-invariance 만; T-7 은 그 stamp 를 먹인 END-TO-END inject 결과의
#   TZ-invariance 를 봉인 (packet §8 "reuse its T-2 TZ-invariance for T-7").
#   distinct-marker = 기대값 exact 비교 (PARSE_ERR/빈값/TZ-drift 우연일치 차단 — 단순 3-way 동일 아님).
#   kst_render_stamp 은 UTC+9 고정 산술(TZ env 무의존) → stamp 동일 → inject 결과 동일 (Windows 포함).
_inject_desc() {
  # $1=TZ $2=stamp → updatedInput.description (json.load 실패 시 PARSE_ERR)
  local payload='{"tool_name":"Bash","agent_type":"general-purpose","tool_input":{"command":"echo hi","description":"nonconformant desc"}}'
  printf '%s' "$payload" | TZ="$1" python3 "$PREFIX" --inject --subject general-purpose --kst-stamp "$2" 2>/dev/null \
    | python3 -c "import json,sys;print(json.load(sys.stdin)['hookSpecificOutput']['updatedInput']['description'])" 2>/dev/null
}

run_inject_tz_invariance() {
  local name="$1" epoch="$2"
  local s_utc s_ny s_seoul d_utc d_ny d_seoul expected
  s_utc=$(TZ=UTC python3 "$KST" --epoch "$epoch" 2>/dev/null) || s_utc=""
  s_ny=$(TZ=America/New_York python3 "$KST" --epoch "$epoch" 2>/dev/null) || s_ny=""
  s_seoul=$(TZ=Asia/Seoul python3 "$KST" --epoch "$epoch" 2>/dev/null) || s_seoul=""
  d_utc=$(_inject_desc "UTC" "$s_utc") || d_utc="PARSE_ERR"
  d_ny=$(_inject_desc "America/New_York" "$s_ny") || d_ny="PARSE_ERR"
  d_seoul=$(_inject_desc "Asia/Seoul" "$s_seoul") || d_seoul="PARSE_ERR"
  expected="[general-purpose] ${s_utc} - nonconformant desc"
  if [ -n "$s_utc" ] && [ "$s_utc" = "$s_ny" ] && [ "$s_ny" = "$s_seoul" ] \
     && [ "$d_utc" = "$expected" ] && [ "$d_ny" = "$expected" ] && [ "$d_seoul" = "$expected" ]; then
    echo "✓ PASS: $name (epoch=$epoch, stamp='$s_utc', desc 3-TZ 동일='$expected') — inject-pipeline TZ-invariance (AC-13)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  stamps utc='$s_utc' ny='$s_ny' seoul='$s_seoul'"
    echo "  desc   utc='$d_utc' ny='$d_ny' seoul='$d_seoul' expected='$expected'"
    FAIL=$((FAIL+1))
  fi
}

run_inject_tz_invariance "T7-1: inject-pipeline TZ-invariance (2024-12-31T20:00Z rollover)" 1735675200
run_inject_tz_invariance "T7-2: inject-pipeline TZ-invariance (epoch 0)" 0

# ─────────────────────────────────────────────────────────────────────────────
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "✓ All $PASS cases pass — T-1(INV-1 exit-0-always) + T-2(INV-2 tz-invariance) + T-4(INV-3 lint-inert) + T-3(hook↔detector seam) + T-7(inject-pipeline TZ-invariance AC-13) + B(no-epoch production smoke) + C(empty-content nonconformant) 입증"
  exit 0
else
  echo "✗ $FAIL case(s) failed"
  exit 1
fi
