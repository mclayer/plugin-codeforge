#!/usr/bin/env bash
# check-no-duplicate-session-start-hook.sh — one-channel rule lint (ADR-038 Amendment 3 §결정 12)
# CFP-475 / ADR-038 Amendment 3 §결정 12 (one-channel rule mechanical lint enforcement)
#
# Detect: .claude/settings.json + plugin-root hooks/hooks.json 양 channel 안
#         prereq-check entry 동시 존재 → exit 2 (warning tier)
#
# Exit code 3-tier (ADR-060 §결정 15 정합):
#   0 = PASS (중복 없음)
#   1 = error (reserved — 본 script 미발화, jq 미설치 또는 unexpected 제외)
#   2 = warning (double-registration detected)
#
# Bypass channel (ADR-060 §결정 7 audit-trailed exception 패턴 정합):
#   PR 에 hotfix-bypass:duplicate-session-start-hook label 부착 시
#   templates/github-workflows/duplicate-session-start-hook-check.yml 가 lint skip

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
SETTINGS="${REPO_ROOT}/.claude/settings.json"
PLUGIN_HOOKS="${REPO_ROOT}/hooks/hooks.json"

# prereq-check 만 detect (drift / worktree-gc 와 disjoint substring)
PREREQ_PATTERN='check-codeforge-prereq\.sh|hooks/session-start[" ]'

settings_has_prereq=false
plugin_has_prereq=false

# jq 가용성 확인 — 미설치 시 grep fallback
if command -v jq >/dev/null 2>&1; then
  # jq path: structured JSON parse
  if [[ -f "$SETTINGS" ]]; then
    if jq -e --arg pat "$PREREQ_PATTERN" '
      (.hooks.SessionStart // [])
      | map(.hooks // []) | flatten
      | any(.command // "" | test($pat))
    ' "$SETTINGS" >/dev/null 2>&1; then
      settings_has_prereq=true
    fi
  fi

  if [[ -f "$PLUGIN_HOOKS" ]]; then
    if jq -e --arg pat "$PREREQ_PATTERN" '
      (.hooks.SessionStart // [])
      | map(.hooks // []) | flatten
      | any(.command // "" | test($pat))
    ' "$PLUGIN_HOOKS" >/dev/null 2>&1; then
      plugin_has_prereq=true
    fi
  fi
else
  # grep fallback (jq 미설치 환경)
  >&2 echo "[duplicate-session-start-hook-check] INFO: jq not found, falling back to grep"
  if [[ -f "$SETTINGS" ]]; then
    if grep -E "$PREREQ_PATTERN" "$SETTINGS" >/dev/null 2>&1; then
      settings_has_prereq=true
    fi
  fi

  if [[ -f "$PLUGIN_HOOKS" ]]; then
    if grep -E "$PREREQ_PATTERN" "$PLUGIN_HOOKS" >/dev/null 2>&1; then
      plugin_has_prereq=true
    fi
  fi
fi

if $settings_has_prereq && $plugin_has_prereq; then
  >&2 echo "[duplicate-session-start-hook-check] WARNING: prereq-check entry detected in BOTH .claude/settings.json AND hooks/hooks.json."
  >&2 echo "  Reproduce: grep -E '${PREREQ_PATTERN}' .claude/settings.json hooks/hooks.json"
  >&2 echo "  Fix: remove the entry from .claude/settings.json (plugin-root hooks/hooks.json is SSOT per ADR-038 Amendment 3 §결정 10)."
  exit 2  # warning tier — ADR-060 §결정 15 exit-code 3-tier
fi

echo "[duplicate-session-start-hook-check] PASS — no duplicate prereq-check entry detected."
exit 0
