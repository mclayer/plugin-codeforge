#!/usr/bin/env bash
# extract-security-ai.sh
# CFP-688 Amendment 3 §결정 5.G / ADR-026 §결정 5.G.b — TC-4 carrier
# lanes.security_ai field extraction from consumer project.yaml
#
# ADR-061 §결정 1: external script (replaces inline workflow heredoc).
# ADR-026 §결정 5.A + Inv-2: fail-closed strict semantic.
#
# Usage:
#   bash scripts/extract-security-ai.sh <cfg_path>
#
# Output (stdout):
#   true    — lanes.security_ai is explicitly "true"
#   false   — lanes.security_ai is explicitly "false" (security opt-in disabled)
#   missing — file absent, field absent, or read error (fail-closed → phase:보안-테스트)
#
# Exit codes:
#   0 — value emitted to stdout (always exits 0 — caller handles missing/true/false semantics)
#
# Inv-2 (ADR-026 §결정 5.A): fail-closed default = phase:보안-테스트.
#   Caller MUST treat "missing" as phase:보안-테스트 (NOT phase:구현-테스트).
#   Only explicit "false" → phase:구현-테스트.
#
# Security (ADR-026 §9 T-NEW-2):
#   - argv[1] = cfg file path only (no shell expansion beyond $1)
#   - yaml parse via python3 minimal scope (no eval/exec/subprocess)
#   - output = "true" / "false" / "missing" only (no other string passthrough)

set -uo pipefail

# ── Input validation ──────────────────────────────────────────────────────────

cfg="${1:-}"

if [ -z "$cfg" ]; then
  echo "missing"
  exit 0
fi

if [ ! -f "$cfg" ]; then
  echo "missing"
  exit 0
fi

# ── Read lanes.security_ai via yq (primary) → python3 (fallback) ─────────────
# Mirror pattern: story-init.yml lines 37-68 (yq → python3 fallback).
# Primary (yq): reads .lanes.security_ai strictly — no // default coercion.
# Fallback (python3): regex-based parser (no external yaml dep required).

_read_via_yq() {
  local file="$1"
  # yq 4.x: null output when field absent (unlike // "false" coercion).
  local val
  val=$(yq -r '.lanes.security_ai' "$file" 2>/dev/null) || return 1
  if [ "$val" = "null" ] || [ -z "$val" ]; then
    echo "missing"
  elif [ "$val" = "true" ]; then
    echo "true"
  elif [ "$val" = "false" ]; then
    echo "false"
  else
    # Unexpected value — treat as missing (fail-closed)
    echo "missing"
  fi
}

_read_via_python3() {
  local file="$1"
  CFG_PATH="$file" python3 - <<'PY'
import os
import re
import sys

path = os.environ.get("CFG_PATH", "")
if not path or not os.path.isfile(path):
    print("missing")
    sys.exit(0)

in_lanes = False
try:
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            # Detect top-level section header (e.g. "lanes:")
            if re.match(r"^[A-Za-z_][\w-]*:\s*$", line):
                in_lanes = (line.split(":", 1)[0].strip() == "lanes")
                continue
            if in_lanes:
                m = re.match(r"^\s{2}security_ai:\s*(.*?)\s*$", line)
                if m:
                    val = m.group(1).strip().strip('"').strip("'")
                    if val == "true":
                        print("true")
                    elif val == "false":
                        print("false")
                    else:
                        print("missing")
                    sys.exit(0)
                # Another top-level key ends lanes section
                if re.match(r"^[A-Za-z_]", line):
                    break
except Exception:
    print("missing")
    sys.exit(0)

print("missing")
PY
}

# ── Execute extraction ────────────────────────────────────────────────────────

if command -v yq >/dev/null 2>&1; then
  _read_via_yq "$cfg"
else
  _read_via_python3 "$cfg"
fi
