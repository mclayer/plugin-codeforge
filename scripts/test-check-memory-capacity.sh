#!/usr/bin/env bash
# CFP-2392 Phase 2 — check-memory-capacity.sh 변별 test (anti-theater)
#
# 검증 대상 = scripts/check-memory-capacity.sh (DeveloperAgent 산출, MEMORY.md 용량관리
# 게이트 — size 가 cap 을 넘는데 slimming 미수행이거나 lossless invariant(entry 0 으로
# 과슬림) 면 warning-tier 로 경고). 본 러너는 §8.2 Test Contract 의 TC1~TC4 를 이행한다.
#
# 선례 = scripts/test-check-worktree-completion-clean.sh (자립 bash 러너, mktemp fixture,
# env override 주입, PASS/FAIL 카운터, exit-code ∧ stdout sentinel 동시 assert). 본 러너는
# 동형 패턴을 답습하되 stub 대신 MEMORY.md fixture 파일을 MEMORY_MD_PATH env 로 주입한다.
#
# anti-theater 원칙 (CFP-2270 D1 + memory gotcha "missing-case + exit assert" — 비협상):
#   - 각 TC = fixture 작성 → 스크립트 실행 → exit code assert ∧ stdout sentinel assert 동시.
#   - discriminating-negative(TC2/TC3) 필수 — size > cap(미슬림) 또는 entry 0(과슬림) 이면
#     WARN 이 *실제로 등장*, size <= cap(TC1)에선 WARN 이 *부재* 임을 양방향 변별
#     (mutation 생존 차단: 항상 PASS 거나 항상 WARN 이면 본 러너가 잡는다).
#   - || true 마스킹 / always-pass 금지.
#
# 대상 스크립트 부재 시 SKIP (DeveloperAgent 산출물 미 commit 상태) — RED 정상.
#
# fixture 주입 = MEMORY_MD_PATH env (대상 스크립트의 test stub 주입점). mktemp 로 MEMORY.md
# fixture 생성 후 size(head -c 로 정확 byte) / entry 유무 조절. TC4 = 존재 안 하는 경로 주입.
# BYPASS = BYPASS_MEMORY_CAPACITY=1 (본 러너 미사용).
#
# 임계 (DeveloperAgent 확정): cap = 24.4KB = 24.4*1024 = 24985.6 → 정수 임계.
# fixture 는 임계 위/아래 안전 마진: <=24000 bytes(아래) / >=26000 bytes(위).
#
# Output contract (DeveloperAgent 확정 — 이걸 assert):
#   - WARN sentinel (정규식): \[memory-capacity\] WARN
#   - PASS sentinel: [memory-capacity] PASS:
#   - 마지막 줄: [memory-capacity] DONE: size=... cap=... warn=...
#   - always exit 0.
#
# Exit code: 0 (all tests pass) / 1 (any test fails)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$REPO_ROOT/scripts/check-memory-capacity.sh"

PASS=0
FAIL=0

# 대상 스크립트 부재 = DeveloperAgent 산출물 미 commit. RED 정상 — SKIP 후 비-fail 종료.
if [ ! -f "$TARGET" ]; then
  echo "::warning::check-memory-capacity.sh 부재 — DevPL 산출물 미 commit (RED 정상)."
  echo "본 러너는 스크립트가 존재하는 전제로 작성됨. DevPL 최종 commit 후 실 검증 전환."
  echo "Total: PASS=0 FAIL=0 (SKIPPED — target absent)"
  exit 0
fi

# ─── fixture helper: MEMORY.md fixture 생성 ─────────────────────────────────
# make_memory <path> <target-bytes> <with-entry(0/1)>
#   - target-bytes 만큼 정확히 채운다 (head -c). with-entry=1 이면 active-Story entry
#     1줄을 선두에 둔 뒤 padding (lossless invariant — entry 존재). =0 이면 entry 없는
#     padding 만 (과슬림 over: active-Story entry 부재 → lossless 위반).
make_memory() {
  local path="$1" target_bytes="$2" with_entry="$3"
  local entry_line="- [CFP-9999 ACTIVE 2026-06-25 — sample active-Story entry](project_cfp_9999_sample.md)"

  if [ "$with_entry" = "1" ]; then
    # entry 1줄 + 개행, 나머지는 padding 으로 정확 byte 맞춤.
    {
      printf '%s\n' "$entry_line"
      # entry+개행 길이만큼 제외한 나머지를 'x' 로 채움.
      local head_len; head_len=$(( ${#entry_line} + 1 ))
      local pad=$(( target_bytes - head_len ))
      [ "$pad" -lt 0 ] && pad=0
      head -c "$pad" /dev/zero | tr '\0' 'x'
    } > "$path"
  else
    # entry 0 (과슬림 over) — 목록 마커 없는 padding 만.
    head -c "$target_bytes" /dev/zero | tr '\0' 'y' > "$path"
  fi

  # 정확 byte 보정 (entry 분기 산술 오차 방지) — truncate 로 hard cap.
  if command -v truncate >/dev/null 2>&1; then
    truncate -s "$target_bytes" "$path"
  fi
}

# ─── 공통 실행 + assert ─────────────────────────────────────────────────────
# run_case <name> <memory-path|EXISTS-FALSE> <expect-warn: yes|no> <expect-exit> \
#          [require-substr] [forbid-substr]
#
# anti-theater 2-축 동시 assert (+ 선택적 line-level 변별):
#   ① exit code — 항상 $expect_exit (게이트는 always exit 0).
#   ② WARN sentinel — `[memory-capacity] WARN` 정규식 등장 여부가 $expect_warn 과 일치.
#   ③ (선택) require-substr — stdout 에 반드시 등장해야 하는 고정 문자열 (lossless WARN 라인 등
#      특정 WARN 축을 size-WARN 과 구분해 pin. 빈값이면 검사 안 함).
#   ④ (선택) forbid-substr — stdout 에 등장하면 안 되는 고정 문자열 (예: lossless WARN 부재 확인).
# 모두 충족해야 PASS.
run_case() {
  local name="$1" mem_path="$2" expect_warn="$3" expect_exit="$4"
  local require_substr="${5:-}" forbid_substr="${6:-}"

  local out exit_code=0
  out=$(
    MEMORY_MD_PATH="$mem_path" \
    bash "$TARGET" 2>&1
  ) || exit_code=$?

  # ① exit code assert (anti-theater: 항상 검사)
  if [ "$exit_code" -ne "$expect_exit" ]; then
    echo "✗ FAIL: $name"
    echo "  expected exit $expect_exit, got $exit_code"
    echo "  output: $out"
    FAIL=$((FAIL + 1))
    return 0
  fi

  # ② WARN sentinel assert — `[memory-capacity] WARN` 정규식 등장 여부.
  local warned=0
  if printf '%s' "$out" | grep -qE '\[memory-capacity\] WARN'; then
    warned=1
  fi
  if [ "$expect_warn" = "yes" ] && [ "$warned" -ne 1 ]; then
    echo "✗ FAIL: $name"
    echo "  expected warn=yes, got warn=$warned"
    echo "  output: $out"
    FAIL=$((FAIL + 1))
    return 0
  fi
  if [ "$expect_warn" = "no" ] && [ "$warned" -ne 0 ]; then
    echo "✗ FAIL: $name"
    echo "  expected warn=no, got warn=$warned"
    echo "  output: $out"
    FAIL=$((FAIL + 1))
    return 0
  fi

  # ③ require-substr (특정 WARN 축 pin — lossless 등)
  if [ -n "$require_substr" ] && ! printf '%s' "$out" | grep -qF "$require_substr"; then
    echo "✗ FAIL: $name"
    echo "  required substring 부재: '$require_substr'"
    echo "  output: $out"
    FAIL=$((FAIL + 1))
    return 0
  fi

  # ④ forbid-substr (특정 라인 부재 확인 — entry 보유 시 lossless WARN 없어야 함 등)
  if [ -n "$forbid_substr" ] && printf '%s' "$out" | grep -qF "$forbid_substr"; then
    echo "✗ FAIL: $name"
    echo "  forbidden substring 등장: '$forbid_substr'"
    echo "  output: $out"
    FAIL=$((FAIL + 1))
    return 0
  fi

  echo "✓ PASS: $name (exit $exit_code, warn=$warned)"
  PASS=$((PASS + 1))
}

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# ─── TC1: size <= cap → exit 0 no-op PASS, WARN 부재 ───────────────────────
# 24000 bytes (cap 24986 아래, 안전 마진). entry 보유. WARN 없어야 함.
make_memory "$TMP/mem_under.md" 24000 1
run_case "TC1: size <= cap(24000B, entry 보유) → no-op PASS, WARN 부재" \
  "$TMP/mem_under.md" "no" 0

# ─── TC2 (discriminating): size > cap, slimming 미수행 → exit 0 ∧ WARN 등장 ──
# 26000 bytes (cap 24986 위, 안전 마진). entry 보유(슬림 안 됨 = 미수행). WARN 의무.
# (TC1 의 WARN 부재와 양방향 변별 — 항상-PASS mutation 을 본 케이스가 잡는다.)
# forbid: lossless WARN 라인은 entry 보유라 등장하면 안 됨 — size-WARN 과 lossless-WARN 의
# 두 축이 독립임을 양방향 pin (TC3 과 짝).
make_memory "$TMP/mem_over.md" 26000 1
run_case "TC2 (discriminating): size > cap(26000B, entry 보유, 미슬림) → size-WARN 등장 ∧ lossless-WARN 부재" \
  "$TMP/mem_over.md" "yes" 0 \
  "size=26000 > cap" \
  "lossless invariant 위반"

# ─── TC3 (lossless invariant): size > cap ∧ entry 0(과슬림 over) → exit 0 ∧ lossless WARN 등장 ─
# 26000 bytes 인데 active-Story entry 부재 = lossless 위반(entry 0 으로 과슬림). WARN 의무.
# require: lossless WARN 라인이 *특정적으로* 등장해야 함 (size-WARN 만으로 vacuous 통과 차단 —
# TC2 forbid 와 짝지어 lossless 축이 entry presence 로 진짜 변별됨을 입증).
make_memory "$TMP/mem_noentry.md" 26000 0
run_case "TC3 (lossless): size > cap(26000B) ∧ active-Story entry 0(과슬림 over) → lossless WARN 등장" \
  "$TMP/mem_noentry.md" "yes" 0 \
  "lossless invariant 위반 — active-Story entry 부재"

# ─── TC4 (fail-safe): MEMORY.md 경로 부재 → exit 0 no-op, WARN 부재 ─────────
# 존재 안 하는 경로 주입 — 게이트는 always exit 0 보존하고 거짓 WARN 을 내지 않아야 한다.
run_case "TC4 (fail-safe): MEMORY.md 경로 부재(존재안하는경로) → no-op, WARN 부재" \
  "$TMP/does-not-exist-memory.md" "no" 0

# ─── 요약 ──────────────────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"

if [ "$FAIL" -eq 0 ]; then
  echo "All tests passed (memory-capacity 변별 검증 — TC1~TC4)."
  exit 0
else
  echo "Some tests failed (memory-capacity 가 WARN/PASS/fail-safe 계약을 못 지킴)."
  exit 1
fi
