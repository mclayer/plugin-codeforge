"""CFP-1584 Sub-A Phase 2 — generate probe body content at specific byte sizes.

Generates 3 markdown filler bodies (1KB, 64KB, 256KB) and prints byte size.
Output written to scripts/cfp-1584-probes/<size>.md so each call to Confluence
can Read the file content verbatim.

Per ADR-061: external file (not heredoc).
"""
from __future__ import annotations

from pathlib import Path

OUT_DIR = Path("scripts/cfp-1584-probes")

# Repeating ASCII payload — markdown-safe (no special syntax that might be re-rendered)
PAYLOAD_UNIT = "This is a probe payload line for CFP-1584 Phase 2 stepped probe. "
# = 64 bytes per unit (ASCII)

TARGETS = [
    ("probe_1kb", 1024),
    ("probe_64kb", 64 * 1024),
    ("probe_256kb", 256 * 1024),
]


def make_body(target_bytes: int, label: str) -> str:
    header = f"# CFP-1584 Phase 2 Probe ({label})\n\n"
    header += f"Probe target byte size: {target_bytes}\n\n"
    header += "Filler content below (ASCII repeat):\n\n"
    remaining = target_bytes - len(header.encode("utf-8"))
    if remaining <= 0:
        return header
    # Repeat payload until reaching target
    repeats = (remaining // len(PAYLOAD_UNIT)) + 1
    body_filler = (PAYLOAD_UNIT * repeats)[:remaining]
    return header + body_filler


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for label, target in TARGETS:
        body = make_body(target, label)
        outfile = OUT_DIR / f"{label}.md"
        outfile.write_text(body, encoding="utf-8")
        actual = len(body.encode("utf-8"))
        print(f"  {label}: target={target}  actual={actual}  file={outfile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
