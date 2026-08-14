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


class TestHeartbeatFileIsolation:
    """판별 테스트: autouse fixture 의 역할을 검증.

    fixture 제거 시 RED 로 변경되어야 하는 테스트 — fixture 의 진정성(실제로 격리하는가)을 입증.
    """

    def test_heartbeat_isolation_env_set_outside_gc_state(self):
        """(ㄱ) 테스트 실행 중 env 설정 + 실 GC state 디렉터리 밖을 가리킴.

        Assert:
          - SCHEDULED_TASK_HEARTBEAT_FILE 이 설정되어 있음
          - 그 값이 ~/.claude/worktree-gc-state 를 포함하지 않음
          - 그 값이 tmp 경로 또는 비어있지 않음
        """
        env_key = "SCHEDULED_TASK_HEARTBEAT_FILE"
        env_value = os.environ.get(env_key)

        # Assert (ㄱ): env 설정됨 + 실 GC state 경로 밖
        assert env_value is not None, f"{env_key} 가 설정되어야 함"
        assert env_value.strip(), f"{env_key} 이 비워있지 않아야 함"
        gc_state_dir = os.path.expanduser("~/.claude/worktree-gc-state")
        assert gc_state_dir not in env_value, (
            f"{env_key} 이 실 GC state 디렉터리({gc_state_dir}) 를 포함하면 안 됨, "
            f"실제: {env_value}"
        )

    def test_heartbeat_isolation_run_does_not_create_real_file(self, tmp_path):
        """(ㄴ) sut.run() 실행 후 실 경로 불변 ∧ 주입 경로에만 기록됨.

        Arrangement:
          - 실 heartbeat 파일의 초기 mtime 저장
          - sut.run() 호출 전 env 값 저장

        Act:
          - sut.run(["--repo-root", tmpdir, "--channel", "test/repo#1"]) 호출

        Assert:
          - 실 경로 파일이 **존재하지 않음** (또는 초기 mtime 유지)
          - 주입 경로(env 값)에 파일이 **실제로 기록됨** (size > 0)
        """
        env_key = "SCHEDULED_TASK_HEARTBEAT_FILE"
        env_value = os.environ.get(env_key)

        # 실 heartbeat 파일 경로
        real_gc_state = os.path.expanduser("~/.claude/worktree-gc-state")
        real_heartbeat_file = os.path.join(real_gc_state, "scheduled-task-last-run.epoch")

        # 실 경로의 초기 상태 저장 (부재 또는 mtime)
        real_file_existed_before = os.path.exists(real_heartbeat_file)
        real_mtime_before = os.path.getmtime(real_heartbeat_file) if real_file_existed_before else None

        # Act: sut.run() 호출 (주입 경로에 heartbeat 기록하도록)
        # scheduled_task_reconcile 모듈은 conftest 상단에서 sys.path 주입됨
        import scheduled_task_reconcile as sut

        # run() 호출 — heartbeat 기록 강제 (repo 여러 번 스캔)
        result = sut.run(["--repo-root", str(tmp_path), "--channel", "test/repo#1"])
        assert result == 0, "run() 항상 0 반환"

        # Assert: 실 경로 무변화
        real_file_exists_after = os.path.exists(real_heartbeat_file)
        real_mtime_after = os.path.getmtime(real_heartbeat_file) if real_file_exists_after else None

        if real_file_existed_before:
            assert real_mtime_after == real_mtime_before, (
                f"실 heartbeat 파일({real_heartbeat_file})이 변경되었음: "
                f"mtime_before={real_mtime_before}, mtime_after={real_mtime_after}"
            )
        else:
            assert not real_file_exists_after, (
                f"실 heartbeat 파일이 생성되었음 (fixture 격리 실패): {real_heartbeat_file}"
            )

        # Assert: 주입 경로에 파일이 실제로 기록됨 (discriminating marker)
        assert env_value is not None, f"{env_key} 이 설정되어야 함"
        assert os.path.exists(env_value), (
            f"주입 경로({env_value})에 파일이 기록되어야 함. "
            f"fixture env 설정이 무시되었거나 sut.run() 이 heartbeat를 호출하지 않음"
        )
        assert os.path.getsize(env_value) > 0, (
            f"주입 경로({env_value})에 파일이 비어있음. "
            f"sentinel 값(distinct marker)이 부재해 exit-code 단독 판정 함정 방지 안 됨"
        )


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
