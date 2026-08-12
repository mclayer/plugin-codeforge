#!/usr/bin/env bash
# CFP-2944 / ADR-025 Amendment 4 §A4-2 — illegal-stop form-set parity 검사 (fence ↔ 4 전파면)
# ADR-061 §결정 1 — thin wrapper (scripts/lib/check_form_set_parity.py SSOT)
#
# 검사: ADR-025 §결정 7 form-set fence 가 등재한 named form id 집합이
#       §결정 7 표 · hook priming TEXT 2채널 · docs/consumer-guide.md §7.1 mirror 4면과 일치하는지
#       (방향 ① 누락 / 방향 ② 초과) + 행 단위 구조 요건(D2) · negative-control presence(D3).
# tier: [정적] (관측 tier — merge 무차단). 근거·정직 천장 상세:
#       scripts/lib/check_form_set_parity.py header.
# Usage / exit code / semantics 상세: scripts/lib/check_form_set_parity.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_form_set_parity.py" "$@"
