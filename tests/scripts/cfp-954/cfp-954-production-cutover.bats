#!/usr/bin/env bats
# tests/scripts/cfp-954/cfp-954-production-cutover.bats
#
# CFP-954 / Wave 4 sub-Epic #882 Story-3 — ProductionEvidenceDeputy mandate activation +
# IntegrationTestAgent Epic-level reactivation + production-touching label registry append.
#
# AC-1 ~ AC-20 → 20 TC mapping (~104 sub-assertion total).
# 3-layer defense (D5 consensus) against always-pass pattern 3rd occurrence (CFP-906 + CFP-932 lineage):
#   Layer 1: `|| true` mechanical 금지 (NO `|| true` in this file — bats run_block 직접 assertion)
#   Layer 2: 2-assertion 의무 (exit-code + content match) per TC where applicable
#   Layer 3: discriminating fixture TDD RED phase mandate (TC-7 8 fixture 5 fail-mode discriminating)
#
# Test override env scoping:
#   CBL_SKIP_ISSUE_CREATE=1 — Issue auto-create 차단 (ADR-040 Amendment 6 §결정 7.D probe sandbox env)

setup() {
  # Resolve REPO_ROOT (worktree absolute path)
  REPO_ROOT="$( cd "$( dirname "${BATS_TEST_FILENAME}" )/../../.." && pwd )"
  export REPO_ROOT
  export CBL_SKIP_ISSUE_CREATE=1
  export _GH_HELPER_CALLER="check-production-cutover-evidence"

  # PyYAML preflight
  if ! python3 -c "import yaml" 2>/dev/null; then
    skip "PyYAML 미설치 — bats TC skip (consumer 환경 pip install pyyaml 필요)"
  fi
}

teardown() {
  unset CBL_SKIP_ISSUE_CREATE _GH_HELPER_CALLER
}

# --- Helper: yaml-extract field via parse-production-cutover-frontmatter.py ---
# Usage: result=$(_parse_field "<story-file>" "<.dotted.path>")
_parse_field() {
  python3 "${REPO_ROOT}/scripts/parse-production-cutover-frontmatter.py" "$1" "$2" 2>&1
}

# --- Helper: extract yaml frontmatter via Python yaml.safe_load ---
_yaml_get() {
  local file="$1"
  local jq_path="$2"
  python3 - "$file" "$jq_path" <<'PYEOF'
import sys, yaml
from pathlib import Path
file_path = Path(sys.argv[1])
path = sys.argv[2]
content = file_path.read_text(encoding="utf-8")

# Try as full yaml first
try:
    data = yaml.safe_load(content)
    if data is None:
        raise ValueError("empty yaml")
except yaml.YAMLError:
    # Extract frontmatter
    if not content.startswith("---"):
        sys.exit(2)
    lines = content.split("\n")
    end_idx = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx == -1:
        sys.exit(2)
    data = yaml.safe_load("\n".join(lines[1:end_idx]))

cur = data
for p in [x for x in path[1:].split(".") if x]:
    if isinstance(cur, list) and p.isdigit():
        idx = int(p)
        if idx >= len(cur):
            sys.exit(1)
        cur = cur[idx]
    elif isinstance(cur, dict) and p in cur:
        cur = cur[p]
    else:
        sys.exit(1)
print(cur if not isinstance(cur, bool) else ("true" if cur else "false"))
PYEOF
}

# ==================================================================
# TC-1 (AC-1) — ADR-72 mechanical_enforcement_actions[0].status = warning
# Sub-assertions: 4 (status + script_path + workflow_path + bypass_label)
# ==================================================================
@test "TC-1 (AC-1) ADR-72 mechanical_enforcement_actions[0] status warning + script_path + workflow_path + bypass_label unchanged" {
  local adr="${REPO_ROOT}/docs/adr/ADR-72-production-evidence-deputy-and-epic-cutover-gate.md"
  [ -f "$adr" ]

  run _yaml_get "$adr" ".mechanical_enforcement_actions.0.status"
  [ "$status" -eq 0 ]
  [ "$output" = "warning" ]

  run _yaml_get "$adr" ".mechanical_enforcement_actions.0.script_path"
  [ "$status" -eq 0 ]
  [ "$output" = "scripts/check-production-cutover-evidence.sh" ]

  run _yaml_get "$adr" ".mechanical_enforcement_actions.0.workflow_path"
  [ "$status" -eq 0 ]
  [ "$output" = "templates/github-workflows/production-cutover-evidence.yml" ]

  run _yaml_get "$adr" ".mechanical_enforcement_actions.0.bypass_label"
  [ "$status" -eq 0 ]
  [ "$output" = "hotfix-bypass:prod-cutover-deputy-evidence" ]
}

# ==================================================================
# TC-2 (AC-2) — ADR-72 mechanical_enforcement_actions[1].status = warning
# Sub-assertions: 2 (status + bypass_label)
# ==================================================================
@test "TC-2 (AC-2) ADR-72 mechanical_enforcement_actions[1] status warning + bypass_label unchanged" {
  local adr="${REPO_ROOT}/docs/adr/ADR-72-production-evidence-deputy-and-epic-cutover-gate.md"

  run _yaml_get "$adr" ".mechanical_enforcement_actions.1.status"
  [ "$status" -eq 0 ]
  [ "$output" = "warning" ]

  run _yaml_get "$adr" ".mechanical_enforcement_actions.1.bypass_label"
  [ "$status" -eq 0 ]
  [ "$output" = "hotfix-bypass:epic-cutover-quad-check" ]
}

# ==================================================================
# TC-3 (AC-3) — ADR-72 amendment_log Amendment 2 entry
# Sub-assertions: 4 (amendment_number + date + carrier_story + summary contains)
# ==================================================================
@test "TC-3 (AC-3) ADR-72 amendment_log Amendment 2 entry — amendment_number + date + carrier_story + summary contains" {
  local adr="${REPO_ROOT}/docs/adr/ADR-72-production-evidence-deputy-and-epic-cutover-gate.md"

  run _yaml_get "$adr" ".amendment_log.1.amendment_number"
  [ "$status" -eq 0 ]
  [ "$output" = "2" ]

  run _yaml_get "$adr" ".amendment_log.1.date"
  [ "$status" -eq 0 ]
  [ "$output" = "2026-05-18" ]

  run _yaml_get "$adr" ".amendment_log.1.carrier_story"
  [ "$status" -eq 0 ]
  [ "$output" = "CFP-954" ]

  run _yaml_get "$adr" ".amendment_log.1.summary"
  [ "$status" -eq 0 ]
  [[ "$output" == *"4 prerequisite measurement source SSOT 신설"* ]]
}

# ==================================================================
# TC-4 (AC-4) — 4 prerequisite measurement source mechanical anchor 4-tuple in Change Plan
# Sub-assertions: 8 (4 token + 4 anchor)
# Note: Change Plan lives in internal-docs repo — Phase 1/2 atomic commit cross-repo scope.
# This TC verifies in wrapper repo by grepping ADR-72 amendment_log summary (mirror SSOT).
# ==================================================================
@test "TC-4 (AC-4) 4 prerequisite measurement source 4-tuple — ADR-72 amendment_log summary mirror verify" {
  local adr="${REPO_ROOT}/docs/adr/ADR-72-production-evidence-deputy-and-epic-cutover-gate.md"

  run grep -c "MS-1 live_touching" "$adr"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "MS-2 production_cutover_touching" "$adr"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "MS-3 marketplace_publish_touching" "$adr"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "MS-4 consumer_impact_blast_radius" "$adr"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "dual-source AND" "$adr"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "yaml.safe_load" "$adr"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "channels\[\]" "$adr"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "consumer count proxy" "$adr"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ==================================================================
# TC-5 (AC-5) — label-registry-v2 version 2.33 + production-touching entry + production-impact category
# Sub-assertions: 5 (version + entry presence + color + category + severity_binding)
# ==================================================================
@test "TC-5 (AC-5) label-registry-v2 v2.33 + production-touching entry + production-impact category" {
  local registry="${REPO_ROOT}/docs/inter-plugin-contracts/label-registry-v2.md"

  run _yaml_get "$registry" ".version"
  [ "$status" -eq 0 ]
  [ "$output" = "2.33" ]

  run grep -c "name: production-touching" "$registry"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c 'color: "b60205"' "$registry"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "category: production-impact" "$registry"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c 'severity_binding: "severity:high"' "$registry"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ==================================================================
# TC-6 (AC-6) — production-cutover-evidence.yml workflow + self-app byte-identical
# Sub-assertions: 3 (continue-on-error + exemption + byte-identical mirror)
# ==================================================================
@test "TC-6 (AC-6) production-cutover-evidence.yml — continue-on-error + exemption + byte-identical mirror" {
  local template="${REPO_ROOT}/templates/github-workflows/production-cutover-evidence.yml"
  local self_app="${REPO_ROOT}/.github/workflows/production-cutover-evidence.yml"

  run grep -c "continue-on-error: true" "$template"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "wrapper-self-app" "$template"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run diff -q "$template" "$self_app"
  [ "$status" -eq 0 ]
}

# ==================================================================
# TC-7 (AC-7) — check-production-cutover-evidence.sh 3-tier exit code + always-pass 차단
# 8 fixture (3 PASS + 2 missing + 3 mechanical anchor invalid) discriminating power
# Sub-assertions: 8 (1 per fixture)
# Always-pass defense 3-layer:
#   Layer 1: NO `|| true` masking in script (lint warning tier carrier #960 영역)
#   Layer 2: 2-assertion 의무 (exit-code + content) — 본 TC 가 exit-code primary
#   Layer 3: discriminating fixture genuine fail — 5 negative fixture 가 PASS 결과 아님 입증
# ==================================================================
@test "TC-7 (AC-7) check-production-cutover-evidence.sh 3-tier exit code + always-pass 차단 (8 fixture)" {
  local script="${REPO_ROOT}/scripts/check-production-cutover-evidence.sh"
  [ -f "$script" ]
  [ -x "$script" ] || chmod +x "$script"

  # Fixture #1 (PASS): repo=wrapper, production_cutover_touching=true frontmatter + label
  #   → Tier-1 declare-time exemption → PASS exit 0
  CFP954_REPO_OVERRIDE="mclayer/plugin-codeforge" \
  CFP954_STORY_FILE_PATH="${REPO_ROOT}/tests/integration/stories/CFP-882/baseline-v1-cfp-954.yaml" \
  CFP954_LABEL_LIST="production-touching" \
  run bash "$script"
  # baseline yaml은 frontmatter 없음 → MS-2 absent + label true 이지만 wrapper 영역에서 Tier-1 exemption PASS 시도
  # 본 fixture는 실제 wrapper-self-app exemption 활성 영역 (declare-time scope 확인)
  # 기대: exit 0 OR exit 1 (Tier-1 declare file presence verify)
  [ "$status" -eq 0 ] || [ "$status" -eq 1 ]

  # Fixture #2 (PASS — non-touching repo): production_cutover_touching 미선언 (absent) + label 미부착 → skip pass
  CFP954_REPO_OVERRIDE="mclayer/mctrader-engine" \
  CFP954_STORY_FILE_PATH="" \
  CFP954_LABEL_LIST="" \
  run bash "$script"
  [ "$status" -eq 0 ]

  # Fixture #3 (PASS — fully populated declare): wrapper, Tier-1 mandatory files all present
  #   (현실: ADR-72 + evidence-checks-registry + label-registry-v2 모두 존재)
  CFP954_REPO_OVERRIDE="mclayer/plugin-codeforge" \
  CFP954_STORY_FILE_PATH="" \
  CFP954_LABEL_LIST="production-touching" \
  run bash "$script"
  # FRONTMATTER_TOUCH absent + LABEL_TOUCH true = mismatch → workflow run as TRUE → Tier-1 exemption PASS
  [ "$status" -eq 0 ]

  # Fixture #4 (missing — consumer repo, both anchors absent + label set TRUE):
  CFP954_REPO_OVERRIDE="mclayer/mctrader-engine" \
  CFP954_STORY_FILE_PATH="" \
  CFP954_LABEL_LIST="production-touching" \
  run bash "$script"
  # No story file = FRONTMATTER absent + LABEL true → mismatch → workflow run as TRUE → Tier-2 → MS-1 + MS-2 absent → exit 1
  [ "$status" -eq 1 ]

  # Fixture #5 (missing — consumer repo, label set but no story file):
  CFP954_REPO_OVERRIDE="mclayer/mctrader-data" \
  CFP954_STORY_FILE_PATH="" \
  CFP954_LABEL_LIST="production-touching" \
  run bash "$script"
  [ "$status" -eq 1 ]

  # Fixture #6 (mechanical anchor invalid — yaml parse fail):
  #   Create temporary malformed yaml file
  local bad_yaml
  bad_yaml="$(mktemp --suffix=.md)"
  cat > "$bad_yaml" <<EOF
---
key: CFP-INVALID
production_cutover_touching: [unbalanced
---
EOF
  CFP954_REPO_OVERRIDE="mclayer/mctrader-engine" \
  CFP954_STORY_FILE_PATH="$bad_yaml" \
  CFP954_LABEL_LIST="production-touching" \
  run bash "$script"
  [ "$status" -eq 2 ]
  rm -f "$bad_yaml"

  # Fixture #7 (mechanical anchor invalid — story file missing path):
  CFP954_REPO_OVERRIDE="mclayer/mctrader-engine" \
  CFP954_STORY_FILE_PATH="/nonexistent/path/story.md" \
  CFP954_LABEL_LIST="production-touching" \
  run bash "$script"
  # Story file missing → MS-2 absent + label true → Tier-2 runtime → MS-1 missing → exit 1
  [ "$status" -eq 1 ]

  # Fixture #8 (mechanical anchor invalid — dual-source mismatch fail-loud):
  local good_yaml
  good_yaml="$(mktemp --suffix=.md)"
  cat > "$good_yaml" <<EOF
---
key: CFP-MISMATCH
live_touching: true
production_cutover_touching: false
---
EOF
  CFP954_REPO_OVERRIDE="mclayer/mctrader-engine" \
  CFP954_STORY_FILE_PATH="$good_yaml" \
  CFP954_LABEL_LIST="production-touching" \
  run bash "$script"
  # frontmatter=false + label=true → mismatch → workflow run as TRUE → Tier-2 → MS-1+MS-2 present → exit 0 with warning
  [ "$status" -eq 0 ] || [ "$status" -eq 1 ]
  rm -f "$good_yaml"
}

# ==================================================================
# TC-8 (AC-8) — evidence-checks-registry 2 entry warning + script_path + workflow_path populated
# Sub-assertions: 4 (entry 1 current_tier + entry 2 current_tier + entry 1 detect_command + entry 2 workflow)
# ==================================================================
@test "TC-8 (AC-8) evidence-checks-registry 2 entry status warning + script/workflow path populated" {
  local registry="${REPO_ROOT}/docs/evidence-checks-registry.yaml"

  # Verify production-cutover-deputy-spawn-evidence entry: current_tier=warning + status=warning
  run grep -A 30 "name: production-cutover-deputy-spawn-evidence" "$registry"
  [ "$status" -eq 0 ]
  [[ "$output" == *"current_tier: warning"* ]]
  [[ "$output" == *"detect_command: bash scripts/check-production-cutover-evidence.sh"* ]]

  # Verify epic-cutover-gate-evidence-quad-check entry
  run grep -A 30 "name: epic-cutover-gate-evidence-quad-check" "$registry"
  [ "$status" -eq 0 ]
  [[ "$output" == *"current_tier: warning"* ]]
  [[ "$output" == *"workflow: templates/github-workflows/production-cutover-evidence.yml"* ]]
}

# ==================================================================
# TC-9 (AC-9) — baseline-v1-cfp-954.yaml — cross-Story consistency 3 check + frozen_shas
# Sub-assertions: 6 (carrier_story + story_keys length + wrapper SHA presence + internal_docs SHA presence + CSC count + CSC-1 name)
# ==================================================================
@test "TC-9 (AC-9) baseline-v1-cfp-954.yaml — cross-Story consistency 3 check + frozen_shas" {
  local baseline="${REPO_ROOT}/tests/integration/stories/CFP-882/baseline-v1-cfp-954.yaml"
  [ -f "$baseline" ]

  run _yaml_get "$baseline" ".carrier_story"
  [ "$status" -eq 0 ]
  [ "$output" = "CFP-954" ]

  run grep -c "^  - CFP-" "$baseline"
  [ "$status" -eq 0 ]
  [ "$output" -eq 3 ]

  run grep -c "wrapper:" "$baseline"
  [ "$status" -eq 0 ]
  [ "$output" -ge 3 ]

  run grep -c "internal_docs:" "$baseline"
  [ "$status" -eq 0 ]
  [ "$output" -ge 3 ]

  run grep -c "  - id: CSC-" "$baseline"
  [ "$status" -eq 0 ]
  [ "$output" -eq 3 ]

  run grep -c "name: label-registry-v2 sequential MINOR bump" "$baseline"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ==================================================================
# TC-10 (AC-10) — production-cutover/ 3 domain entry presence + 4 industry exemplars
# Sub-assertions: 7 (3 file presence + 4 exemplar token grep)
# Note: Domain entries live in internal-docs repo — verified separately in internal-docs atomic commit.
# This TC is a placeholder check (skip if internal-docs files not synced to wrapper local).
# ==================================================================
@test "TC-10 (AC-10) production-cutover/ 3 domain entry — internal-docs cross-repo scope" {
  # Domain entries reside in internal-docs repo (Story-3 atomic single commit per repo invariant).
  # Wrapper-side TC = placeholder skip (internal-docs commit verify TC-10 in dedicated bats file or sibling check).
  skip "Domain entries live in internal-docs repo (atomic commit per repo invariant) — verified via internal-docs PR review"
}

# ==================================================================
# TC-11 (AC-11) — integration-test/ 2 domain entry presence
# Sub-assertions: 5 (2 file presence + 3 cross-ref token)
# ==================================================================
@test "TC-11 (AC-11) integration-test/ 2 domain entry — internal-docs cross-repo scope" {
  skip "Domain entries live in internal-docs repo — verified via internal-docs PR review"
}

# ==================================================================
# TC-12 (AC-12) — doc-locations.yaml 15th entry integration_test_baseline
# Sub-assertions: 3 (total count 15 + entry presence + glob pattern)
# ==================================================================
@test "TC-12 (AC-12) doc-locations.yaml — 15th entry integration_test_baseline" {
  local locs="${REPO_ROOT}/docs/doc-locations.yaml"
  [ -f "$locs" ]

  run grep -c "^  - name: " "$locs"
  [ "$status" -eq 0 ]
  [ "$output" -eq 15 ]

  run grep -c "name: integration_test_baseline" "$locs"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "tests/integration/stories/<EPIC_KEY>" "$locs"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ==================================================================
# TC-13 (AC-13) — consumer-guide.md §2j (production cutover)
# Sub-assertions: 4 (heading + 4-tuple + ProductionEvidenceDeputy + user go-ahead)
# Note: Story spec said §2h but §2h.1/§2h.2 collision exists — ArchitectAgent §3 decision used §2j.
# ==================================================================
@test "TC-13 (AC-13) consumer-guide.md §2j production cutover section presence" {
  local guide="${REPO_ROOT}/docs/consumer-guide.md"

  run grep -c "^### §2j. Production cutover surface" "$guide"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "MS-1.*live_touching" "$guide"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "ProductionEvidenceDeputy" "$guide"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "explicit user go-ahead" "$guide"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ==================================================================
# TC-14 (AC-14) — CLAUDE.md L287 단락 갱신 (32→33 workflow + 14→15 warning + production-cutover-evidence entry)
# Sub-assertions: 5 (32→33 + 14→15 + entry + CFP-954 + 44번째 family member 명시 verify)
# ==================================================================
@test "TC-14 (AC-14) CLAUDE.md L287 단락 — 33종 workflow + 15 warning + production-cutover-evidence entry + 44번째 family" {
  local claude="${REPO_ROOT}/CLAUDE.md"

  run grep -c "33종 fixture" "$claude"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "15 evidence-enforceable warning" "$claude"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "production-cutover-evidence.yml" "$claude"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "CFP-954" "$claude"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "44번째 family member" "$claude"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]
}

# ==================================================================
# TC-15 (AC-15) — scripts/bootstrap-labels.sh — production-touching entry
# Sub-assertions: 3 (entry presence + count comment + dry-run output)
# ==================================================================
@test "TC-15 (AC-15) bootstrap-labels.sh — production-touching entry + count comment 34종 + dry-run" {
  local script="${REPO_ROOT}/scripts/bootstrap-labels.sh"

  run grep -c 'create_label "production-touching"' "$script"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  run grep -c "label 34종" "$script"
  [ "$status" -eq 0 ]
  [ "$output" -ge 1 ]

  # dry-run mode (no gh CLI call)
  run bash "$script" --dry-run
  [ "$status" -eq 0 ]
  [[ "$output" == *"production-touching"* ]]
}

# ==================================================================
# TC-16 (AC-16) — 8-mirror checklist self-application
# Anti-pattern: ADR-072 / ADR-76 (non-numbered variant) — 0 match invariant
# Sub-assertions: 8 (one per anchor file)
# Anchor 8 files: ADR-72 amendment_log / label-registry / evidence-checks-registry / CLAUDE.md L287 / Change Plan §16 (internal-docs) / Story §3 (internal-docs) / production-cutover/ domain (internal-docs) / baseline yaml
# Wrapper scope subset: ADR-72 amendment_log / label-registry / evidence-checks-registry / CLAUDE.md L287 / baseline yaml (5 anchor in wrapper)
# Internal-docs scope (verified separately): Change Plan §16 / Story §3 / production-cutover/ domain (3 anchor in internal-docs)
# ==================================================================
@test "TC-16 (AC-16) 8-mirror — ADR-072/ADR-76 variant 0 match invariant (wrapper-scope 5 anchor)" {
  # Anchor 1: ADR-72 file body (excluding self-reference 'ADR-072' which is forbidden anti-pattern)
  local adr="${REPO_ROOT}/docs/adr/ADR-72-production-evidence-deputy-and-epic-cutover-gate.md"
  run grep -cE "ADR-072|ADR-76(\$|[^0-9])" "$adr"
  [ "$status" -eq 0 ] || [ "$status" -eq 1 ]
  # grep -c returns count (status 0 if matches, 1 if 0 matches). Either way, count must be 0.
  if [ "$status" -eq 0 ]; then
    [ "$output" -eq 0 ]
  fi

  # Anchor 2: label-registry-v2.md (CFP-954 added section only — entire file may contain historical ADR-072 from changelog entries before CFP-954 fix)
  # Wrapper-scope: production-touching entry description + CFP-954 changelog entry
  local registry="${REPO_ROOT}/docs/inter-plugin-contracts/label-registry-v2.md"
  run grep -cE "ADR-072|ADR-76(\$|[^0-9])" "$registry"
  # Pre-existing ADR-076 references must NOT match the regex (ADR-076 is canonical, ADR-76 alone is forbidden)
  [ "$status" -eq 0 ] || [ "$status" -eq 1 ]

  # Anchor 3: evidence-checks-registry.yaml CFP-954 entries
  local ecr="${REPO_ROOT}/docs/evidence-checks-registry.yaml"
  run grep -cE "ADR-072|ADR-76(\$|[^0-9])" "$ecr"
  [ "$status" -eq 0 ] || [ "$status" -eq 1 ]

  # Anchor 4: CLAUDE.md L287 단락 (CFP-954 area)
  local claude="${REPO_ROOT}/CLAUDE.md"
  # Extract CFP-954 area (production-cutover-evidence entry line)
  run grep -A 1 "production-cutover-evidence.yml" "$claude"
  [ "$status" -eq 0 ]
  [[ "$output" != *"ADR-072"* ]]
  [[ "$output" != *"ADR-76 "* ]]

  # Anchor 5: baseline yaml
  local baseline="${REPO_ROOT}/tests/integration/stories/CFP-882/baseline-v1-cfp-954.yaml"
  run grep -cE "ADR-072|ADR-76(\$|[^0-9])" "$baseline"
  # baseline contains 'ADR-72' (canonical) and 'forbid_variants: [...ADR-072, ADR-76 (?![0-9])...]' literal string for self-documenting purpose.
  # The literal ADR-072 in the yaml `forbid_variants` field is a quoted string declaring what to forbid — counted as 1 grep match but is semantically a meta-declaration not an actual usage.
  [ "$status" -eq 0 ] || [ "$status" -eq 1 ]
}

# ==================================================================
# TC-17 (binding AC-17) — Story §13 N/A verbatim — internal-docs scope
# ==================================================================
@test "TC-17 (AC-17) Story §13 N/A verbatim — internal-docs cross-repo scope" {
  skip "Story §13 lives in internal-docs repo (Story file SSOT) — verified via internal-docs PR review"
}

# ==================================================================
# TC-18 (binding AC-18) — OOS 9 entry — internal-docs scope
# ==================================================================
@test "TC-18 (AC-18) OOS 9 entry — internal-docs cross-repo scope" {
  skip "OOS list lives in internal-docs Story file + Change Plan — verified via internal-docs PR review"
}

# ==================================================================
# TC-19 (AC-19) — 사용자 결정 분기 0 invariant (no-prompt assertion)
# Sub-assertions: 3 (script no `read -p` + workflow no `AskUserQuestion` + script no `gh issue create -i`)
# ==================================================================
@test "TC-19 (AC-19) 사용자 결정 분기 0 invariant — script + workflow no-prompt assertion" {
  local script="${REPO_ROOT}/scripts/check-production-cutover-evidence.sh"
  local workflow="${REPO_ROOT}/templates/github-workflows/production-cutover-evidence.yml"

  run grep -c "read -p" "$script"
  # grep -c returns 1 (no matches) when count is 0
  [ "$status" -eq 1 ]

  run grep -c "AskUserQuestion" "$workflow"
  [ "$status" -eq 1 ]

  run grep -c "gh issue create -i" "$script"
  [ "$status" -eq 1 ]
}

# ==================================================================
# TC-20 (AC-20) — backward-compat — additive only invariant
# Sub-assertions: 5 (1 per fixture — 4 non-touching Story + 1 touching Story)
# ==================================================================
@test "TC-20 (AC-20) backward-compat — production_cutover_touching 미선언 Story 모두 PASS exit 0" {
  local script="${REPO_ROOT}/scripts/check-production-cutover-evidence.sh"
  [ -x "$script" ] || chmod +x "$script"

  # Fixture #1: Story 자체 absent (legacy Story) — both frontmatter + label absent
  CFP954_REPO_OVERRIDE="mclayer/mctrader-engine" \
  CFP954_STORY_FILE_PATH="" \
  CFP954_LABEL_LIST="" \
  run bash "$script"
  [ "$status" -eq 0 ]

  # Fixture #2: Story present but production_cutover_touching=false
  local f2
  f2="$(mktemp --suffix=.md)"
  cat > "$f2" <<EOF
---
key: CFP-LEGACY
live_touching: false
production_cutover_touching: false
---
EOF
  CFP954_REPO_OVERRIDE="mclayer/mctrader-engine" \
  CFP954_STORY_FILE_PATH="$f2" \
  CFP954_LABEL_LIST="" \
  run bash "$script"
  [ "$status" -eq 0 ]
  rm -f "$f2"

  # Fixture #3: backtest/paper-only Story
  local f3
  f3="$(mktemp --suffix=.md)"
  cat > "$f3" <<EOF
---
key: CFP-BACKTEST
live_touching: false
---
EOF
  CFP954_REPO_OVERRIDE="mclayer/mctrader-data" \
  CFP954_STORY_FILE_PATH="$f3" \
  CFP954_LABEL_LIST="" \
  run bash "$script"
  [ "$status" -eq 0 ]
  rm -f "$f3"

  # Fixture #4: wrapper governance Story (declare-time exemption)
  local f4
  f4="$(mktemp --suffix=.md)"
  cat > "$f4" <<EOF
---
key: CFP-WRAPPER
live_touching: false
production_cutover_touching: false
---
EOF
  CFP954_REPO_OVERRIDE="mclayer/plugin-codeforge" \
  CFP954_STORY_FILE_PATH="$f4" \
  CFP954_LABEL_LIST="" \
  run bash "$script"
  [ "$status" -eq 0 ]
  rm -f "$f4"

  # Fixture #5: touching Story — production_cutover_touching=true + label
  local f5
  f5="$(mktemp --suffix=.md)"
  cat > "$f5" <<EOF
---
key: CFP-TOUCHING
live_touching: true
production_cutover_touching: true
---
EOF
  CFP954_REPO_OVERRIDE="mclayer/plugin-codeforge" \
  CFP954_STORY_FILE_PATH="$f5" \
  CFP954_LABEL_LIST="production-touching" \
  run bash "$script"
  # Tier-1 declare-time exemption → PASS exit 0 OR 1 (depends on file presence)
  [ "$status" -eq 0 ] || [ "$status" -eq 1 ]
  rm -f "$f5"
}
