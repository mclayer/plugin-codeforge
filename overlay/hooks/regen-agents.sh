#!/usr/bin/env bash
# regen-agents.sh — SessionStart hook for consumer projects
#
# Regenerates .claude/agents/*.md by merging plugin core + project overlay.
#
# Prerequisites:
#   - Plugin installed at ${CLAUDE_PLUGIN_ROOT:-...}/dev-orchestrator
#     (or checked out locally and pointed to via PLUGIN_ROOT env var)
#   - Consumer project has .claude/_overlay/agents/<Name>.md (optional per agent)
#     and optional .claude/_overlay/CLAUDE.md
#   - python3 available with PyYAML installed (`pip install pyyaml`)
#
# Usage (consumer .claude/settings.json):
#   {
#     "hooks": {
#       "SessionStart": [
#         { "command": "bash ${CLAUDE_PLUGIN_ROOT}/dev-orchestrator/overlay/hooks/regen-agents.sh" }
#       ]
#     }
#   }
#
# Behavior:
#   - For each agent in plugin's agents/, emits .claude/agents/<Name>.md as
#     core + overlay merged output. Overlay absent → core-only copy.
#   - Also regenerates CLAUDE.md if consumer has .claude/_overlay/CLAUDE.md.
#   - Idempotent — safe to run every session start.
#   - Errors are emitted to stderr; hook aborts on first failure to surface
#     drift rather than silently write partial state.

set -euo pipefail

# Resolve plugin root.
#   Priority: explicit $PLUGIN_ROOT > $CLAUDE_PLUGIN_ROOT/dev-orchestrator > script's parent .. ..
PLUGIN_ROOT="${PLUGIN_ROOT:-}"
if [ -z "$PLUGIN_ROOT" ]; then
    if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && [ -d "$CLAUDE_PLUGIN_ROOT/dev-orchestrator" ]; then
        PLUGIN_ROOT="$CLAUDE_PLUGIN_ROOT/dev-orchestrator"
    else
        # Fallback: script lives at <PLUGIN_ROOT>/overlay/hooks/regen-agents.sh
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
    fi
fi

MERGE_SCRIPT="$PLUGIN_ROOT/overlay/hooks/merge.py"
PLUGIN_AGENTS_DIR="$PLUGIN_ROOT/agents"
PLUGIN_CLAUDE_MD="$PLUGIN_ROOT/CLAUDE.md"

# Consumer project — invoke from project root.
PROJECT_ROOT="${PROJECT_ROOT:-$PWD}"
OVERLAY_DIR="$PROJECT_ROOT/.claude/_overlay"
OVERLAY_AGENTS_DIR="$OVERLAY_DIR/agents"
OVERLAY_CLAUDE_MD="$OVERLAY_DIR/CLAUDE.md"
OUT_AGENTS_DIR="$PROJECT_ROOT/.claude/agents"
OUT_CLAUDE_MD="$PROJECT_ROOT/CLAUDE.md"

if [ ! -f "$MERGE_SCRIPT" ]; then
    echo "[regen-agents] ERROR: merge.py not found at $MERGE_SCRIPT" >&2
    exit 1
fi
if [ ! -d "$PLUGIN_AGENTS_DIR" ]; then
    echo "[regen-agents] ERROR: plugin agents/ not found at $PLUGIN_AGENTS_DIR" >&2
    exit 1
fi

mkdir -p "$OUT_AGENTS_DIR"

# Regenerate each core agent (with optional overlay on top)
count=0
for core in "$PLUGIN_AGENTS_DIR"/*.md; do
    [ -f "$core" ] || continue
    name="$(basename "$core")"
    overlay="$OVERLAY_AGENTS_DIR/$name"
    out="$OUT_AGENTS_DIR/$name"

    if [ -f "$overlay" ]; then
        python3 "$MERGE_SCRIPT" "$core" "$overlay" > "$out"
    else
        python3 "$MERGE_SCRIPT" "$core" > "$out"
    fi
    count=$((count + 1))
done

# Pick up overlay-only agents (consumer-defined, no core counterpart —
# e.g., preset imports or project-custom agents)
overlay_only_count=0
if [ -d "$OVERLAY_AGENTS_DIR" ]; then
    for overlay in "$OVERLAY_AGENTS_DIR"/*.md; do
        [ -f "$overlay" ] || continue
        name="$(basename "$overlay")"
        core="$PLUGIN_AGENTS_DIR/$name"
        out="$OUT_AGENTS_DIR/$name"

        # Skip if already merged by core pass
        [ -f "$core" ] && continue

        python3 "$MERGE_SCRIPT" --overlay-only "$overlay" > "$out"
        overlay_only_count=$((overlay_only_count + 1))
    done
fi

# Regenerate CLAUDE.md (only if consumer has overlay CLAUDE.md)
if [ -f "$PLUGIN_CLAUDE_MD" ] && [ -f "$OVERLAY_CLAUDE_MD" ]; then
    python3 "$MERGE_SCRIPT" "$PLUGIN_CLAUDE_MD" "$OVERLAY_CLAUDE_MD" > "$OUT_CLAUDE_MD"
    echo "[regen-agents] regenerated $count core + $overlay_only_count overlay-only agents + CLAUDE.md" >&2
else
    echo "[regen-agents] regenerated $count core + $overlay_only_count overlay-only agents (no CLAUDE.md overlay)" >&2
fi
