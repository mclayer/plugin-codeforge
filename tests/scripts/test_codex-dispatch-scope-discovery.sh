#!/usr/bin/env bash
# tests/scripts/test_codex-dispatch-scope-discovery.sh
# CFP-2929 AC-13 — "모든 codex exec dispatch 발화가 lint 스캔 사정권 안" (**discovery 기반 차집합 0**).
#
# 계약 SSOT = Change Plan cfp-2929 §8.0 AC-13 행(L1034) + §8.2 mutation **M-S**(L1218) + §5.1 B-8.
#
# ★★ B-8 (본 test 의 존재 이유) — **파일 목록 하드코딩 = born-stale = 이 AC 가 막으려는 결함의 재생산**.
#   본 Story 가 고치는 원 결함 = "제2 dispatch 표면이 영구 미탐지". 그 표면을 test 가 *열거* 해서
#   찾는다면, 신규 표면은 열거에 없으므로 test 도 못 찾는다 = 결함을 그대로 복제한다.
#   → 양변을 **구조적으로 독립** 하게 만든다:
#       discovery side = repo **전수 walk** (`--list-dispatch-surfaces` — 실 파일시스템 스캔)
#       scope   side = lint **설정값** (`--list-scope-dirs` — 트리와 무관한 상수)
#     ★★ 두 변이 같은 목록에서 나오면 tautology 이고 M-S 가 **생존** 한다. 아래 A13-6 이 그
#        독립성을 적극 반증 시도(사정권 밖 신규 표면이 discovery 에 실제로 잡히는가)로 결박한다.
#
# ★ 제외 선언 (사정권 하드코딩과 다르다 — **가시적 선언**이라 허용): 아래 `EXCLUSIONS` 는
#   "production dispatch 가 아니라 lint 를 RED 로 만들기 위한 **음성 fixture 캐리어**" 를 뺀다.
#   조용한 필터가 되지 않도록 3 결박:
#     (1) 각 항목에 **제외 사유를 인라인 주석**으로 적는다.
#     (2) A13-2 가 "제외 항목은 **실제로 discovery 에 잡혀야** 한다" 를 assert — 사유가 사라진
#         stale 제외는 RED 가 되어 목록이 자동으로 줄어든다 (제외 목록의 무한 팽창 차단).
#     (3) 제외 후 남은 production 표면 수 하한(A13-3) — 전부 제외해 vacuous 로 만드는 경로 차단.
#
# ★ 검사연극 금지: `|| true` · `|| skip` · 조건부 기대 0건. 전 행 단일 기대.
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LINT_PY="$REPO_ROOT/scripts/lib/check_codex_companion_timeout_presence.py"

PASS=0
FAIL=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

ok()  { echo "✓ PASS: $1"; PASS=$((PASS+1)); }
bad() { echo "✗ FAIL: $1"; shift; for l in "$@"; do echo "    $l"; done; FAIL=$((FAIL+1)); }
assert_eq() {
  local name="$1" actual="$2" expected="$3" desc="$4"
  if [ "$actual" = "$expected" ]; then ok "$name — $desc [관측: $actual]"
  else bad "$name" "기대: $expected" "실제: $actual" "설명: $desc"; fi
}

# 안전 count (ADR-060 Amd22 정합 — `grep -c` 는 0 매칭 시 exit 1 이지만 그 exit 는 pass/fail 신호가
#   아니라 **count 표현 수단** 이다. 실 pass/fail 은 반환 count 를 근접 assert 가 gating).
#   ★ `$( … || true)` 형은 쓰지 않는다 — 실패 시 **빈 문자열**을 만들어 후속 산술·비교를
#     `integer expression expected` 로 깨뜨린다(관측 불가 상태 생성). 명시 0 대입으로 고정.
nlines() { local n; n=$(grep -c . "$1" 2>/dev/null) || n=0; printf '%s' "$n"; }
hits()   { local n; n=$(grep -cE "$1" "$2" 2>/dev/null) || n=0; printf '%s' "$n"; }

PYBIN=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then PYBIN="$c"; break; fi
done

# ═══════════════════════════════════════════════════════════════════════════
# §0 setup guard — 양변 인터페이스가 실재하는가 (부재 = 전 케이스 vacuous 위장)
# ═══════════════════════════════════════════════════════════════════════════
echo "═══════════════════════════════════════════════════════════════════════════"
echo " §0 setup guard — discovery/scope 양변 인터페이스"
echo "═══════════════════════════════════════════════════════════════════════════"

if [ -z "$PYBIN" ]; then
  bad "S0-0 python 인터프리터" "python3/python 모두 부재 — AC-13 판정 불가"
  echo "PASS: $PASS / FAIL: $FAIL"; exit 1
fi
ok "S0-0 python 인터프리터 ($PYBIN)"

if [ ! -f "$LINT_PY" ]; then
  bad "S0-1 lint SSOT 존재" "부재: $LINT_PY"
  echo "PASS: $PASS / FAIL: $FAIL"; exit 1
fi
ok "S0-1 lint SSOT 존재 ($LINT_PY)"

# ★ 개행 정규화 의무 (Windows 실측): Windows Python 의 `print` 는 text-mode 개행 변환으로 **CRLF** 를
#   내보낸다 `[verified: python3 … --list-scope-dirs | od -c → p l u g i n s \r \n, Git Bash/MSYS]`.
#   CR 을 안 벗기면 순수 bash `case` prefix 매칭이 `plugins\r` 로 전건 미스매치가 되어 **차집합이
#   전부 '사정권 밖'** 으로 뒤집힌다(= 상시-RED). MSYS grep 은 CR 을 관용해 통과하므로 **검사기마다
#   판정이 갈리는** 형태라 더 위험하다. → 기계 인터페이스 소비 시점에서 1회 정규화한다.
#   ★ 이것은 fail-open 이 아니라 플랫폼 개행 산출물의 정규화다 (판정 자체를 완화하지 않는다).
run_lint() {   # $1 = 실행 cwd, 나머지 = argv → stdout(개행 정규화). rc = python rc (pipefail).
  local dir="$1"; shift
  ( cd "$dir" && "$PYBIN" "$LINT_PY" "$@" ) | tr -d '\r'
}

SCOPE_F="$WORK/scope.txt"
DISC_F="$WORK/discovery.txt"
src=0; run_lint "$REPO_ROOT" --list-scope-dirs         > "$SCOPE_F" 2>"$WORK/scope.err" || src=$?
drc=0; run_lint "$REPO_ROOT" --list-dispatch-surfaces  > "$DISC_F"  2>"$WORK/disc.err"  || drc=$?
assert_eq "S0-2 --list-scope-dirs rc" "$src" "0" "사정권 side 기계 인터페이스 (bash 재구현 = drift 표면 → 금지)"
assert_eq "S0-3 --list-dispatch-surfaces rc" "$drc" "0" "discovery side 기계 인터페이스 (동상)"

SCOPE_N=$(nlines "$SCOPE_F")
DISC_N=$(nlines "$DISC_F")
if [ "$SCOPE_N" -ge 1 ]; then
  ok "S0-4 사정권 비어있지 않음 ($SCOPE_N 항목: $(tr '\n' ' ' < "$SCOPE_F"))"
else
  bad "S0-4 사정권 비어있지 않음" "0 항목 — 사정권이 비면 차집합 검사가 '전부 밖' 이거나 무의미해진다"
fi
if [ "$DISC_N" -ge 1 ]; then
  ok "S0-5 discovery 비어있지 않음 ($DISC_N 표면)"
else
  bad "S0-5 discovery 비어있지 않음" "0 표면 — hollow (스캐너가 아무것도 못 찾으면 차집합 0 은 무의미)"
fi

# ── 사정권 side 의 **트리 비의존성** 실증 (양변 독립의 절반) ─────────────────────────
# 사정권은 설정 상수이므로 어느 트리에서 물어도 같아야 한다. 트리에서 파생되면 discovery 와
# 같은 원천이 되어 tautology 가 된다.
mkdir -p "$WORK/emptytree"
srx=0; run_lint "$WORK/emptytree" --list-scope-dirs > "$WORK/scope_empty.txt" 2>/dev/null || srx=$?
if [ "$srx" -eq 0 ] && diff -q "$SCOPE_F" "$WORK/scope_empty.txt" >/dev/null; then
  ok "S0-6 사정권 side 트리 비의존 (빈 트리에서도 동일 출력) — discovery 와 원천이 다름"
else
  bad "S0-6 사정권 side 트리 비의존" "빈 트리에서 출력이 달라짐(rc=$srx) — 사정권이 트리 파생 = 양변 tautology 위험"
fi

# ═══════════════════════════════════════════════════════════════════════════
# §1 실 repo 차집합 0 (AC-13 본 판정)
# ═══════════════════════════════════════════════════════════════════════════
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " §1 실 repo — discovery − 사정권 − 제외선언 = ∅"
echo "═══════════════════════════════════════════════════════════════════════════"

# ★ 제외 선언 (사유 필수 — (1) 결박). 늘어나면 이 배열이 그대로 눈에 띈다.
EXCLUSIONS=(
  # lint 자신의 discriminating self-test 캐리어. 안에 든 `timeout … codex exec …` 리터럴은
  # **lint 를 RED 로 만들기 위한 음성 fixture** 이며 실행되는 production dispatch 가 아니다.
  # 사정권에 넣으면 상시-RED (fixture 가 곧 위반이므로) — 그래서 제외한다.
  "tests/scripts/test_check-codex-companion-timeout-presence.sh"
)

EXCL_F="$WORK/excl.txt"
printf '%s\n' "${EXCLUSIONS[@]}" > "$EXCL_F"

# 차집합 = discovery − (사정권 디렉터리 prefix) − (제외 선언).
# ★ 사정권은 **디렉터리 prefix** 이지 파일 목록이 아니므로 `comm` 이 아니라 prefix 매칭이 필요하다.
subtract() {   # stdin = 경로 목록, $1 = 사정권 파일, $2 = 제외 파일 → stdout = 남은 것
  local scope_file="$1" excl_file="$2" p d hit
  while IFS= read -r p; do
    [ -n "$p" ] || continue
    hit=0
    while IFS= read -r d; do
      [ -n "$d" ] || continue
      case "$p" in "$d"|"$d"/*) hit=1; break;; esac
    done < "$scope_file"
    if [ "$hit" -eq 0 ] && grep -Fxq -- "$p" "$excl_file"; then hit=1; fi
    [ "$hit" -eq 1 ] || printf '%s\n' "$p"
  done
}

DIFF_F="$WORK/diff.txt"
subtract "$SCOPE_F" "$EXCL_F" < "$DISC_F" > "$DIFF_F"
DIFF_N=$(nlines "$DIFF_F")
if [ "$DIFF_N" -eq 0 ]; then
  ok "A13-1 실 repo 차집합 0 — 모든 dispatch 발화가 스캔 사정권 안 (또는 명시 제외)"
else
  bad "A13-1 실 repo 차집합 0" "사정권 밖 dispatch 표면 $DIFF_N 건:" \
      "$(sed 's/^/      · /' "$DIFF_F")" \
      "→ 사정권(DEFAULT_SCAN_DIRS) 확대 또는 (음성 fixture 라면) EXCLUSIONS 에 사유와 함께 선언"
fi

# (2) 결박 — 제외 항목은 **실제로 discovery 에 잡혀야** 한다. 안 잡히면 사유가 소멸한 stale 제외.
EXCL_STALE=""
for e in "${EXCLUSIONS[@]}"; do
  grep -Fxq -- "$e" "$DISC_F" || EXCL_STALE="$EXCL_STALE $e"
done
if [ -z "$EXCL_STALE" ]; then
  ok "A13-2 제외 선언 전건이 실 discovery 에 실재 (stale 제외 0) — 목록 자동 수축"
else
  bad "A13-2 제외 선언 stale" "discovery 에 없는 제외 항목:$EXCL_STALE" \
      "제외 사유가 소멸했다 — EXCLUSIONS 에서 삭제하라 (조용한 필터 축적 차단)"
fi

# (3) 결박 — 제외 후 production 표면 하한. 전부 제외해 vacuous 로 만드는 경로 차단.
EXCL_N=$(nlines "$EXCL_F")
PROD_N=$(( DISC_N - EXCL_N ))
if [ "$PROD_N" -ge 2 ]; then
  ok "A13-3 hollow guard — 제외 후 production dispatch 표면 $PROD_N 건 (≥2)"
else
  bad "A13-3 hollow guard" "제외 후 production 표면 $PROD_N 건 < 2" \
      "차집합 0 이 '검사할 게 없어서' 인지 '전부 사정권 안이라서' 인지 구분 불가 = hollow"
fi

# ═══════════════════════════════════════════════════════════════════════════
# §2 M-S — 사정권 밖 신규 dispatch 표면 주입 → 차집합 ≥1 (RED 실증)
# ═══════════════════════════════════════════════════════════════════════════
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " §2 M-S — 신규 dispatch 표면 주입 시 RED 가 실제로 나는가"
echo "═══════════════════════════════════════════════════════════════════════════"
# 합성 루트에서 구동한다 (실 repo 를 오염시키지 않는다). 합성 루트는 사정권 디렉터리(`plugins`)와
# 사정권 **밖** 디렉터리를 함께 갖는다.
# ★ 주입 경로 `newlane/agents/PeerDispatchAgent.md` 는 lint 소스 어디에도 등장하지 않는 이름이다
#   (A13-6 이 그 사실을 assert) — 하드코딩 목록이었다면 discovery 가 이 파일을 **영원히 못 찾고**
#   M-S 가 생존한다. 그 생존이 곧 B-8 위반 검출이다.
DISPATCH_LINE='timeout --kill-after=30 300 codex exec -s read-only --output-schema s.json -o "$OUT_JSON" - < p.md'
NORM_LINE='OUT_JSON="$(cygpath -m "$OUT_JSON")"'
ENV_L1='export LC_ALL=C.UTF-8'
ENV_L2='export PYTHONUTF8=1'

mk_surface() {   # $1 = 파일 경로
  mkdir -p "$(dirname "$1")"
  printf '%s\n%s\n%s\n%s\n' "$ENV_L1" "$ENV_L2" "$NORM_LINE" "$DISPATCH_LINE" > "$1"
}

SYN="$WORK/syn"
mk_surface "$SYN/plugins/codeforge-review/agents/CodexReviewAgent.md"   # 사정권 안
mk_surface "$SYN/newlane/agents/PeerDispatchAgent.md"                    # ★ M-S: 사정권 밖

MSRC=0; run_lint "$SYN" --list-dispatch-surfaces . > "$WORK/syn_disc.txt" 2>/dev/null || MSRC=$?
assert_eq "A13-4a 합성 루트 discovery rc" "$MSRC" "0" "M-S 관측 전제"
EMPTY_EXCL="$WORK/empty_excl.txt"; : > "$EMPTY_EXCL"
subtract "$SCOPE_F" "$EMPTY_EXCL" < "$WORK/syn_disc.txt" > "$WORK/syn_diff.txt"
MS_DIFF="$(tr '\n' ',' < "$WORK/syn_diff.txt")"
assert_eq "A13-4 M-S 변이 → 차집합 == 주입 표면 정확히 1건 [KILL]" \
  "$MS_DIFF" "newlane/agents/PeerDispatchAgent.md," \
  "사정권 밖 신규 dispatch 표면이 즉시 검출된다 — 하드코딩 목록이면 이 변이가 생존(= B-8 위반)"

# negative control — 주입분 제거 시 차집합 0 (상시-RED 가 아님을 결박)
rm -rf "$SYN/newlane"
NRC=0; run_lint "$SYN" --list-dispatch-surfaces . > "$WORK/syn_disc2.txt" 2>/dev/null || NRC=$?
subtract "$SCOPE_F" "$EMPTY_EXCL" < "$WORK/syn_disc2.txt" > "$WORK/syn_diff2.txt"
NEG_N=$(nlines "$WORK/syn_diff2.txt")
assert_eq "A13-5 M-S negative control (주입분 제거) → 차집합 0" "$NEG_N" "0" \
  "단일 변수 diff = 사정권 밖 파일 1개 유무. A13-4 가 '무엇이든 RED' 인 상시-RED 아님"

# ── A13-6 anti-hardcode: 주입 경로가 lint 소스에 없음 ∧ 그래도 discovery 가 찾았음 ──
HC=$(hits 'PeerDispatchAgent|newlane' "$LINT_PY")
assert_eq "A13-6a 주입 경로가 lint 소스에 부재" "$HC" "0" \
  "discovery 가 이 파일을 '미리 알고' 있지 않았음"
if grep -Fxq -- "newlane/agents/PeerDispatchAgent.md" "$WORK/syn_disc.txt"; then
  ok "A13-6b anti-hardcode 실증 — 사전 미등재 경로를 discovery 가 실 walk 로 발견 (B-8 준수)"
else
  bad "A13-6b anti-hardcode 실증" "discovery 가 주입 표면을 못 찾음 — 목록 하드코딩 의심 (B-8 위반)"
fi

# ═══════════════════════════════════════════════════════════════════════════
# §3 사정권 확대의 load-bearing 실증 (pre-GREEN 값 대조)
# ═══════════════════════════════════════════════════════════════════════════
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " §3 pre-GREEN 사정권 값으로는 차집합 ≥1 (사정권 확대가 load-bearing)"
echo "═══════════════════════════════════════════════════════════════════════════"
# 사정권 값을 pre-GREEN(origin/main) 것으로 바꾸면 실 repo 차집합이 ≥1 이 되어야 한다.
# 안 그러면 이 Story 의 사정권 확대가 아무것도 바꾸지 않은 것 = 변경이 무의미했다는 뜻.
if git -C "$REPO_ROOT" rev-parse --verify -q origin/main >/dev/null \
   && git -C "$REPO_ROOT" cat-file -e "origin/main:scripts/lib/check_codex_companion_timeout_presence.py" 2>/dev/null; then
  git -C "$REPO_ROOT" show "origin/main:scripts/lib/check_codex_companion_timeout_presence.py" \
    > "$WORK/lint_pre.py"
  sed -n '/^DEFAULT_SCAN_DIRS = (/,/^)/p' "$WORK/lint_pre.py" \
    | grep -oE "'[^']+'" | tr -d "'" > "$WORK/scope_pre.txt"
  PRE_N=$(nlines "$WORK/scope_pre.txt")
  if [ "$PRE_N" -ge 1 ]; then
    ok "A13-7a pre-GREEN 사정권 값 판독 ($PRE_N 항목: $(tr '\n' ' ' < "$WORK/scope_pre.txt"))"
    subtract "$WORK/scope_pre.txt" "$EXCL_F" < "$DISC_F" > "$WORK/diff_pre.txt"
    PRE_DIFF_N=$(nlines "$WORK/diff_pre.txt")
    if [ "$PRE_DIFF_N" -ge 1 ]; then
      ok "A13-7b pre-GREEN 사정권 → 차집합 $PRE_DIFF_N 건 (≥1) [discriminating]: $(tr '\n' ' ' < "$WORK/diff_pre.txt")"
    else
      bad "A13-7b pre-GREEN 사정권 → 차집합 ≥1" "차집합 0 — 사정권 확대가 아무 표면도 새로 덮지 않았다 (변경 무의미 신호)"
    fi
  else
    bad "A13-7a pre-GREEN 사정권 값 판독" "DEFAULT_SCAN_DIRS 파싱 0 항목 — 형태 변경 의심"
  fi
else
  bad "A13-7 pre-GREEN 대조" "origin/main ref 또는 대상 blob 미존재 — 사정권 확대의 load-bearing 미입증"
fi

# ═══════════════════════════════════════════════════════════════════════════
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "✓ All $PASS cases pass — AC-13 discovery 기반 차집합 0 · M-S KILL 실증 · anti-hardcode(B-8) ·"
  echo "  양변 독립(사정권 트리 비의존) · 제외 선언 자동 수축 · pre-GREEN 사정권 대조"
  exit 0
else
  echo "✗ $FAIL case(s) failed"
  exit 1
fi
