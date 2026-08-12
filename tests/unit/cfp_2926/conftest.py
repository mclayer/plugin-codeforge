"""conftest.py — CFP-2926 RTM 명명 테스트 (AC-2~AC-15 계약 이행).

Change Plan §8.0.3-8.0.9 + RTM fixture 계약 SSOT: dispatch packet 이용.

제공 fixture:
  - tmp_path: pytest standard tmpdir
  - capture_output: subprocess 호출 → CompletedProcess
  - golden_fixture: F-1~F-8 기본 입력값 dict
  - repo_root: 프로젝트 루트 경로

상위 tests/conftest.py 가 scripts/lib 를 sys.path 에 주입 → 각 모듈 직접 import 가능.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# tests/unit/cfp_2926/ → repo root (parents[3])
REPO_ROOT = Path(__file__).resolve().parents[3]


def _run_subprocess(cmd, cwd=None, capture_output=True):
    """subprocess.run wrapper — utf-8 인코딩."""
    return subprocess.run(
        cmd,
        cwd=cwd or str(REPO_ROOT),
        capture_output=capture_output,
        text=True,
        encoding="utf-8",
    )


@pytest.fixture
def capture_output():
    """subprocess 호출 fixture (반환: CompletedProcess)."""
    return _run_subprocess


@pytest.fixture
def repo_root():
    """프로젝트 루트 경로."""
    return REPO_ROOT


@pytest.fixture
def golden_fixture():
    """F-1~F-8 fixture 계약 입력값.

    dispatch packet 명시 기대값 기반.
    """
    return {
        "F-1": {
            "name": "순수 batch (14초 군집 16행)",
            "rows": [
                {
                    "event_id": f"ev{i:03d}",
                    "agent_start_at": 1000 + i * 500,  # 0.5초 간격
                    "agent_stop_at": 1000 + i * 500 + 100,
                    "stop_time_source": "hook_stamped",
                }
                for i in range(16)
            ],
            "expected_spawns": 16,
            "expect_verdict": "PASS",  # batch 감지 미구현 — 실제 multiplier 산출
        },
        "F-2": {
            "name": "부분 batch (정상 71 + batch 15)",
            "rows": (
                [
                    {
                        "event_id": f"n{i:03d}",
                        "agent_start_at": 10000 + i * 1000,
                        "agent_stop_at": 10000 + i * 1000 + 500,
                        "stop_time_source": "hook_stamped",
                    }
                    for i in range(71)
                ]
                + [
                    {
                        "event_id": f"b{i:03d}",
                        "agent_start_at": 1000 + i * 100,
                        "agent_stop_at": 1000 + i * 100 + 10,
                        "stop_time_source": "hook_stamped",
                    }
                    for i in range(15)
                ]
            ),
            "expected_spawns": 86,
            "expect_verdict": "PASS",  # batch 혼합 감지 미구현
        },
        "F-3": {
            "name": "오염 baseline (80행, 20행=28% 군집)",
            "rows": (
                [
                    {
                        "event_id": f"c{i:03d}",
                        "agent_start_at": 100 + i * 50,  # 0~2초에 20행 군집
                        "agent_stop_at": 100 + i * 50 + 30,
                        "stop_time_source": "hook_stamped",
                    }
                    for i in range(20)
                ]
                + [
                    {
                        "event_id": f"x{i:03d}",
                        "agent_start_at": 5000 + i * 800,
                        "agent_stop_at": 5000 + i * 800 + 400,
                        "stop_time_source": "hook_stamped",
                    }
                    for i in range(60)
                ]
            ),
            "expected_spawns": 80,
            "expect_verdict": "PASS",  # baseline 오염 감지 미구현
        },
        "F-4": {
            "name": "완전중첩 (4행, 10분, 2개씩 중첩) → multiplier = 2.0",
            "rows": [
                {
                    "event_id": "f4-1a",
                    "agent_start_at": 0,
                    "agent_stop_at": 600000,  # 10분 (600초)
                    "stop_time_source": "hook_stamped",
                },
                {
                    "event_id": "f4-1b",
                    "agent_start_at": 0,
                    "agent_stop_at": 600000,
                    "stop_time_source": "hook_stamped",
                },
                {
                    "event_id": "f4-2a",
                    "agent_start_at": 600000,
                    "agent_stop_at": 1200000,  # 다음 10분
                    "stop_time_source": "hook_stamped",
                },
                {
                    "event_id": "f4-2b",
                    "agent_start_at": 600000,
                    "agent_stop_at": 1200000,
                    "stop_time_source": "hook_stamped",
                },
            ],
            "expected_spawns": 4,
            "expect_multiplier": 2.0,
            "expect_verdict": "PASS",
        },
        "F-5": {
            "name": "반개구간 경계 (off-by-one)",
            "test_cases": [
                {
                    "desc": "A.stop == B.start (무겹침)",
                    "rows": [
                        {
                            "writer_key": "W1",
                            "artifact_key": "A",
                            "first_write": 0,
                            "last_write": 100,
                        },
                        {
                            "writer_key": "W2",
                            "artifact_key": "B",
                            "first_write": 100,
                            "last_write": 200,
                        },
                    ],
                    "expect_p2": 0,
                },
                {
                    "desc": "A.stop == B.start + 1ms (겹침)",
                    "rows": [
                        {
                            "writer_key": "W1",
                            "artifact_key": "A",
                            "first_write": 0,
                            "last_write": 101,
                        },
                        {
                            "writer_key": "W2",
                            "artifact_key": "B",
                            "first_write": 100,
                            "last_write": 200,
                        },
                    ],
                    "expect_p2_gt": 0,
                },
            ],
        },
        "F-6": {
            "name": "혼합 provenance (admissible 3 + unknown 1, hook counter = 4)",
            "rows": [
                {
                    "event_id": "a1",
                    "agent_start_at": 0,
                    "agent_stop_at": 100,
                    "stop_time_source": "hook_stamped",
                },
                {
                    "event_id": "a2",
                    "agent_start_at": 200,
                    "agent_stop_at": 300,
                    "stop_time_source": "hook_stamped",
                },
                {
                    "event_id": "a3",
                    "agent_start_at": 400,
                    "agent_stop_at": 500,
                    "stop_time_source": "hook_stamped",
                },
                {"event_id": "u1", "agent_start_at": None},  # unknown (부재)
            ],
            "expected_spawns": 4,
            "expect_verdict": "INCONCLUSIVE",  # 완전성 미충족
        },
        "F-6p": {
            "name": "전량 0행 (hook 미발화) — expect: INCONCLUSIVE (0==0 GREEN 금지)",
            "rows": [],
            "expected_spawns": 0,
            "expect_verdict": "INCONCLUSIVE",
        },
        "F-7": {
            "name": "dev-process P1·P2 양성 (A→B→A + 구간교집합)",
            "rows": [
                {
                    "writer_key": "W-A",
                    "artifact_key": "art1",
                    "first_write": 0,
                    "last_write": 100,
                },
                {
                    "writer_key": "W-B",
                    "artifact_key": "art2",
                    "first_write": 50,
                    "last_write": 150,
                },
                {
                    "writer_key": "W-A",
                    "artifact_key": "art3",
                    "first_write": 120,
                    "last_write": 200,
                },
            ],
            "expect_p1_gt": 0,
            "expect_p2_gt": 0,
        },
        "F-8": {
            "name": "비대칭 부분중첩 (multiplier = 1.2)",
            # A=[0,20)·B=[15,45)·C=[40,50) (분 단위, 반개구간)
            # Σduration = 20+30+10 = 60
            # union = [0,50) 간격 = 50
            # multiplier = 60÷50 = 1.2
            "rows": [
                {
                    "event_id": "f8-a",
                    "agent_start_at": 0,
                    "agent_stop_at": 20,
                    "stop_time_source": "hook_stamped",
                },
                {
                    "event_id": "f8-b",
                    "agent_start_at": 15,
                    "agent_stop_at": 45,
                    "stop_time_source": "hook_stamped",
                },
                {
                    "event_id": "f8-c",
                    "agent_start_at": 40,
                    "agent_stop_at": 50,
                    "stop_time_source": "hook_stamped",
                },
            ],
            "expected_spawns": 3,
            "expect_multiplier": 1.2,
            "expect_verdict": "PASS",
        },
    }
