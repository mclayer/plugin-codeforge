#!/usr/bin/env python3
"""
validate_sidecar.py — CFP-745 Wave 2 Story-5
Sidecar manifest schema validation helper.

Validates that the sidecar JSON has required fields:
  - schema_version (str)
  - managed_paths (list)

ADR-061 정합 — multi-line Python = 외부 .py 의무 (heredoc 금지)
reconcile-protocol-v1 §4.7 sidecar_manifest_schema SSOT
"""

import json
import sys

# Windows cp949 stdout encoding 차단 (CFP-1393 F8-FU / ADR-061 standardize)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def main():
    if len(sys.argv) < 2:
        print("[validate_sidecar] error: sidecar path argument required", file=sys.stderr)
        sys.exit(1)

    sidecar_path = sys.argv[1]

    try:
        with open(sidecar_path, encoding="utf-8") as f:
            d = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[validate_sidecar] sidecar parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if "schema_version" not in d:
        print("[validate_sidecar] schema_version missing", file=sys.stderr)
        sys.exit(1)

    if "managed_paths" not in d:
        print("[validate_sidecar] managed_paths missing", file=sys.stderr)
        sys.exit(1)

    if not isinstance(d["managed_paths"], list):
        print("[validate_sidecar] managed_paths must be a list", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
