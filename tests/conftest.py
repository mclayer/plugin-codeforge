"""conftest.py — CFP-2687 Phase 2 dev-process observability substrate 테스트 부트스트랩.

`scripts/lib` 를 sys.path 에 주입해 테스트가 under-test 모듈을 직접 import 할 수 있게 한다:
  append_dev_process_event / redact_dev_process_content /
  dev_process_blob_store / query_dev_process_event

QADev 경계: 본 파일 + tests/** 만 작성. production 코드(scripts/lib, hooks) READ-ONLY.
"""

import sys
from pathlib import Path

# tests/ → repo root → scripts/lib
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_LIB = REPO_ROOT / "scripts" / "lib"
if str(SCRIPTS_LIB) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_LIB))
