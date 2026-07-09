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
KST_STAMP = "07/09 19:30"  # RE_KST_STAMP-conformant fixed stamp


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


# ── build_injected_description ───────────────────────────────────────────────

def test_build_injects_prefix():
    got = csdp.build_injected_description("DeveloperAgent", KST_STAMP, "do a thing")
    assert got == "[DeveloperAgent] 07/09 19:30 - do a thing"
    assert csdp.RE_PREFIX.match(got) is not None  # T-5


def test_build_idempotent_returns_none():
    """T-4: 이미 conformant → None (재주입 금지, 이중 프리픽스 미발생)."""
    already = "[X] 07/09 19:30 - already"
    assert csdp.build_injected_description("X", KST_STAMP, already) is None


def test_build_empty_or_whitespace_returns_none():
    assert csdp.build_injected_description("X", KST_STAMP, "") is None
    assert csdp.build_injected_description("X", KST_STAMP, "   ") is None
    assert csdp.build_injected_description("X", KST_STAMP, "\n\t ") is None


def test_build_invalid_kst_returns_none():
    """KST-fail skip (degradation rung 4) — invalid stamp → None."""
    for bad in ["", "2026-07-09T19:30:00Z", "7/9 19:30", "07/09 19:30:00", "garbage"]:
        assert csdp.build_injected_description("X", bad, "content") is None


def test_build_leading_space_content_still_conformant():
    """lstrip 으로 `- ` 직후 \\S 보장 → RE_PREFIX-conformant."""
    got = csdp.build_injected_description("X", KST_STAMP, "   leading spaces")
    assert got == "[X] 07/09 19:30 - leading spaces"
    assert csdp.RE_PREFIX.match(got) is not None


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
    assert ui["description"].startswith("[general-purpose] 07/09 19:30 - ")
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
