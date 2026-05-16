#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-722 — Story per-section ownership mechanical lint
# ADR-060 Amendment 13 §결정 27 — warning-tier entry
# ADR-061 §결정 1 — external .py file (NO heredoc)
#
# Tier: warning (ADR-060 §결정 5 — 첫 도입 = warning mode).
# Exit code: ALWAYS 0 (warning-tier — never block PR).
#
# Algorithm: heading-anchored content slicing (NOT line-range — EC-2 line-shift resilience)
# → per-section diff → append-only vs destructive classification
# → proxy attribution for monopoly sections (§10/§13/§14/§10.5)
#
# References:
#   - Story CFP-722 §7.3 algorithm
#   - story-section-1-immutable.yml:52-53 (heading-anchored slice precedent)
#   - scripts/lib/check_story_section_9_typed.py (dir-absent/dep-absent exit-0 precedent)
#
# Usage:
#   python3 scripts/lib/check_story_section_ownership.py [story_file.md ...]
#   Reads --base-sha / --head-sha / context.json from env or args.
#
# For fixture-based testing, this script accepts direct text via
# internal classify() API.

import sys
import re
import json
import os
import subprocess
from pathlib import Path
from typing import Optional

# ─── Ownership Matrix (machine-readable SSOT cross-ref: docs/domain-knowledge/domain/governance-principle/lane-self-write-ownership-matrix.yaml) ─
# §1 = verbatim-invariant (story-section-1-immutable.yml — EXCLUDED from this lint, cross-ref only)
# §2, §4, §5, §6 = RequirementsPL owner
# §3, §7, §11 = ArchitectAgent/DesignLane owner
# §8, §8.5 = DeveloperPL owner
# §9 final-verdict = Orchestrator
# §10 FIX-Ledger = Orchestrator monopoly (CFP-32)
# §10.5 GitOps = Orchestrator monopoly
# §11 = PMO/ChangePlan SSOT (also ArchitectAgent)
# §13 = ArchitectPL monopoly
# §14 lane-evidence = Orchestrator monopoly (ADR-031)

# Section heading pattern: "## N." or "## N.M." at start of line
SECTION_HEADING_RE = re.compile(r"^##\s+(\d+(?:\.\d+)?)\.", re.MULTILINE)

# Monopoly sections — Orchestrator-only write (CFP-32 / ADR-031)
MONOPOLY_SECTIONS = {"10", "10.5", "13", "14"}

# §1 excluded — handled by story-section-1-immutable.yml
EXCLUDED_SECTIONS = {"1"}

# Section ownership map — lane plugin lanes that own each section
# Key = section number string, Value = list of owning lane identifiers
# "any" = any lane (Orchestrator-only writes are MONOPOLY, not any-lane)
SECTION_OWNERS: dict[str, list[str]] = {
    "2": ["requirements"],    # RequirementsPL
    "4": ["requirements"],
    "4.0": ["requirements"],
    "4.1": ["requirements"],
    "4.2": ["requirements"],
    "4.3": ["requirements"],
    "5": ["requirements"],
    "6": ["requirements"],
    "3": ["design"],          # ArchitectAgent / DesignLane
    "7": ["design"],
    "11": ["design", "pmo"],  # ArchitectAgent (change-plan) + PMO (retro)
    "8": ["develop"],         # DeveloperPL
    "8.5": ["develop"],
    "9": ["review", "design", "develop", "requirements"],  # various lanes write §9 subsections
    "12": ["pmo"],            # PMO (retro/retro-alert)
}

# Branch pattern to infer lane
LANE_BRANCH_RE = re.compile(r"cfp-\d+/(\w+)")

# Exempt protocol ID for carrier-Story bootstrap exemption (ADR-062)
EXEMPT_PROTOCOL_ID = "policy:lane-self-write-boundary-mechanical"

# ─── Frontmatter parsing ──────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter from markdown text. Returns empty dict if absent."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm_text = text[3:end].strip()
    result: dict = {}
    # Simple key: value parser (no full YAML needed for our keys)
    for line in fm_text.splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            k, _, v = line.partition(":")
            result[k.strip()] = v.strip()
    # Handle bootstrap_exempt_protocols list
    if "bootstrap_exempt_protocols:" in fm_text:
        protocols = []
        in_block = False
        for line in fm_text.splitlines():
            if line.strip().startswith("bootstrap_exempt_protocols:"):
                in_block = True
                continue
            if in_block:
                if line.startswith(" ") and line.strip().startswith("- "):
                    val = line.strip()[2:].strip().strip('"\'')
                    protocols.append(val)
                elif line and not line.startswith(" "):
                    break
        result["bootstrap_exempt_protocols"] = protocols
    return result

# ─── Section slicing ─────────────────────────────────────────────────────────

def slice_sections(text: str) -> dict[str, str]:
    """
    Slice markdown into per-section content using heading-anchored approach.
    Returns dict: section_num_str -> section_content (heading line excluded).
    §1 is included in slice but excluded from ownership check (cross-ref only).

    Uses heading regex match positions (NOT line numbers) — EC-2 line-shift resilient.
    """
    sections: dict[str, str] = {}
    matches = list(SECTION_HEADING_RE.finditer(text))
    for i, m in enumerate(matches):
        sec_num = m.group(1)
        # Content starts after the heading line
        content_start = m.end()
        # Find newline end of heading line
        nl = text.find("\n", m.start())
        if nl != -1:
            content_start = nl + 1
        # Content ends at next section heading start (or EOF)
        if i + 1 < len(matches):
            content_end = matches[i + 1].start()
        else:
            content_end = len(text)
        sections[sec_num] = text[content_start:content_end]
    return sections

# ─── Semantic normalization ───────────────────────────────────────────────────

def semantic_normalize(text: str) -> str:
    """
    Normalize text for semantic comparison:
    - Collapse whitespace-only changes
    - Normalize table column alignment (multiple spaces → single space)
    - Normalize link targets: [text](any-target) → [text](LINK)
    Returns normalized text for token-level comparison.
    """
    # Normalize link targets: keep text, remove target variation
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"[\1](LINK)", text)
    # Normalize table column padding (multiple spaces between | separators)
    text = re.sub(r"\|\s+", "| ", text)
    text = re.sub(r"\s+\|", " |", text)
    # Normalize blank lines (multiple blanks → single blank)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing whitespace per line
    lines = [l.rstrip() for l in text.splitlines()]
    return "\n".join(lines)

# ─── Token deletion detection ─────────────────────────────────────────────────

def has_token_deletion(base_content: str, head_content: str) -> bool:
    """
    Returns True if head_content semantically deletes tokens present in base_content.
    Uses normalized comparison.
    """
    base_norm = semantic_normalize(base_content).strip()
    head_norm = semantic_normalize(head_content).strip()
    if not base_norm:
        # Base was empty — no deletion possible
        return False
    # Check if any token in base_norm is missing from head_norm
    base_tokens = set(re.findall(r"\S+", base_norm))
    head_tokens = set(re.findall(r"\S+", head_norm))
    deleted = base_tokens - head_tokens
    # Filter out formatting-only tokens (pure separators, table pipes, etc.)
    meaningful_deleted = {t for t in deleted if not re.match(r"^[|:_\-*=\s]+$", t)}
    return bool(meaningful_deleted)

# ─── Lane attribution from branch / labels ────────────────────────────────────

def infer_lane(branch: str, labels: list[str]) -> Optional[str]:
    """
    Infer lane from branch name or PR labels.
    Returns lane identifier string or None if ambiguous.

    Orchestrator branches: cfp-NNN (flat, no /lane suffix)
    Lane plugin branches: cfp-NNN/<lane> (hierarchical, ADR-024 Amendment 1)
    """
    if not branch:
        return None
    m = LANE_BRANCH_RE.search(branch)
    if m:
        lane_part = m.group(1).lower()
        # Map common lane sub-directory names to canonical lane IDs
        lane_map = {
            "develop": "develop", "dev": "develop",
            "requirements": "requirements", "req": "requirements",
            "design": "design",
            "review": "review",
            "pmo": "pmo",
            "test": "test",
        }
        return lane_map.get(lane_part)
    # Flat branch (cfp-NNN without lane suffix) → Orchestrator pattern
    if re.match(r"^cfp-\d+$", branch):
        return "orchestrator"
    # Check labels for phase hints
    for label in labels:
        if "요구사항" in label:
            return "requirements"
        if "설계" in label and "리뷰" not in label:
            return "design"
        if "구현-리뷰" in label:
            return "review"
        if "구현" in label:
            return "develop"
    return None

# ─── Main classify function ───────────────────────────────────────────────────

class Violation:
    def __init__(self, section: str, kind: str, branch: str, detail: str = ""):
        self.section = section
        self.kind = kind    # "destructive-non-owner" or "monopoly-unauthorized"
        self.branch = branch
        self.detail = detail

    def to_warning_line(self) -> str:
        if self.kind == "destructive-non-owner":
            return (f"warning violation: §{self.section} destructively modified by "
                    f"non-owner lane (branch: {self.branch})")
        elif self.kind == "monopoly-unauthorized":
            return (f"warning violation: §{self.section} monopoly section modified without "
                    f"Orchestrator/delegate attribution (branch: {self.branch})")
        else:
            return f"warning violation: §{self.section} {self.detail} (branch: {self.branch})"


def classify(
    base_text: str,
    head_text: str,
    branch: str,
    labels: list[str],
    frontmatter: Optional[dict] = None,
) -> tuple[list[Violation], bool]:
    """
    Pure classifier function — no I/O.

    Returns:
        (violations, carrier_exempt)
        - violations: list[Violation] (empty = PASS)
        - carrier_exempt: bool — True if bootstrap-exempt short-circuit fired
    """
    if frontmatter is None:
        frontmatter = parse_frontmatter(head_text)

    # EC-4 / §7.6 carrier-Story bootstrap exemption FIRST (short-circuit)
    exempt_protocols = frontmatter.get("bootstrap_exempt_protocols", [])
    story_key = frontmatter.get("carrier_story", "")
    story_self_key = frontmatter.get("key", "")
    if (isinstance(exempt_protocols, list)
            and EXEMPT_PROTOCOL_ID in exempt_protocols
            and story_key == story_self_key
            and story_key):
        return [], True

    # EC-3 new-file: base empty → non-violation (skip)
    if not base_text or not base_text.strip():
        return [], False

    # Slice sections from both base and head
    base_sections = slice_sections(base_text)
    head_sections = slice_sections(head_text)

    # Infer lane from branch/labels
    lane = infer_lane(branch, labels)
    is_orchestrator = (lane == "orchestrator")

    violations: list[Violation] = []

    # Collect all section numbers that appear in either base or head (excluding §1)
    all_sections = set(base_sections.keys()) | set(head_sections.keys())
    all_sections -= EXCLUDED_SECTIONS  # §1 = cross-ref only

    for sec_num in sorted(all_sections, key=lambda x: [int(p) if p.isdigit() else p for p in x.split(".")]):
        base_content = base_sections.get(sec_num, "")
        head_content = head_sections.get(sec_num, "")

        # Skip sections not touched
        if semantic_normalize(base_content).strip() == semantic_normalize(head_content).strip():
            continue

        if sec_num in MONOPOLY_SECTIONS:
            # INV-DI-2: monopoly section — ANY mutation without Orchestrator/delegate = violation
            # Detection: content changed (we already know it changed from above)
            # Attribution: Orchestrator identity = flat branch cfp-NNN (no lane suffix)
            # OR label contains orchestrator-pattern
            if is_orchestrator:
                # Orchestrator or Orchestrator-owned delegate — PASS
                pass
            else:
                # Lane plugin or unknown attribution → violation
                violations.append(Violation(
                    section=sec_num,
                    kind="monopoly-unauthorized",
                    branch=branch,
                ))
        else:
            # INV-DI-1: lane-owned section — check if writer is the owner
            owners = SECTION_OWNERS.get(sec_num, [])
            if not owners:
                # Unknown section — skip (forward-compat)
                continue

            # Check if current lane is an owner
            if lane in owners:
                # Owner lane writing — check append-only vs destructive
                # Owner writes are allowed even if destructive (it's their section)
                pass
            elif is_orchestrator:
                # Orchestrator writing a lane-owned section — delegate pattern, PASS
                pass
            else:
                # Non-owner lane or unknown lane writing this section
                # Check for token deletion (INV-DI-1 predicate)
                if has_token_deletion(base_content, head_content):
                    violations.append(Violation(
                        section=sec_num,
                        kind="destructive-non-owner",
                        branch=branch,
                    ))

    return violations, False

# ─── File-based runner ────────────────────────────────────────────────────────

def get_git_file_content(sha: str, filepath: str) -> Optional[str]:
    """Get file content at a specific git SHA. Returns None if not found."""
    try:
        result = subprocess.run(
            ["git", "show", f"{sha}:{filepath}"],
            capture_output=True, text=True, encoding="utf-8",
        )
        if result.returncode != 0:
            return None
        return result.stdout
    except Exception:
        return None


def run_on_file(filepath: str, base_sha: str, head_sha: str,
                branch: str, labels: list[str]) -> list[Violation]:
    """Run lint on a single story file."""
    base_text = get_git_file_content(base_sha, filepath)
    head_text = get_git_file_content(head_sha, filepath)
    if base_text is None:
        # FM-2/FM-1: base not found → skip (new file or shallow clone)
        print(f"info: {filepath} base not found at {base_sha} — skip (new file or shallow clone)")
        return []
    if head_text is None:
        print(f"info: {filepath} head not found at {head_sha} — skip")
        return []
    violations, carrier_exempt = classify(base_text, head_text, branch, labels)
    if carrier_exempt:
        fm = parse_frontmatter(head_text)
        story_key = fm.get("key", filepath)
        print(f"notice carrier-exempt: {story_key} declares bootstrap_exempt_protocols "
              f"including {EXEMPT_PROTOCOL_ID} — ownership checks bypassed")
    return violations


def main(argv: Optional[list[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    # Check docs/stories dir (or pattern dir) existence
    stories_dir = Path("docs/stories")
    if not stories_dir.exists():
        # Try alternate pattern for monorepo
        alt_dirs = list(Path(".").glob("*/stories"))
        if not alt_dirs:
            print("info docs/stories not present - skip")
            sys.exit(0)

    # Parse CLI args
    base_sha = ""
    head_sha = ""
    branch = ""
    labels: list[str] = []
    path_pattern = "docs/stories/*.md"
    files: list[str] = []

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--base-sha" and i + 1 < len(argv):
            base_sha = argv[i + 1]; i += 2
        elif arg == "--head-sha" and i + 1 < len(argv):
            head_sha = argv[i + 1]; i += 2
        elif arg == "--pr-branch" and i + 1 < len(argv):
            branch = argv[i + 1]; i += 2
        elif arg == "--pr-labels" and i + 1 < len(argv):
            labels = argv[i + 1].split(","); i += 2
        elif arg == "--path-pattern" and i + 1 < len(argv):
            path_pattern = argv[i + 1]; i += 2
        elif arg == "--help":
            print("Usage: check_story_section_ownership.py [--base-sha SHA] [--head-sha SHA] "
                  "[--pr-branch BRANCH] [--pr-labels L1,L2] [--path-pattern GLOB]")
            sys.exit(0)
        elif not arg.startswith("-"):
            files.append(arg)
            i += 1
        else:
            i += 1

    # Fall back to env vars (GitHub Actions context)
    if not base_sha:
        base_sha = os.environ.get("GITHUB_BASE_SHA", "")
    if not head_sha:
        head_sha = os.environ.get("GITHUB_HEAD_SHA", "")
    if not branch:
        branch = os.environ.get("GITHUB_HEAD_REF", "")
    if not labels:
        labels_str = os.environ.get("PR_LABELS", "")
        labels = [l for l in labels_str.split(",") if l]

    # If no SHAs, try git log fallback for local run
    if not base_sha or not head_sha:
        try:
            res = subprocess.run(["git", "log", "--format=%H", "-2"],
                                  capture_output=True, text=True)
            shas = res.stdout.strip().splitlines()
            if len(shas) >= 2 and not head_sha:
                head_sha = shas[0]
            if len(shas) >= 2 and not base_sha:
                base_sha = shas[1]
        except Exception:
            pass

    if not files:
        # Discover story files from pattern
        from glob import glob
        files = sorted(glob(path_pattern, recursive=True))

    if not files:
        print(f"info: no story files matched pattern '{path_pattern}' — skip")
        sys.exit(0)

    if not base_sha or not head_sha:
        print("warning: base-sha or head-sha not provided — skip (cannot diff)")
        sys.exit(0)

    total_violations = 0
    for filepath in files:
        violations = run_on_file(filepath, base_sha, head_sha, branch, labels)
        for v in violations:
            print(v.to_warning_line())
            total_violations += 1

    print(f"check-story-section-ownership: files_scanned={len(files)} violations={total_violations}")
    # Warning tier — ALWAYS exit 0 (ADR-060 §결정 5)
    sys.exit(0)


if __name__ == "__main__":
    main()
