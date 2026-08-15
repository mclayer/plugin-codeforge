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
git -C "$TMP/e4_wt" fetch -q origin || true
# 원격에 없는 phantom ref 를 로컬에만 세워 baseline 이 secret 객체를 제외하게 만든다
git -C "$TMP/e4_wt" update-ref refs/remotes/origin/phantom "$(git -C "$TMP/e4_wt" rev-parse HEAD)"
R4="$(run_land "$TMP/e4_wt" origin salvage-e4)"
note "관측 rc|scan|push" "$R4"
chk "E4 스캔이 secret 를 검출해야" "finding" "$(printf '%s' "$R4" | cut -d'|' -f2)"
chk "E4 push 미도달이어야" "skipped" "$(printf '%s' "$R4" | cut -d'|' -f3)"
E4LEAK="$(git -C "$TMP/e4_origin.git" rev-list --all --objects 2>/dev/null | awk '{print $1}' | git -C "$TMP/e4_origin.git" cat-file --batch 2>/dev/null | grep -ac "$SECRET" || true)"
chk "E4 origin 원격에 secret 미착지" "0" "$E4LEAK"

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
