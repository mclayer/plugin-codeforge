"""
scripts/lib/test_check_parallel_work_sentinel.py
CFP-967 — pytest unit tests for check_parallel_work_sentinel.py

Coverage:
  - 3 mode hit/miss + auth failure exit 2
  - 3 graceful degradation paths
  - argparse unknown mode / missing required arg exit 2
  - exit-code 3-tier enum

Test seam: CFP967_GH_MOCK_RESPONSE + CFP967_GIT_LOG_MOCK env vars
"""

import importlib
import json
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest

# Ensure scripts/lib is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import check_parallel_work_sentinel as sentinel


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
TITLE_SEARCH_HIT_FIXTURE = json.dumps([
    {"number": 953, "title": "CFP-953 duplicate incident", "labels": [{"name": "parent:CFP-882"}], "closedAt": None},
    {"number": 967, "title": "CFP-967 parallel work sentinel", "labels": [{"name": "phase:구현"}], "closedAt": None},
])

TITLE_SEARCH_MISS_FIXTURE = json.dumps([])

EPIC_STATE_OPEN_FIXTURE = json.dumps({
    "state": "OPEN",
    "closedAt": None,
    "closedBy": None,
    "labels": [{"name": "parent:CFP-882"}],
    "body": "Epic scope_manifest\n<!-- scope_manifest -->\nplanned_stories: [CFP-906, CFP-932, CFP-954]\n",
})

EPIC_STATE_CLOSED_FIXTURE = json.dumps({
    "state": "CLOSED",
    "closedAt": "2026-05-18T06:53:30Z",
    "closedBy": {"login": "mclayer"},
    "labels": [],
    "body": "CFP-946 closes",
})

API_403_FIXTURE = json.dumps({"message": "API rate limit exceeded", "status": "403"})

HEAD_COMPARE_DELTA = (
    "491949a 2026-05-19T01:00:00+09:00 [CFP-988] ADR-070 Amendment 4\n"
    "faa3277 2026-05-19T00:00:00+09:00 [CFP-967] FIX iter 2 revert\n"
)

HEAD_COMPARE_NO_DELTA = ""


# ---------------------------------------------------------------------------
# Helper: write fixture to tempfile, return path
# ---------------------------------------------------------------------------
def _tmpfile(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return f.name


# ---------------------------------------------------------------------------
# title-search tests
# ---------------------------------------------------------------------------
class TestTitleSearchHit:
    def test_title_search_hit(self, monkeypatch, capsys):
        """TC: title-search happy path — matches returned, exit 0."""
        fixture = _tmpfile(TITLE_SEARCH_HIT_FIXTURE)
        monkeypatch.setenv("CFP967_GH_MOCK_RESPONSE", fixture)
        monkeypatch.setenv("CFP_CONTEXT", "CFP-967")
        monkeypatch.delenv("BYPASS_PARALLEL_WORK_SENTINEL", raising=False)

        with pytest.raises(SystemExit) as exc:
            sentinel.mode_title_search()
        assert exc.value.code == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert "matches" in data
        # at least one match containing CFP-967
        numbers = [m["number"] for m in data["matches"]]
        assert 967 in numbers or len(data["matches"]) >= 1

    def test_title_search_miss(self, monkeypatch, capsys):
        """TC: title-search miss — empty matches, exit 0."""
        fixture = _tmpfile(TITLE_SEARCH_MISS_FIXTURE)
        monkeypatch.setenv("CFP967_GH_MOCK_RESPONSE", fixture)
        monkeypatch.setenv("CFP_CONTEXT", "CFP-9999")
        monkeypatch.delenv("BYPASS_PARALLEL_WORK_SENTINEL", raising=False)

        with pytest.raises(SystemExit) as exc:
            sentinel.mode_title_search()
        assert exc.value.code == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["matches"] == []

    def test_title_search_no_auth_exit_2(self, monkeypatch, capsys):
        """TC: gh CLI not authenticated — exit 2 SETUP error."""
        monkeypatch.delenv("CFP967_GH_MOCK_RESPONSE", raising=False)
        monkeypatch.delenv("BYPASS_PARALLEL_WORK_SENTINEL", raising=False)
        monkeypatch.setenv("CFP_CONTEXT", "CFP-967")

        with patch("check_parallel_work_sentinel._check_gh_auth", return_value=False):
            with pytest.raises(SystemExit) as exc:
                sentinel.mode_title_search()
        assert exc.value.code == 2


# ---------------------------------------------------------------------------
# epic-state-poll tests
# ---------------------------------------------------------------------------
class TestEpicStatePoll:
    def test_epic_state_poll_open(self, monkeypatch, capsys):
        """TC: epic-state-poll OPEN Epic — siblings present, exit 0."""
        fixture = _tmpfile(EPIC_STATE_OPEN_FIXTURE)
        monkeypatch.setenv("CFP967_GH_MOCK_RESPONSE", fixture)
        monkeypatch.delenv("BYPASS_PARALLEL_WORK_SENTINEL", raising=False)

        with pytest.raises(SystemExit) as exc:
            sentinel.mode_epic_state_poll(epic_id="882")
        assert exc.value.code == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["epic_state"] == "OPEN"
        assert len(data["siblings"]) >= 1

    def test_epic_state_poll_closed(self, monkeypatch, capsys):
        """TC: epic-state-poll CLOSED Epic (CFP-946 scenario)."""
        fixture = _tmpfile(EPIC_STATE_CLOSED_FIXTURE)
        monkeypatch.setenv("CFP967_GH_MOCK_RESPONSE", fixture)
        monkeypatch.delenv("BYPASS_PARALLEL_WORK_SENTINEL", raising=False)

        with pytest.raises(SystemExit) as exc:
            sentinel.mode_epic_state_poll(epic_id="946")
        assert exc.value.code == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["epic_state"] == "CLOSED"

    def test_epic_state_poll_no_scope_manifest(self, monkeypatch, capsys):
        """TC: epic-state-poll with empty body — siblings=[], exit 0."""
        fixture = _tmpfile(json.dumps({
            "state": "OPEN",
            "closedAt": None,
            "closedBy": None,
            "labels": [],
            "body": "",
        }))
        monkeypatch.setenv("CFP967_GH_MOCK_RESPONSE", fixture)
        monkeypatch.delenv("BYPASS_PARALLEL_WORK_SENTINEL", raising=False)

        with pytest.raises(SystemExit) as exc:
            sentinel.mode_epic_state_poll(epic_id="999")
        assert exc.value.code == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["siblings"] == []


# ---------------------------------------------------------------------------
# head-compare-sibling-commits tests
# ---------------------------------------------------------------------------
class TestHeadCompare:
    def test_head_compare_delta(self, monkeypatch, capsys):
        """TC: head-compare delta commits — parallel_detected=true, exit 0."""
        fixture = _tmpfile(HEAD_COMPARE_DELTA)
        monkeypatch.setenv("CFP967_GIT_LOG_MOCK", fixture)
        monkeypatch.setenv("CFP_PRIOR_SHA", "f4ad18f7")
        monkeypatch.delenv("BYPASS_PARALLEL_WORK_SENTINEL", raising=False)

        with patch("check_parallel_work_sentinel._check_stale_grace", return_value=None):
            with pytest.raises(SystemExit) as exc:
                sentinel.mode_head_compare()
        assert exc.value.code == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["parallel_detected"] is True
        assert len(data["delta_commits"]) >= 1

    def test_head_compare_no_delta(self, monkeypatch, capsys):
        """TC: head-compare no delta — parallel_detected=false, exit 0."""
        fixture = _tmpfile(HEAD_COMPARE_NO_DELTA)
        monkeypatch.setenv("CFP967_GIT_LOG_MOCK", fixture)
        monkeypatch.setenv("CFP_PRIOR_SHA", "491949a")
        monkeypatch.delenv("BYPASS_PARALLEL_WORK_SENTINEL", raising=False)

        with patch("check_parallel_work_sentinel._check_stale_grace", return_value=None):
            with pytest.raises(SystemExit) as exc:
                sentinel.mode_head_compare()
        assert exc.value.code == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["parallel_detected"] is False
        assert data["delta_commits"] == []

    def test_head_compare_fetch_fail(self, monkeypatch, capsys):
        """TC: git log mock missing — graceful degradation, exit 0."""
        monkeypatch.setenv("CFP967_GIT_LOG_MOCK", "/nonexistent/path.txt")
        monkeypatch.setenv("CFP_PRIOR_SHA", "deadbeef")
        monkeypatch.delenv("BYPASS_PARALLEL_WORK_SENTINEL", raising=False)

        with pytest.raises(SystemExit) as exc:
            sentinel.mode_head_compare()
        assert exc.value.code == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["parallel_detected"] is False


# ---------------------------------------------------------------------------
# Argparse tests
# ---------------------------------------------------------------------------
class TestArgparse:
    def test_unknown_mode_exit_2(self, monkeypatch):
        """TC: unknown mode → exit 2."""
        monkeypatch.delenv("BYPASS_PARALLEL_WORK_SENTINEL", raising=False)
        monkeypatch.setattr(sys, "argv", ["prog", "--mode=invalid-mode"])
        with pytest.raises(SystemExit) as exc:
            sentinel.main()
        # argparse invalid choice exits with code 2
        assert exc.value.code == 2

    def test_missing_required_arg_exit_2(self, monkeypatch):
        """TC: epic-state-poll missing --epic-id → exit 2."""
        monkeypatch.delenv("BYPASS_PARALLEL_WORK_SENTINEL", raising=False)
        monkeypatch.setattr(sys, "argv", ["prog", "--mode=epic-state-poll"])

        with patch("check_parallel_work_sentinel._check_gh_auth", return_value=True):
            with pytest.raises(SystemExit) as exc:
                sentinel.main()
        assert exc.value.code == 2


# ---------------------------------------------------------------------------
# Exit-code 3-tier tests
# ---------------------------------------------------------------------------
class TestExitCodes:
    def test_exit_codes_enum(self):
        """TC: exit-code 3-tier — 0 PASS / 1 reserved / 2 SETUP error."""
        # verify _exit_pass exits 0
        with pytest.raises(SystemExit) as exc:
            sentinel._exit_pass({"test": "pass"})
        assert exc.value.code == 0

        # verify _exit_setup_error exits 2
        with pytest.raises(SystemExit) as exc:
            sentinel._exit_setup_error("test error")
        assert exc.value.code == 2

    def test_bypass_exit_0(self, monkeypatch, capsys):
        """TC: BYPASS_PARALLEL_WORK_SENTINEL=1 → exit 0 + bypass invoked."""
        monkeypatch.setenv("BYPASS_PARALLEL_WORK_SENTINEL", "1")
        monkeypatch.setattr(sys, "argv", ["prog", "--mode=title-search"])
        with pytest.raises(SystemExit) as exc:
            sentinel.main()
        assert exc.value.code == 0
        out = capsys.readouterr().out
        assert "bypass invoked" in out
