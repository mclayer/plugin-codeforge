#!/usr/bin/env bash
# tests/scripts/test_salvage_land_scan_domain.sh
# CFP-2984 보안테스트 FIX iter1 — S-P1-1 회귀 고정.
#
# ── 무엇을 결박하는가 ────────────────────────────────────────────────
#   `--land` 의 **스캔 정의역이 push 전송 집합을 포함**해야 한다.
#   baseline(`rev-list --not --remotes=<R>`) 의 <R> 이 push 대상 remote 와 어긋나거나,
#   remote-tracking ref 가 원격 실보유를 반영하지 않으면(phantom) 스캔이 제외한 객체가
#   그대로 전송된다 — `SCAN_RESULT: clean` + `PUSH: done` 인데 원격에서 secret 회수 가능.
#
# ── 보장 밖 (over-claim 차단) ────────────────────────────────────────
#   raw `git push` 우회는 L1 정의역 밖이다. 본 테스트는 "secret 유출 0" 을 증명하지 않고
#   **L1 경유 착지에서 스캔 정의역 ⊇ 전송 집합** 만 결박한다.
#
# ── 케이스 ───────────────────────────────────────────────────────────
#   E5  push remote ≠ baseline remote  → 다른 remote 로 무검사 전송
#   E4  phantom remote-tracking ref    → 로컬 ref 가 원격 실보유와 괴리
#   C1  대조군: 정상 경로 clean 입력   → clean + push (무조건-RED 아님 실증)
#   C2  대조군: 정상 경로 secret 입력  → finding (검출력 살아있음 실증)
#
# self-contained bash. Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
SUT="$REPO/scripts/lib/check_salvage_bundle.py"
SECRET='AKIAIOSFODNN7EXAMPLE'
SECRET2='AKIAQQQQZZZZ7WWWWEXA'   # R3 전용 — seed 와 분리해야 leak assert 가 판별력을 갖는다

TMP="$(mktemp -d)"
# CWD ≠ worktree 강제 (다른 git repo) — `-C` 누락 fail-open 이 숨지 않게
mkdir -p "$TMP/cwd" && git init -q "$TMP/cwd" && (cd "$TMP/cwd" && git config user.email t@t && git config user.name t && echo z > z && git add -A && git commit -qm z)
cleanup(){ cd /; rm -rf "$TMP"; }
trap cleanup EXIT

FAIL=0
note(){ printf '  %-46s %s\n' "$1" "$2"; }
chk(){ # $1=label $2=expected $3=actual
  if [ "$2" = "$3" ]; then note "$1" "PASS (=$3)"; else note "$1" "FAIL (기대=$2 실제=$3)"; FAIL=1; fi
}

mkwt(){ # $1=dir  — secret 커밋 1개 보유한 작업 repo
  git init -q "$1"
  git -C "$1" config user.email t@t; git -C "$1" config user.name t
  echo base > "$1/a.txt"; git -C "$1" add -A; git -C "$1" commit -qm base
  printf '%s\n' "$SECRET" > "$1/leak.txt"; git -C "$1" add -A; git -C "$1" commit -qm wip1
}

run_land(){ # $1=wt $2=remote $3=branch  → "rc|scan|push"
  local out rc
  set +e
  out="$(cd "$TMP/cwd" && python3 "$SUT" --land --worktree "$1" --remote "$2" --branch "$3" 2>&1)"
  rc=$?
  set -e
  local scan push
  scan="$(printf '%s' "$out" | sed -n 's/^SCAN_RESULT: //p' | head -1)"
  push="$(printf '%s' "$out" | sed -n 's/^PUSH: //p' | head -1)"
  printf '%s|%s|%s' "$rc" "${scan:-none}" "${push:-none}"
}

echo "===== E5 — push remote ≠ baseline remote ====="
git init -q --bare "$TMP/e5_origin.git"; git init -q --bare "$TMP/e5_pub.git"
mkwt "$TMP/e5_wt"
git -C "$TMP/e5_wt" remote add origin "$TMP/e5_origin.git"
git -C "$TMP/e5_wt" remote add pub "$TMP/e5_pub.git"
# secret 객체를 origin 에만 올려 baseline(origin) 이 그것을 제외하게 만든다
git -C "$TMP/e5_wt" push -q origin HEAD:refs/heads/seed
git -C "$TMP/e5_wt" fetch -q origin
R="$(run_land "$TMP/e5_wt" pub salvage-e5)"
note "관측 rc|scan|push" "$R"
chk "E5 스캔이 secret 를 검출해야" "finding" "$(printf '%s' "$R" | cut -d'|' -f2)"
chk "E5 push 미도달이어야" "skipped" "$(printf '%s' "$R" | cut -d'|' -f3)"
E5LEAK="$(git -C "$TMP/e5_pub.git" rev-list --all --objects 2>/dev/null | awk '{print $1}' | git -C "$TMP/e5_pub.git" cat-file --batch 2>/dev/null | grep -ac "$SECRET" || true)"
chk "E5 pub 원격에 secret 미착지" "0" "$E5LEAK"

echo
echo "===== E4 — phantom remote-tracking ref ====="
git init -q --bare "$TMP/e4_origin.git"
mkwt "$TMP/e4_wt"
git -C "$TMP/e4_wt" remote add origin "$TMP/e4_origin.git"
# 셋업 실패 = 테스트 무효. `|| true` 로 삼키면 phantom 전제가 안 선 채 GREEN 이 나온다
# (이 Story 가 문서화한 **공허 통과** 그 자체).
if ! git -C "$TMP/e4_wt" fetch -q origin; then
  note "E4 셋업 실패 — fetch rc!=0" "테스트 무효 (공허 통과 방지)"; FAIL=1
fi
# 원격에 없는 phantom ref 를 로컬에만 세워 baseline 이 secret 객체를 제외하게 만든다
git -C "$TMP/e4_wt" update-ref refs/remotes/origin/phantom "$(git -C "$TMP/e4_wt" rev-parse HEAD)"
R4="$(run_land "$TMP/e4_wt" origin salvage-e4)"
note "관측 rc|scan|push" "$R4"
chk "E4 스캔이 secret 를 검출해야" "finding" "$(printf '%s' "$R4" | cut -d'|' -f2)"
chk "E4 push 미도달이어야" "skipped" "$(printf '%s' "$R4" | cut -d'|' -f3)"
E4LEAK="$(git -C "$TMP/e4_origin.git" rev-list --all --objects 2>/dev/null | awk '{print $1}' | git -C "$TMP/e4_origin.git" cat-file --batch 2>/dev/null | grep -ac "$SECRET" || true)"
chk "E4 origin 원격에 secret 미착지" "0" "$E4LEAK"

echo
echo "===== R3 — 좁은 refspec(--single-branch) + phantom ref ====="
# fetch --prune 은 remote.<r>.fetch destination 범위만 prune 한다. 좁은 clone 에선
# refs/remotes/origin/main 하나뿐인데 baseline(--not --remotes=origin)은 refs/remotes/origin/* 전체를
# 센다 ⇒ prune 이 손대지 못한 ref 가 baseline 에 계상돼 그 객체가 스캔에서 빠진다.
git init -q --bare "$TMP/r3_origin.git"
mkwt "$TMP/r3_seed"
git -C "$TMP/r3_seed" remote add origin "$TMP/r3_origin.git"
git -C "$TMP/r3_seed" push -q origin HEAD:refs/heads/main
R3SEC="$(git -C "$TMP/r3_seed" rev-parse HEAD)"
git clone -q --single-branch --branch main "$TMP/r3_origin.git" "$TMP/r3_wt"
git -C "$TMP/r3_wt" config user.email t@t; git -C "$TMP/r3_wt" config user.name t
note "refspec" "$(git -C "$TMP/r3_wt" config --get-all remote.origin.fetch | tr '
' ' ')"
# 새 secret 커밋(원격 미보유) + 그것을 가리키는 phantom ref
printf '%s
' "$SECRET2" > "$TMP/r3_wt/leak2.txt"
git -C "$TMP/r3_wt" add -A; git -C "$TMP/r3_wt" commit -qm r3wip
git -C "$TMP/r3_wt" update-ref refs/remotes/origin/phantom "$(git -C "$TMP/r3_wt" rev-parse HEAD)"
# ★ R3 시나리오의 **핵심 셋업** — 이 fetch 가 실패하면 "prune 이 phantom 을 못 지운다" 는
# 전제 자체가 성립하지 않아 뒤 assert 가 무의미해진다. 실패는 반드시 테스트를 무효화한다.
if ! git -C "$TMP/r3_wt" fetch --prune -q origin; then
  note "R3 셋업 실패 — fetch --prune rc!=0" "테스트 무효 (전제 미성립)"; FAIL=1
fi
PH="$(git -C "$TMP/r3_wt" for-each-ref --format='%(refname)' refs/remotes/origin/phantom | wc -l)"
note "fetch --prune 후 phantom 잔존" "$PH  (1 = prune 정의역 밖)"
R3="$(run_land "$TMP/r3_wt" origin salvage-r3)"
note "관측 rc|scan|push" "$R3"
chk "R3 스캔이 secret 를 검출해야" "finding" "$(printf '%s' "$R3" | cut -d'|' -f2)"
chk "R3 push 미도달이어야" "skipped" "$(printf '%s' "$R3" | cut -d'|' -f3)"
R3LEAK="$(git -C "$TMP/r3_origin.git" rev-list --all --objects 2>/dev/null | awk '{print $1}' | git -C "$TMP/r3_origin.git" cat-file --batch 2>/dev/null | grep -ac "$SECRET2" || true)"
chk "R3 origin 에 신규 secret 미착지 (판별 대상 = SECRET2)" "0" "$R3LEAK"

echo
echo "===== S10 — 고유 OID 1000+ (argv transport 회귀) ====="
# 실 repo 는 원격 ref 가 1000+ 라 `--not <OID*N>` argv 가 Windows CreateProcess(~32KB)를 넘긴다.
# 그때 예외가 탈출하면 SCAN_RESULT/PUSH 토큰이 0개가 되어 감사면이 사망한다.
# 소형 픽스처는 이 결함을 **구조적으로** 못 잡는다 — 그래서 대형 픽스처를 상주시킨다.
git init -q --bare "$TMP/s10_origin.git"
git init -q "$TMP/s10_wt"
git -C "$TMP/s10_wt" config user.email t@t; git -C "$TMP/s10_wt" config user.name t
# fast-import 스트림 생성 — awk 로 (LF 고정. Windows 에서 CRLF 가 섞이면 git 이
# `refs/heads/b1?` 로 거부한다 — 이 repo 기지 gotcha)
awk 'BEGIN{
  for (i = 1; i <= 1000; i++) {
    msg = "c" i "\n"; body = "content-" i "\n";
    printf "commit refs/heads/b%d\nmark :%d\ncommitter t <t@t> 0 +0000\ndata %d\n%s", i, i, length(msg), msg;
    printf "M 100644 inline f.txt\ndata %d\n%s\n", length(body), body;
  }
}' > "$TMP/s10_wt/fi.stream"
git -C "$TMP/s10_wt" fast-import --quiet < "$TMP/s10_wt/fi.stream"
rm -f "$TMP/s10_wt/fi.stream"
git -C "$TMP/s10_wt" remote add origin "$TMP/s10_origin.git"
git -C "$TMP/s10_wt" push -q origin --all
git -C "$TMP/s10_wt" checkout -q -b work refs/heads/b1
printf '%s' "$SECRET" > "$TMP/s10_wt/leak.txt"; git -C "$TMP/s10_wt" add -A; git -C "$TMP/s10_wt" commit -qm s10wip
S10N="$(git -C "$TMP/s10_wt" ls-remote origin | awk '{print $1}' | sort -u | wc -l)"
note "고유 OID" "$S10N  (argv 환산 ~$((S10N*41)) B, 32KB 한계 초과)"
set +e
S10OUT="$(cd "$TMP/cwd" && python3 "$SUT" --pre-push-scan --worktree "$TMP/s10_wt" --branch work --remote origin 2>&1)"
set -e
chk "S10 SCAN_RESULT 토큰이 출력돼야 (감사면 생존)" "1" "$(printf '%s' "$S10OUT" | grep -c 'SCAN_RESULT:')"
chk "S10 미처리 예외 0 (터진 게 아니라 판정한 것)" "0" "$(printf '%s' "$S10OUT" | grep -c 'Traceback')"
chk "S10 대형 원격에서도 secret 검출" "finding" "$(printf '%s' "$S10OUT" | sed -n 's/^SCAN_RESULT: //p' | head -1)"

echo
echo "===== 대조군 C1 — clean 입력은 통과해야 (무조건-RED 아님) ====="
git init -q --bare "$TMP/c1_origin.git"
git init -q "$TMP/c1_wt"; git -C "$TMP/c1_wt" config user.email t@t; git -C "$TMP/c1_wt" config user.name t
echo hello > "$TMP/c1_wt/a.txt"; git -C "$TMP/c1_wt" add -A; git -C "$TMP/c1_wt" commit -qm clean
git -C "$TMP/c1_wt" remote add origin "$TMP/c1_origin.git"
RC1="$(run_land "$TMP/c1_wt" origin salvage-c1)"
note "관측 rc|scan|push" "$RC1"
chk "C1 clean 판정" "clean" "$(printf '%s' "$RC1" | cut -d'|' -f2)"
chk "C1 push 수행" "done" "$(printf '%s' "$RC1" | cut -d'|' -f3)"

echo
echo "===== 대조군 C2 — 정상 경로 secret 은 여전히 검출 ====="
git init -q --bare "$TMP/c2_origin.git"
mkwt "$TMP/c2_wt"
git -C "$TMP/c2_wt" remote add origin "$TMP/c2_origin.git"
RC2="$(run_land "$TMP/c2_wt" origin salvage-c2)"
note "관측 rc|scan|push" "$RC2"
chk "C2 finding 판정" "finding" "$(printf '%s' "$RC2" | cut -d'|' -f2)"
chk "C2 push 미도달" "skipped" "$(printf '%s' "$RC2" | cut -d'|' -f3)"

echo
if [ "$FAIL" -eq 0 ]; then echo "ALL PASS — 스캔 정의역 ⊇ 전송 집합 결박 확인"; else echo "FAIL 있음"; fi
exit "$FAIL"
