#!/usr/bin/env bash
# tests/scripts/test_ledger_freshness_guard.sh
# CFP-2984 Phase 2 (구현 lane) — AC-11b discriminating self-test.
#
# AC-11b: freshness 픽스처(경계 직전 / 경계값 / 경계 초과)를 판정 함수에 입력하면
#         경계 직전·경계값은 fresh, 경계 초과는 stale 을 반환하고, 임계값은 해당 채널의
#         기대 기록 주기에서 유도된 값으로 문서에 근거가 기재되며, 임계를 임의로 키운
#         변이체는 경계 초과 픽스처에서 RED 로 전환된다.
#
# ★ BVA 3점 (Change Plan §8.2-D tier A — 정본 픽스처 2건의 결손 보정):
#   T-1 / **T 자신** / T+1. 정본 명세에는 경계값 T 자신이 없어 포함/배타가 미정이었다.
#   본 테스트는 문서가 선언한 부등호를 읽어 판정하며, 문서 기본값은 **배타**
#   (`격차 > T` 일 때만 stale, `격차 = T` 는 fresh — ADR-164 결정 5 부등호 승계).
#
# ★ 실 ledger 파일 **미접근** — 순수 함수 단위 테스트다. 판정 로직만 CI 위에 있고
#   데이터는 픽스처다 (Story `:454` 의 "ledger 기반 판정 = CI 미도달" 제약과 무충돌).
#
# ★ "충분히 큰 임계 → 영구 미발화" 우회 차단 = 2중 검출:
#   (1) 유도 검증 — 문서의 T 가 문서의 C 와 유도 규칙(T = k x C)에서 실제로 나오는가
#   (2) **절대 픽스처** — 경계 초과 픽스처를 T 에 상대적으로 만들지 않고 정본 초 단위
#       상수(1799 / 1800 / 1801)로 고정한다. 상대 픽스처면 임계를 키울 때 픽스처가
#       같이 밀려 검출력이 0 이 된다 (이 트랩이 본 AC 의 핵심 실패 양식이다).
#   ⇒ 정본 C 가 정당하게 바뀌면 본 테스트의 절대 상수도 함께 갱신해야 한다. 그것은
#     의도된 마찰이다 — 임계 변경 = 결정 변경이지 문서 편집이 아니다.
#
# ★ 천장: 본 검사는 T 가 **문서 안에서 자기정합**한지만 본다. C 자체가 실측으로 옳은지는
#   empirical calibration 미완이며(ADR-164 결정 6 proposal 상속) 기계 판정하지 않는다.
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
"""AC-11b oracle — freshness 임계 유도 검증 + BVA 3점 순수 함수 판정."""
import re
import sys

# 정본 절대 픽스처 (초). 상대 픽스처 금지 — 임계 인플레이션 검출력의 원천.
CANON_T_SEC = 1800.0
BVA = [("T-1 경계 직전", CANON_T_SEC - 1, "fresh"),
       ("T   경계값 자신", CANON_T_SEC, "fresh"),
       ("T+1 경계 초과", CANON_T_SEC + 1, "stale")]

PLACEHOLDER = {"", "-", "—", "–", "tbd", "TBD", "?", "(없음)", "없음", "n/a", "N/A"}

_UNIT = {"시간": 3600.0, "h": 3600.0, "분": 60.0, "min": 60.0, "m": 60.0,
         "초": 1.0, "s": 1.0, "ms": 0.001}
_RE_NUM_UNIT = re.compile(r"(\d+(?:\.\d+)?)\s*(시간|분|초|ms|min|h|m|s)")
_RE_ISO_DUR = re.compile(r"\bPT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?\b")
_RE_MULT = re.compile(r"T\s*=\s*(\d+(?:\.\d+)?)\s*(?:x|X|\*|×)\s*C")


def clean(cell):
    return cell.replace("*", "").replace("`", "").strip()


def durations(cell):
    """셀 안의 모든 기간 표기 → 초 리스트 (분/초/시간/ms/ISO 8601 기간 정규화)."""
    txt = clean(cell)
    out = []
    for m in _RE_ISO_DUR.finditer(txt):
        if not any(m.groups()):
            continue
        h, mi, s = (float(g) if g else 0.0 for g in m.groups())
        out.append(h * 3600 + mi * 60 + s)
        txt = txt.replace(m.group(0), " ")
    for num, unit in _RE_NUM_UNIT.findall(txt):
        out.append(float(num) * _UNIT[unit])
    return out


def single_duration(cell):
    """셀의 기간 표기들이 모두 같은 값일 때만 그 값 (불일치 = None, fail-closed)."""
    ds = durations(cell)
    if not ds:
        return None
    return ds[0] if all(abs(d - ds[0]) < 1e-9 for d in ds) else None


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


def freshness(gap_sec, threshold_sec, inclusive):
    """순수 판정 함수 — 격차와 임계만 받는다 (실 ledger 미접근)."""
    if gap_sec is None or threshold_sec is None:
        return "indeterminate"
    if gap_sec < 0:
        return "indeterminate"
    stale = (gap_sec >= threshold_sec) if inclusive else (gap_sec > threshold_sec)
    return "stale" if stale else "fresh"


def main():
    path = sys.argv[1]
    lines = strip_fences(open(path, encoding="utf-8").read().split("\n"))
    sec = section_lines(lines, "### 3.5")
    findings = []
    if not sec:
        print("VIOL structure: '### 3.5' freshness 절이 없다 (fail-closed)")
        return 1
    tabs = tables_in(sec)
    if not tabs:
        print("VIOL structure: '### 3.5' 절에 임계 표가 없다 (fail-closed)")
        return 1

    _, rows = tabs[0]
    cadence = thresh = mult = None
    cadence_basis = thresh_basis = None
    inclusive = None
    for r in rows:
        if len(r) < 2:
            continue
        item = clean(r[0])
        basis = clean(r[2]) if len(r) > 2 else ""
        if "기대 기록 주기" in item:
            cadence, cadence_basis = single_duration(r[1]), basis
        elif "유도 규칙" in item:
            m = _RE_MULT.search(clean(r[1]))
            mult = float(m.group(1)) if m else None
        elif "임계" in item:
            thresh, thresh_basis = single_duration(r[1]), basis
        elif "경계" in item:
            v = clean(r[1])
            inclusive = ("≥" in v) or (">=" in v) or ("이상" in v)

    if cadence is None:
        findings.append("VIOL doc: 기대 기록 주기(C) 값을 읽을 수 없다")
    if mult is None:
        findings.append("VIOL doc: 유도 규칙(T = k x C) 이 기재되지 않았다")
    if thresh is None:
        findings.append("VIOL doc: 임계(T) 값을 읽을 수 없다 (표기 불일치 포함)")
    if inclusive is None:
        findings.append("VIOL doc: 경계 포함/배타가 명시되지 않았다")
    for label, basis in (("C", cadence_basis), ("T", thresh_basis)):
        if basis is None or basis in PLACEHOLDER:
            findings.append("VIOL doc: %s 의 근거 셀이 비었다 (임계 근거 기재 의무)" % label)

    if not findings:
        derived = cadence * mult
        if abs(derived - thresh) > 1e-9:
            findings.append("VIOL derive: T=%.0fs 는 C=%.0fs x k=%g = %.0fs 에서 유도되지 않았다 "
                            "(임의 상수 의심)" % (thresh, cadence, mult, derived))

    if not findings:
        for label, gap, expect in BVA:
            got = freshness(gap, thresh, inclusive)
            if got != expect:
                findings.append("VIOL bva: %s (gap=%.0fs, T=%.0fs) expected=%s got=%s"
                                % (label, gap, thresh, expect, got))
        # 판정불가 축 (음수 격차) — stale 로 접지 않는다
        if freshness(-1, thresh, inclusive) != "indeterminate":
            findings.append("VIOL bva: 음수 격차를 indeterminate 로 반환하지 않는다")

    if findings:
        for f in findings:
            print(f)
        return 1
    print("OK AC-11b: C=%.0fs k=%g T=%.0fs boundary=%s / BVA(1799,1800,1801)=(fresh,fresh,stale)"
          % (cadence, mult, thresh, "inclusive" if inclusive else "exclusive"))
    return 0


sys.exit(main())
PY

cat > "$WORK/mutate.py" <<'PY'
# -*- coding: utf-8 -*-
"""AC-11b mutation generator. usage: mutate.py <src> <dst> <op>"""
import sys

src, dst, op = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(src, encoding="utf-8").read().split("\n")


def row_idx(token):
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|") and token in ln:
            return i
    return None


def set_cell(i, col, val):
    cells = lines[i].strip().strip("|").split("|")
    cells[col] = " %s " % val
    lines[i] = "|" + "|".join(cells) + "|"


T_ROW = "| 임계 (T) |"
C_ROW = "| 기대 기록 주기 상한 (C) |"
K_ROW = "| 유도 규칙 |"
B_ROW = "| 경계 포함/배타 |"

if op == "drop-threshold-row":
    i = row_idx(T_ROW)
    assert i is not None
    del lines[i]

elif op == "blank-threshold-basis":
    i = row_idx(T_ROW)
    assert i is not None
    set_cell(i, 2, "—")

elif op == "drop-derivation-row":
    i = row_idx(K_ROW)
    assert i is not None
    del lines[i]

elif op == "inflate-threshold":
    # 임계를 임의로 키움 (영구 미발화 우회)
    i = row_idx(T_ROW)
    assert i is not None
    set_cell(i, 1, "**120분 = 7200초**")

elif op == "inflate-threshold-iso":
    # 등가변형(RED) — 같은 인플레이션을 ISO 8601 기간 표기로 위장
    i = row_idx(T_ROW)
    assert i is not None
    set_cell(i, 1, "**PT2H**")

elif op == "iso-equivalent":
    # 등가변형(GREEN) — 동일 값을 ISO 8601 기간으로 표기
    i = row_idx(T_ROW)
    assert i is not None
    set_cell(i, 1, "**PT30M**")

elif op == "ms-equivalent":
    # 등가변형(GREEN) — C·T 를 밀리초 표기로
    i = row_idx(C_ROW)
    assert i is not None
    set_cell(i, 1, "**900000ms**")
    j = row_idx(T_ROW)
    assert j is not None
    set_cell(j, 1, "**1800000ms**")

elif op == "inclusive-boundary":
    # 경계를 포함으로 변경 → BVA 경계값 자신이 stale 로 뒤집힌다
    i = row_idx(B_ROW)
    assert i is not None
    set_cell(i, 1, "격차 >= T 이면 stale (경계값 포함)")

elif op == "inflate-both":
    # 유도 규칙은 지키면서 C·T 를 함께 키움 → 유도 검증은 통과, **절대 픽스처**만 잡는다.
    #   (이 케이스가 RED 여야 "2중 검출" 주장이 참이다 — 상대 픽스처였다면 GREEN 으로 샌다.)
    i = row_idx(C_ROW)
    assert i is not None
    set_cell(i, 1, "**30분**")
    j = row_idx(T_ROW)
    assert j is not None
    set_cell(j, 1, "**60분 = 3600초**")

elif op == "inconsistent-threshold":
    # 표기 내부 불일치 (30분 = 3600초) → fail-closed
    i = row_idx(T_ROW)
    assert i is not None
    set_cell(i, 1, "**30분 = 3600초**")

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
    printf '%s\n' "$out" | sed 's/^/       /'
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

echo "── AC-11b ledger freshness guard (BVA 3점 + 임계 유도) ──"

run_case "baseline: 정본 SKILL §3.5 + BVA 3점" GREEN "$SKILL"

mutate_case "M1 제거: 임계(T) 행 삭제"                       RED drop-threshold-row
mutate_case "M2 제거: 임계 근거 셀 공란"                      RED blank-threshold-basis
mutate_case "M3 제거: 유도 규칙 행 삭제(근거 없는 상수)"        RED drop-derivation-row
mutate_case "M4 주입: 임계를 임의로 키움(7200초)"              RED inflate-threshold
mutate_case "M5 주입: 표기 내부 불일치(30분 = 3600초)"         RED inconsistent-threshold
mutate_case "M6 주입: 경계를 포함으로 변경(경계값 뒤집힘)"       RED inclusive-boundary
mutate_case "M7 등가변형(RED): 인플레이션을 PT2H 로 위장"       RED inflate-threshold-iso
mutate_case "M8 절대 픽스처 축: C·T 동반 인플레이션"            RED inflate-both
mutate_case "M9 등가변형(GREEN): 동일 값 PT30M 표기"           GREEN iso-equivalent
mutate_case "M10 등가변형(GREEN): C·T 밀리초 표기"             GREEN ms-equivalent

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
