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

import os
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

    def test_dedup_key_collapses_unnormalizable_paths_by_design(self):
        """fail-closed 정규화가 **서로 다른 경로를 한 키로 접는다** (선언된 보안 선택).

        ★ 이 테스트가 있는 이유 (구현리뷰 iter6 F-CR6-04): `unscrub_verdict_tokens`
          docstring 이 좌역원 존재로부터 *"서로 다른 두 잔재 경로가 같은 `dedup_key` 로
          붕괴할 수 없다"* 를 연역했는데, `dedup_key` 가 통과하는 것은 `_safe_text`
          (= scrub∘_normalize_paths∘sanitize∘scrub)이고 `_normalize_paths` 의
          fail-closed 는 **임의 개수의 입력을 상수 하나로 접는다**. 선언이 코드보다
          넓었다.

        ★ 붕괴 자체는 결함이 아니다 — "정규화 실패 = 위치 미공개" 라는 선언된 선택이다.
          이 테스트는 그 선택을 **고정**해, docstring 이 다시 넓어지면(= 붕괴 불가를
          주장하면) 문면과 실측이 어긋난 상태로 남지 않게 한다.

        ★ 대가도 같이 기록한다: 접힌 세 잔재는 dedup 상 **한 건**이라 하나가 발화되면
          나머지는 "기보고" 로 억제된다. 정규화 불능 경로가 여럿일 때의 알려진 손실이다.
        """
        # 사용자명 무관 결정론 트리거 — 2단(`/home/<seg>`)이 소비 못 하는 형태를
        #   3단 후 잔여 가드가 잡아 필드 전체를 접는다.
        paths = ["/srv/home/", "/var/home/", "/a/Users/"]
        keys = [sut.dedup_key({"cls": "orphan", "display_path": p}) for p in paths]

        assert len(set(keys)) == 1, (
            f"전제 붕괴: fail-closed 붕괴가 관측되지 않는다 — 이 테스트가 고정하려는 "
            f"성질이 사라졌다(선언 정정 필요): {dict(zip(paths, keys))}"
        )
        assert keys[0] == "orphan:" + sut._MASK_UNNORMALIZED, (
            f"붕괴 결과가 예상 마스크와 다르다: {keys[0]!r}"
        )
        # 대조군: 정규화 가능한 서로 다른 경로는 **접히지 않는다**(붕괴가 무조건이 아님)
        ok = [sut.dedup_key({"cls": "orphan", "display_path": p})
              for p in ["~/.claude/worktrees/a", "~/.claude/worktrees/b"]]
        assert len(set(ok)) == 2, f"정규화 가능한 경로까지 접혔다: {ok}"

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


class TestHeartbeatTempFileIsWriterUnique:
    """`write_heartbeat` 의 **임시파일 이름**을 정의역으로 삼는 오라클 (iter6 F-CR6-03).

    ★ 왜 새로 필요했나 — 기존 동시성 oracle ④(`..._heartbeat_atomic_write`)는 이 축을
      **재지 못한다**. 그 오라클이 죽는 것은 `os.replace` 를 지웠을 때뿐이고, 임시명을
      공유(`"%s.tmp" % target`)로 되돌려도 **현행판·수정판 둘 다 GREEN** 이다. 즉
      "동시 writer 전원이 같은 임시파일을 연다" 는 결함이 스위트 아래에서 생존했다.
      실측(로컬 Windows, 폴러 0 = 판독 경합 배제): W=8·4000 write 에서 기록 실패
      3425건 → 611건, W=4·600 write 에서 247건 → 48건.

    ★ 여기서 재는 것은 **이름의 고유성**이지 동시성 자체가 아니다(정의역 한정).
      경쟁 스케줄에 의존하지 않으므로 결정론이고, 그래서 CI 에서 flaky 하지 않다.
      cross-process 고유성은 `mkstemp` 의 O_EXCL 성질에서 따라오지만 **본 테스트가
      그것을 실행해 보이지는 않는다** — 그 축은 위 실측이 근거다.

    mutant kill: `tempfile.mkstemp(...)` → `tmp = "%s.tmp" % target` 복원
      ⇒ leg A(호출 간 동일 경로) · leg B(고정 이름 파일 소멸) **동시 RED**.
    """

    def _spy_replace(self, recorded):
        real = os.replace

        def _spy(src, dst):
            recorded.append(src)
            return real(src, dst)
        return _spy

    def test_temp_path_differs_per_call(self, tmp_path):
        """leg A: 연속 두 호출이 **서로 다른** 임시 경로를 쓴다 (target 자신도 아니다)."""
        target = str(tmp_path / "state" / "heartbeat.epoch")
        recorded = []
        with mock.patch.object(sut.os, "replace", side_effect=self._spy_replace(recorded)):
            sut.write_heartbeat(now=1700000001, path=target)
            sut.write_heartbeat(now=1700000002, path=target)

        assert len(recorded) == 2, f"os.replace 2회 기대(write 경로 미도달?): {recorded}"
        assert len(set(recorded)) == 2, (
            f"임시 경로가 호출 간 동일하다 — 동시 writer 전원이 같은 파일을 연다: {recorded}"
        )
        for src in recorded:
            assert src != target, f"임시 경로가 target 과 같다: {src!r}"
            assert os.path.dirname(src) == os.path.dirname(target), (
                f"임시파일이 target 과 다른 디렉터리다 — os.replace 가 cross-device 가 된다: {src!r}"
            )
        # 성공 경로에서는 임시파일이 소비된다 (자기 잔재 0)
        assert sorted(p.name for p in (tmp_path / "state").iterdir()) == ["heartbeat.epoch"], (
            f"임시파일 잔재: {sorted(p.name for p in (tmp_path / 'state').iterdir())}"
        )
        assert (tmp_path / "state" / "heartbeat.epoch").read_text(
            encoding="utf-8").strip() == "1700000002"

    def test_fixed_shared_temp_name_is_never_touched(self, tmp_path):
        """leg B: `<target>.tmp` **고정 이름** 파일이 write 후에도 무손상.

        구판은 정확히 이 이름을 열어 잘라 썼고(`open(tmp, "w")`) 성공하면 rename 으로
        **없애 버렸다**. 그래서 이 leg 은 "다른 writer 의 진행 중 파일을 건드리지
        않는다" 를 파일 하나로 직접 관측한다.
        """
        state = tmp_path / "state"
        state.mkdir()
        target = state / "heartbeat.epoch"
        shared = state / "heartbeat.epoch.tmp"          # 구판이 쓰던 고정 이름
        shared.write_text("다른 writer 가 쓰는 중\n", encoding="utf-8", newline="\n")

        sut.write_heartbeat(now=1700000003, path=str(target))

        assert shared.exists(), (
            "고정 이름 임시파일이 사라졌다 — 구판처럼 공유 임시명을 쓰고 있다"
        )
        assert shared.read_text(encoding="utf-8") == "다른 writer 가 쓰는 중\n", (
            f"고정 이름 임시파일이 덮여 썼다: {shared.read_text(encoding='utf-8')!r}"
        )
        assert target.read_text(encoding="utf-8").strip() == "1700000003"


class TestWarnFieldSeparation:
    """`_warn` 의 **정적 사실 문구 생존**을 정의역으로 삼는 오라클 (iter6 F-CR6-06).

    ★ 결함 형상: 한 문자열로 합쳐 넘기면 `_normalize_paths` 의 fail-closed 가 **필드
      통째**를 접어 사실 문구까지 지운다. 실측(8워커): 경고 3694줄 전부가
      `[scheduled-task] <미정규화-경로-제거>` 였고 "무엇이 왜 실패했는지" 가 0 이었다.

    ★ 정의역 한정: 이 오라클은 **마스킹 정책을 약화하지 않았음**도 같이 잰다 —
      가변 부분은 여전히 접힌다(leg A 두 번째 단언). 즉 "접기를 껐다" 가 아니라
      "접는 단위를 필드로 좁혔다" 를 재는 것이다.

    mutant kill: `_warn` 를 단일 필드(`_safe_text(msg + ": " + detail)`)로 되돌리기
      ⇒ leg A RED.
    """

    # 사용자명 무관 결정론 트리거: 2단이 소비하지 못하는 `/home/`(뒤 세그먼트 없음)를
    #   3단 후 잔여 가드가 잡아 **필드 전체**를 접는다.
    _COLLAPSING = "[Errno 13] denied: /srv/home/"

    def test_static_prefix_survives_when_detail_collapses(self, capsys):
        """leg A: detail 이 통째로 접혀도 정적 사실 문구는 남는다."""
        sut._warn("heartbeat 기록 실패 (non-blocking)", self._COLLAPSING)
        err = capsys.readouterr().err

        assert "heartbeat 기록 실패 (non-blocking)" in err, (
            f"정적 사실 문구가 사라졌다 — 진단 신호 0: {err!r}"
        )
        assert sut._MASK_UNNORMALIZED in err, (
            f"가변 부분이 접히지 않았다 — 마스킹 정책이 약화됐다: {err!r}"
        )
        assert "/srv/home/" not in err, f"미정규화 경로가 그대로 실렸다: {err!r}"

    def test_single_field_form_erases_prefix(self, capsys):
        """leg B (**대조군**): 같은 내용을 한 필드로 넘기면 사실 문구가 사라진다.

        결함이 실재했음을 같은 프로세스에서 보여 주는 앵커다 — leg A 의 GREEN 이
        "원래 안 지워졌다" 가 아니라 "필드를 나눠서 살아남았다" 임을 귀속시킨다.
        """
        sut._warn("heartbeat 기록 실패 (non-blocking): " + self._COLLAPSING)
        err = capsys.readouterr().err

        assert "heartbeat 기록 실패" not in err, (
            f"대조군 전제 붕괴: 단일 필드인데 문구가 살아남았다 — leg A 가 공허해진다: {err!r}"
        )
        assert sut._MASK_UNNORMALIZED in err, f"대조군 전제 붕괴: 접힘이 없다: {err!r}"


class TestTopLevelExceptionAbsorbedIntoZeroExit:
    """`main()` 의 **최상위 예외 흡수**를 정의역으로 삼는 오라클 (iter7 F-CR7-03).

    ★ 왜 필요했나 — 모듈 헤더가 선언한 INV-F(*"exit code 를 오라클로 쓰지 않는 관례
      상속 — 항상 0"*)는 정상 경로에서만 재고 있었다. 최상위 예외 경로는 미결박이라
      `except Exception` → `except ZeroDivisionError` 변이가 8파일 스위트 **133 passed
      로 생존**했다(firsthand 재현). 그 판본에서는 임의 예외가 그대로 프로세스 밖으로
      나가 advisory 계약(호출자를 막지 않는다)이 깨진다.

    ★ 정의역 한정: 재는 것은 `Exception` 계열의 흡수다. `KeyboardInterrupt`·`SystemExit`
      같은 `BaseException` 은 SUT 가 흡수 대상으로 선언하지 않았고(SystemExit 은 별도
      분기로 명시 처리), 이 오라클도 그 축을 넓히지 않는다.

    mutant kill: `except Exception as e:` → `except ZeroDivisionError as e:`
      ⇒ leg A(임의 예외) RED — 예외가 테스트 밖으로 전파된다.
    """

    def test_arbitrary_exception_yields_zero_exit_and_done_marker(self, monkeypatch, capsys):
        """leg A: `run()` 이 임의 예외로 죽어도 rc 0 · DONE 마커가 남는다."""
        def boom(argv=None):
            raise RuntimeError("합성 최상위 실패")

        monkeypatch.setattr(sut, "run", boom)
        rc = sut.main([])
        cap = capsys.readouterr()

        assert rc == 0, f"최상위 예외가 rc={rc!r} 로 새어 나갔다 (advisory 계약 위반)"
        assert "DONE:" in cap.out, f"예외 경로에서 DONE 마커가 사라졌다: {cap.out!r}"
        assert "최상위 예외" in cap.err, f"예외 흡수 경고가 없다 — 다른 경로로 빠졌다: {cap.err!r}"

    def test_systemexit_from_argparse_yields_zero_exit(self, monkeypatch):
        """leg B: argparse 의 usage 종료(SystemExit)도 0 으로 흡수된다."""
        def bail(argv=None):
            raise SystemExit(2)

        monkeypatch.setattr(sut, "run", bail)
        assert sut.main([]) == 0

    def test_control_clean_run_returns_zero_without_exception_marker(self, monkeypatch, capsys):
        """대조군: 예외가 없으면 흡수 경고도 없다 — leg A 의 경고 단언이 공허하지 않다."""
        monkeypatch.setattr(sut, "run", lambda argv=None: 0)
        assert sut.main([]) == 0
        assert "최상위 예외" not in capsys.readouterr().err


class TestHeartbeatTempFileReclaimedOnFailurePath:
    """`write_heartbeat` **실패 경로의 임시파일 회수**를 정의역으로 삼는 오라클 (iter7 F-CR7-04).

    ★ 왜 필요했나 — 성공 경로의 잔재 부재는 `TestHeartbeatTempFileIsWriterUnique` 가
      이미 재지만, `os.replace` 가 실패한 뒤의 회수(`os.unlink(tmp)`)는 미결박이라 그
      호출을 지운 변이가 8파일 스위트 **133 passed 로 생존**했다(firsthand 재현).
      잔재 관측이 주제인 Story 에서 관측자 자신이 잔재를 쌓는 형상이고, iter6 F-CR6-08
      실측대로 이 OSError 분기는 드문 경로가 아니다(8워커 실행에서 다수 발화).

    ★ 공허 차단: "임시파일이 없다" 는 애초에 만들어지지 않아도 성립한다. 그래서
      `mkstemp` 를 감싸 **생성된 경로를 포획**하고, 그 경로가 사라졌음을 직접 잰다.

    mutant kill: `os.unlink(tmp)` 제거 ⇒ leg A RED (포획한 경로가 살아남는다).
    """

    def _spy_mkstemp(self, recorded):
        real = sut.tempfile.mkstemp

        def _spy(*args, **kwargs):
            fd, path = real(*args, **kwargs)
            recorded.append(path)
            return fd, path
        return _spy

    def test_failure_path_leaves_no_temp_residue(self, tmp_path, capsys):
        """leg A: `os.replace` 실패 후 임시파일이 회수된다."""
        state = tmp_path / "state"
        target = state / "heartbeat.epoch"
        created = []

        with mock.patch.object(sut.tempfile, "mkstemp", side_effect=self._spy_mkstemp(created)), \
                mock.patch.object(sut.os, "replace",
                                  side_effect=OSError(13, "합성 rename 실패")):
            sut.write_heartbeat(now=1700000010, path=str(target))

        err = capsys.readouterr().err
        assert len(created) == 1, f"실패 경로가 임시파일을 만들지 않았다 — 이 오라클이 공허해진다: {created}"
        assert "heartbeat 기록 실패" in err, f"실패 분기에 도달하지 않았다: {err!r}"
        assert not os.path.exists(created[0]), f"임시파일 잔재: {created[0]!r}"
        leftovers = sorted(p.name for p in state.iterdir()) if state.is_dir() else []
        assert leftovers == [], f"상태 디렉터리에 잔재가 남았다: {leftovers}"
        assert not target.exists(), "실패했는데 target 이 갱신됐다"

    def test_control_success_path_consumes_temp_file(self, tmp_path):
        """대조군: 성공 경로에서도 포획한 임시 경로가 남지 않는다(rename 으로 소비)."""
        state = tmp_path / "state"
        target = state / "heartbeat.epoch"
        created = []

        with mock.patch.object(sut.tempfile, "mkstemp", side_effect=self._spy_mkstemp(created)):
            sut.write_heartbeat(now=1700000011, path=str(target))

        assert len(created) == 1
        assert not os.path.exists(created[0])
        assert target.read_text(encoding="utf-8").strip() == "1700000011"


class TestResidualDriveGuardIsFailClosed:
    """`_normalize_paths` **최종 잔여 가드(드라이브 축)**를 정의역으로 삼는 오라클 (F-CLA-03).

    ★ 왜 필요했나 — `_RESIDUAL_DRIVE_RE` 를 무매치로 바꾼 변이가 8파일 스위트
      **133 passed 로 생존**했다(firsthand 재현). 기존 §8.8.1 fuzz 오라클
      (`test_scheduled_task_dynamic_roster.py::_UNNORM_DRIVE_RE`)은 SUT **3단**
      (`_DRIVE_RE`)과 같은 negative lookbehind 를 쓰므로, 잔여 가드가 홀로 잡는 구간
      (드라이브 문자 앞이 영숫자라 3단이 지나치는 형상)이 그 오라클의 정의역 밖이다.
      ⇒ 그 축을 fuzz 오라클로 넓히면 `key=test:/...` 같은 조립 seam 이 거짓 위반이 되므로
        (그 lookbehind 가 존재하는 이유다) 넓히지 않고, 여기 **단위 층**에 결박한다.

    ★ 판별 전제를 표본마다 먼저 단언한다 — 3단·userroot·현 사용자명 어느 갈래도 매치하지
      않아야 「마스킹됨」이 **드라이브 잔여 가드의 공로**로 귀속된다.

    mutant kill: `_RESIDUAL_DRIVE_RE` → 무매치 패턴 ⇒ leg A 4 표본 전부 RED.
    """

    # 드라이브 문자 앞이 영숫자라 3단(`_DRIVE_RE`)이 지나치는 형상 — 잔여 가드만 잡는다.
    LEAK_SAMPLES = (
        r"보존사유=tempD:\zzq1\zzq2",
        r"선언=aE:/zzq3/zzq4",
        r"실측=7F:\zzq5",
        r"key=abcG:/zzq6",
    )
    # 3단이 정상 처리하는 형상 — 마스킹이 아니라 `<drive>` 치환이어야 한다(과잉 차단 대조군).
    STAGE3_SAMPLES = (
        (r"보존사유=D:\zzq1\zzq2", r"보존사유=<drive>\zzq1\zzq2"),
        ("선언=E:/zzq3", "선언=<drive>/zzq3"),
    )

    def test_stage3_missed_drive_is_masked_field_wide(self):
        """leg A: 3단이 놓친 드라이브 잔존은 필드 통째 마스킹으로 간다(fail-closed)."""
        user_re = sut._current_user_residual_re()
        for sample in self.LEAK_SAMPLES:
            assert not sut._DRIVE_RE.search(sample), f"3단이 잡는 표본이면 판별 전제가 붕괴한다: {sample!r}"
            assert not sut._RESIDUAL_USERROOT_RE.search(sample), sample
            assert user_re is None or not user_re.search(sample), (
                f"현 사용자명 갈래가 잡으면 드라이브 축 귀속이 안 된다: {sample!r}"
            )
            assert sut._RESIDUAL_DRIVE_RE.search(sample), sample
            assert sut._normalize_paths(sample) == sut._MASK_UNNORMALIZED, (
                f"잔여 드라이브가 그대로 새어 나갔다: {sut._normalize_paths(sample)!r}"
            )

    def test_control_stage3_handled_drive_is_not_over_masked(self):
        """대조군: 3단이 처리한 경로까지 뭉개지 않는다 — leg A 가 「전량 마스킹」이 아님을 귀속."""
        for sample, expected in self.STAGE3_SAMPLES:
            got = sut._normalize_paths(sample)
            assert got == expected, f"{sample!r} → {got!r}"
            assert got != sut._MASK_UNNORMALIZED

    def test_safe_text_pipeline_carries_the_guard(self):
        """산출 파이프라인(`_safe_text`)까지 같은 결론인지 — 렌더 본문이 실제로 쓰는 경로."""
        for sample in self.LEAK_SAMPLES:
            assert sut._MASK_UNNORMALIZED in sut._safe_text(sample), sample


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not requires_golden"])
