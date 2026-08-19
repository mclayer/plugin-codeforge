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

import yaml

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


# ---------------------------------------------------------------------------
# workflow YAML 술어 (8.C C-1~C-4 — AC-3 · AC-9 공용)
# ---------------------------------------------------------------------------
CHECKER_WORKFLOW_REL = ".github/workflows/fix-ledger-conformance.yml"
CHECKER_TOKENS = ("check-adr-admission", "check_adr_admission",
                  "check-fix-ledger-conformance", "check_fix_ledger_conformance")


def wf_load(wf_text):
    d = yaml.safe_load(wf_text)
    # PyYAML 은 bare `on:` 을 boolean True 키로 읽는다 (YAML 1.1) — 두 표기를 합친다.
    if isinstance(d, dict) and True in d and "on" not in d:
        d = dict(d)
        d["on"] = d.pop(True)
    return d


def wf_jobs(d):
    return (d or {}).get("jobs") or {}


def wf_steps(d):
    for job in wf_jobs(d).values():
        for st in (job or {}).get("steps") or []:
            yield st


_NON_INVOKING_HEADS = frozenset({"echo", "printf", ":", "true", "false", "cat", "#"})


def _strip_quoted(s):
    """따옴표 안 내용을 지운다 — 인용된 이름은 **호출이 아니라 언급**이다."""
    return re.sub(r"'[^']*'|\"[^\"]*\"", " ", s)


def wf_has_checker_invocation(wf_text, tokens=CHECKER_TOKENS):
    """C-1 — checker 실행 `run:` 줄이 실재한다.

    ★ 문자열 **출현**이 아니라 **명령 위치**를 본다. 직전 판은 출현만 봤고,
      `run: echo 'bash scripts/check-adr-admission.sh 는 나중에'` 가 그대로 통과했다
      (본 하네스가 mutant 로 자기검출). 이름 grep 은 dead-gate 를 못 잡는다 —
      이 Story 가 "dead 판정 술어를 이름 grep 에서 소비자 정의역으로 교체" 한 것과 같은 축이다.
    """
    for st in wf_steps(wf_load(wf_text)):
        for line in (st.get("run") or "").split("\n"):
            bare = _strip_quoted(line)
            if not any(tok in bare for tok in tokens):
                continue
            words = bare.strip().split()
            while words and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]):
                words = words[1:]                     # 선행 env 대입은 건너뛴다
            if not words:
                continue
            head = words[0].lstrip("-")
            if head.startswith("#") or head in _NON_INVOKING_HEADS:
                continue
            return True
    return False


def wf_has_dependency_resolution(wf_text):
    """C-2 — 의존성 해소 step 실재. stdlib-only 면 **그 사실을 선언**한 문면으로 대체 가능.

    명령 문자열 자체에 결속하지 않는다 (5.4 AC-3 mutant3: `pip install` 등가 변형은
    GREEN 유지가 정상 — 실 판정은 C-5 수집 테스트 수 non-zero 가 진다).
    """
    for st in wf_steps(wf_load(wf_text)):
        run = st.get("run") or ""
        if re.search(r"(pip3?\s+install|python3?\s+-m\s+pip\s+install|uv\s+pip\s+install|"
                     r"poetry\s+install|npm\s+(ci|install)|apt-get\s+install)", run):
            return True
    return bool(re.search(r"stdlib[- ]only", wf_text, re.I))


def wf_no_continue_on_error(wf_text):
    """C-3 — `continue-on-error` 부재 (tier 강등 차단)."""
    d = wf_load(wf_text)
    for job in wf_jobs(d).values():
        if "continue-on-error" in (job or {}):
            return False
        for st in (job or {}).get("steps") or []:
            if "continue-on-error" in (st or {}):
                return False
    return True


def wf_no_path_filters(wf_text):
    """C-4 (앞 절) — `paths` · `paths-ignore` 부재.

    무관 변경 PR 에서 workflow 레벨 skip 이 나면 context 가 **pending 으로 잔존**한다.
    """
    on = (wf_load(wf_text) or {}).get("on")
    if isinstance(on, dict):
        for ev in on.values():
            if isinstance(ev, dict) and ("paths" in ev or "paths-ignore" in ev):
                return False
    return True


def wf_job_if_always_reports(wf_text):
    """C-4 (뒤 절) — job 레벨 `if:` 가 status 를 미report 로 만들지 않는다.

    해석 seam (리뷰 대상으로 명시): 허용 = 표현식의 변수가 `github.repository` 뿐인
    repo 가드. PR 내용(`github.event…` · `contains(…)` · label · path)에 조건을 거는
    `if:` 는 "대상 변경이 없는 PR 에서도 결론을 report" 요구와 정면 충돌하므로 위반이다.
    """
    for job in wf_jobs(wf_load(wf_text)).values():
        cond = (job or {}).get("if")
        if cond is None:
            continue
        expr = str(cond)
        used = set(re.findall(r"github\.[A-Za-z_.]+", expr)) | set(
            re.findall(r"\b(contains|startsWith|endsWith)\s*\(", expr))
        if used - {"github.repository"}:
            return False
    return True


def wf_invocation_contract(wf_text):
    """C-1 ∧ C-2 ∧ C-3 ∧ C-4 (합성 판정 — 개별 leg 은 위 5 함수)."""
    return (wf_has_checker_invocation(wf_text) and wf_has_dependency_resolution(wf_text)
            and wf_no_continue_on_error(wf_text) and wf_no_path_filters(wf_text)
            and wf_job_if_always_reports(wf_text))


# ---------------------------------------------------------------------------
# 10 FIX Ledger 컬럼 집합 + 유령 컬럼 지시 술어 (AC-11 · AC-6 공용)
# ---------------------------------------------------------------------------
# fix-event-v1 이 정의하는 10 표 컬럼 (계약 문면에서 파생 — 하드코딩 열거가 아니라 대조용 기본값).
SECTION10_COLUMNS = frozenset({
    "Iter", "시각", "레인", "트리거", "원인 판정", "재실행 범위", "RESET?",
    "debate_artifact_ref", "reasoning_carryover", "affected_scope",
    "affected_paths_with_depth", "reproducer_command", "replay_verdict",
})

# 정당 사용(집계 축 `root_cause_class` / `root_cause_distribution`)과 반드시 구별한다.
# 무차별 grep 봉합은 false RED + 실동작 스크립트 파괴다 (4.3 E-7).
_COLREF_RE = re.compile(
    r"([A-Za-z_][A-Za-z0-9_]*(?:\s*\+\s*[A-Za-z_][A-Za-z0-9_]*)*)\s*(?:column|컬럼)"
)
_DIRECTIVE_CTX_RE = re.compile(r"(§\s*10|FIX Ledger row|10 FIX Ledger)")
_RECORD_RE = re.compile(r"(기록|record)")


def contract_section10_columns(contract_text):
    """계약 문서의 10 표 헤더 행에서 컬럼명 집합을 뽑는다 (열거 하드코딩 대체)."""
    for header, _rows in md_tables(contract_text):
        cells = [c.strip() for c in header]
        if "Iter" in cells and any("원인" in c for c in cells):
            return {c for c in cells if c}
    return set(SECTION10_COLUMNS)


def phantom_column_directives(text, columns=None):
    """10 표에 **없는** 컬럼명으로 기록을 지시하는 site 목록 -> [(lineno, 컬럼명, 줄)].

    술어를 "10 표 기록 지시" 문맥으로 좁힌다 — 무차별 `root_cause` grep 은
    `root_cause_class` 정당 사용 32 파일을 false RED 로 만든다 (4.3 E-7).
    """
    cols = set(columns) if columns else set(SECTION10_COLUMNS)
    hits = []
    for lineno, ln in enumerate(text.split("\n"), 1):
        if not _DIRECTIVE_CTX_RE.search(ln) or not _RECORD_RE.search(ln):
            continue
        for m in _COLREF_RE.finditer(ln):
            for name in [p.strip() for p in m.group(1).split("+")]:
                if name and name not in cols:
                    hits.append((lineno, name, ln.strip()))
    return hits


def run_rc(argv, cwd=None, env=None):
    """rc 를 파이프 없이 얻는다 (규율 7). (rc, stdout, stderr) 반환."""
    e = dict(os.environ)
    e["PYTHONIOENCODING"] = "utf-8"
    if env:
        e.update(env)
    p = subprocess.run(argv, cwd=str(cwd or REPO_ROOT), capture_output=True,
                       text=True, encoding="utf-8", errors="replace", env=e)
    return p.returncode, p.stdout, p.stderr
