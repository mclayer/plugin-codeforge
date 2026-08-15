#!/usr/bin/env bash
# tests/scripts/test_split_plan_structure.sh
# CFP-2984 Phase 2 (구현 lane) — AC-7 discriminating self-test.
#
# AC-7: 장수명 lane 작업 계획서에 대해 분할 계획 구조 검사를 실행하면,
#       분할 단위 / 단위별 재개 입력 / 단위 간 확정 경계 3요소 중 하나라도 결손이면
#       검사가 실패하고, 요소를 제거한 변이체는 RED 로 전환된다.
#
# ★ 판정 범위 천장 (정직 라벨 — 비협상):
#   본 검사는 **구조 존재만** 판정한다. 기재된 분할이 실제로 컨텍스트 압박을 줄이는지,
#   즉 **분할 내용의 타당성은 미판정**이다 (AC-7a advisory / 사람 검토 소관).
#   "구조 GREEN = 분할이 타당하다" 로 읽으면 오독이며, 그런 주장을 하지 않는다.
#
# ★ hollow 아님의 증명 (§8.2-E INV-T4): baseline(정본 문서) = PASS 대조군 선행 +
#   임의 계획서 픽스처 GREEN 대조군. 3방향 mutant = ① 열 제거 ② 빈 셀 주입
#   ③ 등가변형(RED = 구조→산문으로 스키마 키 미해소 / GREEN = 헤더 동의어 개명).
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
"""AC-7 oracle — 분할 계획 3요소 스키마 결손 검사 (구조 축 only)."""
import sys

# 3요소 스키마 키 동의어. 'unit' 에 bare '단위' 를 넣으면 '단위별 재개 입력' 이
# 2개 키에 걸려 모호해지므로 수식어를 포함한 표현만 등재한다.
SCHEMA = {
    "unit": ["분할 단위", "작업 단위", "쪼갠 단위", "재개 단위", "덩어리", "unit"],
    "resume_input": ["재개 입력", "재개에 필요한 입력", "재개 시 필요한 입력",
                     "재개용 입력", "resume input", "재개 packet"],
    "boundary": ["확정 경계", "확정 산출 경계", "종료 경계", "커밋 경계", "boundary"],
}
PLACEHOLDER = {"", "-", "—", "–", "tbd", "TBD", "?", "(없음)", "없음", "n/a", "N/A"}


def key_of(cell):
    """헤더 셀 → 정확히 1개 스키마 키로 사상될 때만 그 키 (모호/미지 = None)."""
    low = cell.lower()
    hits = set()
    for k, pats in SCHEMA.items():
        for p in pats:
            if p.lower() in low:
                hits.add(k)
                break
    return hits.pop() if len(hits) == 1 else None


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


def main():
    path = sys.argv[1]
    lines = strip_fences(open(path, encoding="utf-8").read().split("\n"))
    findings = []

    # 분할 계획 표 = 스키마 키를 가장 많이 해소하는 표 (heading 위치 비의존).
    best, best_n, best_map = None, 0, {}
    for header, rows in tables_in(lines):
        kmap = {}
        for idx, cell in enumerate(header):
            k = key_of(cell)
            if k is not None and k not in kmap:
                kmap[k] = idx
        if len(kmap) > best_n:
            best, best_n, best_map = (header, rows), len(kmap), kmap

    if best is None or best_n == 0:
        print("VIOL schema: 분할 계획 3요소 스키마를 해소하는 표가 없다 "
              "(산문 서술만으로는 키 미해소 — fail-closed)")
        return 1

    header, rows = best
    for k in ("unit", "resume_input", "boundary"):
        if k not in best_map:
            findings.append("VIOL schema: 요소 '%s' 열이 결손이다 (해소된 키 = %s)"
                            % (k, sorted(best_map)))

    if not rows:
        findings.append("VIOL rows: 분할 계획 데이터 행이 0건이다")
    for rn, r in enumerate(rows, 1):
        for k, ci in sorted(best_map.items()):
            if ci >= len(r) or not filled(r[ci]):
                findings.append("VIOL rows: %d행의 '%s' 셀이 비었다" % (rn, k))

    if findings:
        for f in findings:
            print(f)
        return 1
    print("OK AC-7: 3요소 스키마 해소 + 데이터 %d행 전건 채움 "
          "(구조 축 only — 내용 타당성 미판정)" % len(rows))
    return 0


sys.exit(main())
PY

cat > "$WORK/mutate.py" <<'PY'
# -*- coding: utf-8 -*-
"""AC-7 mutation / fixture generator. usage: mutate.py <src> <dst> <op>"""
import sys

src, dst, op = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(src, encoding="utf-8").read().split("\n")


def plan_rows():
    """분할 계획 표(헤더+구분+데이터) 라인 인덱스 목록."""
    out = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("|") and ("분할 단위" in s or "단위별 재개 입력" in s):
            out.append(i)
    assert out, "plan header not found"
    h = out[0]
    idxs = [h]
    j = h + 1
    while j < len(lines) and lines[j].strip().startswith("|"):
        idxs.append(j)
        j += 1
    return idxs


def drop_col(idxs, col):
    for i in idxs:
        cells = lines[i].strip().strip("|").split("|")
        if col < len(cells):
            del cells[col]
        lines[i] = "|" + "|".join(cells) + "|"


if op == "drop-resume-col":
    # ① 제거 — '단위별 재개 입력' 열 전체 삭제
    drop_col(plan_rows(), 1)

elif op == "blank-resume-cell":
    # ② 주입 — 데이터 행 1개의 재개 입력 셀만 공란 (빈 요소 삽입)
    idxs = plan_rows()
    data = idxs[2:]
    assert data, "no data rows"
    i = data[0]
    cells = lines[i].strip().strip("|").split("|")
    cells[1] = " — "
    lines[i] = "|" + "|".join(cells) + "|"

elif op == "prose-only":
    # ③ 등가변형(RED) — 표를 지우고 3요소를 산문 문단으로 풀어씀 (스키마 키 미해소)
    idxs = plan_rows()
    first = idxs[0]
    for i in reversed(idxs):
        del lines[i]
    lines.insert(first, "계획서는 작업을 적당한 덩어리로 나누고, 각 덩어리를 다시 "
                        "시작하는 데 필요한 것들을 적고, 덩어리가 끝나는 지점을 정한다.")

elif op == "synonym-header":
    # ③ 등가변형(GREEN) — 헤더만 동의어로 개명 (정규화로 해소되어야 함)
    idxs = plan_rows()
    h = idxs[0]
    lines[h] = "| 작업 단위 | 재개에 필요한 입력 | 단위 종료 확정 경계 |"

elif op == "fixture-valid":
    # 임의 계획서 픽스처(GREEN) — SUT 가 skill 전용이 아님을 보인다
    lines = [
        "# 장수명 lane 작업 계획서 (fixture)",
        "",
        "| 분할 단위 | 단위별 재개 입력 | 단위 간 확정 경계 |",
        "|---|---|---|",
        "| 스키마 정의 | 대상 ADR 목록 | 커밋 1건 + WIP 표식 제거 |",
        "| 검증기 작성 | 스키마 커밋 SHA | 테스트 rc=0 출력 첨부 |",
        "",
    ]

elif op == "fixture-missing-boundary":
    # 임의 계획서 픽스처(RED) — 확정 경계 요소 결손
    lines = [
        "# 장수명 lane 작업 계획서 (fixture, 결손)",
        "",
        "| 분할 단위 | 단위별 재개 입력 |",
        "|---|---|",
        "| 스키마 정의 | 대상 ADR 목록 |",
        "",
    ]

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

echo "── AC-7 split plan structure ──"

run_case "baseline: 정본 session-recovery SKILL.md §3.6" GREEN "$SKILL"

mutate_case "F1 픽스처(GREEN): 임의 계획서 3요소 충족"        GREEN fixture-valid
mutate_case "F2 픽스처(RED): 확정 경계 요소 결손"             RED fixture-missing-boundary
mutate_case "M1 제거: '단위별 재개 입력' 열 삭제"              RED drop-resume-col
mutate_case "M2 주입: 재개 입력 셀 공란(빈 요소)"              RED blank-resume-cell
mutate_case "M3 등가변형(RED): 구조→산문 (스키마 키 미해소)"    RED prose-only
mutate_case "M4 등가변형(GREEN): 헤더 동의어 개명"             GREEN synonym-header

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
