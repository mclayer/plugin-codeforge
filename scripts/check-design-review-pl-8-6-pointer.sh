#!/usr/bin/env bash
# CFP-1089 — DesignReviewPL §8.6 pointer-presence-check lint (3-check)
#
# Trigger: PR open / push 시 docs/inter-plugin-contracts/review-verdict-v4.md 또는
#          codeforge-review canonical templates/review-pl-base.md 변경 detect 시
#
# 3-check:
#   1. findings[].type "audit-gate-pointer-missing" literal 영역 review-verdict-v4 v4.7+ enum 영역 존재
#   2. audit_gate_pointer_self_check_passed verdict-level boolean field schema 정합 (v4.7+)
#   3. ADR-068 Amendment 3 §결정 1 I-6 invariant cross-ref 정합 (ADR-068 frontmatter amendments[3])
#
# Cross-ref:
#   ADR-068 Amendment 3 — I-6 audit-gate-pointer-existence invariant (CFP-1087)
#   ADR-060 — evidence-enforceable framework (warning tier)
#   ADR-061 — Python script convention (thin bash wrapper + scripts/lib/*.py SSOT)
#
# Tier: warning (default), blocking-on-pr 승격 path = sibling Story (ADR-060 §결정 7 AND condition)
#
# Bypass: hotfix-bypass:design-review-pl-8-6-pointer label (audit-trailed)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Delegate to Python SSOT (ADR-061 §결정 1)
PYTHON_SSOT="${SCRIPT_DIR}/lib/check_design_review_pl_8_6_pointer.py"

if [[ ! -f "${PYTHON_SSOT}" ]]; then
    echo "❌ Python SSOT 영역 부재: ${PYTHON_SSOT}" >&2
    exit 2
fi

exec python "${PYTHON_SSOT}" "$@"
