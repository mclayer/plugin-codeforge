#!/usr/bin/env python3
"""
CFP-841 / ADR-082 Amendment 1 §결정 6 scope(a) — corpus annotation lint
corpus enumeration token + file-path co-occurrence → [verified: ...] annotation 검출

4-guard FP 완화 (ADR-068 I-5 + ADR-082 §결정 4/6 EC-3 prior art 직접 재사용):
  guard-1: file-path co-occurrence guard (corpus token + file-path 동시 매칭 시만)
  guard-2: citation≠assertion 면제 (§N 가 ... 판정 / RequirementsPL §5 attribution 패턴)
  guard-3: forward-only effective-date (CORPUS_VERIFY_EFFECTIVE_DATE 이후 신규 line)
  guard-4: self-referential exemption (ADR-082 §결정 6 EC-3 verbatim file allowlist)

ADR-061: multi-line Python 외부 .py 파일 의무.
Local run: python3 scripts/check-corpus-claim-verify.py [file ...]
Exit code: 0=PASS, 1=violation, 2=error
"""

import sys
import re
import os
import subprocess
from datetime import date
from typing import List, Optional

# ─── 상수 정의 ───

# corpus enumeration token (ADR-082 §결정 2(a) 정합)
CORPUS_TOKENS = [
    r'예시\s+\d+건',
    r'전무',
    r'부재',
    r'다수',
]
CORPUS_TOKEN_RE = re.compile('|'.join(CORPUS_TOKENS))

# file-path 인용 패턴 (docs/ templates/ scripts/ .claude/ 경로 포함 md/yaml/yml/py/sh/json)
FILE_PATH_RE = re.compile(
    r'(?:docs/|templates/|scripts/|\.claude/)[\w./_-]*\.(?:md|yaml|yml|py|sh|json)'
)

# [verified: ...] annotation 패턴
VERIFIED_ANNOTATION_RE = re.compile(r'\[verified:\s*git show\s+\S+:\S+\]')

# citation≠assertion 면제 패턴 (guard-2): "§N 가 ... 판정" / "RequirementsPL §N ..." 등 attribution
CITATION_PATTERN_RE = re.compile(
    r'(?:§\d[\d.]*\s+가\s|RequirementsPL\s§|ArchitectAgent\s§|ADR-\d+\s§|'
    r'판정\s+SSOT|SSOT\s판정|verified:\s+git|carrier\s+merge\s|carrier\s+PR)'
)

# self-referential exemption allowlist (guard-4, ADR-082 §결정 6 EC-3 verbatim)
SELF_REF_ALLOWLIST_PATTERNS = [
    r'docs/adr/ADR-082-.*\.md',
    r'wrapper/stories/CFP-776\.md',
    r'wrapper/stories/CFP-841\.md',
    r'change-plans/.*cfp-841.*\.md',
    r'check-corpus-claim-verify',     # 본 스크립트 self-flag 차단
    r'test-check-corpus-claim-verify',  # 본 bats fixture self-flag 차단
    r'test-check-cross-plugin-ownership-verify',  # sibling bats fixture self-flag 차단 (F-CR-841-3)
]
SELF_REF_RE = re.compile('|'.join(SELF_REF_ALLOWLIST_PATTERNS))

# forward-only effective date (guard-3)
DEFAULT_EFFECTIVE_DATE_STR = "2026-05-17"


def get_effective_date() -> date:
    """환경변수 CORPUS_VERIFY_EFFECTIVE_DATE 또는 기본값 반환."""
    env_val = os.environ.get("CORPUS_VERIFY_EFFECTIVE_DATE", DEFAULT_EFFECTIVE_DATE_STR)
    try:
        parts = env_val.split("-")
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except Exception:
        return date(2026, 5, 17)


def get_file_blame_dates(filepath: str) -> List[Optional[date]]:
    """git blame --line-porcelain 으로 각 소스 line 의 commit date 반환 (1:1 index-aligned).

    --line-porcelain: 모든 소스 line 마다 full commit info(author-time 포함) emit.
    --porcelain 대비: commit-block 당 1회 → 소스 line 당 1회로 index 정렬 정합.
    encoding="utf-8", errors="replace": non-UTF-8 locale UnicodeDecodeError 차단.
    """
    try:
        result = subprocess.run(
            ["git", "blame", "--line-porcelain", filepath],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10
        )
        if result.returncode != 0:
            return []
        import datetime
        dates = []
        for line in result.stdout.splitlines():
            if line.startswith("author-time "):
                ts = int(line.split()[1])
                dates.append(datetime.date.fromtimestamp(ts))
        return dates
    except (subprocess.SubprocessError, OSError, ValueError) as e:
        print(f"WARN: git blame failed for {filepath}: {e}", file=sys.stderr)
        return []


def is_self_referential(filepath: str) -> bool:
    """guard-4: 파일 자체가 allowlist 패턴에 매칭되면 면제."""
    norm = filepath.replace("\\", "/")
    return bool(SELF_REF_RE.search(norm))


def check_file(filepath: str, effective_date: date, violations: list) -> None:
    """단일 파일 corpus annotation 검출."""
    if is_self_referential(filepath):
        return

    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"ERROR: {filepath}: {e}", file=sys.stderr)
        return

    blame_dates = get_file_blame_dates(filepath)

    for i, line in enumerate(lines):
        # guard-3: forward-only — blame date 가 effective_date 이전 line 면제
        if blame_dates and i < len(blame_dates) and blame_dates[i] is not None:
            if blame_dates[i] < effective_date:
                continue

        # guard-1: corpus token + file-path co-occurrence
        # ±2줄 window 구성
        window_start = max(0, i - 2)
        window_end = min(len(lines), i + 3)
        window = "".join(lines[window_start:window_end])

        has_corpus_token = bool(CORPUS_TOKEN_RE.search(line))
        if not has_corpus_token:
            continue

        has_file_path_in_window = bool(FILE_PATH_RE.search(window))
        if not has_file_path_in_window:
            # guard-1: corpus token 단독 (file-path 동반 없음) → 면제
            continue

        # guard-2: citation≠assertion 면제
        if CITATION_PATTERN_RE.search(line):
            continue
        # ±2줄 window 에서 attribution 패턴 확인
        if CITATION_PATTERN_RE.search(window):
            continue

        # [verified: ...] annotation 보유 여부 확인 (±2줄 window)
        if VERIFIED_ANNOTATION_RE.search(window):
            continue

        # violation 감지
        lineno = i + 1
        violations.append({
            "file": filepath,
            "line": lineno,
            "text": line.rstrip(),
        })


def main() -> int:
    args = sys.argv[1:]

    # 파일 지정 없으면 PASS (빈 입력)
    if not args:
        sys.stdout.buffer.write(b"PASS: no scan targets (0 files)\n")
        return 0

    effective_date = get_effective_date()
    violations = []

    for filepath in args:
        if os.path.isfile(filepath):
            check_file(filepath, effective_date, violations)
        elif os.path.isdir(filepath):
            for root, _dirs, files in os.walk(filepath):
                for fname in files:
                    if fname.endswith((".md", ".yaml", ".yml")):
                        check_file(os.path.join(root, fname), effective_date, violations)

    if violations:
        sys.stdout.buffer.write(
            ("FAIL: corpus-claim-verify -- CORPUS_CLAIM_UNVERIFIED "
             f"{len(violations)} violation(s)\n").encode("utf-8")
        )
        for v in violations:
            sys.stdout.buffer.write(
                (f"  [{v['file']}:{v['line']}] {v['text'][:120]}\n").encode("utf-8")
            )
        sys.stdout.buffer.write(
            b"\nFix: add [verified: git show <ref>:<path>] annotation after corpus claim\n"
            b"bypass channel: hotfix-bypass:corpus-claim-verify label\n"
        )
        return 1

    sys.stdout.buffer.write(
        (f"PASS: corpus-claim-verify -- 0 violation(s) "
         f"(effective_date={effective_date})\n").encode("utf-8")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
