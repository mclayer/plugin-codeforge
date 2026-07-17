#!/usr/bin/env bash
# tests/scripts/test_check-infra-resource-drift.sh
# CFP-2700 (Epic) G2 Phase 2 (구현 lane) — Discriminating self-test for
#   scripts/lib/check_infra_resource_drift.py (infra-resource manifest drift scan D3 + 역색인 D4).
#
# ★ hollow-gate 아님의 증명 (ADR-157 §결정3/6/7/8/9 / ADR-119 execution-backed) — presence-only 금지,
#   실 exit code + FIXED 출력 토큰 결박 + 대표 mutation RED-flip(스캐너 소스 변형 시 test RED = 생존 0):
#   AC-5  미선언 표면 검출 (workflow secrets.<undeclared> → exit 1 + UNDECLARED) + MK undeclared-off
#     · deprecated alias = allow_set 편입(참조돼도 undeclared 아님) + MK deprecated_unclassified
#     · `_env:` 값 앞 pad≥5 검출 (F-CR-003 회귀 봉인 — 구 {0,4} bound 는 침묵 미탐) + MK env_pad_narrow
#   AC-6  orphan 정산 (선언·미참조 → warning+exit0 / --promote-orphan → exit1) + MK orphan-promote-off
#   AC-7  substring 오분류 제외 (team-spec-decompose.yaml 구조판정 = env-key 0 → inert 무증가) + MK signal-always
#   AC-8  역색인(D4) verdict-invariant (역색인 변조/제거해도 exit 불변, side-output) + MK revindex-noop
#   AC-10 none-disguise fail (infra_resources 부재 + 사유부재 + 표면 → exit1 + NONE-DISGUISE) + MK none-off
#   AC-11 none-disguise pass (resources:none + reason + 표면0 → exit0)  [AC-10 대칭 negative]
#   AC-17 wrapper 실 secret dogfood 스캔 (실 repo → exit0, candidates≥floor, inert>0,
#     G6 수렴 ratchet: baseline 0 pair + grandfathered==0) + MK no-secrets(실 repo candidates 급감 =
#     secrets 스캔 load-bearing)
#   AC-22 wrapper-live DEC-3 수렴 (G6): baseline 제거 상태 스캔 = exit 0 + undeclared 0 + grandfathered 0
#     ("non-zero→zero" 의 zero 면 — 정정 전 동일 조건 undeclared=5 는 G6 착수 시 firsthand 재현, PR 기록).
#     fixture discriminating pair(수렴/미수렴) + 역색인 매핑 상세 = `.py` 채널 관할(disjoint 보완).
#   + born-hollow guard(candidates==0 ∧ inert==0 → exit3) + PERF DoS bound.
#
# ★ P1-A shell env-passthrough carve-in (§결정8(vi)) — dual pin (본 채널 = 스캔 표면 축 관할):
#   PIN-POSITIVE `VAR="${VAR}" <cmd>` → 검출 + MK passthrough_off.
#   PIN-NEGATIVE 변수 '읽기' 일반형 → **미검출이 계약** + MK naive_shell_form(재도입 시 FP 오검출 = RED).
#     장래 "shell 도 전부 스캔" 확대가 실측 정밀도 18-20% 회귀를 부르면 이 케이스가 즉시 RED 로 잡는다
#     = 정직 천장이 산문 아닌 **집행 계약**.
#
# ★ baseline 판별력(F-CR-005) + P1-B(monotonic shrink / content_digest) = `.py` 채널 관할:
#   AC-17 의 baseline 결박은 실파일에서 runtime 도출한다(F-CR-007 — 구 `≥3` 하드코딩은 스캐너 주석·.py·.sh
#   3-site drift 원천이었다; G6 부터 기대값 = 0 pair 수렴 ratchet). baseline 로직 hermetic 케이스(subtract /
#   shrink-refuse / shrink-allow / digest-tamper)는 `.py` 채널이 보유 — 본 채널 미중복(disjoint 보완, 과잉설계 회피).
#
# ★ CFP-2719 §3.8 per-class census floor + D4-COV (Phase 2 增分):
#   AC-17a per-class census floor: 선언 class(workflow/script/inert)의 glob 열거 파일 수 0 → exit 3
#     + `per-class census floor` 토큰 (판별 대조: 동일 corpus 전 class 존재 = exit 0 control) + MK
#     script_globs_empty(LIVE_SCRIPT_GLOBS 공동화 → 완전 corpus 에서 floor 가 exit 3 으로 kill —
#     pre-floor merged 코드에서는 exit 0 침묵 생존하는 discriminating 변이, PL 별도 RED-flip 실증).
#     _mkcorpus 가 keepalive 3종을 무조건 주입(signal-free, census 필드 기여 0)해 기존 fixture 의
#     floor 간섭을 봉합. honest-ceiling: 열거≥1 인데 추출만 사망 = floor 맹점 — 그 축은 AC-17
#     count-assert(candidates≥floor)가 흡수한다("모든 hollow 봉인" 아님).
#   D4-COV coverage 방출: --emit-reverse-index → `NOT scanned = ` 토큰 결박 + MK cov_not_scanned_off
#     (NOT-scanned 절 앵커 치환 → 토큰 소멸 = fixture oracle load-bearing 증명). §8.8 fuzz/property =
#     `.py` 채널 관할(disjoint 보완).
#
# hard-gate-self-verification: enrolled
# identity_bearing: true
#   internal-control identity probe = per-class census floor(AC-17a): 선언 class 는 상시 열거>0 이
#   known-answer 이고, 0 열거 = 계기 사망(glob 상수 오타/경로 이동 silent-green)을 즉시 검출한다.
#
# self-contained bash (tests/scripts 관례 — ADR-151 인벤토리 enroll 채널). Exit 0 = 전 케이스 PASS.

set -uo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SSOT_PY="$REPO_ROOT/scripts/lib/check_infra_resource_drift.py"

PASS=0
FAIL=0

# 실 wrapper census 안정 하한 pin (AC-17 non-vacuity). 실측 candidates 는 스캔 범위 확장 시 변동하므로
#   **정확한 현재치를 여기 박지 않는다** (F-CR-007 수치 drift 근절 — 수치 SSOT = 스캐너 실행 출력).
FLOOR=50

# ── manifest fixture (2-plane: resources[] alias + execution_units) ──
MANIFEST='infra_resources:
  resources:
    - id: raw-nas
      canonical_env: RAW_NAS_URL
      aliases:
        accepted: [MINIO_URL]
    - id: api-cred
      canonical_env: SERVICE_API_TOKEN
  execution_units:
    collector:
      required: [raw-nas]'

# ── compose positive control (진짜 compose = services + image + environment) ──
COMPOSE='services:
  db:
    image: postgres:16-alpine
    environment:
      DATABASE_URL: postgres://app@db/app
      REDIS_URL: redis://redis:6379'

# ── decompose negative (파일명 "compose" substring 이나 실 env-key 0 — AC-7) ──
DECOMPOSE='team_spec_decompose:
  mode: full
  STEP_NAME: parse'

WF_UNDECLARED='name: wf
on: {push: {}}
jobs:
  j:
    steps:
      - run: echo ${{ secrets.ROGUE_TOKEN }}'

WF_DECLARED='name: wf
on: {push: {}}
jobs:
  j:
    steps:
      - run: echo ${{ secrets.RAW_NAS_URL }}'

NOINFRA_YAML='project: demo
atlassian:
  confluence:
    api_token_env: "ROGUE_TOKEN"'

NONEOK_YAML='infra_resources:
  resources: none
  reason: this project has no infra resource dependencies'

# ── deprecated alias 계열 (F-CR-004: classified.add(d) mutant 가 전건 생존 = kill 0 이었음).
#    deprecated = 선언 자원의 sunset 별칭 → 참조돼도 undeclared 아님(allow_set 편입)이 계약.
MANIFEST_DEPRECATED='infra_resources:
  resources:
    - id: raw-nas
      canonical_env: RAW_NAS_URL
      aliases:
        accepted: [MINIO_URL]
        deprecated:
          - name: LEGACY_NAS_URL'

WF_DEPRECATED='name: wf
on: {push: {}}
jobs:
  j:
    steps:
      - run: echo ${{ secrets.LEGACY_NAS_URL }}'

# ── `_env:` pad≥5 (F-CR-003: 구 \s{0,4} bound 는 candidate 로도 미계수 = 침묵 미탐).
#    infra_resources block 밖에 둬야 SELF_EXCLUDE 를 타지 않음(block = 선언면).
PROJ_PAD5='infra_resources:
  resources:
    - id: raw-nas
      canonical_env: RAW_NAS_URL
atlassian:
  confluence:
    api_token_env:     "PAD5_TOKEN"
    other_token_env: "PAD1_TOKEN"'

# ── P1-A carve-in (§결정8(vi)): env-passthrough 자기참조형 = 키 리터럴 position 등가 → 검출 대상.
SH_PASSTHROUGH='#!/usr/bin/env bash
set -euo pipefail
AUDIT_PII_KEY="${AUDIT_PII_KEY}" python3 "$SCRIPT_DIR/lib/redact.py"'

# ── PIN-NEGATIVE (정직 천장 (vi) 의 실행화): shell 변수 "읽기" 일반형 = 미검출이 계약.
#    STORY_KEY(_KEY suffix 라 infra-signal 매치하나 실제론 parse-token — 실측 11 hit 중 6건이 이 계열) /
#    GH_TOKEN 존재검사 / PAGE_TOKEN 자기대입(뒤 명령 없음 = passthrough 아님).
SH_READ_ONLY='#!/usr/bin/env bash
STORY_KEY="${STORY_KEY:-}"
if [ -z "${GH_TOKEN:-}" ]; then
  echo "no token" >&2
fi
PAGE_TOKEN="${PAGE_TOKEN}"
echo "${STORY_KEY}"'

# ── per-class census floor keepalive (CFP-2719 §3.8 NEW-2 봉합) — signal-free 무해 파일 ──
#    선언 3 class(workflow/script/inert) 각각의 glob 열거 ≥1 유지 (census 필드 기여 0 — 기존 케이스의
#    census 수치 기대 무영향). 내용 = 주석만 (secret 참조/env 매핑/quoted 리터럴/passthrough 전부 부재).
KEEPALIVE='# per-class census floor keepalive (CFP-2719 §3.8) — signal-free 무해 파일.
# 목적 = 선언 scan class 의 glob 열거 >=1 유지. census 필드 기여 0.'

# ─────────────────────────────────────────────────────────────────────────────
# _mkcorpus <tmpdir> <project.yaml> [wf.yml] [compose.yml] [decompose.yaml] [scripts/pt.sh]
#   keepalive 3종 무조건 주입 (CFP-2719 §3.8) — AC-17a negative 는 주입 후 rm 로 열거 0 재현.
# ─────────────────────────────────────────────────────────────────────────────
_mkcorpus() {
  local tmp="$1" proj="$2" wf="${3:-}" comp="${4:-}" deco="${5:-}" shs="${6:-}"
  mkdir -p "$tmp/.claude/_overlay" "$tmp/.github/workflows" "$tmp/examples/svc" \
           "$tmp/examples/_floor-keepalive" "$tmp/docs" "$tmp/scripts"
  printf '%s\n' "$proj" > "$tmp/.claude/_overlay/project.yaml"
  printf '%s\n' "$KEEPALIVE" > "$tmp/.github/workflows/_floor_keepalive.yml"
  printf '%s\n' "$KEEPALIVE" > "$tmp/scripts/_floor_keepalive.py"
  printf '%s\n' "$KEEPALIVE" > "$tmp/examples/_floor-keepalive/keepalive.yml"
  [ -n "$wf" ]   && printf '%s\n' "$wf"   > "$tmp/.github/workflows/wf.yml"
  [ -n "$comp" ] && printf '%s\n' "$comp" > "$tmp/examples/svc/compose.yml"
  [ -n "$deco" ] && printf '%s\n' "$deco" > "$tmp/examples/svc/team-spec-decompose.yaml"
  [ -n "$shs" ]  && printf '%s\n' "$shs"  > "$tmp/scripts/pt.sh"
  return 0
}

# lint_case <name> <expected_exit> <expect_token|""> <forbid_token|""> <extra_args> \
#           <project.yaml> [wf] [compose] [decompose] [scripts/pt.sh]
lint_case() {
  local name="$1" eexit="$2" etok="$3" ftok="$4" xargs="$5"
  local proj="$6" wf="${7:-}" comp="${8:-}" deco="${9:-}" shs="${10:-}"
  local tmp exit_code=0 out ok=1
  tmp=$(mktemp -d)
  _mkcorpus "$tmp" "$proj" "$wf" "$comp" "$deco" "$shs"
  # shellcheck disable=SC2086
  out=$(python3 "$SSOT_PY" --repo-root "$tmp" $xargs 2>&1) || exit_code=$?
  [ "$exit_code" -eq "$eexit" ] || ok=0
  if [ -n "$etok" ]; then case "$out" in *"$etok"*) : ;; *) ok=0;; esac; fi
  if [ -n "$ftok" ]; then case "$out" in *"$ftok"*) ok=0;; esac; fi
  rm -rf "$tmp"
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (exit $exit_code)"
    PASS=$((PASS+1))
  else
    echo "X FAIL: $name — expected exit=$eexit expect='$etok' forbid='$ftok', got exit=$exit_code"
    echo "  output: $out"
    FAIL=$((FAIL+1))
  fi
}

# mutant_case <name> <mutation_kind> <expected_exit> <expect_token|""> <forbid_token|""> <extra_args> \
#             <project.yaml> [wf] [compose] [decompose] [scripts/pt.sh]
#   SSOT 를 python 문자열치환으로 mutate → fixture 실행 → 오분류/verdict 변화 확증 (mutation-kill).
mutant_case() {
  local name="$1" kind="$2" eexit="$3" etok="$4" ftok="$5" xargs="$6"
  local proj="$7" wf="${8:-}" comp="${9:-}" deco="${10:-}" shs="${11:-}"
  local tmp exit_code=0 out mutant ok=1
  tmp=$(mktemp -d)
  _mkcorpus "$tmp" "$proj" "$wf" "$comp" "$deco" "$shs"
  mutant="$tmp/mutant.py"
  python3 - "$SSOT_PY" "$mutant" "$kind" <<'PY'
import sys
src_path, out_path, kind = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src_path, encoding="utf-8").read()
if kind == "undeclared_off":
    s2 = s.replace(
        "undeclared_all = [s for s in live_surfaces if s.key not in manifest.classified]",
        "undeclared_all = []", 1)
elif kind == "orphan_promote_off":
    s2 = s.replace("if orphans and args.promote_orphan:", "if orphans and False:", 1)
elif kind == "signal_always":
    s2 = s.replace("def _is_infra_signal(token):",
                   "def _is_infra_signal(token):\n    return True  # MUTANT-signal-always", 1)
elif kind == "revindex_noop":
    s2 = s.replace("def _emit_reverse_index(live_surfaces, manifest):",
                   "def _emit_reverse_index(live_surfaces, manifest):\n    return  # MUTANT-revindex-noop", 1)
elif kind == "none_off":
    s2 = s.replace("if hollow_none and candidates >= 1:", "if False and candidates >= 1:", 1)
elif kind == "no_secrets":
    s2 = s.replace("def _scan_workflow(physical, rel):",
                   "def _scan_workflow(physical, rel):\n    return []  # MUTANT-no-secrets", 1)
elif kind == "deprecated_unclassified":
    s2 = s.replace("            m.classified.add(d)",
                   "            pass  # MUTANT-deprecated-unclassified", 1)
elif kind == "env_pad_narrow":
    s2 = s.replace(r"_env:\s{0,40}", r"_env:\s{0,4}", 1)
elif kind == "passthrough_off":
    s2 = s.replace("            mm = _RE_SHELL_ENV_PASSTHROUGH.match(code)",
                   "            mm = None  # MUTANT-passthrough-off", 1)
elif kind == "naive_shell_form":
    # §결정7(b) FM1 봉인 위반(naive `${VAR}` 읽기 스캔, 실측 정밀도 18-20%)의 재도입 시뮬레이션.
    s2 = s.replace("            mm = _RE_SHELL_ENV_PASSTHROUGH.match(code)",
                   "            mm = re.search(r'\\$\\{([A-Z][A-Z0-9_]{2,64})', code)"
                   "  # MUTANT-naive-shell-form", 1)
elif kind == "script_globs_empty":
    # CFP-2719 MK-17a: script class glob 상수 공동화 → per-class census floor 가 exit 3 으로 kill
    #   (pre-floor merged 코드에서는 exit 0 침묵 생존 — discriminating 변이).
    s2 = s.replace('LIVE_SCRIPT_GLOBS = ("scripts/**/*.py", "scripts/**/*.sh")',
                   "LIVE_SCRIPT_GLOBS = ()  # MUTANT-script-globs-empty", 1)
elif kind == "cov_not_scanned_off":
    # CFP-2719 MK-COV: coverage NOT-scanned 절 앵커 치환 → D4-COV fixture oracle load-bearing 증명.
    s2 = s.replace('"NOT scanned = ', '"MUTANT-cov-off = ', 1)
else:
    s2 = s
assert s2 != s, "mutation did not apply — anchor drift (kind=%s)" % kind
open(out_path, "w", encoding="utf-8").write(s2)
PY
  # shellcheck disable=SC2086
  out=$(python3 "$mutant" --repo-root "$tmp" $xargs 2>&1) || exit_code=$?
  [ "$exit_code" -eq "$eexit" ] || ok=0
  if [ -n "$etok" ]; then case "$out" in *"$etok"*) : ;; *) ok=0;; esac; fi
  if [ -n "$ftok" ]; then case "$out" in *"$ftok"*) ok=0;; esac; fi
  rm -rf "$tmp"
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (mutant($kind) exit $exit_code — RED-flip 확증, 로직 load-bearing)"
    PASS=$((PASS+1))
  else
    echo "X FAIL: $name — mutant($kind) expected exit=$eexit expect='$etok' forbid='$ftok', got exit=$exit_code"
    echo "  output: $out"
    FAIL=$((FAIL+1))
  fi
}

# _census_count <output> <field>  — census 라인에서 `<field>=NNN` 추출.
_census_count() {
  printf '%s\n' "$1" | grep -oE "$2=[0-9]+" | head -1 | grep -oE "[0-9]+" || echo -1
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2700 G2: infra-resource-drift — discriminating self-test (.sh)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

echo "── AC-5 미선언 표면 검출 (workflow secrets.<undeclared> → exit 1 + UNDECLARED) ──"
lint_case "AC-5 undeclared secret ROGUE_TOKEN → FLAG" 1 \
  "::warning::check-infra-resource-drift: UNDECLARED" "" "" \
  "$MANIFEST" "$WF_UNDECLARED" "$COMPOSE"
mutant_case "AC-5 MK undeclared_off → 미검출(RED, exit 0 PASS)" undeclared_off 0 \
  "PASS" "UNDECLARED" "" \
  "$MANIFEST" "$WF_UNDECLARED" "$COMPOSE"
echo

echo "── AC-5 deprecated alias = allow_set 편입 (F-CR-004 mutant kill 확보) ──"
lint_case "AC-5 deprecated alias 참조 → undeclared 아님(exit 0)" 0 \
  "PASS" "LEGACY_NAS_URL" "" \
  "$MANIFEST_DEPRECATED" "$WF_DEPRECATED" "$COMPOSE"
mutant_case "AC-5 MK deprecated_unclassified → 정당 sunset 별칭 오검출(RED, exit 1)" deprecated_unclassified 1 \
  "env-key=LEGACY_NAS_URL" "" "" \
  "$MANIFEST_DEPRECATED" "$WF_DEPRECATED" "$COMPOSE"
echo

echo "── AC-5 \`_env:\` pad≥5 검출 (F-CR-003 회귀 봉인 — 구 bound 는 침묵 미탐) ──"
lint_case 'F-CR-003 pad≥5 _env: → UNDECLARED FLAG(exit 1)' 1 \
  "env-key=PAD5_TOKEN" "" "" \
  "$PROJ_PAD5" "" "$COMPOSE"
mutant_case "F-CR-003 MK env_pad_narrow → PAD5 침묵 미탐 재현(RED)" env_pad_narrow 1 \
  "env-key=PAD1_TOKEN" "PAD5_TOKEN" "" \
  "$PROJ_PAD5" "" "$COMPOSE"
echo

echo "── P1-A PIN-POSITIVE: shell env-passthrough \`VAR=\"\${VAR}\" <cmd>\` 검출 (§결정8(vi) carve-in) ──"
lint_case "P1-A passthrough AUDIT_PII_KEY → UNDECLARED FLAG(exit 1)" 1 \
  "env-key=AUDIT_PII_KEY" "" "" \
  "$MANIFEST" "" "$COMPOSE" "" "$SH_PASSTHROUGH"
lint_case "P1-A passthrough form=passthrough 표기" 1 \
  "form=passthrough" "" "" \
  "$MANIFEST" "" "$COMPOSE" "" "$SH_PASSTHROUGH"
mutant_case "P1-A MK passthrough_off → 미탐(RED, exit 0 PASS)" passthrough_off 0 \
  "PASS" "AUDIT_PII_KEY" "" \
  "$MANIFEST" "" "$COMPOSE" "" "$SH_PASSTHROUGH"
echo

echo "── P1-A PIN-NEGATIVE: shell 변수 '읽기' 일반형 = **미검출이 계약** (정직 천장 (vi) 집행) ──"
# 이 케이스가 RED 면 = naive form/bare 스캔이 재도입된 것(실측 정밀도 18-20% 회귀) → 천장이 산문 아닌 계약.
lint_case "PIN-NEG STORY_KEY/GH_TOKEN/PAGE_TOKEN 읽기 → 미검출(exit 0)" 0 \
  "PASS" "STORY_KEY" "" \
  "$MANIFEST" "" "$COMPOSE" "" "$SH_READ_ONLY"
lint_case "PIN-NEG candidates 로도 미계수 (천장 (vi))" 0 \
  "candidates_scanned=0" "GH_TOKEN" "" \
  "$MANIFEST" "" "$COMPOSE" "" "$SH_READ_ONLY"
mutant_case "PIN-NEG MK naive_shell_form → STORY_KEY FP 오검출(RED-flip = tripwire 발동)" naive_shell_form 1 \
  "env-key=STORY_KEY" "" "" \
  "$MANIFEST" "" "$COMPOSE" "" "$SH_READ_ONLY"
echo

echo "── AC-6 orphan 정산 (선언·미참조 자원) ──"
lint_case "AC-6 orphan default → warning + exit 0" 0 \
  "::warning::check-infra-resource-drift: ORPHAN — resource-id=api-cred" "" "" \
  "$MANIFEST" "$WF_DECLARED" "$COMPOSE"
lint_case "AC-6 orphan --promote-orphan → exit 1" 1 \
  "ORPHAN — resource-id=api-cred" "" "--promote-orphan" \
  "$MANIFEST" "$WF_DECLARED" "$COMPOSE"
mutant_case "AC-6 MK orphan_promote_off → --promote-orphan 무력(RED, exit 0)" orphan_promote_off 0 \
  "PASS" "" "--promote-orphan" \
  "$MANIFEST" "$WF_DECLARED" "$COMPOSE"
echo

echo "── AC-7 substring 오분류 제외 (team-spec-decompose 구조판정 = env-key 0) ──"
# 진짜 compose 만 inert 2(DATABASE_URL/REDIS_URL); decompose 는 구조/infra-signal 0 → inert 무증가.
_ac7_tmp=$(mktemp -d)
_mkcorpus "$_ac7_tmp" "$MANIFEST" "" "$COMPOSE" "$DECOMPOSE"
_ac7_out=$(python3 "$SSOT_PY" --repo-root "$_ac7_tmp" 2>&1); _ac7_exit=$?
_ac7_inert=$(_census_count "$_ac7_out" "inert_skipped")
_ac7_ok=1
[ "$_ac7_exit" -eq 0 ] || _ac7_ok=0
[ "$_ac7_inert" -eq 2 ] || _ac7_ok=0          # decompose 기여 0 (compose 2 만)
case "$_ac7_out" in *"undeclared=0"*) : ;; *) _ac7_ok=0;; esac
rm -rf "$_ac7_tmp"
if [ "$_ac7_ok" -eq 1 ]; then
  echo "OK PASS: AC-7 decompose 구조판정 제외 (inert_skipped=$_ac7_inert = compose-only, decompose 기여 0)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-7 — exit=$_ac7_exit inert_skipped=$_ac7_inert (expected exit 0, inert 2)"
  echo "  output: $_ac7_out"
  FAIL=$((FAIL+1))
fi
# MK signal_always: infra-signal 무차별 True → decompose STEP_NAME 오분류 → inert 증가(≥3).
_ac7m=$(mktemp -d); _mkcorpus "$_ac7m" "$MANIFEST" "" "$COMPOSE" "$DECOMPOSE"
_ac7mut="$_ac7m/mutant.py"
python3 - "$SSOT_PY" "$_ac7mut" <<'PY'
import sys
s = open(sys.argv[1], encoding="utf-8").read()
s2 = s.replace("def _is_infra_signal(token):",
               "def _is_infra_signal(token):\n    return True  # MUTANT-signal-always", 1)
assert s2 != s, "anchor drift"
open(sys.argv[2], "w", encoding="utf-8").write(s2)
PY
_ac7m_out=$(python3 "$_ac7mut" --repo-root "$_ac7m" 2>&1) || true
_ac7m_inert=$(_census_count "$_ac7m_out" "inert_skipped")
rm -rf "$_ac7m"
if [ "$_ac7m_inert" -gt 2 ]; then
  echo "OK PASS: AC-7 MK signal_always → inert_skipped=$_ac7m_inert>2 (decompose 오분류 = 구조판정 load-bearing, RED-flip)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-7 MK signal_always — inert_skipped=$_ac7m_inert (expected >2)"
  echo "  output: $_ac7m_out"
  FAIL=$((FAIL+1))
fi
echo

echo "── AC-8 역색인(D4) verdict-invariant (변조/제거해도 verdict 불변, side-output I-1) ──"
_ac8_tmp=$(mktemp -d); _mkcorpus "$_ac8_tmp" "$MANIFEST" "$WF_DECLARED" "$COMPOSE"
_ac8_noidx=$(python3 "$SSOT_PY" --repo-root "$_ac8_tmp" 2>&1); _ac8_e1=$?
_ac8_idx=$(python3 "$SSOT_PY" --repo-root "$_ac8_tmp" --emit-reverse-index 2>&1); _ac8_e2=$?
_ac8_ok=1
[ "$_ac8_e1" -eq "$_ac8_e2" ] || _ac8_ok=0                            # verdict 불변(flag 유무 무관)
case "$_ac8_idx" in *"referenced_by="*) : ;; *) _ac8_ok=0;; esac      # 역색인 방출 확인(orphan 라인과 무충돌 토큰)
case "$_ac8_noidx" in *"referenced_by="*) _ac8_ok=0;; esac            # flag 없으면 미방출
rm -rf "$_ac8_tmp"
if [ "$_ac8_ok" -eq 1 ]; then
  echo "OK PASS: AC-8 reverse-index emit + verdict-invariant (exit $_ac8_e1==$_ac8_e2, resource-id emit gated by flag)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-8 — e1=$_ac8_e1 e2=$_ac8_e2 (verdict 불변 실패 또는 역색인 방출 이상)"
  FAIL=$((FAIL+1))
fi
# MK revindex_noop: 역색인 방출 제거 → resource-id 소멸(RED-flip) BUT verdict exit 불변(I-1 증명).
mutant_case "AC-8 MK revindex_noop → referenced_by= 소멸(RED) but exit 불변(I-1)" revindex_noop 0 \
  "" "referenced_by=" "--emit-reverse-index" \
  "$MANIFEST" "$WF_DECLARED" "$COMPOSE"
echo

echo "── AC-10 none-disguise fail (infra_resources 부재 + 사유부재 + 표면 → exit1 + NONE-DISGUISE) ──"
lint_case "AC-10 none-disguise (no infra_resources + secret) → FLAG" 1 \
  "::warning::check-infra-resource-drift: NONE-DISGUISE" "" "" \
  "$NOINFRA_YAML" "$WF_UNDECLARED" "$COMPOSE"
mutant_case "AC-10 MK none_off → NONE-DISGUISE 소멸(RED-flip token)" none_off 1 \
  "" "NONE-DISGUISE" "" \
  "$NOINFRA_YAML" "$WF_UNDECLARED" "$COMPOSE"
echo

echo "── AC-11 none-disguise pass (resources:none + reason + 표면0 → exit0) ──"
lint_case "AC-11 none-ok (resources:none + reason + inert only) → PASS" 0 \
  "PASS" "NONE-DISGUISE" "" \
  "$NONEOK_YAML" "" "$COMPOSE"
echo

echo "── born-hollow guard (candidates==0 ∧ inert==0 → exit3, ADR-157 §결정9) ──"
lint_case "born-hollow (manifest present, 표면 0, examples 0) → FAIL exit 3" 3 \
  "FAIL-CLOSED" "" "" \
  "$MANIFEST" "" ""
echo

echo "── AC-17a per-class census floor (CFP-2719 §3.8 — 선언 class 열거 0 → exit 3) ──"
# 판별 대조: 동일 corpus 전 class 존재(control) = exit 0 ↔ script class 파일 전부 rm 후 = floor exit 3.
#   candidates≥1(wf 선언 키) ∧ inert≥1(compose) 이므로 전역 born-hollow guard 조건이 아님 — floor 판별.
_f17_tmp=$(mktemp -d)
_mkcorpus "$_f17_tmp" "$MANIFEST" "$WF_DECLARED" "$COMPOSE"
_f17_ctl_out=$(python3 "$SSOT_PY" --repo-root "$_f17_tmp" 2>&1); _f17_ctl_exit=$?
rm -rf "$_f17_tmp/scripts"
_f17_out=$(python3 "$SSOT_PY" --repo-root "$_f17_tmp" 2>&1); _f17_exit=$?
rm -rf "$_f17_tmp"
_f17_ok=1
[ "$_f17_ctl_exit" -eq 0 ] || _f17_ok=0    # control: 전 class 존재 = floor 미발동 (clean exit 0)
[ "$_f17_exit" -eq 3 ] || _f17_ok=0        # negative: script class 열거 0 = exit 3
case "$_f17_out" in *"per-class census floor"*) : ;; *) _f17_ok=0;; esac
case "$_f17_out" in *"class=script glob=LIVE_SCRIPT_GLOBS enumerated=0"*) : ;; *) _f17_ok=0;; esac
case "$_f17_out" in *"born-hollow guard"*) _f17_ok=0;; esac   # 전역 guard 아님 판별
if [ "$_f17_ok" -eq 1 ]; then
  echo "OK PASS: AC-17a script class 열거 0 → floor exit 3 (control exit $_f17_ctl_exit=0 대조 판별)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-17a — control_exit=$_f17_ctl_exit(expect 0) exit=$_f17_exit(expect 3)"
  echo "  control output: $_f17_ctl_out"
  echo "  output: $_f17_out"
  FAIL=$((FAIL+1))
fi
# MK-17a: LIVE_SCRIPT_GLOBS 공동화 mutant — 완전 corpus(keepalive 전 class + signal 파일)에서
#   floor 가 exit 3 으로 잡아야 kill. pre-floor merged 코드에서는 exit 0 침묵 생존(discriminating —
#   PL 별도 RED-flip 실증). honest-ceiling: 열거≥1 인데 추출만 사망 = floor 맹점(AC-17 count-assert 흡수).
mutant_case "AC-17a MK script_globs_empty → floor exit 3 (glob 상수 사망 검출)" script_globs_empty 3 \
  "per-class census floor" "" "" \
  "$MANIFEST" "$WF_DECLARED" "$COMPOSE"
echo

echo "── D4-COV coverage 방출 (--emit-reverse-index → scanned/NOT-scanned 토큰, CFP-2719 §8.1) ──"
lint_case "D4-COV coverage NOT-scanned(honest-ceiling) 토큰 방출" 0 \
  "NOT scanned = " "" "--emit-reverse-index" \
  "$MANIFEST" "$WF_DECLARED" "$COMPOSE"
mutant_case "D4-COV MK cov_not_scanned_off → NOT scanned 소멸(RED — oracle load-bearing)" cov_not_scanned_off 0 \
  "coverage: scanned = " "NOT scanned" "--emit-reverse-index" \
  "$MANIFEST" "$WF_DECLARED" "$COMPOSE"
echo

echo "── argparse 오류 → exit 2 ──"
_bad_exit=0; python3 "$SSOT_PY" --nonexistent-flag >/dev/null 2>&1 || _bad_exit=$?
if [ "$_bad_exit" -eq 2 ]; then
  echo "OK PASS: argparse 오류 → exit 2"
  PASS=$((PASS+1))
else
  echo "X FAIL: argparse 오류 exit=$_bad_exit (expected 2)"
  FAIL=$((FAIL+1))
fi
echo

echo "── AC-17 wrapper 실 secret dogfood 스캔 (실 repo → exit0, candidates≥$FLOOR, inert>0, G6 수렴 ratchet) ──"
# F-CR-007: debt count 하드코딩 금지 → baseline 실파일에서 runtime 도출. G6(AC-22): 5 pair 전건 manifest
#   등재로 baseline 5→0 shrink 완료 — 이후 결박은 `0 pair + grandfathered==0`(수렴 유지 ratchet).
#   baseline subtract 로직 자체의 non-vacuity 는 `.py` 채널 hermetic 케이스가 결박(F-CR-005 결합 분리).
_bl_pairs=$(grep -cE '^  env_key:' "$REPO_ROOT/docs/infra-resource-baseline.yaml" || true)
_ac17_out=$(python3 "$SSOT_PY" --repo-root "$REPO_ROOT" 2>&1); _ac17_exit=$?
_ac17_cand=$(_census_count "$_ac17_out" "candidates_scanned")
_ac17_inert=$(_census_count "$_ac17_out" "inert_skipped")
_ac17_undecl=$(_census_count "$_ac17_out" "undeclared")
_ac17_gf=$(_census_count "$_ac17_out" "grandfathered")
_ac17_ok=1
[ "$_ac17_exit" -eq 0 ] || _ac17_ok=0
[ "${_ac17_cand:-0}" -ge "$FLOOR" ] || _ac17_ok=0
[ "${_ac17_inert:-0}" -ge 1 ] || _ac17_ok=0        # born-red 아님 (examples compose inert>0)
[ "${_ac17_undecl:-9}" -eq 0 ] || _ac17_ok=0       # 실 wrapper new undeclared 0
[ -f "$REPO_ROOT/docs/infra-resource-baseline.yaml" ] || _ac17_ok=0   # 파일 자체는 존재(digest 대상)
[ "${_bl_pairs:-9}" -eq 0 ] || _ac17_ok=0          # G6 ratchet: baseline 0 pair (신규 debt = manifest 등재로 해소)
[ "${_ac17_gf:-9}" -eq 0 ] || _ac17_ok=0           # G6 ratchet: grandfathered==0 (수렴 유지)
if [ "$_ac17_ok" -eq 1 ]; then
  echo "OK PASS: AC-17 wrapper dogfood (exit 0, candidates=$_ac17_cand≥$FLOOR, inert=$_ac17_inert>0, undeclared=$_ac17_undecl, baseline pair=$_bl_pairs==0, grandfathered=$_ac17_gf==0 — G6 수렴 ratchet)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-17 — exit=$_ac17_exit candidates=$_ac17_cand inert=$_ac17_inert undeclared=$_ac17_undecl gf=$_ac17_gf baseline_pairs=$_bl_pairs"
  echo "  output: $_ac17_out"
  FAIL=$((FAIL+1))
fi
# canonical secret 실 방출 확인 (역색인 resource-id). G6 갱신: confluence-user-email canonical =
#   ATLASSIAN_USER_EMAIL (구 CONFLUENCE_USER_EMAIL 은 accepted alias 로 강등) + AUDIT_PII_KEY 신규.
_ac17_ri=$(python3 "$SSOT_PY" --repo-root "$REPO_ROOT" --emit-reverse-index 2>&1) || true
_canon_ok=1
for k in ANTHROPIC_API_KEY AUDIT_PII_KEY CODEFORGE_CROSS_REPO_PAT ATLASSIAN_API_TOKEN \
         ATLASSIAN_USER_EMAIL CONFLUENCE_BASE_URL CONFLUENCE_SPACE_ID \
         DOCKER_HUB_TOKEN GITHUB_TOKEN SSH_KEY_PASSPHRASE; do
  case "$_ac17_ri" in *"canonical_env=$k"*) : ;; *) _canon_ok=0; echo "  missing canonical_env=$k";; esac
done
# 2계열 수렴 negative: 구 canonical 이 canonical 로 재등장하면 수렴 회귀.
case "$_ac17_ri" in *"canonical_env=CONFLUENCE_USER_EMAIL"*) _canon_ok=0; echo "  CONFLUENCE_USER_EMAIL 이 canonical 로 잔존 (accepted alias 여야 함 — AC-22 회귀)";; esac
if [ "$_canon_ok" -eq 1 ]; then
  echo "OK PASS: AC-17 canonical secret 역색인 방출 (10종 + 구 canonical 강등 확인)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-17 canonical secret 방출 누락/수렴 회귀"
  FAIL=$((FAIL+1))
fi
# AC-22 wrapper-live 수렴 (G6): baseline 제거 상태에서도 exit 0 + undeclared 0 + grandfathered 0
#   ("non-zero→zero" 의 zero 면 — baseline subtract 개입 0 을 --baseline 비존재 경로로 보증).
_ac22_out=$(python3 "$SSOT_PY" --repo-root "$REPO_ROOT" --baseline "$REPO_ROOT/docs/__no-such-baseline__.yaml" 2>&1); _ac22_exit=$?
_ac22_undecl=$(_census_count "$_ac22_out" "undeclared")
_ac22_gf=$(_census_count "$_ac22_out" "grandfathered")
if [ "$_ac22_exit" -eq 0 ] && [ "${_ac22_undecl:-9}" -eq 0 ] && [ "${_ac22_gf:-9}" -eq 0 ]; then
  echo "OK PASS: AC-22 wrapper-live 수렴 — baseline 없이 exit 0 + undeclared=0 + grandfathered=0 (선언만으로 zero)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-22 — exit=$_ac22_exit undeclared=$_ac22_undecl grandfathered=$_ac22_gf (expected 전부 0)"
  echo "  output: $_ac22_out"
  FAIL=$((FAIL+1))
fi
# MK no_secrets: 실 repo secrets 스캔 제거 → candidates 급감(<floor) = secrets 스캔 load-bearing.
_ns_mut=$(mktemp -d)/mutant.py; mkdir -p "$(dirname "$_ns_mut")"
python3 - "$SSOT_PY" "$_ns_mut" <<'PY'
import sys
s = open(sys.argv[1], encoding="utf-8").read()
s2 = s.replace("def _scan_workflow(physical, rel):",
               "def _scan_workflow(physical, rel):\n    return []  # MUTANT-no-secrets", 1)
assert s2 != s, "anchor drift"
open(sys.argv[2], "w", encoding="utf-8").write(s2)
PY
_ns_out=$(python3 "$_ns_mut" --repo-root "$REPO_ROOT" 2>&1) || true
_ns_cand=$(_census_count "$_ns_out" "candidates_scanned")
rm -rf "$(dirname "$_ns_mut")"
if [ "${_ns_cand:-999}" -lt "$FLOOR" ] && [ "${_ns_cand:-999}" -lt "${_ac17_cand:-0}" ]; then
  echo "OK PASS: AC-17 MK no_secrets → candidates=$_ns_cand < floor $FLOOR (< 실측 $_ac17_cand — secrets 스캔 load-bearing, RED-flip)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-17 MK no_secrets — candidates=$_ns_cand (expected < $FLOOR and < $_ac17_cand)"
  FAIL=$((FAIL+1))
fi
echo

echo "── PERF (born-safe DoS bound — 적대적 초장문 라인 < 5s) ──"
_perf_tmp=$(mktemp -d)
mkdir -p "$_perf_tmp/.claude/_overlay" "$_perf_tmp/scripts"
printf '%s\n' "$MANIFEST" > "$_perf_tmp/.claude/_overlay/project.yaml"
python3 - "$_perf_tmp/scripts/dos.py" <<'PY'
import sys
# 단일 물리라인 1.6MB, quoted infra-signal 리터럴 포함 (truncate 후 판정).
open(sys.argv[1], "w", encoding="utf-8").write('X = "FOO_TOKEN" + ' + '"a" '*400000 + '\n')
PY
_perf=$(python3 - "$SSOT_PY" "$_perf_tmp" <<'PY'
import subprocess, sys, time
py, root = sys.argv[1], sys.argv[2]
t0 = time.perf_counter()
try:
    subprocess.run([sys.executable, py, "--repo-root", root],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
    print("%.3f" % (time.perf_counter() - t0))
except subprocess.TimeoutExpired:
    print("999.0")
PY
)
rm -rf "$_perf_tmp"
if awk "BEGIN{exit !($_perf < 5.0)}"; then
  echo "OK PASS: PERF DoS 1.6MB-line wall=${_perf}s (<5s — born-safe bound 성립)"
  PASS=$((PASS+1))
else
  echo "X FAIL: PERF DoS 1.6MB-line wall=${_perf}s (>=5s — bound 파손 의심)"
  FAIL=$((FAIL+1))
fi

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS cases pass — AC-5/6/7/8/10/11/17/17a/22 + D4-COV discriminating + mutation-kill + born-hollow + PERF 결박"
  exit 0
else
  echo "X $FAIL case(s) failed"
  exit 1
fi
