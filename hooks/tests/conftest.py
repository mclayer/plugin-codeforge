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


# ============================================================ 공용 테스트 인프라 (CFP-2965 G1)
#
# 공용 심볼(BASH / requires_bash / run_hook_bash / …)은 **conftest 가 아니라**
# 고유 basename 모듈 `hook_runner_cfp2965.py` 에 있다.
#
#   사유 (CR-201 실측): CI 실 run-line 은 2-dir (`pytest hooks/tests overlay/hooks/tests`).
#   top-level 모듈명 `conftest` 는 두 디렉터리가 공유하는 이름이라
#   `overlay/hooks/tests/conftest.py`(6줄·공용 심볼 0)가 sys.modules["conftest"] 를
#   선점하면 bare `from conftest import requires_bash` 가 그 빈 모듈로 해석돼
#   ImportError → collection ERROR 4 → Interrupted(전체 미실행). 단일 dir 실행은
#   GREEN 이라 로컬에서 안 보였다. conftest 의 자동 로드 성질은 fixture/플러그인
#   side effect 에만 필요하고 공용 상수·헬퍼에는 불필요하므로 분리한다.
#
# 로드 방식: sys.path 무가정 — 명시 경로 importlib 로 읽고 sys.modules 에 등록한다
#   (위 하이픈-파일 로더와 동일 관례). 테스트 파일의 bare
#   `from hook_runner_cfp2965 import ...` 는 sys.modules 를 먼저 맞히므로
#   수집 구성(단일 dir / 2-dir)과 무관하게 동일 객체로 해석된다.

_hr_spec = importlib.util.spec_from_file_location(
    "hook_runner_cfp2965", Path(__file__).resolve().parent / "hook_runner_cfp2965.py"
)
hook_runner_cfp2965 = importlib.util.module_from_spec(_hr_spec)
_hr_spec.loader.exec_module(hook_runner_cfp2965)
sys.modules["hook_runner_cfp2965"] = hook_runner_cfp2965

# 하위호환 재노출 (conftest 를 직접 참조하는 외부 소비자 대비 — hooks/tests 내부
# 테스트는 전부 hook_runner_cfp2965 를 직접 import 한다).
BASH = hook_runner_cfp2965.BASH
RUN_HOOK_CMD = hook_runner_cfp2965.RUN_HOOK_CMD
HOOKS_DIR_FOR_RUNNER = hook_runner_cfp2965.HOOKS_DIR_FOR_RUNNER
requires_bash = hook_runner_cfp2965.requires_bash
requires_windows = hook_runner_cfp2965.requires_windows
run_hook_bash = hook_runner_cfp2965.run_hook_bash
