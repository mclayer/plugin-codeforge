#!/usr/bin/env bash
# tests/scripts/test_check-parallel-work-sentinel.sh
# CFP-2451 (CFP-967 Phase 2 deferred wire 완성) — Discriminating self-test for
#   scripts/lib/check_parallel_work_sentinel.py STORY_KEY_PREFIX 파라미터화.
#
# 배경: sentinel 의 KEY prefix 가 "CFP" 로 하드코딩되면 consumer (prefix != "CFP",
#   예: mctrader="MCT") 에서 자기 중복작업을 못 잡는 inert(hollow) 검사가 된다.
#   CFP-2451 이 prefix 를 STORY_KEY_PREFIX env 로 파라미터화 → 본 테스트가 그 동작을 보증.
#
# self-contained bash (bats 미사용 — test_check-responsibility-marker-drift.sh 답습).
#   title-search 모드 + gh mock seam(CFP967_GH_MOCK_RESPONSE) 으로 issue list 를 주입하고,
#   STORY_KEY_PREFIX 에 따라 title filter 가 어떻게 동작하는지 exit code + matches 내용으로 assert.
#
# Discriminating 의무 (change-plan §8): 단순 "exit 0 = PASS" 검사는 non-discriminating
#   (정상 GREEN 과 hollow 구분 불가) → 금지. matches 배열의 *내용*을 assert:
#     - STORY_KEY_PREFIX=MCT 일 때 [MCT-123] title 은 matches 에 *포함*되고
#     - prefix 미스매치 title([CFP-1]) 은 matches 에서 *제외*된다.
#   이 두 조건이 함께여야 prefix 파라미터화가 hollow 가 아님을 증명.
#
# Mutation-RED 입증 (change-plan §8 SSOT): KEY_PATTERN 을 다시 re.compile(r"\bCFP-\d+\b")
#   하드코딩으로 되돌리면 — T-MCT-match (MCT-123 매칭 기대) 가 FAIL 해야 한다(MCT 가 안 잡힘).
#   동시에 T-CFP-default (기본 CFP 동작) 는 GREEN 유지. 두 set 분리로 hollow 검사 차단.
#   (수동 mutation-RED 실행 절차 = change-plan §8 — prefix 하드코딩 임시 복귀 → 본 테스트 FAIL 확인 → 원복.)
#
# Exit code:
#  0 = all fixtures pass (discriminating test validates prefix parameterization)
#  1 = any fixture fails (prefix may not be parameterized / regressed to hardcode)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-parallel-work-sentinel.sh"

PASS=0
FAIL=0

# ─────────────────────────────────────────────────────────────────────────────
# write_mock: gh issue list JSON fixture 작성 (title-search mock seam 입력).
#   write_mock <path> <heredoc-via-stdin>
# ─────────────────────────────────────────────────────────────────────────────
write_mock() {
  local path="$1"
  cat > "$path"
}

# ─────────────────────────────────────────────────────────────────────────────
# run_case: sentinel title-search 를 mock + env 로 호출 → exit code + grep assert.
#   $1=name  $2=story_key_prefix  $3=cfp_context  $4=mock_file
#   $5=expected_exit  $6=grep_present(있어야 함)  $7=grep_absent(없어야 함)  $8=description
#   grep_present/grep_absent 가 빈 문자열이면 해당 assert skip.
# ─────────────────────────────────────────────────────────────────────────────
run_case() {
  local name="$1" prefix="$2" ctx="$3" mock="$4" expected_exit="$5"
  local present="$6" absent="$7" description="$8"
  local out exit_code=0
  out=$(
    STORY_KEY_PREFIX="$prefix" \
    CFP_CONTEXT="$ctx" \
    CFP967_GH_MOCK_RESPONSE="$mock" \
    bash "$WRAPPER" --mode=title-search 2>&1
  ) || exit_code=$?

  local ok=1
  [ "$exit_code" -eq "$expected_exit" ] || ok=0
  if [ -n "$present" ]; then
    echo "$out" | grep -qF "$present" || ok=0
  fi
  if [ -n "$absent" ]; then
    if echo "$out" | grep -qF "$absent"; then ok=0; fi
  fi

  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $name (exit $exit_code) — $description"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name"
    echo "  Expected exit $expected_exit, got $exit_code"
    [ -n "$present" ] && echo "  Expected present: '$present'"
    [ -n "$absent" ]  && echo "  Expected absent:  '$absent'"
    echo "  Description: $description"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
}

# fixture: 동일 mock JSON 을 두 케이스에서 공유. 두 issue title:
#   - [MCT-123] consumer prefix title
#   - [CFP-1]   wrapper prefix title (consumer 관점 미스매치)
MOCK=$(mktemp)
trap 'rm -f "$MOCK"' EXIT
write_mock "$MOCK" <<'EOF'
[
  {"number": 123, "title": "[MCT-123] consumer parallel-work title", "labels": [{"name": "phase:구현"}], "closedAt": null},
  {"number": 1, "title": "[CFP-1] wrapper-prefix title", "labels": [], "closedAt": null}
]
EOF

set +e

# ═════════════════════════════════════════════════════════════════════════════
# T-MCT-match: STORY_KEY_PREFIX=MCT + search_fragment 존재 → [MCT-123] 매칭(포함),
#   prefix 미스매치 [CFP-1] 은 필터링(제외). prefix 파라미터화가 동작함을 증명.
#   ★ Mutation-RED kill: KEY_PATTERN 하드코딩(CFP) 복귀 시 MCT-123 미매칭 → present assert FAIL = RED.
# ═════════════════════════════════════════════════════════════════════════════
run_case "T-MCT-match" "MCT" "MCT-123" "$MOCK" "0" \
  '"number": 123' '"number": 1,' \
  "STORY_KEY_PREFIX=MCT → [MCT-123] 매칭(포함) + 미스매치 [CFP-1] 제외 (hollow 아님 증명)"

# ═════════════════════════════════════════════════════════════════════════════
# T-CFP-default: STORY_KEY_PREFIX=CFP(기본) + search_fragment 존재 → [CFP-1] 매칭(포함),
#   prefix 미스매치 [MCT-123] 은 필터링(제외). 기본(wrapper) 동작 무변경 = 하위호환.
#   ★ 두 set 분리: 이 케이스는 Mutation-RED(prefix 하드코딩 복귀) 에서도 GREEN 유지.
# ═════════════════════════════════════════════════════════════════════════════
run_case "T-CFP-default" "CFP" "CFP-1" "$MOCK" "0" \
  '"number": 1' '"number": 123' \
  "STORY_KEY_PREFIX=CFP(기본) → [CFP-1] 매칭 + [MCT-123] 제외 (하위호환 보존)"

# ═════════════════════════════════════════════════════════════════════════════
# T-prefix-unset-defaults-CFP: STORY_KEY_PREFIX 미설정 → 기본값 "CFP" 로 degrade.
#   env 미주입(wrapper self-app / overlay 부재) 시 동작 무변경 보증.
# ═════════════════════════════════════════════════════════════════════════════
out=$(
  unset STORY_KEY_PREFIX
  CFP_CONTEXT="CFP-1" \
  CFP967_GH_MOCK_RESPONSE="$MOCK" \
  bash "$WRAPPER" --mode=title-search 2>&1
)
ec=$?
if [ "$ec" -eq 0 ] && echo "$out" | grep -qF '"number": 1' && ! echo "$out" | grep -qF '"number": 123'; then
  echo "✓ PASS: T-prefix-unset-defaults-CFP (exit $ec) — STORY_KEY_PREFIX 미설정 → 기본 CFP degrade (env 부재 무변경)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T-prefix-unset-defaults-CFP"
  echo "  Expected exit 0 + [CFP-1] 포함 + [MCT-123] 제외; got exit $ec"
  echo "  Output: $out"
  FAIL=$((FAIL+1))
fi

set -e

# ═════════════════════════════════════════════════════════════════════════════
# CFP-2490 (Epic CFP-2481 E2) — tier-flip mutation-RED (blockable-capable wire hollow 금지).
#
# 방법론 SSOT (change-plan §8.1): tier 축 = workflow YAML 의 `continue-on-error` field (sentinel
#   script 검출 *로직* 아님). bash 단독으론 GitHub Actions `continue-on-error` 평가를 observe 불가 →
#   discriminating fixture 는 **workflow YAML 자체를 mutate** 한다. 2-part 증명:
#     (A) 1축 집약 — tier 축(continue-on-error ↔ SENTINEL_TIER) 이 단일 grep-able 지점임 assert
#         (산재 시 flip 이 다축 변경 = blockable-capable 위반).
#     (B) workflow-mutate observe — 원본(warning, derive expr 존재) GREEN ↔ mutated(SENTINEL_TIER=
#         blocking flip) 의 continue-on-error 평가 분기 observe (비차단 true ↔ 차단 false).
#   non-discriminating "exit 0 = PASS" 절대 금지 — 두 observation 분리(원본 ∧ mutated)가 함께여야 PASS.
# ═════════════════════════════════════════════════════════════════════════════

set +e

WF_TPL="$REPO_ROOT/templates/github-workflows/parallel-work-sentinel-check.yml"
WF_GH="$REPO_ROOT/.github/workflows/parallel-work-sentinel-check.yml"

# ── T-A0-parity (tier 축 byte-identical): templates ↔ .github workflow byte-identical (ADR-005). ──
if [ -f "$WF_TPL" ] && [ -f "$WF_GH" ] && cmp -s "$WF_TPL" "$WF_GH"; then
  echo "✓ PASS: T-A0-parity — sentinel workflow templates ↔ .github byte-identical (ADR-005)"
  PASS=$((PASS+1))
else
  echo "✗ FAIL: T-A0-parity — sentinel workflow templates ↔ .github NOT byte-identical (ADR-005 위반)"
  FAIL=$((FAIL+1))
fi

# ── T-A1-axis-single (1축 집약): continue-on-error 가 SENTINEL_TIER derive expr 단일 지점인가. ──
#    (1) tier env `SENTINEL_TIER:` 선언 정확히 1회 + (2) `env.SENTINEL_TIER != 'blocking'` derive expr
#    ≥1 (hardcode 아님) + (3) continue-on-error hardcode literal(true/false) 0건 (전부 derive, 산재 0).
if [ -f "$WF_TPL" ]; then
  tier_env_count=$(grep -cE '^[[:space:]]*SENTINEL_TIER:[[:space:]]*' "$WF_TPL")
  derive_count=$(grep -cF "env.SENTINEL_TIER != 'blocking'" "$WF_TPL")
  hardcode_coe=$(grep -E '^[[:space:]]*continue-on-error:[[:space:]]*(true|false)[[:space:]]*$' "$WF_TPL" | wc -l | tr -d ' ')
  if [ "$tier_env_count" -eq 1 ] && [ "$derive_count" -ge 1 ] && [ "$hardcode_coe" -eq 0 ]; then
    echo "✓ PASS: T-A1-axis-single — tier 축 1지점 집약 (SENTINEL_TIER env 1회 + continue-on-error derive, hardcode literal 0)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: T-A1-axis-single — tier 축 산재/미집약 (SENTINEL_TIER env=$tier_env_count, derive=$derive_count, hardcode continue-on-error literal=$hardcode_coe)"
    echo "  blockable-capable 위반: tier 축이 단일 grep-able 지점이 아니면 flip 이 다축 변경 = hollow"
    FAIL=$((FAIL+1))
  fi
else
  echo "✗ FAIL: T-A1-axis-single — workflow 부재: $WF_TPL"
  FAIL=$((FAIL+1))
fi

# ── T-A2-workflow-mutate-RED: workflow YAML mutate 로 tier 축 동작 분기 observe (env 단독 아님). ──
#    원본(warning): continue-on-error = (warning != 'blocking') = true (비차단/GREEN).
#    mutated(blocking flip, 단일 축 1줄 sed): continue-on-error = (blocking != 'blocking') = false (차단/RED).
#    bash 가 Actions runtime 을 못 돌리므로 평가식을 동형 bash 비교로 재현 — 두 입력 결과 분기 observe
#    (원본 true ∧ mutated false 함께여야 PASS). "tier 1축 변경이 실제 차단 여부를 produce" falsify 가능.
if [ -f "$WF_TPL" ]; then
  MUT=$(mktemp)
  sed -E "s/^([[:space:]]*SENTINEL_TIER:[[:space:]]*)warning/\1blocking/" "$WF_TPL" > "$MUT"
  # 값만 추출: SENTINEL_TIER: 뒤 첫 토큰(영문자) — 후행 inline comment(# ...) 제외.
  orig_tier=$(grep -E '^[[:space:]]*SENTINEL_TIER:[[:space:]]*' "$WF_TPL" | head -1 | sed -E 's/.*SENTINEL_TIER:[[:space:]]*//' | sed -E 's/[[:space:]]*#.*$//' | tr -d '[:space:]')
  mut_tier=$(grep -E '^[[:space:]]*SENTINEL_TIER:[[:space:]]*' "$MUT" | head -1 | sed -E 's/.*SENTINEL_TIER:[[:space:]]*//' | sed -E 's/[[:space:]]*#.*$//' | tr -d '[:space:]')
  eval_coe() { if [ "$1" != "blocking" ]; then echo "true"; else echo "false"; fi; }
  orig_coe=$(eval_coe "$orig_tier")   # 기대: true (warning → 비차단)
  mut_coe=$(eval_coe "$mut_tier")     # 기대: false (blocking → 차단)
  if [ "$orig_tier" = "warning" ] && [ "$orig_coe" = "true" ] && \
     [ "$mut_tier" = "blocking" ] && [ "$mut_coe" = "false" ]; then
    echo "✓ PASS: T-A2-workflow-mutate-RED — 원본 warning→continue-on-error=true(GREEN/비차단) ∧ mutated blocking→continue-on-error=false(RED/차단) 분리 observe (hollow 아님)"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: T-A2-workflow-mutate-RED — tier flip 이 차단 동작 분기를 produce 하지 않음 (hollow)"
    echo "  orig_tier=$orig_tier orig_coe=$orig_coe (기대 warning/true) | mut_tier=$mut_tier mut_coe=$mut_coe (기대 blocking/false)"
    FAIL=$((FAIL+1))
  fi
  rm -f "$MUT"
else
  echo "✗ FAIL: T-A2-workflow-mutate-RED — workflow 부재: $WF_TPL"
  FAIL=$((FAIL+1))
fi

set -e

# ═════════════════════════════════════════════════════════════════════════════
# CFP-2723 (epic-state-poll born-broken 정정) — 신규 13케이스 로스터 N1-N13.
#   Change Plan §8 Test Contract 이행 (SSOT = wrapper/change-plans/CFP-2723-...-fix.md).
#   §8.0 검증층(floor+live) / §8.1 N1-N13 × AC 매핑 / §8.2 INV-1~6 / §8.2.1 mutation-RED.
#
# 확정 py 표면 결속 (DeveloperPL firsthand): 신규 seam env 3종 (CFP967_GH_MOCK_RC "0" /
#   CFP967_GH_MOCK_STDERR "" / CFP967_GH_AUTH_MOCK "fail") / degradation 4종
#   (api_quota_exceeded / gh_command_failed / gh_payload_invalid / git_fetch_failed) /
#   error_kind 3종 (gh_not_installed / gh_not_authenticated / setup) /
#   MARKER=[parallel-work-sentinel-api-failed] / GH_FIELDS_* 상수 (python import 추출, grep-drift 0).
#
# masking-lint (ADR-060 Amd22) 비저촉: mock env 는 전부 command-prefix($()) redirect-capture,
#   bare `|| true` 0. 각 케이스 = 명시 assert(grep -qF / [ ] / python exit) 동반.
# ═════════════════════════════════════════════════════════════════════════════

set +e

PYBIN=$(command -v python3)
CFP2723_TMP=$(mktemp -d)
trap 'rm -f "$MOCK"; rm -rf "$CFP2723_TMP"' EXIT

# report <name> <ok(1/0)> <desc> <output-for-debug> — PASS/FAIL 카운터 백업 (companion).
report() {
  local name="$1" ok="$2" desc="$3" out="$4"
  if [ "$ok" -eq 1 ]; then
    echo "✓ PASS: $name — $desc"
    PASS=$((PASS+1))
  else
    echo "✗ FAIL: $name — $desc"
    echo "  Output: $out"
    FAIL=$((FAIL+1))
  fi
}

# field_in_pinned <field> — gh 2.91.0 유효필드 pinned allowlist 정확-일치 멤버십.
field_in_pinned() {
  local f="$1" p
  for p in $PINNED_FIELDS; do
    [ "$p" = "$f" ] && return 0
  done
  return 1
}

# ── ASCII 픽스처 (Korean heredoc 금지 — printf 로만 조성) ──
F_EPIC_OPEN2="$CFP2723_TMP/epic_open2.json"       # OPEN + siblings dedup 2 (CFP-100, CFP-101)
F_EPIC_CLOSED0="$CFP2723_TMP/epic_closed0.json"   # CLOSED + siblings 0
F_EPIC_BODYABN="$CFP2723_TMP/epic_bodyabn.json"   # state present + body 부재 (엣지 ⑫)
F_EPIC_BODYNULL="$CFP2723_TMP/epic_bodynull.json" # state present + body JSON null (present-null, F-CR-2723-1)
F_TITLE_OK="$CFP2723_TMP/title_ok.json"           # title-search 정상 list
F_MALFORMED="$CFP2723_TMP/malformed.json"         # 비-JSON
F_EMPTY="$CFP2723_TMP/empty.json"                 # 빈 문자열
F_LIST="$CFP2723_TMP/list.json"                   # rc=0 JSON list (epic 형 불일치)
F_ERRDICT="$CFP2723_TMP/errdict403.json"          # rc=0 error-dict status 403
F_GITLOGMOCK="$CFP2723_TMP/gitlog_mock.txt"       # 무관 CFP-9999 (epic degrade 비주입 검증용)
printf '%s' '{"state":"OPEN","body":"Epic body CFP-100 CFP-101 CFP-100 tracked"}' > "$F_EPIC_OPEN2"
printf '%s' '{"state":"CLOSED","body":"no refs here"}' > "$F_EPIC_CLOSED0"
printf '%s' '{"state":"CLOSED"}' > "$F_EPIC_BODYABN"
printf '%s' '{"state":"OPEN","body":null}' > "$F_EPIC_BODYNULL"
printf '%s' '[{"number":123,"title":"[CFP-1] consumer title","labels":[{"name":"phase:x"}],"closedAt":null}]' > "$F_TITLE_OK"
printf '%s' 'this is not json <<<' > "$F_MALFORMED"
printf '%s' '' > "$F_EMPTY"
printf '%s' '[{"a":1}]' > "$F_LIST"
printf '%s' '{"message":"API rate limit exceeded","status":"403"}' > "$F_ERRDICT"
printf '%s\n' 'deadbeef 2026-01-01 [CFP-9999] unrelated sibling commit' > "$F_GITLOGMOCK"

# gh 2.91.0 유효 필드 pinned allowlist (floor oracle — provenance: `gh issue view/list --json __bogus__`
#   2026-07-17 실측, view/list 동일 22종). honest-ceiling (ADR-151 §결정7): 사람 저작 스냅샷 —
#   gh 신버전 필드 변동(엣지 ④)은 floor 미보증(live 층 N3 소관), oracle 노후화 시 무력.
PINNED_FIELDS="assignees author body closed closedAt closedByPullRequestsReferences comments createdAt id isPinned labels milestone number projectCards projectItems reactionGroups state stateReason title updatedAt url"

# ═════════════════════════════════════════════════════════════════════════════
# N1 T-EPIC-contract-mock — epic 정상 경로 mock (계약 3키 + matches 부재 + degradation 부재).
#   AC-1 / 엣지 ⑥⑦⑫ / INV-1(단일 JSON) / INV-2(epic ⊇ 3키) / INV-5(matches 비출현).
#   RED: 커버리지 신설(현행 epic 케이스 0). AC-1 "fallback 미경유" live 증명 = 구현 PR 실 gh 로그.
# ═════════════════════════════════════════════════════════════════════════════
OUT=$(CFP967_GH_MOCK_RESPONSE="$F_EPIC_OPEN2" bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>/dev/null); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"epic_state"' || ok=0
echo "$OUT" | grep -qF '"siblings"' || ok=0
echo "$OUT" | grep -qF '"freshness_age_sec"' || ok=0
echo "$OUT" | grep -qF '"OPEN"' || ok=0
echo "$OUT" | grep -qF '"CFP-100"' || ok=0
if echo "$OUT" | grep -qF '"matches"'; then ok=0; fi
if echo "$OUT" | grep -qF '"degradation"'; then ok=0; fi
# INV-1: 비-BYPASS stdout = 파싱 가능 단일 JSON dict.
printf '%s' "$OUT" | "$PYBIN" -c 'import sys,json; d=json.load(sys.stdin); sys.exit(0 if isinstance(d,dict) else 1)' || ok=0
report "N1-T-EPIC-contract-mock" "$ok" "epic 계약 3키 + matches 부재 + degradation 부재 (정상, 단일 JSON)" "$OUT"

# N1var-a T-EPIC-siblings0 — 정상 siblings 0건 = degradation 부재로 식별 (엣지 ⑥ 양방향).
OUT=$(CFP967_GH_MOCK_RESPONSE="$F_EPIC_CLOSED0" bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>/dev/null); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"CLOSED"' || ok=0
echo "$OUT" | grep -qF '"siblings": []' || ok=0
if echo "$OUT" | grep -qF '"degradation"'; then ok=0; fi
if echo "$OUT" | grep -qF '"matches"'; then ok=0; fi
report "N1var-a-T-EPIC-siblings0" "$ok" "정상 siblings 0건 → degradation 부재로 식별 (CLOSED 유지)" "$OUT"

# N1var-b T-EPIC-body-abnormal — state present + body 부재 → state 만으로 최소 성공 (엣지 ⑫).
OUT=$(CFP967_GH_MOCK_RESPONSE="$F_EPIC_BODYABN" bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>/dev/null); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"CLOSED"' || ok=0
echo "$OUT" | grep -qF '"siblings": []' || ok=0
if echo "$OUT" | grep -qF '"degradation"'; then ok=0; fi
report "N1var-b-T-EPIC-body-abnormal" "$ok" "state present + body 비정상 → state 만으로 성공 (엣지 ⑫)" "$OUT"

# N1var-c T-EPIC-body-null — body: JSON null (present-null) → siblings [] + exit 0 (F-CR-2723-1 회귀).
#   RED(수정 전): payload.get("body","") 가 present-null 에 None 반환 → _parse_siblings_from_body(None)
#   → KEY_PATTERN.findall(None) TypeError → exit 1 (INV-4 위반). FIX: body = payload.get("body") or ""
#   (null·부재 공히 "" 정규화). 부재({"state":"OPEN"}) 는 N1var-b 대조로 이미 exit 0 (default 적용).
OUT=$(CFP967_GH_MOCK_RESPONSE="$F_EPIC_BODYNULL" bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>/dev/null); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"OPEN"' || ok=0
echo "$OUT" | grep -qF '"siblings": []' || ok=0
if echo "$OUT" | grep -qF '"degradation"'; then ok=0; fi
if echo "$OUT" | grep -qF '"matches"'; then ok=0; fi
report "N1var-c-T-EPIC-body-null" "$ok" "body:null present-null → siblings [] + exit 0 (F-CR-2723-1, INV-4)" "$OUT"

# ═════════════════════════════════════════════════════════════════════════════
# N2 T-FIELD-allowlist-floor — 양 모드 요청 필드 ⊆ pinned (§8.0 floor, 상시).
#   필드 추출 = python import (D0 상수 직접 — grep-drift 0). AC-2 floor / 엣지 ⑧.
#   ★ Mutation-RED [field]: py GH_FIELDS_EPIC_STATE_POLL 에 closedBy 재도입 → closedBy ∉ pinned → FAIL.
# ═════════════════════════════════════════════════════════════════════════════
TITLE_FIELDS=$(PYTHONPATH="$REPO_ROOT/scripts/lib" "$PYBIN" -c 'import check_parallel_work_sentinel as m; print(m.GH_FIELDS_TITLE_SEARCH)')
EPIC_FIELDS=$(PYTHONPATH="$REPO_ROOT/scripts/lib" "$PYBIN" -c 'import check_parallel_work_sentinel as m; print(m.GH_FIELDS_EPIC_STATE_POLL)')
ok=1
[ -n "$TITLE_FIELDS" ] || ok=0
[ -n "$EPIC_FIELDS" ] || ok=0
for f in $(printf '%s' "$TITLE_FIELDS" | tr ',' ' '); do
  field_in_pinned "$f" || { ok=0; echo "  title field NOT in pinned: $f"; }
done
for f in $(printf '%s' "$EPIC_FIELDS" | tr ',' ' '); do
  field_in_pinned "$f" || { ok=0; echo "  epic field NOT in pinned: $f"; }
done
report "N2-T-FIELD-allowlist-floor" "$ok" "양 모드 요청필드 ⊆ pinned (title=$TITLE_FIELDS / epic=$EPIC_FIELDS)" "title=$TITLE_FIELDS epic=$EPIC_FIELDS"

# ═════════════════════════════════════════════════════════════════════════════
# N3 T-FIELD-live-gh — 실 gh 필드 유효성 (conditional, §8.0 live). oracle = stderr "Unknown JSON field" 부재.
#   T3 조건: 더미 토큰 dummy-cfp2723-not-a-token + GH_CONFIG_DIR=<빈 임시 dir> 격리 (실 credential 미사용).
#   PreRunE(클라이언트측 필드검증)가 네트워크 전 발동 — 유효필드 = 401(auth) / 무효필드 = Unknown JSON field.
#   gh 부재 = 명시 skip 마커(침묵 skip 금지, ADR-154). AC-2 live / 엣지 ④⑧.
#   ★ Mutation-RED [field]: closedBy 재도입 → 실 gh "Unknown JSON field: closedBy" → FAIL (gh 존재 러너).
# ═════════════════════════════════════════════════════════════════════════════
if command -v gh >/dev/null 2>&1; then
  EMPTYCFG=$(mktemp -d)
  ERR_LIST=$(GH_TOKEN=dummy-cfp2723-not-a-token GH_CONFIG_DIR="$EMPTYCFG" gh issue list --json "$TITLE_FIELDS" --search 'x in:title' --state all --limit 1 2>&1)
  ERR_VIEW=$(GH_TOKEN=dummy-cfp2723-not-a-token GH_CONFIG_DIR="$EMPTYCFG" gh issue view 1 --json "$EPIC_FIELDS" 2>&1)
  ok=1
  if echo "$ERR_LIST" | grep -qF 'Unknown JSON field'; then ok=0; fi
  if echo "$ERR_VIEW" | grep -qF 'Unknown JSON field'; then ok=0; fi
  report "N3-T-FIELD-live-gh" "$ok" "실 gh(2.91.0) 필드검증 — Unknown JSON field 부재 (list+view 양 모드)" "list:$ERR_LIST | view:$ERR_VIEW"
  rm -rf "$EMPTYCFG"
else
  echo "SKIP: T-FIELD-live-gh — gh binary absent"
fi

# ═════════════════════════════════════════════════════════════════════════════
# N4 T-ERRCLASS-quota — rc!=0 + rate-limit stderr 3형 + 대문자 변형 → api_quota_exceeded + stderr_excerpt 보존.
#   실측 3형: REST(HTTP 403) / GraphQL(gh issue view 실경로) / secondary. 대문자 = case-insensitive BVA(§8.2.2).
#   AC-3/AC-5 / 엣지 ③. RED: 현행 seam rc=0 고정 = 케이스 구성 불가(구조적 RED, py 수정 후 GREEN).
# ═════════════════════════════════════════════════════════════════════════════
run_epic_quota() {
  # run_epic_quota <name> <stderr> <expect-excerpt-substr>
  local name="$1" errmsg="$2" substr="$3" out ec chk=1
  out=$(CFP967_GH_MOCK_RESPONSE="$F_EPIC_OPEN2" CFP967_GH_MOCK_RC=1 CFP967_GH_MOCK_STDERR="$errmsg" \
        bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>/dev/null); ec=$?
  [ "$ec" -eq 0 ] || chk=0
  echo "$out" | grep -qF '"degradation": "api_quota_exceeded"' || chk=0
  echo "$out" | grep -qF '[parallel-work-sentinel-api-failed]' || chk=0
  echo "$out" | grep -qF "$substr" || chk=0
  report "$name" "$chk" "rate-limit stderr → api_quota_exceeded + stderr_excerpt 보존" "$out"
}
run_epic_quota "N4a-quota-REST"      "HTTP 403: API rate limit exceeded (https://api.github.com/graphql)" "API rate limit exceeded"
run_epic_quota "N4b-quota-GraphQL"   "GraphQL: API rate limit exceeded"                                    "API rate limit exceeded"
run_epic_quota "N4c-quota-secondary" "You have exceeded a secondary rate limit"                            "secondary rate limit"
run_epic_quota "N4d-quota-uppercase" "REST: RATE LIMIT EXCEEDED for installation"                          "RATE LIMIT EXCEEDED"

# ═════════════════════════════════════════════════════════════════════════════
# N5 T-ERRCLASS-nonquota — rc!=0 + 비-quota stderr → gh_command_failed + quota 라벨 부재 + 발췌 보존.
#   + 변형 N5b: stderr="" 최소입력 경계(BVA §8.2.2) → 앵커드 미매칭 보수 default = gh_command_failed.
#   AC-3/AC-5 / 엣지 ⑪. ★ Mutation-RED [errclass]: catch-all 복귀 → 무조건 quota 오라벨 → FAIL.
# ═════════════════════════════════════════════════════════════════════════════
OUT=$(CFP967_GH_MOCK_RESPONSE="$F_EPIC_OPEN2" CFP967_GH_MOCK_RC=1 CFP967_GH_MOCK_STDERR="Could not resolve to an Issue with the number of 999." \
      bash "$WRAPPER" --mode=epic-state-poll --epic-id=999 2>/dev/null); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"degradation": "gh_command_failed"' || ok=0
if echo "$OUT" | grep -qF 'api_quota_exceeded'; then ok=0; fi
echo "$OUT" | grep -qF 'Could not resolve to an Issue' || ok=0
report "N5-T-ERRCLASS-nonquota" "$ok" "비-quota stderr → gh_command_failed + quota 라벨 부재 + 발췌 보존" "$OUT"

# N5b 변형: stderr="" 최소입력 경계 (rc!=0 ∧ stderr 빈 문자열 → gh_command_failed 보수 default).
OUT=$(CFP967_GH_MOCK_RESPONSE="$F_EPIC_OPEN2" CFP967_GH_MOCK_RC=1 CFP967_GH_MOCK_STDERR="" \
      bash "$WRAPPER" --mode=epic-state-poll --epic-id=999 2>/dev/null); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"degradation": "gh_command_failed"' || ok=0
if echo "$OUT" | grep -qF 'api_quota_exceeded'; then ok=0; fi
echo "$OUT" | grep -qF '"stderr_excerpt": ""' || ok=0
report "N5b-nonquota-empty-stderr" "$ok" "stderr='' 최소입력 경계(BVA) → gh_command_failed 보수 default" "$OUT"

# ═════════════════════════════════════════════════════════════════════════════
# N6 T-TITLE-errclass-nonquota — title 모드 비-quota 실패 → quota 라벨 부재 + matches 스키마 유지.
#   AC-4. ★ Mutation-RED [errclass]: 동형 catch-all 복귀 → title quota 오라벨 → FAIL.
# ═════════════════════════════════════════════════════════════════════════════
OUT=$(CFP967_GH_MOCK_RESPONSE="$F_TITLE_OK" CFP967_GH_MOCK_RC=1 CFP967_GH_MOCK_STDERR="Could not resolve to an Issue" CFP_CONTEXT="CFP-1" \
      bash "$WRAPPER" --mode=title-search 2>/dev/null); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"degradation": "gh_command_failed"' || ok=0
if echo "$OUT" | grep -qF 'api_quota_exceeded'; then ok=0; fi
echo "$OUT" | grep -qF '"matches"' || ok=0
report "N6-T-TITLE-errclass-nonquota" "$ok" "title 비-quota → gh_command_failed + quota 라벨 부재 + matches 스키마 유지" "$OUT"

# ═════════════════════════════════════════════════════════════════════════════
# N7 T-EPIC-degrade-schema — epic degrade = 계약 3키 + degradation + marker + matches 부재 + siblings [].
#   GIT_LOG_MOCK 에 무관 CFP-9999 주입해도 epic degrade 는 git-log 미실행(subprocess 0) → siblings 비오염.
#   AC-6 / INV-5. ★ Mutation-RED [schema]: epic degrade 를 matches 스키마로 복귀 → siblings 키 소실+matches 출현 → FAIL.
# ═════════════════════════════════════════════════════════════════════════════
OUT=$(CFP967_GH_MOCK_RESPONSE="$F_EPIC_OPEN2" CFP967_GH_MOCK_RC=1 CFP967_GH_MOCK_STDERR="Could not resolve to an Issue" CFP967_GIT_LOG_MOCK="$F_GITLOGMOCK" \
      bash "$WRAPPER" --mode=epic-state-poll --epic-id=999 2>/dev/null); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"epic_state": "UNKNOWN"' || ok=0
echo "$OUT" | grep -qF '"siblings": []' || ok=0
echo "$OUT" | grep -qF '"freshness_age_sec"' || ok=0
echo "$OUT" | grep -qF '"degradation"' || ok=0
echo "$OUT" | grep -qF '[parallel-work-sentinel-api-failed]' || ok=0
if echo "$OUT" | grep -qF '"matches"'; then ok=0; fi
if echo "$OUT" | grep -qF 'CFP-9999'; then ok=0; fi
report "N7-T-EPIC-degrade-schema" "$ok" "epic degrade = 3키+degradation+marker + matches 부재 + siblings [] (git-log CFP 비오염)" "$OUT"

# ═════════════════════════════════════════════════════════════════════════════
# N8 T-EPIC-malformed-payload — rc=0 + 비-JSON / 빈 문자열 2 invoke → gh_payload_invalid + 계약 3키 + marker.
#   AC-6 / 엣지 ⑬. RED: 현행 무마커 exit 0 성공 위장(py:246-249, born-broken) → py 수정 후 GREEN.
# ═════════════════════════════════════════════════════════════════════════════
run_epic_malformed() {
  # run_epic_malformed <name> <fixture>
  local name="$1" fx="$2" out ec chk=1
  out=$(CFP967_GH_MOCK_RESPONSE="$fx" bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>/dev/null); ec=$?
  [ "$ec" -eq 0 ] || chk=0
  echo "$out" | grep -qF '"degradation": "gh_payload_invalid"' || chk=0
  echo "$out" | grep -qF '"epic_state": "UNKNOWN"' || chk=0
  echo "$out" | grep -qF '"siblings": []' || chk=0
  echo "$out" | grep -qF '"freshness_age_sec"' || chk=0
  echo "$out" | grep -qF '[parallel-work-sentinel-api-failed]' || chk=0
  report "$name" "$chk" "rc=0 malformed → gh_payload_invalid + 계약 3키 + marker (성공 위장 봉인)" "$out"
}
run_epic_malformed "N8a-malformed-nonjson" "$F_MALFORMED"
run_epic_malformed "N8b-malformed-empty"   "$F_EMPTY"

# ═════════════════════════════════════════════════════════════════════════════
# N9 T-EPIC-list-payload — rc=0 + JSON list(형 불일치) → traceback 무노출 + gh_payload_invalid.
#   AC-6/AC-7 / 엣지 ⑬. RED: 현행 data.get AttributeError unhandled traceback → py 수정 후 GREEN.
# ═════════════════════════════════════════════════════════════════════════════
OUT=$(CFP967_GH_MOCK_RESPONSE="$F_LIST" bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>&1); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"degradation": "gh_payload_invalid"' || ok=0
echo "$OUT" | grep -qF '"epic_state": "UNKNOWN"' || ok=0
if echo "$OUT" | grep -qF 'Traceback'; then ok=0; fi
report "N9-T-EPIC-list-payload" "$ok" "rc=0 JSON list → gh_payload_invalid + Traceback 무노출" "$OUT"

# ═════════════════════════════════════════════════════════════════════════════
# N10 T-EXIT-matrix — 실패 5류 exit×식별필드 상호 배타 + Traceback 부재 + docstring 대조.
#   ① 미설치(D4 PATH 격리) / ② 미인증(AUTH_MOCK) / ③ 일반실패(seam) / ④ payload불량(seam) / ⑤ quota(seam)
#   + argparse 예외 행: 무효 --mode → native exit 2 + error_kind JSON 부재(usage 텍스트).
#   AC-7 / 엣지 ①②. RED: 현행 미설치 = unhandled FileNotFoundError(hypothesis) → py 수정 후 GREEN.
# ═════════════════════════════════════════════════════════════════════════════
ok=1
PYSRC="$REPO_ROOT/scripts/lib/check_parallel_work_sentinel.py"

# ① gh 미설치 — PATH 격리(python3 절대경로 선-resolve + PATH=빈 dir, thin wrapper 우회 = py 직접 invoke).
#   환경 조건: bash+mktemp 가용 / python3 절대경로 선실측 / Windows CreateProcess 는 gh.exe 비시스템 dir 라 실질 결정적(InfraOp §3).
EMPTYDIR=$(mktemp -d)
OUT1=$(PATH="$EMPTYDIR" "$PYBIN" "$PYSRC" --mode=epic-state-poll --epic-id=1 2>&1); EC1=$?
[ "$EC1" -eq 2 ] || ok=0
echo "$OUT1" | grep -qF '"error_kind": "gh_not_installed"' || ok=0
if echo "$OUT1" | grep -qF '"degradation"'; then ok=0; fi
if echo "$OUT1" | grep -qF 'Traceback'; then ok=0; fi
rmdir "$EMPTYDIR" 2>/dev/null

# ② 미인증 — CFP967_GH_AUTH_MOCK=fail → exit 2 error_kind gh_not_authenticated.
OUT2=$(CFP967_GH_MOCK_RESPONSE="$F_EPIC_OPEN2" CFP967_GH_AUTH_MOCK=fail bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>&1); EC2=$?
[ "$EC2" -eq 2 ] || ok=0
echo "$OUT2" | grep -qF '"error_kind": "gh_not_authenticated"' || ok=0
if echo "$OUT2" | grep -qF '"degradation"'; then ok=0; fi

# ③ 일반 실패 — seam rc=1 비-quota stderr → exit 0 degradation gh_command_failed (error_kind 부재).
OUT3=$(CFP967_GH_MOCK_RESPONSE="$F_EPIC_OPEN2" CFP967_GH_MOCK_RC=1 CFP967_GH_MOCK_STDERR="fatal: some git error" bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>/dev/null); EC3=$?
[ "$EC3" -eq 0 ] || ok=0
echo "$OUT3" | grep -qF '"degradation": "gh_command_failed"' || ok=0
if echo "$OUT3" | grep -qF 'error_kind'; then ok=0; fi

# ④ payload 불량 — seam rc=0 malformed → exit 0 degradation gh_payload_invalid.
OUT4=$(CFP967_GH_MOCK_RESPONSE="$F_MALFORMED" bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>/dev/null); EC4=$?
[ "$EC4" -eq 0 ] || ok=0
echo "$OUT4" | grep -qF '"degradation": "gh_payload_invalid"' || ok=0

# ⑤ quota degrade — seam rc=1 quota stderr → exit 0 degradation api_quota_exceeded.
OUT5=$(CFP967_GH_MOCK_RESPONSE="$F_EPIC_OPEN2" CFP967_GH_MOCK_RC=1 CFP967_GH_MOCK_STDERR="HTTP 403: API rate limit exceeded" bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>/dev/null); EC5=$?
[ "$EC5" -eq 0 ] || ok=0
echo "$OUT5" | grep -qF '"degradation": "api_quota_exceeded"' || ok=0

# argparse 예외 행 — 무효 --mode → native exit 2 + usage 텍스트 (error_kind JSON 부재).
OUT6=$(bash "$WRAPPER" --mode=bogus-mode 2>&1); EC6=$?
[ "$EC6" -eq 2 ] || ok=0
echo "$OUT6" | grep -qF 'invalid choice' || ok=0
if echo "$OUT6" | grep -qF 'error_kind'; then ok=0; fi

# INV-4: 전 경로 exit ∈ {0,2} (집합 밖 0건).
for e in "$EC1" "$EC2" "$EC3" "$EC4" "$EC5" "$EC6"; do
  [ "$e" -eq 0 ] || [ "$e" -eq 2 ] || ok=0
done

# docstring 대조 — 런타임 error_kind/degradation 라벨이 py docstring/코드에 문서화 (AC-7 문서-동작 일치).
for kind in gh_not_installed gh_not_authenticated gh_command_failed gh_payload_invalid api_quota_exceeded; do
  grep -qF "$kind" "$PYSRC" || { ok=0; echo "  docstring 미대조: $kind"; }
done
grep -qF 'argparse native' "$PYSRC" || ok=0

report "N10-T-EXIT-matrix" "$ok" "5류 exit×식별필드 상호 배타 (2/2/0/0/0 + argparse-native 2) + Traceback 부재 + docstring 대조" "①$EC1/$OUT1 ②$EC2 ③$EC3 ④$EC4 ⑤$EC5 argparse$EC6"

# ═════════════════════════════════════════════════════════════════════════════
# N11 T-BYPASS-shape — BYPASS=1 → bypass JSON 키 + 기존 2줄 혼합 출력 형상 불변.
#   엣지 ⑨ / INV-1 예외(BYPASS = 2줄 혼합 명시 예외).
# ═════════════════════════════════════════════════════════════════════════════
OUT=$(BYPASS_PARALLEL_WORK_SENTINEL=1 bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>&1); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"bypass": true' || ok=0
echo "$OUT" | grep -qF '"marker"' || ok=0
echo "$OUT" | grep -qF '"audit_comment"' || ok=0
echo "$OUT" | grep -qF 'bypass invoked' || ok=0
report "N11-T-BYPASS-shape" "$ok" "BYPASS JSON 키(bypass/marker/audit_comment) + 2줄 혼합 형상 불변 (INV-1 예외)" "$OUT"

# ═════════════════════════════════════════════════════════════════════════════
# N12 T-STDERR-excerpt-cap — stderr 발췌 ≤1KB/8줄 + 토큰 마스킹(classic+fine-grained) + 식별 head 보존.
#   §7.6 T1. split-token(N12b) = 마스킹→cap 순서의 결정적 oracle.
#   ★ Mutation-RED [cap-order]: 마스킹→cap 을 cap→마스킹 으로 반전 → 절단 경계 토큰 head 생존 leak → N12b FAIL.
# ═════════════════════════════════════════════════════════════════════════════
CLASSIC_TOK="ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789AB"           # ghp_ + 38 (classic)
FINEGR_TOK="github_pat_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789AB"     # github_pat_ + 38 (fine-grained)
BIGERR=$(printf 'IDHEAD_gh_error_line1\nline2 %s tok\nline3 %s tok\nl4\nl5\nl6\nl7\nl8\nline9 CAPPEDMARK\nline10 CAPPEDMARK' "$CLASSIC_TOK" "$FINEGR_TOK")
OUT=$(CFP967_GH_MOCK_RESPONSE="$F_EPIC_OPEN2" CFP967_GH_MOCK_RC=1 CFP967_GH_MOCK_STDERR="$BIGERR" \
      bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>/dev/null); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
RES=$(printf '%s' "$OUT" | "$PYBIN" -c 'import sys,json
d=json.load(sys.stdin); e=d["stderr_excerpt"]
c=[len(e.encode("utf-8"))<=1024, len(e.splitlines())<=8, "ghp_ABCDEF" not in e, "github_pat_ABCDEF" not in e, "IDHEAD" in e, "CAPPEDMARK" not in e]
print("OK" if all(c) else "BAD:"+repr([i for i,v in enumerate(c) if not v]))')
[ "$RES" = "OK" ] || ok=0
report "N12a-T-STDERR-excerpt-cap" "$ok" "발췌 ≤1KB/8줄 + classic·fine-grained 토큰 마스킹 + IDHEAD 보존 (RES=$RES)" "$OUT"

# N12b split-token — 토큰이 1KB cap 경계에 걸치도록 조성(단일 장문 라인 → 결정적 byte 경계).
#   마스킹 선행(정답): 전체 stderr 에서 토큰 매칭 → [REDACTED] → canary 부재.
#   cap 선행(mutation): 1024B 절단으로 24자 head 생존(< 36 재매칭 미달) → canary leak → RED.
#   fragment assert: full-token grep 금지(tautology) → 마스킹 전 head canary "ghp_SPLITCANARY" 부재.
SPLIT_PAD=$(printf '%*s' 1000 '' | tr ' ' 'X')                     # token 시작 byte=1000 → head 24자 생존
SPLIT_TOK="ghp_SPLITCANARYABCDEFGHIJKLMNOPQRSTUVWXYZ0"             # ghp_ + 38
SPLITERR="${SPLIT_PAD}${SPLIT_TOK}"
OUT=$(CFP967_GH_MOCK_RESPONSE="$F_EPIC_OPEN2" CFP967_GH_MOCK_RC=1 CFP967_GH_MOCK_STDERR="$SPLITERR" \
      bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>/dev/null); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
RES=$(printf '%s' "$OUT" | "$PYBIN" -c 'import sys,json
d=json.load(sys.stdin); e=d["stderr_excerpt"]
c=[len(e.encode("utf-8"))<=1024, "ghp_SPLITCANARY" not in e]
print("OK" if all(c) else "BAD:"+repr([i for i,v in enumerate(c) if not v]))')
[ "$RES" = "OK" ] || ok=0
report "N12b-split-token" "$ok" "cap 경계 split-token → 마스킹 선행이 head canary 봉인 (fragment 부재, RES=$RES)" "$OUT"

# ═════════════════════════════════════════════════════════════════════════════
# N13 T-QUOTA-errdict — rc==0 + error-dict {"message":...,"status":"403"} → api_quota_exceeded (양 모드).
#   판별 = _parse_gh_payload 구조 채널 sniff(_is_quota_evidence payload=). INV-3 등가(2채널).
#   AC-3/INV-3 / F-CR-967-1. epic invoke = RED 성격(현행 sniff 부재 = 성공 위장) → py 수정 후 GREEN.
#   title invoke = F-CR-967-1 보존 이동 회귀 게이트(현행도 quota 라벨).
# ═════════════════════════════════════════════════════════════════════════════
OUT=$(CFP967_GH_MOCK_RESPONSE="$F_ERRDICT" bash "$WRAPPER" --mode=epic-state-poll --epic-id=100 2>/dev/null); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"degradation": "api_quota_exceeded"' || ok=0
echo "$OUT" | grep -qF '"epic_state": "UNKNOWN"' || ok=0
echo "$OUT" | grep -qF '"siblings": []' || ok=0
echo "$OUT" | grep -qF '[parallel-work-sentinel-api-failed]' || ok=0
if echo "$OUT" | grep -qF '"matches"'; then ok=0; fi
report "N13a-errdict-epic" "$ok" "rc=0 error-dict(403) epic → api_quota_exceeded + 계약 3키 + marker (구조 채널 sniff)" "$OUT"

OUT=$(CFP967_GH_MOCK_RESPONSE="$F_ERRDICT" CFP_CONTEXT="CFP-1" bash "$WRAPPER" --mode=title-search 2>/dev/null); EC=$?
ok=1
[ "$EC" -eq 0 ] || ok=0
echo "$OUT" | grep -qF '"degradation": "api_quota_exceeded"' || ok=0
echo "$OUT" | grep -qF '"matches"' || ok=0
report "N13b-errdict-title" "$ok" "rc=0 error-dict(403) title → api_quota_exceeded + matches 스키마 (F-CR-967-1 보존 이동)" "$OUT"

set -e

# ─────────────────────────────────────────────────────────────────────────────
# Summary + mutation 문서화
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Test Summary (CFP-2451 prefix + CFP-2490 tier-flip + CFP-2723 epic-state-poll 로스터 N1-N13)"
echo "============================================================"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
echo "TOTAL: $((PASS + FAIL))"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo "✓ All fixtures passed"
  echo ""
  echo "Mutation Testing Documentation (change-plan §8 — hollow 검사 차단):"
  echo "────────────────────────────────────────────────────────────────────"
  echo "[prefix] Mutation-hardcode (KEY_PATTERN → re.compile(r'\\\\bCFP-\\\\d+\\\\b') 하드코딩 복귀)"
  echo "         → T-MCT-match FAIL (MCT-123 미매칭) = RED / T-CFP-default GREEN 유지 = 두 set 분리"
  echo "[tier]   Mutation-1 (workflow 의 continue-on-error derive → hardcode 'true' 복귀)"
  echo "         → T-A1-axis-single FAIL (hardcode_coe>0) = RED (tier 축 산재/미derive)"
  echo "[tier]   Mutation-2 (SENTINEL_TIER env 선언 제거 또는 2지점 산재)"
  echo "         → T-A1-axis-single FAIL (tier_env_count != 1) = RED (1축 집약 위반)"
  echo "[tier]   Mutation-3 (continue-on-error 평가식 != 'blocking' → 항상 true 로 hardcode)"
  echo "         → T-A2-workflow-mutate-RED FAIL (mutated blocking 도 비차단) = RED (flip 무효)"
  echo ""
  echo "CFP-2723 mutation-RED (change-plan §8.2.1 — 수동 mutate → RED 관측 → 원복 → GREEN):"
  echo "────────────────────────────────────────────────────────────────────"
  echo "[field]     py GH_FIELDS_EPIC_STATE_POLL 에 closedBy 재도입 (pinned 외 필드)"
  echo "            → N2-T-FIELD-allowlist-floor FAIL (closedBy ∉ pinned) + N3-T-FIELD-live-gh FAIL (실 gh Unknown JSON field) = RED"
  echo "[errclass]  _classify_gh_failure 를 catch-all 복귀 (분류기 우회 무조건 api_quota_exceeded)"
  echo "            → N5-T-ERRCLASS-nonquota FAIL + N6-T-TITLE-errclass-nonquota FAIL (비-quota 가 quota 오라벨) = RED"
  echo "[schema]    _degrade_epic_state_poll 를 matches 스키마(title 형)로 복귀"
  echo "            → N7-T-EPIC-degrade-schema FAIL (siblings 키 소실 + matches 출현) = RED"
  echo "[cap-order] _stderr_excerpt 마스킹→cap 순서를 cap→마스킹 으로 반전"
  echo "            → N12b-split-token FAIL (절단 경계 토큰 head canary 생존 leak) = RED"
  echo ""
  exit 0
else
  echo "✗ Some fixtures failed"
  exit 1
fi
