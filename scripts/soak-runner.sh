#!/usr/bin/env bash
# scripts/soak-runner.sh — soak 지속-liveness orchestration vehicle (reference runner)
#
# CFP-2613 (Epic CFP-2602 G2) / ADR-148 §결정3 (orchestration = vehicle-local net-new)
#   + §결정7 (boot-grace 창 · manifestation-derived OR duration floor).
#
# 역할: fixture/real 데몬을 soak 창 동안 구동하며 (a) 프로세스 생존(exit/restart) 관측 +
#   (b) terminal-sink monotone 전진을 verdict-kernel(evaluate_soak_sample)로 판정해
#   구조화된 verdict 를 산출한다. 이 executable = wrapper fixture-daemon self-test(wave 2)가
#   normal/crash/restart/flat-sink/reverse-sink/slow-boot fixture 로 구동하는 대상.
#
# 재사용 경계 (ADR-148 §결정3 F1): sink-monotone 판정 = verdict-kernel 재사용(단일소스).
#   프로세스 생존(exit/restart 카운트) + boot-grace 창 = genuinely net-new layer
#   (재사용할 기존 구현 없음 — 이 vehicle 이 신작). INV-D3 = 생존 ∧ sink-monotone (AND).
#
# hermetic: network 0 · real deps 0 — caller 가 daemon_cmd / sink_metric_cmd 를 주입.
#
# ── 구동 계약 (env, CLI 인자 우선) ────────────────────────────────────────────
#   SOAK_DAEMON_CMD        데몬 기동 명령 (background 실행). 필수.
#   SOAK_SINK_METRIC_CMD   sink 현재값(정수 1개)을 stdout 출력하는 명령. 필수.
#   SOAK_BOOT_GRACE_S      boot-grace 초 — exit/restart 카운트는 이 창 경과 후 시작. 기본 2.
#   SOAK_THRESHOLD         발현조건 임계 (0 = duration_floor fallback 경로). 기본 0.
#   SOAK_DURATION_FLOOR_S  soak 창(deadline horizon) 초. 기본 30.
#   SOAK_POLL_INTERVAL_S   sink poll 간격 초 (fractional 허용). 기본 1.
#   SOAK_MAX_RESTARTS      post-grace death 후 relaunch 상한(폭주 가드). 기본 5.
#
#   CLI: soak-runner.sh [daemon_cmd] [sink_metric_cmd] [boot_grace_s] [threshold] \
#                       [duration_floor_s] [poll_interval_s]
#        (인자 미제공 시 대응 env 사용)
#
# ── 출력 (machine-parseable) ─────────────────────────────────────────────────
#   RESULT survival=<true|false> sink_monotone_progressed=<true|false> \
#          soak_verified=<true|false> reason=<CODE> soak_duration_s=<n> \
#          soak_duration_basis=<manifestation|floor> boot_grace_s=<n>
#
# ── exit code ────────────────────────────────────────────────────────────────
#   0 = soak_verified true / 1 = soak_verified false (soak FAIL) / 2 = config·setup error.
#   (RESULT 라인은 exit 이전 항상 1회 출력 — self-test 는 RESULT 필드 ∧ exit code 로 assert)
# ──────────────────────────────────────────────────────────────────────────────
#
# boot-grace 상한 방어 = self-test mutation 표적 (ADR-148 §결정7 SSOT: ceiling ≤ soak/2):
#   grace 가 soak 창의 절반을 넘으면 post-grace 관측창 < 절반 → 크래시 은폐 소지.
#   정본 규칙 = grace ≤ duration_floor/2 (관측창 ≥ 절반 보장). 위반 = 2*grace ≥ duration_floor.
#   → config error(exit 2)로 fail-closed 차단 (grace 를 밀어 관측창을 좁혀 FAIL 은폐 불가).

set -uo pipefail  # -e 미사용 의도: 프로세스 감독은 non-zero exit 을 정상 관측하므로.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# verdict-kernel single-source (ADR-148 §결정3) — robust relative resolve.
KERNEL_PATH="$SCRIPT_DIR/lib/soak-verdict-kernel.sh"
if [ ! -f "$KERNEL_PATH" ]; then
  echo "soak-runner: verdict-kernel 부재 ($KERNEL_PATH) — single-source 배선 파손" >&2
  echo "RESULT survival=false sink_monotone_progressed=false soak_verified=false reason=SETUP_ERROR soak_duration_s=0 soak_duration_basis=floor boot_grace_s=0"
  exit 2
fi
# shellcheck source=scripts/lib/soak-verdict-kernel.sh
. "$KERNEL_PATH"

# ── config 해석 (CLI 인자 > env > 기본) ──────────────────────────────────────
DAEMON_CMD="${1:-${SOAK_DAEMON_CMD:-}}"
SINK_METRIC_CMD="${2:-${SOAK_SINK_METRIC_CMD:-}}"
BOOT_GRACE_S="${3:-${SOAK_BOOT_GRACE_S:-2}}"
THRESHOLD="${4:-${SOAK_THRESHOLD:-0}}"
DURATION_FLOOR_S="${5:-${SOAK_DURATION_FLOOR_S:-30}}"
POLL_INTERVAL_S="${6:-${SOAK_POLL_INTERVAL_S:-1}}"
MAX_RESTARTS="${SOAK_MAX_RESTARTS:-5}"

emit_result() {
  # $1=survival $2=sink_prog $3=verified $4=reason $5=dur_s $6=basis $7=grace
  echo "RESULT survival=$1 sink_monotone_progressed=$2 soak_verified=$3 reason=$4 soak_duration_s=$5 soak_duration_basis=$6 boot_grace_s=$7"
}

cfg_error() {
  echo "soak-runner: config error — $1" >&2
  emit_result false false false SETUP_ERROR 0 floor "$BOOT_GRACE_S"
  exit 2
}

[ -n "$DAEMON_CMD" ]      || cfg_error "SOAK_DAEMON_CMD (또는 인자1) 미지정"
[ -n "$SINK_METRIC_CMD" ] || cfg_error "SOAK_SINK_METRIC_CMD (또는 인자2) 미지정"

# 정수 검증 (kernel 은 정수 전제) — soak 창/grace/threshold.
case "$BOOT_GRACE_S$THRESHOLD$DURATION_FLOOR_S" in
  *[!0-9]*) cfg_error "boot_grace_s / threshold / duration_floor_s 는 비음 정수여야 함 (grace=$BOOT_GRACE_S threshold=$THRESHOLD floor=$DURATION_FLOOR_S)" ;;
esac
[ "$DURATION_FLOOR_S" -gt 0 ] || cfg_error "duration_floor_s > 0 필요 (deadline horizon)"

# boot-grace 상한 방어 (ADR-148 §결정7 SSOT: ceiling ≤ soak/2). 위반 = 2*grace ≥ floor.
if [ $(( BOOT_GRACE_S * 2 )) -ge "$DURATION_FLOOR_S" ]; then
  cfg_error "boot_grace_s($BOOT_GRACE_S) > duration_floor_s($DURATION_FLOOR_S)/2 — 관측창 < 절반(크래시 은폐 소지). ceiling ≤ soak/2 (ADR-148 §결정7)"
fi

soak_basis() {
  # threshold>0 = manifestation 경로 / threshold==0 = floor 경로.
  if [ "$THRESHOLD" -gt 0 ]; then echo "manifestation"; else echo "floor"; fi
}

# ── 데몬 감독 helpers ────────────────────────────────────────────────────────
DAEMON_PID=""
launch_daemon() {
  # subshell 로 caller 명령 실행 → background PID.
  eval "$DAEMON_CMD" &
  DAEMON_PID=$!
}
daemon_alive() {
  [ -n "$DAEMON_PID" ] && kill -0 "$DAEMON_PID" 2>/dev/null
}
reap_daemon() {
  # 창 종료 시 잔존 데몬 정리 (soak 성공 케이스 = 우리가 종료).
  if daemon_alive; then
    kill "$DAEMON_PID" 2>/dev/null || true
    wait "$DAEMON_PID" 2>/dev/null || true
  fi
}
trap reap_daemon EXIT

sample_sink() {
  # sink_metric 명령의 stdout(정수). 비정수/공백 = 0 취급 (freeze 감지 방향, 안전).
  local out
  out="$(eval "$SINK_METRIC_CMD" 2>/dev/null | tr -dc '0-9')"
  [ -n "$out" ] || out="0"
  echo "$out"
}

# ── soak 창 구동 ─────────────────────────────────────────────────────────────
BASIS="$(soak_basis)"
START="$(date +%s)"
DEADLINE=$(( START + DURATION_FLOOR_S ))

echo "soak-runner: 시작 grace=${BOOT_GRACE_S}s window=${DURATION_FLOOR_S}s threshold=${THRESHOLD} poll=${POLL_INTERVAL_S}s basis=${BASIS}" >&2
launch_daemon
echo "soak-runner: daemon 기동 pid=$DAEMON_PID" >&2

prev=-1
first=-1
reason="CONTINUE"
death_count=0        # post-grace 데몬 death 횟수 (0 = 생존)
last_exit=0

while true; do
  now="$(date +%s)"
  grace_over=0
  [ $(( now - START )) -ge "$BOOT_GRACE_S" ] && grace_over=1

  # (a) 생존 관측: post-grace 데몬 death = restart/crash (survival false).
  if ! daemon_alive; then
    wait "$DAEMON_PID" 2>/dev/null; ec=$?
    if [ "$grace_over" = "1" ]; then
      death_count=$(( death_count + 1 ))
      last_exit=$ec
      echo "soak-runner: post-grace 데몬 death (exit=$ec, death_count=$death_count)" >&2
      if [ "$death_count" -gt "$MAX_RESTARTS" ]; then
        echo "soak-runner: death_count > MAX_RESTARTS($MAX_RESTARTS) — 조기 종료 (survival false 확정)" >&2
        break
      fi
      launch_daemon  # restart 모델 (창 지속 — sink 관측 계속)
    else
      # grace 내 exit = 부팅 시도(slow-boot). 카운트 없이 relaunch (false-FAIL 방지).
      echo "soak-runner: grace 내 데몬 exit (exit=$ec) — 부팅 시도로 취급, relaunch" >&2
      launch_daemon
    fi
  fi

  # (b) sink 판정: verdict-kernel 재사용 (단일소스).
  cur="$(sample_sink)"
  [ "$first" -lt 0 ] && first="$cur"
  deadline_reached=0
  [ "$now" -ge "$DEADLINE" ] && deadline_reached=1

  reason="$(evaluate_soak_sample "$prev" "$cur" "$first" "$THRESHOLD" "$DURATION_FLOOR_S" "$deadline_reached")"
  echo "soak-runner: sink=$cur prev=$prev first=$first deadline_reached=$deadline_reached -> $reason" >&2

  case "$reason" in
    CONTINUE) prev="$cur"; sleep "$POLL_INTERVAL_S" ;;
    *)        break ;;   # 종점 reason-code (PASS_* / FAIL_*)
  esac
done

END="$(date +%s)"
DURATION_S=$(( END - START ))

# ── verdict 종합 (INV-D3: soak_verified = 생존 ∧ sink monotone 전진) ──────────
if [ "$death_count" -eq 0 ]; then survival="true"; else survival="false"; fi

case "$reason" in
  PASS_THRESHOLD|PASS_FLOOR) sink_prog="true" ;;
  *)                         sink_prog="false" ;;   # FAIL_* / CONTINUE(조기종료)
esac

if [ "$survival" = "true" ] && [ "$sink_prog" = "true" ]; then
  soak_verified="true"
else
  soak_verified="false"
fi

emit_result "$survival" "$sink_prog" "$soak_verified" "$reason" "$DURATION_S" "$BASIS" "$BOOT_GRACE_S"

[ "$soak_verified" = "true" ] && exit 0 || exit 1
