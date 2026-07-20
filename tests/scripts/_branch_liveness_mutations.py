#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/scripts/_branch_liveness_mutations.py — mutation harness for watchdog §8.4

Reusable mutation-harness pattern (following _ac_marker_mutations.py).
For check_branch_liveness.py and emit_branch_heartbeat.py mutation testing.

Verifies that tests are not vacuous-GREEN by mutating core logic and confirming
test suite detects the mutations (kills them).
"""

import argparse
import importlib.util
import os
import re
import sys
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

# Mutation candidates: (desc, kind, needle, replacement)
# kind: "literal" | "regex"
CANDIDATES = {
    "fail-open-promotion": [
        (
            "unknown→fresh fail-open: 'if summary[\"unknown\"] > 0: verdict_top = \"inconclusive\"' → 'pass'",
            "literal",
            'if summary["unknown"] > 0:\n        verdict_top = "inconclusive"',
            'if summary["unknown"] > 0:\n        verdict_top = "ok"  # MUTATED-FAIL-OPEN',
        ),
        (
            "fail-open via regex: inconclusive → ok",
            "regex",
            r'verdict_top\s*=\s*"inconclusive"',
            'verdict_top = "ok"  # MUTATED',
        ),
    ],
    "seq-advance-relaxation": [
        (
            "strict-advance relaxation: 'seq_new > last_seq' → 'seq_new >= last_seq'",
            "literal",
            "seq_new > _as_int(prev_last_seq)",
            "seq_new >= _as_int(prev_last_seq)  # MUTATED-SEQ-RELAX",
        ),
    ],
    "threshold-bypass": [
        (
            "stalled condition bypass: 'elapsed > thr' → 'elapsed >= thr' (minor) → 'elapsed > thr * 2' (bypass)",
            "literal",
            "elapsed > thr",
            "elapsed > thr * 2  # MUTATED-THRESHOLD-BYPASS",
        ),
    ],
    "idle-relaxation-disable": [
        (
            "disable idle-relaxation: 'if idle: -> if False:'",
            "literal",
            "if idle:",
            "if False:  # MUTATED-IDLE-BYPASS",
        ),
    ],
    "total-deadline-removal": [
        (
            "remove total-deadline ceiling: 'if elapsed > _TOTAL_DEADLINE_MIN' → 'if False'",
            "literal",
            "if elapsed is not None and elapsed > _TOTAL_DEADLINE_MIN:",
            "if False:  # MUTATED-REMOVE-CEILING",
        ),
    ],
}


def read_source(path):
    """Read Python source file."""
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _apply(src, kind, needle, repl):
    """Apply mutation: (kind, needle, repl) → (mutated_src, count)."""
    if kind == "literal":
        if needle not in src:
            return src, 0
        return src.replace(needle, repl), src.count(needle)
    # regex
    mutated, n = re.subn(needle, lambda _m: repl, src)
    return mutated, n


def load_module(path, name):
    """Load Python module from file (safe for temp mutations)."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # register for imports
    spec.loader.exec_module(mod)
    return mod


def iter_mutants(kind, out_dir, src_path):
    """Iterate over valid (applied, importable) mutants.

    Yields: (desc, mutant_path, mutant_module)

    Honesty contract:
    - Mutation not applied (diff=0) → not yielded
    - Mutant breaks on import → not yielded (broken mutant, not a kill)
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    src = read_source(src_path)
    candidates = CANDIDATES.get(kind, [])

    if not candidates:
        return

    for i, (desc, mut_kind, needle, repl) in enumerate(candidates):
        mutated, n_applied = _apply(src, mut_kind, needle, repl)

        if n_applied == 0:
            # Not applied
            continue

        # Write temp mutant file
        mutant_name = Path(src_path).stem
        mutant_file = out_dir / f"{mutant_name}_MUTANT_{kind}_{i}.py"
        mutant_file.write_text(mutated, encoding="utf-8")

        try:
            # Try to import — if broken, skip (not a valid kill target)
            mod = load_module(str(mutant_file), f"mutant_{kind}_{i}")
            yield desc, str(mutant_file), mod
        except Exception as e:
            # Broken mutant — not a kill target
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Branch liveness mutation harness"
    )
    parser.add_argument("--kind", required=True,
                        choices=list(CANDIDATES.keys()),
                        help="mutation kind")
    parser.add_argument("--source", required=True, help="source .py file")
    parser.add_argument("--out-dir", required=True, help="output dir for mutants")
    args = parser.parse_args()

    count = 0
    for desc, path, mod in iter_mutants(args.kind, args.out_dir, args.source):
        print(f"  [{args.kind}] {desc}")
        print(f"    file: {path}")
        count += 1

    if count == 0:
        print(f"  [ERROR] No {args.kind} mutations applied (source invariant)")
        sys.exit(1)
    else:
        print(f"[OK] {count} mutant(s) generated for kind={args.kind}")
