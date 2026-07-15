#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tier: [measurement]
# query_dev_process_event.py — dev-process-event-v1 mining/query port (raw typed rows, B/C disjoint)
#
# Carrier: CFP-2687 Phase 2 (구현) / Epic #2686 Story A (선행 substrate)
# SSOT: docs/inter-plugin-contracts/dev-process-event-v1.md §9 (mining/query 진입점) — ADR-155 §결정 7
#
# 책임:
#   - index 원장 `.claude/ledger/dev-process-event.jsonl` (append_dev_process_event.py 가 씀)
#     을 read-only 소비 → filter 통과 **raw typed event rows** 반환.
#   - read-time dedup (event_id — port 소유). optional blob deref (dev_process_blob_store.deref_blob).
#   - B(지표 집계 #2688) / C(verdict 판정 #2689) = **disjoint consumer** — port 하류 무의존.
#     storage 포맷 계약 표면 비노출 (reader port 뒤 격리, drift 봉쇄).
#
# 불변식 (계약 §9 / AC-17 — 절대 위반 금지):
#   - **NO aggregation / NO verdict** — 반환은 raw typed rows 만. "지표 집계 방식"(B)·"게이트
#     판정 규칙"(C) 를 포함하지 않는다 (집계 metric·PASS/FAIL 미산출).
#   - 원장 read-only — IN-PLACE EDIT 절대 금지 (record-only INV, ADR-115 §2).
#   - 0 API call — local I/O only. non-blocking — malformed/empty/부재로도 crash 금지.
#
# ★mining honest-degrade (ADR-119):
#   exact-count / guaranteed-unique 주장 금지. read-time dedup(event_id)는 JSONL append-only
#   (write-time UNIQUE 부재)의 best-effort — `rows_total`/`rows_deduped`/`duplicates_collapsed`
#   를 **관측치**로 emit(query_with_stats). event_id 부재 row 는 canonical row-hash 로 degrade dedup.
#
# 사용:
#   python3 query_dev_process_event.py [--ledger PATH] [--story-key K] [--lane-label L]
#       [--event-type T] [--defect-id ID] [--fix-id ID] [--since ISO] [--until ISO]
#       [--include-blob] [--json]
#   python3 query_dev_process_event.py --self-test
#
# stdlib only (json / hashlib / datetime / argparse / pathlib / sys) — 정규식 미사용 (regex 파싱 경로 부재; ReDoS backtracking 표면 자체가 없음, 별도 반증 대상 아님).

import argparse
import datetime
import hashlib
import json
import os
import sys
from pathlib import Path

# Windows cp949 인코딩 회피 (ADR-061 portability — scripts/lib 관례 재사용)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── blob deref sibling (FROZEN 이름 — 병렬 저작 中, 부재 시 graceful degrade) ──
# dev_process_blob_store.deref_blob(blob_ref) -> bytes | None (BlobDev 소유).
try:
    from dev_process_blob_store import deref_blob as _deref_blob
except Exception:  # pragma: no cover — sibling 미착지 시 graceful
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from dev_process_blob_store import deref_blob as _deref_blob
    except Exception:
        _deref_blob = None


_DEFAULT_LEDGER_REL = Path(".claude") / "ledger" / "dev-process-event.jsonl"

# filter 대상 상관/분류 필드 (계약 §9 입력 단위 — exact-match)
_EXACT_FILTER_KEYS = ("story_key", "lane_label", "event_type", "defect_id", "fix_id")


# ─────────────────────── timestamp parse (UTC Z strict 저장 형식) ────────────────────

def _parse_utc_z(value):
    """dev-process index timestamp_utc = 'YYYY-MM-DDTHH:MM:SS.mmmZ' (UTC Z, ms precision) → aware dt.

    'Z' → '+00:00' 치환 후 fromisoformat (초/ms/µs 소수점 + offset 관용, 정렬 robustness). 실패 시 None.
    """
    if not isinstance(value, str) or not value:
        return None
    s = value.strip()
    try:
        iso = s[:-1] + "+00:00" if s.endswith("Z") else s
        dt = datetime.datetime.fromisoformat(iso)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


# ─────────────────────── dedup key (event_id 우선, row-hash degrade) ─────────────────

def _dedup_key(row):
    """read-time dedup key — event_id 우선. 부재/비정상 → canonical row-hash degrade."""
    eid = row.get("event_id")
    if isinstance(eid, str) and eid:
        return "eid:" + eid
    canonical = json.dumps(row, sort_keys=True, ensure_ascii=False)
    return "row:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ─────────────────────── filter 매칭 ─────────────────────────────────────────────────

def _row_matches(row, filters, since_dt, until_dt):
    """row 가 filter 를 통과하는지 — exact-match(상관/분류) + time-window(timestamp_utc).

    반환: (matched: bool, window_excluded: bool).
    window active 인데 timestamp 파싱 불가/범위 밖 → window_excluded=True (별도 count).
    """
    for k in _EXACT_FILTER_KEYS:
        want = filters.get(k)
        if want is None:
            continue
        if row.get(k) != want:
            return (False, False)

    if since_dt is not None or until_dt is not None:
        ts = _parse_utc_z(row.get("timestamp_utc"))
        if ts is None:
            return (False, True)
        if since_dt is not None and ts < since_dt:
            return (False, True)
        if until_dt is not None and ts > until_dt:
            return (False, True)

    return (True, False)


# ─────────────────────── core query ──────────────────────────────────────────────────

def query_lines(lines, filters=None, since=None, until=None, include_blob=False):
    """JSONL line 시퀀스에서 filter 통과 raw typed rows 반환 + 관측 stats.

    - malformed(비-JSON / dict 아님) → skip + count (raw payload echo 금지).
    - read-time dedup (event_id 우선, row-hash degrade) → duplicates_collapsed.
    - include_blob=True 시 blob_ref 보유 row 에 `_blob`(bytes|None) + `_blob_deref_available` 부착
      (deref 는 반환 row 의 **부가 필드**일 뿐 index 스키마 아님 — 원장 무변경).

    반환: {"rows": [...], "stats": {...}} — ★NO aggregation/verdict (raw rows only, AC-17).
    """
    filters = filters or {}
    since_dt = _parse_utc_z(since) if since else None
    until_dt = _parse_utc_z(until) if until else None

    malformed_skipped = 0
    window_excluded = 0
    filtered_out = 0
    rows_total = 0             # filter 통과 valid dict row (pre-dedup)
    duplicates_collapsed = 0
    seen = set()
    out_rows = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            row = json.loads(stripped)
        except ValueError:
            malformed_skipped += 1
            continue
        if not isinstance(row, dict):
            malformed_skipped += 1
            continue

        matched, excluded = _row_matches(row, filters, since_dt, until_dt)
        if excluded:
            window_excluded += 1
            continue
        if not matched:
            filtered_out += 1
            continue

        rows_total += 1

        key = _dedup_key(row)
        if key in seen:
            duplicates_collapsed += 1
            continue
        seen.add(key)

        if include_blob:
            row = dict(row)  # 복사본 — 원본 mutate 방지
            blob_ref = row.get("blob_ref")
            if blob_ref:
                if _deref_blob is not None:
                    try:
                        row["_blob"] = _deref_blob(blob_ref)
                    except Exception:
                        row["_blob"] = None
                    row["_blob_deref_available"] = True
                else:
                    row["_blob"] = None
                    row["_blob_deref_available"] = False  # sibling 미착지 — honest
        out_rows.append(row)

    rows_deduped = rows_total - duplicates_collapsed
    stats = {
        "rows_total": rows_total,               # ★관측치 — guaranteed-unique 아님 (honest-degrade)
        "rows_deduped": rows_deduped,
        "duplicates_collapsed": duplicates_collapsed,
        "malformed_skipped": malformed_skipped,
        "window_excluded": window_excluded,
        "filtered_out": filtered_out,
        "blob_deref_available": _deref_blob is not None,
        "honesty_note": (
            "read-time dedup 은 event_id 우선(부재 시 row-hash) best-effort — "
            "JSONL write-time UNIQUE 부재. rows_total/rows_deduped/duplicates_collapsed = 관측치, "
            "exact-count/guaranteed-unique 아님. 본 port 는 raw rows 만 — 집계(B)/verdict(C) 미산출."
        ),
    }
    return {"rows": out_rows, "stats": stats}


def _read_ledger_lines(ledger_path):
    """원장 read-only 로드 → line 리스트. 부재/빈 파일 → []. crash 금지."""
    p = Path(ledger_path)
    if not p.exists():
        return []
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return text.splitlines()


def query_file(ledger_path=None, filters=None, since=None, until=None, include_blob=False):
    """파일 경로 기반 query (원장 read-only). 반환 = {"rows": [...], "stats": {...}}."""
    if ledger_path is None:
        proj_dir = os.environ.get("CLAUDE_PROJECT_DIR", "") or "."
        ledger_path = Path(proj_dir) / _DEFAULT_LEDGER_REL
    lines = _read_ledger_lines(ledger_path)
    return query_lines(lines, filters=filters, since=since, until=until, include_blob=include_blob)


# ─────────────────────── public port API (계약 §9) ────────────────────────────────────

def query(ledger_path=None, since=None, until=None, include_blob=False, **filters):
    """mining/query port — filter 통과 **raw typed event rows** 반환 (list[dict]).

    filters = story_key / lane_label / event_type / defect_id / fix_id (exact-match)
              + since / until (time-window on timestamp_utc).
    read-time dedup(event_id) 적용. ★NO aggregation / NO verdict (AC-17) — raw rows only.
    관측 stats 가 필요하면 query_with_stats() 사용 (honest-degrade count).
    """
    return query_file(
        ledger_path=ledger_path, filters=filters, since=since, until=until,
        include_blob=include_blob,
    )["rows"]


def query_with_stats(ledger_path=None, since=None, until=None, include_blob=False, **filters):
    """query() + 관측 stats 동반 반환 → (rows, stats).

    stats = rows_total/rows_deduped/duplicates_collapsed/malformed_skipped/window_excluded
            + honesty_note (exact-count/guaranteed-unique 주장 금지 — mining honest-degrade).
    """
    res = query_file(
        ledger_path=ledger_path, filters=filters, since=since, until=until,
        include_blob=include_blob,
    )
    return res["rows"], res["stats"]


# ─────────────────────── 렌더 (stdout, local only — 0 API call) ───────────────────────

def render(res):
    lines = []
    stats = res["stats"]
    lines.append("=" * 68)
    lines.append("dev-process-event query — raw typed rows (NO aggregation/verdict — AC-17)")
    lines.append("=" * 68)
    lines.append(f"rows_deduped        : {stats['rows_deduped']}")
    lines.append(f"rows_total(pre-dedup): {stats['rows_total']}")
    lines.append(f"duplicates_collapsed: {stats['duplicates_collapsed']}")
    lines.append(f"malformed_skipped   : {stats['malformed_skipped']}")
    lines.append(f"window_excluded     : {stats['window_excluded']}")
    lines.append(f"filtered_out        : {stats['filtered_out']}")
    lines.append(f"blob_deref_available: {stats['blob_deref_available']}")
    lines.append("-" * 68)
    lines.append("HONESTY: " + stats["honesty_note"])
    lines.append("-" * 68)
    for r in res["rows"]:
        lines.append(json.dumps(r, ensure_ascii=False, sort_keys=True))
    lines.append("=" * 68)
    return "\n".join(lines)


# ─────────────────────── self-test (execution-backed, hollow 금지) ─────────────────────

def _self_test():
    """inline synthetic index 로 실제 query 함수 호출 후 관측값 대조."""
    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    def mk(event_type, emit_source, story_key, lane_label, event_id,
           defect_id=None, fix_id=None, blob_ref=None, ts="2026-07-15T10:00:00Z"):
        return json.dumps({
            "event_id": event_id, "schema_version": "dev-process-event-v1",
            "event_type": event_type, "emit_source": emit_source, "timestamp_utc": ts,
            "story_key": story_key, "lane_label": lane_label, "consumer_scope": "wrapper",
            "defect_id": defect_id, "fix_id": fix_id, "blob_ref": blob_ref,
            "redaction_applied": False, "redaction_count": 0, "redaction_rules_fired": [],
            "defect_family": None, "defect_type": None, "time_to_detection": None,
            "detecting_lane": None,
        }, ensure_ascii=False)

    lines = [
        mk("lane_transition", "agent", "CFP-2687", "구현", "e1"),
        mk("verdict", "agent", "CFP-2687", "구현-리뷰", "e2", ts="2026-07-15T11:00:00Z"),
        mk("defect_finding", "agent", "CFP-2687", "설계-리뷰", "e3",
           defect_id="a" * 64, blob_ref="b" * 64, ts="2026-07-15T09:00:00Z"),
        mk("lane_transition", "agent", "CFP-2688", "설계", "e4"),   # 다른 story
        mk("lane_transition", "agent", "CFP-2687", "구현", "e1"),   # e1 중복 (dedup 대상)
        "}{ not json",                                              # malformed
        "[1,2,3]",                                                  # non-dict → malformed
        "",                                                        # 빈 줄 (무시)
    ]

    # ── 케이스 1: filter 無 → 전체(dedup 후) ──
    res_all = query_lines(lines)
    check(res_all["stats"]["rows_total"] == 5,
          f"[c1] rows_total {res_all['stats']['rows_total']} != 5")
    check(res_all["stats"]["duplicates_collapsed"] == 1,
          f"[c1] duplicates_collapsed {res_all['stats']['duplicates_collapsed']} != 1")
    check(res_all["stats"]["rows_deduped"] == 4,
          f"[c1] rows_deduped {res_all['stats']['rows_deduped']} != 4")
    check(res_all["stats"]["malformed_skipped"] == 2,
          f"[c1] malformed_skipped {res_all['stats']['malformed_skipped']} != 2")
    ids = sorted(r["event_id"] for r in res_all["rows"])
    check(ids == ["e1", "e2", "e3", "e4"], f"[c1] dedup 결과 {ids} != e1..e4")

    # ── 케이스 2: story_key filter ──
    rows_2687 = query_lines(lines, filters={"story_key": "CFP-2687"})["rows"]
    check(all(r["story_key"] == "CFP-2687" for r in rows_2687),
          "[c2] story_key filter 누수")
    check(len(rows_2687) == 3, f"[c2] CFP-2687 rows {len(rows_2687)} != 3 (e1,e2,e3)")

    # ── 케이스 3: event_type + lane_label 복합 filter ──
    rows_lt = query_lines(lines, filters={"event_type": "lane_transition",
                                          "story_key": "CFP-2687"})["rows"]
    check(len(rows_lt) == 1 and rows_lt[0]["event_id"] == "e1",
          f"[c3] 복합 filter {[r['event_id'] for r in rows_lt]} != [e1]")

    # ── 케이스 4: time-window ──
    rows_win = query_lines(lines, since="2026-07-15T10:30:00Z")["rows"]
    check(sorted(r["event_id"] for r in rows_win) == ["e2"],
          f"[c4] since window {[r['event_id'] for r in rows_win]} != [e2]")

    # ── 케이스 5: defect_id filter ──
    rows_def = query_lines(lines, filters={"defect_id": "a" * 64})["rows"]
    check(len(rows_def) == 1 and rows_def[0]["event_id"] == "e3",
          "[c5] defect_id filter 실패")

    # ── 케이스 6: include_blob — deref 부재 시 honest available=False ──
    res_blob = query_lines(lines, filters={"event_type": "defect_finding"}, include_blob=True)
    r_blob = res_blob["rows"][0]
    check("_blob_deref_available" in r_blob,
          "[c6] blob 보유 row 에 _blob_deref_available 부재")
    # deref sibling 미착지 환경이면 False + _blob None (honest degrade)
    if _deref_blob is None:
        check(r_blob["_blob_deref_available"] is False and r_blob["_blob"] is None,
              "[c6] sibling 부재인데 honest degrade 아님")

    # ── 케이스 7: public API query() = list[dict] (NO aggregation) ──
    import tempfile
    fd, tmp = tempfile.mkstemp(prefix="devproc-q-selftest-", suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    try:
        before = Path(tmp).read_bytes()
        result = query(ledger_path=tmp, story_key="CFP-2687")
        check(isinstance(result, list) and all(isinstance(r, dict) for r in result),
              "[c7] query() 반환이 list[dict] 아님")
        check(len(result) == 3, f"[c7] query() CFP-2687 len {len(result)} != 3")
        rows_s, stats_s = query_with_stats(ledger_path=tmp)
        check("honesty_note" in stats_s and "exact-count" in stats_s["honesty_note"],
              "[c7] honesty_note 부재/미언급")
        after = Path(tmp).read_bytes()
        check(before == after, "[c7] query 후 원장 byte 변경 (read-only INV 위반)")
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass

    # ── 케이스 8: empty ledger → zero ──
    res_empty = query_lines([])
    check(res_empty["rows"] == [] and res_empty["stats"]["rows_total"] == 0,
          "[c8] empty zero 아님")

    if failures:
        print("[query_dev_process_event --self-test] FAIL")
        for m in failures:
            print("  - " + m)
        return 1

    print(
        "[query_dev_process_event --self-test] PASS "
        f"(filter+dedup OK; window OK; defect_id OK; include_blob honest-degrade OK; "
        f"query()=list[dict] OK; read-only byte-identical OK; empty zero OK; "
        f"blob_deref_available={_deref_blob is not None})"
    )
    return 0


# ─────────────────────── CLI ──────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="dev-process-event-v1 mining/query port — raw typed rows (CFP-2687)"
    )
    p.add_argument("--ledger", default=None,
                   help="dev-process-event.jsonl 경로 (default: .claude/ledger/…)")
    p.add_argument("--story-key", default=None)
    p.add_argument("--lane-label", default=None)
    p.add_argument("--event-type", default=None)
    p.add_argument("--defect-id", default=None)
    p.add_argument("--fix-id", default=None)
    p.add_argument("--since", default=None, help="window 시작 (ISO 8601 UTC Z)")
    p.add_argument("--until", default=None, help="window 종료 (ISO 8601 UTC Z)")
    p.add_argument("--include-blob", action="store_true", help="blob_ref deref 부착 (raw rows 부가)")
    p.add_argument("--json", action="store_true", help="{rows, stats} JSON emit")
    p.add_argument("--self-test", action="store_true", help="execution-backed self-test")
    args = p.parse_args()

    if args.self_test:
        return _self_test()

    filters = {}
    for cli_key, row_key in (("story_key", "story_key"), ("lane_label", "lane_label"),
                             ("event_type", "event_type"), ("defect_id", "defect_id"),
                             ("fix_id", "fix_id")):
        val = getattr(args, cli_key)
        if val is not None:
            filters[row_key] = val

    res = query_file(
        ledger_path=args.ledger, filters=filters, since=args.since, until=args.until,
        include_blob=args.include_blob,
    )
    if args.json:
        print(json.dumps(res, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(render(res))
    # non-blocking advisory — 항상 exit 0 (record-only 측정 채널)
    return 0


if __name__ == "__main__":
    sys.exit(main())
