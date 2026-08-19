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
UNDEC=0

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

# undec — 제3상태 방출기. 「판정 불가」를 「위반」으로 접지 않는다(§3.8.1 4-arm 라우팅,
#   `vacuous:` / `invalid:` 선례와 동형).
#   ★ 이 helper 가 없던 동안 CI 는 기저선 커밋 미판독을 「동결 파일이 변경됐다」로 방출했다 —
#     shallow checkout(depth 1) 에서 rc≠0 이 {변경됨(rc=1)} 과 {객체 부재(rc=128)} 를 한 칸으로
#     접은 결과다. 검사기가 0/실패를 낼 때 「대상 부재」와 「규칙 파손」을 구별하지 못하면
#     본 Story §1 이 표적하는 「미관측을 관측된 값으로 보고」가 검사기 자신에게서 재현된다.
#   계상 규율: PASS 아님 ∧ FAIL 아님 — **충족 계상에서 제외**한다. 다만 leg 귀결은 fail-closed
#     (종료코드 3): 「못 읽었으니 통과」는 같은 병의 반대 방향이므로 GREEN 으로 접지 않는다.
#     세 상태가 출력에서 갈린다 — `OK PASS:` / `X FAIL:` / `? UNDECIDABLE:`.
undec() {
  echo "? UNDECIDABLE: $1"
  shift
  for l in "$@"; do echo "    $l"; done
  UNDEC=$((UNDEC+1))
}

# ═════════════════════════════════════════════════════════════════════════════
# CFP-2995 AC-17 — 판별기 SSOT + gate 모드 조기 분기 (Change Plan §3.8 / §9.8)
#
#   흡수 근거(§9.8): 신규 `.sh` 를 만들면 ADR-151 인벤토리 bijection(전수 enroll)과 실행자
#   명시 열거(invariant-check.yml)가 Phase 1 에서 동시에 깨진다 — **등재해도 RED, 안 해도 RED**.
#   ⇒ 이미 열거돼 있고 이미 phase 1·2 인 본 파일에 싣는다.
#   ★ 정직 비용(숨기지 않는다): 응집이 나빠진다 — 「번들 pre-push redaction」 self-test 안에
#     「Story 범위 경계 판정」이 들어간다. 주제 정합보다 **실행 가능성**을 택한 대가다.
#
#   판정기는 **단일 정본**이다: gate 모드(실 PR)와 self-test 모드(합성 경로)가 같은
#   `ac17_judge` 를 통과한다 — 두 벌로 두면 판별력 leg 이 실 판정과 무관해진다.
# ═════════════════════════════════════════════════════════════════════════════

AC17_BASELINE="6bb0e8aa5be0c5bec9bcb9c672174417e633eacb"
AC17_LIVE=".github/workflows/ac-traceability-matrix.yml"
AC17_TWIN="templates/github-workflows/ac-traceability-matrix.yml"
AC17_STEP_NAME="AC-17 scope-boundary gate"
AC17_FLOOR="scripts/lib/check_salvage_bundle.py"

# ac17_extract_deny <원문.md> — 원문에서 접근 금지 목록을 추출(1행 1경로).
#   앵커 = 「AC-17 기계 가드의 목록 대상」 문자열. Story §4.3(g) 와 §5.4 non-goal 8 이
#   **둘 다** 이 문자열을 담는다(원문 실측 2 hit) — 좌표가 아니라 **내용 유래** 앵커다.
#   §3.9 방출 어휘 폐집합: 호출부는 **개수만** 방출하고 목록 자체를 로그에 싣지 않는다
#   (PRIVATE Story 원문이 PUBLIC Actions 로그에 비가역 착지하는 것을 막는다).
ac17_extract_deny() {
  python3 - "$1" <<'AC17PY'
import io, re, sys
MARK = "AC-17 기계 가드의 목록 대상"
PATH = re.compile(r'`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:py|sh|yml|yaml|md))`')
try:
    lines = io.open(sys.argv[1], encoding="utf-8", newline="").read().split("\n")
except OSError:
    sys.exit(2)
deny = set()
for line in lines:
    if MARK in line:
        deny.update(PATH.findall(line))
for p in sorted(deny):
    print(p)
AC17PY
}

# ac17_judge <금지목록파일> <변경경로파일> — AC-17 판정기(단일 정본).
#   판정 축 ② = 양 피연산자 non-empty **선확인**(부재-assert 항진 차단 — 빈 집합끼리의
#     「변경 0건」은 언제나 참이라 판정이 아니다).
#   floor 대조 = §4.3(g)·§5.4 non-goal 8 소유면 원소 포함 확인(**과소모집 차단** — 목록이
#     불완전한 채로 판정하면 가장 최근에 생긴 경계에 정확히 구멍이 뚫린다).
#   방출 = 개수 + 사유 enum **만**(§3.9 폐집합).
ac17_judge() {
  local deny="$1" changed="$2" n
  if [ ! -s "$deny" ];    then echo "undecidable: 금지 목록 공허 — 판정 축 ② 미충족"; return 1; fi
  if [ ! -s "$changed" ]; then echo "undecidable: 변경 경로 집합 공허 — 판정 축 ② 미충족"; return 1; fi
  if ! grep -qxF "$AC17_FLOOR" "$deny"; then
    echo "undecidable: 금지 목록 floor 미충족 — 소유면 원소 과소모집"
    return 1
  fi
  # grep 의 rc 는 pass/fail 신호가 아니다(무매치 rc=1 = 위반 0 = 정상). 하류 카운터 n 이
  #   유일 판정 신호이며 아래에서 그 값으로 단언한다 — exit-masking 아닌 counter-backup.
  n="$( { grep -xFf "$deny" "$changed" || true; } | wc -l | tr -d '[:space:]' )"
  echo "violations=$n"
  [ "$n" -eq 0 ]
}

# gate 모드 — ac-traceability-matrix.yml 의 additive step 이 **실 PR** 로 위임하는 경로.
#   이 분기는 self-test 픽스처를 만들지 않고 즉시 판정 후 종료한다(러너 시간 0 낭비).
if [ "${CFP2995_AC17_MODE:-}" = "gate" ]; then
  AC17_GATE_DENY="$TMPROOT/ac17-gate-deny.txt"
  AC17_GATE_RC=0
  ac17_extract_deny "${CFP2995_AC17_SOURCE:?}" > "$AC17_GATE_DENY" || AC17_GATE_RC=$?
  if [ "$AC17_GATE_RC" -ne 0 ]; then
    echo "undecidable: 원문 판독 실패 — fail-closed"
    exit 1
  fi
  AC17_GATE_RC=0
  ac17_judge "$AC17_GATE_DENY" "${CFP2995_AC17_CHANGED:?}" || AC17_GATE_RC=$?
  exit "$AC17_GATE_RC"
fi


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

# ─────────────────────────────────────────────────────────────────────────────
# ★ crash-as-RED 차단 (CFP-2984 G7 감사 — 실사건 회귀 방지)
#   본 파일의 **kill 판정**은 ground truth(착지 SHA·원격 secret 유입)라서 크래시로는 충족
#   불가 — mutant 축은 구조적으로 crash-safe 다.
#   그러나 **차단 계열 baseline**(S-M4 · S-UNDEC · S-NONREPO)은 `rc≠0 ∧ 착지 0` 을 성공으로
#   읽는다. SUT 가 예외로 죽어도 정확히 그 모양이 되므로 **크래시가 '차단됨' 으로 위장**한다.
#   그 상태에서는 스캔이 한 줄도 돌지 않았는데 전 차단 케이스가 GREEN 이 된다.
#   ★ SyntaxError·IndentationError 는 Traceback 머리글 없이 출력된다(실측) — 함께 본다.
#   ★ 여기서 FAIL 을 세면 하류 판정이 무엇을 내든 스위트는 반드시 RED 가 된다(fail-loud).
#
#   ★ P2-6 보강 — 스위트 RED 와 **케이스 판정**은 다른 축이다.
#     기존에는 sut_land 가 ng 로 FAIL 을 세어 스위트는 RED 였지만, 하류 케이스식
#     `rc≠0 ∧ 착지 0` 은 크래시 상태에서도 그대로 참이라 S-M4·S-UNDEC·S-NONREPO 가
#     **케이스 수준에서는 `OK PASS`** 를 찍었다. SUT 100% 크래시에서 "차단됨" 3줄이 출력되는
#     화면은 그 자체로 거짓 증거다(리뷰가 실증). → SUT_CRASHED 플래그를 케이스식에 AND 한다.
# ─────────────────────────────────────────────────────────────────────────────
crash_marker() { # <output> → 0 = 크래시 흔적 있음
  case "$1" in
    *Traceback*|*SyntaxError*|*IndentationError*|*TabError*) return 0 ;;
  esac
  return 1
}

# sut_land <cwd> <wt> <branch> [sha] — SUT 를 CWD≠wt 에서 실행.
#   결과: 전역 SUT_RC / SUT_OUT / SUT_CRASHED(1 = 크래시 — 케이스 판정에서 AND 로 소거)
sut_land() {
  local cwd="$1" wt="$2" branch="$3" sha="${4:-}" root="$5"
  local args=(--land --worktree "$wt" --remote origin --branch "$branch")
  [ -z "$sha" ] || args+=(--sha "$sha")
  SUT_RC=0
  SUT_CRASHED=0
  SUT_OUT="$(cd "$cwd" && bash "$root/scripts/check-salvage-bundle.sh" "${args[@]}" 2>&1)" || SUT_RC=$?
  if crash_marker "$SUT_OUT"; then
    SUT_CRASHED=1
    ng "SUT 크래시(오라클 예외) — branch=$branch. rc≠0 을 '차단됨' 으로 읽을 수 없다" "$SUT_OUT"
  fi
}

# 차단 계열 케이스 전용 전제 — 크래시면 그 케이스의 '차단됨' 판정 자체를 성립시키지 않는다.
sut_ran() { [ "${SUT_CRASHED:-0}" -eq 0 ]; }

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
  if sut_ran && [ "$SUT_RC" -ne 0 ] && [ -z "$LANDED" ] && ! origin_has_secret "$A2_ORIGIN"; then
    ok "S-M4 중간 커밋 전용 secret: rc=$SUT_RC(≠0) ∧ 착지 0 ∧ 원격 secret 0 — 차단됨"
  else
    ng "S-M4 실패 — 중간 커밋 secret 이 스캔을 통과했거나 착지했다(또는 SUT 크래시)" \
       "rc=$SUT_RC landed='$LANDED' crashed=${SUT_CRASHED:-0}" "$SUT_OUT"
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
  if sut_ran && [ "$SUT_RC" -ne 0 ] && [ -z "$LANDED" ]; then
    ok "S-UNDEC 입력 cap 초과(판정 불가): rc=$SUT_RC ∧ 착지 0 — 통과로 접지 않음 (SHA $U_SHA)"
  else
    ng "S-UNDEC 실패 — 판정 불가가 통과로 접혔다(fail-open) 또는 SUT 크래시" \
       "rc=$SUT_RC landed='$LANDED' crashed=${SUT_CRASHED:-0}" "$SUT_OUT"
  fi
  assert_marker "S-UNDEC 마커" "SCAN_RESULT: undecidable"

  # S-NONREPO — 비-repo CWD 에서도 동일 판정(처방 ① 이 CWD 의존을 제거했는가).
  FXA3="$TMPROOT/fx-secret3"; mkdir -p "$FXA3"
  read -r A3_WT A3_ORIGIN A3_SHA A3_C1 <<< "$(fx_secret_mid "$FXA3")"
  sut_land "$NONREPO" "$A3_WT" salvage-secret "" "$REPO_ROOT"
  LANDED="$(origin_landed "$A3_ORIGIN" salvage-secret)"
  if sut_ran && [ "$SUT_RC" -ne 0 ] && [ -z "$LANDED" ]; then
    ok "S-NONREPO 비-repo CWD 에서도 검출 ∧ 착지 0 (rc=$SUT_RC) — CWD 의존 제거 확인"
  else
    ng "S-NONREPO 실패(또는 SUT 크래시)" \
       "rc=$SUT_RC landed='$LANDED' crashed=${SUT_CRASHED:-0}" "$SUT_OUT"
  fi
  # ★ P2-6: rc≠0 은 '스캔이 돌아 finding 이 났다' 와 '아무것도 못 하고 죽었다' 를 구별 못 한다.
  #   마커를 요구해 **검출 경로를 실제로 통과했다** 는 양(positive) 증거를 남긴다.
  assert_marker "S-NONREPO 마커" "SCAN_RESULT: finding"
  assert_marker "S-NONREPO 마커" "PUSH: skipped"

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
    # (a) 구 bash/리터럴 형태  (b) S-P1-1 봉합 후 python 형태 `"--remotes=%s" % remote`
    #     (b) 는 **리스트 원소 뒤**에 pathspec 을 넣는다 — `% remote` 앞에 끼우면 SyntaxError/TypeError
    #     로 죽고, 그러면 mutant 가 "탐지돼서" 가 아니라 "터져서" kill 되는 hollow kill 이 된다.
    "glob": [(r"--not(['\"\s,]+)--remotes=origin",
              r"--not\1--remotes=origin\1--\1README.md"),
             (r"(\"--remotes=%s\"\s*%\s*remote)\]", r'\1, "--", "README.md"]'),
             # (c) S-10 봉합 후 형태 — 제외집합이 stdin 이라 rev-list argv 자체가 앵커다.
             (r'(\["rev-list", "--objects", "--stdin"\])',
              r'["rev-list", "--objects", "--stdin", "--", "README.md"]')],
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

# ═════════════════════════════════════════════════════════════════════════════
# Part 5 — SCAN_BLOCKING_RULES 9룰 결박 (구현리뷰 P1-3)
#
# 결함: `SCAN_BLOCKING_RULES` (check_salvage_bundle.py:555-565) 는 SUT 정의부 밖에서
#   참조하는 테스트가 0 이었다. 스캔 픽스처의 secret 페이로드가 1종
#   (`AKIAIOSFODNN7EXAMPLE` = cloud_key)뿐이라, 차단집합을 `("cloud_key",)` 로
#   **9→1 축소해도 self-test 전건이 GREEN** 이었다(리뷰 실증).
#   → 넓힘 방향은 대조군 3종(S-E/S-REF/S-BEN)이 이미 결박한다(되돌리면 즉시 RED).
#     **축소 방향만 열려 있었다.** 여기서 닫는다.
#
# 관측면 2층:
#   ① S-BR-SET   — 집합 멤버십 정확 일치(축소·확대 양방향 즉시 검출). 싸다.
#   ② S-BR-FIRE  — 9룰 **각각**에 전용 페이로드를 물려 실제로 차단 판정이 나는지.
#                  ①만 두면 "이름은 있는데 발화하지 않는 룰" 을 못 본다 — 그 천장을 ②가 닫는다.
#   ③ S-BR-DROP  — 룰 1종씩 제거한 변이 9개. 해당 페이로드가 차단→통과로 **전환**해야 killed.
#                  ②가 "발화한다" 를 보이면 ③은 "그 발화가 차단에 load-bearing 하다" 를 보인다.
#   ④ S-BR-1     — 9→1 전면 축소. 나머지 8종이 전부 통과로 전환돼야 killed.
#
#   ★ 전용 페이로드 9종은 각각 **정확히 1룰만** 발화함을 실측 확인했다(룰 간 중복 발화 0).
#     이 격리 덕분에 ③의 per-rule 전환 판정이 성립한다.
#   ★ 정직 천장: 관측 대상은 "차단집합 멤버십 + 각 멤버의 차단 기여" 다.
#     탐지기 정규식 자체의 재현율(어떤 실 secret 형태를 놓치는가)은 본 축 밖 —
#     예: URL basic-auth · raw hex 는 9룰 어디에도 안 걸린다. JWT 는 최대 연속 토큰별 독립 판정이라 문맥 표지 없는 단독 입력에서 길이 하한과 엔트로피 하한을 함께 넘는 토큰이 하나라도 있으면 cloud_key 로 걸리고 그런 토큰이 하나도 없으면 룰 0 발화이며, 헤더 문맥과 자격증명 키 문맥과 env-dump 전체 제외 문맥에 감싸인 입력은 그 문맥 룰이 선행 발화해 걸린다(ADR-179 §7 F-12).
# ═════════════════════════════════════════════════════════════════════════════
echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Part 5 — SCAN_BLOCKING_RULES 9룰 결박 (P1-3)"
echo "═══════════════════════════════════════════════════════════════════════════"

BR_PROBE="$TMPROOT/br_probe.py"
cat >"$BR_PROBE" <<'PYEOF'
"""차단집합 + 룰별 차단 기여 관측 probe.

크래시하면 `::br-done::` 을 내지 않는다 — 상류 bash 가 그 부재를 harness FAIL 로 끊으므로
'출력 없음' 이 조용히 kill 로 오독되지 않는다.
"""
import importlib.util
import sys
import traceback

target = sys.argv[1]

# 룰별 전용 페이로드 — 각각 정확히 1룰만 발화(실측). 실 자격증명 0.
#   ★ `ghp_`·`github_pat_` 접두는 런타임 결합으로 만든다(소스에 리터럴 토큰 패턴을 남기지 않음).
G36 = "a1b2c3d4e5" * 3 + "f6g7h8"
G82 = ("A" * 41) + ("b" * 41)
ENVD = "\n".join("VAR%d=value%d" % (i, i) for i in range(10))

CASES = [
    ("private_key_block",
     "-----BEGIN RSA PRIVATE KEY-----\nZZZZ\n-----END RSA PRIVATE KEY-----"),
    ("authorization_header", "Authorization: Bearer tokvalue123456"),
    ("cookie_header", "Cookie: sid=abc123xyz"),
    ("github_pat", "ghp" + "_" + G36),
    ("github_fine_grained_pat", "github" + "_pat_" + G82),
    ("cloud_key", "AKIA" + "IOSFODNN7EXAMPLE"),
    ("api_key_credential", "api_key: XXXXYYYYZZZZWWWW"),
    ("env_dump_excluded", ENVD),
    ("credential_subprocess_excluded", "aws_secret_access_key present here"),
]

try:
    spec = importlib.util.spec_from_file_location("_sut_br", target)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_sut_br"] = mod
    spec.loader.exec_module(mod)
    red = mod._import_redactor()
    print("::br-set:: %s" % ",".join(sorted(mod.SCAN_BLOCKING_RULES)))
    for label, text in CASES:
        verdict, blocking, advisory = mod._scan_blob(text, red)
        print("::br-case:: %s %s blocking=%s advisory=%s"
              % (label, verdict, ",".join(sorted(blocking)) or "-",
                 ",".join(sorted(advisory)) or "-"))
except BaseException:
    traceback.print_exc()
    raise SystemExit(3)

print("::br-done::")
PYEOF

BR_MUT="$TMPROOT/br_mutate.py"
cat >"$BR_MUT" <<'PYEOF'
"""차단집합 **축소** 변이기. rc 3 = 앵커 drift(튜플 형태가 바뀌었다)."""
import re
import sys

src, out, drop = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding="utf-8").read()
m = re.search(r"SCAN_BLOCKING_RULES = \(\n(.*?)\n\)\n", s, re.S)
if not m:
    sys.stderr.write("ANCHOR-DRIFT: SCAN_BLOCKING_RULES 튜플 형태 변경\n")
    sys.exit(3)
names = re.findall(r'"([a-z_]+)"', m.group(1))
if drop == "ALL_BUT_CLOUD":
    keep = ["cloud_key"]
else:
    if drop not in names:
        sys.stderr.write("ANCHOR-DRIFT: %s 부재\n" % drop)
        sys.exit(3)
    keep = [n for n in names if n != drop]
new = "SCAN_BLOCKING_RULES = (\n" + "".join('    "%s",\n' % n for n in keep) + ")\n"
open(out, "w", encoding="utf-8", newline="\n").write(s[:m.start()] + new + s[m.end():])
PYEOF

# 9룰 — SUT 정의 순서. BR_EXPECT 는 정렬형(집합 비교용).
BR_RULES=(private_key_block authorization_header cookie_header github_pat
          github_fine_grained_pat cloud_key api_key_credential
          env_dump_excluded credential_subprocess_excluded)
BR_EXPECT="api_key_credential,authorization_header,cloud_key,cookie_header,credential_subprocess_excluded,env_dump_excluded,github_fine_grained_pat,github_pat,private_key_block"

br_run() { BR_OUT="$(python3 "$BR_PROBE" "$1" 2>&1)" || true; }
br_done() { case "$BR_OUT" in *"::br-done::"*) return 0 ;; esac; return 1; }
br_verdict() { printf '%s\n' "$BR_OUT" | sed -n "s/^::br-case:: $1 \([a-z]*\) .*/\1/p" | tail -1; }

br_mutant() { # <rule|ALL_BUT_CLOUD> → stdout: 변이 SUT 경로. rc3 = 앵커 drift
  local drop="$1" d="$TMPROOT/br-mut-$RANDOM$RANDOM"
  mkdir -p "$d"
  cp "$REPO_ROOT/scripts/lib/"*.py "$d/" 2>/dev/null || true
  python3 "$BR_MUT" "$REPO_ROOT/scripts/lib/check_salvage_bundle.py" \
    "$d/check_salvage_bundle.py" "$drop" >/dev/null 2>"$TMPROOT/br-mut.err" || return 3
  printf '%s\n' "$d/check_salvage_bundle.py"
}

if [ "$SUT_PRESENT" -eq 1 ]; then
  br_run "$REPO_ROOT/scripts/lib/check_salvage_bundle.py"
  if ! br_done; then
    ng "S-BR baseline probe 크래시 — 하류 전건 판정 무효(INV-T4)" "$BR_OUT"
  else
    BR_GOT="$(printf '%s\n' "$BR_OUT" | sed -n 's/^::br-set:: //p' | tail -1)"
    assert_eq "S-BR-SET 차단집합 멤버십 9룰 정확 일치" "$BR_EXPECT" "$BR_GOT" \
      "축소·확대 양방향 결박. 변경이 정당하면 ADR-179 §결정 2 와 함께 갱신할 것."
    for r in "${BR_RULES[@]}"; do
      v="$(br_verdict "$r")"
      if [ "$v" = "finding" ]; then
        ok "S-BR-FIRE $r — 전용 페이로드가 차단 판정(발화 실증)"
      else
        ng "S-BR-FIRE $r — 전용 페이로드가 차단되지 않음(verdict='$v')" \
           "이름만 있고 발화하지 않는 룰 = 차단집합의 죽은 원소" "$BR_OUT"
      fi
    done
  fi

  # ③ per-rule 축소 변이 — 룰 1종 제거 시 그 페이로드가 차단→통과로 전환해야 killed.
  for r in "${BR_RULES[@]}"; do
    BR_MRC=0
    BR_MPATH="$(br_mutant "$r")" || BR_MRC=$?
    if [ "$BR_MRC" -ne 0 ]; then
      ng "S-BR-DROP $r — 축소 변이 앵커 drift" "$(cat "$TMPROOT/br-mut.err" 2>/dev/null)"
      continue
    fi
    br_run "$BR_MPATH"
    if ! br_done; then
      ng "S-BR-DROP $r — mutant probe 크래시(거짓 kill 차단)" "$BR_OUT"
      continue
    fi
    v="$(br_verdict "$r")"
    if [ "$v" = "clean" ]; then
      ok "S-BR-DROP $r — 축소 mutant killed (차단→통과 전환 실증)"
    else
      ng "S-BR-DROP $r — 축소 mutant survived (verdict='$v')" \
         "이 룰을 지워도 차단이 유지된다 = 차단 기여 미실증" "$BR_OUT"
    fi
  done

  # ④ 9→1 전면 축소 — 리뷰가 실증한 바로 그 변이. 나머지 8종이 전부 통과로 전환돼야 killed.
  BR_MRC=0
  BR_MPATH="$(br_mutant ALL_BUT_CLOUD)" || BR_MRC=$?
  if [ "$BR_MRC" -ne 0 ]; then
    ng "S-BR-1 9→1 전면 축소 — 변이 앵커 drift" "$(cat "$TMPROOT/br-mut.err" 2>/dev/null)"
  else
    br_run "$BR_MPATH"
    if ! br_done; then
      ng "S-BR-1 9→1 전면 축소 — mutant probe 크래시(거짓 kill 차단)" "$BR_OUT"
    else
      BR_FLIP=0
      for r in "${BR_RULES[@]}"; do
        [ "$r" = "cloud_key" ] && continue
        [ "$(br_verdict "$r")" = "clean" ] && BR_FLIP=$((BR_FLIP + 1))
      done
      if [ "$BR_FLIP" -eq 8 ] && [ "$(br_verdict cloud_key)" = "finding" ]; then
        ok "S-BR-1 9→1 전면 축소 mutant killed (8종 차단→통과 전환, cloud_key 만 잔존)"
      else
        ng "S-BR-1 9→1 전면 축소 mutant survived — 리뷰 실증 결함 미봉합" \
           "통과 전환 $BR_FLIP/8, cloud_key verdict='$(br_verdict cloud_key)'" "$BR_OUT"
      fi
    fi
  fi
fi


# ═════════════════════════════════════════════════════════════════════════════
# Part 6 — CFP-2995 AC-17 범위 경계 + §3.8.2 ADDITIVE-ONLY 4-정의역 (신규 Part)
# ═════════════════════════════════════════════════════════════════════════════
echo
echo "── Part 6: AC-17 범위 경계 판별기 + ADDITIVE-ONLY 4-정의역 ──"

# ── 6-1. 판별력 (§8-fixture AC-17) — 금지 표면 내부 1건 / 외부 0건 으로 갈리는가 ──
#   한쪽만 보면 항진과 구별되지 않는다. 두 합성 경로를 **같은** 판정기에 통과시킨다.
AC17_DENY_F="$TMPROOT/ac17-deny.txt"
printf '%s\n' "$AC17_FLOOR" > "$AC17_DENY_F"
AC17_CH_IN="$TMPROOT/ac17-changed-inside.txt"
printf '%s\n' "$AC17_FLOOR" "docs/stories/CFP-2995.md" > "$AC17_CH_IN"
AC17_CH_OUT="$TMPROOT/ac17-changed-outside.txt"
printf '%s\n' "docs/stories/CFP-2995.md" "archive/adr/ADR-179-agent-salvage-bundle-handoff.md" > "$AC17_CH_OUT"

AC17_IN_RC=0
AC17_IN_OUT="$(ac17_judge "$AC17_DENY_F" "$AC17_CH_IN")" || AC17_IN_RC=$?
AC17_OUT_RC=0
AC17_OUT_OUT="$(ac17_judge "$AC17_DENY_F" "$AC17_CH_OUT")" || AC17_OUT_RC=$?

if [ "$AC17_IN_OUT" = "violations=1" ] && [ "$AC17_IN_RC" -ne 0 ] \
   && [ "$AC17_OUT_OUT" = "violations=0" ] && [ "$AC17_OUT_RC" -eq 0 ]; then
  ok "AC-17 판별력 — 내부 합성 경로 1건(RED) / 외부 합성 경로 0건(GREEN) 으로 갈린다"
else
  ng "AC-17 판별력 미성립 — 판정기가 두 합성 경로를 구별하지 못한다" \
     "inside='$AC17_IN_OUT' rc=$AC17_IN_RC (기대 violations=1 ∧ rc!=0)" \
     "outside='$AC17_OUT_OUT' rc=$AC17_OUT_RC (기대 violations=0 ∧ rc=0)"
fi

# ── 6-2. floor 음성 대조 — 목록 과소모집이 조용히 GREEN 이 되지 않는다 ──
AC17_DENY_SHORT="$TMPROOT/ac17-deny-short.txt"
printf '%s\n' "docs/irrelevant.md" > "$AC17_DENY_SHORT"
AC17_FL_RC=0
AC17_FL_OUT="$(ac17_judge "$AC17_DENY_SHORT" "$AC17_CH_OUT")" || AC17_FL_RC=$?
case "$AC17_FL_OUT:$AC17_FL_RC" in
  undecidable:*floor*:0) ng "AC-17 floor 음성대조 — 사유는 맞으나 rc=0 (fail-closed 미성립)" ;;
  undecidable:*floor*)   ok "AC-17 floor 음성대조 — 소유면 과소모집이 undecidable(RED) 로 접힌다" ;;
  *) ng "AC-17 floor 음성대조 실패 — 불완전 목록이 판정을 통과했다" \
        "out='$AC17_FL_OUT' rc=$AC17_FL_RC (기대 undecidable:*floor* ∧ rc!=0)" ;;
esac

# ── 6-3. 공허 정의역 음성 대조 — 판정 축 ②(부재-assert 항진 차단) ──
: > "$TMPROOT/ac17-empty.txt"
AC17_EM_RC=0
AC17_EM_OUT="$(ac17_judge "$AC17_DENY_F" "$TMPROOT/ac17-empty.txt")" || AC17_EM_RC=$?
case "$AC17_EM_OUT:$AC17_EM_RC" in
  undecidable:*공허*:0) ng "AC-17 공허 음성대조 — 사유는 맞으나 rc=0 (fail-closed 미성립)" ;;
  undecidable:*공허*)   ok "AC-17 공허 음성대조 — 빈 변경 집합이 「위반 0」이 아니라 undecidable(RED)" ;;
  *) ng "AC-17 공허 음성대조 실패 — 빈 집합이 충족으로 계상됐다" \
        "out='$AC17_EM_OUT' rc=$AC17_EM_RC (기대 undecidable:*공허* ∧ rc!=0)" ;;
esac

# ── 6-3.5. 기저선 판독 가능성 1회 판정 (하류 6-4 / 6-5 / 6-6 / Part 7 [E] 공유) ──
#   판정을 가르는 축은 여기 하나다: **읽힘 ∧ 동일 / 읽힘 ∧ 다름 / 못 읽음**.
#   못 읽음의 관측된 원인 = 러너 checkout 이 shallow(depth 1) 라 기저선 커밋 객체가 부재.
#   → 축 B 가 .github/workflows/invariant-check.yml 의 checkout 에 fetch-depth: 0 을 배선해
#     이 상태를 해소한다. 축 A(본 절)만 있으면 CI 에서 영구 undecidable = 판별력 0 이 된다.
AC17_BASE_READ=1
git -C "$REPO_ROOT" cat-file -e "${AC17_BASELINE}^{commit}" 2>/dev/null || AC17_BASE_READ=0
AC17_BASE_WHY="기저선 ${AC17_BASELINE} 커밋 객체 미판독 — shallow checkout 의심(fetch-depth 미지정)"
AC17_BASE_WHY2="판정 불가이지 위반 아님 — 이 leg 은 충족 계상에서 제외되고 종료코드 3(fail-closed)으로 귀결한다"

# ── 6-4. 동결 2 파일 무변경 (AC-12 인접 — 본 Story 는 읽기만 한다) ──
#   `git diff --quiet` 의 rc 는 3분된다: 0=차분 없음 / 1=차분 있음 / 그 외(128 등)=git 자체 실패.
#   rc≠0 을 통째로 「변경됨」에 매핑하면 **판독 실패가 위반으로 승격**한다(원 결함).
for AC17_FZ in "scripts/lib/check_salvage_bundle.py" "scripts/lib/redact_dev_process_content.py"; do
  if [ "$AC17_BASE_READ" -eq 0 ]; then
    undec "동결 파일 판정 불가 — $AC17_FZ" "$AC17_BASE_WHY" "$AC17_BASE_WHY2"
    continue
  fi
  AC17_FZ_RC=0
  git -C "$REPO_ROOT" diff --quiet "$AC17_BASELINE" -- "$AC17_FZ" || AC17_FZ_RC=$?
  case "$AC17_FZ_RC" in
    0) ok "동결 파일 무변경(기저선 대비 diff 0) — $AC17_FZ" ;;
    1) ng "동결 파일이 변경됐다 — $AC17_FZ" "AC-12 byte-identical 보존 위반 (diff 실재)" ;;
    *) undec "동결 파일 판정 불가 — $AC17_FZ" \
             "git diff 자체가 실패했다(rc=$AC17_FZ_RC) — 차분 관측에 도달하지 못했다" \
             "$AC17_BASE_WHY2" ;;
  esac
done

# ── 6-5. born-RED 짝 — AC-17 step 이 두 사본 모두에 실재 + 기저선에는 부재 ──
#   부재-assert 가 아니라 **positive assert** 다: 「없지 않다」가 아니라 「있다」를 단언한다.
for AC17_F in "$AC17_LIVE" "$AC17_TWIN"; do
  if [ ! -f "$REPO_ROOT/$AC17_F" ]; then
    ng "AC-17 배선 대상 부재: $AC17_F"
  elif grep -qF "$AC17_STEP_NAME" "$REPO_ROOT/$AC17_F"; then
    ok "AC-17 step 실재(positive assert) — $AC17_F"
  else
    ng "AC-17 step 부재 — $AC17_F" "born-RED 짝의 GREEN 측 미착지"
  fi
done

if cmp -s "$REPO_ROOT/$AC17_LIVE" "$REPO_ROOT/$AC17_TWIN"; then
  ok "ac-traceability-matrix.yml live ↔ template twin byte 동일"
else
  ng "live ↔ template twin 불일치" "invariant-check parity leg 이 EXIT 1 로 접는다"
fi

# 음성 대조 — 기저선 리비전에는 step 이 **없어야** 한다(검사가 항진이 아님을 보인다).
if [ "$AC17_BASE_READ" -eq 0 ]; then
  undec "born-RED 음성대조 판정 불가 — 기저선 미판독" "$AC17_BASE_WHY" "$AC17_BASE_WHY2"
elif git -C "$REPO_ROOT" archive "$AC17_BASELINE" "$AC17_LIVE" 2>/dev/null | tar -xO 2>/dev/null \
     | grep -qF "$AC17_STEP_NAME"; then
  ng "born-RED 음성대조 실패 — 기저선에 이미 AC-17 step 이 있다(검사가 항진)"
else
  ok "born-RED 음성대조 — 기저선 ${AC17_BASELINE} 에 AC-17 step 부재(RED 측 실증)"
fi

# ── 6-6. §3.8.2 ADDITIVE-ONLY 4-정의역 차분 판정 (live + template twin 양쪽 동일 적용) ──
#   기저선 = **계약 상수**(동적 기저선 금지 — 착지 후 양변이 같아져 공허참=항진이 된다).
#   각 정의역: 착지 후 ⊇ 착지 전 ∧ 착지 전 원소에 대응하는 step 노드가 byte 동일.
#   규율 2: 공허 정의역은 `vacuous: <정의역명>` 명시 방출 + 계상 제외 + **leg RED**
#           (제외 ≠ 무시 — 공허를 빼고 남은 것만으로 PASS 를 주지 않는다).
AC17_ADD_OUT="$TMPROOT/ac17-additivity.txt"
AC17_ADD_RC=0
python3 - "$REPO_ROOT" "$AC17_BASELINE" "$AC17_LIVE" "$AC17_TWIN" > "$AC17_ADD_OUT" 2>&1 <<'AC17ADDPY' || AC17_ADD_RC=$?
import hashlib, json, os, subprocess, sys
root, baseline = sys.argv[1], sys.argv[2]
paths = sys.argv[3:]
try:
    import yaml
except ImportError:
    print("undecidable: PyYAML 부재 — additivity 판정불가(fail-closed)")
    sys.exit(3)

def at_baseline(rel):
    a = subprocess.run(["git", "-C", root, "archive", baseline, rel], capture_output=True)
    if a.returncode != 0:
        return None
    t = subprocess.run(["tar", "-xO"], input=a.stdout, capture_output=True)
    if t.returncode != 0 or not t.stdout:
        return None
    return t.stdout.decode("utf-8")

def domains(text):
    doc = yaml.safe_load(text)
    jobs = doc.get("jobs") or {}
    a, c, d = {}, set(), set()
    for job in jobs.values():
        for st in (job.get("steps") or []):
            if "name" in st:
                idx = "name:" + st["name"]
            elif "uses" in st:
                idx = "uses:" + st["uses"]
            else:
                idx = "run-sha256:" + hashlib.sha256((st.get("run") or "").encode("utf-8")).hexdigest()
            a[idx] = json.dumps(st, sort_keys=True, ensure_ascii=False)
            if "uses" in st:
                c.add(st["uses"])
            d |= set((st.get("env") or {}).keys())
        c |= set((job.get("outputs") or {}).keys())
    d |= set((doc.get("env") or {}).keys())
    return {"a_step_nodes": a, "b_job_keys": set(jobs), "c_action_pins": c, "d_env_keys": d}

# 종료코드 3분 — 1=실 위반(부분집합 파괴/기존 step 편집/공허 정의역) / 3=판정 불가(기저선
#   미판독·추출기 파손) / 0=충족. 판정 불가를 1 로 접으면 「위반 없음」을 관측하지 못한 상태가
#   「위반 있음」으로 승격한다. 둘 다 fail-closed 지만 **방출 어휘와 계상이 갈린다**.
violations = 0
undecidables = 0
for rel in paths:
    pre_text = at_baseline(rel)
    if pre_text is None:
        print("undecidable: 기저선 리비전 미판독 — " + rel)
        undecidables += 1
        continue
    try:
        with open(os.path.join(root, rel), encoding="utf-8") as fh:
            post = domains(fh.read())
        pre = domains(pre_text)
    except Exception as exc:
        print("undecidable: 추출기 파손 — " + rel + " (" + type(exc).__name__ + ")")
        undecidables += 1
        continue
    for key in ("a_step_nodes", "b_job_keys", "c_action_pins", "d_env_keys"):
        pre_s, post_s = set(pre[key]), set(post[key])
        if not pre_s or not post_s:
            # 공허 정의역은 판정 불가가 아니라 **오라클 결함**이다(양변을 읽고도 빌 수 있다).
            #   기존 규율(계상 제외 + leg RED) 유지 — 기저선 미판독과 다른 축이다.
            print("vacuous: " + key + " (" + rel + ") — 계상 제외 + leg RED")
            violations += 1
            continue
        if not pre_s <= post_s:
            print("VIOLATION " + key + " (" + rel + ") 착지 전 원소 소실: " + repr(sorted(pre_s - post_s)))
            violations += 1
            continue
        if key == "a_step_nodes":
            drift = [k for k in pre[key] if pre[key][k] != post[key][k]]
            if drift:
                print("VIOLATION a_step_nodes (" + rel + ") 기존 step 편집: " + repr(drift))
                violations += 1
                continue
        print("OK " + key + " (" + rel + "): 착지 전 " + str(len(pre_s)) + " ⊆ 착지 후 " + str(len(post_s)))
sys.exit(1 if violations else (3 if undecidables else 0))
AC17ADDPY

case "$AC17_ADD_RC" in
  0) ok "ADDITIVE-ONLY 4-정의역 — 양 사본 전건 착지 후 ⊇ 착지 전 ∧ 기존 step byte 동일"
     sed 's/^/    /' "$AC17_ADD_OUT" ;;
  3) undec "ADDITIVE-ONLY 4-정의역 판정 불가" "$(sed 's/^/  /' "$AC17_ADD_OUT")" "$AC17_BASE_WHY2" ;;
  *) ng "ADDITIVE-ONLY 4-정의역 위반 (rc=$AC17_ADD_RC)" "$(sed 's/^/  /' "$AC17_ADD_OUT")" ;;
esac

# ── 6-7. 방출 어휘 폐집합 (§3.9) — sentinel 비출현이 계약이다 ──
#   판정기 방출문에 원문 인용·금지목록 덤프가 섞이면 PRIVATE Story 가 PUBLIC 로그에 착지한다.
AC17_VOCAB_BAD=0
for AC17_EMIT in "$AC17_IN_OUT" "$AC17_OUT_OUT" "$AC17_FL_OUT" "$AC17_EM_OUT"; do
  case "$AC17_EMIT" in
    violations=[0-9]*|undecidable:*|not-applicable:*) ;;
    *) AC17_VOCAB_BAD=$((AC17_VOCAB_BAD+1)) ;;
  esac
done
if [ "$AC17_VOCAB_BAD" -eq 0 ]; then
  ok "AC-17 방출 어휘 폐집합 — 4 방출 전건이 {violations=N · undecidable: · not-applicable:} 안"
else
  ng "AC-17 방출 어휘 폐집합 위반 $AC17_VOCAB_BAD 건" "폐집합 밖 어휘가 방출됐다(§3.9)"
fi


# ═════════════════════════════════════════════════════════════════════════════
# Part 7 — CFP-2995 AC-13/14: ADR-179 F-12 정정 사이트 문면 lint + 실행 대조
#
#   AC-13 = 재위치 앵커로 식별한 4 사이트(J1~J4)가 각각 「탐지 여부」를 진술하는가.
#   AC-14 = 그 진술의 함의가 D1(bare 11) ∪ D2(문맥 래핑 6) = 17 입력에서 실 탐지기
#           실행 결과와 일치하며 어느 입력에서도 미결정으로 남지 않는가.
#
#   ★ 대조군 4종을 함께 싣고 **각각 RED 임을 단언**한다 — 대조군이 없으면 「이식 오류」를
#     잡는 기계 leg 이 0 이다. 네 대조군은 **서로 다른 축**에서 RED 를 낸다:
#       OLD(정확성) · DRAFT(전역성) · WRONG_TOTAL(정확성·argmax) · GLOBAL_OVERREACH(정의역)
#   ★ per-witness 방출 — 수치 일치만으로 충족 계상하지 않는다. 「다른 이유로 RED 인」
#     대조군이 조건을 통과하는 것을 막기 위해 판정을 낸 **입력 id 집합**을 방출한다.
#   ★ GLOBAL_OVERREACH 는 aggregate RED 로 계상하지 않는다 — `D1 단독 GREEN` ∧
#     `D1∪D2 RED` 의 **논리곱**이며, D1 이 RED 면 `invalid:` 방출 + **leg RED**
#     (계상 제외 ≠ 무시 — 정의역 축 유일 대조군의 무효화는 판별력 상실이다).
#
#   ★ 정직 잔여 (숨기지 않는다):
#     (1) 저작 규율 2(「임계 수치 리터럴 금지」)는 **기계 검사하지 않는다.** 정정문이
#         종전 거짓을 「」로 인용해 반증할 때 그 인용이 수치를 정당하게 담기 때문이다
#         (착지문 J2 가 실제로 그렇다) — 계수 기반 금지는 옳은 문면을 RED 로 만든다.
#         ⇒ 본 leg 은 **하한 지시자의 positive assert**(상수 이름 또는 「하한」)만 재고,
#         리터럴 금지는 **리뷰 판정면**으로 남긴다.
#     (2) `DRAFT`·`GLOBAL_OVERREACH` 술어의 정본은 internal-docs 리비전이나 wrapper CI
#         에서 그 repo 를 읽을 수 없다 ⇒ 술어를 **코드로 인라인**하고 출처를 immutable
#         ref 로 주석에 핀한다(`WRONG_TOTAL` 이 계획서에서 인라인된 것과 같은 형태).
#         인라인 사본과 원본의 일치는 리뷰 판정면이다.
# ═════════════════════════════════════════════════════════════════════════════
echo
echo "── Part 7: AC-13/14 ADR-179 사이트 문면 lint + 17 입력 실행 대조 + 대조군 4종 ──"

AC1314_OUT="$TMPROOT/ac1314.out"
AC1314_RC=0
python3 - "$REPO_ROOT" "$AC17_BASELINE" > "$AC1314_OUT" 2>&1 <<'AC1314PY' || AC1314_RC=$?

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CFP-2995 AC-13/14 — ADR-179 F-12 정정 사이트 문면 lint + 실행 대조 + 대조군 4종.

호출: python3 ac1314.py <REPO_ROOT> <BASELINE_SHA> <결과파일>
결과파일 = 1행 1판정, "OK<TAB>메시지" 또는 "NG<TAB>메시지<TAB>상세".
"""
import base64
import importlib.util
import io
import math
import os
import re
import subprocess
import sys

ROOT, BASELINE = sys.argv[1], sys.argv[2]
RESULTS = []


def ok(msg):
    RESULTS.append("OK\t" + msg)


def ng(msg, detail=""):
    RESULTS.append("NG\t" + msg + "\t" + detail)


def un(msg, detail=""):
    """제3상태 — 판정에 필요한 입력을 못 읽었다. 위반도 충족도 아니다(shell `undec` 로 라우팅)."""
    RESULTS.append("UN\t" + msg + "\t" + detail)


# ── SUT 로드 (실 탐지기 — 대역 아님) ─────────────────────────────────────────
spec = importlib.util.spec_from_file_location(
    "rd", os.path.join(ROOT, "scripts", "lib", "redact_dev_process_content.py"))
rd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd)

MIN_LEN = rd.CLOUD_GENERIC_MIN_LEN
MIN_ENT = rd.CLOUD_ENTROPY_MIN
TOKEN_RE = re.compile(r"[A-Za-z0-9_-]+")   # 탐지기 문자 클래스(점 없음) 근사 — 최대 연속 토큰


def ent(s):
    if not s:
        return 0.0
    return -sum((s.count(c) / len(s)) * math.log2(s.count(c) / len(s)) for c in set(s))


def toks(s):
    return TOKEN_RE.findall(s)


# ══════════════════ 입력 집합 D1(11) ∪ D2(6) = 17 ════════════════════════════
def b64(b):
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


HDR = b64(b'{"alg":"HS256","typ":"JWT"}')
HDR_NONE = b64(b'{"alg":"none","typ":"JWT"}')
PL_STD = b64(b'{"sub":"1234567890","name":"John Doe","iat":1516239022}')
PL_SHORT = "eyJhIjoxfQ"
SIG43 = "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
SIG39 = SIG43[:39]
PL_G = "A" * 22 + "B" * 22
HDR_HI = "Zm9vYmFyOTk3M3F3ZXJ0eXVpb3Bhc2RmZ2hqa2x6eGN2Ym5tMTIzNDU2Nzg5MFFXRVJUWVVJ"[:70]
J_TOKEN = "PXm5m5UsXbHV2Hk24bN8uWiHWUW5UitmJHHJV4bt"          # 40자 ent 4.087
K_TOKEN = "rcroucuWNo6WbnzokrrWk96JcbbcrGWooNch4c9HWhYNG"     # 45자 ent 3.895

MEET = HDR + "." + PL_STD + "." + SIG43
FAIL = HDR + "." + PL_SHORT + "." + SIG43[:20]


def envdump(tok):
    return "\n".join(["SESSION_TOKEN=" + tok] + ["VAR%d=value%d" % (i, i) for i in range(1, 10)])


# (id, 부류, 조건, 텍스트) — D1 은 bare(문맥 표지 없음), D2 는 문맥 래핑.
D1 = [
    ("a", None, None, HDR + "." + PL_STD + "." + SIG43),
    ("b", None, None, HDR + "." + PL_STD + "." + SIG39),
    ("c", None, None, HDR_NONE + "." + PL_STD),
    ("d", None, None, HDR + "." + PL_SHORT + "." + SIG39),
    ("e", None, None, "A" * 41),
    ("f", None, None, HDR + "." + PL_SHORT + "." + SIG43),
    ("g", None, None, HDR + "." + PL_G + "." + SIG43),
    ("h", None, None, HDR_HI + "." + PL_SHORT + ".abcdef"),
    ("i", None, None, "A" * 160 + SIG43),
    ("j", None, None, J_TOKEN),
    ("k", None, None, K_TOKEN),
]
D2 = [
    ("w1", "header",     "meet", "Authorization: Bearer " + MEET),
    ("w2", "credential", "meet", "token: " + MEET),
    ("w3", "envdump",    "meet", envdump(MEET)),
    ("w4", "header",     "fail", "Authorization: Bearer " + FAIL),
    ("w5", "credential", "fail", "token: " + FAIL),
    ("w6", "envdump",    "fail", envdump(FAIL)),
]
ALL = D1 + D2

# ── D2 셀 non-empty 선확인 (§8-fixture — 3 부류 × {meet,fail} = 6 셀) ─────────
CELLS = [(k, c) for k in ("header", "credential", "envdump") for c in ("meet", "fail")]
vac = [(k, c) for k, c in CELLS if not [x for x in D2 if x[1] == k and x[2] == c]]
if vac:
    for k, c in vac:
        ng("vacuous: D2/%s/%s — 셀 공허" % (k, c), "leg RED (총 개수 일치만으로 충족 계상 불가)")
else:
    ok("D2 셀 전수 non-empty 선확인 — 3 부류 × {조건충족, 조건미달} = 6 셀 전건 비공허")

if len(ALL) != 17:
    ng("입력 집합 크기 %d (기대 17)" % len(ALL), "D1 11 ∪ D2 6")
else:
    ok("실행 대조 입력 집합 = D1 11 ∪ D2 6 = 17")

# ── 관측축 = 탐지 여부 (redaction_rules_fired 비어있지 않은가) ────────────────
ACTUAL = {}
for cid, klass, cond, text in ALL:
    _t, audit = rd.redact(text)
    fired = audit["redaction_rules_fired"]
    ACTUAL[cid] = bool(fired)

# ══════════════════ 술어 5종 (착지문 + 대조군 4) ═════════════════════════════
# 반환: True(탐지 함의) / False(미탐지 함의) / None(미결정 — 함의하지 않음)

def is_jwtish(text):
    parts = text.split(".")
    return len(parts) in (2, 3) and all(parts) and all(TOKEN_RE.fullmatch(p) for p in parts)


def any_meets(text):
    return any(len(t) >= MIN_LEN and ent(t) >= MIN_ENT for t in toks(text))


def pred_landed(cid, klass, cond, text):
    """착지문 — 정의역 한정(문맥 표지 없는 단독 입력) + 존재 양화 + 문맥 3부류 위임절."""
    if klass in ("header", "credential", "envdump"):
        return True          # 위임절: 그 문맥 룰이 선행 발화해 탐지·차단된다
    return any_meets(text)


def pred_old(cid, klass, cond, text):
    """OLD — wrapper @6bb0e8aa5 ADR-179 :195 표 행.
    셀1 `JWT — alg=none 또는 서명 39자 이하` · 셀4 `통과 (룰 0 발화)`.
    그 밖의 입력에 대해서는 아무것도 함의하지 않는다(미결정)."""
    if not is_jwtish(text):
        return None
    parts = text.split(".")
    alg_none = len(parts) == 2 or (len(parts) == 3 and not parts[2])
    short_sig = len(parts) == 3 and len(parts[2]) <= 39
    return False if (alg_none or short_sig) else None


def pred_draft(cid, klass, cond, text):
    """DRAFT — internal-docs @f2790210 blob 7cba3e3a §10.1.
    셀1 `JWT — 세 세그먼트 중 어느 하나도 길이 조건과 엔트로피 조건을 함께 충족하지 않는 경우`
    · 셀2·3·4 무변(= 통과). 정의역이 「세 세그먼트」로 한정된 **부분 술어**."""
    parts = text.split(".")
    if not (is_jwtish(text) and len(parts) == 3):
        return None
    if any(len(p) >= MIN_LEN and ent(p) >= MIN_ENT for p in parts):
        return None          # 이 경우는 셀1 정의역 밖 — 함의 없음
    return False


def pred_wrong_total(cid, klass, cond, text):
    """WRONG_TOTAL — 계획서 §8-fixture 인라인(저자 합성 반사실, repo 사본 없음).
    「가장 긴 토큰 하나만 판정」 = argmax 단일 선택(존재 양화가 아님)."""
    ts = toks(text)
    if not ts:
        return False
    t = max(ts, key=len)
    return len(t) >= MIN_LEN and ent(t) >= MIN_ENT


def pred_global_overreach(cid, klass, cond, text):
    """GLOBAL_OVERREACH — internal-docs @ce1d1c0c blob d21205d8 §10.1 (라) site 1 iter1 착지문.
    착지문과 같은 존재 양화이나 **정의역 한정과 위임절이 없다**(전칭)."""
    return any_meets(text)


PREDS = [
    ("landed",           pred_landed),
    ("OLD",              pred_old),
    ("DRAFT",            pred_draft),
    ("WRONG_TOTAL",      pred_wrong_total),
    ("GLOBAL_OVERREACH", pred_global_overreach),
]


def evaluate(fn, subset):
    undec, mism = [], []
    for cid, klass, cond, text in subset:
        imp = fn(cid, klass, cond, text)
        if imp is None:
            undec.append(cid)
        elif imp != ACTUAL[cid]:
            mism.append(cid)
    return undec, mism


REPORT = {}
for name, fn in PREDS:
    REPORT[name] = {"all": evaluate(fn, ALL), "d1": evaluate(fn, D1), "d2": evaluate(fn, D2)}

# ── AC-14: 착지문은 17 입력 전건 미결정 0 · 불일치 0 ─────────────────────────
lu, lm = REPORT["landed"]["all"]
if not lu and not lm:
    ok("AC-14 착지문 실행 대조 — D1∪D2 17 입력 전건 미결정 0 · 불일치 0")
else:
    ng("AC-14 착지문 실행 대조 실패 — 미결정 %d · 불일치 %d" % (len(lu), len(lm)),
       "미결정 증인=%s · 불일치 증인=%s" % (lu or "없음", lm or "없음"))

# ── 대조군 3종: RED + per-witness 방출 ───────────────────────────────────────
for name in ("OLD", "DRAFT", "WRONG_TOTAL"):
    u, m = REPORT[name]["all"]
    if u or m:
        ok("대조군 %s = RED (미결정 %d · 불일치 %d) — 증인 미결정=%s 불일치=%s"
           % (name, len(u), len(m), u or "없음", m or "없음"))
    else:
        ng("대조군 %s 가 RED 가 아니다 — 검사가 이식 오류를 잡지 못한다" % name,
           "미결정 0 · 불일치 0 (착지문과 같은 판정)")

# ── GLOBAL_OVERREACH: D1 단독 GREEN ∧ D1∪D2 RED 의 **논리곱** ────────────────
gu1, gm1 = REPORT["GLOBAL_OVERREACH"]["d1"]
gua, gma = REPORT["GLOBAL_OVERREACH"]["all"]
d1_green = not gu1 and not gm1
all_red = bool(gua or gma)
gud2, gmd2 = REPORT["GLOBAL_OVERREACH"]["d2"]
if not d1_green:
    ng("invalid: GLOBAL_OVERREACH (D1 not GREEN) — 계상 제외 + leg RED",
       "D1 미결정=%s 불일치=%s · 정의역 축 유일 대조군의 무효화는 「검사가 판별력을 잃었다」"
       % (gu1 or "없음", gm1 or "없음"))
elif not all_red:
    ng("GLOBAL_OVERREACH 논리곱 미성립 — D1∪D2 가 RED 가 아니다",
       "D2 확장의 판별력이 실증되지 않았다")
else:
    ok("대조군 GLOBAL_OVERREACH = D1 단독 GREEN ∧ D1∪D2 RED (논리곱 성립) — "
       "D2 불일치 증인=%s (D2 없이는 검출 불가)" % (gmd2 or "없음"))

# ══════════════════ AC-13 사이트 문면 lint (J1~J4) ═══════════════════════════
ADR_REL = "archive/adr/ADR-179-agent-salvage-bundle-handoff.md"
SH_REL = "tests/scripts/test_bundle_pre_push_redaction.sh"

SITES = [
    ("J1", ADR_REL, lambda l: l.lstrip().startswith("|") and "alg=none" in l),
    ("J2", ADR_REL, lambda l: l.lstrip().startswith("① **표준 JWT 는 차단된다")),
    ("J3", ADR_REL, lambda l: "정정된 문면: **밖 =" in l),
    # ★ (바) 규율 자기적용 — 이 검사기는 자기가 스캔하는 파일 안에 산다.
    #   앵커 문자열을 소스에 **연속으로** 적으면 그 줄 자신이 2번째 hit 가 돼 앵커 유일성을
    #   스스로 깨뜨린다(실제로 깨뜨렸고 본 leg 이 그것을 검출했다) ⇒ 런타임 결합으로 분리한다.
    ("J4", SH_REL,  lambda l: ("ADR-179 §" + "7 F-12") in l),
]
# 3요소 + 부정 분기 + 정의역 한정절 (상수 이름 또는 「하한」 — 수치 리터럴 아님)
AXES = [
    ("독립 판정", ["독립 판정", "독립으로", "독립 판정이라"]),
    ("길이 하한", ["길이 하한", "CLOUD_GENERIC_MIN_LEN"]),
    ("엔트로피 하한", ["엔트로피 하한", "CLOUD_ENTROPY_MIN"]),
    ("부정 분기", ["하나도 없으면", "하나도 존재하지 않으면"]),
    ("정의역 한정절", ["정의역은 다른 룰의 문맥 표지 없이", "술어의 정의역은 다른 룰의 문맥 표지 없이",
                  "문맥 표지 없이 단독으로 주어진 입력", "문맥 표지 없는 단독 입력"]),
]


def read_lines(rel):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8", newline="") as fh:
        return fh.read().split("\n")


def at_baseline(rel):
    a = subprocess.run(["git", "-C", ROOT, "archive", BASELINE, rel], capture_output=True)
    if a.returncode != 0:
        return None
    t = subprocess.run(["tar", "-xO"], input=a.stdout, capture_output=True)
    if t.returncode != 0 or not t.stdout:
        return None
    return t.stdout.decode("utf-8").split("\n")


def lint(line):
    return [nm for nm, alts in AXES if not any(a in line for a in alts)]


post_missing = 0
for sid, rel, pred in SITES:
    lines = read_lines(rel)
    hits = [l for l in lines if pred(l)]
    if len(hits) != 1:
        ng("AC-13 %s 앵커 유일성 실패 — %d hit (기대 1)" % (sid, len(hits)),
           "재위치 앵커가 착지 후 파일에 정확히 한 번 등장해야 한다")
        post_missing += 1
        continue
    miss = lint(hits[0])
    if miss:
        ng("AC-13 %s 문면 미충족 — 결손 축 %s" % (sid, miss), rel)
        post_missing += 1
    else:
        ok("AC-13 %s — 앵커 hit=1 ∧ 5축(독립·길이하한·엔트로피하한·부정분기·정의역한정) 전건 충족" % sid)

if post_missing == 0:
    ok("AC-13 착지 후 사이트 전수 = 4 · 미충족 0")

# ── [E] 음성 대조 — 착지 전 4 사이트는 같은 lint 를 통과하지 못한다 ──────────
pre_ok = 0
pre_unread = 0
for sid, rel, pred in SITES:
    lines = at_baseline(rel)
    if lines is None:
        pre_unread += 1
        continue
    hits = [l for l in lines if pred(l)]
    if len(hits) == 1 and not lint(hits[0]):
        pre_ok += 1
if pre_unread:
    un("[E] 음성 대조 판정 불가 — 기저선 %s 미판독 %d 사이트" % (BASELINE[:9], pre_unread),
       "착지 전 상태를 못 읽었다 = 판별력 결여가 아니라 미관측 (shallow checkout 의심)")
elif pre_ok == 0:
    ok("[E] 음성 대조 — 착지 전 4 사이트 전건 lint 미충족 (검사가 항진이 아니다)")
else:
    ng("[E] 음성 대조 실패 — 착지 전 사이트 %d 개가 이미 lint 를 통과한다" % pre_ok,
       "lint 가 착지 전후를 구별하지 못한다 = 판별력 0")

sys.stdout.write("\n".join(RESULTS) + "\n")
sys.exit(1 if any(r.startswith("NG") for r in RESULTS)
         else (3 if any(r.startswith("UN") for r in RESULTS) else 0))
AC1314PY

if [ ! -s "$AC1314_OUT" ]; then
  ng "AC-13/14 leg 무출력 (rc=$AC1314_RC)" "undecidable — 하네스가 판정을 내지 못했다(fail-closed)"
else
  while IFS="$(printf '\t')" read -r AC1314_V AC1314_M AC1314_D; do
    case "$AC1314_V" in
      OK) ok "$AC1314_M" ;;
      NG) ng "$AC1314_M" "$AC1314_D" ;;
      UN) undec "$AC1314_M" "$AC1314_D" "$AC17_BASE_WHY2" ;;
      *)  ng "AC-13/14 leg 출력 파손" "$AC1314_V $AC1314_M" ;;
    esac
  done < "$AC1314_OUT"
fi

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "UNDECIDABLE: $UNDEC"
# 종료코드 3분 — 0=충족 / 1=실 위반 / 3=판정 불가(fail-closed).
#   3 은 GREEN 이 아니다: 판정에 필요한 입력을 못 읽은 상태를 통과로 접으면 「미관측을 관측된 0
#   으로 보고」가 되어 본 Story 가 표적하는 형태 그대로가 된다. 동시에 「위반」으로도 접지
#   않는다 — 그 방향은 이 검사가 실제로 산출했던 거짓 단정(「동결 파일이 변경됐다」)이다.
if [ "$FAIL" -eq 0 ] && [ "$UNDEC" -eq 0 ]; then
  echo "OK All $PASS cases pass — 4-변종/primitive 정의역/술어 협착/대조군 3종/mutant 4종 + CFP-2995 AC-17 범위경계·additivity + AC-13/14 사이트 대조·대조군 4종 결박"
  echo "   (보장 범위 = L1 경유 착지 경로 한정. raw git push 우회는 L1 정의역 밖 — L3 사후 탐지.)"
  exit 0
elif [ "$FAIL" -eq 0 ]; then
  echo "? $UNDEC case(s) undecidable — 충족 계상 제외 ∧ GREEN 아님 (fail-closed)"
  echo "   판정 불가는 위반 단정의 근거가 아니다. 기저선 커밋 객체 부재가 원인이면"
  echo "   러너 checkout 의 fetch-depth 를 확인하라(.github/workflows/invariant-check.yml)."
  exit 3
else
  echo "X $FAIL case(s) failed / $UNDEC undecidable"
  exit 1
fi
