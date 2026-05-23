#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-508 / ADR-060 Amendment 7 / §결정 20 — evidence-checks-registry entry name ↔ workflow
# file naming convention lint (warning mode)
# CFP-478 / ADR-061 §결정 1 + Amendment 1 §결정 6.A — heredoc Python 외부 .py split
#
# Usage / exit code / semantics 상세: scripts/check-evidence-registry-naming.sh header.
import sys, os
from pathlib import Path

# Windows console (cp949) 호환 — UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import yaml
except ImportError:
    print("check-evidence-registry-naming: pyyaml 미설치 (meta-error)", file=sys.stderr)
    sys.exit(2)

# ─── DRIFT allowlist (ADR-060 Amendment 7 §결정 20 — CFP-954 +2 production-cutover pair) ───
DRIFT_ALLOWLIST = {
    ("rate-limit-fallback-rate",       "rate-limit-fallback-kpi.yml"):       "ADR-057 KPI dashboard — basename divergence (rate vs kpi)",
    ("lane-evidence-trail",            "lane-evidence-check.yml"):           "ADR-031 lane evidence — basename divergence (trail vs check)",
    ("doc-locations-registry",         "doc-locations-check.yml"):           "ADR-041 doc-locations — basename divergence (registry vs check)",
    ("inter-plugin-contracts",         "contract-lint.yml"):                 "multi-job workflow pattern — 4 entry 공유 (ADR-008/010)",
    ("inter-plugin-drift",             "contract-lint.yml"):                 "multi-job workflow pattern — 4 entry 공유 (ADR-011)",
    ("comment-prefix-registry",        "contract-lint.yml"):                 "multi-job workflow pattern — 4 entry 공유 (comment-prefix-registry-v1)",
    ("label-registry-sync",            "contract-lint.yml"):                 "multi-job workflow pattern — 4 entry 공유 (label-registry-v2)",
    ("marketplace-sync",               "contract-lint.yml"):                 "Retired entry — multi-job pattern (CFP-457 cleanup)",
    ("write-permission-redistribution","lint.yml"):                          "multi-job workflow pattern — lint.yml shared job",
    ("evidence-registry-schema-validation", "evidence-registry-check.yml"): "ADR-060 Amendment 2 — schema validation lint basename divergence",
    ("wording-ssot-grep-lint",             "wording-ssot-check.yml"):       "ADR-068 §결정 5 wording SSOT lint — basename divergence (grep-lint vs check)",
    ("workflow-permissions-block-presence", "workflow-permissions-check.yml"): "ADR-060 Amendment 8 §결정 21 — workflow permissions lint basename divergence (block-presence vs check)",
    ("retro-alert-pickup-rate",            "retro-alert-pickup-kpi.yml"):      "ADR-045 §D-5 CFP-628 — KPI sentinel basename divergence (rate vs kpi)",
    ("auto-phase-label-sibling-parity",    "sibling-workflow-parity.yml"):     "CFP-685 carrier — CFP-481/ADR-060 Amendment 4 lineage 보존, family scope self-app naming",
    ("workflow-actionlint-precommit",      "actionlint-check.yml"):            "CFP-688 §5.G.b — ADR-026 prescribed frontmatter action name (ADR-040 Amd3 §7.A verbatim binding) vs workflow basename divergence",
    ("post-merge-followup-workflow-success-rate-kpi", "post-merge-followup-success-rate-kpi.yml"): "CFP-688 §5.G.d — ADR-026 prescribed entry name (workflow infix) vs workflow basename divergence",
    ("production-cutover-deputy-spawn-evidence", "production-cutover-evidence.yml"): "CFP-954 / ADR-72 §결정 3 — entry name semantic 'deputy-spawn-evidence' 보존 (ProductionEvidenceDeputy spawn trigger gate), workflow 는 broader 'production-cutover-evidence' cover (Conservative no-rename §결정 20)",
    ("epic-cutover-gate-evidence-quad-check", "production-cutover-evidence.yml"): "CFP-954 / ADR-72 §결정 5 — entry name semantic 'epic-cutover-gate-evidence-quad' 보존 (EPIC CLOSED gate 4-evidence-quad verify), workflow 는 broader 'production-cutover-evidence' cover (Conservative no-rename §결정 20)",
    ("canary-compatibility-check",      "canary-promotion-criteria.yml"):    "CFP-991 / ADR-72 Amd 3 + ADR-076 §결정 9.6 — entry name semantic 'canary-compatibility-check' 보존 (canary 호환성 4-tuple evidence verify, reconcile-protocol-v1 §4.14 canary_compatibility_check_binding), workflow 는 broader 'canary-promotion-criteria' cover (Conservative no-rename §결정 20)",
    ("dependency-order-enforce",        "dependency-order-check.yml"):       "CFP-1059 / ADR-090 §결정 2 — entry name semantic cross-layer 'enforce' verb 보존 (expand source-first / contract leaf-first 변경 순서 invariant enforcement), workflow basename 'dependency-order-check' substring miss (enforce vs check) (Conservative no-rename §결정 20)",
}

REGISTRY_PATH = Path("docs/evidence-checks-registry.yaml")

if not REGISTRY_PATH.exists():
    print(f"check-evidence-registry-naming: registry file 부재: {REGISTRY_PATH} (meta-error)", file=sys.stderr)
    sys.exit(2)

try:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
except yaml.YAMLError as e:
    print(f"check-evidence-registry-naming: yaml parse 실패: {e} (meta-error)", file=sys.stderr)
    sys.exit(2)
except OSError as e:
    print(f"check-evidence-registry-naming: file read 실패: {e} (meta-error)", file=sys.stderr)
    sys.exit(2)

if not isinstance(data, dict) or "entries" not in data:
    print("check-evidence-registry-naming: registry yaml 구조 이상 — entries 키 부재 (meta-error)", file=sys.stderr)
    sys.exit(2)

entries = data.get("entries", [])
if not isinstance(entries, list):
    print("check-evidence-registry-naming: entries 가 list 가 아님 (meta-error)", file=sys.stderr)
    sys.exit(2)

violations = []
drift_advisories = []
checked = 0
skipped_retired = 0

for entry in entries:
    if not isinstance(entry, dict):
        continue

    name = entry.get("name", "(unnamed)")
    status = entry.get("status", "Active")

    if status == "Retired":
        skipped_retired += 1
        continue

    workflow_path_str = entry.get("workflow", "")
    if not workflow_path_str:
        continue

    # CFP-827 — `.get(k, default)` 는 key 부재 시만 default 반환. ADR-060 schema 가
    # `detect_command: null` 허용 (e.g. behavioral directive only entry — adr-077-* 등) →
    # `.get("detect_command", "")` 가 None 반환 → None.strip() AttributeError.
    # `or ""` 로 null + missing + empty 3-case 통일.
    detect_command = entry.get("detect_command") or ""
    is_github_actions_runtime = (detect_command.strip() == "github-actions-runtime")

    workflow_path = Path(workflow_path_str)
    workflow_basename = workflow_path.name

    checked += 1

    if not workflow_path.exists():
        violations.append({
            "entry": name,
            "workflow": workflow_path_str,
            "reason": f"workflow file 부재: {workflow_path_str}",
        })
        continue

    if is_github_actions_runtime:
        continue

    entry_name_lower = name.lower()
    basename_no_ext = workflow_basename.replace(".yml", "").replace(".yaml", "").lower()

    exact_match = (entry_name_lower == basename_no_ext)
    partial_match = (entry_name_lower in basename_no_ext) or (basename_no_ext in entry_name_lower)

    allowlist_key = (name, workflow_basename)
    in_allowlist = allowlist_key in DRIFT_ALLOWLIST

    if not (exact_match or partial_match or in_allowlist):
        violations.append({
            "entry": name,
            "workflow": workflow_path_str,
            "reason": (
                f"naming DRIFT allowlist 밖 — entry name '{name}' vs workflow basename "
                f"'{basename_no_ext}' (substring match 없음, allowlist 미등록)"
            ),
        })
    elif in_allowlist and not (exact_match or partial_match):
        drift_advisories.append({
            "entry": name,
            "workflow": workflow_basename,
            "reason": DRIFT_ALLOWLIST[allowlist_key],
        })

print(
    f"check-evidence-registry-naming: {checked} entry 검증 "
    f"({skipped_retired} Retired skip, {len(drift_advisories)} allowlist DRIFT advisory)"
)

if drift_advisories:
    print(f"\nADVISORY — allowlist DRIFT {len(drift_advisories)}건 (Conservative no-rename policy, §결정 20):")
    for d in drift_advisories:
        print(f"  [{d['entry']}] → {d['workflow']} — {d['reason']}")

if not violations:
    print("OK workflow file existence + naming convention lint PASS (ADR-060 §결정 20)")
    sys.exit(0)

print(f"\nVIOLATION {len(violations)}건 — workflow file 부재 OR allowlist 밖 DRIFT:", file=sys.stderr)
for v in violations:
    print(f"  [{v['entry']}] {v['reason']}", file=sys.stderr)
print(
    "\nConservative no-rename policy (ADR-060 Amendment 7 §결정 20): "
    "workflow file 부재 시 생성 의무. DRIFT 시 DRIFT_ALLOWLIST 등록 또는 entry name 정정 의무.",
    file=sys.stderr,
)
print(
    "Bypass (운영 hotfix 한정): `hotfix-bypass:evidence-naming` label + PR description "
    "`### Bypass reason` 본문 (ADR-024 Amendment 3 §결정 6.A).",
    file=sys.stderr,
)
sys.exit(1)
