#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CFP-848 / ADR-077 §결정 8 integration lint fixtures — TC-1..TC-12.

Test fixtures for check_adr_077_integration.py validation:
  TC-1: stale-gate precondition declare 존재 (G-1 positive/negative)
  TC-2: 재조사 카운터 §10 비합산 (G-2 negative grep)
  TC-3: ESCALATE escape valve class (G-3)
  TC-4: 4-layer disjoint 무손상 (G-4 negative grep on §10)
  TC-5: cross-Story 통합 checklist 존재 (G-5)
  TC-6: Story-3 deferred carrier 전이 (D3 registry parity)
  TC-7: self-ref graceful (target Story file 부재 시 exit 0)
  TC-8: workflow self-app byte-identical (templates/ ↔ .github/)
  TC-9: thin-wrapper 정합 (exec python3 lib/ 5-line 패턴)
  TC-10: CFP-897 G-3 negation marker exclusion — "NOT failure/abort" / "아님" / "미동반" declare = PASS
  TC-11: CFP-897 G-2/G-4 §10 prose vs table data — disjoint declaration in prose = PASS
  TC-12: CFP-897 self-ref code-block strip — lint spec regex literal in ``` code = PASS

Framework: pytest (ADR-061 §결정 1 + Amendment 1 §결정 6.A)
"""
import subprocess
import tempfile
import filecmp
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LINT_SCRIPT = REPO_ROOT / "scripts" / "lib" / "check_adr_077_integration.py"
REGISTRY_PATH = REPO_ROOT / "docs" / "evidence-checks-registry.yaml"
TEMPLATE_WORKFLOW = REPO_ROOT / "templates" / "github-workflows" / "adr-077-integration.yml"
SELFAPP_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "adr-077-integration.yml"
THIN_WRAPPER = REPO_ROOT / "scripts" / "check-adr-077-integration.sh"


def _run_lint(cwd: Path) -> tuple[int, str, str]:
    """Run integration lint Python SSOT with cwd, capture (exit_code, stdout, stderr)."""
    result = subprocess.run(
        ["python3", str(LINT_SCRIPT)],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout or "", result.stderr or ""


def _make_story_dir(tmp_path: Path) -> Path:
    """Create wrapper/stories/ directory in tmp_path."""
    story_dir = tmp_path / "wrapper" / "stories"
    story_dir.mkdir(parents=True, exist_ok=True)
    return story_dir


def _write_story(story_dir: Path, content: str, name: str = "CFP-TEST.md") -> Path:
    """Write a Story file fixture."""
    path = story_dir / name
    path.write_text(content, encoding="utf-8")
    return path


# ─── Canonical clean Story fixture (all G-1..G-5 satisfied) ───
CLEAN_STORY = """# CFP-TEST: 테스트 Story

## 1. 요구사항

ADR-077 §결정 8 cross-ref — stale 마킹 ↔ phase:설계 진입 차단.
재조사 완료 전 차단 policy.

## 7. 설계

Epic A 5-layer consistency (Story-1 CFP-759 / Story-2 CFP-778 / Story-3 CFP-785):
4-layer disjoint 무손상 확인.

cross-Story layer consistency table:
| Layer | Story | 결과 |
|---|---|---|
| 정책 | CFP-759 | PASS |
| 본문 | CFP-778 | PASS |
| lane | CFP-785 | PASS |
| contract | CFP-834 | PASS |

## 9. Clarification 재조사 이력

| # | spawn | 결과 | 비고 |
|---|---|---|---|
| 1 | 2026-05-17 | resolved | recheck_counter disjoint (§10 합산 금지) |

§10 FIX Ledger 와 disjoint — cross-pollinate 0.

## 10. FIX Ledger

| Iter | 실패 레인 | 원인 | 판정 | 비고 |
|---|---|---|---|---|
| 1 | 구현-리뷰 | 구현 | 구현 원인 | fix applied |

## 12. ESCALATE

ESCALATE 이력: escalation_class: scope_redefinition_required (§10 무기록).
"""


class TestTC1StaleGateDeclare:
    """TC-1: G-1 stale-gate precondition declare 존재."""

    def test_clean_story_passes(self) -> None:
        """TC-1 positive: stale-gate declare 존재 시 PASS."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            story_dir = _make_story_dir(tmp_path)
            _write_story(story_dir, CLEAN_STORY)
            rc, stdout, _ = _run_lint(tmp_path)
            assert rc == 0, f"clean story with stale-gate declare → exit 0 expected. stdout={stdout}"

    def test_missing_stale_gate_declare_fails(self) -> None:
        """TC-1 negative: stale-gate declare 부재 시 FAIL (discriminating fixture)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            story_dir = _make_story_dir(tmp_path)
            content = """# CFP-TEST: Story without stale-gate

## 7. 설계

Epic A 5-layer consistency (Story-1 CFP-759 / Story-2 CFP-778 / Story-3 CFP-785):
cross-Story layer consistency.

## 9. Clarification

§10 합산 금지 disjoint 선언.

## 10. FIX Ledger

| Iter | 실패 레인 | 원인 |
|---|---|---|
| 1 | 구현-리뷰 | 구현 |

## 12. ESCALATE

escalation_class: scope_redefinition_required.
"""
            _write_story(story_dir, content)
            rc, _, stderr = _run_lint(tmp_path)
            assert rc != 0, (
                "stale-gate declare 부재 → exit 1 expected (G-1 violation)"
            )
            assert "G-1" in stderr, f"G-1 violation message expected in stderr: {stderr}"


class TestTC2RecheckCounterDisjoint:
    """TC-2: G-2 재조사 카운터 §10 비합산 (negative grep)."""

    def test_clean_story_no_recheck_in_ledger_passes(self) -> None:
        """TC-2 positive: §10에 recheck 토큰 부재 시 PASS."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            story_dir = _make_story_dir(tmp_path)
            _write_story(story_dir, CLEAN_STORY)
            rc, stdout, _ = _run_lint(tmp_path)
            assert rc == 0, f"clean story → exit 0. stdout={stdout}"

    def test_recheck_counter_in_ledger_fails(self) -> None:
        """TC-2 negative: §10 FIX Ledger에 recheck_counter 토큰 주입 → FAIL (discriminating)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            story_dir = _make_story_dir(tmp_path)
            content = """# CFP-TEST: Story with recheck in §10

## 1. 요구사항

ADR-077 §결정 8 cross-ref — stale 마킹 ↔ phase:설계 진입 차단.

## 7. 설계

Epic A cross-Story layer consistency (CFP-759 / CFP-778 / CFP-785).
4-layer disjoint.

## 9. Clarification

§10 합산 금지 disjoint.

## 10. FIX Ledger

| Iter | 실패 레인 | 원인 | recheck_counter | 비고 |
|---|---|---|---|---|
| 1 | 구현-리뷰 | 구현 | 2 | cross-pollinate violation |

## 12. ESCALATE

escalation_class: scope_redefinition_required.
"""
            _write_story(story_dir, content)
            rc, _, stderr = _run_lint(tmp_path)
            assert rc != 0, (
                "§10 FIX Ledger 에 recheck_counter 주입 → exit 1 expected (G-2/G-4 cross-pollinate)"
            )


class TestTC3EscalateEscapeValve:
    """TC-3: G-3 ESCALATE escape valve class."""

    def test_escalate_without_class_fails(self) -> None:
        """TC-3 negative: ESCALATE + escalation_class 부재 → FAIL."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            story_dir = _make_story_dir(tmp_path)
            content = """# CFP-TEST: ESCALATE without class

## 1. 요구사항

ADR-077 §결정 8 cross-ref — stale 마킹 ↔ phase:설계 진입 차단.

## 7. 설계

Epic A cross-Story (CFP-759 / CFP-778 / CFP-785).

## 9. Clarification

§10 합산 금지 disjoint.

## 10. FIX Ledger

| Iter | 실패 레인 | 원인 |
|---|---|---|
| 1 | 구현 | 구현 |

## 12.

ESCALATE 이력 (no class specified).
"""
            _write_story(story_dir, content)
            rc, _, stderr = _run_lint(tmp_path)
            assert rc != 0, (
                "ESCALATE 출현 + escalation_class 부재 → exit 1 expected (G-3 violation)"
            )
            assert "G-3" in stderr, f"G-3 violation expected in stderr: {stderr}"

    def test_escalate_with_failure_forbidden(self) -> None:
        """TC-3 negative: ESCALATE + failure 동반 → FAIL."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            story_dir = _make_story_dir(tmp_path)
            content = """# CFP-TEST: ESCALATE with failure

## 1. 요구사항

ADR-077 §결정 8 cross-ref — stale 마킹 ↔ phase:설계 진입 차단.

## 7. 설계

Epic A cross-Story (CFP-759 / CFP-778 / CFP-785).

## 9. Clarification

§10 합산 금지 disjoint.

## 10. FIX Ledger

| Iter | 실패 레인 | 원인 |
|---|---|---|
| 1 | 구현 | 구현 |

## 12.

ESCALATE → failure mode (잘못된 표현).
escalation_class: scope_redefinition_required.
"""
            _write_story(story_dir, content)
            rc, _, stderr = _run_lint(tmp_path)
            assert rc != 0, (
                "ESCALATE + failure 동반 → exit 1 expected (G-3 forbidden)"
            )


class TestTC4FourLayerDisjoint:
    """TC-4: G-4 4-layer disjoint 무손상 (negative grep §10 헤더/row)."""

    def test_recheck_in_ledger_header_fails(self) -> None:
        """TC-4 negative: §10 표 헤더에 재조사 카운터 토큰 주입 → FAIL (discriminating)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            story_dir = _make_story_dir(tmp_path)
            content = """# CFP-TEST: 재조사 카운터 in §10 header

## 1. 요구사항

ADR-077 §결정 8 cross-ref — stale 마킹 ↔ phase:설계 진입 차단.

## 7. 설계

Epic A cross-Story (CFP-759 / CFP-778 / CFP-785).
4-layer disjoint.

## 9. Clarification

§10 합산 금지 disjoint.

## 10. FIX Ledger

| Iter | 실패 레인 | 원인 | 재조사 카운터 | 비고 |
|---|---|---|---|---|
| 1 | 구현 | 구현 | 0 | 잘못된 합산 |

## 12. ESCALATE

escalation_class: scope_redefinition_required.
"""
            _write_story(story_dir, content)
            rc, _, stderr = _run_lint(tmp_path)
            assert rc != 0, (
                "§10 헤더에 재조사 카운터 토큰 → exit 1 expected (G-4 cross-pollinate)"
            )


class TestTC5CrossStoryChecklist:
    """TC-5: G-5 cross-Story 통합 일관성 checklist 존재."""

    def test_missing_cross_story_checklist_fails(self) -> None:
        """TC-5 negative: Epic A 5-layer checklist 부재 → FAIL."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            story_dir = _make_story_dir(tmp_path)
            content = """# CFP-TEST: No cross-story checklist

## 1. 요구사항

ADR-077 §결정 8 cross-ref — stale 마킹 ↔ phase:설계 진입 차단.

## 9. Clarification

§10 합산 금지 disjoint.

## 10. FIX Ledger

| Iter | 실패 레인 | 원인 |
|---|---|---|
| 1 | 구현 | 구현 |

## 12. ESCALATE

escalation_class: scope_redefinition_required.
"""
            _write_story(story_dir, content)
            rc, _, stderr = _run_lint(tmp_path)
            assert rc != 0, (
                "cross-Story checklist 부재 → exit 1 expected (G-5 violation)"
            )
            assert "G-5" in stderr, f"G-5 violation expected in stderr: {stderr}"


class TestTC6DeferredCarrierTransition:
    """TC-6: Story-3 deferred carrier 전이 — registry parity (detect_command non-null + Active)."""

    def test_registry_adr077_ratchet_active(self) -> None:
        """TC-6: evidence-checks-registry adr-077-ratchet-declared = Active + detect_command 비null."""
        assert REGISTRY_PATH.exists(), f"Registry not found: {REGISTRY_PATH}"
        content = REGISTRY_PATH.read_text(encoding="utf-8")

        # adr-077-ratchet-declared must have detect_command != null and status: Active
        import re
        # Find the adr-077-ratchet-declared block
        block_match = re.search(
            r"name:\s*adr-077-ratchet-declared.*?(?=\n  - name:|\Z)",
            content,
            re.DOTALL,
        )
        assert block_match, "adr-077-ratchet-declared entry not found in registry"
        block = block_match.group(0)
        assert "detect_command: null" not in block, (
            "adr-077-ratchet-declared detect_command must be non-null (D3 transition)"
        )
        assert "status: Active" in block, (
            "adr-077-ratchet-declared status must be Active (D3 transition)"
        )

    def test_registry_adr077_design_reading_active(self) -> None:
        """TC-6: evidence-checks-registry adr-077-design-reading-mandate-declared = Active."""
        assert REGISTRY_PATH.exists(), f"Registry not found: {REGISTRY_PATH}"
        content = REGISTRY_PATH.read_text(encoding="utf-8")

        import re
        block_match = re.search(
            r"name:\s*adr-077-design-reading-mandate-declared.*?(?=\n  - name:|\Z)",
            content,
            re.DOTALL,
        )
        assert block_match, "adr-077-design-reading-mandate-declared entry not found"
        block = block_match.group(0)
        assert "detect_command: null" not in block, (
            "adr-077-design-reading-mandate-declared detect_command must be non-null"
        )
        assert "status: Active" in block, (
            "adr-077-design-reading-mandate-declared status must be Active (D3 transition)"
        )


class TestTC7SelfRefGraceful:
    """TC-7: self-ref graceful — target Story file 부재 시 exit 0 (sys.exit(1) 금지)."""

    def test_no_story_files_exits_zero(self) -> None:
        """TC-7: Story file 부재 (wrapper/stories/ 미존재) → exit 0, graceful skip."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # No story files created — empty directory
            rc, _, stderr = _run_lint(tmp_path)
            assert rc == 0, (
                "Story file 부재 시 exit 0 (sys.exit(1) 금지) — graceful skip (CFP-702/744 교훈)"
            )
            assert "SKIP" in stderr, (
                f"stderr에 SKIP 메시지 출력 확인: {stderr}"
            )


class TestTC8WorkflowSelfAppByteIdentical:
    """TC-8: workflow self-app byte-identical (ADR-065 §결정 1)."""

    def test_template_and_selfapp_byte_identical(self) -> None:
        """TC-8: templates/github-workflows/adr-077-integration.yml ↔ .github/workflows/ diff 0."""
        assert TEMPLATE_WORKFLOW.exists(), f"Template workflow not found: {TEMPLATE_WORKFLOW}"
        assert SELFAPP_WORKFLOW.exists(), f"Self-app workflow not found: {SELFAPP_WORKFLOW}"
        assert filecmp.cmp(str(TEMPLATE_WORKFLOW), str(SELFAPP_WORKFLOW), shallow=False), (
            "template ↔ .github/workflows byte-identical 위반 (ADR-065 §결정 1)"
        )


class TestTC10G3NegationMarkerExclusion:
    """TC-10 (CFP-897): G-3 negation marker exclusion — normal NOT failure / 아님 / 미동반 declares = PASS."""

    BASE_CLEAN_FRAGMENT = """## 1. 요구사항

ADR-077 §결정 8 cross-ref — stale 마킹 ↔ phase:설계 진입 차단.

## 7. 설계

Epic A 5-layer consistency (Story-1 CFP-759 / Story-2 CFP-778 / Story-3 CFP-785).
4-layer disjoint.

## 9. Clarification

§10 합산 금지 disjoint.

## 10. FIX Ledger

| Iter | 실패 레인 | 원인 |
|---|---|---|
| 1 | 구현-리뷰 | 구현 |
"""

    def _wrap(self, escalate_section: str) -> str:
        """Wrap the §12 ESCALATE fragment with a clean base."""
        return (
            "# CFP-TEST: " + escalate_section[:20] + "\n\n"
            + self.BASE_CLEAN_FRAGMENT
            + "\n## 12. ESCALATE\n\n"
            + escalate_section
        )

    def _check(self, escalate_text: str, expect_pass: bool) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            story_dir = _make_story_dir(tmp_path)
            _write_story(story_dir, self._wrap(escalate_text))
            rc, stdout, stderr = _run_lint(tmp_path)
            if expect_pass:
                assert rc == 0, (
                    f"negation declare expected PASS but FAIL: stderr={stderr}\n"
                    f"text={escalate_text!r}"
                )
            else:
                assert rc != 0, (
                    f"genuine forbidden expected FAIL but PASS: stdout={stdout}\n"
                    f"text={escalate_text!r}"
                )

    def test_NOT_failure_abort_passes(self) -> None:
        """ESCALATE + 'NOT failure/abort' negative declare → PASS (FP 차단)."""
        text = (
            "ESCALATE escape valve = escalation_class:scope_redefinition_required "
            "(NOT failure/abort). "
        )
        self._check(text, expect_pass=True)

    def test_failure_anim_passes(self) -> None:
        """ESCALATE + 'failure 아님' negative declare → PASS."""
        text = (
            "ESCALATE 출현 시 failure 아님 — escalation_class:scope_redefinition_required "
            "정상 escape valve."
        )
        self._check(text, expect_pass=True)

    def test_dansoon_abort_anim_passes(self) -> None:
        """ESCALATE + '단순 abort 아님' negative declare → PASS."""
        text = (
            "ESCALATE 는 단순 abort 아님 — scope_redefinition_required class. "
            "escalation_class: scope_redefinition_required."
        )
        self._check(text, expect_pass=True)

    def test_genuine_failure_still_fails(self) -> None:
        """ESCALATE + 정말 failure 동반 (negation marker 없음) → 여전히 FAIL."""
        text = (
            "ESCALATE 후 작업이 failure 처리되었다. "
            "escalation_class: scope_redefinition_required."
        )
        self._check(text, expect_pass=False)


class TestTC11G2G4ProseVsTableData:
    """TC-11 (CFP-897): §10 prose disjoint declaration text = PASS, only table data violations FAIL."""

    def test_disjoint_declaration_in_prose_passes(self) -> None:
        """§10 section 안 prose paragraph 의 'recheck_counter ↔ §10 disjoint' 정합성 declaration = PASS."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            story_dir = _make_story_dir(tmp_path)
            content = """# CFP-TEST: prose disjoint declaration

## 1. 요구사항

ADR-077 §결정 8 cross-ref — stale 마킹 ↔ phase:설계 진입 차단.

## 7. 설계

Epic A 5-layer consistency (Story-1 CFP-759 / Story-2 CFP-778 / Story-3 CFP-785).
4-layer disjoint.

## 9. Clarification

§10 합산 금지 disjoint.

## 10. FIX Ledger

본 §10 FIX Ledger 는 재조사 카운터(§9.0) 와 disjoint — cross-pollinate 0.
recheck_counter 토큰은 §10 표 row data 영역에 등장 금지 (CFP-897 prose 영역 제외).

| Iter | 실패 레인 | 원인 | 판정 | 비고 |
|---|---|---|---|---|
| 1 | 구현-리뷰 | 구현 | 구현 원인 | fix applied |

## 12. ESCALATE

escalation_class: scope_redefinition_required (NOT failure/abort).
"""
            _write_story(story_dir, content)
            rc, stdout, stderr = _run_lint(tmp_path)
            assert rc == 0, (
                f"prose disjoint declaration in §10 section → PASS expected. "
                f"stderr={stderr}"
            )


class TestTC12SelfRefCodeBlockStrip:
    """TC-12 (CFP-897): self-ref lint spec 인용 (markdown code block 또는 inline code) = PASS."""

    def test_lint_regex_in_fenced_code_passes(self) -> None:
        """§8.1 같은 lint spec section 안 ``` fenced code 의 regex literal 인용 = FP 차단."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            story_dir = _make_story_dir(tmp_path)
            content = """# CFP-TEST: self-ref lint spec

## 1. 요구사항

ADR-077 §결정 8 cross-ref — stale 마킹 ↔ phase:설계 진입 차단.

## 7. 설계

Epic A 5-layer consistency (Story-1 CFP-759 / Story-2 CFP-778 / Story-3 CFP-785).
4-layer disjoint.

## 8.1 Test Contract — adr-077-integration lint spec

본 section 은 lint regex 의 self-ref 인용 영역 — 모든 regex literal 은 code block 안에 contain.

```python
# G-3 forbidden: ESCALATE 와 forbidden 토큰 동반 within 200 chars
G3_FORBIDDEN = re.compile(r"ESCALATE.{0,200}(?:failure|abort)", re.DOTALL)
# G-4 negative grep on §10: recheck_counter token in 재조사 카운터 row → FAIL
G4_RECHECK_TOKEN = re.compile(r"recheck_counter|재조사\\s*카운터")
# G-3 negation markers — NOT failure/abort 등 negative declare exempt
G3_NEGATION_MARKERS = re.compile(r"NOT\\s+(?:failure|abort)")
```

Test case fixtures verify 본 contract 가 §12 ESCALATE 정상 declare 와 어떻게 분리되는지.

## 9. Clarification

§10 합산 금지 disjoint.

## 10. FIX Ledger

| Iter | 실패 레인 | 원인 |
|---|---|---|
| 1 | 구현-리뷰 | 구현 |

## 12. ESCALATE

escalation_class: scope_redefinition_required (NOT failure/abort).
"""
            _write_story(story_dir, content)
            rc, stdout, stderr = _run_lint(tmp_path)
            assert rc == 0, (
                f"lint spec regex literal in ``` code block → PASS expected (FP 차단). "
                f"stderr={stderr}"
            )


class TestTC9ThinWrapperConformance:
    """TC-9: thin-wrapper 정합 (exec python3 lib/ 5-line 패턴, ADR-061 §결정 1)."""

    def test_thin_wrapper_exec_pattern(self) -> None:
        """TC-9: check-adr-077-integration.sh = exec python3 lib/... 패턴 정합."""
        assert THIN_WRAPPER.exists(), f"Thin wrapper not found: {THIN_WRAPPER}"
        content = THIN_WRAPPER.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
        # Must have exec python3 ... lib/check_adr_077_integration.py
        assert any("exec python3" in line and "check_adr_077_integration.py" in line for line in lines), (
            f"thin wrapper must contain 'exec python3 ... check_adr_077_integration.py'. "
            f"Non-comment lines: {lines}"
        )
        # Must be ≤ 7 non-empty non-comment lines (ADR-061 thin-wrapper)
        assert len(lines) <= 7, (
            f"thin wrapper must be ≤ 7 non-comment lines (ADR-061). Got {len(lines)}: {lines}"
        )
