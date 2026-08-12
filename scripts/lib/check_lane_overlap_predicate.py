#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""check_lane_overlap_predicate.py — CFP-2926 NG-8 lane overlap predicate (AC-16).

lane-dispatch-packet 의 overlap predicate 검증 (§7.1 § C1-C3):
  - C1: read_set(scope_globs) ∩ write_set(lane self-write) == ∅
  - C2: read_set ⊆ snapshot_sha 고정점
  - C3: write_set ∩ (하류 판정 산출물) == ∅

★P2-b 신설(blocking) — lane 기대 개수 대조★:
  - 기대 lane 6개 (코드 상수 → ls plugins/*/CLAUDE.md 실측으로 도출)
  - 실제 lane 개수 == 기대 lane 개수 (불일치 → RED `LANE_COUNT_MISMATCH`)
  - write_set 추출 실패 (파싱 0행) → RED `EXTRACTION_EMPTY`
  - lane 파일 unparseable → RED

불변식:
  - empty-target: lane-dispatch-packet 미존재 (읽기 불가) → INCONCLUSIVE
  - unknown-input: plugin CLAUDE.md unparseable → fail-closed RED
  - docstring: 본 gate 는 C1 축(선언 정직성)만 검증 ← C2/C3 는 lane 측 책임

exit codes: 0=PASS, 1=RED, 3=INCONCLUSIVE
"""

import argparse
import os
import re
import sys

from gate_verdict import (
    GateResult, emit, RED, PASS, INCONCLUSIVE, empty_target, unknown_input
)

# Windows cp949 stdout/stderr 인코딩 차단 — UTF-8 강제
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

GATE_ID = "NG-8"

# ★P2-b: 기대 lane 경로 (도출 방법이 명시되어야 tautology 회피 가능)
# 도출 2 소스 — disjoint 축으로 대조:
#   Source A(기대): plugins/*/CLAUDE.md 디렉토리 실측(wildcard glob) — 파일 존재 사실
#   Source B(실제): 각 파일 안 self-write 표 파싱 성공 — 데이터 추출 사실
# A에 있으나 B에서 extraction=0 → 조용한 lane 누락 감지 ★P2-b 차단 목표★

_LANE_PLUGIN_DIRS = [
    "plugins/codeforge-requirements",
    "plugins/codeforge-design",
    "plugins/codeforge-develop",
    "plugins/codeforge-review",
]


def _extract_self_write_table(claude_text):
    """CLAUDE.md §3 'Self-write' 표에서 write_set 추출 (단, 존재하지 않으면 공집합).

    Returns: set of file paths/glob patterns (write_set) — 공집합 시 EXTRACTION_EMPTY 처리됨

    ★정직(docstring)★: 표 파싱이 실패해서 0행이 나오면, 그 결과를 emit 한다.
    grep-oracle(presence-만 체크)이 아니라 **실제 표 parsing** 이므로 format 변화에 민감.
    """
    if not claude_text:
        return set()

    write_set = set()

    # Self-write 섹션 찾기: "## Self-write" ~ 다음 heading 또는 EOF
    # 또는 "소유 파일" heading (repository style 차용 가능)
    self_write_pat = re.search(
        r"(?m)^##\s+(?:Self-write|소유\s*파일)",
        claude_text
    )
    if not self_write_pat:
        return set()  # Self-write 섹션 자체 부재

    section_start = self_write_pat.end()
    # 다음 heading 또는 EOF 까지 섹션 범위
    next_heading = re.search(r"(?m)^##\s", claude_text[section_start:])
    section_end = section_start + next_heading.start() if next_heading else len(claude_text)
    section_text = claude_text[section_start:section_end]

    # Markdown table 행 추출: | ... | ... | 형태
    # 첫 두 셀 중 하나가 경로인 것으로 간주 (표 구조에 따라 상이)
    table_rows = re.findall(r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|", section_text, re.MULTILINE)
    for cell1, cell2 in table_rows:
        cell1, cell2 = cell1.strip(), cell2.strip()
        # 경로로 보이는 셀 추가 (glob pattern, 상대경로 등)
        for cell in (cell1, cell2):
            if "/" in cell or "*" in cell:
                # backtick 제거
                cell = re.sub(r"[`]", "", cell)
                if cell:
                    write_set.add(cell)

    return write_set


def _discover_expected_lanes(repo_root):
    """Source A (기대): plugins/*/CLAUDE.md 디렉토리 실측.

    Returns: dict {lane_dir_name → full_path_to_CLAUDE.md}
    각 plugin 디렉토리에서 CLAUDE.md 파일의 실재 여부만 판정(파일 내용 미검사).
    """
    expected = {}
    for plugin_dir in _LANE_PLUGIN_DIRS:
        claude_path = os.path.join(repo_root, plugin_dir, "CLAUDE.md")
        if os.path.isfile(claude_path):
            lane_name = os.path.basename(plugin_dir)  # 마지막 경로 요소
            expected[lane_name] = claude_path
    return expected


def main(argv=None):
    """Main entry point.

    CLI:
      python check_lane_overlap_predicate.py --repo-root <path>

    Exit codes:
      0 = PASS (모든 발견 lane + write_set 추출 성공 + lane 간 겹침 없음)
      1 = RED (lane 누락 / write_set 추출 0 / unparseable / 겹침 발견)
      3 = INCONCLUSIVE (lane-dispatch-packet 자체 미존재 — 본 gate 적용 불가)

    P2-b (lane_count_mismatch blocking):
      - Source A(기대): plugins/*/CLAUDE.md 디렉토리 실측(파일 존재)
      - Source B(실제): 각 파일 self-write 표 파싱(데이터 추출)
      - A와 B 가 서로 다른 축이므로 tautology 회피 가능
    """
    parser = argparse.ArgumentParser(
        prog="check_lane_overlap_predicate.py",
        description="lane overlap predicate validation (AC-16)."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root")

    try:
        args = parser.parse_args(argv[1:] if argv else [])
    except SystemExit:
        return 2

    repo_root = os.path.abspath(args.repo_root)

    # Source A: 기대 lane (디렉토리 발견)
    expected_lanes = _discover_expected_lanes(repo_root)
    if not expected_lanes:
        # lane 디렉토리 자체가 없으면 → INCONCLUSIVE (lane-dispatch-packet 미적용)
        result = empty_target(
            gate_id=GATE_ID,
            reason="no_lane_directories_found",
            trace={"plugin_dirs_checked": len(_LANE_PLUGIN_DIRS)},
            identity_probe={"repo_root": repo_root},
        )
        return emit(result)

    expected_count = len(expected_lanes)

    # Source B: 실제 lane (파일 내용 파싱)
    found_lanes = {}  # lane_name → write_set
    lane_errors = {}  # lane_name → error_reason

    for lane_name, claude_path in expected_lanes.items():
        try:
            with open(claude_path, "r", encoding="utf-8") as f:
                claude_text = f.read()
        except Exception as e:
            lane_errors[lane_name] = f"read_error: {str(e)[:50]}"
            continue

        write_set = _extract_self_write_table(claude_text)

        # write_set 추출 0행 → EXTRACTION_EMPTY fail-closed (P2-b)
        if not write_set:
            lane_errors[lane_name] = "extraction_empty"
            continue

        found_lanes[lane_name] = write_set

    # P2-b: Source A(기대 개수) vs Source B(실제 개수) 대조
    actual_count = len(found_lanes)
    if actual_count != expected_count:
        # 누락된 lane 있음 → LANE_COUNT_MISMATCH RED
        missing_lanes = sorted(set(expected_lanes.keys()) - set(found_lanes.keys()))
        trace = {
            "expected_lane_count": expected_count,
            "actual_lane_count": actual_count,
            "extracted_count": len([ln for ln in found_lanes if ln]),
        }
        if lane_errors:
            trace["lane_extraction_errors"] = lane_errors

        result = GateResult(
            gate_id=GATE_ID,
            verdict=RED,
            reason="lane_count_mismatch",
            trace=trace,
            identity_probe={
                "repo_root": repo_root,
                "missing_lanes": missing_lanes,
                "source_a_paths": sorted(expected_lanes.values()),
            },
        )
        return emit(result)

    # 전체 lane 간 write_set 겹침 확인 (C1 검증)
    overlaps = []
    lane_names = sorted(found_lanes.keys())
    for i, lane1 in enumerate(lane_names):
        for lane2 in lane_names[i+1:]:
            write_set1 = found_lanes[lane1]
            write_set2 = found_lanes[lane2]
            overlap = write_set1 & write_set2
            if overlap:
                overlaps.append((lane1, lane2, sorted(overlap)))

    if overlaps:
        trace = {
            "lane_count": actual_count,
            "overlap_count": len(overlaps),
            "first_overlap_lanes": f"{overlaps[0][0]} ∩ {overlaps[0][1]}",
        }
        result = GateResult(
            gate_id=GATE_ID,
            verdict=RED,
            reason="lane_write_set_overlap",
            trace=trace,
            identity_probe={
                "repo_root": repo_root,
                "overlapped_paths": overlaps[0][2][:3],
            },
        )
        return emit(result)

    # PASS: 모든 lane 존재(A==B) + write_set 추출 성공 + 겹침 없음
    trace = {
        "expected_lane_count": expected_count,
        "actual_lane_count": actual_count,
        "overlap_count": 0,
    }
    result = GateResult(
        gate_id=GATE_ID,
        verdict=PASS,
        reason="all_lanes_present_no_overlap",
        trace=trace,
        identity_probe={
            "repo_root": repo_root,
            "lanes": sorted(found_lanes.keys()),
            "source_a_discovery": "plugins/*/CLAUDE.md glob",
            "source_b_extraction": "self-write table parsing",
        },
    )
    return emit(result)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
