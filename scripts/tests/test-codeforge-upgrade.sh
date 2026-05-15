#!/usr/bin/env bash
# test-codeforge-upgrade.sh — CFP-743 §8 Test Contract impl
# CLI argument parser 단위 테스트 (Change Plan §8.1 / §8.2)
#
# 커버리지:
#   AC-1: user_decision_branches: 0 (no prompt)
#   AC-2: --dry-run mode 출력
#   AC-3: --apply mode 출력
#   AC-4: --rollback <version> mode 출력
#   §8.2 경계: unknown arg reject / missing --rollback version / 추가 인자 거부
#   §7.1 trust boundary: enum whitelist reject

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CLI="${REPO_ROOT}/scripts/codeforge-upgrade.sh"

PASS=0
FAIL=0
# Note: arithmetic with ((var++)) returns exit 1 when result is 0 in bash.
# Use PASS=$((PASS+1)) pattern to avoid false exit under set -e sub-shells.

_assert_exit() {
    local tc_name="${1}"
    local expected_exit="${2}"
    shift 2
    local actual_exit=0
    "$@" >/dev/null 2>&1 || actual_exit=$?
    if [[ "${actual_exit}" -eq "${expected_exit}" ]]; then
        echo "PASS [${tc_name}]"
        PASS=$((PASS+1))
    else
        echo "FAIL [${tc_name}] expected exit=${expected_exit} got exit=${actual_exit}"
        FAIL=$((FAIL+1))
    fi
}

_assert_output_contains() {
    local tc_name="${1}"
    local needle="${2}"
    shift 2
    local output
    output=$("$@" 2>&1) || true
    if echo "${output}" | grep -qF "${needle}"; then
        echo "PASS [${tc_name}]"
        PASS=$((PASS+1))
    else
        echo "FAIL [${tc_name}] expected '${needle}' in output"
        echo "  actual output: ${output}"
        FAIL=$((FAIL+1))
    fi
}

echo "=== codeforge-upgrade.sh CLI 단위 테스트 ==="

# TC-1: --dry-run → exit 0, mode=dry_run 출력 (AC-2)
_assert_exit "TC-1a: --dry-run exit 0" 0 bash "${CLI}" --dry-run
_assert_output_contains "TC-1b: --dry-run mode 출력" "mode: dry_run" bash "${CLI}" --dry-run

# TC-2: --apply → exit 0, mode=transaction 출력 (AC-3)
_assert_exit "TC-2a: --apply exit 0" 0 bash "${CLI}" --apply
_assert_output_contains "TC-2b: --apply mode 출력" "mode: transaction" bash "${CLI}" --apply

# TC-3: --rollback <version> → exit 0, mode=snapshot_restore + version 출력 (AC-4)
_assert_exit "TC-3a: --rollback exit 0" 0 bash "${CLI}" --rollback 5.74.0
_assert_output_contains "TC-3b: --rollback mode 출력" "mode: snapshot_restore" bash "${CLI}" --rollback 5.74.0
_assert_output_contains "TC-3c: --rollback version 출력" "rollback_version: 5.74.0" bash "${CLI}" --rollback 5.74.0

# TC-4: --rollback 인자 없음 → exit 1 (§8.2 경계)
_assert_exit "TC-4: --rollback version 미제공 exit 1" 1 bash "${CLI}" --rollback

# TC-5: unknown arg → exit 1, enum whitelist reject (§7.1 / §8.2)
_assert_exit "TC-5a: unknown arg exit 1" 1 bash "${CLI}" --unknown-arg
_assert_output_contains "TC-5b: unknown arg error 메시지" "enum whitelist reject" bash "${CLI}" --unknown-arg 2>&1 || true

# TC-6: 인자 없음 → exit 1 (§8.2 경계)
_assert_exit "TC-6: 인자 없음 exit 1" 1 bash "${CLI}"

# TC-7: --apply 뒤 추가 인자 → exit 1 (free-text injection 차단, §7.1)
_assert_exit "TC-7: 추가 인자 거부 exit 1" 1 bash "${CLI}" --apply extra_arg

# TC-8: --help → exit 0 (사용법 출력)
_assert_exit "TC-8: --help exit 0" 0 bash "${CLI}" --help

# TC-9: thin dispatcher — check-codeforge-version-drift.sh 직접 실행 금지 확인 (§4.4)
# CLI 가 drift check script 를 exec/source 로 실행하지 않음을 확인.
# 주의: CLI 출력 메시지에 script 이름이 언급("주의: ...")되는 것은 정상 — 실행 흔적 패턴만 검사.
# 실행 흔적 패턴: "MAJOR drift detected" / "Version drift found" 등 drift 스크립트 stdout
TC9_OUTPUT="$(bash "${CLI}" --dry-run 2>&1)"
if echo "${TC9_OUTPUT}" | grep -qE "drift (detected|found|check:)"; then
    echo "FAIL [TC-9: thin dispatcher] CLI 가 drift check script 를 직접 실행함 (§4.4 위반)"
    FAIL=$((FAIL+1))
else
    echo "PASS [TC-9: thin dispatcher — drift-check script 직접 실행 없음 (§4.4)]"
    PASS=$((PASS+1))
fi

# TC-10: user_decision_branches=0 — 출력에 prompt/interactive 패턴 없음 (AC-1)
TC10_OUTPUT="$(bash "${CLI}" --apply 2>&1)"
if echo "${TC10_OUTPUT}" | grep -qiE "(enter|press|confirm|y/n|yes/no)\?"; then
    echo "FAIL [TC-10: no prompt] 사용자 prompt 패턴 감지됨 (user_decision_branches: 0 위반)"
    FAIL=$((FAIL+1))
else
    echo "PASS [TC-10: no prompt — user_decision_branches: 0]"
    PASS=$((PASS+1))
fi

# TC-11: UpgradeAgent spawn 위임 출력 확인 (§3.1 thin dispatcher 증명)
_assert_output_contains "TC-11: UpgradeAgent spawn 위임 출력" "UpgradeAgent" bash "${CLI}" --apply

# TC-12: reconcile_protocol_version: 1.2 출력 확인 (계약 정합)
_assert_output_contains "TC-12: reconcile_protocol_version 출력" "reconcile_protocol_version: 1.2" bash "${CLI}" --apply

echo ""
echo "=== 결과 ==="
echo "PASS: ${PASS}"
echo "FAIL: ${FAIL}"
echo "TOTAL: $((PASS + FAIL))"
if [[ "${FAIL}" -gt 0 ]]; then
    exit 1
else
    exit 0
fi
