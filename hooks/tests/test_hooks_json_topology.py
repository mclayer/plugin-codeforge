"""test_hooks_json_topology.py — CFP-2587 Phase 2 §8 T-8 topology-config guard (I5).

계약 SSOT: Story CFP-2587 §7.10 T-8 / §8.2 I5.
Runtime 무실행(config-shape only) → multi-hook 불필요, 토폴로지-측정 gate(spike)와 disjoint.
근거: spike(manual·1회성)가 검증한 프로덕션 4-hook Bash 토폴로지 전제가 미래 hook 편집
(sibling 추가/제거, injection matcher 오등록)으로 drift 하면 spike 결과 stale · durable suite
green = false confidence → 이 loop 를 닫는 config-shape pin.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent
HOOKS_JSON = WORKTREE_ROOT / "hooks" / "hooks.json"
HOOKS_DIR = WORKTREE_ROOT / "hooks"

# 프로덕션 토폴로지 exact-set (spike 전제 — drift 시 이 테스트가 회귀 검출)
EXPECTED_BASH = {
    "cross-repo-gh-safety",
    "repo-confinement",
    "git-branch-delete-merge-gate",
    "pretooluse-bash-description-inject",   # CFP-2587 injection hook
}
EXPECTED_AGENT = {"pretooluse-agent-spawn-gate"}


def _matcher_hook_names(matcher: str) -> set:
    data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    for entry in data["hooks"]["PreToolUse"]:
        if entry.get("matcher") == matcher:
            # command = '"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd" <hook-name>'
            return {h["command"].split()[-1].strip('"') for h in entry["hooks"]}
    return set()


def test_bash_matcher_exact_4_hook_set():
    """Bash matcher = 정확히 4 hook (3 sibling deny-gate + injection). exact-set (초과/누락 검출)."""
    assert _matcher_hook_names("Bash") == EXPECTED_BASH


def test_agent_matcher_single_hook():
    """Agent matcher = 단일 hook (multi-hook 무관 유지 — #15897-immune 비대칭 보존)."""
    assert _matcher_hook_names("Agent") == EXPECTED_AGENT


def test_injection_hook_registered_and_file_exists():
    assert "pretooluse-bash-description-inject" in _matcher_hook_names("Bash")
    assert (HOOKS_DIR / "pretooluse-bash-description-inject").exists()


def test_single_writer_only_injection_hooks_emit_updated_input():
    """AC-18 single-writer pin (best-effort 정적 grep — dynamic emit 미포착 caveat):
    Bash matcher 등록 hook 중 `updatedInput` 을 emit 하는 것은 injection hook 뿐.
    3 sibling deny-gate 는 updatedInput 미emit (exit-2/stdout-JSON-없음)."""
    emitters = set()
    for name in _matcher_hook_names("Bash"):
        # hook launcher + 그 launcher 가 exec 하는 python core 둘 다 스캔
        candidates = [HOOKS_DIR / name, HOOKS_DIR / (name + ".py")]
        text = ""
        for c in candidates:
            if c.exists():
                text += c.read_text(encoding="utf-8", errors="replace")
        # 문자열 'updatedInput' 을 직접 저작하거나 --inject 로 위임하면 emitter 로 간주
        if "updatedInput" in text or "--inject" in text:
            emitters.add(name)
    assert emitters == {"pretooluse-bash-description-inject"}, (
        f"updatedInput single-writer 위반: {emitters}")


def test_hooks_json_valid_and_agent_not_multi_hook():
    """Agent matcher 에 2번째 hook 추가 시 #15897 gratuitous 도입 → 이 assert 가 방어."""
    names = _matcher_hook_names("Agent")
    assert len(names) == 1, f"Agent matcher multi-hook 회귀 (#15897 gratuitous): {names}"
