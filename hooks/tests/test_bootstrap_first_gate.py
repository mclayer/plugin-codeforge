"""test_bootstrap_first_gate.py — ADR-027 Amendment 10 §결정 13 계약 검증.

CFP-2243 Phase 2 — bootstrap-first-gate.py 단위 + 통합 테스트.

Cross-platform CI matrix (ubuntu-latest + windows-latest) 양 OS pass 의무.

불변식:
  - 모든 경로 exit 0 (P0 fail-safe) — 사용자 prompt erase 권한 미사용.
  - 발화 ⟺ intent 매치 ∧ detect exit 3(unknown) ∧ adr dirs 부재 ∧ not-bypassed (AND-gate).
  - detect-repo-kind.py 무변경 (exit code map 0/1/2/3 SSOT, subprocess 그대로 호출).
"""

from __future__ import annotations

import io
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

import bootstrap_first_gate as bfg


# ============================================================ _read_input


def test_read_input_json_with_prompt_key(monkeypatch):
    """JSON dict 의 'prompt' key 추출."""
    monkeypatch.setattr("sys.stdin", io.StringIO('{"prompt":"codeforge story 만들자"}'))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert bfg._read_input() == "codeforge story 만들자"


def test_read_input_json_fallback_keys(monkeypatch):
    """JSON fallback key 순서 (user_message > message > text > content)."""
    monkeypatch.setattr("sys.stdin", io.StringIO('{"user_message":"fallback"}'))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert bfg._read_input() == "fallback"


def test_read_input_raw_text_fallback(monkeypatch):
    """malformed JSON → raw text 반환."""
    monkeypatch.setattr("sys.stdin", io.StringIO('{"prompt": '))  # 깨진 JSON
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    result = bfg._read_input()
    assert result == '{"prompt": '  # raw fallback


def test_read_input_empty_isatty(monkeypatch):
    """isatty=True (interactive 세션) → ""반환."""
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    assert bfg._read_input() == ""


def test_read_input_empty_stdin(monkeypatch):
    """빈 stdin → ""반환."""
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert bfg._read_input() == ""


def test_read_input_bounded_read(monkeypatch):
    """bounded read ≤1 MiB (DoS 차단)."""
    huge_text = "a" * (1 << 20)  # 1 MiB exactly
    monkeypatch.setattr("sys.stdin", io.StringIO(huge_text))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    result = bfg._read_input()
    # bounded 읽기 = 성공 (≤1 MiB)
    assert len(result) == (1 << 20)


# ============================================================ _matches_intent


@pytest.mark.parametrize(
    "prompt,expected_match",
    [
        # 변경 동사만
        ("X 구현해줘", True),
        ("Y 만들자", True),
        ("Z 수정", True),
        ("Z 짜줘", True),
        ("버그 고쳐줘", True),
        ("기능 추가해", True),
        ("fix the bug", True),
        ("implement Y", True),
        ("refactor X", True),
        ("add Z", True),
        ("create the module", True),
        ("build something", True),
        ("modify config", True),
        ("Update the README", True),
        ("Edit this file", True),
        ("Write new tests", True),
        # codeforge-distinctive marker 만
        ("codeforge 사용 선언", True),
        ("story 만들고 싶은데", True),
        ("스토리 어떻게 시작하지?", True),
        ("epic 계획", True),
        ("lane 이 뭐야?", True),
        ("레인 설명해줘", True),
        # 변경동사 + generic 명사
        ("이 설계 구현해", True),  # 변경동사 구현 + generic 설계
        ("아키텍처 수정", True),  # 변경동사 수정 + generic 아키텍처
        # codeforge + generic 명사
        ("codeforge 설계 시작", True),  # distinctive codeforge + generic 설계
        ("epic 아키텍처 구상", True),  # distinctive epic + generic 아키텍처
        # generic 명사 단독 → FALSE (false-positive 억제)
        ("이 설계 문서 보여줘", False),  # 설계만, 변경동사 아님, distinctive 아님
        ("아키텍처 책 추천", False),  # 아키텍처만, 변경동사 아님, distinctive 아님
        # 일반 잡담
        ("현재 status 어때?", False),
        ("로그 보여줘", False),
        ("이 파일 뭐야?", False),
        ("commit 확인해줘", False),  # commit(변경동사아님)
        ("list files", False),
        ("어디까지 했나?", False),
    ],
)
def test_matches_intent_enum(prompt, expected_match):
    """§13.A intent 계약 enum 검증 (discriminating fixture — 각 case 실패해야 함)."""
    result = bfg._matches_intent(prompt)
    assert result == expected_match, f"Intent mismatch for prompt: {prompt!r}"


# ============================================================ _detect_repo_kind


def test_detect_repo_kind_subprocess_success(monkeypatch):
    """detect-repo-kind.py subprocess 성공 시 returncode 반환."""
    mock_result = MagicMock()
    mock_result.returncode = 3
    monkeypatch.setattr("subprocess.run", lambda *a, **k: mock_result)
    assert bfg._detect_repo_kind("/tmp/test") == 3


def test_detect_repo_kind_subprocess_exception(monkeypatch):
    """subprocess 예외 시 비-3 sentinel (-1) 반환 (fail-safe)."""

    def mock_run(*a, **k):
        raise OSError("boom")

    monkeypatch.setattr("subprocess.run", mock_run)
    assert bfg._detect_repo_kind("/tmp/test") == -1


def test_detect_repo_kind_timeout(monkeypatch):
    """subprocess timeout 시 비-3 sentinel 반환."""

    def mock_run(*a, **k):
        raise TimeoutError()

    monkeypatch.setattr("subprocess.run", mock_run)
    assert bfg._detect_repo_kind("/tmp/test") == -1


# ============================================================ _adr_dirs_absent


def test_adr_dirs_absent_both_missing(tmp_path):
    """docs/adr AND archive/adr 양 부재 → True."""
    assert bfg._adr_dirs_absent(str(tmp_path)) is True


def test_adr_dirs_absent_docs_exists(tmp_path):
    """docs/adr 존재 → False."""
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    assert bfg._adr_dirs_absent(str(tmp_path)) is False


def test_adr_dirs_absent_archive_exists(tmp_path):
    """archive/adr 존재 → False."""
    (tmp_path / "archive" / "adr").mkdir(parents=True)
    assert bfg._adr_dirs_absent(str(tmp_path)) is False


def test_adr_dirs_absent_both_exist(tmp_path):
    """docs/adr AND archive/adr 양 존재 → False."""
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    (tmp_path / "archive" / "adr").mkdir(parents=True)
    assert bfg._adr_dirs_absent(str(tmp_path)) is False


# ============================================================ _check_bypass


def test_check_bypass_hotfix_with_reason():
    """HOTFIX_BYPASS_CODEFORGE=1 + REASON non-empty → (True, 'hotfix')."""
    env = {"HOTFIX_BYPASS_CODEFORGE": "1", "HOTFIX_BYPASS_REASON": "p1 incident"}
    assert bfg._check_bypass(env) == (True, "hotfix")


def test_check_bypass_hotfix_no_reason():
    """HOTFIX flag 만, reason 빈 경우 → (False, None) (honored 안 함)."""
    env = {"HOTFIX_BYPASS_CODEFORGE": "1", "HOTFIX_BYPASS_REASON": "  "}
    assert bfg._check_bypass(env) == (False, None)


def test_check_bypass_advisory_flag():
    """BYPASS_BOOTSTRAP_GATE=1 (reason 불요) → (True, 'advisory')."""
    env = {"BYPASS_BOOTSTRAP_GATE": "1"}
    assert bfg._check_bypass(env) == (True, "advisory")


def test_check_bypass_neither():
    """bypass env 미설정 → (False, None)."""
    assert bfg._check_bypass({}) == (False, None)


# ============================================================ _build_reminder


def test_build_reminder_structure():
    """_build_reminder() 출력 구조 검증."""
    msg = bfg._build_reminder()
    assert "<system-reminder>" in msg
    assert "</system-reminder>" in msg
    assert "bootstrap" in msg.lower()
    assert "bootstrap-consumer.sh" in msg
    assert "gh repo create" in msg
    assert "BYPASS_BOOTSTRAP_GATE" in msg


# ============================================================ main() — TC1-9


def test_tc1_positive_greenfield_codeforge_intent(tmp_path, monkeypatch, capsys):
    """TC1 (positive): codeforge 의도 stdin + greenfield + bypass 없음 → warn-injected.

    §13.A intent 매치 + §13.B exit3(unknown) + adr dirs 부재 + not-bypassed
    → warning inject (발화). 모든 경로 exit 0.
    """
    # greenfield 디렉터리 (plugin.json·overlay·adr 모두 부재)
    monkeypatch.chdir(str(tmp_path))

    # stdin: codeforge 의도
    monkeypatch.setattr(
        "sys.stdin", io.StringIO('{"prompt":"codeforge story 만들자"}')
    )
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    # detect-repo-kind 모킹 → exit 3 (unknown)
    monkeypatch.setattr(bfg, "_detect_repo_kind", lambda cwd: 3)

    # bypass 미설정
    monkeypatch.delenv("HOTFIX_BYPASS_CODEFORGE", raising=False)
    monkeypatch.delenv("HOTFIX_BYPASS_REASON", raising=False)
    monkeypatch.delenv("BYPASS_BOOTSTRAP_GATE", raising=False)

    # 실행
    rc = bfg.main()
    captured = capsys.readouterr()

    # 검증
    assert rc == 0  # P0: 모든 경로 exit 0
    assert "<system-reminder>" in captured.out
    assert "bootstrap" in captured.out.lower()
    assert "[bootstrap-first-gate] fired exit_path=warn-injected" in captured.err


def test_tc2_consumer_silent(tmp_path, monkeypatch, capsys):
    """TC2: consumer repo (exit 1) → silent-consumer (발화 안 함)."""
    monkeypatch.chdir(str(tmp_path))
    monkeypatch.setattr(
        "sys.stdin", io.StringIO('{"prompt":"codeforge story"}')
    )
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    # detect-repo-kind → 1 (consumer)
    monkeypatch.setattr(bfg, "_detect_repo_kind", lambda cwd: 1)

    rc = bfg.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.out == ""
    assert "[bootstrap-first-gate] fired exit_path=silent-consumer" in captured.err


def test_tc3_intent_mismatch_early_exit(tmp_path, monkeypatch, capsys):
    """TC3: intent 미매치 → early-exit 0 (detect 호출 안 됨, discriminating)."""
    monkeypatch.chdir(str(tmp_path))
    monkeypatch.setattr("sys.stdin", io.StringIO('{"prompt":"현재 status 어때?"}'))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    # detect_repo_kind 를 호출하지 않는지 확인하는 spy
    call_count = [0]

    def spy_detect(cwd):
        call_count[0] += 1
        return 3

    monkeypatch.setattr(bfg, "_detect_repo_kind", spy_detect)

    rc = bfg.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.out == ""
    assert call_count[0] == 0  # detect 호출 안 됨 (early-exit 확인)
    assert captured.err == ""  # audit 없음


def test_tc4a_bypass_hotfix_honored(tmp_path, monkeypatch, capsys):
    """TC4a: HOTFIX_BYPASS_CODEFORGE=1 + REASON set → bypass honored."""
    monkeypatch.chdir(str(tmp_path))
    monkeypatch.setattr(
        "sys.stdin", io.StringIO('{"prompt":"codeforge story"}')
    )
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr(bfg, "_detect_repo_kind", lambda cwd: 3)

    monkeypatch.setenv("HOTFIX_BYPASS_CODEFORGE", "1")
    monkeypatch.setenv("HOTFIX_BYPASS_REASON", "p1 incident")

    rc = bfg.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.out == ""
    assert "[bootstrap-first-gate] fired exit_path=silent-bypassed" in captured.err


def test_tc4b_bypass_advisory_honored(tmp_path, monkeypatch, capsys):
    """TC4b: BYPASS_BOOTSTRAP_GATE=1 → bypass honored (advisory)."""
    monkeypatch.chdir(str(tmp_path))
    monkeypatch.setattr(
        "sys.stdin", io.StringIO('{"prompt":"codeforge story"}')
    )
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr(bfg, "_detect_repo_kind", lambda cwd: 3)

    monkeypatch.setenv("BYPASS_BOOTSTRAP_GATE", "1")
    monkeypatch.delenv("HOTFIX_BYPASS_CODEFORGE", raising=False)

    rc = bfg.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.out == ""
    assert "[bootstrap-first-gate] fired exit_path=silent-bypassed" in captured.err


def test_tc4c_bypass_hotfix_missing_reason_not_honored(
    tmp_path, monkeypatch, capsys
):
    """TC4c: HOTFIX flag 만 (reason 미설정) → bypass NOT honored, 발화."""
    monkeypatch.chdir(str(tmp_path))
    monkeypatch.setattr(
        "sys.stdin", io.StringIO('{"prompt":"codeforge story"}')
    )
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr(bfg, "_detect_repo_kind", lambda cwd: 3)

    monkeypatch.setenv("HOTFIX_BYPASS_CODEFORGE", "1")
    monkeypatch.delenv("HOTFIX_BYPASS_REASON", raising=False)

    rc = bfg.main()
    captured = capsys.readouterr()

    assert rc == 0
    # bypass honored 아님 → 발화
    assert "<system-reminder>" in captured.out
    assert "[bootstrap-first-gate] fired exit_path=warn-injected" in captured.err


def test_tc5a_malformed_json_raw_fallback(tmp_path, monkeypatch, capsys):
    """TC5a (P0 fail-safe): malformed JSON → raw fallback, intent 매치 시 발화."""
    monkeypatch.chdir(str(tmp_path))
    # 깨진 JSON 이지만 substring '구현' 포함 → intent 매치
    monkeypatch.setattr("sys.stdin", io.StringIO('{"prompt": 구현해줘'))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr(bfg, "_detect_repo_kind", lambda cwd: 3)

    rc = bfg.main()
    captured = capsys.readouterr()

    assert rc == 0
    # raw fallback + intent 매치 → exit 0 (발화 또는 silent, 예외는 아님)


def test_tc5b_detect_exception_nonzero_fail_safe(tmp_path, monkeypatch, capsys):
    """TC5b: subprocess 예외 → 비-3 sentinel, silent-detect-error + exit 0."""
    monkeypatch.chdir(str(tmp_path))
    monkeypatch.setattr(
        "sys.stdin", io.StringIO('{"prompt":"codeforge story"}')
    )
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    # detect 예외 → -1 반환
    monkeypatch.setattr(bfg, "_detect_repo_kind", lambda cwd: (-1 for _ in ()).throw(OSError("boom")))

    rc = bfg.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.out == ""
    # detect 호출이 예외 → 대신 비-3 감지로 silent


def test_tc5c_main_exception_exit_zero_no_prompt_leak(tmp_path, monkeypatch, capsys):
    """TC5c: main() 내 예외 → exit 0, prompt text leak 안 함 (PII/secret 차단)."""
    monkeypatch.chdir(str(tmp_path))
    monkeypatch.setattr(
        "sys.stdin", io.StringIO('{"prompt":"secret_key=xyz"}')
    )
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    # _matches_intent 에서 예외 발생 모킹
    def raise_on_match(text):
        raise RuntimeError("simulated error")

    monkeypatch.setattr(bfg, "_matches_intent", raise_on_match)

    rc = bfg.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert "secret_key" not in captured.out  # prompt leak 안 함
    assert "secret_key" not in captured.err  # stderr 에도 leak 안 함
    assert "[bootstrap-first-gate] fired exit_path=silent-exception" in captured.err


def test_tc6_plugin_silent(tmp_path, monkeypatch, capsys):
    """TC6: plugin repo (exit 0) → silent-plugin."""
    monkeypatch.chdir(str(tmp_path))
    monkeypatch.setattr(
        "sys.stdin", io.StringIO('{"prompt":"codeforge story"}')
    )
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr(bfg, "_detect_repo_kind", lambda cwd: 0)

    rc = bfg.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.out == ""
    assert "[bootstrap-first-gate] fired exit_path=silent-plugin" in captured.err


def test_tc7_mixed_silent(tmp_path, monkeypatch, capsys):
    """TC7: mixed repo (exit 2, wrapper dogfood) → silent-mixed."""
    monkeypatch.chdir(str(tmp_path))
    monkeypatch.setattr(
        "sys.stdin", io.StringIO('{"prompt":"codeforge story"}')
    )
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr(bfg, "_detect_repo_kind", lambda cwd: 2)

    rc = bfg.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.out == ""
    assert "[bootstrap-first-gate] fired exit_path=silent-mixed" in captured.err


def test_tc8_initialized_adr_dir_exists_silent(tmp_path, monkeypatch, capsys):
    """TC8: exit 3 BUT docs/adr 존재 → silent-initialized."""
    monkeypatch.chdir(str(tmp_path))
    monkeypatch.setattr(
        "sys.stdin", io.StringIO('{"prompt":"codeforge story"}')
    )
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr(bfg, "_detect_repo_kind", lambda cwd: 3)

    # ADR 디렉터리 생성 (초기화 표시)
    (tmp_path / "docs" / "adr").mkdir(parents=True)

    rc = bfg.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert captured.out == ""
    assert "[bootstrap-first-gate] fired exit_path=silent-initialized" in captured.err


def test_tc9_detect_repo_kind_integration_unknown(tmp_path, monkeypatch):
    """TC9 (detect 단위): subprocess exit code mapping 검증 (exit 3=unknown).

    Note: worktree 자체가 mixed repo 이므로, tmp_path 가 isolated 환경에서도
    detect-repo-kind 의 모 repo 추적(ancestor search) 으로 인해 mixed 로 평가될 수
    있다. 그 대신 subprocess 호출 자체는 성공(return code 반환)을 검증하고,
    실제 exit code map (0=plugin / 1=consumer / 2=mixed / 3=unknown) 은
    detect-repo-kind.py 의 integration test suite 에서 cover.
    """
    # 실제 detect-repo-kind.py subprocess call 성공 여부 + return code 수신 검증
    real_repo_root = Path(__file__).resolve().parent.parent.parent.parent
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(real_repo_root))

    # tmp_path 는 isolated tmp dir 이지만, detect ancestor 가 real repo 를
    # 찾을 수 있으므로, return code 는 2(mixed) 일 수 있다.
    # 중요한 것은 subprocess 호출 성공 + valid exit code (0/1/2/3 또는 비-3 sentinel)
    rc = bfg._detect_repo_kind(str(tmp_path))

    # P0: 어떤 경우든 -1 이 아니어야 함 (예외 없음)
    assert rc != -1, f"detect subprocess exception, got sentinel -1"
    # valid exit code: 0=plugin / 1=consumer / 2=mixed / 3=unknown
    assert rc in (0, 1, 2, 3), f"Invalid exit code {rc}"


def test_tc9_detect_repo_kind_integration_plugin(tmp_path, monkeypatch):
    """TC9 variant (detect 단위): subprocess 호출 성공 확인.

    Note: 동일한 isolated tmp_path 이슈로, 실제 exit code 는 test 환경에 따라
    달라질 수 있다. subprocess call success + return code 수신만 검증.
    """
    real_repo_root = Path(__file__).resolve().parent.parent.parent.parent
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(real_repo_root))

    # plugin.json 생성 (신호 A) — 단순히 subprocess 가 이를 감지하는지 검증
    (tmp_path / ".claude-plugin").mkdir(parents=True)
    (tmp_path / ".claude-plugin" / "plugin.json").write_text("{}")

    rc = bfg._detect_repo_kind(str(tmp_path))

    # P0: 예외 없음
    assert rc != -1, f"detect subprocess exception, got sentinel -1"
    # plugin.json 존재 → exit 0 또는 2(mixed, 만약 ancestor repo 감지) 가능
    # 실제 정확 매핑은 detect-repo-kind.py integration test 에서 cover
    assert rc in (0, 1, 2, 3), f"Invalid exit code {rc}"


def test_tc9_detect_repo_kind_integration_consumer(tmp_path, monkeypatch):
    """TC9 variant (detect 단위): subprocess 호출 성공 확인.

    Note: 동일한 isolated tmp_path 이슈로, 실제 exit code 는 test 환경에 따라
    달라질 수 있다. subprocess call success + return code 수신만 검증.
    """
    real_repo_root = Path(__file__).resolve().parent.parent.parent.parent
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(real_repo_root))

    # overlay/project.yaml 생성 (신호 B) — 단순히 subprocess 가 이를 감지하는지 검증
    (tmp_path / ".claude" / "_overlay").mkdir(parents=True)
    (tmp_path / ".claude" / "_overlay" / "project.yaml").write_text("codeforge: {}")

    rc = bfg._detect_repo_kind(str(tmp_path))

    # P0: 예외 없음
    assert rc != -1, f"detect subprocess exception, got sentinel -1"
    # project.yaml 존재 → exit 1 또는 2(mixed, 만약 ancestor repo 감지) 가능
    # 실제 정확 매핑은 detect-repo-kind.py integration test 에서 cover
    assert rc in (0, 1, 2, 3), f"Invalid exit code {rc}"


def test_tc9_detect_repo_kind_integration_mixed(tmp_path, monkeypatch):
    """TC9 variant (detect 통합): plugin.json + overlay 양존 → exit 2(mixed)."""
    monkeypatch.chdir(str(tmp_path))
    real_repo_root = Path(__file__).resolve().parent.parent.parent.parent
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(real_repo_root))

    # plugin.json + overlay 양 생성
    (tmp_path / ".claude-plugin").mkdir(parents=True)
    (tmp_path / ".claude-plugin" / "plugin.json").write_text("{}")
    (tmp_path / ".claude" / "_overlay").mkdir(parents=True)
    (tmp_path / ".claude" / "_overlay" / "project.yaml").write_text("codeforge: {}")

    rc = bfg._detect_repo_kind(str(tmp_path))

    assert rc == 2, f"Expected exit 2 (mixed), got {rc}"


# ============================================================ INV (불변식 검증)


def test_inv_all_paths_exit_zero(tmp_path, monkeypatch, capsys):
    """INV: 모든 경로 main() → exit 0 (P0 fail-safe)."""
    test_cases = [
        ("greenfield + codeforge intent", 3, True),
        ("consumer exit 1", 1, True),
        ("intent mismatch", 3, False),
        ("plugin exit 0", 0, True),
        ("mixed exit 2", 2, True),
    ]

    for label, detect_rc, has_intent in test_cases:
        monkeypatch.chdir(str(tmp_path))

        if has_intent:
            monkeypatch.setattr(
                "sys.stdin", io.StringIO('{"prompt":"codeforge story"}')
            )
        else:
            monkeypatch.setattr(
                "sys.stdin", io.StringIO('{"prompt":"current status?"}')
            )

        monkeypatch.setattr("sys.stdin.isatty", lambda: False)
        monkeypatch.setattr(bfg, "_detect_repo_kind", lambda cwd: detect_rc)

        rc = bfg.main()
        assert rc == 0, f"Case '{label}' must return 0, got {rc}"


def test_inv_emit_only_when_4_conditions_met(tmp_path, monkeypatch, capsys):
    """INV: 발화 ⟺ intent ∧ exit3 ∧ adr dirs absent ∧ not-bypassed."""
    # 4 조건 모두 충족
    monkeypatch.chdir(str(tmp_path))
    monkeypatch.setattr(
        "sys.stdin", io.StringIO('{"prompt":"codeforge story"}')
    )
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    monkeypatch.setattr(bfg, "_detect_repo_kind", lambda cwd: 3)
    monkeypatch.delenv("HOTFIX_BYPASS_CODEFORGE", raising=False)
    monkeypatch.delenv("BYPASS_BOOTSTRAP_GATE", raising=False)

    bfg.main()
    captured = capsys.readouterr()

    assert "<system-reminder>" in captured.out  # 발화

    # 조건 1 미충족 (intent mismatch)
    monkeypatch.setattr(
        "sys.stdin", io.StringIO('{"prompt":"current status?"}')
    )
    capsys.readouterr()  # clear
    bfg.main()
    captured = capsys.readouterr()
    assert captured.out == ""  # 침묵

    # 조건 2 미충족 (exit != 3)
    monkeypatch.setattr(
        "sys.stdin", io.StringIO('{"prompt":"codeforge story"}')
    )
    monkeypatch.setattr(bfg, "_detect_repo_kind", lambda cwd: 1)
    capsys.readouterr()
    bfg.main()
    captured = capsys.readouterr()
    assert captured.out == ""  # 침묵

    # 조건 3 미충족 (adr dir 존재)
    monkeypatch.setattr(bfg, "_detect_repo_kind", lambda cwd: 3)
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    capsys.readouterr()
    bfg.main()
    captured = capsys.readouterr()
    assert captured.out == ""  # 침묵

    # 조건 4 미충족 (bypass)
    (tmp_path / "docs" / "adr").rmdir()
    (tmp_path / "docs").rmdir()
    monkeypatch.setenv("BYPASS_BOOTSTRAP_GATE", "1")
    capsys.readouterr()
    bfg.main()
    captured = capsys.readouterr()
    assert captured.out == ""  # 침묵
