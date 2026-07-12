#!/usr/bin/env bash
# tests/scripts/test-check-doc-section-8-9.sh
# CFP-2612 (Epic CFP-2602 G5) Phase 2 — Discriminating self-test for §8.9 런타임 DAST 보안 동적 축 doc-section lint
# (ADR-150 §결정 10). L3 execution-liveness: mutation 을 실제 kill (형식 green 금지).
#
# QADeveloperAgent 가 change-plan §8.10 authoritative matrix + §8.2 fixtures + §8.4 mutation A/B/D/E/F/G
# 를 입력으로 작성. 검증 대상 = scripts/lib/check_doc_section_schema.py check_section_8_9()
# (canonical = ADR-150 §결정 10 pinned interface, DeveloperAgent-CORE 가 verbatim 삽입).
# 선례 = tests/scripts/test-check-doc-section-8-8.sh (verbatim-homolog 구조 — 4기법 → single `dast` 축 축약).
#
# check_section_8_9() 동작 (canonical, 검증 기준):
#  - §8.9 헤딩 부재 → 무검사(return []). §8.6 gap 무관(§8.9 헤딩만 트리거).
#  - §8.9 헤딩 존재 + §8.9.0 헤딩 부재 → fail.
#  - §8.9.0 표 `| dast | (DO|N/A) |` 행 미파싱 → fail.
#  - g_boundary_check token 이 §8.9 region(§8.9 헤딩 ~ 다음 #{1,4} 헤딩) 에 부재 → fail (AC-2c).
#  - dast=DO 시:
#      · §8.9.1 산출물 계약 12 필드(target/attack_surface/scanner_or_harness/payload_class/oracle/
#        repro_seed/execution_budget/pass_condition/status/auth_mode/environment_ref/observed_result) 누락 → fail (AC-2a).
#      · status ∉ {executed,infeasible,natural_na} → fail (AC-2b).
#      · status=infeasible 인데 infeasibility_reason(≥30자) 부재 → fail (AC-2b).
#      · payload_class ∈ {active,destructive} 인데 environment_ref non-prod/ephemeral marker 부재 → fail (AC-6a blast-radius).
#      · attack_surface authenticated(not un-) ∧ auth_mode=unauthenticated ∧ infeasibility_reason 부재 → fail (AC-6b silent FN).
#  - dast=N/A(aggregate) 시: §8.9.x 헤딩 + substantive reason(30자 minimum, NA_85_SUBSTANTIVE_RE) 필수.
#  ★ 정직 천장(ADR-150 §결정3): 게이트는 applicability 레코드·12 필드·status enum·infeasible⟹reason·2 cross-field
#    선언-정합 presence/구조까지만. 검출력(discriminating)/공격표면 열거 완결성/사유타당성/g_boundary_check 준수는
#    강제하지 않음(G3·review·advisory defense-in-depth) — TC-CLEAN-PASS 가 detection 미강제(천장) 실증.
#
# ── CWD 의무 (CFP-2449 gotcha) ────────────────────────────────────────────────
#  check_doc_section_schema.py 는 CWD-상대 스캔(`Path("docs/change-plans").rglob`). argv 무시.
#  → 격리 임시 dir 에 docs/change-plans/cfp-9999-fixture.md 만들고 그 dir 를 CWD 로 python3 호출.
#  cfp 번호 = 9999 (LEGACY_CHANGE_PLAN_CFPS 회피). fixture 는 §1-§11 skeleton 전부 포함 —
#  §8.9 외 사유(필수 섹션 누락 등) fail 0 격리.
#
# ── §8.10 authoritative matrix (matrix ⊇ §8.2 discriminating fixtures 불변식) ──
#  TC-CLEAN-PASS  완전-valid DO 12필드 + 0 검출(observed_result=no vuln) → exit 0 (천장 실증 — detection 미강제)
#  F-DO-MISSING   DO 12필드 중 1개 누락 → exit 1  ↔  완전 → exit 0 (discriminating, MUT-A kill-fixture)
#  F-NO-G-CHECK   g_boundary_check token 부재 → exit 1 (AC-2c, MUT-B kill-fixture)
#  F-STATUS-BAD   status=enum 외 값 → exit 1 (AC-2b, MUT-D kill-fixture)
#  F-INFEAS-NR    status=infeasible + reason 부재 → exit 1  ↔  reason(≥30) → exit 0 (AC-2b, MUT-E kill-fixture)
#  F-ACTIVE-PROD  payload_class=active + environment_ref prod(marker 부재) → exit 1 (AC-6a, MUT-F kill-fixture)
#  F-AUTH-SILENT  attack_surface authenticated + auth_mode=unauthenticated + reason 부재 → exit 1 ↔ reason → exit 0 (AC-6b, MUT-G)
#  F-NA-VAGUE     dast=N/A + §8.9.x vague(<30) → exit 1  ↔  F-NA-SUBSTANTIVE(≥30, 3축) → exit 0 (AC-1b, discriminating)
#  F-8.6-GAP      §8.5(+§8.5.4) → §8.9 gap(§8.6 부재) → §8.9 외 사유 fail 0 → exit 0 (false-positive 0, §8.8 self-test 동형)
#  sibling-guard  check_section_8_9() 부재/미배선 → 명시 FAIL(silent skip 금지)
#  ceiling-honesty  LIVE 실 template §8.9.5 4 잔여 개시 + "완전 봉인" over-claim 부재 (NO fixture-fallback)
#  ※ F-8.8-BLEED(L355 region-slice 무회귀) = 별도 test-check-doc-section-8-8.sh 재구동으로 증명(본 파일 밖).
#
# ── Mutation A/B/D/E/F/G 실 RED 증명 (execution-liveness L3) ────────────────────
#  canonical 6개 check 에 sentinel 주석: MUT-A-DO-FIELDS / MUT-B-G-TOKEN / MUT-D-STATUS-ENUM /
#  MUT-E-INFEAS-REASON / MUT-F-ACTIVE-PROD / MUT-G-AUTH-UNAUTH.
#  각 mutation = $LINT_PY 복사 → sentinel 라인을 동일 들여쓰기 `pass` 로 sed 무력화 → kill-fixture 실행.
#  KILL 판정: original(kill-fixture)=exit 1 AND mutated(kill-fixture)=exit 0 → original≠mutated → KILLED.
#  mutated 가 여전히 exit 1 = check hollow → self-test FAIL(형식 green 차단).
#  (MUT-A-DO-FIELDS sentinel 은 §8.8 L413 과 공유 — sed 가 양쪽 무력화하나 kill-fixture 는 §8.8 헤딩 부재라
#   §8.8 check 는 []; §8.9 MUT-A 무력화만 유효 → KILL 판정 무영향.)
#
# ── 사전 의존 (sibling DeveloperAgent-CORE) ───────────────────────────────────
#  check_section_8_9() 미삽입/미배선 시 → 명시 FAIL 로 sibling-dependency 노출(silent skip 금지).
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

# ── sibling-dependency guard (§8.8 self-test 동형) ──
if [ ! -f "$LINT_PY" ]; then
  echo "✗ FAIL: check_doc_section_schema.py 부재 ($LINT_PY)"
  exit 1
fi
if ! grep -q 'def check_section_8_9' "$LINT_PY"; then
  echo "✗ FAIL: check_doc_section_schema.py 에 check_section_8_9() 부재 (DeveloperAgent-CORE 미삽입 — sibling-dependent, 함수 미삽입, PL 재실행 필요)"
  exit 1
fi
# 추가 guard: main() 미배선(호출 부재) 검출 — 함수만 있고 호출 없으면 §8.9 검사가 실행되지 않아
# 모든 fixture exit 0 → 전 TC false-pass. def 1줄 + main 호출 1줄 => 최소 2 라인 매칭 기대.
if [ "$(grep -c 'check_section_8_9' "$LINT_PY")" -lt 2 ]; then
  echo "✗ FAIL: check_section_8_9() 가 main() 에 미배선 (호출 부재 — 함수 dead-code). PL 재실행 필요"
  exit 1
fi

# ═════════════════════════════════════════════════════════════════════════════
# change-plan §1-§11 skeleton (§8.9 외 사유 fail 0 격리). §8 본문 = per-fixture §8.9.
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

SEC89_HEADER="#### §8.9 DAST 로스터 (런타임 동적 보안 — oracle=attack ⊥ G4 robustness — CONDITIONAL — CFP-2612 / ADR-150)"

# emit_89_table <status> <g|nog>
#   g   → §8.9.0 표 3번째 컬럼에 g_boundary_check token 포함(AC-2c 충족).
#   nog → 3번째 컬럼명·셀에서 g_boundary_check token 제거(AC-2c 위반).
emit_89_table() {
  local status="$1" g="${2:-g}"
  echo "##### §8.9.0 Applicability decision (필수)"
  if [ "$g" = "g" ]; then
    echo "| axis | applicability_status (DO/N/A) | g_boundary_check |"
    echo "|---|:-:|---|"
    echo "| dast | $status | g_boundary_check: soak/restart/replay(G2)·fuzz(G4) 경계 미침범 확인 |"
  else
    echo "| axis | applicability_status (DO/N/A) | boundary_note |"
    echo "|---|:-:|---|"
    echo "| dast | $status | boundary reviewed ok |"
  fi
}

# emit_89_do <omit> <payload> <status> <env> <surface> <auth> <reason>
#   omit    : 누락할 필드명 ("" = 전부 기재)
#   payload : payload_class 값 (passive|active|destructive)
#   status  : status 값 (executed|infeasible|natural_na|bogus...)
#   env     : environment_ref 값 (non-prod marker 유무 제어)
#   surface : attack_surface 값 (authenticated 유무 제어)
#   auth    : auth_mode 값 (unauthenticated|session|token)
#   reason  : no|yes|short (infeasibility_reason 포함 여부/길이)
# ※ 필드 값은 12 필드명을 substring 으로 포함하지 않도록 설계(substring presence 검사 오탐 방지).
emit_89_do() {
  local omit="${1:-}" payload="${2:-active}" status="${3:-executed}"
  local env="${4:-ephemeral staging cluster}" surface="${5:-public unauthenticated endpoint}"
  local auth="${6:-unauthenticated}" reason="${7:-no}"
  echo "##### §8.9.1 dast (DO — 산출물 계약)"
  [ "$omit" = "target" ]             || echo "- target: order-api deployed service"
  [ "$omit" = "attack_surface" ]     || echo "- attack_surface: $surface"
  [ "$omit" = "scanner_or_harness" ] || echo "- scanner_or_harness: ZAP baseline passive scan"
  [ "$omit" = "payload_class" ]      || echo "- payload_class: $payload"
  [ "$omit" = "oracle" ]             || echo "- oracle: SQL injection execution as defect"
  [ "$omit" = "repro_seed" ]         || echo "- repro_seed: fixed request vector corpus"
  [ "$omit" = "execution_budget" ]   || echo "- execution_budget: 500 requests"
  [ "$omit" = "pass_condition" ]     || echo "- pass_condition: 0 confirmed high severity"
  [ "$omit" = "status" ]             || echo "- status: $status"
  [ "$omit" = "auth_mode" ]          || echo "- auth_mode: $auth"
  [ "$omit" = "environment_ref" ]    || echo "- environment_ref: $env"
  [ "$omit" = "observed_result" ]    || echo "- observed_result: 0 alerts / no vuln detected"
  if [ "$reason" = "yes" ]; then
    echo "- infeasibility_reason: 인증 세션 토큰 조달 불가로 해당 인증 표면 능동 스캔을 이번 주기에는 수행 불가함"
  elif [ "$reason" = "short" ]; then
    echo "- infeasibility_reason: 짧음"
  fi
}

# emit_89_5_ceiling  — 정직 천장(§8.9.5). fixture fidelity 용(lint 미검사, TC-CLEAN-PASS 에만 포함).
emit_89_5_ceiling() {
  echo "##### §8.9.5 정직 천장"
  echo "- (i) 검출력 = G3 위임 (ii) 완결성 = review 보강 (iii) 사유타당성 = review 판정 (iv) g_boundary_check presence != 실준수 (게이트 강제 아님)"
}

# emit_89_x_na <substantive|vague>  — aggregate dast=N/A 명시
emit_89_x_na() {
  echo "##### §8.9.x N/A 명시 (dast 미적용 — runtime-inert)"
  if [ "$1" = "vague" ]; then
    echo "N/A — 짧음"
  else
    echo "N/A — codeforge 자체는 배포되는 서비스가 아니라 문서·플러그인 정의라 deployable service 0 이고 상주 실행 공격 표면·비신뢰 입력 수신·기동 가능 3-요건 중 상주 실행이 결여되어 자연 N/A. 검증 채널: check_section_8_9 self-test. 면제 분류: plugin-meta-na"
  fi
}

# ── CFP-2628 born-hollow fixtures (present-but-blank field: 콜론 뒤 same-line 공백 + 다음 줄 내용) ──
#   버그: 값-캡처 `<field>:\s*(.+)` 가 re.MULTILINE 에서 `\s*` 로 개행을 삼켜 다음 줄을 값으로 흡수(false-fill).
#   fix: same-line `<field>:[ \t]*(.*)$` (형제 §8.10 activation_test_ref/on_state_assertion 이미 안전 idiom).
#   각 emit = blank field 직후 줄에 흡수-대상 내용 배치. 12 필드 전부 present + 단일 원인 격리 → born-hollow 거동만 차이.

# emit_89_do_hollow_reason — status=infeasible + blank infeasibility_reason + 다음 줄 ≥30자 사유.
#   fixed → reason_ok=False → MUT-E fire → exit 1(정탐).  buggy → 다음 줄 흡수 → reason_ok=True → exit 0(hollow).
emit_89_do_hollow_reason() {
  echo "##### §8.9.1 dast (DO — 산출물 계약)"
  echo "- target: order-api deployed service"
  echo "- attack_surface: public unauthenticated endpoint"
  echo "- scanner_or_harness: ZAP baseline passive scan"
  echo "- payload_class: passive"
  echo "- oracle: SQL injection execution as defect"
  echo "- repro_seed: fixed request vector corpus"
  echo "- execution_budget: 500 requests"
  echo "- pass_condition: 0 confirmed high severity"
  echo "- status: infeasible"
  echo "- auth_mode: unauthenticated"
  echo "- environment_ref: local sandbox"
  echo "- observed_result: 0 alerts / no vuln detected"
  echo "- infeasibility_reason:"
  echo "인증 세션 토큰 조달 불가로 해당 인증 표면 능동 스캔을 이번 주기에는 수행 불가함으로 판단됨"
}

# emit_89_do_hollow_env — payload=active + blank environment_ref + 다음 줄 nonprod marker(ephemeral/staging/sandbox...).
#   fixed → env_val='' → NONPROD 미매치 → AC-6a blast-radius fire → exit 1(정탐).  buggy → 다음 줄 흡수 → NONPROD 매치 → exit 0(hollow, 보안 FN).
emit_89_do_hollow_env() {
  echo "##### §8.9.1 dast (DO — 산출물 계약)"
  echo "- target: order-api deployed service"
  echo "- attack_surface: public unauthenticated endpoint"
  echo "- scanner_or_harness: ZAP baseline passive scan"
  echo "- payload_class: active"
  echo "- oracle: SQL injection execution as defect"
  echo "- repro_seed: fixed request vector corpus"
  echo "- execution_budget: 500 requests"
  echo "- pass_condition: 0 confirmed high severity"
  echo "- status: executed"
  echo "- auth_mode: unauthenticated"
  echo "- observed_result: 0 alerts / no vuln detected"
  echo "- environment_ref:"
  echo "ephemeral staging cluster throwaway sandbox used only for this scan run"
}

# emit_89_do_hollow_surface (★역-polarity) — blank attack_surface + 다음 줄 authenticated(not 'un') + auth_mode=unauthenticated.
#   buggy → surface_val 이 다음 줄 'authenticated' 흡수 → MUT-G phantom fire → exit 1.
#   fixed → surface_val='' → 미fire → exit 0(다른 fail 0 = clean). infeasibility_reason/environment_ref 와 polarity 반대.
emit_89_do_hollow_surface() {
  echo "##### §8.9.1 dast (DO — 산출물 계약)"
  echo "- target: order-api deployed service"
  echo "- attack_surface:"
  echo "authenticated admin console reachable behind the login boundary only"
  echo "- scanner_or_harness: ZAP baseline passive scan"
  echo "- payload_class: passive"
  echo "- oracle: SQL injection execution as defect"
  echo "- repro_seed: fixed request vector corpus"
  echo "- execution_budget: 500 requests"
  echo "- pass_condition: 0 confirmed high severity"
  echo "- status: executed"
  echo "- auth_mode: unauthenticated"
  echo "- environment_ref: local sandbox"
  echo "- observed_result: 0 alerts / no vuln detected"
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
# TC-CLEAN-PASS (천장 실증, F-DAST-CLEAN-PASS) — 완전-valid DO 12필드 + 0 검출 → exit 0
#   게이트가 detection 을 강제하지 않음을 실증(INV-G5-4 천장). ★ 본 self-test 의 핵심 정직 TC.
#   payload=active + env=ephemeral(marker) → blast-radius 통과. attack_surface unauthenticated →
#   AC-6b 미트리거. status=executed. observed_result="no vuln detected"(0 검출)여도 exit 0.
# ═════════════════════════════════════════════════════════════════════════════
tc_clean_body() {
  emit_skeleton_head
  echo "$SEC89_HEADER"
  emit_89_table DO g
  emit_89_do "" active executed "ephemeral staging cluster" "public unauthenticated endpoint" unauthenticated no
  emit_89_5_ceiling
  emit_skeleton_tail
}
EC_CLEAN=$(run_case tc_clean_body 0 "TC-CLEAN-PASS-ceiling" "완전-valid DO 12필드 + 0 검출(no vuln) → exit 0 (detection 미강제 천장)" | tail -1)

# ═════════════════════════════════════════════════════════════════════════════
# F-DO-MISSING-FIELD — DO 레코드 observed_result 누락 → exit 1 (AC-2a, MUT-A kill-fixture)
#   payload=passive(blast-radius 무관) + executed + unauth → 유일 실패 = 필드 누락(단일 원인 격리).
# ═════════════════════════════════════════════════════════════════════════════
fdo_miss_body() {
  emit_skeleton_head
  echo "$SEC89_HEADER"
  emit_89_table DO g
  emit_89_do "observed_result" passive executed "local sandbox" "public unauthenticated endpoint" unauthenticated no
  emit_skeleton_tail
}
fdo_ok_body() {
  emit_skeleton_head
  echo "$SEC89_HEADER"
  emit_89_table DO g
  emit_89_do "" passive executed "local sandbox" "public unauthenticated endpoint" unauthenticated no
  emit_skeleton_tail
}
EC_FDO_MISS=$(run_case fdo_miss_body 1 "F-DO-MISSING-FIELD" "DO observed_result 누락 → exit 1 (AC-2a)" | tail -1)
EC_FDO_OK=$(run_case fdo_ok_body 0 "F-DO-COMPLETE" "DO 12필드 완전 → exit 0" | tail -1)
assert_discriminating "$EC_FDO_MISS" "$EC_FDO_OK" "F-DO miss=$EC_FDO_MISS vs complete"

# ═════════════════════════════════════════════════════════════════════════════
# F-NO-G-CHECK — g_boundary_check token 부재 → exit 1 (AC-2c, MUT-B kill-fixture)
#   dast=N/A + §8.9.x substantive + nog → 유일 실패 = g_boundary_check 부재(단일 원인).
# ═════════════════════════════════════════════════════════════════════════════
fnog_body() {
  emit_skeleton_head
  echo "$SEC89_HEADER"
  emit_89_table N/A nog
  emit_89_x_na substantive
  emit_skeleton_tail
}
EC_FNOG=$(run_case fnog_body 1 "F-NO-G-CHECK" "g_boundary_check token 부재 → exit 1 (AC-2c)" | tail -1)

# ═════════════════════════════════════════════════════════════════════════════
# F-STATUS-BAD-ENUM — status=bogus(enum 외) → exit 1 (AC-2b, MUT-D kill-fixture)
# ═════════════════════════════════════════════════════════════════════════════
fstatus_body() {
  emit_skeleton_head
  echo "$SEC89_HEADER"
  emit_89_table DO g
  emit_89_do "" passive bogus "local sandbox" "public unauthenticated endpoint" unauthenticated no
  emit_skeleton_tail
}
EC_FSTATUS=$(run_case fstatus_body 1 "F-STATUS-BAD-ENUM" "status=bogus(enum 외) → exit 1 (AC-2b)" | tail -1)

# ═════════════════════════════════════════════════════════════════════════════
# F-INFEASIBLE-NO-REASON — status=infeasible + reason 부재 → exit 1 (AC-2b, MUT-E kill-fixture)
#   ↔ reason(≥30) 존재 → exit 0 (discriminating)
# ═════════════════════════════════════════════════════════════════════════════
finfeas_body() {
  emit_skeleton_head
  echo "$SEC89_HEADER"
  emit_89_table DO g
  emit_89_do "" passive infeasible "local sandbox" "public unauthenticated endpoint" unauthenticated no
  emit_skeleton_tail
}
finfeas_ok_body() {
  emit_skeleton_head
  echo "$SEC89_HEADER"
  emit_89_table DO g
  emit_89_do "" passive infeasible "local sandbox" "public unauthenticated endpoint" unauthenticated yes
  emit_skeleton_tail
}
EC_FINF=$(run_case finfeas_body 1 "F-INFEASIBLE-NO-REASON" "status=infeasible + reason 부재 → exit 1 (AC-2b)" | tail -1)
EC_FINF_OK=$(run_case finfeas_ok_body 0 "F-INFEASIBLE-WITH-REASON" "status=infeasible + reason(≥30) → exit 0" | tail -1)
assert_discriminating "$EC_FINF" "$EC_FINF_OK" "F-INFEAS noreason=$EC_FINF vs reason"

# ═════════════════════════════════════════════════════════════════════════════
# F-ACTIVE-PROD — payload_class=active + environment_ref production(marker 부재) → exit 1 (AC-6a, MUT-F)
#   ↔ TC-CLEAN-PASS(active + ephemeral marker) = exit 0 discriminating.
# ═════════════════════════════════════════════════════════════════════════════
factive_body() {
  emit_skeleton_head
  echo "$SEC89_HEADER"
  emit_89_table DO g
  emit_89_do "" active executed "production cluster" "public unauthenticated endpoint" unauthenticated no
  emit_skeleton_tail
}
EC_FACT=$(run_case factive_body 1 "F-ACTIVE-PROD" "payload=active + env=production(marker 부재) → exit 1 (AC-6a blast-radius)" | tail -1)
assert_discriminating "$EC_FACT" "$EC_CLEAN" "F-ACTIVE-PROD prod=$EC_FACT vs clean(ephemeral marker)"

# ═════════════════════════════════════════════════════════════════════════════
# F-AUTH-UNAUTH-SILENT — attack_surface authenticated + auth_mode=unauthenticated + reason 부재 → exit 1 (AC-6b, MUT-G)
#   ↔ 동일 조건 + reason 존재 → exit 0 (discriminating)
# ═════════════════════════════════════════════════════════════════════════════
fauth_body() {
  emit_skeleton_head
  echo "$SEC89_HEADER"
  emit_89_table DO g
  emit_89_do "" passive executed "local sandbox" "authenticated admin endpoint" unauthenticated no
  emit_skeleton_tail
}
fauth_ok_body() {
  emit_skeleton_head
  echo "$SEC89_HEADER"
  emit_89_table DO g
  emit_89_do "" passive executed "local sandbox" "authenticated admin endpoint" unauthenticated yes
  emit_skeleton_tail
}
EC_FAUTH=$(run_case fauth_body 1 "F-AUTH-UNAUTH-SILENT" "authenticated ∧ auth_mode=unauthenticated ∧ reason 부재 → exit 1 (AC-6b silent FN)" | tail -1)
EC_FAUTH_OK=$(run_case fauth_ok_body 0 "F-AUTH-WITH-REASON" "authenticated ∧ unauthenticated + reason(≥30) → exit 0" | tail -1)
assert_discriminating "$EC_FAUTH" "$EC_FAUTH_OK" "F-AUTH silent=$EC_FAUTH vs reason"

# ═════════════════════════════════════════════════════════════════════════════
# F-NA-VAGUE ↔ F-NA-SUBSTANTIVE — dast=N/A + §8.9.x vague(<30) → exit 1 ↔ substantive(≥30, 3축) → exit 0 (AC-1b)
# ═════════════════════════════════════════════════════════════════════════════
fna_vague_body() {
  emit_skeleton_head
  echo "$SEC89_HEADER"
  emit_89_table N/A g
  emit_89_x_na vague
  emit_skeleton_tail
}
fna_sub_body() {
  emit_skeleton_head
  echo "$SEC89_HEADER"
  emit_89_table N/A g
  emit_89_x_na substantive
  emit_skeleton_tail
}
EC_FNA_V=$(run_case fna_vague_body 1 "F-NA-VAGUE" "dast=N/A + §8.9.x reason <30자(vague) → exit 1 (AC-1b)" | tail -1)
EC_FNA_S=$(run_case fna_sub_body 0 "F-NA-SUBSTANTIVE" "dast=N/A + §8.9.x substantive 30자+(3축) → exit 0" | tail -1)
assert_discriminating "$EC_FNA_V" "$EC_FNA_S" "F-NA vague=$EC_FNA_V vs substantive"

# ═════════════════════════════════════════════════════════════════════════════
# F-8.6-GAP — §8.5(+§8.5.4) → §8.9 gap(§8.6 부재) → §8.9 외 사유 fail 0 → exit 0 (false-positive 0)
#   §8.8 self-test TC7 동형: §8.9 헤딩 존재만 트리거(§8.6 존재 전제 안 함) → gap false-positive 없음.
# ═════════════════════════════════════════════════════════════════════════════
f86gap_body() {
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
  # §8.6 의도적 부재(gap) → §8.9 로 점프
  echo "$SEC89_HEADER"
  emit_89_table N/A g
  emit_89_x_na substantive
  emit_skeleton_tail
}
EC_86GAP=$(run_case f86gap_body 0 "F-8.6-GAP" "§8.5.4 → §8.9 gap(§8.6 부재) → §8.9 외 사유 fail 0 → exit 0" | tail -1)

# ═════════════════════════════════════════════════════════════════════════════
# CFP-2628 born-hollow (present-but-blank field false-fill 봉인) — 3 field
#   ★ RED-first: unfixed(buggy) checker 로 돌리면 아래 run_case/assert 는 FAIL(RED) 이 정상 —
#     born-hollow 이 다음 줄을 흡수해 정탐 못 함(reason/env exit 0, surface exit 1 phantom).
#     Dev 가 4 site 를 `[ \t]*(.*)$` idiom 으로 fix 하면 GREEN. 테스트 약화 금지.
#   각 케이스 = born-hollow(다음 줄 흡수) vs same-line 정상 anchor(EC_*) 로 discriminating.
# ═════════════════════════════════════════════════════════════════════════════
fhollow_reason_body()  { emit_skeleton_head; echo "$SEC89_HEADER"; emit_89_table DO g; emit_89_do_hollow_reason;  emit_skeleton_tail; }
fhollow_env_body()     { emit_skeleton_head; echo "$SEC89_HEADER"; emit_89_table DO g; emit_89_do_hollow_env;     emit_skeleton_tail; }
fhollow_surface_body() { emit_skeleton_head; echo "$SEC89_HEADER"; emit_89_table DO g; emit_89_do_hollow_surface; emit_skeleton_tail; }

# (AC-1a→AC-2a) infeasibility_reason born-hollow → fixed exit 1(정탐) ↔ same-line reason(EC_FINF_OK=0)
EC_HOLLOW_REASON=$(run_case fhollow_reason_body 1 "F-HOLLOW-REASON(CFP-2628)" "blank infeasibility_reason + 다음 줄 ≥30자 흡수 → fixed exit 1(정탐)" | tail -1)
assert_discriminating "$EC_HOLLOW_REASON" "$EC_FINF_OK" "F-HOLLOW-REASON hollow=$EC_HOLLOW_REASON vs same-line reason(EC_FINF_OK)"

# (AC-1c→AC-2c, 보안 FN 봉인) environment_ref born-hollow → fixed exit 1(blast-radius 미격리 정탐) ↔ same-line env(EC_CLEAN=0)
EC_HOLLOW_ENV=$(run_case fhollow_env_body 1 "F-HOLLOW-ENV(CFP-2628)" "payload=active + blank environment_ref + 다음 줄 nonprod marker 흡수 → fixed exit 1(AC-6a 정탐)" | tail -1)
assert_discriminating "$EC_HOLLOW_ENV" "$EC_CLEAN" "F-HOLLOW-ENV hollow=$EC_HOLLOW_ENV vs same-line env(EC_CLEAN)"

# (AC-1d→AC-2d, ★역-polarity) attack_surface born-hollow → fixed exit 0(미fire 정탐) ↔ same-line authenticated(EC_FAUTH=1)
#   polarity-agnostic: fixed=0 ↔ anchor=1 이 discriminating(두 exit 상이). buggy 였다면 hollow=1(phantom)=anchor → 비-discriminating(RED).
EC_HOLLOW_SURFACE=$(run_case fhollow_surface_body 0 "F-HOLLOW-SURFACE(CFP-2628)" "blank attack_surface + 다음 줄 authenticated → fixed exit 0(미fire 정탐)" | tail -1)
assert_discriminating "$EC_HOLLOW_SURFACE" "$EC_FAUTH" "F-HOLLOW-SURFACE hollow=$EC_HOLLOW_SURFACE vs same-line authenticated(EC_FAUTH)"

# ── test_ceiling_honesty_disclosed (doc-presence — LIVE 회귀가드, NO fixture-fallback) ──
#   §8.8 self-test 의 ceiling_honesty_check 을 §8.9.5 대상으로 verbatim mirror.
#   실 template(plugins/codeforge-design/templates/change-plan.md) §8.9.5 를 직접 검증한다.
#   4 잔여(검출력 / 완결성 / 타당성 / g_boundary_check) 존재 +
#   "완전 봉인" hard-claim 부재('"완전 봉인" ... 금지' 는 honest disclaimer — 금지 문맥 제외).
#   실 template 부재/§8.9.5 미존재 = FAIL(회귀 표면화 — hollow fixture fallback 폐지, skip-with-note 금지).
ceiling_honesty_check() {
  local target="$REPO_ROOT/plugins/codeforge-design/templates/change-plan.md" src="change-plan.md 실 템플릿"
  if [ ! -f "$target" ] || ! grep -q '§8\.9\.5' "$target"; then
    echo "✗ FAIL: test_ceiling_honesty_disclosed — 실 템플릿($target) 부재 또는 §8.9.5 미존재 (LIVE 회귀가드 — hollow fixture fallback 폐지)" >&2
    tally_fail
    return
  fi
  local ok=1
  for tok in "검출력" "완결성" "타당성" "g_boundary_check"; do
    grep -q "$tok" "$target" || { echo "  ceiling honesty: '$tok' 부재 ($src)" >&2; ok=0; }
  done
  # over-claim 검출: "완전 봉인" 을 hard-claim 하면 FAIL. 단 "완전 봉인 ... 금지"(honest disclaimer)는 허용
  #   → "완전 봉인" 이 있는데 그 줄에 "금지" 가 없으면 over-claim.
  if grep "완전 봉인" "$target" | grep -qv "금지"; then
    echo "  ceiling honesty: '완전 봉인' hard-claim(금지 문맥 아님) 존재 = over-claim ($src)" >&2; ok=0
  fi
  if [ "$ok" = "1" ]; then
    echo "✓ PASS: test_ceiling_honesty_disclosed — 실 템플릿 §8.9.5 4 잔여 개시 + '완전 봉인' hard-claim 부재 ($src)" >&2
    tally_pass
  else
    echo "✗ FAIL: test_ceiling_honesty_disclosed — ceiling honesty 개시 미충족 ($src)" >&2
    tally_fail
  fi
}
ceiling_honesty_check

# ═════════════════════════════════════════════════════════════════════════════
# Mutation A/B/D/E/F/G 실 RED kill (execution-liveness L3)
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

MUT_A=$(run_mutation_kill "MUT-A-DO-FIELDS"     fdo_miss_body "Mutation-A(DO-fields)")      # kill-fixture = F-DO-MISSING-FIELD
MUT_B=$(run_mutation_kill "MUT-B-G-TOKEN"       fnog_body     "Mutation-B(g-token)")        # kill-fixture = F-NO-G-CHECK
MUT_D=$(run_mutation_kill "MUT-D-STATUS-ENUM"   fstatus_body  "Mutation-D(status-enum)")    # kill-fixture = F-STATUS-BAD-ENUM
MUT_E=$(run_mutation_kill "MUT-E-INFEAS-REASON" finfeas_body  "Mutation-E(infeas-reason)")  # kill-fixture = F-INFEASIBLE-NO-REASON
MUT_F=$(run_mutation_kill "MUT-F-ACTIVE-PROD"   factive_body  "Mutation-F(active-prod)")    # kill-fixture = F-ACTIVE-PROD
MUT_G=$(run_mutation_kill "MUT-G-AUTH-UNAUTH"   fauth_body    "Mutation-G(auth-unauth)")    # kill-fixture = F-AUTH-UNAUTH-SILENT

# ═════════════════════════════════════════════════════════════════════════════
# CFP-2628 capture-line mutation (ADR-136 L3 — capture 라인 자체를 target)
#   기존 MUT-E/G 는 `fails.append` 소비 라인만 sed → `\s*(.+)`↔`[ \t]*(.*)$` 를 미구별(그래서 born-hollow 가
#   self-test 통과해 landed). 신규 = capture 라인 `<field>:[ \t]*(.*)$` 를 buggy `<field>:\s*(.+)` 로
#   python 정확 치환(sed 백슬래시 함정 회피) 후 born-hollow fixture 재실행 → orig(fixed) ≠ mutated(buggy) = KILLED.
#   sentinel = capture 라인(소비 라인 아님). polarity-agnostic(orig≠mut). fixed idiom 부재(Dev 미수정/born-hollow
#   잔존) → python exit 3 → 명시 FAIL(=RED).
# ═════════════════════════════════════════════════════════════════════════════
exec_fixture() {  # <body_fn> <lint_py> → exit code echo(no tally). polarity-agnostic 비교용 raw runner.
  local body_fn="$1" lint="$2"
  local T; T=$(mktemp -d)
  mkdir -p "$T/docs/change-plans"
  "$body_fn" > "$T/docs/change-plans/cfp-9999-fixture.md"
  local ec=0
  ( cd "$T" && "$PY" "$lint" >/dev/null 2>&1 ) || ec=$?
  rm -rf "$T"
  echo "$ec"
}
run_capture_line_mutation() {  # <field> <body_fn> <mut_name>
  local field="$1" body_fn="$2" mut_name="$3"
  local MUT_DIR; MUT_DIR=$(mktemp -d)
  local MUT_PY="$MUT_DIR/check_doc_section_schema.py"
  local rc=0
  "$PY" - "$LINT_PY" "$field" "$MUT_PY" <<'PYEOF' || rc=$?
import sys
lint_py, field, out = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(lint_py, encoding="utf-8").read()
old = field + r":[ \t]*(.*)$"   # fixed idiom (same-line only)
new = field + r":\s*(.+)"        # buggy idiom (개행 흡수)
if old not in src:
    sys.exit(3)                  # fixed idiom 부재 → mutation 적용 불가 (Dev 미수정/born-hollow 잔존)
open(out, "w", encoding="utf-8").write(src.replace(old, new))
sys.exit(0)
PYEOF
  if [ "$rc" != "0" ]; then
    echo "✗ FAIL: $mut_name — capture-line fixed idiom '$field:[ \\t]*(.*)\$' 부재 (Dev 미수정/born-hollow 잔존 — mutation 적용 불가, RED)" >&2
    tally_fail; rm -rf "$MUT_DIR"; echo "NA NA"; return
  fi
  if ! "$PY" -c "import py_compile,sys; py_compile.compile(sys.argv[1], doraise=True)" "$MUT_PY" >/dev/null 2>&1; then
    echo "✗ FAIL: $mut_name — mutated lint 문법 오류" >&2
    tally_fail; rm -rf "$MUT_DIR"; echo "NA NA"; return
  fi
  local ec_orig ec_mut
  ec_orig=$(exec_fixture "$body_fn" "$LINT_PY")
  ec_mut=$(exec_fixture "$body_fn" "$MUT_PY")
  if [ "$ec_orig" != "$ec_mut" ]; then
    echo "✓ PASS: $mut_name KILLED (capture-line) — orig(exit=$ec_orig) ≠ mutated(exit=$ec_mut) polarity-agnostic (born-hollow 구별)" >&2
    tally_pass
  else
    echo "✗ FAIL: $mut_name SURVIVED (capture-line) — orig(exit=$ec_orig) == mutated(exit=$ec_mut) = born-hollow 미구별(hollow)" >&2
    tally_fail
  fi
  rm -rf "$MUT_DIR"
  echo "$ec_orig $ec_mut"
}
CMUT_REASON=$(run_capture_line_mutation  "infeasibility_reason" fhollow_reason_body  "CaptureMut-infeasibility_reason")  # born-hollow = fhollow_reason_body
CMUT_ENV=$(run_capture_line_mutation     "environment_ref"      fhollow_env_body     "CaptureMut-environment_ref")       # born-hollow = fhollow_env_body
CMUT_SURFACE=$(run_capture_line_mutation "attack_surface"       fhollow_surface_body "CaptureMut-attack_surface")        # born-hollow = fhollow_surface_body (역-polarity)

# ═════════════════════════════════════════════════════════════════════════════
# CFP-2636 (Epic CFP-2602 enum-field 값-존재 gap 봉인 / ADR-150 §결정4) — payload_class/auth_mode/status
#   value-존재(present-but-blank/absent → fail-closed) + enum-validity(∉ enum → fail).
#   ★ 핵심 보안 FN: payload_class blank → 이전 `\s*(\S+)` 개행 흡수 → '-'(다음 줄 marker) 캡처 → ∉ ACTIVE →
#     blast-radius 검사 SKIP → active/destructive 를 production 격리 없이 통과(exit 0). fix = _capture_field
#     same-line 앵커 + value-존재 fail-closed. RED(unfixed): 아래 F-PAYLOAD-BLANK 는 exit 0(=FAIL RED). fix 후 exit 1.
#   discriminating: F-PAYLOAD-BLANK(exit1) ⊥ TC-PASSIVE-CLEAN(valid passive exit0, 정직천장 INV-G5-4 무침범).
# ═════════════════════════════════════════════════════════════════════════════

# emit_89_do_blank_payload — payload_class BLANK(콜론 뒤 same-line 무값) + env=production(marker 부재) + 12필드 present.
#   unfixed: payload_val 이 개행 넘어 '-'(다음 줄 marker) 흡수 → ∉ ACTIVE → blast-radius skip → exit 0(보안 FN, RED).
#   fixed:   payload_val=None → MUT-H fire → exit 1(값-존재 봉인). 단일 원인 격리(그 외 12필드 valid).
emit_89_do_blank_payload() {
  echo "##### §8.9.1 dast (DO — 산출물 계약)"
  echo "- target: order-api deployed service"
  echo "- attack_surface: public unauthenticated endpoint"
  echo "- scanner_or_harness: ZAP baseline passive scan"
  echo "- payload_class:"
  echo "- oracle: SQL injection execution as defect"
  echo "- repro_seed: fixed request vector corpus"
  echo "- execution_budget: 500 requests"
  echo "- pass_condition: 0 confirmed high severity"
  echo "- status: executed"
  echo "- auth_mode: unauthenticated"
  echo "- environment_ref: production cluster"
  echo "- observed_result: 0 alerts / no vuln detected"
}
# emit_89_do_blank_auth — auth_mode BLANK + 그 외 valid. fixed → auth_val=None → MUT-J fire → exit 1.
emit_89_do_blank_auth() {
  echo "##### §8.9.1 dast (DO — 산출물 계약)"
  echo "- target: order-api deployed service"
  echo "- attack_surface: public unauthenticated endpoint"
  echo "- scanner_or_harness: ZAP baseline passive scan"
  echo "- payload_class: passive"
  echo "- oracle: SQL injection execution as defect"
  echo "- repro_seed: fixed request vector corpus"
  echo "- execution_budget: 500 requests"
  echo "- pass_condition: 0 confirmed high severity"
  echo "- status: executed"
  echo "- auth_mode:"
  echo "- environment_ref: local sandbox"
  echo "- observed_result: 0 alerts / no vuln detected"
}
# emit_89_do_blank_status — status BLANK + 그 외 valid. fixed → status_val=None → MUT-K fire → exit 1.
emit_89_do_blank_status() {
  echo "##### §8.9.1 dast (DO — 산출물 계약)"
  echo "- target: order-api deployed service"
  echo "- attack_surface: public unauthenticated endpoint"
  echo "- scanner_or_harness: ZAP baseline passive scan"
  echo "- payload_class: passive"
  echo "- oracle: SQL injection execution as defect"
  echo "- repro_seed: fixed request vector corpus"
  echo "- execution_budget: 500 requests"
  echo "- pass_condition: 0 confirmed high severity"
  echo "- status:"
  echo "- auth_mode: unauthenticated"
  echo "- environment_ref: local sandbox"
  echo "- observed_result: 0 alerts / no vuln detected"
}

# ── TC-PASSIVE-CLEAN (정직 천장, INV-G5-4) — valid passive + auth_mode=session(valid enum) + 0검출 → exit 0 ──
tc_passive_clean_body() {
  emit_skeleton_head; echo "$SEC89_HEADER"; emit_89_table DO g
  emit_89_do "" passive executed "local sandbox" "public unauthenticated endpoint" session no
  emit_89_5_ceiling; emit_skeleton_tail
}
EC_PASSIVE_CLEAN=$(run_case tc_passive_clean_body 0 "TC-PASSIVE-CLEAN(CFP-2636)" "valid passive + auth_mode=session + 0검출 → exit 0 (정직천장 INV-G5-4 — value-존재가 detection-forcing 으로 안 번짐)" | tail -1)

# ── F-PAYLOAD-BLANK — payload_class blank + env=production → exit 1 (이전 exit 0 보안 FN) ⊥ TC-PASSIVE-CLEAN ──
fpayload_blank_body() { emit_skeleton_head; echo "$SEC89_HEADER"; emit_89_table DO g; emit_89_do_blank_payload; emit_skeleton_tail; }
EC_PAYLOAD_BLANK=$(run_case fpayload_blank_body 1 "F-PAYLOAD-BLANK(CFP-2636)" "payload_class blank + env=production → exit 1 (AC-1 blast-radius 우회 봉인, 이전 exit 0 보안 FN)" | tail -1)
assert_discriminating "$EC_PAYLOAD_BLANK" "$EC_PASSIVE_CLEAN" "F-PAYLOAD-BLANK blank=$EC_PAYLOAD_BLANK vs passive-clean (FN 봉인 ⊥ FP 무유발 INV-1)"

# ── F-PAYLOAD-ENUM — payload_class=banana(오타) → exit 1 (이전 silent pass) ⊥ TC-PASSIVE-CLEAN ──
fpayload_enum_body() { emit_skeleton_head; echo "$SEC89_HEADER"; emit_89_table DO g; emit_89_do "" banana executed "local sandbox" "public unauthenticated endpoint" unauthenticated no; emit_skeleton_tail; }
EC_PAYLOAD_ENUM=$(run_case fpayload_enum_body 1 "F-PAYLOAD-ENUM(CFP-2636)" "payload_class=banana(enum 외) → exit 1 (AC-2 enum-validity, 이전 silent pass)" | tail -1)
assert_discriminating "$EC_PAYLOAD_ENUM" "$EC_PASSIVE_CLEAN" "F-PAYLOAD-ENUM banana=$EC_PAYLOAD_ENUM vs passive-clean"

# ── F-AUTH-BLANK — auth_mode blank → exit 1 (숨은 FN 봉인) ──
fauth_blank_body() { emit_skeleton_head; echo "$SEC89_HEADER"; emit_89_table DO g; emit_89_do_blank_auth; emit_skeleton_tail; }
EC_AUTH_BLANK=$(run_case fauth_blank_body 1 "F-AUTH-BLANK(CFP-2636)" "auth_mode blank → exit 1 (AC-4 값-존재, 이전 숨은 FN)" | tail -1)
assert_discriminating "$EC_AUTH_BLANK" "$EC_PASSIVE_CLEAN" "F-AUTH-BLANK blank=$EC_AUTH_BLANK vs passive-clean"

# ── F-AUTH-ENUM — auth_mode=cookie(무효) → exit 1 ──
fauth_enum_body() { emit_skeleton_head; echo "$SEC89_HEADER"; emit_89_table DO g; emit_89_do "" passive executed "local sandbox" "public unauthenticated endpoint" cookie no; emit_skeleton_tail; }
EC_AUTH_ENUM=$(run_case fauth_enum_body 1 "F-AUTH-ENUM(CFP-2636)" "auth_mode=cookie(enum 외) → exit 1 (AC-4 enum-validity)" | tail -1)
assert_discriminating "$EC_AUTH_ENUM" "$EC_PASSIVE_CLEAN" "F-AUTH-ENUM cookie=$EC_AUTH_ENUM vs passive-clean"

# ── F-STATUS-BLANK-89 — §8.9.1 status blank → exit 1 (값-존재 강제) ──
fstatus_blank_body() { emit_skeleton_head; echo "$SEC89_HEADER"; emit_89_table DO g; emit_89_do_blank_status; emit_skeleton_tail; }
EC_STATUS_BLANK_89=$(run_case fstatus_blank_body 1 "F-STATUS-BLANK-89(CFP-2636)" "§8.9.1 status blank → exit 1 (AC-5 값-존재)" | tail -1)
assert_discriminating "$EC_STATUS_BLANK_89" "$EC_PASSIVE_CLEAN" "F-STATUS-BLANK-89 blank=$EC_STATUS_BLANK_89 vs passive-clean"

# ── AC-6b-PRESERVE — attack_surface authenticated + auth_mode=session → exit 0 (session=실 auth → AC-6b 미발동, FN 아님) ⊥ F-AUTH-UNAUTH-SILENT ──
ac6b_preserve_body() { emit_skeleton_head; echo "$SEC89_HEADER"; emit_89_table DO g; emit_89_do "" passive executed "local sandbox" "authenticated admin endpoint" session no; emit_skeleton_tail; }
EC_AC6B_PRESERVE=$(run_case ac6b_preserve_body 0 "AC-6b-PRESERVE(CFP-2636)" "attack_surface authenticated + auth_mode=session → exit 0 (session=실 auth, AC-6b 미발동 — §3.7 의미 보존)" | tail -1)
assert_discriminating "$EC_AC6B_PRESERVE" "$EC_FAUTH" "AC-6b-PRESERVE session=$EC_AC6B_PRESERVE vs unauthenticated-silent(EC_FAUTH — INV-4 AC-6b 보존)"

# ── F-ANCHOR-NOSWALLOW — payload blank fail 메시지가 blank 지목('-' 아님, same-line 앵커 개행 미흡수 실증, AC-3) ──
anchor_noswallow_check() {
  local T; T=$(mktemp -d); mkdir -p "$T/docs/change-plans"
  fpayload_blank_body > "$T/docs/change-plans/cfp-9999-fixture.md"
  local out; out=$( cd "$T" && "$PY" "$LINT_PY" 2>&1 ); rm -rf "$T"
  # 정탐: present-but-blank 메시지 존재 AND 개행 흡수한 "enum 위반 '-'" phantom 부재.
  if echo "$out" | grep -q "payload_class present-but-blank" && ! echo "$out" | grep -qF "enum 위반 '-'"; then
    echo "✓ PASS: F-ANCHOR-NOSWALLOW(CFP-2636) — fail 메시지가 blank(present-but-blank) 지목, 개행 흡수 '-' phantom 부재 (AC-3 same-line 앵커)" >&2
    tally_pass
  else
    echo "✗ FAIL: F-ANCHOR-NOSWALLOW(CFP-2636) — 개행 흡수 phantom 또는 present-but-blank 메시지 부재. out: $out" >&2
    tally_fail
  fi
}
anchor_noswallow_check

# ── free-text 6-site 무회귀 (F-INFEAS-NR / F-ACTIVE-PROD / F-AUTH-SILENT 코드 diff 0 — CFP-2628 idiom verbatim) ──
#   위 EC_FINF(=1)/EC_FACT(=1)/EC_FAUTH(=1) 은 free-text 소비 TC — helper 배선 밖. enum 4-site fix 후에도 무변경 통과 확인.
if [ "$EC_FINF" = "1" ] && [ "$EC_FACT" = "1" ] && [ "$EC_FAUTH" = "1" ]; then
  echo "✓ PASS: FREE-TEXT-NO-REGRESSION(CFP-2636) — F-INFEAS-NR/F-ACTIVE-PROD/F-AUTH-SILENT 무회귀(exit 1 유지, AC-7 zero-touch)" >&2
  tally_pass
else
  echo "✗ FAIL: FREE-TEXT-NO-REGRESSION(CFP-2636) — free-text 소비 TC 회귀 (F-INFEAS=$EC_FINF F-ACTIVE=$EC_FACT F-AUTH=$EC_FAUTH)" >&2
  tally_fail
fi

# ── Mutation H/I/J/J2/K 실 RED kill (execution-liveness L3, 캡처-라인 지향 value-존재 분기 무력화) ──
MUT_H=$(run_mutation_kill  "MUT-H-PAYLOAD-PRESENCE" fpayload_blank_body "Mutation-H(payload-presence)")  # kill-fixture = F-PAYLOAD-BLANK
MUT_I=$(run_mutation_kill  "MUT-I-PAYLOAD-ENUM"     fpayload_enum_body  "Mutation-I(payload-enum)")      # kill-fixture = F-PAYLOAD-ENUM
MUT_J=$(run_mutation_kill  "MUT-J-AUTH-PRESENCE"    fauth_blank_body    "Mutation-J(auth-presence)")     # kill-fixture = F-AUTH-BLANK
MUT_J2=$(run_mutation_kill "MUT-J2-AUTH-ENUM"       fauth_enum_body     "Mutation-J2(auth-enum)")        # kill-fixture = F-AUTH-ENUM
MUT_K=$(run_mutation_kill  "MUT-K-STATUS-PRESENCE"  fstatus_blank_body  "Mutation-K(status-presence)")   # kill-fixture = F-STATUS-BLANK-89

echo ""
echo "── CFP-2636 enum-field 값-존재 gap 봉인 결과 ──"
echo "TC-PASSIVE-CLEAN=$EC_PASSIVE_CLEAN F-PAYLOAD(blank/enum)=$EC_PAYLOAD_BLANK/$EC_PAYLOAD_ENUM F-AUTH(blank/enum)=$EC_AUTH_BLANK/$EC_AUTH_ENUM F-STATUS-BLANK-89=$EC_STATUS_BLANK_89 AC-6b-PRESERVE=$EC_AC6B_PRESERVE"
echo "Mutation kill (orig mut): H=[$MUT_H] I=[$MUT_I] J=[$MUT_J] J2=[$MUT_J2] K=[$MUT_K]  (KILLED = 1 0)"

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
PASS=$(grep -cF "P" "$TALLY" 2>/dev/null | head -1); PASS=$(( PASS + 0 ))
FAIL=$(grep -cF "F" "$TALLY" 2>/dev/null | head -1); FAIL=$(( FAIL + 0 ))

echo ""
echo "============================================================"
echo "Test Summary (CFP-2612 §8.9 런타임 DAST 보안 동적 축 doc-section lint)"
echo "============================================================"
echo "PASS: $PASS / FAIL: $FAIL / TOTAL: $((PASS+FAIL))"
echo "CLEAN=$EC_CLEAN F-DO(miss/ok)=$EC_FDO_MISS/$EC_FDO_OK F-NO-G=$EC_FNOG F-STATUS=$EC_FSTATUS"
echo "F-INFEAS(nr/ok)=$EC_FINF/$EC_FINF_OK F-ACTIVE-PROD=$EC_FACT F-AUTH(silent/ok)=$EC_FAUTH/$EC_FAUTH_OK"
echo "F-NA(vague/sub)=$EC_FNA_V/$EC_FNA_S F-8.6-GAP=$EC_86GAP"
echo "CFP-2628 born-hollow: reason=$EC_HOLLOW_REASON env=$EC_HOLLOW_ENV surface=$EC_HOLLOW_SURFACE (fixed 기대 1/1/0)"
echo "Mutation kill (orig mut): A=[$MUT_A] B=[$MUT_B] D=[$MUT_D] E=[$MUT_E] F=[$MUT_F] G=[$MUT_G]  (KILLED = 1 0)"
echo "CFP-2628 capture-line MUT (orig mut): reason=[$CMUT_REASON] env=[$CMUT_ENV] surface=[$CMUT_SURFACE]  (KILLED = orig≠mut, polarity-agnostic)"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All discriminating cases passed (matrix ⊇ §8.2 fixtures + mutation A/B/D/E/F/G + CFP-2628 born-hollow/capture-line KILLED)"
  exit 0
else
  echo "✗ Some cases failed"
  exit 1
fi
