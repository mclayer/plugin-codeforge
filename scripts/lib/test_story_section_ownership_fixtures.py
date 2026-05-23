#!/usr/bin/env python3
"""
CFP-722 fixture-based test runner for check_story_section_ownership.py
Tests the classify() pure function against fixture input/expected pairs.
Usage: python3 scripts/lib/test_story_section_ownership_fixtures.py [--verbose]
Exit:  0=all pass, 1=any fail
"""
import sys, json, pathlib
import sys

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Allow import from same directory
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from check_story_section_ownership import classify, parse_frontmatter, drift_warning_line

FIXTURE_ROOT = pathlib.Path(__file__).parent.parent.parent / "tests/fixtures/cfp-722/check-story-section-ownership"
VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv


def load_fixture(case_dir: pathlib.Path):
    base = (case_dir / "input/base.md").read_text(encoding="utf-8")
    head = (case_dir / "input/head.md").read_text(encoding="utf-8")
    ctx = json.loads((case_dir / "input/context.json").read_text(encoding="utf-8"))
    expected_stdout = (case_dir / "expected/stdout.txt").read_text(encoding="utf-8").strip()
    expected_exit = (case_dir / "expected/exit-code.txt").read_text(encoding="utf-8").strip()
    return base, head, ctx, expected_stdout, expected_exit


def run_classify(base_text, head_text, ctx):
    """Run classify() and format output like the script would."""
    branch = ctx.get("pr_branch", "")
    labels = ctx.get("pr_labels", [])
    fm = parse_frontmatter(head_text)
    violations, carrier_exempt, drift_warnings = classify(
        base_text, head_text, branch, labels, fm)
    lines = []
    if carrier_exempt:
        story_key = fm.get("key", "unknown")
        from check_story_section_ownership import EXEMPT_PROTOCOL_ID
        lines.append(
            f"notice carrier-exempt: {story_key} declares bootstrap_exempt_protocols "
            f"including {EXEMPT_PROTOCOL_ID} — ownership checks bypassed"
        )
    # EC-1 LOUD heading-drift warnings (Story §7.6 + Change Plan §13.B mandate)
    for sec_num in drift_warnings:
        lines.append(drift_warning_line(sec_num))
    for v in violations:
        lines.append(v.to_warning_line())
    return "\n".join(lines), "0"  # always exit 0 (warning tier)


def main():
    if not FIXTURE_ROOT.exists():
        print(f"FAIL: fixture root not found: {FIXTURE_ROOT}")
        return 1

    cases = sorted(FIXTURE_ROOT.iterdir())
    total = passed = 0
    failures = []

    for case_dir in cases:
        if not case_dir.is_dir():
            continue
        case_name = case_dir.name
        total += 1
        try:
            base, head, ctx, expected_stdout, expected_exit = load_fixture(case_dir)
        except Exception as e:
            failures.append(f"[{case_name}] LOAD ERROR: {e}")
            continue

        actual_stdout, actual_exit = run_classify(base, head, ctx)
        expected_stdout_stripped = expected_stdout.strip()
        actual_stdout_stripped = actual_stdout.strip()

        ok = True
        if actual_exit != expected_exit:
            failures.append(f"[{case_name}] exit-code mismatch: got={actual_exit!r} expected={expected_exit!r}")
            ok = False

        # For cases with expected violations, check each expected line is present
        if expected_stdout_stripped:
            expected_lines = set(expected_stdout_stripped.splitlines())
            actual_lines = set(actual_stdout_stripped.splitlines())
            missing = expected_lines - actual_lines
            unexpected = actual_lines - expected_lines
            if missing:
                failures.append(f"[{case_name}] missing expected output lines:\n  " + "\n  ".join(missing))
                ok = False
            if unexpected:
                failures.append(f"[{case_name}] unexpected output lines:\n  " + "\n  ".join(unexpected))
                ok = False
        else:
            # Expected empty stdout — actual should have no violation/notice lines
            violation_lines = [l for l in actual_stdout_stripped.splitlines()
                               if l.startswith("warning violation:") or l.startswith("notice carrier-exempt:")]
            if violation_lines:
                failures.append(f"[{case_name}] expected no violations but got:\n  " + "\n  ".join(violation_lines))
                ok = False

        if ok:
            passed += 1
            if VERBOSE:
                print(f"PASS [{case_name}]")
        else:
            if VERBOSE:
                print(f"FAIL [{case_name}]")

    print(f"\nCFP-722 fixture tests: {passed}/{total} PASS", end="")
    if failures:
        print(f", {len(failures)} failure(s):")
        for f in failures:
            print(f"  {f}")
        return 1
    print(" -- all OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
