#!/usr/bin/env python3
"""
Measure 429 rate-limit incidents from Story §14 Lane Evidence markers.
Aggregate to docs/kpi/429-incident.json + append history JSONL.

CFP-1354 FIX iter 3 — workflow → bash → python 5-flag handshake contract:
  --week         ISO week YYYY-W## (default: current UTC week)
  --as-of        ISO 8601 date (override "now", for deterministic backfill)
  --out          Output JSON path (default: docs/kpi/429-incident.json)
  --history-out  Output JSONL path (default: docs/kpi/429-incident-history.jsonl)
  --repo-root    Repository root (default: ".")

Schema compatibility (existing docs/kpi/429-incident.json):
  schema_version / history_file / measured_at / window_weeks /
  weekly_incident_count / cascade_incidents / max_cascade_depth / gate_status
"""

import argparse
import json
import re
from pathlib import Path
from datetime import datetime, timezone


SCHEMA_VERSION = "1.0"
DEFAULT_WINDOW_WEEKS = 4


def main():
    parser = argparse.ArgumentParser(description="Measure 429 incidents from Story files")
    parser.add_argument("--week", default=None, help="ISO week YYYY-W##")
    parser.add_argument("--as-of", default=None, help="ISO 8601 date override (YYYY-MM-DD)")
    parser.add_argument("--out", default=None, help="Output JSON path")
    parser.add_argument("--history-out", default=None, help="Output history JSONL path")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)

    # Compute "now" — --as-of overrides current time for deterministic backfill
    if args.as_of:
        try:
            now = datetime.strptime(args.as_of, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            # Permit full ISO 8601 if user passes YYYY-MM-DDTHH:MM:SSZ
            now = datetime.fromisoformat(args.as_of.replace("Z", "+00:00"))
    else:
        now = datetime.now(timezone.utc)

    # Compute ISO week (Python isocalendar returns (year, week, weekday))
    if args.week:
        week = args.week
    else:
        iso_year, iso_week, _ = now.isocalendar()
        week = f"{iso_year}-W{iso_week:02d}"

    # Default output paths (workflow contract)
    out_file = Path(args.out) if args.out else repo_root / "docs" / "kpi" / "429-incident.json"
    history_file = Path(args.history_out) if args.history_out else repo_root / "docs" / "kpi" / "429-incident-history.jsonl"

    # Scan docs/stories/*.md for §14 Lane Evidence markers
    count_429 = 0
    cascade_incidents = 0
    max_cascade_depth = 0

    stories_dir = repo_root / "docs" / "stories"
    if stories_dir.is_dir():
        for story_file in stories_dir.glob("*.md"):
            try:
                content = story_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            # [429-auto-retry: count=N] aggregation
            markers = re.findall(r"\[429-auto-retry:\s*count=(\d+)", content)
            for marker in markers:
                count_429 += int(marker)

            # [429-cascade: depth=N] cascade incident tracking
            cascade_markers = re.findall(r"\[429-cascade:\s*depth=(\d+)", content)
            for depth in cascade_markers:
                d = int(depth)
                cascade_incidents += 1
                if d > max_cascade_depth:
                    max_cascade_depth = d

    # Gate status determination (CFP-1354 / ADR-109 §결정 6)
    if cascade_incidents > 0 or count_429 >= 20:
        gate_status = "alert"
    elif count_429 >= 10:
        gate_status = "warning"
    else:
        gate_status = "operational"

    measured_at_iso = now.isoformat()

    # Build JSON payload — schema-compatible with existing docs/kpi/429-incident.json
    kpi = {
        "schema_version": SCHEMA_VERSION,
        "history_file": str(history_file.relative_to(repo_root)) if history_file.is_absolute() is False or repo_root.resolve() in history_file.resolve().parents else str(history_file),
        "measured_at": measured_at_iso,
        "window_weeks": DEFAULT_WINDOW_WEEKS,
        "weekly_incident_count": count_429,
        "cascade_incidents": cascade_incidents,
        "max_cascade_depth": max_cascade_depth,
        "gate_status": gate_status,
    }

    # If existing file has additional/custom fields, preserve schema_version + window_weeks
    if out_file.exists():
        try:
            with open(out_file, encoding="utf-8") as f:
                existing = json.load(f)
            # Preserve window_weeks if explicitly set
            if isinstance(existing, dict) and "window_weeks" in existing:
                kpi["window_weeks"] = existing["window_weeks"]
            if isinstance(existing, dict) and "history_file" in existing:
                kpi["history_file"] = existing["history_file"]
        except (OSError, json.JSONDecodeError):
            pass

    # Persist JSON snapshot
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(kpi, f, indent=2)
        f.write("\n")

    # Append to history JSONL (one JSON object per line, idempotent last-line replace per week)
    history_file.parent.mkdir(parents=True, exist_ok=True)
    history_lines = []
    if history_file.exists():
        with open(history_file, encoding="utf-8") as f:
            history_lines = [line.strip() for line in f if line.strip()]

    # Remove last line if same week (idempotent update)
    if history_lines:
        try:
            last_entry = json.loads(history_lines[-1])
            if last_entry.get("week") == week:
                history_lines.pop()
        except json.JSONDecodeError:
            pass

    current_entry = {
        "week": week,
        "measured_at": measured_at_iso,
        "weekly_incident_count": count_429,
        "cascade_incidents": cascade_incidents,
        "max_cascade_depth": max_cascade_depth,
        "gate_status": gate_status,
    }
    history_lines.append(json.dumps(current_entry, separators=(",", ":")))

    with open(history_file, "w", encoding="utf-8") as f:
        f.write("\n".join(history_lines) + "\n")

    print(
        f"[measure-429-incident] week={week} count={count_429} "
        f"cascade={cascade_incidents} max_depth={max_cascade_depth} gate={gate_status}"
    )


if __name__ == "__main__":
    main()
