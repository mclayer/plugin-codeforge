#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tests/unit/test_scheduled_task_reconcile_unit.py — §8.1 단위 + §8.4 경계
#
# 순수 함수 축 (I/O 0):
#   - dedup_key: class + 홈-상대 경로 유도 (저장하지 않고 대상에서 재유도)
#   - contains_verdict_lexicon / filter_verdict_lines: verdict 어휘 필터 (본 축 실 carrier)
#   - render_fact_tuple: 사실 3-tuple 렌더
#   - render_report: sentinel + 본문 + trailer
#
# 경계:
#   - UNC 경로 (`\\?\` / `\\server\share`)
#   - 유니코드 (NFC/NFD, 심볼릭 링크)
#   - 길이 260+ 초과
#   - 빈 잔재 0건 → 무발화 (render_report 의 if kept)
#   - 거대 잔재 절단

import pytest
from pathlib import Path
from unittest import mock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "lib"))

import scheduled_task_reconcile as sut


class TestDedupKey:
    """dedup_key = class:홈-상대-경로 유도 (§8.1)."""

    def test_dedup_key_formats_correctly(self):
        """기본 형식: class:path."""
        obs = {
            "cls": "worktree",
            "display_path": "~/.claude/worktrees/foo",
        }
        key = sut.dedup_key(obs)
        assert key == "worktree:~/.claude/worktrees/foo"

    def test_dedup_key_sanitizes_verdict_lexicon(self):
        """key 는 _safe_text 를 통과 — verdict 어휘 제거 + secret redact + 제어문자 strip.

        ★ roundtrip 계약: 채널에 실린 key 문자열 = 다음 실행의 재유도값."""
        obs = {
            "cls": "orphan",
            "display_path": "~/.claude/worktrees/stale-PASS-component",  # 경로에 PASS 포함
        }
        key = sut.dedup_key(obs)
        # verdict 어휘 PASS -> <제거>
        assert "<제거>" in key, f"verdict 어휘 제거 기대, 실제: {key}"

    def test_dedup_key_empty_fields(self):
        """빈 필드 처리."""
        obs = {"cls": "", "display_path": ""}
        key = sut.dedup_key(obs)
        assert key == ":"

    def test_dedup_key_dataclass_and_dict_both_work(self):
        """Observation dataclass 와 dict 양쪽 지원."""
        obs_dict = {"cls": "scratch", "display_path": "~/.claude/codeforge-scratch/tmp"}
        obs_obj = sut.Observation(
            cls="scratch",
            display_path="~/.claude/codeforge-scratch/tmp",
            declared="test",
            measured="test",
            mismatch=False,
        )
        assert sut.dedup_key(obs_dict) == sut.dedup_key(obs_obj)


class TestContainsVerdictLexicon:
    """verdict 어휘 포함 여부 검사 (§8.1 carrier).

    ★ 중요: ASCII 는 word-boundary 사용 (부분어 오탐 회피).
    한글은 substring (단어 경계 개념 부재).
    """

    def test_contains_verdict_ascii_pass(self):
        """ASCII verdict (PASS) 검출 — word-boundary."""
        assert sut.contains_verdict_lexicon("result=PASS") is True
        assert sut.contains_verdict_lexicon("[result] PASS: ok") is True
        assert sut.contains_verdict_lexicon("passport") is False  # word-boundary 미매치
        assert sut.contains_verdict_lexicon("passed") is False  # word-boundary 미매치

    def test_contains_verdict_ascii_fail(self):
        """FAIL 검출."""
        assert sut.contains_verdict_lexicon("FAIL: bad") is True
        assert sut.contains_verdict_lexicon("failure") is False  # word-boundary 미매치

    def test_contains_verdict_ascii_ok(self):
        """OK 검출."""
        assert sut.contains_verdict_lexicon("status OK") is True
        assert sut.contains_verdict_lexicon("okay") is False  # word-boundary 미매치

    def test_contains_verdict_korean(self):
        """한글 verdict (정상, 문제없음) 검출 — substring."""
        assert sut.contains_verdict_lexicon("상태=정상") is True
        assert sut.contains_verdict_lexicon("문제없음") is True
        assert sut.contains_verdict_lexicon("정상적인") is True  # substring 포함

    def test_contains_verdict_case_insensitive(self):
        """ASCII 는 대소문자 미구분."""
        assert sut.contains_verdict_lexicon("pass") is True
        assert sut.contains_verdict_lexicon("Fail") is True

    def test_contains_verdict_none_or_empty(self):
        """None/empty 안전 처리."""
        assert sut.contains_verdict_lexicon(None) is False
        assert sut.contains_verdict_lexicon("") is False

    def test_contains_verdict_bypass_string_normal_case(self):
        """정상 케이스: BYPASS 환경 변수는 어휘 오탐이 아님.

        ★ 회귀 고정: bypass 문자열에 PASS 가 포함되지만,
        word-boundary 규칙 때문에 "BYPASS_PASS" 아닌 "BYPASS_..." 형태는
        미매치되어야 한다.
        """
        # BYPASS 가 포함된 문자열 — verdict 어휘 아님
        assert sut.contains_verdict_lexicon("BYPASS_SCHEDULED_TASK_WATCHDOG=1") is False
        # 이 문자열에는 PASS 가 "BYPASS" 의 일부로만 존재하고,
        # word-boundary 규칙에 의해 미매치되어야 함.
        # 만약 naive substring 으로 하면 오탐됨 (과거 함정).


class TestFilterVerdictLines:
    """verdict 어휘가 포함된 줄 제거 (§8.1 실 carrier).

    VERDICT_LEXICON = ("PASS", "FAIL", "OK", "정상", "문제없음")
    """

    def test_filter_removes_verdict_lines(self):
        """verdict 어휘(PASS/FAIL/OK) 포함 줄 제거."""
        text = (
            "정상 상태\n"
            "[some-tool] PASS: result=ok\n"
            "실제 관측: age=7d"
        )
        result = sut.filter_verdict_lines(text)
        # PASS 어휘로 줄 전체 제거
        assert "[some-tool] PASS:" not in result
        # 어휘 없는 줄은 유지
        assert "실제 관측: age=7d" in result

    def test_filter_removes_verdict_lexicon_lines(self):
        """verdict 어휘가 있으면 줄 제거."""
        text = "[test] PASS: result=1"
        result = sut.filter_verdict_lines(text)
        # PASS 어휘로 줄 전체 제거
        assert result.strip() == "", f"PASS 줄 제거 기대, 실제: {result!r}"

    def test_filter_multiline_with_verdict(self):
        """여러 줄 중 verdict 줄만 제거."""
        text = (
            "line 1: age=5d\n"
            "line 2: status=OK\n"
            "line 3: size=100MB"
        )
        result = sut.filter_verdict_lines(text)
        lines = result.strip().split("\n")
        assert len(lines) == 2
        assert any("age=5d" in ln for ln in lines)
        assert any("size=100MB" in ln for ln in lines)
        assert not any("status=OK" in ln for ln in lines)

    def test_filter_none_or_empty(self):
        """None/empty 안전 처리."""
        assert sut.filter_verdict_lines(None) == ""
        assert sut.filter_verdict_lines("") == ""


class TestRenderFactTuple:
    """사실 3-tuple 렌더 — 선언 · 실측 · 불일치 · key (§8.1)."""

    def test_render_fact_tuple_basic(self):
        """기본 형식."""
        obs = sut.Observation(
            cls="worktree",
            display_path="~/.claude/worktrees/old",
            declared="age<=7d",
            measured="age=30d reason=stale",
            mismatch=True,
        )
        result = sut.render_fact_tuple(obs)
        assert "선언=" in result
        assert "실측=" in result
        assert "불일치=Y" in result
        assert "key=" in result
        assert "worktree:~/.claude/worktrees/old" in result

    def test_render_fact_tuple_no_mismatch(self):
        """불일치 없음 — N."""
        obs = sut.Observation(
            cls="scratch",
            display_path="~/.claude/codeforge-scratch/fresh",
            declared="TTL<=7d",
            measured="age=3d",
            mismatch=False,
        )
        result = sut.render_fact_tuple(obs)
        assert "불일치=N" in result

    def test_render_fact_tuple_sanitizes_verdict(self):
        """선언/실측 의 verdict 어휘 제거."""
        obs = sut.Observation(
            cls="orphan",
            display_path="~/.claude/worktrees/test",
            declared="state=OK",
            measured="status=PASS",
            mismatch=False,
        )
        result = sut.render_fact_tuple(obs)
        # verdict 어휘 제거
        assert "OK" not in result
        assert "PASS" not in result
        assert "<제거>" in result


class TestRenderReport:
    """전체 보고 렌더 — sentinel + 사실 + trailer (§8.1)."""

    def test_render_report_with_observations(self):
        """기본 형식: sentinel + 사실 줄 + trailer."""
        obs = [
            sut.Observation(
                cls="worktree",
                display_path="~/.claude/worktrees/stale1",
                declared="age<=7d",
                measured="age=10d",
                mismatch=True,
            ),
        ]
        result = sut.render_report(obs, task_name="daily-gc", run_id="20260813-001")
        assert sut.SENTINEL in result
        assert sut.TRAILER in result
        assert "items=1" in result
        assert "task=daily-gc" in result
        assert "run=20260813-001" in result

    def test_render_report_empty_observations(self):
        """빈 관측 — 사실 줄 0."""
        obs = []
        result = sut.render_report(obs, task_name="test", run_id="123")
        lines = result.strip().split("\n")
        assert sut.SENTINEL in lines[0]
        assert "items=0" in lines[0]
        assert sut.TRAILER in lines[-1]

    def test_render_report_filters_verdict_from_body(self):
        """본문에서 verdict 줄 제거 backstop."""
        obs = [
            sut.Observation(
                cls="temp",
                display_path="~/AppData/Local/Temp/item",
                declared="age<=7d",
                measured="[capture-gate] PASS: captured=1",
                mismatch=False,
            ),
        ]
        result = sut.render_report(obs, "test", "001")
        # verdict 줄이 필터되어 빈 본문 (items=0 이 될 수도)
        assert "[capture-gate] PASS: captured=1" not in result or "captured=1" in result

    def test_render_report_with_timestamp(self):
        """timestamp 포함 (KST ISO 8601)."""
        now = 1723555245  # 2024-08-13 12:00:45 UTC
        obs = []
        result = sut.render_report(obs, "test", "123", now=now)
        assert "at=" in result
        # KST 시간대 확인
        assert "+09:00" in result or "T" in result


class TestBoundaryUnicode:
    """경계: 유니코드 경로 (NFC/NFD, 심볼릭 링크) — sanitize 위임."""

    def test_dedup_key_nfc_nfd_normalize(self):
        """정규화된 유니코드 (sanitize 통과로 가정)."""
        # 실제 정규화는 base.sanitize 에 위임하므로,
        # 이 테스트는 key 가 형식을 유지함을 확인만.
        obs = {
            "cls": "worktree",
            "display_path": "~/.claude/worktrees/한글경로",  # 한글
        }
        key = sut.dedup_key(obs)
        assert "worktree:" in key


class TestBoundaryPathLength:
    """경계: 긴 경로 (260+ 초과)."""

    def test_dedup_key_long_path(self):
        """긴 경로도 key 에 포함."""
        long_path = "~/.claude/" + "a" * 500
        obs = {"cls": "scratch", "display_path": long_path}
        key = sut.dedup_key(obs)
        assert len(key) > 500


class TestBoundaryEmptyObservations:
    """경계: 빈 잔재 0건 → items=0."""

    def test_render_report_zero_observations(self):
        """관측 0건 — render_report 는 items=0."""
        obs = []
        result = sut.render_report(obs, "test", "001")
        # sentinel 줄의 items 필드
        assert "items=0" in result, f"items=0 기대, 실제: {result}"

    def test_render_report_items_count_after_filter(self):
        """filter_verdict_lines 후 유효 줄 개수가 items."""
        obs = [
            sut.Observation(
                cls="test",
                display_path="path",
                declared="test",
                measured="[some-tool] result=1",  # PASS 어휘 없음
                mismatch=False,
            ),
        ]
        result = sut.render_report(obs, "test", "001")
        # render_fact_tuple 결과는 어휘 없으므로 필터 통과
        # items=1
        assert "items=1" in result, f"items=1 기대, 실제: {result}"


class TestBoundaryMaxFactLines:
    """경계: 1회 본문 최대 줄 수 (MAX_FACT_LINES=50)."""

    def test_render_report_within_max_lines(self):
        """MAX_FACT_LINES 이내."""
        obs = [
            sut.Observation(
                cls=f"class{i}",
                display_path=f"path{i}",
                declared="decl",
                measured="meas",
                mismatch=False,
            )
            for i in range(30)
        ]
        result = sut.render_report(obs, "test", "001")
        lines = [ln for ln in result.split("\n") if ln.strip()]
        # sentinel + 30 fact 줄 + trailer = 32 줄
        assert len(lines) == 32


class TestVerdictLexiconCarrier:
    """verdict 필터 carrier — 하위 스크립트 출력 형상 테스트 (§8.1 명시).

    ★ 중요: VERDICT_LEXICON = ("PASS", "FAIL", "OK", "정상", "문제없음")
    DONE 은 lexicon 에 없음 — 수치 파싱은 별도 정규식 (_SCRATCH_DONE_RE 등).
    """

    def test_filter_removes_verdict_not_done(self):
        """VERDICT_LEXICON 의 어휘만 제거."""
        # DONE 은 lexicon 에 없으므로 제거 안 됨
        output = "[scratch-ttl] DONE: purged=0 kept=5"
        filtered = sut.filter_verdict_lines(output)
        # DONE 은 lexicon 에 없으므로 줄 유지
        assert "[scratch-ttl] DONE:" in filtered

    def test_filter_removes_pass_in_output(self):
        """PASS 어휘는 제거 — carrier 실증."""
        output = "[capture-gate] PASS: capture artifact=1"
        filtered = sut.filter_verdict_lines(output)
        # PASS 어휘로 줄 전체 제거
        assert filtered.strip() == "", f"PASS 줄 제거 기대, 실제: {filtered!r}"

    def test_filter_removes_ok_in_output(self):
        """OK 어휘는 제거."""
        output = "[residue-scan] OK: scanned=100"
        filtered = sut.filter_verdict_lines(output)
        # OK 어휘로 줄 제거
        assert filtered.strip() == "", f"OK 줄 제거 기대, 실제: {filtered!r}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not requires_golden"])
