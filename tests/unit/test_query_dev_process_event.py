"""test_query_dev_process_event.py — mining/query port suite (raw rows, B/C disjoint).

CFP-2687 Phase 2. Change Plan §3.6 + §8 + Story AC-16/17.
Under test: scripts/lib/query_dev_process_event.py

불변식:
  · AC-17: raw typed rows 만 반환 — NO aggregation / NO verdict.
  · read-time dedup (event_id): 동일 event_id → 1행으로 collapse (관측치, guaranteed-unique 아님).
  · read-only: query 후 원장 byte 불변.
  · blob deref 통합: include_blob → _blob == redacted bytes.
  · filter: story_key / lane_label / event_type / time-window.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import append_dev_process_event as ade
import query_dev_process_event as q


def _seed(ledger: Path):
    """append primitive 로 실제 원장 seed (fixture 위조 아님 — 진짜 emit)."""
    ade.append_event(ledger_path=str(ledger), event_type="lane_transition",
                     emit_source="agent", story_key="CFP-2687", lane_label="구현",
                     consumer_scope="wrapper", seq="a")
    ade.append_event(ledger_path=str(ledger), event_type="verdict",
                     emit_source="agent", story_key="CFP-2687", lane_label="구현-리뷰",
                     consumer_scope="wrapper", seq="b")
    ade.append_event(ledger_path=str(ledger), event_type="lane_transition",
                     emit_source="agent", story_key="CFP-2688", lane_label="설계",
                     consumer_scope="wrapper", seq="c")


class TestRawRowsNoAggregation:
    def test_query_returns_list_of_raw_dicts(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        _seed(ledger)
        rows = q.query(ledger_path=str(ledger))
        assert isinstance(rows, list)
        assert all(isinstance(r, dict) for r in rows)
        # 각 row 는 raw index row — allow-list 필드 보유, 집계 키(count/verdict/pass) 부재
        for r in rows:
            assert set(r.keys()).issubset(set(ade._ROW_KEYS))
            assert "verdict_result" not in r and "count" not in r and "pass" not in r

    def test_stats_are_observations_not_verdict(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        _seed(ledger)
        rows, stats = q.query_with_stats(ledger_path=str(ledger))
        assert "rows_total" in stats and "duplicates_collapsed" in stats
        assert "honesty_note" in stats
        # PASS/FAIL verdict 미산출
        assert "PASS" not in json.dumps(stats) and "FAIL" not in json.dumps(stats)


class TestReadTimeDedup:
    def test_identical_event_id_collapses(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        # 동일 논리 이벤트 2회 append → 동일 event_id (append primitive 결정성)
        kw = dict(event_type="lane_transition", emit_source="agent",
                  story_key="CFP-2687", lane_label="구현", consumer_scope="wrapper", seq="dup")
        ade.append_event(ledger_path=str(ledger), **kw)
        ade.append_event(ledger_path=str(ledger), **kw)
        rows, stats = q.query_with_stats(ledger_path=str(ledger))
        assert stats["rows_total"] == 2
        assert stats["duplicates_collapsed"] == 1
        assert stats["rows_deduped"] == 1
        assert len(rows) == 1

    def test_negative_control_distinct_ids_not_collapsed(self, tmp_path):
        """[negative control] 서로 다른 event_id 는 collapse 되지 않는다 (dedup 이 과잉 아님)."""
        ledger = tmp_path / "dev-process-event.jsonl"
        _seed(ledger)  # 3 distinct events
        rows, stats = q.query_with_stats(ledger_path=str(ledger))
        assert stats["duplicates_collapsed"] == 0
        assert len(rows) == 3


class TestReadOnly:
    def test_query_does_not_mutate_ledger(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        _seed(ledger)
        before = ledger.read_bytes()
        q.query(ledger_path=str(ledger), story_key="CFP-2687")
        q.query_with_stats(ledger_path=str(ledger))
        after = ledger.read_bytes()
        assert before == after, "query 후 원장 byte 변경 (read-only INV 위반)"


class TestFilters:
    def test_story_key_filter(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        _seed(ledger)
        rows = q.query(ledger_path=str(ledger), story_key="CFP-2687")
        assert len(rows) == 2
        assert all(r["story_key"] == "CFP-2687" for r in rows)

    def test_event_type_and_lane_composite_filter(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        _seed(ledger)
        rows = q.query(ledger_path=str(ledger), event_type="lane_transition",
                       story_key="CFP-2687")
        assert len(rows) == 1
        assert rows[0]["lane_label"] == "구현"

    def test_empty_ledger_zero_rows(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        rows = q.query(ledger_path=str(ledger))
        assert rows == []


class TestBlobDerefIntegration:
    def test_include_blob_returns_redacted_bytes(self, tmp_path, monkeypatch):
        """include_blob → blob_ref 보유 row 에 _blob == redacted bytes 부착 (blob store 통합)."""
        import dev_process_blob_store as bs
        # blob 저장은 blob store root 에, index 는 ledger 에
        blob_root = tmp_path / "store"
        blob_ref, _ = bs.capture_blob("evidence body for query deref", root=str(blob_root))
        assert blob_ref is not None

        # query 의 deref sibling 이 같은 root 를 보도록 wrap
        monkeypatch.setattr(q, "_deref_blob",
                            lambda ref: bs.deref_blob(ref, root=str(blob_root)))

        ledger = tmp_path / "dev-process-event.jsonl"
        ade.append_event(ledger_path=str(ledger), event_type="prompt_input",
                         emit_source="hook", story_key="CFP-2687", lane_label="구현",
                         consumer_scope="wrapper", blob_ref=blob_ref, seq="blob")
        res = q.query_file(ledger_path=str(ledger), include_blob=True)
        row = res["rows"][0]
        assert row["_blob_deref_available"] is True
        assert row["_blob"] == bs.deref_blob(blob_ref, root=str(blob_root))
        assert b"evidence body" in row["_blob"]
