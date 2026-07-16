#!/usr/bin/env bash
# tests/scripts/test_check-infra-resource-drift.sh
# CFP-2700 (Epic) G2 Phase 2 (구현 lane) — Discriminating self-test for
#   scripts/lib/check_infra_resource_drift.py (infra-resource manifest drift scan D3 + 역색인 D4).
#
# ★ hollow-gate 아님의 증명 (ADR-157 §결정3/6/7/8/9 / ADR-119 execution-backed) — presence-only 금지,
#   실 exit code + FIXED 출력 토큰 결박 + 대표 mutation RED-flip(스캐너 소스 변형 시 test RED = 생존 0):
#   AC-5  미선언 표면 검출 (workflow secrets.<undeclared> → exit 1 + UNDECLARED) + MK undeclared-off
#   AC-6  orphan 정산 (선언·미참조 → warning+exit0 / --promote-orphan → exit1) + MK orphan-promote-off
#   AC-7  substring 오분류 제외 (team-spec-decompose.yaml 구조판정 = env-key 0 → inert 무증가) + MK signal-always
#   AC-8  역색인(D4) verdict-invariant (역색인 변조/제거해도 exit 불변, side-output) + MK revindex-noop
#   AC-10 none-disguise fail (infra_resources 부재 + 사유부재 + 표면 → exit1 + NONE-DISGUISE) + MK none-off
#   AC-11 none-disguise pass (resources:none + reason + 표면0 → exit0)  [AC-10 대칭 negative]
#   AC-17 wrapper 실 secret 9종 dogfood 스캔 (실 repo → exit0, candidates≥floor, inert>0, grandfathered=4)
#     + MK no-secrets(실 repo candidates 급감 = secrets 스캔 load-bearing)
#   + born-hollow guard(candidates==0 ∧ inert==0 → exit3) + PERF DoS bound.
#
# self-contained bash (tests/scripts 관례 — ADR-151 인벤토리 enroll 채널). Exit 0 = 전 케이스 PASS.

set -uo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SSOT_PY="$REPO_ROOT/scripts/lib/check_infra_resource_drift.py"

PASS=0
FAIL=0

# 실 wrapper census floor (AC-17 non-vacuity — 현 실측 candidates_scanned=129, 안정 하한 pin).
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

# ─────────────────────────────────────────────────────────────────────────────
# _mkcorpus <tmpdir> <project.yaml> [wf.yml] [compose.yml] [decompose.yaml]
# ─────────────────────────────────────────────────────────────────────────────
_mkcorpus() {
  local tmp="$1" proj="$2" wf="${3:-}" comp="${4:-}" deco="${5:-}"
  mkdir -p "$tmp/.claude/_overlay" "$tmp/.github/workflows" "$tmp/examples/svc" "$tmp/docs"
  printf '%s\n' "$proj" > "$tmp/.claude/_overlay/project.yaml"
  [ -n "$wf" ]   && printf '%s\n' "$wf"   > "$tmp/.github/workflows/wf.yml"
  [ -n "$comp" ] && printf '%s\n' "$comp" > "$tmp/examples/svc/compose.yml"
  [ -n "$deco" ] && printf '%s\n' "$deco" > "$tmp/examples/svc/team-spec-decompose.yaml"
  return 0
}

# lint_case <name> <expected_exit> <expect_token|""> <forbid_token|""> <extra_args> \
#           <project.yaml> [wf] [compose] [decompose]
lint_case() {
  local name="$1" eexit="$2" etok="$3" ftok="$4" xargs="$5"
  local proj="$6" wf="${7:-}" comp="${8:-}" deco="${9:-}"
  local tmp exit_code=0 out ok=1
  tmp=$(mktemp -d)
  _mkcorpus "$tmp" "$proj" "$wf" "$comp" "$deco"
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
#             <project.yaml> [wf] [compose] [decompose]
#   SSOT 를 python 문자열치환으로 mutate → fixture 실행 → 오분류/verdict 변화 확증 (mutation-kill).
mutant_case() {
  local name="$1" kind="$2" eexit="$3" etok="$4" ftok="$5" xargs="$6"
  local proj="$7" wf="${8:-}" comp="${9:-}" deco="${10:-}"
  local tmp exit_code=0 out mutant ok=1
  tmp=$(mktemp -d)
  _mkcorpus "$tmp" "$proj" "$wf" "$comp" "$deco"
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

echo "── AC-17 wrapper 실 secret dogfood 스캔 (실 repo → exit0, candidates≥$FLOOR, inert>0, grandfathered=4) ──"
_ac17_out=$(python3 "$SSOT_PY" --repo-root "$REPO_ROOT" 2>&1); _ac17_exit=$?
_ac17_cand=$(_census_count "$_ac17_out" "candidates_scanned")
_ac17_inert=$(_census_count "$_ac17_out" "inert_skipped")
_ac17_undecl=$(_census_count "$_ac17_out" "undeclared")
_ac17_gf=$(_census_count "$_ac17_out" "grandfathered")
_ac17_ok=1
[ "$_ac17_exit" -eq 0 ] || _ac17_ok=0
[ "${_ac17_cand:-0}" -ge "$FLOOR" ] || _ac17_ok=0
[ "${_ac17_inert:-0}" -ge 1 ] || _ac17_ok=0        # born-red 아님 (examples compose inert>0)
[ "${_ac17_undecl:-9}" -eq 0 ] || _ac17_ok=0       # 실 wrapper new undeclared 0 (baseline grandfather)
[ "${_ac17_gf:-0}" -ge 3 ] || _ac17_ok=0
if [ "$_ac17_ok" -eq 1 ]; then
  echo "OK PASS: AC-17 wrapper dogfood (exit 0, candidates=$_ac17_cand≥$FLOOR, inert=$_ac17_inert>0, undeclared=$_ac17_undecl, grandfathered=$_ac17_gf)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-17 — exit=$_ac17_exit candidates=$_ac17_cand inert=$_ac17_inert undeclared=$_ac17_undecl gf=$_ac17_gf"
  echo "  output: $_ac17_out"
  FAIL=$((FAIL+1))
fi
# 9종 canonical secret 실 방출 확인 (역색인 resource-id).
_ac17_ri=$(python3 "$SSOT_PY" --repo-root "$REPO_ROOT" --emit-reverse-index 2>&1) || true
_nine_ok=1
for k in ANTHROPIC_API_KEY CODEFORGE_CROSS_REPO_PAT ATLASSIAN_API_TOKEN CONFLUENCE_BASE_URL \
         CONFLUENCE_SPACE_ID CONFLUENCE_USER_EMAIL DOCKER_HUB_TOKEN GITHUB_TOKEN SSH_KEY_PASSPHRASE; do
  case "$_ac17_ri" in *"canonical_env=$k"*) : ;; *) _nine_ok=0; echo "  missing canonical_env=$k";; esac
done
if [ "$_nine_ok" -eq 1 ]; then
  echo "OK PASS: AC-17 9종 canonical secret 역색인 방출 (대상수 9 ≥ 1)"
  PASS=$((PASS+1))
else
  echo "X FAIL: AC-17 9종 canonical secret 방출 누락"
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
  echo "OK All $PASS cases pass — AC-5/6/7/8/10/11/17 discriminating + mutation-kill + born-hollow + PERF 결박"
  exit 0
else
  echo "X $FAIL case(s) failed"
  exit 1
fi
