#!/usr/bin/env bash
# tests/scripts/test_bundle_pre_push_redaction.sh
# CFP-2984 Phase 2 (구현 lane) — AC-32 discriminating self-test.
#   착지(P1 = origin push) 직전 secret·PII 스캔 게이트.
#
# ── 보장 명제 (over-claim 차단 — Story §7.12-E) ────────────────────────────────
#   본 오라클이 결박하는 것은 "**L1(scripts/check-salvage-bundle.sh)을 경유한 착지 경로에 한해**
#   스캔 단계를 거치지 않은 착지가 0건" 이다. raw `git push` 우회 경로는 L1 정의역 **밖**이며
#   L3(CI backstop)가 **사후 탐지**할 뿐 비가역 공개를 되돌리지 못한다.
#   "secret·PII 유출 0" / "모든 착지 경로에서 스캔 미경유 0건" 은 본 테스트가 증명하지 않는다.
#
# ── 4 구성요소 (하나라도 빠지면 hollow) ────────────────────────────────────────
#  (a) 픽스처가 **CWD ≠ <worktree>** 를 강제한다. `CWD == wt` 고정 픽스처는 `-C` 누락 fail-open 을
#      영원히 검출하지 못한다(§7.12-B1 처방 ④). Part 1 이 4-변종(G1~G4)으로 실증하고,
#      Part 3/4 의 SUT 호출은 **전부 다른 git repo 를 CWD 로** 실행한다.
#  (b) mutant 4종 — ①스캔 제거 ②재기록(TOCTOU) ③glob 배제 ④**중간 커밋 전용 secret**.
#      ④ 가 primitive 퇴화(2-tree 차분)를 잡는 **유일** leg 다(§7.12-B2 P0-1).
#  (c) 대조군 3종 — clean-input / benign `missing` 문면 / 범위 하한(F). 대조군 없는 오라클은
#      "항상 RED" 구현이 mutant 를 전부 kill 하면서 통과한다(§8.2-E INV-T4).
#  (d) 실 부작용 0 — 전 픽스처가 `mktemp -d` 내부 임시 git repo. 실 원격 push 0(origin = 로컬 bare).
#
# ── ②↔③ 상보성 (어느 하나로 대체 불가) ────────────────────────────────────────
#   G1(비-repo CWD)은 `cat-file` 이 죽어 `missing` 토큰이 **0건** ⇒ ③ 은 못 잡고 rc(②)만 잡는다.
#   G2·G3(다른 repo CWD)은 **rc=0** 이라 ②가 볼 실패가 없다 ⇒ ③만 잡는다. Part 1 이 실증한다.
#
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail

export PYTHONIOENCODING=utf-8
export GIT_CONFIG_NOSYSTEM=1
export GIT_TERMINAL_PROMPT=0

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SUT="$REPO_ROOT/scripts/check-salvage-bundle.sh"
REDACTOR="$REPO_ROOT/scripts/lib/redact_dev_process_content.py"

# 픽스처 secret = AWS access key id 형태(공식 문서 예시 값 — 실 자격증명 아님).
#   `_RE_CLOUD_STRUCT` (redact_dev_process_content.py:147-151) 구조 매칭 → RULE_CLOUD_KEY 발화.
#   hex/email 계열을 피한 이유 = 그 두 룰은 git OID·commit author 로 상시 발화하는 식별자 축이라
#   검출 신호로 쓸 수 없다(Part 3 대조군 REF 가 이 사실을 결박한다).
SECRET='AKIAIOSFODNN7EXAMPLE'

PASS=0
FAIL=0

TMPROOT="$(mktemp -d)"
trap 'rm -rf "$TMPROOT"' EXIT

# ─────────────────────────────────────────────────────────────────────────────
# assert helper (FAIL 카운터 backup)
# ─────────────────────────────────────────────────────────────────────────────
ok() {
  echo "OK PASS: $1"
  PASS=$((PASS+1))
}

ng() {
  echo "X FAIL: $1"
  shift
  for l in "$@"; do echo "    $l"; done
  FAIL=$((FAIL+1))
}

assert_eq() { # <name> <expected> <actual> [note]
  if [ "$2" = "$3" ]; then
    ok "$1 (= $3)${4:+ — $4}"
  else
    ng "$1" "expected='$2' actual='$3'" "${4:-}"
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# 픽스처 빌더 — 전부 mktemp 내부. origin = 로컬 bare repo (실 원격 0).
#   공통: BASE 커밋을 origin 에 push → remote-tracking ref 확립
#         ⇒ `--not --remotes=origin` baseline 이 BASE 를 제외한다.
# ─────────────────────────────────────────────────────────────────────────────
git_init_pair() { # <dir>  → $dir/wt (main) + $dir/origin.git, BASE 는 origin 에 착지
  local d="$1"
  mkdir -p "$d/wt"
  git init -q --bare "$d/origin.git"
  git init -q -b main "$d/wt"
  git -C "$d/wt" config user.email dev@example.com
  git -C "$d/wt" config user.name Dev
  git -C "$d/wt" config commit.gpgsign false
  printf 'base line\n' > "$d/wt/README.md"
  git -C "$d/wt" add README.md >/dev/null
  git -C "$d/wt" commit -qm BASE
  git -C "$d/wt" remote add origin "$d/origin.git"
  git -C "$d/wt" push -q origin main
}

commit_file() { # <wt> <relpath> <content> <msg>
  printf '%s\n' "$3" > "$1/$2"
  git -C "$1" add "$2" >/dev/null
  git -C "$1" commit -qm "$4"
}

# clean 번들 blob — ADR-179 §결정 2-U allowlist 필드 + S-10 참조형 값(40hex SHA / blob:sha256:<64hex>).
#   ★ 이 값들은 스키마가 **요구**하는 형태다. 게이트가 hex 축으로 판정하면 자기 스키마에 막힌다.
write_clean_bundle() { # <wt>
  local base
  base="$(git -C "$1" rev-parse HEAD)"
  cat > "$1/salvage-bundle.json" <<EOF
{"branch":"cfp-2984-phase2",
 "last_commit_sha":"$base",
 "wip_summary":"작업 중단 지점 요약 — 산문 1필드(ADR-178 6-4 값공간 폐쇄)",
 "unfinished":["scripts/foo.sh:12-40"],
 "resume_point":"tests/scripts/bar.sh:120-140",
 "notes_ref":"blob:sha256:0000000000000000000000000000000000000000000000000000000000000000",
 "integrity_tag":"ok","producer":"DeveloperAgent"}
EOF
}

# 픽스처 A — 중간 커밋 전용 secret (BASE → C1[secret] → C2[마스킹]). SHA = C2.
fx_secret_mid() { # <dir> → echo "<wt> <origin> <sha> <c1>"
  local d="$1"
  git_init_pair "$d"
  commit_file "$d/wt" leak.txt "aws_key: $SECRET" C1
  local c1; c1="$(git -C "$d/wt" rev-parse HEAD)"
  commit_file "$d/wt" leak.txt "aws_key: [MASKED]" C2
  echo "$d/wt $d/origin.git $(git -C "$d/wt" rev-parse HEAD) $c1"
}

# 픽스처 B — clean 번들 (secret·PII 부재). 대조군 E + REF.
fx_clean() { # <dir> → echo "<wt> <origin> <sha>"
  local d="$1"
  git_init_pair "$d"
  write_clean_bundle "$d/wt"
  git -C "$d/wt" add salvage-bundle.json >/dev/null
  git -C "$d/wt" commit -qm CLEAN
  echo "$d/wt $d/origin.git $(git -C "$d/wt" rev-parse HEAD)"
}

# 픽스처 C — benign `missing` 문면 (평문 1행 + `<40hex> missing` 인용 blob). 대조군.
fx_benign_missing() { # <dir> → echo "<wt> <origin> <sha>"
  local d="$1"
  git_init_pair "$d"
  {
    printf 'the upstream record is missing\n'
    printf '0123456789abcdef0123456789abcdef01234567 missing\n'
  } > "$d/wt/notes.md"
  git -C "$d/wt" add notes.md >/dev/null
  git -C "$d/wt" commit -qm BENIGN
  echo "$d/wt $d/origin.git $(git -C "$d/wt" rev-parse HEAD)"
}

# 픽스처 D — 범위 하한 (secret 이 <upstream> **아래에만** 존재, 신규분은 clean).
fx_range_lower() { # <dir> → echo "<wt> <origin> <sha> <upstream>"
  local d="$1"
  mkdir -p "$d/wt"
  git init -q --bare "$d/origin.git"
  git init -q -b main "$d/wt"
  git -C "$d/wt" config user.email dev@example.com
  git -C "$d/wt" config user.name Dev
  git -C "$d/wt" config commit.gpgsign false
  commit_file "$d/wt" hist.txt "legacy: $SECRET" OLD
  git -C "$d/wt" remote add origin "$d/origin.git"
  git -C "$d/wt" push -q origin main
  local up; up="$(git -C "$d/wt" rev-parse HEAD)"
  commit_file "$d/wt" new.txt "clean new work" NEW
  echo "$d/wt $d/origin.git $(git -C "$d/wt" rev-parse HEAD) $up"
}

# 픽스처 E — TOCTOU: BASE → C2(clean, 스캔 대상) → C3(secret, 스캔 이후 재기록).
fx_toctou() { # <dir> → echo "<wt> <origin> <c2> <c3>"
  local d="$1"
  git_init_pair "$d"
  commit_file "$d/wt" work.txt "clean work" C2
  local c2; c2="$(git -C "$d/wt" rev-parse HEAD)"
  commit_file "$d/wt" late.txt "aws_key: $SECRET" C3
  echo "$d/wt $d/origin.git $c2 $(git -C "$d/wt" rev-parse HEAD)"
}

# 다른 git repo (CWD 오염원) / 비-repo 디렉터리
OTHER="$TMPROOT/other-repo"
mkdir -p "$OTHER"
git init -q -b main "$OTHER"
git -C "$OTHER" config user.email dev@example.com
git -C "$OTHER" config user.name Dev
git -C "$OTHER" config commit.gpgsign false
printf 'unrelated\n' > "$OTHER/x.txt"
git -C "$OTHER" add x.txt >/dev/null
git -C "$OTHER" commit -qm OTHER
NONREPO="$TMPROOT/nonrepo"
mkdir -p "$NONREPO"

# ═════════════════════════════════════════════════════════════════════════════
echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2984 AC-32: 착지 직전 secret·PII 스캔 — discriminating self-test"
echo "═══════════════════════════════════════════════════════════════════════════"
echo
echo "── Part 1: CWD 4-변종 (G1~G4) — 처방 ①②③ 의 필요성 + ②↔③ 상보성 실증 ──"

FXA="$TMPROOT/fx-secret"; mkdir -p "$FXA"
read -r A_WT A_ORIGIN A_SHA A_C1 <<< "$(fx_secret_mid "$FXA")"

# variant <cwd> <mode:naive|pipefail|fixed> → "rc hits misstok"
variant() {
  local cwd="$1" mode="$2" rc=0 oids hits misstok
  local obj="$TMPROOT/variant-$mode-$RANDOM.out"
  oids="$(git -C "$A_WT" rev-list --objects "$A_SHA" --not --remotes=origin | awk '{print $1}')"
  # 파일 캡처 = 객체 스트림의 널바이트가 command substitution 경고를 내지 않게(판정 무관, 노이즈 제거).
  case "$mode" in
    naive)
      ( cd "$cwd" && printf '%s\n' "$oids" | git cat-file --batch ) > "$obj" 2>&1 || rc=$?
      ;;
    pipefail)
      ( cd "$cwd" && set -o pipefail && printf '%s\n' "$oids" | git cat-file --batch ) \
        > "$obj" 2>&1 || rc=$?
      ;;
    fixed)
      # ★ 처방 적용: ② pipefail · ③ --batch-check 무결성 fail-closed · ① cat-file 에도 -C
      ( cd "$cwd" && set -o pipefail \
        && ! printf '%s\n' "$oids" | git -C "$A_WT" cat-file --batch-check 2>/dev/null \
             | grep -qE '^[0-9a-f]{40,64} (missing|dangling)$' \
        && printf '%s\n' "$oids" | git -C "$A_WT" cat-file --batch ) > "$obj" 2>&1 || rc=$?
      ;;
  esac
  hits="$(grep -ac "$SECRET" "$obj" || true)"
  misstok="$(grep -acE '(missing|dangling)$' "$obj" || true)"
  echo "$rc $hits $misstok"
}

read -r G1_RC G1_HIT G1_MISS <<< "$(variant "$NONREPO" naive)"
read -r G2_RC G2_HIT G2_MISS <<< "$(variant "$OTHER" naive)"
read -r G3_RC G3_HIT G3_MISS <<< "$(variant "$OTHER" pipefail)"
read -r G4_RC G4_HIT G4_MISS <<< "$(variant "$OTHER" fixed)"

printf '   G1 비-repo CWD  · 초판(-C 없음)      : rc=%s secret_hit=%s missing_tok=%s\n' "$G1_RC" "$G1_HIT" "$G1_MISS"
printf '   G2 다른 repo CWD · 초판(-C 없음)      : rc=%s secret_hit=%s missing_tok=%s\n' "$G2_RC" "$G2_HIT" "$G2_MISS"
printf '   G3 다른 repo CWD · 초판+pipefail      : rc=%s secret_hit=%s missing_tok=%s\n' "$G3_RC" "$G3_HIT" "$G3_MISS"
printf '   G4 다른 repo CWD · 처방 ①②③ 적용     : rc=%s secret_hit=%s missing_tok=%s\n' "$G4_RC" "$G4_HIT" "$G4_MISS"

# G1 — 에러로 잡힌다(rc≠0) ∧ secret 미검출 ∧ `missing` 토큰 0 (③ 가드는 G1 을 못 잡는다).
if [ "$G1_RC" -ne 0 ] && [ "$G1_HIT" -eq 0 ] && [ "$G1_MISS" -eq 0 ]; then
  ok "G1 비-repo CWD: rc=$G1_RC(≠0) ∧ hit 0 ∧ missing 토큰 0 — rc(②) 축만 잡는다"
else
  ng "G1 기대 이탈" "rc=$G1_RC hit=$G1_HIT missing=$G1_MISS (기대: rc≠0, hit=0, missing=0)"
fi

# G2 — ★★ 조용히 성공: rc=0 ∧ secret 미검출 ∧ missing 토큰 다수.
if [ "$G2_RC" -eq 0 ] && [ "$G2_HIT" -eq 0 ] && [ "$G2_MISS" -gt 0 ]; then
  ok "G2 다른 repo CWD: rc=0 ∧ hit 0 ∧ missing 토큰 $G2_MISS — 조용한 무검사(진짜 위험)"
else
  ng "G2 기대 이탈" "rc=$G2_RC hit=$G2_HIT missing=$G2_MISS (기대: rc=0, hit=0, missing>0)"
fi

# G3 — ★★ pipefail 무력: 여전히 rc=0 ∧ 미검출.
if [ "$G3_RC" -eq 0 ] && [ "$G3_HIT" -eq 0 ] && [ "$G3_MISS" -gt 0 ]; then
  ok "G3 pipefail 추가해도 rc=0 ∧ hit 0 — pipefail 은 rc=0 변종을 못 잡는다(②의 한계)"
else
  ng "G3 기대 이탈" "rc=$G3_RC hit=$G3_HIT missing=$G3_MISS (기대: rc=0, hit=0, missing>0)"
fi

# G4 — 처방 적용 시 DETECTED.
if [ "$G4_HIT" -ge 1 ] && [ "$G4_MISS" -eq 0 ]; then
  ok "G4 처방 ①②③ 적용: secret_hit=$G4_HIT ∧ missing 토큰 0 — DETECTED(착지 차단 가능)"
else
  ng "G4 기대 이탈" "rc=$G4_RC hit=$G4_HIT missing=$G4_MISS (기대: hit≥1, missing=0)"
fi

# ★ ②↔③ 상보성: 두 처방이 서로를 대체하지 못함을 한 명제로 결박.
if [ "$G1_MISS" -eq 0 ] && [ "$G1_RC" -ne 0 ] && [ "$G2_RC" -eq 0 ] && [ "$G2_MISS" -gt 0 ]; then
  ok "②↔③ 상보성: G1 은 ③(missing 토큰)이 못 잡고 ②(rc)만 · G2 는 ②가 못 잡고 ③만 — 대체 불가"
else
  ng "②↔③ 상보성 실증 실패" "G1(rc=$G1_RC,miss=$G1_MISS) G2(rc=$G2_RC,miss=$G2_MISS)"
fi

echo
echo "── Part 2: 스캔 primitive 정의역 + 술어 협착 (pipeline 수준 실측) ──"

# A/B/C — §7.12-B2 재현. ④ leg 의 근거: 2-tree 차분은 중간 커밋 secret 을 놓친다.
BASE_SHA="$(git -C "$A_WT" rev-parse "$A_SHA"^^)"   # BASE = C2 의 조부모
P_A="$(git -C "$A_WT" diff --unified=0 "$BASE_SHA".."$A_SHA" | grep -c "$SECRET" || true)"
P_B="$(git -C "$A_WT" rev-list --objects "$A_SHA" --not --remotes=origin | awk '{print $1}' \
       | git -C "$A_WT" cat-file --batch | grep -c "$SECRET" || true)"
P_C="$(git -C "$A_WT" log -p --unified=0 "$BASE_SHA".."$A_SHA" | grep -c "$SECRET" || true)"
assert_eq "P2-A 구 primitive(2-tree diff) 는 중간 커밋 secret 미검출" 0 "$P_A" "정의역 퇴화의 정체"
if [ "$P_B" -ge 1 ]; then
  ok "P2-B 신 primitive(rev-list --objects → cat-file --batch) 검출 = $P_B"
else
  ng "P2-B 신 primitive 미검출" "hit=$P_B (기대 ≥1)"
fi
if [ "$P_C" -ge 1 ]; then
  ok "P2-C 차선(log -p) 검출 = $P_C"
else
  ng "P2-C 차선 미검출" "hit=$P_C"
fi

# benign `missing` 문면 — 구 술어(--batch 합본) FIRE / 신 술어(--batch-check 헤더전용) silent.
FXC="$TMPROOT/fx-benign"; mkdir -p "$FXC"
read -r C_WT C_ORIGIN C_SHA <<< "$(fx_benign_missing "$FXC")"
C_OIDS="$(git -C "$C_WT" rev-list --objects "$C_SHA" --not --remotes=origin | awk '{print $1}')"
OLD_BENIGN="$(printf '%s\n' "$C_OIDS" | git -C "$C_WT" cat-file --batch \
              | grep -cE '[[:space:]](missing|dangling)$' || true)"
NEW_BENIGN="$(printf '%s\n' "$C_OIDS" | git -C "$C_WT" cat-file --batch-check \
              | grep -cE '^[0-9a-f]{40,64} (missing|dangling)$' || true)"
FAKE_OID="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
OLD_REAL="$(printf '%s\n%s\n' "$C_OIDS" "$FAKE_OID" | git -C "$C_WT" cat-file --batch \
            | grep -cE '[[:space:]](missing|dangling)$' || true)"
NEW_REAL="$(printf '%s\n%s\n' "$C_OIDS" "$FAKE_OID" | git -C "$C_WT" cat-file --batch-check \
            | grep -cE '^[0-9a-f]{40,64} (missing|dangling)$' || true)"
if [ "$OLD_BENIGN" -ge 1 ] && [ "$NEW_BENIGN" -eq 0 ]; then
  ok "P2-D benign 문면: 구 술어(--batch) FIRE=$OLD_BENIGN(오발화) / 신 술어(--batch-check)=0(silent)"
else
  ng "P2-D 술어 협착 실증 실패" "OLD=$OLD_BENIGN NEW=$NEW_BENIGN (기대 OLD≥1, NEW=0)"
fi
# ★ 형제 회귀 확인: 협착이 **진짜 누락 OID 검출력**을 파괴하지 않았는가 (봉합이 형제를 깨는 class).
if [ "$OLD_REAL" -ge 1 ] && [ "$NEW_REAL" -ge 1 ]; then
  ok "P2-E 형제 회귀 없음: 진짜 누락 OID 는 구·신 술어 둘 다 FIRE (OLD=$OLD_REAL NEW=$NEW_REAL)"
else
  ng "P2-E 협착이 검출력을 파괴" "OLD_REAL=$OLD_REAL NEW_REAL=$NEW_REAL (둘 다 ≥1 이어야)"
fi

# F — 범위 하한 (E 는 상한, F 는 하한을 지킨다).
FXD="$TMPROOT/fx-range"; mkdir -p "$FXD"
read -r D_WT D_ORIGIN D_SHA D_UP <<< "$(fx_range_lower "$FXD")"
F1="$(git -C "$D_WT" rev-list --objects "$D_UP".."$D_SHA" | awk '{print $1}' \
      | git -C "$D_WT" cat-file --batch | grep -c "$SECRET" || true)"
F2="$(git -C "$D_WT" rev-list --objects "$D_SHA" --not --remotes=origin | awk '{print $1}' \
      | git -C "$D_WT" cat-file --batch | grep -c "$SECRET" || true)"
F3="$(git -C "$D_WT" rev-list --objects "$D_SHA" | awk '{print $1}' \
      | git -C "$D_WT" cat-file --batch | grep -c "$SECRET" || true)"
assert_eq "P2-F1 올바른 range(<upstream>..SHA) → 0" 0 "$F1" "이미 원격에 있는 과거 secret 은 본 착지의 책임 아님"
assert_eq "P2-F2 채택 baseline(SHA --not --remotes=origin) → 0" 0 "$F2" "F1 과 동치 — 신규 브랜치에서도 동작"
assert_eq "P2-F3 mutant(--not 누락) → 1 (거짓양성 RED)" 1 "$F3" "하한을 잃으면 전 이력이 finding 이 된다"

echo
echo "── Part 3: SUT 결박 (scripts/check-salvage-bundle.sh) — CWD ≠ worktree 강제 ──"

SUT_PRESENT=0
if [ -f "$SUT" ]; then
  SUT_PRESENT=1
else
  ng "SUT 부재: $SUT — AC-32 결박 legs(Part 3/4) 미실행" \
     "AC-32 는 실 스캔 게이트의 동작을 요구한다. G1 산출 착지 전까지 RED 가 정상이다." \
     "미실행 leg: S-E(clean 대조군) S-REF(참조형 값 대조군) S-BEN(benign missing) S-M4(중간커밋 secret)" \
     "            S-NONREPO(비-repo CWD) SM-1(스캔 제거) SM-2(TOCTOU) SM-3(glob) SM-4(primitive 퇴화)"
fi

# sut_land <cwd> <wt> <branch> [sha] — SUT 를 CWD≠wt 에서 실행. 결과: 전역 SUT_RC / SUT_OUT
sut_land() {
  local cwd="$1" wt="$2" branch="$3" sha="${4:-}" root="$5"
  local args=(--land --worktree "$wt" --remote origin --branch "$branch")
  [ -z "$sha" ] || args+=(--sha "$sha")
  SUT_RC=0
  SUT_OUT="$(cd "$cwd" && bash "$root/scripts/check-salvage-bundle.sh" "${args[@]}" 2>&1)" || SUT_RC=$?
}

origin_landed() { # <origin> <branch> → 착지한 SHA (없으면 빈 문자열)
  git -C "$1" rev-parse --verify -q "refs/heads/$2" 2>/dev/null || true
}

origin_has_secret() { # <origin> → 0 = secret 존재
  git -C "$1" rev-list --objects --all 2>/dev/null | awk '{print $1}' \
    | git -C "$1" cat-file --batch 2>/dev/null | grep -q "$SECRET"
}

# 마커 축 — rc·착지(ground truth) 와 **분리된 보조 축**. 마커만으로 판정하지 않는다
#   (자기 보고 문자열은 ground truth 가 아니다 — 착지 여부가 정본).
assert_marker() { # <name> <expected marker line>
  if printf '%s' "$SUT_OUT" | grep -qx -- "$2"; then
    ok "$1 (마커 '$2')"
  else
    ng "$1 — 마커 '$2' 부재" "$SUT_OUT"
  fi
}

if [ "$SUT_PRESENT" -eq 1 ]; then
  # S-E — clean-input 대조군: 0-finding ∧ 정상 완료(push 도달). 없으면 "항상 RED" 구현이 통과한다.
  FXB="$TMPROOT/fx-clean"; mkdir -p "$FXB"
  read -r B_WT B_ORIGIN B_SHA <<< "$(fx_clean "$FXB")"
  sut_land "$OTHER" "$B_WT" salvage-clean "" "$REPO_ROOT"
  LANDED="$(origin_landed "$B_ORIGIN" salvage-clean)"
  if [ "$SUT_RC" -eq 0 ] && [ "$LANDED" = "$B_SHA" ]; then
    ok "S-E clean-input 대조군: rc=0 ∧ push 도달(refs/heads/salvage-clean = $B_SHA)"
  else
    ng "S-E clean-input 대조군 실패 — '항상 RED' 게이트 의심" \
       "rc=$SUT_RC landed='$LANDED' expected='$B_SHA'" "$SUT_OUT"
  fi
  assert_marker "S-E 마커" "SCAN_RESULT: clean"
  assert_marker "S-E 마커" "PUSH: done"

  # S-REF — 참조형 값 대조군: 번들이 자기 스키마가 요구하는 40hex SHA · blob:sha256:<64hex> 를
  #   담아도 0-finding. (식별자 표기를 secret 으로 판정하면 스키마 자신이 게이트를 막는다.)
  if [ "$SUT_RC" -eq 0 ]; then
    ok "S-REF 참조형 값 대조군: last_commit_sha(40hex)+blob:sha256(64hex) 보유 번들이 0-finding"
  else
    ng "S-REF 참조형 값 대조군 실패" \
       "ADR-179 §결정 2-U allowlist 가 요구하는 값(40hex SHA 등)이 finding 으로 판정됨 — born-RED" \
       "$SUT_OUT"
  fi

  # S-BEN — benign `missing` 문면 대조군: 0-finding ∧ push 도달. 술어를 되돌리면 여기가 RED 로 전환.
  FXC2="$TMPROOT/fx-benign2"; mkdir -p "$FXC2"
  read -r C2_WT C2_ORIGIN C2_SHA <<< "$(fx_benign_missing "$FXC2")"
  sut_land "$OTHER" "$C2_WT" salvage-benign "" "$REPO_ROOT"
  LANDED="$(origin_landed "$C2_ORIGIN" salvage-benign)"
  if [ "$SUT_RC" -eq 0 ] && [ "$LANDED" = "$C2_SHA" ]; then
    ok "S-BEN benign missing 문면: rc=0 ∧ push 도달 — ③ 술어 협착 유지(회귀 앵커)"
  else
    ng "S-BEN benign 대조군 실패 — ③ 술어가 일상 문면에 오발화" \
       "rc=$SUT_RC landed='$LANDED' expected='$C2_SHA'" "$SUT_OUT"
  fi

  # S-M4 — ★ mutant ④: 중간 커밋에만 secret. 검출 ∧ **push 미도달**.
  FXA2="$TMPROOT/fx-secret2"; mkdir -p "$FXA2"
  read -r A2_WT A2_ORIGIN A2_SHA A2_C1 <<< "$(fx_secret_mid "$FXA2")"
  sut_land "$OTHER" "$A2_WT" salvage-secret "" "$REPO_ROOT"
  LANDED="$(origin_landed "$A2_ORIGIN" salvage-secret)"
  if [ "$SUT_RC" -ne 0 ] && [ -z "$LANDED" ] && ! origin_has_secret "$A2_ORIGIN"; then
    ok "S-M4 중간 커밋 전용 secret: rc=$SUT_RC(≠0) ∧ 착지 0 ∧ 원격 secret 0 — 차단됨"
  else
    ng "S-M4 실패 — 중간 커밋 secret 이 스캔을 통과했거나 착지했다" \
       "rc=$SUT_RC landed='$LANDED'" "$SUT_OUT"
  fi
  assert_marker "S-M4 마커" "SCAN_RESULT: finding"
  assert_marker "S-M4 마커" "PUSH: skipped"

  # S-UNDEC — 판정 불가를 **통과로 접지 않는다**(F-3 fail-open 대응). 입력 cap 초과 blob.
  #   "스캔 미통과 상태로 착지 0건" 의 미통과에는 판정 불가가 포함된다.
  FXU="$TMPROOT/fx-undec"; mkdir -p "$FXU"
  git_init_pair "$FXU"
  python3 -c "import sys; open(sys.argv[1],'w',newline='\n').write('a'*1200000+'\n')" \
    "$FXU/wt/huge.txt"
  git -C "$FXU/wt" add huge.txt >/dev/null
  git -C "$FXU/wt" commit -qm HUGE
  U_SHA="$(git -C "$FXU/wt" rev-parse HEAD)"
  sut_land "$OTHER" "$FXU/wt" salvage-undec "" "$REPO_ROOT"
  LANDED="$(origin_landed "$FXU/origin.git" salvage-undec)"
  if [ "$SUT_RC" -ne 0 ] && [ -z "$LANDED" ]; then
    ok "S-UNDEC 입력 cap 초과(판정 불가): rc=$SUT_RC ∧ 착지 0 — 통과로 접지 않음 (SHA $U_SHA)"
  else
    ng "S-UNDEC 실패 — 판정 불가가 통과로 접혔다(fail-open)" \
       "rc=$SUT_RC landed='$LANDED'" "$SUT_OUT"
  fi
  assert_marker "S-UNDEC 마커" "SCAN_RESULT: undecidable"

  # S-NONREPO — 비-repo CWD 에서도 동일 판정(처방 ① 이 CWD 의존을 제거했는가).
  FXA3="$TMPROOT/fx-secret3"; mkdir -p "$FXA3"
  read -r A3_WT A3_ORIGIN A3_SHA A3_C1 <<< "$(fx_secret_mid "$FXA3")"
  sut_land "$NONREPO" "$A3_WT" salvage-secret "" "$REPO_ROOT"
  LANDED="$(origin_landed "$A3_ORIGIN" salvage-secret)"
  if [ "$SUT_RC" -ne 0 ] && [ -z "$LANDED" ]; then
    ok "S-NONREPO 비-repo CWD 에서도 검출 ∧ 착지 0 (rc=$SUT_RC) — CWD 의존 제거 확인"
  else
    ng "S-NONREPO 실패" "rc=$SUT_RC landed='$LANDED'" "$SUT_OUT"
  fi

  # S-TOCTOU-BASE — baseline: 스캔한 그 SHA(C2)만 나간다. HEAD(C3)의 secret 은 원격에 없어야.
  FXE="$TMPROOT/fx-toctou"; mkdir -p "$FXE"
  read -r E_WT E_ORIGIN E_C2 E_C3 <<< "$(fx_toctou "$FXE")"
  sut_land "$OTHER" "$E_WT" salvage-toctou "$E_C2" "$REPO_ROOT"
  LANDED="$(origin_landed "$E_ORIGIN" salvage-toctou)"
  if [ "$SUT_RC" -eq 0 ] && [ "$LANDED" = "$E_C2" ] && ! origin_has_secret "$E_ORIGIN"; then
    ok "S-TOCTOU baseline: 스캔 SHA(C2)만 착지 ∧ 이후 재기록분(C3 secret) 원격 부재"
  else
    ng "S-TOCTOU baseline 실패 — 착지 산출물 ≠ 스캔 산출물" \
       "rc=$SUT_RC landed='$LANDED' expected C2='$E_C2' (HEAD C3='$E_C3')" "$SUT_OUT"
  fi
fi

echo
echo "── Part 4: mutant kill (SUT 변이 — baseline PASS ∧ mutated RED 쌍으로만 성립) ──"

MUT="$TMPROOT/mutate.py"
cat > "$MUT" <<'PYEOF'
#!/usr/bin/env python3
"""AC-32 mutation applier — SUT 사본에 변이를 적용. 앵커 부재 = exit 3(큰 소리로 실패).

언어 비의존 앵커: 구분자를 캡처해 bash 문자열형(`rev-list --objects`)과
python 리스트형(`"rev-list", "--objects"`) 양쪽에 같은 규칙이 적용된다.
"""
import re
import sys
from pathlib import Path

KINDS = {
    # ③ glob 배제 — 객체 목록에 pathspec 을 주입해 번들 경로를 스캔 대상에서 제외.
    "glob": [(r"--not(['\"\s,]+)--remotes=origin",
              r"--not\1--remotes=origin\1--\1README.md")],
    # ④ primitive 퇴화 — 최종 tree 만 보게 만들어 중간 커밋을 놓치게 한다(2-tree 차분 등가).
    "degrade": [(r"rev-list(['\"\s,]+)--objects",
                 r"rev-list\1--objects\1--max-count=1")],
    # ② TOCTOU — 고정 SHA 대신 HEAD 를 push (스캔 산출물 ≠ 착지 산출물).
    "toctou": [(r"%\s*\(\s*sha\s*,\s*branch\s*\)", r'% ("HEAD", branch)'),
               (r"\"\$SHA\"(:refs/heads/)", r'"HEAD"\1'),
               (r"\$\{SHA\}(:refs/heads/)", r"HEAD\1"),
               (r"\$SHA(:refs/heads/)", r"HEAD\1"),
               (r"\{sha\}(:refs/heads/)", r"HEAD\1"),
               (r"sha\s*\+\s*(['\"]):refs/heads/", r"'HEAD' + \1:refs/heads/")],
}


def main():
    tree, kind = Path(sys.argv[1]), sys.argv[2]
    rules = KINDS[kind]
    applied = 0
    for p in sorted(list(tree.rglob("*.py")) + list(tree.rglob("*.sh"))):
        src = p.read_text(encoding="utf-8", errors="replace")
        out = src
        for pat, rep in rules:
            out, n = re.subn(pat, rep, out)
            applied += n
        if out != src:
            p.write_text(out, encoding="utf-8", newline="\n")
    if applied == 0:
        print(f"::error::mutation '{kind}' 앵커 부재 — SUT 구현 형태 drift (변이 미적용)",
              file=sys.stderr)
        return 3
    print(f"mutation '{kind}' applied={applied}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
PYEOF

# mk_mutant_tree <dest> <kind|stub-redactor> → SUT 사본 + 변이. rc 3 = 앵커 drift.
mk_mutant_tree() {
  local dest="$1" kind="$2" rc=0
  mkdir -p "$dest/scripts/lib"
  cp "$SUT" "$dest/scripts/"
  cp "$REPO_ROOT/scripts/lib/"*.py "$dest/scripts/lib/" 2>/dev/null || true
  if [ "$kind" = "stub-redactor" ]; then
    # ① 스캔 단계 제거 — 탐지 엔진을 no-op 으로 치환(구현 형태 비의존).
    #   ★ 계약면(RULE_NAMES·cap 상수)은 **원본과 동일하게 유지**한다. 값공간을 비우면 SUT 의
    #     룰-이름 drift 가드가 `undecidable` 로 fail-closed 해버려 **스캔 경로를 통과하지 못하고**,
    #     그러면 이 mutant 는 "탐지 제거" 가 아니라 "무결성 가드 발동" 을 시험하게 된다(정의역 오염).
    #     따라서 인터페이스는 온전히 두고 **발화만 침묵**시켜 탐지 경로만 정확히 겨눈다.
    {
      printf '%s\n' '"""AC-32 mutant stub — 탐지 발화만 침묵(인터페이스·값공간은 원본 동일)."""'
      grep -E '^(BYTE_CAP|LINE_CAP|PARSE_TIMEOUT_S) =|^RULE_[A-Z_]+ = "' "$REDACTOR"
      sed -n '/^RULE_NAMES = frozenset({/,/^})/p' "$REDACTOR"
      printf '\n\ndef redact(raw):\n'
      printf '    return (raw if isinstance(raw, str) else ""), {\n'
      printf '        "redaction_applied": False, "redaction_count": 0, "redaction_rules_fired": [],\n'
      printf '    }\n'
    } > "$dest/scripts/lib/redact_dev_process_content.py"
  else
    python3 "$MUT" "$dest" "$kind" >/dev/null 2>&1 || rc=$?
  fi
  return $rc
}

# mutant_case <name> <kind> <fixture:secret|toctou> — baseline 은 Part 3 에서 이미 확보됨
mutant_case() {
  local name="$1" kind="$2" fx="$3" rc=0 dest wt origin sha c1 c2 c3 landed leaked
  dest="$TMPROOT/mut-$kind-$RANDOM"
  mk_mutant_tree "$dest" "$kind" || rc=$?
  if [ "$rc" -eq 3 ]; then
    ng "$name — 변이 앵커 부재(SUT 구현 형태 drift)" \
       "mutate.py 가 적용할 앵커를 찾지 못했다. SUT 계약 재확인 필요(보고 대상)."
    return 0
  fi

  local d="$TMPROOT/fxm-$kind-$RANDOM"; mkdir -p "$d"
  if [ "$fx" = "toctou" ]; then
    read -r wt origin c2 c3 <<< "$(fx_toctou "$d")"
    SUT_RC=0
    SUT_OUT="$(cd "$OTHER" && bash "$dest/scripts/check-salvage-bundle.sh" \
      --land --worktree "$wt" --remote origin --branch m --sha "$c2" 2>&1)" || SUT_RC=$?
    landed="$(origin_landed "$origin" m)"
    leaked=1
    origin_has_secret "$origin" && leaked=0
    # killed ⟺ 변이가 결과를 바꿨다: C3 착지 또는 원격 secret 유입.
    if [ "$leaked" -eq 0 ] || { [ -n "$landed" ] && [ "$landed" = "$c3" ]; }; then
      ok "$name — mutant killed (착지='$landed' C3='$c3' 원격secret=$([ $leaked -eq 0 ] && echo 있음 || echo 없음))"
    else
      ng "$name — mutant survived (오라클이 TOCTOU 를 구별하지 못한다)" \
         "rc=$SUT_RC landed='$landed' c2='$c2' c3='$c3'" "$SUT_OUT"
    fi
  else
    read -r wt origin sha c1 <<< "$(fx_secret_mid "$d")"
    SUT_RC=0
    SUT_OUT="$(cd "$OTHER" && bash "$dest/scripts/check-salvage-bundle.sh" \
      --land --worktree "$wt" --remote origin --branch m 2>&1)" || SUT_RC=$?
    landed="$(origin_landed "$origin" m)"
    # baseline(Part 3 S-M4) = rc≠0 ∧ 착지 0. killed ⟺ 변이 하에서 통과(rc=0) 또는 착지 발생.
    if [ "$SUT_RC" -eq 0 ] || [ -n "$landed" ]; then
      ok "$name — mutant killed (변이 하에서 통과: rc=$SUT_RC 착지='$landed')"
    else
      ng "$name — mutant survived (변이해도 여전히 차단 — 검출 경로가 변이 지점과 무관)" \
         "rc=$SUT_RC landed='$landed'" "$SUT_OUT"
    fi
  fi
}

if [ "$SUT_PRESENT" -eq 1 ]; then
  mutant_case "SM-1 ①스캔 제거(탐지 엔진 no-op 치환)" stub-redactor secret
  mutant_case "SM-2 ②재기록 TOCTOU(고정 SHA→HEAD push)" toctou toctou
  mutant_case "SM-3 ③glob 배제(객체 목록에 pathspec 주입)" glob secret
  mutant_case "SM-4 ④primitive 퇴화(--max-count=1 = 최종 tree 만)" degrade secret
fi

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS cases pass — 4-변종/primitive 정의역/술어 협착/대조군 3종/mutant 4종 결박"
  echo "   (보장 범위 = L1 경유 착지 경로 한정. raw git push 우회는 L1 정의역 밖 — L3 사후 탐지.)"
  exit 0
else
  echo "X $FAIL case(s) failed"
  exit 1
fi
