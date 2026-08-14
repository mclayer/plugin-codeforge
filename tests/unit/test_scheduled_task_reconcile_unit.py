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
        """key 는 _safe_text 를 통과 — verdict 어휘 무력화 + secret redact + 제어문자 strip.

        ★ roundtrip 계약: 채널에 실린 key 문자열 = 다음 실행의 재유도값.
        ★ 변환 정정 (구현리뷰 iter5 F-CR5-03): 어휘 무력화가 **삭제 치환**(`<제거>`)에서
          **가역 이스케이프**로 바뀌었다. 구판은 비단사라 `…-PASS-…` 와 `…-FAIL-…` 이
          같은 키로 붕괴했다. 단언을 그 계약에 맞춰 재조준한다 —
          (a) 어휘 매치 0 (b) 주변 사실 보존 (c) 가역."""
        obs = {
            "cls": "orphan",
            "display_path": "~/.claude/worktrees/stale-PASS-component",  # 경로에 PASS 포함
        }
        key = sut.dedup_key(obs)
        assert not sut.contains_verdict_lexicon(key), f"verdict 어휘 잔존: {key}"
        assert "stale-" in key and "-component" in key, (
            f"어휘 주변 경로 사실이 손실됐다 (삭제 변환 회귀 의심): {key}"
        )
        # 가역 — 두 번 스크럽되므로(_safe_text) 좌역원도 두 번
        restored = sut.unscrub_verdict_tokens(sut.unscrub_verdict_tokens(key))
        assert restored == "orphan:~/.claude/worktrees/stale-PASS-component", (
            f"가역성 파괴: {restored!r}"
        )

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
        # verdict 어휘 무력화 (F-CR5-03: 삭제 → 가역 이스케이프)
        assert "OK" not in result
        assert "PASS" not in result
        assert not sut.contains_verdict_lexicon(result), f"어휘 매치 잔존: {result!r}"
        # 사실 보존 — 어휘 자리가 통째 사라지지 않는다 (삭제 변환 회귀 검출)
        assert "state=" in result and "status=" in result, f"필드가 손실됨: {result!r}"


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
        """본문의 verdict 어휘는 **치환**되고 관측 사실은 **보존**된다 (INV-E).

        ★ 이전 판본 `assert A not in r or B in r` 은 B("captured=1")가 A("[capture-gate]
          PASS: captured=1")의 **부분문자열**이라 논리 항진명제였다: A 가 남으면 B 도 남고,
          A 가 사라지면 좌항이 참 — 어느 쪽이든 통과. 실 산출을 직접 단언한다.
        """
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

        # (ㄱ) verdict 어휘는 산출에 0 (INV-E)
        assert "PASS" not in result, f"verdict 어휘 PASS 잔존: {result!r}"
        assert not sut.contains_verdict_lexicon(result), f"어휘 매치 잔존: {result!r}"
        # (ㄴ) 어휘 자리는 **가역 이스케이프**로 남는다 (F-CR5-03: 삭제 치환 폐기).
        #      `[capture-gate] PASS:` → `[capture-gate] P%-ASS:` — 어휘는 죽었고 자리는 산다.
        assert sut._LEXICON_ESCAPE in result, f"이스케이프 마커 미검출: {result!r}"
        assert "capture-gate" in result, f"어휘 주변 사실이 손실됨: {result!r}"
        # (ㄷ) 사실은 보존 — 줄 제거가 아니라 어휘 치환 (관측 손실 0)
        assert "captured=1" in result, f"관측 사실이 손실됨: {result!r}"
        assert "items=1" in result, f"사실 줄이 통째 사라짐: {result!r}"

    def test_render_report_with_timestamp(self):
        """trailer `at=` 는 **KST(+09:00)** ISO 8601 정본값이다 — 로컬 TZ 무관 결정론.

        ★ 이전 판본 `assert "+09:00" in result or "T" in result` 은 우변이 상시 참이었다
          (ISO 8601 은 어느 TZ 든 항상 'T' 를 포함) → KST 축을 전혀 재지 않았다.
          여기서는 `at=` 값을 뽑아 **정본 문자열 동일성**으로 단언한다.

        mutant kill: `_kst_iso` 의 `timezone(timedelta(hours=9))` → `timezone.utc` ⇒ RED.
        """
        import re
        now = 1723555245           # epoch → KST 2024-08-13T22:20:45+09:00
        obs = []
        result = sut.render_report(obs, "test", "123", now=now)

        m = re.search(r"at=(\S+)", result)
        assert m is not None, f"trailer at= 필드 부재: {result!r}"
        at_value = m.group(1)
        assert at_value == "2024-08-13T22:20:45+09:00", (
            f"KST 정본값 불일치 (UTC 등 타 TZ 로 렌더되면 여기서 RED): {at_value!r}"
        )
        assert at_value.endswith("+09:00"), f"KST offset 부재: {at_value!r}"


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
    """경계: 긴 경로 (260+ 초과) + dedup 키 길이 상한 **대칭 적용**."""

    def test_dedup_key_long_path(self):
        """상한 초과 경로는 **경계화 키**가 되고 상한 이내 경로는 원문 그대로다.

        ★ 계약 변경 이력 (ArchitectPL 설계 판정 이행 — D3 라운드트립 봉합):
          이전 판본은 `assert len(key) > 500` 이었다. 그러나 역추출
          (`fetch_existing_keys`)이 `_MAX_KEY_LEN` 초과 키를 폐기하므로, 정방향이 상한을
          넘는 키를 발화하면 그 잔재는 **영원히 재수집되지 않아 매 실행 중복 발화**가
          된다(비대칭 상한). 이제 정방향도 같은 상한을 지킨다.

        검사 축 4종:
          ① 상한 초과 → len(key) <= _MAX_KEY_LEN (대칭)
          ② 경계화 형상 = 앞 480자 원문 + `~` + 8-hex
          ③ 앞부분이 동일하고 뒤만 다른 두 장문 경로가 **서로 다른 키** (digest 판별)
          ④ 상한 이내 경로는 경계화하지 않는다 (원문 보존 — 무차별 해싱 금지)
        """
        long_path = "~/.claude/" + "a" * 500        # raw = 8 + 510 = 518 > 512
        obs = {"cls": "scratch", "display_path": long_path}
        key = sut.dedup_key(obs)

        # ① 대칭 상한
        assert len(key) <= sut._MAX_KEY_LEN, (
            f"상한 초과 키 발화 (역추출이 폐기 → 무한 중복 발화): len={len(key)}"
        )
        # ② 경계화 형상
        assert len(key) == sut._KEY_BOUND_PREFIX + 1 + sut._KEY_BOUND_DIGEST, (
            f"경계화 형상 불일치: len={len(key)}"
        )
        assert key.startswith("scratch:~/.claude/aaa"), f"앞부분 원문 미보존: {key[:40]!r}"
        prefix, sep, digest = key.rpartition("~")
        assert sep == "~" and len(digest) == sut._KEY_BOUND_DIGEST, f"digest 접미 부재: {key[-20:]!r}"
        assert all(c in "0123456789abcdef" for c in digest), f"digest 가 hex 가 아님: {digest!r}"

        # ③ 앞 480자 동일 + 뒤만 다른 장문 → 서로 다른 키
        other = {"cls": "scratch", "display_path": long_path + "-DIFFERENT-TAIL"}
        assert sut.dedup_key(other) != key, (
            "앞부분 동일 장문 경로가 같은 키로 합쳐짐 — digest 판별 실패"
        )

        # ④ 상한 이내는 원문 그대로 (무차별 해싱 금지)
        short = {"cls": "scratch", "display_path": "~/.claude/short"}
        assert sut.dedup_key(short) == "scratch:~/.claude/short", (
            f"상한 이내 키가 경계화됨: {sut.dedup_key(short)!r}"
        )


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
