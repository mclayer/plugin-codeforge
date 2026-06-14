#!/usr/bin/env bash
# test-check-no-superpowers.sh — 4 케이스 검증 (positive/negative)
# ADR-122 회귀 방지 설계 fixture — 정규식 · EXEMPT · 콜론 구분
set -euo pipefail

# ── 격리 sandbox 생성 (repo 오염 방지) ────────────────────────────────────────
SANDBOX=$(mktemp -d)
trap "rm -rf '$SANDBOX'" EXIT

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_PATH="$REPO_ROOT/scripts/check-no-superpowers.sh"

# SCAN_ROOT 환경변수 지원 추가 (test fixture 용 override)
SCAN_ROOT="${SCAN_ROOT:-$REPO_ROOT}"

# ── Case (a): positive — temp 영역에 라이브 호출 inject → exit 1 기대 ──────────
echo "━━ Case (a): positive — superpowers:brainstorming 라이브 호출"
CASE_A_DIR="$SANDBOX/case-a"
mkdir -p "$CASE_A_DIR/docs"
cat > "$CASE_A_DIR/docs/test-positive.md" << 'EOF'
# Test positive

본 문서에서 brainstorming 을 호출한다:

[superpowers:brainstorming](스킬 호출)

내용 종료.
EOF

# SCAN_ROOT 환경변수로 스크립트에 case 디렉터리 지정 (exit code 로 검사)
if SCAN_ROOT="$CASE_A_DIR" bash "$SCRIPT_PATH" >/dev/null 2>&1; then
  echo "✗ Case (a) FAIL: exit 0 (warning 미감지)"
  CASE_A_PASS=false
else
  echo "✓ Case (a) PASS: exit 1 (warning 호출 감지)"
  CASE_A_PASS=true
fi

# ── Case (b): negative — literal 경로 문자열만 존재 (콜론 아님) → exit 0 기대 ────
echo ""
echo "━━ Case (b): negative — docs/superpowers/specs/x.md literal 경로 (no colon)"
CASE_B_DIR="$SANDBOX/case-b"
mkdir -p "$CASE_B_DIR/docs"
cat > "$CASE_B_DIR/docs/test-literal-path.md" << 'EOF'
# Test literal path

스펙 위치: docs/superpowers/specs/brainstorm-design.md

이것은 경로 참조일 뿐 호출이 아니다.
EOF

if SCAN_ROOT="$CASE_B_DIR" bash "$SCRIPT_PATH" 2>&1 | grep -q "OK"; then
  echo "✓ Case (b) PASS: exit 0 (literal 경로만으로 미감지)"
  CASE_B_PASS=true
else
  echo "✗ Case (b) FAIL: literal 경로가 오탐 (false positive)"
  CASE_B_PASS=false
fi

# ── Case (c): negative — archive/adr/ 안의 호출 → EXEMPT → exit 0 기대 ────────
echo ""
echo "━━ Case (c): negative — archive/adr/ EXEMPT 영역 내 호출"
CASE_C_DIR="$SANDBOX/case-c"
mkdir -p "$CASE_C_DIR/archive/adr"
cat > "$CASE_C_DIR/archive/adr/ADR-999-test.md" << 'EOF'
# ADR-999 Test (이력 보존)

과거 설계에서 superpowers:brainstorming 을 사용했었다.
이는 이력 문서이므로 EXEMPT 한다.
EOF

if SCAN_ROOT="$CASE_C_DIR" bash "$SCRIPT_PATH" 2>&1 | grep -q "OK"; then
  echo "✓ Case (c) PASS: exit 0 (archive/adr/** EXEMPT)"
  CASE_C_PASS=true
else
  echo "✗ Case (c) FAIL: archive/adr 가 filter 미적용"
  CASE_C_PASS=false
fi

# ── Case (d): positive — playbook 동형 라이브 doc 경로에 호출 → exit 1 기대 ──────
echo ""
echo "━━ Case (d): positive — docs/orchestrator-playbook.md 동형 라이브 호출"
CASE_D_DIR="$SANDBOX/case-d"
mkdir -p "$CASE_D_DIR/docs"
cat > "$CASE_D_DIR/docs/orchestrator-playbook.md" << 'EOF'
# Orchestrator Playbook

절차:

1. superpowers:executing-plans 를 호출하여 계획을 실행한다.
2. 검증 단계를 거친다.

종료.
EOF

if SCAN_ROOT="$CASE_D_DIR" bash "$SCRIPT_PATH" >/dev/null 2>&1; then
  echo "✗ Case (d) FAIL: exit 0 (playbook 호출 미감지)"
  CASE_D_PASS=false
else
  echo "✓ Case (d) PASS: exit 1 (라이브 playbook 호출 감지)"
  CASE_D_PASS=true
fi

# ── 결과 종합 ──────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 결과 종합:"
ALL_PASS=true
for case in A B C D; do
  VAR="CASE_${case}_PASS"
  if [[ "${!VAR}" == "true" ]]; then
    echo "  Case ($case): ✓ PASS"
  else
    echo "  Case ($case): ✗ FAIL"
    ALL_PASS=false
  fi
done

if $ALL_PASS; then
  echo ""
  echo "✓ 모든 테스트 케이스 PASS (exit 0)"
  exit 0
else
  echo ""
  echo "✗ 테스트 실패 케이스 존재 (exit 1)"
  exit 1
fi
