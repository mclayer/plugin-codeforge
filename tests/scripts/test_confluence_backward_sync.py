#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_confluence_backward_sync.py — AC-4/5/7/8/9/14"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import json
import os
import pytest
import confluence_backward_sync as B
from sync_sentinel import (
    SUBSTRATE_MARKER, anchor_equality_skip, commit_message_is_substrate,
    dedup_key
)


class TestAC4_FlagOnDarkPath:
    def test_ac4_flag_off_skip(self, monkeypatch):
        monkeypatch.delenv('CFP2829_BACKWARD_SYNC_ENABLED', raising=False)
        assert B.backward_sync_enabled() is False


class TestAC5_InvAGitPRProposalOnly:
    def test_ac5_pos_build_pr_proposal_disables_automerge(self):
        p = B.build_pr_proposal('docs/x.md', 'feat-branch')
        assert p['auto_merge'] is False
        assert p['direct_push_to_base'] is False

    def test_ac5_pos_assert_pr_only_passes(self):
        p = B.build_pr_proposal('docs/y.md', 'fix-branch')
        B.assert_pr_only(p)

    def test_ac5_mut_automerge_escape_detected(self):
        p = B.build_pr_proposal('docs/z.md', 'test-branch')
        p['auto_merge'] = True
        with pytest.raises(B.InvariantViolation):
            B.assert_pr_only(p)


class TestAC7_SentinelMarkerFastPath:
    def test_ac7_anchor_equality_skip_equal_returns_true(self):
        assert anchor_equality_skip('abc', 'abc') is True

    def test_ac7_anchor_equality_skip_notequal_returns_false(self):
        assert anchor_equality_skip('abc', 'def') is False

    def test_ac7_sentinel_commit_message(self):
        msg = "fix\n\n" + SUBSTRATE_MARKER
        assert commit_message_is_substrate(msg) is True

    def test_ac7_dedup_key_deterministic(self):
        k1 = dedup_key('p1', 3)
        k2 = dedup_key('p1', 3)
        assert k1 == k2 == ('p1', 3)


class TestAC8_AnchorACanonical:
    def test_ac8_pos_deterministic_anchor_a(self):
        md = b'# doc\ncontent\n'
        a1 = B.substrate_anchor_a(md)
        a2 = B.substrate_anchor_a(md)
        assert a1 == a2

    def test_ac8_pos_crlf_normalization(self):
        a = B.substrate_anchor_a(b'content\r\n')
        b = B.substrate_anchor_a(b'content\n')
        assert a == b

    def test_ac8_pos_creds_free(self, monkeypatch):
        monkeypatch.delenv('ATLASSIAN_API_TOKEN', raising=False)
        h = B.substrate_anchor_a(b'test')
        assert len(h) == 64


class TestAC9_ReadDivergenceRouting:
    def test_ac9_pos_agent_route(self):
        assert B.resolve_read_source('agent') == 'git-substrate'

    def test_ac9_pos_human_route(self):
        assert B.resolve_read_source('human') == 'atlassian-first'

    def test_ac9_pos_unknown_raises(self):
        with pytest.raises(ValueError, match='unknown'):
            B.resolve_read_source('unknown')


class TestAC14_DedupPolling:
    def test_ac14_pos_new_page_detected(self):
        candidates = [{'page_id': 'p1', 'version_number': 1}]
        changed = B.detect_changes(candidates, seen={})
        assert len(changed) == 1

    def test_ac14_pos_idempotency(self):
        seen = {'p1': 1}
        candidates = [{'page_id': 'p1', 'version_number': 1}]
        changed = B.detect_changes(candidates, seen=seen)
        assert len(changed) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
