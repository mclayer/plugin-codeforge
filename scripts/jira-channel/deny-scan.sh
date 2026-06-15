#!/usr/bin/env bash
# CFP-2285 S2 (#2288) — Jira 결정 채널 payload deny-scan (security MUST)
# 인용 출처: ADR-099 Amendment 1 §A1-2 (payload deny-scan hard-block).
#   "Jira 로 송신되는 코멘트 payload 는 송신 전 deny-scan 으로 hard-block 한다
#    (통과 못하면 송신 차단, warning 아님)."
#   대상: secret/credential/token · 절대 파일경로 · full transcript/코드블록 통째.
#   ADR-099 §결정 5 token 금지(stdout/lint/transcript 등장 금지)의 outbound 확장.
#
# 결정론적 순수 텍스트 처리만 수행한다(MCP 호출 없음 — MCP post 는 skill/Orchestrator 담당).
#
# 입력: payload 본문 = stdin 또는 $1(파일 경로).
# 출력/exit:
#   clean        -> exit 0  (stdout/stderr 무출력)
#   위반 검출    -> exit 2  + 위반 패턴 목록 stderr 보고 (post 중단 신호)
#   입력 오류    -> exit 3  (파일 미존재 등)
#
# ADR-061 §결정 1 — bash 우선(복잡 로직 아님, 순수 grep 패턴 매칭).
set -euo pipefail

# ---- 입력 로드 (stdin | $1 파일) ----
if [ "$#" -ge 1 ]; then
  if [ ! -f "$1" ]; then
    echo "deny-scan: 입력 파일 없음: $1" >&2
    exit 3
  fi
  PAYLOAD="$(cat -- "$1")"
else
  PAYLOAD="$(cat -)"
fi

VIOLATIONS=()

# grep -qiE: 대소문자 무시 + 확장정규식. 매치 시 위반 추가.
# `-e "$2"` 로 패턴을 명시 — `-----BEGIN…` 처럼 `-` 로 시작하는 패턴이 grep 옵션으로
# 오인되는 것을 막는다 (FIX P0: PEM 헤더 미적중 원인).
_match() {
  # $1 = 라벨, $2 = 정규식 (대소문자 무시)
  if printf '%s' "$PAYLOAD" | grep -qiE -e "$2"; then
    VIOLATIONS+=("$1")
  fi
}
# 대소문자 구분이 필요한 패턴(예: Bearer / base64 hex)용.
_match_cs() {
  if printf '%s' "$PAYLOAD" | grep -qE -e "$2"; then
    VIOLATIONS+=("$1")
  fi
}

# ---- (A) secret / credential / token 패턴 (ADR-099 §A1-2 / §결정 5) ----
# 주제어 단독 언급("JWT token 검증 로직 A/B?")은 정상 결정 질문이므로 통과시키고,
# 값 할당 형태(secret: <값> / token=<값>)만 차단한다 (FIX P1 false-positive 축소).
_match    "secret-keyword-assignment(secret|token|password|api_key = <값>)" \
          '(secret|token|password|passwd|credential|api[_-]?key|private[_-]?key|access[_-]?key)[[:space:]]*[:=][[:space:]]*[^[:space:]]{8,}'
_match_cs "bearer-token-header" \
          'Bearer[[:space:]]+[A-Za-z0-9._-]+'
_match    "1password-secret-ref(op://)" \
          'op://'
_match    "aws-style-key(AKIA…)" \
          'AKIA[0-9A-Z]{16}'
_match    "github-token(gh[pousr]_…)" \
          'gh[pousr]_[A-Za-z0-9]{20,}'
_match_cs "slack-token(xox[baprs]-…)" \
          'xox[baprs]-[A-Za-z0-9-]+'
_match_cs "google-api-key(AIza…)" \
          'AIza[0-9A-Za-z_-]{35}'
_match_cs "pem-private-key-header" \
          '-----BEGIN[ A-Z]*PRIVATE KEY-----'
_match_cs "jwt-token(eyJ….eyJ….…)" \
          'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'
# 40+ 길이 hex/base64 entropy 블록 (token 누출 휴리스틱).
# 단, 순수 hex git commit SHA(anchor URL `…/commit/<40-hex>` 정상 포함)는 예외 — 차단하면
# 정상 결정 payload 가 막혀 채널 가용성이 떨어진다 (FIX P1 false-positive 축소).
# ERE 에 lookahead 가 없으므로 함수로 분리: 40+ blob 후보를 뽑은 뒤
#   순수 [0-9a-f] hex(=git SHA 형태)면 위반에서 제외, 그 외(대문자·base64 +/= 포함)만 위반.
_entropy_blob_violation() {
  # blob 문자 클래스에서 `/` 제외 — URL 경로 슬래시(`…/commit/<sha>`)가 토큰을 병합해
  # git SHA 가 URL 조각과 한 덩어리로 묶이는 것을 막는다(그래야 순수 hex 예외가 작동). (FIX P1)
  printf '%s' "$PAYLOAD" \
    | grep -oE '[A-Za-z0-9+]{40,}={0,2}' \
    | while IFS= read -r blob; do
        # 순수 소문자 hex(0-9a-f)로만 이뤄진 blob = git SHA 형태 → 예외(미적중).
        if printf '%s' "$blob" | grep -qE '[^0-9a-f]'; then
          echo "HIT"
          break
        fi
      done
}
if [ "$(_entropy_blob_violation)" = "HIT" ]; then
  VIOLATIONS+=("high-entropy-blob(40+ hex/base64, git-SHA 예외)")
fi

# ---- (B) 절대 파일경로 (내부 구조 노출 차단, ADR-099 §A1-2) ----
# Windows drive 경로는 역슬래시(C:\) AND 슬래시(C:/) 둘 다 잡는다 (FIX P0).
# drive letter 앞을 단어경계(비영문)로 제한 — `https:/`·`ftp:/` 같은 URL scheme 의 `s:`/`p:`
# 오인 차단을 막는다(드라이브 문자는 단일 letter, scheme 은 letter 로 끝나는 단어). (FIX P1)
_match_cs "windows-abs-path(C:\\ 또는 C:/)" \
          '(^|[^A-Za-z])[A-Za-z]:[\\/]'
# UNC 경로(\\server\share) 차단 (FIX P0).
# bracket-form [\] 로 리터럴 backslash 표기 — `\\…\\` 형 패턴 끝의 trailing-backslash
# ERE 파싱 오류를 피한다(grep "Trailing backslash"). [\]{2}=두 backslash, [^\]+=비backslash, [\]=한 backslash.
_match_cs "unc-path(\\\\server\\share)" \
          '[\]{2}[^\]+[\]'
_match    "msys-drive-path(/c/ 등)" \
          '(^|[^A-Za-z0-9])/[a-z]/'
# claude-home: foo.claude/ 오인 차단 방지 위해 선행 경계를 영숫자·점 제외 클래스로 (FIX P2).
_match    "claude-home-path(~/.claude)" \
          '(^|[^A-Za-z0-9.])~?/?\.claude/'
# unix-home/abs: 선행 경계를 영숫자 제외 클래스로 넓혀 `:`·`"`·`=`·tab 선행도 cover —
#   file:/Users/… · path "/home/… · path=/c/… 형태 통과를 막는다 (FIX P0).
_match    "unix-home-abs-path(/home//Users//root)" \
          '(^|[^A-Za-z0-9])/(home|Users|root)/'

# ---- (C) full transcript / 코드블록 통째 송신 차단 (휴리스틱) ----
# 코드펜스(```) 블록이 N(=8)줄을 초과하면 코드 통째 송신으로 간주.
# awk: 펜스 토글 카운트로 블록 내부 줄 수 측정.
FENCE_OVERFLOW="$(printf '%s\n' "$PAYLOAD" | awk '
  /^[[:space:]]*```/ { infence = !infence; if (infence) lines=0; next }
  infence { lines++; if (lines > 8) { print "OVER"; exit } }
')"
if [ "$FENCE_OVERFLOW" = "OVER" ]; then
  VIOLATIONS+=("code-fence-overflow(>8줄 코드블록 통째)")
fi
# transcript dump 휴리스틱: agent transcript 마커가 다수 등장.
TRANSCRIPT_MARKS="$(printf '%s\n' "$PAYLOAD" \
  | grep -ciE '^[[:space:]]*(\[?(assistant|user|system|tool_use|tool_result)\]?[:>])' || true)"
if [ "${TRANSCRIPT_MARKS:-0}" -ge 4 ]; then
  VIOLATIONS+=("transcript-dump(role-marker 4+ 줄)")
fi

# ---- 판정 ----
if [ "${#VIOLATIONS[@]}" -gt 0 ]; then
  {
    echo "deny-scan: BLOCKED — Jira 송신 차단 (ADR-099 Amendment 1 §A1-2)"
    for v in "${VIOLATIONS[@]}"; do
      echo "  - 위반: $v"
    done
  } >&2
  exit 2
fi

exit 0
