#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-833 Phase 2 — DialogFidelityAgent effectiveness measurement (ADR-071 Amendment 3)
# ADR-061 §결정 1 thin wrapper pattern (scripts/check-dialog-fidelity-effect.sh SSOT)
#
# 책임:
#   docs/orchestrator-communication-incidents.md ## Incidents 테이블 parse
#   → trigger cell 분류 (backfill / realtime)
#   → A-B baseline delta 계산 (proxy signal — NOT causal effectiveness measure)
#   → monthly-equivalent normalization + sample insufficient sentinel
#   → advisory operational signal 출력 (stdout)
#
# proxy qualification (Change Plan §3.1 / ADR-071 §결정 14):
#   before=backfill / after=realtime collection mode 상이
#   → delta = instrumentation mode change / backfill completeness /
#              reviewer behavior 변화도 반영 가능.
#   advisory operational signal only, not causal effectiveness measure.
#
# Exit codes:
#   0 = PASS (delta 산정 성공 or sample insufficient N/A or bypass)
#   1 = WARN (advisory signal — warning mode, PR merge 미차단)
#   2 = ERROR (file read 실패 등 unexpected)
#
# INV-DM-2: detect-only read-only — file 변경 0, autofix 채널 절대 금지.
# Idempotent invariant: 동일 input → 동일 output.

import sys
import re
import argparse
from pathlib import Path
from datetime import datetime, date, timezone, timedelta
from collections import defaultdict

# Windows console (cp949) 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ─── 상수 ───

# Story-1 merge 기준점: DialogFidelityAgent 도입 이후 = "realtime detect" 시작 기준
# CFP-777 / Story-1 merge commit 577f96f, 2026-05-17 KST
STORY1_MERGE_DATE = date(2026, 5, 17)

# sample insufficient threshold (Change Plan §3.1 — pragmatic noise-floor sentinel)
SAMPLE_THRESHOLD = 3

# realtime trigger 허용 enum
REALTIME_TRIGGERS = frozenset(["layer-3-keyword", "layer-4-n1", "layer-4-m5"])

# backfill marker prefix (trigger cell 시작 문자열)
BACKFILL_MARKER = "backfill"

# proxy qualification 문구 (ADR-058 §결정 3 모달 어휘 금지 — "임시"/"한시적" 금지)
PROXY_NOTICE = (
    "advisory operational signal only, not causal effectiveness measure. "
    "before=backfill / after=realtime collection mode 상이 — "
    "delta reflects instrumentation mode change / backfill completeness / "
    "reviewer behavior changes, not solely DialogFidelityAgent effect."
)

# default incidents file path (repo root 기준)
DEFAULT_INCIDENTS_PATH = Path(__file__).parent.parent.parent / "docs" / "orchestrator-communication-incidents.md"


# ─── 핵심 함수: markdown table parse ───

def parse_incidents_table(text: str) -> list[dict]:
    """
    ## Incidents 마크다운 테이블을 row list 로 parse.
    각 row = dict with keys: iter, timestamp, story_key, pattern_dimension,
                              pattern_summary, trigger, different_dimension_after_halt,
                              escalation_outcome
    헤더/구분자 행 제외. | 로 분리.
    """
    rows = []
    in_table = False
    header_seen = False
    sep_seen = False

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if in_table:
                # 테이블 끝
                break
            continue

        # 헤더 탐지: "iter" column
        if "iter" in stripped.lower() and "timestamp" in stripped.lower():
            in_table = True
            header_seen = True
            continue

        if in_table and not header_seen:
            continue

        # 구분자 행 (---|--- 패턴) 건너뜀
        if re.match(r"^\|[\s\-|]+\|$", stripped):
            sep_seen = True
            continue

        if in_table and header_seen and sep_seen:
            # 데이터 행
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) >= 6:
                rows.append({
                    "iter": cells[0].strip(),
                    "timestamp": cells[1].strip(),
                    "story_key": cells[2].strip(),
                    "pattern_dimension": cells[3].strip(),
                    "pattern_summary": cells[4].strip(),
                    "trigger": cells[5].strip(),
                    "different_dimension_after_halt": cells[6].strip() if len(cells) > 6 else "",
                    "escalation_outcome": cells[7].strip() if len(cells) > 7 else "",
                })

    return rows


# ─── 핵심 함수: trigger cell 분류 ───

def classify_rows(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    rows 를 backfill / realtime 으로 분류.
    - trigger cell 이 'backfill' 로 시작하면 backfill
    - trigger cell 이 REALTIME_TRIGGERS enum 중 하나로 시작하면 realtime
      (예: "layer-4-n1 (active-detect, ...)" 형태도 startswith 로 매핑)
    - 그 외 = 미분류 (backfill 로 안전 처리)
    """
    backfill = []
    realtime = []
    for row in rows:
        trigger = row.get("trigger", "").strip().lower()
        if trigger.startswith(BACKFILL_MARKER):
            backfill.append(row)
        elif any(trigger.startswith(rt) for rt in REALTIME_TRIGGERS):
            realtime.append(row)
        else:
            # 알 수 없는 trigger = 보수적으로 backfill 처리 (advisory only)
            backfill.append(row)
    return backfill, realtime


# ─── 핵심 함수: baseline monthly-equivalent rate 계산 ───

def _parse_timestamp(ts_str: str) -> date | None:
    """timestamp 문자열 → date (KST 기준). 파싱 실패 시 None."""
    ts_str = ts_str.strip()
    # 다양한 포맷 시도
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",      # ISO8601 with tz
        "%Y-%m-%dT%H:%M:%S",        # ISO8601 no tz
        "%Y-%m-%d %H:%M",           # space-separated
        "%Y-%m-%d",                 # date only
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(ts_str[:len(fmt) + 6], fmt)
            return dt.date()
        except ValueError:
            pass
    # 더 유연한 파싱 시도 (앞 10자리 날짜 추출)
    m = re.match(r"(\d{4}-\d{2}-\d{2})", ts_str)
    if m:
        try:
            return date.fromisoformat(m.group(1))
        except ValueError:
            pass
    return None


def compute_baseline_monthly_equivalent(backfill_rows: list[dict]) -> float:
    """
    backfill row 들의 occurrence span 으로 monthly-equivalent rate 계산.
    Change Plan §3.1: span_days = min/max timestamp date 차이 (inclusive).
    rate = len(backfill_rows) / span_days * 30
    span_days = max(1, (max_date - min_date).days + 1)  # inclusive
    """
    if not backfill_rows:
        return 0.0

    dates = []
    for row in backfill_rows:
        d = _parse_timestamp(row.get("timestamp", ""))
        if d:
            dates.append(d)

    if not dates:
        # timestamp parse 실패 시 단순 count / 1month
        return float(len(backfill_rows))

    min_date = min(dates)
    max_date = max(dates)
    span_days = max(1, (max_date - min_date).days + 1)  # inclusive span

    return len(backfill_rows) / span_days * 30


# ─── 핵심 함수: after rate 계산 (month-bucketed) ───

def compute_after_monthly_rate(realtime_rows: list[dict]) -> float:
    """
    realtime row 들의 month-bucketed rate.
    분자 = Story-1 merge 이후 realtime detect row count.
    분모 = measurement window 월 수 (= 1, 1 month rolling).
    현재 구현: 전체 realtime row count / 1 month (1 month rolling window 기준).
    """
    # 1 month rolling window: 현재 realtime row 전체를 1 month 로 환산
    # (single-month bucket — cron monthly, 분모 = 1)
    return float(len(realtime_rows))


# ─── 핵심 함수: A-B delta 계산 ───

def compute_delta(backfill_rows: list[dict], realtime_rows: list[dict]) -> dict:
    """
    A-B baseline delta 계산.
    Returns:
        {
            "status": "insufficient" | "ok" | "advisory",
            "realtime_count": int,
            "backfill_count": int,
            "before_monthly_eq": float,
            "after_monthly_rate": float,
            "delta": float | None,  # after - before (음수 = 감소 = proxy 긍정 신호)
            "note": str,
        }
    """
    realtime_count = len(realtime_rows)
    backfill_count = len(backfill_rows)

    # sample insufficient sentinel (Change Plan §3.1, threshold=3)
    if realtime_count < SAMPLE_THRESHOLD:
        return {
            "status": "insufficient",
            "realtime_count": realtime_count,
            "backfill_count": backfill_count,
            "before_monthly_eq": 0.0,
            "after_monthly_rate": 0.0,
            "delta": None,
            "note": (
                f"N/A — sample insufficient (realtime detect row = {realtime_count} < {SAMPLE_THRESHOLD}). "
                "advisory only. pragmatic noise-floor sentinel: "
                "1-2 row = single-incident high-variance noise. "
                + PROXY_NOTICE
            ),
        }

    before = compute_baseline_monthly_equivalent(backfill_rows)
    after = compute_after_monthly_rate(realtime_rows)
    delta = after - before  # 음수 = after < before = verifier 효과 proxy 신호

    return {
        "status": "ok",
        "realtime_count": realtime_count,
        "backfill_count": backfill_count,
        "before_monthly_eq": round(before, 2),
        "after_monthly_rate": round(after, 2),
        "delta": round(delta, 2),
        "note": PROXY_NOTICE,
    }


# ─── 출력 포매터 ───

def format_output(result: dict) -> str:
    lines = [
        "=== DialogFidelityAgent Effectiveness Measurement (proxy signal) ===",
        f"status          : {result['status']}",
        f"backfill rows   : {result['backfill_count']}",
        f"realtime rows   : {result['realtime_count']}",
    ]

    if result["status"] == "insufficient":
        lines.append(f"delta           : N/A")
    else:
        lines.append(f"before(monthly-eq): {result['before_monthly_eq']:.2f} incidents/month")
        lines.append(f"after(monthly)  : {result['after_monthly_rate']:.2f} incidents/month")
        lines.append(f"delta           : {result['delta']:+.2f} (음수 = verifier 효과 proxy 신호)")

    lines.append("")
    lines.append(f"proxy notice: {result['note']}")
    return "\n".join(lines)


# ─── 메인 ───

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="DialogFidelityAgent effectiveness measurement (ADR-071 Amendment 3 / CFP-833)"
    )
    parser.add_argument(
        "--incidents-file",
        type=Path,
        default=DEFAULT_INCIDENTS_PATH,
        help=f"communication-incidents.md 경로 (기본: {DEFAULT_INCIDENTS_PATH})",
    )
    args = parser.parse_args(argv)

    incidents_file: Path = args.incidents_file

    # file 존재 확인
    if not incidents_file.exists():
        print(
            f"ERROR: incidents file not found: {incidents_file}",
            file=sys.stderr
        )
        sys.exit(2)

    # 파일 read (read-only, INV-DM-2)
    try:
        text = incidents_file.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"ERROR: file read failed: {e}", file=sys.stderr)
        sys.exit(2)

    # parse + 분류
    rows = parse_incidents_table(text)
    backfill, realtime = classify_rows(rows)

    # delta 계산
    result = compute_delta(backfill_rows=backfill, realtime_rows=realtime)

    # 출력
    print(format_output(result))

    # exit code (warning mode — advisory, PR merge 미차단)
    # 0 = PASS (delta 산정 성공 or sample insufficient N/A)
    # 1 = WARN (advisory: delta >= 0, 즉 after >= before = verifier 효과 없음 proxy 신호)
    if result["status"] == "insufficient":
        sys.exit(0)
    elif result["delta"] is not None and result["delta"] >= 0:
        # after >= before = 감소 신호 없음 (advisory warning, PR block 안 함)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
