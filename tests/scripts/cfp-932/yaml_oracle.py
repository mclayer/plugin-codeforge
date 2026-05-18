#!/usr/bin/env python3
"""
yaml_oracle.py — CFP-932 Phase 2 bats test helper
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

  python yaml_oracle.py workflow_yaml <yml_file> <key_path> <expected_value>
      → exit 0 if yaml[key_path] == expected_value (dot-notation key path)
      → exit 1 if mismatch
      → exit 2 on parse error
      key_path examples: "on.schedule.0.cron" / "jobs.drift-detection.continue-on-error"

  python yaml_oracle.py workflow_permissions_deny_all <yml_file>
      → exit 0 if top-level permissions: {} (deny-all)
      → exit 1 if mismatch

  python yaml_oracle.py evidence_registry_entry <yaml_file> <entry_name>
      → exit 0 if entry_name exists in registry with current_tier field
      → exit 1 if missing or schema violation

  python yaml_oracle.py infer_write_zero <script_path>
      → exit 0 if script has no write syscall patterns (>, >>, tee, sed -i)
      → exit 1 if potential write found

  python yaml_oracle.py workflow_files_byte_identical <file1> <file2>
      → exit 0 if files are byte-identical
      → exit 1 if different
"""

import sys
import os
import re

VALID_TIERS = {"stable", "beta", "canary"}


def load_yaml_safe(path):
    import yaml
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


def cmd_workflow_yaml(yml_file, key_path, expected_value):
    """Exit 0 if yaml[key_path] matches expected_value (dot-notation)."""
    try:
        data = load_yaml_safe(yml_file)
    except Exception as e:
        print(f"PARSE_ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    # Navigate dot-notation path (support integer index via digit test)
    parts = key_path.split(".")
    current = data
    for part in parts:
        if current is None:
            print(f"PATH_NOT_FOUND: key '{part}' in path '{key_path}'", file=sys.stderr)
            sys.exit(1)
        if isinstance(current, list):
            try:
                idx = int(part)
                current = current[idx]
            except (ValueError, IndexError) as e:
                print(f"LIST_INDEX_ERROR: {e} at path '{key_path}'", file=sys.stderr)
                sys.exit(1)
        elif isinstance(current, dict):
            if part not in current:
                # PyYAML 1.1 quirk: 'on' is parsed as bool True, 'off' as False, 'yes'/'no' etc.
                # GitHub Actions YAML uses 'on:' as event trigger key — handle the alias
                YAML11_BOOL_ALIASES = {"on": True, "off": False, "yes": True, "no": False}
                if part in YAML11_BOOL_ALIASES and YAML11_BOOL_ALIASES[part] in current:
                    current = current[YAML11_BOOL_ALIASES[part]]
                else:
                    print(f"KEY_NOT_FOUND: '{part}' in {list(current.keys())}", file=sys.stderr)
                    sys.exit(1)
            else:
                current = current[part]
        else:
            print(f"UNEXPECTED_TYPE: {type(current)} at path '{key_path}'", file=sys.stderr)
            sys.exit(1)

    # Compare (handle bool/string conversion for YAML values)
    actual_str = str(current).lower() if isinstance(current, bool) else str(current)
    expected_str = str(expected_value).lower() if expected_value.lower() in ("true", "false") else expected_value

    if actual_str != expected_str:
        print(f"VALUE_MISMATCH: got={actual_str!r} expected={expected_str!r}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: {key_path}={current!r}")
    sys.exit(0)


def cmd_workflow_permissions_deny_all(yml_file):
    """Exit 0 if top-level permissions: {} (deny-all)."""
    try:
        data = load_yaml_safe(yml_file)
    except Exception as e:
        print(f"PARSE_ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    perms = data.get("permissions")
    # permissions: {} means empty dict or None (YAML parses {} as None or {} depending on parser)
    if perms is None or perms == {}:
        print("OK: permissions deny-all ({})")
        sys.exit(0)
    else:
        print(f"PERMISSIONS_NOT_DENY_ALL: got={perms!r}", file=sys.stderr)
        sys.exit(1)


def cmd_evidence_registry_entry(yaml_file, entry_name):
    """Exit 0 if entry_name in registry yaml with required current_tier field."""
    try:
        data = load_yaml_safe(yaml_file)
    except Exception as e:
        print(f"PARSE_ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if data is None:
        print("EMPTY_REGISTRY", file=sys.stderr)
        sys.exit(1)

    # evidence-checks-registry: root may be a list OR a dict with 'entries' key
    # (schema version matters — newer format uses {schema_version, entries: [...]} dict)
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        entries = data.get("entries", [])
    else:
        entries = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if entry.get("name") == entry_name:
            if "current_tier" not in entry:
                print(f"MISSING_current_tier: entry '{entry_name}' found but current_tier absent", file=sys.stderr)
                sys.exit(1)
            tier_val = entry["current_tier"]
            print(f"OK: entry={entry_name!r} current_tier={tier_val!r}")
            sys.exit(0)

    print(f"ENTRY_NOT_FOUND: '{entry_name}' not in registry", file=sys.stderr)
    sys.exit(1)


def cmd_infer_write_zero(script_path):
    """Exit 0 if script has no file write patterns (write-0 invariant).

    write-0 invariant: script must not redirect output to files.
    stdout (>&1) and stderr (>&2) redirects are allowed.

    Approach: line-by-line analysis excluding heredoc content blocks and
    comment lines. Checks for actual shell file-write redirection syntax.
    """
    WRITE_PATTERNS = [
        r'\btee\b\s+[^|&\s]',   # tee <file> (not piped or fd)
        r'sed\s+-i',             # sed in-place
        r'python.*\.write\s*\(', # python file.write() call
        r'open\s*\([^)]*["\']w["\']',  # open(path, 'w') or open(path, "w")
    ]
    # Shell file-write redirect: "cmd > /path/to/file" or "cmd >> /path/to/file"
    # NOT matching: >&2, >/dev/null, 2>/dev/null, within quoted strings
    # The key insight: file writes target /path, $VAR, ~/ etc. — NOT &N or /dev/null
    FILE_REDIRECT = re.compile(
        r'(?<![&2])'       # not preceded by & or 2 (not >&2 or 2>)
        r'>{1,2}'          # > or >>
        r'\s*'             # optional space
        r'(?!/dev/null)'   # not discard
        r'(?![&\d])'       # not fd redirect (&1, &2, 1, 2)
        r'(?:[$/~]|\w+/)'  # filename starting with $, /, ~, or word/  (actual path)
    )

    with open(script_path, encoding="utf-8") as f:
        lines = f.readlines()

    in_heredoc = False
    heredoc_end = None
    violations = []

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()

        # Track heredoc blocks (skip content inside heredocs — not shell code)
        if in_heredoc:
            if stripped == heredoc_end:
                in_heredoc = False
                heredoc_end = None
            continue
        heredoc_match = re.match(r"<<['\"]?(\w+)['\"]?", line)
        if heredoc_match:
            in_heredoc = True
            heredoc_end = heredoc_match.group(1)

        # Skip comment lines and empty lines
        if stripped.startswith("#") or not stripped:
            continue

        # Check file-write redirect pattern (only outside heredocs)
        # Exclude pure echo/printf lines (they write to stdout, not files)
        is_echo_line = re.match(r'\s*(echo|printf)\s', line)
        if FILE_REDIRECT.search(line) and not is_echo_line:
            violations.append(f"line {lineno}: file redirect detected: {stripped!r}")

        # Check other write patterns
        for pattern in WRITE_PATTERNS:
            if re.search(pattern, line):
                violations.append(f"line {lineno} pattern={pattern!r}: {stripped!r}")

    if violations:
        print(f"WRITE_DETECTED: {violations}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: no write syscall patterns found in {os.path.basename(script_path)}")
    sys.exit(0)


def cmd_workflow_files_byte_identical(file1, file2):
    """Exit 0 if two files are byte-identical."""
    with open(file1, "rb") as f1:
        data1 = f1.read()
    with open(file2, "rb") as f2:
        data2 = f2.read()

    if data1 == data2:
        print(f"OK: byte-identical ({len(data1)} bytes)")
        sys.exit(0)
    else:
        # Find first difference
        for i, (b1, b2) in enumerate(zip(data1, data2)):
            if b1 != b2:
                print(f"NOT_IDENTICAL: first diff at byte {i}: {b1!r} vs {b2!r}", file=sys.stderr)
                break
        else:
            print(f"NOT_IDENTICAL: length difference {len(data1)} vs {len(data2)}", file=sys.stderr)
        sys.exit(1)


COMMANDS = {
    "channel": cmd_channel,
    "validate_enum": cmd_validate_enum,
    "workflow_yaml": cmd_workflow_yaml,
    "workflow_permissions_deny_all": cmd_workflow_permissions_deny_all,
    "evidence_registry_entry": cmd_evidence_registry_entry,
    "infer_write_zero": cmd_infer_write_zero,
    "workflow_files_byte_identical": cmd_workflow_files_byte_identical,
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
