"""conftest.py — CFP-2687 Phase 2 dev-process observability substrate 테스트 부트스트랩.

`scripts/lib` 를 sys.path 에 주입해 테스트가 under-test 모듈을 직접 import 할 수 있게 한다:
  append_dev_process_event / redact_dev_process_content /
  dev_process_blob_store / query_dev_process_event

QADev 경계: 본 파일 + tests/** 만 작성. production 코드(scripts/lib, hooks) READ-ONLY.
"""

import json
import subprocess
import sys
from pathlib import Path

# tests/ → repo root → scripts/lib
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_LIB = REPO_ROOT / "scripts" / "lib"
if str(SCRIPTS_LIB) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_LIB))


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
