#!/usr/bin/env bash
# tests/scripts/test-check-doc-section-8-8.sh
# CFP-2605 (Epic CFP-2602 G4) Phase 2 — Discriminating self-test for §8.8 doc-section lint
# (ADR-146 §결정 5). L3 execution-liveness: mutation 을 실제 kill (형식 green 금지).
#
# QADeveloperAgent 가 change-plan §8.9 authoritative matrix + §8.2 fixtures + §8.4 mutation A/B/C
# 를 입력으로 작성. 검증 대상 = scripts/lib/check_doc_section_schema.py check_section_8_8()
# (canonical = ADR-146 §결정 5 pinned interface, DeveloperAgent-CORE 가 verbatim 삽입).
# 선례 = tests/scripts/test-check-doc-section-8-7.sh (verbatim-homolog 구조).
#
# check_section_8_8() 동작 (canonical, 검증 기준):
#  - §8.8 헤딩 부재 → 무검사(return []). §8.6/§8.7 gap 무관(§8.8 헤딩만 트리거).
#  - §8.8 헤딩 존재 + §8.8.0 헤딩 부재 → fail.
#  - §8.8.0 표 4 기법 행(fuzz/property/load/concurrency) status(DO|N/A) 미파싱(행 누락) → fail.
#  - g2_boundary_check token 이 §8.8 region 에 부재 → fail (AC-7).
#  - do_count>=1 시 per-technique:
#      · DO → §8.8.N 산출물 계약 필수 필드(fuzz 6 / property 4 / load 4 / concurrency 5) 누락 → fail (AC-3/4).
#             load=DO 는 §8.8.3 본문에 §8.3 Perf Baseline token 필수 (AC-6).
#      · N/A(mixed) → §8.8.N per-technique substantive infeasibility_reason(30자 minimum) 부재 → fail (AC-2 hollow-gap).
#  - na_count==4(aggregate) → §8.8.x 헤딩 + substantive reason(30자 minimum) 필수.
#  ★ 정직 천장(ADR-146 결정8): 게이트는 applicability 표·계약 필드 presence/구조까지만. 검출력/완결성/
#    사유타당성/g2-준수는 강제하지 않음(review·advisory·G3 defense-in-depth) — TC9 가 over-reach 부재 실증.
#
# ── CWD 의무 (CFP-2449 gotcha) ────────────────────────────────────────────────
#  check_doc_section_schema.py 는 CWD-상대 스캔(`Path("docs/change-plans").rglob`). argv 무시.
#  → 격리 임시 dir 에 docs/change-plans/cfp-9999-fixture.md 만들고 그 dir 를 CWD 로 python3 호출.
#  cfp 번호 = 9999 (LEGACY_CHANGE_PLAN_CFPS 회피). fixture 는 §1-§11 skeleton 전부 포함 —
#  §8.8 외 사유(필수 섹션 누락 등) fail 0 격리.
#
# ── §8.9 authoritative matrix (matrix ⊇ §8.2 fixtures 불변식) ─────────────────
#  TC1  fuzz-DO-6필드(+3 N/A substantive) → exit 0  ↔  TC2 fuzz 필드1 누락 → exit 1 (discriminating)
#  TC3  aggregate N/A vague(<30자) → exit 1          ↔  TC3ok substantive → exit 0 (discriminating)
#  TC4  (F-ROW-OMIT) concurrency 행 누락 → exit 1 (침묵 skip 반증 AC-1a/9)
#  TC5  (F-LOAD-NO-PERF) load=DO 인데 §8.3 token 부재 → exit 1 (AC-6)
#  TC6  (F-NO-G2-CHECK) g2_boundary_check token 부재 → exit 1 (AC-7)
#  TC7  (F-8.6-GAP) §8.5(+§8.5.4) → §8.8 gap(§8.6 부재) → §8.8 외 사유 fail 0 → exit 0 (false-positive 0)
#  TC8  (F-MIXED-NA) DO 3(유효) + concurrency N/A vague → exit 1 (AC-2 hollow-gap discriminating)
#  TC9  (F-CEILING-OVERREACH) 4 DO 유효 + g2 + §8.8.5 천장 → exit 0 (over-reach 부재) + ceiling honesty 개시 grep
#  TC-4b/4c/4d  property/load/concurrency per-technique DO 필드(1개 누락 → exit 1 ↔ 완전 → exit 0)
#  sibling-guard  check_section_8_8() 부재/미배선 → 명시 FAIL(silent skip 금지)
#
# ── Mutation A/B/C 실 RED 증명 (execution-liveness L3) ─────────────────────────
#  canonical 3개 check 에 sentinel 주석: MUT-A-DO-FIELDS / MUT-B-G2-TOKEN / MUT-C-MIXED-NA.
#  각 mutation = $LINT_PY 복사 → sentinel 라인을 동일 들여쓰기 `pass` 로 sed 무력화 → kill-fixture 실행.
#  KILL 판정: original(kill-fixture)=exit 1 AND mutated(kill-fixture)=exit 0 → original≠mutated → KILLED.
#  mutated 가 여전히 exit 1 = check hollow → self-test FAIL(형식 green 차단).
#
# ── 사전 의존 (sibling DeveloperAgent-CORE) ───────────────────────────────────
#  check_section_8_8() 미삽입/미배선 시 → 명시 FAIL 로 sibling-dependency 노출(silent skip 금지).
#  (Windows: 필요 시 MSYS_NO_PATHCONV=1. bats 불필요 — 순수 bash. python 미노출 시 즉시 FAIL.)
#  CHECK_DOC_LINT_PY env override = mutation copy·격리 검증용(default = repo 실 lint).
#
# Exit code: 0 = all discriminating cases pass, 1 = any fail

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LINT_PY="${CHECK_DOC_LINT_PY:-$REPO_ROOT/scripts/lib/check_doc_section_schema.py}"

TALLY=$(mktemp)
trap 'rm -f "$TALLY"' EXIT
tally_pass() { echo "P" >> "$TALLY"; }
tally_fail() { echo "F" >> "$TALLY"; }

PY="python3"
command -v python3 >/dev/null 2>&1 || PY="python"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "✗ FAIL: python3/python 부재 — lint 실행 불가"
  exit 1
fi

# ── sibling-dependency guard (§8.7 self-test L58-61 동형) ──
if [ ! -f "$LINT_PY" ]; then
  echo "✗ FAIL: check_doc_section_schema.py 부재 ($LINT_PY)"
  exit 1
fi
if ! grep -q 'def check_section_8_8' "$LINT_PY"; then
  echo "✗ FAIL: check_doc_section_schema.py 에 check_section_8_8() 부재 (DeveloperAgent-CORE 미삽입 — sibling-dependent, 함수 미삽입, PL 재실행 필요)"
  exit 1
fi
# 추가 guard: main() 미배선(호출 부재) 검출 — 함수만 있고 호출 없으면 §8.8 검사가 실행되지 않아
# 모든 fixture exit 0 → 전 TC false-pass. def 1줄 + main 호출 1줄 => 최소 2 라인 매칭 기대.
if [ "$(grep -c 'check_section_8_8' "$LINT_PY")" -lt 2 ]; then
  echo "✗ FAIL: check_section_8_8() 가 main() 에 미배선 (호출 부재 — 함수 dead-code). PL 재실행 필요"
  exit 1
fi

# ═════════════════════════════════════════════════════════════════════════════
# change-plan §1-§11 skeleton (§8.8 외 사유 fail 0 격리). §8 본문 = per-fixture §8.8.
# ═════════════════════════════════════════════════════════════════════════════
emit_skeleton_head() {
  cat <<'EOF'
### §1. 목적
fixture
### §2. 현재 구조
fixture
### §3. 도입할 설계
fixture
### §4. API 계약
fixture
### §7. 보안
fixture
### §8. Test Contract
EOF
}
emit_skeleton_tail() {
  cat <<'EOF'
### §10. FIX Ledger
fixture
### §11. 데이터 마이그레이션
fixture
EOF
}

SEC88_HEADER="#### §8.8 동적 테스트 로스터 (CONDITIONAL — CFP-2605 / ADR-146)"

# emit_88_table <fuzz> <property> <load> <concurrency> <g2|nog2>
#   g2 → g2_boundary_check token 포함(AC-7 충족). nog2 → 3번째 컬럼명·셀에서 token 제거.
emit_88_table() {
  local fs="$1" ps="$2" ls="$3" cs="$4" g2="${5:-g2}"
  echo "##### §8.8.0 Applicability decision (필수)"
  if [ "$g2" = "g2" ]; then
    echo "| technique | applicability_status (DO/N/A) | g2_boundary_check |"
    echo "|---|:-:|---|"
    echo "| fuzz | $fs | g2_boundary_check: soak/restart/replay 미신설 확인 |"
    echo "| property | $ps | g2_boundary_check ok |"
    echo "| load | $ls | g2_boundary_check ok |"
    echo "| concurrency | $cs | g2_boundary_check ok |"
  else
    echo "| technique | applicability_status (DO/N/A) | boundary_note |"
    echo "|---|:-:|---|"
    echo "| fuzz | $fs | boundary reviewed ok |"
    echo "| property | $ps | boundary reviewed ok |"
    echo "| load | $ls | boundary reviewed ok |"
    echo "| concurrency | $cs | boundary reviewed ok |"
  fi
}

# emit_88_fuzz_do [omit-field]  — fuzz DO 산출물 6 필드 (omit 시 해당 필드 라인 제거)
emit_88_fuzz_do() {
  local omit="${1:-}"
  echo "##### §8.8.1 fuzz (DO)"
  [ "$omit" = "target" ]           || echo "- target: parser_fn"
  [ "$omit" = "input_surface" ]    || echo "- input_surface: raw bytes"
  [ "$omit" = "oracle" ]           || echo "- oracle: panic/hang"
  [ "$omit" = "seed_or_corpus" ]   || echo "- seed_or_corpus: corpus dir"
  [ "$omit" = "execution_budget" ] || echo "- execution_budget: 100000 회"
  [ "$omit" = "pass_condition" ]   || echo "- pass_condition: crash 0"
}

# emit_88_property_do [omit-field]  — property DO 산출물 4 필드
emit_88_property_do() {
  local omit="${1:-}"
  echo "##### §8.8.2 property (DO)"
  [ "$omit" = "property_definition" ] || echo "- property_definition: parse then serialize identity"
  [ "$omit" = "input_generator" ]     || echo "- input_generator: hypothesis 전략"
  [ "$omit" = "sample_budget" ]       || echo "- sample_budget: 1000 examples"
  [ "$omit" = "pass_condition" ]      || echo "- pass_condition: falsifying 0"
}

# emit_88_load_do [omit-field] [perf|noperf]  — load DO 산출물 4 필드. perf 시 §8.3 token 포함(AC-6).
emit_88_load_do() {
  local omit="${1:-}" perf="${2:-perf}"
  echo "##### §8.8.3 load (DO)"
  [ "$omit" = "load_profile" ] || echo "- load_profile: ramp 100 to 1000 rps"
  [ "$omit" = "metrics" ]      || echo "- metrics: p95 throughput error-rate"
  if [ "$omit" != "threshold_or_baseline_ref" ]; then
    if [ "$perf" = "perf" ]; then
      echo "- threshold_or_baseline_ref: §8.3 Perf Baseline 대비 saturation"
    else
      echo "- threshold_or_baseline_ref: baseline 대비 saturation (perf token 제거)"
    fi
  fi
  [ "$omit" = "duration" ]     || echo "- duration: 10m"
}

# emit_88_concurrency_do [omit-field]  — concurrency DO 산출물 5 필드
emit_88_concurrency_do() {
  local omit="${1:-}"
  echo "##### §8.8.4 concurrency (DO)"
  [ "$omit" = "shared_state" ]    || echo "- shared_state: in-memory ledger map"
  [ "$omit" = "execution_model" ] || echo "- execution_model: N goroutine 경합"
  [ "$omit" = "worker_count" ]    || echo "- worker_count: 64"
  [ "$omit" = "oracle" ]          || echo "- oracle: 잔고 보존 invariant"
  [ "$omit" = "duration" ]        || echo "- duration: 5m"
}

# emit_88_na_sub <sub> <technique> <substantive|vague>  — mixed-case per-technique N/A 사유
emit_88_na_sub() {
  local sub="$1" tech="$2" kind="$3"
  echo "##### §$sub $tech (N/A)"
  if [ "$kind" = "vague" ]; then
    echo "N/A — 짧음"
  else
    echo "N/A — $tech 미적용: 공유 상태 없는 순수 단일 함수 경로라 해당 기법 대상 표면이 구조적으로 부재해 자연 N/A 상태를 유지함"
  fi
}

# emit_88_x_na <substantive|vague>  — aggregate 4 N/A 명시
emit_88_x_na() {
  echo "##### §8.8.x N/A 명시 (4 기법 모두 미적용)"
  if [ "$1" = "vague" ]; then
    echo "N/A — 짧음"
  else
    echo "N/A — 본 Story 는 순수 파서 단일 함수만 수정해 fuzz property load concurrency 4 기법 대상 표면이 모두 부재하고 실행 가능 런타임 경로가 없어 동적 로스터 자연 면제. 검증 채널: 단위 테스트"
  fi
}

# emit_88_5_ceiling  — 정직 천장(§8.8.5). 4 잔여(검출력/완결성/사유타당성/g2!=준수) 개시, "완전 봉인" hard-claim 부재.
emit_88_5_ceiling() {
  echo "##### §8.8.5 정직 천장"
  echo "- (i) 검출력 = G3 discriminating 위임 (ii) 완결성 = review·advisory 보강 (iii) 사유타당성 = review 판정 (iv) g2_boundary_check presence != 준수 (게이트 강제 아님)"
}

# run_case <body_fn> <expected_exit> <name> <desc> [lint_py]
run_case() {
  local body_fn="$1" expected="$2" name="$3" desc="$4"
  local lint="${5:-$LINT_PY}"
  local T; T=$(mktemp -d)
  mkdir -p "$T/docs/change-plans"
  "$body_fn" > "$T/docs/change-plans/cfp-9999-fixture.md"
  local out ec=0
  out=$( cd "$T" && "$PY" "$lint" 2>&1 ) || ec=$?
  if [ "$ec" = "$expected" ]; then
    echo "✓ PASS: $name (exit $ec) — $desc" >&2
    echo "P" >> "$TALLY"
  else
    {
      echo "✗ FAIL: $name"
      echo "  Expected exit $expected, got $ec"
      echo "  Description: $desc"
      echo "  Lint output: $out"
    } >&2
    echo "F" >> "$TALLY"
  fi
  rm -rf "$T"
  echo "$ec"
}

# assert_discriminating <ec_a> <ec_b> <label>
assert_discriminating() {
  local a="$1" b="$2" label="$3"
  if [ "$a" != "$b" ]; then
    echo "✓ PASS: ANTI-THEATER discriminating — $label (exit $a ≠ $b)" >&2
    tally_pass
  else
    echo "✗ FAIL: ANTI-THEATER — $label (exit $a == $b) = non-discriminating hollow" >&2
    tally_fail
  fi
}

# ═════════════════════════════════════════════════════════════════════════════
# TC1 — fuzz-DO 6필드 완전 (+ 3 N/A substantive) → exit 0
# ═════════════════════════════════════════════════════════════════════════════
tc1_body() {
  emit_skeleton_head
  echo "$SEC88_HEADER"
  emit_88_table DO N/A N/A N/A g2
  emit_88_fuzz_do ""
  emit_88_na_sub 8.8.2 property substantive
  emit_88_na_sub 8.8.3 load substantive
  emit_88_na_sub 8.8.4 concurrency substantive
  emit_88_5_ceiling
  emit_skeleton_tail
}
EC_TC1=$(run_case tc1_body 0 "TC1-fuzzDO-6field-PASS" "fuzz DO 6필드 완전 + 3 N/A substantive → exit 0" | tail -1)

# ═════════════════════════════════════════════════════════════════════════════
# TC2 — fuzz-DO pass_condition 누락 → exit 1 (Mutation-A kill-fixture)
# ═════════════════════════════════════════════════════════════════════════════
tc2_body() {
  emit_skeleton_head
  echo "$SEC88_HEADER"
  emit_88_table DO N/A N/A N/A g2
  emit_88_fuzz_do "pass_condition"
  emit_88_na_sub 8.8.2 property substantive
  emit_88_na_sub 8.8.3 load substantive
  emit_88_na_sub 8.8.4 concurrency substantive
  emit_88_5_ceiling
  emit_skeleton_tail
}
EC_TC2=$(run_case tc2_body 1 "TC2-fuzzDO-missing-field-FAIL" "fuzz DO pass_condition 누락 → exit 1 (AC-3/4)" | tail -1)
assert_discriminating "$EC_TC1" "$EC_TC2" "TC1(6필드)=$EC_TC1 vs TC2(필드누락)"

# ═════════════════════════════════════════════════════════════════════════════
# TC3 — aggregate 4 N/A vague reason → exit 1  ↔  TC3ok substantive → exit 0
# ═════════════════════════════════════════════════════════════════════════════
tc3_body() {
  emit_skeleton_head
  echo "$SEC88_HEADER"
  emit_88_table N/A N/A N/A N/A g2
  emit_88_x_na vague
  emit_skeleton_tail
}
EC_TC3=$(run_case tc3_body 1 "TC3-agg-NA-vague-FAIL" "aggregate 4 N/A + reason 30자 미만(vague) → exit 1" | tail -1)

tc3ok_body() {
  emit_skeleton_head
  echo "$SEC88_HEADER"
  emit_88_table N/A N/A N/A N/A g2
  emit_88_x_na substantive
  emit_skeleton_tail
}
EC_TC3OK=$(run_case tc3ok_body 0 "TC3ok-agg-NA-substantive-PASS" "aggregate 4 N/A + substantive 30자+ → exit 0 (over-strict 검출)" | tail -1)
assert_discriminating "$EC_TC3" "$EC_TC3OK" "TC3(vague)=$EC_TC3 vs TC3ok(substantive)"

# ═════════════════════════════════════════════════════════════════════════════
# TC4 — (F-ROW-OMIT) concurrency 행 자체 누락 → exit 1 (AC-1a/9 침묵 skip 반증)
# ═════════════════════════════════════════════════════════════════════════════
tc4_body() {
  emit_skeleton_head
  echo "$SEC88_HEADER"
  echo "##### §8.8.0 Applicability decision (필수)"
  echo "| technique | applicability_status (DO/N/A) | g2_boundary_check |"
  echo "|---|:-:|---|"
  echo "| fuzz | N/A | g2_boundary_check ok |"
  echo "| property | N/A | g2_boundary_check ok |"
  echo "| load | N/A | g2_boundary_check ok |"
  # concurrency 행 의도적 누락 (F-ROW-OMIT)
  emit_88_x_na substantive
  emit_skeleton_tail
}
EC_TC4=$(run_case tc4_body 1 "TC4-row-omit-concurrency-FAIL" "concurrency 행 누락 → 4 기법 미파싱 → exit 1" | tail -1)

# ═════════════════════════════════════════════════════════════════════════════
# TC5 — (F-LOAD-NO-PERF) load=DO 인데 §8.8.3 본문에 §8.3 token 부재 → exit 1 (AC-6)
# ═════════════════════════════════════════════════════════════════════════════
tc5_body() {
  emit_skeleton_head
  echo "$SEC88_HEADER"
  emit_88_table N/A N/A DO N/A g2
  emit_88_na_sub 8.8.1 fuzz substantive
  emit_88_na_sub 8.8.2 property substantive
  emit_88_load_do "" noperf
  emit_88_na_sub 8.8.4 concurrency substantive
  emit_skeleton_tail
}
EC_TC5=$(run_case tc5_body 1 "TC5-load-no-perf-FAIL" "load DO + 4필드 완전이나 §8.3 token 부재 → exit 1 (AC-6)" | tail -1)

# ═════════════════════════════════════════════════════════════════════════════
# TC6 — (F-NO-G2-CHECK) g2_boundary_check token 부재 → exit 1 (AC-7) (Mutation-B kill-fixture)
# ═════════════════════════════════════════════════════════════════════════════
tc6_body() {
  emit_skeleton_head
  echo "$SEC88_HEADER"
  emit_88_table N/A N/A N/A N/A nog2
  emit_88_x_na substantive
  emit_skeleton_tail
}
EC_TC6=$(run_case tc6_body 1 "TC6-no-g2-token-FAIL" "g2_boundary_check token 전체 부재 → exit 1 (AC-7)" | tail -1)

# ═════════════════════════════════════════════════════════════════════════════
# TC7 — (F-8.6-GAP) §8.5(+§8.5.4) → §8.8 gap(§8.6 부재) → §8.8 외 사유 fail 0 → exit 0 (false-positive 0)
# ═════════════════════════════════════════════════════════════════════════════
tc7_body() {
  emit_skeleton_head
  cat <<'EOF'
#### §8.5 Stateful / restart invariant tests (CONDITIONAL)
##### §8.5.0 Applicability decision (필수)
| 적용 조건 | Y/N | 근거 |
|---|:-:|---|
| Long-running connection | N | 본 Story 는 declarative 산출물만 — 런타임 connection 0건으로 long-running 형상 부재함 |
| Stateful in-memory cache | N | in-memory cache 미사용 — stateless 산출물이라 cache 상태 누적 형상 자체 부재함 |
| Background worker | N | background worker 미도입 — 동기 처리만이라 worker lifecycle 형상 부재 상태 유지함 |
| Process restart-aware system | N | restart-aware system 부재 — 영속 상태 0건이라 restart recovery 형상 무관 상태 유지함 |
##### §8.5.4 N/A 명시 (4 적용 조건 모두 No 시)
N/A — 본 Story 는 declarative 산출물만 수정해 stateful 4 조건 모두 부재. 검증 채널: 단위 테스트. 면제 분류: runtime-inert
EOF
  # §8.6 의도적 부재(gap) → §8.8 로 점프
  echo "$SEC88_HEADER"
  emit_88_table N/A N/A N/A N/A g2
  emit_88_x_na substantive
  emit_skeleton_tail
}
EC_TC7=$(run_case tc7_body 0 "TC7-86-gap-allow" "§8.5.4 → §8.8 gap(§8.6 부재) → §8.8 외 사유 fail 0 → exit 0" | tail -1)

# ═════════════════════════════════════════════════════════════════════════════
# TC8 — (F-MIXED-NA) DO 3(유효) + concurrency N/A vague → exit 1 (Mutation-C kill-fixture)
# ═════════════════════════════════════════════════════════════════════════════
tc8_body() {
  emit_skeleton_head
  echo "$SEC88_HEADER"
  emit_88_table DO DO DO N/A g2
  emit_88_fuzz_do ""
  emit_88_property_do ""
  emit_88_load_do "" perf
  emit_88_na_sub 8.8.4 concurrency vague
  emit_88_5_ceiling
  emit_skeleton_tail
}
EC_TC8=$(run_case tc8_body 1 "TC8-mixed-NA-vague-FAIL" "DO 3(유효) + concurrency N/A vague → exit 1 (AC-2 hollow-gap)" | tail -1)

# ═════════════════════════════════════════════════════════════════════════════
# TC9 — (F-CEILING-OVERREACH) 4 DO 유효 + g2 + §8.8.5 천장 → exit 0 (over-reach 부재 실증)
# ═════════════════════════════════════════════════════════════════════════════
tc9_body() {
  emit_skeleton_head
  echo "$SEC88_HEADER"
  emit_88_table DO DO DO DO g2
  emit_88_fuzz_do ""
  emit_88_property_do ""
  emit_88_load_do "" perf
  emit_88_concurrency_do ""
  emit_88_5_ceiling
  emit_skeleton_tail
}
EC_TC9=$(run_case tc9_body 0 "TC9-ceiling-overreach-PASS" "4 DO 유효 + g2 + §8.8.5 천장 → exit 0 (게이트 fail-close 안 함)" | tail -1)

# ── test_ceiling_honesty_disclosed (doc-presence) ──
#   change-plan.md 템플릿 우선(다른 worker 삽입). 부재 시 skip-with-note + fixture §8.8.5 로 검증.
#   4 잔여(검출력/완결성/사유타당성/g2_boundary_check) 존재 + "완전 봉인" hard-claim 부재 grep assert.
ceiling_honesty_check() {
  local target="" src=""
  if [ -f "$REPO_ROOT/templates/change-plan.md" ] && grep -q '§8\.8\.5' "$REPO_ROOT/templates/change-plan.md" 2>/dev/null; then
    target="$REPO_ROOT/templates/change-plan.md"; src="change-plan.md 템플릿"
  else
    echo "  (note) change-plan.md 템플릿 §8.8.5 미삽입 — fixture §8.8.5 로 검증(skip-with-note)" >&2
    target=$(mktemp); tc9_body > "$target"; src="fixture §8.8.5"
  fi
  local ok=1
  for tok in "검출력" "완결성" "사유타당성" "g2_boundary_check"; do
    grep -q "$tok" "$target" || { echo "  ceiling honesty: '$tok' 부재 ($src)" >&2; ok=0; }
  done
  if grep -q "완전 봉인" "$target"; then
    echo "  ceiling honesty: '완전 봉인' hard-claim 존재 = over-claim ($src)" >&2; ok=0
  fi
  if [ "$ok" = "1" ]; then
    echo "✓ PASS: test_ceiling_honesty_disclosed — 4 잔여 개시 + '완전 봉인' 부재 ($src)" >&2
    tally_pass
  else
    echo "✗ FAIL: test_ceiling_honesty_disclosed — ceiling honesty 개시 미충족 ($src)" >&2
    tally_fail
  fi
  [ "$src" = "fixture §8.8.5" ] && rm -f "$target"
}
ceiling_honesty_check

# ═════════════════════════════════════════════════════════════════════════════
# TC-4b/4c/4d — per-technique DO 필드 검증 (1개 누락 → exit 1 ↔ 완전 → exit 0)
# ═════════════════════════════════════════════════════════════════════════════
# TC-4b property
tc4b_miss_body() {
  emit_skeleton_head; echo "$SEC88_HEADER"
  emit_88_table N/A DO N/A N/A g2
  emit_88_na_sub 8.8.1 fuzz substantive
  emit_88_property_do "sample_budget"
  emit_88_na_sub 8.8.3 load substantive
  emit_88_na_sub 8.8.4 concurrency substantive
  emit_skeleton_tail
}
tc4b_ok_body() {
  emit_skeleton_head; echo "$SEC88_HEADER"
  emit_88_table N/A DO N/A N/A g2
  emit_88_na_sub 8.8.1 fuzz substantive
  emit_88_property_do ""
  emit_88_na_sub 8.8.3 load substantive
  emit_88_na_sub 8.8.4 concurrency substantive
  emit_skeleton_tail
}
EC_4B_MISS=$(run_case tc4b_miss_body 1 "TC4b-property-missing-FAIL" "property DO sample_budget 누락 → exit 1" | tail -1)
EC_4B_OK=$(run_case tc4b_ok_body 0 "TC4b-property-complete-PASS" "property DO 4필드 완전 → exit 0" | tail -1)
assert_discriminating "$EC_4B_MISS" "$EC_4B_OK" "TC-4b property miss=$EC_4B_MISS vs ok"

# TC-4c load (§8.3 는 양쪽 유지 — 필드 누락만 차이)
tc4c_miss_body() {
  emit_skeleton_head; echo "$SEC88_HEADER"
  emit_88_table N/A N/A DO N/A g2
  emit_88_na_sub 8.8.1 fuzz substantive
  emit_88_na_sub 8.8.2 property substantive
  emit_88_load_do "duration" perf
  emit_88_na_sub 8.8.4 concurrency substantive
  emit_skeleton_tail
}
tc4c_ok_body() {
  emit_skeleton_head; echo "$SEC88_HEADER"
  emit_88_table N/A N/A DO N/A g2
  emit_88_na_sub 8.8.1 fuzz substantive
  emit_88_na_sub 8.8.2 property substantive
  emit_88_load_do "" perf
  emit_88_na_sub 8.8.4 concurrency substantive
  emit_skeleton_tail
}
EC_4C_MISS=$(run_case tc4c_miss_body 1 "TC4c-load-missing-FAIL" "load DO duration 누락(§8.3 유지) → exit 1" | tail -1)
EC_4C_OK=$(run_case tc4c_ok_body 0 "TC4c-load-complete-PASS" "load DO 4필드 완전 + §8.3 → exit 0" | tail -1)
assert_discriminating "$EC_4C_MISS" "$EC_4C_OK" "TC-4c load miss=$EC_4C_MISS vs ok"

# TC-4d concurrency (5필드)
tc4d_miss_body() {
  emit_skeleton_head; echo "$SEC88_HEADER"
  emit_88_table N/A N/A N/A DO g2
  emit_88_na_sub 8.8.1 fuzz substantive
  emit_88_na_sub 8.8.2 property substantive
  emit_88_na_sub 8.8.3 load substantive
  emit_88_concurrency_do "worker_count"
  emit_skeleton_tail
}
tc4d_ok_body() {
  emit_skeleton_head; echo "$SEC88_HEADER"
  emit_88_table N/A N/A N/A DO g2
  emit_88_na_sub 8.8.1 fuzz substantive
  emit_88_na_sub 8.8.2 property substantive
  emit_88_na_sub 8.8.3 load substantive
  emit_88_concurrency_do ""
  emit_skeleton_tail
}
EC_4D_MISS=$(run_case tc4d_miss_body 1 "TC4d-concurrency-missing-FAIL" "concurrency DO worker_count 누락 → exit 1" | tail -1)
EC_4D_OK=$(run_case tc4d_ok_body 0 "TC4d-concurrency-complete-PASS" "concurrency DO 5필드 완전 → exit 0" | tail -1)
assert_discriminating "$EC_4D_MISS" "$EC_4D_OK" "TC-4d concurrency miss=$EC_4D_MISS vs ok"

# ═════════════════════════════════════════════════════════════════════════════
# Mutation A/B/C 실 RED kill (execution-liveness L3)
#   $LINT_PY 복사 → sentinel 라인 sed 무력화(pass) → kill-fixture 로 original vs mutated 비교.
#   KILLED = original(exit 1) ≠ mutated(exit 0). hollow(둘 다 exit 1) = FAIL.
# ═════════════════════════════════════════════════════════════════════════════
run_mutation_kill() {
  local sentinel="$1" body_fn="$2" mut_name="$3"
  local MUT_DIR; MUT_DIR=$(mktemp -d)
  local MUT_PY="$MUT_DIR/check_doc_section_schema.py"
  sed -E "s/^([[:space:]]*)fails\\.append.*${sentinel}.*\$/\\1pass/" "$LINT_PY" > "$MUT_PY"
  # hollow mutation 방지 — sed 가 실제로 sentinel 라인을 바꿨는지 확인
  if diff -q "$LINT_PY" "$MUT_PY" >/dev/null 2>&1; then
    echo "✗ FAIL: $mut_name — sentinel '$sentinel' 부재/sed 무효 (mutation 적용 불가, hollow)" >&2
    tally_fail; rm -rf "$MUT_DIR"; echo "NA NA"; return
  fi
  # 문법 유효성 — mutated 가 valid python 인지 (broken mutation 방지)
  if ! "$PY" -c "import py_compile,sys; py_compile.compile(sys.argv[1], doraise=True)" "$MUT_PY" >/dev/null 2>&1; then
    echo "✗ FAIL: $mut_name — mutated lint 문법 오류 (sed 파손)" >&2
    tally_fail; rm -rf "$MUT_DIR"; echo "NA NA"; return
  fi
  local ec_orig; ec_orig=$(run_case "$body_fn" 1 "${mut_name}-original-catches" "original lint 이 kill-fixture 를 잡음 (exit 1)" | tail -1)
  local ec_mut;  ec_mut=$(run_case "$body_fn" 0 "${mut_name}-mutated-misses" "mutated lint 이 kill-fixture 를 놓침 (exit 0)" "$MUT_PY" | tail -1)
  if [ "$ec_orig" != "$ec_mut" ]; then
    echo "✓ PASS: $mut_name KILLED — original(exit=$ec_orig) ≠ mutated(exit=$ec_mut) = discriminating (hollow 아님)" >&2
    tally_pass
  else
    echo "✗ FAIL: $mut_name SURVIVED — original(exit=$ec_orig) == mutated(exit=$ec_mut) = check hollow (형식 green)" >&2
    tally_fail
  fi
  rm -rf "$MUT_DIR"
  echo "$ec_orig $ec_mut"
}

MUT_A=$(run_mutation_kill "MUT-A-DO-FIELDS" tc2_body "Mutation-A(DO-fields)")     # kill-fixture = TC2
MUT_B=$(run_mutation_kill "MUT-B-G2-TOKEN"  tc6_body "Mutation-B(g2-token)")      # kill-fixture = TC6
MUT_C=$(run_mutation_kill "MUT-C-MIXED-NA"  tc8_body "Mutation-C(mixed-NA)")      # kill-fixture = TC8

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
PASS=$(grep -cF "P" "$TALLY" 2>/dev/null | head -1); PASS=$(( PASS + 0 ))
FAIL=$(grep -cF "F" "$TALLY" 2>/dev/null | head -1); FAIL=$(( FAIL + 0 ))

echo ""
echo "============================================================"
echo "Test Summary (CFP-2605 §8.8 동적 테스트 로스터 doc-section lint)"
echo "============================================================"
echo "PASS: $PASS / FAIL: $FAIL / TOTAL: $((PASS+FAIL))"
echo "TC1=$EC_TC1 TC2=$EC_TC2 TC3=$EC_TC3 TC3ok=$EC_TC3OK TC4=$EC_TC4 TC5=$EC_TC5 TC6=$EC_TC6 TC7=$EC_TC7 TC8=$EC_TC8 TC9=$EC_TC9"
echo "TC-4b(miss/ok)=$EC_4B_MISS/$EC_4B_OK  TC-4c=$EC_4C_MISS/$EC_4C_OK  TC-4d=$EC_4D_MISS/$EC_4D_OK"
echo "Mutation kill (orig mut): A=[$MUT_A] B=[$MUT_B] C=[$MUT_C]  (KILLED = 1 0)"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All discriminating cases passed (matrix ⊇ §8.2 fixtures + mutation A/B/C KILLED)"
  exit 0
else
  echo "✗ Some cases failed"
  exit 1
fi
