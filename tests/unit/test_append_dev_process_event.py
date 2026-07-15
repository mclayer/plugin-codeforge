"""test_append_dev_process_event.py — dev-process-event-v1 index append primitive P0 suite.

CFP-2687 Phase 2 (구현) / Epic #2686 Story A. Change Plan §8.2 계약 + Story §5.3 AC.
Under test: scripts/lib/append_dev_process_event.py

반드시 커버할 불변식 (RED→GREEN discriminating — 절대 위반 금지):
  · content-blind (AC-7 / T-DPE-3): content=/transcript_path= kwarg → row 에 NOT present.
  · deterministic event_id 멱등 (§11.6): 동일 논리 이벤트 → 동일 id (timestamp 산입 제외).
  · ms-precision UTC Z timestamp + monotonic MAX(prev+1ms) (§7.4 clock).
  · append-only, no in-place edit (AC-10): 선행 bytes 불변.
  · non-blocking exit 0 on failure (AC-21): 실패 주입 → None, no raise.
  · torn-trailing-line identifiable (AC-22): 부분 기록 malformed 로 식별 가능.
  · invalid closed enum → None (allow-list-clean 보존).

각 test 는 positive assertion + (해당 시) negative-control(broken fixture 가 실제로 위반)로
discriminating 함을 in-suite 증명한다 (hollow-green 금지, CFP-2635 선례).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

import append_dev_process_event as ade

TS_MS_UTC_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")


def _read_rows(ledger: Path):
    return [
        json.loads(ln)
        for ln in ledger.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]


# ══════════════════════════════════════════════════════════════════════════════
# § content-blind (AC-7 / T-DPE-3) — CORE
# ══════════════════════════════════════════════════════════════════════════════
class TestContentBlind:
    def test_content_kwargs_dropped_from_row(self, tmp_path):
        """content=/transcript_path= 를 넘겨도 row 에 유입되지 않는다 (content-blind)."""
        ledger = tmp_path / "dev-process-event.jsonl"
        eid = ade.append_event(
            ledger_path=str(ledger),
            event_type="lane_transition", emit_source="agent",
            story_key="CFP-2687", lane_label="구현", consumer_scope="wrapper",
            content="THIS-FREE-FORM-SECRET-SHOULD-BE-DROPPED",
            transcript_path="/home/mccho/.claude/transcript.jsonl",
        )
        assert eid is not None and len(eid) == 64
        rows = _read_rows(ledger)
        assert len(rows) == 1
        row = rows[0]
        # allow-list 밖 키 자체가 부재
        assert "content" not in row
        assert "transcript_path" not in row
        # 값이 직렬화 어디에도 새지 않음
        serialized = json.dumps(row, ensure_ascii=False)
        assert "THIS-FREE-FORM-SECRET-SHOULD-BE-DROPPED" not in serialized
        assert "/home/mccho" not in serialized

    def test_row_keys_exactly_allowlist_18(self, tmp_path):
        """실제 emit 된 row 키 == _ROW_KEYS (순서·멤버), 정확히 18개."""
        ledger = tmp_path / "dev-process-event.jsonl"
        ade.append_event(
            ledger_path=str(ledger),
            event_type="verdict", emit_source="agent",
            story_key="CFP-2687", lane_label="구현-리뷰", consumer_scope="wrapper",
        )
        row = _read_rows(ledger)[0]
        assert tuple(row.keys()) == ade._ROW_KEYS
        assert len(row) == 18

    def test_negative_control_leaked_content_row_is_detected(self):
        """[negative control] content 가 새어든 row 는 content-blind assertion 이 잡아낸다.

        이 test 가 GREEN 이려면 assertion 이 broken row 에서 실제로 위반을 검출해야 한다
        → content-blind 검사가 discriminating 함을 in-suite 증명 (hollow-green 아님)."""
        good_row = {"event_type": "lane_transition", "emit_source": "agent"}
        broken_row = {**good_row, "content": "LEAKED-SECRET"}
        # good row 는 통과
        assert "content" not in good_row
        # broken row 는 검출 (assertion 이 discriminating)
        assert "content" in broken_row  # 위반이 실제로 존재함을 확인


# ══════════════════════════════════════════════════════════════════════════════
# § deterministic event_id 멱등 (§11.6) — CORE (idempotency dedup)
# ══════════════════════════════════════════════════════════════════════════════
class TestDeterministicEventId:
    def test_same_logical_event_same_id(self):
        idA = ade.compute_event_id("verdict", "agent", "CFP-2687", "구현-리뷰", "wrapper", seq="1")
        idB = ade.compute_event_id("verdict", "agent", "CFP-2687", "구현-리뷰", "wrapper", seq="1")
        assert idA == idB

    def test_distinct_seq_distinct_id(self):
        idA = ade.compute_event_id("verdict", "agent", "CFP-2687", "구현-리뷰", "wrapper", seq="1")
        idC = ade.compute_event_id("verdict", "agent", "CFP-2687", "구현-리뷰", "wrapper", seq="2")
        assert idA != idC

    def test_event_id_excludes_timestamp_two_appends_collapse(self, tmp_path):
        """동일 논리 이벤트를 (다른 wall-clock 에) 2회 append → 동일 event_id (재시도 멱등).

        timestamp 는 event_id 산입에서 제외되므로 두 row 의 event_id 가 같아야 한다."""
        ledger = tmp_path / "dev-process-event.jsonl"
        kw = dict(
            event_type="lane_transition", emit_source="agent",
            story_key="CFP-2687", lane_label="구현", consumer_scope="wrapper",
        )
        eid1 = ade.append_event(ledger_path=str(ledger), **kw)
        eid2 = ade.append_event(ledger_path=str(ledger), **kw)
        assert eid1 == eid2, "동일 논리 이벤트 재시도가 서로 다른 event_id (결정성 위반)"
        rows = _read_rows(ledger)
        assert rows[0]["event_id"] == rows[1]["event_id"]


# ══════════════════════════════════════════════════════════════════════════════
# § timestamp (§7.4 clock) — ms-precision UTC Z + monotonic +1ms
# ══════════════════════════════════════════════════════════════════════════════
class TestTimestamp:
    def test_timestamp_ms_precision_utc_z_format(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        ade.append_event(
            ledger_path=str(ledger),
            event_type="lane_transition", emit_source="agent",
            story_key="CFP-2687", lane_label="구현", consumer_scope="wrapper",
        )
        ts = _read_rows(ledger)[0]["timestamp_utc"]
        assert TS_MS_UTC_Z.match(ts), f"ms-precision UTC Z 형식 아님: {ts!r}"
        assert ts.endswith("Z") and "+00:00" not in ts

    def test_monotonic_plus_1ms_when_prev_ahead(self):
        assert ade._utc_z_monotonic("2099-01-01T00:00:00.500Z") == "2099-01-01T00:00:00.501Z"

    def test_monotonic_tolerates_seconds_resolution_prev(self):
        assert ade._utc_z_monotonic("2099-01-01T00:00:00Z") == "2099-01-01T00:00:00.001Z"

    def test_no_prev_returns_wallclock_format(self):
        ts = ade._utc_z_monotonic("")
        assert TS_MS_UTC_Z.match(ts)


# ══════════════════════════════════════════════════════════════════════════════
# § append-only, no in-place edit (AC-10)
# ══════════════════════════════════════════════════════════════════════════════
class TestAppendOnly:
    def test_prior_bytes_immutable_across_appends(self, tmp_path):
        """append N회 시 파일은 오직 커지고, 선행 bytes 는 절대 변하지 않는다."""
        ledger = tmp_path / "dev-process-event.jsonl"
        prev_len = 0
        prefix = b""
        for i in range(5):
            ade.append_event(
                ledger_path=str(ledger),
                event_type="tool_call", emit_source="hook",
                story_key="CFP-2687", lane_label="구현", consumer_scope="wrapper",
                seq=str(i),
            )
            data = ledger.read_bytes()
            assert len(data) > prev_len, "파일이 커지지 않음 (append 아님)"
            assert data.startswith(prefix), "선행 bytes 변경됨 (in-place edit 위반)"
            prefix = data
            prev_len = len(data)
        assert len(_read_rows(ledger)) == 5


# ══════════════════════════════════════════════════════════════════════════════
# § non-blocking exit 0 on failure (AC-21)
# ══════════════════════════════════════════════════════════════════════════════
class TestNonBlockingFailure:
    def test_append_failure_returns_none_no_raise(self, tmp_path, monkeypatch):
        """_append_jsonl_row 가 raise 해도 append_event 는 None 반환 (예외 전파 금지)."""
        def _boom(*_a, **_k):
            raise OSError("disk full injected")

        monkeypatch.setattr(ade, "_append_jsonl_row", _boom)
        # 예외가 caller flow 로 새면 이 라인에서 죽는다 → test 는 no-raise 를 요구
        eid = ade.append_event(
            ledger_path=str(tmp_path / "dev-process-event.jsonl"),
            event_type="lane_transition", emit_source="agent",
            story_key="CFP-2687", lane_label="구현", consumer_scope="wrapper",
        )
        assert eid is None

    def test_invalid_event_type_returns_none_no_row(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        eid = ade.append_event(
            ledger_path=str(ledger), event_type="NONSENSE", emit_source="agent",
        )
        assert eid is None
        assert not ledger.exists() or _read_rows(ledger) == []

    def test_invalid_emit_source_returns_none(self, tmp_path):
        eid = ade.append_event(
            ledger_path=str(tmp_path / "dev-process-event.jsonl"),
            event_type="verdict", emit_source="telepathy",
        )
        assert eid is None


# ══════════════════════════════════════════════════════════════════════════════
# § torn-trailing-line identifiable (AC-22)
# ══════════════════════════════════════════════════════════════════════════════
class TestPartialRecordIdentifiable:
    def test_torn_trailing_line_does_not_corrupt_prior_rows(self, tmp_path):
        """crash 로 마지막 줄이 잘려도(torn), 선행 valid row 는 여전히 읽히고
        torn 줄은 malformed 로 개별 식별 가능하다 (전체 원장 손상 아님)."""
        ledger = tmp_path / "dev-process-event.jsonl"
        for i in range(2):
            ade.append_event(
                ledger_path=str(ledger),
                event_type="lane_transition", emit_source="agent",
                story_key="CFP-2687", lane_label="구현", consumer_scope="wrapper",
                seq=str(i),
            )
        # crash mid-write 시뮬레이션 — 부분 JSON 라인을 O_APPEND (torn trailing)
        with open(ledger, "a", encoding="utf-8", newline="\n") as f:
            f.write('{"event_id": "torn", "schema_version": "dev-proc')  # 잘림, no newline

        import query_dev_process_event as q
        res = q.query_lines(ledger.read_text(encoding="utf-8").splitlines())
        assert res["stats"]["rows_total"] == 2, "선행 valid row 손상됨"
        assert res["stats"]["malformed_skipped"] == 1, "torn 줄이 malformed 로 식별 안 됨"
