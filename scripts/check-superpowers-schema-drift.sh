#!/usr/bin/env bash
# scripts/check-superpowers-schema-drift.sh — wrapper SSOT vs superpowers snapshot drift (CFP-121).
#
# 2 check:
#   1. wrapper SSOT (docs/superpowers-integration.md §2) 가 참조하는 모든 superpowers skill
#      이 snapshot 파일 (templates/superpowers-skill-snapshot.txt) 에 존재하는가
#      (broken reference detection)
#   2. (optional, if local superpowers install exists) local install 의 skill 디렉토리 목록
#      이 snapshot 과 일치하는가 (early warning for snapshot 갱신 필요)
#
# Usage:
#   scripts/check-superpowers-schema-drift.sh
#     [--ssot <path>]      (default: docs/superpowers-integration.md)
#     [--snapshot <path>]  (default: templates/superpowers-skill-snapshot.txt)
#     [--local-install <dir>]  (default: ~/.claude/plugins/cache/claude-plugins-official/superpowers/<latest>/skills)
#     [--strict]           (check 2 fail → exit 1, default = warn-only)
#
# Exit: 0 pass / 1 fail (check 1) / 2 unknown arg

set -u

SSOT="docs/superpowers-integration.md"
SNAPSHOT="templates/superpowers-skill-snapshot.txt"
LOCAL_INSTALL=""
STRICT=0

while [ $# -gt 0 ]; do
  case "$1" in
    --ssot) SSOT="$2"; shift 2 ;;
    --snapshot) SNAPSHOT="$2"; shift 2 ;;
    --local-install) LOCAL_INSTALL="$2"; shift 2 ;;
    --strict) STRICT=1; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

FAIL=0

# --- Check 1: SSOT-referenced skills ⊆ snapshot ---
if [ ! -f "$SSOT" ]; then
  echo "FAIL: SSOT doc not found: $SSOT" >&2
  exit 1
fi
if [ ! -f "$SNAPSHOT" ]; then
  echo "FAIL: snapshot not found: $SNAPSHOT" >&2
  exit 1
fi

# Extract skill names referenced in SSOT (pattern: `superpowers:<name>`)
SSOT_SKILLS=$(grep -oE 'superpowers:[a-z][a-z0-9-]*' "$SSOT" | sed 's/^superpowers://' | sort -u)

# Extract snapshot skill names (skip comments + version header + empty lines)
SNAPSHOT_SKILLS=$(grep -vE '^\s*#|^\s*$|^SUPERPOWERS_VERSION:' "$SNAPSHOT" | tr -d ' \t' | grep -v '^$' | sort -u)

# Check: SSOT_SKILLS ⊆ SNAPSHOT_SKILLS
MISSING=$(comm -23 <(echo "$SSOT_SKILLS") <(echo "$SNAPSHOT_SKILLS"))
if [ -n "$MISSING" ]; then
  echo "FAIL check 1: SSOT references skills not in snapshot:" >&2
  echo "$MISSING" | sed 's/^/  - superpowers:/' >&2
  echo "" >&2
  echo "  Resolution: either" >&2
  echo "    (a) update snapshot file ($SNAPSHOT) to add the skill (if it exists in superpowers)" >&2
  echo "    (b) update SSOT ($SSOT §2) to remove the broken reference (if skill was deprecated)" >&2
  FAIL=$((FAIL+1))
fi

# --- Check 2: snapshot vs local install (advisory unless --strict) ---
if [ -z "$LOCAL_INSTALL" ]; then
  # Try to find latest install
  CACHE_BASE="$HOME/.claude/plugins/cache/claude-plugins-official/superpowers"
  if [ -d "$CACHE_BASE" ]; then
    LATEST=$(ls "$CACHE_BASE" 2>/dev/null | sort -V | tail -1)
    if [ -n "$LATEST" ] && [ -d "$CACHE_BASE/$LATEST/skills" ]; then
      LOCAL_INSTALL="$CACHE_BASE/$LATEST/skills"
    fi
  fi
fi

if [ -n "$LOCAL_INSTALL" ] && [ -d "$LOCAL_INSTALL" ]; then
  LOCAL_SKILLS=$(ls "$LOCAL_INSTALL" 2>/dev/null | sort -u)

  # Snapshot skills in local but not snapshot = local has new skills (snapshot needs update)
  LOCAL_NEW=$(comm -23 <(echo "$LOCAL_SKILLS") <(echo "$SNAPSHOT_SKILLS"))
  # Snapshot skills not in local = local is older (snapshot ahead)
  LOCAL_MISSING=$(comm -13 <(echo "$LOCAL_SKILLS") <(echo "$SNAPSHOT_SKILLS"))

  if [ -n "$LOCAL_NEW" ]; then
    echo "WARN check 2: local install has skills not in snapshot:" >&2
    echo "$LOCAL_NEW" | sed 's/^/  + /' >&2
    echo "  → snapshot may need update (likely superpowers version bump)" >&2
    [ "$STRICT" -eq 1 ] && FAIL=$((FAIL+1))
  fi
  if [ -n "$LOCAL_MISSING" ]; then
    echo "WARN check 2: snapshot has skills not in local install:" >&2
    echo "$LOCAL_MISSING" | sed 's/^/  - /' >&2
    echo "  → local superpowers may be older than snapshot (re-install recommended)" >&2
    [ "$STRICT" -eq 1 ] && FAIL=$((FAIL+1))
  fi
fi

if [ "$FAIL" -gt 0 ]; then
  echo "" >&2
  echo "FAILED: $FAIL check(s)" >&2
  exit 1
fi
exit 0
