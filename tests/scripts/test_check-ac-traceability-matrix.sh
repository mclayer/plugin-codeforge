#!/usr/bin/env bash
# tests/scripts/test_check-ac-traceability-matrix.sh
# CFP-2603 (Epic CFP-2602 G1) Phase 2 / ADR-145 — Discriminating self-test for the
#   AC-ID zero-drop fail-closed gate:
#     scripts/lib/check_ac_traceability_matrix.py  (Hop1/2/3 pure core)
#     scripts/check-ac-traceability-matrix.sh      (thin wrapper, ADR-061)
#
# 배경 (change-plan §8): 게이트가 hollow(always-PASS) 도, over-reach(천장 위반) 도 아님을 보증한다.
#   각 F-fixture(§8.2) = 임시 AC-source(§5 마크다운 표) + §8 RTM(§8.1 마크다운 표) + tests-root 조합을
#   실제로 구성하고 CLI 를 구동해 exit code 를 *동작으로* assert (|| true 금지 — 실 exit 값 검사).
#   CLI 계약(scripts/check-ac-traceability-matrix.sh 헤더 고정): exit 0 = PASS only, 그 외 = fail-closed.
#
# distinct-marker 의무 (QADev subprocess-fork — exit code 단독 판정 금지): FAIL 판정은
#   exit code ∧ 도메인 sentinel(`ac-traceability-matrix`) ∧ python Traceback 부재로 삼중 확인 →
#   interpreter/shell 표준 exit 우연일치·crash 를 gate-verdict 로 오판하지 않는다.
#
# self-contained bash (bats 미사용 — test_check-venue-shape-fidelity-presence.sh 골격 답습).
#
# ── 테스트-더블 주입점 (ADR-140 hygiene — 최소 affordance, 재설계 아님) ──────────────
#   기본값 = 실 Dev-A core (CI·synthesis 는 무설정으로 실 core 대비 실행). QADev 는 병렬 Phase 2
#   (실 core 미착륙) 상황에서 RED→GREEN discrimination 을 reference oracle 로 사후 입증하기 위해
#   AC_TRACE_PY/SH/LIB 를 override 한다 (cross-layer working-tree drift 대응 — RED 진정성 입증).
#     AC_TRACE_PY  = core .py (default: scripts/lib/check_ac_traceability_matrix.py)
#     AC_TRACE_SH  = thin wrapper (default: scripts/check-ac-traceability-matrix.sh)
#     AC_TRACE_LIB = ac_id.py 를 담은 dir (default: scripts/lib) — mutation temp-copy 용
#
# Mutation kill (§8.4 / §8.8 linter self-test — L3): core 를 temp 로 복사·변조(실 결정라인 targeted
#   transform)한 뒤 타겟 fixture 재실행 → fixture 가 RED 로 뒤집히면(exit1→exit0 leak) mutant kill.
#   변조 미적용(diff 0)=INCONCLUSIVE → self-test FAIL (born-broken 방지 — CFP-2530/2535 계보).
#     Mutation A: Hop2 coverage 무력화 → F-AC4-RED kill
#     Mutation B: Hop3 born-missing ast→grep 변조 → F-ORACLE-GUARD kill (§8.8)
#     Mutation C: fail-closed(빈 AC)→fail-open 변조 → F-AC7-a kill
#     Mutation E: anti-degradation skip-absorb 변조(degraded→비적용 PASS) → F-APPLIC-DEGRADED kill (CFP-2609)
#     Mutation F: empty-AC(F-AC7-a)→비적용 PASS 오라우팅 변조 → F-AC7-a kill (CFP-2609)
#     Mutation NOTOKEN: structural-signature keying 무력화(has_sig 무시=token-only) → F-APPLIC-DEGRADED-NOTOKEN kill (CFP-2609 Codex P2)
#
# Exit: 0 = all fixtures/mutations pass    1 = any fail (or core 미착륙 RED-first)

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
: "${AC_TRACE_PY:=$REPO_ROOT/scripts/lib/check_ac_traceability_matrix.py}"
: "${AC_TRACE_SH:=$REPO_ROOT/scripts/check-ac-traceability-matrix.sh}"
: "${AC_TRACE_LIB:=$REPO_ROOT/scripts/lib}"

SENTINEL="ac-traceability-matrix"  # 도메인 stdout/stderr sentinel (distinct-marker)
PASS=0
FAIL=0
TMPDIRS=()
cleanup() { for d in "${TMPDIRS[@]:-}"; do [ -n "$d" ] && rm -rf "$d"; done; }
trap cleanup EXIT

# ── preflight ────────────────────────────────────────────────────────────────
command -v python3 >/dev/null 2>&1 || { echo "✗ FAIL: python3 미설치 (setup-error)"; exit 1; }
python3 -c "import yaml" >/dev/null 2>&1 || true  # core 는 yaml 미사용 — 관용
if [ ! -f "$AC_TRACE_PY" ]; then
  echo "✗ RED (implementation-not-landed): core 부재 — $AC_TRACE_PY"
  echo "   병렬 Phase 2 — Dev-A core 착륙 시 GREEN (synthesis 확인). discrimination 은 reference oracle 로 입증."
  exit 1
fi
AC_ID_PY="$AC_TRACE_LIB/ac_id.py"
[ -f "$AC_ID_PY" ] || { echo "✗ RED: ac_id.py 부재 — $AC_ID_PY"; exit 1; }

TMP="$(mktemp -d)"; TMPDIRS+=("$TMP")

# ── fixture builders (공통화 — ADR-140 hygiene; Dev-A 실 파서 포맷 = §5/§8 마크다운 표) ──
# AC-source: `## §5` + 표(header: ID|source|tier). rows = "id source tier" 삼중.
mk_ac_source() {  # $1=file ; 이후 "id source tier" 삼중 반복
  local f="$1"; shift
  { printf '## §5. Acceptance Criteria\n\n| ID | source | tier | statement |\n|---|---|---|---|\n'
    while [ "$#" -ge 3 ]; do printf '| %s | %s | %s | given-when-then |\n' "$1" "$2" "$3"; shift 3; done
  } > "$f"
}
mk_ac_source_empty()     { printf '## §5. Acceptance Criteria\n\n| ID | source | tier |\n|---|---|---|\n' > "$1"; }  # 표 header 만, 0 rows
mk_ac_source_countonly() { printf '## §5. Acceptance Criteria\n\nacceptance_criteria_count: 3 (항목화 목록 없음 — 산문만, 표 부재)\n' > "$1"; }

# RTM: `## §8` + `### §8.1 RTM` 표(header: AC|tier|명명 테스트|검증). test cell:
#   backtick 식별자 → 매핑 / `-` → (명명 테스트 없음) / `TODO` → plain placeholder(sham, no backtick).
mk_rtm() {  # $1=file ; 이후 "ac tier test" 삼중 반복
  local f="$1"; shift
  { printf '## §8. Test Contract\n\n### §8.1 RTM\n\n| AC | tier | 명명 테스트 | 검증 |\n|---|---|---|---|\n'
    while [ "$#" -ge 3 ]; do
      case "$3" in
        -)    printf '| %s | %s | (명명 테스트 없음) | v |\n' "$1" "$2" ;;
        TODO) printf '| %s | %s | TODO | v |\n' "$1" "$2" ;;
        *)    printf '| %s | %s | `%s` | v |\n' "$1" "$2" "$3" ;;
      esac
      shift 3
    done
  } > "$f"
}
mk_rtm_notable()     { printf '## §8. Test Contract\n\n(RTM 표 미선언 — 미선언 §8)\n' > "$1"; }
mk_rtm_placeholder() { printf '## §8. 개발 서사\n\n*(DeveloperPL 작성 예정 — Phase 2 PR에서)*\n' > "$1"; }

# tests-root builders (Hop3 ast symbol)
tr_with_def()     { mkdir -p "$1"; printf 'def %s():\n    assert True\n' "$2" > "$1/test_gen.py"; }
tr_comment_only() { mkdir -p "$1"; printf '# planned: %s (아직 실 def 아님)\n"""%s appears only in a docstring"""\n_n = "%s"\ndef test_unrelated():\n    pass\n' "$2" "$2" "$2" > "$1/test_gen.py"; }
tr_unrelated()    { mkdir -p "$1"; printf 'def test_unrelated():\n    pass\n' > "$1/test_gen.py"; }
tr_stub()         { mkdir -p "$1"; printf 'def %s(): pass\n' "$2" > "$1/test_gen.py"; }

# ── 적용성(applicability) AC-source builders (CFP-2609 §8.2 — ADR-145 §결정8) ────
mk_ac_source_noac()     { printf '## §5. Acceptance Criteria\n\n(추적할 AC 없음 — marketplace sync / Epic close / sibling parity)\n' > "$1"; }  # 표 signature 부재 ∧ AC-ID 토큰 부재 → 비적용 positive
mk_ac_source_degtoken() { printf '## §5. Acceptance Criteria\n\n산문으로 AC-1a 를 언급하나 항목화 표(id/source/tier signature) 부재(degradation).\n' > "$1"; }  # 산문 토큰 present ∧ 표 부재
mk_ac_source_notoken()  { printf '## §5. Acceptance Criteria\n\n| ID | source | tier | statement |\n|---|---|---|---|\n| XX-1 | derived | normative | given-when-then |\n' > "$1"; }  # 표 signature present ∧ ID 손상(AC-ID 토큰 부재)
mk_ac_source_advonly()  { printf '## §5. Acceptance Criteria\n\n| ID | source | tier | statement |\n|---|---|---|---|\n| AC-1 | user | advisory | given-when-then |\n| AC-2 | user | declared | given-when-then |\n' > "$1"; }  # records present ∧ 0 normative

# ── gate runner + distinct-marker asserts ─────────────────────────────────────
GATE_EC=0; GATE_OUT=""
run_gate() { local core="$1"; shift; GATE_EC=0; GATE_OUT="$(python3 "$core" "$@" 2>&1)" || GATE_EC=$?; }

case_pass() { # <name> <core> <desc> -- <args...>
  local name="$1" core="$2" desc="$3"; shift 3; [ "$1" = "--" ] && shift
  run_gate "$core" "$@"
  if [ "$GATE_EC" -eq 0 ]; then echo "✓ PASS: $name (exit 0) — $desc"; PASS=$((PASS+1))
  else echo "✗ FAIL: $name — expected exit 0, got $GATE_EC — $desc"; echo "    out: $GATE_OUT"; FAIL=$((FAIL+1)); fi
}
case_fail() { # <name> <core> <desc> -- <args...>  (fail-closed gate verdict: exit1 ∧ sentinel ∧ no-Traceback)
  local name="$1" core="$2" desc="$3"; shift 3; [ "$1" = "--" ] && shift
  run_gate "$core" "$@"
  if [ "$GATE_EC" -eq 1 ] && printf '%s' "$GATE_OUT" | grep -q "$SENTINEL" && ! printf '%s' "$GATE_OUT" | grep -q "Traceback (most recent call last)"; then
    echo "✓ PASS: $name (exit 1 + sentinel) — $desc"; PASS=$((PASS+1))
  elif [ "$GATE_EC" -eq 1 ]; then
    echo "✗ FAIL: $name — exit 1 이나 도메인 sentinel 부재 또는 Traceback (crash≠gate-verdict, distinct-marker 위반) — $desc"; echo "    out: $GATE_OUT"; FAIL=$((FAIL+1))
  else
    echo "✗ FAIL: $name — expected fail-closed exit 1, got $GATE_EC — $desc"; echo "    out: $GATE_OUT"; FAIL=$((FAIL+1)); fi
}

CORE="$AC_TRACE_PY"
echo "════════════════════════════════════════════════════════════════════"
echo "F-fixtures (change-plan §8.2) — core: $CORE"
echo "════════════════════════════════════════════════════════════════════"

# F-AC4-GREEN — 전 normative AC 커버 → exit 0
f=$TMP/f_ac4g; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative
mk_rtm       "$f/rtm.md" AC-1a normative test_ac_id_wellformed_and_schema
case_pass F-AC4-GREEN "$CORE" "전 normative AC → §8 명명 테스트 매핑 → PASS" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm "$f/rtm.md"

# F-AC4-RED — 미커버 normative AC(orphan) → exit 1  [Mutation A 타겟]
f=$TMP/f_ac4r; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative AC-2 derived normative
mk_rtm       "$f/rtm.md" AC-1a normative test_ac_id_wellformed_and_schema
case_fail F-AC4-RED "$CORE" "normative AC-2 미커버(orphan, §8 미매핑) → Hop2 coverage FAIL" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm "$f/rtm.md"

# F-AC2-MALFORMED — required-4 malformed(invalid tier / bad id) → Hop1 validate_ac_record FAIL
#   (S4 / Option(a) — "AC well-formed N"(R2)=필수 4필드 malformed 입증)
f=$TMP/f_ac2mal; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived bogus                 # invalid tier enum (required-4 malformed)
mk_rtm       "$f/rtm.md" AC-1a normative test_x
case_fail F-AC2-MALFORMED-tier "$CORE" "§5 required-4 tier=bogus(invalid enum) → Hop1 well-formed FAIL" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm "$f/rtm.md"
f2=$TMP/f_ac2mal_id; mkdir -p "$f2"
mk_ac_source "$f2/ac.md" AC-1A derived normative            # bad id (uppercase sub-letter)
mk_rtm       "$f2/rtm.md" AC-1A normative test_x
case_fail F-AC2-MALFORMED-id "$CORE" "§5 required-4 id=AC-1A(malformed) → Hop1 well-formed FAIL" -- \
  --phase 1 --ac-source "$f2/ac.md" --rtm "$f2/rtm.md"

# F-AC2-4COL-OK — 정상 4-컬럼(id/source/tier/statement, optional 3 부재) + 매핑 완비 → PASS
#   (S4 / Option(a) born-broken 반증 — derived 3 부재가 false-FAIL 안 됨)
f=$TMP/f_ac2ok; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-2 derived normative             # mk_ac_source 는 statement 컬럼 emit (4-col)
mk_rtm       "$f/rtm.md" AC-2 normative test_ac_schema_fields_present
case_pass F-AC2-4COL-OK "$CORE" "4-컬럼(optional 3 부재) + 매핑 완비 → PASS (derived 부재 false-FAIL 반증)" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm "$f/rtm.md"

# F-AC5 — Phase1 명명 fidelity 미충족(normative 명명 테스트 부재) → exit 1
f=$TMP/f_ac5; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-5 user normative
mk_rtm       "$f/rtm.md" AC-5 normative -
case_fail F-AC5 "$CORE" "Phase1 normative AC 명명 테스트 부재(명명 fidelity 미충족) → FAIL" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm "$f/rtm.md"

# F-AC6 — Phase2 born-missing(symbol 부재) → exit 1
f=$TMP/f_ac6; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-6 user normative
mk_rtm       "$f/rtm.md" AC-6 normative test_ac6_missing
tr_unrelated "$f/tests"
case_fail F-AC6 "$CORE" "Phase2 명명 테스트 symbol 부재(born-missing) → FAIL" -- \
  --phase 2 --ac-source "$f/ac.md" --rtm "$f/rtm.md" --tests-root "$f/tests"

# F-PHASE-SEP — Phase1 은 born-missing 미실행(부재해도 PASS), Phase2 만 FAIL
f=$TMP/f_sep; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative
mk_rtm       "$f/rtm.md" AC-1a normative test_ghost_symbol
tr_unrelated "$f/tests"   # test_ghost_symbol 실 def 부재
case_pass F-PHASE-SEP-p1 "$CORE" "Phase1: 실 symbol 부재해도 명명 매핑 존재 → PASS(born-missing 미실행)" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm "$f/rtm.md" --tests-root "$f/tests"
case_fail F-PHASE-SEP-p2 "$CORE" "Phase2: 동일 symbol 부재 → born-missing FAIL (phase 분리 입증)" -- \
  --phase 2 --ac-source "$f/ac.md" --rtm "$f/rtm.md" --tests-root "$f/tests"

# F-AC7-a — 빈 AC 목록 → exit 1  [Mutation C 타겟]
f=$TMP/f_ac7a; mkdir -p "$f"
mk_ac_source_empty "$f/ac.md"; mk_rtm "$f/rtm.md" AC-1a normative test_x
case_fail F-AC7-a "$CORE" "빈 AC 목록(§5 표 0 rows) bypass → fail-closed FAIL" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm "$f/rtm.md"

# F-AC7-b — 미선언 §8(RTM 매핑 테이블 부재) → exit 1
f=$TMP/f_ac7b; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative; mk_rtm_notable "$f/rtm.md"
case_fail F-AC7-b "$CORE" "미선언 §8(RTM 매핑 테이블 부재) bypass → fail-closed FAIL" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm "$f/rtm.md"

# F-AC7-b2 — §8 개발서사 placeholder(작성 예정) → false-FAIL 함정 봉인 → exit 1
f=$TMP/f_ac7b2; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative; mk_rtm_placeholder "$f/rtm.md"
case_fail F-AC7-b2 "$CORE" "§8 개발서사 placeholder(작성 예정) = authoritative RTM 아님 → fail-closed FAIL (ADR-145 §결정6 P1)" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm "$f/rtm.md"

# F-AC7-c — stub 명명 회피(plain placeholder cell, backtick 없음) → normative 미매핑 → exit 1
f=$TMP/f_ac7c; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative; mk_rtm "$f/rtm.md" AC-1a normative TODO
case_fail F-AC7-c "$CORE" "normative AC → sham/placeholder(TODO, non-backtick) 명명 회피 → 미매핑 FAIL" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm "$f/rtm.md"

# F-AC7-d — phase 오선언(invalid) → 판정불가 non-zero (argparse choices → exit 2; contract 'else' non-PASS)
f=$TMP/f_ac7d; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative; mk_rtm "$f/rtm.md" AC-1a normative test_x
run_gate "$CORE" --phase 3 --ac-source "$f/ac.md" --rtm "$f/rtm.md"
if [ "$GATE_EC" -ne 0 ] && printf '%s' "$GATE_OUT" | grep -qi "phase\|choice"; then
  echo "✓ PASS: F-AC7-d (exit $GATE_EC, non-PASS + phase-reject) — invalid --phase EXPLICIT 신호 → fail-closed(non-zero)"; PASS=$((PASS+1))
else
  echo "✗ FAIL: F-AC7-d — invalid phase 가 non-zero fail-closed 아님 (got $GATE_EC)"; echo "    out: $GATE_OUT"; FAIL=$((FAIL+1))
fi

# F-ADVISORY — advisory(AC-10) 미커버여도 PASS (over-reach kill)
f=$TMP/f_adv; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative AC-10 user advisory
mk_rtm       "$f/rtm.md" AC-1a normative test_x AC-10 advisory -
case_pass F-ADVISORY "$CORE" "advisory AC-10 명명 테스트 없음 → PASS (게이트가 강제하면 천장위반=RED)" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm "$f/rtm.md"

# F-DECLARED — declared(AC-1b) 미커버여도 PASS (over-reach kill)
f=$TMP/f_dec; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative AC-1b user declared
mk_rtm       "$f/rtm.md" AC-1a normative test_x AC-1b declared -
case_pass F-DECLARED "$CORE" "declared AC-1b 명명 테스트 없음 → PASS (forged machine test 금지, 천장)" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm "$f/rtm.md"

# F-ORACLE-GUARD — 함수명이 주석/docstring/문자열 안에만 존재 → born-missing FAIL  [Mutation B 타겟]
f=$TMP/f_oracle; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative
mk_rtm       "$f/rtm.md" AC-1a normative test_only_in_comment
tr_comment_only "$f/tests" test_only_in_comment
case_fail F-ORACLE-GUARD "$CORE" "명명 테스트명이 주석/docstring/문자열에만 존재(실 def 없음) → ast born-missing FAIL (grep 이면 거짓 PASS)" -- \
  --phase 2 --ac-source "$f/ac.md" --rtm "$f/rtm.md" --tests-root "$f/tests"

# F-RENAME — 명명 테스트 rename → Phase2 FAIL
f=$TMP/f_ren; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative
mk_rtm       "$f/rtm.md" AC-1a normative test_expected_name
tr_with_def "$f/tests" test_renamed_away
case_fail F-RENAME "$CORE" "RTM=test_expected_name, 실파일=test_renamed_away → born-missing FAIL" -- \
  --phase 2 --ac-source "$f/ac.md" --rtm "$f/rtm.md" --tests-root "$f/tests"

# F-ABSENT — 명명 테스트 삭제(tests-root 무관 파일만) → Phase2 FAIL
f=$TMP/f_abs; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative
mk_rtm       "$f/rtm.md" AC-1a normative test_deleted
tr_unrelated "$f/tests"
case_fail F-ABSENT "$CORE" "명명 테스트 삭제(symbol 부재) → born-missing FAIL" -- \
  --phase 2 --ac-source "$f/ac.md" --rtm "$f/rtm.md" --tests-root "$f/tests"

# F-STUB — def test_x(): pass = 파일∧symbol 실재 → PASS (G3 경계, 본 게이트 소관 아님을 confess)
#   ⚠ G3 CONFESS: stub 이 기능을 discriminating 하게 행사하는지(=G3 소관)는 본 G1 게이트가 판정하지 않는다.
#   파일∧symbol ast-resolve = born-missing PASS 가 *의도된* 경계.
f=$TMP/f_stub; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative
mk_rtm       "$f/rtm.md" AC-1a normative test_stub_ok
tr_stub "$f/tests" test_stub_ok
case_pass F-STUB "$CORE" "def test_stub_ok(): pass = 실 symbol 존재 → born-missing PASS (G3 경계 confess)" -- \
  --phase 2 --ac-source "$f/ac.md" --rtm "$f/rtm.md" --tests-root "$f/tests"

# F-LINKBREAK — cross-repo 내러티브↔실파일 링크 단절(tests-root 경로 dangling) → 판정불가 FAIL
f=$TMP/f_link; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative
mk_rtm       "$f/rtm.md" AC-1a normative test_x
case_fail F-LINKBREAK "$CORE" "Phase2 tests-root 경로 단절(dangling) → 판정불가 fail-closed FAIL (default-green 금지)" -- \
  --phase 2 --ac-source "$f/ac.md" --rtm "$f/rtm.md" --tests-root "$f/does-not-exist"

# F-SUBLETTER — AC-1a sub-letter 가 drop 되지 않음 (naive AC-\d+ 면 AC-1 로 붕괴 → 거짓 PASS)
#   correct: AC-1(mapped) ∧ AC-1a(normative UNmapped) distinct → AC-1a orphan → FAIL.
#   sub-letter drop 게이트: AC-1a→AC-1 붕괴 → AC-1 mapped 로 보고 거짓 PASS(exit 0).
f=$TMP/f_sub; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1 derived normative AC-1a derived normative
mk_rtm       "$f/rtm.md" AC-1 normative test_one_mapped
case_fail F-SUBLETTER "$CORE" "AC-1(mapped)+AC-1a(unmapped) → AC-1a distinct orphan FAIL (sub-letter drop 반증)" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm "$f/rtm.md"

# ── 적용성(applicability) discriminating fixtures (CFP-2609 §8.2 — 3경로 + anti-degradation) ──
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "Applicability (CFP-2609 §8.2) — 비적용→PASS / 판정불가·미추적→FAIL discriminate"
echo "════════════════════════════════════════════════════════════════════"

# F-APPLIC-NONAPPLICABLE (PASS) — §5 AC 표 부재 ∧ AC-ID 토큰 부재(resolved) → exit 0 (비적용 positive, AC-1a)
#   skip 이 REACHABLE 함(over-strict 아님) 입증.
f=$TMP/f_applic_none; mkdir -p "$f"
mk_ac_source_noac "$f/ac.md"
case_pass F-APPLIC-NONAPPLICABLE "$CORE" "§5 AC 표·AC-ID 토큰 부재 → 비적용 in-job PASS (skip REACHABLE)" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm-not-yet

# F-APPLIC-DEGRADED (FAIL) — §5 산문 AC-ID 토큰 present ∧ parseable 표 부재 → exit 1 (anti-degradation, AC-2)  [Mutation E 타겟]
f=$TMP/f_applic_deg; mkdir -p "$f"
mk_ac_source_degtoken "$f/ac.md"
case_fail F-APPLIC-DEGRADED "$CORE" "산문 AC-ID 토큰 present + 표 파손(degradation) → 판정불가 FAIL (degraded→skip 흡수 금지)" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm-not-yet

# F-APPLIC-DEGRADED-NOTOKEN (FAIL) — 표 signature present ∧ ID 손상(XX-1, AC-ID 토큰 부재) → exit 1  [Mutation NOTOKEN 타겟]
#   ★ Codex P2: structural-signature keying — table 구조 present 면 token 부재라도 NO_AC_SURFACE 아님(Hop1 malformed 경유 FAIL).
#   token-only keying 이면 XX-1 손상표가 비적용 PASS 로 샘(anti-degradation 붕괴) → 봉인 입증.
f=$TMP/f_applic_notok; mkdir -p "$f"
mk_ac_source_notoken "$f/ac.md"
case_fail F-APPLIC-DEGRADED-NOTOKEN "$CORE" "표 signature present + ID=XX-1(토큰 부재) → SURFACE_PRESENT→Hop1 malformed FAIL (token-only keying 봉인)" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm-not-yet

# F-APPLIC-0NORMATIVE (PASS) — §5 표 present + records well-formed + 0 normative(전부 declared/advisory) → exit 0 (비적용-유사, e7)
f=$TMP/f_applic_0n; mkdir -p "$f"
mk_ac_source_advonly "$f/ac.md"
case_pass F-APPLIC-0NORMATIVE "$CORE" "records present·0 normative(전부 declared/advisory) → 비적용-유사 PASS" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm-not-yet

# F-APPLIC-SUPPRESS (FAIL) — resolved §5 ≥1 normative unmapped → exit 1 (위장 불가, AC-3; = F-AC4-RED 강화)
f=$TMP/f_applic_sup; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative
mk_rtm       "$f/rtm.md" AC-1a normative -
case_fail F-APPLIC-SUPPRESS "$CORE" "적용(§5 normative present) + §8 미추적 → FAIL 도달 (신호 non-suppressible)" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm "$f/rtm.md"

# F-PHASE1-RTM-NOTYET (PASS) — phase 1 + rtm not-yet EXPLICIT 신호 + ≥1 normative → exit 0 (Hop1 only, AC-4)
#   placeholder fallback(§8 "작성 예정" FAIL, F-AC7-b2)과 구분 — EXPLICIT --rtm-not-yet.
f=$TMP/f_applic_notyet; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative
case_pass F-PHASE1-RTM-NOTYET "$CORE" "phase1 + --rtm-not-yet + normative → Hop1 only PASS (placeholder fallback 아님)" -- \
  --phase 1 --ac-source "$f/ac.md" --rtm-not-yet

# ── L2 execution-liveness (§8.9): .github/ ↔ templates/ workflow byte-identical ──
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "L2 (§8.9) — workflow byte-identical copy"
echo "════════════════════════════════════════════════════════════════════"
WF_A="$REPO_ROOT/.github/workflows/ac-traceability-matrix.yml"
WF_B="$REPO_ROOT/templates/github-workflows/ac-traceability-matrix.yml"
if [ -f "$WF_A" ] && [ -f "$WF_B" ]; then
  if diff -q "$WF_A" "$WF_B" >/dev/null 2>&1; then
    echo "✓ PASS: L2-byte-identical — .github/ ↔ templates/ workflow diff 0"; PASS=$((PASS+1))
  else
    echo "✗ FAIL: L2-byte-identical — workflow 두 copy 가 divergent (diff≠0)"; FAIL=$((FAIL+1))
  fi
else
  echo "✗ FAIL: L2-byte-identical — workflow 미착륙 (RED-first; Dev-A 착륙 시 GREEN)"
  echo "    A=$WF_A ($([ -f "$WF_A" ] && echo present || echo ABSENT)) / B=$WF_B ($([ -f "$WF_B" ] && echo present || echo ABSENT))"
  FAIL=$((FAIL+1))
fi

# ── thin wrapper passthrough (ADR-061) ────────────────────────────────────────
if [ -f "$AC_TRACE_SH" ]; then
  wf=$TMP/wf; mkdir -p "$wf"
  mk_ac_source_empty "$wf/ac.md"; mk_rtm "$wf/rtm.md" AC-1a normative test_x
  ec=0; bash "$AC_TRACE_SH" --phase 1 --ac-source "$wf/ac.md" --rtm "$wf/rtm.md" >/dev/null 2>&1 || ec=$?
  if [ "$ec" -eq 1 ]; then echo "✓ PASS: wrapper-passthrough (exit 1) — thin wrapper exit-code passthrough (ADR-061)"; PASS=$((PASS+1))
  else echo "✗ FAIL: wrapper-passthrough — expected exit 1 passthrough, got $ec"; FAIL=$((FAIL+1)); fi
else
  echo "✗ FAIL: wrapper-passthrough — $AC_TRACE_SH 미착륙 (RED-first)"; FAIL=$((FAIL+1))
fi

# ── Mutation A/B/C (§8.4 / §8.8 linter self-test — kill 실증, Dev-A 실 결정라인 targeted) ──
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "Mutation kill (§8.4 / §8.8) — core 변조 후 타겟 fixture RED 뒤집힘 입증"
echo "════════════════════════════════════════════════════════════════════"

# mutate <sed-expr> <mutdir> → 0 if 적용(diff≠0), 1 if 미적용(INCONCLUSIVE)
mutate() {
  local sed_expr="$1" out="$2"
  mkdir -p "$out"; cp "$AC_ID_PY" "$out/ac_id.py"
  sed -E "$sed_expr" "$AC_TRACE_PY" > "$out/$(basename "$AC_TRACE_PY")"
  diff -q "$AC_TRACE_PY" "$out/$(basename "$AC_TRACE_PY")" >/dev/null 2>&1 && return 1 || return 0
}
run_mut_kill() { # <name> <mutdir> <desc> -- <args...>  (원본 exit1 → 변조 exit0 = kill)
  local name="$1" mutdir="$2" desc="$3"; shift 3; [ "$1" = "--" ] && shift
  local mutcore="$mutdir/$(basename "$AC_TRACE_PY")" base_ec=0 mut_ec=0
  ( python3 "$AC_TRACE_PY" "$@" >/dev/null 2>&1 ) || base_ec=$?
  ( python3 "$mutcore"      "$@" >/dev/null 2>&1 ) || mut_ec=$?
  if [ "$base_ec" -eq 1 ] && [ "$mut_ec" -eq 0 ]; then
    echo "✓ PASS: $name — 원본 exit1 → 변조 exit0 (mutant KILL) — $desc"; PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name — kill 미입증 (원본=$base_ec 변조=$mut_ec, 기대 1→0) — $desc"; FAIL=$((FAIL+1)); fi
}

# Mutation A — Hop2 coverage 무력화 (normative-미커버 조건 → if False)
MA=$TMP/mutA
if mutate 's/if tier == "normative" and not tests:/if False:  # MUTATED-A/' "$MA"; then
  fa=$TMP/f_ac4r
  run_mut_kill Mutation-A "$MA" "coverage 무조건 PASS 변조 → F-AC4-RED kill" -- \
    --phase 1 --ac-source "$fa/ac.md" --rtm "$fa/rtm.md"
else
  echo "✗ INCONCLUSIVE: Mutation-A — Hop2 coverage 결정라인(if tier==normative and not tests:) 미검출 → synthesis 가 실 core 에 sed 재배선 필요"; FAIL=$((FAIL+1))
fi

# Mutation B — Hop3 born-missing ast→grep 변조 (§8.8 linter self-test: 텍스트 매칭 오라클 주입)
MB=$TMP/mutB
if mutate 's|tree = ast.parse\(src, filename=path\)|symbols.update(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", src)); tree = ast.parse("", filename=path)  # MUTATED-B grep-oracle|' "$MB"; then
  fb=$TMP/f_oracle
  run_mut_kill Mutation-B "$MB" "born-missing ast→grep(텍스트) 변조 → F-ORACLE-GUARD kill (§8.8 self-test)" -- \
    --phase 2 --ac-source "$fb/ac.md" --rtm "$fb/rtm.md" --tests-root "$fb/tests"
else
  echo "✗ INCONCLUSIVE: Mutation-B — Hop3 ast 심볼수집 결정라인(tree = ast.parse(src, filename=path)) 미검출 → synthesis 가 실 core born-missing ast→grep 변조를 재배선 필요"; FAIL=$((FAIL+1))
fi

# Mutation C — fail-closed(빈 AC) → fail-open 변조 (if not records: → if False:)
MC=$TMP/mutC
if mutate 's/if not records:/if False:  # MUTATED-C/' "$MC"; then
  fc=$TMP/f_ac7a
  run_mut_kill Mutation-C "$MC" "fail-closed(빈 AC)→fail-open 변조 → F-AC7-a kill" -- \
    --phase 1 --ac-source "$fc/ac.md" --rtm "$fc/rtm.md"
else
  echo "✗ INCONCLUSIVE: Mutation-C — fail-closed(빈 AC) 결정라인(if not records:) 미검출 → synthesis 가 실 core fail-closed 라인에 sed 재배선 필요"; FAIL=$((FAIL+1))
fi

# Mutation D — Hop1 validate_ac_record 호출 무력화 (AC-2 non-hollow 배선 self-test, S4 / Option(a))
MD=$TMP/mutD
if mutate 's/for v in validate_ac_record\(rec\):/for v in []:  # MUTATED-D/' "$MD"; then
  fd=$TMP/f_ac2mal
  run_mut_kill Mutation-D "$MD" "Hop1 validate_ac_record 호출 무력화 → F-AC2-MALFORMED(tier=bogus) kill" -- \
    --phase 1 --ac-source "$fd/ac.md" --rtm "$fd/rtm.md"
else
  echo "○ SKIP: Mutation-D — hop1 'for v in validate_ac_record(rec):' 미검출 (인터페이스 형태 상이) — 착륙 시 유효, F-AC2-MALFORMED discriminator 로 충분(S4 omittable)"
fi

# ── 적용성 Mutation E/F/NOTOKEN (CFP-2609 §8.4 — born-hollow 봉인 실증) ──────────
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "Applicability mutation kill (CFP-2609 §8.4) — 적용성 born-hollow 봉인 실증"
echo "════════════════════════════════════════════════════════════════════"

# Mutation E — anti-degradation guard 무력화 (산문 AC-ID 토큰 present UNDECIDABLE → NO_AC_SURFACE PASS 로 흡수)
ME=$TMP/mutE
if mutate 's/if has_ac_surface_claim:/if False:  # MUTATED-E/' "$ME"; then
  fe=$TMP/f_applic_deg
  run_mut_kill Mutation-E "$ME" "anti-degradation skip-absorb 변조(degraded→비적용 PASS) → F-APPLIC-DEGRADED kill" -- \
    --phase 1 --ac-source "$fe/ac.md" --rtm-not-yet
else
  echo "✗ INCONCLUSIVE: Mutation-E — anti-degradation 결정라인(if has_ac_surface_claim:) 미검출 → synthesis 재배선 필요"; FAIL=$((FAIL+1))
fi

# Mutation F — empty-AC(F-AC7-a) → 비적용 PASS 오라우팅 변조 (SURFACE_EMPTY return → NO_AC_SURFACE)
#   NB: 3-tuple return 이므로 inline 주석 삽입 금지(tuple 절단 → unpack crash). enum 토큰만 치환.
MF=$TMP/mutF
if mutate 's/return APPLIC_SURFACE_EMPTY,/return APPLIC_NO_AC_SURFACE,/' "$MF"; then
  ff=$TMP/f_ac7a
  run_mut_kill Mutation-F "$MF" "empty-AC(F-AC7-a)→비적용 오흡수 변조 → F-AC7-a kill (표 부재 vs 표 present·0 rows 구분)" -- \
    --phase 1 --ac-source "$ff/ac.md" --rtm "$ff/rtm.md"
else
  echo "✗ INCONCLUSIVE: Mutation-F — empty-AC 결정라인(return APPLIC_SURFACE_EMPTY,) 미검출 → synthesis 재배선 필요"; FAIL=$((FAIL+1))
fi

# Mutation NOTOKEN — structural-signature keying 무력화 (has_sig 분기 skip → token-only keying leak)
#   ★ Codex P2: 표 signature present(has_sig)를 무시하면 XX-1 손상 표가 비적용 PASS 로 샌다.
MN=$TMP/mutN
if mutate 's/if has_sig:/if False:  # MUTATED-NOTOKEN/' "$MN"; then
  fn=$TMP/f_applic_notok
  run_mut_kill Mutation-NOTOKEN "$MN" "structural-signature keying 무력화(has_sig 무시=token-only) → F-APPLIC-DEGRADED-NOTOKEN kill" -- \
    --phase 1 --ac-source "$fn/ac.md" --rtm-not-yet
else
  echo "✗ INCONCLUSIVE: Mutation-NOTOKEN — structural-signature 결정라인(if has_sig:) 미검출 → synthesis 재배선 필요"; FAIL=$((FAIL+1))
fi

# ── story_uri-absent 비적용 선언(F-NONE-*, CFP-2634 §결정9 — ADR-145 §결정9) ──────
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "F-NONE-* (CFP-2634 §결정9) — story_uri-absent ac_applicability:none 선언"
echo "════════════════════════════════════════════════════════════════════"

# run_gate_none <core> <reason> [extra args...] — source 없이 none-flag 로 구동(§결정9).
run_gate_none() { local core="$1" reason="$2"; shift 2; GATE_EC=0; GATE_OUT="$(python3 "$core" --phase 1 --ac-applicability-none --none-reason "$reason" --rtm-not-yet --tests-root tests "$@" 2>&1)" || GATE_EC=$?; }

# F-NONE-PASS — story_uri 부재 + none 선언(비-공백 사유) → exit 0 ∧ 출력 "비적용" 포함
run_gate_none "$CORE" "marketplace-sync — 추적 AC 없음"
if [ "$GATE_EC" -eq 0 ] && printf '%s' "$GATE_OUT" | grep -q "비적용"; then
  echo "✓ PASS: F-NONE-PASS (exit 0 + '비적용' 공개) — story_uri 부재 + none 선언(비-공백 사유) → 비적용 PASS"; PASS=$((PASS+1))
else
  echo "✗ FAIL: F-NONE-PASS — expected exit 0 ∧ '비적용' 포함, got exit=$GATE_EC"; echo "    out: $GATE_OUT"; FAIL=$((FAIL+1))
fi

# F-NONE-NOREASON — --none-reason "" 또는 공백 → exit 1 ∧ sentinel ∧ no-Traceback  [M-NONE-REASON 타겟]
for reason in "" "   "; do
  run_gate_none "$CORE" "$reason"
  if [ "$GATE_EC" -eq 1 ] && printf '%s' "$GATE_OUT" | grep -q "$SENTINEL" && ! printf '%s' "$GATE_OUT" | grep -q "Traceback (most recent call last)"; then
    echo "✓ PASS: F-NONE-NOREASON (reason='$reason', exit 1 + sentinel) — none-무사유 fail-closed(AC-2)"; PASS=$((PASS+1))
  else
    echo "✗ FAIL: F-NONE-NOREASON (reason='$reason') — expected exit 1 ∧ sentinel ∧ no-Traceback, got exit=$GATE_EC"; echo "    out: $GATE_OUT"; FAIL=$((FAIL+1))
  fi
done

# F-BOTH-ABSENT — --ac-source 도 --ac-applicability-none 도 부재 → exit 1 ∧ sentinel ∧ no-Traceback  [M-BOTHABSENT 타겟]
run_gate "$CORE" --phase 1 --rtm-not-yet --tests-root tests
if [ "$GATE_EC" -eq 1 ] && printf '%s' "$GATE_OUT" | grep -q "$SENTINEL" && ! printf '%s' "$GATE_OUT" | grep -q "Traceback (most recent call last)"; then
  echo "✓ PASS: F-BOTH-ABSENT (exit 1 + sentinel) — 둘다부재 distinct default guard fail-closed(AC-1c)"; PASS=$((PASS+1))
else
  echo "✗ FAIL: F-BOTH-ABSENT — expected exit 1 ∧ sentinel ∧ no-Traceback, got exit=$GATE_EC"; echo "    out: $GATE_OUT"; FAIL=$((FAIL+1))
fi

# F-NONE-SPOOF — --ac-source(normative≥1) + none 선언(사유 존재) → exit 1(위장 불가, surface overrides none)  [M-SPOOF 타겟]
f=$TMP/f_none_spoof; mkdir -p "$f"
mk_ac_source "$f/ac.md" AC-1a derived normative
run_gate "$CORE" --phase 1 --ac-source "$f/ac.md" --ac-applicability-none --none-reason "위장" --rtm-not-yet --tests-root tests
if [ "$GATE_EC" -eq 1 ] && printf '%s' "$GATE_OUT" | grep -q "$SENTINEL" && ! printf '%s' "$GATE_OUT" | grep -q "Traceback (most recent call last)"; then
  echo "✓ PASS: F-NONE-SPOOF (exit 1 + sentinel) — normative+none 위장 → FAIL(AC-3, surface overrides none)"; PASS=$((PASS+1))
else
  echo "✗ FAIL: F-NONE-SPOOF — expected exit 1 ∧ sentinel ∧ no-Traceback, got exit=$GATE_EC"; echo "    out: $GATE_OUT"; FAIL=$((FAIL+1))
fi

# F-NONE-COEXIST-0N — NO_AC_SURFACE(§5 AC 표·토큰 부재) + none 선언 → exit 0(병존-무해)
f=$TMP/f_none_coexist; mkdir -p "$f"
mk_ac_source_noac "$f/ac.md"
run_gate "$CORE" --phase 1 --ac-source "$f/ac.md" --ac-applicability-none --none-reason "병존" --rtm-not-yet --tests-root tests
if [ "$GATE_EC" -eq 0 ]; then
  echo "✓ PASS: F-NONE-COEXIST-0N (exit 0) — NO_AC_SURFACE + none 선언 → 병존-무해 PASS"; PASS=$((PASS+1))
else
  echo "✗ FAIL: F-NONE-COEXIST-0N — expected exit 0, got exit=$GATE_EC"; echo "    out: $GATE_OUT"; FAIL=$((FAIL+1))
fi

# ── Mutation M-NONE-REASON / M-SPOOF / M-BOTHABSENT (CFP-2634 §결정9 — none-declaration 3 결정라인) ──
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "Mutation kill (CFP-2634 §결정9) — none-declaration 3 결정라인 봉인 실증"
echo "════════════════════════════════════════════════════════════════════"

# Mutation M-NONE-REASON — reason-guard 무력화(if not (none_reason and none_reason.strip()): → if False)
MG=$TMP/mutG
if mutate 's/if not \(none_reason and none_reason\.strip\(\)\):/if False:  # MUTATED-NONE-REASON/' "$MG"; then
  run_mut_kill M-NONE-REASON "$MG" "reason-guard 무력화(none+빈사유) → F-NONE-NOREASON kill" -- \
    --phase 1 --ac-applicability-none --none-reason "" --rtm-not-yet --tests-root tests
else
  echo "✗ INCONCLUSIVE: M-NONE-REASON — reason-guard 결정라인(if not (none_reason and none_reason.strip()):) 미검출 → synthesis 재배선 필요"; FAIL=$((FAIL+1))
fi

# Mutation M-SPOOF — spoof-guard 무력화(if none_declaration and ac_source_path is None: → if none_declaration:)
MH=$TMP/mutH
if mutate 's/if none_declaration and ac_source_path is None:/if none_declaration:  # MUTATED-SPOOF/' "$MH"; then
  fh=$TMP/f_none_spoof
  run_mut_kill M-SPOOF "$MH" "spoof-guard 무력화(normative+none 위장) → F-NONE-SPOOF kill" -- \
    --phase 1 --ac-source "$fh/ac.md" --ac-applicability-none --none-reason "위장" --rtm-not-yet --tests-root tests
else
  echo "✗ INCONCLUSIVE: M-SPOOF — spoof-guard 결정라인(if none_declaration and ac_source_path is None:) 미검출 → synthesis 재배선 필요"; FAIL=$((FAIL+1))
fi

# Mutation M-BOTHABSENT — both-absent-guard 무력화(if ac_source_path is None and not none_declaration: → if False)
MI=$TMP/mutI
if mutate 's/if ac_source_path is None and not none_declaration:/if False:  # MUTATED-BOTHABSENT/' "$MI"; then
  run_mut_kill M-BOTHABSENT "$MI" "both-absent-guard 무력화(둘다부재) → F-BOTH-ABSENT kill" -- \
    --phase 1 --rtm-not-yet --tests-root tests
else
  echo "✗ INCONCLUSIVE: M-BOTHABSENT — both-absent-guard 결정라인(if ac_source_path is None and not none_declaration:) 미검출 → synthesis 재배선 필요"; FAIL=$((FAIL+1))
fi

# ── summary ───────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "Summary (CFP-2603 G1 AC-traceability zero-drop self-test)"
echo "════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"; echo "FAIL: $FAIL"; echo "TOTAL: $((PASS+FAIL))"
[ "$FAIL" -eq 0 ] && { echo "✓ All fixtures + mutations passed"; exit 0; } || { echo "✗ Some checks failed"; exit 1; }
