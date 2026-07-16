#!/usr/bin/env bash
# test-check-no-superpowers.sh — CFP-2704 Phase 2 self-test (§8.1 AC-1~8 + §5.3 P2 pin)
#
# spec = Change Plan §8 (authoritative Test Contract). 대상 gate =
#   scripts/check-no-superpowers.sh (status-aware lib 위임 포함). 각 케이스는
#   실 gate 를 SCAN_ROOT sandbox 로 실행하고 exit code + 출력 substring 2축을
#   관측한다 (presence-grep 단독 금지 — exit code 반드시 캡처해 판정).
#
# ── AC ↔ 케이스 매핑 (§8.1) ──────────────────────────────────────────────────
#   AC-1 : test_live_adr_new_token_detected(pos) / test_live_adr_baseline_only_no_new_violation(neg)
#   AC-2 : test_retired_adr_exempt(neg) / test_retired_flip_to_live_detected(pos)
#   AC-3 : test_current_corpus_delta_zero(neg)                     [실 archive/adr cp -r 미러]
#   AC-4 : test_slash_path_no_false_positive(neg) / test_colon_token_detected(pos)
#   AC-5 : test_swap_count_invariant_detected(pos) / test_baseline_append_shrink_only_fail(pos)
#   AC-6 : test_status_variants_normalized(matrix) / test_absent_status_fail_closed(pos)
#   AC-7 : test_selftest_suite_bidirectional(meta)
#   AC-8 : test_charter_adr122_no_self_flag(neg) / test_charter_new_token_detected(pos)
#   P2   : test_active_status_positive_pin(pos) / test_warning_tier_exit_one_pin(pos)
#   음성대조 2겹(§8.3 c) : test_negcontrol_knownbad_caught(pos)
#   F-CLA-001 회귀 : test_nonutf8_adr_read_failclosed_not_silent_drop(pos, 비-UTF8 read-guard)
#
# ── false-oracle 회피(§8.3 b) ────────────────────────────────────────────────
#   두 "OK" 메시지를 특정 문구로 구분한다. `grep -q "OK"` 절대 금지:
#     HITS 0        → "라이브 superpowers: 호출 없음 (OK)"    (substring: "호출 없음")
#     잔존 위반 0   → "라이브 호출은 EXEMPT 영역에만 존재 (OK)" (substring: "EXEMPT 영역에만")
#     잔존 위반 有  → "⚠ superpowers-allow warning ..."       (substring: "warning")
#
# ── tautology 회피(§8.3 c) ───────────────────────────────────────────────────
#   REFERENCE_MAX 13-signature 는 본 self-test 에 독립 타이핑(lib 미참조).
#   현 baseline 은 lib import 로 추출 → REFERENCE_MAX 대비 ⊆(shrink-only) assert.
#   subset/discrimination 판정은 순수 python 내부 수행(Windows CRLF landmine 우회).
#
# ── 정직 서술(§8.3 d, honest ceiling) ────────────────────────────────────────
#   본 스위트는 grandfather-밖 신규 signature 재유입을 검출한다. 역사서술(prose)
#   FP 는 warning tier residual 로 수용한다. "100% 검출"/"universal 완전봉인" 아님.
#
# ── exit-masking / mock-seam 회피(ADR-060 Amd22) ─────────────────────────────
#   모든 gate 호출은 redirect-capture(GATE_OUT=$(...))로 출력을, 직후 GATE_EC=$?
#   로 exit code 를 캡처해 if/카운터로 판정한다. bare `cmd || true` 미사용.
#   SCAN_ROOT 는 mock 이 아니라 실 gate 대상 fixture sandbox override 이며, 주입
#   경로마다 gate 동작을 exit+출력 assertion 으로 검증한다.
set -uo pipefail

SANDBOX=$(mktemp -d)
trap 'rm -rf "$SANDBOX"' EXIT

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_PATH="$REPO_ROOT/scripts/check-no-superpowers.sh"
LIBDIR="$REPO_ROOT/scripts/lib"

if [[ ! -x "$SCRIPT_PATH" ]]; then
  echo "✗ FATAL: gate 미발견 또는 비실행: $SCRIPT_PATH"
  exit 2
fi

# ── tally / 판정 인프라 ──────────────────────────────────────────────────────
TEST_TOTAL=0
TEST_PASS=0
FAILED_CASES=""
POS_TOTAL=0; POS_OK=0
NEG_TOTAL=0; NEG_OK=0

record_result() { # $1=casename $2=ok(true|false)
  TEST_TOTAL=$((TEST_TOTAL + 1))
  if [[ "$2" == true ]]; then
    TEST_PASS=$((TEST_PASS + 1))
    echo "  ✓ PASS: $1"
  else
    FAILED_CASES="${FAILED_CASES}${FAILED_CASES:+, }$1"
    echo "  ✗ FAIL: $1"
  fi
}

mark_pos() { POS_TOTAL=$((POS_TOTAL + 1)); [[ "$1" -ne 0 ]] && POS_OK=$((POS_OK + 1)); return 0; }
mark_neg() { NEG_TOTAL=$((NEG_TOTAL + 1)); [[ "$1" -eq 0 ]] && NEG_OK=$((NEG_OK + 1)); return 0; }

GATE_OUT=""
GATE_EC=0
run_gate() { # $1=scan_root ; 출력→GATE_OUT, exit→GATE_EC (redirect-capture 예외)
  GATE_OUT=$(SCAN_ROOT="$1" bash "$SCRIPT_PATH" 2>&1)
  GATE_EC=$?
}

has()  { printf '%s' "$GATE_OUT" | grep -qF -- "$1"; }   # 고정 문자열 substring
nhas() { ! printf '%s' "$GATE_OUT" | grep -qF -- "$1"; } # 미포함

# ── 공통 상수 ────────────────────────────────────────────────────────────────
NEW_TOKEN="superpowers:executing-plans"        # baseline-밖 신규 signature (violation 유발)
MSG_NO_HITS="호출 없음"                          # HITS 0 메시지 구분자
MSG_EXEMPT_ONLY="EXEMPT 영역에만"                # 잔존 위반 0 메시지 구분자
MSG_WARNING="warning"                           # 잔존 위반 有 메시지 구분자
ADR073_REL="archive/adr/ADR-073-orchestrator-verify-before-assert.md"
ADR122_REL="archive/adr/ADR-122-superpowers-dependency-removal.md"

mkfix_dir() { local d="$SANDBOX/$1/archive/adr"; mkdir -p "$d"; printf '%s' "$SANDBOX/$1"; }

# ─────────────────────────────────────────────────────────────────────────────
# AC-1 — live ADR 신규토큰 검출 / baseline-only 무위반
# ─────────────────────────────────────────────────────────────────────────────
test_live_adr_new_token_detected() {           # pos
  local root; root=$(mkfix_dir ac1p)
  cat > "$root/$ADR073_REL" <<'ADREOF'
---
adr_number: 73
status: Accepted
---
baseline grandfather: superpowers:writing-plans superpowers:subagent-driven-development
신규 재유입: superpowers:executing-plans
ADREOF
  run_gate "$root"
  local ok=true
  [[ "$GATE_EC" -ne 0 ]] || ok=false                 # exit≠0
  has "ADR-073" || ok=false                            # 경로 substring
  has "$NEW_TOKEN" || ok=false                         # 토큰 substring
  has "$MSG_WARNING" || ok=false
  mark_pos "$GATE_EC"
  record_result "test_live_adr_new_token_detected (pos, exit=$GATE_EC)" "$ok"
}

test_live_adr_baseline_only_no_new_violation() { # neg
  local root; root=$(mkfix_dir ac1n)
  cat > "$root/$ADR073_REL" <<'ADREOF'
---
adr_number: 73
status: Accepted
---
오직 baseline 토큰: superpowers:writing-plans superpowers:subagent-driven-development
ADREOF
  run_gate "$root"
  local ok=true
  [[ "$GATE_EC" -eq 0 ]] || ok=false                   # exit 0
  has "$MSG_EXEMPT_ONLY" || ok=false                   # HITS 有 → grandfather → "EXEMPT 영역에만"
  nhas "$MSG_NO_HITS" || ok=false                      # "호출 없음" 아님을 구분(false-oracle 회피)
  nhas "$NEW_TOKEN" || ok=false                        # 그 파일發 위반 라인 부재
  mark_neg "$GATE_EC"
  record_result "test_live_adr_baseline_only_no_new_violation (neg, exit=$GATE_EC)" "$ok"
}

# ─────────────────────────────────────────────────────────────────────────────
# AC-2 — retired file-level EXEMPT / status flip→live 검출
# ─────────────────────────────────────────────────────────────────────────────
test_retired_adr_exempt() {                     # neg (retired = 합성 경로 허용)
  local root; root=$(mkfix_dir ac2n)
  cat > "$root/archive/adr/ADR-777-synthetic-retired.md" <<'ADREOF'
---
adr_number: 777
status: Superseded by ADR-999
---
retired 이력 문서가 superpowers:executing-plans 를 과거에 사용했다.
ADREOF
  run_gate "$root"
  local ok=true
  [[ "$GATE_EC" -eq 0 ]] || ok=false                   # exit 0 (retired EXEMPT)
  has "$MSG_EXEMPT_ONLY" || ok=false
  nhas "$MSG_WARNING" || ok=false
  mark_neg "$GATE_EC"
  record_result "test_retired_adr_exempt (neg, exit=$GATE_EC)" "$ok"
}

test_retired_flip_to_live_detected() {          # pos (동 파일 status→Accepted flip)
  local root; root=$(mkfix_dir ac2p)
  cat > "$root/archive/adr/ADR-777-synthetic-retired.md" <<'ADREOF'
---
adr_number: 777
status: Accepted
---
이제 live 로 flip 되어 superpowers:executing-plans 재유입.
ADREOF
  run_gate "$root"
  local ok=true
  [[ "$GATE_EC" -ne 0 ]] || ok=false                   # exit≠0
  has "$NEW_TOKEN" || ok=false                         # 검출 substring
  has "$MSG_WARNING" || ok=false
  mark_pos "$GATE_EC"
  record_result "test_retired_flip_to_live_detected (pos, exit=$GATE_EC)" "$ok"
}

# ─────────────────────────────────────────────────────────────────────────────
# AC-3 — 현 corpus delta zero (실 archive/adr 전체 미러)
# ─────────────────────────────────────────────────────────────────────────────
test_current_corpus_delta_zero() {              # neg
  local root="$SANDBOX/ac3"
  mkdir -p "$root/archive"
  cp -r "$REPO_ROOT/archive/adr" "$root/archive/"   # 실 corpus mirror (실 13 grandfather 경로)
  run_gate "$root"
  local ok=true
  [[ "$GATE_EC" -eq 0 ]] || ok=false                   # 잔존 위반 0 → exit 0
  has "$MSG_EXEMPT_ONLY" || ok=false                   # HITS 有(실 토큰) → "EXEMPT 영역에만"
  nhas "$MSG_NO_HITS" || ok=false                      # "호출 없음" 아님(HITS 존재) 구분
  nhas "$MSG_WARNING" || ok=false                      # archive/adr 귀속 위반 count==0
  mark_neg "$GATE_EC"
  record_result "test_current_corpus_delta_zero (neg, exit=$GATE_EC)" "$ok"
}

# ─────────────────────────────────────────────────────────────────────────────
# AC-4 — 슬래시 경로 오탐 0 / 콜론 토큰 검출 (두 축 미붕괴)
# ─────────────────────────────────────────────────────────────────────────────
test_slash_path_no_false_positive() {           # neg
  local root="$SANDBOX/ac4n"
  mkdir -p "$root/docs"
  cat > "$root/docs/x.md" <<'DOCEOF'
스펙 위치: docs/superpowers/specs/x.md 는 경로 참조일 뿐 호출이 아니다.
DOCEOF
  run_gate "$root"
  local ok=true
  [[ "$GATE_EC" -eq 0 ]] || ok=false                   # exit 0
  has "$MSG_NO_HITS" || ok=false                       # HITS 0 → "호출 없음"(오탐 0)
  nhas "$MSG_WARNING" || ok=false
  mark_neg "$GATE_EC"
  record_result "test_slash_path_no_false_positive (neg, exit=$GATE_EC)" "$ok"
}

test_colon_token_detected() {                   # pos
  local root="$SANDBOX/ac4p"
  mkdir -p "$root/docs"
  cat > "$root/docs/y.md" <<'DOCEOF'
라이브 호출: superpowers:brainstorming 을 콜론으로 호출한다.
DOCEOF
  run_gate "$root"
  local ok=true
  [[ "$GATE_EC" -ne 0 ]] || ok=false                   # exit≠0 (축 미붕괴)
  has "superpowers:brainstorming" || ok=false
  has "$MSG_WARNING" || ok=false
  mark_pos "$GATE_EC"
  record_result "test_colon_token_detected (pos, exit=$GATE_EC)" "$ok"
}

# ─────────────────────────────────────────────────────────────────────────────
# AC-5 — swap count-invariant 검출 / baseline shrink-only(append 거부)
# ─────────────────────────────────────────────────────────────────────────────
test_swap_count_invariant_detected() {          # pos (baseline 토큰→신규, count 불변)
  local root; root=$(mkfix_dir ac5s)
  cat > "$root/$ADR073_REL" <<'ADREOF'
---
adr_number: 73
status: Accepted
---
유지된 baseline: superpowers:subagent-driven-development
교체 투입 신규(writing-plans→executing-plans, count 불변): superpowers:executing-plans
ADREOF
  run_gate "$root"
  local ok=true
  [[ "$GATE_EC" -ne 0 ]] || ok=false                   # 새 signature 검출 → exit≠0
  has "$NEW_TOKEN" || ok=false
  nhas "superpowers:subagent-driven-development" || ok=false  # 유지 baseline 은 grandfather(위반 미출력)
  mark_pos "$GATE_EC"
  record_result "test_swap_count_invariant_detected (pos, exit=$GATE_EC)" "$ok"
}

test_baseline_append_shrink_only_fail() {       # pos (REFERENCE_MAX 독립 대비 subset+discrimination)
  # 판정 전량 순수 python (Windows CRLF landmine 우회). REFERENCE_MAX = test-local
  # 독립 타이핑(lib 미참조; base 702593e9 census byte-exact). 현 baseline 은 lib import.
  local verdict
  verdict=$(python3 - "$LIBDIR" <<'PYEOF'
import sys
sys.path.insert(0, sys.argv[1])
import check_superpowers_status_aware as m

REFERENCE_MAX = {
    ("archive/adr/ADR-017-skill-override-path-enforcement.md", "superpowers:brainstorming"),
    ("archive/adr/ADR-017-skill-override-path-enforcement.md", "superpowers:writing-plans"),
    ("archive/adr/ADR-027-consumer-adoption-protocol.md", "superpowers:brainstorming"),
    ("archive/adr/ADR-035-codeforge-agent-teams-epic-architecture.md", "superpowers:using-git-worktrees"),
    ("archive/adr/ADR-044-phase-scoped-sequential-team.md", "superpowers:using-git-worktrees"),
    ("archive/adr/ADR-064-decision-principle-mandate.md", "superpowers:brainstorming"),
    ("archive/adr/ADR-064-decision-principle-mandate.md", "superpowers:writing-plans"),
    ("archive/adr/ADR-073-orchestrator-verify-before-assert.md", "superpowers:subagent-driven-development"),
    ("archive/adr/ADR-073-orchestrator-verify-before-assert.md", "superpowers:writing-plans"),
    ("archive/adr/ADR-082-write-time-self-write-verification-mandate.md", "superpowers:subagent-driven-development"),
    ("archive/adr/ADR-085-multi-session-collaboration-protocol.md", "superpowers:writing-plans"),
    ("archive/adr/ADR-122-superpowers-dependency-removal.md", "superpowers:brainstorming"),
    ("archive/adr/ADR-122-superpowers-dependency-removal.md", "superpowers:writing-plans"),
}
cur = set(m.FROZEN_SUPERPOWERS_BASELINE)
# known_new = baseline-밖 하드코딩 signature (append 거부 실증용)
known_new = ("archive/adr/ADR-073-orchestrator-verify-before-assert.md", "superpowers:executing-plans")

subset_ok   = cur <= REFERENCE_MAX                       # ① 현 baseline ⊆ REFERENCE_MAX (== 아님)
discrim_ok  = not ((cur | {known_new}) <= REFERENCE_MAX) # ② (baseline ∪ known_new) ⊄ REFERENCE_MAX
outside_ok  = known_new not in REFERENCE_MAX             # known_new 이 실제 baseline-밖

print("SUBSET_OK" if subset_ok else "SUBSET_FAIL")
print("DISCRIM_OK" if discrim_ok else "DISCRIM_FAIL")
print("OUTSIDE_OK" if outside_ok else "OUTSIDE_FAIL")
PYEOF
)
  local pyec=$?
  local ok=true
  [[ "$pyec" -eq 0 ]] || ok=false
  printf '%s' "$verdict" | grep -qF "SUBSET_OK"  || ok=false
  printf '%s' "$verdict" | grep -qF "DISCRIM_OK" || ok=false
  printf '%s' "$verdict" | grep -qF "OUTSIDE_OK" || ok=false
  record_result "test_baseline_append_shrink_only_fail (subset ⊆ / append 거부 실증)" "$ok"
}

# ─────────────────────────────────────────────────────────────────────────────
# AC-6 — status 변종 정규화 matrix / status 부재 fail-closed
# ─────────────────────────────────────────────────────────────────────────────
_variant_case() { # $1=label $2=status_value $3=expect(retired|live)  → sub-result(true/false)
  local label="$1" status_value="$2" expect="$3"
  local root; root=$(mkfix_dir "ac6-$label")
  {
    echo "---"
    echo "status: $status_value"
    echo "---"
    echo "변종 status 검증: superpowers:executing-plans"
  } > "$root/archive/adr/ADR-variant-$label.md"
  run_gate "$root"
  if [[ "$expect" == retired ]]; then
    mark_neg "$GATE_EC"
    if [[ "$GATE_EC" -eq 0 ]] && has "$MSG_EXEMPT_ONLY"; then echo true; else echo false; fi
  else # live
    mark_pos "$GATE_EC"
    if [[ "$GATE_EC" -ne 0 ]] && has "$NEW_TOKEN"; then echo true; else echo false; fi
  fi
}

test_status_variants_normalized() {             # matrix
  local ok=true r
  # retired 변종 → EXEMPT
  r=$(_variant_case "upper-superseded" "SUPERSEDED" retired);          [[ "$r" == true ]] || ok=false
  r=$(_variant_case "superseded-by-suffix" "Superseded by ADR-800" retired); [[ "$r" == true ]] || ok=false
  r=$(_variant_case "deprecated" "deprecated" retired);                [[ "$r" == true ]] || ok=false
  # live 변종 → violation
  r=$(_variant_case "inline-comment" "Accepted # 승인 주석" live);      [[ "$r" == true ]] || ok=false
  r=$(_variant_case "adopted" "Adopted" live);                         [[ "$r" == true ]] || ok=false
  r=$(_variant_case "proposed" "proposed" live);                       [[ "$r" == true ]] || ok=false
  # body-dup 특수: frontmatter Superseded 가 body status 중복 위에서 우선(fence scoping)
  local root; root=$(mkfix_dir ac6-bodydup)
  cat > "$root/archive/adr/ADR-variant-bodydup.md" <<'ADREOF'
---
status: Superseded by ADR-800
---
본문에 status: Accepted 가 중복 등장한다(무시되어야 함).
superpowers:executing-plans
ADREOF
  run_gate "$root"
  mark_neg "$GATE_EC"
  { [[ "$GATE_EC" -eq 0 ]] && has "$MSG_EXEMPT_ONLY"; } || ok=false
  record_result "test_status_variants_normalized (matrix: retired→EXEMPT ∧ live→violation ∧ body-dup)" "$ok"
}

test_absent_status_fail_closed() {              # pos (frontmatter/status 부재)
  local root; root=$(mkfix_dir ac6-absent)
  cat > "$root/archive/adr/ADR-888-nostatus.md" <<'ADREOF'
# ADR-888 frontmatter 부재
status 부재 상태에서 superpowers:executing-plans 재유입.
ADREOF
  run_gate "$root"
  local ok=true
  [[ "$GATE_EC" -ne 0 ]] || ok=false                   # exit≠0
  has "[status-unknown fail-closed scan]" || ok=false  # 진단 substring
  has "$NEW_TOKEN" || ok=false
  mark_pos "$GATE_EC"
  record_result "test_absent_status_fail_closed (pos, exit=$GATE_EC)" "$ok"
}

# ─────────────────────────────────────────────────────────────────────────────
# AC-8 — charter ADR-122 self-flag 0 / charter 신규토큰 검출
# ─────────────────────────────────────────────────────────────────────────────
test_charter_adr122_no_self_flag() {            # neg (실 ADR-122 cp)
  local root; root=$(mkfix_dir ac8n)
  cp "$REPO_ROOT/$ADR122_REL" "$root/$ADR122_REL"   # 실파일 cp (brainstorming·writing-plans = baseline 12·13)
  run_gate "$root"
  local ok=true
  [[ "$GATE_EC" -eq 0 ]] || ok=false                   # self-flag 0 → exit 0
  has "$MSG_EXEMPT_ONLY" || ok=false
  nhas "$MSG_WARNING" || ok=false
  mark_neg "$GATE_EC"
  record_result "test_charter_adr122_no_self_flag (neg, exit=$GATE_EC)" "$ok"
}

test_charter_new_token_detected() {             # pos
  local root; root=$(mkfix_dir ac8p)
  cp "$REPO_ROOT/$ADR122_REL" "$root/$ADR122_REL"
  printf '\n라이브 재유입: %s\n' "$NEW_TOKEN" >> "$root/$ADR122_REL"
  run_gate "$root"
  local ok=true
  [[ "$GATE_EC" -ne 0 ]] || ok=false                   # exit≠0
  has "$NEW_TOKEN" || ok=false
  has "ADR-122" || ok=false
  mark_pos "$GATE_EC"
  record_result "test_charter_new_token_detected (pos, exit=$GATE_EC)" "$ok"
}

# ─────────────────────────────────────────────────────────────────────────────
# §5.3 P2 pin
# ─────────────────────────────────────────────────────────────────────────────
test_active_status_positive_pin() {             # pos (Active = live positive-pin, fail-closed default 미의존 실증)
  local root; root=$(mkfix_dir p2active)
  cat > "$root/archive/adr/ADR-892-active.md" <<'ADREOF'
---
status: Active
---
superpowers:executing-plans
ADREOF
  run_gate "$root"
  local ok=true
  [[ "$GATE_EC" -ne 0 ]] || ok=false                   # Active(명시 live) → violation
  has "$NEW_TOKEN" || ok=false
  nhas "[status-unknown fail-closed scan]" || ok=false # unknown fail-closed 경로 아님(live 경로로 검출) 구분
  mark_pos "$GATE_EC"
  record_result "test_active_status_positive_pin (pos, exit=$GATE_EC)" "$ok"
}

test_warning_tier_exit_one_pin() {              # pos (잔존 위반 fixture → exit==1 정확 pin)
  local root; root=$(mkfix_dir p2warn)
  mkdir -p "$root/docs"
  cat > "$root/docs/live.md" <<'DOCEOF'
잔존 위반: superpowers:brainstorming
DOCEOF
  run_gate "$root"
  local ok=true
  [[ "$GATE_EC" -eq 1 ]] || ok=false                   # warning tier = exit 정확히 1
  has "$MSG_WARNING" || ok=false
  mark_pos "$GATE_EC"
  record_result "test_warning_tier_exit_one_pin (pos, exit=$GATE_EC)" "$ok"
}

# ─────────────────────────────────────────────────────────────────────────────
# 음성대조 2겹(§8.3 c) — known-bad 가 실 gate 위반을 catch (① 토큰 substring ② exit≠0)
# ─────────────────────────────────────────────────────────────────────────────
test_negcontrol_knownbad_caught() {             # pos
  local root; root=$(mkfix_dir negctl)
  # known_new 을 실 live baseline 경로(ADR-073, Accepted)에 주입
  cat > "$root/$ADR073_REL" <<'ADREOF'
---
adr_number: 73
status: Accepted
---
known-bad 주입: superpowers:executing-plans
ADREOF
  run_gate "$root"
  local ok=true
  has "$NEW_TOKEN" || ok=false                         # ① 위반 출력에 known_new 토큰 substring 등장
  [[ "$GATE_EC" -ne 0 ]] || ok=false                   # ② 동 주입 시 exit≠0
  mark_pos "$GATE_EC"
  record_result "test_negcontrol_knownbad_caught (음성대조 2겹, exit=$GATE_EC)" "$ok"
}

# ─────────────────────────────────────────────────────────────────────────────
# F-CLA-001 회귀(구현리뷰 dual-peer) — 비-UTF8 바이트 archive/adr 파일의 read 예외가
#   침묵 드롭 아닌 fail-closed 검출로 유입되는지 (parse_status file-read 무가드 봉합 실증).
#   RED(정정 전): read_text UnicodeDecodeError → __main__ crash → python non-zero exit →
#     위반 미surface(traceback 누출, 토큰·진단 부재). GREEN(정정 후): read 예외 → None →
#     unknown → DT-6 fail-closed scan → 토큰 검출 + 진단, python exit 0(모듈 계약 복원).
#   비-UTF8 바이트(\xff\xfe)는 토큰과 다른 라인에 배치 → grep 은 clean 토큰 라인만 emit
#   (python stdin decode 무접촉); parse_status 의 전체 파일 read 만 예외 유발(F-CLA-001 정확 타겟).
# ─────────────────────────────────────────────────────────────────────────────
test_nonutf8_adr_read_failclosed_not_silent_drop() {   # pos (F-CLA-001 봉합)
  local root; root=$(mkfix_dir fcla001)
  {
    printf -- '---\n'
    printf 'adr_number: 999\n'
    printf 'status: Accepted\n'
    printf -- '---\n'
    printf 'invalid utf8 byte here: \xff\xfe end-of-line\n'
    printf 'live reintro token: %s\n' "$NEW_TOKEN"
  } > "$root/archive/adr/ADR-999-nonutf8.md"
  run_gate "$root"
  local ok=true
  [[ "$GATE_EC" -ne 0 ]] || ok=false                        # 침묵 드롭 아님 → 비-0 exit
  has "$NEW_TOKEN" || ok=false                               # 토큰 검출(정정 전=traceback, 토큰 부재)
  has "[status-unknown fail-closed scan]" || ok=false        # read실패 → unknown → DT-6 fail-closed 경로
  nhas "Traceback" || ok=false                               # python crash 누출 없음(graceful)
  nhas "UnicodeDecodeError" || ok=false                      # 동
  mark_pos "$GATE_EC"
  record_result "test_nonutf8_adr_read_failclosed_not_silent_drop (pos, F-CLA-001, exit=$GATE_EC)" "$ok"
}

# ─────────────────────────────────────────────────────────────────────────────
# AC-7 — 스위트 양방향(meta): 각 pos→위반검출 ∧ 각 neg→정상 (집계 후행)
# ─────────────────────────────────────────────────────────────────────────────
test_selftest_suite_bidirectional() {           # meta (모든 gate 케이스 실행 후 마지막)
  local ok=true
  [[ "$POS_TOTAL" -ge 1 ]] || ok=false
  [[ "$NEG_TOTAL" -ge 1 ]] || ok=false
  [[ "$POS_OK" -eq "$POS_TOTAL" ]] || ok=false          # 모든 pos → exit≠0
  [[ "$NEG_OK" -eq "$NEG_TOTAL" ]] || ok=false          # 모든 neg → exit 0
  record_result "test_selftest_suite_bidirectional (meta: pos=$POS_OK/$POS_TOTAL neg=$NEG_OK/$NEG_TOTAL)" "$ok"
}

# ── 실행 순서 (bidirectional meta 는 반드시 최후) ────────────────────────────
echo "━━ CFP-2704 superpowers-allow gate self-test (AC-1~8 + P2) ━━"
test_live_adr_new_token_detected
test_live_adr_baseline_only_no_new_violation
test_retired_adr_exempt
test_retired_flip_to_live_detected
test_current_corpus_delta_zero
test_slash_path_no_false_positive
test_colon_token_detected
test_swap_count_invariant_detected
test_baseline_append_shrink_only_fail
test_status_variants_normalized
test_absent_status_fail_closed
test_charter_adr122_no_self_flag
test_charter_new_token_detected
test_active_status_positive_pin
test_warning_tier_exit_one_pin
test_negcontrol_knownbad_caught
test_nonutf8_adr_read_failclosed_not_silent_drop
test_selftest_suite_bidirectional   # meta — 집계 후행

# ── 종합 ─────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "결과: ${TEST_PASS}/${TEST_TOTAL} PASS  (pos ${POS_OK}/${POS_TOTAL} 검출, neg ${NEG_OK}/${NEG_TOTAL} 정상)"
if [[ "$TEST_PASS" -eq "$TEST_TOTAL" ]]; then
  echo "✓ 전 케이스 PASS"
  exit 0
else
  echo "✗ 실패 케이스: ${FAILED_CASES}"
  exit 1
fi
