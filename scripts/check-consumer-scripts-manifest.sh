#!/usr/bin/env bash
# check-consumer-scripts-manifest.sh — CFP-109 manifest validation lint
#
# Validates templates/consumer-scripts.manifest entries:
#   1. Format: <script-path>[:<dependent-workflow-path>]  — at most 1 colon
#   2. Path traversal reject: no leading '/' or '..' segment in either path
#   3. Script existence: script_path file exists in plugin repo
#   4. Script executable: -x permission on script_path (Linux/macOS perm bit)
#   5. Workflow existence (if specified): dep_workflow file exists
#   6. Workflow path constraint: dep_workflow must be templates/github-workflows/*.yml
#
# Plugin-internal CI lint (NOT consumer-distributable).
#
# Usage:
#   bash scripts/check-consumer-scripts-manifest.sh [<manifest-path>] [<plugin-root>]
#     manifest-path: defaults to templates/consumer-scripts.manifest
#     plugin-root: defaults to current working directory
#
# Output: per-entry PASS/FAIL line + total + exit code
#   exit 0 = all entries valid
#   exit 1 = at least 1 entry FAIL
#   exit 2 = manifest file not found / argument error

set -u

MANIFEST="${1:-templates/consumer-scripts.manifest}"
PLUGIN_ROOT="${2:-$(pwd)}"

# Support both absolute and relative manifest paths
case "$MANIFEST" in
    /*) MANIFEST_FULL="$MANIFEST" ;;
    *)  MANIFEST_FULL="$PLUGIN_ROOT/$MANIFEST" ;;
esac

if [ ! -f "$MANIFEST_FULL" ]; then
    echo "[manifest-lint] ERROR: manifest not found: $MANIFEST_FULL" >&2
    exit 2
fi

cd -- "$PLUGIN_ROOT" || { echo "[manifest-lint] ERROR: cd failed: $PLUGIN_ROOT" >&2; exit 2; }

PASS_COUNT=0
FAIL_COUNT=0
LINE_NUM=0

while IFS= read -r line; do
    LINE_NUM=$((LINE_NUM + 1))
    # trim leading/trailing whitespace
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    case "$line" in '#'*|'') continue ;; esac

    # Format: ≤1 colon
    colon_count="$(echo "$line" | tr -cd ':' | wc -c | tr -d ' ')"
    if [ "$colon_count" -gt 1 ]; then
        echo "[manifest-lint] FAIL line $LINE_NUM: too many colons (got $colon_count, max 1): $line" >&2
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi

    # Parse parts
    script_path="${line%%:*}"
    if [ "$script_path" = "$line" ]; then
        dep_workflow=""
    else
        dep_workflow="${line#*:}"
    fi

    # CFP-109 P1 (Codex AREA 2): explicit trailing-colon FAIL
    # Trailing colon (e.g. `scripts/foo.sh:`) silently treated as no workflow before — now reject.
    if [ "$colon_count" -eq 1 ] && [ -z "$dep_workflow" ]; then
        echo "[manifest-lint] FAIL line $LINE_NUM: trailing colon with empty workflow: $line" >&2
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi
    # Leading colon (empty script_path)
    if [ -z "$script_path" ]; then
        echo "[manifest-lint] FAIL line $LINE_NUM: empty script_path: $line" >&2
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi

    entry_fail=0

    # Check 2a: path traversal + leading-dash on script_path (CFP-112 AREA 4b)
    case "$script_path" in
        /*)
            echo "[manifest-lint] FAIL line $LINE_NUM: script absolute path: $script_path" >&2
            entry_fail=1
            ;;
        *..*)
            echo "[manifest-lint] FAIL line $LINE_NUM: script path traversal ('..'): $script_path" >&2
            entry_fail=1
            ;;
        -*)
            echo "[manifest-lint] FAIL line $LINE_NUM: script leading-dash (option-injection risk): $script_path" >&2
            entry_fail=1
            ;;
    esac

    # Check 2b: path traversal + leading-dash on dep_workflow (if present, CFP-112 AREA 4b)
    if [ -n "$dep_workflow" ]; then
        case "$dep_workflow" in
            /*)
                echo "[manifest-lint] FAIL line $LINE_NUM: workflow absolute path: $dep_workflow" >&2
                entry_fail=1
                ;;
            *..*)
                echo "[manifest-lint] FAIL line $LINE_NUM: workflow path traversal ('..'): $dep_workflow" >&2
                entry_fail=1
                ;;
            -*)
                echo "[manifest-lint] FAIL line $LINE_NUM: workflow leading-dash (option-injection risk): $dep_workflow" >&2
                entry_fail=1
                ;;
        esac
    fi

    # Skip subsequent checks if path is malformed
    if [ "$entry_fail" -ne 0 ]; then
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi

    # Check 3: script file exists
    if [ ! -f "$script_path" ]; then
        echo "[manifest-lint] FAIL line $LINE_NUM: script not found: $script_path" >&2
        entry_fail=1
    fi

    # Check 4: script executable (perm bit) — 확장자-인지 면제 (CFP-2408, 설계리뷰 P1#1)
    # 면제 = 말단확장자 ∈ {.tsv,.mjs} (데이터/import-only ESM) AND 경로에
    # exec-script 확장자(.sh/.py/.ps1/.bash)가 어디에도 부재. 이중확장
    # (scripts/foo.sh.txt / x.sh.tsv 류)은 exec-script 확장자 보유 → strict 우선
    # → 여전히 FAIL (strictness ratchet 보존). 광역 allowlist(.md/.txt/.json 등)는
    # 본 Story 등록 대상 0건 → 면제 안 함(strict branch).
    exempt=0
    case "$script_path" in
        *.tsv|*.mjs)  # 말단확장자 = 데이터/import-only
            case "$script_path" in
                *.sh|*.sh.*|*.py|*.py.*|*.ps1|*.ps1.*|*.bash|*.bash.*)
                    exempt=0 ;;          # 이중확장(.sh.tsv 등) = exec-script 확장자 보유 → strict 우선
                *) exempt=1 ;;           # 순수 .tsv/.mjs 만 면제
            esac
            ;;
    esac
    if [ "$exempt" -eq 0 ] && [ -f "$script_path" ] && [ ! -x "$script_path" ]; then
        echo "[manifest-lint] FAIL line $LINE_NUM: script not executable: $script_path" >&2
        entry_fail=1
    fi

    # Check 5+6: dep workflow validation
    if [ -n "$dep_workflow" ]; then
        # Check 6: must be templates/github-workflows/*.{yml,yaml} — direct child only (CFP-112 AREA 3)
        # GitHub Actions accepts both .yml and .yaml; sub-directories are not workflow paths.
        case "$dep_workflow" in
            templates/github-workflows/*/*)
                echo "[manifest-lint] FAIL line $LINE_NUM: workflow sub-directory not allowed: $dep_workflow" >&2
                entry_fail=1
                ;;
            templates/github-workflows/*.yml|templates/github-workflows/*.yaml) ;;
            *)
                echo "[manifest-lint] FAIL line $LINE_NUM: workflow must match 'templates/github-workflows/*.{yml,yaml}': $dep_workflow" >&2
                entry_fail=1
                ;;
        esac

        # Check 5: workflow file exists
        if [ ! -f "$dep_workflow" ]; then
            echo "[manifest-lint] FAIL line $LINE_NUM: workflow not found: $dep_workflow" >&2
            entry_fail=1
        fi
    fi

    if [ "$entry_fail" -ne 0 ]; then
        FAIL_COUNT=$((FAIL_COUNT + 1))
    else
        echo "[manifest-lint] PASS line $LINE_NUM: $line"
        PASS_COUNT=$((PASS_COUNT + 1))
    fi
done < "$MANIFEST_FULL"

echo ""
echo "[manifest-lint] Summary: $PASS_COUNT pass, $FAIL_COUNT fail"

if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
fi
exit 0

