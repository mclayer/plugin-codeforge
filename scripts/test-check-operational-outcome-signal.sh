#!/usr/bin/env bash
# CFP-2361 PS4 (신설) / CFP-2613 G2 — Discriminating self-test for check-operational-outcome-signal.sh
#
# 표면 A (선언 fail-closed) execution-liveness L3 (ADR-148 §결정4, ADR-136 결정14):
#   L3 self-tested = 정상→PASS / 위반→FAIL + 가드 mutation→RED (mutation-kill).
#
# 두 축:
#   (1) GREEN 축 — 실 스크립트가 fixture 를 정확히 분류 (blocking exit-code + marker).
#   (2) mutation-kill 축 — 가드를 무력화한 mutant 스크립트에서 위반 fixture 가 통과하면
#       (mutation 생존) = hollow-gate → self-test FAIL. mutant 에서 suite 가 깨져야(RED) 정상.
#
# 9-시나리오 매핑 중 표면 A 담당 (soak-runner 축 = test-soak-verdict-kernel.sh):
#   #6 daemon_type/sink_probes 미선언 FAIL · #7 fake-source FAIL · #9 hard-claim FAIL
#   + daemon_type 스코핑(long_running_daemon blocking vs request_response_service warning).
#
# Exit code: 0 (all pass — GREEN suite + 모든 mutation killed) / 1 (any fail).
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_SRC="$REPO_ROOT/scripts/check-operational-outcome-signal.sh"

PASS=0
FAIL=0
ok()  { echo "✓ PASS: $1"; PASS=$((PASS+1)); }
bad() { echo "✗ FAIL: $1"; echo "    $2"; FAIL=$((FAIL+1)); }

# ── fixture 정의 (name | expected_exit | story_content) ───────────────────────
# expected_exit: 1 = blocking FAIL 기대 / 0 = PASS(비적용/완비) 기대.
fixture() {
  local name="$1"
  case "$name" in
    daemon_type_missing)  cat <<'EOF'
---
operational: true
---
# daemon Story (daemon_type 미선언)
EOF
      ;;
    lrd_incomplete)  cat <<'EOF'
---
operational: true
---
daemon_type: long_running_daemon
(선언 대부분 누락 — outcome-signal / liveness 판정 유형 부재)
EOF
      ;;
    lrd_complete)  cat <<'EOF'
---
operational: true
---
daemon_type: long_running_daemon
terminal downstream sink: object-store parts
monotone progress metric: written parts count
발현조건 임계: >= 8 MiB/shard
sink_probes:
  - name: parts
    probe_type: sink-advance
soak = "완전 봉인" 아님 (증명 불가 정직 구분, honest_ceiling_ack)
EOF
      ;;
    lrd_sinkprobes_only)  cat <<'EOF'
---
operational: true
---
daemon_type: long_running_daemon
terminal downstream sink: object-store parts
monotone progress metric: written parts count
발현조건 임계: >= 8 MiB/shard
(liveness 판정 유형 목록만 누락 — 나머지 완비, 봉인 아님/증명 불가)
EOF
      ;;
    lrd_fake_source)  cat <<'EOF'
---
operational: true
---
daemon_type: long_running_daemon
terminal downstream sink: x
monotone progress metric: x
발현조건 임계: x
sink_probes: [x]
smoke: MCTRADER_SOURCE=fake
EOF
      ;;
    lrd_hardclaim_noack)  cat <<'EOF'
---
operational: true
---
daemon_type: long_running_daemon
terminal downstream sink: x
monotone progress metric: x
발현조건 임계: x
sink_probes: [x]
본 게이트는 모든 크래시 모드를 완전 봉인 한다.
EOF
      ;;
    lrd_hardclaim_withack)  cat <<'EOF'
---
operational: true
---
daemon_type: long_running_daemon
terminal downstream sink: x
monotone progress metric: x
발현조건 임계: x
sink_probes: [x]
soak PASS 는 완전 봉인 아님 — 무한 미래는 증명 불가 (정직 천장).
EOF
      ;;
    rrs_scoping)  cat <<'EOF'
---
operational: true
---
daemon_type: request_response_service
(HTTP 서비스 — 신규 blocking 미적용, warning 만)
EOF
      ;;
    non_operational)  cat <<'EOF'
---
title: 일반 Story
---
operational 요구 없음
EOF
      ;;
  esac
}

# name -> 기대 exit
declare -A EXPECT=(
  [daemon_type_missing]=1
  [lrd_incomplete]=1
  [lrd_sinkprobes_only]=1
  [lrd_fake_source]=1
  [lrd_hardclaim_noack]=1
  [lrd_complete]=0
  [lrd_hardclaim_withack]=0
  [rrs_scoping]=0
  [non_operational]=0
)
FIXTURE_NAMES="daemon_type_missing lrd_incomplete lrd_sinkprobes_only lrd_fake_source lrd_hardclaim_noack lrd_complete lrd_hardclaim_withack rrs_scoping non_operational"

# run_suite <script_path> <label>: 모든 fixture 를 script 로 검사, 기대 exit 와 대조.
# return 0 = suite 전원 기대 일치 / 1 = 하나라도 불일치.
run_suite() {
  local script="$1" label="$2"
  local suite_ok=0
  local tmp; tmp=$(mktemp -d)
  mkdir -p "$tmp/docs/stories" "$tmp/scripts"
  cp "$script" "$tmp/scripts/check-operational-outcome-signal.sh"
  local n exp ec
  for n in $FIXTURE_NAMES; do
    exp="${EXPECT[$n]}"
    fixture "$n" > "$tmp/docs/stories/TEST.md"
    ec=0
    ( cd "$tmp" && bash scripts/check-operational-outcome-signal.sh >/dev/null 2>&1 ) || ec=$?
    if [ "$ec" -ne "$exp" ]; then
      [ "$label" = "GREEN" ] && bad "GREEN suite: fixture '$n' expected exit=$exp got exit=$ec" ""
      suite_ok=1
    fi
  done
  rm -rf "$tmp"
  return $suite_ok
}

echo "============================================"
echo " 표면 A self-test (execution-liveness L3)"
echo "============================================"

# ── 축 1: GREEN — 실 스크립트가 전 fixture 정확 분류 ──
if run_suite "$SCRIPT_SRC" "GREEN"; then
  ok "GREEN suite — 실 스크립트가 8 fixture 전원 기대 exit 일치 (daemon_type 스코핑 + 미선언/fake-source/hard-claim fail-closed)"
else
  bad "GREEN suite — 실 스크립트 분류 불일치" "(위 라인 참조)"
fi

# ── 축 2: mutation-kill — 가드 무력화 mutant 에서 위반 fixture 가 통과하면 hollow ──
# 각 mutation 은 특정 blocking 가드를 죽인다. suite 가 mutant 에서 깨져야(RED) mutation killed.
mutation_kill() {
  local mname="$1" sed_expr="$2"
  local mut; mut=$(mktemp)
  sed -E "$sed_expr" "$SCRIPT_SRC" > "$mut"
  if run_suite "$mut" "MUTANT:$mname" ; then
    # suite 가 mutant 에서도 전원 통과 = mutation 생존 = hollow-gate.
    bad "mutation SURVIVED: $mname (가드가 load-bearing 아님 — hollow)" "mutant suite 가 깨지지 않음"
  else
    ok "mutation killed: $mname (mutant 에서 suite RED — 가드 load-bearing 실증)"
  fi
  rm -f "$mut"
}

# M1: daemon_type presence 가드 무력화 → daemon_type_missing 이 exit 0 로 새어나감.
mutation_kill "daemon_type-presence 무력화" \
  's/if \[ -z "\$daemon_type" \]; then/if false; then/'

# M2: sink_probes 가드 무력화 → lrd_incomplete 의 sink_probes error 소실 (여전히 3요소로 FAIL 유지되나
#     아래 M4 와 결합해 개별 가드 load-bearing 확인). sink_probes grep 을 항상-존재로 치환.
mutation_kill "sink_probes-presence 무력화" \
  's/if ! grep -q "sink_probes"/if false \&\& ! grep -q "sink_probes"/'

# M3: fake-source 가드 무력화 → lrd_fake_source 가 exit 0 로 통과.
mutation_kill "fake-source 가드 무력화" \
  's/if \[ -n "\$fake_hit" \]; then/if false; then/'

# M4: honest-ceiling(완전 봉인) 가드 무력화 → lrd_hardclaim_noack 가 통과.
mutation_kill "honest-ceiling 가드 무력화" \
  "s/if grep -qE '완전 봉인' /if false \&\& grep -qE '완전 봉인' /"

# M5: blocking exit 무력화 (exit 1 → exit 0) → 모든 위반 fixture 가 exit 0.
mutation_kill "blocking exit(1→0) 무력화" \
  's/exit 1$/exit 0/'

echo ""
echo "============================================"
echo "Total: PASS=$PASS FAIL=$FAIL"
echo "============================================"
if [ "$FAIL" -eq 0 ]; then
  echo "All tests passed (GREEN suite + 모든 mutation killed — 표면 A discriminating 실증)"
  exit 0
else
  echo "Some tests failed (표면 A lint hollow 또는 분류 오류)"
  exit 1
fi
