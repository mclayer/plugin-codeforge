#!/usr/bin/env bash
# tests/scripts/test_intensity_branch_no_silent_zero.sh
# CFP-2984 Phase 2 (구현 lane) — AC-24 discriminating self-test.
#
# 대상 = `skills/rate-limit-429-mitigation/SKILL.md` Decision tree 의 **강도(intensity) 판정 분기**
#        (외부 데이터원 = `docs/kpi/429-incident-history.jsonl`).
#
# 오라클 2축 (전건 AND):
#   [계산축] 분기를 **순수 함수**로 구현해 데이터원 부재 3형태를 먹인다 —
#            파일 없음 / 빈 파일 / DATA 행 0(빈 배열). 세 형태 모두 **"부재" 로 정규화**되고,
#            그 결과가 `low`(intensity 0) 와 **구분**돼야 한다. 부재를 0 으로 삼키면 RED.
#   [문면축] 문서가 그 부재 분기와 **명시 보고**를 실제로 지시하는가 (부재 = fail-closed RED).
#
# ★ 왜 이 AC 가 필요한가 (ADR-109 §결정 4 Amendment 3 telemetry-gated 재선언):
#   그 데이터원의 기계 append 경로가 **0건**이라 count 는 항구적으로 0 이다. 부재를 Low 로
#   낙하시키면 "관측 결과 한산함" 과 "관측 자체가 없음" 이 구분 불가해진다 = silent-zero.
#
# ★ 대조군 없는 오라클 = hollow: TC-C* 가 정상 데이터에서 low/medium/high 가 **정상 산출**됨을
#   확인한다. 없으면 "무조건 absent 반환" 구현이 mutant 를 전부 kill 하면서 통과한다.
#
# ★ 정직 천장: 본 검사는 **문서가 지시하는 분기 계약**을 모델링한 순수 함수 위에서 판정한다.
#   Orchestrator 가 런타임에 그 계약을 실제로 따르는지는 정적으로 확인 불가 — 사람 검토 잔여다.
#
# self-contained bash + 순수 픽스처 (INV-T3: 네트워크 0 · 실 ~/.claude 0 · 실 git 원격 0).
# Exit 0 = 전 케이스 PASS.

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

# ─────────────────────────────────────────────────────────────────────────────
# [계산축] SUT = 문서가 지시하는 분기 계약의 순수 함수 모델
# ─────────────────────────────────────────────────────────────────────────────
SUT="$WORK/intensity_branch.py"
cat > "$SUT" <<'PYSUT'
# -*- coding: utf-8 -*-
"""강도 판정 분기 (SUT) — 데이터원 부재를 침묵으로 삼키지 않는다.

classify(source) -> (bucket, reported)
  source: None(파일 없음) | ""(빈 파일) | "[]"(빈 배열) | JSONL 본문
  bucket ∈ {"absent", "low", "medium", "high"}
  reported: bool — 데이터원 부재를 **명시 보고**했는가
"""
import json


def datasource_absent(source):
    """부재 3형태 정규화: 파일 없음 / 빈 파일 / DATA 행 0(빈 배열 포함)."""
    if source is None:
        return True
    if source.strip() == "":
        return True
    if source.strip() in ("[]", "{}"):
        return True
    return count_rows(source) is None


def count_rows(source):
    """DATA 행 수. 파싱 가능한 행이 0이면 None(= 부재로 정규화)."""
    rows = 0
    for line in source.split("\n"):
        t = line.strip()
        if not t or t.startswith("#"):
            continue
        if t in ("[]", "{}"):
            continue
        try:
            json.loads(t)
        except ValueError:
            continue
        rows += 1
    return rows if rows > 0 else None


def classify(source):
    if datasource_absent(source):
        # 명시 보고 + Low 와 구분되는 별 bucket. `low` 로 낙하 금지.
        return ("absent", True)
    n = count_rows(source)
    if n == 1:
        return ("medium", False)
    if n >= 2:
        return ("high", False)
    return ("low", False)
PYSUT

RUNNER="$WORK/run_branch.py"
cat > "$RUNNER" <<'PYRUN'
# -*- coding: utf-8 -*-
import importlib.util
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass

spec = importlib.util.spec_from_file_location("sut", sys.argv[1])
sut = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sut)

ONE = '{"timestamp":"2026-08-15T10:00:00+09:00","retry_count":1}'
TWO = ONE + "\n" + '{"timestamp":"2026-08-15T10:05:00+09:00","retry_count":2}'

CASES = [
    # ③ 등가변형: 부재 3형태 — 표기가 달라도 모두 "부재" 로 정규화돼야 한다
    ("A1-missing-file", None),
    ("A2-empty-file", ""),
    ("A3-empty-array", "[]"),
    ("A4-comment-only", "# header only\n\n"),
    # clean-input 대조군: 정상 데이터에서 분기가 살아 있는가
    ("D1-one-incident", ONE),
    ("D2-two-incidents", TWO),
]

for name, src in CASES:
    bucket, reported = sut.classify(src)
    print("%s|%s|%s" % (name, bucket, "reported" if reported else "silent"))
PYRUN

expect() {
  local out="$1" name="$2" want="$3" label="$4"
  local line
  # ★ crash-as-RED / crash-as-diff 차단: 러너가 크래시하면 grep 이 빈 줄을 내고
  #   expect_not 이 "달라졌다" 며 통과해버린다. 크래시는 무조건 FAIL 이다.
  case "$out" in
    *Traceback*)
      echo "X FAIL: $label — 러너 크래시(Traceback). 산출 차이를 검출로 셀 수 없다"
      FAIL=$((FAIL + 1))
      return ;;
  esac
  line=$(printf '%s\n' "$out" | grep "^$name|" || true)
  if [ "$line" = "$name|$want" ]; then
    echo "OK PASS: $label ($line)"
    PASS=$((PASS + 1))
  else
    echo "X FAIL: $label"
    echo "  expected '$name|$want', got '$line'"
    FAIL=$((FAIL + 1))
  fi
}

expect_not() {
  local out="$1" name="$2" forbidden="$3" label="$4"
  local line
  # ★ crash-as-RED / crash-as-diff 차단: 러너가 크래시하면 grep 이 빈 줄을 내고
  #   expect_not 이 "달라졌다" 며 통과해버린다. 크래시는 무조건 FAIL 이다.
  case "$out" in
    *Traceback*)
      echo "X FAIL: $label — 러너 크래시(Traceback). 산출 차이를 검출로 셀 수 없다"
      FAIL=$((FAIL + 1))
      return ;;
  esac
  line=$(printf '%s\n' "$out" | grep "^$name|" || true)
  if [ "$line" != "$name|$forbidden" ]; then
    echo "OK PASS: $label (got '$line')"
    PASS=$((PASS + 1))
  else
    echo "X FAIL: $label (mutant 가 정본과 동일 산출 — 검출력 0)"
    echo "  line: $line"
    FAIL=$((FAIL + 1))
  fi
}

mutate_sut() {
  local dest="$1" kind="$2"
  "$PY" - "$SUT" "$dest" "$kind" <<'PYMUT'
import io
import sys
src, dest, kind = sys.argv[1], sys.argv[2], sys.argv[3]
s = io.open(src, encoding="utf-8").read()
if kind == "silent_zero":
    # ① 제거: 부재 보고 분기를 지운다 → 부재가 low(0건)로 조용히 낙하.
    old = '    if datasource_absent(source):\n        # 명시 보고 + Low 와 구분되는 별 bucket. `low` 로 낙하 금지.\n        return ("absent", True)'
    new = '    if datasource_absent(source):\n        return ("low", False)'
elif kind == "silent_but_distinct":
    # ② 주입: bucket 은 구분하되 **보고를 침묵**시킨다 (부분 이행 = 미이행).
    old = '        return ("absent", True)'
    new = '        return ("absent", False)'
elif kind == "partial_normalization":
    # ③ 등가변형 저항 제거: 부재 3형태 중 "빈 배열" 표기만 부재 정규화에서 뺀다.
    #   ★ `[]` 는 두 경로(직접 guard + count_rows 스킵)로 부재 판정되므로 **둘 다** 제거해야
    #     실제 검출력 차이가 난다. 한쪽만 지우면 mutant 가 정본과 동일 산출을 내고(= 중복 방어),
    #     그것을 "잡았다" 고 적으면 검사연극이다. 초판이 정확히 그 오류를 냈다.
    old = (
        '    if source.strip() in ("[]", "{}"):\n        return True\n'
    )
    new = "    if False:\n        return True\n"
    assert s.count(old) == 1, ("mutant anchor A count != 1", s.count(old))
    s = s.replace(old, new)
    old = '        if t in ("[]", "{}"):\n            continue'
    new = "        if False:\n            continue"
else:
    raise SystemExit("unknown mutant kind %r" % kind)
assert s.count(old) == 1, ("mutant anchor count != 1", s.count(old), kind)
io.open(dest, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
PYMUT
}

# ─────────────────────────────────────────────────────────────────────────────
# [문면축] 문서가 부재 분기 + 명시 보고를 실제로 지시하는가
# ─────────────────────────────────────────────────────────────────────────────
DOCORACLE="$WORK/oracle_doc.py"
cat > "$DOCORACLE" <<'PYDOC'
# -*- coding: utf-8 -*-
"""문면축 오라클 — Decision tree 가 데이터원 부재 분기와 명시 보고를 지시하는가."""
import argparse
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True)
    args = ap.parse_args()
    text = io.open(args.skill, encoding="utf-8").read()

    # Decision tree 절만 정의역으로 삼는다 (다른 절의 유사 문구로 통과하는 것 차단).
    m = re.search(r"^## Decision tree.*?(?=^## |\Z)", text, re.M | re.S)
    if not m:
        print("FAILCLOSED: `## Decision tree` 절 부재 — 정의역 소실")
        return 1
    section = m.group(0)

    findings = []

    # ★ 판정은 **구조 형태**로 한다 — 단어 presence 로 하면 주석에 그 단어가 남아 있는 한
    #   분기를 지워도 통과한다(presence-only 퇴화). 초판이 정확히 그 오류를 냈고
    #   TC-DOC-M1 / TC-DOC-M3 이 그것을 실행으로 잡았다.
    fence = re.search(r"^```\s*$\n(.*?)^```\s*$", section, re.M | re.S)
    code = fence.group(1) if fence else ""
    if not code.strip():
        findings.append("D0: Decision tree 절에 분기 코드 블록 부재 (fail-closed)")

    # (a) 부재 판정 **분기**(조건문 형태)
    mbranch = re.search(r"^(\s*)if\s+datasource_absent\s*\(", code, re.M)
    if not mbranch:
        findings.append("D1: 데이터원 부재 판정 **분기**(`if datasource_absent(...)`) 부재 — silent-zero 금지 미이행")
        branch_body = ""
    else:
        # 분기 본문 = 조건문 다음 줄부터 들여쓰기가 유지되는 구간
        start = code.index(mbranch.group(0)) + len(mbranch.group(0))
        rest = code[start:].split("\n")[1:]
        indent = len(mbranch.group(1))
        body = []
        for ln in rest:
            if ln.strip() == "":
                body.append(ln)
                continue
            if len(ln) - len(ln.lstrip()) <= indent:
                break
            body.append(ln)
        branch_body = "\n".join(body)

    # (b) 명시 보고 — **분기 본문 안**에 있어야 한다
    if not re.search(r"report\s*\(", branch_body):
        findings.append("D2: 부재 분기 본문 안에 **명시 보고**(`report(...)`) 지시 부재")
    # (c) Low 와 구분되는 별 bucket — **분기 본문 안 대입** 형태
    if not re.search(r'bucket\s*=\s*"unknown_absent_datasource"', branch_body):
        findings.append("D3: 부재 분기 본문에 Low 와 구분되는 전용 bucket 대입 부재")
    # (d) 부재 3형태 정규화 명시
    forms = sum(
        1
        for pat in (r"파일\s*없음|파일\s*부재", r"빈\s*파일", r"DATA\s*행\s*0|빈\s*배열")
        if re.search(pat, section)
    )
    if forms < 3:
        findings.append("D4: 부재 3형태(파일 없음 / 빈 파일 / DATA 행 0) 정규화 명시 %d/3" % forms)

    if findings:
        print("\n".join(findings))
        return 1
    print("OK finding=0 (doc-axis)")
    return 0


sys.exit(main())
PYDOC

doc_case() {
  local name="$1" expected_exit="$2" expect_substr="$3" skill_path="$4"
  local out exit_code=0 ok=1
  out=$("$PY" "$DOCORACLE" --skill "$skill_path" 2>&1) || exit_code=$?
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
  if [ -n "$expect_substr" ]; then
    case "$out" in *"$expect_substr"*) : ;; *) ok=0 ;; esac
  fi
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

mutate_doc() {
  local dest="$1" old="$2" new="$3"
  "$PY" - "$SKILL" "$dest" "$old" "$new" <<'PYMUT'
import io
import sys
src, dest, old, new = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
s = io.open(src, encoding="utf-8").read()
assert s.count(old) == 1, ("mutant anchor count != 1", s.count(old), old[:60])
io.open(dest, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
PYMUT
}

echo "── AC-24: 강도 판정 분기 — 데이터원 부재 silent-zero 금지"

# ── [계산축] baseline (clean-input 대조군 포함) ─────────────────────────────
BASE=$("$PY" "$RUNNER" "$SUT")
expect "$BASE" "A1-missing-file"  "absent|reported" "TC-A1 부재①파일 없음 → absent + 명시 보고"
expect "$BASE" "A2-empty-file"    "absent|reported" "TC-A2 부재②빈 파일 → absent + 명시 보고"
expect "$BASE" "A3-empty-array"   "absent|reported" "TC-A3 부재③빈 배열 → absent + 명시 보고"
expect "$BASE" "A4-comment-only"  "absent|reported" "TC-A4 부재④DATA 행 0 → absent + 명시 보고"
expect "$BASE" "D1-one-incident"  "medium|silent"   "TC-D1 대조군 정상 1건 → medium (분기 생존)"
expect "$BASE" "D2-two-incidents" "high|silent"     "TC-D2 대조군 정상 2건 → high (분기 생존)"

# ★ 대조군의 의미: A* 가 전부 absent 인 것이 "무조건 absent 반환" 때문이 아님을 D1/D2 가 못박는다.

# ── [계산축] ① 제거 mutant: 부재 보고 분기 삭제 → silent-zero ──────────────
M1="$WORK/m1.py"; mutate_sut "$M1" "silent_zero"
M1_OUT=$("$PY" "$RUNNER" "$M1")
expect_not "$M1_OUT" "A1-missing-file" "absent|reported" "TC-M1a ①제거 → A1 RED (부재가 low 로 낙하)"
expect_not "$M1_OUT" "A2-empty-file"   "absent|reported" "TC-M1b ①제거 → A2 RED"
expect_not "$M1_OUT" "A3-empty-array"  "absent|reported" "TC-M1c ①제거 → A3 RED"
# 형제 회귀: 같은 mutant 아래에서도 정상 데이터 분기는 살아 있다 → 검출이 부재 축에서만 발생
expect "$M1_OUT" "D2-two-incidents" "high|silent" "TC-M1d 형제 회귀 — silent-zero mutant 는 정상 분기를 바꾸지 않는다"

# ── [계산축] ② 주입 mutant: bucket 은 구분하되 보고를 침묵 ─────────────────
M2="$WORK/m2.py"; mutate_sut "$M2" "silent_but_distinct"
M2_OUT=$("$PY" "$RUNNER" "$M2")
expect_not "$M2_OUT" "A1-missing-file" "absent|reported" "TC-M2 ②주입 보고 침묵 → A1 RED (부분 이행 = 미이행)"

# ── [계산축] ③ 등가변형 저항 제거: 부재 3형태 중 하나만 정규화에서 뺀다 ────
M3="$WORK/m3.py"; mutate_sut "$M3" "partial_normalization"
M3_OUT=$("$PY" "$RUNNER" "$M3")
expect "$M3_OUT" "A1-missing-file" "absent|reported" "TC-M3a 형제 회귀 — 다른 부재 형태는 여전히 정상"
expect_not "$M3_OUT" "A3-empty-array" "absent|reported" "TC-M3b ③등가변형 빈 배열 정규화 제거 → A3 RED"

# ── [문면축] 대조군 + mutant ───────────────────────────────────────────────
doc_case "TC-DOC-C1 정본 Decision tree — 0 finding" 0 "finding=0" "$SKILL"

D1="$WORK/d1.md"
mutate_doc "$D1" "if datasource_absent(src):" "if False:  # 부재 판정 제거"
doc_case "TC-DOC-M1 ①제거 부재 판정 분기 삭제 → D1 RED" 1 "D1:" "$D1"

D2="$WORK/d2.md"
mutate_doc "$D2" '    report("429 telemetry 데이터원 부재 — intensity 미판정")   # 명시 보고 의무' "    pass"
doc_case "TC-DOC-M2 ①제거 명시 보고 지시 삭제 → D2 RED" 1 "D2:" "$D2"

D3="$WORK/d3.md"
mutate_doc "$D3" '    bucket = "unknown_absent_datasource"    # Low 로 낙하 금지 (부재 != 0건)' '    bucket = "low"'
doc_case "TC-DOC-M3 ②주입 부재를 Low bucket 으로 → D3 RED" 1 "D3:" "$D3"

D4="$WORK/d4.md"
mutate_doc "$D4" "# 데이터원 부재 3형태(파일 없음 / 빈 파일 / DATA 행 0)는 모두 \"부재\" 로 정규화한다." \
  "# 데이터원 부재는 부재로 처리한다."
doc_case "TC-DOC-M4 ①제거 3형태 정규화 명시 삭제 → D4 RED" 1 "D4:" "$D4"

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
