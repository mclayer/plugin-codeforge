#!/usr/bin/env bash
# tests/scripts/test_nontest_script_execution_liveness.sh
# CFP-2984 Phase 2 (구현 lane) — AC-12b discriminating self-test.
#
# AC-12b: ADR-151 인벤토리 **정의역 밖**(= tests/scripts/*.sh 가 아닌) 신설 검사 스크립트에
#   실행 workflow step 이 존재하는지 검사한다. 실행자 0건 = RED. 실행 step 제거 변이체 = RED.
#
# ★ 재발명 아님(정의역 disjoint)의 **실행 증명** — 선언이 아니라 실측:
#   ADR-151 메타게이트(scripts/check-selftest-execution-liveness.sh)는
#   `tests_dir.glob("*.sh")` 비재귀 1:1 bijection 이라 `scripts/*.sh` 를 **구조적으로 못 본다**.
#   본 self-test 는 같은 픽스처에서 (a) ADR-151 게이트 verdict 불변(blind) ∧ (b) 본 프로브 verdict
#   0→1 전환(sees) 을 **동시에** 확인해 두 정의역이 disjoint 임을 결박한다 (DJ-1/DJ-2).
#
# ★ "존재 ≠ 실행" (본 repo 실사건 — CFP-2976: pytest 3종의 유일 등장처가 주석 1줄):
#   프로브는 YAML/shell 주석을 제거한 뒤에만 경로 토큰을 찾고, live trigger 없는 workflow 는
#   실행자로 세지 않는다. 두 협착이 load-bearing 임을 EQ-decoy / DEAD 케이스가 실증한다.
#
# 대조군 필수(§8.2-E INV-T4): 무조건-RED 프로브는 모든 mutant 를 kill 하면서 통과한다.
#   → BASE-1(직접 호출) · EQ-var · EQ-uses · RC(실 코퍼스 positive control) 4종이 GREEN 대조군.
#
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail

# Windows 로컬 견고성: python helper stdout 를 utf-8 로 고정 (CI=Linux 는 utf-8 기본).
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ADR151_GATE="$REPO_ROOT/scripts/check-selftest-execution-liveness.sh"

# AC-12b 대상 = ADR-151 정의역 밖 **신설** 검사 스크립트 (Change Plan §8.1 RTM 실측 = 1본).
TARGETS=("scripts/check-salvage-bundle.sh")
# 실 코퍼스 positive control = 이미 실행 배선된 정의역 밖 검사 스크립트(프로브가 항상-0 이 아님을 실증).
CONTROL_TARGET="scripts/check-selftest-execution-liveness.sh"

PASS=0
FAIL=0

TMPROOT="$(mktemp -d)"
trap 'rm -rf "$TMPROOT"' EXIT

PROBE="$TMPROOT/liveness_probe.py"

# ─────────────────────────────────────────────────────────────────────────────
# 프로브 — 정의역 밖 스크립트의 workflow 실행자 해소 (호출 그래프 1-hop)
# ─────────────────────────────────────────────────────────────────────────────
cat > "$PROBE" <<'PYEOF'
#!/usr/bin/env python3
"""AC-12b probe — ADR-151 정의역 밖 검사 스크립트의 workflow 실행자 해소.

실행자(executor) 정의 = 아래 3조건 AND 인 `.github/workflows/<f>.yml` 1건:
  (1) live trigger 보유 — push | pull_request | schedule | workflow_dispatch
      (workflow_call 전용 = 호출자 미해소 → 실행자로 세지 않는다. 천장 declare.)
  (2) **주석 제거 후** 본문(∪ `uses: ./<local>` 복합 액션 1-hop 확장)에 target 경로 토큰 등장
  (3) `.github/workflows` 실파일 — `templates/github-workflows` 사본은 실행자 아님

주석 제거가 load-bearing: "유일 등장처 = 주석 1줄" 은 실행자 0건이다.
경로 토큰 매칭이라 `run:` 직접호출 / 변수 경유 / 복합 액션 경유 3형태를 모두 1로 집계한다.

천장(over-claim 금지): 1-hop 로컬 액션까지만 해소한다(중첩 액션·reusable workflow 호출자 역추적·
`if:` 조건부 skip·runner label 부재는 미해소). "실행자 1건" = 정적 호출 그래프상 도달 가능일 뿐
"실제로 매 PR 에서 실행됨" 의 증명이 아니다.
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except Exception:  # pragma: no cover - PyYAML 부재 = 판정불가 = fail-closed
    yaml = None

LIVE_TRIGGERS = {"push", "pull_request", "schedule", "workflow_dispatch"}


def strip_comments(text):
    """YAML/shell 주석 제거 — 따옴표 밖 '#' 이후를 폐기(전각 라인·inline 공통)."""
    out = []
    for line in text.splitlines():
        buf = []
        quote = None
        for ch in line:
            if quote:
                buf.append(ch)
                if ch == quote:
                    quote = None
                continue
            if ch in ("'", '"'):
                quote = ch
                buf.append(ch)
                continue
            if ch == "#":
                break
            buf.append(ch)
        out.append("".join(buf))
    return "\n".join(out)


def triggers_of(raw):
    """raw YAML 에서 on: 트리거 이름 집합. 파싱 실패 = 빈 집합(fail-closed)."""
    if yaml is None:
        return set()
    try:
        data = yaml.safe_load(raw)
    except Exception:
        return set()
    if not isinstance(data, dict):
        return set()
    node = data.get("on", data.get(True))  # YAML 1.1: bare `on:` 은 boolean True 키로 파싱된다
    if node is None:
        return set()
    if isinstance(node, str):
        return {node}
    if isinstance(node, list):
        return {str(x) for x in node}
    if isinstance(node, dict):
        return {str(k) for k in node}
    return set()


_SCRIPT_REF = re.compile(r"(?:tests|scripts)/[A-Za-z0-9_./-]+\.(?:sh|py)")


def _referenced_scripts(body):
    """workflow 본문(주석 제거 후)이 직접 언급하는 repo 스크립트 경로 — 2-hop 진단 전용."""
    return _SCRIPT_REF.findall(body)


def expand_local_actions(stripped, repo_root):
    """`uses: ./<path>` 복합 액션 1-hop 확장 — 액션 내부 run: 도 실행자 본문으로 계상."""
    parts = [stripped]
    for line in stripped.splitlines():
        s = line.strip()
        if not s.startswith("uses:"):
            continue
        val = s[len("uses:"):].strip().strip("'\"")
        if not val.startswith("./"):
            continue
        base = repo_root / val[2:]
        for cand in ("action.yml", "action.yaml"):
            p = base / cand
            if p.is_file():
                parts.append(strip_comments(p.read_text(encoding="utf-8", errors="replace")))
    return "\n".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser(description="AC-12b non-test script execution liveness probe")
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--target", action="append", default=[])
    args = ap.parse_args(argv)

    root = Path(args.repo_root).resolve()
    if not args.target:
        print("::error::[AC-12b] target 0건 — vacuous 판정 금지 (fail-closed)", file=sys.stderr)
        return 1

    live = []
    wfdir = root / ".github" / "workflows"
    if wfdir.is_dir():
        files = sorted(list(wfdir.glob("*.yml")) + list(wfdir.glob("*.yaml")))
        for p in files:
            raw = p.read_text(encoding="utf-8", errors="replace")
            if not (triggers_of(raw) & LIVE_TRIGGERS):
                continue
            live.append((p.name, expand_local_actions(strip_comments(raw), root)))

    rc = 0
    for t in args.target:
        tn = t.replace("\\", "/")
        if not (root / tn).is_file():
            print(f"::error::[AC-12b] {tn}: 대상 스크립트 실파일 부재 — 판정불가(fail-closed)",
                  file=sys.stderr)
            print(f"EXECUTORS {tn} 0 -")
            rc = 1
            continue
        hits = [name for name, body in live if tn in body]
        print(f"EXECUTORS {tn} {len(hits)} {','.join(hits) if hits else '-'}")
        if not hits:
            # 진단 전용(verdict 무영향) — workflow 가 직접 실행하는 repo 스크립트가 target 을
            # 간접 호출하는가(2-hop). 판정은 **직접 실행자**로만 한다(설계 §5.3.2 3형태 = hop-1).
            # 이 줄은 "왜 0 인가" 를 구분해 준다: 완전 미실행 vs 자가-테스트 경유 간접 실행.
            indirect = []
            for name, body in live:
                for cand in sorted(set(_referenced_scripts(body))):
                    p = root / cand
                    if not p.is_file() or cand == tn:
                        continue
                    try:
                        inner = strip_comments(p.read_text(encoding="utf-8", errors="replace"))
                    except OSError:
                        continue
                    if tn in inner:
                        indirect.append(f"{name}→{cand}")
            print(f"INDIRECT {tn} {len(indirect)} {','.join(indirect) if indirect else '-'}")
            print(f"::error::[AC-12b] {tn}: 실행 workflow step 0건 "
                  f"(silent-un-run — 주석 언급·dead workflow 는 실행자 아님)", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
PYEOF

# ─────────────────────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────────────────────
ok() {
  echo "OK PASS: $1"
  PASS=$((PASS+1))
}

ng() {
  echo "X FAIL: $1"
  shift
  for l in "$@"; do echo "    $l"; done
  FAIL=$((FAIL+1))
}

# ─────────────────────────────────────────────────────────────────────────────
# ★ crash-as-RED 차단 (CFP-2984 G7 감사 — 실사건 회귀 방지)
#   프로브가 예외로 죽으면 rc=1 이 되는데, want=1 인 케이스(M1·M2·EQ-c·EQ-d·DJ-2)는 그것을
#   그대로 "검출했다" 로 계상한다 — 아무것도 안 보고 만점. 크래시는 검출이 아니다.
#   ★ 실사건: AC-11b 오라클의 무효 정규식으로 전 케이스가 크래시했는데 mutant 7종이 전부
#     "RED"= killed 로 계상될 뻔했다.
#   ★ SyntaxError·IndentationError 는 Traceback 머리글 없이 출력된다(실측) — 함께 본다.
# ─────────────────────────────────────────────────────────────────────────────
crash_marker() { # <output> → 0 = 크래시 흔적 있음
  case "$1" in
    *Traceback*|*SyntaxError*|*IndentationError*|*TabError*) return 0 ;;
  esac
  return 1
}

# probe_case <name> <expected_rc> <repo-root> <target...>
probe_case() {
  local name="$1" want="$2" root="$3"; shift 3
  local args=() t out rc=0
  for t in "$@"; do args+=(--target "$t"); done
  out=$(python3 "$PROBE" --repo-root "$root" "${args[@]}" 2>&1) || rc=$?
  if crash_marker "$out"; then
    ng "$name — 프로브 크래시(예외). rc≠0 을 검출로 셀 수 없다" "$out"
    return
  fi
  # 무증거 RED 차단 — rc≠0 인데 실행자 집계(EXECUTORS) 근거 라인이 없으면 판정 불가.
  if [ "$rc" -ne 0 ] && ! printf '%s' "$out" | grep -q '^EXECUTORS'; then
    ng "$name — RED 인데 판정 근거(EXECUTORS 집계)가 없다 (무증거 RED)" "$out"
    return
  fi
  if [ "$rc" -eq "$want" ]; then
    ok "$name (rc=$rc) — $(printf '%s' "$out" | grep '^EXECUTORS' | tr '\n' ';')"
  else
    ng "$name" "expected rc=$want, got rc=$rc" "$out"
  fi
}

# mk_fixture <dir> <variant>
#   variant: direct | removed | decoy | var | uses | dead | orphan
mk_fixture() {
  local d="$1" variant="$2"
  mkdir -p "$d/scripts" "$d/.github/workflows" "$d/tests/scripts"
  printf '#!/usr/bin/env bash\necho check-x\n' > "$d/scripts/check-x.sh"

  local trigger="  push:
    branches: [main]
  pull_request:
    branches: [main]"
  [ "$variant" != "dead" ] || trigger="  workflow_call:"

  local step
  case "$variant" in
    direct|orphan)
      step="      - name: run check-x
        run: bash scripts/check-x.sh" ;;
    removed)
      step="      - name: unrelated
        run: echo nothing-runs-the-target" ;;
    decoy)
      # ★ 유일 등장처가 주석 1줄 (CFP-2976 실사건 형태) — 실행자 0 이어야 한다.
      step="      - name: unrelated
        run: |
          # bash scripts/check-x.sh  (과거 배선 흔적 — 실행 아님)
          echo nothing-runs-the-target" ;;
    var)
      step="      - name: run via variable
        run: |
          S=scripts/check-x.sh
          bash \"\$S\"" ;;
    uses)
      mkdir -p "$d/.github/actions/runx"
      printf 'name: runx\nruns:\n  using: composite\n  steps:\n    - shell: bash\n      run: bash scripts/check-x.sh\n' \
        > "$d/.github/actions/runx/action.yml"
      step="      - name: run via composite action
        uses: ./.github/actions/runx" ;;
    dead)
      step="      - name: run check-x
        run: bash scripts/check-x.sh" ;;
  esac

  {
    printf 'name: fixture\n\non:\n%s\n\njobs:\n  j:\n    runs-on: ubuntu-latest\n    steps:\n' "$trigger"
    printf '      - uses: actions/checkout@v4\n'
    printf '%s\n' "$step"
  } > "$d/.github/workflows/ci.yml"

  if [ "$variant" = "orphan" ]; then
    printf '#!/usr/bin/env bash\necho check-y\n' > "$d/scripts/check-y.sh"
  fi
}

echo "═══════════════════════════════════════════════════════════════════════════"
echo " CFP-2984 AC-12b: 정의역 밖 검사 스크립트 실행 liveness — discriminating self-test"
echo "═══════════════════════════════════════════════════════════════════════════"
echo
echo "── baseline 대조군 (실행 step 실재 → GREEN) ──"

F_DIRECT="$TMPROOT/f-direct"; mk_fixture "$F_DIRECT" direct
probe_case "BASE-1 baseline: run: 직접 호출 → 실행자 1 (GREEN)" 0 "$F_DIRECT" scripts/check-x.sh

echo
echo "── ① 제거 mutant (실행 step 삭제 → RED 전환) ──"

F_REMOVED="$TMPROOT/f-removed"; mk_fixture "$F_REMOVED" removed
probe_case "M1 제거: 실행 step 삭제 → 실행자 0 (RED)" 1 "$F_REMOVED" scripts/check-x.sh

echo
echo "── ② 주입 mutant (실행자 없는 스크립트 1본 추가 → RED 전환) ──"

F_ORPHAN="$TMPROOT/f-orphan"; mk_fixture "$F_ORPHAN" orphan
probe_case "M2 주입: 실행자 있는 1본 + 없는 1본 → RED" 1 "$F_ORPHAN" scripts/check-x.sh scripts/check-y.sh
# 같은 픽스처에서 실행자 있는 쪽만 물으면 GREEN — 무조건-RED 아님을 결박(대조 축).
probe_case "M2-대조: 같은 픽스처, 실행자 보유 target 만 → GREEN" 0 "$F_ORPHAN" scripts/check-x.sh

echo
echo "── ③ 등가변형 mutant (표기 변경 — 호출 그래프 해소로 3형태 모두 실행자 1) ──"

F_VAR="$TMPROOT/f-var"; mk_fixture "$F_VAR" var
probe_case "EQ-a 변수 경유(S=path; bash \$S) → 실행자 1 (거짓 RED 없음)" 0 "$F_VAR" scripts/check-x.sh

F_USES="$TMPROOT/f-uses"; mk_fixture "$F_USES" uses
probe_case "EQ-b 복합 액션 경유(uses: ./…/action.yml) → 실행자 1 (1-hop 해소)" 0 "$F_USES" scripts/check-x.sh

# ★ 우회 방향 등가변형: 실행 step 을 지우고 **주석 1줄**만 남긴다(문자열은 그대로 등장).
#   리터럴 grep 오라클이면 여기서 GREEN 이 나와 hollow 가 된다 → MUST RED.
F_DECOY="$TMPROOT/f-decoy"; mk_fixture "$F_DECOY" decoy
probe_case "EQ-c decoy: 유일 등장처가 주석 1줄 → 실행자 0 (RED — 존재≠실행)" 1 "$F_DECOY" scripts/check-x.sh

# ★ dead workflow: 실행 step 은 있으나 live trigger 부재 → 실행자 0.
F_DEAD="$TMPROOT/f-dead"; mk_fixture "$F_DEAD" dead
probe_case "EQ-d dead workflow(workflow_call 전용) → 실행자 0 (RED)" 1 "$F_DEAD" scripts/check-x.sh

echo
echo "── 정의역 disjoint 실증 (재발명 아님 — ADR-151 게이트는 이 축을 못 본다) ──"

# 픽스처 D: ADR-151 게이트가 **PASS** 하는 최소 코퍼스(bijection 성립 + META 레코드 alive).
DJ="$TMPROOT/dj"
mkdir -p "$DJ/tests/scripts" "$DJ/docs"
printf '#!/usr/bin/env bash\nexit 0\n' > "$DJ/tests/scripts/test_check-selftest-execution-liveness.sh"
cat > "$DJ/docs/selftest-execution-liveness-inventory.yaml" <<'YEOF'
self_tests:
  - self_test: tests/scripts/test_check-selftest-execution-liveness.sh
    execution_channel: manual_registered
    channel_status: alive
    blocking_tier: manual
    discriminating_fixture: present
    l2_full_scope: "N/A"
    manual_reason: "AC-12b 정의역 disjoint 실증 전용 픽스처 레코드이며 실 채널이 아니다(테스트 임시 코퍼스)."
    g_boundary_check: "runtime 축(soak/DAST/real-render) 무침범 — 정적 픽스처 전용."
YEOF

dj_before_rc=0
dj_before=$(bash "$ADR151_GATE" --repo-root "$DJ" \
  --inventory "$DJ/docs/selftest-execution-liveness-inventory.yaml" 2>&1) || dj_before_rc=$?

# 정의역 밖 스크립트 1본 추가 — 실행자 0건(픽스처에 workflow 자체가 없다).
mkdir -p "$DJ/scripts"
printf '#!/usr/bin/env bash\necho fixture-check\n' > "$DJ/scripts/check-fixture-thing.sh"

dj_after_rc=0
dj_after=$(bash "$ADR151_GATE" --repo-root "$DJ" \
  --inventory "$DJ/docs/selftest-execution-liveness-inventory.yaml" 2>&1) || dj_after_rc=$?

# DJ-1: ADR-151 게이트는 판정 가능한 상태(rc=0 PASS)에서 **verdict·출력 불변** = blind.
#   (판정불가 상태에서의 불변은 무의미하므로 rc=0 을 함께 결박한다 — verdict-invariant 함정 회피.)
if [ "$dj_before_rc" -eq 0 ] && [ "$dj_after_rc" -eq 0 ] && [ "$dj_before" = "$dj_after" ]; then
  ok "DJ-1 ADR-151 게이트: 정의역 밖 스크립트 추가 전후 verdict 불변(rc=0→0, 출력 동일) = 구조적 blind"
else
  ng "DJ-1 ADR-151 게이트 blind 실증 실패" \
     "before rc=$dj_before_rc / after rc=$dj_after_rc" \
     "before: $dj_before" "after: $dj_after"
fi

# DJ-2: 같은 전이에서 본 프로브는 0→1 (sees). 두 게이트의 정의역이 disjoint.
dj_probe_before_rc=0
python3 "$PROBE" --repo-root "$DJ" --target tests/scripts/test_check-selftest-execution-liveness.sh \
  >/dev/null 2>&1 || dj_probe_before_rc=$?
dj_probe_after_rc=0
dj_probe_after=$(python3 "$PROBE" --repo-root "$DJ" --target scripts/check-fixture-thing.sh 2>&1) \
  || dj_probe_after_rc=$?
if [ "$dj_probe_after_rc" -eq 1 ]; then
  ok "DJ-2 본 프로브: 같은 픽스처의 정의역 밖 스크립트를 실행자 0건으로 검출(rc=1) = sees"
else
  ng "DJ-2 본 프로브가 정의역 밖 스크립트를 못 봄" "rc=$dj_probe_after_rc" "$dj_probe_after"
fi

echo
echo "── 실 코퍼스 (positive control + AC-12b 대상) ──"

# RC: 이미 실행 배선된 정의역 밖 검사 스크립트 → 실행자 ≥1 (프로브가 항상-0 이 아님을 실증).
probe_case "RC positive control: $CONTROL_TARGET → 실행자 ≥1 (GREEN)" 0 "$REPO_ROOT" "$CONTROL_TARGET"

# AC-12b 본체: 신설 대상 전건 실행자 ≥1.
probe_case "AC-12b 실 코퍼스: ${TARGETS[*]} → 실행자 ≥1" 0 "$REPO_ROOT" "${TARGETS[@]}"

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo " Test Summary"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "PASS: $PASS"
echo "FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "OK All $PASS cases pass — 실행자 해소/주석-decoy/dead-workflow/정의역 disjoint 결박"
  exit 0
else
  echo "X $FAIL case(s) failed"
  exit 1
fi
