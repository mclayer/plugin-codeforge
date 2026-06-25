#!/usr/bin/env bash
# check-codeforge-version-drift.sh — codeforge plugin family version drift check (CFP-262 / ADR-037)
#
# 세션 개시 의무 sub-step. installed plugin manifest version 과 marketplace.json latest 비교.
# Drift severity 분류 (ADR-037):
#   MAJOR drift → exit 1 (hard-stop blocking, /plugins update 의무)
#   MINOR drift → stderr warning, exit 0 (auto-proceed)
#   PATCH drift → stdout notice, exit 0 (info)
#
# Bypass: BYPASS_VERSION_DRIFT=1 + BYPASS_VERSION_DRIFT_REASON env
#
# Dependencies: gh CLI (auth), jq, semver via awk
# Cross-platform: Windows Git Bash / macOS / Linux
#
# Usage:
#   bash scripts/check-codeforge-version-drift.sh           # 9 plugin 모두 검사
#   bash scripts/check-codeforge-version-drift.sh --plugin codeforge  # 특정 plugin 만
#   bash scripts/check-codeforge-version-drift.sh --json    # machine-readable JSON
#
# Exit codes: 0 (no drift / MINOR / PATCH only) / 1 (MAJOR drift detected) / 2 (prerequisite missing)

set -u

# Bypass check (audit trail 의무)
if [[ "${BYPASS_VERSION_DRIFT:-0}" == "1" ]]; then
  if [[ -z "${BYPASS_VERSION_DRIFT_REASON:-}" ]]; then
    echo "ERROR: BYPASS_VERSION_DRIFT=1 requires BYPASS_VERSION_DRIFT_REASON (audit trail)" >&2
    exit 2
  fi
  echo "::warning:: drift check BYPASSED — reason: $BYPASS_VERSION_DRIFT_REASON" >&2
  exit 0
fi

# Prerequisite check
for cmd in gh jq awk; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "ERROR: $cmd 미설치" >&2; exit 2; }
done

if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: gh CLI 미인증. 'gh auth login' 실행 후 재시도." >&2
  exit 2
fi

# Plugin → marketplace 매핑 (11 entry — codeforge 9 plugin + codex + superpowers)
# CFP-1219: codeforge-deploy + codeforge-deploy-review 추가 (ADR-087/088, CFP-1059 S2/S3 resolved)
declare -A PLUGIN_MARKETPLACE=(
  [codeforge]="mclayer/marketplace"
  [codeforge-requirements]="mclayer/marketplace"
  [codeforge-design]="mclayer/marketplace"
  [codeforge-review]="mclayer/marketplace"
  [codeforge-develop]="mclayer/marketplace"
  [codeforge-test]="mclayer/marketplace"
  [codeforge-pmo]="mclayer/marketplace"
  [codeforge-deploy]="mclayer/marketplace"          # ADR-087 Deploy lane (CFP-1219 활성)
  [codeforge-deploy-review]="mclayer/marketplace"   # ADR-088 Deploy Review lane (CFP-1219 활성)
  [codex]="openai-codex/marketplace"
  [superpowers]="claude-plugins-official/marketplace"
)

# Single plugin filter (--plugin <name>)
FILTER=""
JSON_MODE=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --plugin) FILTER="$2"; shift 2 ;;
    --json) JSON_MODE=1; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

# Plugin install directory (Claude Code convention)
PLUGINS_DIR="${HOME}/.claude/plugins/cache"
[[ ! -d "$PLUGINS_DIR" ]] && { echo "ERROR: plugin cache 부재 ($PLUGINS_DIR)" >&2; exit 2; }

# semver compare via awk — returns 0 (eq) / 1 (lt) / 2 (gt) / 3 (downgrade impossible — version invalid)
semver_cmp() {
  awk -v a="$1" -v b="$2" 'BEGIN {
    split(a, A, "."); split(b, B, ".")
    for (i = 1; i <= 3; i++) {
      if (A[i] + 0 < B[i] + 0) { print 1; exit }
      if (A[i] + 0 > B[i] + 0) { print 2; exit }
    }
    print 0
  }'
}

# Drift classify per ADR-037 — major / minor / patch / none
drift_classify() {
  local installed="$1" latest="$2"
  awk -v inst="$installed" -v lat="$latest" 'BEGIN {
    split(inst, I, "."); split(lat, L, ".")
    if (L[1] + 0 > I[1] + 0) { print "major"; exit }
    if (L[2] + 0 > I[2] + 0) { print "minor"; exit }
    if (L[3] + 0 > I[3] + 0) { print "patch"; exit }
    print "none"
  }'
}

# Find latest installed version of a plugin (highest version dir)
installed_version() {
  local plugin="$1" mp="$2"
  local plugin_dir="${PLUGINS_DIR}/${mp%/marketplace}/${plugin}"
  [[ ! -d "$plugin_dir" ]] && { echo ""; return; }

  # 가장 최근 version dir 찾기 (대안: jq plugin.json — version 다중 install 케이스)
  local latest_v=""
  while IFS= read -r v_dir; do
    [[ -f "$v_dir/.claude-plugin/plugin.json" ]] || continue
    local v
    v=$(jq -r '.version' "$v_dir/.claude-plugin/plugin.json" 2>/dev/null)
    [[ -z "$v" || "$v" == "null" ]] && continue
    if [[ -z "$latest_v" || "$(semver_cmp "$v" "$latest_v")" == "2" ]]; then
      latest_v="$v"
    fi
  done < <(find "$plugin_dir" -maxdepth 1 -mindepth 1 -type d 2>/dev/null)

  echo "$latest_v"
}

# Fetch marketplace latest version
marketplace_version() {
  local plugin="$1" mp="$2"
  gh api "repos/${mp}/contents/.claude-plugin/marketplace.json" --jq '.content' 2>/dev/null \
    | base64 --decode 2>/dev/null \
    | jq -r --arg name "$plugin" '.plugins[] | select(.name==$name) | .version' 2>/dev/null
}

# Run check
[[ $JSON_MODE -eq 1 ]] && echo -n "{\"results\":["
exit_code=0
results=()
i=0

for plugin in "${!PLUGIN_MARKETPLACE[@]}"; do
  if [[ -n "$FILTER" && "$plugin" != "$FILTER" ]]; then continue; fi
  mp="${PLUGIN_MARKETPLACE[$plugin]}"

  installed=$(installed_version "$plugin" "$mp")
  latest=$(marketplace_version "$plugin" "$mp")

  if [[ -z "$installed" ]]; then
    msg="plugin '$plugin' 미설치 (install: /plugins install ${plugin}@${mp%/marketplace})"
    [[ $JSON_MODE -eq 1 ]] || echo "::warning::$msg" >&2
    results+=("{\"plugin\":\"$plugin\",\"status\":\"not-installed\",\"message\":\"$msg\"}")
    continue
  fi

  if [[ -z "$latest" || "$latest" == "null" ]]; then
    msg="plugin '$plugin' marketplace fetch 실패 ($mp)"
    [[ $JSON_MODE -eq 1 ]] || echo "::warning::$msg" >&2
    results+=("{\"plugin\":\"$plugin\",\"status\":\"fetch-failed\",\"installed\":\"$installed\",\"message\":\"$msg\"}")
    continue
  fi

  drift=$(drift_classify "$installed" "$latest")

  case "$drift" in
    major)
      msg="$plugin: stale MAJOR ($installed → $latest). /plugins update $plugin REQUIRED."
      [[ $JSON_MODE -eq 1 ]] || echo "::error::$msg" >&2
      exit_code=1
      ;;
    minor)
      msg="$plugin: stale MINOR ($installed → $latest). Recommend /plugins update $plugin."
      [[ $JSON_MODE -eq 1 ]] || echo "::warning::$msg" >&2
      ;;
    patch)
      msg="$plugin: stale PATCH ($installed → $latest)."
      [[ $JSON_MODE -eq 1 ]] || echo "::notice::$msg"
      ;;
    none)
      msg="$plugin: up-to-date ($installed)."
      [[ $JSON_MODE -eq 1 ]] || echo "$msg"
      ;;
  esac

  results+=("{\"plugin\":\"$plugin\",\"status\":\"$drift\",\"installed\":\"$installed\",\"latest\":\"$latest\"}")
done

if [[ $JSON_MODE -eq 1 ]]; then
  IFS=','; echo "${results[*]}],\"exit_code\":$exit_code}"
else
  echo ""
  if [[ $exit_code -eq 1 ]]; then
    echo "FAIL: MAJOR drift detected — codeforge 작업 진입 차단. /plugins update 후 세션 재시작." >&2
  fi
fi

exit $exit_code
