#!/usr/bin/env bash
# CFP-407 / ADR-062 — check-carrier-bootstrap.sh unit tests
#
# 3 fixture cases (ADR-062 §결정 2 + §결정 8 self-application):
#   case 1: carrier present + §3 protocol reference 정합 → PASS
#   case 2: carrier_story 선언 + bootstrap_exempt_protocols 누락 → FAIL
#   case 3: 미정의 type prefix (예: agent:) → FAIL
#
# 추가 보조 case (안전망):
#   case 4: non-carrier Story (frontmatter 미선언) → PASS (면제)
#   case 5: malformed typed key (예: "ADR-062" prefix 없음) → FAIL

set -euo pipefail
cd "$(dirname "$0")/.."

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

FIXTURE_DIR="$TMPDIR/docs/stories"
mkdir -p "$FIXTURE_DIR"

REPO_ROOT="$(pwd)"
LINT="bash ${REPO_ROOT}/scripts/check-carrier-bootstrap.sh"

PASS_COUNT=0
FAIL_COUNT=0

assert_lint_pass() {
    local fixture="$1"
    local desc="$2"
    if (cd "$TMPDIR" && $LINT "$fixture" > /dev/null 2>&1); then
        echo "✓ PASS: $desc"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "✗ FAIL: $desc (expected PASS, got FAIL)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

assert_lint_fail() {
    local fixture="$1"
    local desc="$2"
    if (cd "$TMPDIR" && $LINT "$fixture" > /dev/null 2>&1); then
        echo "✗ FAIL: $desc (expected FAIL, got PASS)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    else
        echo "✓ PASS: $desc"
        PASS_COUNT=$((PASS_COUNT + 1))
    fi
}

# ─── case 1: carrier present + §3 protocol reference 정합 → PASS ───
cat > "$FIXTURE_DIR/CFP-407.md" <<'EOF'
---
key: CFP-407
title: carrier Story bootstrap dependency 룰
status: phase:설계
type: story
date: 2026-05-12
github_issue: mclayer/plugin-codeforge#407
carrier_story: CFP-407
bootstrap_exempt_protocols:
  - "adr:ADR-062"
---

# CFP-407: carrier Story bootstrap

## §1. 사용자 요구사항
ditto

## §3. 관련 ADR

### 3.1 직접 제약
- ADR-062 (본 Story 가 carrier — self-application 첫 사례)
- ADR-058 (구현 패턴 template)

## §4.0. 관련 코드 경로 목록
ditto
EOF

assert_lint_pass "docs/stories/CFP-407.md" "case 1: carrier present + §3 'ADR-062' 참조 → PASS"

# ─── case 2: carrier_story 선언 + bootstrap_exempt_protocols 누락 → FAIL ───
cat > "$FIXTURE_DIR/CFP-998.md" <<'EOF'
---
key: CFP-998
title: missing bootstrap_exempt_protocols
status: phase:설계
type: story
date: 2026-05-12
github_issue: mclayer/plugin-codeforge#998
carrier_story: CFP-998
---

# CFP-998

## §1. 사용자 요구사항
ditto
EOF

assert_lint_fail "docs/stories/CFP-998.md" "case 2: carrier_story 선언 + exempt_protocols 누락 → FAIL"

# ─── case 3: 미정의 type prefix → FAIL ───
cat > "$FIXTURE_DIR/CFP-997.md" <<'EOF'
---
key: CFP-997
title: invalid type prefix
status: phase:설계
type: story
date: 2026-05-12
github_issue: mclayer/plugin-codeforge#997
carrier_story: CFP-997
bootstrap_exempt_protocols:
  - "agent:DeveloperAgent"
---

# CFP-997

## §1. 사용자 요구사항
ditto

## §3. 관련 ADR
test
EOF

assert_lint_fail "docs/stories/CFP-997.md" "case 3: 미정의 type prefix 'agent:' → FAIL"

# ─── case 4: non-carrier Story (frontmatter 미선언) → PASS (면제) ───
cat > "$FIXTURE_DIR/CFP-996.md" <<'EOF'
---
key: CFP-996
title: non-carrier story
status: phase:설계
type: story
date: 2026-05-12
github_issue: mclayer/plugin-codeforge#996
---

# CFP-996

## §1. 사용자 요구사항
ditto
EOF

assert_lint_pass "docs/stories/CFP-996.md" "case 4: non-carrier (frontmatter 미선언) → PASS"

# ─── case 5: malformed typed key (prefix 없음) → FAIL ───
cat > "$FIXTURE_DIR/CFP-995.md" <<'EOF'
---
key: CFP-995
title: malformed typed key
status: phase:설계
type: story
date: 2026-05-12
github_issue: mclayer/plugin-codeforge#995
carrier_story: CFP-995
bootstrap_exempt_protocols:
  - "ADR-062"
---

# CFP-995

## §1. 사용자 요구사항
ditto

## §3. 관련 ADR
test
EOF

assert_lint_fail "docs/stories/CFP-995.md" "case 5: malformed typed key 'ADR-062' (prefix 없음) → FAIL"

# ─── 추가 case 6: §3 본문에 carrier protocol 참조 부재 → FAIL ───
cat > "$FIXTURE_DIR/CFP-994.md" <<'EOF'
---
key: CFP-994
title: §3 reference missing
status: phase:설계
type: story
date: 2026-05-12
github_issue: mclayer/plugin-codeforge#994
carrier_story: CFP-994
bootstrap_exempt_protocols:
  - "adr:ADR-062"
---

# CFP-994

## §1. 사용자 요구사항
ditto

## §3. 관련 ADR
무관한 ADR 만 언급
EOF

assert_lint_fail "docs/stories/CFP-994.md" "case 6: §3 본문 carrier protocol 참조 부재 → FAIL"

echo ""
echo "─── Test Summary ───"
echo "Passed: $PASS_COUNT"
echo "Failed: $FAIL_COUNT"

if [ $FAIL_COUNT -gt 0 ]; then
    exit 1
fi
exit 0
