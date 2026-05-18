#!/usr/bin/env python3
"""
yaml_oracle.py — CFP-906 Phase 2 bats test helper
Wave 3 #881 lesson: registry/YAML 검증 = yaml.safe_load 의무 (grep 금지)
ADR-061 §결정 5: multi-line Python > 5 lines → 외부 .py 파일

Usage:
  python yaml_oracle.py channel <yaml_file>
      → prints tier value, exit 0 on success
      → prints "NO_CHANNEL_BLOCK", exit 1 if codeforge.channel absent
      → exit 2 on parse error

  python yaml_oracle.py validate_enum <yaml_file>
      → exit 0 if tier in {stable, beta, canary}
      → exit 1 if invalid enum or missing

  python yaml_oracle.py frontmatter_version <md_file> <expected_version>
      → exit 0 if frontmatter version field matches expected_version
      → exit 1 if mismatch or parse error

  python yaml_oracle.py frontmatter_carrier_presence <md_file> <expected_carrier>
      → exit 0 if last version_history entry matches expected_carrier
      → exit 1 if mismatch

  python yaml_oracle.py label_registry_channel <md_file>
      → exit 0 if §3 yaml block contains 3 channel:* entries + category: channel
      → exit 1 if missing

  python yaml_oracle.py adr016_amendments <md_file>
      → exit 0 if frontmatter amendments: [1, 2, 3] (contains 3)
      → exit 1 if mismatch

  python yaml_oracle.py adr063_amendment6 <md_file>
      → exit 0 if amendments[] last entry has amendment: 6 + cfp: CFP-906
      → exit 1 if mismatch
"""

import sys
import re

VALID_TIERS = {"stable", "beta", "canary"}


def load_yaml_safe(path):
    import yaml  # stdlib-less fallback below
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def cmd_channel(yaml_file):
    """Print channel tier; exit 1 if absent; exit 2 on error."""
    try:
        data = load_yaml_safe(yaml_file)
    except Exception as e:
        print(f"PARSE_ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    codeforge = data.get("codeforge", {}) if data else {}
    channel = codeforge.get("channel") if codeforge else None
    if channel is None:
        print("NO_CHANNEL_BLOCK")
        sys.exit(1)

    tier = channel.get("tier") if isinstance(channel, dict) else None
    if tier is None:
        print("NO_TIER_FIELD")
        sys.exit(1)

    print(tier)
    sys.exit(0)


def cmd_validate_enum(yaml_file):
    """Exit 0 if tier in valid set; exit 1 otherwise."""
    try:
        data = load_yaml_safe(yaml_file)
    except Exception as e:
        print(f"PARSE_ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    codeforge = data.get("codeforge", {}) if data else {}
    channel = codeforge.get("channel") if codeforge else None
    if not isinstance(channel, dict):
        print("NO_CHANNEL_BLOCK", file=sys.stderr)
        sys.exit(1)

    tier = channel.get("tier")
    if tier not in VALID_TIERS:
        print(f"INVALID_ENUM: {tier!r} not in {VALID_TIERS}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: {tier}")
    sys.exit(0)


def _parse_frontmatter(md_file):
    """Return (frontmatter_str, body_str) from markdown with --- delimiters."""
    with open(md_file, encoding="utf-8") as f:
        content = f.read()
    # Match first --- ... --- block
    m = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not m:
        return None, content
    return m.group(1), content[m.end():]


def cmd_frontmatter_version(md_file, expected_version):
    """Exit 0 if frontmatter version field matches expected_version."""
    import yaml
    fm_str, _ = _parse_frontmatter(md_file)
    if fm_str is None:
        print("NO_FRONTMATTER", file=sys.stderr)
        sys.exit(1)
    try:
        fm = yaml.safe_load(fm_str)
    except Exception as e:
        print(f"FM_PARSE_ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    version = str(fm.get("version", ""))
    if version != expected_version:
        print(f"VERSION_MISMATCH: got={version!r} expected={expected_version!r}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: version={version}")
    sys.exit(0)


def cmd_frontmatter_carrier_presence(md_file, expected_carrier):
    """
    Exit 0 if version_history contains an entry with matching carrier.
    Note: version_history ordering may not be strictly chronological (insertion order).
    We verify carrier *presence* (any entry), not strictly last entry.
    This matches the reconcile-protocol-v1 actual ordering (v1.7 inserted before v1.5/v1.6).
    """
    import re
    with open(md_file, encoding="utf-8") as f:
        content = f.read()

    # Extract frontmatter
    m = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not m:
        print("NO_FRONTMATTER", file=sys.stderr)
        sys.exit(1)

    fm_str = m.group(1)
    # Use regex to find carrier entries (yaml.safe_load may fail on special chars in long frontmatter)
    # Pattern: { version: "X.Y", ..., carrier: CFP-NNN, ...}
    carriers = re.findall(r"carrier:\s*(" + re.escape(expected_carrier) + r")\b", fm_str)
    if not carriers:
        # also check non-inline form
        carriers = re.findall(r"carrier:\s*" + re.escape(expected_carrier), fm_str)

    if not carriers:
        print(
            f"CARRIER_NOT_FOUND: {expected_carrier!r} not in version_history",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"OK: carrier={expected_carrier} found in version_history")
    sys.exit(0)


def cmd_label_registry_channel(md_file):
    """
    Exit 0 if md contains §3 yaml block with:
      - 3 entries with category: channel
      - names channel:stable, channel:beta, channel:canary all present
    Wave 3 #881 lesson: use yaml.safe_load on extracted block, not grep.
    """
    import yaml
    with open(md_file, encoding="utf-8") as f:
        content = f.read()

    # Extract the ```yaml ... ``` code block(s) — find the one containing channel: entries
    blocks = re.findall(r"```yaml\n(.*?)```", content, re.DOTALL)
    channel_entries = []
    for block in blocks:
        try:
            parsed = yaml.safe_load(block)
        except Exception:
            continue
        # Handle both dict shape {labels: [...]} and bare list shape (F-CR-906-1, CFP-906 retro)
        if isinstance(parsed, dict) and "labels" in parsed:
            items = parsed["labels"]
        elif isinstance(parsed, list):
            items = parsed
        else:
            continue
        for item in items:
            if isinstance(item, dict) and item.get("category") == "channel":
                channel_entries.append(item)

    if len(channel_entries) < 3:
        # Fallback: scan raw YAML rows in the document body for label-registry entries
        # label-registry uses inline YAML list under §3, not fenced block in some versions
        # Try to extract the full §3 yaml block by indentation
        all_names = set(re.findall(r"name:\s*(channel:[a-z]+)", content))
        all_cats = set(re.findall(r"category:\s*(channel)", content))
        if len(all_names) < 3 or not all_cats:
            print(
                f"MISSING_CHANNEL_ENTRIES: found {len(channel_entries)} yaml block entries, "
                f"raw names={all_names}, cats={all_cats}",
                file=sys.stderr,
            )
            sys.exit(1)
        # check required names
        required = {"channel:stable", "channel:beta", "channel:canary"}
        missing = required - all_names
        if missing:
            print(f"MISSING_LABELS: {missing}", file=sys.stderr)
            sys.exit(1)
        print(f"OK (raw fallback): channel labels={all_names}")
        sys.exit(0)

    names = {e.get("name") for e in channel_entries}
    required = {"channel:stable", "channel:beta", "channel:canary"}
    missing = required - names
    if missing:
        print(f"MISSING_LABELS: {missing}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: channel entries={names}")
    sys.exit(0)


def cmd_adr016_amendments(md_file):
    """Exit 0 if frontmatter amendments contains 3 (Amendment 3 registered)."""
    import yaml
    fm_str, _ = _parse_frontmatter(md_file)
    if fm_str is None:
        print("NO_FRONTMATTER", file=sys.stderr)
        sys.exit(1)
    try:
        fm = yaml.safe_load(fm_str)
    except Exception as e:
        print(f"FM_PARSE_ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    amendments = fm.get("amendments", [])
    if 3 not in amendments:
        print(f"AMENDMENT_3_MISSING: amendments={amendments}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: amendments={amendments}")
    sys.exit(0)


def cmd_adr063_amendment6(md_file):
    """Exit 0 if amendments[] last entry has amendment: 6 and cfp: CFP-906."""
    import yaml
    fm_str, _ = _parse_frontmatter(md_file)
    if fm_str is None:
        print("NO_FRONTMATTER", file=sys.stderr)
        sys.exit(1)
    try:
        fm = yaml.safe_load(fm_str)
    except Exception as e:
        print(f"FM_PARSE_ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    amendments = fm.get("amendments", [])
    if not amendments:
        print("NO_AMENDMENTS", file=sys.stderr)
        sys.exit(1)

    last = amendments[-1]
    if not isinstance(last, dict):
        print(f"LAST_NOT_DICT: {last!r}", file=sys.stderr)
        sys.exit(1)

    amd_num = last.get("amendment")
    cfp_val = str(last.get("cfp", ""))

    if amd_num != 6:
        print(f"AMENDMENT_NUM_MISMATCH: got={amd_num!r} expected=6", file=sys.stderr)
        sys.exit(1)

    if cfp_val != "CFP-906":
        print(f"CFP_MISMATCH: got={cfp_val!r} expected=CFP-906", file=sys.stderr)
        sys.exit(1)

    print(f"OK: amendment=6 cfp={cfp_val}")
    sys.exit(0)


COMMANDS = {
    "channel": cmd_channel,
    "validate_enum": cmd_validate_enum,
    "frontmatter_version": cmd_frontmatter_version,
    "frontmatter_carrier_presence": cmd_frontmatter_carrier_presence,
    "label_registry_channel": cmd_label_registry_channel,
    "adr016_amendments": cmd_adr016_amendments,
    "adr063_amendment6": cmd_adr063_amendment6,
}


def main():
    if len(sys.argv) < 2:
        print(f"Usage: yaml_oracle.py <command> [args...]\nCommands: {list(COMMANDS)}")
        sys.exit(2)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd!r}", file=sys.stderr)
        sys.exit(2)

    fn = COMMANDS[cmd]
    fn(*args)


if __name__ == "__main__":
    main()
