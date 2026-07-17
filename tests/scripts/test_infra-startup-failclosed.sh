#!/usr/bin/env bash
# tests/scripts/test_infra-startup-failclosed.sh
# CFP-2700 (Epic) G3 Phase 2 (구현 lane) — Discriminating self-test (.sh channel) for
#   scripts/lib/check_infra_manifest_schema.py (AC-2) + scripts/lib/infra_startup_validator.py
#   (AC-3/9/15 D2 startup fail-closed reference-impl) + tests/fixtures/infra-refimpl/ (AC-19).
#
# ★ hollow-gate 아님의 증명 (ADR-157 §결정2 / ADR-119 execution-backed) — presence-grep 금지,
#   전 케이스 실 exit code + FIXED 토큰 결박 + 대표 mutation RED-flip:
#   AC-2  4 필수 필드(id/canonical_env/aliases/required) 필드별 negative → exit 1 + 누락 필드명
#         + positive control + MK schema_required_off.
#   AC-3  D2 4계약 — required 미설정 → exit 78(EX_CONFIG, 구성오류 distinct code) + 자원 ID loud /
#         빈 값 reject / optional_degradable degrade 계속 / block·unit 미선언 fail-closed /
#         dangling rid × optional_degradable = manifest 무결성 실패 → mode 무관 78 (F-CR-2724-1)
#         + MK missing_masked (missing 삼킴 → BOOT-REFUSED 소멸 = RED-flip).
#   AC-9  allow-set parity — --emit-allow-set union == 스캐너 parse_manifest classified (diff 0 실측)
#         + MK deprecated_unclassified(공유 파서 G2 동일 anchor) → PARITY-BROKEN exit 78 트립.
#   AC-15 채택 3-way — adopted+누락 FAIL / 미채택+사유 비적용 PASS / 미채택+사유부재 FAIL.
#   AC-19 fixture pair — **env -i self-contained** 실행: enforced 미설정 → startup 단계 exit 78 +
#         BUSINESS_OP_REACHED 센티넬 **부재** / unenforced → 센티넬 출력 후 late-crash (판별).
#
# ★ .py 채널(test_infra-startup-failclosed.py) 과 disjoint 보완 — hermetic 상세·mutation 다수
#   (.env red-herring / mode_default_open / adoption_failopen / missing_masked-주입-enforced 퇴화)는
#   .py 채널 관할. 본 채널 = env -i 실행 표면 + 대표 RED-flip (과잉 중복 회피).
#
# self-contained bash (tests/scripts 관례 — ADR-151 인벤토리 enroll 채널). Exit 0 = 전 케이스 PASS.

set -uo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIB="$REPO_ROOT/scripts/lib"
SCHEMA_PY="$LIB/check_infra_manifest_schema.py"
VALIDATOR_PY="$LIB/infra_startup_validator.py"
PARSER_PY="$LIB/check_infra_resource_drift.py"
FIXTURE_DIR="$REPO_ROOT/tests/fixtures/infra-refimpl"
FIXTURE_MANIFEST="$FIXTURE_DIR/manifest.yaml"
SENTINEL="BUSINESS_OP_REACHED"

PASS=0
FAIL=0

VALID_MANIFEST='infra_resources:
  resources:
    - id: raw-nas
      canonical_env: RAW_NAS_URL
      aliases:
        accepted: [MINIO_URL]
    - id: derived-nas
      canonical_env: DERIVED_NAS_URL
      aliases:
        accepted: []
  execution_units:
    collector:
      required: [raw-nas, derived-nas]
      resource_modes:
        raw-nas: required
        derived-nas: optional_degradable
        derived-nas_degraded_behavior: "derived write skip + WARN"'

# case <name> <cmd-exit-expected> <expect_token|""> <forbid_token|""> — $CASE_OUT/$CASE_EXIT 소비.
_judge() {
  local name="$1" eexit="$2" etok="$3" ftok="$4" ok=1
  [ "$CASE_EXIT" -eq "$eexit" ] || ok=0
  if [ -n "$etok" ]; then case "$CASE_OUT" in *"$etok"*) : ;; *) ok=0;; esac; fi
  if [ -n "$ftok" ]; then case "$CASE_OUT" in *"$ftok"*) ok=0;; esac; fi
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (exit $CASE_EXIT)"
    PASS=$((PASS+1))
  else
    echo "X FAIL: $name — expected exit=$eexit expect='$etok' forbid='$ftok', got exit=$CASE_EXIT"
    echo "  output: $CASE_OUT"
    FAIL=$((FAIL+1))
  fi
}

# schema_case <name> <expected_exit> <expect> <forbid> <manifest-content>
schema_case() {
  local name="$1" eexit="$2" etok="$3" ftok="$4" content="$5" tmp
  tmp=$(mktemp -d)
  printf '%s\n' "$content" > "$tmp/m.yaml"
  CASE_EXIT=0
  CASE_OUT=$(python3 "$SCHEMA_PY" --manifest "$tmp/m.yaml" 2>&1) || CASE_EXIT=$?
  rm -rf "$tmp"
  _judge "$name" "$eexit" "$etok" "$ftok"
}

# validator_case <name> <expected_exit> <expect> <forbid> <extra-env KEY=V ...> -- <args...>
validator_case() {
  local name="$1" eexit="$2" etok="$3" ftok="$4"
  shift 4
  local envs=()
  while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do envs+=("$1"); shift; done
  shift  # --
  CASE_EXIT=0
  CASE_OUT=$(env "${envs[@]}" python3 "$VALIDATOR_PY" "$@" 2>&1) || CASE_EXIT=$?
  _judge "$name" "$eexit" "$etok" "$ftok"
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2700 G3: infra-startup-failclosed — discriminating self-test (.sh)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

echo "── AC-2 manifest schema 4 필수 필드 (positive + 필드별 negative → 누락 필드명) ──"
schema_case "AC-2 positive control → PASS(exit 0)" 0 \
  "check-infra-manifest-schema: PASS" "" "$VALID_MANIFEST"
schema_case "AC-2 id 누락 → exit 1 + 필드명" 1 \
  "필수 필드 누락: id" "" \
  "$(printf '%s\n' "$VALID_MANIFEST" | sed 's/^    - id: raw-nas$/    - id_removed_marker: x/')"
schema_case "AC-2 canonical_env 누락 → exit 1 + 필드명" 1 \
  "필수 필드 누락: canonical_env" "" \
  "$(printf '%s\n' "$VALID_MANIFEST" | grep -v '      canonical_env: RAW_NAS_URL')"
schema_case "AC-2 aliases 누락 → exit 1 + 필드명" 1 \
  "필수 필드 누락: aliases" "" \
  "$(printf '%s\n' "$VALID_MANIFEST" | sed '/- id: derived-nas/,/accepted: \[\]/{/aliases:/d; /accepted: \[\]/d}')"
schema_case "AC-2 execution_unit required 누락 → exit 1 + 필드명" 1 \
  "필수 필드 누락: required" "" \
  "$(printf '%s\n' "$VALID_MANIFEST" | grep -v '      required: \[raw-nas, derived-nas\]')"
# MK schema_required_off: required 검사 무력화 → negative 가 통과(RED-flip).
_mk_tmp=$(mktemp -d)
mkdir -p "$_mk_tmp/mutlib"
cp "$PARSER_PY" "$VALIDATOR_PY" "$_mk_tmp/mutlib/"
python3 - "$SCHEMA_PY" "$_mk_tmp/mutlib/check_infra_manifest_schema.py" <<'PY'
import sys
s = open(sys.argv[1], encoding="utf-8").read()
s2 = s.replace('        if "required" not in u["keys"]:',
               "        if False:  # MUTANT-schema-required-off", 1)
assert s2 != s, "anchor drift"
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(s2)
PY
printf '%s\n' "$VALID_MANIFEST" | grep -v '      required: \[raw-nas, derived-nas\]' > "$_mk_tmp/m.yaml"
_mk_exit=0
_mk_out=$(python3 "$_mk_tmp/mutlib/check_infra_manifest_schema.py" --manifest "$_mk_tmp/m.yaml" 2>&1) || _mk_exit=$?
rm -rf "$_mk_tmp"
if [ "$_mk_exit" -eq 0 ] && ! printf '%s' "$_mk_out" | grep -q "필수 필드 누락: required"; then
  echo "OK PASS: AC-2 MK schema_required_off → required 위반 소멸 + exit 0 (RED-flip, 검사 load-bearing)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-2 MK schema_required_off — exit=$_mk_exit"
  echo "  output: $_mk_out"
  FAIL=$((FAIL+1))
fi
echo

echo "── AC-3 D2 startup fail-closed (exit 78 EX_CONFIG + 자원 ID loud) ──"
validator_case "AC-3 required 미설정 → BOOT-REFUSED(exit 78) + raw-nas" 78 \
  "BOOT-REFUSED" "" PYTHONIOENCODING=utf-8 -- --unit collector --manifest "$FIXTURE_MANIFEST"
validator_case "AC-3 미설정 자원 ID(raw-nas) loud 로그" 78 \
  "raw-nas" "" PYTHONIOENCODING=utf-8 -- --unit collector --manifest "$FIXTURE_MANIFEST"
validator_case "AC-3 계약(3) 빈 값 reject (RAW_NAS_URL='  ')" 78 \
  "STARTUP-FAILCLOSED" "" "RAW_NAS_URL=  " PYTHONIOENCODING=utf-8 -- --unit collector --manifest "$FIXTURE_MANIFEST"
validator_case "AC-3 계약(4) optional_degradable → degrade+WARN 계속(exit 0)" 0 \
  "DEGRADED" "" RAW_NAS_URL=http://nas PYTHONIOENCODING=utf-8 -- --unit collector --manifest "$FIXTURE_MANIFEST"
validator_case "AC-3 계약(4) mode 엔트리 부재 = required 취급(writer, exit 78)" 78 \
  "STARTUP-FAILCLOSED" "" PYTHONIOENCODING=utf-8 -- --unit writer --manifest "$FIXTURE_MANIFEST"
validator_case "AC-3 unit 미선언 → fail-closed(78, '감지 비활성' 금지)" 78 \
  "실행단위 미선언" "" PYTHONIOENCODING=utf-8 -- --unit ghost --manifest "$FIXTURE_MANIFEST"
# F-CR-2724-1: dangling rid(plane A 미정의) × optional_degradable → manifest 무결성 실패 =
#   mode 무관 exit 78 + STARTUP-OK 부재 (::error:: 발화 후 DEGRADED→exit 0 fail-open 금지).
_dg_tmp=$(mktemp -d)
printf '%s\n' 'infra_resources:
  resources:
    - id: raw-nas
      canonical_env: RAW_NAS_URL
      aliases:
        accepted: []
  execution_units:
    collector:
      required: [raw-nas, ghost-res]
      resource_modes:
        raw-nas: required
        ghost-res: optional_degradable
        ghost-res_degraded_behavior: "ghost skip"' > "$_dg_tmp/m.yaml"
validator_case "AC-3 dangling×optional_degradable → mode 무관 exit 78 + STARTUP-OK 부재 (F-CR-2724-1)" 78 \
  "plane A 미정의" "STARTUP-OK" RAW_NAS_URL=http://nas PYTHONIOENCODING=utf-8 -- --unit collector --manifest "$_dg_tmp/m.yaml"
rm -rf "$_dg_tmp"
# MK missing_masked: missing 판정 삼킴 → BOOT-REFUSED 소멸 + exit 0 (RED-flip).
_mm_tmp=$(mktemp -d)
mkdir -p "$_mm_tmp/mutlib"
cp "$PARSER_PY" "$SCHEMA_PY" "$_mm_tmp/mutlib/"
python3 - "$VALIDATOR_PY" "$_mm_tmp/mutlib/infra_startup_validator.py" <<'PY'
import sys
s = open(sys.argv[1], encoding="utf-8").read()
s2 = s.replace("    if missing:", "    if False:  # MUTANT-missing-masked", 1)
assert s2 != s, "anchor drift"
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(s2)
PY
_mm_exit=0
_mm_out=$(python3 "$_mm_tmp/mutlib/infra_startup_validator.py" --unit collector --manifest "$FIXTURE_MANIFEST" 2>&1) || _mm_exit=$?
rm -rf "$_mm_tmp"
if [ "$_mm_exit" -eq 0 ] && ! printf '%s' "$_mm_out" | grep -q "BOOT-REFUSED"; then
  echo "OK PASS: AC-3 MK missing_masked → BOOT-REFUSED 소멸 + exit 0 (RED-flip, exit-masking 금지 load-bearing)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-3 MK missing_masked — exit=$_mm_exit"
  echo "  output: $_mm_out"
  FAIL=$((FAIL+1))
fi
echo

echo "── AC-9 allow-set parity (스캐너/startup 동일 manifest 허용집합 diff 0) ──"
_p_union=$(python3 "$VALIDATOR_PY" --emit-allow-set --manifest "$FIXTURE_MANIFEST" 2>&1 | grep -oE 'union=.*$' | head -1)
# 스캐너측 classified 산출 — 경로는 argv 로 전달 (heredoc 내 문자열 삽입은 Windows Git Bash 의
#   MSYS 경로 변환을 못 받아 open 실패 → argv 전달이 양 플랫폼 안전).
_p_scanner=$(python3 - "$LIB" "$FIXTURE_MANIFEST" <<'PY'
import sys
sys.path.insert(0, sys.argv[1])
import check_infra_resource_drift as d
m = d.parse_manifest(sys.argv[2])
print("union=" + ",".join(sorted(m.classified)))
PY
)
if [ -n "$_p_union" ] && [ "$_p_union" = "$_p_scanner" ]; then
  echo "OK PASS: AC-9 parity diff 0 — startup($_p_union) == scanner($_p_scanner)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-9 parity — startup='$_p_union' scanner='$_p_scanner'"
  FAIL=$((FAIL+1))
fi
# MK deprecated_unclassified (공유 파서, G2 동일 anchor) → PARITY-BROKEN exit 78 트립.
_pm_tmp=$(mktemp -d)
mkdir -p "$_pm_tmp/mutlib"
cp "$SCHEMA_PY" "$VALIDATOR_PY" "$_pm_tmp/mutlib/"
python3 - "$PARSER_PY" "$_pm_tmp/mutlib/check_infra_resource_drift.py" <<'PY'
import sys
s = open(sys.argv[1], encoding="utf-8").read()
s2 = s.replace("            m.classified.add(d)",
               "            pass  # MUTANT-deprecated-unclassified", 1)
assert s2 != s, "anchor drift"
open(sys.argv[2], "w", encoding="utf-8", newline="\n").write(s2)
PY
_pm_exit=0
_pm_out=$(python3 "$_pm_tmp/mutlib/infra_startup_validator.py" --emit-allow-set --manifest "$FIXTURE_MANIFEST" 2>&1) || _pm_exit=$?
rm -rf "$_pm_tmp"
if [ "$_pm_exit" -eq 78 ] && printf '%s' "$_pm_out" | grep -q "PARITY-BROKEN"; then
  echo "OK PASS: AC-9 MK deprecated_unclassified → PARITY-BROKEN exit 78 (parity = 집행 계약, RED-flip)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-9 MK deprecated_unclassified — exit=$_pm_exit"
  echo "  output: $_pm_out"
  FAIL=$((FAIL+1))
fi
echo

echo "── AC-15 채택 경로 3-way ──"
validator_case "AC-15 adopted:true + 누락 → ADOPTION-FAIL(78)" 78 \
  "ADOPTION-FAIL" "" PYTHONIOENCODING=utf-8 -- --adoption-check --manifest "$FIXTURE_MANIFEST"
_a15_tmp=$(mktemp -d)
printf '%s\n  startup_validation:\n    adopted: false\n    reason: "declarative-only consumer"\n' \
  "$VALID_MANIFEST" > "$_a15_tmp/with_reason.yaml"
printf '%s\n  startup_validation:\n    adopted: false\n' "$VALID_MANIFEST" > "$_a15_tmp/no_reason.yaml"
CASE_EXIT=0
CASE_OUT=$(python3 "$VALIDATOR_PY" --adoption-check --manifest "$_a15_tmp/with_reason.yaml" 2>&1) || CASE_EXIT=$?
_judge "AC-15 미채택 + 사유 → NOT-ADOPTED-PASS(0, 비적용)" 0 "NOT-ADOPTED-PASS" ""
CASE_EXIT=0
CASE_OUT=$(python3 "$VALIDATOR_PY" --adoption-check --manifest "$_a15_tmp/no_reason.yaml" 2>&1) || CASE_EXIT=$?
_judge "AC-15 미채택 + 사유부재 → ADOPTION-FAIL(78)" 78 "ADOPTION-FAIL" ""
rm -rf "$_a15_tmp"
echo

echo "── AC-19 discriminating fixture pair (env -i self-contained, 센티넬 판별) ──"
# env -i: 자원 키(RAW_NAS_URL 등) 상속 0 보증. python 구동 필수 키만 재주입 — Linux CI 는 PATH 만으로
#   충분, Windows(Git Bash) 는 python 런처가 SYSTEMROOT/LOCALAPPDATA 등을 요구해 존재 시만 승계
#   (자원 키가 아니므로 self-containment 무손상).
_envi() {
  local keep=(PATH="$PATH" PYTHONIOENCODING=utf-8)
  local k
  for k in SYSTEMROOT SystemRoot LOCALAPPDATA APPDATA USERPROFILE PATHEXT TEMP TMP; do
    if [ -n "$(eval "printf '%s' \"\${$k:-}\"")" ]; then
      keep+=("$k=$(eval "printf '%s' \"\${$k}\"")")
    fi
  done
  env -i "${keep[@]}" "$@"
}
_e_exit=0
_e_out=$(_envi python3 "$FIXTURE_DIR/refimpl_enforced.py" 2>&1) || _e_exit=$?
if [ "$_e_exit" -eq 78 ] && ! printf '%s' "$_e_out" | grep -q "$SENTINEL" \
   && printf '%s' "$_e_out" | grep -q "raw-nas"; then
  echo "OK PASS: AC-19 enforced 미설정 → startup 단계 exit 78 + 센티넬 부재 + raw-nas loud (선언O+대조O=PASS 형상)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-19 enforced — exit=$_e_exit (expected 78 + no sentinel)"
  echo "  output: $_e_out"
  FAIL=$((FAIL+1))
fi
_e2_exit=0
_e2_out=$(_envi RAW_NAS_URL=http://nas python3 "$FIXTURE_DIR/refimpl_enforced.py" 2>&1) || _e2_exit=$?
if [ "$_e2_exit" -eq 0 ] && printf '%s' "$_e2_out" | grep -q "$SENTINEL"; then
  echo "OK PASS: AC-19 enforced 설정 → business 도달(센티넬) + exit 0"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-19 enforced 설정 — exit=$_e2_exit"
  echo "  output: $_e2_out"
  FAIL=$((FAIL+1))
fi
_u_exit=0
_u_out=$(_envi python3 "$FIXTURE_DIR/refimpl_unenforced.py" 2>&1) || _u_exit=$?
if [ "$_u_exit" -ne 0 ] && [ "$_u_exit" -ne 78 ] && printf '%s' "$_u_out" | grep -q "$SENTINEL"; then
  echo "OK PASS: AC-19 unenforced → 센티넬 출력 후 late-crash(exit $_u_exit ≠ 0/78) (선언O+대조X=FAIL 형상 판별)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-19 unenforced — exit=$_u_exit (expected 비0/비78 + sentinel)"
  echo "  output: $_u_out"
  FAIL=$((FAIL+1))
fi

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS cases pass — AC-2/3/9/15/19 discriminating + mutation RED-flip + env -i 판별"
  exit 0
else
  echo "X $FAIL case(s) failed"
  exit 1
fi
