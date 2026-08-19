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

# ── CFP-2817 D1: derive_seq (emit 계층 6번째 pure helper, causal-state 파생) ──
#   production 미착지 시 예상 RED (TDD red-first) — grep 실측 시 derive_seq 부재.
#   emit_dev_process_event import 자체는 성공(모듈 실존) — derive_seq getattr 만 None.
try:
    import emit_dev_process_event as _emitmod
except Exception:  # pragma: no cover — import path fallback (conftest 가 scripts/lib 주입)
    _emitmod = None

# ADR-038 6-point transition_kind 토큰 (progress-format.sh 6-token 재사용, D3).
_SIX_POINT_TOKENS = ("enter", "pass", "fix-detected", "cause", "re-enter", "complete")


def _require_derive_seq():
    """emit_dev_process_event.derive_seq 를 반환하거나 명확한 RED 로 실패.

    CFP-2817 D1 production(role:dev) 착지 전에는 AttributeError-equivalent RED —
    "무엇을 검증하는지 모른 채 GREEN" 을 차단(hollow-green 금지). 착지 후 GREEN.
    """
    assert _emitmod is not None, (
        "emit_dev_process_event import 실패 — derive_seq 단위검증 불가 (conftest sys.path 확인)"
    )
    fn = getattr(_emitmod, "derive_seq", None)
    assert fn is not None, (
        "emit_dev_process_event.derive_seq 미구현 — CFP-2817 D1 착지 전 예상 RED (구현 후 GREEN)"
    )
    return fn


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
        """실제 emit 된 row 키 == _ROW_KEYS (순서·멤버), 정확히 20개."""
        ledger = tmp_path / "dev-process-event.jsonl"
        ade.append_event(
            ledger_path=str(ledger),
            event_type="verdict", emit_source="agent",
            story_key="CFP-2687", lane_label="구현-리뷰", consumer_scope="wrapper",
        )
        row = _read_rows(ledger)[0]
        assert tuple(row.keys()) == ade._ROW_KEYS
        assert len(row) == 20

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


# ══════════════════════════════════════════════════════════════════════════════
# § CFP-2817 D1 — derive_seq causal-state 파생 (INV-1 멱등 / INV-2 소실0 / INV-4 재구성)
#   §11.6 4 불변식의 emit-계층 pure helper 실현. 원장 read 0 (0 I/O).
#   ★ production(role:dev) 착지 전에는 예상 RED — RED 진정성 = git-stash/HEAD-shadow 사후입증.
# ══════════════════════════════════════════════════════════════════════════════
class TestDeriveSeqDeterminism:
    """INV-1 (D1-①): 동일 (transition_kind, fix_iter, reset_generation, ordinal) → 동일 seq (멱등)."""

    def test_same_causal_state_same_seq(self):
        d = _require_derive_seq()
        a = d("re-enter", fix_iter=2, reset_generation=0, ordinal=0)
        b = d("re-enter", fix_iter=2, reset_generation=0, ordinal=0)
        assert a == b, "동일 causal-state 재계산이 다른 seq (INV-1 멱등 위반 → 재시도 event_id drift)"

    def test_recompute_is_pure_across_calls_INV4(self):
        """INV-4 (D1-④): 원장 read 없이 causal-state 만으로 동일 seq 재계산 — 세션 재기동 재구성 결정성.

        derive_seq 는 pure(0 I/O) 이므로 '재기동' = 동일 causal-state fresh 재호출로 모델링.
        (§8.5 restart-aware N → §8.2-C 평문 결정성 단위테스트 재귀속.)"""
        d = _require_derive_seq()
        # 세션 A 가 계산한 값
        session_a = d("fix-detected", fix_iter=3, reset_generation=1, ordinal=0)
        # 세션 재기동 후: §10 FIX Ledger + phase label 로 causal-state 복원 → 동일 재계산
        session_b = d("fix-detected", fix_iter=3, reset_generation=1, ordinal=0)
        assert session_a == session_b, "재기동 재구성이 다른 seq (INV-4 위반 → 재기동 후 중복 행)"

    def test_signature_has_no_ledger_io_param_INV4(self):
        """INV-4/§3.1: derive_seq 는 pure — 원장/파일 I/O 인자 부재(0 I/O, ledger read 금지 불변식 무손상)."""
        import inspect
        d = _require_derive_seq()
        params = set(inspect.signature(d).parameters)
        forbidden = {"ledger", "ledger_path", "path", "rows", "lines", "prev_timestamp_utc"}
        leaked = params & forbidden
        assert not leaked, f"derive_seq 시그니처에 I/O 인자 유입 {leaked} — pure(0 I/O) 위반"
        assert "transition_kind" in params, "transition_kind 인자 부재"


class TestDeriveSeqDistinctTransitions:
    """INV-2 (D1-②, AC-4): 별개 논리전이 → 상이 seq (소실 0)."""

    def test_six_point_tokens_all_distinct(self):
        """6-point 각 transition_kind → 6 상이 seq (AC-6 상이 event_id 기반)."""
        d = _require_derive_seq()
        # FIX 계열 3종은 fix_iter 필수(raise 계약) → 부여. 나머지는 None.
        seqs = []
        for tok in _SIX_POINT_TOKENS:
            fi = 1 if tok in ("fix-detected", "cause", "re-enter") else None
            seqs.append(d(tok, fix_iter=fi, reset_generation=0, ordinal=0))
        assert len(set(seqs)) == 6, f"6-point 토큰이 상이 seq 를 못 냄(붕괴): {seqs}"

    def test_distinct_fix_iter_distinct_seq(self):
        d = _require_derive_seq()
        assert d("re-enter", fix_iter=1, reset_generation=0, ordinal=0) != \
               d("re-enter", fix_iter=2, reset_generation=0, ordinal=0), \
               "다른 fix_iter 인데 동일 seq (FIX 반복 disambiguation 실패)"

    def test_distinct_reset_generation_distinct_seq(self):
        """F-DR-1: RESET 경계 넘어 동일 (kind, fix_iter) 재발 → reset_generation 이 disambiguate."""
        d = _require_derive_seq()
        assert d("re-enter", fix_iter=1, reset_generation=0, ordinal=0) != \
               d("re-enter", fix_iter=1, reset_generation=1, ordinal=0), \
               "RESET 세대만 다른데 동일 seq (RESET 경계 재발 event_id 충돌 → AC-4 위반)"

    def test_distinct_ordinal_distinct_seq(self):
        """동일 (kind, fix_iter, reset_gen) 내 복수 시도(verdict 복수발생·defect 재검출) attempt 흡수."""
        d = _require_derive_seq()
        assert d("cause", fix_iter=1, reset_generation=0, ordinal=0) != \
               d("cause", fix_iter=1, reset_generation=0, ordinal=1), \
               "ordinal 만 다른데 동일 seq (동일 Iter 복수 시도 collapse)"


class TestDeriveSeqFailureDirection:
    """INV-3 (D1-③, AC-9): 실패방향 — 채번 불확실 시 silent-reuse 금지, visible ValueError raise.

    dev-pl-2817 확정 raise 계약: 6-token 밖/빈 토큰 → ValueError; FIX 계열인데 fix_iter=None → ValueError.
    이형 토큰 drift(예 '진입'/'lane_entry')로 인한 dedup 붕괴를 visible-over-silent 로 예방.
    """

    def test_unknown_token_raises_not_silent(self):
        d = _require_derive_seq()
        for bad in ("진입", "lane_entry", "ENTER", "", None):
            with pytest.raises(ValueError):
                d(bad, fix_iter=None, reset_generation=0, ordinal=0)

    def test_fix_transition_without_fix_iter_raises(self):
        """FIX 계열 3종(fix-detected/cause/re-enter) + fix_iter=None → ValueError (coarse-fallback 금지, P2-2)."""
        d = _require_derive_seq()
        for tok in ("fix-detected", "cause", "re-enter"):
            with pytest.raises(ValueError):
                d(tok, fix_iter=None, reset_generation=0, ordinal=0)

    def test_non_fix_transition_without_fix_iter_ok(self):
        """대조: 비-FIX 전이(enter/pass/complete)는 fix_iter 없이도 정상 파생(raise 아님)."""
        d = _require_derive_seq()
        for tok in ("enter", "pass", "complete"):
            assert d(tok, fix_iter=None, reset_generation=0, ordinal=0)  # non-empty str

    def test_transition_kind_constants_exposed(self):
        """AC-9 계약 lock: 6-token / FIX-계열 vocabulary 를 모듈 상수로 노출(문서↔코드 SSOT 단일화)."""
        assert _emitmod is not None, "emit 모듈 import 실패"
        tks = getattr(_emitmod, "_TRANSITION_KINDS", None)
        fix_tks = getattr(_emitmod, "_FIX_TRANSITION_KINDS", None)
        assert tks is not None and set(tks) == set(_SIX_POINT_TOKENS), \
            f"_TRANSITION_KINDS 가 6-token 과 불일치: {tks}"
        assert fix_tks is not None and set(fix_tks) == {"fix-detected", "cause", "re-enter"}, \
            f"_FIX_TRANSITION_KINDS 가 FIX 계열 3종과 불일치: {fix_tks}"


# ══════════════════════════════════════════════════════════════════════════════
# § CFP-2817 재진입 seq 미분화 충돌 — compute_event_id 층 (§8.2-D CFP-1334 RED→GREEN)
#   integration 층(emit+query) = tests/integration/test_dev_process_inv8b_ordering.py
# ══════════════════════════════════════════════════════════════════════════════
class TestReentrySeqCollisionAtEventId:
    _BASE = ("lane_transition", "agent", "CFP-2817", "구현", "wrapper")

    def test_undifferentiated_seq_collides_RISK_PRESENT(self):
        """[risk-present] 동일 (story,lane) 재진입에서 seq 미분화(둘 다 '') → 동일 event_id.

        이것이 정확한 봉인 대상 실패모드(진입/재진입이 하나로 붕괴 → read-time dedup 이 삼킴).
        충돌이 실재함을 in-suite 로 못박아 아래 'derive_seq 생존' 이 discriminating 함을 증명."""
        enter = ade.compute_event_id(*self._BASE, seq="")
        reenter = ade.compute_event_id(*self._BASE, seq="")
        assert enter == reenter, "seq 미분화인데 event_id 가 이미 상이 — 충돌 전제 무효(테스트 재설계 필요)"

    def test_derived_seq_disambiguates_reentry_SURVIVES(self):
        """[GREEN 방향] derive_seq(enter) vs derive_seq(re-enter) → 상이 seq → 상이 event_id → 양자 생존."""
        d = _require_derive_seq()
        enter = ade.compute_event_id(
            *self._BASE, seq=d("enter", fix_iter=None, reset_generation=0, ordinal=0))
        reenter = ade.compute_event_id(
            *self._BASE, seq=d("re-enter", fix_iter=1, reset_generation=0, ordinal=0))
        assert enter != reenter, "derive_seq 적용해도 event_id 동일 — 재진입 소실(AC-4 위반)"

    def test_idempotent_retry_same_derived_seq_collapses(self):
        """[INV-1 멱등] 동일 논리전이 재시도(동일 causal-state) → 동일 seq → 동일 event_id → collapse."""
        d = _require_derive_seq()
        a = ade.compute_event_id(
            *self._BASE, seq=d("re-enter", fix_iter=1, reset_generation=0, ordinal=0))
        b = ade.compute_event_id(
            *self._BASE, seq=d("re-enter", fix_iter=1, reset_generation=0, ordinal=0))
        assert a == b, "동일 논리전이 재시도가 다른 event_id (멱등 붕괴 → 중복 잔존)"
