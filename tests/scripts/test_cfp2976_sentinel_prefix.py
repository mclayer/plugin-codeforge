"""CFP-2976 — parallel-work sentinel 판별력 복원 검사 (AC-1~AC-6).

★왜 Python 인가 (bash harness 와의 분업):
  `tests/scripts/test_check-parallel-work-sentinel.sh`(661줄, CFP-2451/2490/2723)는
  **CLI 계층**을 gh mock seam 으로 검증한다 — 그 축은 그대로 둔다.
  본 모듈은 **Python SSOT 내부 함수**(`resolve_prefix` / `_prefix_from_overlay` / `_exit_pass`)를
  직접 검증한다. 두 벌 중복이 아니라 계층 분업이며, CFP-2976 3속성의 SSOT 는 **본 모듈**이다
  (bash 쪽에 같은 케이스를 두지 않는다 — "같은 규칙 두 벌 = 한쪽만 고쳐진다" 회피).

★kill-mutant (§8.4.1):
  - `resolve_prefix` 를 `os.environ.get("STORY_KEY_PREFIX", "CFP")` 로 되돌리면
      test_2976_a_derive_from_overlay / test_2976_b_fail_closed 가 FAIL
  - `_exit_pass` 의 `payload.setdefault("determined", True)` 를 제거하면
      test_2976_c_determined_contract 가 FAIL
"""

import importlib
import io
import json
import os
import subprocess
import sys

import pytest

_LIB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "scripts",
    "lib",
)
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)


def _fresh_module():
    """모듈 재로드 — `_PREFIX_CACHE` 전역 캐시가 케이스 간 누수되지 않도록."""
    import check_parallel_work_sentinel as m

    importlib.reload(m)
    return m


def _git_repo(path):
    """최소 git repo — `_repo_root()` 가 toplevel 을 찾을 수 있어야 overlay 해석이 성립."""
    subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("STORY_KEY_PREFIX", raising=False)


def test_2976_a_derive_from_overlay(tmp_path, monkeypatch):
    """AC-1·AC-2·AC-4·AC-6 — env 미주입 시 project.yaml 에서 prefix 를 유도한다.

    ★실사고: 구 코드는 env 미주입 시 조용히 "CFP" 로 떨어져, prefix 가 다른 consumer 에서
      정의상 공집합(`{"matches": []}`)을 반환했고 그 빈 결과가 착수 통행증으로 소비됐다.
    """
    repo = tmp_path / "consumer"
    (repo / ".claude" / "_overlay").mkdir(parents=True)
    _git_repo(repo)
    (repo / ".claude" / "_overlay" / "project.yaml").write_text(
        'github:\n  story_key_prefix: "ZZT"\n', encoding="utf-8"
    )
    monkeypatch.chdir(repo)

    m = _fresh_module()
    assert m.resolve_prefix() == "ZZT", "overlay 유도 실패 — 조용한 CFP fallback 회귀 의심"
    assert m.key_pattern().search("[ZZT-123] impl") is not None
    assert m.key_pattern().search("[CFP-1] impl") is None, "prefix 미스매치가 매칭됐다"


def test_2976_b_fail_closed(tmp_path, monkeypatch):
    """AC-1·AC-5 — env·overlay 모두 부재 시 fail-closed(exit 2)로 차단한다.

    조용한 기본값은 "안 찾음"과 "없음"을 구분 불가하게 만들어 오판을 생산한다.
    """
    repo = tmp_path / "bare"
    repo.mkdir()
    _git_repo(repo)
    monkeypatch.chdir(repo)

    m = _fresh_module()
    with pytest.raises(SystemExit) as exc:
        m.resolve_prefix()
    assert exc.value.code == 2, "fail-closed 가 아니다 — 조용한 기본값 회귀 의심"


def test_2976_c_determined_contract(monkeypatch):
    """AC-3·AC-5 — 성공 payload 에 `determined: true` 가 명시된다.

    `matches: []` 단독으로는 "부재"를 주장할 수 없다. 호출자가 판정 불가를 부재로 읽는 경로를
    구조적으로 차단하는 유일한 수단이 이 필드다.
    """
    monkeypatch.setenv("STORY_KEY_PREFIX", "CFP")  # prefix 축과 무관하게 고정
    m = _fresh_module()

    buf = io.StringIO()
    real = sys.stdout
    sys.stdout = buf
    try:
        with pytest.raises(SystemExit) as exc:
            m._exit_pass({"matches": []})
    finally:
        sys.stdout = real

    assert exc.value.code == 0
    payload = json.loads(buf.getvalue().strip())
    assert payload.get("determined") is True, "determined 계약 부재 — setdefault 제거 회귀 의심"
    assert payload.get("matches") == []
