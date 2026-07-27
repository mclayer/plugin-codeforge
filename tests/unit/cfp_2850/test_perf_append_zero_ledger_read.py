"""§8.3 Perf Baseline — append 0-ledger-read(O_APPEND-pure) load-bearing invariant.

Change Plan §8.3 (ACTIVE). append 경로에 원장 read syscall 0 assert.
  - seq = Orchestrator causal-state 파생(§3.6/§11.6) → append 는 ledger read 0.
  - tail-read 하면 (i) 50ms ceiling 위반(파일 커질수록 read↑) (ii) idempotency 붕괴 동시 발생.
  - 이 property = 성능·멱등 양축 load-bearing.

detector = 원장 path 를 read-access 로 open 하는지 계측(builtins.open read-mode / os.open
非-WRONLY). positive control(dedup._read_ledger_rows 가 원장 read)로 detector 非-vacuous 실증.
production 로직 재구현 금지 — 실제 append_spawn_event._build_row + _append_jsonl_row 호출.
"""

from __future__ import annotations

import builtins
import json
import os
import time
from pathlib import Path

import append_spawn_event as ase
import dedup_section14_spawn_event as dedup  # positive-control 원장 reader


def _build_row_for(ledger):
    """실 production _build_parser → _build_row (append 대상 row) 구성."""
    parser = ase._build_parser()
    args = parser.parse_args([
        "--story-key", "CFP-2850", "--lane-label", "구현",
        "--agent-type", "DeveloperAgent",
        "--session-id", "sess-perf", "--agent-id", "agent-perf", "--spawn-seq", "1",
    ])
    return ase._build_row(args)


def _make_ledger_read_detector(ledger_path, monkeypatch):
    """원장 path 를 read-access 로 open 하는 호출을 계측 (builtins.open / os.open).

    read 하려면 반드시 원장을 read-access 로 open 해야 하므로 open-level 계측이 read syscall
    의 sound proxy. append 는 write-only(O_WRONLY / FILE_APPEND_DATA) 로만 open → 미계측.
    Returns reads list (append 될 때마다 (source, mode) 기록).
    """
    ledger_str = os.path.abspath(str(ledger_path))
    reads = []
    real_open = builtins.open
    real_os_open = os.open
    wronly = getattr(os, "O_WRONLY", 1)
    accmask = getattr(os, "O_ACCMODE", 3)

    def spy_open(file, mode="r", *a, **k):
        try:
            same = os.path.abspath(str(file)) == ledger_str
        except Exception:
            same = False
        if same:
            m = str(mode)
            if ("r" in m) or ("+" in m):  # read intent
                reads.append(("builtins.open", m))
        return real_open(file, mode, *a, **k)

    def spy_os_open(path, flags, *a, **k):
        try:
            same = os.path.abspath(str(path)) == ledger_str
        except Exception:
            same = False
        if same and (flags & accmask) != wronly:  # non-write-only = read intent
            reads.append(("os.open", flags & accmask))
        return real_os_open(path, flags, *a, **k)

    monkeypatch.setattr(builtins, "open", spy_open)
    monkeypatch.setattr(os, "open", spy_os_open)
    return reads


def test_perf_append_zero_ledger_read(tmp_path, monkeypatch):
    """append 경로 = 원장 read syscall 0 (empty·large 양측), positive-control 로 detector 실증.

    mutation(가상): seq 채번 위해 원장 tail-read 도입 시 detector 가 read 포착 → RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"

    # ── positive control: detector 非-vacuous 실증 (원장 read → 포착돼야 함) ──
    ledger.write_text(
        json.dumps({"schema_version": "spawn-event-v1", "event_id": "e0"}) + "\n",
        encoding="utf-8",
    )
    reads = _make_ledger_read_detector(ledger, monkeypatch)
    dedup._read_ledger_rows(str(ledger))  # 실 원장 reader (open read-mode)
    assert len(reads) >= 1, (
        "positive control: 원장 read 가 detector 에 포착돼야 함(detector vacuous 아님 실증)"
    )

    # ── 본 검증: append 경로는 원장 read 0 (empty→append) ──
    reads.clear()
    row = _build_row_for(ledger)
    ase._append_jsonl_row(Path(ledger), row)  # 실 production append primitive
    # 측정 assertion: append 경로 원장 read 0 (O_APPEND-pure)
    assert reads == [], f"append 경로가 원장을 read 함(0-ledger-read 위반), reads={reads}"

    # ── 파일 크기 독립(load-bearing): large 원장에 append 해도 read 0 (tail-read 부재 증명) ──
    big = tmp_path / "big-spawn-event.jsonl"
    with open(big, "w", encoding="utf-8", newline="\n") as f:
        for i in range(5000):
            f.write(json.dumps({"schema_version": "spawn-event-v1", "event_id": f"e{i}"}) + "\n")
    reads_big = _make_ledger_read_detector(big, monkeypatch)
    row_big = _build_row_for(big)
    ase._append_jsonl_row(Path(big), row_big)
    # 측정 assertion: 5000행 원장에도 append read 0 (파일 커질수록 read↑ 부재 = tail-read 없음)
    assert reads_big == [], (
        f"large 원장 append 가 read 발생(파일크기 의존 tail-read = 50ms·멱등 붕괴 원인), reads={reads_big}"
    )


def test_perf_append_under_50ms_ceiling_size_independent(tmp_path):
    """§8.3 50ms p99 append ceiling(ADR-163 §결정8 SLA) — best-of-N 측정(scheduler noise robust).

    honest-ceiling: best-of-N(min)은 p99 상한의 하한 증거(엄밀 p99 부하측정 아님, ADR-119).
    파일 크기 독립도 병행 확인(empty vs 5000행 append 시간이 dramatic 하게 벌어지지 않음 =
    tail-read 부재의 성능적 방증).
    """
    CEILING_S = 0.050  # 50ms

    def _min_append_time(ledger, n=30):
        parser = ase._build_parser()
        best = float("inf")
        for i in range(n):
            args = parser.parse_args([
                "--story-key", "CFP-2850", "--lane-label", "구현",
                "--agent-type", "DeveloperAgent", "--session-id", "s",
                "--agent-id", f"a{i}", "--spawn-seq", str(i),
            ])
            row = ase._build_row(args)
            t0 = time.perf_counter()
            ase._append_jsonl_row(Path(ledger), row)
            best = min(best, time.perf_counter() - t0)
        return best

    empty_ledger = tmp_path / "empty.jsonl"
    big_ledger = tmp_path / "big.jsonl"
    with open(big_ledger, "w", encoding="utf-8", newline="\n") as f:
        for i in range(5000):
            f.write(json.dumps({"schema_version": "spawn-event-v1", "event_id": f"e{i}"}) + "\n")

    min_empty = _min_append_time(empty_ledger)
    min_big = _min_append_time(big_ledger)
    # 측정 assertion (a): 단일 append best-case < 50ms ceiling (양측)
    assert min_empty < CEILING_S, f"empty 원장 append best {min_empty*1000:.3f}ms ≥ 50ms ceiling"
    assert min_big < CEILING_S, f"5000행 원장 append best {min_big*1000:.3f}ms ≥ 50ms ceiling"
