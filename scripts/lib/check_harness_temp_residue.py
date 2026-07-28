#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# check_harness_temp_residue.py — harness Temp 관측기 (AC-6 1단계, observe-only)
#
# Carrier: CFP-2822 Phase 2 (구현) — 세션 잔재 발견 스캐너 (ADR-169 §결정 6, ④ Temp 관측기)
# 설계 SSOT: change-plan cfp-2822 §3.2④ / §3.5 / §7.2 T-TEMP / §8.10 dark-path (1) /
#           §11.6 IDEM-6 / Story AC-6 / INV-9.
#
# ── 1단계 (즉시 in-scope) = 관측·보고 + git-aware 판정만 ─────────────────────────────
#   Temp 하위 총량·나이·git-여부 관측 + `git -C <temp> rev-parse --git-common-dir` 로
#   소유 repo 역추적 → unpushed/stash/locked → fail-safe 보존 사유 "temp-git-worktree".
#   ★ INV-9 = 삭제 syscall 0 (본 1단계). git-aware 로그 존재.
#
# ── 2단계 (조건부 삭제) = default DISABLED (TEMP_GC_DELETE_ENABLED default-off) ──────
#   §8.10 dark-path (1): flag off 로 삭제 경로 도달 불가(status=infeasible 정당 landing).
#   삭제 경로 코드는 두되(현세션 self-scratchpad 배제 + git-aware preserve), flag ON 은
#   §3.2④ 4-전제 충족 후에만. landing ≠ done — gated 상태 정직 추적.
#
# Temp 경로 = tempfile.gettempdir()/claude — cross-platform (Windows %TEMP%\claude /
#   POSIX $TMPDIR|/tmp 자동 해소, 하드코딩 금지). [firsthand: gettempdir()/claude 실존 확인]

from __future__ import annotations

import os
import sys
import tempfile

_SELF_DIR = os.path.dirname(os.path.abspath(__file__))
if _SELF_DIR not in sys.path:
    sys.path.insert(0, _SELF_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import check_orphan_worktree_classify as base  # noqa: E402

SCRIPT_NAME = "harness-temp"

# 2단계 삭제 gate (default-off — §3.6 별도 축, bypass 아님). ON = 4-전제 충족 후만.
TEMP_GC_DELETE_ENABLED = os.environ.get("TEMP_GC_DELETE_ENABLED", "") == "1"

# 관측 walk bound (Perf S1 DoS-bound — 8GB+ Temp 전량 walk 회귀 방어).
_MAX_WALK_ENTRIES = 200_000


def harness_temp_root():
    """harness Temp 세션 스크래치 루트 (cross-platform). 부재 시 경로만 반환(호출자 존재확인)."""
    return os.path.join(tempfile.gettempdir(), "claude")


def _self_scratchpad_markers():
    """현세션 self-scratchpad 배제 신호 (T-TEMP-1 — 활성 세션 삭제 금지).
    CLAUDE_SESSION_ID 로 세션 dir 식별 (detached child 는 유실 가능 → 부재 시 빈 set)."""
    sid = os.environ.get("CLAUDE_SESSION_ID", "").strip()
    return {sid} if sid else set()


def _dir_size_and_count(path):
    """디렉터리 총 바이트 + 파일 수 (bounded walk). (bytes, files, truncated)."""
    total = 0
    files = 0
    truncated = False
    stack = [path]
    while stack:
        cur = stack.pop()
        try:
            with os.scandir(cur) as it:
                for entry in it:
                    if files >= _MAX_WALK_ENTRIES:
                        truncated = True
                        return (total, files, truncated)
                    try:
                        if entry.is_symlink():
                            continue  # 링크 크기 미집계 (loop/오염 방어)
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                        elif entry.is_file(follow_symlinks=False):
                            total += entry.stat(follow_symlinks=False).st_size
                            files += 1
                    except OSError:
                        continue
        except OSError:
            continue
    return (total, files, truncated)


def git_common_dir(path):
    """`git -C <path> rev-parse --git-common-dir` → 소유 git-common-dir (역추적). 실패 → None.

    T-DEL-4: 위조 gitdir 방어는 실재+역등록 확인(호출자). 여기선 rev-parse 결과만."""
    if not path or not os.path.isdir(path):
        return None
    cp = base._git(["-C", path, "rev-parse", "--git-common-dir"], cwd=path)
    if cp is None or cp.returncode != 0:
        return None
    out = (cp.stdout or "").strip()
    return out or None


def owning_toplevel(path):
    """temp git 항목의 소유 worktree top-level. 실패 → None."""
    cp = base._git(["-C", path, "rev-parse", "--show-toplevel"], cwd=path)
    if cp is None or cp.returncode != 0:
        return None
    out = (cp.stdout or "").strip()
    return out or None


def classify_temp_entry(entry_path, now=None):
    """Temp 세션 항목 git-aware 관측 판정 (삭제 0 — 관측만).

    반환 dict: {path, size, files, age, is_git, owning, preserve(bool), reason}.
      · is_git + (dirty/unpushed/stash) → preserve "temp-git-worktree" (fail-safe).
      · is_git + 판정불능 → preserve "network-inconclusive".
      · non-git → preserve=False(관측상 삭제 후보 신호) but 1단계 삭제 0."""
    size, files, truncated = _dir_size_and_count(entry_path)
    age = base.age_seconds(entry_path, now=now)
    gcd = git_common_dir(entry_path)
    is_git = gcd is not None
    reason = None
    preserve = False
    owning = None
    if is_git:
        owning = owning_toplevel(entry_path) or entry_path
        dirty = base.is_dirty(owning)
        up_count, up_inconc = base.unpushed_count(owning)
        st_count, st_inconc = base.stash_count(owning)
        if up_inconc or st_inconc:
            preserve, reason = True, "network-inconclusive"
        elif dirty or up_count > 0 or st_count > 0:
            preserve, reason = True, "temp-git-worktree"
        else:
            # git 항목이나 상태 전부 음성 → 여전히 1단계 삭제 0, 2단계도 git-aware preserve 기본
            preserve, reason = True, "temp-git-worktree"
    return {
        "path": entry_path,
        "size": size,
        "files": files,
        "truncated": truncated,
        "age": age,
        "is_git": is_git,
        "owning": owning,
        "preserve": preserve,
        "reason": reason,
    }


def observe_temp(temp_root=None, now=None):
    """Temp 하위 관측 (INV-9 — 삭제 syscall 0). 세션 dir 단위 집계 + git-aware.

    반환: {root, exists, total_size, total_files, entry_count, oldest_age, entries(list)}."""
    root = temp_root or harness_temp_root()
    if not os.path.isdir(root):
        return {"root": root, "exists": False, "total_size": 0, "total_files": 0,
                "entry_count": 0, "oldest_age": 0, "entries": []}
    n = base.now_epoch() if now is None else now
    self_markers = _self_scratchpad_markers()
    entries = []
    total_size = total_files = 0
    oldest = 0
    try:
        names = sorted(os.listdir(root))
    except OSError:
        names = []
    for name in names:
        full = os.path.join(root, name)
        if not os.path.isdir(full):
            continue
        info = classify_temp_entry(full, now=n)
        info["is_self_session"] = any(m and m in name for m in self_markers)
        total_size += info["size"]
        total_files += info["files"]
        oldest = max(oldest, info["age"] or 0)
        entries.append(info)
    return {
        "root": root,
        "exists": True,
        "total_size": total_size,
        "total_files": total_files,
        "entry_count": len(entries),
        "oldest_age": oldest,
        "entries": entries,
    }


def emit_observation(obs, prefix=SCRIPT_NAME):
    """관측 보고 (advisory stderr). git-aware 로그 존재(INV-9 검증축). 삭제 0."""
    if not obs["exists"]:
        print("[%s] Temp 루트 부재 — 관측 대상 0: %s"
              % (prefix, base.sanitize(obs["root"])), file=sys.stderr)
        return
    mb = obs["total_size"] / (1024 * 1024)
    print("[%s] OBSERVE (INV-9 삭제 0): root=%s entries=%d size=%.1fMB oldest=%dd"
          % (prefix, base.sanitize(obs["root"]), obs["entry_count"], mb,
             (obs["oldest_age"] or 0) // 86400), file=sys.stderr)
    for e in obs["entries"]:
        git_tag = "git" if e["is_git"] else "loose"
        preserve_tag = (" PRESERVE(%s)" % base.sanitize(e["reason"])) if e["preserve"] else ""
        self_tag = " SELF-SESSION" if e.get("is_self_session") else ""
        age_d = (e["age"] or 0) // 86400
        print("[%s]   [%s]%s%s age=%dd files=%d %s"
              % (prefix, git_tag, preserve_tag, self_tag, age_d, e["files"],
                 base.sanitize(e["path"])), file=sys.stderr)


def _stage2_delete(obs, allowed_roots):
    """2단계 조건부 삭제 (dark-path — TEMP_GC_DELETE_ENABLED gate 뒤, default 도달 불가).

    §3.2④ 전제: 현세션 self-scratchpad 배제 + git-aware preserve + age 임계.
    실 활성화(flag ON) = §3.2④ 4-전제 충족 후만. flag off → 본 함수 호출 자체 미도달."""
    removed = 0
    threshold = base.STALE_DAYS * 86400
    for e in obs["entries"]:
        if e.get("is_self_session"):
            continue  # T-TEMP-1 현세션 배제
        if e["preserve"]:
            continue  # git-aware fail-safe 보존
        if (e["age"] or 0) <= threshold:
            continue  # 나이 미도달 (mtime AND, T-DEL-3)
        ok, _note = base.safe_remove(e["path"], allowed_roots)
        if ok:
            removed += 1
    return removed


def main(argv=None):
    """standalone 진입 (축 격리). 1단계 관측·보고. always exit 0. INV-9 삭제 syscall 0."""
    import argparse
    ap = argparse.ArgumentParser(description="harness Temp 관측기 (observe-only, INV-9)")
    ap.add_argument("--temp-root", default=None, help="Temp 루트 override (기본 gettempdir/claude)")
    args = ap.parse_args(argv)

    obs = observe_temp(temp_root=args.temp_root)
    emit_observation(obs)

    # 2단계 삭제 gate — default-off (§8.10 dark-path (1) status=infeasible landing).
    if TEMP_GC_DELETE_ENABLED:
        # dark-path: allowed_roots = Temp 루트 자신만 (봉쇄). 실 활성화는 4-전제 충족 후.
        n_removed = _stage2_delete(obs, allowed_roots=[obs["root"]])
        print("[%s] STAGE2-DELETE (enabled): removed=%d" % (SCRIPT_NAME, n_removed),
              file=sys.stderr)
    print("[%s] DONE: observed=%d preserved=%d (INV-9 stage1 delete=0)"
          % (SCRIPT_NAME, obs["entry_count"],
             sum(1 for e in obs["entries"] if e["preserve"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
