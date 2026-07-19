#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_active_sessions_presence.py
CFP-2761 §5.2 / ADR-085 §결정8 — Story active_sessions presence PR-time lint (warning tier).

멀티세션 협업 프로토콜(ADR-085)의 active_sessions[] 소유 기록이 Story 산출물에 **존재**하는지를
PR 시점(커밋된 content 관측)에 검사한다. committed-content observable — 커밋된 파일만 보고 판정.

검사 대상:
  Story markdown (default glob docs/stories/**/*.md, repo-root 상대; 또는 명시 --files).
  각 Story 파일:
    PASS = frontmatter 에 active_sessions 키 존재 OR 본문에 <!-- active_sessions --> 블록 존재.
    else = warn (active_sessions[] frontmatter 도 body 블록도 부재).

DoS guard (§8.6, ADR-082 Amendment 38 resource-safety): anchored bounded regex + per-line length
  cap + O(n) frontmatter 경계 파싱. 총 작업량 유한 bound (bounded degradation — 임의 입력 무해 아님).

CLI 계약 (ADR-061 house style — 고정, self-test + hook 소비):
  bash scripts/check-active-sessions-presence.sh --repo-root DIR [--files STORY.md ...]
    → DIR 하 docs/stories/**/*.md (default) 또는 명시 --files 만 스캔.

Exit codes (ADR-060 §결정5 tri-tier — warning tier, advisory NEVER blocks):
  0 = clean (finding 0) OR warning finding 방출 OR zero-target honest no-op.
      finding 은 STDOUT 에 `::warning::active-sessions-presence: <detail>` 로 surface (advisory).
  2 = usage/argparse 오류.
  3 = born-hollow fail-closed (repo-root 부재 / dir 아님).
  1 = strict-tier 미사용 (warning tier).
  zero-target(TC-EMPTY) = honest-degrade: exit 0 + 명시 non-silent line (silent-green 금지).

ADR refs: CFP-2761 §5.2 (carrier) / ADR-085 §결정8 (multi-session active_sessions presence owner) /
  ADR-060 §결정5 (warning tri-tier) / ADR-082 Amendment 38 §8.6 (resource-safety DoS guard) /
  ADR-061 §결정1 (Python SSOT + thin wrapper).
"""

import argparse
import glob
import os
import re
import sys

# Windows cp949 stdout/stderr 인코딩 차단 — UTF-8 강제 (ADR-061 portability 답습).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

CHECK_NAME = "active-sessions-presence"

# per-file 물리 라인 스캔 cap + per-line length cap (§8.6 bounded read).
PER_FILE_SCAN_CAP = 50000
MAX_PHYSICAL_LINE_LEN = 8192

# frontmatter 안 active_sessions 키 (top-level `active_sessions:` 라인).
_FM_ACTIVE_SESSIONS_RE = re.compile(r"^active_sessions\s{0,8}:")
# 본문 active_sessions 블록 마커.
_BODY_ACTIVE_SESSIONS_RE = re.compile(r"<!--\s{0,8}active_sessions\s{0,8}-->")

DEFAULT_STORY_GLOB = os.path.join("docs", "stories", "**", "*.md")


def _read_lines_bounded(path):
    """파일을 라인 count cap + per-line truncate 로 bounded read. 실패 → None."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = []
            for idx, raw in enumerate(f):
                if idx >= PER_FILE_SCAN_CAP:
                    break
                if len(raw) > MAX_PHYSICAL_LINE_LEN:
                    raw = raw[:MAX_PHYSICAL_LINE_LEN]
                lines.append(raw.rstrip("\n").rstrip("\r"))
            return lines
    except OSError:
        return None


def _has_active_sessions(lines):
    """frontmatter active_sessions 키 OR 본문 <!-- active_sessions --> 블록 존재 여부."""
    # frontmatter 블록 경계: 선두 `---` ... 다음 `---`.
    in_fm = False
    fm_started = False
    for idx, line in enumerate(lines):
        if idx == 0 and line.strip() == "---":
            in_fm = True
            fm_started = True
            continue
        if in_fm:
            if line.strip() == "---":
                in_fm = False
                continue
            if _FM_ACTIVE_SESSIONS_RE.match(line):
                return True
        else:
            if _BODY_ACTIVE_SESSIONS_RE.search(line):
                return True
    # frontmatter 없이 시작한 파일도 본문 블록만 재확인 (fm_started False 경로 커버).
    if not fm_started:
        for line in lines:
            if _BODY_ACTIVE_SESSIONS_RE.search(line):
                return True
    return False


def _collect_story_files(repo_root, explicit_files):
    """explicit_files 지정 시 그 파일만, 아니면 docs/stories/**/*.md."""
    if explicit_files:
        paths = [os.path.abspath(p) for p in explicit_files]
    else:
        paths = glob.glob(os.path.join(repo_root, DEFAULT_STORY_GLOB), recursive=True)
    out = []
    for p in sorted(set(paths)):
        if os.path.isfile(p) and p.endswith(".md"):
            out.append(p)
    return out


def main(argv):
    parser = argparse.ArgumentParser(
        prog="check_active_sessions_presence.py",
        description="Story active_sessions presence PR-time lint (warning tier).",
    )
    parser.add_argument("--repo-root", default=None, help="스캔 루트 (기본 = scripts/lib 기준 자동 탐지).")
    parser.add_argument("--files", nargs="*", default=None, help="명시 Story 파일만 스캔.")
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2

    repo_root = args.repo_root
    if repo_root is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    repo_root = os.path.abspath(repo_root)
    if not os.path.isdir(repo_root):
        print(
            "::error::%s: repo-root 부재 또는 dir 아님: %s (born-hollow fail-closed)"
            % (CHECK_NAME, repo_root),
            file=sys.stderr,
        )
        return 3

    story_files = _collect_story_files(repo_root, args.files)
    if not story_files:
        print("%s: no candidate targets scanned (honest no-op)" % CHECK_NAME)
        return 0

    findings = []
    for path in story_files:
        rel = os.path.relpath(path, repo_root).replace(os.sep, "/")
        lines = _read_lines_bounded(path)
        if lines is None:
            continue
        if not _has_active_sessions(lines):
            findings.append(rel)

    if findings:
        for rel in findings:
            print(
                "::warning::%s: %s: Story lacks active_sessions[] frontmatter and "
                "<!-- active_sessions --> body block" % (CHECK_NAME, rel)
            )
        print(
            "%s: %d finding over %d story — warning tier (advisory, PR 미차단)"
            % (CHECK_NAME, len(findings), len(story_files))
        )
        return 0

    print(
        "%s: PASS — active_sessions presence 확인 %d story (warning tier)"
        % (CHECK_NAME, len(story_files))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
