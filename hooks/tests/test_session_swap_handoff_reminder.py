"""test_session_swap_handoff_reminder.py — CFP-2742 Phase 2 §8 Test Contract 이행 (TDD).

계약 SSOT:
  Story CFP-2742 §8 Test Contract / ADR-071 §결정 24 (session-swap controlled-path —
  handoff 6 필수요소 + 자족성 + advisory ceiling) / §결정 18 (bare reflex 전환 anti-pattern
  cross-ref, disjoint 축). 채널 = session-swap-handoff-reminder.py 의 UNCONDITIONAL
  UserPromptSubmit reminder hook public surface 검증 — 세션 전환 권유 전 자족 handoff
  프롬프트 선제 생성 norm 을 매 turn salient 하게 유지.
  story-transition-autonomy-reminder.py(§7.8, CFP-2567) 동형 hook-frame(ADR-115 5층
  graceful degradation, 전경로 exit 0, JSON additionalContext emit) 재사용 — 그 self-test
  (test_story_transition_autonomy_reminder.py) 를 구조적 참조 패턴으로 사용.

8 discriminating fixtures (spawn packet §계약, ①~⑧ 각각 mutation-kill 대상):
  ① hooks.json 미등록 회귀 — UserPromptSubmit command 문자열에 hook 이름 부재 시 falsify.
  ② hookEventName 오기 회귀 — "UserPromptSubmit" 아닌 값 시 falsify.
  ③ 6요소/자족성 문구 누락 회귀 — 개별 exact-substring (OR-bundling 금지, mutation survival 0).
  ④ JSON 래핑 누락 회귀 (#13912) — plain-stdout 이면 json.loads 가 falsify.
  ⑤ unconditional 위반(intent-gate 삽입) 회귀 — non-change-verb/query/empty/raw-non-json/
    fallback-key 입력 전체가 여전히 발화해야 함.
  ⑥ exit-0 fail-safe 회귀 — 정상/empty/예외주입 케이스 모두 exit 0 + 예외 경로 audit line.
  ⑦ 기존 5-hook 보존 위반 회귀 — hooks.json UserPromptSubmit 배열에 5 기존 + 신규 1 = 6 전부 존재.
  ⑧ PII echo 회귀 — sentinel 이 stderr/additionalContext 어디에도 부재 (복수 parametrize).

anti-theater 규칙 (mutation 생존 0):
  - 구조/PII 판정은 raw-stdout substring 이 아니라 json.loads 후 key-path 순회로만 판정.
  - INV-6 / FX-3 6요소·자족성 문구는 개별 assert (묶음 OR 금지 — 하나 누락도 falsify).

TDD red→green 순서: 병렬 DeveloperAgent 가 hooks/session-swap-handoff-reminder.py production 을
  작성하기 전(pre-GREEN)에는 conftest import 실패 또는 assert fail 이 정상.

RED 진정성 입증 (cross-layer working-tree drift, git stash 기법) — 본 worktree 는 단일 세션
  concurrent dispatch 이나 QADev 테스트 작성 시점에 production 파일이 이미 working tree 에
  존재(GREEN 선착). agent §RED 상태 확인 관행 / stash 기법에 따라 pre-GREEN HEAD 노출 →
  discriminating case genuine 실패 확인 → GREEN 복원 후 재확인 절차를 수행함 (보고는 호출자
  텍스트 응답에 기재, 본 파일에는 미기재).
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

import session_swap_handoff_reminder as sshr


# worktree root = tests/ → hooks/ → root (precedent: story-transition-autonomy test L45)
WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent
HOOKS_JSON = WORKTREE_ROOT / "hooks" / "hooks.json"

# ── 계약 exact strings (spawn packet §계약 — PINNED, 반드시 이 문자열로 assert) ──────────────
MARKER = "[codeforge session-swap-handoff]"
ADR_REF = "ADR-071"
DECISION_24 = "§결정 24"
DECISION_18 = "§결정 18"

EL1 = "① 진행 Story/PR·Epic 번호"
EL2 = "② 완료 vs 남은 lane·단계"
EL3 = "③ worktree·브랜치 경로"
EL4 = "④ 기결정=재논의 금지 목록"
EL5 = "⑤ 이번 세션 gotcha"
EL6 = "⑥ 다음 세션 첫 액션 1문"

SELF_CONTAIN_1 = "현 세션 참조 0"
SELF_CONTAIN_2 = "복붙 1회 완결"

BLOCK_OPEN = "<system-reminder>"
BLOCK_CLOSE = "</system-reminder>"

NEW_HOOK_NAME = "session-swap-handoff-reminder"
EXISTING_5_HOOKS = [
    "korean-english-recovery",
    "bootstrap-first-gate",
    "skip-offer-reminder",
    "deferred-recovery-reminder",
    "story-transition-autonomy-reminder",
]


def _set_stdin(monkeypatch, text: str) -> None:
    """stdin 을 io.StringIO 로 치환 + isatty=False (non-interactive 세션 모사)."""
    monkeypatch.setattr("sys.stdin", io.StringIO(text))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)


def _ups_commands() -> list:
    """hooks.json UserPromptSubmit 배열의 모든 hook command 문자열 리스트."""
    data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    ups_groups = data["hooks"]["UserPromptSubmit"]
    return [
        h.get("command", "")
        for group in ups_groups
        for h in group.get("hooks", [])
    ]


def _assert_all_six_elements_and_self_containment(ctx: str, label: str = "") -> None:
    """6 필수요소 + 자족성 문구 + 마커 + ADR 참조 + 블록 태그를 개별 assert (mutation survival 0)."""
    assert EL1 in ctx, f"{label}: 6요소 ① 부재"
    assert EL2 in ctx, f"{label}: 6요소 ② 부재"
    assert EL3 in ctx, f"{label}: 6요소 ③ 부재"
    assert EL4 in ctx, f"{label}: 6요소 ④ 부재"
    assert EL5 in ctx, f"{label}: 6요소 ⑤ 부재"
    assert EL6 in ctx, f"{label}: 6요소 ⑥ 부재"
    assert SELF_CONTAIN_1 in ctx, f"{label}: 자족성 문구 '{SELF_CONTAIN_1}' 부재"
    assert SELF_CONTAIN_2 in ctx, f"{label}: 자족성 문구 '{SELF_CONTAIN_2}' 부재"
    assert MARKER in ctx, f"{label}: 마커 부재"
    assert ADR_REF in ctx, f"{label}: ADR-071 참조 부재"
    assert DECISION_24 in ctx, f"{label}: §결정 24 참조 부재"
    assert DECISION_18 in ctx, f"{label}: §결정 18 참조 부재"
    assert BLOCK_OPEN in ctx, f"{label}: <system-reminder> 블록 open 부재"
    assert BLOCK_CLOSE in ctx, f"{label}: </system-reminder> 블록 close 부재"


# ============================================================ FX-① hooks.json 등록 회귀


def test_fx1_hooks_json_has_session_swap_handoff_entry():
    """FX-①: hooks.json UserPromptSubmit 배열에 session-swap-handoff-reminder entry 존재.

    TDD red→green — pre-GREEN HEAD 에서는 fail(정상, Dev 가 6번째 entry append 후 통과).
    """
    assert HOOKS_JSON.exists(), f"hooks.json 부재: {HOOKS_JSON}"
    commands = _ups_commands()
    matches = [c for c in commands if NEW_HOOK_NAME in c]
    assert len(matches) >= 1, (
        f"hooks.json UserPromptSubmit 에 {NEW_HOOK_NAME} entry 부재 "
        f"(등록된 commands: {commands})"
    )


# ============================================================ FX-② hookEventName 오기 회귀


def test_fx2_hook_event_name_is_userpromptsubmit(monkeypatch, capsys):
    """FX-②: 파싱된 hookSpecificOutput.hookEventName == 'UserPromptSubmit' (오기 회귀 falsify)."""
    _set_stdin(monkeypatch, '{"prompt":"무엇이든"}')
    sshr.main()
    captured = capsys.readouterr()
    obj = json.loads(captured.out)
    assert obj["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"


# ============================================================ FX-③ 6요소/자족성 문구 누락 회귀


def test_fx3_six_elements_and_self_containment_in_parsed_context(monkeypatch, capsys):
    """FX-③: parsed additionalContext 에 6요소 + 자족성 문구 + 마커 + ADR 참조 + 블록 개별 존재.

    anti-theater: raw stdout 이 아니라 파싱된 additionalContext 값에서 개별 exact-substring 검사
    (묶음 OR 금지 — 하나 누락도 이 assert 가 falsify).
    """
    _set_stdin(monkeypatch, '{"prompt":"무엇이든"}')
    sshr.main()
    captured = capsys.readouterr()
    obj = json.loads(captured.out)
    ctx = obj["hookSpecificOutput"]["additionalContext"]
    _assert_all_six_elements_and_self_containment(ctx, label="FX-3")


# ============================================================ FX-④ JSON 래핑 누락 회귀 (#13912)


def test_fx4_emit_json_structure_keypath(monkeypatch, capsys):
    """FX-④ (anti-theater): emit JSON 구조 = key-path 순회 검증.

    substring assert 는 plain-stdout 회귀(#13912 — JSON 래핑 누락하고 reminder 텍스트만
    print)를 못 잡는다. json.loads 후 key-path 순회만 그 불변식을 falsify.
    """
    _set_stdin(monkeypatch, '{"prompt":"무엇이든"}')
    sshr.main()
    captured = capsys.readouterr()
    obj = json.loads(captured.out)  # plain stdout 면 여기서 JSONDecodeError → fail
    assert obj["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert "additionalContext" in obj["hookSpecificOutput"]
    assert isinstance(obj["hookSpecificOutput"]["additionalContext"], str)


# ============================================================ FX-⑤ unconditional 위반 회귀


@pytest.mark.parametrize(
    "label,stdin_text",
    [
        ("non-change-verb", '{"prompt":"진행해"}'),
        ("query", '{"prompt":"현황은?"}'),
        ("empty", ""),
        ("raw-non-json", "그냥 텍스트"),
        ("fallback-key", '{"user_message":"fallback"}'),
    ],
)
def test_fx5_unconditional_fires_for_every_input(label, stdin_text, monkeypatch, capsys):
    """FX-⑤ (discriminating): intent-gate 삽입 회귀 — 모든 입력 case 여전히 발화.

    regex/intent gate 였다면 non-change-verb·query 등 일부 입력에서 silent(무발화) 했을 것.
    """
    _set_stdin(monkeypatch, stdin_text)
    rc = sshr.main()
    captured = capsys.readouterr()
    assert rc == 0, f"FX-5 ({label}): exit 0 위반"
    assert captured.out.strip() != "", f"FX-5 ({label}): 무발화 (unconditional 위반, intent-gate 회귀)"
    obj = json.loads(captured.out)
    assert obj["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"


# ============================================================ FX-⑥ exit-0 fail-safe 회귀


def test_fx6_normal_exit_zero(monkeypatch, capsys):
    """FX-⑥: 정상 입력 main() returncode 0."""
    _set_stdin(monkeypatch, '{"prompt":"정상"}')
    assert sshr.main() == 0


def test_fx6_empty_exit_zero(monkeypatch, capsys):
    """FX-⑥: empty 입력 main() returncode 0."""
    _set_stdin(monkeypatch, "")
    assert sshr.main() == 0


def test_fx6_exception_injected_exit_zero_and_audit(monkeypatch, capsys):
    """FX-⑥: _build_reminder 예외 주입 → 여전히 exit 0 + audit line + prompt leak 0.

    main() 의 try/except 전체 감쌈 검증. audit prefix = [session-swap-handoff-reminder].
    """
    _set_stdin(monkeypatch, '{"prompt":"정상"}')

    def boom():
        raise RuntimeError("boom")

    monkeypatch.setattr(sshr, "_build_reminder", boom)
    rc = sshr.main()
    captured = capsys.readouterr()
    assert rc == 0  # 예외 발생해도 exit 0
    assert (
        "[session-swap-handoff-reminder] fired exit_path=silent-exception"
        in captured.err
    )
    assert "정상" not in captured.err  # prompt leak 안 함


# ============================================================ FX-⑦ 기존 5-hook 보존 회귀


def test_fx7_existing_5_hooks_preserved_plus_new_6th():
    """FX-⑦: hooks.json UserPromptSubmit 안 기존 5 hook 전부 존재 + 신규 1 = 총 6.

    mutation = 기존 hook 이 교체/누락되면 이 assert 가 개별 falsify.
    """
    commands = _ups_commands()
    joined = "\n".join(commands)
    for existing_name in EXISTING_5_HOOKS:
        assert existing_name in joined, f"FX-7: 기존 hook '{existing_name}' 소실 (보존 위반)"
    assert NEW_HOOK_NAME in joined, f"FX-7: 신규 hook '{NEW_HOOK_NAME}' 부재"
    matched_names = {
        name for name in EXISTING_5_HOOKS + [NEW_HOOK_NAME] if name in joined
    }
    assert matched_names == set(EXISTING_5_HOOKS + [NEW_HOOK_NAME]), (
        f"FX-7: 6-hook 전체 집합 불일치 (matched={matched_names})"
    )


# ============================================================ FX-⑧ PII echo 회귀


@pytest.mark.parametrize(
    "sentinel,stdin_text",
    [
        ("SENTINEL_SWAP_A_111", '{"prompt":"SENTINEL_SWAP_A_111 구현"}'),
        ("SENTINEL_SWAP_B_222", '{"user_message":"SENTINEL_SWAP_B_222 만들자"}'),
        ("SENTINEL_SWAP_C_333", "SENTINEL_SWAP_C_333 그냥 raw"),
    ],
)
def test_fx8_no_prompt_leak_stderr_and_context(sentinel, stdin_text, monkeypatch, capsys):
    """FX-⑧: 고유 sentinel prompt → stderr AND parsed additionalContext 어디에도 부재."""
    _set_stdin(monkeypatch, stdin_text)
    sshr.main()
    captured = capsys.readouterr()
    assert sentinel not in captured.err, f"FX-8: {sentinel} stderr leak (PII 차단 위반)"
    obj = json.loads(captured.out)
    assert sentinel not in obj["hookSpecificOutput"]["additionalContext"], (
        f"FX-8: {sentinel} additionalContext leak"
    )


# ============================================================ TC-_read_input 단위 (5 키 + fallback)


@pytest.mark.parametrize(
    "key",
    ["prompt", "user_message", "message", "text", "content"],
)
def test_read_input_json_keys(key, monkeypatch):
    """_read_input JSON dict key 추출 (5종 parametrize)."""
    _set_stdin(monkeypatch, json.dumps({key: "extracted_value"}))
    assert sshr._read_input() == "extracted_value"


def test_read_input_malformed_json_raw_fallback(monkeypatch):
    """_read_input malformed JSON → raw text 반환 (fallback)."""
    _set_stdin(monkeypatch, '{"prompt": ')  # 깨진 JSON
    assert sshr._read_input() == '{"prompt": '


def test_read_input_isatty_empty(monkeypatch):
    """_read_input isatty=True (interactive) → "" 반환."""
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    assert sshr._read_input() == ""


# ============================================================ INV-1 ~ INV-6 (불변식, sibling 동형)


# 다양한 입력 case — INV 루프 공용 (sentinel 포함 PII case 도)
_INV_INPUTS = [
    ("change-verb json", '{"prompt":"X 구현해줘"}'),
    ("non-change-verb json", '{"prompt":"진행해"}'),
    ("query json", '{"prompt":"현황은?"}'),
    ("empty stdin", ""),
    ("raw non-json", "그냥 텍스트"),
    ("fallback key json", '{"user_message":"fallback"}'),
    ("sentinel pii json", '{"prompt":"SENTINEL_LEAK_xyz789 만들자"}'),
]


@pytest.mark.parametrize("label,stdin_text", _INV_INPUTS)
def test_inv1_all_inputs_exit_zero(label, stdin_text, monkeypatch, capsys):
    """INV-1: 모든 입력 case main() → exit 0 (P0 fail-safe)."""
    _set_stdin(monkeypatch, stdin_text)
    rc = sshr.main()
    capsys.readouterr()
    assert rc == 0, f"INV-1 위반 ({label}): exit {rc}"


@pytest.mark.parametrize("label,stdin_text", _INV_INPUTS)
def test_inv2_all_inputs_emit_parseable_json(label, stdin_text, monkeypatch, capsys):
    """INV-2: 모든 입력 case stdout JSON 파싱됨 (unconditional emit — regex gate 없음)."""
    _set_stdin(monkeypatch, stdin_text)
    sshr.main()
    captured = capsys.readouterr()
    assert captured.out.strip() != "", f"INV-2 위반 ({label}): 무발화"
    obj = json.loads(captured.out)  # 파싱 실패 시 fail
    assert isinstance(obj, dict), f"INV-2 위반 ({label}): dict 아님"


def test_inv3_additional_context_is_static(monkeypatch, capsys):
    """INV-3: additionalContext = 정적 (서로 다른 입력에 동일 텍스트, set 크기 1).

    입력 무관 정적 reminder 임을 falsify — 입력에 따라 텍스트가 달라지면(echo 등) 실패.
    """
    contexts = []
    for _, stdin_text in _INV_INPUTS:
        _set_stdin(monkeypatch, stdin_text)
        sshr.main()
        captured = capsys.readouterr()
        obj = json.loads(captured.out)
        contexts.append(obj["hookSpecificOutput"]["additionalContext"])
    assert len(set(contexts)) == 1, (
        f"INV-3 위반: additionalContext 가 입력별로 다름 (distinct={len(set(contexts))})"
    )


@pytest.mark.parametrize(
    "sentinel,stdin_text",
    [
        ("SENTINEL_A_111", '{"prompt":"SENTINEL_A_111 구현"}'),
        ("SENTINEL_B_222", '{"user_message":"SENTINEL_B_222 만들자"}'),
        ("SENTINEL_C_333", "SENTINEL_C_333 그냥 raw"),
    ],
)
def test_inv4_no_prompt_echo_stderr_and_context(sentinel, stdin_text, monkeypatch, capsys):
    """INV-4: stderr AND parsed additionalContext 에 prompt echo 0 (여러 sentinel)."""
    _set_stdin(monkeypatch, stdin_text)
    sshr.main()
    captured = capsys.readouterr()
    assert sentinel not in captured.err, f"INV-4 위반: {sentinel} stderr leak"
    obj = json.loads(captured.out)
    assert sentinel not in obj["hookSpecificOutput"]["additionalContext"], (
        f"INV-4 위반: {sentinel} additionalContext leak"
    )


@pytest.mark.parametrize("label,stdin_text", _INV_INPUTS)
def test_inv5_hook_event_name_always_userpromptsubmit(
    label, stdin_text, monkeypatch, capsys
):
    """INV-5: stdout JSON 의 hookEventName 항상 'UserPromptSubmit'."""
    _set_stdin(monkeypatch, stdin_text)
    sshr.main()
    captured = capsys.readouterr()
    obj = json.loads(captured.out)
    assert obj["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit", (
        f"INV-5 위반 ({label})"
    )


@pytest.mark.parametrize("label,stdin_text", _INV_INPUTS)
def test_inv6_six_elements_and_self_containment_in_parsed_context(
    label, stdin_text, monkeypatch, capsys
):
    """INV-6 (load-bearing): parsed additionalContext 에 6요소 + 자족성 문구 각각 존재.

    over-suppression 차단 불변식 — reminder 가 전환 자체를 장려하지 않으면서도(advisory
    ceiling) 6 필수요소 + 자족성을 반드시 명시해야 한다. 개별 assert (묶음 OR 금지).
    """
    _set_stdin(monkeypatch, stdin_text)
    sshr.main()
    captured = capsys.readouterr()
    obj = json.loads(captured.out)
    ctx = obj["hookSpecificOutput"]["additionalContext"]
    _assert_all_six_elements_and_self_containment(ctx, label=f"INV-6 ({label})")


def test_inv6_build_reminder_unit_six_elements_and_self_containment():
    """INV-6 (load-bearing, build 단위): _build_reminder() 반환에 6요소 + 자족성 개별 존재.

    main()·emit 우회 — build 함수 자체를 직접 호출해 6요소 + 자족성 + 마커 + 블록 검증.
    """
    msg = sshr._build_reminder()
    _assert_all_six_elements_and_self_containment(msg, label="build-unit")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
