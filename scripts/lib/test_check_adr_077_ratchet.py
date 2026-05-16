#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CFP-785 / ADR-077 §결정 3·9 mandate fixtures — Group A (ratchet).

Test fixtures for check_adr_077_ratchet.py validation:
  - A-1: positive (실 ADR-077.md PASS)
  - A-2: negative (invariant 누락 3 sub-cases)
  - A-3: self-ref graceful (파일 부재 시 exit 0, sys.exit(1) 금지)

Framework: pytest (ADR-061 §결정 1 + Amendment 1 §결정 6.A)
"""
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_lint(script_name: str, cwd: Path) -> tuple[int, str, str]:
    """Run lint script with cwd, capture (exit_code, stdout, stderr)."""
    script = REPO_ROOT / "scripts" / "lib" / script_name
    result = subprocess.run(
        ["python3", str(script)],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout or "", result.stderr or ""


def _create_dummy_adr(tmp_path: Path, content: str) -> None:
    """Create dummy ADR-077 fixture in tmp_path/docs/adr/."""
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True, exist_ok=True)
    (adr_dir / "ADR-077-clarification-forced-reinvestigation-propagation.md").write_text(
        content, encoding="utf-8"
    )


class TestA1RatchetPositive:
    """A-1: Positive case — real ADR-077.md with all 3 invariants present."""

    def test_real_adr_077_passes(self) -> None:
        """ADR-077 실파일 + 3 invariant 전부 존재 시 PASS."""
        rc, _, _ = _run_lint("check_adr_077_ratchet.py", REPO_ROOT)
        assert rc == 0, (
            "ADR-077 frontmatter is_transitional:false + "
            "§결정 9 ratchet 선언 + ADR-058 §결정 5 sunset_justification 참조 존재 → exit 0"
        )


class TestA2RatchetNegative:
    """A-2: Negative cases — 3 sub-variants missing 1 invariant each."""

    def test_missing_is_transitional_false(self) -> None:
        """A-2a: is_transitional:false 누락 → FAIL."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            dummy_content = """---
title: ADR-077 Dummy
category: governance
is_transitional: true
---
## 개요
Sample ADR.

## §결정 9
5 ratchet 속성 명시.

ADR-058 §결정 5 sunset_justification 참조.
"""
            _create_dummy_adr(tmp_path, dummy_content)
            rc, _, _ = _run_lint("check_adr_077_ratchet.py", tmp_path)
            assert rc != 0, (
                "is_transitional:false 누락 (is_transitional: true) → exit 1 expected"
            )

    def test_missing_ratchet_decision_9(self) -> None:
        """A-2b: §결정 9 ratchet 선언 문구 누락 → FAIL."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            dummy_content = """---
title: ADR-077 Dummy
category: governance
is_transitional: false
---
## 개요
Sample ADR without ratchet decision.

## §결정 8
Other decision.

ADR-058 §결정 5 sunset_justification 참조.
"""
            _create_dummy_adr(tmp_path, dummy_content)
            rc, _, _ = _run_lint("check_adr_077_ratchet.py", tmp_path)
            assert rc != 0, (
                "ratchet decision 9 문구 누락 → exit 1 expected"
            )

    def test_missing_sunset_justification_ref(self) -> None:
        """A-2c: ADR-058 §결정 5 sunset_justification 참조 누락 → FAIL."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            dummy_content = """---
title: ADR-077 Dummy
category: governance
is_transitional: false
---
## 개요
Sample ADR.

## §결정 9
5 ratchet 속성: (1) scope (2) condition (3) metric (4) who (5) how.
ratchet 선언.
"""
            _create_dummy_adr(tmp_path, dummy_content)
            rc, _, _ = _run_lint("check_adr_077_ratchet.py", tmp_path)
            assert rc != 0, (
                "ADR-058 §결정 5 sunset_justification 참조 누락 → exit 1 expected"
            )


class TestA3RatchetSelfRefGraceful:
    """A-3: Self-ref graceful — ADR-077 부재 시 exit 0 (sys.exit(1) 금지)."""

    def test_adr_077_absent_exits_zero(self) -> None:
        """ADR-077.md 부재 (docs/adr/ 미존재) → exit 0, graceful skip."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            rc, _, stderr = _run_lint("check_adr_077_ratchet.py", tmp_path)
            assert rc == 0, (
                "ADR-077 파일 부재 시 exit 0 (sys.exit(1) 금지) — graceful skip"
            )
            assert "SKIP" in stderr, (
                "stderr에 [SKIP] 메시지 출력 확인"
            )
