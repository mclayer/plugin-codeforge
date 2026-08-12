#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""check_slot_budget_table.py — CFP-2926 NG-21 / AC-12 슬롯 예산 표 합 검사.

Story §7.7.4 "슬롯 — static budget (런타임 카운터 원리적 불가)" 의 예산 표가
**대상 문서에 실재**하고 그 합이 **세션 슬롯 상한 20** 과 일치함을 판정한다.

    | 몫                        | 슬롯 |
    | Reserved (lead 전용)      |  4   |
    | lane PL pool              | 14   |
    | Headroom (미할당 고정)    |  2   |
                          합계 = 20

3-state verdict = `gate_verdict` 재사용 (신규 verdict 체계 발명 0).

── ★핵심 요구 — "우연히 RED" 금지★ ────────────────────────────────────────
Story §8.0.8 (1) NG-21 행:
  "★표 미발견 ∨ 파싱 행 **0** → RED★ — ★'합 0 ≠ 20 이라 **우연히** RED' 에 의존
   금지, **명시 분기** 로 분리★"

⇒ 아래 4 경로는 각각 **고유 reason 문자열**을 갖는 별개 분기다. 합계 비교(sum
   != 20)에 **도달하기 전에** 끊는다. 합계 산술의 부수효과로 RED 가 나오는 경로는
   존재하지 않는다:

  | reason                    | 언제 | verdict |
  |---|---|---|
  | `target_doc_not_found`    | 대상 문서 자체 부재 | RED |
  | `table_heading_not_found` | ★heading rename★ — 표 anchor 소멸 | RED |
  | `table_not_found`         | heading 은 있으나 그 아래 표 블록 부재 | RED |
  | `table_rows_zero`         | 표는 있으나 **데이터 행 0** (vacuous) | RED |
  | `budget_column_not_found` | 슬롯 열 header 미식별 | RED (unknown-input) |
  | `non_numeric_cell`        | 표 셀 비수치 | RED (unknown-input, exit 1) |
  | `slot_budget_sum_mismatch`| 위 전건 통과 ∧ 합 ≠ 20 | RED |
  | `slot_budget_sum_ok`      | 합 == 20 | PASS |

★heading rename → 0행 vacuous★ 은 NG-8 과 **동형 추출 축**이다 — 추출기가 anchor
를 잃으면 "위반 0" 이 아니라 "관측 0" 인데, 이를 GREEN 으로 흡수하면 게이트가
조용히 죽는다. 그래서 anchor 소멸은 sum 판정과 **다른 이름**으로 RED 를 낸다.

── ★대상 문서 pin — 설계 pending (정직 declare)★ ──────────────────────────
2026-08-12 실측: 슬롯 예산 표는 ★wrapper repo 어디에도 존재하지 않는다★
(`grep -rn "Reserved (lead\\|Headroom\\|lane PL pool\\|static budget\\|슬롯 예산"`
 → 매칭 0). Story §7.7.4 안에만 있고, Story 는 `codeforge-internal-docs` repo 소속
이라 본 게이트의 스캔 대상이 아니다. §7.14 P-12 는 이 처방을 `advisory`(G2 미충족)
로 판정했을 뿐 **repo 측 carrier 를 지정하지 않았다**.

⇒ `DEFAULT_TARGET_DOC` 는 **제안 pin** 이며(Orchestrator 절차 SSOT = playbook),
   carrier 확정은 **설계 lane 소관**이다. 본 모듈은 표를 창작하지 않는다.
   표가 착지하기 전까지 live 실행은 `table_heading_not_found` RED 가 정상 거동이며
   (fail-closed, 조용한 통과 0), carrier 가 달라지면 `--doc` / `--heading` 으로
   재-pin 한다 — 판정 로직 변경 불요.

── 이 게이트가 보증하지 않는 것 (over-claim 금지) ─────────────────────────
  (a) 표의 합이 20 이라는 것은 ★admission 규율의 문서적 정합★ 일 뿐이다. Story
      §7.7.4 가 못박았듯 static budget 은 **런타임 강제가 아니며** 세션 내 running
      count 관측면이 없다. 본 게이트는 "20 슬롯이 bound 를 준다"를 보증하지 않는다.
  (b) 몫 이름(Reserved / lane PL pool / Headroom)의 **의미**는 검사하지 않는다.
      행 라벨을 바꾸고 숫자만 유지하면 미검출이다.
  (c) 행 개수는 trace 로만 emit 하고 판정하지 않는다 — 몫 분할이 3→4 로 바뀌어도
      합이 20 이면 PASS. (행 수 pin 은 정책 변경마다 false RED 를 낸다.)
  (d) heading 이후 **첫 번째** 표만 본다. 같은 절에 표가 여러 개면 뒤 표는 미관측.

exit codes: 0 = PASS / 1 = RED / 3 = INCONCLUSIVE
"""

from __future__ import annotations

import argparse
import os
import re
import sys

from gate_verdict import (  # noqa: E402
    GateResult,
    PASS,
    RED,
    emit,
    unknown_input,
)

# Windows cp949 stdout/stderr 차단 — UTF-8 강제
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

GATE_ID = "NG-21"

# ★세션 슬롯 상한★ — Story §6.1 / §7.7.4 (공식 문서 "20 subagents ... in a session").
EXPECTED_TOTAL = 20

# 설계 pending pin (위 docstring 참조). `--doc` 로 override 가능.
DEFAULT_TARGET_DOC = "docs/orchestrator-playbook.md"

# 슬롯 예산 표 anchor — markdown heading 줄에 "슬롯" ∧ ("예산"|"budget") 이 함께.
DEFAULT_HEADING_PATTERN = r"^#{2,6}\s+.*슬롯.*(?:예산|budget)"

# 슬롯 열 header 식별 — "슬롯" 또는 "slot(s)".
_BUDGET_COLUMN_HEADER = re.compile(r"슬롯|slots?", re.IGNORECASE)

_HEADING_LINE = re.compile(r"^#{1,6}\s")
_TABLE_SEPARATOR = re.compile(r"^\|[\s:|-]+\|?\s*$")

# 셀 정리 — markdown 강조·백틱·별표·쉼표·공백 제거 후 순수 정수만 남긴다.
_CELL_NOISE = re.compile(r"[*`★☆~_\s,]")
_PURE_INT = re.compile(r"^-?\d+$")


def _split_row(line):
    """`| a | b | c |` → ['a', 'b', 'c'] (양끝 빈 셀 제거)."""
    cells = line.split("|")
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return [c.strip() for c in cells]


def _find_table_block(lines, heading_idx):
    """heading 다음의 첫 markdown 표 블록을 찾는다.

    Returns: (start_idx, block_lines) 또는 (None, []) — 다음 heading 전까지 표 없음.
    """
    i = heading_idx + 1
    n = len(lines)
    while i < n:
        line = lines[i]
        if _HEADING_LINE.match(line):
            return None, []  # 다음 heading 도달 = 이 절에 표 없음
        if line.lstrip().startswith("|"):
            start = i
            block = []
            while i < n and lines[i].lstrip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            return start, block
        i += 1
    return None, []


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_slot_budget_table.py",
        description="NG-21 / AC-12 슬롯 예산 표 합 검사 (3-state verdict).",
    )
    parser.add_argument("--repo-root", default=".", help="Repository root (default: cwd)")
    parser.add_argument(
        "--doc",
        default=DEFAULT_TARGET_DOC,
        help="슬롯 예산 표가 사는 문서 (repo-root 상대경로). 설계 carrier 확정 시 재-pin.",
    )
    parser.add_argument(
        "--heading",
        default=DEFAULT_HEADING_PATTERN,
        help="표 heading 정규식 (MULTILINE, 줄 단위 적용)",
    )
    parser.add_argument(
        "--expected-total",
        type=int,
        default=EXPECTED_TOTAL,
        help="기대 합계 (default: 20)",
    )
    args = parser.parse_args(list(argv[1:]) if argv else [])

    repo_root = os.path.abspath(args.repo_root)
    rel_doc = args.doc.replace("\\", "/")
    abs_doc = os.path.join(repo_root, rel_doc.replace("/", os.sep))

    probe = {
        "repo_root": repo_root,
        "target_doc": rel_doc,
        "heading_pattern": args.heading,
        "expected_total": args.expected_total,
    }

    # ── 분기 1: 대상 문서 부재 (표 미발견의 최상위 사례) ────────────────────
    if not os.path.isfile(abs_doc):
        return emit(
            GateResult(
                gate_id=GATE_ID,
                verdict=RED,
                reason="target_doc_not_found",
                trace={"parsed_rows": 0, "sum": None, "doc_lines": 0},
                identity_probe=probe,
            )
        )

    # ── [154-AC-4] 읽기/디코드 실패 = fail-closed RED ───────────────────────
    try:
        with open(abs_doc, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        probe["detail"] = str(exc)[:120]
        return emit(
            unknown_input(
                gate_id=GATE_ID,
                reason="unparseable_doc",
                trace={"parsed_rows": 0, "sum": None, "doc_lines": 0},
                identity_probe=probe,
            )
        )

    probe["doc_lines"] = len(lines)

    # ── 분기 2: ★heading rename → anchor 소멸★ ─────────────────────────────
    heading_re = re.compile(args.heading)
    heading_idx = None
    for idx, line in enumerate(lines):
        if heading_re.search(line):
            heading_idx = idx
            break
    if heading_idx is None:
        return emit(
            GateResult(
                gate_id=GATE_ID,
                verdict=RED,
                reason="table_heading_not_found",
                trace={"parsed_rows": 0, "sum": None, "doc_lines": len(lines)},
                identity_probe=probe,
            )
        )

    probe["heading_line"] = heading_idx + 1
    probe["heading_text"] = lines[heading_idx].strip()[:160]

    # ── 분기 3: heading 은 있으나 표 블록 부재 ──────────────────────────────
    table_start, block = _find_table_block(lines, heading_idx)
    if table_start is None or not block:
        return emit(
            GateResult(
                gate_id=GATE_ID,
                verdict=RED,
                reason="table_not_found",
                trace={"parsed_rows": 0, "sum": None, "doc_lines": len(lines)},
                identity_probe=probe,
            )
        )

    probe["table_first_line"] = table_start + 1
    probe["table_block_lines"] = len(block)

    header_cells = _split_row(block[0])
    data_lines = [
        ln for ln in block[1:] if not _TABLE_SEPARATOR.match(ln)
    ]

    # ── 분기 4: ★데이터 행 0 → vacuous★ (합계 계산 이전에 끊는다) ──────────
    if not data_lines:
        return emit(
            GateResult(
                gate_id=GATE_ID,
                verdict=RED,
                reason="table_rows_zero",
                trace={
                    "parsed_rows": 0,
                    "sum": None,
                    "doc_lines": len(lines),
                    "table_block_lines": len(block),
                },
                identity_probe=probe,
            )
        )

    # ── 분기 5: 슬롯 열 header 미식별 = unknown-input ───────────────────────
    col_idx = None
    for i, cell in enumerate(header_cells):
        if _BUDGET_COLUMN_HEADER.search(_CELL_NOISE.sub("", cell)):
            col_idx = i
            break
    if col_idx is None:
        probe["header_cells"] = header_cells
        return emit(
            unknown_input(
                gate_id=GATE_ID,
                reason="budget_column_not_found",
                trace={
                    "parsed_rows": 0,
                    "sum": None,
                    "candidate_rows": len(data_lines),
                },
                identity_probe=probe,
            )
        )

    probe["budget_column_index"] = col_idx
    probe["budget_column_header"] = header_cells[col_idx]

    # ── 분기 6: 셀 파싱 — 비수치는 조용히 제외하지 않고 fail-closed RED ─────
    values = []
    row_labels = []
    for offset, ln in enumerate(data_lines):
        cells = _split_row(ln)
        label = _CELL_NOISE.sub("", cells[0]) if cells else ""
        if col_idx >= len(cells):
            probe["offending_row"] = ln[:160]
            return emit(
                unknown_input(
                    gate_id=GATE_ID,
                    reason="non_numeric_cell",
                    trace={
                        "parsed_rows": len(values),
                        "sum": sum(values) if values else 0,
                        "failed_row_index": offset,
                        "failure_kind": "missing_column",
                    },
                    identity_probe=probe,
                )
            )
        raw = _CELL_NOISE.sub("", cells[col_idx])
        if not _PURE_INT.match(raw):
            probe["offending_row"] = ln[:160]
            probe["offending_cell"] = cells[col_idx][:80]
            return emit(
                unknown_input(
                    gate_id=GATE_ID,
                    reason="non_numeric_cell",
                    trace={
                        "parsed_rows": len(values),
                        "sum": sum(values) if values else 0,
                        "failed_row_index": offset,
                        "failure_kind": "not_an_integer",
                    },
                    identity_probe=probe,
                )
            )
        values.append(int(raw))
        row_labels.append(cells[0].strip()[:60] if cells else "")

    total = sum(values)
    trace = {
        "parsed_rows": len(values),
        "sum": total,
        "expected_total": args.expected_total,
        "row_values": values,
        "doc_lines": len(lines),
    }
    probe["row_labels"] = row_labels

    # ── 분기 7: 합계 대조 (여기까지 온 것은 추출이 실증된 경우뿐) ───────────
    if total != args.expected_total:
        return emit(
            GateResult(
                gate_id=GATE_ID,
                verdict=RED,
                reason="slot_budget_sum_mismatch",
                trace=trace,
                identity_probe=probe,
            )
        )

    return emit(
        GateResult(
            gate_id=GATE_ID,
            verdict=PASS,
            reason="slot_budget_sum_ok",
            trace=trace,
            identity_probe=probe,
        )
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
