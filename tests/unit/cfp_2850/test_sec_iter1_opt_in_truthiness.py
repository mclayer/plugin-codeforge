"""보안 lane iter1 **S-1** — opt-in gate 문자열 truthiness 정규화 (fail-open 회귀 방어).

구 구현의 `_opt_in_enabled` 는 config 값을 `bool(tel.get("enabled", False))` 로만 접었다.
YAML 에서 운영자가 `enabled: "false"` 처럼 **따옴표**를 붙이면 값이 bool 이 아니라 **문자열**
`"false"` 가 되고, 비어있지 않은 문자열은 파이썬에서 전부 truthy → **운영자가 명시적으로 끈
계측이 그대로 돌아간다**(fail-open, ADR-043 §결정 1 opt-in default false 위반). `"no"`·`"off"`·
`"0"` 도 동일하다. 이 축은 조용히 틀리는 경로라 — 원장에 row 가 쌓이는 것 말고는 아무 신호가
없다 — 실패를 눈으로 볼 수 있는 테스트가 유일한 방벽이다.

본 파일이 고정하는 계약:
  - quoted falsey 문자열(`"false"` / `"no"` / `"off"` / `"0"` / `""`) = **False** → row 0.
  - 미지 문자열(`"maybe"`) = **fail-closed**(row 0) + stderr WARN (무음 판정 금지).
  - unquoted bool / int(`false` / `0` / `true` / `1`) = 기존 동작 **보존**(과잉 거부 회귀 방어).

불변: append 경로는 **exit-0 / never-block**(ADR-115) — gate OFF 는 "실패" 가 아니라 no-op 다.
따라서 어떤 케이스에서도 비-0 exit 를 기대하지 않는다.

production 로직 재구현 금지 — 전부 실제 `append_spawn_event.py` CLI(run_append) 호출 결과로 판정.
"""

from __future__ import annotations

import json

import pytest

try:  # production 이 lazy import 하는 선택 의존 — 부재 환경에서도 축이 죽지 않게 json 으로 대체
    import yaml as _yaml  # noqa: F401

    _CONFIG_KIND = "yaml"
except ImportError:  # pragma: no cover — pyyaml 부재 환경
    _CONFIG_KIND = "json"


def _write_project_config(proj, enabled_literal, spawn_literal, enabled_value, spawn_value):
    """`${CLAUDE_PROJECT_DIR}` 의 telemetry config 작성 (실 운영자 형상 모사).

    yaml 경로는 **따옴표 유무를 raw 텍스트로 직접 제어**한다 — `"false"`(문자열) 와
    `false`(bool) 의 구분이 본 축의 전부이므로 직렬화기에 맡기지 않는다.
    """
    proj.mkdir(parents=True, exist_ok=True)
    if _CONFIG_KIND == "yaml":
        path = proj / "project.yaml"
        path.write_text(
            "telemetry:\n"
            "  enabled: %s\n"
            "  channels:\n"
            "    spawn_event: %s\n" % (enabled_literal, spawn_literal),
            encoding="utf-8",
        )
        return path
    path = proj / "project.json"
    path.write_text(
        json.dumps(
            {"telemetry": {"enabled": enabled_value, "channels": {"spawn_event": spawn_value}}}
        ),
        encoding="utf-8",
    )
    return path


def _run_with_config(tmp_path, monkeypatch, run_append, **cfg):
    """config 만으로 gate 를 판정시키는 실행 (CLI opt-in flag 미부착)."""
    proj = tmp_path / "proj"
    cfg_path = _write_project_config(proj, **cfg)
    assert cfg_path.is_file(), "config fixture 미생성 — vacuous 실행 방지"
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(proj))
    ledger = tmp_path / "spawn-event.jsonl"
    res = run_append(
        ledger,
        opt_in=False,  # ← CLI flag 미부착: gate source 를 config 로 강제
        story_key="CFP-2850",
        lane_label="구현",
        agent_type="DeveloperAgent",
        session_id="sess-optin",
        agent_id="agent-optin",
        spawn_seq="1",
    )
    return res, ledger


# quoted falsey 문자열 — (python 값, yaml literal spelling)
_QUOTED_FALSEY = [
    ("false", '"false"'),
    ("no", '"no"'),
    ("off", '"off"'),
    ("0", '"0"'),
    ("", '""'),
]
_FALSEY_IDS = ["quoted-false", "quoted-no", "quoted-off", "quoted-zero", "quoted-empty"]


@pytest.mark.parametrize("value,literal", _QUOTED_FALSEY, ids=_FALSEY_IDS)
def test_optin_quoted_falsey_string_keeps_gate_closed(
    tmp_path, monkeypatch, run_append, read_rows, value, literal
):
    """(disc) 따옴표 붙은 falsey 문자열은 gate 를 **열지 못한다** — row 0.

    discriminating: 구 구현(`bool("false") is True`)으로 되돌리면 row 1 → RED.
    (`""` 만은 구 구현에서도 falsey — regression-guard 성격으로 동반 고정한다.)
    """
    res, ledger = _run_with_config(
        tmp_path,
        monkeypatch,
        run_append,
        enabled_literal=literal,
        spawn_literal=literal,
        enabled_value=value,
        spawn_value=value,
    )
    # 측정 assertion (a): never-block — gate OFF 는 실패가 아니라 no-op
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    # (b): row 0 — 운영자가 끈 계측이 돌아가면 fail-open
    assert read_rows(ledger) == [], (
        f"telemetry.enabled={literal} (문자열 {value!r}) 인데 row 착지 — "
        f"운영자 opt-out 이 문자열 truthiness 로 무력화됨(fail-open, ADR-043 §결정 1 위반)"
    )


def test_optin_quoted_falsey_on_channel_only_keeps_gate_closed(
    tmp_path, monkeypatch, run_append, read_rows
):
    """(disc) 상위 `enabled: true` 라도 채널이 `"false"` 면 gate 는 닫힌다 (AND 축 보존).

    gate = telemetry.enabled **AND** channels.spawn_event. 채널 키 경로도 같은 정규화를
    타는지 별도로 고정한다 — 한쪽만 고치는 부분 수리를 잡는다.
    """
    res, ledger = _run_with_config(
        tmp_path,
        monkeypatch,
        run_append,
        enabled_literal="true",
        spawn_literal='"false"',
        enabled_value=True,
        spawn_value="false",
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    assert read_rows(ledger) == [], (
        'channels.spawn_event="false"(문자열) 인데 row 착지 — 채널 축 truthiness 미정규화'
    )


def test_optin_unknown_string_fails_closed_with_warn(
    tmp_path, monkeypatch, run_append, read_rows
):
    """(disc) 해석 불가 문자열(`"maybe"`)은 **fail-closed**(row 0) + stderr WARN.

    미지 값을 truthy 로 접으면 오타 하나가 계측을 켠다. 반대로 무음으로 끄면 운영자가
    "왜 안 도는지" 를 알 길이 없다 → 닫되 **반드시 보이게** 닫는다.
    discriminating: 미지 문자열을 truthy 로 되돌리면 row 1 → RED. WARN 을 지우면 (b) RED.
    """
    res, ledger = _run_with_config(
        tmp_path,
        monkeypatch,
        run_append,
        enabled_literal='"maybe"',
        spawn_literal='"maybe"',
        enabled_value="maybe",
        spawn_value="maybe",
    )
    # 측정 assertion (a): fail-closed — 해석 불가 → 켜지 않는다
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    assert read_rows(ledger) == [], (
        "미지 opt-in 문자열 'maybe' 가 gate 를 열었음 — fail-open (해석 불가는 닫아야 함)"
    )
    # (b): 무음 판정 금지 — 왜 안 도는지 stderr 로 식별 가능
    assert "WARN" in res.stderr, (
        f"미지 opt-in 값이 무음으로 처리됨 (stderr WARN 부재) — stderr={res.stderr!r}"
    )
    assert (
        "maybe" in res.stderr or "enabled" in res.stderr or "spawn_event" in res.stderr
    ), f"WARN 이 어떤 값/필드 때문인지 식별 불가 — stderr={res.stderr!r}"


@pytest.mark.parametrize(
    "literal,value", [("false", False), ("0", 0)], ids=["unquoted-bool-false", "int-zero"]
)
def test_optin_unquoted_bool_and_int_false_still_closed(
    tmp_path, monkeypatch, run_append, read_rows, literal, value
):
    """(reg) unquoted bool / int 0 의 기존 OFF 동작 보존 — 정규화가 이 경로를 건드리지 않는다."""
    res, ledger = _run_with_config(
        tmp_path,
        monkeypatch,
        run_append,
        enabled_literal=literal,
        spawn_literal=literal,
        enabled_value=value,
        spawn_value=value,
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    assert read_rows(ledger) == [], f"telemetry.enabled={literal} 인데 row 착지"


@pytest.mark.parametrize(
    "literal,value", [("true", True), ("1", 1)], ids=["unquoted-bool-true", "int-one"]
)
def test_optin_truthy_values_still_enable(
    tmp_path, monkeypatch, run_append, read_rows, literal, value
):
    """(reg + vacuity guard) truthy 값은 여전히 gate 를 연다 — config 채널이 **살아있음**의 증거.

    이 대조군이 없으면 위 falsey 케이스들은 "config 를 아예 안 읽어서 row 0" 인 vacuous
    통과와 구분되지 않는다. 동시에 정규화가 정상 opt-in 까지 막는 과잉 거부도 잡는다.
    """
    res, ledger = _run_with_config(
        tmp_path,
        monkeypatch,
        run_append,
        enabled_literal=literal,
        spawn_literal=literal,
        enabled_value=value,
        spawn_value=value,
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    rows = read_rows(ledger)
    # 측정 assertion: config 경로가 실제로 gate 를 연다(=falsey 케이스의 row 0 이 vacuous 아님)
    assert len(rows) == 1, (
        f"telemetry.enabled={literal} (truthy) 인데 row {len(rows)} — "
        f"정규화가 정상 opt-in 을 막았거나 config 채널이 죽음. stderr={res.stderr!r}"
    )
    assert rows[0]["story_key"] == "CFP-2850"


@pytest.mark.parametrize(
    "literal,value", [('"true"', "true"), ('"1"', "1")], ids=["quoted-true", "quoted-one"]
)
def test_optin_quoted_truthy_string_is_never_silently_ignored(
    tmp_path, monkeypatch, run_append, read_rows, literal, value
):
    """(disc) quoted truthy 문자열은 **켜지거나, 끄되 WARN** — 무음 무시는 금지.

    `"0"` 이 False 로 정규화된다면 대칭으로 `"1"`/`"true"` 는 True 로 읽히는 것이 자연스럽다.
    다만 구현이 이들을 "미지 문자열" 로 보아 fail-closed 하는 선택도 계약상 허용 범위다
    (미지 = 닫되 보이게). 본 테스트는 **둘 중 어느 설계든 무방하되 조용히 틀리지는 말 것**
    만 고정한다 — 운영자가 켰다고 믿는데 아무 신호 없이 꺼져 있는 상태를 금지.
    (정책 확정은 §8 소관 — 본 assert 는 over-specify 를 피해 침묵만 차단한다.)
    """
    res, ledger = _run_with_config(
        tmp_path,
        monkeypatch,
        run_append,
        enabled_literal=literal,
        spawn_literal=literal,
        enabled_value=value,
        spawn_value=value,
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    enabled = len(read_rows(ledger)) == 1
    # 측정 assertion: enabled(=truthy 인정) 이거나, 아니면 WARN 이 반드시 동반된다
    assert enabled or "WARN" in res.stderr, (
        f"telemetry.enabled={literal} 인데 row 0 이면서 stderr WARN 도 없음 — "
        f"운영자가 켠 계측이 무음으로 무시됨. stderr={res.stderr!r}"
    )
