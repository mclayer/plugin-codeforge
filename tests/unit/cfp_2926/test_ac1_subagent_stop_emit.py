#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""test_ac1_subagent_stop_emit.py — CFP-2926 AC-1 L1 / NG-16 자동 emit RTM 테스트.

RTM (Story §8.0.2): `AC-1 | L1 자동 emit | test_spawn_event_auto_emit_on_subagent_stop
| T1 | 자동 경로 비활성 → row diff 0`

Story §8.0.8 (1) NG-16 규격:
  - empty-target : ★세션 내 subagent 종료 **0건** → `INCONCLUSIVE`★
                   (row diff 0 을 "자동 emit 정상"으로 읽지 않음 —
                    ★mutant M-E 의 기대값이 정확히 `diff 0` 이라 **양성/공백 구분 필수**★)
  - unknown-input: 등록면 파싱 불가 → fail-closed (기본값 대체 금지)
  - trace        : 기대 종료 이벤트 수 · emit 된 row 수
  - identity_bearing: **true** — 채널 = `hooks.json` SubagentStop **등록면**.
                   ★NG-12 와 동형 단일 실패점★ — 등록 블록 누락 = 전건 침묵

★본 테스트의 핵심 명제★
  관측치 "이번 세션에 새 row 0" **하나만으로는** 다음 두 상태를 구별할 수 없다:
    (A) 자동 경로 **사망** — subagent 는 종료했는데 emit 이 0     → 반드시 RED
    (B) 세션 **공백**      — 종료 자체가 0건이라 emit 도 0        → INCONCLUSIVE
  ⇒ 구별의 근거 2축 = ★등록면(hook) 독립 축★ + ★기대 종료 이벤트 수(`--expected-stops`)★.
     `TestNG16PositiveVsBlank` 가 같은 `diff 0` 관측에서 두 verdict 가 **갈리는지**
     축마다 실물로 falsify 한다.

★★born-broken 정정 대조 (DeveloperPL firsthand 검출 → 본 워커 수정)★★
  종전 모듈은 등록면을 `<repo_root>/hooks.json` 에서 찾고 `data["hooks"]` 를 list 로
  가정해, ★정상 등록(`hooks/hooks.json:183`)을 원리적으로 못 봤다★ ⇒ 어떤 입력에도
  `hook_registered: false` → ★항상 RED = 판별력 0★. 본 파일의
  `test_real_repo_registration_channel_reaches_actual_surface` 가 그 회귀를 직접
  겨눈다(수정 전이면 반드시 실패한다).
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from unittest.mock import patch

import pytest

# sys.path 는 상위 conftest 에서 이미 scripts/lib 를 주입했으므로 직접 import 가능
from check_subagent_stop_auto_emit import GATE_ID, main
from gate_verdict import EXIT_INCONCLUSIVE, EXIT_PASS, EXIT_RED

_HOOK_CMD = {"type": "command", "command": "run-hook.cmd subagent-stop", "async": False}

# 실제 Claude Code 등록 구조 — `hooks` 값이 dict (event 이름 → 등록 배열)
_REAL_SHAPE = {"hooks": {"SessionStart": [], "SubagentStop": [{"hooks": [_HOOK_CMD]}]}}
_REAL_SHAPE_NO_STOP = {"hooks": {"SessionStart": [], "Stop": [{"hooks": [_HOOK_CMD]}]}}


# ---------------------------------------------------------------------------
# fixture helper — 합성 세션 repo (작업 트리 무오염)
# ---------------------------------------------------------------------------

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_registration(root: Path, payload, rel: str = "hooks/hooks.json") -> None:
    _write(root / rel, json.dumps(payload, ensure_ascii=False, indent=2))


def build_session_repo(root: Path, hook_active: bool = True) -> Path:
    """SubagentStop 등록면(실제 구조) + 빈 stop-event 원장을 갖는 세션 repo."""
    write_registration(root, _REAL_SHAPE if hook_active else _REAL_SHAPE_NO_STOP)
    _write(root / ".claude" / "ledger" / "stop-event.jsonl", "")
    return root


def ledger_rows(root: Path) -> int:
    path = root / ".claude" / "ledger" / "stop-event.jsonl"
    if not path.is_file():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def simulate_session(root: Path, expected_stops: int, hook_active: bool) -> int:
    """subagent 를 `expected_stops` 개 종료시킨다. 반환 = ★실제 row diff★.

    ★자동 경로(hook)가 비활성이면 원장은 한 줄도 늘지 않는다★ — 이것이 RTM 이
    지정한 mutant("자동 경로 비활성 → row diff **0**") 의 문자 그대로의 재현이다.
    """
    before = ledger_rows(root)
    if hook_active:
        path = root / ".claude" / "ledger" / "stop-event.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8", newline="\n") as f:
            for i in range(expected_stops):
                f.write(json.dumps(
                    {"event": "subagent_stop", "agent_type": "W%d" % i,
                     "stop_time_source": "hook_stamped"},
                    ensure_ascii=False) + "\n")
    return ledger_rows(root) - before


def run_gate(root: Path, expected_stops: int | None = None):
    argv = ["check_subagent_stop_auto_emit.py", "--repo-root", str(root)]
    if expected_stops is not None:
        argv += ["--expected-stops", str(expected_stops)]
    stdout = io.StringIO()
    with patch("sys.stdout", stdout):
        exit_code = main(argv)
    payload = json.loads(stdout.getvalue().strip().splitlines()[-1])
    assert payload["gate_id"] == GATE_ID
    return exit_code, payload


@pytest.fixture
def session_repo(tmp_path):
    return build_session_repo(tmp_path / "session")


# ===========================================================================
# ★RTM 명명 테스트★ — Story §8.0.2 문자열과 정확히 일치해야 한다
# ===========================================================================

def test_spawn_event_auto_emit_on_subagent_stop(session_repo):
    """AC-1 L1 / NG-16 — 자동 emit 왕복 + RTM mutant(자동 경로 비활성 → row diff 0).

    ★규격 대조★ (§8.0.8 NG-16): "세션 내 subagent 종료 **0건** → INCONCLUSIVE".
    본 mutant 는 종료 **2건** 인데 emit 이 0 인 경우이므로 empty-target 조건에
    해당하지 **않는다** ⇒ ★INCONCLUSIVE 가 아니라 RED★ 여야 한다.
    같은 관측치(`diff 0`)가 verdict 를 가르는지가 이 테스트의 load-bearing 속성이다.
    """
    # --- GREEN: 자동 경로 살아있음 — 종료 2건 → row 2건 -----------------------
    diff_live = simulate_session(session_repo, expected_stops=2, hook_active=True)
    assert diff_live == 2, "자동 경로가 살아있으면 종료 수만큼 append 돼야 한다"

    exit_green, payload_green = run_gate(session_repo, expected_stops=2)
    assert exit_green == EXIT_PASS, payload_green
    assert payload_green["verdict"] == "PASS"
    assert payload_green["trace"]["hook_registered"] is True
    assert payload_green["trace"]["ledger_row_count"] == 2
    assert payload_green["trace"]["expected_stop_count"] == 2

    # --- ★RTM mutant★: 자동 경로 비활성 → row diff 0 (기대 종료 2건) ---------
    write_registration(session_repo, _REAL_SHAPE_NO_STOP)
    expected_stops = 2
    diff_dead = simulate_session(session_repo, expected_stops, hook_active=False)
    assert diff_dead == 0, "mutant 전제 — 자동 경로 사망 시 row 는 늘지 않는다"

    exit_red, payload_red = run_gate(session_repo, expected_stops=expected_stops)
    assert exit_red == EXIT_RED, payload_red
    assert payload_red["reason"] == "subagent_stop_hook_not_registered", payload_red
    # ★핵심★ diff 0 이지만 기대 종료 2건 — 공백(INCONCLUSIVE) 으로 흡수되면 안 된다
    assert expected_stops > 0
    assert exit_red != EXIT_INCONCLUSIVE, "자동 경로 사망을 '공백 세션'으로 읽으면 안 된다"
    assert exit_red != EXIT_PASS

    # --- revert 왕복 (negative control — "항상 RED" 와 구별) -----------------
    write_registration(session_repo, _REAL_SHAPE)
    exit_back, payload_back = run_gate(session_repo, expected_stops=2)
    assert exit_back == EXIT_PASS, payload_back
    assert payload_back["trace"]["hook_registered"] is True


# ===========================================================================
# ★양성 / 공백 구분★ — 같은 `diff 0` 이 두 verdict 로 갈리는가
# ===========================================================================

class TestNG16PositiveVsBlank:
    """`row diff 0` 관측 하나로는 못 가르는 두 상태를 실제로 가르는지 falsify."""

    def test_same_zero_diff_yields_two_different_verdicts(self, tmp_path):
        """(A) 자동 경로 사망 → RED / (B) 세션 공백 → INCONCLUSIVE — 등록면 축.

        ★두 시나리오의 관측치는 완전히 동일하다 (`row diff == 0`)★.
        두 verdict 가 같아지면 게이트는 "0 == 0" 을 무비판 수용하는 것이다.
        """
        dead = build_session_repo(tmp_path / "dead", hook_active=False)
        expected_a = 2
        diff_a = simulate_session(dead, expected_a, hook_active=False)
        exit_a, payload_a = run_gate(dead)

        blank = build_session_repo(tmp_path / "blank", hook_active=True)
        expected_b = 0
        diff_b = simulate_session(blank, expected_b, hook_active=True)
        exit_b, payload_b = run_gate(blank)

        assert diff_a == diff_b == 0, "전제: 두 관측치가 동일해야 대조가 성립한다"
        assert (expected_a, expected_b) == (2, 0), "구별 근거 = 기대 종료 수"

        assert exit_a == EXIT_RED, payload_a
        assert exit_b == EXIT_INCONCLUSIVE, payload_b
        assert exit_a != exit_b, "★같은 diff 0 이 같은 verdict 로 붕괴하면 안 된다★"
        assert payload_a["reason"] != payload_b["reason"]
        assert EXIT_PASS not in (exit_a, exit_b), "diff 0 은 어느 쪽도 GREEN 이 아니다"

    def test_expected_stop_count_separates_dead_from_blank(self, tmp_path):
        """★기계면 구분★ — 등록면이 **살아있는데도** emit 0 인 형상을 가른다.

        등록면 축만으로는 "등록은 됐는데 발화만 죽은" 경우를 못 가른다(정직 천장).
        `--expected-stops` 를 주면 같은 `row 0` 관측이:
          - 기대 3건 → RED `stop_event_emit_missing`
          - 기대 0건 → INCONCLUSIVE `no_subagent_stops_expected`
        로 갈려야 한다. 두 실행의 유일한 차이는 **기대치 인자 하나** 다(축 귀속).
        """
        repo = build_session_repo(tmp_path / "silent", hook_active=True)
        assert ledger_rows(repo) == 0

        exit_dead, payload_dead = run_gate(repo, expected_stops=3)
        exit_blank, payload_blank = run_gate(repo, expected_stops=0)

        assert exit_dead == EXIT_RED, payload_dead
        assert payload_dead["reason"] == "stop_event_emit_missing", payload_dead
        assert payload_dead["trace"]["expected_stop_count"] == 3

        assert exit_blank == EXIT_INCONCLUSIVE, payload_blank
        assert payload_blank["reason"] == "no_subagent_stops_expected", payload_blank
        assert exit_dead != exit_blank, "★기대치가 유일 차이인데 verdict 가 같으면 안 된다★"

    def test_blank_session_is_inconclusive_not_pass(self, session_repo):
        """[154-AC-3] 종료 0건 → INCONCLUSIVE (0 == 0 을 GREEN 으로 읽지 않음)."""
        assert simulate_session(session_repo, 0, hook_active=True) == 0
        exit_code, payload = run_gate(session_repo)
        assert exit_code == EXIT_INCONCLUSIVE, payload
        assert payload["verdict"] == "INCONCLUSIVE"
        assert payload["reason"] == "stop_event_ledger_empty", payload
        assert exit_code != EXIT_PASS

    def test_ledger_absent_is_inconclusive_not_pass(self, session_repo):
        """원장 파일 자체 부재도 공백 취급 — non-GREEN."""
        (session_repo / ".claude" / "ledger" / "stop-event.jsonl").unlink()
        exit_code, payload = run_gate(session_repo)
        assert exit_code == EXIT_INCONCLUSIVE, payload
        assert payload["reason"] == "stop_event_ledger_absent", payload
        assert payload["trace"]["ledger_exists"] is False


# ===========================================================================
# 등록면 축 — identity_bearing 채널 (NG-12 동형 단일 실패점)
# ===========================================================================

class TestNG16RegistrationChannel:
    """등록면이 죽으면 원장이 아무리 두툼해도 RED 여야 한다."""

    def test_registration_probe_is_discriminating(self, session_repo):
        """원장 row 를 고정한 채 **등록면만** 뒤집어 verdict 가 바뀌는지 확인.

        원장 축을 상수로 묶었으므로 verdict 변화의 원인은 등록면 축 하나뿐이다
        (교란 변수 제거 — 등록면이 load-bearing 임을 축 귀속으로 증명).
        """
        simulate_session(session_repo, 3, hook_active=True)
        rows_before = ledger_rows(session_repo)

        exit_on, _ = run_gate(session_repo)
        write_registration(session_repo, _REAL_SHAPE_NO_STOP)
        exit_off, payload_off = run_gate(session_repo)

        assert ledger_rows(session_repo) == rows_before == 3, "원장 축은 불변이어야 한다"
        assert exit_on == EXIT_PASS
        assert exit_off == EXIT_RED, payload_off
        assert payload_off["trace"]["ledger_row_count"] == 3, \
            "row 가 있어도 등록면이 죽으면 RED — 원장 수치로 덮이면 안 된다"

    def test_registration_file_deleted_is_red(self, session_repo):
        """등록면 파일 자체 부재 → RED (미등록과 **별 reason**)."""
        (session_repo / "hooks" / "hooks.json").unlink()
        exit_code, payload = run_gate(session_repo)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"] == "hooks_registration_file_not_found", payload
        assert payload["reason"] != "subagent_stop_hook_not_registered"
        assert payload["identity_probe"]["resolved_registration_file"] is None

    def test_unparseable_registration_is_fail_closed_red(self, session_repo):
        """[154-AC-4] 등록면 JSON 파손 → RED `hooks_registration_unparseable`.

        ★파싱 실패를 '미등록' 으로 뭉뚱그리면 원인 추적이 죽는다★ — 별 reason 으로
        분리하고 `identity_probe.parse_error` 에 실제 예외를 echo 한다.
        """
        _write(session_repo / "hooks" / "hooks.json", "{ this is not json")
        exit_code, payload = run_gate(session_repo)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"] == "hooks_registration_unparseable", payload
        assert "parse_error" in payload["identity_probe"], payload
        assert payload["trace"]["hook_registered"] is False

    @pytest.mark.parametrize("payload_shape,expected_shape", [
        ({"hooks": {"SubagentStop": [{"hooks": []}]}}, "hooks.dict"),
        ({"SubagentStop": [{"hooks": []}]}, "flat.dict"),
        ({"hooks": [{"event_type": "SubagentStop"}]}, "hooks.list"),
        ([{"event_type": "SubagentStop"}], "top.list"),
    ])
    def test_supported_registration_shapes(self, session_repo, payload_shape, expected_shape):
        """★born-broken 재발 방지★ — 4 구조 전건에서 등록을 인식해야 한다.

        종전 결함의 절반은 "실제 구조(`hooks` 값이 dict)를 훑지 않음" 이었다.
        `hooks.dict` 케이스가 그 회귀를 직접 겨눈다.
        """
        simulate_session(session_repo, 1, hook_active=True)
        write_registration(session_repo, payload_shape)
        exit_code, payload = run_gate(session_repo)
        assert payload["trace"]["hook_registered"] is True, payload
        assert payload["identity_probe"]["registration_shape"] == expected_shape, payload
        assert exit_code == EXIT_PASS, payload

    def test_registration_path_is_resolved_and_echoed(self, tmp_path):
        """[154-AC-13] resolve 된 등록면 경로를 probe 에 echo 한다.

        ★경로 미도달이 곧 vacuous 판정★ 이었던 것이 종전 born-broken 의 직접
        원인이므로, "어느 후보를 실제로 열었는지" 를 반드시 밖으로 내보낸다.
        """
        # 1순위(hooks/hooks.json) 가 있으면 그것을 쓴다
        primary = tmp_path / "primary"
        build_session_repo(primary)
        _, p1 = run_gate(primary)
        assert p1["identity_probe"]["resolved_registration_file"].replace("\\", "/") \
            == "hooks/hooks.json", p1

        # 1순위 부재 시 2순위(repo 루트) 로 degrade 하되 그 사실을 echo 한다
        fallback = tmp_path / "fallback"
        write_registration(fallback, _REAL_SHAPE, rel="hooks.json")
        _write(fallback / ".claude" / "ledger" / "stop-event.jsonl", "")
        _, p2 = run_gate(fallback)
        assert p2["identity_probe"]["resolved_registration_file"] == "hooks.json", p2
        assert p2["trace"]["hook_registered"] is True, p2

    def test_trace_and_probe_shape(self, session_repo):
        """[154-AC-5] trace numeric (기대 종료 수 · emit row 수)."""
        simulate_session(session_repo, 4, hook_active=True)
        _, payload = run_gate(session_repo, expected_stops=4)
        trace = payload["trace"]
        assert trace["ledger_row_count"] == 4
        assert trace["expected_stop_count"] == 4
        assert isinstance(trace["ledger_row_count"], int)
        assert isinstance(trace["expected_stop_count"], int)
        assert isinstance(trace["hook_registered"], bool)
        assert isinstance(trace["ledger_exists"], bool)
        assert str(session_repo) in payload["identity_probe"]["repo_root"]

    def test_negative_expected_stops_is_fail_closed(self, session_repo):
        """음수 기대치 = 미지 입력 → fail-closed RED (기본값 대체 금지)."""
        exit_code, payload = run_gate(session_repo, expected_stops=-1)
        assert exit_code == EXIT_RED, payload
        assert payload["reason"] == "expected_stops_negative", payload


class TestNG16Hygiene:
    def test_uses_gate_verdict_helpers(self):
        """공유 헬퍼 재사용 (신규 verdict 체계 발명 금지)."""
        import check_subagent_stop_auto_emit as mod

        source = Path(mod.__file__).read_text(encoding="utf-8")
        assert "from gate_verdict import" in source
        assert "empty_target(" in source
        assert "unknown_input(" in source


# ===========================================================================
# 실 repo — born-broken 회귀 가드 (수정 전이면 반드시 실패한다)
# ===========================================================================

def test_real_repo_registration_channel_reaches_actual_surface(repo_root):
    """★born-broken 회귀 가드★ — 게이트가 **실제 등록면에 도달**하는지 실측.

    wrapper 의 실 등록면은 `hooks/hooks.json` 이고 `SubagentStop` 이 정상 등록돼
    있다(firsthand: `hooks/hooks.json:183`). 종전 구현은 `<repo_root>/hooks.json`
    을 보고 `data["hooks"]` 를 list 로 가정해 ★항상 `hook_registered: false`★ 였다
    (= false RED, 판별력 0). 이 테스트는 그 회귀를 직접 겨눈다.

    ★verdict 자체는 고정하지 않는다★ — 원장(`.claude/ledger/stop-event.jsonl`)
    존재 여부는 세션마다 달라 PASS(행 있음) / INCONCLUSIVE(행 없음) 로 갈린다.
    고정하는 것은 ★등록면 도달★ 과 ★false RED 부재★ 두 가지다.
    """
    exit_code, payload = run_gate(Path(repo_root))
    probe = payload["identity_probe"]

    assert payload["trace"]["hook_registered"] is True, \
        "실 등록면에 도달하지 못했다 (born-broken 회귀): %s" % payload
    assert probe["resolved_registration_file"] is not None
    assert probe["resolved_registration_file"].replace("\\", "/").endswith("hooks.json")
    assert payload["reason"] != "subagent_stop_hook_not_registered", payload
    assert exit_code != EXIT_RED, payload
    assert payload["verdict"] in ("PASS", "INCONCLUSIVE"), payload
