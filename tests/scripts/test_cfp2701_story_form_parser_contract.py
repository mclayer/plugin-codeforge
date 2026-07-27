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


# ============================================================ CFP-2844 §7.6 상수
# 설계 Fork A (parse 정규화, trim-inclusive) — story-init.yml §1 파서의 optional 필드
#   (Component / Epic Milestone) 값을 정규화한다. GitHub Issue Form 미입력 시 렌더되는
#   `_No response_` placeholder + whitespace-only 입력 → '' 로 소거해 component/milestone
#   라벨 오부착을 차단. FIX = 기존 `sed '/^$/d'` 를 trim + anchored-removal + blank-drop 로 확장.
#
# 계약 SSOT: Change Plan §7.6 Test Contract (AC-1~AC-7). 본 self-test 는 §7.6 계약만 참조하고
#   구현(src/**·workflow)을 스펙으로 삼지 않는다 — sed_expr 를 테스트가 직접 주입해 FIX↔취약
#   대조(mutation-kill teeth)를 self-contained 로 증명.

# optional 필드 id (story.yml F1 firsthand 확인 — id: component / epic-milestone)
COMPONENT_FIELD_ID = "component"
MILESTONE_FIELD_ID = "epic-milestone"

# awk 헤더 프로그램 (ASCII — Korean-in-argv 무관, 기존 `-f` 파일 패턴 준수).
#   story-init.yml parse step L398/393 verbatim awk 헤더.
_AWK_COMPONENT = r"""/^### Component/{flag=1; next} /^### /{flag=0} flag"""
_AWK_MILESTONE = r"""/^### Epic Milestone/{flag=1; next} /^### /{flag=0} flag"""

# sed 인자 문자열 (cmd 조립 시 `sed ` 뒤에 그대로 삽입). single-quote 포함 형태.
_SED_OLD = r"""'/^$/d'"""  # 취약(vulnerable-revert) — 현행 CFP-2701 REQ 파이프라인 default 와 동일
_SED_FIX = r"""-e 's/^[[:space:]]*//;s/[[:space:]]*$//' -e 's/^_No response_$//' -e '/^$/d'"""
# fix-broadening mutation (과광범) — 유효 소문자 토큰까지 '' 로 삼킴 → scope-containment 대조 (RED)
_SED_BROADENING = r"""-e 's/^[[:space:]]*//;s/[[:space:]]*$//' -e 's/^[a-z]*$//' -e '/^$/d'"""
# anchored-only (trim 절 제거) — whitespace-only 미소거 → trim 절 teeth 별도 증명 (D2 lock, RED)
_SED_ANCHORED_ONLY = r"""-e 's/^_No response_$//' -e '/^$/d'"""

# FIX sed 의 distinctive 리터럴 (anti-drift 결속 — test 9)
_FIX_SED_ANCHOR_LITERAL = "s/^_No response_$//"
_FIX_SED_TRIM_LITERAL = "s/^[[:space:]]*//"

# story-init.yml mirror (wrapper-managed 소스, 헬퍼 확장 §3 신설 상수).
STORY_INIT_YML_MIRROR = WORKTREE_ROOT / "templates" / "github-workflows" / "story-init.yml"

# CONTENT anchor (byte-identity region slice — offset-robust, 하드코딩 line 번호 금지).
#   naive whole-file diff 금지: live/mirror 는 story_uri commit-SHA ref 블록에서 정당하게
#   divergent(수 line) → whole-file diff 는 born-RED. region-scoped 대칭만 검증.
_PARSE_REGION_START = "MILESTONE=$(printf '%s' \"$ISSUE_BODY\""
_PARSE_REGION_END = 'echo "component=$COMPONENT" >> "$GITHUB_OUTPUT"'
_LABEL_REGION_START = "- name: Add component label"
_LABEL_REGION_END = 'gh issue edit "$ISSUE_NUMBER" --add-label "component:$COMPONENT"'


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


def _render_body(
    form: dict, sentinel: str, overrides: dict[str, str] | None = None
) -> str:
    """실 폼 YAML → GitHub Issue body 근사 렌더.

    규칙 (Change Plan §8.1):
      - type: markdown item → heading 없이 attributes.value 본문만 emit.
      - attributes.label 보유 item → `### <label>\\n\\n<value>\\n`.
      - REQ_FIELD_ID 필드의 <value> = sentinel, 나머지 optional = `_No response_`.

    overrides (CFP-2844 §7.6, backward-compatible 확장):
      {field_id: value} 로 특정 optional 필드 값을 명시 주입 (예 Component field id →
      `_No response_` / `workflows` / `frobnicate` / `   `). 미지정(None) 시 기존 동작 유지
      (REQ=sentinel, 나머지 optional=`_No response_`) — 현행 CFP-2701 호출부 무변경.
    """
    overrides = overrides or {}
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
        item_id = item.get("id")
        if item_id in overrides:
            value = overrides[item_id]
        elif item_id == REQ_FIELD_ID:
            value = sentinel
        else:
            value = "_No response_"
        out.append(f"### {label}")
        out.append("")
        out.append(value)
        out.append("")
    return "\n".join(out) + "\n"


def _run_parser(
    body: str,
    awk_prog: str = _AWK_PROG,
    sed_expr: str = _SED_OLD,
    head1: bool = False,
    strip_output: bool = True,
) -> str:
    """실 story-init awk|sed 파서를 subprocess 로 실행해 추출값 반환.

    awk 프로그램은 UTF-8 임시 파일로 `-f` 전달 — ★ Korean-in-argv 인코딩 오염 회피.
    (Windows Git Bash 로 `-c` 인자에 한글 awk 패턴을 직접 전달하면 코드페이지 변환으로
    패턴이 손상 → degraded `/^### /` 가 첫 헤더에 우연 매치 = latent false-oracle. body 는
    stdin[UTF-8], awk 프로그램은 -f 파일[UTF-8] → 양쪽 UTF-8 바이트 일치로 결정적 매칭.
    파일명은 ASCII, `-c` 커맨드에 한글 0.)

    확장 (CFP-2844 §7.6, backward-compatible):
      sed_expr: `sed ` 뒤에 그대로 삽입되는 인자 문자열 (OLD/FIX/broadening/anchored 교체).
                default=_SED_OLD(`'/^$/d'`) → 현행 CFP-2701 REQ 파이프라인과 동일.
                FIX(`-e '...' -e '...' -e '...'`) 형태도 그대로 삽입.
      head1: True 시 종단 `| head -1` 추가 (component/milestone 실 파이프라인 정합).
      strip_output: True(default) → `.strip()` (기존 동작 보존). False → `.rstrip("\\n")`
                    (실 workflow `$(...)` command substitution 정합 — leading/internal
                    whitespace 보존; whitespace-only teeth 증명용, CFP-2844 test 8).
    """
    assert WORKING_BASH is not None
    fd, awk_path = tempfile.mkstemp(suffix=".awk")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(awk_prog)
        posix_path = awk_path.replace("\\", "/")  # MSYS2 awk 는 C:/... 형식 수용
        head_suffix = " | head -1" if head1 else ""
        # 한글 0 — awk 본문은 파일 안. sed_expr 는 single-quote 포함 인자 문자열 그대로 삽입.
        cmd = f"awk -f '{posix_path}' | sed {sed_expr}{head_suffix}"
        r = subprocess.run(
            [WORKING_BASH, "-c", cmd],
            input=body,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        return r.stdout.strip() if strip_output else r.stdout.rstrip("\n")
    finally:
        os.unlink(awk_path)


def _slice_region(text: str, start_anchor: str, end_anchor: str) -> str:
    """text 에서 start_anchor 포함 라인 ~ end_anchor 포함 라인(inclusive) 을 CONTENT 로 slice.

    offset-robust (line 번호 하드코딩 금지) — anchor 라인 내용으로 위치를 찾는다.
    anchor-not-found 시 loud-fail (assert) — silent 빈-slice 거짓통과 차단.
    end_anchor 는 start_idx 이후에서만 탐색 (역방향 우연 매치 배제).
    """
    lines = text.splitlines(keepends=True)
    start_idx = next((i for i, ln in enumerate(lines) if start_anchor in ln), None)
    assert start_idx is not None, f"start anchor 부재 (loud-fail): {start_anchor!r}"
    end_idx = next(
        (j for j in range(start_idx, len(lines)) if end_anchor in lines[j]), None
    )
    assert end_idx is not None, (
        f"end anchor 부재 (start 이후, loud-fail): {end_anchor!r}"
    )
    return "".join(lines[start_idx : end_idx + 1])


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


# ============================================================================
# CFP-2844 §7.6 RTM — story-init.yml optional 필드(Component/Milestone) parse 정규화.
#   설계 Fork A (parse 정규화, trim-inclusive). 각 fixture-discriminating 테스트는
#   FIX 파이프라인 → 기대값 assert + discriminating 대조(vulnerable/broadening/anchored) →
#   반대 결과 assert 를 둘 다 포함 (mutation-kill teeth self-증명, self-contained GREEN).
# ============================================================================


@_SKIP_NO_BASH
def test_cfp2844_component_no_response_normalizes_empty():
    """AC-1 (normative): Component=`_No response_` → FIX 파이프라인 → '' (라벨 오부착 차단).

    대조(vulnerable-revert OLD sed `'/^$/d'`): `_No response_` 생존 → RED 증명. FIX 의
    anchored-removal 절(`s/^_No response_$//`)이 load-bearing 임을 self-prove (mutation-kill).
    """
    form = _load_form(F1_PATH)
    body = _render_body(form, "SENT-2844-c1", overrides={COMPONENT_FIELD_ID: "_No response_"})
    fix = _run_parser(body, awk_prog=_AWK_COMPONENT, sed_expr=_SED_FIX, head1=True)
    assert fix == "", f"FIX: Component=`_No response_` 가 '' 로 정규화되지 않음 (got {fix!r})"
    old = _run_parser(body, awk_prog=_AWK_COMPONENT, sed_expr=_SED_OLD, head1=True)
    assert old == "_No response_", (
        f"대조(teeth) 실패: OLD sed 에서 `_No response_` 가 생존하지 않음 (got {old!r}) — "
        f"FIX 가 vacuous (discriminating 대조가 mutant 을 kill 하지 못함)."
    )


@_SKIP_NO_BASH
def test_cfp2844_empty_component_seam_no_addlabel():
    """AC-2 (normative, SEAM): Component=`_No response_` → FIX → '' + label-guard 결속.

    실 workflow 'Add component label' step 의 guard 리터럴
    `steps.parse.outputs.component != ''` 이 실재함을 assert — parse→'' 와 label 오부착 차단의
    결속(seam) 증명.

    정직 천장 (ADR-119): cascade(job green + native type 부착)는 runtime-only(CI 는 실 Issue
    이벤트 미발화) → CI 는 SEAM(parse 결과 '' ∧ guard 리터럴 실재)만 증명. GitHub 실렌더/실
    라벨 부착은 주장하지 않는다.
    """
    form = _load_form(F1_PATH)
    body = _render_body(form, "SENT-2844-c2", overrides={COMPONENT_FIELD_ID: "_No response_"})
    fix = _run_parser(body, awk_prog=_AWK_COMPONENT, sed_expr=_SED_FIX, head1=True)
    assert fix == "", f"seam: Component=`_No response_` → '' 정규화 실패 (got {fix!r})"
    text = STORY_INIT_YML.read_text(encoding="utf-8")
    assert "steps.parse.outputs.component != ''" in text, (
        "seam 결속 실패: 'Add component label' step guard 리터럴 "
        "`steps.parse.outputs.component != ''` 부재 — parse→'' 가 라벨 오부착을 차단하는 결속 끊김."
    )


@_SKIP_NO_BASH
def test_cfp2844_component_valid_passthrough():
    """AC-3 (normative): Component=`workflows`(유효값) → FIX → `workflows` (회귀 0 passthrough).

    대조(fix-broadening mutation, 과광범 sed `s/^[a-z]*$//` 추가): `workflows`→'' (broadening
    이면 RED). FIX 가 유효 소문자 토큰을 over-strip 하지 않음을 self-prove (scope-containment).
    """
    form = _load_form(F1_PATH)
    body = _render_body(form, "SENT-2844-c3", overrides={COMPONENT_FIELD_ID: "workflows"})
    fix = _run_parser(body, awk_prog=_AWK_COMPONENT, sed_expr=_SED_FIX, head1=True)
    assert fix == "workflows", f"FIX: 유효 component `workflows` passthrough 실패 (got {fix!r})"
    broad = _run_parser(body, awk_prog=_AWK_COMPONENT, sed_expr=_SED_BROADENING, head1=True)
    assert broad == "", (
        f"대조(teeth) 실패: broadening sed 가 `workflows` 를 '' 로 삼키지 않음 (got {broad!r}) — "
        f"FIX 의 scope 검증이 무효 (broadening mutation 이 discriminate 하지 못함)."
    )


@_SKIP_NO_BASH
def test_cfp2844_component_invalid_nonempty_unchanged():
    """AC-4 (normative): Component=`frobnicate`(overlay 목록 외) → FIX → `frobnicate` 불변.

    parse 정규화는 placeholder/whitespace 만 소거 — 목록 외 유효-형태 값은 그대로 통과(scope
    봉쇄; 목록 대조는 후속 overlay 검증 소관). 대조(broadening sed): `frobnicate`→'' (RED).
    정직: fix-removal revert 가 아닌 scope-containment mutation (FIX 의 과잉소거 부재 증명).
    """
    form = _load_form(F1_PATH)
    body = _render_body(form, "SENT-2844-c4", overrides={COMPONENT_FIELD_ID: "frobnicate"})
    fix = _run_parser(body, awk_prog=_AWK_COMPONENT, sed_expr=_SED_FIX, head1=True)
    assert fix == "frobnicate", f"FIX: 목록 외 값 `frobnicate` 불변 실패 (got {fix!r})"
    broad = _run_parser(body, awk_prog=_AWK_COMPONENT, sed_expr=_SED_BROADENING, head1=True)
    assert broad == "", (
        f"대조(teeth) 실패: broadening sed 가 `frobnicate` 를 '' 로 삼키지 않음 (got {broad!r})."
    )


def test_cfp2844_parse_region_mirror_byte_identity():
    """AC-5: parse region(MILESTONE 시작 ~ component echo 종료, inclusive) live↔mirror 대칭.

    CONTENT anchor slice (offset-robust — 하드코딩 line 번호 금지; anchor-not-found = loud-fail).
    naive whole-file diff 금지: live/mirror 는 story_uri commit-SHA ref 블록에서 정당하게
    divergent → whole-file diff 는 born-RED. region-scoped 대칭(FIX 가 양 파일에 동일 적용)만 검증.
    """
    assert STORY_INIT_YML.exists(), f"live 부재: {STORY_INIT_YML}"
    assert STORY_INIT_YML_MIRROR.exists(), f"mirror 부재: {STORY_INIT_YML_MIRROR}"
    live = _slice_region(
        STORY_INIT_YML.read_text(encoding="utf-8"), _PARSE_REGION_START, _PARSE_REGION_END
    )
    mirror = _slice_region(
        STORY_INIT_YML_MIRROR.read_text(encoding="utf-8"), _PARSE_REGION_START, _PARSE_REGION_END
    )
    assert live == mirror, (
        "parse region live↔mirror 비대칭 — FIX 가 한쪽에만 적용(mirror drift)."
        f"\n--- live ---\n{live}\n--- mirror ---\n{mirror}"
    )


def test_cfp2844_label_region_mirror_byte_identity():
    """AC-5: label region('Add component label' 시작 ~ --add-label 종료, inclusive) live↔mirror 대칭.

    동일 offset-robust CONTENT anchor slice + loud-fail 규율. label-guard/부착 step 이 양 파일에
    동형 유지됨을 region-scoped 로 검증 (whole-file diff 의 born-RED 회피).
    """
    assert STORY_INIT_YML.exists(), f"live 부재: {STORY_INIT_YML}"
    assert STORY_INIT_YML_MIRROR.exists(), f"mirror 부재: {STORY_INIT_YML_MIRROR}"
    live = _slice_region(
        STORY_INIT_YML.read_text(encoding="utf-8"), _LABEL_REGION_START, _LABEL_REGION_END
    )
    mirror = _slice_region(
        STORY_INIT_YML_MIRROR.read_text(encoding="utf-8"), _LABEL_REGION_START, _LABEL_REGION_END
    )
    assert live == mirror, (
        "label region live↔mirror 비대칭 — label step drift."
        f"\n--- live ---\n{live}\n--- mirror ---\n{mirror}"
    )


@_SKIP_NO_BASH
def test_cfp2844_milestone_no_response_normalizes_empty():
    """AC-6 (declared): Milestone=`_No response_` → FIX → '' (Component 과 동형 정규화).

    대조(vulnerable-revert OLD sed): Milestone `_No response_` 생존 → RED 증명.
    """
    form = _load_form(F1_PATH)
    body = _render_body(form, "SENT-2844-m1", overrides={MILESTONE_FIELD_ID: "_No response_"})
    fix = _run_parser(body, awk_prog=_AWK_MILESTONE, sed_expr=_SED_FIX, head1=True)
    assert fix == "", f"FIX: Milestone=`_No response_` → '' 정규화 실패 (got {fix!r})"
    old = _run_parser(body, awk_prog=_AWK_MILESTONE, sed_expr=_SED_OLD, head1=True)
    assert old == "_No response_", (
        f"대조(teeth) 실패: OLD sed 에서 Milestone `_No response_` 생존 안 함 (got {old!r})."
    )


@_SKIP_NO_BASH
def test_cfp2844_component_whitespace_only_normalizes_empty():
    """AC-7 (declared, D2 lock): Component=`   `(공백3) → FIX → '' (trim 절 teeth).

    대조(anchored-only sed, trim 절 제거 `-e 's/^_No response_$//' -e '/^$/d'`): `   ` 가
    non-empty 로 생존 → RED 증명. trim 절(`s/^[[:space:]]*//;s/[[:space:]]*$//`)이 whitespace-only
    를 소거하는 load-bearing 절임을 anchored-only 대조로 별도 증명.

    strip_output=False → 실 workflow `$(...)` command substitution 정합 (leading whitespace 보존).
    `.strip()` 오적용 시 whitespace 생존 teeth 가 소실되므로 raw(trailing-newline-only) 비교.
    """
    form = _load_form(F1_PATH)
    body = _render_body(form, "SENT-2844-c8", overrides={COMPONENT_FIELD_ID: "   "})
    fix = _run_parser(
        body, awk_prog=_AWK_COMPONENT, sed_expr=_SED_FIX, head1=True, strip_output=False
    )
    assert fix == "", f"FIX: whitespace-only Component → '' 정규화 실패 (got {fix!r})"
    anchored = _run_parser(
        body, awk_prog=_AWK_COMPONENT, sed_expr=_SED_ANCHORED_ONLY, head1=True, strip_output=False
    )
    assert anchored == "   ", (
        f"대조(teeth) 실패: anchored-only sed(trim 절 제거)에서 whitespace `   ` 가 소거됨 "
        f"(got {anchored!r}) — trim 절 teeth 증명 실패 (whitespace 가 생존해야 trim 절 load-bearing)."
    )


def test_cfp2844_component_pipeline_matches_real_workflow():
    """anti-drift (secondary bind): 실 story-init.yml 에 FIX sed distinctive 리터럴 실재 assert.

    behavioral(test 1-8)이 primary teeth. 본 test 는 secondary — FIX sed 의 distinctive 절
    (`s/^_No response_$//` anchored-removal + `s/^[[:space:]]*//` trim)이 실 워크플로에 landing
    됐는지 결속. exact-literal 대조라 reformat(공백/순서 변경) 시 brittle-RED 가능 — 그 경우
    behavioral teeth 는 유지되고 본 anti-drift 만 재정합 필요 (정직 기록).

    ★ 병렬 DeveloperAgent 의 workflow FIX 가 landing 되면 GREEN, 아직이면 RED (deliverable
    실패 아님 — PL 이 통합 재실행).
    """
    assert STORY_INIT_YML.exists(), f"story-init.yml 부재: {STORY_INIT_YML}"
    text = STORY_INIT_YML.read_text(encoding="utf-8")
    assert _FIX_SED_ANCHOR_LITERAL in text, (
        f"anti-drift: FIX anchored 절 `{_FIX_SED_ANCHOR_LITERAL}` 가 story-init.yml 에 부재 — "
        f"workflow FIX 미landing 또는 drift."
    )
    assert _FIX_SED_TRIM_LITERAL in text, (
        f"anti-drift: FIX trim 절 `{_FIX_SED_TRIM_LITERAL}` 가 story-init.yml 에 부재."
    )
