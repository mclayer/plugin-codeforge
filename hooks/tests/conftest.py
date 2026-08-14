"""conftest.py — bootstrap-first-gate 테스트 fixture + importlib 로더.

비표준 파일명(하이픈 포함) bootstrap-first-gate.py 를 importlib 로 로드해
bootstrap_first_gate 모듈명으로 노출하는 패턴. overlay/hooks/tests/conftest.py
패턴 답습.
"""

import os
import shutil
import subprocess
import sys
import importlib.util
from pathlib import Path

import pytest

# sys.path 에 hooks/ 디렉터리 주입
HOOKS_DIR = Path(__file__).resolve().parent.parent
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

# bootstrap-first-gate.py 를 bootstrap_first_gate 모듈명으로 로드
_spec = importlib.util.spec_from_file_location(
    "bootstrap_first_gate", HOOKS_DIR / "bootstrap-first-gate.py"
)
bootstrap_first_gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bootstrap_first_gate)
sys.modules["bootstrap_first_gate"] = bootstrap_first_gate

# git-branch-delete-merge-gate.py 를 git_branch_delete_merge_gate 모듈명으로 로드 (CFP-2282)
_gbdmg_spec = importlib.util.spec_from_file_location(
    "git_branch_delete_merge_gate", HOOKS_DIR / "git-branch-delete-merge-gate.py"
)
git_branch_delete_merge_gate = importlib.util.module_from_spec(_gbdmg_spec)
_gbdmg_spec.loader.exec_module(git_branch_delete_merge_gate)
sys.modules["git_branch_delete_merge_gate"] = git_branch_delete_merge_gate

# skip-offer-reminder.py 를 skip_offer_reminder 모듈명으로 로드 (CFP-2456)
_sor_spec = importlib.util.spec_from_file_location(
    "skip_offer_reminder", HOOKS_DIR / "skip-offer-reminder.py"
)
skip_offer_reminder = importlib.util.module_from_spec(_sor_spec)
_sor_spec.loader.exec_module(skip_offer_reminder)
sys.modules["skip_offer_reminder"] = skip_offer_reminder

# story-transition-autonomy-reminder.py 를 story_transition_autonomy_reminder 모듈명으로 로드 (CFP-2567 채널 1)
_star_spec = importlib.util.spec_from_file_location(
    "story_transition_autonomy_reminder",
    HOOKS_DIR / "story-transition-autonomy-reminder.py",
)
story_transition_autonomy_reminder = importlib.util.module_from_spec(_star_spec)
_star_spec.loader.exec_module(story_transition_autonomy_reminder)
sys.modules["story_transition_autonomy_reminder"] = story_transition_autonomy_reminder

# session-swap-handoff-reminder.py 를 session_swap_handoff_reminder 모듈명으로 로드 (CFP-2742 Phase 2)
_sshr_spec = importlib.util.spec_from_file_location(
    "session_swap_handoff_reminder",
    HOOKS_DIR / "session-swap-handoff-reminder.py",
)
session_swap_handoff_reminder = importlib.util.module_from_spec(_sshr_spec)
_sshr_spec.loader.exec_module(session_swap_handoff_reminder)
sys.modules["session_swap_handoff_reminder"] = session_swap_handoff_reminder

# check_inline_write_gate.py (scripts/lib/) — CFP-2544 inline-write gate SSOT
_REPO_ROOT = HOOKS_DIR.parent
_ciwg_spec = importlib.util.spec_from_file_location(
    "check_inline_write_gate", _REPO_ROOT / "scripts" / "lib" / "check_inline_write_gate.py"
)
check_inline_write_gate = importlib.util.module_from_spec(_ciwg_spec)
_ciwg_spec.loader.exec_module(check_inline_write_gate)
sys.modules["check_inline_write_gate"] = check_inline_write_gate

# agent_spawn_transition_reminder.py (scripts/lib/) — CFP-2567 채널 2 helper (PreToolUse(Agent))
_astr_spec = importlib.util.spec_from_file_location(
    "agent_spawn_transition_reminder",
    _REPO_ROOT / "scripts" / "lib" / "agent_spawn_transition_reminder.py",
)
agent_spawn_transition_reminder = importlib.util.module_from_spec(_astr_spec)
_astr_spec.loader.exec_module(agent_spawn_transition_reminder)
sys.modules["agent_spawn_transition_reminder"] = agent_spawn_transition_reminder

# scripts/lib 을 sys.path 에 주입 (check_spawn_description_prefix 의 _load_build_context
# sibling import + 직접 import 를 위해) — CFP-2587 Phase 2
_SCRIPTS_LIB = _REPO_ROOT / "scripts" / "lib"
if str(_SCRIPTS_LIB) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_LIB))

# check_spawn_description_prefix.py (scripts/lib/) — CFP-2587 Phase 2 injection constructor SSOT
_csdp_spec = importlib.util.spec_from_file_location(
    "check_spawn_description_prefix",
    _SCRIPTS_LIB / "check_spawn_description_prefix.py",
)
check_spawn_description_prefix = importlib.util.module_from_spec(_csdp_spec)
_csdp_spec.loader.exec_module(check_spawn_description_prefix)
sys.modules["check_spawn_description_prefix"] = check_spawn_description_prefix


# ============================================================ 공용 훅 러너 (CFP-2965 F1)
#
# 배경: 일부 테스트가 훅을 `["cmd.exe", "/c", run-hook.cmd, <hook>]` 로 하드코딩해
#   실행했다. Windows 에서만 성립하는 형태라 Linux CI(ubuntu-latest)에서는
#   FileNotFoundError → 전건 FAIL 한다. 훅의 **판정 축**(deny / fail-open 거동)은 OS 와
#   무관하므로 bash 직접 호출로 통일한다 (test_golden_corpus.py 동형).
#
#   등가성 실측(2026-08-14, Windows): worktree-location-guard TIER={block, warn, 미설정}
#   3케이스에서 cmd.exe 경유와 bash 직접 호출의 rc·stderr 가 완전 일치.
#
#   run-hook.cmd 경유가 *본질*인 축(배치 런처의 exit code 전파 등)은 훅의 판정이 아니라
#   런처 자체의 계약이므로, 그 축만 `requires_windows` 로 명시 분리한다.
#
# 중복 정직 기록: `shutil.which("bash")` 사본이 hooks/tests/ 에 이미 7개 존재한다
#   (test_cross_repo_gh_safety / test_dev_process_capture_wrappers / test_dynamic_contracts_c /
#    test_golden_corpus / test_pretooluse_agent_spawn_gate / test_pretooluse_bash_description_inject /
#    test_repo_confinement). 본 helper 는 그 정본 자리이며, 신규 유입을 막는다.
#   기존 7개의 수렴은 본 FIX 범위 밖(무관 테스트 회귀 위험) — 별건 기계적 정리 대상.

HOOKS_DIR_FOR_RUNNER = HOOKS_DIR
RUN_HOOK_CMD = HOOKS_DIR / "run-hook.cmd"

BASH = shutil.which("bash") or (
    r"C:\Program Files\Git\bin\bash.exe"
    if os.name == "nt" and Path(r"C:\Program Files\Git\bin\bash.exe").exists()
    else None
)

requires_bash = pytest.mark.skipif(BASH is None, reason="bash interpreter 부재")
requires_windows = pytest.mark.skipif(
    os.name != "nt",
    reason="run-hook.cmd(cmd.exe) 런처 경유가 본질인 축 — Windows 전용",
)


def run_hook_bash(
    hook_name: str,
    stdin_bytes: bytes | None = None,
    env: dict | None = None,
    timeout: int = 30,
) -> tuple[int, str, str]:
    """`hooks/<hook_name>` 을 bash 로 직접 실행 → (rc, stdout, stderr).

    타임아웃·기동 실패는 rc=-1 + 사유 문자열로 환원한다 (호출부가 rc 로 단정하도록).
    """
    try:
        proc = subprocess.run(
            [BASH, str(HOOKS_DIR / hook_name)],
            input=stdin_bytes,
            capture_output=True,
            env=env,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as exc:  # 기동 실패 (bash 부재 등)
        return -1, "", f"{type(exc).__name__}: {exc}"
    return (
        proc.returncode,
        proc.stdout.decode("utf-8", errors="replace"),
        proc.stderr.decode("utf-8", errors="replace"),
    )
