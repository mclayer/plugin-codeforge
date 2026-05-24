#!/usr/bin/env python3
"""
Measure 429 rate-limit incidents from Story §14 Lane Evidence markers.
Aggregate to docs/kpi/429-incident.json + append history.jsonl.
"""

import argparse
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="Measure 429 incidents from Story files")
    parser.add_argument("--week", default=None, help="ISO week YYYY-W##")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    week = args.week or datetime.now().strftime("%Y-W%V")

    # Scan docs/stories/*.md for §14 Lane Evidence blocks
    count_429 = 0
    count_other = 0

    for story_file in (repo_root / "docs" / "stories").glob("*.md"):
        with open(story_file, encoding="utf-8") as f:
            content = f.read()

        # Grep for [429-auto-retry: ...] markers in §14 Lane Evidence
        markers = re.findall(r"\[429-auto-retry: count=(\d+)", content)
        for marker in markers:
            count_429 += int(marker)

        # Grep for other rate-limit incidents
        other_markers = re.findall(r"\[rate-limit-fallback:.*?\]", content)
        count_other += len(other_markers)

    # Load or init docs/kpi/429-incident.json
    kpi_file = repo_root / "docs" / "kpi" / "429-incident.json"
    kpi_file.parent.mkdir(parents=True, exist_ok=True)

    if kpi_file.exists():
        with open(kpi_file) as f:
            kpi = json.load(f)
    else:
        kpi = {"weekly_counts": {}, "gate_status": "operational"}

    # Update week entry (idempotent: last write wins)
    kpi["weekly_counts"][week] = {"count": count_429, "other": count_other, "updated_at": datetime.utcnow().isoformat() + "Z"}

    # Persist
    with open(kpi_file, "w") as f:
        json.dump(kpi, f, indent=2)

    # Append to history.jsonl (one JSON object per line, idempotent last-line replace)
    history_file = repo_root / "docs" / "kpi" / "429-incident.jsonl"
    history_file.parent.mkdir(parents=True, exist_ok=True)

    history_lines = []
    if history_file.exists():
        with open(history_file) as f:
            history_lines = [line.strip() for line in f if line.strip()]

    # Remove last line if same week (idempotent update)
    if history_lines:
        last_entry = json.loads(history_lines[-1])
        if last_entry.get("week") == week:
            history_lines.pop()

    # Append current week
    current_entry = {
        "week": week,
        "count": count_429,
        "other": count_other,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    history_lines.append(json.dumps(current_entry, separators=(",", ":")))

    with open(history_file, "w") as f:
        f.write("\n".join(history_lines) + "\n")

    print(f"[measure-429-incident] week={week} count={count_429} other={count_other}")


if __name__ == "__main__":
    main()
