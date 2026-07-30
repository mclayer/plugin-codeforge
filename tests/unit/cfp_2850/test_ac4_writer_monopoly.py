"""AC-4 — writer monopoly (Orchestrator-owned writer).

Change Plan §8.1.1 RTM AC-4. phase1.
  - writer ownership = Orchestrator(-owned delegate) (ADR-039 §결정3).
  - write 지점 = Orchestrator task-notification 수신 시점 single-write (Amendment 4).
  - lane/plugin 직접 append = 요구 충족 아님 (policy_violation).

★F-CR-006 (구현리뷰 FIX Iter2) — 서술 grep → **계약 YAML 블록 구조 파싱** 전환:
  구 test 는 문서 아무 곳의 "Orchestrator"/"policy_violation" 문자열 존재만 봤기에
  `append_rules.writer` 블록이 삭제·이동·재구성돼도(계약 문면 변경) 통과하는
  non-discriminating 상태였다. 본 파일은 §3 fenced YAML 을 실제로 파싱해
  `append_rules.writer` **위치·자료형·명제**를 구조적으로 assert 한다 —
  writer 규범이 사라지면 KeyError/assert 로 RED.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACT = REPO_ROOT / "docs" / "inter-plugin-contracts" / "spawn-event-v1.md"


def _load_contract_yaml_block():
    """계약 §3 의 fenced ```yaml 블록(= append_rules 를 담은 블록)을 파싱해 dict 반환.

    문면 grep 이 아니라 구조 파싱 — 블록 부재/파싱 불가/append_rules 소실은 전부 RED.
    """
    text = CONTRACT.read_text(encoding="utf-8")
    blocks = re.findall(r"```yaml\n(.*?)\n```", text, re.S)
    candidates = [b for b in blocks if "append_rules:" in b]
    assert candidates, (
        "계약 §3 에 append_rules 를 담은 ```yaml 블록이 없음 — writer 규범이 구조적으로 소실"
    )
    # ★F-CX2-002 하드닝: append_rules 블록은 **유일**해야 한다. 동명 블록이 2개 이상이면
    # `candidates[0]` 이 어느 블록인지 문서 순서에 좌우돼(엉뚱한 블록 파싱) 아래 구조
    # assert 가 실제 규범이 아닌 사본을 검증할 수 있다 — 계약 SSOT 이중화 자체를 차단한다.
    assert len(candidates) == 1, (
        "계약에 append_rules 를 담은 ```yaml 블록이 %d개 — SSOT 이중화(파싱이 엉뚱한 블록을 "
        "집을 수 있음). 계약 블록은 유일해야 함" % len(candidates)
    )
    data = yaml.safe_load(candidates[0])
    assert isinstance(data, dict), f"§3 YAML 블록이 mapping 이 아님: {type(data)}"
    return data


@pytest.fixture(scope="module")
def contract_yaml():
    return _load_contract_yaml_block()


def test_ac4_append_rules_writer_block_structure(contract_yaml):
    """append_rules.writer 가 **append_rules 하위의 non-empty list** 로 존재 (구조 pin).

    mutation: writer 를 top-level 로 이동 / 삭제 / 문자열로 축약하면 RED.
    """
    # 측정 assertion (a): 같은 블록에 schema + append_rules 공존 (§3 항목 블록임을 확인)
    assert "spawn_event_schema" in contract_yaml, "§3 블록에 spawn_event_schema 부재 (오파싱)"
    assert "append_rules" in contract_yaml, "append_rules 블록 소실 (writer 규범 carrier 부재)"
    append_rules = contract_yaml["append_rules"]
    assert isinstance(append_rules, dict), f"append_rules 는 mapping 이어야 함, got {type(append_rules)}"
    # (b): writer 는 append_rules 하위 (top-level 승격 = 구조 drift)
    assert "writer" in append_rules, "append_rules.writer 규범 부재"
    assert "writer" not in contract_yaml, "writer 는 append_rules 하위여야 함 (top-level 이동 금지)"
    writer = append_rules["writer"]
    # (c): writer 는 non-empty 규범 list
    assert isinstance(writer, list) and writer, f"append_rules.writer 는 non-empty list, got {writer!r}"
    assert all(isinstance(e, str) and e.strip() for e in writer), "writer 항목은 비어있지 않은 문자열"


def test_ac4_orchestrator_owned_writer(contract_yaml):
    """(구조) append_rules.writer 안에 Orchestrator ownership 명제 + ADR-039 근거가 존재.

    mutation: ownership 주체를 lane/hook 으로 바꾸거나 근거 ADR 인용을 지우면 RED.
    """
    writer = contract_yaml["append_rules"]["writer"]
    # 측정 assertion (a): ownership 주체 = Orchestrator (근거 ADR-039 동반 entry)
    ownership_entries = [e for e in writer if "Orchestrator" in e and "ADR-039" in e]
    assert ownership_entries, (
        f"writer 규범에 'Orchestrator ownership + ADR-039 근거' 명제 부재, got {writer}"
    )
    # (b): write 지점 = task-notification 수신 시점 single-write (Amendment 4 topology)
    single_write_entries = [
        e for e in writer if "single-write" in e and "task-notification" in e
    ]
    assert single_write_entries, (
        f"writer 규범에 'task-notification 수신 시점 single-write' 명제 부재 (writer topology 소실), "
        f"got {writer}"
    )


def test_ac4_lane_direct_append_not_counted(contract_yaml):
    """(neg, 구조) lane/plugin 직접 append = policy_violation 이 **writer 규범 안에** 명문.

    구 test 는 문서 전역 grep 이라 policy_violation 이 무관 절에만 있어도 통과했다.
    mutation: writer 에서 policy_violation 명제를 빼면(허용/침묵) RED.
    """
    writer = contract_yaml["append_rules"]["writer"]
    violation_entries = [e for e in writer if "policy_violation" in e and "lane" in e]
    # 측정 assertion: lane 직접 write 배제 명제가 writer 규범 안에 존재
    assert violation_entries, (
        f"append_rules.writer 안에 'lane 직접 write = policy_violation' 명제 부재 "
        f"(writer monopoly 무력화), got {writer}"
    )


def test_ac4_opt_in_default_false_norm_in_append_rules(contract_yaml):
    """(구조) opt-in default-false 규범이 append_rules 하위에 존속 (silent always-on 금지).

    AC-3 counter gate 의 계약 근거 — 이 규범이 계약에서 사라지면 opt-in gate 요구가
    문서상 무근거가 된다. mutation: opt_in_default_false 블록 삭제/true 전환 시 RED.
    """
    append_rules = contract_yaml["append_rules"]
    assert "opt_in_default_false" in append_rules, "opt-in default-false 규범 블록 소실"
    opt_in = append_rules["opt_in_default_false"]
    assert isinstance(opt_in, dict), f"opt_in_default_false 는 mapping, got {type(opt_in)}"
    rule = str(opt_in.get("rule", ""))
    # 측정 assertion (a): 두 flag AND 의 default false 규범
    assert "false" in rule and "telemetry.enabled" in rule and "spawn_event" in rule, (
        f"opt-in default-false 규범 문면(telemetry.enabled + channels.spawn_event false)이 아님: {rule!r}"
    )
    # (b): silent always-on 금지 명제
    assert "금지" in str(opt_in.get("silent_always_on", "")), (
        f"silent always-on 금지 명제 부재, got {opt_in.get('silent_always_on')!r}"
    )
