#!/usr/bin/env bash
# tests/scripts/test_native_multiplier_stance.sh
# CFP-2984 Phase 2 (구현 lane) — AC-5b discriminating self-test.
#
# 대상 = `skills/rate-limit-429-mitigation/SKILL.md` 의 `native-multiplier-stance` 정본 fence.
#
# 오라클 = 네이티브 재시도 승수(증폭식 `N x M` 의 **N**)에 대한 **명시 입장**이
#          closed 3-enum(`수용` / `상한 재설정` / `관측만`) 중 하나로 기재돼 있는가.
#          **미기재 = 검사 실패(fail-closed).**
#
# 검사 항목 (전건 AND):
#   S1 fence 실재 (부재 = fail-closed RED)
#   S2 `dominant:` 지배 승수 선언 실재 ∧ 그 승수가 stance 행으로 등재
#   S3 요구 승수 2종(`CLAUDE_CODE_MAX_RETRIES` / `CLAUDE_CODE_RETRY_WATCHDOG`) 전건 stance 보유
#   S4 stance 값 전건이 closed 3-enum 원소 (enum 밖 값 = RED)
#   S5 `300` 의 **조건부성** 기재 — watchdog 활성 전제가 명시돼야 한다
#       (E-3d verbatim = "watchdog now raises … to 300 and lifts the cap of 15")
#   S6 지배 승수 = `CLAUDE_CODE_MAX_RETRIES` (기본 상한 15). `300` 을 현행 지배값으로
#       선언하면 위험을 20배 과장한다 → RED
#
# ★ ③ 등가변형(동의 표현으로 산문 서술)은 **enum 값공간이 고정**돼 있어 미해소 → RED.
#   이것이 "산문으로 풀어써도 통과" 를 막는 기제다 (Story §5.3.2 AC-5b 행).
#
# ★ 정직 천장: 본 검사는 **입장이 기재됐는가**를 강제할 뿐 **그 입장이 옳은가**는 판정하지 않는다.
#   `수용` 이 타당한 선택인지는 사람 검토 축이다.
#
# self-contained bash + 순수 픽스처 (INV-T3). Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILL="$REPO_ROOT/skills/rate-limit-429-mitigation/SKILL.md"

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

PASS=0
FAIL=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

ORACLE="$WORK/oracle_5b.py"
cat > "$ORACLE" <<'PYORACLE'
# -*- coding: utf-8 -*-
"""AC-5b 오라클 — 네이티브 재시도 승수 명시 입장 (closed 3-enum).

exit 0 = finding 0.  exit 1 = finding >= 1 (fail-closed 포함).
"""
import argparse
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass

RE_FENCE = re.compile(r"^```([A-Za-z0-9_-]*)\s*$")

STANCE_ENUM = ("수용", "상한 재설정", "관측만")
REQUIRED_MULTIPLIERS = ("CLAUDE_CODE_MAX_RETRIES", "CLAUDE_CODE_RETRY_WATCHDOG")
EXPECTED_DOMINANT = "CLAUDE_CODE_MAX_RETRIES"


def read(path):
    return io.open(path, encoding="utf-8").read()


def fences(text):
    out, cur, info = [], None, None
    for line in text.split("\n"):
        m = RE_FENCE.match(line)
        if m and cur is None:
            cur, info = [], m.group(1)
            continue
        if line.strip() == "```" and cur is not None:
            out.append((info, cur))
            cur, info = None, None
            continue
        if cur is not None:
            cur.append(line)
    return out


def norm(s):
    return re.sub(r"\s+", " ", s.strip().strip("`").strip()).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True)
    args = ap.parse_args()

    text = read(args.skill)
    findings = []

    body = None
    for info, lines in fences(text):
        if info == "native-multiplier-stance":
            body = lines
            break
    if body is None:
        print("FAILCLOSED: S1 `native-multiplier-stance` 정본 fence 부재 — 입장 미기재")
        return 1

    dominant = None
    rows = {}
    for ln in body:
        t = ln.strip()
        if not t or t.startswith("#"):
            continue
        m = re.match(r"^dominant\s*:\s*(.+)$", t)
        if m:
            dominant = norm(m.group(1))
            continue
        parts = [norm(p) for p in t.split("|")]
        if len(parts) != 4:
            findings.append("S1: stance 행 형식 위반 (4열 아님): %r" % (t,))
            continue
        rows[parts[0]] = {"value": parts[1], "condition": parts[2], "stance": parts[3]}

    # S2 지배 승수 선언
    if dominant is None:
        findings.append("S2: `dominant:` 지배 승수 선언 부재 (fail-closed)")
    elif dominant not in rows:
        findings.append("S2: 선언된 지배 승수 %r 가 stance 행에 미등재" % dominant)

    # S3 요구 승수 전건 stance 보유
    for mult in REQUIRED_MULTIPLIERS:
        if mult not in rows:
            findings.append("S3: 승수 %s 에 대한 명시 입장 미기재 (fail-closed)" % mult)

    # S4 stance 값공간 (closed 3-enum)
    for mult, row in sorted(rows.items()):
        if row["stance"] not in STANCE_ENUM:
            findings.append(
                "S4: 승수 %s 의 stance %r 가 값공간 밖 (허용 = %s)"
                % (mult, row["stance"], " / ".join(STANCE_ENUM))
            )

    # S5 `300` 조건부성 기재
    watchdog = rows.get("CLAUDE_CODE_RETRY_WATCHDOG")
    if watchdog is not None:
        blob = watchdog["value"] + " " + watchdog["condition"]
        if "300" not in blob:
            findings.append("S5: watchdog 승수 값 `300` 미기재")
        elif not re.search(r"활성|enabled|켜|watchdog", blob, re.I):
            findings.append("S5: `300` 의 발동 조건(watchdog 활성 전제)이 미기재 — 무조건 현행값으로 읽힌다")

    # S6 지배 승수 정합 — `300` 을 현행 지배값으로 선언하면 위험 20배 과장
    if dominant is not None and dominant != EXPECTED_DOMINANT:
        findings.append(
            "S6: 지배 승수 선언 %r != %s — `300` 계열을 현행 지배값으로 두면 증폭 위험을 과장한다"
            % (dominant, EXPECTED_DOMINANT)
        )

    if findings:
        print("\n".join(findings))
        return 1
    print(
        "OK finding=0 (multipliers=%d, dominant=%s, stances=%s)"
        % (len(rows), dominant, ",".join(sorted(r["stance"] for r in rows.values())))
    )
    return 0


sys.exit(main())
PYORACLE

run_case() {
  local name="$1" expected_exit="$2" expect_substr="$3" skill_path="$4"
  local out exit_code=0 ok=1
  out=$("$PY" "$ORACLE" --skill "$skill_path" 2>&1) || exit_code=$?
  # ★ crash-as-RED 차단 (형제 워커 실사건 회귀 방지): 오라클이 예외로 죽어서 난 rc!=0 은
  #   "검출" 이 아니다. 정규식 컴파일 오류 하나로 전 mutant 가 RED 로 보이는 하네스 사망을 막는다.
  case "$out" in
    *Traceback*)
      echo "X FAIL: $name — 오라클 크래시(Traceback). RED 를 검출로 셀 수 없다"
      printf '%s
' "$out" | sed 's/^/       /'
      FAIL=$((FAIL + 1))
      return ;;
  esac
  [ "$exit_code" -eq "$expected_exit" ] || ok=0
  # ★ P2-5 (CFP-2984): 빈 substr = 판정을 exit code 단독에 맡기는 것이다.
  #   크래시는 그 코드를 위조할 수 있으므로(rc≠0 을 ‘검출’ 로 오독), 산출 대조 없는 케이스를
  #   harness 결함으로 끈는다. 현행 호출부는 전건 비어있지 않음(신규 RED 0) — 향후 유입만 차단하는 ratchet.
  if [ -z "$expect_substr" ]; then
    echo "X FAIL: $name — harness 결함: expect_substr 가 비었다(판정이 exit code 단독)"
    FAIL=$((FAIL + 1))
    return
  fi
  case "$out" in *"$expect_substr"*) : ;; *) ok=0 ;; esac
  if [ "$ok" -eq 1 ]; then
    echo "OK PASS: $name (exit $exit_code)"
    PASS=$((PASS + 1))
  else
    echo "X FAIL: $name"
    echo "  expected exit=$expected_exit substr='$expect_substr', got exit=$exit_code"
    echo "  output: $out"
    FAIL=$((FAIL + 1))
  fi
}

mutate() {
  local dest="$1" src="$2" old="$3" new="$4"
  "$PY" - "$src" "$dest" "$old" "$new" <<'PYMUT'
import io
import sys
src, dest, old, new = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
s = io.open(src, encoding="utf-8").read()
assert s.count(old) == 1, ("mutant anchor count != 1", s.count(old), old[:60])
io.open(dest, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
PYMUT
}

echo "── AC-5b: 네이티브 재시도 승수 명시 입장 (closed 3-enum)"

# ── TC-C1 clean-input 대조군 (실 정본) ───────────────────────────────────────
run_case "TC-C1 정본 SKILL.md — 0 finding" 0 "finding=0" "$SKILL"

# ── TC-C2 clean-input 대조군 (합성 최소 정본, 다른 enum 값 사용) ────────────
SYN="$WORK/syn_clean.md"
cat > "$SYN" <<'SYNEOF'
# synthetic clean fixture

```native-multiplier-stance
dominant: CLAUDE_CODE_MAX_RETRIES
CLAUDE_CODE_MAX_RETRIES | 기본 상한 15 | 상시 | 상한 재설정
CLAUDE_CODE_RETRY_WATCHDOG | 활성 시 300 | watchdog 활성일 때만 | 관측만
```
SYNEOF
run_case "TC-C2 합성 정본(다른 enum 값 '상한 재설정') — 0 finding" 0 "finding=0" "$SYN"

# ── TC-M1 ① 제거: 입장 fence 삭제 → fail-closed ────────────────────────────
M1="$WORK/m1.md"
mutate "$M1" "$SKILL" '```native-multiplier-stance' '```renamed-away'
run_case "TC-M1 ①제거 입장 fence 삭제 → fail-closed RED" 1 "FAILCLOSED" "$M1"

# ── TC-M1b ① 제거: 승수 1종의 stance 행만 삭제 ──────────────────────────────
M1B="$WORK/m1b.md"
mutate "$M1B" "$SKILL" \
  "CLAUDE_CODE_RETRY_WATCHDOG | 활성 시 300 (15 cap 해제) | watchdog 활성일 때만 — 호스트 env·settings 둘 다 미설정 실측 | 관측만" \
  "# (행 삭제됨)"
run_case "TC-M1b ①제거 승수 1종 입장 삭제 → S3 RED" 1 "S3:" "$M1B"

# ── TC-M2 ② 주입: enum 밖 값 기입 ──────────────────────────────────────────
M2="$WORK/m2.md"
mutate "$M2" "$SKILL" \
  "상시 (현 지배 승수) | 수용" \
  "상시 (현 지배 승수) | 추후 검토"
run_case "TC-M2 ②주입 enum 밖 stance 값 → S4 RED" 1 "S4:" "$M2"

# ── TC-M3 ③ 등가변형: 동의 표현 산문으로 풀어씀 → enum 미해소 ──────────────
M3="$WORK/m3.md"
mutate "$M3" "$SKILL" \
  "CLAUDE_CODE_MAX_RETRIES | 기본 상한 15 | 상시 (현 지배 승수) | 수용" \
  "우리는 네이티브 기본 상한 15 를 그대로 받아들이기로 한다 (별도 조정 없음)."
run_case "TC-M3 ③등가변형 산문 서술 → 값공간 미해소 → S3 RED" 1 "S3:" "$M3"

# ── TC-M3b ③ 등가변형: stance 값을 동의어로 개명 ───────────────────────────
M3B="$WORK/m3b.md"
mutate "$M3B" "$SKILL" "상시 (현 지배 승수) | 수용" "상시 (현 지배 승수) | 그대로 수락"
run_case "TC-M3b ③등가변형 stance 동의어 개명 → 값공간 고정이라 RED" 1 "S4:" "$M3B"

# ── TC-M4 ② 주입: `300` 의 조건부성 제거 (무조건 현행값처럼 기재) ──────────
M4="$WORK/m4.md"
mutate "$M4" "$SKILL" \
  "CLAUDE_CODE_RETRY_WATCHDOG | 활성 시 300 (15 cap 해제) | watchdog 활성일 때만 — 호스트 env·settings 둘 다 미설정 실측 | 관측만" \
  "CLAUDE_CODE_RETRY_WATCHDOG | 300 | 상시 | 관측만"
run_case "TC-M4 ②주입 300 조건부성 제거(무조건 현행값 표기) → S5 RED" 1 "S5:" "$M4"

# ── TC-M5 ② 주입: 지배 승수를 watchdog 으로 오선언 (위험 20배 과장) ────────
M5="$WORK/m5.md"
mutate "$M5" "$SKILL" "dominant: CLAUDE_CODE_MAX_RETRIES" "dominant: CLAUDE_CODE_RETRY_WATCHDOG"
run_case "TC-M5 ②주입 지배 승수 오선언 → S6 RED" 1 "S6:" "$M5"

# ── TC-M6 ① 제거: `dominant:` 선언 삭제 ────────────────────────────────────
M6="$WORK/m6.md"
mutate "$M6" "$SKILL" "dominant: CLAUDE_CODE_MAX_RETRIES" "# dominant 선언 삭제됨"
run_case "TC-M6 ①제거 지배 승수 선언 삭제 → S2 RED" 1 "S2:" "$M6"

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
