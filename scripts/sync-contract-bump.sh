#!/usr/bin/env bash
# CFP-408 — Cross-repo sibling sync PR sequence 자동화
#
# inter-plugin contract version bump 시 3단계 sync PR sequence 자동 생성:
#   1) Canonical lane plugin repo (MAJOR bump 필수 first per ADR-010 Amendment 2)
#   2) Wrapper sibling repo (mclayer/plugin-codeforge)
#   3) Marketplace mirror PR (mclayer/marketplace) — version field 변경 시
#
# Merge order: canonical → wrapper sibling → marketplace.
# 본 script 는 PR 본문에 sequence dependency 명시 + branch + commit + push + gh pr create.
#
# 안전 기본값: --dry-run mode 가 default 가 아니지만, real-run 은 confirmation prompt 의무.
#
# 사용:
#   $ scripts/sync-contract-bump.sh <contract> <new-version> [--dry-run]
#
#   예:
#   $ scripts/sync-contract-bump.sh review-verdict 4.2 --dry-run
#   $ scripts/sync-contract-bump.sh design-output 2.2
#
# 인자:
#   <contract>      — MANIFEST.yaml 의 contracts[].name 값 (예: review-verdict, fix-event)
#                     주의: kind:registry (fix-event 등) 는 본 script 적용 대상 외 (ADR-010 §결정 3)
#   <new-version>   — X.Y 또는 X.Y.Z (SemVer-like, ADR-008 룰)
#   --dry-run       — 모든 단계 simulation 만 출력, 파일 / git / gh 변경 없음
#
# Exit codes:
#   0 — 정상 종료 (dry-run 또는 real-run PASS)
#   2 — 인자 부족 / 사용법 오류
#   3 — contract 식별 실패 (MANIFEST 미등록 / kind:registry / canonical_repo null)
#   4 — version 형식 위반
#   5 — git / gh 실행 실패 (real-run)
#   6 — sibling file 미발견 / canonical fetch 실패
#
# Dependencies: bash, git, gh CLI, python3 + pyyaml (MANIFEST parse).
# ADR-010 §결정 4 (sync 트리거) + Amendment 2 (canonical-first MAJOR) 정합.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MANIFEST="$REPO_ROOT/docs/inter-plugin-contracts/MANIFEST.yaml"

usage() {
    cat <<'USAGE'
Usage: sync-contract-bump.sh <contract-name> <new-version> [--dry-run]

inter-plugin contract version bump 시 3단계 sync PR sequence 자동 생성.

Arguments:
  contract-name    MANIFEST.yaml 의 contracts[].name (예: review-verdict)
  new-version      X.Y 또는 X.Y.Z (ADR-008 SemVer-like)

Options:
  --dry-run        모든 단계 simulation 만 출력 (파일/git/gh 변경 없음)
  -h, --help       이 메시지 출력

Examples:
  sync-contract-bump.sh review-verdict 4.2 --dry-run
  sync-contract-bump.sh design-output 2.2

Merge order:
  1) canonical (lane plugin repo)
  2) wrapper sibling (plugin-codeforge)
  3) marketplace mirror (mclayer/marketplace, version 필드 변경 시만)

SSOT: ADR-010 (sibling sync) + ADR-008 (versioning) + ADR-016 (marketplace).
USAGE
}

# ---------- arg parse ----------
if [ "$#" -eq 0 ]; then
    usage >&2
    exit 2
fi

case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
esac

if [ "$#" -lt 2 ]; then
    echo "ERROR: contract-name + new-version 인자 필요" >&2
    usage >&2
    exit 2
fi

CONTRACT="$1"
NEW_VERSION="$2"
DRY_RUN=0
shift 2
while [ "$#" -gt 0 ]; do
    case "$1" in
        --dry-run) DRY_RUN=1 ;;
        *) echo "ERROR: 알 수 없는 인자: $1" >&2; usage >&2; exit 2 ;;
    esac
    shift
done

# ---------- version format validation ----------
if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]; then
    echo "ERROR: version 형식 위반 (X.Y 또는 X.Y.Z 필요) — '$NEW_VERSION'" >&2
    exit 4
fi

# ---------- MANIFEST lookup ----------
if [ ! -f "$MANIFEST" ]; then
    echo "ERROR: MANIFEST.yaml 미발견: $MANIFEST" >&2
    exit 3
fi

# Python helper: contract entry lookup + canonical_repo extraction.
LOOKUP_RESULT=$(python3 - "$CONTRACT" "$MANIFEST" <<'PY' 2>&1
import sys, yaml, json
contract_name, manifest_path = sys.argv[1], sys.argv[2]
with open(manifest_path, encoding="utf-8") as f:
    data = yaml.safe_load(f)
# contracts[] = kind:contract entries (ADR-010 정합)
for entry in data.get("contracts", []) or []:
    if entry.get("name") == contract_name or entry.get("name") == contract_name.replace("-", "_"):
        canonical_repo = entry.get("canonical_repo")
        canonical_path = entry.get("canonical_path", "docs/inter-plugin-contracts/")
        if not canonical_repo:
            print(f"ERROR: contract {contract_name} canonical_repo null (wrapper-canonical?)", file=sys.stderr)
            sys.exit(3)
        files = entry.get("files", [])
        active_file = None
        for fent in files:
            if fent.get("status") == "Active":
                active_file = fent.get("file")
                break
        print(json.dumps({
            "name": entry["name"],
            "canonical_repo": canonical_repo,
            "canonical_path": canonical_path,
            "active_file": active_file,
            "kind": "contract",
        }))
        sys.exit(0)
# Not in contracts[] — check registries[] (kind:registry — out of scope)
for entry in data.get("registries", []) or []:
    if entry.get("name") == contract_name or entry.get("name") == contract_name.replace("-", "_"):
        print(f"ERROR: '{contract_name}' is kind:registry — sync-contract-bump.sh applies to kind:contract only (ADR-010 §결정 3)", file=sys.stderr)
        sys.exit(3)
# Also check by file prefix
for entry in (data.get("contracts") or []) + (data.get("registries") or []):
    for fent in entry.get("files", []):
        fname = fent.get("file", "")
        if fname.startswith(f"{contract_name}-"):
            kind = "contract" if entry in (data.get("contracts") or []) else "registry"
            if kind == "registry":
                print(f"ERROR: '{contract_name}' matches kind:registry file — sync-contract-bump.sh applies to kind:contract only", file=sys.stderr)
                sys.exit(3)
print(f"ERROR: contract '{contract_name}' MANIFEST.yaml 미등록", file=sys.stderr)
sys.exit(3)
PY
)
LOOKUP_RC=$?

if [ "$LOOKUP_RC" -ne 0 ]; then
    echo "$LOOKUP_RESULT" >&2
    exit "$LOOKUP_RC"
fi

# Parse JSON output
CANONICAL_REPO=$(echo "$LOOKUP_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['canonical_repo'])")
CANONICAL_PATH=$(echo "$LOOKUP_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['canonical_path'])")
CONTRACT_NAME_CANON=$(echo "$LOOKUP_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['name'])")

# Determine MAJOR bump (canonical-first 의무 per ADR-010 Amendment 2)
NEW_MAJOR="${NEW_VERSION%%.*}"
ACTIVE_FILE=$(echo "$LOOKUP_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('active_file') or '')")
IS_MAJOR_BUMP=0
if [ -n "$ACTIVE_FILE" ]; then
    # active file 명에서 vN 추출 (e.g., review-verdict-v4.md → 4)
    CURRENT_MAJOR=$(echo "$ACTIVE_FILE" | sed -E 's/.*-v([0-9]+).*/\1/')
    if [ "$NEW_MAJOR" -gt "$CURRENT_MAJOR" ] 2>/dev/null; then
        IS_MAJOR_BUMP=1
    fi
fi

NEW_FILE_BASENAME="${CONTRACT}-v${NEW_MAJOR}.md"
WRAPPER_SIBLING="$REPO_ROOT/docs/inter-plugin-contracts/$NEW_FILE_BASENAME"

# Slug for branch (CFP-NNN 인지 모름 → contract+version 기반 fallback)
BRANCH_SLUG="contract-sync/${CONTRACT}-v${NEW_VERSION//./-}"

# ---------- emit plan ----------
echo "===================================================="
echo "sync-contract-bump.sh — CFP-408"
echo "===================================================="
echo "Contract:        $CONTRACT_NAME_CANON ($CONTRACT)"
echo "New version:     $NEW_VERSION"
echo "Canonical repo:  $CANONICAL_REPO"
echo "Canonical path:  $CANONICAL_PATH"
echo "Wrapper sibling: docs/inter-plugin-contracts/$NEW_FILE_BASENAME"
echo "Bump type:       $([ "$IS_MAJOR_BUMP" -eq 1 ] && echo "MAJOR (canonical-first 의무 — ADR-010 Amendment 2)" || echo "MINOR/PATCH (wrapper-first 허용)")"
echo "Branch slug:     $BRANCH_SLUG"
echo "Mode:            $([ "$DRY_RUN" -eq 1 ] && echo "DRY-RUN (no side effects)" || echo "REAL-RUN")"
echo ""

# Merge order plan
echo "Planned merge order:"
if [ "$IS_MAJOR_BUMP" -eq 1 ]; then
    echo "  1) canonical PR    ($CANONICAL_REPO) — MAJOR bump first 의무"
    echo "  2) wrapper sibling (mclayer/plugin-codeforge) — canonical merge 후"
    echo "  3) marketplace     (mclayer/marketplace) — version 변경 시"
else
    echo "  1) canonical PR    ($CANONICAL_REPO)"
    echo "  2) wrapper sibling (mclayer/plugin-codeforge)"
    echo "  3) marketplace     (mclayer/marketplace) — version 변경 시"
fi
echo ""

# ---------- Stage 1: wrapper sibling preparation (file diff preview) ----------
echo "----- Stage 1: wrapper sibling (mclayer/plugin-codeforge) -----"
if [ -f "$WRAPPER_SIBLING" ]; then
    echo "  · sibling file 존재: $WRAPPER_SIBLING"
    echo "    → frontmatter contract_version 갱신 + amendment_log entry 추가 의무 (수동)"
else
    echo "  · sibling file 신설 필요: $WRAPPER_SIBLING"
    echo "    → canonical $CANONICAL_REPO 의 $CANONICAL_PATH$NEW_FILE_BASENAME 본문 verbatim mirror"
    echo "    → 상위 SSOT 위치 섹션 추가 의무"
fi
echo "  · branch: $BRANCH_SLUG"
echo "  · commit: 'docs(contract): $CONTRACT v$NEW_VERSION sibling sync'"
echo "  · PR title: 'docs(contract): $CONTRACT v$NEW_VERSION wrapper sibling sync'"
echo ""

# ---------- Stage 2: canonical lane plugin ----------
echo "----- Stage 2: canonical ($CANONICAL_REPO) -----"
echo "  · target file: $CANONICAL_PATH$NEW_FILE_BASENAME"
echo "  · branch: $BRANCH_SLUG"
echo "  · note: 본 script 는 canonical repo clone / commit 자동화 미포함 (Phase 2 follow-up)"
echo "    → 수동 절차: git clone $CANONICAL_REPO; 본 sibling file을 verbatim 복사; PR open"
echo ""

# ---------- Stage 3: marketplace ----------
echo "----- Stage 3: marketplace (mclayer/marketplace) -----"
echo "  · version 필드 mirror 필요한 경우만 실행"
echo "  · plugin.json 의 version 변경 동반 시 mclayer/marketplace 의 plugins[name=$CONTRACT_NAME_CANON] sync PR"
echo "  · note: contract MAJOR 만 변경, plugin.json version 무변경 시 skip"
echo ""

# ---------- Stage 4: Story / PR body footer template ----------
echo "----- PR body sequence dependency footer template -----"
cat <<EOF
---

## Sync sequence (ADR-010 §결정 4 + Amendment 2)

Merge order:
1. canonical ($CANONICAL_REPO) → wrapper sibling → marketplace mirror
2. **MAJOR bump 시 canonical-first 의무** (현 PR bump type: $([ "$IS_MAJOR_BUMP" -eq 1 ] && echo "MAJOR" || echo "MINOR/PATCH"))
3. 본 PR merge 후 다음 PR open

cc: \`scripts/sync-contract-bump.sh $CONTRACT $NEW_VERSION\`
EOF
echo ""

if [ "$DRY_RUN" -eq 1 ]; then
    echo "===================================================="
    echo "DRY-RUN complete — no side effects."
    echo "===================================================="
    exit 0
fi

# ---------- REAL-RUN: confirmation + execution ----------
echo "===================================================="
echo "REAL-RUN mode — 본 script 는 wrapper sibling stage 만 자동화."
echo "canonical / marketplace stage 는 수동 (Phase 2 follow-up CFP)."
echo "===================================================="
echo ""
echo "Proceed with wrapper sibling branch + commit + PR? [y/N]"
read -r CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Aborted by user."
    exit 0
fi

# gh availability check
if ! command -v gh >/dev/null 2>&1; then
    echo "ERROR: gh CLI 미설치 — real-run 불가" >&2
    exit 5
fi
if ! gh auth status >/dev/null 2>&1; then
    echo "ERROR: gh 미인증 — 'gh auth login' 실행 후 재시도" >&2
    exit 5
fi

# Create branch + verify sibling file exists (manual edit 의무)
if [ ! -f "$WRAPPER_SIBLING" ]; then
    echo "ERROR: wrapper sibling file $WRAPPER_SIBLING 미발견 — 수동 작성 후 재실행 의무" >&2
    exit 6
fi

cd "$REPO_ROOT"
git checkout -b "$BRANCH_SLUG" 2>/dev/null || git checkout "$BRANCH_SLUG"
git add "$WRAPPER_SIBLING" docs/inter-plugin-contracts/MANIFEST.yaml 2>/dev/null || true
if ! git diff --staged --quiet; then
    git commit -m "docs(contract): $CONTRACT v$NEW_VERSION sibling sync

ADR-010 §결정 4 sibling sync trigger.
Bump type: $([ "$IS_MAJOR_BUMP" -eq 1 ] && echo "MAJOR" || echo "MINOR/PATCH")
sync-contract-bump.sh CFP-408." || { echo "ERROR: commit 실패" >&2; exit 5; }
else
    echo "WARN: staged 변경 없음 — sibling file 또는 MANIFEST 수동 갱신 필요"
fi

git push -u origin "$BRANCH_SLUG" || { echo "ERROR: push 실패" >&2; exit 5; }

PR_TITLE="docs(contract): $CONTRACT v$NEW_VERSION wrapper sibling sync"
PR_BODY=$(cat <<EOF
## Summary
- $CONTRACT contract v$NEW_VERSION wrapper sibling sync
- Canonical SSOT: \`$CANONICAL_REPO/$CANONICAL_PATH$NEW_FILE_BASENAME\`
- Bump type: $([ "$IS_MAJOR_BUMP" -eq 1 ] && echo "MAJOR — canonical-first per ADR-010 Amendment 2" || echo "MINOR/PATCH")

## Sync sequence (ADR-010)
1. canonical ($CANONICAL_REPO) → wrapper sibling (this PR) → marketplace
2. Merge order strict 의무 (\`merge-order:N\` label per ADR-050)

## Generated by
\`scripts/sync-contract-bump.sh $CONTRACT $NEW_VERSION\` (CFP-408)
EOF
)
gh pr create --title "$PR_TITLE" --body "$PR_BODY" --base main --head "$BRANCH_SLUG" || { echo "ERROR: gh pr create 실패" >&2; exit 5; }

echo ""
echo "===================================================="
echo "Wrapper sibling PR opened. Next steps:"
echo "  1) canonical repo ($CANONICAL_REPO) 에 동일 변경 PR open"
echo "  2) marketplace.json 의 plugins[].version 변경 동반 시 marketplace sync PR"
echo "===================================================="
exit 0
