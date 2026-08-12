#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-2944 / ADR-025 Amendment 4 §A4-2 — illegal-stop form-set parity 검사 (fence ↔ 4 전파면)
# ADR-061 §결정 1 Python-SSOT 패턴 (thin wrapper = scripts/check-form-set-parity.sh)
#   + §결정 11 ReDoS-safe (라인 단위 스캔 + 단일 char-class quantifier — nested quantifier 0)
#     ↳ 근거 = ① 구조적: 사용 정규식 전건이 단일 char-class quantifier 이고 인접 quantifier·중첩 0,
#       후보 토큰의 form-id 적격성은 정규식이 아니라 선형 시간 파이썬 검사로 판정한다
#       ② 실측: --self-test 합성 fixture + 8193자 라인 fixture 통과.
#       단 wall-clock 벤치마크·복잡도 회귀 self-test 는 **없다** → 본 서술은 bounded degradation 선언이지
#       "임의 입력 무해" 단정이 아니다 (ADR-168 §결정 16 honest-ceiling).
#
# tier: [정적]  (관측 tier — merge 무차단)
#   근거(firsthand 실측): 본 검사의 유일 실행 채널
#   `.github/workflows/orchestrator-autonomy-stop-taxonomy-check.yml` 은 job-level 및 step-level
#   `continue-on-error: true` 이며, CLAUDE.md branch protection required contexts 8-tuple 에 미등재다.
#   즉 본 검사의 RED 는 **관측될 뿐 merge 를 막지 못한다** (ADR-025 §A4-6-3 / Story CFP-2944 §7.9 U-1).
#   승격 경로 = ADR-060 evidence-gate (연속 green 이력 + 오탐 0 적립 후 발의). "이 검사로 차단한다" 류
#   표현을 쓰지 않는다.
#
# ── 목적 ────────────────────────────────────────────────────────────────────────
#   ADR-025 §결정 7 의 form-set fence 가 illegal-stop **named form id 집합의 유일 원본**이고,
#   (1) §결정 7 표 (2) hook priming TEXT ch1 (3) hook priming TEXT ch2 (4) consumer mirror
#   4면이 전파면이다. 어느 한 쌍이라도 form id 집합이 어긋나면 두-주인 SSOT 재생산이므로 정적 검출한다.
#
# ── 검사 방향 2 (ADR-025 §A4-2) ────────────────────────────────────────────────
#   ① fence 등재 전 id 가 4면 전건에 **anchor 표기**로 존재 (누락 = 위반)
#   ② 4면에서 추출한 anchored id 후보 중 **fence 미등재** ∧ taxonomy class 명 밖 = 위반 (초과)
#
# ── anchor 표기 규약 (§A4-2 신설) ──────────────────────────────────────────────
#   ① backtick 감쌈: `over-halt`      ② dash 동반 괄호: (over-halt — …)
#   요건 = **id 당 면마다 최소 1 anchor** (모든 인스턴스 문장에 anchor 의무 없음 — 렌더 가독성 보존).
#   fence 자신은 규약 대상 밖 (파서 원본이라 backtick 삽입 시 파싱 값 오염) → 표 region 획득 시 제외.
#
# ── 행 단위 구조 요건 D2 (§A4-2 운용정의) ──────────────────────────────────────
#   fence 등재 **각** id 는 §결정 7 표에 **자기 행**을 가지며, 그 행 안에 ① 축별 discriminant 3항
#   ② tier 라벨 을 함께 보유한다.
#   * **"자기 행" 의 기계 판정 = 그 id anchor 가 행의 첫 셀(Pattern 열)에 존재하는 행.**
#     §A4-2 가 "동거 상속을 충족으로 보지 않는다"(다른 form 의 행에 얹혀 tier·discriminant 를 상속하는
#     형태)를 명시하므로, 사유 셀 안의 cross-ref 언급(예: vague-pause 행 본문의 `over-halt` 포인터)은
#     자기 행으로 계산하지 않는다. 이 첫-셀 규칙이 그 불인정 조항의 운용정의다.
#   * 축 참조("vague-pause 와 동일 축(A2)")는 3항을 대신하지 않는다 → 3항 term 을 **개별 presence** 로
#     판정한다 (실 표의 구분자가 행마다 `∧` / `+` 로 갈리므로 구분자 의존 판정은 오탐).
#   * 정의역 = fence 등재 named form id 한정. 표의 무기명 예시 행은 대상 아님.
#
# ── negative-control presence D3 ───────────────────────────────────────────────
#   표 region 행 중 `CFP-2944` 를 포함하는 행(= Amendment 4 저작 행) 전건이 `negative control` 리터럴
#   보유. **정의역을 이 이상 넓히지 않는다** — ADR-025 frontmatter 가 "정의역 = 본 amendment 저작 행
#   한정이며 Story CFP-2944 검사 술어 D3 과 동일 정의역" 이라 못박았고, 기왕 착지한 vague-pause 행은
#   Amendment 3 저작물이라 정의역 밖이다.
#
# ── 불변식 (Story CFP-2944 §7.12.2) ────────────────────────────────────────────
#   INV-T1 집합 동일성만 검사 — **개수 assert 0**
#   INV-T3 fail-closed — ADR-025 존재(wrapper) ∧ 면 2~4 중 파일 부재 또는 대상 함수 부재 → exit 1
#          (fail-open 금지). ADR-025 **자체** 부재 = honest no-op exit 0 (consumer 축에만 허용)
#   INV-T4 form id 리터럴 하드코딩 0 — fence 파싱만. `TAXONOMY_CLASS_NAMES` 는 form id 가 아니라
#          taxonomy class 명이며, fence 등재 id 와 교집합이 생기면 즉시 exit 2 로 자기 반증한다
#   INV-T5 --self-test fixture 는 실 아티팩트 form 문자열 재사용 0 (합성 id 로 구성 — tautological 방어)
#   INV-T6 자기참조 절대수치 assert 0 — 술어로만 판정 (행수·id 개수 assert 없음)
#
# ── Usage ──────────────────────────────────────────────────────────────────────
#   check_form_set_parity.py              # 인자 0개 = repo root(cwd) 기준 4면 검사
#   check_form_set_parity.py <path>       # 디렉터리 = repo root / ADR-025 파일 = 그 repo root 유도
#   check_form_set_parity.py --self-test  # 합성 fixture RED/GREEN 판별 (CI step)
#
# ── Exit code / stdout marker (엣지 enum 요건: traceback 발 exit 1 과 위반 exit 1 구별) ──
#   0 = PASS                  → `[form-set-parity] PASS — …`
#   0 = honest no-op          → `[form-set-parity] ADR-025 파일 부재 — honest no-op …`
#   1 = 위반                  → `[form-set-parity] FAIL — …` (+ 면·id·방향 행 단위 열거)
#   2 = setup error           → `[form-set-parity] setup error: …` (stderr)
#   엣지 거동: 비-UTF8 → exit 2 / 인자 경로 미존재 → exit 2 / 파일 인자 basename 불일치 → honest no-op
#   exit 0 / fence 0행(0byte 포함)·fence 중복 id → exit 2 / 8193자 라인 = 내성(정상 처리).
#   fence 미닫힘 2형 (firsthand 실측, 결정적):
#     (a) 후속 ``` 이 전무 → ValueError → exit 2
#     (b) 후속 ``` 이 있어 그 토큰이 block 을 닫음 → 그 block 을 파싱. 실 문서에서 추가로 딸려온
#         산문 라인은 `<id> | <축>` 형식 미매칭이라 유효 행 0 → inventory 행 집합은 불변(생존).
#         즉 (b) 는 검출되지 않는다 — markdown fence 토글의 원리적 귀결이며 over-claim 하지 않는다.
#
# ── 정직 천장 (over-claim 0 — ADR-025 §A4-6) ───────────────────────────────────
#   1. 행동 준수는 강제되지 않는다 — 어떤 정적 검사도 "실제로 안 멈췄는가"를 판정할 수 없다.
#      본 검사가 얻는 것은 문서·기계 표면 간 정합뿐이다.
#   2. **검출 sufficiency 는 undecidable** — 본 검사는 *등재된* form 의 4면 동기화만 본다.
#      "6번째 form 을 미리 등재하게" 는 강제하지 못한다.
#   3. **방향 ② 는 anchor 규약 준수면에 한해서만 검출한다** — 규약 밖 bare 산문 토큰
#      (한글 산문 안 kebab 토큰)으로 신규 form id 를 심으면 **미탐**이다. "방향 ② 완전 검출" 주장 금지.
#      방향 ①(fence→면)만 표기 규약과 무관하게 완전하다.
#   4. hook 면 텍스트는 대상 FunctionDef 의 **모든 str 상수**(docstring 포함)를 concat 한 것이다.
#      따라서 anchor 가 priming TEXT 본문이 아니라 docstring 에만 있어도 방향 ① 은 충족된다 — 검출 한계.
#   5. 본 검사 RED 는 merge 를 막지 못한다 (위 tier 절).

import ast
import os
import re
import shutil
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# ── home_marker (wrapper governance sentinel — consumer 부재 시 honest no-op) ──
ADR025_BASENAME = "ADR-025-stop-discipline-non-whitelist-as-defect.md"
HOME_MARKER = os.path.join("archive", "adr", ADR025_BASENAME)

# ── taxonomy class 명 (ADR-144 §결정 2 소유) — form id 가 **아니다**. 방향 ② 오탐 방어 allowlist ──
TAXONOMY_CLASS_NAMES = frozenset({"decision-null", "ask-trigger"})

# ── 축별 discriminant 3항 (§A4-2 운용정의 — 개별 presence 판정) ──
AXIS_DISCRIMINANTS = {
    "A2": ("잔여작업 有", "payload = 0", "volitional"),
    "A1": ("잔여작업 有", "payload > 0", "ask-trigger 3종 미해당"),
}
TIER_LABEL = "[advisory]"
NEGATIVE_CONTROL_LITERAL = "negative control"
AMENDMENT4_ROW_MARKER = "CFP-2944"  # D3 정의역 = 본 amendment 저작 행 한정

MARKER = "[form-set-parity]"

# ── 4 전파면 (SURFACES) ──
HOOK_CH1_PATH = os.path.join("hooks", "story-transition-autonomy-reminder.py")
HOOK_CH2_PATH = os.path.join("scripts", "lib", "agent_spawn_transition_reminder.py")
CONSUMER_GUIDE_PATH = os.path.join("docs", "consumer-guide.md")

SURFACES = [
    {
        "key": "adr-decision7-table",
        "path": HOME_MARKER,
        "kind": "adr_table",
        "desc": "ADR-025 §결정 7 표 (fence 블록 제외 region)",
    },
    {
        "key": "hook-ch1",
        "path": HOOK_CH1_PATH,
        "kind": "py_func",
        "func": "_build_reminder",
        "desc": "hook priming TEXT ch1 (UserPromptSubmit)",
    },
    {
        "key": "hook-ch2",
        "path": HOOK_CH2_PATH,
        "kind": "py_func",
        "func": "_build_context",
        "desc": "hook priming TEXT ch2 (Agent spawn priming)",
    },
    {
        "key": "consumer-mirror",
        "path": CONSUMER_GUIDE_PATH,
        "kind": "guide_region",
        "desc": "docs/consumer-guide.md §7.1 mirror",
    },
]


class SetupError(Exception):
    """검사 성립 불가 (exit 2) — 위반(exit 1) 과 구별되는 setup 축."""


# ── anchor 추출 (ReDoS-safe: 단일 char-class quantifier, nested quantifier 0) ──
# 후보 토큰만 정규식으로 잘라내고, form-id 적격성은 선형 시간 파이썬 검사로 판정한다.
_BACKTICK_TOKEN_RE = re.compile(r"`([a-z0-9][a-z0-9-]*)`")
_PAREN_DASH_TOKEN_RE = re.compile(r"\(([a-z0-9][a-z0-9-]*)\s*—")
_MAX_FORM_ID_LEN = 64


def _is_form_id_candidate(token):
    """kebab-case form id 후보 적격성 (선형 판정 — 정규식 backtracking 부재).

    요건: 소문자 시작 · `-` 1개 이상 · 선두/말미 `-` 없음 · 연속 `--` 없음 · 길이 상한.
    (일반 어휘·경로·파일명은 하이픈 부재 또는 `.`/`/` 포함으로 자연 배제된다.)
    """
    if not token or len(token) > _MAX_FORM_ID_LEN:
        return False
    if not ("a" <= token[0] <= "z"):
        return False
    if "-" not in token or token.endswith("-") or "--" in token:
        return False
    return True


def extract_anchored_ids(surface_text):
    """surface_text 에서 §A4-2 anchor 표기 규약을 만족하는 form id 후보 집합 반환.

    규약 ① backtick 감쌈 `foo-bar` / 규약 ② dash 동반 괄호 `(foo-bar — …)`.
    규약 밖 bare 산문 토큰은 **추출하지 않는다**(방향 ② 미탐 — 헤더 정직 천장 3항).
    """
    found = set()
    if not surface_text:
        return found
    for regex in (_BACKTICK_TOKEN_RE, _PAREN_DASH_TOKEN_RE):
        for m in regex.finditer(surface_text):
            tok = m.group(1)
            if _is_form_id_candidate(tok):
                found.add(tok)
    return found


# ── fence 파싱 (form id 집합의 유일 원본 — 리터럴 하드코딩 0) ──
def parse_fence(adr_text):
    """ADR 본문에서 form-set fence 를 파싱해 (form_id, 축) 목록을 **등재 순서 보존**으로 반환.

    fence 행 형식 = `<form-id> | <축> | <표 anchor 예시>`. `#` 주석·빈 줄은 건너뛴다.
    복수 fenced block 중 **유효 행을 최초로 산출하는 block** 을 inventory 로 채택한다
    (다이어그램 등 무관 fence 는 유효 행 0 이라 자연 배제).

    Raises:
        ValueError: fence 미닫힘 (열린 채 문서 종료) — 결정적 거동, 호출측이 setup error 로 매핑.
    """
    rows = []
    in_fence = False
    block = []
    for raw in (adr_text or "").split("\n"):
        if raw.lstrip().startswith("```"):
            if not in_fence:
                in_fence = True
                block = []
            else:
                in_fence = False
                parsed = _parse_fence_block(block)
                if parsed:
                    return parsed
            continue
        if in_fence:
            block.append(raw)
    if in_fence:
        raise ValueError("fence 미닫힘 — ``` 가 열린 채 문서가 끝났다")
    return rows


def _parse_fence_block(block_lines):
    """단일 fenced block 을 inventory 행으로 파싱 (유효 행 없으면 빈 리스트)."""
    parsed = []
    for line in block_lines:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split("|", 2)
        if len(parts) < 2:
            continue
        form_id = parts[0].strip()
        axis = parts[1].strip()
        if not _is_form_id_candidate(form_id) or not axis:
            continue
        parsed.append((form_id, axis))
    return parsed


# ── region 획득 ──
def _strip_fenced_blocks(text):
    """fenced code block 라인 제거 (fence 자신은 anchor 규약 대상 밖 — §A4-2)."""
    out = []
    in_fence = False
    for raw in text.split("\n"):
        if raw.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(raw)
    return "\n".join(out)


def decision7_table_region(adr_text):
    """ADR-025 §결정 7 region 에서 **fence 블록을 제외한** 표 region 문자열 반환.

    fence 를 제외하지 않으면 방향 ① 이 tautological 이 된다(원본이 자기 자신을 증명).
    §결정 7 heading 부재 시 빈 문자열 (호출측이 fail-closed 위반으로 처리).
    """
    lines = (adr_text or "").split("\n")
    start = None
    end = len(lines)
    for i, line in enumerate(lines):
        if start is None:
            if line.startswith("### 결정 7"):
                start = i
            continue
        if line.startswith("### ") or line.startswith("## "):
            end = i
            break
    if start is None:
        return ""
    return _strip_fenced_blocks("\n".join(lines[start:end]))


def consumer_guide_region(guide_text):
    """docs/consumer-guide.md 의 `## 7.1 ` ~ 다음 `## ` 직전 region 문자열 반환 (부재 시 빈 문자열)."""
    lines = (guide_text or "").split("\n")
    start = None
    end = len(lines)
    for i, line in enumerate(lines):
        if start is None:
            if line.startswith("## 7.1 "):
                start = i
            continue
        if line.startswith("## "):
            end = i
            break
    if start is None:
        return ""
    return "\n".join(lines[start:end])


def hook_priming_text(py_source, func_name):
    """py_source 안 func_name FunctionDef 본문의 str 상수를 concat 해 반환.

    docstring 을 포함한 모든 str 상수가 대상이다 (헤더 정직 천장 4항 — 검출 한계 declare).

    Raises:
        ValueError: 대상 함수 부재 또는 소스 파싱 실패 (호출측이 fail-closed 위반으로 매핑).
    """
    try:
        tree = ast.parse(py_source or "")
    except (SyntaxError, ValueError) as e:
        raise ValueError(f"파이썬 소스 파싱 실패: {e}")
    target = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            target = node
            break
    if target is None:
        raise ValueError(f"대상 함수 부재: {func_name}")
    chunks = []
    for sub in ast.walk(target):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            chunks.append(sub.value)
    return "\n".join(chunks)


# ── 표 행 유틸 ──
def _norm_ws(text):
    """연속 공백류를 단일 공백으로 정규화 (term presence 판정 robustness)."""
    return re.sub(r"\s+", " ", text)


def _table_rows(region_text):
    """표 region 의 데이터 행 후보 (구분선 행 제외)."""
    rows = []
    for raw in region_text.split("\n"):
        s = raw.strip()
        if not s.startswith("|"):
            continue
        cells = s.split("|")
        body = "".join(cells).strip()
        if body and set(body) <= set("-: "):
            continue  # `|---|---|` 구분선
        rows.append(s)
    return rows


def _first_cell(row):
    """표 행의 첫 셀(Pattern 열) 텍스트."""
    parts = row.split("|")
    return parts[1] if len(parts) > 1 else ""


# ── D2 / D3 ──
def check_row_structure(adr_text):
    """D2(행 단위 구조 요건) + D3(negative-control presence) 위반 목록 반환."""
    violations = []
    try:
        fence = parse_fence(adr_text)
    except ValueError as e:
        return [f"fence 파싱 실패 — {e}"]
    if not fence:
        return ["fence 파싱 결과 0행 — form-set SSOT 부재 (구조 검사 성립 불가)"]

    region = decision7_table_region(adr_text)
    if not region.strip():
        return ["§결정 7 표 region 획득 실패 — heading `### 결정 7` 부재 (fail-closed)"]
    rows = _table_rows(region)

    for form_id, axis in fence:
        own_rows = [r for r in rows if form_id in extract_anchored_ids(_first_cell(r))]
        if not own_rows:
            violations.append(
                f"D2 자기 행 부재 — id=`{form_id}`: §결정 7 표에 첫 셀 anchor 를 갖는 자기 행이 없다 "
                f"(동거 상속·사유 셀 cross-ref 는 충족 불인정 — ADR-025 §A4-2)"
            )
            continue
        terms = AXIS_DISCRIMINANTS.get(axis)
        if terms is None:
            violations.append(
                f"D2 축 미정의 — id=`{form_id}` 축=`{axis}`: discriminant 3항 정의 부재로 행 구조 평가 불가 "
                f"(fail-closed — AXIS_DISCRIMINANTS 확장 또는 fence 축 정정 필요)"
            )
            continue
        best_missing = None
        for row in own_rows:
            norm = _norm_ws(row)
            missing = [t for t in terms if t not in norm]
            if TIER_LABEL not in norm:
                missing = missing + [f"tier 라벨 {TIER_LABEL}"]
            if not missing:
                best_missing = []
                break
            if best_missing is None or len(missing) < len(best_missing):
                best_missing = missing
        if best_missing:
            violations.append(
                f"D2 행 구조 미달 — id=`{form_id}` 축=`{axis}`: 자기 행에 부재 항목 "
                f"{best_missing} (축 참조·동거 상속은 3항을 대신하지 않는다 — ADR-025 §A4-2)"
            )

    for row in rows:
        if AMENDMENT4_ROW_MARKER in row and NEGATIVE_CONTROL_LITERAL not in row:
            head = _norm_ws(_first_cell(row)).strip()[:60]
            violations.append(
                f"D3 negative control 부재 — `{AMENDMENT4_ROW_MARKER}` 저작 행에 "
                f"`{NEGATIVE_CONTROL_LITERAL}` 리터럴이 없다 (행 선두: {head})"
            )
    return violations


# ── 면 텍스트 획득 ──
def _read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _surface_text(root, surface):
    """(text, violation) — 획득 실패 시 text=None + fail-closed 위반 문자열 (INV-T3)."""
    rel = surface["path"]
    abspath = os.path.join(root, rel)
    if not os.path.exists(abspath):
        return None, (
            f"면 파일 부재 — 면={surface['key']} ({rel}): ADR-025 는 존재하는 wrapper 인데 전파면이 없다 "
            f"(fail-closed — honest no-op 은 ADR-025 자체 부재 축에만 허용, INV-T3)"
        )
    try:
        raw = _read_text(abspath)
    except (OSError, UnicodeDecodeError) as e:
        raise SetupError(f"읽기 실패: {rel}: {e}")
    kind = surface["kind"]
    if kind == "adr_table":
        region = decision7_table_region(raw)
        if not region.strip():
            return None, (
                f"면 region 부재 — 면={surface['key']} ({rel}): heading `### 결정 7` 획득 실패 (fail-closed)"
            )
        return region, None
    if kind == "guide_region":
        region = consumer_guide_region(raw)
        if not region.strip():
            return None, (
                f"면 region 부재 — 면={surface['key']} ({rel}): `## 7.1 ` 섹션 획득 실패 (fail-closed)"
            )
        return region, None
    if kind == "py_func":
        try:
            return hook_priming_text(raw, surface["func"]), None
        except ValueError as e:
            return None, (
                f"면 함수 부재 — 면={surface['key']} ({rel}): {e} (fail-closed, INV-T3)"
            )
    raise SetupError(f"알 수 없는 면 kind: {kind}")


# ── parity 본체 ──
def check_parity(root):
    """(violations, evidence) 반환. root = repo root 경로.

    Raises:
        SetupError: 검사 성립 불가 (ADR 읽기 실패 / fence 0행·미닫힘·중복 / 어휘 자기모순).
    """
    adr_path = os.path.join(root, HOME_MARKER)
    try:
        adr_text = _read_text(adr_path)
    except (OSError, UnicodeDecodeError) as e:
        raise SetupError(f"ADR-025 읽기 실패: {adr_path}: {e}")

    try:
        fence = parse_fence(adr_text)
    except ValueError as e:
        raise SetupError(f"fence 파싱 실패: {e}")
    if not fence:
        raise SetupError("fence 파싱 결과 0행 — form-set SSOT(§결정 7 fence) 부재로 검사 성립 불가")

    fence_ids = []
    for form_id, _axis in fence:
        if form_id in fence_ids:
            raise SetupError(f"fence 중복 id: `{form_id}` — form-set SSOT 모호 (검사 성립 불가)")
        fence_ids.append(form_id)
    fence_id_set = set(fence_ids)

    # INV-T4 자기 반증 — taxonomy class 명 allowlist 가 form id 공간을 침범하면 방향 ② 가 눈멀게 된다.
    overlap = sorted(fence_id_set & set(TAXONOMY_CLASS_NAMES))
    if overlap:
        raise SetupError(
            f"어휘 자기모순: TAXONOMY_CLASS_NAMES 가 fence 등재 id 를 포함 {overlap} — "
            "allowlist 가 form id 를 가려 방향 ② 검출이 무력화된다 (INV-T4)"
        )

    violations = []
    evidence = {
        "root": root,
        "fence": list(fence),
        "surfaces": {},
    }

    for surface in SURFACES:
        text, surface_violation = _surface_text(root, surface)
        record = {
            "path": surface["path"],
            "desc": surface["desc"],
            "available": text is not None,
            "anchored": [],
            "missing": [],
            "extra": [],
        }
        if text is None:
            violations.append(surface_violation)
            # fail-closed — 획득 실패면 그 면의 전 id 를 누락으로 계상 (fail-open 금지)
            record["missing"] = list(fence_ids)
            evidence["surfaces"][surface["key"]] = record
            continue
        anchored = extract_anchored_ids(text)
        record["anchored"] = sorted(anchored)
        record["missing"] = [fid for fid in fence_ids if fid not in anchored]
        record["extra"] = sorted(anchored - fence_id_set - set(TAXONOMY_CLASS_NAMES))
        for fid in record["missing"]:
            violations.append(
                f"방향 ① 누락 — 면={surface['key']} ({surface['path']}): fence 등재 id `{fid}` 의 "
                f"anchor 표기가 없다 (규약: `{fid}` 또는 ({fid} — …))"
            )
        for extra in record["extra"]:
            violations.append(
                f"방향 ② 초과 — 면={surface['key']} ({surface['path']}): fence 미등재 id `{extra}` 가 "
                f"anchor 표기로 단독 등장 (fence 등재 또는 표기 정정 필요)"
            )
        evidence["surfaces"][surface["key"]] = record

    violations.extend(check_row_structure(adr_text))
    return violations, evidence


# ── self-test (합성 fixture — INV-T5: 실 아티팩트 form 문자열 재사용 0) ──
_SYN_ADR_HEAD = "### 결정 7 — 합성 불법 stop 패턴 (self-test fixture)"


def _synthetic_files():
    """합성 mini-repo 파일 맵 (상대경로 → 내용). 실 form id 는 한 건도 쓰지 않는다."""
    adr = "\n".join(
        [
            "# 합성 ADR (self-test fixture)",
            "",
            _SYN_ADR_HEAD,
            "",
            "| Pattern | Defect 사유 |",
            "|---|---|",
            "| 합성 무발화 정지 (alpha-form — 합성, CFP-2944) | 잔여작업 有 ∧ 결정 payload = 0 ∧ "
            "volitional. negative control: 다음 tool call 이 불가능했던 정지. `[advisory]` |",
            "| 합성 확인 질문 (beta-form — 합성, CFP-2944) | 잔여작업 有 ∧ payload > 0 ∧ "
            "ask-trigger 3종 미해당. negative control: decider escalation. `[advisory]` |",
            "",
            "```",
            "# 합성 inventory (self-test fixture)",
            "# 형식: <form-id> | <축> | <표 anchor 예시>",
            "alpha-form | A2 | 합성 무발화 정지",
            "beta-form | A1 | 합성 확인 질문",
            "```",
            "",
            "### 결정 8 — 합성 후행 섹션",
            "",
        ]
    )
    hook1 = "\n".join(
        [
            "def _build_reminder() -> str:",
            '    return "\\n".join([',
            '        "합성 priming ch1: `alpha-form` 금지",',
            '        "합성 priming ch1: `beta-form` 금지",',
            "    ])",
            "",
        ]
    )
    hook2 = "\n".join(
        [
            "def _build_context(subagent_type: str) -> str:",
            '    return "합성 priming ch2: `alpha-form` 금지 + `beta-form` 금지"',
            "",
        ]
    )
    guide = "\n".join(
        [
            "## 7.1 합성 Stop discipline (self-test fixture)",
            "",
            "- `alpha-form` 금지",
            "- `beta-form` 금지",
            "",
            "## 7.2 합성 후행 섹션",
            "",
        ]
    )
    return {
        HOME_MARKER: adr,
        HOOK_CH1_PATH: hook1,
        HOOK_CH2_PATH: hook2,
        CONSUMER_GUIDE_PATH: guide,
    }


def _materialize(files, root):
    for rel, content in files.items():
        path = os.path.join(root, rel)
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)


def _mut(files, rel, old, new):
    out = dict(files)
    out[rel] = out[rel].replace(old, new)
    return out


def _mut_all(files, old, new):
    return {rel: content.replace(old, new) for rel, content in files.items()}


def _drop(files, rel):
    out = dict(files)
    out.pop(rel, None)
    return out


def _self_test_cases():
    base = _synthetic_files()
    return [
        ("GREEN: 4면 form 집합 동일 + 행 구조·negative control 충족", base, 0),
        (
            "GREEN: rename invariance (MR-1 — fence·4면 일괄 rename 후에도 불변, 하드코딩 0)",
            _mut_all(base, "alpha-form", "delta-form"),
            0,
        ),
        (
            "GREEN: taxonomy class 명 anchor 등장 (form id 아님 — 방향 ② 오탐 방어)",
            _mut(base, CONSUMER_GUIDE_PATH, "- `beta-form` 금지", "- `beta-form` 금지 (`decision-null` 축)"),
            0,
        ),
        (
            "RED: 방향 ① 누락 (hook ch2 에서 한 id anchor 소실)",
            _mut(base, HOOK_CH2_PATH, "`alpha-form` 금지 + ", ""),
            1,
        ),
        (
            "RED: 방향 ② 초과 (consumer mirror 에 fence 미등재 id anchor 단독 등장)",
            _mut(base, CONSUMER_GUIDE_PATH, "- `beta-form` 금지", "- `beta-form` 금지\n- `phantom-form` 금지"),
            1,
        ),
        (
            "RED: D2 discriminant 부재 (자기 행에서 3항 중 1항 소실)",
            _mut(base, HOME_MARKER, "잔여작업 有 ∧ 결정 payload = 0 ∧ volitional.", "축은 alpha 와 동일."),
            1,
        ),
        (
            "RED: D2 자기 행 부재 (첫 셀 anchor 소실 — 사유 셀 동거 상속만 잔존)",
            _mut(
                base,
                HOME_MARKER,
                "| 합성 확인 질문 (beta-form — 합성, CFP-2944) | 잔여작업 有",
                "| 합성 확인 질문 | `beta-form` 참조. 잔여작업 有",
            ),
            1,
        ),
        (
            "RED: D3 negative control 부재 (CFP-2944 저작 행)",
            _mut(base, HOME_MARKER, "negative control: decider escalation. ", ""),
            1,
        ),
        ("RED: 면 파일 부재 fail-closed (hook ch1 삭제 — INV-T3)", _drop(base, HOOK_CH1_PATH), 1),
        (
            "RED: 면 대상 함수 부재 fail-closed (hook ch1 함수명 드리프트 — INV-T3)",
            _mut(base, HOOK_CH1_PATH, "def _build_reminder(", "def _build_reminder_renamed("),
            1,
        ),
    ]


def self_test():
    """합성 fixture 로 RED→GREEN discriminating 판별. 실 아티팩트 form 문자열 재사용 0 (INV-T5)."""
    failed = []
    for name, files, expect in _self_test_cases():
        tmp = tempfile.mkdtemp(prefix="form-set-parity-selftest-")
        try:
            _materialize(files, tmp)
            try:
                violations, _evidence = check_parity(tmp)
                got = 1 if violations else 0
                detail = f"violations={len(violations)}"
            except SetupError as e:
                got = 2
                detail = f"setup error: {e}"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        status = "OK" if got == expect else "MISMATCH"
        if got != expect:
            failed.append(name)
        print(f"  [{status}] {name} (expect {expect}, got {got}; {detail})")
    if failed:
        print(f"[self-test] FAIL — {len(failed)} case mismatch")
        return 1
    print("[self-test] PASS — 전 case 기대 일치 (GREEN/RED discriminating 실증, 합성 id 전용)")
    return 0


# ── entrypoint ──
def _resolve_root(args):
    """(root, no_op_reason) — no_op_reason 이 non-None 이면 honest no-op exit 0."""
    if not args:
        return ".", None
    target = args[0]
    if os.path.isdir(target):
        return target, None
    if os.path.isfile(target):
        if os.path.basename(target) != ADR025_BASENAME:
            return None, f"파일 인자 basename 불일치: {target}"
        # <root>/archive/adr/ADR-025-….md → root
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(target))))
        return root, None
    raise SetupError(f"경로 미존재: {target}")


def main(argv):
    args = [a for a in argv[1:] if a != "--self-test"]
    if "--self-test" in argv[1:]:
        return self_test()
    try:
        root, no_op_reason = _resolve_root(args)
    except SetupError as e:
        print(f"{MARKER} setup error: {e}", file=sys.stderr)
        return 2
    if no_op_reason is not None:
        print(f"{MARKER} ADR-025 파일 부재 — honest no-op (PASS, {no_op_reason}).")
        return 0
    if not os.path.exists(os.path.join(root, HOME_MARKER)):
        print(
            f"{MARKER} ADR-025 파일 부재 — honest no-op (PASS, consumer degradation). "
            "form-set fence 는 wrapper governance 전용."
        )
        return 0
    try:
        violations, evidence = check_parity(root)
    except SetupError as e:
        print(f"{MARKER} setup error: {e}", file=sys.stderr)
        return 2
    fence_render = ", ".join(f"{fid}({axis})" for fid, axis in evidence["fence"])
    if violations:
        print(f"{MARKER} FAIL — form-set parity 위반 (ADR-025 §A4-2 검사 방향 2 / 행 구조 요건):")
        for v in violations:
            print(f"  {v}")
        print(f"  fence 등재(원본): {fence_render}")
        return 1
    print(
        f"{MARKER} PASS — fence ↔ 4 전파면 form id 집합 동일 + 행 구조·negative control 충족. "
        f"fence 등재: {fence_render}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
