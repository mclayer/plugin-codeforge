#!/usr/bin/env bash
# tests/scripts/test_incomplete_state_preservation_path.sh
# CFP-2984 Phase 2 (구현 lane) — AC-28 discriminating self-test.
#
# AC-28: 작업물 보존 절차 문서에서 미완결 상태의 산출 고정 경로 존재를 검사하면,
#        완결 경로만 존재하고 미완결 고정 경로가 부재한 경우 검사가 실패한다.
#
# ★ 완결 경로만 있는 문서는 중단 상황에서 쓸모가 없다 — "경로 존재" 를 완결 축으로만
#   세면 오라클이 항진한다. 따라서 상태 축을 정규화해 미완결 행을 별도로 요구한다.
#
# ★ 부속 축 (Change Plan §8.2-D tier B — State Transition 무효 전이):
#   `저장 실패 → 성공 보고` · `번들 미생성 → 재spawn 인계` 2 무효 전이가 문서에
#   금지로 선언돼 있어야 한다. 선언이 사라지면 RED.
#
# ★ hollow 아님의 증명 (§8.2-E INV-T4): baseline(정본 문서) = PASS 대조군 선행.
#   3방향 mutant = ① 제거 ② 주입(빈 껍데기 미완결 행) ③ 등가변형(RED/GREEN 2축).
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

cat > "$WORK/oracle.py" <<'PY'
# -*- coding: utf-8 -*-
"""AC-28 oracle — 미완결 상태 산출 고정 경로 + 무효 전이 선언 검사."""
import sys

PLACEHOLDER = {"", "-", "—", "–", "tbd", "TBD", "?", "(없음)", "없음", "n/a", "N/A"}

# 상태 축 정규화. '미완결' 을 먼저 본다 — '완결' 은 '미완결' 의 부분 문자열이다.
INCOMPLETE_PATS = ["미완결", "미완", "부분 산출", "부분산출", "중단", "incomplete", "partial"]
COMPLETE_PATS = ["완결", "complete", "done"]

# 무효 전이 2종 (from, to) 동의어 사전.
INVALID_TRANSITIONS = [
    (["저장 실패", "저장실패", "기록 실패", "persist fail", "save fail"],
     ["성공 보고", "성공보고", "성공으로 보고", "success 보고", "성공 리턴"]),
    (["번들 미생성", "번들미생성", "번들 부재", "bundle 미생성", "bundle 부재"],
     ["재spawn 인계", "재spawn", "re-spawn 인계", "re-spawn", "인계"]),
]


def state_of(cell):
    low = cell.lower()
    if any(p.lower() in low for p in INCOMPLETE_PATS):
        return "incomplete"
    if any(p.lower() in low for p in COMPLETE_PATS):
        return "complete"
    return None


def filled(cell):
    return cell.strip() not in PLACEHOLDER and len(cell.strip()) > 0


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


def section_lines(lines, heading_prefix):
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
    sec = section_lines(strip_fences(raw), "### 3.3")
    findings = []

    if not sec:
        print("VIOL structure: '### 3.3' 보존 경로 절이 없다 (fail-closed)")
        return 1

    tabs = tables_in(sec)
    if not tabs:
        print("VIOL structure: '### 3.3' 절에 보존 경로 표가 없다 (fail-closed)")
        return 1

    # (1) 상태 축 — 미완결 행이 산출 고정 행위 + 종료 표식을 모두 갖는가
    _, rows = tabs[0]
    states = {}
    good_incomplete = 0
    for r in rows:
        if len(r) < 3:
            continue
        st = state_of(r[0])
        if st is None:
            continue
        states.setdefault(st, 0)
        states[st] += 1
        if st == "incomplete" and filled(r[1]) and filled(r[2]):
            good_incomplete += 1

    if states.get("complete", 0) == 0:
        findings.append("VIOL state: 완결 경로 행이 없다 (대조 축 소실 — 표 파싱 의심)")
    if states.get("incomplete", 0) == 0:
        findings.append("VIOL state: 미완결 상태 행이 0건 — 완결 경로만 존재한다")
    elif good_incomplete == 0:
        findings.append("VIOL state: 미완결 행은 있으나 산출 고정 행위 또는 종료 표식 셀이 비었다")

    # (2) State Transition — 무효 전이 2종 선언 존재
    declared = []
    for _, rws in tabs[1:]:
        for r in rws:
            if r:
                declared.append(r[0])
    joined = " ".join(declared).lower()
    for idx, (froms, tos) in enumerate(INVALID_TRANSITIONS, 1):
        hit = False
        for d in declared:
            dl = d.lower()
            if any(f.lower() in dl for f in froms) and any(t.lower() in dl for t in tos):
                hit = True
                break
        if not hit:
            findings.append("VIOL transition: 무효 전이 #%d 선언이 없다 (from=%s to=%s)"
                            % (idx, froms[0], tos[0]))
    if not declared and not joined:
        findings.append("VIOL transition: 무효 전이 표 자체가 없다 (fail-closed)")

    if findings:
        for f in findings:
            print(f)
        return 1
    print("OK AC-28: 미완결 산출 고정 경로 %d건 + 무효 전이 2종 선언 충족" % good_incomplete)
    return 0


sys.exit(main())
PY

cat > "$WORK/mutate.py" <<'PY'
# -*- coding: utf-8 -*-
"""AC-28 mutation generator. usage: mutate.py <src> <dst> <op>"""
import sys

src, dst, op = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(src, encoding="utf-8").read().split("\n")


def idx_of(pred):
    for i, ln in enumerate(lines):
        if pred(ln):
            return i
    return None


def incomplete_row_idxs():
    return [i for i, ln in enumerate(lines)
            if ln.strip().startswith("| 미완결")]


if op == "drop-incomplete-rows":
    # ① 제거 — 미완결 행 전건 삭제 (완결 경로만 남긴다)
    for i in reversed(incomplete_row_idxs()):
        del lines[i]

elif op == "hollow-incomplete-row":
    # ② 주입 — 진짜 미완결 행을 지우고 '미완결' 라벨만 단 빈 껍데기 행을 삽입
    idxs = incomplete_row_idxs()
    assert idxs, "target rows not found"
    first = idxs[0]
    for i in reversed(idxs):
        del lines[i]
    lines.insert(first, "| 미완결 | — | — | (미배선) |")

elif op == "synonym-hollow":
    # ③ 등가변형(RED) — 상태 라벨을 동의어로 개명 + 산출 고정 행위 셀 공란화.
    #   리터럴 '미완결' 매칭 오라클이면 통과해버리는 회피형 결함이다.
    idxs = incomplete_row_idxs()
    assert idxs, "target rows not found"
    for i in idxs:
        cells = lines[i].strip().strip("|").split("|")
        cells[0] = " 부분 산출 "
        cells[1] = " — "
        lines[i] = "|" + "|".join(cells) + "|"

elif op == "synonym-intact":
    # ③ 등가변형(GREEN) — 상태 라벨만 동의어로 개명, 내용 무손상 (거짓 RED 금지)
    idxs = incomplete_row_idxs()
    assert idxs, "target rows not found"
    for i in idxs:
        cells = lines[i].strip().strip("|").split("|")
        cells[0] = cells[0].replace("미완결", "부분 산출(미완)")
        lines[i] = "|" + "|".join(cells) + "|"

elif op == "drop-transition-1":
    # State Transition — `저장 실패 → 성공 보고` 무효 전이 선언 삭제
    i = idx_of(lambda l: l.strip().startswith("| 저장 실패"))
    assert i is not None, "target row not found"
    del lines[i]

elif op == "drop-transition-2":
    # State Transition — `번들 미생성 → 재spawn 인계` 무효 전이 선언 삭제
    i = idx_of(lambda l: l.strip().startswith("| 번들 미생성"))
    assert i is not None, "target row not found"
    del lines[i]

elif op == "transition-synonym":
    # ③ 등가변형(GREEN) — 무효 전이 표기를 동의어로 재작성 (의미 보존)
    i = idx_of(lambda l: l.strip().startswith("| 저장 실패"))
    assert i is not None, "target row not found"
    cells = lines[i].strip().strip("|").split("|")
    cells[0] = " 저장실패 -> 성공으로 보고 "
    lines[i] = "|" + "|".join(cells) + "|"
    j = idx_of(lambda l: l.strip().startswith("| 번들 미생성"))
    assert j is not None, "target row not found"
    cells = lines[j].strip().strip("|").split("|")
    cells[0] = " 번들 부재 -> re-spawn 인계 "
    lines[j] = "|" + "|".join(cells) + "|"

else:
    raise SystemExit("unknown op: %s" % op)

with open(dst, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(lines))
PY

run_case() {
  local name="$1" expected="$2" doc="$3"
  local rc=0 out verdict
  out=$("$PYBIN" "$WORK/oracle.py" "$doc" 2>&1) || rc=$?
  if [ "$rc" -eq 0 ]; then verdict="GREEN"; else verdict="RED"; fi
  # ★ crash-as-RED 차단: 오라클이 예외로 죽어서 난 rc!=0 은 "검출"이 아니다.
  #   (실사건: 정규식 컴파일 오류로 전 케이스가 크래시했는데 mutant 는 전부 RED 로 보였다.)
  case "$out" in
    *Traceback*)
      echo "FAIL $name — 오라클 크래시(Traceback). RED 를 검출로 셀 수 없다"
      printf '%s
' "$out" | sed 's/^/       /'
      FAIL=$((FAIL+1))
      return ;;
  esac
  if [ "$verdict" = "RED" ] && ! printf '%s' "$out" | grep -q "VIOL"; then
    echo "FAIL $name — RED 인데 판정 근거 마커(VIOL)가 없다 (무증거 RED)"
    printf '%s
' "$out" | sed 's/^/       /'
    FAIL=$((FAIL+1))
    return
  fi
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

echo "── AC-28 incomplete-state preservation path ──"

run_case "baseline: 정본 session-recovery SKILL.md" GREEN "$SKILL"

mutate_case "M1 제거: 미완결 행 전건 삭제(완결 경로만)"        RED drop-incomplete-rows
mutate_case "M2 주입: 빈 껍데기 미완결 행(라벨만)"              RED hollow-incomplete-row
mutate_case "M3 등가변형(RED): 동의어 라벨 + 고정 행위 공란"     RED synonym-hollow
mutate_case "M4 등가변형(GREEN): 동의어 라벨 + 내용 무손상"      GREEN synonym-intact
mutate_case "M5 무효전이: 저장 실패→성공 보고 선언 삭제"        RED drop-transition-1
mutate_case "M6 무효전이: 번들 미생성→재spawn 인계 선언 삭제"    RED drop-transition-2
mutate_case "M7 등가변형(GREEN): 무효 전이 동의어 재작성"        GREEN transition-synonym

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
