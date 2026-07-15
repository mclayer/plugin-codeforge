#!/usr/bin/env bash
# tests/scripts/test-gitattributes-cmd-crlf.sh
# CFP-2702 Phase 2 (구현 lane) — AC-6 회귀 테스트
#   symbol: test_gitattributes_cmd_eol_crlf_channels
#
# 대상: .gitattributes 의 `*.cmd text eol=crlf` + `*.bat text eol=crlf` override.
#   전역 `* text=auto eol=lf` 아래에서 cmd/bat 만 CRLF 로 되돌리는 override 가, git 이 blob 을
#   LF 로 정규 저장하더라도 **배포 채널**(checkout / clone / archive)에서는 CRLF 를 산출하게 함.
#   (cmd.exe 는 CRLF 전제 → LF-only 배치는 @REM 배너를 명령 실행 → 스퓨리어스 stderr; packet §6 Fact 1.)
#
# ★ discriminating (hollow-gate 아님) 증명 — 3축이 함께여야 GREEN 의미가 성립:
#   (1) 정상 PASS  : real-repo `git check-attr` = text:set + eol:crlf, 그리고 override 있는 임시 repo 의
#                    checkout/archive 산출물 CR>0 (packet §6 Fact 3).
#   (2) 결함 재현 RED: override **없는** 임시 repo(전역 eol=lf 만)의 동일 .cmd checkout/archive 산출물
#                    CR==0 → override 가 load-bearing 임을 대조 증명(override 제거 = LF 배포로 회귀).
#   (3) 정밀도    : blob(`git show`)은 LF(CR==0)인데 채널 산출물만 CRLF(CR>0)임을 대조 —
#                    "blob 로 검증하면 부적합, checkout/archive 채널로 검증해야 함"을 결박.
#
# 자립성: 배포 채널 검증은 real-repo 상태에 의존하지 않도록 **임시 git repo** 를 만들어 수행
#   (커밋된 .gitattributes + .cmd 로 git 정규화·체크아웃을 실제 구동). 네트워크 0.
#
# Exit code: 0 = 전 케이스 PASS, 1 = 1+ 실패.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
GITATTR="$REPO_ROOT/.gitattributes"

PASS=0
FAIL=0

# 격리 repo commit 가능하도록 git author env 강제 (CI 에 user.* 미설정 가능).
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t

WORK="$(mktemp -d)"
# shellcheck disable=SC2064
trap "rm -rf '$WORK'" EXIT

pass() { echo "OK PASS: $1"; PASS=$((PASS+1)); }
fail() { echo "X FAIL: $1"; FAIL=$((FAIL+1)); }

# count_cr <file> : 파일 안 CR(\r) 바이트 개수 echo.
#   grep-free (tr -cd) — 0 매치에서도 exit 0 유지(set -e/pipefail 안전; grep -o 는 무매치 exit 1).
count_cr() { tr -cd '\r' < "$1" | wc -c | tr -d '[:space:]'; }

# mk_repo <dir> <attrs_content> : git repo 생성 + .gitattributes(attrs) + sample.cmd(2줄) 커밋.
mk_repo() {
  local dir="$1" attrs="$2"
  mkdir -p "$dir"
  ( cd "$dir" && git init -q )
  printf '%s\n' "$attrs" > "$dir/.gitattributes"
  # 대상 .cmd 는 LF 로 작업트리에 둔다 → git 이 저장 시 LF 정규화, 채널에서 eol 적용.
  printf 'batch line one\nbatch line two\n' > "$dir/sample.cmd"
  # 'LF will be replaced by CRLF' 경고는 eol 변환이 걸림을 알리는 기대 noise → 억제.
  # (add 실 실패 시 && 단절로 commit 미실행 → set -e 로 loud abort 유지.)
  ( cd "$dir" && git add -A 2>/dev/null && git commit -q -m init )
}

# ch_blob <dir> <out>       : blob(git show) 산출 → out.
# ch_archive <dir> <out>    : git archive 채널 산출 → out (tar -xO 로 파일 본문 추출).
# ch_checkout <dir> <out>   : clean checkout-index 채널 산출 → out.
ch_blob()     { git -C "$1" show HEAD:sample.cmd > "$2"; }
ch_archive()  { git -C "$1" archive HEAD sample.cmd | tar -xO > "$2"; }
ch_checkout() { local co; co=$(mktemp -d); ( cd "$1" && git --work-tree="$co" checkout-index -a -f ); cp "$co/sample.cmd" "$2"; rm -rf "$co"; }

echo "==========================================================================="
echo " CFP-2702 AC-6: .gitattributes *.cmd/*.bat eol=crlf 배포 채널 — discriminating self-test"
echo "==========================================================================="

# ═════════════════════════════════════════════════════════════════════════════
# Case 1 (real-repo attr): 실 repo 의 hooks/run-hook.cmd 에 대해 check-attr = text:set + eol:crlf.
# ═════════════════════════════════════════════════════════════════════════════
if [ ! -f "$GITATTR" ]; then
  fail "setup — .gitattributes 부재 ($GITATTR)"
else
  attr_out=$(git -C "$REPO_ROOT" check-attr text eol -- hooks/run-hook.cmd 2>&1) || true
  if case "$attr_out" in *"text: set"*) true;; *) false;; esac \
     && case "$attr_out" in *"eol: crlf"*) true;; *) false;; esac; then
    pass "Case 1 real-repo check-attr — hooks/run-hook.cmd: text:set + eol:crlf"
  else
    fail "Case 1 real-repo check-attr — 기대 text:set+eol:crlf, 실제:
$attr_out"
  fi
fi

# ═════════════════════════════════════════════════════════════════════════════
# Case 2 (§5.6 edge — .cmd + .bat 두 override 줄 존재): .bat 누락 회귀 방지.
# ═════════════════════════════════════════════════════════════════════════════
cmd_line=0; bat_line=0
grep -qE '^\*\.cmd[[:space:]]+text[[:space:]]+eol=crlf' "$GITATTR" && cmd_line=1 || true
grep -qE '^\*\.bat[[:space:]]+text[[:space:]]+eol=crlf' "$GITATTR" && bat_line=1 || true
if [ "$cmd_line" -eq 1 ] && [ "$bat_line" -eq 1 ]; then
  pass "Case 2 override 줄 존재 — '*.cmd text eol=crlf' ∧ '*.bat text eol=crlf' (.bat 누락 회귀 방지)"
else
  fail "Case 2 override 줄 — cmd=$cmd_line(기대1) bat=$bat_line(기대1)"
fi

# 실 repo 의 .bat check-attr 도 동일 override 를 받는지 (합성 경로) 확증.
bat_attr=$(git -C "$REPO_ROOT" check-attr text eol -- some/dir/foo.bat 2>&1) || true
if case "$bat_attr" in *"eol: crlf"*) true;; *) false;; esac; then
  pass "Case 2b .bat check-attr — foo.bat: eol:crlf (override 적용 확증)"
else
  fail "Case 2b .bat check-attr — 기대 eol:crlf, 실제: $bat_attr"
fi

# ═════════════════════════════════════════════════════════════════════════════
# Case 3 (배포 채널 CR>0, override 있음): 임시 repo(전역 eol=lf + *.cmd eol=crlf) →
#   checkout/archive 산출물 CR>0. 대조로 blob(git show)은 LF(CR==0) — 채널로 검증해야 함을 결박.
# ═════════════════════════════════════════════════════════════════════════════
R_ON="$WORK/repo-override-on"
mk_repo "$R_ON" '* text=auto eol=lf
*.cmd text eol=crlf'

ch_blob     "$R_ON" "$WORK/on-blob.cmd"
ch_archive  "$R_ON" "$WORK/on-archive.cmd"
ch_checkout "$R_ON" "$WORK/on-checkout.cmd"
on_blob=$(count_cr "$WORK/on-blob.cmd")
on_arc=$(count_cr "$WORK/on-archive.cmd")
on_co=$(count_cr "$WORK/on-checkout.cmd")

# 정밀도: blob 은 LF(0) 이어야 하고, 채널(archive/checkout)은 CR>0 이어야 함.
if [ "$on_blob" -eq 0 ]; then
  pass "Case 3a 정밀도 — blob(git show) CR=0 (LF 정규 저장; blob 로 검증하면 부적합)"
else
  fail "Case 3a 정밀도 — blob CR=$on_blob (기대 0, blob 은 LF 정규화여야)"
fi
if [ "$on_arc" -gt 0 ] && [ "$on_co" -gt 0 ]; then
  pass "Case 3b 배포 채널 CR>0 — archive CR=$on_arc, checkout CR=$on_co (override 로 CRLF 배포)"
else
  fail "Case 3b 배포 채널 — archive CR=$on_arc / checkout CR=$on_co (둘 다 >0 기대)"
fi

# ═════════════════════════════════════════════════════════════════════════════
# Case 4 (discriminating — override 없음): 전역 eol=lf 만인 임시 repo → 동일 .cmd 의 채널 산출물
#   CR==0. override 가 load-bearing (제거 = LF 배포로 회귀) 임을 대조 증명 = hollow-gate 아님.
# ═════════════════════════════════════════════════════════════════════════════
R_OFF="$WORK/repo-override-off"
mk_repo "$R_OFF" '* text=auto eol=lf'

ch_archive  "$R_OFF" "$WORK/off-archive.cmd"
ch_checkout "$R_OFF" "$WORK/off-checkout.cmd"
off_arc=$(count_cr "$WORK/off-archive.cmd")
off_co=$(count_cr "$WORK/off-checkout.cmd")
if [ "$off_arc" -eq 0 ] && [ "$off_co" -eq 0 ]; then
  pass "Case 4 discriminating — override 無 repo: archive CR=$off_arc ∧ checkout CR=$off_co (둘 다 0) → override load-bearing 확증"
else
  fail "Case 4 discriminating — override 無인데 CR 발생 (archive=$off_arc checkout=$off_co, 기대 0/0) = 대조 실패"
fi

# ═════════════════════════════════════════════════════════════════════════════
echo "==========================================================================="
echo " Test Summary (CFP-2702 AC-6 .gitattributes cmd/bat eol=crlf 배포 채널)"
echo "==========================================================================="
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "TOTAL: $((PASS + FAIL))"
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS case(s) pass — check-attr / .bat 회귀가드 / 채널 CR>0 / override-off 대조 결박"
  exit 0
else
  echo "X $FAIL case(s) failed"
  exit 1
fi
