#!/usr/bin/env bash
# CFP-2574 / ADR-143 §결정 4 — spawn description-prefix DETECT thin wrapper + self-test
# ADR-061 §결정 1 — thin wrapper (scripts/lib/check_spawn_description_prefix.py SSOT)
#
# 범위① Agent spawn 최상위 헤더 description 이 렌더-줄 프리픽스 `[에이전트명] MM/DD HH:MM - 내용`
# 형식인지 DETECT (warning-tier, exit 0, rewrite/mutation 0 — SecurityArch §7.1 non-mutation 상속).
#
# 모드:
#   --self-test            : 인라인 discriminating fixtures (1 conformant + 6 nonconformant) 로 detector
#                            검증. detector 가 오분류하면 exit 1 (meta-test). 전부 맞으면 exit 0.
#   (없음)|--description-stdin : stdin 을 detector 로 passthrough, exit 0.
# Graceful degrade: Python·detector 부재 → stderr warning + exit 0 (advisory non-blocking).
# Usage / exit / semantics 상세: scripts/lib/check_spawn_description_prefix.py header.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DETECTOR="$SCRIPT_DIR/lib/check_spawn_description_prefix.py"
MARKER="[check-spawn-description-prefix]"

# Python 탐색
PY=""
if command -v python3 >/dev/null 2>&1; then
  PY="python3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
fi

usage() {
  cat >&2 <<'USAGE'
Usage:
  check-spawn-description-prefix.sh --self-test           # 인라인 fixtures 로 detector meta-검증
  check-spawn-description-prefix.sh [--description-stdin]  # stdin passthrough (default)
USAGE
}

# detector 를 desc 인자로 실행 → description_prefix_conformant 를 'true'/'false'/'error' 로 echo
detector_verdict() {
  local desc="$1"
  local out
  out="$(printf '%s' "$desc" | "$PY" "$DETECTOR" --description-stdin 2>/dev/null)" || true
  printf '%s' "$out" | "$PY" -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    print('true' if d.get('description_prefix_conformant') else 'false')
except Exception:
    print('error')
"
}

# 단일 fixture 검증 — detector 판정이 expected 와 다르면 return 1 (meta-test 실패)
check_case() {
  local name="$1" desc="$2" expected="$3"
  local got
  got="$(detector_verdict "$desc")"
  if [ "$got" != "$expected" ]; then
    echo "$MARKER SELF-TEST case '$name': expected conformant=$expected got=$got" >&2
    return 1
  fi
  return 0
}

run_self_test() {
  if [ -z "$PY" ]; then
    echo "$MARKER WARN: Python unavailable — self-test skipped (graceful, exit 0)" >&2
    return 0
  fi
  if [ ! -f "$DETECTOR" ]; then
    echo "$MARKER WARN: detector not found ($DETECTOR) — self-test skipped (graceful, exit 0)" >&2
    return 0
  fi

  local fail=0
  # conformant fixture (expected true)
  check_case "conformant"      "[DeveloperAgent] 07/05 02:13 - x"        "true"  || fail=1
  # nonconformant fixtures (expected false) — 6 discriminating axes
  check_case "missing-bracket" "DeveloperAgent 07/05 02:13 - x"         "false" || fail=1
  check_case "missing-time"    "[DeveloperAgent] - x"                   "false" || fail=1
  check_case "date-sep-hyphen" "[DeveloperAgent] 07-05 02:13 - x"       "false" || fail=1
  check_case "offset-present"  "[DeveloperAgent] 07/05 02:13+09:00 - x" "false" || fail=1
  check_case "double-space"    "[DeveloperAgent] 07/05 02:13  - x"      "false" || fail=1
  check_case "wrong-sep-colon" "[DeveloperAgent] 07/05 02:13 : x"       "false" || fail=1

  if [ "$fail" -ne 0 ]; then
    echo "$MARKER SELF-TEST FAIL — detector misclassified 1+ fixture (meta-test, exit 1)" >&2
    return 1
  fi
  echo "$MARKER SELF-TEST PASS — 7 discriminating fixtures (1 conformant + 6 nonconformant)"
  return 0
}

run_passthrough() {
  if [ -z "$PY" ]; then
    echo "$MARKER WARN: Python unavailable — passthrough skipped (graceful, exit 0)" >&2
    exit 0
  fi
  if [ ! -f "$DETECTOR" ]; then
    echo "$MARKER WARN: detector not found ($DETECTOR) — passthrough skipped (graceful, exit 0)" >&2
    exit 0
  fi
  "$PY" "$DETECTOR" --description-stdin || true
  exit 0
}

case "${1:-}" in
  --self-test)
    run_self_test
    exit $?
    ;;
  ""|--description-stdin)
    run_passthrough
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    echo "$MARKER ERROR: unknown arg '$1'" >&2
    usage
    exit 2
    ;;
esac
