#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-fix-event-depth-scope-presence.py
CFP-842 / ADR-067 Amendment 1 §결정 4 / ADR-060 §결정 5

fix-event-v1 v1.3 depth-aware scope 의 mechanical enforcement advisory layer.

§10 FIX Ledger 표 파싱 → 각 row 의 트리거 컬럼에 broken-link / path 정정 계열
heuristic grep 감지 → 해당 row 의 `affected_paths_with_depth` column (11번째)
non-null 검증. 누락 시 advisory warning 출력.

Heuristic patterns (false-positive risk 명시):
  broken-link / broken link / path 정정 / link 정정 / 404 / dangling /
  relative path / doc-location-registry / link target / href /
  cross-module path / over-correction

Warning tier (ADR-060 §결정 5, first iteration):
  exit 0 = PASS (모든 detected row 에 affected_paths_with_depth 존재 또는 0 row)
  exit 1 = WARNING (하나 이상의 row 에 affected_paths_with_depth 누락)
  exit 2 = SETUP error (파일 미존재 / §10 표 파싱 실패)

Self-meta loop 차단:
  hotfix-bypass:fix-event-depth-scope label 부착 시 workflow 에서 conditional skip.
  본 스크립트 자체는 exit 코드만 담당.

Sandbox isolation (#836 lesson):
  CBL_SKIP_ISSUE_CREATE=1 -live repo write 영역 없음 (lint only).
  본 스크립트는 파일 read-only + stdout advisory 출력 only.

Usage:
  python3 scripts/check-fix-event-depth-scope-presence.py <story-file-path>
  python3 scripts/check-fix-event-depth-scope-presence.py docs/stories/CFP-NNN.md

Exit codes (ADR-060 §결정 15 3-tier):
  0 = PASS
  1 = WARNING (advisory, warning tier)
  2 = SETUP error (missing file / parse error)

False-positive risk 명시 (§7.2 TM-1):
  어휘 grep heuristic 만으로 semantic precision 불가.
  "broken-link" 어휘가 있어도 depth annotation 이 불필요한 경우 존재.
  false-positive 는 bypass label + reviewer responsibility.
"""

import re
import sys
import os

# Windows cp949 / 기타 좁은 locale 환경에서 UTF-8 출력 강제
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf8"):
    import io
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# §10 FIX Ledger 표 섹션 탐지 패턴
SECTION_10_PATTERN = re.compile(r"##\s+§10\s+FIX\s+Ledger", re.IGNORECASE)

# 표 헤더 행 패턴 (| Iter | 로 시작)
HEADER_ROW_PATTERN = re.compile(r"^\|\s*Iter\s*\|", re.IGNORECASE)

# 구분선 행 패턴 (|---|--- 형식)
SEPARATOR_ROW_PATTERN = re.compile(r"^\|[-| :]+\|")

# 다음 섹션 (## §N) 시작 패턴
NEXT_SECTION_PATTERN = re.compile(r"^##\s+§\d+")

# broken-link / path 정정 계열 heuristic grep 패턴
BROKEN_LINK_HEURISTIC_PATTERN = re.compile(
    r"broken.link|broken link|path 정정|link 정정|\b404\b|dangling|"
    r"relative path|doc-location-registry|link target|\bhref\b|"
    r"cross-module path|over-correction",
    re.IGNORECASE,
)


def read_story_file(filepath):
    """Story 파일 읽기. 파일 없으면 exit 2."""
    if not os.path.isfile(filepath):
        print(
            f"[fix-event-depth-scope-presence] SETUP ERROR: 파일 미존재 -{filepath}",
            file=sys.stderr,
        )
        sys.exit(2)
    with open(filepath, encoding="utf-8", errors="replace") as f:
        return f.readlines()


def find_section_10_start(lines):
    """
    §10 FIX Ledger 섹션 시작 라인 index 반환.
    미발견 시 None.
    """
    for idx, line in enumerate(lines):
        if SECTION_10_PATTERN.search(line):
            return idx
    return None


def parse_fix_ledger_rows(lines, section_start):
    """
    §10 섹션부터 다음 ##  §N 섹션 전까지 FIX Ledger 표 파싱.

    Returns:
      list of dict {
        "row_index": int (원본 라인 index),
        "columns": list[str] (셀 값 strip),
        "trigger": str,           # 4번째 column (0-indexed: 3)
        "affected_paths": str,    # 11번째 column (0-indexed: 10), 없으면 ""
      }
    """
    rows = []
    in_table = False
    header_col_count = 0

    for idx in range(section_start + 1, len(lines)):
        line = lines[idx]
        stripped = line.strip()

        # 다음 섹션 도달 시 중단
        if NEXT_SECTION_PATTERN.match(stripped):
            break

        # 표 헤더 행 탐지
        if HEADER_ROW_PATTERN.match(stripped):
            in_table = True
            # 헤더 column 수 파악
            header_cols = [c.strip() for c in stripped.split("|")]
            # 앞뒤 빈 문자열 제거 (| 로 시작·끝나는 경우)
            header_cols = [c for c in header_cols if c]
            header_col_count = len(header_cols)
            continue

        # 구분선 행 스킵
        if in_table and SEPARATOR_ROW_PATTERN.match(stripped):
            continue

        # 데이터 행 파싱
        if in_table and stripped.startswith("|") and stripped.endswith("|"):
            cols = [c.strip() for c in stripped.split("|")]
            cols = [c for c in cols if c or True]  # 빈 문자열 포함하여 분할 후
            # | 로 split 하면 앞뒤 빈 str 이 생김 -제거
            cols_raw = stripped.split("|")
            # 첫·마지막 빈 원소 제거
            if cols_raw and cols_raw[0] == "":
                cols_raw = cols_raw[1:]
            if cols_raw and cols_raw[-1] == "":
                cols_raw = cols_raw[:-1]
            cols = [c.strip() for c in cols_raw]

            # 최소 4 column (Iter / 시각 / 레인 / 트리거) 있어야 데이터 행
            if len(cols) < 4:
                continue

            trigger = cols[3] if len(cols) > 3 else ""
            # 11번째 column (0-indexed 10) = affected_paths_with_depth
            affected_paths = cols[10] if len(cols) > 10 else ""

            rows.append({
                "row_index": idx,
                "line_number": idx + 1,
                "columns": cols,
                "trigger": trigger,
                "affected_paths": affected_paths,
            })

    return rows


def is_broken_link_row(row):
    """트리거 컬럼에 broken-link / path 정정 계열 heuristic 어휘 포함 여부."""
    return bool(BROKEN_LINK_HEURISTIC_PATTERN.search(row["trigger"]))


def has_affected_paths(row):
    """
    affected_paths_with_depth column 이 non-null, non-empty 인지.
    "null" / "" / column 자체 부재 는 null 로 간주.
    """
    val = row["affected_paths"].strip()
    if not val:
        return False
    if val.lower() == "null":
        return False
    return True


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python3 check-fix-event-depth-scope-presence.py <story-file-path>",
            file=sys.stderr,
        )
        sys.exit(2)

    filepath = sys.argv[1]

    # 파일 읽기
    lines = read_story_file(filepath)

    # §10 FIX Ledger 섹션 탐지
    section_start = find_section_10_start(lines)
    if section_start is None:
        # §10 섹션 자체 부재 -TC-5 (non-§10 commit) → PASS
        print(
            f"[fix-event-depth-scope-presence] PASS -§10 FIX Ledger 섹션 부재 (non-§10 commit): {filepath}"
        )
        sys.exit(0)

    # FIX Ledger 행 파싱
    rows = parse_fix_ledger_rows(lines, section_start)

    if not rows:
        # 표 행 없음 (header + 구분선만 또는 빈 표) → PASS
        print(
            f"[fix-event-depth-scope-presence] PASS -§10 FIX Ledger 표 행 없음 (FIX 0건): {filepath}"
        )
        sys.exit(0)

    # broken-link / path 정정 계열 행 필터
    broken_link_rows = [r for r in rows if is_broken_link_row(r)]

    if not broken_link_rows:
        # broken-link 계열 FIX row 없음 → TC-3 (non-broken-link FIX) → PASS
        print(
            f"[fix-event-depth-scope-presence] PASS -broken-link/path 정정 계열 FIX row 없음: {filepath}"
        )
        sys.exit(0)

    # affected_paths_with_depth 누락 행 검사
    missing_rows = [r for r in broken_link_rows if not has_affected_paths(r)]

    if not missing_rows:
        # TC-1 (broken-link FIX with depth) → PASS
        total = len(broken_link_rows)
        print(
            f"[fix-event-depth-scope-presence] PASS -"
            f"{total} broken-link/path 정정 FIX row(s) 모두 affected_paths_with_depth 존재: {filepath}"
        )
        sys.exit(0)

    # WARNING: affected_paths_with_depth 누락 행 존재 → TC-2
    print(
        f"[fix-event-depth-scope-presence] WARNING -"
        f"{len(missing_rows)}/{len(broken_link_rows)} broken-link/path 정정 FIX row(s) 에 "
        f"affected_paths_with_depth 누락 (advisory only -warning tier, ADR-060 §결정 5): {filepath}"
    )
    for r in missing_rows:
        trigger_preview = r["trigger"][:80]
        print(f"  line {r['line_number']}: trigger=[{trigger_preview}]")

    print(
        "  Note: 어휘 grep heuristic 만 사용 (semantic precision 불가) -"
        "false-positive 가능. reviewer responsibility. "
        "bypass: hotfix-bypass:fix-event-depth-scope label (ADR-024 Amendment 3 §결정 6.A, 40th family)"
    )
    # warning tier: exit 1 (not blocking)
    sys.exit(1)


if __name__ == "__main__":
    main()
