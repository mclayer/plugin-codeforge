#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ADR-181 §결정 5 ③-dt (iv) 결정표 — 재현기 R (수용 기준 하네스).

**정본 = ADR-181 (iv) 표 자신**이다. 본 모듈은 그 표를 두 축으로 나눠 다룬다:

* **기대값** — 표를 **파싱해서** 얻는다. 정수·판정을 소스에 pin 하지 않는다
  (ADR-181 (0-c) *"열거를 정본으로 두지 마라 — 재현 규칙 + immutable ref"*).
* **입력 바이트** — 표의 ``입력 바이트`` 열은 산문이 아니라 리터럴이지만 markdown
  셀 안이라 기계 추출이 불가하다. ⇒ 아래 ``FIXTURES`` 에 **전사(transcribe)** 한다.
  전사분과 파싱분의 **행 id 대칭차 0** 이 zero-drop 조건이며, 그 대조가 본 모듈의
  1차 검사다 (행이 표에 추가됐는데 전사가 없으면 즉시 실패한다).

pin 2종도 **표 자신에서 읽는다** — ``REPO_STATE`` ((iv-L)) · ``실행일`` ((iv-0) 상수 블록).

★ **문면에 없는 조각을 메우지 않는 것이 유일한 구성 규칙**이다 (ADR-181 재현기 R 구성 규칙).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from check_adr_admission import (  # noqa: E402
    GREEN,
    OUT,
    RED,
    RepoState,
    evaluate,
)

# --------------------------------------------------------------------------
# (iv-0) 공통 상수 — 행마다 재기술하지 않는다
# --------------------------------------------------------------------------
A = "adr_number: 999"
D = "date: 2026-08-16"
R = "[repo=mclayer/plugin-codeforge]"
OK = "carrier=#2985 expiry=2026-09-15 " + R
K = "mechanical_enforcement_actions"
TAB = "\t"
FENCE = "`" * 3

# (iv-0) 골격 — 각 행의 입력 = <FM> 자리에 그 행의 바이트를 넣은 파일 전체
#   ---
#   adr_number: 999          <- 상수 A (born-vacuous 해소, FIX Iter 9)
#   <FM>
#   ---
#   <BODY>

BODY_19 = "\n".join([
    "",
    "## 본문",
    "",
    FENCE,
    f"{K}: []  # {OK}",
    FENCE,
]) + "\n"


def build(fm_lines: list[str], *, body: str = "", prefix: str = "",
          eol: str = "\n", terminator: bool = True) -> str:
    """골격 + 위치 슬롯 4종. ``base`` 슬롯은 별도 인자로 다룬다."""
    lines = ["---", A] + fm_lines
    if terminator:
        lines.append("---")
    text = "\n".join(lines) + "\n" + body
    text = prefix + text
    if eol != "\n":
        text = text.replace("\n", eol)
    return text


def build_base(fm_lines: list[str]) -> str:
    """base 리비전 파일 — 셀이 지정한 줄이 **base FM 전체**다 (생략기호 금지)."""
    return "\n".join(["---"] + fm_lines + ["---"]) + "\n"


# --------------------------------------------------------------------------
# 입력 바이트 전사 — (iv) 표 ``입력 바이트`` 열 verbatim
# --------------------------------------------------------------------------
FIXTURES: dict[str, dict] = {
    "1":   {"fm": [D, f"{K}: []  # {OK}"]},
    "2":   {"fm": [D, f"{K}: []"]},
    "3":   {"fm": [D, f"{K}: []", f"# {OK}"]},
    "4":   {"fm": [D, f"{K}: []", "", "", "# beta2 audit #1113 (2026-05-21)"]},
    "5":   {"fm": [D, f"{K}: []  # carrier=#2985 expiry=9999-12-31 {R}"]},
    "6":   {"fm": [D, f"{K}: []  # carrier none. not #0. expiry TBD - "
                      "2099-01-01 is only an example"]},
    "7":   {"fm": [D, f"{K}: [ ]  # {OK}"]},
    "8":   {"fm": [D, f'"{K}": []  # {OK}']},
    "9":   {"fm": [D, f"{K}:", f"  []  # {OK}"]},
    "10":  {"fm": [D, "status: Accepted"]},
    "11":  {"fm": [D, f"{K}: []  # carrier=#2985 expiry=2026-09-15 {R} carrier=#1"]},
    "12":  {"fm": [D, f"{K}: []  # carrier=#2985 expiry=2026-09-15 {R} "
                      "expiry=2027-01-01"]},
    "13":  {"fm": [D, f"{K}: []  # carrier=#2985 expiry=2020-01-01 {R}"]},
    "14":  {"fm": [D, f"{K}: []  # {OK}", 'broken: "unterminated']},
    "15":  {"fm": ["date: 2026-05-13", "amendment_log:", "  - date: 2026-08-16",
                   f"{K}: []  # carrier=#2985 expiry=2026-12-01 {R}"]},
    "16":  {"fm": [D, "amendment_log:", "  - date: 2026-05-17",
                   f"{K}: []  # carrier=#2985 expiry=2027-01-01 {R}"]},
    "17":  {"fm": [D, f"{K}: []  # carrier=#2985 expiry=2026-09-15"]},
    "17b": {"fm": [D, f"{K}: []  # {OK} {R}"]},
    "18":  {"fm": [D, f"{K}: []  # this is not a carrier=#2985 "
                      f"expiry=2026-09-15 {R}"]},
    "19":  {"fm": [D, f"{K}: []  # {OK}"], "body": BODY_19},
    "20":  {"fm": [D, f"{K}: []{TAB}# {OK}"]},
    "21":  {"fm": [D, f"{K}: []  # carrier=#2985{TAB}expiry=2026-09-15 {R}"]},
    "22":  {"fm": [D, f"{K}: []  # {OK}",
                   f"{K}: []  # carrier=#2985 expiry=2099-01-01 {R}"]},
    "23":  {"fm": [D, f"{K}: []  # carrier=#2985 carrier=#1 "
                      f"expiry=2026-09-15 {R}"]},
    "24":  {"fm": [D, f"{K}: []  # carrier=#12345678 expiry=2026-09-15 {R}"]},
    # 아랍-인도 숫자 U+0661 U+0662 U+0663 — `\d` 오전사 판별
    "25":  {"fm": [D, f"{K}: []  # carrier=#1١٢٣ "
                      f"expiry=2026-09-15 {R}"]},
    "26":  {"fm": [D, f"{K}: []  # carrier=#0985 expiry=2026-09-15 {R}"]},
    "27":  {"fm": [D, 'title: "long title text', f'{K}: []  # {OK}"']},
    "28":  {"fm": [D, f"{K}: []  # {OK} non-carrier=#3"]},
    "29":  {"fm": [D, f"{K}: []  # carrier=#2985 expiry=2026-09-31 {R}"]},
    "30":  {"fm": [D, f"{K}: []  # carrier=#2985 expiry=2026-09-15 "
                      "[repo=mclayer/plugin codeforge]"]},
    "31":  {"fm": [f"{K}: []  # carrier=#2985 expiry=9999-12-31 {R}"]},
    "32":  {"fm": ["date: TBD",
                   f"{K}: []  # carrier=#2985 expiry=9999-12-31 {R}"]},
    "33":  {"fm": [D, f"{K}: []  # {OK}", "---", "other: x"]},
    "33b": {"fm": [D, f"{K}: []  # {OK}", "---", "This line is prose.",
                   "Other-Key: x"]},
    # 위치 슬롯 `prefix` — U+FEFF 1문자, **파일 선두**(<FM> 슬롯 안이 아니다)
    "34":  {"fm": [D, f"{K}: []  # {OK}"], "prefix": "﻿"},
    # 위치 슬롯 `eol` — CRLF, 파일 전체
    "35":  {"fm": [D, f"{K}: []  # {OK}"], "eol": "\r\n"},
    "36":  {"fm": ["adr_number: null", D, "status: Active"]},
    "37":  {"fm": ["adr_number: null", D, f"{K}: []  # {OK}"],
            "base": ["adr_number: 67"]},
    "38":  {"fm": [D, f"{K}: []  # carrier=#2985 expiry=2026-08-17 {R}"]},
    "39":  {"fm": [D, f"{K}: []  # carrier=#2985 expiry=2027-02-12 {R}"]},
    "40":  {"fm": [D, f"{K}: []  # carrier=#2985 expiry=2027-05-01 {R}"]},
    # 위치 슬롯 `terminator` — FM 종단 `---` 제거
    "41":  {"fm": [A, D, f"{K}: []  # {OK}"], "terminator": False},
    # 위치 슬롯 `base` — 그 2줄이 base FM 전체 (`status` 키 소실)
    "42":  {"fm": [A, D, f"{K}: []  # {OK}"],
            "base": ["adr_number: 67", "status: Accepted"]},
    "43":  {"fm": [D, f"{K}:", "  - scripts/check-adr-amendment-parity.sh"]},
    "44":  {"fm": [D, f"{K}:", "  - script_path: scripts/check-no-atlassian.sh"]},
    "45":  {"fm": [D, f"{K}:",
                   "  - script_path: scripts/check-adr-amendment-parity.sh"]},
    "45b": {"fm": [D, f"{K}:",
                   "  - script_path: docs/evidence-checks-registry.yaml"]},
    "46":  {"fm": [D, f"{K}:", "  - script_path: scripts/check-adr-admission.sh"]},
    "46b": {"fm": [D, f"{K}:", "  - script_path: .codeforge/project.yaml"]},
    "47":  {"fm": [D, f"{K}: []  # {OK}", "---", "Other-Key: x"]},
    # `K` = U+212A KELVIN SIGN (NFC 정준 싱글턴 -> ASCII `K`)
    "47K": {"fm": [D, f"{K}: []  # {OK}", "---", "Other-Key: x"]},
    "48":  {"fm": [D, f"{K}:", "  - script_path: scripts/lib"]},
    "49":  {"fm": [D, f"{K}:", "  - script_path: "
                   "archive/adr/ADR-027-consumer-adoption-protocol.md"]},
    "50":  {"fm": [D, f"{K}:", "  - workflow: "
                   "templates/github-workflows/retro-alert-pickup-kpi.yml"]},
    "50b": {"fm": [D, f"{K}:", "  - workflow: "
                   "templates/github-workflows/claude-md-line-cap.yml"]},
    "50c": {"fm": [D, f"{K}:", "  - workflow: templates/github-workflows/test.yml"]},
    "50d": {"fm": [D, f"{K}:", "  - workflow: "
                   ".github/workflows/invariant-check.yml"]},
    "51":  {"fm": [D, f"{K}:", "  - workflow_path: "
                   "templates/github-workflows/version-3way-atomic.yml"]},
    "52":  {"fm": [D, f"{K}:", "  - action: bootstrap-labels"]},
    "53":  {"fm": [D, f"{K}:",
                   "  - detect_command: bash scripts/check-claude-md-line-cap.sh"]},
    "54":  {"fm": [D, f"{K}:", "  - script_path: scripts/next-phase.sh"]},
    "55":  {"fm": [D, f"{K}:", "  - script_path: scripts/retro-retry-helper.sh"]},
    "56":  {"fm": [D, f"{K}:", "  - script_path: scripts/extract-security-ai.sh"]},
    "57":  {"fm": [D, f"{K}:", "  - script_path: scripts/bootstrap-labels.sh"]},
    "58":  {"fm": [D, f'"{K}":',
                   "  - script_path: scripts/check-adr-amendment-parity.sh"]},
    # 한 항목이 경로 키 2개 보유 — ALL(규정) -> RED / ANY -> GREEN
    "58b": {"fm": [D, f"{K}:",
                   "  - script_path: scripts/check-adr-amendment-parity.sh",
                   "    workflow: templates/github-workflows/test.yml"]},
}


# --------------------------------------------------------------------------
# (iv) 표 파싱 — 기대값·pin 은 표에서 읽는다
# --------------------------------------------------------------------------
VERDICT_TOKENS = {GREEN, RED, OUT}
RE_ROW_ID = re.compile(r"^\**\s*([0-9]+[a-zA-Z]?)\s*\**$")
RE_REPO_STATE = re.compile(
    r"REPO_STATE\s*:=\s*\S+\s+commit\s+([0-9a-f]{7,40})"
)
RE_AS_OF = re.compile(r"실행일\s*:=\s*([0-9]{4}-[0-9]{2}-[0-9]{2})")


def _clean(cell: str) -> str:
    return cell.replace("**", "").replace("★", "").replace("`", "").strip()


def parse_table(adr_text: str) -> dict[str, tuple[str, str | None]]:
    """(iv) 표 본문 행 -> ``{행 id: (verdict, exit 사유)}``.

    행 선택 술어 = **기대 열(3번째 칸)이 GREEN/RED/OUT 인 행** (ADR-181 산출 명령).
    행 id 만으로 세면 다른 표까지 잡힌다 — 그 함정을 여기서 피한다.
    """
    expected: dict[str, tuple[str, str | None]] = {}
    for line in adr_text.split("\n"):
        if not line.startswith("|"):
            continue
        cells = line.split("|")
        if len(cells) < 5:
            continue
        m = RE_ROW_ID.match(cells[1].strip())
        if not m:
            continue
        verdict = _clean(cells[3])
        if verdict not in VERDICT_TOKENS:
            continue
        reason_cell = _clean(cells[4])
        # `—` (em-dash) = exit 사유 없음
        reason = None if reason_cell in ("", "—", "-", "— (검사 없음)") else reason_cell
        if reason is not None and reason.startswith("— "):
            reason = None
        expected[m.group(1)] = (verdict, reason)
    return expected


def parse_pins(adr_text: str) -> tuple[str, _dt.date]:
    m_repo = RE_REPO_STATE.search(adr_text)
    m_asof = RE_AS_OF.search(adr_text)
    if not m_repo:
        raise SystemExit("ADR-181 에서 REPO_STATE pin 을 찾지 못했다 — 재현 조건 부재")
    if not m_asof:
        raise SystemExit("ADR-181 에서 실행일 pin 을 찾지 못했다 — 재현 조건 부재")
    return m_repo.group(1), _dt.date.fromisoformat(m_asof.group(1))


def instantiate(spec: dict) -> tuple[str, str | None]:
    head = build(
        spec["fm"],
        body=spec.get("body", ""),
        prefix=spec.get("prefix", ""),
        eol=spec.get("eol", "\n"),
        terminator=spec.get("terminator", True),
    )
    base = build_base(spec["base"]) if "base" in spec else None
    return head, base


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="adr181-table-reproducer",
        description="ADR-181 (iv) 결정표 전 행 (verdict, exit 사유) 전건 재현",
    )
    parser.add_argument(
        "--adr",
        default="archive/adr/ADR-181-verification-domain-deficit-normative.md",
        help="(iv) 표 SSOT 경로",
    )
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--repo-state", default=None,
                        help="사다리 입력원 rev override (기본 = ADR 의 REPO_STATE pin)")
    parser.add_argument("--as-of", default=None,
                        help="실행일 override (기본 = ADR 의 실행일 pin)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    adr_path = args.adr
    if args.repo_root:
        adr_path = os.path.join(args.repo_root, args.adr)
    with open(adr_path, encoding="utf-8") as fh:
        adr_text = fh.read()

    expected = parse_table(adr_text)
    pin_rev, pin_as_of = parse_pins(adr_text)
    rev = args.repo_state or pin_rev
    as_of = _dt.date.fromisoformat(args.as_of) if args.as_of else pin_as_of

    # -- zero-drop: 파싱분 <-> 전사분 행 id 대칭차 0 ----------------------
    only_table = sorted(set(expected) - set(FIXTURES))
    only_fixture = sorted(set(FIXTURES) - set(expected))
    print(f"table_rows={len(expected)} fixture_rows={len(FIXTURES)} "
          f"repo_state={rev} as_of={as_of.isoformat()}")
    if only_table or only_fixture:
        print("ROW-SET MISMATCH — 수용 기준과 전사분이 갈렸다 (zero-drop 위반)")
        if only_table:
            print(f"  표에만 있는 행 (전사 누락): {only_table}")
        if only_fixture:
            print(f"  전사에만 있는 행 (표에서 제거됨): {only_fixture}")
        return 1

    repo = RepoState(rev, args.repo_root)

    match = 0
    mismatches: list[str] = []
    for row_id in sorted(expected, key=lambda s: (int(re.match(r"\d+", s).group()), s)):
        head, base = instantiate(FIXTURES[row_id])
        try:
            got = evaluate(head, base, as_of, repo)
        except Exception as exc:  # 예외는 skip 이 아니라 불일치다
            mismatches.append(f"  행 {row_id}: 예외 {type(exc).__name__}: {exc}")
            continue
        want = expected[row_id]
        if got.as_pair() == want:
            match += 1
            if args.verbose:
                print(f"  ok   행 {row_id}: {got.verdict}/{got.reason}")
        else:
            mismatches.append(
                f"  행 {row_id}: 기대 {want[0]}/{want[1]} != 산출 "
                f"{got.verdict}/{got.reason}"
            )

    total = len(expected)
    print(f"rows_checked={total} match={match} mismatch={len(mismatches)}")
    if mismatches:
        print("MISMATCH — (iv) 표와 어긋나면 어긋난 쪽은 구현이다:")
        for line in mismatches:
            print(line)
        return 1
    print("PASS — (iv) 결정표 전 행 (verdict, exit 사유) 전건 재현")
    return 0


if __name__ == "__main__":
    sys.exit(main())
