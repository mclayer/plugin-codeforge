#!/usr/bin/env python3
"""
read_version_pin.py — reads .codeforge.version_pin.version from project.yaml

Usage:
    python3 read_version_pin.py <path/to/project.yaml>

Stdout output (one of):
    PIN_ABSENT                          — codeforge.version_pin block not present
    PIN_MALFORMED:<reason>              — block present but invalid
    PIN_VERSION:<version_string>        — version found

Exit codes:
    0  — success (output printed)
    10 — PyYAML not available
    11 — parse error
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit(10)


def main() -> int:
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: read_version_pin.py <path/to/project.yaml>\n")
        return 11

    path = Path(sys.argv[1])
    if not path.exists():
        print("PIN_ABSENT")
        return 0

    try:
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except Exception as exc:
        sys.stderr.write(f"YAML parse error: {exc}\n")
        return 11

    if not isinstance(data, dict):
        print("PIN_MALFORMED:not_a_mapping")
        return 0

    codeforge = data.get("codeforge")
    if not codeforge or not isinstance(codeforge, dict):
        print("PIN_ABSENT")
        return 0

    version_pin = codeforge.get("version_pin")
    if version_pin is None:
        print("PIN_ABSENT")
        return 0

    if not isinstance(version_pin, dict):
        print("PIN_MALFORMED:not_a_mapping")
        return 0

    version = version_pin.get("version")
    if version is None:
        print("PIN_MALFORMED:no_version_field")
        return 0

    if not isinstance(version, str) or len(version.strip()) == 0:
        print("PIN_MALFORMED:empty_or_non_string")
        return 0

    print("PIN_VERSION:" + version.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
