#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ADR-181 §결정 5 ③-dt admission checker (D-7c) — 참조 구현.

수용 기준 SSOT = ``archive/adr/ADR-181-verification-domain-deficit-normative.md``
§결정 5 ③-dt **(iv) 결정표**. 본 모듈은 그 표의 ``(verdict, exit 사유)`` 쌍을
재현하는 것을 유일한 정합 조건으로 삼는다.

**층 지위** — ADR-181 (0-a) 3층 중 **층 1((iv) 결정표)** 이 판정 SSOT 이고 (ii)/(iii)
산문은 층 3(설명용)이다. 본 구현이 (iv) 표와 어긋나면 **어긋난 쪽은 본 구현**이다.

평가 순서 (ADR-181 (iv) `평가 순서` 행 + (vi-1) 말미 확정)::

    b1 -> b2 -> b3(파싱) -> b4 -> b5  ->  ADRQ(정의역)  ->  발행일 정규화  ->  (iii) leg

정직 라벨 (ADR-181 §결정 6 · §결정 3 C-2):
  * ``ladder-unwired`` 의 ``배선`` 은 **호출이 아니라 출현**이고 workflow 축은
    **설치 실재**다. 따라서 사다리 GREEN 은 `declared` 이며 *"기계 강제된다"* 의
    `normative` 단정이 아니다 ((iv-L) `dead()` 접합부 문단 · (iv-L3) 천장 문단).
  * ``REPO`` 는 repo 토큰의 **부재**만 봉인하며 *어느* repo 인지 검증하지 않는다.
  * ``배선_wf`` 는 basename twin 의 **blob 존재**만 본다 — byte-parity 가 아니다.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import subprocess
import sys
import unicodedata
from typing import Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - 환경 결손을 조용히 통과시키지 않는다
    sys.stderr.write("check_adr_admission: PyYAML 이 필요합니다 (pip install pyyaml)\n")
    raise

# --------------------------------------------------------------------------
# 값공간 — verdict 3값 (ADR-181 (iv) 기대 열 3-값화 문단)
# --------------------------------------------------------------------------
GREEN = "GREEN"
RED = "RED"
OUT = "OUT"          # ADRQ 불성립 ∧ 자격 박탈 아님 (ⓑ) = 검사 없음 ≠ 통과

# exit 사유 토큰 — (iii) 면제 축 + (iv-L2) 사다리 축 + 경계/정의역/발행일 축
R_FM_BOUNDARY = "fm-boundary"
R_FM_PARSE = "fm-parse-error"
R_DOMAIN_ESCAPE = "domain-escape"
R_PUBDATE_MISSING = "pubdate-missing"
R_PUBDATE_VALUE = "pubdate-value"
R_MEA_MISSING = "mea-missing"
R_LINE_FORM = "line-form"
R_CARRIER_TOKEN = "carrier-token"
R_EXPIRY_TOKEN = "expiry-token"
R_REPO_TOKEN = "repo-token"
R_TOKEN_ORDER = "token-order"
R_EXPIRY_VALUE = "expiry-value"
R_EXPIRED = "expired"
R_OVER_CAP = "over-cap"
R_LADDER_PATH_KEY = "ladder-path-key"
R_LADDER_PATH_MISSING = "ladder-path-missing"
R_LADDER_UNWIRED = "ladder-unwired"

MEA_KEY = "mechanical_enforcement_actions"

# (vi-2) 만기 상한 = 발행일 + 180일. 값의 자의성은 ADR-181 (vi-2) 말미가 declare 한다.
EXPIRY_CAP_DAYS = 180

# (vii) ③-key — 경로 키 closed-set (FIX Iter 11: 8원 -> 3원)
PATH_KEYS: tuple[str, ...] = ("script_path", "workflow", "workflow_path")
# 경로 추출원이 **아니다** — 되돌리면 (iv) 행 52·53 이 ladder-path-missing 으로 오진단된다.
NON_PATH_KEYS: tuple[str, ...] = ("action", "check", "detect_command", "script", "path")

# --------------------------------------------------------------------------
# (ii) 고정 토큰 형식 — 캡처 c 안에서만 탐색한다
# --------------------------------------------------------------------------
# SCOPE = frontmatter 블록 (파일 전체 아님). DOTALL 금지 · MULTILINE.
RE_LINE = re.compile(
    r"^" + re.escape(MEA_KEY) + r":[ \t]*\[\][ \t]*#(?P<c>[^\n]*)$",
    re.MULTILINE,
)
RE_CAR = re.compile(r"(?<![0-9A-Za-z_-])carrier=#(?P<n>[1-9][0-9]{0,6})(?![0-9])")
RE_EXP = re.compile(r"(?<![0-9A-Za-z_-])expiry=(?P<d>[0-9]{4}-[0-9]{2}-[0-9]{2})(?![0-9])")
RE_REPO = re.compile(r"(?<![0-9A-Za-z_-])\[repo=(?P<r>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\]")
RE_PFX = re.compile(
    r"^[ \t]*carrier=#[1-9][0-9]{0,6}[ \t]+expiry=[0-9]{4}-[0-9]{2}-[0-9]{2}"
    r"[ \t]+\[repo=[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\]"
)

# b4 의 `FM-형 줄` 리터럴 (ADR-181 경계 블록 — FIX Iter 10 확정)
RE_FMLINE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*:([ \t].*)?$")


class Verdict:
    """``(verdict, exit 사유)`` 쌍 — 수용 기준의 축."""

    __slots__ = ("verdict", "reason", "detail")

    def __init__(self, verdict: str, reason: str | None, detail: str | None = None) -> None:
        self.verdict = verdict
        self.reason = reason
        self.detail = detail

    def as_pair(self) -> tuple[str, str | None]:
        return (self.verdict, self.reason)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Verdict):
            return self.as_pair() == other.as_pair()
        if isinstance(other, tuple):
            return self.as_pair() == tuple(other)
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.as_pair())

    def __repr__(self) -> str:  # pragma: no cover - 진단용
        return f"Verdict({self.verdict!r}, {self.reason!r})"


# --------------------------------------------------------------------------
# front-end — 입력 정규화 + 경계 b1~b5
# --------------------------------------------------------------------------
def normalize_input(text: str) -> str:
    """유니코드 정규화는 판정을 바꾸는 자유 변수다 (ADR-181 front-end `NFC` 축).

    판별 행 47K (U+212A KELVIN SIGN -> ASCII ``K`` 정준 싱글턴).
    """
    return unicodedata.normalize("NFC", text)


def split_frontmatter(text: str) -> tuple[str | None, list[str], int]:
    """b1·b2 를 적용해 frontmatter 텍스트를 잘라낸다 (독법 β).

    반환 ``(fm_text | None, lines, terminator_index)``. ``fm_text`` 가 ``None`` 이면
    b1 또는 b2 위반이다 — ``b1`` 을 **위치 탐색 전제**로 쓴다(β 규정 독법).
    """
    lines = text.split("\n")
    # b1 — 파일이 정확히 `---` + LF 로 시작 (BOM·선행 공백·CRLF 불허)
    if not text.startswith("---\n"):
        return None, lines, -1
    # b2 — 1행 이후 첫 단독 `^---$` = FM 종단
    for idx in range(1, len(lines)):
        if lines[idx] == "---":
            return "\n".join(lines[1:idx]), lines, idx
    return None, lines, -1


def parse_frontmatter(fm_text: str) -> tuple[dict | None, str | None]:
    """b3 — YAML 파싱 성공 ∧ 결과가 mapping. 예외는 skip 이 아니라 named RED."""
    try:
        data = yaml.safe_load(fm_text)
    except Exception:
        return None, R_FM_PARSE
    if not isinstance(data, dict):
        return None, R_FM_PARSE
    return data, None


def check_b4(lines: Sequence[str], terminator_index: int) -> bool:
    """b4 — FM 종단 다음 줄부터 첫 비-FM-형·비-공백 줄까지, FM-형 줄이 0.

    ★ 천장 (`declared`) — 창은 **첫 비-FM-형 비공백 줄에서 닫힌다**. 종단 직후에 평문
    1줄만 두면 창이 공집합이 되고 뒤로 밀려난 키는 몇 개든 검사되지 않는다
    (ADR-181 행 33b 천장 전시 · 실 ADR 코퍼스 174 전건에서 이 창은 공집합).
    """
    for line in lines[terminator_index + 1:]:
        if line.strip() == "":
            continue
        if RE_FMLINE.match(line):
            return False
        return True
    return True


def check_b5(head_fm: dict, base_fm: dict | None) -> bool:
    """b5 — base 존재 시 ``keys(FM_head) ⊇ keys(FM_base)``.

    ★ 천장 (`declared`) — **키 집합만** 보고 값을 비교하지 않는다. 그래서 만기를 둔 채
    ``date:`` 한 줄을 미래로 옮겨 상한 창을 재개하는 회피는 본 술어로 막히지 않는다
    (ADR-181 (vi-1) 15번째 회피 경로 천장).
    """
    if base_fm is None:
        return True
    return set(head_fm.keys()) >= set(base_fm.keys())


def adrq(fm: dict | None) -> bool:
    """``ADRQ(t)`` — ADR 자격 술어. ``ADR-*.md`` 는 파일명 패턴이지 자격 술어가 아니다.

    타입 불문 (실측 int 171 · str 2 · null 1) — int 만 자격으로 두면 좁힘 오류다.
    """
    if fm is None:
        return False
    return "adr_number" in fm and fm["adr_number"] is not None


def resolve_pubdate(fm: dict) -> tuple[_dt.date | None, str | None]:
    """발행일 정규화 (front-end — leg 이 재구현하지 않는다).

    PyYAML 이 ``date: 2026-08-16`` 을 ``datetime.date`` 로 이미 변환하므로 문면의
    ``date.fromisoformat(발행일)`` 을 그대로 적용하면 정상 ADR 전건에서 TypeError 다
    (ADR-181 FIX Iter 8 P1-1). 타입별 분기를 리터럴로 적는다.
    """
    if "date" not in fm or fm["date"] is None:
        return None, R_PUBDATE_MISSING
    value = fm["date"]
    if isinstance(value, _dt.datetime):
        return value.date(), None
    if isinstance(value, _dt.date):
        return value, None
    if isinstance(value, str):
        try:
            return _dt.date.fromisoformat(value), None
        except ValueError:
            return None, R_PUBDATE_VALUE
    return None, R_PUBDATE_VALUE


# --------------------------------------------------------------------------
# (iv-L) repo 상태 — 사다리 3연언지의 입력원
# --------------------------------------------------------------------------
# 접두 리터럴 4종. ★ 제거 순서 = P-4 -> P-3 -> P-2 -> P-1 (긴 접두부터, `./` 마지막).
# 순서가 판정을 뒤집는 중첩 표기가 존재한다 (ADR-181 (iv-L) FIX Iter 12 규정).
RE_P4 = re.compile(r"\$\{\{[ \t]*github\.workspace[ \t]*\}\}/")
RE_P3 = re.compile(r"\$\{GITHUB_WORKSPACE\}/")
RE_P2 = re.compile(r"\$GITHUB_WORKSPACE/")
# P-1 `./` — 좌측 인접 문자가 [A-Za-z0-9_./-] 가 아닐 때만 (`../` 보호)
RE_P1 = re.compile(r"(?<![A-Za-z0-9_./-])\./")

RE_COMMENT_LINE = re.compile(r"^[ \t]*#")


def normalize_paths(text: str) -> str:
    """``정규화(t)`` — 접두 리터럴 4종을 규정 순서로 제거한다."""
    text = RE_P4.sub("", text)
    text = RE_P3.sub("", text)
    text = RE_P2.sub("", text)
    text = RE_P1.sub("", text)
    return text


def strip_comment_lines(text: str) -> str:
    """``run블롭'`` — **선두** 주석줄만 빈 줄로 치환한다.

    ★ 천장 (`declared`) — 행 중간 trailing 주석은 제거하지 않는다. 셸에서 ``#`` 가
    주석을 여는지는 인용 상태에 의존하며 정규식 근사는 fail-closed 오분류를 낸다
    (ADR-181 (iv-L) β 천장 — 오분류 실물 witness 기재).
    """
    return "\n".join("" if RE_COMMENT_LINE.match(ln) else ln for ln in text.split("\n"))


def _collect_run_scalars(node: object, out: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "run" and isinstance(value, str):
                out.append(value)
            else:
                _collect_run_scalars(value, out)
    elif isinstance(node, list):
        for item in node:
            _collect_run_scalars(item, out)


class RepoState:
    """``REPO_STATE`` — 사다리 3연언지의 입력원 (immutable ref 권장).

    ``실재(p)``  = ``git ls-tree -r --name-only <rev> -- p`` 출력에 ``p`` 완전일치 줄 존재
                   (즉 blob 이어야 한다 — 디렉터리·부분경로는 실재가 아니다).
    ``배선(p)``  = 정규화(run블롭') 에서 ``p`` 가 경로 경계와 함께 등장 (**출현**, 호출 아님).
    ``배선_wf`` = ``INSTALL(p)`` 가 트리의 blob 으로 실재 (**설치 실재**).
    """

    def __init__(self, rev: str, repo_root: str | None = None) -> None:
        self.rev = rev
        self.repo_root = repo_root
        self._tree: set[str] | None = None
        self._wire_text: str | None = None

    # -- git primitives ----------------------------------------------------
    def _git(self, *args: str) -> str:
        cmd = ["git"]
        if self.repo_root:
            cmd += ["-C", self.repo_root]
        cmd += list(args)
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if proc.returncode != 0:
            raise RuntimeError(
                f"git {' '.join(args)} 실패 (rc={proc.returncode}): {proc.stderr.strip()}"
            )
        return proc.stdout

    @property
    def tree(self) -> set[str]:
        if self._tree is None:
            out = self._git("ls-tree", "-r", "--name-only", self.rev)
            self._tree = {ln for ln in out.split("\n") if ln}
        return self._tree

    def exists(self, path: str) -> bool:
        """``실재(p)`` — 완전일치 blob 존재. 실행권한 비트·확장자는 보지 않는다."""
        return path in self.tree

    @property
    def wire_text(self) -> str:
        """``정규화(run블롭')`` — 판정 텍스트 (주석줄 제거 후 접두 정규화)."""
        if self._wire_text is None:
            blobs: list[str] = []
            for path in sorted(self.tree):
                if not path.startswith(".github/workflows/"):
                    continue
                if not (path.endswith(".yml") or path.endswith(".yaml")):
                    continue
                try:
                    content = self._git("show", f"{self.rev}:{path}")
                    doc = yaml.safe_load(content)
                except Exception:
                    continue
                _collect_run_scalars(doc, blobs)
            raw = "\n".join(blobs)
            self._wire_text = normalize_paths(strip_comment_lines(raw))
        return self._wire_text

    def wired_script(self, path: str) -> bool:
        """스크립트 축 ``배선`` — 경계 매치. 재는 것은 **출현**이지 호출이 아니다."""
        pattern = (
            r"(?<![A-Za-z0-9_./-])" + re.escape(path) + r"(?![A-Za-z0-9_.-])"
        )
        return re.search(pattern, self.wire_text) is not None

    def wired_workflow(self, path: str) -> bool:
        """workflow 축 ``배선_wf`` — ``INSTALL(p)`` 설치 실재 ((iv-L3) 분기).

        ★ 천장 (`declared`) — basename twin 의 **존재**만 본다. 내용 동일성(byte-parity)도,
        ``on:`` 트리거의 존재·종류도 묻지 않는다. ``.github/workflows/`` 하위 경로는
        ``INSTALL(p) = p`` 이므로 이 연언지가 **항진**이 된다(행 50d 천장 전시).
        """
        return self.exists(self.install_path(path))

    @staticmethod
    def install_path(path: str) -> str:
        """``INSTALL(p)`` — 하위면 자신, 아니면 ``.github/workflows/`` + basename."""
        if path.startswith(".github/workflows/"):
            return path
        return ".github/workflows/" + path.rsplit("/", 1)[-1]

    def wired(self, key: str, path: str) -> bool:
        """``배선(k, p)`` — 분기 기준은 **항목의 경로 키**이지 경로 문자열의 모양이 아니다."""
        if key in ("workflow", "workflow_path"):
            return self.wired_workflow(path)
        return self.wired_script(path)


# --------------------------------------------------------------------------
# (iii) 판정 술어 — 면제 축 / 사다리 축
# --------------------------------------------------------------------------
def exempt(fm: dict, fm_text: str, as_of: _dt.date, pubdate: _dt.date) -> str | None:
    """``exempt(file)`` — 성립이면 ``None``, 실패면 exit 사유 토큰.

    leg 평가 순서가 규정이며 (iv) 표의 ``exit 사유`` 열이 그 순서의 관측이다.
    """
    # mea 키 존재 — 정규식이 아니라 **YAML 키 멤버십** (행 8·27 이 이 계층을 판별한다)
    if MEA_KEY not in fm:
        return R_MEA_MISSING

    # LINE 이 SCOPE(frontmatter 블록) 안에서 정확히 1회 매치
    matches = RE_LINE.findall(fm_text)
    if len(matches) != 1:
        return R_LINE_FORM
    comment = RE_LINE.search(fm_text).group("c")

    # 복수 토큰 = 선택 규칙이 아니라 RED (max 를 택하면 fail-open 경로가 생긴다)
    cars = RE_CAR.findall(comment)
    if len(cars) != 1:
        return R_CARRIER_TOKEN
    exps = RE_EXP.findall(comment)
    if len(exps) != 1:
        return R_EXPIRY_TOKEN
    repos = RE_REPO.findall(comment)
    if len(repos) != 1:
        return R_REPO_TOKEN

    # PFX 가 캡처 c 의 **선두**에 매치 (부인 산문 매설 봉인)
    if RE_PFX.match(comment) is None:
        return R_TOKEN_ORDER

    # 값 판정은 값 파서에 맡기고 술어는 형식만 본다 — 예외는 skip 이 아니라 named RED
    try:
        expiry = _dt.date.fromisoformat(exps[0])
    except ValueError:
        return R_EXPIRY_VALUE

    if not (expiry >= as_of):
        return R_EXPIRED
    if not (expiry <= pubdate + _dt.timedelta(days=EXPIRY_CAP_DAYS)):
        return R_OVER_CAP
    return None


def ladder(fm: dict, repo: RepoState) -> tuple[bool, str | None]:
    """``ladder(file)`` — 성립이면 ``(True, None)``, 실패면 ``(False, 사유)``.

    ★ 다중 경로 키 = **ALL(연언)** 이다 (ADR-181 (vii) FIX Iter 13 규정 — ANY 는 fail-open).
    ★ 항목 사이도 (iii) 문면 *"각 항목에서"* 를 따라 **ALL** 이다. 다만 (iv) 표는 이 축을
      행사하지 않는다(``K`` 항목 2개 이상인 행 = 0) — ADR-181 16번째 회피 경로 천장.
    """
    items = fm.get(MEA_KEY)
    if not isinstance(items, list) or len(items) < 1:
        return False, None  # 사다리 미선택 (사유 없음)

    for item in items:
        if not isinstance(item, dict):
            return False, R_LADDER_PATH_KEY
        present = [k for k in PATH_KEYS if k in item]
        if not present:
            return False, R_LADDER_PATH_KEY
        for key in present:
            value = item[key]
            if not isinstance(value, str) or not value:
                return False, R_LADDER_PATH_KEY
            if not repo.exists(value):
                return False, R_LADDER_PATH_MISSING
            if not repo.wired(key, value):
                return False, R_LADDER_UNWIRED
    return True, None


def admissible(fm: dict, fm_text: str, as_of: _dt.date, pubdate: _dt.date,
               repo: RepoState) -> Verdict:
    """``admissible(file) := ladder(file) OR exempt(file)``.

    두 경로를 **모두 평가**하고 OR 를 취한다. 사유 귀속만 (iv-L2) 규칙을 따른다 —
    ``len(mea) >= 1`` 이면 사다리 토큰, 아니면 면제 토큰.
    """
    ladder_ok, ladder_reason = ladder(fm, repo)
    exempt_reason = exempt(fm, fm_text, as_of, pubdate)
    if ladder_ok or exempt_reason is None:
        return Verdict(GREEN, None)

    items = fm.get(MEA_KEY)
    if isinstance(items, list) and len(items) >= 1:
        return Verdict(RED, ladder_reason)
    return Verdict(RED, exempt_reason)


# --------------------------------------------------------------------------
# 통합 평가 — 경계 우선
# --------------------------------------------------------------------------
def evaluate(head_text: str, base_text: str | None, as_of: _dt.date,
             repo: RepoState) -> Verdict:
    """``(verdict, exit 사유)`` 쌍을 낸다. 평가 순서 = 경계 우선.

    경계·파싱이 깨진 입력을 정의역 층에서 먼저 걸러내면 이 문서가 세 번 고발한
    *"예외 = skip"* 이 정의역 층에서 부활한다 — 그래서 경계가 먼저다.
    """
    head_text = normalize_input(head_text)

    fm_text, lines, term = split_frontmatter(head_text)
    if fm_text is None:                       # b1 또는 b2
        return Verdict(RED, R_FM_BOUNDARY)

    head_fm, parse_reason = parse_frontmatter(fm_text)
    if parse_reason is not None:              # b3
        return Verdict(RED, parse_reason)

    if not check_b4(lines, term):             # b4
        return Verdict(RED, R_FM_BOUNDARY)

    base_fm = None
    if base_text is not None:
        base_text = normalize_input(base_text)
        base_fm_text, _, _ = split_frontmatter(base_text)
        if base_fm_text is not None:
            base_fm, _ = parse_frontmatter(base_fm_text)

    if not check_b5(head_fm, base_fm):        # b5
        return Verdict(RED, R_FM_BOUNDARY)

    # 정의역 — ADRQ 양방향 처분
    if not adrq(head_fm):
        if base_fm is not None and adrq(base_fm):
            return Verdict(RED, R_DOMAIN_ESCAPE)   # ⓐ 자격 박탈
        return Verdict(OUT, None)                  # ⓑ 정의역 밖 = 검사 없음

    # 발행일 정규화 (front-end — (iii) leg 앞)
    pubdate, pub_reason = resolve_pubdate(head_fm)
    if pub_reason is not None:
        return Verdict(RED, pub_reason)

    return admissible(head_fm, fm_text, as_of, pubdate, repo)


# --------------------------------------------------------------------------
# CLI — PR diff forward-only 정의역
# --------------------------------------------------------------------------
ADR_GLOB_PREFIX = "archive/adr/ADR-"


def _run_git(repo_root: str | None, *args: str) -> tuple[int, str, str]:
    cmd = ["git"]
    if repo_root:
        cmd += ["-C", repo_root]
    cmd += list(args)
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, proc.stdout, proc.stderr


def changed_adr_files(base_ref: str, head_ref: str, repo_root: str | None) -> list[str]:
    """정의역 = **PR diff forward-only** — 이 PR 이 추가·수정한 ``archive/adr/ADR-*.md``.

    건드리지 않은 파일은 평가하지 않는다 (코퍼스 소급 0). ``ADRQ`` 자격 판정은
    파일별 평가 안에서 이뤄진다 — 파일명 패턴은 후보 열거자일 뿐이다.
    """
    rc, out, err = _run_git(repo_root, "diff", "--name-only", "--diff-filter=AM",
                            f"{base_ref}...{head_ref}")
    if rc != 0:
        raise RuntimeError(f"git diff 실패: {err.strip()}")
    paths = []
    for line in out.split("\n"):
        line = line.strip()
        if line.startswith(ADR_GLOB_PREFIX) and line.endswith(".md"):
            paths.append(line)
    return sorted(paths)


def _show(repo_root: str | None, rev: str, path: str) -> str | None:
    rc, out, _ = _run_git(repo_root, "show", f"{rev}:{path}")
    if rc != 0:
        return None
    return out


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check-adr-admission",
        description="ADR-181 §결정 5 admission test — 신규 규범 선언의 입장료 검사",
    )
    parser.add_argument("--base-ref", default="origin/main",
                        help="merge-base 대상 ref (정의역 = PR diff forward-only)")
    parser.add_argument("--head-ref", default="HEAD", help="검사 대상 ref")
    parser.add_argument("--repo-root", default=None, help="git repo 루트 (기본 = CWD)")
    parser.add_argument("--repo-state", default=None,
                        help="사다리 3연언지의 입력원 rev (기본 = --head-ref)")
    parser.add_argument("--as-of", default=None,
                        help="실행일 pin YYYY-MM-DD (기본 = 오늘 UTC)")
    parser.add_argument("--paths", nargs="*", default=None,
                        help="정의역을 직접 지정 (diff 대신)")
    parser.add_argument("--tier", choices=("warning", "blocking"), default="warning",
                        help="warning = RED 를 보고하되 rc=0 (ADR-171 §결정 5 warning-first)")
    args = parser.parse_args(argv)

    as_of = (_dt.date.fromisoformat(args.as_of) if args.as_of
             else _dt.datetime.now(_dt.timezone.utc).date())
    repo = RepoState(args.repo_state or args.head_ref, args.repo_root)

    if args.paths is not None:
        paths = sorted(args.paths)
    else:
        try:
            paths = changed_adr_files(args.base_ref, args.head_ref, args.repo_root)
        except RuntimeError as exc:
            sys.stderr.write(f"check-adr-admission: {exc}\n")
            return 2

    rows_checked = 0
    counts = {GREEN: 0, RED: 0, OUT: 0}
    reds: list[tuple[str, str | None]] = []

    for path in paths:
        head_text = _show(args.repo_root, args.head_ref, path)
        if head_text is None:
            continue
        base_text = _show(args.repo_root, args.base_ref, path)
        verdict = evaluate(head_text, base_text, as_of, repo)
        rows_checked += 1
        counts[verdict.verdict] += 1
        marker = {GREEN: "GREEN", RED: "RED  ", OUT: "OUT  "}[verdict.verdict]
        reason = verdict.reason or "-"
        print(f"{marker} [{reason}] {path}")
        if verdict.verdict == RED:
            reds.append((path, verdict.reason))

    print(
        f"rows_checked={rows_checked} green={counts[GREEN]} "
        f"red={counts[RED]} out={counts[OUT]} as_of={as_of.isoformat()} "
        f"repo_state={repo.rev} tier={args.tier}"
    )

    if not reds:
        return 0
    print("")
    print("ADR-181 §결정 5 admission test 미충족 — 아래 선언은 ① registry entry 와")
    print("② 면제(carrier+만기) 또는 사다리((가)(나)(다)) 중 하나를 갖춰야 한다.")
    for path, reason in reds:
        print(f"  - {path}: {reason}")
    if args.tier == "warning":
        print("tier=warning — 본 게이트는 아직 차단하지 않는다 (ADR-171 §결정 5 warning-first).")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
