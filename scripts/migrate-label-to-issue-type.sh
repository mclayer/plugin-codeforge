#!/usr/bin/env bash
# migrate-label-to-issue-type.sh — CFP-2251 / ADR-049 §결정 4 + Amendment 1
#
# type:* label hack → native GitHub Issue Types cutover (additive 재구성).
#
# 매핑 (ADR-049 Amendment 1 — additive):
#   type:epic  → Epic   (org 신설 type)
#   type:story → Story  (org 신설 type)
#   type:bug   → Bug    (기존 org type 재사용)
#   (Audit 은 본 cutover 미포함 — deferred. Task/Feature 는 GitHub 기본, 비대상.)
#
# 모드:
#   --dry-run (기본) : 변경 0. 대상 이슈 목록 + 매핑 + count + 이미-typed skip 수 출력.
#   --apply          : 실 변환 (native Issue Type 부착).
#   --verify         : 변환 후 정합 확인 (type:* label 보유 이슈의 native type 정합 검증).
#
# idempotent: 이미 올바른 native type 보유 이슈는 skip (2회 --apply = 1회 결과).
# batched + rate-limit backoff. shell injection 차단 (이슈 번호 숫자 검증).
#
# API 패턴 (CFP-2251 실측 — story-init.yml L539-559 의 type_id 결함 정정):
#   org type 가용성 = gh api /orgs/{org}/issue-types --jq '.[]|select(.name==<T>)|.id'
#   부착(정정)      = gh api --method PATCH /repos/{owner}/{repo}/issues/{n} -f type=<TypeName>
#   주의: `--field type_id=<id>` 는 REST 가 2xx 반환하나 SILENT 무시됨(type 미설정).
#         실 cutover 첫 --apply 가 487 "성공" 후 --verify 487 MISMATCH 로 발각 → `-f type=<이름>`
#         으로 정정 후 재apply → verify PASS. story-init.yml L556 도 동일 type_id 결함 보유
#         (native 부착 여태 silent 실패) — S4(#2252, story-init.yml owner)에서 정정 대상.
#
# 사용:
#   bash scripts/migrate-label-to-issue-type.sh                       # dry-run, mclayer/plugin-codeforge
#   bash scripts/migrate-label-to-issue-type.sh --apply --batch-size 50
#   bash scripts/migrate-label-to-issue-type.sh --verify
#   bash scripts/migrate-label-to-issue-type.sh --repo OWNER/REPO --org ORG --dry-run
#
set -euo pipefail

# ── 기본값 ────────────────────────────────────────────────────────────────
MODE="dry-run"
REPO="mclayer/plugin-codeforge"
ORG=""                       # 미지정 시 REPO owner 에서 파생
BATCH_SIZE=50
SLEEP_BETWEEN=1              # batch 간 sleep (초) — rate-limit 안전 마진
MAX_BACKOFF=64              # 지수 backoff 상한 (초)

# type:* label → native Issue Type 매핑 (Audit 없음 — deferred).
# bash 3.2 (macOS) 호환 위해 연관배열 대신 case 함수 사용.
map_label_to_type() {
  case "$1" in
    type:epic)  echo "Epic" ;;
    type:story) echo "Story" ;;
    type:bug)   echo "Bug" ;;
    *)          echo "" ;;
  esac
}
MAPPED_LABELS="type:epic type:story type:bug"

# ── 인자 파싱 ──────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) MODE="dry-run"; shift ;;
    --apply)   MODE="apply"; shift ;;
    --verify)  MODE="verify"; shift ;;
    --repo)    REPO="${2:?--repo 인자 누락}"; shift 2 ;;
    --org)     ORG="${2:?--org 인자 누락}"; shift 2 ;;
    --batch-size) BATCH_SIZE="${2:?--batch-size 인자 누락}"; shift 2 ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "ERROR: 알 수 없는 인자 '$1' (--help 참조)" >&2; exit 2 ;;
  esac
done

# org 파생 (REPO = owner/repo)
if [[ -z "$ORG" ]]; then
  ORG="${REPO%%/*}"
fi

# batch-size 숫자 검증
if ! [[ "$BATCH_SIZE" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: --batch-size 는 양의 정수여야 함 (받음: '$BATCH_SIZE')" >&2; exit 2
fi

# Git Bash(MSYS) URL path-rewrite 차단 — gh api leading-slash endpoint 보호.
export MSYS_NO_PATHCONV=1

# ── 사전 점검 ──────────────────────────────────────────────────────────────
command -v gh >/dev/null 2>&1 || { echo "ERROR: gh CLI 미설치" >&2; exit 3; }
gh auth status >/dev/null 2>&1 || { echo "ERROR: gh 미인증 (gh auth login)" >&2; exit 3; }

echo "=========================================================="
echo " migrate-label-to-issue-type.sh"
echo "   mode      : $MODE"
echo "   repo      : $REPO"
echo "   org       : $ORG"
echo "   batch-size: $BATCH_SIZE"
echo "   매핑      : type:epic→Epic / type:story→Story / type:bug→Bug (Audit deferred)"
echo "=========================================================="

# ── org Issue Type ID 조회 (story-init.yml L549-550 패턴) ─────────────────
# 반환: TYPE_ID (없으면 빈 문자열)
resolve_type_id() {
  local type_name="$1"
  gh api "/orgs/${ORG}/issue-types" \
    --jq ".[] | select(.name == \"${type_name}\") | .id" 2>/dev/null || true
}

# 매핑 대상 type 의 org type id 사전 해석 (Epic/Story/Bug)
TYPE_ID_EPIC="$(resolve_type_id Epic)"
TYPE_ID_STORY="$(resolve_type_id Story)"
TYPE_ID_BUG="$(resolve_type_id Bug)"

type_id_for() {
  case "$1" in
    Epic)  echo "$TYPE_ID_EPIC" ;;
    Story) echo "$TYPE_ID_STORY" ;;
    Bug)   echo "$TYPE_ID_BUG" ;;
    *)     echo "" ;;
  esac
}

echo
echo "--- org Issue Type 가용성 (READ-ONLY) ---"
printf "  Epic  : %s\n" "${TYPE_ID_EPIC:-(미생성 — Orchestrator 가 gh api POST 로 신설 필요)}"
printf "  Story : %s\n" "${TYPE_ID_STORY:-(미생성 — Orchestrator 가 gh api POST 로 신설 필요)}"
printf "  Bug   : %s\n" "${TYPE_ID_BUG:-(미생성 — 예상 외: 기존 org Bug 재사용 대상)}"
echo

# apply 모드에서 필요한 type id 부재 시 중단 (graceful — 어떤 type 누락인지 명시).
if [[ "$MODE" == "apply" ]]; then
  MISSING=""
  [[ -z "$TYPE_ID_EPIC"  ]] && MISSING="$MISSING Epic"
  [[ -z "$TYPE_ID_STORY" ]] && MISSING="$MISSING Story"
  [[ -z "$TYPE_ID_BUG"   ]] && MISSING="$MISSING Bug"
  if [[ -n "$MISSING" ]]; then
    echo "ERROR: --apply 불가 — 다음 org Issue Type 미생성:$MISSING" >&2
    echo "       Orchestrator 가 먼저 'gh api /orgs/${ORG}/issue-types -X POST' 로 신설할 것." >&2
    exit 4
  fi
fi

# ── 대상 이슈 수집 (label 별, open+closed 전체) ───────────────────────────
# 출력 형식(stdout 캡처용): "<번호>\t<label>\t<target_type>\t<현재_native_type|null>"
#
# gh issue list --json 은 native Issue Type 필드 미노출 (gh 2.91.0 실측 — issueType 무효).
# 따라서 REST GET /repos/{repo}/issues?labels=...&state=all 사용 — .type 가 inline 노출.
# --paginate 로 415 건도 전수 수집 (per_page 100 자동 페이징).
# 주의: REST issues endpoint 는 PR 도 반환 (PR=issue) → .pull_request != null 제외 의무.
collect_targets() {
  local label target_type
  for label in $MAPPED_LABELS; do
    target_type="$(map_label_to_type "$label")"
    gh api --paginate "repos/${REPO}/issues?labels=${label}&state=all&per_page=100" \
        --jq ".[] | select(.pull_request == null) | \"\(.number)\t${label}\t${target_type}\t\(.type.name // \"null\")\"" \
      2>/dev/null || true
  done
}

# 이슈 번호 숫자 검증 (shell injection 차단)
is_valid_issue_number() {
  [[ "$1" =~ ^[1-9][0-9]*$ ]]
}

# 단일 이슈에 native type 부착 (idempotent — 이미 동일 type 이면 PATCH no-op).
# 정정된 패턴: PATCH /repos/{repo}/issues/{n} -f type=<TypeName> (type_id 는 silent 무시 — 위 헤더 주석).
apply_one() {
  local num="$1" target_type="$2" tid
  # 존재 확인용으로 type id 해석 (org 에 해당 type 없으면 skip).
  tid="$(type_id_for "$target_type")"
  [[ -z "$tid" ]] && { echo "    SKIP #$num (org type 미존재: $target_type)"; return 1; }
  # CFP-2251 실측 수정: REST 이슈 type 설정은 `type=<이름>` 필드. `type_id` 는 2xx 를
  # 반환하나 무시됨(silent no-op — story-init.yml L556 동일 결함, S4 FU). 이름으로 PATCH.
  if gh api --method PATCH "/repos/${REPO}/issues/${num}" \
       -f "type=${target_type}" >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

# 지수 backoff 1회 재시도 (rate-limit / 일시 오류 보호)
apply_one_with_backoff() {
  local num="$1" target_type="$2" backoff=1
  while :; do
    if apply_one "$num" "$target_type"; then return 0; fi
    if (( backoff > MAX_BACKOFF )); then return 1; fi
    echo "    재시도 #$num — ${backoff}s backoff (rate-limit/일시오류)"
    sleep "$backoff"
    backoff=$(( backoff * 2 ))
  done
}

# ── 모드별 실행 ────────────────────────────────────────────────────────────
TARGETS="$(collect_targets)"
TOTAL=0; SKIP_ALREADY=0; TODO=0
declare -i CNT_EPIC=0 CNT_STORY=0 CNT_BUG=0

# 집계 (변경 없이 분류만)
while IFS=$'\t' read -r num label target current; do
  [[ -z "${num:-}" ]] && continue
  TOTAL=$(( TOTAL + 1 ))
  case "$target" in
    Epic)  CNT_EPIC=$(( CNT_EPIC + 1 )) ;;
    Story) CNT_STORY=$(( CNT_STORY + 1 )) ;;
    Bug)   CNT_BUG=$(( CNT_BUG + 1 )) ;;
  esac
  if [[ "$current" == "$target" ]]; then
    SKIP_ALREADY=$(( SKIP_ALREADY + 1 ))
  else
    TODO=$(( TODO + 1 ))
  fi
done <<< "$TARGETS"

case "$MODE" in
  # ── DRY-RUN: 변경 0, 분류 출력 ─────────────────────────────────────────
  dry-run)
    echo "--- 대상 이슈 (DRY-RUN — 변경 0) ---"
    echo "  매핑 분류별 count:"
    printf "    type:epic  → Epic  : %d\n" "$CNT_EPIC"
    printf "    type:story → Story : %d\n" "$CNT_STORY"
    printf "    type:bug   → Bug   : %d\n" "$CNT_BUG"
    echo "  --------------------------------"
    printf "    총 대상            : %d\n" "$TOTAL"
    printf "    이미 native type 보유 (skip 예정) : %d\n" "$SKIP_ALREADY"
    printf "    변환 예정 (TODO)   : %d\n" "$TODO"
    echo
    echo "  (상세 목록 head 20):"
    echo "$TARGETS" | head -20 | awk -F'\t' 'NF{printf "    #%-6s %-12s → %-6s (현재: %s)\n",$1,$2,$3,$4}'
    echo
    echo "  apply 실행 시: bash $0 --apply --batch-size $BATCH_SIZE --repo $REPO"
    ;;

  # ── APPLY: 실 변환 (batched + backoff) ─────────────────────────────────
  apply)
    echo "--- 변환 실행 (--apply) ---"
    OK=0; FAIL=0; SKIPPED=0; PROCESSED=0
    while IFS=$'\t' read -r num label target current; do
      [[ -z "${num:-}" ]] && continue
      if ! is_valid_issue_number "$num"; then
        echo "    SKIP (비정상 번호): '$num'"; FAIL=$(( FAIL + 1 )); continue
      fi
      if [[ "$current" == "$target" ]]; then
        SKIPPED=$(( SKIPPED + 1 )); continue   # idempotent skip
      fi
      if apply_one_with_backoff "$num" "$target"; then
        OK=$(( OK + 1 ))
        echo "    OK   #$num $label → $target"
      else
        FAIL=$(( FAIL + 1 ))
        echo "    FAIL #$num $label → $target"
      fi
      PROCESSED=$(( PROCESSED + 1 ))
      if (( PROCESSED % BATCH_SIZE == 0 )); then
        echo "  --- batch 경계 ($PROCESSED 처리) — ${SLEEP_BETWEEN}s sleep (rate-limit) ---"
        sleep "$SLEEP_BETWEEN"
      fi
    done <<< "$TARGETS"
    echo
    echo "--- apply 결과 ---"
    printf "  변환 성공 : %d\n  skip(이미) : %d\n  실패      : %d\n" "$OK" "$SKIPPED" "$FAIL"
    [[ "$FAIL" -gt 0 ]] && { echo "  WARN: 실패 $FAIL 건 — --verify 로 잔여 확인 후 재실행(idempotent)"; exit 5; }
    echo "  완료. --verify 로 정합 확인 권장."
    ;;

  # ── VERIFY: 변환 정합 확인 ─────────────────────────────────────────────
  verify)
    echo "--- 변환 정합 확인 (--verify) ---"
    MISMATCH=0; MATCH=0
    while IFS=$'\t' read -r num label target current; do
      [[ -z "${num:-}" ]] && continue
      if [[ "$current" == "$target" ]]; then
        MATCH=$(( MATCH + 1 ))
      else
        MISMATCH=$(( MISMATCH + 1 ))
        echo "    MISMATCH #$num $label → 기대 '$target' / 실제 '$current'"
      fi
    done <<< "$TARGETS"
    echo
    printf "  정합   : %d\n  불일치 : %d\n" "$MATCH" "$MISMATCH"
    if [[ "$MISMATCH" -gt 0 ]]; then
      echo "  FAIL: 불일치 $MISMATCH 건 — --apply 재실행(idempotent) 필요"; exit 5
    fi
    echo "  PASS: 전 대상 이슈 native type 정합."
    ;;
esac

echo "=========================================================="
