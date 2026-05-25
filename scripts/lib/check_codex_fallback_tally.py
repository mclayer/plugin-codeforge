#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1368 / ADR-052 Amendment 14 — codex-fallback-subclass-tally mechanical wire
# ADR-060 Amendment 14 §결정 28 — dual-binding enforcement (declaration: ADR-052/070/081, enforcement: ADR-060)
#
# Purpose:
#   PR-time + cron warning-tier lint for Codex worker fail-mode enum accumulation.
#   Tallies [codex-sandbox-fallback: <fail-mode>] and
#   [codex-substitution-scope-declared: <scope-enum>] markers from Story §10.
#   Per-enum count >= threshold (3) → escalation_action: escalate_user (ADR-045 §D-9).
#
# 9 fail-mode enum closed-set SSOT (ADR-052 §A3 line 812 + ADR-070 §결정 D1):
#   api_missing / version_skew / enterprise_blocked / gh_api_network_blocked /
#   manual_substitution_declared / inline_orchestrator_verify_only /
#   subagent_recursion_blocked / dispatch_stall_or_stream_timeout /
#   codex_truncated_no_verdict
#
# CodeQL ReDoS guard (CFP-1497 sentinel + ADR-061 Amendment 3):
#   literal string containment ONLY — no regex on untrusted input.
#   Line-by-line parse + literal prefix/suffix strip.
#
# ADR-013 §1 atomic rename pattern (local repo write):
#   os.replace(tmp_path, jsonl_path) — POSIX atomic rename guarantee.
#   No cross-repo write (wrapper local only, Wave 1 scope).
#
# Exit codes (ADR-060 §결정 15 3-tier):
#   0 = PASS
#   1 = WARNING (threshold breach OR invalid enum detected — warning tier, PR merge not blocked)
#   2 = META-ERROR (file not found / IO error)
#
# Self-exempt channels:
#   - HOTFIX_BYPASS_CODEX_FALLBACK_TALLY=1 env → skip all checks, exit 0 with [BYPASS] marker
#   - --carrier-story CFP-1368 → skip enforcement (self-carrier bootstrap-exempt)
#
# SecurityArch TH-2: set +x equivalent — CODEFORGE_CROSS_REPO_PAT never echoed.
#
# ADR-061 §결정 1: this file is invoked via thin bash wrapper (check-codex-fallback-tally.sh)
# ADR-081 §D5 declaration-only retain: presence grep heuristic only (semantic = reviewer)

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# Windows console (cp949) 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Exit code 3-tier (ADR-060 §결정 15)
EXIT_PASS = 0
EXIT_WARNING = 1
EXIT_META_ERROR = 2

# Per-enum threshold (ADR-045 §D-9 strict, per-enum sub-domain self-tuned)
THRESHOLD = 3

# KST timezone offset (ADR-079 KST display normative)
KST = timezone(timedelta(hours=9))

# 9 fail-mode enum closed-set SSOT (ADR-052 §A3 + ADR-070 §결정 D1)
VALID_FAIL_MODE_ENUM = frozenset({
    "api_missing",
    "version_skew",
    "enterprise_blocked",
    "gh_api_network_blocked",
    "manual_substitution_declared",
    "inline_orchestrator_verify_only",
    "subagent_recursion_blocked",
    "dispatch_stall_or_stream_timeout",
    "codex_truncated_no_verdict",
})

# Substitution path 3-enum SSOT (ADR-052 Amendment 8)
VALID_SUBSTITUTION_PATH_ENUM = frozenset({
    "inline_orchestrator_verify",
    "manual_substitution_declare",
    "fallback_skip_with_marker",
})

# Marker prefixes (comment-prefix-registry-v1 v1.5 SSOT)
FALLBACK_MARKER_PREFIX = "[codex-sandbox-fallback: "
SUBSTITUTION_MARKER_PREFIX = "[codex-substitution-scope-declared: "
MARKER_SUFFIX = "]"

# Self-carrier exempt (bootstrap-exempt, ADR-062 §결정 8 + CFP-963 precedent)
SELF_EXEMPT_CARRIER = "CFP-1368"


def _parse_fallback_markers(content: str) -> list[dict]:
    """
    CodeQL ReDoS guard (CFP-1497 + ADR-061 Amd 3):
    Literal string containment ONLY — no regex on untrusted content.
    Line-by-line parse with literal prefix/suffix strip.
    """
    results = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith(FALLBACK_MARKER_PREFIX) and stripped.endswith(MARKER_SUFFIX):
            # literal extraction — no regex
            inner = stripped[len(FALLBACK_MARKER_PREFIX): -len(MARKER_SUFFIX)].strip()
            results.append({
                "marker_type": "codex-sandbox-fallback",
                "value": inner,
                "raw_line": stripped,
            })
    return results


def _parse_substitution_markers(content: str) -> list[dict]:
    """
    CodeQL ReDoS guard: literal string containment only.
    """
    results = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith(SUBSTITUTION_MARKER_PREFIX) and stripped.endswith(MARKER_SUFFIX):
            inner = stripped[len(SUBSTITUTION_MARKER_PREFIX): -len(MARKER_SUFFIX)].strip()
            results.append({
                "marker_type": "codex-substitution-scope-declared",
                "value": inner,
                "raw_line": stripped,
            })
    return results


def _read_jsonl_tally(jsonl_path: Path) -> dict[str, int]:
    """
    Read existing jsonl file and compute per-enum tally.
    Returns dict: {enum_value: count}
    """
    tally: dict[str, int] = {}
    if not jsonl_path.exists():
        return tally
    try:
        content = jsonl_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return tally
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
            enum_val = row.get("enum_value", "")
            if enum_val:
                tally[enum_val] = tally.get(enum_val, 0) + 1
        except (json.JSONDecodeError, ValueError):
            continue
    return tally


def _atomic_append_jsonl(jsonl_path: Path, new_rows: list[dict]) -> None:
    """
    ADR-013 §1 atomic rename pattern — POSIX guarantee.
    Write to tmp file → os.replace(tmp, jsonl_path).
    Handles concurrent writes safely (last writer wins per atomic rename guarantee).
    """
    if not new_rows:
        return

    # Read existing content
    existing_lines: list[str] = []
    if jsonl_path.exists():
        try:
            existing_lines = [
                line for line in jsonl_path.read_text(encoding="utf-8", errors="replace").splitlines()
                if line.strip()
            ]
        except OSError:
            pass

    # Append new rows
    new_lines = [json.dumps(row, ensure_ascii=False) for row in new_rows]
    all_lines = existing_lines + new_lines

    # Write to tmp then atomic rename (ADR-013 §1)
    parent = jsonl_path.parent
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(parent),
        delete=False,
        suffix=".tmp",
    ) as tmp_f:
        tmp_path = tmp_f.name
        for line in all_lines:
            tmp_f.write(line + "\n")

    # POSIX atomic rename — os.replace is cross-platform best-effort
    os.replace(tmp_path, str(jsonl_path))


def run_tally_check(
    jsonl_file: str,
    story_file: str,
    carrier_story: Optional[str] = None,
    dry_run: bool = False,
) -> dict:
    """
    Main tally check logic.

    Returns:
        status:           "PASS" | "WARNING" | "EXEMPT" | "META-ERROR"
        exit_code:        0 | 1 | 2
        tally:            dict[enum_value, count] (cumulative including new rows)
        new_rows:         int
        invalid_enums:    list[str]
        threshold_breached: list[str]
        advisory_markers: list[str]
        message:          str
    """
    advisory_markers: list[str] = []
    result: dict = {
        "status": "PASS",
        "exit_code": EXIT_PASS,
        "tally": {},
        "new_rows": 0,
        "invalid_enums": [],
        "threshold_breached": [],
        "advisory_markers": advisory_markers,
        "message": "",
    }

    # --- Self-exempt: HOTFIX_BYPASS env (ADR-068 I-3 unconditional guard) ---
    bypass_env = os.environ.get("HOTFIX_BYPASS_CODEX_FALLBACK_TALLY", "").strip()
    if bypass_env == "1":
        result["status"] = "PASS"
        result["exit_code"] = EXIT_PASS
        result["message"] = "[BYPASS] HOTFIX_BYPASS_CODEX_FALLBACK_TALLY=1 — tally check skipped"
        advisory_markers.append("[bypass-active: HOTFIX_BYPASS_CODEX_FALLBACK_TALLY=1]")
        print(result["message"])
        return result

    # --- Self-carrier exempt (bootstrap-exempt, CFP-963 precedent) ---
    if carrier_story == SELF_EXEMPT_CARRIER:
        result["status"] = "PASS"
        result["exit_code"] = EXIT_PASS
        result["message"] = f"[exempt] carrier_story={SELF_EXEMPT_CARRIER} self-exempt — tally check skipped"
        advisory_markers.append(f"[self-exempt: carrier_story={SELF_EXEMPT_CARRIER}]")
        return result

    # --- File read: story file ---
    story_path = Path(story_file)
    try:
        story_content = story_path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        result["status"] = "META-ERROR"
        result["exit_code"] = EXIT_META_ERROR
        result["message"] = f"[meta-error] Story file not found: {story_file}"
        return result
    except OSError as exc:
        result["status"] = "META-ERROR"
        result["exit_code"] = EXIT_META_ERROR
        result["message"] = f"[meta-error] IO error reading {story_file}: {exc}"
        return result

    # --- Parse markers from story file ---
    fallback_markers = _parse_fallback_markers(story_content)
    substitution_markers = _parse_substitution_markers(story_content)

    # --- Validate enum membership (9-enum closed-set check) ---
    invalid_enums: list[str] = []
    valid_markers: list[dict] = []
    for marker in fallback_markers:
        enum_val = marker["value"]
        if enum_val in VALID_FAIL_MODE_ENUM:
            valid_markers.append(marker)
        else:
            invalid_enums.append(enum_val)
            advisory_markers.append(
                f"[unknown-enum: {enum_val} — Out-of-scope or typo "
                f"(9-enum closed-set SSOT: ADR-052 §A3 + ADR-070 §결정 D1)]"
            )

    result["invalid_enums"] = invalid_enums

    # --- jsonl path ---
    jsonl_path = Path(jsonl_file)

    # --- Read existing tally ---
    existing_tally = _read_jsonl_tally(jsonl_path)

    # --- Build new rows to append ---
    now_kst = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S+09:00")
    new_rows: list[dict] = []
    if not dry_run:
        for marker in valid_markers:
            # Build jsonl row (6-field schema, Change Plan §2.2 SSOT)
            row = {
                "enum_value": marker["value"],
                "occurred_at": now_kst,
                "story_key": story_path.stem if story_path.stem else "UNKNOWN",
                "dispatch_task_id": "",  # caller may enrich via --dispatch-task-id
                "substitution_path": "",  # enriched from substitution marker if available
                "evidence": marker["raw_line"],
            }
            # Try to correlate substitution path marker
            if substitution_markers:
                sub_val = substitution_markers[0]["value"]
                if sub_val in VALID_SUBSTITUTION_PATH_ENUM:
                    row["substitution_path"] = sub_val
            new_rows.append(row)

    # --- Atomic append (ADR-013 §1 os.replace pattern) ---
    if new_rows:
        _atomic_append_jsonl(jsonl_path, new_rows)

    # --- Compute updated tally ---
    updated_tally = dict(existing_tally)
    for row in new_rows:
        enum_val = row["enum_value"]
        updated_tally[enum_val] = updated_tally.get(enum_val, 0) + 1

    result["tally"] = updated_tally
    result["new_rows"] = len(new_rows)

    # --- Threshold check (per-enum count >= THRESHOLD → escalate_user, ADR-045 §D-9) ---
    threshold_breached: list[str] = []
    for enum_val, count in updated_tally.items():
        if count >= THRESHOLD:
            threshold_breached.append(f"{enum_val}={count}")
            advisory_markers.append(
                f"[threshold-breach: {enum_val} count={count} >= {THRESHOLD} "
                f"(escalation_action: escalate_user, ADR-045 §D-9)]"
            )
    result["threshold_breached"] = threshold_breached

    # --- Determine final status ---
    has_warning = bool(invalid_enums) or bool(threshold_breached)

    if has_warning:
        result["status"] = "WARNING"
        result["exit_code"] = EXIT_WARNING
        parts = []
        if invalid_enums:
            parts.append(f"invalid enum(s): {', '.join(invalid_enums)}")
        if threshold_breached:
            parts.append(f"threshold breach: {', '.join(threshold_breached)}")
        result["message"] = "[WARNING] codex-fallback-tally: " + "; ".join(parts)
    else:
        result["status"] = "PASS"
        result["exit_code"] = EXIT_PASS
        tally_summary = ", ".join(f"{k}={v}" for k, v in sorted(updated_tally.items())) or "empty"
        result["message"] = f"[PASS] codex-fallback-tally: {tally_summary} | new_rows={len(new_rows)}"

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CFP-1368 codex-fallback-subclass-tally mechanical lint"
    )
    parser.add_argument(
        "--jsonl-file",
        default="docs/kpi/codex-fallback-tally.jsonl",
        help="Path to the jsonl event log file (default: docs/kpi/codex-fallback-tally.jsonl)",
    )
    parser.add_argument(
        "--story-file",
        required=True,
        help="Path to the Story §10 file to scan for markers",
    )
    parser.add_argument(
        "--carrier-story",
        default=None,
        help="Carrier Story key (CFP-NNN) for self-exempt bootstrap check",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Dry-run mode — parse + tally but do not append to jsonl",
    )

    args = parser.parse_args()

    result = run_tally_check(
        jsonl_file=args.jsonl_file,
        story_file=args.story_file,
        carrier_story=args.carrier_story,
        dry_run=args.dry_run,
    )

    # Print result summary
    print(result["message"])
    for marker in result.get("advisory_markers", []):
        print(marker)

    if result.get("threshold_breached"):
        print("[ACTION-REQUIRED] Per-enum threshold breach detected.")
        print("  → escalation_action: escalate_user (ADR-045 §D-9)")
        print("  → Create GitHub Issue to track systemic class determination.")
        for breach in result["threshold_breached"]:
            print(f"     breach: {breach}")

    if result.get("invalid_enums"):
        print("[WARNING] Unknown enum value(s) detected (Out-of-scope or typo):")
        for inv_enum in result["invalid_enums"]:
            print(f"  unknown enum value: {inv_enum}")
            print(f"  → 9-enum closed-set SSOT: ADR-052 §A3 + ADR-070 §결정 D1")
            print(f"  → If this is the 10th enum candidate, defer to separate follow-up CFP.")

    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
