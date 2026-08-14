"""test_check_spawn_description_prefix_inject.py — CFP-2587 Phase 2 §8 Test Contract (TDD).

계약 SSOT: Story CFP-2587 §7.10 (Test Contract) / ADR-143 Amendment 1.
Covers the injection constructor (`scripts/lib/check_spawn_description_prefix.py`):
  _sanitize_subject (G2) / build_injected_description / run_inject (--inject mode).

anti-theater (mutation 생존 0): exit-code 단독 판정 금지 — 모든 assert 는 stdout-JSON
을 json.loads 후 키/값 substring 으로 falsify. fail-open 은 "no updatedInput" 로 검증
(exit 0 만으로는 불충분 — partial updatedInput 이 없음을 명시 assert).

real-shape fixtures (ADR-006 Amd1, toy 금지): tests/spike/cfp-2587-updatedinput-honor/fixtures/*.json
= 실제 PreToolUse payload 캡처 (spike RESULTS.md). GO/NO-GO 게이트(harness honor)는 unit-testable
아님 — 여기 durable T-N 은 producer 축(우리 hook 이 올바른 JSON 을 emit 하는가)만 검증.
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

import check_spawn_description_prefix as csdp

WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES = WORKTREE_ROOT / "tests" / "spike" / "cfp-2587-updatedinput-honor" / "fixtures"
CHECKER = WORKTREE_ROOT / "scripts" / "lib" / "check_spawn_description_prefix.py"
KST_STAMP = "07/09 19:30:00"  # RE_KST_STAMP-conformant fixed stamp (with seconds, CFP-2836)
KST_STAMP_SS = "07/09 19:30:03"  # Optional-seconds variant for AC-2/4 discriminating test


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _run_inject(payload: dict, subject: str, kst_stamp: str, reminder: bool = False,
                env: dict | None = None) -> dict | None:
    """--inject 를 subprocess fork 로 실행 → stdout JSON dict (또는 stdout 없으면 None).
    exit code 도 반환 검증 위해 별도 assert (여기선 stdout 파싱만). fail-open = exit 0 always."""
    argv = [sys.executable, str(CHECKER), "--inject", "--subject", subject,
            "--kst-stamp", kst_stamp]
    if reminder:
        argv.append("--transition-reminder")
    run_env = dict(os.environ)
    if env:
        run_env.update(env)
    proc = subprocess.run(argv, input=json.dumps(payload), capture_output=True,
                          text=True, encoding="utf-8", env=run_env)
    assert proc.returncode == 0, f"fail-open 위반: exit {proc.returncode}"  # I1 exit-0-always
    out = proc.stdout.strip()
    if not out:
        return None
    # I3: 정확히 1 JSON (trailing data 없음)
    dec = json.JSONDecoder()
    obj, idx = dec.raw_decode(out)
    assert out[idx:].strip() == "", "stdout 에 2번째 JSON/trailing data 존재 (I3 위반)"
    return obj


# ── _sanitize_subject (G2) — subject-sanitize edges ──────────────────────────

@pytest.mark.parametrize("raw,expected", [
    ("ArchitectAgent", "ArchitectAgent"),
    ("codeforge-requirements:ResearcherAgent", "ResearcherAgent"),   # namespace strip
    ("my-plugin:reviewer", "reviewer"),
    ("a:b:c", "c"),                                                   # 마지막 ':' 뒤만
    ("has]bracket", "hasbracket"),                                    # ']' strip
    ("[wrapped]", "wrapped"),                                         # '[' + ']' strip
    ("X" * 100, "X" * 64),                                            # ≤64 truncate
    ("", "unknown-agent"),                                            # empty → fallback
    ("   ", "unknown-agent"),                                         # whitespace → fallback
    ("]]]", "unknown-agent"),                                         # all-bracket → fallback
])
def test_sanitize_subject(raw, expected):
    assert csdp._sanitize_subject(raw) == expected


def test_sanitize_subject_result_always_re_prefix_safe():
    """어떤 subject 든 sanitize 후 프리픽스가 RE_PREFIX 를 깨지 않음 (']' 없음·≤64)."""
    for raw in ["a]b", "x" * 200, "plug:in:name", "]", ""]:
        s = csdp._sanitize_subject(raw)
        assert "]" not in s and "[" not in s and 1 <= len(s) <= 64
        built = "[%s] %s - x" % (s, KST_STAMP)
        assert csdp.RE_PREFIX.match(built) is not None


# ── F6 (CFP-2587 Phase 2 FIX-2) — 제어문자 정규화 (단일 라인 라벨) ─────────────

def test_sanitize_subject_normalizes_control_chars():
    """F6: subject 안 개행/탭/제어문자 → 공백 (단일 라인 라벨 보장). 결과에 \\n,\\t,\\r 부재."""
    s = csdp._sanitize_subject("Foo\nBar\tBaz")
    assert "\n" not in s and "\t" not in s and "\r" not in s
    assert "Foo" in s and "Bar" in s


def test_sanitize_subject_bracket_and_control_combo_still_conformant():
    """F6: 제어문자+대괄호 혼합도 정규화 후 RE_PREFIX 안전 (주입 프리픽스가 렌더 줄 1개)."""
    built = csdp.build_injected_description("A\nB", KST_STAMP, "raw")
    assert built is not None
    assert csdp.RE_PREFIX.match(built) is not None
    assert "\n" not in built.split(" - ", 1)[0]  # 프리픽스(subject 부분)에 개행 없음


# ── build_injected_description ───────────────────────────────────────────────

def test_build_injects_prefix():
    got = csdp.build_injected_description("DeveloperAgent", KST_STAMP, "do a thing")
    assert got == "[DeveloperAgent] 07/09 19:30:00 - do a thing"
    assert csdp.RE_PREFIX.match(got) is not None  # T-5


def test_build_idempotent_returns_none():
    """T-4: 이미 conformant → None (재주입 금지, 이중 프리픽스 미발생)."""
    already = "[X] 07/09 19:30:00 - already"
    assert csdp.build_injected_description("X", KST_STAMP, already) is None


def test_build_idempotent_both_forms():
    """AC-4 idempotency양형: both old (MM/DD HH:MM) and new (MM/DD HH:MM:SS) conformant forms
    should return None (no re-injection). Mutation: guard removal → double-prefix RED."""
    # Old form (pre-CFP-2836)
    old_already = "[X] 07/09 19:30 - already conformant"
    assert csdp.build_injected_description("X", KST_STAMP, old_already) is None

    # New form (post-CFP-2836)
    new_already = "[X] 07/09 19:30:03 - already conformant"
    assert csdp.build_injected_description("X", KST_STAMP_SS, new_already) is None


def test_build_empty_or_whitespace_returns_none():
    assert csdp.build_injected_description("X", KST_STAMP, "") is None
    assert csdp.build_injected_description("X", KST_STAMP, "   ") is None
    assert csdp.build_injected_description("X", KST_STAMP, "\n\t ") is None


def test_build_invalid_kst_returns_none():
    """KST-fail skip (degradation rung 4) — invalid stamp → None.
    NOTE: "07/09 19:30:00" is VALID (optional-seconds after CFP-2836), removed from bad-list."""
    for bad in ["", "2026-07-09T19:30:00Z", "7/9 19:30", "garbage"]:
        assert csdp.build_injected_description("X", bad, "content") is None


def test_build_invalid_kst_seconds_malformed():
    """AC-2 bidirectional mutation-lock: 초 자릿수/콜론 오류 strictly nonconformant.
    mutation: RE_KST_STAMP을 (:\\d{1,3})?로 over-broad 하거나 \\d{1,2}로 완화 → RED
    (single-digit/3-digit/missing-colon-sep 통과 = false-positive)."""
    # Single-digit seconds: "14:30:3" 또는 "07/09 14:30:3"
    malformed = ["07/09 14:30:3", "07/09 14:30:030", "07/09 14:30::", "07/09 14:30: 00"]
    for bad in malformed:
        result = csdp.build_injected_description("X", bad, "content")
        assert result is None, f"malformed KST '{bad}' should reject (AC-2 bidirectional)"


def test_build_valid_kst_with_optional_seconds():
    """AC-2 positive case: optional-seconds accept both MM/DD HH:MM and MM/DD HH:MM:SS.
    After CFP-2836, both forms are conformant."""
    # Old form (HH:MM only, no seconds)
    old_form = "07/09 19:30"
    got_old = csdp.build_injected_description("X", old_form, "old action")
    assert got_old is not None and "[X] 07/09 19:30 - old action" in got_old

    # New form (HH:MM:SS with seconds)
    new_form = KST_STAMP_SS  # "07/09 19:30:03"
    got_new = csdp.build_injected_description("X", new_form, "new action")
    assert got_new is not None and "[X] 07/09 19:30:03 - new action" in got_new


def test_re_prefix_matches_both_old_and_new_forms():
    r"""AC-3 RE_PREFIX acceptor backward-compat: both old (HH:MM) and new (HH:MM:SS)
    are conformant to RE_PREFIX regex. Mutation: seconds optional removal (:\d{2})? → mandatory
    or complete removal → RED (old-form rejection)."""
    # Old form conformant
    old_prefix = "[ArchitectAgent] 07/05 14:30 - old form"
    assert csdp.RE_PREFIX.match(old_prefix) is not None, "old form HH:MM should match"

    # New form conformant
    new_prefix = "[ArchitectAgent] 07/05 14:30:45 - new form"
    assert csdp.RE_PREFIX.match(new_prefix) is not None, "new form HH:MM:SS should match"

    # Malformed (incomplete seconds) non-conformant
    malformed = "[ArchitectAgent] 07/05 14:30:4 - incomplete second"
    assert csdp.RE_PREFIX.match(malformed) is None, "incomplete second should NOT match"


def test_build_leading_space_content_still_conformant():
    """lstrip 으로 `- ` 직후 \\S 보장 → RE_PREFIX-conformant."""
    got = csdp.build_injected_description("X", KST_STAMP, "   leading spaces")
    assert got == "[X] 07/09 19:30:00 - leading spaces"
    assert csdp.RE_PREFIX.match(got) is not None


# ── F2 (CFP-2587 Phase 2 FIX-2) — leading-ws idempotency (double-stamp 방지) ──

def test_build_injected_leading_ws_already_conformant_skips():
    """F2/§11.6: leading-ws + 이미 conformant → None (double-stamp 방지, f(f(x))=f(x)).
    lstrip 후 conformance 판정이므로 선행 공백이 있어도 재주입 SKIP."""
    out = csdp.build_injected_description("Dev", KST_STAMP, "  [ResearcherAgent] 07/09 19:30 - x")
    assert out is None


def test_build_injected_leading_ws_nonconformant_injects_once():
    """F2: leading-ws + nonconformant → 1회 주입, 프리픽스 정확히 1개([Dev]) — content 는 lstrip 적용."""
    out = csdp.build_injected_description("Dev", KST_STAMP, "   raw content")
    assert out is not None and out.startswith("[Dev] 07/09 19:30:00 - raw content")
    assert out.count("[Dev]") == 1


def test_build_result_passes_single_regex_ssot():
    """T-5: inject 결과가 SSOT check_description 통과 (재구현 regex 아님)."""
    got = csdp.build_injected_description("codeforge-requirements:ResearcherAgent",
                                         KST_STAMP, "some action")
    assert got.startswith("[ResearcherAgent] ")
    res = csdp.check_description(got)
    assert res["description_prefix_conformant"] is True and res["empty"] is False


# ── run_inject (--inject) — T-1 REPLACE-safety (TOP PRIORITY) ────────────────

def test_inject_whole_echo_preserves_all_args_bash():
    """T-1 (AC-4/5/6): real-shape Bash payload → command 등 verbatim 보존 + description prefixed.
    RED(naive description-only)=arg 소실 / GREEN(whole-echo)."""
    payload = _load_fixture("bash-in-subagent.json")
    payload["tool_input"]["timeout"] = 120000
    payload["tool_input"]["run_in_background"] = False
    orig_cmd = payload["tool_input"]["command"]
    obj = _run_inject(payload, "general-purpose", KST_STAMP)
    ui = obj["hookSpecificOutput"]["updatedInput"]
    # whole-echo: 모든 원 인자 보존 (I2)
    assert ui["command"] == orig_cmd
    assert ui["timeout"] == 120000
    assert ui["run_in_background"] is False
    # description = stamped prefix + original
    assert ui["description"].startswith("[general-purpose] 07/09 19:30:00 - ")
    assert csdp.RE_PREFIX.match(ui["description"]) is not None
    # G4: NO permissionDecision
    assert "permissionDecision" not in obj["hookSpecificOutput"]


def test_inject_agent_whole_echo_preserves_prompt_subagent_type():
    payload = _load_fixture("agent-spawn.json")
    orig_prompt = payload["tool_input"]["prompt"]
    orig_sub = payload["tool_input"]["subagent_type"]
    obj = _run_inject(payload, orig_sub, KST_STAMP)
    ui = obj["hookSpecificOutput"]["updatedInput"]
    assert ui["prompt"] == orig_prompt
    assert ui["subagent_type"] == orig_sub
    assert ui["description"].startswith("[%s] " % csdp._sanitize_subject(orig_sub))


# ── T-2 source-branching (constructor side — subject arg → correct prefix) ────

def test_inject_subject_arg_verbatim_after_sanitize():
    """T-2(b): namespace-scoped subject → strip 후 프리픽스."""
    payload = {"tool_name": "Bash", "agent_type": "codeforge-requirements:ResearcherAgent",
               "tool_input": {"command": "ls", "description": "list"}}
    obj = _run_inject(payload, "codeforge-requirements:ResearcherAgent", KST_STAMP)
    ui = obj["hookSpecificOutput"]["updatedInput"]
    assert ui["description"].startswith("[ResearcherAgent] ")
    assert ui["command"] == "ls"


# ── dispatch 위치 인식 (CFP-2965 F6) ─────────────────────────────────────────

def test_dispatch_position_aware_subject_equal_to_mode_literal():
    """subject 값이 모드 리터럴("--inject-bash") 과 같아도 --inject 경로를 유지한다.

    구 dispatch 는 `"--inject-bash" in argv` (position-blind 멤버십) 라
    `--inject --subject "--inject-bash"` 호출이 Bash 표면(run_inject_bash)으로 새고,
    Agent payload 는 그 쪽 tool_name/agent_type 가드에 걸려 **주입이 통째로 소실**됐다.
    값-위치 shadowing 은 _scan_argv 가 봉합했지만 dispatch 는 그 밖이었다.

    판별 지표 2:
      (1) additionalContext 존재 — run_inject(Agent 표면)만 emit (bash 모드엔 경로 부재)
      (2) updatedInput 이 subject 프리픽스로 stamped + 원 인자 verbatim (주입 소실 0)
    """
    payload = _load_fixture("agent-spawn.json")
    orig_prompt = payload["tool_input"]["prompt"]

    obj = _run_inject(payload, "--inject-bash", KST_STAMP, reminder=True)
    assert obj is not None, "stdout 부재 — --inject-bash 로 오분기해 주입이 소실됐다"
    hso = obj["hookSpecificOutput"]

    # (1) Agent 표면 경로 확정
    assert "additionalContext" in hso, (
        "run_inject 경로가 아니다 — subject 값이 모드 리터럴이라 오분기 "
        "(position-blind dispatch 회귀)"
    )
    # (2) 주입 소실 0 + whole-echo 보존
    ui = hso["updatedInput"]
    assert ui["prompt"] == orig_prompt
    assert ui["description"].startswith("[--inject-bash] %s - " % KST_STAMP)
    assert csdp.RE_PREFIX.match(ui["description"]) is not None
    assert "permissionDecision" not in hso  # G4 무손상


def test_detect_mode_not_hijacked_by_mode_literal_in_value_position():
    """detect 모드(--description-stdin) 가 뒤따르는 모드 리터럴에 납치되지 않는다.

    구 코드: `"--inject" in argv` 멤버십이 참이 되어 run_inject 로 새고, stdin 이
    PreToolUse JSON 이 아니라 fail-open(무출력) → detect 산출이 사라진다.
    """
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--description-stdin", "--subject", "--inject"],
        input="[X] 07/09 19:30:00 - ok", capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0
    out = proc.stdout.strip()
    assert out, "detect 산출 부재 — --inject 로 오분기 (position-blind dispatch 회귀)"
    obj = json.loads(out)
    assert "description_prefix_conformant" in obj, f"detect 산출이 아니다: {obj}"
    assert "hookSpecificOutput" not in obj, "inject 산출이 섞였다 (모드 오분기)"


# ── T-3 merge (Agent surface — single JSON, both keys) ───────────────────────

def test_inject_reminder_merge_single_json_both_keys():
    """T-3: --transition-reminder + nonconformant → 1 JSON with updatedInput AND additionalContext."""
    payload = _load_fixture("agent-spawn.json")
    obj = _run_inject(payload, payload["tool_input"]["subagent_type"], KST_STAMP, reminder=True)
    hso = obj["hookSpecificOutput"]
    assert "updatedInput" in hso
    assert "additionalContext" in hso
    assert "story-transition-autonomy" in hso["additionalContext"]
    assert "permissionDecision" not in hso  # NEVER deny


def test_inject_reminder_unconditional_when_conformant():
    """T-3 회귀가드 (§7.3 LOAD-BEARING): 이미-conformant → updatedInput SKIP 이나 additionalContext 여전히 present."""
    payload = {"tool_name": "Agent",
               "tool_input": {"subagent_type": "X", "prompt": "p",
                              "description": "[X] 07/09 19:30 - already"}}
    obj = _run_inject(payload, "X", KST_STAMP, reminder=True)
    hso = obj["hookSpecificOutput"]
    assert "updatedInput" not in hso                 # idempotent skip
    assert "story-transition-autonomy" in hso["additionalContext"]  # reminder 잔존


# ── T-6 fail-open ────────────────────────────────────────────────────────────

def test_inject_malformed_json_fail_open_no_updated_input():
    """T-6: malformed stdin → exit 0, NO updatedInput (원 args intact)."""
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--inject", "--subject", "X", "--kst-stamp", KST_STAMP],
        input="{not json", capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0
    out = proc.stdout.strip()
    # no reminder → 완전 no stdout (partial updatedInput 절대 없음)
    assert out == "" or "updatedInput" not in json.loads(out).get("hookSpecificOutput", {})


def test_inject_malformed_json_with_reminder_emits_reminder_only():
    """T-6: malformed stdin + --transition-reminder → reminder-only (updatedInput 없음), exit 0."""
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--inject", "--subject", "X", "--kst-stamp",
         KST_STAMP, "--transition-reminder"],
        input="{not json", capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0
    hso = json.loads(proc.stdout.strip())["hookSpecificOutput"]
    assert "updatedInput" not in hso                  # never partial
    assert "story-transition-autonomy" in hso["additionalContext"]


def test_inject_empty_description_no_updated_input():
    payload = {"tool_name": "Bash", "agent_type": "A",
               "tool_input": {"command": "ls", "description": ""}}
    obj = _run_inject(payload, "A", KST_STAMP)
    assert obj is None  # skip → no stdout


def test_inject_bypass_skips_updated_input_but_keeps_reminder():
    payload = _load_fixture("agent-spawn.json")
    obj = _run_inject(payload, "X", KST_STAMP, reminder=True,
                      env={"BYPASS_CODEFORGE_PRETOOLUSE_AGENT_GATE": "1"})
    hso = obj["hookSpecificOutput"]
    assert "updatedInput" not in hso
    assert "story-transition-autonomy" in hso["additionalContext"]


# ── T-7 TZ-invariance (AC-13) ────────────────────────────────────────────────

def test_kst_stamp_tz_invariant():
    """T-7: kst_render_stamp.py 는 TZ 무관하게 동일 --epoch 에 동일 stamp (UTC+9 고정 산술)."""
    kst_py = WORKTREE_ROOT / "scripts" / "lib" / "kst_render_stamp.py"
    epoch = "1751000000"  # 고정 instant
    outs = set()
    for tz in ["UTC", "America/New_York", "Asia/Seoul", "Pacific/Kiritimati"]:
        env = dict(os.environ); env["TZ"] = tz
        p = subprocess.run([sys.executable, str(kst_py), "--epoch", epoch],
                           capture_output=True, text=True, encoding="utf-8", env=env)
        assert p.returncode == 0
        outs.add(p.stdout.strip())
    assert len(outs) == 1, f"TZ-variant stamps differ: {outs}"


# ── Perf (§8.3) — single-fork < 500ms/dispatch ───────────────────────────────

def test_inject_single_fork_perf_under_500ms():
    """§8.3: single --inject fork wall-time < 500ms (single-fork mandate). 실측 — 가정 금지.
    노트: cold-start python fork 포함. 값을 stdout 으로 남겨 회귀 관측."""
    payload = _load_fixture("bash-in-subagent.json")
    best = min(_time_one(payload) for _ in range(3))  # best-of-3 (noise 완화)
    print(f"\n[PERF] single --inject fork best-of-3 = {best*1000:.1f} ms")
    assert best < 0.5, f"single-fork {best*1000:.1f}ms >= 500ms (perf 회귀)"


def _time_one(payload: dict) -> float:
    t0 = time.perf_counter()
    subprocess.run([sys.executable, str(CHECKER), "--inject", "--subject",
                    "general-purpose", "--kst-stamp", KST_STAMP],
                   input=json.dumps(payload), capture_output=True, text=True, encoding="utf-8")
    return time.perf_counter() - t0


# ── back-compat: --description-stdin 무회귀 ──────────────────────────────────

def test_backcompat_description_stdin_unchanged():
    proc = subprocess.run([sys.executable, str(CHECKER), "--description-stdin"],
                          input="foo", capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0
    res = json.loads(proc.stdout.strip())
    assert res["description_prefix_conformant"] is False and res["empty"] is False


# ── CFP-2599 P2×2 하드닝 mutation-lock (§8 Test Contract TC1-5) ────────────────
#   D1: _sanitize_subject Unicode 개행(U+0085 NEL/U+2028 LS/U+2029 PS) 접힘 (정규식 클래스 확장).
#   D2: run_inject positional-safe argv 스캐너 (first-match value-shadow + position-blind 멤버십 봉합).
#   mutation-lock = fix 원복 시 RED (각 docstring 에 RED 조건 명시).
#   NOTE: 개행류는 escape 표기(\x85/\u2028/\u2029)로만 기술 — 소스에 raw line separator 미주입.

# subject 중간(미들 배치) — trailing 개행류는 .strip() 이 접어 mutation 없이도 라벨 1줄(hollow).
# 미들 배치라야 D1 delta 를 discriminate (설계 §9.2 ④ 실증).
UNICODE_NL_MIDDLE = ["\x85", "\u2028", "\u2029"]


@pytest.mark.parametrize("c", UNICODE_NL_MIDDLE)
def test_tc1_sanitize_unicode_newline_folds_to_single_line(c):
    """TC1/AC-1/AC-3 (D1 mutation-lock): 미들 배치 Unicode 개행 → 단일 공백, splitlines len 1.
    mutation(클래스에서 \\x85\\u2028\\u2029 제거 원복) → c 잔존 → splitlines 2 → FAIL."""
    s = csdp._sanitize_subject("A" + c + "B")
    assert c not in s
    assert len(s.splitlines()) == 1
    assert s == "A B"          # 개행 → 단일 공백 (정규식 확장: 내부공백 collapse 부수효과 부재)


@pytest.mark.parametrize("c", UNICODE_NL_MIDDLE)
def test_tc1_build_label_single_render_line(c):
    """TC1/AC-2 (D1 mutation-lock): 라벨 프리픽스가 미들 Unicode 개행에도 정확히 1 렌더 줄.
    mutation 원복 시 built.splitlines() == 2 → FAIL."""
    built = csdp.build_injected_description("A" + c + "B", KST_STAMP, "raw action")
    assert built is not None
    assert len(built.splitlines()) == 1
    assert built == "[A B] 07/09 19:30:00 - raw action"
    assert csdp.RE_PREFIX.match(built) is not None


def _bash_payload(desc: str = "raw action") -> dict:
    """Bash surface payload — 실제 --transition-reminder/--subject-absent flag 미전달 표면."""
    return {"tool_name": "Bash", "agent_type": "x",
            "tool_input": {"command": "ls", "description": desc}}


def test_tc2a_reminder_value_shadow_no_excess_reminder():
    """TC2a/AC-5 (D2 mutation-lock): Bash surface(실제 --transition-reminder flag 미전달) +
    subject 값 == '--transition-reminder' 리터럴 → additionalContext 부재(잉여 reminder 0),
    description 은 sanitized subject 로 정상 주입.
    mutation('--transition-reminder' in argv 멤버십 원복) → 잉여 reminder emit → FAIL."""
    obj = _run_inject(_bash_payload(), "--transition-reminder", KST_STAMP)  # reminder=False
    assert obj is not None
    hso = obj["hookSpecificOutput"]
    assert "additionalContext" not in hso          # 값-위치 리터럴이 flag 로 오인 안 됨
    assert hso["updatedInput"]["description"] == "[--transition-reminder] 07/09 19:30:00 - raw action"
    assert hso["updatedInput"]["command"] == "ls"  # whole-echo 보존 (I2)


def test_tc2b_subject_absent_value_shadow_still_injects():
    """TC2b/AC-6 (D2 mutation-lock, 최악 fail-open): subject 값 == '--subject-absent' 리터럴이고
    실제 --subject-absent flag 미전달 → injection SKIP 되지 않음(정상 주입).
    mutation('--subject-absent' in argv 멤버십 원복) → subject_absent 오판 → injection SKIP
    (updatedInput 부재 = 프리픽스 미주입) → FAIL."""
    obj = _run_inject(_bash_payload(), "--subject-absent", KST_STAMP)
    assert obj is not None                         # skip 안 됨
    assert obj["hookSpecificOutput"]["updatedInput"]["description"] == \
        "[--subject-absent] 07/09 19:30:00 - raw action"


def test_tc2c_kst_stamp_value_shadow_first_match_reads_valid_stamp():
    """TC2c (D2 mutation-lock): subject 값 == '--kst-stamp' 리터럴 + 실제 --kst-stamp <valid> →
    positional 소비로 valid stamp 읽힘(정상 주입).
    mutation(argv.index first-match 원복) → subject-값 위치의 '--kst-stamp' 를 stamp 로 오독 →
    stamp='--kst-stamp' invalid → KST-fail skip(updatedInput 부재) → FAIL."""
    obj = _run_inject(_bash_payload(), "--kst-stamp", KST_STAMP)
    assert obj is not None                         # KST-fail skip 아님
    assert obj["hookSpecificOutput"]["updatedInput"]["description"] == \
        "[--kst-stamp] 07/09 19:30:00 - raw action"


def test_tc4_empty_subject_unknown_agent_fallback_single_line():
    """TC4 (N2 empty-string 문서 lock — F4 정직 표기: D1/D2 delta mutation-lock 아님;
    D1/D2 delta lock 은 TC1/TC2a-c). empty subject → UNKNOWN_AGENT fallback, splitlines len 1.
    fallback 제거 mutation 시 출력 empty → splitlines len 0 → FAIL (AC-3 정밀화: non-empty 후 len 1)."""
    assert csdp._sanitize_subject("") == csdp.UNKNOWN_AGENT
    assert csdp._sanitize_subject("").splitlines() == ["unknown-agent"]
    assert len(csdp.UNKNOWN_AGENT.splitlines()) == 1


def test_tc5_ec2_mixed_ascii_and_unicode_newline_single_line():
    """TC5/EC-2 (무회귀): ASCII '\\n' + Unicode U+2028 혼합 개행 동시 → 모두 공백, 라벨 1 렌더 줄.
    (정상 경로 whole-echo/idempotent/fail-open/KST-invalid/back-compat 무회귀는 파일 전체 스위트 담보.)"""
    built = csdp.build_injected_description("A\nB\u2028C", KST_STAMP, "raw action")
    assert built is not None
    assert len(built.splitlines()) == 1
    assert built == "[A B C] 07/09 19:30:00 - raw action"
    assert csdp.RE_PREFIX.match(built) is not None
