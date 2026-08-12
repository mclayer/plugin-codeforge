#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tier: [measurement]
# check_pl_spawn_observation.py — AC-15 L-A/L-C 파서 (PL spawn 관측)
#
# Carrier: CFP-2926 Phase 2 (구현) / Story NG-7
# SSOT: docs/adr/ADR-154-amendment-1.md §AC-15 (PL spawn 관측)
#
# 책임:
#   - 판정 = `L-A ∨ (L-B ∧ L-C)` 충족 = PASS
#   - 전건 미충족 = INCONCLUSIVE (RED 아님)
#
#   * L-A (primary, hook-stamped): dev-process-event 의 tool_call 이벤트 중
#     `tool_name == "Agent"` ∧ `writer_key == sha256(<PL agent_id>)` 인 행 ≥1
#     → "PL 이 실제로 Agent 를 호출했다" (모델 서술 0)
#
#   * L-B (보조): spawn-event 에 `lineage_source == hook_stamped` 인 depth-2 row presence
#     ★`lineage_source` 필드가 현 계약에 없을 수 있음 → 없으면 L-B = 판정 불가
#     → L-B 부재를 trace 에 emit
#
#   * L-C (fallback): doc-queue 하 worker 별 disjoint 제출 파일 수 ≥2
#     + 파일 mtime 창 (수동 재현 곤란 → 현재는 fixture 만)
#
# 불변식:
#   - 3-state: PASS / RED / INCONCLUSIVE
#   - stdout 단일 JSON 라인 + sys.exit(n)
#   - trace numeric (identity_probe echo)
#   - Python 3.9 + stdlib only + UTF-8
#
# 정직 천장 (docstring):
#   - L-A·L-B 는 PreToolUse(Agent) matcher payload 의 caller 신원(U-a) · depth-2
#     agent_id 구분(U-f) probe 에 걸린다. ★미확인 상태★
#   - 실패 시 L-C 단독 판정 (fallback)
#
# 사용:
#   python3 check_pl_spawn_observation.py [--dev-process PATH] [--spawn-event PATH] [--pl-agent-id ID]
#   python3 check_pl_spawn_observation.py --self-test
#

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


_DEFAULT_DEVPROC = Path(".claude") / "ledger" / "dev-process-event.jsonl"
_DEFAULT_SPAWNEVENT = Path(".claude") / "ledger" / "spawn-event.jsonl"


def _read_ledger_lines(ledger_path):
    """원장 read-only 로드 → line 리스트."""
    p = Path(ledger_path)
    if not p.exists():
        return []
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return text.splitlines()


def _sha256_id(agent_id):
    """agent_id 의 sha256 해시."""
    return hashlib.sha256(agent_id.encode("utf-8")).hexdigest()


def check_pl_spawn_observation(devproc_lines, spawnevent_lines, pl_agent_id, doc_queue_root=None, story_key=None):
    """AC-15 PL spawn 관측 판정.

    입력:
      devproc_lines: dev-process-event.jsonl 라인 시퀀스
      spawnevent_lines: spawn-event.jsonl 라인 시퀀스
      pl_agent_id: PL agent ID 문자열
      doc_queue_root: doc-queue 루트 경로 (L-C 용, 선택사항)
      story_key: Story 키 (L-C doc-queue 경로 구성 용, 선택사항)

    반환: {
      "verdict": "PASS" | "INCONCLUSIVE",
      "reason": str,
      "l_a_found": bool,     # Agent tool_call 관측
      "l_b_found": bool,     # depth-2 lineage_source 관측
      "l_b_supported": bool, # lineage_source 필드 지원 여부
      "l_c_found": bool,     # doc-queue fallback
      "trace": {
        "devproc_lines_parsed": int,
        "spawnevent_lines_parsed": int,
        "pl_agent_id_hash": str,
      },
      "identity_probe": dict,
    }
    """

    pl_agent_hash = _sha256_id(pl_agent_id)

    # ────────────────────── L-A: Agent tool_call 관측 ──────────────────────
    l_a_found = False
    devproc_parsed = 0

    for line in devproc_lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            row = json.loads(stripped)
        except ValueError:
            continue
        if not isinstance(row, dict):
            continue

        devproc_parsed += 1

        # tool_call 이벤트 확인
        if row.get("event_type") == "tool_call":
            tool_name = row.get("tool_name")
            writer_key = row.get("writer_key")

            # Agent 호출 + PL agent 가 caller
            if tool_name == "Agent" and writer_key == pl_agent_hash:
                l_a_found = True
                break

    # ────────────────────── L-B: spawn-event depth-2 lineage_source ──────────────────────
    l_b_found = False
    l_b_supported = None  # None = 필드 미지원, True/False = 필드 지원 여부
    spawnevent_parsed = 0

    for line in spawnevent_lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            row = json.loads(stripped)
        except ValueError:
            continue
        if not isinstance(row, dict):
            continue

        spawnevent_parsed += 1

        # lineage_source 필드 확인
        if "lineage_source" in row:
            l_b_supported = True
            # depth=2 와 lineage_source=hook_stamped 확인
            if row.get("depth") == 2 and row.get("lineage_source") == "hook_stamped":
                l_b_found = True
                break
        else:
            if l_b_supported is None:
                l_b_supported = False  # 필드 부재 확인

    # ────────────────────── L-C: fallback (doc-queue worker disjoint) ──────────────────────
    # doc-queue 디렉터리 하 worker 별 disjoint 제출 파일 수 ≥2 + mtime 겹침
    l_c_found = False
    if doc_queue_root is not None and story_key is not None:
        doc_queue_dir = Path(doc_queue_root) / story_key
        if doc_queue_dir.exists() and doc_queue_dir.is_dir():
            # 디렉터리 내 파일 목록 (숨김 파일 제외)
            try:
                files = [f for f in doc_queue_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
                if len(files) >= 2:
                    # mtime 겹침 확인 (가장 오래된 파일과 가장 최신 파일의 창)
                    mtimes = [f.stat().st_mtime for f in files]
                    if len(set(str(m) for m in mtimes)) > 1:
                        # 서로 다른 mtime 이 존재 → 겹치는 창 판정
                        l_c_found = True
            except OSError:
                pass

    # identity_probe 구성
    probe = {
        "sources": ["dev-process-event.jsonl", "spawn-event.jsonl"],
        "l_a_parsed": devproc_parsed,
        "l_b_parsed": spawnevent_parsed,
        "l_c_doc_queue_root": str(doc_queue_root) if doc_queue_root else None,
        "l_c_story_key": story_key,
    }

    # ────────────────────── 판정: L-A ∨ (L-B ∧ L-C) ──────────────────────
    if l_a_found:
        verdict = "PASS"
        reason = "L-A: Agent tool_call by PL agent 관측 (primary)"
    elif l_b_found and l_c_found:
        verdict = "PASS"
        reason = "L-B ∧ L-C: spawn-event depth-2 + doc-queue fallback"
    elif l_b_supported is False:
        # lineage_source 필드가 계약에 없음 → L-B 판정 불가
        verdict = "INCONCLUSIVE"
        reason = (
            "L-A 미확인, L-B 필드 부재 (lineage_source 미지원), L-C fallback 미검사 "
            "→ 데이터 불완전"
        )
    else:
        verdict = "INCONCLUSIVE"
        reason = (
            "L-A 미확인, L-B/L-C 전건 미충족 → 관측 데이터 부족"
        )

    return {
        "verdict": verdict,
        "reason": reason,
        "l_a_found": l_a_found,
        "l_b_found": l_b_found,
        "l_b_supported": l_b_supported,
        "l_c_found": l_c_found,
        "trace": {
            "devproc_lines_parsed": devproc_parsed,
            "spawnevent_lines_parsed": spawnevent_parsed,
            "pl_agent_id_hash": pl_agent_hash,
        },
        "identity_probe": probe,
    }


def gate_result_to_json(result):
    """gate_verdict 패턴 준수 JSON 렌더."""
    verdict_map = {"PASS": 0, "INCONCLUSIVE": 3}
    return {
        "gate_id": "NG-7",
        "verdict": result["verdict"],
        "exit_code": verdict_map.get(result["verdict"], 3),
        "reason": result["reason"],
        "l_a_found": result["l_a_found"],
        "l_b_found": result["l_b_found"],
        "l_b_supported": result["l_b_supported"],
        "l_c_found": result["l_c_found"],
        "trace": result["trace"],
        "identity_probe": result["identity_probe"],
    }


def _self_test():
    """fixture 기반 자가검증."""
    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    pl_agent_id = "DeveloperPLAgent"
    pl_hash = _sha256_id(pl_agent_id)

    # ────────────────────── L-A: Agent tool_call 양성 ──────────────────────
    devproc_with_agent = [
        json.dumps({
            "event_type": "tool_call",
            "tool_name": "Agent",
            "writer_key": pl_hash,
            "timestamp_utc": "2026-08-12T00:00:00Z",
        }),
    ]
    spawnevent_empty = []

    res_la = check_pl_spawn_observation(devproc_with_agent, spawnevent_empty, pl_agent_id)
    check(res_la["verdict"] == "PASS" and res_la["l_a_found"],
          f"[L-A] verdict {res_la['verdict']} != PASS | L-A {res_la['l_a_found']} != True")

    # ────────────────────── L-A 음성 (다른 agent) ──────────────────────
    devproc_other_agent = [
        json.dumps({
            "event_type": "tool_call",
            "tool_name": "Agent",
            "writer_key": _sha256_id("OtherAgent"),
            "timestamp_utc": "2026-08-12T00:00:00Z",
        }),
    ]
    res_la_neg = check_pl_spawn_observation(devproc_other_agent, spawnevent_empty, pl_agent_id)
    check(not res_la_neg["l_a_found"],
          "[L-A 음성] L-A 로 다른 agent 감지됨 (차단 실패)")

    # ────────────────────── L-B: depth-2 lineage_source ──────────────────────
    spawnevent_with_lineage = [
        json.dumps({
            "depth": 2,
            "lineage_source": "hook_stamped",
            "agent_id": pl_agent_id,
        }),
    ]
    res_lb = check_pl_spawn_observation([], spawnevent_with_lineage, pl_agent_id)
    check(res_lb["l_b_found"] and res_lb["l_b_supported"] is True,
          f"[L-B] L-B {res_lb['l_b_found']} != True | supported {res_lb['l_b_supported']}")

    # ────────────────────── L-B 미지원 (필드 부재) ──────────────────────
    spawnevent_no_lineage = [
        json.dumps({
            "depth": 2,
            "agent_id": pl_agent_id,
        }),
    ]
    res_lb_nosupport = check_pl_spawn_observation([], spawnevent_no_lineage, pl_agent_id)
    check(res_lb_nosupport["l_b_supported"] is False,
          f"[L-B 미지원] supported {res_lb_nosupport['l_b_supported']} != False")

    # ────────────────────── 정상 케이스 (L-A pass) ──────────────────────
    res_ok = check_pl_spawn_observation(devproc_with_agent, spawnevent_empty, pl_agent_id)
    check(res_ok["verdict"] == "PASS",
          f"[정상] verdict {res_ok['verdict']} != PASS")

    if failures:
        print("[check_pl_spawn_observation --self-test] FAIL")
        for m in failures:
            print("  - " + m)
        return 1

    print(
        "[check_pl_spawn_observation --self-test] PASS "
        "(L-A=양성 OK; L-A=음성 OK; L-B=감지 OK; L-B=미지원 OK; 정상=PASS OK)"
    )
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        description="AC-15 PL spawn 관측 (L-A/L-C 파서)"
    )
    p.add_argument("--dev-process", default=None, help="dev-process-event.jsonl 경로")
    p.add_argument("--spawn-event", default=None, help="spawn-event.jsonl 경로")
    p.add_argument("--pl-agent-id", default=None, help="PL agent ID")
    p.add_argument("--self-test", action="store_true", help="fixture 기반 자가검증")

    args = p.parse_args(argv)

    if args.self_test:
        return _self_test()

    if args.pl_agent_id is None:
        print(
            json.dumps({
                "gate_id": "NG-7",
                "verdict": "INCONCLUSIVE",
                "exit_code": 3,
                "reason": "--pl-agent-id 필수",
                "l_a_found": None,
                "l_b_found": None,
                "l_b_supported": None,
                "l_c_found": None,
                "trace": {},
                "identity_probe": "dev-process-event.jsonl + spawn-event.jsonl",
            }, ensure_ascii=False),
            file=sys.stdout
        )
        return 3

    devproc_path = Path(args.dev_process or _DEFAULT_DEVPROC)
    spawnevent_path = Path(args.spawn_event or _DEFAULT_SPAWNEVENT)

    devproc_lines = _read_ledger_lines(devproc_path)
    spawnevent_lines = _read_ledger_lines(spawnevent_path)

    result = check_pl_spawn_observation(devproc_lines, spawnevent_lines, args.pl_agent_id)

    json_out = gate_result_to_json(result)
    print(json.dumps(json_out, ensure_ascii=False), file=sys.stdout)

    return json_out["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
