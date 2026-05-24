#!/usr/bin/env bash
# check-living-architecture-update.sh — Living Architecture per-Epic mandatory update gate lint
#
# Carrier: CFP-1429 (Sub-C S3.5 of EPIC #1415 Mega-Epic) — ADR-112 mechanical_enforcement_actions wire
# Owner ADR: ADR-112 §결정 1 (per-Epic mandatory update gate) + §결정 2 (closed-binary: 5-anchor update OR no-op explicit declare)
# Wire layer: ADR-082 §결정 6 retain pattern 답습 (Wave 1 declare = ADR-112 mechanical_enforcement_actions / Wave 2 wire = 본 script)
# Tier: warning (ADR-060 §결정 5 — 첫 도입 = warning mode)
# Bypass label: hotfix-bypass:living-architecture-update (label-registry-v2 84th family member)
#
# CFP-478 / ADR-061 §결정 1 + §결정 6.A — thin wrapper (scripts/lib/check_living_architecture_update.py SSOT)
# CFP-1408 — always cd to repo root (msys2 absolute POSIX→Windows path conversion 회피, relative path 전달)
# CFP-1369/CFP-1398 — ASCII status indicators ([OK] / [WARN]) terminal Windows console 호환
# CFP-1421 — GH_TOKEN env passthrough to gh CLI
#
# Modes:
#   default — PR-mode: detect touched files via `gh pr view --json files` + PR/commit body
#             grep for `[living-arch-no-impact: <rationale>]` marker; warn if neither present
#   --pr N  — explicit PR number
#   --file PATH — body file (offline self-test)
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier = 항상 exit 0, PR merge 미차단)
#   2 — setup error (gh 미설치 등)
#
# Usage / 상세 semantics: scripts/lib/check_living_architecture_update.py header.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."   # CFP-1408 — always cd (msys2 absolute POSIX→Windows path conversion 회피)
exec python3 "scripts/lib/check_living_architecture_update.py" "$@"
