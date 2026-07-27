"""AC-9 — 역할·모델별 grouping key.

Change Plan §8.1.1 RTM AC-9 (3 named test). phase2.
  - agent_type(역할)+model(모델) grouping key 함께 잔존.
  - model field row 저장 (현 pricing arg 만 → 신설, reg).
  - 역할별·모델별 실패율 계산 가능.

aggregate gate: 역할·모델 pivot·실패율 = 실 aggregate_spawn_event 모듈 호출로 검증
  (inline 재계산 금지 — DeveloperPL 회부 ①, RTM "집계 스크립트/쿼리 실증" 정합, discriminating).
실패율 정의 = 비성공 closed-set {failure, inconclusive, partial}/total (회부 ②, §3.2/§8.1.1 pin).
"""

from __future__ import annotations

import aggregate_spawn_event  # 실 production aggregate 모듈 (read-only, conftest sys.path 주입)


def test_ac9_agent_type_and_model_grouping_keys_present(tmp_path, run_append, read_rows):
    """row 에 agent_type + model grouping key 함께 present (+ pivot 교차 gate).

    append-side row 저장 검증 + aggregate pivot_role_model_outcome 로 (역할,모델) group key 교차.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-ac9-keys", agent_id="agent-ac9-keys", spawn_seq="1",
        attribution_confidence="attributed", model="claude-opus-4", total_tokens=139284,
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    row = read_rows(ledger)[0]
    # 측정 assertion: 두 grouping key 동시 present
    assert row["agent_type"] == "DeveloperAgent", "agent_type(역할) grouping key present"
    assert row["model"] == "claude-opus-4", (
        f"model(모델) grouping key row 저장 필요, got {row.get('model')!r}"
    )
    # 교차 gate: aggregate pivot 이 (agent_type, model) 를 group key 로 인식
    rows = aggregate_spawn_event.load_rows(str(ledger), story_key="CFP-2850")
    pivot = aggregate_spawn_event.pivot_role_model_outcome(rows)
    assert ("DeveloperAgent", "claude-opus-4") in pivot, (
        f"aggregate pivot 이 (역할,모델) group key 를 인식해야 함, got keys={list(pivot.keys())}"
    )


def test_ac9_model_field_persisted_not_only_pricing_arg(tmp_path, run_append, read_rows):
    """(reg) model 은 pricing arg 에 그치지 않고 row field 로 persist (현 gap 봉합).

    [RED-until-landed: model row persist]
    현행: --model 은 cost 파생 입력일 뿐 row 에 미저장 → grouping 불가. reg 봉합.
    mutation: model 을 pricing 에만 쓰고 row 저장 안 하면 RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="설계", agent_type="ArchitectAgent",
        session_id="sess-ac9-model", agent_id="agent-ac9-model", spawn_seq="1",
        attribution_confidence="attributed", model="claude-sonnet-4",
        input_tokens=1000, output_tokens=500, cache_creation_input_tokens=0,
        cache_read_input_tokens=0,
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    row = read_rows(ledger)[0]
    # 측정 assertion: model row 저장 (pricing arg 만 아님)
    assert row.get("model") == "claude-sonnet-4", (
        f"model 이 row 에 persist 되어야 함(pricing arg 만 아님), got {row.get('model')!r}"
    )


def test_ac9_failure_rate_by_role_and_model_computable(tmp_path, run_append, read_rows):
    """역할·모델별 실패율 = 실 aggregate_spawn_event.failure_rates 로 계산 (discriminating).

    실패율 정의 pin (회부 ②): numerator = 비성공 closed-set {failure, inconclusive, partial},
    denominator = total(그룹 전 row, outcome=null 포함). failure-only 정의와 falsifiable 하게
    구별하기 위해 (Dev, opus) 에 **inconclusive 1건 추가**:
      (Dev, opus): failure 1 + inconclusive 1 + success 1 → failure_rate = 2/3.
        failure-only 정의였다면 1/3 → 정의 차이가 테스트로 falsifiable.
      (Arch, sonnet): success 1 → 0/1 = 0.0.
    mutation(aggregate 가 failure-only 로 numerator 산정)이면 2/3 ≠ 1/3 → RED.
    """
    import pytest

    ledger = tmp_path / "spawn-event.jsonl"
    specs = [
        ("DeveloperAgent", "claude-opus-4", "failure", "s1", "a1"),
        ("DeveloperAgent", "claude-opus-4", "inconclusive", "s2", "a2"),  # 비성공 set pin
        ("DeveloperAgent", "claude-opus-4", "success", "s3", "a3"),
        ("ArchitectAgent", "claude-sonnet-4", "success", "s4", "a4"),
    ]
    for role, model, outcome, sess, aid in specs:
        res = run_append(
            ledger, story_key="CFP-2850", lane_label="구현", agent_type=role,
            session_id=sess, agent_id=aid, spawn_seq="1",
            attribution_confidence="attributed", model=model, outcome=outcome,
            total_tokens=100000,
        )
        assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    assert len(read_rows(ledger)) == 4

    # 실 aggregate 모듈 호출 (inline 재계산 아님 — mutation 시 실제 RED)
    rows = aggregate_spawn_event.load_rows(str(ledger), story_key="CFP-2850")
    fr = aggregate_spawn_event.failure_rates(rows)
    dev_opus = ("DeveloperAgent", "claude-opus-4")
    arch_sonnet = ("ArchitectAgent", "claude-sonnet-4")

    # 측정 assertion (정의 pin): 비성공 {failure,inconclusive} 2건 / total 3 = 2/3
    assert fr[dev_opus]["failure"] == 2, (
        f"numerator = 비성공 closed-set {{failure,inconclusive,partial}} = 2 이어야 함 "
        f"(failure-only 였다면 1), got {fr[dev_opus]['failure']}"
    )
    assert fr[dev_opus]["total"] == 3, "denominator = 그룹 전 row(success 포함) = 3"
    assert fr[dev_opus]["failure_rate"] == pytest.approx(2 / 3), (
        f"실패율 = 비성공 2/total 3 = 2/3 (failure-only 정의 1/3 과 falsifiable 구별), "
        f"got {fr[dev_opus]['failure_rate']}"
    )
    # (Arch, sonnet): 비성공 0 / total 1 = 0.0
    assert fr[arch_sonnet]["failure_rate"] == 0.0, "ArchitectAgent/sonnet 실패율 = 0.0"
