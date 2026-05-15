#!/usr/bin/env bash
# CFP-27 Phase 0b — 도입 (warning 모드)
# CFP-28 Phase 0c — strict 전환 (exit=1 on warnings)
# CFP-32 (ζ arc F1) — docs/inter-plugin-contracts/ 신규 path 추가
# CFP-46 PR-G — §7.4 운영 리스크 schema (5 항목) + CONDITIONAL N/A 사유 (10자 minimum) 강제
# CFP-47 PR-G — §8.5 Stateful / restart invariant tests applicability lint (30자 minimum)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — thin wrapper (scripts/lib/check_doc_section_schema.py SSOT)
# 검사: 5 owner doc path 의 본문 필수 섹션 헤딩
# Usage / exit code / semantics 상세: scripts/lib/check_doc_section_schema.py header.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ "$#" -eq 0 ] && cd "$SCRIPT_DIR/.."
exec python3 "$SCRIPT_DIR/lib/check_doc_section_schema.py" "$@"
