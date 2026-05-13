#!/usr/bin/env bash
# test_measure_rate_limit_fallback_section_aware.sh
# CFP-492 — measure-rate-limit-fallback.sh exit 4 section-aware parsing smoke test (2 case)
#
# Case 1 (OK): 정상 ADR file path → exit 4 미발동 (SONNET_AGENTS 모두 §결정 섹션에서 검출)
# Case 2 (false-positive prevention): agent 이름이 ## 거절된 대안 섹션에만 존재하는 temp ADR
#                                     → section-aware parsing 으로 SKIP → exit 0 정상 종료
#                                     (전체 file grep 시 exit 4 발생했을 케이스)
#
# Usage:
#   bash tests/scripts/test_measure_rate_limit_fallback_section_aware.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && git rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/../..")"
MEASURE_SCRIPT="$REPO_ROOT/scripts/measure-rate-limit-fallback.sh"
ADR_057="$REPO_ROOT/docs/adr/ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md"
ADR_042="$REPO_ROOT/docs/adr/ADR-042-agent-model-selection-policy.md"

# Color output (TERM-aware)
if [[ -t 1 ]]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  NC='\033[0m'
else
  RED=''
  GREEN=''
  NC=''
fi

TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

assert_true() {
  local desc="$1"
  local condition="$2"

  TESTS_RUN=$((TESTS_RUN + 1))
  if eval "$condition"; then
    echo -e "${GREEN}PASS${NC} $desc"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}FAIL${NC} $desc"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

echo "==================================================================="
echo "CFP-492 — measure-rate-limit-fallback.sh exit 4 section-aware test"
echo "Target: $MEASURE_SCRIPT"
echo "==================================================================="
echo ""

# Pre-flight
if [[ ! -f "$MEASURE_SCRIPT" ]]; then
  echo -e "${RED}FATAL${NC} measure script 부재: $MEASURE_SCRIPT"
  exit 2
fi

echo "[Case 1/2] OK case — 정상 ADR (§결정 섹션에 SONNET_AGENTS 8종 포함) → exit 4 미발동"
echo "-------------------------------------------------------------------"

# Case 1: 현재 ADR-057 / ADR-042 를 wrapper-path 로 지정 → exit 4 미발동 (exit 0)
CASE1_EXIT=0
bash "$MEASURE_SCRIPT" \
  --wrapper-path "$REPO_ROOT" \
  --as-of "2025-01" \
  >/dev/null 2>&1 || CASE1_EXIT=$?

# exit 4 (SONNET_AGENTS enum drift) 가 아니면 OK (다른 비0 exit = 입력/write 오류지만 exit 4 아님)
assert_true "Case 1: exit code != 4 (SONNET_AGENTS 모두 §결정 섹션에서 감지됨)" \
  "[ $CASE1_EXIT -ne 4 ]"

echo ""
echo "[Case 2/2] false-positive prevention — agent 이름이 거절 대안 섹션에만 존재하는 temp ADR"
echo "           전체 file grep 시 exit 0, section-aware 시 exit 0 (감지 SKIP — false-positive 방지)"
echo "-------------------------------------------------------------------"

# Case 2: 임시 ADR 파일 작성 — SONNET_AGENTS agent 이름이 §결정 섹션 외부에만 존재.
# 전체 file grep (CFP-492 이전 구현) 이라면: ADR_DETECTED_AGENTS 에 이 이름들이 포함되어
# SONNET_AGENTS subset 검증을 통과하게 됨 (false-positive → exit 0 / 잘못된 PASS).
# section-aware parsing (CFP-492 이후): §결정 섹션 외부 = SKIP → ADR_DETECTED_AGENTS 에 미포함.
# 단, exit 4 는 "SONNET_AGENTS agent 가 ADR 에 부재" 시 발동.
# → 이 temp ADR 은 §결정 섹션 에 SONNET_AGENTS 이름 없음 = exit 4 를 유도 가능.
#   하지만 ADR file 이 부재 시 exit 4 skip (ADR file 미존재 = silent skip) 하므로,
#   temp ADR 을 ADR_057_FILE / ADR_042_FILE 경로로 교체한 임시 wrapper-path 를 구성해야 함.
#
# 구현: 임시 디렉터리에 measure script + temp ADR 을 배치하여 --wrapper-path 로 override.

TMP_DIR="$(mktemp -d -t cfp492-section-test.XXXXXX)"
trap 'rm -rf "$TMP_DIR"' EXIT

mkdir -p "$TMP_DIR/docs/adr"
mkdir -p "$TMP_DIR/docs/stories"

# temp ADR-057: §결정 섹션 없음, 거절 대안 섹션에만 SONNET_AGENTS 이름 포함.
# section-aware parsing → §결정 섹션 내부 = 비어 있음 → SONNET_AGENTS 감지 0건.
# exit 4 조건 = SONNET_AGENTS 의 특정 agent 가 ADR 본문에 부재.
# → 이 temp ADR 에서는 exit 4 가 발동해야 "section-aware 가 제대로 SKIP 했다" 증명.
# 즉, Case 2 의 assert = exit 4 == 4 (거절 대안 섹션의 agent 이름은 SKIP)
cat > "$TMP_DIR/docs/adr/ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md" <<'TEMPEOF'
---
title: "ADR-057 test fixture (CFP-492 section-aware test)"
---

## 상태

Accepted

## 거절된 대안

이 섹션에는 DeveloperAgent, BackendDeveloperAgent, FrontendDeveloperAgent,
IntegrationTestAgent, StatefulTestAgent, CodebaseMapperAgent,
RefactorAgent, DeveloperPLAgent 가 언급되어 있으나
§결정 섹션 외부이므로 section-aware parsing 으로 SKIP 되어야 함.

## 근거

DeveloperAgent 는 여기서도 언급되지만 역시 §결정 섹션 외부.

## 관련 파일
TEMPEOF

# temp ADR-042: 동일 — §결정 섹션 없음.
cat > "$TMP_DIR/docs/adr/ADR-042-agent-model-selection-policy.md" <<'TEMPEOF'
---
title: "ADR-042 test fixture (CFP-492 section-aware test)"
---

## 상태

Accepted

## 거절된 대안

이 섹션에도 agent 이름들이 있으나 §결정 섹션 외부 — SKIP 대상.

## 관련 파일
TEMPEOF

# measure script 실행 — wrapper-path = TMP_DIR
# section-aware parsing 시: §결정 섹션에서 agent 이름 감지 0건 → SONNET_AGENTS drift → exit 4
CASE2_EXIT=0
bash "$MEASURE_SCRIPT" \
  --wrapper-path "$TMP_DIR" \
  --as-of "2025-01" \
  >/dev/null 2>&1 || CASE2_EXIT=$?

assert_true "Case 2: exit 4 발동 (§결정 섹션 외부 agent 이름 SKIP 확인 — false-positive 방지)" \
  "[ $CASE2_EXIT -eq 4 ]"

echo ""
echo "==================================================================="
echo "Test summary: $TESTS_PASSED / $TESTS_RUN passed, $TESTS_FAILED failed"
echo "==================================================================="

if [[ $TESTS_FAILED -gt 0 ]]; then
  exit 1
fi

exit 0
