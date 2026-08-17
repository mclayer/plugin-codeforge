"""conftest.py — CFP-2687 Phase 2 dev-process observability substrate 테스트 부트스트랩.

`scripts/lib` 를 sys.path 에 주입해 테스트가 under-test 모듈을 직접 import 할 수 있게 한다:
  append_dev_process_event / redact_dev_process_content /
  dev_process_blob_store / query_dev_process_event

QADev 경계: 본 파일 + tests/** 만 작성. production 코드(scripts/lib, hooks) READ-ONLY.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest

# tests/ → repo root → scripts/ + scripts/lib
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
SCRIPTS_LIB = SCRIPTS_DIR / "lib"
for _p in (str(SCRIPTS_DIR), str(SCRIPTS_LIB)):
    if _p not in sys.path:
        sys.path.insert(0, _p)


@pytest.fixture(autouse=True, scope="function")
def isolated_scheduled_task_heartbeat_file(tmp_path):
    """autouse fixture: in-process 테스트가 실 사용자 heartbeat 파일을 오염시키지 않도록 격리.

    Rationale (scope='function'):
      각 테스트가 독립적인 tmp 디렉터리를 가지므로 테스트 간 간섭 0.
      테스트 완료 후 pytest가 자동으로 tmp 정리 (os.chdir 재귀 문제 우회).

    Behavior:
      - 기존 env 저장 (monkeypatch 대신 try/finally로 복원)
      - SCHEDULED_TASK_HEARTBEAT_FILE 을 tmp_path 내 임시 파일로 설정
      - 테스트 실행
      - 기존 env 복원
    """
    env_key = "SCHEDULED_TASK_HEARTBEAT_FILE"
    original_value = os.environ.get(env_key)

    # tmp 내 heartbeat 파일 경로 설정
    heartbeat_path = str(tmp_path / "scheduled-task-test-heartbeat.epoch")
    os.environ[env_key] = heartbeat_path

    try:
        yield
    finally:
        # 원래 env 복원 (부재했으면 제거)
        if original_value is None:
            os.environ.pop(env_key, None)
        else:
            os.environ[env_key] = original_value


@pytest.fixture(autouse=True, scope="function")
def reset_workspace_prefix_cache():
    """autouse fixture: `scheduled_task_reconcile._workspace_prefix_cache` 세션 누수 차단.

    문제 (구현리뷰 iter4 회부 관측 조치 B):
      그 캐시는 **모듈 전역**인데 이를 리셋하는 site 가 repo 전체 **0건**이었다.
      그래서 pytest 세션 안에서 **최초 해소자 승리**가 된다 — 어떤 테스트가 먼저
      `_workspace_prefixes()` 를 태우느냐에 따라 이후 전 테스트가 그 값을 물려받고,
      "실 subprocess 가 도는가" 같은 성질이 **실행 순서에 좌우**된다.

    처방: 매 테스트 전후로 `None`(미해소)으로 되돌린다. 테스트는 자기 값을 주입하든
      lazy 해소를 태우든 자유롭되, 그 결과가 형제에게 새지 않는다.

    ★ 성능 테스트 영향 = **실측 판정**(추정 금지 — 회부 지시). 대상 =
      `test_scheduled_task_stateful.py` 의 200-iteration 루프(WARMUP=20 이후 절대 순증).

      (1) 기전 — 캐시 리셋 regime vs 워밍 regime 을 같은 호출로 대조 실측:
            lazy 해소 진입(`default_scan_roots(None)`)  0회 / 0회   (동일)
            실 subprocess 형상  `git -C <repo_root> worktree list --porcelain`  (동일)
          루프가 부르는 `collect_observations(scan_roots=...)` 는
          `_observe_workspace_residue` 에서 `_set_workspace_prefixes()` 로 권위값을
          직접 주입하므로 **lazy 해소 경로를 아예 타지 않는다**. 관측된 그 1건은
          `discover()` 의 등록 worktree 조회이지 캐시 해소가 아니다(초기 판별 오류를
          `-C .` vs `-C <repo_root>` 로 분해해 정정).

      (2) 종단 — 200-iteration 3-trial (gc_net 개 / mem_net KB, 상한 100 / 512):
            fixture 부재 → gc 0 / 0 / 0     · mem 50.3 / 55.7 / 49.3
            fixture 적용 → gc 0 / 0 / 0     · mem 50.5 / 50.1 / 49.0
          gc 는 동일(spread 0), mem 은 fixture 적용 구간이 부재 구간 범위 안에 들어온다.
          두 regime 모두 상한의 1/10 수준이며 전 trial GREEN.

      ⇒ **판정: 영향 없음**. autouse 범위에서 성능 테스트를 제외할 근거 없음(제외 0).

    production 무접촉 — 캐시 속성만 되돌리며 production 측 lazy 폴백은 정당 판정이다
    (AC-13 불변식은 3단 + fail-closed 잔여 가드가 보유하고 캐시에 의존하지 않는다).
    """
    try:
        import scheduled_task_reconcile as _sut
    except Exception:            # noqa: BLE001 — 모듈 부재 환경에서 스위트를 깨지 않는다
        yield
        return

    _sut._workspace_prefix_cache = None
    try:
        yield
    finally:
        _sut._workspace_prefix_cache = None


def run_cli_check_liveness(script_path, comments_path, cursor_path, now_iso):
    """★ F-CR-001/F-CR-002 Reusable helper: invoke check_branch_liveness.py CLI.

    Args:
        script_path: Path to check_branch_liveness.py
        comments_path: Path to comments JSON file
        cursor_path: Path to cursor JSON file
        now_iso: ISO8601 timestamp string (--now argument)

    Returns:
        (rc, parsed_json) tuple where parsed_json is the --json output parsed as dict,
        or None if JSON parsing fails.
    """
    cmd = [
        sys.executable,
        str(script_path),
        "--comments", str(comments_path),
        "--cursor", str(cursor_path),
        "--now", now_iso,
        "--json"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    parsed = None
    if result.returncode == 0:
        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError:
            pass

    return result.returncode, parsed
