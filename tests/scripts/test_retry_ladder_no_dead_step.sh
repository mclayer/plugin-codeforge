#!/usr/bin/env bash
# tests/scripts/test_retry_ladder_no_dead_step.sh
# CFP-2984 Phase 2 (구현 lane) — AC-23 discriminating self-test.
#
# 정의역 = `skills/rate-limit-429-mitigation/SKILL.md` ∪ `archive/adr/ADR-109-*.md` **본문 전체**의
#          **실행 흐름 지시 단계**(사다리 rung · attempt · §결정 3 번호 step · 레지스트리 행).
#          서술·참조목록·Cross-ref 는 제외한다.
#
# 오라클 = 각 단계가 지시하는 **대상 조항**을 참조 무결성으로 해소:
#   (a) 대상 문서 실재  (b) 해당 **조항** 앵커 실재  (c) 그 조항이 retired(dead-mark)로 표시되지 않음
#   (d) 단계가 조항 ref 를 **0개** 보유 = 미해소 → fail-closed RED (공허 통과 차단)
#
# ★ 판정 단위 = 문서 status 가 아니라 **조항(§결정) 단위**:
#   ADR-057 은 `Superseded` 이지만 §결정 4 / §결정 6(529 cooldown)은 **여전히 유효**하다.
#   문서 status 를 위반 근거로 삼는 오라클은 그 두 조항을 오검출한다 — TC-C3 가 그 오검출 부재를
#   대조군으로 못박는다(정밀도 keystone).
#
# ★ 정의역에 ADR 본문을 포함해야 하는 이유:
#   SKILL.md 만 훑으면 ADR-109 §결정 3 안의 dead rung 을 **공허 통과**한다. TC-M4 가 그 경로를 실증한다.
#
# ★ 정직 천장: 본 검사는 **명시 dead-mark 로 표시된 조항**을 지시하는 단계만 잡는다.
#   dead 인데 아무도 dead-mark 를 달지 않은 조항은 잡히지 않는다 — 그 축은 사람 검토 잔여다.
#
# self-contained bash + 순수 픽스처 (INV-T3). Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILL="$REPO_ROOT/skills/rate-limit-429-mitigation/SKILL.md"
ADR109="$REPO_ROOT/archive/adr/ADR-109-in-process-429-mitigation-framework.md"
ADR_DIR="$REPO_ROOT/archive/adr"

PY=python3
command -v python3 >/dev/null 2>&1 || PY=python

PASS=0
FAIL=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

ORACLE="$WORK/oracle_23.py"
cat > "$ORACLE" <<'PYORACLE'
# -*- coding: utf-8 -*-
"""AC-23 오라클 — 재시도 사다리 실행 흐름 지시 단계의 조항 참조 무결성.

exit 0 = finding 0.  exit 1 = finding >= 1.
`--dump-retired` 는 판정에 쓰인 retired 조항 집합을 출력한다(대조군 검증용).
"""
import argparse
import glob
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass

RE_FENCE = re.compile(r"^```([A-Za-z0-9_-]*)\s*$")
# 조항 ref — 링크 표기 `[ADR-057](ADR-057-....md)` · 평문 `ADR-057` · 축약 공백 전부 흡수.
RE_CLAUSE = re.compile(
    r"ADR[-\s]?(\d{2,4})[^\n]{0,80}?(?:§\s*결정\s*(\d+)|Amendment\s*(\d+)|\bA(\d+)-(\d+)\b)"
)
RE_BARE_CLAUSE = re.compile(r"§\s*결정\s*(\d+)")
# dead-mark 주석 — 보존 규약(ADR-141 A6-6 dead-mark 보존 동형)에 따라 지시가 아니라 **이력**이다.
RE_DEADMARK_SEG = re.compile(
    r"(?:prior tenant|구 tenant|이전 tenant)\s*:?[^\n]{0,160}?(?:moot|dead|폐기|retired)[^\n]*"
)
# dead **verdict** 토큰 — 판정어 위치(연결어 뒤)에서만 인정한다.
#   `dead slot` / `dead-mark` / `dead rung` 처럼 다른 명사를 수식하는 용법은 판정이 아니다.
RE_DEAD_TOKEN = re.compile(
    r"(?:moot/dead|moot|dead|retired|폐기)(?![\w-]*(?:\s|-)?(?:slot|rung|path|tenant|mark|line|step))"
)
RE_DEAD_CONNECTOR = re.compile(r"(?:[=:,]|[—-]|[는은로]\s)\s*\**\s*$")
# 조항 ref 를 **위치와 함께** 뽑기 위한 패턴 (ADR 접두 있는 형태 / bare `§결정 N`)
RE_CLAUSE_POS = re.compile(r"ADR[-\s]?(\d{2,4})[^\n]{0,80}?(?:§\s*결정\s*(\d+)|Amendment\s*(\d+))")
RE_BARE_POS = re.compile(r"§\s*결정\s*(\d+)")
RE_ADR_NUM = re.compile(r"ADR[-\s]?(\d{2,4})")


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


def strip_deadmarks(text):
    """dead-mark 보존 주석을 제거한다 — 보존된 이력은 실행 지시가 아니다."""
    return RE_DEADMARK_SEG.sub(" <dead-mark-annotation-stripped> ", text)


def collect_steps(skill_text, adr_text):
    """실행 흐름 지시 단계 목록: (origin, label, raw_text)."""
    steps = []

    # (1) SKILL 사다리 pseudo — `attempt ...` 로 시작하는 chunk
    for _info, body in fences(skill_text):
        joined = "\n".join(body)
        if "attempt 1:" not in joined and "attempts 3" not in joined:
            continue
        for chunk in re.split(r"\n\s*\n", joined):
            head = chunk.strip().split("\n")[0] if chunk.strip() else ""
            if re.match(r"^attempts?\s", head):
                steps.append(("SKILL:pseudo", head[:48], chunk))

    # (2) SKILL 레지스트리 표 데이터 행 — SSOT 셀이 그 단계의 지시 대상
    for ln in skill_text.split("\n"):
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) != 7 or cells[0].lower() == "slot" or re.match(r"^[-\s:]+$", cells[0]):
            continue
        label = cells[1].strip("`")
        steps.append(("SKILL:registry", label, cells[5] + " " + cells[4]))

    # (3) ADR-109 §결정 3 번호 step (본문 포함 — SKILL-only 정의역의 공허 통과 차단)
    lines = strip_frontmatter(adr_text).split("\n")
    inside = False
    for ln in lines:
        if ln.startswith("### "):
            inside = ln.startswith("### §결정 3")
            continue
        if not inside:
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", ln)
        if m:
            steps.append(("ADR-109:§결정3", "step" + m.group(1), ln))
    return steps


def clause_refs(text):
    """단계 텍스트에서 조항 ref 를 추출한다 (dead-mark 주석 제거 후)."""
    body = strip_deadmarks(text)
    refs = set()
    for m in RE_CLAUSE.finditer(body):
        adr = int(m.group(1))
        if m.group(2):
            refs.add((adr, "§결정 %s" % m.group(2)))
        elif m.group(3):
            refs.add((adr, "Amendment %s" % m.group(3)))
        else:
            refs.add((adr, "A%s-%s" % (m.group(4), m.group(5))))
    if not refs:
        # ADR 번호 없이 `§결정 N` 만 쓴 경우 = 자기 문서(ADR-109) 조항 지시
        for m in RE_BARE_CLAUSE.finditer(body):
            refs.add((109, "§결정 %s" % m.group(1)))
    return refs


RE_LINK_SUBJECT = re.compile(r"^\s*[-*>]*\s*\[ADR[-\s]?(\d{2,4})\]")


def strip_frontmatter(text):
    """YAML frontmatter 제거 — AC-23 정의역 = **본문 전체**.

    frontmatter 의 amendment_log 는 "무엇을 무엇으로 교체했다" 는 **서사 감사면**이라
    실행 흐름 지시가 아니며, 그 서사 안의 dead 어휘를 판정원으로 쓰면 **신 tenant** 가
    오검출된다(구 tenant 를 dead 로 재규정하는 문장에서 신 tenant 가 더 가까이 놓인다).
    """
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    return text[end + 5:] if end != -1 else text


def _clause_positions(line, default_adr):
    """한 줄에서 (end_pos, (adr, clause)) 목록.

    bare `§결정 N` 귀속 우선순위: `본 §결정` → 자기 문서 / 줄머리 링크 주어 → 그 ADR /
    그 외 → 같은 줄 직전 ADR / 없으면 default.
    (줄머리 링크 주어 규칙이 없으면 `[ADR-057](...) — Superseded(by ADR-141). §결정 2 = moot/dead`
     에서 §결정 2 가 ADR-141 로 오귀속된다.)
    """
    out = []
    taken = []
    for m in RE_CLAUSE_POS.finditer(line):
        adr = int(m.group(1))
        clause = "§결정 %s" % m.group(2) if m.group(2) else "Amendment %s" % m.group(3)
        out.append((m.end(), (adr, clause)))
        taken.append((m.start(), m.end()))
    subj = RE_LINK_SUBJECT.match(line)
    subject_adr = int(subj.group(1)) if subj else None
    for m in RE_BARE_POS.finditer(line):
        if any(a <= m.start() < b for a, b in taken):
            continue
        if line[:m.start()].rstrip().endswith("본"):
            adr = default_adr
        elif subject_adr is not None:
            adr = subject_adr
        else:
            prev = [a for a in RE_ADR_NUM.finditer(line) if a.end() <= m.start()]
            adr = int(prev[-1].group(1)) if prev else default_adr
        out.append((m.end(), (adr, "§결정 %s" % m.group(1))))
    out.sort()
    return out


def retired_clauses(texts):
    """정의역 전체에서 **조항 단위** dead-mark 를 수집한다.

    문서 status(`Superseded`)는 **판정원이 아니다** — status 를 위반 근거로 삼으면
    ADR-057 §결정 4 / §결정 6(여전히 유효)이 오검출된다.
    판정 = "dead verdict 토큰의 **가장 가까운 선행 조항 ref**(60자 이내)" 결속.
    """
    out = set()
    for t, default_adr in texts:
        for line in strip_frontmatter(t).split("\n"):
            refs = _clause_positions(line, default_adr)
            if not refs:
                continue
            for m in RE_DEAD_TOKEN.finditer(line):
                if not RE_DEAD_CONNECTOR.search(line[max(0, m.start() - 15):m.start()]):
                    continue  # 판정어 위치가 아님 (수식·서술 용법)
                prior = [r for r in refs if r[0] <= m.start()]
                if not prior:
                    continue
                end, clause = prior[-1]
                if m.start() - end <= 60:
                    out.add(clause)
    return out


def adr_path(adr_dir, num):
    hits = sorted(glob.glob(os.path.join(adr_dir, "ADR-%03d-*.md" % num)))
    return hits[0] if hits else None


def clause_anchor_present(text, clause):
    if clause.startswith("§결정 "):
        n = clause.split()[-1]
        # 표기 편차 흡수: `### §결정 2` (ADR-109 계열) ↔ `### 결정 2:` (ADR-057 계열)
        return re.search(r"^#{2,4}\s*§?\s*결정\s*%s\b" % re.escape(n), text, re.M) is not None
    if clause.startswith("Amendment "):
        n = clause.split()[-1]
        return re.search(r"^#{2,3}\s*Amendment\s*%s\b" % re.escape(n), text, re.M) is not None
    return clause in text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True)
    ap.add_argument("--adr109", required=True)
    ap.add_argument("--adr-dir", required=True)
    ap.add_argument("--dump-retired", action="store_true")
    args = ap.parse_args()

    skill_text = read(args.skill)
    adr_text = read(args.adr109)
    retired = retired_clauses([(skill_text, 109), (adr_text, 109)])

    if args.dump_retired:
        for adr, cl in sorted(retired):
            print("RETIRED ADR-%03d %s" % (adr, cl))
        return 0

    findings = []
    steps = collect_steps(skill_text, adr_text)
    if not steps:
        print("FAILCLOSED: 실행 흐름 지시 단계 추출 0건 — 정의역 소실")
        return 1

    for origin, label, raw in steps:
        refs = clause_refs(raw)
        if not refs:
            findings.append("UNRESOLVED: [%s] %s — 조항 ref 0개 (fail-closed)" % (origin, label))
            continue
        for adr, clause in sorted(refs):
            path = adr_path(args.adr_dir, adr)
            if path is None:
                findings.append("MISSINGDOC: [%s] %s → ADR-%03d 문서 부재" % (origin, label, adr))
                continue
            if not clause_anchor_present(read(path), clause):
                findings.append(
                    "MISSINGCLAUSE: [%s] %s → ADR-%03d %s 앵커 부재" % (origin, label, adr, clause)
                )
                continue
            if (adr, clause) in retired:
                findings.append(
                    "DEADSTEP: [%s] %s → ADR-%03d %s 는 dead-mark 조항" % (origin, label, adr, clause)
                )

    if findings:
        print("\n".join(findings))
        return 1
    print("OK finding=0 (steps=%d, retired_clauses=%d)" % (len(steps), len(retired)))
    return 0


sys.exit(main())
PYORACLE

run_case() {
  local name="$1" expected_exit="$2" expect_substr="$3" skill_path="$4" adr_path="$5"
  local out exit_code=0 ok=1
  out=$("$PY" "$ORACLE" --skill "$skill_path" --adr109 "$adr_path" --adr-dir "$ADR_DIR" 2>&1) || exit_code=$?
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

# assert_absent: 출력에 substring 이 **없어야** 하는 대조군 (오검출 부재 확증)
assert_absent() {
  local name="$1" forbidden="$2" cmd_out="$3"
  case "$cmd_out" in
    *"$forbidden"*)
      echo "X FAIL: $name (금지 substring '$forbidden' 출현)"
      echo "  output: $cmd_out"
      FAIL=$((FAIL + 1))
      ;;
    *)
      echo "OK PASS: $name"
      PASS=$((PASS + 1))
      ;;
  esac
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

echo "── AC-23: 재시도 사다리 dead-step 부재 (조항 단위 참조 무결성)"

# ── TC-C1 clean-input 대조군 ────────────────────────────────────────────────
run_case "TC-C1 정본 SKILL ∪ ADR-109 — 0 finding" 0 "finding=0" "$SKILL" "$ADR109"

# ── TC-C2 대조군: 보존된 dead-mark 주석이 위반으로 잡히지 않는다 ────────────
RETIRED_DUMP=$("$PY" "$ORACLE" --skill "$SKILL" --adr109 "$ADR109" --adr-dir "$ADR_DIR" --dump-retired 2>&1)
case "$RETIRED_DUMP" in
  *"RETIRED ADR-057 §결정 2"*)
    echo "OK PASS: TC-C2 dead-mark 수집 — ADR-057 §결정 2 가 retired 집합에 실재"
    PASS=$((PASS + 1))
    ;;
  *)
    echo "X FAIL: TC-C2 retired 집합에 ADR-057 §결정 2 부재 (수집기 사망 → 이후 leg 전부 무의미)"
    echo "  output: $RETIRED_DUMP"
    FAIL=$((FAIL + 1))
    ;;
esac

# ── TC-C3 ★ 정밀도 keystone: 문서 status 로 판정하면 오검출되는 조항 2건 ────
# ADR-057 은 `Superseded` 이나 §결정 4 / §결정 6 은 유효 — retired 집합에 들어가면 안 된다.
assert_absent "TC-C3a ADR-057 §결정 4 는 retired 아님 (status 기반 오검출 부재)" "RETIRED ADR-057 §결정 4" "$RETIRED_DUMP"
assert_absent "TC-C3b ADR-057 §결정 6 은 retired 아님 (status 기반 오검출 부재)" "RETIRED ADR-057 §결정 6" "$RETIRED_DUMP"

# ── TC-M1 ① 제거: 레지스트리 행의 SSOT 지시를 지움 → 조항 ref 0 → fail-closed ─
M1="$WORK/m1.md"
mutate "$M1" "$SKILL" \
  "| 2 | \`cross-model-substitution\` | codeforge | session limit, usage limit | ADR-141 Amendment 6 fable→opus fresh re-spawn | ADR-141 Amendment 6 | - |" \
  "| 2 | \`cross-model-substitution\` | codeforge | session limit, usage limit | fresh re-spawn | - | - |"
run_case "TC-M1 ①제거 지시 조항 삭제 → UNRESOLVED fail-closed RED" 1 "UNRESOLVED" "$M1" "$ADR109"

# ── TC-M2 ② 주입: dead 조항(ADR-057 §결정 2)을 live tenant 로 부활 ──────────
M2="$WORK/m2.md"
mutate "$M2" "$SKILL" \
  "attempt 2: cross-model substitution (step2 slot) — 현 tenant = ADR-141 Amendment 6" \
  "attempt 2: ADR-057 §결정 2 model fallback (Sonnet → Opus, max 1회)"
run_case "TC-M2 ②주입 dead 조항 부활 → DEADSTEP RED" 1 "DEADSTEP" "$M2" "$ADR109"

# ── TC-M3 ③ 등가변형 3형태: 링크 / 제목 / 공백-축약 표기 ────────────────────
M3A="$WORK/m3a.md"
mutate "$M3A" "$SKILL" \
  "attempt 2: cross-model substitution (step2 slot) — 현 tenant = ADR-141 Amendment 6" \
  "attempt 2: [ADR-057](../../archive/adr/ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) §결정 2 로 대체 실행"
run_case "TC-M3a ③등가변형 링크 표기 → 같은 조항으로 해소 → DEADSTEP RED" 1 "DEADSTEP" "$M3A" "$ADR109"

M3B="$WORK/m3b.md"
mutate "$M3B" "$SKILL" \
  "attempt 2: cross-model substitution (step2 slot) — 현 tenant = ADR-141 Amendment 6" \
  "attempt 2: sonnet→opus 모델 폴백 절차(ADR-057 orchestrator opus mandate §결정 2)를 적용"
run_case "TC-M3b ③등가변형 제목 표기 → 같은 조항으로 해소 → DEADSTEP RED" 1 "DEADSTEP" "$M3B" "$ADR109"

M3C="$WORK/m3c.md"
mutate "$M3C" "$SKILL" \
  "attempt 2: cross-model substitution (step2 slot) — 현 tenant = ADR-141 Amendment 6" \
  "attempt 2: ADR 057 의 §  결정  2 경로로 진입"
run_case "TC-M3c ③등가변형 공백-축약 표기 → 정규화 후 해소 → DEADSTEP RED" 1 "DEADSTEP" "$M3C" "$ADR109"

# ── TC-M4 ★ 정의역 실증: ADR 본문에만 dead rung 을 주입 ─────────────────────
# SKILL.md 만 훑는 오라클은 이 mutant 를 **공허 통과**한다. ADR 본문 포함이 필수임을 실증.
M4="$WORK/adr109_m4.md"
mutate "$M4" "$ADR109" \
  "3. **opus 도 429 → 6 attempts soak**" \
  "3. **ADR-057 §결정 2 재적용 후 soak**"
run_case "TC-M4 정의역 실증 — ADR 본문에만 dead rung 주입 → DEADSTEP RED" 1 "ADR-109:§결정3" "$SKILL" "$M4"

# ── TC-M5 참조 무결성: 존재하지 않는 조항 앵커 지시 ─────────────────────────
M5="$WORK/m5.md"
mutate "$M5" "$SKILL" "| ADR-109 §결정 3 step4 | - |" "| ADR-109 §결정 99 step4 | - |"
run_case "TC-M5 실재하지 않는 조항 앵커 → MISSINGCLAUSE RED" 1 "MISSINGCLAUSE" "$M5" "$ADR109"

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
