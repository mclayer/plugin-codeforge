#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CFP-785 / ADR-077 §결정 3·9 mandate fixtures — Group B (design-reading).

Test fixtures for check_adr_077_design_reading_mandate.py validation:
  - B-1: positive (실 ADR-077.md PASS)
  - B-2: negative (invariant 누락 3 sub-cases)
  - B-3: self-ref graceful (파일 부재 시 exit 0, sys.exit(1) 금지)

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


class TestB1DesignReadingPositive:
    """B-1: Positive case — real ADR-077.md with all 3 invariants present."""

    def test_real_adr_077_passes(self) -> None:
        """ADR-077 실파일 + 3 invariant 전부 존재 시 PASS."""
        rc, _, _ = _run_lint("check_adr_077_design_reading_mandate.py", REPO_ROOT)
        assert rc == 0, (
            "ADR-077 §결정 3 skim 금지 + 의도/근거 + "
            "ChangeImpactAgent, FeasibilityAgent, ContinuityAgent 전부 등장 → exit 0"
        )


class TestB2DesignReadingNegative:
    """B-2: Negative cases — 3 sub-variants missing 1 invariant each."""

    def test_missing_skim_prohibition(self) -> None:
        """B-2a: 'skim 금지' 문구 누락 → FAIL."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            dummy_content = """---
title: ADR-077 Dummy
category: governance
is_transitional: false
---
## 개요
Sample ADR without skim prohibition.

## §결정 3
Design reading 관련 결정. 깊이있게 읽을 것.

의도와 근거를 파악한다.

ChangeImpactAgent, FeasibilityAgent, ContinuityAgent 적용.
"""
            _create_dummy_adr(tmp_path, dummy_content)
            rc, _, _ = _run_lint("check_adr_077_design_reading_mandate.py", tmp_path)
            assert rc != 0, (
                "skim 금지 문구 누락 → exit 1 expected"
            )

    def test_missing_intent_rationale(self) -> None:
        """B-2b: '의도'/'근거' 표현 둘 다 누락 → FAIL."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            dummy_content = """---
title: ADR-077 Dummy
category: governance
is_transitional: false
---
## 개요
Sample ADR without intent/rationale.

## §결정 3
Design reading mandate.

skim 금지.

ChangeImpactAgent, FeasibilityAgent, ContinuityAgent 적용.
"""
            _create_dummy_adr(tmp_path, dummy_content)
            rc, _, _ = _run_lint("check_adr_077_design_reading_mandate.py", tmp_path)
            assert rc != 0, (
                "의도와 근거 표현 둘 다 누락 → exit 1 expected"
            )

    def test_missing_one_agent(self) -> None:
        """B-2c: 3 agent 중 1개 (FeasibilityAgent) 누락 → FAIL (AND 조건)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            dummy_content = """---
title: ADR-077 Dummy
category: governance
is_transitional: false
---
## 개요
Sample ADR with incomplete agent list.

## §결정 3
Design reading mandate.

skim 금지. 의도와 근거를 파악한다.

Requirements 라인은 ChangeImpactAgent와 ContinuityAgent가 적용한다.
"""
            _create_dummy_adr(tmp_path, dummy_content)
            rc, _, _ = _run_lint("check_adr_077_design_reading_mandate.py", tmp_path)
            assert rc != 0, (
                "3 agent 중 FeasibilityAgent 누락 (AND 조건) → exit 1 expected"
            )


class TestB3DesignReadingSelfRefGraceful:
    """B-3: Self-ref graceful — ADR-077 부재 시 exit 0 (sys.exit(1) 금지)."""

    def test_adr_077_absent_exits_zero(self) -> None:
        """ADR-077.md 부재 (docs/adr/ 미존재) → exit 0, graceful skip."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            rc, _, stderr = _run_lint("check_adr_077_design_reading_mandate.py", tmp_path)
            assert rc == 0, (
                "ADR-077 파일 부재 시 exit 0 (sys.exit(1) 금지) — graceful skip"
            )
            assert "SKIP" in stderr, (
                "stderr에 [SKIP] 메시지 출력 확인"
            )
