#!/usr/bin/env python3
"""
merge.py — agent md core + overlay merger

Usage:
    python3 merge.py <core.md> <overlay.md>

Produces merged agent md to stdout. Consumer SessionStart hook invokes this
per agent and redirects stdout to `.claude/agents/<Name>.md`.

Merge semantics (see docs/plugin-design.md):
- Body: core body + "\\n\\n---\\n\\n## Project Overlay — <project>\\n\\n" + overlay body
- Frontmatter scalars (name, description, model, color): core-wins. overlay
  differing value → abort.
- Frontmatter arrays (tools, permissions.allow, permissions.deny): concat +
  dedup (core first, overlay tail).
- Frontmatter maps: recursive (nested arrays concat+dedup).

If overlay file is missing, emits core-only with auto-generated header.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "ERROR: PyYAML required. Install: pip install pyyaml\n"
    )
    sys.exit(2)


FRONTMATTER_DELIMITER = "---"
SCALAR_FIELDS_CORE_WINS = {"name", "description", "model", "color"}


def split_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter_dict, body). Empty frontmatter if absent."""
    if not raw.startswith(FRONTMATTER_DELIMITER + "\n"):
        return {}, raw
    parts = raw.split("\n" + FRONTMATTER_DELIMITER + "\n", 1)
    if len(parts) != 2:
        sys.stderr.write("ERROR: malformed frontmatter (no closing ---)\n")
        sys.exit(3)
    fm_text = parts[0][len(FRONTMATTER_DELIMITER) + 1:]
    body = parts[1]
    fm = yaml.safe_load(fm_text) or {}
    if not isinstance(fm, dict):
        sys.stderr.write("ERROR: frontmatter is not a YAML mapping\n")
        sys.exit(3)
    return fm, body


def dedup_list(seq: list[Any]) -> list[Any]:
    """Dedup preserving order (stringified equality)."""
    seen: set[str] = set()
    out: list[Any] = []
    for item in seq:
        key = str(item)
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def deep_merge(core: Any, overlay: Any, path: str = "") -> Any:
    """Deep merge overlay into core.

    - scalars: in SCALAR_FIELDS_CORE_WINS → core-wins with abort on mismatch;
               other scalars → core-wins silently
    - lists: concat + dedup (core first)
    - dicts: recurse per key
    """
    if isinstance(core, list) and isinstance(overlay, list):
        return dedup_list(list(core) + list(overlay))
    if isinstance(core, dict) and isinstance(overlay, dict):
        out: dict[str, Any] = dict(core)
        for key, ov_val in overlay.items():
            if key in out:
                out[key] = deep_merge(out[key], ov_val, f"{path}.{key}")
            else:
                out[key] = ov_val
        return out
    # scalars
    field = path.lstrip(".")
    if field in SCALAR_FIELDS_CORE_WINS and core != overlay:
        sys.stderr.write(
            f"ERROR: overlay scalar mismatch at {path!r}: "
            f"core={core!r} overlay={overlay!r}. Core identity fields "
            f"(name/description/model/color) must not diverge.\n"
        )
        sys.exit(4)
    return core  # core-wins for all scalars


def merge_frontmatter(core_fm: dict[str, Any], overlay_fm: dict[str, Any]) -> dict[str, Any]:
    # Sanity check: name must match if both present
    if "name" in core_fm and "name" in overlay_fm:
        if core_fm["name"] != overlay_fm["name"]:
            sys.stderr.write(
                f"ERROR: agent name mismatch: core={core_fm['name']!r} "
                f"overlay={overlay_fm['name']!r}\n"
            )
            sys.exit(4)
    return deep_merge(core_fm, overlay_fm)


def render_frontmatter(fm: dict[str, Any]) -> str:
    if not fm:
        return ""
    return (
        FRONTMATTER_DELIMITER
        + "\n"
        + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).rstrip()
        + "\n"
        + FRONTMATTER_DELIMITER
        + "\n"
    )


def auto_header(core_path: Path, overlay_path: Path | None) -> str:
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    overlay_src = str(overlay_path) if overlay_path else "(none)"
    return (
        f"<!--\n"
        f"  GENERATED FROM {core_path} + {overlay_src}\n"
        f"  DO NOT EDIT DIRECTLY. Edit source files and let SessionStart hook regenerate.\n"
        f"  Last regenerated: {ts}\n"
        f"-->\n\n"
    )


def main() -> int:
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        sys.stderr.write(
            "Usage: merge.py <core.md> [<overlay.md>]\n"
            "Emits merged agent md to stdout.\n"
        )
        return 1

    core_path = Path(sys.argv[1])
    overlay_path = Path(sys.argv[2]) if len(sys.argv) == 3 else None

    if not core_path.exists():
        sys.stderr.write(f"ERROR: core file not found: {core_path}\n")
        return 5

    core_raw = core_path.read_text(encoding="utf-8")
    core_fm, core_body = split_frontmatter(core_raw)

    if overlay_path is not None and overlay_path.exists():
        overlay_raw = overlay_path.read_text(encoding="utf-8")
        overlay_fm, overlay_body = split_frontmatter(overlay_raw)
        merged_fm = merge_frontmatter(core_fm, overlay_fm)
        overlay_body_stripped = overlay_body.strip()
        if overlay_body_stripped:
            body = (
                core_body.rstrip()
                + "\n\n---\n\n## Project Overlay\n\n"
                + overlay_body_stripped
                + "\n"
            )
        else:
            body = core_body
    else:
        merged_fm = core_fm
        body = core_body

    sys.stdout.write(render_frontmatter(merged_fm))
    sys.stdout.write(auto_header(core_path, overlay_path))
    sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
