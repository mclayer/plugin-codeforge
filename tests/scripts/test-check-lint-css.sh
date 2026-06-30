#!/usr/bin/env bash
# tests/scripts/test-check-lint-css.sh
# CFP-2505 Phase 2 — Discriminating self-test for check-lint.sh CSS 분기 (ADR-136 §8 / 결정6).
#
# DeveloperAgent 의 scripts/check-lint.sh run_css_lint() 검증 (보조 채널 — consumer pre-push/manual
# lint runner). css-lint.yml(강제력) 과 직교 — check-lint.sh = 개발자 친화(early feedback).
#
# check-lint.sh 동작 (검증됨, scripts/check-lint.sh):
#  - run_css_lint(): package.json 존재 + npx 존재 + grep '"stylelint"' package.json → stylelint 실행.
#  - detect 안 되면(package.json 에 stylelint 없음) CSS 분기 return 0 → 다른 lint 영향 0.
#  - 외부 계약: exit 0=PASS/skip, 1=FAIL / --fix / --quiet (불변 — ADR-136 결정6).
#
# 본 test 가 CWD 를 fixture dir 로 바꾼 뒤 `bash <worktree>/scripts/check-lint.sh` 호출
# (check-lint.sh 는 CWD-상대 package.json/pyproject.toml detect — 호출 위치가 CWD).
#
# ── discriminating (anti-theater 비협상) ──────────────────────────────────────
#  - F-bad(미닫힌 brace) → exit 1 (FAIL) ≠ F-clean(올바른 css) → exit 0 (PASS). 둘 다 동일 결과면 hollow.
#  - F-no-stylelint(package.json 에 stylelint 없음) → CSS skip, 다른 lint 영향 0 (exit 0).
#  - 외부 계약 회귀 방지: --quiet 플래그는 출력만 축소(fix 안 함) → 미닫힌 brace 여전히 exit 1.
#    --fix 플래그도 미닫힌 brace = CssSyntaxError(parser-level) 는 unfixable → exit 1 + 파일 무변경.
#    ★ 버전 의존 동작 (실측 — 본 test 작성 중 stylelint 16 vs 17 차이 포착): stylelint 16.x 는 --fix 로
#      brace 를 auto-close(exit 0) 하지만, CI pin 17.13.0 은 CssSyntaxError 를 unfixable 로 처리 →
#      --fix 로도 exit 2(→ check-lint.sh exit 1) + 파일 무변경. parser-level 1급 방어가 --fix 로도
#      우회 불가 = ADR-136 결정4-A 와 정합(더 강한 계약). 본 test 는 CI pin(17.x) 동작을 assert.
#    ★ flag variant 별 fresh fixture 필수: 같은 fixture 재사용 시 한 케이스의 부수효과가 후속 케이스
#      결과를 오염(false-pass) — 본 test 작성 중 실측 포착(16.x 에서 --fix 가 파일 in-place 보정).
#
# ── stylelint pin (npx cache 사용) ────────────────────────────────────────────
#  check-lint.sh 의 run_css_lint() 는 `npx stylelint` (pin 무명시 — consumer node_modules 의 pinned
#  stylelint 사용 전제). 본 test 는 fixture package.json 에 stylelint pin + npx --yes 로 cache 충당.
#  STYLELINT_PIN env override. InfraEngineer preset pin 과 cross-ref.
#
# ── graceful skip ─────────────────────────────────────────────────────────────
#  npx 부재 / stylelint install 실패(offline) 시 명시 ::notice:: skip + exit 0 (silent pass 위장 금지).
#
# Exit code: 0 = all pass (or graceful skip), 1 = any fail

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHECK_LINT="$REPO_ROOT/scripts/check-lint.sh"
STYLELINT_PIN="${STYLELINT_PIN:-17.13.0}"  # wrapper preset(.stylelintrc.json/css-lint.yml) 와 일치

PASS=0
FAIL=0
SKIP=0

note() { echo "::notice::$*"; }

# check-lint.sh 존재 확인 (sibling DeveloperAgent 산출물 — run_css_lint 함수).
if [ ! -f "$CHECK_LINT" ]; then
  echo "✗ FAIL: scripts/check-lint.sh 부재 (DeveloperAgent run_css_lint 미산출)"
  exit 1
fi
if ! grep -q 'run_css_lint' "$CHECK_LINT"; then
  echo "✗ FAIL: scripts/check-lint.sh 에 run_css_lint() 부재 (DeveloperAgent 미구현 — sibling-dependent)"
  exit 1
fi

# npx precondition.
if ! command -v npx >/dev/null 2>&1; then
  note "[test-check-lint-css] npx 미설치 — graceful skip. NOT a silent pass. CI ubuntu 재검증."
  echo "SKIP: npx 부재."
  exit 0
fi

# stylelint install probe (offline graceful skip).
# 단, no-stylelint 케이스(F-no-stylelint)는 stylelint 불요 → probe 실패해도 그 케이스만은 의미.
STYLELINT_OK=1
PROBE=$(mktemp -d)
if ! ( cd "$PROBE" && timeout 240 npx --yes "stylelint@${STYLELINT_PIN}" --version >/dev/null 2>&1 ); then
  STYLELINT_OK=0
fi
rm -rf "$PROBE"

# fixture package.json 에 stylelint 를 install 해 check-lint.sh 의 `npx stylelint` 가 그것을 쓰게 한다
# (npx 가 local node_modules 우선). offline 이면 STYLELINT_OK=0 → stylelint 케이스 skip.

# ─────────────────────────────────────────────────────────────────────────────
# run_check_lint <fixture-dir> [flags...] → echo exit code
#   CWD 를 fixture-dir 로 바꿔 호출 (check-lint.sh CWD-상대 detect).
# ─────────────────────────────────────────────────────────────────────────────
run_check_lint_exit() {
  local dir="$1"; shift
  local ec=0
  ( cd "$dir" && timeout 240 bash "$CHECK_LINT" "$@" >/dev/null 2>&1 ) || ec=$?
  echo "$ec"
}

assert_eq() {
  local name="$1" expected="$2" actual="$3" desc="$4"
  if [ "$actual" = "$expected" ]; then
    echo "✓ PASS: $name (got $actual) — $desc"
    PASS=$((PASS+1)); return 0
  else
    echo "✗ FAIL: $name"
    echo "  Expected $expected, got $actual"
    echo "  Description: $desc"
    FAIL=$((FAIL+1)); return 1
  fi
}

# fixture builder: package.json(stylelint) + .stylelintrc + node_modules(stylelint install).
#   minimal config(extends 없음) — parser-level CssSyntaxError 는 rule 무관(test-css-lint.sh 와 동형).
build_stylelint_fixture() {
  local dir="$1"
  cat > "$dir/package.json" <<EOF
{ "name":"cfp2505-cl-fixture","version":"1.0.0","devDependencies":{"stylelint":"${STYLELINT_PIN}"} }
EOF
  cat > "$dir/.stylelintrc.json" <<'EOF'
{ "rules": { "block-no-empty": true } }
EOF
  ( cd "$dir" && timeout 300 npm install --no-audit --no-fund >/dev/null 2>&1 )
}

EC_BAD="n/a"; EC_CLEAN="n/a"

if [ "$STYLELINT_OK" -eq 1 ]; then
  # ══════════════════════════════════════════════════════════════════════════
  # F-bad: package.json(stylelint) + 미닫힌 brace .css → check-lint.sh exit 1 (FAIL)
  #   ★ flag variant 별 fresh fixture (--fix in-place 보정 → 재사용 금지).
  # ══════════════════════════════════════════════════════════════════════════
  FB=$(mktemp -d)
  if build_stylelint_fixture "$FB"; then
    printf '.terminal-controls .tt-live {\n  color: red;\n' > "$FB/bad.css"  # 미닫힌 brace
    EC_BAD=$(run_check_lint_exit "$FB")
    assert_eq "F-bad-blocks" "1" "$EC_BAD" "stylelint detect + 미닫힌 brace .css → check-lint.sh exit 1 (FAIL)"
    rm -rf "$FB"
  else
    note "[test-check-lint-css] F-bad fixture npm install 실패 — graceful skip."
    echo "SKIP: F-bad install 불가."; SKIP=$((SKIP+1)); rm -rf "$FB"
  fi

  # ── F-bad-quiet: fresh fixture, --quiet (출력만 축소, fix 안 함) → 미닫힌 brace 여전히 exit 1 ──
  FBQ=$(mktemp -d)
  if build_stylelint_fixture "$FBQ"; then
    printf '.terminal-controls .tt-live {\n  color: red;\n' > "$FBQ/bad.css"
    EC_BAD_QUIET=$(run_check_lint_exit "$FBQ" --quiet)
    assert_eq "F-bad-quiet-still-blocks" "1" "$EC_BAD_QUIET" "--quiet 플래그 CSS 분기 동작 — 출력만 축소, fix 안 함 → exit 1 불변(외부 계약)"
    rm -rf "$FBQ"
  else
    note "[test-check-lint-css] F-bad-quiet fixture install 실패 — graceful skip."
    echo "SKIP: F-bad-quiet install 불가."; SKIP=$((SKIP+1)); rm -rf "$FBQ"
  fi

  # ── F-bad-fix: fresh fixture, --fix → CssSyntaxError(parser-level) unfixable → exit 1 + 파일 무변경 ──
  #   --fix 의 CSS 분기 동작이지만, 미닫힌 brace = parser-level CssSyntaxError 는 stylelint 17.x 가
  #   unfixable 로 처리 → 여전히 차단(check-lint.sh exit 1). parser-level 1급 방어는 --fix 로도 우회 불가
  #   (ADR-136 결정4-A 정합). 파일은 무변경(닫는 brace 미삽입 = unfixable 증거).
  FBF=$(mktemp -d)
  if build_stylelint_fixture "$FBF"; then
    printf '.terminal-controls .tt-live {\n  color: red;\n' > "$FBF/bad.css"
    EC_BAD_FIX=$(run_check_lint_exit "$FBF" --fix)
    assert_eq "F-bad-fix-still-blocks" "1" "$EC_BAD_FIX" "--fix 플래그 CSS 분기 동작 — CssSyntaxError(parser-level) unfixable → exit 1 불변(1급 방어 우회 불가, ADR-136 결정4-A)"
    # unfixable 증거: --fix 후에도 파일에 닫는 brace 미삽입(parser error 는 auto-fix 안 됨).
    if grep -q '}' "$FBF/bad.css"; then
      echo "✗ FAIL: F-bad-fix-file-unchanged — --fix 가 brace 를 닫았다(닫는 brace 존재) = 17.x unfixable 전제 위반(pin/버전 확인 필요)"
      FAIL=$((FAIL+1))
    else
      echo "✓ PASS: F-bad-fix-file-unchanged — --fix 후 bad.css 무변경(닫는 brace 미삽입) = CssSyntaxError unfixable 확인"
      PASS=$((PASS+1))
    fi
    rm -rf "$FBF"
  else
    note "[test-check-lint-css] F-bad-fix fixture install 실패 — graceful skip."
    echo "SKIP: F-bad-fix install 불가."; SKIP=$((SKIP+1)); rm -rf "$FBF"
  fi

  # ══════════════════════════════════════════════════════════════════════════
  # F-clean: package.json(stylelint) + 올바른 .css → check-lint.sh exit 0 (PASS)
  #   F-bad ↔ F-clean discriminating.
  # ══════════════════════════════════════════════════════════════════════════
  FC=$(mktemp -d)
  if build_stylelint_fixture "$FC"; then
    printf '.foo {\n  color: red;\n}\n' > "$FC/good.css"
    EC_CLEAN=$(run_check_lint_exit "$FC")
    assert_eq "F-clean-passes" "0" "$EC_CLEAN" "stylelint detect + 올바른 .css → check-lint.sh exit 0 (PASS)"
    # clean 은 보정 대상 없음 → --fix 로도 exit 0 불변(fresh 재사용 무해 — clean fixture 는 mutate 안 됨)
    EC_CLEAN_FIX=$(run_check_lint_exit "$FC" --fix)
    assert_eq "F-clean-fix-passes" "0" "$EC_CLEAN_FIX" "--fix 플래그 — clean .css exit 0 불변(외부 계약)"
    rm -rf "$FC"
  else
    note "[test-check-lint-css] F-clean fixture npm install 실패 — graceful skip."
    echo "SKIP: F-clean install 불가."; SKIP=$((SKIP+1)); rm -rf "$FC"
  fi

  # anti-theater discriminating
  if [ "$EC_BAD" != "n/a" ] && [ "$EC_CLEAN" != "n/a" ]; then
    if [ "$EC_BAD" = "$EC_CLEAN" ]; then
      echo "✗ FAIL: ANTI-THEATER — F-bad(exit=$EC_BAD) == F-clean(exit=$EC_CLEAN) = non-discriminating hollow"
      FAIL=$((FAIL+1))
    else
      echo "✓ PASS: ANTI-THEATER discriminating — F-bad(exit=$EC_BAD) ≠ F-clean(exit=$EC_CLEAN)"
      PASS=$((PASS+1))
    fi
  fi
else
  note "[test-check-lint-css] stylelint@${STYLELINT_PIN} install 불가(offline 추정) — stylelint 케이스(F-bad/F-clean) graceful skip. NOT a silent pass. CI 재검증."
  echo "SKIP: stylelint install 불가 (F-bad/F-clean 미실행)."
  SKIP=$((SKIP+1))
fi

# ══════════════════════════════════════════════════════════════════════════
# F-no-stylelint: package.json 에 stylelint 키 없음(eslint 만, npx 도 안 깔림 가정) →
#   run_css_lint() 가 grep '"stylelint"' 실패 → CSS 분기 return 0. 다른 lint 영향 0.
#   stylelint install 불요 → STYLELINT_OK 무관 항상 실행.
#   package.json 에 lint 도구 키 0 + pyproject 없음 → RAN_ANY=0 → "no detected lint tool" skip exit 0.
# ══════════════════════════════════════════════════════════════════════════
FN=$(mktemp -d)
cat > "$FN/package.json" <<'EOF'
{ "name":"no-stylelint","version":"1.0.0" }
EOF
printf '.terminal-controls .tt-live {\n  color: red;\n' > "$FN/bad.css"  # 미닫힌 brace 이지만 stylelint detect 안 됨
EC_NO=$(run_check_lint_exit "$FN")
assert_eq "F-no-stylelint-skip" "0" "$EC_NO" "package.json 에 stylelint 키 부재 → CSS 분기 skip(detect 안 됨), 미닫힌 brace 무시 exit 0 (다른 lint 영향 0)"
rm -rf "$FN"

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2505 check-lint.sh CSS 분기)"
echo "============================================================"
echo "PASS: $PASS / FAIL: $FAIL / SKIP: $SKIP / TOTAL ASSERT: $((PASS+FAIL))"
echo "stylelint pin: ${STYLELINT_PIN}"
echo "Discriminating: F-bad exit=$EC_BAD ≠ F-clean exit=$EC_CLEAN"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All cases passed (SKIP=$SKIP 명시적 graceful skip — silent pass 아님)"
  exit 0
else
  echo "✗ Some cases failed"
  exit 1
fi
