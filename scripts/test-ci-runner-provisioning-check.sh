#!/usr/bin/env bash
# scripts/test-ci-runner-provisioning-check.sh
# Epic CFP-2607 Phase 2 (W0 부트스트랩) — Discriminating self-test for ci-runner-provisioning-check.sh
#
# ADR-147 §결정4 — self-hosted CI runner migration 의 provisioning-lint (billing-독립,
# provisioning-time / operator·hub-run). NOT a hosted GitHub Actions workflow (born-dead-gate 방지).
# 각 fixture 는 mktemp fixture-root 안에 fake `gh` stub 을 PATH 주입해 visibility 분기 /
# 변수 presence(200) vs unset(404) vs permission(403) / matrix(--require-windows) / fail-loud 토큰을 변별 assert.
#
# self-contained bash (bats 미사용 — test-wire-branch-protection.sh 답습). run_case 헬퍼 + per-case fixture-root build.
# live GitHub 의존 0 — fake gh stub 이 모든 API 응답을 fixture-controlled 출력으로 대체.
#
# Discriminating 분기 1:1 주석표 (Change Plan §8 — mutation 생존 0):
#  - D-visibility (public→exit0 var-unset)          → C1  (public 404 → exit!=0 이면 RED)
#  - D-public-warn (public+var set → WARN exit0)     → C1b (WARN 토큰 부재 시 RED — 오설정 미경고)
#  - D-selfhost-set (private+linux200 → exit0)       → C2  (exit!=0 이면 RED — false alarm)
#  - D-failloud (private+linux404 → exit1 GAP)       → C3  (exit!=1 또는 GAP 토큰 부재 → RED, AC-11)
#  - D-internal (internal 도 self-host 대상)          → C4  (internal 404 → exit1 아니면 RED)
#  - D-matrix (require-windows+win404 → exit1)       → C5  (win 토큰 부재 시 RED)
#  - D-matrix-ok (양 변수 set → exit0)                → C5b (regression-guard: 양 변수 set 통과)
#  - D-403-graceful (permission → exit3)             → C6  (exit3 아니면 RED — 403 을 fail-loud 오판)
#  - D-gh-missing (gh 부재 → exit2)                   → C7  (exit2+'gh' 토큰 — bash syntax-err exit2 collision 방어)
#  - D-usage (missing --repo → exit2)                → C8  (exit2+'--repo' 토큰 — 동상 collision 방어)
#  - D-born-dead (hosted workflow 미배선)             → C9  (workflow 가 SUT 호출 시 RED, ADR-147 §결정4(ii))
#
# distinct-marker 의무 (QADev): SUT 를 subprocess fork 하므로 exit-code 단독 판정 금지.
#   bash 는 결측파일→exit127, syntax-err→exit2. exit2 기대(C7/C8) 는 born-broken SUT(syntax-err exit2) 와
#   collision → 도메인 stdout/stderr 토큰('gh' / '--repo') 병행 assert 로 fork 진정성 discriminate.
#   exit 1(C3/C4/C5) 도 도메인 토큰(PROVISIONING GAP 등) 병행. exit 0(C1/C2/C5b) 는 표준 실패코드(127/2/1) 와
#   비-collision → exit-code 단독 충분.
#
# Exit code: 0 = all cases pass / 1 = any case fails

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUT="$REPO_ROOT/scripts/ci-runner-provisioning-check.sh"
BASH_BIN="$(command -v bash)"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# fake gh stub builder — fixture-root/bin/gh 가 PATH 선두에서 실 gh 를 가린다.
# stub 동작은 fixture-root/gh-fixture/ 안 파일로 제어:
#   - visibility.txt : `gh api repos/<r> --jq .visibility` 응답 (public|private|internal)
#   - linux-var      : CI_RUNS_ON_LINUX_JSON presence mode (200=set / 404=unset / 403=permission)
#   - windows-var    : CI_RUNS_ON_WINDOWS_JSON presence mode (동일 enum)
# 404/403 = 실 gh 처럼 stderr 에 리터럴 'HTTP 404' / 'HTTP 403' 토큰 emit + nonzero exit
# (SUT 가 stderr grep 으로 404 vs 403 구별 가능하도록 설계).
# ─────────────────────────────────────────────────────────────────────────────
build_gh_stub() {
  local root="$1"
  mkdir -p "$root/bin" "$root/gh-fixture"
  cat > "$root/bin/gh" <<'STUB'
#!/usr/bin/env bash
# fake gh stub — CFP-2607 W0 self-test. fixture dir = $GH_FIXTURE_DIR.
FX="${GH_FIXTURE_DIR:?GH_FIXTURE_DIR unset}"
ALL="$*"

# ── actions variable presence probe (WINDOWS — LINUX 보다 먼저: 이름 구별) ──
if [[ "$ALL" == *"actions/variables/CI_RUNS_ON_WINDOWS_JSON"* ]]; then
  mode="$(cat "$FX/windows-var" 2>/dev/null || echo 404)"
  case "$mode" in
    200) echo '{"name":"CI_RUNS_ON_WINDOWS_JSON","value":"[\"windows-latest\"]"}'; exit 0 ;;
    403) echo "gh: Resource not accessible by integration (HTTP 403)" >&2; exit 1 ;;
    *)   echo "gh: Not Found (HTTP 404)" >&2; exit 1 ;;
  esac
fi

# ── actions variable presence probe (LINUX) ──
if [[ "$ALL" == *"actions/variables/CI_RUNS_ON_LINUX_JSON"* ]]; then
  mode="$(cat "$FX/linux-var" 2>/dev/null || echo 404)"
  case "$mode" in
    200) echo '{"name":"CI_RUNS_ON_LINUX_JSON","value":"[\"ubuntu-latest\"]"}'; exit 0 ;;
    403) echo "gh: Resource not accessible by integration (HTTP 403)" >&2; exit 1 ;;
    *)   echo "gh: Not Found (HTTP 404)" >&2; exit 1 ;;
  esac
fi

# ── repo auto-detect (gh repo view) — harness 내 undetectable (C8 missing-repo 강건화) ──
if [[ "$ALL" == *"repo view"* ]]; then
  echo "gh: could not determine repo from environment" >&2; exit 1
fi

# ── visibility probe: gh api repos/<r> --jq .visibility ──
if [[ "$ALL" == *"repos/"* ]]; then
  cat "$FX/visibility.txt" 2>/dev/null || echo "private"
  exit 0
fi

echo "{}"; exit 0
STUB
  chmod +x "$root/bin/gh"
}

# build_fixture: fixture-root 에 gh stub + visibility/linux/windows mode 세팅
# args: root visibility linux_mode [windows_mode=404]
build_fixture() {
  local root="$1" visibility="$2" linux_mode="$3" windows_mode="${4:-404}"
  build_gh_stub "$root"
  local fx="$root/gh-fixture"
  printf '%s\n' "$visibility"   > "$fx/visibility.txt"
  printf '%s\n' "$linux_mode"   > "$fx/linux-var"
  printf '%s\n' "$windows_mode" > "$fx/windows-var"
}

# run_case: SUT 를 stub PATH 로 fork, exit + (0개 이상) stderr 토큰 present-assert.
# args: name expected_exit description root sut_args [required_stderr_token ...]
#   sut_args = 공백구분 단일 문자열(우리 args 는 공백 없음). 빈 문자열 = 무-인자(C8).
run_case() {
  local name="$1" expected_exit="$2" description="$3" root="$4" sut_args="$5"; shift 5
  local out exit_code=0
  # shellcheck disable=SC2086
  out=$( PATH="$root/bin:$PATH" GH_FIXTURE_DIR="$root/gh-fixture" \
         bash "$SUT" $sut_args 2>&1 ) || exit_code=$?
  local ok=1 reasons=""
  if [ "$exit_code" -ne "$expected_exit" ]; then
    ok=0; reasons="expected exit $expected_exit, got $exit_code"
  fi
  local tok
  for tok in "$@"; do
    if ! printf '%s' "$out" | grep -qF -- "$tok"; then
      ok=0; reasons="${reasons:+$reasons | }missing stderr token '$tok'"
    fi
  done
  if [ "$ok" -ne 1 ]; then
    echo "✗ FAIL: $name — $reasons"
    echo "  desc: $description"
    echo "  args: [$sut_args]"
    echo "  out : $out"
    FAIL=$((FAIL+1)); rm -rf "$root"; return 1
  fi
  echo "✓ PASS: $name (exit $exit_code) — $description"
  PASS=$((PASS+1)); rm -rf "$root"; return 0
}

# PATH 에서 gh(.exe) 보유 디렉토리만 제거 (coreutils 보존) — C7 gh-missing 재현.
strip_gh_from_path() {
  local newpath="" d
  local IFS=':'
  for d in $PATH; do
    [ -z "$d" ] && continue
    if [ -x "$d/gh" ] || [ -x "$d/gh.exe" ]; then continue; fi
    newpath="${newpath:+$newpath:}$d"
  done
  printf '%s' "$newpath"
}

echo "=== ci-runner-provisioning-check.sh discriminating self-test (CFP-2607 W0) ==="

# ── C1: public → exit 0 (var-unset path, D-visibility) ──
R=$(mktemp -d); build_fixture "$R" public 404
run_case "C1-public-var-unset" 0 "public repo → exit 0 (hosted 유지, 변수 unset 정상)" \
  "$R" "--repo owner/test-repo"

# ── C1b: public + 변수 set → WARN + exit 0 (D-public-warn, distinct marker) ──
R=$(mktemp -d); build_fixture "$R" public 200
run_case "C1b-public-var-set-warn" 0 "public repo 에 변수 set(오설정) → WARN 로그 + exit 0" \
  "$R" "--repo owner/test-repo" "WARN"

# ── C2: private + CI_RUNS_ON_LINUX_JSON set(200) → exit 0 (D-selfhost-set) ──
R=$(mktemp -d); build_fixture "$R" private 200
run_case "C2-private-linux-set" 0 "private(self-host 대상) + linux 변수 set → exit 0 PASS" \
  "$R" "--repo owner/test-repo"

# ── C3: private + linux unset(404) → exit 1 fail-loud + 토큰 (D-failloud, AC-11) ──
R=$(mktemp -d); build_fixture "$R" private 404
run_case "C3-private-linux-unset-failloud" 1 "private + linux 변수 unset → exit 1 fail-loud (billing-deadlock 조기 감지)" \
  "$R" "--repo owner/test-repo" "PROVISIONING GAP" "gh variable set CI_RUNS_ON_LINUX_JSON"

# ── C4: internal + var unset → exit 1 (internal 도 self-host 대상, D-internal) ──
R=$(mktemp -d); build_fixture "$R" internal 404
run_case "C4-internal-var-unset-failloud" 1 "internal(self-host 대상) + 변수 unset → exit 1 fail-loud" \
  "$R" "--repo owner/test-repo" "PROVISIONING GAP" "gh variable set CI_RUNS_ON_LINUX_JSON"

# ── C5: private matrix --require-windows, linux200 + windows404 → exit 1 (D-matrix) ──
R=$(mktemp -d); build_fixture "$R" private 200 404
run_case "C5-private-matrix-windows-unset" 1 "matrix(--require-windows): linux set + windows unset → exit 1 fail-loud" \
  "$R" "--repo owner/test-repo --require-windows" "PROVISIONING GAP" "gh variable set CI_RUNS_ON_WINDOWS_JSON"

# ── C5b: private matrix 양 변수 set → exit 0 (regression-guard, D-matrix-ok) ──
R=$(mktemp -d); build_fixture "$R" private 200 200
run_case "C5b-private-matrix-both-set" 0 "matrix(--require-windows): linux+windows 양 변수 set → exit 0 PASS" \
  "$R" "--repo owner/test-repo --require-windows"

# ── C6: private + 403 permission → exit 3 graceful + '403' 토큰 (D-403-graceful) ──
R=$(mktemp -d); build_fixture "$R" private 403
run_case "C6-private-403-graceful" 3 "private + gh api 403(권한부족) → exit 3 graceful (non-blocking WARN)" \
  "$R" "--repo owner/test-repo" "403"

# ── C7: gh 부재 → exit 2 + 'gh' 토큰 (D-gh-missing, PATH 격리 + distinct marker) ──
STRIPPED="$(strip_gh_from_path)"
c7_exit=0
c7_out=$( PATH="$STRIPPED" "$BASH_BIN" "$SUT" --repo owner/test-repo 2>&1 ) || c7_exit=$?
if [ "$c7_exit" -eq 2 ] && printf '%s' "$c7_out" | grep -qF -- "gh"; then
  echo "✓ PASS: C7-gh-missing (exit $c7_exit) — gh 부재(PATH) → exit 2 (+도메인 'gh' 토큰)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: C7-gh-missing — expected exit 2 + stderr 'gh', got exit $c7_exit"
  echo "  out : $c7_out"
  FAIL=$((FAIL+1))
fi

# ── C8: --repo 인자 누락 → exit 2 + '--repo' 토큰 (D-usage, distinct marker) ──
R=$(mktemp -d); build_fixture "$R" private 404
run_case "C8-missing-repo-arg" 2 "--repo 인자 누락 → exit 2 usage error" \
  "$R" "" "--repo"

# ── C9: born-dead-gate 구조 assertion — hosted workflow 미배선 (ADR-147 §결정4(ii)) ──
# repo-level: .github/workflows/*.yml 중 SUT 를 호출하는 것이 0 이어야 함(provisioning-lint 는
# hosted CI 가 아닌 operator/hub-run 도구 — hosted 화 시 self-hosted 미이관 repo 에서 born-dead).
WF_DIR="$REPO_ROOT/.github/workflows"
if [ ! -d "$WF_DIR" ]; then
  echo "✗ FAIL: C9-born-dead-gate — $WF_DIR 부재 (구조 검증 불가/vacuous 방지)"
  FAIL=$((FAIL+1))
elif grep -rlF "ci-runner-provisioning-check.sh" "$WF_DIR" >/dev/null 2>&1; then
  echo "✗ FAIL: C9-born-dead-gate — hosted workflow 가 provisioning-check 호출 (born-dead-gate 위반):"
  grep -rlF "ci-runner-provisioning-check.sh" "$WF_DIR"
  FAIL=$((FAIL+1))
else
  echo "✓ PASS: C9-born-dead-gate — .github/workflows/*.yml 중 ci-runner-provisioning-check.sh 호출 0건"
  PASS=$((PASS+1))
fi

echo ""
echo "=== Summary: $PASS PASS, $FAIL FAIL ==="
[ "$FAIL" -eq 0 ] || exit 1
exit 0
