#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# replay_spawn_event.py — spawn-event-v1 replay 재구성 (read-only aggregate)
#
# Carrier: CFP-2393 Phase 2 (구현) / Epic CFP-2391 S3
# 출처: oh-my-claudecode (MIT, https://github.com/Yeachan-Heo/oh-my-claudecode)
#       — agent-replay-*.jsonl 경과초 keyed + replay event 종류(agent_start/agent_stop/
#       tool/file_touch/mode_change) 차용. enforcement 는 비-차용 (측정·관측만).
#
# 책임:
#   - 기존 ledger(spawn-event.jsonl) read → elapsed_seconds keyed 시간순 merge → replay 재구성.
#   - event_type 별 정렬 + parent_event_id chain 으로 nested spawn 트리 재구성.
#   - read-time dedup (deterministic event_id 중복 제거 — JSONL append-only, DB UNIQUE 부재 OK).
#   - 새 저장계층 미신설 (read-only aggregate — contract Phase 2 scope).
#
# 불변식:
#   - 0 API call, local read only.
#   - graceful: ledger 부재 → 빈 결과 + exit 0.
#   - elapsed_seconds = replay 정렬 key (절대 timestamp 와 별개 — contract §2).
#
# 사용:
#   python3 replay_spawn_event.py [--ledger-path <abs>] [--story-key CFP-2393]
#       [--format json|table]
#
# Exit codes:
#   0 = 성공 (빈 결과 포함 — graceful)
#   2 = setup error (ledger path 디렉터리 등 비정상 — 단 부재는 graceful 0)

import argparse
import json
import os
import sys
from pathlib import Path

# Windows cp949 인코딩 회피 (ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


_LEDGER_BASENAME = "spawn-event.jsonl"
_DEFAULT_PARENT_REL = os.path.join(".claude", "ledger")

# event_type 정렬 우선순위 (동일 elapsed_seconds tie-break — 재구성 가독성)
_EVENT_TYPE_ORDER = {
    "agent_start": 0,
    "mode_change": 1,
    "tool": 2,
    "file_touch": 3,
    "agent_stop": 4,
}


def _resolve_ledger_path(ledger_path_arg):
    """ledger path 결정 — append_spawn_event 와 동일 default 규칙."""
    if ledger_path_arg:
        return Path(ledger_path_arg)
    proj_dir = os.environ.get("CLAUDE_PROJECT_DIR", "") or "."
    return Path(proj_dir) / _DEFAULT_PARENT_REL / _LEDGER_BASENAME


def _read_ledger(ledger_path):
    """JSONL ledger read → list of row dict. graceful (부재/깨진 line skip).

    Returns list[dict]. 부재 → [].
    """
    rows = []
    if not ledger_path.exists():
        return rows
    try:
        text = ledger_path.read_text(encoding="utf-8")
    except OSError:
        return rows
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue  # 깨진 line skip (graceful)
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def _dedup_by_event_id(rows):
    """read-time dedup — deterministic event_id 중복 제거 (first-wins).

    JSONL append-only 라 at-least-once 재시도 시 동일 event_id 중복 가능 →
    aggregate/replay 시점 dedup (contract §3 idempotency.rule).
    """
    seen = set()
    deduped = []
    for row in rows:
        eid = row.get("event_id")
        if eid is None:
            deduped.append(row)  # event_id 없는 row 는 dedup 불가 — 보존
            continue
        if eid in seen:
            continue
        seen.add(eid)
        deduped.append(row)
    return deduped


def _filter_story(rows, story_key):
    """story_key filter (지정 시)."""
    if not story_key:
        return rows
    return [r for r in rows if r.get("story_key") == story_key]


def _sort_key(row):
    """elapsed_seconds keyed 시간순 정렬 key (절대 timestamp 와 별개).

    elapsed_seconds None → 후순위(무한대 근사). event_type 으로 tie-break.
    """
    es = row.get("elapsed_seconds")
    es_key = es if isinstance(es, (int, float)) else float("inf")
    et = row.get("event_type")
    et_key = _EVENT_TYPE_ORDER.get(et, 99)
    return (es_key, et_key)


def _build_spawn_tree(rows):
    """parent_event_id chain 으로 nested spawn 트리 재구성.

    Returns dict {root_event_ids: [...], children: {parent_event_id: [child event_id, ...]}}.
    parent_event_id == None → root spawn.
    """
    children = {}
    roots = []
    known_ids = {r.get("event_id") for r in rows if r.get("event_id")}
    for row in rows:
        eid = row.get("event_id")
        parent = row.get("parent_event_id")
        if parent is None or parent not in known_ids:
            roots.append(eid)
        else:
            children.setdefault(parent, []).append(eid)
    return {"roots": roots, "children": children}


def _emit_json(sorted_rows, tree):
    """replay 결과 JSON 출력 (stdout)."""
    payload = {
        "replay_event_count": len(sorted_rows),
        "events": sorted_rows,
        "spawn_tree": tree,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _emit_table(sorted_rows):
    """replay 결과 표 출력 (stdout — 사람 가독)."""
    if not sorted_rows:
        print("replay-spawn-event: 0 events (빈 ledger 또는 filter 결과 없음)")
        return
    header = "elapsed_s | event_type | lane | agent_type | attribution | event_id(12)"
    print(header)
    print("-" * len(header))
    for row in sorted_rows:
        es = row.get("elapsed_seconds")
        es_s = ("%.1f" % es) if isinstance(es, (int, float)) else "—"
        eid = (row.get("event_id") or "")[:12]
        print(
            "%s | %s | %s | %s | %s | %s"
            % (
                es_s,
                row.get("event_type", "—"),
                row.get("lane_label", "—"),
                row.get("agent_type", "—"),
                row.get("attribution_confidence", "—"),
                eid,
            )
        )
    print("")
    print("replay-spawn-event: %d events (elapsed_seconds keyed)" % len(sorted_rows))


def cmd_replay(args):
    ledger_path = _resolve_ledger_path(args.ledger_path)

    rows = _read_ledger(ledger_path)
    rows = _dedup_by_event_id(rows)
    rows = _filter_story(rows, args.story_key)
    sorted_rows = sorted(rows, key=_sort_key)
    tree = _build_spawn_tree(sorted_rows)

    if args.format == "json":
        _emit_json(sorted_rows, tree)
    else:
        _emit_table(sorted_rows)

    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="spawn-event-v1 replay 재구성 (CFP-2393 Phase 2 — read-only aggregate)"
    )
    parser.add_argument("--ledger-path", default="",
                        help="spawn-event.jsonl 경로 (default: ${CLAUDE_PROJECT_DIR}/.claude/ledger/...)")
    parser.add_argument("--story-key", default="",
                        help="story_key filter (지정 시 해당 Story event 만)")
    parser.add_argument("--format", default="table", choices=["json", "table"],
                        help="출력 형식 (default table)")
    args = parser.parse_args()
    cmd_replay(args)


if __name__ == "__main__":
    main()
