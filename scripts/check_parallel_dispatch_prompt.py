#!/usr/bin/env python3
"""scripts/check_parallel_dispatch_prompt.py

parallel-dispatch-protocol-v1 §8 mechanical enforcement — warning tier lint.

SSOT: docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md §4 + §8
Carrier ADR: ADR-064 Amendment 1 §결정 4 (mechanical_enforcement_actions[].action = parallel-dispatch-prompt-check)
Framework: ADR-060 evidence-enforceable promotion framework (warning tier)

Verification (5 항목):
  1. plan DAG batches list 박제 — `[Parallel Dispatch Hint]` 또는 `parallel_with` / `batch-` pattern
  2. pl_autonomous_parallel_authority required 박제 (disabled 차단 영역)
  3. sequential_mandate_reasons 6 enum 외 영역 발견 시 위반
  4. file_conflict_resolution_patterns 박제 — `same-file-different-method` 또는 `same-file-same-method` pattern
  5. worker_count <= worker_count_max (default 7) — count 명시 시 검증

Scope: docs/stories/**.md + spec/plan/PR description payload (CLI arg 또는 stdin).

Exit codes (ADR-060 Amendment 2 §결정 15 정합):
  0 = PASS (모든 검사 통과)
  1 = WARN (warning tier — 1+ 위반 detected, continue-on-error workflow 정합)
  2 = ERROR (script malformed input — meta level)

Bypass: hotfix-bypass:parallel-dispatch-prompt label (ADR-024 Amendment 3 정합).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows (cp949 console default) — Linux/macOS no-op.
# GitHub Actions ubuntu-latest 는 LANG=C.UTF-8 default 이므로 reconfigure no-op.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

SEQUENTIAL_MANDATE_ENUM = {
    "tdd_red_phase",
    "schema_migration",
    "adr_reservation_append",
    "fix_ledger_append",
    "sibling_sync_ordering",
    "marketplace_sync_ordering",
}

PARALLEL_AUTHORITY_PATTERN = re.compile(
    r"pl_autonomous_parallel_authority\s*[:=]\s*(['\"]?)(required|optional|disabled)\1",
    re.IGNORECASE,
)
DAG_HINT_PATTERN = re.compile(
    r"\[Parallel Dispatch Hint\]|parallel_with|batch-\d+\s*\(\s*병렬",
    re.IGNORECASE,
)
CONFLICT_RESOLUTION_PATTERN = re.compile(
    r"same-file-different-method|same-file-different-section|same-file-same-method",
    re.IGNORECASE,
)
# Match `sequential_mandate_reason: <value>` lines where value is a concrete enum literal
# (not the schema type declaration `list[str]` or `list[enum]`). Capture group = scalar string.
SEQUENTIAL_REASON_PATTERN = re.compile(
    r"sequential_mandate_reason[s]?\s*[:=]\s*(['\"]?)([a-z_]+(?:\s*,\s*[a-z_]+)*)\1\s*(?:#.*)?$",
    re.IGNORECASE | re.MULTILINE,
)
SEQUENTIAL_REASON_SCHEMA_BLACKLIST = {"list", "str", "enum", "any"}
WORKER_COUNT_PATTERN = re.compile(
    r"worker_count\s*[:=]\s*(\d+)",
    re.IGNORECASE,
)
WORKER_COUNT_MAX_DEFAULT = 7

# Hotfix bypass env var (ADR-040 Amendment 5 패턴 정합)
BYPASS_ENV = "BYPASS_PARALLEL_DISPATCH"


def check_file(path: Path) -> list[str]:
    """Return list of warning messages for a single file. Empty = PASS."""
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        warnings.append(f"{path}: read error — {exc}")
        return warnings

    # 1. plan DAG batches list 박제
    if not DAG_HINT_PATTERN.search(text):
        warnings.append(
            f"{path}: [WARN-1] plan DAG hint missing — `[Parallel Dispatch Hint]` 또는 "
            f"`parallel_with` / `batch-N (병렬)` pattern 부재 (registry §4.1)"
        )

    # 2. pl_autonomous_parallel_authority required
    match = PARALLEL_AUTHORITY_PATTERN.search(text)
    if match:
        value = match.group(2).lower()
        if value == "disabled":
            warnings.append(
                f"{path}: [WARN-2] pl_autonomous_parallel_authority=disabled — ratchet 차단 영역 "
                f"(ADR-058 §결정 5 sunset_justification 의무, registry §4.2)"
            )
        elif value == "optional":
            # F-006b: optional 영역 sunset_justification 의무 (ADR-058 §결정 5 / registry §4.2).
            # heuristic — 같은 file 영역 'sunset_justification' keyword 부재 시 [WARN-2-OPT] 발화.
            if "sunset_justification" not in text.lower():
                warnings.append(
                    f"{path}: [WARN-2-OPT] pl_autonomous_parallel_authority=optional — "
                    f"sunset_justification 3-tuple (metric / who / how) 박제 의무 부재 "
                    f"(ADR-058 §결정 5 / registry §4.2)"
                )
    elif "pl_autonomous_parallel_authority" in text.lower():
        warnings.append(
            f"{path}: [WARN-2] pl_autonomous_parallel_authority field malformed — "
            f"enum [required | optional | disabled] expected (registry §4.2)"
        )

    # 3. sequential_mandate_reasons 6 enum 외 영역 발견
    # NOTE: schema type declarations (`list[str]`, `enum`) 영역 false positive 회피 —
    # SEQUENTIAL_REASON_SCHEMA_BLACKLIST 토큰 차단.
    for reason_match in SEQUENTIAL_REASON_PATTERN.finditer(text):
        raw = reason_match.group(2)
        if not raw:
            continue
        for token in re.split(r"[,\s\"']+", raw):
            token = token.strip().lower()
            if not token or token in SEQUENTIAL_REASON_SCHEMA_BLACKLIST:
                continue
            if token not in SEQUENTIAL_MANDATE_ENUM:
                warnings.append(
                    f"{path}: [WARN-3] sequential_mandate_reason '{token}' = 6 enum 외 영역 "
                    f"(ADR-039 §결정 7 policy_violation_subdecision 발화 — registry §3 close-set)"
                )

    # 4. file_conflict_resolution_patterns 박제 (DAG hint 존재 시에만 의무)
    if DAG_HINT_PATTERN.search(text) and not CONFLICT_RESOLUTION_PATTERN.search(text):
        warnings.append(
            f"{path}: [WARN-4] file_conflict_resolution_patterns missing — "
            f"`same-file-different-method` / `same-file-different-section` / `same-file-same-method` "
            f"pattern 부재 (registry §4.4)"
        )

    # 5. worker_count <= worker_count_max
    for wc_match in WORKER_COUNT_PATTERN.finditer(text):
        count = int(wc_match.group(1))
        if count > WORKER_COUNT_MAX_DEFAULT:
            warnings.append(
                f"{path}: [WARN-5] worker_count={count} > worker_count_max default "
                f"{WORKER_COUNT_MAX_DEFAULT} (OperationalRiskArchitect §7.4.4 rate-limit consult "
                f"— registry §6.2)"
            )

    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        default=[],
        help="File paths to check. Empty = scan docs/stories/*.md",
    )
    args = parser.parse_args()

    if os.environ.get(BYPASS_ENV) == "1":
        print(f"[parallel-dispatch-prompt-check] BYPASS via {BYPASS_ENV}=1 — exit 0")
        return 0

    targets: list[Path] = []
    if args.paths:
        for p in args.paths:
            path = Path(p)
            if path.is_dir():
                targets.extend(path.rglob("*.md"))
            elif path.exists():
                targets.append(path)
            else:
                print(f"[parallel-dispatch-prompt-check] skip (not found): {p}", file=sys.stderr)
    else:
        stories = Path("docs/stories")
        if stories.is_dir():
            targets = list(stories.glob("*.md"))

    if not targets:
        print("[parallel-dispatch-prompt-check] no target files found — exit 0 (no scope)")
        return 0

    all_warnings: list[str] = []
    for target in targets:
        all_warnings.extend(check_file(target))

    if not all_warnings:
        print(
            f"[parallel-dispatch-prompt-check] PASS — {len(targets)} file(s) scanned, 0 warning"
        )
        return 0

    print(
        f"[parallel-dispatch-prompt-check] WARN — {len(all_warnings)} finding(s) across "
        f"{len(targets)} file(s):"
    )
    for w in all_warnings:
        print(f"  {w}")
    print()
    print(
        "SSOT: docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md §4 + §8 + §3"
    )
    print(
        "Bypass channel: hotfix-bypass:parallel-dispatch-prompt label (ADR-024 Amendment 3)"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
