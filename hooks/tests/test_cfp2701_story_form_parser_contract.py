"""test_cfp2701_story_form_parser_contract.py — CFP-2701 Phase 2 §8 정합 self-test.

계약 SSOT:
  Change Plan `cfp-2701-story-form-parser-header-drift.md` §8.1 RTM (wrapper-self
  dogfood → RTM 앵커 = Change Plan §8, Story §8 아님, ADR-145 §결정10).

검증 대상:
  story.yml 폼(F1/F2)이 렌더할 실 Issue body 를 story-init.yml §1 파서(awk)에
  통과시켰을 때 추출 REQ(§1)이 non-empty 인지 — 폼↔파서 `### 사용자 요구사항`
  헤더 정합. 폼 라벨 또는 파서 헤더를 드리프트로 되돌리면 REQ EMPTY (mutation-kill).

RTM (Change Plan §8.1):
  - AC-1 (normative): test_cfp2701_form_renders_nonempty_section1 (F1/F2 parametrize)
  - AC-2 (normative): test_cfp2701_mutation_kill_form_label_redrift
                    + test_cfp2701_mutation_kill_parser_header

anti-theater 규칙 (presence-grep 금지 — Story §5.3 AC-2 사용자 명시):
  - fixture 는 실 폼 YAML 에서 파생 (하드코딩 body 금지 → 폼 라벨 드리프트 포착).
  - 실 story-init awk 파서를 subprocess 로 실행 (presence-grep 아님).
  - PARSER_PIPELINE awk expression 이 실 workflow (story-init.yml) 에 실재함을 assert
    (파서가 drift 하면 본 테스트 사본도 함께 깨지도록 결속).
  - mutation 2종(폼 라벨 재드리프트 / 파서 헤더 토큰 치환) → REQ EMPTY 로 mutant kill.

정직 천장 (Change Plan §8.1 — AC-3 declared, hard-claim 금지):
  CI 는 GitHub 실 폼 렌더러를 호출할 수 없다 → `label → ### <label>` 규칙으로 렌더
  body 를 **근사**한다 (근거 = 전 시스템의 내부 co-design, 파서의 `### Epic Milestone`
  /`### Component` awk 가 F3 라벨과 정확 대응). "GitHub 실렌더 검증" 은 주장하지 않는다.

CI: lint.yml hook-unit-tests job (ubuntu-latest, requirements.txt 의 pyyaml).
  bash/awk/sed 부재 (로컬 Windows) 시 pytest.skip. ★ bare `bash` = WSL relay 破손
  (execvpe 실패 → 빈출력 거짓통과) 회피 — 후보 bash 를 known round-trip 으로 검증한
  뒤에만 신뢰 (설계리뷰가 이 함정으로 자기 false-oracle 겪음 → 반드시 회피).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

# worktree root = tests/ → hooks/ → root (precedent: test_skip_offer_reminder.py L37)
WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent

# 폼 2 파일 (F1 = 라이브, F2 = wrapper-managed 소스 / consumer-guide §2c manual-cp)
F1_PATH = WORKTREE_ROOT / ".github" / "ISSUE_TEMPLATE" / "story.yml"
F2_PATH = WORKTREE_ROOT / "templates" / ".github" / "ISSUE_TEMPLATE" / "story.yml"
STORY_INIT_YML = WORKTREE_ROOT / ".github" / "workflows" / "story-init.yml"

# 요건 필드 식별자 (F3 계승) — 값(sentinel)을 이 필드에 주입
REQ_FIELD_ID = "user-requirement-verbatim"

# 실 story-init.yml §1 파서 (P1, story-init.yml:371 verbatim awk).
#   _AWK_PROG = awk 프로그램 본문 (실행 시 -f 파일로 전달 — Korean-in-argv 회피).
#   _AWK_EXPR = story-init.yml 에 실재하는 `awk '...'` 리터럴 (anti-drift 결속용).
_AWK_PROG = r"""/^### 사용자 요구사항/{flag=1; next} /^### /{flag=0} flag"""
_AWK_EXPR = "awk '" + _AWK_PROG + "'"
PARSER_PIPELINE = _AWK_EXPR + r""" | sed '/^$/d'"""


# ============================================================ working-bash 해석

def _candidate_bashes() -> list[str]:
    """후보 bash 목록. Windows Git Bash 절대경로 우선(WSL relay 회피), 그 다음 PATH.

    ubuntu-latest CI: Git Bash 경로 부재 → shutil.which("bash") = /usr/bin/bash 사용.
    """
    cands: list[str] = []
    for p in (
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
    ):
        if os.path.exists(p):
            cands.append(p)
    which = shutil.which("bash")
    if which and which not in cands:
        cands.append(which)
    return cands


def _resolve_working_bash() -> str | None:
    """실제로 stdin→awk→stdout 을 round-trip 하는 bash 만 신뢰해 반환.

    Windows WSL relay(System32\\bash.exe)는 awk 파이프에서 execvpe 실패 → 빈출력 →
    거짓 PASS. 후보마다 알려진 marker 를 실 파서와 동일 mechanism(bash -c + awk + stdin)
    으로 round-trip 시켜 검증한 뒤에만 채택 (false-oracle 봉인).
    """
    for b in _candidate_bashes():
        try:
            r = subprocess.run(
                [b, "-c", "awk '{print}'"],
                input="__cfp2701_probe__",
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
            )
        except Exception:
            continue
        if r.returncode == 0 and r.stdout.strip() == "__cfp2701_probe__":
            return b
    return None


WORKING_BASH = _resolve_working_bash()
_SKIP_NO_BASH = pytest.mark.skipif(
    WORKING_BASH is None,
    reason="round-trip 검증 통과한 bash 부재 (로컬 Windows WSL relay 회피) — 실 게이트는 ubuntu-latest",
)


# ============================================================ fixture 헬퍼

def _load_form(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _render_body(form: dict, sentinel: str) -> str:
    """실 폼 YAML → GitHub Issue body 근사 렌더.

    규칙 (Change Plan §8.1):
      - type: markdown item → heading 없이 attributes.value 본문만 emit.
      - attributes.label 보유 item → `### <label>\\n\\n<value>\\n`.
      - REQ_FIELD_ID 필드의 <value> = sentinel, 나머지 optional = `_No response_`.
    """
    out: list[str] = []
    for item in form.get("body", []):
        attrs = item.get("attributes", {}) or {}
        if item.get("type") == "markdown":
            out.append(str(attrs.get("value", "")).rstrip("\n"))
            out.append("")  # 블록 구분 blank
            continue
        label = attrs.get("label")
        if label is None:
            continue
        value = sentinel if item.get("id") == REQ_FIELD_ID else "_No response_"
        out.append(f"### {label}")
        out.append("")
        out.append(value)
        out.append("")
    return "\n".join(out) + "\n"


def _run_parser(body: str, awk_prog: str = _AWK_PROG) -> str:
    """실 story-init awk|sed 파서를 subprocess 로 실행해 추출 REQ 반환.

    awk 프로그램은 UTF-8 임시 파일로 `-f` 전달 — ★ Korean-in-argv 인코딩 오염 회피.
    (Windows Git Bash 로 `-c` 인자에 한글 awk 패턴을 직접 전달하면 코드페이지 변환으로
    패턴이 손상 → degraded `/^### /` 가 첫 헤더에 우연 매치 = latent false-oracle. body 는
    stdin[UTF-8], awk 프로그램은 -f 파일[UTF-8] → 양쪽 UTF-8 바이트 일치로 결정적 매칭.
    파일명은 ASCII, `-c` 커맨드에 한글 0.)
    """
    assert WORKING_BASH is not None
    fd, awk_path = tempfile.mkstemp(suffix=".awk")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(awk_prog)
        posix_path = awk_path.replace("\\", "/")  # MSYS2 awk 는 C:/... 형식 수용
        cmd = f"awk -f '{posix_path}' | sed '/^$/d'"  # 한글 0 — awk 본문은 파일 안
        r = subprocess.run(
            [WORKING_BASH, "-c", cmd],
            input=body,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        return r.stdout.strip()
    finally:
        os.unlink(awk_path)


# ============================================================ AC-1 (normative)

@_SKIP_NO_BASH
@pytest.mark.parametrize("form_path", [F1_PATH, F2_PATH], ids=["F1", "F2"])
def test_cfp2701_form_renders_nonempty_section1(form_path: Path):
    """AC-1 (normative): 수정 후 폼(F1/F2) 렌더 body → 실 파서 → REQ non-empty ∧ SENTINEL 포함.

    execution-backed: 실 폼 YAML 파생 fixture + 실 awk 파서 subprocess 실행.
    """
    assert form_path.exists(), f"폼 파일 부재: {form_path}"
    sentinel = "CFP2701-SENTINEL-8f3a1c2e-verbatim-req-body"
    form = _load_form(form_path)
    body = _render_body(form, sentinel)
    req = _run_parser(body)
    assert req != "", (
        f"{form_path.name}: 파서가 §1(REQ)을 빈 값으로 추출 — 폼↔파서 헤더 드리프트. "
        f"렌더 body 에 `### 사용자 요구사항` 헤더 부재 추정."
    )
    assert sentinel in req, (
        f"{form_path.name}: REQ 에 요건 SENTINEL 미포함 (REQ={req!r}) — "
        f"요건 필드 값이 §1 캡처 구간으로 흐르지 않음."
    )


# ============================================================ AC-2 (normative) — mutation-kill

@_SKIP_NO_BASH
def test_cfp2701_mutation_kill_form_label_redrift():
    """AC-2 (normative): 폼측 mutation — 요건 필드 라벨을 구 WHY 헤더로 재드리프트 → REQ EMPTY.

    폼 라벨을 `WHY — 해결하려는 문제 / 목표` 로 되돌리면 렌더 body 에 `### 사용자 요구사항`
    이 사라져 파서가 빈 REQ 를 낸다 = mutant kill (AC-1 이 presence-grep/tautology 아님 확증).
    """
    sentinel = "CFP2701-SENTINEL-mutation-form-label"
    form = _load_form(F1_PATH)
    mutated = False
    for item in form.get("body", []):
        if item.get("id") == REQ_FIELD_ID:
            item["attributes"]["label"] = "WHY — 해결하려는 문제 / 목표"
            mutated = True
    assert mutated, f"mutation 대상 필드({REQ_FIELD_ID}) 미발견 — 폼 구조 drift"
    body = _render_body(form, sentinel)
    req = _run_parser(body)
    assert req == "", (
        f"mutant 생존: 요건 라벨 재드리프트에도 REQ non-empty (REQ={req!r}) — "
        f"AC-1 이 실 파서 기반이 아니라 presence-grep 일 위험."
    )


@_SKIP_NO_BASH
def test_cfp2701_mutation_kill_parser_header():
    """AC-2 (normative): 파서측 mutation — awk 헤더 토큰 치환 → 정상 body 에서 REQ EMPTY.

    PARSER_PIPELINE 안 `사용자 요구사항` 토큰을 다른 문자열로 치환한 파서를 정상 body 에
    실행하면 헤더 미매치로 빈 REQ = mutant kill (실 헤더 토큰이 load-bearing 임을 확증).
    """
    sentinel = "CFP2701-SENTINEL-mutation-parser-header"
    form = _load_form(F1_PATH)
    body = _render_body(form, sentinel)
    # sanity: 정상 파서로는 non-empty (mutant 대비 대조군)
    assert _run_parser(body) != "", "대조군 실패: 정상 파서가 정상 body 에서 빈 REQ"
    mutated_prog = _AWK_PROG.replace("사용자 요구사항", "재드리프트-미존재-헤더")
    assert mutated_prog != _AWK_PROG, "파서 mutation 미적용 — 토큰 치환 실패"
    req = _run_parser(body, awk_prog=mutated_prog)
    assert req == "", (
        f"mutant 생존: 파서 헤더 토큰 치환에도 REQ non-empty (REQ={req!r}) — "
        f"awk 헤더가 load-bearing 이 아님."
    )


# ============================================================ anti-drift 결속

def test_cfp2701_parser_pipeline_matches_real_workflow():
    """PARSER_PIPELINE awk expression 이 실 story-init.yml 에 실재함을 assert.

    워크플로 파서가 바뀌면 본 테스트 사본이 drift 로 flag (테스트가 실 파서를 미러함 보장).
    """
    assert STORY_INIT_YML.exists(), f"story-init.yml 부재: {STORY_INIT_YML}"
    text = STORY_INIT_YML.read_text(encoding="utf-8")
    assert _AWK_EXPR in text, (
        "PARSER_PIPELINE 의 awk expression 이 story-init.yml 에 없음 — 파서 drift 또는 "
        "테스트 사본 stale. 실 파서와 테스트 상수를 재정합하라."
    )
