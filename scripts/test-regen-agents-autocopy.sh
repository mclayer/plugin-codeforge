#!/usr/bin/env bash
# test-regen-agents-autocopy.sh — CFP-112 (Codex CFP-110 AREA 7) auto-copy self-test
#
# Verifies the CFP-110 auto-copy block in overlay/hooks/regen-agents.sh under 5 cases:
#   1. absent-target:      consumer scripts/<name> 부재 → cp 됨, COPIED_SCRIPTS reported
#   2. existing-target:    consumer scripts/<name> 존재 → 보존, content 변경 없음
#   3. traversal-skip:     manifest entry 가 ../ 또는 / prefix → silent skip
#   4. degraded-suppress:  workflow_distribution.missing_workflows 에 dep workflow → cp skip
#   5. nonblocking-fail:   source 부재 → silent skip, hook exit 0
#
# Strategy: build mock plugin/consumer trees in $PWD-relative tmp dirs and invoke
# regen-agents.sh with PLUGIN_ROOT + PROJECT_ROOT + OVERLAY_PROJECT_YAML overrides.
# Plugin agents/ dir intentionally absent → regen-agents.sh hits the "wrapper agent 0개"
# graceful skip path (line 64-69), but the auto-copy block runs BEFORE that check is hit?
# Actually no — auto-copy block runs after agent regen step (CFP-110 ordering), so wrapper
# 0-agent skip exits early. We need a sibling test that bypasses that skip, OR we ensure
# mock plugin has a dummy agents/ dir so regen proceeds.
#
# Decision: mock plugin has empty agents/ dir → regen runs with count=0 → proceeds to
# auto-copy block. This is the most realistic codeforge case (wrapper has 0 agents but
# auto-copy still runs).
#
# Plugin-internal CI test (consumer 미배포).

set -u

REPO_ROOT="${1:-$(pwd)}"
HOOK="$REPO_ROOT/overlay/hooks/regen-agents.sh"

if [ ! -f "$HOOK" ]; then
    echo "[autocopy-test] ERROR: regen-agents.sh not found: $HOOK" >&2
    exit 2
fi

PASS_COUNT=0
FAIL_COUNT=0
TMPROOT="$(mktemp -d -t cfp112.XXXXXX)"
trap 'rm -rf "$TMPROOT"' EXIT

# ----------------------------------------------------------------- helpers

# Build mock plugin/consumer skeleton + return paths via globals.
mock_setup() {
    local case_name="$1"
    local manifest_content="$2"
    local missing_workflows="${3:-}"  # comma-separated list of basenames; empty = full mode

    PLUGIN_DIR="$TMPROOT/$case_name/plugin"
    CONSUMER_DIR="$TMPROOT/$case_name/consumer"
    rm -rf "$TMPROOT/$case_name"
    mkdir -p "$PLUGIN_DIR/agents" "$PLUGIN_DIR/templates" "$PLUGIN_DIR/scripts" \
             "$PLUGIN_DIR/templates/github-workflows" \
             "$PLUGIN_DIR/overlay/hooks" \
             "$CONSUMER_DIR/.claude/_overlay"

    # Manifest
    printf '%s\n' "$manifest_content" > "$PLUGIN_DIR/templates/consumer-scripts.manifest"

    # Source script (real file with shebang) — referenced by manifest entries
    cat > "$PLUGIN_DIR/scripts/check-story-section-schema.sh" <<'SHEOF'
#!/usr/bin/env bash
echo "fixture script body"
SHEOF
    chmod +x "$PLUGIN_DIR/scripts/check-story-section-schema.sh"

    # Stub workflow yml (referenced from manifest dep workflow)
    cat > "$PLUGIN_DIR/templates/github-workflows/story-section-schema.yml" <<'YEOF'
name: stub
YEOF

    # Plugin-side merge.py + validate_config.py + check-bootstrap.sh stubs (regen-agents.sh
    # references these). Only need them to be valid path / non-error.
    cat > "$PLUGIN_DIR/overlay/hooks/merge.py" <<'PYEOF'
#!/usr/bin/env python3
import sys; sys.exit(0)
PYEOF
    chmod +x "$PLUGIN_DIR/overlay/hooks/merge.py"

    # Validate stub: always exit 0 (config valid). Skip if file absent.
    cat > "$PLUGIN_DIR/overlay/hooks/validate_config.py" <<'PYEOF'
#!/usr/bin/env python3
import sys; sys.exit(0)
PYEOF
    chmod +x "$PLUGIN_DIR/overlay/hooks/validate_config.py"

    # bootstrap stub (regen-agents.sh calls it; non-blocking with || true)
    cat > "$PLUGIN_DIR/overlay/hooks/check-bootstrap.sh" <<'SHEOF'
#!/usr/bin/env bash
exit 0
SHEOF
    chmod +x "$PLUGIN_DIR/overlay/hooks/check-bootstrap.sh"

    # Consumer overlay project.yaml — minimal; conditionally include workflow_distribution
    if [ -n "$missing_workflows" ]; then
        cat > "$CONSUMER_DIR/.claude/_overlay/project.yaml" <<EOF
project:
  name: test-consumer
github:
  org: testorg
  repo: testrepo
  default_branch: main
  pr_title_prefix_template: "[\${KEY}]"
  story_key_prefix: T
workflow_distribution:
  mode: degraded
  missing_workflows:
EOF
        for w in $(echo "$missing_workflows" | tr ',' ' '); do
            echo "    - $w" >> "$CONSUMER_DIR/.claude/_overlay/project.yaml"
        done
    else
        cat > "$CONSUMER_DIR/.claude/_overlay/project.yaml" <<EOF
project:
  name: test-consumer
github:
  org: testorg
  repo: testrepo
  default_branch: main
  pr_title_prefix_template: "[\${KEY}]"
  story_key_prefix: T
EOF
    fi

    # Copy actual hook from repo to plugin mock (so logic under test is the real script)
    cp "$REPO_ROOT/overlay/hooks/regen-agents.sh" "$PLUGIN_DIR/overlay/hooks/regen-agents.sh"
    chmod +x "$PLUGIN_DIR/overlay/hooks/regen-agents.sh"
}

# Run regen-agents.sh against the mock environment.
# Captures both stdout+stderr and exit code in globals (no `|| true` masking).
# Codex CFP-112 AREA 2 P2 fix.
LAST_HOOK_OUT=""
LAST_HOOK_EXIT=0
run_hook() {
    LAST_HOOK_OUT="$(
        cd "$CONSUMER_DIR" && \
        PLUGIN_ROOT="$PLUGIN_DIR" \
        PROJECT_ROOT="$CONSUMER_DIR" \
        OVERLAY_PROJECT_YAML="$CONSUMER_DIR/.claude/_overlay/project.yaml" \
        bash "$PLUGIN_DIR/overlay/hooks/regen-agents.sh" 2>&1
    )"
    LAST_HOOK_EXIT=$?
}

assert() {
    local case_name="$1"
    local desc="$2"
    local cond="$3"
    if [ "$cond" = "1" ]; then
        echo "[autocopy-test] PASS: $case_name — $desc"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "[autocopy-test] FAIL: $case_name — $desc" >&2
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

# ----------------------------------------------------------------- case 1: absent-target

mock_setup "case1-absent" "scripts/check-story-section-schema.sh:templates/github-workflows/story-section-schema.yml"
run_hook
target="$CONSUMER_DIR/scripts/check-story-section-schema.sh"
# Primary assertion: file-state (target created with expected content). Output text = secondary.
exists=0
[ -f "$target" ] && exists=1
content_match=0
[ "$exists" = "1" ] && grep -q "fixture script body" "$target" && content_match=1
[ "$exists" = "1" ] && [ "$content_match" = "1" ] && [ "$LAST_HOOK_EXIT" = "0" ] \
    && assert "case1-absent" "target created with expected content (exit=0)" 1 \
    || assert "case1-absent" "target created with expected content (exists=$exists, content_match=$content_match, exit=$LAST_HOOK_EXIT)" 0

# ----------------------------------------------------------------- case 2: existing-target

mock_setup "case2-existing" "scripts/check-story-section-schema.sh:templates/github-workflows/story-section-schema.yml"
mkdir -p "$CONSUMER_DIR/scripts"
echo "ORIGINAL" > "$CONSUMER_DIR/scripts/check-story-section-schema.sh"
run_hook
content="$(cat "$CONSUMER_DIR/scripts/check-story-section-schema.sh")"
[ "$content" = "ORIGINAL" ] && [ "$LAST_HOOK_EXIT" = "0" ] \
    && assert "case2-existing" "content preserved (exit=0)" 1 \
    || assert "case2-existing" "content preserved (got '$content', exit=$LAST_HOOK_EXIT)" 0

# ----------------------------------------------------------------- case 3: traversal-skip

# Pre-stage a sentinel file at a relative path the manifest would target IF traversal ran.
# Traversal entry `../../etc/passwd` would resolve from CONSUMER_DIR — verify the
# sentinel is NOT created/touched (state-based, Codex AREA 2 P2 fix).
mock_setup "case3-traversal" "../../etc/passwd"
TRAVERSAL_TARGET="$TMPROOT/case3-traversal/etc/passwd"
mkdir -p "$(dirname "$TRAVERSAL_TARGET")"
echo "SENTINEL" > "$TRAVERSAL_TARGET"
run_hook
sentinel_content="$(cat "$TRAVERSAL_TARGET" 2>/dev/null || echo MISSING)"
# State assertion: sentinel content must remain SENTINEL (no overwrite via traversal).
[ "$sentinel_content" = "SENTINEL" ] && [ "$LAST_HOOK_EXIT" = "0" ] \
    && assert "case3-traversal" "sentinel preserved (no traversal write, exit=0)" 1 \
    || assert "case3-traversal" "sentinel preserved (got '$sentinel_content', exit=$LAST_HOOK_EXIT)" 0

# ----------------------------------------------------------------- case 4: degraded-suppress

mock_setup "case4-degraded" \
    "scripts/check-story-section-schema.sh:templates/github-workflows/story-section-schema.yml" \
    "story-section-schema.yml"
run_hook
target="$CONSUMER_DIR/scripts/check-story-section-schema.sh"
exists=0
[ -f "$target" ] && exists=1
[ "$exists" = "0" ] && [ "$LAST_HOOK_EXIT" = "0" ] \
    && assert "case4-degraded" "degraded mode suppressed copy (exit=0)" 1 \
    || assert "case4-degraded" "degraded mode suppressed copy (exists=$exists, exit=$LAST_HOOK_EXIT)" 0

# ----------------------------------------------------------------- case 5: nonblocking-fail

mock_setup "case5-source-missing" "scripts/this-does-not-exist.sh"
run_hook
target="$CONSUMER_DIR/scripts/this-does-not-exist.sh"
target_exists=0
[ -f "$target" ] && target_exists=1
[ "$target_exists" = "0" ] && [ "$LAST_HOOK_EXIT" = "0" ] \
    && assert "case5-source-missing" "source missing → no copy, hook exit 0" 1 \
    || assert "case5-source-missing" "source missing → no copy, hook exit 0 (target_exists=$target_exists, exit=$LAST_HOOK_EXIT)" 0

# ----------------------------------------------------------------- summary

echo ""
echo "[autocopy-test] Summary: $PASS_COUNT pass, $FAIL_COUNT fail"

if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
fi
exit 0
