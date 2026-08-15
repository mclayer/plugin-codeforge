#!/usr/bin/env bash
# tests/scripts/test_salvage_no_retry_reapply.sh
# CFP-2984 Phase 2 (구현 lane) — AC-33 discriminating self-test.
#
# ★ 명명 테스트 심볼 (Change Plan §8.1 RTM): test_salvage_no_retry_reapply
#
# SUT = scripts/check-salvage-bundle.sh --store (scripts/lib/check_salvage_bundle.py)
# 정본: ADR-179 §결정 8 — degrade 사다리 + **재시도 예산 0**.
#   "salvage 경로는 재시도를 발행하지 않는다(예산 0). 복구 절차가 스스로 예산을 곱하면
#    축1 이 축2 를 악화시킨다."  ⊕ §8.2-E INV-T6.
#
# 검사 대상 명제 (AC-33): salvage **자신이 실패**하는 경로에서
#   ① 재시도·대기 정책이 **재적용되지 않고**(적용 건수 0) ② 단일 시도 후 degrade 로 진입한다.
#
# ★ 오라클 관측면 = **선언이 아니라 계산**:
#   시도 마커 `::salvage-store-attempt::` 를 **시도 함수 본문 안에서** emit 하므로,
#   재시도를 어떤 제어 흐름으로 표현하든(직접 재호출 / 대기 루프 / 재귀) 마커가 그 횟수만큼
#   증가한다. 즉 "재시도 0" 을 자기 선언(`retry_budget: 0` 문자열)으로 믿지 않는다.
#   대기(재시도 없는 sleep)는 시도 마커로 안 잡히므로 **`time.sleep` 호출 계수** leg 를 따로 둔다
#   (벽시계 아님 — 아래 assert_kill_sleep 주석의 flake 근인 참조).
#
# INV-T3 순수 픽스처: 네트워크 0 · 실 `~/.claude/**` 0 · 실 git 원격 0 · 쓰기는 mktemp -d 내부만.
#   저장 실패 주입 = `--out` 을 **기존 디렉터리**로 지정(open(...,"w") → OSError). 권한 조작 없음.
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO_ROOT/scripts/check-salvage-bundle.sh"
SSOT_PY="$REPO_ROOT/scripts/lib/check_salvage_bundle.py"
FIX="$REPO_ROOT/tests/fixtures/cfp2984/salvage"

PASS=0
FAIL=0
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/blocked-as-dir"

BUNDLE="$FIX/bundle-valid.json"
FAIL_ARGS=(--store --bundle "$BUNDLE" --out "$TMP/blocked-as-dir")
OK_ARGS=(--store --bundle "$BUNDLE" --out "$TMP/ok.json")

make_mutant() {
  python3 - "$SSOT_PY" "$1" "$2" "$3" <<'PY'
import sys
src, out, old, new = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
s = open(src, encoding="utf-8").read()
n = s.count(old)
if n != 1:
    sys.stderr.write("ANCHOR-DRIFT n=%d old=%r\n" % (n, old))
    sys.exit(3)
open(out, "w", encoding="utf-8", newline="\n").write(s.replace(old, new, 1))
PY
}

count_attempts() {
  printf '%s\n' "$1" | grep -c '::salvage-store-attempt::' || true
}

# ─────────────────────────────────────────────────────────────────────────────
# ★ crash-as-RED 차단 (CFP-2984 G7 감사 — 실사건 회귀 방지)
#   오라클·변이체가 예외로 죽어서 난 rc≠0 / 마커 부재는 **검출이 아니다**.
#   ★ assert_kill_absent 의 kill 판정은 "mutant 출력에 needle 부재" 다 — 크래시한 mutant 는
#     아무것도 못 내므로 **자동으로 killed 로 오독**된다.
#   ★ assert_kill_attempts(시도 ≥2 요구) · assert_kill_sleep(sleep 호출 ≥1 요구) 는 kill 조건이
#     **양(positive) 산출**이라 크래시로는 충족 불가 — 구조적으로 crash-safe.
#     단 assert_kill_sleep 은 baseline 쪽이 `0` 을 요구하므로 baseline 크래시가 조건을 만족시킬
#     수 있다 → 완주 마커 `::probe-complete::` 부재를 양 팔 모두에서 harness FAIL 로 끊는다.
#   ★ SyntaxError·IndentationError 는 Traceback 머리글 없이 출력된다(실측) — 함께 본다.
# ─────────────────────────────────────────────────────────────────────────────
crash_marker() { # <output> → 0 = 크래시 흔적 있음
  case "$1" in
    *Traceback*|*SyntaxError*|*IndentationError*|*TabError*) return 0 ;;
  esac
  return 1
}

fail_crash() {
  echo "X FAIL: $1 — $2 크래시(오라클 예외). rc≠0·마커 부재를 검출로 셀 수 없다"
  printf '%s\n' "$3" | sed 's/^/    ! /'
  FAIL=$((FAIL + 1))
}

# ─────────────────────────────────────────────────────────────────────────────
# assert_attempts: 실패 경로 / 성공 경로 각각 시도 마커가 **정확히 1** 이어야 한다.
# ─────────────────────────────────────────────────────────────────────────────
assert_attempts() {
  local name="$1" want="$2"
  shift 2
  local out n
  out=$(bash "$WRAPPER" "$@" 2>&1) || true
  if crash_marker "$out"; then fail_crash "$name" "SUT" "$out"; return; fi
  n=$(count_attempts "$out")
  if [ "$n" -eq "$want" ]; then
    echo "OK PASS: $name (시도 $n 회)"
    PASS=$((PASS + 1))
  else
    echo "X FAIL: $name — 시도 want=$want got=$n"
    printf '%s\n' "$out" | sed 's/^/    /'
    FAIL=$((FAIL + 1))
  fi
}

assert_contains() {
  local name="$1" needle="$2"
  shift 2
  local out
  out=$(bash "$WRAPPER" "$@" 2>&1) || true
  if crash_marker "$out"; then fail_crash "$name" "SUT" "$out"; return; fi
  case "$out" in
    *"$needle"*)
      echo "OK PASS: $name"
      PASS=$((PASS + 1))
      ;;
    *)
      echo "X FAIL: $name — '$needle' 부재"
      printf '%s\n' "$out" | sed 's/^/    /'
      FAIL=$((FAIL + 1))
      ;;
  esac
}

# assert_kill_attempts: baseline 시도 1 → mutant 시도 ≥2 여야 killed (재시도 유입 검출).
assert_kill_attempts() {
  local label="$1" old="$2" new="$3"
  local m="$TMP/mutant_$((RANDOM)).py" bout mout bn mn
  if ! make_mutant "$m" "$old" "$new" 2>"$TMP/anchor.err"; then
    echo "X FAIL: $label — ANCHOR-DRIFT: $(cat "$TMP/anchor.err")"
    FAIL=$((FAIL + 1))
    return
  fi
  bout=$(bash "$WRAPPER" "${FAIL_ARGS[@]}" 2>&1) || true
  mout=$(python3 "$m" "${FAIL_ARGS[@]}" 2>&1) || true
  bn=$(count_attempts "$bout")
  mn=$(count_attempts "$mout")
  if [ "$bn" -eq 1 ] && [ "$mn" -ge 2 ]; then
    echo "OK KILLED: $label (baseline 시도 $bn 회 → mutant 시도 $mn 회)"
    PASS=$((PASS + 1))
  else
    echo "X SURVIVED: $label — baseline 시도 $bn(want 1) mutant 시도 $mn(want ≥2)"
    echo "    ⇒ AC-33 advisory 강등 대상 (Story :649)"
    FAIL=$((FAIL + 1))
  fi
}

# assert_kill_absent: baseline 에는 있고 mutant 에는 없어야 killed (degrade 기록 소멸 검출).
assert_kill_absent() {
  local label="$1" old="$2" new="$3" needle="$4"
  local m="$TMP/mutant_$((RANDOM)).py" bout mout bhit=0 mhit=0
  if ! make_mutant "$m" "$old" "$new" 2>"$TMP/anchor.err"; then
    echo "X FAIL: $label — ANCHOR-DRIFT: $(cat "$TMP/anchor.err")"
    FAIL=$((FAIL + 1))
    return
  fi
  bout=$(bash "$WRAPPER" "${FAIL_ARGS[@]}" 2>&1) || true
  mout=$(python3 "$m" "${FAIL_ARGS[@]}" 2>&1) || true
  if crash_marker "$bout"; then fail_crash "$label" "baseline(대조군 무효 — INV-T4)" "$bout"; return; fi
  # ★ 크래시한 mutant 는 needle 을 못 내므로 '기록 無' = killed 로 오독된다. 여기서 끊는다.
  if crash_marker "$mout"; then fail_crash "$label" "mutant(치환이 소스를 깨뜨림 = 거짓 kill)" "$mout"; return; fi
  case "$bout" in *"$needle"*) bhit=1 ;; esac
  case "$mout" in *"$needle"*) mhit=1 ;; esac
  if [ "$bhit" -eq 1 ] && [ "$mhit" -eq 0 ]; then
    echo "OK KILLED: $label (baseline 기록 有 → mutant 기록 無)"
    PASS=$((PASS + 1))
  else
    echo "X SURVIVED: $label — baseline hit=$bhit(want 1) mutant hit=$mhit(want 0)"
    echo "    ⇒ AC-33 advisory 강등 대상 (Story :649)"
    FAIL=$((FAIL + 1))
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# ★ '대기' 축 관측면 = **`time.sleep` 호출 계수** (벽시계 아님).
#
#   구 구현(`mutant 경과 − baseline 경과 ≥ 2500ms`)의 flake 근인 2건:
#     (a) **양 팔 스택 비대칭** — baseline `bash "$WRAPPER"`(bash+python 2단) vs
#         mutant `python3 "$m"`(python 단독). "상대 대조" 라면서 두 팔이 다른 스택이었다.
#     (b) **노이즈 대역 ≈ 임계** — 리뷰 실측 Δ=2321(RED)/1999(RED)/4600(GREEN)ms, 임계 2500ms.
#   이 본은 invariant-check.yml 의 required corpus 라 flake 1회 = repo 전체 PR 차단이었다.
#   → 시간축을 버리고 결정론으로 바꾼다. 러너 부하 종속성 0, 실제 대기 0(테스트 5초 단축).
#
#   probe 는 대상 모듈 로드 **전에** `time.sleep` 을 계수 함수로 치환하므로
#   `time.sleep(5.0)` 과 `from time import sleep` 양 표기를 모두 포착한다(둘 다 실측 확인).
#
#   ★ 정직한 천장 — 관측면은 `time.sleep` 호출 **1종**이다. busy-wait 루프 ·
#     `select`/`socket` timeout · 외부 `sleep 5` 프로세스로 표현된 대기는 **미검출**.
#     구 벽시계 오라클은 원리상 그것들도 봤으나 임계에서 판정 불가였다(위 (b)) —
#     "판정 못 하는 넓은 관측면" 을 "판정하는 좁은 관측면" 으로 바꾼 교환임을 명시한다.
# ─────────────────────────────────────────────────────────────────────────────
PROBE="$TMP/sleep_probe.py"
cat >"$PROBE" <<'PY'
import importlib.util
import sys
import time
import traceback

target = sys.argv[1]
argv = sys.argv[2:]

_calls = []
_real_sleep = time.sleep


def _counting_sleep(secs, *a, **k):
    # 실제로 자지 않는다 — 계수만 한다(벽시계 비의존).
    _calls.append(float(secs))
    return None


# ★ 대상 로드 **전에** 치환 → `from time import sleep` 바인딩도 계수 함수를 집는다.
time.sleep = _counting_sleep

try:
    spec = importlib.util.spec_from_file_location("_sut_under_probe", target)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_sut_under_probe"] = mod
    spec.loader.exec_module(mod)
    rc = mod.main(argv)
except SystemExit as e:
    rc = e.code
except BaseException:
    # 완주 마커를 내지 않고 죽는다 — 크래시가 'sleep 0' 으로 오독될 여지를 없앤다.
    traceback.print_exc()
    raise SystemExit(3)
finally:
    time.sleep = _real_sleep

print("::probe-complete:: sleep_calls=%d sleep_total=%.3f rc=%s"
      % (len(_calls), sum(_calls), rc))
PY

probe_sleep_calls() { # <output> → sleep 호출 수. 완주 마커 부재 시 빈 문자열(= 크래시).
  printf '%s\n' "$1" | sed -n 's/.*::probe-complete:: sleep_calls=\([0-9][0-9]*\) .*/\1/p' | tail -1
}

# assert_kill_sleep: baseline sleep 호출 0 → mutant ≥1 이어야 killed.
#   양 팔 모두 동일 스택(`python3 "$PROBE" <target>`) — (a) 비대칭 제거.
assert_kill_sleep() {
  local label="$1" old="$2" new="$3"
  local m="$TMP/mutant_$((RANDOM)).py" bout mout bn mn
  if ! make_mutant "$m" "$old" "$new" 2>"$TMP/anchor.err"; then
    echo "X FAIL: $label — ANCHOR-DRIFT: $(cat "$TMP/anchor.err")"
    FAIL=$((FAIL + 1))
    return
  fi
  bout=$(python3 "$PROBE" "$SSOT_PY" "${FAIL_ARGS[@]}" 2>&1) || true
  mout=$(python3 "$PROBE" "$m" "${FAIL_ARGS[@]}" 2>&1) || true
  bn=$(probe_sleep_calls "$bout")
  mn=$(probe_sleep_calls "$mout")
  if [ -z "$bn" ]; then fail_crash "$label" "baseline(대조군 무효 — INV-T4)" "$bout"; return; fi
  if [ -z "$mn" ]; then fail_crash "$label" "mutant(치환이 소스를 깨뜨림 = 거짓 kill)" "$mout"; return; fi
  if [ "$bn" -eq 0 ] && [ "$mn" -ge 1 ]; then
    echo "OK KILLED: $label (baseline sleep 호출 ${bn}회 → mutant ${mn}회)"
    PASS=$((PASS + 1))
  else
    echo "X SURVIVED: $label — baseline sleep=$bn(want 0) mutant sleep=$mn(want ≥1)"
    echo "    ⇒ AC-33 의 '대기' 축은 advisory 강등 대상 (Story :649)"
    FAIL=$((FAIL + 1))
  fi
}

echo "══ 1. clean-input 대조군 (정상 저장 경로) ══"
assert_attempts "대조군 저장 성공 → 시도 1회"      1 "${OK_ARGS[@]}"
assert_contains "대조군 저장 성공 보고"            "SALVAGE_STORE: PASS" "${OK_ARGS[@]}"

echo "══ 2. AC-33 — 실패 경로: 단일 시도 후 degrade ══"
assert_attempts "저장 실패 → 시도 **1회**(재적용 0)" 1 "${FAIL_ARGS[@]}"
assert_contains "degrade 종점 F3 사고 레코드 산출"   '"degrade": "F3"'  "${FAIL_ARGS[@]}"
assert_contains "재시도 예산 0 기록"                 '"retry_budget": 0' "${FAIL_ARGS[@]}"
assert_contains "실패 경로 종료 보고가 성공 아님"    "SALVAGE_STORE: FAIL (stored=false)" "${FAIL_ARGS[@]}"

echo "══ 3. 3방향 mutant — AC-33 ══"
assert_kill_absent "AC-33 ①제거 (degrade 사고 레코드 경로 삭제)" \
  'print("::salvage-incident:: %s" % json.dumps(record, ensure_ascii=False, sort_keys=True))' \
  'pass' \
  '::salvage-incident::'

assert_kill_attempts "AC-33 ②주입·의미변경 경계 (실패 경로에 backoff 재시도 3회 주입)" \
  '        _store_attempt(out_path, payload)' \
  '        for _attempt in (1, 2, 3):
            try:
                _store_attempt(out_path, payload)
                break
            except OSError:
                if _attempt == 3:
                    raise
                time.sleep(0.01)'

assert_kill_attempts "AC-33 ③등가변형·값 표현 (재시도를 직접 호출 대신 대기 루프로 표현)" \
  '        _store_attempt(out_path, payload)' \
  '        for _spin in range(4):
            try:
                _store_attempt(out_path, payload)
                break
            except OSError:
                time.sleep(0.01)
        else:
            raise OSError("wait-loop exhausted")'

assert_kill_sleep "AC-33 ④주입 (재시도 없이 **대기만** — 시도 마커로는 안 잡히는 축)" \
  '    except OSError as exc:' \
  '    except OSError as exc:
        time.sleep(5.0)'

# ★ ④ 의 등가변형: 같은 대기를 다른 표기로 쓴다. `time.sleep` 속성 조회를 우회하는
#   `from time import sleep` 바인딩에도 관측면이 버티는지 — 오라클 자기 자문(표기 등가변형).
assert_kill_sleep "AC-33 ⑤등가변형 (같은 대기를 from-import 표기로 — 관측면 우회 시도)" \
  '    except OSError as exc:' \
  '    except OSError as exc:
        from time import sleep as _s
        _s(5.0)'

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
