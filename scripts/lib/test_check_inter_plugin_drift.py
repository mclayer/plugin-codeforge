#!/usr/bin/env python3
# test_check_inter_plugin_drift.py — CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A
# SSOT extracted from test-check-inter-plugin-drift.sh build_baseline_fixture() PYEOF heredoc.
#
# Purpose: Build drift=0 baseline fixture from current sibling state.
#          canonical fixture = sibling raw content (양쪽 normalize 가 동일 적용되므로 drift 0).
#
# Usage:   python3 scripts/lib/test_check_inter_plugin_drift.py <fix_dir>
# Args:    fix_dir — destination directory for fixture files
# CWD:     Must be repo root (docs/inter-plugin-contracts/MANIFEST.yaml 기준).
# Exit:    0=ok, 1=error.
import pathlib
import sys

try:
    import yaml
except ImportError:
    print("test_check_inter_plugin_drift: pyyaml 미설치 — fixture 생성 skip", file=sys.stderr)
    sys.exit(0)


def build_baseline_fixture(fix_dir_str: str) -> None:
    fix_dir = pathlib.Path(fix_dir_str)
    manifest = yaml.safe_load(
        pathlib.Path("docs/inter-plugin-contracts/MANIFEST.yaml").read_text(encoding="utf-8")
    )
    for contract in (manifest or {}).get("contracts", []):
        repo = contract.get("canonical_repo", "")
        repo_basename = repo.split("/")[-1]
        for fent in contract.get("files", []):
            fname = fent.get("file", "")
            status = fent.get("status", "")
            if status != "Active":
                continue
            sibling = pathlib.Path("docs/inter-plugin-contracts") / fname
            if not sibling.exists():
                continue
            # canonical fixture = sibling raw content
            # (양쪽 normalize 가 동일 적용되므로 drift 0)
            target_dir = fix_dir / repo_basename
            target_dir.mkdir(parents=True, exist_ok=True)
            (target_dir / fname).write_text(
                sibling.read_text(encoding="utf-8"), encoding="utf-8"
            )


def main() -> int:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <fix_dir>", file=sys.stderr)
        return 1
    fix_dir_str = sys.argv[1]
    try:
        build_baseline_fixture(fix_dir_str)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
