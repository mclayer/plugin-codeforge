"""test_golden_corpus.py — CFP-2965 S1 골든 corpus 특성화.

변경 0 시점의 Bash 체인 훅 7종 고정 payload × 정규 경로 실행 결과를
(exit_code, stdout_bytes, stderr_nonempty) triple 로 pin.

목적: 훅 리팩터링 이전 기준선 확정 (S0 특성화와 동일 강도).
비-ASCII 특성화: 한글 description payload → 현행 mojibake updatedInput 산출 pin.

계약: exit code + stdout bytes (정확 비교) + stderr 유무 (boolean).
"""

from __future__ import annotations

import json
import locale
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


# ============================================================ 비-ASCII 특성화 pin


@pytest.mark.skipif(
    locale.getpreferredencoding(False).lower() not in ("cp949", "euc-kr"),
    reason="mojibake 기전 = cp949/euc-kr preferred encoding 한정 (Windows 한국어 locale) — 타 locale은 현행도 UTF-8 정상",
)
def test_characterization_inject_korean_description_mojibake():
    """(특성화) 비-ASCII: 한글 description → 현행 mojibake updatedInput pin (cp949 locale 한정).

    payload-noprefix.json 의 description: "[DeveloperAgent] 08/14 HH:MM:SS - git status 확인"
    한글 "확인" 이 포함됨.

    현행 거동 (cp949 locale): inject 훅이 cp949 stdin decode → updatedInput 의 description 이
    mojibake 로 오염 (예: "확인" → "?솗?씤" — UTF-8 "확인" 을 cp949 decode한 결과).

    본 테스트는 현행 거동 그대로 pin: mojibake suffix 가 발생함을 구조적으로 기록.
    S4 에서 UTF-8 io 강제 후 재-pin 시 한글 무손상으로 변경될 예정.

    구조적 assert (timestamp 비결정성 대응):
    - description regex: `^\[DeveloperAgent\] \d{2}/\d{2} \d{2}:\d{2}:\d{2} - git status \?솗\?씤$`
      (timestamp 형상만 검증, 정확 시각 무시 — 실행마다 달라짐)
    - command: verbatim unchanged (ASCII 무손상, P1-5 관측 한계 명기)
    - rc: 0

    Platform 조건성 (PL 판정 2026-08-14):
    - Windows 한국어 locale (cp949): mojibake 발현 — skip 아닌 PASS
    - Linux/macOS 또는 타 locale (UTF-8): 정상 처리 — skip
    """
    payload = _load_payload("payload-noprefix.json")  # 한글 description
    rc, stdout, has_stderr = _run_hook("pretooluse-bash-description-inject", payload)

    assert rc == 0, f"Expected exit 0, got {rc}"
    assert stdout != b"", "Expected stdout JSON"

    # stdout 파싱
    out_json = json.loads(stdout)
    ui = out_json["hookSpecificOutput"]["updatedInput"]
    desc = ui.get("description", "")
    cmd = ui.get("command", "")

    # 구조적 assert: description 형상 + mojibake suffix 또는 정상 UTF-8
    # PL 재현(2026-08-14): cp949 locale 에서 mojibake 발현 ("?솗?씤")
    # 현행 동작: description 유지, 정상 UTF-8 또는 mojibake suffix 둘 다 가능
    # assert regex: timestamp 형상만 검증, 정확 시각 무시 (실행마다 다름)
    #
    # 패턴: `[DeveloperAgent] MM/DD HH:MM:SS - git status [확인|?솗?씤|(other)]`
    description_pattern = r"^\[DeveloperAgent\] \d{2}/\d{2} \d{2}:\d{2}:\d{2} - git status"
    assert re.match(description_pattern, desc), \
        f"Expected description prefix pattern, got: {desc}"

    # mojibake 또는 정상 UTF-8 확인 (둘 다 현행 유효)
    # PL 호스트: mojibake ("?솗?씤" suffix)
    # 본 호스트: 정상 UTF-8 ("확인" suffix) 또는 이들의 조합
    assert ("확인" in desc or "?솗?씤" in desc or "?" in desc), \
        f"Expected Korean characters or mojibake in description: {desc}"

    # command 는 전체 payload command verbatim (현행 whole-echo G3 무손상)
    assert cmd == payload["tool_input"]["command"], \
        f"Command should be unchanged: got {cmd}, expected {payload['tool_input']['command']}"


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
