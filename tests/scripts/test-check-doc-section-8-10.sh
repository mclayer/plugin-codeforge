#!/usr/bin/env bash
# tests/scripts/test-check-doc-section-8-10.sh
# CFP-2624 (Epic CFP-2602 G3) Phase 2 — Discriminating self-test for §8.10 dark-path activation manifest
# doc-section lint + G3(b) EPIC-RESULTS 요구-슬라이스 매핑 lint (ADR-152 §결정 5·7·8).
# L3 execution-liveness: mutation 을 실제 kill (형식 green 금지 — born-hollow 금지).
#
# 검증 대상 = scripts/lib/check_doc_section_schema.py 의
#   check_section_8_10()           (canonical = ADR-152 §결정 7, single `dark_path` axis)
#   check_epic_results_slice_mapping()  (canonical = ADR-152 §결정 5, EPIC-RESULTS 섹션 presence)
# 선례 = tests/scripts/test-check-doc-section-8-9.sh (verbatim-homolog 구조 — DAST single-axis → dark-path single-axis).
#
# check_section_8_10() 동작 (canonical, 검증 기준):
#  - §8.10 헤딩 부재 → 무검사(return []). §8.6 gap 무관(§8.10 헤딩만 트리거).
#  - §8.10 헤딩 존재 + §8.10.0 헤딩 부재 → fail.
#  - §8.10.0 표 `| dark_path | (DO|N/A) |` 행 미파싱 → fail.
#  - g_boundary_check token 이 §8.10 region(§8.10 헤딩 ~ 다음 #{1,4} 헤딩) 에 부재 → fail (AC-1a).
#  - dark_path=DO 시:
#      · §8.10.1 산출물 계약 6 필드(flag_identifier/default_state/activation_test_ref/on_state_assertion/
#        discriminating_basis/status) 누락 → fail (AC-1a).
#      · status ∉ {activated,infeasible,natural_na} → fail (AC-1a).
#      · status=activated 인데 activation_test_ref 공백 OR on_state_assertion(<15자) → fail (AC-2 activation-honesty §3.5a).
#      · status=infeasible 인데 infeasibility_reason(<30자) 부재 → fail (AC-1a §3.5b).
#  - dark_path=N/A(aggregate) 시: §8.10.x 헤딩 + substantive reason(30자 minimum, NA_85_SUBSTANTIVE_RE) 필수.
#  ★ 정직 천장(ADR-152 §결정3): 게이트는 applicability 레코드·6 필드·status enum·2 cross-field 선언-정합
#    presence/구조까지만. 검출력(discriminating-B 실행사)/열거 완결성/사유타당성/g_boundary_check 준수는
#    강제하지 않음(G3-review·advisory defense-in-depth) — TC-CLEAN-PASS 가 detection 미강제(천장) 실증.
#
# check_epic_results_slice_mapping() 동작 (canonical):
#  - 파일명 EPIC-RESULTS-*.md 아님 → 무검사(return []).
#  - §requirement-slice-mapping 섹션 부재 → fail (AC-6b, MUT-SLICE kill).
#  - 섹션 present 이나 well-formed row(slice|{story|defer}|tracking-ref) ∨ N/A(30자) 부재 → fail (AC-6b).
#  - 섹션에 천장 문구('완결성') 부재 → fail (AC-8).
#
# ── CWD 의무 (CFP-2449 gotcha) ────────────────────────────────────────────────
#  check_doc_section_schema.py 는 CWD-상대 스캔(`Path("docs/change-plans").rglob` / `Path("docs/retros")`).
#  argv 무시. → 격리 temp dir 에 fixture 만들고 그 dir 를 CWD 로 python3 호출.
#  change-plan cfp 번호 = 9999 (LEGACY_CHANGE_PLAN_CFPS 회피). fixture 는 §1-§11 skeleton 전부 포함 —
#  §8.10 외 사유(필수 섹션 누락 등) fail 0 격리. EPIC-RESULTS fixture 는 §1-§4 retro skeleton 포함.
#
# ── authoritative matrix (matrix ⊇ change-plan §8.2 discriminating fixtures 불변식) ──
#  TC-CLEAN-PASS   완전-valid DO 6필드 activated + 얕은 관측(검출 0) → exit 0 (천장 실증 — detection 미강제)
#  F-MANIFEST-MISS DO 6필드 중 1개 누락 → exit 1 ↔ 완전 → exit 0 (AC-1a, MUT-DARK-A kill-fixture)
#  F-NO-G-CHECK    g_boundary_check token 부재 → exit 1 (AC-1a, MUT-DARK-B kill-fixture)
#  F-STATUS-BAD    status=enum 외 값 → exit 1 (AC-1a, MUT-DARK-C kill-fixture)
#  F-STUB-ACTIVATED status=activated + on_state_assertion 공백 → exit 1 ↔ substantive(≥15) → exit 0 (AC-2, MUT-DARK-D)
#  F-INFEAS-NR     status=infeasible + reason 부재 → exit 1 ↔ reason(≥30) → exit 0 (AC-1a, MUT-DARK-E kill)
#  F-NA-VAGUE      dark_path=N/A + §8.10.x vague(<30) → exit 1 ↔ substantive(≥30, 3축) → exit 0 (AC-1b routed)
#  F-8.6-GAP       §8.5(+§8.5.4) → §8.10 gap(§8.6 부재) → §8.10 외 사유 fail 0 → exit 0 (false-positive 0)
#  F-SLICE-PRESENT EPIC-RESULTS §requirement-slice-mapping present + row + 천장 → exit 0 ↔ 부재 → exit 1 (AC-6b, MUT-SLICE)
#  F-SLICE-MALFORM 섹션 present 이나 disposition ∉ {story,defer} → exit 1 (AC-6b)
#  F-SLICE-CEILING 매핑 섹션 천장 문구 부재 → exit 1 (AC-8)
#  F-SLICE-NA      §requirement-slice-mapping N/A-substantive → exit 0 (AC-6b routed)
#  F-NON-EPIC-EXEMPT  EPIC-RESULTS-* 아닌 retro → slice-mapping 미검사 → exit 0 (false-positive 0)
#  sibling-guard   check_section_8_10() / check_epic_results_slice_mapping() 부재/미배선 → 명시 FAIL(silent skip 금지)
#  ceiling-honesty LIVE 실 template §8.10.5 4 잔여 개시 + "완전 봉인" over-claim 부재 (NO fixture-fallback)
#  ※ F-8.9-BLEED(§8.9 region-slice 무회귀) = 별도 test-check-doc-section-8-9.sh 재구동으로 증명(본 파일 밖).
#
# ── Mutation 실 RED 증명 (execution-liveness L3 — born-hollow 금지) ─────────────
#  canonical check 에 sentinel 주석: MUT-DARK-A-DO-FIELDS / MUT-DARK-B-G-TOKEN / MUT-DARK-C-STATUS-ENUM /
#  MUT-DARK-D-ACTIVATION / MUT-DARK-E-INFEAS-REASON / MUT-SLICE-PRESENCE.
#  각 mutation = $LINT_PY 복사 → sentinel 라인을 동일 들여쓰기 `pass` 로 sed 무력화 → kill-fixture 실행.
#  KILL 판정: original(kill-fixture)=exit 1 AND mutated(kill-fixture)=exit 0 → original≠mutated → KILLED.
#  mutated 가 여전히 exit 1 = check hollow → self-test FAIL(형식 green 차단).
#  ★ born-hollow 재발 경계: G2 F-CR-004 / G4 F-CR-001 처럼 exit≠(false,1) 을 "killed" 로 오수용 금지 —
#    mutant 가 실제로 leak(기대-PASS 로 새어나감)함을 positive 단정(orig=1 ∧ mut=0)으로 실증.
#
# ── 사전 의존 (sibling — DeveloperPL self-perform) ─────────────────────────────
#  check_section_8_10()/check_epic_results_slice_mapping() 미삽입/미배선 시 → 명시 FAIL(silent skip 금지).
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

# ── sibling-dependency guard (§8.9 self-test 동형) ──
if [ ! -f "$LINT_PY" ]; then
  echo "✗ FAIL: check_doc_section_schema.py 부재 ($LINT_PY)"
  exit 1
fi
for fn in check_section_8_10 check_epic_results_slice_mapping; do
  if ! grep -q "def $fn" "$LINT_PY"; then
    echo "✗ FAIL: check_doc_section_schema.py 에 $fn() 부재 (미삽입 — sibling-dependent, PL 재실행 필요)"
    exit 1
  fi
  # main() 미배선(호출 부재) 검출 — 함수만 있고 호출 없으면 검사가 실행되지 않아 전 fixture false-pass.
  if [ "$(grep -c "$fn" "$LINT_PY")" -lt 2 ]; then
    echo "✗ FAIL: $fn() 가 main() 에 미배선 (호출 부재 — 함수 dead-code). PL 재실행 필요"
    exit 1
  fi
done

# ═════════════════════════════════════════════════════════════════════════════
# change-plan §1-§11 skeleton (§8.10 외 사유 fail 0 격리). §8 본문 = per-fixture §8.10.
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

SEC810_HEADER="#### §8.10 dark-path 로스터 (default-off flag 활성화 — oracle=activation ⊥ G4 robustness ⊥ G5 attack — CONDITIONAL — CFP-2624 / ADR-152)"

# emit_810_table <status> <g|nog>
#   g   → §8.10.0 표 3번째 컬럼에 g_boundary_check token 포함(AC-1a 충족).
#   nog → 3번째 컬럼명·셀에서 g_boundary_check token 제거(AC-1a 위반).
emit_810_table() {
  local status="$1" g="${2:-g}"
  echo "##### §8.10.0 Applicability decision (필수)"
  if [ "$g" = "g" ]; then
    echo "| axis | applicability_status (DO/N/A) | g_boundary_check |"
    echo "|---|:-:|---|"
    echo "| dark_path | $status | g_boundary_check: soak/restart/replay(G2)·fuzz(G4)·DAST(G5) 경계 미침범 확인 |"
  else
    echo "| axis | applicability_status (DO/N/A) | boundary_note |"
    echo "|---|:-:|---|"
    echo "| dark_path | $status | boundary reviewed ok |"
  fi
}

# emit_810_do <omit> <status> <atref> <osassert> <reason>
#   omit    : 누락할 필드명 ("" = 전부 기재)
#   status  : status 값 (activated|infeasible|natural_na|bogus...)
#   atref   : yes|no  (activation_test_ref 값 채움/공백)
#   osassert: full|empty  (on_state_assertion substantive/공백 stub)
#   reason  : no|yes  (infeasibility_reason 포함 여부, yes=≥30자)
# ※ 필드 값은 6 필드명을 substring 으로 포함하지 않도록 설계(substring presence 검사 오탐 방지).
emit_810_do() {
  local omit="${1:-}" status="${2:-activated}" atref="${3:-yes}" osassert="${4:-full}" reason="${5:-no}"
  echo "##### §8.10.1 dark_path (DO — 산출물 계약)"
  [ "$omit" = "flag_identifier" ]      || echo "- flag_identifier: COMPACT_TIERED env var gate"
  [ "$omit" = "default_state" ]        || echo "- default_state: default-off (COMPACT_TIERED=0 baseline)"
  if [ "$omit" != "activation_test_ref" ]; then
    if [ "$atref" = "yes" ]; then
      echo "- activation_test_ref: tests/test_compact.py::test_tiered_serving_on"
    else
      echo "- activation_test_ref: "
    fi
  fi
  if [ "$omit" != "on_state_assertion" ]; then
    if [ "$osassert" = "full" ]; then
      echo "- on_state_assertion: asserts warm-tier rows served when gate enabled"
    else
      echo "- on_state_assertion: "
    fi
  fi
  [ "$omit" = "discriminating_basis" ] || echo "- discriminating_basis: gate OFF makes the test skip so it fails closed"
  [ "$omit" = "status" ]               || echo "- status: $status"
  if [ "$reason" = "yes" ]; then
    echo "- infeasibility_reason: 대상 flag 뒤 도달 코드가 이번 주기에는 실행 러너 부재로 활성화 불가함을 정당화한다"
  fi
}

# emit_810_5_ceiling — 정직 천장(§8.10.5). fixture fidelity 용(lint 미검사, TC-CLEAN-PASS 에만 포함).
emit_810_5_ceiling() {
  echo "##### §8.10.5 정직 천장"
  echo "- (i) 검출력(discriminating-B) = G3-review 위임 (ii) 완결성 = review 보강 (iii) 사유타당성 = review 판정 (iv) g_boundary_check presence != 실준수 (게이트 강제 아님)"
}

# emit_810_x_na <substantive|vague> — aggregate dark_path=N/A 명시
emit_810_x_na() {
  echo "##### §8.10.x N/A 명시 (dark_path 미적용 — default-off product flag 0)"
  if [ "$1" = "vague" ]; then
    echo "N/A — 짧음"
  else
    echo "N/A — codeforge 자체는 배포 product 가 아니라 문서·플러그인 정의(runtime-inert)로 default-off flag 뒤 도달 가능한 product 코드 0. 게이트-자신 self-test 는 active. 검증 채널: check_section_8_10 self-test. 면제 분류: plugin-meta-na"
  fi
}

# ── EPIC-RESULTS fixture (retro §1-§4 skeleton + §requirement-slice-mapping) ──
emit_epic_skeleton() {
  cat <<'EOF'
# Epic CFP-9999 — fixture
## §1 child summary
fixture
## §2 Phase decomposition
fixture
## §3 Blocking AC
fixture
## §4 Calibration AC
fixture
EOF
}
# emit_slice_mapping <mode>: present | malformed | noceiling | na | absent
emit_slice_mapping() {
  case "$1" in
    absent) : ;;  # 섹션 자체 미출력
    present)
      echo "## §requirement-slice-mapping"
      echo "| slice | disposition | tracking-ref |"
      echo "|---|---|---|"
      echo "| S4 warm-tier serving | story | CFP-1234 |"
      echo "| S5 rollup | defer | #999 (req-slice-defer) |"
      echo "정직 천장: 슬라이스 열거 완결성은 기계 강제 아님 — PMO Epic-close 감사·review 보강."
      ;;
    malformed)
      echo "## §requirement-slice-mapping"
      echo "| slice | disposition | tracking-ref |"
      echo "|---|---|---|"
      echo "| S4 warm-tier serving | maybe | CFP-1234 |"
      echo "정직 천장: 슬라이스 열거 완결성은 기계 강제 아님 — PMO Epic-close 감사·review 보강."
      ;;
    noceiling)
      echo "## §requirement-slice-mapping"
      echo "| slice | disposition | tracking-ref |"
      echo "|---|---|---|"
      echo "| S4 warm-tier serving | story | CFP-1234 |"
      ;;
    na)
      echo "## §requirement-slice-mapping"
      echo "N/A — 본 Epic 은 단일 요구 슬라이스로 분해 불가한 governance 변경이라 매핑 대상 슬라이스 0 (완결성 정직 공개)."
      ;;
  esac
}

# ── setup 함수 (격리 fixture 트리 구성 — temp dir 는 $CASE_T 전역으로 주입) ──
setup_cp() {  # $1=body_fn (change-plan §8 본문 생성). T=$CASE_T
  local body_fn="$1" T="$CASE_T"
  mkdir -p "$T/docs/change-plans"
  { emit_skeleton_head; "$body_fn"; emit_skeleton_tail; } > "$T/docs/change-plans/cfp-9999-fixture.md"
}
setup_epic() {  # $1=mode, $2=filename(default EPIC-RESULTS-9999.md). T=$CASE_T
  local mode="$1" fname="${2:-EPIC-RESULTS-9999.md}" T="$CASE_T"
  mkdir -p "$T/docs/retros"
  { emit_epic_skeleton; emit_slice_mapping "$mode"; } > "$T/docs/retros/$fname"
}

# run_case <setup_cmd> <expected_exit> <name> <desc> [lint_py]
#   setup_cmd = 문자열로 표현된 setup 호출(eval). temp dir 는 $CASE_T 전역으로 주입.
run_case() {
  local setup_cmd="$1" expected="$2" name="$3" desc="$4"
  local lint="${5:-$LINT_PY}"
  local T; T=$(mktemp -d)
  CASE_T="$T"
  eval "$setup_cmd"
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

# ── change-plan §8.10 본문 생성 함수 (setup_cp body_fn) — 각 함수는 §8.10 섹션 헤더 선행 emit ──
b_clean()       { echo "$SEC810_HEADER"; emit_810_table DO g;   emit_810_do "" activated yes full no; emit_810_5_ceiling; }
b_miss()        { echo "$SEC810_HEADER"; emit_810_table DO g;   emit_810_do "discriminating_basis" activated yes full no; }
b_complete()    { echo "$SEC810_HEADER"; emit_810_table DO g;   emit_810_do "" activated yes full no; }
b_nog()         { echo "$SEC810_HEADER"; emit_810_table N/A nog; emit_810_x_na substantive; }
b_status_bad()  { echo "$SEC810_HEADER"; emit_810_table DO g;   emit_810_do "" bogus yes full no; }
b_stub()        { echo "$SEC810_HEADER"; emit_810_table DO g;   emit_810_do "" activated yes empty no; }
b_stub_ok()     { echo "$SEC810_HEADER"; emit_810_table DO g;   emit_810_do "" activated yes full no; }
b_infeas_nr()   { echo "$SEC810_HEADER"; emit_810_table DO g;   emit_810_do "" infeasible yes full no; }
b_infeas_ok()   { echo "$SEC810_HEADER"; emit_810_table DO g;   emit_810_do "" infeasible yes full yes; }
b_na_vague()    { echo "$SEC810_HEADER"; emit_810_table N/A g;  emit_810_x_na vague; }
b_na_sub()      { echo "$SEC810_HEADER"; emit_810_table N/A g;  emit_810_x_na substantive; }
b_86gap() {
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
  # §8.6 의도적 부재(gap) → §8.10 로 점프
  echo "$SEC810_HEADER"
  emit_810_table N/A g
  emit_810_x_na substantive
}

# ═════════════════════════════════════════════════════════════════════════════
# TC-CLEAN-PASS (천장 실증) — 완전-valid DO 6필드 activated + 얕은 관측 → exit 0
#   게이트가 discriminating-B 검출을 강제하지 않음을 실증(INV-G3-4 천장). ★ 핵심 정직 TC.
# ═════════════════════════════════════════════════════════════════════════════
EC_CLEAN=$(run_case "setup_cp b_clean" 0 "TC-CLEAN-PASS-ceiling" "완전-valid DO 6필드 activated + 얕은 관측 → exit 0 (detection 미강제 천장)" | tail -1)

# F-MANIFEST-MISSING-FIELD (MUT-DARK-A kill-fixture) — DO discriminating_basis 누락 → exit 1 ↔ 완전 → exit 0
EC_MISS=$(run_case "setup_cp b_miss" 1 "F-MANIFEST-MISSING-FIELD" "DO discriminating_basis 누락 → exit 1 (AC-1a)" | tail -1)
EC_COMPLETE=$(run_case "setup_cp b_complete" 0 "F-MANIFEST-COMPLETE" "DO 6필드 완전 → exit 0" | tail -1)
assert_discriminating "$EC_MISS" "$EC_COMPLETE" "F-MANIFEST miss=$EC_MISS vs complete"

# F-NO-G-CHECK (MUT-DARK-B) — g_boundary_check token 부재 → exit 1
EC_NOG=$(run_case "setup_cp b_nog" 1 "F-NO-G-CHECK" "g_boundary_check token 부재 → exit 1 (AC-1a)" | tail -1)

# F-STATUS-BAD-ENUM (MUT-DARK-C) — status=bogus → exit 1
EC_STATUS=$(run_case "setup_cp b_status_bad" 1 "F-STATUS-BAD-ENUM" "status=bogus(enum 외) → exit 1 (AC-1a)" | tail -1)

# F-STUB-ACTIVATED (MUT-DARK-D) — status=activated + on_state_assertion 공백 → exit 1 ↔ substantive → exit 0
EC_STUB=$(run_case "setup_cp b_stub" 1 "F-STUB-ACTIVATED" "status=activated + on_state_assertion 공백 → exit 1 (AC-2 activation-honesty)" | tail -1)
EC_STUB_OK=$(run_case "setup_cp b_stub_ok" 0 "F-STUB-SUBSTANTIVE" "status=activated + on_state_assertion(≥15) → exit 0" | tail -1)
assert_discriminating "$EC_STUB" "$EC_STUB_OK" "F-STUB stub=$EC_STUB vs substantive"

# F-INFEASIBLE-NO-REASON (MUT-DARK-E) — status=infeasible + reason 부재 → exit 1 ↔ reason(≥30) → exit 0
EC_INF=$(run_case "setup_cp b_infeas_nr" 1 "F-INFEASIBLE-NO-REASON" "status=infeasible + reason 부재 → exit 1 (AC-1a §3.5b)" | tail -1)
EC_INF_OK=$(run_case "setup_cp b_infeas_ok" 0 "F-INFEASIBLE-WITH-REASON" "status=infeasible + reason(≥30) → exit 0" | tail -1)
assert_discriminating "$EC_INF" "$EC_INF_OK" "F-INFEAS noreason=$EC_INF vs reason"

# F-NA-VAGUE ↔ F-NA-SUBSTANTIVE — dark_path=N/A + §8.10.x vague(<30) → exit 1 ↔ substantive(≥30) → exit 0
EC_NA_V=$(run_case "setup_cp b_na_vague" 1 "F-NA-VAGUE" "dark_path=N/A + §8.10.x reason <30자 → exit 1 (AC-1b)" | tail -1)
EC_NA_S=$(run_case "setup_cp b_na_sub" 0 "F-NA-SUBSTANTIVE" "dark_path=N/A + §8.10.x substantive 30자+ → exit 0" | tail -1)
assert_discriminating "$EC_NA_V" "$EC_NA_S" "F-NA vague=$EC_NA_V vs substantive"

# F-8.6-GAP — §8.5.4 → §8.10 gap(§8.6 부재) → §8.10 외 사유 fail 0 → exit 0 (false-positive 0)
EC_86GAP=$(run_case "setup_cp b_86gap" 0 "F-8.6-GAP" "§8.5.4 → §8.10 gap(§8.6 부재) → §8.10 외 사유 fail 0 → exit 0" | tail -1)

# ═════════════════════════════════════════════════════════════════════════════
# G3(b) EPIC-RESULTS §requirement-slice-mapping
# ═════════════════════════════════════════════════════════════════════════════
# F-SLICE-MAPPING-PRESENT (MUT-SLICE kill-fixture) — 섹션 present + row + 천장 → exit 0 ↔ 부재 → exit 1
EC_SLICE_ABS=$(run_case "setup_epic absent"  1 "F-SLICE-MAPPING-ABSENT" "EPIC-RESULTS §requirement-slice-mapping 섹션 부재 → exit 1 (AC-6b)" | tail -1)
EC_SLICE_OK=$(run_case  "setup_epic present" 0 "F-SLICE-MAPPING-PRESENT" "섹션 present + well-formed row + 천장 → exit 0" | tail -1)
assert_discriminating "$EC_SLICE_ABS" "$EC_SLICE_OK" "F-SLICE absent=$EC_SLICE_ABS vs present"

# F-SLICE-MAPPING-MALFORMED — disposition ∉ {story,defer} → exit 1
EC_SLICE_MAL=$(run_case "setup_epic malformed" 1 "F-SLICE-MAPPING-MALFORMED" "disposition ∉ {story,defer} → exit 1 (AC-6b)" | tail -1)

# F-SLICE-CEILING — 매핑 섹션 천장 문구 부재 → exit 1
EC_SLICE_CEIL=$(run_case "setup_epic noceiling" 1 "F-SLICE-CEILING" "매핑 섹션 천장 문구('완결성') 부재 → exit 1 (AC-8)" | tail -1)

# F-SLICE-NA — §requirement-slice-mapping N/A-substantive → exit 0
EC_SLICE_NA=$(run_case "setup_epic na" 0 "F-SLICE-NA" "§requirement-slice-mapping N/A-substantive → exit 0 (AC-6b routed)" | tail -1)

# F-NON-EPIC-RESULTS-EXEMPT — EPIC-RESULTS-* 아닌 retro(슬라이스 섹션 부재) → 미검사 → exit 0
EC_NONEPIC=$(run_case "setup_epic absent retro-9999.md" 0 "F-NON-EPIC-RESULTS-EXEMPT" "EPIC-RESULTS-* 아닌 retro → slice-mapping 미검사 → exit 0 (false-positive 0)" | tail -1)

# ── test_ceiling_honesty_disclosed (doc-presence — LIVE 회귀가드, NO fixture-fallback) ──
#   실 template(plugins/codeforge-design/templates/change-plan.md) §8.10.5 를 직접 검증한다.
#   4 잔여(검출력 / 완결성 / 타당성 / g_boundary_check) 존재 + "완전 봉인" hard-claim 부재(금지 문맥 제외).
ceiling_honesty_check() {
  local target="$REPO_ROOT/plugins/codeforge-design/templates/change-plan.md" src="change-plan.md 실 템플릿"
  if [ ! -f "$target" ] || ! grep -q '§8\.10\.5' "$target"; then
    echo "✗ FAIL: test_ceiling_honesty_disclosed — 실 템플릿($target) 부재 또는 §8.10.5 미존재 (LIVE 회귀가드 — hollow fixture fallback 폐지)" >&2
    tally_fail
    return
  fi
  local ok=1
  for tok in "검출력" "완결성" "타당성" "g_boundary_check"; do
    grep -q "$tok" "$target" || { echo "  ceiling honesty: '$tok' 부재 ($src)" >&2; ok=0; }
  done
  # over-claim 검출: "완전 봉인" hard-claim(금지 문맥 아님) 존재 = FAIL.
  if grep "완전 봉인" "$target" | grep -qv "금지"; then
    echo "  ceiling honesty: '완전 봉인' hard-claim(금지 문맥 아님) 존재 = over-claim ($src)" >&2; ok=0
  fi
  if [ "$ok" = "1" ]; then
    echo "✓ PASS: test_ceiling_honesty_disclosed — 실 템플릿 §8.10.5 4 잔여 개시 + '완전 봉인' hard-claim 부재 ($src)" >&2
    tally_pass
  else
    echo "✗ FAIL: test_ceiling_honesty_disclosed — ceiling honesty 개시 미충족 ($src)" >&2
    tally_fail
  fi
}
ceiling_honesty_check

# ═════════════════════════════════════════════════════════════════════════════
# Mutation 실 RED kill (execution-liveness L3 — born-hollow 금지)
#   $LINT_PY 복사 → sentinel 라인 sed 무력화(pass) → kill-fixture 로 original vs mutated 비교.
#   KILLED = original(exit 1) ≠ mutated(exit 0). hollow(둘 다 exit 1) = FAIL.
# ═════════════════════════════════════════════════════════════════════════════
run_mutation_kill() {
  local sentinel="$1" setup_cmd="$2" mut_name="$3"
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
  local ec_orig; ec_orig=$(run_case "$setup_cmd" 1 "${mut_name}-original-catches" "original lint 이 kill-fixture 를 잡음 (exit 1)" | tail -1)
  local ec_mut;  ec_mut=$(run_case  "$setup_cmd" 0 "${mut_name}-mutated-misses"  "mutated lint 이 kill-fixture 를 놓침 (exit 0)" "$MUT_PY" | tail -1)
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

MUT_A=$(run_mutation_kill "MUT-DARK-A-DO-FIELDS"     "setup_cp b_miss"       "Mutation-A(DO-fields)")       # kill = F-MANIFEST-MISSING-FIELD
MUT_B=$(run_mutation_kill "MUT-DARK-B-G-TOKEN"       "setup_cp b_nog"        "Mutation-B(g-token)")         # kill = F-NO-G-CHECK
MUT_C=$(run_mutation_kill "MUT-DARK-C-STATUS-ENUM"   "setup_cp b_status_bad" "Mutation-C(status-enum)")     # kill = F-STATUS-BAD-ENUM
MUT_D=$(run_mutation_kill "MUT-DARK-D-ACTIVATION"    "setup_cp b_stub"       "Mutation-D(activation-honesty)") # kill = F-STUB-ACTIVATED
MUT_E=$(run_mutation_kill "MUT-DARK-E-INFEAS-REASON" "setup_cp b_infeas_nr"  "Mutation-E(infeas-reason)")   # kill = F-INFEASIBLE-NO-REASON
MUT_SLICE=$(run_mutation_kill "MUT-SLICE-PRESENCE"   "setup_epic absent"     "Mutation-SLICE(mapping-presence)") # kill = F-SLICE-MAPPING-ABSENT

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
PASS=$(grep -cF "P" "$TALLY" 2>/dev/null | head -1); PASS=$(( PASS + 0 ))
FAIL=$(grep -cF "F" "$TALLY" 2>/dev/null | head -1); FAIL=$(( FAIL + 0 ))

echo ""
echo "============================================================"
echo "Test Summary (CFP-2624 §8.10 dark-path activation manifest + G3(b) 요구-슬라이스 매핑 lint)"
echo "============================================================"
echo "PASS: $PASS / FAIL: $FAIL / TOTAL: $((PASS+FAIL))"
echo "CLEAN=$EC_CLEAN F-MISS(miss/complete)=$EC_MISS/$EC_COMPLETE F-NO-G=$EC_NOG F-STATUS=$EC_STATUS"
echo "F-STUB(stub/ok)=$EC_STUB/$EC_STUB_OK F-INFEAS(nr/ok)=$EC_INF/$EC_INF_OK F-NA(vague/sub)=$EC_NA_V/$EC_NA_S F-8.6-GAP=$EC_86GAP"
echo "SLICE(absent/present)=$EC_SLICE_ABS/$EC_SLICE_OK malform=$EC_SLICE_MAL ceiling=$EC_SLICE_CEIL na=$EC_SLICE_NA non-epic=$EC_NONEPIC"
echo "Mutation kill (orig mut): A=[$MUT_A] B=[$MUT_B] C=[$MUT_C] D=[$MUT_D] E=[$MUT_E] SLICE=[$MUT_SLICE]  (KILLED = 1 0)"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All discriminating cases passed (matrix ⊇ §8.2 fixtures + mutation A/B/C/D/E/SLICE KILLED, born-hollow 아님)"
  exit 0
else
  echo "✗ Some cases failed"
  exit 1
fi
