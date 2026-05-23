#!/usr/bin/env python3
"""
scripts/lib/check_claude_md_amendment_ref.py
CFP-708 / ADR-074 — CLAUDE.md Amendment ref drift detection logic

Algorithm:
  1. CLAUDE.md 안 모든 "[ADR-NNN](...)" 링크 + 인접 "Amendment N (CFP-NNN)" 패턴 detect
  2. 각 ADR 파일의 frontmatter amendment_log[] or amendments[] 길이 파악
  3. CLAUDE.md claim Amendment N > actual length → drift (exit 1)
  4. ADR 파일 미존재 → setup error (exit 2)
  5. 모두 OK → exit 0

Exit codes:
  0 = clean (no drift)
  1 = drift detected (amendment claim > ADR frontmatter length)
  2 = setup error (ADR file not found, YAML parse error)

Usage:
  python3 scripts/lib/check_claude_md_amendment_ref.py --claude-md CLAUDE.md --adr-dir docs/adr
"""

import argparse
import glob
import re
import sys
from pathlib import Path

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# YAML frontmatter 파싱 (pyyaml 없어도 동작하는 간단한 파서)
def _parse_frontmatter(content: str) -> dict:
    """--- ... --- 사이의 YAML frontmatter 를 기본 파싱."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return {}

    fm_lines = lines[1:end_idx]
    result = {}

    # 최소한 amendment_log / amendments 배열 길이 파악
    # 단순 key: 값 파싱 + 배열 항목 카운트
    current_key = None
    in_list = False
    list_count = 0

    for line in fm_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # 배열 항목 (  - amendment: N)
        if stripped.startswith("- ") and in_list:
            # amendment 배열 항목 카운트 (최상위 - 만)
            indent = len(line) - len(line.lstrip())
            if indent <= 2:  # 최상위 배열 항목
                list_count += 1
            continue

        # key: value 파싱
        if ":" in stripped and not stripped.startswith("-"):
            in_list = False
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()

            if key in ("amendment_log", "amendments"):
                current_key = key
                in_list = True
                list_count = 0
                result[key] = []  # placeholder
            elif current_key and key not in ("amendment_log", "amendments"):
                # 다른 key 진입 → 배열 종료
                if current_key in result:
                    result[current_key] = list_count
                current_key = None

    # 마지막 배열 닫기
    if current_key and current_key in result:
        result[current_key] = list_count

    return result


def _get_amendment_count(adr_path: Path) -> int:
    """ADR 파일에서 amendment_log 또는 amendments 배열 길이 반환. 없으면 0."""
    try:
        content = adr_path.read_text(encoding="utf-8")
    except OSError as e:
        raise FileNotFoundError(f"ADR file read error: {adr_path}: {e}") from e

    # pyyaml 사용 시도 (설치되어 있으면 정확)
    try:
        import yaml  # type: ignore[import]

        lines = content.splitlines()
        if lines and lines[0].strip() == "---":
            end_idx = None
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    end_idx = i
                    break
            if end_idx:
                fm_text = "\n".join(lines[1:end_idx])
                fm = yaml.safe_load(fm_text) or {}
                # amendment_log 또는 amendments 배열 길이
                for key in ("amendment_log", "amendments"):
                    if key in fm and isinstance(fm[key], list):
                        return len(fm[key])
                return 0

    except ImportError:
        pass

    # pyyaml 없음 → 간단한 파서 사용
    fm = _parse_frontmatter(content)
    for key in ("amendment_log", "amendments"):
        if key in fm:
            val = fm[key]
            if isinstance(val, int):
                return val
            if isinstance(val, list):
                return len(val)
    return 0


def _find_adr_file(adr_dir: Path, adr_num: int) -> Path | None:
    """ADR-NNN-*.md 파일 glob 탐색. 없으면 None."""
    pattern = str(adr_dir / f"ADR-{adr_num:03d}-*.md")
    matches = glob.glob(pattern)
    if not matches:
        # 0-padding 없는 형태도 시도 (예: ADR-9-...)
        pattern2 = str(adr_dir / f"ADR-{adr_num}-*.md")
        matches = glob.glob(pattern2)
    return Path(matches[0]) if matches else None


def check(claude_md_path: str, adr_dir_path: str) -> int:
    """
    Returns:
      0 = clean
      1 = drift
      2 = setup error
    """
    claude_md = Path(claude_md_path)
    adr_dir = Path(adr_dir_path)

    if not claude_md.exists():
        print(f"[ERROR] CLAUDE.md not found: {claude_md}", file=sys.stderr)
        return 2

    content = claude_md.read_text(encoding="utf-8")
    lines = content.splitlines()

    # CLAUDE.md 전체에서 두 패턴을 same-line strict pure 로 결합 detect (ADR-074 Amendment 1 §결정 9):
    #   "[ADR-NNN](...)" 링크 AND "Amendment M (CFP-K)" 인용이 동일 line 에 있어야 pair 성립.
    #   cross-context window (±5) 완전 제거 — phantom-ahead/stale-behind false-pair class 차단.

    # ADR 링크 regex
    adr_link_re = re.compile(r"\[ADR-(\d+)\]\([^)]+\)")
    # Amendment 참조 regex (캡처: amendment number)
    amend_re = re.compile(r"Amendment\s+(\d+)\s*\(CFP-\d+\)")

    # (adr_num, claimed_amendment, line_number) 튜플 목록 수집
    refs: list[tuple[int, int, int]] = []

    for line_idx, line in enumerate(lines):
        adr_matches = list(adr_link_re.finditer(line))
        if not adr_matches:
            continue

        # 이 라인에 ADR 링크가 있음 — 동일 라인에서만 Amendment 참조 탐색 (same-line strict pure)
        # option (b) Same-line strict pure: ADR-N 링크와 Amendment M (CFP-K) 인용이
        # 반드시 같은 line 에 존재해야 pairing 성립. ±5 cross-context window 제거.
        # 근거: ADR-074 Amendment 1 §결정 9 (CFP-1009 carrier).
        amend_matches = list(amend_re.finditer(line))
        if not amend_matches:
            continue

        for adr_match in adr_matches:
            adr_num = int(adr_match.group(1))
            for amend_match in amend_matches:
                claimed = int(amend_match.group(1))
                # 중복 방지 (같은 adr_num + claimed 조합)
                if (adr_num, claimed, line_idx + 1) not in refs:
                    refs.append((adr_num, claimed, line_idx + 1))

    if not refs:
        # Amendment 참조 패턴 없음 → PASS
        print("[PASS] No 'Amendment N (CFP-NNN)' references found in CLAUDE.md -- nothing to check.")
        return 0

    drift_found = False
    setup_error = False

    for adr_num, claimed, lineno in refs:
        adr_file = _find_adr_file(adr_dir, adr_num)
        if adr_file is None:
            print(
                f"[SETUP-ERROR] CLAUDE.md line {lineno}: ADR-{adr_num:03d} file not found "
                f"in {adr_dir} -- claimed Amendment {claimed}",
                file=sys.stderr,
            )
            setup_error = True
            continue

        try:
            actual_count = _get_amendment_count(adr_file)
        except FileNotFoundError as e:
            print(f"[SETUP-ERROR] {e}", file=sys.stderr)
            setup_error = True
            continue

        if actual_count == 0 and claimed > 0:
            print(
                f"[DRIFT] CLAUDE.md line {lineno}: ADR-{adr_num:03d} claims Amendment {claimed} "
                f"but ADR frontmatter has no amendment_log/amendments array. "
                f"(ADR file: {adr_file.name})"
            )
            drift_found = True
        elif claimed != actual_count:
            # claimed < actual_count: CLAUDE.md 가 최신 Amendment 미반영 (stale)
            # claimed > actual_count: CLAUDE.md 가 존재하지 않는 Amendment 참조 (phantom)
            direction = "stale (behind)" if claimed < actual_count else "phantom (ahead)"
            print(
                f"[DRIFT] CLAUDE.md line {lineno}: ADR-{adr_num:03d} Amendment {claimed} claim "
                f"is {direction} -- ADR frontmatter amendment count = {actual_count} "
                f"(latest = Amendment {actual_count}). "
                f"(ADR file: {adr_file.name})"
            )
            drift_found = True
        else:
            print(
                f"[OK] CLAUDE.md line {lineno}: ADR-{adr_num:03d} Amendment {claimed} "
                f"(ADR has {actual_count} amendments -- claim matches latest)"
            )

    if setup_error:
        return 2
    if drift_found:
        return 1
    print("[PASS] All Amendment refs are current.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CFP-708/ADR-074 CLAUDE.md Amendment ref drift detection"
    )
    parser.add_argument("--claude-md", default="CLAUDE.md", help="Path to CLAUDE.md")
    parser.add_argument("--adr-dir", default="docs/adr", help="Path to ADR directory")
    args = parser.parse_args()

    sys.exit(check(args.claude_md, args.adr_dir))


if __name__ == "__main__":
    main()
