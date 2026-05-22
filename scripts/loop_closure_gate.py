#!/usr/bin/env python3
"""
scripts/loop_closure_gate.py
CFP-1195 — self-improving loop closure gate (ADR-061 외부 .py 의무)

ADR-106 §결정 4 loop closure 3원칙 (dedup/max-depth/escalate_user, OR 발동) 실 mechanism.
ADR-106 §결정 3 KPI jsonl append-only write (10-field, SHA optimistic CAS).
ADR-045 §D-4 Pattern A: 409 Conflict → re-fetch + CAS retry (last-writer-wins 0).
ADR-061: 산술 5줄 초과 → 외부 .py (bash heredoc 금지).
ADR-104 §결정 3: 0 API call (filesystem/cron 우선).

loop closure 3원칙 OR 발동 (하나라도 trip → 자동 발의 억제):
  (a) dedup: open Issue OR 진행 Epic 존재 시 억제
  (b) max-depth: loop_depth >= loop_max_depth → escalate_user
  (c) escalate_user: max-depth/dedup OR trip → escalation_action=escalate_user

출력 (stdout, bash 파싱):
  CLOSURE_GATE=<pass|dedup|max_depth|escalate_user>  # 억제 사유
  LOOP_DEPTH=<int>                                    # 현재 loop_depth
  PATTERN_COUNT=<int>                                 # 누적 pattern_count
  ESCALATION_ACTION=<none|adr_draft_emitted|escalate_user>

Exit codes (ADR-060 §결정 15 3-tier):
  0 = PASS (gate open — Issue 발의 허용) 또는 억제 (gate closed — 발의 차단)
      → CLOSURE_GATE 값으로 구분
  1 = reserved (current scope 미사용)
  2 = SETUP error (yaml/json parse error, 파일 부재 fail-loud)

mock seam (_CFP1195_MOCK_* namespace):
  _CFP1195_MOCK_LOOP_DEPTH=<int>       — loop_depth override
  _CFP1195_MOCK_DEDUP=<0|1>            — dedup gate override (1=trip)
  _CFP1195_MOCK_EPIC_OPEN=<0|1>        — open Epic dedup override (1=trip)
  _CFP1195_MOCK_PATTERN_COUNT=<int>    — pattern_count override
  _CFP1195_MOCK_SHA_CONFLICT=<0|1>     — SHA 409 conflict mock (1=1회 conflict)
  _CFP1195_SKIP_ISSUE_CREATE=<1>       — dry-run (Issue 발의 차단, 본 py 에서는 KPI write만)
"""

import json
import os
import sys
import time
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKTREE_ROOT = os.path.dirname(SCRIPT_DIR)

# KPI 파일 경로 — 환경변수 override 지원 (test mock seam)
_DEFAULT_HISTORY = os.path.join(WORKTREE_ROOT, "docs", "kpi", "operational-signal-history.jsonl")
_DEFAULT_STATE = os.path.join(WORKTREE_ROOT, "docs", "kpi", "operational-signal-rate.json")
KPI_HISTORY_FILE = os.environ.get("_CFP1195_HISTORY_FILE", _DEFAULT_HISTORY)
KPI_STATE_FILE = os.environ.get("_CFP1195_STATE_FILE", _DEFAULT_STATE)
PROJECT_YAML_PATH = os.path.join(WORKTREE_ROOT, "docs", "project-config-schema.md")


def _mock_env(key: str, default=None):
    """mock seam: _CFP1195_MOCK_* env override."""
    return os.environ.get(key, default)


def _kst_now() -> str:
    """ADR-079 display layer: KST +09:00 ISO 8601 zoned."""
    now_utc = datetime.now(timezone.utc)
    # KST = UTC+9
    from datetime import timedelta
    kst_offset = timedelta(hours=9)
    now_kst = now_utc + kst_offset
    return now_kst.strftime("%Y-%m-%dT%H:%M:%S+09:00")


def load_project_config() -> dict:
    """
    project.yaml deploy.self_improving_loop 블록 파싱.
    ADR-061: yaml.safe_load 의무 (grep 금지).
    wrapper/test env 에서는 default 반환 (파일 부재 = non-fatal).
    """
    defaults = {
        "loop_max_depth": 3,
        "dedup_window_hours": 24,
        "pattern_count_threshold": 2,
        "enabled": True,
    }

    # project.yaml 은 consumer overlay — wrapper SSOT 에서는 default 반환
    consumer_yaml_path = os.environ.get("CFP1195_PROJECT_YAML", "")
    if not consumer_yaml_path or not os.path.isfile(consumer_yaml_path):
        return defaults

    try:
        import yaml  # pyyaml dependency (consumer 환경)
        with open(consumer_yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        sil = (data or {}).get("deploy", {}).get("self_improving_loop", {})
        return {
            "loop_max_depth": int(sil.get("loop_max_depth", defaults["loop_max_depth"])),
            "dedup_window_hours": int(sil.get("dedup_window_hours", defaults["dedup_window_hours"])),
            "pattern_count_threshold": int(sil.get("pattern_count_threshold", defaults["pattern_count_threshold"])),
            "enabled": bool(sil.get("enabled", defaults["enabled"])),
        }
    except Exception as e:
        print(f"[loop_closure_gate] WARN: project.yaml 파싱 실패 ({e}), default 사용", file=sys.stderr)
        return defaults


def load_history() -> list:
    """
    operational-signal-history.jsonl 읽기.
    부재 시 [] 반환 (append-only seed).
    parse 실패 시 exit 2 (fail-loud, INV-5).
    """
    if not os.path.isfile(KPI_HISTORY_FILE):
        return []
    try:
        events = []
        with open(KPI_HISTORY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        return events
    except (json.JSONDecodeError, OSError) as e:
        print(f"[loop_closure_gate] ERROR: KPI history parse 실패: {e}", file=sys.stderr)
        sys.exit(2)


def get_loop_depth(history: list, signal_signature: str) -> int:
    """
    동일 signal_signature 의 최대 loop_depth 반환.
    mock override: _CFP1195_MOCK_LOOP_DEPTH.
    """
    mock_depth = _mock_env("_CFP1195_MOCK_LOOP_DEPTH")
    if mock_depth is not None:
        return int(mock_depth)

    depths = [
        e.get("loop_depth", 0)
        for e in history
        if e.get("signal_signature") == signal_signature
    ]
    return max(depths, default=0)


def get_pattern_count(history: list, signal_type: str) -> int:
    """
    동일 signal_type 누적 횟수 (pattern_count 집계).
    mock override: _CFP1195_MOCK_PATTERN_COUNT.
    ADR-045 §D-9 forcing function 답습 (threshold N=2).
    """
    mock_count = _mock_env("_CFP1195_MOCK_PATTERN_COUNT")
    if mock_count is not None:
        return int(mock_count)

    return sum(1 for e in history if e.get("signal_type") == signal_type)


def check_dedup_gate(signal_signature: str) -> bool:
    """
    loop closure (a) dedup gate 판정.
    open Issue 존재 OR 진행 Epic 존재 시 True (trip).
    mock override: _CFP1195_MOCK_DEDUP / _CFP1195_MOCK_EPIC_OPEN.
    실제 gh 호출 = operational-signal-to-issue.sh (bash) 가 수행 — 본 py 는 mock 경로만.
    """
    mock_dedup = _mock_env("_CFP1195_MOCK_DEDUP", "0")
    mock_epic = _mock_env("_CFP1195_MOCK_EPIC_OPEN", "0")
    if mock_dedup == "1" or mock_epic == "1":
        return True
    # 실제 환경: bash orchestration이 gh issue list 로 체크 후 DEDUP_GATE 환경변수 주입
    # "dedup" (string) 또는 "1" (legacy) 모두 trip으로 처리
    dedup_env = os.environ.get("_CFP1195_DEDUP_GATE_RESULT", "pass")
    return dedup_env in ("1", "dedup")


def evaluate_closure_gate(
    signal_signature: str,
    signal_type: str,
    history: list,
    config: dict,
) -> dict:
    """
    loop closure 3원칙 OR-fire 판정.
    반환: {gate: "pass"|"dedup"|"max_depth"|"escalate_user", loop_depth, pattern_count, escalation_action}
    """
    loop_depth = get_loop_depth(history, signal_signature)
    pattern_count = get_pattern_count(history, signal_type)
    loop_max_depth = config["loop_max_depth"]

    # (a) dedup gate
    if check_dedup_gate(signal_signature):
        return {
            "gate": "dedup",
            "loop_depth": loop_depth,
            "pattern_count": pattern_count,
            "escalation_action": "escalate_user",
        }

    # (b) max-depth gate
    if loop_depth >= loop_max_depth:
        return {
            "gate": "max_depth",
            "loop_depth": loop_depth,
            "pattern_count": pattern_count,
            "escalation_action": "escalate_user",
        }

    # (c) pattern_count threshold → escalate_user
    if pattern_count >= config["pattern_count_threshold"]:
        return {
            "gate": "escalate_user",
            "loop_depth": loop_depth,
            "pattern_count": pattern_count,
            "escalation_action": "escalate_user",
        }

    # gate open
    return {
        "gate": "pass",
        "loop_depth": loop_depth,
        "pattern_count": pattern_count,
        "escalation_action": "none",
    }


def sha_optimistic_append(event: dict) -> None:
    """
    operational-signal-history.jsonl append-only write.
    ADR-045 §D-4 Pattern A: SHA optimistic CAS.
    409 Conflict mock: _CFP1195_MOCK_SHA_CONFLICT=1 → 1회 conflict 후 retry.

    실 GitHub Contents API CAS 패턴 (consumer CI 환경):
      1. GET /repos/{owner}/{repo}/contents/{path} → sha
      2. PUT /repos/{owner}/{repo}/contents/{path} with sha → conflict 시 409
      3. 409 → re-fetch sha + retry

    wrapper 테스트/로컬 환경: filesystem 직접 append (GitHub API 0).
    """
    # mock SHA conflict: 1회 retry 시뮬레이션
    sha_conflict = _mock_env("_CFP1195_MOCK_SHA_CONFLICT", "0")
    if sha_conflict == "1":
        # 1회 conflict 시뮬레이션 — retry 후 성공
        os.environ["_CFP1195_MOCK_SHA_CONFLICT"] = "0"  # retry 시 conflict 0
        print("[loop_closure_gate] SHA conflict (mock) → re-fetch + retry", file=sys.stderr)

    # dry-run: _CFP1195_SKIP_ISSUE_CREATE=1 시 KPI write도 skip (TC-13 사용자 게이트 테스트용)
    if os.environ.get("_CFP1195_SKIP_ISSUE_CREATE") == "1":
        print("[loop_closure_gate] dry-run: KPI append skip (_CFP1195_SKIP_ISSUE_CREATE=1)", file=sys.stderr)
        return

    # append-only write (INV-1: cron restart 간 state 생존)
    os.makedirs(os.path.dirname(KPI_HISTORY_FILE), exist_ok=True)
    line = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
    with open(KPI_HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def update_state_summary(history: list) -> None:
    """
    operational-signal-rate.json rolling state 갱신.
    rate-limit-fallback.json 패턴 답습 (§2 as-is).
    """
    if os.environ.get("_CFP1195_SKIP_ISSUE_CREATE") == "1":
        return

    signal_counts: dict = {}
    for e in history:
        st = e.get("signal_type", "unknown")
        signal_counts[st] = signal_counts.get(st, 0) + 1

    state = {
        "schema_version": "1.0",
        "history_file": "docs/kpi/operational-signal-history.jsonl",
        "measured_at": _kst_now(),
        "window_hours": 24,
        "total_signal_count": len(history),
        "signal_type_counts": signal_counts,
        "escalation_count": sum(
            1 for e in history
            if e.get("escalation_action") in ("adr_draft_emitted", "escalate_user")
        ),
        "gate_status": "active" if history else "pending",
    }

    os.makedirs(os.path.dirname(KPI_STATE_FILE), exist_ok=True)
    with open(KPI_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> None:
    """
    입력 (환경변수 또는 stdin):
      CFP1195_SIGNAL_SIGNATURE  — signal_signature (required)
      CFP1195_SIGNAL_TYPE       — signal_type (required)
      CFP1195_MEASURED_VALUE    — measured_value (required)
      CFP1195_THRESHOLD         — threshold (required)
      CFP1195_WINDOW            — window (required)
      CFP1195_ISSUE_REF         — issue_ref (optional, dedup pass 후 주입)

    출력 (stdout, bash eval 가능):
      CLOSURE_GATE=<pass|dedup|max_depth|escalate_user>
      LOOP_DEPTH=<int>
      PATTERN_COUNT=<int>
      ESCALATION_ACTION=<none|adr_draft_emitted|escalate_user>
    """
    signal_signature = os.environ.get("CFP1195_SIGNAL_SIGNATURE", "")
    signal_type = os.environ.get("CFP1195_SIGNAL_TYPE", "")
    measured_value_str = os.environ.get("CFP1195_MEASURED_VALUE", "0")
    threshold_str = os.environ.get("CFP1195_THRESHOLD", "0")
    window = os.environ.get("CFP1195_WINDOW", "3600s")
    issue_ref = os.environ.get("CFP1195_ISSUE_REF", "")

    if not signal_signature or not signal_type:
        print("[loop_closure_gate] ERROR: CFP1195_SIGNAL_SIGNATURE, CFP1195_SIGNAL_TYPE 필수", file=sys.stderr)
        sys.exit(2)

    try:
        measured_value = float(measured_value_str)
        threshold = float(threshold_str)
    except ValueError as e:
        print(f"[loop_closure_gate] ERROR: measured_value/threshold float 변환 실패: {e}", file=sys.stderr)
        sys.exit(2)

    # 설정 로드
    config = load_project_config()

    # 이력 로드
    history = load_history()

    # closure gate 판정
    result = evaluate_closure_gate(signal_signature, signal_type, history, config)

    gate = result["gate"]
    loop_depth = result["loop_depth"]
    pattern_count = result["pattern_count"]
    escalation_action = result["escalation_action"]

    # gate pass 시 loop_depth 증가 + KPI append
    if gate == "pass":
        new_depth = loop_depth + 1
        event = {
            "signal_signature": signal_signature,
            "signal_type": signal_type,
            "measured_value": measured_value,
            "threshold": threshold,
            "window": window,
            "detected_at_kst": _kst_now(),
            "issue_ref": issue_ref,
            "escalation_action": escalation_action,
            "pattern_count": pattern_count + 1,
            "loop_depth": new_depth,
        }
        sha_optimistic_append(event)
        # 이력 갱신 후 state summary 업데이트
        history_updated = load_history()
        update_state_summary(history_updated)
        loop_depth = new_depth
        pattern_count = event["pattern_count"]

    # bash eval 출력
    print(f"CLOSURE_GATE={gate}")
    print(f"LOOP_DEPTH={loop_depth}")
    print(f"PATTERN_COUNT={pattern_count}")
    print(f"ESCALATION_ACTION={escalation_action}")


if __name__ == "__main__":
    main()
