#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-2829 S2 (leg A) — forward↔backward 순환차단 순수 predicate (AC-7, §3.8 / §7.R R-4 / §7.R2 IO-9).
"""forward↔backward re-sync loop 차단 판정 (순수 predicate — unit-testable).

판정 우선순위 (Change Plan §3.8 / IO-9):
  - **PRIMARY = anchor-equality skip-if-equal** (authoritative / truth 결정):
      forward push 전 live anchor A(git-source sha256) == 현 git source hash → skip(no-op).
      marker-sentinel(HEAD~1..HEAD 단일 window — squash/multi-commit 시 붕괴)보다 근원적.
  - **SECONDARY/fast-path = sentinel marker** (저비용 short-circuit):
      machine-authored backward substrate commit 을 commit trailer 로 self 제외.
  → 둘 중 하나라도 equal/self 판정 시 forward-sync skip → re-sync loop 결정론 차단.

dedup key = (page_id, version_number) — ordering invariant, 중복 PR 제거(AC-14).

★ 배선 경계 (interface-freeze / DevPL→ArchitectPL 회부 中):
  본 모듈은 순수 predicate 만 노출한다. forward(confluence_forward_sync.py cmd_sync) 진입부
  배선은 **하지 않는다** — forward_sync.py 는 AC-3/L605 interface-freeze(0줄 변경) 대상이라
  Change Plan §3.8/R-4 의 "cmd_sync 1줄 가드 삽입"과 모순되기 때문이다. SUBSTRATE_MARKER 는
  backward-writer stamp ↔ forward filter 양쪽이 참조하는 단일 SSOT 상수로만 제공한다.
"""

# ── SSOT 상수 (backward-writer stamp ↔ forward filter 양쪽 참조 — 분산 하드코딩 금지) ──
SUBSTRATE_MARKER = "[confluence-backward-substrate]"


def commit_message_is_substrate(message: str) -> bool:
    """commit message 에 SUBSTRATE_MARKER 가 있으면 True (machine-authored backward substrate).

    순수·unit-testable. backward-writer 는 이 marker 를 commit trailer 로 삽입한다.
    marker 부재/None → False.
    """
    if not message:
        return False
    return SUBSTRATE_MARKER in message


def is_machine_authored_substrate(commit_ref: str, repo: str = None) -> bool:
    """commit_ref 의 commit message 를 취득해 substrate marker 판정 (secondary/fast-path).

    git -C <repo> log -1 --format=%B <commit_ref> 로 메시지 취득 후 commit_message_is_substrate 위임.
    repo=None 이면 cwd. git 실패/부재 → False (fail-safe: 판정 불가 시 sentinel skip 안 함 →
    PRIMARY anchor-equality 로 fall-through, authoritative 판정에 위임).
    """
    import subprocess
    cmd = ["git"]
    if repo:
        cmd += ["-C", repo]
    cmd += ["log", "-1", "--format=%B", commit_ref]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except (OSError, ValueError):
        return False
    if result.returncode != 0:
        return False
    return commit_message_is_substrate(result.stdout)


def anchor_equality_skip(live_anchor_a: str, current_git_source_hash: str) -> bool:
    """PRIMARY 순환차단 (IO-9): 두 anchor A 값이 equal → True(skip no-op).

    forward push 전 live anchor A(Confluence 저장 git-source sha256) 가 현 git source hash 와
    같으면 이미 동기 상태 → forward push skip. 값 부재(빈 문자열/None)면 False
    (equality 확인 불가 → skip 안 함, 안전측 = sync 진행).
    """
    if not live_anchor_a or not current_git_source_hash:
        return False
    return live_anchor_a == current_git_source_hash


def dedup_key(page_id, version_number):
    """중복 PR 제거 dedup key = (page_id, version_number) 결정론 반환 (ordering invariant, AC-14)."""
    return (page_id, version_number)
