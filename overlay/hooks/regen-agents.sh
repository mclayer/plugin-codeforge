#!/usr/bin/env bash
# regen-agents.sh — SessionStart hook for consumer projects
#
# Regenerates .claude/agents/*.md by merging plugin core + project overlay.
#
# Prerequisites:
#   - Plugin installed at ${CLAUDE_PLUGIN_ROOT:-...}/codeforge
#     (or checked out locally and pointed to via PLUGIN_ROOT env var)
#   - Consumer project has .claude/_overlay/agents/<Name>.md (optional per agent)
#     and optional .claude/_overlay/CLAUDE.md
#   - python3 available with PyYAML installed (`pip install pyyaml`)
#
# Usage (consumer .claude/settings.json) — schema-correct (CFP-106 fix #169):
#   {
#     "hooks": {
#       "SessionStart": [
#         {
#           "hooks": [
#             {
#               "type": "command",
#               "command": "bash ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/regen-agents.sh"
#             }
#           ]
#         }
#       ]
#     }
#   }
#
# Note: Claude Code hook schema = EventName -> [{ matcher?, hooks: [{type, command}] }].
#       Flat `{"command": "..."}` form 은 silently dropped — 반드시 nested 3-level 사용.
#       `${CLAUDE_PLUGIN_ROOT}` 는 plugin manifest 측 hook 에서만 자동 치환됨.
#       Consumer 가 직접 settings.json 에 작성 시 절대경로 또는 별도 env 사용 권장.
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
#   Priority: explicit $PLUGIN_ROOT > $CLAUDE_PLUGIN_ROOT/codeforge > script's parent .. ..
PLUGIN_ROOT="${PLUGIN_ROOT:-}"
if [ -z "$PLUGIN_ROOT" ]; then
    if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && [ -d "$CLAUDE_PLUGIN_ROOT/codeforge" ]; then
        PLUGIN_ROOT="$CLAUDE_PLUGIN_ROOT/codeforge"
    else
        # Fallback: script lives at <PLUGIN_ROOT>/overlay/hooks/regen-agents.sh
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
    fi
fi

MERGE_SCRIPT="$PLUGIN_ROOT/overlay/hooks/merge.py"
VALIDATE_SCRIPT="$PLUGIN_ROOT/overlay/hooks/validate_config.py"
BOOTSTRAP_CHECK_SCRIPT="$PLUGIN_ROOT/overlay/hooks/check-bootstrap.sh"
PLUGIN_AGENTS_DIR="$PLUGIN_ROOT/agents"
PLUGIN_CLAUDE_MD="$PLUGIN_ROOT/CLAUDE.md"

# Consumer project — invoke from project root.
PROJECT_ROOT="${PROJECT_ROOT:-$PWD}"
OVERLAY_DIR="$PROJECT_ROOT/.claude/_overlay"
OVERLAY_AGENTS_DIR="$OVERLAY_DIR/agents"
OVERLAY_CLAUDE_MD="$OVERLAY_DIR/CLAUDE.md"
OVERLAY_PROJECT_YAML="$OVERLAY_DIR/project.yaml"
OUT_AGENTS_DIR="$PROJECT_ROOT/.claude/agents"
OUT_CLAUDE_MD="$PROJECT_ROOT/CLAUDE.md"

if [ ! -f "$MERGE_SCRIPT" ]; then
    echo "[regen-agents] ERROR: merge.py not found at $MERGE_SCRIPT" >&2
    exit 1
fi
if [ ! -d "$PLUGIN_AGENTS_DIR" ]; then
    # CFP-40 ζ arc 후 wrapper agent 0개 — agents/ 디렉토리 부재 시 graceful skip
    # (lane plugin 들의 자체 regen-agents.sh 가 실제 agent merge 처리)
    echo "[regen-agents] codeforge wrapper agent 0개 (ζ arc wrapper-only) — lane plugin 으로 위임" >&2
    exit 0
fi

# Validate project.yaml schema (fail-fast if malformed or missing required fields).
# Missing file is a warning, not an error (consumer may be in initial setup).
if [ -f "$VALIDATE_SCRIPT" ]; then
    if ! python3 "$VALIDATE_SCRIPT" "$OVERLAY_PROJECT_YAML"; then
        echo "[regen-agents] ABORT: project.yaml schema violation — fix before session starts" >&2
        exit 1
    fi
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

# CFP-110: Auto-copy consumer-distributable scripts (manifest-driven).
# Runs AFTER agent regen + IMMEDIATELY BEFORE check-bootstrap.sh so Check 4 (CFP-97) sees
# scripts as present (no false WARN). Semantics: cp -n (atomic no-clobber, Codex AREA 2 P1
# fix) — only copies if consumer file absent. Respects CFP-109 manifest schema
# (`<script>[:<workflow>]`) + degraded mode suppression via missing_workflows.
CONSUMER_SCRIPTS_MANIFEST="$PLUGIN_ROOT/templates/consumer-scripts.manifest"
if [ -f "$CONSUMER_SCRIPTS_MANIFEST" ]; then
    # Read workflow_distribution.missing_workflows (CFP-89) for degraded suppression
    WD_MISSING_AUTO=""
    if [ -f "$OVERLAY_PROJECT_YAML" ]; then
        WD_MISSING_AUTO=$(python3 - "$OVERLAY_PROJECT_YAML" <<'PYEOF' 2>/dev/null
import sys
try:
    import yaml
    with open(sys.argv[1]) as f:
        data = yaml.safe_load(f) or {}
    wd = data.get("workflow_distribution", {})
    missing = wd.get("missing_workflows", []) or []
    print(",".join(missing))
except Exception:
    pass
PYEOF
)
    fi

    COPIED_SCRIPTS=()
    while IFS= read -r line; do
        # trim leading/trailing whitespace
        line="${line#"${line%%[![:space:]]*}"}"
        line="${line%"${line##*[![:space:]]}"}"
        case "$line" in '#'*|'') continue ;; esac
        # CFP-109: parse script-path[:dep-workflow]
        script_path="${line%%:*}"
        if [ "$script_path" = "$line" ]; then
            dep_workflow=""
        else
            dep_workflow="${line#*:}"
        fi
        # Path traversal + leading-dash guard (silent skip; manifest is plugin-trusted)
        # CFP-112 AREA 4b: leading `-` rejected to prevent option injection in cp/mkdir/chmod
        case "$script_path" in
            /*|*..*|-*) continue ;;
        esac
        # Degraded suppression — skip if dep workflow basename ∈ missing_workflows
        if [ -n "$dep_workflow" ] && [ -n "$WD_MISSING_AUTO" ]; then
            dep_basename_auto="$(basename "$dep_workflow")"
            if echo ",$WD_MISSING_AUTO," | grep -Fq ",$dep_basename_auto,"; then
                continue
            fi
        fi
        # cp -n atomic no-clobber. Track creation via existence delta.
        target="$PROJECT_ROOT/$script_path"
        source_path="$PLUGIN_ROOT/$script_path"
        if [ ! -f "$source_path" ]; then
            continue
        fi
        target_existed_before=0
        [ -f "$target" ] && target_existed_before=1
        mkdir -p "$(dirname "$target")"
        if cp -n "$source_path" "$target" 2>/dev/null; then
            if [ "$target_existed_before" -eq 0 ] && [ -f "$target" ]; then
                chmod +x "$target" 2>/dev/null || true
                COPIED_SCRIPTS+=("$script_path")
            fi
        fi
    done < "$CONSUMER_SCRIPTS_MANIFEST"

    if [ ${#COPIED_SCRIPTS[@]} -gt 0 ]; then
        echo "[regen-agents] auto-copied ${#COPIED_SCRIPTS[@]} consumer script(s) (CFP-110): ${COPIED_SCRIPTS[*]}" >&2
    fi
fi

# Bootstrap drift check (CFP-12) — non-blocking. WARN만 출력, hook 진행은 계속.
# CFP-11 발견 drift: org workflow permissions / 18 plugin label 부재 자동 검출.
# CFP-110 ordering: auto-copy 직후 실행 — Check 4 (CFP-97) 가 auto-copy 후 상태 검증.
if [ -x "$BOOTSTRAP_CHECK_SCRIPT" ]; then
    OVERLAY_PROJECT_YAML="$OVERLAY_PROJECT_YAML" bash "$BOOTSTRAP_CHECK_SCRIPT" || true
fi
