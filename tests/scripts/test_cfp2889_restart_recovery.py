#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_cfp2889_restart_recovery.py — §8.5.2 process restart recovery (CFP-2889 Change Plan).

restart 시나리오 3축 (§8.5.2):
  1. SIGKILL 등가 (`Popen.kill()` = TerminateProcess — finally 미실행 경로):
     write-ahead 불변식 — `write_intent` 가 HTTP 시도 **이전** 영속화되어, kill 시점에
     "intent 실재 ∧ result 부재" 상태가 결정적으로 관측된다 (상태 C 구조적 차단).
  2. graceful (KeyboardInterrupt): run_live 의 try/finally 가 cleanup 을 실행하고
     abort 이벤트(orphan snapshot 포함)를 남긴다.
     **실행 플랫폼 매핑 (설계리뷰 iter2 NEW-1 — platform-explicit, skip 금지)**:
     양 플랫폼 공통 = cooperative KeyboardInterrupt 주입 (in-process — win32 는 특정 pid
     SIGINT 전달 불가라 이것이 대체 경로 그 자체). POSIX 추가 분기 = 실 SIGINT 시그널을
     subprocess 로 전달 (win32 에서는 동일 불변식을 cooperative 축이 이미 커버 — 명시
     분기이지 조용한 비활성화가 아니다).
  3. 재실행 안전 (§8.5.3 replay 는 test_confluence_property_rest.py D-6 소속 —
     upsert 수렴·stale-chunk 선소거).

mock 경계: MOCK_429 env 로 실 HTTP 0 (실 API 미도달 — §8.5.2 "mock store dry 경로" 등가.
transport 도달 전 mock 분기라 golden 불요).
"""

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pytest

from lib.confluence_property_rest import PROPERTY_KEY_PREFIX, _SyntheticResponse
import confluence_backward_measure as measure

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"
SCRIPTS_LIB = SCRIPTS / "lib"

# 자식 driver — write 1회 시도 (MOCK_429 로 실 HTTP 0). pause seam 이 intent 직후 지연을
# 만들어 부모가 그 창에서 kill 할 수 있게 한다. record_write_outcome 은 write 완료 후에만
# 도달한다 (kill 시 미도달 = write_result 부재의 판별 근거).
_DRIVER = r"""
import sys
sys.path.insert(0, {scripts!r})
sys.path.insert(0, {scripts_lib!r})
from pathlib import Path
from confluence_backward_measure import RunContext
from lib.confluence_measurement_client import create_measurement_client

ctx = RunContext("killtest", events_path=Path({events!r}))
client = create_measurement_client("https://mclayer.atlassian.net", "tok-fake", "e@x.io",
                                   accounting=ctx.accounting)
ok, env, err = client.create_property_v2("21430274", "codeforge.sync.canonical.__killprobe",
                                         {{"v": 1}}, dry=False)
ctx.record_write_outcome(bool(ok), label="killtest")
print("DRIVER_DONE", flush=True)
"""


def _spawn_driver(events_path: Path, pause_seconds: str) -> subprocess.Popen:
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("ATLASSIAN_", "CFP2829_", "CFP2889_", "CFP1495_"))}
    env.update({
        "CFP1495_API_MOCK_429": "1",                  # 실 HTTP 0 — transport 도달 전 mock 분기
        "CFP2889_TEST_PAUSE_AFTER_INTENT": pause_seconds,
        "PYTHONIOENCODING": "utf-8",
    })
    code = _DRIVER.format(scripts=str(SCRIPTS), scripts_lib=str(SCRIPTS_LIB),
                          events=str(events_path))
    return subprocess.Popen([sys.executable, "-c", code], env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _read_events(events_path: Path):
    if not events_path.exists():
        return []
    return [json.loads(line) for line in
            events_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _wait_for_event(events_path: Path, event_type: str, timeout: float = 15.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if any(e.get("event") == event_type for e in _read_events(events_path)):
            return True
        time.sleep(0.1)
    return False


def test_sigkill_equiv_write_ahead_intent_persisted(tmp_path):
    """§8.5.2 ①: kill (TerminateProcess = SIGKILL 등가) 시점에 write_intent 실재 ∧
    write_result 부재 — write-ahead 가 HTTP 이전 영속화됨 (intent 를 HTTP 뒤로 옮기는
    mutant 는 kill 창에서 intent 부재로 RED)."""
    events_path = tmp_path / "kill-events.ndjson"
    proc = _spawn_driver(events_path, pause_seconds="30")
    try:
        assert _wait_for_event(events_path, "write_intent"), "write_intent 미기록 (write-ahead 부재)"
        proc.kill()                                   # TerminateProcess — finally 미실행 경로
        proc.wait(timeout=10)
    finally:
        if proc.poll() is None:
            proc.kill()
    events = _read_events(events_path)
    types = [e["event"] for e in events]
    assert "write_intent" in types
    assert "write_result" not in types, "kill 이전에 result 기록 — pause seam·write-ahead 전제 붕괴"
    intent = next(e for e in events if e["event"] == "write_intent")
    assert intent["key"] == f"{PROPERTY_KEY_PREFIX}.__killprobe"


def test_sigkill_control_run_to_completion(tmp_path):
    """§8.5.2 ① 대조군: kill 없이 완주 → intent ∧ result 양쪽 실재 (①의 'result 부재' 가
    kill 때문임을 판별 — 이 대조군 없으면 'result 원래 안 씀' hollow 를 못 가른다)."""
    events_path = tmp_path / "control-events.ndjson"
    proc = _spawn_driver(events_path, pause_seconds="0")
    try:
        out, err = proc.communicate(timeout=60)
    finally:
        if proc.poll() is None:
            proc.kill()
    assert proc.returncode == 0, f"대조군 driver 실패 — stderr tail: {err.decode('utf-8', 'replace')[-300:]}"
    types = [e["event"] for e in _read_events(events_path)]
    assert "write_intent" in types and "write_result" in types


class _GracefulFakeClient:
    """run_live graceful 결박용 — page GET 200+sentinel / 열거 [] / DELETE 기록."""

    def __init__(self, accounting):
        self.accounting = accounting
        self.header_captures = []
        self.rate_events = []
        self.removed = []
        self.last_list_partial = False

    def _perform_request(self, method, path, *, body_bytes=None, params=None,
                         dry=False, timeout=10):
        return _SyntheticResponse(200, {}, json.dumps(
            {"title": "CFP-2889-THROWAWAY-restart", "results": []}))

    def list_properties_v2(self, page_id, key=None, dry=None):
        return []

    def remove_property_v2(self, page_id, property_id, dry=None):
        self.removed.append(property_id)
        return True, None


def test_graceful_keyboardinterrupt_cleanup_runs(monkeypatch, tmp_path):
    """§8.5.2 ② (양 플랫폼 공통 — cooperative): 측정 중 KeyboardInterrupt →
    run_live finally 가 cleanup 실행 + abort 이벤트(orphan snapshot) 기록.

    win32 에서는 특정 pid SIGINT 전달이 불가하므로 cooperative 주입이 **대체 경로 그 자체**다
    (조용한 비활성화 아님 — 본 테스트는 모든 플랫폼에서 실행된다)."""
    monkeypatch.setattr(measure, "scratch_dir", lambda: tmp_path)   # golden 후보 잔재 격리
    ctx = measure.RunContext("graceful", events_path=tmp_path / "events.ndjson")
    client = _GracefulFakeClient(ctx.accounting)

    def interrupted_w1(client_, ctx_, page_id_, dry_):
        ctx_.register_orphan(f"{PROPERTY_KEY_PREFIX}.__gprobe", property_id=77)
        raise KeyboardInterrupt()

    monkeypatch.setattr(measure, "scenario_w1", interrupted_w1)
    exit_code, results = measure.run_live(
        client, ctx, "999999999999", {"size_budget": True, "error_codes": False})
    assert exit_code == 1
    assert client.removed == [77], "KeyboardInterrupt 경로에서 cleanup 미실행 (P0-c)"
    events = _read_events(tmp_path / "events.ndjson")
    abort = [e for e in events if e["event"] == "abort"]
    assert len(abort) == 1
    assert any(o["key"].endswith("__gprobe") for o in abort[0]["orphan_registry"])
    assert results["operational_verdict"] == "ABORTED"


def test_graceful_posix_real_sigint(tmp_path):
    """§8.5.2 ② POSIX 추가 분기: 실 SIGINT 를 자식에 전달 — KeyboardInterrupt 승격 경로.

    platform-explicit 분기 (skip 금지): win32 에서는 특정 pid SIGINT 전달 자체가 불가하므로
    본 분기는 **kill() 등가로 강등해 write-ahead 불변식만 재확인**한다 (graceful 축은 위
    cooperative 테스트가 win32 포함 전 플랫폼에서 이미 커버). POSIX 에서는 실 시그널로
    KeyboardInterrupt → driver 의 record_write_outcome 미도달을 확인한다."""
    events_path = tmp_path / "sigint-events.ndjson"
    proc = _spawn_driver(events_path, pause_seconds="30")
    try:
        assert _wait_for_event(events_path, "write_intent")
        if sys.platform == "win32":
            proc.kill()                               # win32 분기 — SIGKILL 등가 (명시 강등)
        else:
            proc.send_signal(signal.SIGINT)           # POSIX 분기 — 실 SIGINT
        proc.wait(timeout=15)
    finally:
        if proc.poll() is None:
            proc.kill()
    types = [e["event"] for e in _read_events(events_path)]
    assert "write_intent" in types
    assert "write_result" not in types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
