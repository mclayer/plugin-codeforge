#!/usr/bin/env bash
# CFP-2377 Phase 2 — check-worktree-completion-clean.sh 변별 test (anti-theater)
#
# 검증 대상 = scripts/check-worktree-completion-clean.sh (DevPL 산출, 완료 Story
# worktree 잔존 검출 게이트). 본 러너는 §8 Test Contract 의 TC-3 / TC-4 / TC-6 을
# 이행한다. 선례 = scripts/test-check-operational-outcome-signal.sh (자립 bash 러너,
# mktemp fixture, git/gh stub 주입, PASS/FAIL 카운터, exit-code + stdout 동시 assert).
#
# anti-theater 원칙 (vacuous 거짓통과 금지):
#   - 각 test = fixture 작성 → 스크립트 실행 → exit code assert + 검출-신호 assert 동시.
#   - missing-case (검출 대상 부재 = 정리됨) 가 별도 test 로 존재해 false-positive 차단.
#   - || true 마스킹 / always-pass 금지. mutation 생존 안 하게:
#     · TC-3 = 잔존 worktree fixture 면 검출, 정리됨 fixture 면 비검출 (양방향 변별).
#     · TC-4 = gh 미인증 stub 이면 prune 0 + advisory + exit 0 (fail-safe 상속).
#     · TC-6 = open(mergedAt null) Story root 면 orphan 오판 안 함 (순서 invariant).
#
# 대상 스크립트 부재 시 SKIP (DevPL 산출물 미 commit 상태) — RED 정상. DevPL 최종
# commit 시 합쳐지면 실 검증으로 전환된다 (테스트 설계 자체는 합쳐진 상태 전제).
#
# stub 주입 = check-worktree-stale.sh 동일 패턴 GC_GIT_BIN / GC_GH_BIN env override
# (templates/scripts/check-worktree-stale.sh:34-37 실측 동형). DRY_RUN = GC_DRY_RUN=1.
# 검출 대상 Story = STORY_KEY=cfp-NNN env (설계 계약 F2 / ADR-040 Amd9 §결정 7.K).
#
# Exit code: 0 (all tests pass) / 1 (any test fails)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$REPO_ROOT/scripts/check-worktree-completion-clean.sh"

PASS=0
FAIL=0

# 대상 스크립트 부재 = DevPL 산출물 미 commit. RED 정상 — SKIP 후 비-fail 종료.
if [ ! -f "$TARGET" ]; then
  echo "::warning::check-worktree-completion-clean.sh 부재 — DevPL 산출물 미 commit 상태 (RED 정상)."
  echo "본 러너는 스크립트가 존재하는 전제로 작성됨. DevPL 최종 commit 후 실 검증 전환."
  echo "Total: PASS=0 FAIL=0 (SKIPPED — target absent)"
  exit 0
fi

# ─── fixture helper: fake `git` stub 생성 ───────────────────────────────────
# git worktree list --porcelain 출력을 고정 stub 으로 주입한다. 그 외 git 하위명령
# (-C status / rev-parse / cat-file / rev-list / worktree remove / branch -D) 은
# 검출 게이트가 호출할 수 있으므로 안전 default 반환 (clean / 성공) 한다.
make_git_stub() {
  local stub_path="$1" porcelain_file="$2" dirty="${3:-0}"
  local status_emit=""
  # dirty=1 이면 git status --porcelain 가 tracked 변경 1줄 방출 → 게이트가 보존해야 함.
  [ "$dirty" = "1" ] && status_emit=' M src/touched.py'
  cat > "$stub_path" <<STUB
#!/usr/bin/env bash
# fake git stub — worktree list --porcelain 만 고정 출력, 나머지는 안전 default.
args=("\$@")
# -C <dir> 접두 흡수
if [ "\${1:-}" = "-C" ]; then
  shift 2
fi
case "\${1:-}" in
  rev-parse)
    # --show-toplevel → REPO_ROOT 흉내
    echo "$REPO_ROOT"
    exit 0
    ;;
  worktree)
    if [ "\${2:-}" = "list" ]; then
      cat "$porcelain_file"
      exit 0
    fi
    # worktree remove → 성공 (실제 제거 안 함, 게이트는 검증만)
    exit 0
    ;;
  status)
    # --porcelain → dirty 면 tracked 변경 1줄, 아니면 clean(빈 출력).
    [ -n "$status_emit" ] && echo "$status_emit"
    exit 0
    ;;
  cat-file)
    exit 0
    ;;
  rev-list)
    echo "0"
    exit 0
    ;;
  branch)
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
STUB
  chmod 755 "$stub_path"
}

# ─── fixture helper: fake `gh` stub 생성 ────────────────────────────────────
# auth_status = 0(인증) / 1(미인증). merged_at = "null" 또는 ISO timestamp 문자열.
# gh pr view --json mergedAt / gh pr list --json ... 양형 응답.
make_gh_stub() {
  local stub_path="$1" auth_status="$2" merged_at="$3"
  cat > "$stub_path" <<STUB
#!/usr/bin/env bash
# fake gh stub — auth status + mergedAt 응답 주입.
case "\${1:-}" in
  auth)
    # gh auth status → 인증 여부
    exit $auth_status
    ;;
  pr)
    # gh pr view --json mergedAt / gh pr list --json ...
    if [ "$merged_at" = "null" ]; then
      # open PR (mergedAt null) — list 는 빈 배열, view 는 mergedAt null
      case " \$* " in
        *" list "*) echo "[]" ;;
        *) echo '{"mergedAt":null}' ;;
      esac
    else
      case " \$* " in
        *" list "*) echo '[{"number":1,"headRefOid":"deadbeefcafe0000000000000000000000000001"}]' ;;
        *) echo '{"mergedAt":"$merged_at"}' ;;
      esac
    fi
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
STUB
  chmod 755 "$stub_path"
}

# ─── 공통 실행 + assert ─────────────────────────────────────────────────────
# run_case <name> <STORY_KEY> <porcelain-text> <gh-auth(0/1)> <gh-mergedAt> \
#          <detect-path> <expect-detect: yes|no> <expect-exit>
#
# 검출 신호 판정 (anti-theater 2-축 동시):
#   ① 경로-anchor — detect-path(완료 worktree 절대경로)가 stdout 에 실제 등장.
#   ② 동사-anchor — 그 경로가 검출/prune 동사 맥락 줄에 있어야 함
#      (단순 worktree 목록 echo · header 의 STORY_KEY echo 와 구분).
# 둘 다 충족해야 detected=1. 둘 중 하나만이면 비검출 (false-positive 차단).
# 검출 마커 문자열은 DevPL 산출물 확정 전이라 동사 어휘를 넓게 잡되, "0건/none/clean/
# 정리됨" 요약 줄(경로 없음)은 동사 매치돼도 경로-anchor 부재로 비검출 처리된다.
run_case() {
  local name="$1" story_key="$2" porcelain="$3" gh_auth="$4" gh_merged="$5"
  local detect_path="$6" expect_detect="$7" expect_exit="$8" dirty="${9:-0}"

  local tmp; tmp=$(mktemp -d)
  printf '%s\n' "$porcelain" > "$tmp/porcelain.txt"
  make_git_stub "$tmp/git" "$tmp/porcelain.txt" "$dirty"
  make_gh_stub "$tmp/gh" "$gh_auth" "$gh_merged"

  local out exit_code=0
  out=$(
    STORY_KEY="$story_key" \
    GC_GIT_BIN="$tmp/git" \
    GC_GH_BIN="$tmp/gh" \
    GC_DRY_RUN=1 \
    bash "$TARGET" 2>&1
  ) || exit_code=$?

  rm -rf "$tmp"

  # exit code assert (anti-theater: 항상 검사)
  if [ "$exit_code" -ne "$expect_exit" ]; then
    echo "✗ FAIL: $name"
    echo "  expected exit $expect_exit, got $exit_code"
    echo "  output: $out"
    FAIL=$((FAIL + 1))
    return 0
  fi

  # 검출 신호 assert — detect-path 가 검출/prune 동사 맥락 줄에 등장해야 검출 (2-축).
  local detected=0
  if printf '%s' "$out" \
       | grep -F "$detect_path" \
       | grep -qiE "DETECT|검출|stale|잔존|would-prune|PRUNING|orphan|남음"; then
    detected=1
  fi

  if [ "$expect_detect" = "yes" ] && [ "$detected" -eq 1 ]; then
    echo "✓ PASS: $name (검출됨, exit $exit_code)"
    PASS=$((PASS + 1))
  elif [ "$expect_detect" = "no" ] && [ "$detected" -eq 0 ]; then
    echo "✓ PASS: $name (비검출 — orphan 오판 안 함, exit $exit_code)"
    PASS=$((PASS + 1))
  else
    echo "✗ FAIL: $name"
    echo "  expected detect=$expect_detect, got detect=$detected"
    echo "  output: $out"
    FAIL=$((FAIL + 1))
  fi
}

WT_BASE="$HOME/.claude/worktrees/plugin-codeforge"

# ─── TC-3: 완료 worktree 잔존 검출 (양방향 변별 — missing-case 포함) ─────────
# (3a) sub-worktree cfp-NNN/lane/* 잔존 = 즉시 검출 (F2 (b)). gh 인증 + clean.
run_case "TC-3a: sub-worktree(cfp-2377/lane/dev) 잔존 → 즉시 검출" \
  "cfp-2377" \
  "worktree $WT_BASE/cfp-2377/lane/dev
HEAD aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
branch refs/heads/cfp-2377/lane/dev
" \
  0 "2026-06-20T00:00:00Z" \
  "$WT_BASE/cfp-2377/lane/dev" "yes" 0

# (3b) missing-case = 정리됨 (대상 worktree 부재 = main 만). 검출 0.
run_case "TC-3b (missing-case): worktree 정리됨(main 만) → 비검출" \
  "cfp-2377" \
  "worktree $WT_BASE
HEAD bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
branch refs/heads/main
" \
  0 "2026-06-20T00:00:00Z" \
  "$WT_BASE/cfp-2377" "no" 0

# (3c) 다른 Story 의 worktree 만 잔존 = 본 STORY_KEY 검출 0 (scope (a) 변별).
run_case "TC-3c: 다른 Story(cfp-9999) worktree 만 잔존 → 본 STORY_KEY 비검출" \
  "cfp-2377" \
  "worktree $WT_BASE/cfp-9999/lane/dev
HEAD cccccccccccccccccccccccccccccccccccccccc
branch refs/heads/cfp-9999/lane/dev
" \
  0 "2026-06-20T00:00:00Z" \
  "$WT_BASE/cfp-9999/lane/dev" "no" 0

# ─── TC-4: fail-safe 상속 (gh 미인증 → 보존 + advisory + exit 0) ────────────
# gh 미인증 stub 이면 mergedAt 판정 불가 → 검출/prune 0 + always exit 0 advisory.
# Story root flat (cfp-2377) 잔존이지만 gh 미인증이라 보수적 비검출 (보존).
run_case "TC-4: gh 미인증 → prune 0 + advisory + exit 0 (fail-safe)" \
  "cfp-2377" \
  "worktree $WT_BASE/cfp-2377
HEAD dddddddddddddddddddddddddddddddddddddddd
branch refs/heads/cfp-2377
" \
  1 "null" \
  "$WT_BASE/cfp-2377" "no" 0

# (4b) dirty worktree → data-loss 가드로 보존 (검출/prune 안 함) + exit 0.
# gh 인증 + merged 라 평소면 검출 대상이지만 tracked 변경 보유 시 절대 보존.
run_case "TC-4b: dirty worktree(tracked 변경) → 보존 + exit 0 (data-loss 가드)" \
  "cfp-2377" \
  "worktree $WT_BASE/cfp-2377/lane/dev
HEAD 1111111111111111111111111111111111111111
branch refs/heads/cfp-2377/lane/dev
" \
  0 "2026-06-20T00:00:00Z" \
  "$WT_BASE/cfp-2377/lane/dev" "no" 0 \
  1

# ─── TC-6: 순서 invariant (open Story root = mergedAt null → orphan 오판 안 함) ─
# F2 (c): Story root cfp-NNN flat 은 Phase 2 PR mergedAt non-null 일 때만 검출.
# open(보존 중, mergedAt null)이면 제외 — false-positive 회피 (EC-3 정합).
run_case "TC-6: open Story root(mergedAt null) → 보존 worktree orphan 오판 안 함" \
  "cfp-2377" \
  "worktree $WT_BASE/cfp-2377
HEAD eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
branch refs/heads/cfp-2377
" \
  0 "null" \
  "$WT_BASE/cfp-2377" "no" 0

# ─── TC-6b: merged Story root(mergedAt non-null) → 검출 (순서 invariant 反면) ─
# mergedAt non-null 확인 후에는 Story root flat 도 검출 대상 (F2 (c) positive).
run_case "TC-6b: merged Story root(mergedAt non-null) → 검출 (F2 (c) positive)" \
  "cfp-2377" \
  "worktree $WT_BASE/cfp-2377
HEAD ffffffffffffffffffffffffffffffffffffffff
branch refs/heads/cfp-2377
" \
  0 "2026-06-20T00:00:00Z" \
  "$WT_BASE/cfp-2377" "yes" 0

# ─── 요약 ──────────────────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"

if [ "$FAIL" -eq 0 ]; then
  echo "All tests passed (완료-게이트 변별 검증 — TC-3/TC-4/TC-6)."
  exit 0
else
  echo "Some tests failed (완료-게이트가 검출/순서/fail-safe 계약을 못 지킴)."
  exit 1
fi
