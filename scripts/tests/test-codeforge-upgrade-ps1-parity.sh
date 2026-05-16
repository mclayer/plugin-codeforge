#!/usr/bin/env bash
# test-codeforge-upgrade-ps1-parity.sh — CFP-744 §8 cross-platform parity test
#
# Change Plan §3.7.2-parser ps1 parity binding (AC-11):
#   codeforge-upgrade.ps1 도 동일 7-invariant parser refactor
#   (sh↔ps1 byte-level behavior parity — reconcile-protocol-v1 §4.5 parity_invariant).
#   7항목 매트릭스 검증.
#
# strict-verify-gate: RAW verbatim 출력.
# PowerShell 5.1 (powershell.exe) 사용 — pwsh 부재 시 powershell.exe fallback.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PS1="${REPO_ROOT}/scripts/codeforge-upgrade.ps1"

# PowerShell 실행기 탐색
PWSH_BIN=""
if command -v pwsh >/dev/null 2>&1; then
    PWSH_BIN="pwsh"
elif command -v powershell.exe >/dev/null 2>&1; then
    PWSH_BIN="powershell.exe"
elif command -v powershell >/dev/null 2>&1; then
    PWSH_BIN="powershell"
fi

PASS=0
FAIL=0

if [[ -z "${PWSH_BIN}" ]]; then
    echo "SKIP: PowerShell 실행기 부재 (pwsh/powershell.exe/powershell 미발견)"
    echo "ps1 parity test = SKIPPED (CI Linux runner = pwsh 설치 필요, 본 env Windows powershell.exe 사용)"
    exit 0
fi

# Windows path 변환 (MSYS → Windows)
_winpath() {
    if command -v cygpath >/dev/null 2>&1; then
        cygpath -w "${1}"
    else
        echo "${1}"
    fi
}
PS1_WIN="$(_winpath "${PS1}")"

_run_ps1() {
    # ps1 실행 — stdout+stderr 합쳐 반환, exit code 별도
    "${PWSH_BIN}" -NoProfile -ExecutionPolicy Bypass -File "${PS1_WIN}" "$@" 2>&1
}
_ps1_exit() {
    "${PWSH_BIN}" -NoProfile -ExecutionPolicy Bypass -File "${PS1_WIN}" "$@" >/dev/null 2>&1
    echo $?
}

_assert_ps1_exit() {
    local tc="${1}"; local expected="${2}"; shift 2
    local actual
    actual="$(_ps1_exit "$@")"
    if [[ "${actual}" -eq "${expected}" ]]; then
        echo "PASS [${tc}]"; PASS=$((PASS+1))
    else
        echo "FAIL [${tc}] expected exit=${expected} got=${actual}"; FAIL=$((FAIL+1))
    fi
}

_assert_ps1_contains() {
    local tc="${1}"; local needle="${2}"; shift 2
    local out
    out="$(_run_ps1 "$@")"
    if printf '%s' "${out}" | grep -qF -- "${needle}"; then
        echo "PASS [${tc}]"; PASS=$((PASS+1))
    else
        echo "FAIL [${tc}] expected '${needle}' in output"
        echo "  actual: ${out}"; FAIL=$((FAIL+1))
    fi
}

TMP_REPO="$(mktemp -d)"; git -C "${TMP_REPO}" init -q >/dev/null 2>&1
TMP_NONGIT="$(mktemp -d)"
trap 'rm -rf "${TMP_REPO}" "${TMP_NONGIT}"' EXIT
TMP_REPO_WIN="$(_winpath "${TMP_REPO}")"
TMP_NONGIT_WIN="$(_winpath "${TMP_NONGIT}")"

echo "=== codeforge-upgrade.ps1 7-invariant parser refactor parity (${PWSH_BIN}) ==="

# (a) 기존 mode invocation byte-identical
_assert_ps1_exit "PS-a1: --dry-run exit 0" 0 --dry-run
_assert_ps1_contains "PS-a2: --dry-run mode=dry_run" "mode: dry_run" --dry-run
_assert_ps1_exit "PS-a3: --apply exit 0" 0 --apply
_assert_ps1_contains "PS-a4: --apply mode=transaction" "mode: transaction" --apply
_assert_ps1_exit "PS-a5: --rollback <ver> exit 0" 0 --rollback 5.74.0
_assert_ps1_contains "PS-a6: --rollback mode=snapshot_restore" "mode: snapshot_restore" --rollback 5.74.0
_assert_ps1_contains "PS-a7: --rollback version 출력" "rollback_version: 5.74.0" --rollback 5.74.0
_assert_ps1_exit "PS-a8: --rollback 미제공 exit 1" 1 --rollback
_assert_ps1_exit "PS-a9: 인자 없음 exit 1" 1
_assert_ps1_exit "PS-a10: --help exit 0" 0 --help

# (b) --repo orthogonal (mode 순서 무관)
_assert_ps1_exit "PS-b1: --apply --repo <git> exit 0" 0 --apply --repo "${TMP_REPO_WIN}"
_assert_ps1_exit "PS-b2: --repo <git> --apply 순서 역전 exit 0" 0 --repo "${TMP_REPO_WIN}" --apply
_assert_ps1_contains "PS-b3: --apply --repo mode 보존" "mode: transaction" --apply --repo "${TMP_REPO_WIN}"

# (c) --rollback value-taking 보존 (--repo 공존)
_assert_ps1_contains "PS-c1: --repo --rollback value" "rollback_version: 5.73.0" --repo "${TMP_REPO_WIN}" --rollback 5.73.0

# (d) mode 정확히 1개 강제
_assert_ps1_exit "PS-d1: mode 0개 (--repo only) exit 1" 1 --repo "${TMP_REPO_WIN}"
_assert_ps1_exit "PS-d2: mode 2개 충돌 exit 1" 1 --apply --dry-run

# (e) unknown arg enum whitelist reject
#   Note: Windows console (cp949) 가 한글 stderr 를 mangle 함 — ASCII-stable marker 로 검증
#   (PS-e1 exit 1 + ASCII whitelist 안내 출력 = reject 동작 입증).
_assert_ps1_exit "PS-e1: unknown arg exit 1" 1 --bogus-flag
_assert_ps1_contains "PS-e2: unknown arg whitelist 안내 (ASCII)" "--apply" --bogus-flag
_assert_ps1_exit "PS-e3: --repo value 누락 exit 1" 1 --apply --repo

# (f) downstream pipeline 무변경 (canonical/input_repo_root 출력 보존)
_assert_ps1_contains "PS-f1: canonical_repo_root 출력 보존" "canonical_repo_root:" --apply
_assert_ps1_contains "PS-f2: input_repo_root 출력 보존" "input_repo_root:" --apply

# (g) fallback byte-identical + env override
_assert_ps1_contains "PS-g1: fallback canonical = REPO_ROOT 부모" "$(basename "${REPO_ROOT}")" --apply

# §7.4.1 (i) --repo wrong-target abort
_assert_ps1_exit "PS-i1: --repo non-existent abort" 2 --apply --repo "C:\\nonexistent\\xyz999"
_assert_ps1_exit "PS-i2: --repo non-git dir abort" 2 --apply --repo "${TMP_NONGIT_WIN}"
# ASCII-stable marker (한글은 cp949 console mangle 됨 — repo_target_failure tag 는 ASCII)
_assert_ps1_contains "PS-i3: wrong-target marker (ASCII)" "repo_target_failure" --apply --repo "${TMP_NONGIT_WIN}"

echo ""
echo "=== 결과 (ps1 7-invariant parity) ==="
echo "PASS: ${PASS}"
echo "FAIL: ${FAIL}"
echo "TOTAL: $((PASS + FAIL))"
[[ "${FAIL}" -gt 0 ]] && exit 1 || exit 0
