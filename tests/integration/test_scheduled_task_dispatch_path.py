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
# ── 실 subprocess 표면 (실측치 — 서술 아님) ───────────────────────────────────────
#   결론: gh 바이너리·네트워크 도달 경로 0. `_gh` 를 in-process 객체로 치환하고
#   채널 문자열도 실재하지 않는 더미(`qadev-harness/none#1`)를 쓴다.
#
#   ★ 이전 판본은 그 결론의 **근거**로 *"`run()` 이 도달할 수 있는 subprocess 호출
#     site 는 `_gh` 하나뿐"* 이라고 썼다 — **거짓이었다**(구현리뷰 iter4 F-CR-401).
#     `subprocess.run`/`Popen` 을 가로채 실측하면 `_gh` **밖**에 실 subprocess 가 1건 있다:
#         `git -C . worktree list --porcelain`
#       ← **`run()` (4) dedup 필터** → `dedup_key` → `_safe_text` → `_normalize_paths`
#         → `_mask_workspace_prefix` → `_workspace_prefixes()` 의 **lazy 해소**.
#         `collect_observations` 를 fixture 로 대체하면 권위값 주입 지점
#         (`_observe_workspace_residue` 의 `_set_workspace_prefixes()`)이 통째로
#         건너뛰어지기 때문이다.
#     무너진 건 "단일 site" 라는 **근거 명제**이고, 결론(네트워크 도달 0)은 유지된다
#     — 위 1건은 로컬 git 조회이지 gh·네트워크가 아니다.
#
#   ★ 귀속 정정 (구현리뷰 iter5 F-CR5-04): FIX4 봉합은 이 자리에 lazy 해소 site 를
#     `render_report → …` 로 적었다. **실측 콜스택은 `dedup_key → …`** 다 —
#     `run()` 은 (4) 단계에서 `fresh = [o for o in observations if dedup_key(o) not in
#     existing]` 로 `dedup_key` 를 **먼저** 부르고, `render_report` 는 그 뒤 (4) 말미다.
#     iter4 finding 이 옳게 지목했던 함수를 봉합이 틀린 함수로 바꿔 적은 것이며,
#     실측치(스택 프레임 판독)로 되돌린다:
#       run:792 `fresh = [...dedup_key(o)...]` → dedup_key:377 `cls = _safe_text(...)`
#       → _safe_text:291 → _normalize_paths:269 → _mask_workspace_prefix:252
#       → _workspace_prefixes()
#     (`render_report` 도 같은 경로를 타지만 **최초 해소자가 아니다** — 최초 1회에서만
#      lazy 해소가 일어나므로 site 귀속은 첫 호출자에게 간다.)
#
#   봉합 2단 (F-CR-401):
#     ① **캐시 순서 의존 제거** — `invoke_run` 이 workspace 접두를 **명시 주입**해 lazy
#        해소를 없앤다 ⇒ 실 subprocess **0건**. (`_workspace_prefix_cache` 는 모듈 전역인데
#        이를 리셋하는 test/conftest 가 repo 전체 **0건**이라, 주입이 없으면 pytest 세션의
#        **최초 해소자 승리** 순서 의존이 된다.) 주입 전 값은 `finally` 로 복원해 본 harness
#        가 형제 스위트에 캐시를 흘리지도 않는다 — 순서 의존을 **양방향**으로 끊는다.
#     ② **서술을 단언으로 승격** — `invoke_run` 이 `subprocess.run`/`Popen` 을 가로채
#        실행을 **차단**하고 argv 를 기록한 뒤 허용집합(`ALLOWED_SUBPROCESS`)과 `==` 로
#        대조한다. 이 명제가 다음에 틀리면 스위트가 **RED** 가 된다(서술은 절대 RED 가
#        되지 않는다 — 그게 F-CR-401 의 본질이었다). production 표면 신설 **0**.
#     비공허성: 기록기 자체가 죽은 계측이 아님은 `TestSubprocessSurface` 의 lazy-해소
#        케이스가 **비어있지 않은** 기록을 단언해 증명한다.
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
# ★ 분해 기대값은 **리터럴 고정**이다 — production `_parse_channel()` 로 유도하면
#   그 분해가 뒤바뀌는 mutant 에서 기대값도 함께 뒤집혀 오라클이 조용히 죽는다
#   (F-CR-406 이 잡은 위치 판별력 0 과 동종의 함정). 손으로 분해해 박아둔다.
CHANNEL_REPO = "qadev-harness/none"
CHANNEL_NUMBER = "1"

# ── 실 subprocess 허용집합 (F-CR-401 ② — 서술이 아니라 단언) ──────────────────────
#   `invoke_run` 은 `subprocess.run`/`Popen` 을 가로채 **실행을 차단**하고 argv 를 기록한
#   뒤 이 집합과 `==` 로 대조한다. 기본 형상(workspace 접두 명시 주입)의 실측치 = **0건**.
ALLOWED_SUBPROCESS = frozenset()
#   접두를 주입하지 **않으면** `_workspace_prefixes()` lazy 해소가 내는 유일한 site.
#   (git 바이너리명은 production override 상수에서 취한다 — 본 단언의 load-bearing 부분은
#    "worktree list --porcelain 이 정확히 1건" 이지 바이너리명이 아니다.)
LAZY_WORKSPACE_SITE = frozenset({
    (sut.base.GC_GIT_BIN, "-C", ".", "worktree", "list", "--porcelain"),
})

_DONE_RE = re.compile(
    r"\[scheduled-task\] DONE: observed=(\d+) new=(\d+) posted=(\d+) halted=(\d+)"
)
_FACT_LINE_PREFIX = "- 선언="


def _argv_tuple(args, kwargs):
    """`subprocess.run(...)` / `Popen(...)` 의 첫 인자를 비교 가능한 tuple 로."""
    raw = args[0] if args else kwargs.get("args")
    if isinstance(raw, (list, tuple)):
        return tuple(str(x) for x in raw)
    return (str(raw),)


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


# 이 모듈이 실 상태 디렉터리에 만들 수 있는 파일의 소유 접두 (HEARTBEAT_FILE·STOP_FLAG_LOCAL 공통)
OWNED_STATE_PREFIX = "scheduled-task"


def owned_gc_state_files():
    """실 `GC_STATE_DIR` 안 **모듈 소유 접두**(`scheduled-task*`) 파일 상대경로 집합.

    ★ **읽기 전용 walk 만** 한다 — 생성·삭제·수정 0 (실 사용자 상태 무접촉).
    ★ 소유 접두 한정 이유(판정 3): `~/.claude/worktree-gc-state` 는
      `session-start-gc-catchup` 등이 공유하는 **가변 디렉터리**라, 전면 스냅샷 동등
      단언은 병렬 세션·다른 훅의 정상 활동만으로도 깨지는 flaky 오라클이 된다.
      본 모듈이 만들 수 있는 이름 공간으로 좁혀야 신호가 남는다.
    ★ 홈 접근 불가(디렉터리 부재·권한) → `None` (graceful skip — 단언을 건너뛴다).
    """
    state_dir = getattr(sut, "GC_STATE_DIR", None)
    if not state_dir:
        return None
    try:
        if not os.path.isdir(state_dir):
            return set()          # 디렉터리 자체가 없으면 소유 파일도 0 (정상 정의역)
        out = set()
        for dirpath, _dirnames, filenames in os.walk(str(state_dir)):
            for fn in filenames:
                rel = os.path.relpath(os.path.join(dirpath, fn), str(state_dir))
                rel = rel.replace(os.sep, "/")
                if rel.split("/")[0].startswith(OWNED_STATE_PREFIX) or \
                        os.path.basename(rel).startswith(OWNED_STATE_PREFIX):
                    out.add(rel)
        return out
    except OSError:
        return None               # 권한 등 접근 불가 — 판정 불가로 정직 처리


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


def invoke_run(tmp_path, observations, chan, channel=CHANNEL,
               task="qadev-harness", run_id="r-001",
               seal_workspace_prefixes=True, allow_subprocess=ALLOWED_SUBPROCESS):
    """`sut.run()` 을 **완주**시키고 산출을 구조화해 반환한다.

    격리 4중:
      ① `ENV_HEARTBEAT_FILE` → tmp (실 사용자 생존 신호 무접촉 — 사후 단언)
      ② `STOP_FLAG_LOCAL` → tmp 의 **부재 경로** (실 F2 플래그가 존재하면 전 케이스가
         정지 분기로 새어 조용히 거짓통과한다 — 그 함정 차단)
      ③ `tempfile.tempdir` → tmp (`post_report` 의 `--body-file` 임시파일까지 tmp 안)
      ④ `subprocess.run`/`Popen` → **기록 후 차단** (실행 0). 아래 참조.

    workspace 접두 캐시 봉인 (`seal_workspace_prefixes`, F-CR-401 ①):
      `sut._workspace_prefix_cache` 는 **모듈 전역**이고 이를 리셋하는 test/conftest 가
      repo 전체 0건이라, 손대지 않으면 pytest 세션의 **최초 해소자 승리** 순서 의존이
      된다(= 실 subprocess 발생 여부가 테스트 실행 순서에 좌우된다). 기본값은 tmp 접두를
      **명시 주입**해 lazy 해소를 제거하고, 종료 시 **원래 값으로 복원**해 형제 스위트로
      캐시가 새지 않게 한다 — 순서 의존을 양방향으로 끊는다.
      ★ production 측 "lazy 폴백 허용 여부"는 설계 판정 대상이며 여기서 손대지 않는다.

    실 subprocess 단언 (`allow_subprocess`, F-CR-401 ②):
      가로챈 `subprocess.run`/`Popen` 은 **실행하지 않고** argv 만 기록한다(차단 = 실
      gh·git 도달 0 의 구조적 보증). 기록 집합을 `allow_subprocess` 와 `==` 로 대조하므로,
      허용집합 밖 subprocess 가 하나라도 늘면 **RED** 가 된다.

    사후 보편 단언 (공허 통과 차단):
      · `rc == 0` (INV-F)
      · 실 heartbeat 파일 무변화
      · `collect_observations` 정확히 1회 호출 (fixture seam 실효)
      · 채널 지정 시 gh 포트 **호출 기록 비어있지 않음**
      · 실 subprocess argv 집합 == `allow_subprocess`
      · 상태 잔여 2축 (F-CR-403: 1차 축소 → 판정 3 부분 확장)
          ① tmp **root** 하위 파일 = heartbeat 뿐 (임시파일 누수 4건 kill)
          ② 실 `GC_STATE_DIR` 안 **소유 접두**(`scheduled-task*`) 신규 파일 0
             — 읽기 전용 walk, 홈 접근 불가 시 graceful skip.
        ☞ 두 축 합쳐도 "로컬 상태 저장 0" **전칭**은 아니다: 소유 접두 밖 이름이나
          제3의 경로에 쓰면 여전히 안 보인다 (아래 정직 천장 참조).
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

    posted_before = len(chan.posted)
    real_before = real_heartbeat_state()
    owned_before = owned_gc_state_files()      # 읽기 전용 스냅샷 (판정 3 — 실 상태 무접촉)
    out, err = io.StringIO(), io.StringIO()

    seen_subprocess = []

    def _spy_run(*args, **kwargs):
        seen_subprocess.append(_argv_tuple(args, kwargs))
        return subprocess.CompletedProcess(
            args[0] if args else kwargs.get("args"), 127,
            stdout="", stderr="[qadev-harness] subprocess 차단",
        )

    def _spy_popen(*args, **kwargs):
        seen_subprocess.append(_argv_tuple(args, kwargs))
        raise OSError("[qadev-harness] Popen 차단")

    prev_prefix_cache = sut._workspace_prefix_cache
    try:
        with mock.patch.dict(os.environ, {sut.ENV_HEARTBEAT_FILE: hb_path}):
            for k in (sut.ENV_CHANNEL, sut.ENV_TASK_NAME, sut.ENV_RUN_ID, sut.GH_BIN_ENV):
                os.environ.pop(k, None)      # 앰비언트 설정 유입 차단 (patch.dict 가 복원)
            if seal_workspace_prefixes:
                sut._set_workspace_prefixes([root])   # 권위값 명시 주입 (lazy 해소 제거)
            else:
                sut._workspace_prefix_cache = None    # lazy 해소 경로 강제 (site 실측용)
            with mock.patch.object(sut, "STOP_FLAG_LOCAL", stop_local), \
                    mock.patch.object(tempfile, "tempdir", root), \
                    mock.patch.object(sut, "collect_observations",
                                      return_value=list(observations)) as spy_collect, \
                    mock.patch.object(sut, "_gh", chan), \
                    mock.patch.object(subprocess, "run", _spy_run), \
                    mock.patch.object(subprocess, "Popen", _spy_popen):
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    rc = sut.run(argv)
    finally:
        sut._workspace_prefix_cache = prev_prefix_cache   # 형제 스위트로 캐시 누수 0

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

    assert set(seen_subprocess) == set(allow_subprocess), (
        "실 subprocess 호출 집합이 허용집합과 불일치 (F-CR-401 단언).\n"
        "  실측: %r\n  허용: %r\n"
        "허용집합 밖 site 가 늘었다면 `_gh` 치환만으로는 실 바이너리·네트워크 도달 0 이 "
        "더 이상 보장되지 않는다 — 헤더의 근거 명제부터 다시 실측하라."
        % (sorted(seen_subprocess), sorted(allow_subprocess))
    )

    # 정의역 축 ①: tmp root 하위 임시파일 누수 0 (`--body-file` 미삭제 등 4건 kill).
    residue = files_under(root)
    expected_files = {"heartbeat.epoch"}
    assert residue == expected_files, (
        "tmp root 하위 파일이 %r (기대 %r) — 임시파일이 누수됐거나 heartbeat 기록 경로가 "
        "소실됐다" % (sorted(residue), sorted(expected_files))
    )

    # 정의역 축 ②: 실 `GC_STATE_DIR` 안 **모듈 소유 접두** 신규 파일 0 (판정 3 확장).
    #   축 ① 단독이면 dedup 캐시를 `GC_STATE_DIR/scheduled-task-*` 에 쓰는 mutant 가
    #   **생존**한다 — tmp root 밖이라 안 보이기 때문이다. 그 사각을 여기서 덮는다.
    #   ★ seam 신설(GC_STATE_DIR 리디렉트)은 **기각**됐다: 그 경로를 env 로 옮기면
    #     F2 긴급 정지 플래그(`STOP_FLAG_LOCAL`)가 **함께 이동**해 env 만으로 정지
    #     장치를 무력화할 수 있게 되는 fail-unsafe flip 이다. 그래서 리디렉트 대신
    #     **읽기 전용 walk 로 실 디렉터리를 관측**한다.
    if owned_before is not None:
        owned_after = owned_gc_state_files()
        if owned_after is not None:
            new_owned = owned_after - owned_before
            assert not new_owned, (
                "실 GC_STATE_DIR 에 모듈 소유(`%s*`) 신규 파일이 생겼다: %r\n"
                "  dir=%s\n"
                "로컬 상태 저장은 INV-C 위반이다 (dedup 상태 저장소 = append-only 채널 자신). "
                "tmp root 정의역(축 ①)만으로는 이 축이 보이지 않는다."
                % (OWNED_STATE_PREFIX, sorted(new_owned),
                   getattr(sut, "GC_STATE_DIR", "?"))
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

        # 채널 인자가 **올바른 위치**로 전달됐는가 (owner_repo ↔ number 뒤바꿈 kill)
        #   ★ 이전 판본은 `"qadev-harness/none" in argv and "1" in argv` 였다 — 리스트
        #     **멤버십**이라 두 값이 서로 자리를 바꿔도 둘 다 여전히 리스트에 있어
        #     통과했다(판별력 0, 구현리뷰 iter4 F-CR-406). 형상 `==` 로 교체한다.
        comment_argv = chan.commented()[0]
        assert comment_argv[:6] == [
            "issue", "comment", CHANNEL_NUMBER, "--repo", CHANNEL_REPO, "--body-file",
        ], "gh comment argv 형상 불일치 (number↔repo 위치 확인): %r" % comment_argv
        assert len(comment_argv) == 7, (
            "gh comment argv 길이 %d (기대 7 — 말미는 --body-file 경로): %r"
            % (len(comment_argv), comment_argv)
        )

        # 형제 축: 조회 argv 도 같은 위치 계약을 진다 (분해가 뒤바뀌면 양쪽이 함께 깨진다)
        view_argv = chan.viewed()[0]
        assert view_argv == [
            "issue", "view", CHANNEL_NUMBER, "--repo", CHANNEL_REPO, "--json", "comments",
        ], "gh view argv 형상 불일치 (number↔repo 위치 확인): %r" % view_argv

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

        ★ 상태 무저장(INV-B/INV-C) **정황**: 두 실행 사이에 tmp root 하위 상태 파일이
          하나도 생기지 않는데 잔여분이 정확히 회수된다 — 회수 근거가 로컬 커서가 아니라
          채널 자신이라는 쪽에 무게가 실린다.
          ☞ 정의역 한정 (F-CR-403 1차): `invoke_run` 이 단언하는 것은 **tmp root 하위**
            파일 = heartbeat 뿐이다. production `GC_STATE_DIR` 축은 미측정이므로 이것은
            "로컬 상태 저장소 0" **전칭의 증명이 아니다**. 이 케이스가 실제로 kill 하는
            것은 상한 절단 제거 mutant 이고, 상태 무저장은 그 정의역 안의 정황이다.
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


# ═══════════════════════ 실 subprocess 표면 (F-CR-401 승격 단언) ═════════════════
class TestSubprocessSurface:
    """헤더의 "실 subprocess 표면" 명제를 **서술이 아니라 오라클**로 둔다.

    이전 판본의 결함은 문면 오류가 **아니라** 구조였다 — 어떤 오라클도 서술층을
    정의역으로 삼지 않아, 명제가 틀려도 스위트가 RED 가 될 방법이 없었다.
    """

    def test_run_executes_zero_real_subprocess(self, tmp_path):
        """기본 형상(접두 명시 주입)에서 실 subprocess **0건**.

        mutant kill: 허용집합 밖 subprocess 를 1건이라도 도입 ⇒ RED
          (예: `_normalize_paths` 에 임의 `subprocess.run` 삽입).
        비공허 앵커: 조기 반환이 아니라 **발화까지 완주**한 실행에서 0건이어야 한다 —
          gh 포트 호출 2회(view+comment)와 `posted=1` 로 완주를 확증한다.
        """
        chan = FakeChannel()

        r = invoke_run(tmp_path, make_obs_list(2), chan)   # 내부에서 == ALLOWED 단언

        assert len(chan.calls) == 2, "gh 포트 호출 %d회 (기대 2: view+comment)" % len(chan.calls)
        assert (r.observed, r.new, r.posted, r.halted) == (2, 2, 1, 0), (
            "완주 앵커 불일치: observed=%d new=%d posted=%d halted=%d"
            % (r.observed, r.new, r.posted, r.halted)
        )

    def test_lazy_workspace_prefix_resolution_is_the_remaining_site(self, tmp_path):
        """접두를 주입하지 **않으면** lazy 해소가 실 subprocess 를 정확히 1건 낸다.

        ★ 이 케이스가 두 가지를 동시에 한다:
          (a) **기록기 비공허성 증명** — 허용집합이 비어있지 않은 쪽으로도 `==` 가 맞는지
              보이므로, 기록기가 "아무것도 못 잡는 죽은 계측" 이 아님이 확정된다.
              (이게 없으면 `== frozenset()` 단언은 기록기가 고장나도 항상 통과한다.)
          (b) 헤더가 주장하는 **실측 site 를 그 자리에서 재현** — 문면이 낡으면 RED.

        실행은 차단되므로 실제 `git` 은 돌지 않는다(기록만).

        ★ fallback 서술 정정 (구현리뷰 iter5 F-CR5-05): 직전 판본은 *"해소 실패 시
          production 은 `except Exception → ()` 로 떨어지고 3단 가드가 불변식을 유지"*
          라고 적었다 — **실측과 다르다**. 기록기는 예외를 던지지 않고 `returncode=127` 의
          `CompletedProcess` 를 돌려주므로 `_workspace_prefixes()` 의 `except` 절은
          **한 번도 타지 않는다**(`default_scan_roots` 실측: 예외 0). 결과 캐시도 `()` 가
          아니라 **비어있지 않은 접두 tuple**이며, 즉 이 케이스에서 lazy 해소는 **성공**한다.
          `run()` 이 완주하는 이유는 fallback 이 작동해서가 아니라 **해소가 그냥 성공하기
          때문**이다. (`except → ()` 경로는 production 에 실재하지만 이 케이스의 정의역이
          아니며, 여기서 그 경로가 검증됐다고 읽어서는 안 된다.)
        """
        chan = FakeChannel()

        r = invoke_run(tmp_path, make_obs_list(2), chan,
                       seal_workspace_prefixes=False,
                       allow_subprocess=LAZY_WORKSPACE_SITE)

        assert len(chan.posted) == 1, "발화 개체 %d (기대 1 — 이 축도 완주한다)" % len(chan.posted)
        assert (r.observed, r.new, r.posted, r.halted) == (2, 2, 1, 0)

    def test_prefix_cache_is_restored_so_sibling_order_is_free(self, tmp_path):
        """캐시 봉인이 **양방향**인가 — harness 가 세션 전역 캐시를 남기지 않는다.

        남기면 형제 스위트의 실 subprocess 발생 여부가 본 파일의 실행 순서에 좌우된다
        (`_workspace_prefix_cache` 리셋 fixture 는 repo 전체 0건).
        """
        before = sut._workspace_prefix_cache

        invoke_run(tmp_path, make_obs_list(1), FakeChannel())

        assert sut._workspace_prefix_cache is before, (
            "harness 가 workspace 접두 캐시를 세션에 흘렸다: before=%r after=%r"
            % (before, sut._workspace_prefix_cache)
        )


# ═══════════════════════ 정직 천장 (본 harness 가 봉인하지 않는 것) ═══════════════
# · 본 harness 는 `_gh` **아래**(실 gh 바이너리 argv 수용성 · GitHub API 응답 형상 ·
#   rate limit · 권한)를 검증하지 않는다. 그 축은 live 실측(AC-1) 소관이며 미측정이다.
# · `--body-file` 경유 한글 라운드트립은 여기서 UTF-8 로 읽어 확인하지만, 실 gh 의
#   Windows argv mangling 은 대상 밖이다.
# · subprocess 기록기의 정의역은 `subprocess.run` / `subprocess.Popen` **두 진입점**이다.
#   `os.system` · `os.popen` · `os.spawn*` · C 확장이 직접 내는 프로세스는 잡지 못한다.
#   따라서 "실 subprocess 0" 은 **그 두 진입점에 한한 실측**이지 프로세스 생성 전칭
#   봉인이 아니다 (`subprocess` 고수준 API 인 `call`/`check_call`/`check_output` 은 내부적으로
#   이 둘을 거치므로 커버된다 — ADR-119 검사연극 금지).
# · 상태 잔여 단언의 정의역은 (tmp root 전량) ∪ (실 `GC_STATE_DIR` 안 `scheduled-task*`)
#   두 축뿐이다. 소유 접두 **밖** 이름으로 쓰거나 제3의 경로(레지스트리·다른 홈 하위·
#   원격)에 쓰는 상태 저장은 여전히 관측되지 않는다. 접두 한정은 그 디렉터리가 다른
#   훅과 공유되는 가변 디렉터리라 전면 스냅샷이 flaky 하기 때문에 택한 **의도된 좁힘**
#   이며, 따라서 "로컬 상태 저장 0(INV-C)" 을 전칭으로 봉인하지 않는다.
#   - 축 ② 는 **delta 오라클**이다: 파일이 한 번 생기면 이후 호출의 before 스냅샷에
#     포함되므로, 한 세션 안에서 같은 위반을 **반복 검출하지는 않는다**(실측: 위반
#     mutant 에서 첫 테스트 1건만 RED). 스위트를 붉게 만들기엔 충분하지만 "발생 횟수"
#     를 세는 계측은 아니다.
#   - 축 ② 는 실 디렉터리를 보므로, 테스트 실행 중 **다른 프로세스**가 `scheduled-task*`
#     를 새로 만들면 원리적으로 거짓 RED 가 가능하다(실 스케줄 작업 동시 구동 등).
#     이는 기존 `real_heartbeat_state()` 단언이 이미 지고 있던 노출과 같은 종류이며,
#     접두 한정이 그 표면을 최소화한 결과다(전면 스냅샷 대비).
# · 따라서 본 파일의 GREEN 은 "발화가 실 채널에 착지한다" 를 봉인하지 않는다 —
#   봉인 대상은 `run()` 의 발화 **분기 로직**뿐이다 (ADR-119 검사연극 금지).

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
