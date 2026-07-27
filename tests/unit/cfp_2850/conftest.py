"""conftest.py — CFP-2850 spawn-event 실측 append + outcome 분류 테스트 부트스트랩.

QADev 경계 (본 파일 + tests/** 만 write): production 코드(scripts/lib, hooks) READ-ONLY.
production 로직을 테스트 안에서 재구현하지 않는다 — 실제 append_spawn_event.py CLI/함수를
subprocess/import 로 호출해 검증 (Change Plan §8 제약).

제공 fixture:
  - run_append: 실제 scripts/lib/append_spawn_event.py CLI 를 subprocess 로 호출.
  - read_rows: ledger jsonl 파싱 → list[dict].
  - golden:    §8.7 captured-golden fixture 모듈 (실측 task-notification).

상위 tests/conftest.py 가 이미 scripts/lib 를 sys.path 에 주입 → append_spawn_event /
spawn_event_pricing / dedup_section14_spawn_event 직접 import 가능.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

# tests/unit/cfp_2850/ → repo root (parents[3])
REPO_ROOT = Path(__file__).resolve().parents[3]
APPEND_SCRIPT = REPO_ROOT / "scripts" / "lib" / "append_spawn_event.py"
GOLDEN_PATH = REPO_ROOT / "tests" / "fixtures" / "cfp_2850" / "task_notification_usage_golden.py"

# 23-field 계약↔runtime parity 기대 (Change Plan §3.7 / §10.A — 19-field + 4 additive).
CONTRACT_19_FIELDS = (
    "event_id", "schema_version", "timestamp", "story_key", "lane_label",
    "agent_type", "attribution_confidence", "input_tokens", "output_tokens",
    "cache_creation_input_tokens", "cache_read_input_tokens", "cost_usd",
    "duration_ms", "tool_call_count", "actor", "parent_event_id",
    "consumer_scope", "event_type", "elapsed_seconds",
)
NEW_4_FIELDS = ("total_tokens", "model", "outcome", "termination_cause")
CONTRACT_23_FIELDS = CONTRACT_19_FIELDS + NEW_4_FIELDS

# outcome / termination_cause closed-set (Change Plan §3.2 / §10.A verbatim).
OUTCOME_ENUM = {"success", "inconclusive", "failure", "partial"}
TERMINATION_CAUSE_ENUM = {"normal", "timeout", "zero_output", "error", "cancelled"}


def _cli_run(ledger_path, opt_in=True, **flags):
    """실제 append_spawn_event.py CLI subprocess 호출 (production 재구현 금지).

    flags: underscored flag 명 → 값. True 면 store_true, None/False 면 생략.
    opt_in=True 면 --telemetry-enabled --spawn-event-enabled 부착.
    Returns subprocess.CompletedProcess.
    """
    cmd = [sys.executable, str(APPEND_SCRIPT)]
    if ledger_path is not None:
        cmd += ["--ledger-path", str(ledger_path)]
    for key, val in flags.items():
        flag = "--" + key.replace("_", "-")
        if val is True:
            cmd.append(flag)
        elif val is None or val is False:
            continue
        else:
            cmd += [flag, str(val)]
    if opt_in:
        cmd += ["--telemetry-enabled", "--spawn-event-enabled"]
    return subprocess.run(
        cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, encoding="utf-8"
    )


def _read_rows(ledger_path):
    """ledger jsonl → list[dict] (부재/빈 파일 → [])."""
    p = Path(ledger_path)
    if not p.exists():
        return []
    return [
        json.loads(line)
        for line in p.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


@pytest.fixture
def run_append():
    return _cli_run


@pytest.fixture
def read_rows():
    return _read_rows


@pytest.fixture(scope="session")
def golden():
    """§8.7 captured-golden fixture 모듈 로드 (실측 task-notification)."""
    spec = importlib.util.spec_from_file_location(
        "cfp2850_golden", str(GOLDEN_PATH)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
