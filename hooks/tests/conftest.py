"""conftest.py — bootstrap-first-gate 테스트 fixture + importlib 로더.

비표준 파일명(하이픈 포함) bootstrap-first-gate.py 를 importlib 로 로드해
bootstrap_first_gate 모듈명으로 노출하는 패턴. overlay/hooks/tests/conftest.py
패턴 답습.
"""

import sys
import importlib.util
from pathlib import Path

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
