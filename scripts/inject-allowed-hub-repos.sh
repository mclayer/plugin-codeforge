#!/bin/bash
# inject-allowed-hub-repos.sh
# Idempotent post-reconcile injection of consumer ALLOWED_HUB_REPOS extensions
# into GitHub workflow env vars. ADR-116 consumer-applicability (idempotent reconcile-then-patch).
#
# Mechanism:
#  1. Read consumer .claude/_overlay/project.yaml phase_gate.allowed_hub_repos[]
#  2. For each .github/workflows/*.{yml,yaml} containing ALLOWED_HUB_REPOS env:
#     - Merge template default + project.yaml entries (dedup, never-reduce)
#     - Rewrite env value line (only ALLOWED_HUB_REPOS, rest untouched)
#  3. Idempotent: re-run = same result (dedup guards)
#
# Usage:
#  bash scripts/inject-allowed-hub-repos.sh [--repo <consumer-root>] [--dry-run]
#
# Exit:
#  0 = success (or no-op)
#  1 = error (YAML parse / file not writable / invalid entry format)

set -euo pipefail

# D2: bash 4+ version guard (CFP-2057, ADR-116 §결정 4)
# declare -A (associative array) 는 bash 4.0+ 전용 — bash 3.2 (macOS 기본) 미지원.
# 실행 환경 = CI/Linux (bash ≥5) 한정; 이 guard 가 macOS silent 실패를 명시 거부로 전환.
if [ -z "${BASH_VERSINFO:-}" ] || [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
  echo "ERROR: requires bash >= 4 (declare -A associative array). macOS 기본 bash 3.2 미지원 — brew install bash 또는 CI/Linux 에서 실행." >&2
  exit 1
fi

REPO_ROOT="${REPO_ROOT:-.}"
DRY_RUN=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse CLI args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_ROOT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    *)
      echo "Usage: $0 [--repo <consumer-root>] [--dry-run]" >&2
      exit 1
      ;;
  esac
done

PROJECT_YAML="${REPO_ROOT}/.claude/_overlay/project.yaml"
WORKFLOWS_DIR="${REPO_ROOT}/.github/workflows"

# Validate YAML, extract phase_gate.allowed_hub_repos[]
# Exit 0 if field absent, exit 1 on parse error.
# 호출자가 반환코드를 직접 확인하도록 output 변수로 사용 — set -e 환경에서
# 프로세스 치환(<(...))은 exit 코드 전파 보장이 없으므로 명시 처리.
extract_allowed_repos() {
  local project_yaml="$1"
  python3 "${SCRIPT_DIR}/lib/extract_allowed_hub_repos.py" "$project_yaml"
  return $?
}

# Template default ALLOWED_HUB_REPOS value
TEMPLATE_DEFAULT="github.com/mclayer/codeforge-internal-docs"

# Validate repo entry format (domain/owner/repo, e.g. github.com/mclayer/mctrader-hub)
# Positive charset whitelist: only alphanumeric, dot, underscore, hyphen in each segment
validate_repo_entry() {
  local entry="$1"
  # Pattern: 3 segments separated by exactly 2 slashes
  # Each segment: [A-Za-z0-9._-]+ (alphanumeric, dot, underscore, hyphen)
  # Rejects: commas, quotes, spaces, semicolons, newlines, parens, shell metacharacters
  if [[ ! "$entry" =~ ^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$ ]]; then
    echo "WARN: Invalid repo entry format (skip): $entry" >&2
    return 1
  fi
  return 0
}

# Merge template default + project.yaml entries, dedup, output comma-separated
merge_allowed_repos() {
  local project_yaml="$1"
  # Use associative array (bash 4+) to track uniqueness
  declare -A seen
  local -a result

  # Template default first
  result+=("$TEMPLATE_DEFAULT")
  seen["$TEMPLATE_DEFAULT"]=1

  # Project.yaml entries (from extract_allowed_repos)
  # YAML parse error propagation: 프로세스 치환(<(...)) 은 set -e 내에서
  # 하위 프로세스 exit code 를 보장하지 않으므로, 먼저 직접 실행해 성공 여부 확인.
  if [[ -f "$project_yaml" ]]; then
    local extract_output
    if ! extract_output=$(python3 "${SCRIPT_DIR}/lib/extract_allowed_hub_repos.py" "$project_yaml" 2>&1); then
      # YAML parse error (exit 1 from python) — 상위로 전파
      echo "$extract_output" >&2
      return 1
    fi
    # stdout 만 재사용 (stderr 는 이미 소비)
    while IFS= read -r repo_entry; do
      [[ -z "$repo_entry" ]] && continue
      # Trim leading/trailing whitespace using bash parameter expansion (no xargs)
      repo_entry="${repo_entry#"${repo_entry%%[![:space:]]*}"}"
      repo_entry="${repo_entry%"${repo_entry##*[![:space:]]}"}"
      [[ -z "$repo_entry" ]] && continue
      if validate_repo_entry "$repo_entry"; then
        # Dedup: skip if already seen
        if [[ "${seen[$repo_entry]:-}" != "1" ]]; then
          result+=("$repo_entry")
          seen["$repo_entry"]=1
        fi
      fi
    done <<< "$extract_output"
  fi

  # Output comma-separated, quoted for YAML env value
  local merged=""
  for repo in "${result[@]}"; do
    if [[ -z "$merged" ]]; then
      merged="$repo"
    else
      merged="${merged},${repo}"
    fi
  done

  echo "$merged"
}

# Inject merged value into workflow env line
# Input: workflow file path, merged value
# Output: rewritten file (or stdout in dry-run)
inject_workflow_env() {
  local workflow_file="$1"
  local merged_value="$2"

  # Find ALLOWED_HUB_REPOS env line, rewrite value only
  # Pattern: ALLOWED_HUB_REPOS: "..." (double-quoted only)
  # Detect quote style mismatch and warn

  if [[ "$DRY_RUN" == 1 ]]; then
    echo "=== DRY-RUN: Would inject into $workflow_file ==="
    sed -n '/^[[:space:]]*ALLOWED_HUB_REPOS:/p' "$workflow_file" || true
    echo "New value: ALLOWED_HUB_REPOS: \"$merged_value\""
    echo ""
  else
    # Check if line exists with double-quotes (expected format)
    if ! grep -q '^[[:space:]]*ALLOWED_HUB_REPOS:[[:space:]]*".*"[[:space:]]*$' "$workflow_file"; then
      # Line with different quote style found, warn but skip rewrite
      if grep -q '^[[:space:]]*ALLOWED_HUB_REPOS:' "$workflow_file"; then
        echo "WARN: ALLOWED_HUB_REPOS line found but value not rewritten (quote style mismatch): $workflow_file" >&2
        return 1
      fi
      return 0
    fi

    # In-place rewrite using AWK
    # Match: ALLOWED_HUB_REPOS: "<anything>" → ALLOWED_HUB_REPOS: "<merged_value>"
    # Use temporary file (PID-isolated, $$ suffix) to avoid sed portability issues.
    # D3 (CFP-2057, CWE-377 완화): /tmp 고정 marker 파일 IPC 제거 —
    #   AWK 가 rewrite 발생 시 stderr 에 "REWRITTEN" 신호 emit,
    #   bash 가 2>&1 1>tmp_file 패턴으로 stderr 캡처 → 파일시스템 IPC 불요 (TOCTOU 표면 소거).
    local tmp_file="${workflow_file}.tmp.$$"

    # AWK rewrites ALLOWED_HUB_REPOS line only (idempotent safe).
    # On match: emit "REWRITTEN" to stderr as IPC signal (no /tmp marker file).
    # Redirect: stdout → tmp_file (rewritten content), stderr → awk_stderr variable.
    local awk_stderr
    awk_stderr=$(awk -v merged="$merged_value" '
      /^[[:space:]]*ALLOWED_HUB_REPOS:[[:space:]]*".*"[[:space:]]*$/ {
        match($0, /^[[:space:]]*/);
        indent = substr($0, RSTART, RLENGTH);
        printf "%sALLOWED_HUB_REPOS: \"%s\"\n", indent, merged;
        print "REWRITTEN" > "/dev/stderr";
        next;
      }
      { print; }
    ' "$workflow_file" 2>&1 1>"$tmp_file") || true

    # Check if rewrite actually happened (REWRITTEN signal in captured stderr)
    if [[ "${awk_stderr}" != *"REWRITTEN"* ]]; then
      rm -f "$tmp_file"
      echo "WARN: ALLOWED_HUB_REPOS line found but value not rewritten (quote style mismatch): $workflow_file" >&2
      return 1
    fi

    mv "$tmp_file" "$workflow_file"
    echo "Injected: $workflow_file"
  fi
}

# Main
main() {
  # No-op if project.yaml absent (consumer not using phase_gate.allowed_hub_repos)
  if [[ ! -f "$PROJECT_YAML" ]]; then
    echo "No $PROJECT_YAML — no-op" >&2
    return 0
  fi

  # Compute merged value
  merged=$(merge_allowed_repos "$PROJECT_YAML")
  if [[ -z "$merged" ]]; then
    echo "No phase_gate.allowed_hub_repos entries — no-op" >&2
    return 0
  fi

  # Find all .github/workflows/*.{yml,yaml} with ALLOWED_HUB_REPOS env
  if [[ ! -d "$WORKFLOWS_DIR" ]]; then
    echo "Workflows directory not found: $WORKFLOWS_DIR — no-op" >&2
    return 0
  fi

  found_any=0
  skipped_count=0
  while IFS= read -r workflow_file; do
    if grep -q '^[[:space:]]*ALLOWED_HUB_REPOS:' "$workflow_file"; then
      if ! inject_workflow_env "$workflow_file" "$merged"; then
        skipped_count=$((skipped_count + 1))
        continue
      fi
      found_any=1
    fi
  done < <(find "$WORKFLOWS_DIR" -maxdepth 1 \( -name "*.yml" -o -name "*.yaml" \))

  if [[ $found_any -eq 0 ]]; then
    echo "No workflows with ALLOWED_HUB_REPOS env found — no-op" >&2
  fi

  return 0
}

main
