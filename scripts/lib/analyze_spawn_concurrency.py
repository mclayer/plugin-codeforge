#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# analyze_spawn_concurrency.py — spawn-event-v1 병렬 dispatch **진단**(read-only diagnostic)
#
# Carrier: CFP-2914 Phase 2 (구현) — Change Plan §3.1 / §3.2 / §3.6 / §4.1 / §4.4 / §11.6.A.
#
# 책임 (2 서브커맨드):
#   - codispatch   : Story별 co-dispatch 참고치 + PEER-2/1/0 census + 실효 3-상태 집계.
#                    ★실효 3-상태 사다리(§3.2.1)의 **유일 정본**이다 — 게이트 leg
#                    (check-lane-evidence.sh)에 사본을 두지 않는다(§3.2.1a born-hollow:
#                    Story §14 입력에는 termination_cause·tool_call_count 가 없어 규칙 1~3 이
#                    도달 불가, outcome 은 동음이의라 규칙 4 가 항상 false → 판별력 0).
#   - criticalpath : Story별 지배 span(임계 경로) — agent 단위·lane 단위 귀속.
#
# 정직 라벨 (over-claim 금지 — ADR-119):
#   - 본 스크립트는 **진단 도구이지 게이트가 아니다**. 어떤 판정도 차단·강제하지 않으며
#     "위반" 판정에서도 exit 0 이다 (§3.9 / §4.1).
#   - 개시 시각은 `timestamp − duration_ms` **역산**이다. `timestamp` 는 subagent 의 stop 시각이
#     아니라 원장 **write 시각**(Orchestrator 의 append 호출 시점)이므로, 두 행의 write_lag 이
#     다르면 개시 차가 그 오차만큼 왜곡된다 → **60초 임계에 대해 판별력이 없다**(§2.6).
#     방향·크기 순위의 참고치로만 읽는다.
#   - 임계 경로는 **근사**다 — 원장에 의존 간선이 없다(`parent_event_id` = 관측 전 행 null).
#     시간 포함관계(중첩) + lane 순서로 근사하며 그 사실을 산출 헤더에 명시한다(§3.6.3).
#   - `duration_ms` 는 usage block ∪ wall-clock 두 측정량이 혼재하고 provenance 필드가 없다.
#     본 Story 는 이를 해소하지 않으며 그 사실만 표기한다(§11.6.A #4).
#   - `model` 이 대부분 null 이라 모델 tier/버킷 축은 **산출 불가**다. 추정하지 않는다(#8).
#   - 원장에 FIX iteration 필드가 없다 → 같은 lane 의 서로 다른 FIX 라운드가 한 그룹으로 접힌다.
#     (게이트 leg 의 (lane, iteration) 2축 키잉은 Story §14 입력 축이며 본 파일과 disjoint.)
#
# 불변식:
#   - **I-9 원장 read-only** — 어떤 경로로도 원장에 write 하지 않는다(파일 open 은 읽기 모드만).
#   - 0 API call · local read only. graceful: 원장 부재 → 빈 결과 + exit 0.
#   - 재현성(§11.6.A) — 계산은 **UTC epoch 정수 ms 단일 레이어**. elapsed_seconds(float) 미사용.
#     event_id dedup 수행 + 소멸 건수 병기, duration_ms 결측은 분모 제외 + 별도 카운터 병기.
#
# 재사용 (ADR-140 단일 원본 — 신규 구현 금지):
#   - replay_spawn_event : _resolve_ledger_path / _read_ledger / _dedup_by_event_id / _filter_story
#   - aggregate_spawn_event : _setup_error (exit 2 판정 — 형제 규약 동일 표면)
#
# 사용:
#   python3 analyze_spawn_concurrency.py <codispatch|criticalpath>
#       [--ledger-path <abs>] [--story-key CFP-2914] [--format json|table]
#
# Exit codes:
#   0 = 성공 (빈 결과·원장 부재 포함 — graceful. "위반" 판정도 0)
#   2 = setup error (ledger path 가 디렉터리 등 비정상 — 단 부재는 graceful 0)
#   ※ **1 은 정의하지 않는다** — 재사용 대상 `_read_ledger` 가 부재 시 `[]` 반환 / malformed
#      line 은 `continue` skip 이라 "입력 파싱 실패" 종료 경로가 구조적으로 도달 불가하다.
#      도달 불가 코드를 계약에 적으면 declared-not-bound 를 본 Story 안에서 재생산한다(§4.1).

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Windows cp949 인코딩 회피 (ADR-061 portability — 형제 4종 동일 preamble)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 형제 primitive REUSE (ADR-140 reuse-before-write) — ledger read/dedup/filter/경로결정 및
# setup-error 판정을 복제하지 않는다. import 실패 시 path fallback (aggregate_spawn_event 선례).
try:
    import replay_spawn_event as _replay
    import aggregate_spawn_event as _aggregate
except Exception:  # pragma: no cover — import path fallback
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import replay_spawn_event as _replay
    import aggregate_spawn_event as _aggregate


# ─────────────────────── 상수 ────────────────────────────────────────────────

# record type discriminator (contract §2.1) — spawn-event.jsonl 은 **공유 channel** 이라
# self-context-v1 등 별 record type 이 같은 파일에 섞인다. 집계 대상 = spawn row 만
# (aggregate_spawn_event.load_rows 의 F-CR-002 선례 동형 — 필터 → dedup 순서 동일).
_SPAWN_SCHEMA_VERSION = "spawn-event-v1"

# ★peer 신원 함수 — **채택 = 엄격안**(§3.1.5).
# 근거: `spawn-event-v1.md:74` 가 agent_type 을 roster-derived semi-open enum 으로 규정하고
# 미등재 값의 fallback 을 `unknown-agent` 로 못박는다. `"claude"` 는 roster 실명이 아니므로
# peer 신원으로 승격할 근거가 없다. 다만 이 선택이 결과를 절반으로 가르므로 완화안(loose)
# 수치를 **병기**한다(채택안 명시 + 양 수치 노출).
_PEER_STRICT = frozenset({"ClaudeReviewAgent", "CodexReviewAgent"})
_PEER_LOOSE_EXTRA = frozenset({"claude"})
_PEER_LOOSE = _PEER_STRICT | _PEER_LOOSE_EXTRA

# co-dispatch 조작적 임계 (§3.1.1) — 그룹 내 개시 시각 diff < 60s.
# 기존 기계 구현(check-lane-evidence.sh check_parallelization)의 60s 와 동일 값이다.
_CODISPATCH_WINDOW_MS = 60 * 1000

# lane 순서 — 임계 경로 간선의 **방향 제약**(§3.6.3 "lane 순서")에만 쓴다.
# 미등재 lane(예: "없음"·null)은 None → 순서 제약을 적용하지 않는다(근사가 그만큼 약해지며,
# 그 약화를 산출 헤더에 declare 한다). 8 lane 시퀀스 = CLAUDE.md 핵심 흐름.
_LANE_ORDER = {
    "요구사항": 0,
    "요구사항-리뷰": 1,
    "설계": 2,
    "설계-리뷰": 3,
    "구현": 4,
    "구현-리뷰": 5,
    "구현-테스트": 6,
    "보안-테스트": 7,
}

# ─────────────────────── 실효 3-상태 enum (§3.2.1 · ADR-068 I-1) ─────────────

# ★enum 의미 docstring 의무(ADR-068 I-1 / §4.4) — **값 나열이 아니라 의미**를 기술한다.
# NON_EFFECTIVE = 기록은 있으나 산출이 0 임이 **확정**된 상태.
# INDETERMINATE = 산출 여부를 **알 수 없는** 상태(결측 ≠ 0). **PASS 로 접지 않는다.**
# EFFECTIVE     = 산출이 있었음이 관측된 상태.
#
# caller 분기 매핑(ADR-068 I-2): 그룹 판정은 `EFFECTIVE ≥ 2` 만 dual-peer 성립.
# `INDETERMINATE` 는 위반이 아니라 **별개 상태로 집계**되어 출력된다(위반으로도, PASS 로도
# 접지 않는다). 본 enum 은 *산출을 냈는가*(A 축, 원장 입력)를 묻는다 — 게이트 leg 의
# `SPAWN_TIMING_*` 4-상태(*측정이 가능한가*, B 축, Story §14 입력)와 **disjoint** 하다.
NON_EFFECTIVE = "NON_EFFECTIVE"
INDETERMINATE = "INDETERMINATE"
EFFECTIVE = "EFFECTIVE"

# 신원 단위 상태 병합 우선순위 — 한 신원(agent_type)이 그룹 안에 여러 row 를 가질 때
# "한 번이라도 산출을 낸 신원"은 EFFECTIVE 로 본다(EFFECTIVE > INDETERMINATE > NON_EFFECTIVE).
_STATE_RANK = {EFFECTIVE: 2, INDETERMINATE: 1, NON_EFFECTIVE: 0}


def effective_state(row):
    """실효 3-상태 사다리 — **순서 의존**(위에서부터 평가). ★본 함수가 사다리의 유일 정본.

    ```
    1) termination_cause == "zero_output"  → NON_EFFECTIVE
    2) tool_call_count == 0                → NON_EFFECTIVE
    3) tool_call_count is null             → INDETERMINATE   (결측 ≠ 0)
    4) outcome == "partial"                → INDETERMINATE
    5) otherwise                           → EFFECTIVE
    ```

    ★**규칙 1 ↔ 규칙 2 는 redundant 가 아니다** (분리 담체 실물):
    `zero_output` 이면 `tool_call_count` 도 0 일 것 같지만 실물은 **`null`** 이다 —
    `CFP-2869 / 설계-리뷰 / CodexReviewAgent / termination_cause: zero_output /
    tool_call_count: null / outcome: partial` 1건. `null == 0` 은 거짓이므로 **규칙 2 는
    발화하지 않는다**. 규칙 1 을 제거하면 이 행은 규칙 3 으로 낙하해
    NON_EFFECTIVE → INDETERMINATE 로 **상태가 바뀐다**. 두 규칙은 서로를 대체하지 않는다.

    ★**규칙 2 가 유일 discriminator 인 반례**:
    `CFP-2875 / 보안-테스트 / CodexReviewAgent / duration_ms 37,677 / tool_call_count 0 /
    outcome: success / termination_cause: normal` — `outcome` 도 `termination_cause` 도
    정상값이고 `tool_call_count` 만이 discriminator 다. 규칙 2 를 빼면 이 행이 EFFECTIVE 로
    위장된다(37.7초 동안 도구 호출 0 = 산출 0 확정).

    타입 방어: `bool` 은 `int` subclass 라 `True/False` 가 `tool_call_count == 0` 에
    오산입되지 않도록 명시 배제한다(비-int 값은 규칙 2 를 발화시키지 않는다).
    """
    if row.get("termination_cause") == "zero_output":
        return NON_EFFECTIVE
    tcc = row.get("tool_call_count")
    if not isinstance(tcc, bool) and isinstance(tcc, int) and tcc == 0:
        return NON_EFFECTIVE
    if tcc is None:
        return INDETERMINATE
    if row.get("outcome") == "partial":
        return INDETERMINATE
    return EFFECTIVE


# ─────────────────────── 시간 축 (UTC epoch 정수 ms 단일 레이어) ──────────────

def _parse_ts_ms(ts):
    """원장 `timestamp`(UTC `...Z`) → epoch **정수 ms**. 파싱 불가 → None.

    §11.6.A #5 — 계산은 UTC epoch 단일 레이어에서만 수행한다. #7 — 정수 ms 만 쓰고
    `elapsed_seconds`(float)는 계산에 사용하지 않는다(원장 실측상 전 행 null 이기도 하다).
    표시 변환(KST 등)은 하지 않고 **원장 UTC 문자열을 원본 그대로** 출력한다
    (외부 timestamp 원본 보존 규약 — 변환 0회 = tz 오차 유입 0).
    """
    if not isinstance(ts, str):
        return None
    try:
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None
    return int(dt.replace(tzinfo=timezone.utc).timestamp()) * 1000


def _duration_ms(row):
    """`duration_ms` 정수 반환 — 결측·비정수·음수 → None (추정 금지, honest-null)."""
    d = row.get("duration_ms")
    if isinstance(d, bool) or not isinstance(d, int) or d < 0:
        return None
    return d


def _start_ms(row):
    """역산 개시 시각(ms) = `timestamp` − `duration_ms`. 둘 중 하나라도 결측 → None.

    ★판별력 제한(§2.6): `timestamp` 는 stop 시각이 아니라 원장 **write 시각**이므로 이 역산은
    두 행의 write_lag 이 같다는 가정 위에서만 성립한다. 60초 임계에 대해 판별력이 없다.
    """
    d = _duration_ms(row)
    if d is None:
        return None
    t = _parse_ts_ms(row.get("timestamp"))
    if t is None:
        return None
    return t - d


def _row_sort_key(row):
    """정렬 tie-break — `replay_spawn_event._sort_key`(:139) 의 **튜플 패턴** 재사용.

    함수 자체를 호출하지 않는 이유: `_sort_key` 의 1차 key 가 `elapsed_seconds`(float)인데
    §11.6.A #7 이 float 를 계산에 쓰는 것을 금지한다(원장 실측 = 전 행 null 이라 정렬이
    무의미해지기도 한다). → **결측을 +inf 로 후순위화하는 패턴**만 계승하고 key 축을 정수
    ms 로 바꾼다(새 규칙 발명 0 — 선례 계승).

    전순서 확정을 위해 (개시 ms, −소요 ms, lane, agent_type, event_id) 5-튜플을 쓴다.
    tie-break 를 제거하면 동률 입력에서 산출이 비결정이 된다(§8 MUT-5 가 무는 축).
    """
    s = _start_ms(row)
    s_key = s if s is not None else float("inf")
    d = _duration_ms(row)
    d_key = -d if d is not None else 0
    return (
        s_key,
        d_key,
        str(row.get("lane_label")),
        str(row.get("agent_type")),
        str(row.get("event_id")),
    )


# ─────────────────────── row 로드 (형제 primitive REUSE) ─────────────────────

def _count_nonempty_lines(ledger_path):
    """물리 non-empty line 수 — malformed skip **건수 산출용**(§4.1: skip 건수 헤더 명시).

    ★JSON 파싱을 재구현하지 않는다 — **줄 수만** 센다. `_read_ledger` 가 돌려준 dict 수와의
    차이 = parse 실패(또는 비-dict) 로 skip 된 건수다. open 파라미터는 `_read_ledger`(:96)와
    **동일해야** 계수가 발산하지 않는다(S-4 행분할 규칙 `\\n` only + errors="replace" 계승).
    부재·OSError → 0 (graceful).
    """
    path_str = str(ledger_path)
    if not os.path.isfile(path_str):
        return 0
    n = 0
    try:
        with open(path_str, encoding="utf-8", errors="replace", newline="\n") as f:
            for line in f:
                if line.strip():
                    n += 1
    except OSError:
        return n
    return n


def load_rows(ledger_path, story_key=""):
    """ledger read → schema filter → event_id dedup → story filter. Returns (rows, stats).

    replay_spawn_event 의 `_read_ledger` / `_dedup_by_event_id` / `_filter_story` REUSE
    (ADR-140 — JSONL read + at-least-once dedup 단일 원본). 부재 → ([], stats) graceful.

    stats 는 §4.1 JSON schema 의 정직 카운터 3종을 채운다:
      - malformed_skipped : parse 실패·비-dict 로 skip 된 물리 line 수 (예외 전파 0)
      - dedup_collapsed   : event_id 중복으로 소멸한 행 수. **두 분기 모두 틀린 문제**임을
                            명시한다 — dedup 하면 실제로는 서로 다른 spawn 이 조용히 소멸하고,
                            dedup 안 하면 계약(spawn-event-v1.md:72) idempotency invariant
                            미준수다. 계약 준수를 택하고 손실을 표기한다(§11.6.A #1).
      - dedup_collapsed_differing : 소멸분 중 **살아남은 행과 내용이 실제로 다른** 행 수.
                            "소멸분이 진짜 다른 spawn 인가"를 추정이 아니라 **실측**으로 낸다
                            (같은 수치면 손실 전량이 실 데이터 손실이라는 뜻). 이 값이 0 보다
                            크면 **입력 행 순서가 바뀔 때 산출이 바뀔 수 있다** — first-wins
                            dedup 의 생존자가 달라지기 때문이다(원장은 append-only 라 실사용
                            경로에서는 순서가 고정된다. firsthand 확인: 중복을 제거한 입력은
                            무작위 재배열에도 산출이 bit-identical).
      - foreign_schema_skipped : 같은 채널에 섞인 타 record type(self-context-v1 등) 수.
    """
    physical = _count_nonempty_lines(ledger_path)
    raw = _replay._read_ledger(Path(ledger_path))
    spawn_rows = [r for r in raw if r.get("schema_version") == _SPAWN_SCHEMA_VERSION]
    deduped = _replay._dedup_by_event_id(spawn_rows)
    rows = _replay._filter_story(deduped, story_key)

    first_by_id = {}
    collapsed_differing = 0
    for r in spawn_rows:
        eid = r.get("event_id")
        if eid is None:
            continue
        if eid not in first_by_id:
            first_by_id[eid] = r
        elif r != first_by_id[eid]:
            collapsed_differing += 1

    stats = {
        "physical_lines": physical,
        "malformed_skipped": max(0, physical - len(raw)),
        "foreign_schema_skipped": len(raw) - len(spawn_rows),
        "dedup_collapsed": len(spawn_rows) - len(deduped),
        "dedup_collapsed_differing": collapsed_differing,
    }
    return rows, stats


# ─────────────────────── codispatch: 클러스터 · PEER census · 실효 집계 ───────

def _story_of(row):
    return row.get("story_key")


def codispatch_story_groups(rows):
    """Story 축 co-dispatch 참고치 — 개시 diff < 60s (§3.1.1).

    ★클러스터 키 = **story_key**(lane 아님). co-dispatch 는 "같은 batch(한 메시지)에서
    dispatch 됐는가" 이고 한 batch 가 lane 라벨을 가로지를 수 있어 lane 으로 쪼개면 같은
    batch 가 갈라진다. 이 키 선택은 Change Plan §3.1.4 의 chief firsthand 참고치
    (CFP-2869 11/27 · CFP-2875 4/26 · CFP-2902 2/17)를 **재현 확인**하여 확정했다.

    분모 규약(§3.1.2): ① `duration_ms` 결측 = 역산 불가 → 분모 제외 + `unmeasurable` 병기
    (위반으로 계상하지 않는다) ② dedup 은 load_rows 에서 이미 수행 ③ 판정 대상 = 같은 story
    안에 측정 가능 행이 2 이상인 그룹만(단독 spawn 은 "판정 비대상" — 위반 아님)
    ④ 6-enum 정당 순차는 현 원장 schema 로 **판별 불가** → 분모에서 빼지 않으며 뺀 척도 하지
    않는다(미분리를 정직 declare).

    "co-dispatch 행" = 같은 story 안에 개시 시각이 60s 미만으로 떨어진 다른 행이 존재하는 행.
    정렬 후 인접 이웃만 보면 충분하다(동치). 클러스터는 단일연결(single-linkage)이라 3개 이상이
    사슬처럼 이어지면 클러스터 폭이 60s 를 넘을 수 있어 `span_ms` 를 같이 실어 노출한다.
    """
    by_story = defaultdict(list)
    for r in rows:
        by_story[_story_of(r)].append(r)

    groups = []
    for story in sorted(by_story, key=lambda s: str(s)):
        srows = by_story[story]
        measurable = [r for r in srows if _start_ms(r) is not None]
        measurable.sort(key=_row_sort_key)
        starts = [_start_ms(r) for r in measurable]

        co_flags = []
        for i, s in enumerate(starts):
            near = False
            if i > 0 and (s - starts[i - 1]) < _CODISPATCH_WINDOW_MS:
                near = True
            if i + 1 < len(starts) and (starts[i + 1] - s) < _CODISPATCH_WINDOW_MS:
                near = True
            co_flags.append(near)

        clusters = []
        cur = []
        for i, r in enumerate(measurable):
            if cur and (starts[i] - starts[i - 1]) >= _CODISPATCH_WINDOW_MS:
                if len(cur) >= 2:
                    clusters.append(cur)
                cur = []
            cur.append(i)
        if len(cur) >= 2:
            clusters.append(cur)

        cluster_out = []
        for idxs in clusters:
            span = starts[idxs[-1]] - starts[idxs[0]]
            cluster_out.append({
                "size": len(idxs),
                "span_ms": span,
                "chained_beyond_window": span >= _CODISPATCH_WINDOW_MS,
                "first_start_utc": measurable[idxs[0]].get("timestamp"),
                "agents": [measurable[i].get("agent_type") for i in idxs],
                "lanes": sorted({str(measurable[i].get("lane_label")) for i in idxs}),
            })

        co_rows = sum(1 for f in co_flags if f)
        groups.append({
            "kind": "codispatch",
            "story_key": story,
            "rows": len(srows),
            "measurable": len(measurable),
            "unmeasurable": len(srows) - len(measurable),
            "codispatch_rows": co_rows,
            "codispatch_ratio": (co_rows / len(measurable)) if measurable else None,
            "judgeable": len(measurable) >= 2,
            "clusters": cluster_out,
        })
    return groups


def _identity_states(group_rows, identity_set):
    """그룹 안 신원(agent_type)별 실효 상태 — 한 신원의 여러 row 는 최상위 상태로 병합."""
    best = {}
    for r in group_rows:
        a = r.get("agent_type")
        if a not in identity_set:
            continue
        st = effective_state(r)
        if a not in best or _STATE_RANK[st] > _STATE_RANK[best[a]]:
            best[a] = st
    return best


def peer_lane_groups(rows):
    """(story_key, lane_label) 그룹별 PEER census + 실효 dual-peer + co-dispatch 판정.

    ★1급 산출 = **PEER-0 / PEER-1 / 비실효 그룹의 표면화**(§3.2.4). co-dispatch leg 는 존치
    하되(빼면 회귀 감시 채널 소멸) 우선순위를 재배치한 것이며 **검사량 축소가 아니다**.

    census 모집단 = 전 (story, lane) 그룹 — peer 가 아예 0인 lane 도 노출해야 커버리지
    (whether) 결손이 보인다. 반면 **실효 dual-peer 비율의 판정 대상(denominator)** 은
    "peer 후보(loose)를 1개 이상 보유한 그룹"으로 고정한다 — 신원 함수(엄격/완화)를 바꿔도
    분모가 흔들리지 않아야 두 수치(§3.1.5 표)가 비교 가능하기 때문이다.

    그룹 내 co-dispatch 판정은 §3.1.1 정의 그대로 **개시 max−min < 60s** 이되, 판정 정의역은
    **채택 신원(엄격안)의 peer row** 다 — peer 가 한 batch 로 떴는가를 묻는 leg 이기 때문이다.
    lane 그룹 전체(PL span 포함)로 재면 오래 도는 PL row 하나가 폭을 지배해 전 그룹이 자동
    STAGGERED 가 되어 판별력이 0 이 된다. lane 전체 폭은 다른 물음(lane 전개 폭)이므로
    `lane_span_ms` 로 **분리 노출**한다. 측정 가능 peer row 가 2 미만이면 "판정 불가"
    (위반 아님)로 남긴다.

    ★iteration 축 부재: 원장에 FIX iteration 필드가 없어 같은 lane 의 서로 다른 라운드가 한
    그룹으로 접힌다(선언된 근사 — 게이트 leg 의 (lane, iteration) 2축 키잉과 disjoint).
    """
    by_key = defaultdict(list)
    for r in rows:
        by_key[(_story_of(r), r.get("lane_label"))].append(r)

    groups = []
    for key in sorted(by_key, key=lambda k: (str(k[0]), str(k[1]))):
        grows = by_key[key]
        strict_states = _identity_states(grows, _PEER_STRICT)
        loose_states = _identity_states(grows, _PEER_LOOSE)
        eff_strict = sorted(a for a, s in strict_states.items() if s == EFFECTIVE)
        eff_loose = sorted(a for a, s in loose_states.items() if s == EFFECTIVE)

        peer_starts = [_start_ms(r) for r in grows
                       if r.get("agent_type") in _PEER_STRICT and _start_ms(r) is not None]
        if len(peer_starts) >= 2:
            span = max(peer_starts) - min(peer_starts)
            verdict = "CO-DISPATCH" if span < _CODISPATCH_WINDOW_MS else "STAGGERED"
        else:
            span = None
            verdict = "판정 불가(측정 가능 peer row < 2)"
        lane_starts = [_start_ms(r) for r in grows if _start_ms(r) is not None]
        lane_span = (max(lane_starts) - min(lane_starts)) if len(lane_starts) >= 2 else None

        n_strict = len(strict_states)
        groups.append({
            "kind": "peer",
            "story_key": key[0],
            "lane_label": key[1],
            "rows": len(grows),
            "peer_census": "PEER-%d" % min(n_strict, 2),
            "peer_census_loose": "PEER-%d" % min(len(loose_states), 2),
            "peers_strict": sorted(strict_states),
            "peers_loose": sorted(loose_states),
            "peer_verdicts": [
                {"agent_type": a, "state": loose_states[a]} for a in sorted(loose_states)
            ],
            "judged": bool(loose_states),
            "dual_peer_effective_strict": len(eff_strict) >= 2,
            "dual_peer_effective_loose": len(eff_loose) >= 2,
            "effective_peers_strict": eff_strict,
            "codispatch": verdict,
            "codispatch_span_ms": span,
            "lane_span_ms": lane_span,
        })
    return groups


# ─────────────────────── criticalpath: 지배 span 근사 ────────────────────────

def _nodes_of(rows):
    """측정 가능 행 → 임계 경로 노드. 결측 행은 노드가 되지 못한다(honest 제외)."""
    nodes = []
    for r in rows:
        s = _start_ms(r)
        d = _duration_ms(r)
        if s is None or d is None:
            continue
        nodes.append({
            "start": s,
            "end": s + d,
            "dur": d,
            "lane": r.get("lane_label"),
            "agent": r.get("agent_type"),
            "timestamp": r.get("timestamp"),
            "event_id": r.get("event_id"),
            "sort": _row_sort_key(r),
        })
    nodes.sort(key=lambda n: n["sort"])
    return nodes


def _mark_nesting(nodes):
    """시간 **포함관계**(중첩) 계수 — 다른 노드를 시간적으로 포함하는 노드 = nesting parent.

    §3.6.3 이 간선 근사 재료로 지목한 "시간 포함관계"는 본 구현에서 **순차 간선의 자동 배제
    조건**으로 작동한다: u 가 v 를 포함하면 정의상 `u.end > v.start` 이므로 `_build_chains`
    의 선행 조건(`u.end ≤ v.start`)을 만족할 수 없다 — 중첩(동시 실행) 쌍은 별도 규칙 없이
    사슬 간선에서 빠진다. 실물에서 PL span 이 자기 worker span 을 통째로 포함하는 형상이
    여기에 해당한다(부모–자식은 순차가 아니라 동시다).

    ★중첩 노드를 사슬 **후보 자체**에서 빼지는 않는다. AC-12a fixture `cp-basic` 에서
    B(5s~905s)가 D(10s~210s)를 포함하는데, 포함=후보 제외로 두면 정답 사슬 B→C 가 소멸해
    기대 정답(1,205s)이 무너진다(firsthand 반증 — 초안 구현에서 실제로 확인 후 정정).
    → 중첩은 **계수·노출만** 하고 후보 자격은 건드리지 않는다.

    구간이 완전히 동일한 두 노드는 서로 포함으로 보지 않는다(형제 취급 — 상호 배제 방지).
    """
    for u in nodes:
        u["nesting_parent"] = False
    for u in nodes:
        for v in nodes:
            if u is v:
                continue
            if u["start"] <= v["start"] and v["end"] <= u["end"] and (
                u["start"], u["end"]) != (v["start"], v["end"]):
                u["nesting_parent"] = True
                break
    return nodes


def _lane_ok(u, v):
    """lane 순서 제약 — 뒤 lane 이 앞 lane 의 선행일 수 없다. 미상 lane 은 제약 미적용."""
    iu = _LANE_ORDER.get(u["lane"])
    iv = _LANE_ORDER.get(v["lane"])
    if iu is None or iv is None:
        return True
    return iu <= iv


def _build_chains(nodes):
    """의존 간선 **근사** — 각 노드마다 "가장 늦게 끝난 선행"(nearest predecessor) 1개.

    간선 조건: u.end ≤ v.start (시간상 선행) ∧ lane 순서 정합. 동률이면 `_row_sort_key`
    파생 튜플로 tie-break 하여 전순서를 확정한다(tie-break 제거 = 비결정, §8 MUT-5 축).
    각 노드의 진입 간선이 1개이므로 그래프는 사슬의 forest 가 되고, u.end ≤ v.start 가
    시간 단조라 사이클이 생기지 않는다(그래도 walk 시 방문 가드를 둔다).
    """
    pred = {}
    for v in nodes:
        best = None
        for u in nodes:
            if u is v:
                continue
            if u["end"] > v["start"]:
                continue
            if not _lane_ok(u, v):
                continue
            cand = (u["end"], u["sort"])
            if best is None or cand > (best["end"], best["sort"]):
                best = u
        if best is not None:
            pred[id(v)] = best
    return pred


def _chain_of(node, pred):
    chain = []
    seen = set()
    cur = node
    while cur is not None and id(cur) not in seen:
        seen.add(id(cur))
        chain.append(cur)
        cur = pred.get(id(cur))
    chain.reverse()
    return chain


def criticalpath_story_groups(rows):
    """Story별 지배 span(임계 경로) — agent 단위·lane 단위 귀속.

    ★**근사**다(§3.6.3). 원장에 의존 간선이 없다(`parent_event_id` 관측 전 행 null) —
    시간 포함관계(중첩은 순차 간선에서 자동 배제) + 시간 선행 + lane 순서로 근사한다.

    ★**단일 최장 span 과 구별**되는 것이 핵심이다(§3.6.3). 임계 경로는 **간선을 1개 이상
    갖는 사슬**(노드 ≥ 2)로 정의한다 — 노드 1개는 그래프를 통과하는 '경로'가 아니라 그냥
    span 이고, 그것을 임계 경로라 부르면 정확히 §3.6.3 이 금지한 "단일 최장 span 오인"이
    된다. 단일 최장 span 은 `longest_single_span_ms` 로 **따로** 낸다. 이 정의 하에서
    비연쇄 span 을 아무리 키워도(§8 MUT-4) 사슬 정답은 불변이다.
    사슬이 없으면(연쇄 2 노드 미만) 임계 경로는 **판정 불가**(None)로 남긴다 — 단일 span 을
    임계 경로 자리에 끼워 넣지 않는다.

    사슬 길이(wall)는 `end(마지막) − start(첫)` 로 사슬 중간 공백까지 포함하며,
    `work`(사슬 노드 소요 합)를 함께 낸다.

    I-6 상하한 관측: `max(사슬 후보 span) ≤ 임계경로 ≤ sum(span)`. ★**두 읽기를 모두 낸다** —
    `wall`(사슬 공백 포함)은 lane 사이 유휴가 길면 상한 `sum(span)` 을 넘어설 수 있고
    (실 원장 실측: 5 story 중 4 story 에서 wall > sum), `work`(사슬 노드 소요 합)는 정의상
    두 경계 안에 들어온다. 어느 읽기가 I-6 을 만족하는지 산출에 그대로 노출하고
    (i6_* 4 플래그) 판정하지 않는다 — 본 산출은 관측치이지 게이트가 아니다.
    """
    by_story = defaultdict(list)
    for r in rows:
        by_story[_story_of(r)].append(r)

    groups = []
    for story in sorted(by_story, key=lambda s: str(s)):
        srows = by_story[story]
        nodes = _mark_nesting(_nodes_of(srows))
        pred = _build_chains(nodes)

        best_chain = []
        best_key = None
        for n in nodes:
            chain = _chain_of(n, pred)
            if len(chain) < 2:
                continue  # 노드 1개 = 경로 아님(단일 span 은 별 지표로 낸다)
            wall = chain[-1]["end"] - chain[0]["start"]
            key = (wall, len(chain), chain[-1]["sort"])
            if best_key is None or key > best_key:
                best_key = key
                best_chain = chain

        wall_ms = (best_chain[-1]["end"] - best_chain[0]["start"]) if best_chain else None
        work_ms = sum(n["dur"] for n in best_chain) if best_chain else None
        sum_span = sum(n["dur"] for n in nodes)
        # ★I-6 재배선(D-2 확정): max_span = max(사슬 노드 span) — 사슬-스코프로 좁혀 I-6 정의에 정합
        # 미선택 잔여 R-b: 사슬 밖 최장 span 은 `longest_single_span_ms` 로 따로 낸다
        max_span = max((n["dur"] for n in best_chain), default=None) if best_chain else None
        longest_single_span = max((n["dur"] for n in nodes), default=None)  # 전체 노드

        by_agent = defaultdict(lambda: {"ms": 0, "n": 0})
        by_lane = defaultdict(lambda: {"ms": 0, "n": 0})
        for n in best_chain:
            by_agent[str(n["agent"])]["ms"] += n["dur"]
            by_agent[str(n["agent"])]["n"] += 1
            by_lane[str(n["lane"])]["ms"] += n["dur"]
            by_lane[str(n["lane"])]["n"] += 1

        groups.append({
            "kind": "criticalpath",
            "story_key": story,
            "rows": len(srows),
            "nodes": len(nodes),
            "unmeasurable": len(srows) - len(nodes),
            "nesting_parents": sum(1 for n in nodes if n["nesting_parent"]),
            "path_undecidable": not best_chain,
            "path_nodes": [
                {
                    "agent_type": n["agent"],
                    "lane_label": n["lane"],
                    "timestamp_utc": n["timestamp"],
                    "offset_s": (n["start"] - best_chain[0]["start"]) / 1000.0,
                    "duration_ms": n["dur"],
                }
                for n in best_chain
            ],
            "critical_path_wall_ms": wall_ms,
            "critical_path_work_ms": work_ms,
            "longest_single_span_ms": longest_single_span,  # 미선택 R-b: 전체 노드 max
            "sum_span_ms": sum_span,
            "i6_wall_lower_ok": (wall_ms is not None and max_span is not None
                                 and max_span <= wall_ms),
            "i6_wall_upper_ok": (wall_ms is not None and wall_ms <= sum_span),
            "i6_work_lower_ok": (work_ms is not None and max_span is not None
                                 and max_span <= work_ms),
            "i6_work_upper_ok": (work_ms is not None and work_ms <= sum_span),
            "attribution_agent": {
                k: v for k, v in sorted(by_agent.items(), key=lambda kv: (-kv[1]["ms"], kv[0]))
            },
            "attribution_lane": {
                k: v for k, v in sorted(by_lane.items(), key=lambda kv: (-kv[1]["ms"], kv[0]))
            },
        })
    return groups


# ─────────────────────── 산출 조립 · 출력 ────────────────────────────────────

def build_payload(subcommand, rows, stats, story_key):
    """§4.1 JSON schema 7 키 envelope — 두 서브커맨드 공통(그룹 kind 로만 구분).

    denominator = **역산 가용 행 수**(dedup 후 ∧ `duration_ms` 가용) = co-dispatch 판정 분모.
    unmeasurable = `duration_ms` 결측으로 분모에서 제외된 행 수(위반 아님 — §3.1.2 축①).
    """
    measurable = sum(1 for r in rows if _start_ms(r) is not None)
    verdicts = Counter(effective_state(r) for r in rows)
    if subcommand == "codispatch":
        groups = codispatch_story_groups(rows) + peer_lane_groups(rows)
    else:
        groups = criticalpath_story_groups(rows)
    return {
        "story_key": story_key or None,
        "denominator": measurable,
        "unmeasurable": len(rows) - measurable,
        "dedup_collapsed": stats["dedup_collapsed"],
        "malformed_skipped": stats["malformed_skipped"],
        "groups": groups,
        "verdict_counts": {
            EFFECTIVE: verdicts.get(EFFECTIVE, 0),
            INDETERMINATE: verdicts.get(INDETERMINATE, 0),
            NON_EFFECTIVE: verdicts.get(NON_EFFECTIVE, 0),
        },
    }


def _honesty_lines(subcommand, rows, stats, ledger_path):
    """산출 헤더의 정직 라벨 — 판별력 제한·근사·미해소 축을 **항상** 동반한다(§3.1.3/§3.6.3)."""
    model_null = sum(1 for r in rows if r.get("model") is None)
    lines = [
        "analyze-spawn-concurrency (%s) — 진단(diagnostic) 산출이며 게이트가 아니다."
        " 어떤 판정도 차단하지 않고 exit 0 이다." % subcommand,
        "원장: %s (물리 %d행 / spawn-event-v1 판독 %d행)"
        % (ledger_path, stats["physical_lines"], len(rows)),
        "정직 카운터: malformed_skipped=%d · dedup_collapsed=%d(그중 내용 상이 %d — 계약"
        " idempotency 를 지키느라 실제로 다른 spawn 이 소멸한 건수) · foreign_schema_skipped=%d"
        % (stats["malformed_skipped"], stats["dedup_collapsed"],
           stats["dedup_collapsed_differing"], stats["foreign_schema_skipped"]),
        "[판별력 제한] 개시 시각 = timestamp − duration_ms **역산**. timestamp 는 stop 시각이"
        " 아니라 원장 write 시각이라 두 행의 write_lag 이 다르면 개시 차가 왜곡된다 →"
        " 60초 임계에 대해 이 방법은 판별력이 없다(방향성 참고치).",
        "[provenance 미해소] duration_ms 는 usage block ∪ wall-clock 혼재이며 provenance"
        " 필드가 없다. 본 산출은 이를 해소하지 않는다.",
        "[산출 불가] model=null %d/%d → 모델 tier/버킷 축은 사후 확인 불가(추정하지 않는다)."
        % (model_null, len(rows)),
        "[미분리 declare] 6-enum 정당 순차(sequential mandate)는 현 원장 schema 로 판별 불가라"
        " 분모에서 빼지 않으며 뺀 척도 하지 않는다.",
        "[그룹 축 declare] 원장에 FIX iteration 필드가 없어 같은 lane 의 서로 다른 라운드가"
        " 한 그룹으로 접힌다.",
        "[시각 표기] 원장 UTC 문자열 원본 보존(표시 변환 0회) · 계산은 UTC epoch 정수 ms 단일 레이어.",
    ]
    if subcommand == "codispatch":
        lines.append(
            "[peer 신원 함수] 채택 = 엄격안 {ClaudeReviewAgent, CodexReviewAgent}"
            " (agent_type 은 roster-derived semi-open enum 이고 \"claude\" 는 roster 실명이"
            " 아니다). 완화안(+\"claude\") 수치를 병기하되 두 수치를 서로의 검증으로 쓰지 않는다.")
        lines.append(
            "[센서스 파라미터] 필드=원장 agent_type · 매칭=enum 값 정확 일치 ·"
            " 모집단=spawn-event.jsonl 판독 %d행 (Story §14 free-text `agent` 채널과 별개)."
            % len(rows))
    else:
        lines.append(
            "[근사 declare] 임계 경로는 근사다 — 원장에 의존 간선이 없다(parent_event_id 실측"
            " 전 행 null). 시간 포함관계(중첩 = 동시 실행 → 순차 간선에서 자동 배제) +"
            " 시간 선행(가장 늦게 끝난 선행 1개) + lane 순서로 근사했다.")
        lines.append(
            "[정의] 임계 경로 = 간선 1개 이상을 갖는 사슬(노드 ≥ 2). **단일 최장 span 과"
            " 다르다** — 단일 span 은 longest_single_span 으로 따로 낸다. 사슬이 없으면"
            " 임계 경로는 판정 불가로 남기며 단일 span 을 그 자리에 끼워 넣지 않는다.")
        lines.append(
            "[lane 제약 약화] 미등재 lane(예: \"없음\")은 순서 제약을 적용하지 않는다.")
    return lines


def _fmt_s(ms):
    return "—" if ms is None else "%.1f" % (ms / 1000.0)


def _emit_json(payload, honesty):
    """JSON 은 stdout 에 **순수 JSON 만** — 정직 라벨은 stderr 로 내보내 파싱을 깨지 않는다."""
    for line in honesty:
        print("# " + line, file=sys.stderr)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _emit_table_codispatch(payload, honesty):
    for line in honesty:
        print(line)
    print("")

    cds = [g for g in payload["groups"] if g["kind"] == "codispatch"]
    peers = [g for g in payload["groups"] if g["kind"] == "peer"]

    print("[표 A] Story별 co-dispatch 역산 참고치 (개시 diff < 60s · 분모 = 역산 가용 행)")
    header = "story | rows | 역산가용 | 역산불가 | co-dispatch | 비율"
    print(header)
    print("-" * len(header))
    for g in cds:
        ratio = g["codispatch_ratio"]
        print("%s | %d | %d | %d | %d | %s"
              % (g["story_key"], g["rows"], g["measurable"], g["unmeasurable"],
                 g["codispatch_rows"],
                 ("%.0f%%" % (ratio * 100)) if ratio is not None else "판정 비대상"))
    if not cds:
        print("(0 story — 빈 원장 또는 filter 결과 없음)")
    print("")

    print("[표 B] (story, lane) 그룹 PEER census + 실효 3-상태 + co-dispatch")
    header = ("story | lane | rows | census(strict) | peer 후보 실효상태(loose 병기) |"
              " dual(strict) | dual(loose) | peer co-dispatch | peer span_s | lane span_s")
    print(header)
    print("-" * len(header))
    for g in peers:
        verd = ", ".join("%s=%s" % (v["agent_type"], v["state"]) for v in g["peer_verdicts"])
        print("%s | %s | %d | %s | %s | %s | %s | %s | %s | %s"
              % (g["story_key"], g["lane_label"], g["rows"], g["peer_census"],
                 verd or "—",
                 "Y" if g["dual_peer_effective_strict"] else "N",
                 "Y" if g["dual_peer_effective_loose"] else "N",
                 g["codispatch"], _fmt_s(g["codispatch_span_ms"]),
                 _fmt_s(g["lane_span_ms"])))
    if not peers:
        print("(0 group)")
    print("")

    census = Counter(g["peer_census"] for g in peers)
    judged = [g for g in peers if g["judged"]]
    ds = sum(1 for g in judged if g["dual_peer_effective_strict"])
    dl = sum(1 for g in judged if g["dual_peer_effective_loose"])
    n = len(judged)
    print("PEER census (전 %d 그룹, 채택 엄격안 기준): PEER-2 %d / PEER-1 %d / PEER-0 %d"
          % (len(peers), census.get("PEER-2", 0), census.get("PEER-1", 0),
             census.get("PEER-0", 0)))
    print("실효 dual-peer (판정 대상 = peer 후보 1개 이상 보유 그룹 %d): "
          "채택 엄격안 %d/%d (%s) · 병기 완화안 %d/%d (%s)"
          % (n, ds, n, ("%.1f%%" % (100.0 * ds / n)) if n else "—",
             dl, n, ("%.1f%%" % (100.0 * dl / n)) if n else "—"))
    vc = payload["verdict_counts"]
    print("실효 3-상태 집계 (판독 전 행): EFFECTIVE %d / INDETERMINATE %d / NON_EFFECTIVE %d"
          % (vc[EFFECTIVE], vc[INDETERMINATE], vc[NON_EFFECTIVE]))
    print("denominator=%d · unmeasurable=%d · dedup_collapsed=%d · malformed_skipped=%d"
          % (payload["denominator"], payload["unmeasurable"],
             payload["dedup_collapsed"], payload["malformed_skipped"]))


def _emit_table_criticalpath(payload, honesty):
    for line in honesty:
        print(line)
    print("")

    groups = payload["groups"]
    print("[표 C] Story별 지배 span(임계 경로 근사) — 단일 최장 span 과 병기")
    header = ("story | 임계경로 wall_s | work_s | 경로노드/전체노드 | 최장단일span_s |"
              " sum_span_s | 중첩부모 | I-6 wall(하/상) | I-6 work(하/상)")
    print(header)
    print("-" * len(header))
    for g in groups:
        # 임계 경로 판정 불가면 I-6 은 **비대상**이다 — 위반(NG)으로 표기하지 않는다.
        i6 = ("—/— | —/—" if g["path_undecidable"] else "%s/%s | %s/%s" % (
            "OK" if g["i6_wall_lower_ok"] else "NG",
            "OK" if g["i6_wall_upper_ok"] else "NG",
            "OK" if g["i6_work_lower_ok"] else "NG",
            "OK" if g["i6_work_upper_ok"] else "NG"))
        print("%s | %s | %s | %d/%d | %s | %s | %d | %s"
              % (g["story_key"],
                 "판정 불가" if g["path_undecidable"] else _fmt_s(g["critical_path_wall_ms"]),
                 _fmt_s(g["critical_path_work_ms"]), len(g["path_nodes"]),
                 g["nodes"], _fmt_s(g["longest_single_span_ms"]),
                 _fmt_s(g["sum_span_ms"]), g["nesting_parents"], i6))
    if not groups:
        print("(0 story — 빈 원장 또는 filter 결과 없음)")
    print("")

    for g in groups:
        if g["path_undecidable"]:
            print("[%s] 임계 경로 판정 불가 — 연쇄 2 노드 미만(측정 가능 노드 %d개, 최장 단일"
                  " span %ss)" % (g["story_key"], g["nodes"],
                                  _fmt_s(g["longest_single_span_ms"])))
            print("")
            continue
        print("[%s] 임계 경로 노드 %d개 (wall %ss / work %ss)"
              % (g["story_key"], len(g["path_nodes"]),
                 _fmt_s(g["critical_path_wall_ms"]), _fmt_s(g["critical_path_work_ms"])))
        for i, n in enumerate(g["path_nodes"]):
            print("  %d. %s / %s | start(utc write-anchor)=%s | +%.1fs | %ss"
                  % (i + 1, n["lane_label"], n["agent_type"], n["timestamp_utc"],
                     n["offset_s"], _fmt_s(n["duration_ms"])))
        if g["attribution_agent"]:
            print("  agent 귀속: " + " · ".join(
                "%s %ss(%d)" % (k, _fmt_s(v["ms"]), v["n"])
                for k, v in g["attribution_agent"].items()))
            print("  lane  귀속: " + " · ".join(
                "%s %ss(%d)" % (k, _fmt_s(v["ms"]), v["n"])
                for k, v in g["attribution_lane"].items()))
        print("")


# ─────────────────────── CLI ────────────────────────────────────────────────

def _worktree_path_notice(ledger_path):
    """§11.6.A #6 — 입력 파일 위치는 **main checkout 전제**. worktree 경로면 경고한다.

    worktree 에서 실행하면 별 원장 파일이 생기고 병합 경로가 없다(파티션). 판정은
    경로 문자열 heuristic 이며(정직: 완전 판별 아님) 경고만 낸다 — 차단하지 않는다.
    """
    s = str(ledger_path).replace("\\", "/")
    if "/worktrees/" in s:
        print("[notice] ledger 경로가 worktree 안이다 — 본 산출은 main checkout 원장을 전제한다"
              " (worktree 원장은 별 파티션이며 병합 경로가 없다): %s" % ledger_path,
              file=sys.stderr)


def run(args):
    ledger_path = _replay._resolve_ledger_path(args.ledger_path)

    # setup error 판정 = aggregate_spawn_event._setup_error REUSE (형제 규약 동일 표면).
    # 부재는 setup error 가 아니다(graceful 0 — 계측 미시작은 통상 상태).
    err = _aggregate._setup_error(ledger_path)
    if err is not None:
        print("[codeforge-spawn-concurrency-setup-error] analyze-spawn-concurrency: %s" % err,
              file=sys.stderr)
        sys.exit(2)

    _worktree_path_notice(ledger_path)

    rows, stats = load_rows(ledger_path, args.story_key)
    payload = build_payload(args.subcommand, rows, stats, args.story_key)
    honesty = _honesty_lines(args.subcommand, rows, stats, ledger_path)

    if args.format == "json":
        _emit_json(payload, honesty)
    elif args.subcommand == "codispatch":
        _emit_table_codispatch(payload, honesty)
    else:
        _emit_table_criticalpath(payload, honesty)

    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="spawn-event-v1 병렬 dispatch 진단 (CFP-2914 Phase 2 — read-only diagnostic,"
                    " 게이트 아님)")
    parser.add_argument("subcommand", choices=["codispatch", "criticalpath"],
                        help="codispatch = co-dispatch 참고치 + PEER census + 실효 3-상태 /"
                             " criticalpath = 지배 span(임계 경로 근사)")
    parser.add_argument("--ledger-path", default="",
                        help="spawn-event.jsonl 경로 (default: ${CLAUDE_PROJECT_DIR}/.claude/ledger/...)")
    parser.add_argument("--story-key", default="",
                        help="story_key filter (지정 시 해당 Story event 만)")
    parser.add_argument("--format", default="table", choices=["json", "table"],
                        help="출력 형식 (default table)")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
