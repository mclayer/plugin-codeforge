"""보안 lane iter1 **S-3 / S-6** — 원장에 실을 수 있는 값의 형(型) 위생.

**S-3 (`elapsed_seconds`)**: T-TAMP-2 의 usage sanity 는 `_USAGE_INT_FIELDS` 7종만 덮고
`elapsed_seconds` 는 빠져 있었다. 그래서 `_coerce_float_or_none` 이 `float("NaN")` /
`float("Infinity")` / 음수 / `True`(bool 은 int subclass → `float(True)==1.0`) 를 전부
통과시킨다. NaN·Infinity 는 `json.dumps` 가 `NaN` / `Infinity` **bare 리터럴**로 써버려
원장 행이 **RFC 8259 위반 JSON** 이 되고, 엄격한 downstream 파서에서 그 행이 통째로
사라진다 — 게다가 NaN 은 비교 연산에 전파돼 정렬·집계를 조용히 오염시킨다. bool 은
`1.0` 초로 둔갑해 **측정한 적 없는 값이 측정치인 척** 착지한다(fake-attributed 와 같은 죄).
계약: 비음수 + `math.isfinite` + bool 배제(int 쌍둥이와 대칭).

**S-6 (args-file 값 타입)**: args-file 병합은 `setattr` 로 **JSON 값을 그대로** args 에
꽂는다. `{"story-key": {"a": 1}}` 이면 `str(args.story_key)` 가 `"{'a': 1}"` — 파이썬 repr
이 원장 필드로 착지한다(list 도 동일). scalar 만 허용하고 dict/list 는 거부 + WARN.

불변: append 경로는 **exit-0 / never-block**(ADR-115) — 값이 불량이어도 차단하지 않는다.
정상 처분은 "해당 값을 버리고(null/기본값) WARN + 필요 시 unattributed 강등" 이다.

production 로직 재구현 금지 — 실제 `append_spawn_event.py` CLI(run_append) 호출로만 판정.
"""

from __future__ import annotations

import json

import pytest

_NON_JSON_CONSTANTS = ("NaN", "Infinity", "-Infinity")


def _write_args_file(path, payload):
    """args-file 작성. `allow_nan=True`(기본) — NaN/Infinity 를 실제 writer 형상대로 실어보낸다."""
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def _assert_rfc8259_strict(ledger):
    """원장 각 행이 **엄격 JSON**(RFC 8259) 인지 — bare NaN/Infinity 리터럴 0.

    `parse_constant` 는 `NaN`/`Infinity`/`-Infinity` 리터럴을 만났을 때만 호출된다.
    """
    text = ledger.read_text(encoding="utf-8")
    for idx, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        json.loads(
            line,
            parse_constant=lambda c, _i=idx: pytest.fail(
                f"원장 {_i}행에 RFC 8259 비적합 리터럴 {c!r} 착지 — 엄격 파서에서 행 전체가 소실됨"
            ),
        )


_BASE = {
    "story-key": "CFP-2850",
    "lane-label": "구현",
    "agent-type": "DeveloperAgent",
    "session-id": "sess-val",
    "agent-id": "agent-val",
    "spawn-seq": "1",
}


# ─────────────────────── S-3 — elapsed_seconds sanity ───────────────────────


def _run_bad_elapsed(tmp_path, run_append, read_rows, label, value):
    """불량 elapsed_seconds 1건 append → 공통 불변식 확인 후 (row, stderr) 반환.

    공통 불변식 = never-block(exit 0) + row 기록 + 엄격 JSON + WARN 가시화.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    args_file = _write_args_file(
        tmp_path / f"args-{label}.json", dict(_BASE, **{"elapsed-seconds": value})
    )
    res = run_append(ledger, opt_in=True, args_file=str(args_file))

    # 측정 assertion (a): never-block — 불량 값이 append 를 차단하지 않는다
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    rows = read_rows(ledger)
    assert len(rows) == 1, f"record-only: row 는 여전히 기록돼야 함, got {len(rows)}"
    # (b): 원장 행이 엄격 JSON — bare NaN/Infinity 리터럴 0 (RFC 8259)
    _assert_rfc8259_strict(ledger)
    raw = ledger.read_text(encoding="utf-8")
    for const in _NON_JSON_CONSTANTS:
        assert f": {const}" not in raw, f"원장 raw 에 bare {const} 리터럴 착지 — raw={raw!r}"
    # (c): 무음 drop 금지 — 어떤 필드가 왜 문제였는지 stderr 로 식별 가능
    assert "WARN" in res.stderr and "elapsed_seconds" in res.stderr, (
        f"elapsed_seconds 불량값이 무음 처리됨 — stderr={res.stderr!r}"
    )
    return rows[0], res.stderr


_NULLED_ELAPSED = [
    ("nan-string", "NaN"),
    ("inf-string", "Infinity"),
    ("neg-inf-string", "-Infinity"),
    ("nan-float", float("nan")),
    ("inf-float", float("inf")),
    ("bool-true", True),
    ("bool-false", False),
]


@pytest.mark.parametrize("label,value", _NULLED_ELAPSED, ids=[c[0] for c in _NULLED_ELAPSED])
def test_elapsed_seconds_non_finite_or_bool_lands_as_null(
    tmp_path, run_append, read_rows, label, value
):
    """(disc) NaN / ±Infinity / bool 은 `elapsed_seconds` 로 **착지하지 않는다**(null).

    NaN·Infinity 는 `json.dumps` 가 비표준 토큰으로 직렬화해 원장 행 자체를 RFC 8259
    미적합으로 만든다 — 엄격 파서를 쓰는 downstream 에서 그 행이 통째로 사라진다.
    bool 은 `float(True)==1.0` 로 둔갑해 **측정한 적 없는 1초** 가 측정치인 척 앉는다.
    discriminating: `_coerce_float_or_none` 이 구 구현(`float(value)` 무검증)으로 돌아가면
    값이 실려 RED (NaN/Inf 는 엄격 JSON assert 까지 동반 RED).
    """
    row, _ = _run_bad_elapsed(tmp_path, run_append, read_rows, label, value)
    assert row["elapsed_seconds"] is None, (
        f"elapsed_seconds={value!r} 가 원장에 {row['elapsed_seconds']!r} 로 착지 — "
        f"측정한 적 없는 값이 측정치로 둔갑(T-TAMP-2 float 축 미이행)"
    )


@pytest.mark.parametrize(
    "label,value", [("negative-int", -5), ("negative-float", -1.5)],
    ids=["negative-int", "negative-float"],
)
def test_elapsed_seconds_negative_is_never_trusted(
    tmp_path, run_append, read_rows, label, value
):
    """(disc) 음수 elapsed_seconds 는 **신뢰 측정치로 착지하지 않는다** — null 또는 unattributed.

    음수 경과시간은 물리적으로 불가능하므로 "측정했다" 고 말할 수 없다. 계약이 허용하는
    처분은 두 가지다 — 값을 null 로 버리거나(honest-null), 값은 남기되 attribution 을
    `unattributed` 로 강등해 **신뢰 표식을 떼는 것**. 어느 쪽이든 `attributed` 로 남으면
    downstream 이 -5초를 실측치로 소비한다.
    discriminating: T-TAMP-2 float 축 편입을 되돌리면 attributed + 음수값이 살아남아 RED.
    """
    row, stderr = _run_bad_elapsed(tmp_path, run_append, read_rows, label, value)
    landed = row["elapsed_seconds"]
    attribution = row["attribution_confidence"]
    # 측정 assertion: 신뢰 표식 제거 — attributed 로는 절대 남지 않는다
    assert attribution != "attributed", (
        f"음수 elapsed_seconds={value!r} 가 attributed 로 착지 — 불가능한 값이 실측치로 소비됨. "
        f"row={row!r}"
    )
    # 계약이 명시한 두 처분 중 하나여야 한다 (null 또는 unattributed 강등)
    assert landed is None or attribution == "unattributed", (
        f"음수 elapsed_seconds 처분이 계약 밖 — landed={landed!r}, "
        f"attribution={attribution!r}, stderr={stderr!r}"
    )


@pytest.mark.parametrize(
    "value,expected",
    [(12.5, 12.5), (0, 0.0), ("139.0", 139.0), (139, 139.0)],
    ids=["float", "zero", "numeric-string", "int"],
)
def test_elapsed_seconds_valid_values_preserved(
    tmp_path, run_append, read_rows, value, expected
):
    """(reg + vacuity guard) 정상 elapsed_seconds 는 그대로 보존 — 과잉 거부 회귀 방어.

    이 대조군이 없으면 위 불량 케이스들은 "elapsed_seconds 를 항상 null 로 만드는" 구현으로도
    통과해버린다(vacuous). 0 은 경계값(비음수 하한) 이라 함께 고정한다.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    args_file = _write_args_file(
        tmp_path / "args-ok.json", dict(_BASE, **{"elapsed-seconds": value})
    )
    res = run_append(ledger, opt_in=True, args_file=str(args_file))

    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    rows = read_rows(ledger)
    assert len(rows) == 1
    # 측정 assertion: 정상 값은 무손실 보존
    assert rows[0]["elapsed_seconds"] == expected, (
        f"정상 elapsed_seconds={value!r} 가 {rows[0]['elapsed_seconds']!r} 로 변형/소실 — "
        f"sanity 검사의 과잉 거부. stderr={res.stderr!r}"
    )
    assert "elapsed_seconds" not in res.stderr, (
        f"정상 값에 대해 WARN 발화 — 경보 피로 유발. stderr={res.stderr!r}"
    )


# ─────────────────────── S-6 — args-file 값은 scalar 만 ───────────────────────


def test_argsfile_dict_and_list_values_rejected_with_warn(tmp_path, run_append, read_rows):
    """(disc) args-file 값이 dict / list 면 **거부 + WARN** — 파이썬 repr 착지 0.

    구 구현은 JSON 값을 그대로 `setattr` 해서 `str(args.story_key)` 가 `"{'a': 1}"` 로
    원장에 실렸다. 계약 필드에 파이썬 repr 이 들어가면 downstream 파싱/집계/조인이
    조용히 어긋난다(그리고 그 행은 "정상 row" 처럼 보인다).
    discriminating: scalar 검증을 빼면 repr 이 착지해 (b)/(c) RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    payload = dict(_BASE)
    payload["story-key"] = {"a": 1}
    payload["agent-type"] = ["x", "y"]
    payload["lane-label"] = {"nested": ["구현"]}
    payload["total-tokens"] = {"n": 5}
    args_file = _write_args_file(tmp_path / "args-container.json", payload)

    res = run_append(ledger, opt_in=True, args_file=str(args_file))

    # 측정 assertion (a): never-block — 거부해도 row 는 기록
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    rows = read_rows(ledger)
    assert len(rows) == 1, f"record-only: row 는 여전히 기록돼야 함, got {len(rows)}"
    row = rows[0]
    # (b): repr 흔적 0 — raw 행에 dict/list 문자열이 없다
    raw = ledger.read_text(encoding="utf-8")
    for fragment in ("{'a'", "['x'", "'nested'", "{'n'"):
        assert fragment not in raw, (
            f"args-file 의 container 값이 파이썬 repr 로 원장에 착지: {fragment!r} in {raw!r}"
        )
    # (c): 필드 자체가 scalar 형 유지 (dict/list 가 JSON object/array 로 실리지도 않는다)
    assert isinstance(row["story_key"], str) and "{" not in row["story_key"], (
        f"story_key 가 container 로 오염됨: {row['story_key']!r}"
    )
    assert isinstance(row["agent_type"], str) and "[" not in row["agent_type"], (
        f"agent_type 이 container 로 오염됨: {row['agent_type']!r}"
    )
    assert isinstance(row["lane_label"], str) and "{" not in row["lane_label"], (
        f"lane_label 이 container 로 오염됨: {row['lane_label']!r}"
    )
    assert row["total_tokens"] is None or isinstance(row["total_tokens"], int), (
        f"total_tokens 가 container 로 오염됨: {row['total_tokens']!r}"
    )
    # (d): 무음 drop 금지 — 어떤 키가 거부됐는지 stderr 로 식별 가능
    assert "WARN" in res.stderr, f"container 값 거부가 무음 처리됨 — stderr={res.stderr!r}"
    for name in ("story_key", "agent_type", "lane_label", "total_tokens"):
        assert name in res.stderr, (
            f"거부된 키 '{name}' 가 stderr 에 식별되지 않음(무음 drop) — stderr={res.stderr!r}"
        )


def test_argsfile_scalar_values_still_merge(tmp_path, run_append, read_rows):
    """(reg + vacuity guard) scalar(문자열 / 정수 / 한국어) 는 여전히 정상 병합.

    이 대조군이 없으면 위 테스트는 "args-file 병합을 통째로 끄는" 구현으로도 통과한다.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    args_file = _write_args_file(
        tmp_path / "args-scalar.json",
        dict(_BASE, **{"total-tokens": 139284, "attribution-confidence": "attributed"}),
    )
    res = run_append(ledger, opt_in=True, args_file=str(args_file))

    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    rows = read_rows(ledger)
    assert len(rows) == 1
    # 측정 assertion: scalar 병합 무손상 (한국어 lane_label 포함)
    assert rows[0]["story_key"] == "CFP-2850"
    assert rows[0]["lane_label"] == "구현"
    assert rows[0]["agent_type"] == "DeveloperAgent"
    assert rows[0]["total_tokens"] == 139284, (
        f"scalar 값 병합이 깨짐 — container 거부의 과잉 적용. got {rows[0]['total_tokens']!r}"
    )
