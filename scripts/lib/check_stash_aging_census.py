#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# check_stash_aging_census.py — multi-repo stash 집계 + aging (AC-14)
#
# Carrier: CFP-2822 Phase 2 (구현) — 세션 잔재 발견 스캐너 (ADR-169 §결정 7)
# 설계 SSOT: change-plan cfp-2822 §3.5 flat sibling / §7.4.1 aging / Story AC-14.
#
# 책임: repo 별 stash 건수 + 최고령 age 집계 → 가시화. age>임계 재알림 후보 방출.
# 비책임(Non-goal 확정): **자동 삭제 실행 0**. git stash 는 의도적 사용자 데이터(무만료,
#   reflog.c expire=0) — 자동삭제 = 보존 원칙 역행(ADR-169 §결정 7). 가시화만.
#
# INV-3: 집계 리포트 = 건수 + 나이 동반 (사유없는 보존 아님 — 사용자 데이터 명시).

from __future__ import annotations

import os
import sys

# self-dir path 보정 + base substrate import (사이클 없음 — File 2 는 사이블링 미import).
_SELF_DIR = os.path.dirname(os.path.abspath(__file__))
if _SELF_DIR not in sys.path:
    sys.path.insert(0, _SELF_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import check_orphan_worktree_classify as base  # noqa: E402

SCRIPT_NAME = "stash-census"

# aging 임계 (기존 STALE_DAYS 관행 상속 — 신규 env 아님).
STASH_AGE_ALERT_DAYS = base.STALE_DAYS


def stash_entries(repo_path):
    """repo 의 stash 항목별 생성 epoch 리스트. git 실패 → (None inconclusive).

    `git -C <repo> stash list --format=%ct` — %ct = committer date(Unix epoch).
    반환: (epochs:list[int]|None). None = git 실패(판정불능)."""
    if not repo_path or not os.path.isdir(repo_path):
        return None
    if not base.has_git_dir(repo_path):
        return None
    cp = base._git(["-C", repo_path, "stash", "list", "--format=%ct"], cwd=repo_path)
    if cp is None or cp.returncode != 0:
        return None
    epochs = []
    for line in (cp.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            epochs.append(int(line))
        except ValueError:
            continue
    return epochs


def repo_stash_census(repo_path, now=None):
    """단일 repo stash census — {path, count, oldest_age, inconclusive}."""
    n = base.now_epoch() if now is None else now
    epochs = stash_entries(repo_path)
    if epochs is None:
        return {"path": repo_path, "count": 0, "oldest_age": None, "inconclusive": True}
    if not epochs:
        return {"path": repo_path, "count": 0, "oldest_age": 0, "inconclusive": False}
    # 최고령 = 가장 오래된 stash (min epoch) 기준, 미래 mtime clamp
    oldest_age = max(0, n - min(epochs))
    return {"path": repo_path, "count": len(epochs), "oldest_age": oldest_age,
            "inconclusive": False}


def stash_census(repo_paths, now=None):
    """multi-repo stash 집계. 삭제 0 (Non-goal).

    반환: {total_stashes, repos_with_stash, oldest_age, aging(list), per_repo(list)}.
      aging = age>임계 인 repo census (재알림 후보 — 실 dedup/backoff 는 orchestrator report)."""
    n = base.now_epoch() if now is None else now
    per_repo = []
    seen = set()
    for rp in repo_paths:
        key = base._norm(rp)
        if key in seen:
            continue
        seen.add(key)
        c = repo_stash_census(rp, now=n)
        if c["count"] > 0 or c["inconclusive"]:
            per_repo.append(c)
    total = sum(c["count"] for c in per_repo)
    with_stash = sum(1 for c in per_repo if c["count"] > 0)
    ages = [c["oldest_age"] for c in per_repo if c["oldest_age"]]
    oldest = max(ages) if ages else 0
    threshold = STASH_AGE_ALERT_DAYS * 86400
    aging = [c for c in per_repo if (c["oldest_age"] or 0) > threshold]
    return {
        "total_stashes": total,
        "repos_with_stash": with_stash,
        "oldest_age": oldest,
        "aging": aging,
        "per_repo": per_repo,
    }


def emit_census(census, prefix=SCRIPT_NAME):
    """가시화 출력 (advisory, stderr). INV-3 — 건수 + 나이. 삭제 0."""
    for c in census["per_repo"]:
        if c["inconclusive"]:
            print("[%s] INCONCLUSIVE (git 판정불능): %s"
                  % (prefix, base.sanitize(c["path"])), file=sys.stderr)
            continue
        age_d = (c["oldest_age"] or 0) // 86400
        aging_tag = " AGING" if (c["oldest_age"] or 0) > STASH_AGE_ALERT_DAYS * 86400 else ""
        print("[%s] STASH%s: count=%d oldest=%dd repo=%s"
              % (prefix, aging_tag, c["count"], age_d, base.sanitize(c["path"])),
              file=sys.stderr)


def discover_repos(roots):
    """스캔 root 하위 git-bearing dir 열거 (multi-repo census 대상). root 자신도 포함."""
    repos = []
    seen = set()

    def _add(p):
        if p and os.path.isdir(p) and base.has_git_dir(p):
            k = base._norm(p)
            if k not in seen:
                seen.add(k)
                repos.append(p)

    for root in roots:
        root = os.path.expanduser(root)
        _add(root)
        try:
            for name in sorted(os.listdir(root)):
                _add(os.path.join(root, name))
        except OSError:
            continue
    return repos


def main(argv=None):
    """standalone 진입 (축 격리). --root 다회 → multi-repo census. always exit 0."""
    import argparse
    ap = argparse.ArgumentParser(description="multi-repo stash census + aging (가시화, 삭제 0)")
    ap.add_argument("--root", action="append", default=[], help="스캔 root (다회 지정 가능)")
    args = ap.parse_args(argv)

    roots = args.root or [os.getcwd()]
    repos = discover_repos(roots)
    census = stash_census(repos)
    emit_census(census)
    print("[%s] DONE: stashes=%d repos=%d oldest=%dd"
          % (SCRIPT_NAME, census["total_stashes"], census["repos_with_stash"],
             (census["oldest_age"] or 0) // 86400))
    return 0


if __name__ == "__main__":
    sys.exit(main())
