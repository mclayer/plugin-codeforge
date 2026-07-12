#!/usr/bin/env bash
# scripts/check-resource-safety-claim-proof.sh — resource-safety claim ↔ proof-link presence lint thin wrapper
#
# CFP-2646 / ADR-082 Amendment 38 §결정 16 — governance/보안 tooling(evidence-check 게이트·보안 script·
#   워크플로 YAML)의 docstring·inline 주석·워크플로 YAML 주석에 resource-safety/복잡도/DoS-guard 안전성-claim
#   을 쓸 때 paired proof-reference OR honest-ceiling 문구 presence 를 정적 검사한다. presence ≠ truth
#   (honesty ceiling ADR-151 §결정7 상속) — claim 의 참됨은 강제하지 않음. warning tier (PR merge 무차단).
# ADR-061 §결정 1: Python entry-point + thin bash wrapper (python3 exec forward, 로직 0).
#
# Usage / exit code / semantics 상세: scripts/lib/check_resource_safety_claim_proof.py header.
#   bash scripts/check-resource-safety-claim-proof.sh [--repo-root DIR] [--baseline PATH]
#   bash scripts/check-resource-safety-claim-proof.sh --repo-root DIR --files F1 F2 ...   # AC-3 self-application
#   bash scripts/check-resource-safety-claim-proof.sh --repo-root DIR --write-baseline    # grandfather 동결
#     0 = PASS (new-over-claim 0 또는 대상 부재 no-op) / 1 = FLAG 1+ (warning) / 2 = usage error.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

command -v python3 >/dev/null 2>&1 || {
  echo "[codeforge-resource-safety-claim-proof-infra-error] check-resource-safety-claim-proof: python3 not installed" >&2
  exit 2
}

exec python3 "$SCRIPT_DIR/lib/check_resource_safety_claim_proof.py" "$@"
