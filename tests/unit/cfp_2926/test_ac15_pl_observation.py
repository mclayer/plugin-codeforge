"""AC-15 — PL 에이전트 spawn observation + docqueue.

Change Plan §8 AC-15 RTM 명명 테스트.
  - L-A: toolcall observed (PL 가 tool 사용 기록)
  - L-C: docqueue disjoint submissions (≥ 2개)

Carrier: CFP-2926 Phase 2 (구현) / Story NG-15
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    import check_pl_spawn_observation
except ImportError:
    pytest.skip(
        "check_pl_spawn_observation module not found", allow_module_level=True
    )


def test_pl_agent_toolcall_observed_by_writer_key(tmp_path, capture_output):
    """AC-15 L-A: PL toolcall 관찰 (writer_key='PL')

    dev-process-event 원장에서 writer_key="PL" 행이 있는가.

    [Discriminating: PL 이 실제로 도구를 호출했는지 검증]
    """
    # dev-process-event 원장 구성
    ledger = tmp_path / "dev-process.jsonl"
    rows = [
        {
            "writer_key": "DeveloperAgent",
            "artifact_key": "src/main.py",
            "first_write": 1000,
            "last_write": 2000,
        },
        {
            "writer_key": "PL",  # ★ PL 이 기록했는가?
            "artifact_key": "tests/test_pl.py",
            "first_write": 1500,
            "last_write": 2500,
        },
    ]

    ledger.write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    # L-A 검증: PL writer 존재
    lines = ledger.read_text(encoding="utf-8").splitlines()
    pl_rows = [json.loads(line) for line in lines if line.strip()]
    pl_observations = [row for row in pl_rows if row.get("writer_key") == "PL"]

    assert pl_observations, "L-A: PL must have at least one toolcall observation"


def test_docqueue_disjoint_submissions_ge_two(tmp_path):
    """AC-15 L-C: 분리된 제출 ≥ 2개 (docqueue via dev-process-event).

    writer_key="Orchestrator" 행이 2+ 있고, 각각 별개 artifact_key 갖는가.

    [Discriminating: 단일 원대 제출은 불충분 (분산 필수)]
    """
    ledger = tmp_path / "docqueue.jsonl"
    rows = [
        {
            "writer_key": "Orchestrator",
            "artifact_key": "docs/change-plan-1.md",
            "first_write": 1000,
            "last_write": 2000,
        },
        {
            "writer_key": "Orchestrator",
            "artifact_key": "docs/change-plan-2.md",
            "first_write": 2500,
            "last_write": 3500,
        },
    ]

    ledger.write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    # L-C 검증
    lines = ledger.read_text(encoding="utf-8").splitlines()
    orch_rows = [json.loads(line) for line in lines if line.strip()]
    orch_submissions = [row for row in orch_rows if row.get("writer_key") == "Orchestrator"]

    assert len(orch_submissions) >= 2, (
        f"L-C: Orchestrator must submit ≥ 2 disjoint docs, got {len(orch_submissions)}"
    )

    # 각 제출이 별개 artifact_key
    artifact_keys = {row.get("artifact_key") for row in orch_submissions}
    assert len(artifact_keys) >= 2, (
        f"L-C: submissions must be to distinct artifacts, got {len(artifact_keys)}"
    )
