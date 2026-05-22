#!/usr/bin/env bash
# check-atlassian-tool-drift.sh
# CFP-1256 / ADR-103 §결정 3 Option B mitigation — atlassian-tool-drift check
# warning tier (ADR-060 evidence-checks-registry entry: atlassian-tool-drift)
#
# Option B per-tool deny decomposition 의 allow-by-omission weakening surface 감지:
#   verified snapshot (docs/atlassian-tool-snapshot.txt) ↔ .claude/settings.json permissions.deny 비교
#   → snapshot tool 중 deny 누락 = drift warning
#
# 현재 = instance 무관 declaration-only Wave 1:
#   - snapshot = placeholder (docs/atlassian-tool-snapshot.txt)
#   - snapshot 이 placeholder 면 check = advisory warning (exit 0)
#   - 실 snap 채움 후 drift 감지 가능
#
# Exit code:
#   0 — OK (snapshot placeholder advisory / 모든 snapshot tool 이 deny 에 존재)
#   1 — drift warning (snapshot tool 중 deny 누락 발견)
#
# ADR-061: bash 로 구현 (Python 불요 — 파일 비교 + grep 만 사용, 복잡한 로직 없음)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SNAPSHOT_FILE="${REPO_ROOT}/docs/atlassian-tool-snapshot.txt"
SETTINGS_FILE="${REPO_ROOT}/.claude/settings.json"

# ── snapshot 존재 확인 ──────────────────────────────────────────────────────
if [[ ! -f "${SNAPSHOT_FILE}" ]]; then
  echo "[WARN] atlassian-tool-drift: snapshot 파일 없음 (${SNAPSHOT_FILE})" >&2
  echo "  → docs/atlassian-tool-snapshot.txt 생성 후 실 Atlassian 인스턴스 tool 목록 채울 것" >&2
  exit 0  # 파일 부재 = advisory (exit 0)
fi

# ── snapshot placeholder 여부 확인 ─────────────────────────────────────────
# 실 tool entry (mcp__atlassian__로 시작하는 줄) 가 없으면 placeholder
REAL_TOOLS=$(grep -v '^\s*#' "${SNAPSHOT_FILE}" | grep -v '^\s*$' | grep '^mcp__atlassian__' || true)

if [[ -z "${REAL_TOOLS}" ]]; then
  echo "[ADVISORY] atlassian-tool-drift: snapshot placeholder — 실 tool 목록 미등록" >&2
  echo "  → Atlassian 인스턴스 연결 후 docs/atlassian-tool-snapshot.txt 채울 것 (ADR-103 §결정 3)" >&2
  echo "  → instance setup 후 enumerate: /mcp list-tools 또는 Claude Code mcp__atlassian__* 확인" >&2
  exit 0  # placeholder = advisory exit 0 (Warning 발화 + 계속)
fi

# ── settings.json deny 목록 추출 ───────────────────────────────────────────
if [[ ! -f "${SETTINGS_FILE}" ]]; then
  echo "[WARN] atlassian-tool-drift: settings.json 없음 (${SETTINGS_FILE})" >&2
  echo "  → .claude/settings.json 에 permissions.deny 설정 필요 (ADR-099 §결정 1 Layer 1)" >&2
  exit 1
fi

# permissions.deny 블록에서 atlassian tool 항목 추출 (grep 기반 간이 파서)
DENY_TOOLS=$(grep -o '"mcp__atlassian__[^"]*"' "${SETTINGS_FILE}" | tr -d '"' || true)

# ── drift 확인: snapshot tool 중 deny 에 없는 항목 ──────────────────────────
DRIFT_FOUND=false
DRIFT_LIST=""

while IFS= read -r tool; do
  [[ -z "${tool}" ]] && continue
  if ! echo "${DENY_TOOLS}" | grep -qF "${tool}"; then
    DRIFT_FOUND=true
    DRIFT_LIST="${DRIFT_LIST}  - ${tool}\n"
  fi
done <<< "${REAL_TOOLS}"

if [[ "${DRIFT_FOUND}" == "true" ]]; then
  echo "[WARN] atlassian-tool-drift: snapshot tool 중 permissions.deny 누락 발견 (allow-by-omission drift)" >&2
  echo "  → 아래 tool 이 .claude/settings.json permissions.deny 에 없음:" >&2
  printf "${DRIFT_LIST}" >&2
  echo "" >&2
  echo "  → deny 열거 갱신 의무 (ADR-103 §결정 3 Option B atlassian-tool-drift check)" >&2
  echo "  → pattern_count >= 2 재발 시 blocking-on-pr 승격 (ADR-060 evidence-checks-registry)" >&2
  exit 1
fi

echo "[OK] atlassian-tool-drift: snapshot 전부 deny 에 존재 (allow-by-omission drift 없음)" >&2
exit 0
