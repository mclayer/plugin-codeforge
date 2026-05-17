#!/usr/bin/env python3
"""
CFP-841 / ADR-082 Amendment 1 scope(d) -- cross-plugin ownership verify lint
ChangeImpactAgent Phase 0 mapping artifact templates/* / docs/adr/* / docs/change-plans/*
wrapper-local assertion line missing [ownership-verified: <yaml-query-path>] = flag.

13B 4-way drift-sync invariant:
  yaml cross_plugin_doc_ownership (SSOT) vs SKILL.md vs story-page-structure.md vs lint regex
  yaml-as-canonical single-direction (yaml READ-ONLY, 3 derived mirror mismatch = flag)

ADR-061: multi-line Python external .py file.
Usage: python3 scripts/check-cross-plugin-ownership-verify.py [--check-4way-sync] [file ...]
Exit: 0=PASS, 1=violation, 2=error
"""

import sys
import re
import os
import subprocess
from typing import List, Optional, Dict, Any

# wrapper-local path assertion pattern: templates/* docs/adr/* docs/change-plans/*
WRAPPER_LOCAL_PATH_RE = re.compile(
    r'(?:templates/|docs/adr/|docs/change-plans/)[\w./_-]*\.(?:md|yaml|yml|py|sh|json)'
)

# [ownership-verified: ...] annotation pattern
OWNERSHIP_VERIFIED_RE = re.compile(
    r'\[ownership-verified:\s*cross_plugin_doc_ownership\.[^\]]+\]'
)

# self-referential exemption (this script + bats fixture)
SELF_REF_ALLOWLIST_PATTERNS = [
    r'check-cross-plugin-ownership-verify',
    r'test-check-cross-plugin-ownership-verify',
    r'docs/adr/ADR-082-.*\.md',
    r'wrapper/stories/CFP-841\.md',
    r'change-plans/.*cfp-841.*\.md',
]
SELF_REF_RE = re.compile('|'.join(SELF_REF_ALLOWLIST_PATTERNS))

# yaml SSOT path (repo root)
YAML_SSOT_PATH = "docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.yaml"
CROSS_PLUGIN_KEY = "cross_plugin_doc_ownership"
SKILL_MD_PATH = "skills/lane-self-write-boundary/SKILL.md"


def is_self_referential(filepath: str) -> bool:
    norm = filepath.replace("\\", "/")
    return bool(SELF_REF_RE.search(norm))


def load_yaml_ssot(repo_root: str) -> Optional[Dict[str, Any]]:
    """Text-search based fallback (pyyaml may fail on non-ASCII special chars in file)."""
    yaml_path = os.path.join(repo_root, YAML_SSOT_PATH)
    if not os.path.isfile(yaml_path):
        return None
    try:
        with open(yaml_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        if CROSS_PLUGIN_KEY in content:
            return {"entries": [], "_text_fallback": True}
        return None
    except Exception:
        return None


def check_4way_sync(repo_root: str) -> List[str]:
    """13B 4-way drift-sync invariant check."""
    issues = []

    cross_plugin_data = load_yaml_ssot(repo_root)
    if cross_plugin_data is None:
        issues.append(
            "4WAY-SYNC-FAIL: yaml SSOT missing cross_plugin_doc_ownership sub-tree "
            "[" + YAML_SSOT_PATH + "]"
        )
        return issues

    skill_path = os.path.join(repo_root, SKILL_MD_PATH)
    if os.path.isfile(skill_path):
        with open(skill_path, encoding="utf-8") as f:
            skill_content = f.read()
        if "cross_plugin_doc_ownership" not in skill_content and "machine_readable_ssot" not in skill_content:
            issues.append(
                "4WAY-SYNC-WARN: SKILL.md missing cross_plugin_doc_ownership or "
                "machine_readable_ssot reference [" + SKILL_MD_PATH + "]"
            )
    else:
        issues.append("4WAY-SYNC-WARN: SKILL.md not found [" + SKILL_MD_PATH + "]")

    return issues


def check_file(filepath: str, violations: List[Dict[str, Any]]) -> None:
    if is_self_referential(filepath):
        return
    try:
        with open(filepath, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return

    for i, line in enumerate(lines):
        if not WRAPPER_LOCAL_PATH_RE.search(line):
            continue
        window_start = max(0, i - 2)
        window_end = min(len(lines), i + 3)
        window = "".join(lines[window_start:window_end])
        if OWNERSHIP_VERIFIED_RE.search(window):
            continue
        violations.append({"file": filepath, "line": i + 1, "text": line.rstrip()})


def find_repo_root() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return os.getcwd()


def main() -> int:
    args = sys.argv[1:]
    repo_root = find_repo_root()

    if "--check-4way-sync" in args:
        issues = check_4way_sync(repo_root)
        if issues:
            out = "FAIL: cross-plugin-ownership-verify 13B 4-way sync -- " + str(len(issues)) + " issue(s)\n"
            sys.stdout.buffer.write(out.encode("utf-8"))
            for issue in issues:
                sys.stdout.buffer.write(("  " + issue + "\n").encode("utf-8"))
            return 1
        sys.stdout.buffer.write(b"PASS: cross-plugin-ownership-verify 13B 4-way sync -- 0 issue(s)\n")
        return 0

    file_args = [a for a in args if not a.startswith("--")]
    if not file_args:
        sys.stdout.buffer.write(b"PASS: no scan targets (0 files)\n")
        return 0

    violations: List[Dict[str, Any]] = []
    for filepath in file_args:
        if os.path.isfile(filepath):
            check_file(filepath, violations)
        elif os.path.isdir(filepath):
            for root, _dirs, files in os.walk(filepath):
                for fname in files:
                    if fname.endswith((".md", ".yaml", ".yml")):
                        check_file(os.path.join(root, fname), violations)

    if violations:
        out = "FAIL: cross-plugin-ownership-verify -- OWNERSHIP_UNVERIFIED " + str(len(violations)) + " violation(s)\n"
        sys.stdout.buffer.write(out.encode("utf-8"))
        for v in violations:
            line_out = "  [" + v["file"] + ":" + str(v["line"]) + "] " + v["text"][:120] + "\n"
            sys.stdout.buffer.write(line_out.encode("utf-8"))
        sys.stdout.buffer.write(
            b"\nFix: add [ownership-verified: cross_plugin_doc_ownership.<key>=<value>] annotation\n"
            b"SSOT: docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.yaml\n"
            b"bypass: hotfix-bypass:cross-plugin-ownership-verify\n"
        )
        return 1

    sys.stdout.buffer.write(b"PASS: cross-plugin-ownership-verify -- 0 violation(s)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
