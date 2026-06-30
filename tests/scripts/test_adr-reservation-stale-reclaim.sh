#!/usr/bin/env bash
# tests/scripts/test_adr-reservation-stale-reclaim.sh
# CFP-2491 / Epic CFP-2481 E3b — stale-reclaim Python smoke test.
# FIX (구현리뷰 P0 carry F1): inline heredoc Python 추출(scripts/lib/adr-reservation-stale-reclaim.py)에 따른
#   test-escape 폐쇄 — bats(primitive)가 미실행하던 reclaim 로직을 실제 실행해 검증한다.
#
# 검증 (Change Plan §3.5 / ADR-133 A1-4 정책):
#   SMOKE-1: stale claimed + ADR 미존재 → abandoned 마킹 (changed=1)
#   SMOKE-2: max_adr_number 불변 (번호 free 복원 0 — 단조성 보존, gap 잔류)
#   SMOKE-3: 대응 ADR 파일 존재(committed) → 회수 대상 아님 (claimed 유지)
#   SMOKE-4: TTL 미경과(recent claim) → skip (claimed 유지)
#   SMOKE-5: --out write path 정상 (CHANGED 정수 stdout + state file write)
#
# 실 SSOT in-place mutate 0 — 전부 mktemp 격리.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RECLAIM_PY="$REPO_ROOT/scripts/lib/adr-reservation-stale-reclaim.py"
PYBIN="$(command -v python3 || command -v python)"

PASS=0
FAIL=0

run_reclaim() {
  # $1=state-file $2=adr-dir $3=cutoff [$4=out]
  if [ -n "${4:-}" ]; then
    "$PYBIN" "$RECLAIM_PY" --state-file "$1" --adr-dir "$2" --cutoff "$3" --out "$4"
  else
    "$PYBIN" "$RECLAIM_PY" --state-file "$1" --adr-dir "$2" --cutoff "$3"
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "CFP-2491: ADR-RESERVATION stale-reclaim Python smoke test (test-escape 폐쇄)"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# ─── SMOKE-1+2+3+4: 혼합 claims → abandoned/유지 정확 판정 + max 불변 ─────────────
test_mixed_reclaim() {
  local d state adr_dir out
  d="$("$PYBIN" -c 'import tempfile,os; print(tempfile.mkdtemp().replace(os.sep,"/"))')"  # cross-tool path 일관 (MSYS bash ↔ python)
  state="$d/claim-state.json"
  adr_dir="$d/archive/adr"
  out="$d/new-state.json"
  mkdir -p "$adr_dir"
  # ADR-133 = committed (file 존재) / ADR-134 = stale + 미존재 / ADR-200 = recent
  echo "# adr 133" > "$adr_dir/ADR-133-foo.md"
  cat > "$state" <<JSON
{
  "max_adr_number": 200,
  "claims": [
    {"adr_number": 133, "claimant": "A:c1:r1", "status": "claimed", "claimed_at": "2026-01-01T00:00:00Z"},
    {"adr_number": 134, "claimant": "A:c2:r2", "status": "claimed", "claimed_at": "2026-01-01T00:00:00Z"},
    {"adr_number": 200, "claimant": "A:c3:r3", "status": "claimed", "claimed_at": "2026-06-29T00:00:00Z"}
  ]
}
JSON
  local changed
  changed=$(run_reclaim "$state" "$adr_dir" "2026-06-01T00:00:00Z" "$out")

  # SMOKE-5: --out 모드 stdout = changed 정수
  if [ "$changed" != "1" ]; then
    echo "✗ FAIL: SMOKE-1 changed — expected 1, got '$changed'"; FAIL=$((FAIL+1)); rm -rf "$d"; return 1
  fi

  # 결과 state 검사
  local s134 s133 s200 maxn
  s134=$("$PYBIN" -c "import json; d=json.load(open('$out',encoding='utf-8')); print([c['status'] for c in d['claims'] if c['adr_number']==134][0])")
  s133=$("$PYBIN" -c "import json; d=json.load(open('$out',encoding='utf-8')); print([c['status'] for c in d['claims'] if c['adr_number']==133][0])")
  s200=$("$PYBIN" -c "import json; d=json.load(open('$out',encoding='utf-8')); print([c['status'] for c in d['claims'] if c['adr_number']==200][0])")
  maxn=$("$PYBIN" -c "import json; d=json.load(open('$out',encoding='utf-8')); print(d['max_adr_number'])")
  rm -rf "$d"

  # SMOKE-1: 134 → abandoned
  if [ "$s134" = "abandoned" ]; then echo "✓ PASS: SMOKE-1 — stale+미존재(134) abandoned 마킹"; PASS=$((PASS+1)); else echo "✗ FAIL: SMOKE-1 — 134=$s134 (기대 abandoned)"; FAIL=$((FAIL+1)); fi
  # SMOKE-2: max 불변 (200)
  if [ "$maxn" = "200" ]; then echo "✓ PASS: SMOKE-2 — max_adr_number 불변(200, 번호 free 복원 0)"; PASS=$((PASS+1)); else echo "✗ FAIL: SMOKE-2 — max=$maxn (기대 200)"; FAIL=$((FAIL+1)); fi
  # SMOKE-3: 133 committed → claimed 유지
  if [ "$s133" = "claimed" ]; then echo "✓ PASS: SMOKE-3 — committed(133 file 존재) claimed 유지(회수 대상 아님)"; PASS=$((PASS+1)); else echo "✗ FAIL: SMOKE-3 — 133=$s133 (기대 claimed)"; FAIL=$((FAIL+1)); fi
  # SMOKE-4: 200 recent → claimed 유지
  if [ "$s200" = "claimed" ]; then echo "✓ PASS: SMOKE-4 — recent(200 TTL 미경과) claimed 유지(skip)"; PASS=$((PASS+1)); else echo "✗ FAIL: SMOKE-4 — 200=$s200 (기대 claimed)"; FAIL=$((FAIL+1)); fi
}

# ─── SMOKE-5: --out write path (state file 실제 생성) ─────────────────────────────
test_out_write() {
  local d state adr_dir out changed
  d="$("$PYBIN" -c 'import tempfile,os; print(tempfile.mkdtemp().replace(os.sep,"/"))')"  # cross-tool path 일관 (MSYS bash ↔ python)
  state="$d/s.json"; adr_dir="$d/adr"; out="$d/o.json"
  mkdir -p "$adr_dir"
  echo '{"max_adr_number":50,"claims":[{"adr_number":50,"claimant":"A:c:r","status":"claimed","claimed_at":"2026-01-01T00:00:00Z"}]}' > "$state"
  changed=$(run_reclaim "$state" "$adr_dir" "2026-06-01T00:00:00Z" "$out")
  if [ -f "$out" ] && [ "$changed" = "1" ]; then
    echo "✓ PASS: SMOKE-5 — --out write path (state file 생성 + changed=1 stdout)"; PASS=$((PASS+1))
  else
    echo "✗ FAIL: SMOKE-5 — out exists=$([ -f "$out" ] && echo 1 || echo 0) changed=$changed"; FAIL=$((FAIL+1))
  fi
  rm -rf "$d"
}

test_mixed_reclaim || true
test_out_write || true

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "Stale-reclaim smoke Results: $PASS passed, $FAIL failed"
echo "═══════════════════════════════════════════════════════════════════════════════"
if [ "$FAIL" -eq 0 ]; then echo "All stale-reclaim smoke tests PASSED ✓"; exit 0; else echo "Some stale-reclaim smoke tests FAILED ✗"; exit 1; fi
