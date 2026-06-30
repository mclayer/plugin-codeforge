#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
scripts/lib/check_force_push_base_advance.py
CFP-2490 / ADR-135 (Epic CFP-2481 E2) — force-push base-advance CI 사후 detect (L2, warning tier)

own-branch force-push pre-flight 가드의 **L2 채널** (사후 가시화). force-push 는 발생 시점에
이미 origin 이 변경된 후라 CI 는 **차단 불가능** — 사후 detect(warning) 만 가능 (ADR-135 §결정 2).
진짜 pre-flight 차단은 L1 local pre-push hook(opt-in) 만 가능 (templates/.claude/hooks/pre-push.sh.sample).

검사 명제 (ADR-135 §결정 1.2 — base-advance / divergence detect):
  PR 의 head branch tip 이 base branch(origin/main) 의 advance 를 미반영한 채 열려 있으면
  (= base 가 head 작성 이후 advance 했는데 rebase 안 됨) → force-push 시 sibling commit
  ancestry corruption 위험 신호로 사후 표면화 (warning).

  - base-advance: base 가 head..base 방향으로 N>0 commit advance (head 가 base 를 미포함).
  - divergence  : base 가 head 의 ancestor 가 아님 (head 가 base 의 일부 commit 미반영).

입력 (CI 환경 — git ancestry 실측, PR-body-proxy 아님 = 위조 곤란):
  --base-sha <SHA>   base branch tip SHA (예: origin/main, github.event.pull_request.base.sha)
  --head-sha <SHA>   PR head tip SHA (github.event.pull_request.head.sha)
  --base-ref <REF>   (선택) base ref 이름 (메시지용, default "main")
  SHA 미제공 시 환경변수 BASE_SHA / HEAD_SHA fallback.

graceful degradation (§7.4 — rate-limit / offline 완화):
  SHA 가 local repo 에 부재(shallow checkout / fetch 실패) → ::warning + exit 0 (비차단, advisory degrade).
  git 미설치 / SHA 인자 전무 → SETUP exit 2.

ReDoS-safe (ADR-061 Amd3 §결정 11):
  git output parse only — line-by-line, 정규식은 SHA-shape anchored simple regex (nested quantifier 0).
  shell injection 차단 = subprocess list-arg (shell=False), 사용자 입력 SHA 는 SHA-shape 검증 후 사용.

Exit codes (ADR-060 §결정 5 3-tier — warning tier):
  0 = PASS (base-advance/divergence 0) / graceful skip (SHA 부재)
  1 = WARN (base-advance 또는 divergence 검출 — workflow continue-on-error 로 비차단, advisory only)
  2 = SETUP error (git 미설치 / SHA 인자 전무)

ADR refs: ADR-135 (carrier, §결정 1·2·5·6) / ADR-039 §결정 14 (Pre-spawn-pin sibling) /
  ADR-060 §결정 5 (warning tier) / ADR-061 (thin wrapper + Python SSOT) / ADR-005 (byte-identical workflow).
"""

import argparse
import os
import re
import subprocess
import sys

# Windows cp949 인코딩 회피 — stdout/stderr UTF-8 강제 (ADR-061 portability).
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# SHA-shape anchored simple regex (ReDoS-safe — bounded quantifier, nested 0).
_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")

EXIT_PASS = 0
EXIT_WARN = 1
EXIT_SETUP = 2


def _emit_warning(msg: str) -> None:
    """GitHub Actions warning annotation + stderr."""
    print(f"::warning::{msg}", file=sys.stderr)


def _git(args, check=False):
    """subprocess git (shell=False, list-arg). 실패 시 (rc, out) 반환."""
    try:
        proc = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=False,
        )
        return proc.returncode, (proc.stdout or "").strip()
    except FileNotFoundError:
        return 127, ""


def _is_valid_sha(sha: str) -> bool:
    return bool(sha) and bool(_SHA_RE.match(sha))


def _rev_known(sha: str) -> bool:
    """SHA 가 local repo 에서 resolvable 한지 (shallow checkout 에서 부재 가능)."""
    rc, _ = _git(["cat-file", "-e", f"{sha}^{{commit}}"])
    return rc == 0


def check(base_sha: str, head_sha: str, base_ref: str) -> int:
    # git 존재 확인 (SETUP).
    rc, _ = _git(["--version"])
    if rc == 127:
        print("[codeforge-evidence-registry-infra-error] check-force-push-base-advance: git not installed",
              file=sys.stderr)
        return EXIT_SETUP

    # SHA 인자 전무 = SETUP (호출 계약 위반).
    if not base_sha and not head_sha:
        print("[codeforge-evidence-registry-infra-error] check-force-push-base-advance: "
              "--base-sha/--head-sha (또는 BASE_SHA/HEAD_SHA env) 미제공",
              file=sys.stderr)
        return EXIT_SETUP

    # SHA-shape 검증 (injection-safe — shell 미사용이지만 형식 검증으로 fail-fast).
    for label, sha in (("base", base_sha), ("head", head_sha)):
        if sha and not _is_valid_sha(sha):
            print(f"[codeforge-evidence-registry-infra-error] check-force-push-base-advance: "
                  f"{label}-sha 형식 무효 (SHA-shape 아님): {sha!r}",
                  file=sys.stderr)
            return EXIT_SETUP

    if not base_sha or not head_sha:
        _emit_warning("base-sha/head-sha 중 하나가 비어 있음 — force-push base-advance check graceful skip (advisory degrade)")
        return EXIT_PASS

    # graceful: SHA 가 local repo 에 부재(shallow / fetch 실패) → 비차단 degrade.
    if not _rev_known(base_sha) or not _rev_known(head_sha):
        _emit_warning(
            f"base({base_sha[:12]}) 또는 head({head_sha[:12]}) SHA 가 local repo 에 부재 "
            f"(shallow checkout / fetch 실패) — force-push base-advance check graceful skip (비차단)"
        )
        return EXIT_PASS

    # base-advance: head..base 방향 commit 수 (base 가 head 를 넘어 advance 한 정도).
    rc, out = _git(["rev-list", "--count", f"{head_sha}..{base_sha}"])
    if rc != 0:
        _emit_warning("git rev-list 실패 — force-push base-advance check graceful skip (비차단)")
        return EXIT_PASS
    try:
        behind = int(out.splitlines()[0]) if out else 0
    except (ValueError, IndexError):
        behind = 0

    # divergence: base 가 head 의 ancestor 인가 (아니면 head 가 base 의 일부 commit 미반영 = diverged).
    rc_anc, _ = _git(["merge-base", "--is-ancestor", base_sha, head_sha])
    diverged = (rc_anc != 0)  # rc 0 = base 가 head 의 ancestor (정상), 비-0 = diverged

    if behind > 0 or diverged:
        detail = []
        if behind > 0:
            detail.append(f"base(origin/{base_ref}) 가 head 보다 {behind} 커밋 advance")
        if diverged:
            detail.append(f"head 가 origin/{base_ref} 의 일부 commit 미반영 (diverged)")
        _emit_warning(
            "force-push base-advance 사후 detect (warning, 비차단) — "
            + " / ".join(detail)
            + f". head={head_sha[:12]} base={base_sha[:12]}. "
            "force-push 전 base rebase 권고 (sibling commit ancestry corruption 위험). "
            "차단형 가드는 L1 local pre-push hook (PRE_PUSH_BASE_CHECK=1) — ADR-135 §결정 2."
        )
        print(
            f"::notice::본 detect 는 사후 가시화(warning) 입니다. force-push 는 이미 발생했을 수 있으며 "
            f"CI 는 차단 불가 (ADR-135 §결정 2 한계 — opt-in L1 hook 만 진짜 pre-flight)."
        )
        return EXIT_WARN

    print(f"force-push base-advance check PASS — head 가 origin/{base_ref} 를 포함 (base-advance/divergence 0).")
    return EXIT_PASS


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="force-push base-advance CI 사후 detect (L2, warning tier) — ADR-135"
    )
    parser.add_argument("--base-sha", default=os.environ.get("BASE_SHA", ""))
    parser.add_argument("--head-sha", default=os.environ.get("HEAD_SHA", ""))
    parser.add_argument("--base-ref", default=os.environ.get("BASE_REF", "main"))
    args = parser.parse_args(argv)
    return check(args.base_sha.strip(), args.head_sha.strip(), args.base_ref.strip() or "main")


if __name__ == "__main__":
    sys.exit(main())
