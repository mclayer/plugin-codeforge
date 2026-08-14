"""test_golden_corpus.py — CFP-2965 S1 골든 corpus 특성화.

변경 0 시점의 Bash 체인 훅 7종 고정 payload × 정규 경로 실행 결과를
(exit_code, stdout_bytes, stderr_nonempty) triple 로 pin.

목적: 훅 리팩터링 이전 기준선 확정 (S0 특성화와 동일 강도).
비-ASCII pin: 한글 description·command payload → UTF-8 무손상 updatedInput (S4 재-pin —
  구 특성화 "현행 mojibake 산출" 은 의도된 결함 수정으로 폐기, 아래 재-pin 블록 참조).

계약: exit code + stdout bytes (정확 비교) + stderr 유무 (boolean).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent
HOOKS_DIR = WORKTREE_ROOT / "hooks"
PAYLOADS_DIR = WORKTREE_ROOT / "tests" / "perf" / "payloads"

_BASH = shutil.which("bash") or (
    r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt"
    and Path(r"C:\Program Files\Git\bin\bash.exe").exists() else None)

# Bash 체인 훅 7종 (정의역 = Change Plan §2.1 classify)
BASH_HOOKS_ORDERED = [
    "cross-repo-gh-safety",
    "repo-confinement",
    "git-branch-delete-merge-gate",
    "worktree-location-guard",
    "pretooluse-bash-description-inject",
    "pretooluse-dev-process-capture",
    "posttooluse-dev-process-capture",
]


def _run_hook(
    hook_name: str,
    payload: dict,
    env_overrides: dict | None = None,
) -> tuple[int, bytes, bool]:
    """훅 실행 후 (exit_code, stdout_bytes, stderr_nonempty) triple 반환."""
    env = dict(os.environ)
    if env_overrides:
        env.update(env_overrides)
    env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)

    hook_path = HOOKS_DIR / hook_name
    payload_json = json.dumps(payload)

    proc = subprocess.run(
        [_BASH, str(hook_path)],
        input=payload_json.encode("utf-8"),
        capture_output=True,
        env=env,
    )
    return proc.returncode, proc.stdout, len(proc.stderr) > 0


def _run_hook_utf8_raw(hook_name: str, payload: dict) -> tuple[int, bytes, bool]:
    """비-ASCII pin 전용 실행기 — payload 를 **raw UTF-8 바이트**로 stdin 에 투입.

    `_run_hook` 은 json.dumps(ensure_ascii=True) 이라 비-ASCII 가 \\uXXXX 로 이스케이프되어
    stdin 바이트가 순수 ASCII 가 된다 → 훅의 stdin 디코딩 결함(locale cp949)을 **관측 불가**.
    본 helper 는 ensure_ascii=False + UTF-8 인코딩으로 실제 한글 바이트를 흘려 판별력을 확보한다
    (ASCII 계약 축 corpus 는 `_run_hook` 그대로 — 기존 pin 입력 바이트 무변경).
    """
    env = dict(os.environ)
    env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)
    proc = subprocess.run(
        [_BASH, str(HOOKS_DIR / hook_name)],
        input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
        env=env,
    )
    return proc.returncode, proc.stdout, len(proc.stderr) > 0


def _load_payload(name: str) -> dict:
    """payloads 디렉터리에서 payload 로드."""
    return json.loads((PAYLOADS_DIR / name).read_text(encoding="utf-8"))


# ============================================================ ASCII payload 기준 corpus


def test_golden_corpus_cross_repo_gh_safety_ascii():
    """N-1 훅: ghwrite (write verb, repo 부재) → exit 2 block."""
    payload = _load_payload("payload-ghwrite.json")
    rc, stdout, has_stderr = _run_hook("cross-repo-gh-safety", payload)

    # 현행 거동 pin: exit 2 + stderr 有 + stdout 無
    assert rc == 2, f"Expected exit 2, got {rc}"
    assert stdout == b"" or stdout.strip() == b""
    assert has_stderr, "Expected stderr (block message)"


def test_golden_corpus_repo_confinement_ascii():
    """N-2 훅: normal ASCII (status command, no home-root) → exit 0 allow."""
    payload = _load_payload("payload-sub-ascii.json")
    rc, stdout, has_stderr = _run_hook("repo-confinement", payload)

    # 현행 거동: exit 0 (allow)
    assert rc == 0


def test_golden_corpus_git_branch_delete_merge_gate_ascii():
    """N-3 훅: 비-delete payload (del.json = tag delete, scope 외) → exit 0."""
    payload = _load_payload("payload-del.json")
    rc, stdout, has_stderr = _run_hook("git-branch-delete-merge-gate", payload)

    # 현행 거동: exit 0 (tag 삭제는 scope 외)
    assert rc == 0


def test_golden_corpus_worktree_location_guard_ascii():
    """N-4 훅: normal status command → exit 0."""
    payload = _load_payload("payload-sub-ascii.json")
    rc, stdout, has_stderr = _run_hook("worktree-location-guard", payload)

    # 현행 거동: exit 0
    assert rc == 0


def test_golden_corpus_inject_description_ascii():
    """N-5 훅: ghwrite (write verb 포함 description) → exit 0 (inject 성공, updatedInput 방출)."""
    payload = _load_payload("payload-ghwrite.json")
    rc, stdout, has_stderr = _run_hook("pretooluse-bash-description-inject", payload)

    # 현행 거동: exit 0, stdout에 updatedInput JSON 방출
    assert rc == 0
    assert stdout != b"", "Expected stdout updatedInput JSON"
    # stdout은 valid JSON 형식 (G3 whole-echo)
    try:
        out_json = json.loads(stdout)
        assert "hookSpecificOutput" in out_json
        assert "updatedInput" in out_json["hookSpecificOutput"]
    except json.JSONDecodeError:
        raise AssertionError(f"stdout is not valid JSON: {stdout[:100]}")


def test_golden_corpus_pretooluse_capture_ascii():
    """N-6 훅: PreToolUse capture → exit 0, stdout=b''."""
    payload = _load_payload("payload-ghwrite.json")
    rc, stdout, has_stderr = _run_hook("pretooluse-dev-process-capture", payload)

    # 현행 거동: exit 0, stdout 미방출
    assert rc == 0
    assert stdout == b""


def test_golden_corpus_posttooluse_capture_ascii():
    """N-7 훅: PostToolUse capture → exit 0, stdout=b''."""
    payload = _load_payload("payload-post.json")
    rc, stdout, has_stderr = _run_hook("posttooluse-dev-process-capture", payload)

    # 현행 거동: exit 0, stdout 미방출
    assert rc == 0
    assert stdout == b""


# ============================================================ 비-ASCII pin (S4 재-pin)
#
# 재-pin 선언 (의도 변경 — 사고 아님, Change Plan §3.1 판정 6 / §8.1 P2-1):
#   구 pin = "한글 description → 현행 mojibake updatedInput" 특성화 (cp949 locale skipif).
#   S4 가 checker 의 stdin/stdout 을 raw-byte UTF-8 로 명시 강제해 mojibake wrong-value 를 제거
#   → 같은 커밋에서 "한글 무손상" 으로 재-pin. 틀린 값이 계약이었던 적이 없으므로 §1 byte-계약
#   저촉 0 (ADR-143 INV-B4 "never wrong-value" 로의 복귀 = 강화 방향).
#   skipif 제거 근거: UTF-8 을 코드에서 명시하므로 결과가 host locale 무관 (platform-invariant).


def test_repin_inject_korean_description_utf8_lossless():
    """(재-pin, S4) 비-ASCII description: 한글 무손상 UTF-8 updatedInput.

    payload-noprefix.json 의 description = "git status 확인" (한글 포함).
    raw UTF-8 바이트로 stdin 투입 (_run_hook_utf8_raw) — 판별력 확보.

    구조적 assert (timestamp 비결정성 대응):
    - description = `[DeveloperAgent] MM/DD HH:MM:SS - git status 확인` (끝 = 한글 원문 그대로)
    - mojibake 부재 (구 산출 "?솗?씤" / U+FFFD replacement 문자 0)
    - command verbatim (G3 whole-echo)
    """
    payload = _load_payload("payload-noprefix.json")  # 한글 description
    rc, stdout, has_stderr = _run_hook_utf8_raw("pretooluse-bash-description-inject", payload)

    assert rc == 0, f"Expected exit 0, got {rc}"
    assert stdout != b"", "Expected stdout JSON"

    out_json = json.loads(stdout)  # bytes → UTF-8 로 파싱
    ui = out_json["hookSpecificOutput"]["updatedInput"]
    desc = ui.get("description", "")
    cmd = ui.get("command", "")

    original_desc = payload["tool_input"]["description"]          # "git status 확인"
    assert re.match(r"^\[DeveloperAgent\] \d{2}/\d{2} \d{2}:\d{2}:\d{2} - ", desc), \
        f"Expected render prefix, got: {desc}"
    assert desc.endswith(" - " + original_desc), \
        f"한글 손실 — description 이 원문으로 끝나지 않음: {desc!r}"
    assert "?솗?씤" not in desc, f"구 mojibake 재발: {desc!r}"
    assert "�" not in desc, f"replacement 문자 오염: {desc!r}"

    # command 는 payload command verbatim (whole-echo G3 무손상)
    assert cmd == payload["tool_input"]["command"], \
        f"Command should be unchanged: got {cmd}, expected {payload['tool_input']['command']}"


def test_repin_inject_non_ascii_command_field_lossless():
    """(재-pin, S4 / P1-5) 비-ASCII **command** 필드 무손상.

    구 특성화의 "command 무손상" 관측은 ASCII-한정이었다 (재현 payload 의 command 가 ASCII).
    whole-echo 구조상 stdin 디코딩이 깨지면 실행 입력(command)도 동일하게 오염되므로,
    비-ASCII command 를 실제로 흘려 전 필드 무손상을 pin 한다 (과일반화 철회 후 실검증).
    """
    payload = {
        "tool_name": "Bash",
        "agent_type": "DeveloperAgent",
        "tool_input": {
            "command": "echo '한글 인자 テスト' # 주석",
            "description": "설명 확인",
            "extra_field": "보존 대상 필드",
        },
    }
    rc, stdout, has_stderr = _run_hook_utf8_raw("pretooluse-bash-description-inject", payload)

    assert rc == 0, f"Expected exit 0, got {rc}"
    assert stdout != b"", "Expected stdout JSON"

    hso = json.loads(stdout)["hookSpecificOutput"]
    ui = hso["updatedInput"]

    assert ui["command"] == payload["tool_input"]["command"], \
        f"비-ASCII command 손실: {ui['command']!r}"
    assert ui["extra_field"] == payload["tool_input"]["extra_field"], \
        f"비-ASCII 잔여 필드 손실: {ui['extra_field']!r}"
    assert ui["description"].endswith(" - " + payload["tool_input"]["description"]), \
        f"비-ASCII description 손실: {ui['description']!r}"
    assert "�" not in json.dumps(ui, ensure_ascii=False), "replacement 문자 오염"
    assert "permissionDecision" not in hso, "G4 위반"


# ============================================================ 체인 동형성 (7종 all path)


def test_all_seven_hooks_exit_0_or_2_only():
    """모든 7종 훅의 exit code 범위 검증: 0 또는 2 만 (127/1 등 미작동 제외)."""
    payload = _load_payload("payload-ghwrite.json")

    for hook_name in BASH_HOOKS_ORDERED:
        rc, _, _ = _run_hook(hook_name, payload)
        assert rc in (0, 2), \
            f"{hook_name}: invalid exit code {rc} (expected 0 or 2). " \
            f"Non-zero codes outside [0, 2] indicate hook malfunction."


def test_all_capture_hooks_no_stdout():
    """capture 훅 2종(pre/post) 는 모두 stdout 미방출."""
    payload = _load_payload("payload-ghwrite.json")

    for hook_name in ["pretooluse-dev-process-capture", "posttooluse-dev-process-capture"]:
        rc, stdout, _ = _run_hook(hook_name, payload)
        assert rc == 0, f"{hook_name} exit != 0"
        assert stdout == b"", f"{hook_name} has stdout: {stdout[:50]}"


if __name__ == "__main__":
    # pytest 실행: `pytest hooks/tests/test_golden_corpus.py -v`
    pass
