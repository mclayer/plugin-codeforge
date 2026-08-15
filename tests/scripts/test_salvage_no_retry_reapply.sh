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
#   대기(재시도 없는 sleep)는 마커로 안 잡히므로 **경과시간 상대 대조** leg 를 따로 둔다.
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
# assert_attempts: 실패 경로 / 성공 경로 각각 시도 마커가 **정확히 1** 이어야 한다.
# ─────────────────────────────────────────────────────────────────────────────
assert_attempts() {
  local name="$1" want="$2"
  shift 2
  local out n
  out=$(bash "$WRAPPER" "$@" 2>&1) || true
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

# assert_kill_wait: **상대** 경과시간 대조 — 절대 임계는 느린 러너에서 flake 라 쓰지 않는다.
#   killed ⟺ mutant 경과 − baseline 경과 ≥ 2500ms (주입 대기 5.0s 대비 2× 여유).
assert_kill_wait() {
  local label="$1" old="$2" new="$3"
  local m="$TMP/mutant_$((RANDOM)).py" s e bms mms
  if ! make_mutant "$m" "$old" "$new" 2>"$TMP/anchor.err"; then
    echo "X FAIL: $label — ANCHOR-DRIFT: $(cat "$TMP/anchor.err")"
    FAIL=$((FAIL + 1))
    return
  fi
  s=$(date +%s%N)
  bash "$WRAPPER" "${FAIL_ARGS[@]}" >/dev/null 2>&1 || true
  e=$(date +%s%N)
  bms=$(((e - s) / 1000000))
  s=$(date +%s%N)
  python3 "$m" "${FAIL_ARGS[@]}" >/dev/null 2>&1 || true
  e=$(date +%s%N)
  mms=$(((e - s) / 1000000))
  if [ $((mms - bms)) -ge 2500 ]; then
    echo "OK KILLED: $label (baseline ${bms}ms → mutant ${mms}ms, Δ=$((mms - bms))ms)"
    PASS=$((PASS + 1))
  else
    echo "X SURVIVED: $label — Δ=$((mms - bms))ms (want ≥2500ms; baseline ${bms}ms mutant ${mms}ms)"
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

assert_kill_wait "AC-33 ④추가 (재시도 없이 **대기만** 주입 — 마커로는 안 잡히는 축)" \
  '    except OSError as exc:' \
  '    except OSError as exc:
        time.sleep(5.0)'

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
