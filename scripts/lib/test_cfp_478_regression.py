#!/usr/bin/env python3
# test_cfp_478_regression.py — CFP-478 Phase 2 regression test runner
# ADR-061 §결정 1 + Amendment 1 §결정 6.A — 20 candidate migration verification (CFP-722 Phase 2 +1).
#
# 검사: 각 scripts/*.sh thin wrapper 가 대응하는 scripts/lib/*.py 를 정상 호출하는지 확인.
# 검사 항목:
#   1. shell wrapper 파일 존재 + python heredoc 부재 (heredoc 완전 제거 확인)
#   2. scripts/lib/*.py SSOT 파일 존재
#   3. wrapper 본문에 `scripts/lib/<name>.py` 참조 포함
#   4. fixtures/ 하위 입력/출력 파일 존재 (있는 경우)
#
# Usage:  python3 scripts/lib/test_cfp_478_regression.py [--verbose]
# Exit:   0=all pass, 1=any fail
import pathlib
import sys
import re

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent

# 20 candidates: (shell_wrapper_name, lib_py_name)
CANDIDATES = [
    ("check-doc-section-schema.sh",            "check_doc_section_schema.py"),
    ("check-doc-locations.sh",                  "check_doc_locations.py"),
    ("check-decision-principle-vocabulary.sh",  "check_decision_principle_vocabulary.py"),
    ("check-evidence-registry-naming.sh",       "check_evidence_registry_naming.py"),
    ("check-carrier-bootstrap.sh",              "check_carrier_bootstrap.py"),
    ("check-domain-knowledge-schema.sh",        "check_domain_knowledge_schema.py"),
    ("check-adr-sunset-criteria.sh",            "check_adr_sunset_criteria.py"),
    ("check-workflow-yaml.sh",                  "check_workflow_yaml.py"),
    ("check-inter-plugin-contracts.sh",         "check_inter_plugin_contracts.py"),
    ("check-story-section-schema.sh",           "check_story_section_schema.py"),
    ("check-label-registry.sh",                 "check_label_registry.py"),
    ("check-story-section-9-typed.sh",          "check_story_section_9_typed.py"),
    ("check-doc-frontmatter.sh",                "check_doc_frontmatter.py"),
    ("check-comment-prefix.sh",                 "check_comment_prefix.py"),
    ("sync-contract-bump.sh",                   "sync_contract_bump.py"),
    ("audit-trail-fetch.sh",                    "audit_trail_pii_redact.py"),
    ("test-check-inter-plugin-drift.sh",        "test_check_inter_plugin_drift.py"),
    ("test-cfp-140-ghec-governance.sh",         "test_cfp_140_ghec_governance.py"),
    ("sync-required-workflows.sh",              "sync_required_workflows.py"),
    # CFP-722 Phase 2 — 20번째 entry (pure thin-wrapper, NOT HYBRID)
    ("check-story-section-ownership.sh",        "check_story_section_ownership.py"),
]

# Wrappers that retain non-trivial bash logic (not full thin-wrapper pattern)
# These have Python heredocs REPLACED but are NOT pure thin wrappers themselves.
HYBRID_WRAPPERS = {
    "sync-contract-bump.sh",
    "audit-trail-fetch.sh",
    "test-check-inter-plugin-drift.sh",
    "test-cfp-140-ghec-governance.sh",
    "sync-required-workflows.sh",
}

# Multi-line heredoc patterns that must NOT appear in migrated wrappers
HEREDOC_PATTERNS = [
    re.compile(r"python3\s+-\s+<<", re.MULTILINE),   # python3 - <<'PY' / <<'EOF'
    re.compile(r"python3\s+<<\w+", re.MULTILINE),      # python3 <<PYEOF
    re.compile(r"<<\s*'PY'\s*\n.*?\nPY", re.DOTALL),   # heredoc body
    re.compile(r"<<\s*PYEOF\s*\n.*?\nPYEOF", re.DOTALL),
]


def check_candidate(sh_name: str, py_name: str, verbose: bool) -> list[str]:
    failures: list[str] = []
    sh_path = REPO_ROOT / "scripts" / sh_name
    py_path = REPO_ROOT / "scripts" / "lib" / py_name

    # 1. Shell wrapper exists
    if not sh_path.exists():
        failures.append(f"[MISSING shell] {sh_path}")
        return failures

    # 2. Python lib file exists
    if not py_path.exists():
        failures.append(f"[MISSING lib] {py_path}")

    # 3. Wrapper references lib file
    sh_text = sh_path.read_text(encoding="utf-8", errors="replace")
    lib_ref = f"scripts/lib/{py_name}"
    alt_ref = f"lib/{py_name}"  # relative reference in exec calls
    if lib_ref not in sh_text and alt_ref not in sh_text:
        failures.append(f"[NO LIB REF] {sh_name} does not reference {py_name}")

    # 4. Heredoc check (only for non-hybrid wrappers — hybrid ones may have other inline python3 -c)
    if sh_name not in HYBRID_WRAPPERS:
        for pat in HEREDOC_PATTERNS:
            if pat.search(sh_text):
                failures.append(
                    f"[HEREDOC FOUND] {sh_name} still contains multi-line Python heredoc"
                )
                break
    else:
        # Hybrid: just verify the specific lib reference that was migrated is present
        if verbose:
            print(f"  [hybrid] {sh_name}: lib ref check only (bash logic retained)")

    # 5. Fixture dir (if exists)
    fixture_dir = REPO_ROOT / "tests" / "fixtures" / "cfp-478" / sh_name.replace(".sh", "")
    if fixture_dir.exists():
        # Check that it has at least one input file
        inputs = list(fixture_dir.glob("input*")) + list(fixture_dir.glob("*.input.*"))
        if not inputs:
            if verbose:
                print(f"  [warn] {sh_name}: fixture dir exists but no input files")

    return failures


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    verbose = "--verbose" in argv or "-v" in argv

    total = 0
    passed = 0
    all_failures: list[str] = []

    for sh_name, py_name in CANDIDATES:
        total += 1
        failures = check_candidate(sh_name, py_name, verbose)
        if failures:
            for f in failures:
                print(f"FAIL [{sh_name}]: {f}")
            all_failures.extend(failures)
        else:
            passed += 1
            if verbose:
                print(f"PASS [{sh_name}]")

    print(f"\nCFP-478 regression: {passed}/{total} candidates PASS", end="")
    if all_failures:
        print(f", {len(all_failures)} failure(s)")
        return 1
    print(" -- all OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
