"""CFP-104 — userprompt_reminder.py 단위 테스트.

Cross-platform CI matrix (ubuntu-latest + windows-latest) 양 OS pass 의무.
"""

from __future__ import annotations

import io

import pytest

import userprompt_reminder as upr


# ============================================================ _read_input


def test_read_input_json_with_prompt_key(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO('{"prompt": "X 구현해줘"}'))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert upr._read_input() == "X 구현해줘"


def test_read_input_json_with_user_message_key(monkeypatch):
    monkeypatch.setattr(
        "sys.stdin", io.StringIO('{"user_message": "fix bug", "session_id": "x"}')
    )
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert upr._read_input() == "fix bug"


def test_read_input_raw_text_fallback(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("plain text 구현"))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert upr._read_input() == "plain text 구현"


def test_read_input_empty_isatty(monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    assert upr._read_input() == ""


def test_read_input_empty_stdin(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert upr._read_input() == ""


def test_read_input_json_array_returns_raw(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO('["not", "a", "dict"]'))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    # Arrays not dicts — raw fallback.
    result = upr._read_input()
    assert result == '["not", "a", "dict"]'


# ============================================================ _matches_change_intent


@pytest.mark.parametrize(
    "prompt",
    [
        "X 구현해줘",
        "Y 만들자",
        "Z 수정",
        "Z 짜줘",
        "버그 고쳐줘",
        "기능 추가해",
        "fix the bug",
        "implement Y",
        "refactor X",
        "add Z",
        "create the new module",
        "build something",
        "modify config",
        "Update the README",
        "Edit this file",
        "Write new tests",
    ],
)
def test_matches_change_intent_positive(prompt):
    assert upr._matches_change_intent(prompt), f"should match: {prompt!r}"


@pytest.mark.parametrize(
    "prompt",
    [
        "현황은 어때?",
        "what's there?",
        "show me logs",
        "commit log",
        "list files",
        "현재 status?",
        "어디까지 했나?",
        "Can you explain this?",
    ],
)
def test_matches_change_intent_no_false_positive(prompt):
    assert not upr._matches_change_intent(prompt), f"should NOT match: {prompt!r}"


def test_matches_change_intent_custom_patterns():
    import re
    pats = [re.compile(r"foo", re.IGNORECASE)]
    assert upr._matches_change_intent("foobar", pats)
    assert not upr._matches_change_intent("baz", pats)


# ============================================================ _detect_active_story


def test_detect_active_story_cfp(monkeypatch):
    monkeypatch.setattr(upr, "_run_git_branch", lambda: "cfp-104/userprompt-reminder")
    key, phase = upr._detect_active_story()
    assert key == "CFP-104"
    assert phase == "userprompt-reminder"


def test_detect_active_story_mct(monkeypatch):
    monkeypatch.setattr(upr, "_run_git_branch", lambda: "mct-63/epic-close")
    key, phase = upr._detect_active_story()
    assert key == "MCT-63"
    assert phase == "epic-close"


def test_detect_active_story_no_phase(monkeypatch):
    monkeypatch.setattr(upr, "_run_git_branch", lambda: "cfp-96")
    key, phase = upr._detect_active_story()
    assert key == "CFP-96"
    assert phase is None


def test_detect_active_story_main(monkeypatch):
    monkeypatch.setattr(upr, "_run_git_branch", lambda: "main")
    assert upr._detect_active_story() == (None, None)


def test_detect_active_story_other_prefix(monkeypatch):
    monkeypatch.setattr(upr, "_run_git_branch", lambda: "feat/something")
    assert upr._detect_active_story() == (None, None)


def test_detect_active_story_empty_branch(monkeypatch):
    monkeypatch.setattr(upr, "_run_git_branch", lambda: "")
    assert upr._detect_active_story() == (None, None)


def test_detect_active_story_uppercase(monkeypatch):
    monkeypatch.setattr(upr, "_run_git_branch", lambda: "CFP-200/foo")
    key, phase = upr._detect_active_story()
    assert key == "CFP-200"
    assert phase == "foo"


# ============================================================ _check_bypass


def test_check_bypass_full():
    env = {"HOTFIX_BYPASS_CODEFORGE": "1", "HOTFIX_BYPASS_REASON": "p1 incident"}
    assert upr._check_bypass(env) == (True, "p1 incident")


def test_check_bypass_flag_only_no_reason():
    env = {"HOTFIX_BYPASS_CODEFORGE": "1"}
    assert upr._check_bypass(env) == (False, "REASON_MISSING")


def test_check_bypass_flag_with_empty_reason():
    env = {"HOTFIX_BYPASS_CODEFORGE": "1", "HOTFIX_BYPASS_REASON": "  "}
    assert upr._check_bypass(env) == (False, "REASON_MISSING")


def test_check_bypass_flag_zero():
    env = {"HOTFIX_BYPASS_CODEFORGE": "0", "HOTFIX_BYPASS_REASON": "ignored"}
    assert upr._check_bypass(env) == (False, None)


def test_check_bypass_neither():
    assert upr._check_bypass({}) == (False, None)


# ============================================================ _build_reminder


def test_build_reminder_with_story():
    msg = upr._build_reminder("CFP-104", "userprompt-reminder", False)
    assert "<system-reminder>" in msg
    assert "</system-reminder>" in msg
    assert "CFP-104" in msg
    assert "userprompt-reminder" in msg
    assert "ADR-027" in msg
    assert "ADR-022" in msg


def test_build_reminder_no_story():
    msg = upr._build_reminder(None, None, False)
    assert "활성 Story 미검출" in msg
    assert "story.yml" in msg


def test_build_reminder_no_phase():
    msg = upr._build_reminder("CFP-104", None, False)
    assert "CFP-104" in msg
    assert "branch phase" not in msg


def test_build_reminder_bypass_warn():
    msg = upr._build_reminder(None, None, True)
    assert "WARN" in msg
    assert "REASON" in msg
    assert "Bypass NOT honored" in msg


def test_build_reminder_no_bypass_warn():
    msg = upr._build_reminder(None, None, False)
    assert "Bypass NOT honored" not in msg


# ============================================================ main()


def test_main_change_request_emits_reminder(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO('{"prompt": "X 구현해줘"}'))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr(upr, "_run_git_branch", lambda: "cfp-104/test")
    monkeypatch.delenv("HOTFIX_BYPASS_CODEFORGE", raising=False)
    monkeypatch.delenv("HOTFIX_BYPASS_REASON", raising=False)
    rc = upr.main()
    captured = capsys.readouterr()
    assert rc == 0
    assert "<system-reminder>" in captured.out
    assert "CFP-104" in captured.out


def test_main_no_change_intent_silent(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO('{"prompt": "현황은?"}'))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    rc = upr.main()
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out == ""
    assert captured.err == ""


def test_main_bypass_silent_with_audit_log(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO('{"prompt": "X 구현해줘"}'))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setenv("HOTFIX_BYPASS_CODEFORGE", "1")
    monkeypatch.setenv("HOTFIX_BYPASS_REASON", "p1 incident")
    rc = upr.main()
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out == ""
    assert "BYPASS" in captured.err
    assert "p1 incident" in captured.err


def test_main_bypass_flag_only_emits_reminder_with_warn(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO('{"prompt": "X 구현해줘"}'))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr(upr, "_run_git_branch", lambda: "main")
    monkeypatch.setenv("HOTFIX_BYPASS_CODEFORGE", "1")
    monkeypatch.delenv("HOTFIX_BYPASS_REASON", raising=False)
    rc = upr.main()
    captured = capsys.readouterr()
    assert rc == 0
    assert "<system-reminder>" in captured.out
    assert "Bypass NOT honored" in captured.out


def test_main_empty_input_silent(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    rc = upr.main()
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out == ""


def test_main_raw_text_change_intent(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("저 함수 좀 수정해줘"))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr(upr, "_run_git_branch", lambda: "")
    monkeypatch.delenv("HOTFIX_BYPASS_CODEFORGE", raising=False)
    rc = upr.main()
    captured = capsys.readouterr()
    assert rc == 0
    assert "<system-reminder>" in captured.out
    assert "활성 Story 미검출" in captured.out
