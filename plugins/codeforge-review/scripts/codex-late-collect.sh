#!/usr/bin/env bash
# CFP-2929 §3.5 E5 — named lead-collect routine (ADR-139 §결정 7(i) 실현)
#
# 호출 형식 (bare-name 금지 — §4.5 helper 호출 형태 계약):
#   "${CLAUDE_PLUGIN_ROOT}/scripts/codex-late-collect.sh" <lane> <round_id>
#
#   <lane>      = closed enum 4종 (requirements-review|design|code|security). 경로 보간 **전** 검증.
#   <round_id>  = LEAD 가 **이번 회차 dispatch 기동 전에 1회 발급**한 회차 유일 토큰
#                 (`^[A-Za-z0-9_-]{8,64}$`). dispatch packet 과 **같은 값**이어야 한다 (§3.0a L3).
#                 ★ **필수 2번째 인자 — 기본값 추정 금지**. default 를 두면 회차 귀속 층(L3)이 통째로 무력화된다.
#
# 무엇을 하는 루틴인가:
#   `codex exec` dispatch 가 남긴 **고정 경로 manifest**(lane 당 1)를 진입점으로, 그 회차의 out.json
#   verdict 를 **재dispatch 없이** 1회 회수한다 (AC-10 / AC-11). 회수 불가·귀속 불명은 전건 fail-closed
#   inconclusive — **미상 rc 로는 절대 PASS 하지 않는다** (§3.4 chief 판정).
#
# ★ auto-wake 장치가 아니다 — LEAD 가 호출하는 **named routine**(discretionary·advisory)이며 타이머가
#   부모를 깨우지 않는다. ADR-139 §결정 7(ii) full auto-wake-parent dispatcher 는 **DEFER 유지**.
#   collect 을 blocking 물리강제로 요구하는 것 = ADR-115 C2 위반 → record-only.
#
# 절차 (8 step, **순서 고정** — §3.5 표가 SSOT):
#   0   인자·환경 검증            → 미충족 = rc=2 usage 종료, **outcome marker 미발화**
#   1   고정경로 manifest read     → 부재 = `outcome=no-dispatch`
#   2   필수 10 키 검증 (schema/lane/round_id 형식/dispatch_start 자릿수/category_enum 실재)
#       → 위반 = **schema 불일치 축** fail-closed
#   2b  회차 귀속 결박(L3)         → `manifest.round_id != argv` = `reason=stale-manifest`
#   3   elapsed = now − dispatch_start (극성 결박 — 비교 술어 rc 0/1/그 외 3분기)
#   4   OP-1 하한 (부재 ∧ 하한 미충족) → `outcome=in-flight`, **재dispatch 금지**
#   5   부재 ∧ 하한 충족           → §3.3 discriminator → 라벨 + inconclusive
#   6   실재 → 신선도 결박(mtime ≥ dispatch_start) → 위반 = `reason=stale-artifact`
#   7   rc stamp 판독(L2, 전체-파일 **바이트** 검증) → AC-6 helper 재검증 → verdict read → 원자적 rename
#
# exit code (본 스크립트 정의 — 설계 미규정분, marker 가 1차 관측 채널):
#   0 = `outcome=consumed` (verdict 획득. **이 값만 획득을 뜻한다**)
#   1 = 그 외 전건 (no-dispatch / in-flight / 각 거부 / helper·codex rc≠0) = **미획득 = inconclusive**
#   2 = usage·환경 오류 (step 0). ★ 이때 outcome marker 를 발화하지 않는다 — 호출 자체가 불성립한 것이지
#       "dispatch 가 없었다"가 아니다. 두 상태를 섞으면 collector 부재가 `no-dispatch` 로 조용히 흡수된다.
#
# 로그 위생 (§7.5): 절대경로 / `$HOME` 전개값 / NONCE / promptfile 본문 / out.json findings 본문을
#   stdout·stderr 어디에도 싣지 않는다. 경로는 **basename 까지만**.
#
# env: `CODEX_REVIEW_ARTIFACT_TTL_SEC` (default 604800 = 7일) **1종만**.
#   ★ iter3 에서 `CODEX_NOT_BEFORE_FLOOR_EPOCH` / `CODEX_CLOCK_SKEW_TOL_SEC` /
#     `CODEX_COLLECT_CAPTURE_EPS_SEC` 3종은 **폐지**됐다 (round_id 동등 비교로 불요). 되살리지 말 것.

# ★ `set -e` 금지 — 모든 실패 경로를 **명시 분기**로 처분한다 (조용한 조기 종료 = 관측 소실).
set -u

# ── 상수 ────────────────────────────────────────────────────────────────────────
readonly MANIFEST_SCHEMA_CONST='codex-dispatch-manifest-v1'
readonly RE_LANE='^(requirements-review|design|code|security)$'
readonly RE_ROUND_ID='^[A-Za-z0-9_-]{8,64}$'
# ★ 자릿수 상한이 계약의 일부 (§4.2) — 상한 없는 `^[0-9]+$` 는 산술 술어에서 rc=2 fall-through(fail-open)를
#   만든다. 10 자리 = 2286년까지. bignum 구조적 배제.
readonly RE_UINT10='^[0-9]{1,10}$'
# OP-1 하한 = dispatch_start + N + K + margin. margin default 30s (§3.6 4계층 시간 전순서).
readonly OP1_MARGIN_SEC=30
# 입력 파일 read 상한 — **bounded degradation** 이지 임의 입력 무해성 단정 아님 (honest ceiling).
readonly MAX_MANIFEST_BYTES=65536
readonly MAX_OUT_JSON_BYTES=$((16 * 1024 * 1024))

# ── marker 발화 (§4.3 어휘 — 이 4 함수 밖에서 marker 문자열을 조립하지 않는다) ──────────
_marker_outcome()  { printf '[codex-late-collect: outcome=%s]\n' "$1"; }          # consumed|in-flight|no-dispatch
_marker_rejected() { printf '[codex-collect-rejected: reason=%s]\n' "$1"; }       # stale-artifact|rc-unknown|stale-manifest|consume-seal-failed
_marker_dialect()  { printf '[codex-outpath-dialect-mangled: basename=%s]\n' "$1"; }
_marker_absent()   { printf '[codex-output-absent-unclassified: stdout_bytes=%s]\n' "$1"; }

_diag() { printf 'codex-late-collect: %s\n' "$*" >&2; }   # 진단 = stderr. 경로는 basename 까지만.

_basename() {   # 경로 basename — `/` 와 `\` 둘 다 구분자로 취급 (manifest 내 두 방언 공존, §3.4)
  local p="$1"
  p=${p##*/}
  p=${p##*\\}
  printf '%s' "$p"
}

_usage() {
  printf 'usage: codex-late-collect.sh <lane> <round_id>\n' >&2
  printf '  <lane>     = requirements-review|design|code|security\n' >&2
  printf '  <round_id> = LEAD 발급 회차 토큰 ^[A-Za-z0-9_-]{8,64}$ (dispatch packet 과 동일 값)\n' >&2
}

# ── step 0: 인자·환경 검증 ───────────────────────────────────────────────────────
# 미충족 = rc=2 즉시 종료 + outcome marker **미발화** (관측을 위조하지 않는다).
if [ "$#" -ne 2 ]; then
  _diag "인자 개수 오류 — 2개 필수 (받은 개수: $#)"
  _usage
  exit 2
fi
LANE="$1"
ARGV_ROUND_ID="$2"

if [[ ! "$LANE" =~ $RE_LANE ]]; then
  _diag "lane 이 closed enum 4종 밖 — 경로 보간 거부"
  _usage
  exit 2
fi
if [[ ! "$ARGV_ROUND_ID" =~ $RE_ROUND_ID ]]; then
  # ★ 기본값 추정 금지 — default 를 두면 회차 귀속 층(L3)이 무력화된다.
  _diag "round_id 형식 위반 — ^[A-Za-z0-9_-]{8,64}\$ 필요 (값은 로그 미기재)"
  _usage
  exit 2
fi
if [ -z "${CLAUDE_PLUGIN_ROOT:-}" ] || [ ! -d "${CLAUDE_PLUGIN_ROOT}" ]; then
  # helper `rc=127 → fail-closed` 규정과 **대칭** — 호출 불성립을 no-dispatch 로 흡수하지 않는다.
  _diag "CLAUDE_PLUGIN_ROOT 미설정 또는 디렉터리 아님 — 호출 불성립(rc=2), no-dispatch 아님"
  exit 2
fi
if [ -z "${HOME:-}" ]; then
  _diag "HOME 미설정 — 아티팩트 디렉터리 도출 불가(rc=2)"
  exit 2
fi

# ── 아티팩트 좌표 (AC-11 2-hop 간접: lane → 고정경로 manifest → ${TS} out.json) ────────
# `<scratch>` = ADR-169 관례 `~/.claude/codeforge-scratch/` (repo 밖 임시 산출물 유일 허용 위치).
# ★ dispatch 측 `CR_DIR="<scratch>/codex-review"` 치환값과 **같은 루트**여야 한다 — 이 일치는
#   collector 가 검증할 수 없는 producer-consumer 결박이다(불일치 = 전건 `no-dispatch`).
# ★ scratch **루트는 열거하지 않는다** (§7.5 — 루트에 무관 비밀 파일 상주). 전용 하위 디렉터리만 본다.
CR_DIR="${HOME}/.claude/codeforge-scratch/codex-review"
MANIFEST="${CR_DIR}/dispatch-${LANE}.json"
RC_STAMP="${CR_DIR}/dispatch-${LANE}.rc"

# ── 유틸: 파일 mtime(epoch) ──────────────────────────────────────────────────────
_file_mtime() {   # $1=경로 ; stdout=epoch ; rc=1 = 판독 실패
  local f="$1" v=''
  v="$(stat -c %Y "$f" 2>/dev/null)" || v=''
  [ -n "$v" ] || v="$(stat -f %m "$f" 2>/dev/null)" || v=''
  [ -n "$v" ] || v="$(date -r "$f" +%s 2>/dev/null)" || v=''
  [ -n "$v" ] || return 1
  printf '%s' "$v"
}

# ── 유틸: 정수 비교 술어 (극성 결박, §3.5 step 3) ────────────────────────────────
# rc 를 **0 / 1 / 그 외** 3분기로 받기 위한 얇은 래퍼. `if [ … ]; then 거부; fi` 형은
# rc≠0(=2, integer expression expected)을 전부 "정상"으로 접는다 → 금지.
_int_lt() { [ "$1" -lt "$2" ]; }   # 0 = $1<$2 / 1 = $1>=$2 / 2 = 술어 오류
_int_ge() { [ "$1" -ge "$2" ]; }   # 0 = $1>=$2 / 1 = $1<$2 / 2 = 술어 오류

# ── 유틸: 최소 JSON 판독 (producer = §3.4 `_json_esc` 2-치환 계약) ────────────────
# ★ 파서가 곧 타입 검사기다 — 패턴 불일치 = 부재와 동일하게 **schema 불일치 축 fail-closed**.
_json_key_count() {   # $1=json, $2=key → 키 리터럴 출현 횟수 (중복 키 fail-closed 용)
  # ★ **순수 bash — 서브프로세스 0**. 종전 `printf | grep -o -F | wc -l | tr` 는 필드당 4 프로세스 ×
  #   필드 10 = 호출당 40 fork 였고, 이 루틴의 주 실행 환경인 **Windows Git Bash 는 fork 를 에뮬레이션**해
  #   호스트 프로세스 경합 시 파이프라인이 통째로 멈추거나 `127`(fork 실패)로 죽는다 (본 워크트리에서
  #   firsthand 관측 — 동일 fixture 가 호스트 부하에 따라 hang / rc=127 / 정상 을 오갔다).
  #   판정 로직은 동일(키 리터럴 출현 횟수)하고 fork 표면만 제거한다.
  local needle="\"$2\"" rest="$1" n=0
  while [ -n "$rest" ]; do
    case "$rest" in
      *"$needle"*) rest="${rest#*"$needle"}"; n=$(( n + 1 )) ;;
      *) break ;;
    esac
  done
  printf '%s' "$n"
}

_json_raw_str() {   # $1=json, $2=key → stdout = **이스케이프된 그대로**의 값 / rc=1 = 부재·형식 위반
  local json="$1" key="$2" re
  re='"'"$key"'"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)"'
  [[ "$json" =~ $re ]] || return 1
  printf '%s' "${BASH_REMATCH[1]}"
}

_json_unesc() {   # $1=raw → stdout = 언이스케이프 값 / rc=1 = producer 계약 밖 escape
  local s="$1" out='' c n
  while [ -n "$s" ]; do
    c=${s:0:1}
    # ★ 오탐 억제(사유) — `'\'` 는 **리터럴 백슬래시 1자**이지 작은따옴표 이스케이프 시도(SC1003 이 가정하는
    #   `'\''` 관용구)가 아니다. JSON escape 선행자를 판별·소비하는 것이 이 루프의 목적이라 백슬래시 자체가
    #   대상 문자다(§3.4 producer 2-치환 계약). 코드 의미 변경 0 → **이 if 블록 한정** 억제.
    # shellcheck disable=SC1003
    if [ "$c" = '\' ]; then
      n=${s:1:1}
      case "$n" in
        '\'|'"') out="$out$n"; s=${s:2} ;;
        # `\n`·`\t`·`\uXXXX` 등은 producer 2-치환 계약(§3.4) 밖 → 조용히 오역하지 않고 fail-closed.
        *) return 1 ;;
      esac
    else
      out="$out$c"; s=${s:1}
    fi
  done
  printf '%s' "$out"
}

_json_str_field() {   # $1=json, $2=key → stdout = 값 / rc=1 = 부재·중복·형식·escape 위반
  local json="$1" key="$2" raw
  [ "$(_json_key_count "$json" "$key")" = "1" ] || return 1
  raw="$(_json_raw_str "$json" "$key")" || return 1
  _json_unesc "$raw" || return 1
}

_json_uint_field() {   # $1=json, $2=key → stdout = 값(`{1,10}` 자리) / rc=1 = 부재·중복·타입·자릿수 위반
  local json="$1" key="$2" re
  [ "$(_json_key_count "$json" "$key")" = "1" ] || return 1
  # 문자열형(`"123"`)은 여는 `"` 때문에 매칭되지 않는다 = 타입 검사 내장.
  # 11 자리 이상은 `[0-9]{1,10}` 뒤 구분자(`,`/`}`) 요구가 깨져 전건 불일치 = 자릿수 상한 강제.
  re='"'"$key"'"[[:space:]]*:[[:space:]]*([0-9]{1,10})[[:space:]]*[,}]'
  [[ "$json" =~ $re ]] || return 1
  printf '%s' "${BASH_REMATCH[1]}"
}

# ── §3.4 rc stamp 전체-파일 **바이트** 검증 (L2 = 프로세스 귀속) ────────────────────
# ★★ 이 함수는 Change Plan §3.4 의 코드를 **그대로** 쓴다. "단순화" 금지 — 그 단순화가 정확히 born-broken 이다:
#   · `read -r t1 t2 rest` 2-토큰 형 → **3-토큰·2행을 조용히 ACCEPT** (firsthand 실측)
#   · `content="$(cat "$1")"` 변형-산출 비교형 → `$()` 가 NUL 을 소거하고 MSYS bash 가 CR 을 흡수해
#     **NUL 후행·NUL 선행·CRLF 3형을 ACCEPT** (firsthand 실측, **플랫폼 의존 판정**)
#   · `grep -P '…\n\z'` 한 줄 대안 → 정상 케이스까지 거부
# 3-검사 분해는 각 검사가 무엇을 배제하는지 1:1 로 대응해, 후속 리팩터가 판별력을 잃는 것을 막는다.
_rc_stamp_ok() {                      # $1 = stamp 경로, $2 = manifest dispatch_id
  local f="$1" line
  [ -f "$f" ] || return 1
  [ "$(LC_ALL=C tr -d '0-9\- \n' < "$f" | wc -c)" -eq 0 ] || return 1
  [ "$(LC_ALL=C wc -l < "$f")" -eq 1 ] || return 1
  [ "$(LC_ALL=C tail -c 1 "$f" | od -An -c | tr -d ' \n')" = '\n' ] || return 1
  IFS= read -r line < "$f"
  [[ "$line" =~ ^([0-9]+-[0-9]+)\ ([0-9]+)$ ]] || return 1
  [ "${BASH_REMATCH[1]}" = "$2" ] || return 1
  RC_STAMP_VALUE="${BASH_REMATCH[2]}"; return 0
}

# ── §11.6 retention sweep — ★ **삭제 축 전용. verdict 후보를 절대 반환하지 않는다** ─────
# glob 금지는 *선택*(verdict artifact 도출) 경로에 대한 금지다. 본 sweep 은 *삭제* 이며
# `.consumed` 접미사 파일만 대상으로 한다. 선택 경로(step 1·7)와 **코드상 분리**돼 있고,
# 이 함수는 stdout 을 내지 않으며 어떤 경로 값도 caller 에게 돌려주지 않는다.
# honest ceiling: collect 루틴이 호출될 때만 도는 **advisory** — bounded 성장은 기계 보증이 아니다.
_ttl_sweep() {
  local ttl now f mt age
  ttl="${CODEX_REVIEW_ARTIFACT_TTL_SEC:-604800}"
  [[ "$ttl" =~ $RE_UINT10 ]] || return 0     # 부정 값 = 아무것도 삭제하지 않음(삭제 축 fail-safe)
  [ -d "$CR_DIR" ] || return 0
  now="$(date +%s 2>/dev/null)" || return 0
  [[ "$now" =~ $RE_UINT10 ]] || return 0
  for f in "$CR_DIR"/*.consumed; do
    [ -f "$f" ] || continue                  # glob 미매치 리터럴 · 디렉터리 · 심볼릭 대상 제외
    mt="$(_file_mtime "$f")" || continue
    [[ "$mt" =~ $RE_UINT10 ]] || continue
    age=$(( now - mt ))
    if _int_lt "$ttl" "$age"; then
      rm -f "$f" 2>/dev/null || true         # 회수 실패는 관측만 — 판정에 영향 없음
    fi
  done
  return 0
}

# ── §3.3 discriminator — mangled 경로 프로브 (1순위) ──────────────────────────────
# MSYS_NO_PATHCONV 하에서 POSIX 경로 `/c/Users/…` 를 받은 Windows 프로그램은 그것을 현재 드라이브
# 루트 기준으로 해석해 `C:\c\Users\…`(= POSIX 표기 `/c/c/Users/…`)에 쓴다 (E-6 그림자 트리 실측).
# ★ **존재 확인만** — read/consume 절대 금지 (판정 입력이지 verdict 채널이 아니다, B-a).
_mangled_probe_path() {   # $1=out_json → stdout = 프로브 후보 경로 / rc=1 = 후보 도출 불가
  local p="$1" drive rest posix
  case "$p" in
    [A-Za-z]:/*|[A-Za-z]:\\*)
      # ★ 오탐 억제(사유) — 정의역이 위 case 패턴으로 **ASCII 드라이브 문자 1자**에 이미 협착돼 있고,
      #   `LC_ALL=C` 가 로케일 독립을 의도적으로 고정한다. `[:upper:]`/`[:lower:]` 제안은 accent·외국어
      #   알파벳 입력을 위한 것인데 그런 입력은 이 분기에 도달할 수 없다 → 치환 이득 0, 의도만 흐려진다.
      # shellcheck disable=SC2018,SC2019
      drive="$(printf '%s' "${p:0:1}" | LC_ALL=C tr 'A-Z' 'a-z')"
      rest="${p:2}"
      rest="${rest//\\//}"
      posix="/${drive}${rest}"
      ;;
    /*)
      # 이미 POSIX 형 — 드라이브는 알 수 없으므로 관례상 `c` 를 가정 (best-effort 프로브).
      drive='c'
      posix="$p"
      ;;
    *) return 1 ;;
  esac
  printf '/%s%s' "$drive" "$posix"
}

# ── AC-6 helper (§4.5 호출 형태 계약) ────────────────────────────────────────────
# bare-name 금지 — **인터프리터 명시 + 플러그인루트 상대 경로**. helper 는 wrapper repo `scripts/lib/`
# 소유이며 배포 표면에 없다(#2934) → consumer 에서는 **부재 = rc=127 → fail-closed** 로 정직 열화한다.
# ★ `|| true` · `|| skip` · `2>/dev/null; rc=0` 금지 (§3.5 불가침 2항 정면 위반).
_python_bin() {
  local p
  p="$(command -v python3 2>/dev/null)" && { printf '%s' "$p"; return 0; }
  p="$(command -v python 2>/dev/null)"  && { printf '%s' "$p"; return 0; }
  return 1
}

# ── TTL sweep = 매 호출 (step 0 통과 후. 선택 경로와 무관한 별 축) ──────────────────
_ttl_sweep

# ── step 1: 고정경로 manifest read — **정확 경로 1개만. glob·newest-선택 절대 금지** ──
if [ ! -f "$MANIFEST" ]; then
  _marker_outcome no-dispatch
  exit 1
fi

manifest_bytes="$(LC_ALL=C wc -c < "$MANIFEST" 2>/dev/null)" || manifest_bytes=''
if [ -z "$manifest_bytes" ] || ! [[ "$manifest_bytes" =~ ^[0-9]+$ ]]; then
  _diag "manifest 크기 판독 실패 — schema 축 fail-closed"
  exit 1
fi
if _int_lt "$MAX_MANIFEST_BYTES" "$manifest_bytes"; then
  _diag "manifest oversize (${manifest_bytes}B > ${MAX_MANIFEST_BYTES}B) — schema 축 fail-closed"
  exit 1
fi
MANIFEST_JSON="$(LC_ALL=C cat "$MANIFEST" 2>/dev/null)" || MANIFEST_JSON=''
if [ -z "$MANIFEST_JSON" ]; then
  _diag "manifest 판독 실패/빈 파일 — schema 축 fail-closed"
  exit 1
fi

# ── step 2: schema const · lane 일치 · round_id 형식 · dispatch_start 자릿수 · category_enum ──
# ★ 필수 필드 **10 키** 중 1+ 부재·타입 불일치 = **전건 fail-closed**(부분 수용 금지).
#   내역 = §4.2 표 **8 행**(= **9 키** — `timeout_n`/`kill_after_k` 가 한 행에 2 키) ⊕ `category_enum` 1 키.
#   ★ `category_enum` 은 아직 **§4.2 표에 미반영**이다(그 표는 8 행 = 9 키 그대로이며 본문은 "필수 8 필드"로
#     적는다) — 본 줄의 10 은 **collector 가 실제로 강제하는 계수**이고, 표 반영은 ArchitectPL 비준 대기다.
#     두 계수를 하나로 뭉뚱그려 "§4.2 가 10 키를 규정한다"고 쓰면 없는 문면을 인용하는 것이 된다.
# ★ 이 축은 **`stale-manifest` 와 섞지 않는다** — 형식 위반 = producer 결함(schema 축) /
#   값 불일치 = 잔재·caller 결함(귀속 축, step 2b).
_schema_reject() { _diag "manifest schema 불일치 축 fail-closed — $1"; exit 1; }

m_schema="$(_json_str_field "$MANIFEST_JSON" schema)"           || _schema_reject "schema 필드 부재/형식"
[ "$m_schema" = "$MANIFEST_SCHEMA_CONST" ]                      || _schema_reject "schema const 불일치"

m_lane="$(_json_str_field "$MANIFEST_JSON" lane)"               || _schema_reject "lane 필드 부재/형식"
[[ "$m_lane" =~ $RE_LANE ]]                                     || _schema_reject "lane 값이 closed enum 밖"
[ "$m_lane" = "$LANE" ]                                         || _schema_reject "lane 인자-필드 불일치"

m_dispatch_id="$(_json_str_field "$MANIFEST_JSON" dispatch_id)" || _schema_reject "dispatch_id 필드 부재/형식"
[ -n "$m_dispatch_id" ]                                         || _schema_reject "dispatch_id 빈 값"

m_round_id="$(_json_str_field "$MANIFEST_JSON" round_id)"       || _schema_reject "round_id 필드 부재/형식"
[[ "$m_round_id" =~ $RE_ROUND_ID ]]                             || _schema_reject "round_id 형식 위반(producer 결함 — stale-manifest 아님)"

m_out_json="$(_json_str_field "$MANIFEST_JSON" out_json)"       || _schema_reject "out_json 필드 부재/형식"
[ -n "$m_out_json" ]                                            || _schema_reject "out_json 빈 값"

# ★ `promptfile` 은 **실재 검증만** 하고 **경로로 열지 않는다** — audit 전용 필드이며 미정규화(POSIX 가능)다.
#   열면 §3.1 이 닫은 경로 방언 축이 재개봉된다 (§3.4 dialect 비대칭은 의도적).
m_promptfile="$(_json_str_field "$MANIFEST_JSON" promptfile)"   || _schema_reject "promptfile 필드 부재/형식"
[ -n "$m_promptfile" ]                                          || _schema_reject "promptfile 빈 값"

# ★ `category_enum` = **필수 필드**(§4.2 승격 — DeveloperPL 판정, ArchitectPL 비준 대기). "additive 선택
#   필드" 아니다. 승격 근거 2:
#   ① step 7 의 AC-6 helper 는 인자를 **정확히 3개** 요구한다(`len(args) != 3 → rc=2` setup error) —
#      collector argv 는 `<lane> <round_id>` 2개뿐이라 3번째 인자의 유일 조달처가 이 필드다. 즉 step 7
#      **의무를 완료하는 데 없으면 안 되는 입력** = 정의상 필수지 선택이 아니다.
#   ② 부재 검사를 step 7 에 두면 **결함이 은폐된다** — `category_enum` 부재 ∧ out.json 부재 ∧ OP-1 하한
#      미충족 회차는 step 4 에서 `outcome=in-flight` 로 빠져나가 producer 계약 결함이 전혀 발화하지 않는다
#      (firsthand 실측). 필수 필드 부재는 회차 진행 상태와 무관하게 **즉시** 드러나야 한다.
#   ★ 축 = **schema 불일치 축**(필수 필드 부재·타입 불일치 = producer 결함). `rc-unknown`(rc stamp 판독 축)·
#     `stale-manifest`(값 불일치 = 귀속 축)와 **섞지 않는다** — §4.3 4 reason 의 축 disjoint 규율.
#   ★ `-n` 검사가 load-bearing — 빈 문자열을 helper 에 넘기면 allowed set 이 공집합이 되고, `findings: []`
#     인 out.json 은 검사 ⑤ 를 **공허 참으로 통과**한다(= 판정 입력 위조와 등가의 fail-open).
m_category_enum="$(_json_str_field "$MANIFEST_JSON" category_enum)" || _schema_reject "category_enum 필드 부재/형식"
[ -n "$m_category_enum" ]                                           || _schema_reject "category_enum 빈 값"

m_dispatch_start="$(_json_uint_field "$MANIFEST_JSON" dispatch_start)" || _schema_reject "dispatch_start 부재/타입/자릿수(^[0-9]{1,10}\$)"
m_timeout_n="$(_json_uint_field "$MANIFEST_JSON" timeout_n)"           || _schema_reject "timeout_n 부재/타입/자릿수"
m_kill_after_k="$(_json_uint_field "$MANIFEST_JSON" kill_after_k)"     || _schema_reject "kill_after_k 부재/타입/자릿수"

# ── step 2b: 회차 귀속 결박 (L3) — **문자열 동등 비교 1개. 시계·순서·EPS 추론 0** ──────
if [ "$m_round_id" != "$ARGV_ROUND_ID" ]; then
  _marker_rejected stale-manifest
  exit 1
fi

# ── step 3: elapsed = now − dispatch_start (극성 결박) ───────────────────────────
NOW="$(date +%s 2>/dev/null)" || NOW=''
if ! [[ "$NOW" =~ $RE_UINT10 ]]; then
  _diag "현재 시각 판독 실패/형식 위반 — 산술 투입 거부(fail-closed)"
  exit 1
fi
# ★ 두 피연산자 모두 `^[0-9]{1,10}$` 선검사를 통과한 값만 투입한다. bare-name 산술은 빈값·비정수를
#   **0 으로 흡수**해 `elapsed = now` 를 만들고 OP-1 하한을 항상 충족시킨다(fail-open) — 선검사가 그 방어다.
ELAPSED=$(( NOW - m_dispatch_start ))
OP1_LOWER_BOUND=$(( m_timeout_n + m_kill_after_k + OP1_MARGIN_SEC ))

# ── step 4/5: out.json 부재 경로 ────────────────────────────────────────────────
if [ ! -f "$m_out_json" ]; then
  # step 4 — OP-1 하한. 비교 술어 rc 를 0/1/그 외 3분기로 받는다.
  _int_lt "$ELAPSED" "$OP1_LOWER_BOUND"; cmp_rc=$?
  case "$cmp_rc" in
    0)
      # 하한 미충족 = INV-L3 3-state 의 "미획득"이지 stall 아님. ★ **재dispatch 금지**.
      _marker_outcome in-flight
      exit 1
      ;;
    1) : ;;   # 하한 충족 → step 5
    *)
      # 선검사를 통과했다면 rc=2 는 발생하지 않아야 한다 — 발생 = 계약 위반이므로 조용히 통과시키지 않는다.
      _diag "OP-1 비교 술어 rc=${cmp_rc} — 계약 위반, 명시 fail-closed 거부"
      exit 1
      ;;
  esac

  # step 5 — §3.3 discriminator. ★ collect 시점에는 dispatch stdout/stderr 가 관측면에 없다
  #   (2순위 stderr signature · 3순위 stdout 바이트 수는 dispatch 시점 전용) → 1순위 프로브만 가용.
  probe="$(_mangled_probe_path "$m_out_json")" || probe=''
  if [ -n "$probe" ] && [ -e "$probe" ]; then
    _marker_dialect "$(_basename "$m_out_json")"
  else
    # ★ stdout 미관측 sentinel `-1` — 실측 `0`(§3.3 상 "상류 crash 강신호")과 **구별**한다.
    #   관측하지 않은 값을 0 으로 적으면 이 Story 가 진단한 "허구 관측" class 의 재생산이다.
    #   ★ **설계 미규정** — §4.3 은 payload 를 "정수" 로만 규정하고 미관측 값 공간을 정하지 않았다.
    #     `-1` 은 잠정 채택이며 **ArchitectPL 판정 대기**(DeveloperPL 에스컬레이션 목록).
    _marker_absent -1
  fi
  exit 1
fi

# ── step 6: 신선도 결박 (mtime(out.json) ≥ dispatch_start) ───────────────────────
# ★ 자기참조 한계 — 기준점을 manifest 에서 읽으므로 **manifest 자신의 staleness 는 검출 불가**.
#   그 축은 step 2b 전담. 이 검사가 실제로 발화하는 셀은 좌표가 겹치는 C9 뿐이다.
out_mtime="$(_file_mtime "$m_out_json")" || out_mtime=''
if ! [[ "$out_mtime" =~ $RE_UINT10 ]]; then
  # 판정 입력(mtime) 판독 실패 — §4.3 4 reason 어느 축에도 속하지 않는다. 오귀속하지 않고 조용히
  # 통과시키지도 않는다: 진단만 남기고 fail-closed.
  _diag "out.json mtime 판독 실패 — 신선도 판정 불가, fail-closed(소비 0)"
  exit 1
fi
_int_ge "$out_mtime" "$m_dispatch_start"; cmp_rc=$?
case "$cmp_rc" in
  0) : ;;                                   # 신선
  1) _marker_rejected stale-artifact; exit 1 ;;
  *) _diag "신선도 비교 술어 rc=${cmp_rc} — 계약 위반, 명시 fail-closed 거부"; exit 1 ;;
esac

# ── step 7: rc stamp 판독(L2) → AC-6 helper 재검증 → verdict read → 원자적 rename ──
# 부재 / **프로세스** 귀속 불일치 / 토큰 수 이상(1·3-토큰) / 2행 이상 / 개행 미종료 / 선행 공백 /
# NUL·CR 등 허용 외 바이트 / 2nd 비정수 → **전건** `rc-unknown` fail-closed.
RC_STAMP_VALUE=''
if ! _rc_stamp_ok "$RC_STAMP" "$m_dispatch_id"; then
  _marker_rejected rc-unknown
  exit 1
fi
CODEX_RC="$RC_STAMP_VALUE"
# `_rc_stamp_ok` 의 2nd 토큰 정규식은 `[0-9]+`(상한 없음)이라 bignum 이 통과할 수 있고, 그 값은
# `[ "$CODEX_RC" -eq 0 ]` 에서 rc=2 fall-through(fail-open)를 만든다 → 자릿수 상한을 여기서 결박한다.
# (§3.4 함수 본문은 verbatim 유지 — 검증을 함수 밖에서 **추가**한다.)
if ! [[ "$CODEX_RC" =~ $RE_UINT10 ]]; then
  _marker_rejected rc-unknown
  exit 1
fi

# AC-6 helper 재검증 — inline 경로와 **동일 판정 authority 1개**(같은 helper·같은 verdict-read form).
HELPER_SCHEMA="${CLAUDE_PLUGIN_ROOT}/schemas/codex-review-output-schema-v1.json"
HELPER_PY="${CLAUDE_PLUGIN_ROOT}/../../scripts/lib/check_codex_review_output_schema.py"
# helper 3번째 인자 `<category_enum>` 은 **packet 유래**이며 argv(2개)로는 오지 않는다 → manifest
# **필수 필드** `category_enum`(§4.2 승격 — DeveloperPL 판정, ArchitectPL 비준 대기)에서 받는다.
# producer(dispatch 템플릿)와 consumer(본 스크립트)는 같은 plugin·같은 버전으로 함께 배포되므로 skew 가
# 구조적으로 불가능하다 → `schema` const 무변경(제거·의미 변경이 아니므로 새 const 의무 미발동).
#   ★ **여기서 다시 파싱하지도, 부재를 다시 검사하지도 않는다** — step 2 가 실재·non-empty 를 이미 보증한다.
#     종전의 `if [ -z "$CATEGORY_ENUM" ]` fail-closed 분기는 승격으로 **도달 불가**가 됐고, 도달 불가 분기는
#     어떤 테스트로도 falsify 할 수 없는 "보호한다는 주장"만 남긴다(= 검사연극). 같은 필드를 2회 파싱하는
#     것 또한 두 판정이 갈릴 수 있는 drift 표면이다. 단일 파싱·단일 강제점(step 2)으로 좁힌다.
#   ★ 날조 금지는 그대로 유효 — 값은 manifest 원본 그대로이며, 부재 시 **임의 값 생성 없이** step 2 에서
#     schema 축 fail-closed 로 종료된다(helper 검사 ⑤ 의 판정 입력을 위조하지 않는다).

HELPER_RC=0
if [ ! -f "$HELPER_PY" ]; then
  # 배포본 helper 부재(#2934) = 정직한 열화. `rc=127 → fail-closed` 성질 보존 — 우회 금지.
  _diag "AC-6 helper 부재 — rc=127 fail-closed(소비 0). 우회(|| true 등) 금지"
  HELPER_RC=127
else
  PYTHON_BIN="$(_python_bin)" || PYTHON_BIN=''
  if [ -z "$PYTHON_BIN" ]; then
    _diag "python 인터프리터 부재 — helper 실행 불가, rc=127 fail-closed"
    HELPER_RC=127
  else
    "$PYTHON_BIN" "$HELPER_PY" "$m_out_json" "$HELPER_SCHEMA" "$m_category_enum" >&2
    HELPER_RC=$?
  fi
fi

if [ "$CODEX_RC" -eq 0 ] && [ "$HELPER_RC" -eq 0 ]; then
  # verdict 정본 = out.json `verdict` 필드 (exit→severity 매핑 금지, I-7).
  out_bytes="$(LC_ALL=C wc -c < "$m_out_json" 2>/dev/null)" || out_bytes=''
  if [ -z "$out_bytes" ] || ! [[ "$out_bytes" =~ ^[0-9]+$ ]] || _int_lt "$MAX_OUT_JSON_BYTES" "$out_bytes"; then
    _diag "out.json 크기 판독 실패/상한 초과 — verdict read 거부(fail-closed)"
    exit 1
  fi
  OUT_JSON_TEXT="$(LC_ALL=C cat "$m_out_json" 2>/dev/null)" || OUT_JSON_TEXT=''
  VERDICT="$(_json_str_field "$OUT_JSON_TEXT" verdict)" || VERDICT=''
  if [ -z "$VERDICT" ]; then
    _diag "out.json verdict 필드 판독 실패 — 소비 0(fail-closed)"
    exit 1
  fi
  # ★ 원자적 rename = at-most-once 봉인. **rc 검사 의무** — 미검사 시 §11.6 "2회 소비 구조적 불가능"
  #   선언이 조용히 거짓이 된다. 실패 = verdict 를 읽었더라도 재소비 가능 상태로 남기지 않는다.
  # ★ 목적지가 **디렉터리**면 `mv -f a b` 는 실패하지 않고 `b/a` 로 **이동**한다 (firsthand 실측 —
  #   Git Bash coreutils). 그 경로는 "동일 디렉터리 rename, 하위 디렉터리 이동 금지"(§3.5 아티팩트 수명)를
  #   위반하고 `*.consumed` TTL sweep 사각으로 빠지므로, rc 검사만으로는 봉인 실패가 관측되지 않는다
  #   → 좌표 선점을 **봉인 실패(트랜잭션 축)** 로 명시 처분한다. (`mv -T` 는 GNU 전용이라 미사용.)
  if [ -d "${m_out_json}.consumed" ]; then
    _marker_rejected consume-seal-failed
    exit 1
  fi
  if ! mv -f "$m_out_json" "${m_out_json}.consumed"; then
    _marker_rejected consume-seal-failed
    exit 1
  fi
  printf 'verdict=%s\n' "$VERDICT"
  _marker_outcome consumed
  exit 0
fi

# codex rc≠0 ∨ helper rc≠0 = inline 경로와 동일 처분 (fail-closed inconclusive, PASS 승격 0).
_diag "소비 조건 미충족 (codex_rc=${CODEX_RC}, helper_rc=${HELPER_RC}) — inconclusive, 소비 0"
exit 1
