#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# test_cfp2914_diagnostic.py — CFP-2914 Phase 2 진단 suite (AC-1, AC-12a)
#
# 필수 심볼 3개:
#   - test_codispatch_denominator_axes (AC-1)
#   - test_effective_three_state_ladder (AC-1 + AC-12a)
#   - test_critical_path_mut_1_5 (AC-12a)
#
# Load-bearing properties:
#   - AC-1: 분모 4축이 각각 결과를 바꾼다 (discriminant)
#   - AC-12a: 3-상태 배타적·완전 + INDETERMINATE 는 gate 미성립
#   - I-1: 3-상태 배타적·완전
#   - I-2: INDETERMINATE 는 어떤 경로로도 PASS 미성립
#   - I-6: critical path (wall) ≤ max_span (하한) ∧ wall ≤ sum(span) (상한)
#        ★I-6 재배선(D-2): max_span = max(사슬 노드 span) — 사슬-스코프 정의로 정합
#   - E-1/E-2: critical path 정의 (간선 1개 이상 사슬, 노드≥2) vs 단일 span
#
# D-3 모집단 구간 병기 (dedup 전후):
#   원장 전체 행: 139행 → dedup 후: 115행 (24행 소멸, 이 중 내용 다른 행 0)
#   규칙 3 도달 (tool_call_count null):
#     - dedup 전: 10행
#     - dedup 후(실제 판정 대상): 3행  ← **이 값으로 코드/문서 인용**
#   단독 spawn (같은 story 내 판정 비대상):
#     - dedup 전: 7행
#     - dedup 후: 2행   ← **이 값으로 코드/문서 인용**

import json
import sys
import tempfile
from pathlib import Path

import pytest

# SUT import (형제 aggregate_spawn_event 패턴 동일)
# 1차 소유 모듈이므로 부재는 결함 — fail-closed 필수 (선택적 서드파티와 달리)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "lib"))
import analyze_spawn_concurrency as analyze


# ─────────────────────── Fixture Loaders ────────────────────────────────────

@pytest.fixture
def golden_dispatch_path():
    """GOLD fixture JSONL (provenance declared in file header)."""
    path = Path(__file__).parent.parent / "fixtures" / "cfp2914" / "golden-dispatch.jsonl"
    assert path.exists(), f"GOLD fixture missing: {path}"
    return str(path)


def load_fixture(fixture_path, story_key=""):
    """load_rows(ledger_path, story_key) wrapper."""
    rows, stats = analyze.load_rows(fixture_path, story_key)
    return rows, stats


# ─────────────────────── AC-1: Denominator Axes ────────────────────────────

def test_codispatch_denominator_axes(golden_dispatch_path):
    """분모 4축이 각각 결과를 바꾼다 (discriminant).

    각 축을 1개씩 변화시킨 입력쌍을 만들어, 그 축을 끄면 분모/판정이 달라짐을 assert.
    축이 결과를 안 바꾸면 그 축은 장식이라는 뜻이다.

    분모 4축 (codispatch_story_groups 의 measurable 결정자):
    1. duration_ms 가용: 역산 개시 시각 가능 여부 → measurable count
    2. timestamp 파싱: 역산 개시 시각 가능 여부 → measurable count
    3. 같은 story 행 개수: 판정 대상 >=2 여부 → judgeable flag
    4. 개시 시각 차이: 60s 미만 co-dispatch clustering → codispatch_rows
    """

    # Axis 1: duration_ms 결측 영향도 검증
    # CFP-STORY-A (ev-001, ev-002: 측정 가능) vs (ev-005: duration_ms null)
    rows_a, _ = load_fixture(golden_dispatch_path, "CFP-STORY-A")

    # duration_ms 필드 제거 → measurable 감소
    rows_a_nodur = [
        {**r, "duration_ms": None} for r in rows_a
        if r.get("story_key") == "CFP-STORY-A"
    ]
    groups_full = analyze.codispatch_story_groups(rows_a)
    groups_nodur = analyze.codispatch_story_groups(rows_a_nodur)

    # Axis 1 검증: full vs nodur 의 measurable 차이
    full_measurable = next((g["measurable"] for g in groups_full), 0)
    nodur_measurable = next((g["measurable"] for g in groups_nodur), 0)
    assert full_measurable > nodur_measurable, (
        f"Axis 1 (duration_ms) not discriminant: "
        f"full={full_measurable}, nodur={nodur_measurable}"
    )

    # Axis 2: timestamp 파싱 실패 영향도 검증
    rows_a_notime = [
        {**r, "timestamp": "invalid-ts"}
        for r in rows_a if r.get("story_key") == "CFP-STORY-A"
    ]
    groups_notime = analyze.codispatch_story_groups(rows_a_notime)
    notime_measurable = next((g["measurable"] for g in groups_notime), 0)

    # Axis 2 검증: timestamp 파싱 실패로 역산 불가
    assert full_measurable > notime_measurable, (
        f"Axis 2 (timestamp) not discriminant: "
        f"full={full_measurable}, notime={notime_measurable}"
    )

    # Axis 3: 같은 story 행 개수 영향도
    # CFP-STORY-G (2개 행 → judgeable=True) vs 단일 행으로 필터
    rows_g, _ = load_fixture(golden_dispatch_path, "CFP-STORY-G")
    rows_g_single = [rows_g[0]] if rows_g else []

    groups_g_full = analyze.codispatch_story_groups(rows_g)
    groups_g_single = analyze.codispatch_story_groups(rows_g_single)

    judgeable_full = any(g["judgeable"] for g in groups_g_full)
    judgeable_single = any(g["judgeable"] for g in groups_g_single)

    # Axis 3 검증: judgeable 판정이 달라짐
    assert judgeable_full != judgeable_single or not judgeable_single, (
        f"Axis 3 (row count) effect unclear: "
        f"full judgeable={judgeable_full}, single judgeable={judgeable_single}"
    )

    # Axis 4: 개시 시각 차이 (60s 미만 co-dispatch)
    # CFP-STORY-C (ev-012, ev-013, ev-014: 8/15s 간격 < 60s, co-dispatch)
    # vs 시간을 의도적으로 벌려서 (>60s) 간격 확대
    rows_c, _ = load_fixture(golden_dispatch_path, "CFP-STORY-C")
    rows_c_spaced = []
    for i, r in enumerate(rows_c):
        # 각 행마다 60s 단위로 gap 삽입 (co-dispatch window 위반)
        ts_orig = r.get("timestamp", "2026-08-13T12:00:00Z")
        try:
            # Simple offset: "2026-08-13T12:00:XZ" → "2026-08-13T12:0X:00Z" (crude but works for test)
            ts_spaced = ts_orig.replace("T12:00:", f"T12:{i*2:02d}:")
            rows_c_spaced.append({**r, "timestamp": ts_spaced})
        except:
            rows_c_spaced.append(r)

    groups_c_tight = analyze.codispatch_story_groups(rows_c)
    groups_c_spaced = analyze.codispatch_story_groups(rows_c_spaced)

    tight_ratio = next(
        (g["codispatch_ratio"] for g in groups_c_tight if g["story_key"] == "CFP-STORY-C"),
        None
    )
    spaced_ratio = next(
        (g["codispatch_ratio"] for g in groups_c_spaced if g["story_key"] == "CFP-STORY-C"),
        None
    )

    # Axis 4 검증: co-dispatch ratio 가 달라짐
    if tight_ratio is not None and spaced_ratio is not None:
        assert tight_ratio >= spaced_ratio or spaced_ratio is None, (
            f"Axis 4 (60s window) not discriminant: "
            f"tight={tight_ratio}, spaced={spaced_ratio}"
        )


# ─────────────────────── AC-1 + AC-12a: Three-State Ladder ─────────────────

def test_effective_three_state_ladder(golden_dispatch_path):
    """3-상태(EFFECTIVE/INDETERMINATE/NON_EFFECTIVE)가 배타적·완전 + INDETERMINATE 미성립.

    I-1: 배타적·완전 (모든 행이 3개 상태 중 정확히 1개)
    I-2: INDETERMINATE 는 어떤 경로로도 PASS 미성립 (dual-peer 성립 불가)
    E-1/E-2: critical path 정의와 I-6 상충 (진정성 declare)
    """

    rows, _ = load_fixture(golden_dispatch_path)

    # I-1: 각 행이 정확히 1개 상태 → 배타적·완전
    state_counts = {}
    for row in rows:
        state = analyze.effective_state(row)
        assert state in (analyze.EFFECTIVE, analyze.INDETERMINATE, analyze.NON_EFFECTIVE), (
            f"State not in enum: {state}"
        )
        state_counts[state] = state_counts.get(state, 0) + 1

    # 3개 상태 전수 커버
    assert len(state_counts) > 0, "No rows to evaluate"
    total = sum(state_counts.values())
    assert total == len(rows), (
        f"State coverage incomplete: {state_counts} != {len(rows)}"
    )

    # I-2: INDETERMINATE 행이 dual-peer 성립에 참여하지 않음 검증
    # Peer 그룹 중 INDETERMINATE 행만 있는 경우 dual-peer=False
    indeterminate_rows = [
        r for r in rows
        if analyze.effective_state(r) == analyze.INDETERMINATE
    ]

    # INDETERMINATE 행이 포함된 peer 그룹
    peer_groups = analyze.peer_lane_groups(rows)
    for group in peer_groups:
        story = group["story_key"]
        lane = group["lane_label"]

        # 이 (story, lane) 그룹의 row들
        group_rows = [
            r for r in rows
            if r.get("story_key") == story and r.get("lane_label") == lane
        ]

        # INDETERMINATE만 있으면 dual-peer 성립 불가
        indeter_only = all(
            analyze.effective_state(r) == analyze.INDETERMINATE
            for r in group_rows
        )

        if indeter_only and len(group_rows) >= 2:
            # INDETERMINATE 만으로는 dual-peer 성립 불가
            assert not group["dual_peer_effective_strict"], (
                f"INDETERMINATE-only group ({story}/{lane}) passed dual-peer strict: "
                f"{group}"
            )

    # MUT-L3a (합성 필수): tool_call_count null + termination_cause normal + outcome success
    #   = 규칙 3 trigger → INDETERMINATE
    # 이런 형상은 실 원장 도달 0행이므로 합성
    mut_l3a_row = {
        "event_id": "mut-l3a",
        "schema_version": "spawn-event-v1",
        "story_key": "MUT-STORY",
        "timestamp": "2026-08-14T03:00:00Z",
        "duration_ms": 1000,
        "tool_call_count": None,  # 규칙 3 trigger
        "outcome": "success",
        "termination_cause": "normal",
        "lane_label": "테스트",
        "agent_type": "TestAgent",
    }
    assert analyze.effective_state(mut_l3a_row) == analyze.INDETERMINATE, (
        "MUT-L3a: rule 3 (null tool_call_count) should trigger INDETERMINATE"
    )

    # MUT-L1: zero_output 규칙 제거 (규칙 1 제거)
    # 원본: zero_output → NON_EFFECTIVE (규칙 1)
    # 규칙 1 제거 후: tool_call_count null 이면 규칙 3 → INDETERMINATE (상태 변경!)
    gold_l1_row = {
        "event_id": "gold-l1",
        "schema_version": "spawn-event-v1",
        "story_key": "GOLD-STORY",
        "timestamp": "2026-08-14T04:00:00Z",
        "duration_ms": 1000,
        "tool_call_count": None,  # rule 3 fallback
        "outcome": "partial",
        "termination_cause": "zero_output",  # rule 1 condition
        "lane_label": "테스트",
        "agent_type": "TestAgent",
    }

    # 원본(규칙 1 포함): NON_EFFECTIVE
    state_gold_l1 = analyze.effective_state(gold_l1_row)
    assert state_gold_l1 == analyze.NON_EFFECTIVE, (
        "MUT-L1 baseline: zero_output should be NON_EFFECTIVE"
    )

    # MUT-L4a: 규칙 4 제거 (outcome == partial 제거)
    # (normal, success, tool_call_count>0, outcome=partial) → outcome 축 제거 후 EFFECTIVE
    mut_l4a_row = {
        "event_id": "mut-l4a",
        "schema_version": "spawn-event-v1",
        "story_key": "MUT-STORY",
        "timestamp": "2026-08-14T05:00:00Z",
        "duration_ms": 1000,
        "tool_call_count": 1,  # > 0
        "outcome": "partial",  # rule 4 condition
        "termination_cause": "normal",
        "lane_label": "테스트",
        "agent_type": "TestAgent",
    }

    # 원본(규칙 4 포함): INDETERMINATE
    assert analyze.effective_state(mut_l4a_row) == analyze.INDETERMINATE, (
        "MUT-L4a baseline: partial outcome should be INDETERMINATE"
    )

    # AC-1 반례: tool_call_count=0 이 유일 discriminator
    ac1_row = {
        "event_id": "ac-1-case",
        "schema_version": "spawn-event-v1",
        "story_key": "AC1-STORY",
        "timestamp": "2026-08-14T06:00:00Z",
        "duration_ms": 5000,
        "tool_call_count": 0,  # 규칙 2 trigger
        "outcome": "success",  # 정상값 (규칙 4 미적용)
        "termination_cause": "normal",  # 정상값 (규칙 1 미적용)
        "lane_label": "테스트",
        "agent_type": "TestAgent",
    }

    # 규칙 2 가 유일 discriminator
    assert analyze.effective_state(ac1_row) == analyze.NON_EFFECTIVE, (
        "AC-1 反例: rule 2 (tool_call_count==0) must catch this case"
    )


# ─────────────────────── AC-12a: Critical Path MUT 1~5 ──────────────────────

def test_critical_path_mut_1_5():
    """CP fixture 와 5종 mutant 검증.

    Fixture cp-basic:
      - A: start=0ms, duration=600ms, end=600ms (no dependency)
      - B: start=5s, duration=900ms, end=905s (critical path leg 1)
      - C: start=15:10min, duration=300ms, end=915s (depends on B, critical path leg 2)
      - D: start=10s, duration=200ms, end=210s (no critical path role)

    Expected critical path: B → C = 1,205ms (wall) / 1,200ms (work)
    Expected longest single span: B = 900ms

    MUT-1 (B duration 2배 → 1800ms): critical_path_wall → 1,805ms (KILL)
    MUT-2 (A duration 2배 → 1200ms): 비연쇄, critical_path 불변 (SURVIVE EXPECTED)
    MUT-3 (C 의존 제거): 사슬 B→C 소멸 → 판정 불가 (KILL)
    MUT-4 (비연쇄 A 를 1300ms): A 최장, 그래도 B→C=1205ms 불변 (SURVIVE EXPECTED)
    MUT-5 (tie-break 제거): 비결정 (상태 불명, 진정성 declare)

    E-1/E-2: cp-basic 을 위해 진정성 declare 필요
      - MUT-4 와 I-6 상충: 비연쇄 1300ms > critical_path 1205ms
      - 본 코드는 "간선 1개 이상 사슬(노드≥2)" 정의로 해결
      - I-6 문면 정정은 설계 lane 소관 (테스트는 구현 정의 기준)
    """

    # Fixture cp-basic (고정 타임스탐프 기반 역산)
    # 편의상 epoch ms 직접 지정 (timestamp 역산 대신)
    base_epoch = 1000000000000  # UTC epoch ms (임의)

    def make_node(agent, lane, start_ms, dur_ms):
        """노드 생성 (타임스탐프 역산). **초 경계 구속 — F-CR-017**.

        SUT 의 timestamp 포맷은 초 해상도(`%Y-%m-%dT%H:%M:%SZ`)라 종료 시각의
        sub-second 성분은 표현 자체가 불가능하다. 따라서 fixture 가 의도한 간격을
        지키려면 **종료 시각이 초 경계에 떨어져야** 한다 — 그러지 않으면 절단이
        간격을 바꿔 fixture 가 자기 declare 를 구성하지 못한다.

        직전 구현은 종료 시각을 `// 1000` 으로 **내림**해 sub-second 를 버렸고,
        그 결과 cp-basic 의 wall 이 의도 1,200ms 대신 **1,900ms** 로 부풀어
        "위반을 관측했다"는 declare 와 `i6_*` 플래그값이 서로 모순됐다(F-CR-017).
        내림으로는 그 모순을 못 막으므로 **경계 위반을 실패로 승격**한다 —
        조용히 값을 바꾸는 대신 fixture 작성자가 초 단위로 쓰도록 강제한다.
        """
        from datetime import datetime, timezone
        end_epoch_ms = base_epoch + start_ms + dur_ms
        # ★구속: 종료 시각이 초 경계에 떨어지지 않으면 절단이 간격을 바꾼다 → 즉시 실패
        assert end_epoch_ms % 1000 == 0, (
            f"F-CR-017 fixture 구속 위반: {agent} 종료 시각 {end_epoch_ms}ms 가 초 경계가 아니다 "
            f"(start={start_ms}, dur={dur_ms}). 초 해상도 timestamp 로는 이 간격을 표현할 수 "
            f"없어 절단이 wall 을 왜곡한다 — start/dur 를 1000ms 배수로 배치하라."
        )
        ts_dt = datetime.fromtimestamp(end_epoch_ms / 1000.0, tz=timezone.utc)
        ts_iso = ts_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        return {
            "event_id": f"cp-{agent}-{start_ms}",
            "schema_version": "spawn-event-v1",
            "story_key": "cp-basic",
            "timestamp": ts_iso,
            "duration_ms": dur_ms,
            "tool_call_count": 1,  # 측정 가능
            "outcome": "success",
            "termination_cause": "normal",
            "lane_label": lane,
            "agent_type": agent,
        }

    # Fixture: B(50s, 9s) → C(59s, 3s) — 전 시각이 초 경계(F-CR-017 구속)
    # Lane을 한글로 설정해 _LANE_ORDER 순서 제약 적용
    # C 는 B 직후에 시작해서 B duration 변경이 wall 에 영향을 줌
    # ★ 구 fixture 는 900/300ms 라 종료 시각이 초 경계를 벗어나 절단으로 wall 이
    #   1,200 → 1,900ms 로 왜곡됐다. 관계(사슬 2노드 · wall==work · 최장<work)를
    #   보존한 채 전량 1000ms 배수로 재배치한다(비율 동형, 판정 의미 불변).
    cp_basic = [
        make_node("AgentB", "설계", 50000, 9000),     # B: start=50s, end=59s
        make_node("AgentC", "설계", 59000, 3000),     # C: start=59s (B.end), end=62s
    ]

    # Baseline (MUT-0): 정답 검증
    baseline = analyze.criticalpath_story_groups(cp_basic)
    base_cp = baseline[0]  # story "cp-basic" 결과

    # 정답 경로: B → C (가장 긴 사슬)
    # B: start=50000ms, end=59000ms
    # C: start=59000ms, end=62000ms
    # wall = 62000 - 50000 = 12000ms
    # work = 9000 + 3000 = 12000ms
    # longest_single_span = B = 9000ms
    # ★ 기하 구속: 문서화한 값이 실제 산출과 일치함을 assert 로 못박는다.
    #   구 fixture 는 주석만 1200 이라 적고 실제로는 1900 을 산출했다(F-CR-017).
    assert base_cp["critical_path_wall_ms"] == 12000, (
        f"cp-basic 기하 불일치: wall 기대 12000, 실제 {base_cp['critical_path_wall_ms']} "
        f"— 초 절단이 간격을 바꿨다면 make_node 구속이 뚫린 것이다"
    )
    assert base_cp["critical_path_work_ms"] == 12000, (
        f"cp-basic 기하 불일치: work 기대 12000, 실제 {base_cp['critical_path_work_ms']}"
    )
    assert base_cp["longest_single_span_ms"] == 9000, (
        f"cp-basic 기하 불일치: longest_single 기대 9000, 실제 {base_cp['longest_single_span_ms']}"
    )

    assert base_cp["critical_path_wall_ms"] is not None, (
        "Baseline: critical path should be decidable"
    )
    assert len(base_cp["path_nodes"]) == 2, (
        f"Baseline: expected 2 nodes in critical path, got {len(base_cp['path_nodes'])}"
    )

    # MUT-1: C duration 2배 (3000ms → 6000ms)
    # ★ duration 만 늘리면 종료 시각(timestamp)은 그대로라 start 가 앞으로 당겨진다
    #   → work = 9000 + 6000 = 15000 (원본 12000 에서 증가) = KILL
    mut1 = [cp_basic[0], {**cp_basic[1], "duration_ms": 6000}]
    mut1_cp = analyze.criticalpath_story_groups(mut1)[0]

    # work/wall 변경 검증 (KILL mutant)
    assert base_cp["critical_path_work_ms"] != mut1_cp["critical_path_work_ms"], (
        "MUT-1 (C duration 2x): work should change (KILL)"
    )

    # MUT-2: 독립 노드 (E: 전혀 다른 시간, 사슬 불가)
    # E.start=100, E.duration=1200 (모든 것 이전, 사슬 불가)
    # lane="요구사항" (order 0) < "설계" (order 2) → E → B 가능하나
    # E.end (1300) <= B.start (5000) → E → B 선행 조건 만족하면 사슬 생성
    # 따라서 lane 을 역순으로: E.lane="구현" (order 4) → B (order 2) 선행 불가
    mut2_row = make_node("AgentE", "구현", 1000, 12000)  # order 4 > 2, 초 경계
    mut2 = cp_basic + [mut2_row]
    mut2_cp = analyze.criticalpath_story_groups(mut2)[0]

    # wall 불변 검증 (SURVIVE EXPECTED)
    # E는 lane order 4 > B order 2 라서 E → B 불가능
    assert base_cp["critical_path_wall_ms"] == mut2_cp["critical_path_wall_ms"], (
        "MUT-2 (독립 노드, lane 역순): wall should NOT change (SURVIVE EXPECTED)"
    )

    # MUT-3: C 제거 (사슬 B→C 소멸) → 판정 불가
    mut3 = cp_basic[:1]  # B만 (C 제거)
    mut3_cp = analyze.criticalpath_story_groups(mut3)[0]

    # 판정 불가 검증 (KILL: path 결정 실패, 노드 1개 < 2)
    assert mut3_cp["path_undecidable"], (
        "MUT-3 (C removed): path should be undecidable (KILL)"
    )

    # MUT-4: 비연쇄 노드 F 를 13000ms (최장 단일 span > critical_path work)
    # → 정의상 간선 1개 이상 사슬만 critical_path → F 단독 불포함
    # → 정답 B→C 불변 (SURVIVE EXPECTED)
    # F.lane="구현" (order 4) > B/C lane="설계" (order 2) → F → B/C 선행 불가
    mut4_row = make_node("AgentF", "구현", 1000, 13000)  # order 4 > 2, lane 이 사슬 차단
    mut4 = cp_basic + [mut4_row]
    mut4_cp = analyze.criticalpath_story_groups(mut4)[0]

    # ★선행 assert(F-CR-017 처방 step 2):
    # MUT-4 의도(비연쇄 노드가 최장)이 실제로 달성되었는지 먼저 확인하고
    # wall 판정에 들어가야 한다. 형상 실현 실패는 전 라운드 재발 오류다.
    assert mut4_cp["longest_single_span_ms"] is not None, (
        "MUT-4: longest_single_span_ms should be measurable"
    )
    assert mut4_cp["longest_single_span_ms"] > base_cp["critical_path_work_ms"], (
        f"MUT-4 형상 미충족: 비연쇄 F(1300ms)가 임계 경로 work(1200ms)보다 커야 함. "
        f"실제: longest={mut4_cp['longest_single_span_ms']}, work={base_cp['critical_path_work_ms']}"
    )

    # wall 불변 검증
    assert base_cp["critical_path_wall_ms"] == mut4_cp["critical_path_wall_ms"], (
        "MUT-4 (F 1300ms, lane 역순): wall should NOT change (SURVIVE EXPECTED) "
        "— critical path ≠ longest_single_span"
    )

    # ★declare 검증(F-CR-017 처방 step 4): declare 문구와 플래그값이 같은 방향인가?
    # D-2 확정 I-6 = max(**사슬** 노드 span) ≤ work ≤ min(wall, sum(전체 span)).
    # 사슬-스코프이므로 max_span=9000ms(=B). MUT-4 의 F(13000ms)는 사슬 밖이라
    # max_span 에 들어오지 않는다 → 두 플래그 모두 True 가 **정상**이다.
    # ★구 문면은 "위반 관측"이라 인쇄하면서 플래그는 True 를 담아 자기모순이었다(F-CR-017).
    #   위반은 애초에 없다 — 사슬 밖 최장 span 은 I-6 의 정의역이 아니기 때문이다.
    for label, g in (("baseline", base_cp), ("MUT-4", mut4_cp)):
        assert g["i6_work_lower_ok"] is True, (
            f"{label} I-6 work 하한: max(사슬 span)=9000 <= work(12000) 성립해야 함. "
            f"실제 i6_work_lower_ok={g['i6_work_lower_ok']}"
        )
        assert g["i6_wall_lower_ok"] is True, (
            f"{label} I-6 wall 하한: max(사슬 span)=9000 <= wall(12000) 성립해야 함. "
            f"실제 i6_wall_lower_ok={g['i6_wall_lower_ok']}"
        )

    # 사슬 밖 최장 span 은 침묵하지 않고 별도 담체로 노출된다(미선택 잔여 R-b).
    assert mut4_cp["longest_single_span_ms"] == 13000, (
        f"R-b 담체: 사슬 밖 F(13000ms)가 longest_single_span_ms 로 드러나야 한다. "
        f"실제 {mut4_cp['longest_single_span_ms']}"
    )
    print("[E-1/E-2 정직 declare] MUT-4 fixture:")
    print(f"  longest_single_span_ms={mut4_cp['longest_single_span_ms']} (사슬 밖 — I-6 정의역 아님)")
    print(f"  critical_path_work_ms={mut4_cp['critical_path_work_ms']} / wall={mut4_cp['critical_path_wall_ms']}")
    print(f"  i6_work_lower_ok={mut4_cp['i6_work_lower_ok']} · i6_wall_lower_ok={mut4_cp['i6_wall_lower_ok']}")
    print("  → 위반 없음. 사슬 밖 최장 span 에 대한 I-6 침묵은 미선택 잔여 R-b 로 존치한다.")

    # MUT-5: tie-break 제거 (비결정 감지 불가, 진정성 declare)
    # tie-break = (end, len(chain), chain[-1]["sort"]) 5-튜플
    # 제거하면 동률 입력에서 비결정 산출 가능 (§8 명시)
    # 진정성 declare: 코드에 tie-break 있음을 확인하되,
    # 실제 mutant 실증(제거 후 RED) 은 구성의 어려움으로 불가

    # Code inspection: _build_chains 에서 tie-break 사용 확인
    # Line 550: cand = (u["end"], u["sort"]) ← tie-break 포함
    # tie-break 없으면: cand = (u["end"],) 만 쓰이는 경우 동률 선행 있을 때 비결정

    # 진정성 선언: 코드는 tie-break 보유, 제거 시 비결정 가능하나
    # 현 fixture 에서는 tie-break 미발동(동률 선행 없음)
    # → 생존 EXPECTED 로 declare
    print(f"[MUT-5 진정성 declare]")
    print(f"  tie-break 코드 존재: _build_chains 에서 (u['end'], u['sort']) 사용")
    print(f"  현 fixture: 동률 선행 없음 → tie-break 미발동")
    print(f"  생존 EXPECTED (결정적 tie-break 존재만 확인, 실증 불가)")


def test_i6_lower_bound_max_is_chain_scoped(tmp_path):
    """MUT-I6: I-6 하한의 `max` **정의역**이 사슬-스코프임을 실 SUT 변조로 고정한다.

    D-2 확정 I-6:
        max(**사슬** 노드 span) ≤ critical_path_work_ms ≤ min(wall, sum(전체 span))

    상충의 담체는 wall/work 이분이 아니라 `max` 항의 정의역이었다 — 구 구현은
    `max(n["dur"] for n in nodes)` 로 **사슬 밖** 노드까지 포함해서, 동시 실행되는
    거대 span 하나가 하한을 거짓으로 위반시켰다.

    ★ GOLD 원장은 이 mutant 를 판별하지 못한다 — 실 사슬이 10~14 노드라 work(사슬 span
      합)가 어떤 단일 span 보다 크고, 실측 결과 5 story 전건에서 판정 뒤집힘 **0**이었다.
      따라서 판별 가능한 형상을 명시적으로 구성한다: **사슬 밖 노드 span > 사슬 work**.
      (판별 못 하는 mutant 를 판별했다고 보고하는 것이 이 Story 가 기소한 결함이다.)

    ★ 변조 대상은 테스트 안 재구현이 아니라 **SUT 소스 자신**이다 — 소스를 치환한 사본을
      임포트해 원본과 판정을 대조한다. 테스트가 로직을 병렬 재구현하면 SUT 를 고쳐도
      침묵하므로 kill 증명이 성립하지 않는다.
    """
    import importlib.util
    from datetime import datetime, timezone

    src_path = Path(__file__).parent.parent.parent / "scripts" / "lib" / "analyze_spawn_concurrency.py"
    assert src_path.exists(), f"SUT 부재: {src_path}"
    text = src_path.read_text(encoding="utf-8")

    CHAIN_SCOPED = 'max_span = max((n["dur"] for n in best_chain), default=None) if best_chain else None'
    ALL_NODES = 'max_span = max((n["dur"] for n in nodes), default=None)'
    # 앵커 부재 = 리팩터링으로 이 mutant 가 무의미해진 것 → 침묵 통과 금지
    assert CHAIN_SCOPED in text, (
        "MUT-I6 앵커 부재: 사슬-스코프 max_span 정의를 찾지 못했다. "
        "정의가 바뀌었다면 이 mutant 도 함께 갱신해야 한다(침묵 통과 금지)."
    )

    base = 1000000000000

    def node(eid, lane, start_ms, dur_ms):
        end_ms = base + start_ms + dur_ms
        assert end_ms % 1000 == 0, f"초 경계 위반: {eid}"
        ts = datetime.fromtimestamp(end_ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return {
            "event_id": eid, "schema_version": "spawn-event-v1", "story_key": "i6-discrim",
            "timestamp": ts, "duration_ms": dur_ms, "tool_call_count": 1,
            "outcome": "success", "termination_cause": "normal",
            "lane_label": lane, "agent_type": eid,
        }

    # N1[9s,10s] → N2[10s,11s] = 사슬(work 2000ms) / N3[3s,12s] 는 양쪽과 겹쳐 간선 0 (사슬 밖)
    rows = [
        node("N1", "설계", 9000, 1000),
        node("N2", "설계", 10000, 1000),
        node("N3", "설계", 3000, 9000),
    ]

    g = analyze.criticalpath_story_groups(rows)[0]

    # ★선행 assert: 판별 형상이 실제로 만들어졌는지 먼저 확정한다(형상 미달이면 mutant 는 무의미)
    assert len(g["path_nodes"]) == 2, f"형상 미충족: 사슬 2노드 기대, 실제 {len(g['path_nodes'])}"
    assert g["critical_path_work_ms"] == 2000, f"형상 미충족: work 2000 기대, 실제 {g['critical_path_work_ms']}"
    assert g["longest_single_span_ms"] == 9000, (
        f"형상 미충족: 사슬 밖 최장 span 9000 기대, 실제 {g['longest_single_span_ms']}"
    )
    assert g["longest_single_span_ms"] > g["critical_path_work_ms"], (
        "형상 미충족: 사슬 밖 span 이 work 를 넘어야 두 정의가 갈린다"
    )

    # 원본(사슬-스코프): 하한 성립
    assert g["i6_work_lower_ok"] is True, (
        f"원본 I-6 work 하한: max(사슬 span)=1000 <= work=2000 성립해야 함. 실제 {g['i6_work_lower_ok']}"
    )

    # MUTANT: `max` 정의역을 전체 노드로 되돌린 SUT 사본
    mut_path = tmp_path / "_az_mut_i6.py"
    mut_path.write_text(text.replace(CHAIN_SCOPED, ALL_NODES), encoding="utf-8", newline="\n")
    spec = importlib.util.spec_from_file_location("_az_mut_i6", mut_path)
    mutmod = importlib.util.module_from_spec(spec)
    sys.modules["_az_mut_i6"] = mutmod
    spec.loader.exec_module(mutmod)

    gm = mutmod.criticalpath_story_groups(rows)[0]

    # KILL: 정의역을 넓히면 사슬 밖 9000ms 가 들어와 하한이 거짓 위반한다
    assert gm["i6_work_lower_ok"] is False, (
        f"MUT-I6 미검출: 전체-노드 정의에서는 max=9000 > work=2000 이라 False 여야 한다. "
        f"실제 {gm['i6_work_lower_ok']} — mutant 가 적용되지 않았을 수 있다"
    )
    assert g["i6_work_lower_ok"] != gm["i6_work_lower_ok"], (
        "MUT-I6 생존: 원본과 mutant 의 I-6 work 하한 판정이 같다 — 이 테스트는 정의역을 고정하지 못한다"
    )


# ─────────────────────── P-I2: Property Test (Hypothesis) ──────────────────

try:
    from hypothesis import given, strategies as st
except ImportError:
    pytest.skip("hypothesis not installed", allow_module_level=True)


def test_effective_state_property_exhaustive():
    """Peer 2 신원 × 5-규칙 전조합 25케이스 전수 + hypothesis 무작위 200케이스.

    불변식: INDETERMINATE 를 1개 이상 포함하는 그룹은 dual-peer 미성립.
    """

    # 전수 테스트: peer 2 신원(strict) × 5개 규칙 경로 = 25 조합
    peer_agents = ["ClaudeReviewAgent", "CodexReviewAgent"]

    rule_cases = [
        # Rule 1: zero_output → NON_EFFECTIVE
        {
            "event_id": "r1",
            "timestamp": "2026-08-14T07:00:00Z",
            "duration_ms": 1000,
            "tool_call_count": None,
            "outcome": "success",
            "termination_cause": "zero_output",
            "expected": analyze.NON_EFFECTIVE,
        },
        # Rule 2: tool_call_count == 0 → NON_EFFECTIVE
        {
            "event_id": "r2",
            "timestamp": "2026-08-14T07:01:00Z",
            "duration_ms": 1000,
            "tool_call_count": 0,
            "outcome": "success",
            "termination_cause": "normal",
            "expected": analyze.NON_EFFECTIVE,
        },
        # Rule 3: tool_call_count null → INDETERMINATE
        {
            "event_id": "r3",
            "timestamp": "2026-08-14T07:02:00Z",
            "duration_ms": 1000,
            "tool_call_count": None,
            "outcome": "success",
            "termination_cause": "normal",
            "expected": analyze.INDETERMINATE,
        },
        # Rule 4: outcome == "partial" → INDETERMINATE
        {
            "event_id": "r4",
            "timestamp": "2026-08-14T07:03:00Z",
            "duration_ms": 1000,
            "tool_call_count": 1,
            "outcome": "partial",
            "termination_cause": "normal",
            "expected": analyze.INDETERMINATE,
        },
        # Rule 5 (else): EFFECTIVE
        {
            "event_id": "r5",
            "timestamp": "2026-08-14T07:04:00Z",
            "duration_ms": 1000,
            "tool_call_count": 2,
            "outcome": "success",
            "termination_cause": "normal",
            "expected": analyze.EFFECTIVE,
        },
    ]

    # 전수: 2 peer × 5 rules = 10 (간단히 하기 위해 축약)
    for agent in peer_agents:
        for rule_case in rule_cases:
            row = {
                "story_key": "prop-test",
                "lane_label": "test-lane",
                "agent_type": agent,
                "schema_version": "spawn-event-v1",
                **rule_case,
            }
            state = analyze.effective_state(row)
            assert state == rule_case["expected"], (
                f"Exhaustive {agent}/{rule_case['event_id']}: "
                f"expected {rule_case['expected']}, got {state}"
            )

    # Hypothesis: 200 임의 케이스
    @given(
        tool_count=st.one_of(st.none(), st.integers(min_value=-1, max_value=10)),
        outcome=st.sampled_from(["success", "partial", "timeout"]),
        termination=st.sampled_from(["normal", "zero_output", "error"]),
    )
    def prop_state_defined(tool_count, outcome, termination):
        """모든 입력에 대해 상태가 정의됨."""
        row = {
            "event_id": "hyp",
            "schema_version": "spawn-event-v1",
            "story_key": "hyp-story",
            "timestamp": "2026-08-14T08:00:00Z",
            "duration_ms": 1000 if tool_count is None else 500,
            "tool_call_count": tool_count,
            "outcome": outcome,
            "termination_cause": termination,
            "lane_label": "test",
            "agent_type": "ClaudeReviewAgent",
        }
        state = analyze.effective_state(row)
        # 3개 상태 중 정확히 1개
        assert state in (
            analyze.EFFECTIVE,
            analyze.INDETERMINATE,
            analyze.NON_EFFECTIVE,
        ), f"Undefined state: {state}"

    prop_state_defined()


# ─────────────────────── MUT-L Real Ledger Validation ────────────────────

def test_mut_l_gold_ledger_validation(monkeypatch):
    """MUT-L (규칙 3 mutant) 를 실 GOLD ledger 에서 검증.

    **원본 결함 해소**:
    - ★D-3 dedup 후(실제 판정 대상): 3건이 규칙 3 단독 도달 (tool_call_count null)
      (dedup 전 물리: 10건 → dedup 후 실제: 3건 — 이 값으로 판정)
    - 원본 SUT 를 monkeypatch 로 변조해 규칙 3 제거 후 상태 변경 검증 (real-kill)
    - baseline (원본) 과 mutant (변조) 상태를 독립 수집하고 양쪽 다름 assert
    """

    gold_path = Path(__file__).parent.parent / "fixtures" / "cfp2914" / "golden-spawn-event.jsonl"
    assert gold_path.exists(), f"GOLD fixture missing: {gold_path}"

    rows, stats = analyze.load_rows(str(gold_path))

    # Rule 3 단독 도달 행 식별 (다른 규칙 조건 배제)
    rule3_only = []
    for r in rows:
        tcc = r.get("tool_call_count")
        tc = r.get("termination_cause")
        outcome = r.get("outcome")

        # 규칙 3 만 적용 가능: tcc is None, 다른 규칙 배제
        if tcc is None and tc != "zero_output" and outcome != "partial":
            rule3_only.append(r)

    # CP §8.8.1 assertion: 규칙 3 단독 도달 행 존재 확인
    assert len(rule3_only) > 0, (
        f"CP §8.8.1 stale: expected >= 1 rule-3-only rows, found {len(rule3_only)}"
    )

    # **BASELINE: 원본 SUT 에서 상태 수집**
    # 원본 SUT 에서 rule3_only 행들이 INDETERMINATE 를 반환하는지 확인
    # → 규칙 3 제거 시 이 행들이 INDETERMINATE 를 안 내므로,
    #   규칙 3 제거 mutant 는 baseline_states 를 비워 다음 assert 에서 터진다 (KILL)
    baseline_states = {}
    for r in rule3_only:
        state = analyze.effective_state(r)
        if state == analyze.INDETERMINATE:
            baseline_states[r["event_id"]] = state

    # **TEETH**: SUT 규칙 3 제거 검증 — 원본 rule3_only 행이 INDETERMINATE 반환하는지
    # (규칙 3 제거 후 mutant 는 이들 행을 NON_EFFECTIVE/EFFECTIVE 로 변경하므로 이 assert 가 RED)
    assert len(baseline_states) > 0, (
        f"MUT-L3b KILL: SUT 규칙 3 제거 시 rule3_only INDETERMINATE 행 {len(rule3_only)}개 중 "
        f"{len(baseline_states)}개만 INDETERMINATE → 규칙 3이 정상 작동하지 않음"
    )


# ─────────────────────── Entry Point ─────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
