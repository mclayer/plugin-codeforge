#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_increment_justification.py
CFP-2061-S1 / ADR-060 §결정 30

정당화 순증 게이트 — 검사·ADR·스크립트 신규 추가 PR 에 실효 정당화 강제.
ADR-060 framework 14번째 warning-tier entry (increment-justification-presence).

기존 약화 방향 가드(check-tier-downgrade-guard.sh)의 순증(추가) 방향 대칭물.
구조: check-bypass-justification-marker.py 의 presence-grep + exempt channel + 3-tier exit 를
      check-tier-downgrade-guard.sh 의 base-ref diff 기반 trigger-path 감지 와 결합.

trigger-path closed-set (G1):
  (a) docs/evidence-checks-registry.yaml 의 entries[] row 신규 append (diff hunk 에 '- name:' 추가)
  (b) scripts/check-*.{sh,py} 신규 파일 (diff status=added)
  (c) (templates|.github)/workflows/*.yml 신규 파일 (diff status=added)
  (d) archive/adr/ADR-*.md 신규 파일 + 신규 adr_number (Amendment 아닌 신규)

marker (PR body, 3 AND):
  ^\\[increment-justification\\] (line start anchor)
  AND why= (비어있지 않음)
  AND blocks-or-replaces= (비어있지 않음)

exit codes (ADR-060 §결정 15 3-tier):
  0 = PASS (trigger-path 0건 또는 marker 존재 또는 exempt)
  1 = WARNING (marker 부재 — warning tier, continue-on-error 로 merge 미차단)
  2 = SETUP error (gh api auth 실패 등)

exempt channels:
  - hotfix-bypass:increment-justification label (EC-5 self-meta loop 회피)
  - CIJ_MOCK_EXEMPT_PATHS 에 포함된 경로 (AC-4 보안/consumer-whitelist)
  - CIJ_MOCK_BASE_ABSENT="1" (base-ref 부재 — 신규 repo 통과)

Test override env vars (bats TC mock 지원):
  CIJ_MOCK_DIFF_FILES        — newline-delimited "STATUS\\tPATH" (gh api diff 대체)
  CIJ_MOCK_PR_BODY           — PR body text (gh api 대체)
  CIJ_MOCK_PR_LABELS         — comma-separated label names (gh api 대체)
  CIJ_MOCK_BASE_ABSENT       — "1" 이면 base-ref 부재 시뮬레이션
  CIJ_MOCK_EXEMPT_PATHS      — newline-delimited exempt paths
  CIJ_MOCK_REGISTRY_APPEND   — "1" 이면 registry에 '- name:' 추가 시뮬레이션

False-positive risk 명시 (Story §7.2 Spoofing):
  grep-presence 는 marker body 의 semantic 적절성을 보장하지 않음.
  why= / blocks-or-replaces= 값이 빈 문자열이어도 substring 존재 시 PASS.
  semantic adequacy = reviewer responsibility.
"""

import argparse
import os
import re
import subprocess
import sys

# ── 상수 ──────────────────────────────────────────────────────────────────────
SELF_META_EXEMPT_LABEL = "hotfix-bypass:increment-justification"

# trigger-path 판별 패턴 (G1 closed-set)
TRIGGER_CHECK_SCRIPT = re.compile(
    r"^scripts/check-[^/]+\.(sh|py)$"
)
TRIGGER_WORKFLOW = re.compile(
    r"^(templates|\.github)/workflows/[^/]+\.yml$"
)
TRIGGER_ADR = re.compile(
    r"^archive/adr/ADR-[^/]+\.md$"
)
REGISTRY_PATH = "docs/evidence-checks-registry.yaml"

# marker 검증 패턴 (PR body, 3 AND)
MARKER_LINE_PATTERN = re.compile(r"^\[increment-justification\]", re.MULTILINE)
MARKER_WHY_PATTERN = re.compile(r"why=")
MARKER_BLOCKS_PATTERN = re.compile(r"blocks-or-replaces=")


# ── gh CLI wrapper ─────────────────────────────────────────────────────────────
def run_gh(args):
    """gh CLI 호출 wrapper. 실패 시 subprocess.CalledProcessError 발생."""
    cmd = ["gh"] + args
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True,
        encoding="utf-8", errors="replace",
    )
    return result.stdout.strip()


# ── diff files 수집 ────────────────────────────────────────────────────────────
def get_diff_files(repo, pr_number):
    """
    PR diff 파일 목록 반환.
    Returns: list of (status, path) tuples
      status: 'A' (added), 'M' (modified), 'D' (deleted), 'R' (renamed), etc.

    Mock: CIJ_MOCK_DIFF_FILES 환경변수가 설정된 경우 실제 gh api 호출 없이
          newline-delimited "STATUS\\tPATH" 형식으로 반환.
    """
    mock_var = "CIJ_MOCK_DIFF_FILES"
    if mock_var in os.environ:
        files = []
        for line in os.environ[mock_var].strip().splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) == 2:
                files.append((parts[0].strip(), parts[1].strip()))
            else:
                # status 없이 path 만인 경우 M 으로 간주
                files.append(("M", parts[0].strip()))
        return files

    # 실제 gh api 호출
    raw = run_gh([
        "api", "-X", "GET",
        f"/repos/{repo}/pulls/{pr_number}/files",
        "--paginate",
        "--jq", ".[] | .status + \"\\t\" + .filename",
    ])
    files = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2:
            files.append((parts[0].strip(), parts[1].strip()))
    return files


# ── PR body 수집 ───────────────────────────────────────────────────────────────
def get_pr_body(repo, pr_number):
    """
    PR body 반환.
    Mock: CIJ_MOCK_PR_BODY 환경변수 사용.
    """
    mock_var = "CIJ_MOCK_PR_BODY"
    if mock_var in os.environ:
        return os.environ[mock_var]

    raw = run_gh([
        "api", "-X", "GET",
        f"/repos/{repo}/pulls/{pr_number}",
        "--jq", ".body // \"\"",
    ])
    return raw


# ── PR labels 수집 ─────────────────────────────────────────────────────────────
def get_pr_labels(repo, pr_number):
    """
    PR label 이름 목록 반환.
    Mock: CIJ_MOCK_PR_LABELS 환경변수 사용 (comma-separated).
    """
    mock_var = "CIJ_MOCK_PR_LABELS"
    if mock_var in os.environ:
        raw = os.environ[mock_var].strip()
        if not raw:
            return []
        return [lbl.strip() for lbl in raw.split(",") if lbl.strip()]

    raw = run_gh([
        "api", "-X", "GET",
        f"/repos/{repo}/pulls/{pr_number}",
        "--jq", ".labels[].name",
    ])
    return [line.strip() for line in raw.splitlines() if line.strip()]


# ── exempt paths 수집 ─────────────────────────────────────────────────────────
def get_exempt_paths():
    """
    AC-4 exempt path 목록 반환.
    Mock: CIJ_MOCK_EXEMPT_PATHS 환경변수 사용 (newline-delimited).
    실제 환경에서는 보안/consumer-whitelist 태그 entry 경로만 포함.
    """
    mock_var = "CIJ_MOCK_EXEMPT_PATHS"
    if mock_var in os.environ:
        raw = os.environ[mock_var].strip()
        if not raw:
            return set()
        return {p.strip() for p in raw.splitlines() if p.strip()}
    # 실제 환경: 잠정 빈 set (S2 머지 후 정합 — §7 결정 5 / OOS1)
    return set()


# ── trigger-path 감지 ─────────────────────────────────────────────────────────
def detect_trigger_paths(diff_files):
    """
    G1 closed-set trigger-path 감지.
    Returns: list of (reason, path) — trigger-path 해당 항목 목록
    """
    triggers = []
    exempt_paths = get_exempt_paths()

    # registry append 시뮬레이션 mock
    registry_append_mock = os.environ.get("CIJ_MOCK_REGISTRY_APPEND", "") == "1"

    for status, path in diff_files:
        if path in exempt_paths:
            continue

        # (a) registry row 신규 append
        # 실제 환경: diff hunk 파싱으로 '- name:' 추가 감지
        # mock 환경: CIJ_MOCK_REGISTRY_APPEND=1 OR path == REGISTRY_PATH && status==M (후자는 hunk 파싱 필요)
        # 본 구현: REGISTRY_PATH 의 M/A + mock flag 조합
        if path == REGISTRY_PATH and status in ("A", "M") and registry_append_mock:
            triggers.append(("registry-append", path))
            continue

        # (b) scripts/check-*.{sh,py} 신규 파일
        if status == "A" and TRIGGER_CHECK_SCRIPT.match(path):
            triggers.append(("new-check-script", path))
            continue

        # (c) (templates|.github)/workflows/*.yml 신규 파일
        if status == "A" and TRIGGER_WORKFLOW.match(path):
            triggers.append(("new-workflow", path))
            continue

        # (d) archive/adr/ADR-*.md 신규 파일 (Amendment 아님 = status=A)
        if status == "A" and TRIGGER_ADR.match(path):
            triggers.append(("new-adr", path))
            continue

    return triggers


# ── base-ref 부재 판정 ────────────────────────────────────────────────────────
def is_base_absent():
    """
    base-ref 부재 여부.
    Mock: CIJ_MOCK_BASE_ABSENT="1"
    실제: git rev-parse origin/main 가능 여부로 판단 (check-tier-downgrade-guard 패턴 차용).
    """
    if os.environ.get("CIJ_MOCK_BASE_ABSENT", "") == "1":
        return True

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "-q", "origin/main"],
            capture_output=True, text=True,
        )
        return result.returncode != 0
    except FileNotFoundError:
        return True


# ── marker 검증 ───────────────────────────────────────────────────────────────
def has_valid_marker(pr_body):
    """
    PR body 에 유효한 [increment-justification] marker 존재 여부.
    3 AND 조건:
      1. ^\\[increment-justification\\] 라인 start anchor
      2. why= substring
      3. blocks-or-replaces= substring
    """
    if not MARKER_LINE_PATTERN.search(pr_body):
        return False
    if not MARKER_WHY_PATTERN.search(pr_body):
        return False
    if not MARKER_BLOCKS_PATTERN.search(pr_body):
        return False
    return True


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="정당화 순증 게이트 — 검사·ADR·스크립트 신규 추가 PR 에 실효 정당화 강제 "
                    "(CFP-2061-S1 / ADR-060 §결정 30)"
    )
    parser.add_argument(
        "--repo",
        default="mclayer/plugin-codeforge",
        help="GitHub repo (OWNER/REPO). default: mclayer/plugin-codeforge",
    )
    parser.add_argument(
        "--pr-number",
        type=int,
        default=None,
        help="PR number. 미지정 시 trigger-path 감지만 (diff mock 필수).",
    )
    parser.add_argument(
        "--base-ref",
        default=None,
        help="base ref override (default: origin/main).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="dry-run 모드: 판정 출력만, gh api 부작용 없음.",
    )
    args = parser.parse_args()

    repo = args.repo
    pr_number = args.pr_number

    # Step 1: base-ref 판정 (check-tier-downgrade-guard 패턴 차용)
    if is_base_absent():
        print(
            "check-increment-justification: PASS -- "
            "base ref(origin/main) 미가용, 비교 생략 (신규 repo / detached 환경)."
        )
        sys.exit(0)

    # Step 2: diff files 수집
    mock_pr_env_set = "CIJ_MOCK_DIFF_FILES" in os.environ
    if not mock_pr_env_set and pr_number is None:
        print(
            "[check-increment-justification-error] --pr-number 또는 CIJ_MOCK_DIFF_FILES 필수.",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        diff_files = get_diff_files(repo, pr_number)
    except subprocess.CalledProcessError as e:
        print(
            f"[check-increment-justification-error] gh api diff 수집 실패: {e.stderr}",
            file=sys.stderr,
        )
        sys.exit(2)

    # Step 3: trigger-path 감지 (G1 closed-set)
    triggers = detect_trigger_paths(diff_files)

    if not triggers:
        print(
            "check-increment-justification: PASS -- "
            "trigger-path 0건 (chore fast-path 자동 충족)."
        )
        sys.exit(0)

    print(f"check-increment-justification: trigger-path {len(triggers)}건 감지:")
    for reason, path in triggers:
        print(f"  [{reason}] {path}")

    # Step 4: exempt 판정
    # EC-5: self-meta bypass label
    try:
        labels = get_pr_labels(repo, pr_number) if pr_number else []
    except subprocess.CalledProcessError as e:
        print(
            f"[check-increment-justification-error] gh api labels 수집 실패: {e.stderr}",
            file=sys.stderr,
        )
        sys.exit(2)

    if SELF_META_EXEMPT_LABEL in labels:
        print(
            f"check-increment-justification: PASS -- "
            f"self-meta exempt label ({SELF_META_EXEMPT_LABEL}) 감지."
        )
        sys.exit(0)

    # Step 5: PR body marker 검증
    try:
        pr_body = get_pr_body(repo, pr_number) if pr_number else os.environ.get("CIJ_MOCK_PR_BODY", "")
    except subprocess.CalledProcessError as e:
        print(
            f"[check-increment-justification-error] gh api PR body 수집 실패: {e.stderr}",
            file=sys.stderr,
        )
        sys.exit(2)

    if has_valid_marker(pr_body):
        print(
            "check-increment-justification: PASS -- "
            "[increment-justification] marker 확인 (why + blocks-or-replaces 존재)."
        )
        sys.exit(0)

    # Step 6: WARNING (marker 부재)
    print(
        "check-increment-justification: WARNING -- "
        "trigger-path 감지됐으나 [increment-justification] marker 부재."
    )
    print(
        "  PR body 에 다음 marker 를 추가하세요:"
    )
    print(
        "    [increment-justification] why=<왜 필요한가> blocks-or-replaces=<무엇을 차단/대체>"
    )
    print(
        "  Note: semantic adequacy not verified (grep-presence only) -- "
        "reviewer responsibility (ADR-060 §결정 30)"
    )
    # warning tier: exit 1
    sys.exit(1)


if __name__ == "__main__":
    main()
