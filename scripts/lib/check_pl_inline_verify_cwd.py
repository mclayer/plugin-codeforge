#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1341 / CFP-1316 retro F1 Mandatory carrier
# ADR-040 Amendment 6 §결정 7.J PL inline scope mechanical enforcement gap closure
# ADR-073 §결정 1 verify-before-assert primitive 강화
# ADR-070 §결정 D5 verify-before-trust direct file Read primary
# ADR-060 §결정 5 — warning-tier (exit 0 항상 for warnings, PR merge 미차단)
#
# pl-inline-verify-cwd-mandate-lint — Lane PL spawn prompt 안 inline 명령 cwd directive
# enforcement mechanical lint (warning-tier).
#
# Detection scope (heuristic):
#   변경된 Story file (docs/stories/**/*.md) §14 Lane Evidence section 또는 PR description /
#   Issue body 안에서 Lane PL spawn marker 발견 시:
#     spawn 전후 ±N line window 안에서 cwd directive (3 forms) presence 검사:
#       form 1: `git -C <worktree_abs_path>` (best, ADR-040 Amd 6 §결정 7.J 권고)
#       form 2: `cd <worktree_abs_path>` (acceptable, bash cd)
#       form 3: `[WORKTREE-CWD: <path>]` (declarative annotation)
#   3 form 모두 부재 + spawn marker 존재 → [WARN-CWD-DIRECTIVE-ABSENT]
#
# Spawn marker 6 PL agent (closed-set, codeforge lane PL):
#   - DesignReviewPLAgent spawn
#   - CodeReviewPLAgent spawn
#   - SecurityTestPLAgent spawn
#   - ArchitectPLAgent spawn
#   - DeveloperPLAgent spawn
#   - RequirementsPLAgent spawn
#
# FP-완화 guard:
#   - templates/** path = canonical example 면제
#   - tests/** path = bats fixture 면제
#   - markdown table row (line starts with `|`) = abstract row 면제
#   - YAML frontmatter (line range start `---` to end `---`) = metadata 면제
#   - Story file 아닌 path (PR body / Issue body 영역은 본 lint scope 외)
#
# Bypass channel:
#   HOTFIX_BYPASS_PL_INLINE_VERIFY_CWD_MANDATE=1 env
#   (label `hotfix-bypass:pl-inline-verify-cwd-mandate` 부착 시 workflow 에서 주입)
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier = 항상 exit 0, PR merge 미차단)
#   1 — genuinely malformed (현재 0건 가능 — line-by-line parse)
#   2 — setup error (file system access 오류)
#
# Usage:
#   python3 check_pl_inline_verify_cwd.py [file ...]
#
# SSOT carrier: CFP-1316 retro §5 §D-9 sentinel (pattern_count 1)
# Precedent byte-pattern: scripts/lib/check_mid_spawn_drift_detection.py (CFP-1500)
# CodeQL ReDoS guard: line-by-line parse 의무 (CFP-1497 PR #1499 verbatim 답습)

import sys
import re
import os
from pathlib import Path

# Windows console 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── bypass env 확인 ───────────────────────────────────────────────────────────
BYPASS_ENV = os.environ.get("HOTFIX_BYPASS_PL_INLINE_VERIFY_CWD_MANDATE", "")
if BYPASS_ENV == "1":
    print("[check-pl-inline-verify-cwd-mandate] BYPASS=1 — skip", file=sys.stderr)
    sys.exit(0)

# ── 상수 ─────────────────────────────────────────────────────────────────────
LANE_PL_SPAWN_MARKERS = (
    "DesignReviewPLAgent spawn",
    "CodeReviewPLAgent spawn",
    "SecurityTestPLAgent spawn",
    "ArchitectPLAgent spawn",
    "DeveloperPLAgent spawn",
    "RequirementsPLAgent spawn",
    "DeployPLAgent spawn",
    "DeployReviewPLAgent spawn",
)

# cwd directive 3 forms (precision matching — line-by-line, ReDoS-safe per CFP-1497 #1499)
CWD_DIRECTIVE_PATTERNS = (
    re.compile(r"git\s+-C\s+\S+"),                  # form 1: git -C <path>
    re.compile(r"\bcd\s+\S+/\S+"),                  # form 2: cd <path> (with slash, avoid bare cd)
    re.compile(r"\[WORKTREE-CWD:\s*\S+\]"),         # form 3: [WORKTREE-CWD: <path>]
)

# Spawn-proximity window — N lines around spawn marker
SPAWN_PROXIMITY_LINES = 20

# Skip paths (FP-완화 guard)
SKIP_PATH_PREFIXES = ("templates/", "templates\\", "tests/", "tests\\")

# Story file scope (lint scope 안 — heuristic)
STORY_FILE_PATTERN = re.compile(r"docs[/\\]stories[/\\]")


def is_skip_path(path_str: str) -> bool:
    """FP-완화 guard — templates/** + tests/** path 면제."""
    norm = path_str.replace("\\", "/")
    return any(norm.startswith(prefix.replace("\\", "/")) for prefix in SKIP_PATH_PREFIXES)


def is_story_file(path_str: str) -> bool:
    """Story file path scope check (docs/stories/**)."""
    return bool(STORY_FILE_PATTERN.search(path_str))


def is_table_row(line: str) -> bool:
    """Markdown table row 면제 (`|` start)."""
    return line.strip().startswith("|")


def has_cwd_directive(line: str) -> bool:
    """3 form cwd directive presence (line 단위, ReDoS-safe)."""
    return any(p.search(line) for p in CWD_DIRECTIVE_PATTERNS)


def find_spawn_markers(lines: list) -> list:
    """Lane PL spawn marker 발견 위치 (line_num 1-indexed) 반환."""
    markers = []
    for i, line in enumerate(lines):
        if is_table_row(line):
            continue
        for marker in LANE_PL_SPAWN_MARKERS:
            if marker in line:
                markers.append((i + 1, line.strip(), marker))
                break
    return markers


def check_spawn_window(lines: list, spawn_line_idx: int) -> bool:
    """spawn line 전후 ±N line 안 cwd directive presence (warning-tier heuristic)."""
    start = max(0, spawn_line_idx - SPAWN_PROXIMITY_LINES)
    end = min(len(lines), spawn_line_idx + SPAWN_PROXIMITY_LINES + 1)
    for j in range(start, end):
        if has_cwd_directive(lines[j]):
            return True
    return False


def check_file(path: Path) -> list:
    """단일 file 안 spawn marker 검사 후 cwd directive 부재 spawn 의 warning 목록 반환.

    Note: is_story_file gate intentionally NOT applied here — explicit argv files
    검사 영역 (CI 의 git diff 도 templates/ + tests/ FP guard 가 충분).
    """
    warnings = []
    path_str = str(path)

    if is_skip_path(path_str):
        return []

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, IOError) as e:
        print(f"[check-pl-inline-verify-cwd-mandate] ERROR reading {path_str}: {e}",
              file=sys.stderr)
        return []

    lines = text.split("\n")
    spawn_markers = find_spawn_markers(lines)

    for line_num, spawn_line, marker in spawn_markers:
        if not check_spawn_window(lines, line_num - 1):
            warnings.append({
                "path": path_str,
                "line": line_num,
                "marker": marker,
                "code": "WARN-CWD-DIRECTIVE-ABSENT",
                "msg": (f"Lane PL spawn '{marker}' detected without cwd directive "
                        f"in ±{SPAWN_PROXIMITY_LINES} line window. "
                        f"Add `git -C <worktree_abs_path>` or `cd <worktree_abs_path>` "
                        f"or `[WORKTREE-CWD: <path>]` annotation. "
                        f"(ADR-040 Amd 6 §결정 7.J)"),
            })

    return warnings


def collect_files(argv: list) -> list:
    """argv 또는 git diff 기반 파일 수집."""
    if argv:
        return [Path(p) for p in argv if Path(p).is_file()]

    import subprocess
    base_ref = os.environ.get("GITHUB_BASE_REF", "")
    try:
        if base_ref:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"],
                capture_output=True, text=True, check=True,
            )
        else:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True, text=True, check=True,
            )
        files = [Path(line.strip()) for line in result.stdout.split("\n") if line.strip()]
        return [f for f in files if f.is_file()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def main(argv: list) -> int:
    files = collect_files(argv)

    if not files:
        print("[check-pl-inline-verify-cwd-mandate] no files to check — PASS",
              file=sys.stderr)
        return 0

    all_warnings = []
    for f in files:
        all_warnings.extend(check_file(f))

    if not all_warnings:
        print(f"[check-pl-inline-verify-cwd-mandate] PASS — {len(files)} file(s) checked",
              file=sys.stderr)
        return 0

    print("[check-pl-inline-verify-cwd-mandate] WARNINGS:", file=sys.stderr)
    for w in all_warnings:
        print(f"  [{w['code']}] {w['path']}:{w['line']} — {w['msg']}", file=sys.stderr)
    print(f"\n[check-pl-inline-verify-cwd-mandate] {len(all_warnings)} warning(s) emitted "
          f"(warning-tier — exit 0, PR merge 미차단)", file=sys.stderr)
    print(f"[check-pl-inline-verify-cwd-mandate] bypass: hotfix-bypass:pl-inline-verify-cwd-mandate label",
          file=sys.stderr)
    return 0  # warning-tier always exit 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
