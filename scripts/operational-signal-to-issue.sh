#!/usr/bin/env bash
# scripts/operational-signal-to-issue.sh
# CFP-1195 — self-improving loop closure (thin bash orchestration)
#
# ADR-106 §결정 1 단계 2-b:
#   (a) 비-monitor 신호 source 직접 입력 → ops-signal Issue 발의
#   (b) Epic-level dedup gate (모든 ops-signal Issue 대상) — S4/S5 0 line touch
#
# loop closure 3원칙 (ADR-106 §결정 4, OR 발동):
#   (a) dedup: open Issue OR 진행 Epic 존재 → 발의 차단
#   (b) max-depth: loop_depth >= 상한 → escalate_user
#   (c) escalate_user: max-depth/dedup OR trip → 자동 발의 0 + 사용자 통지
#
# 단계 4: 사용자 게이트 — 자동 Epic 개시 금지 (self-improving != self-executing)
#
# ADR-104 §결정 3: 0 API call (filesystem/cron 우선)
# ADR-104 §결정 4: wrapper fast-pass (Tier-1 declare-time exemption)
# ADR-061: 산술 5줄 초과 → loop_closure_gate.py 위임
# ADR-060: exit 3-tier (0=PASS / 1=reserved / 2=SETUP error)
# ADR-079: KST timestamp (detected_at_kst)
#
# 답습 source: check-rollback-signal.sh (CFP-1193) + check-operational-regression.sh (CFP-1194)
#   wrapper fast-pass / _CFP1193_MOCK_* 패턴 / exit 3-tier / ops-signal label
#
# mock seam (_CFP1195_MOCK_* namespace):
#   _CFP1195_MOCK_DEDUP=<0|1>           — dedup gate (open Issue) mock (1=trip)
#   _CFP1195_MOCK_EPIC_OPEN=<0|1>       — Epic-level dedup mock (1=trip)
#   _CFP1195_MOCK_LOOP_DEPTH=<int>      — loop_depth override
#   _CFP1195_MOCK_PATTERN_COUNT=<int>   — pattern_count override
#   _CFP1195_MOCK_SHA_CONFLICT=<0|1>    — SHA 409 conflict mock
#   _CFP1195_MOCK_REPO_NAME=<str>       — repo name override (wrapper fast-pass)
#   _CFP1195_SKIP_ISSUE_CREATE=<1>      — dry-run (Issue 발의 차단)
#
# Exit codes:
#   0 = PASS (발의 성공 또는 gate trip → 억제 정상 처리)
#   1 = reserved
#   2 = SETUP error (python3 부재 / loop_closure_gate.py 부재 / parse error)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKTREE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOOP_CLOSURE_GATE_PY="${WORKTREE_ROOT}/scripts/loop_closure_gate.py"

# --- 인수 파싱 ---
REPO=""
SIGNAL_TYPE=""
MEASURED_VALUE=""
THRESHOLD=""
WINDOW="3600s"
SIGNAL_SOURCE="direct"  # "direct" = 비-monitor 신호 (단계 2-b (a))

usage() {
  cat <<'EOF'
Usage: operational-signal-to-issue.sh --repo <owner/repo> --signal-type <type> \
         --measured-value <float> --threshold <float> [--window <str>]

Options:
  --repo <owner/repo>        대상 consumer repo (wrapper fast-pass 기준)
  --signal-type <type>       신호 유형 (error_rate|latency_burn_rate|regression|smoke_health)
  --measured-value <float>   측정값
  --threshold <float>        임계값
  --window <str>             측정 window (default: 3600s)

환경변수 (mock seam):
  _CFP1195_MOCK_DEDUP=1       — open Issue dedup mock
  _CFP1195_MOCK_EPIC_OPEN=1   — open Epic dedup mock
  _CFP1195_MOCK_LOOP_DEPTH=N  — loop_depth override
  _CFP1195_SKIP_ISSUE_CREATE=1 — dry-run
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)           REPO="$2"; shift 2 ;;
    --signal-type)    SIGNAL_TYPE="$2"; shift 2 ;;
    --measured-value) MEASURED_VALUE="$2"; shift 2 ;;
    --threshold)      THRESHOLD="$2"; shift 2 ;;
    --window)         WINDOW="$2"; shift 2 ;;
    --help|-h)        usage; exit 0 ;;
    *) echo "[ERROR] unknown arg: $1" >&2; exit 1 ;;
  esac
done

# --- 필수 인수 확인 ---
if [[ -z "${REPO}" || -z "${SIGNAL_TYPE}" || -z "${MEASURED_VALUE}" || -z "${THRESHOLD}" ]]; then
  echo "[ERROR] --repo, --signal-type, --measured-value, --threshold 필수" >&2
  usage >&2
  exit 1
fi

# --- wrapper fast-pass (Tier-1 declare-time exemption, ADR-104 §결정 4 / ADR-072) ---
# mock seam: _CFP1195_MOCK_REPO_NAME override
EFFECTIVE_REPO="${_CFP1195_MOCK_REPO_NAME:-${REPO}}"
if [[ "${EFFECTIVE_REPO}" == "mclayer/plugin-codeforge" ]]; then
  echo "[operational-signal-to-issue] wrapper repo detected — fast-pass exit 0 (Tier-1 declare-time exemption)"
  exit 0
fi

# --- python3 의존성 확인 (ADR-061 정합) ---
if ! command -v python3 &>/dev/null; then
  echo "[ERROR] python3 not found — loop_closure_gate.py 실행 불가" >&2
  exit 2
fi

if [[ ! -f "${LOOP_CLOSURE_GATE_PY}" ]]; then
  echo "[ERROR] loop_closure_gate.py 부재: ${LOOP_CLOSURE_GATE_PY}" >&2
  exit 2
fi

# --- signature 생성 (S4/S5 패턴 답습: sha256 hex 16-char) ---
# sha256(signal_type|measured_value|window) | head -c 16
SIG_RAW="${SIGNAL_TYPE}|${MEASURED_VALUE}|${WINDOW}"
if command -v sha256sum &>/dev/null; then
  SIGNATURE="$(echo -n "${SIG_RAW}" | sha256sum | cut -c1-16)"
elif command -v shasum &>/dev/null; then
  SIGNATURE="$(echo -n "${SIG_RAW}" | shasum -a 256 | cut -c1-16)"
elif command -v python3 &>/dev/null; then
  SIGNATURE="$(python3 -c "import hashlib,sys; print(hashlib.sha256(sys.argv[1].encode()).hexdigest()[:16])" "${SIG_RAW}")"
else
  echo "[ERROR] sha256 도구 부재 (sha256sum/shasum/python3 중 1개 필요)" >&2
  exit 2
fi

echo "[operational-signal-to-issue] signal_type=${SIGNAL_TYPE} signature=${SIGNATURE}"

# --- Epic-level dedup gate (b): open Issue OR 진행 Epic 존재 체크 ---
# S4/S5 Issue-level dedup 과 disjoint (layer 확장 — S4/S5 0 line touch)
DEDUP_TRIP=0
EPIC_DEDUP_TRIP=0

# mock seam
if [[ "${_CFP1195_MOCK_DEDUP:-0}" == "1" ]]; then
  DEDUP_TRIP=1
  echo "[operational-signal-to-issue] dedup mock: open Issue 존재 (mock)"
fi

if [[ "${_CFP1195_MOCK_EPIC_OPEN:-0}" == "1" ]]; then
  EPIC_DEDUP_TRIP=1
  echo "[operational-signal-to-issue] dedup mock: open Epic 존재 (mock)"
fi

# 실제 gh 호출 (dry-run 아닌 경우)
if [[ "${_CFP1195_SKIP_ISSUE_CREATE:-0}" != "1" && "${DEDUP_TRIP}" == "0" ]]; then
  # open Issue dedup (동일 signature — S4/S5 Issue-level 답습, Epic-level 추가)
  OPEN_ISSUE_COUNT=$(
    gh issue list \
      --repo "${REPO}" \
      --state open \
      --label "ops-signal" \
      --search "\"signature: ${SIGNATURE}\"" \
      --json number \
      --jq 'length' \
      2>/dev/null || echo "0"
  )
  if [[ "${OPEN_ISSUE_COUNT}" -gt 0 ]]; then
    DEDUP_TRIP=1
    echo "[operational-signal-to-issue] Epic-level dedup: open Issue ${OPEN_ISSUE_COUNT}건 존재 (signature: ${SIGNATURE})"
  fi
fi

if [[ "${_CFP1195_SKIP_ISSUE_CREATE:-0}" != "1" && "${EPIC_DEDUP_TRIP}" == "0" ]]; then
  # open Epic dedup (동일 signature — S6 신설)
  OPEN_EPIC_COUNT=$(
    gh issue list \
      --repo "${REPO}" \
      --state open \
      --search "type:epic \"signature: ${SIGNATURE}\"" \
      --json number \
      --jq 'length' \
      2>/dev/null || echo "0"
  )
  if [[ "${OPEN_EPIC_COUNT}" -gt 0 ]]; then
    EPIC_DEDUP_TRIP=1
    echo "[operational-signal-to-issue] Epic-level dedup: open Epic ${OPEN_EPIC_COUNT}건 존재 (signature: ${SIGNATURE})"
  fi
fi

# 종합 dedup gate 결과를 환경변수로 주입 (loop_closure_gate.py 참조)
export _CFP1195_DEDUP_GATE_RESULT
if [[ "${DEDUP_TRIP}" == "1" || "${EPIC_DEDUP_TRIP}" == "1" ]]; then
  _CFP1195_DEDUP_GATE_RESULT="1"
else
  _CFP1195_DEDUP_GATE_RESULT="0"
fi

# --- loop_closure_gate.py 호출 (산술 위임 — ADR-061) ---
GATE_OUTPUT=$(
  CFP1195_SIGNAL_SIGNATURE="${SIGNATURE}" \
  CFP1195_SIGNAL_TYPE="${SIGNAL_TYPE}" \
  CFP1195_MEASURED_VALUE="${MEASURED_VALUE}" \
  CFP1195_THRESHOLD="${THRESHOLD}" \
  CFP1195_WINDOW="${WINDOW}" \
  python3 "${LOOP_CLOSURE_GATE_PY}" 2>&1
) || {
  EXIT_CODE=$?
  if [[ ${EXIT_CODE} -eq 2 ]]; then
    echo "[ERROR] loop_closure_gate.py SETUP error" >&2
    exit 2
  fi
}

# bash eval로 출력 파싱
eval "${GATE_OUTPUT}" 2>/dev/null || true

CLOSURE_GATE="${CLOSURE_GATE:-pass}"
LOOP_DEPTH="${LOOP_DEPTH:-0}"
PATTERN_COUNT="${PATTERN_COUNT:-0}"
ESCALATION_ACTION="${ESCALATION_ACTION:-none}"

echo "[operational-signal-to-issue] closure_gate=${CLOSURE_GATE} loop_depth=${LOOP_DEPTH} pattern_count=${PATTERN_COUNT}"

# --- closure gate 결과 처리 ---
if [[ "${CLOSURE_GATE}" != "pass" ]]; then
  echo "[operational-signal-to-issue] loop closure gate trip: ${CLOSURE_GATE} → 자동 발의 억제"
  if [[ "${ESCALATION_ACTION}" == "escalate_user" ]]; then
    echo ""
    echo "============================================================"
    echo "[ADR-106 §결정 4] loop closure gate TRIP — escalate_user"
    echo "============================================================"
    echo "  gate_reason: ${CLOSURE_GATE}"
    echo "  loop_depth: ${LOOP_DEPTH}"
    echo "  pattern_count: ${PATTERN_COUNT}"
    echo "  signal_type: ${SIGNAL_TYPE}"
    echo "  signature: ${SIGNATURE}"
    echo ""
    echo "ORCHESTRATOR DIRECTIVE: loop closure gate trip — PMOAgent를 spawn하여"
    echo "운영 신호 누적 상황을 사용자에게 보고하십시오."
    echo "자동 Epic 개시 금지 (self-improving != self-executing, ADR-106 §결정 4 단계 4)."
    echo "============================================================"
  fi
  exit 0  # gate trip = 정상 처리 (발의 억제 = PASS)
fi

# --- 단계 2-b (a): 비-monitor 신호 Issue 발의 ---
# S4/S5-originated Issue = Epic-level dedup gate 만 (재발의 0 — double-issue 차단)
# 단계 4: 자동 Epic 개시 금지 (사용자 확인 게이트 의무)

ISSUE_TITLE="[ops-signal] ${SIGNAL_TYPE} 임계 초과 감지 (signature: ${SIGNATURE})"
ISSUE_BODY="## 운영 신호 감지 (자동 알림)

**신호 유형**: ${SIGNAL_TYPE}
**측정값**: ${MEASURED_VALUE}
**임계값**: ${THRESHOLD}
**측정 window**: ${WINDOW}
**signature**: ${SIGNATURE}
**loop_depth**: ${LOOP_DEPTH}
**pattern_count**: ${PATTERN_COUNT}

> 본 Issue 는 ADR-106 §결정 1 단계 2-b self-improving loop 회로가 자동 발의했습니다.
> Epic 개시 여부는 사용자 확인 게이트 후 결정 (self-improving != self-executing).

### 다음 단계 (단계 3 → 단계 4)
- check-ops-signal-alerts.sh 가 pattern_count ≥ 2 감지 시 PMOAgent escalation
- PMOAgent 보고 → Orchestrator → **사용자 확인 후** 다음 Epic 후보 결정
- 자동 Epic 개시 금지 (ADR-106 §결정 4 단계 4 사용자 게이트 의무)
"

if [[ "${_CFP1195_SKIP_ISSUE_CREATE:-0}" == "1" ]]; then
  echo "[operational-signal-to-issue] dry-run: Issue 발의 skip (_CFP1195_SKIP_ISSUE_CREATE=1)"
  echo "[operational-signal-to-issue] PASS — gate open, Issue 발의 ready"
  exit 0
fi

echo "[operational-signal-to-issue] ops-signal Issue 발의 중..."
ISSUE_URL=$(
  gh issue create \
    --repo "${REPO}" \
    --title "${ISSUE_TITLE}" \
    --body "${ISSUE_BODY}" \
    --label "ops-signal" \
    2>/dev/null
) || {
  echo "[ERROR] gh issue create 실패" >&2
  exit 2
}

echo "[operational-signal-to-issue] ops-signal Issue 발의 완료: ${ISSUE_URL}"
echo "[operational-signal-to-issue] PASS"
exit 0
