#!/usr/bin/env bash
# test-codeforge-upgrade-repo.sh — CFP-744 §8 Test Contract impl (AC-11 parser refactor)
#
# Change Plan §3.7.2-parser 7-invariant byte-level binding 검증:
#   (a) 기존 mode invocation 불변 (--dry-run / --apply / --rollback <version> byte-identical)
#   (b) --repo <path> orthogonal (mode 와 순서 무관)
#   (c) --rollback <version> value-taking 보존
#   (d) mode 정확히 1개 강제 + 중복/충돌 reject
#   (e) free-text injection 차단 (unknown arg enum whitelist reject)
#   (f) downstream pipeline 무변경 (_to_canonical → CANONICAL_REPO_ROOT → input_repo_root)
#   (g) --repo/env 미지정 fallback byte-identical
#
# strict-verify-gate (CFP-744 Wave 1 #738 교훈): RAW verbatim 출력.
# Story-3 MERGED file regression 0 입증 (refactor 전후 byte-identical 동작).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CLI="${REPO_ROOT}/scripts/codeforge-upgrade.sh"

PASS=0
FAIL=0

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

_assert_output_not_contains() {
    local tc_name="${1}"
    local needle="${2}"
    shift 2
    local output
    output=$("$@" 2>&1) || true
    if echo "${output}" | grep -qF "${needle}"; then
        echo "FAIL [${tc_name}] unexpected '${needle}' in output"
        echo "  actual output: ${output}"
        FAIL=$((FAIL+1))
    else
        echo "PASS [${tc_name}]"
        PASS=$((PASS+1))
    fi
}

echo "=== codeforge-upgrade.sh AC-11 --repo parser refactor 7-invariant 검증 ==="

# tmp git repo 준비 (--repo <valid-git-repo> 검증용)
TMP_REPO="$(mktemp -d)"
git -C "${TMP_REPO}" init -q >/dev/null 2>&1
TMP_NONGIT="$(mktemp -d)"   # non-git dir (검증 실패 경로)
trap 'rm -rf "${TMP_REPO}" "${TMP_NONGIT}"' EXIT

# ---------------------------------------------------------------------------
# Invariant (a): 기존 mode invocation byte-identical (refactor 전후 regression 0)
# ---------------------------------------------------------------------------
_assert_exit "INV-a1: --dry-run exit 0 (불변)" 0 bash "${CLI}" --dry-run
_assert_output_contains "INV-a2: --dry-run mode=dry_run (불변)" "mode: dry_run" bash "${CLI}" --dry-run
_assert_exit "INV-a3: --apply exit 0 (불변)" 0 bash "${CLI}" --apply
_assert_output_contains "INV-a4: --apply mode=transaction (불변)" "mode: transaction" bash "${CLI}" --apply
_assert_exit "INV-a5: --rollback <ver> exit 0 (불변)" 0 bash "${CLI}" --rollback 5.74.0
_assert_output_contains "INV-a6: --rollback mode=snapshot_restore (불변)" "mode: snapshot_restore" bash "${CLI}" --rollback 5.74.0
_assert_output_contains "INV-a7: --rollback version 출력 (불변)" "rollback_version: 5.74.0" bash "${CLI}" --rollback 5.74.0
# 기존 error 메시지 byte-identical
_assert_output_contains "INV-a8: --rollback 미제공 error 문구 불변" "오류: --rollback 에는 version 인자가 필요합니다" bash "${CLI}" --rollback
_assert_exit "INV-a9: --rollback 미제공 exit 1 (불변)" 1 bash "${CLI}" --rollback
_assert_output_contains "INV-a10: 인자 없음 error 문구 불변" "오류: 인자가 필요합니다" bash "${CLI}"
_assert_exit "INV-a11: 인자 없음 exit 1 (불변)" 1 bash "${CLI}"
_assert_exit "INV-a12: --help exit 0 (불변)" 0 bash "${CLI}" --help

# ---------------------------------------------------------------------------
# Invariant (b): --repo <path> orthogonal — mode 와 순서 무관
# ---------------------------------------------------------------------------
_assert_exit "INV-b1: --apply --repo <git> exit 0" 0 bash "${CLI}" --apply --repo "${TMP_REPO}"
_assert_exit "INV-b2: --repo <git> --apply exit 0 (순서 역전)" 0 bash "${CLI}" --repo "${TMP_REPO}" --apply
_assert_output_contains "INV-b3: --apply --repo mode=transaction 보존" "mode: transaction" bash "${CLI}" --apply --repo "${TMP_REPO}"
_assert_output_contains "INV-b4: --repo --apply mode=transaction 보존 (순서 역전)" "mode: transaction" bash "${CLI}" --repo "${TMP_REPO}" --apply
_assert_exit "INV-b5: --dry-run --repo <git> exit 0" 0 bash "${CLI}" --dry-run --repo "${TMP_REPO}"
_assert_exit "INV-b6: --repo <git> --rollback <ver> exit 0" 0 bash "${CLI}" --repo "${TMP_REPO}" --rollback 5.74.0
_assert_output_contains "INV-b7: --repo --rollback version 보존" "rollback_version: 5.74.0" bash "${CLI}" --repo "${TMP_REPO}" --rollback 5.74.0
# --repo 가 input_repo_root 에 반영됨 (canonical 변환 후 TMP_REPO 경로 포함)
_assert_output_contains "INV-b8: --repo 가 input_repo_root 에 반영" "$(basename "${TMP_REPO}")" bash "${CLI}" --apply --repo "${TMP_REPO}"

# ---------------------------------------------------------------------------
# Invariant (c): --rollback <version> value-taking 보존 (--repo 와 공존)
# ---------------------------------------------------------------------------
_assert_output_contains "INV-c1: --rollback value consume (--repo 공존)" "rollback_version: 5.73.0" bash "${CLI}" --repo "${TMP_REPO}" --rollback 5.73.0
_assert_exit "INV-c2: --rollback 미제공 + --repo = exit 1" 1 bash "${CLI}" --repo "${TMP_REPO}" --rollback

# ---------------------------------------------------------------------------
# Invariant (d): mode 정확히 1개 강제 + 중복/충돌 reject
# ---------------------------------------------------------------------------
_assert_exit "INV-d1: mode 0개 (--repo only) exit 1" 1 bash "${CLI}" --repo "${TMP_REPO}"
_assert_exit "INV-d2: mode 2개 (--apply --dry-run) 충돌 reject" 1 bash "${CLI}" --apply --dry-run
_assert_exit "INV-d3: mode 중복 (--apply --apply) reject" 1 bash "${CLI}" --apply --apply
_assert_output_contains "INV-d4: mode 충돌 error 문구" "mode" bash "${CLI}" --apply --dry-run 2>&1 || true

# ---------------------------------------------------------------------------
# Invariant (e): free-text injection 차단 — unknown arg enum whitelist reject
# ---------------------------------------------------------------------------
_assert_exit "INV-e1: unknown arg exit 1" 1 bash "${CLI}" --bogus-flag
_assert_output_contains "INV-e2: unknown arg enum whitelist reject 문구" "알 수 없는 인자" bash "${CLI}" --bogus-flag 2>&1 || true
_assert_exit "INV-e3: --repo 후 unknown arg reject" 1 bash "${CLI}" --repo "${TMP_REPO}" --bogus
_assert_exit "INV-e4: --repo value 누락 exit 1" 1 bash "${CLI}" --apply --repo

# ---------------------------------------------------------------------------
# Invariant (f): downstream pipeline 무변경 — canonical_repo_root 출력 보존
# ---------------------------------------------------------------------------
_assert_output_contains "INV-f1: canonical_repo_root 출력 보존 (fallback)" "canonical_repo_root:" bash "${CLI}" --apply
_assert_output_contains "INV-f2: input_repo_root 출력 보존" "input_repo_root:" bash "${CLI}" --apply
_assert_output_contains "INV-f3: --repo canonical_repo_root 출력 보존" "canonical_repo_root:" bash "${CLI}" --apply --repo "${TMP_REPO}"

# ---------------------------------------------------------------------------
# Invariant (g): --repo/env 미지정 fallback byte-identical
#   fallback = $(cd "${SCRIPT_DIR}/.." && pwd) = REPO_ROOT
# ---------------------------------------------------------------------------
FALLBACK_OUT="$(bash "${CLI}" --apply 2>&1)"
FALLBACK_CANON="$(echo "${FALLBACK_OUT}" | grep '^canonical_repo_root:' | head -1)"
if echo "${FALLBACK_CANON}" | grep -qF "$(basename "${REPO_ROOT}")"; then
    echo "PASS [INV-g1: fallback canonical = REPO_ROOT 부모 (byte-identical)]"
    PASS=$((PASS+1))
else
    echo "FAIL [INV-g1: fallback canonical mismatch] got: ${FALLBACK_CANON}"
    FAIL=$((FAIL+1))
fi
# env CODEFORGE_REPO_ROOT override
_assert_output_contains "INV-g2: CODEFORGE_REPO_ROOT env override" "$(basename "${TMP_REPO}")" \
    env CODEFORGE_REPO_ROOT="${TMP_REPO}" bash "${CLI}" --apply
# 우선순위: --repo > env (--repo 가 env 를 이김)
ENV_REPO="$(mktemp -d)"; git -C "${ENV_REPO}" init -q >/dev/null 2>&1
PRIO_OUT="$(env CODEFORGE_REPO_ROOT="${ENV_REPO}" bash "${CLI}" --apply --repo "${TMP_REPO}" 2>&1)"
if echo "${PRIO_OUT}" | grep -qF "$(basename "${TMP_REPO}")" && ! echo "${PRIO_OUT}" | grep -qF "$(basename "${ENV_REPO}")"; then
    echo "PASS [INV-g3: --repo > env 우선순위]"
    PASS=$((PASS+1))
else
    echo "FAIL [INV-g3: --repo > env 우선순위] output: ${PRIO_OUT}"
    FAIL=$((FAIL+1))
fi
rm -rf "${ENV_REPO}"

# ---------------------------------------------------------------------------
# §7.4.1 (i): --repo wrong-target 검증 (실재 디렉터리 + .git 보유)
# ---------------------------------------------------------------------------
_assert_exit "DR-i1: --repo non-existent path abort" 2 bash "${CLI}" --apply --repo "/nonexistent/path/xyz123"
_assert_exit "DR-i2: --repo non-git dir abort" 2 bash "${CLI}" --apply --repo "${TMP_NONGIT}"
_assert_output_contains "DR-i3: --repo non-git abort-before-touch 문구" "abort-before-touch" bash "${CLI}" --apply --repo "${TMP_NONGIT}" 2>&1 || true

echo ""
echo "=== 결과 (AC-11 parser refactor 7-invariant) ==="
echo "PASS: ${PASS}"
echo "FAIL: ${FAIL}"
echo "TOTAL: $((PASS + FAIL))"
if [[ "${FAIL}" -gt 0 ]]; then
    exit 1
else
    exit 0
fi
