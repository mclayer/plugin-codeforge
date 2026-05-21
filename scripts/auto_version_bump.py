#!/usr/bin/env python3
"""
scripts/auto_version_bump.py
CFP-1059-S6 — Epic close -> semver bump + git tag = Docker tag (ADR-061 외부 .py)

ADR-026 Amendment 6: Epic close -> post-merge-followup -> semver bump + git tag
ADR-063: git tag = Docker tag 1:1 (container name 1:1)

§11.6 idempotency:
  git tag 존재 시 skip (재실행 = no-op)
  변경 repo 만 bump (동일 Epic 재처리 시 동일 tag)

§7.5 secret: DOCKER_HUB_TOKEN = env var only (log 금지)
"""

import argparse
import subprocess
import sys
import re


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="semver bump + git tag")
    p.add_argument("--repo-path", required=True)
    p.add_argument("--current-version", required=True)
    p.add_argument("--bump-type", choices=["major", "minor", "patch"], default="minor")
    p.add_argument("--mock-git", default="0")
    return p.parse_args()


def bump_version(version: str, bump_type: str) -> str:
    """semver bump (major.minor.patch)"""
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version.lstrip("v"))
    if not match:
        raise ValueError(f"semver 형식 아님: {version}")
    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:
        return f"{major}.{minor}.{patch + 1}"


def tag_exists(repo_path: str, tag: str, mock_git: str) -> bool:
    """git tag 존재 여부 확인"""
    if mock_git == "1":
        # mock: TEST_TMP/repo git 실 확인
        try:
            result = subprocess.run(
                ["git", "-C", repo_path, "tag", "-l", tag],
                capture_output=True, text=True
            )
            return tag in result.stdout.strip()
        except Exception:
            return False
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "tag", "-l", tag],
            capture_output=True, text=True
        )
        return tag in result.stdout.strip()
    except Exception:
        return False


def create_tag(repo_path: str, tag: str, mock_git: str) -> None:
    """git tag 생성 (= Docker tag 1:1, ADR-063)"""
    if mock_git == "1":
        # mock: 실 git tag 생성
        subprocess.run(
            ["git", "-C", repo_path, "tag", tag],
            check=True, capture_output=True
        )
        print(f"[INFO] git tag 생성 (mock): {tag}")
        print(f"[INFO] Docker tag 1:1: {tag} [empirical-source: ADR-063 atomic invariant]")
        return
    subprocess.run(
        ["git", "-C", repo_path, "tag", tag],
        check=True
    )
    print(f"[INFO] git tag 생성: {tag}")
    print(f"[INFO] Docker tag 1:1: {tag} [empirical-source: ADR-063]")


def main() -> int:
    args = parse_args()

    new_version = bump_version(args.current_version, args.bump_type)
    tag = f"v{new_version}"

    print(f"[INFO] auto-version-bump: {args.current_version} -> {new_version} ({args.bump_type})")
    print(f"[INFO] tag: {tag}")

    # idempotency: tag 존재 시 skip
    if tag_exists(args.repo_path, tag, args.mock_git):
        print(f"[INFO] tag {tag} 이미 존재 — skip (idempotent no-op)")
        return 0

    # git tag 생성 (= Docker tag 1:1)
    try:
        create_tag(args.repo_path, tag, args.mock_git)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] git tag 생성 실패: {e}", file=sys.stderr)
        return 1

    print(f"[INFO] version bump 완료: {tag} (git tag = Docker tag = container name 1:1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
