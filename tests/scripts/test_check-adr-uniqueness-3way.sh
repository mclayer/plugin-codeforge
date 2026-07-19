#!/usr/bin/env bash
# tests/scripts/test_check-adr-uniqueness-3way.sh
# CFP-2563 Phase 2 (QADeveloperAgent) — 3-way ADR uniqueness lint 검증.
# Change Plan CFP-2563 §8 Test Contract 이행:
#   Q1 = lint self-test (born-valid RED→GREEN, hollow-gate 차단) — INV-8/INV-9/INV-10/INV-11 + mu1/mu2/mu3.
#   Q2 = INV-12 file↔row lapse SYNTHETIC fixture (design-review P3-3 fold-in — 실 15-row lapse 는 DeveloperAgent
#        backfill run 이 소비하므로 의존 불가 → isolated synthetic fixture 로 검출 증명).
#
# 대상(구현-under-test, DeveloperAgent 병렬 작성): scripts/lib/check-adr-uniqueness-3way.py
#   계약(§3.3 / §8.7): file명 번호 ↔ frontmatter adr_number ↔ RESERVATION row 3-way 정합 lint,
#   findings 1+ 면 exit 1 (warning tier), clean = exit 0, setup-error = exit 2.
#
# ── 인터페이스 가정(interface-first TDD, §8 미명시 → repo convention 채택) ──────────────────
#   CLI: `python3 check-adr-uniqueness-3way.py [--root <repo-root>]`  (선례: check_whitelist_manifest_3way.py --root)
#        → --root 미지원 시 --repo-root / positional 도 probe (check_adr_cross_ref_consistency.py 선례).
#   scan target: <root>/archive/adr/ADR-*.md  +  <root>/archive/adr/ADR-RESERVATION.md.
#   sentinel(distinct-marker 의무, CFP-2243 TC9 회피): defect fixture 는 exit 1 **및** stdout 에 충돌 번호
#        (zero-pad 무관 `0*<n>`) 출현을 병행 assert — exit-code 단독 판정 금지(미 fork/absent = exit 2 회피).
#   ⚠ 인터페이스 불일치 시 real-impl assert 는 RED — DevPL→Architect §8 signature 명시 요청 대상.
#
# anti-theater: clean fixture = exit 0 / defect fixture = exit 1 (0↔1 대조 = discriminating, absent(2) 과 구분).
#   각 mutant(mu1/mu2/mu3) 은 fixture-discrimination proof 로 non-hollow 입증 — 결함 fixture 위에서
#   mutant 행위를 embody 한 reference detector 를 돌려 **survive(미검출/오검출)** 함을 보이고,
#   동일 fixture 에서 real lint 는 **kill(정검출)** 해야 함을 assert. survival(real lint 미검출) 목표 = 0.
#
# 실 SSOT 파일 in-place mutate 0 — 전부 mktemp fixture 격리. real ADR-RESERVATION.md 무터치.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LINT="$REPO_ROOT/scripts/lib/check-adr-uniqueness-3way.py"
PYBIN="$(command -v python3 || command -v python)"

PASS=0
FAIL=0
PENDING=0   # real-impl 부재(interface-first RED) — impl 착지 후 0 이어야 함.

pass()    { echo "  ✓ PASS: $1"; PASS=$((PASS+1)); }
fail()    { echo "  ✗ FAIL: $1"; FAIL=$((FAIL+1)); }
pending() { echo "  … RED-PENDING(real-impl 부재/interface): $1"; PENDING=$((PENDING+1)); }

# ─── fixture builders ────────────────────────────────────────────────────────
# mk_adr <adr_dir> <filenum-as-in-filename> <frontmatter-adr_number> <slug> [carrier]
mk_adr() {
  local d="$1" fn="$2" fm="$3" slug="$4" carrier="${5:-CFP-9000}"
  cat > "$d/ADR-$fn-$slug.md" <<EOF
---
adr_number: $fm
title: fixture $slug
status: Active
category: governance
date: 2026-07-03
carrier_story: $carrier
---

# ADR-$fn fixture body
본문에 cross-ref noise 를 둘 수 있음 (구조적 파싱 = 본문 무시).
EOF
}

# mk_reservation <adr_dir> <row...>  where row = "num|epic|status|reserved_at"
mk_reservation() {
  local d="$1"; shift
  {
    echo '---'
    echo 'adr_number: null'
    echo 'title: fixture reservation'
    echo 'status: Active'
    echo 'category: governance'
    echo 'schema_version: 1.1'
    echo '---'
    echo ''
    echo '# fixture reservation'
    echo ''
    echo '| adr_number | epic | status | reserved_at |'
    echo '|---|---|---|---|'
    local row
    for row in "$@"; do
      IFS='|' read -r n e s r <<< "$row"
      echo "| $n | $e | $s | $r |"
    done
  } > "$d/ADR-RESERVATION.md"
}

new_root() { mktemp -d; }
adr_dir_of() { mkdir -p "$1/archive/adr"; echo "$1/archive/adr"; }

# ─── real lint invocation probe (interface robustness) ───────────────────────
# 결과: rc = exit code, LINT_OUT = stdout. $1 = adr_dir (reservation = <adr_dir>/ADR-RESERVATION.md).
# 실측 인터페이스(firsthand --help) = `--adr-dir <dir> --reservation-path <path>` (primary form).
# --lapse-scope-min 0 주입 = fixture 저번호(≤112) slot 도 lapse 판정 대상화(default 113 우회, 결정성).
LINT_OUT=""
run_lint() {
  local adrdir="$1" res out rc errf form
  res="$adrdir/ADR-RESERVATION.md"; errf="$(mktemp)"
  for form in adrdir root repo-root pos; do
    case "$form" in
      adrdir)    out="$("$PYBIN" "$LINT" --adr-dir "$adrdir" --reservation-path "$res" --lapse-scope-min 0 2>"$errf")"; rc=$? ;;
      root)      out="$("$PYBIN" "$LINT" --root "$adrdir" 2>"$errf")"; rc=$? ;;
      repo-root) out="$("$PYBIN" "$LINT" --repo-root "$adrdir" 2>"$errf")"; rc=$? ;;
      pos)       out="$("$PYBIN" "$LINT" "$adrdir" 2>"$errf")"; rc=$? ;;
    esac
    # argparse flag 오류(exit 2 + usage/unrecognized) 면 다음 form 시도
    if [ "$rc" -eq 2 ] && grep -qiE 'unrecognized|usage:|invalid choice|error:' "$errf"; then
      continue
    fi
    break
  done
  rm -f "$errf"
  LINT_OUT="$out"
  return "$rc"
}

impl_present() { [ -f "$LINT" ]; }

# ─── 실-script mutation harness (F-CX-002 — reference-detector → 실-script mutation) ──
# 재구현 reference-detector 증명(mu1~mu3 = fixture-discrimination)만으로는 실 script 를 mutate 해도
# test 가 못 잡는다(Codex 실측: MU1/MU3 survive). 실 script COPY 를 sed mutate 해 동일 fixture 위에서
# 돌려 finding 이 사라짐(결과 달라짐)을 직접 assert = 회귀를 CI 가 kill. mutation 은 COPY 에만 —
# tracked tree/실 script 무터치.
VARIANT_OUT=""
run_script() {
  # $1 = script path, $2 = adr_dir. VARIANT_OUT 에 stdout, return = exit code (primary form 고정).
  local script="$1" adrdir="$2" res out rc
  res="$adrdir/ADR-RESERVATION.md"
  out="$("$PYBIN" "$script" --adr-dir "$adrdir" --reservation-path "$res" --lapse-scope-min 0 2>/dev/null)"; rc=$?
  VARIANT_OUT="$out"
  return "$rc"
}
mk_mutant() {
  # $1 = sed expression. $LINT 의 mutated COPY 경로를 echo (tracked tree 무변경, temp 격리).
  local sed_expr="$1" md cp
  md="$(mktemp -d)"; cp="$md/mutant-lint.py"
  sed "$sed_expr" "$LINT" > "$cp"
  echo "$cp"
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo "CFP-2563 §8 — check-adr-uniqueness-3way lint 자기검증 (Q1 self-test + Q2 INV-12)"
echo "═══════════════════════════════════════════════════════════════════════════"

# ─── GREEN baseline: clean fixture → exit 0 (born-valid RED→GREEN 의 GREEN 축) ──
echo ""
echo "── GREEN baseline (clean fixture → exit 0) ──"
R="$(new_root)"; A="$(adr_dir_of "$R")"
mk_adr "$A" 200 200 alpha CFP-1
mk_adr "$A" 201 201 beta  CFP-2
mk_reservation "$A" "200|CFP-1|active|2026-07-03" "201|CFP-2|active|2026-07-03"
if impl_present; then
  run_lint "$A"; rc=$?
  # BASELINE assert (line-anchored): clean → exit 0.
  if [ "$rc" -eq 0 ]; then pass "baseline clean fixture exit 0"; else fail "baseline clean expected exit 0, got $rc / out=$LINT_OUT"; fi
else
  pending "baseline clean (scripts/lib/check-adr-uniqueness-3way.py 부재)"
fi
rm -rf "$R"

# ─── INV-8: filename-collision (동일 filename 번호 2 파일) → 검출 ──────────────
echo ""
echo "── INV-8 filename-collision (ADR-042 x2) → 검출 ──"
R="$(new_root)"; A="$(adr_dir_of "$R")"
mk_adr "$A" 042 42 policy    CFP-1
mk_adr "$A" 042 42 channel   CFP-2   # 동일 slot 42 두 파일 — filename-key 충돌
mk_adr "$A" 043 43 other     CFP-3
mk_reservation "$A" "42|CFP-1|active|2026-07-03" "43|CFP-3|active|2026-07-03"
if impl_present; then
  run_lint "$A"; rc=$?
  # INV-8 assert: exit 1 AND stdout 에 42 출현(distinct-marker).
  if [ "$rc" -eq 1 ] && echo "$LINT_OUT" | grep -qE '0*42\b'; then
    pass "INV-8 filename-collision 042 검출 (exit 1 + sentinel 42)"
  else
    fail "INV-8 filename-collision: exit=$rc sentinel=$(echo "$LINT_OUT" | grep -oE '0*42' | head -1) (기대 exit 1 + '42')"
  fi
else
  pending "INV-8 filename-collision"
fi
rm -rf "$R"

# ─── INV-8/INV-9: frontmatter-collision (ADR-045 fm=43 ↔ ADR-043 fm=43) ───────
# filename-only lint(mu1)은 filename 43,45 를 distinct 로 보아 미검출 → 여기서 mu1 survive.
echo ""
echo "── INV-8/INV-9 frontmatter-collision (ADR-045 fm=43) → 검출 + mu1 kill ──"
R="$(new_root)"; A="$(adr_dir_of "$R")"
mk_adr "$A" 043 43 realforty3 CFP-1
mk_adr "$A" 045 43 collider   CFP-2   # filename=45, frontmatter=43 → frontmatter slot 43 충돌 + filename↔fm mismatch
mk_reservation "$A" "43|CFP-1|active|2026-07-03" "45|CFP-2|active|2026-07-03"
if impl_present; then
  run_lint "$A"; rc=$?
  # INV-8(frontmatter-key 충돌) + INV-9(filename↔frontmatter mismatch) — exit 1 + [frontmatter-collision]
  # finding-type line 존재 + sentinel 43 (MU1 강화: exit+sentinel 단독 아닌 finding 종류 단위 assert —
  # mismatch finding 만으로도 exit 1/43 이 나므로 finding-type 을 함께 봐야 hollow 아님).
  if [ "$rc" -eq 1 ] && echo "$LINT_OUT" | grep -qE '^\[frontmatter-collision\]' && echo "$LINT_OUT" | grep -qE '0*43\b'; then
    pass "INV-8/9 frontmatter-collision 045(fm=43) 검출 (exit 1 + [frontmatter-collision] finding-line + sentinel 43)"
  else
    fail "INV-8/9 frontmatter-collision: exit=$rc out=$LINT_OUT (기대 exit 1 + '43')"
  fi
else
  pending "INV-8/9 frontmatter-collision"
fi
# mu1 discrimination proof: filename-only detector 는 이 fixture 를 survive(미검출)해야 = fixture discriminating.
"$PYBIN" - "$A" <<'PYEOF'
import sys, re, glob, os
adr_dir = sys.argv[1]
# mu1: filename-only collision (frontmatter-key 무시)
filenums = []
for p in glob.glob(os.path.join(adr_dir, "ADR-*-*.md")):
    m = re.match(r"ADR-0*(\d+)-", os.path.basename(p))
    if m: filenums.append(int(m.group(1)))
# frontmatter-key
fmnums = []
for p in glob.glob(os.path.join(adr_dir, "ADR-*-*.md")):
    for line in open(p, encoding="utf-8"):
        m = re.match(r'\s*adr_number:\s*"?0*(\d+)"?', line)
        if m: fmnums.append(int(m.group(1))); break
def has_dup(xs): return len(xs) != len(set(xs))
mu1_detects = has_dup(filenums)          # filename-only: 43,45,43? no -> filenames are 43,45 distinct -> False
correct_detects = has_dup(fmnums)        # frontmatter-key: 43,43 -> True
# fixture discriminating iff mu1 survives(False) while correct kills(True)
ok = (mu1_detects is False) and (correct_detects is True)
print("MU1_PROOF:" + ("OK" if ok else f"BAD mu1={mu1_detects} correct={correct_detects}"))
PYEOF
mu1_line="$("$PYBIN" - "$A" <<'PYEOF'
import sys, re, glob, os
adr_dir=sys.argv[1]
fn=[]; fm=[]
for p in glob.glob(os.path.join(adr_dir,"ADR-*-*.md")):
    m=re.match(r"ADR-0*(\d+)-",os.path.basename(p))
    if m: fn.append(int(m.group(1)))
    for line in open(p,encoding="utf-8"):
        mm=re.match(r'\s*adr_number:\s*"?0*(\d+)"?',line)
        if mm: fm.append(int(mm.group(1))); break
d=lambda xs: len(xs)!=len(set(xs))
print("OK" if (d(fn) is False and d(fm) is True) else "BAD")
PYEOF
)"
if [ "$mu1_line" = "OK" ]; then pass "mu1 discrimination proof (filename-only survives, frontmatter-key kills)"; else fail "mu1 proof: $mu1_line"; fi
rm -rf "$R"

# ─── INV-9: filename↔frontmatter mismatch flag (단일 파일, 충돌 없이도 mismatch) ─
echo ""
echo "── INV-9 filename↔frontmatter mismatch flag (ADR-045 fm=43, 단독) → 검출 ──"
R="$(new_root)"; A="$(adr_dir_of "$R")"
mk_adr "$A" 045 43 lonely CFP-1   # filename 45 ≠ frontmatter 43 (다른 파일 없이도 mismatch)
mk_reservation "$A" "45|CFP-1|active|2026-07-03"
if impl_present; then
  run_lint "$A"; rc=$?
  # INV-9 assert: mismatch flag → exit 1 (filename 45 와 frontmatter 43 불일치).
  if [ "$rc" -eq 1 ] && echo "$LINT_OUT" | grep -qE '0*4[35]\b'; then
    pass "INV-9 filename↔frontmatter mismatch flag 검출 (exit 1)"
  else
    fail "INV-9 mismatch: exit=$rc out=$LINT_OUT (기대 exit 1 + 45/43)"
  fi
else
  pending "INV-9 mismatch flag"
fi
rm -rf "$R"

# ─── INV-10: 구조적 파싱 — row 본문 cross-ref 오탐 0 + mu2 kill ────────────────
# clean fixture(모든 파일↔row 정합) + 한 row 의 reserved_at 본문에 "ADR-999 참조" noise.
# 구조적 파서(첫 열 slot)=오탐 0(exit 0). 문자열-grep 파서(mu2)=999 를 slot 으로 오추출 → false lapse.
echo ""
echo "── INV-10 구조적 파싱 (본문 'ADR-999 참조' cross-ref noise) → 오탐 0 + mu2 kill ──"
R="$(new_root)"; A="$(adr_dir_of "$R")"
mk_adr "$A" 200 200 alpha CFP-1
mk_adr "$A" 201 201 beta  CFP-2
mk_reservation "$A" \
  "200|CFP-1|active|2026-07-03 (관련 ADR-999 참조 — cross-ref noise, 실 slot 아님)" \
  "201|CFP-2|active|2026-07-03"
if impl_present; then
  run_lint "$A"; rc=$?
  # INV-10 assert: 구조적 파싱 → 본문 999 무시 → false-positive 0 → exit 0.
  if [ "$rc" -eq 0 ]; then
    pass "INV-10 구조적 파싱 오탐 0 (본문 ADR-999 무시, exit 0)"
  else
    fail "INV-10 구조적 파싱: exit=$rc out=$LINT_OUT (기대 exit 0 = 오탐 0)"
  fi
else
  pending "INV-10 구조적 파싱 오탐 0"
fi
# mu2 discrimination proof: string-grep 파서는 본문 999 를 slot 으로 오추출 → false lapse(오검출) = survive.
mu2_line="$("$PYBIN" - "$A" <<'PYEOF'
import sys, re, glob, os
adr_dir=sys.argv[1]
res=open(os.path.join(adr_dir,"ADR-RESERVATION.md"),encoding="utf-8").read()
files=set()
for p in glob.glob(os.path.join(adr_dir,"ADR-*-*.md")):
    m=re.match(r"ADR-0*(\d+)-",os.path.basename(p))
    if m: files.add(int(m.group(1)))
# mu2: whole-text grep 으로 모든 ADR-N 토큰을 "referenced slot" 으로 간주
grep_slots=set(int(x) for x in re.findall(r"ADR-0*(\d+)", res))
# 구조적: 표 첫 열만
struct_slots=set()
for line in res.splitlines():
    m=re.match(r"\|\s*0*(\d+)\s*\|", line)
    if m: struct_slots.add(int(m.group(1)))
# lapse(파일 존재, slot 부재) 오탐 여부: mu2 는 files 대비 grep noise 로 999 를 '참조된 slot' 취급하여
# 999 파일 부재를 mismatch/false finding 으로 낸다. 구조적은 999 미포함.
mu2_falsepos = (999 in grep_slots) and (999 not in struct_slots)
print("OK" if mu2_falsepos else f"BAD grep={sorted(grep_slots)} struct={sorted(struct_slots)}")
PYEOF
)"
if [ "$mu2_line" = "OK" ]; then pass "mu2 discrimination proof (string-grep 는 본문 999 오탐 = survive, 구조적은 무시)"; else fail "mu2 proof: $mu2_line"; fi
rm -rf "$R"

# ─── INV-11: numeric 정규화 (zero-pad 동일 slot 인식) + mu3 kill ───────────────
# ADR-72 (2-digit) + ADR-072 (3-digit), 둘 다 frontmatter 72 → 정규화 후 동일 slot 72 = 충돌.
echo ""
echo "── INV-11 numeric 정규화 (ADR-72 vs ADR-072 = slot 72 충돌) → 검출 + mu3 kill ──"
R="$(new_root)"; A="$(adr_dir_of "$R")"
mk_adr "$A" 72  72 twodigit  CFP-1
mk_adr "$A" 072 72 threedigit CFP-2   # 문자열은 "72"≠"072", 정규화하면 둘 다 72
mk_reservation "$A" "72|CFP-1|active|2026-07-03"
if impl_present; then
  run_lint "$A"; rc=$?
  # INV-11 assert: 정규화 후 동일 slot 72 충돌 → exit 1 + sentinel 72.
  if [ "$rc" -eq 1 ] && echo "$LINT_OUT" | grep -qE '0*72\b'; then
    pass "INV-11 zero-pad 정규화 동일 slot 72 충돌 검출 (exit 1 + sentinel 72)"
  else
    fail "INV-11 zero-pad: exit=$rc out=$LINT_OUT (기대 exit 1 + '72')"
  fi
else
  pending "INV-11 numeric 정규화"
fi
# mu3 discrimination proof: 문자열-키(정규화 생략) detector 는 "72"≠"072" → 미검출 = survive.
mu3_line="$("$PYBIN" - "$A" <<'PYEOF'
import sys, re, glob, os
adr_dir=sys.argv[1]
str_keys=[]; int_keys=[]
for p in glob.glob(os.path.join(adr_dir,"ADR-*-*.md")):
    m=re.match(r"ADR-(0*\d+)-",os.path.basename(p))
    if m:
        str_keys.append(m.group(1))          # mu3: 원문 문자열 "72" / "072"
        int_keys.append(int(m.group(1)))     # 정규화 int 72 / 72
d=lambda xs: len(xs)!=len(set(xs))
mu3_detects=d(str_keys)       # "72","072" distinct -> False (survive)
correct_detects=d(int_keys)   # 72,72 -> True (kill)
print("OK" if (mu3_detects is False and correct_detects is True) else f"BAD str={str_keys} int={int_keys}")
PYEOF
)"
if [ "$mu3_line" = "OK" ]; then pass "mu3 discrimination proof (문자열-키 survive, 정규화-int kill)"; else fail "mu3 proof: $mu3_line"; fi
rm -rf "$R"

# ─── Q2 / INV-12: file↔row lapse (SYNTHETIC fixture, 실 15-lapse 비의존) ────────
echo ""
echo "── Q2 INV-12 file↔row lapse (SYNTHETIC: ADR-300 파일 존재 ∧ row 부재) → 검출 ──"
R="$(new_root)"; A="$(adr_dir_of "$R")"
mk_adr "$A" 300 300 present CFP-1
mk_adr "$A" 301 301 alsopresent CFP-2
# reservation 에 301 은 있으나 300 row 누락 = lapse.
mk_reservation "$A" "301|CFP-2|active|2026-07-03"
if impl_present; then
  run_lint "$A"; rc=$?
  # INV-12 assert: 파일 300 존재 + row 부재 → lapse 검출 → exit 1 + sentinel 300.
  if [ "$rc" -eq 1 ] && echo "$LINT_OUT" | grep -qE '0*300\b'; then
    pass "INV-12 file↔row lapse (300 파일 존재/row 부재) 검출 (exit 1 + sentinel 300)"
  else
    fail "INV-12 lapse: exit=$rc out=$LINT_OUT (기대 exit 1 + '300')"
  fi
else
  pending "INV-12 file↔row lapse"
fi
# INV-12 clean control: 300 row 도 존재 → lapse 0 → exit 0.
mk_reservation "$A" "300|CFP-1|active|2026-07-03" "301|CFP-2|active|2026-07-03"
if impl_present; then
  run_lint "$A"; rc=$?
  if [ "$rc" -eq 0 ]; then
    pass "INV-12 clean control (row 완비 → lapse 0, exit 0)"
  else
    fail "INV-12 clean control: exit=$rc out=$LINT_OUT (기대 exit 0)"
  fi
else
  pending "INV-12 clean control"
fi
rm -rf "$R"

# ═══ 실-script mutation kill proofs (F-CX-002 — Codex MU1/MU3 survive 봉쇄) ═══════════
# 위 mu1~mu3 는 재구현 reference-detector 증명(fixture-discrimination)이라 실 script mutate 를 못 잡음.
# 아래 두 블록은 실 script COPY 를 sed mutate 해 돌려 finding 이 사라짐(결과 달라짐)을 직접 assert.

# ─── MU3-real: exact-basename 제외 → substring 회귀 → reservation-슬러그 ADR 누락 kill ──
# 실 script 는 `base == "ADR-RESERVATION.md"` 정확 basename 으로만 RESERVATION 을 제외한다.
# 이를 `"reservation" in base.lower()` substring 으로 회귀시키면 basename 에 'reservation' 을 포함한
# 실 ADR(예: ADR-133-adr-reservation-*, ADR-036-*-reservation-*)이 스캔에서 누락(firsthand 함정, L49-51).
# colliding reservation-슬러그 ADR 2개(둘 다 slot 500) fixture 로 그 회귀를 kill.
echo ""
echo "── MU3-real 실-script mutation (exact-basename → substring 회귀) → filename-collision 500 소멸 kill ──"
R="$(new_root)"; A="$(adr_dir_of "$R")"
mk_adr "$A" 500 500 adr-reservation-thing CFP-1   # basename 에 'reservation' 포함
mk_adr "$A" 500 500 other                 CFP-2   # 동일 slot 500 → filename-collision
mk_reservation "$A" "500|CFP-1|active|2026-07-03"
if impl_present; then
  # (a) 실 script = 500 filename-collision 검출 (finding-type line 단위).
  run_lint "$A"; rc=$?
  real_hit=0
  if [ "$rc" -eq 1 ] && echo "$LINT_OUT" | grep -qE '^\[filename-collision\]' && echo "$LINT_OUT" | grep -qE '0*500\b'; then real_hit=1; fi
  # (b) mutant(exact-basename → substring) = reservation-슬러그 ADR 누락 → 파일 1개만 스캔 → 500 collision 소멸.
  MUT="$(mk_mutant 's/if base == RESERVATION_BASENAME:/if "reservation" in base.lower():/')"
  run_script "$MUT" "$A"; mrc=$?
  mut_lost=0
  if ! { echo "$VARIANT_OUT" | grep -qE '^\[filename-collision\]' && echo "$VARIANT_OUT" | grep -qE '0*500\b'; }; then mut_lost=1; fi
  rm -rf "$(dirname "$MUT")"
  if [ "$real_hit" -eq 1 ] && [ "$mut_lost" -eq 1 ]; then
    pass "MU3-real — 실 script 는 reservation-슬러그 500 collision kill / exact-basename→substring 회귀 mutant 는 소멸 → CI 가 회귀 검출 (real rc=$rc, mutant rc=$mrc)"
  else
    fail "MU3-real: real_hit=$real_hit(기대1) mut_lost=$mut_lost(기대1) rc=$rc mrc=$mrc — hollow 의심"
  fi
else
  pending "MU3-real 실-script mutation (exact-basename 회귀)"
fi
rm -rf "$R"

# ─── MU1-real: frontmatter-collision 검출 비활성(len>1 → len>99) → finding 소멸 kill ──
# filename 은 distinct(43,45)라 filename-only 로는 안 잡히는 frontmatter-key 충돌(§3.3 INV-8 dual-key 핵심).
# 검출을 비활성해도 mismatch finding(ADR-045 45≠43)은 잔존해 exit 1/sentinel 43 은 그대로 → exit·sentinel
# 단독으로는 killable 아님. finding-type([frontmatter-collision]) 소멸을 직접 assert 해야 kill.
echo ""
echo "── MU1-real 실-script mutation (frontmatter-collision 검출 비활성) → [frontmatter-collision] finding 소멸 kill ──"
R="$(new_root)"; A="$(adr_dir_of "$R")"
mk_adr "$A" 043 43 realforty3 CFP-1
mk_adr "$A" 045 43 collider   CFP-2   # filename 45, fm 43 → frontmatter slot 43 충돌
mk_reservation "$A" "43|CFP-1|active|2026-07-03" "45|CFP-2|active|2026-07-03"
if impl_present; then
  # (a) 실 script = [frontmatter-collision] finding-type 출력.
  run_lint "$A"; rc=$?
  real_fm=0
  if [ "$rc" -eq 1 ] && echo "$LINT_OUT" | grep -qE '^\[frontmatter-collision\]'; then real_fm=1; fi
  # (b) mutant(frontmatter 검출 비활성) = [frontmatter-collision] 소멸(mismatch 는 잔존, exit 여전 1).
  MUT="$(mk_mutant 's/by_fm.items() if len(v) > 1/by_fm.items() if len(v) > 99/')"
  run_script "$MUT" "$A"; mrc=$?
  mut_lost=0
  if ! echo "$VARIANT_OUT" | grep -qE '^\[frontmatter-collision\]'; then mut_lost=1; fi
  rm -rf "$(dirname "$MUT")"
  if [ "$real_fm" -eq 1 ] && [ "$mut_lost" -eq 1 ]; then
    pass "MU1-real — 실 script 는 [frontmatter-collision] finding 출력 / 검출-비활성 mutant 는 소멸 → CI 가 회귀 검출 (exit 단독 아닌 finding-line 단위, mutant rc=$mrc 유지)"
  else
    fail "MU1-real: real_fm=$real_fm(기대1) mut_lost=$mut_lost(기대1) rc=$rc mrc=$mrc — hollow 의심"
  fi
else
  pending "MU1-real 실-script mutation (frontmatter-collision 비활성)"
fi
rm -rf "$R"

# ─── born-valid smoke → SYNTHETIC fixture 이관 (§8.T-1, CFP-2566 C0 shared-infra) ──────────
# (구) real-repo 결함 의존(hits>=4 + fm_hit>=1)은 hollow: (a) fm_hit 이 CFP-2759 의 043/061
# frontmatter-collision 정정 후 lapse noise 우연매칭(검출력 0) (b) 42/47/48/56 renumber(CFP-2566
# C1~C4) 시 hits 붕괴. → self-contained SYNTHETIC fixture(mktemp)로 이관 — real archive/adr 무터치,
# real-pair count 독립(이후 per-pair child 가 smoke 를 재차 RED 로 만들지 않음).
# 주입: filename-collision(ADR-042 ×2, fm=42) + frontmatter-collision(fm=43 pair, distinct filename).
# assert = count-agnostic per-finding-type + sentinel (NO hits>=N, NO global total — CFP-2759 F-D1).
echo ""
echo "── born-valid smoke (SYNTHETIC: filename-collision 42 + frontmatter-collision 43 → 검출) ──"
R="$(new_root)"; A="$(adr_dir_of "$R")"
mk_adr "$A" 042 42 policy-fixture  CFP-1   # 동일 slot 42 두 파일 A (filename-key 충돌)
mk_adr "$A" 042 42 channel-fixture CFP-2   # 동일 slot 42 두 파일 B → filename-collision 42
mk_adr "$A" 043 43 realforty3      CFP-3   # filename 43, fm 43
mk_adr "$A" 045 43 collider        CFP-4   # filename 45, fm 43 → frontmatter slot 43 충돌 (distinct filename)
mk_reservation "$A" \
  "42|CFP-1|active|2026-07-19" \
  "43|CFP-3|active|2026-07-19" \
  "45|CFP-4|active|2026-07-19"
if impl_present; then
  run_lint "$A"; rc=$?
  # count-agnostic per-finding-type + sentinel: exit 1 ∧ [filename-collision]∧42 ∧ [frontmatter-collision]∧43.
  fnc=0; fmc=0
  { echo "$LINT_OUT" | grep -qE '^\[filename-collision\]' && echo "$LINT_OUT" | grep -qE '0*42\b'; } && fnc=1
  { echo "$LINT_OUT" | grep -qE '^\[frontmatter-collision\]' && echo "$LINT_OUT" | grep -qE '0*43\b'; } && fmc=1
  if [ "$rc" -eq 1 ] && [ "$fnc" -eq 1 ] && [ "$fmc" -eq 1 ]; then
    pass "born-valid smoke (synthetic) — filename-collision 42 + frontmatter-collision 43 검출 (exit 1, per-finding-type sentinel)"
  else
    fail "born-valid smoke (synthetic): exit=$rc filename-collision+42=$fnc frontmatter-collision+43=$fmc (기대 exit 1 + 둘 다 1) — hollow 의심"
  fi
else
  pending "born-valid smoke (synthetic fixture)"
fi
rm -rf "$R"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "Results: $PASS passed, $FAIL failed, $PENDING red-pending(real-impl 부재/interface)"
echo "  discrimination proof(mu1/mu2/mu3) survival 목표 = 0 (all proofs OK → fixture 가 mutant 를 kill)"
echo "═══════════════════════════════════════════════════════════════════════════"
if [ "$FAIL" -eq 0 ] && [ "$PENDING" -eq 0 ]; then
  echo "All GREEN ✓"; exit 0
else
  echo "RED — real-impl 착지 후 재실행(PL consolidated) 시 GREEN 기대."; exit 1
fi
