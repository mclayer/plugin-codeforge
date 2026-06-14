"""conftest.py — bootstrap-first-gate 테스트 fixture + importlib 로더.

비표준 파일명(하이픈 포함) bootstrap-first-gate.py 를 importlib 로 로드해
bootstrap_first_gate 모듈명으로 노출하는 패턴. overlay/hooks/tests/conftest.py
패턴 답습.
"""

import sys
import importlib.util
from pathlib import Path

# sys.path 에 hooks/ 디렉터리 주입
HOOKS_DIR = Path(__file__).resolve().parent.parent
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))

# bootstrap-first-gate.py 를 bootstrap_first_gate 모듈명으로 로드
_spec = importlib.util.spec_from_file_location(
    "bootstrap_first_gate", HOOKS_DIR / "bootstrap-first-gate.py"
)
bootstrap_first_gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bootstrap_first_gate)
sys.modules["bootstrap_first_gate"] = bootstrap_first_gate
