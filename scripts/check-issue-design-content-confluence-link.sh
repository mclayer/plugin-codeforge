#!/usr/bin/env bash
# check-issue-design-content-confluence-link.sh — Issue / PR body 안 design content 인용 시 Confluence anchor link 동반 의무 lint
#
# Carrier: CFP-1421 (Sub-A S1.3 of EPIC #1415 Mega-Epic)
# Owner ADR: ADR-111 §결정 5 (cross-link discipline — git anchor + Confluence anchor 양쪽 link 의무)
# Wire layer: ADR-082 §결정 6 retain pattern 답습 (Wave 1 declare → Wave 2 wire = 본 script)
# Tier: warning (ADR-060 §결정 5 — 첫 도입 = warning mode)
# Bypass label: hotfix-bypass:issue-design-content-confluence-link (label-registry-v2 79번째 family member)
#
# Scope: Issue / PR body 안 design doc 4 closed-enum 인용 (ADR-111 §결정 1) detect →
#        각 인용 부근에 Confluence anchor link (mclayer.atlassian.net) 또는 git anchor presence verify.
#
# Closed-enum 4 mirror 대상 detection regex:
#   - ADR:               `ADR-\d{3}`
#   - Living Arch:       `docs/architecture/`
#   - Change Plan:       `docs/change-plans/`
#   - Domain Knowledge:  `docs/domain-knowledge/`
#
# Confluence anchor presence regex: `(mclayer\.)?atlassian\.net/wiki/spaces/`
# Git anchor (fallback) presence regex: `docs/(adr|architecture|change-plans|domain-knowledge)/[A-Za-z0-9_\-/]+\.md`
#
# Output:
#   exit 0 — PASS or warning (warning-tier semantics)
#   exit 2 — argv error / missing prereq
#   exit 3 — file/issue fetch error
#
# Usage:
#   bash scripts/check-issue-design-content-confluence-link.sh --issue 1421
#   bash scripts/check-issue-design-content-confluence-link.sh --pr 1500
#   bash scripts/check-issue-design-content-confluence-link.sh --file /path/to/body.md
#
# Bypass:
#   - `hotfix-bypass:issue-design-content-confluence-link` label 부착 시 skip (warning 발화 안 함)
#
# ADR-061 정합: bash 본문 짧음 (single-pass grep heuristic), Python heredoc 미사용.
# ADR-068 I-3 정합: bypass label 부재 시 unconditional warning (조건 분기 0).
# ADR-082 §결정 1 layer 1-C 정합: USER-UTTERANCE-VERBATIM 평문 leak surface 신설 0 (Issue body fetch 만, write 0).

set -u

# 색상 (terminal only)
if [ -t 2 ]; then
    YELLOW='\033[1;33m'
    GREEN='\033[1;32m'
    NC='\033[0m'
else
    YELLOW=''
    GREEN=''
    NC=''
fi

# ─── Argument parse ───────────────────────────────────────────────────────────
MODE=""
TARGET=""
BYPASS_LABEL="hotfix-bypass:issue-design-content-confluence-link"

while [ $# -gt 0 ]; do
    case "$1" in
        --issue)
            MODE="issue"
            TARGET="${2:-}"
            shift 2
            ;;
        --pr)
            MODE="pr"
            TARGET="${2:-}"
            shift 2
            ;;
        --file)
            MODE="file"
            TARGET="${2:-}"
            shift 2
            ;;
        --help|-h)
            sed -n '1,40p' "$0"
            exit 0
            ;;
        *)
            echo "ERROR: unknown arg '$1' (expected --issue N | --pr N | --file PATH)" >&2
            exit 2
            ;;
    esac
done

if [ -z "$MODE" ] || [ -z "$TARGET" ]; then
    echo "ERROR: --issue N | --pr N | --file PATH required" >&2
    exit 2
fi

# ─── Prereq: gh CLI (--issue / --pr 모드만) ───────────────────────────────────
if [ "$MODE" != "file" ]; then
    if ! command -v gh >/dev/null 2>&1; then
        echo "ERROR: gh CLI 미설치 (--issue / --pr 모드 필수)" >&2
        exit 3
    fi
fi

# ─── Body + label fetch ───────────────────────────────────────────────────────
BODY=""
LABELS=""

case "$MODE" in
    issue)
        if ! BODY=$(gh issue view "$TARGET" --json body --jq '.body' 2>&1); then
            echo "ERROR: Issue #$TARGET fetch 실패 — $BODY" >&2
            exit 3
        fi
        LABELS=$(gh issue view "$TARGET" --json labels --jq '[.labels[].name] | join(",")' 2>&1 || echo "")
        ;;
    pr)
        if ! BODY=$(gh pr view "$TARGET" --json body --jq '.body' 2>&1); then
            echo "ERROR: PR #$TARGET fetch 실패 — $BODY" >&2
            exit 3
        fi
        LABELS=$(gh pr view "$TARGET" --json labels --jq '[.labels[].name] | join(",")' 2>&1 || echo "")
        ;;
    file)
        if [ ! -f "$TARGET" ]; then
            echo "ERROR: file '$TARGET' 부재" >&2
            exit 3
        fi
        BODY=$(cat "$TARGET")
        LABELS=""
        ;;
esac

# ─── Bypass label check ───────────────────────────────────────────────────────
if echo "$LABELS" | grep -q "$BYPASS_LABEL"; then
    echo -e "${GREEN}[PASS]${NC} bypass label '$BYPASS_LABEL' 부착 — skip (warning 발화 안 함)" >&2
    exit 0
fi

# ─── Design content reference detection (ADR-111 §결정 1 closed-enum 4) ──────
# 인용 패턴: ADR-NNN / docs/architecture/* / docs/change-plans/* / docs/domain-knowledge/*
REFERENCE_REGEX='(ADR-[0-9]{3}|docs/architecture/|docs/change-plans/|docs/domain-knowledge/)'

# Confluence anchor presence
CONFLUENCE_REGEX='atlassian\.net/wiki/spaces/'

# Git anchor (fallback acceptable per ADR-111 §결정 5 — "양쪽 link" 영역)
GIT_ANCHOR_REGEX='docs/(adr|architecture|change-plans|domain-knowledge)/[A-Za-z0-9_./-]+\.md'

# Count references
REF_COUNT=$(echo "$BODY" | grep -oE "$REFERENCE_REGEX" | sort -u | wc -l | tr -d ' ')

if [ "$REF_COUNT" = "0" ]; then
    echo -e "${GREEN}[PASS]${NC} design content 인용 0건 — lint 영역 외" >&2
    exit 0
fi

# Check Confluence anchor presence
CONF_HITS=$(echo "$BODY" | grep -oE "$CONFLUENCE_REGEX" | wc -l | tr -d ' ')
GIT_HITS=$(echo "$BODY" | grep -oE "$GIT_ANCHOR_REGEX" | wc -l | tr -d ' ')

# 의무: design content 인용 시 confluence anchor OR git anchor 둘 다 grep-presence
# ADR-111 §결정 5 — "양쪽 link" — 한쪽만 있으면 warning (이상적: 양쪽 동시)
if [ "$CONF_HITS" -gt 0 ] && [ "$GIT_HITS" -gt 0 ]; then
    echo -e "${GREEN}[PASS]${NC} design content 인용 ${REF_COUNT}건 — Confluence anchor ${CONF_HITS}건 + git anchor ${GIT_HITS}건 (양 channel 가시화 충족)" >&2
    exit 0
fi

# Warning emission
echo -e "${YELLOW}[WARNING]${NC} design content 인용 ${REF_COUNT}건 발견 — cross-link discipline 미충족" >&2
echo "  - Confluence anchor (atlassian.net/wiki/spaces/...): ${CONF_HITS}건" >&2
echo "  - Git anchor (docs/{adr,architecture,change-plans,domain-knowledge}/*.md): ${GIT_HITS}건" >&2
echo "" >&2
echo "  ADR-111 §결정 5 — design content 인용 시 양 channel (Confluence + git) 동시 link 의무 (cross-link discipline)" >&2
echo "  Bypass: '$BYPASS_LABEL' label 부착 시 skip" >&2
echo "  Wave 1 declaration-only — warning-tier (exit 0)" >&2

# Detected references (debug 영역)
echo "" >&2
echo "  Detected design content references:" >&2
echo "$BODY" | grep -oE "$REFERENCE_REGEX" | sort -u | sed 's/^/    - /' >&2

# warning tier — exit 0 (ADR-060 §결정 5 첫 도입 mode)
exit 0
