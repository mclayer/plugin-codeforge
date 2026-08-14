#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CI 실 run-line parity — 2-dir 수집이 collection ERROR 없이 성립하는가 (CFP-2965 G1 / CR-201).

왜 필요한가 (born-blind 축):
  CI(lint.yml hook-unit-tests) 의 실 run-line 은 **2-dir** 이다:
      pytest hooks/tests overlay/hooks/tests -q
  그런데 로컬 검증은 관행적으로 단일 dir(`pytest hooks/tests -q`)만 돌렸다. 두 dir 를
  함께 수집하면 `overlay/hooks/tests/conftest.py`(6줄·공용 심볼 0) 가 top-level 모듈명
  `conftest` 를 선점해, `hooks/tests` 의 테스트들이 하던 bare `from conftest import ...`
  가 **overlay 쪽 conftest** 로 해석된다 → ImportError → collection ERROR → Interrupted
  (그 시점 전체 미실행). 단일 dir 실행은 GREEN 이라 로컬에서 영영 안 보인다.

  즉 "로컬 GREEN" 과 "CI GREEN" 사이에 관측 사각이 있었다. 이 테스트가 그 사각을 닫는다.

RED 실측 (수정 전 HEAD bc3c8e96e, 2026-08-14 firsthand):
    $ python -m pytest hooks/tests overlay/hooks/tests --collect-only -q ; echo $?
    E   ImportError: cannot import name 'requires_bash' from 'conftest'
        (.../overlay/hooks/tests/conftest.py)
    ERROR hooks/tests/test_argv_path_form_3arm.py
    ERROR hooks/tests/test_bypass_env_disjoint.py
    ERROR hooks/tests/test_check_worktree_location_guard_block_tier.py
    ERROR hooks/tests/test_hook_failopen_matrix.py
    !!!!! Interrupted: 4 errors during collection !!!!!
    791 tests collected, 4 errors in 1.68s
    TRUE_EXIT=2
  → 본 테스트는 그 상태에서 FAIL 한다 (자연 discriminating — mutant 조작 불필요).

판정 정밀도:
  `"error" in output` 류 substring 판정은 쓰지 않는다 — `--collect-only -q` 는 test ID 를
  나열하고, 코퍼스에 `test_tc5b_main_silent_detect_error_audit` 처럼 이름에 'error' 가
  든 테스트가 실재한다(실측). 따라서 pytest 의 **구조적 마커**로만 판정한다:
    (1) exit code == 0
    (2) "errors during collection" 부재
    (3) 줄 선두 "ERROR " (short summary 행) 부재
    (4) 수집 건수 > 0 (0건 수집을 '오류 없음'으로 오독하지 않도록 — 공허 통과 차단)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# CI 실 run-line 과 동일한 2-dir (lint.yml hook-unit-tests).
CI_TEST_DIRS = ("hooks/tests", "overlay/hooks/tests")


def _collect_only() -> tuple[int, str]:
    """2-dir --collect-only 실행 → (rc, stdout+stderr). 실행 비용 실측 ≈2-4s."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *CI_TEST_DIRS,
         "--collect-only", "-q", "-p", "no:cacheprovider"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def test_ci_two_dir_collection_is_clean():
    """CI 실 run-line(2-dir) 수집에 collection ERROR 0 ∧ exit 0."""
    rc, out = _collect_only()

    assert "errors during collection" not in out, (
        "2-dir 수집에서 collection ERROR 발생 — CI 는 여기서 Interrupted 되어 "
        "전체 미실행이 된다 (로컬 단일-dir GREEN 은 이를 못 본다).\n"
        f"--- pytest 출력 tail ---\n{out[-3000:]}"
    )
    summary_errors = re.findall(r"^ERROR .*$", out, flags=re.MULTILINE)
    assert not summary_errors, (
        "pytest short summary 에 ERROR 행 존재:\n" + "\n".join(summary_errors)
    )
    assert rc == 0, f"2-dir --collect-only exit {rc} (기대 0)\n{out[-3000:]}"


def test_ci_two_dir_collection_is_non_empty():
    """정의역 비공허 — 0건 수집을 '오류 없음' 으로 오독하지 않는다."""
    _rc, out = _collect_only()

    m = re.search(r"(\d+) tests? collected", out)
    assert m, f"수집 건수 요약을 찾지 못함 (출력 형식 변경?):\n{out[-2000:]}"
    collected = int(m.group(1))
    assert collected > 0, "수집 0건 — 판정 대상 소실"

    # 두 dir 모두에서 실제로 수집됐는지 (한쪽만 수집돼도 parity 가 아니다)
    for d in CI_TEST_DIRS:
        needle = d.replace("/", "\\") if "\\" in out else d
        assert needle in out or d in out, (
            f"'{d}' 에서 수집된 항목이 출력에 없다 — 2-dir parity 미성립\n{out[:2000]}"
        )


def test_no_bare_conftest_import_in_hook_tests():
    """회귀 가드: hooks/tests 의 bare `from conftest import ...` 재유입 차단.

    top-level 모듈명 `conftest` 는 overlay 와 충돌하는 **공유 이름**이라 어느 쪽이
    선점될지 수집 구성에 좌우된다. 공용 심볼은 고유 basename 모듈
    (`hook_runner_cfp2965`) 경유로만 가져온다.
    """
    offenders = []
    for p in sorted((REPO_ROOT / "hooks" / "tests").glob("*.py")):
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            s = line.strip()
            if s.startswith("from conftest import") or s == "import conftest":
                offenders.append(f"{p.relative_to(REPO_ROOT)}:{i}: {s}")

    assert not offenders, (
        "bare conftest import 재유입 (2-dir 수집에서 overlay conftest 로 해석된다):\n"
        + "\n".join(f"  - {o}" for o in offenders)
    )
