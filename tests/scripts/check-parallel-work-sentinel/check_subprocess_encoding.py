"""
tests/scripts/check-parallel-work-sentinel/check_subprocess_encoding.py
CFP-1540 — TC-9 Part B helper: AST-verify 3-kwarg combo at all subprocess.run text=True sites.

Usage: python3 check_subprocess_encoding.py <impl_file_path>
Exit 0: PASS (all text=True calls have encoding+errors kwargs)
Exit 1: FAIL (missing 3-kwarg at 1+ sites)
"""
import ast
import sys


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: check_subprocess_encoding.py <impl_file_path>", file=sys.stderr)
        sys.exit(2)

    impl_path = sys.argv[1]
    with open(impl_path, "r", encoding="utf-8") as f:
        src = f.read()

    tree = ast.parse(src)
    errors = 0
    total_text_calls = 0

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        is_subprocess_run = (
            isinstance(func, ast.Attribute)
            and func.attr == "run"
            and isinstance(func.value, ast.Name)
            and func.value.id == "subprocess"
        )
        if not is_subprocess_run:
            continue
        has_text = any(kw.arg == "text" for kw in node.keywords)
        if not has_text:
            continue
        total_text_calls += 1
        has_encoding = any(kw.arg == "encoding" for kw in node.keywords)
        has_errors = any(kw.arg == "errors" for kw in node.keywords)
        if not (has_encoding and has_errors):
            errors += 1
            print(
                f"MISSING 3-kwarg at line {node.lineno}: "
                f"encoding={has_encoding} errors={has_errors}",
                file=sys.stderr,
            )

    if errors > 0:
        print(
            f"FAIL: {errors}/{total_text_calls} subprocess.run text=True calls "
            "missing encoding+errors kwargs"
        )
        sys.exit(1)

    print(f"PASS: all {total_text_calls} subprocess.run text=True calls have 3-kwarg combo")
    sys.exit(0)


if __name__ == "__main__":
    main()
