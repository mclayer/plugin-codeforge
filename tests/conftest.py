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
