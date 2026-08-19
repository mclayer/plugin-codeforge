"""CFP-2985 Phase 2 — RTM 8.1.1 명명 테스트 43 의 공유 술어 + 대조군 하네스.

계약(SSOT) = internal-docs `wrapper/change-plans/cfp-2985-fix-root-cause-telemetry.md` 8
             (8.1 자산 4층 / 8.1.1 RTM / 8.2 hollow 방지 5규율 + H-6 / 8.C CI 실행 보장)
           + internal-docs `wrapper/stories/CFP-2985.md` 5.3 AC 20 · 5.4 mutant 6방향
           + wrapper `archive/adr/ADR-181-verification-domain-deficit-normative.md` 결정 5 3-dt (iv)

본 모듈은 **테스트가 아니다** — 술어 구현과 대조군 하네스만 제공한다.

하네스 규율 (이 Story 가 16 라운드에 걸쳐 실측한 것):
  H-1 독립성        : mutation 이 대상 술어 **단독으로** 판정을 뒤집는가.
  H-4 대조군 의무   : mutant 를 해석하기 **전에** control 이 GREEN 임을 확인한다.
                      (무효 mutant 5건이 전부 정반대 결론 직전까지 갔다.)
  H-6 묶음 ablation 금지 : mutant 는 **하위 조건 단위로 개별** 주입한다.
                      묶으면 판별 0 인 leg 이 숨는다 (4 라운드 미검출 실측).
  양성 ∧ 음성 쌍     : 존재-assert 단독은 **확대 방향에 구조적으로 무력**하다
                      (등식 pin -> 존재 assert 로 바꾸자 +425행 60% 팽창이 9/9 통과).
                      -> 모든 술어에 `green_variants`(등가변형 = GREEN 유지) 를 함께 건다.
  L3 정수 pin 금지   : 실 코퍼스는 남의 커밋으로 움직인다 -> immutable SHA 고정 + 존재/부등식 assert.
  자기참조 계수 금지 : 테스트가 자기 파일 안 문자열을 세면 그 줄 자신이 계수에 들어간다.

정직 천장 (declared): 본 스위트는 wrapper repo 안에서 실행된다. Story · Change Plan 은
  internal-docs repo 소재라 wrapper CI 에 **비가시**하다. 그 축의 leg 은 환경변수
  `CFP2985_INTERNAL_DOCS` 주입 시에만 실물 대조가 성립하며, 미주입 시에도 각 테스트의
  **discriminating core(합성 대조군 · mutant)는 그대로 실행**된다 (전량 skip = dead test 금지).
  이 천장을 지우고 "실 코퍼스를 검증한다" 고 인용하면 over-claim 이다.
"""

import os
import re
import subprocess
from pathlib import Path

# tests/cfp2985/ -> tests/ -> repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

# L3 immutable ref (8.1 — `origin/main` 지정 금지: 2 커밋 전진에 388->390 이동 실측)
CORPUS_SHA = "7e3127a8d3a385bc820632f55d2c18fe870f20db"
CUT_SHA = CORPUS_SHA                       # Story 7.11 자기적용 baseline cut (AC-10a)
CUT_TIME = "2026-08-16T18:06:03+09:00"

STORY_REL = "wrapper/stories/CFP-2985.md"
PLAN_REL = "wrapper/change-plans/cfp-2985-fix-root-cause-telemetry.md"
ADR181_REL = "archive/adr/ADR-181-verification-domain-deficit-normative.md"
CONTRACT_FIX_EVENT_REL = "docs/inter-plugin-contracts/fix-event-v1.md"
CONTRACT_DEBATE_REL = "docs/inter-plugin-contracts/debate-protocol-v1.md"
CONTRACT_LABEL_REL = "docs/inter-plugin-contracts/label-registry-v2.md"
REGISTRY_REL = "docs/evidence-checks-registry.yaml"
REVIEW_PL_BASE_REL = "plugins/codeforge-review/templates/review-pl-base.md"

# fix-event-v1 v1.6 이 판정해야 하는 `원인 판정` enum-밖 실측 4축 (Story 5.3 AC-1).
OFFAXIS_4 = ("요구사항", "환경", "설계-리뷰", "구현-리뷰")


# ---------------------------------------------------------------------------
# 입력원
# ---------------------------------------------------------------------------
def wrapper_path(rel):
    return REPO_ROOT / rel


def wrapper_text(rel):
    """wrapper repo 상대경로 텍스트. 부재 시 None (판정불가와 위반을 구별하기 위해)."""
    p = wrapper_path(rel)
    return p.read_text(encoding="utf-8") if p.is_file() else None


def internal_docs_root():
    """internal-docs 체크아웃 루트. 미주입이면 None.

    자동 탐색을 하지 않는다 — 주변 worktree 를 뒤지면 "어느 커밋을 읽었는지" 가
    환경 의존이 되어 L3 immutable-ref 규율이 무너진다. 명시 주입만 인정한다.
    """
    v = os.environ.get("CFP2985_INTERNAL_DOCS", "").strip()
    if not v:
        return None
    p = Path(v)
    return p if p.is_dir() else None


def internal_docs_text(rel):
    """internal-docs 상대경로 텍스트 또는 None(미주입/부재).

    pytest.skip 을 쓰지 않는다 — skip 하면 같은 함수 안 discriminating core 가
    리포트에서 사라져 "돌았는데 안 돈 것처럼" 보인다.
    """
    root = internal_docs_root()
    if root is None:
        return None
    p = root / rel
    return p.read_text(encoding="utf-8") if p.is_file() else None


def internal_docs_absent_reason(rel):
    """실물 leg 미실행 사유 문자열 (보고용 — 침묵 skip 금지)."""
    root = internal_docs_root()
    if root is None:
        return ("CFP2985_INTERNAL_DOCS 미주입 -> internal-docs 축 실물 leg 미실행 "
                "(declared 천장; discriminating core 는 실행됨)")
    return "%s 부재 @ %s" % (rel, root)


# ---------------------------------------------------------------------------
# H-4 / H-6 / 양성 ∧ 음성 하네스
# ---------------------------------------------------------------------------
def assert_discriminating(predicate, control, mutants, green_variants=(), *, label):
    """대조군 선통과 -> mutant 개별 판별 -> 등가변형 GREEN 유지 를 한 실행에서 대조한다.

    Args:
      predicate: 입력 -> bool (True=GREEN/적법, False=RED/위반). bool 이 아니면 실패시킨다.
      control:   조작 0 인 정상 입력. **먼저** GREEN 이어야 한다 (H-4).
      mutants:   [(이름, 입력)] — 각각 **단독으로** RED 를 내야 한다 (H-1 · H-6 개별 주입).
      green_variants: [(이름, 입력)] — 표기 등가변형. GREEN 유지여야 한다 (확대 방향 방어).
    """
    cv = predicate(control)
    assert cv is True, (
        "[%s] 대조군(control)이 GREEN 이 아니다 (verdict=%r) — 이 상태의 mutant RED 는 "
        "항진 오라클과 구별 불가(H-4). mutant 해석을 중단한다." % (label, cv)
    )

    survivors = []
    for name, mutant in mutants:
        mv = predicate(mutant)
        if mv is not False:
            survivors.append((name, mv))
    assert not survivors, (
        "[%s] mutant 생존 = hollow(H-1). 개별 주입(H-6) 기준 생존 목록: %r" % (label, survivors)
    )

    over_broad = []
    for name, variant in green_variants:
        vv = predicate(variant)
        if vv is not True:
            over_broad.append((name, vv))
    assert not over_broad, (
        "[%s] 등가변형이 RED = 술어가 표기 앵커에 결속(과대). 목록: %r" % (label, over_broad)
    )


# ---------------------------------------------------------------------------
# 마크다운 표 파싱 (AC-11 / AC-17 / AC-19 공용)
# ---------------------------------------------------------------------------
_FENCE = re.compile(r"^\s*(```|~~~)")


def strip_fenced(lines):
    """코드펜스 내부 줄을 None 으로 마스킹 (펜스 안 표를 표로 세지 않는다)."""
    out = []
    infence = False
    for ln in lines:
        if _FENCE.match(ln):
            infence = not infence
            out.append(None)
            continue
        out.append(None if infence else ln)
    return out


def _is_pipe_row(ln):
    return ln is not None and ln.lstrip().startswith("|")


def _is_separator_row(ln):
    if not _is_pipe_row(ln):
        return False
    cells = ln.strip().strip("|").split("|")
    return bool(cells) and all(re.fullmatch(r"\s*:?-{2,}:?\s*", c) for c in cells)


def split_cells(row):
    r"""셀 분해 — `\|` 이스케이프 해제 + 인라인 코드스팬 안 파이프를 분리자로 취급하지 않는다.

    (Change Plan 8 이 승계한 3.0(a-3) 표 경계 규칙 (v) 의 wrapper 측 대응.)
    """
    cells, buf, in_code, i = [], [], False, 0
    s = row.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            buf.append("|")
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
            buf.append(ch)
            i += 1
            continue
        if ch == "|" and not in_code:
            cells.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    cells.append("".join(buf).strip())
    return cells


def md_tables(text):
    """[(header_cells, [row_cells...])] — 펜스 제외. 빈 줄이 표를 끊는다."""
    lines = strip_fenced(text.split("\n"))
    tables, i, n = [], 0, len(lines)
    while i < n:
        if _is_pipe_row(lines[i]) and i + 1 < n and _is_separator_row(lines[i + 1]):
            header = split_cells(lines[i])
            rows, j = [], i + 2
            while j < n and _is_pipe_row(lines[j]):
                if not _is_separator_row(lines[j]):
                    rows.append(split_cells(lines[j]))
                j += 1
            tables.append((header, rows))
            i = j
            continue
        i += 1
    return tables


def norm_header(cell):
    """헤더 정규화 — 장식 strip + 소문자 + 공백 축약."""
    c = cell.replace("*", "").replace("`", "")
    c = re.sub(r"[★☆]", "", c)
    return re.sub(r"\s+", " ", c).strip().lower()


def norm_cell(cell):
    """셀 값 정규화 (Story 3.0(a-4) P-AD 승계).

    선두 별표 · 공백 strip -> 장식(`**` / `__` / 백틱 / `~~`) strip
    -> 괄호 주석 후행부 절단 -> strip.
    """
    c = cell.strip()
    c = re.sub(r"^[★☆\s]+", "", c)
    for dec in ("**", "__", "~~", "`"):
        c = c.replace(dec, "")
    c = re.sub(r"\s*[(（].*$", "", c)
    return c.strip()


def select_tables(tables, required_headers):
    """헤더가 required 를 **동시 보유**하는 표들 (P-R — 컬럼명 단독 식별 금지)."""
    out = []
    for header, rows in tables:
        hs = [norm_header(h) for h in header]
        if all(any(req in h for h in hs) for req in required_headers):
            out.append((header, rows))
    return out


def col_index(header, needle):
    for i, h in enumerate(header):
        if needle in norm_header(h):
            return i
    return -1


# ---------------------------------------------------------------------------
# 공용 정규식 (문자군 주의: ERE `[a-z]` 는 대문자 배제 — 본 모듈은 Python `re` 전용)
# ---------------------------------------------------------------------------
SHA40_RE = re.compile(r"\b[0-9a-f]{40}\b")
ISO8601_KST_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+09:?00\b")
CARRIER_RE = re.compile(r"#\d+")
DUEDATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def run_rc(argv, cwd=None, env=None):
    """rc 를 파이프 없이 얻는다 (규율 7). (rc, stdout, stderr) 반환."""
    e = dict(os.environ)
    e["PYTHONIOENCODING"] = "utf-8"
    if env:
        e.update(env)
    p = subprocess.run(argv, cwd=str(cwd or REPO_ROOT), capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=e)
    return p.returncode, p.stdout, p.stderr
