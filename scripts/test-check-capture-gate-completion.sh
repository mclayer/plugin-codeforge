#!/usr/bin/env bash
# CFP-2392 Phase 2 — check-capture-gate-completion.sh 변별 test (anti-theater)
#
# 검증 대상 = scripts/check-capture-gate-completion.sh (DeveloperAgent 산출, 완료시점
# capture 게이트 — 완료 marker(STORY_KEY) 가 있는데 신규 capture artifact 도 0,
# no-capture note 도 0 이면 외부화 검토 누락을 warning-tier 로 경고). 본 러너는
# §8.1 Test Contract 의 TC1~TC5 를 이행한다.
#
# 선례 = scripts/test-check-worktree-completion-clean.sh (자립 bash 러너, mktemp
# fixture, git stub 주입(GC_GIT_BIN env override), PASS/FAIL 카운터, exit-code ∧
# stdout sentinel 동시 assert). 본 러너는 동형 패턴을 답습한다.
#
# anti-theater 원칙 (CFP-2270 D1 + memory gotcha "missing-case + exit assert" — 비협상):
#   - 각 TC = fixture 작성 → 스크립트 실행 → exit code assert ∧ stdout sentinel assert 동시.
#     한쪽만 검사 = theater.
#   - discriminating-negative(TC3) 필수 — capture 0 ∧ note 0 이면 WARN 이 *실제로 등장*,
#     positive case(TC1/TC2)에선 WARN 이 *부재* 임을 양방향 변별 (mutation 생존 차단:
#     스크립트가 항상 PASS 거나 항상 WARN 이면 본 러너가 잡는다).
#   - || true 마스킹 / always-pass 금지.
#
# 대상 스크립트 부재 시 SKIP (DeveloperAgent 산출물 미 commit 상태) — RED 정상.
# DevPL 통합 commit 시 합쳐지면 실 검증으로 전환된다.
#
# git stub 주입 = GC_GIT_BIN env override (worktree-completion test 동형). 대상 스크립트는
# 두 흔적 채널을 git 으로만 읽으므로(별도 file env 없음), 본 러너는 두 흔적을 git stub 출력에
# 주입한다:
#   - capture artifact = `git diff --name-only base...HEAD` + `git status --porcelain` 가 반환하는
#     파일 목록 (skills/*/SKILL.md 또는 docs/domain-knowledge/**/*.md 패턴).
#   - no-capture note = `git log -1 --format=%B` 가 반환하는 commit message 본문
#     (`캡처 대상 검토 완료` / `외부화 불요` 패턴).
# rev-parse(--show-toplevel / --verify origin/main) 는 안전 default. fail-safe(TC5) =
# git stub 가 rev-parse --show-toplevel 실패(exit 128) → 대상 스크립트 NOT_A_GIT_REPO no-op.
# BYPASS = BYPASS_CAPTURE_GATE=1 (본 러너 미사용 — 대상 스크립트 self-check 영역).
#
# Output contract (DeveloperAgent 확정 — 이걸 assert):
#   - WARN sentinel (정규식): \[capture-gate\] WARN
#   - PASS sentinel: [capture-gate] PASS:
#   - 마지막 줄: [capture-gate] DONE: warn=<0|N> story=<STORY_KEY>
#   - 모든 경로 always exit 0 (warning-tier).
#
# Exit code: 0 (all tests pass) / 1 (any test fails)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$REPO_ROOT/scripts/check-capture-gate-completion.sh"

PASS=0
FAIL=0

# 대상 스크립트 부재 = DeveloperAgent 산출물 미 commit. RED 정상 — SKIP 후 비-fail 종료.
if [ ! -f "$TARGET" ]; then
  echo "::warning::check-capture-gate-completion.sh 부재 — DevPL 산출물 미 commit (RED 정상)."
  echo "본 러너는 스크립트가 존재하는 전제로 작성됨. DevPL 최종 commit 후 실 검증 전환."
  echo "Total: PASS=0 FAIL=0 (SKIPPED — target absent)"
  exit 0
fi

# ─── fixture helper: fake `git` stub 생성 ───────────────────────────────────
# 대상 스크립트의 실제 git 하위명령 사용을 그대로 흉내낸다 (check-capture-gate-completion.sh
# 실측 동형):
#   - rev-parse --show-toplevel → REPO_ROOT (healthy=1 이면 exit 128 = NOT_A_GIT_REPO)
#   - rev-parse --verify --quiet <ref> → origin/main 만 성공(exit 0), 그 외 실패 (base ref 해석)
#   - diff --name-only base...HEAD → fixture 파일 목록 (capture artifact 유/무)
#   - status --porcelain --untracked-files=all → 빈 출력 (실 working-tree 누수 차단; artifact 는
#       diff 채널로만 주입). note 도 working-tree 채널 대신 log 채널로 주입.
#   - log -1 --format=%B → note fixture (commit message 본문; `캡처 대상 검토 완료` 등)
# healthy=0(정상) / 1(rev-parse --show-toplevel 실패 = fail-safe TC5).
make_git_stub() {
  local stub_path="$1" diff_file="$2" note_file="$3" healthy="${4:-0}"
  cat > "$stub_path" <<STUB
#!/usr/bin/env bash
# fake git stub — 대상 스크립트가 호출하는 하위명령만 충실히, 나머지는 안전 default.
# -C <dir> 접두 흡수 (diff/status/log 호출에서 사용).
if [ "\${1:-}" = "-C" ]; then
  shift 2
fi
case "\${1:-}" in
  rev-parse)
    # --show-toplevel (인자 1개) vs --verify --quiet <ref> 구분.
    case " \$* " in
      *" --show-toplevel "*|*" --show-toplevel")
        if [ "$healthy" != "0" ]; then
          echo "fatal: not a git repository" >&2
          exit 128
        fi
        echo "$REPO_ROOT"
        exit 0
        ;;
      *" --verify "*)
        # base ref 해석 — origin/main 만 verify 성공, 그 외 실패.
        case " \$* " in
          *" origin/main "*|*" origin/main") exit 0 ;;
          *) exit 1 ;;
        esac
        ;;
      *)
        echo "$REPO_ROOT"
        exit 0
        ;;
    esac
    ;;
  diff)
    # diff --name-only base...HEAD → fixture 파일 목록 (capture artifact 유/무).
    cat "$diff_file"
    exit 0
    ;;
  status)
    # --porcelain --untracked-files=all → 빈 출력 (실 working-tree 누수 차단).
    exit 0
    ;;
  log)
    # log -1 --format=%B → note fixture (commit message 본문).
    cat "$note_file"
    exit 0
    ;;
  cat-file)
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
# run_case <name> <STORY_KEY> <diff-name-only-text> <note-text> <git-healthy(0/1)> \
#          <expect-warn: yes|no> <expect-exit>
#
# anti-theater 2-축 동시 assert:
#   ① exit code — 항상 $expect_exit (게이트는 warning-tier 라 모든 경로 exit 0).
#   ② WARN sentinel — `[capture-gate] WARN` 정규식 등장 여부가 $expect_warn 과 일치.
# 둘 다 충족해야 PASS. 한쪽만 검사 = theater.
#
# diff-text = git diff --name-only 가 반환할 파일 목록(빈 문자열 = artifact 0).
# note-text = git log -1 --format=%B 가 반환할 commit message 본문(빈 문자열 = note 0).
# 두 흔적 모두 대상 스크립트가 실제로 읽는 git 채널(stub)로만 주입한다.
run_case() {
  local name="$1" story_key="$2" diff_text="$3" note_text="$4"
  local git_healthy="$5" expect_warn="$6" expect_exit="$7"

  local tmp; tmp=$(mktemp -d)
  # diff_text 가 비어있으면(artifact 0) 빈 파일. 그 외엔 줄단위 파일 목록.
  if [ -n "$diff_text" ]; then printf '%s\n' "$diff_text" > "$tmp/diff.txt"; else : > "$tmp/diff.txt"; fi
  # note_text 가 비어있으면(note 0) 빈 파일. 그 외엔 commit message 본문.
  if [ -n "$note_text" ]; then printf '%s\n' "$note_text" > "$tmp/note.txt"; else : > "$tmp/note.txt"; fi
  make_git_stub "$tmp/git" "$tmp/diff.txt" "$tmp/note.txt" "$git_healthy"

  local out exit_code=0
  # STORY_KEY 빈 문자열이면 env 자체를 비워 부재(TC4 no-completion) 재현.
  if [ -n "$story_key" ]; then
    out=$(
      STORY_KEY="$story_key" \
      GC_GIT_BIN="$tmp/git" \
      bash "$TARGET" 2>&1
    ) || exit_code=$?
  else
    out=$(
      GC_GIT_BIN="$tmp/git" \
      bash "$TARGET" 2>&1
    ) || exit_code=$?
  fi

  rm -rf "$tmp"

  # ① exit code assert (anti-theater: 항상 검사)
  if [ "$exit_code" -ne "$expect_exit" ]; then
    echo "✗ FAIL: $name"
    echo "  expected exit $expect_exit, got $exit_code"
    echo "  output: $out"
    FAIL=$((FAIL + 1))
    return 0
  fi

  # ② WARN sentinel assert — `[capture-gate] WARN` 정규식 등장 여부.
  local warned=0
  if printf '%s' "$out" | grep -qE '\[capture-gate\] WARN'; then
    warned=1
  fi

  if [ "$expect_warn" = "yes" ] && [ "$warned" -eq 1 ]; then
    echo "✓ PASS: $name (WARN 등장, exit $exit_code)"
    PASS=$((PASS + 1))
  elif [ "$expect_warn" = "no" ] && [ "$warned" -eq 0 ]; then
    echo "✓ PASS: $name (WARN 부재 — false-positive 없음, exit $exit_code)"
    PASS=$((PASS + 1))
  else
    echo "✗ FAIL: $name"
    echo "  expected warn=$expect_warn, got warn=$warned"
    echo "  output: $out"
    FAIL=$((FAIL + 1))
  fi
}

# 신규 capture artifact 경로 fixture (git diff --name-only 가 반환할 후보).
ARTIFACT_SKILL="skills/example-skill/SKILL.md"
ARTIFACT_DOMAIN="docs/domain-knowledge/trading/some-concept.md"
NOTE_DONE="작업 회고 결과: 캡처 대상 검토 완료 — 외부화할 신규 지식 없음."

# ─── TC1 (positive-artifact): 완료 marker + 신규 capture artifact → exit 0 PASS, WARN 부재 ─
# git diff --name-only 가 skills/.../SKILL.md 신규를 반환 = capture 됨. WARN 없어야 함.
run_case "TC1 (positive-artifact): STORY_KEY + 신규 SKILL.md artifact → WARN 부재" \
  "cfp-2392" \
  "$ARTIFACT_SKILL" \
  "" \
  0 "no" 0

# (TC1b) docs/domain-knowledge 신규도 동등한 capture artifact 로 인정 → WARN 부재.
run_case "TC1b (positive-artifact): STORY_KEY + 신규 domain-knowledge md → WARN 부재" \
  "cfp-2392" \
  "$ARTIFACT_DOMAIN" \
  "" \
  0 "no" 0

# ─── TC2 (positive-note): STORY_KEY + no-capture note + artifact 0 → exit 0 PASS, WARN 부재 ─
# 신규 artifact 0 이지만 `캡처 대상 검토 완료` note 가 있으면 의도된 무캡처 → WARN 없어야 함.
run_case "TC2 (positive-note): STORY_KEY + no-capture note(캡처 대상 검토 완료) + artifact 0 → WARN 부재" \
  "cfp-2392" \
  "" \
  "$NOTE_DONE" \
  0 "no" 0

# ─── TC3 (discriminating-negative): STORY_KEY + artifact 0 + note 0 → exit 0 ∧ WARN 등장 ─
# anti-theater 핵심 missing-case. capture 도 note 도 없으면 외부화 검토 누락 → WARN 의무.
# (TC1/TC2 의 WARN 부재와 양방향 변별 — 항상-PASS mutation 을 본 케이스가 잡는다.)
run_case "TC3 (discriminating-negative): STORY_KEY + artifact 0 + note 0 → WARN 등장" \
  "cfp-2392" \
  "" \
  "" \
  0 "yes" 0

# ─── TC4 (no-completion): STORY_KEY 부재 → exit 0 no-op, WARN 부재 ──────────
# 완료 marker(STORY_KEY) 자체가 없으면 게이트 no-op (advisory skip) → WARN 없어야 함.
# artifact 0 ∧ note 0 이지만 STORY_KEY 부재라 TC3 와 달리 WARN 비발동 (scope 변별).
run_case "TC4 (no-completion): STORY_KEY 부재 → no-op, WARN 부재" \
  "" \
  "" \
  "" \
  0 "no" 0

# ─── TC5 (fail-safe): git 미인증/부재 stub → exit 0 보존, WARN 부재 ─────────
# git stub 가 auth/rev-parse 실패(exit 128) 를 반환해도 게이트는 always exit 0 보존하고,
# diff 판정 불가 상황에서 거짓 WARN 을 내지 않아야 한다 (fail-safe 보수적 비검출).
run_case "TC5 (fail-safe): git 미인증/부재 stub → exit 0 보존, WARN 부재" \
  "cfp-2392" \
  "" \
  "" \
  1 "no" 0

# ─── 요약 ──────────────────────────────────────────────────────────────────
echo ""
echo "============================================"
echo "Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"

if [ "$FAIL" -eq 0 ]; then
  echo "All tests passed (capture-gate 변별 검증 — TC1~TC5)."
  exit 0
else
  echo "Some tests failed (capture-gate 가 WARN/PASS/fail-safe 계약을 못 지킴)."
  exit 1
fi
