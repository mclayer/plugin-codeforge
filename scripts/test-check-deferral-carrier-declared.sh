#!/usr/bin/env bash
# scripts/test-check-deferral-carrier-declared.sh
# CFP-2591 Phase 2 — Discriminating self-test for check-deferral-carrier-declared.sh (ADR-060 §결정 6).
#
# (b) deferral carrier declared (no-TBD) lint — governance surface 전반에서 미해결 placeholder
#   carrier(deferred_followup_cfp: TBD / CFP-TBD / unwired FU-N-N) 를 grep-기반 mechanical 검출 +
#   5축 allowlist 면제 + baseline new-only grandfather subtract 를 양방향 입증 + mutation-kill.
#
# anti-theater test: lint 이 실제로 genuine placeholder 를 잡고 allowlist 가 정탐(history/negation/
#   counterfactual)을 면제함을 양방향 입증. ★핵심 discriminator = CB-CHANNEL (같은 파일 live TBD +
#   history 주석 공존 → live 만 FLAG). content-anchor fixture (line# 하드코딩 0).
#
# mutation testing (production code 깨뜨리면 RED — mutation 생존 0):
#  - CB-Mut-1: 검출 정규식(_RE_TBD_CARRIER) 제거 → CB-DET-1 RED (placeholder 미검출).
#  - CB-Mut-2: allowlist 무력화(allowlist_match 항상 None) → CB-ALLOW-1 RED (history 과검출).
#  - CB-Mut-3: history/comment allowlist over-broaden(#-anchor 제거 → 들여쓴 라인 전체 면제)
#              → CB-CHANNEL RED (live TBD silent 면제 = false-negative).
#  - CB-Mut-4: SELF_EXCLUDE 제거 → CB-SELF RED (self 파일 self-FLAG).
#
# documented-limitation (fixture 작성 대상 아님, 주석 기재):
#  - path-within-line allowlist: 토큰 인접(±40) 파일경로(.sh/.py/...) 참조 시 면제 →
#    `FU-N-N # scripts/absent.sh (미배선)` 처럼 unwired FU 가 absent script 를 가리켜도 exempt
#    (silent false-negative 가능). CB-DET-3-note 로 실측 문서화 + ArchitectPL 회부 (발견 사항).
#
# Exit code:
#  0 = all tests pass (discriminating test validates lint)
#  1 = any test fails (lint may not be detecting mutations correctly)
#
# Prior art: scripts/test-check-lane-count-ssot.sh (mktemp -d + trap + cp production + run_test +
#   mutate_and_check literal-replace via env-var). scripts/test-check-deferred-followup-reconcile.sh
#   (sibling gate self-test — baseline gen fixture).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PASS=0
FAIL=0

# 임시 테스트 repo (★NON-git — git ls-files 실패 → os.walk fallback 로 --paths 파일 발견.
#   lane-count 하니스 동일 전제. git-init 하면 미-track 파일이 ls-files 에서 누락되어 SETUP 오탐).
TMP_REPO=$(mktemp -d)
trap "rm -rf '$TMP_REPO'" EXIT

mkdir -p "$TMP_REPO/scripts/lib"
mkdir -p "$TMP_REPO/docs"

# production script 복사 (격리 실행 — mutation 시 복사본만 변조).
#   check_deferred_followup_reconcile.py = load_baseline import 의존 (동일 scripts/lib/ sibling).
cp "$REPO_ROOT/scripts/check-deferral-carrier-declared.sh" "$TMP_REPO/scripts/"
cp "$REPO_ROOT/scripts/lib/check_deferral_carrier_declared.py" "$TMP_REPO/scripts/lib/"
cp "$REPO_ROOT/scripts/lib/check_deferred_followup_reconcile.py" "$TMP_REPO/scripts/lib/"

PROD_PY="$TMP_REPO/scripts/lib/check_deferral_carrier_declared.py"
PROD_PY_BAK="$TMP_REPO/scripts/lib/check_deferral_carrier_declared.py.bak"
cp "$PROD_PY" "$PROD_PY_BAK"

# ─────────────────────── low-level assert ────────────────────────────────────
# assert_carrier <name> <out> <ec> <should yes/no> <exp_exit> <must|-> <mustnot|-> <desc>
assert_carrier() {
  local name="$1" out="$2" ec="$3" should="$4" exp="$5" must="$6" mustnot="$7" desc="$8"
  local ok=1
  [ "$ec" -eq "$exp" ] || ok=0
  local has_flag=0
  if echo "$out" | grep -q "::warning::check-deferral-carrier-declared: FLAG"; then has_flag=1; fi
  if [ "$should" = "yes" ] && [ "$has_flag" -ne 1 ]; then ok=0; fi
  if [ "$should" = "no" ]  && [ "$has_flag" -ne 0 ]; then ok=0; fi
  if [ "$must" != "-" ] && ! echo "$out" | grep -qE "$must"; then ok=0; fi
  if [ "$mustnot" != "-" ] &&   echo "$out" | grep -qE "$mustnot"; then ok=0; fi
  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $name (FLAG=$has_flag exit $ec)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  exp_exit=$exp got=$ec should_flag=$should has_flag=$has_flag must='$must' mustnot='$mustnot'"
    echo "  Description: $desc"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
  return 0
}

# ─────────────────────── run_test (single-file fixture) ──────────────────────
# run_test <name> <fixture_rel> <content> <should yes/no> <exp_exit> <desc> [must|-] [mustnot|-]
run_test() {
  local name="$1" rel="$2" content="$3" should="$4" exp="$5" desc="$6"
  local must="${7:--}" mustnot="${8:--}"
  printf '%s\n' "$content" > "$TMP_REPO/$rel"
  local out ec=0
  out=$( cd "$TMP_REPO" && bash scripts/check-deferral-carrier-declared.sh check --repo-root . --paths "$rel" 2>&1 ) || ec=$?
  assert_carrier "$name" "$out" "$ec" "$should" "$exp" "$must" "$mustnot" "$desc"
}

# run_test_setup: 검사 경로 부재 → exit 2 (SETUP, fixture 미사용)
run_test_setup() {
  local name="$1" desc="$2"
  local out ec=0
  out=$( cd "$TMP_REPO" && bash scripts/check-deferral-carrier-declared.sh check --repo-root . --paths "docs/__nonexistent__" 2>&1 ) || ec=$?
  if [ "$ec" -eq 2 ]; then
    echo "✓ PASS: $name (exit 2 SETUP)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name (expected exit 2, got $ec)"
    echo "  $desc"; echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
  return 0
}

echo "═══════════════ check-deferral-carrier-declared self-test (CFP-2591) ═══════════════"
echo ""
echo "── Group 2: detection (placeholder carrier) ──"

# CB-DET-1 (AC-1) TBD carrier
run_test "CB-DET-1 TBD carrier" "docs/cb_det1.md" \
  '  deferred_followup_cfp: TBD (section split ...)' \
  yes 1 "deferred_followup_cfp: TBD → FLAG (AC-1)"

# CB-DET-2 (AC-1) CFP-TBD sibling placeholder
run_test "CB-DET-2 CFP-TBD placeholder" "docs/cb_det2.md" \
  '        - CFP-TBD   # sibling placeholder' \
  yes 1 "CFP-TBD 토큰 → FLAG (라인 선두 아닌 주석은 comment-line 축 비해당, AC-1)"

# CB-DET-3 (AC-2/5) unwired FU marker (★path-ref allowlist 회피 위해 인접 파일경로 미포함)
run_test "CB-DET-3 unwired FU marker" "docs/cb_det3.md" \
  '  - FU-9999-1  (배선 workflow 미발의 — placeholder)' \
  yes 1 "FU-9999-1 unwired 마커 → FLAG (AC-2/5)"

# CB-DET-3-note: packet-literal 변형(인접 .sh 경로 포함)은 path-within-line allowlist 로 EXEMPT.
#   실측 documented-limitation — path-ref 축이 unwired FU→absent script silent 면제 (발견 사항, ArchitectPL 회부).
run_test "CB-DET-3-note path-ref exemption (documented-limitation)" "docs/cb_det3n.md" \
  '  - FU-9999-1  # scripts/check-absent.sh (미배선)' \
  no 0 "인접 .sh 경로 참조 → path-within-line allowlist 면제 (silent false-negative — ArchitectPL 회부)"

echo ""
echo "── Group 2: allowlist 면제 (history / negation / counterfactual) ──"

# CB-ALLOW-1 (EC-11 history) — 주석(#) 라인 history axis
run_test "CB-ALLOW-1 history comment" "docs/cb_allow1.md" \
  '# 과거 CFP-1559 는 CFP-TBD 로 남겨 silent-drop 됐다 (교훈)' \
  no 0 "# 선두 history 주석 CFP-TBD → no-FLAG (history axis, EC-11)"

# CB-ALLOW-2 negation — 토큰 인접 부정 마커
run_test "CB-ALLOW-2 negation" "docs/cb_allow2.md" \
  'deferred_followup_cfp 는 TBD 금지 — 반드시 CFP 발급' \
  no 0 "TBD 금지 부정 인접 → no-FLAG (negation axis)"

# CB-ALLOW-3 counterfactual — 가정 조건절
run_test "CB-ALLOW-3 counterfactual" "docs/cb_allow3.md" \
  '만약 carrier 를 TBD 로 남기면 게이트 blind 가 된다' \
  no 0 "만약 ... TBD ... blind 가정문 → no-FLAG (counterfactual axis)"

echo ""
echo "── Group 2: ★CB-CHANNEL (same-file live+history split — 핵심 discriminator) ──"

# CB-CHANNEL (AC-14/8) — 같은 파일 live TBD(검출) + history 주석(면제) 공존 → live 만 FLAG.
#   line 1 = live TBD (FLAG), line 2 = history 주석 (exempt). Kills CB-Mut-3 (history over-broaden).
run_test "CB-CHANNEL same-file live+history split" "docs/cb_chan.md" \
  "$(printf '  deferred_followup_cfp: TBD\n# 과거 issue 에서 CFP-TBD 로 남겨 silent-drop 됐다 (history)')" \
  yes 1 "live TBD(line1) FLAG + history 주석(line2) exempt → FLAG live-only (AC-14/8, CB-Mut-3 kill)" \
  "cb_chan.md:1" "cb_chan.md:2"

echo ""
echo "── Group 2: self-scan boundary (§7.3.3) ──"

# CB-SELF — SELF_EXCLUDE 경로에 TBD 넣어도 no-FLAG. clean 파일 동반(files>0 유지 → SETUP 아님).
#   scan ONLY self-excluded → files 0 → exit 2 이므로 clean 파일 필수. Kills self-FLAG mutant(CB-Mut-4).
printf '%s\n' '  deferred_followup_cfp: TBD' > "$TMP_REPO/docs/deferred-followup-baseline.yaml"
printf '%s\n' 'clean content — no placeholder token' > "$TMP_REPO/docs/cb_self_clean.md"
self_out=$( cd "$TMP_REPO" && bash scripts/check-deferral-carrier-declared.sh check --repo-root . \
              --paths docs/deferred-followup-baseline.yaml docs/cb_self_clean.md 2>&1 ) || self_ec=$?
self_ec=${self_ec:-0}
assert_carrier "CB-SELF self-exclude (baseline.yaml TBD 미검출)" "$self_out" "$self_ec" \
  no 0 "-" "-" "SELF_EXCLUDE 경로(baseline.yaml) TBD → 미스캔 no-FLAG + clean 파일로 files>0 (§7.3.3)"

echo ""
echo "── Group 2: baseline grandfather (new-only) ──"

# CB-ALLOW-GF — 기존 surface 는 grandfathered(면제), 신규 distinct 토큰만 FLAG (new-only).
#   ★(b) lint 는 content_digest tamper-verify 안 함(gate 와 다름) → hand-crafted baseline 유효.
printf '%s\n' '  deferred_followup_cfp: TBD' > "$TMP_REPO/docs/cb_gf.md"
cat > "$TMP_REPO/cb_baseline.yaml" <<'YAML'
declaration_surfaces:
- locator: docs/cb_gf.md:1
  token: 'deferred_followup_cfp: TBD'
  reason: pre-existing (CFP-2591 baseline snapshot grandfather)
YAML
gf_out=$( cd "$TMP_REPO" && bash scripts/check-deferral-carrier-declared.sh check --repo-root . \
            --paths docs/cb_gf.md --baseline cb_baseline.yaml 2>&1 ) || gf_ec=$?
gf_ec=${gf_ec:-0}
assert_carrier "CB-ALLOW-GF grandfather (기존 surface 면제)" "$gf_out" "$gf_ec" \
  no 0 "GRANDFATHERED 1" "-" "baseline declaration_surfaces 매치 → grandfathered no-FLAG"

# CB-ALLOW-GF control — 같은 파일에 신규 distinct 토큰(CFP-TBD) 추가 → 그것만 FLAG (new-only).
#   (동일 TBD 를 한 줄 더 넣으면 line-drift tolerant 매치로 grandfathered 되므로 distinct 토큰 사용.)
printf '%s\n' '  deferred_followup_cfp: TBD' '  legacy_ref: CFP-TBD' > "$TMP_REPO/docs/cb_gf.md"
gf2_out=$( cd "$TMP_REPO" && bash scripts/check-deferral-carrier-declared.sh check --repo-root . \
             --paths docs/cb_gf.md --baseline cb_baseline.yaml 2>&1 ) || gf2_ec=$?
gf2_ec=${gf2_ec:-0}
assert_carrier "CB-ALLOW-GF control (신규 distinct 토큰만 FLAG)" "$gf2_out" "$gf2_ec" \
  yes 1 "NEW 1 / GRANDFATHERED 1" "-" "신규 CFP-TBD 만 new-debt FLAG (기존 TBD grandfathered — new-only)"

echo ""
echo "── Group 2: exit semantics ──"

# no-token clean → exit 0
run_test "CB-EXIT-0 no-token clean" "docs/cb_clean.md" \
  '평범한 문서 라인, placeholder 토큰 없음' \
  no 0 "토큰 0 → exit 0 (PASS)"

# token 1+ (no baseline) → exit 1  (pure detection)
run_test "CB-EXIT-1 token → exit 1" "docs/cb_exit1.md" \
  '  deferred_followup_cfp: TBD' \
  yes 1 "baseline 미지정 → pure detection → 토큰 1+ → exit 1"

# 검사 경로 부재 → exit 2 (SETUP)
run_test_setup "CB-EXIT-2 SETUP (검사 경로 부재)" "존재하지 않는 glob → files 0 → exit 2"

# --baseline 명시인데 missing → exit 2 (SETUP)
bl_out=$( cd "$TMP_REPO" && bash scripts/check-deferral-carrier-declared.sh check --repo-root . \
            --paths docs/cb_clean.md --baseline nonexistent-baseline.yaml 2>&1 ) || bl_ec=$?
bl_ec=${bl_ec:-0}
if [ "$bl_ec" -eq 2 ]; then
  echo "✓ PASS: CB-EXIT-2b SETUP (--baseline missing) (exit 2)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: CB-EXIT-2b (--baseline missing, expected exit 2 got $bl_ec)"
  echo "  Output: $bl_out"
  FAIL=$((FAIL+1))
fi

# ─────────────────────── mutation testing (production 변조 → fixture RED) ────
echo ""
echo "── mutation testing (production 변조 시 RED — mutation 생존 0) ──"

# mutate_and_check <mut_name> <old_str> <new_str> <paths_string> <orig_should_flag yes/no> <desc>
#   PROD_PY 1회 literal 치환(env-var — backslash/heredoc 안전). no-op = fail-loud (anchor stale).
#   caller 가 fixture 파일을 미리 write (Group 2 에서 이미 생성됨 → 재사용). orig 반대 결과 = kill.
mutate_and_check() {
  local mut_name="$1" old_str="$2" new_str="$3" paths="$4" orig="$5" desc="$6"
  cp "$PROD_PY_BAK" "$PROD_PY"
  local changed
  changed=$( MUT_OLD="$old_str" MUT_NEW="$new_str" MUT_PATH="$PROD_PY" python3 - <<'PYEOF'
import os, io
path = os.environ["MUT_PATH"]
old = os.environ["MUT_OLD"]
new = os.environ["MUT_NEW"]
src = io.open(path, encoding="utf-8").read()
if old not in src:
    print("NOOP")
else:
    io.open(path, "w", encoding="utf-8").write(src.replace(old, new, 1))
    print("CHANGED")
PYEOF
)
  if [ "$changed" != "CHANGED" ]; then
    echo "✗ FAIL: $mut_name — mutation anchor NOT FOUND (stale anchor, 치환 no-op)"
    echo "  old_str: $old_str"
    cp "$PROD_PY_BAK" "$PROD_PY"
    FAIL=$((FAIL+1))
    return 0
  fi
  local out ec=0
  # shellcheck disable=SC2086
  out=$( cd "$TMP_REPO" && bash scripts/check-deferral-carrier-declared.sh check --repo-root . --paths $paths 2>&1 ) || ec=$?
  local has_flag=0
  if echo "$out" | grep -q "::warning::check-deferral-carrier-declared: FLAG"; then has_flag=1; fi
  cp "$PROD_PY_BAK" "$PROD_PY"
  local killed=0
  if [ "$orig" = "yes" ] && [ "$has_flag" -eq 0 ]; then killed=1; fi
  if [ "$orig" = "no" ]  && [ "$has_flag" -eq 1 ]; then killed=1; fi
  if [ "$killed" -eq 1 ]; then
    echo "✓ PASS: $mut_name killed (mutation 생존 0)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $mut_name SURVIVED (has_flag=$has_flag orig=$orig — lint 결함 가능)"
    echo "  Description: $desc"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
  return 0
}

# CB-Mut-1: 검출 정규식(_RE_TBD_CARRIER) never-match → CB-DET-1 RED (TBD 미검출).
mutate_and_check "CB-Mut-1 (검출 정규식 제거)" \
  '_RE_TBD_CARRIER = re.compile(r"deferred_followup_cfp:\s{0,3}TBD")' \
  '_RE_TBD_CARRIER = re.compile(r"__NEVER_MATCH_TBD__")' \
  "docs/cb_det1.md" "yes" \
  "검출 정규식 제거 시 deferred_followup_cfp: TBD(CB-DET-1) 미검출 = RED"

# CB-Mut-2: allowlist_match 항상 None → CB-ALLOW-1 RED (history 과검출).
mutate_and_check "CB-Mut-2 (allowlist 무력화)" \
  'def allowlist_match(line, token):
    """' \
  'def allowlist_match(line, token):
    return None  # CB-MUT-2
    """' \
  "docs/cb_allow1.md" "no" \
  "allowlist 무력화 시 history 주석(CB-ALLOW-1) 과검출 = RED"

# CB-Mut-3: comment-line allowlist over-broaden(#-anchor 제거 → 들여쓴 라인 전체 면제)
#   → CB-CHANNEL RED (live TBD line1 silent 면제 = false-negative).
mutate_and_check "CB-Mut-3 (history over-broaden)" \
  '_RE_ALLOW_COMMENT_LINE = re.compile(r"^\s{0,8}#")' \
  '_RE_ALLOW_COMMENT_LINE = re.compile(r"^\s{0,8}")' \
  "docs/cb_chan.md" "yes" \
  "comment-line #-anchor 제거 시 live TBD(들여쓴 라인) 까지 silent 면제 = false-negative RED (CB-CHANNEL)"

# CB-Mut-4: SELF_EXCLUDE 제거 → CB-SELF RED (self 파일 self-FLAG).
mutate_and_check "CB-Mut-4 (SELF_EXCLUDE 제거)" \
  'if rp_norm in SELF_EXCLUDE_PATHS:' \
  'if rp_norm in ():' \
  "docs/deferred-followup-baseline.yaml docs/cb_self_clean.md" "no" \
  "SELF_EXCLUDE 제거 시 self 경로(baseline.yaml) TBD self-FLAG 과검출 = RED (CB-SELF)"

# ─────────────────────── 종합 ───────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  PASS: $PASS / FAIL: $FAIL"
echo "═══════════════════════════════════════════════════════════════"

if [ "$FAIL" -gt 0 ]; then
  echo "✗ self-test FAILED (lint 결함 또는 mutation 생존 — 회귀 차단)"
  exit 1
fi
echo "✓ self-test PASSED (Group 2 detection/allowlist/channel/self/grandfather + 4 mutation kill)"
echo "  documented-limitation: path-within-line allowlist unwired-FU-→-absent-script exemption"
echo "    (CB-DET-3-note 실측 — ArchitectPL 회부 대상 발견 사항)"
exit 0
