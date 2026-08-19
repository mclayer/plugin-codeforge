#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# reconcile_429_lease.py — 429 subagent concurrency lease reconciliation
#
# Carrier: CFP-2967 Phase 2 (workerC — lease acquire/release + reconcile 4-status)
#
# 책임:
#   - 만료 및 reconcile 4-status 보고 (no_data / aligned / orphan_expired / stop_without_lease)
#   - 미매칭 lease age 분포 산출 (TTL 미확정 Phase A — age 분포만 보고)
#   - read-time 만료 (읽기만 함, 쓰기 없음 = crash-safe)
#   - 0 API call, stdlib only
#
# 사용:
#   python3 reconcile_429_lease.py [--ledger-dir <path>] [--stop-event-file <path>]
#
# 출력:
#   JSON 보고서(stdout): {
#       "status": "aligned|orphan_expired|stop_without_lease|no_data",
#       "active_leases": <count>,
#       "matching_stops": <count>,
#       "orphaned_leases": <count>,
#       "orphaned_ages_seconds": [<age1>, <age2>, ...],
#       "age_min_seconds": <min_age>,
#       "age_max_seconds": <max_age>,
#       "age_mean_seconds": <mean_age>,
#       "timestamp": "<ISO8601 UTC Z>"
#   }
#
# 4-status 정의:
#   - no_data: 파일 없음 / lease 0 / stop-event 0 (측정 불가)
#   - aligned: active_leases <= matching_stops (정상 상태 — 획득한 만큼 해제)
#   - orphan_expired: active_leases > 0 ∧ age > TTL (미해제 → 만료로 흡수)
#   - stop_without_lease: stop-event > 0 ∧ no lease 존재 (resume 증거)

import argparse
import datetime
import json
import os
import statistics
import sys
from pathlib import Path


def _utc_now_z() -> str:
    """UTC ISO 8601 타임스탬프 (UTC Z strict)."""
    utc_now = datetime.datetime.now(tz=datetime.timezone.utc)
    return utc_now.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_lease_file(lease_file: Path) -> dict:
    """lease 파일 파싱.

    성공: {"agent_id": "...", "timestamp": "...", "renewed_at": "..."}
    실패: None
    """
    try:
        with open(lease_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _parse_stop_event_file(stop_event_file: Path) -> list:
    """stop-event.jsonl 파싱 (행단위).

    각 행: {"timestamp_kst": "...", "hook_source": "...", "session_id": "...", ...}
    실패 행은 스킵
    반환: list of dicts
    """
    events = []
    if not stop_event_file.exists():
        return events

    try:
        with open(stop_event_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass  # 파싱 실패 행 스킵
    except Exception:
        pass

    return events


def _calculate_age_seconds(renewed_at_iso: str) -> float:
    """renewed_at (ISO8601 UTC) 로부터 현재까지 경과 초.

    실패: -1.0
    """
    try:
        # ISO 8601 UTC Z 파싱
        renewed_dt = datetime.datetime.fromisoformat(renewed_at_iso.replace("Z", "+00:00"))
        now_utc = datetime.datetime.now(tz=datetime.timezone.utc)
        delta = now_utc - renewed_dt
        return delta.total_seconds()
    except Exception:
        return -1.0


def reconcile(ledger_dir: Path, stop_event_file: Path) -> dict:
    """reconcile 4-status 계산."""

    # lease 파일 수집
    leases = []
    if ledger_dir.exists():
        for lease_file in ledger_dir.glob("429-lease-*.json"):
            parsed = _parse_lease_file(lease_file)
            if parsed:
                leases.append(parsed)

    # stop-event 수집
    stops = _parse_stop_event_file(stop_event_file)

    active_lease_count = len(leases)
    matching_stop_count = len([s for s in stops if s.get("hook_source") in ("stop", "subagent-stop")])

    # 나이 계산 (orphaned leases only)
    ages_seconds = []
    for lease in leases:
        renewed_at = lease.get("renewed_at")
        if renewed_at:
            age = _calculate_age_seconds(renewed_at)
            if age >= 0:
                ages_seconds.append(age)

    # 통계
    age_min = min(ages_seconds) if ages_seconds else None
    age_max = max(ages_seconds) if ages_seconds else None
    age_mean = statistics.mean(ages_seconds) if ages_seconds else None

    # 4-status 판정 (TTL 미확정이므로 orphan_expired 판정 = age 분포 보고만)
    # 주의: stop_without_lease 는 "구조적 증인" — 정확한 판별은 불가능하나 관측됨
    # 순서 중요: no_data → orphan_expired → aligned → stop_without_lease
    status = "no_data"

    if active_lease_count == 0 and matching_stop_count == 0:
        # 케이스: 파일 없음 / lease 0 / stop 0
        status = "no_data"
    elif active_lease_count > matching_stop_count:
        # 케이스: active > stops (일부 lease 미해제/만료 = 분명한 orphan)
        status = "orphan_expired"
    elif active_lease_count <= matching_stop_count and (active_lease_count > 0 or matching_stop_count == 0):
        # 케이스: (active <= stops AND active > 0) OR (active == 0 AND stops == 0)
        # 정상 진행 또는 대칭
        status = "aligned"
    else:
        # 케이스: active == 0 AND stops > 0
        # 유일한 모호한 경우: (1) 완료+해제 (2) resume 또는 (3) 만료+회수
        # 이 경우 구조적으로 resume 증인이 될 수 있음 (BS-1 potentially observed)
        # 단, phase A 에서는 TTL 미확정이라 "orphan_expired" 와는 다른 분류
        status = "stop_without_lease"

    # 나이가 있으면 정렬
    ages_seconds_sorted = sorted(ages_seconds) if ages_seconds else []

    return {
        "status": status,
        "active_leases": active_lease_count,
        "matching_stops": matching_stop_count,
        "orphaned_leases": max(0, active_lease_count - matching_stop_count),
        "orphaned_ages_seconds": ages_seconds_sorted,
        "age_min_seconds": age_min,
        "age_max_seconds": age_max,
        "age_mean_seconds": age_mean,
        "timestamp": _utc_now_z(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="429 subagent concurrency lease reconciliation"
    )
    parser.add_argument(
        "--ledger-dir",
        default=None,
        help="ledger directory (default: CLAUDE_PROJECT_DIR/.claude/ledger)"
    )
    parser.add_argument(
        "--stop-event-file",
        default=None,
        help="stop-event.jsonl path (default: CLAUDE_PROJECT_DIR/.claude/ledger/stop-event.jsonl)"
    )

    args = parser.parse_args()

    # ledger dir 결정
    ledger_dir = Path(args.ledger_dir) if args.ledger_dir else None
    if not ledger_dir and "CLAUDE_PROJECT_DIR" in os.environ:
        ledger_dir = Path(os.environ["CLAUDE_PROJECT_DIR"]) / ".claude" / "ledger"
    if not ledger_dir:
        ledger_dir = Path.cwd() / ".claude" / "ledger"

    # stop-event 파일 결정
    stop_event_file = Path(args.stop_event_file) if args.stop_event_file else None
    if not stop_event_file and "CLAUDE_PROJECT_DIR" in os.environ:
        stop_event_file = Path(os.environ["CLAUDE_PROJECT_DIR"]) / ".claude" / "ledger" / "stop-event.jsonl"
    if not stop_event_file:
        stop_event_file = ledger_dir / "stop-event.jsonl"

    # reconcile 실행
    result = reconcile(ledger_dir, stop_event_file)

    # JSON 출력
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # error → exit 0 (호출자 gate 아님, record-only)
        print(
            json.dumps({
                "status": "error",
                "error": str(e),
                "timestamp": _utc_now_z(),
            }),
            file=sys.stderr
        )
        sys.exit(0)
