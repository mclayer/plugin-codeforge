"""test_skip_offer_reminder.py — CFP-2456 Phase 2 §8.1 Test Contract 이행 (TDD).

계약 SSOT:
  Story CFP-2456 §8.1 Test Contract (spawn-packet 락) — skip-offer-reminder.py 의
  UNCONDITIONAL UserPromptSubmit reminder hook public surface 검증.
  ADR-027 Amendment 12 §결정 15 / ADR-127 Amendment 1.

불변식 (INV-1~6):
  - INV-1: 모든 입력 case main() → exit 0 (P0 fail-safe).
  - INV-2: 모든 입력 case stdout JSON 파싱됨 (unconditional emit — regex gate 없음).
  - INV-3: additionalContext = 정적 (서로 다른 입력에 동일 텍스트).
  - INV-4: stderr 에 prompt echo 0 (여러 sentinel — PII/secret 차단).
  - INV-5: stdout JSON 의 hookEventName 항상 "UserPromptSubmit".
  - INV-6: _build_reminder() 반환에 키워드 5종 (ADR-127 / 정식 / 생략 / skip / AskUserQuestion) 전부.

CI: lint.yml hook-unit-tests job (ubuntu-latest). windows matrix 미포함 — advisory 단발
훅이라 비용 대비 가치 낮음 (bootstrap-first-gate test 와 동일 정책 답습).

anti-theater 규칙 (mutation 생존 0):
  - TC-04/TC-05: substring assert 절대 금지 — json.loads 후 key-path 순회만.
  - TC-02: 변경동사 없는 prompt (load-bearing 차별 — 구 hook 대비).
  - TC-09: 양파일 동시 검사 (편측 누락 차단).
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

import skip_offer_reminder as sor


# worktree root = tests/ → hooks/ → root (precedent: bootstrap-first-gate test L518-521)
WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent


def _set_stdin(monkeypatch, text: str) -> None:
    """stdin 을 io.StringIO 로 치환 + isatty=False (non-interactive 세션 모사)."""
    monkeypatch.setattr("sys.stdin", io.StringIO(text))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)


# ============================================================ TC-01 (P0)


def test_tc01_change_verb_prompt_fires(monkeypatch, capsys):
    """TC-01 (P0): change-verb prompt → main() → stdout 비어있지 않음 + json.loads 성공.

    §8.1 row TC-01. 변경동사 prompt 의 정상 경로 발화.
    """
    _set_stdin(monkeypatch, '{"prompt":"X 구현해줘"}')
    rc = sor.main()
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out.strip() != ""  # 발화 (비어있지 않음)
    obj = json.loads(captured.out)  # 파싱 성공 (TypeError/ValueError 시 fail)
    assert isinstance(obj, dict)


# ============================================================ TC-02 (P0, discriminating)


@pytest.mark.parametrize(
    "prompt",
    [
        "진행해",       # 변경동사 없음 — 단순 진행 지시
        "현황은?",      # 질의 (변경동사 0)
        "다음 단계",    # 명사구 (변경동사 0)
    ],
)
def test_tc02_non_change_verb_prompt_still_fires(prompt, monkeypatch, capsys):
    """TC-02 (P0, discriminating): non-change-verb prompt → 여전히 발화.

    이게 핵심 차별 invariant — 구 userprompt_reminder.py (변경동사 regex gate)
    였다면 여기서 silent (무발화) 했을 것. unconditional fire 라서 변경동사 없는
    turn 에도 발화한다. 구 hook 대비 load-bearing 차별 — 변경동사 prompt 만 쓰면
    이 TC 가 TC-01 과 구분 안 돼 무의미해진다 (regex gate 회귀 못 잡음).

    §8.1 row TC-02.
    """
    _set_stdin(monkeypatch, json.dumps({"prompt": prompt}, ensure_ascii=False))
    rc = sor.main()
    captured = capsys.readouterr()
    assert rc == 0
    assert captured.out.strip() != "", f"non-change-verb prompt 무발화 (회귀): {prompt!r}"
    obj = json.loads(captured.out)
    assert obj["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"


# ============================================================ TC-03 (P0)


@pytest.mark.parametrize(
    "stdin_text,label",
    [
        ("", "empty stdin"),
        ("그냥 텍스트", "raw 비-JSON stdin"),
    ],
)
def test_tc03_empty_and_raw_input_still_fires(stdin_text, label, monkeypatch, capsys):
    """TC-03 (P0): empty stdin + raw 비-JSON stdin 둘 다 → 발화 + exit 0.

    unconditional fire + fail-safe — 입력 형태 무관 발화. JSON 파싱 실패해도
    예외 없이 발화한다 (raw fallback). §8.1 row TC-03.
    """
    _set_stdin(monkeypatch, stdin_text)
    rc = sor.main()
    captured = capsys.readouterr()
    assert rc == 0, f"{label}: exit 0 위반"
    assert captured.out.strip() != "", f"{label}: 무발화 (unconditional 위반)"
    obj = json.loads(captured.out)
    assert obj["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"


# ============================================================ TC-04 (P0, anti-theater)


def test_tc04_emit_json_structure_keypath(monkeypatch, capsys):
    """TC-04 (P0, anti-theater): emit JSON 구조 = key-path 순회 검증.

    anti-theater 사유: substring assert ('additionalContext' in captured.out) 는
    plain-stdout 회귀 (#13912 — JSON 래핑 누락하고 reminder 텍스트만 print) 를 못 잡는다.
    JSON 으로 파싱한 뒤 hookSpecificOutput.hookEventName / additionalContext key-path 를
    순회해야만 "올바른 hookSpecificOutput JSON 형식" 불변식을 falsify 할 수 있다.

    §8.1 row TC-04. spec invariant: JSON additionalContext 형식.
    """
    _set_stdin(monkeypatch, '{"prompt":"무엇이든"}')
    sor.main()
    captured = capsys.readouterr()
    obj = json.loads(captured.out)  # plain stdout 면 여기서 JSONDecodeError → fail
    assert obj["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert "additionalContext" in obj["hookSpecificOutput"]
    assert isinstance(obj["hookSpecificOutput"]["additionalContext"], str)


# ============================================================ TC-05 (P0)


def test_tc05_reminder_keywords_in_parsed_context(monkeypatch, capsys):
    """TC-05 (P0): additionalContext 텍스트에 ADR-127 키워드 5종 검사.

    anti-theater: stdout raw 가 아니라 파싱된 additionalContext 값에서 검사 —
    JSON 키 이름 (예: 'additionalContext' literal) 이 우연히 키워드를 포함해도
    실제 reminder 텍스트가 비면 falsify 되도록. ADR-127 AND 정식 AND 생략
    AND (skip OR AskUserQuestion).

    §8.1 row TC-05.
    """
    _set_stdin(monkeypatch, '{"prompt":"무엇이든"}')
    sor.main()
    captured = capsys.readouterr()
    obj = json.loads(captured.out)
    ctx = obj["hookSpecificOutput"]["additionalContext"]  # 파싱된 값 (raw stdout 아님)
    assert "ADR-127" in ctx
    assert "정식" in ctx
    assert "생략" in ctx
    assert ("skip" in ctx) or ("AskUserQuestion" in ctx)


# ============================================================ TC-06 (P0)


def test_tc06_normal_exit_zero(monkeypatch, capsys):
    """TC-06 (P0): 정상 입력 main() returncode 0."""
    _set_stdin(monkeypatch, '{"prompt":"정상"}')
    assert sor.main() == 0


def test_tc06_empty_exit_zero(monkeypatch, capsys):
    """TC-06 (P0): empty 입력 main() returncode 0."""
    _set_stdin(monkeypatch, "")
    assert sor.main() == 0


def test_tc06_exception_exit_zero(monkeypatch, capsys):
    """TC-06 (P0): _build_reminder 예외 주입 → 여전히 exit 0 (전경로 fail-safe).

    예외 경로에서도 P0 exit 0 불변식 falsify. main() 의 try/except 전체 감쌈 검증.
    §8.1 row TC-06.
    """
    _set_stdin(monkeypatch, '{"prompt":"정상"}')

    def boom():
        raise RuntimeError("boom")

    monkeypatch.setattr(sor, "_build_reminder", boom)
    rc = sor.main()
    captured = capsys.readouterr()
    assert rc == 0  # 예외 발생해도 exit 0
    # 예외 경로 audit (prompt echo 0)
    assert "[skip-offer-reminder] fired exit_path=silent-exception" in captured.err
    assert "정상" not in captured.err  # prompt leak 안 함


# ============================================================ TC-07 (P0)


def test_tc07_no_prompt_leak_to_stderr(monkeypatch, capsys):
    """TC-07 (P0): 고유 sentinel prompt → stderr 에 sentinel 미포함 (PII/secret 차단).

    stdout 의 additionalContext 는 정적 reminder 라 sentinel 미포함 (추가 assert).
    §8.1 row TC-07. spec invariant: no-PII (prompt echo 0).
    """
    sentinel = "SENTINEL_SECRET_abc123"
    _set_stdin(monkeypatch, json.dumps({"prompt": f"{sentinel} 구현"}, ensure_ascii=False))
    sor.main()
    captured = capsys.readouterr()
    assert sentinel not in captured.err, "sentinel 이 stderr 로 leak (PII 차단 위반)"
    # 정적 reminder 라 stdout additionalContext 에도 sentinel 미포함
    obj = json.loads(captured.out)
    assert sentinel not in obj["hookSpecificOutput"]["additionalContext"]


# ============================================================ TC-08 (P1) — _read_input 단위


@pytest.mark.parametrize(
    "key",
    ["prompt", "user_message", "message", "text", "content"],
)
def test_tc08_read_input_json_keys(key, monkeypatch):
    """TC-08 (P1): _read_input JSON dict key 추출 (5종 parametrize).

    §8.1 row TC-08. bootstrap-first-gate test L32-43 답습.
    """
    _set_stdin(monkeypatch, json.dumps({key: "extracted_value"}))
    assert sor._read_input() == "extracted_value"


def test_tc08_read_input_malformed_json_raw_fallback(monkeypatch):
    """TC-08 (P1): malformed JSON → raw text 반환 (fallback)."""
    _set_stdin(monkeypatch, '{"prompt": ')  # 깨진 JSON
    assert sor._read_input() == '{"prompt": '


def test_tc08_read_input_isatty_empty(monkeypatch):
    """TC-08 (P1): isatty=True (interactive) → "" 반환."""
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    assert sor._read_input() == ""


def test_tc08_read_input_bounded_1mib(monkeypatch):
    """TC-08 (P1): bounded read ≤1 MiB (DoS 차단)."""
    huge = "a" * (1 << 20)  # 1 MiB exactly
    _set_stdin(monkeypatch, huge)
    result = sor._read_input()
    assert len(result) == (1 << 20)


# ============================================================ TC-09 (P1, structural-grep)


def test_tc09_story_yml_no_doc_only_dropdown_both_files():
    """TC-09 (P1, structural-grep): story.yml 양파일 'Doc-only fast-path' 0건.

    양파일 동시 검사 — .github/ISSUE_TEMPLATE/story.yml +
    templates/.github/ISSUE_TEMPLATE/story.yml. 한 파일만 검사하면 편측 누락
    (한쪽 dropdown 잔존) 을 못 잡는 anti-theater. ADR-127 doc-only fast-path 폐지.

    주의: DeveloperAgent/InfraEngineer 가 dropdown 제거를 끝내야 통과 (TDD red→green
    순서상 pre-GREEN HEAD 에서는 fail — 정상).

    §8.1 row TC-09.
    """
    targets = [
        WORKTREE_ROOT / ".github" / "ISSUE_TEMPLATE" / "story.yml",
        WORKTREE_ROOT / "templates" / ".github" / "ISSUE_TEMPLATE" / "story.yml",
    ]
    for path in targets:
        assert path.exists(), f"story.yml 부재: {path}"
        content = path.read_text(encoding="utf-8")
        assert "문서 (Doc-only fast-path)" not in content, (
            f"Doc-only fast-path dropdown 잔존 (ADR-127 폐지 위반): {path}"
        )


# ============================================================ TC-10 (P1)


def test_tc10_hooks_json_has_skip_offer_entry():
    """TC-10 (P1): hooks.json UserPromptSubmit 배열에 skip-offer-reminder entry 존재.

    json 파싱 후 UserPromptSubmit hook command 문자열에 'skip-offer-reminder' 포함하는
    hook 1개 이상. 주의: InfraEngineer 가 3rd entry 추가해야 통과 (TDD red→green —
    pre-GREEN HEAD 에서는 fail, 정상).

    §8.1 row TC-10. spec invariant: unconditional fire (hook wiring 등록).
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
    matches = [c for c in commands if "skip-offer-reminder" in c]
    assert len(matches) >= 1, (
        "hooks.json UserPromptSubmit 에 skip-offer-reminder entry 부재 "
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
    rc = sor.main()
    capsys.readouterr()
    assert rc == 0, f"INV-1 위반 ({label}): exit {rc}"


@pytest.mark.parametrize("label,stdin_text", _INV_INPUTS)
def test_inv2_all_inputs_emit_parseable_json(label, stdin_text, monkeypatch, capsys):
    """INV-2: 모든 입력 case stdout JSON 파싱됨 (unconditional emit — regex gate 없음)."""
    _set_stdin(monkeypatch, stdin_text)
    sor.main()
    captured = capsys.readouterr()
    assert captured.out.strip() != "", f"INV-2 위반 ({label}): 무발화"
    obj = json.loads(captured.out)  # 파싱 실패 시 fail
    assert isinstance(obj, dict), f"INV-2 위반 ({label}): dict 아님"


def test_inv3_additional_context_is_static(monkeypatch, capsys):
    """INV-3: additionalContext = 정적 (서로 다른 입력에 동일 텍스트).

    입력 무관 정적 reminder 임을 falsify — 입력에 따라 텍스트가 달라지면 (echo 등)
    실패한다.
    """
    contexts = []
    for _, stdin_text in _INV_INPUTS:
        _set_stdin(monkeypatch, stdin_text)
        sor.main()
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
def test_inv4_no_prompt_echo_to_stderr(sentinel, stdin_text, monkeypatch, capsys):
    """INV-4: stderr 에 prompt echo 0 (여러 sentinel — PII/secret 차단)."""
    _set_stdin(monkeypatch, stdin_text)
    sor.main()
    captured = capsys.readouterr()
    assert sentinel not in captured.err, f"INV-4 위반: {sentinel} stderr leak"
    # stdout additionalContext 도 정적이라 sentinel 미포함
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
    sor.main()
    captured = capsys.readouterr()
    obj = json.loads(captured.out)
    assert obj["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit", (
        f"INV-5 위반 ({label})"
    )


def test_inv6_build_reminder_all_keywords():
    """INV-6: _build_reminder() 반환에 키워드 5종 전부.

    ADR-127 / 정식 / 생략 / skip / AskUserQuestion — 4번째는 (skip OR AskUserQuestion)
    이 아니라 키워드 존재성 5종 모두를 직접 검사 (build 단위 더 엄격).
    """
    msg = sor._build_reminder()
    assert "ADR-127" in msg
    assert "정식" in msg
    assert "생략" in msg
    assert "skip" in msg
    assert "AskUserQuestion" in msg
    # system-reminder 블록 구조도 검증
    assert "<system-reminder>" in msg
    assert "</system-reminder>" in msg
