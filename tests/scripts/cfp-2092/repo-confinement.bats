#!/usr/bin/env bats
# CFP-2092: repo-confinement PreToolUse(Bash) 가드 테스트
# repo 밖(홈 루트) 스크래치 누출 차단 (exit 2 = block, exit 0 = allow).
#
# discriminating fixture 의무 (CFP-1334):
#   BLOCK 케이스는 구현 없으면 RED → 구현 후 GREEN.
# ADR-061 준수: external .py SSOT, bats wrapper.

SCRIPT="$(dirname "$BATS_TEST_DIRNAME")/../../scripts/check-repo-confinement.sh"
LIB="$(dirname "$BATS_TEST_DIRNAME")/../../scripts/lib/check_repo_confinement.py"

# JSON payload 생성 헬퍼 — tool_name / command / cwd 조합.
# (jq 비의존 — python 으로 안전 직렬화.)
_payload() {
  python3 - "$1" "$2" "$3" << 'PYEOF'
import json, sys
tool_name, command, cwd = sys.argv[1], sys.argv[2], sys.argv[3]
obj = {"tool_name": tool_name, "tool_input": {"command": command}}
if cwd:
    obj["cwd"] = cwd
print(json.dumps(obj))
PYEOF
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

# ─── BLOCK 케이스 (discriminating) ─────────────────────────────────────

@test "명시 홈 쓰기 '> ~/foo.md' → exit 2 (BLOCK)" {
  local pl
  pl="$(_payload "Bash" "echo hi > ~/foo.md" "")"
  run bash -c "printf '%s' '$pl' | python3 '$LIB'"
  [ "$status" -eq 2 ]
}

@test "cwd=home + 'git clone url foo' → exit 2 (BLOCK)" {
  local home pl
  home="$(python3 -c 'import os;print(os.path.expanduser("~"))')"
  pl="$(_payload "Bash" "git clone https://example.com/x.git foo" "$home")"
  run bash -c "printf '%s' '$pl' | python3 '$LIB'"
  [ "$status" -eq 2 ]
}

# F-1: fd 번호 redirect 우회 차단
@test "F-1: 'echo x 1>~/leak.md' → exit 2 (BLOCK, fd redirect)" {
  local pl
  pl="$(_payload "Bash" "echo x 1>~/leak.md" "")"
  run bash -c "printf '%s' '$pl' | python3 '$LIB'"
  [ "$status" -eq 2 ]
}

@test "F-1: 'echo x 2>>~/leak.md' → exit 2 (BLOCK, fd append redirect)" {
  local pl
  pl="$(_payload "Bash" "echo x 2>>~/leak.md" "")"
  run bash -c "printf '%s' '$pl' | python3 '$LIB'"
  [ "$status" -eq 2 ]
}

# F-5: path traversal carve-out 우회 차단
@test "F-5: 'echo x > ~/.claude/../leak.md' → exit 2 (BLOCK, traversal)" {
  local pl
  pl="$(_payload "Bash" "echo x > ~/.claude/../leak.md" "")"
  run bash -c "printf '%s' '$pl' | python3 '$LIB'"
  [ "$status" -eq 2 ]
}

# F-4: cwd=home + .claude 무관 명령 → 면제 과대 차단
@test "F-4: cwd=home + 'echo x > out.txt && cat ~/.config/foo' → exit 2 (.claude 없음)" {
  local home pl
  home="$(python3 -c 'import os;print(os.path.expanduser("~"))')"
  pl="$(_payload "Bash" "echo x > out.txt && cat ~/.config/foo" "$home")"
  run bash -c "printf '%s' '$pl' | python3 '$LIB'"
  [ "$status" -eq 2 ]
}

# ─── ALLOW 케이스 ──────────────────────────────────────────────────────

@test "carve-out '> ~/.claude/codeforge-scratch/foo.md' → exit 0 (ALLOW)" {
  local pl
  pl="$(_payload "Bash" "echo hi > ~/.claude/codeforge-scratch/foo.md" "")"
  run bash -c "printf '%s' '$pl' | python3 '$LIB'"
  [ "$status" -eq 0 ]
}

@test "비-Bash tool (Read) → exit 0 (ALLOW)" {
  local pl
  pl="$(_payload "Read" "echo hi > ~/foo.md" "")"
  run bash -c "printf '%s' '$pl' | python3 '$LIB'"
  [ "$status" -eq 0 ]
}

@test "repo 안 cwd + 'echo hi > out.txt' (cwd≠home) → exit 0 (ALLOW)" {
  local tmp pl
  tmp="$(mktemp -d)"
  pl="$(_payload "Bash" "echo hi > out.txt" "$tmp")"
  run bash -c "printf '%s' '$pl' | python3 '$LIB'"
  rm -rf "$tmp"
  [ "$status" -eq 0 ]
}

@test "읽기 명령 'cat ~/foo' → exit 0 (ALLOW — 쓰기 맥락 아님, false-positive 없음)" {
  local pl
  pl="$(_payload "Bash" "cat ~/foo" "")"
  run bash -c "printf '%s' '$pl' | python3 '$LIB'"
  [ "$status" -eq 0 ]
}

# F-1 false-positive 회피: fd-dup `2>&1` 은 redirect 으로 안 침 (홈 타깃 없음, cwd≠home)
@test "F-1 회피: 'cmd 2>&1' (cwd≠home, 홈 타깃 없음) → exit 0 (ALLOW)" {
  local tmp pl
  tmp="$(mktemp -d)"
  pl="$(_payload "Bash" "somecmd 2>&1" "$tmp")"
  run bash -c "printf '%s' '$pl' | python3 '$LIB'"
  rm -rf "$tmp"
  [ "$status" -eq 0 ]
}

# F-4 회피: cwd=home + `git clone url ~/.claude/x` (정식 carve-out) → exit 0
@test "F-4 회피: cwd=home + 'git clone url ~/.claude/x' → exit 0 (ALLOW)" {
  local home pl
  home="$(python3 -c 'import os;print(os.path.expanduser("~"))')"
  pl="$(_payload "Bash" "git clone https://example.com/x.git ~/.claude/x" "$home")"
  run bash -c "printf '%s' '$pl' | python3 '$LIB'"
  [ "$status" -eq 0 ]
}

# `cd ~` (cwd≠home, 생성 동사·redirect 없음) → exit 0
@test "'cd ~' (cwd≠home) → exit 0 (ALLOW)" {
  local tmp pl
  tmp="$(mktemp -d)"
  pl="$(_payload "Bash" "cd ~" "$tmp")"
  run bash -c "printf '%s' '$pl' | python3 '$LIB'"
  rm -rf "$tmp"
  [ "$status" -eq 0 ]
}

# ─── Bypass ────────────────────────────────────────────────────────────

@test "BYPASS_REPO_CONFINEMENT=1 + BLOCK 케이스 → exit 0" {
  local pl
  pl="$(_payload "Bash" "echo hi > ~/foo.md" "")"
  run bash -c "printf '%s' '$pl' | BYPASS_REPO_CONFINEMENT=1 python3 '$LIB'"
  [ "$status" -eq 0 ]
}
