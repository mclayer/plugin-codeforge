"""AC-12 — single-writer topology + within-path event_id dedup + COUNT reconcile(F-B).

Change Plan §8.1.1 RTM AC-12 (4 named test). phase2.
  - hooks/subagent-stop 의 spawn-event row-write RETIRED (single-writer = Orchestrator).
  - deterministic event_id → within-path 이중 append dedup(read-time).
  - retire 후 hook∥Orchestrator 이중계산 0.
  - **F-B (discriminating)**: hook spawn-completion COUNTER > recorded row COUNT →
    survivorship gap 가시(gap 은닉 시 RED).

★F-CR-001 ⑤ (구현리뷰 FIX Iter2): COUNTER 가 opt-in gate 뒤로 이동했으므로 count-reconcile
  시나리오의 전제 regime = **opt-in ON** 이다 (OFF regime 은 counter 자체가 0 → gap 정의상 0,
  survivorship 관측 불가). 본 파일의 ledger row 는 전부 `opt_in=True` 명시로 ON regime 을 고정한다
  (기본값 의존 금지 — 기본값이 뒤집혀도 전제가 조용히 바뀌지 않도록).
  실 hook 을 fork 해 counter 를 **실제로 증가**시키는 ON-regime e2e =
  `test_ac3_counter_opt_in_gate.py::test_ac12_count_reconcile_under_opt_in_on_regime`.

production 로직 재구현 금지 — 실제 hooks/subagent-stop 텍스트 +
  scripts/lib/reconcile_spawn_completion_count.py (import + CLI) + append_spawn_event
  _compute_event_id 직접 호출.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import aggregate_spawn_event as agg  # 실 production aggregate 진입점 (AC-9/AC-10 reader)
import append_spawn_event  # 실 production 모듈 (tests/conftest.py 가 scripts/lib 주입)
import reconcile_spawn_completion_count as recon  # 실 production reconcile 모듈
import replay_spawn_event as replay  # 실 production 정본 ledger reader

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK = REPO_ROOT / "hooks" / "subagent-stop"
RECONCILE_SCRIPT = REPO_ROOT / "scripts" / "lib" / "reconcile_spawn_completion_count.py"


def _run_reconcile_cli(count_path, ledger_path):
    """실제 reconcile CLI 를 subprocess 로 fork (production 재구현 금지).

    reconcile 은 record-only → exit 0 무조건. 따라서 **exit code 단독 판정 금지** —
    도메인 sentinel(status/gap) 을 stdout JSON 으로 병행 assert (distinct-marker 의무,
    본 agent §외부 script subprocess fork 규율). Returns (returncode, parsed_json|None).
    """
    cmd = [
        sys.executable, str(RECONCILE_SCRIPT), "check",
        "--count-path", str(count_path),
        "--ledger-path", str(ledger_path),
        "--json",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    parsed = None
    try:
        parsed = json.loads(proc.stdout.strip())
    except (json.JSONDecodeError, AttributeError):
        parsed = None
    return proc.returncode, parsed


def test_ac12_single_writer_hook_spawn_append_retired():
    """(reg, 구조) hooks/subagent-stop 의 spawn-event **row-write** RETIRED — single-writer 보존.

    ★판정 기준 정정 (FIX Iter2): 구 assert 는 `"append_spawn_event" not in text` 라는
    **식별자 부재** 프록시였다. 이는 (i) row-write 가 아닌 정당한 재사용 — 예: opt-in gate 판정을
    `append_spawn_event._opt_in_enabled` import 로 **재사용**(ADR-140 reuse-before-write) — 까지
    싸잡아 RED 로 만들고, (ii) 식별자 없이 row 를 쓰는 우회(별 wrapper 경유)는 못 잡는
    양방향 부정확 프록시였다. 실 불변식은 "**spawn-event row 를 쓰지 않는다**" 이므로,
    row-writer CLI 호출의 **argv 서명**(row identity/lane-context flag)이 hook 에 없음을 본다.
    behavioral 확증(실 hook 실행 → spawn-event-v1 row 0)은
      `test_ac3_counter_opt_in_gate.py::test_ac12_hook_writes_no_spawn_event_row_under_opt_in_on`.

    mutation: hook 이 row-write 를 부활(identity flag 전달)하면 이중 writer → event_id
      cross-path 불일치로 이중계수(AC-12 위반) → 이 reg 가 RED.
    """
    text = HOOK.read_text(encoding="utf-8")
    # 실행 라인만 검사 (주석 라인 제외) — 주석의 row-flag 언급은 retire 를 **설명**하는 문서이지
    # 실행이 아니다. 실행 여부가 판정 대상이므로 comment-stripped 코드에서만 서명을 찾는다.
    code = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
    # 측정 assertion (a): spawn-event row-writer CLI 의 argv 서명 부재 (row-write 호출 0)
    row_write_flags = ("--spawn-seq", "--story-key", "--lane-label", "--attribution-confidence")
    present = [f for f in row_write_flags if f in code]
    assert not present, (
        f"hooks/subagent-stop 실행부에 spawn-event row-write argv 서명 {present} 등장 — "
        "single-writer(Orchestrator) 위반 (row-write 부활)"
    )
    # (b): retire 명문 marker 존재
    assert "RETIRED" in text, "spawn-event row-write RETIRE marker 부재 (single-writer 근거 소실)"
    # (c): 경량 disjoint COUNTER 는 보존(crash-safe 분모) — spawn-completion.count append
    assert "spawn-completion.count" in text, (
        "retire 후 경량 spawn-completion COUNTER(disjoint 채널) 가 보존돼야 함(F-B reconcile 분모)"
    )


def test_ac12_deterministic_event_id_within_path_dedup(tmp_path, run_append, read_rows):
    """deterministic event_id → within-path 재append dedup(read-time first-wins).

    동일 (session_id, agent_id, spawn_seq) → 동일 event_id → 재시도/이중 append 여도
    recorded COUNT(read-time dedup)는 1 로 collapse(at-least-once idempotent, §11.6).
    """
    # (a) 순수 함수 결정성 핀: 동일 입력 → 동일 event_id (random UUID 금지)
    e1 = append_spawn_event._compute_event_id("sh", "ah", "1")
    e2 = append_spawn_event._compute_event_id("sh", "ah", "1")
    e_diff = append_spawn_event._compute_event_id("sh", "ah", "2")
    # 측정 assertion: 동일 입력 event_id 동일, spawn_seq 다르면 상이
    assert e1 == e2, "동일 (session,agent,seq) → 동일 event_id (deterministic, InfraOpArch §11.6)"
    assert e1 != e_diff, "spawn_seq 다르면 event_id 상이 (within-path 구분)"

    # (b) within-path dedup: 동일 identity 2회 + distinct 1회 → 물리 3행, recorded 2
    ledger = tmp_path / "spawn-event.jsonl"
    for _ in range(2):  # 동일 identity 재append (dup event_id) — opt-in ON regime 명시
        run_append(
            ledger, opt_in=True, story_key="CFP-2850", lane_label="구현",
            agent_type="DeveloperAgent",
            session_id="sess-dup", agent_id="agent-dup", spawn_seq="7",
        )
    run_append(  # distinct identity (별 event_id)
        ledger, opt_in=True, story_key="CFP-2850", lane_label="구현",
        agent_type="DeveloperAgent",
        session_id="sess-dup", agent_id="agent-distinct", spawn_seq="8",
    )
    physical = read_rows(ledger)
    assert len(physical) == 3, f"물리 append 3행 기대(dedup 前), got {len(physical)}"
    # 측정 assertion: production read-time dedup → recorded 2 (dup event_id collapse)
    recorded = recon.count_recorded_rows(str(ledger))
    assert recorded == 2, (
        f"deterministic event_id read-time dedup → recorded 2 이어야 함(3 물리행 中 dup 1 collapse), "
        f"got {recorded}"
    )


def test_ac12_no_double_count_after_retire(tmp_path, run_append):
    """(reg) retire 후 hook∥Orchestrator 이중계산 0.

    완료 1건: Orchestrator single-writer 가 spawn-event row 1 append + hook 이 disjoint
    COUNTER 1 line append. hook 은 spawn-event row 를 더 이상 안 쓰므로 recorded=1(2 아님).
    mutation: hook 이 spawn-event row 도 쓰면 recorded=2 → gap!=0 → 이 reg RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    count_path = tmp_path / "spawn-completion.count"
    # Orchestrator single-writer: 완료 1건 → spawn-event row 1 (opt-in ON regime 명시 — ⑤)
    run_append(
        ledger, opt_in=True, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-nodouble", agent_id="agent-nodouble", spawn_seq="1",
    )
    # hook disjoint COUNTER: 동일 완료 1건 → count line 1 (opt-in ON 이므로 counter 발화)
    count_path.write_text("2026-07-28T01:00:00Z\n", encoding="utf-8")

    result = recon.reconcile(str(count_path), str(ledger))
    # 측정 assertion: recorded=1 (hook 이 spawn-event row 이중 append 안 함 — retire)
    assert result["recorded_row_count"] == 1, (
        f"완료 1건 → recorded 1 이어야 함(hook 이중 write 부활 시 2 → RED), got {result['recorded_row_count']}"
    )
    assert result["hook_completion_count"] == 1
    # gap 0(aligned) — 이중계산 0
    assert result["gap"] == 0 and result["status"] == "aligned", (
        f"retire 후 이중계산 0(gap 0 aligned)이어야 함, got {result}"
    )


def test_ac12_count_reconcile_hook_counter_vs_recorded_gap_visible(tmp_path, run_append):
    """(disc — F-B) hook COUNTER > recorded row COUNT → survivorship gap 가시.

    counter 3 completions, recorded 1 → gap 2 가 reconcile 출력에 VISIBLE(gap_observed).
    discriminating: gap 을 은닉(recorded==counter 로 위장)하면 status aligned 로 뒤집혀 RED.

    subprocess fork — exit code(record-only exit 0) 단독 판정 금지 → stdout JSON
    sentinel(status/gap) 병행 assert (distinct-marker 규율).
    """
    ledger = tmp_path / "spawn-event.jsonl"
    count_path = tmp_path / "spawn-completion.count"
    # hook COUNTER = 3 completions (opt-in ON regime — crash·notification-loss 포함 계수)
    count_path.write_text("t1\nt2\nt3\n", encoding="utf-8")
    # recorded = 1 spawn-event row (Orchestrator single-writer 가 2건 놓침 = survivorship)
    run_append(
        ledger, opt_in=True, story_key="CFP-2850", lane_label="구현", agent_type="DeveloperAgent",
        session_id="sess-gap", agent_id="agent-gap", spawn_seq="1",
    )

    returncode, parsed = _run_reconcile_cli(count_path, ledger)
    # distinct-marker: 도메인 sentinel(status/gap) 병행 assert — exit code 단독 판정 금지
    assert parsed is not None, "reconcile --json stdout 파싱 실패 (fork 미발생 or 형상 붕괴)"
    # 측정 assertion (primary sentinel): gap 2 가 VISIBLE + status gap_observed
    assert parsed["status"] == "gap_observed", (
        f"counter(3) > recorded(1) → gap_observed 여야 함(gap 은닉 시 aligned 로 뒤집혀 RED), "
        f"got status={parsed.get('status')!r}"
    )
    assert parsed["gap"] == 2, (
        f"survivorship gap = 3-1 = 2 가 VISIBLE 이어야 함, got gap={parsed.get('gap')!r}"
    )
    assert parsed["hook_completion_count"] == 3 and parsed["recorded_row_count"] == 1
    # secondary: record-only → exit 0 (gate 아님, INV-5). gap 은 관측치이지 실패 판정 아님.
    assert returncode == 0, f"reconcile 은 record-only exit 0(gate 아님)이어야 함, got {returncode}"


# ═══════════════ 보안 lane iter1 S-4 — reader 행분할 정책 통일 ═══════════════
#
# AC-12 는 "단일 writer + 이중계수 0" 을 지키지만, **읽는 쪽이 서로 다른 행분할 규칙**을 쓰면
# 같은 원장에서 서로 다른 row 수가 나온다. 정본 reader `replay._read_ledger` 는
# `str.splitlines()` 를 쓰는데, 파이썬의 `splitlines()` 는 `\n` 말고도 **U+0085(NEL) ·
# U+2028(LINE SEPARATOR) · U+2029(PARAGRAPH SEPARATOR)** 에서도 문자열을 쪼갠다. 반면
# `dedup_section14._read_ledger_rows` 의 `for line in f`(universal-newline)는 이 셋을 개행으로
# 보지 않는다. `agent_type` 에 그 문자가 하나 섞이면 — 에이전트 이름은 외부에서 흘러드는
# 값이다 — 그 행은 aggregate 쪽에서만 조각나 **JSON 파싱 실패로 통째 사라지고**, reconcile
# 쪽에서는 멀쩡히 세어진다. 결과: 사용자가 보는 집계에서 토큰이 조용히 증발하는데 **reconcile
# 의 gap 은 0** 이라 아무도 손실을 보지 못한다(자기 손실 관측 불가).
#
# 봉인 = **reader 행분할 `\n` 통일**. writer 측 문자 배제/정규화는 ArchitectPL 판정으로
# **기각**됐다(`json.dumps` 가 <0x20 제어문자를 이미 escape 하므로 분할 유발 문자는 이 셋뿐이고
# universal-newline 은 이 셋을 분할하지 않는다 → reader 통일만으로 완전 폐쇄. `ensure_ascii=True`
# 전환은 golden vector byte-exact 파손이라 금지). 따라서 본 절은 writer 동작에 대한 assert 를
# 두지 않는다.
#
# 배치 근거: 이 파일이 3 진입점 중 aggregate 를 한 번도 통과시키지 않은 것이 본 결함의 미탐지
# 원인이다 — 같은 자리에서 3 진입점을 모두 통과시켜 재발을 막는다.

# 행분할 후보 문자 (source 에는 escape 로 기재 — raw 문자 삽입은 편집 도구 왜곡 위험)
_LINE_SPLIT_CHARS = {
    "U+2028": "\u2028",
    "U+0085": "\u0085",
    "U+2029": "\u2029",
}


def _append_with_args_file(tmp_path, run_append, ledger, seq, agent_type, story_key, tokens):
    """UTF-8 args-file 채널로 1 row append (argv cp949 mangle 회피 — 계약상 실값 채널).

    session_id/spawn_seq 를 행마다 달리해 event_id 를 분리한다(read-time dedup 아티팩트 제거).
    """
    args_file = tmp_path / ("args-split-%d.json" % seq)
    args_file.write_text(
        json.dumps(
            {
                "story-key": story_key,
                "lane-label": "구현",
                "agent-type": agent_type,
                "session-id": "sess-split-%d" % seq,
                "agent-id": "agent-split-%d" % seq,
                "spawn-seq": str(seq),
                "total-tokens": tokens,
                "attribution-confidence": "attributed",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    res = run_append(ledger, opt_in=True, args_file=str(args_file))
    assert res.returncode == 0, f"append exit {res.returncode}: {res.stderr}"
    return res


def _build_split_char_ledger(tmp_path, run_append):
    """정상 2행 + 행분할 후보 문자를 실은 3행 = 논리 5행 원장."""
    ledger = tmp_path / "spawn-event.jsonl"
    rows = [
        (1, "clean-agent-1", 50000),
        (2, "evil\u2028agent", 90000),
        (3, "e2\u0085x", 90000),
        (4, "e3\u2029x", 90000),
        (5, "clean-agent-2", 40000),
    ]
    for seq, agent_type, tokens in rows:
        _append_with_args_file(
            tmp_path, run_append, ledger, seq, agent_type, "CFP-2850", tokens
        )
    return ledger, rows


def test_ac12_reader_row_count_parity_across_three_entry_points(tmp_path, run_append):
    """(disc) `agent_type` 에 U+2028/U+0085/U+2029 가 섞여도 **3 진입점 row 계수가 동일**.

    진입점: `replay._read_ledger` / `aggregate.load_rows` / `recon.count_recorded_rows`.
    discriminating: 셋 중 **하나만** `splitlines()` 행분할로 되돌려도 계수가 갈려 RED.
    """
    ledger, logical_rows = _build_split_char_ledger(tmp_path, run_append)
    expected = len(logical_rows)

    # fixture 실재 확인(vacuous 방지): 문제 문자가 원장 raw 에 실제로 존재한다.
    # writer 정규화는 ArchitectPL 판정으로 기각 → 이 문자들은 원장에 그대로 남는 것이 정상.
    raw = ledger.read_bytes()
    for name, ch in _LINE_SPLIT_CHARS.items():
        assert ch.encode("utf-8") in raw, (
            f"{name} 가 원장 raw 에 부재 — 결함 형상이 재현되지 않음(vacuous). "
            f"writer 측 정규화가 들어왔다면 ArchitectPL 판정(writer 방어 기각) 위반이다."
        )
    # writer 가 append 한 물리 개행 수 = 논리 row 수 (원장 자체는 정상 — 문제는 읽는 쪽)
    lf_count = raw.count(b"\n")
    assert lf_count == expected, f"writer LF 수 {lf_count} != 논리 row {expected}"

    n_replay = len(replay._read_ledger(Path(ledger)))
    n_aggregate = len(agg.load_rows(str(ledger)))
    n_reconcile = recon.count_recorded_rows(str(ledger))

    # 측정 assertion (a): 3 진입점 모두 논리 row 수와 일치
    assert (n_replay, n_aggregate, n_reconcile) == (expected, expected, expected), (
        f"reader 행분할 정책 불일치 — replay={n_replay} / aggregate={n_aggregate} / "
        f"reconcile={n_reconcile} (논리 row {expected}). splitlines() 계열 reader 가 "
        f"U+2028/U+0085/U+2029 를 개행으로 보아 행을 조각내고 있다."
    )

    # (b): 집계 실값(total_tokens)도 진입점 간 동일 — 은닉된 토큰 0
    expected_tokens = sum(r[2] for r in logical_rows)
    tok_replay = sum(r.get("total_tokens") or 0 for r in replay._read_ledger(Path(ledger)))
    tok_aggregate = sum(r.get("total_tokens") or 0 for r in agg.load_rows(str(ledger)))
    assert tok_replay == tok_aggregate == expected_tokens, (
        f"진입점별 total_tokens 발산 — replay={tok_replay} / aggregate={tok_aggregate} "
        f"(실제 {expected_tokens}). 사용자가 보는 집계에서 토큰이 조용히 증발한다."
    )


def test_ac12_reconcile_cannot_hide_reader_divergence(tmp_path, run_append):
    """(disc) reader 가 갈리면 reconcile 은 **자기 손실을 볼 수 없다** — 그 무음을 차단.

    hook COUNTER 5 = recorded 5 → reconcile 은 `aligned`(gap 0)를 보고한다. 그런데 aggregate
    쪽이 splitlines 로 3행을 잃으면 사용자 집계만 2행이 된다 — reconcile 은 이 손실을
    구조적으로 감지하지 못한다(자기가 쓰는 reader 로는 5행이 멀쩡히 보이므로). 따라서
    "gap 0" 은 **aggregate 계수가 같을 때에만** 정직하다. 두 조건을 함께 고정한다.
    """
    ledger, logical_rows = _build_split_char_ledger(tmp_path, run_append)
    count_path = tmp_path / "spawn-completion.count"
    count_path.write_text("\n".join(["1"] * len(logical_rows)) + "\n", encoding="utf-8")

    returncode, parsed = _run_reconcile_cli(count_path, ledger)
    assert parsed is not None, "reconcile --json stdout 파싱 실패 (fork 미발생 or 형상 붕괴)"
    assert returncode == 0, f"reconcile 은 record-only exit 0 이어야 함, got {returncode}"

    # 측정 assertion (a): reconcile 은 gap 0 aligned 를 보고한다 (전제)
    assert parsed["status"] == "aligned" and parsed["gap"] == 0, (
        f"완료 {len(logical_rows)}건 = recorded {len(logical_rows)}건 이어야 함, got {parsed}"
    )
    # (b): 그 'aligned' 가 정직하려면 aggregate 계수도 같아야 한다 — 무음 손실 차단
    n_aggregate = len(agg.load_rows(str(ledger)))
    assert n_aggregate == parsed["recorded_row_count"], (
        f"reconcile 은 aligned(recorded={parsed['recorded_row_count']}) 인데 aggregate 는 "
        f"{n_aggregate}행만 본다 — reconcile 이 감지하지 못하는 무음 손실 "
        f"{parsed['recorded_row_count'] - n_aggregate}행."
    )


def test_ac12_reader_survives_undecodable_bytes(tmp_path, run_append):
    """(disc) 깨진 바이트가 섞인 원장에서도 3 진입점이 **crash 없이** 정상 행을 읽는다.

    정본 reader 들은 `encoding="utf-8"` 을 `except OSError` 로만 감쌌다 — 디코드 불가 바이트가
    한 줄만 섞여도 `UnicodeDecodeError`(ValueError 계열)가 잡히지 않고 튀어나가 reader 전체가
    죽는다(부분 손실이 아니라 전면 정지). `errors="replace"` 로 통일하면 깨진 줄만 JSON 파싱
    실패로 skip 되고 나머지는 살아남는다.
    discriminating: `errors="replace"` 를 빼면 UnicodeDecodeError 로 RED.
    """
    ledger = tmp_path / "spawn-event.jsonl"
    _append_with_args_file(tmp_path, run_append, ledger, 1, "clean-a", "CFP-2850", 1000)
    # 디코드 불가 바이트 라인 삽입 (JSON 으로도 성립하지 않는 형상)
    with open(ledger, "ab") as fh:
        fh.write(b"\xff\xfe not-json\n")
    _append_with_args_file(tmp_path, run_append, ledger, 2, "clean-b", "CFP-2850", 2000)

    # fixture 실재 확인: 깨진 바이트가 실제로 원장에 있다
    assert b"\xff\xfe" in ledger.read_bytes(), "깨진 바이트 fixture 미착지(vacuous)"

    # 측정 assertion: 예외 전파 없이 정상 2행만 반환 (깨진 줄은 skip)
    n_replay = len(replay._read_ledger(Path(ledger)))
    n_aggregate = len(agg.load_rows(str(ledger)))
    n_reconcile = recon.count_recorded_rows(str(ledger))
    assert (n_replay, n_aggregate, n_reconcile) == (2, 2, 2), (
        f"깨진 바이트 1줄에 reader 계수가 흔들림 — replay={n_replay} / "
        f"aggregate={n_aggregate} / reconcile={n_reconcile} (정상 행 2)"
    )
