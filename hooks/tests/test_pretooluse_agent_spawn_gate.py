"""test_pretooluse_agent_spawn_gate.py — CFP-2567 Phase 2 채널 2 Test Contract 이행 (TDD).

계약 SSOT:
  Story CFP-2567 §7.8 / ADR-071 §결정 22 §22.4 (Amendment 13) — D2 채널 2.
  PreToolUse(Agent) additionalContext non-block inject (autonomous 전환 창 — Story 존재 이유).
  기존 배선된 hooks/pretooluse-agent-spawn-gate(spawn-format 4-block warning gate) 확장:
  채널 2 helper scripts/lib/agent_spawn_transition_reminder.py 를 통해 전환 reminder 를
  stdout additionalContext 로 inject. **NEVER deny** (1차 출처 code.claude.com/docs/en/hooks) —
  4-block warning gate 는 Wave1 항상 exit 0 무손상.

두 층:
  (A) in-process helper 단위 — agent_spawn_transition_reminder 모듈 직접 import.
      전 플랫폼(Windows 포함) 실행. json.loads 후 key-path parse + NEVER deny.
  (B) subprocess 통합 — bash 로 실제 gate 스크립트 fork.
      기존 4-block warning 회귀 무손상 확인. CI ubuntu 실행, Windows skip
      (precedent = test_pretooluse_inline_write_gate.py subprocess 패턴).

anti-theater 규칙 (mutation 생존 0):
  - exit code 단독 판정 금지 — additionalContext 마커 substring(json.loads 후) 병행 assert.
  - NEVER deny 는 permissionDecision != "deny" 로 falsify (deny 이면 FAIL).
  - subprocess: 4-block warning 마커 존재/부재로 회귀 무손상 판별(편측 누락 차단).

TDD red→green 순서: 병렬 DeveloperAgent 가 (i) scripts/lib/agent_spawn_transition_reminder.py
production + (ii) hooks/pretooluse-agent-spawn-gate 채널 2 emit 삽입을 완료하기 전(pre-GREEN)
에는 conftest import 실패 또는 subprocess stdout 부재로 fail 이 정상.
"""

from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import agent_spawn_transition_reminder as astr


# worktree root = tests/ → hooks/ → root
WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent

# 채널 2 계약 exact strings (spawn packet §계약)
TRANSITION_MARKER = "story-transition-autonomy"  # _build_context 마커 substring
GATE_WARNING_MARKER = "[codeforge-wrapper-pretooluse-agent-gate]"  # 기존 4-block warning 마커
GATE_SCRIPT = WORKTREE_ROOT / "hooks" / "pretooluse-agent-spawn-gate"

# 채널2 _build_context 정당 멈춤 3종 carve-out — 실측 exact string (production 무수정 lock).
# 주의: 채널1 _build_reminder 는 ① 을 "요구 자체가 애매" 로 쓰지만, 채널2 _build_context 는
# 더 짧은 "요구 애매" 를 쓴다(scripts/lib/agent_spawn_transition_reminder.py:83 실측). 각 채널
# 테스트는 자기 채널 production 이 실제로 방출하는 문자열을 lock 한다(F-CR-CLAUDE-001 P2 대칭).
CARVEOUT_AMBIGUOUS = "요구 애매"            # 채널2 ① (채널1 = "요구 자체가 애매")
CARVEOUT_TRADEOFF = "진짜 가치 trade-off"    # 채널2 ② (채널1 동일)
CARVEOUT_IRREVERSIBLE = "비가역·고비용"       # 채널2 ③ (채널1 동일)


def _call_main_rc(mod) -> int:
    """main() 반환값 정규화 — return int 또는 sys.exit(code) 관례 모두 exit-0 invariant 로.

    채널 2 helper 계약 = main() 반환 0. 그러나 sibling(check_inline_write_gate)이
    sys.exit 관례를 쓰므로 cross-layer TDD 에서 Dev 가 어느 관례를 택하든 load-bearing
    invariant(NEVER non-zero exit)를 falsify 하도록 정규화.
    """
    try:
        rc = mod.main()
    except SystemExit as e:  # sys.exit(0) 관례
        rc = e.code if e.code is not None else 0
    return rc if rc is not None else 0


# ============================================================ (A-1) _extract_subagent_type 단위


def test_extract_subagent_type_present():
    """_extract_subagent_type: tool_input.subagent_type 존재 → 그 값 반환."""
    payload = {"tool_input": {"subagent_type": "RequirementsPLAgent"}}
    assert astr._extract_subagent_type(payload) == "RequirementsPLAgent"


def test_extract_subagent_type_key_absent():
    """_extract_subagent_type: subagent_type 키 부재 → '' (빈 문자열)."""
    assert astr._extract_subagent_type({"tool_input": {}}) == ""
    assert astr._extract_subagent_type({}) == ""


def test_extract_subagent_type_non_dict():
    """_extract_subagent_type: non-dict payload → '' (fail-open)."""
    assert astr._extract_subagent_type(None) == ""
    assert astr._extract_subagent_type("not a dict") == ""
    assert astr._extract_subagent_type(123) == ""
    assert astr._extract_subagent_type(["list"]) == ""


# ============================================================ (A-2) _is_lane_pl 단위


@pytest.mark.parametrize(
    "value,expected",
    [
        ("RequirementsPLAgent", True),   # lane PL — 전환 창 전형(Story k+1 lane-PL spawn)
        ("CodeReviewPLAgent", True),     # lane PL
        ("DeveloperAgent", False),       # 비-PL worker
        ("", False),                     # 빈 문자열
    ],
)
def test_is_lane_pl(value, expected):
    """_is_lane_pl: lane PL 판별 (전환 창 over-fire 완화용 subagent_type 판별)."""
    assert astr._is_lane_pl(value) is expected


# ============================================================ (A-3) _build_context 단위


def test_build_context_contract_pl():
    """_build_context(PL): 마커 + ADR-071 + over-halt + over-ask + 정당 멈춤 3종 개별 lock.

    F-CR-CLAUDE-001 [P2] hardening (구현리뷰 Claude peer): 채널1 INV-6 대칭 — 정당 멈춤
    3종을 개별 exact-substring assert 로 mutation-lock(묶음 OR 금지). _build_context 에서
    carve-out 하나 삭제하는 mutation 이 이 테스트를 생존하지 못하도록 한다.
    """
    ctx = astr._build_context("RequirementsPLAgent")
    assert TRANSITION_MARKER in ctx
    assert "ADR-071" in ctx
    assert "over-halt" in ctx
    assert "over-ask" in ctx
    # 정당 멈춤 3종 — 각각 개별 exact substring (mutation survival 방지, 채널1 INV-6 대칭)
    assert CARVEOUT_AMBIGUOUS in ctx, f"carve-out ① '{CARVEOUT_AMBIGUOUS}' 부재"
    assert CARVEOUT_TRADEOFF in ctx, f"carve-out ② '{CARVEOUT_TRADEOFF}' 부재"
    assert CARVEOUT_IRREVERSIBLE in ctx, f"carve-out ③ '{CARVEOUT_IRREVERSIBLE}' 부재"


@pytest.mark.parametrize("subagent_type", ["RequirementsPLAgent", "DeveloperAgent", ""])
def test_build_context_marker_all_variants(subagent_type):
    """_build_context: PL / 비-PL / 빈 문자열 모두 마커 inject (전환 창 누락 방지).

    subagent_type 판별로 text 가 달라져도 전환 마커는 항상 포함 — 전환 창을
    놓치지 않기 위함(§22.4 (e) 매 Agent spawn fire).
    """
    ctx = astr._build_context(subagent_type)
    assert TRANSITION_MARKER in ctx, f"marker 부재 (subagent_type={subagent_type!r})"


# ============================================================ (A-4) _emit 봉투 단위 (NEVER deny)


def test_emit_envelope_never_deny(capsys):
    """_emit: hookSpecificOutput 봉투 = PreToolUse + additionalContext + NEVER deny.

    permissionDecision 키는 부재(또는 최소한 != 'deny') — 채널 2 는 절대 차단하지 않는다.
    """
    astr._emit("hello-transition-ctx")
    out = capsys.readouterr().out.strip()
    obj = json.loads(out)  # plain stdout 면 여기서 JSONDecodeError → fail
    hso = obj["hookSpecificOutput"]
    assert hso["hookEventName"] == "PreToolUse"
    assert hso["additionalContext"] == "hello-transition-ctx"
    assert hso.get("permissionDecision", None) != "deny", (
        "NEVER deny 위반 — 채널 2 는 permissionDecision=deny 금지"
    )


# ============================================================ (A-5) main() execution — key-path parse


def _run_main_with_stdin(monkeypatch, capsys, payload_json: str):
    """stdin 주입 → main() 실행 → (rc, stripped_stdout) 반환."""
    monkeypatch.setattr("sys.stdin", io.StringIO(payload_json))
    rc = _call_main_rc(astr)
    out = capsys.readouterr().out.strip()
    return rc, out


@pytest.mark.parametrize(
    "subagent_type,label",
    [
        ("RequirementsPLAgent", "lane PL (전환 창 전형)"),
        ("DeveloperAgent", "비-PL worker (전환 창 누락 방지)"),
        (None, "subagent_type 부재 (전환 창 누락 방지)"),
    ],
)
def test_main_injects_marker_and_never_deny(subagent_type, label, monkeypatch, capsys):
    """main(): well-formed Agent payload → additionalContext 마커 inject + NEVER deny + exit 0.

    key-path parse: obj["hookSpecificOutput"]["additionalContext"] 순회(substring assert 금지).
    PL / 비-PL / subagent_type 부재 모두 마커 inject + exit 0 (전환 창 누락 방지, §22.4 (e)).
    """
    tool_input = {"prompt": "일부만 있는 spawn prompt"}
    if subagent_type is not None:
        tool_input["subagent_type"] = subagent_type
    payload = {"tool_name": "Agent", "tool_input": tool_input}

    rc, out = _run_main_with_stdin(monkeypatch, capsys, json.dumps(payload, ensure_ascii=False))

    assert rc == 0, f"{label}: exit 0 위반 (rc={rc})"
    assert out != "", f"{label}: 무발화 (전환 창 누락)"
    obj = json.loads(out)  # key-path parse
    hso = obj["hookSpecificOutput"]
    assert hso["hookEventName"] == "PreToolUse", f"{label}: hookEventName 위반"
    assert TRANSITION_MARKER in hso["additionalContext"], f"{label}: 전환 마커 미inject"
    # NEVER deny — 부재/allow 만 허용, deny 이면 FAIL
    assert hso.get("permissionDecision", None) != "deny", f"{label}: NEVER deny 위반"


@pytest.mark.parametrize(
    "stdin_text,label",
    [
        ("", "빈 stdin"),
        ("   \n\t ", "공백 only stdin"),
        ('{"tool_input":', "malformed JSON"),
    ],
)
def test_main_fail_open_exit_zero(stdin_text, label, monkeypatch, capsys):
    """main(): 빈/malformed stdin → exit 0 (fail-open), 발화 시에도 NEVER deny.

    fail-open 은 무발화 허용(전환 창 판별 불가) — 그러나 어떤 경우에도 exit non-zero
    또는 deny 금지.
    """
    rc, out = _run_main_with_stdin(monkeypatch, capsys, stdin_text)
    assert rc == 0, f"{label}: fail-open exit 0 위반 (rc={rc})"
    # 발화했다면 deny 금지 (무발화면 skip)
    if out:
        obj = json.loads(out)
        assert obj.get("hookSpecificOutput", {}).get("permissionDecision", None) != "deny", (
            f"{label}: fail-open 경로에서도 NEVER deny"
        )


# ============================================================ (B) subprocess 통합 (4-block 회귀 무손상)


def _skip_if_no_bash():
    """bash 부재 또는 Windows → subprocess 통합 skip (precedent 정합)."""
    if shutil.which("bash") is None:
        pytest.skip("bash not found in PATH")
    if sys.platform == "win32":
        pytest.skip("subprocess bash tests skipped on Windows (WSL path resolution)")
    if not GATE_SCRIPT.exists():
        pytest.skip(f"gate script not found: {GATE_SCRIPT}")


# 4-block 모두 포함한 prompt (verifier check_spawn_prompt_format.py 매칭 규칙 정합):
#   블록1: [PRE-SPAWN-ORIGIN-MAIN-SHA] : <7~40 hex>
#   블록2: [USER-UTTERANCE-VERBATIM] 는 반드시 단독 line (trailing whitespace 만 허용)
#   블록3: "worktree" 포함 line
#   블록4: "parallel" + "dispatch" 같은 line
_PROMPT_ALL_BLOCKS = "\n".join(
    [
        "[PRE-SPAWN-ORIGIN-MAIN-SHA] : 9ad4760272e105e2423090933c0092a8a15adebb",
        "[USER-UTTERANCE-VERBATIM]",
        "worktree-first directive: work only in this worktree",
        "parallel-dispatch directive: you run in parallel with a dispatch sibling",
    ]
)


def _run_gate_subprocess(prompt_text: str):
    """gate 스크립트를 bash 로 fork — Agent spawn payload(prompt) 주입 후 결과 반환."""
    payload = {
        "tool_name": "Agent",
        "tool_input": {
            "subagent_type": "RequirementsPLAgent",
            "prompt": prompt_text,
        },
    }
    env = os.environ.copy()
    env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)  # verifier + 채널 2 helper 경로 해결
    # 채널 2 는 4-block warning 과 disjoint 하도록 bypass env 는 미설정
    env.pop("BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE", None)
    return subprocess.run(
        ["bash", str(GATE_SCRIPT)],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        cwd=str(WORKTREE_ROOT),
        env=env,
    )


def test_subprocess_four_block_missing_channel2_emit_and_warning_intact():
    """subprocess: 4-block 일부 누락 prompt → 채널 2 emit + 기존 4-block warning 무손상.

    (i) returncode 0 (Wave1 항상 exit 0).
    (ii) stdout json.loads → additionalContext 전환 마커 존재 + permissionDecision deny 아님.
    (iii) stderr 에 기존 4-block warning 마커 존재(회귀 무손상).
    exit code 단독 금지 — stdout 마커 + stderr 마커 병행 assert(distinct-marker 의무, §2247).
    """
    _skip_if_no_bash()
    result = _run_gate_subprocess("일부만 있는 spawn prompt")  # 4 block 부재

    assert result.returncode == 0, (
        f"Wave1 exit 0 위반 (rc={result.returncode}, stderr={result.stderr!r})"
    )
    # (ii) 채널 2 emit — stdout 은 채널 2 JSON 정확히 1개
    out = result.stdout.strip()
    obj = json.loads(out)  # plain/빈 stdout 이면 JSONDecodeError → RED
    hso = obj["hookSpecificOutput"]
    assert TRANSITION_MARKER in hso["additionalContext"], "채널 2 전환 마커 미inject"
    assert hso.get("permissionDecision", None) != "deny", "NEVER deny 위반"
    # (iii) 기존 4-block warning 회귀 무손상 — stderr 마커 존재
    assert GATE_WARNING_MARKER in result.stderr, (
        "4-block warning 마커 부재 — 기존 gate stderr 회귀(무손상 위반)"
    )


def test_subprocess_four_block_present_channel2_emit_no_warning():
    """subprocess: 4-block 모두 포함 prompt → 채널 2 emit 유지 + 4-block warning 부재.

    정상 경로(4 block 완비)도 채널 2 emit 은 유지되고, 기존 4-block warning 은 발화 안 함.
    (i) returncode 0. (ii) stdout additionalContext 전환 마커 존재 + deny 아님.
    (iii) stderr 에 4-block warning 마커 부재(정상 경로 무경고).
    """
    _skip_if_no_bash()
    result = _run_gate_subprocess(_PROMPT_ALL_BLOCKS)

    assert result.returncode == 0, (
        f"exit 0 위반 (rc={result.returncode}, stderr={result.stderr!r})"
    )
    # (ii) 채널 2 emit 유지
    out = result.stdout.strip()
    obj = json.loads(out)
    hso = obj["hookSpecificOutput"]
    assert TRANSITION_MARKER in hso["additionalContext"], "정상 경로 채널 2 전환 마커 미inject"
    assert hso.get("permissionDecision", None) != "deny", "NEVER deny 위반"
    # (iii) 정상 경로 = 4-block warning 부재
    assert GATE_WARNING_MARKER not in result.stderr, (
        "4 block 완비인데 warning 마커 발화 (false-positive 회귀)"
    )


# ════════════════════════════════ (C) CFP-2587 Phase 2 — Agent 표면 --inject 통합 (T-1/T-2a/T-3/T-4)
#
# 배경: hooks/pretooluse-agent-spawn-gate 가 CFP-2587 에서 `--inject --subject <subagent_type>
#   --kst-stamp <stamp> --transition-reminder` 로 재배선 (구 detect-warn + 구 reminder emit 을
#   단일 inject 로 대체). subject source = tool_input.subagent_type (spike AC-7 / §결정1).
#
# 이 블록은 Agent 표면 고유 축(위 (B) 채널2-only 커버리지 空)을 실 hook fork 로 봉인:
#   · T-2a (AC-7 §결정1 anti-test): subagent_type + stray top-level agent_type=dispatcher 공존 시
#       subject = subagent_type. dispatcher/Orchestrator 명 절대 미주입. (Bash 표면 대칭은
#       test_pretooluse_bash_description_inject.py — agent_type wins over stray subagent_type.)
#   · T-1 whole-echo: prompt/run_in_background verbatim 보존 + description 스탬프.
#   · T-3 merge: 단일 JSON 에 updatedInput ∧ additionalContext 병존 (bare, NEVER deny).
#   · T-4 idempotency: 이미 conformant → updatedInput SKIP 但 additionalContext 유지 (§7.3 회귀가드).
#
# git-bash 해석(_AGENT_INJECT_BASH): bash-hook 테스트와 동일 패턴 — Windows Git-Bash 에서도 실행
#   (기존 (B) block 의 win32-skip 보다 넓은 커버리지; Agent hook fork 는 git-bash 안전 실증).

_AGENT_INJECT_BASH = shutil.which("bash") or (
    r"C:\Program Files\Git\bin\bash.exe"
    if sys.platform == "win32" and Path(r"C:\Program Files\Git\bin\bash.exe").exists()
    else None
)
_agent_inject = pytest.mark.skipif(_AGENT_INJECT_BASH is None, reason="bash interpreter 부재")

_FIXTURES_DIR = WORKTREE_ROOT / "tests" / "spike" / "cfp-2587-updatedinput-honor" / "fixtures"
_INJECT_STAMP_SUBSTR = "[codeforge story-transition-autonomy]"  # full marker (TRANSITION_MARKER 는 substring)


def _load_agent_fixture():
    return json.loads((_FIXTURES_DIR / "agent-spawn.json").read_text(encoding="utf-8"))


def _fork_agent_gate(payload: dict):
    """Agent gate hook 을 git-bash 로 fork → (rc, stdout_stripped). UTF-8 capture (한국어 reminder)."""
    env = dict(os.environ)
    env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)
    env.pop("BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE", None)
    proc = subprocess.run(
        [_AGENT_INJECT_BASH, str(GATE_SCRIPT)],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
    )
    return proc.returncode, proc.stdout.strip()


@_agent_inject
def test_agent_inject_subagent_type_not_dispatcher():
    """T-2a (AC-7 §결정1 anti-test): subagent_type + stray top-level agent_type=SomeDispatcher 공존 →
    subject = subagent_type (ArchitectAgent). dispatcher 명 절대 미주입."""
    payload = {"tool_name": "Agent", "agent_type": "SomeDispatcher",
               "tool_input": {"subagent_type": "ArchitectAgent", "prompt": "do x",
                              "description": "nonconformant header desc"}}
    rc, out = _fork_agent_gate(payload)
    assert rc == 0, f"exit 0 위반 rc={rc}"
    hso = json.loads(out)["hookSpecificOutput"]  # 단일 JSON (Extra data → 실패)
    desc = hso["updatedInput"]["description"]
    assert desc.startswith("[ArchitectAgent] "), desc
    assert "SomeDispatcher" not in desc, f"§결정1 위반 — dispatcher 명 주입됨: {desc!r}"
    assert "permissionDecision" not in hso, "bare 위반 (permissionDecision 존재)"


@_agent_inject
def test_agent_inject_whole_echo_and_reminder_merge():
    """T-1/T-3 (Agent 표면): nonconformant → whole-echo(prompt/run_in_background/subagent_type verbatim)
    + description 스탬프 + additionalContext reminder 병합 (단일 JSON, bare)."""
    payload = _load_agent_fixture()
    orig = dict(payload["tool_input"])          # {description,prompt,subagent_type,run_in_background}
    orig["description"] = "raw nonconformant header"
    payload["tool_input"] = orig
    rc, out = _fork_agent_gate(payload)
    assert rc == 0
    hso = json.loads(out)["hookSpecificOutput"]
    ui = hso["updatedInput"]
    assert ui["prompt"] == orig["prompt"], "prompt 소실/변조 (whole-echo 위반)"
    assert ui["run_in_background"] == orig["run_in_background"], "run_in_background 소실/변조"
    assert ui["subagent_type"] == orig["subagent_type"], "subagent_type 소실/변조"
    assert ui["description"].startswith("[general-purpose] "), ui["description"]  # subagent_type=general-purpose
    assert _INJECT_STAMP_SUBSTR in hso["additionalContext"], "reminder 마커 부재 (merge 위반)"
    assert "permissionDecision" not in hso, "bare 위반"


@_agent_inject
def test_agent_inject_idempotent_conformant_keeps_reminder_only():
    """T-4/§7.3 회귀가드: 이미 conformant description → updatedInput SKIP 但 additionalContext 유지."""
    payload = {"tool_name": "Agent",
               "tool_input": {"subagent_type": "ArchitectAgent", "prompt": "p",
                              "description": "[ArchitectAgent] 07/09 14:30 - already conformant"}}
    rc, out = _fork_agent_gate(payload)
    assert rc == 0
    hso = json.loads(out)["hookSpecificOutput"]
    assert "updatedInput" not in hso, "idempotent 위반 — 이미 conformant 인데 updatedInput 주입"
    assert _INJECT_STAMP_SUBSTR in hso["additionalContext"], "reminder UNCONDITIONAL 위반"


# ═══════════════════════ CFP-2587 Phase 2 구현리뷰 FIX-2 (QADev) — F4/F3 회귀 가드 봉인
#
# F4 (§7.3 LOAD-BEARING): prompt 키 부재(빈 prompt) 또는 prompt="" 여도 additionalContext(reminder)
#   무조건 emit. 구 회귀(early-exit)는 빈 prompt 시 stdout 완전 empty → json.loads 실패로 RED.
# F3 (§7.7-2 field-absent SKIP, Bash 표면 §7.7-3 대칭): subagent_type 키 자체 부재 → injection(updatedInput)
#   SKIP 하되 additionalContext(reminder)는 여전히 present. present-but-empty("") → injection 발생 +
#   description 프리픽스 = [unknown-agent] (G2 fallback).
# distinct-marker 규율 상속: exit code 단독 판정 금지 — json.loads 후 key-path/substring 병행 assert.


@_agent_inject
def test_agent_inject_empty_prompt_still_emits_reminder():
    """F4/§7.3 회귀가드: prompt 키 부재(빈 prompt) Agent payload → additionalContext(reminder)
    여전히 present. 구 회귀(early-exit)는 stdout 완전 empty → json.loads 실패로 RED.
    subagent_type present(+nonconformant desc) → injection 도 발생."""
    payload = {"tool_name": "Agent",
               "tool_input": {"subagent_type": "ArchitectAgent",
                              "description": "raw nonconformant header"}}  # prompt 키 부재
    rc, out = _fork_agent_gate(payload)
    assert rc == 0, f"exit 0 위반 rc={rc}"
    hso = json.loads(out)["hookSpecificOutput"]   # 구 회귀면 out=="" → JSONDecodeError = RED
    assert _INJECT_STAMP_SUBSTR in hso["additionalContext"], "§7.3 위반 — 빈 prompt 시 reminder 소실"
    # subagent_type present → injection 도 발생
    assert hso["updatedInput"]["description"].startswith("[ArchitectAgent] "), hso["updatedInput"]["description"]
    assert "permissionDecision" not in hso, "bare 위반 (NEVER deny)"


@_agent_inject
def test_agent_inject_explicit_empty_prompt_string_reminder():
    """F4/§7.3 회귀가드 variant: prompt=""(명시적 빈 문자열) → additionalContext(reminder) 여전히 present."""
    payload = {"tool_name": "Agent",
               "tool_input": {"subagent_type": "ArchitectAgent", "prompt": "",
                              "description": "raw nonconformant"}}
    rc, out = _fork_agent_gate(payload)
    assert rc == 0, f"exit 0 위반 rc={rc}"
    hso = json.loads(out)["hookSpecificOutput"]
    assert _INJECT_STAMP_SUBSTR in hso["additionalContext"], "§7.3 위반 — 명시적 빈 prompt 시 reminder 소실"


@_agent_inject
def test_agent_inject_subagent_type_absent_skips_injection_keeps_reminder():
    """F3/§7.7-2: subagent_type 키 부재 → updatedInput 부재(injection skip) 但 additionalContext present.
    field-absent 는 위반 아님(SKIP) — Bash 표면 §7.7-3 대칭."""
    payload = {"tool_name": "Agent",
               "tool_input": {"prompt": "p", "description": "raw nonconformant"}}  # subagent_type 키 부재
    rc, out = _fork_agent_gate(payload)
    assert rc == 0, f"exit 0 위반 rc={rc}"
    hso = json.loads(out)["hookSpecificOutput"]
    assert "updatedInput" not in hso, "§7.7-2 위반 — field-absent 인데 injection 발생"
    assert _INJECT_STAMP_SUBSTR in hso["additionalContext"], "reminder 소실"
    assert "permissionDecision" not in hso, "bare 위반 (NEVER deny)"


@_agent_inject
def test_agent_inject_subagent_type_present_empty_unknown_agent():
    """F3/G2: subagent_type present-but-empty("") → injection 발생 + [unknown-agent] fallback 프리픽스."""
    payload = {"tool_name": "Agent",
               "tool_input": {"subagent_type": "", "prompt": "p",
                              "description": "raw nonconformant"}}
    rc, out = _fork_agent_gate(payload)
    assert rc == 0, f"exit 0 위반 rc={rc}"
    hso = json.loads(out)["hookSpecificOutput"]
    assert hso["updatedInput"]["description"].startswith("[unknown-agent] "), hso["updatedInput"]["description"]
    assert _INJECT_STAMP_SUBSTR in hso["additionalContext"], "reminder 소실"
    assert "permissionDecision" not in hso, "bare 위반 (NEVER deny)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
