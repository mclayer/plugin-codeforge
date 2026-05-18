#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-923 / ADR-078 P-S4 — pytest TC for check_architecture_drift.py (8 TC)
import subprocess
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LINT_SCRIPT = REPO_ROOT / "scripts" / "lib" / "check_architecture_drift.py"
THIN_WRAPPER = REPO_ROOT / "scripts" / "check-architecture-drift.sh"


def write_arch_doc(tmp_path: Path, body: str) -> Path:
    arch_dir = tmp_path / "docs" / "architecture"
    arch_dir.mkdir(parents=True, exist_ok=True)
    f = arch_dir / "codeforge-family.md"
    f.write_text(body, encoding="utf-8")
    return f


def run_lint(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(LINT_SCRIPT), *args]
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace")


def test_tc1_clean_seed_pass():
    """TC-1: S2 seed PASS invariant (Story AC-7 mandatory, Epic §위험 §2 mitigation)."""
    seed_path = "docs/architecture/codeforge-family.md"
    assert (REPO_ROOT / seed_path).is_file(), "S2 seed file 부재"
    result = run_lint(REPO_ROOT, seed_path)
    assert result.returncode == 0, (
        f"TC-1 FAIL: S2 seed must PASS first-run lint.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


def test_tc2_missing_plugin_name_fails(tmp_path):
    body = textwrap.dedent("""\
        ---
        kind: architecture_doc
        ---
        ## 모듈
        codeforge / codeforge-requirements / codeforge-design / codeforge-review / codeforge-develop / codeforge-pmo
        ## 경계
        boundaries
        ## 인터페이스 계약
        review_verdict / requirements_output / design_output / develop_output / test_verdict / pmo_output / git_ops_event
        ## 데이터 흐름
        flow
        """)
    f = write_arch_doc(tmp_path, body)
    result = run_lint(tmp_path, str(f.relative_to(tmp_path)))
    assert result.returncode == 1
    assert "codeforge-test" in result.stderr


def test_tc3_missing_contract_name_fails(tmp_path):
    body = textwrap.dedent("""\
        ---
        kind: architecture_doc
        ---
        ## 모듈
        codeforge / codeforge-requirements / codeforge-design / codeforge-review / codeforge-develop / codeforge-test / codeforge-pmo
        ## 경계
        boundaries
        ## 인터페이스 계약
        review_verdict / requirements_output / design_output / develop_output / test_verdict / pmo_output
        ## 데이터 흐름
        flow
        """)
    f = write_arch_doc(tmp_path, body)
    result = run_lint(tmp_path, str(f.relative_to(tmp_path)))
    assert result.returncode == 1
    assert "git_ops_event" in result.stderr


def test_tc4_anti_scope_line_pattern_fails(tmp_path):
    body = textwrap.dedent("""\
        ---
        kind: architecture_doc
        ---
        ## 모듈
        codeforge / codeforge-requirements / codeforge-design / codeforge-review / codeforge-develop / codeforge-test / codeforge-pmo

        class OrchestratorAgent:

        ## 경계
        boundaries
        ## 인터페이스 계약
        review_verdict / requirements_output / design_output / develop_output / test_verdict / pmo_output / git_ops_event
        ## 데이터 흐름
        flow
        """)
    f = write_arch_doc(tmp_path, body)
    result = run_lint(tmp_path, str(f.relative_to(tmp_path)))
    assert result.returncode == 1
    assert "anti-scope" in result.stderr


def test_tc5_story_changeplan_exempt(tmp_path):
    """ADR-082 §결정 6 EC-3 — Story/Change-Plan/ADR scope guard 자연 면제."""
    story_path = tmp_path / "docs" / "stories" / "CFP-923.md"
    story_path.parent.mkdir(parents=True, exist_ok=True)
    story_path.write_text("class FooBar:\nimport baz\n", encoding="utf-8")
    result = run_lint(tmp_path, str(story_path.relative_to(tmp_path)))
    assert result.returncode == 0


def test_tc6_fenced_code_exempt(tmp_path):
    body = textwrap.dedent("""\
        ---
        kind: architecture_doc
        ---
        ## 모듈
        codeforge / codeforge-requirements / codeforge-design / codeforge-review / codeforge-develop / codeforge-test / codeforge-pmo

        ```python
        class FooBar:
            def baz(self):
                pass
        ```

        ## 경계
        boundaries
        ## 인터페이스 계약
        review_verdict / requirements_output / design_output / develop_output / test_verdict / pmo_output / git_ops_event
        ## 데이터 흐름
        flow
        """)
    f = write_arch_doc(tmp_path, body)
    result = run_lint(tmp_path, str(f.relative_to(tmp_path)))
    assert result.returncode == 0, f"TC-6 FAIL: fenced code citation exemption.\nstderr:\n{result.stderr}"


def test_tc7_path_scope_guard(tmp_path):
    other = tmp_path / "docs" / "other" / "file.md"
    other.parent.mkdir(parents=True, exist_ok=True)
    other.write_text("class Foo:\n", encoding="utf-8")
    result = run_lint(tmp_path, str(other.relative_to(tmp_path)))
    assert result.returncode == 0


def test_tc8_thin_wrapper_conformance():
    """ADR-061 §결정 1 thin wrapper format."""
    assert THIN_WRAPPER.is_file(), "thin wrapper 부재"
    content = THIN_WRAPPER.read_text(encoding="utf-8")
    lines = [ln for ln in content.splitlines() if ln.strip()]
    assert len(lines) <= 12, f"thin wrapper 라인 수 초과: {len(lines)}"
    assert "exec python3" in content
    assert "lib/check_architecture_drift.py" in content
    assert "set -euo pipefail" in content
