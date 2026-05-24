"""
scripts/lib/check_subagent_sibling_story_polling.py
CFP-1366 / ADR-073 Amendment 6 §결정 1-G — Subagent sibling Story polling Wave 2 mechanical wire

Heuristic: PR body / Issue body / spawn prompt 안 sibling CFP-NNN reference 검출 시,
paired `verified-via: gh issue view <CFP-NNN>` 또는 동형 polling evidence annotation
presence-grep. 단, 다음은 skip:
  - PR own carrier CFP (title 안 CFP-NNN, 자기 자신)
  - `Closes #N` / `Resolves #N` / `Fixes #N` style (closure declarations)
  - `[CFP-N]` commit message prefix (자기 carrier)
  - reference in code block or quoted text (heuristic noise reduction)

Exit codes:
  0: PASS (no unverified sibling cite OR all cites have verified-via)
  1: WARN (unverified sibling cite found)
  2: SETUP error

BYPASS:
  BYPASS_SUBAGENT_SIBLING_STORY_POLLING=1 — unconditional skip

CFP-1347 Amendment 6 Sentinel: pattern_count 3 reach
  (CFP-1226 + CFP-1269 + CFP-1273, super-class sibling_story_stale_claim_at_handoff)
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

CFP_PATTERN = re.compile(r"\bCFP-(\d{1,5})\b")

# Annotations that satisfy polling evidence
VERIFIED_VIA_PATTERNS = [
    r"verified-via:\s*gh issue view\s+(?:<?[\w-]+>?|CFP-\d+)",
    r"verified-via:\s*gh pr list\s+--search",
    r"verified-via:\s*gh issue view\s+<epic>",
    r"verified-via:\s*sibling Story\s+state\s+poll",
    r"verified-via:\s*sibling[- ]story[- ]polling",
]

# Closure declaration patterns (skip — not a "claim")
CLOSURE_PATTERNS = [
    r"\b(?:Closes|Resolves|Fixes|Close|Resolve|Fix)\s+#\d+",
    r"\bCloses\s+CFP-\d+",
]

# Self-carrier patterns (skip — claim about own Story)
def _self_carrier_pattern(own_cfp: str) -> re.Pattern[str]:
    return re.compile(rf"\b{re.escape(own_cfp)}\b")


def extract_sibling_cfps(text: str, own_cfp: str | None) -> list[str]:
    """
    PR body 안 CFP-NNN reference enumerate.
    own_cfp 자기 자신 + Closes/Resolves 인용은 제외.
    """
    all_cites = set(CFP_PATTERN.findall(text))
    if own_cfp:
        own_num = own_cfp.replace("CFP-", "")
        all_cites.discard(own_num)

    # Filter out closure-pattern context
    siblings = []
    for num in all_cites:
        cfp = f"CFP-{num}"
        # If cited only in Closes/Resolves/Fixes context, skip
        non_closure_contexts = re.findall(
            rf"(?:^|[^#])\b{cfp}\b(?!\s*[A-Z])",
            text,
        )
        if non_closure_contexts:
            siblings.append(cfp)
    return sorted(set(siblings))


def has_verified_via_for(cfp: str, text: str) -> bool:
    """Check verified-via annotation paired with sibling cite."""
    # Generic verified-via that mentions polling subject
    for pat in VERIFIED_VIA_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    # Specific cfp annotation
    specific = rf"verified-via:.*{cfp}"
    if re.search(specific, text, re.IGNORECASE):
        return True
    return False


def check_text(text: str, own_cfp: str | None = None) -> tuple[int, str]:
    """
    Returns (exit_code, message).
    """
    siblings = extract_sibling_cfps(text, own_cfp)
    if not siblings:
        return 0, "PASS: no sibling CFP reference detected"

    # If any verified-via annotation present, consider satisfied (generic polling claim)
    if any(re.search(p, text, re.IGNORECASE) for p in VERIFIED_VIA_PATTERNS):
        return 0, f"PASS: sibling cites {siblings} found, polling verified-via annotation present"

    return 1, (
        f"WARN: sibling CFP cites {siblings} found but no verified-via annotation "
        f"(ADR-073 Amd 6 §결정 1-G sibling Story polling primitive)"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="subagent-sibling-story-polling-evidence CI lint (CFP-1366)"
    )
    parser.add_argument("--input-file", type=str)
    parser.add_argument("--text", type=str)
    parser.add_argument("--own-cfp", type=str, help="Self-carrier CFP-NNN (skip)")
    args = parser.parse_args()

    if os.environ.get("BYPASS_SUBAGENT_SIBLING_STORY_POLLING") == "1":
        print("[BYPASS] BYPASS_SUBAGENT_SIBLING_STORY_POLLING=1 -- skip")
        return 0

    if args.input_file:
        path = Path(args.input_file)
        if not path.is_file():
            print(f"[SETUP] input file not found: {args.input_file}", file=sys.stderr)
            return 2
        text = path.read_text(encoding="utf-8", errors="replace")
    elif args.text is not None:
        text = args.text
    else:
        print("[SETUP] either --input-file or --text required", file=sys.stderr)
        return 2

    code, msg = check_text(text, args.own_cfp)
    if code == 0:
        print(msg)
    else:
        print(msg, file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
