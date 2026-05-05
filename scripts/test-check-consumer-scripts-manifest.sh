#!/usr/bin/env bash
# test-check-consumer-scripts-manifest.sh — CFP-109 lint script self-test
#
# Asserts each fixture in scripts/test-fixtures/consumer-scripts-manifest/
# produces the expected exit code from scripts/check-consumer-scripts-manifest.sh:
#   - valid-*.manifest    → exit 0
#   - fail-*.manifest     → exit 1
#
# Plugin-internal CI test (Codex AREA 7 P1 fix).

set -u

REPO_ROOT="${1:-$(pwd)}"
LINT="$REPO_ROOT/scripts/check-consumer-scripts-manifest.sh"
FIXTURE_DIR="$REPO_ROOT/scripts/test-fixtures/consumer-scripts-manifest"

if [ ! -f "$LINT" ]; then
    echo "[self-test] ERROR: lint script not found: $LINT" >&2
    exit 2
fi
if [ ! -d "$FIXTURE_DIR" ]; then
    echo "[self-test] ERROR: fixture dir not found: $FIXTURE_DIR" >&2
    exit 2
fi

PASS_COUNT=0
FAIL_COUNT=0

for fixture in "$FIXTURE_DIR"/*.manifest; do
    [ -f "$fixture" ] || continue
    fname="$(basename "$fixture")"

    case "$fname" in
        valid-*) expected_exit=0 ;;
        fail-*)  expected_exit=1 ;;
        *)
            echo "[self-test] SKIP: unknown fixture name pattern: $fname" >&2
            continue
            ;;
    esac

    # Run lint with this fixture (silent on stderr — we only check exit)
    bash "$LINT" "$fixture" "$REPO_ROOT" >/dev/null 2>&1
    actual_exit=$?

    if [ "$actual_exit" -eq "$expected_exit" ]; then
        echo "[self-test] PASS: $fname (exit=$actual_exit, expected=$expected_exit)"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "[self-test] FAIL: $fname (exit=$actual_exit, expected=$expected_exit)" >&2
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
done

echo ""
echo "[self-test] Summary: $PASS_COUNT pass, $FAIL_COUNT fail"

if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
fi
exit 0
