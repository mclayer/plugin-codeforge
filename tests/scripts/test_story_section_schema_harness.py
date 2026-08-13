"""
Harness for T3 (test_check_story_section_schema.py) validation.

AC-8: Thin entry layer to satisfy Hop3 symbol existence requirement.
Runs T3 once per module and caches result.
Validates two orthogonal axes:
  - Axis A (outcome): failed==0 ∧ errors==0 ∧ skipped==0
  - Axis B (completeness): collected == N (N = AST test def count)

Change Plan §3.5 / §8.1 RTM normative.
"""

import subprocess
import ast
import re
from pathlib import Path
from typing import Optional, Dict


class TestStorySchemaHarness:
    """
    Runs T3 subprocess via pytest and validates outcome against spec.
    Module-level caching: single T3 execution per test session.
    """

    # Module-level cache
    _cached_result: Optional[Dict] = None
    _expected_test_count: int = 0
    _t3_path: Path = None

    @classmethod
    def setup_class(cls):
        """
        Setup: Compute N via AST, run T3 once, cache result.
        """
        # Locate T3 from spec blob: scripts/lib/test_check_story_section_schema.py
        cls._t3_path = Path(__file__).resolve().parent.parent.parent / "scripts/lib/test_check_story_section_schema.py"

        if not cls._t3_path.exists():
            raise FileNotFoundError(f"T3 not found: {cls._t3_path}")

        # Count test defs via AST (N)
        with open(cls._t3_path, encoding='utf-8') as f:
            tree = ast.parse(f.read())
        test_nodes = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')
        ]
        cls._expected_test_count = len(test_nodes)

        # Run T3 via pytest subprocess (once per session)
        result = subprocess.run(
            ['python', '-m', 'pytest', str(cls._t3_path),
             '-q', '--tb=no', '-p', 'no:cacheprovider'],
            capture_output=True,
            text=True,
            cwd=Path(__file__).resolve().parent.parent.parent
        )

        # Cache: parse pytest -q output
        cls._cached_result = cls._parse_pytest_output(result.stdout, result.stderr, result.returncode)

    @staticmethod
    def _parse_pytest_output(stdout: str, stderr: str, returncode: int) -> Dict:
        """
        Parse pytest -q output to extract: passed, failed, error, skipped, collected.

        Format examples:
          - "21 passed in 76.10s (0:01:16)"
          - "14 failed, 3 passed, 4 errors in 91.60s (0:01:31)"
          - "5 passed, 5 skipped in 1.23s"

        Returns dict: {'passed': int, 'failed': int, 'error': int, 'skipped': int, 'collected': int, 'exit': int}
        """
        result = {
            'passed': 0,
            'failed': 0,
            'error': 0,
            'skipped': 0,
            'collected': None,
            'exit': returncode,
            'stdout': stdout,
            'stderr': stderr
        }

        # Combine output (pytest may write to either)
        combined = stdout + stderr

        # Pattern 1: "N passed" or "N failed" or "N error" or "N skipped"
        for match in re.finditer(r'(\d+)\s+(passed|failed|error|skipped)', combined):
            count_str, category = match.groups()
            count = int(count_str)
            if category == 'error':
                category = 'error'
            result[category] = count

        # Pattern 2: pytest --collect-only shows "collected N items"
        # But with -q we get from output. Try to infer from "N passed/failed/error/skipped"
        # If we have outcome, sum = collected (approximately)
        total_outcome = result['passed'] + result['failed'] + result['error'] + result['skipped']
        if total_outcome > 0:
            result['collected'] = total_outcome

        # Try direct pattern for "collected"
        collected_match = re.search(r'collected (\d+) item', combined)
        if collected_match:
            result['collected'] = int(collected_match.group(1))

        return result

    def test_t3_outcome_axis_no_failure_error_skip(self):
        """
        AC-8 Axis A: Outcome is all-pass.

        Spec: failed==0 ∧ errors==0 ∧ skipped==0

        Kills: partial failures, incomplete runs, skip-only runs.
        Orthogonal to Axis B (does not care about collection count, only outcome).
        """
        result = self._cached_result

        assert result['failed'] == 0, (
            f"T3 suite has {result['failed']} failed tests; "
            f"full output:\n{result['stdout']}\n{result['stderr']}"
        )
        assert result['error'] == 0, (
            f"T3 suite has {result['error']} errors; "
            f"full output:\n{result['stdout']}\n{result['stderr']}"
        )
        assert result['skipped'] == 0, (
            f"T3 suite has {result['skipped']} skipped tests; "
            f"full output:\n{result['stdout']}\n{result['stderr']}"
        )

    def test_t3_collection_axis_equals_ast_count(self):
        """
        AC-8 Axis B: Collection completeness.

        Spec: collected == N where N = AST(T3) test def count.

        Kills: under-collection, early termination, direct-python runner pitfall (exit 0 on partial run).
        Orthogonal to Axis A (tests may be collected but not all passing).

        Change Plan §8.1.1 proves axes are disjoint:
          - A does not catch under-collection (5 collected all pass → Axis A PASS, Axis B FAIL)
          - B does not catch outcome failures (21 collected, 3 fail → Axis A FAIL, Axis B PASS)
        """
        result = self._cached_result
        n = self._expected_test_count

        assert result['collected'] is not None, (
            f"Could not parse collection count from pytest output; "
            f"stdout:\n{result['stdout']}\nstderr:\n{result['stderr']}"
        )
        assert result['collected'] == n, (
            f"T3 collected {result['collected']} tests, expected {n} (AST count); "
            f"output:\n{result['stdout']}\n{result['stderr']}"
        )
