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

import re
import pytest
from pathlib import Path

import check_stale_local_main_checkout as cslmc

# 정본 로더 = 고유 basename 인프라 모듈 (구 `from test_hook_timeout_contract import
# _load_hooks_json` 테스트-간 import 대체 — CR-201 이름 해석 흔들림 표면 제거).
from hook_runner_cfp2965 import load_hooks_json as _load_hooks_json

BRANCH_GATE_HOOK = "git-branch-delete-merge-gate"
STALE_FETCH_ENV = "CODEFORGE_STALE_FETCH_TIMEOUT_SEC"


def _leaf_timeout(hook_name: str) -> int:
    """hooks.json 에서 `<hook_name>` leaf handler 의 timeout 실파싱.

    구 코드는 `HOOK_TIMEOUT = 60` 을 테스트에 하드코딩했다 — hooks.json 의 timeout 이
    바뀌어도 불변식이 옛 값으로 계속 "검증"되는 결속 없는 상수였다. 실물 파싱으로 묶어
    hooks.json 이 움직이면 INV-T3 가 그 값으로 재판정되게 한다.
    """
    data = _load_hooks_json()
    found = [
        handler
        for entries in data["hooks"].values()
        for entry in entries
        for handler in entry.get("hooks", [])
        if hook_name in handler.get("command", "")
    ]
    assert len(found) == 1, (
        f"hooks.json 에 {hook_name} leaf handler 가 정확히 1개여야 함 (실측 {len(found)})"
    )
    timeout = found[0].get("timeout")
    assert isinstance(timeout, int) and timeout > 0, (
        f"{hook_name} timeout 이 양의 int 가 아님: {timeout!r}"
    )
    return timeout


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
    MARGIN = 10  # fail-open margin (Change Plan §3.2 — 설계 상수)
    HOOK_TIMEOUT = _leaf_timeout(BRANCH_GATE_HOOK)  # hooks.json 실파싱 (하드코딩 금지)

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


@pytest.mark.parametrize(
    "env_value,expected",
    [
        (None, 10),   # 미설정   → default 10
        ("7", 7),     # 상한 이하 → 그대로 (하향 전용이라 손대지 않음)
        ("26", 10),   # 상한 초과 → 10 으로 하향 clamp
        ("0", 10),    # 하한 미만 → default 10 (0 초 fetch 금지)
        ("abc", 10),  # 파싱 불가 → default 10 (fail-safe)
    ],
)
def test_stale_fetch_env_clamp_constants(monkeypatch, env_value, expected):
    """S3: STALE_FETCH env clamp 를 **실호출**로 검증 (표 5케이스).

    구 코드는 (a) 존재하지 않는 경로(`hooks/../check-stale-local-main-checkout.py`)를 보고
    (b) 파일이 없으면 skip 했으며 (c) 있더라도 `"clamp" in content or "min(" in content`
    라는 문자열 검사였다 — 주석에 `min(` 한 조각만 있어도 통과하는 준항진이었다.
    실물은 `scripts/lib/check_stale_local_main_checkout.py` 이며, 여기서는 clamp 함수를
    직접 호출해 입력→출력 표를 고정한다.

    함수명은 RTM 수집 키라 유지하고 몸통만 교체했다.
    """
    if env_value is None:
        monkeypatch.delenv(STALE_FETCH_ENV, raising=False)
    else:
        monkeypatch.setenv(STALE_FETCH_ENV, env_value)

    actual = cslmc._get_fetch_timeout()
    assert actual == expected, (
        f"{STALE_FETCH_ENV}={env_value!r} → {actual} (기대 {expected})"
    )


def test_stale_fetch_clamp_is_downward_only(monkeypatch):
    """clamp 는 **하향 전용** — 어떤 env 값으로도 상한을 넘길 수 없다.

    표 5케이스는 고른 점만 고정하므로, 상한 돌파 가능성 자체를 별도로 막는다
    (SessionStart 훅 timeout 하한 불변식을 env 로 위반 못 하게 하는 것이 이 clamp 의 목적).
    """
    cap = cslmc.FETCH_TIMEOUT_CLAMP_SEC
    for raw in ("1", "9", "10", "11", "60", "3600", "999999", "-5", "", " 7 "):
        monkeypatch.setenv(STALE_FETCH_ENV, raw)
        got = cslmc._get_fetch_timeout()
        assert 1 <= got <= cap, f"{STALE_FETCH_ENV}={raw!r} → {got} (허용 1..{cap} 이탈)"
