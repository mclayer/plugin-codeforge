#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tests/integration/test_scheduled_task_dispatch_path.py
#   — `run()` **발화 경로 완주** harness (구현리뷰 iter4 F-C 봉합)
#
# ── 계기 (ArchitectPL 재평가 실측) ────────────────────────────────────────────────
#   기존 스위트의 `run()` 호출 site 7개가 **전부 조기 반환**했다 —
#     `--dry-run`(2) · 관측 0건(1) · F2 ON(1) · 정지 플래그(2) · `--channel` 미지정(1).
#   ⇒ `fetch_existing_keys()` 에 도달하는 테스트 0건, `post_report()` 도달을 단언하는
#     테스트 0건. 스위트는 **억제 분기만** 검사하고 **발화 분기는 전혀** 검사하지 않았다.
#   미커버 범위는 2줄이 아니라 꼬리 전체다:
#     채널 조회 실패 가드 → dedup 필터 → 신규 0건 가드 → 상한 절단 → 렌더 → 발화
#     → 발화실패 가드.
#
# ── 설계: 주입 표면 신설 0 ───────────────────────────────────────────────────────
#   · 유일 주입점 = **`_gh` 포트**(기존 seam — `STR_GH_BIN` 의 in-process 쌍).
#     `fetch_existing_keys` · dedup 필터 · 신규 0건 가드 · `MAX_FACT_LINES` 절단 ·
#     `render_report` · `post_report` · 발화실패 가드는 **전부 실 production 코드**가
#     돈다. 대역은 subprocess 경계 하나뿐이다.
#   · `collect_observations` 만 fixture 로 대체 — 실 홈 스캔 0 (hermetic).
#   · production 표면(신규 CLI 플래그·env) 신설 **0**
#     (§5.1 "신규 플래그 0건" · ADR-172 §결정 4 lever 계상 규율).
#
# ── 실 GitHub 무접촉 (구조적) ─────────────────────────────────────────────────────
#   `run()` 이 도달할 수 있는 subprocess 호출 site 는 `_gh` **하나뿐**이다
#   (`--repo-root` 지정으로 `_git_toplevel` 미도달, `collect_observations` 는 fixture).
#   그 하나를 in-process 객체로 치환하므로 gh 바이너리·네트워크 도달 경로가 0 이다.
#   채널 문자열도 실재하지 않는 더미(`qadev-harness/none#1`)다.
#
# ── 비공허성 앵커 (mock-seam 규율) ────────────────────────────────────────────────
#   매 호출에서 (a) `[scheduled-task] DONE: observed=N new=M posted=P halted=H` 를
#   **파싱해 값으로** 단언하고 (b) gh 포트 **호출 기록이 비어있지 않음** 을 단언한다.
#   앵커가 없으면 "경로를 탔다" 가 아니라 "죽은 seam 이 조용히 통과" 가 된다.

import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "lib"))

import scheduled_task_reconcile as sut

# 실재하지 않는 더미 채널 — 실 repo·Issue 금지(발화가 실 GitHub 로 나가지 않게).
CHANNEL = "qadev-harness/none#1"

_DONE_RE = re.compile(
    r"\[scheduled-task\] DONE: observed=(\d+) new=(\d+) posted=(\d+) halted=(\d+)"
)
_FACT_LINE_PREFIX = "- 선언="


# ═══════════════════════ 실 사용자 상태 무접촉 검사 헬퍼 ═══════════════════════════
def real_heartbeat_state():
    """실 사용자 heartbeat 파일 스냅샷 (mtime_ns, size). 부재 = None.

    `sut.HEARTBEAT_FILE` 은 import 시점 `expanduser("~")` 로 확정되므로 HOME override
    로는 격리되지 않는다. 본 harness 는 `ENV_HEARTBEAT_FILE` 로 기록 대상을 tmp 로
    돌리고 이 스냅샷으로 실 경로 무접촉을 단언한다 — 테스트가 스케줄 작업의 생존
    신호를 위조하면 watchdog 이 구조적 false-negative 가 된다(ADR-172 §결정 6)."""
    try:
        st = os.stat(sut.HEARTBEAT_FILE)
    except OSError:
        return None
    return (st.st_mtime_ns, st.st_size)


def files_under(root):
    """root 하위 **파일** 상대경로 집합 (디렉터리 제외, posix 구분자)."""
    out = set()
    for dirpath, _dirnames, filenames in os.walk(str(root)):
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), str(root))
            out.add(rel.replace(os.sep, "/"))
    return out


# ═══════════════════════ gh 포트 대역 (유일 주입점) ═══════════════════════════════
class FakeChannel:
    """`sut._gh` 대역 — append-only 보고 채널을 in-process 로 재현한다 (INV-C).

    ★ 이 객체는 **subprocess 경계**만 대신한다. 호출자인 `fetch_existing_keys` /
      `post_report` 는 실 production 코드가 그대로 돈다 — 키 추출(INV-D 본문 폐기),
      `--body-file` 경유 본문 전달, returncode 판정 전부 실물이다.

    Args:
        view_rc: `issue view` 반환 코드 (0 아님 ⇒ `fetch_existing_keys` → None).
        comment_rc: `issue comment` 반환 코드 (0 아님 ⇒ `post_report` → False).
        view_stdout: `issue view` stdout 강제 치환 (형식 위반 주입용, None 이면 정상 JSON).
    """

    def __init__(self, view_rc=0, comment_rc=0, view_stdout=None):
        self.comments = []      # 채널에 실재하는 코멘트 본문 전량 (seed + posted)
        self.posted = []        # 이번 harness 실행들이 **실제로 착지시킨** 본문만
        self.calls = []         # gh argv 기록 (비공허성 앵커)
        self.view_rc = view_rc
        self.comment_rc = comment_rc
        self.view_stdout = view_stdout

    def seed(self, body):
        """채널에 이미 실려 있는 코멘트를 심는다 (기보고분 재현)."""
        self.comments.append(body)
        return self

    def seed_report(self, observations, task="seed", run_id="seed"):
        """production 렌더러로 기보고 코멘트를 심는다 — 키 라운드트립이 실물이 되게."""
        return self.seed(sut.render_report(list(observations), task, run_id))

    # --- 포트 인터페이스: `_gh(args, timeout=...)` 형상 ---
    def __call__(self, args, timeout=None):
        argv = [str(a) for a in args]
        self.calls.append(argv)

        if "view" in argv and "--json" in argv:
            if self.view_rc != 0:
                return subprocess.CompletedProcess(argv, self.view_rc, stdout="", stderr="")
            payload = self.view_stdout
            if payload is None:
                payload = json.dumps({"comments": [{"body": b} for b in self.comments]})
            return subprocess.CompletedProcess(argv, 0, stdout=payload, stderr="")

        if "comment" in argv:
            body = ""
            if "--body-file" in argv:
                path = argv[argv.index("--body-file") + 1]
                with open(path, encoding="utf-8") as fh:
                    body = fh.read()
            if self.comment_rc != 0:
                return subprocess.CompletedProcess(argv, self.comment_rc, stdout="", stderr="")
            self.comments.append(body)
            self.posted.append(body)
            return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    # --- 조회 편의 ---
    def viewed(self):
        return [c for c in self.calls if "view" in c]

    def commented(self):
        return [c for c in self.calls if "comment" in c]


# ═══════════════════════ 관측 fixture ════════════════════════════════════════════
def make_obs(idx, cls="worktree"):
    """결정론 관측 1건. `%03d` 고정폭 — 키가 서로 **접두 관계가 되지 않게**
    (`harness-001` 이 `harness-002` 의 접두라면 `in` 단언이 조용히 오판한다)."""
    return sut.Observation(
        cls=cls,
        display_path="~/.claude/worktrees/harness-%03d" % idx,
        declared="정리 완료(잔재 0)",
        measured="잔존 %d일" % (idx % 7 + 1),
        mismatch=True,
    )


def make_obs_list(n, start=1):
    return [make_obs(i) for i in range(start, start + n)]


def keys_of(observations):
    return [sut.dedup_key(o) for o in observations]


# ═══════════════════════ run() 완주 harness ══════════════════════════════════════
@dataclass
class RunOutcome:
    rc: int
    stdout: str
    stderr: str
    observed: int
    new: int
    posted: int
    halted: int
    chan: object = None
    body: str = None            # 이번 호출이 착지시킨 본문 (미발화면 None)
    argv: list = field(default_factory=list)

    def fact_lines(self):
        if self.body is None:
            return []
        return [ln for ln in self.body.splitlines() if ln.startswith(_FACT_LINE_PREFIX)]

    def items_field(self):
        m = re.search(r"items=(\d+)", self.body or "")
        return int(m.group(1)) if m else None


def invoke_run(tmp_path, observations, chan, channel=CHANNEL, argv_extra=(),
               task="qadev-harness", run_id="r-001", expect_heartbeat=True):
    """`sut.run()` 을 **완주**시키고 산출을 구조화해 반환한다.

    격리 3중:
      ① `ENV_HEARTBEAT_FILE` → tmp (실 사용자 생존 신호 무접촉 — 사후 단언)
      ② `STOP_FLAG_LOCAL` → tmp 의 **부재 경로** (실 F2 플래그가 존재하면 전 케이스가
         정지 분기로 새어 조용히 거짓통과한다 — 그 함정 차단)
      ③ `tempfile.tempdir` → tmp (`post_report` 의 `--body-file` 임시파일까지 tmp 안)

    사후 보편 단언 (공허 통과 차단):
      · `rc == 0` (INV-F)
      · 실 heartbeat 파일 무변화
      · `collect_observations` 정확히 1회 호출 (fixture seam 실효)
      · 채널 지정 시 gh 포트 **호출 기록 비어있지 않음**
      · tmp 하위 파일 = heartbeat 뿐 (**로컬 dedup 상태 파일 0** — INV-C)
      · `DONE:` 마커 실재 + 파싱 성공
    """
    root = str(tmp_path)
    repo_root = os.path.join(root, "repo")
    os.makedirs(repo_root, exist_ok=True)
    hb_path = os.path.join(root, "heartbeat.epoch")
    stop_local = os.path.join(root, "never-created-f2.disabled")

    argv = ["--repo-root", repo_root, "--task-name", task, "--run-id", run_id]
    if channel:
        argv += ["--channel", channel]
    argv += list(argv_extra)

    posted_before = len(chan.posted)
    real_before = real_heartbeat_state()
    out, err = io.StringIO(), io.StringIO()

    with mock.patch.dict(os.environ, {sut.ENV_HEARTBEAT_FILE: hb_path}):
        for k in (sut.ENV_CHANNEL, sut.ENV_TASK_NAME, sut.ENV_RUN_ID, sut.GH_BIN_ENV):
            os.environ.pop(k, None)      # 앰비언트 설정 유입 차단 (patch.dict 가 복원)
        with mock.patch.object(sut, "STOP_FLAG_LOCAL", stop_local), \
                mock.patch.object(tempfile, "tempdir", root), \
                mock.patch.object(sut, "collect_observations",
                                  return_value=list(observations)) as spy_collect, \
                mock.patch.object(sut, "_gh", chan):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = sut.run(argv)

    stdout, stderr = out.getvalue(), err.getvalue()

    assert rc == 0, "INV-F 위반 (exit code 를 신호로 씀): rc=%r / stderr=%r" % (rc, stderr)
    assert real_heartbeat_state() == real_before, (
        "테스트가 실 사용자 heartbeat 경로를 건드렸다: %s" % sut.HEARTBEAT_FILE
    )
    assert spy_collect.call_count == 1, (
        "collect_observations 호출 %d회 (기대 1) — fixture seam 미작동 또는 조기 반환"
        % spy_collect.call_count
    )
    if channel:
        assert chan.calls, (
            "gh 포트 호출 기록이 비어 있다 — 채널 축 미진입(조기 반환) 또는 seam 사망. "
            "stdout=%r stderr=%r" % (stdout, stderr)
        )

    residue = files_under(root)
    expected_files = {"heartbeat.epoch"} if expect_heartbeat else set()
    assert residue == expected_files, (
        "tmp 하위 파일이 %r (기대 %r) — 로컬 dedup 상태 파일이 생겼거나(INV-C 위반) "
        "heartbeat 기록 경로가 소실됐다" % (sorted(residue), sorted(expected_files))
    )

    m = _DONE_RE.search(stdout)
    assert m is not None, "DONE 마커 부재 (경로 미완주): stdout=%r stderr=%r" % (stdout, stderr)

    body = chan.posted[posted_before] if len(chan.posted) > posted_before else None
    return RunOutcome(
        rc=rc, stdout=stdout, stderr=stderr,
        observed=int(m.group(1)), new=int(m.group(2)),
        posted=int(m.group(3)), halted=int(m.group(4)),
        chan=chan, body=body, argv=argv,
    )


# ═══════════════════════ F-C 최소 커버 6종 ═══════════════════════════════════════
class TestFirePathReached:
    """① 발화 도달 — 관측 ≥1 ∧ 채널 지정 ∧ 채널 비어 있음 ⇒ 발화 1회."""

    def test_posts_once_when_channel_empty(self, tmp_path):
        """mutant kill: `ok = post_report(channel, body)` → `ok = True` (발화 제거) ⇒ RED.

        비공허성 앵커: `DONE: observed=2 new=2 posted=1 halted=0` + gh `issue comment` 1회.
        """
        obs = make_obs_list(2)
        chan = FakeChannel()

        r = invoke_run(tmp_path, obs, chan)

        # 발화가 **실제로** 일어났는가 (개체 수)
        assert len(chan.posted) == 1, (
            "발화 개체 %d (기대 1) — 발화 경로 미도달" % len(chan.posted)
        )
        assert len(chan.commented()) == 1, "gh `issue comment` 호출 %d회 (기대 1)" % len(chan.commented())
        assert len(chan.viewed()) == 1, "gh `issue view` 호출 %d회 (기대 1)" % len(chan.viewed())

        # 본문에 관측이 실렸는가
        assert r.body is not None
        assert sut.SENTINEL in r.body, "sentinel 마커 부재 — 자기 코멘트 식별 불가(INV-D)"
        assert sut.TRAILER in r.body, "trailer 마커 부재"
        for k in keys_of(obs):
            assert ("key=%s" % k) in r.body, "관측 %r 가 발화 본문에 미등재" % k
        assert r.items_field() == 2, "items=%r (기대 2)" % r.items_field()
        assert len(r.fact_lines()) == 2, "사실 줄 %d (기대 2)" % len(r.fact_lines())

        # 채널 인자가 그대로 전달됐는가 (owner/repo#N 분해)
        comment_argv = chan.commented()[0]
        assert "qadev-harness/none" in comment_argv and "1" in comment_argv, (
            "채널 인자 전달 불일치: %r" % comment_argv
        )

        # DONE 앵커
        assert (r.observed, r.new, r.posted, r.halted) == (2, 2, 1, 0), (
            "DONE 불일치: observed=%d new=%d posted=%d halted=%d" % (r.observed, r.new, r.posted, r.halted)
        )


class TestFirePathDedupFilter:
    """② dedup 필터 — 채널이 이미 보유한 키는 본문에서 빠진다."""

    def test_posts_only_fresh_keys(self, tmp_path):
        """mutant kill: `fresh = [o for o in observations if ...]` → `fresh = list(observations)`
        (필터 제거) ⇒ 기보고 키가 본문에 재등장 ⇒ RED.
        """
        obs = make_obs_list(3)
        reported, fresh_obs = obs[:1], obs[1:]
        chan = FakeChannel().seed_report(reported)      # o1 은 이미 기보고

        r = invoke_run(tmp_path, obs, chan)

        assert len(chan.posted) == 1, "발화 개체 %d (기대 1)" % len(chan.posted)
        k_reported = sut.dedup_key(reported[0])
        assert ("key=%s" % k_reported) not in r.body, (
            "기보고 키 %r 가 본문에 재등재 — dedup 필터 미작동(매 실행 중복 발화)" % k_reported
        )
        for k in keys_of(fresh_obs):
            assert ("key=%s" % k) in r.body, "신규 키 %r 누락" % k
        assert r.items_field() == 2, "items=%r (기대 2 — 신규분만)" % r.items_field()
        assert len(r.fact_lines()) == 2, "사실 줄 %d (기대 2)" % len(r.fact_lines())
        assert (r.observed, r.new, r.posted, r.halted) == (3, 2, 1, 0), (
            "DONE 불일치: observed=%d new=%d posted=%d halted=%d" % (r.observed, r.new, r.posted, r.halted)
        )


class TestFirePathNoFreshGuard:
    """③ 신규 0건 가드 — 관측 전량이 기보고면 발화하지 않는다 (빈 보고 금지)."""

    def test_no_post_when_all_keys_already_reported(self, tmp_path):
        """mutant kill: `if not fresh: ... return 0` 가드 제거 ⇒ 빈 본문 발화 ⇒ RED."""
        obs = make_obs_list(3)
        chan = FakeChannel().seed_report(obs)           # 전 키 기보고

        r = invoke_run(tmp_path, obs, chan)

        assert chan.posted == [], (
            "신규 0건인데 발화 %d회 — 빈 보고 금지 가드 미작동: %r" % (len(chan.posted), chan.posted)
        )
        assert chan.commented() == [], "gh `issue comment` 가 호출됨: %r" % chan.commented()
        assert len(chan.viewed()) == 1, "채널 조회는 1회 있어야 한다 (경로 도달 증거)"
        assert "신규 0건" in r.stderr, "신규 0건 사유 미보고: %r" % r.stderr
        assert (r.observed, r.new, r.posted, r.halted) == (3, 0, 0, 0), (
            "DONE 불일치: observed=%d new=%d posted=%d halted=%d" % (r.observed, r.new, r.posted, r.halted)
        )


class TestFirePathMaxFactLinesTruncation:
    """④ 상한 절단 — 1회 본문은 `MAX_FACT_LINES` 이하, 초과분은 **다음 실행 재관측**."""

    def test_truncates_and_remainder_reobserved_next_run(self, tmp_path):
        """mutant kill: `to_post = fresh[:MAX_FACT_LINES]` → `to_post = fresh` ⇒ RED.

        ★ 상태 무저장(INV-B/INV-C) 확증: 두 실행 사이에 **로컬 상태 파일이 하나도 생기지
          않는데** 잔여분이 정확히 회수된다 — 회수 근거가 로컬 커서가 아니라 채널 자신임.
          (`invoke_run` 이 매 호출마다 tmp 하위 파일 = heartbeat 뿐임을 단언한다.)
        """
        total = sut.MAX_FACT_LINES + 7
        obs = make_obs_list(total)
        chan = FakeChannel()

        # --- 1회차: 상한까지만 적재 ---
        r1 = invoke_run(tmp_path, obs, chan)

        assert len(chan.posted) == 1, "1회차 발화 개체 %d (기대 1)" % len(chan.posted)
        assert len(r1.fact_lines()) == sut.MAX_FACT_LINES, (
            "1회차 사실 줄 %d (상한 %d 초과 — 절단 미작동)"
            % (len(r1.fact_lines()), sut.MAX_FACT_LINES)
        )
        assert r1.items_field() == sut.MAX_FACT_LINES, "1회차 items=%r" % r1.items_field()
        assert "상한" in r1.stderr, "절단 사유 미보고: %r" % r1.stderr
        assert (r1.observed, r1.new, r1.posted, r1.halted) == (total, total, 1, 0), (
            "1회차 DONE 불일치: observed=%d new=%d posted=%d halted=%d"
            % (r1.observed, r1.new, r1.posted, r1.halted)
        )

        all_keys = keys_of(obs)
        loaded = [k for k in all_keys if ("key=%s" % k) in r1.body]
        remainder = [k for k in all_keys if k not in loaded]
        assert len(loaded) == sut.MAX_FACT_LINES, "1회차 적재 키 %d" % len(loaded)
        assert len(remainder) == 7, "잔여 키 %d (기대 7)" % len(remainder)

        # --- 2회차: 같은 관측 전량 재관측 ⇒ 잔여 7건만 발화 ---
        r2 = invoke_run(tmp_path, obs, chan, run_id="r-002")

        assert len(chan.posted) == 2, "2회차 발화 개체 누계 %d (기대 2)" % len(chan.posted)
        assert len(r2.fact_lines()) == 7, "2회차 사실 줄 %d (기대 7 — 잔여분)" % len(r2.fact_lines())
        for k in remainder:
            assert ("key=%s" % k) in r2.body, "잔여 키 %r 가 2회차에 미회수 (영구 미관측)" % k
        for k in loaded:
            assert ("key=%s" % k) not in r2.body, "1회차 적재 키 %r 가 2회차에 중복 발화" % k
        assert (r2.observed, r2.new, r2.posted, r2.halted) == (total, 7, 1, 0), (
            "2회차 DONE 불일치: observed=%d new=%d posted=%d halted=%d"
            % (r2.observed, r2.new, r2.posted, r2.halted)
        )


class TestFirePathChannelQueryFailure:
    """⑤ 채널 조회 실패 fail-closed — 조회 불가면 **무발화**(누락은 다음 실행 자기치유)."""

    def test_no_post_when_fetch_returns_none(self, tmp_path):
        """mutant kill: `if existing is None: → existing = set()` (빈 집합 취급) ⇒ 발화 ⇒ RED."""
        obs = make_obs_list(3)
        chan = FakeChannel(view_rc=1)                  # `issue view` 실패

        # 전제 확증: 이 조건에서 production 판정이 실제로 None 인가
        assert sut.fetch_existing_keys(CHANNEL, gh=FakeChannel(view_rc=1)) is None

        r = invoke_run(tmp_path, obs, chan)

        assert chan.posted == [], (
            "조회 실패인데 발화 %d회 — fail-closed 위반(중복 발화 위험): %r"
            % (len(chan.posted), chan.posted)
        )
        assert chan.commented() == [], "gh `issue comment` 가 호출됨: %r" % chan.commented()
        assert len(chan.viewed()) == 1, "채널 조회 시도는 1회 있어야 한다 (경로 도달 증거)"
        assert "채널 조회 실패" in r.stderr, "조회 실패 사유 미보고: %r" % r.stderr
        assert (r.observed, r.new, r.posted, r.halted) == (3, 0, 0, 0), (
            "DONE 불일치: observed=%d new=%d posted=%d halted=%d" % (r.observed, r.new, r.posted, r.halted)
        )

    def test_no_post_when_view_stdout_malformed(self, tmp_path):
        """형제 조건: 조회는 성공했으나 응답이 JSON 이 아니면 동일하게 fail-closed."""
        obs = make_obs_list(2)
        chan = FakeChannel(view_stdout="not-a-json{{{")

        r = invoke_run(tmp_path, obs, chan)

        assert chan.posted == [], "형식 위반 응답인데 발화: %r" % chan.posted
        assert "채널 조회 실패" in r.stderr, "조회 실패 사유 미보고: %r" % r.stderr
        assert (r.observed, r.new, r.posted, r.halted) == (2, 0, 0, 0)


class TestFirePathPostFailureNonBlocking:
    """⑥ 발화 실패 비차단 — 실패해도 exit 0 유지 + 사유 보고 (INV-F)."""

    def test_post_failure_keeps_exit_zero_and_warns(self, tmp_path):
        """mutant kill: `if not ok:` 분기를 `raise RuntimeError(...)` 또는 `return 1` 로
        치환 ⇒ RED (`invoke_run` 의 `rc == 0` 단언 또는 예외 전파).
        """
        obs = make_obs_list(3)
        chan = FakeChannel(comment_rc=1)               # `issue comment` 실패

        r = invoke_run(tmp_path, obs, chan)

        assert r.rc == 0, "INV-F 위반: rc=%r" % r.rc
        # 비공허성: 발화를 **시도**는 했는가 (조용히 건너뛴 게 아님)
        assert len(chan.commented()) == 1, (
            "발화 시도 %d회 (기대 1) — 실패 경로가 아니라 미도달 경로였다" % len(chan.commented())
        )
        assert chan.posted == [], "실패했는데 채널에 착지: %r" % chan.posted
        assert "채널 발화 실패" in r.stderr, "발화 실패 사유 미보고: %r" % r.stderr
        assert (r.observed, r.new, r.posted, r.halted) == (3, 3, 0, 0), (
            "DONE 불일치: observed=%d new=%d posted=%d halted=%d" % (r.observed, r.new, r.posted, r.halted)
        )


# ═══════════════════════ 정직 천장 (본 harness 가 봉인하지 않는 것) ═══════════════
# · 본 harness 는 `_gh` **아래**(실 gh 바이너리 argv 수용성 · GitHub API 응답 형상 ·
#   rate limit · 권한)를 검증하지 않는다. 그 축은 live 실측(AC-1) 소관이며 미측정이다.
# · `--body-file` 경유 한글 라운드트립은 여기서 UTF-8 로 읽어 확인하지만, 실 gh 의
#   Windows argv mangling 은 대상 밖이다.
# · 따라서 본 파일의 GREEN 은 "발화가 실 채널에 착지한다" 를 봉인하지 않는다 —
#   봉인 대상은 `run()` 의 발화 **분기 로직**뿐이다 (ADR-119 검사연극 금지).

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
