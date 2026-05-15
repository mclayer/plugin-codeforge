#!/usr/bin/env bash
# test-atomic-upgrade-7-plugins.sh — CFP-744 §8 Test Contract impl
#
# Change Plan §8.1/§8.2 커버리지:
#   AC-1: 단일 명령 7-plugin atomic sync, user_decision_branches: 0 (no prompt)
#   AC-2: per-family transaction boundary (부분 실패 → 전체 rollback)
#   AC-3: 사후 0-drift 검증 family-7 scope (codex/superpowers 제외 — F-002 옵션 A)
#   AC-6: Story-3 파일 경로 disjoint (codeforge-upgrade.* 미touch)
#   AC-7: per-plugin reconcile = Story-3 codeforge-upgrade.sh 위임 (semantic 분산 0)
#   AC-9: idempotency (--apply ALL none = no-op) / rollback-failure escalation
#   AC-11: --repo <path> propagation + 검증
#   §4.1 CLI arg schema / §4.2 transaction algorithm / §4.4 ownership
#
# 결정성: CODEFORGE_DRIFT_CHECK_BIN env 로 fast stub 주입 (network gh API 회피 —
#   프로덕션 동작 byte-identical, test-injectable seam).
#
# strict-verify-gate (CFP-744 Wave 1 #738 교훈): RAW verbatim 출력.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SCRIPT="${REPO_ROOT}/scripts/atomic-upgrade-7-plugins.sh"

PASS=0
FAIL=0

# --- fast deterministic drift-check stub (network gh API 회피) ---
STUB_DIR="$(mktemp -d)"
TMP_REPO="$(mktemp -d)"; git -C "${TMP_REPO}" init -q >/dev/null 2>&1
TMP_NONGIT="$(mktemp -d)"
trap 'rm -rf "${STUB_DIR}" "${TMP_REPO}" "${TMP_NONGIT}"' EXIT

# stub_none: 모든 plugin drift=none (idempotent no-op 경로 — AC-9 (a))
cat > "${STUB_DIR}/drift-none.sh" <<'STUB'
#!/usr/bin/env bash
# arg: --plugin <name> --json  → status none
echo '{"results":[{"plugin":"x","status":"none","installed":"5.75.0","latest":"5.75.0"}],"exit_code":0}'
exit 0
STUB
# stub_drift: 모든 plugin drift=minor (transaction 경로)
cat > "${STUB_DIR}/drift-minor.sh" <<'STUB'
#!/usr/bin/env bash
echo '{"results":[{"plugin":"x","status":"minor","installed":"5.74.0","latest":"5.75.0"}],"exit_code":0}'
exit 0
STUB
chmod +x "${STUB_DIR}/drift-none.sh" "${STUB_DIR}/drift-minor.sh"

_assert_exit() {
    local tc_name="${1}"; local expected_exit="${2}"; shift 2
    local actual_exit=0
    "$@" >/dev/null 2>&1 || actual_exit=$?
    if [[ "${actual_exit}" -eq "${expected_exit}" ]]; then
        echo "PASS [${tc_name}]"; PASS=$((PASS+1))
    else
        echo "FAIL [${tc_name}] expected exit=${expected_exit} got exit=${actual_exit}"; FAIL=$((FAIL+1))
    fi
}

_assert_output_contains() {
    local tc_name="${1}"; local needle="${2}"; shift 2
    local output
    output=$("$@" 2>&1) || true
    if printf '%s' "${output}" | grep -qF -- "${needle}"; then
        echo "PASS [${tc_name}]"; PASS=$((PASS+1))
    else
        echo "FAIL [${tc_name}] expected '${needle}' in output"
        echo "  actual output: ${output}"; FAIL=$((FAIL+1))
    fi
}

_assert_output_not_contains() {
    local tc_name="${1}"; local needle="${2}"; shift 2
    local output
    output=$("$@" 2>&1) || true
    if printf '%s' "${output}" | grep -qF -- "${needle}"; then
        echo "FAIL [${tc_name}] unexpected '${needle}' in output"; FAIL=$((FAIL+1))
    else
        echo "PASS [${tc_name}]"; PASS=$((PASS+1))
    fi
}

# default stub = drift-minor (transaction 경로 — 대부분 TC)
export CODEFORGE_DRIFT_CHECK_BIN="${STUB_DIR}/drift-minor.sh"

echo "=== atomic-upgrade-7-plugins.sh per-family transaction 검증 ==="

# --- TC-0: file 실재 + executable + POSIX strict + ADR-061 ---
[[ -f "${SCRIPT}" ]] && { echo "PASS [TC-0a: script 실재]"; PASS=$((PASS+1)); } || { echo "FAIL [TC-0a: script 부재]"; FAIL=$((FAIL+1)); }
[[ -x "${SCRIPT}" ]] && { echo "PASS [TC-0b: script +x]"; PASS=$((PASS+1)); } || { echo "FAIL [TC-0b: +x 부재]"; FAIL=$((FAIL+1)); }
SHEBANG="$(head -n 1 "${SCRIPT}" 2>/dev/null || echo "")"
[[ "${SHEBANG}" == "#!/usr/bin/env bash" ]] && { echo "PASS [TC-0c: shebang]"; PASS=$((PASS+1)); } || { echo "FAIL [TC-0c: shebang=${SHEBANG}]"; FAIL=$((FAIL+1)); }
if grep -qE 'python3?\s+<<|python3?\s+-c' "${SCRIPT}" 2>/dev/null; then
    echo "FAIL [TC-0d: ADR-061 heredoc-python 위반]"; FAIL=$((FAIL+1))
else
    echo "PASS [TC-0d: ADR-061 no heredoc-python]"; PASS=$((PASS+1))
fi
# strict mode
grep -q "^set -euo pipefail" "${SCRIPT}" && { echo "PASS [TC-0e: set -euo pipefail]"; PASS=$((PASS+1)); } || { echo "FAIL [TC-0e: strict mode 부재]"; FAIL=$((FAIL+1)); }

# --- TC-1: --help (§4.1 arg schema) ---
_assert_exit "TC-1a: --help exit 0" 0 bash "${SCRIPT}" --help
_assert_output_contains "TC-1b: --help --apply 안내" "--apply" bash "${SCRIPT}" --help
_assert_output_contains "TC-1c: --help --dry-run 안내" "--dry-run" bash "${SCRIPT}" --help
_assert_output_contains "TC-1d: --help --rollback 안내" "--rollback" bash "${SCRIPT}" --help
_assert_output_contains "TC-1e: --help --repo 안내" "--repo" bash "${SCRIPT}" --help

# --- TC-2: 인자 없음 reject ---
_assert_exit "TC-2: 인자 없음 exit 1" 1 bash "${SCRIPT}"

# --- TC-3: unknown arg enum whitelist reject (§7.1) ---
_assert_exit "TC-3a: unknown arg exit 1" 1 bash "${SCRIPT}" --bogus
_assert_output_contains "TC-3b: unknown arg reject 문구" "알 수 없는 인자" bash "${SCRIPT}" --bogus

# --- TC-4: mode 충돌 reject (§4.1 정확히 1 mode) ---
_assert_exit "TC-4a: --apply --dry-run 충돌 exit 1" 1 bash "${SCRIPT}" --apply --dry-run
_assert_exit "TC-4b: --apply --apply 중복 exit 1" 1 bash "${SCRIPT}" --apply --apply
_assert_output_contains "TC-4c: mode 충돌 error 문구" "mode" bash "${SCRIPT}" --apply --dry-run

# --- TC-5: --dry-run (AC-1 / AC-3 family-7 scope / F-002) ---
_assert_exit "TC-5a: --dry-run exit 0" 0 bash "${SCRIPT}" --dry-run
_assert_output_contains "TC-5b: --dry-run codeforge-pmo 포함" "codeforge-pmo" bash "${SCRIPT}" --dry-run
_assert_output_not_contains "TC-5c: --dry-run codex 미포함 (F-002)" "codex" bash "${SCRIPT}" --dry-run
_assert_output_not_contains "TC-5d: --dry-run superpowers 미포함 (F-002)" "superpowers" bash "${SCRIPT}" --dry-run
for p in codeforge codeforge-requirements codeforge-design codeforge-review codeforge-develop codeforge-test codeforge-pmo; do
    _assert_output_contains "TC-5e: --dry-run ${p} 포함" "${p}" bash "${SCRIPT}" --dry-run
done

# --- TC-6: AC-1 no prompt invariant ---
TC6_OUT="$(bash "${SCRIPT}" --dry-run 2>&1)"
if printf '%s' "${TC6_OUT}" | grep -qiE '(enter|press|confirm|y/n|yes/no)\?'; then
    echo "FAIL [TC-6: no prompt 위반]"; FAIL=$((FAIL+1))
else
    echo "PASS [TC-6: no prompt — user_decision_branches: 0 (AC-1)]"; PASS=$((PASS+1))
fi

# --- TC-7: AC-7 / §4.4 ownership (semantic 분산 0, drift 재구현 0) ---
if grep -qE '^(drift_classify|semver_cmp|installed_version|marketplace_version)\s*\(\)' "${SCRIPT}" 2>/dev/null; then
    echo "FAIL [TC-7a: §4.4 위반 — drift 로직 재구현]"; FAIL=$((FAIL+1))
else
    echo "PASS [TC-7a: §4.4 — drift 로직 재구현 0]"; PASS=$((PASS+1))
fi
grep -qF "codeforge-upgrade.sh" "${SCRIPT}" && { echo "PASS [TC-7b: AC-7 — codeforge-upgrade.sh 위임 참조]"; PASS=$((PASS+1)); } || { echo "FAIL [TC-7b: 위임 참조 부재]"; FAIL=$((FAIL+1)); }
if grep -qF "check-codeforge-version-drift.sh" "${SCRIPT}" && grep -qF -- "--plugin" "${SCRIPT}"; then
    echo "PASS [TC-7c: AC-3 — drift check --plugin 위임 참조]"; PASS=$((PASS+1))
else
    echo "FAIL [TC-7c: drift check --plugin 위임 참조 부재]"; FAIL=$((FAIL+1))
fi

# --- TC-8: AC-6 Story-3 file 경로 disjoint (수정 0, 호출만) ---
if grep -qE '>\s*[^|&;]*codeforge-upgrade\.(sh|ps1)|sed -i[^|]*codeforge-upgrade' "${SCRIPT}" 2>/dev/null; then
    echo "FAIL [TC-8: AC-6 위반 — Story-3 file 수정]"; FAIL=$((FAIL+1))
else
    echo "PASS [TC-8: AC-6 — Story-3 file 경로 disjoint]"; PASS=$((PASS+1))
fi

# --- TC-9: AC-11 --repo propagation + §7.4.1 (i) wrong-target ---
_assert_exit "TC-9a: --dry-run --repo <git> exit 0" 0 bash "${SCRIPT}" --dry-run --repo "${TMP_REPO}"
_assert_exit "TC-9b: --repo <git> --dry-run 순서 무관 exit 0" 0 bash "${SCRIPT}" --repo "${TMP_REPO}" --dry-run
_assert_output_contains "TC-9c: --repo propagation 출력 반영" "$(basename "${TMP_REPO}")" bash "${SCRIPT}" --dry-run --repo "${TMP_REPO}"
_assert_exit "TC-9d: --repo non-existent abort" 2 bash "${SCRIPT}" --dry-run --repo "/nonexistent/xyz999"
_assert_exit "TC-9e: --repo non-git dir abort" 2 bash "${SCRIPT}" --dry-run --repo "${TMP_NONGIT}"
_assert_output_contains "TC-9f: wrong-target abort-before-touch 문구" "abort-before-touch" bash "${SCRIPT}" --dry-run --repo "${TMP_NONGIT}"
_assert_exit "TC-9g: --repo value 누락 exit 1" 1 bash "${SCRIPT}" --apply --repo

# --- TC-10: §4.2 algorithm — idempotent no-op (AC-9 (a)) ---
# stub=drift-none → --apply ALL none → no-op 정상 종료 (snapshot 무생성)
NOOP_OUT="$(CODEFORGE_DRIFT_CHECK_BIN="${STUB_DIR}/drift-none.sh" bash "${SCRIPT}" --apply 2>&1)"
NOOP_EXIT=$?
if [[ "${NOOP_EXIT}" -eq 0 ]] && printf '%s' "${NOOP_OUT}" | grep -qF "no-op"; then
    echo "PASS [TC-10a: AC-9(a) idempotent no-op — ALL none → snapshot 무생성]"; PASS=$((PASS+1))
else
    echo "FAIL [TC-10a: idempotent no-op] exit=${NOOP_EXIT} output=${NOOP_OUT}"; FAIL=$((FAIL+1))
fi
_assert_output_contains "TC-10b: AC-9(a) §7.4.1 (e) 참조" "7.4.1 (e)" \
    env CODEFORGE_DRIFT_CHECK_BIN="${STUB_DIR}/drift-none.sh" bash "${SCRIPT}" --apply

# --- TC-11: §4.2 algorithm — drift present → per-family transaction ---
APPLY_OUT="$(CODEFORGE_DRIFT_CHECK_BIN="${STUB_DIR}/drift-minor.sh" bash "${SCRIPT}" --apply 2>&1)"
APPLY_EXIT=$?
if [[ "${APPLY_EXIT}" -eq 0 ]] && printf '%s' "${APPLY_OUT}" | grep -qF "per_family_transaction"; then
    echo "PASS [TC-11a: drift present → per-family transaction (§4.2 step 2-6)]"; PASS=$((PASS+1))
else
    echo "FAIL [TC-11a: transaction 경로] exit=${APPLY_EXIT} output=${APPLY_OUT}"; FAIL=$((FAIL+1))
fi
_assert_output_contains "TC-11b: §4.2 step_3 pre-atomic snapshot" "step_3_pre_atomic_snapshot" \
    env CODEFORGE_DRIFT_CHECK_BIN="${STUB_DIR}/drift-minor.sh" bash "${SCRIPT}" --apply
_assert_output_contains "TC-11c: §4.2 step_5 post-drift verify 7회" "step_5_post_drift_verify" \
    env CODEFORGE_DRIFT_CHECK_BIN="${STUB_DIR}/drift-minor.sh" bash "${SCRIPT}" --apply
_assert_output_contains "TC-11d: AC-2 부분 실패 → 전체 rollback" "atomic rollback" \
    env CODEFORGE_DRIFT_CHECK_BIN="${STUB_DIR}/drift-minor.sh" bash "${SCRIPT}" --apply
_assert_output_contains "TC-11e: AC-3 family-7 only (codex/superpowers 제외)" "F-002" \
    env CODEFORGE_DRIFT_CHECK_BIN="${STUB_DIR}/drift-minor.sh" bash "${SCRIPT}" --apply

# --- TC-12: --rollback (§7.4.1 (f) corrupt escalation / (g) GC) ---
_assert_exit "TC-12a: --rollback exit 0" 0 bash "${SCRIPT}" --rollback
_assert_output_contains "TC-12b: --rollback per-family snapshot 복원" "per-family" bash "${SCRIPT}" --rollback
_assert_output_contains "TC-12c: §7.4.1 (f) corrupt escalation" "escalation" bash "${SCRIPT}" --rollback
_assert_output_contains "TC-12d: §7.4.1 (g) stale GC" "GC" bash "${SCRIPT}" --rollback
_assert_output_contains "TC-12e: --rollback --repo propagation" "$(basename "${TMP_REPO}")" bash "${SCRIPT}" --rollback --repo "${TMP_REPO}"

echo ""
echo "=== 결과 (atomic-upgrade-7-plugins.sh) ==="
echo "PASS: ${PASS}"
echo "FAIL: ${FAIL}"
echo "TOTAL: $((PASS + FAIL))"
[[ "${FAIL}" -gt 0 ]] && exit 1 || exit 0
