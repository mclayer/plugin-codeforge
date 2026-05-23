"""
test_check_evidence_registry_naming.py — CFP-827 regression test

scripts/lib/check_evidence_registry_naming.py 의 `detect_command: null` 처리 회귀 테스트.

Bug (CFP-827): `entry.get("detect_command", "")` 는 key 가 명시적 null 값으로
존재할 때 None 을 반환 → `.strip()` 호출 시 AttributeError.

Fix: `entry.get("detect_command") or ""` 로 null + missing + empty 3-case 통일.

본 테스트는 script 를 subprocess 로 실행하며 fixture cwd 안에서:
  - `docs/evidence-checks-registry.yaml` (detect_command: null entry 포함)
  - 검증 대상 workflow file
2 종을 임시로 구성한 뒤 script 가 AttributeError 없이 종료하는지 확인한다.
"""

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest


_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "lib" / "check_evidence_registry_naming.py"


def _write_fixture(root: Path, detect_command_value: str) -> None:
    """Build a minimal evidence-checks-registry.yaml + matching workflow file.

    detect_command_value: yaml literal (e.g. 'null', '"bash foo.sh"', '~').
    """
    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    # entry name == workflow basename (no .yml) → exact_match path 통과.
    workflow_dir = root / "templates" / "github-workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    (workflow_dir / "fixture-entry.yml").write_text("# fixture\n", encoding="utf-8")

    yaml_body = textwrap.dedent(
        f"""\
        entries:
          - name: fixture-entry
            status: Active
            detect_command: {detect_command_value}
            workflow: templates/github-workflows/fixture-entry.yml
        """
    )
    (docs / "evidence-checks-registry.yaml").write_text(yaml_body, encoding="utf-8")


def _run_script(cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_SCRIPT_PATH)],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


class TestDetectCommandNull:
    """CFP-827 — `detect_command: null` 가 AttributeError 를 일으키지 않아야 한다."""

    def test_null_detect_command_does_not_raise(self, tmp_path):
        """detect_command: null 일 때 script 가 AttributeError 없이 정상 종료."""
        _write_fixture(tmp_path, "null")
        result = _run_script(tmp_path)
        # The original bug surfaces as AttributeError in traceback on stderr.
        assert "AttributeError" not in result.stderr, (
            f"AttributeError 재발 — fix 회귀:\nstderr={result.stderr!r}\nstdout={result.stdout!r}"
        )
        assert "NoneType" not in result.stderr, (
            f"NoneType 메시지 잔존 — fix 회귀:\nstderr={result.stderr!r}"
        )
        # exact_match 통과 → exit 0 기대 (workflow file 도 fixture 가 생성).
        assert result.returncode == 0, (
            f"unexpected non-zero exit:\n"
            f"  exit={result.returncode}\n  stdout={result.stdout!r}\n  stderr={result.stderr!r}"
        )

    def test_tilde_detect_command_does_not_raise(self, tmp_path):
        """detect_command: ~ (yaml null alias) 도 동일하게 처리되어야 한다."""
        _write_fixture(tmp_path, "~")
        result = _run_script(tmp_path)
        assert "AttributeError" not in result.stderr, result.stderr
        assert result.returncode == 0, (
            f"unexpected non-zero exit:\n"
            f"  exit={result.returncode}\n  stdout={result.stdout!r}\n  stderr={result.stderr!r}"
        )

    def test_normal_detect_command_still_works(self, tmp_path):
        """기존 정상 입력 (string) 도 그대로 동작 — 회귀 방지."""
        _write_fixture(tmp_path, '"bash scripts/whatever.sh"')
        result = _run_script(tmp_path)
        assert "AttributeError" not in result.stderr, result.stderr
        assert result.returncode == 0, (
            f"unexpected non-zero exit:\n"
            f"  exit={result.returncode}\n  stdout={result.stdout!r}\n  stderr={result.stderr!r}"
        )
