"""CFP-1089 — DesignReviewPL §8.6 pointer-presence-check lint Python SSOT.

3-check (warning tier per ADR-060):
1. findings[].type "audit-gate-pointer-missing" literal review-verdict-v4 v4.7+ enum 정합
2. audit_gate_pointer_self_check_passed verdict-level boolean field schema 정합
3. ADR-068 Amendment 3 §결정 1 I-6 invariant cross-ref 정합 (frontmatter amendments[3])

Exit codes (ADR-060 §결정 15 3-tier):
- 0: PASS (3-check OK)
- 1: WARNING (1+ check 영역 부재 또는 cross-ref drift, warning tier non-blocking)
- 2: META-ERROR (file 부재, parse 실패 — fail-loud)

Cross-ref:
- ADR-068 Amendment 3 §결정 6 표 4번째 row: audit-gate-pointer-existence-check (deferred-followup)
- ADR-060 §결정 7 promotion gate AND condition (PR ≥ 20 + bypass-외-failure = 0 + sibling Story merged)
"""

import os
import re
import sys
from pathlib import Path

# Force UTF-8 stdout for Windows cp949 compatibility
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")


def find_repo_root() -> Path:
    """Find repo root via .git directory walk-up."""
    p = Path(__file__).resolve()
    for parent in [p, *p.parents]:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("repo root (.git) not found")


def check_1_findings_type_enum_literal(repo_root: Path) -> tuple[bool, str]:
    """Check 1: findings[].type "audit-gate-pointer-missing" literal review-verdict-v4 v4.7+ enum 정합."""
    rv_path = repo_root / "docs" / "inter-plugin-contracts" / "review-verdict-v4.md"
    if not rv_path.exists():
        return (False, f"review-verdict-v4.md not found: {rv_path}")

    content = rv_path.read_text(encoding="utf-8")
    # contract_version verify
    cv_match = re.search(r'^contract_version:\s*"([0-9.]+)"', content, re.MULTILINE)
    if not cv_match:
        return (False, "contract_version field not found")
    version = cv_match.group(1)
    if version < "4.7":
        return (False, f"contract_version {version} < 4.7 — audit-gate-pointer-missing literal 영역 부재")

    # Enum literal presence
    if '"audit-gate-pointer-missing"' not in content:
        return (False, 'findings[].type enum literal "audit-gate-pointer-missing" 부재')

    return (True, f"v{version} + audit-gate-pointer-missing literal OK")


def check_2_verdict_field_schema(repo_root: Path) -> tuple[bool, str]:
    """Check 2: audit_gate_pointer_self_check_passed verdict-level boolean field schema 정합."""
    rv_path = repo_root / "docs" / "inter-plugin-contracts" / "review-verdict-v4.md"
    if not rv_path.exists():
        return (False, f"review-verdict-v4.md not found: {rv_path}")

    content = rv_path.read_text(encoding="utf-8")
    if "audit_gate_pointer_self_check_passed" not in content:
        return (False, "audit_gate_pointer_self_check_passed field schema 부재")
    # ADR-068 Amendment 3 cross-ref verify
    if "ADR-068 Amendment 3" not in content:
        return (False, "ADR-068 Amendment 3 cross-ref 부재")
    return (True, "audit_gate_pointer_self_check_passed field + ADR-068 Amendment 3 cross-ref OK")


def check_3_adr_068_amendment_3_cross_ref(repo_root: Path) -> tuple[bool, str]:
    """Check 3: ADR-068 Amendment 3 §결정 1 I-6 invariant cross-ref 정합."""
    adr_path = repo_root / "docs" / "adr" / "ADR-068-boundary-completeness-invariants.md"
    if not adr_path.exists():
        return (False, f"ADR-068 not found: {adr_path}")

    content = adr_path.read_text(encoding="utf-8")
    # frontmatter amendments[3] verify
    if "amendment_id: 3" not in content:
        return (False, "ADR-068 frontmatter amendments[3] (amendment_id: 3) 부재")
    if "CFP-1087" not in content:
        return (False, "ADR-068 Amendment 3 CFP-1087 reference 부재")
    if "I-6" not in content:
        return (False, "ADR-068 I-6 invariant declaration 부재")
    if "audit-gate-pointer-existence" not in content:
        return (False, "ADR-068 §결정 1 I-6 audit-gate-pointer-existence invariant declaration 부재")
    return (True, "ADR-068 Amendment 3 + I-6 declaration + CFP-1087 cross-ref OK")


def main() -> int:
    try:
        repo_root = find_repo_root()
    except RuntimeError as e:
        print(f"❌ META-ERROR: {e}", file=sys.stderr)
        return 2

    print(f"🔍 CFP-1089 DesignReviewPL §8.6 pointer-presence-check (repo: {repo_root.name})")
    print()

    checks = [
        ("Check 1 — findings[].type audit-gate-pointer-missing enum literal", check_1_findings_type_enum_literal),
        ("Check 2 — audit_gate_pointer_self_check_passed verdict field schema", check_2_verdict_field_schema),
        ("Check 3 — ADR-068 Amendment 3 + I-6 invariant cross-ref", check_3_adr_068_amendment_3_cross_ref),
    ]

    warnings = []
    for name, check_fn in checks:
        try:
            ok, msg = check_fn(repo_root)
            status = "✅ PASS" if ok else "⚠️  WARN"
            print(f"  {status}: {name}")
            print(f"          {msg}")
            if not ok:
                warnings.append(name)
        except Exception as e:
            print(f"  ❌ META-ERROR: {name}", file=sys.stderr)
            print(f"          {e}", file=sys.stderr)
            return 2

    print()
    if warnings:
        print(f"⚠️  WARNING tier — {len(warnings)} check 영역 미통과 (non-blocking)")
        print("   Bypass: hotfix-bypass:design-review-pl-8-6-pointer label (audit-trailed)")
        return 1
    print("✅ All 3 checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
