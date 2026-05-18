#!/usr/bin/env python3
"""
get_consumer_tier.py — CFP-932 Phase 2 — consumer project.yaml channel tier 취득
ADR-061 §결정 5: multi-line Python (>5줄) → 외부 .py 파일 (check-channel-drift.sh 위임)

Usage:
  python3 scripts/get_consumer_tier.py <project_yaml_path>

Exit codes:
  0 = success — prints tier to stdout
  1 = file absent (prints "absent")
  2 = YAML parse error (prints PARSE_ERROR to stderr, fail-loud)

spec §3.3 line 135 + §7.1 EP-3 line 269:
  absent(graceful stable) ≠ broken(명시 error) 분기 보존
  broken YAML → exit 2 (silent stable fallback 금지)
"""

import sys
import yaml


def main():
    if len(sys.argv) < 2:
        print("Usage: get_consumer_tier.py <project_yaml_path>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]

    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print("absent")
        sys.exit(0)
    except yaml.YAMLError as e:
        print(f"PARSE_ERROR: {path}: {e}", file=sys.stderr)
        sys.exit(2)

    codeforge = (data or {}).get("codeforge", {}) or {}
    channel = codeforge.get("channel") or {}
    tier = (channel if isinstance(channel, dict) else {}).get("tier", "stable")
    print(tier)
    sys.exit(0)


if __name__ == "__main__":
    main()
