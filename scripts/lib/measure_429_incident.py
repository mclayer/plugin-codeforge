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
import os
import re
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

# A2 (#1459) — cross-platform file lock for JSONL append race / TOCTOU
# POSIX: fcntl.flock(LOCK_EX) / Windows: msvcrt.locking(LK_LOCK)
if os.name == "nt":
    import msvcrt
else:
    import fcntl


SCHEMA_VERSION = "1.0"
DEFAULT_WINDOW_WEEKS = 4


# A1 (#1458) — collector secret redaction defense-in-depth
# Marker regex are count-only by design (\d+), but defense-in-depth: coerce
# every extracted scalar through _coerce_int / _coerce_str_safe so that even
# if marker schema is widened in future, content cannot leak unsanitized.
_SAFE_STR_RE = re.compile(r"^[0-9A-Za-z_\-:\.]{0,128}$")


def _coerce_int(raw, *, field):
    """Coerce regex-captured value to int; raise on non-digit (no silent fail)."""
    if not isinstance(raw, str) or not raw.isdigit():
        raise ValueError(f"[A1-guard] non-numeric value rejected for field={field!r}: {raw!r}")
    value = int(raw)
    if value < 0 or value > 10_000_000:
        raise ValueError(f"[A1-guard] out-of-range value for field={field!r}: {value}")
    return value


def _coerce_str_safe(raw, *, field):
    """Whitelist-validate string scalars — reject if any char outside [A-Za-z0-9_\\-:.]."""
    if not isinstance(raw, str) or not _SAFE_STR_RE.match(raw):
        raise ValueError(f"[A1-guard] unsafe string rejected for field={field!r}: {raw!r}")
    return raw


# A2 (#1459) — cross-platform exclusive lock context manager
class _ExclusiveFileLock:
    """OS-native exclusive lock around an open file handle.

    POSIX  : fcntl.flock(LOCK_EX) (advisory but enforced for cooperating processes)
    Windows: msvcrt.locking(LK_LOCK, ...) (mandatory range lock, blocks ~10s then retries)
    """

    def __init__(self, fp):
        self.fp = fp

    def __enter__(self):
        if os.name == "nt":
            # Windows: mandatory lock on first byte; LK_LOCK blocks up to ~10s with retry
            try:
                self.fp.seek(0)
                msvcrt.locking(self.fp.fileno(), msvcrt.LK_LOCK, 1)
            except OSError:
                # Empty file or seek failure — fall back to no-op lock (best-effort)
                pass
        else:
            fcntl.flock(self.fp.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.name == "nt":
            try:
                self.fp.seek(0)
                msvcrt.locking(self.fp.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
        else:
            fcntl.flock(self.fp.fileno(), fcntl.LOCK_UN)
        return False


def _atomic_write_text(path: Path, content: str) -> None:
    """A2 (#1459) — atomic write via tmp file + os.replace (rename is atomic on same FS)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


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

            # [429-auto-retry: count=N] aggregation — A1 guard: _coerce_int rejects non-digit
            markers = re.findall(r"\[429-auto-retry:\s*count=(\d+)", content)
            for marker in markers:
                try:
                    count_429 += _coerce_int(marker, field="429-auto-retry.count")
                except ValueError as exc:
                    print(f"[A1-guard] skip malformed marker in {story_file.name}: {exc}", file=sys.stderr)

            # [429-cascade: depth=N] cascade incident tracking — A1 guard
            cascade_markers = re.findall(r"\[429-cascade:\s*depth=(\d+)", content)
            for depth in cascade_markers:
                try:
                    d = _coerce_int(depth, field="429-cascade.depth")
                except ValueError as exc:
                    print(f"[A1-guard] skip malformed marker in {story_file.name}: {exc}", file=sys.stderr)
                    continue
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

    # Persist JSON snapshot — A2 (#1459) atomic write (tmp + rename) on same FS
    _atomic_write_text(out_file, json.dumps(kpi, indent=2) + "\n")

    # Append to history JSONL — A2 (#1459) exclusive flock + atomic rewrite
    # idempotent last-line replace per week, race-safe across concurrent invocations
    history_file.parent.mkdir(parents=True, exist_ok=True)

    # Open in r+ if exists else create empty (lock-then-read-then-rewrite atomic envelope)
    if history_file.exists():
        lock_mode = "r+"
    else:
        # Create empty file first so we can lock it
        history_file.touch()
        lock_mode = "r+"

    with open(history_file, lock_mode, encoding="utf-8") as fp:
        with _ExclusiveFileLock(fp):
            fp.seek(0)
            raw = fp.read()
            history_lines = [line.strip() for line in raw.splitlines() if line.strip()]

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

            # Rewrite under lock (truncate + write + fsync)
            fp.seek(0)
            fp.truncate()
            fp.write("\n".join(history_lines) + "\n")
            fp.flush()
            os.fsync(fp.fileno())

    print(
        f"[measure-429-incident] week={week} count={count_429} "
        f"cascade={cascade_incidents} max_depth={max_cascade_depth} gate={gate_status}"
    )


if __name__ == "__main__":
    main()
