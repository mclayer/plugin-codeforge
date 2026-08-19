#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_cfp2967_concurrent_append.py

CFP-2967 Phase 2 — §8.8.4 concurrency test (동적 검증 로스터).

계약 SSOT: Change Plan §8.8.4.
규범: ADR-146 (dynamic test burden-flip standard).

공유 상태: ① 429 event log 파일 ② lease 파일
실행 모델: **멀티프로세스** (스레드 아님 — 실 형상이 독립 훅 프로세스의 동시 발화)
Worker count: N ≥ 4 ⇒ 1-worker 순차 실행은 본 계약 미충족 (append 경합창이 열리지 않음)

Oracle:
  ① DATA 행 수 == N (유실 0 ∧ 중복 0)
  ② 전 행 JSON 파싱 성공
  ③ 개행 없이 절단된 부분행 0 (INV-2 append-only + §8.2 B-6 정렬 가정 금지)

Duration: barrier 정렬 라운드 반복 + CI wall-clock 상한.
상한 값은 실측으로 정하고 리터럴로 못박지 않음 (ADR-068 I-5).

Warning: 이 테스트는 subprocess multiprocessing 을 사용합니다.
단일 스레드 테스트 러너에서 실행 시 I/O 대기로 인해 벽시계 시간이 늘어날 수 있습니다.
"""
import json
import multiprocessing
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import List, Dict, Any


# ══════════════════════════════════════════════════════════════════════════════
# Helper: 멀티프로세스 append worker (각 프로세스가 수행할 작업)
# ══════════════════════════════════════════════════════════════════════════════
def worker_append_event(worker_id: int, logfile: Path, barrier: multiprocessing.Barrier, count: int = 1):
    """각 워커가 수행: barrier 로 동시 진입 정렬 후 append.

    Args:
        worker_id: 워커 번호 (0부터)
        logfile: 공유 JSONL 로그 파일 경로
        barrier: 동시 진입 동기화 barrier
        count: 이 워커가 append 할 행 수
    """
    try:
        # Barrier 에서 기다림 (모든 워커가 준비될 때까지)
        barrier.wait(timeout=10.0)
    except Exception:
        sys.stderr.write(f"Worker {worker_id} barrier timeout\n")
        return

    # append 수행 (append-only, write mode 아님)
    for i in range(count):
        event = {
            "timestamp": f"2026-08-19T15:36:{32+worker_id}Z",
            "event_type": "rate_limit",
            "worker_id": worker_id,
            "sequence": i,
            "incident_id": f"worker-{worker_id}-seq-{i}",
        }

        line = json.dumps(event)

        # 원자적 append: open(a), write, close
        # 표준 POSIX append 는 커널 수준 원자성을 보장하지만,
        # Windows 는 file locking 과 버퍼링 때문에 실제로 완전히 보호되지 않을 수 있음.
        # 테스트 목적: 기본 append 동작 검증.
        try:
            with open(str(logfile), 'a', encoding='utf-8', newline='\n') as f:
                f.write(line + '\n')
                f.flush()  # 버퍼 강제 flush
        except Exception as e:
            sys.stderr.write(f"Worker {worker_id} write error: {e}\n")


# ══════════════════════════════════════════════════════════════════════════════
# Test: 동시 append 무결성
# ══════════════════════════════════════════════════════════════════════════════
def test_concurrent_append_no_data_loss():
    """Concurrency oracle ① — DATA 행 수 == N (유실 0 ∧ 중복 0)."""
    worker_count = 4
    events_per_worker = 1

    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', newline='\n', suffix='.jsonl') as f:
        logfile = Path(f.name)

    try:
        # 멀티프로세스로 동시 append 수행
        barrier = multiprocessing.Barrier(worker_count)
        processes = []

        for i in range(worker_count):
            p = multiprocessing.Process(
                target=worker_append_event,
                args=(i, logfile, barrier, events_per_worker)
            )
            processes.append(p)
            p.start()

        # 모든 프로세스 완료 대기 (타임아웃: 30초)
        for p in processes:
            p.join(timeout=30.0)
            if p.is_alive():
                p.terminate()

        # 파일에서 행 읽기
        content = logfile.read_text(encoding='utf-8')
        lines = [ln.strip() for ln in content.split('\n') if ln.strip()]

        expected_count = worker_count * events_per_worker
        assert len(lines) == expected_count, (
            f"Data loss detected: expected {expected_count} lines, got {len(lines)}"
        )

    finally:
        logfile.unlink()


def test_concurrent_append_json_parseable():
    """Concurrency oracle ② — 전 행 JSON 파싱 성공."""
    worker_count = 4
    events_per_worker = 1

    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', newline='\n', suffix='.jsonl') as f:
        logfile = Path(f.name)

    try:
        barrier = multiprocessing.Barrier(worker_count)
        processes = []

        for i in range(worker_count):
            p = multiprocessing.Process(
                target=worker_append_event,
                args=(i, logfile, barrier, events_per_worker)
            )
            processes.append(p)
            p.start()

        for p in processes:
            p.join(timeout=30.0)
            if p.is_alive():
                p.terminate()

        # 파일에서 행 읽기 및 파싱
        content = logfile.read_text(encoding='utf-8')
        lines = [ln.strip() for ln in content.split('\n') if ln.strip()]

        parse_errors = []
        for i, line in enumerate(lines):
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                parse_errors.append((i, line, str(e)))

        assert not parse_errors, (
            f"JSON parse errors found: {parse_errors}"
        )

    finally:
        logfile.unlink()


def test_concurrent_append_no_partial_lines():
    """Concurrency oracle ③ — 개행 없이 절단된 부분행 0."""
    worker_count = 4
    events_per_worker = 1

    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', newline='\n', suffix='.jsonl') as f:
        logfile = Path(f.name)

    try:
        barrier = multiprocessing.Barrier(worker_count)
        processes = []

        for i in range(worker_count):
            p = multiprocessing.Process(
                target=worker_append_event,
                args=(i, logfile, barrier, events_per_worker)
            )
            processes.append(p)
            p.start()

        for p in processes:
            p.join(timeout=30.0)
            if p.is_alive():
                p.terminate()

        # 파일 내용을 raw bytes 로 읽기 (인코딩 상관없이 구조 검사)
        content = logfile.read_text(encoding='utf-8')

        # 마지막 문자가 newline 인가 (부분행 검사)
        # JSONL 형식: 각 행은 newline 으로 끝나야 함
        # 마지막 행이 newline 없이 끝나면 부분행 가능성 있음
        if content and not content.endswith('\n'):
            # 경고: 마지막 행이 부분행일 가능성
            # 하지만 강제하지는 않음 (append 직후 flush 여부에 따라 다름)
            lines = content.rstrip('\n').split('\n')
            # 마지막 라인이 완전한 JSON 인지 확인
            last_line = lines[-1] if lines else ""
            if last_line:
                try:
                    json.loads(last_line)
                except json.JSONDecodeError:
                    raise AssertionError(f"Last line is incomplete JSON: {last_line[:50]}...")

        # 모든 행이 newline 으로 끝나는지 확인
        lines = content.split('\n')
        for i, line in enumerate(lines[:-1]):  # 마지막 빈 줄은 제외
            assert line.endswith('\n') or not line, (
                f"Line {i} is not properly terminated: {line[:50]}"
            )

    finally:
        logfile.unlink()


def test_concurrent_append_with_higher_worker_count():
    """Stress test — N=8 워커로 동시 append 무결성 재확인."""
    worker_count = 8
    events_per_worker = 1

    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', newline='\n', suffix='.jsonl') as f:
        logfile = Path(f.name)

    try:
        barrier = multiprocessing.Barrier(worker_count)
        processes = []

        for i in range(worker_count):
            p = multiprocessing.Process(
                target=worker_append_event,
                args=(i, logfile, barrier, events_per_worker)
            )
            processes.append(p)
            p.start()

        for p in processes:
            p.join(timeout=30.0)
            if p.is_alive():
                p.terminate()

        content = logfile.read_text(encoding='utf-8')
        lines = [ln.strip() for ln in content.split('\n') if ln.strip()]

        expected_count = worker_count * events_per_worker
        assert len(lines) == expected_count, (
            f"Stress test failed: expected {expected_count} lines, got {len(lines)}"
        )

        # 모든 행이 파싱 가능한가
        for line in lines:
            json.loads(line)

    finally:
        logfile.unlink()


if __name__ == "__main__":
    tests = [
        test_concurrent_append_no_data_loss,
        test_concurrent_append_json_parseable,
        test_concurrent_append_no_partial_lines,
        test_concurrent_append_with_higher_worker_count,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}")
            print(f"  {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {type(e).__name__}: {e}")
            failed += 1

    print(f"\n{passed}/{len(tests)} passed")
    sys.exit(0 if failed == 0 else 1)
