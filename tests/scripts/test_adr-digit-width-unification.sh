#!/usr/bin/env bash
# tests/scripts/test_adr-digit-width-unification.sh
# CFP-2762 — ADR 파일명 3-digit zero-pad(ADR-NNN) 통일 self-test (durable regression + discriminating fixture).
#
# 판정 축:
#   post-state invariant I-A~I-E (실 corpus 대상 기계 검증) + discriminating fixture(pre-RED → post-GREEN).
#   상시 drift-guard 는 기존 warning-tier uniqueness lint(check-adr-uniqueness-3way.py, CANONICAL_PAD_WIDTH=3)가
#   담당 — 본 self-test = 1회 정규화 정합 실증 + regression fixture 영속화(CFP-881 built-then-pruned 회피).
#
# ★hard-fail 채널 배선(MEMORY CFP-2635/881): 본 self-test 는 warning-tier fence(continue-on-error) 안에
#   매몰하지 않고 전용 workflow(.github/workflows/adr-digit-width-check.yml)에서 hard-fail 로 실행 —
#   RED = check run 실패(이빨). non-required(branch protection 7-tuple 무변경)이나 RED 가 swallowed 되지 않음.
#   pytest 수집 self-poison(ModuleNotFound) 회피 위해 bash self-test(수집 대상 아님).
#
# ★본 파일은 fixture 성격상 `ADR-72` 토큰(패턴·픽스처)을 의도적으로 포함 → I-D exclusion allowlist 등재
#   (기존 tests/scripts/test_check-adr-uniqueness-3way.sh 선례 동형).
#
# exit 0 = ALL GREEN / exit 1 = 1+ FAIL / exit 2 = 실행 오류.

set -u
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)" || exit 2
cd "$REPO_ROOT" || exit 2
FAIL=0
pass() { echo "  [PASS] $*"; }
fail() { echo "  [FAIL] $*"; FAIL=$((FAIL+1)); }

# word-boundary ADR-72 (negative lookahead — ADR-720..729 제외). grep -E 로 표현.
WB='ADR-72([^0-9]|$)'

# ── embedded word-boundary normalizer (self-contained·durable — 외부 script 의존 0) ──
# ADR-72(?![0-9]) -> ADR-072, raw-byte utf-8, newline 보존.
normalize_file() {
  python3 -c 'import sys,re; p=sys.argv[1]; d=open(p,"rb").read(); open(p,"wb").write(re.sub(rb"ADR-72(?![0-9])",rb"ADR-072",d))' "$1"
}
# no-op stub (판정력 실증용 — 정규화 안 하면 RED 유지)
noop_file() { : ; }

echo "== I-A: 2-digit-name ADR 파일 = 0 (ADR-072 존재) =="
TWO=$(git ls-files 'archive/adr/ADR-*.md' | grep -E 'ADR-[0-9]{2}-' || true)
[ -z "$TWO" ] && pass "2-digit-name ADR 0" || fail "2-digit-name ADR 잔존: $TWO"
if git ls-files 'archive/adr/ADR-072-production-evidence-deputy-and-epic-cutover-gate.md' | grep -q .; then
  pass "ADR-072 파일 존재"
else
  fail "ADR-072 파일 부재"
fi

echo "== I-B: uniqueness lint zero-pad-drift(번호 72) finding = 0 =="
LINT=$(python3 scripts/lib/check-adr-uniqueness-3way.py 2>&1 || true)
if echo "$LINT" | grep -qE "token '72'"; then
  fail "zero-pad-drift(token '72') finding 잔존"
else
  pass "zero-pad-drift(72) finding 0"
fi

echo "== I-C: citation-slug L1 — 번호 72 broken-slug = 0 =="
CIT=$(python3 scripts/lib/check_adr_citation_slug.py --l1-only archive/adr docs plugins skills scripts templates .github 2>&1 || true)
if echo "$CIT" | grep -q 'ADR-072 slug file missing'; then
  fail "citation-slug L1 ADR-072 broken-slug 발생"
else
  pass "citation-slug L1 ADR-072 정합"
fi

echo "== I-D: stray ADR-72 word-boundary ⊆ exclusion allowlist (정확 일치) =="
ALLOW="archive/prune-2026-06/CHECK-VERDICT.md
archive/prune-2026-06/RED-TEAM-FINDINGS.md
archive/prune-2026-06/UNDERSTANDING.md
archive/CHANGELOG-legacy.md
tests/scripts/test_check-adr-uniqueness-3way.sh
archive/adr/ADR-065-architect-phase1-mechanical-self-check.md
tests/scripts/test_adr-digit-width-unification.sh"
RESID=$(git grep -lE "$WB" -- . || true)
EXTRA=$(comm -23 <(printf '%s\n' "$RESID" | sort -u | grep -v '^$') <(printf '%s\n' "$ALLOW" | sort -u))
if [ -z "$EXTRA" ]; then
  pass "allowlist 외 stray 0"
else
  fail "allowlist 외 stray ADR-72: $(echo "$EXTRA" | tr '\n' ' ')"
fi

echo "== I-E: plugin.json 내 ADR-72 stray = 0 =="
PJ=$(git grep -lE "$WB" -- 'plugins/*/.claude-plugin/plugin.json' || true)
[ -z "$PJ" ] && pass "plugin.json ADR-72 0" || fail "plugin.json ADR-72 잔존: $PJ"

echo "== discriminating fixture (pre-RED → post-GREEN, no-op stub 이빨) =="
TMP=$(mktemp -d) || exit 2
mkfix() { printf 'ref ADR-72 참조\nADR-720 경계불변\nADR-072 이미3digit\nADR-7 경계불변\n' > "$1"; }

# (1) pre-state: 정규화 미적용 → RED (ADR-72 word-boundary >= 1) — born-green 아님 증명
mkfix "$TMP/f1.txt"
PRE=$(grep -cE "$WB" "$TMP/f1.txt" || true)
[ "$PRE" -ge 1 ] && pass "pre-state RED (ADR-72 ${PRE} occ)" || fail "pre-state 가 RED 아님 (born-green)"

# (2) post-state: 정규화 적용 → GREEN (ADR-72 = 0) + EP/BVA 경계 보존
normalize_file "$TMP/f1.txt"
POST=$(grep -cE "$WB" "$TMP/f1.txt" || true)
[ "$POST" -eq 0 ] && pass "post-state GREEN (ADR-72 0)" || fail "post-state 가 GREEN 아님 (ADR-72 ${POST})"
grep -q 'ADR-720 경계불변' "$TMP/f1.txt" && pass "ADR-720 경계 불변" || fail "ADR-720 경계 파괴"
grep -q 'ADR-7 경계불변' "$TMP/f1.txt" && pass "ADR-7 경계 불변" || fail "ADR-7 경계 파괴"
grep -q 'ADR-0072' "$TMP/f1.txt" && fail "이중정규화 발생(ADR-0072)" || pass "이중정규화 0 (ADR-072 불변)"
grep -q 'ADR-072 이미3digit' "$TMP/f1.txt" && pass "기존 ADR-072 불변" || fail "기존 ADR-072 훼손"

# (3) 판정력 실증: no-op stub → RED 유지 (fixture 에 이빨 있음)
mkfix "$TMP/f2.txt"
noop_file "$TMP/f2.txt"
STUB=$(grep -cE "$WB" "$TMP/f2.txt" || true)
[ "$STUB" -ge 1 ] && pass "no-op stub RED 유지 (판정력 있음)" || fail "no-op stub 가 GREEN (이빨 없음)"
rm -rf "$TMP"

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "[self-test] ALL GREEN — CFP-2762 ADR digit-width 3-digit 통일 정합"
  exit 0
else
  echo "[self-test] ${FAIL} FAIL — CFP-2762 digit-width self-test RED"
  exit 1
fi
