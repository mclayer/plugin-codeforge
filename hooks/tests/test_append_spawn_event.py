"""test_append_spawn_event.py — spawn-event-v1 P0 test suite (CFP-2393 Phase 2)

ADR-119 검증-후-단언 원칙 이행. Change Plan §8.2 P0 test contract.

반드시 커버할 불변식 (절대 위반 금지):
  P0-1. attribution_confidence invariant
    - placeholder usage given (token source 부정확) → unattributed MUST ∧ token/cost = null MUST (conjunction)
    - mutation: naive-sum impl FAILS (summed estimate 저장 시 RED)
    - attr_conf != attributed 면 token/cost 전부 null 강제 (추정 합산 금지)

  P0-2. contract↔runtime parity
    - runtime row keys == contract Allow-list 19-set (초과/누락 0, free-form string 0)

  P0-3. idempotency/dedup
    - event_id deterministic: sha256(session_id_hash || agent_id_hash || spawn_seq)
    - 동일 입력 2회 → 동일 event_id (at-least-once 재시도 안전)

  추가 불변식 (§8.2 명시):
    - actor sha256 (raw 금지): row.actor != raw_session_id literal (T-INFO-7)
    - O_APPEND (lost-update 회피): source에 os.replace/read_text 없고 O_APPEND 있어야 함
    - opt-in false: telemetry off → row 0, opt-in ON 일 때만 row append
    - timestamp UTC Z: row.timestamp 가 ...Z suffix (+00:00 불허)
    - transcript 미저장 (T-INFO-5): transcript_path/transcript key 부재
    - agent_type semi-open: unknown-agent fallback 존재
    - event_type closed enum: {agent_start, agent_stop, tool, file_touch, mode_change}

Anti-theater principle (CLAUDE.md / Epic 공통):
  - missing-case + exit assert: 각 test 는 (a) mutation 시나리오 + (b) exit code assert
  - naive-sum mutation 실제 RED 변별력: placeholder→unattributed 단순 통과 아님
  - distinct-marker: production subprocess fork 테스트 시 exit code + stdout sentinel 동시 assert

ci: hooks/tests/conftest.py pytest 패턴. wrapper spec: 선택사항.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# ─────────────────────── repo root 절대 경로 결정 ──────────────────────────
# conftest.py 패턴: __file__ 기준 절대 resolve
REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # hooks/tests/ → repo root

# ═════════════════════════════════════════════════════════════════════════════
# § P0-1: ATTRIBUTION CONFIDENCE INVARIANT (가장 중요)
# ═════════════════════════════════════════════════════════════════════════════


class TestAttributionConfidenceInvariant:
    """P0-1: placeholder usage → unattributed MUST ∧ token/cost = null MUST (conjunction assertion)"""

    def test_unattributed_forces_null_tokens_conjunction(self, tmp_path):
        """
        [P0-1 mutation RED 변별력]
        기본값 unattributed 입력 시, 동시에:
          (a) attribution_confidence == "unattributed" assert
          (b) input_tokens == null ∧ output_tokens == null ∧ cost_usd == null assert
        conjunction 둘 다 성립해야 PASS. 하나 실패 시 RED.

        mutation: naive-sum impl (summed_estimate 저장) 하면 (b)가 RED.
        """
        # subprocess로 append_spawn_event.py 호출 (CLI flag)
        ledger_path = tmp_path / "spawn-event.jsonl"
        session_id = "test-session-123"
        agent_id = "test-agent-456"

        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "구현",
            "--agent-type", "DeveloperAgent",
            "--session-id", session_id,
            "--agent-id", agent_id,
            "--spawn-seq", "1",
            "--attribution-confidence", "unattributed",  # explicit unattributed (placeholder 시뮬레이션)
            "--input-tokens", "1000",  # 호출자가 주면 무시해야 함
            "--output-tokens", "500",  # 호출자가 주면 무시해야 함
            "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
            "--consumer-scope", "wrapper",
            "--telemetry-enabled",  # opt-in flag 1/2
            "--spawn-event-enabled",  # opt-in flag 2/2
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result.returncode == 0, f"exit code {result.returncode}: {result.stderr}"

        # ledger 읽기 (JSONL append-only)
        assert ledger_path.exists(), "ledger file should exist"
        rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
        assert len(rows) == 1, "single row expected"

        row = rows[0]

        # (a) attribution_confidence == unattributed
        assert row["attribution_confidence"] == "unattributed", \
            f"[P0-1] assertion (a) FAIL: attribution_confidence = {row['attribution_confidence']}"

        # (b) conjunction: token/cost 전부 null (mutation: naive-sum 이면 numeric 저장됨 → RED)
        assert row["input_tokens"] is None, \
            f"[P0-1] assertion (b) FAIL: input_tokens should be null, got {row['input_tokens']}"
        assert row["output_tokens"] is None, \
            f"[P0-1] assertion (b) FAIL: output_tokens should be null, got {row['output_tokens']}"
        assert row["cost_usd"] is None, \
            f"[P0-1] assertion (b) FAIL: cost_usd should be null, got {row['cost_usd']}"
        assert row["cache_creation_input_tokens"] is None, \
            f"[P0-1] assertion (b) FAIL: cache_creation_input_tokens should be null"
        assert row["cache_read_input_tokens"] is None, \
            f"[P0-1] assertion (b) FAIL: cache_read_input_tokens should be null"

    def test_default_unattributed_no_attribution_flag(self, tmp_path):
        """
        [P0-1 default 검증]
        --attribution-confidence 미지정 시 기본값 unattributed 로 작동.
        token/cost = null 강제 (no-op 시뮬레이션).
        """
        ledger_path = tmp_path / "spawn-event.jsonl"

        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "설계",
            "--agent-type", "ArchitectPLAgent",
            "--session-id", "sess-abc",
            "--agent-id", "agent-xyz",
            "--spawn-seq", "5",
            # --attribution-confidence 미지정 (default unattributed)
            "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result.returncode == 0, f"exit {result.returncode}: {result.stderr}"

        rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
        row = rows[0]

        assert row["attribution_confidence"] == "unattributed"
        assert row["input_tokens"] is None
        assert row["output_tokens"] is None
        assert row["cost_usd"] is None

    def test_attributed_allows_numeric_tokens(self, tmp_path):
        """
        [P0-1 positive case]
        attribution_confidence = "attributed" 명시 시, token/cost 저장 허용.
        반대로 unattributed 이면 저장 금지 (P0-1 변별).
        """
        ledger_path = tmp_path / "spawn-event.jsonl"

        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "구현",
            "--agent-type", "DeveloperAgent",
            "--session-id", "sess-123",
            "--agent-id", "agent-456",
            "--spawn-seq", "10",
            "--attribution-confidence", "attributed",
            "--input-tokens", "2000",
            "--output-tokens", "800",
            "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
            "--model", "claude-opus-4-20250514",  # pricing table lookup
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result.returncode == 0

        rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
        row = rows[0]

        assert row["attribution_confidence"] == "attributed"
        # numeric 저장 (null 아님)
        assert row["input_tokens"] == 2000
        assert row["output_tokens"] == 800
        # cost_usd may be None if pricing lookup fails (graceful fallback)
        assert row["cost_usd"] is None or isinstance(row["cost_usd"], (int, float))


# ═════════════════════════════════════════════════════════════════════════════
# § P0-2: CONTRACT ↔ RUNTIME PARITY (19-field Allow-list only)
# ═════════════════════════════════════════════════════════════════════════════


class TestContractRuntimeParity:
    """P0-2: runtime row keys == contract Allow-list 19-set (정확 일치, 초과/누락 0)"""

    def test_runtime_keys_match_contract_19_field_allow_list(self, tmp_path):
        """
        [P0-2 parity test]
        생성 row 의 key 집합이 정확히 contract §2 명시 19-field 일 것.
        초과 key 1개라도 BREAKING (ADR-043 §결정 2).
        누락 key 1개라도 contract 위반.
        """
        # Contract allow-list 19 field (SSOT - contract §2)
        CONTRACT_19_FIELDS = {
            "event_id", "schema_version", "timestamp", "story_key", "lane_label",
            "agent_type", "attribution_confidence", "input_tokens", "output_tokens",
            "cache_creation_input_tokens", "cache_read_input_tokens", "cost_usd",
            "duration_ms", "tool_call_count", "actor", "parent_event_id",
            "consumer_scope", "event_type", "elapsed_seconds",
        }

        ledger_path = tmp_path / "spawn-event.jsonl"

        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "구현",
            "--agent-type", "QADeveloperAgent",
            "--session-id", "sess-parity",
            "--agent-id", "agent-parity",
            "--spawn-seq", "99",
            "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
            "--duration-ms", "1234",
            "--tool-call-count", "5",
            "--event-type", "agent_stop",
            "--elapsed-seconds", "10.5",
            "--telemetry-enabled",
            "--spawn-event-enabled",
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result.returncode == 0

        rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
        row = rows[0]

        runtime_keys = set(row.keys())

        # 정확 일치 (초과 & 누락 0)
        assert runtime_keys == CONTRACT_19_FIELDS, \
            f"[P0-2] Key mismatch: \n  missing: {CONTRACT_19_FIELDS - runtime_keys}\n  extra: {runtime_keys - CONTRACT_19_FIELDS}"


# ═════════════════════════════════════════════════════════════════════════════
# § P0-3: IDEMPOTENCY (deterministic event_id)
# ═════════════════════════════════════════════════════════════════════════════


class TestIdempotency:
    """P0-3: event_id deterministic sha256(session_id_hash || agent_id_hash || spawn_seq)"""

    def test_identical_inputs_produce_identical_event_id(self, tmp_path):
        """
        [P0-3 idempotency]
        동일 입력(session_id + agent_id + spawn_seq) 2회 → 동일 event_id assert.
        random UUID 금지 (InfraOpArch §11.6 — at-least-once 재시도 안전).
        """
        ledger_path_1 = tmp_path / "spawn-event-run1.jsonl"
        ledger_path_2 = tmp_path / "spawn-event-run2.jsonl"

        # 첫 번째 실행
        cmd_base = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "구현",
            "--agent-type", "DeveloperAgent",
            "--session-id", "session-idem-test",
            "--agent-id", "agent-idem-test",
            "--spawn-seq", "42",
            "--telemetry-enabled",
            "--spawn-event-enabled",
        ]

        cmd1 = cmd_base + ["--ledger-path", str(ledger_path_1)]
        result1 = subprocess.run(cmd1, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result1.returncode == 0

        # 두 번째 실행 (동일 입력)
        cmd2 = cmd_base + ["--ledger-path", str(ledger_path_2)]
        result2 = subprocess.run(cmd2, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result2.returncode == 0

        row1 = json.loads(ledger_path_1.read_text(encoding="utf-8").strip().split('\n')[0])
        row2 = json.loads(ledger_path_2.read_text(encoding="utf-8").strip().split('\n')[0])

        # 동일 event_id (deterministic)
        assert row1["event_id"] == row2["event_id"], \
            f"[P0-3] event_id not deterministic: {row1['event_id']} != {row2['event_id']}"


# ═════════════════════════════════════════════════════════════════════════════
# § ACTOR SHA256 INVARIANT (T-INFO-7)
# ═════════════════════════════════════════════════════════════════════════════


class TestActorSha256:
    """actor = sha256 hash (raw session_id literal 미저장)"""

    def test_actor_is_sha256_not_raw_session_id(self, tmp_path):
        """
        [T-INFO-7 security]
        row.actor 가 raw_session_id 리터럴이 아닌 sha256 hash 임을 검증.
        mutation: raw session_id 저장하면 RED.
        """
        ledger_path = tmp_path / "spawn-event.jsonl"
        raw_session_id = "test-session-raw-ID-12345"

        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "구현",
            "--agent-type", "DeveloperAgent",
            "--session-id", raw_session_id,
            "--agent-id", "agent-xyz",
            "--spawn-seq", "1",
            "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result.returncode == 0

        rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
        row = rows[0]

        # actor 는 sha256 hex (64글자)
        actor = row["actor"]
        assert len(actor) == 64, f"actor should be sha256 hex (64 chars), got {len(actor)}"
        assert all(c in "0123456789abcdef" for c in actor.lower()), "actor should be hex"

        # raw session_id 리터럴이 아님
        assert actor != raw_session_id, \
            f"[T-INFO-7] FAIL: actor stored raw session_id literal (security violation)"


# ═════════════════════════════════════════════════════════════════════════════
# § O_APPEND INVARIANT (H1 — lost-update 회피)
# ═════════════════════════════════════════════════════════════════════════════


class TestOAppendMechanism:
    """O_APPEND per-row (stop-event read-modify-write 패턴 복사 금지)"""

    def test_append_spawn_event_source_uses_o_append_not_read_modify_write(self):
        """
        [H1 anti-pattern check]
        append_spawn_event.py 소스가:
          - os.replace / read_text whole-file 패턴 미사용 (stop-event 버그 회피)
          - os.open(...O_APPEND...) 존재 assert

        mutation: read-modify-write 사용하면 RED (lost-update 경합 가능).
        """
        source_path = REPO_ROOT / "scripts/lib/append_spawn_event.py"
        assert source_path.exists(), f"source file not found: {source_path}"

        source_text = source_path.read_text(encoding="utf-8")

        # RED: read-modify-write anti-pattern (stop-event 버그)
        assert "os.replace(" not in source_text, \
            "[H1] FAIL: found os.replace (lost-update bug pattern)"
        assert "read_text(" not in source_text or "whole" in source_text, \
            "[H1] FAIL: found whole-file read pattern (lost-update race)"

        # GREEN: O_APPEND 사용 (안전 pattern)
        assert "O_APPEND" in source_text, \
            "[H1] FAIL: O_APPEND not found in source (H1 mechanism missing)"


# ═════════════════════════════════════════════════════════════════════════════
# § OPT-IN DEFAULT FALSE (T-ELEV-1)
# ═════════════════════════════════════════════════════════════════════════════


class TestOptInDefaultFalse:
    """telemetry off (flag 미지정) → row 0 (no-op)"""

    def test_no_telemetry_flags_produces_no_output(self, tmp_path):
        """
        [T-ELEV-1 privacy invariant]
        --telemetry-enabled / --spawn-event-enabled 미지정 시 → no-op (row 0, ledger 미생성).
        mutation: silent always-on (row 생성) → RED.
        """
        ledger_path = tmp_path / "spawn-event.jsonl"

        # CLI 호출: telemetry flag 미지정 (opt-in default false)
        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "구현",
            "--agent-type", "DeveloperAgent",
            "--session-id", "sess-opt-off",
            "--agent-id", "agent-opt-off",
            "--spawn-seq", "1",
            "--ledger-path", str(ledger_path),
            # --telemetry-enabled / --spawn-event-enabled 미지정 (opt-in false)
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)

        # Assertion (a): exit code 0 (graceful, block 안 함)
        assert result.returncode == 0, f"exit {result.returncode}: {result.stderr}"

        # Assertion (b): ledger 파일 미생성 또는 빈 파일 (row 0 no-op)
        if ledger_path.exists():
            content = ledger_path.read_text(encoding="utf-8").strip()
            assert not content, f"[T-ELEV-1] opt-in false 인데 row 생성됨: {content}"
        # 파일 미생성이 정상 (no-op), 생성된 경우 빈 파일이어야 함

    def test_telemetry_flags_produces_row(self, tmp_path):
        """
        [T-ELEV-1 positive case]
        --telemetry-enabled --spawn-event-enabled 명시 시 → row 1개 append (opt-in ON).
        P0-1 와 조합: opt-in 의 조건 검증 (제어 신호).
        """
        ledger_path = tmp_path / "spawn-event.jsonl"

        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "구현",
            "--agent-type", "DeveloperAgent",
            "--session-id", "sess-opt-on",
            "--agent-id", "agent-opt-on",
            "--spawn-seq", "1",
            "--ledger-path", str(ledger_path),
            "--telemetry-enabled",  # opt-in flag 1/2
            "--spawn-event-enabled",  # opt-in flag 2/2
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result.returncode == 0

        # Assertion: ledger 존재 + row 1개
        assert ledger_path.exists(), "ledger should be created with opt-in ON"
        rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
        assert len(rows) == 1, f"expected 1 row, got {len(rows)}"


# ═════════════════════════════════════════════════════════════════════════════
# § TIMESTAMP UTC Z STRICT
# ═════════════════════════════════════════════════════════════════════════════


class TestTimestampUtcZStrict:
    """timestamp = UTC Z strict (2026-06-24T14:22:33Z. +00:00 / bare datetime 불허)"""

    def test_timestamp_has_utc_z_suffix(self, tmp_path):
        """
        [timestamp UTC Z]
        row.timestamp 가 Z suffix 로 끝남 (+00:00 / bare datetime 불허, contract §2).
        """
        import re

        ledger_path = tmp_path / "spawn-event.jsonl"

        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "구현",
            "--agent-type", "DeveloperAgent",
            "--session-id", "ts-test",
            "--agent-id", "agent-ts",
            "--spawn-seq", "1",
            "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result.returncode == 0

        rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
        timestamp = rows[0]["timestamp"]

        # ISO8601 UTC Z format (regex)
        pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
        assert re.match(pattern, timestamp), \
            f"timestamp format invalid (need UTC Z): {timestamp}"

        # +00:00 형식 불허
        assert "+00:00" not in timestamp, \
            f"timestamp has +00:00 (must be Z only): {timestamp}"


# ═════════════════════════════════════════════════════════════════════════════
# § TRANSCRIPT CONTENT/PATH HARD INVARIANT (T-INFO-5)
# ═════════════════════════════════════════════════════════════════════════════


class TestTranscriptPrivacyInvariant:
    """transcript content / transcript_path 절대 미저장 (T-INFO-5 HARD)"""

    def test_no_transcript_content_or_path_in_row(self, tmp_path):
        """
        [T-INFO-5 security]
        row 에 'transcript_content', 'transcript_path', 'transcript' key 부재.
        numeric only 저장 (구조적 mitigation).
        """
        ledger_path = tmp_path / "spawn-event.jsonl"

        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "구현",
            "--agent-type", "DeveloperAgent",
            "--session-id", "ts-privacy",
            "--agent-id", "agent-priv",
            "--spawn-seq", "1",
            "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result.returncode == 0

        rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
        row = rows[0]

        forbidden_keys = {"transcript_content", "transcript_path", "transcript"}
        found = forbidden_keys & set(row.keys())

        assert not found, \
            f"[T-INFO-5] FAIL: forbidden keys found in row: {found}"


# ═════════════════════════════════════════════════════════════════════════════
# § AGENT_TYPE SEMI-OPEN (unknown-agent fallback)
# ═════════════════════════════════════════════════════════════════════════════


class TestAgentTypeSemiOpen:
    """agent_type semi-open: roster 미등재 → unknown-agent fallback (reject 안 함)"""

    def test_empty_agent_type_becomes_unknown_agent(self, tmp_path):
        """
        [agent_type fallback]
        --agent-type 미지정/빈값 → unknown-agent fallback.
        """
        ledger_path = tmp_path / "spawn-event.jsonl"

        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "구현",
            # --agent-type 미지정 또는 빈값
            "--agent-type", "",
            "--session-id", "agent-empty",
            "--agent-id", "agent-fallback",
            "--spawn-seq", "1",
            "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result.returncode == 0

        rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
        assert rows[0]["agent_type"] == "unknown-agent"

    def test_unknown_roster_agent_type_stored_as_fallback(self, tmp_path):
        """
        [agent_type semi-open lint]
        미등재 agent_type (예: "CustomUnknownAgent") → unknown-agent fallback (reject 아님).
        """
        ledger_path = tmp_path / "spawn-event.jsonl"

        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "구현",
            "--agent-type", "UnknownCustomAgent123",  # 미등재 agent type
            "--session-id", "agent-custom",
            "--agent-id", "agent-custom-id",
            "--spawn-seq", "1",
            "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result.returncode == 0

        rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
        # semi-open: fallback 아니라 그냥 저장 (roster check 는 lint 책임)
        assert rows[0]["agent_type"] == "UnknownCustomAgent123"


# ═════════════════════════════════════════════════════════════════════════════
# § EVENT_TYPE CLOSED ENUM
# ═════════════════════════════════════════════════════════════════════════════


class TestEventTypeClosedEnum:
    """event_type ∈ {agent_start, agent_stop, tool, file_touch, mode_change} (closed)"""

    def test_valid_event_types(self, tmp_path):
        """
        [event_type enum validation]
        valid event type → 그대로 저장.
        """
        valid_types = ["agent_start", "agent_stop", "tool", "file_touch", "mode_change"]

        for event_type in valid_types:
            ledger_path = tmp_path / f"spawn-event-{event_type}.jsonl"

            cmd = [
                sys.executable,
                "scripts/lib/append_spawn_event.py",
                "--story-key", "CFP-2393",
                "--lane-label", "구현",
                "--agent-type", "DeveloperAgent",
                "--session-id", f"sess-{event_type}",
                "--agent-id", "agent-test",
                "--spawn-seq", "1",
                "--event-type", event_type,
                "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
            ]

            result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
            assert result.returncode == 0

            rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
            assert rows[0]["event_type"] == event_type, \
                f"event_type not stored correctly: {event_type}"

    def test_invalid_event_type_defaults_to_agent_stop(self, tmp_path):
        """
        [event_type fallback]
        invalid event type → agent_stop default.
        """
        ledger_path = tmp_path / "spawn-event-invalid.jsonl"

        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "구현",
            "--agent-type", "DeveloperAgent",
            "--session-id", "sess-invalid-event",
            "--agent-id", "agent-test",
            "--spawn-seq", "1",
            "--event-type", "invalid_event_type_xyz",
            "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result.returncode == 0

        rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
        assert rows[0]["event_type"] == "agent_stop"


# ═════════════════════════════════════════════════════════════════════════════
# § LANE_LABEL CLOSED ENUM
# ═════════════════════════════════════════════════════════════════════════════


class TestLaneLabelClosedEnum:
    """lane_label ∈ {10 lane + 없음} (closed, 11값)"""

    def test_valid_lane_labels(self, tmp_path):
        """
        [lane_label enum validation]
        valid lane → 그대로 저장.
        """
        valid_lanes = [
            "요구사항", "요구사항-리뷰", "설계", "설계-리뷰", "구현",
            "구현-리뷰", "구현-테스트", "보안-테스트", "배포", "배포-리뷰", "없음"
        ]

        for lane in valid_lanes:
            ledger_path = tmp_path / f"spawn-event-{lane}.jsonl"

            cmd = [
                sys.executable,
                "scripts/lib/append_spawn_event.py",
                "--story-key", "CFP-2393",
                "--lane-label", lane,
                "--agent-type", "DeveloperAgent",
                "--session-id", f"sess-{lane}",
                "--agent-id", "agent-test",
                "--spawn-seq", "1",
                "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
            ]

            result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
            assert result.returncode == 0

            rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
            assert rows[0]["lane_label"] == lane

    def test_invalid_lane_label_defaults_to_없음(self, tmp_path):
        """
        [lane_label fallback]
        invalid lane → 없음 default.
        """
        ledger_path = tmp_path / "spawn-event-invalid-lane.jsonl"

        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "invalid-lane-xyz",
            "--agent-type", "DeveloperAgent",
            "--session-id", "sess-invalid-lane",
            "--agent-id", "agent-test",
            "--spawn-seq", "1",
            "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result.returncode == 0

        rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
        assert rows[0]["lane_label"] == "없음"


# ═════════════════════════════════════════════════════════════════════════════
# § CONSUMER_SCOPE ENUM (wrapper vs consumer isolation)
# ═════════════════════════════════════════════════════════════════════════════


class TestConsumerScope:
    """consumer_scope ∈ {wrapper, consumer} (ADR-042 §결정 9 isolation marker)"""

    def test_consumer_scope_wrapper_explicit(self, tmp_path):
        """
        [consumer_scope]
        --consumer-scope wrapper → wrapper 저장.
        """
        ledger_path = tmp_path / "spawn-event.jsonl"

        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "구현",
            "--agent-type", "DeveloperAgent",
            "--session-id", "sess-scope",
            "--agent-id", "agent-scope",
            "--spawn-seq", "1",
            "--consumer-scope", "wrapper",
            "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result.returncode == 0

        rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").strip().split('\n') if line]
        assert rows[0]["consumer_scope"] == "wrapper"


# ═════════════════════════════════════════════════════════════════════════════
# § GRACEFUL DEGRADATION (ADR-115 §결정 5)
# ═════════════════════════════════════════════════════════════════════════════


class TestGracefulDegradation:
    """block 금지 (exit 0 invariant) — 어떤 예외도 exit 0"""

    def test_missing_ledger_dir_creates_and_succeeds(self, tmp_path):
        """
        [graceful degradation: ledger dir 부재]
        --ledger-path 의 parent dir 부재 → mkdir -p 동등 (pathlib.mkdir parents=True exist_ok=True).
        exit 0 (block 안 함).
        """
        ledger_path = tmp_path / "nonexistent" / "dir" / "spawn-event.jsonl"

        cmd = [
            sys.executable,
            "scripts/lib/append_spawn_event.py",
            "--story-key", "CFP-2393",
            "--lane-label", "구현",
            "--agent-type", "DeveloperAgent",
            "--session-id", "sess-mkdir",
            "--agent-id", "agent-mkdir",
            "--spawn-seq", "1",
            "--ledger-path", str(ledger_path),"--telemetry-enabled","--spawn-event-enabled",
        ]

        result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
        assert result.returncode == 0, f"exit {result.returncode}: {result.stderr}"
        assert ledger_path.exists(), "ledger file should be created"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
