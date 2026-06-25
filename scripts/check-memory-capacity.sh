#!/usr/bin/env bash
# check-memory-capacity.sh — MEMORY.md 용량관리 게이트 (warning-tier 로컬 self-check)
#
# Carrier: CFP-2392 (ADR-129 §결정 2 — MEMORY.md 용량관리)
#          ADR-071 Amendment 12 §18.7 (§18.2 24.4KB cap + §18.3 슬림화 normative deferred 실현)
#
# 책임 경계 (검증만 — slimming 실행·archive 판단은 Orchestrator 가 owner):
#   - MEMORY.md size > 24.4KB cap 시 slimming 수행 흔적 AND active-Story entry 보존(lossless) 검출.
#   - "이 entry 가 archive 적격 완료-Story 인가" 판정 = semantic → lint 불가(honest decline, ADR-119 abstention).
#     본 lint 은 size + entry presence 만.
#   - warning-tier 로컬 self-check (required CI 불가 — MEMORY.md = ~/.claude 외부 파일 + 클라우드
#     러너 미접근, ADR-128 worktree-clean 동근원).
#
# 입력:
#   MEMORY_MD_PATH=<path>  (test stub 주입점. 빈값/부재 시 default 경로 탐색 → 못 찾으면 exit 0 no-op)
#
# 임계값 (cap): 24.4KB = 24.4 * 1024 = 24985.6 bytes → 정수 임계 24986 bytes.
#   size <= cap → no-op (PASS). size > cap → slimming 흔적 검사.
#
# 검출 메커니즘 (ADR-129 §결정 2):
#   - MEMORY.md 경로 부재(harness 미생성) → no-op exit 0 (graceful, TC4 fail-safe)
#   - size <= cap → PASS exit 0 no-op (TC1)
#   - size > cap → slimming 흔적 검사:
#       slimming 흔적 부재(size 감소 흔적 없음 + archive/topic 갱신 흔적 없음) → WARN (TC2)
#   - lossless invariant (TC3): slimming 후 entry 0 으로 슬림화 = 손실 → active-Story(=any) entry
#       presence 검사. entry 0(파일이 entry 없이 비거나 헤더만) → WARN (lossless 위반).
#       정교한 active-Story 판정은 semantic → lint 범위 밖 (honest decline — presence 만).
#
# fail-safe — always exit 0 (warning-tier):
#   (1) MEMORY.md 경로 부재 → exit 0 no-op (graceful)
#   (2) 읽기 실패 → exit 0 no-op
#   (3) PASS/WARN 모두 exit 0 (required CI 불가, 로컬 self-check)
#
# Output contract (QADev test 가 assert):
#   - WARN 시 stdout: "[memory-capacity] WARN: ..." (sentinel = 정규식 \[memory-capacity\] WARN)
#   - PASS 시 stdout: "[memory-capacity] PASS: ..." (sentinel = \[memory-capacity\] PASS)
#   - no-op(경로부재) 시 stdout: "[memory-capacity] no-op: ..."
#   - 마지막 줄: "[memory-capacity] DONE: size=<bytes> cap=<임계> warn=<0|N>"
#
# Bypass:
#   BYPASS_MEMORY_CAPACITY=1 — skip + exit 0.

set -uo pipefail

# 임계값: 24.4KB = 24.4 * 1024 = 24985.6 → 정수 24986 bytes
MEMORY_CAP_BYTES="${MEMORY_CAP_BYTES:-24986}"

# BYPASS: BYPASS_MEMORY_CAPACITY=1 → 검출 skip
if [[ "${BYPASS_MEMORY_CAPACITY:-}" == "1" ]]; then
  echo "[memory-capacity] BYPASS_MEMORY_CAPACITY=1, skipping" >&2
  exit 0
fi

# MEMORY.md 경로 해석 — env 우선, 빈값이면 default 경로 탐색.
MEMORY_MD_PATH="${MEMORY_MD_PATH:-}"

resolve_memory_path() {
  # 명시 env 가 있으면 그대로 사용 (test stub 주입점)
  if [[ -n "$MEMORY_MD_PATH" ]]; then
    printf '%s' "$MEMORY_MD_PATH"
    return 0
  fi
  # default 탐색 — ~/.claude/projects/<hash>/memory/MEMORY.md (hash glob 불가 → 1개만 존재 시 채택,
  #   복수/부재면 빈값 → no-op). HOME 부재 안전.
  local base="${HOME:-}/.claude/projects"
  [[ -z "${HOME:-}" || ! -d "$base" ]] && { printf ''; return 0; }
  local found=() f
  for f in "$base"/*/memory/MEMORY.md; do
    [[ -f "$f" ]] && found+=("$f")
  done
  if [[ "${#found[@]}" -eq 1 ]]; then
    printf '%s' "${found[0]}"
    return 0
  fi
  # 0개 또는 복수 = 자동 선택 불가 → no-op (graceful)
  printf ''
  return 0
}

MEM_PATH="$(resolve_memory_path)"

# 경로 부재 / 파일 없음 → no-op exit 0 (graceful, TC4 fail-safe)
if [[ -z "$MEM_PATH" || ! -f "$MEM_PATH" ]]; then
  echo "[memory-capacity] no-op: MEMORY.md 경로 부재 (graceful)" >&2
  echo "[memory-capacity] DONE: size=0 cap=$MEMORY_CAP_BYTES warn=0"
  exit 0
fi

# size 측정 — wc -c (읽기 실패 → no-op fail-safe)
SIZE="$(wc -c < "$MEM_PATH" 2>/dev/null | tr -d '[:space:]')" || SIZE=""
if [[ -z "$SIZE" || ! "$SIZE" =~ ^[0-9]+$ ]]; then
  echo "[memory-capacity] no-op: MEMORY.md 읽기 실패 (graceful)" >&2
  echo "[memory-capacity] DONE: size=0 cap=$MEMORY_CAP_BYTES warn=0"
  exit 0
fi

WARN=0

# size <= cap → no-op PASS (TC1)
if [[ "$SIZE" -le "$MEMORY_CAP_BYTES" ]]; then
  echo "[memory-capacity] PASS: size=$SIZE <= cap=$MEMORY_CAP_BYTES (용량 여유, slimming 불요)"
  echo "[memory-capacity] DONE: size=$SIZE cap=$MEMORY_CAP_BYTES warn=$WARN"
  exit 0
fi

# size > cap — slimming 미수행 = over-cap 자체가 흔적 부재 (TC2).
#   본 게이트 시점에 size 가 여전히 cap 초과 = slimming 결과 미반영 → WARN.
echo "[memory-capacity] WARN: size=$SIZE > cap=$MEMORY_CAP_BYTES, slimming 미수행 (용량관리 필요)"
WARN=$((WARN + 1))

# lossless invariant (TC3) — slimming 후 entry 0 으로 슬림화 = 손실.
#   entry presence 검사: MEMORY.md index entry 마커(`- [` 리스트 항목) 존재 여부.
#   semantic active-Story 판정 불가(honest decline) → "최소 1 entry 보존" presence 만.
ENTRY_COUNT="$(grep -cE '^- \[' "$MEM_PATH" 2>/dev/null | tr -d '[:space:]')" || ENTRY_COUNT="0"
[[ -z "$ENTRY_COUNT" || ! "$ENTRY_COUNT" =~ ^[0-9]+$ ]] && ENTRY_COUNT="0"
if [[ "$ENTRY_COUNT" -eq 0 ]]; then
  echo "[memory-capacity] WARN: lossless invariant 위반 — active-Story entry 부재 (entry 0)"
  WARN=$((WARN + 1))
fi

echo "[memory-capacity] DONE: size=$SIZE cap=$MEMORY_CAP_BYTES warn=$WARN"
exit 0
