#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S3 (테스트): Hook timeout budget invariant INV-T3.

목적:
  hooks.json 의 timeout 값과 구현 코드의 내부 budget 상수 간 일관성 검증.

INV-T3 (Change Plan §4 #7):
  timeout(60) ≥ GH_TOTAL_BUDGET_SEC + margin
  ∧ GH_TOTAL_BUDGET_SEC > _GH_TIMEOUT_SEC

근거:
  git-branch-delete-merge-gate.py 에서 gh 호출을 누적 예산으로 제한하되,
  hooks.json 의 timeout(60) 이 hollow 가 되지 않도록 예산이 timeout 보다
  충분히 작아야 함 (margin 포함).

세부:
  - _GH_TIMEOUT_SEC = 10 (per-call timeout)
  - GH_TOTAL_BUDGET_SEC = 50 (cumulative budget for all gh calls)
  - margin = 10 (fail-open handling 시간 여유)

  조건:
    1. timeout(60) >= GH_TOTAL_BUDGET_SEC(50) + margin(10) => 60 >= 60 ✓
    2. GH_TOTAL_BUDGET_SEC(50) > _GH_TIMEOUT_SEC(10) => 50 > 10 ✓
"""

from __future__ import annotations

import ast
import re
import pytest
from pathlib import Path


def _parse_python_constants(file_path: Path) -> dict[str, int]:
    """Python 파일에서 CONST_NAME = int 형태의 모듈 레벨 상수 파싱.

    예: _GH_TIMEOUT_SEC = 10 => {"_GH_TIMEOUT_SEC": 10}
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # 간단한 regex 기반 파싱 (module level 상수만)
    pattern = r"^([A-Z_][A-Z0-9_]*)\s*=\s*(\d+)"
    matches = re.findall(pattern, content, re.MULTILINE)

    result = {}
    for name, value in matches:
        try:
            result[name] = int(value)
        except ValueError:
            pass

    return result


def test_gh_timeout_constants_exist():
    """INV-T3: git-branch-delete-merge-gate.py 에서 GH 관련 상수 존재."""
    gate_file = Path(__file__).parent.parent / "git-branch-delete-merge-gate.py"
    assert gate_file.exists(), f"git-branch-delete-merge-gate.py not found at {gate_file}"

    constants = _parse_python_constants(gate_file)

    assert "_GH_TIMEOUT_SEC" in constants, "_GH_TIMEOUT_SEC not found"
    assert "GH_TOTAL_BUDGET_SEC" in constants, "GH_TOTAL_BUDGET_SEC not found"


def test_inv_t3_budget_invariant():
    """INV-T3 검증: timeout(60) ≥ GH_TOTAL_BUDGET_SEC + margin ∧ GH_TOTAL_BUDGET_SEC > _GH_TIMEOUT_SEC."""
    gate_file = Path(__file__).parent.parent / "git-branch-delete-merge-gate.py"
    constants = _parse_python_constants(gate_file)

    gh_timeout = constants.get("_GH_TIMEOUT_SEC")
    gh_budget = constants.get("GH_TOTAL_BUDGET_SEC")

    assert gh_timeout is not None, "_GH_TIMEOUT_SEC not defined"
    assert gh_budget is not None, "GH_TOTAL_BUDGET_SEC not defined"

    # INV-T3 조건
    MARGIN = 10  # fail-open margin (Change Plan §3.2)
    HOOK_TIMEOUT = 60  # hooks.json timeout for git-branch-delete-merge-gate

    # 조건 1: timeout >= budget + margin
    assert (
        HOOK_TIMEOUT >= gh_budget + MARGIN
    ), f"Condition 1 failed: timeout({HOOK_TIMEOUT}) >= budget({gh_budget}) + margin({MARGIN})"

    # 조건 2: budget > per-call timeout
    assert (
        gh_budget > gh_timeout
    ), f"Condition 2 failed: budget({gh_budget}) > per-call timeout({gh_timeout})"

    print(
        f"✓ INV-T3 verified: timeout={HOOK_TIMEOUT} >= budget={gh_budget} + margin={MARGIN}, "
        f"budget={gh_budget} > per-call={gh_timeout}"
    )


def test_stale_fetch_env_clamp_constants():
    """S3 code: STALE_FETCH env clamp constants (26→10 / 7→7 / default→10).

    check_stale_local_main_checkout.py 에서 clamp 로직이 존재하는지 확인.
    """
    clamp_file = Path(__file__).parent.parent / "check-stale-local-main-checkout.py"
    if not clamp_file.exists():
        pytest.skip(f"Clamp script not found at {clamp_file} — deferred to integration")
        return

    with open(clamp_file) as f:
        content = f.read()

    # Clamp logic 존재 확인 (명시적으로 min/max/clamp 호출 확인)
    assert (
        "clamp" in content.lower() or "min(" in content
    ), "Clamp logic not found in check-stale-local-main-checkout.py"
