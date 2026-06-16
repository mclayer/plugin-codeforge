#!/usr/bin/env bash
# scripts/test-check-marketplace-cadence-lag.sh — CFP-2310 S3 (#2313) companion self-test
#
# Arc B 발행 cadence lag detect 테스트 harness. scripts/check-marketplace-cadence-lag.sh
# (production script) 의 lag 판정·Issue 생성·dedup signature 로직을 discriminating fixture
# (RED→GREEN proof) 로 검증한다. ADR-037 Amendment 2 §결정 A2-5 (TestContractArch) 렌즈 이행:
#
#   (a) GREEN (in-sync)      — 합성 marketplace = repo version 전부 일치 → 0 lag, Issue 금지
#   (b) RED (main-ahead)      — 1 plugin marketplace 낮춤 → lag 감지, Issue dry-run 발동
#   (c) RED (marketplace-missing) — 1 plugin 제거 → lag 감지, direction=marketplace-missing
#   (d) DEDUP (signature)     — version-제외 안정성: 같은 plugin+direction, 다른 version
#                              → 동일 signature (dedup 무력화 방지)
#
# 각 case 마다:
#   - marketplace.json 런타임 합성 (repo 버전 기준 → case별 조작)
#   - production script 호출 (MLD_SKIP_ISSUE_CREATE=1 + --marketplace-json override)
#   - stdout 마커 assert (expected-verdict / expected-marker / forbid-marker)
#
# Exit codes:
#   0 = 모든 case verdict + 마커 일치 (RED→GREEN proof + isolation 성립)
#   1 = 1+ case verdict 또는 마커 불일치 (proof / isolation 깨짐)
#   2 = production script 부재 (fail-loud)

set -uo pipefail

# Windows cp949 회피 — UTF-8 강제
export LC_ALL="${LC_ALL:-C.UTF-8}" 2>/dev/null || true

REPO_ROOT="${1:-$(pwd)}"
GATE="$REPO_ROOT/scripts/check-marketplace-cadence-lag.sh"
TEMP_MP_DIR="/tmp/codeforge-cadence-test-$$"

# ── fail-loud 환경 점검 ──
if [ ! -f "$GATE" ]; then
    echo "[cadence-test] ERROR: production script 부재: $GATE" >&2
    exit 2
fi

# ── 임시 디렉터리 정리 trap ──
trap "rm -rf '$TEMP_MP_DIR'" EXIT

mkdir -p "$TEMP_MP_DIR"

# ── 헬퍼: jq 로 marketplace.json 안전하게 생성 ──
_synthesize_marketplace_json() {
    local case_type="$1"
    local case_plugin="${2:-}"
    local case_alt_version="${3:-}"

    # roster 읽기 + 임시 파일로 저장 (bash 내 로직만 사용)
    bash "$GATE" roster --repo-root "$REPO_ROOT" 2>/dev/null > "$TEMP_MP_DIR/.roster-tmp"

    # jq 로 marketplace.json 구성 (plugin 제외/버전 조작 로직은 jq 내부)
    jq -nR \
        --arg case_type "$case_type" \
        --arg case_plugin "$case_plugin" \
        --arg case_alt_version "$case_alt_version" \
        '{plugins: [inputs | split("\t") |
           if .[0] != "" then
             {name: .[0], version:
               if $case_type == "main-ahead" and .[0] == $case_plugin then $case_alt_version
               elif $case_type == "marketplace-missing" and .[0] == $case_plugin then null
               else .[1] end}
           else empty end |
           select(.version != null)]}' \
        < "$TEMP_MP_DIR/.roster-tmp"
}

# ── test case loop ──
PASS_COUNT=0
FAIL_COUNT=0

# Case 1: green-in-sync-no-lag
echo "[cadence-test] Running: green-in-sync-no-lag"
{
    _synthesize_marketplace_json "in-sync" "" "" > "$TEMP_MP_DIR/case1-marketplace.json"

    out_1="$(MLD_SKIP_ISSUE_CREATE=1 bash "$GATE" check --repo-root "$REPO_ROOT" --marketplace-json "$TEMP_MP_DIR/case1-marketplace.json" 2>&1)"

    fail_msg=""
    if ! printf '%s\n' "$out_1" | grep -qE "PASS - 0 lag"; then
        fail_msg="expected 'PASS - 0 lag' marker"
    fi
    # forbid: LAG detected / would create issue 절대 금지
    if printf '%s\n' "$out_1" | grep -qE "LAG detected"; then
        fail_msg="${fail_msg:+$fail_msg; }forbid: LAG should not be detected in in-sync"
    fi
    if printf '%s\n' "$out_1" | grep -qE "would create issue"; then
        fail_msg="${fail_msg:+$fail_msg; }forbid: should not create issue in in-sync"
    fi

    if [ -z "$fail_msg" ]; then
        echo "  ✓ PASS"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "  ✗ FAIL: $fail_msg" >&2
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

# Case 2: red-main-ahead-creates-issue
echo "[cadence-test] Running: red-main-ahead-creates-issue"
{
    _synthesize_marketplace_json "main-ahead" "codeforge" "6.24.0" > "$TEMP_MP_DIR/case2-marketplace.json"

    out_2="$(MLD_SKIP_ISSUE_CREATE=1 bash "$GATE" check --repo-root "$REPO_ROOT" --marketplace-json "$TEMP_MP_DIR/case2-marketplace.json" 2>&1)"

    fail_msg=""
    if ! printf '%s\n' "$out_2" | grep -qE "::warning::.*LAG detected"; then
        fail_msg="expected '::warning::.*LAG detected' marker"
    fi
    if ! printf '%s\n' "$out_2" | grep -qE "direction=main-ahead"; then
        fail_msg="${fail_msg:+$fail_msg; }expected 'direction=main-ahead'"
    fi
    if ! printf '%s\n' "$out_2" | grep -qE "\\[DRY-RUN\\] would create issue"; then
        fail_msg="${fail_msg:+$fail_msg; }expected dry-run issue create"
    fi

    if [ -z "$fail_msg" ]; then
        echo "  ✓ PASS"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "  ✗ FAIL: $fail_msg" >&2
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

# Case 3: red-marketplace-missing
echo "[cadence-test] Running: red-marketplace-missing"
{
    _synthesize_marketplace_json "marketplace-missing" "codeforge-pmo" "" > "$TEMP_MP_DIR/case3-marketplace.json"

    out_3="$(MLD_SKIP_ISSUE_CREATE=1 bash "$GATE" check --repo-root "$REPO_ROOT" --marketplace-json "$TEMP_MP_DIR/case3-marketplace.json" 2>&1)"

    fail_msg=""
    if ! printf '%s\n' "$out_3" | grep -qE "::warning::.*LAG detected"; then
        fail_msg="expected '::warning::.*LAG detected' marker"
    fi
    if ! printf '%s\n' "$out_3" | grep -qE "direction=marketplace-missing"; then
        fail_msg="${fail_msg:+$fail_msg; }expected 'direction=marketplace-missing'"
    fi

    if [ -z "$fail_msg" ]; then
        echo "  ✓ PASS"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "  ✗ FAIL: $fail_msg" >&2
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

# Case 4: dedup-stable-signature (version-제외 안정성)
# D4 함정 회피: signature 가 version 값과 무관하게 안정되는지 검증
# 같은 plugin+direction, 다른 marketplace version → 동일 signature 기대
echo "[cadence-test] Running: dedup-stable-signature"
{
    _synthesize_marketplace_json "main-ahead" "codeforge" "6.24.0" > "$TEMP_MP_DIR/case4a-marketplace.json"
    _synthesize_marketplace_json "main-ahead" "codeforge" "6.23.0" > "$TEMP_MP_DIR/case4b-marketplace.json"

    # 두 평가 출력에서 signature 추출
    out_4a="$(MLD_SKIP_ISSUE_CREATE=1 bash "$GATE" check --repo-root "$REPO_ROOT" --marketplace-json "$TEMP_MP_DIR/case4a-marketplace.json" 2>&1)"
    out_4b="$(MLD_SKIP_ISSUE_CREATE=1 bash "$GATE" check --repo-root "$REPO_ROOT" --marketplace-json "$TEMP_MP_DIR/case4b-marketplace.json" 2>&1)"

    # mp-lag-sig=<16char hex> 추출
    sig_4a="$(printf '%s\n' "$out_4a" | grep -oE 'mp-lag-sig=[0-9a-f]{16}' | head -1 | cut -d= -f2)"
    sig_4b="$(printf '%s\n' "$out_4b" | grep -oE 'mp-lag-sig=[0-9a-f]{16}' | head -1 | cut -d= -f2)"

    # D4 보조 assert: production signature subcommand 직접 비교 (version-독립 검증)
    sig_direct="$(bash "$GATE" signature --plugin codeforge --direction main-ahead 2>/dev/null)"

    fail_msg=""
    if [ -z "$sig_4a" ] || [ -z "$sig_4b" ]; then
        fail_msg="signature extraction failed (sig_4a='$sig_4a', sig_4b='$sig_4b')"
    elif [ "$sig_4a" != "$sig_4b" ]; then
        fail_msg="signature mismatch: $sig_4a != $sig_4b (version should not affect sig — D4 violation)"
    elif [ -n "$sig_direct" ] && [ "$sig_4a" != "$sig_direct" ]; then
        fail_msg="signature mismatch vs production subcommand: $sig_4a != $sig_direct (isolation check)"
    fi

    if [ -z "$fail_msg" ]; then
        echo "  ✓ PASS (signature=$sig_4a stable across version changes)"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "  ✗ FAIL: $fail_msg" >&2
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

echo ""
echo "[cadence-test] Summary: $PASS_COUNT pass, $FAIL_COUNT fail"

if [ "$PASS_COUNT" -eq 0 ] && [ "$FAIL_COUNT" -eq 0 ]; then
    echo "[cadence-test] ERROR: 평가된 case 0개" >&2
    exit 2
fi

if [ "$FAIL_COUNT" -gt 0 ]; then
    exit 1
fi
exit 0
