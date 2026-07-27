#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""conftest.py — CFP-2829 S2 Phase 2 backward-sync 테스트 부트스트랩.

`scripts/` 와 `scripts/lib/` 를 sys.path 에 주입해 테스트가 under-test 모듈을 직접 import 할 수 있게 한다:
  - confluence_property_chunking / confluence_backward_sync / confluence_backward_gate
  - confluence_property_rest / sync_sentinel

QADev 경계: 본 파일 + tests/scripts/** 만 작성. production 코드(scripts/*, scripts/lib/*) READ-ONLY.
"""

import sys
from pathlib import Path

# tests/scripts/ → repo root → scripts/ + scripts/lib/
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
SCRIPTS_LIB = SCRIPTS_DIR / "lib"
for _p in (str(SCRIPTS_DIR), str(SCRIPTS_LIB)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
