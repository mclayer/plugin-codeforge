#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-442 Phase 2 / ADR-060 Amendment 11 §결정 25 — pytest test suite
# scripts/lib/check_evidence_registry_anomaly.py 단위 테스트
#
# TC-1 (mandatory): 현행 SSOT (docs/evidence-checks-registry.yaml) → exit 0 (PASS)
# TC-2 (mandatory): negative missing-entry fixture → exit 1 (anomaly DETECTED)
# TC-3 (mandatory): ALLOWLIST self-exempt in-place test → ALLOWLIST path 4개 미검출 확인
# TC-5 (optional): META-ERROR broken yaml → exit 2 (META-ERROR)
#
# 실행:
#   cd <worktree-root>
#   python -m pytest tests/scripts/check-evidence-registry-anomaly/test_check_evidence_registry_anomaly.py -v
import subprocess
import sys
from pathlib import Path

# worktree root 탐색 (tests/scripts/<dir> 3레벨 위)
THIS_DIR = Path(__file__).parent.resolve()
WORKTREE_ROOT = THIS_DIR.parent.parent.parent  # tests/scripts/check-evidence-registry-anomaly → root
FIXTURES_DIR = THIS_DIR / "fixtures"

PYTHON_HELPER = WORKTREE_ROOT / "scripts" / "lib" / "check_evidence_registry_anomaly.py"

EXIT_PASS = 0
EXIT_VALIDATION_FAIL = 1
EXIT_META_ERROR = 2


def run_helper(registry_path: Path) -> subprocess.CompletedProcess:
    """Python helper 직접 호출 (worktree root cwd, registry path 인자).

    Windows cp949 encoding 회피: encoding 명시 (utf-8) + errors='replace'.
    """
    return subprocess.run(
        [sys.executable, str(PYTHON_HELPER), str(registry_path)],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(WORKTREE_ROOT),
    )


# ─────────────────────────────────────────────────────────────────────────────
# TC-1 (mandatory) — 현행 SSOT registry → exit 0 (PASS)
# ─────────────────────────────────────────────────────────────────────────────
def test_tc1_positive_current_state():
    """TC-1: 현행 SSOT docs/evidence-checks-registry.yaml → PASS (exit 0).

    evidence-registry-anomaly 51번째 entry 포함 후 sub-check 1 + sub-check 2 모두 0건 기대.
    ALLOWLIST assertion 은 worktree root cwd 에서 실행하므로 통과.
    """
    registry = WORKTREE_ROOT / "docs" / "evidence-checks-registry.yaml"
    assert registry.exists(), f"TC-1: SSOT registry 부재 — {registry}"

    result = run_helper(registry)
    assert result.returncode == EXIT_PASS, (
        f"TC-1 FAIL: expected exit 0 (PASS), got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "PASS" in result.stdout or "anomaly 0건" in result.stdout, (
        f"TC-1 FAIL: PASS message 부재\nstdout: {result.stdout}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TC-2 (mandatory) — negative missing entry → exit 1 (anomaly DETECTED)
# ─────────────────────────────────────────────────────────────────────────────
def test_tc2_negative_missing_entry():
    """TC-2: lane-evidence-trail 누락 fixture → anomaly DETECTED (exit 1).

    sub-check 1 에서 lane-evidence-trail 미등록 violation 검출 예상.
    fixture 가 사용되더라도 sub-check 2 는 전체 scripts/workflows 디렉토리를 스캔하므로
    추가 violations 도 가능 — exit 1 확인 + lane-evidence-trail 메시지 확인.
    """
    fixture = FIXTURES_DIR / "02-negative-registry-missing-entry.yaml"
    assert fixture.exists(), f"TC-2 fixture 부재: {fixture}"

    result = run_helper(fixture)
    assert result.returncode == EXIT_VALIDATION_FAIL, (
        f"TC-2 FAIL: expected exit 1 (anomaly), got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "lane-evidence-trail" in result.stderr, (
        f"TC-2 FAIL: lane-evidence-trail violation message 부재\nstderr: {result.stderr}"
    )
    assert "sub-check 1" in result.stderr, (
        f"TC-2 FAIL: sub-check 1 label 부재\nstderr: {result.stderr}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TC-3 (mandatory) — ALLOWLIST self-exempt 확인
# ─────────────────────────────────────────────────────────────────────────────
def test_tc3_allowlist_self_exempt():
    """TC-3: ALLOWLIST 4-path 이 sub-check 2 violation 으로 등장하지 않는 것 확인.

    check-evidence-registry-anomaly.sh + 2 workflow yml = ALLOWLIST purpose (a) exclude.
    현행 SSOT 사용 시 exit 0 (PASS) 이어야 하며,
    scripts/check-evidence-registry-anomaly.sh 가 violation 으로 등장하면 FAIL.
    """
    registry = WORKTREE_ROOT / "docs" / "evidence-checks-registry.yaml"
    assert registry.exists(), f"TC-3: SSOT registry 부재 — {registry}"

    result = run_helper(registry)

    # ALLOWLIST scripts 가 sub-check 2 violation 으로 등장하지 않아야 함
    assert "check-evidence-registry-anomaly.sh' — 4-criteria PASS" not in result.stderr, (
        f"TC-3 FAIL: ALLOWLIST self-exempt 실패 — check-evidence-registry-anomaly.sh 가 violation\n"
        f"stderr: {result.stderr}"
    )
    assert "evidence-registry-anomaly-check.yml' — 4-criteria PASS" not in result.stderr, (
        f"TC-3 FAIL: ALLOWLIST self-exempt 실패 — evidence-registry-anomaly-check.yml 가 violation\n"
        f"stderr: {result.stderr}"
    )
    # TC-3 핵심: 현행 SSOT 상태에서 exit 0 (PASS)
    assert result.returncode == EXIT_PASS, (
        f"TC-3 FAIL: expected exit 0 (PASS) with SSOT registry + ALLOWLIST, got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TC-5 (optional) — META-ERROR broken yaml → exit 2
# ─────────────────────────────────────────────────────────────────────────────
def test_tc5_meta_error_yaml_parse_fail():
    """TC-5: broken yaml fixture → META-ERROR (exit 2).

    registry yaml parse 실패 시 exit 2 + META-ERROR 메시지 출력 확인.
    """
    fixture = FIXTURES_DIR / "05a-meta-error-yaml-parse-fail.yaml"
    assert fixture.exists(), f"TC-5 fixture 부재: {fixture}"

    result = run_helper(fixture)
    assert result.returncode == EXIT_META_ERROR, (
        f"TC-5 FAIL: expected exit 2 (META-ERROR), got {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert "META-ERROR" in result.stderr, (
        f"TC-5 FAIL: META-ERROR message 부재\nstderr: {result.stderr}"
    )
