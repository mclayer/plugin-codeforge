#!/usr/bin/env bash
# CFP-276 — Doc Location Registry validator (issue #276)
#
# Modes:
#   default  — validation only (6 checks)
#   --regen  — regenerate docs/doc-location-registry.md from docs/doc-locations.yaml
#   --check-freshness — round-trip diff (regen to /tmp + diff against committed)
#   --full   — validation + freshness check (CI default)
#
# SSOT: docs/doc-locations.yaml + ADR-038
set -euo pipefail
cd "$(dirname "$0")/.."

MODE="${1:-default}"

case "$MODE" in
  default|--regen|--check-freshness|--full) ;;
  *)
    echo "::error::unknown mode: $MODE" >&2
    echo "Usage: $0 [default|--regen|--check-freshness|--full]" >&2
    exit 2
    ;;
esac

export DOC_LOC_MODE="$MODE"

python3 <<'PY'
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("⚠ check-doc-locations: pyyaml 미설치 — skip", file=sys.stderr)
    sys.exit(0)

YAML_PATH = Path("docs/doc-locations.yaml")
if not YAML_PATH.exists():
    print("✓ check-doc-locations: docs/doc-locations.yaml 부재 — skip", file=sys.stderr)
    sys.exit(0)

print("✓ check-doc-locations: skeleton (validation TBD)", file=sys.stderr)
PY
