#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hook_runner_cfp2965.py — hooks/tests 공용 테스트 인프라 (고유 basename 모듈).

왜 conftest.py 가 아니라 이 파일인가 (CFP-2965 G1 / CR-201):
  CI 실 run-line 은 2-dir 이다 — `pytest hooks/tests overlay/hooks/tests -q`.
  이때 top-level 모듈명 `conftest` 는 **두 디렉터리가 공유하는 이름**이라,
  `overlay/hooks/tests/conftest.py`(6줄·공용 심볼 0) 가 sys.modules["conftest"] 를
  선점하면 이쪽 테스트의 `from conftest import requires_bash` 가 그 빈 모듈로
  해석돼 ImportError → collection ERROR → Interrupted(전체 미실행) 이 된다.
  단일 dir 실행은 GREEN 이라 로컬에서는 안 보이는 사각이었다 (실측: 4 ERROR, exit 2).

  → 공용 심볼은 **고유 basename** 모듈에 둔다. `hook_runner_cfp2965` 는 overlay 를
    포함한 어느 수집 대상에도 동명 파일이 없어 선점 충돌이 원리적으로 불가능하다.
  → conftest.py 에는 pytest 가 자동 로드해야만 의미가 있는 것(플러그인 side effect,
    fixture)만 남긴다. 공용 상수·헬퍼는 conftest 의 자동 로드 성질을 필요로 하지 않는다.

  회귀 가드: hooks/tests 의 bare `from conftest import ...` 재유입은
    test_ci_parity_collection.py::test_no_bare_conftest_import_in_hook_tests 가 차단.

배경 (F1 승계): 일부 테스트가 훅을 `["cmd.exe", "/c", run-hook.cmd, <hook>]` 로
  하드코딩해 실행했다. Windows 에서만 성립하는 형태라 Linux CI(ubuntu-latest)에서는
  FileNotFoundError → 전건 FAIL 한다. 훅의 **판정 축**(deny / fail-open 거동)은 OS 와
  무관하므로 bash 직접 호출로 통일한다 (test_golden_corpus.py 동형).

  등가성 실측(2026-08-14, Windows): worktree-location-guard TIER={block, warn, 미설정}
  3케이스에서 cmd.exe 경유와 bash 직접 호출의 rc·stderr 가 완전 일치.

  run-hook.cmd 경유가 *본질*인 축(배치 런처의 exit code 전파 등)은 훅의 판정이 아니라
  런처 자체의 계약이므로, 그 축만 `requires_windows` 로 명시 분리한다.

중복 정직 기록: `shutil.which("bash")` 사본이 hooks/tests/ 에 이미 7개 존재한다
  (test_cross_repo_gh_safety / test_dev_process_capture_wrappers / test_dynamic_contracts_c /
   test_golden_corpus / test_pretooluse_agent_spawn_gate / test_pretooluse_bash_description_inject /
   test_repo_confinement). 본 모듈이 그 정본 자리이며, 신규 유입을 막는다.
  기존 7개의 수렴은 본 FIX 범위 밖(무관 테스트 회귀 위험) — 별건 기계적 정리 대상.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

# hooks/ (테스트 대상 훅들이 있는 디렉터리) / hooks/tests/
TESTS_DIR = Path(__file__).resolve().parent
HOOKS_DIR = TESTS_DIR.parent
REPO_ROOT = HOOKS_DIR.parent

HOOKS_DIR_FOR_RUNNER = HOOKS_DIR
RUN_HOOK_CMD = HOOKS_DIR / "run-hook.cmd"

BASH = shutil.which("bash") or (
    r"C:\Program Files\Git\bin\bash.exe"
    if os.name == "nt" and Path(r"C:\Program Files\Git\bin\bash.exe").exists()
    else None
)

requires_bash = pytest.mark.skipif(BASH is None, reason="bash interpreter 부재")
requires_windows = pytest.mark.skipif(
    os.name != "nt",
    reason="run-hook.cmd(cmd.exe) 런처 경유가 본질인 축 — Windows 전용",
)


def run_hook_bash(
    hook_name: str,
    stdin_bytes: bytes | None = None,
    env: dict | None = None,
    timeout: int = 30,
) -> tuple[int, str, str]:
    """`hooks/<hook_name>` 을 bash 로 직접 실행 → (rc, stdout, stderr).

    타임아웃·기동 실패는 rc=-1 + 사유 문자열로 환원한다 (호출부가 rc 로 단정하도록).
    """
    try:
        proc = subprocess.run(
            [BASH, str(HOOKS_DIR / hook_name)],
            input=stdin_bytes,
            capture_output=True,
            env=env,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as exc:  # 기동 실패 (bash 부재 등)
        return -1, "", f"{type(exc).__name__}: {exc}"
    return (
        proc.returncode,
        proc.stdout.decode("utf-8", errors="replace"),
        proc.stderr.decode("utf-8", errors="replace"),
    )


def load_hooks_json() -> dict:
    """hooks/hooks.json 로드 (테스트 공용 SSOT 로더).

    구조: 같은 헬퍼가 여러 테스트 파일에 사본으로 있었고, 그중 하나를 다른 파일이
    **테스트-간 import** 로 끌어 쓰고 있었다(test_hook_timeout_invariant_t3 →
    test_hook_timeout_contract). 테스트 모듈은 수집 구성에 따라 이름 해석이 흔들리는
    표면이라 인프라 심볼의 출처로 부적합하다 — 여기로 이설한다.

    부재·구조 이상은 FAIL (구 test_hook_timeout_contract._load_hooks_json 의 계약 승계
    — 조용히 빈 dict 를 돌려 하류 assert 를 공허하게 만들지 않는다).
    """
    hooks_path = HOOKS_DIR / "hooks.json"
    assert hooks_path.exists(), f"hooks.json not found at {hooks_path}"
    with open(hooks_path, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict) and "hooks" in data, "Invalid hooks.json structure"
    return data


# ── 게이트 ↔ bypass env 매핑 (테스트 공용 정의역) ─────────────────────────────
#   PreToolUse deny 게이트 4종의 1:1 bypass env. bypass disjoint 축(INV-B1)과
#   timeout rationale 표의 AC-16 #1 정의역이 **같은 4종**을 가리켜야 하므로,
#   두 테스트가 서로를 import 하지 않고 여기를 공통 출처로 삼는다.
BYPASS_ENVS = {
    "cross-repo-gh-safety": "BYPASS_CROSS_REPO_GH_SAFETY",
    "repo-confinement": "BYPASS_REPO_CONFINEMENT",
    "git-branch-delete-merge-gate": "BYPASS_BRANCH_DELETE_MERGE_GATE",
    "worktree-location-guard": "BYPASS_WORKTREE_LOCATION_GUARD",
}


def parametrize_argvalues(func, argnames: str) -> list:
    """테스트 함수에 **실제로 붙은** @pytest.mark.parametrize 의 argvalues 를 꺼낸다.

    커버리지·completeness assert 가 기대값을 원본 상수에서 재유도하면 자기 자신을
    비교하는 항진명제가 된다 — parametrize 목록에서 항목을 빼도 늘 통과한다.
    실 파라미터를 데코레이터에서 직접 읽어야 정의역 축소가 검출된다.
    """
    marks = [m for m in getattr(func, "pytestmark", []) if m.name == "parametrize"]
    for m in marks:
        if m.args and m.args[0] == argnames:
            return list(m.args[1])
    raise AssertionError(
        f"{func.__name__} 에 parametrize({argnames!r}) 가 없다 — "
        f"현재 마크 argnames: {[m.args[0] for m in marks if m.args]}"
    )


def assert_module_origin(module) -> None:
    """테스트-간 import 출처 보증 — 해당 모듈이 hooks/tests 하위에서 왔는가.

    불가피한 테스트-간 import(census 결과 상수 등)에 동반한다. 동명 파일이 다른
    수집 대상에서 선점되면 여기서 fail-closed 로 끊긴다 (조용한 오출처 차단).
    """
    origin = getattr(module, "__file__", None)
    assert origin, f"{getattr(module, '__name__', module)} 의 __file__ 부재 — 출처 불명"
    resolved = Path(origin).resolve()
    assert resolved.parent == TESTS_DIR, (
        f"{module.__name__} 이 hooks/tests 밖에서 로드됐다 (모듈명 선점 의심): {resolved}"
    )
