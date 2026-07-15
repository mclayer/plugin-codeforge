"""test_dev_process_concurrency.py — concurrency P0 (§8.8: 병렬 append lost-update / torn 0).

CFP-2687 Phase 2. Change Plan §8.8 concurrency P0 + §7.4.1 (O_APPEND per-row) + §11.6.
Under test: scripts/lib/append_dev_process_event.py (append_event → _append_jsonl_row O_APPEND).

두 축을 분리 검증 (정직 — 설계 §7.4.1 honest-ceiling 반영):
  · INTEGRITY (cross-platform GREEN): 병렬 append 하에서도 landed row 는 절대 torn/interleaved
    되지 않는다 — 각 줄 valid JSON dict, 정확히 18 키. (single os.write per small row.)
  · NO-LOST-UPDATE (count == writes): POSIX 는 atomic O_APPEND 로 보장(GREEN). **Windows msvcrt
    O_APPEND = seek+write 비원자** → 고동시성에서 whole-row lost-update 발생(clean loss, torn 아님).
    → win32 xfail(strict=False), POSIX(ubuntu CI authoritative)에서 실검증.
    ★발견사항: append_spawn_event._append_jsonl_row:420 주석 "cross-process lost-update 회피"는
      Windows 에서 over-claim (change-plan §7.4.1 "kernel-atomic 단정 아님"이 이미 hedge).
"""

from __future__ import annotations

import concurrent.futures
import json
import subprocess
import sys
from pathlib import Path

import pytest

import append_dev_process_event as ade

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

N_WORKERS = 8
ROWS_PER_WORKER = 25
TOTAL = N_WORKERS * ROWS_PER_WORKER

WIN = sys.platform == "win32"
_WIN_APPEND_XFAIL = pytest.mark.xfail(
    WIN, strict=False,
    reason="Windows msvcrt O_APPEND 비원자(seek+write) → 고동시성 whole-row lost-update. "
           "POSIX atomic O_APPEND 에서는 count==writes GREEN. 발견사항(매핑표) — src 미수정(QADev).",
)


def _worker(ledger_path: str, worker_id: int):
    for i in range(ROWS_PER_WORKER):
        ade.append_event(
            ledger_path=ledger_path,
            event_type="tool_call", emit_source="hook",
            story_key="CFP-2687", lane_label="구현", consumer_scope="wrapper",
            seq="w%d-r%d" % (worker_id, i),   # distinct → distinct event_id
        )
    return worker_id


def _run_threads(ledger: Path):
    with concurrent.futures.ThreadPoolExecutor(max_workers=N_WORKERS) as ex:
        futs = [ex.submit(_worker, str(ledger), w) for w in range(N_WORKERS)]
        for f in concurrent.futures.as_completed(futs):
            f.result()
    return [ln for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]


class TestConcurrentAppendIntegrity:
    """landed row 무결성 — torn/interleaved 0 (cross-platform GREEN)."""

    def test_thread_parallel_no_torn_or_interleaved_rows(self, tmp_path):
        raw_lines = _run_threads(tmp_path / "dev-process-event.jsonl")
        assert raw_lines, "아무 row 도 기록되지 않음"
        eids = []
        for ln in raw_lines:
            row = json.loads(ln)   # torn/interleaved 이면 여기서 raise → RED
            assert isinstance(row, dict)
            assert tuple(row.keys()) == ade._ROW_KEYS, "interleaved/부분 row (키 손상)"
            eids.append(row["event_id"])
        # landed row 는 서로 다른 논리 이벤트 (distinct seq) → event_id 충돌 0
        assert len(set(eids)) == len(eids), "landed row event_id 충돌 (interleave 오염)"


class TestConcurrentAppendNoLostUpdate:
    """count == writes — POSIX atomic O_APPEND (GREEN) / Windows 비원자 (xfail)."""

    @_WIN_APPEND_XFAIL
    def test_thread_parallel_count_equals_writes(self, tmp_path):
        raw_lines = _run_threads(tmp_path / "dev-process-event.jsonl")
        assert len(raw_lines) == TOTAL, f"lost-update: {len(raw_lines)} lines != {TOTAL} writes"

    @_WIN_APPEND_XFAIL
    def test_process_parallel_cli_count_equals_procs(self, tmp_path):
        """별도 프로세스(subprocess CLI) 병렬 append — cross-process O_APPEND.

        distinct-marker: exit code 0 만 보지 않고 최종 원장 valid-JSON row 수(도메인 산출)를
        병행 assert (exit-code-only false-positive 회피 — QADev distinct-marker 의무)."""
        ledger = tmp_path / "dev-process-event.jsonl"
        n_proc = 6
        script = str(REPO_ROOT / "scripts" / "lib" / "append_dev_process_event.py")
        lanes = ["요구사항", "설계", "구현", "구현-리뷰", "보안-테스트", "배포"]
        procs = []
        for w in range(n_proc):
            cmd = [
                sys.executable, script,
                "--ledger-path", str(ledger),
                "--event-type", "lane_transition", "--emit-source", "agent",
                "--story-key", "CFP-2687", "--lane-label", lanes[w],  # distinct → distinct id
                "--consumer-scope", "wrapper",
            ]
            procs.append(subprocess.Popen(cmd, cwd=str(REPO_ROOT),
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE))
        for p in procs:
            out, err = p.communicate(timeout=60)
            assert p.returncode == 0, f"CLI exit {p.returncode}: {err.decode(errors='replace')}"

        lines = [ln for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
        # (a) 무결성: 각 줄 valid JSON + 18 키 (distinct-marker — exit0 단독 판정 금지)
        for ln in lines:
            row = json.loads(ln)
            assert tuple(row.keys()) == ade._ROW_KEYS
        # (b) no-lost-update: 줄 수 == 프로세스 수 (POSIX GREEN / win32 xfail)
        assert len(lines) == n_proc, f"cross-process lost-update: {len(lines)} != {n_proc}"


class TestProcessCliIntegrity:
    """subprocess CLI 병렬 append 무결성 — torn 0 (cross-platform GREEN, count 무관)."""

    def test_process_cli_landed_rows_valid(self, tmp_path):
        ledger = tmp_path / "dev-process-event.jsonl"
        n_proc = 6
        script = str(REPO_ROOT / "scripts" / "lib" / "append_dev_process_event.py")
        lanes = ["요구사항", "설계", "구현", "구현-리뷰", "보안-테스트", "배포"]
        procs = [
            subprocess.Popen(
                [sys.executable, script, "--ledger-path", str(ledger),
                 "--event-type", "lane_transition", "--emit-source", "agent",
                 "--story-key", "CFP-2687", "--lane-label", lanes[w],
                 "--consumer-scope", "wrapper"],
                cwd=str(REPO_ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for w in range(n_proc)
        ]
        for p in procs:
            _, err = p.communicate(timeout=60)
            assert p.returncode == 0, f"CLI exit {p.returncode}: {err.decode(errors='replace')}"
        lines = [ln for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert lines, "아무 row 도 기록되지 않음"
        for ln in lines:
            row = json.loads(ln)   # torn 이면 RED
            assert tuple(row.keys()) == ade._ROW_KEYS
