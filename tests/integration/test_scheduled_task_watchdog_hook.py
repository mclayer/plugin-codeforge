#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tests/integration/test_scheduled_task_watchdog_hook.py — watchdog hook 판독 오라클
#
# 대상 SUT: hooks/session-start-scheduled-task-watchdog (bash, SessionStart hook)
#
# 계약 5 케이스 (구현리뷰 iter2 F-6 — ArchitectPL 이 §8.1 커버리지 정의역 결손으로 판정):
#   ① absent   (heartbeat 파일 부재 = **미채택**) → 발화 **0**  (F-CR5-06 판정 반영)
#   ② invalid  (정수 파싱 불능 내용)         → 발화 1줄
#   ③ stale    (age > threshold, 기본 172800) → 발화 1줄
#   ④ fresh    (age <= threshold)           → 발화 **0**  ← 대조군(비공허성의 핵심)
#   ⑤ bypass   (BYPASS_SCHEDULED_TASK_WATCHDOG=1) → audit 1줄 + 판독 미수행
#   공통: exit 0 (SessionStart hook 이 세션을 죽이지 않는다)
#
# ★ 발화 정의역 = **채택자 한정** (구현리뷰 iter5 F-CR5-06, ArchitectPL 설계 판정):
#   본 hook 은 전 consumer 세션에 등록되므로 `absent → 발화` 는 **미채택 환경 전체**가
#   매 세션 1줄을 받는다는 뜻이었다. 미채택 환경의 heartbeat 부재는 사망이 아니라
#   정상이며, 그것을 사망 신호로 읽는 것은 관측 **대상의 부재**를 관측의 **실패**로
#   오분류하는 것이다. "채택했는데 죽었다" 는 ②③ 이 이미 담당한다.
#   ☞ 대가(구조적 무음): "채택했으나 1회도 실행되지 않음" class 는 heartbeat 부재만으로
#     판별 불가다 — 채택 표식이 유일 근거이며 표식 부재 시 무음이다(hook 주석에도 기재).
#
# ★ ①④ 두 무발화 케이스만으로는 "항상 무발화" 구현이 통과한다 — 그래서 ②③⑤ 의 발화
#   단언이 짝으로 필요하고, 반대로 ①④ 가 없으면 "항상 발화" 구현이 통과한다.
#   양방향 대조군이 둘 다 있어야 오라클에 판별력이 있다.
#
# ★ 격리: hook 은 `GC_STATE_DIR="${HOME:-/tmp}/.claude/…"` 를 **런타임에** 평가하므로
#   env HOME override 로 격리가 실제 성립한다(ArchitectPL 실측). python
#   `expanduser()` 가 import 시점에 실 홈을 확정하는 함정(§8.3 실 채널 사고의 근인)과
#   **disjoint** 한 성질이다. 실 `~/.claude/worktree-gc-state/` 는 읽지도 쓰지도 않는다.
#
# ★ 상한 (over-claim 차단): 이 오라클이 검사하는 것은 **판독 로직뿐**이다.
#   실 스케줄 작업의 사망·stall 재현은 §8.0-b **L1 = SUT 아님**이라 정의역 밖이며,
#   따라서 **§8.3 class (i)·(ii) 의 미판정 상태를 바꾸지 않는다.** 이 파일의 GREEN 을
#   "스케줄 작업 생존이 검증됐다" 로 읽어서는 안 된다 — 읽은 값을 옳게 판정하는지만 본다.

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
HOOK_PATH = REPO_ROOT / "hooks" / "session-start-scheduled-task-watchdog"

DEFAULT_THRESHOLD = 172800          # hook 기본 임계값(초) — 발화 줄의 threshold_seconds 로 재확인
MARKER = "[scheduled-task-watchdog]"
FACT_RE = re.compile(
    r"^\[scheduled-task-watchdog\] last_run_epoch=(\S+) age_seconds=(\S+) threshold_seconds=(\S+)$"
)
BYPASS_RE = re.compile(
    r"^\[scheduled-task-watchdog\] bypass env BYPASS_SCHEDULED_TASK_WATCHDOG=1$"
)


# ══════════════════════════ working-bash 해석 (false-oracle 봉인) ══════════════
def _candidate_bashes():
    """Windows Git Bash 절대경로 우선(WSL relay 회피) → PATH 순. ubuntu CI 는 /usr/bin/bash."""
    cands = []
    for p in (
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
    ):
        if os.path.exists(p):
            cands.append(p)
    which = shutil.which("bash")
    if which and which not in cands:
        cands.append(which)
    return cands


def _resolve_working_bash():
    """실제로 round-trip 하는 bash 만 채택 (Windows WSL relay = 빈출력 → 거짓 PASS 봉인)."""
    for b in _candidate_bashes():
        try:
            r = subprocess.run(
                [b, "-c", "printf '__cfp2949_probe__'"],
                capture_output=True, text=True, encoding="utf-8", timeout=30,
            )
        except Exception:      # noqa: BLE001 — 후보 탐색이라 어떤 실패든 다음 후보로
            continue
        if r.returncode == 0 and r.stdout.strip() == "__cfp2949_probe__":
            return b
    return None


WORKING_BASH = _resolve_working_bash()

# ★ 비공허성 가드: **CI(비-Windows)에서 bash 부재 = skip 이 아니라 FAIL**.
#   skip 을 허용하면 이 파일 전체가 CI 에서 조용히 0 검사로 붕괴한다(born-dead 재발).
#   로컬 Windows 에서 신뢰 가능한 bash 가 없을 때만 skip 을 허용한다.
if WORKING_BASH is None and sys.platform != "win32":
    raise RuntimeError(
        "round-trip 검증을 통과한 bash 부재 — 이 플랫폼(CI 포함)에서는 skip 을 허용하지 "
        "않는다. watchdog hook 오라클이 조용히 0 검사가 되는 것을 막기 위한 fail-closed."
    )

_SKIP_NO_BASH = pytest.mark.skipif(
    WORKING_BASH is None,
    reason="round-trip 검증 통과 bash 부재 (로컬 Windows 한정 허용 — CI 는 위에서 FAIL)",
)


# ══════════════════════════ 실행 헬퍼 ═════════════════════════════════════════
def _run_hook(home_dir, extra_env=None, timeout=60):
    """tmp HOME 으로 격리해 hook 실행 → CompletedProcess.

    ★ HOME 은 forward-slash 로 넘긴다 — Git Bash 가 `C:/...` 를 그대로 다루기 때문이며,
      backslash 경로는 bash 문자열에서 escape 로 오독될 여지가 있다.
    """
    assert WORKING_BASH is not None
    env = dict(os.environ)
    # 실 사용자 상태로 새는 축을 전부 차단 (HOME 만이 hook 의 상태 경로 결정자다)
    env["HOME"] = str(home_dir).replace("\\", "/")
    for leak in ("USERPROFILE", "BYPASS_SCHEDULED_TASK_WATCHDOG",
                 "SCHEDULED_TASK_WATCHDOG_THRESHOLD_SECONDS"):
        env.pop(leak, None)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [WORKING_BASH, str(HOOK_PATH)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=timeout,
    )


def _marker_lines(cp):
    """stderr 중 hook 마커 줄만 (다른 잡음 줄과 분리)."""
    return [ln.strip() for ln in (cp.stderr or "").splitlines() if MARKER in ln]


def _prepare_home(tmp_path, content=None):
    """tmp HOME + 상태 디렉터리 생성. content 가 None 이면 heartbeat 파일을 만들지 않는다."""
    state_dir = tmp_path / ".claude" / "worktree-gc-state"
    state_dir.mkdir(parents=True, exist_ok=True)
    hb = state_dir / "scheduled-task-last-run.epoch"
    if content is not None:
        hb.write_text(content, encoding="utf-8", newline="\n")
    return tmp_path, hb


# ══════════════════════════ ① absent (미채택 = 무발화) ═══════════════════════
@_SKIP_NO_BASH
def test_watchdog_absent_heartbeat_reports_zero_lines(tmp_path):
    """① heartbeat 파일 부재 = **미채택** → 발화 **0** · exit 0 (F-CR5-06 판정).

    ★ 기대가 뒤집힌 케이스다. 직전 판본은 `absent → 발화 1줄` 이었고, 그 형상은 본 hook 이
      **전 consumer 세션에 등록**되므로 스케줄 작업을 채택하지 않은 환경 전부가 매 세션
      1줄을 받는다는 뜻이었다(blast radius 미선언). 미채택 환경의 heartbeat 부재는
      사망이 아니라 정상이며, "채택했는데 죽었다" 는 ②(invalid)·③(stale)이 담당한다.

    ★ 구조적 무음(대가, 은폐 금지): "채택했으나 1회도 실행되지 않음" class 는 heartbeat
      부재만으로 판별 불가다 — 채택 표식이 유일 근거이고 표식이 없으면 무음이다.
      이 테스트의 GREEN 을 "미실행이 없다" 로 읽어서는 안 된다.

    mutant kill: `absent → should_report=true` 복원 ⇒ **이 테스트만 RED**
      (②③⑤ 는 무손상 — 그 분기를 건드리지 않으므로).
    """
    home, hb = _prepare_home(tmp_path, content=None)
    assert not hb.exists(), f"전제 붕괴: heartbeat 파일이 존재한다 ({hb})"

    cp = _run_hook(home)

    assert cp.returncode == 0, f"SessionStart hook 은 exit 0 이어야 한다: rc={cp.returncode}"
    lines = _marker_lines(cp)
    assert lines == [], (
        f"미채택(heartbeat 부재) 환경은 무발화여야 한다, 실제: {lines}"
    )
    # 비공허 앵커: 무발화가 "hook 이 아예 안 돌아서" 가 아님을 같은 홈에서 확증한다 —
    #   같은 형상에 stale heartbeat 만 심으면 1줄이 나온다(판독·판정은 살아 있다).
    hb.write_text("%d\n" % (int(time.time()) - 200000), encoding="utf-8", newline="\n")
    cp2 = _run_hook(home)
    lines2 = _marker_lines(cp2)
    assert len(lines2) == 1 and FACT_RE.match(lines2[0]), (
        "대조 실패: 같은 홈에 stale heartbeat 를 심었는데 발화가 없다 — 위 무발화가 "
        f"'미채택 판정' 이 아니라 'hook 무동작' 이었을 수 있다. 실제: {lines2}"
    )


# ══════════════════════════ ② invalid ════════════════════════════════════════
@_SKIP_NO_BASH
def test_watchdog_invalid_heartbeat_reports_one_line(tmp_path):
    """② 정수 파싱 불능 내용 → 사실 1줄 발화 · exit 0.

    mutant kill: 판정부 `should_report=true` 3 분기 제거 ⇒ RED.
    """
    home, hb = _prepare_home(tmp_path, content="not-an-epoch\n")
    assert hb.read_text(encoding="utf-8").strip() == "not-an-epoch", "전제 붕괴: fixture 내용 불일치"

    cp = _run_hook(home)

    assert cp.returncode == 0, f"SessionStart hook 은 exit 0 이어야 한다: rc={cp.returncode}"
    lines = _marker_lines(cp)
    assert len(lines) == 1, f"발화 1줄 기대, 실제 {len(lines)}줄: {lines}"
    m = FACT_RE.match(lines[0])
    assert m is not None, f"사실 줄 형식 불일치: {lines[0]!r}"
    assert m.group(1) == "invalid", f"last_run_epoch=invalid 기대, 실제 {m.group(1)!r}"
    # ★ 파싱 불능 내용이 산출에 그대로 실려 나가지 않는다 (판독값 누출 0)
    assert "not-an-epoch" not in (cp.stderr or ""), "파싱 불능 원문이 산출에 실렸다"


# ══════════════════════════ ③ stale ══════════════════════════════════════════
@_SKIP_NO_BASH
def test_watchdog_stale_beyond_threshold_reports_one_line(tmp_path):
    """③ age > threshold(기본 172800) → 사실 1줄 발화 · exit 0.

    ★ 비공허성 앵커: 발화된 `age_seconds` 가 **주입한 epoch 에서 유도된 값**임을 대역으로
      확인한다(상수 발화·미판독 구현 배제). `threshold_seconds` 로 기본값 적용도 재확인.

    mutant kill: 판정부 `should_report=true` 3 분기 제거 ⇒ RED.
    """
    injected_age = DEFAULT_THRESHOLD + 27200        # = 200000s (임계 초과가 자명한 값)
    now = int(time.time())
    home, hb = _prepare_home(tmp_path, content="%d\n" % (now - injected_age))

    cp = _run_hook(home)

    assert cp.returncode == 0, f"SessionStart hook 은 exit 0 이어야 한다: rc={cp.returncode}"
    lines = _marker_lines(cp)
    assert len(lines) == 1, f"발화 1줄 기대, 실제 {len(lines)}줄: {lines}"
    m = FACT_RE.match(lines[0])
    assert m is not None, f"사실 줄 형식 불일치: {lines[0]!r}"

    assert m.group(3) == str(DEFAULT_THRESHOLD), (
        f"기본 임계값 {DEFAULT_THRESHOLD} 기대, 실제 {m.group(3)!r}"
    )
    reported_age = int(m.group(2))
    assert reported_age > DEFAULT_THRESHOLD, (
        f"임계 초과 상태인데 age_seconds={reported_age} <= {DEFAULT_THRESHOLD}"
    )
    # 비공허성: 주입값에서 유도됐는가 (프로세스 기동 지연 여유 300s)
    assert abs(reported_age - injected_age) <= 300, (
        f"age_seconds={reported_age} 가 주입 age={injected_age} 에서 유도된 값이 아니다 — "
        "hook 이 heartbeat 를 실제로 판독했다는 근거가 없다(상수 발화 의심)"
    )


# ══════════════════════════ ④ fresh (대조군) ═════════════════════════════════
@_SKIP_NO_BASH
def test_watchdog_fresh_heartbeat_reports_zero_lines(tmp_path):
    """④ **대조군** — age <= threshold → 발화 0 · exit 0.

    ★ 이 케이스가 오라클 전체의 비공허성을 짊어진다. ①②③ 만 있으면 `should_report` 를
      무조건 true 로 둔 구현이 전부 통과한다.

    mutant kill: `should_report` 를 무조건 true ⇒ **이 테스트만 RED**.
    """
    now = int(time.time())
    home, hb = _prepare_home(tmp_path, content="%d\n" % now)
    assert hb.exists(), "전제 붕괴: fresh heartbeat fixture 부재 — 발화 0 이 공허해진다"

    cp = _run_hook(home)

    assert cp.returncode == 0, f"SessionStart hook 은 exit 0 이어야 한다: rc={cp.returncode}"
    lines = _marker_lines(cp)
    assert lines == [], f"fresh heartbeat 는 무발화여야 한다, 실제: {lines}"

    # 부수효과 0 — hook 은 판독만 한다 (상태 디렉터리에 새 파일 0, 내용 무변경)
    state_dir = hb.parent
    assert [p.name for p in state_dir.iterdir()] == [hb.name], (
        f"hook 이 상태 디렉터리에 부수 산출을 남겼다: {[p.name for p in state_dir.iterdir()]}"
    )
    assert hb.read_text(encoding="utf-8").strip() == str(now), "hook 이 heartbeat 내용을 변경했다"


# ══════════════════════════ ⑤ bypass ═════════════════════════════════════════
@_SKIP_NO_BASH
def test_watchdog_bypass_emits_audit_and_skips_read(tmp_path):
    """⑤ BYPASS=1 → audit 1줄 + 판독 미수행 · exit 0.

    ★ 형상: **stale heartbeat 를 심어 둔 채로** bypass 한다. 판독·판정이 돌았다면 반드시
      사실 줄(`last_run_epoch=`)이 나오므로, 그 줄의 부재가 "판독 미수행" 의 증거다.
      bypass 를 빈 홈에서 시험하면 사실 줄 부재가 bypass 때문인지 판독 결과 때문인지
      구별되지 않아 오라클이 공허해진다.

    ★ 정직 천장: "판독 미수행" 은 **판독의 관측 가능한 귀결이 0** 임으로 잰다 —
      파일 open syscall 을 직접 계측하지는 않는다(bash hook 에 그 계측 seam 이 없다).
    """
    now = int(time.time())
    home, hb = _prepare_home(tmp_path, content="%d\n" % (now - 200000))   # stale = 발화 조건

    # 전제 확인: bypass 가 없으면 이 형상은 사실 1줄을 낸다 (대조 근거)
    baseline = _run_hook(home)
    assert len(_marker_lines(baseline)) == 1, (
        f"전제 붕괴: bypass 없이 발화 1줄이 나와야 한다, 실제: {_marker_lines(baseline)}"
    )

    cp = _run_hook(home, extra_env={"BYPASS_SCHEDULED_TASK_WATCHDOG": "1"})

    assert cp.returncode == 0, f"SessionStart hook 은 exit 0 이어야 한다: rc={cp.returncode}"
    lines = _marker_lines(cp)
    assert len(lines) == 1, f"audit 1줄 기대, 실제 {len(lines)}줄: {lines}"
    assert BYPASS_RE.match(lines[0]), f"audit 줄 형식 불일치: {lines[0]!r}"
    # 판독 미수행 — 사실 줄이 나오지 않았다 (stale 을 심어 뒀는데도)
    assert "last_run_epoch=" not in (cp.stderr or ""), (
        f"bypass 인데 판독·판정 산출이 나왔다: {cp.stderr!r}"
    )
