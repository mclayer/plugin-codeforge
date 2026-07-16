#!/usr/bin/env bash
# scripts/check-infra-resource-drift.sh — infra-resource manifest drift scan (D3) + 역색인(D4) thin wrapper
#
# CFP-2700 (Epic) G2 / ADR-157 §결정3(D3) + §결정6(D4) — manifest(.claude/_overlay/project.yaml
#   infra_resources:)가 선언한 인프라 자원(canonical_env + alias)과 실 참조면(workflow secrets. /
#   project.yaml _env: / scripts 정적 리터럴)을 대조해 미선언 표면(drift 원천)·orphan(dead 선언)을
#   census-floor oracle 로 검출. census 3-count(candidates/inert/undeclared) + verdict warning-tier /
#   census fail-closed 비대칭 + grandfather baseline + none-disguise anti-hollow + born-safe.
#   ADR-119 게이트=ground-truth 정합. base scan 한정(cross-repo=G5 / startup=G3 정의역 밖).
# ADR-061 §결정 1: Python entry-point + thin bash wrapper (python3 exec forward, 로직 0).
#
# Usage / exit code / semantics 상세: scripts/lib/check_infra_resource_drift.py header.
#   bash scripts/check-infra-resource-drift.sh [--repo-root DIR] [--manifest PATH] [--baseline PATH]
#     [--promote-orphan] [--write-baseline] [--allow-baseline-growth --reason TEXT] [--emit-reverse-index]
#     0 = PASS (new undeclared 0) / 1 = FLAG (undeclared / none-disguise / orphan+promote — warning;
#         + --write-baseline monotonic shrink 위반 거부) / 2 = usage·manifest 오류
#     / 3 = fail-closed: census born-hollow (candidates==0 ∧ inert==0) 또는 baseline substrate-failure
#         (content_digest 불일치·필드부재 = 손상 baseline).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-infra-resource-drift-infra-error] check-infra-resource-drift: python3 not installed" >&2
  exit 2
}

exec python3 "$SCRIPT_DIR/lib/check_infra_resource_drift.py" "$@"
