"""
Harness for T3 (test_check_story_section_schema.py) validation.

AC-8: Thin entry layer to satisfy Hop3 symbol existence requirement.
Runs T3 once per module and caches the result.
Validates two orthogonal axes:
  - Axis A (outcome):      failed==0 ∧ errors==0 ∧ skipped==0
  - Axis B (completeness): collected == N (N = AST test def count)

Change Plan §3.5 / §8.1 RTM normative.

★ oracle = **junit XML** (not `-q` text regex).
  RTM AC-8 심볼이 걸리는 곳이므로 강건한 oracle 에 배선한다 — 텍스트 정규식은
  pytest 출력 포맷 변화에 깨지고, 깨지면 카운트가 조용히 0 이 되어
  축 A(`failed==0`)가 **공허하게 통과**한다. T3-CI workflow step 과 동일 oracle.
"""

import ast
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Dict


class TestStorySchemaHarness:
    """Runs T3 via pytest subprocess and validates outcome against spec."""

    _cached_result: Optional[Dict] = None
    _expected_test_count: int = 0
    _t3_path: Path = None

    @classmethod
    def setup_class(cls):
        """Compute N via AST, run T3 once, cache the junit-parsed result."""
        repo_root = Path(__file__).resolve().parent.parent.parent
        cls._t3_path = repo_root / "scripts/lib/test_check_story_section_schema.py"

        if not cls._t3_path.exists():
            raise FileNotFoundError(f"T3 not found: {cls._t3_path}")

        # N 은 상수 금지 — AST 산출 (CP §8.1). workflow(:66-70) 와 동일 산출식.
        with open(cls._t3_path, encoding='utf-8') as fh:
            tree = ast.parse(fh.read())
        cls._expected_test_count = sum(
            1 for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith('test')
        )

        # ★ sys.executable — 'python' 문자열은 러너와 다른 인터프리터를 잡을 수 있다.
        with tempfile.TemporaryDirectory() as td:
            junit = Path(td) / "t3-results.xml"
            proc = subprocess.run(
                [sys.executable, '-m', 'pytest', str(cls._t3_path),
                 '-q', '--tb=no', '-p', 'no:cacheprovider',
                 f'--junitxml={junit}'],
                capture_output=True, text=True,
                encoding='utf-8', errors='replace',
                cwd=repo_root
            )
            cls._cached_result = cls._parse_junit(junit, proc)

    @staticmethod
    def _parse_junit(junit_path: Path, proc) -> Dict:
        """junit XML 을 파싱해 결과 dict 반환.

        XML 부재 = T3 가 아예 실행되지 못한 것 ⇒ 카운트 0 으로 넘겨 축 A 를
        공허 통과시키지 않고 **즉시 실패**시킨다.
        """
        if not Path(junit_path).exists():
            raise AssertionError(
                "junit XML 미생성 — T3 실행 자체가 실패했다(카운트 0 을 통과로 읽으면 안 된다).\n"
                f"exit={proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
            )
        root = ET.parse(junit_path).getroot()
        node = root.find('testsuite') if root.tag == 'testsuites' else root
        total = int(node.get('tests', 0))
        failed = int(node.get('failures', 0))
        errors = int(node.get('errors', 0))
        skipped = int(node.get('skipped', 0))
        return {
            'collected': total,
            'failed': failed,
            'error': errors,
            'skipped': skipped,
            'passed': total - failed - errors - skipped,
            'exit': proc.returncode,
            'stdout': proc.stdout,
            'stderr': proc.stderr,
        }

    def test_t3_outcome_axis_no_failure_error_skip(self):
        """
        AC-8 Axis A (outcome): failed==0 ∧ errors==0 ∧ skipped==0.

        Kills: 구판 회귀(부분 실패) · 전량 skip(pytest exit 0 함정).
        Axis B 가 못 잡는 축 — 21건 수집돼도 3건 실패면 B 는 통과한다.
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
        AC-8 Axis B (collection completeness): collected == N (N = AST 산출).

        Kills: under-collection · 조기 종료(직접 실행 함정에서 일부만 실행).
        Axis A 가 못 잡는 축 — 5건만 돌고 전부 통과하면 A 는 통과한다.
        CP §8.1.1 양방향 비포섭.
        """
        result = self._cached_result
        n = self._expected_test_count

        assert n > 0, "AST 로 T3 test def 0건 — 하네스 파손"
        assert result['collected'] == n, (
            f"T3 collected {result['collected']} tests, expected {n} (AST count); "
            f"output:\n{result['stdout']}\n{result['stderr']}"
        )
