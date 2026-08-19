"""test_dev_process_concurrency.py — concurrency P0 (§8.8: 병렬 append lost-update / torn 0).

CFP-2687 Phase 2. Change Plan §8.8 concurrency P0 + §7.4.1 (O_APPEND per-row) + §11.6.
Under test: scripts/lib/append_dev_process_event.py (append_event → _append_jsonl_row O_APPEND).

두 축을 분리 검증 (정직 — 설계 §7.4.1 honest-ceiling 반영):
  · INTEGRITY (cross-platform GREEN): 병렬 append 하에서도 landed row 는 절대 torn/interleaved
    되지 않는다 — 각 줄 valid JSON dict, 정확히 20 키. (single os.write per small row.)
  · NO-LOST-UPDATE (count == writes): cross-platform GREEN (CFP-2817 FIX Iter 3). POSIX os.O_APPEND
    단일-write = 이미 kernel-atomic. Windows = FILE_APPEND_DATA(ctypes CreateFileW, FILE_WRITE_DATA
    불포함) kernel-atomic append 로 MSVCRT lseek-then-write 대체 → 완료행 clobber 0. iter1 win32
    xfail 철회(봉합 완료 — ADR-155 Amendment 1).
    ★정정됨: append_spawn_event._append_jsonl_row 은 이제 kernel-atomic(FILE_APPEND_DATA / POSIX
      O_APPEND). 이전 :420 "over-claim" 발견사항 = ADR-155 Amendment 1 로 실 보증 확립(정정).
    ★discriminating(hollow-green 차단, §8.8): test_negative_control_lost_update_is_detectable 가
      pre-fix lseek-then-write 비원자를 강제 재현 → count oracle(lost_rows>0)이 clobber 검출.
      GREEN 이 vacuous 아님을 증명(threshold = lost_rows>0, harness-config-independent).
"""

from __future__ import annotations

import concurrent.futures
import json
import os
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
# CFP-2817 FIX Iter 3: Windows FILE_APPEND_DATA kernel-atomic append 봉합 → win32 xfail 철회.
# count==writes 가 이제 cross-platform GREEN(완료행 clobber 0). discriminating 은 아래
# test_negative_control_lost_update_is_detectable(pre-fix 경로 강제 재현)로 보장.


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

    def test_thread_parallel_count_equals_writes(self, tmp_path):
        # CFP-2817 FIX Iter 3: FILE_APPEND_DATA/POSIX O_APPEND kernel-atomic → clobber 0 (win32 포함 GREEN).
        raw_lines = _run_threads(tmp_path / "dev-process-event.jsonl")
        assert len(raw_lines) == TOTAL, f"lost-update: {len(raw_lines)} lines != {TOTAL} writes"

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
        # (a) 무결성: 각 줄 valid JSON + 20 키 (distinct-marker — exit0 단독 판정 금지)
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


class TestClobberOracleDiscriminating:
    """§8.8 discriminating (hollow-green 차단): count==writes oracle 가 실제로 clobber 를 검출함을 증명.

    pre-fix lseek-then-write 비원자(kernel-atomic FILE_APPEND_DATA/O_APPEND 미경유)를 강제 재현 →
    lost_rows>0 검출. 이 RED negative-control 이 없으면 GREEN(count==writes)이 vacuous(항상 통과)일 수
    있다. GREEN 짝 = TestConcurrentAppendNoLostUpdate(kernel-atomic 공유 primitive 경유, clobber 0).
    threshold = lost_rows>0 (harness-config-independent — 관측 magnitude[9.9-12.8%, Codex 재현]는 참고).
    """

    def test_negative_control_lost_update_is_detectable(self, tmp_path):
        ledger = tmp_path / "neg-control.jsonl"
        ledger.write_bytes(b"")
        # equal-length distinct lines (실 index row 처럼 동일 길이 — clean overwrite 결정론 재현)
        line_a = (json.dumps({"seq": "A", "pad": "x" * 40}) + "\n").encode("utf-8")
        line_b = (json.dumps({"seq": "B", "pad": "y" * 40}) + "\n").encode("utf-8")
        p = str(ledger)
        # pre-fix lseek-then-write 비원자 재현: 두 writer 가 각자 EOF offset 계산(둘 다 0=empty) 후
        # 그 offset 에 write → B 가 A 를 통째 clobber. kernel-atomic append 였다면 구조적으로 불가.
        fd_a = os.open(p, os.O_WRONLY | os.O_CREAT, 0o600)
        fd_b = os.open(p, os.O_WRONLY | os.O_CREAT, 0o600)
        try:
            os.lseek(fd_a, 0, os.SEEK_END)   # A: offset 0
            os.lseek(fd_b, 0, os.SEEK_END)   # B: offset 0 (A 아직 미write → 동일 offset)
            os.write(fd_a, line_a)           # A → offset 0
            os.write(fd_b, line_b)           # B → offset 0 → A clobber
        finally:
            os.close(fd_a)
            os.close(fd_b)
        lines = [ln for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
        # 2 writes 했으나 clobber 로 소실 → count oracle(len==writes)이 검출(lost_rows>0 = discriminating).
        assert len(lines) < 2, (
            "negative-control 실패: lseek-then-write 비원자가 clobber 를 재현해야 함 "
            "(미재현 시 count==writes GREEN 이 vacuous — oracle 판별력 미증명). got %d rows" % len(lines))
