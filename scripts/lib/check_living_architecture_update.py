#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1429 (Sub-C S3.5 of EPIC #1415) — Living Architecture per-Epic mandatory update gate lint
# Owner ADR: ADR-112 §결정 1 (per-Epic mandatory update gate) + §결정 2 (closed-binary)
# Wire layer: ADR-082 §결정 6 retain pattern 답습 (Wave 1 declare → Wave 2 wire = 본 script)
# Tier: warning (ADR-060 §결정 5 — 첫 도입 = warning mode)
# Bypass label: hotfix-bypass:living-architecture-update
#
# ADR-061 §결정 1 — Python SSOT (heredoc 금지), ADR-060 §결정 5 warning-tier
# ADR-068 I-3 정합 — bypass label 부재 시 unconditional warning (조건 분기 0)
#
# 검사 (PR-mode default — ADR-112 §결정 2 closed-binary):
#   (a) PR touched files 안 `docs/architecture/<plugin>.md` (Living Architecture page) presence
#   (b) PR body / commit message 안 `[living-arch-no-impact: <rationale>]` explicit declare
#   양쪽 모두 부재 시 [WARN] emit — exit 0 retain (warning-tier)
#
# 비고: ADR-112 §결정 1 trigger = "Epic close 직전 (Epic 마지막 Story Phase 2 PR merge 직전)"
#       per-Epic granularity 가 ideal — 본 lint = per-PR heuristic proxy (PR-level evidence presence).
#       추후 Epic-aware enforcement = sibling carrier (warning-tier 도입 후 evidence-gated promotion).
#
# Exit code (ADR-060 §결정 15 3-tier):
#   0 — PASS 또는 WARN (warning-tier = 항상 exit 0, PR merge 미차단)
#   2 — setup error (gh 미설치 등)
#
# Usage:
#   python3 check_living_architecture_update.py             # PR-mode (GITHUB_REF or PR_NUMBER env)
#   python3 check_living_architecture_update.py --pr 1429   # explicit PR
#   python3 check_living_architecture_update.py --file body.md  # offline self-test

import os
import re
import sys
import subprocess
from pathlib import Path

# Windows console 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPT_NAME = "[check-living-arch-update]"
BYPASS_LABEL = "hotfix-bypass:living-architecture-update"

# ─── 상수 ─────────────────────────────────────────────────────────────────────
# ADR-112 §결정 2 (b) no-op explicit declare marker
NO_OP_MARKER_RE = re.compile(r"\[living-arch-no-impact:\s*[^\]]+\]")
# Living Architecture page path pattern (ADR-078 SSOT)
LIVING_ARCH_PATH_RE = re.compile(r"^docs/architecture/.+\.md$")


def _parse_args(argv):
    """argv 파싱 — (mode, target) 반환."""
    mode = "pr"
    target = None
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--help", "-h"):
            print(__doc__ or "", file=sys.stderr)
            sys.exit(0)
        elif arg == "--pr" and i + 1 < len(argv):
            mode = "pr"
            target = argv[i + 1]
            i += 2
        elif arg == "--file" and i + 1 < len(argv):
            mode = "file"
            target = argv[i + 1]
            i += 2
        else:
            print(f"{SCRIPT_NAME} ERROR: unknown arg '{arg}'", file=sys.stderr)
            sys.exit(2)
    # PR mode default: env fallback
    if mode == "pr" and target is None:
        target = os.environ.get("PR_NUMBER", "")
        if not target:
            ref = os.environ.get("GITHUB_REF", "")
            # refs/pull/N/merge 등 패턴
            m = re.search(r"refs/pull/(\d+)/", ref)
            if m:
                target = m.group(1)
    return mode, target


def _gh_available():
    """gh CLI 존재 확인."""
    try:
        subprocess.run(
            ["gh", "--version"], capture_output=True, check=True, timeout=10
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _fetch_pr_files(pr_number):
    """gh pr view --json files — touched file path list 반환. 실패 시 [] + warning."""
    try:
        result = subprocess.run(
            [
                "gh", "pr", "view", str(pr_number),
                "--json", "files",
                "--jq", ".files[].path",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(
                f"{SCRIPT_NAME} [WARN] gh pr view files 실패 (exit {result.returncode}): {result.stderr.strip()}",
                file=sys.stderr,
            )
            return []
        return [p.strip() for p in result.stdout.splitlines() if p.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"{SCRIPT_NAME} [WARN] gh pr view files 실패 — {e}", file=sys.stderr)
        return []


def _fetch_pr_body(pr_number):
    """gh pr view --json body — PR body 반환. 실패 시 '' + warning."""
    try:
        result = subprocess.run(
            ["gh", "pr", "view", str(pr_number), "--json", "body", "--jq", ".body"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(
                f"{SCRIPT_NAME} [WARN] gh pr view body 실패 (exit {result.returncode})",
                file=sys.stderr,
            )
            return ""
        return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"{SCRIPT_NAME} [WARN] gh pr view body 실패 — {e}", file=sys.stderr)
        return ""


def _fetch_pr_labels(pr_number):
    """gh pr view --json labels — label name list 반환. 실패 시 []."""
    try:
        result = subprocess.run(
            [
                "gh", "pr", "view", str(pr_number),
                "--json", "labels",
                "--jq", "[.labels[].name] | join(\",\")",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return []
        return [s.strip() for s in result.stdout.strip().split(",") if s.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def _check_body_for_marker(body):
    """body 안 no-op marker presence 검사."""
    return bool(NO_OP_MARKER_RE.search(body or ""))


def _check_files_for_living_arch(files):
    """touched file list 안 Living Architecture page presence 검사. 매칭 list 반환."""
    return [f for f in files if LIVING_ARCH_PATH_RE.match(f)]


def _run_pr_mode(pr_number):
    """PR-mode: gh CLI 로 files + body + labels fetch → closed-binary check."""
    if not _gh_available():
        print(
            f"{SCRIPT_NAME} ERROR: gh CLI 미설치 — PR-mode 사용 불가 (--file PATH 로 offline 검사 가능)",
            file=sys.stderr,
        )
        sys.exit(2)

    # Bypass label check
    labels = _fetch_pr_labels(pr_number)
    if BYPASS_LABEL in labels:
        print(
            f"{SCRIPT_NAME} [OK] bypass label '{BYPASS_LABEL}' 부착 — skip (warning 발화 안 함)",
            file=sys.stderr,
        )
        return 0

    files = _fetch_pr_files(pr_number)
    body = _fetch_pr_body(pr_number)

    living_arch_hits = _check_files_for_living_arch(files)
    marker_present = _check_body_for_marker(body)

    # ADR-112 §결정 2 closed-binary
    # (a) 5-anchor section update 완료 = Living Architecture page touched
    # (b) 5-anchor 모두 update 불필요 = [living-arch-no-impact: <rationale>] explicit declare
    # (c) 위 양쪽 부재 = WARN (ADR-112 §결정 4 — DesignReviewPL emit `living-architecture-not-updated`)

    if living_arch_hits:
        print(
            f"{SCRIPT_NAME} [OK] Living Architecture page touched ({len(living_arch_hits)}건): "
            f"{', '.join(living_arch_hits)}",
            file=sys.stderr,
        )
        return 0

    if marker_present:
        print(
            f"{SCRIPT_NAME} [OK] no-op marker '[living-arch-no-impact: ...]' detected in PR body — explicit declare 충족",
            file=sys.stderr,
        )
        return 0

    # WARN — exit 0 retain (warning-tier ADR-060 §결정 5)
    print(
        f"{SCRIPT_NAME} [WARN] Living Architecture update gate 미충족 (ADR-112 §결정 2 closed-binary):",
        file=sys.stderr,
    )
    print(
        f"  (a) Living Architecture page (docs/architecture/<plugin>.md) touched: 0건",
        file=sys.stderr,
    )
    print(
        f"  (b) PR body 안 '[living-arch-no-impact: <rationale>]' explicit declare: 부재",
        file=sys.stderr,
    )
    print(
        f"  → ArchitectAgent re-spawn 의무 (ADR-112 §결정 1) — 5-anchor section 영향 평가 후 (a) update 또는 (b) declare 추가",
        file=sys.stderr,
    )
    print(
        f"  Bypass: '{BYPASS_LABEL}' label 부착 시 skip",
        file=sys.stderr,
    )
    print(
        f"  Wave 1 — warning-tier (exit 0, PR merge 미차단). pattern_count >= 3 재발 시 promote (evidence-checks-registry).",
        file=sys.stderr,
    )
    return 0  # warning-tier — always exit 0


def _run_file_mode(file_path):
    """file-mode: 단일 파일 (PR body proxy) 안 no-op marker presence 만 검사 (offline self-test)."""
    path = Path(file_path)
    if not path.exists():
        print(f"{SCRIPT_NAME} ERROR: file '{file_path}' 부재", file=sys.stderr)
        sys.exit(2)
    body = path.read_text(encoding="utf-8", errors="replace")
    if _check_body_for_marker(body):
        print(
            f"{SCRIPT_NAME} [OK] no-op marker '[living-arch-no-impact: ...]' detected in {file_path}",
            file=sys.stderr,
        )
    else:
        print(
            f"{SCRIPT_NAME} [WARN] no-op marker '[living-arch-no-impact: ...]' 부재 in {file_path}",
            file=sys.stderr,
        )
        print(
            f"  (file-mode = offline self-test, Living Architecture page touched check 영역 외 — PR-mode 사용 권장)",
            file=sys.stderr,
        )
    return 0  # warning-tier


def main():
    mode, target = _parse_args(sys.argv[1:])

    if mode == "pr":
        if not target:
            print(
                f"{SCRIPT_NAME} INFO: PR number 부재 (--pr N 또는 PR_NUMBER/GITHUB_REF env 미설정) — skip",
                file=sys.stderr,
            )
            sys.exit(0)
        rc = _run_pr_mode(target)
    elif mode == "file":
        rc = _run_file_mode(target)
    else:
        print(f"{SCRIPT_NAME} ERROR: unknown mode '{mode}'", file=sys.stderr)
        sys.exit(2)

    sys.exit(rc)


if __name__ == "__main__":
    main()
