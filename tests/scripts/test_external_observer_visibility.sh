#!/usr/bin/env bash
# tests/scripts/test_external_observer_visibility.sh
# CFP-2984 Phase 2 (구현 lane) — AC-29 discriminating self-test.
#
# AC-29: 세션 외부 관측자(branch-liveness-watchdog)가 credential 부재로 dry-run 종료할 때
#   "수집량 0" 사실과 그 "사유"(credential 부재)가 구조화 필드로 가시화되어, 후속 조회가
#   **"관측됨 0"(observed, count=0)** 과 **"미관측"(unobserved)** 을 구별할 수 있어야 한다.
#
# ★ 오라클 정의역 = 실 workflow 파일의 `id: observation` step 의 `run:` 블록을 **YAML 로 추출해
#   실제로 실행**한 산출(record)이다. 문면 presence 검사가 아니다 — 필드가 적혀 있어도 실행
#   결과가 두 시나리오를 구별 못 하면 RED 다.
#
# ★ exit code 무접촉 (ADR-157 §결정 8 accepted-risk 보존): 본 테스트는 emitter 가 전 시나리오에서
#   rc=0 임을 **적극 assert** 한다 — 후일 누가 "secret 부재 → 실패" 로 역전시키면 이 leg 이 RED.
#
# 3방향 mutant (전부 실 파일 변형 적용 — 선언 아님):
#   ① 제거      M1 = 방출 블록에서 `unobserved_reason` 필드 삭제            → C1 RED
#   ② 주입      M2 = dry-run 분기 사유를 `none` 으로 주입 (수집 0 + 사유 누락) → C3 RED
#   ③ 등가변형  M3a/b/c = 사유를 `unknown` / `null` / 빈 문자열 로 표기 변형   → C3 RED
#               (3형태 모두 "미관측·사유 미상" 으로 정규화되어 사유 가시화가 소실됨)
#   ④ 구별 붕괴 M4 = dry-run 분기 state 를 `observed` 로 → 두 시나리오 record 동일 → C4 RED
#
# 대조군(INV-T4): 무변조 정본 workflow 로 dry-run·ok 두 시나리오 실행 → 전 검사 PASS.
#   baseline PASS 없이는 어떤 kill 주장도 성립하지 않는다.
#
# INV-T3 순수 픽스처: 네트워크 0 · 실 ~/.claude/** 0 · 실 git 원격 0 · 쓰기는 mktemp -d 내부만.
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WORKFLOW="$REPO_ROOT/.github/workflows/branch-liveness-watchdog.yml"

PASS=0
FAIL=0

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# ─────────────────────────────────────────────────────────────────────────────
# checker.py — 방출 record 에 대한 4 검사 (C1~C4). 전부 fail-closed.
# ─────────────────────────────────────────────────────────────────────────────
cat > "$WORK/checker.py" <<'PY'
#!/usr/bin/env python3
"""AC-29 가시화 record 검사기 (fail-closed).

C1 필드 전수성   : observation_state / collected_count / unobserved_reason 3필드 전건 존재.
C2 state enum    : observation_state ∈ {observed, unobserved} (vacuous·enum 밖 = RED).
C3 사유 구체성   : state == unobserved ⟹ unobserved_reason 이 **구체 사유**.
                   vacuous 표기 3형태(빈 문자열 / null / unknown 계열) = 사유 미가시 = RED.
C4 구별 가능성   : "관측됨 0" record 와 "미관측" record 가 서로 다른 관측 상태로 해소.
"""
import sys

VACUOUS = {"", "null", "nil", "none-specified", "unspecified", "unknown", "n/a", "na", "-"}
STATE_ENUM = {"observed", "unobserved"}
# state == unobserved 일 때 허용되는 구체 사유 — "왜 관측하지 못했는가" 를 지시해야 한다.
CONCRETE_REASONS = {"credential-absent", "fetch-error", "fetch-status-missing"}


def load(path):
    """key=value 방출 파일 → dict (마지막 값 우선). 파일 부재 = fail-closed."""
    rec = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                rec[k.strip()] = v.strip()
    except OSError as e:
        return None, "record 파일 판독 불가(%s) — fail-closed" % e
    return rec, None


def norm(v):
    return str(v).strip().lower()


def check_record(path, label):
    rec, err = load(path)
    if rec is None:
        return ["[%s] %s" % (label, err)]
    v = []
    # C1
    for k in ("observation_state", "collected_count", "unobserved_reason"):
        if k not in rec:
            v.append("[%s] C1 가시화 필드 `%s` 부재 — 후속 조회가 관측 상태를 판독 불가" % (label, k))
    if v:
        return v
    state = norm(rec["observation_state"])
    reason = norm(rec["unobserved_reason"])
    count = rec["collected_count"].strip()
    # C2
    if state in VACUOUS or state not in STATE_ENUM:
        v.append("[%s] C2 observation_state 값 '%s' 가 enum {observed, unobserved} 밖 (vacuous 포함)"
                 % (label, rec["observation_state"]))
    if not count.isdigit():
        v.append("[%s] C2 collected_count 값 '%s' 가 정수 아님 — 수집량 미해소" % (label, count))
    # C3
    if state == "unobserved":
        if reason in VACUOUS:
            v.append("[%s] C3 미관측인데 사유가 vacuous('%s') — '수집 0 사실' 만 있고 '사유' 가 "
                     "가시화되지 않음" % (label, rec["unobserved_reason"]))
        elif reason not in CONCRETE_REASONS:
            v.append("[%s] C3 미관측 사유 '%s' 가 구체 사유 집합 %s 밖"
                     % (label, rec["unobserved_reason"], sorted(CONCRETE_REASONS)))
    elif state == "observed":
        if reason not in ("none",) and reason not in VACUOUS:
            v.append("[%s] C3 관측됨인데 미관측 사유 '%s' 가 붙음 — 상태 모순"
                     % (label, rec["unobserved_reason"]))
    return v


def check_distinguish(dry_path, ok_path):
    dry, e1 = load(dry_path)
    okr, e2 = load(ok_path)
    if dry is None or okr is None:
        return ["C4 record 판독 불가 — fail-closed (%s / %s)" % (e1, e2)]
    v = []
    ds = norm(dry.get("observation_state", ""))
    os_ = norm(okr.get("observation_state", ""))
    dc = dry.get("collected_count", "").strip()
    oc = okr.get("collected_count", "").strip()
    if dc != "0" or oc != "0":
        v.append("C4 픽스처 전제 붕괴 — 두 시나리오 모두 수집량 0 이어야 대조가 성립 (dry=%s ok=%s)"
                 % (dc, oc))
    if ds == os_:
        v.append("C4 '미관측'(credential 부재 dry-run) 과 '관측됨 0'(성공·대상 0건) 이 동일 상태 "
                 "'%s' 로 해소 — 후속 조회가 둘을 구별할 수 없음" % ds)
    if ds != "unobserved":
        v.append("C4 credential 부재 dry-run 이 'unobserved' 로 해소되지 않음 (실측 '%s')" % ds)
    if os_ != "observed":
        v.append("C4 성공·대상 0건이 'observed' 로 해소되지 않음 (실측 '%s')" % os_)
    return v


def main():
    mode = sys.argv[1]
    if mode == "record":
        viol = check_record(sys.argv[2], sys.argv[3])
    elif mode == "distinguish":
        viol = check_distinguish(sys.argv[2], sys.argv[3])
    else:
        print("unknown mode", file=sys.stderr)
        sys.exit(2)
    for x in viol:
        print("VIOLATION: %s" % x)
    sys.exit(1 if viol else 0)


if __name__ == "__main__":
    main()
PY

# ─────────────────────────────────────────────────────────────────────────────
# extract.py — workflow YAML 에서 `id: observation` step 의 run 블록을 그대로 뽑는다.
#   (문자열 grep 아님 — YAML 구조 해소. step 부재 = exit 1 fail-closed.)
# ─────────────────────────────────────────────────────────────────────────────
cat > "$WORK/extract.py" <<'PY'
#!/usr/bin/env python3
import sys
import yaml

wf_path, out_path = sys.argv[1], sys.argv[2]
with open(wf_path, encoding="utf-8") as f:
    doc = yaml.safe_load(f)
steps = doc["jobs"]["watchdog"]["steps"]
hit = [s for s in steps if s.get("id") == "observation"]
if len(hit) != 1:
    print("SETUP: `id: observation` step %d 개 (기대 1) — 가시화 step 부재/중복" % len(hit),
          file=sys.stderr)
    sys.exit(1)
run = hit[0].get("run")
if not run:
    print("SETUP: observation step 에 run 블록 부재", file=sys.stderr)
    sys.exit(1)
with open(out_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(run)
PY

# ─────────────────────────────────────────────────────────────────────────────
# run_emitter <workflow> <fetch_status> <raw_count> <raw_reason> <outdir>
#   → outdir/out.txt (GITHUB_OUTPUT 방출), outdir/rc (emitter 종료 코드)
# ─────────────────────────────────────────────────────────────────────────────
run_emitter() {
  local wf="$1" fs="$2" rc_count="$3" rc_reason="$4" outdir="$5"
  local rc=0
  mkdir -p "$outdir"
  : > "$outdir/out.txt"
  : > "$outdir/summary.md"
  if ! python3 "$WORK/extract.py" "$wf" "$outdir/emit.sh" 2> "$outdir/extract.err"; then
    echo "EXTRACT_FAIL" > "$outdir/out.txt"
    echo 99 > "$outdir/rc"
    return 0
  fi
  env -u GITHUB_OUTPUT -u GITHUB_STEP_SUMMARY \
    FETCH_STATUS="$fs" \
    RAW_COLLECTED_COUNT="$rc_count" \
    RAW_UNOBSERVED_REASON="$rc_reason" \
    GITHUB_OUTPUT="$outdir/out.txt" \
    GITHUB_STEP_SUMMARY="$outdir/summary.md" \
    bash "$outdir/emit.sh" > "$outdir/stdout.txt" 2> "$outdir/stderr.txt" || rc=$?
  echo "$rc" > "$outdir/rc"
}

# ─────────────────────────────────────────────────────────────────────────────
# ★ crash-as-RED 차단 (CFP-2984 G7 감사 — 실사건 회귀 방지)
#   `rc≠0 → RED` 단독 판정은 **크래시와 검출을 구별하지 못한다**. 오라클이 예외로 죽으면
#   expect=RED 인 전 케이스가 "잡았다" 로 계상되고 mutant 원장이 통째로 거짓이 된다.
#   ★ baseline 대조군은 **조건부 크래시**(검출 경로에서만 죽는 경우)를 못 잡는다 — G7 실증.
#   ★ SyntaxError·IndentationError 는 Traceback 머리글 없이 출력된다(실측) — 함께 본다.
# ─────────────────────────────────────────────────────────────────────────────
crash_marker() { # <output> → 0 = 크래시 흔적 있음
  case "$1" in
    *Traceback*|*SyntaxError*|*IndentationError*|*TabError*) return 0 ;;
  esac
  return 1
}

assert_case() {
  # assert_case <name> <expected: PASS|RED> <checker args...>
  local name="$1" expect="$2"; shift 2
  local rc=0 out
  out="$(python3 "$WORK/checker.py" "$@" 2>&1)" || rc=$?
  if crash_marker "$out"; then
    echo "X   FAIL: $name — 오라클 크래시(예외). rc≠0 을 검출(RED)로 셀 수 없다"
    echo "$out" | sed 's/^/    ! /'
    FAIL=$((FAIL+1)); return
  fi
  if [ "$rc" -ne 0 ] && ! printf '%s' "$out" | grep -q "VIOLATION"; then
    echo "X   FAIL: $name — RED 인데 판정 근거 마커(VIOLATION)가 없다 (무증거 RED)"
    echo "$out" | sed 's/^/    ! /'
    FAIL=$((FAIL+1)); return
  fi
  local verdict="PASS"
  [ "$rc" -eq 0 ] || verdict="RED"
  if [ "$verdict" = "$expect" ]; then
    echo "OK  $name (expect=$expect got=$verdict)"
    PASS=$((PASS+1))
  else
    echo "X   FAIL: $name (expect=$expect got=$verdict)"
    echo "    checker: $out"
    FAIL=$((FAIL+1))
  fi
}

assert_rc0() {
  local name="$1" outdir="$2" rc
  rc="$(cat "$outdir/rc")"
  if [ "$rc" = "0" ]; then
    echo "OK  $name (emitter rc=0 — ADR-157 accepted-risk 보존)"
    PASS=$((PASS+1))
  else
    echo "X   FAIL: $name — emitter rc=$rc (기대 0). exit code 역전 = ADR-157 §결정 8 위반"
    cat "$outdir/stderr.txt" || true
    FAIL=$((FAIL+1))
  fi
}

echo "── AC-29 external observer visibility — 정본 workflow: $WORKFLOW"

# ── 대조군 (INV-T4 baseline) ────────────────────────────────────────────────
run_emitter "$WORKFLOW" "dry-run" "" ""        "$WORK/base_dry"
run_emitter "$WORKFLOW" "ok"      "0" "none"   "$WORK/base_ok"
assert_case "baseline/dry-run record (미관측 + 사유)"      PASS record "$WORK/base_dry/out.txt" "baseline-dry-run"
assert_case "baseline/ok record (관측됨 0)"                 PASS record "$WORK/base_ok/out.txt"  "baseline-ok"
assert_case "baseline/C4 두 시나리오 구별"                  PASS distinguish "$WORK/base_dry/out.txt" "$WORK/base_ok/out.txt"
assert_rc0  "baseline/dry-run emitter exit 0"               "$WORK/base_dry"
assert_rc0  "baseline/ok emitter exit 0"                    "$WORK/base_ok"

# 방출 실물 1회 표시 (증거 — 산출을 숨기지 않는다)
echo "    [baseline dry-run record]"; sed 's/^/      /' "$WORK/base_dry/out.txt"
echo "    [baseline ok record]";      sed 's/^/      /' "$WORK/base_ok/out.txt"

# ── mutant 적용 (실 파일 변형) ──────────────────────────────────────────────
mutate() {
  # mutate <name> <sed-expr...> → $WORK/<name>.yml
  local name="$1"; shift
  cp "$WORKFLOW" "$WORK/$name.yml"
  local e
  for e in "$@"; do
    python3 - "$WORK/$name.yml" "$e" <<'PY'
import io, sys
path, expr = sys.argv[1], sys.argv[2]
old, new = expr.split("\t", 1)
raw = io.open(path, encoding="utf-8").read()
if old not in raw:
    print("SETUP: mutant 앵커 미발견 — %r" % old[:60], file=sys.stderr)
    sys.exit(3)
io.open(path, "w", encoding="utf-8", newline="\n").write(raw.replace(old, new, 1))
PY
  done
}

# ① 제거 — 방출 블록에서 unobserved_reason 필드 삭제
mutate M1 "$(printf 'echo "unobserved_reason=${REASON_N}"\n\t')"
run_emitter "$WORK/M1.yml" "dry-run" "" "" "$WORK/m1"
assert_case "M1 ①제거: 가시화 필드 삭제" RED record "$WORK/m1/out.txt" "M1"

# ② 주입 — dry-run 분기 사유를 none 으로 (수집 0 사실만 남고 사유 소실)
mutate M2 "$(printf 'REASON_N="credential-absent"\tREASON_N="none"')"
run_emitter "$WORK/M2.yml" "dry-run" "" "" "$WORK/m2"
assert_case "M2 ②주입: 수집 0 + 사유 누락" RED record "$WORK/m2/out.txt" "M2"

# ③ 등가변형 — 사유를 vacuous 3형태로 표기 변형 (unknown / null / 빈 문자열)
mutate M3a "$(printf 'REASON_N="credential-absent"\tREASON_N="unknown"')"
run_emitter "$WORK/M3a.yml" "dry-run" "" "" "$WORK/m3a"
assert_case "M3a ③등가변형: 사유 'unknown' 표기" RED record "$WORK/m3a/out.txt" "M3a"

mutate M3b "$(printf 'REASON_N="credential-absent"\tREASON_N="null"')"
run_emitter "$WORK/M3b.yml" "dry-run" "" "" "$WORK/m3b"
assert_case "M3b ③등가변형: 사유 'null' 표기" RED record "$WORK/m3b/out.txt" "M3b"

mutate M3c "$(printf 'REASON_N="credential-absent"\tREASON_N=""')"
run_emitter "$WORK/M3c.yml" "dry-run" "" "" "$WORK/m3c"
assert_case "M3c ③등가변형: 사유 빈 문자열" RED record "$WORK/m3c/out.txt" "M3c"

# ④ 구별 붕괴 — dry-run 을 observed 로 접어 "관측됨 0" 과 동일 record 화
mutate M4 "$(printf 'dry-run)\n              OBS_STATE="unobserved"\tdry-run)\n              OBS_STATE="observed"')"
run_emitter "$WORK/M4.yml" "dry-run" "" "" "$WORK/m4"
run_emitter "$WORK/M4.yml" "ok" "0" "none"  "$WORK/m4ok"
assert_case "M4 ④구별붕괴: 미관측 → observed 접힘" RED distinguish "$WORK/m4/out.txt" "$WORK/m4ok/out.txt"

# ── 형제 회귀 확인 (봉합이 형제 검출력을 파괴하지 않았는가) ─────────────────
# vacuous 정규화가 "정상 사유" 까지 삼키지 않는지: fetch-failed 경로도 구체 사유로 해소돼야 한다.
run_emitter "$WORKFLOW" "fetch-failed" "" "" "$WORK/sib_ff"
assert_case "형제/fetch-failed 도 구체 사유로 해소" PASS record "$WORK/sib_ff/out.txt" "sibling-fetch-failed"
# fetch_status 자체가 소실된 경로도 "미관측 + 사유 명시" 로 해소돼야 한다(조용한 통과 금지).
run_emitter "$WORKFLOW" "" "" "" "$WORK/sib_missing"
assert_case "형제/fetch_status 소실도 미관측·사유 명시" PASS record "$WORK/sib_missing/out.txt" "sibling-status-missing"
assert_rc0  "형제/fetch_status 소실 emitter exit 0" "$WORK/sib_missing"

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
