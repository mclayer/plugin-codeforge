#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_force_push_base_advance.py
CFP-2490 / ADR-135 (Epic CFP-2481 E2) — force-push pre-flight HEAD-pin 가드 L2 CI
사후 detect Python SSOT lint engine (warning tier, exit 3-tier).

own-branch push-time race-guard 의 **사후 detect** layer (L2). force-push 는 CI 로
*차단* 불가능 (force-push 발생 후 origin 이 이미 변경됨) — 본 엔진은 PR head 가 base
보다 BEHIND(base-advance) 인지 / base 와 diverged 인지를 git ancestry 로 실측해 warning
emit 한다 (ADR-135 §결정 2 L2, §결정 5 warning tier 고정). 진짜 pre-flight 차단(L1)은
opt-in local pre-push hook (templates/.claude/hooks/pre-push.sh.sample) 만 가능.

검사 (exit 3-tier):
  1. base ref 결정 (CI: BASE_REF/GITHUB_BASE_REF env → origin/<base>, fallback main).
     head ref 결정 (HEAD_SHA env → 아니면 git HEAD).
  2. base-advance detect — `git rev-list --count <head>..<base>` (BEHIND>0 = base 진행).
     `--force-with-lease` 가 못 잡는 base(main) advance 를 직접 cover.
  3. divergence detect — `git merge-base --is-ancestor <base> <head>` false = diverged
     (head 가 base 를 포함하지 않음 = rebase 필요 = force-push 시 ancestry corruption 위험).

graceful-degradation (2-tier 엄격 분리 — change-plan §7.4 rate-limit / §7.5):
  data-absence(A) = fail-open(exit 0, honest ::notice:: — silent default 아님):
    base ref 미해결(origin/<base> 부재 / shallow clone fetch 실패 / single-commit) =
    비교 비대상 = 정책 공백과 동형 fail-open (false-PASS 아닌 honest no-op).
  setup-error(B) = fail-closed(exit 2):
    git 미설치 / git 명령 실행 실패(repo 아님) = 검증 로직 못 돎.

offline-first (gh 불요 — 입력 전부 git ancestry, actions/checkout fetch-depth:0 전제).
ReDoS-safe (regex 미사용 — git plumbing + 정수 비교). read-only (verifier — write 0).

Usage:
  python3 check_force_push_base_advance.py [--base <ref>] [--head <ref>]
    --base 미지정: env BASE_REF → GITHUB_BASE_REF → "main" 순서로 결정 (origin/<base> 우선).
    --head 미지정: env HEAD_SHA → "HEAD".

Exit codes (ADR-060 §결정 5 3-tier — warning tier):
  0 = PASS (base-advance/divergence 0) OR data-absence honest no-op (fail-open)
  1 = base-advance 또는 divergence 검출 1+ (workflow continue-on-error 로 비차단, advisory warning)
  2 = SETUP error (git 미설치 / repo 아님 / CLI 인자 형식 오류) — fail-closed

ADR refs: ADR-135 §결정 1/2/5 (carrier — own-branch push-time pre-flight + 2-layer + warning tier) /
  ADR-060 §결정 5/6/19 (warning-tier evidence framework + 승격 evidence-gate) /
  ADR-061 §결정 1 (Python SSOT + thin wrapper) / ADR-039 §결정 14 (self-claim SHA 신뢰 금지 sibling) /
  ADR-119 (검사연극 금지 — opt-in/사후 detect 한계 정직 기술).
"""

import argparse
import os
import subprocess
import sys

# 출력 인코딩 robust 화 (env isolation — change-plan §7.4 / EC-5): Windows(MSYS/cp949) 등 비-UTF-8
# locale 에서 print() 가 한글·em-dash(—) 를 못 encode 해 UnicodeEncodeError 로 죽는 것을 차단.
# reconfigure 가능하면 UTF-8 + errors='replace' 로 전환 (Python 3.7+ TextIOWrapper.reconfigure).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

EXIT_PASS = 0       # PASS or data-absence honest no-op (fail-open)
EXIT_VIOLATION = 1  # base-advance / divergence 검출 (advisory warning, 비차단)
EXIT_SETUP = 2      # SETUP·ENV error (fail-closed)


def _notice(msg: str) -> None:
    print(f"::notice::check-force-push-base-advance: {msg}")


def _warning(msg: str) -> None:
    print(f"::warning::check-force-push-base-advance: {msg}")


def _error(msg: str) -> None:
    print(f"::error::check-force-push-base-advance: {msg}", file=sys.stderr)


def _git(args, cwd=None):
    """git 실행. (returncode, stdout_stripped). 실행 자체 실패(FileNotFoundError)는 raise."""
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout.strip()


def _resolve_ref(ref: str):
    """ref → resolved commit SHA. 미해결 시 None (data-absence)."""
    rc, out = _git(["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"])
    if rc == 0 and out:
        return out
    return None


def _resolve_base(base_arg):
    """base ref 후보 결정 + 해결. origin/<base> 우선, fallback <base>. 미해결 시 (None, label)."""
    base = base_arg or os.environ.get("BASE_REF") or os.environ.get("GITHUB_BASE_REF") or "main"
    base = base.strip()
    # origin/<base> 우선 (CI fetch 후 remote-tracking ref).
    for candidate in (f"origin/{base}", base):
        sha = _resolve_ref(candidate)
        if sha:
            return sha, candidate
    return None, base


def run(base_arg=None, head_arg=None) -> int:
    # setup: git 존재 + repo 여부 확인 (fail-closed).
    try:
        rc, _ = _git(["rev-parse", "--is-inside-work-tree"])
    except FileNotFoundError:
        _error("git not installed (setup-error, fail-closed exit 2)")
        return EXIT_SETUP
    if rc != 0:
        _error("not inside a git work tree (setup-error, fail-closed exit 2)")
        return EXIT_SETUP

    head = (head_arg or os.environ.get("HEAD_SHA") or "HEAD").strip()
    head_sha = _resolve_ref(head)
    if not head_sha:
        # head 미해결 = data-absence (detached/empty) — honest no-op.
        _notice(f"head ref '{head}' 미해결 — 비교 비대상 (data-absence fail-open, exit 0)")
        return EXIT_PASS

    base_sha, base_label = _resolve_base(base_arg)
    if not base_sha:
        # base 미해결 = data-absence (origin/<base> 부재 / shallow / single-commit) — honest no-op.
        _notice(
            f"base ref '{base_label}' 미해결 — 비교 비대상 "
            f"(data-absence fail-open, exit 0; CI 는 actions/checkout fetch-depth:0 + base fetch 필요)"
        )
        return EXIT_PASS

    if base_sha == head_sha:
        _notice(f"head == base ({base_label}) — base-advance/divergence 0 (PASS)")
        return EXIT_PASS

    violations = []

    # (1) base-advance: head..base 의 BEHIND count.
    rc, behind_out = _git(["rev-list", "--count", f"{head_sha}..{base_sha}"])
    if rc != 0:
        # ancestry 비교 실패(공통 조상 없음 등) = data-absence — honest no-op.
        _notice(
            f"git rev-list 비교 실패 (head..{base_label}) — 공통 조상 미존재 가능, 비교 비대상 "
            f"(data-absence fail-open, exit 0)"
        )
        return EXIT_PASS
    try:
        behind = int(behind_out or "0")
    except ValueError:
        behind = 0
    if behind > 0:
        violations.append(
            f"base-advance: head 가 {base_label} 보다 {behind} 커밋 BEHIND "
            f"(force-push 시 sibling commit overwrite 위험 — git rebase origin/{base_label} 권고)"
        )

    # (2) divergence: base 가 head 의 ancestor 가 아니면 diverged.
    rc, _ = _git(["merge-base", "--is-ancestor", base_sha, head_sha])
    # rc 0 = base 가 head 의 ancestor (포함됨, non-diverged). rc 1 = diverged. rc>1 = error.
    if rc == 1:
        violations.append(
            f"divergence: {base_label} 가 head 의 ancestor 아님 (head 가 base 미포함 = rebase 필요 = "
            f"ancestry corruption 위험)"
        )

    if violations:
        for v in violations:
            _warning(v)
        _warning(
            "force-push pre-flight 한계 정직 기술 (ADR-135 §결정 2 / ADR-119): 본 L2 CI detect 는 "
            "사후 가시화(warning) 만 — force-push 차단 불가. 진짜 pre-flight 차단(L1)은 opt-in "
            "local pre-push hook (templates/.claude/hooks/pre-push.sh.sample, PRE_PUSH_BASE_CHECK=1) 만 가능."
        )
        return EXIT_VIOLATION

    _notice(f"base-advance/divergence 0 (head ↔ {base_label} fast-forward 정합) — PASS")
    return EXIT_PASS


def main() -> int:
    parser = argparse.ArgumentParser(
        description="force-push pre-flight base-advance/divergence L2 CI 사후 detect (ADR-135, warning tier)."
    )
    parser.add_argument("--base", default=None, help="base ref (default: env BASE_REF/GITHUB_BASE_REF/main, origin/<base> 우선)")
    parser.add_argument("--head", default=None, help="head ref (default: env HEAD_SHA/HEAD)")
    args = parser.parse_args()
    return run(base_arg=args.base, head_arg=args.head)


if __name__ == "__main__":
    sys.exit(main())
