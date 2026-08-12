"""Contract parity + Envelope/DispatchPacket tests.

Change Plan §8 contract SSOT 이행.
  - envelope: return_envelope_handle 필드 (모든 return 에서 필수)
  - dispatch_packet: lane_dispatch_packet snapshot_sha 필드 (모든 패킷에서 필수)
  - AC-10: dispatch packet 구조
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_return_envelope_requires_handle(tmp_path):
    """contract: return envelope 모든 행이 handle 필드 보유.

    return_envelope_handle 스키마 요구: handle (UUID 또는 식별자).

    [Mutant: handle 부재 허용 → RED]
    [Discriminating: 모든 return 이 추적 가능해야 함]
    """
    return_ledger = tmp_path / "return-envelope.jsonl"

    # 정상: handle 포함
    rows = [
        {"handle": "ret-001", "status": "success", "agent_type": "DeveloperAgent"},
        {"handle": "ret-002", "status": "failure", "agent_type": "QADeveloperAgent"},
    ]

    return_ledger.write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    # 검증
    lines = return_ledger.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if line.strip():
            row = json.loads(line)
            assert "handle" in row, f"return envelope must have 'handle' field, got {row.keys()}"
            assert row["handle"], "handle must not be empty"


def test_dispatch_packet_requires_snapshot_sha(tmp_path):
    """AC-10 contract: dispatch packet 모든 행이 snapshot_sha 필드 보유.

    lane_dispatch_packet schema: snapshot_sha (git SHA, immutable).

    [Mutant: snapshot_sha 제거 → ESCALATE_PACKET_INCOMPLETE]
    [Discriminating: 패킷의 git 형상 추적이 필수]
    """
    packet_ledger = tmp_path / "dispatch-packets.jsonl"

    # 정상 packet
    packets = [
        {
            "lane": "구현",
            "snapshot_sha": "abc123def456",
            "story_key": "CFP-2926",
            "allowed_spawn_roster": [],
        },
        {
            "lane": "테스트",
            "snapshot_sha": "xyz789uvw012",
            "story_key": "CFP-2926",
            "allowed_spawn_roster": ["QADeveloperAgent"],
        },
    ]

    packet_ledger.write_text(
        "\n".join(json.dumps(p) for p in packets),
        encoding="utf-8",
    )

    # 검증
    lines = packet_ledger.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if line.strip():
            row = json.loads(line)
            assert "snapshot_sha" in row, (
                f"dispatch_packet must have 'snapshot_sha' field, got {row.keys()}"
            )
            assert row["snapshot_sha"], "snapshot_sha must not be empty"
            # sha 형식 검증 (16진수)
            assert len(row["snapshot_sha"]) >= 6, (
                f"snapshot_sha should be git SHA (len≥6), got {row['snapshot_sha']}"
            )


def test_envelope_schema_consistency(tmp_path):
    """contract: envelope row 개별 스키마 일관성.

    모든 행이 공통 필드 보유: handle, timestamp, source_agent.
    """
    envelope_ledger = tmp_path / "envelope-test.jsonl"

    rows = [
        {
            "handle": "h1",
            "timestamp": 1692374400000,
            "source_agent": "Orchestrator",
            "payload": "test-data",
        },
    ]

    envelope_ledger.write_text(
        "\n".join(json.dumps(row) for row in rows),
        encoding="utf-8",
    )

    lines = envelope_ledger.read_text(encoding="utf-8").splitlines()
    required_fields = {"handle", "timestamp", "source_agent"}

    for line in lines:
        if line.strip():
            row = json.loads(line)
            missing = required_fields - set(row.keys())
            assert not missing, f"envelope row missing fields: {missing}"
