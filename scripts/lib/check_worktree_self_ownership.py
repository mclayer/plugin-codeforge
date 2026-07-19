#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_worktree_self_ownership.py
CFP-2761 §5.2 / ADR-073 Amendment 3 §결정1-D — worktree self-ownership 3-tuple verify (warning tier).
HOOK-ONLY (workflow:null) — CI 워크플로 게이트 아님, hook 경유 advisory 검증.

path-based 3-tuple 소유 검증 (ADR-073 Amendment 3 §결정1-D). LIVE mode(실 git 조회) 와
FIXTURE-INJECTION mode(deterministic self-test 용 파일 주입) 를 모두 지원한다.

3-tuple (§결정1-D):
  (a) toplevel(git rev-parse --show-toplevel) ↔ worktree-list(git worktree list --porcelain) 의
      worktree path 가 normalize(forward-slash + lowercase drive letter) 후 MATCH.
  (b) HEAD/branch lineage ↔ reflog membership — --branch 가 reflog 내용에 등장.
  (c) worktree-list 가 --branch 포함 AND reflog 가 --branch 포함 → 2-source AND.
      reflog 파일 empty/missing(90d GC) → (a)+(c) 2-source AND 로 fallback (§결정1-D fallback;
      (b) drop, (c) 는 worktree-list membership 단독으로 degrade).

  §결정1-E: subagent 가 parallel_session_conflict verdict 를 내면 Orchestrator re-verify 필요 —
    --subagent-verdict parallel_session_conflict flag 전달 시 별도 warning 방출.

mode 판정:
  fixture args(--toplevel / --worktree-list-file / --reflog-file / --branch) 중 1+ 존재 = FIXTURE.
    fixture 필수 = toplevel + worktree-list-file + branch (reflog-file 는 optional, 부재 = GC fallback).
  fixture args 전무 = LIVE — 실 git -C <repo-root> rev-parse/worktree list/reflog 조회.

DoS guard (§8.6, ADR-082 Amendment 38 resource-safety): worktree-list/reflog 파일 bounded read
  (per-line cap + line-count cap), anchored bounded regex, O(n) 파싱. bounded degradation.

CLI 계약 (ADR-061 house style — 고정, hook + self-test 소비):
  bash scripts/check-worktree-self-ownership.sh [--repo-root DIR]
       [--toplevel PATH --worktree-list-file FILE --reflog-file FILE --branch NAME]
       [--subagent-verdict VERDICT]

Exit codes (ADR-060 §결정5 tri-tier — warning tier, advisory NEVER blocks):
  0 = clean (mismatch 0) OR mismatch warning 방출.
      finding 은 STDOUT 에 `::warning::worktree-self-ownership-verify: <detail>` 로 surface.
  2 = usage/argparse 오류 OR 불완전 fixture (bad args).
  3 = 미사용 (본 검사는 항상 현 worktree 대상 — zero-target 개념 없음).
  1 = strict-tier 미사용 (warning tier).

ADR refs: CFP-2761 §5.2 (carrier) / ADR-073 Amendment 3 §결정1-D/1-E (worktree self-ownership
  3-tuple) / ADR-060 §결정5 (warning tri-tier) / ADR-082 Amendment 38 §8.6 (resource-safety) /
  ADR-061 §결정1 (Python SSOT + thin wrapper).
"""

import argparse
import os
import re
import subprocess
import sys

# Windows cp949 stdout/stderr 인코딩 차단 — UTF-8 강제 (ADR-061 portability 답습).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

CHECK_NAME = "worktree-self-ownership-verify"

# bounded read 상수 (§8.6).
MAX_READ_BYTES = 4 * 1024 * 1024  # worktree-list/reflog 파일 상한 4MB (bounded degradation).

# git worktree list --porcelain 파서.
_WT_PATH_RE = re.compile(r"^worktree\s{1,8}(.{1,4096})$")
_WT_BRANCH_RE = re.compile(r"^branch\s{1,8}refs/heads/(.{1,512})$")
_DRIVE_RE = re.compile(r"^([A-Za-z]):")


def _normalize_path(p):
    """forward-slash + lowercase drive letter + trailing-slash strip (§결정1-D normalize)."""
    s = str(p).strip().replace("\\", "/")
    m = _DRIVE_RE.match(s)
    if m:
        s = s[0].lower() + s[1:]
    return s.rstrip("/")


def _read_text_bounded(path):
    """파일 bounded read → str. 부재/실패 → None."""
    if not path or not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(MAX_READ_BYTES)
    except OSError:
        return None


def _parse_worktree_list(content):
    """porcelain 내용 → (normalized_paths set, branch_names set)."""
    paths = set()
    branches = set()
    if not content:
        return paths, branches
    for raw in content.splitlines():
        line = raw.rstrip("\r")
        mp = _WT_PATH_RE.match(line)
        if mp:
            paths.add(_normalize_path(mp.group(1)))
            continue
        mb = _WT_BRANCH_RE.match(line)
        if mb:
            branches.add(mb.group(1).strip())
    return paths, branches


# ─────────────────────── LIVE mode git 조회 ──────────────────────────────────────

def _git(repo_root, args):
    """git 서브프로세스 실행 → stdout(str) 또는 None (실패)."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_root] + args,
            capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout


# ─────────────────────── 3-tuple 판정 ────────────────────────────────────────────

def _evaluate(toplevel, wt_content, reflog_content, branch):
    """3-tuple 판정 → findings=[detail]. reflog empty/missing 시 (a)+(c) fallback."""
    findings = []
    norm_top = _normalize_path(toplevel) if toplevel else ""
    wt_paths, wt_branches = _parse_worktree_list(wt_content)

    tuple_a_ok = norm_top != "" and norm_top in wt_paths
    if not tuple_a_ok:
        findings.append(
            "tuple a mismatch: toplevel=%s not in worktree-list paths=%s"
            % (norm_top, sorted(wt_paths))
        )

    wl_has_branch = bool(branch) and (branch in wt_branches or (wt_content and branch in wt_content))
    reflog_available = bool(reflog_content) and reflog_content.strip() != ""

    if reflog_available:
        reflog_has_branch = bool(branch) and branch in reflog_content
        if not reflog_has_branch:
            findings.append(
                "tuple b mismatch: branch=%s absent from reflog lineage" % branch
            )
        tuple_c_ok = wl_has_branch and reflog_has_branch
        if not tuple_c_ok:
            findings.append(
                "tuple c mismatch: worktree-list∧reflog AND failed (wl=%s reflog=%s branch=%s)"
                % (wl_has_branch, reflog_has_branch, branch)
            )
    else:
        # reflog empty/missing (90d GC) → (a)+(c) 2-source AND fallback; (c)=worktree-list membership.
        if not wl_has_branch:
            findings.append(
                "tuple c mismatch: worktree-list membership failed (reflog GC fallback, "
                "wl=%s branch=%s)" % (wl_has_branch, branch)
            )
    return findings


def main(argv):
    parser = argparse.ArgumentParser(
        prog="check_worktree_self_ownership.py",
        description="worktree self-ownership 3-tuple verify (HOOK-ONLY, warning tier).",
    )
    parser.add_argument("--repo-root", default=None, help="LIVE mode git 조회 루트 (기본 = cwd/자동 탐지).")
    parser.add_argument("--toplevel", default=None, help="FIXTURE: 시뮬레이트 git rev-parse --show-toplevel.")
    parser.add_argument("--worktree-list-file", default=None, help="FIXTURE: git worktree list --porcelain 파일.")
    parser.add_argument("--reflog-file", default=None, help="FIXTURE: git reflog 내용 파일 (부재=90d GC fallback).")
    parser.add_argument("--branch", default=None, help="FIXTURE: HEAD 브랜치명.")
    parser.add_argument("--subagent-verdict", default=None, help="subagent verdict (parallel_session_conflict 시 §결정1-E warning).")
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2

    fixture_mode = any(
        v is not None
        for v in (args.toplevel, args.worktree_list_file, args.reflog_file, args.branch)
    )

    warnings = []

    if fixture_mode:
        # fixture 필수 = toplevel + worktree-list-file + branch (reflog-file optional).
        if not args.toplevel or not args.worktree_list_file or not args.branch:
            print(
                "::error::%s: 불완전 fixture — --toplevel/--worktree-list-file/--branch 필수 "
                "(reflog-file optional). bad args." % CHECK_NAME,
                file=sys.stderr,
            )
            return 2
        wt_content = _read_text_bounded(args.worktree_list_file)
        if wt_content is None:
            print(
                "::error::%s: --worktree-list-file 읽기 불가: %s (bad args)"
                % (CHECK_NAME, args.worktree_list_file),
                file=sys.stderr,
            )
            return 2
        reflog_content = _read_text_bounded(args.reflog_file) if args.reflog_file else None
        warnings = _evaluate(args.toplevel, wt_content, reflog_content, args.branch)
    else:
        # LIVE mode — 실 git 조회.
        repo_root = args.repo_root
        if repo_root is None:
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        repo_root = os.path.abspath(repo_root)
        toplevel = _git(repo_root, ["rev-parse", "--show-toplevel"])
        toplevel = toplevel.strip() if toplevel else None
        wt_content = _git(repo_root, ["worktree", "list", "--porcelain"])
        reflog_content = _git(repo_root, ["reflog", "-n", "200"])
        branch = _git(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"])
        branch = branch.strip() if branch else None
        if toplevel is None or wt_content is None or branch is None:
            # git 조회 실패 = 비-repo/git 부재 = advisory degrade (non-blocking, exit 0).
            print(
                "%s: git 조회 실패 (비-repo 또는 git 부재) — LIVE advisory degrade, "
                "3-tuple 검증 skip (honest no-op)" % CHECK_NAME
            )
            return _emit_subagent_and_return(args, warnings)
        warnings = _evaluate(toplevel, wt_content, reflog_content, branch)

    return _emit_subagent_and_return(args, warnings)


def _emit_subagent_and_return(args, warnings):
    """tuple warning + §결정1-E subagent-verdict warning 방출 후 exit 0."""
    for detail in warnings:
        print("::warning::%s: %s" % (CHECK_NAME, detail))

    if args.subagent_verdict == "parallel_session_conflict":
        print(
            "::warning::%s: subagent parallel_session_conflict — re-verify required" % CHECK_NAME
        )

    if not warnings and args.subagent_verdict != "parallel_session_conflict":
        print("%s: ownership verified — 3-tuple mismatch 0 (advisory)" % CHECK_NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
