#!/usr/bin/env python3
"""CFP-1346 / ADR-108 §결정 3 — label-registry-v2 description count parity lint.

Detection rule:
  label-registry-v2.md §3 yaml block 안 hotfix-bypass:* entry description text 의
  'N번째 hotfix-bypass:* family member' citation = raw active
  `grep -c '^  - name: hotfix-bypass:'` count post-append parity.

Lint scope (false positive 차단):
  - NEW append entry (PR diff 영역) 만 catch
  - Prior frozen entries = false_positive 영역, skip
  - Non-hotfix-bypass:* count semantic ("N번째 tier" 등) = false_positive, skip

ADR-061 정합: Python SSOT (> 5줄), bash 5-line thin wrapper 호출.
Windows cp949 limitation 차단: sys.stdout.reconfigure(encoding='utf-8').
ADR-060 exit-code 3-tier: 0 (PASS) / 1 (FAIL hard) / 2 (advisory FAIL warning tier).
Error visibility (ADR-082 Amendment 9 §결정 11.B / CFP-1330): silent error mask 금지.
network_scope: offline (ADR-060 Amendment 14 §결정 28).
"""

import os
import re
import subprocess
import sys

# Windows cp949 limitation 차단 (ADR-061 + DesignReviewPL out-of-scope obs #2 pre-apply)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LABEL_REGISTRY_PATH_FRAGMENT = "docs/inter-plugin-contracts/label-registry-v2.md"

# catch pattern: literal "N번째 hotfix-bypass:* family member" exact form
# ADR-108 §결정 3 + Researcher #2 gap 정합
CATCH_PATTERN = re.compile(r"(\d+)번째 hotfix-bypass:\* family member")

# exclude patterns — non-count semantic (false positive 차단)
EXCLUDE_PATTERNS = [
    re.compile(r"\d+번째 tier"),
    re.compile(r"\d+번째 source"),
    re.compile(r"\d+번째 enum\s"),
    re.compile(r"\d+번째 verdict-level"),
    re.compile(r"\d+번째 literal"),
    re.compile(r"\d+번째 optional\s"),
    re.compile(r"\d+번째 sub-"),
    re.compile(r"\d+번째 invariant"),
    re.compile(r"\d+번째 field"),
    re.compile(r"\d+번째 entry\b"),  # non-bypass entry context
]

# bypass label env var name
BYPASS_LABEL_ENV = "BYPASS_LABEL"
BYPASS_LABEL_VALUE = "hotfix-bypass:label-registry-frozen-baseline-count-parity"

# env var for changed files (space or newline separated)
CHANGED_FILES_ENV = "CHANGED_FILES"

# env var for registry path override (testing)
REGISTRY_PATH_ENV = "LABEL_REGISTRY_PATH"

# env var for diff scope override (testing) — JSON list of "added" lines
DIFF_LINES_ENV = "DIFF_ADDED_LINES"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_repo_root() -> str:
    """git rev-parse --show-toplevel으로 repo root 획득."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"ERROR: git rev-parse failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def is_bypass_active() -> bool:
    """bypass label env var 확인."""
    bypass = os.environ.get(BYPASS_LABEL_ENV, "").strip()
    return bypass == BYPASS_LABEL_VALUE


def get_registry_path(repo_root: str) -> str:
    """label-registry-v2.md 절대 경로 반환 (env override 지원)."""
    override = os.environ.get(REGISTRY_PATH_ENV, "").strip()
    if override:
        return override
    return os.path.join(repo_root, LABEL_REGISTRY_PATH_FRAGMENT)


def is_registry_touched() -> bool:
    """PR diff scope 안에 label-registry-v2.md 가 포함되어 있는지 확인.

    CHANGED_FILES env var (space/newline separated file list) 사용.
    미설정 시 git diff HEAD~1 기반 fallback.
    """
    changed_env = os.environ.get(CHANGED_FILES_ENV, "").strip()
    if changed_env:
        changed_files = changed_env.replace("\n", " ").split()
        for f in changed_files:
            if LABEL_REGISTRY_PATH_FRAGMENT in f or f.endswith("label-registry-v2.md"):
                return True
        return False

    # fallback: git diff HEAD~1 --name-only
    result = subprocess.run(
        ["git", "diff", "HEAD~1", "--name-only"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        # diff 불가 (초기 커밋 등) — conservative PASS
        return False
    for line in result.stdout.splitlines():
        if LABEL_REGISTRY_PATH_FRAGMENT in line or line.endswith("label-registry-v2.md"):
            return True
    return False


def get_diff_added_lines(registry_path: str) -> list[str]:
    """PR diff 에서 label-registry-v2.md 의 newly added (+) lines 반환.

    DIFF_ADDED_LINES env var 설정 시 해당 값 사용 (newline separated, testing).
    미설정 시 git diff HEAD~1 기반 fallback.
    """
    diff_env = os.environ.get(DIFF_LINES_ENV, "").strip()
    if diff_env:
        return [line for line in diff_env.splitlines() if line]

    result = subprocess.run(
        ["git", "diff", "HEAD~1", "--", registry_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return []

    added = []
    for line in result.stdout.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])  # strip leading "+"
    return added


def count_raw_hotfix_bypass_entries(registry_path: str) -> int:
    """label-registry-v2.md 안 `^  - name: hotfix-bypass:` 라인 수 반환.

    raw active count post-append (ADR-108 §결정 3 기준).
    """
    try:
        with open(registry_path, encoding="utf-8") as f:
            content = f.read()
    except OSError as e:
        print(f"ERROR: 파일 읽기 실패 ({registry_path}): {e}", file=sys.stderr)
        sys.exit(1)

    count = 0
    for line in content.splitlines():
        if line.startswith("  - name: hotfix-bypass:"):
            count += 1
    return count


def extract_claim_from_added_lines(added_lines: list[str]) -> int | None:
    """Added lines 에서 'N번째 hotfix-bypass:* family member' claim 추출.

    false positive 차단:
    - EXCLUDE_PATTERNS 에 해당하는 라인은 skip
    - catch pattern 이 여러 번 나오면 마지막 값 사용 (append order 기준)

    Returns:
        int claim_count 또는 None (claim 없음 — lint skip)
    """
    last_claim: int | None = None

    for line in added_lines:
        # exclude pattern 체크
        should_exclude = any(pat.search(line) for pat in EXCLUDE_PATTERNS)
        if should_exclude:
            continue

        # catch pattern 체크
        m = CATCH_PATTERN.search(line)
        if m:
            last_claim = int(m.group(1))

    return last_claim


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    """Main entry point.

    Returns:
        0 — PASS
        1 — FAIL hard (claim mismatch)
        2 — advisory FAIL (warning tier, ADR-060 exit-code 3-tier)
    """
    # bypass label 체크
    if is_bypass_active():
        bypass_label = os.environ.get(BYPASS_LABEL_ENV, "")
        print(f"SKIPPED — bypass label attached: {bypass_label}")
        print("[audit] bypass label honored — lint skipped (ADR-108 §결정 3 bypass channel)")
        return 0

    repo_root = get_repo_root()
    registry_path = get_registry_path(repo_root)

    # label-registry-v2.md 가 PR diff 에 없으면 lint skip
    if not is_registry_touched():
        print("SKIP — label-registry-v2.md not in diff scope, lint not applicable")
        return 0

    # diff added lines 추출
    added_lines = get_diff_added_lines(registry_path)
    if not added_lines:
        print("SKIP — no added lines in label-registry-v2.md diff")
        return 0

    # claim 추출
    claim = extract_claim_from_added_lines(added_lines)
    if claim is None:
        print("SKIP — no 'N번째 hotfix-bypass:* family member' claim in added lines")
        return 0

    # raw post-append count
    raw_count = count_raw_hotfix_bypass_entries(registry_path)

    # parity check
    if claim == raw_count:
        print(f"PASS — parity verified: claim {claim} == raw post-append {raw_count}")
        return 0
    else:
        print(
            f"FAIL — claim {claim} != raw post-append {raw_count} "
            f"(description text drift detected, ADR-108 §결정 3)"
        )
        print(
            "[audit] label-registry-frozen-baseline-count-parity FAIL: "
            f"description claims '{claim}번째 hotfix-bypass:* family member' "
            f"but raw active count post-append = {raw_count}. "
            "Correct the description text before merging."
        )
        # warning tier (ADR-060 exit-code 3-tier) — exit 2 (advisory FAIL)
        return 2


if __name__ == "__main__":
    sys.exit(main())
