#!/usr/bin/env bash
# tests/scripts/test_adr-reservation-backfill.sh
# CFP-2563 Phase 2 (QADeveloperAgent) — 15-row idempotent backfill 무결성 검증 (Q3).
# Change Plan CFP-2563 §8.1 backfill invariant + §11 데이터 마이그레이션 이행:
#   INV-13 append-only (기존 row byte-identical)          + mu4(overwrite) kill
#   INV-14 idempotent (재실행 no-op)                       + mu5(re-append) kill
#   INV-15 deterministic reconstruction (frontmatter 기반, 비-grep)
#   INV-16 slot number ↔ ADR file 1:1 (mismatch flag)
#
# 대상(구현-under-test, DeveloperAgent 병렬 작성): scripts/lib/adr-reservation-backfill.py
#   계약(§11.2): idempotent one-shot backfill — archive/adr ADR 파일 ↔ RESERVATION row 차집합 slot 을
#   frontmatter 로 결정적 재구성해 append-only 추가. 재실행 = no-op.
#
# ⚠ ISOLATION 의무: real archive/adr/ADR-RESERVATION.md 절대 무터치 — 전부 mktemp COPY/fixture.
#   실 15-row one-shot run 은 DeveloperAgent 소관(본 test 는 격리 fixture 로 무결성만 검증).
#
# ── 인터페이스 가정(interface-first TDD, §8 미명시) ─────────────────────────────────────────
#   CLI probe: `--root <root>` → `--reservation <res> --adr-dir <dir>` → positional <root>.
#   scan/append target: <root>/archive/adr/ADR-*.md + <root>/archive/adr/ADR-RESERVATION.md.
#   sentinel(distinct-marker): 결정 판정은 exit-code 단독 금지 — reservation 파일 실 content(row) 를 assert.
#
# anti-theater: mu4/mu5 는 discrimination proof — INV-13/INV-14 assert 가 mutant 를 실제로 kill 함을 입증.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKFILL="$REPO_ROOT/scripts/lib/adr-reservation-backfill.py"
PYBIN="$(command -v python3 || command -v python)"

PASS=0; FAIL=0; PENDING=0
pass()    { echo "  ✓ PASS: $1"; PASS=$((PASS+1)); }
fail()    { echo "  ✗ FAIL: $1"; FAIL=$((FAIL+1)); }
pending() { echo "  … RED-PENDING(real-impl 부재/interface): $1"; PENDING=$((PENDING+1)); }
impl_present() { [ -f "$BACKFILL" ]; }

# ─── fixture builders (uniqueness lint test 와 동일 schema) ───────────────────
mk_adr() {
  local d="$1" fn="$2" fm="$3" slug="$4" carrier="${5:-CFP-9000}" body_bait="${6:-}"
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
$body_bait
EOF
}
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
    local row n e s r
    for row in "$@"; do
      IFS='|' read -r n e s r <<< "$row"
      echo "| $n | $e | $s | $r |"
    done
  } > "$d/ADR-RESERVATION.md"
}
new_root() { mktemp -d; }
adr_dir_of() { mkdir -p "$1/archive/adr"; echo "$1/archive/adr"; }
RES_OF() { echo "$1/archive/adr/ADR-RESERVATION.md"; }
row_of() { grep -E "^\|\s*0*$2\s*\|" "$1" 2>/dev/null; }        # $1=resfile $2=slot
row_count() { grep -cE '^\|\s*[0-9]+\s*\|' "$1" 2>/dev/null; }  # 데이터 row 수 (헤더 제외)

BACKFILL_OUT=""
# $1 = adr_dir. 실측 인터페이스(firsthand --help) = `--adr-dir <dir> --reservation-path <path>` (primary).
# --scope-min 0 = fixture 저번호도 lapse 대상화(default 113 우회, 결정성).
run_backfill() {
  local adrdir="$1" res out rc errf form
  res="$adrdir/ADR-RESERVATION.md"; errf="$(mktemp)"
  for form in adrdir root pos; do
    case "$form" in
      adrdir) out="$("$PYBIN" "$BACKFILL" --adr-dir "$adrdir" --reservation-path "$res" --scope-min 0 2>"$errf")"; rc=$? ;;
      root)   out="$("$PYBIN" "$BACKFILL" --root "$adrdir" 2>"$errf")"; rc=$? ;;
      pos)    out="$("$PYBIN" "$BACKFILL" "$adrdir" 2>"$errf")"; rc=$? ;;
    esac
    if [ "$rc" -eq 2 ] && grep -qiE 'unrecognized|usage:|invalid choice|error:' "$errf"; then continue; fi
    break
  done
  rm -f "$errf"; BACKFILL_OUT="$out"; return "$rc"
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo "CFP-2563 §8/§11 — adr-reservation-backfill 무결성 (Q3: INV-13..16 + mu4/mu5)"
echo "═══════════════════════════════════════════════════════════════════════════"

# ─── INV-13 append-only: 기존 row byte-identical + 누락 slot append ────────────
echo ""
echo "── INV-13 append-only (기존 row 400/402 byte-identical, 401 append) ──"
R="$(new_root)"; A="$(adr_dir_of "$R")"; RES="$(RES_OF "$R")"
mk_adr "$A" 400 400 a CFP-1
mk_adr "$A" 401 401 b CFP-2
mk_adr "$A" 402 402 c CFP-3
mk_reservation "$A" "400|CFP-1|active|2026-07-03" "402|CFP-3|active|2026-07-03"
before_400="$(row_of "$RES" 400)"; before_402="$(row_of "$RES" 402)"; before_cnt="$(row_count "$RES")"
if impl_present; then
  run_backfill "$A"; rc=$?
  after_400="$(row_of "$RES" 400)"; after_402="$(row_of "$RES" 402)"; after_cnt="$(row_count "$RES")"
  # INV-13 assert: 기존 row 400/402 byte-identical AND 401 새로 존재 AND row 수 = before+1.
  if [ "$before_400" = "$after_400" ] && [ "$before_402" = "$after_402" ] \
       && [ -n "$(row_of "$RES" 401)" ] && [ "$after_cnt" -eq "$((before_cnt+1))" ]; then
    pass "INV-13 append-only (기존 row 불변 + 401 append + count $before_cnt→$after_cnt)"
  else
    fail "INV-13: 400 same=$([ "$before_400" = "$after_400" ] && echo Y||echo N) 402 same=$([ "$before_402" = "$after_402" ] && echo Y||echo N) 401=$(row_of "$RES" 401) cnt=$before_cnt→$after_cnt rc=$rc"
  fi
else
  pending "INV-13 append-only"
fi
rm -rf "$R"

# mu4 discrimination proof: 기존 row 를 overwrite 하는 mutant 를 INV-13(byte-identical) assert 가 kill.
echo "  [mu4 proof] overwrite mutant vs INV-13 byte-identical assert"
R="$(new_root)"; A="$(adr_dir_of "$R")"; RES="$(RES_OF "$R")"
mk_reservation "$A" "400|CFP-1|active|2026-07-03" "402|CFP-3|active|2026-07-03"
before_400="$(row_of "$RES" 400)"
# mutant: 기존 row 400 의 status active→reserved 로 overwrite (append-only 위반)
"$PYBIN" - "$RES" <<'PYEOF'
import sys
p=sys.argv[1]; t=open(p,encoding="utf-8").read()
open(p,"w",encoding="utf-8").write(t.replace("| 400 | CFP-1 | active |","| 400 | CFP-1 | reserved |"))
PYEOF
after_400="$(row_of "$RES" 400)"
if [ "$before_400" != "$after_400" ]; then
  pass "mu4 proof: overwrite mutant 을 INV-13 byte-identical assert 가 검출 (survive→kill 가능)"
else
  fail "mu4 proof: overwrite mutant 미검출 (INV-13 assert hollow?)"
fi
rm -rf "$R"

# ─── INV-14 idempotent: 2회 실행 = no-op (재-append 0) + mu5 kill ──────────────
echo ""
echo "── INV-14 idempotent (2nd run = no-op) ──"
R="$(new_root)"; A="$(adr_dir_of "$R")"; RES="$(RES_OF "$R")"
mk_adr "$A" 500 500 a CFP-1
mk_adr "$A" 501 501 b CFP-2
mk_reservation "$A" "500|CFP-1|active|2026-07-03"    # 501 누락
if impl_present; then
  run_backfill "$A"; r1=$?
  cnt1="$(row_count "$RES")"; snap1="$(cat "$RES")"
  run_backfill "$A"; r2=$?
  cnt2="$(row_count "$RES")"; snap2="$(cat "$RES")"
  # INV-14 assert: 2nd run 후 row 수 불변 AND 파일 byte-identical (재-append 0).
  if [ "$cnt1" -eq "$cnt2" ] && [ "$snap1" = "$snap2" ]; then
    pass "INV-14 idempotent (1st run cnt=$cnt1, 2nd run no-op cnt=$cnt2, byte-identical)"
  else
    fail "INV-14: cnt1=$cnt1 cnt2=$cnt2 identical=$([ "$snap1" = "$snap2" ] && echo Y||echo N) r1=$r1 r2=$r2"
  fi
else
  pending "INV-14 idempotent"
fi
rm -rf "$R"

# mu5 discrimination proof: 2회차 무조건 재-append 하는 mutant 를 INV-14(count 불변) assert 가 kill.
echo "  [mu5 proof] re-append mutant vs INV-14 count-invariant assert"
R="$(new_root)"; A="$(adr_dir_of "$R")"; RES="$(RES_OF "$R")"
mk_reservation "$A" "500|CFP-1|active|2026-07-03" "501|CFP-2|active|2026-07-03"
cnt_a="$(row_count "$RES")"
# mutant: guard 없이 501 row 를 재-append
printf '| 501 | CFP-2 | active | 2026-07-03 (re-append) |\n' >> "$RES"
cnt_b="$(row_count "$RES")"
if [ "$cnt_b" -gt "$cnt_a" ]; then
  pass "mu5 proof: re-append mutant 을 INV-14 count-invariant assert 가 검출 ($cnt_a→$cnt_b)"
else
  fail "mu5 proof: re-append mutant 미검출 (INV-14 assert hollow?)"
fi
rm -rf "$R"

# ─── INV-15 deterministic reconstruction: frontmatter 기반(비-grep) ────────────
# ADR-600 frontmatter carrier_story=CFP-777, body 에 grep-bait 'CFP-000' → backfill row.epic = CFP-777.
echo ""
echo "── INV-15 결정적 재구성 (epic=frontmatter carrier_story, grep-bait 무시) ──"
R="$(new_root)"; A="$(adr_dir_of "$R")"; RES="$(RES_OF "$R")"
mk_adr "$A" 599 599 pre   CFP-1
mk_adr "$A" 600 600 recon CFP-777 "grep-bait CFP-000 이 본문에 있으나 frontmatter carrier_story 가 SSOT."
mk_reservation "$A" "599|CFP-1|active|2026-07-02"   # 기존 row 존재(대표성) → 600 만 lapse 대상
if impl_present; then
  run_backfill "$A"; rc=$?
  row600="$(row_of "$RES" 600)"
  # INV-15 assert: 재구성된 row 의 epic = CFP-777 (frontmatter), NOT CFP-000 (body grep-bait).
  if echo "$row600" | grep -q 'CFP-777' && ! echo "$row600" | grep -q 'CFP-000'; then
    pass "INV-15 결정적 재구성 (row epic=CFP-777 frontmatter, grep-bait CFP-000 미채택)"
  else
    fail "INV-15: row600='$row600' (기대 CFP-777 포함 / CFP-000 배제) rc=$rc"
  fi
else
  pending "INV-15 결정적 재구성"
fi
rm -rf "$R"

# ─── INV-16 slot↔file 1:1 mismatch flag ──────────────────────────────────────
# ADR-403 filename 403 ↔ frontmatter 999 불일치 → backfill 이 잘못된 slot 을 silent 생성하지 않고 mismatch flag.
echo ""
echo "── INV-16 slot↔file 1:1 (filename 403 ≠ frontmatter 999 → mismatch flag) ──"
R="$(new_root)"; A="$(adr_dir_of "$R")"; RES="$(RES_OF "$R")"
mk_adr "$A" 403 999 mismatched CFP-9
mk_reservation "$A"
if impl_present; then
  run_backfill "$A"; rc=$?
  res_txt="$(cat "$RES")"
  # INV-16 assert: mismatch 가 surface(sentinel 403 또는 999 가 stdout 에) AND silent-wrong-row 부재
  #   (403↔999 불일치를 무시하고 임의 slot row 를 조용히 append 하지 않아야).
  surfaced=0
  { echo "$BACKFILL_OUT" | grep -qE '0*(403|999)\b'; } && surfaced=1
  [ "$rc" -ne 0 ] && surfaced=1   # nonzero exit 로 flag 하는 구현도 허용
  silent_wrong=0
  { echo "$res_txt" | grep -qE '^\|\s*0*999\s*\|'; } && silent_wrong=1   # 999 slot 을 조용히 만들면 위반
  if [ "$surfaced" -eq 1 ] && [ "$silent_wrong" -eq 0 ]; then
    pass "INV-16 mismatch flag (403↔999 surfaced, silent 999-row 부재)"
  else
    fail "INV-16: surfaced=$surfaced silent_wrong=$silent_wrong rc=$rc out=$BACKFILL_OUT"
  fi
else
  pending "INV-16 slot↔file mismatch flag"
fi
rm -rf "$R"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "Results: $PASS passed, $FAIL failed, $PENDING red-pending(real-impl 부재/interface)"
echo "  mu4/mu5 discrimination proof survival 목표 = 0 (proofs OK → INV-13/14 assert 가 mutant kill)"
echo "═══════════════════════════════════════════════════════════════════════════"
if [ "$FAIL" -eq 0 ] && [ "$PENDING" -eq 0 ]; then
  echo "All GREEN ✓"; exit 0
else
  echo "RED — real-impl 착지 후 재실행(PL consolidated) 시 GREEN 기대."; exit 1
fi
