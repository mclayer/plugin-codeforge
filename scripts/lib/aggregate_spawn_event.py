#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# aggregate_spawn_event.py — spawn-event-v1 outcome/model aggregate (read-only)
#
# Carrier: CFP-2850 Phase 2 (구현) / Epic CFP-2391 — N9 agent outcome 분류 aggregate.
# 출처: oh-my-claudecode (MIT, https://github.com/Yeachan-Heo/oh-my-claudecode)
#       — per-agent registry(agent_type/token_usage) 집계 개념 차용. enforcement 비-차용
#       (측정·관측만 — ADR-163 §결정 10 measurement-vs-fix boundary).
#
# 책임 (Change Plan §5 / §8.1.1 AC-9 / AC-10):
#   - AC-9 pivot: agent_type(역할) × model(모델) × outcome → group. 역할·모델별 실패율
#     (비성공 outcome 비율) 계산 가능. model row field REUSE (append_spawn_event 저장분).
#   - AC-10 wasted-token join: outcome-conditioned 낭비토큰 = 비성공 outcome
#     {failure, inconclusive, partial} 의 **실측 total_tokens** 합. 추정 token 금지
#     (honest-null, ADR-119) — total_tokens=null row 는 낭비합산에서 정직 제외.
#
# 불변식:
#   - **read-only** — 신규 저장계층 0 (replay_spawn_event 와 동형, contract Phase 2 scope).
#     append 경로(append_spawn_event) 무접촉 · _append_jsonl_row primitive 무변경.
#   - **event_id read-time dedup** — replay_spawn_event 의 _read_ledger/_dedup_by_event_id/
#     _filter_story/_resolve_ledger_path primitive REUSE (중복 유입 금지 — ADR-140).
#   - **추정 금지 (honest-null)** — total_tokens=null(비attributed) row 는 낭비집계 제외.
#     naive 추정치로 메꾸지 않는다 (AC-10 neg test / ADR-119 검증-후-단언).
#   - 0 API call, local read only. graceful: ledger 부재 → 빈 결과 + exit 0 (ADR-115).
#   - record-only aggregate — 어떤 판정도 gate 아님 (INV-5). exit 0 (setup error 만 2).
#
# 사용:
#   python3 aggregate_spawn_event.py [--ledger-path <abs>] [--story-key CFP-2850]
#       [--format json|table]
#
# Exit codes:
#   0 = 성공 (빈 결과 포함 — graceful)
#   2 = setup error (ledger path 가 디렉터리 등 비정상 — 단 부재는 graceful 0)

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Windows cp949 인코딩 회피 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# replay_spawn_event read/dedup/filter primitive REUSE (ADR-140 reuse-before-write) —
# 신규 ledger-read/dedup 로직 복제 금지. import 실패 시 path fallback(append_spawn_event 선례).
try:
    import replay_spawn_event as _replay
except Exception:  # pragma: no cover — import path fallback
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import replay_spawn_event as _replay


# ─────────────────────── outcome vocab (append_spawn_event 정합) ──────────────

# 비성공(낭비) outcome closed-set — append_spawn_event._OUTCOMES 中 success 제외.
# wasted-token 낭비집계 대상 + 실패율 numerator (Change Plan §8.1.1 AC-9/AC-10).
# outcome=null(unclassified) / success 는 낭비·실패 대상 아님 (`outcome != success`
# 광의가 아닌 명시 closed-set — outcome=None 정직 제외).
_NONSUCCESS_OUTCOMES = frozenset({"failure", "inconclusive", "partial"})

# record type discriminator (contract §2.1) — spawn-event.jsonl 은 **공유 channel** 이라
# self-context-v1 등 별 record type 이 같은 파일에 섞인다. 집계 대상 = spawn row 만.
_SPAWN_SCHEMA_VERSION = "spawn-event-v1"


# ─────────────────────── row 로드 (replay primitive REUSE) ───────────────────

def load_rows(ledger_path, story_key=""):
    """ledger read → **schema_version filter** → event_id read-time dedup → story_key filter.

    replay_spawn_event 의 _read_ledger / _dedup_by_event_id / _filter_story REUSE
    (ADR-140 — JSONL read + at-least-once dedup 로직 단일 원본). 부재 → [] (graceful).

    ★F-CR-002 (구현리뷰 FIX Iter 2) — schema_version 필터 신설:
    spawn-event.jsonl 은 spawn-event-v1 과 self-context-v1 이 `schema_version`
    discriminator 로 공존하는 **공유 channel**(contract §2.1). 필터 부재 시 self-context row
    (agent_type/model/outcome/total_tokens 전부 부재)가 `(None, None)` 그룹으로 pivot 에
    유입돼 AC-9 실패율 denominator 를 오염시키고, AC-10 낭비집계 row_count 를 부풀렸다.
    필터 위치·형태 = reconcile_spawn_completion_count.count_recorded_rows(:109) 동형 패턴
    REUSE (filter → dedup 순서 동일 — 신규 로직 0).
    """
    rows = _replay._read_ledger(Path(ledger_path))
    rows = [r for r in rows if r.get("schema_version") == _SPAWN_SCHEMA_VERSION]
    rows = _replay._dedup_by_event_id(rows)
    rows = _replay._filter_story(rows, story_key)
    return rows


# ─────────────────────── AC-9 pivot (역할 × 모델 × outcome) ───────────────────

def pivot_role_model_outcome(rows):
    """AC-9 pivot — (agent_type, model) → Counter(outcome) group.

    역할(agent_type) × 모델(model) 별 outcome 분포. outcome=null 은 `None` key 로 집계
    (누락 은폐 금지 — honest). model=null 은 `None` model key.
    Returns dict[(agent_type, model)] = Counter({outcome_or_None: count}).
    """
    pivot = defaultdict(Counter)
    for r in rows:
        key = (r.get("agent_type"), r.get("model"))
        pivot[key][r.get("outcome")] += 1
    return dict(pivot)


def failure_rates(rows):
    """AC-9 역할·모델별 실패율 — (agent_type, model) → {total, failure, failure_rate}.

    failure = 비성공 outcome {failure, inconclusive, partial} 카운트 (closed-set).
    failure_rate = failure / total (그룹 총 row). total==0 → None (0-division 회피).
    total = 그룹 전 row (outcome=null 포함 denominator — 미분류를 성공으로 위장하지 않음).
    """
    tally = defaultdict(lambda: {"total": 0, "failure": 0})
    for r in rows:
        key = (r.get("agent_type"), r.get("model"))
        tally[key]["total"] += 1
        if r.get("outcome") in _NONSUCCESS_OUTCOMES:
            tally[key]["failure"] += 1
    result = {}
    for key, t in tally.items():
        total = t["total"]
        result[key] = {
            "total": total,
            "failure": t["failure"],
            "failure_rate": (t["failure"] / total) if total else None,
        }
    return result


# ─────────────────────── AC-10 wasted-token join (honest-null) ────────────────

def _measured_total_tokens(row):
    """row 의 실측 total_tokens 반환 — int(비음수) 아니면 None (추정 금지, honest-null).

    total_tokens=null(비attributed) / 비정수 → None (낭비집계에서 정직 제외).
    bool 은 int subclass 이므로 명시 배제 (True/False 오산입 방지).
    """
    v = row.get("total_tokens")
    if isinstance(v, bool):
        return None
    if isinstance(v, int) and v >= 0:
        return v
    return None


def wasted_tokens(rows):
    """AC-10 outcome-conditioned 낭비토큰 — 비성공 outcome 의 **실측** total_tokens 합.

    낭비집계 대상 = outcome ∈ {failure, inconclusive, partial} AND total_tokens 실측(non-null).
    total_tokens=null row 는 추정치로 메꾸지 않고 제외 (honest-null, ADR-119 / AC-10 neg).
    Returns int (대상 없음 → 0).
    """
    total = 0
    for r in rows:
        if r.get("outcome") not in _NONSUCCESS_OUTCOMES:
            continue
        tok = _measured_total_tokens(r)
        if tok is None:
            continue  # 추정 대체 금지 — 정직 제외
        total += tok
    return total


def wasted_tokens_by_group(rows):
    """AC-9×AC-10 join — (agent_type, model) → 비성공 outcome 실측 total_tokens 합.

    역할·모델별 낭비토큰 (outcome-conditioned, honest-null 동일 규칙).
    Returns dict[(agent_type, model)] = int.
    """
    by_group = defaultdict(int)
    for r in rows:
        if r.get("outcome") not in _NONSUCCESS_OUTCOMES:
            continue
        tok = _measured_total_tokens(r)
        if tok is None:
            continue
        by_group[(r.get("agent_type"), r.get("model"))] += tok
    return dict(by_group)


# ─────────────────────── aggregate 조립 + 출력 ───────────────────────────────

def aggregate(rows):
    """전체 aggregate 조립 (AC-9 pivot/failure_rate + AC-10 wasted-token join)."""
    fr = failure_rates(rows)
    wg = wasted_tokens_by_group(rows)
    pivot = pivot_role_model_outcome(rows)
    groups = []
    for key in sorted(pivot.keys(), key=lambda k: (str(k[0]), str(k[1]))):
        agent_type, model = key
        outcomes = {(k if k is not None else "null"): v for k, v in pivot[key].items()}
        groups.append({
            "agent_type": agent_type,
            "model": model,
            "outcomes": outcomes,
            "total": fr[key]["total"],
            "failure": fr[key]["failure"],
            "failure_rate": fr[key]["failure_rate"],
            "wasted_tokens": wg.get(key, 0),
        })
    return {
        "row_count": len(rows),
        "groups": groups,
        "wasted_tokens_total": wasted_tokens(rows),
    }


def _emit_json(agg):
    print(json.dumps(agg, ensure_ascii=False, indent=2))


def _emit_table(agg):
    groups = agg["groups"]
    if not groups:
        print("aggregate-spawn-event: 0 groups (빈 ledger 또는 filter 결과 없음)")
        return
    header = "agent_type | model | total | failure | failure_rate | wasted_tokens"
    print(header)
    print("-" * len(header))
    for g in groups:
        fr = g["failure_rate"]
        fr_s = ("%.3f" % fr) if isinstance(fr, (int, float)) else "—"
        print(
            "%s | %s | %d | %d | %s | %d"
            % (
                g["agent_type"] if g["agent_type"] is not None else "—",
                g["model"] if g["model"] is not None else "—",
                g["total"],
                g["failure"],
                fr_s,
                g["wasted_tokens"],
            )
        )
    print("")
    print(
        "aggregate-spawn-event: %d groups / wasted_tokens_total=%d (outcome≠success × 실측 token, 추정 제외)"
        % (len(groups), agg["wasted_tokens_total"])
    )


def _setup_error(ledger_path):
    """setup error 판정 — ledger path 가 비정상 형상이면 사유 문자열, 정상이면 None.

    ★F-CR-012 (구현리뷰 FIX Iter 2) — 종료코드 규약 실배선:
    모듈 docstring 이 `2 = setup error (ledger path 가 디렉터리 등 비정상)` 를 **선언만** 하고
    구현이 없어, 디렉터리/권한 오류가 `_read_ledger` 의 OSError swallow 로 **빈 결과 + exit 0**
    (= "0 groups" 정상 출력)으로 위장됐다. usage/setup 오류와 "정말 데이터가 없음"을 호출자가
    구분 못 하는 silent-success → exit 2 로 분리한다.
    **경계**: ledger **부재**는 setup error 아님(graceful 0 — 계측 미시작 정상 상태).
    본 script 는 read-only aggregate 이며 append 경로가 아니다 — append 의 exit-0 불변식
    (ADR-115, record-only never-block)과는 별 축이다(혼동 금지).
    """
    p = Path(ledger_path)
    if p.is_dir():
        return "ledger path 가 디렉터리 (파일 기대): %s" % p
    if p.exists():
        try:
            with open(str(p), "rb"):
                pass
        except OSError as e:
            return "ledger read 불가 (%s): %s" % (e.__class__.__name__, p)
    return None


def cmd_aggregate(args):
    ledger_path = _replay._resolve_ledger_path(args.ledger_path)

    err = _setup_error(ledger_path)
    if err is not None:
        print(
            "[codeforge-spawn-event-aggregate-setup-error] aggregate-spawn-event: %s" % err,
            file=sys.stderr,
        )
        sys.exit(2)

    rows = load_rows(ledger_path, args.story_key)
    agg = aggregate(rows)
    if args.format == "json":
        _emit_json(agg)
    else:
        _emit_table(agg)
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="spawn-event-v1 outcome/model aggregate (CFP-2850 Phase 2 — read-only, AC-9/AC-10)"
    )
    parser.add_argument("--ledger-path", default="",
                        help="spawn-event.jsonl 경로 (default: ${CLAUDE_PROJECT_DIR}/.claude/ledger/...)")
    parser.add_argument("--story-key", default="",
                        help="story_key filter (지정 시 해당 Story event 만)")
    parser.add_argument("--format", default="table", choices=["json", "table"],
                        help="출력 형식 (default table)")
    args = parser.parse_args()
    cmd_aggregate(args)


if __name__ == "__main__":
    main()
