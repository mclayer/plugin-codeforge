#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-1412 / ADR-081 Amendment 8 §결정 D9 / ADR-060 §결정 28
#
# Codex worker origin/main fetch directive mechanical layer — Python SSOT
#
# Purpose:
#   PR-time warning-tier lint for Codex worker spawn-prompt body.
#   Checks presence of [ORIGIN-MAIN-DIRECTIVE] block OR valid fallback marker.
#   Either directive block OR valid fallback marker → PASS.
#   Both absent OR invalid fallback enum → WARNING (exit 1).
#
# [ORIGIN-MAIN-DIRECTIVE] block presence (ADR-081 Amendment 8 D9 SSOT):
#   The Codex worker spawn prompt body must contain one of:
#     (a) [ORIGIN-MAIN-DIRECTIVE] block (marker line presence heuristic)
#     (b) [origin-main-directive-fallback: <fallback-enum>] marker
#         fallback-enum closed-set 3 values:
#           network_scope_offline
#           legacy_prompt_format
#           intentional_working_tree_verify
#
# Why:
#   Codex worker spawn prompts that lack origin/main fetch directive may produce
#   stale-baseline findings (CFP-1333 5/5 FP evidence — ADR-081 Amendment 8
#   §결정 D9 enforcement carrier). Lint ensures directive or declared fallback
#   is present in every Codex worker spawn prompt body file.
#
# Exit codes (ADR-060 Amendment 2 §결정 15 3-tier):
#   0 = PASS (directive block present, OR valid fallback marker present)
#   1 = WARNING (both absent, or fallback with invalid enum value)
#   2 = META-ERROR (file not found / IO error)
#
# Bypass channel (ADR-060 §결정 28.C):
#   BYPASS_CODEX_ORIGIN_MAIN_DIRECTIVE=1 env → silent skip + audit trail (exit 0)
#   PR with hotfix-bypass:codex-origin-main-directive-check label → caller handles
#
# SecurityArch TH-2 (§7.2): set +x guard equivalent — no PAT/token in output.
#   CODEFORGE_CROSS_REPO_PAT never echoed to stdout/stderr.
#
# ADR-061 §결정 1: this file is invoked via thin bash wrapper
#   (check-codex-origin-main-directive-presence.sh)
# ADR-081 §D5 declaration-only retain: presence grep heuristic only
#   (semantic = reviewer)

import os
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

# [ORIGIN-MAIN-DIRECTIVE] block presence heuristic (ADR-081 Amendment 8 D9)
_DIRECTIVE_BLOCK_RE = re.compile(
    r"\[ORIGIN-MAIN-DIRECTIVE\]",
    re.MULTILINE,
)

# Fallback marker pattern
_FALLBACK_MARKER_RE = re.compile(
    r"\[origin-main-directive-fallback:\s*(.+?)\]",
    re.MULTILINE,
)

# Fallback enum closed-set 3 values (ADR-081 Amendment 8 D9 SSOT)
VALID_FALLBACK_ENUM = frozenset({
    "network_scope_offline",
    "legacy_prompt_format",
    "intentional_working_tree_verify",
})

# Bypass env (ADR-060 §결정 28.C)
_BYPASS_ENV = "BYPASS_CODEX_ORIGIN_MAIN_DIRECTIVE"


def check_origin_main_directive_presence(
    file_path: str,
) -> dict:
    """
    Lint a Codex worker spawn-prompt body file for [ORIGIN-MAIN-DIRECTIVE] block
    OR valid [origin-main-directive-fallback: <enum>] marker presence.

    Returns a dict with:
        status:           "PASS" | "WARNING" | "EXEMPT" | "META-ERROR"
        exit_code:        0 | 1 | 2
        directive_found:  bool (True if [ORIGIN-MAIN-DIRECTIVE] block present)
        fallback_value:   str or None (detected fallback enum value if present)
        message:          str (human-readable summary)
    """
    result: dict = {
        "status": "PASS",
        "exit_code": EXIT_PASS,
        "directive_found": False,
        "fallback_value": None,
        "message": "",
    }

    # --- Bypass env check (ADR-060 §결정 28.C) ---
    if os.environ.get(_BYPASS_ENV, "").strip() == "1":
        result["status"] = "PASS"
        result["exit_code"] = EXIT_PASS
        result["message"] = (
            f"[codex-origin-main-directive-check] BYPASS: "
            f"{_BYPASS_ENV}=1 — lint skipped (audit trail: bypass activated)"
        )
        print(result["message"])
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

    # --- Check (a): [ORIGIN-MAIN-DIRECTIVE] block presence ---
    directive_match = _DIRECTIVE_BLOCK_RE.search(content)
    if directive_match:
        result["status"] = "PASS"
        result["exit_code"] = EXIT_PASS
        result["directive_found"] = True
        result["message"] = (
            "[codex-origin-main-directive-check] PASS: "
            "[ORIGIN-MAIN-DIRECTIVE] block present in Codex worker spawn-prompt body "
            "(ADR-081 Amendment 8 §결정 D9)."
        )
        print(result["message"])
        return result

    # --- Check (b): [origin-main-directive-fallback: <enum>] marker presence ---
    fallback_match = _FALLBACK_MARKER_RE.search(content)
    if fallback_match:
        fallback_value = fallback_match.group(1).strip()
        result["fallback_value"] = fallback_value

        if fallback_value in VALID_FALLBACK_ENUM:
            # Valid fallback enum → PASS
            result["status"] = "PASS"
            result["exit_code"] = EXIT_PASS
            result["message"] = (
                f"[codex-origin-main-directive-check] PASS: "
                f"[origin-main-directive-fallback: {fallback_value}] present "
                f"(valid closed-set enum, ADR-081 Amendment 8 §결정 D9). "
                f"Rationale declared — lint satisfied."
            )
            print(result["message"])
            return result
        else:
            # Invalid fallback enum → WARNING (exit 1)
            result["status"] = "WARNING"
            result["exit_code"] = EXIT_WARNING
            result["message"] = (
                f"[codex-origin-main-directive-check] WARNING: "
                f"[origin-main-directive-fallback: {fallback_value!r}] found but "
                f"value is not a valid closed-set enum. "
                f"Valid values: network_scope_offline | legacy_prompt_format | "
                f"intentional_working_tree_verify "
                f"(ADR-081 Amendment 8 §결정 D9). "
                f"warning tier — PR merge not blocked (ADR-060 §결정 28). "
                f"Bypass: hotfix-bypass:codex-origin-main-directive-check label."
            )
            print(result["message"])
            return result

    # --- Both absent → WARNING (exit 1) ---
    result["status"] = "WARNING"
    result["exit_code"] = EXIT_WARNING
    result["message"] = (
        "[codex-origin-main-directive-check] WARNING: "
        "[ORIGIN-MAIN-DIRECTIVE] block absent AND no valid "
        "[origin-main-directive-fallback: <enum>] marker in "
        "Codex worker spawn-prompt body. "
        "Add one of: "
        "(a) [ORIGIN-MAIN-DIRECTIVE] block in prompt body, or "
        "(b) [origin-main-directive-fallback: network_scope_offline | "
        "legacy_prompt_format | intentional_working_tree_verify] marker. "
        "(ADR-081 Amendment 8 §결정 D9). "
        "warning tier — PR merge not blocked (ADR-060 §결정 28). "
        "Bypass: hotfix-bypass:codex-origin-main-directive-check label."
    )
    print(result["message"])
    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main() -> int:
    """CLI entry point.
    Usage: python3 check_codex_origin_main_directive_presence.py <file> [<file2> ...]
    """
    args = sys.argv[1:]

    if not args:
        print(
            "Usage: python3 check_codex_origin_main_directive_presence.py <prompt-file> [...]",
            file=sys.stderr,
        )
        print(
            "Lints Codex worker spawn-prompt body for [ORIGIN-MAIN-DIRECTIVE] block presence.",
            file=sys.stderr,
        )
        print(
            "Exit codes: 0=PASS | 1=WARNING | 2=META-ERROR (ADR-060 §결정 15 3-tier)",
            file=sys.stderr,
        )
        return EXIT_PASS  # no file = advisory pass (graceful degradation)

    # Process each file — worst exit code wins
    max_exit = EXIT_PASS
    for f in args:
        result = check_origin_main_directive_presence(f)
        if result["exit_code"] > max_exit:
            max_exit = result["exit_code"]

    return max_exit


if __name__ == "__main__":
    sys.exit(main())
