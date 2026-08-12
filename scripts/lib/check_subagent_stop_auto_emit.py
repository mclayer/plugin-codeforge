#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""check_subagent_stop_auto_emit.py — CFP-2926 NG-16 SubagentStop 자동 emit (AC-1 L1).

`stop-event-v1.md` §3.5 검증 2축:
  1. **등록면 축** — SubagentStop hook 이 실제로 등록돼 있는가 (`hooks/hooks.json`)
  2. **원장 축**   — stop_event 가 JSONL 원장에 append 됐는가
                    (`.claude/ledger/stop-event.jsonl`)

★§8.0.8 NG-16 규격★
  - empty-target : 세션 내 subagent 종료 **0건** → `INCONCLUSIVE`
                   (row diff 0 을 "자동 emit 정상"으로 읽지 않음 — mutant M-E 의
                    기대값이 정확히 `diff 0` 이라 ★양성/공백 구분 필수★)
  - unknown-input: 등록면 파싱 불가 → fail-closed RED (기본값 대체 금지)
  - trace        : 기대 종료 이벤트 수 · emit 된 row 수
  - identity_bearing: **true** — 채널 = `hooks.json` SubagentStop 등록면.
                   ★NG-12 와 동형 단일 실패점★ — 등록 블록 누락 = 전건 침묵

★★born-broken 정정 이력 (CFP-2926 Phase 2 — DeveloperPL firsthand 검출)★★
  종전 구현은 ★정상 등록된 hook 을 원리적으로 검출하지 못했다★:
    (1) **경로 오류** — `os.path.join(repo_root, "hooks.json")` 을 봤으나 실제
        등록면은 ★`hooks/hooks.json`★ 이다 ⇒ `isfile` False 로 즉시 미등록 반환,
        파싱 로직에 **도달조차 못 함**.
    (2) **구조 오인** — 경로를 고쳐도 실패. 실제 구조는
        `{"hooks": {"SessionStart":…, "SubagentStop":[…]}}` 로 `data["hooks"]` 가
        ★dict★ 인데 종전 분기는 `list` 를 가정했고, 최상위 `"SubagentStop" in data`
        도 미스였다.
  ⇒ 결과: `hooks/hooks.json:183` 에 SubagentStop 이 **정상 등록**돼 있는데도
     `hook_registered: false` → ★false RED★. **어떤 입력에도 항상 RED** 였으므로
     등록/미등록을 구분하지 못했다 = ★판별력 0★. ★항상 RED 인 게이트는 항상 GREEN
     인 게이트와 똑같이 hollow★ 이며, 본 행이 스스로 경고한 "등록 블록 누락 = 전건
     침묵" 을 게이트 자신이 재현한 형상이었다.
  ⇒ 정정: 등록면 후보를 **우선순위대로 resolve** 하고, ★resolve 된 경로를
     `identity_probe` 에 echo★ 하며([154-AC-13]), dict/list 두 구조를 모두 훑는다.

★정직 천장 — 본 게이트가 검출하지 못하는 축★
  - 등록 **선언**만 확인한다 — hook 이 실제로 **발화**했는지는 원장 축이 간접
    증거일 뿐이며, 등록돼 있고 원장에 행이 있어도 그 행이 **이 hook 이 쓴 것**
    인지는 대조하지 않는다(행 provenance 미검증).
  - `--expected-stops` 미지정 시 "종료 0건(공백)" 과 "종료가 있었는데 emit 0
    (자동 경로 사망)" 은 ★원장 축만으로는 구별 불가★ 하며, 구별은 **등록면 축**
    에만 의존한다 — 등록은 살아있는데 발화만 죽은 형상은 미탐이다.
  - "100% 기계강제" 아님.

exit codes: 0=PASS, 1=RED, 3=INCONCLUSIVE
"""

import argparse
import json
import os
import sys

from gate_verdict import (
    GateResult, emit, RED, PASS, empty_target, unknown_input
)

# Windows cp949 stdout/stderr 인코딩 차단 — UTF-8 강제
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

GATE_ID = "NG-16"

# ★등록면 후보 — 우선순위대로 resolve 하고 resolved 경로를 probe 에 echo 한다★
# 1순위 = wrapper 실제 등록면. 2순위 = repo 루트(구 구현 가정 · consumer overlay).
_HOOKS_REGISTRATION_CANDIDATES = (
    os.path.join("hooks", "hooks.json"),
    "hooks.json",
    os.path.join(".claude", "hooks.json"),
)

_STOP_EVENT_LEDGER_REL = os.path.join(".claude", "ledger", "stop-event.jsonl")

_EVENT_NAME = "SubagentStop"


def _resolve_registration_file(repo_root):
    """등록면 파일을 우선순위대로 resolve. Returns: (abs_path or None, rel or None)."""
    for rel in _HOOKS_REGISTRATION_CANDIDATES:
        path = os.path.join(repo_root, rel)
        if os.path.isfile(path):
            return path, rel
    return None, None


def _find_subagent_stop_block(data):
    """파싱된 등록 payload 에서 SubagentStop 블록을 찾는다.

    지원 구조 (실제 구조를 **먼저** 시도하고 구 fallback 을 보존):
      A. `{"hooks": {"SubagentStop": [...]}}`  ← ★Claude Code 실제 구조★
      B. `{"SubagentStop": [...]}`             ← 평면 dict
      C. `{"hooks": [{"event_type": "SubagentStop", ...}]}` ← list-of-dict
      D. `[{"event_type": "SubagentStop", ...}]`            ← 최상위 list

    Returns: (found: bool, block, shape: str)
    """
    if isinstance(data, dict):
        inner = data.get("hooks")
        # A — hooks 값이 dict (event 이름 → 등록 배열)
        if isinstance(inner, dict) and _EVENT_NAME in inner:
            return True, inner[_EVENT_NAME], "hooks.dict"
        # B — 평면 dict
        if _EVENT_NAME in data:
            return True, data[_EVENT_NAME], "flat.dict"
        # C — hooks 값이 list
        if isinstance(inner, list):
            for item in inner:
                if isinstance(item, dict) and item.get("event_type") == _EVENT_NAME:
                    return True, item, "hooks.list"
        return False, None, "dict.no-match"

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("event_type") == _EVENT_NAME:
                return True, item, "top.list"
        return False, None, "list.no-match"

    return False, None, "unknown-root"


def _check_hooks_registration(repo_root):
    """등록면 축 판정.

    Returns: dict —
        `resolved_rel`(str|None) · `file_found`(bool) · `parse_error`(str|None) ·
        `registered`(bool) · `shape`(str|None)
    """
    path, rel = _resolve_registration_file(repo_root)
    if path is None:
        return {
            "resolved_rel": None, "file_found": False,
            "parse_error": None, "registered": False, "shape": None,
        }

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        # ★파싱 실패를 '미등록 아님' 으로 흡수하지 않는다 — unknown-input fail-closed★
        return {
            "resolved_rel": rel, "file_found": True,
            "parse_error": "%s: %s" % (type(e).__name__, str(e)[:80]),
            "registered": False, "shape": None,
        }

    found, _block, shape = _find_subagent_stop_block(data)
    return {
        "resolved_rel": rel, "file_found": True, "parse_error": None,
        "registered": bool(found), "shape": shape,
    }


def _check_stop_event_ledger(repo_root):
    """원장 축 — stop-event.jsonl 행 수. Returns: (has_ledger, row_count)."""
    ledger_path = os.path.join(repo_root, _STOP_EVENT_LEDGER_REL)
    if not os.path.isfile(ledger_path):
        return False, 0
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            return True, sum(1 for line in f if line.strip())
    except Exception:
        return False, 0


def main(argv=None):
    """Main entry point.

    CLI:
      python check_subagent_stop_auto_emit.py --repo-root <path> [--expected-stops N]

    판정 순서 (명시 분기):
      1. 등록면 파일 부재            → RED `hooks_registration_file_not_found`
      2. 등록면 파싱 불가            → RED `hooks_registration_unparseable` (fail-closed)
      3. SubagentStop 미등록         → RED `subagent_stop_hook_not_registered`
      4. `--expected-stops 0`        → INCONCLUSIVE `no_subagent_stops_expected` (공백)
      5. `--expected-stops N>0` ∧ row 0 → RED `stop_event_emit_missing`
                                        ★양성/공백 구분의 기계면★
      6. 원장 부재 / 행 0 (기대 미지) → INCONCLUSIVE (`0 == 0` 을 GREEN 으로 안 읽음)
      7. 그 외                       → PASS
    """
    parser = argparse.ArgumentParser(
        prog="check_subagent_stop_auto_emit.py",
        description="SubagentStop 등록면 + stop_event 원장 append 검사 (AC-1 L1 / NG-16).",
    )
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    parser.add_argument(
        "--expected-stops", type=int, default=None,
        help="세션 내 기대 subagent 종료 이벤트 수. 지정 시 '공백(0건)' 과 "
             "'자동 경로 사망(N건인데 emit 0)' 을 기계로 가른다. 미지정 시 그 구분은 "
             "등록면 축에만 의존한다(정직 천장).",
    )

    try:
        args = parser.parse_args(argv[1:] if argv else [])
    except SystemExit:
        return 2

    repo_root = os.path.abspath(args.repo_root)
    expected_stops = args.expected_stops

    reg = _check_hooks_registration(repo_root)
    ledger_exists, row_count = _check_stop_event_ledger(repo_root)

    trace = {
        "hook_registered": reg["registered"],
        "ledger_exists": ledger_exists,
        "ledger_row_count": row_count,
        "expected_stop_count": expected_stops,
        "registration_candidate_count": len(_HOOKS_REGISTRATION_CANDIDATES),
    }
    # ★[154-AC-13]★ 실제로 무엇을 봤는지 — 경로 오타/미도달이 vacuous 판정이 되지
    # 않도록 resolve 결과를 그대로 echo 한다(종전 born-broken 의 직접 원인).
    probe = {
        "repo_root": repo_root,
        "registration_candidates": list(_HOOKS_REGISTRATION_CANDIDATES),
        "resolved_registration_file": reg["resolved_rel"],
        "registration_shape": reg["shape"],
        "ledger_path": _STOP_EVENT_LEDGER_REL,
    }

    # --- 1. 등록면 파일 부재 (채널 미도달) ---------------------------------
    if not reg["file_found"]:
        return emit(GateResult(
            gate_id=GATE_ID, verdict=RED,
            reason="hooks_registration_file_not_found",
            trace=trace, identity_probe=probe,
        ))

    # --- 2. 등록면 파싱 불가 (unknown-input fail-closed) --------------------
    if reg["parse_error"] is not None:
        probe_err = dict(probe)
        probe_err["parse_error"] = reg["parse_error"]
        return emit(unknown_input(
            gate_id=GATE_ID,
            reason="hooks_registration_unparseable",
            trace=trace, identity_probe=probe_err,
        ))

    # --- 3. SubagentStop 미등록 (자동 경로 사망) ----------------------------
    if not reg["registered"]:
        return emit(GateResult(
            gate_id=GATE_ID, verdict=RED,
            reason="subagent_stop_hook_not_registered",
            trace=trace, identity_probe=probe,
        ))

    # --- 4-5. 기대 종료 수와 대조 (양성/공백 구분의 기계면) -----------------
    if expected_stops is not None:
        if expected_stops < 0:
            return emit(unknown_input(
                gate_id=GATE_ID, reason="expected_stops_negative",
                trace=trace, identity_probe=probe,
            ))
        if expected_stops == 0:
            return emit(empty_target(
                gate_id=GATE_ID, reason="no_subagent_stops_expected",
                trace=trace, identity_probe=probe,
            ))
        if row_count == 0:
            # 종료는 있었는데 emit 이 0 — ★공백(INCONCLUSIVE) 으로 흡수 금지★
            return emit(GateResult(
                gate_id=GATE_ID, verdict=RED,
                reason="stop_event_emit_missing",
                trace=trace, identity_probe=probe,
            ))

    # --- 6. 원장 축 공백 (기대 미지) → non-GREEN ----------------------------
    if not ledger_exists:
        return emit(empty_target(
            gate_id=GATE_ID, reason="stop_event_ledger_absent",
            trace=trace, identity_probe=probe,
        ))

    if row_count == 0:
        return emit(empty_target(
            gate_id=GATE_ID, reason="stop_event_ledger_empty",
            trace=trace, identity_probe=probe,
        ))

    # --- 7. PASS ------------------------------------------------------------
    return emit(GateResult(
        gate_id=GATE_ID, verdict=PASS,
        reason="subagent_stop_hook_and_ledger_present",
        trace=trace, identity_probe=probe,
    ))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
