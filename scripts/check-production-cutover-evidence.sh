#!/usr/bin/env bash
# scripts/check-production-cutover-evidence.sh
#
# CFP-954 / ADR-072 §결정 3 production-cutover-evidence verifier (warning tier).
#
# Mechanical anchor 4-tuple (Change Plan §3.5 + ADR-072 amendment_log Amendment 2):
#   MS-1: live_touching                    — Story frontmatter (yaml.safe_load)
#   MS-2: production_cutover_touching      — dual-source AND (frontmatter + label)
#   MS-3: marketplace_publish_touching     — plugin.json .version diff + marketplace.json channels[] touch
#   MS-4: consumer_impact_blast_radius     — marketplace.json channels[] consumer count proxy
#
# 3-tier exit code (ADR-060 §결정 15):
#   0 = PASS  (exemption pass OR Tier-2 runtime MS-1/MS-2 anchor present + dual-source match;
#             MS-3/MS-4 = Story-4 carrier declare-time scope, runtime full implementation deferred)
#   1 = missing (production_cutover_touching=true but anchor field 부재 — MS-1/MS-2 scope)
#   2 = mechanical anchor invalid (yaml parse fail / dual-source mismatch / cross-repo fetch fail)
#
# Story-3 scope (declare-time vs runtime — measurement_source disjoint):
#   - Runtime verify: MS-1 (live_touching) + MS-2 (production_cutover_touching) — full executable
#   - Declare-time scope: MS-3 (marketplace_publish_touching) + MS-4 (consumer_impact_blast_radius)
#     → Story-4 carrier (promotion criteria 4-tuple executable, real proxy measurement)
#
# Trigger axis (Story-3 D2 consensus): PR-open + workflow_dispatch (cron 24h 미권고).
#
# Wrapper-self-app exemption (Story-3 D3 consensus 2-tier):
#   Tier 1 (declare-time, repo=wrapper) — frontmatter/amendment_log/cross-ref presence verify only
#   Tier 2 (runtime, repo=consumer)     — 실 4-evidence-quad measurement
#
# Test override env:
#   CBL_SKIP_ISSUE_CREATE=1   — Issue auto-create 차단 (sandbox env, ADR-040 Amendment 6 §결정 7.D)
#   CFP954_SKIP_ISSUE_CREATE=1 — legacy fallback (precedent CFP673/CFP932 답습)
#   CFP954_STORY_FILE_PATH=<path>  — bats fixture story file override
#   CFP954_REPO_OVERRIDE=<owner/repo>  — repo context override (default: $GITHUB_REPOSITORY)
#   CFP954_LABEL_LIST=<comma-list>     — PR label set override (default: gh pr view 결과)
#   CFP954_ALWAYS_PASS_DEBUG=1         — discriminating fixture stash 환경 explicit fail-loud

set -euo pipefail

# Resolve SCRIPT_DIR (lib helper source 경로 의존)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Source shared gh API helper (D1 consensus — 3-way WET 해소)
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib/gh-api-helpers.sh"

_GH_HELPER_CALLER="check-production-cutover-evidence"

# --- Skip-Issue helper unified (CBL primary + CFP954 fallback, D2/E3 consensus) ---
_should_skip_issue() {
  if [[ -n "${CBL_SKIP_ISSUE_CREATE:-}" ]] || [[ -n "${CFP954_SKIP_ISSUE_CREATE:-}" ]]; then
    return 0
  fi
  return 1
}

# --- (1) Story file path resolution (D4 MS-1 input) ---
STORY_FILE="${CFP954_STORY_FILE_PATH:-}"
if [[ -z "$STORY_FILE" ]]; then
  # Default: ${REPO_ROOT}/docs/stories/<KEY>.md (consumer path)
  # codeforge family (dogfood-out): wrapper Story → ../codeforge-internal-docs/wrapper/stories/<KEY>.md
  # For runtime production cutover check, consumer self-owned Story file is canonical.
  if [[ -n "${PR_NUMBER:-}" ]]; then
    echo "::warning::${_GH_HELPER_CALLER}: PR_NUMBER=${PR_NUMBER} but CFP954_STORY_FILE_PATH unset — fallback to dogfood path"
  fi
  # Fallback: scan docs/stories/ for first match (best-effort)
  if [[ -d "${REPO_ROOT}/docs/stories" ]]; then
    STORY_FILE="$(find "${REPO_ROOT}/docs/stories" -maxdepth 1 -name "*.md" 2>/dev/null | head -1)"
  fi
fi

# Parser path (D1 / ADR-061 §결정 1 외부 .py 의무)
PARSER="${SCRIPT_DIR}/parse-production-cutover-frontmatter.py"

# --- (2) Repo context (D3 wrapper-self-app exemption Tier-1) ---
REPO="${CFP954_REPO_OVERRIDE:-${GITHUB_REPOSITORY:-}}"
IS_WRAPPER_REPO=0
if [[ "$REPO" == "mclayer/plugin-codeforge" ]]; then
  IS_WRAPPER_REPO=1
fi

# --- (3) MS-2 dual-source AND check (frontmatter + label) ---
FRONTMATTER_TOUCH="null"
LABEL_TOUCH="null"
MISMATCH=0

if [[ -n "$STORY_FILE" ]] && [[ -f "$STORY_FILE" ]]; then
  set +e
  FRONTMATTER_TOUCH="$(python3 "$PARSER" "$STORY_FILE" ".production_cutover_touching" 2>/dev/null)"
  rc=$?
  set -e
  if [[ $rc -eq 2 ]]; then
    echo "[codeforge-kpi-infra-error] ${_GH_HELPER_CALLER}: frontmatter yaml.safe_load failure on $STORY_FILE" >&2
    exit 2
  fi
  if [[ $rc -eq 1 ]]; then
    FRONTMATTER_TOUCH="absent"
  fi
fi

# Label parse (CFP954_LABEL_LIST override OR gh pr view via PR_NUMBER)
LABELS="${CFP954_LABEL_LIST:-}"
if [[ -z "$LABELS" ]] && [[ -n "${PR_NUMBER:-}" ]] && [[ -n "$REPO" ]]; then
  set +e
  LABELS="$(gh pr view "$PR_NUMBER" --repo "$REPO" --json labels --jq '.labels | map(.name) | join(",")' 2>/dev/null || echo "")"
  set -e
fi

if [[ "$LABELS" == *"production-touching"* ]]; then
  LABEL_TOUCH="true"
else
  LABEL_TOUCH="false"
fi

# --- (4) Dual-source AND semantic + mismatch detection (D4 MS-2 + OpRiskArch §C.2) ---
# fail-loud over fail-silent — mismatch = Issue auto-create + workflow run as TRUE
PROD_CUTOVER_TOUCHING="false"
if [[ "$FRONTMATTER_TOUCH" == "true" ]] && [[ "$LABEL_TOUCH" == "true" ]]; then
  PROD_CUTOVER_TOUCHING="true"
elif [[ "$FRONTMATTER_TOUCH" == "false" ]] && [[ "$LABEL_TOUCH" == "false" ]]; then
  PROD_CUTOVER_TOUCHING="false"
elif [[ "$FRONTMATTER_TOUCH" == "absent" ]] && [[ "$LABEL_TOUCH" == "false" ]]; then
  PROD_CUTOVER_TOUCHING="false"
elif [[ "$FRONTMATTER_TOUCH" == "null" ]] && [[ "$LABEL_TOUCH" == "false" ]]; then
  # Story file absent + label absent = production_cutover_touching not declared (skip scope)
  PROD_CUTOVER_TOUCHING="false"
else
  # Mismatch: 1 source true + 1 source false/absent
  MISMATCH=1
  PROD_CUTOVER_TOUCHING="true"  # fail-loud: workflow run as TRUE, Issue create
  echo "::warning::${_GH_HELPER_CALLER}: dual-source mismatch detected — frontmatter=${FRONTMATTER_TOUCH} label=${LABEL_TOUCH}" >&2
fi

# --- (5) Early exit: production_cutover_touching=false → workflow PASS (skip 영역) ---
if [[ "$PROD_CUTOVER_TOUCHING" == "false" ]]; then
  echo "${_GH_HELPER_CALLER}: PASS — production_cutover_touching=false (skip scope, additive-only invariant)"
  exit 0
fi

# --- (6) Tier-1 wrapper-self-app exemption (D3 consensus) ---
# Story-3 자체 PR 영역: repo=wrapper + production_cutover_touching=true → declare-time scope check
# code_change definition (OpRiskArch §C.1 redefinition):
#   runtime behavior change = src/** + scripts/**/*.{sh,py} + templates/github-workflows/*.yml
#   exempt = docs/** + CLAUDE.md + scripts/**/*.{yaml,yml} (data file) + tests/**
# Story-3 자체 = scripts/check-production-cutover-evidence.sh 신설 → runtime behavior change > 0 → Tier-1 exemption (declare-time presence verify only)
if [[ $IS_WRAPPER_REPO -eq 1 ]]; then
  # Tier-1 declare-time scope check: ADR-072 frontmatter + amendment_log + cross-ref presence
  ADR_72_PATH="${REPO_ROOT}/archive/adr/ADR-072-production-evidence-deputy-and-epic-cutover-gate.md"
  EVIDENCE_REGISTRY_PATH="${REPO_ROOT}/docs/evidence-checks-registry.yaml"
  LABEL_REGISTRY_PATH="${REPO_ROOT}/docs/inter-plugin-contracts/label-registry-v2.md"

  declare_failures=0
  if [[ ! -f "$ADR_72_PATH" ]]; then
    echo "::warning::${_GH_HELPER_CALLER}: Tier-1 declare-time — ADR-072 file absent" >&2
    declare_failures=$((declare_failures + 1))
  fi
  if [[ ! -f "$EVIDENCE_REGISTRY_PATH" ]]; then
    echo "::warning::${_GH_HELPER_CALLER}: Tier-1 declare-time — evidence-checks-registry.yaml absent" >&2
    declare_failures=$((declare_failures + 1))
  fi
  if [[ ! -f "$LABEL_REGISTRY_PATH" ]]; then
    echo "::warning::${_GH_HELPER_CALLER}: Tier-1 declare-time — label-registry-v2.md absent" >&2
    declare_failures=$((declare_failures + 1))
  fi

  if [[ $declare_failures -gt 0 ]]; then
    echo "${_GH_HELPER_CALLER}: FAIL (declare-time) — ${declare_failures} mandatory wrapper SSOT file 부재"
    exit 1
  fi
  echo "${_GH_HELPER_CALLER}: PASS — wrapper Tier-1 declare-time exemption (Story-3 self-applicable, ADR-072 §결정 6 정합)"
  if [[ $MISMATCH -eq 1 ]] && ! _should_skip_issue; then
    gh issue create \
      --repo mclayer/plugin-codeforge \
      --label "drift-detection" \
      --title "[PROD-CUTOVER] dual-source mismatch (declare-time)" \
      --body "check-production-cutover-evidence: dual-source AND mismatch — frontmatter=${FRONTMATTER_TOUCH} label=${LABEL_TOUCH} (story=${STORY_FILE}, repo=${REPO})

signature: dual-source-mismatch|${REPO}|${FRONTMATTER_TOUCH}|${LABEL_TOUCH}

[codeforge-kpi-infra-error] CFP-954 / ADR-072 §결정 3" \
      2>/dev/null || true
  fi
  exit 0
fi

# --- (7) Tier-2 runtime exemption (consumer Story 영역) — 4-tuple anchor verify ---
# MS-1: live_touching (Story frontmatter)
LIVE_TOUCHING="absent"
if [[ -n "$STORY_FILE" ]] && [[ -f "$STORY_FILE" ]]; then
  set +e
  LIVE_TOUCHING="$(python3 "$PARSER" "$STORY_FILE" ".live_touching" 2>/dev/null)"
  rc=$?
  set -e
  if [[ $rc -eq 2 ]]; then
    echo "[codeforge-kpi-infra-error] ${_GH_HELPER_CALLER}: frontmatter yaml.safe_load failure on $STORY_FILE (MS-1)" >&2
    exit 2
  fi
  if [[ $rc -eq 1 ]]; then
    LIVE_TOUCHING="absent"
  fi
fi

# MS-3: marketplace_publish_touching (plugin.json + marketplace.json diff)
# Story-3 = Story-4 carrier (promotion criteria 4-tuple executable, declare-time scope only).
# Declare-time scope: MS-1/MS-2 만 runtime verify — MS-3 = absent (hardcoded sentinel).
# Runtime full implementation (plugin.json .version diff + marketplace.json channels[] touch)
# = Story-4 carrier (별 PR, promotion criteria 4-tuple executable measurement).
MARKETPLACE_PUBLISH="absent"

# MS-4: consumer_impact_blast_radius (marketplace.json channels[] consumer count proxy)
# Story-3 = Story-4 carrier (promotion criteria 4-tuple executable, declare-time scope only).
# Declare-time scope: MS-1/MS-2 만 runtime verify — MS-4 = best_effort_pending (hardcoded sentinel).
# Runtime full proxy measurement (marketplace.json channels[] consumer count aggregate)
# = Story-4 / Story-5 carrier (별 PR, real proxy measurement).
CONSUMER_BLAST="best_effort_pending"

# --- (8) Runtime declare-time presence verify (Tier-2 minimal scope) ---
runtime_failures=0
if [[ "$LIVE_TOUCHING" == "absent" ]]; then
  echo "::warning::${_GH_HELPER_CALLER}: MS-1 live_touching absent in $STORY_FILE" >&2
  runtime_failures=$((runtime_failures + 1))
fi
if [[ "$FRONTMATTER_TOUCH" == "absent" ]]; then
  echo "::warning::${_GH_HELPER_CALLER}: MS-2 production_cutover_touching absent in $STORY_FILE" >&2
  runtime_failures=$((runtime_failures + 1))
fi

# Issue auto-create dedup signature
if [[ $runtime_failures -gt 0 ]]; then
  if ! _should_skip_issue; then
    SIG="missing-anchor|${REPO}|${STORY_FILE##*/}|runtime"
    gh issue create \
      --repo mclayer/plugin-codeforge \
      --label "drift-detection" \
      --title "[PROD-CUTOVER] missing anchor (runtime, repo=${REPO})" \
      --body "check-production-cutover-evidence: ${runtime_failures} mandatory mechanical anchor missing (live_touching / production_cutover_touching / marketplace_publish_touching / consumer_impact_blast_radius).

story_file: ${STORY_FILE}
repo: ${REPO}

signature: ${SIG}

[codeforge-kpi-infra-error] CFP-954 / ADR-072 §결정 3" \
      2>/dev/null || true
  fi
  echo "${_GH_HELPER_CALLER}: FAIL (runtime) — ${runtime_failures} mandatory anchor missing"
  exit 1
fi

if [[ $MISMATCH -eq 1 ]] && ! _should_skip_issue; then
  gh issue create \
    --repo mclayer/plugin-codeforge \
    --label "drift-detection" \
    --title "[PROD-CUTOVER] dual-source mismatch (runtime)" \
    --body "check-production-cutover-evidence: dual-source AND mismatch — frontmatter=${FRONTMATTER_TOUCH} label=${LABEL_TOUCH} (story=${STORY_FILE}, repo=${REPO})

signature: dual-source-mismatch|${REPO}|${FRONTMATTER_TOUCH}|${LABEL_TOUCH}

[codeforge-kpi-infra-error] CFP-954 / ADR-072 §결정 3" \
    2>/dev/null || true
fi

echo "${_GH_HELPER_CALLER}: PASS — Tier-2 runtime scope (4-tuple anchor present, MS-3/MS-4 best-effort declare)"
exit 0
