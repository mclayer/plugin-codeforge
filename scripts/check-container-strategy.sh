#!/usr/bin/env bash
# CFP-128 / ADR-033 — Docker-first Infra Engineering lint
#
# Validate: project.yaml `infra_strategy: docker_first` consumer 의 Dockerfile + compose.yml 존재
#   - docker_first → Dockerfile + (compose.yml | docker-compose.yml) 둘 다 존재 의무 → exit 0
#   - legacy_systemd → skip (legacy fallback OK)
#   - none → skip (library / config-only repo)
#   - infra_strategy 미명시 → default = docker_first 적용
#
# Story KEY: CFP-128 (sibling sync 후 codeforge-develop / design / review 도 적용)
# Test wrapper: scripts/test-check-container-strategy.sh (5 시나리오 TDD)

set -euo pipefail

PROJECT_YAML=".claude/_overlay/project.yaml"

# overlay 부재 시 skip — wrapper repo / non-consumer dir 사용 안전
if [ ! -f "$PROJECT_YAML" ]; then
  echo "[check-container-strategy] no overlay project.yaml — skip"
  exit 0
fi

# infra_strategy 추출 (yaml grep, default docker_first)
STRATEGY=$(grep -E '^infra_strategy:' "$PROJECT_YAML" | head -1 | awk '{print $2}' | tr -d '"' | tr -d "'" || echo "")
STRATEGY="${STRATEGY:-docker_first}"

case "$STRATEGY" in
  docker_first)
    if [ ! -f "Dockerfile" ]; then
      echo "[check-container-strategy] FAIL: Dockerfile missing under infra_strategy=docker_first"
      echo "  → resolve: (a) Dockerfile 작성, (b) infra_strategy: legacy_systemd | none 명시 override"
      exit 1
    fi
    # compose.yml 또는 docker-compose.yml 양쪽 accept (Codex P1-3 duality coverage)
    if [ ! -f "compose.yml" ] && [ ! -f "docker-compose.yml" ]; then
      echo "[check-container-strategy] FAIL: compose.yml (또는 docker-compose.yml) missing under infra_strategy=docker_first"
      echo "  → resolve: (a) compose.yml 작성, (b) infra_strategy override"
      exit 1
    fi
    echo "[check-container-strategy] PASS: docker_first artifacts present"
    ;;
  legacy_systemd|none)
    echo "[check-container-strategy] SKIP: infra_strategy=$STRATEGY"
    ;;
  *)
    echo "[check-container-strategy] FAIL: unknown infra_strategy=$STRATEGY"
    echo "  → valid values: docker_first | legacy_systemd | none"
    exit 1
    ;;
esac
