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
import threading
from pathlib import Path

import pytest

import append_dev_process_event as ade
import dev_process_blob_store as bs
import query_dev_process_event as q

# CFP-2817: KPI 집계기 (AC-2 판정식 — 무변경 소비 접점)
try:
    import aggregate_dev_process_event as agg
except Exception:  # pragma: no cover
    agg = None

_AGG_REQUIRED = pytest.mark.skipif(agg is None, reason="aggregate_dev_process_event 미착지")


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


# ── CFP-2817 D1: derive_seq (production role:dev 착지 전 예상 RED) ──
def _derive_seq():
    """emit_dev_process_event.derive_seq 반환 or 명확한 RED (hollow-green 차단)."""
    assert emitmod is not None, "emit_dev_process_event 미착지 — derive_seq 검증 불가"
    fn = getattr(emitmod, "derive_seq", None)
    assert fn is not None, (
        "emit_dev_process_event.derive_seq 미구현 — CFP-2817 D1 착지 전 예상 RED (구현 후 GREEN)"
    )
    return fn


# ── AC-2 판정식용 synthetic index row 조립 (격리 aggregate 로직 검증 — 완료 증거 아님, AC-10 무손상) ──
_ALL_ROW_KEYS_DEFAULTS = dict(
    schema_version="dev-process-event-v1", consumer_scope="wrapper",
    defect_id=None, fix_id=None, blob_ref=None,
    redaction_applied=False, redaction_count=0, redaction_rules_fired=[],
    defect_family=None, defect_type=None, time_to_detection=None, detecting_lane=None,
)


def _mk_line(event_type, emit_source, ts, story="CFP-2817", lane="구현", eid=None):
    """격리 검증용 synthetic JSONL row — aggregate 판정식(AC-2) 로직 lock 전용.

    ★ 실 완료-증거 원장이 아니라 in-memory line (AC-10 synthetic-emit 금지와 disjoint —
    이건 aggregate 계산 검증이지 완료 판정 증거가 아님)."""
    eid = eid or "%s|%s|%s|%s" % (event_type, emit_source, ts, lane)
    row = dict(_ALL_ROW_KEYS_DEFAULTS)
    row.update(event_id=eid, event_type=event_type, emit_source=emit_source,
               timestamp_utc=ts, story_key=story, lane_label=lane)
    return json.dumps(row, ensure_ascii=False)


def _cycletime_of(lines):
    res = q.query_lines(lines)
    return agg.aggregate_rows(res["rows"], res["stats"])["cycletime"]


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


# ══════════════════════════════════════════════════════════════════════════════
# § CFP-2817 AC-6 — 6-point → lane_transition 매핑 회귀 (CLI 배선 end-to-end)
#   CLI 가 --transition-kind → derive_seq 파생 → seq 각인 → 6 상이 event_id.
# ══════════════════════════════════════════════════════════════════════════════
@_EMIT_REQUIRED
class TestSixPointMappingRegression:
    def test_six_point_via_cli_yields_distinct_event_ids(self, tmp_path):
        """AC-6: 6-point 각 시점 CLI emit → 6 상이 event_id, 6행 전부 생존(dedup 삼킴 0).

        read-time transition-kind 판별은 요구하지 않음(§2.2 coarse) — 행 존재·상이 id 만 관측."""
        ledger = tmp_path / "dev-process-event.jsonl"
        specs = [
            ("enter", []), ("pass", []),
            ("fix-detected", ["--fix-iter", "1"]), ("cause", ["--fix-iter", "1"]),
            ("re-enter", ["--fix-iter", "1"]), ("complete", []),
        ]
        for tok, extra in specs:
            rc = emitmod.main(
                ["lane-transition", "--story-key", "CFP-2817", "--lane-label", "구현",
                 "--transition-kind", tok, "--consumer-scope", "wrapper",
                 "--ledger-path", str(ledger)] + extra)
            assert rc == 0, "CLI lane-transition(%s) exit %r != 0 (record-only 위반)" % (tok, rc)
        rows = q.query(ledger_path=str(ledger), story_key="CFP-2817",
                       lane_label="구현", event_type="lane_transition")
        eids = [r["event_id"] for r in rows]
        assert len(rows) == 6, "6-point lane_transition 행 %d != 6 (dedup 소실 or emit 실패)" % len(rows)
        assert len(set(eids)) == 6, "6-point 이 상이 event_id 를 못 냄: %s" % eids
        assert all(r["emit_source"] == "agent" for r in rows), "6-point 행 emit_source != agent"


# ══════════════════════════════════════════════════════════════════════════════
# § CFP-2817 AC-4 §8.2-D — 재진입 dedup discriminating (생존 / collapse / 멱등)
# ══════════════════════════════════════════════════════════════════════════════
@_EMIT_REQUIRED
class TestReentryDedupDiscriminating:
    _KW = dict(content=None, consumer_scope="wrapper")

    def _emit(self, ledger, store, seq):
        return emitmod.emit_lane_transition(
            "CFP-2817", "구현", ledger_path=str(ledger), blob_root=str(store), seq=seq, **self._KW)

    def test_distinct_reentry_both_survive(self, tmp_path):
        """생존(INV-2 소실0): state-derived seq(enter vs re-enter) → 2행 생존."""
        d = _derive_seq()
        ledger, store = tmp_path / "l.jsonl", tmp_path / "s"
        self._emit(ledger, store, d("enter", fix_iter=None, reset_generation=0, ordinal=0))
        self._emit(ledger, store, d("re-enter", fix_iter=1, reset_generation=0, ordinal=0))
        rows = q.query(ledger_path=str(ledger), story_key="CFP-2817",
                       lane_label="구현", event_type="lane_transition")
        assert len(rows) == 2, "재진입 별개전이 생존 실패 %d != 2 (AC-4 소실)" % len(rows)

    def test_undifferentiated_seq_collapse_NEGATIVE_CONTROL(self, tmp_path):
        """collapse(hollow-green 차단): seq 미분화(둘 다 '') → 동일 event_id → read-time dedup 1행.

        이 붕괴가 실재함을 못박아 위 '생존' 이 discriminating(seq 규율에 민감)함을 in-suite 증명."""
        ledger, store = tmp_path / "l.jsonl", tmp_path / "s"
        self._emit(ledger, store, "")
        self._emit(ledger, store, "")
        rows = q.query(ledger_path=str(ledger), story_key="CFP-2817",
                       lane_label="구현", event_type="lane_transition")
        assert len(rows) == 1, "seq 미분화인데 dedup collapse 안 됨 %d != 1 (충돌 전제 무효)" % len(rows)

    def test_idempotent_retry_collapses(self, tmp_path):
        """멱등대조(INV-1): 동일 논리전이 재시도(동일 derive_seq) → 동일 event_id → 1행."""
        d = _derive_seq()
        ledger, store = tmp_path / "l.jsonl", tmp_path / "s"
        for _ in range(2):
            self._emit(ledger, store, d("re-enter", fix_iter=1, reset_generation=0, ordinal=0))
        rows = q.query(ledger_path=str(ledger), story_key="CFP-2817",
                       lane_label="구현", event_type="lane_transition")
        assert len(rows) == 1, "동일 논리전이 재시도 collapse 안 됨 %d != 1 (멱등 붕괴)" % len(rows)


# ══════════════════════════════════════════════════════════════════════════════
# § CFP-2817 AC-2 §8.2-A1 — 완료판정식 (interval_count>=1, status/measured_at 금지)
#   ★ synthetic line = aggregate 계산 로직 lock 전용, 완료 증거 아님(AC-10 무손상).
# ══════════════════════════════════════════════════════════════════════════════
@_AGG_REQUIRED
class TestAc2NonVacuousVerdict:
    def test_hook_only_ledger_vacuous_status_but_zero_interval(self):
        """★핵심: hook-only 원장 → status='measured'·measured_at non-null (VACUOUS) 이나
        interval_count==0·by_group=={} → 완료판정에 status/measured_at 사용 금지 근거."""
        lines = [
            _mk_line("tool_call", "hook", "2026-07-24T10:00:00.000Z"),
            _mk_line("prompt_input", "hook", "2026-07-24T10:00:01.000Z"),
            _mk_line("diff", "hook", "2026-07-24T10:00:02.000Z"),
        ]
        snap = _cycletime_of(lines)
        assert snap["status"] == "measured", "hook 행 존재인데 status != measured (판정 전제 무효)"
        assert snap["measured_at"] is not None, "hook 행 존재인데 measured_at None (판정 전제 무효)"
        assert snap["overall"]["interval_count"] == 0, "hook-only 인데 interval_count != 0 (오염)"
        assert snap["overall"]["by_group"] == {}, "hook-only 인데 by_group != {}"

    def test_agent_lane_transition_moves_interval_and_closes(self):
        """AC-2 PASS 방향: agent lane_transition≥1 → interval_count≥1; verdict anchor → closed≥1."""
        lines = [
            _mk_line("tool_call", "hook", "2026-07-24T10:00:00.000Z"),        # noise
            _mk_line("lane_transition", "agent", "2026-07-24T10:00:01.000Z", lane="구현"),
            _mk_line("verdict", "agent", "2026-07-24T10:00:05.000Z", lane="구현"),
        ]
        snap = _cycletime_of(lines)
        assert snap["overall"]["interval_count"] >= 1, "agent lane_transition 인데 interval_count 0"
        assert snap["overall"]["closed_interval_count"] >= 1, \
            "verdict anchor 있는데 closed_interval_count 0 (§8.2-A1 강화)"
        assert snap["overall"]["by_group"] != {}, "interval 있는데 by_group == {}"

    def test_hook_noise_does_not_contaminate_interval_count(self):
        """'hook 행이 있어도 interval_count 오염 0' — Port-A hook 타입(tool_call/prompt_input/diff)
        추가는 interval_count 불변. interval_count = emit_source=agent lane_transition 파생
        (Port-A hook 어댑터는 lane_transition 어휘 미발화 → hook lane_transition 행 0 by-construction)."""
        agent_only = [
            _mk_line("lane_transition", "agent", "2026-07-24T10:00:01.000Z", lane="구현"),
            _mk_line("lane_transition", "agent", "2026-07-24T10:00:02.000Z", lane="구현-리뷰"),
        ]
        with_noise = agent_only + [
            _mk_line("tool_call", "hook", "2026-07-24T10:00:03.000Z"),
            _mk_line("prompt_input", "hook", "2026-07-24T10:00:04.000Z"),
            _mk_line("diff", "hook", "2026-07-24T10:00:05.000Z"),
        ]
        ic_clean = _cycletime_of(agent_only)["overall"]["interval_count"]
        ic_noisy = _cycletime_of(with_noise)["overall"]["interval_count"]
        assert ic_clean == ic_noisy == 2, "hook noise 오염: clean=%r noisy=%r" % (ic_clean, ic_noisy)


# ══════════════════════════════════════════════════════════════════════════════
# § CFP-2817 AC-12 — defect_finding 배선-존재 게이트 (격리 ledger, spy + negative-control)
#   dispatch = D6-a emit CLI main() 서브커맨드 (dev-pl-2817 확정). raw --seq 미노출.
# ══════════════════════════════════════════════════════════════════════════════
def _defect_argv(ledger):
    # review-verdict-v4-shaped test-double (실결점 아님 — 배선 존재만 증명). defect_type = closed vocab(OBJ-1).
    return [
        "defect-finding", "--story-key", "CFP-2817", "--lane-label", "구현-리뷰",
        "--transition-kind", "fix-detected", "--fix-iter", "1",
        "--defect-family", "design-boundary", "--defect-type", "boundary-completeness",
        "--detecting-lane", "구현-리뷰", "--consumer-scope", "wrapper",
        "--ledger-path", str(ledger),
    ]


def _lane_argv(ledger):
    return [
        "lane-transition", "--story-key", "CFP-2817", "--lane-label", "구현",
        "--transition-kind", "enter", "--consumer-scope", "wrapper",
        "--ledger-path", str(ledger),
    ]


@_EMIT_REQUIRED
class TestAc12DefectFindingWiring:
    def test_defect_finding_command_lands_agent_row(self, tmp_path):
        """defect-finding 서브커맨드 → 격리 ledger 에 emit_source=agent ∧ defect_finding 행 1개.

        distinct-marker: exit-code 단독 아님 — ledger 행(emit_source=agent) 병행 assert
        (REC-2: emit() 경유 = emit_source=agent 고정, append_event 직접 우회면 이 신호 불성립)."""
        ledger = tmp_path / "dev-process-event.jsonl"
        rc = emitmod.main(_defect_argv(ledger))
        assert rc == 0, "emit CLI defect-finding exit %r != 0 (record-only 위반)" % rc
        rows = q.query(ledger_path=str(ledger), event_type="defect_finding")
        assert len(rows) == 1, "defect_finding 행 %d != 1 (배선 부재)" % len(rows)
        assert rows[0]["emit_source"] == "agent", "defect_finding 이 agent writer 로 안 감 (REC-2 우회)"
        assert rows[0]["defect_family"] == "design-boundary", "defect_family 전파 실패"

    def test_defect_dispatch_calls_emit_defect_finding_SPY(self, tmp_path, monkeypatch):
        """positive: defect-finding 커맨드 → _dispatch_emit 이 emit_defect_finding 실호출(spy)."""
        calls = []
        real = emitmod.emit_defect_finding

        def _spy(*a, **k):
            calls.append((a, k))
            return real(*a, **k)

        monkeypatch.setattr(emitmod, "emit_defect_finding", _spy)
        emitmod.main(_defect_argv(tmp_path / "l.jsonl"))
        assert len(calls) == 1, "defect-finding 커맨드인데 emit_defect_finding 미호출 (배선 부재=AC-12 방지대상)"

    def test_lane_command_does_NOT_call_defect_NEGATIVE_CONTROL(self, tmp_path, monkeypatch):
        """negative-control(hollow-green 차단): lane-transition 커맨드 → emit_defect_finding 미호출.

        clean 세션(결점 미발생)에서 defect dispatch 이 오발화하지 않음을 못박아
        '2/3 배선으로 AC 통과' 오탐(정확히 AC-12 방지대상)을 차단."""
        calls = []
        monkeypatch.setattr(emitmod, "emit_defect_finding", lambda *a, **k: calls.append(1))
        ledger = tmp_path / "l.jsonl"
        emitmod.main(_lane_argv(ledger))
        assert calls == [], "lane-transition 인데 emit_defect_finding 발화 (defect dispatch 오발화)"
        assert q.query(ledger_path=str(ledger), event_type="defect_finding") == [], \
            "lane-transition 인데 defect_finding 행 생성"


# ══════════════════════════════════════════════════════════════════════════════
# § CFP-2817 AC-13 — emit 경로 시각 소스 단일화 (CLI --timestamp 부재, primitive UTC 만)
# ══════════════════════════════════════════════════════════════════════════════
_TS_MS_UTC_Z = __import__("re").compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")


@_EMIT_REQUIRED
class TestAc13TimeSourceWiring:
    def test_cli_rejects_timestamp_flag(self, tmp_path):
        """AC-13: CLI 에 --timestamp 부재 — caller 시각 계산·주입 경로 0 (unrecognized → SystemExit)."""
        with pytest.raises(SystemExit):
            emitmod.main(["lane-transition", "--story-key", "CFP-2817", "--lane-label", "구현",
                          "--transition-kind", "enter",
                          "--timestamp", "2020-01-01T00:00:00.000Z",
                          "--ledger-path", str(tmp_path / "l.jsonl")])

    def test_emitted_timestamp_is_primitive_utc_z(self, tmp_path):
        """저장 timestamp = primitive 내부 UTC Z(ms) — caller 주입 아님(§2.6 축5 기봉인)."""
        ledger = tmp_path / "l.jsonl"
        emitmod.main(["lane-transition", "--story-key", "CFP-2817", "--lane-label", "구현",
                      "--transition-kind", "enter", "--consumer-scope", "wrapper",
                      "--ledger-path", str(ledger)])
        rows = q.query(ledger_path=str(ledger))
        assert len(rows) == 1
        assert _TS_MS_UTC_Z.match(rows[0]["timestamp_utc"]), \
            "timestamp_utc ms-precision UTC Z 아님: %r" % rows[0]["timestamp_utc"]


# ══════════════════════════════════════════════════════════════════════════════
# § CFP-2817 AC-8/AC-7/AC-11 — Port-A 무회귀 + emit_source 무결성 + story_key 오귀속 0
# ══════════════════════════════════════════════════════════════════════════════
@_EMIT_REQUIRED
class TestPortARegressionAndIsolation:
    def test_emit_rejects_all_port_a_types(self, tmp_path):
        """AC-8/INV-7: Port-A 3종(prompt_input/tool_call/diff)은 agent writer(emit)로 기록 0."""
        ledger = tmp_path / "l.jsonl"
        for t in ("prompt_input", "tool_call", "diff"):
            assert emitmod.emit(t, content="x", consumer_scope="wrapper",
                                ledger_path=str(ledger), blob_root=str(tmp_path / "s"),
                                story_key="CFP-2817", lane_label="구현") is None, \
                "Port-A %s 이 agent writer 로 기록됨(침범)" % t
        assert q.query(ledger_path=str(ledger)) == []

    def test_hook_and_agent_streams_coexist(self, tmp_path):
        """AC-8: 배선 후 hook Port-A stream 지속 + agent Port-B 공존(무회귀), 침범 0."""
        ledger = tmp_path / "l.jsonl"
        ade.append_event(ledger_path=str(ledger), event_type="tool_call", emit_source="hook",
                         story_key="CFP-2817", lane_label="구현", consumer_scope="wrapper", seq="h1")
        emitmod.emit_lane_transition("CFP-2817", "구현", content=None, consumer_scope="wrapper",
                                     ledger_path=str(ledger), blob_root=str(tmp_path / "s"), seq="a1")
        rows = q.query(ledger_path=str(ledger))
        assert {r["emit_source"] for r in rows} == {"hook", "agent"}, "hook/agent 공존 실패"
        for r in rows:
            if r["event_type"] in ("prompt_input", "tool_call", "diff"):
                assert r["emit_source"] == "hook", "Port-A 타입이 agent 로 기록(침범)"
            if r["event_type"] in ("lane_transition", "verdict", "defect_finding",
                                   "fix_transition", "final_artifact"):
                assert r["emit_source"] == "agent", "Port-B 타입이 hook 으로 기록"

    def test_emit_stamps_agent_source(self, tmp_path):
        """AC-7/INV-7: emit() 는 emit_source 를 agent 로 고정(writer monopoly)."""
        ledger = tmp_path / "l.jsonl"
        emitmod.emit_lane_transition("CFP-2817", "구현", content=None, consumer_scope="wrapper",
                                     ledger_path=str(ledger), blob_root=str(tmp_path / "s"), seq="x")
        assert q.query(ledger_path=str(ledger))[0]["emit_source"] == "agent"

    def test_parallel_story_keys_no_misattribution(self, tmp_path):
        """AC-11/INV-10: 병렬 Story 동일 ledger — story_key 명시주입 → 오귀속 0, cross-story 충돌 0."""
        ledger, store = tmp_path / "l.jsonl", tmp_path / "s"
        emitmod.emit_lane_transition("CFP-2817", "구현", content=None, consumer_scope="wrapper",
                                     ledger_path=str(ledger), blob_root=str(store), seq="x")
        emitmod.emit_lane_transition("CFP-2999", "구현", content=None, consumer_scope="wrapper",
                                     ledger_path=str(ledger), blob_root=str(store), seq="x")
        r17 = q.query(ledger_path=str(ledger), story_key="CFP-2817")
        r99 = q.query(ledger_path=str(ledger), story_key="CFP-2999")
        assert len(r17) == 1 and r17[0]["story_key"] == "CFP-2817", "CFP-2817 오귀속"
        assert len(r99) == 1 and r99[0]["story_key"] == "CFP-2999", "CFP-2999 오귀속"
        assert r17[0]["event_id"] != r99[0]["event_id"], "cross-story event_id 충돌(story_key 미산입)"


# ══════════════════════════════════════════════════════════════════════════════
# § CFP-2817 §8.8 concurrency — Port-A hook ∥ Port-B agent 2-writer O_APPEND (§6.3 edge#7 / R5)
#   oracle: 성공 append event_id 전량 read-back 생존(선행 완료행 clobber 0) ∧ torn 개별 skippable.
#   정직 천장: small-row bounded·platform-observational(Windows dev-host)·primitive 무변경.
# ══════════════════════════════════════════════════════════════════════════════
class TestConcurrentTwoWriterAppend:
    @staticmethod
    def _w_hook(ledger, n, out):
        for i in range(n):
            eid = ade.append_event(ledger_path=str(ledger), event_type="tool_call",
                                   emit_source="hook", story_key="CFP-2817", lane_label="구현",
                                   consumer_scope="wrapper", seq="hook-%d" % i)
            if eid:
                out.append(eid)

    @staticmethod
    def _w_agent(ledger, n, out):
        for i in range(n):
            eid = ade.append_event(ledger_path=str(ledger), event_type="lane_transition",
                                   emit_source="agent", story_key="CFP-2817", lane_label="구현",
                                   consumer_scope="wrapper", seq="agent-%d" % i)
            if eid:
                out.append(eid)

    def _run(self, ledger, n=500):
        rh, ra = [], []
        th = threading.Thread(target=self._w_hook, args=(ledger, n, rh))
        ta = threading.Thread(target=self._w_agent, args=(ledger, n, ra))
        th.start(); ta.start(); th.join(); ta.join()
        text = ledger.read_text(encoding="utf-8")
        nonblank = [ln for ln in text.splitlines() if ln.strip()]
        res = q.query_lines(text.splitlines())
        return set(rh) | set(ra), res, len(nonblank)

    def test_two_writer_reader_skip_tolerant_and_survivors_valid(self, tmp_path):
        """§8.8 honest 불변식(satisfiable): 2-writer 후에도 reader(query_lines) 무크래시 ∧
        생존행 전부 well-formed(손상 survivor 0) ∧ 물리 nonblank == valid + malformed
        (torn/merged 행이 개별 skippable — 전체 원장 손상 아님, malformed 로 격리)."""
        exp, res, nonblank = self._run(tmp_path / "dev-process-event.jsonl")
        # reader 는 mangled ledger 에도 crash 없이 raw rows 반환
        for r in res["rows"]:
            assert isinstance(r, dict) and len(r.get("event_id", "")) == 64, "손상 survivor row"
            assert r["emit_source"] in ("hook", "agent"), "survivor emit_source 손상"
            assert r["event_type"] in ("tool_call", "lane_transition"), "survivor event_type 손상"
        # 물리 nonblank 라인 = valid(rows_total) + malformed_skipped (phantom/은폐 라인 0 = skip-tolerant)
        assert nonblank == res["stats"]["rows_total"] + res["stats"]["malformed_skipped"], \
            "nonblank(%d) != valid(%d)+malformed(%d) — reader 회계 불일치" % (
                nonblank, res["stats"]["rows_total"], res["stats"]["malformed_skipped"])

    def test_two_writer_completed_row_clobber_zero(self, tmp_path):
        """§8.8 oracle: 선행 완료행 바이트 clobber 0 (성공 append event_id 전량 생존).

        CFP-2817 FIX Iter 3: 공유 primitive append_spawn_event._append_jsonl_row 이 cross-platform
        kernel-atomic append(Windows FILE_APPEND_DATA / POSIX O_APPEND, ADR-155 Amendment 1)로 완료행
        clobber 를 봉인 → iter1 xfail(R5 '무보장 천장') 철회, cross-platform 실 GREEN. discriminating
        negative-control = test_dev_process_concurrency.TestClobberOracleDiscriminating."""
        exp, res, _ = self._run(tmp_path / "dev-process-event.jsonl")
        got = {r["event_id"] for r in res["rows"]}
        missing = exp - got
        assert not missing, "완료행 clobber %d건 (§6.1 R5 Windows O_APPEND 비원자 — 실측 유실)" % len(missing)
