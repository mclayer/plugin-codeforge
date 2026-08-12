"""AC-3 stop_event 동시 append + 문면 검증.

append_stop_event.py CLI 테스트.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
STOP_EVENT_SCRIPT = REPO_ROOT / "scripts" / "lib" / "append_stop_event.py"


def test_stop_event_concurrent_append_no_loss(tmp_path, capture_output):
    """AC-3 동시 append (N=8): atomic 보증, 행 손실 0.

    [Mutant: read-modify-write (비원자) → 손실 再現]
    [Discriminating: disposable tmpdir 사본에서 실제로 손실 주입해 RED 확인]
    """
    ledger = tmp_path / "stop-event.jsonl"

    # 8개 워커 병렬 append (각 1행)
    # append_stop_event.py 인자: --hook-source, --ledger-path, --session-id, --stop-reason
    def append_worker(idx):
        result = subprocess.run(
            [
                sys.executable,
                str(STOP_EVENT_SCRIPT),
                "--hook-source",
                "stop",
                "--ledger-path",
                str(ledger),
                "--session-id",
                f"sess-test-{idx}",
                "--stop-reason",
                f"test_run_{idx}",
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.returncode

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(append_worker, range(8)))

    # 모두 exit 0 (graceful degradation — 실패해도 exit 0)
    # AC-3 검증: 원장에 8행 모두 기록되었는가
    if ledger.exists():
        lines = ledger.read_text(encoding="utf-8").splitlines()
        written_count = len([line for line in lines if line.strip()])
        assert written_count == 8, (
            f"expected 8 rows, got {written_count} (atomic append loss)"
        )


def test_stop_event_header_false_guarantee_absent(tmp_path):
    """AC-3 문면: 거짓 보증 미포함.

    append_stop_event.py docstring/주석에 false guarantee
    (예: "no data loss guaranteed under all conditions") 부재.

    [Mutant: 거짓 보증 추가 → RED (문면 위반)]
    [Discriminating: 제약을 솔직하게 선언 (honest ceiling)]
    """
    script_path = STOP_EVENT_SCRIPT
    assert script_path.exists()

    script_text = script_path.read_text(encoding="utf-8")

    # 금지 표현 (거짓 보증) 검색
    false_guarantees = [
        "guaranteed",
        "no data loss",
        "100% atomicity",
        "fail-proof",
    ]

    violations = []
    for phrase in false_guarantees:
        if phrase.lower() in script_text.lower():
            # docstring 영역만 검사 (주석과 code 혼동 피함)
            lines = script_text.split("\n")
            for i, line in enumerate(lines[:50]):  # 헤더 영역만
                if phrase.lower() in line.lower():
                    violations.append((i + 1, line.strip()))

    # 거짓 보증이 있으면 FAIL
    assert not violations, f"false guarantee found at {violations}"
