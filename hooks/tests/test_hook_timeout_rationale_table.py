#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S3 (테스트): Hook timeout rationale table AC-4, AC-16.

목적:
  28개 hook × timeout 값 × empirical_source (Change Plan §3.2 verbatim) bijection 검증.

AC-4: 테스트 내 rationale 표 (28행) ↔ hooks.json bijection 확인.
AC-16: fail-open 계상 3항 (게이트 4종 fail-open / 내부 subprocess 하한 / SessionEnd 특례)
        이 표에 필드로 실재.

AC-16 판정 정의역 = **행** (CFP-2965 F5-1):
  구 판정은 표 전체 연결 문자열에 대한 `A or B` 단락 평가라 게이트별 누락을 못 잡았고
  (#2 는 assert 없는 dead var 였다), 게이트 4종이 모두 무계상이어도 통과했다.
  현재는 게이트 4종을 행 단위로 각각 판정하고, #2 는 표의 선언값을 실물 상수
  (git_branch_delete_merge_gate.GH_TOTAL_BUDGET_SEC) 와 대조한다.

세부:
  - hooks.json 의 25개 hook 별로 timeout 값 + empirical_source 기술
  - source 는 "Change Plan §3.2 설명" 형태로 명시
  - bijection: hooks.json 의 hook 개수 = table 행 수 (25)
  - 전 행 empirical_source 비어있지 않음 (non-empty)
  - AC-16 체계: 테이블에 위 3항 필드 포함하여 계상

테이블 행 구조:
  hook_name | timeout_sec | empirical_source (or AC-16 category)
"""

from __future__ import annotations

import json
import re
import pytest
from pathlib import Path


# ==============================================================================
# S3 (테스트): Hook timeout rationale table (AC-4, AC-16)
# ==============================================================================

# 변경 전 행동 특성화: hooks.json 의 25개 hook 별 timeout 근거 표
# (Change Plan §3.2 verbatim 요약 + AC-16 3항 계상)
TIMEOUT_RATIONALE_TABLE = [
    # SessionStart
    (
        "session-start",
        10,
        "§3.2 SessionStart anchor: local worktree init + temp file write ≤10s (현행 실측)",
    ),
    (
        "stale-local-main-checkout",
        30,
        "§3.2 SessionStart #1: git fetch origin/main + stale check (network 30s cap)",
    ),
    (
        "stray-scratch-leak",
        10,
        "§3.2 SessionStart #2: home-root leak scan (filesystem scan ≤10s)",
    ),
    (
        "session-start-gc-catchup",
        30,
        "§3.2 SessionStart #3: orphan worktree cleanup (file ops 30s cap)",
    ),
    (
        "session-start-scheduled-task-watchdog",
        10,
        "§3.2 SessionStart #4: 로컬 스케줄 작업 표식 스캔 — stray-scratch-leak 과 "
        "동일 범주(읽기전용 filesystem scan ≤10s, network 미접촉)라 같은 10s 예산. "
        "작업량 bound = -maxdepth 3 · 최대 200 파일 · grep -F(고정 문자열). "
        "실측 0.364~0.666s (5회, rc=0) — 10s 예산 대비 약 15~27배 여유",
    ),
    # PreToolUse Bash (5개)
    # ↓ 게이트 4종은 AC-16 #1 fail-open 손실을 행 자체에 계상한다 (표 밖 산문 아님).
    (
        "cross-repo-gh-safety",
        10,
        "§3.2 PreToolUse cross-repo gate: regex+deny 로직 (no network, ≤10s). "
        "AC-16 #1 fail-open 계상: timeout 초과 = 훅 kill → deny 미발화 → 통과 수렴 "
        "(차단 손실 = cross-repo gh 오작동 유입, 흔적 0)",
    ),
    (
        "repo-confinement",
        10,
        "§3.2 PreToolUse repo confine gate: path check + deny (≤10s local). "
        "AC-16 #1 fail-open 계상: timeout 초과 = 훅 kill → deny 미발화 → 통과 수렴 "
        "(차단 손실 = repo 경계 밖 write 유입, 흔적 0)",
    ),
    (
        "git-branch-delete-merge-gate",
        60,
        "§3.2 PreToolUse gh-query gate: PR list 조회 (GH_TOTAL_BUDGET_SEC=50 + margin). "
        "AC-16 #1 fail-open 계상: gh 부재·오류·JSON 파싱 실패·예산 소진·timeout kill 이 "
        "전부 통과 수렴 (차단 손실 = 미머지 PR branch 선삭제 유입). "
        "AC-16 #2 내부 subprocess 하한: GH_TOTAL_BUDGET_SEC=50 < timeout 60 — "
        "'죽어서 통과'(kill, 흔적 0) 를 '돌아서 통과'(진단 stderr, 흔적 有) 로 전환",
    ),
    (
        "worktree-location-guard",
        15,
        "§3.2 PreToolUse worktree guard: standard path check + deny (≤15s). "
        "AC-16 #1 fail-open 계상: timeout 초과 = 훅 kill → deny 미발화 → 통과 수렴 "
        "(차단 손실 = 표준 밖 worktree 생성 유입, 흔적 0)",
    ),
    (
        "pretooluse-bash-description-inject",
        5,
        "§3.2 PreToolUse sed transform: description 주입 (≤5s regex)",
    ),
    # PreToolUse ScheduleWakeup
    (
        "schedule-wakeup-reminder",
        10,
        "§3.2 PreToolUse schedule hook: message format (≤10s)",
    ),
    # PreToolUse Agent
    (
        "pretooluse-agent-spawn-gate",
        10,
        "§3.2 PreToolUse agent gate: subject sanitize + render (≤10s)",
    ),
    # PreToolUse Write|Edit|MultiEdit
    (
        "pretooluse-inline-write-gate",
        10,
        "§3.2 PreToolUse inline write gate: regex + deny (≤10s)",
    ),
    # PreToolUse Agent|Bash|Write|Edit|MultiEdit (복합 matcher)
    (
        "pretooluse-dev-process-capture",
        5,
        "§3.2 PreToolUse capture wrapper: JSON serialize + payload cap (≤5s)",
    ),
    # PostToolUse Bash|Write|Edit|MultiEdit
    (
        "posttooluse-dev-process-capture",
        5,
        "§3.2 PostToolUse capture wrapper: payload append + audit (≤5s)",
    ),
    # UserPromptSubmit (6개)
    (
        "korean-english-recovery",
        10,
        "§3.2 UserPromptSubmit recovery: layout detection (≤10s)",
    ),
    (
        "bootstrap-first-gate",
        10,
        "§3.2 UserPromptSubmit bootstrap: fork detection (<=10s)",
    ),
    (
        "skip-offer-reminder",
        10,
        "§3.2 UserPromptSubmit reminder: cached LAST_SKIP check (≤10s)",
    ),
    (
        "deferred-recovery-reminder",
        10,
        "§3.2 UserPromptSubmit deferred check: tool resolver cache (≤10s)",
    ),
    (
        "story-transition-autonomy-reminder",
        10,
        "§3.2 UserPromptSubmit story gate: JSON payload validation (≤10s)",
    ),
    (
        "session-swap-handoff-reminder",
        10,
        "§3.2 UserPromptSubmit handoff: context preparation (≤10s)",
    ),
    # Stop
    ("stop", 10, "§3.2 Stop: cleanup message (≤10s)"),
    # StopFailure (CFP-2967 — 신규 이벤트)
    (
        "stopfailure-429-incident-record",
        5,
        "§3.2 StopFailure 429 기록 (CFP-2967): entry 0 인 **신규 이벤트**라 기존 예산 기여 0. "
        "공식 문서 verbatim \"All matching hooks run in parallel.\" ⇒ 이벤트별 wall = "
        "**max, not Σ**. 발화 빈도 = 정상 턴 **0회**(턴 사망 시에만). 작업량 = stdin "
        "drain-and-discard + Python 1회 fork + 상수 1행 append(원장 read 0, payload 파싱 0). "
        "**record-only** — 출력·exit code 가 소비되지 않아 구조적으로 게이트가 아니며, "
        "만료의 실손실은 '차단 실패'가 아니라 **미기록 incident 1건**이다. "
        "만료 확률 절대값은 **미측정 — declare**(추정치 기재 금지)",
    ),
    # SessionEnd (AC-16 특례: async timeout 1)
    (
        "session-end",
        1,
        "§3.2 SessionEnd special (AC-16 #3): async timeout (fire-and-forget, 1s cap)",
    ),
    # SubagentStart
    (
        "subagent-start-render-discipline",
        10,
        "§3.2 SubagentStart render: subject/time injection (≤10s)",
    ),
    (
        "subagent-start-progress-commit-priming",
        10,
        "§3.2 SubagentStart priming: pointer-only additionalContext emit (정적 3줄 규범 pointer — "
        "filesystem/network touch 0, git 조작 0, JSON parse 후 stdout 1건), fail-open exit 0 (≤10s)",
    ),
    (
        "subagent-start-429-lease",
        5,
        "§3.2 SubagentStart 429 lease (CFP-2967): lease 파일 1건 생성만 수행 — host-local "
        "`.claude/ledger/**` 고정, network 0 · git 조작 0 · repo walk 0 이라 sibling "
        "render-discipline(10s)보다 작업량이 구조적으로 작다. 같은 이벤트의 형제 훅과 "
        "**병렬 실행**되므로 이벤트 wall = max(Σ 아님) 이며 5s 는 현 max(10s)를 올리지 않는다. "
        "record-only 관측 — 만료의 실손실 = lease 1건 미기록이고, 설계가 증감 쌍이 아니라 "
        "**만료 기반 reconcile** 이라 유실이 상한을 영구 잠그지 않는다(`stop_without_lease` 로 흡수). "
        "만료 확률 절대값은 **미측정 — declare**",
    ),
    # SubagentStop
    (
        "subagent-stop",
        10,
        "§3.2 SubagentStop: cleanup (≤10s)",
    ),
]


# AC-16 #1 정의역 — PreToolUse deny 게이트 4종 (fail-open 손실 계상 대상).
# 이 목록의 임의 축소는 test_ac16_fail_open_gate_set_matches_bypass_gates 가 잡는다.
FAIL_OPEN_GATES = (
    "cross-repo-gh-safety",
    "repo-confinement",
    "git-branch-delete-merge-gate",
    "worktree-location-guard",
)


def _load_hooks_json() -> dict:
    """hooks.json 로드."""
    hooks_path = Path(__file__).parent.parent / "hooks.json"
    with open(hooks_path) as f:
        return json.load(f)


def _extract_hooks_from_json() -> list[tuple[str, int, str]]:
    """hooks.json 에서 (hook_name, timeout, '') 튜플 리스트 추출 (삽입 순서)."""
    hooks_data = _load_hooks_json()
    result = []

    for event_name, matchers in hooks_data["hooks"].items():
        if not isinstance(matchers, list):
            continue

        for matcher_entry in matchers:
            hooks_list = matcher_entry.get("hooks", [])
            for hook in hooks_list:
                cmd = hook.get("command", "")
                timeout = hook.get("timeout")

                # Extract hook name from command
                if "/" in cmd:
                    parts = cmd.split()
                    if len(parts) >= 2:
                        hook_name = parts[-1]
                    else:
                        hook_name = cmd
                else:
                    hook_name = cmd

                if timeout is not None:
                    result.append((hook_name, timeout, ""))

    return result


def test_hook_timeout_rationale_bijection():
    """AC-4: rationale table ↔ hooks.json bijection."""
    json_hooks = _extract_hooks_from_json()
    table_hooks = TIMEOUT_RATIONALE_TABLE

    # 개수 일치
    assert len(json_hooks) == len(table_hooks), (
        f"Count mismatch: json={len(json_hooks)}, table={len(table_hooks)}"
    )

    # 순서 + 값 일치 (ordered bijection)
    for i, ((json_name, json_timeout, _), (table_name, table_timeout, table_source)) in enumerate(
        zip(json_hooks, table_hooks)
    ):
        assert json_name == table_name, (
            f"Row {i}: hook name mismatch: json={json_name}, table={table_name}"
        )
        assert json_timeout == table_timeout, (
            f"Row {i} ({json_name}): timeout mismatch: json={json_timeout}, table={table_timeout}"
        )


def test_hook_timeout_rationale_all_nonempty():
    """AC-4: 전 행의 empirical_source 필드가 non-empty."""
    for hook_name, timeout, source in TIMEOUT_RATIONALE_TABLE:
        assert source, (
            f"Hook {hook_name} has empty empirical_source (AC-4 violation)"
        )
        assert isinstance(source, str) and len(source) > 0


def _row(hook_name: str) -> tuple[str, int, str]:
    """rationale 표에서 hook 행 1건 조회 (부재 = FAIL)."""
    for row in TIMEOUT_RATIONALE_TABLE:
        if row[0] == hook_name:
            return row
    raise AssertionError(f"rationale 표에 '{hook_name}' 행이 없다")


@pytest.mark.parametrize("gate_name", FAIL_OPEN_GATES)
def test_ac16_fail_open_accounted_per_gate(gate_name: str):
    """AC-16 #1: 게이트 4종 **각 행**이 fail-open 손실을 계상한다.

    구 판정은 표 전체를 이어붙인 뒤 `"fail-open" in text or "AC-16" in text` 로
    단락 평가했다 — 표 어딘가에 "AC-16" 한 글자만 있으면(예: SessionEnd 특례 행)
    게이트 4종이 전부 무계상이어도 통과한다. 즉 정의역이 "표 전체"라 게이트별
    누락을 원리적으로 검출하지 못했다. 여기서 정의역을 **행**으로 좁힌다.
    """
    _name, _timeout, source = _row(gate_name)

    assert "AC-16 #1" in source, (
        f"{gate_name}: AC-16 #1 fail-open 계상 태그 부재 — 행 자체에 계상되어야 한다.\n"
        f"현재 source: {source}"
    )
    assert "fail-open" in source.lower(), (
        f"{gate_name}: 'fail-open' 표기 부재 (source: {source})"
    )
    assert "손실" in source, (
        f"{gate_name}: 손실 계상(무엇이 통과로 새는가) 부재 — "
        f"'fail-open 이다'만 적고 대가를 안 적으면 계상이 아니다. (source: {source})"
    )


def test_ac16_fail_open_gate_set_matches_bypass_gates():
    """AC-16 #1 정의역 고정: 게이트 4종 목록이 bypass disjoint 축과 동일.

    FAIL_OPEN_GATES 를 임의로 줄이면(예: branch-gate 제외) 위 per-gate 테스트가
    조용히 축소된다. 독립 SSOT(bypass env 축)와 대조해 그 축소를 검출한다.

    출처: 구 코드는 `from test_bypass_env_disjoint import BYPASS_ENVS` 로 **테스트
    모듈**을 import 했다 — 테스트 모듈명은 수집 구성에 따라 해석이 흔들리는 표면이라
    (CR-201: overlay conftest 선점 사례) 인프라 심볼 출처로 부적합하다.
    고유명 모듈 `hook_runner_cfp2965` 를 공통 출처로 삼는다.
    """
    from hook_runner_cfp2965 import BYPASS_ENVS

    assert set(FAIL_OPEN_GATES) == set(BYPASS_ENVS.keys()), (
        f"게이트 4종 정의역 불일치: rationale={sorted(FAIL_OPEN_GATES)} "
        f"vs bypass축={sorted(BYPASS_ENVS.keys())}"
    )


def test_ac16_internal_subprocess_floor_accounted():
    """AC-16 #2: 내부 subprocess 하한이 계상 + **실물 상수와 정합**.

    구 코드는 `subprocess_haul_found` 를 세팅만 하고 assert 하지 않는 dead var 였다
    (어떤 표 내용이든 통과). 여기서는 표가 선언한 하한값을 실제 훅 모듈 상수와
    대조하고, 그 하한이 hooks.json timeout 미만인지(= timeout 이 hollow 가 아닌지)
    까지 판정한다.
    """
    import git_branch_delete_merge_gate as branch_gate

    hook_name, timeout, source = _row("git-branch-delete-merge-gate")

    assert "AC-16 #2" in source, f"AC-16 #2 내부 subprocess 하한 미계상 (source: {source})"

    m = re.search(r"GH_TOTAL_BUDGET_SEC=(\d+)", source)
    assert m, f"표에 GH_TOTAL_BUDGET_SEC=<값> 형태의 하한 선언 부재 (source: {source})"
    declared = int(m.group(1))

    assert declared == branch_gate.GH_TOTAL_BUDGET_SEC, (
        f"표가 선언한 하한({declared}) 이 실물 상수"
        f"({branch_gate.GH_TOTAL_BUDGET_SEC}) 와 불일치 — 표가 stale"
    )
    assert declared < timeout, (
        f"내부 subprocess 하한({declared}) 이 hook timeout({timeout}) 이상 — "
        f"timeout 이 hollow (예산 소진 진단 전에 kill 된다)"
    )


def test_ac16_session_end_special_case_documented():
    """AC-16 #3: SessionEnd async timeout 특례가 그 행에 명시."""
    _name, timeout, source = _row("session-end")

    assert "AC-16 #3" in source, f"AC-16 #3 태그 부재 (source: {source})"
    assert "async" in source.lower(), f"async 특례 표기 부재 (source: {source})"
    assert timeout == 1, f"SessionEnd 특례 timeout 은 1s (got {timeout})"


def test_hook_timeout_rationale_row_count_matches_pin():
    """Table 이 정확히 28행임을 확인.

    pin 갱신 이력: 26 → **28** (CFP-2967 Phase 2). 증분 +2 = `StopFailure`
    `stopfailure-429-incident-record` 1건 + `SubagentStart` `subagent-start-429-lease` 1건.
    ★ 이 값은 문서 문면에서 베끼지 않는다 — 정본은 명령이 낸다:
        python -c "import json,sys;d=json.load(sys.stdin);print(sum(1 for ev in d['hooks'].values() for m in ev for h in m.get('hooks',[]) if h.get('timeout') is not None))" < hooks/hooks.json
    (2026-08-19 실측 산출 = 28. pin 상수만 고치고 표 본체를 안 고치면
    test_hook_timeout_rationale_bijection 이 RED — 두 site 동시 갱신 의무.)
    """
    assert len(TIMEOUT_RATIONALE_TABLE) == 28, (
        f"Expected 28 rationale rows, got {len(TIMEOUT_RATIONALE_TABLE)}"
    )
    print(f"✓ Rationale table has complete 28 rows with bijection to hooks.json")
