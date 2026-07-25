"""test_dev_process_args_file.py — --args-file UTF-8 채널 round-trip (CFP-2817 FIX Iter 3 결함2).

한국어 lane_label 이 Windows Git Bash cp949 argv byte-mangle → `_norm_lane_label` 미매칭 → "없음"
collapse 되던 회귀(결함2)를, UTF-8 args-file 채널(ASCII path 만 argv·한국어 content 는 파일 내부)로
byte-exact round-trip 함을 검증. change-plan §3.6 / §5 (결함2 봉합) · emit_dev_process_event.py
_dispatch_from_args_file.

★discriminating: lane_label byte-exact 단언 + "없음" 부정 단언 — CLI 가 locale(cp949) default 로
  read 하면(회귀) 한국어가 mangle 되어 두 단언 모두 RED. utf-8 명시 read 여야 GREEN.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EMIT = str(REPO_ROOT / "scripts" / "lib" / "emit_dev_process_event.py")


def _run_emit_args_file(tmp_path, payload):
    ledger = tmp_path / "dev-process-event.jsonl"
    payload = dict(payload, ledger_path=str(ledger))
    args_file = tmp_path / "emit_args.json"
    # UTF-8 로 write (한국어 content 는 파일 내부 — argv 미경유). ensure_ascii=False 로 실 한국어 바이트.
    args_file.write_bytes(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    r = subprocess.run(
        [sys.executable, EMIT, "--args-file", str(args_file)],  # ★ASCII path 만 argv
        cwd=str(REPO_ROOT), capture_output=True, timeout=60,
    )
    assert r.returncode == 0, "emit --args-file exit %d: %r" % (
        r.returncode, r.stderr.decode(errors="replace"))
    rows = [json.loads(ln) for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return rows


@pytest.mark.parametrize("lane", ["구현", "구현-리뷰", "설계", "요구사항", "보안-테스트"])
def test_args_file_korean_lane_label_round_trips(tmp_path, lane):
    rows = _run_emit_args_file(tmp_path, {
        "command": "lane-transition", "story_key": "CFP-2817",
        "lane_label": lane, "transition_kind": "enter", "consumer_scope": "wrapper",
    })
    assert len(rows) == 1, "정확히 1 row emit"
    # ★핵심(결함2 봉합): 한국어 lane_label byte-exact — cp949 mangle / "없음" collapse 0
    assert rows[0]["lane_label"] == lane, \
        "lane_label mangle/collapse: got %r want %r" % (rows[0]["lane_label"], lane)
    assert rows[0]["lane_label"] != "없음", "argv-mangle 회귀(없음 collapse)"
    assert rows[0]["emit_source"] == "agent", "Port-B agent-emit"


def test_args_file_ac13_rejects_caller_timestamp(tmp_path):
    """AC-13: args-file 의 caller-computed timestamp 필드는 무시(저장층 UTC 단일 소스). WARN 만·exit 0."""
    ledger = tmp_path / "dev-process-event.jsonl"
    args_file = tmp_path / "emit_args.json"
    payload = {"command": "lane-transition", "story_key": "CFP-2817", "lane_label": "구현",
               "transition_kind": "enter", "consumer_scope": "wrapper",
               "ledger_path": str(ledger), "timestamp": "2020-01-01T00:00:00Z"}
    args_file.write_bytes(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    r = subprocess.run([sys.executable, EMIT, "--args-file", str(args_file)],
                       cwd=str(REPO_ROOT), capture_output=True, timeout=60)
    assert r.returncode == 0, r.stderr.decode(errors="replace")
    rows = [json.loads(ln) for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(rows) == 1
    # caller 가 준 2020 timestamp 가 아니라 저장층 실제 UTC 여야 함(AC-13)
    assert not rows[0].get("timestamp_utc", "").startswith("2020-01-01"), \
        "AC-13 위반: caller timestamp 가 저장됨"
