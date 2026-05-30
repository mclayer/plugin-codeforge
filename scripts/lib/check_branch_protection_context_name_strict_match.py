"""CFP-1849 — branch-protection-context-name-strict-match warning lint (Wave 2 mechanical wire).

main branch protection 의 required check context name 이 actual workflow job 표시명과
strict match 확인. 1차 occurrence: CFP-1808 (silent pass — `deploy-lane-presence` context
name mismatch → 모든 후속 PR pending/BLOCKED 가짜 CLEAN). CFP-1807 manual catch carrier 완료
후 본 CFP-1849 가 Wave 2 mechanical lint 로 promote (CFP-1807 retro F-001).

Logic (4 step):
  Step 1: gh api repos/<owner>/<repo>/branches/main/protection/required_status_checks
          --jq '.contexts[]' 로 required contexts list fetch
  Step 2: .github/workflows/*.yml 전수 scan — 각 file 안 `jobs.<job_id>.name:` value 추출
          (jobs.<id>.name 부재 시 job id 자체 fallback — gh checks 표시 동작 정합)
  Step 3: 각 required context name 에 대해:
            exact match in workflow job names → PASS
            substring match (context ⊂ job_name OR job_name ⊂ context) → PASS_SUBSTR
            no match → FAIL (warning emit)
  Step 4: mismatch table emit (markdown), exit 0 (warning-tier per ADR-060 §결정 5)

Tier: warning (ADR-060 §결정 5 default — first introduction, exit 0).
Owner ADR: ADR-024 §결정 6.A (branch protection policy) + ADR-060 (framework).
Bypass: `hotfix-bypass:branch-protection-context-name-strict-match` label.

Implementation notes:
  - ADR-061 Amendment 3 §결정 11 정합 — PyYAML safe_load (no regex parse), ReDoS-safe.
  - PyYAML 부재 시 fallback line-by-line scan (per-entry scan cap 200 line, anchored simple regex).
  - gh CLI = primary; CI 환경 `GH_TOKEN` env 의무 (workflow 가 주입).

Exit codes:
  0 — PASS (all contexts match) OR FAIL-as-warning (mismatch detected, markdown table)
  2 — usage error (gh CLI absent, workflow dir missing, etc.)

Usage:
  python scripts/lib/check_branch_protection_context_name_strict_match.py [--repo <slug>]
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Windows Git Bash / cp949 console — force UTF-8 stdout/stderr (CFP-418 evidence inherit).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

# Per-entry scan cap (ADR-061 Amendment 3 §결정 11 boundary detection).
DEFAULT_SCAN_CAP = 200

# Default repo slug (this wrapper plugin).
DEFAULT_REPO = "mclayer/plugin-codeforge"

# Workflow dir relative to repo root.
WORKFLOW_DIR = ".github/workflows"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="CFP-1849 branch protection context name strict match lint"
    )
    p.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPO),
        help=f"Repo slug (default: {DEFAULT_REPO} or $GITHUB_REPOSITORY)",
    )
    p.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent,
        help="Repo root path (default: 2 levels above script)",
    )
    p.add_argument(
        "--workflow-dir",
        default=None,
        help=f"Override workflow dir (default: <repo-root>/{WORKFLOW_DIR})",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress markdown header when no mismatch detected",
    )
    return p.parse_args()


def fetch_required_contexts(repo: str) -> Tuple[List[str], str]:
    """Fetch actual `main` branch protection required contexts via gh CLI.

    Returns `(contexts, status)` where status is one of:
      - "ok"
      - "not_protected" (404 — repos/.../branches/main/protection)
      - "error: <msg>" (other failures)
    """
    # Allow test override (bats fixture path — Windows .exe vs shim resolution).
    override_mode = os.environ.get("GH_CLI_BIN_OVERRIDE_MODE", "")
    if override_mode == "python_shim":
        shim_script = os.environ.get("GH_SHIM_SCRIPT", "")
        cmd = [
            sys.executable,
            shim_script,
            "api",
            f"repos/{repo}/branches/main/protection/required_status_checks",
            "--jq",
            ".contexts[]",
        ]
    else:
        gh_bin = os.environ.get("GH_CLI_BIN", "gh")
        cmd = [
            gh_bin,
            "api",
            f"repos/{repo}/branches/main/protection/required_status_checks",
            "--jq",
            ".contexts[]",
        ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except FileNotFoundError:
        return [], "error: gh CLI not available"
    except subprocess.TimeoutExpired:
        return [], "error: gh CLI timeout after 30s"

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        if "Not Found" in stderr or "404" in stderr or "HTTP 404" in stderr:
            return [], "not_protected"
        return [], f"error: {stderr[:200]}"

    stdout = result.stdout or ""
    contexts = [line.strip() for line in stdout.splitlines() if line.strip()]
    return contexts, "ok"


def extract_job_names_from_yaml(yaml_path: Path) -> List[Tuple[str, str]]:
    """Extract `(job_id, displayed_name)` pairs from a workflow yml.

    displayed_name = jobs.<job_id>.name if present else job_id (gh checks fallback).
    Uses PyYAML if available; otherwise line-by-line scan (ADR-061 Amd 3 §결정 11).
    """
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        yaml = None

    try:
        text = yaml_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    if yaml is not None:
        try:
            doc = yaml.safe_load(text)
        except yaml.YAMLError:
            doc = None
        if isinstance(doc, dict):
            jobs = doc.get("jobs") or {}
            if isinstance(jobs, dict):
                out: List[Tuple[str, str]] = []
                for job_id, job_spec in jobs.items():
                    if isinstance(job_spec, dict):
                        name = job_spec.get("name") or job_id
                        out.append((str(job_id), str(name)))
                    else:
                        out.append((str(job_id), str(job_id)))
                return out

    # Fallback line-by-line scan (ReDoS-safe per ADR-061 Amd 3 §결정 11).
    # Anchored simple regex, per-entry scan cap.
    lines = text.splitlines()
    out_lines: List[Tuple[str, str]] = []
    in_jobs = False
    current_job_id = ""
    current_job_name = ""
    job_indent = -1
    scanned = 0

    job_id_re = re.compile(r"^(\s*)([A-Za-z0-9_-]+):\s*$")
    name_re = re.compile(r"^(\s*)name:\s*(.+)$")

    for line in lines:
        scanned += 1
        if scanned > DEFAULT_SCAN_CAP * 5:  # workflow yml typically < 200 line
            break

        stripped = line.rstrip()

        # detect `jobs:` start
        if stripped == "jobs:":
            in_jobs = True
            continue

        if not in_jobs:
            continue

        # top-level (column 0) non-jobs key ends jobs section
        if stripped and not stripped.startswith(" ") and stripped != "jobs:":
            in_jobs = False
            continue

        # detect job id at indent level 2 (under `jobs:`)
        m = job_id_re.match(line)
        if m:
            indent = len(m.group(1))
            if indent == 2:
                # commit previous job
                if current_job_id:
                    out_lines.append(
                        (current_job_id, current_job_name or current_job_id)
                    )
                current_job_id = m.group(2)
                current_job_name = ""
                job_indent = indent
                continue

        # detect name within current job (indent > job_indent)
        if current_job_id:
            nm = name_re.match(line)
            if nm:
                indent = len(nm.group(1))
                if indent == job_indent + 2:
                    name_val = nm.group(2).strip().strip("'\"")
                    current_job_name = name_val

    # commit last job
    if current_job_id:
        out_lines.append((current_job_id, current_job_name or current_job_id))

    return out_lines


def collect_workflow_job_names(workflow_dir: Path) -> List[Tuple[str, str, str]]:
    """Scan workflow_dir for *.yml and return `(file_basename, job_id, displayed_name)`."""
    if not workflow_dir.is_dir():
        return []

    out: List[Tuple[str, str, str]] = []
    for yml_path in sorted(workflow_dir.glob("*.yml")):
        for job_id, name in extract_job_names_from_yaml(yml_path):
            out.append((yml_path.name, job_id, name))
    for yml_path in sorted(workflow_dir.glob("*.yaml")):
        for job_id, name in extract_job_names_from_yaml(yml_path):
            out.append((yml_path.name, job_id, name))
    return out


def classify_match(
    context: str, job_entries: List[Tuple[str, str, str]]
) -> Tuple[str, List[str]]:
    """Classify match level for a context.

    Returns `(level, candidates)`:
      level: "exact" / "substring" / "none"
      candidates: matched job descriptors (`<file>::<job_id> ['name']`)
    """
    exact: List[str] = []
    substr: List[str] = []
    for filename, job_id, name in job_entries:
        descriptor = f"{filename}::{job_id} '{name}'"
        if context == job_id or context == name:
            exact.append(descriptor)
        elif context in job_id or context in name or job_id in context or name in context:
            substr.append(descriptor)
    if exact:
        return "exact", exact
    if substr:
        return "substring", substr
    return "none", []


def emit_markdown(rows: List[dict], quiet: bool) -> None:
    """Emit warning markdown table."""
    no_match = [r for r in rows if r["level"] == "none"]
    substr_only = [r for r in rows if r["level"] == "substring"]

    if not no_match and not substr_only:
        if not quiet:
            print(
                "[branch-protection-context-name-strict-match] PASS — "
                "all required check contexts match workflow job names exactly."
            )
        return

    print("## branch-protection-context-name-strict-match (warning)")
    print()
    print(
        "ADR-024 §결정 6.A + ADR-060 — required check context name 이 actual workflow "
        "job 표시명과 strict match 검증."
    )
    print()

    if no_match:
        print("### FAIL — no matching workflow job (silent BLOCKED risk)")
        print()
        print("| context | risk |")
        print("|---------|------|")
        for r in no_match:
            print(
                f"| `{r['context']}` | required check name 이 어떤 workflow job 과도 "
                f"match 되지 않음 — 영원히 pending → PR merge 영구 차단 OR silent skip |"
            )
        print()

    if substr_only:
        print("### WARN — substring match only (verify intent)")
        print()
        print("| context | candidate job(s) |")
        print("|---------|------------------|")
        for r in substr_only:
            cands = "; ".join(f"`{c}`" for c in r["candidates"])
            print(f"| `{r['context']}` | {cands} |")
        print()

    print(
        "_Bypass: attach `hotfix-bypass:branch-protection-context-name-strict-match` "
        "label with `### Bypass reason` PR body section (ADR-024 Amendment 16 §결정 6.A.8)._"
    )


def main() -> int:
    args = parse_args()

    workflow_dir = (
        Path(args.workflow_dir)
        if args.workflow_dir
        else (args.repo_root / WORKFLOW_DIR)
    )
    if not workflow_dir.is_dir():
        print(
            f"[error] workflow dir not found: {workflow_dir}", file=sys.stderr
        )
        return 2

    contexts, status = fetch_required_contexts(args.repo)
    if status == "error: gh CLI not available":
        print("[skip] gh CLI not available, lint skipped (warning-tier)", file=sys.stderr)
        return 0
    if status.startswith("error"):
        print(f"[skip] {status}, lint skipped (warning-tier)", file=sys.stderr)
        return 0
    if status == "not_protected":
        print(
            f"[info] {args.repo}: main branch not protected, lint skipped",
            file=sys.stderr,
        )
        return 0

    job_entries = collect_workflow_job_names(workflow_dir)
    if not job_entries:
        print(
            f"[warn] no workflow jobs found in {workflow_dir}", file=sys.stderr
        )
        return 0

    rows = []
    for ctx in contexts:
        level, cands = classify_match(ctx, job_entries)
        rows.append({"context": ctx, "level": level, "candidates": cands})

    emit_markdown(rows, args.quiet)
    # warning-tier: always exit 0 (ADR-060 §결정 5 default).
    return 0


if __name__ == "__main__":
    sys.exit(main())
