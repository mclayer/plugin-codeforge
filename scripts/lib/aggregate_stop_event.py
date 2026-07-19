#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tier: [measurement]
# aggregate_stop_event.py — L5 stop-event 원장 aggregate (record-only, strict measurement)
#
# Carrier: CFP-2573 Phase 2 (구현) — ADR-144 §결정 5 (L5, GAP-7 실체 = aggregate 부재)
# SSOT: docs/inter-plugin-contracts/stop-event-v1.md §5.1 (v1.2)
#
# 책임:
#   - 실 구현 원장 `.claude/ledger/stop-event.jsonl` (5-field JSONL, append_stop_event.py 가 씀)
#     을 read-only 소비 → per-reason_class count + 부당/정당 ratio 산출.
#   - reason_class 자동분류 불가(원장 = stop_reason free-form) → classification-map sidecar
#     (PMO retro artifact) 有 → ratio / 無 → per-stop_reason frequency honest degrade.
#   - row-hash dedup (canonical JSON sort_keys → sha256; event_id 부재 forward-compat).
#
# 불변식 (binding):
#   - tier = [measurement] STRICT record-only — "측정 ≠ 분류". 인과 주장 금지
#     ("10:2 실측" / "telemetry 가 stop 을 줄인다" 절대 금지 — 빈도 측정만).
#   - 0 API call (ADR-163 §결정 8) — local I/O only. external service 호출 절대 금지.
#   - 원장 read-only — IN-PLACE EDIT 절대 금지 (record-only INV, ADR-115 §2 / ADR-072 disjoint).
#   - non-blocking — malformed / empty / 부재 로도 crash 금지, aggregate exit 0.
#
# 사용:
#   python3 aggregate_stop_event.py [--ledger PATH] [--classification-map PATH]
#                                   [--since ISO] [--until ISO] [--json]
#   python3 aggregate_stop_event.py --self-test
#
# stdlib only (json / hashlib / datetime / argparse / pathlib / sys). ReDoS-safe (regex 미사용).

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

# Windows cp949 인코딩 회피 (ADR-061 portability — 기존 scripts/lib 관례 재사용)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ─────────────────────── 상수 (stop-event-v1 §3.4 reason_class 4-enum) ───────────────

_DEFAULT_LEDGER_REL = Path(".claude") / "ledger" / "stop-event.jsonl"

# 부당 (policy_violation*) — stop-event-v1 §5.1
_ILLEGIT = ("policy_violation", "policy_violation_rate_limit_induced")
# 정당 (user_stop_legitimate · decider_escalation_required) — stop-event-v1 §5.1
_LEGIT = ("user_stop_legitimate", "decider_escalation_required")
# reason_class closed enum (§3.4) — deterministic 0-fill 순서 보존용 tuple
_REASON_CLASS_ENUM = _ILLEGIT + _LEGIT
_ENUM_SET = frozenset(_REASON_CLASS_ENUM)

# ★HONESTY (binding) — stop-event-v1 §5.1: all-unclassified 시 emit 의무 문구
_HONESTY_MEASURE_NEQ_CLASSIFY = (
    "분류 없인 정량 불가 (측정 ≠ 분류) — stop_reason frequency 는 측정치일 뿐 "
    "정당/부당 분류가 아님. 분류는 PMO retro classification-map sidecar 로만 충당."
)
_HONESTY_TIER = (
    "[measurement] tier STRICT — 빈도 측정만. 인과 주장 금지 "
    "(telemetry 가 stop 을 줄인다 / 10:2 실측 등)."
)
_HONESTY_DEDUP_UNDERCOUNT = (
    "row-hash dedup 은 동일-초 별개 이벤트를 병합할 수 있음 → exact-count 아님 "
    "(under-count 가능). rows_total / rows_deduped / duplicates_collapsed 함께 참조."
)


# ─────────────────────── KST 헬퍼 (append_stop_event._kst_now 관례 재사용) ────────────

def _kst_now_iso() -> str:
    """KST ISO 8601 타임스탬프 (ADR-079 §결정 1 display layer KST). 관례 재사용, 신규 아님."""
    utc_now = datetime.datetime.now(tz=datetime.timezone.utc)
    kst = datetime.timezone(datetime.timedelta(hours=9))
    return utc_now.astimezone(kst).strftime("%Y-%m-%dT%H:%M:%S+09:00")


def _parse_iso_aware(value):
    """
    tz-aware ISO 8601 parse (window / timestamp — 외부 NTP 무관, 로컬 tz).
    naive 입력은 KST(+09:00) 로 간주해 aware 로 승격. parse 실패 시 None.
    """
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
    return dt


# ─────────────────────── dedup (canonical JSON → sha256) ──────────────────────────────

def _row_hash(row: dict) -> str:
    """canonical JSON (sort_keys) → sha256 (event_id 부재 대응 forward-compat + canonicalization)."""
    canonical = json.dumps(row, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ─────────────────────── classification-map sidecar ───────────────────────────────────

def load_classification_map(path):
    """
    optional classification-map sidecar 로드 → {stop_reason: reason_class} dict.
    형식 = JSON object. 부재/malformed → None (honest degrade, crash 금지).
    reason_class enum 외 값은 무시(불량 매핑 주입 차단).
    """
    if path is None:
        return None
    p = Path(path)
    if not p.exists():
        return None
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(raw, dict):
        return None
    cmap = {}
    for k, v in raw.items():
        if isinstance(k, str) and isinstance(v, str) and v in _ENUM_SET:
            cmap[k] = v
    return cmap if cmap else {}


# ─────────────────────── reason_class 해석 ────────────────────────────────────────────

def _resolve_reason_class(row: dict, classification_map):
    """
    reason_class 해석 우선순위:
      1) row 내 native reason_class (18-field forward-compat) — enum 유효 시
      2) classification_map[stop_reason] (sidecar)
      3) None (unclassified)
    """
    native = row.get("reason_class")
    if isinstance(native, str) and native in _ENUM_SET:
        return native
    if classification_map:
        sr = row.get("stop_reason")
        if isinstance(sr, str):
            mapped = classification_map.get(sr)
            if mapped in _ENUM_SET:
                return mapped
    return None


# ─────────────────────── core aggregate ──────────────────────────────────────────────

def aggregate_lines(lines, classification_map=None, since=None, until=None,
                    ledger_path=None, classification_map_path=None):
    """
    JSONL line 시퀀스를 aggregate → report dict.

    - malformed (비-JSON / dict 아님) → skip + count (raw payload echo 금지, count 만).
    - 빈 줄 → 무시 (malformed 아님).
    - row-hash dedup → duplicates_collapsed.
    - window (since/until) active 시 tz-aware timestamp_kst 필터.
    - classification_map 有 → per-reason_class count + ratio / 無 → frequency honest degrade.
    """
    since_dt = _parse_iso_aware(since) if since else None
    until_dt = _parse_iso_aware(until) if until else None
    window_active = since_dt is not None or until_dt is not None

    malformed_skipped = 0
    rows_total = 0            # window 통과 valid dict row (pre-dedup)
    duplicates_collapsed = 0
    window_excluded = 0
    seen_hashes = set()

    reason_class_counts = {c: 0 for c in _REASON_CLASS_ENUM}
    reason_class_counts["unclassified"] = 0
    stop_reason_frequency = {}

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

        # window 필터 (active 시): tz-aware parse. unparseable/미포함 → 제외 + count.
        if window_active:
            ts = _parse_iso_aware(row.get("timestamp_kst"))
            if ts is None:
                window_excluded += 1
                continue
            if since_dt is not None and ts < since_dt:
                window_excluded += 1
                continue
            if until_dt is not None and ts > until_dt:
                window_excluded += 1
                continue

        rows_total += 1

        # row-hash dedup
        h = _row_hash(row)
        if h in seen_hashes:
            duplicates_collapsed += 1
            continue
        seen_hashes.add(h)

        # stop_reason frequency (항상 측정)
        sr = row.get("stop_reason")
        sr_key = sr if isinstance(sr, str) else "<missing>"
        stop_reason_frequency[sr_key] = stop_reason_frequency.get(sr_key, 0) + 1

        # reason_class 분류
        rc = _resolve_reason_class(row, classification_map)
        if rc is None:
            reason_class_counts["unclassified"] += 1
        else:
            reason_class_counts[rc] += 1

    rows_deduped = rows_total - duplicates_collapsed

    illegitimate_total = sum(reason_class_counts[c] for c in _ILLEGIT)
    legitimate_total = sum(reason_class_counts[c] for c in _LEGIT)
    classified_total = illegitimate_total + legitimate_total
    unclassified_total = reason_class_counts["unclassified"]

    if classified_total > 0:
        ratio = f"{illegitimate_total}:{legitimate_total}"
    else:
        ratio = "N/A (분류 없음 — classification-map 부재/미매칭)"

    # honesty_notes — binding emit 규칙
    honesty_notes = [_HONESTY_TIER, _HONESTY_DEDUP_UNDERCOUNT]
    if classification_map is None or unclassified_total > 0 or classified_total == 0:
        honesty_notes.insert(0, _HONESTY_MEASURE_NEQ_CLASSIFY)

    report = {
        "schema_note": "stop-event-v1 §5.1 aggregate (v1.2) — tier [measurement] record-only",
        "generated_at_kst": _kst_now_iso(),
        "ledger_path": str(ledger_path) if ledger_path is not None else None,
        "classification_map_path": (
            str(classification_map_path) if classification_map_path is not None else None
        ),
        "classification_map_present": classification_map is not None,
        "window": (
            {"since": since, "until": until} if window_active else None
        ),
        "rows_total": rows_total,
        "rows_deduped": rows_deduped,
        "duplicates_collapsed": duplicates_collapsed,
        "malformed_skipped": malformed_skipped,
        "window_excluded": window_excluded,
        "reason_class_counts": reason_class_counts,
        "stop_reason_frequency": stop_reason_frequency,
        "classified_total": classified_total,
        "unclassified_total": unclassified_total,
        "illegitimate_total": illegitimate_total,
        "legitimate_total": legitimate_total,
        "ratio_illegitimate_to_legitimate": ratio,
        "honesty_notes": honesty_notes,
    }
    return report


def _read_ledger_lines(ledger_path: Path):
    """원장 read-only 로드 → line 리스트. 부재/빈 파일 → [] (zero-count). crash 금지."""
    if not ledger_path.exists():
        return []
    try:
        text = ledger_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return text.splitlines()


def aggregate_file(ledger_path, classification_map=None, since=None, until=None,
                   classification_map_path=None):
    """파일 경로 기반 aggregate (원장 read-only — IN-PLACE EDIT 절대 없음)."""
    lp = Path(ledger_path)
    lines = _read_ledger_lines(lp)
    return aggregate_lines(
        lines,
        classification_map=classification_map,
        since=since,
        until=until,
        ledger_path=lp,
        classification_map_path=classification_map_path,
    )


# ─────────────────────── 렌더 (stdout, local only — 0 API call) ───────────────────────

def render_report(report: dict) -> str:
    lines = []
    lines.append("=" * 68)
    lines.append("stop-event 원장 aggregate — tier [measurement] (record-only)")
    lines.append("=" * 68)
    lines.append(f"ledger            : {report['ledger_path']}")
    lines.append(f"classification-map: {report['classification_map_path']}"
                 f" (present={report['classification_map_present']})")
    if report["window"]:
        lines.append(f"window            : since={report['window']['since']} "
                     f"until={report['window']['until']} "
                     f"(excluded={report['window_excluded']})")
    lines.append(f"generated_at_kst  : {report['generated_at_kst']}")
    lines.append("-" * 68)
    lines.append(f"rows_total          : {report['rows_total']}")
    lines.append(f"rows_deduped        : {report['rows_deduped']}")
    lines.append(f"duplicates_collapsed: {report['duplicates_collapsed']}")
    lines.append(f"malformed_skipped   : {report['malformed_skipped']}")
    lines.append("-" * 68)
    lines.append("reason_class_counts:")
    for c in _REASON_CLASS_ENUM:
        lines.append(f"  {c:<38}: {report['reason_class_counts'][c]}")
    lines.append(f"  {'unclassified':<38}: {report['reason_class_counts']['unclassified']}")
    lines.append("-" * 68)
    lines.append(f"classified_total   : {report['classified_total']}")
    lines.append(f"unclassified_total : {report['unclassified_total']}")
    lines.append(f"부당(illegitimate) : {report['illegitimate_total']}")
    lines.append(f"정당(legitimate)   : {report['legitimate_total']}")
    lines.append(f"ratio 부당:정당     : {report['ratio_illegitimate_to_legitimate']}")
    lines.append("-" * 68)
    lines.append("stop_reason_frequency (측정치 — 분류 아님):")
    if report["stop_reason_frequency"]:
        for reason, cnt in sorted(report["stop_reason_frequency"].items(),
                                  key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"  {reason:<38}: {cnt}")
    else:
        lines.append("  (empty — zero-count)")
    lines.append("-" * 68)
    lines.append("HONESTY:")
    for note in report["honesty_notes"]:
        lines.append(f"  - {note}")
    lines.append("=" * 68)
    return "\n".join(lines)


# ─────────────────────── self-test (execution-backed, hollow 금지) ─────────────────────

def _self_test() -> int:
    """
    inline synthetic mixed ledger 로 실제 aggregate 함수 호출 후 관측값 대조.
    count 하드코딩 금지 — composition spec 에서 expected 를 산출 + 2-fixture cross-run falsify.
    mutation → RED discriminating (classification flip → count/ratio 변화 / ledger-mutate → INV 위반).
    """
    import tempfile

    # composition: (stop_reason, expected_class_with_map, repeat)
    #   vague_pause×3 / legit×2 / escalation×1 + legacy(무매핑)×2 = 8 valid
    comp = [
        ("stop_vague_pause", "policy_violation", 3),
        ("stop_user_complete", "user_stop_legitimate", 2),
        ("stop_escalation", "decider_escalation_required", 1),
        ("stop_legacy_a", None, 1),   # legacy 5-field, map 미포함 → unclassified
        ("stop_legacy_b", None, 1),   # legacy 5-field, map 미포함 → unclassified
    ]

    def _build_rows(spec):
        # 각 row 를 distinct 하게 생성 (session_id 에 uniq index) — 동일-초 별개 이벤트를
        # row-hash 가 병합하지 않도록. dedup 테스트는 별도로 byte-identical row 사용.
        rows = []
        uniq = 0
        for sr, _cls, rep in spec:
            for _ in range(rep):
                rows.append({
                    "timestamp_kst": "2026-07-05T10:00:00+09:00",
                    "hook_source": "stop",
                    "hook_decision": "record-only",
                    "session_id": f"sess-selftest-{uniq}",
                    "stop_reason": sr,
                })
                uniq += 1
        return rows

    def _expected_class_counts(spec, use_map):
        exp = {c: 0 for c in _REASON_CLASS_ENUM}
        exp["unclassified"] = 0
        for _sr, cls, rep in spec:
            key = cls if (use_map and cls is not None) else "unclassified"
            exp[key] += rep
        return exp

    # classification-map = composition 에서 유도 (하드코딩 아님)
    cmap = {sr: cls for sr, cls, _rep in comp if cls is not None}

    rows_a = _build_rows(comp)
    malformed_line = "}{ this is not json ::"           # malformed × 1
    non_dict_line = "[1, 2, 3]"                          # JSON 이나 dict 아님 → malformed
    lines_a = [json.dumps(r, ensure_ascii=False) for r in rows_a]
    lines_a_with_bad = list(lines_a) + [malformed_line, non_dict_line, ""]  # +빈 줄(무시)

    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    # ── 케이스 1: classification-map 有 → per-class count + ratio ──
    rep1 = aggregate_lines(lines_a_with_bad, classification_map=cmap)
    exp1 = _expected_class_counts(comp, use_map=True)
    for c in list(_REASON_CLASS_ENUM) + ["unclassified"]:
        check(
            rep1["reason_class_counts"][c] == exp1[c],
            f"[map有] reason_class[{c}] {rep1['reason_class_counts'][c]} != expected {exp1[c]}",
        )
    exp_illeg = sum(exp1[c] for c in _ILLEGIT)
    exp_leg = sum(exp1[c] for c in _LEGIT)
    check(rep1["illegitimate_total"] == exp_illeg,
          f"[map有] illegitimate {rep1['illegitimate_total']} != {exp_illeg}")
    check(rep1["legitimate_total"] == exp_leg,
          f"[map有] legitimate {rep1['legitimate_total']} != {exp_leg}")
    check(rep1["ratio_illegitimate_to_legitimate"] == f"{exp_illeg}:{exp_leg}",
          f"[map有] ratio {rep1['ratio_illegitimate_to_legitimate']} != {exp_illeg}:{exp_leg}")
    check(rep1["malformed_skipped"] == 2,
          f"[map有] malformed_skipped {rep1['malformed_skipped']} != 2")
    check(rep1["rows_total"] == len(rows_a),
          f"[map有] rows_total {rep1['rows_total']} != {len(rows_a)}")
    check(rep1["unclassified_total"] == exp1["unclassified"],
          f"[map有] unclassified {rep1['unclassified_total']} != {exp1['unclassified']}")

    # ── 케이스 2: classification-map 無 → all-unclassified + honesty 서술 present ──
    rep2 = aggregate_lines(lines_a_with_bad, classification_map=None)
    check(rep2["classified_total"] == 0,
          f"[map無] classified_total {rep2['classified_total']} != 0")
    check(rep2["unclassified_total"] == len(rows_a),
          f"[map無] unclassified {rep2['unclassified_total']} != {len(rows_a)}")
    check(rep2["ratio_illegitimate_to_legitimate"].startswith("N/A"),
          f"[map無] ratio 미 N/A: {rep2['ratio_illegitimate_to_legitimate']}")
    honesty_joined = " ".join(rep2["honesty_notes"])
    check("측정 ≠ 분류" in honesty_joined,
          "[map無] honesty '측정 ≠ 분류' 서술 부재")
    # frequency 측정치 정합
    check(rep2["stop_reason_frequency"].get("stop_vague_pause") == 3,
          f"[map無] freq[vague] {rep2['stop_reason_frequency'].get('stop_vague_pause')} != 3")

    # ── dedup: 동일 row 2회 → duplicates_collapsed ≥ 1 ──
    dup_row = json.dumps(rows_a[0], ensure_ascii=False)
    rep_dup = aggregate_lines([dup_row, dup_row], classification_map=cmap)
    check(rep_dup["duplicates_collapsed"] >= 1,
          f"[dedup] duplicates_collapsed {rep_dup['duplicates_collapsed']} < 1")
    check(rep_dup["rows_deduped"] == 1,
          f"[dedup] rows_deduped {rep_dup['rows_deduped']} != 1")

    # ── 2-fixture cross-run falsify (하드코딩 방어): B = A + vague 1개 → policy_violation +1 ──
    comp_b = comp + [("stop_vague_pause", "policy_violation", 1)]
    lines_b = [json.dumps(r, ensure_ascii=False) for r in _build_rows(comp_b)]
    rep_b = aggregate_lines(lines_b, classification_map=cmap)
    delta = rep_b["reason_class_counts"]["policy_violation"] - rep1["reason_class_counts"]["policy_violation"]
    check(delta == 1,
          f"[cross-run] policy_violation delta {delta} != 1 (하드코딩 의심)")

    # ── record-only INV: 파일 기반 aggregate 후 원장 byte-identical ──
    tmp = None
    try:
        fd, tmp_path = tempfile.mkstemp(prefix="stop-event-selftest-", suffix=".jsonl")
        import os
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("\n".join(lines_a_with_bad))
        tmp = Path(tmp_path)
        before = tmp.read_bytes()
        _ = aggregate_file(tmp, classification_map=cmap)
        after = tmp.read_bytes()
        check(before == after, "[record-only] aggregate 후 원장 byte 변경됨 (INV 위반)")
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()

    # ── empty ledger → zero-count ──
    rep_empty = aggregate_lines([], classification_map=None)
    check(rep_empty["rows_total"] == 0 and rep_empty["malformed_skipped"] == 0,
          "[empty] zero-count 아님")

    if failures:
        print("[aggregate_stop_event --self-test] FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(
        "[aggregate_stop_event --self-test] PASS "
        f"(map有: policy_violation={rep1['reason_class_counts']['policy_violation']} "
        f"user_stop_legitimate={rep1['reason_class_counts']['user_stop_legitimate']} "
        f"decider_escalation_required={rep1['reason_class_counts']['decider_escalation_required']} "
        f"unclassified={rep1['unclassified_total']} ratio={rep1['ratio_illegitimate_to_legitimate']} "
        f"malformed={rep1['malformed_skipped']}; "
        f"map無: all-unclassified={rep2['unclassified_total']} ratio={rep2['ratio_illegitimate_to_legitimate']}; "
        f"dedup collapsed={rep_dup['duplicates_collapsed']}; cross-run delta=+1; record-only byte-identical OK)"
    )
    return 0


# ─────────────────────── CLI ──────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="stop-event 원장 aggregate — tier [measurement] record-only (CFP-2573)"
    )
    parser.add_argument(
        "--ledger",
        default=str(_DEFAULT_LEDGER_REL),
        help="stop-event.jsonl 경로 (default: .claude/ledger/stop-event.jsonl)",
    )
    parser.add_argument(
        "--classification-map",
        default=None,
        help="optional PMO retro sidecar (JSON {stop_reason: reason_class}) — 有 시 ratio",
    )
    parser.add_argument("--since", default=None, help="window 시작 (ISO 8601, tz-aware/naive=KST)")
    parser.add_argument("--until", default=None, help="window 종료 (ISO 8601, tz-aware/naive=KST)")
    parser.add_argument("--json", action="store_true", help="report 를 JSON 으로 emit")
    parser.add_argument("--self-test", action="store_true", help="execution-backed self-test")
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    cmap = load_classification_map(args.classification_map)
    report = aggregate_file(
        args.ledger,
        classification_map=cmap,
        since=args.since,
        until=args.until,
        classification_map_path=args.classification_map,
    )

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_report(report))
    # non-blocking advisory — 항상 exit 0 (record-only 측정 채널)
    return 0


if __name__ == "__main__":
    sys.exit(main())
