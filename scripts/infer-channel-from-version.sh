#!/usr/bin/env bash
# infer-channel-from-version.sh — CFP-932 Wave 4 sub-Epic #882 Story-2 — D3 migration tool
#
# 역할: read-only inference (write 0 invariant — project.yaml write edge 구조적 부재)
#   install plugin.json .version → registry marketplace.json channels[*].versions[] membership → tier 결정
#   project.yaml codeforge.channel block stdout 제안 (agent write 0 절대 invariant — ADR-027 §4b)
#
# ADR-027 §4b: consumer-authored write boundary 절대 보존
# INV-3: write-0 guard = tool 진입부터 종료까지 무조건 (transitive — sub-process도 write 0)
# ADR-061: heredoc-python 금지, 외부 .py oracle 사용
# DC-3 (CFP-932): CFP932_* test override env namespace
#
# Usage:
#   bash scripts/infer-channel-from-version.sh [--plugin-json-dir <dir>] [--marketplace <path>]
#
# Exit codes:
#   0 = 정상 (tier 추론 완료 — known or unknown)
#   2 = PARSE_ERROR (broken overlay YAML / missing dependency) — silent stable fallback 금지

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- test override env (CFP932_* namespace, DC-3) ---
PLUGIN_JSON_DIR="${CFP932_INFER_PLUGIN_JSON_DIR:-}"
MARKETPLACE_PATH="${CFP932_INFER_MARKETPLACE_PATH:-}"

# --- argument parse ---
while [[ $# -gt 0 ]]; do
    case "${1}" in
        --plugin-json-dir)
            if [[ $# -lt 2 ]]; then
                echo "오류: --plugin-json-dir 에는 디렉터리 경로 인자가 필요합니다." >&2
                exit 2
            fi
            PLUGIN_JSON_DIR="${2}"
            shift 2
            ;;
        --marketplace)
            if [[ $# -lt 2 ]]; then
                echo "오류: --marketplace 에는 파일 경로 인자가 필요합니다." >&2
                exit 2
            fi
            MARKETPLACE_PATH="${2}"
            shift 2
            ;;
        --help|-h)
            cat <<'USAGE'
infer-channel-from-version.sh — CFP-932 D3 migration tool (read-only inference)

사용법:
  bash scripts/infer-channel-from-version.sh [--plugin-json-dir <dir>] [--marketplace <path>]

옵션:
  --plugin-json-dir <dir>   install plugin.json lookup 디렉터리 (default: gh API)
  --marketplace <path>      registry marketplace.json local 파일 (default: gh API)

원칙:
  - write 0 invariant: project.yaml 미수정 (stdout 제안 only — ADR-027 §4b)
  - INV-3: transitive write-0 (sub-process 포함)
  - 매칭 tier 없으면 unknown + stable 권장
USAGE
            exit 0
            ;;
        *)
            echo "오류: 알 수 없는 인자: '${1}'" >&2
            echo "허용: --plugin-json-dir <dir> / --marketplace <path>" >&2
            exit 2
            ;;
    esac
done

# --- dependency check ---
command -v jq >/dev/null 2>&1 || { echo "[infer-channel] SETUP_ERROR: jq not installed" >&2; exit 2; }

if [[ -z "${MARKETPLACE_PATH}" ]]; then
    command -v gh >/dev/null 2>&1 || { echo "[infer-channel] SETUP_ERROR: gh CLI not installed" >&2; exit 2; }
fi

# --- marketplace.json 취득 ---
MARKETPLACE_JSON=""
if [[ -n "${MARKETPLACE_PATH}" ]]; then
    if [[ ! -f "${MARKETPLACE_PATH}" ]]; then
        echo "[infer-channel] PARSE_ERROR: marketplace override path not found: ${MARKETPLACE_PATH}" >&2
        exit 2
    fi
    MARKETPLACE_JSON="$(cat "${MARKETPLACE_PATH}")"
else
    MARKETPLACE_RAW="$(gh api "repos/mclayer/marketplace/contents/.claude-plugin/marketplace.json" 2>&1)" || {
        echo "[infer-channel] PARSE_ERROR: gh API failed — marketplace.json 취득 불가" >&2
        exit 2
    }
    MARKETPLACE_JSON="$(echo "${MARKETPLACE_RAW}" | jq -r '.content' 2>/dev/null | base64 -d 2>/dev/null || echo "")"
    if [[ -z "${MARKETPLACE_JSON}" ]]; then
        echo "[infer-channel] PARSE_ERROR: marketplace.json base64 decode 실패" >&2
        exit 2
    fi
fi

# JSON validate
if ! echo "${MARKETPLACE_JSON}" | jq empty 2>/dev/null; then
    echo "[infer-channel] PARSE_ERROR: marketplace.json is not valid JSON" >&2
    exit 2
fi

# --- install plugin.json .version 취득 (codeforge plugin) ---
PLUGIN_VERSION=""
if [[ -n "${PLUGIN_JSON_DIR}" ]]; then
    PLUGIN_JSON_PATH="${PLUGIN_JSON_DIR}/codeforge.json"
    if [[ ! -f "${PLUGIN_JSON_PATH}" ]]; then
        echo "[infer-channel] PARSE_ERROR: plugin.json not found: ${PLUGIN_JSON_PATH}" >&2
        exit 2
    fi
    PLUGIN_JSON_CONTENT="$(cat "${PLUGIN_JSON_PATH}")"
    if ! echo "${PLUGIN_JSON_CONTENT}" | jq empty 2>/dev/null; then
        echo "[infer-channel] PARSE_ERROR: plugin.json is not valid JSON" >&2
        exit 2
    fi
    PLUGIN_VERSION="$(echo "${PLUGIN_JSON_CONTENT}" | jq -r '.version // empty' 2>/dev/null || echo "")"
else
    PLUGIN_RAW="$(gh api "repos/mclayer/plugin-codeforge/contents/.claude-plugin/plugin.json" 2>&1)" || {
        echo "[infer-channel] PARSE_ERROR: gh API failed — plugin.json 취득 불가" >&2
        exit 2
    }
    PLUGIN_JSON_CONTENT="$(echo "${PLUGIN_RAW}" | jq -r '.content' 2>/dev/null | base64 -d 2>/dev/null || echo "")"
    if [[ -z "${PLUGIN_JSON_CONTENT}" ]]; then
        echo "[infer-channel] PARSE_ERROR: plugin.json base64 decode 실패" >&2
        exit 2
    fi
    PLUGIN_VERSION="$(echo "${PLUGIN_JSON_CONTENT}" | jq -r '.version // empty' 2>/dev/null || echo "")"
fi

if [[ -z "${PLUGIN_VERSION}" ]]; then
    echo "[infer-channel] PARSE_ERROR: plugin.json .version field 부재" >&2
    exit 2
fi

# --- marketplace.json channels[*].versions[] membership 역추론 ---
INFERRED_TIER=""

# channels 블록 존재 확인 (Story-4 전 = populate 0 → graceful unknown)
CHANNELS_COUNT="$(echo "${MARKETPLACE_JSON}" | jq '[.plugins[] | select(.name == "codeforge")] | .[0].channels // [] | length' 2>/dev/null || echo "0")"

if [[ "${CHANNELS_COUNT}" == "0" ]] || [[ -z "${CHANNELS_COUNT}" ]]; then
    # channels[] 미populate (Story-4 전) → graceful unknown (OQ-1 / INV-8)
    INFERRED_TIER="unknown"
else
    # channels[*].versions[] membership lookup
    for tier in stable beta canary; do
        MATCHED="$(echo "${MARKETPLACE_JSON}" | jq --arg tier "${tier}" --arg ver "${PLUGIN_VERSION}" \
            '[.plugins[] | select(.name == "codeforge")] | .[0].channels // [] | .[] | select(.tier == $tier) | .versions // [] | .[] | select(. == $ver)' \
            2>/dev/null || echo "")"
        if [[ -n "${MATCHED}" ]]; then
            INFERRED_TIER="${tier}"
            break
        fi
    done

    if [[ -z "${INFERRED_TIER}" ]]; then
        INFERRED_TIER="unknown"
    fi
fi

# --- 결과 출력 (stdout-only, write 0) ---
echo "[infer-channel] install version ${PLUGIN_VERSION} → matched tier: ${INFERRED_TIER}"

SUGGEST_TIER="${INFERRED_TIER}"
if [[ "${INFERRED_TIER}" == "unknown" ]]; then
    SUGGEST_TIER="stable"
    echo "[infer-channel] 매칭 tier 없음 (channels[] 미등록 또는 version 불일치) → stable 권장"
fi

echo "[infer-channel] Suggested project.yaml addition:"
cat <<SUGGEST
codeforge:
  channel:
    tier: ${SUGGEST_TIER}
SUGGEST
echo "[infer-channel] Copy the above block to .claude/_overlay/project.yaml (codeforge agent write 금지 — ADR-027 §4b)"

exit 0
