#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_confluence_backward_author_preset.py — AC-10 축① (author preset validation)."""

import sys
import yaml
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest


def load_backward_author_frontmatter() -> dict:
    """Load backward-author agent frontmatter."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    agent_file = repo_root / ".claude" / "agents" / "confluence-sync-backward-author.md"

    if not agent_file.exists():
        pytest.skip(f"Agent file not found: {agent_file}")

    with open(agent_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse YAML frontmatter (between --- delimiters)
    if not content.startswith('---'):
        pytest.skip("No YAML frontmatter found")

    end_marker = content.find('\n---\n', 4)
    if end_marker == -1:
        pytest.skip("Frontmatter not properly closed")

    frontmatter_text = content[4:end_marker]
    return yaml.safe_load(frontmatter_text) or {}


# ── AC-10 축①: disallowedTools 실재 (write Confluence tool 봉인) ────────────

def test_ac10_disallowed_tools_defined():
    """AC-10: disallowedTools field exists in frontmatter."""
    fm = load_backward_author_frontmatter()
    assert "disallowedTools" in fm, "disallowedTools must be defined"
    assert isinstance(fm["disallowedTools"], list), "disallowedTools must be list"


def test_ac10_confluence_create_page_disallowed():
    """AC-10: createConfluencePage must be in disallowedTools."""
    fm = load_backward_author_frontmatter()
    disallowed = fm.get("disallowedTools", [])
    assert "mcp__plugin_atlassian_atlassian__createConfluencePage" in disallowed


def test_ac10_confluence_update_page_disallowed():
    """AC-10: updateConfluencePage must be in disallowedTools."""
    fm = load_backward_author_frontmatter()
    disallowed = fm.get("disallowedTools", [])
    assert "mcp__plugin_atlassian_atlassian__updateConfluencePage" in disallowed


def test_ac10_no_confluence_write_in_tools():
    """AC-10: no Confluence write tool (create*/update*) in tools list."""
    fm = load_backward_author_frontmatter()
    tools = fm.get("tools", [])

    # Confluence write tools to forbid
    forbidden_patterns = [
        "createConfluencePage",
        "updateConfluencePage",
        "createConfluenceFooterComment",
        "createConfluenceInlineComment",
    ]

    for tool in tools:
        for pattern in forbidden_patterns:
            assert pattern not in tool, f"Write tool {tool} found in allowed tools list"


def test_ac10_model_tier():
    """AC-10: model tier must be 'opus' (production strong requirement)."""
    fm = load_backward_author_frontmatter()
    assert fm.get("model") == "opus", "model must be 'opus' for backward-author"


# ── AC-10 축① source-mutation kill (static artifact — agent frontmatter) ───
#
# 이 AC 의 "production logic" = agent frontmatter(정적 artifact) 그 자체다. 위 positive
# 테스트(test_ac10_confluence_create_page_disallowed / _update_page_disallowed /
#  _no_confluence_write_in_tools)가 실 frontmatter 를 직접 파싱해 disallowedTools 봉인을
# 검증하므로 artifact 변조에 대해 discriminating 하다.
#
# artifact-mutation kill 실증 (neuter→run→RED→restore, DevPL firsthand):
#   .claude/agents/confluence-sync-backward-author.md 의 disallowedTools 목록에서
#   `mcp__plugin_atlassian_atlassian__createConfluencePage` 라인 삭제
#     → test_ac10_confluence_create_page_disallowed RED.
#   명령: python -m pytest tests/scripts/test_confluence_backward_author_preset.py::test_ac10_confluence_create_page_disallowed
#   기대: 라인 삭제 시 FAILED / 복원 시 PASSED.


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
