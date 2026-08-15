#!/usr/bin/env bash
# tests/scripts/test_retry_layer_overlap.sh
# CFP-2984 Phase 2 (구현 lane) — AC-5c discriminating self-test.
#
# 대상 = `skills/rate-limit-429-mitigation/SKILL.md` 의 재시도 사다리 레지스트리
#        (native ∪ codeforge 통합) + ADR-109 §결정 1 Amendment 1 (b) 6-literal code-fence.
#
# 오라클 = computed-set 교집합 + 역방향 4 leg (Change Plan §8.2-A):
#   R1 전수성   — 모든 단계가 `층 ∈ {native, codeforge}` 보유 (+ pseudo 사다리 경로 키 전건 등재)
#   R2 앵커 의무 — `층=native` 단계는 mechanism_ref 보유 ∧ 정본 앵커 집합 원소 ∧ axis=retry
#   R3 앵커 유일성 — 한 mechanism_ref 를 2개 이상 native 단계가 주장 불가
#   R4 클래스 정합 — native 단계의 대상 클래스 = 그 앵커가 커버하는 클래스와 일치
#   FWD 교집합  — derived 층=codeforge 단계의 대상 클래스 ∩ native 커버 클래스 = 공집합
#
# ★ hollow 아님의 증명 (§5.1 대조군 + §5.2 3방향 + R3 유일 discriminating 실증):
#   - clean-input 대조군(TC-C1/TC-C2) = 정본 입력 → 0-finding ∧ exit 0. "무조건 RED" 오라클 배제.
#   - TC-M6(M-R(b) 완전 위장) 은 R1·R2·R4·FWD 를 전건 통과하고 **R3 만** 잡는다.
#   - TC-M7 은 같은 입력을 R3 제외 3-leg 로 돌려 **놓치는 것(exit 0)** 을 실행 출력으로 보인다.
#
# ★ 정직 천장 (over-claim 금지 — Change Plan §8.2-A):
#   R1~R4 가 닫는 것은 **중복형 오라벨**뿐이다. **치환형**(문서에 native rung 자체가 없고
#   codeforge 동작 서술 하나만 `native` 로 적힌 경우)은 자연어 의미 판정으로 환원되어 **잔여**이며
#   AC-5(advisory, 사람 검토)에 귀속된다. 본 검사를 "층 오라벨 완전 봉쇄" 로 서술하지 말 것.
#
# self-contained bash + 순수 픽스처 (INV-T3: 네트워크 0 · 실 ~/.claude 0 · 실 git 원격 0).
# Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILL="$REPO_ROOT/skills/rate-limit-429-mitigation/SKILL.md"
ADR109="$REPO_ROOT/archive/adr/ADR-109-in-process-429-mitigation-framework.md"

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

PASS=0
FAIL=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

ORACLE="$WORK/oracle_5c.py"
cat > "$ORACLE" <<'PYORACLE'
# -*- coding: utf-8 -*-
"""AC-5c 오라클 — 재시도 사다리 층 레지스트리 역방향 4 leg + 교집합.

exit 0 = finding 0.  exit 1 = finding >= 1 (fail-closed 포함).
finding 은 `<LEG>: <detail>` 한 줄씩 출력한다.
"""
import argparse
import io
import re
import sys

try:  # Windows 로컬 견고성 — 콘솔 기본 인코딩(cp949)에서 finding 출력이 죽지 않도록.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover - py<3.7 / 비 TextIO
    pass

RE_FENCE = re.compile(r"^```([A-Za-z0-9_-]*)\s*$")


def read(path):
    return io.open(path, encoding="utf-8").read()


def fences(text):
    """(info, [line, ...]) 목록."""
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


def norm_class(s):
    """대상 클래스 토큰 정규화 — 대소문자·공백·백틱·따옴표 등가변형 흡수."""
    s = s.strip().strip("`").strip().strip('"').strip()
    return re.sub(r"\s+", " ", s).lower()


def norm_layer(s):
    return re.sub(r"\s+", "", s.strip().strip("`").strip()).lower()


def norm_anchor(s):
    return re.sub(r"\s+", "", s.strip().strip("`").strip()).upper()


def parse_six_literals(adr_text):
    """ADR-109 §결정 1 Amendment 1 (b) 6-literal code-fence 를 **파싱**한다.

    하드코딩 사본 금지 — fence 를 못 찾으면 fail-closed.
    """
    best = None
    for _info, lines in fences(adr_text):
        vals = []
        ok = True
        for ln in lines:
            t = ln.strip()
            if not t:
                continue
            m = re.match(r'^"(.+)"$', t)
            if not m:
                ok = False
                break
            vals.append(m.group(1))
        if ok and len(vals) == 6:
            best = vals
            break
    return best


def parse_anchor_fence(skill_text):
    """`native-cover-anchor` fence → {anchor: (axis, frozenset(classes))}."""
    for info, lines in fences(skill_text):
        if info != "native-cover-anchor":
            continue
        table = {}
        for ln in lines:
            t = ln.strip()
            if not t or t.startswith("#"):
                continue
            parts = [p.strip() for p in t.split("|")]
            if len(parts) != 3:
                return None, "anchor fence 행 형식 위반: %r" % (t,)
            anchor, axis, classes = parts
            table[norm_anchor(anchor)] = (
                axis.strip().lower(),
                frozenset(norm_class(c) for c in classes.split(",") if c.strip()),
            )
        return table, None
    return None, "`native-cover-anchor` fence 부재"


REQUIRED_COLS = ["slot", "경로 키", "층", "대상 클래스", "tenant", "SSOT", "mechanism_ref"]


def parse_registry(skill_text):
    """레지스트리 markdown 표 → row dict 목록."""
    lines = skill_text.split("\n")
    for i, ln in enumerate(lines):
        if not ln.startswith("|"):
            continue
        header = [c.strip() for c in ln.strip().strip("|").split("|")]
        if [h.lower() for h in header] != [c.lower() for c in REQUIRED_COLS]:
            continue
        if i + 1 >= len(lines) or not re.match(r"^\|[-\s|:]+\|$", lines[i + 1].strip()):
            return None, "레지스트리 표 구분자 행 부재"
        rows = []
        for body in lines[i + 2:]:
            if not body.startswith("|"):
                break
            cells = [c.strip() for c in body.strip().strip("|").split("|")]
            if len(cells) != len(header):
                return None, "레지스트리 표 셀 수 불일치: %r" % (body,)
            rows.append(dict(zip(REQUIRED_COLS, cells)))
        return rows, None
    return None, "레지스트리 표 부재 (헤더 %s 미발견)" % (" / ".join(REQUIRED_COLS),)


RE_PATHKEY_IN_PSEUDO = re.compile(r"경로 키 `([A-Za-z0-9_-]+)`")


def pseudo_path_keys(skill_text):
    """Step 3 사다리 pseudo 블록이 명명한 경로 키 집합 (구조→산문 탈출 차단)."""
    keys = set()
    for _info, body in fences(skill_text):
        joined = "\n".join(body)
        if "attempt 1:" in joined or "attempts 3" in joined:
            keys |= set(RE_PATHKEY_IN_PSEUDO.findall(joined))
    return keys


def derive_layer(row, anchors):
    """`층` 을 행 내용(SSOT 권위 + mechanism_ref)에서 **독립 도출**한다.

    선언 라벨(`층` 열)은 입력으로 쓰지 않는다 — 도출값과 선언을 교차검증하기 위함.
    """
    ssot = row["SSOT"].strip().strip("`")
    ref = norm_anchor(row["mechanism_ref"])
    has_anchor = ref not in ("", "-", "—") and ref in anchors
    harness_authority = bool(re.search(r"harness|CHANGELOG", ssot, re.I))
    codeforge_authority = bool(re.search(r"ADR-\d+|skills/|playbook", ssot, re.I))
    if harness_authority and not codeforge_authority and has_anchor:
        return "native"
    if codeforge_authority and not harness_authority:
        return "codeforge"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True)
    ap.add_argument("--adr109", required=True)
    ap.add_argument("--legs", default="R1,R2,R3,R4,FWD")
    args = ap.parse_args()
    legs = set(x.strip() for x in args.legs.split(",") if x.strip())

    findings = []
    skill_text = read(args.skill)
    adr_text = read(args.adr109)

    six = parse_six_literals(adr_text)
    if not six:
        findings.append("FAILCLOSED: ADR-109 6-literal code-fence 파싱 실패 (하드코딩 사본 금지)")
        print("\n".join(findings))
        return 1
    valid_classes = set(norm_class(x) for x in six)

    anchors, err = parse_anchor_fence(skill_text)
    if anchors is None:
        findings.append("FAILCLOSED: %s" % err)
        print("\n".join(findings))
        return 1

    rows, err = parse_registry(skill_text)
    if rows is None:
        findings.append("FAILCLOSED: %s" % err)
        print("\n".join(findings))
        return 1
    if not rows:
        findings.append("FAILCLOSED: 레지스트리 표에 데이터 행 0")
        print("\n".join(findings))
        return 1

    derived_map = []
    for row in rows:
        key = row["경로 키"].strip().strip("`") or "<이름없음>"
        declared = norm_layer(row["층"])
        # ---- R1 전수성 -----------------------------------------------------
        if "R1" in legs:
            if declared not in ("native", "codeforge"):
                findings.append("R1: 단계 %s 의 `층` 이 미기재·값공간 밖 (%r)" % (key, row["층"]))
            classes = [norm_class(c) for c in row["대상 클래스"].split(",") if c.strip()]
            if not classes:
                findings.append("R1: 단계 %s 의 대상 클래스 미기재" % key)
            for c in classes:
                if c not in valid_classes:
                    findings.append("R1: 단계 %s 의 대상 클래스 %r 이 6-literal 값공간 밖" % (key, c))
        derived = derive_layer(row, anchors)
        derived_map.append((key, declared, derived, row))
        if derived is None:
            findings.append("R1: 단계 %s 의 `층` 을 SSOT·mechanism_ref 에서 도출 불가 (fail-closed)" % key)
        elif declared in ("native", "codeforge") and derived != declared:
            findings.append(
                "R1: 단계 %s 의 도출값(%s) != 선언 라벨(%s) — 교차검증 불일치" % (key, derived, declared)
            )

    # ---- R1 (구조→산문 탈출 차단) -----------------------------------------
    if "R1" in legs:
        registered = set(r["경로 키"].strip().strip("`") for r in rows)
        for k in sorted(pseudo_path_keys(skill_text)):
            if k not in registered:
                findings.append("R1: 사다리 pseudo 의 경로 키 %s 가 레지스트리 미등재 (표 밖 산문)" % k)

    # R2/R3/R4 = **주장(claim)** 축 — 선언이 native 이거나 도출값이 native 이면 앵커 의무를 진다.
    # (선언만 native 로 바꾸고 앵커를 안 다는 M-R(a) 를 R2 가 직접 잡게 하기 위함 — §8.2-A 문면 정합.)
    claim_native_rows = [(k, r) for (k, dc, dv, r) in derived_map if dv == "native" or dc == "native"]
    # FWD 교집합 피연산자 = **도출값** (선언 라벨 아님 — AC-5c iter3 F-6 정정).
    native_rows = [(k, r) for (k, _dc, dv, r) in derived_map if dv == "native"]
    codeforge_rows = [(k, r) for (k, _dc, dv, r) in derived_map if dv == "codeforge"]

    # ---- R2 앵커 의무 ------------------------------------------------------
    if "R2" in legs:
        for key, row in claim_native_rows:
            ref = norm_anchor(row["mechanism_ref"])
            if ref in ("", "-", "—"):
                findings.append("R2: native 단계 %s 가 mechanism_ref 미보유" % key)
                continue
            if ref not in anchors:
                findings.append("R2: native 단계 %s 의 앵커 %s 가 정본 앵커 집합 밖" % (key, ref))
                continue
            if anchors[ref][0] != "retry":
                findings.append(
                    "R2: native 단계 %s 가 axis=%s 앵커(%s) 인용 — 재시도 발행 레지스트리 정의역 밖"
                    % (key, anchors[ref][0], ref)
                )

    # ---- R3 앵커 유일성 ----------------------------------------------------
    if "R3" in legs:
        seen = {}
        for key, row in claim_native_rows:
            ref = norm_anchor(row["mechanism_ref"])
            if ref in ("", "-", "—"):
                continue
            seen.setdefault(ref, []).append(key)
        for ref, keys in sorted(seen.items()):
            if len(keys) > 1:
                findings.append("R3: 앵커 %s 를 native 단계 %d개가 중복 주장 (%s)" % (ref, len(keys), ", ".join(keys)))

    # ---- R4 클래스 정합 ----------------------------------------------------
    if "R4" in legs:
        for key, row in claim_native_rows:
            ref = norm_anchor(row["mechanism_ref"])
            if ref not in anchors:
                continue
            declared_classes = frozenset(norm_class(c) for c in row["대상 클래스"].split(",") if c.strip())
            if declared_classes != anchors[ref][1]:
                findings.append(
                    "R4: native 단계 %s 의 대상 클래스 %s != 앵커 %s 커버 클래스 %s"
                    % (key, sorted(declared_classes), ref, sorted(anchors[ref][1]))
                )

    # ---- FWD 교집합 (피연산자 = 도출값) -----------------------------------
    if "FWD" in legs:
        nat = set()
        for _key, row in native_rows:
            nat |= set(norm_class(c) for c in row["대상 클래스"].split(",") if c.strip())
        cfg = set()
        for _key, row in codeforge_rows:
            cfg |= set(norm_class(c) for c in row["대상 클래스"].split(",") if c.strip())
        if not nat:
            findings.append("FWD: native 행 0 — 공집합 위 항진(구조적 항상-GREEN) 차단, fail-closed")
        inter = sorted(nat & cfg)
        if inter:
            findings.append("FWD: 두 층의 대상 클래스 교집합 비공집합 → 재시도 중첩 발행 %s" % (inter,))

    if findings:
        print("\n".join(findings))
        return 1
    print("OK finding=0 (rows=%d native=%d codeforge=%d)" % (len(rows), len(native_rows), len(codeforge_rows)))
    return 0


sys.exit(main())
PYORACLE

# ─────────────────────────────────────────────────────────────────────────────
# run_case: 오라클 실행 → exit code + 출력 substring 대조
#   인자: <name> <expected_exit> <expect_substr|""> <skill_path> <legs>
# ─────────────────────────────────────────────────────────────────────────────
run_case() {
  local name="$1" expected_exit="$2" expect_substr="$3" skill_path="$4" legs="$5"
  local out exit_code=0 ok=1
  out=$("$PY" "$ORACLE" --skill "$skill_path" --adr109 "$ADR109" --legs "$legs" 2>&1) || exit_code=$?
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
    echo "  expected exit=$expected_exit substr='$expect_substr' legs=$legs, got exit=$exit_code"
    echo "  output: $out"
    FAIL=$((FAIL + 1))
  fi
}

# mutate: 원본 SKILL 사본에 python 문자열치환 mutant 적용
#   인자: <dest> <src> <old> <new>
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

echo "── AC-5c: 재시도 층 중첩 (역방향 4 leg + 교집합)"

# ── TC-C1 clean-input 대조군 (실 정본) ───────────────────────────────────────
run_case "TC-C1 정본 SKILL.md — 0 finding" 0 "finding=0" "$SKILL" "R1,R2,R3,R4,FWD"

# ── TC-C2 clean-input 대조군 (합성 최소 정본) ────────────────────────────────
# 실 문서와 독립인 합성 픽스처로도 GREEN 이 나오는지 확인 — "실 문서에만 맞춘 오라클" 배제.
SYN="$WORK/synthetic_clean.md"
cat > "$SYN" <<'SYNEOF'
# synthetic clean fixture

```native-cover-anchor
# <anchor> | <axis> | <커버 클래스>
CHANGELOG:854 | retry | 429
CHANGELOG:837 | non-retry | usage limit
```

```
attempt 1: 경로 키 `only-rung`
```

| slot | 경로 키 | 층 | 대상 클래스 | tenant | SSOT | mechanism_ref |
|---|---|---|---|---|---|---|
| - | `native-x` | native | 429 | harness backoff | harness CHANGELOG | CHANGELOG:854 |
| 1 | `only-rung` | codeforge | session limit | ADR-141 Amendment 6 | ADR-141 Amendment 6 | - |
SYNEOF
run_case "TC-C2 합성 정본 픽스처 — 0 finding" 0 "finding=0" "$SYN" "R1,R2,R3,R4,FWD"

# ── TC-M1 ① 제거: 레지스트리 표 헤더 파손 → fail-closed ─────────────────────
M1="$WORK/m1.md"
mutate "$M1" "$SKILL" \
  "| slot | 경로 키 | 층 | 대상 클래스 | tenant | SSOT | mechanism_ref |" \
  "| slot | 경로 키 | 대상 클래스 | tenant | SSOT | mechanism_ref |"
run_case "TC-M1 ①제거 레지스트리 표 부재 → fail-closed RED" 1 "FAILCLOSED" "$M1" "R1,R2,R3,R4,FWD"

# ── TC-M1b ① 제거: 앵커 정본 fence 삭제 → fail-closed ───────────────────────
M1B="$WORK/m1b.md"
mutate "$M1B" "$SKILL" '```native-cover-anchor' '```anchor-fence-renamed-away'
run_case "TC-M1b ①제거 앵커 정본 fence 부재 → fail-closed RED" 1 "FAILCLOSED" "$M1B" "R1,R2,R3,R4,FWD"

# ── TC-M2 ② 주입: 네이티브 커버 클래스를 대상으로 하는 codeforge 단계 추가 ───
M2="$WORK/m2.md"
mutate "$M2" "$SKILL" \
  "| 4 | \`manual-resume\` | codeforge | session limit, usage limit |" \
  "| 4 | \`manual-resume\` | codeforge | session limit, usage limit, 429 |"
run_case "TC-M2 ②주입 codeforge 단계가 네이티브 커버 클래스 대상 → 교집합 RED" 1 "FWD:" "$M2" "R1,R2,R3,R4,FWD"

# ── TC-M3 M-R(a): 진짜 codeforge 단계를 `native` 로 개명만 ───────────────────
M3="$WORK/m3.md"
mutate "$M3" "$SKILL" \
  "| 2 | \`cross-model-substitution\` | codeforge |" \
  "| 2 | \`cross-model-substitution\` | native |"
run_case "TC-M3 M-R(a) 개명만 → R2 앵커 미보유 RED (잡힘)" 1 "R2: native 단계" "$M3" "R1,R2,R3,R4,FWD"

# ── TC-M4 ③ 등가변형: 개명 표기를 대소문자·공백·백틱으로 변형 ───────────────
M4="$WORK/m4.md"
mutate "$M4" "$SKILL" \
  "| 2 | \`cross-model-substitution\` | codeforge |" \
  "| 2 | \`cross-model-substitution\` |  \`NATIVE\`  |"
# ★ 여기서 "R2:" 를 요구하는 것이 곧 정규화 실증이다 — 정규화가 실패했다면 `  `NATIVE`  ` 는
#   값공간 밖(R1)으로만 잡히고 native 주장으로 인식되지 않아 R2 는 발화하지 않는다.
run_case "TC-M4 ③등가변형 층 표기 변형(NATIVE/공백/백틱) → 정규화 후 여전히 R2 RED" 1 "R2: native 단계" "$M4" "R1,R2,R3,R4,FWD"

# ── TC-M5 ③ 등가변형: 단계를 표 밖 산문으로 이동 → 스키마 미해소 ────────────
M5="$WORK/m5.md"
mutate "$M5" "$SKILL" \
  "| 3 | \`soak\` | codeforge | session limit, usage limit | ADR-109 §결정 2 max attempts soak | ADR-109 §결정 3 step3 | - |" \
  "soak 단계는 ADR-109 §결정 3 step3 을 따른다 (산문 서술로 이동)."
run_case "TC-M5 ③등가변형 구조→산문 이동 → fail-closed RED" 1 "표 밖 산문" "$M5" "R1,R2,R3,R4,FWD"

# ── TC-M6 M-R(b): 개명 + 유효 앵커 복사 + 클래스 정합 + SSOT 위장 (완전 위장) ─
M6="$WORK/m6.md"
mutate "$M6" "$SKILL" \
  "| 2 | \`cross-model-substitution\` | codeforge | session limit, usage limit | ADR-141 Amendment 6 fable→opus fresh re-spawn | ADR-141 Amendment 6 | - |" \
  "| 2 | \`cross-model-substitution\` | native | rate limit, quota exceeded, 429, Server is temporarily limiting | harness 자동 backoff 재시도 | harness CHANGELOG | CHANGELOG:854 |"
run_case "TC-M6 M-R(b) 완전 위장 → 4-leg 에서 R3 로 RED (잡힘)" 1 "R3:" "$M6" "R1,R2,R3,R4,FWD"

# ── TC-M7 같은 M-R(b) 를 R3 제외 3-leg 로 → 놓친다 (R3 유일성 실증) ─────────
run_case "TC-M7 M-R(b) 를 R3 제외 3-leg 로 → 놓침(exit 0) = R3 유일 discriminating 실증" 0 "finding=0" "$M6" "R1,R2,R4,FWD"

# ── TC-P1 정밀도 대조군: 정본에서 non-retry 앵커 인용 시도 → R2 가 잡는다 ────
P1="$WORK/p1.md"
mutate "$P1" "$SKILL" "| harness CHANGELOG | CHANGELOG:854 |" "| harness CHANGELOG | CHANGELOG:837 |"
run_case "TC-P1 native 행이 axis=non-retry 앵커 인용 → R2 RED (참칭 차단)" 1 "R2:" "$P1" "R1,R2,R3,R4,FWD"

# ── TC-P2 정밀도 대조군: 6-literal 값공간 밖 클래스 → R1 RED ────────────────
P2="$WORK/p2.md"
mutate "$P2" "$SKILL" \
  "| 1 | \`same-model-timing\` | codeforge | session limit, usage limit |" \
  "| 1 | \`same-model-timing\` | codeforge | session limit, 임의클래스 |"
run_case "TC-P2 값공간 밖 대상 클래스 → R1 RED (fail-closed)" 1 "값공간 밖" "$P2" "R1,R2,R3,R4,FWD"

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
