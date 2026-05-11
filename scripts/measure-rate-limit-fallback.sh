#!/usr/bin/env bash
# measure-rate-limit-fallback.sh
# CFP-393 / ADR-057 Amendment 2 / evidence-checks-registry.yaml entry `rate-limit-fallback-rate`
#
# 책임: §14 Lane Evidence `[rate-limit-fallback:sonnet→opus]` 태그 카운트 aggregator
#       (CFP-388 evidence-enforceable framework 첫 non-sunset application).
#
# 입력:
#   - wrapper repo `docs/stories/**.md` §14 row scan
#   - internal-docs repo `wrapper/stories/**.md` §14 row scan (--internal-docs-path 지정 시)
#
# 출력: KPI JSON (Change Plan §4.2 schema verbatim) — stdout (--out 미지정) 또는 file
#
# 의존: bash 5+, jq, grep, awk, date, sort. offline runnable (네트워크 egress 0건).
#
# Idempotent invariant: 동일 input → 동일 output (T-9 fixture).
# Atomic write: stdout = streaming JSON. --out 사용 시 tmpfile + mv.
#
# 분모: Sonnet 잔류 5 agent 의 §14 row spawn 카운트.
#       SSOT (verbatim, ADR-039 default subagent context — hardcode + cross-ref):
#         - DeveloperAgent           (ADR-057 §결정 3 + ADR-042 Amendment 4)
#         - BackendDeveloperAgent    (ADR-057 §결정 3 + ADR-042 Amendment 4)
#         - FrontendDeveloperAgent   (ADR-057 §결정 3 + ADR-042 Amendment 4)
#         - IntegrationTestAgent     (ADR-057 §결정 3 + ADR-042 Amendment 4)
#         - StatefulTestAgent        (ADR-057 §결정 3 + ADR-042 Amendment 4)
#       drift 발견 시 별도 CFP follow-up (Story CFP-393 §11 follow-up #1).
#
# 분자: §14 `transcript` 필드 substring `[rate-limit-fallback:sonnet→opus]`
#       또는 ASCII fallback `[rate-limit-fallback:sonnet->opus]` (T-8 fixture).
#
# Sample size sentinel: 각 month spawn 카운트 모두 ≥ 50 시에만 sufficient
#                       (Change Plan §8 T-2 — monthly AND, sunset gate 의미 정합).
#                       false 시 `fallback_rate_percent: null`, `gate_status: sample_insufficient`.
#
# Threshold: `>= 1.0%` strict violation (Change Plan §8 T-4).
#
# Window: 3 calendar month rolling, UTC, half-open `[month-N-start, month-N+1-start)`.
#         --as-of YYYY-MM 로 "now" override (idempotency + 테스트 가능성).
#
# Exit codes: 0=정상, 1=입력 검증 실패 (script error), 2=write 실패 (--out 지정 시).
#
# CLI:
#   bash scripts/measure-rate-limit-fallback.sh \
#     [--internal-docs-path <path>] \
#     [--out <json-path>] \
#     [--as-of YYYY-MM] \
#     [--wrapper-path <path>]
set -euo pipefail

# Sonnet 잔류 agent 5종 — ADR-057 §결정 3 / ADR-042 Amendment 4 SSOT verbatim.
SONNET_AGENTS=(
  "DeveloperAgent"
  "BackendDeveloperAgent"
  "FrontendDeveloperAgent"
  "IntegrationTestAgent"
  "StatefulTestAgent"
)

WINDOW_MONTHS=3
SAMPLE_MIN_PER_MONTH=50         # Change Plan §4.2 + §8 T-2 (monthly AND)
THRESHOLD_PERCENT="1.0"          # Change Plan §8 T-4 (strict >= violation)

# --- 옵션 파싱 ---
INTERNAL_DOCS_PATH=""
WRAPPER_PATH=""
OUT_FILE=""
AS_OF=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --internal-docs-path)
      INTERNAL_DOCS_PATH="${2:-}"; shift 2 ;;
    --wrapper-path)
      WRAPPER_PATH="${2:-}"; shift 2 ;;
    --out)
      OUT_FILE="${2:-}"; shift 2 ;;
    --as-of)
      AS_OF="${2:-}"; shift 2 ;;
    -h|--help)
      sed -n '2,30p' "$0" >&2; exit 0 ;;
    *)
      echo "[measure-rate-limit-fallback] unknown option: $1" >&2; exit 1 ;;
  esac
done

# 기본 wrapper-path = script 실행 디렉터리 기준 repo root.
if [[ -z "$WRAPPER_PATH" ]]; then
  WRAPPER_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fi

# Story file 후보 path.
WRAPPER_STORIES_DIR="$WRAPPER_PATH/docs/stories"
INTERNAL_DOCS_STORIES_DIR=""
if [[ -n "$INTERNAL_DOCS_PATH" ]]; then
  # internal-docs monorepo layout: <root>/wrapper/stories/CFP-N.md
  if [[ -d "$INTERNAL_DOCS_PATH/wrapper/stories" ]]; then
    INTERNAL_DOCS_STORIES_DIR="$INTERNAL_DOCS_PATH/wrapper/stories"
  fi
fi

# --- 시계 결정 ---
# AS_OF override 우선, 없으면 "now" UTC.
if [[ -n "$AS_OF" ]]; then
  if [[ ! "$AS_OF" =~ ^[0-9]{4}-[0-9]{2}$ ]]; then
    echo "[measure-rate-limit-fallback] --as-of 는 YYYY-MM 형식이어야 합니다: $AS_OF" >&2
    exit 1
  fi
  REF_YEAR="${AS_OF%-*}"
  REF_MONTH="${AS_OF#*-}"
  # leading zero 제거 (10# = decimal 강제)
  REF_MONTH=$((10#$REF_MONTH))
  REF_YEAR=$((10#$REF_YEAR))
else
  REF_YEAR=$(date -u +%Y)
  REF_MONTH=$(date -u +%m)
  REF_MONTH=$((10#$REF_MONTH))
  REF_YEAR=$((10#$REF_YEAR))
fi

# 3 month rolling window = 직전 N month (REF month 미포함).
# half-open `[start, end)` — 본 month 가 N+1 안에 들어가지 않도록.
# 예: AS_OF=2026-06, WINDOW=3 → buckets = {2026-03, 2026-04, 2026-05} (5월 31일까지).
declare -a WINDOW_BUCKETS=()
for ((i=WINDOW_MONTHS; i>=1; i--)); do
  M=$((REF_MONTH - i))
  Y=$REF_YEAR
  while ((M < 1)); do M=$((M + 12)); Y=$((Y - 1)); done
  WINDOW_BUCKETS+=("$(printf "%04d-%02d" "$Y" "$M")")
done

# --- Story file 수집 ---
STORY_FILES=()
if [[ -d "$WRAPPER_STORIES_DIR" ]]; then
  while IFS= read -r -d '' f; do STORY_FILES+=("$f"); done < <(find "$WRAPPER_STORIES_DIR" -maxdepth 1 -type f -name "*.md" -print0 2>/dev/null || true)
fi
PARTIAL_DATA=false
if [[ -n "$INTERNAL_DOCS_STORIES_DIR" ]]; then
  while IFS= read -r -d '' f; do STORY_FILES+=("$f"); done < <(find "$INTERNAL_DOCS_STORIES_DIR" -maxdepth 1 -type f -name "*.md" -print0 2>/dev/null || true)
elif [[ -n "$INTERNAL_DOCS_PATH" ]]; then
  echo "[measure-rate-limit-fallback] WARN: internal-docs path 부재 또는 wrapper/stories/ 누락 — wrapper-only mode" >&2
  PARTIAL_DATA=true
else
  # internal-docs 가 의도적으로 미지정 (local dev) — partial 표기 (Change Plan §7.4 OR-2 + §3.3 T-10).
  PARTIAL_DATA=true
fi

# --- §14 row scan ---
# 단순 line scan: §14 row 의 `agent:` + `spawned_at:` + `transcript:` 라인 3종을 grouped 추출.
# YAML 정식 파서 도입 X (offline + 의존 최소 — bash + grep + awk).
# 가정: 각 row block 안에서 `- lane:` 시작 → 다음 `- lane:` 또는 EOF 까지가 1 row.
# 각 row 의 agent / spawned_at / transcript 한 줄씩.
#
# 출력 (tab-separated): <month-bucket>\t<agent>\t<has_fallback_tag:0|1>
SCAN_OUT="$(mktemp -t cfp393-scan.XXXXXX)"
trap 'rm -f "$SCAN_OUT"' EXIT

awk '
function ltrim(s){sub(/^[ \t]+/,"",s); return s}
function rtrim(s){sub(/[ \t]+$/,"",s); return s}
function trim(s){return rtrim(ltrim(s))}
BEGIN {
  in_evidence = 0
  cur_agent = ""
  cur_spawned_at = ""
  cur_transcript = ""
  cur_active = 0
}
function emit_row() {
  if (cur_active == 0) return
  # month bucket = spawned_at YYYY-MM prefix (T-6: malformed → skip).
  bucket = ""
  if (match(cur_spawned_at, /^[0-9]{4}-[0-9]{2}/)) {
    bucket = substr(cur_spawned_at, RSTART, RLENGTH)
  }
  # tag detect: Unicode → 또는 ASCII -> (T-8).
  fb = 0
  if (cur_transcript ~ /\[rate-limit-fallback:sonnet(\xe2\x86\x92|->)opus\]/) {
    fb = 1
  }
  if (bucket != "" && cur_agent != "") {
    printf "%s\t%s\t%d\n", bucket, cur_agent, fb
  }
  cur_agent = ""; cur_spawned_at = ""; cur_transcript = ""
  cur_active = 0
}
{
  line = $0
  # §14 섹션 시작 감지
  if (line ~ /^##[[:space:]]+§14\./) { in_evidence = 1; next }
  if (in_evidence == 0) next
  # §14 끝 = 다음 section header `## §` 또는 EOF
  if (line ~ /^##[[:space:]]+§[0-9]/ && line !~ /§14/) { emit_row(); in_evidence = 0; next }

  # row 경계: `  - lane:` (2 space indent + dash). 새 row 시작 시 직전 row emit.
  if (line ~ /^[[:space:]]+-[[:space:]]+lane:/) {
    emit_row()
    cur_active = 1
    next
  }
  if (cur_active == 0) next
  # field 추출.
  if (line ~ /^[[:space:]]+agent:/) {
    sub(/^[[:space:]]+agent:[[:space:]]*/, "", line)
    cur_agent = trim(line)
    next
  }
  if (line ~ /^[[:space:]]+spawned_at:/) {
    sub(/^[[:space:]]+spawned_at:[[:space:]]*/, "", line)
    cur_spawned_at = trim(line)
    next
  }
  if (line ~ /^[[:space:]]+transcript:/) {
    sub(/^[[:space:]]+transcript:[[:space:]]*/, "", line)
    # transcript value 는 quote 둘러쌀 수 있음 — substring 매치만 하므로 raw 보존.
    cur_transcript = trim(line)
    next
  }
}
END {
  emit_row()
}
' "${STORY_FILES[@]}" > "$SCAN_OUT" 2>/dev/null || true

# --- Aggregation ---
# monthly_data 각 bucket 별 spawn_total + fallback_count 산출.
# Sonnet agent 5종만 분모 — substring 매치 (plugin namespace `(codeforge-*@*)` 무시).
declare -A SPAWN_MAP
declare -A FB_MAP
for b in "${WINDOW_BUCKETS[@]}"; do
  SPAWN_MAP["$b"]=0
  FB_MAP["$b"]=0
done

WINDOW_FIRST="${WINDOW_BUCKETS[0]}"
WINDOW_LAST="${WINDOW_BUCKETS[-1]}"

while IFS=$'\t' read -r bucket agent fb_flag; do
  [[ -z "$bucket" ]] && continue
  # bucket 이 window 안에 있는지 확인 (lexical 비교 OK — YYYY-MM 정렬).
  if [[ "$bucket" < "$WINDOW_FIRST" || "$bucket" > "$WINDOW_LAST" ]]; then
    continue
  fi
  # agent 가 Sonnet 5종에 포함되는지 substring 매치.
  matched=0
  for sa in "${SONNET_AGENTS[@]}"; do
    if [[ "$agent" == *"$sa"* ]]; then matched=1; break; fi
  done
  [[ $matched -eq 0 ]] && continue
  SPAWN_MAP["$bucket"]=$((SPAWN_MAP["$bucket"] + 1))
  if [[ "$fb_flag" == "1" ]]; then
    FB_MAP["$bucket"]=$((FB_MAP["$bucket"] + 1))
  fi
done < "$SCAN_OUT"

# monthly_data array 구성 + 누계.
WIN_TOTAL_SPAWN=0
WIN_TOTAL_FB=0
SAMPLE_SUFFICIENT=true   # monthly AND
MONTHLY_JSON_ITEMS=()

for b in "${WINDOW_BUCKETS[@]}"; do
  m_spawn=${SPAWN_MAP["$b"]}
  m_fb=${FB_MAP["$b"]}
  WIN_TOTAL_SPAWN=$((WIN_TOTAL_SPAWN + m_spawn))
  WIN_TOTAL_FB=$((WIN_TOTAL_FB + m_fb))

  # invariant: fb <= spawn
  if (( m_fb > m_spawn )); then
    echo "[measure-rate-limit-fallback] INVARIANT VIOLATION: fb=$m_fb > spawn=$m_spawn (bucket=$b)" >&2
    exit 1
  fi

  m_sufficient="false"
  if (( m_spawn >= SAMPLE_MIN_PER_MONTH )); then
    m_sufficient="true"
  else
    SAMPLE_SUFFICIENT=false
  fi

  if [[ "$m_sufficient" == "true" ]]; then
    m_rate=$(awk -v fb="$m_fb" -v sp="$m_spawn" 'BEGIN{ if(sp==0) print "null"; else printf "%.4f", (fb/sp)*100 }')
    if [[ "$m_rate" == "null" ]]; then
      m_rate_jq="null"
      m_gate="sample_insufficient"
    else
      m_rate_jq="$m_rate"
      # threshold check (>= 1.0% violation)
      ge=$(awk -v r="$m_rate" -v t="$THRESHOLD_PERCENT" 'BEGIN{ print (r+0 >= t+0) ? "1" : "0" }')
      if [[ "$ge" == "1" ]]; then
        m_gate="violated"
      else
        m_gate="on_track"
      fi
    fi
  else
    m_rate_jq="null"
    m_gate="sample_insufficient"
  fi

  MONTHLY_JSON_ITEMS+=("$(jq -n \
    --arg month "$b" \
    --argjson spawn "$m_spawn" \
    --argjson fb "$m_fb" \
    --argjson rate "$m_rate_jq" \
    --arg gate "$m_gate" \
    '{month:$month, sonnet_spawn_total:$spawn, fallback_count:$fb, rate:$rate, gate_status:$gate}')")
done

# Rolling summary.
if (( WIN_TOTAL_FB > WIN_TOTAL_SPAWN )); then
  echo "[measure-rate-limit-fallback] INVARIANT VIOLATION: window fb=$WIN_TOTAL_FB > spawn=$WIN_TOTAL_SPAWN" >&2
  exit 1
fi

if [[ "$SAMPLE_SUFFICIENT" == "true" ]]; then
  if (( WIN_TOTAL_SPAWN == 0 )); then
    WIN_RATE_JQ="null"
    WIN_GATE="sample_insufficient"
  else
    WIN_RATE=$(awk -v fb="$WIN_TOTAL_FB" -v sp="$WIN_TOTAL_SPAWN" 'BEGIN{ printf "%.4f", (fb/sp)*100 }')
    WIN_RATE_JQ="$WIN_RATE"
    ge=$(awk -v r="$WIN_RATE" -v t="$THRESHOLD_PERCENT" 'BEGIN{ print (r+0 >= t+0) ? "1" : "0" }')
    if [[ "$ge" == "1" ]]; then WIN_GATE="violated"; else WIN_GATE="on_track"; fi
  fi
else
  WIN_RATE_JQ="null"
  WIN_GATE="sample_insufficient"
fi

# Backward-compat 필드: KPI JSON Phase 1 seed schema 와 정합.
# Change Plan §4.2 schema (monthly_data + rolling_summary) + legacy fields (measured_at /
# sonnet_spawn_total / fallback_count / fallback_rate_percent / sample_size_sufficient / gate_status).
# 둘 다 출력 — consumer / lint 양쪽 호환.
NOW_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# monthly_data array JSON build.
MONTHLY_JSON_ARR="$(printf '%s\n' "${MONTHLY_JSON_ITEMS[@]}" | jq -s '.')"

FINAL_JSON="$(jq -n \
  --arg schema "1.0" \
  --arg measured_at "$NOW_ISO" \
  --argjson window_months "$WINDOW_MONTHS" \
  --arg calc "monthly AND sample sufficiency; rolling 3-month UTC half-open [start,end); threshold >= ${THRESHOLD_PERCENT}% strict violation" \
  --argjson monthly "$MONTHLY_JSON_ARR" \
  --argjson win_spawn "$WIN_TOTAL_SPAWN" \
  --argjson win_fb "$WIN_TOTAL_FB" \
  --argjson win_rate "$WIN_RATE_JQ" \
  --arg win_gate "$WIN_GATE" \
  --argjson sample_suff "$([[ "$SAMPLE_SUFFICIENT" == "true" ]] && echo "true" || echo "false")" \
  --argjson partial "$([[ "$PARTIAL_DATA" == "true" ]] && echo "true" || echo "false")" \
  '{
    schema_version: $schema,
    measured_at: $measured_at,
    last_updated: $measured_at,
    window_months: $window_months,
    calculation_method: $calc,
    monthly_data: $monthly,
    rolling_summary: {
      window_total_spawn: $win_spawn,
      window_total_fallback: $win_fb,
      window_rate: $win_rate,
      gate_status: $win_gate
    },
    sonnet_spawn_total: $win_spawn,
    fallback_count: $win_fb,
    fallback_rate_percent: $win_rate,
    sample_size_sufficient: $sample_suff,
    gate_status: $win_gate,
    partial_data: $partial
  }')"

# --- 출력 ---
if [[ -n "$OUT_FILE" ]]; then
  TMP_OUT="$(mktemp -t cfp393-kpi.XXXXXX)" || { echo "[measure-rate-limit-fallback] mktemp failed" >&2; exit 2; }
  printf '%s\n' "$FINAL_JSON" > "$TMP_OUT" || { echo "[measure-rate-limit-fallback] write failed: $TMP_OUT" >&2; exit 2; }
  mkdir -p "$(dirname "$OUT_FILE")" 2>/dev/null || true
  mv "$TMP_OUT" "$OUT_FILE" || { echo "[measure-rate-limit-fallback] mv failed: $OUT_FILE" >&2; exit 2; }
  echo "[measure-rate-limit-fallback] wrote: $OUT_FILE" >&2
else
  printf '%s\n' "$FINAL_JSON"
fi

exit 0
