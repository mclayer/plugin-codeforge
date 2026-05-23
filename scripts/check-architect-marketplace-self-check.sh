#!/usr/bin/env bash
# Gap A — Change Plan §13 marketplace sync 선언 검증 lint
# ADR-063 §결정 21 (Amendment 9 / CFP-604) carrier
#
# 목적: PR 이 .claude-plugin/plugin.json mirrored field 를 변경할 때
#       Change Plan §13 `marketplace_sync_required` 선언의 presence/completeness 를 검증한다.
#       §결정 9 (Amendment 1) Layer 2 의 declarative declare 의무에 대응하는 mechanical 검증 채널.
#
# ADR refs:
#   ADR-063 §결정 21 (Gap A lint mandate), §결정 9 (Amendment 1, Layer 2 declare 의무)
#   ADR-054 (doc-only fast-path false-positive 차단)
#   ADR-061 §결정 5 sanity check 3종 의무 (diff inspection / lint re-run / sample file Read)
#   ADR-016 (mirrored field 4종: name/version/description/author)
#   ADR-024 Amendment 3 (hotfix-bypass:architect-marketplace-self-check family member)
#   ADR-060 §결정 5 (warning tier default — Gap A 신규 lint baseline)
#
# 입력 환경변수:
#   BASE_REF:       비교 대상 ref (default: origin/main)
#   PR_BODY:        PR description 본문 (bypass label / dogfood-out marker 감지용)
#   PR_LABELS:      개행 구분 label 목록 (hotfix-bypass / doc-only fast-path 감지용)
#   GH_TOKEN:       GitHub API 토큰 (cross-repo fetch 용)
#
# Exit codes:
#   0 = PASS (plugin.json 변경 없음, doc-only fast-path, 선언 완전)
#   1 = WARNING (선언 부재 또는 불완전 — warning tier, continue-on-error: true)
#   2 = ENVIRONMENT ERROR (jq 미설치 등)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

BASE_REF="${BASE_REF:-origin/main}"
PR_BODY="${PR_BODY:-}"
PR_LABELS="${PR_LABELS:-}"

# ──────────────────────────────── sanity check (ADR-061 §결정 5) ────────────────────────────────
# (1) diff inspection — git, jq 가용성
command -v git >/dev/null 2>&1 || { echo "❌ check-architect-marketplace-self-check: git 미설치" >&2; exit 2; }
command -v jq  >/dev/null 2>&1 || { echo "❌ check-architect-marketplace-self-check: jq 미설치 — install jq (https://stedolan.github.io/jq/)" >&2; exit 2; }

PLUGIN_JSON=".claude-plugin/plugin.json"

if [[ ! -f "$PLUGIN_JSON" ]]; then
  echo "ℹ check-architect-marketplace-self-check: $PLUGIN_JSON 부재 — skip (consumer overlay 시나리오)"
  exit 0
fi

# ──────────────────────────── bypass label 확인 ────────────────────────────────────────────────
if echo "$PR_LABELS" | grep -q "^hotfix-bypass:architect-marketplace-self-check$"; then
  echo "ℹ check-architect-marketplace-self-check: hotfix-bypass:architect-marketplace-self-check label 감지 — skip"
  echo "  ⚠ audit: hotfix-bypass 적용 — marketplace sync 선언 검증 skip됨 (ADR-024 Amendment 3)"
  exit 0
fi

# ──────────────────────────── Step 1: plugin.json mirrored field 변경 감지 ──────────────────────

git fetch origin --quiet 2>/dev/null || true

if ! git rev-parse "$BASE_REF" >/dev/null 2>&1; then
  echo "ℹ check-architect-marketplace-self-check: base ref $BASE_REF 없음 — skip"
  exit 0
fi

DIFF=$(git diff "$BASE_REF" -- "$PLUGIN_JSON" 2>/dev/null || true)

if [[ -z "$DIFF" ]]; then
  echo "✓ check-architect-marketplace-self-check: plugin.json mirrored field 무변경 — §13 선언 검증 영역 외"
  exit 0
fi

# mirrored field 4종 변경 여부 확인 (ADR-016 §결정 1 verbatim)
MIRRORED_CHANGED=0
for field in name version description author; do
  if echo "$DIFF" | grep -qE "^[-+]\s*\"${field}\":"; then
    MIRRORED_CHANGED=1
    break
  fi
done

if [[ "$MIRRORED_CHANGED" -eq 0 ]]; then
  echo "✓ check-architect-marketplace-self-check: plugin.json 변경됨, mirrored field 4종 (name/version/description/author) 무변경 — §13 선언 검증 영역 외"
  exit 0
fi

echo "ℹ check-architect-marketplace-self-check: plugin.json mirrored field 변경 감지 — §13 선언 검증 진행"

# ──────────────────────────── Step 2: doc-only fast-path 확인 ─────────────────────────────────
# ADR-054 doc-only fast-path — Change Plan 미산출이 정상인 경로

if echo "$PR_LABELS" | grep -qE "^(phase:문서|fast-path:doc-only)$"; then
  echo "✓ check-architect-marketplace-self-check: doc-only fast-path label 감지 — Change Plan 부재 정상 (ADR-054)"
  exit 0
fi

# ──────────────────────────── Step 3: Change Plan file 탐색 + dogfood-out 분기 ────────────────────

# (A) wrapper-self case: 동일 PR diff 안 change-plans/*.md 탐색
CHANGE_PLAN_IN_DIFF=$(git diff --name-only "$BASE_REF" 2>/dev/null | grep -E "(change-plans|change_plans)/.*\\.md$" | head -1 || true)

# (B) cross-repo dogfood-out case 신호 감지
#     신호 1: PR body 안 "Change Plan: <URL>" link
#     신호 2: PR body 또는 Issue body 안 "dogfood-out:true" marker
DOGFOOD_LINK=$(echo "$PR_BODY" | grep -oE "Change Plan: https://github\.com/[^ ]+" | head -1 || true)
DOGFOOD_MARKER=$(echo "$PR_BODY" | grep -E "^dogfood-out:\s*true" | head -1 || true)

if [[ -z "$CHANGE_PLAN_IN_DIFF" ]]; then
  # Change Plan 이 동일 PR 에 없음 — (A) vs (B) 분기 판정
  if [[ -n "$DOGFOOD_LINK" || -n "$DOGFOOD_MARKER" ]]; then
    # (B) cross-repo dogfood-out case
    echo "⚠ check-architect-marketplace-self-check: cross-repo dogfood-out case 감지"
    echo "   Change Plan 이 외부 repo 에 위치 — manual verify 권고"

    # cross-repo fetch 시도 (CFP-820 패턴 답습)
    if [[ -n "$DOGFOOD_LINK" ]]; then
      # PR body 에서 "Change Plan: https://github.com/OWNER/REPO/blob/BRANCH/path/to/file.md" 형식 파싱
      PLAN_URL=$(echo "$PR_BODY" | grep -oE "Change Plan: https://github\.com/[^ ]+" | sed 's/Change Plan: //' | head -1 || true)
      if [[ -n "$PLAN_URL" && -n "${GH_TOKEN:-}" ]]; then
        # URL 에서 owner/repo + path 추출해 gh api 호출
        PLAN_PATH=$(echo "$PLAN_URL" | sed -E 's|https://github\.com/([^/]+)/([^/]+)/blob/[^/]+/(.+)|\1/\2 \3|' || true)
        PLAN_REPO=$(echo "$PLAN_PATH" | cut -d' ' -f1)
        PLAN_FILE=$(echo "$PLAN_PATH" | cut -d' ' -f2-)
        if [[ -n "$PLAN_REPO" && -n "$PLAN_FILE" ]]; then
          REMOTE_PLAN=$(GH_TOKEN="$GH_TOKEN" gh api -H "Accept: application/vnd.github.raw" \
            "repos/$PLAN_REPO/contents/$PLAN_FILE" 2>/dev/null || echo "")
          if [[ -n "$REMOTE_PLAN" ]]; then
            echo "  cross-repo Change Plan fetch 성공 — §13 block 검증 진행"
            # cross-repo §13 검증 (step 4-5 동형)
            _check_plan_content() {
              local plan_content="$1"
              local sync_req
              sync_req=$(echo "$plan_content" | grep -E "^marketplace_sync_required:" | head -1 | sed 's/marketplace_sync_required:\s*//' | tr -d ' ' || true)
              if [[ -z "$sync_req" ]]; then
                echo "⚠ check-architect-marketplace-self-check: [cross-repo] Change Plan §13 'marketplace_sync_required:' field 부재"
                echo "   ADR-063 §결정 9 Amendment 1 Layer 2 — declare 의무 (false 도 명시 필요)"
                return 1
              fi
              if [[ "$sync_req" == "true" ]]; then
                local changed_fields
                changed_fields=$(echo "$plan_content" | grep -E "^mirrored_fields_changed:" | head -1 || true)
                local trigger_plugins
                trigger_plugins=$(echo "$plan_content" | grep -E "^triggering_plugins:" | head -1 || true)
                local fields_empty=0
                local plugins_empty=0
                echo "$changed_fields" | grep -qE "\[\s*\]" && fields_empty=1
                [[ -z "$changed_fields" ]] && fields_empty=1
                echo "$trigger_plugins" | grep -qE "\[\s*\]" && plugins_empty=1
                [[ -z "$trigger_plugins" ]] && plugins_empty=1
                if [[ "$fields_empty" -eq 1 || "$plugins_empty" -eq 1 ]]; then
                  echo "⚠ check-architect-marketplace-self-check: [cross-repo] marketplace_sync_required: true 이지만 선언 불완전"
                  [[ "$fields_empty"   -eq 1 ]] && echo "   - mirrored_fields_changed[] 가 비어있거나 부재"
                  [[ "$plugins_empty"  -eq 1 ]] && echo "   - triggering_plugins[] 가 비어있거나 부재"
                  return 1
                fi
              fi
              return 0
            }
            if ! _check_plan_content "$REMOTE_PLAN"; then
              exit 1
            fi
            echo "✓ check-architect-marketplace-self-check: cross-repo Change Plan §13 선언 검증 PASS"
            exit 0
          fi
        fi
      fi
    fi
    # cross-repo fetch 불가 / 링크 파싱 실패 시 conditional warning (silent skip 금지)
    echo "  ⚠ cross-repo Change Plan fetch 불가 (GH_TOKEN 미설정 또는 URL 파싱 실패)"
    echo "     manual verify 권고: Change Plan §13 'marketplace_sync_required:' 선언을 직접 확인하세요"
    echo "     ADR-063 §결정 21 (B) cross-repo dogfood-out case"
    exit 1
  else
    # (A) wrapper-self case: Change Plan 부재 → warning
    echo "⚠ check-architect-marketplace-self-check: plugin.json mirrored field 변경 PR 인데 Change Plan §13 선언 부재"
    echo "   발견: .claude-plugin/plugin.json mirrored field 변경"
    echo "   기대: Change Plan §13 'marketplace_sync_required:' 선언 (ADR-063 §결정 9 Amendment 1 Layer 2)"
    echo ""
    echo "   해결:"
    echo "   1. Change Plan §13 에 다음을 추가하세요:"
    echo "      marketplace_sync_required: true   # 또는 false"
    echo "      mirrored_fields_changed: [version, description]   # 변경된 field 목록"
    echo "      triggering_plugins:"
    echo "        - <plugin-name> (<MAJOR|MINOR|PATCH>)"
    echo ""
    echo "   2. doc-only fast-path 시 'phase:문서' 또는 'fast-path:doc-only' label 부착 (ADR-054)"
    echo "   3. 긴급 bypass: hotfix-bypass:architect-marketplace-self-check label (ADR-024 Amendment 3)"
    exit 1
  fi
fi

# ──────────────────────────── Step 4: Change Plan §13 presence 검증 ──────────────────────────────
echo "  Change Plan file: $CHANGE_PLAN_IN_DIFF"
PLAN_CONTENT=$(git show "HEAD:$CHANGE_PLAN_IN_DIFF" 2>/dev/null || cat "$CHANGE_PLAN_IN_DIFF" 2>/dev/null || true)

if [[ -z "$PLAN_CONTENT" ]]; then
  echo "⚠ check-architect-marketplace-self-check: Change Plan 파일 읽기 실패 — manual verify 권고"
  exit 1
fi

SYNC_REQ=$(echo "$PLAN_CONTENT" | grep -E "^marketplace_sync_required:" | head -1 | sed 's/marketplace_sync_required:\s*//' | tr -d ' ' || true)

if [[ -z "$SYNC_REQ" ]]; then
  echo "⚠ check-architect-marketplace-self-check: Change Plan §13 'marketplace_sync_required:' field 부재"
  echo "   Change Plan: $CHANGE_PLAN_IN_DIFF"
  echo "   ADR-063 §결정 9 Amendment 1 Layer 2 — declare 의무 (true 또는 false 명시, silent skip 금지)"
  echo ""
  echo "   해결: Change Plan §13 에 'marketplace_sync_required: true|false' 추가"
  exit 1
fi

echo "  marketplace_sync_required: $SYNC_REQ"

# ──────────────────────────── Step 5: marketplace_sync_required: true 시 completeness 검증 ───────

if [[ "$SYNC_REQ" == "true" ]]; then
  CHANGED_FIELDS=$(echo "$PLAN_CONTENT" | grep -E "^mirrored_fields_changed:" | head -1 || true)
  TRIGGER_PLUGINS=$(echo "$PLAN_CONTENT" | grep -E "^triggering_plugins:" | head -1 || true)

  FIELDS_EMPTY=0
  PLUGINS_EMPTY=0

  echo "$CHANGED_FIELDS" | grep -qE "\[\s*\]" && FIELDS_EMPTY=1
  [[ -z "$CHANGED_FIELDS" ]] && FIELDS_EMPTY=1
  echo "$TRIGGER_PLUGINS" | grep -qE "\[\s*\]" && PLUGINS_EMPTY=1
  [[ -z "$TRIGGER_PLUGINS" ]] && PLUGINS_EMPTY=1

  if [[ "$FIELDS_EMPTY" -eq 1 || "$PLUGINS_EMPTY" -eq 1 ]]; then
    echo "⚠ check-architect-marketplace-self-check: marketplace_sync_required: true 이지만 선언 불완전"
    echo "   Change Plan: $CHANGE_PLAN_IN_DIFF"
    [[ "$FIELDS_EMPTY"   -eq 1 ]] && echo "   - mirrored_fields_changed[] 가 비어있거나 부재 (변경된 field 목록 명시 의무)"
    [[ "$PLUGINS_EMPTY"  -eq 1 ]] && echo "   - triggering_plugins[] 가 비어있거나 부재 (대상 plugin + bump type 명시 의무)"
    echo ""
    echo "   ADR-063 §결정 9 Amendment 1 Layer 2 completeness 조건:"
    echo "     mirrored_fields_changed: [version, description]   # 예시"
    echo "     triggering_plugins:"
    echo "       - codeforge (MINOR)   # 예시"
    exit 1
  fi

  echo "  mirrored_fields_changed: ✓"
  echo "  triggering_plugins: ✓"
fi

# ──────────────────────────── Step 6: PASS ───────────────────────────────────────────────────────
echo ""
echo "✓ check-architect-marketplace-self-check: Change Plan §13 선언 검증 PASS"
echo "  marketplace_sync_required: $SYNC_REQ (ADR-063 §결정 9 Amendment 1 Layer 2 정합)"
exit 0
