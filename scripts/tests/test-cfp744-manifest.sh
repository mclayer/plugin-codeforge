#!/usr/bin/env bash
# test-cfp744-manifest.sh — CFP-744 §8 Test Contract impl (AC-10 consumer-scripts.manifest)
#
# Change Plan §3.7.1 / §5 AC-10:
#   - 4 entry append: codeforge-upgrade.sh / codeforge-upgrade.ps1 /
#     lib/path_normalize.py / atomic-upgrade-7-plugins.sh
#   - check-consumer-scripts-manifest.sh PASS (Check 3 file-existence + Check 4 executable-bit)
#   - workflow-invoked 아님 = dependent-workflow 미부착
#
# strict-verify-gate (CFP-744 Wave 1 #738 교훈): RAW verbatim 출력.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
MANIFEST="${REPO_ROOT}/templates/consumer-scripts.manifest"
LINT="${REPO_ROOT}/scripts/check-consumer-scripts-manifest.sh"

PASS=0
FAIL=0

echo "=== CFP-744 AC-10 consumer-scripts.manifest 4 entry 검증 ==="

# AC-10: 4 entry 실재 (codeforge-upgrade.sh/.ps1 / lib/path_normalize.py / atomic-upgrade-7-plugins.sh)
for entry in \
    "scripts/codeforge-upgrade.sh" \
    "scripts/codeforge-upgrade.ps1" \
    "scripts/lib/path_normalize.py" \
    "scripts/atomic-upgrade-7-plugins.sh"; do
    if grep -qxF "${entry}" "${MANIFEST}" 2>/dev/null; then
        echo "PASS [AC-10: manifest entry '${entry}']"
        PASS=$((PASS+1))
    else
        echo "FAIL [AC-10: manifest entry '${entry}' 부재]"
        FAIL=$((FAIL+1))
    fi
done

# AC-10: 4 entry 는 workflow-invoked 아님 → dependent-workflow 미부착 (colon 없음)
for entry in \
    "scripts/codeforge-upgrade.sh" \
    "scripts/codeforge-upgrade.ps1" \
    "scripts/lib/path_normalize.py" \
    "scripts/atomic-upgrade-7-plugins.sh"; do
    line="$(grep -F "${entry}" "${MANIFEST}" 2>/dev/null | head -1 || echo "")"
    if [[ "${line}" == "${entry}" ]]; then
        echo "PASS [AC-10: '${entry}' dependent-workflow 미부착 (colon 0)]"
        PASS=$((PASS+1))
    else
        echo "FAIL [AC-10: '${entry}' line='${line}' (colon/format 이상)]"
        FAIL=$((FAIL+1))
    fi
done

# Check 4: executable-bit — CI-faithful SSOT = git-tracked mode (git ls-files -s).
#   Linux CI (actions/checkout@v4, core.filemode=true) 가 git mode 100755 verbatim
#   restore → check-consumer-scripts-manifest.sh Check 4 [ ! -x ] PASS.
#   Windows worktree -x bit (core.filemode=false) = 무의미 artifact — git mode 가 SSOT.
#   lint extension 무관 (.py/.ps1 면제 없음 — verify-before-trust 확인).
for f in \
    "scripts/codeforge-upgrade.sh" \
    "scripts/codeforge-upgrade.ps1" \
    "scripts/lib/path_normalize.py" \
    "scripts/atomic-upgrade-7-plugins.sh"; do
    GITMODE="$(cd "${REPO_ROOT}" && git ls-files -s "${f}" 2>/dev/null | awk '{print $1}')"
    if [[ "${GITMODE}" == "100755" ]]; then
        echo "PASS [AC-10 Check 4: '${f}' git-mode=100755 (Linux CI -x TRUE → Check 4 PASS)]"
        PASS=$((PASS+1))
    else
        echo "FAIL [AC-10 Check 4: '${f}' git-mode=${GITMODE} (NOT 100755 — Linux CI Check 4 FAIL)]"
        FAIL=$((FAIL+1))
    fi
done

# check-consumer-scripts-manifest.sh RAW 실행 — Windows filemode 한계 명시.
#   Windows worktree (core.filemode=false): .ps1/.py worktree -x FALSE → 2 FAIL 예상
#     (Windows artifact — git mode 100755 = CI SSOT 위 git-mode 검증이 decisive proof).
#   Linux CI: actions/checkout restore 100755 → -x TRUE → 0 FAIL.
echo ""
echo "--- check-consumer-scripts-manifest.sh RAW (Windows worktree) ---"
LINT_OUT="$(cd "${REPO_ROOT}" && bash "${LINT}" 2>&1)"
LINT_EXIT=$?
echo "${LINT_OUT}"
echo "--- lint exit: ${LINT_EXIT} (Windows worktree) ---"

# CI-faithful 판정: git-tracked mode 100755 + 비-executable-bit lint 항목 0 FAIL.
#   Windows worktree -x artifact 외 모든 manifest entry 가 PASS 여야 함.
NON_XBIT_FAIL="$(printf '%s' "${LINT_OUT}" | grep -c 'FAIL' || true)"
XBIT_FAIL="$(printf '%s' "${LINT_OUT}" | grep -c 'script not executable: scripts/codeforge-upgrade.ps1\|script not executable: scripts/lib/path_normalize.py' || true)"
if [[ "${NON_XBIT_FAIL}" -eq "${XBIT_FAIL}" ]] && [[ "${XBIT_FAIL}" -le 2 ]]; then
    echo "PASS [AC-10: lint FAIL = Windows -x artifact 한정 (${XBIT_FAIL}건, git-mode 100755 검증 위에서 decisive PASS — Linux CI 0 FAIL)]"
    PASS=$((PASS+1))
else
    echo "FAIL [AC-10: lint 에 non-xbit FAIL 존재 (총 ${NON_XBIT_FAIL} FAIL, xbit-artifact ${XBIT_FAIL}건) — 실 production defect]"
    FAIL=$((FAIL+1))
fi

echo ""
echo "=== 결과 (AC-10 manifest) ==="
echo "PASS: ${PASS}"
echo "FAIL: ${FAIL}"
echo "TOTAL: $((PASS + FAIL))"
if [[ "${FAIL}" -gt 0 ]]; then
    exit 1
else
    exit 0
fi
