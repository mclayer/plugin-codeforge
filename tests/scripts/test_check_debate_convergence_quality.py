#!/usr/bin/env python3
"""Tests for scripts/check_debate_convergence_quality.py (CFP-582 Phase 2).

TDD format — 7 test cases:
1. positive — 3 marker all present (PASS, exit 0)
2. negative — [COUNTERARGUMENT] 없음 (WARNING, exit 1)
3. negative — [ALTERNATIVE_PROPOSED] 없음 (WARNING, exit 1)
4. negative — [DEBATE_PURPOSE_STATEMENT] 없음 (WARNING, exit 1)
5. edge — no debate transcript section in file (PASS, exit 0 — not applicable)
6. edge — multiple debate transcript sections (모두 검증, 하나라도 WARNING 면 exit 1)
7. error — file not found (ERROR, exit 2)

ADR-060 §결정 15 tri-tier exit-code 정합:
- 0 = PASS (violation 없음 또는 transcript section 없음)
- 1 = WARNING (1+ marker missing)
- 2 = ERROR (파일 미존재 / parse error)
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

# Import the script under test
THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_debate_convergence_quality as checker  # noqa: E402

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

ALL_MARKERS_CONTENT = textwrap.dedent("""\
    # CFP-TEST Story

    ## 9. Debate Transcripts

    ### Debate transcript: F-001

    #### Round 0

    [DEBATE_PURPOSE_STATEMENT]
    본 debate 의 목적은 cross-module boundary 정합성 검증이다.

    #### Round 1

    **Claude worker:**

    [COUNTERARGUMENT]
    제안된 설계의 경계 처리 방식은 기존 ADR-059 §결정 4 와 충돌한다.

    [ALTERNATIVE_PROPOSED]
    boundary guard 를 upstream 모듈에 배치하는 방식으로 재설계를 제안한다.

    **Codex worker:**

    [COUNTERARGUMENT]
    Claude worker 의 upstream placement 제안은 latency SLA 를 위반할 수 있다.
""")

MISSING_COUNTERARGUMENT_CONTENT = textwrap.dedent("""\
    # CFP-TEST Story

    ## 9. Debate Transcripts

    ### Debate transcript: F-002

    #### Round 0

    [DEBATE_PURPOSE_STATEMENT]
    본 debate 의 목적은 경계 조건 검증이다.

    #### Round 1

    **Claude worker:**

    [ALTERNATIVE_PROPOSED]
    대안 제안: guard 를 downstream 에 배치한다.
""")

MISSING_ALTERNATIVE_PROPOSED_CONTENT = textwrap.dedent("""\
    # CFP-TEST Story

    ## 9. Debate Transcripts

    ### Debate transcript: F-003

    #### Round 0

    [DEBATE_PURPOSE_STATEMENT]
    본 debate 의 목적은 API 계약 검증이다.

    #### Round 1

    **Claude worker:**

    [COUNTERARGUMENT]
    현재 설계는 API contract 의 요청/응답 schema 정합성 부재 문제가 있다.
""")

MISSING_DEBATE_PURPOSE_STATEMENT_CONTENT = textwrap.dedent("""\
    # CFP-TEST Story

    ## 9. Debate Transcripts

    ### Debate transcript: F-004

    #### Round 1

    **Claude worker:**

    [COUNTERARGUMENT]
    현재 설계에 대한 반론: 경계 조건 처리 누락.

    [ALTERNATIVE_PROPOSED]
    대안: 명시적 guard clause 추가.
""")

NO_TRANSCRIPT_CONTENT = textwrap.dedent("""\
    # CFP-TEST Story

    ## 1. 요구사항

    Story 본문 내용. debate transcript section 없음.

    ## 8. 구현

    구현 내용.
""")

MULTI_TRANSCRIPT_CONTENT_ONE_MISSING = textwrap.dedent("""\
    # CFP-TEST Story

    ## 9. Debate Transcripts

    ### Debate transcript: F-005

    #### Round 0

    [DEBATE_PURPOSE_STATEMENT]
    첫 번째 debate 목적 선언.

    #### Round 1

    [COUNTERARGUMENT]
    첫 번째 transcript 반론.

    [ALTERNATIVE_PROPOSED]
    첫 번째 transcript 대안.

    ### Debate transcript: F-006

    #### Round 0

    [DEBATE_PURPOSE_STATEMENT]
    두 번째 debate 목적 선언.

    #### Round 1

    [COUNTERARGUMENT]
    두 번째 transcript 반론.

    <!-- ALTERNATIVE_PROPOSED 누락 — 두 번째 transcript 검증 실패 기대 -->
""")

MULTI_TRANSCRIPT_ALL_PASS_CONTENT = textwrap.dedent("""\
    # CFP-TEST Story

    ## 9. Debate Transcripts

    ### Debate transcript: F-007

    #### Round 0

    [DEBATE_PURPOSE_STATEMENT]
    첫 번째 debate 목적 선언.

    #### Round 1

    [COUNTERARGUMENT]
    첫 번째 반론.

    [ALTERNATIVE_PROPOSED]
    첫 번째 대안.

    ### Debate transcript: F-008

    #### Round 0

    [DEBATE_PURPOSE_STATEMENT]
    두 번째 debate 목적 선언.

    #### Round 1

    [COUNTERARGUMENT]
    두 번째 반론.

    [ALTERNATIVE_PROPOSED]
    두 번째 대안.
""")


def _write_tmp(content: str, suffix: str = ".md") -> str:
    """Write content to a temporary file and return its path."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception:
        os.close(fd)
        raise
    return path


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------


class TestCheckDebateConvergenceQuality:
    """7 test cases for check_debate_convergence_quality.py."""

    def test_case_1_all_markers_present_pass(self):
        """Test case 1 (positive): 3 marker all present → PASS, exit 0."""
        path = _write_tmp(ALL_MARKERS_CONTENT)
        try:
            result = checker.check_file(path)
            assert result == 0, (
                f"3 marker 모두 존재 시 exit 0 기대, 실제: {result}"
            )
        finally:
            os.unlink(path)

    def test_case_2_missing_counterargument_warning(self):
        """Test case 2 (negative): [COUNTERARGUMENT] 없음 → WARNING, exit 1."""
        path = _write_tmp(MISSING_COUNTERARGUMENT_CONTENT)
        try:
            result = checker.check_file(path)
            assert result == 1, (
                f"[COUNTERARGUMENT] 누락 시 exit 1 기대, 실제: {result}"
            )
        finally:
            os.unlink(path)

    def test_case_3_missing_alternative_proposed_warning(self):
        """Test case 3 (negative): [ALTERNATIVE_PROPOSED] 없음 → WARNING, exit 1."""
        path = _write_tmp(MISSING_ALTERNATIVE_PROPOSED_CONTENT)
        try:
            result = checker.check_file(path)
            assert result == 1, (
                f"[ALTERNATIVE_PROPOSED] 누락 시 exit 1 기대, 실제: {result}"
            )
        finally:
            os.unlink(path)

    def test_case_4_missing_debate_purpose_statement_warning(self):
        """Test case 4 (negative): [DEBATE_PURPOSE_STATEMENT] 없음 → WARNING, exit 1."""
        path = _write_tmp(MISSING_DEBATE_PURPOSE_STATEMENT_CONTENT)
        try:
            result = checker.check_file(path)
            assert result == 1, (
                f"[DEBATE_PURPOSE_STATEMENT] 누락 시 exit 1 기대, 실제: {result}"
            )
        finally:
            os.unlink(path)

    def test_case_5_no_transcript_section_pass(self):
        """Test case 5 (edge): transcript section 없음 → PASS, exit 0 (not applicable)."""
        path = _write_tmp(NO_TRANSCRIPT_CONTENT)
        try:
            result = checker.check_file(path)
            assert result == 0, (
                f"transcript section 없으면 exit 0 기대 (not applicable), 실제: {result}"
            )
        finally:
            os.unlink(path)

    def test_case_6_multiple_transcripts_one_missing_warning(self):
        """Test case 6 (edge): multiple transcripts, 하나 missing → exit 1."""
        path = _write_tmp(MULTI_TRANSCRIPT_CONTENT_ONE_MISSING)
        try:
            result = checker.check_file(path)
            assert result == 1, (
                f"복수 transcript 중 하나 missing 시 exit 1 기대, 실제: {result}"
            )
        finally:
            os.unlink(path)

    def test_case_7_file_not_found_error(self):
        """Test case 7 (error): file not found → ERROR, exit 2."""
        nonexistent = "/nonexistent/path/story-file-12345.md"
        result = checker.check_file(nonexistent)
        assert result == 2, (
            f"파일 미존재 시 exit 2 기대, 실제: {result}"
        )
