#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ADR-181 §결정 5 (0-c) leg ablation 재실행 — **판별력 실증** (`D-LEG` L2/L3-ⓒ).

*"구현하지 않아도 표 전건 재현이 성립하는 leg 은 재현해야 할 것의 집합에 없다."*
(ADR-181 `D-LEG`). 67/67 재현 자체는 **하네스가 항진일 때도 성립**하므로, 본 모듈이
leg 을 하나씩 끄고 (iv) 표 전 행을 재실행해 **뒤집히는 행 집합**을 낸다.

두 종류의 기대를 함께 둔다 (양성 ∧ 음성 대조군):

* **양성** — ADR-181 (0-c) / (iv-L) 이 **행 id 로 declare 한 뒤집힘 집합**과 정확히 일치해야 한다.
* **음성** — 같은 문서가 **판별 0 이라고 declare 한 leg** 은 한 행도 뒤집으면 안 된다.
  (뒤집으면 문서 쪽이 틀렸거나 구현이 규정보다 넓다 — 어느 쪽이든 보고 대상이다.)

``report_only`` = ADR 이 행 집합을 명시하지 않은 leg. **기대를 지어내지 않고** 관측만 낸다.

leg-off 는 **연산**이지 이름이 아니다 (ADR-181 FIX Iter 11 규율) — 각 항목의
``op`` 주석이 그 연산이다.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check_adr_admission as C  # noqa: E402
import adr181_table_reproducer as T  # noqa: E402

# 패치 대상 — ablation 마다 스냅샷 후 복원한다
_PATCHABLE = (
    "split_frontmatter", "parse_frontmatter", "check_b4", "check_b5", "adrq",
    "domain_verdict", "resolve_pubdate", "normalize_input", "normalize_paths",
    "strip_comment_lines", "ladder", "exempt", "SCOPE_OF", "PARSE_EXPIRY",
    "LOWER_BOUND_OK", "UPPER_BOUND_OK", "EXEMPT_LEGS", "PATH_KEYS",
    "EXPIRY_CAP_DAYS", "RE_FMLINE", "RE_CAR", "RE_PFX", "RE_LINE",
)
_REPO_METHODS = ("exists", "wired_script", "wired_workflow", "wired")


def _snapshot() -> tuple[dict, dict]:
    mod = {k: getattr(C, k) for k in _PATCHABLE}
    repo = {k: getattr(C.RepoState, k) for k in _REPO_METHODS}
    return mod, repo


def _restore(state: tuple[dict, dict]) -> None:
    mod, repo = state
    for k, v in mod.items():
        setattr(C, k, v)
    for k, v in repo.items():
        setattr(C.RepoState, k, v)


def _drop_leg(name: str) -> None:
    C.EXEMPT_LEGS = [t for t in C.EXEMPT_LEGS if t[0] != name]


# --------------------------------------------------------------------------
# leg-off 연산 정의
# --------------------------------------------------------------------------
def off_b1() -> None:
    """op: `b1`(선두 `---`+LF) 을 위치 탐색 전제에서 제거 — BOM·CRLF 를 걷어내고 탐색."""
    def patched(text):
        t = text.lstrip("﻿").replace("\r\n", "\n")
        lines = t.split("\n")
        for idx in range(1, len(lines)):
            if lines[idx] == "---":
                return "\n".join(lines[1:idx]), lines, idx
        return None, lines, -1
    C.split_frontmatter = patched


def off_b2() -> None:
    """op: FM 종단 부재를 위반으로 보지 않고 나머지 전체를 FM 으로 읽는다."""
    def patched(text):
        lines = text.split("\n")
        if not text.startswith("---\n"):
            return None, lines, -1
        for idx in range(1, len(lines)):
            if lines[idx] == "---":
                return "\n".join(lines[1:idx]), lines, idx
        return "\n".join(lines[1:]), lines, len(lines) - 1
    C.split_frontmatter = patched


def off_b3() -> None:
    """op: 파싱 예외를 named RED 가 아니라 **skip** 으로 (빈 mapping 으로 계속)."""
    def patched(fm_text):
        try:
            data = C.yaml.safe_load(fm_text)
        except Exception:
            return {}, None
        if not isinstance(data, dict):
            return {}, None
        return data, None
    C.parse_frontmatter = patched


def off_b4() -> None:
    """op: FM 종단 이후 FM-형 줄 검사 제거."""
    C.check_b4 = lambda lines, term: True


def off_b5() -> None:
    """op: base top-level 키 보존 검사 제거."""
    C.check_b5 = lambda head_fm, base_fm: True


def off_domain() -> None:
    """op: ADR 자격 술어 제거 — 파일명 glob 만으로 정의역 인정."""
    C.adrq = lambda fm: True


def off_d_escape() -> None:
    """op: 자격 박탈 가지(ⓐ) 제거 — ¬ADRQ 는 전부 ⓑ(OUT)."""
    def patched(head_fm, base_fm):
        if C.adrq(head_fm):
            return None
        return C.Verdict(C.OUT, None)
    C.domain_verdict = patched


def off_nfc() -> None:
    """op: 입력 유니코드 정규화 제거."""
    C.normalize_input = lambda text: text


def off_fmline() -> None:
    """op: `FM-형 줄` 을 `^[a-z_]+:` 로 좁힘 (독법 B — 대문자·하이픈 키가 샌다)."""
    C.RE_FMLINE = re.compile(r"^[a-z_]+:")


def off_mea() -> None:
    """op: `mea-missing` leg 제거 (YAML 키 멤버십 검사)."""
    _drop_leg(C.R_MEA_MISSING)


def off_scope() -> None:
    """op: `SCOPE` 를 frontmatter 에서 **파일 전체**로 되돌림."""
    C.SCOPE_OF = lambda fm_text, full_text: full_text


def off_repo() -> None:
    """op: `repo-token` leg 제거."""
    _drop_leg(C.R_REPO_TOKEN)


def off_pfx() -> None:
    """op: `token-order`(PFX 선두 앵커) leg 제거."""
    _drop_leg(C.R_TOKEN_ORDER)


def off_order() -> None:
    """op: 평가 순서 `REPO` <-> `PFX` 교환 (leg 제거가 아니라 순서 교환)."""
    legs = list(C.EXEMPT_LEGS)
    i = [n for n, _ in legs].index(C.R_REPO_TOKEN)
    j = [n for n, _ in legs].index(C.R_TOKEN_ORDER)
    legs[i], legs[j] = legs[j], legs[i]
    C.EXEMPT_LEGS = legs


def off_expvalue() -> None:
    """op: 만기 값 파싱 예외를 named RED 가 아니라 **skip** 으로."""
    def patched(raw):
        try:
            return _dt.date.fromisoformat(raw), None
        except ValueError:
            return None, None
    C.PARSE_EXPIRY = patched


def off_pubdate() -> None:
    """op: 발행일 부재·오값을 named RED 가 아니라 skip 으로 (상한 leg 이 증발)."""
    orig = C.resolve_pubdate

    def patched(fm):
        value, reason = orig(fm)
        return (value, None) if reason else (value, None)
    C.resolve_pubdate = patched

    def guarded_over_cap(ctx):
        if ctx.pubdate is None:
            return None
        return C._leg_over_cap(ctx)
    C.EXEMPT_LEGS = [
        (n, guarded_over_cap if n == C.R_OVER_CAP else f) for n, f in C.EXEMPT_LEGS
    ]


def off_cap180() -> None:
    """op: 상한 상수 180 -> 365 (검토 주기 미만 성질 상실)."""
    C.EXPIRY_CAP_DAYS = 365


def off_lower_eq() -> None:
    """op: 하한 `>=` -> `>` (당일 만기 탈락)."""
    C.LOWER_BOUND_OK = lambda expiry, as_of: expiry > as_of


def off_upper_eq() -> None:
    """op: 상한 `<=` -> `<` (정확히 상한인 날짜 탈락)."""
    C.UPPER_BOUND_OK = lambda expiry, cap: expiry < cap


def off_car_leading() -> None:
    """op: carrier 선두 숫자군 `[1-9]` -> `[0-9]` (CAR·PFX 동시 — 선행 0 통과)."""
    C.RE_CAR = re.compile(r"(?<![0-9A-Za-z_-])carrier=#(?P<n>[0-9][0-9]{0,6})(?![0-9])")
    C.RE_PFX = re.compile(
        r"^[ \t]*carrier=#[0-9][0-9]{0,6}[ \t]+expiry=[0-9]{4}-[0-9]{2}-[0-9]{2}"
        r"[ \t]+\[repo=[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\]"
    )


def off_car_unicode() -> None:
    """op: 숫자군 `[0-9]` -> `\\d` 오전사 (Python 에서 유니코드 숫자를 먹는다)."""
    C.RE_CAR = re.compile(r"(?<![0-9A-Za-z_-])carrier=#(?P<n>[1-9]\d{0,6})(?!\d)")
    C.RE_PFX = re.compile(
        r"^[ \t]*carrier=#[1-9]\d{0,6}[ \t]+expiry=\d{4}-\d{2}-\d{2}"
        r"[ \t]+\[repo=[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\]"
    )


def off_car_boundary() -> None:
    """op: carrier 토큰 경계군 제거 (접미 산문의 `non-carrier=#3` 이 2회째로 셈된다)."""
    C.RE_CAR = re.compile(r"carrier=#(?P<n>[1-9][0-9]{0,6})(?![0-9])")


def off_exist_pathspec() -> None:
    """op: `실재` 를 `ls-tree` 완전일치 -> pathspec(디렉터리 비공백) 으로 되돌림."""
    def patched(self, path):
        if path in self.tree:
            return True
        return any(t.startswith(path + "/") for t in self.tree)
    C.RepoState.exists = patched


def off_wire_boundary() -> None:
    """op: `배선` 경계 매치 -> 부분문자열 포함 (URL 조각 안 경로가 샌다)."""
    C.RepoState.wired_script = lambda self, path: path in self.wire_text


def off_wire_trailing_slash() -> None:
    """op: 뒤 경계 문자군에 `/` 추가 — ADR 이 **판별 0** 이라 declare 한 변형."""
    def patched(self, path):
        pattern = r"(?<![A-Za-z0-9_./-])" + re.escape(path) + r"(?![A-Za-z0-9_./-])"
        return re.search(pattern, self.wire_text) is not None
    C.RepoState.wired_script = patched


def _norm_without(skip: str):
    def patched(text):
        if skip != "P-4":
            text = C.RE_P4.sub("", text)
        if skip != "P-3":
            text = C.RE_P3.sub("", text)
        if skip != "P-2":
            text = C.RE_P2.sub("", text)
        if skip != "P-1":
            text = C.RE_P1.sub("", text)
        return text
    return patched


def off_p1() -> None:
    """op: 접두 리터럴 (P-1) `./` 제거를 끔."""
    C.normalize_paths = _norm_without("P-1")


def off_p2() -> None:
    """op: 접두 리터럴 (P-2) `$GITHUB_WORKSPACE/` 제거를 끔."""
    C.normalize_paths = _norm_without("P-2")


def off_p3() -> None:
    """op: 접두 리터럴 (P-3) `${GITHUB_WORKSPACE}/` 제거를 끔."""
    C.normalize_paths = _norm_without("P-3")


def off_p4() -> None:
    """op: 접두 리터럴 (P-4) `${{ github.workspace }}/` 제거를 끔."""
    C.normalize_paths = _norm_without("P-4")


def off_prefix_order() -> None:
    """op: 접두 제거 순서를 P-1 -> P-4 로 역전 — ADR 이 **판별 0** 이라 declare 한 변형."""
    def patched(text):
        text = C.RE_P1.sub("", text)
        text = C.RE_P2.sub("", text)
        text = C.RE_P3.sub("", text)
        text = C.RE_P4.sub("", text)
        return text
    C.normalize_paths = patched


def off_comment_strip() -> None:
    """op: 선두 주석줄 제거를 끔 — ADR 이 **표 내 판별 0** 이라 declare 한 leg."""
    C.strip_comment_lines = lambda text: text


def off_wf_branch() -> None:
    """op: (iv-L3) workflow 축 분기 제거 — workflow 도 `run:` 블롭 축으로 판정."""
    C.RepoState.wired = lambda self, key, path: self.wired_script(path)


def _drop_path_key(key: str):
    def op() -> None:
        C.PATH_KEYS = tuple(k for k in C.PATH_KEYS if k != key)
    return op


def _add_path_key(key: str):
    def op() -> None:
        C.PATH_KEYS = C.PATH_KEYS + (key,)
    return op


def off_ladder_stub() -> None:
    """op: 사다리를 `len(mea) >= 1` 로만 구현 (3연언지 전부 삭제) — stub checker."""
    def patched(fm, repo):
        items = fm.get(C.MEA_KEY)
        if not isinstance(items, list) or len(items) < 1:
            return False, None
        return True, None
    C.ladder = patched


def off_key_any() -> None:
    """op: 한 항목의 다중 경로 키를 ALL 이 아니라 **ANY**(pick-first `break`) 로."""
    def patched(fm, repo):
        items = fm.get(C.MEA_KEY)
        if not isinstance(items, list) or len(items) < 1:
            return False, None
        for item in items:
            if not isinstance(item, dict):
                return False, C.R_LADDER_PATH_KEY
            present = [k for k in C.PATH_KEYS if k in item]
            if not present:
                return False, C.R_LADDER_PATH_KEY
            key = present[0]          # pick-first = ANY
            value = item[key]
            if not isinstance(value, str) or not value:
                return False, C.R_LADDER_PATH_KEY
            if not repo.exists(value):
                return False, C.R_LADDER_PATH_MISSING
            if not repo.wired(key, value):
                return False, C.R_LADDER_UNWIRED
        return True, None
    C.ladder = patched


# --------------------------------------------------------------------------
# ablation 등록 — 기대는 ADR 문면에서만 온다 (지어내지 않는다)
# --------------------------------------------------------------------------
class Ablation:
    def __init__(self, name, op, *, verdict=None, reason_only=None,
                 declared_zero=False, report_only=False, source=""):
        self.name = name
        self.op = op
        self.verdict = set(verdict or [])
        self.reason_only = set(reason_only or [])
        self.declared_zero = declared_zero
        self.report_only = report_only
        self.source = source


ABLATIONS: list[Ablation] = [
    # ---- 경계 축 — (0-c) 표가 행 id 로 declare ---------------------------
    Ablation("b1", off_b1, verdict=["34", "35"], source="(0-c) `b1`(β 독법) 2"),
    Ablation("b2", off_b2, verdict=["41"], source="(0-c) `b2` 1"),
    Ablation("b3/FMPARSE", off_b3, verdict=["14", "20"],
             source="(0-c) `FMPARSE`(=`b3`) 2 — RED -> OUT"),
    Ablation("b4", off_b4, verdict=["33", "47", "47K"], source="(0-c) `b4` 3"),
    Ablation("b5", off_b5, verdict=["42"], source="(0-c) `b5` 1"),
    Ablation("FMLINE 좁힘", off_fmline, verdict=["47", "47K"],
             source="(0-c) `FMLINE` 좁힘 (`^[a-z_]+:`) 2"),
    # ---- 정의역 축 -------------------------------------------------------
    Ablation("DOMAIN", off_domain, verdict=["36", "37"],
             source="(0-c) `DOMAIN` off — 36 OUT->RED/mea-missing · 37 RED->GREEN"),
    Ablation("D-ESCAPE", off_d_escape, verdict=["37"],
             source="(0-c) `D-ESCAPE` 1 — RED/domain-escape -> OUT"),
    Ablation("NFC", off_nfc, verdict=["47K"], source="(iv) 행 47K — NFC off -> GREEN"),
    # ---- 사다리 축 -------------------------------------------------------
    Ablation("PATH_KEYS drop script_path", _drop_path_key("script_path"),
             verdict=["45", "45b", "54", "55", "56", "57", "58"],
             reason_only=["44", "46", "46b", "48", "49"],
             source="(0-c) `LADDER_KEY` 12"),
    Ablation("PATH_KEYS drop workflow", _drop_path_key("workflow"),
             verdict=["50", "50b", "50d", "58b"], reason_only=["50c"],
             source="(0-c) `PATH_KEYS` drop `workflow` 5"),
    Ablation("PATH_KEYS drop workflow_path", _drop_path_key("workflow_path"),
             verdict=["51"], source="(0-c) `PATH_KEYS` drop `workflow_path` 1"),
    Ablation("PATH_KEYS add action", _add_path_key("action"),
             reason_only=["52"], source="(0-c) `PATH_KEYS` add `action` 1 — 사유만"),
    Ablation("PATH_KEYS add detect_command", _add_path_key("detect_command"),
             reason_only=["53"],
             source="(0-c) `PATH_KEYS` add `detect_command` 1 — 사유만"),
    Ablation("WF_BRANCH", off_wf_branch, verdict=["50b", "50d"],
             source="(0-c) `WF_BRANCH` 2"),
    Ablation("WIRE 접두 (P-3)", off_p3, verdict=["56"],
             source="(0-c) `WIRE` 접두 (P-3) 1 (주석제거 on 일 때만)"),
    Ablation("ladder stub", off_ladder_stub,
             verdict=["45", "45b", "50", "50b", "50d", "51", "54", "55", "56",
                      "57", "58"],
             reason_only=[],
             report_only=True,
             source="(iv) stub checker — 최종 67행 mismatch 10 "
                    "(43·44·46·46b·48·49·50c·52·53·58b)"),
    Ablation("key ANY (pick-first)", off_key_any, verdict=["58b"],
             source="(vii) FIX Iter 13 — 58b 가 이 축의 유일 판별자"),
    # ---- 음성 대조군 — ADR 이 판별 0 이라 declare --------------------------
    Ablation("WIRE 선두 주석줄 제거", off_comment_strip, declared_zero=True,
             source="(0-c) `WIRE` 선두 주석줄 제거 — 표 내 판별 0"),
    Ablation("WIRE 뒤 경계 `/` 추가", off_wire_trailing_slash, declared_zero=True,
             source="(iv-L) 뒤 경계에 `/` 추가 — 최종 67행 뒤집힘 0"),
    Ablation("접두 제거 순서 역전", off_prefix_order, declared_zero=True,
             source="(iv-L) 접두 제거 순서 — 현 67행 판별 0"),
    Ablation("ORDER (REPO<->PFX)", off_order, reason_only=["17", "30"],
             source="(0-c) `ORDER` 2 — verdict 축 0, 사유만 17 · 30"),
    # ---- 면제 leg 축 — ADR 이 집합을 명시하지 않은 것은 report_only ---------
    Ablation("MEA", off_mea, report_only=True, source="(iv) 행 27 — MEA 제거 시 GREEN"),
    Ablation("SCOPE", off_scope, report_only=True, source="(iv) 행 19 — 파일 전체 정의역"),
    Ablation("REPO", off_repo, report_only=True, source="(iv) 행 17b — REPO 제거 시 GREEN"),
    Ablation("PFX", off_pfx, report_only=True, source="(iv) 행 18 — PFX 없으면 GREEN"),
    Ablation("EXPVALUE", off_expvalue, report_only=True,
             source="(iv) 행 29 — 예외 skip 시 GREEN"),
    Ablation("PUBDATE", off_pubdate, report_only=True,
             source="(iv) 행 31·32 — PUBDATE off 시 GREEN"),
    Ablation("상수 180 -> 365", off_cap180, report_only=True,
             source="(iv) 행 40 — 365 로 넓히면 GREEN"),
    Ablation("하한 `>=` -> `>`", off_lower_eq, report_only=True, source="(iv) 행 38"),
    Ablation("상한 `<=` -> `<`", off_upper_eq, report_only=True, source="(iv) 행 39"),
    Ablation("CAR 선두 `[1-9]`->`[0-9]`", off_car_leading, report_only=True,
             source="(iv) 행 26"),
    Ablation("CAR `[0-9]`->`\\d`", off_car_unicode, report_only=True, source="(iv) 행 25"),
    Ablation("CAR 토큰 경계군 제거", off_car_boundary, report_only=True,
             source="(iv) 행 28"),
    Ablation("실재 -> pathspec", off_exist_pathspec, report_only=True,
             source="(iv) 행 48"),
    Ablation("배선 경계 -> 부분문자열", off_wire_boundary, report_only=True,
             source="(iv) 행 49"),
    Ablation("P-1 `./`", off_p1, report_only=True, source="(iv) 행 54"),
    Ablation("P-2 `$GITHUB_WORKSPACE/`", off_p2, report_only=True, source="(iv) 행 55"),
    Ablation("P-4 `${{ github.workspace }}/`", off_p4, report_only=True,
             source="(iv) 행 57"),
]


def _run_all(expected, as_of, rev, repo_root):
    repo = C.RepoState(rev, repo_root)
    out = {}
    for row_id in expected:
        head, base = T.instantiate(T.FIXTURES[row_id])
        try:
            v = C.evaluate(head, base, as_of, repo)
            out[row_id] = v.as_pair()
        except Exception as exc:
            out[row_id] = ("EXC", f"{type(exc).__name__}")
    return out


def _sort_rows(rows):
    return sorted(rows, key=lambda s: (int(re.match(r"\d+", s).group()), s))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="adr181-leg-ablation",
        description="(0-c) leg ablation 재실행 — 판별력 실증 (양성 ∧ 음성 대조군)",
    )
    parser.add_argument(
        "--adr",
        default="archive/adr/ADR-181-verification-domain-deficit-normative.md")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    adr_path = os.path.join(args.repo_root, args.adr) if args.repo_root else args.adr
    with open(adr_path, encoding="utf-8") as fh:
        adr_text = fh.read()
    expected = T.parse_table(adr_text)
    rev, as_of = T.parse_pins(adr_text)

    baseline = _run_all(expected, as_of, rev, args.repo_root)
    base_mismatch = [r for r in expected if baseline[r] != expected[r]]
    print(f"baseline rows={len(expected)} mismatch={len(base_mismatch)} "
          f"repo_state={rev} as_of={as_of.isoformat()}")
    if base_mismatch:
        print("BASELINE MISMATCH — ablation 해석 전에 규정판이 먼저 일치해야 한다")
        for r in _sort_rows(base_mismatch):
            print(f"  행 {r}: 기대 {expected[r]} != 산출 {baseline[r]}")
        return 1

    failures: list[str] = []
    print("")
    print(f"{'leg-off 연산':<34} {'verdict':<28} {'사유만':<20} 판정")
    print("-" * 104)

    for ab in ABLATIONS:
        state = _snapshot()
        try:
            ab.op()
            got = _run_all(expected, as_of, rev, args.repo_root)
        finally:
            _restore(state)

        v_flips = {r for r in expected if got[r][0] != baseline[r][0]}
        r_flips = {r for r in expected
                   if got[r][0] == baseline[r][0] and got[r][1] != baseline[r][1]}

        if ab.declared_zero:
            ok = not v_flips and not r_flips
            tag = "OK (음성 대조군)" if ok else "FAIL — 판별 0 선언과 불일치"
        elif ab.report_only:
            ok = True
            tag = "report-only"
        else:
            ok = (v_flips == ab.verdict and r_flips == ab.reason_only)
            tag = "OK" if ok else "FAIL — ADR 선언 집합과 불일치"

        if not ok:
            failures.append(
                f"  {ab.name}: 선언 verdict={_sort_rows(ab.verdict)} "
                f"사유만={_sort_rows(ab.reason_only)} / 관측 "
                f"verdict={_sort_rows(v_flips)} 사유만={_sort_rows(r_flips)} "
                f"[{ab.source}]"
            )
        print(f"{ab.name:<34} {str(_sort_rows(v_flips)):<28} "
              f"{str(_sort_rows(r_flips)):<20} {tag}")
        if args.verbose:
            print(f"{'':<34} source: {ab.source}")

    print("")
    total = len(ABLATIONS)
    asserted = sum(1 for a in ABLATIONS if not a.report_only)
    print(f"ablations={total} asserted={asserted} "
          f"report_only={total - asserted} failures={len(failures)}")
    if failures:
        print("FAIL:")
        for line in failures:
            print(line)
        return 1
    print("PASS — 선언 집합 일치 ∧ 판별 0 선언 leg 은 한 행도 뒤집지 않음")
    return 0


if __name__ == "__main__":
    sys.exit(main())
