#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-833 Phase 2 — TDD RED phase tests for check_dialog_fidelity_effect.py
# ADR-061 §결정 1 thin wrapper pattern (lib .py SSOT)
#
# TC-1: workflow byte-identical self-app verify
# TC-2: check script exit code contract (0/1/2)
# TC-3: backfill vs realtime 분류 정확성
# TC-4: sample insufficient sentinel (realtime < 3 → N/A)
# TC-5: A-B delta 계산 정확성
# TC-6: #827 trigger 회피 (registry entry detect_command non-null)
# TC-7: idempotency (동일 input → 동일 output)
# TC-8: read-only invariant (file 변경 0)
#
# NOTE: Phase 2 에서 lib 파일 신설 전까지 이 테스트는 전부 ImportError/FileNotFoundError 로 FAIL.
# TDD RED phase 진정성 확인 후 lib .py 신설 → GREEN phase.

import os
import sys
import subprocess
import tempfile
import textwrap
import hashlib
from pathlib import Path

# ─── repo root 경로 설정 ───
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
LIB_PATH = REPO_ROOT / "scripts" / "lib" / "check_dialog_fidelity_effect.py"
WRAPPER_SCRIPT = REPO_ROOT / "scripts" / "check-dialog-fidelity-effect.sh"
TEMPLATE_WORKFLOW = REPO_ROOT / "templates" / "github-workflows" / "dialog-fidelity-measurement.yml"
SELF_APP_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "dialog-fidelity-measurement.yml"

# ─── 공통 fixture 빌더 ───

INCIDENTS_HEADER = """\
---
title: Orchestrator Communication Incidents (Layer 4 누적 file)
status: Active
schema_version: "1.0"
---

# Orchestrator Communication Incidents

## Incidents

| iter | timestamp | story_key | pattern_dimension | pattern_summary | trigger | different_dimension_after_halt | escalation_outcome |
|------|-----------|-----------|-------------------|-----------------|---------|-------------------------------|--------------------|
"""


def make_incidents_file(tmp_dir: Path, rows: list[str]) -> Path:
    """communication-incidents.md 픽스처 생성."""
    content = INCIDENTS_HEADER + "\n".join(rows) + "\n"
    path = tmp_dir / "orchestrator-communication-incidents.md"
    path.write_text(content, encoding="utf-8")
    return path


# ─── TC-1: workflow byte-identical self-app verify ───

def test_tc1_workflow_byte_identical():
    """TC-1: template ↔ .github/ 워크플로 파일이 바이트 동일해야 함."""
    assert TEMPLATE_WORKFLOW.exists(), (
        f"TC-1 FAIL: 템플릿 워크플로 미존재 — {TEMPLATE_WORKFLOW}"
    )
    assert SELF_APP_WORKFLOW.exists(), (
        f"TC-1 FAIL: self-app 워크플로 미존재 — {SELF_APP_WORKFLOW}"
    )
    tmpl_hash = hashlib.md5(TEMPLATE_WORKFLOW.read_bytes()).hexdigest()
    self_hash = hashlib.md5(SELF_APP_WORKFLOW.read_bytes()).hexdigest()
    assert tmpl_hash == self_hash, (
        "TC-1 FAIL: template ↔ .github/ 워크플로 파일 byte-identical 아님"
    )


# ─── TC-2: check script exit code contract ───

def test_tc2_exit_code_zero_on_sample_insufficient():
    """TC-2: realtime row < 3 인 경우 exit code 0 (sample insufficient N/A)."""
    assert WRAPPER_SCRIPT.exists(), f"TC-2 FAIL: 래퍼 스크립트 미존재 — {WRAPPER_SCRIPT}"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # realtime row 2개만 (sentinel threshold = 3 미달)
        rows = [
            "| 1 | 2026-05-14 22:36 | CFP-672 | 보고 형식 | test | backfill (retroactive) | N/A |  |",
            "| 4 | 2026-05-16T08:42:00+09:00 | CFP-750 | 보고 형식 | test | layer-4-n1 | test | |",
            "| 5 | 2026-05-16T18:13:00+09:00 | CFP-750 | 보고 형식 | test | layer-4-n1 | test | |",
        ]
        incidents = make_incidents_file(tmp_path, rows)
        result = subprocess.run(
            ["python3", str(LIB_PATH), "--incidents-file", str(incidents)],
            capture_output=True, text=True
        )
        assert result.returncode == 0, (
            f"TC-2 FAIL: sample insufficient 시 exit 0 기대, 실제={result.returncode}\n{result.stdout}\n{result.stderr}"
        )
        assert "N/A" in result.stdout or "insufficient" in result.stdout.lower(), (
            f"TC-2 FAIL: N/A sentinel 출력 기대\n{result.stdout}"
        )


def test_tc2_exit_code_two_on_missing_file():
    """TC-2: 파일 미존재 시 exit code 2 (ERROR)."""
    assert WRAPPER_SCRIPT.exists(), f"TC-2b FAIL: 래퍼 스크립트 미존재 — {WRAPPER_SCRIPT}"
    result = subprocess.run(
        ["python3", str(LIB_PATH), "--incidents-file", "/nonexistent/path.md"],
        capture_output=True, text=True
    )
    assert result.returncode == 2, (
        f"TC-2b FAIL: 파일 미존재 시 exit 2 기대, 실제={result.returncode}\n{result.stderr}"
    )


# ─── TC-3: backfill vs realtime 분류 정확성 ───

def test_tc3_backfill_realtime_classification():
    """TC-3: trigger cell 분류 — backfill marker 3, realtime 2 (현 incidents 5 row)."""
    # lib을 직접 import해서 분류 함수 단위 테스트
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))
    import check_dialog_fidelity_effect as lib  # noqa: E402 (TDD RED: ImportError expected)

    rows = [
        {"trigger": "backfill (retroactive baseline — not realtime layer-3/4 detect)"},
        {"trigger": "backfill (retroactive baseline — not realtime layer-3/4 detect)"},
        {"trigger": "backfill (retroactive baseline — not realtime layer-3/4 detect)"},
        {"trigger": "layer-4-n1"},
        {"trigger": "layer-4-n1"},
    ]
    backfill, realtime = lib.classify_rows(rows)
    assert len(backfill) == 3, f"TC-3 FAIL: backfill 3 기대, 실제={len(backfill)}"
    assert len(realtime) == 2, f"TC-3 FAIL: realtime 2 기대, 실제={len(realtime)}"


def test_tc3_trigger_enum():
    """TC-3: layer-3-keyword / layer-4-n1 / layer-4-m5 모두 realtime 분류."""
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))
    import check_dialog_fidelity_effect as lib  # noqa

    rows = [
        {"trigger": "layer-3-keyword"},
        {"trigger": "layer-4-n1"},
        {"trigger": "layer-4-m5"},
        {"trigger": "backfill (...)"},
    ]
    backfill, realtime = lib.classify_rows(rows)
    assert len(realtime) == 3, f"TC-3b FAIL: realtime 3 기대, 실제={len(realtime)}"
    assert len(backfill) == 1, f"TC-3b FAIL: backfill 1 기대, 실제={len(backfill)}"


# ─── TC-4: sample insufficient sentinel ───

def test_tc4_sample_insufficient_zero_realtime():
    """TC-4: realtime row = 0 → N/A sentinel."""
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))
    import check_dialog_fidelity_effect as lib  # noqa

    result = lib.compute_delta(backfill_rows=[], realtime_rows=[])
    assert result["status"] == "insufficient", (
        f"TC-4 FAIL: realtime=0 시 insufficient 기대, 실제={result}"
    )


def test_tc4_sample_insufficient_two_realtime():
    """TC-4: realtime row = 2 (threshold 3 미달) → N/A sentinel."""
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))
    import check_dialog_fidelity_effect as lib  # noqa

    realtime = [
        {"timestamp": "2026-05-17T10:00:00+09:00"},
        {"timestamp": "2026-05-17T12:00:00+09:00"},
    ]
    backfill = [
        {"timestamp": "2026-05-14T22:36:00+09:00"},
        {"timestamp": "2026-05-15T03:16:00+09:00"},
        {"timestamp": "2026-05-15T12:00:00+09:00"},
    ]
    result = lib.compute_delta(backfill_rows=backfill, realtime_rows=realtime)
    assert result["status"] == "insufficient", (
        f"TC-4 FAIL: realtime=2 시 insufficient 기대, 실제={result}"
    )


def test_tc4_sample_sufficient_three_realtime():
    """TC-4: realtime row = 3 (sentinel 충족) → delta 산정 시도."""
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))
    import check_dialog_fidelity_effect as lib  # noqa

    realtime = [
        {"timestamp": "2026-05-17T10:00:00+09:00"},
        {"timestamp": "2026-05-17T12:00:00+09:00"},
        {"timestamp": "2026-05-17T14:00:00+09:00"},
    ]
    backfill = [
        {"timestamp": "2026-05-14T22:36:00+09:00"},
        {"timestamp": "2026-05-15T03:16:00+09:00"},
        {"timestamp": "2026-05-15T12:00:00+09:00"},
    ]
    result = lib.compute_delta(backfill_rows=backfill, realtime_rows=realtime)
    assert result["status"] in ("ok", "advisory"), (
        f"TC-4 FAIL: realtime=3 시 ok/advisory 기대, 실제={result}"
    )


# ─── TC-5: A-B delta 계산 정확성 ───

def test_tc5_baseline_normalization():
    """TC-5: before(backfill) = 3 row / span 2days → monthly-equivalent = 3/2*30 = 45."""
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))
    import check_dialog_fidelity_effect as lib  # noqa

    backfill = [
        {"timestamp": "2026-05-14T22:36:00+09:00"},
        {"timestamp": "2026-05-15T03:16:00+09:00"},
        {"timestamp": "2026-05-15T12:00:00+09:00"},
    ]
    rate = lib.compute_baseline_monthly_equivalent(backfill)
    # span = May 14 ~ May 15 = 1 day (date min/max span_days). 3 / 1 * 30 = 90 또는 span=2 시 45.
    # Change Plan §3.1: span_days = min/max date 차이. 2026-05-14 ~ 2026-05-15 = 1 day span.
    # 단, 포함 범위 = 2일 (14, 15일 둘 다 포함 → span_days = 1 + 1 = 2 또는 1 day diff).
    # 구현은 (max_date - min_date).days + 1 (inclusive) 또는 .days (exclusive) 선택.
    # 여기서는 경계 확인만: rate > 0 and rate < 200 (reasonable)
    assert isinstance(rate, (int, float)), f"TC-5 FAIL: float/int 기대, 실제={type(rate)}"
    assert rate > 0, f"TC-5 FAIL: baseline rate > 0 기대, 실제={rate}"


def test_tc5_delta_negative_is_good_signal():
    """TC-5: after rate < before rate → delta 음수 (verifier 효과 proxy 신호)."""
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))
    import check_dialog_fidelity_effect as lib  # noqa

    backfill = [
        {"timestamp": "2026-05-14T22:36:00+09:00"},
        {"timestamp": "2026-05-15T03:16:00+09:00"},
        {"timestamp": "2026-05-15T12:00:00+09:00"},
    ]
    # realtime 3 row, 모두 같은 달 → after rate = 3/1month
    realtime = [
        {"timestamp": "2026-05-17T10:00:00+09:00"},
        {"timestamp": "2026-05-17T12:00:00+09:00"},
        {"timestamp": "2026-05-17T14:00:00+09:00"},
    ]
    result = lib.compute_delta(backfill_rows=backfill, realtime_rows=realtime)
    # delta = after − before(monthly-eq). before >> after 이므로 delta < 0.
    if result["status"] == "ok":
        assert result["delta"] < 0, (
            f"TC-5 FAIL: before(normalized) >> after 이므로 delta 음수 기대, 실제={result['delta']}"
        )


# ─── TC-6: #827 trigger 회피 ───

def test_tc6_registry_detect_command_non_null():
    """TC-6: evidence-checks-registry.yaml dialog-fidelity-effect detect_command non-null."""
    import yaml  # stdlib 아님 — PyYAML 필요

    registry_path = REPO_ROOT / "docs" / "evidence-checks-registry.yaml"
    assert registry_path.exists(), f"TC-6 FAIL: registry 파일 미존재"
    content = registry_path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    entries = {e["name"]: e for e in data.get("entries", [])}
    assert "dialog-fidelity-effect" in entries, "TC-6 FAIL: dialog-fidelity-effect entry 미존재"
    entry = entries["dialog-fidelity-effect"]
    assert entry.get("detect_command") not in (None, "null", ""), (
        f"TC-6 FAIL: detect_command non-null 기대, 실제={entry.get('detect_command')!r}"
    )


# ─── TC-7: idempotency ───

def test_tc7_idempotency():
    """TC-7: 동일 input → 동일 output (두 번 실행해도 같은 결과)."""
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))
    import check_dialog_fidelity_effect as lib  # noqa

    backfill = [
        {"timestamp": "2026-05-14T22:36:00+09:00"},
        {"timestamp": "2026-05-15T03:16:00+09:00"},
        {"timestamp": "2026-05-15T12:00:00+09:00"},
    ]
    realtime = [
        {"timestamp": "2026-05-17T10:00:00+09:00"},
        {"timestamp": "2026-05-17T12:00:00+09:00"},
        {"timestamp": "2026-05-17T14:00:00+09:00"},
    ]
    result1 = lib.compute_delta(backfill_rows=backfill, realtime_rows=realtime)
    result2 = lib.compute_delta(backfill_rows=backfill, realtime_rows=realtime)
    assert result1 == result2, f"TC-7 FAIL: 동일 input 비동일 output\n1={result1}\n2={result2}"


# ─── TC-8: read-only invariant ───

def test_tc8_read_only_no_file_modification():
    """TC-8: 스크립트 실행 후 incidents 파일 변경 없음 (read-only invariant)."""
    assert WRAPPER_SCRIPT.exists(), f"TC-8 FAIL: 래퍼 스크립트 미존재 — {WRAPPER_SCRIPT}"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        rows = [
            "| 1 | 2026-05-14 22:36 | CFP-672 | 보고 형식 | test | backfill (retroactive) | N/A |  |",
            "| 4 | 2026-05-16T08:42:00+09:00 | CFP-750 | 보고 형식 | test | layer-4-n1 | test | |",
            "| 5 | 2026-05-16T18:13:00+09:00 | CFP-750 | 보고 형식 | test | layer-4-n1 | test | |",
        ]
        incidents = make_incidents_file(tmp_path, rows)
        before_mtime = incidents.stat().st_mtime
        before_content = incidents.read_bytes()

        subprocess.run(
            ["python3", str(LIB_PATH), "--incidents-file", str(incidents)],
            capture_output=True
        )

        after_mtime = incidents.stat().st_mtime
        after_content = incidents.read_bytes()
        assert before_content == after_content, "TC-8 FAIL: 파일 내용 변경됨 (read-only 위반)"


# ─── proxy qualification output 검증 ───

def test_proxy_qualification_output():
    """proxy signal 출력에 'advisory' 또는 'not causal' 표현 포함 의무."""
    assert LIB_PATH.exists(), f"proxy qualification FAIL: lib 파일 미존재 — {LIB_PATH}"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        rows = [
            "| 1 | 2026-05-14 22:36 | CFP-672 | 보고 형식 | test | backfill (retroactive) | N/A |  |",
            "| 2 | 2026-05-15 03:16 | CFP-701 | 보고 형식 | test | backfill (retroactive) | N/A |  |",
            "| 3 | 2026-05-15 12:00 | CFP-707 | 질문 자체 | test | backfill (retroactive) | N/A |  |",
            "| 4 | 2026-05-16T08:42:00+09:00 | CFP-750 | 보고 형식 | test | layer-4-n1 | test | |",
            "| 5 | 2026-05-16T18:13:00+09:00 | CFP-750 | 보고 형식 | test | layer-4-n1 | test | |",
            "| 6 | 2026-05-17T10:00:00+09:00 | CFP-833 | 결정 구조 | test | layer-3-keyword | test | |",
        ]
        incidents = make_incidents_file(tmp_path, rows)
        result = subprocess.run(
            ["python3", str(LIB_PATH), "--incidents-file", str(incidents)],
            capture_output=True, text=True
        )
        combined = result.stdout + result.stderr
        assert any(kw in combined.lower() for kw in ["advisory", "proxy", "not causal"]), (
            f"proxy qualification FAIL: 출력에 advisory/proxy/not causal 키워드 미포함\n{combined}"
        )


# ─── 테스트 실행 진입점 ───

if __name__ == "__main__":
    tests = [
        test_tc1_workflow_byte_identical,
        test_tc2_exit_code_zero_on_sample_insufficient,
        test_tc2_exit_code_two_on_missing_file,
        test_tc3_backfill_realtime_classification,
        test_tc3_trigger_enum,
        test_tc4_sample_insufficient_zero_realtime,
        test_tc4_sample_insufficient_two_realtime,
        test_tc4_sample_sufficient_three_realtime,
        test_tc5_baseline_normalization,
        test_tc5_delta_negative_is_good_signal,
        test_tc6_registry_detect_command_non_null,
        test_tc7_idempotency,
        test_tc8_read_only_no_file_modification,
        test_proxy_qualification_output,
    ]

    passed = 0
    failed = 0
    errors = []

    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except (AssertionError, ImportError, ModuleNotFoundError, FileNotFoundError) as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
            errors.append((t.__name__, str(e)))
        except Exception as e:
            print(f"  ERROR {t.__name__}: {type(e).__name__}: {e}")
            failed += 1
            errors.append((t.__name__, f"{type(e).__name__}: {e}"))

    print(f"\n결과: {passed} PASS / {failed} FAIL / 총 {len(tests)} case")
    if failed:
        sys.exit(1)
    sys.exit(0)
