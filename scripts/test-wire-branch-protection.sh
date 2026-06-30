#!/usr/bin/env bash
# scripts/test-wire-branch-protection.sh
# CFP-2469 Phase 2 (Epic CFP-2468 Track W/W1) — Discriminating self-test for wire-branch-protection.sh
#
# ADR-132 §결정 1-6 — branch protection write SSOT 의 discriminating fixture (Change Plan §8 SSOT).
# 각 fixture 는 mktemp fixture-root 안에 fake `gh` stub 을 구성(PATH 주입)해 wire-* 의
# GET-merge-PUT / shape 분기 / 정합 게이트 / 403 graceful / restrictions=null 동작을 변별 assert.
#
# self-contained bash (bats 미사용 — CFP-2383 답습). run_fixture 헬퍼 + per-fixture fixture-root build.
# live GitHub 의존 0 — fake gh stub 이 모든 API 응답을 fixture-controlled JSON 으로 대체.
#
# Mutation testing 1:1 주석표 (Change Plan §8 — mutation 생존 0):
#  - Mutation-1 (shape→review_count 분기 제거: solo도 1)     → F1 (solo dry-run review_count!=0) PASS 면 RED (AC-2 deadlock)
#  - Mutation-2 (team review_count 0 강제)                   → F2 (team review_count!=1) PASS 면 RED (AC-2 team)
#  - Mutation-3 (403 → exit 2 hard-fail mutate)             → F3 (403 exit!=3) PASS 면 RED (AC-3 graceful)
#  - Mutation-4 (정합 게이트 제외 제거: 미정합도 배선)        → F4 (미정합 context 포함) PASS 면 RED (AC-4 pending)
#  - Mutation-5 (GET-merge union 제거: naive overwrite)      → F5 (consumer 고유 context 소실) PASS 면 RED (AC-5)
#  - Mutation-6 (restrictions=null → []  mutate)            → F6 (payload restrictions!=null) PASS 면 RED (§2.6)
#  - Mutation-7 (enforce_admins=true → false mutate)        → F7 (payload enforce_admins!=true) PASS 면 RED (REQ-2)
#  - Mutation-8 (--inspect dead-gate 분기 제거: 0 contexts도 exit0) → F8 (inspect 0-ctx exit!=3) PASS 면 RED (AC-6)
#  - Mutation-9 (strict=true default 제거)                  → F9 (payload strict!=true) PASS 면 RED (§결정5)
#  - Mutation-10 (_current_contexts guard 제거: 404 JSON 캡처)  → F11/F13b/F14 (payload error token 포함 / inspect contexts=1) PASS 면 RED (AC-a/AC-e)
#  - Mutation-11 (_actual_check_names guard 제거: 404 JSON 캡처) → F12a/F12b (actual set 오염) PASS 면 RED (AC-c)
#
# Exit code: 0 = all fixtures pass / 1 = any fixture fails

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WIRE="$REPO_ROOT/scripts/wire-branch-protection.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# fake gh stub builder — fixture-root/bin/gh 가 PATH 선두에서 실 gh 를 가린다.
# stub 동작은 fixture-root/gh-fixture/ 안 파일로 제어:
#   - check-runs.txt     : actual check run 표시명 (정합 게이트 input), newline-separated
#   - cur-contexts.txt   : 현 protection contexts (GET-merge input), newline-separated
#   - protection.json    : GET protection 응답 (--inspect / enforce_admins)
#   - put-exit           : PUT 시 stub 이 반환할 exit (0=성공 / 1=403 simulate)
#   - put-stderr.txt     : PUT 실패 시 stderr 내용 (403 문구 등)
#   - put-captured.txt   : PUT payload 가 여기에 기록됨 (assert 대상)
# ─────────────────────────────────────────────────────────────────────────────
build_gh_stub() {
  local root="$1"
  mkdir -p "$root/bin" "$root/gh-fixture"
  cat > "$root/bin/gh" <<'STUB'
#!/usr/bin/env bash
# fake gh stub — CFP-2469 self-test. fixture dir = $GH_FIXTURE_DIR.
FX="${GH_FIXTURE_DIR:?GH_FIXTURE_DIR unset}"
# join args
ALL="$*"

# repo view (자동 탐지)
if [[ "$ALL" == *"repo view"* ]]; then
  echo "owner/test-repo"; exit 0
fi

# PUT branch protection (--input -)
if [[ "$ALL" == *"-X PUT"* && "$ALL" == *"/protection"* ]]; then
  cat > "$FX/put-captured.txt"   # capture stdin payload
  local_exit="$(cat "$FX/put-exit" 2>/dev/null || echo 0)"
  if [ "$local_exit" != "0" ]; then
    cat "$FX/put-stderr.txt" >&2 2>/dev/null || echo "HTTP 403: Resource not accessible" >&2
    exit "$local_exit"
  fi
  echo '{"url":"ok"}'; exit 0
fi

# GET commits/<branch> → sha
if [[ "$ALL" == *"/commits/"* && "$ALL" == *"check-runs"* ]]; then
  if [ -f "$FX/check-runs-404" ]; then
    # 실 gh 404: error JSON 을 stdout 으로 emit + non-zero exit (cli/cli#5209)
    echo '{"message":"Not Found","documentation_url":"https://docs.github.com/rest","status":"404"}'; exit 1
  fi
  cat "$FX/check-runs.txt" 2>/dev/null || true
  exit 0
fi
if [[ "$ALL" == *"/commits/"* ]]; then
  if [ -f "$FX/commits-404" ]; then
    echo '{"message":"No commit found for SHA","status":"404"}'; exit 1
  fi
  echo "deadbeefsha"; exit 0
fi

# GET required_status_checks → contexts
if [[ "$ALL" == *"required_status_checks"* ]]; then
  if [ -f "$FX/rsc-404" ]; then
    echo '{"message":"Branch not protected","documentation_url":"https://docs.github.com/rest","status":"404"}'; exit 1
  fi
  cat "$FX/cur-contexts.txt" 2>/dev/null || true
  exit 0
fi

# GET protection/enforce_admins
if [[ "$ALL" == *"protection/enforce_admins"* ]]; then
  echo "true"; exit 0
fi

# GET protection (object) → --inspect
if [[ "$ALL" == *"/protection"* ]]; then
  if [ -f "$FX/protection-absent" ]; then
    echo "HTTP 404: Branch not protected" >&2; exit 1
  fi
  cat "$FX/protection.json" 2>/dev/null || echo '{"url":"ok"}'
  exit 0
fi

# default
echo "{}"; exit 0
STUB
  chmod +x "$root/bin/gh"
}

# run_fixture: wire-* 를 stub PATH 로 실행, exit + (선택) payload grep assert
# args: name expected_exit description root [extra wire args...]
run_fixture() {
  local name="$1" expected_exit="$2" description="$3" root="$4"; shift 4
  local out exit_code=0
  out=$( PATH="$root/bin:$PATH" GH_FIXTURE_DIR="$root/gh-fixture" \
         bash "$WIRE" --repo owner/test-repo "$@" 2>&1 ) || exit_code=$?
  if [ "$exit_code" -ne "$expected_exit" ]; then
    echo "✗ FAIL: $name — expected exit $expected_exit, got $exit_code"
    echo "  desc: $description"
    echo "  out: $out"
    FAIL=$((FAIL+1)); rm -rf "$root"; return 1
  fi
  echo "✓ PASS: $name (exit $exit_code) — $description"
  PASS=$((PASS+1)); rm -rf "$root"; return 0
}

# payload assertion helper — PUT payload (put-captured.txt) 에 대해 grep 조건 assert.
# args: name description root grep-mode(present|absent) pattern [extra wire args...]
run_payload_fixture() {
  local name="$1" description="$2" root="$3" mode="$4" pattern="$5"; shift 5
  local out exit_code=0
  out=$( PATH="$root/bin:$PATH" GH_FIXTURE_DIR="$root/gh-fixture" \
         bash "$WIRE" --repo owner/test-repo "$@" 2>&1 ) || exit_code=$?
  local captured="$root/gh-fixture/put-captured.txt"
  local ok=1
  if [ ! -f "$captured" ]; then
    echo "✗ FAIL: $name — PUT payload 미캡처 (PUT 미호출?). out: $out"
    FAIL=$((FAIL+1)); rm -rf "$root"; return 1
  fi
  if [ "$mode" = "present" ]; then
    grep -qF "$pattern" "$captured" || ok=0
  else
    grep -qF "$pattern" "$captured" && ok=0
  fi
  if [ "$ok" -ne 1 ]; then
    echo "✗ FAIL: $name — payload assert ($mode '$pattern') 실패"
    echo "  desc: $description"
    echo "  payload: $(cat "$captured")"
    FAIL=$((FAIL+1)); rm -rf "$root"; return 1
  fi
  echo "✓ PASS: $name — $description"
  PASS=$((PASS+1)); rm -rf "$root"; return 0
}

# ── baseline fixture-root (정합 actual = 후보 core 4 전부) ──
build_baseline() {
  local root="$1"
  build_gh_stub "$root"
  local fx="$root/gh-fixture"
  cat > "$fx/check-runs.txt" <<'EOF'
phase-gate-mergeable
invariant-check
doc frontmatter schema (CFP-28 — strict)
doc section schema (CFP-28 — strict)
EOF
  : > "$fx/cur-contexts.txt"        # 현 contexts 0
  echo "0" > "$fx/put-exit"
  echo '{"url":"ok","required_status_checks":{"contexts":["phase-gate-mergeable"]},"enforce_admins":{"enabled":true}}' > "$fx/protection.json"
}

echo "=== wire-branch-protection.sh discriminating self-test (CFP-2469) ==="

# ── F1: solo shape → review_count 0 (AC-2 deadlock 회피, Mutation-1) ──
R=$(mktemp -d); build_baseline "$R"
run_payload_fixture "F1-solo-review-count-0" "solo shape → required_approving_review_count 0 (deadlock 회피)" \
  "$R" present '"required_approving_review_count": 0' --shape solo

# ── F2: team shape → review_count 1 (AC-2 team, Mutation-2) ──
R=$(mktemp -d); build_baseline "$R"
run_payload_fixture "F2-team-review-count-1" "team shape → required_approving_review_count 1" \
  "$R" present '"required_approving_review_count": 1' --shape team

# ── F3: 403 → exit 3 graceful (AC-3, Mutation-3) ──
R=$(mktemp -d); build_baseline "$R"
echo "1" > "$R/gh-fixture/put-exit"
printf 'HTTP 403: Resource not accessible by integration\n' > "$R/gh-fixture/put-stderr.txt"
run_fixture "F3-403-graceful" 3 "403 권한 부족 → exit 3 graceful (hard-fail 아님)" "$R" --shape solo

# ── F4: 미정합 context 배선 제외 (AC-4, Mutation-4) ──
# actual check-runs 에 'invariant-check' 부재 → payload 에서 제외돼야 함.
R=$(mktemp -d); build_baseline "$R"
cat > "$R/gh-fixture/check-runs.txt" <<'EOF'
phase-gate-mergeable
EOF
run_payload_fixture "F4-context-gate-exclude" "actual 미정합 context (invariant-check) 배선 제외" \
  "$R" absent 'invariant-check' --shape solo

# ── F5: GET-merge union — consumer 고유 context 보존 (AC-5, Mutation-5) ──
R=$(mktemp -d); build_baseline "$R"
cat > "$R/gh-fixture/cur-contexts.txt" <<'EOF'
consumer-custom-check
phase-gate-mergeable
EOF
run_payload_fixture "F5-get-merge-union" "현 consumer 고유 context (consumer-custom-check) union 보존" \
  "$R" present 'consumer-custom-check' --shape solo

# ── F6: restrictions=null (§2.6, Mutation-6) ──
R=$(mktemp -d); build_baseline "$R"
run_payload_fixture "F6-restrictions-null" "restrictions null (빈배열 [] 아님 — deadlock 회피)" \
  "$R" present '"restrictions": null' --shape solo

# ── F7: enforce_admins=true (REQ-2, Mutation-7) ──
R=$(mktemp -d); build_baseline "$R"
run_payload_fixture "F7-enforce-admins-true" "enforce_admins true (dead-gate 차단 핵심)" \
  "$R" present '"enforce_admins": true' --shape solo

# ── F8: --inspect dead-gate 검출 (AC-6, Mutation-8) ──
# protection 활성이나 contexts 0 → exit 3 (dead gate).
R=$(mktemp -d); build_baseline "$R"
echo '{"url":"ok","required_status_checks":{"contexts":[]},"enforce_admins":{"enabled":true}}' > "$R/gh-fixture/protection.json"
: > "$R/gh-fixture/cur-contexts.txt"
run_fixture "F8-inspect-dead-gate" 3 "--inspect: contexts 0개 → exit 3 (dead gate 검출)" "$R" --inspect

# ── F8b: --inspect 배선됨 → exit 0 ──
R=$(mktemp -d); build_baseline "$R"
echo '{"url":"ok","required_status_checks":{"contexts":["phase-gate-mergeable"]},"enforce_admins":{"enabled":true}}' > "$R/gh-fixture/protection.json"
echo "phase-gate-mergeable" > "$R/gh-fixture/cur-contexts.txt"
run_fixture "F8b-inspect-wired" 0 "--inspect: contexts 배선됨 → exit 0" "$R" --inspect

# ── F9: strict=true default (§결정5, Mutation-9) ──
R=$(mktemp -d); build_baseline "$R"
run_payload_fixture "F9-strict-true" "required_status_checks.strict true default" \
  "$R" present '"strict": true' --shape solo

# ── F10: --dry-run PUT 0 (side-effect 0) ──
R=$(mktemp -d); build_baseline "$R"
out=$( PATH="$R/bin:$PATH" GH_FIXTURE_DIR="$R/gh-fixture" bash "$WIRE" --repo owner/test-repo --shape solo --dry-run 2>&1 ) || true
if [ -f "$R/gh-fixture/put-captured.txt" ]; then
  echo "✗ FAIL: F10-dry-run-no-put — --dry-run 인데 PUT 호출됨"; FAIL=$((FAIL+1))
else
  echo "✓ PASS: F10-dry-run-no-put — --dry-run PUT 0 (side-effect 0)"; PASS=$((PASS+1))
fi
rm -rf "$R"

# ─────────────────────────────────────────────────────────────────────────────
# CFP-2493 Phase 2 — gh GET 404 error-JSON 오염 guard (_gh_get_or_fail / Get-GhOrEmpty)
# discriminating fixture. 실 gh 는 HTTP error body 를 stdout 으로 emit + non-zero exit
# (cli/cli#5209) → `2>/dev/null||true` 로 못 막음. fix = GET 단계 exit-code guard.
# stub error-mode (check-runs-404 / commits-404 / rsc-404 토글) = stdout error JSON + exit 1.
# fix 부재(guard 제거 mutation) 시 404 JSON 1줄이 existing/actual set 으로 캡처 → 오염.
# ─────────────────────────────────────────────────────────────────────────────

# ── F11: _current_contexts 404 (unprotected branch) — error token 미오염 (AC-a, M10) ──
# rsc-404 토글 → required_status_checks GET 이 404 JSON + exit 1.
# guard: _current_contexts 빈 set 반환 → merged = applied candidates only (error token 0).
# guard 부재(M10): 404 JSON 1줄이 existing 으로 캡처 → merged union → payload contexts 에 'message' 오염 → RED.
R=$(mktemp -d); build_baseline "$R"
: > "$R/gh-fixture/cur-contexts.txt"
touch "$R/gh-fixture/rsc-404"
run_payload_fixture "F11-current-contexts-404" "unprotected branch (rsc 404) → payload contexts 에 gh-error token 0건" \
  "$R" absent 'message' --shape solo

# ── F12a: _actual_check_names sha 404 (commits 404) — actual 빈 set, error token 0건 (AC-c, M11) ──
# commits-404 토글 → sha GET 이 404 JSON + exit 1.
# guard: _actual_check_names 빈 set → 정합 게이트 "actual 0개" branch → 후보 전체 fallback → PUT(payload 정상).
# guard 부재(M11): sha 자리에 404 JSON 1줄 캡처 → check-runs GET URL 오염 + actual_raw 오염 → 후보 전체 제외 → PUT 미발생(exit 3) → run_payload "PUT 미캡처" FAIL. (양 regime 차이 = discriminating)
R=$(mktemp -d); build_baseline "$R"
touch "$R/gh-fixture/commits-404"
run_payload_fixture "F12a-actual-sha-404" "sha GET 404 → actual 빈 set + 후보 전체 fallback, payload error token 0건" \
  "$R" absent 'message' --shape solo

# ── F12b: _actual_check_names check-runs 404 (sha 정상) — actual 빈 set (AC-c, M11) ──
# check-runs-404 토글 → sha 정상(deadbeefsha) → check-runs GET 이 404 JSON + exit 1.
# guard: actual_raw 빈 → "actual 0개" branch → 후보 전체 fallback → payload 정상(error token 0).
# guard 부재(M11): actual_raw = 404 JSON 1줄 → 후보 전체가 grep -qxF 불일치로 제외 → merged 0 → exit 3 → "PUT 미캡처" FAIL.
R=$(mktemp -d); build_baseline "$R"
touch "$R/gh-fixture/check-runs-404"
run_payload_fixture "F12b-actual-checkruns-404" "check-runs GET 404 → actual 빈 set, payload error token 0건" \
  "$R" absent 'message' --shape solo

# ── F13: valid-empty (200 contexts=[]) vs 404 구분 (AC-h) ──
# 전자: cur-contexts.txt 빈 (200 정상) → 빈 set 정상 수용 → 후보 union 진행 → payload 에 phase-gate-mergeable present.
R=$(mktemp -d); build_baseline "$R"
: > "$R/gh-fixture/cur-contexts.txt"
run_payload_fixture "F13-valid-empty-200" "200 빈 contexts → 빈 set 정상 수용 + 후보 union (payload 에 phase-gate-mergeable present)" \
  "$R" present 'phase-gate-mergeable' --shape solo
# 후자: rsc-404 → 빈 set 정규화 + error token('Branch not protected') 0건 (404 ≠ valid-empty 명시 구분).
R=$(mktemp -d); build_baseline "$R"
touch "$R/gh-fixture/rsc-404"
run_payload_fixture "F13b-unprotected-404" "404 → 빈 set 정규화 + error token 0건 (valid-empty 200 과 구분)" \
  "$R" absent 'Branch not protected' --shape solo

# ── F14: unprotected rsc --inspect → contexts=0 exit 3 (404 라인을 contexts=1 오인 안 함, AC-e) ──
# protection object GET 정상(protection.json 존재) → _protection_exists true → _current_contexts 호출.
# rsc-404 → required_status_checks 404 JSON + exit 1.
# guard: _current_contexts 빈 set → cur_count=0 → exit 3.
# guard 부재(M10): 404 JSON 1줄 → grep -c . = 1 → cur_count=1 → exit 0 → RED (expected 3, got 0).
R=$(mktemp -d); build_baseline "$R"
echo '{"url":"ok","required_status_checks":{"contexts":[]},"enforce_admins":{"enabled":true}}' > "$R/gh-fixture/protection.json"
touch "$R/gh-fixture/rsc-404"
run_fixture "F14-inspect-unprotected-404" 3 "--inspect: rsc 404 → contexts=0 exit 3 (404 라인 contexts=1 오인 차단)" "$R" --inspect

echo ""
echo "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ "$FAIL" -eq 0 ] || exit 1
exit 0
