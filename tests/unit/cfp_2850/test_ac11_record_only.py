"""AC-11 — record-only non-blocking fail-VISIBLE.

Change Plan §8.1.1 RTM AC-11 (3 named test). phase1.
  - append 예외 시 실행 차단 금지 (exit 0).
  - drop 은 stderr VISIBLE (silent-success 금지).
  - outcome 분류도 record-only (gate/block/deny 세우지 않음).

exit0/stderr = 현행 graceful degradation → GREEN.
outcome record-only = [RED-until-landed: --outcome flag].
"""

from __future__ import annotations


def _force_append_exception(tmp_path, run_append):
    """ledger-path 를 디렉터리로 만들어 append open 실패를 강제 (graceful 경로 유발)."""
    isdir = tmp_path / "ledger-is-a-dir"
    isdir.mkdir(parents=True, exist_ok=True)  # 파일이어야 할 경로가 디렉터리 → open 실패
    return run_append(
        isdir, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-ac11-exc", agent_id="agent-ac11-exc", spawn_seq="1",
    )


def test_ac11_exit0_on_append_exception(tmp_path, run_append):
    """append 예외 발생 → exit 0 (실행 흐름 비차단, ADR-115 §결정5).

    mutation: 예외 시 non-zero exit(block) 하면 RED.
    """
    res = _force_append_exception(tmp_path, run_append)
    # 측정 assertion: 예외에도 exit 0 (비차단)
    assert res.returncode == 0, f"append 예외 시에도 exit 0 이어야 함, got {res.returncode}: {res.stderr}"


def test_ac11_drop_stderr_visible(tmp_path, run_append):
    """drop 은 stderr VISIBLE (silent-success 금지) — WARN trace surface.

    mutation: 예외를 silent 삼키면(stderr 빈) RED.
    """
    res = _force_append_exception(tmp_path, run_append)
    # 측정 assertion: drop 이 stderr 로 가시화 (silent 아님)
    assert res.returncode == 0
    assert "WARN" in res.stderr or "append failed" in res.stderr, (
        f"drop 이 stderr 로 VISIBLE 해야 함 (silent-success 금지), stderr={res.stderr!r}"
    )


def test_ac11_outcome_record_only_no_gate(tmp_path, run_append, read_rows):
    """outcome 분류는 record-only — outcome=failure 여도 gate/block/deny 없음 (exit 0).

    [RED-until-landed: --outcome flag]
    mutation: outcome=failure 를 gate 로 삼아 non-zero exit/block 하면 RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-ac11-rec", agent_id="agent-ac11-rec", spawn_seq="1",
        outcome="failure", termination_cause="error",
    )
    # 측정 assertion: 비성공 outcome 도 record-only (exit 0, gate 없음)
    assert res.returncode == 0, (
        f"outcome=failure 는 record-only 여야 함(gate 금지, exit 0), got {res.returncode}: {res.stderr}"
    )
    row = read_rows(ledger)[0]
    assert row["outcome"] == "failure", "failure 는 기록만 (차단 아님)"
