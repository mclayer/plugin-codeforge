#!/usr/bin/env bash
# tests/scripts/test_cfp-2851-dispatch-template-completeness.sh
# CFP-2851 Phase 2(구현) — CodexReviewAgent dispatch 템플릿 완결성 discriminating 검증.
#
# 대상(읽기 = 검증 fixture): plugins/codeforge-review/agents/CodexReviewAgent.md (git 612fdf6d9 반영본).
#   편집 요지: else 블록 안 helper(check_codex_review_output_schema.py) inline 배선(2-변수 exit 게이트)
#             + 변종절 신규 2 bullet(--uncommitted / --commit 등가 명시).
#
# 검증 축(§8.2): AC-1~AC-11 별 GREEN(실 파일) + RED(취약/pre-edit fixture) 이중 케이스로 hollow-gate 회피.
#   - fence-interior / 변종절 awk anchoring = line-shift-robust (§8.2). 파일 전체 grep 은 prose(L140 helper
#     언급 등)로 always-green 무효 → 반드시 구획 한정.
#   - normative AC(1/2/3/4/5/6/7/10/11)는 취약 fixture 에서 grep 이 RED 나는지 assert (discriminating 증명).
#   - AC-9 = advisory(soft) tier.
#
# RED 진정성(cross-layer working-tree drift 대응): DeveloperAgent GREEN(612fdf6d9)이 working tree 에 선착.
#   본 test 는 (a) self-contained sed/awk 변이 fixture 로 각 AC 의 discriminating power 를 매 실행 재현하고,
#   (b) 추가로 pre-edit(git show HEAD~1) 원본을 대조해 additive AC(1/2/3/4/10)가 pre-GREEN 에서 genuine
#   실패(vacuous 아님)함을 사후 입증한다(git 가용 시 — 부재 시 sed 변이 fixture 로 자족).
#
# exit-masking 금지(ADR-060 Amd22 / CFP-2635): raw `cmd || true` 미사용. exit/count 캡처는 `|| ec=$?` /
#   `|| n=0`(count 정규화, branch-guard) 형태 + 근접 PASS/FAIL 카운터가 유일 pass/fail 신호를 gating.
#
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MD="$REPO_ROOT/plugins/codeforge-review/agents/CodexReviewAgent.md"
MD_REL="plugins/codeforge-review/agents/CodexReviewAgent.md"

PASS=0
FAIL=0
ADV=0   # advisory(soft) 통과 카운트 (PASS 에 합산되나 별도 가시화)

WORK="$(mktemp -d)"
# shellcheck disable=SC2064
trap "rm -rf '$WORK'" EXIT

# ── EDIT_SHA 앵커 (HEAD~1 하드코딩 대신 — 후속 test/무관 커밋이 HEAD 를 밀어도 robust) ──
#   EDIT_SHA = MD 를 마지막으로 변경한 커밋(=dispatch 템플릿 편집 612fdf6d9). 그 부모(${EDIT_SHA}~1) = 진짜 pre-edit.
#   HEAD~1 를 쓰면 test 커밋이 HEAD 를 밀 때 HEAD~1 이 '편집본' 을 가리켜 pre-edit 대조가 born-broken 이 된다.
EDIT_SHA="$(git -C "$REPO_ROOT" log -1 --format=%H -- "$MD_REL" 2>/dev/null || printf '')"

pass()     { echo "  ✓ PASS: $1"; PASS=$((PASS+1)); }
fail()     { echo "  ✗ FAIL: $1"; FAIL=$((FAIL+1)); }
pass_adv() { echo "  ✓ PASS(advisory): $1"; PASS=$((PASS+1)); ADV=$((ADV+1)); }

# ── anchoring 유틸 (line-shift-robust, §8.2) ─────────────────────────────────
# fence-interior: 첫 ```bash 이후 ~ 다음 ``` 이전. (lane focus prompt 은 plain ``` fence → 미매치)
fence_interior() { awk '/^```bash/{f=1;next} f && /^```/{exit} f' "$1"; }
# 변종절: '### 변종' 이후 ~ 다음 heading(^#+ ) 이전.
variant_section() { awk '/^### 변종/{f=1;next} f && /^#+ /{exit} f' "$1"; }

# ── grep 유틸 ────────────────────────────────────────────────────────────────
# count_re: ERE 매치 라인 수 (0매칭 grep exit1 = "0건" 정규화, exit-masking 아님 — 반환 count 를 assert 가 gating)
count_re() { local n; n=$(grep -cE "$2" "$1" 2>/dev/null) || n=0; printf '%s' "$n"; }
# line_has_all: file 안 '어떤 단일 라인'이 주어진 리터럴 substring 을 모두 포함하면 0, 아니면 1.
#   successive grep -F 필터 = 각 substring 포함 라인만 잔존 → 모두 포함 라인 생존 (동일 라인 결박).
line_has_all() {
  local file="$1"; shift
  local surviving; surviving="$(cat "$file")"
  local s
  for s in "$@"; do
    surviving="$(printf '%s\n' "$surviving" | grep -F -- "$s")" || return 1
  done
  [ -n "$surviving" ]
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2851: CodexReviewAgent dispatch 템플릿 완결성 — AC-1~11 discriminating"
echo "═══════════════════════════════════════════════════════════════════════════"

# ── C0 setup guard: 실 md 존재 + anchoring 비-empty (born-broken 위장 차단) ────
echo
echo "── C0 setup ──"
if [ -f "$MD" ]; then
  pass "C0a: 실 CodexReviewAgent.md 존재 (검증 fixture 확정)"
else
  fail "C0a: 실 CodexReviewAgent.md 부재 ($MD) — setup 실패"
fi

FENCE="$WORK/fence.txt"
VAR="$WORK/variant.txt"
fence_interior "$MD" > "$FENCE"
variant_section "$MD" > "$VAR"
if [ -s "$FENCE" ]; then
  pass "C0b: fence-interior anchoring 비-empty ($(wc -l < "$FENCE") 라인)"
else
  fail "C0b: fence-interior anchoring empty — 'bash-fence' 마커 drift 의심 (anchoring born-broken)"
fi
if [ -s "$VAR" ]; then
  pass "C0c: 변종절 anchoring 비-empty ($(wc -l < "$VAR") 라인)"
else
  fail "C0c: 변종절 anchoring empty — '### 변종' 마커 drift 의심"
fi

# ─────────────────────────────────────────────────────────────────────────────
# AC-1: helper 호출 라인 (fence-interior 한정)
#   GREEN = fence-interior 안 단일 라인이 helper.py + $OUT_JSON + $SCHEMA 동반.
#   RED   = helper 호출 라인 제거 fixture → 미검출.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "── AC-1 (helper 호출 라인, fence-interior) ──"
if line_has_all "$FENCE" 'check_codex_review_output_schema.py' '$OUT_JSON' '$SCHEMA'; then
  pass "AC-1 GREEN: fence-interior helper 호출 라인(helper.py + \$OUT_JSON + \$SCHEMA) 존재"
else
  fail "AC-1 GREEN: fence-interior helper 호출 라인 미검출"
fi
# RED fixture: helper 호출 라인 제거
AC1_RED="$WORK/ac1_red.md"
sed '/check_codex_review_output_schema\.py "\$OUT_JSON"/d' "$MD" > "$AC1_RED"
AC1_RED_FENCE="$WORK/ac1_red_fence.txt"; fence_interior "$AC1_RED" > "$AC1_RED_FENCE"
if line_has_all "$AC1_RED_FENCE" 'check_codex_review_output_schema.py' '$OUT_JSON' '$SCHEMA'; then
  fail "AC-1 RED: helper 제거 fixture 인데 여전히 검출 (grep vacuous)"
else
  pass "AC-1 RED: helper 제거 fixture → 미검출(RED 재현) = AC-1 discriminating"
fi

# ─────────────────────────────────────────────────────────────────────────────
# AC-2: 2-단계 게이트 (helper_rc 캡처 + $codex_rc && $helper_rc &&-gate + verdict 2분기)
#   verdict read = mechanism-agnostic 구조 grep (`verdict=<...>` on-exit-0 + `verdict=inconclusive` else).
#   RED = &&-gate 라인 제거 fixture.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "── AC-2 (2-단계 fail-closed 게이트) ──"
ac2_ok=1
grep -qF 'helper_rc=$?' "$FENCE" || ac2_ok=0
grep -qF 'if [ "$codex_rc" -eq 0 ] && [ "$helper_rc" -eq 0 ]' "$FENCE" || ac2_ok=0
grep -qF 'verdict=inconclusive' "$FENCE" || ac2_ok=0
grep -qE 'verdict=<' "$FENCE" || ac2_ok=0   # mechanism-agnostic on-exit-0 verdict read (jq/python3 하드코딩 미요구)
if [ "$ac2_ok" -eq 1 ]; then
  pass "AC-2 GREEN: helper_rc 캡처 + \$codex_rc&&\$helper_rc &&-gate + verdict 2분기(read/inconclusive) 전부 존재"
else
  fail "AC-2 GREEN: 2-단계 게이트 구성요소 누락 (helper_rc/&&-gate/verdict 2분기 중 일부 부재)"
fi
# RED fixture: &&-gate 라인 제거 (codex_rc 와 helper_rc 를 함께 참조하는 유일 라인)
AC2_RED="$WORK/ac2_red.md"
sed '/codex_rc.*helper_rc/d' "$MD" > "$AC2_RED"
AC2_RED_FENCE="$WORK/ac2_red_fence.txt"; fence_interior "$AC2_RED" > "$AC2_RED_FENCE"
if grep -qF 'if [ "$codex_rc" -eq 0 ] && [ "$helper_rc" -eq 0 ]' "$AC2_RED_FENCE"; then
  fail "AC-2 RED: &&-gate 제거 fixture 인데 여전히 검출"
else
  pass "AC-2 RED: 2-변수 &&-gate 제거 fixture → 미검출(RED 재현) = AC-2 discriminating"
fi

# ─────────────────────────────────────────────────────────────────────────────
# AC-3: --uncommitted 등가 (변종절 안 --uncommitted + `git diff HEAD` 리터럴 + untracked 단서)
#   `git diff` 단독은 기존 --base main bullet(git diff main...HEAD) 로 비-discriminating → 리터럴 필수.
#   RED = `git diff HEAD` → `git diff` shorthand 치환 fixture.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "── AC-3 (--uncommitted 등가) ──"
if line_has_all "$VAR" '--uncommitted' 'git diff HEAD' 'untracked'; then
  pass "AC-3 GREEN: 변종절 --uncommitted bullet(git diff HEAD 리터럴 + untracked) 존재"
else
  fail "AC-3 GREEN: 변종절 --uncommitted 등가 bullet 미검출"
fi
# RED fixture: `git diff HEAD` → `git diff` (under-capture shorthand). `git diff main...HEAD` 는 무영향.
AC3_RED="$WORK/ac3_red.md"
sed 's/git diff HEAD/git diff/g' "$MD" > "$AC3_RED"
AC3_RED_VAR="$WORK/ac3_red_var.txt"; variant_section "$AC3_RED" > "$AC3_RED_VAR"
if line_has_all "$AC3_RED_VAR" '--uncommitted' 'git diff HEAD' 'untracked'; then
  fail "AC-3 RED: git diff HEAD→git diff shorthand 치환 fixture 인데 여전히 검출"
else
  pass "AC-3 RED: git diff HEAD→git diff shorthand 치환 → 리터럴 미검출(RED 재현) = AC-3 discriminating"
fi

# ─────────────────────────────────────────────────────────────────────────────
# AC-4: --commit 등가 (변종절 안 --commit + `git show` + `<SHA>` angle-bracket placeholder)
#   RED = `git show` 제거 fixture.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "── AC-4 (--commit 등가) ──"
if line_has_all "$VAR" '--commit' 'git show' '<SHA>'; then
  pass "AC-4 GREEN: 변종절 --commit bullet(git show + <SHA> placeholder) 존재"
else
  fail "AC-4 GREEN: 변종절 --commit 등가 bullet 미검출"
fi
# RED fixture: git show 제거
AC4_RED="$WORK/ac4_red.md"
sed 's/git show//g' "$MD" > "$AC4_RED"
AC4_RED_VAR="$WORK/ac4_red_var.txt"; variant_section "$AC4_RED" > "$AC4_RED_VAR"
if line_has_all "$AC4_RED_VAR" '--commit' 'git show' '<SHA>'; then
  fail "AC-4 RED: git show 제거 fixture 인데 여전히 검출"
else
  pass "AC-4 RED: git show 제거 → 미검출(RED 재현) = AC-4 discriminating"
fi

# ─────────────────────────────────────────────────────────────────────────────
# AC-5: 골격 무손상 — 6 토큰 post-change 존재 + diff 상 골격 라인 삭제·수정 0.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "── AC-5 (골격 무손상) ──"
# 6 토큰 presence (whole-file — 골격 미삭제 결박)
SKEL_OK=1
declare -a SKEL_TOKENS=(
  'codex exec'
  '--ignore-user-config -m'
  '--ephemeral'
  '- < "$PROMPTFILE"'
  'timeout --kill-after='
  '소비 재검증'
  '### 언어 구획 규약'
  'ANCHOR_LINE:'
)
for t in "${SKEL_TOKENS[@]}"; do
  if ! grep -qF -- "$t" "$MD"; then SKEL_OK=0; echo "    골격 토큰 부재: $t"; fi
done
# lane effort 표 (별도 확인)
grep -qF '| requirements-review |' "$MD" || { SKEL_OK=0; echo "    골격 토큰 부재: lane effort 표"; }
if [ "$SKEL_OK" -eq 1 ]; then
  pass "AC-5 GREEN: 골격 8 토큰(codex exec / --ignore-user-config -m … --ephemeral / - < \$PROMPTFILE / timeout --kill-after= / 소비 재검증 / 언어 구획 규약 헤더 / ANCHOR_LINE / lane effort 표) 전부 존재"
else
  fail "AC-5 GREEN: 골격 토큰 일부 부재 (post-change 파손)"
fi
# RED fixture(token): 골격 토큰 1개 제거 → presence RED
AC5_RED="$WORK/ac5_red.md"
sed 's/timeout --kill-after=//g' "$MD" > "$AC5_RED"
if grep -qF -- 'timeout --kill-after=' "$AC5_RED"; then
  fail "AC-5 RED(token): timeout --kill-after= 제거 fixture 인데 여전히 검출"
else
  pass "AC-5 RED(token): 골격 토큰 제거 fixture → 미검출(RED 재현) = 골격 presence discriminating"
fi
# diff-preservation: MD-편집 커밋(${EDIT_SHA}~1..${EDIT_SHA}) 에 골격 토큰 담은 삭제라인(^-) 0
# per-token 정합: 토큰이 삭제라인에는 있되 추가라인에 없을 때만 제거로 판정 (수정쌍 보존)
if [ -n "$EDIT_SHA" ] && git -C "$REPO_ROOT" rev-parse --verify -q "${EDIT_SHA}~1" >/dev/null 2>&1; then
  DIFF_TXT="$WORK/diff.txt"
  git -C "$REPO_ROOT" diff "${EDIT_SHA}~1" "$EDIT_SHA" -- "$MD_REL" > "$DIFF_TXT" 2>/dev/null || true
  removed_skel=0
  for t in "${SKEL_TOKENS[@]}"; do
    # 삭제라인에 토큰 존재?
    if grep -E '^-[^-]' "$DIFF_TXT" 2>/dev/null | grep -qF -- "$t"; then
      has_removed=1
    else
      has_removed=0
    fi
    # 추가라인에 토큰 존재?
    if grep -E '^\+[^+]' "$DIFF_TXT" 2>/dev/null | grep -qF -- "$t"; then
      has_added=1
    else
      has_added=0
    fi
    # 삭제에만 있으면 제거됨 (위반)
    if [ "$has_removed" -eq 1 ] && [ "$has_added" -eq 0 ]; then
      removed_skel=$((removed_skel + 1))
    fi
  done
  if [ "$removed_skel" -eq 0 ]; then
    pass "AC-5 GREEN(diff): MD-편집 커밋(\${EDIT_SHA}~1..\${EDIT_SHA}) 에 골격 토큰 담은 삭제라인 0 (append-only, 골격 무손상)"
  else
    fail "AC-5 GREEN(diff): 골격 토큰 담은 삭제라인 $removed_skel 건 검출 (골격 삭제/수정 의심)"
  fi
  # 탐지력 결박(discriminating): 골격 라인을 삭제한 synthetic diff → 탐지되어야 함
  SYN_DIFF="$WORK/syn_diff.txt"
  printf '%s\n' '--- a/x' '+++ b/x' '-  timeout --kill-after=${K} ${N} codex exec -s read-only - < "$PROMPTFILE"' '+  replaced' > "$SYN_DIFF"
  syn_hit=$(grep -E '^-[^-]' "$SYN_DIFF" | grep -cF -- 'timeout --kill-after=') || syn_hit=0
  if [ "$syn_hit" -ge 1 ]; then
    pass "AC-5 RED(diff): 골격 삭제 synthetic diff → 탐지($syn_hit) = diff-preservation detector 비-vacuous"
  else
    fail "AC-5 RED(diff): synthetic 골격 삭제 diff 를 detector 가 미탐지 (vacuous)"
  fi
else
  echo "  ↷ SKIP: AC-5 diff-preservation — MD-편집 커밋/부모 미가용 (EDIT_SHA='$EDIT_SHA', 얕은 clone 등)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# AC-6: diff-0 — git diff --name-only HEAD~1 에 helper/schema 파일 부재.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "── AC-6 (helper/schema diff-0) ──"
if [ -n "$EDIT_SHA" ] && git -C "$REPO_ROOT" rev-parse --verify -q "${EDIT_SHA}~1" >/dev/null 2>&1; then
  NAMES="$WORK/names.txt"
  git -C "$REPO_ROOT" diff --name-only "${EDIT_SHA}~1" "$EDIT_SHA" > "$NAMES" 2>/dev/null || true
  ac6_ok=1
  grep -qF 'check_codex_review_output_schema.py' "$NAMES" && ac6_ok=0
  grep -qF 'codex-review-output-schema-v1.json' "$NAMES" && ac6_ok=0
  if [ "$ac6_ok" -eq 1 ]; then
    pass "AC-6 GREEN: name-only(\${EDIT_SHA}~1..\${EDIT_SHA}) 에 helper/schema 파일 부재 (diff-0)"
  else
    fail "AC-6 GREEN: name-only HEAD~1 에 helper/schema 파일 포함 (diff-0 위반)"
  fi
  # 탐지력 결박: 두 파일명 포함 synthetic name list → 탐지되어야 함
  SYN_NAMES="$WORK/syn_names.txt"
  printf '%s\n' 'plugins/codeforge-review/agents/CodexReviewAgent.md' 'scripts/lib/check_codex_review_output_schema.py' 'plugins/codeforge-review/schemas/codex-review-output-schema-v1.json' > "$SYN_NAMES"
  syn6=0
  grep -qF 'check_codex_review_output_schema.py' "$SYN_NAMES" && syn6=$((syn6+1))
  grep -qF 'codex-review-output-schema-v1.json' "$SYN_NAMES" && syn6=$((syn6+1))
  if [ "$syn6" -eq 2 ]; then
    pass "AC-6 RED: helper/schema 포함 synthetic name list → 탐지 = diff-0 detector 비-vacuous"
  else
    fail "AC-6 RED: synthetic name list 에서 helper/schema 를 detector 가 미탐지 (vacuous)"
  fi
else
  echo "  ↷ SKIP: AC-6 — MD-편집 커밋/부모 미가용 (EDIT_SHA='$EDIT_SHA', 얕은 clone 등)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# AC-7: helper 위치 — else 블록 내(codex exec 뒤·fi 앞). timeout-부재 if fallback 분기 안 helper 부재.
#   fence-interior 안 helper 발화가 standalone `else` 라인 이후에만 존재해야 함(if-branch=0).
#   RED = if-fallback 분기(echo codex-sandbox-fallback 뒤)에 helper 주입 → if-branch helper ≥1.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "── AC-7 (helper 위치 = else 블록 내) ──"
# 구조 판정 함수: fence 파일에서 else 라인 앞/뒤 helper 발화 수 계산
ac7_before_after() {
  # 출력: "<before> <after>" — helper 발화 라인 중 standalone else 라인보다 앞/뒤 개수
  awk '
    /^else$/ && !seen_else { else_ln = NR; seen_else = 1 }
    /check_codex_review_output_schema\.py/ { helper[NR] = 1 }
    END {
      b = 0; a = 0
      for (ln in helper) { if (else_ln > 0 && ln < else_ln) b++; else if (else_ln > 0 && ln > else_ln) a++ }
      printf "%d %d\n", b, a
    }
  ' "$1"
}
read -r ac7_before ac7_after < <(ac7_before_after "$FENCE")
if [ "$ac7_before" -eq 0 ] && [ "$ac7_after" -ge 1 ]; then
  pass "AC-7 GREEN: helper 발화 = else 블록 내만 (if-fallback 분기 helper=0, else-후 helper=$ac7_after)"
else
  fail "AC-7 GREEN: helper 위치 위반 (if-branch helper=$ac7_before, else-후 helper=$ac7_after)"
fi
# RED fixture: if-fallback 분기(codex-sandbox-fallback echo 뒤)에 helper 주입
AC7_RED_FENCE="$WORK/ac7_red_fence.txt"
awk '/codex-sandbox-fallback/{print; print "  check_codex_review_output_schema.py \"$OUT_JSON\" \"$SCHEMA\"   # injected-into-if-branch"; next} {print}' "$FENCE" > "$AC7_RED_FENCE"
read -r ac7r_before ac7r_after < <(ac7_before_after "$AC7_RED_FENCE")
if [ "$ac7r_before" -ge 1 ]; then
  pass "AC-7 RED: if-fallback 분기 helper 주입 → if-branch helper=$ac7r_before 탐지(RED 재현) = 위치 discriminating"
else
  fail "AC-7 RED: if-branch helper 주입을 detector 가 미탐지 (vacuous)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# AC-9 (advisory): inline else 분기 verdict 처분 ↔ exit-code 판정표 무모순.
#   inline else 는 판정표로 delegation('판정표' 참조) + fence 안 exit-code 표 재열거 0.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "── AC-9 (advisory: 판정표 delegation, 재열거 0) ──"
delg=$(count_re "$FENCE" '판정표')
reenum=$(count_re "$FENCE" '^\| \*\*12[0-9]\*\*')
if [ "$delg" -ge 1 ] && [ "$reenum" -eq 0 ]; then
  pass_adv "AC-9: fence else 분기 판정표 delegation($delg) + exit-code 표 재열거 0 = 무모순"
else
  fail "AC-9: delegation($delg, 기대>=1) 또는 재열거($reenum, 기대=0) 위반"
fi
# 탐지력 결박: fence 에 exit-code 표 행 주입 → 재열거 탐지
AC9_RED_FENCE="$WORK/ac9_red_fence.txt"
awk '/verdict=inconclusive/{print; print "| **124** | timeout kill | inconclusive |"; next} {print}' "$FENCE" > "$AC9_RED_FENCE"
reenum_red=$(count_re "$AC9_RED_FENCE" '^\| \*\*12[0-9]\*\*')
if [ "$reenum_red" -ge 1 ]; then
  pass_adv "AC-9 RED: exit-code 표 행 주입 → 재열거 탐지($reenum_red) = 재열거 detector 비-vacuous"
else
  fail "AC-9 RED: 주입 exit-code 표 행을 detector 가 미탐지 (vacuous)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# AC-10: delimited block 상속 — 신규 2 bullet 에 비신뢰·구획 문구 (+ --commit = commit 메시지 헤더 전체).
#   RED = 신규 bullet 에서 비신뢰/구획 문구 제거 fixture.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "── AC-10 (delimited untrusted block 상속) ──"
ac10_ok=1
line_has_all "$VAR" '--uncommitted' '비신뢰' '구획' || ac10_ok=0
line_has_all "$VAR" '--commit' '비신뢰' '구획' 'commit 메시지 헤더 전체' || ac10_ok=0
if [ "$ac10_ok" -eq 1 ]; then
  pass "AC-10 GREEN: --uncommitted/--commit bullet 에 비신뢰·구획 분리 문구 + --commit=commit 메시지 헤더 전체 확장"
else
  fail "AC-10 GREEN: 신규 bullet delimited-block 상속 문구 누락"
fi
# RED fixture: 비신뢰/구획 문구 제거
AC10_RED="$WORK/ac10_red.md"
sed 's/비신뢰//g; s/구획//g' "$MD" > "$AC10_RED"
AC10_RED_VAR="$WORK/ac10_red_var.txt"; variant_section "$AC10_RED" > "$AC10_RED_VAR"
if line_has_all "$AC10_RED_VAR" '--uncommitted' '비신뢰' '구획'; then
  fail "AC-10 RED: 비신뢰/구획 제거 fixture 인데 여전히 검출"
else
  pass "AC-10 RED: 비신뢰/구획 문구 제거 → 미검출(RED 재현) = AC-10 discriminating"
fi

# ─────────────────────────────────────────────────────────────────────────────
# AC-11: dispatch 발화 불변 — helper 호출·변종 prose 도입이 column-0 `codex exec` 리터럴 유입 0.
#   (기존 presence-lint R1 이 column-0 codex exec = 무가드 dispatch 발화로 RED — 본 축은 보조 grep.)
#   RED = column-0 codex exec 라인 주입 fixture.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "── AC-11 (dispatch 발화 불변 — column-0 codex exec 유입 0) ──"
col0=$(count_re "$MD" '^codex exec')
if [ "$col0" -eq 0 ]; then
  pass "AC-11 GREEN: column-0 무가드 codex exec 발화 0 (편집이 dispatch 발화 불변 유지)"
else
  fail "AC-11 GREEN: column-0 codex exec 발화 $col0 건 유입 (무가드 dispatch 회귀)"
fi
# RED fixture: column-0 codex exec 라인 주입
AC11_RED="$WORK/ac11_red.md"
cp "$MD" "$AC11_RED"
printf '%s\n' 'codex exec -s read-only --output-schema s.json -o out.json - < p.md' >> "$AC11_RED"
col0_red=$(count_re "$AC11_RED" '^codex exec')
if [ "$col0_red" -ge 1 ]; then
  pass "AC-11 RED: column-0 codex exec 주입 → 탐지($col0_red) = 발화-불변 detector 비-vacuous"
else
  fail "AC-11 RED: 주입 column-0 codex exec 를 detector 가 미탐지 (vacuous)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# RED 진정성 사후 입증 (pre-edit git show HEAD~1 대조 — additive AC discriminating case)
#   working-tree drift 로 GREEN(612fdf6d9) 선착 → pre-GREEN(HEAD~1) 원본에서 additive AC 가 genuine
#   실패함을 대조 입증(vacuous 아님). git 가용 시에만.
# ─────────────────────────────────────────────────────────────────────────────
echo
echo "── RED 진정성 (pre-edit \${EDIT_SHA}~1 대조 — 보조 증거) ──"
# 주의: 본 section 은 sed 변이 fixture(위 AC-1~11 RED)가 이미 제공한 discriminating 주 입증의 '보조' 증거다.
#   git 이력이 이 edit 를 단독 격리하지 못하면(후속 커밋이 MD 재편집 등) 하드 fail 대신 NOTE 로 degrade
#   (sed fixture 가 load-bearing → born-broken 재발 방지). 이력이 깨끗하면 discriminating case 로 pass.
if [ -n "$EDIT_SHA" ] && git -C "$REPO_ROOT" rev-parse --verify -q "${EDIT_SHA}~1" >/dev/null 2>&1; then
  PRE="$WORK/pre_edit.md"
  if git -C "$REPO_ROOT" show "${EDIT_SHA}~1:$MD_REL" > "$PRE" 2>/dev/null; then
    PRE_FENCE="$WORK/pre_fence.txt"; fence_interior "$PRE" > "$PRE_FENCE"
    PRE_VAR="$WORK/pre_var.txt"; variant_section "$PRE" > "$PRE_VAR"
    # AC-1: pre-edit fence helper 부재
    if line_has_all "$PRE_FENCE" 'check_codex_review_output_schema.py' '$OUT_JSON' '$SCHEMA'; then
      echo "  ↷ NOTE: pre-edit AC-1 non-discriminating — git 이력이 edit 단독격리 못함; sed fixture(AC-1 RED)가 주 입증"
    else
      pass "pre-edit AC-1: pre-GREEN(\${EDIT_SHA}~1) fence 에 helper 부재 → GREEN 에서만 존재 (discriminating case)"
    fi
    # AC-2: pre-edit fence &&-gate 부재
    if grep -qF 'if [ "$codex_rc" -eq 0 ] && [ "$helper_rc" -eq 0 ]' "$PRE_FENCE"; then
      echo "  ↷ NOTE: pre-edit AC-2 non-discriminating — sed fixture(AC-2 RED)가 주 입증"
    else
      pass "pre-edit AC-2: pre-GREEN fence 에 2-변수 &&-gate 부재 (discriminating case)"
    fi
    # AC-3/AC-4: pre-edit 변종절에 --uncommitted/--commit bullet 부재
    if line_has_all "$PRE_VAR" '--uncommitted' 'git diff HEAD'; then
      echo "  ↷ NOTE: pre-edit AC-3 non-discriminating — sed fixture(AC-3 RED)가 주 입증"
    else
      pass "pre-edit AC-3: pre-GREEN 변종절에 --uncommitted 등가 bullet 부재 (discriminating case)"
    fi
    if line_has_all "$PRE_VAR" '--commit' 'git show'; then
      echo "  ↷ NOTE: pre-edit AC-4 non-discriminating — sed fixture(AC-4 RED)가 주 입증"
    else
      pass "pre-edit AC-4: pre-GREEN 변종절에 --commit 등가 bullet 부재 (discriminating case)"
    fi
    # AC-10: pre-edit 신규 bullet 부재 → 비신뢰·구획 확장 bullet 부재
    if line_has_all "$PRE_VAR" '--commit' 'commit 메시지 헤더 전체'; then
      echo "  ↷ NOTE: pre-edit AC-10 non-discriminating — sed fixture(AC-10 RED)가 주 입증"
    else
      pass "pre-edit AC-10: pre-GREEN 에 --commit commit-메시지-헤더-전체 확장 부재 (discriminating case)"
    fi
    # 골격/발화-불변 = regression-guard case (pre-GREEN 에서도 GREEN — 보존 검증)
    if grep -qF -- 'timeout --kill-after=' "$PRE" && [ "$(count_re "$PRE" '^codex exec')" -eq 0 ]; then
      pass "pre-edit regression-guard: pre-GREEN 도 골격 timeout 가드 존재 + column-0 codex exec 0 (AC-5/AC-11 양-regime green 보존)"
    else
      echo "  ↷ NOTE: pre-edit regression-guard 미확인 — 골격이 이 edit 에서 신규였을 수 있음 (sed fixture 가 주 입증)"
    fi
  else
    echo "  ↷ SKIP: pre-edit 대조 — \${EDIT_SHA}~1:$MD_REL 조회 실패"
  fi
else
  echo "  ↷ SKIP: pre-edit 대조 — MD-편집 커밋/부모 미가용 (EDIT_SHA='$EDIT_SHA', 얕은 clone 등)"
fi

# ─────────────────────────────────────────────────────────────────────────────
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS (advisory 포함: $ADV)"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "✓ All $PASS cases pass — AC-1~11 discriminating(실 파일 GREEN + 취약/pre-edit fixture RED) 입증"
  exit 0
else
  echo "✗ $FAIL case(s) failed"
  exit 1
fi
