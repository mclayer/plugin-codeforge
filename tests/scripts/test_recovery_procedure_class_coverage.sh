#!/usr/bin/env bash
# tests/scripts/test_recovery_procedure_class_coverage.sh
# CFP-2984 Phase 2 (구현 lane) — AC-27 discriminating self-test.
#
# AC-27: 세션 복원 절차 문서에서 mid-run 사망 / stall / 한도 도달 3클래스의
#        대응 항목이 모두 존재하고, 항목을 제거한 변이체는 RED 로 전환된다.
#
# ★ 오라클 정의역에 frontmatter 포함 (ModuleArch B-1-7 / Change Plan §3.5):
#   skill 의 공개 계약면 = frontmatter `description`. body 만 커버하고 description 이
#   3클래스에 도달하지 않으면 "body 는 커버하는데 라우팅은 도달하지 않는" 상태다.
#   따라서 class 별 2-limb (a) body 라우팅 행 + 진입점 (b) description 도달 을 모두 요구한다.
#
# ★ hollow 아님의 증명 (§8.2-E INV-T4): baseline(정본 문서) = PASS 대조군을 항상 먼저
#   실행한다. baseline 이 이미 RED 면 mutant RED 는 아무것도 증명하지 않는다.
#   3방향 mutant = ① 제거 ② 주입 ③ 등가변형(RED = 결함 + 표기 회피 / GREEN = 순수 표기 변경).
#
# INV-T3 순수 픽스처: 네트워크 0 · 실 ~/.claude/** 0 · 실 git 원격 0 · 쓰기는 mktemp -d 내부만.
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKILL="$REPO_ROOT/skills/session-recovery/SKILL.md"
PYBIN="$(command -v python3 || command -v python)"

PASS=0
FAIL=0

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# ─────────────────────────────────────────────────────────────────────────────
# oracle.py — AC-27 판정기. exit 0 = 커버 충족, exit 1 = 위반.
# ─────────────────────────────────────────────────────────────────────────────
cat > "$WORK/oracle.py" <<'PY'
# -*- coding: utf-8 -*-
"""AC-27 oracle — 3 failure class 대응 항목 존재 검사 (정의역 = frontmatter + body)."""
import sys

# 정본 class 동의어 사전. 문서 표기가 바뀌어도 canonical id 로 사상한다(리터럴 매칭 금지).
CANON_PATTERNS = {
    "429":   ["429", "rate limit", "rate-limit", "레이트 리밋"],
    "limit": ["세션 한도", "세션·주간 한도", "주간 한도", "한도 도달", "session limit",
              "usage limit", "사용량 한도", "한도"],
    "stall": ["stall", "무출력", "무응답", "정체", "timeout", "타임아웃"],
    "death": ["mid-run 사망", "중도 사망", "실행 중 사망", "사망", "중단", "death"],
}
# AC-27 이 요구하는 3 class (429 는 AC-25 의 4-class 차집합 축 소관).
REQUIRED = ["death", "stall", "limit"]

PLACEHOLDER = {"", "-", "—", "–", "tbd", "TBD", "?", "(없음)", "없음", "n/a", "N/A"}


def canon_ids(cell):
    """cell 문자열 → 매칭된 canonical id 집합 (동의어 정규화)."""
    low = cell.lower()
    hits = set()
    for cid, pats in CANON_PATTERNS.items():
        for p in pats:
            if p.lower() in low:
                hits.add(cid)
                break
    return hits


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
    """연속 '|' 블록 → (header, rows) 리스트."""
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


def frontmatter_description(lines):
    if not lines or lines[0].strip() != "---":
        return ""
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            break
        if lines[i].startswith("description:"):
            return lines[i][len("description:"):].strip()
    return ""


def section_lines(lines, heading_prefix):
    """heading 으로 시작하는 절의 본문 라인 (다음 동급 이상 heading 전까지)."""
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
        if s.startswith("#") and not s.startswith("####"):
            break
        out.append(ln)
    return out


def main():
    path = sys.argv[1]
    raw = open(path, encoding="utf-8").read().split("\n")
    desc = frontmatter_description(raw)
    body = strip_fences(raw)

    routing = section_lines(body, "### 3.1")
    tabs = tables_in(routing)
    findings = []
    if not tabs:
        findings.append("VIOL structure: '### 3.1' 절에 라우팅 표가 없다 (fail-closed)")
        covered = {}
    else:
        header, rows = tabs[0]
        covered = {}
        for r in rows:
            if len(r) < 2:
                continue
            ids = canon_ids(r[0])
            if len(ids) != 1:
                # 0 = 미지 class / 2+ = 모호 → 커버로 세지 않는다 (fail-closed)
                continue
            cid = ids.pop()
            entry = r[1].strip()
            covered[cid] = entry not in PLACEHOLDER and len(entry) > 0

    for cid in REQUIRED:
        if cid not in covered:
            findings.append("VIOL body: class '%s' 대응 항목이 라우팅 표에 없다" % cid)
        elif not covered[cid]:
            findings.append("VIOL body: class '%s' 행은 있으나 진입점 셀이 비었다" % cid)
        if not canon_ids(desc) & {cid}:
            findings.append("VIOL frontmatter: class '%s' 가 description 에 도달하지 않는다" % cid)

    if findings:
        for f in findings:
            print(f)
        return 1
    print("OK AC-27: 3 class(death/stall/limit) x 2limb(body routing + frontmatter) 전건 충족")
    return 0


sys.exit(main())
PY

# ─────────────────────────────────────────────────────────────────────────────
# mutate.py — 정본 사본에 변이 1종 적용. argv = ASCII 만 (한글 argv mangling 회피).
# ─────────────────────────────────────────────────────────────────────────────
cat > "$WORK/mutate.py" <<'PY'
# -*- coding: utf-8 -*-
"""AC-27 mutation generator. usage: mutate.py <src> <dst> <op>"""
import sys

src, dst, op = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(src, encoding="utf-8").read().split("\n")


def row_index(pred):
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|") and pred(ln):
            return i
    return None


if op == "drop-death-row":
    # ① 제거 — mid-run 사망 라우팅 행 삭제
    i = row_index(lambda l: "mid-run 사망" in l and "3-step runbook" in l)
    assert i is not None, "target row not found"
    del lines[i]

elif op == "blank-stall-entry":
    # ② 주입 — stall 행은 남기되 진입점 셀을 빈 값으로 (커버 참칭)
    i = row_index(lambda l: l.strip().startswith("| stall"))
    assert i is not None, "target row not found"
    cells = lines[i].strip().strip("|").split("|")
    cells[1] = " — "
    lines[i] = "|" + "|".join(cells) + "|"

elif op == "desc-drop-stall":
    # ③ 등가변형(RED) — body 무손상, 공개 계약면(frontmatter)에서만 stall 탈락
    for i, ln in enumerate(lines):
        if ln.startswith("description:"):
            lines[i] = ln.replace("mid-run 사망·stall·세션 한도 도달",
                                  "mid-run 사망·세션 한도 도달")
            break

elif op == "prose-death":
    # ③ 등가변형(RED) — 구조→산문: 표 행은 지우고 class 명은 산문으로 남겨 grep 오라클을 속인다
    i = row_index(lambda l: "mid-run 사망" in l and "3-step runbook" in l)
    assert i is not None, "target row not found"
    del lines[i]
    for j, ln in enumerate(lines):
        if ln.startswith("### 3.2"):
            lines.insert(j, "mid-run 사망 케이스도 물론 중요하게 다룬다 (ADR-178 참조).")
            lines.insert(j + 1, "")
            break

elif op == "relocate-part3":
    # ③ 등가변형(GREEN 기대) — 3부 블록 전체를 다른 위치로 이동 (의미 보존, 위치만 변경)
    s = next(i for i, l in enumerate(lines) if l.startswith("## 3부"))
    block = lines[s:]
    rest = lines[:s]
    t = next(i for i, l in enumerate(rest) if l.startswith("## 1부"))
    lines = rest[:t] + block + [""] + rest[t:]

elif op == "synonym-labels":
    # ③ 등가변형(GREEN 기대) — class 라벨을 동의어로 개명 (정규화로 해소되어야 함)
    for i, ln in enumerate(lines):
        if ln.strip().startswith("| mid-run 사망 |"):
            lines[i] = ln.replace("| mid-run 사망 |", "| 실행 중 사망 |", 1)
        elif ln.strip().startswith("| stall (무출력 정체) |"):
            lines[i] = ln.replace("| stall (무출력 정체) |", "| 무출력 정체 |", 1)
        elif ln.strip().startswith("| 세션·주간 한도 |"):
            lines[i] = ln.replace("| 세션·주간 한도 |", "| 사용량 한도 도달 |", 1)

else:
    raise SystemExit("unknown op: %s" % op)

with open(dst, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines))
PY

# ─────────────────────────────────────────────────────────────────────────────
run_case() {
  local name="$1" expected="$2" doc="$3"
  local rc=0 out verdict
  out=$("$PYBIN" "$WORK/oracle.py" "$doc" 2>&1) || rc=$?
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

mutate_case() {
  local name="$1" expected="$2" op="$3"
  local dst="$WORK/mut-$op.md"
  if ! "$PYBIN" "$WORK/mutate.py" "$SKILL" "$dst" "$op" >/dev/null 2>&1; then
    echo "FAIL $name — mutation '$op' 적용 실패 (앵커 소실)"
    FAIL=$((FAIL+1))
    return
  fi
  run_case "$name" "$expected" "$dst"
}

echo "── AC-27 recovery procedure class coverage ──"

# 대조군 (INV-T4) — 정본 문서는 반드시 GREEN 이어야 한다.
run_case "baseline: 정본 session-recovery SKILL.md" GREEN "$SKILL"

# ① 제거
mutate_case "M1 제거: mid-run 사망 라우팅 행 삭제"          RED drop-death-row
# ② 주입
mutate_case "M2 주입: stall 행 진입점 셀 공란(커버 참칭)"    RED blank-stall-entry
# ③ 등가변형 — RED 축 (결함 + 표기 회피)
mutate_case "M3 등가변형(RED): frontmatter 에서만 stall 탈락" RED desc-drop-stall
mutate_case "M4 등가변형(RED): 구조→산문 (행 삭제+산문 잔존)" RED prose-death
# ③ 등가변형 — 정밀도 축 (순수 표기/위치 변경 → 거짓 RED 금지)
mutate_case "M5 등가변형(GREEN): 3부 블록 위치 이동"         GREEN relocate-part3
mutate_case "M6 등가변형(GREEN): class 라벨 동의어 개명"      GREEN synonym-labels

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
