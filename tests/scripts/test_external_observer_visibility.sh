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
# ★ exit code 무접촉 (ADR-164 §결정 4 graceful degrade 보존): 본 테스트는 emitter 가 전 시나리오에서
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
#   parse-error = P2-3(CFP-2984) 봉합분. 응답은 왔으나 파싱이 깨져 셀 수 없었던 경우 —
#   구 구현에서 이 상태가 "관측했고 0건" 으로 접히던 것이 silent-zero 자기모순이었다.
#   ★ CFP-2995 — 4 → 12 원소. watchdog 의 값 공간 확장과 **분리 불가**한 동반 변경이다
#     (미갱신 시 신규 사유가 전건 "구체 사유 집합 밖" 으로 RED — 의도된 결합).
#   HTTP 축 5: 비-2xx 응답을 한 사유로 접지 않는다 — 401/403(자격증명 교체) · 404(URL·권한,
#     Jira 가 "이슈 부재 또는 권한 없음" 으로 문서화) · 429(우리 cadence) · 5xx(벤더 장애,
#     escalation 주체가 반대) · other(위 넷에 배정되지 않은 비-2xx **잔여 전칭**: 1xx·3xx·잔여 4xx).
#   AC-2 축 3: 보고된 수집량이 관측 가능한 전체를 나타내지 않는 세 경로 —
#     element-shape-unexpected(원소 무신호 드롭) · count-unresolved(산출 실패) · page-truncated(부분관측).
CONCRETE_REASONS = {
    # 기존 4
    "credential-absent", "fetch-error", "fetch-status-missing", "parse-error",
    # HTTP 축 5 (CFP-2995)
    "http-error-auth", "http-error-not-found", "http-error-rate-limited",
    "http-error-server", "http-error-other",
    # AC-2 축 3 (CFP-2995)
    "element-shape-unexpected", "count-unresolved", "page-truncated",
}


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
import re
import sys
import yaml

wf_path, out_path = sys.argv[1], sys.argv[2]
# ★ CFP-2995 Seam 1 — step 선택자 매개변수화(종전은 "observation" 하드코딩).
#   id 우선, 없으면 name 으로 찾는다 — id 가 없는 step 도 실행 대상이 될 수 있다.
selector = sys.argv[3] if len(sys.argv) > 3 else "observation"
with open(wf_path, encoding="utf-8") as f:
    doc = yaml.safe_load(f)
steps = doc["jobs"]["watchdog"]["steps"]
hit = [s for s in steps if s.get("id") == selector]
if not hit:
    hit = [s for s in steps if s.get("name") == selector]
if len(hit) != 1:
    print("SETUP: step '%s' %d 개 (기대 1) — 대상 step 부재/중복" % (selector, len(hit)),
          file=sys.stderr)
    sys.exit(1)
run = hit[0].get("run")
if not run:
    print("SETUP: step '%s' 에 run 블록 부재" % selector, file=sys.stderr)
    sys.exit(1)
# ★ GitHub 표현식은 bash 문법이 아니다(${{ ... }} = bad substitution). 실행 가능하도록
#   자리표시자로 치환한다 — **하네스 변환이며 숨기지 않고 선언한다.**
#   본 변환은 판정 대상 축(방출 레코드·진단 표면)을 건드리지 않는다.
_GHA = chr(92) + "$" + chr(92) + "{" + chr(92) + "{" + "[^}]*" + chr(92) + "}" + chr(92) + "}"
run = re.sub(_GHA, "__GHA_EXPR__", run)
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
    echo "OK  $name (emitter rc=0 — ADR-164 §결정 4 graceful degrade 보존)"
    PASS=$((PASS+1))
  else
    echo "X   FAIL: $name — emitter rc=$rc (기대 0). exit code 역전 = ADR-164 §결정 4 위반"
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

# ── P2-3 봉합 결박: parse-degraded (CFP-2984 구현리뷰) ──────────────────────
#   구 fetch step 은 bare `except: json.dump([])` 로 401 오류 바디·HTML 오류 페이지를
#   빈 배열로 접고 `fetch_status=ok` 를 찍어, 하류가 "관측했고 0건"(observed/0/none)을
#   방출했다 — AC-29 가 구별하려던 두 상태의 혼동이자 AC-24 위반.
#   봉합 = fetch_status 에 parse-degraded 분기 신설. 여기서 그 분기가
#   **unobserved + 구체 사유** 로 해소되는지 결박한다(exit code 무접촉).
run_emitter "$WORKFLOW" "parse-degraded" "" "" "$WORK/sib_parse"
assert_case "P2-3/parse-degraded 는 미관측·구체 사유로 해소" PASS record "$WORK/sib_parse/out.txt" "sibling-parse-degraded"
assert_rc0  "P2-3/parse-degraded emitter exit 0 (ADR-164 §결정 4 무접촉)" "$WORK/sib_parse"
# ★ 핵심 구별: parse-degraded 가 '관측됨 0'(ok 경로) 과 **같은 record 로 접히면** 봉합이 무효다.
run_emitter "$WORKFLOW" "ok" "0" "none" "$WORK/sib_parse_ok"
assert_case "P2-3/parse-degraded ≠ 관측됨 0 (구별 유지)" PASS distinguish \
  "$WORK/sib_parse/out.txt" "$WORK/sib_parse_ok/out.txt"


# ═════════════════════════════════════════════════════════════════════════════
# CFP-2995 — 무신호 영점(silent zero) 봉합 판별력 (AC-1·2·3·4·5·19 + sentinel + §4.3)
#
# ★ 오라클 정의역 = 실 workflow 의 `id: fetch-comments` step 을 YAML 로 추출해
#   **실제로 실행**한 산출이다. 위 AC-29 절과 같은 원칙 — 문면 presence 검사가 아니다.
#
# ★ curl 대역 (PATH-shadow) — INV-T3(네트워크 0) 보존. loopback http.server 미채택:
#   그것은 실 소켓이라 이 파일이 자기 헤더에 선언한 불변식을 문면 그대로 위반한다.
#   대역의 충실성은 가정이 아니라 **측정**한다 — 침묵 2축을 실 바이너리와 대조하는
#   leg 을 먼저 통과시킨 뒤에만 대역 기반 판정을 계상한다(band-fidelity gate).
#   ★ 정직 잔여: 대역은 curl 이 아니다. 충실성은 아래 2축 + 상태코드/파일기록/rc 범위
#     까지만 검증되며 그 밖의 적합성은 미검증이다. "curl 과 동등" 이라 쓰지 않는다.
#
# ★ python3 대역 — 실 바이너리에 **위임**한다. 유일한 개입은 AC-2 (b) 산출 실패
#   픽스처에서 그 호출의 **입력**(comments.json)을 읽기 불가로 만드는 것뿐이며,
#   실패는 실 코드 경로에서 실제로 발생한다(모의 반환값 아님).
#
# ★ 3상태 규율: 「관측했는데 X」와 「관측 못 함」을 구별한다. 판정에 필요한 기저선·
#   바이너리가 없으면 통과가 아니라 **판정 불가 → RED**(명시 사유 동반)로 접는다.
# ═════════════════════════════════════════════════════════════════════════════

BASELINE_SHA="6bb0e8aa5be0c5bec9bcb9c672174417e633eacb"
REAL_CURL="$(command -v curl || true)"
REAL_PYTHON3="$(command -v python3 || true)"
BAND_DIR="$WORK/band"
mkdir -p "$BAND_DIR"

ok()  { echo "OK  $1"; PASS=$((PASS+1)); }
bad() { echo "X   FAIL: $1 — $2"; FAIL=$((FAIL+1)); }

# ── curl 대역 ────────────────────────────────────────────────────────────────
# 실 바이너리 관측치 재현:
#   HTTP 오류      → rc 0 · stderr 0 B · -o 파일 기록 · -w = 상태코드
#   transport 실패 → rc 6 · -w = 000 · -o **미생성** · stderr 는 -S 유무에 좌우
cat > "$BAND_DIR/curl" <<'BAND'
#!/usr/bin/env bash
OUT=""; SHOW_ERR=0
while [ $# -gt 0 ]; do
  case "$1" in
    -o) OUT="$2"; shift 2 ;;
    -sS) SHOW_ERR=1; shift ;;
    -S) SHOW_ERR=1; shift ;;
    *) shift ;;
  esac
done
if [ "${BAND_MODE:-http}" = "transport" ]; then
  printf '000'
  if [ "$SHOW_ERR" = "1" ]; then
    printf 'curl: (6) Could not resolve host: %s\n' "${BAND_HOST:-nonexistent.invalid}" >&2
  fi
  exit 6
fi
if [ -n "$OUT" ]; then cp "$BAND_BODY" "$OUT"; fi
printf '%s' "${BAND_CODE:-200}"
exit 0
BAND
chmod +x "$BAND_DIR/curl"

# ── python3 대역 (실 바이너리 위임) ──────────────────────────────────────────
cat > "$BAND_DIR/python3" <<'BAND'
#!/usr/bin/env bash
for a in "$@"; do
  case "$a" in
    *"len(json.load(open('comments.json')))"*)
      if [ "${BAND_BREAK_COUNT:-0}" = "1" ]; then printf 'NOT-JSON{' > comments.json; fi ;;
  esac
done
exec "$BAND_REAL_PYTHON3" "$@"
BAND
chmod +x "$BAND_DIR/python3"

# ── ac4.py — AC-4 ①② 정의역 추출·대조 (착지 전 불변 리비전 대 착지 후) ──────
cat > "$WORK/ac4.py" <<'PY'
#!/usr/bin/env python3
"""AC-4 ①(실행되는 종료 문) · ②(비차단 설정) 정의역 분리 추출 + 착지 전후 대조.

★ 총 개수 일치만으로는 충족으로 계상하지 않는다 — 원소 단위로 대조한다.
★ 양 피연산자 non-empty 를 **먼저** 확인한다(부재-assert 항진 차단).
"""
import io, re, sys
import yaml

def read(p):
    return io.open(p, encoding="utf-8").read()

def domain_exits(txt):
    """① run 블록에서 **실제로 실행되는** exit <n> 문. 주석 줄 배제."""
    out = []
    for i, line in enumerate(txt.split("\n"), 1):
        if line.strip().startswith("#"):
            continue
        m = re.search(r"(?<![\w-])exit\s+(\d+)\b", line)
        if m:
            out.append(int(m.group(1)))
    return out

def domain_coe(txt):
    """② 비차단 설정 = continue-on-error 선언, job-level ∪ step-level.
    원소는 키가 아니라 **키=값** 쌍이다 — 값을 빼면 true->false 뒤집기가 통과한다."""
    doc = yaml.safe_load(txt)
    res = []
    for jn, jb in doc["jobs"].items():
        if "continue-on-error" in jb:
            res.append("job:%s:continue-on-error=%s" % (jn, jb["continue-on-error"]))
        for s in jb.get("steps", []):
            if "continue-on-error" in s:
                res.append("step:%s:continue-on-error=%s"
                           % (s.get("id") or s.get("name"), s["continue-on-error"]))
    return sorted(res)

def main():
    base, cur = read(sys.argv[1]), read(sys.argv[2])
    v = []
    be, ce = domain_exits(base), domain_exits(cur)
    bc, cc = domain_coe(base), domain_coe(cur)

    # ② 양 피연산자 non-empty 선확인
    for name, a, b in (("① 종료문", be, ce), ("② 비차단 설정", bc, cc)):
        if not a:
            v.append("%s 착지 전 열거가 비어있다 — 대조 불성립" % name)
        if not b:
            v.append("%s 착지 후 열거가 비어있다 — 대조 불성립" % name)
    if v:
        print("\n".join("VIOLATION: " + x for x in v))
        return 1

    # ① 실행되는 종료 문이 전건 종료코드 0
    nonzero = [c for c in ce if c != 0]
    if nonzero:
        v.append("① 착지 후 종료코드 0 이 아닌 종료 문 %s — ADR-164 §결정 4 graceful degrade 역전" % nonzero)
    # ① 착지 전 각 종료 문이 착지 후에도 대응 원소를 가짐 (삭제 금지). multiset 포함.
    rem = list(ce)
    missing = []
    for c in be:
        if c in rem:
            rem.remove(c)
        else:
            missing.append(c)
    if missing:
        v.append("① 착지 전 종료 문 %s 이 착지 후 대응 원소를 잃었다 — 삭제 불허" % missing)

    # ② 원소 단위 동일 (총 개수 일치만으로 계상하지 않는다)
    if bc != cc:
        v.append("② 비차단 설정이 원소 단위로 달라졌다: 착지 전 %s -> 착지 후 %s" % (bc, cc))
    elif len(bc) != len(cc):
        v.append("② 개수 불일치 %d -> %d" % (len(bc), len(cc)))

    print("① 종료문 착지 전 %d -> 착지 후 %d (전건 exit 0: %s)"
          % (len(be), len(ce), not nonzero))
    print("② 비차단 설정 원소 %s (착지 전후 동일: %s)" % (cc, bc == cc))
    for x in v:
        print("VIOLATION: %s" % x)
    return 1 if v else 0

if __name__ == "__main__":
    sys.exit(main())
PY

# ── run_fetch <workflow> <outdir> [ENV=VAL ...] ──────────────────────────────
run_fetch() {
  local wf="$1" outdir="$2"; shift 2
  local rc=0
  rm -rf "$outdir"; mkdir -p "$outdir"
  : > "$outdir/out.txt"; : > "$outdir/summary.md"
  if ! python3 "$WORK/extract.py" "$wf" "$outdir/fetch.sh" fetch-comments 2> "$outdir/extract.err"; then
    echo "EXTRACT_FAIL" > "$outdir/out.txt"; echo 99 > "$outdir/rc"; return 0
  fi
  (
    cd "$outdir" && env -u GITHUB_OUTPUT -u GITHUB_STEP_SUMMARY \
      PATH="$BAND_DIR:$PATH" BAND_REAL_PYTHON3="$REAL_PYTHON3" \
      "$@" \
      GITHUB_OUTPUT="$outdir/out.txt" GITHUB_STEP_SUMMARY="$outdir/summary.md" \
      bash "$outdir/fetch.sh" > "$outdir/stdout.txt" 2> "$outdir/stderr.txt"
  ) || rc=$?
  echo "$rc" > "$outdir/rc"
}

field()  { sed -n "s/^$2=//p" "$1/out.txt" | tail -1; }
keyset() { sed -n 's/^\([a-z_][a-z_]*\)=.*/\1/p' "$1/out.txt" | sort -u | tr '\n' ' '; }

# 워크플로가 **손으로 적은** 문자열을 배제하고 실행 대상이 생성한 진단만 남긴다 (AC-19 귀속 고정).
foreign_diag() {
  grep -v '^\[branch-liveness-watchdog\]' "$1/stderr.txt" 2>/dev/null \
    | sed 's/^\[parse-error\] //' | grep -v '^[[:space:]]*$' || true
}
curl_diag_present()  { foreign_diag "$1" | grep -q '^curl:'; }
parse_diag_present() { foreign_diag "$1" | grep -qE 'Error|Traceback'; }

echo ""
echo "── CFP-2995 무신호 영점 봉합 — 정본 workflow: $WORKFLOW"

# ═════════════════════════════════════════════════════════════════════════════
# band-fidelity gate — 대역이 침묵 2축을 실 바이너리와 동일하게 재현하는가 (AC-19 선결)
# ═════════════════════════════════════════════════════════════════════════════
probe_silence() {
  # probe_silence <bin|BAND> <flag> <outdir> → "rc|stderr(empty|nonempty)|-w값|-o(present|absent)"
  local bin="$1" flag="$2" d="$3"
  mkdir -p "$d"; local rc=0
  if [ "$bin" = "BAND" ]; then
    env BAND_MODE=transport BAND_HOST=nonexistent.invalid \
      "$BAND_DIR/curl" $flag -w '%{http_code}' -o "$d/o" "https://nonexistent.invalid/x" \
      > "$d/w" 2> "$d/e" || rc=$?
  else
    "$bin" $flag -w '%{http_code}' -o "$d/o" --connect-timeout 3 --max-time 8 \
      "https://nonexistent.invalid/x" > "$d/w" 2> "$d/e" || rc=$?
  fi
  local ebit ofile
  if [ -s "$d/e" ]; then ebit=nonempty; else ebit=empty; fi
  if [ -f "$d/o" ]; then ofile=present; else ofile=absent; fi
  printf '%s|%s|%s|%s' "$rc" "$ebit" "$(cat "$d/w")" "$ofile"
}

BAND_TRUSTED=0
if [ -z "$REAL_CURL" ]; then
  bad "AC-19/band-fidelity" "실 curl 바이너리 부재 — 대역 충실성을 측정할 수 없다(판정 불가). fail-closed"
elif [ -z "$REAL_PYTHON3" ]; then
  bad "AC-19/band-fidelity" "실 python3 바이너리 부재 — 판정 불가. fail-closed"
else
  R_S="$(probe_silence "$REAL_CURL" "-s"  "$WORK/fid_rs")"
  R_SS="$(probe_silence "$REAL_CURL" "-sS" "$WORK/fid_rss")"
  B_S="$(probe_silence BAND "-s"  "$WORK/fid_bs")"
  B_SS="$(probe_silence BAND "-sS" "$WORK/fid_bss")"
  echo "    [실 curl] -s: $R_S   -sS: $R_SS"
  echo "    [대역   ] -s: $B_S   -sS: $B_SS"
  # 축① -s 단독 = stderr 침묵 / 축② -sS = 진단 실재.
  # ★ 바이트 수는 pin 하지 않는다 — 실측상 대상 호스트명 길이에 따라 변한다.
  #   재는 것은 empty/nonempty 이분이다.
  if [ "$R_S" = "$B_S" ] && [ "$R_SS" = "$B_SS" ]; then
    if [ "$R_S" = "$R_SS" ]; then
      bad "AC-19/band-fidelity" "실 바이너리에서 두 축이 구별되지 않는다 — 픽스처가 판별력을 못 준다"
    else
      BAND_TRUSTED=1
      ok "AC-19/band-fidelity: 대역이 침묵 2축(-s 침묵 / -sS 진단)을 실 바이너리와 동일 재현"
    fi
  else
    bad "AC-19/band-fidelity" "대역 != 실 바이너리 (실 -s=$R_S 대역 -s=$B_S / 실 -sS=$R_SS 대역 -sS=$B_SS)"
  fi
fi

# ── 픽스처 본문 ──────────────────────────────────────────────────────────────
FX="$WORK/fx"; mkdir -p "$FX"
printf '%s' '{"comments":[],"total":0,"startAt":0}'                                       > "$FX/zero.json"
printf '%s' '{"comments":[{"body":"a"}],"total":1,"startAt":0}'                            > "$FX/one.json"
printf '%s' '{"comments":[{"body":"a"},"NOT-A-DICT",{"body":"b"}],"total":3,"startAt":0}'  > "$FX/mixed.json"
printf '%s' '{"comments":[{"body":"a"},{"body":"b"}],"total":57,"startAt":0}'              > "$FX/trunc.json"
printf '%s' '{"errorMessages":["issue not found"]}'                                        > "$FX/errshape.json"
printf '%s' '[]'                                                                           > "$FX/bare.json"

CRED="JIRA_READ_TOKEN=t ATLASSIAN_USER_EMAIL=u@example.invalid"

# ═════════════════════════════════════════════════════════════════════════════
# AC-1 — HTTP 오류 + **정상 파싱되는 수집 컨테이너 본문** → (ok,0,none) 금지
#   ★ V-5: "401 + Jira 오류 본문" 픽스처는 공허하다 — 그것은 변경 전에도 이미
#     parse-degraded 로 잡혔다. (ok,0,none) 을 실제로 생산하던 유일 입력은
#     **HTTP 오류 + well-formed 본문** 이다. 그것을 pin 한다.
# ═════════════════════════════════════════════════════════════════════════════
ac1_case() { # <code> <body> <기대 사유> <라벨>
  local d="$WORK/ac1_$1"
  run_fetch "$WORKFLOW" "$d" BAND_MODE=http BAND_CODE="$1" BAND_BODY="$2" $CRED
  local fs cc ur
  fs="$(field "$d" fetch_status)"; cc="$(field "$d" collected_count)"; ur="$(field "$d" unobserved_reason)"
  if [ "$fs" = "ok" ] && [ "$cc" = "0" ] && [ "$ur" = "none" ]; then
    bad "AC-1/$4" "HTTP $1 인데 관측성공 0건 형태 (ok,0,none) 를 방출했다 — 무신호 영점"
  elif [ "$ur" != "$3" ]; then
    bad "AC-1/$4" "미관측 사유가 '$ur' (기대 '$3') — HTTP 오류를 가리키는 구체 사유가 아니다"
  else
    ok "AC-1/$4: HTTP $1 + well-formed 본문 -> ($fs, $cc, $ur)"
  fi
}
ac1_case 401 "$FX/zero.json" "http-error-auth"         "401 자격증명"
ac1_case 403 "$FX/bare.json" "http-error-auth"         "403 권한"
ac1_case 404 "$FX/zero.json" "http-error-not-found"    "404 이슈부재-또는-권한없음"
ac1_case 429 "$FX/zero.json" "http-error-rate-limited" "429 rate limit"
ac1_case 503 "$FX/zero.json" "http-error-server"       "503 벤더 장애"
ac1_case 302 "$FX/zero.json" "http-error-other"        "302 비-2xx 잔여 전칭"
ac1_case 100 "$FX/zero.json" "http-error-other"        "100 1xx 도 잔여 전칭이 덮는다"

# ═════════════════════════════════════════════════════════════════════════════
# AC-3 (역방향 보호) — 200 + {"comments":[]} → (ok,0,none) **그대로** 방출
#   AC-1 의 과교정 대조군이다. 이 leg 이 없으면 "전부 unobserved" 구현이 AC-1 을 통과한다.
# ═════════════════════════════════════════════════════════════════════════════
run_fetch "$WORKFLOW" "$WORK/ac3" BAND_MODE=http BAND_CODE=200 BAND_BODY="$FX/zero.json" $CRED
if [ "$(field "$WORK/ac3" fetch_status)" = "ok" ] \
   && [ "$(field "$WORK/ac3" collected_count)" = "0" ] \
   && [ "$(field "$WORK/ac3" unobserved_reason)" = "none" ]; then
  ok "AC-3: 200 + 진짜 0건 -> (ok, 0, none) 보존 (관측된 0 != 미관측)"
else
  bad "AC-3" "진짜 0건이 ($(field "$WORK/ac3" fetch_status), $(field "$WORK/ac3" collected_count), $(field "$WORK/ac3" unobserved_reason)) 로 방출 — 과교정"
fi
run_fetch "$WORKFLOW" "$WORK/ac3b" BAND_MODE=http BAND_CODE=200 BAND_BODY="$FX/one.json" $CRED
if [ "$(field "$WORK/ac3b" fetch_status)" = "ok" ] && [ "$(field "$WORK/ac3b" collected_count)" = "1" ]; then
  ok "AC-3/실수집: 200 + 1건 -> (ok, 1, none)"
else
  bad "AC-3/실수집" "1건 수집이 (ok,1,none) 로 방출되지 않음"
fi

# ═════════════════════════════════════════════════════════════════════════════
# AC-2 — 보고된 수집량이 관측 가능한 전체를 나타내지 않는 세 갈래
#   하한 원소는 **착지 전 좌표가 아니라 재위치 앵커 문자열**로 식별한다.
#   각 앵커가 착지 후 파일에 **정확히 한 번** 등장해야 재위치가 성립한다.
# ═════════════════════════════════════════════════════════════════════════════
anchor_once() { # <앵커> <라벨>
  local n; n="$(grep -cF -- "$1" "$WORKFLOW" || true)"
  if [ "$n" = "1" ]; then
    ok "AC-2/앵커 재위치: $2 (정확히 1회)"
  else
    bad "AC-2/앵커 재위치: $2" "착지 후 파일에 $n 회 등장 (기대 1) — 재위치 미성립"
  fi
}
# 형태① 하한 (무신호 사이트 표) — Story 가 동결한 문자열 verbatim
anchor_once "c.get('body', '') for c in comments if isinstance(c, dict)" "형태1(a) 원소 드롭"
anchor_once 'OBSERVED_COUNT=$(python3 -c'                                "형태1(b) 산출 실패"
# 형태② 하한 (부분관측 사이트 표) — 두 앵커가 **각각 다른 결손**을 가리킨다
anchor_once '/rest/api/3/issue/${CONTROL_ISSUE_KEY}/comments'            "형태2(c) 요청 페이지 창"
anchor_once "comments = data['comments']"                                "형태2(c) 전체량 대조"

# (a) 원소 무신호 드롭
run_fetch "$WORKFLOW" "$WORK/ac2a" BAND_MODE=http BAND_CODE=200 BAND_BODY="$FX/mixed.json" $CRED
if [ "$(field "$WORK/ac2a" unobserved_reason)" = "element-shape-unexpected" ] \
   && [ "$(field "$WORK/ac2a" fetch_status)" != "ok" ]; then
  ok "AC-2/형태1(a): 예상 밖 형태 원소 드롭 -> element-shape-unexpected"
else
  bad "AC-2/형태1(a)" "혼합 배열이 ($(field "$WORK/ac2a" fetch_status), $(field "$WORK/ac2a" unobserved_reason)) 로 방출 — 드롭이 무신호"
fi

# (b) 산출 실패 — 그 호출의 **입력**을 읽기 불가로 만든다 (실 코드 경로에서 실제 실패)
run_fetch "$WORKFLOW" "$WORK/ac2b" BAND_MODE=http BAND_CODE=200 BAND_BODY="$FX/one.json" BAND_BREAK_COUNT=1 $CRED
if [ "$(field "$WORK/ac2b" unobserved_reason)" = "count-unresolved" ] \
   && [ "$(field "$WORK/ac2b" fetch_status)" != "ok" ]; then
  ok "AC-2/형태1(b): 수집량 산출 실패 -> count-unresolved ('0 건' 으로 접지 않는다)"
else
  bad "AC-2/형태1(b)" "산출 실패가 ($(field "$WORK/ac2b" fetch_status), $(field "$WORK/ac2b" collected_count), $(field "$WORK/ac2b" unobserved_reason)) 로 방출 — OR-fallback 잔존 의심"
fi

# (c) 부분관측 — 취득분(startAt + len) < total
run_fetch "$WORKFLOW" "$WORK/ac2c" BAND_MODE=http BAND_CODE=200 BAND_BODY="$FX/trunc.json" $CRED
if [ "$(field "$WORK/ac2c" unobserved_reason)" = "page-truncated" ]; then
  ok "AC-2/형태2(c): 취득 2 < 전체 57 -> page-truncated (부분을 전체로 보고하지 않는다)"
else
  bad "AC-2/형태2(c)" "절단이 ($(field "$WORK/ac2c" fetch_status), $(field "$WORK/ac2c" collected_count), $(field "$WORK/ac2c" unobserved_reason)) 로 방출 — 부분이 전체로 보고됨"
fi
# 판별력: 절단이 아니면 절단이라 하지 않는다 (항진 차단)
if [ "$(field "$WORK/ac3b" unobserved_reason)" != "page-truncated" ]; then
  ok "AC-2/형태2(c) 판별력: 비절단 응답은 page-truncated 로 접히지 않는다"
else
  bad "AC-2/형태2(c) 판별력" "완전 응답까지 절단으로 판정 — 항진"
fi

# ═════════════════════════════════════════════════════════════════════════════
# AC-5 — 실패 class 해상도 보존
#   transport 실패의 사유가 **HTTP 상태 코드 유래 값공간에 속하지 않을 것**.
#   한쪽이 빈 값·부재여서 생기는 차이는 충족으로 계상하지 않는다.
# ═════════════════════════════════════════════════════════════════════════════
run_fetch "$WORKFLOW" "$WORK/ac5t" BAND_MODE=transport $CRED
R_TRANSPORT="$(field "$WORK/ac5t" unobserved_reason)"
R_HTTP="$(field "$WORK/ac1_404" unobserved_reason)"
if [ -z "$R_TRANSPORT" ] || [ -z "$R_HTTP" ]; then
  bad "AC-5" "한쪽 사유가 빈 값/부재 (transport='$R_TRANSPORT' http='$R_HTTP') — 차이를 충족으로 계상하지 않는다"
elif [ "$R_TRANSPORT" = "$R_HTTP" ]; then
  bad "AC-5" "transport 실패와 HTTP 오류가 같은 사유 '$R_TRANSPORT' 로 접힘 — 해상도 손실"
elif [[ "$R_TRANSPORT" == http-error* ]]; then
  bad "AC-5" "transport 사유 '$R_TRANSPORT' 가 HTTP 유래 값공간에 속함 — 전송 실패가 HTTP 오류로 접힘"
else
  ok "AC-5: transport='$R_TRANSPORT' != http='$R_HTTP', transport 사유가 HTTP 값공간 밖"
fi
# 귀속 고정 — 판정 순서가 curl_rc 우선인가. transport 실패에서 -w 는 000 을 낸다;
# http_code 를 먼저 봤다면 사유가 http-error-* 로 붕괴했을 것이다.
if [ "$(field "$WORK/ac5t" http_code)" = "000" ] && [ "$(field "$WORK/ac5t" curl_rc)" = "6" ]; then
  ok "AC-5/판정 순서: raw 는 (http_code=000, curl_rc=6) 인데 사유는 transport 축 — curl_rc 우선 성립"
else
  bad "AC-5/판정 순서" "transport 실패 raw 가 (http_code=$(field "$WORK/ac5t" http_code), curl_rc=$(field "$WORK/ac5t" curl_rc)) — 픽스처 전제 붕괴"
fi
# HTTP 5 bucket 이 서로 다른 값으로 해소되는가 (1-bucket fallback 이 아님)
BUCKETS="$(for c in 401 404 429 503 302; do field "$WORK/ac1_$c" unobserved_reason; done | sort -u | wc -l)"
if [ "$BUCKETS" -ge 5 ]; then
  ok "AC-5/bucket 해상도: 401·404·429·5xx·기타가 $BUCKETS 개 서로 다른 사유로 해소"
else
  bad "AC-5/bucket 해상도" "5 종 HTTP 오류가 $BUCKETS 개 사유로만 해소 — 운영자가 로그를 파야 한다"
fi

# ═════════════════════════════════════════════════════════════════════════════
# AC-4 — 종료 계약 무변 (3 정의역 분리 추출, 착지 전 불변 리비전과 대조)
#   ① 실제로 실행되는 종료 문 (주석 배제)  ② 비차단 설정 (job ∪ step, 키=값)
#   ③ 분기별 출력 키 집합 — **실행으로** 수집한다(문면 아님).
#   ★ 어느 정의역에서도 총 개수 일치만으로 충족 계상하지 않는다 — 원소 단위 대조.
# ═════════════════════════════════════════════════════════════════════════════
BASE_WF="$WORK/baseline.yml"
BASE_OK=0
if git -C "$REPO_ROOT" archive "$BASELINE_SHA" .github/workflows/branch-liveness-watchdog.yml 2>/dev/null | tar -xO > "$BASE_WF" 2>/dev/null; then
  if [ -s "$BASE_WF" ]; then BASE_OK=1; fi
fi
if [ "$BASE_OK" = "1" ]; then
  AC4_RC=0
  AC4_OUT="$(python3 "$WORK/ac4.py" "$BASE_WF" "$WORKFLOW" 2>&1)" || AC4_RC=$?
  echo "$AC4_OUT" | sed 's/^/    /'
  if [ "$AC4_RC" -eq 0 ]; then
    ok "AC-4/12: 종료문·비차단 설정 착지 전후 대조 (원소 단위)"
  else
    bad "AC-4/12" "착지 전후 대조 실패 (위 내역)"
  fi
else
  bad "AC-4/12" "착지 전 불변 리비전 $BASELINE_SHA 판독 불가 — 판정 불가(as-built 기저선 금지). fail-closed"
fi

# ③ 분기별 출력 키 집합 — 실행 수집. 하한 4 분기를 먼저 확인한 뒤 **분기 전수**로 넓힌다.
run_fetch "$WORKFLOW" "$WORK/br_dry" BAND_MODE=http
run_fetch "$WORKFLOW" "$WORK/br_pd"  BAND_MODE=http BAND_CODE=200 BAND_BODY="$FX/errshape.json" $CRED
BR_LABEL=("자격증명 부재" "fetch 실패" "파싱 열화" "정상 수집" "HTTP 오류(신설)" "원소 드롭" "산출 실패" "페이지 절단")
BR_DIR=("$WORK/br_dry" "$WORK/ac5t" "$WORK/br_pd" "$WORK/ac3" "$WORK/ac1_404" "$WORK/ac2a" "$WORK/ac2b" "$WORK/ac2c")
AC4_3_OK=1
REF_KEYS="$(keyset "${BR_DIR[0]}")"
i=0
while [ "$i" -lt "${#BR_DIR[@]}" ]; do
  K="$(keyset "${BR_DIR[$i]}")"
  if [ "$K" != "$REF_KEYS" ]; then
    bad "AC-4/3" "분기 '${BR_LABEL[$i]}' 키 집합 [$K] != 기준 [$REF_KEYS]"
    AC4_3_OK=0
  fi
  i=$((i+1))
done
if [ -z "$REF_KEYS" ]; then
  bad "AC-4/3" "기준 분기의 키 집합이 비어있다 — 양 피연산자 non-empty 위반"
elif [ "$AC4_3_OK" = "1" ]; then
  ok "AC-4/3: ${#BR_DIR[@]} 분기(하한 4 초과) 전건 출력 키 집합 동일 — [$REF_KEYS]"
fi
if [ "${#BR_DIR[@]}" -ge 4 ]; then
  ok "AC-4/3 floor: 하한 4 분기(자격증명 부재·fetch 실패·파싱 열화·정상 수집) 포함"
else
  bad "AC-4/3 floor" "분기 열거가 하한 4 에 미달"
fi
i=0; ALLRC=1
while [ "$i" -lt "${#BR_DIR[@]}" ]; do
  if [ "$(cat "${BR_DIR[$i]}/rc")" != "0" ]; then
    bad "AC-4/1실행" "분기 '${BR_LABEL[$i]}' rc=$(cat "${BR_DIR[$i]}/rc") (기대 0)"
    ALLRC=0
  fi
  i=$((i+1))
done
if [ "$ALLRC" = "1" ]; then
  ok "AC-4/1실행: ${#BR_DIR[@]} 분기 전건 rc=0 (ADR-164 §결정 4 graceful degrade 보존)"
fi

# ═════════════════════════════════════════════════════════════════════════════
# sentinel leg — curl **미실행** 분기의 raw 2필드가 not-executed (§8-fixture, E-16)
#   ★ 정직 등급 = E-11 형: 이 leg 을 삭제해도 RED 로 전환되는 AC 는 0.
#     「기계 검사 있음 + 삭제 방지는 리뷰 판정면」이지 「AC 가 기계 보존」이 아니다.
#   ★ 부재-assert 금지 — 「000 이 아님」이 아니라 「not-executed 임」을 단언한다.
# ═════════════════════════════════════════════════════════════════════════════
if [ "$(field "$WORK/br_dry" http_code)" = "not-executed" ] \
   && [ "$(field "$WORK/br_dry" curl_rc)" = "not-executed" ]; then
  ok "sentinel: curl 미실행 분기의 raw 2필드 = not-executed (값공간 밖 명시 토큰)"
else
  bad "sentinel" "curl 미실행 분기가 (http_code=$(field "$WORK/br_dry" http_code), curl_rc=$(field "$WORK/br_dry" curl_rc)) — 미관측이 관측치로 위장"
fi
# 음성 대조 — sentinel 을 000 으로 바꾼 변형본에서 같은 단언이 실패해야 한다.
mutate MS "$(printf 'HTTP_CODE="not-executed"\tHTTP_CODE="000"')" "$(printf 'CURL_RC="not-executed"\tCURL_RC="000"')"
run_fetch "$WORK/MS.yml" "$WORK/ms" BAND_MODE=http
if [ "$(field "$WORK/ms" http_code)" = "not-executed" ]; then
  bad "sentinel/음성 대조" "sentinel 을 000 으로 바꾼 변형본이 여전히 not-executed 로 읽힘 — 검사가 실물을 안 본다"
else
  ok "sentinel/음성 대조: 000 변형본에서 같은 단언이 실패 (판별력 실증, 실측 '$(field "$WORK/ms" http_code)')"
fi

# ═════════════════════════════════════════════════════════════════════════════
# AC-19 — 세 침묵 축. 각 축마다 **변형본에서 같은 단언이 실패**함을 짝으로 세운다.
#   ★ 부재-assert 금지: 2>/dev/null 의 **부재**를 단언하는 것은 교과서적 hollow oracle
#     이다 (-s 단독이 이미 0 바이트를 낸다). -S 의 **실재를 positive 로** 단언한다.
#   ★ 바이트 수 pin 금지 — stderr 길이는 대상 호스트명 길이에 따라 변한다(실측).
# ═════════════════════════════════════════════════════════════════════════════
if [ "$BAND_TRUSTED" = "1" ]; then
  if grep -qF -- 'curl -sS -X GET' "$WORKFLOW"; then
    ok "AC-19/축0: -S(진단 표시)가 argv 에 실재한다 (positive 단언)"
  else
    bad "AC-19/축0" "curl -sS 가 실재하지 않는다 — 진단 억제가 복원됐을 수 있다"
  fi
  # ★ 주석 문면 배제 — AC-4 가 세운 것과 같은 규율이고, 여기엔 그 이유의 **실물**이 있다:
  #   이 workflow 의 정직 주석이 금지 토큰을 **인용**하므로 파일 전체를 훑으면 검사가
  #   자기 주석에 걸려 RED 가 된다(실제로 한 번 그렇게 됐다). 정정문이 그 문자열을
  #   인용해 계수가 늘어나는 형태 — **판정은 계수가 아니라 위치로** 한다.
  #   ★ 정직 범위: 아래 6 토큰만 기계 검사한다. `-i` 는 계약상 금지이나 토큰이 너무
  #     일반적이라(예: `sed -i`) 거짓양성 없이 검사할 수 없다 — 리뷰 판정면으로 남긴다.
  forbidden_opts() { # <workflow> → 검출된 금지 옵션 목록 (없으면 빈 문자열)
    local wf="$1" o out=""
    grep -v '^[[:space:]]*#' "$wf" > "$WORK/nc.txt" || true
    for o in '%{json}' '%{header_json}' ' -v ' ' --trace' ' -D ' ' -L '; do
      if grep -qF -- "$o" "$WORK/nc.txt"; then out="$out $o"; fi
    done
    printf '%s' "$out"
  }
  BADOPT="$(forbidden_opts "$WORKFLOW")"
  if [ -z "$BADOPT" ]; then
    ok "AC-19/argv 계약: 실 argv 에 금지 옵션(%{json}·%{header_json}·-v·--trace·-D·-L) 0"
  else
    bad "AC-19/argv 계약" "금지 옵션 검출:$BADOPT"
  fi
  # 판별력 — 주석 배제가 검사를 **공허하게** 만들지 않았음을 실증한다.
  #   실 argv 에 금지 옵션을 넣은 변형본은 반드시 검출돼야 한다.
  mutate V5 "$(printf 'curl -sS -X GET\tcurl -sS -v -X GET')"
  if [ -n "$(forbidden_opts "$WORK/V5.yml")" ]; then
    ok "AC-19/argv 계약 판별력: argv 에 -v 를 넣은 변형본이 검출됨 (주석 배제 후에도 살아있다)"
  else
    bad "AC-19/argv 계약 판별력" "금지 옵션을 실 argv 에 넣었는데 검출되지 않는다 — 주석 배제가 검사를 공허하게 만들었다"
  fi

  if curl_diag_present "$WORK/ac5t"; then
    ok "AC-19/축1: transport 실패에서 실행 대상이 생성한 curl 진단이 표면에 실재"
  else
    bad "AC-19/축1" "curl 자기 진단이 표면에 없다 (손저작 배제 후 잔여: $(foreign_diag "$WORK/ac5t" | head -1))"
  fi
  mutate V1 "$(printf 'curl -sS -X GET\tcurl -s -X GET')"
  run_fetch "$WORK/V1.yml" "$WORK/v1" BAND_MODE=transport $CRED
  if curl_diag_present "$WORK/v1"; then
    bad "AC-19/축1 판별력" "-s 단독 변형본에서도 같은 단언이 통과 — 검사가 진단 억제를 못 잡는다"
  else
    ok "AC-19/축1 판별력: -s 단독 변형본에서 같은 단언이 실패"
  fi
  mutate V2 "$(printf -- '-o comments_raw.json) || CURL_RC=$?\t-o comments_raw.json 2>/dev/null) || CURL_RC=$?')"
  run_fetch "$WORK/V2.yml" "$WORK/v2" BAND_MODE=transport $CRED
  if curl_diag_present "$WORK/v2"; then
    bad "AC-19/축2 판별력" "curl stderr 폐기 변형본에서도 같은 단언이 통과"
  else
    ok "AC-19/축2 판별력: curl stderr 폐기 복원 변형본에서 같은 단언이 실패"
  fi
  run_fetch "$WORKFLOW" "$WORK/ac19p" BAND_MODE=http BAND_CODE=200 BAND_BODY="$FX/errshape.json" $CRED
  if parse_diag_present "$WORK/ac19p"; then
    ok "AC-19/축3: 파싱 열화 분기의 실행 대상 생성 진단이 표면에 실재"
  else
    bad "AC-19/축3" "파싱 진단이 표면에 없다"
  fi
  mutate V3 "$(printf "sed 's/^/[parse-error] /' parse_err.txt >&2 2>/dev/null || true\tsed 's/^/[parse-error] /' parse_err.txt >/dev/null 2>&1 || true")"
  run_fetch "$WORK/V3.yml" "$WORK/v3" BAND_MODE=http BAND_CODE=200 BAND_BODY="$FX/errshape.json" $CRED
  if parse_diag_present "$WORK/v3"; then
    bad "AC-19/축3 판별력" "parse 진단 폐기 변형본에서도 같은 단언이 통과"
  else
    ok "AC-19/축3 판별력: parse 진단 폐기 복원 변형본에서 같은 단언이 실패"
  fi
else
  bad "AC-19" "band-fidelity 미성립 — 대역 기반 판정을 계상하지 않는다 (fail-closed)"
fi

# ═════════════════════════════════════════════════════════════════════════════
# §4.3 STEP_SUMMARY 정직 1줄 — positive 실재 단언 + 음성 대조
#   ★ 정직 등급 = E-11 형 (E-18): 이 leg 을 삭제해도 RED 로 전환되는 AC 는 **0**.
#     AC-4 ③ 은 GITHUB_OUTPUT 키 집합을 재고 GITHUB_STEP_SUMMARY 는 별 스트림이라
#     이 축을 읽지 않는다. 「AC 가 기계 보존」으로 쓰지 않는다.
# ═════════════════════════════════════════════════════════════════════════════
HONEST_SENTENCE="이 표면은 실행된 run 만 기술한다"
run_summary() { # <workflow> <outdir>
  local wf="$1" d="$2"
  rm -rf "$d"; mkdir -p "$d"; : > "$d/summary.md"; : > "$d/out.txt"
  if ! python3 "$WORK/extract.py" "$wf" "$d/sum.sh" "Surface verdict to GitHub STEP_SUMMARY" 2> "$d/extract.err"; then
    echo "EXTRACT_FAIL" > "$d/summary.md"; return 0
  fi
  (
    cd "$d" && env -u GITHUB_OUTPUT -u GITHUB_STEP_SUMMARY \
      GITHUB_STEP_SUMMARY="$d/summary.md" GITHUB_OUTPUT="$d/out.txt" \
      bash "$d/sum.sh" > "$d/stdout.txt" 2> "$d/stderr.txt"
  ) || true
}
run_summary "$WORKFLOW" "$WORK/sum_base"
if grep -qF -- "$HONEST_SENTENCE" "$WORK/sum_base/summary.md"; then
  ok "§4.3 정직 1줄: 실행 산출 STEP_SUMMARY 에 자기 사각지대 문장이 실재"
else
  bad "§4.3 정직 1줄" "실행 산출에 그 문장이 없다 (침묵을 주제로 하는 변경이 자기 사각지대에 침묵)"
fi
mutate V4 "$(printf 'echo "> 이 표면은 실행된 run 만 기술한다 — 실행되지 않았거나 취소된 tick 은 여기 나타나지 않는다." >> "$GITHUB_STEP_SUMMARY"\t:')"
run_summary "$WORK/V4.yml" "$WORK/sum_mut"
if grep -qF -- "$HONEST_SENTENCE" "$WORK/sum_mut/summary.md"; then
  bad "§4.3 음성 대조" "echo 를 제거한 변형본에서도 문장이 검출됨 — 검사가 실행 산출을 안 본다"
else
  ok "§4.3 음성 대조: 해당 echo 를 제거한 변형본이 RED (판별력 실증)"
fi

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
