#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tests/integration/test_scheduled_task_watchdog_hook.py — watchdog hook 판독 오라클
#
# 대상 SUT: hooks/session-start-scheduled-task-watchdog (bash, SessionStart hook)
#
# 계약 케이스 (구현리뷰 iter2 F-6 — ArchitectPL 이 §8.1 커버리지 정의역 결손으로 판정):
#   ①a absent + 채택 표식 **부재 확정** (미채택) → 발화 **0**
#   ①b absent + 채택 표식 **존재** (채택했는데 한 번도 안 돎) → 발화 1줄
#   ①c absent + **스캔 bound 도달**(파일 상한 소진 ∨ 깊이 상한 밖 내용) = 판정 불가
#       → 발화 1줄 (구현리뷰 iter6 F-CR6-01)
#   ②  invalid  (정수 파싱 불능 내용)         → 발화 1줄
#   ③  stale    (age > threshold, 기본 172800) → 발화 1줄
#   ④  fresh    (age <= threshold)           → 발화 **0**  ← 대조군(비공허성의 핵심)
#   ⑤  bypass   (BYPASS_SCHEDULED_TASK_WATCHDOG=1) → audit 1줄 + 판독 미수행
#   공통: exit 0 (SessionStart hook 이 세션을 죽이지 않는다)
#   ★ 케이스 **개수는 적지 않는다** — 수기 사본이라 늘 때마다 stale 이 된다
#     (구현리뷰 iter6 F-CR6-07 실물: "5 케이스"·"6 케이스" 표기가 실제 7 과 어긋나 있었다).
#     같은 이유로 스캔 bound 상수도 베끼지 않고 `_hook_int_const` 로 hook 에서 판독한다.
#
# ★ 발화 정의역 = **채택자 한정** (구현리뷰 iter5 F-CR5-06, ArchitectPL 설계 판정):
#   본 hook 은 전 consumer 세션에 등록되므로 `absent → 무조건 발화` 는 **미채택 환경
#   전체**가 매 세션 1줄을 받는다는 뜻이었다. 미채택 환경의 heartbeat 부재는 사망이
#   아니라 정상이며, 그것을 사망 신호로 읽는 것은 관측 **대상의 부재**를 관측의
#   **실패**로 오분류하는 것이다.
#
# ★ 표식 판별자 도입 (Orchestrator 지시 1 — 채택자 탐지 회복, **축별로 갈린다**):
#   `absent → 무조건 무발화` 로 두면 "채택했으나 1회도 실행되지 않음" class 가 구조적
#   무음이 되어 **false-negative 를 하나 늘린다**(3-conjunct (ㄴ) 완화 방향 0 미충족).
#   채택 표식을 판별자로 넣어 침묵을 **미채택에만** 적용한다.
#   표식 = `~/.claude/scheduled-tasks/**` 안에 우리 CLI 를 지목하는 태스크 정의
#   (앱이 만드는 **기존 산물**, 신규 파일 0건, scratch 밖 = TTL purge 비대상).
#   ☞ 탐지 회복은 **2 축으로 갈린다**(ADR-172 Amendment 4 A4-2 — 종전 문면은 두 축을
#     한 칸에 뭉쳐 조건 없는 명제처럼 읽히게 뒀다):
#     · **자원 bound 축** — FIX7 이 bound 소진을 "표식 없음" 이 아니라 **판정 불가 →
#       발화**로 좁혀 탐지 손실을 폐쇄했다(A4-1 실측 A·B). 이 축에 한해 조건부가 아니다.
#     · **표식 가시성 축** — (i) 벤더 경로 rename·이전 (ii) sentinel 소실 (iii) 파일 아닌
#       저장형태·다른 HOME: 탐지 손실이 **잔존**한다. pre-FIX6 은 이 형상에서 발화했고
#       현행은 침묵한다(A4-1 실측 E·F). ⇒ 전체 명제는 **여전히 조건부**다.
#     ★ 축 라벨 정정(A4-3): 이 잔여 3종은 종전에 **거짓 발화 축**("침묵 방향이라 거짓
#       발화 없음")으로 라벨돼 있었다. 그 서술은 참이지만 축이 틀렸다 — 실제로는
#       **탐지 축의 손실 경로**(진짜 채택자가 무음이 된다)다. 축을 잘못 붙였기 때문에
#       탐지 회복 주장과 잔여 열거가 모순으로 보이지 않고 병존했다.
#     ★ 저작 규율: "탐지 손실 0" 을 조건 없이 쓰지 않는다 — 축 명시 + 잔존 병기. [ceiling: 금지 대상 문구의 mention]
#     hook 헤더 "정직 천장" 절 = 구현측 SSOT, 결정 SSOT = ADR-172 Amd 4.
#   ☞ **거짓 발화는 제거가 아니라 축소**됐다(A4-2 정직 귀결 3): 표식이 실재해도 스캔이
#     파일 상한 밖·깊이 상한 밖이면 못 보므로(iter6 F-CR6-01) hook 은 그 경우를 "표식
#     없음" 이 아니라 **판정 불가 → 발화**로 결론짓는다. 그 대가로 소음의 정의역이
#     pre-FIX6 의 "전 consumer" → "태스크 정의 200 파일 초과 ∨ depth 4 이상 환경 한정"
#     으로 줄었을 뿐이며, 그 환경은 **미채택인데도 발화**한다(A4-1 실측 C·G).
#     hook 헤더 (iv) 가 SSOT.
#
# ★ 판별력 구조: **무발화** 케이스(①a·④)만으로는 "항상 무발화" 구현이 통과하고,
#   **발화** 케이스(①b·①c·②·③·⑤)만으로는 "항상 발화" 구현이 통과한다. 양방향 대조군이
#   둘 다 있어야 오라클에 판별력이 있다. ①a/①b 는 **같은 heartbeat 상태(absent)** 에서
#   표식만 다르므로, 둘의 결과가 갈린다는 것이 곧 표식 판별자가 살아 있다는 증거다.
#   ①c 는 ①a 와 **표식도 heartbeat 도 같고**(둘 다 부재) 스캔 bound 도달 여부만 다르다 —
#   그 둘이 갈린다는 것이 bound 판별자(판정 불가 ≠ 없음)가 살아 있다는 증거다.
#
# ★ 격리: hook 은 상태 경로를 **런타임에** 유도하므로 env override 로 격리가 실제
#   성립한다(ArchitectPL 실측). python `expanduser()` 가 import 시점에 실 홈을 확정하는
#   함정(§8.3 실 채널 사고의 근인)과 **disjoint** 한 성질이다.
#   ★ 단 유도 축이 **HOME 하나가 아니다** (FIX13 / F-SEC-5 writer 동형화 이후) —
#     Windows 에서는 `USERPROFILE` → `HOMEDRIVE`+`HOMEPATH` 순이다. `_run_hook` 이
#     tmp 를 두 축에 모두 세우고 HOMEDRIVE/HOMEPATH 를 제거하는 이유이며, 그래야
#     실 `~/.claude/worktree-gc-state/` 를 읽지도 쓰지도 않는다는 성질이 유지된다.
#
# ★ 축 어긋남 케이스 (⑥ — FIX13 신설): heartbeat/표식이 writer 축(USERPROFILE)에 있고
#   HOME 이 다른 곳을 가리킬 때 hook 이 **침묵하지 않는지**를 잰다. 종전에는 두 경로가
#   함께 HOME 으로 이동해 "미채택" 으로 떨어져 조용히 무장해제됐다(보안 lane F-SEC-5).
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
    """tmp 홈으로 격리해 hook 실행 → CompletedProcess.

    ★ 경로는 forward-slash 로 넘긴다 — Git Bash 가 `C:/...` 를 그대로 다루기 때문이며,
      backslash 경로는 bash 문자열에서 escape 로 오독될 여지가 있다.

    ★ 격리 축이 **HOME 하나가 아니다** (FIX13 / F-SEC-5 — writer 동형화 이후):
      hook 은 이제 writer(python `expanduser`)와 같은 규칙으로 base 를 유도하므로
      Windows 에서는 `USERPROFILE` → `HOMEDRIVE`+`HOMEPATH` 를 본다. HOME 만 tmp 로
      돌리고 나머지를 그대로 두면 hook 이 **실 사용자 홈**을 읽는다(격리 붕괴 +
      실 상태 판독). 그래서 tmp 를 **두 축에 모두** 세우고 HOMEDRIVE/HOMEPATH 는 제거한다.
      ⇒ 어느 유도 규칙이 적용되든 결과 base 는 tmp 다(플랫폼 판별에 의존하지 않는 격리).
    """
    assert WORKING_BASH is not None
    env = dict(os.environ)
    home_s = str(home_dir).replace("\\", "/")
    env["HOME"] = home_s
    env["USERPROFILE"] = home_s
    for leak in ("HOMEDRIVE", "HOMEPATH", "BYPASS_SCHEDULED_TASK_WATCHDOG",
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


def _prepare_home(tmp_path, content=None, adopted=False):
    """tmp HOME + 상태 디렉터리 생성.

    Args:
        content: None 이면 heartbeat 파일을 만들지 않는다(absent 형상).
        adopted: True 면 **채택 표식**(태스크 정의 + sentinel)을 심는다.
    """
    state_dir = tmp_path / ".claude" / "worktree-gc-state"
    state_dir.mkdir(parents=True, exist_ok=True)
    hb = state_dir / "scheduled-task-last-run.epoch"
    if content is not None:
        hb.write_text(content, encoding="utf-8", newline="\n")
    if adopted:
        _plant_adoption_marker(tmp_path)
    return tmp_path, hb


def _plant_adoption_marker(home_dir, task_name="codeforge-local-residue-observe"):
    """채택 표식 = 앱이 만드는 태스크 정의 산물 (ADR-172 '관련 파일' 형상 그대로).

    `~/.claude/scheduled-tasks/<task-name>/SKILL.md` 안에 ADR-172 §결정 2 박제 프롬프트가
    지목하는 우리 CLI 경로를 담는다 — hook 의 sentinel 이 그 모듈명이다.
    ★ tmp HOME 안에서만 만든다(실 사용자 `~/.claude/scheduled-tasks` 무접촉).
    """
    task_dir = Path(home_dir) / ".claude" / "scheduled-tasks" / task_name
    task_dir.mkdir(parents=True, exist_ok=True)
    prompt = task_dir / "SKILL.md"
    prompt.write_text(
        "codeforge 로컬 잔재 관측 (관측-only · 보고 전용)\n"
        "3. scripts/lib/scheduled_task_reconcile.py 를 실행한다.\n",
        encoding="utf-8", newline="\n",
    )
    return prompt


def _plant_unrelated_task(home_dir, task_name="someone-elses-task"):
    """**우리와 무관한** 스케줄 작업 정의 (sentinel 없음) — 오탐 배제 대조군."""
    task_dir = Path(home_dir) / ".claude" / "scheduled-tasks" / task_name
    task_dir.mkdir(parents=True, exist_ok=True)
    other = task_dir / "SKILL.md"
    other.write_text("매일 아침 뉴스 요약을 만든다.\n", encoding="utf-8", newline="\n")
    return other


# ═══════════════════ 스캔 bound 상수 — hook 에서 **직접 판독** ════════════════════
def _hook_int_const(name):
    """hook 의 `NAME=<정수>` 대입을 판독한다.

    ★ 수기 사본을 두지 않는 이유(구현리뷰 iter6 F-CR6-07 class): 상수를 테스트에 베껴
      적으면 hook 이 값을 바꿨을 때 테스트가 **다른 bound 를 조용히 시험**한다. 판독
      실패는 fail-closed(예외) — 상수가 rename 되면 테스트가 시끄럽게 죽는다.
    """
    text = HOOK_PATH.read_text(encoding="utf-8")
    m = re.search(r"^%s=(\d+)\s*$" % re.escape(name), text, re.MULTILINE)
    if m is None:
        raise AssertionError(
            f"hook 에서 상수 {name} 판독 실패 — bound 오라클이 다른 값을 시험하게 되므로 "
            f"fail-closed 로 중단한다 ({HOOK_PATH})"
        )
    return int(m.group(1))


ADOPTION_MAX_FILES = _hook_int_const("ADOPTION_MAX_FILES")
ADOPTION_MAX_DEPTH = _hook_int_const("ADOPTION_MAX_DEPTH")


def _plant_filler_files(home_dir, count, sub="filler"):
    """sentinel 을 **포함하지 않는** 태스크 정의 파일 `count` 개 (깊이 2, bound 안).

    반환 = 생성 경로 목록. 어느 파일도 sentinel 을 담지 않는다(전제 단언에서 재확인).
    """
    task_dir = Path(home_dir) / ".claude" / "scheduled-tasks" / sub
    task_dir.mkdir(parents=True, exist_ok=True)
    made = []
    for i in range(count):
        p = task_dir / ("f%04d.md" % i)
        p.write_text("뉴스 요약 태스크 %d\n" % i, encoding="utf-8", newline="\n")
        made.append(p)
    return made


def _plant_adoption_marker_deep(home_dir, depth=None):
    """채택 표식을 **깊이 상한 밖**(기본 = MAX_DEPTH + 1)에 심는다.

    `find -maxdepth N -type f` 는 이 파일을 열거하지 않는다 — 즉 sentinel 이 실재하지만
    스캔 정의역 밖이다. 이것이 F-CR6-01 반례 2형상 중 하나다.
    """
    file_depth = (ADOPTION_MAX_DEPTH + 1) if depth is None else depth
    d = Path(home_dir) / ".claude" / "scheduled-tasks"
    for i in range(file_depth - 1):        # 파일이 file_depth 가 되도록 디렉터리를 쌓는다
        d = d / ("d%d" % i)
    d.mkdir(parents=True, exist_ok=True)
    prompt = d / "SKILL.md"
    prompt.write_text(
        "codeforge 로컬 잔재 관측 (관측-only · 보고 전용)\n"
        "3. scripts/lib/scheduled_task_reconcile.py 를 실행한다.\n",
        encoding="utf-8", newline="\n",
    )
    return prompt


def _visible_to_scan(home_dir):
    """hook 의 `find -maxdepth N -type f` 가 실제로 열거하는 파일 목록(전제 검증용)."""
    root = Path(home_dir) / ".claude" / "scheduled-tasks"
    out = []
    for p in root.rglob("*"):
        if p.is_file() and len(p.relative_to(root).parts) <= ADOPTION_MAX_DEPTH:
            out.append(p)
    return out


# ══════════════════ ①a absent + 표식 부재 (미채택 = 무발화) ═══════════════════
@_SKIP_NO_BASH
def test_watchdog_absent_without_adoption_marker_reports_zero_lines(tmp_path):
    """①a heartbeat 부재 + 채택 표식 **부재** = 미채택 → 발화 **0** · exit 0.

    ★ 직전 판본은 `absent → 발화 1줄` 이었고, 그 형상은 본 hook 이 **전 consumer 세션에
      등록**되므로 스케줄 작업을 채택하지 않은 환경 전부가 매 세션 1줄을 받는다는
      뜻이었다(blast radius 미선언). 미채택 환경의 heartbeat 부재는 사망이 아니라 정상이다.

    ★ 이 침묵은 **미채택에만** 적용된다 — 표식이 있으면 ①b 가 발화한다. 그래서 이
      테스트의 GREEN 은 "미실행 탐지를 포기했다" 는 뜻이 **아니다**(직전 판본과의 차이).

    mutant kill: `absent → should_report=true` 복원 ⇒ **이 테스트만 RED**
      (①b②③⑤ 는 무손상 — 그 분기를 건드리지 않으므로).
    """
    home, hb = _prepare_home(tmp_path, content=None, adopted=False)
    assert not hb.exists(), f"전제 붕괴: heartbeat 파일이 존재한다 ({hb})"
    assert not (Path(home) / ".claude" / "scheduled-tasks").exists(), (
        "전제 붕괴: 미채택 형상인데 태스크 정의 디렉터리가 있다"
    )

    cp = _run_hook(home)

    assert cp.returncode == 0, f"SessionStart hook 은 exit 0 이어야 한다: rc={cp.returncode}"
    lines = _marker_lines(cp)
    assert lines == [], (
        f"미채택(표식·heartbeat 모두 부재) 환경은 무발화여야 한다, 실제: {lines}"
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


@_SKIP_NO_BASH
def test_watchdog_absent_with_unrelated_task_reports_zero_lines(tmp_path):
    """①a' **오탐 배제 대조군** — 우리와 무관한 스케줄 작업만 있으면 여전히 무발화.

    ★ 표식을 "디렉터리 존재" 로 두면 이 형상이 거짓 발화한다(운영자가 다른 용도의
      스케줄 작업을 쓰는 것은 흔하다). 그래서 판별자를 **sentinel 내용**으로 뒀고,
      이 케이스가 그 선택의 판별력을 짊어진다.

    mutant kill: 표식 술어를 `[[ -d "$TASK_DEF_ROOT" ]]`(존재만) 로 완화 ⇒ RED.
    """
    home, hb = _prepare_home(tmp_path, content=None, adopted=False)
    other = _plant_unrelated_task(home)
    assert other.exists(), "전제 붕괴: 무관 태스크 정의 미생성"
    assert "scheduled_task_reconcile" not in other.read_text(encoding="utf-8"), (
        "전제 붕괴: 무관 태스크에 sentinel 이 섞였다 — 대조군이 성립하지 않는다"
    )

    cp = _run_hook(home)

    assert cp.returncode == 0, f"exit 0 기대: rc={cp.returncode}"
    assert _marker_lines(cp) == [], (
        f"우리 CLI 를 지목하지 않는 태스크만 있는 환경은 무발화여야 한다: {_marker_lines(cp)}"
    )


# ═══════════ ①b absent + 표식 존재 (채택했는데 한 번도 안 돎 = 실 이상) ═══════════
@_SKIP_NO_BASH
def test_watchdog_absent_with_adoption_marker_reports_one_line(tmp_path):
    """①b heartbeat 부재 + 채택 표식 **존재** → 사실 1줄 발화 · exit 0.

    ★ 이 케이스가 짊어지는 것은 **표식이 보이는 정의역 안에서의 탐지 회복**이지 전체
      명제가 아니다. `absent → 표식 무관 무발화` 로 두면 "채택했으나 1회도 실행되지
      않음" class 가 구조적 무음이 되어 false-negative 를 하나 늘린다. 표식 판별자가 그
      손실을 되돌리되, 표식 자체가 안 보이는 경우(파일 헤더 **표식 가시성 축** (i)(ii)
      (iii))는 잔존이다 — ADR-172 Amd 4 A4-1 실측 E·F.

    ★ ①a 와 **heartbeat 상태가 동일**(absent)하고 표식만 다르다 — 두 결과가 갈린다는
      사실 자체가 판별자가 살아 있다는 증거다(공통 원인으로 둘 다 통과할 수 없다).

    mutant kill: 표식 판별자 제거(`absent → 무조건 false` 복원) ⇒ **이 테스트만 RED**.
    """
    home, hb = _prepare_home(tmp_path, content=None, adopted=True)
    assert not hb.exists(), f"전제 붕괴: heartbeat 파일이 존재한다 ({hb})"
    marker = Path(home) / ".claude" / "scheduled-tasks"
    assert marker.is_dir(), "전제 붕괴: 채택 표식 미생성"

    cp = _run_hook(home)

    assert cp.returncode == 0, f"exit 0 기대: rc={cp.returncode}"
    lines = _marker_lines(cp)
    assert len(lines) == 1, f"발화 1줄 기대, 실제 {len(lines)}줄: {lines}"
    m = FACT_RE.match(lines[0])
    assert m is not None, f"사실 줄 형식 불일치: {lines[0]!r}"
    assert m.group(1) == "absent", f"last_run_epoch=absent 기대, 실제 {m.group(1)!r}"
    assert m.group(2) == "unknown", f"age_seconds=unknown 기대, 실제 {m.group(2)!r}"


# ═══════ ①c 스캔 bound 도달 = 판정 불가 (구현리뷰 iter6 F-CR6-01) ═══════════════
@_SKIP_NO_BASH
def test_watchdog_absent_beyond_file_cap_reports_one_line(tmp_path):
    """①c-1 **파일 상한 소진** → 판정 불가 → 발화 1줄.

    ★ 이 오라클의 정의역은 **bound 그 자체**다. iter6 이전 판본에서는 `-maxdepth`·
      `head -200`·`grep -F` 를 전부 지워도 스위트가 GREEN 이었다 — bound 를 정의역으로
      삼는 검사가 **0건**이었기 때문이다.

    ★ 실측 반례(iter6): sentinel 이 **실재하는데** 스캔 순서 251번째면 hook 이 침묵했다.
      "못 찾음" 을 "없음" 으로 결론지었기 때문이고, 그 결과 (ㄴ) class(채택했는데
      한 번도 안 돎)가 bound 밖에서 조용히 되살아났다.

    3 leg 구성 — 판별력 귀속을 분리해 둔다:
      · leg A (**mutant kill 담당 · 완전 결정론**): 상한 초과 파일 + sentinel **전무**
        → 발화. 여기엔 표식이 어디에도 없으므로 발화의 유일한 근거가 "cap 소진 =
        판정 불가" 다. 파일 열거 순서에 전혀 의존하지 않는다.
      · leg B (**반례 형상 재현**): 상한 초과 파일 + sentinel 존재 → 발화. 단 이 leg 은
        **결과만** 고정한다 — 발화 경로가 "sentinel 발견" 인지 "cap 소진" 인지는
        `find` 의 열거 **순서**에 달렸고 그 순서는 파일시스템 의존이라 여기서 pin 하지
        않는다(로컬 NTFS 실측은 251번째 = cap 밖이었다).
      · leg C (**대조군 · 오탐 0**): bound **안**에서 전량 확인 + sentinel 전무 → 침묵.
        leg A 와 형상이 같고 파일 수만 다르므로, 둘이 갈린다는 사실이 곧 "무조건 발화"
        구현이 아님을 보증한다.

    mutant kill: hook 의 `(( scanned >= ADOPTION_MAX_FILES )) → return 0` 를 제거해
      bound 도달을 다시 "표식 없음" 으로 결론짓기 ⇒ **leg A RED**(leg C 는 GREEN 유지).
    """
    # ── leg A: cap 초과 + sentinel 전무 (결정론) ──
    home_a, hb_a = _prepare_home(tmp_path / "a", content=None, adopted=False)
    made = _plant_filler_files(home_a, ADOPTION_MAX_FILES + 50)
    assert not hb_a.exists(), "전제 붕괴: heartbeat 가 존재한다"
    assert len(_visible_to_scan(home_a)) > ADOPTION_MAX_FILES, (
        "전제 붕괴: 스캔 가시 파일 수가 상한을 넘지 않는다 — cap 이 소진되지 않는다"
    )
    for p in made[:5] + made[-5:]:
        assert "scheduled_task_reconcile" not in p.read_text(encoding="utf-8"), (
            f"전제 붕괴: filler 에 sentinel 이 섞였다 ({p})"
        )

    cp_a = _run_hook(home_a)
    assert cp_a.returncode == 0, f"exit 0 기대: rc={cp_a.returncode}"
    lines_a = _marker_lines(cp_a)
    assert len(lines_a) == 1, (
        f"cap 소진 = 판정 불가 → 발화 1줄 기대, 실제 {len(lines_a)}줄: {lines_a}. "
        "bound 도달을 '표식 없음' 으로 결론지으면 채택 환경이 bound 밖에서 무음이 된다"
    )
    assert FACT_RE.match(lines_a[0]), f"사실 줄 형식 불일치: {lines_a[0]!r}"

    # ── leg B: cap 초과 + sentinel 존재 (iter6 반례 형상) ──
    home_b, _ = _prepare_home(tmp_path / "b", content=None, adopted=False)
    _plant_filler_files(home_b, ADOPTION_MAX_FILES + 50)
    sentinel_file = _plant_adoption_marker(home_b, task_name="zzz-ours")
    assert "scheduled_task_reconcile" in sentinel_file.read_text(encoding="utf-8"), (
        "전제 붕괴: sentinel 미기재 — 반례 형상이 성립하지 않는다"
    )

    cp_b = _run_hook(home_b)
    assert cp_b.returncode == 0, f"exit 0 기대: rc={cp_b.returncode}"
    lines_b = _marker_lines(cp_b)
    assert len(lines_b) == 1, (
        f"sentinel 이 실재하는 환경은 발화해야 한다(스캔 순서와 무관하게), "
        f"실제 {len(lines_b)}줄: {lines_b}"
    )

    # ── leg C: bound 안 + sentinel 전무 → 침묵 (오탐 0) ──
    home_c, _ = _prepare_home(tmp_path / "c", content=None, adopted=False)
    _plant_filler_files(home_c, 5)
    assert len(_visible_to_scan(home_c)) < ADOPTION_MAX_FILES, "전제 붕괴: 대조군이 cap 을 넘었다"

    cp_c = _run_hook(home_c)
    assert cp_c.returncode == 0, f"exit 0 기대: rc={cp_c.returncode}"
    assert _marker_lines(cp_c) == [], (
        f"bound 안에서 전량 확인한 미채택 환경은 침묵해야 한다(오탐 0): {_marker_lines(cp_c)}"
    )


@_SKIP_NO_BASH
def test_watchdog_absent_beyond_max_depth_reports_one_line(tmp_path):
    """①c-2 **깊이 상한 밖 내용 존재** → 판정 불가 → 발화 1줄.

    ★ 실측 반례(iter6): sentinel 이 depth 4 에 있으면 hook 이 침묵했다(depth 3 대조군은
      발화). `-maxdepth 3` 이 스캔 정의역을 자르는데 그 밖을 "없음" 으로 결론지었기 때문이다.

    2 leg — 두 홈의 차이는 **깊이 상한 밖 내용의 유무 하나**다:
      · leg A: sentinel 을 MAX_DEPTH+1 에 심는다(스캔 정의역 밖) → 발화.
      · leg B (대조군): 같은 홈에서 그 깊은 서브트리만 제거 → 침묵. 깊이 probe 가
        발화의 원인이었음을 이 대조가 귀속시킨다(다른 변수는 동일).

    mutant kill: hook 의 `-mindepth N+1 -maxdepth N+1 -print -quit` 존재 확인 블록 제거
      ⇒ **leg A RED**(leg B 는 GREEN 유지).
    """
    # ── leg A: 깊이 상한 밖 sentinel ──
    home, hb = _prepare_home(tmp_path / "deep", content=None, adopted=False)
    deep = _plant_adoption_marker_deep(home)
    assert not hb.exists(), "전제 붕괴: heartbeat 가 존재한다"
    assert deep not in _visible_to_scan(home), (
        f"전제 붕괴: 깊은 sentinel 이 스캔 정의역 **안**에 있다 — 반례 형상이 아니다 ({deep})"
    )
    assert _visible_to_scan(home) == [], (
        f"전제 붕괴: 깊이 {ADOPTION_MAX_DEPTH} 이하에 파일이 있다 — "
        f"발화 원인이 깊이 probe 로 귀속되지 않는다: {_visible_to_scan(home)}"
    )

    cp = _run_hook(home)
    assert cp.returncode == 0, f"exit 0 기대: rc={cp.returncode}"
    lines = _marker_lines(cp)
    assert len(lines) == 1, (
        f"깊이 상한 밖 내용 존재 = 판정 불가 → 발화 1줄 기대, 실제 {len(lines)}줄: {lines}"
    )
    assert FACT_RE.match(lines[0]), f"사실 줄 형식 불일치: {lines[0]!r}"

    # ── leg B: 같은 홈에서 깊은 서브트리만 제거 → 침묵 ──
    shutil.rmtree(Path(home) / ".claude" / "scheduled-tasks" / "d0")
    assert (Path(home) / ".claude" / "scheduled-tasks").is_dir(), (
        "전제 붕괴: 대조군에서 태스크 루트까지 지웠다 — 변수가 둘이 된다"
    )

    cp2 = _run_hook(home)
    assert cp2.returncode == 0, f"exit 0 기대: rc={cp2.returncode}"
    assert _marker_lines(cp2) == [], (
        f"깊이 상한 밖 내용이 사라지면 침묵해야 한다(변수 1개 대조): {_marker_lines(cp2)}"
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


# ═══════ ⑥ base 유도 축 어긋남 = writer 동형화 (F-SEC-5, ADR-172 Amd 6 / A6-7) ═══════
def _run_hook_axes(home_dir, userprofile_dir, extra_env=None, timeout=60):
    """HOME 과 USERPROFILE 을 **다르게** 세워 hook 실행 (축 어긋남 재현).

    ★ 설계 판정(A6-7)이 요구한 형상: *"판별 테스트는 두 env 를 **다르게** 세운 격리에서
      발화를 보여야 한다"*. `_run_hook` 은 두 축을 같은 tmp 로 맞추므로 이 축을 못 잰다.
    ★ 격리: 두 축 모두 tmp 이고 HOMEDRIVE/HOMEPATH 는 제거한다 — 어느 유도 규칙이
      적용되든 실 사용자 홈에 닿지 않는다.
    """
    assert WORKING_BASH is not None
    env = dict(os.environ)
    env["HOME"] = str(home_dir).replace("\\", "/")
    env["USERPROFILE"] = str(userprofile_dir).replace("\\", "/")
    for leak in ("HOMEDRIVE", "HOMEPATH", "BYPASS_SCHEDULED_TASK_WATCHDOG",
                 "SCHEDULED_TASK_WATCHDOG_THRESHOLD_SECONDS"):
        env.pop(leak, None)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [WORKING_BASH, str(HOOK_PATH)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=timeout,
    )


def _writer_base(home_dir, userprofile_dir):
    """writer(python `expanduser`)가 **실제로** 고르는 축을 그 자리에서 잰다.

    ★ 상수로 박지 않는다 — 이 오라클의 전제는 "writer 는 USERPROFILE 을 고른다" 이고,
      그 전제가 플랫폼에 따라 다르면 테스트가 **다른 것을 재게 된다**. 실측으로 고정한다.
    """
    env = dict(os.environ)
    env["HOME"] = str(home_dir).replace("\\", "/")
    env["USERPROFILE"] = str(userprofile_dir).replace("\\", "/")
    for leak in ("HOMEDRIVE", "HOMEPATH"):
        env.pop(leak, None)
    cp = subprocess.run(
        [sys.executable, "-c", "import os;print(os.path.expanduser('~'))"],
        capture_output=True, text=True, encoding="utf-8", env=env, timeout=60,
    )
    assert cp.returncode == 0, f"writer 축 실측 실패: {cp.stderr!r}"
    return cp.stdout.strip().replace("\\", "/").rstrip("/")


def _norm(p):
    return str(p).replace("\\", "/").rstrip("/")


@_SKIP_NO_BASH
@pytest.mark.skipif(sys.platform != "win32",
                    reason="HOME↔USERPROFILE 분기는 Windows(ntpath) 축에서만 성립 — "
                           "POSIX 에서는 두 축이 정의상 갈리지 않는다(정의역 밖)")
class TestWriterBaseHomomorphism:
    """⑥ reader 의 base 유도가 **writer 와 동형**인가 (F-SEC-5).

    ★ 결함 형상(실측): CLI 는 heartbeat 를 **USERPROFILE 축**에 쓰고(Windows `ntpath` 는
      HOME 을 보지 않는다), hook 은 heartbeat 와 채택 표식을 **둘 다 `${HOME}`** 으로
      읽었다. 두 env 가 갈리면 그 둘이 **함께 이동**해 "표식 부재 + heartbeat 부재" =
      미채택으로 떨어져 **침묵**한다 — 채택자인데 감시가 조용히 무장해제된다.
      적대자 없이도 성립하며(툴체인이 HOME 을 다르게 세우면 그만), env 통제자는 이
      방향을 **침묵 쪽으로** 무기화할 수 있다.

    ★ 판별 구조 (한 방향만으로는 귀속되지 않는다):
      leg A  writer 축에 표식 · heartbeat 부재      → **발화** (종전 침묵 = 결함)
      leg B  writer 축에 fresh heartbeat            → **침묵** (반대 방향 — "항상 발화"
             구현 배제. 이 leg 이 없으면 leg A 를 무조건 발화로 통과시킬 수 있다)
      leg C  표식이 **비-writer 축(HOME)에만** 존재 → **침묵** (base 가 실제로 writer 축
             으로 **이동**했음의 증거. 종전 코드는 여기서 발화했다)
      ⇒ A 와 C 는 종전/현행이 **정확히 뒤집히는** 쌍이라, 둘이 동시에 성립하는 구현은
        "base 를 writer 축으로 옮긴" 구현뿐이다.

    mutant kill: `_state_base` 를 `printf '%s' "${HOME:-/tmp}"` 로 되돌리기
      ⇒ leg A RED (leg B 는 GREEN 유지 — 균일 실패가 아니다).
    """

    def test_writer_axis_is_userprofile_precondition(self, tmp_path):
        """전제 실측: 이 호스트에서 writer 는 **USERPROFILE 축**을 고른다.

        ★ 이 전제가 깨지면 아래 leg 들이 재는 대상이 달라진다. 그래서 별도 테스트로
          앞세워, 전제 붕괴가 **다른 테스트의 실패로 위장되지 않게** 한다.
        """
        a, b = tmp_path / "axis-home", tmp_path / "axis-profile"
        a.mkdir(); b.mkdir()
        assert _norm(a) != _norm(b), "정의역 붕괴: 두 축이 같은 경로다"
        assert _writer_base(a, b) == _norm(b), (
            f"전제 붕괴: writer 가 USERPROFILE 축을 고르지 않는다 — "
            f"실측 {_writer_base(a, b)!r}, 기대 {_norm(b)!r}"
        )

    def test_legA_adopted_on_writer_axis_reports(self, tmp_path):
        """leg A: 표식이 **writer 축**에 있고 heartbeat 부재 → 발화 1줄.

        종전 구현은 여기서 **침묵**했다(HOME 축만 봤으므로 표식도 heartbeat 도 못 봤다).
        """
        home, profile = tmp_path / "axis-home", tmp_path / "axis-profile"
        (home / ".claude").mkdir(parents=True)          # HOME 축은 비어 있다
        profile.mkdir()
        marker = _plant_adoption_marker(profile)

        # 전제: 표식은 writer 축에만 있고, 어느 축에도 heartbeat 가 없다
        assert marker.exists(), "전제 붕괴: 표식 미생성"
        assert not (home / ".claude" / "scheduled-tasks").exists(), (
            "전제 붕괴: HOME 축에도 표식이 있다 — 축 귀속이 안 된다"
        )
        for base in (home, profile):
            hb = base / ".claude" / "worktree-gc-state" / "scheduled-task-last-run.epoch"
            assert not hb.exists(), f"전제 붕괴: heartbeat 가 존재한다 ({hb})"

        cp = _run_hook_axes(home, profile)

        assert cp.returncode == 0, f"exit 0 기대: rc={cp.returncode}"
        lines = _marker_lines(cp)
        assert len(lines) == 1, (
            f"축이 갈린 채택 환경은 발화해야 한다(침묵 = 감시 무장해제), 실제 {len(lines)}줄: "
            f"{lines}. stderr={cp.stderr[:300]!r}"
        )
        m = FACT_RE.match(lines[0])
        assert m is not None, f"사실 줄 형식 불일치: {lines[0]!r}"
        assert m.group(1) == "absent", f"last_run_epoch=absent 기대: {m.group(1)!r}"

    def test_legB_fresh_heartbeat_on_writer_axis_is_silent(self, tmp_path):
        """leg B (**대조군**): fresh heartbeat 가 **writer 축**에 있으면 침묵.

        ★ 이 leg 이 짊어지는 것: heartbeat 판독도 같은 base 로 이동했는가.
          표식만 옮기고 heartbeat 를 HOME 에 남기면 여기서 RED 다 —
          writer 가 쓴 fresh heartbeat 를 못 보고 **매 세션 거짓 발화**하기 때문이다
          (지시의 "한쪽만 고치면 반대 방향으로 어긋난다" 가 정확히 이 leg).
        """
        home, profile = tmp_path / "axis-home", tmp_path / "axis-profile"
        home.mkdir(); profile.mkdir()
        state = profile / ".claude" / "worktree-gc-state"
        state.mkdir(parents=True)
        hb = state / "scheduled-task-last-run.epoch"
        hb.write_text("%d\n" % int(time.time()), encoding="utf-8", newline="\n")
        _plant_adoption_marker(profile)

        assert hb.exists(), "전제 붕괴: fresh heartbeat 미생성"
        assert not (home / ".claude").exists(), "전제 붕괴: HOME 축에 상태가 있다"

        cp = _run_hook_axes(home, profile)

        assert cp.returncode == 0, f"exit 0 기대: rc={cp.returncode}"
        assert _marker_lines(cp) == [], (
            f"writer 축의 fresh heartbeat 를 못 읽어 거짓 발화했다: {_marker_lines(cp)}"
        )

    def test_legC_marker_on_non_writer_axis_is_silent(self, tmp_path):
        """leg C: 표식이 **비-writer 축(HOME)에만** 있으면 침묵 — base 이동의 증거.

        ★ 종전 구현은 여기서 **발화**했다. leg A 와 정확히 뒤집힌 쌍이라, 둘이 동시에
          성립하는 구현은 base 를 writer 축으로 옮긴 구현뿐이다("항상 발화"·"항상 침묵"
          어느 쪽도 두 leg 을 함께 만족시키지 못한다).
        ★ 선언된 대가: writer 가 쓰지 않는 축의 표식은 이제 보이지 않는다. 그 축에는
          heartbeat 도 생기지 않으므로 관측 대상 자체가 그 축에 없다 — 동형화가 뜻하는
          바가 이것이다(정본 축 = writer 축).
        """
        home, profile = tmp_path / "axis-home", tmp_path / "axis-profile"
        home.mkdir(); profile.mkdir()
        marker = _plant_adoption_marker(home)          # 비-writer 축에만 표식

        assert marker.exists(), "전제 붕괴: 표식 미생성"
        assert not (profile / ".claude").exists(), (
            "전제 붕괴: writer 축에도 상태가 있다 — 축 귀속이 안 된다"
        )

        cp = _run_hook_axes(home, profile)

        assert cp.returncode == 0, f"exit 0 기대: rc={cp.returncode}"
        assert _marker_lines(cp) == [], (
            f"base 가 writer 축으로 이동하지 않았다(HOME 축 표식으로 발화): "
            f"{_marker_lines(cp)}"
        )

    def test_real_user_state_is_never_read(self, tmp_path):
        """격리 회귀: 실 사용자 홈을 읽지 않는다 (규율 5).

        ★ writer 동형화로 유도 축이 늘었으므로(USERPROFILE·HOMEDRIVE+HOMEPATH), 격리가
          HOME 하나로는 부족해졌다. 그 격리가 실제로 성립하는지 **산출로** 확인한다:
          실 홈에는 heartbeat 가 있을 수 있고, 그것을 읽었다면 fresh/stale 판정이
          tmp 형상과 달라진다. 여기서는 두 축 모두 빈 tmp 이므로 **침묵**이 정답이다.
        """
        home, profile = tmp_path / "h", tmp_path / "p"
        home.mkdir(); profile.mkdir()
        cp = _run_hook_axes(home, profile)
        assert cp.returncode == 0, f"exit 0 기대: rc={cp.returncode}"
        assert _marker_lines(cp) == [], (
            f"빈 tmp 두 축인데 발화했다 — 실 사용자 상태를 읽었을 가능성: "
            f"{_marker_lines(cp)}"
        )
        # 부수효과 0 — 어느 축에도 파일을 만들지 않는다
        for base in (home, profile):
            assert list(base.rglob("*")) == [], (
                f"hook 이 상태를 생성했다(판독 전용 위반): {list(base.rglob('*'))}"
            )
