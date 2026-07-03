"""test_story_transition_autonomy_reminder.py — CFP-2567 Phase 2 §7.8 Test Contract 이행 (TDD).

계약 SSOT:
  Story CFP-2567 §7.8 Test Contract / ADR-071 §결정 22 §22.4 (Amendment 13).
  채널 1 = story-transition-autonomy-reminder.py 의 UNCONDITIONAL UserPromptSubmit
  reminder hook public surface 검증 — Epic 내 Story 전환 자율 진행(over-halt/over-ask 방지)
  norm 을 매 user turn 에 salient 하게 유지하되, 정당 멈춤 3종 carve-out 은 반드시 포함.
  skip-offer-reminder.py(§결정 21) 동형 hook-frame(ADR-115 5층 graceful degradation,
  전경로 exit 0, JSON additionalContext emit) 재사용.

불변식 (INV-1~6):
  - INV-1: 모든 입력 case main() → exit 0 (P0 fail-safe).
  - INV-2: 모든 입력 case stdout JSON 파싱됨 (unconditional emit — regex gate 없음).
  - INV-3: additionalContext = 정적 (서로 다른 입력에 동일 텍스트, set 크기 1).
  - INV-4: stderr AND parsed additionalContext 에 prompt echo 0 (sentinel — PII/secret 차단).
  - INV-5: stdout JSON 의 hookEventName 항상 "UserPromptSubmit".
  - INV-6 (load-bearing): parsed additionalContext 에 정당 멈춤 3종 carve-out 이
    각각 개별 exact substring 으로 존재 + 마커 + ADR 참조 + <system-reminder> 블록.
    막연한 "clause 포함" 금지 — mutation survival(한 carve-out 삭제) 방지.

anti-theater 규칙 (mutation 생존 0):
  - INV-2/4/5/6: substring assert 절대 금지 — stdout 을 json.loads 후 key-path
    obj["hookSpecificOutput"]["additionalContext"] 순회만.
  - INV-6: 3 carve-out 을 개별 assert (묶음 OR 금지 — 하나 누락도 falsify).

CI: lint.yml hook-unit-tests job (ubuntu-latest). windows matrix 미포함 —
advisory 단발 훅이라 비용 대비 가치 낮음 (skip-offer-reminder test 동일 정책 답습).

TDD red→green 순서: 병렬 DeveloperAgent 가 hooks/story-transition-autonomy-reminder.py
production 을 작성하기 전(pre-GREEN)에는 conftest import 실패 또는 assert fail 이 정상.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

import story_transition_autonomy_reminder as star


# worktree root = tests/ → hooks/ → root (precedent: skip_offer_reminder test L37)
WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent

# 계약 exact strings (spawn packet §계약 — 반드시 이 문자열로 assert)
MARKER = "[codeforge story-transition-autonomy]"
CARVEOUT_AMBIGUOUS = "요구 자체가 애매"       # ask-trigger ①
CARVEOUT_TRADEOFF = "진짜 가치 trade-off"      # ask-trigger ②
CARVEOUT_IRREVERSIBLE = "비가역·고비용"         # ask-trigger ③


def _set_stdin(monkeypatch, text: str) -> None:
    """stdin 을 io.StringIO 로 치환 + isatty=False (non-interactive 세션 모사)."""
    monkeypatch.setattr("sys.stdin", io.StringIO(text))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)


# ============================================================ TC-01 (P0) 정상 경로


def test_tc01_change_verb_prompt_fires(monkeypatch, capsys):
    """TC-01 (P0): change-verb prompt → main() → stdout 비어있지 않음 + json.loads 성공."""
    _set_stdin(monkeypatch, '{"prompt":"X 구현해줘"}')
    rc = star.main()
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out.strip() != ""  # 발화 (비어있지 않음)
    obj = json.loads(captured.out)  # 파싱 성공 (TypeError/ValueError 시 fail)
    assert isinstance(obj, dict)


# ============================================================ TC-02 (P0, discriminating)


@pytest.mark.parametrize(
    "prompt",
    [
        "진행해",       # 변경동사 없음 — 단순 진행 지시(전환 창 전형)
        "현황은?",      # 질의 (변경동사 0)
        "다음 스토리",  # 명사구 (전환 지시, 변경동사 0)
    ],
)
def test_tc02_non_change_verb_prompt_still_fires(prompt, monkeypatch, capsys):
    """TC-02 (P0, discriminating): non-change-verb prompt → 여전히 발화 (unconditional).

    load-bearing 차별 — regex gate 였다면 여기서 silent(무발화)했을 것. 전환 창은
    "진행해"·"다음 스토리" 같은 변경동사 없는 turn 이 전형이라 이 case 가 핵심.
    """
    _set_stdin(monkeypatch, json.dumps({"prompt": prompt}, ensure_ascii=False))
    rc = star.main()
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out.strip() != "", f"non-change-verb prompt 무발화 (회귀): {prompt!r}"
    obj = json.loads(captured.out)
    assert obj["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"


# ============================================================ TC-03 (P0) fail-safe 입력


@pytest.mark.parametrize(
    "stdin_text,label",
    [
        ("", "empty stdin"),
        ("그냥 텍스트", "raw 비-JSON stdin"),
    ],
)
def test_tc03_empty_and_raw_input_still_fires(stdin_text, label, monkeypatch, capsys):
    """TC-03 (P0): empty stdin + raw 비-JSON stdin 둘 다 → 발화 + exit 0."""
    _set_stdin(monkeypatch, stdin_text)
    rc = star.main()
    captured = capsys.readouterr()
    assert rc == 0, f"{label}: exit 0 위반"
    assert captured.out.strip() != "", f"{label}: 무발화 (unconditional 위반)"
    obj = json.loads(captured.out)
    assert obj["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"


# ============================================================ TC-04 (P0, anti-theater)


def test_tc04_emit_json_structure_keypath(monkeypatch, capsys):
    """TC-04 (P0, anti-theater): emit JSON 구조 = key-path 순회 검증.

    substring assert('additionalContext' in captured.out) 는 plain-stdout 회귀(#13912
    — JSON 래핑 누락하고 reminder 텍스트만 print)를 못 잡는다. json.loads 후 key-path
    순회만 그 불변식을 falsify.
    """
    _set_stdin(monkeypatch, '{"prompt":"무엇이든"}')
    star.main()
    captured = capsys.readouterr()
    obj = json.loads(captured.out)  # plain stdout 면 여기서 JSONDecodeError → fail
    assert obj["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert "additionalContext" in obj["hookSpecificOutput"]
    assert isinstance(obj["hookSpecificOutput"]["additionalContext"], str)


# ============================================================ TC-05 (P0) 마커·ADR 참조


def test_tc05_marker_and_adr_refs_in_parsed_context(monkeypatch, capsys):
    """TC-05 (P0): additionalContext 텍스트에 마커 + ADR-071 계열 참조 존재.

    anti-theater: stdout raw 가 아니라 파싱된 additionalContext 값에서 검사.
    """
    _set_stdin(monkeypatch, '{"prompt":"무엇이든"}')
    star.main()
    captured = capsys.readouterr()
    obj = json.loads(captured.out)
    ctx = obj["hookSpecificOutput"]["additionalContext"]  # 파싱된 값(raw stdout 아님)
    assert MARKER in ctx
    assert "ADR-071" in ctx
    assert "§결정 22" in ctx
    assert "over-halt" in ctx
    assert "over-ask" in ctx
    assert "§결정 18" in ctx  # disjoint session-swap cross-ref
    assert "<system-reminder>" in ctx
    assert "</system-reminder>" in ctx


# ============================================================ TC-06 (P0) exit 0 전경로


def test_tc06_normal_exit_zero(monkeypatch, capsys):
    """TC-06 (P0): 정상 입력 main() returncode 0."""
    _set_stdin(monkeypatch, '{"prompt":"정상"}')
    assert star.main() == 0


def test_tc06_empty_exit_zero(monkeypatch, capsys):
    """TC-06 (P0): empty 입력 main() returncode 0."""
    _set_stdin(monkeypatch, "")
    assert star.main() == 0


def test_tc06_exception_exit_zero(monkeypatch, capsys):
    """TC-06 (P0): _build_reminder 예외 주입 → 여전히 exit 0 + audit + prompt leak 0.

    예외 경로에서도 P0 exit 0 불변식 falsify. main() 의 try/except 전체 감쌈 검증.
    audit prefix = [story-transition-autonomy-reminder] (skip-offer 동형).
    """
    _set_stdin(monkeypatch, '{"prompt":"정상"}')

    def boom():
        raise RuntimeError("boom")

    monkeypatch.setattr(star, "_build_reminder", boom)
    rc = star.main()
    captured = capsys.readouterr()
    assert rc == 0  # 예외 발생해도 exit 0
    assert (
        "[story-transition-autonomy-reminder] fired exit_path=silent-exception"
        in captured.err
    )
    assert "정상" not in captured.err  # prompt leak 안 함


# ============================================================ TC-07 (P0) no-PII


def test_tc07_no_prompt_leak_to_stderr(monkeypatch, capsys):
    """TC-07 (P0): 고유 sentinel prompt → stderr AND parsed additionalContext 어디에도 부재."""
    sentinel = "SENTINEL_SECRET_abc123"
    _set_stdin(monkeypatch, json.dumps({"prompt": f"{sentinel} 구현"}, ensure_ascii=False))
    star.main()
    captured = capsys.readouterr()
    assert sentinel not in captured.err, "sentinel 이 stderr 로 leak (PII 차단 위반)"
    obj = json.loads(captured.out)
    assert sentinel not in obj["hookSpecificOutput"]["additionalContext"]


# ============================================================ TC-08 (P1) _read_input 단위


@pytest.mark.parametrize(
    "key",
    ["prompt", "user_message", "message", "text", "content"],
)
def test_tc08_read_input_json_keys(key, monkeypatch):
    """TC-08 (P1): _read_input JSON dict key 추출 (5종 parametrize)."""
    _set_stdin(monkeypatch, json.dumps({key: "extracted_value"}))
    assert star._read_input() == "extracted_value"


def test_tc08_read_input_malformed_json_raw_fallback(monkeypatch):
    """TC-08 (P1): malformed JSON → raw text 반환 (fallback)."""
    _set_stdin(monkeypatch, '{"prompt": ')  # 깨진 JSON
    assert star._read_input() == '{"prompt": '


def test_tc08_read_input_isatty_empty(monkeypatch):
    """TC-08 (P1): isatty=True (interactive) → "" 반환."""
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    assert star._read_input() == ""


# ============================================================ TC-09 (P1) hooks.json wiring


def test_tc09_hooks_json_has_story_transition_entry():
    """TC-09 (P1): hooks.json UserPromptSubmit 배열에 story-transition-autonomy-reminder entry 존재.

    json 파싱 후 UserPromptSubmit hook command 문자열에 'story-transition-autonomy-reminder'
    포함하는 hook 1개 이상. TDD red→green — pre-GREEN HEAD 에서는 fail(정상, Dev 가 5번째
    entry append 후 통과).

    §22.4 D2 채널 1: UserPromptSubmit 배열 append.
    """
    hooks_json = WORKTREE_ROOT / "hooks" / "hooks.json"
    assert hooks_json.exists(), f"hooks.json 부재: {hooks_json}"
    data = json.loads(hooks_json.read_text(encoding="utf-8"))
    ups_groups = data["hooks"]["UserPromptSubmit"]
    commands = [
        h.get("command", "")
        for group in ups_groups
        for h in group.get("hooks", [])
    ]
    matches = [c for c in commands if "story-transition-autonomy-reminder" in c]
    assert len(matches) >= 1, (
        "hooks.json UserPromptSubmit 에 story-transition-autonomy-reminder entry 부재 "
        f"(등록된 commands: {commands})"
    )


# ============================================================ INV-1 ~ INV-6 (불변식)


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
    rc = star.main()
    capsys.readouterr()
    assert rc == 0, f"INV-1 위반 ({label}): exit {rc}"


@pytest.mark.parametrize("label,stdin_text", _INV_INPUTS)
def test_inv2_all_inputs_emit_parseable_json(label, stdin_text, monkeypatch, capsys):
    """INV-2: 모든 입력 case stdout JSON 파싱됨 (unconditional emit — regex gate 없음)."""
    _set_stdin(monkeypatch, stdin_text)
    star.main()
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
        star.main()
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
    star.main()
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
    star.main()
    captured = capsys.readouterr()
    obj = json.loads(captured.out)
    assert obj["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit", (
        f"INV-5 위반 ({label})"
    )


@pytest.mark.parametrize("label,stdin_text", _INV_INPUTS)
def test_inv6_three_carveouts_in_parsed_context(label, stdin_text, monkeypatch, capsys):
    """INV-6 (load-bearing): parsed additionalContext 에 정당 멈춤 3종 carve-out 각각 존재.

    over-suppression(EDGE-1) 차단 불변식 — reminder 가 전환 자율 진행을 강조하면서도
    정당 멈춤 3종(ask-trigger ①②③)을 반드시 명시해야 한다. 3 carve-out 을 개별 assert
    (묶음 OR 금지 — 하나만 삭제해도 mutation 이 falsify 되도록). 마커/ADR 참조/블록도 동반.
    """
    _set_stdin(monkeypatch, stdin_text)
    star.main()
    captured = capsys.readouterr()
    obj = json.loads(captured.out)
    ctx = obj["hookSpecificOutput"]["additionalContext"]
    # 정당 멈춤 3종 — 각각 개별 exact substring (mutation survival 방지)
    assert CARVEOUT_AMBIGUOUS in ctx, f"INV-6 ({label}): carve-out ① '{CARVEOUT_AMBIGUOUS}' 부재"
    assert CARVEOUT_TRADEOFF in ctx, f"INV-6 ({label}): carve-out ② '{CARVEOUT_TRADEOFF}' 부재"
    assert CARVEOUT_IRREVERSIBLE in ctx, f"INV-6 ({label}): carve-out ③ '{CARVEOUT_IRREVERSIBLE}' 부재"
    # 마커 + ADR 참조 + 블록
    assert MARKER in ctx
    assert "ADR-071" in ctx
    assert "§결정 22" in ctx
    assert "§결정 18" in ctx
    assert "<system-reminder>" in ctx
    assert "</system-reminder>" in ctx


def test_inv6_build_reminder_unit_three_carveouts():
    """INV-6 (load-bearing, build 단위): _build_reminder() 반환에 3 carve-out 개별 존재.

    main()·emit 우회 — build 함수 자체를 직접 호출해 정당 멈춤 3종 + 마커 + 블록 검증.
    build 단위로도 3-carve-out 개별 assert (spawn packet §계약 명시).
    """
    msg = star._build_reminder()
    # 정당 멈춤 3종 — 개별 exact substring
    assert CARVEOUT_AMBIGUOUS in msg
    assert CARVEOUT_TRADEOFF in msg
    assert CARVEOUT_IRREVERSIBLE in msg
    # 마커 + ADR 참조
    assert MARKER in msg
    assert "ADR-071" in msg
    assert "§결정 22" in msg
    assert "over-halt" in msg
    assert "over-ask" in msg
    assert "§결정 18" in msg
    # system-reminder 블록 구조
    assert "<system-reminder>" in msg
    assert "</system-reminder>" in msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
