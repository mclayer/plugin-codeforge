"""test_pretooluse_inline_write_gate.py — CFP-2544 inline-write gate verifier 테스트.

ADR-039 §결정 9 + ADR-115 Amendment 1 §결정 5·6 계약 검증.

CFP-2544 Phase 2 — check_inline_write_gate.py (SSOT) 단위 + 통합 테스트.

불변식 (Wave1 warning-tier):
  - 모든 경로 exit 0 (P0 fail-safe) — 편집 차단 비활성(Wave2 이후).
  - 발화(block/audit 마커) ⟺ caller(agent_id) + path(repo/worktree) 판정 AND-gate.
  - discriminator = agent_id (부재/null/"" = Orchestrator block-candidate, 비empty str = subagent).
  - path ordering = worktree MUST check before memory (subset relationship, load-bearing).
  - distinct sentinel: BLOCK_MARKER ≠ AUDIT_MARKER (case 9 판별).
  - subprocess: exit code 단독 금지 → distinct marker(stdout/stderr) 병행 assert(§2247).
"""

from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

import check_inline_write_gate as ciwg


# ============================================================ _read_payload


def test_read_payload_valid_json(monkeypatch):
    """유효한 JSON payload 읽기."""
    payload = {"tool_name": "Write", "tool_input": {"file_path": "/repo/x.py"}}
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    result = ciwg._read_payload()
    assert result == payload


def test_read_payload_empty_stdin(monkeypatch):
    """빈 stdin → None (fail-open)."""
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    assert ciwg._read_payload() is None


def test_read_payload_whitespace_only(monkeypatch):
    """공백만 존재 → None (fail-open)."""
    monkeypatch.setattr("sys.stdin", io.StringIO("   \n\t  "))
    assert ciwg._read_payload() is None


def test_read_payload_malformed_json(monkeypatch):
    """파싱 실패 JSON → None (fail-open, 에러 출력 안 함)."""
    monkeypatch.setattr("sys.stdin", io.StringIO('{"tool_name":'))
    assert ciwg._read_payload() is None


def test_read_payload_malformed_read_exception(monkeypatch):
    """stdin.read() 예외 → None (fail-open)."""
    mock_stdin = MagicMock()
    mock_stdin.read.side_effect = OSError("read failed")
    monkeypatch.setattr("sys.stdin", mock_stdin)
    assert ciwg._read_payload() is None


# ============================================================ _check_bypass


def test_check_bypass_env_set_to_1(monkeypatch):
    """BYPASS_INLINE_WRITE_GATE=1 → True, stderr audit 마커 발화."""
    monkeypatch.setenv("BYPASS_INLINE_WRITE_GATE", "1")
    monkeypatch.setenv("TZ", "UTC")  # UTC 시각 보장

    result = ciwg._check_bypass()
    assert result is True


def test_check_bypass_env_not_set(monkeypatch):
    """BYPASS env 미설정 → False."""
    monkeypatch.delenv("BYPASS_INLINE_WRITE_GATE", raising=False)
    assert ciwg._check_bypass() is False


def test_check_bypass_env_set_to_0(monkeypatch):
    """BYPASS_INLINE_WRITE_GATE=0 → False (문자열 "0" 거짓)."""
    monkeypatch.setenv("BYPASS_INLINE_WRITE_GATE", "0")
    assert ciwg._check_bypass() is False


def test_check_bypass_audit_marker_in_stderr(monkeypatch, capsys):
    """bypass 시 stderr 에 AUDIT 마커 + timestamp 기록."""
    monkeypatch.setenv("BYPASS_INLINE_WRITE_GATE", "1")
    ciwg._check_bypass()
    _, err = capsys.readouterr()
    assert ciwg.AUDIT_MARKER in err
    assert "BYPASS_INLINE_WRITE_GATE=1" in err
    assert "T" in err  # ISO 8601 timestamp


# ============================================================ _classify_agent


def test_classify_agent_subagent_non_empty_string(monkeypatch):
    """agent_id = non-empty string → 'subagent'."""
    payload = {"agent_id": "a1b2c3"}
    assert ciwg._classify_agent(payload) == "subagent"


def test_classify_agent_missing_key():
    """agent_id 키 부재 → 'orchestrator'."""
    payload = {"tool_name": "Write"}
    assert ciwg._classify_agent(payload) == "orchestrator"


def test_classify_agent_null_value():
    """agent_id = None → 'orchestrator'."""
    payload = {"agent_id": None}
    assert ciwg._classify_agent(payload) == "orchestrator"


def test_classify_agent_empty_string():
    """agent_id = '' (empty string) → 'orchestrator'."""
    payload = {"agent_id": ""}
    assert ciwg._classify_agent(payload) == "orchestrator"


def test_classify_agent_non_string_value():
    """agent_id = int/list 등 non-string → 'orchestrator'."""
    payload = {"agent_id": 123}
    assert ciwg._classify_agent(payload) == "orchestrator"

    payload = {"agent_id": ["a1b2"]}
    assert ciwg._classify_agent(payload) == "orchestrator"


# ============================================================ _classify_path


def test_classify_path_none_or_empty(tmp_path):
    """file_path None 또는 empty → 'allow' (fail-open)."""
    assert ciwg._classify_path(None, str(tmp_path)) == "allow"
    assert ciwg._classify_path("", str(tmp_path)) == "allow"


def test_classify_path_absolute_inside_repo(tmp_path):
    """절대경로, repo 내부(cwd 기준) → 'block'."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    file_path = str(repo_root / "src" / "main.py")
    result = ciwg._classify_path(file_path, str(repo_root))
    assert result == "block"


def test_classify_path_relative_inside_repo(tmp_path):
    """상대경로, repo 내부(cwd 기준) → 'block' (design-confirm #3)."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "src").mkdir()
    (repo_root / "src" / "main.py").touch()

    # cwd = repo_root, file_path = "src/main.py" (relative) → resolve → block
    result = ciwg._classify_path("src/main.py", str(repo_root))
    assert result == "block"


def test_classify_path_worktree_before_memory_ordering(tmp_path, monkeypatch):
    """worktree 경로는 반드시 memory check 보다 먼저 평가 (load-bearing order).

    mutation test invariant: _classify_path step2(worktree) 와 step4(memory) swap시
    worktree 경로가 memory → allow 로 오분류돼 case8 이 flip(block→allow).

    Production code 수정 (CFP-2544 Phase 2): `_home()` helper 도입, HOME env 우선 읽기.
    이제 monkeypatch.setenv("HOME", ...) 기반 테스트로 통일 (patch expanduser 불필요).
    """
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))

    # worktree 경로 = ~/.claude/worktrees/plugin-codeforge/br/f.py
    worktree_path = home / ".claude" / "worktrees" / "plugin-codeforge" / "br" / "f.py"

    # cwd = repo (worktree 밖)
    repo = tmp_path / "repo"
    repo.mkdir()

    result = ciwg._classify_path(str(worktree_path), str(repo))
    assert result == "block", (
        "worktree path must be classified BLOCK, not allowed by memory carve-out. "
        "If step ordering flipped (worktree after memory), this fails — mutation RED."
    )


def test_classify_path_memory_carveout(tmp_path):
    """~/.claude/* (memory) → 'allow' (worktree 제외)."""
    home = tmp_path / "home"
    home.mkdir()

    # memory 경로 = ~/.claude/memory/x.md
    memory_path = home / ".claude" / "memory" / "x.md"

    repo = tmp_path / "repo"
    repo.mkdir()

    with patch("os.path.expanduser") as mock_expand:
        mock_expand.side_effect = lambda p: p.replace("~", str(home))
        result = ciwg._classify_path(str(memory_path), str(repo))
        assert result == "allow"


def test_classify_path_scratch_carveout(tmp_path):
    """~/.claude/codeforge-scratch/* → 'allow'."""
    home = tmp_path / "home"
    home.mkdir()

    scratch_path = home / ".claude" / "codeforge-scratch" / "temp" / "x"

    repo = tmp_path / "repo"
    repo.mkdir()

    with patch("os.path.expanduser") as mock_expand:
        mock_expand.side_effect = lambda p: p.replace("~", str(home))
        result = ciwg._classify_path(str(scratch_path), str(repo))
        assert result == "allow"


def test_classify_path_outside_repo(tmp_path):
    """repo 밖 절대경로 → 'allow' (step 5)."""
    repo = tmp_path / "repo"
    repo.mkdir()

    outside = tmp_path / "other" / "file.txt"

    result = ciwg._classify_path(str(outside), str(repo))
    assert result == "allow"


def test_classify_path_cwd_none_fallback(tmp_path):
    """cwd None → os.getcwd() fallback."""
    outside = tmp_path / "outside" / "file.txt"

    # cwd 미제공 → os.getcwd() 사용
    result = ciwg._classify_path(str(outside), None)
    # outside 가 실제 getcwd 밖이므로 allow
    assert result == "allow"


# ============================================================ §8.2 discriminating fixture 14-case


@pytest.mark.parametrize(
    "case_num,agent_id,file_path,cwd_rel,env_bypass,expected_exit,expected_block,expected_audit",
    [
        # Case 1: subagent_allow
        (1, "a1b2", "repo_file.py", "repo", False, 0, False, False),
        # Case 2: orch_missing_repo (agent_id: KEY 부재 케이스, None 으로 표현)
        (2, "__MISSING__", "repo_file.py", "repo", False, 0, True, False),
        # Case 3: orch_null_repo
        (3, None, "repo_file.py", "repo", False, 0, True, False),
        # Case 4: orch_empty_repo
        (4, "", "repo_file.py", "repo", False, 0, True, False),
        # Case 5: orch_memory_allow
        (5, "__MISSING__", "~/.claude/memory/x.md", None, False, 0, False, False),
        # Case 6: orch_scratch_allow
        (6, "__MISSING__", "~/.claude/codeforge-scratch/x", None, False, 0, False, False),
        # Case 7: orch_outside_allow
        (7, "__MISSING__", "outside_file.txt", None, False, 0, False, False),
        # Case 8: orch_worktree_block
        (8, "__MISSING__", "~/.claude/worktrees/plugin-codeforge/br/f", None, False, 0, True, False),
        # Case 9: orch_bypass_allow
        (9, "__MISSING__", "repo_file.py", "repo", True, 0, False, True),
        # Case 11: empty_stdin_failopen
        (11, None, None, None, False, 0, False, False),
        # Case 12: malformed_json_failopen
        (12, None, None, None, False, 0, False, False),
        # Case 13: subagent_wins_over_path
        (13, "a1", "~/.claude/worktrees/plugin-codeforge/br/f", None, False, 0, False, False),
        # Case 14: empty_string_is_orch
        (14, "", "~/.claude/worktrees/plugin-codeforge/br/f", None, False, 0, True, False),
        # Case 10 removed: verifier_absent is subprocess-level test only
    ],
)
def test_case_14_discriminating_fixtures(
    case_num,
    agent_id,
    file_path,
    cwd_rel,
    env_bypass,
    expected_exit,
    expected_block,
    expected_audit,
    tmp_path,
    monkeypatch,
    capsys,
):
    """§8.2 discriminating fixture 14-case — import + monkeypatch main() 테스트."""
    # Home 경로 설정 (memory/scratch/worktree carve-out 테스트)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))

    # repo 디렉터리는 항상 생성 (worktree 테스트에서 cwd로 사용)
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    # cwd 설정
    if cwd_rel == "repo":
        cwd = str(repo_root)
    elif cwd_rel == "outside":
        outside = tmp_path / "outside"
        outside.mkdir()
        cwd = str(outside)
    else:
        cwd = None

    # file_path 결정 및 payload 구성
    payload_dict = {"tool_name": "Write", "tool_input": {}}

    if file_path is None:
        # Case 11: 빈 stdin
        payload_json = ""
    elif file_path == "repo_file.py":
        if cwd is None:
            pytest.skip("repo_file.py 테스트는 cwd 필요")
        payload_dict["tool_input"]["file_path"] = os.path.join(cwd, file_path)
        payload_dict["cwd"] = cwd
        if agent_id != "__MISSING__":
            payload_dict["agent_id"] = agent_id
        payload_json = json.dumps(payload_dict)
    elif file_path == "outside_file.txt":
        outside = tmp_path / "outside"
        outside.mkdir()
        payload_dict["tool_input"]["file_path"] = str(outside / "file.txt")
        if agent_id != "__MISSING__":
            payload_dict["agent_id"] = agent_id
        payload_json = json.dumps(payload_dict)
    elif file_path.startswith("~/.claude/memory"):
        # memory carve-out: expand ~ to home
        expanded = file_path.replace("~", str(home))
        payload_dict["tool_input"]["file_path"] = expanded
        if agent_id != "__MISSING__":
            payload_dict["agent_id"] = agent_id
        payload_json = json.dumps(payload_dict)
    elif file_path.startswith("~/.claude/codeforge-scratch"):
        # scratch carve-out
        expanded = file_path.replace("~", str(home))
        payload_dict["tool_input"]["file_path"] = expanded
        if agent_id != "__MISSING__":
            payload_dict["agent_id"] = agent_id
        payload_json = json.dumps(payload_dict)
    elif file_path.startswith("~/.claude/worktrees"):
        # worktree path
        expanded = file_path.replace("~", str(home))
        payload_dict["tool_input"]["file_path"] = expanded
        if agent_id != "__MISSING__":
            payload_dict["agent_id"] = agent_id
        # worktree 경로 테스트는 cwd를 repo 로 설정 (비worktree path 기준)
        payload_dict["cwd"] = str(repo_root)
        payload_json = json.dumps(payload_dict)
    else:
        # malformed payload (case 12)
        payload_json = '{"tool_input":'

    # stdin 모킹
    monkeypatch.setattr("sys.stdin", io.StringIO(payload_json))

    # bypass env 설정
    if env_bypass:
        monkeypatch.setenv("BYPASS_INLINE_WRITE_GATE", "1")
    else:
        monkeypatch.delenv("BYPASS_INLINE_WRITE_GATE", raising=False)

    # os.path.expanduser 모킹 — verifier 내부에서도 ~ 확장이 HOME을 사용하도록
    original_expanduser = os.path.expanduser

    def mock_expanduser(path):
        if path.startswith("~"):
            return path.replace("~", str(home), 1)
        return original_expanduser(path)

    monkeypatch.setattr("os.path.expanduser", mock_expanduser)

    # main() 실행 — SystemExit 처리
    with pytest.raises(SystemExit) as exc_info:
        ciwg.main()

    assert exc_info.value.code == expected_exit, f"Case {case_num}: expected exit {expected_exit}"

    # stderr 확인
    _, err = capsys.readouterr()

    if expected_block:
        assert ciwg.BLOCK_MARKER in err, (
            f"Case {case_num}: expected BLOCK marker in stderr, got: {err!r}"
        )
        assert ciwg.AUDIT_MARKER not in err, (
            f"Case {case_num}: AUDIT marker should not appear with BLOCK"
        )
    elif expected_audit:
        assert ciwg.AUDIT_MARKER in err, (
            f"Case {case_num}: expected AUDIT marker in stderr, got: {err!r}"
        )
        assert ciwg.BLOCK_MARKER not in err, (
            f"Case {case_num}: BLOCK marker should not appear with AUDIT (distinct sentinel)"
        )
    else:
        # silent (no marker expected)
        assert ciwg.BLOCK_MARKER not in err, (
            f"Case {case_num}: unexpected BLOCK marker in stderr: {err!r}"
        )
        assert ciwg.AUDIT_MARKER not in err, (
            f"Case {case_num}: unexpected AUDIT marker in stderr: {err!r}"
        )


# ============================================================ §8.3 load-bearing invariant


# ============================================================ §8.2 case 10: verifier_absent_failopen


def test_case_10_verifier_absent_failopen(tmp_path, monkeypatch, capsys):
    """Case 10: verifier SSOT 누락 → subprocess wrapper fail-open exit 0 (no BLOCK marker).

    subprocess wrapper(scripts/check-inline-write-gate.sh) 이 lib/check_inline_write_gate.py
    를 못 찾으면 fail-open(exit 0, stderr "WARNING") → no BLOCK marker.

    이 테스트는 subprocess 레벨에서만 의미가 있으므로 별도 테스트.
    """
    bash_exe = shutil.which("bash")
    if bash_exe is None:
        pytest.skip("bash not found in PATH")

    # Windows/WSL environment skip
    if sys.platform == "win32":
        pytest.skip("subprocess bash tests skipped on Windows (WSL path resolution)")

    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    repo_file = os.path.join(repo, "main.py")

    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": repo_file},
        "cwd": str(repo),
    }

    payload_json = json.dumps(payload)

    # temp dir 에 wrapper 만 복사, lib/ 없음 → SSOT 미발견 → fail-open
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        wrapper_src = (
            Path(__file__).parent.parent.parent / "scripts" / "check-inline-write-gate.sh"
        )
        if not wrapper_src.exists():
            pytest.skip("wrapper script not found")

        wrapper_copy = temp_dir / "check-inline-write-gate.sh"
        wrapper_copy.write_text(wrapper_src.read_text(encoding="utf-8"))
        wrapper_copy.chmod(0o755)

        env = os.environ.copy()
        env["HOME"] = str(home)

        result = subprocess.run(
            ["bash", str(wrapper_copy)],
            input=payload_json,
            capture_output=True,
            text=True,
            cwd=str(temp_dir),  # lib/ 경로 부재 환경
            env=env,
        )

        assert result.returncode == 0, "verifier absent → fail-open exit 0"
        assert ciwg.BLOCK_MARKER not in result.stderr, (
            "verifier absent → no BLOCK marker (fail-open graceful degradation, case 10)"
        )


# ============================================================ §8.3 load-bearing invariant


def test_invariant_worktree_before_memory_ordering(tmp_path, monkeypatch, capsys):
    """Load-bearing invariant: worktree path MUST check before memory.

    mutation test: if step2(worktree) and step4(memory) are swapped in _classify_path,
    this test MUST FAIL (RED) because worktree would be misclassified as memory → allow.
    """
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))

    # worktree 경로 = ~/.claude/worktrees/plugin-codeforge/br/f.py
    worktree_file = home / ".claude" / "worktrees" / "plugin-codeforge" / "br" / "f.py"

    repo = tmp_path / "repo"
    repo.mkdir()

    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(worktree_file)},
        "cwd": str(repo),
        # agent_id 부재 → Orchestrator block-candidate
    }

    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))

    # os.path.expanduser 모킹 — verifier 내부에서도 ~ 확장이 HOME을 사용하도록
    original_expanduser = os.path.expanduser

    def mock_expanduser(path):
        if path.startswith("~"):
            return path.replace("~", str(home), 1)
        return original_expanduser(path)

    monkeypatch.setattr("os.path.expanduser", mock_expanduser)

    with pytest.raises(SystemExit) as exc_info:
        ciwg.main()

    assert exc_info.value.code == 0
    _, err = capsys.readouterr()
    assert ciwg.BLOCK_MARKER in err, (
        "worktree path must be BLOCKED regardless of memory carve-out order. "
        "This test discriminates correct (worktree→memory) vs incorrect (memory→worktree) ordering."
    )


def test_invariant_agent_id_tri_state(tmp_path, monkeypatch, capsys):
    """agent_id tri-state: missing/null/"" all → orchestrator block-candidate.

    mutation test: if `if not agent_id` → `if "agent_id" not in payload`, cases with
    agent_id=None or "" would incorrectly pass (GREEN), but this test must differentiate.
    """
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    repo_file = os.path.join(repo, "src", "main.py")

    for agent_id_val, case_name in [
        (None, "null"),  # case 3
        ("", "empty_string"),  # case 4
    ]:
        payload_dict = {
            "tool_name": "Write",
            "tool_input": {"file_path": repo_file},
            "cwd": str(repo),
        }
        if agent_id_val is not None:
            payload_dict["agent_id"] = agent_id_val

        monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload_dict)))
        monkeypatch.setenv("HOME", str(home))

        with pytest.raises(SystemExit) as exc_info:
            ciwg.main()

        assert exc_info.value.code == 0, f"{case_name}: exit 0"
        _, err = capsys.readouterr()
        assert ciwg.BLOCK_MARKER in err, (
            f"{case_name}: agent_id={agent_id_val!r} must trigger BLOCK (Orchestrator block-candidate)"
        )


def test_invariant_never_exit_2_wave1(tmp_path, monkeypatch):
    """Wave1 never exit 2: all paths exit 0 (deny non-active yet).

    mutation test: if exit 0 changed to exit 2 for block-candidate, this fails (RED).
    """
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    worktree_file = home / ".claude" / "worktrees" / "plugin-codeforge" / "br" / "f.py"

    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(worktree_file)},
        "cwd": str(repo),
    }

    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    monkeypatch.setenv("HOME", str(home))

    with pytest.raises(SystemExit) as exc_info:
        ciwg.main()

    assert exc_info.value.code == 0, "Wave1: must ALWAYS exit 0, never exit 2"


# ============================================================ §8.3 design-confirm 3종


def test_design_confirm_multiedit_live_schema(tmp_path, monkeypatch, capsys):
    """design-confirm #1: MultiEdit payload form + live schema (file_path top-level).

    MultiEdit 의 tool_input = {"file_path":"...", "edits":[...]} 형상.
    file_path 가 top-level (edits[] 중첩 아님). 이 형상이 worktree 경로에서 BLOCK 됨 assert.
    """
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))

    repo = tmp_path / "repo"
    repo.mkdir()

    worktree_file = home / ".claude" / "worktrees" / "plugin-codeforge" / "br" / "test.py"

    # MultiEdit payload: file_path top-level + edits array
    payload = {
        "tool_name": "MultiEdit",
        "tool_input": {
            "file_path": str(worktree_file),
            "edits": [
                {"old_string": "foo", "new_string": "bar"},
                {"old_string": "baz", "new_string": "qux"},
            ],
        },
        "cwd": str(repo),
        # agent_id 부재 → Orchestrator
    }

    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))

    # os.path.expanduser 모킹
    original_expanduser = os.path.expanduser

    def mock_expanduser(path):
        if path.startswith("~"):
            return path.replace("~", str(home), 1)
        return original_expanduser(path)

    monkeypatch.setattr("os.path.expanduser", mock_expanduser)

    with pytest.raises(SystemExit) as exc_info:
        ciwg.main()

    assert exc_info.value.code == 0
    _, err = capsys.readouterr()
    assert ciwg.BLOCK_MARKER in err, (
        "MultiEdit with worktree file_path (top-level) must be BLOCKED"
    )


def test_design_confirm_distinct_sentinel_bypass_vs_block(tmp_path, monkeypatch, capsys):
    """design-confirm #2: distinct sentinel — AUDIT_MARKER ≠ BLOCK_MARKER.

    case 9 (bypass): AUDIT marker exist AND BLOCK marker absent → distinct verification.
    """
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    repo_file = os.path.join(repo, "main.py")

    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": repo_file},
        "cwd": str(repo),
    }

    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("BYPASS_INLINE_WRITE_GATE", "1")

    with pytest.raises(SystemExit) as exc_info:
        ciwg.main()

    assert exc_info.value.code == 0
    _, err = capsys.readouterr()

    # AUDIT 존재, BLOCK 부재 (distinct)
    assert ciwg.AUDIT_MARKER in err, "bypass must emit AUDIT marker"
    assert ciwg.BLOCK_MARKER not in err, "bypass must NOT emit BLOCK marker (distinct)"

    # 마커 문자열이 실제로 다른지 확인 (design-confirm #2)
    assert ciwg.AUDIT_MARKER != ciwg.BLOCK_MARKER, "markers must be distinct strings"


def test_design_confirm_relative_path_resolve(tmp_path, monkeypatch, capsys):
    """design-confirm #3: relative file_path resolves via cwd before classification.

    relative path + repo-inside cwd → resolve → BLOCK (design-confirm #3).
    """
    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "src").mkdir()

    # relative path
    rel_path = "src/main.py"

    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": rel_path},
        "cwd": str(repo),
        # agent_id 부재 → Orchestrator block-candidate
    }

    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    monkeypatch.setenv("HOME", str(home))

    with pytest.raises(SystemExit) as exc_info:
        ciwg.main()

    assert exc_info.value.code == 0
    _, err = capsys.readouterr()
    assert ciwg.BLOCK_MARKER in err, (
        "relative path within repo must resolve to absolute (cwd-based) and be BLOCKED"
    )


# ============================================================ §8.4 perf


def test_perf_main_under_50ms(tmp_path, monkeypatch):
    """perf: main() in-process < 50ms (fail-open scenarios + subagent short-circuit)."""
    home = tmp_path / "home"
    home.mkdir()

    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": "/some/path"},
        "agent_id": "a1b2c3",  # subagent → early exit
    }

    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    monkeypatch.setenv("HOME", str(home))

    start = time.perf_counter()
    with pytest.raises(SystemExit):
        ciwg.main()
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert elapsed_ms < 50, f"main() took {elapsed_ms:.1f}ms, expected < 50ms"


# ============================================================ subprocess integration (wrapper + verifier)


def test_subprocess_wrapper_block_case(tmp_path, monkeypatch):
    """subprocess: bash wrapper fork + block case distinct marker assert.

    exit code AND stderr BLOCK marker 동시 assert (distinct-marker 의무, §2247).
    """
    bash_exe = shutil.which("bash")
    if bash_exe is None:
        pytest.skip("bash not found in PATH")

    # Windows/WSL environment skip — bash path resolution issue
    if sys.platform == "win32":
        pytest.skip("subprocess bash tests skipped on Windows (WSL path resolution)")

    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    worktree_file = home / ".claude" / "worktrees" / "plugin-codeforge" / "br" / "f.py"

    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(worktree_file)},
        "cwd": str(repo),
    }

    payload_json = json.dumps(payload)

    wrapper_script = (
        Path(__file__).parent.parent.parent / "scripts" / "check-inline-write-gate.sh"
    )
    if not wrapper_script.exists():
        pytest.skip(f"wrapper script not found: {wrapper_script}")

    env = os.environ.copy()
    env["HOME"] = str(home)

    result = subprocess.run(
        ["bash", str(wrapper_script)],
        input=payload_json,
        capture_output=True,
        text=True,
        env=env,
    )

    # Wave1: exit 0 항상
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}"

    # distinct marker: BLOCK 존재 + AUDIT 부재
    assert ciwg.BLOCK_MARKER in result.stderr, (
        "wrapper fork must emit BLOCK marker in stderr (discriminating block case)"
    )
    assert ciwg.AUDIT_MARKER not in result.stderr, (
        "BLOCK case must not emit AUDIT marker"
    )


def test_subprocess_wrapper_bypass_case(tmp_path, monkeypatch):
    """subprocess: bash wrapper fork + bypass case distinct marker assert."""
    bash_exe = shutil.which("bash")
    if bash_exe is None:
        pytest.skip("bash not found in PATH")

    # Windows/WSL environment skip
    if sys.platform == "win32":
        pytest.skip("subprocess bash tests skipped on Windows (WSL path resolution)")

    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    repo_file = os.path.join(repo, "main.py")

    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": repo_file},
        "cwd": str(repo),
    }

    payload_json = json.dumps(payload)

    wrapper_script = (
        Path(__file__).parent.parent.parent / "scripts" / "check-inline-write-gate.sh"
    )
    if not wrapper_script.exists():
        pytest.skip(f"wrapper script not found: {wrapper_script}")

    env = os.environ.copy()
    env["HOME"] = str(home)
    env["BYPASS_INLINE_WRITE_GATE"] = "1"

    result = subprocess.run(
        ["bash", str(wrapper_script)],
        input=payload_json,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, f"expected exit 0, got {result.returncode}"

    # distinct marker: AUDIT 존재 + BLOCK 부재
    assert ciwg.AUDIT_MARKER in result.stderr, (
        "bypass case must emit AUDIT marker"
    )
    assert ciwg.BLOCK_MARKER not in result.stderr, (
        "AUDIT case must not emit BLOCK marker (distinct sentinel, §2247)"
    )


def test_subprocess_wrapper_verifier_absent_failopen(tmp_path, monkeypatch):
    """subprocess: verifier absent → wrapper fail-open exit 0 (no block marker).

    case 10: verifier SSOT 미발견 → wrapper 가 exit 0 (graceful degradation).
    distinct-marker obligation: BLOCK marker 부재 assert (§2247 입증).
    """
    bash_exe = shutil.which("bash")
    if bash_exe is None:
        pytest.skip("bash not found in PATH")

    # Windows/WSL environment skip
    if sys.platform == "win32":
        pytest.skip("subprocess bash tests skipped on Windows (WSL path resolution)")

    home = tmp_path / "home"
    home.mkdir()

    repo = tmp_path / "repo"
    repo.mkdir()

    repo_file = os.path.join(repo, "main.py")

    payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": repo_file},
        "cwd": str(repo),
    }

    payload_json = json.dumps(payload)

    # temp dir 에 wrapper 만 복사, lib/ 없음 → SSOT 미발견 → fail-open
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        wrapper_src = (
            Path(__file__).parent.parent.parent / "scripts" / "check-inline-write-gate.sh"
        )
        if not wrapper_src.exists():
            pytest.skip("wrapper script not found")

        wrapper_copy = temp_dir / "check-inline-write-gate.sh"
        wrapper_copy.write_text(wrapper_src.read_text(encoding="utf-8"))
        wrapper_copy.chmod(0o755)

        env = os.environ.copy()
        env["HOME"] = str(home)

        result = subprocess.run(
            ["bash", str(wrapper_copy)],
            input=payload_json,
            capture_output=True,
            text=True,
            cwd=str(temp_dir),  # lib/ 경로 부재 환경
            env=env,
        )

        assert result.returncode == 0, "verifier absent → fail-open exit 0"
        assert ciwg.BLOCK_MARKER not in result.stderr, (
            "verifier absent → no BLOCK marker (fail-open graceful degradation, case 10)"
        )


# ============================================================ Edge cases


def test_edge_case_non_target_tool(tmp_path, monkeypatch, capsys):
    """non-target tool (예: Bash, Agent, etc) → fail-open exit 0."""
    payload = {
        "tool_name": "Bash",
        "tool_input": {"command": "ls -la"},
    }

    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))

    with pytest.raises(SystemExit) as exc_info:
        ciwg.main()

    assert exc_info.value.code == 0
    _, err = capsys.readouterr()
    assert ciwg.BLOCK_MARKER not in err, "non-target tool → scope 외, fail-open"


def test_edge_case_edit_tool(tmp_path, monkeypatch, capsys):
    """Edit tool (target tool 3종 중 1) → block candidate path 판정."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))

    repo = tmp_path / "repo"
    repo.mkdir()

    worktree_file = home / ".claude" / "worktrees" / "plugin-codeforge" / "br" / "f.py"

    payload = {
        "tool_name": "Edit",  # target tool
        "tool_input": {"file_path": str(worktree_file), "old_string": "x", "new_string": "y"},
        "cwd": str(repo),
    }

    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))

    # os.path.expanduser 모킹
    original_expanduser = os.path.expanduser

    def mock_expanduser(path):
        if path.startswith("~"):
            return path.replace("~", str(home), 1)
        return original_expanduser(path)

    monkeypatch.setattr("os.path.expanduser", mock_expanduser)

    with pytest.raises(SystemExit) as exc_info:
        ciwg.main()

    assert exc_info.value.code == 0
    _, err = capsys.readouterr()
    assert ciwg.BLOCK_MARKER in err, "Edit on worktree must be BLOCKED"


def test_edge_case_tool_input_missing(tmp_path, monkeypatch, capsys):
    """tool_input 부재 → file_path None → scope 외, fail-open."""
    payload = {
        "tool_name": "Write",
        # tool_input 없음
    }

    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))

    with pytest.raises(SystemExit) as exc_info:
        ciwg.main()

    assert exc_info.value.code == 0
    _, err = capsys.readouterr()
    assert ciwg.BLOCK_MARKER not in err, "missing tool_input → fail-open"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
