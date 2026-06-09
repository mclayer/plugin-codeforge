#!/usr/bin/env bats
# CFP-2092: stray-scratch-leak SessionStart 안전망 테스트
# 홈 루트 codeforge 스크래치 의심 항목 advisory 경고 (항상 exit 0).
#
# discriminating fixture 의무 (CFP-1334):
#   WARN 케이스는 구현 없으면 RED → 구현 후 GREEN.
# ADR-061 준수: external .py SSOT, bats wrapper.

SCRIPT="$(dirname "$BATS_TEST_DIRNAME")/../../scripts/check-stray-scratch-leak.sh"
LIB="$(dirname "$BATS_TEST_DIRNAME")/../../scripts/lib/check_stray_scratch_leak.py"

setup() {
  FAKE_HOME="$(mktemp -d)"
}

teardown() {
  rm -rf "$FAKE_HOME"
}

# ─── 기본 동작 ─────────────────────────────────────────────────────────

@test "스크립트 파일 존재" {
  [ -f "$SCRIPT" ]
}

@test "Python SSOT 파일 존재 (ADR-061)" {
  [ -f "$LIB" ]
}

@test "스크립트에 실행 위임(exec python3) 패턴 존재 (ADR-061 thin wrapper)" {
  grep -q "exec python3" "$SCRIPT"
}

# ─── WARN 케이스 (discriminating) ──────────────────────────────────────

@test "홈 루트에 '.tmp-x-story.md' → stderr 경고 + 이름 포함, exit 0" {
  touch "$FAKE_HOME/.tmp-x-story.md"
  run env HOME="$FAKE_HOME" USERPROFILE="$FAKE_HOME" python3 "$LIB"
  [ "$status" -eq 0 ]
  echo "$output" | grep -q "WARNING"
  echo "$output" | grep -q ".tmp-x-story.md"
}

# ─── 깨끗한 HOME ───────────────────────────────────────────────────────

@test "깨끗한 tmp HOME → 경고 없음, exit 0" {
  run env HOME="$FAKE_HOME" USERPROFILE="$FAKE_HOME" python3 "$LIB"
  [ "$status" -eq 0 ]
  ! echo "$output" | grep -q "WARNING"
}

# ─── Bypass ────────────────────────────────────────────────────────────

@test "BYPASS_STRAY_SCRATCH_LEAK=1 → 경고 없음, exit 0" {
  touch "$FAKE_HOME/.tmp-x-story.md"
  run env HOME="$FAKE_HOME" USERPROFILE="$FAKE_HOME" BYPASS_STRAY_SCRATCH_LEAK=1 python3 "$LIB"
  [ "$status" -eq 0 ]
  ! echo "$output" | grep -q "WARNING"
}
