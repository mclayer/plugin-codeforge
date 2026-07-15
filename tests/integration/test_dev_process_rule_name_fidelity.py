"""test_dev_process_rule_name_fidelity.py — emit→append rule-name FIDELITY 영구 회귀 가드.

CFP-2687 Phase 2 (구현) / Epic #2686 Story A. T-DPE-8 / AC-14 (audit rule-name fidelity).
Under test (round-trip): emit_dev_process_event.emit
    → dev_process_blob_store.capture_blob → redact_dev_process_content.redact (audit 산출)
    → append_dev_process_event.append_event (_norm_redaction_rules 정규화 → index row).

배경 (drift 회귀 원천 — 이 suite 가 봉인하는 결함):
  append_dev_process_event 의 redaction_rules_fired enum 이 과거 하이픈 축약형
  (credential/gh-pat/…)으로 하드코딩되어 producer(redact_dev_process_content.RULE_NAMES,
  snake_case)와 drift → _norm_redaction_rules 가 non-email 규칙명을 전량 silent drop
  (redaction_rules_fired 가 [] 또는 email-only 로 붕괴)했다. 이제 append 는 producer
  RULE_NAMES 를 single-source import 한다. 본 suite 는 그 정합을 **단일 unit assertion 이
  아닌 emit→append round-trip end-to-end** 로 영구 봉인한다.

불변식 (RED→GREEN discriminating — hollow-green 금지, CFP-2635 선례):
  · end-to-end fidelity (AC-14): content 가 ≥2 non-email 규칙을 trigger 하면 index row 의
    redaction_rules_fired 는 그 실제 규칙명을 보존한다 — [] 아님, collapse 아님.
  · enum single-SSOT: append._REDACTION_RULES == redact.RULE_NAMES (미래 drift fail-loud).
  · discriminating: 정규화를 OLD drift(non-email drop)로 monkeypatch → fidelity RED,
    복원 → GREEN. drift 는 round-trip 전체를 통과해 실 붕괴를 재현한다 (in-suite 증명).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import append_dev_process_event as ade
import dev_process_blob_store as bs
import redact_dev_process_content as rd

try:
    import emit_dev_process_event as emitmod
except Exception:  # pragma: no cover — import path fallback
    emitmod = None

_EMIT_REQUIRED = pytest.mark.skipif(
    emitmod is None,
    reason="emit_dev_process_event(Port B) 미착지 — round-trip fidelity 는 emit 소유",
)

# ≥2 non-email 규칙을 trigger: 절대/home 경로 + Authorization 헤더 + token(api_key).
# firsthand redact() 관측: abs_or_home_path / authorization_header / api_key_credential 방출.
_MULTI_RULE_CONTENT = (
    "opened /home/mccho/.ssh/id_rsa\n"
    "Authorization: Bearer abcdef0123456789ABCDEF\n"
    "token=ZYXWVUTSRQPONMLK9876"
)
# 위 content 가 실제로 방출하는 non-email 규칙명 (redact() 관측 기반 — 전부 non-email).
_EXPECTED_NON_EMAIL_RULES = frozenset(
    {"abs_or_home_path", "authorization_header", "api_key_credential"}
)


def _read_rows(ledger: Path):
    if not ledger.exists():
        return []
    return [
        json.loads(ln)
        for ln in ledger.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]


def _emit_and_row(tmp_dir: Path, content: str = _MULTI_RULE_CONTENT):
    """emit→append round-trip 1회 실행 후 (event_id, 마지막 index row) 반환."""
    ledger = tmp_dir / "dev-process-event.jsonl"
    store = tmp_dir / "store"
    eid = emitmod.emit_lane_transition(
        "CFP-2687", "구현", content=content, consumer_scope="wrapper",
        ledger_path=str(ledger), blob_root=str(store),
    )
    rows = _read_rows(ledger)
    return eid, (rows[-1] if rows else None)


def _assert_rule_name_fidelity(row):
    """AC-14 fidelity 핵심 assertion 묶음 — drift row 에서 RED, 정합 row 에서 GREEN.

    TestFidelityIsDiscriminating 이 이 함수로 discrimination 을 in-suite 증명한다
    (동일 assertion 이 drift 에서 실제로 실패함을 pytest.raises 로 관측)."""
    fired = row["redaction_rules_fired"]
    # (1) [] 로 붕괴하지 않는다
    assert fired, "redaction_rules_fired 가 [] 로 붕괴 (non-email 규칙명 collapse — AC-14 위반)"
    # (2) 실제 non-email 규칙명 보존
    assert _EXPECTED_NON_EMAIL_RULES <= set(fired), (
        f"non-email 규칙명 미보존 (fidelity 위반): "
        f"missing={sorted(_EXPECTED_NON_EMAIL_RULES - set(fired))} got={fired}"
    )
    # (3) 모든 방출 이름이 closed enum(redact.RULE_NAMES) 소속
    assert set(fired) <= set(rd.RULE_NAMES), (
        f"closed enum 밖 규칙명 유입: {sorted(set(fired) - set(rd.RULE_NAMES))}"
    )
    # (4) audit flag/count 정합
    assert row["redaction_applied"] is True, "redaction_applied False (secret 있는데 미기록)"
    assert row["redaction_count"] >= 2, f"redaction_count < 2: {row['redaction_count']}"


# ══════════════════════════════════════════════════════════════════════════════
# § (1) end-to-end fidelity (T-DPE-8 / AC-14) — CORE
# ══════════════════════════════════════════════════════════════════════════════
@_EMIT_REQUIRED
class TestEmitAppendRuleNameFidelity:
    def test_non_email_rule_names_survive_round_trip(self, tmp_path):
        """content 가 ≥2 non-email 규칙 trigger → index row 가 실제 규칙명 보존 (AC-14).

        [] 아님, collapse 아님, closed enum, applied True, count>=2."""
        eid, row = _emit_and_row(tmp_path)
        assert eid is not None and len(eid) == 64, f"event_id 부적합: {eid!r}"
        assert row is not None, "index row 미기록 (activation/emit 실패)"
        _assert_rule_name_fidelity(row)
        # task 지정 대표 2개 이름을 명시적으로 재확인
        assert "abs_or_home_path" in row["redaction_rules_fired"]
        assert "authorization_header" in row["redaction_rules_fired"]

    def test_fidelity_preserved_without_leaking_secret_values(self, tmp_path):
        """규칙 이름은 보존되되 raw secret/경로 값은 index row·blob 에 유입 안 됨 (T-DPE-8 duality).

        fidelity(이름 보존)와 content-blind(값 미유입)가 동시에 성립함을 봉인."""
        _, row = _emit_and_row(tmp_path)
        # 이름은 살아있고
        assert _EXPECTED_NON_EMAIL_RULES <= set(row["redaction_rules_fired"])
        # 값은 index row 어디에도 없음
        rowjson = json.dumps(row, ensure_ascii=False)
        assert "/home/mccho" not in rowjson
        assert "abcdef0123456789ABCDEF" not in rowjson
        assert "ZYXWVUTSRQPONMLK9876" not in rowjson
        # blob 도 redacted (raw secret 부재 — redaction 선행)
        blob_ref = row["blob_ref"]
        assert blob_ref is not None and len(blob_ref) == 64, f"blob_ref 부적합: {blob_ref!r}"
        blob = bs.deref_blob(blob_ref, root=str(tmp_path / "store"))
        assert blob is not None, "blob deref 실패 (INV-8b blob-before-index 위반)"
        assert b"abcdef0123456789ABCDEF" not in blob, "blob 에 raw secret 잔존 (redaction 미선행)"
        assert b"/home/mccho" not in blob


# ══════════════════════════════════════════════════════════════════════════════
# § (2) enum single-SSOT guard — append._REDACTION_RULES == redact.RULE_NAMES
# ══════════════════════════════════════════════════════════════════════════════
class TestAppendEnumSingleSSOT:
    def test_append_redaction_rules_single_source_of_truth(self):
        """append 의 accepted rule-name set == producer redact.RULE_NAMES (미래 drift fail-loud)."""
        assert set(ade._REDACTION_RULES) == set(rd.RULE_NAMES), (
            "append._REDACTION_RULES != redact.RULE_NAMES — audit enum drift\n"
            f"  append_only={sorted(set(ade._REDACTION_RULES) - set(rd.RULE_NAMES))}\n"
            f"  redact_only={sorted(set(rd.RULE_NAMES) - set(ade._REDACTION_RULES))}"
        )

    def test_every_producer_rule_name_accepted_by_append_norm(self):
        """producer 가 방출 가능한 모든 규칙명이 append 정규화에서 살아남는다 (drop 0).

        _norm_redaction_rules 가 정렬 보존 그대로 통과시켜, closed enum 축소 없음을 확인."""
        all_names = sorted(rd.RULE_NAMES)
        assert ade._norm_redaction_rules(all_names) == all_names

    def test_norm_still_drops_unregistered_name(self):
        """[대조] 미등재 규칙명은 여전히 drop (allow-list-clean 유지 — SSOT 정합이 게이트를 약화하지 않음)."""
        out = ade._norm_redaction_rules(["abs_or_home_path", "NOT-A-REAL-RULE", "email"])
        assert out == ["abs_or_home_path", "email"]
        assert "NOT-A-REAL-RULE" not in out


# ══════════════════════════════════════════════════════════════════════════════
# § (3) RED→GREEN discriminating proof — fidelity 검사가 drift 에 민감함을 in-suite 증명
# ══════════════════════════════════════════════════════════════════════════════
def _drift_drop_non_email(raw):
    """OLD append drift 재현 — non-email 규칙명을 전량 silent drop.

    과거 하이픈 축약형(credential/gh-pat/…) mismatch 로 'email' 만 우연히 살아남고
    나머지 snake_case producer 이름이 전부 정규화에서 탈락하던 증상을 재현."""
    if not raw:
        return []
    if isinstance(raw, str):
        raw = [raw]
    return [i.strip() for i in raw if isinstance(i, str) and i.strip() == "email"]


@_EMIT_REQUIRED
class TestFidelityIsDiscriminating:
    def test_red_under_simulated_drift_green_after_restore(self, tmp_path, monkeypatch):
        """fidelity 검사가 discriminating 함을 in-suite 증명 (hollow-green 금지).

        정규화를 OLD drift(non-email drop)로 monkeypatch → 동일 fidelity assertion 이
        drift round-trip row 에서 RED(AssertionError), 복원 후 GREEN. drift 는 emit→append
        round-trip 전체를 통과하므로 unit-level 이 아닌 실 붕괴를 재현한다."""
        # ── GREEN baseline (fixed single-SSOT): fidelity 성립 ──
        _, row_ok = _emit_and_row(tmp_path / "green_pre")
        _assert_rule_name_fidelity(row_ok)  # 통과

        # ── RED: OLD drift 재현 → non-email 규칙명 붕괴 ──
        monkeypatch.setattr(ade, "_norm_redaction_rules", _drift_drop_non_email)
        _, row_drift = _emit_and_row(tmp_path / "red_drift")
        # round-trip 이 실제로 붕괴 (content 에 email 없음 → non-email 전량 drop → [])
        assert row_drift["redaction_rules_fired"] == [], (
            f"drift 인데 규칙명이 붕괴하지 않음(non-discriminating): "
            f"{row_drift['redaction_rules_fired']}"
        )
        assert "abs_or_home_path" not in row_drift["redaction_rules_fired"]
        assert "authorization_header" not in row_drift["redaction_rules_fired"]
        # ★동일 fidelity assertion 이 drift row 에서 실제로 RED → 검사의 discrimination 봉인
        with pytest.raises(AssertionError):
            _assert_rule_name_fidelity(row_drift)

        # ── GREEN restored: 복원 후 fidelity 재성립 ──
        monkeypatch.undo()
        _, row_restored = _emit_and_row(tmp_path / "green_post")
        _assert_rule_name_fidelity(row_restored)  # 다시 통과
