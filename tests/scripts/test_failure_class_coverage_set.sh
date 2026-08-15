#!/usr/bin/env bash
# tests/scripts/test_failure_class_coverage_set.sh
# CFP-2984 Phase 2 (구현 lane) — AC-25 discriminating self-test.
#
# AC-25: 실패 4클래스 정본 집합과 대응 절차 문서의 커버 클래스 집합의 **차집합**을 계산하면,
#        차집합 원소 전건이 문서에 미커버로 명시 열거되고 각각 진입점이 지정되며,
#        클래스 1개를 열거에서 빼거나 진입점을 지운 변이체는 RED 로 전환된다.
#
# ★ 항진(tautology) 회피의 핵심 = **값공간을 SUT 밖에 고정**한다.
#   초판 AC-25 는 순수 presence 형이라 클래스 값공간이 문서 자신에서 나왔고,
#   "미커버 없음" 이 자기참조로 항상 참이었다. 본 오라클은 값공간을 검사 대상 문서가
#   아닌 **ADR 정본 표**에서 읽고, 개수(=4)가 아니면 fail-closed 한다.
#
# ★ 값공간 앵커 실측 정정 (ADR-119 firsthand — 보고 대상):
#   Change Plan §3.5 / ADR-179 §결정 7 은 "4-class closed set SSOT = ADR-109 단일" 이라
#   선언한다. 그러나 `archive/adr/ADR-109-*.md` 를 실측하면 **실패 4클래스를 열거한 표·
#   code-fence 가 없다** — ADR-109 가 닫은 집합은 *detection literal* 6종(§결정 1 +
#   Amendment 1 (b))과 판별식 D 의 4치 출력(Amendment 2 (e))이지 `429 / 세션·주간 한도 /
#   stall / mid-run 사망` 4-class 가 아니다. repo 안에서 그 4-class 를 기계 판독 가능한
#   형태로 열거한 유일한 표면 = **ADR-179 §결정 7 라우팅 표**다.
#   ⇒ 값공간 앵커 = ADR-179 §결정 7 (SUT 밖 = 항진 회피 요건 충족)이며,
#     "SSOT = ADR-109" 선언은 별 limb 으로 **pointer 존재**를 검사한다
#     (skill 이 rival closed set 을 자기 정의하지 못하게 하는 §3.5 축).
#
# ★ hollow 아님의 증명 (§8.2-E INV-T4): baseline(정본 문서 쌍) = PASS 대조군 선행.
#   미커버 **선언 경로가 살아있음**도 별 케이스로 증명한다(M4 GREEN) — 선언 경로가
#   죽어 있으면 "차집합 원소를 선언하면 통과" 라는 AC 문면이 도달 불가능한 죽은 가지다.
#
# INV-T3 순수 픽스처: 네트워크 0 · 실 ~/.claude/** 0 · 실 git 원격 0 · 쓰기는 mktemp -d 내부만.
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILL="$REPO_ROOT/skills/session-recovery/SKILL.md"
ADR179="$REPO_ROOT/archive/adr/ADR-179-agent-salvage-bundle-handoff.md"
PYBIN="$(command -v python3 || command -v python)"

PASS=0
FAIL=0

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

cat > "$WORK/oracle.py" <<'PY'
# -*- coding: utf-8 -*-
"""AC-25 oracle — computed-set 차집합 (값공간 = SUT 밖 ADR 정본 표)."""
import sys

CANON_PATTERNS = {
    "429":   ["429", "rate limit", "rate-limit", "레이트 리밋"],
    "limit": ["세션 한도", "세션·주간 한도", "주간 한도", "한도 도달", "session limit",
              "usage limit", "사용량 한도", "한도"],
    "stall": ["stall", "무출력", "무응답", "정체", "timeout", "타임아웃"],
    "death": ["mid-run 사망", "중도 사망", "실행 중 사망", "사망", "중단", "death"],
}
EXPECTED_CARDINALITY = 4
PLACEHOLDER = {"", "-", "—", "–", "tbd", "TBD", "?", "(없음)", "없음", "n/a", "N/A"}


def canon_ids(cell):
    low = cell.lower()
    hits = set()
    for cid, pats in CANON_PATTERNS.items():
        for p in pats:
            if p.lower() in low:
                hits.add(cid)
                break
    return hits


def canon_one(cell):
    """정확히 1개 canonical id 로 사상될 때만 그 id, 아니면 None (fail-closed)."""
    ids = canon_ids(cell)
    return ids.pop() if len(ids) == 1 else None


def strip_fences(lines):
    out, infence = [], False
    for ln in lines:
        if ln.lstrip().startswith("```"):
            infence = not infence
            continue
        if not infence:
            out.append(ln)
    return out


def split_row(line):
    body = line.strip().replace(chr(92) + "|", chr(1))
    body = body.strip("|")
    return [c.replace(chr(1), "|").strip() for c in body.split("|")]


def is_sep(line):
    cells = split_row(line)
    return bool(cells) and all(set(c) <= set("-: ") and "-" in c for c in cells)


def tables_in(lines):
    out, i, n = [], 0, len(lines)
    while i < n:
        if lines[i].strip().startswith("|"):
            blk = []
            while i < n and lines[i].strip().startswith("|"):
                blk.append(lines[i])
                i += 1
            if len(blk) >= 3 and is_sep(blk[1]):
                out.append((split_row(blk[0]), [split_row(r) for r in blk[2:]]))
        else:
            i += 1
    return out


def section_lines(lines, heading_prefix, stop_depth=4):
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith(heading_prefix):
            start = i + 1
            break
    if start is None:
        return []
    out = []
    for ln in lines[start:]:
        s = ln.lstrip()
        if s.startswith("#") and not s.startswith("#" * stop_depth):
            break
        out.append(ln)
    return out


def filled(cell):
    return cell.strip() not in PLACEHOLDER and len(cell.strip()) > 0


def main():
    skill_path, adr_path = sys.argv[1], sys.argv[2]
    skill = strip_fences(open(skill_path, encoding="utf-8").read().split("\n"))
    adr = strip_fences(open(adr_path, encoding="utf-8").read().split("\n"))
    findings = []

    # ── (A) 값공간 = SUT 밖 정본 표 (ADR-179 §결정 7) ──────────────────────────
    vs_sec = section_lines(adr, "### §결정 7")
    vs_tabs = tables_in(vs_sec)
    value_space = []
    if not vs_tabs:
        print("VIOL anchor: ADR 정본 라우팅 표를 찾지 못했다 (값공간 미고정 — fail-closed)")
        return 1
    for r in vs_tabs[0][1]:
        if not r:
            continue
        cid = canon_one(r[0])
        if cid is None:
            findings.append("VIOL anchor: 정본 class 셀 '%s' 가 정확히 1개로 사상되지 않는다" % r[0])
            continue
        if cid not in value_space:
            value_space.append(cid)
    if len(value_space) != EXPECTED_CARDINALITY:
        findings.append("VIOL anchor: 정본 값공간 크기 %d (기대 %d) — 차집합 정의역 불성립"
                        % (len(value_space), EXPECTED_CARDINALITY))
        for f in findings:
            print(f)
        return 1

    # ── (B) 커버 집합 = SUT(§3.1) ─────────────────────────────────────────────
    routing = section_lines(skill, "### 3.1")
    r_tabs = tables_in(routing)
    covered = set()
    if not r_tabs:
        findings.append("VIOL structure: '### 3.1' 라우팅 표 부재 (fail-closed)")
    else:
        for r in r_tabs[0][1]:
            if len(r) < 2:
                continue
            cid = canon_one(r[0])
            if cid is None:
                continue
            if filled(r[1]):
                covered.add(cid)

    # ── (C) 미커버 명시 선언 집합 = SUT(§3.2) ─────────────────────────────────
    unc_sec = section_lines(skill, "### 3.2")
    declared = set()
    for _, rows in tables_in(unc_sec):
        for r in rows:
            if len(r) < 3:
                continue
            cid = canon_one(r[0])
            if cid is None:
                continue
            if filled(r[2]):          # 임시 진입점 셀
                declared.add(cid)

    # ── (D) 차집합 판정 ───────────────────────────────────────────────────────
    diff = [c for c in value_space if c not in covered]
    for c in diff:
        if c not in declared:
            findings.append("VIOL diff: class '%s' 가 커버도 아니고 미커버 선언(진입점 포함)도 없다" % c)

    # ── (E) closed set SSOT pointer — rival 정의 금지 (Change Plan §3.5) ──────
    ptr = any(("closed set" in ln) and ("ADR-109" in ln) and ("SSOT" in ln) for ln in skill)
    if not ptr:
        findings.append("VIOL ssot: closed set SSOT = ADR-109 pointer 선언이 없다 "
                        "(skill 이 rival closed set 을 자기 정의할 위험)")

    if findings:
        for f in findings:
            print(f)
        return 1
    print("OK AC-25: 값공간 %s / 커버 %s / 선언 %s / 차집합 %s"
          % (sorted(value_space), sorted(covered), sorted(declared), sorted(diff)))
    return 0


sys.exit(main())
PY

cat > "$WORK/mutate.py" <<'PY'
# -*- coding: utf-8 -*-
"""AC-25 mutation generator. usage: mutate.py <src> <dst> <op>"""
import sys

src, dst, op = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(src, encoding="utf-8").read().split("\n")

UNCOVERED_HEADER = ["| 미커버 class | 사유 | 임시 진입점 |", "|---|---|---|"]


def idx_of(pred):
    for i, ln in enumerate(lines):
        if pred(ln):
            return i
    return None


def insert_uncovered_table(rows):
    j = idx_of(lambda l: l.startswith("### 3.3"))
    assert j is not None, "section 3.3 anchor not found"
    block = [""] + UNCOVERED_HEADER + rows + [""]
    lines[j:j] = block


if op == "drop-stall-row":
    # ① 제거 — stall 라우팅 행 삭제, 미커버 선언 없음
    i = idx_of(lambda l: l.strip().startswith("| stall"))
    assert i is not None
    del lines[i]

elif op == "blank-429-entry":
    # ② 주입 — 429 행은 남기되 진입점 공란 (커버 참칭)
    i = idx_of(lambda l: l.strip().startswith("| 429"))
    assert i is not None
    cells = lines[i].strip().strip("|").split("|")
    cells[1] = " — "
    lines[i] = "|" + "|".join(cells) + "|"

elif op == "prose-limit":
    # ③ 등가변형(RED) — 구조→산문: 한도 class 행 삭제 + 클래스명은 산문으로 잔존
    i = idx_of(lambda l: l.strip().startswith("| 세션·주간 한도"))
    assert i is not None
    del lines[i]
    j = idx_of(lambda l: l.startswith("### 3.2"))
    assert j is not None
    lines.insert(j, "세션·주간 한도 상황도 물론 중요하며 별도로 다룬다.")
    lines.insert(j + 1, "")

elif op == "declared-with-entry":
    # 선언 경로 생존 증명(GREEN 기대) — 행 삭제 + §3.2 에 진입점 포함 미커버 선언
    i = idx_of(lambda l: l.strip().startswith("| stall"))
    assert i is not None
    del lines[i]
    insert_uncovered_table(["| stall | 임계 empirical 미확정 | ADR-139 결정 2 inconclusive 기록 |"])

elif op == "declared-without-entry":
    # ② 주입(RED) — 미커버 선언은 했으나 임시 진입점을 지운 변이체 (AC-25 문면 명시)
    i = idx_of(lambda l: l.strip().startswith("| stall"))
    assert i is not None
    del lines[i]
    insert_uncovered_table(["| stall | 임계 empirical 미확정 | — |"])

elif op == "synonym-labels":
    # ③ 등가변형(GREEN) — class 라벨 동의어 개명 (정규화로 해소되어야 함)
    for i, ln in enumerate(lines):
        if ln.strip().startswith("| 429 계열 (rate limit) |"):
            lines[i] = ln.replace("| 429 계열 (rate limit) |", "| HTTP 429 |", 1)
        elif ln.strip().startswith("| stall (무출력 정체) |"):
            lines[i] = ln.replace("| stall (무출력 정체) |", "| 무응답 정체 |", 1)
        elif ln.strip().startswith("| mid-run 사망 |"):
            lines[i] = ln.replace("| mid-run 사망 |", "| 실행 중 사망 |", 1)
        elif ln.strip().startswith("| 세션·주간 한도 |"):
            lines[i] = ln.replace("| 세션·주간 한도 |", "| 사용량 한도 도달 |", 1)

elif op == "drop-ssot-pointer":
    # rival 정의 방지 축(RED) — closed set SSOT pointer 선언 삭제
    i = idx_of(lambda l: ("closed set" in l) and ("ADR-109" in l) and ("SSOT" in l))
    assert i is not None
    del lines[i]

elif op == "anchor-shrink":
    # 값공간 앵커 파손(RED, fail-closed) — ADR 정본 표에서 stall 행 제거
    i = idx_of(lambda l: l.strip().startswith("| stall "))
    assert i is not None
    del lines[i]

else:
    raise SystemExit("unknown op: %s" % op)

with open(dst, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines))
PY

run_case() {
  local name="$1" expected="$2" skill="$3" adr="$4"
  local rc=0 out verdict
  out=$("$PYBIN" "$WORK/oracle.py" "$skill" "$adr" 2>&1) || rc=$?
  if [ "$rc" -eq 0 ]; then verdict="GREEN"; else verdict="RED"; fi
  if [ "$verdict" = "$expected" ]; then
    echo "OK   $name — expected=$expected got=$verdict (rc=$rc)"
    PASS=$((PASS+1))
  else
    echo "FAIL $name — expected=$expected got=$verdict (rc=$rc)"
    printf '%s\n' "$out" | sed 's/^/       /'
    FAIL=$((FAIL+1))
  fi
}

mutate_skill_case() {
  local name="$1" expected="$2" op="$3"
  local dst="$WORK/skill-$op.md"
  if ! "$PYBIN" "$WORK/mutate.py" "$SKILL" "$dst" "$op" >/dev/null 2>&1; then
    echo "FAIL $name — mutation '$op' 적용 실패 (앵커 소실)"
    FAIL=$((FAIL+1))
    return
  fi
  run_case "$name" "$expected" "$dst" "$ADR179"
}

echo "── AC-25 failure-class coverage set (computed 차집합) ──"

run_case "baseline: 정본 SKILL + 정본 ADR-179 §결정 7" GREEN "$SKILL" "$ADR179"

mutate_skill_case "M1 제거: stall 행 삭제(선언 없음)"            RED drop-stall-row
mutate_skill_case "M2 주입: 429 진입점 공란(커버 참칭)"          RED blank-429-entry
mutate_skill_case "M3 등가변형(RED): 구조→산문 (한도 행 삭제)"    RED prose-limit
mutate_skill_case "M4 선언 경로 생존: 미커버+진입점 선언"         GREEN declared-with-entry
mutate_skill_case "M5 주입: 미커버 선언 있으나 진입점 삭제"        RED declared-without-entry
mutate_skill_case "M6 등가변형(GREEN): class 라벨 동의어 개명"     GREEN synonym-labels
mutate_skill_case "M7 rival 방지: closed set SSOT pointer 삭제"   RED drop-ssot-pointer

# 값공간 앵커 자신이 깨지면 차집합 정의역이 불성립 → fail-closed RED 여야 한다.
if "$PYBIN" "$WORK/mutate.py" "$ADR179" "$WORK/adr-shrunk.md" anchor-shrink >/dev/null 2>&1; then
  run_case "M8 앵커 파손: 정본 표 4→3 (fail-closed)" RED "$SKILL" "$WORK/adr-shrunk.md"
else
  echo "FAIL M8 앵커 파손 — mutation 적용 실패 (앵커 소실)"
  FAIL=$((FAIL+1))
fi

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
