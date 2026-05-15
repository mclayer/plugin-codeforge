#!/usr/bin/env bash
# CFP-508 / ADR-060 Amendment 7 / §결정 20 — evidence-checks-registry entry name ↔ workflow
# file naming convention lint (warning mode)
#
# 검증 룰:
#   1. 각 entry 의 workflow: field path 가 실제 file 존재 검증 (file existence check)
#      - Exception 1: detect_command: github-actions-runtime entry → workflow file 존재만 검증 (job name 무관)
#      - Exception 2: status: Retired entry → skip
#   2. naming convention advisory:
#      - entry name 이 workflow basename 의 substring OR vice versa OR explicit allowlist
#      - DRIFT (no match) 시 stderr advisory output (workflow rename 강제 X)
#      - DRIFT allowlist 10건 (ADR-060 Amendment 7 §결정 20 audit 결과 hardcode)
#        미래 entry 추가 시 명시적 allowlist 등록 의무
#
# Exit code (ADR-060 Amendment 2 §결정 15 3-tier):
#   0 PASS: 모든 workflow file 존재 + DRIFT 모두 allowlist 안
#   1 violation: workflow file 부재 OR DRIFT 가 allowlist 밖
#   2 meta-error: yaml parse 실패 / python3 미설치 등 환경 결격
#
# Usage:
#   $ bash scripts/check-evidence-registry-naming.sh            # 전체 registry 검증
#   $ bash scripts/check-evidence-registry-naming.sh --help     # 이 header 출력 + exit 0
#
# carrier: ADR-060 Amendment 7 + §결정 20 (CFP-508)
# scope: docs/evidence-checks-registry.yaml
# Conservative no-rename policy: workflow rename 금지 — CI history + branch protection
#   required_status_checks.contexts 영향 회피 (§결정 20)

set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    # bash comment block (파일 상단 #으로 시작하는 연속 라인) 만 출력
    sed -n '2,/^[^#]/{ /^[^#]/q; s/^# \?//; p }' "$0"
    exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "check-evidence-registry-naming: python3 미설치 (meta-error)" >&2
    exit 2
fi

python3 - <<'PY'
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

# ─── DRIFT allowlist (ADR-060 Amendment 7 §결정 20 — 10건 hardcode) ───
# Conservative no-rename policy: 기존 entry 에 대한 workflow rename 금지.
# 미래 신규 entry 추가 시 EXACT/partial match 로 등록 의무.
# allowlist 밖 DRIFT 발생 시 exit 1 (workflow rename 또는 allowlist 등록 의무).
DRIFT_ALLOWLIST = {
    # (entry_name, workflow_basename): reason
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

    # Exception 2: Retired entry skip
    if status == "Retired":
        skipped_retired += 1
        continue

    workflow_path_str = entry.get("workflow", "")
    if not workflow_path_str:
        # workflow 필드 없는 entry — skip (schema 검증은 check-evidence-registry.sh 담당)
        continue

    detect_command = entry.get("detect_command", "")
    is_github_actions_runtime = (detect_command.strip() == "github-actions-runtime")

    # workflow path 는 templates/ prefix 로 시작 (SSOT)
    # 실제 .github/workflows/ 에도 self-app byte-identical 존재해야 하나,
    # file existence 검증은 templates/ 기준 (SSOT canonical path)
    workflow_path = Path(workflow_path_str)
    workflow_basename = workflow_path.name

    checked += 1

    # ─── 검증 1: workflow file 존재 ───
    if not workflow_path.exists():
        violations.append({
            "entry": name,
            "workflow": workflow_path_str,
            "reason": f"workflow file 부재: {workflow_path_str}",
        })
        continue  # file 부재 시 naming check skip

    # ─── 검증 2: naming convention (github-actions-runtime exception) ───
    if is_github_actions_runtime:
        # Exception 1: github-actions-runtime entry — workflow file 존재만 검증
        continue

    entry_name_lower = name.lower()
    basename_no_ext = workflow_basename.replace(".yml", "").replace(".yaml", "").lower()

    # match 판정 (3종)
    exact_match = (entry_name_lower == basename_no_ext)
    partial_match = (entry_name_lower in basename_no_ext) or (basename_no_ext in entry_name_lower)

    # allowlist key = (entry_name, workflow_basename) 대소문자 원본
    allowlist_key = (name, workflow_basename)
    in_allowlist = allowlist_key in DRIFT_ALLOWLIST

    if not (exact_match or partial_match or in_allowlist):
        # DRIFT 가 allowlist 밖 → violation
        violations.append({
            "entry": name,
            "workflow": workflow_path_str,
            "reason": (
                f"naming DRIFT allowlist 밖 — entry name '{name}' vs workflow basename "
                f"'{basename_no_ext}' (substring match 없음, allowlist 미등록)"
            ),
        })
    elif in_allowlist and not (exact_match or partial_match):
        # allowlist 로 허용된 DRIFT → advisory
        drift_advisories.append({
            "entry": name,
            "workflow": workflow_basename,
            "reason": DRIFT_ALLOWLIST[allowlist_key],
        })

# ─── 결과 출력 ───
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
PY
