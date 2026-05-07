#!/usr/bin/env bash
# CFP-128 / ADR-033 — TDD wrapper for scripts/check-container-strategy.sh
# 5 시나리오: docker_first / docker_first_old_compose_name / legacy_systemd / none / negative-Dockerfile / negative-compose
# Codex P1-3 fix: REPO_ROOT 명시 + duality (compose.yml | docker-compose.yml) coverage + 2 negative case

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$REPO_ROOT/scripts/check-container-strategy.sh"
FIXT="$REPO_ROOT/scripts/fixtures/check-container-strategy"

[ -f "$SCRIPT" ] || { echo "FAIL: $SCRIPT 부재"; exit 1; }
[ -d "$FIXT" ] || { echo "FAIL: $FIXT 부재"; exit 1; }

PASS=0; FAIL=0

# Scenario 1: docker_first + Dockerfile + compose.yml → PASS
if ( cd "$FIXT/docker_first" && bash "$SCRIPT" >/dev/null 2>&1 ); then
  echo "PASS: scenario 1 docker_first (compose.yml)"; PASS=$((PASS+1))
else
  echo "FAIL: scenario 1 docker_first (compose.yml)"; FAIL=$((FAIL+1))
fi

# Scenario 1b: docker_first + Dockerfile + docker-compose.yml (옛 naming, duality fixture)
if ( cd "$FIXT/docker_first_old_compose_name" && bash "$SCRIPT" >/dev/null 2>&1 ); then
  echo "PASS: scenario 1b docker_first (docker-compose.yml duality)"; PASS=$((PASS+1))
else
  echo "FAIL: scenario 1b docker_first (docker-compose.yml duality)"; FAIL=$((FAIL+1))
fi

# Scenario 2: legacy_systemd → PASS (skip)
if ( cd "$FIXT/legacy_systemd" && bash "$SCRIPT" >/dev/null 2>&1 ); then
  echo "PASS: scenario 2 legacy_systemd (skip)"; PASS=$((PASS+1))
else
  echo "FAIL: scenario 2 legacy_systemd"; FAIL=$((FAIL+1))
fi

# Scenario 3: none → PASS (skip)
if ( cd "$FIXT/none" && bash "$SCRIPT" >/dev/null 2>&1 ); then
  echo "PASS: scenario 3 none (skip)"; PASS=$((PASS+1))
else
  echo "FAIL: scenario 3 none"; FAIL=$((FAIL+1))
fi

# Scenario 4 (negative): docker_first 인데 Dockerfile 부재 → exit 1
TMP1=$(mktemp -d)
mkdir -p "$TMP1/.claude/_overlay"
cp "$FIXT/docker_first/.claude/_overlay/project.yaml" "$TMP1/.claude/_overlay/"
# compose.yml 만 복사 (Dockerfile 누락)
cp "$FIXT/docker_first/compose.yml" "$TMP1/" 2>/dev/null || true
if ( cd "$TMP1" && bash "$SCRIPT" >/dev/null 2>&1 ); then
  echo "FAIL: scenario 4 negative-Dockerfile (should exit 1 but passed)"; FAIL=$((FAIL+1))
else
  echo "PASS: scenario 4 negative-Dockerfile (correctly exit 1)"; PASS=$((PASS+1))
fi
rm -rf "$TMP1"

# Scenario 5 (negative): docker_first 인데 compose 부재 → exit 1
TMP2=$(mktemp -d)
mkdir -p "$TMP2/.claude/_overlay"
cp "$FIXT/docker_first/.claude/_overlay/project.yaml" "$TMP2/.claude/_overlay/"
cp "$FIXT/docker_first/Dockerfile" "$TMP2/" 2>/dev/null || true
# compose.yml 미복사
if ( cd "$TMP2" && bash "$SCRIPT" >/dev/null 2>&1 ); then
  echo "FAIL: scenario 5 negative-compose (should exit 1 but passed)"; FAIL=$((FAIL+1))
else
  echo "PASS: scenario 5 negative-compose (correctly exit 1)"; PASS=$((PASS+1))
fi
rm -rf "$TMP2"

echo "---"
echo "PASS: $PASS / FAIL: $FAIL"
[ "$FAIL" -eq 0 ] || exit 1
echo "ALL PASS"
