"""F-CR-002 (구현리뷰 FIX Iter2) — 공유 channel record type 격리 회귀 테스트.

`spawn-event.jsonl` 은 **공유 channel** 이다 (contract §2.1): `spawn-event-v1` 23-field row 와
`self-context-v1` 6-field row 가 `schema_version` discriminator 로 같은 파일에 공존한다.
`aggregate_spawn_event.load_rows` 가 이 discriminator 를 무시하면 —
  - AC-9 pivot 에 `(None, None)` 그룹 유입 + 실패율 denominator 오염,
  - AC-10 낭비집계의 row_count 팽창
이 발생한다. 본 파일은 오염 row 를 실제로 섞은 뒤 **spawn-event-v1 만** 집계됨을 gate 한다.

production 로직 재구현 금지 — 오염 row 는 실 `append_self_context_event.py` CLI 가 쓰고
(동일 채널 공유 실형상), 집계는 실 `aggregate_spawn_event` 모듈이 수행한다.

[RED-until-landed: aggregate_spawn_event.load_rows schema_version 필터]
  필터 부재 시 self-context row 가 그대로 집계에 유입 → len(rows)/row_count/failure_rate 불일치 RED.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import aggregate_spawn_event  # 실 production aggregate 모듈 (read-only)

REPO_ROOT = Path(__file__).resolve().parents[3]
SELF_CONTEXT_SCRIPT = REPO_ROOT / "scripts" / "lib" / "append_self_context_event.py"


def _append_self_context_rows(ledger, count):
    """실 append_self_context_event.py CLI 로 self-context-v1 오염 row 를 동일 ledger 에 append.

    합성 JSON 박제가 아니라 **production writer** 가 쓰는 실 형상 (공유 channel 실재 증명).
    Returns 마지막 CompletedProcess.
    """
    proc = None
    for i in range(count):
        proc = subprocess.run(
            [
                sys.executable, str(SELF_CONTEXT_SCRIPT),
                "--session-id", f"sess-selfctx-{i}",
                "--turn-index", str(i),
                "--cause-category", "spawn-dispatch",
                "--delegation-ratio", "0.5",
                "--pre-tokens", "120000",
                "--ledger-path", str(ledger),
                "--telemetry-enabled", "--spawn-event-enabled",
            ],
            capture_output=True, text=True, encoding="utf-8", cwd=str(REPO_ROOT),
        )
        assert proc.returncode == 0, f"self-context append exit {proc.returncode}: {proc.stderr}"
    return proc


def _write_spawn_rows(ledger, run_append):
    """AC-9/AC-10 대상 spawn-event-v1 row 2건 (failure 1 + success 1, 동일 역할·모델)."""
    specs = [
        ("failure", 100000, "s-iso-1", "a-iso-1"),
        ("success", 900000, "s-iso-2", "a-iso-2"),
    ]
    for outcome, tokens, sess, aid in specs:
        res = run_append(
            ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
            session_id=sess, agent_id=aid, spawn_seq="1",
            attribution_confidence="attributed", model="claude-opus-4",
            outcome=outcome, total_tokens=tokens,
        )
        assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"


def test_aggregate_excludes_self_context_rows_from_pivot_and_rates(tmp_path, run_append, read_rows):
    """(disc) self-context-v1 오염 row 3건을 섞어도 pivot/실패율/낭비집계는 spawn-event-v1 만.

    물리 5행(spawn 2 + self-context 3) → 집계 대상 2행.
    필터 부재 시: rows 5 → pivot 에 (None, None) 그룹 + (Dev,opus) 실패율 denominator 는 그대로나
      row_count 5 / 그룹 3 → 본 assertion 전부 RED (discriminating).
    """
    ledger = tmp_path / "spawn-event.jsonl"
    _write_spawn_rows(ledger, run_append)
    _append_self_context_rows(ledger, 3)

    # 전제(fixture 실재): 물리 5행 + self-context row 가 실제로 섞여 있음
    physical = read_rows(ledger)
    assert len(physical) == 5, f"물리 5행(spawn 2 + self-context 3) 기대, got {len(physical)}"
    assert sum(1 for r in physical if r.get("schema_version") == "self-context-v1") == 3, (
        "오염 fixture 가 실제로 self-context-v1 row 를 남겨야 함(vacuous 방지)"
    )

    # 측정 assertion (a): 집계 로드는 spawn-event-v1 만 (story_key filter 미사용 — 필터 축 분리)
    rows = aggregate_spawn_event.load_rows(str(ledger))
    assert len(rows) == 2, (
        f"aggregate 는 spawn-event-v1 2행만 집계해야 함(self-context 오염 배제), got {len(rows)}"
    )
    assert all(r.get("schema_version") == "spawn-event-v1" for r in rows), (
        f"집계 대상에 타 record type 유입: {[r.get('schema_version') for r in rows]}"
    )

    # (b): pivot 에 오염 그룹 (None, None) 부재
    pivot = aggregate_spawn_event.pivot_role_model_outcome(rows)
    assert (None, None) not in pivot, (
        f"self-context row 가 (None, None) 그룹으로 pivot 오염, keys={list(pivot.keys())}"
    )
    assert set(pivot.keys()) == {("DeveloperAgent", "claude-opus-4")}, (
        f"group key 는 spawn row 파생 1개여야 함, got {list(pivot.keys())}"
    )

    # (c): 실패율 denominator 무오염 — 비성공 1 / total 2 = 0.5
    fr = aggregate_spawn_event.failure_rates(rows)[("DeveloperAgent", "claude-opus-4")]
    assert fr["total"] == 2 and fr["failure"] == 1, f"denominator/numerator 오염, got {fr}"
    assert fr["failure_rate"] == pytest.approx(0.5), (
        f"실패율 = 1/2 (오염 row 가 denominator 에 산입되면 1/5 등으로 붕괴), got {fr['failure_rate']}"
    )

    # (d): 낭비집계 + row_count 무오염
    agg = aggregate_spawn_event.aggregate(rows)
    assert agg["row_count"] == 2, f"row_count 는 spawn row 2 여야 함, got {agg['row_count']}"
    assert agg["wasted_tokens_total"] == 100000, (
        f"낭비토큰 = 비성공 실측 100000 (success 900000·self-context 제외), "
        f"got {agg['wasted_tokens_total']}"
    )
    assert len(agg["groups"]) == 1, f"group 은 1개여야 함, got {agg['groups']}"


def test_aggregate_excludes_unknown_future_record_type(tmp_path, run_append, read_rows):
    """(disc) 미지의 future record type 이 spawn row 와 **동일 field 형상**이어도 배제.

    self-context 배제는 "field 가 없어서" 우연히 통과할 수 있다(field-presence 휴리스틱).
    본 test 는 agent_type/model/outcome/total_tokens 를 **전부 갖춘** 타 record type 을 섞어
    배제 근거가 `schema_version` allow-list 임을 falsifiable 하게 pin 한다.
    필터가 없거나 blocklist(self-context 만 제외) 방식이면 RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    _write_spawn_rows(ledger, run_append)

    # 오염: 미래 record type (spawn row 와 같은 field 를 가진 위장 형상)
    intruder = {
        "schema_version": "future-record-v9",
        "event_id": "f" * 64,
        "story_key": "CFP-2850",
        "agent_type": "DeveloperAgent",
        "model": "claude-opus-4",
        "outcome": "failure",
        "total_tokens": 777777,
    }
    with open(ledger, "a", encoding="utf-8") as f:
        f.write(json.dumps(intruder, ensure_ascii=False) + "\n")

    assert len(read_rows(ledger)) == 3, "물리 3행(spawn 2 + intruder 1) 기대"

    rows = aggregate_spawn_event.load_rows(str(ledger))
    # 측정 assertion (a): allow-list 방식 → 미지 record type 배제
    assert len(rows) == 2, (
        f"schema_version allow-list(spawn-event-v1) 로 미지 record type 배제해야 함, got {len(rows)}"
    )
    assert all(r.get("event_id") != "f" * 64 for r in rows), "intruder row 가 집계에 유입됨"
    # (b): 낭비집계 오염 0 (intruder 의 777777 미산입)
    assert aggregate_spawn_event.wasted_tokens(rows) == 100000, (
        f"intruder total_tokens 777777 이 낭비집계에 산입되면 안 됨, "
        f"got {aggregate_spawn_event.wasted_tokens(rows)}"
    )
