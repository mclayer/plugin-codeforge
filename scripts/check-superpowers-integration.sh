#!/usr/bin/env bash
# scripts/check-superpowers-integration.sh
# CFP-113 — superpowers integration lint (3 check)
#   1. SSOT §2 row count vs agent md superpowers reference count (drift)
#   2. agent md 의 stale `docs/superpowers/**` 권한 표기 detection
#   3. agent md 의 helper fragment inline copy detection (link 만 허용)
#
# Usage:
#   scripts/check-superpowers-integration.sh
#     [--ssot <path>]         (default: docs/superpowers-integration.md)
#     [--agent-glob <glob>]   (default: lane plugin sibling clones)
#     [--helpers-dir <path>]  (default: templates/skill-prompt-helpers/)
#
# Exit: 0 pass / 1 fail (any check)

set -u

SSOT="docs/superpowers-integration.md"
AGENT_GLOB=""
HELPERS_DIR="templates/skill-prompt-helpers"

while [ $# -gt 0 ]; do
  case "$1" in
    --ssot) SSOT="$2"; shift 2 ;;
    --agent-glob) AGENT_GLOB="$2"; shift 2 ;;
    --helpers-dir) HELPERS_DIR="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

FAIL=0

# --- Check 1: SSOT row count vs agent superpowers reference count ---
if [ ! -f "$SSOT" ]; then
  echo "FAIL: SSOT doc not found: $SSOT" >&2
  FAIL=$((FAIL+1))
else
  # Count §2 table rows. Strategy: rows starting with "| " AND containing "superpowers:".
  # This counts each invocation point (handles both fixture 1-row and real SSOT 23-row).
  # NOTE: grep -c always outputs a count (even 0). Don't add `|| echo 0` — that double-emits.
  SSOT_ROWS=$(grep -c '^| .*superpowers:' "$SSOT" 2>/dev/null)
  SSOT_ROWS=${SSOT_ROWS:-0}

  # Count agent md files referencing "superpowers:" in real content (not in code blocks)
  AGENT_FILES=()
  if [ -n "$AGENT_GLOB" ]; then
    # Use glob expansion via shell
    for f in $AGENT_GLOB; do
      [ -f "$f" ] && AGENT_FILES+=("$f")
    done
  else
    # Default: search lane plugin sibling clones
    for sibling in ../plugin-codeforge-requirements ../plugin-codeforge-design ../plugin-codeforge-review ../plugin-codeforge-develop ../plugin-codeforge-test ../plugin-codeforge-pmo; do
      if [ -d "$sibling/agents" ]; then
        for f in "$sibling"/agents/*.md; do
          [ -f "$f" ] && AGENT_FILES+=("$f")
        done
      fi
    done
  fi

  AGENT_COUNT=0
  for f in "${AGENT_FILES[@]:-}"; do
    [ -z "$f" ] && continue
    if grep -q "superpowers:" "$f" 2>/dev/null; then
      AGENT_COUNT=$((AGENT_COUNT+1))
    fi
  done

  # Drift detection: row count must match agent count (when agents present)
  if [ "$AGENT_COUNT" -gt 0 ] && [ "$SSOT_ROWS" -lt "$AGENT_COUNT" ]; then
    echo "FAIL check 1: SSOT row count ($SSOT_ROWS) < agent superpowers reference count ($AGENT_COUNT) — drift detected" >&2
    FAIL=$((FAIL+1))
  fi
fi

# --- Check 2: agent md stale `docs/superpowers/**` permission ---
STALE_FILES=""
if [ -n "${AGENT_FILES[*]:-}" ]; then
  for f in "${AGENT_FILES[@]}"; do
    [ -z "$f" ] && continue
    if grep -qE 'Edit\(docs/superpowers/|Write\(docs/superpowers/' "$f" 2>/dev/null; then
      STALE_FILES="$STALE_FILES  $f"$'\n'
    fi
  done
fi
if [ -n "$STALE_FILES" ]; then
  echo "FAIL check 2: stale 'docs/superpowers/**' permission in:" >&2
  echo -n "$STALE_FILES" >&2
  FAIL=$((FAIL+1))
fi

# --- Check 3: helper fragment inline copy detection ---
if [ -d "$HELPERS_DIR" ] && [ -n "${AGENT_FILES[*]:-}" ]; then
  for fragment in "$HELPERS_DIR"/*.md; do
    [ -f "$fragment" ] || continue
    DISTINCT_LINE=$(grep -m1 "When invoking" "$fragment" 2>/dev/null || true)
    if [ -n "$DISTINCT_LINE" ]; then
      INLINE_FILES=""
      for f in "${AGENT_FILES[@]}"; do
        [ -z "$f" ] && continue
        if grep -qF "$DISTINCT_LINE" "$f" 2>/dev/null; then
          INLINE_FILES="$INLINE_FILES  $f"$'\n'
        fi
      done
      if [ -n "$INLINE_FILES" ]; then
        echo "FAIL check 3: helper fragment '$fragment' inline-copied in:" >&2
        echo -n "$INLINE_FILES" >&2
        FAIL=$((FAIL+1))
      fi
    fi
  done
fi

if [ "$FAIL" -gt 0 ]; then
  echo "" >&2
  echo "FAILED: $FAIL check(s)" >&2
  exit 1
fi
exit 0
