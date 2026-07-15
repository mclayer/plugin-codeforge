"""test_dev_process_inv8b_ordering.py — INV-8b blob-before-index + emit_source + lane fallback.

CFP-2687 Phase 2. Change Plan §7.1 (INV-8b, T-DPE-5) + §3.4 (capture 이원화 / emit_source /
NON-ambient lane→"없음") + Story §5.4.

★ wave-2 sibling (emit_dev_process_event.py + hooks/*-dev-process-capture, HookDev) 는 본
worktree 에 아직 착지하지 않았다. INV-8b orchestration(capture_blob→append_event)의 소유자는
그 emit 계층이므로, 착지 전에는:
  · INV-8b 를 primitive 조합 수준에서 검증 (blob 이 index 前 durable, 역순 = dangling 검출).
  · emit_source / NON-ambient lane fallback 은 append primitive 수준에서 검증 (계약 표면 동일).
  · wave-2 landing 시 자동 활성화되는 조건부 full-orchestration test 를 함께 배선.
이 파일은 emit 계층 착지 후 그 orchestration 을 직접 겨냥하는 test 로 확장(재spawn)된다.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import append_dev_process_event as ade
import dev_process_blob_store as bs
import query_dev_process_event as q


def _read_rows(ledger: Path):
    if not ledger.exists():
        return []
    return [json.loads(ln) for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _emit_ordered(raw, ledger, store_root, **index_fields):
    """INV-8b 를 준수하는 정석 orchestration 을 test 안에서 모델링.

    (1) capture_blob (blob write 완결) → (2) append_event(blob_ref).
    emit 계층(wave-2)이 소유하는 순서를 primitive 로 재현해 순서 불변식을 검증."""
    blob_ref, _audit = bs.capture_blob(raw, root=str(store_root))
    eid = ade.append_event(ledger_path=str(ledger), blob_ref=blob_ref, **index_fields)
    return blob_ref, eid


# ══════════════════════════════════════════════════════════════════════════════
# § INV-8b — blob written BEFORE index row (T-DPE-5 dangling 봉인) — CORE
# ══════════════════════════════════════════════════════════════════════════════
class TestInv8bBlobBeforeIndex:
    def test_blob_durable_before_index_exists(self, tmp_path):
        """capture_blob 반환 시점에 blob 은 disk 에 durable, index 원장은 아직 0행."""
        ledger = tmp_path / "dev-process-event.jsonl"
        store = tmp_path / "store"
        blob_ref, _ = bs.capture_blob("prompt evidence body", root=str(store))
        # blob 은 즉시 deref 가능 (write 완결)
        assert bs.deref_blob(blob_ref, root=str(store)) is not None
        # 아직 append_event 호출 전 → index 원장 부재/0행
        assert _read_rows(ledger) == []

    def test_correct_order_never_dangling(self, tmp_path):
        """정석 순서(blob→index)로 기록된 모든 index row 의 blob_ref 는 deref 가능(non-dangling)."""
        ledger = tmp_path / "dev-process-event.jsonl"
        store = tmp_path / "store"
        for i in range(3):
            _emit_ordered(
                "evidence payload %d" % i, ledger, store,
                event_type="prompt_input", emit_source="hook",
                story_key="CFP-2687", lane_label="구현", consumer_scope="wrapper", seq=str(i),
            )
        rows = _read_rows(ledger)
        assert len(rows) == 3
        for r in rows:
            assert r["blob_ref"] is not None
            assert bs.deref_blob(r["blob_ref"], root=str(store)) is not None, \
                "index row 가 dangling blob_ref 참조 (INV-8b 위반)"

    def test_wrong_order_produces_dangling_NEGATIVE_CONTROL(self, tmp_path):
        """[negative control] index-first(역순) 로 기록하면 dangling 이 실제로 발생한다.

        → 'no-dangling' 검사가 순서에 민감(discriminating)함을 in-suite 증명.
        blob 이 store 에 없는데 index 가 그 blob_ref 를 참조하면 deref None (dangling)."""
        ledger = tmp_path / "dev-process-event.jsonl"
        store = tmp_path / "store"
        # blob 을 만들지 않고, 존재하지 않는 blob_ref 로 index 를 먼저 기록 (역순 시뮬레이션)
        fake_ref = "c" * 64
        ade.append_event(ledger_path=str(ledger), blob_ref=fake_ref,
                         event_type="prompt_input", emit_source="hook",
                         story_key="CFP-2687", lane_label="구현", consumer_scope="wrapper")
        rows = _read_rows(ledger)
        assert rows[0]["blob_ref"] == fake_ref
        # 역순 결과 = dangling: index 는 있는데 blob 은 없음 (금지 상태)
        assert bs.deref_blob(fake_ref, root=str(store)) is None

    def test_crash_between_leaves_orphan_blob_not_dangling_index(self, tmp_path):
        """crash 가 blob write 後·index write 前 이면 → {blob 존재, index 부재} (허용 가능한
        orphan blob, GC 대상). 절대 {index 존재, blob 부재}(dangling) 로 남지 않는다."""
        ledger = tmp_path / "dev-process-event.jsonl"
        store = tmp_path / "store"
        blob_ref, _ = bs.capture_blob("evidence before crash", root=str(store))
        # ── 여기서 crash (append_event 미도달) ──
        assert bs.deref_blob(blob_ref, root=str(store)) is not None   # blob 존재
        assert _read_rows(ledger) == []                                # index 부재 (orphan blob)


# ══════════════════════════════════════════════════════════════════════════════
# § emit_source discriminator {hook, agent} (§3.4)
# ══════════════════════════════════════════════════════════════════════════════
class TestEmitSourceDiscriminator:
    def test_hook_and_agent_both_accepted(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        ade.append_event(ledger_path=str(ledger), event_type="prompt_input",
                         emit_source="hook", story_key="CFP-2687", lane_label="구현",
                         consumer_scope="wrapper", seq="h")
        ade.append_event(ledger_path=str(ledger), event_type="verdict",
                         emit_source="agent", story_key="CFP-2687", lane_label="구현-리뷰",
                         consumer_scope="wrapper", seq="a")
        rows = _read_rows(ledger)
        assert {r["emit_source"] for r in rows} == {"hook", "agent"}

    def test_spoofed_emit_source_rejected(self, tmp_path):
        eid = ade.append_event(
            ledger_path=str(tmp_path / "dev-process-event.jsonl"),
            event_type="verdict", emit_source="spoofed-provenance",
            story_key="CFP-2687", lane_label="구현", consumer_scope="wrapper",
        )
        assert eid is None


# ══════════════════════════════════════════════════════════════════════════════
# § NON-ambient lane → "없음" fallback (vacuous, not fake-consistent) (§3.4)
# ══════════════════════════════════════════════════════════════════════════════
class TestNonAmbientLaneFallback:
    def test_unknown_lane_falls_back_to_none_label(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        ade.append_event(ledger_path=str(ledger), event_type="tool_call",
                         emit_source="hook", story_key="CFP-2687",
                         lane_label="totally-not-a-registered-lane", consumer_scope="wrapper")
        assert _read_rows(ledger)[0]["lane_label"] == "없음"

    def test_empty_lane_falls_back_to_none_label(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        ade.append_event(ledger_path=str(ledger), event_type="tool_call",
                         emit_source="hook", story_key="CFP-2687",
                         lane_label="", consumer_scope="wrapper")
        assert _read_rows(ledger)[0]["lane_label"] == "없음"

    def test_valid_lane_preserved(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        ade.append_event(ledger_path=str(ledger), event_type="lane_transition",
                         emit_source="agent", story_key="CFP-2687",
                         lane_label="보안-테스트", consumer_scope="wrapper")
        assert _read_rows(ledger)[0]["lane_label"] == "보안-테스트"


# ══════════════════════════════════════════════════════════════════════════════
# § emit 계층(wave-2 HookDev) 실 orchestration — INV-8b 의 실제 소유자 대상 검증
# ══════════════════════════════════════════════════════════════════════════════
try:
    import emit_dev_process_event as emitmod
except Exception:  # pragma: no cover
    emitmod = None

_EMIT_REQUIRED = pytest.mark.skipif(
    emitmod is None,
    reason="wave-2 emit_dev_process_event 미착지 — 착지 후 활성화(INV-8b 는 위 primitive 조합으로도 커버)",
)

_SECRET = "api_key = AKIAIOSFODNN7EXAMPLE and /home/mccho/.ssh/id_rsa"


def _boom(*_a, **_k):
    raise OSError("append failure injected")


@_EMIT_REQUIRED
class TestEmitLayerOrchestration:
    """emit(Port B) dispatcher 가 INV-8b/content-blind/redaction-선행/activation 를 실 orchestrate.

    primitive 조합 모델(위)보다 강함 — INV-8b 순서의 실제 소유자(emit 계층)를 직접 겨냥."""

    def test_inv8b_content_event_blob_before_index_and_content_blind(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        store = tmp_path / "store"
        eid = emitmod.emit_lane_transition(
            "CFP-2687", "구현",
            content="lane 전이 설계-리뷰 → 구현. " + _SECRET,
            consumer_scope="wrapper", ledger_path=str(ledger), blob_root=str(store),
        )
        assert eid is not None and len(eid) == 64
        row = _read_rows(ledger)[0]
        # Port B → emit_source=agent
        assert row["emit_source"] == "agent"
        # INV-8b: blob_ref 존재 + deref 성공 (blob 이 index 前 durable, dangling 0)
        assert row["blob_ref"] is not None
        blob = bs.deref_blob(row["blob_ref"], root=str(store))
        assert blob is not None, "index row 의 blob 부재 (INV-8b blob-before-index 위반)"
        # content-blind: raw secret 이 index row 에 절대 유입되지 않음
        rowjson = json.dumps(row, ensure_ascii=False)
        assert "AKIAIOSFODNN7EXAMPLE" not in rowjson and "/home/" not in rowjson
        assert "content" not in row
        # redaction-선행: secret 원문이 blob 에도 없음 + audit 기록
        assert b"AKIAIOSFODNN7EXAMPLE" not in blob, "blob 에 raw secret 잔존 (redaction 미선행)"
        assert row["redaction_applied"] is True and row["redaction_count"] >= 1

    def test_content_none_is_blob_less(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        emitmod.emit_verdict("CFP-2687", "구현-리뷰", content=None, consumer_scope="wrapper",
                             ledger_path=str(ledger), blob_root=str(tmp_path / "s"))
        row = _read_rows(ledger)[-1]
        assert row["blob_ref"] is None and row["redaction_applied"] is False

    def test_port_a_event_types_rejected(self, tmp_path):
        """hook-source 3종(prompt_input/tool_call/diff)은 agent writer 로 기록 금지(Port 경계)."""
        ledger = tmp_path / "dev-process-event.jsonl"
        for t in ("prompt_input", "tool_call", "diff"):
            out = emitmod.emit(t, content="x", consumer_scope="wrapper",
                               ledger_path=str(ledger), blob_root=str(tmp_path / "s"),
                               story_key="CFP-2687", lane_label="구현")
            assert out is None, f"Port A event_type={t} 이 agent writer 로 기록됨"
        assert _read_rows(ledger) == []

    def test_activation_gate_wrapper_on_consumer_off(self, tmp_path):
        """α 비대칭: wrapper always-on(기록) / consumer opt-in default-false(미기록)."""
        lw = tmp_path / "w.jsonl"
        lc = tmp_path / "c.jsonl"
        assert emitmod.emit_lane_transition(
            "CFP-2687", "구현", content="x", consumer_scope="wrapper",
            ledger_path=str(lw), blob_root=str(tmp_path / "sw")) is not None
        assert emitmod.emit_lane_transition(
            "CFP-2687", "구현", content="x", consumer_scope="consumer",
            ledger_path=str(lc), blob_root=str(tmp_path / "sc")) is None
        assert _read_rows(lc) == [], "consumer default-false 인데 기록됨"

    def test_record_only_non_blocking_on_injected_failure(self, tmp_path, monkeypatch):
        """append 실패 주입 → emit 은 raise 없이 None 반환(record-only exit-0, ADR-115)."""
        monkeypatch.setattr(emitmod, "append_event", _boom)
        out = emitmod.emit_lane_transition(
            "CFP-2687", "구현", content=None, consumer_scope="wrapper",
            ledger_path=str(tmp_path / "l.jsonl"), blob_root=str(tmp_path / "s"))
        assert out is None
