"""test_subagent_start_progress_commit_priming.py — CFP-2966 Phase 2 / CP §8.2.5(b) INV-T10.

계약 SSOT: Change Plan CFP-2966 §8.2.5(b) (구현리뷰 Iter1 F-2 → ArchitectPL 설계 판정으로
additive 신설된 test-axis) / ADR-178 §결정 2·5·12 / ADR-115 Amendment 2 §결정 5 (fail-open).

SubagentStart priming 훅 = pointer-only. stdin JSON payload 를 받아 progress-commit 규범
pointer 를 additionalContext 로 emit 한다 (filesystem·network·git 조작 0).

INV-T10 행동 계약 3케이스:
  ① 정상 payload  → additionalContext **내용 대조** (emit 3요소 — presence 단독 금지)
  ② 빈·깨진 stdin → rc=0 ∧ 무출력 (fail-open — 세션 차단 0)
  ③ python 부재   → rc=0 (emit 경로 결손이지만 세션 미차단)

born-hollow 방지 3조건 (CFP-2799 교훈 — sibling test_subagent_start_render_discipline 답습):
  (i)  대상 분기 실도달 fixture ✓ — ③ 은 PATH 에서 python 보유 디렉터리를 제거한 뒤
       **hook 이 실제로 python 을 못 찾는지 precondition 으로 검증**한다 (못 찾게 만들지
       못했으면 skip — 다른 이유로 통과하는 wrong-reason PASS 금지).
  (ii) assert = additionalContext **내용** 명시 대조 ✓ — 존재-여부 단독 금지 +
       CP §8.2.5(c) 흡수-방지 불변식(조각 출현 정확히 1회).
  (iii) mutant RED firsthand — **실증 범위를 명시한다** (무조건부 단정 금지):
       실행으로 RED 를 확인한 변조는 아래 4종이다 —
         h1 산문 ADR 번호 변조 / h2 적재 단위 의미 반전(의미 단위→시간 주기) /
         h3 정본 경로 변조 / h4 subject 템플릿 변조.
       ★ "문면을 변조하면 RED" 라는 **무조건부 일반화는 하지 않는다** — Iter 1 커밋에서
         mutant 1종(h3)만 실행하고 전체로 일반화했다가 Iter 2 에서 h1·h2 가 7 passed 로
         생존해 반증됐다 (F-CR-201). 조각이 덮지 않는 문면 변조는 여전히 미검출이다
         (CP §8.2.5(d) 천장 — 조각-국소 보장이지 문면 전역 봉인이 아님).

anti-theater: stdout 전체가 유효 JSON 1건인지 + hookSpecificOutput 형상 + 내용 문자열 정합.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import pytest


WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent
HOOK_SCRIPT = WORKTREE_ROOT / "hooks" / "subagent-start-progress-commit-priming"

_BASH = shutil.which("bash") or (
    r"C:\Program Files\Git\bin\bash.exe" if os.name == "nt"
    and Path(r"C:\Program Files\Git\bin\bash.exe").exists() else None)

pytestmark = pytest.mark.skipif(_BASH is None, reason="bash interpreter 부재 (non-Git-Bash CI)")

_PY_NAMES = ("python3", "python3.exe", "python", "python.exe")

# 판별 조각 — CP §8.2.5(c) 흡수-방지 불변식 + §8.2.5(d) 대조 대상 확정.
#
# 계약 (d) 가 확정한 emit 3요소 = 규범 pointer · subject 형식 · 정본 위치
#   (구 문면의 "self명·앵커" 는 sibling render-discipline 훅에서 전사된 오기재 — 본 훅은 emit 하지
#    않는다. 존재하지 않는 요소의 대조 요구를 제거한 것이지 요건 추가가 아니다.)
#   ★ 규범 pointer 요소만 **2 리터럴로 앵커**한다 — 식별 축(ADR 번호+결정 번호)과 적재 단위 축
#     (의미 단위 vs 시간 주기)이 서로 다른 변조 표적이라 한 리터럴로는 둘 다 못 잡는다
#     (Iter 2 실증: h1 = 식별 축 변조 / h2 = 적재 단위 축 의미 반전). 요소는 3, 리터럴은 4.
#
# 조각 선정 규칙 (CP §8.2.5(c)) — **라인-앵커형**: 각 조각은 대조 컨텍스트에서 정확히 1회만
#   출현해야 한다. 짧은 토큰(`ADR-178`, `의미 단위`)은 정본 경로·subject 템플릿에 재출현해
#   count 2 가 되고, 그러면 그 축을 변조해도 다른 출현이 대조를 **흡수**해 비판별이 된다
#   (Iter 2 F-CR-201 실측: h1·h2 둘 다 7 passed 생존). 아래 assert 가 이 성질을 기계 고정한다.
#
# 천장 (CP §8.2.5(d)): 본 불변식은 **조각이 덮는 문면에 한해** 판별을 보장한다. 조각이 덮지
#   않는 문면 변조는 여전히 미검출이며, "훅 문면이 기계적으로 봉인된다" 를 주장하지 않는다.
_EXPECTED_FRAGMENTS = (
    "ADR-178 §결정 2/5/12",                                        # 규범 pointer — 식별 축
    "atomic 의미 단위 경계마다",                                    # 규범 pointer — 적재 단위 축
    "Subject: [CFP-NNN][WIP]",                                     # subject 형식
    "archive/adr/ADR-178-subagent-progress-commit-preservation.md",  # 정본 위치
)


def _run_hook(payload: Optional[str] = None,
              env_override: Optional[dict] = None) -> tuple[int, str, str]:
    """hook 을 subprocess 로 bash 실행 — stdin 에 payload 주입. (rc, stdout, stderr)."""
    if not HOOK_SCRIPT.exists():
        pytest.fail(f"hook script 부재: {HOOK_SCRIPT} (CP §5 Phase 2 산출물)")
    run_env = dict(os.environ)
    run_env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)
    if env_override:
        run_env.update(env_override)
    proc = subprocess.run(
        [_BASH, str(HOOK_SCRIPT)],
        input=payload or "",
        capture_output=True,
        text=True,
        env=run_env,
        timeout=30,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _executable_lines(body: Optional[str] = None) -> list:
    """훅 본문에서 **실행 라인**만 추출 (주석 + additionalContext 문자열 블록 제외).

    훅이 서브에이전트에게 **전달하는** 텍스트에는 'git commit' 이 등장한다 (그게 규범 문면이다).
    그것을 훅 자신의 동작으로 오독하면 검사가 무의미해지므로, `ADDITIONAL_CONTEXT="` 부터
    닫는 따옴표 라인까지의 문자열 리터럴 블록을 **범위로** 제외한다 (라인별 문자열 매칭 금지 —
    우선순위 실수로 정작 위반 라인이 빠지는 취약 필터를 피한다).
    """
    if body is None:
        body = HOOK_SCRIPT.read_text(encoding="utf-8")
    out, in_ctx = [], False
    for ln in body.splitlines():
        if not in_ctx and ln.startswith("ADDITIONAL_CONTEXT="):
            in_ctx = True
            continue
        if in_ctx:
            if ln.rstrip().endswith('"'):      # 문자열 리터럴 종료
                in_ctx = False
            continue
        if ln.lstrip().startswith("#"):
            continue
        if ln.strip():
            out.append(ln)
    return out


def _path_without_python() -> Optional[str]:
    """현재 PATH 에서 python 실행파일을 보유한 디렉터리만 제거한 PATH 를 만든다.

    PATH 를 통째로 비우면 `cat` 마저 사라져 **다른 이유로** 조기 exit 0 하는
    wrong-reason PASS 가 된다 (born-hollow (i) 위반). 따라서 python 보유 디렉터리만 뺀다.
    """
    kept = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue
        d = Path(entry)
        try:
            has_py = any((d / n).exists() for n in _PY_NAMES)
        except OSError:
            has_py = False
        if not has_py:
            kept.append(entry)
    return os.pathsep.join(kept) if kept else None


# ── ① 정상 payload — additionalContext 내용 대조 ────────────────────────────────

def test_normal_payload_emits_progress_commit_pointer():
    """INV-T10 ①: 유효 SubagentStart payload → 규범 pointer 를 담은 유효 JSON 1건 emit."""
    payload = json.dumps({
        "hook_event_name": "SubagentStart",
        "agent_type": "codeforge-develop:QADeveloperAgent",
    })
    rc, out, _err = _run_hook(payload)

    assert rc == 0, f"fail-open 위반 — rc={rc}"
    assert out.strip(), "정상 payload 인데 무출력 (priming 미도달)"

    parsed = json.loads(out)  # stdout 전체가 유효 JSON 1건이어야 한다
    assert "hookSpecificOutput" in parsed, f"hookSpecificOutput 부재: {parsed}"
    hso = parsed["hookSpecificOutput"]
    assert hso.get("hookEventName") == "SubagentStart", (
        f"hookEventName 불일치: {hso.get('hookEventName')!r}")

    ctx = hso.get("additionalContext", "")
    assert ctx, "additionalContext 공백 — pointer 미전달"
    for frag in _EXPECTED_FRAGMENTS:
        # CP §8.2.5(c) 흡수-방지 불변식 — presence 가 아니라 **정확히 1회** 를 요구한다.
        #   count 0 = 문면 표류(변조) / count >= 2 = 조각이 흡수 가능해져 판별력 상실.
        occurrences = ctx.count(frag)
        assert occurrences == 1, (
            f"판별 조각 {frag!r} 출현 {occurrences}회 (정확히 1회여야 한다).\n"
            f"  0회 = 훅 문면 표류/변조 · 2회 이상 = 다른 출현이 변조를 흡수해 비판별화\n"
            f"  (Iter 2 F-CR-201: 짧은 토큰 'ADR-178'·'의미 단위' 가 각각 정본 경로·subject "
            f"템플릿에 재출현해 h1·h2 를 흡수했다)\n"
            f"실제 additionalContext={ctx!r}")


# ── ② 빈·깨진 stdin — rc=0 ∧ 무출력 ────────────────────────────────────────────

@pytest.mark.parametrize("payload,label", [
    ("", "빈 stdin"),
    ("{not json", "깨진 JSON"),
    ("  \n\t ", "공백만"),
])
def test_broken_stdin_is_fail_open_and_silent(payload: str, label: str):
    """INV-T10 ②: 입력 결손 → rc=0 ∧ 무출력 (세션 차단 0, 부분 JSON 오염 0)."""
    rc, out, _err = _run_hook(payload)
    assert rc == 0, f"{label}: fail-open 위반 — rc={rc} (훅이 세션을 막으면 안 된다)"
    assert out.strip() == "", (
        f"{label}: 무출력이어야 하는데 stdout 존재 — 부분/무효 JSON 오염 위험: {out!r}")


def test_non_object_json_payload_stays_wellformed():
    """`null` 처럼 **유효 JSON 이지만 객체가 아닌** 입력의 실거동 고정 (관찰 기록).

    CP §8.2.5(b) ② 의 계약 문면은 "빈·깨진 stdin" 이다. `null` 은 둘 다 아니라서
    훅은 파싱에 성공하고 pointer 를 emit 한다 (실측). 이는 계약 위반이 아니다 —
    실 harness 는 항상 객체를 보내므로 도달하지 않는 입력이다.
    따라서 "무출력" 을 강제하지 않고(= 계약 밖 요구 신설 금지), **오염 부재**만 고정한다:
    출력이 있다면 반드시 유효 JSON 1건 + 올바른 형상이어야 한다.
    (객체 여부 검증 추가는 설계 판정 사항 — DevPL 자체 결정 금지, 관찰만 보고)
    """
    rc, out, _err = _run_hook("null")
    assert rc == 0, f"fail-open 위반 — rc={rc}"
    if out.strip():
        parsed = json.loads(out)  # 부분/무효 JSON 오염 금지
        assert parsed.get("hookSpecificOutput", {}).get("hookEventName") == "SubagentStart"


# ── ③ python 부재 — rc=0 (emit 경로 결손이지만 fail-open) ───────────────────────

def test_missing_python_degrades_fail_open():
    """INV-T10 ③: python 부재 환경 → rc=0 (무출력 degrade, 세션 미차단).

    precondition 검증 포함 — PATH 조작으로 실제 python 이 사라졌는지 먼저 확인한다.
    """
    stripped = _path_without_python()
    if stripped is None:
        pytest.skip("PATH 전 항목이 python 보유 — 부재 시뮬 불가")

    # precondition: 이 PATH 에서 python 이 정말 안 잡히는가 (wrong-reason PASS 차단)
    probe = subprocess.run(
        [_BASH, "-c", "command -v python3 || command -v python || echo __NOPY__"],
        capture_output=True, text=True, env={**os.environ, "PATH": stripped}, timeout=30)
    if "__NOPY__" not in probe.stdout:
        pytest.skip(f"python 부재 시뮬 실패 (여전히 해결됨: {probe.stdout.strip()!r})")

    payload = json.dumps({"hook_event_name": "SubagentStart", "agent_type": "DeveloperAgent"})
    rc, out, _err = _run_hook(payload, env_override={"PATH": stripped})

    assert rc == 0, f"python 부재 시 fail-open 위반 — rc={rc}"
    assert out.strip() == "", (
        f"python 부재인데 stdout 존재 — emit 경로가 python 단일 경로라는 헤더 (d) 와 불일치: {out!r}")


# ── 훅 정적 property 회귀 (헤더 선언 ↔ 실물) ─────────────────────────────────────

def test_hook_performs_no_git_or_filesystem_mutation():
    """헤더 (b) 선언 회귀: 영속 filesystem 변경·git 조작 0.

    CFP-2966 구현리뷰 Iter1 P2 ④ — 이 훅의 rationale/헤더가 "worktree snapshot + git commit"
    으로 오기재됐던 전례가 있다. 실물이 pointer-only 임을 기계로 고정한다.
    """
    exec_lines = _executable_lines()
    assert exec_lines, "실행 라인 추출 실패 — 이 검사가 vacuous 해진다 (정의역 0행 금지)"
    joined = "\n".join(exec_lines)
    for forbidden in ("mkdir ", "rm ", "mv ", "cp ", "tee ", "git add", "git commit"):
        assert forbidden not in joined, (
            f"훅이 {forbidden!r} 를 실행한다 — pointer-only 선언 위반 (헤더 (b)).\n"
            f"실행 라인:\n{joined}")
