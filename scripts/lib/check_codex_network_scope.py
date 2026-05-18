#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-963 / ADR-081 Amendment 4 §결정 D1.D / ADR-060 Amendment 14 §결정 28
#
# Codex worker network_scope mechanical layer — Python SSOT
#
# Purpose:
#   PR-time warning-tier lint for Codex worker spawn-prompt body.
#   Checks presence + enum membership of `network_scope:` field.
#   Boolean legacy `sandbox_network_required:` = advisory only (grace window).
#
# 4-tier network_scope enum (ADR-081 Amendment 4 D1.D SSOT):
#   offline                     — file-IO-only sandbox (most restrictive)
#   repo-fetch-only             — own-repo file-IO + own-repo git fetch
#   web-fetch                   — external HTTP / cross-repo / git fetch cross-repo
#   offline_substitution_declared — Codex CLI unavailable → Orchestrator substitution
#
# Graceful degradation step pair (a)(b)(c) — playbook §3.10.1-bis SSOT:
#   (a) detect → declare: detect fail-mode (api_missing/version_skew/enterprise_blocked)
#       → offline_substitution_declared declare before spawn
#   (b) verify-before-trust: ADR-070 §결정 D1 substitution scope 3-path enum ALL applied
#   (c) Story §10 [codex-sandbox-fallback: <FAIL_MODE>] marker + §14 network_scope_actual field
#
# Exit codes (ADR-060 Amendment 2 §결정 15 3-tier):
#   0 = PASS (field present + valid enum) or advisory-only (legacy boolean / unknown enum)
#   1 = WARNING (field absent or empty — warning tier, PR merge not blocked)
#   2 = META-ERROR (file not found / IO error)
#
# Self-exempt channels (ADR-060 Amendment 14 §결정 28.C):
#   - PR with hotfix-bypass:codex-sandbox-substitution label → caller handles bypass
#   - carrier_story argument == "CFP-963" → skip enforcement (self-exempt)
#
# SecurityArch TH-2 (§7.2): set +x guard equivalent — no PAT/token in output.
#   CODEFORGE_CROSS_REPO_PAT never echoed to stdout/stderr.
#
# ADR-061 §결정 1: this file is invoked via thin bash wrapper (check-codex-network-scope.sh)
# ADR-081 §D5 declaration-only retain: presence grep heuristic only (semantic = reviewer)

import re
import sys
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

# 4-tier network_scope enum SSOT (ADR-081 Amendment 4 D1.D)
VALID_ENUM_VALUES = frozenset({
    "offline",
    "repo-fetch-only",
    "web-fetch",
    "offline_substitution_declared",
})

# Boolean legacy field (ADR-081 Amendment 3 / grace window)
LEGACY_FIELD = "sandbox_network_required"

# network_scope field pattern (line-anchor presence grep, ADR-081 §D5 heuristic)
_NETWORK_SCOPE_RE = re.compile(
    r"^\s*network_scope\s*:\s*(.*)$",
    re.MULTILINE,
)
_LEGACY_BOOL_RE = re.compile(
    r"^\s*sandbox_network_required\s*:\s*(.*)$",
    re.MULTILINE,
)


def check_network_scope_presence(
    file_path: str,
    carrier_story: Optional[str] = None,
) -> dict:
    """
    Lint a Codex worker spawn-prompt body file for network_scope field.

    Returns a dict with:
        status:           "PASS" | "WARN" | "WARNING" | "EXEMPT" | "META-ERROR"
        exit_code:        0 | 1 | 2
        enum_value:       str or None (the detected enum value if PASS)
        advisory_markers: list[str] (advisory tags emitted)
        message:          str (human-readable summary)
    """
    advisory_markers: list = []
    result: dict = {
        "status": "PASS",
        "exit_code": EXIT_PASS,
        "enum_value": None,
        "advisory_markers": advisory_markers,
        "message": "",
    }

    # --- Self-exempt: carrier_story=CFP-963 (ADR-060 §결정 28.C) ---
    if carrier_story == "CFP-963":
        result["status"] = "PASS"
        result["exit_code"] = EXIT_PASS
        result["message"] = "[exempt] carrier_story=CFP-963 self-exempt — lint skipped"
        advisory_markers.append("[self-exempt: carrier_story=CFP-963]")
        return result

    # --- File read ---
    path = Path(file_path)
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        result["status"] = "META-ERROR"
        result["exit_code"] = EXIT_META_ERROR
        result["message"] = f"[meta-error] File not found: {file_path}"
        return result
    except OSError as exc:
        result["status"] = "META-ERROR"
        result["exit_code"] = EXIT_META_ERROR
        result["message"] = f"[meta-error] IO error reading {file_path}: {exc}"
        return result

    # --- Legacy boolean detection (ADR-081 Amendment 3 grace window) ---
    legacy_match = _LEGACY_BOOL_RE.search(content)
    if legacy_match:
        legacy_val = legacy_match.group(1).strip()
        advisory_markers.append(
            f"[legacy-boolean-detected: sandbox_network_required={legacy_val}]"
        )
        # Advisory mapping hint (ADR-081 Amendment 4 D1.D.legacy_grace_window)
        # false ↔ offline / true ↔ web-fetch (default broad path)
        if legacy_val in ("false", "False"):
            advisory_markers.append("[legacy-advisory: maps to offline]")
        elif legacy_val in ("true", "True"):
            advisory_markers.append("[legacy-advisory: maps to web-fetch]")

    # --- network_scope field detection ---
    ns_match = _NETWORK_SCOPE_RE.search(content)

    if ns_match is None:
        # Field absent — check if legacy boolean compensates
        if legacy_match:
            # Boolean present: advisory only (I-INV1 grace window, exit 0)
            result["status"] = "PASS"
            result["exit_code"] = EXIT_PASS
            result["message"] = (
                "[legacy-boolean-detected] network_scope field absent but "
                "sandbox_network_required present — advisory grace (ADR-081 Amendment 4 "
                "D1.D.legacy_grace_window). Migrate to network_scope: <enum>."
            )
            print(result["message"])
            for m in advisory_markers:
                print(m)
            return result
        # No field at all → WARNING (exit 1, I-INV3)
        result["status"] = "WARNING"
        result["exit_code"] = EXIT_WARNING
        result["message"] = (
            "[codex-network-scope-presence] WARNING: network_scope field absent in "
            "Codex worker spawn-prompt body. "
            "Add: network_scope: <offline|repo-fetch-only|web-fetch|offline_substitution_declared> "
            "(ADR-081 Amendment 4 §결정 D1.D). "
            "warning tier — PR merge not blocked (ADR-060 §결정 28)."
        )
        print(result["message"])
        return result

    # Field present — validate enum value
    enum_val = ns_match.group(1).strip()

    if not enum_val:
        # Empty value → WARNING (exit 1)
        result["status"] = "WARNING"
        result["exit_code"] = EXIT_WARNING
        result["message"] = (
            "[codex-network-scope-presence] WARNING: network_scope field is empty. "
            "Valid values: offline | repo-fetch-only | web-fetch | offline_substitution_declared "
            "(ADR-081 Amendment 4 §결정 D1.D)."
        )
        print(result["message"])
        return result

    if enum_val in VALID_ENUM_VALUES:
        # PASS
        result["status"] = "PASS"
        result["exit_code"] = EXIT_PASS
        result["enum_value"] = enum_val
        result["message"] = (
            f"[codex-network-scope-presence] PASS: network_scope={enum_val} "
            f"(valid 4-tier enum, ADR-081 Amendment 4 D1.D)."
        )
        # Emit coexist advisory if boolean also present
        if legacy_match:
            result["message"] += " [legacy-boolean-coexist: migrate sandbox_network_required]"
        print(result["message"])
        for m in advisory_markers:
            print(m)
        return result

    # Unknown enum value (I-INV2) → advisory only, exit 0 (ADR-068 I-3 unconditional guard)
    advisory_markers.append(f"[unknown-enum-value-advisory: network_scope={enum_val}]")
    result["status"] = "PASS"  # advisory-only = exit 0 (not blocking)
    result["exit_code"] = EXIT_PASS
    result["enum_value"] = enum_val
    result["message"] = (
        f"[codex-network-scope-presence] ADVISORY: network_scope={enum_val} is not a "
        f"recognized 4-tier enum value. "
        f"Valid: offline | repo-fetch-only | web-fetch | offline_substitution_declared "
        f"(ADR-081 Amendment 4 D1.D). "
        f"Advisory only — exit 0 (ADR-068 I-3 unconditional guard placement, grace window)."
    )
    print(result["message"])
    for m in advisory_markers:
        print(m)
    return result


# ---------------------------------------------------------------------------
# verify-before-trust reference (playbook §3.10.1-bis step (b))
# ADR-070 §결정 D1 substitution scope 3-path enum:
#   inline_orchestrator_verify / manual_substitution_declare / fallback_skip_with_marker
#
# Story §10 marker format (step (c)):
#   [codex-sandbox-fallback: <FAIL_MODE>]
#   network_scope_actual: <enum-value-or-null>
#
# FAIL_MODE enum (playbook L1349, 6 kinds — NOT new here, existing codified):
#   api_missing / version_skew / enterprise_blocked /
#   gh_api_network_blocked / manual_substitution_declared / inline_orchestrator_verify_only
#
# These constants are here as documentation / grep-presence anchors (TC-BAT-4b/4c).
# ---------------------------------------------------------------------------
SUBSTITUTION_PATH_ENUM = (
    "inline_orchestrator_verify",
    "manual_substitution_declare",
    "fallback_skip_with_marker",
)

FAIL_MODE_ENUM = (
    "api_missing",
    "version_skew",
    "enterprise_blocked",
    "gh_api_network_blocked",
    "manual_substitution_declared",
    "inline_orchestrator_verify_only",
)

STORY_10_MARKER_FORMAT = "[codex-sandbox-fallback: {FAIL_MODE}]"
LANE_EVIDENCE_FIELD = "network_scope_actual"


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main() -> int:
    """CLI entry point. Usage: python3 check_codex_network_scope.py <file> [--carrier-story CFP-NNN]"""
    args = sys.argv[1:]

    # Parse --carrier-story flag
    carrier_story: Optional[str] = None
    files = []
    i = 0
    while i < len(args):
        if args[i] == "--carrier-story" and i + 1 < len(args):
            carrier_story = args[i + 1]
            i += 2
        else:
            files.append(args[i])
            i += 1

    if not files:
        print(
            "Usage: python3 check_codex_network_scope.py <prompt-file> [--carrier-story CFP-NNN]",
            file=sys.stderr,
        )
        print(
            "Lints Codex worker spawn-prompt body for network_scope: <4-tier enum> field.",
            file=sys.stderr,
        )
        print(
            "Exit codes: 0=PASS | 1=WARNING | 2=META-ERROR (ADR-060 §결정 15 3-tier)",
            file=sys.stderr,
        )
        return EXIT_PASS  # no file = advisory pass (graceful degradation)

    # Process each file — worst exit code wins
    max_exit = EXIT_PASS
    for f in files:
        result = check_network_scope_presence(f, carrier_story=carrier_story)
        if result["exit_code"] > max_exit:
            max_exit = result["exit_code"]

    return max_exit


if __name__ == "__main__":
    sys.exit(main())
