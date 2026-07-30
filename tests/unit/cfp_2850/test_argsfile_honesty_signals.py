"""구현리뷰 FIX Iter2 — args-file 채널 + 정직 신호 gate (F-CR-004 / F-CR-008 / F-CR-009 / F-CR-010 / F-CR-014).

Change Plan §3.4 args-file 채널(OQ-3 / T-ELEV-1) + §7.2 T-TAMP-2 + ADR-043 §결정 1 opt-in.
전부 "조용히 잘못되는" 경로를 가시화/차단하는 축이라 하나의 파일로 묶는다:

  - F-CR-004 ①  args-file 미지의 키 drop → **stderr WARN**(무음 drop 금지)
  - F-CR-004 ③  attributed 인데 token 측정 field 전무 → **unattributed 강등**(hollow attributed 금지)
  - F-CR-008    T-TAMP-2 sanity 를 **argv 경로까지** 적용(전달 매체별 비대칭 구멍 봉인)
  - F-CR-009    args-file 이 **opt-in gate flag 를 실어 우회 금지**(정책 채널 아님)
  - F-CR-010    args-file `utf-8-sig` 수용(BOM 있는 UTF-8 — Windows 편집기 산출)
  - F-CR-014    미매칭 enum 값 → **stderr WARN**(무음 강등 금지) / 미제공은 WARN 대상 아님

production 로직 재구현 금지 — 전부 실 `append_spawn_event.py` CLI(run_append) 호출 결과로 판정.
exit-masking(`|| true` 류) 없음: 모든 실행은 returncode + row 상태 + stderr 를 동반 assert.
"""

from __future__ import annotations

import json


def _write_args_file(path, payload, encoding="utf-8"):
    """UTF-8(옵션 BOM) JSON args-file 작성 — 실 writer(Orchestrator) 형상 모사 fixture."""
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding=encoding)
    return path


# ─────────────── F-CR-004 ① — 미지의 키 drop 은 stderr 로 가시화 ───────────────


def test_argsfile_unknown_key_dropped_with_stderr_warn(tmp_path, run_append, read_rows):
    """(disc) args-file 의 allow-list 밖 키는 drop 하되 **stderr WARN** 으로 표면화.

    무음 drop 이면 오타 키(`total-token`)나 계약 drift(writer 가 보내는 신규 field 를 append 가
    모름)가 조용히 사라지고 row 는 정상처럼 보인다 (silent-success-on-error).
    mutation: WARN 을 지우면(무음 drop 복귀) RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    args_file = _write_args_file(tmp_path / "args.json", {
        "story-key": "CFP-2850",
        "lane-label": "구현",
        "agent-type": "DeveloperAgent",
        "session-id": "sess-drop", "agent-id": "agent-drop", "spawn-seq": "1",
        "total-token": 139284,      # 오타 (정상은 total-tokens) → drop 대상
        "wasted_tokens": 999,       # 계약 밖 field → drop 대상
    })
    res = run_append(ledger, args_file=str(args_file))

    # 측정 assertion (a): record-only never-block (drop 은 실패가 아님)
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    rows = read_rows(ledger)
    assert len(rows) == 1, f"drop 이 있어도 row 는 기록돼야 함(graceful), got {len(rows)}"
    # (b): drop 이 stderr 로 VISIBLE + 어떤 키가 사라졌는지 식별 가능
    assert "WARN" in res.stderr, f"drop 이 무음 처리됨 (stderr WARN 부재), stderr={res.stderr!r}"
    for name in ("total_token", "wasted_tokens"):
        assert name in res.stderr, (
            f"drop 된 키 '{name}' 가 stderr 에 식별되지 않음(무음 drop) — stderr={res.stderr!r}"
        )
    # (c): drop 된 키는 row 에 유입되지 않음 (allow-list 무손상)
    assert "wasted_tokens" not in rows[0] and "total_token" not in rows[0], (
        f"allow-list 밖 키가 row 에 유입됨: {sorted(rows[0].keys())}"
    )
    # (d): 정상 키는 정상 병합 (drop 이 전체 병합을 망치지 않음)
    assert rows[0]["story_key"] == "CFP-2850" and rows[0]["lane_label"] == "구현"


# ─────────────── F-CR-009 — args-file 은 opt-in gate 를 우회할 수 없다 ───────────────


def test_argsfile_cannot_bypass_opt_in_gate(tmp_path, run_append, read_rows):
    """(disc) args-file 이 telemetry/spawn_event gate flag 를 실어도 **row 0** (우회 차단).

    opt-in 은 정책 결정(ADR-043 §결정 1 default false)이며 gate source = 명시 CLI flag 또는
    project config 뿐이다. args-file 은 **측정 실값 채널** — 파일 하나로 always-on 이 되면
    consumer 의 opt-out 이 무력화된다.
    mutation: gate flag 를 병합 대상에 되돌리면 row 1 → RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    args_file = _write_args_file(tmp_path / "args.json", {
        "story-key": "CFP-2850", "lane-label": "구현", "agent-type": "DeveloperAgent",
        "session-id": "sess-bypass", "agent-id": "agent-bypass", "spawn-seq": "1",
        "telemetry-enabled": True,      # ← gate 우회 시도
        "spawn-event-enabled": True,    # ← gate 우회 시도
    })
    res = run_append(ledger, opt_in=False, args_file=str(args_file))

    # 측정 assertion (a): opt-in OFF 유지 → row 0 (silent always-on 차단)
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    assert read_rows(ledger) == [], (
        "args-file 의 gate flag 로 opt-in 이 우회됨 — telemetry always-on bypass (ADR-043 §결정 1 위반)"
    )
    # (b): 우회 시도는 무음 무시가 아니라 stderr 로 가시화
    assert "WARN" in res.stderr and (
        "telemetry_enabled" in res.stderr or "telemetry-enabled" in res.stderr
    ), f"gate flag 병합 거부가 stderr 로 표면화돼야 함, stderr={res.stderr!r}"


# ─────────────── F-CR-010 — args-file utf-8-sig(BOM) 수용 ───────────────


def test_argsfile_utf8_bom_accepted_with_korean_values(tmp_path, run_append, read_rows):
    """(disc) BOM 있는 UTF-8 args-file 도 정상 병합 (Windows 편집기/PowerShell 산출 형상).

    BOM 미수용이면 json parse 실패 → argv 값으로 fallback → lane_label 이 '없음' 으로 붕괴
    (한국어 lane-context 유실 = AC-14 dedup 이 다시 vacuous).
    mutation: reader 를 utf-8 로 되돌리면 lane_label='없음' → RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    args_file = _write_args_file(
        tmp_path / "args-bom.json",
        {
            "story-key": "CFP-2850", "lane-label": "구현-리뷰",
            "agent-type": "CodeReviewPLAgent",
            "session-id": "sess-bom", "agent-id": "agent-bom", "spawn-seq": "1",
        },
        encoding="utf-8-sig",  # ← BOM 부착
    )
    # fixture 실재 확인: 파일이 실제로 BOM 으로 시작 (vacuous 방지)
    assert args_file.read_bytes().startswith(b"\xef\xbb\xbf"), "BOM fixture 가 실제로 BOM 을 못 가짐"

    res = run_append(ledger, args_file=str(args_file))
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    rows = read_rows(ledger)
    assert len(rows) == 1, f"BOM args-file 병합 실패로 row 형상 붕괴, stderr={res.stderr!r}"
    # 측정 assertion: BOM 파일의 한국어 lane_label 이 그대로 병합 (fallback '없음' 아님)
    assert rows[0]["lane_label"] == "구현-리뷰", (
        f"BOM 있는 args-file 의 lane_label 병합 실패(파싱 실패 → argv fallback), "
        f"got {rows[0]['lane_label']!r} / stderr={res.stderr!r}"
    )
    assert rows[0]["agent_type"] == "CodeReviewPLAgent"


# ─────────────── F-CR-008 — T-TAMP-2 sanity 는 argv 경로에도 적용 ───────────────


def test_ttamp2_argv_negative_usage_forces_unattributed(tmp_path, run_append, read_rows):
    """(disc) argv 로 전달된 음수 usage 정수도 T-TAMP-2 위반 → unattributed 강제 + token null.

    구 구현은 sanity 검증이 args-file 병합 안에만 있어, 같은 값을 argv 로 주면 무검증 통과했다
    (전달 매체별 비대칭 구멍). mutation: 검증을 args-file 안으로 되돌리면 attributed + 음수
    저장 → RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-tamp-argv", agent_id="agent-tamp-argv", spawn_seq="1",
        attribution_confidence="attributed", model="claude-opus-4",
        total_tokens=-5,  # ← argv 경로 T-TAMP-2 위반 (비음수 위반)
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    row = read_rows(ledger)[0]
    # 측정 assertion (a): 위반 → attribution 강등 (추정·오염값 승격 금지)
    assert row["attribution_confidence"] == "unattributed", (
        f"argv 경로 T-TAMP-2 위반인데 attributed 유지됨, got {row['attribution_confidence']}"
    )
    # (b): token null (음수 오염값 저장 금지)
    assert row["total_tokens"] is None, f"오염 usage 값이 저장됨, got {row['total_tokens']}"
    assert row["cost_usd"] is None
    # (c): 위반은 stderr 로 VISIBLE
    assert "WARN" in res.stderr and "total_tokens" in res.stderr, (
        f"T-TAMP-2 위반이 stderr 로 표면화돼야 함, stderr={res.stderr!r}"
    )


def test_ttamp2_argv_overflow_usage_forces_unattributed(tmp_path, run_append, read_rows):
    """(disc) argv 상한 초과(overflow) usage 정수도 동일하게 unattributed 강제.

    비음수 축과 상한 축은 별 위반이므로 둘 다 pin (한쪽만 구현해도 RED 되도록).
    """
    ledger = tmp_path / "spawn-event.jsonl"
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-tamp-cap", agent_id="agent-tamp-cap", spawn_seq="1",
        attribution_confidence="attributed", model="claude-opus-4",
        total_tokens=10 ** 15,  # ← sanity cap(1e12) 초과
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    row = read_rows(ledger)[0]
    # 측정 assertion: 상한 초과 → unattributed + token null
    assert row["attribution_confidence"] == "unattributed", (
        f"상한 초과인데 attributed 유지됨, got {row['attribution_confidence']}"
    )
    assert row["total_tokens"] is None, f"상한 초과 값이 저장됨, got {row['total_tokens']}"


# ─────────────── F-CR-004 ③ — hollow attributed 강등 ───────────────


def test_hollow_attributed_demoted_without_token_measurement(tmp_path, run_append, read_rows):
    """(disc) attributed 선언 + token 측정 field 전무 → unattributed 강등 (hollow attributed 금지).

    계약 §2: attributed = "측정 실측 source 확보(4-way 분해 OR aggregate-only)". 측정치가
    하나도 없는 attributed row 는 상태 표기와 실체가 모순이며, AC-15 landing bar(attributed
    row ≥1)를 **bare 배선만으로** 통과시키는 activation≠landing 위장 경로가 된다.
    양팔 대조로 vacuous 아님 실증: 측정 1개(total_tokens) 있으면 attributed 유지(tier-2).
    """
    # (a) hollow: attributed 선언, 측정 field 0 → 강등
    ledger_hollow = tmp_path / "hollow.jsonl"
    res_h = run_append(
        ledger_hollow, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-hollow", agent_id="agent-hollow", spawn_seq="1",
        attribution_confidence="attributed", model="claude-opus-4",
    )
    assert res_h.returncode == 0, f"exit {res_h.returncode}: {res_h.stderr}"
    row_h = read_rows(ledger_hollow)[0]
    # 측정 assertion (a): 측정 전무 attributed → unattributed 강등
    assert row_h["attribution_confidence"] == "unattributed", (
        f"측정 field 전무인데 attributed 로 기록됨(hollow attributed), "
        f"got {row_h['attribution_confidence']}"
    )
    assert row_h["total_tokens"] is None and row_h["cost_usd"] is None
    # 강등은 stderr 로 VISIBLE (무음 강등 금지)
    assert "WARN" in res_h.stderr, f"hollow 강등이 stderr 로 표면화돼야 함, stderr={res_h.stderr!r}"

    # (b) tier-3 형상(계약 §2.2): duration 실측만 있고 token 부재 → 여전히 unattributed
    ledger_t3 = tmp_path / "tier3.jsonl"
    res_t3 = run_append(
        ledger_t3, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-t3", agent_id="agent-t3", spawn_seq="1",
        attribution_confidence="attributed", duration_ms=524995, tool_call_count=25,
        termination_cause="zero_output",
    )
    assert res_t3.returncode == 0, f"exit {res_t3.returncode}: {res_t3.stderr}"
    row_t3 = read_rows(ledger_t3)[0]
    # 측정 assertion (b): duration/tool 은 token source 가 아님 → tier-3 = unattributed
    assert row_t3["attribution_confidence"] == "unattributed", (
        "계약 §2.2 tier-3(블록 부재, duration=wall-clock) 형상은 unattributed 여야 함 — "
        f"duration 존재를 attribution 근거로 세면 오분류, got {row_t3['attribution_confidence']}"
    )
    assert row_t3["duration_ms"] == 524995, "duration 실측 자체는 보존 (강등이 measure 를 지우지 않음)"
    assert row_t3["total_tokens"] is None

    # (c) positive control: 측정 1개(tier-2 aggregate-only) → attributed 유지 (강등 아님)
    ledger_ok = tmp_path / "tier2.jsonl"
    res_ok = run_append(
        ledger_ok, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-tier2", agent_id="agent-tier2", spawn_seq="1",
        attribution_confidence="attributed", model="claude-opus-4", total_tokens=139284,
    )
    assert res_ok.returncode == 0, f"exit {res_ok.returncode}: {res_ok.stderr}"
    row_ok = read_rows(ledger_ok)[0]
    # 측정 assertion (c): tier-2 는 강등 대상 아님 (강등 규칙이 과잉 아님을 실증)
    assert row_ok["attribution_confidence"] == "attributed", (
        f"tier-2(aggregate-only) 는 attributed 유지여야 함(과잉 강등), "
        f"got {row_ok['attribution_confidence']}"
    )
    assert row_ok["total_tokens"] == 139284


# ─────────────── F-CR-014 — 미매칭 enum 값 WARN (미제공은 대상 아님) ───────────────


def test_unmatched_enum_value_warns_on_stderr(tmp_path, run_append, read_rows):
    """(disc) closed-set 밖 enum 값은 강등하되 **stderr WARN** 으로 표면화 (무음 강등 금지).

    호출자 오타(outcome='succeeded')와 "값 미제공"이 ledger 상 동일(null)이라, WARN 이 없으면
    분류 파이프라인의 오타가 영구 미검출된다.
    mutation: WARN 제거 시 RED. (강등 자체는 유지 — record-only never-block)
    """
    ledger = tmp_path / "spawn-event.jsonl"
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-enum-warn", agent_id="agent-enum-warn", spawn_seq="1",
        outcome="succeeded",              # ← 오타 (정상은 success)
        termination_cause="timed_out",    # ← 오타 (정상은 timeout)
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    row = read_rows(ledger)[0]
    # 측정 assertion (a): 강등은 유지 (free-form leak 0 — T-INFO-8)
    assert row["outcome"] is None and row["termination_cause"] is None, (
        f"미매칭 값이 row 에 leak: outcome={row['outcome']!r}, tc={row['termination_cause']!r}"
    )
    # (b): 강등 사실이 field 명과 함께 stderr 로 VISIBLE
    assert "WARN" in res.stderr, f"미매칭 enum 강등이 무음 처리됨, stderr={res.stderr!r}"
    assert "outcome" in res.stderr and "termination_cause" in res.stderr, (
        f"어떤 field 가 강등됐는지 stderr 로 식별 가능해야 함, stderr={res.stderr!r}"
    )


def test_absent_enum_value_does_not_warn(tmp_path, run_append, read_rows):
    """(경계) enum 값 **미제공**은 정상 honest-null — WARN 대상 아님 (WARN 남발 차단).

    미제공까지 WARN 하면 정상 경로가 경고로 도배돼 실제 오타 신호가 묻힌다.
    mutation: 미제공에도 WARN 하면 stderr 비어있지 않아 RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    res = run_append(
        ledger, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-enum-quiet", agent_id="agent-enum-quiet", spawn_seq="1",
        # outcome / termination_cause / model 전부 미제공
    )
    assert res.returncode == 0, f"exit {res.returncode}: {res.stderr}"
    row = read_rows(ledger)[0]
    assert row["outcome"] is None and row["termination_cause"] is None, "미제공 → honest-null"
    # 측정 assertion: 정상 경로 stderr 무출력 (WARN 남발 없음)
    assert res.stderr.strip() == "", (
        f"미제공(정상 honest-null) 경로에서 WARN 발생 — 신호 대 잡음 붕괴, stderr={res.stderr!r}"
    )
