#!/usr/bin/env bash
# tests/scripts/test_stall_predicate.sh
# CFP-2984 Phase 2 (구현 lane) — AC-8 / AC-9 discriminating self-test.
#
# AC-8: wall-clock 상한 초과와 진행신호 부재가 **동시 성립할 때만** stall 을 반환한다.
# AC-9: 출력은 느리나 진행신호가 계속 도착하면 stall 이 아니며, 이 케이스를 제거한
#       변이체는 RED 로 전환된다.
#
# ★ 판정 함수는 **테스트 내부 순수 함수**다 (신규 production 스크립트 신설 0 —
#   AC-12b 정의역 대상 실측 1본 고정 제약). 구현 변종(ref / mut-*)을 같은 케이스
#   표에 통과시켜 mutation-kill 을 실증한다.
#
# ★ 값공간·경계 앵커 (실측):
#   - 진행신호 3원소 = output mtime / content grep / task-notification
#     [archive/adr/ADR-139-background-wait-liveness-gate.md 결정 1 INV-L3].
#     "마커 레지스트리" 자산은 부재하므로 INV-L3 산문 3원소 열거가 실재 정본이다.
#   - 경계는 **배타**: `elapsed > ceiling` 일 때만 초과. `elapsed == ceiling` 은 미초과.
#   - 판정불가(음수·비수치·NaN·빈 상한)는 **stall 이 아니다** → `indeterminate`.
#     판정불가를 stall 로 접으면 오탐이 폭증한다 (Change Plan §8.2-D EP 축).
#
# ★ hollow 아님의 증명 (§8.2-E INV-T4): `ref` 구현이 케이스 표 **전건 PASS**(대조군)
#   임을 먼저 보이고, 각 mutant 가 최소 1 케이스를 깨는 것을 보인다. baseline 이
#   이미 RED 면 mutant RED 는 아무것도 증명하지 않는다.
#
# INV-T3 순수 픽스처: 네트워크 0 · 실 ~/.claude/** 0 · 실 git 원격 0 · 쓰기는 mktemp -d 내부만.
# self-contained bash (tests/scripts 관례). Exit 0 = 전 케이스 PASS.

set -euo pipefail
export PYTHONIOENCODING=utf-8

PYBIN="$(command -v python3 || command -v python)"

PASS=0
FAIL=0

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

cat > "$WORK/runner.py" <<'PY'
# -*- coding: utf-8 -*-
"""AC-8/AC-9 stall 술어 + 케이스 표 + 구현 변종. usage: runner.py <variant>"""
import datetime
import sys

# ADR-139 결정 1 INV-L3 진행신호 3원소 (닫힌 값공간).
INV_L3 = ("output-mtime", "content-grep", "task-notification")

NOW = 1800000000  # 고정 관측 시각 (epoch seconds) — 결정론적 픽스처.
MIN_CASES = 20


def _iso(epoch):
    off = datetime.timezone(datetime.timedelta(hours=9))
    return datetime.datetime.fromtimestamp(epoch, off).isoformat()


def parse_dur(v, variant):
    """경과/상한 → 초(float). 판정 불가면 None."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        x = float(v)
        if x != x or x in (float("inf"), float("-inf")):
            return None
        return x if x >= 0 else None
    s = str(v).strip()
    if not s:
        return None
    if variant == "mut-no-unit-normalize":
        # ③ 등가변형 kill 대상 — 단위 접미사를 그냥 잘라내고 수치만 비교 (정규화 없음)
        num = s.rstrip("ms")
        try:
            x = float(num)
        except ValueError:
            return None
        return x if x >= 0 else None
    if s.endswith("ms"):
        body = s[:-2]
        scale = 0.001
    elif s.endswith("s"):
        body = s[:-1]
        scale = 1.0
    else:
        body = s
        scale = 1.0
    try:
        x = float(body)
    except ValueError:
        return None
    if x != x or x in (float("inf"), float("-inf")):
        return None
    return x * scale if x >= 0 else None


def parse_ts(s, variant):
    """진행신호 타임스탬프 → epoch 초. 표기 = epoch 초 / epoch 밀리초 / ISO 8601."""
    s = s.strip()
    if variant == "mut-no-ts-normalize":
        # ③ 등가변형 kill 대상 — epoch 초 10자리만 인식 (ISO·ms 는 미해석 = 부재 취급)
        return float(s) if s.isdigit() and len(s) == 10 else None
    if s.isdigit():
        return float(s) / 1000.0 if len(s) >= 13 else float(s)
    try:
        return datetime.datetime.fromisoformat(s).timestamp()
    except ValueError:
        return None


def progress_count(signals, ceiling_s, variant):
    """진행신호 개수 — 이름이 INV-L3 값공간이고 신선(0 <= age <= ceiling)해야 1건."""
    n = 0
    for raw in signals:
        if "@" not in raw:
            continue
        name, ts_raw = raw.split("@", 1)
        name = name.strip()
        if variant != "mut-open-signal-namespace" and name not in INV_L3:
            continue
        ts = parse_ts(ts_raw, variant)
        if ts is None:
            continue
        if variant != "mut-ignore-signal-freshness":
            age = NOW - ts
            if age < 0 or age > ceiling_s:
                continue
        n += 1
    return n


def stall_verdict(elapsed, ceiling, signals, variant="ref"):
    e = parse_dur(elapsed, variant)
    c = parse_dur(ceiling, variant)
    if e is None or c is None:
        if variant == "mut-indeterminate-as-stall":
            return "stall"
        return "indeterminate"

    exceeded = (e >= c) if variant == "mut-inclusive-boundary" else (e > c)

    if variant == "mut-drop-signal-conjunct":
        # ① 제거 — AND 의 진행신호 항을 삭제 (시간 축 단독 판정)
        return "stall" if exceeded else "not-stall"

    need = 2 if variant == "mut-drop-slow-normal-branch" else 1
    absent = progress_count(signals, c, variant) < need

    if exceeded and absent:
        return "stall"
    return "not-stall"


S_OUT = "output-mtime@%d" % (NOW - 10)
S_GREP = "content-grep@%d" % (NOW - 5)
S_TASK = "task-notification@%d" % (NOW - 3)
S_ISO = "content-grep@%s" % _iso(NOW - 10)
S_MS = "task-notification@%d" % ((NOW - 10) * 1000)
S_STALE = "output-mtime@%d" % (NOW - 2000)
S_FUTURE = "output-mtime@%d" % (NOW + 600)
S_UNKNOWN = "heartbeat@%d" % (NOW - 10)

# (id, elapsed, ceiling, signals, expected)
CASES = [
    # ── Decision Table 4행 전수 (2조건 AND) ──
    ("DT1 초과 AND 부재",            901, 900, [], "stall"),
    ("DT2 초과 AND 존재(느린 정상)",  901, 900, [S_OUT], "not-stall"),
    ("DT3 미초과 AND 부재",          899, 900, [], "not-stall"),
    ("DT4 미초과 AND 존재",          899, 900, [S_GREP], "not-stall"),
    # ── BVA (경계 배타) ──
    ("BVA elapsed = ceiling-1",      899, 900, [], "not-stall"),
    ("BVA elapsed = ceiling (배타)", 900, 900, [], "not-stall"),
    ("BVA elapsed = ceiling+1",      901, 900, [], "stall"),
    # ── Equivalence Partitioning: 판정불가는 stall 이 아니다 ──
    ("EP invalid elapsed = -1",      -1, 900, [], "indeterminate"),
    ("EP invalid elapsed = abc",     "abc", 900, [], "indeterminate"),
    ("EP invalid elapsed = NaN",     float("nan"), 900, [], "indeterminate"),
    ("EP invalid ceiling = 빈값",     901, "", [], "indeterminate"),
    ("EP valid elapsed = 900",       900, 900, [], "not-stall"),
    # ── 진행신호 3원소 부분집합 0 / 1 / 3 ──
    ("SUB 0개 → 부재",               901, 900, [], "stall"),
    ("SUB 1개(output mtime)",        901, 900, [S_OUT], "not-stall"),
    ("SUB 1개(content grep)",        901, 900, [S_GREP], "not-stall"),
    ("SUB 1개(task-notification)",   901, 900, [S_TASK], "not-stall"),
    ("SUB 3개 전부",                 901, 900, [S_OUT, S_GREP, S_TASK], "not-stall"),
    # ── ③ 등가변형: 타임스탬프 표기 (epoch 초 / ISO 8601 / 밀리초) ──
    ("NOTATION ISO 8601",            901, 900, [S_ISO], "not-stall"),
    ("NOTATION epoch 밀리초",         901, 900, [S_MS], "not-stall"),
    # ── ③ 등가변형: 시간 단위 s <-> ms ──
    ("UNIT elapsed 899000ms < 900s", "899000ms", "900s", [], "not-stall"),
    ("UNIT elapsed 901000ms > 900s", "901000ms", "900s", [], "stall"),
    # ── 신선도·값공간 폐쇄 (진행신호 참칭 차단) ──
    ("STALE 신호(age > ceiling)",     901, 900, [S_STALE], "stall"),
    ("FUTURE 신호(age < 0)",          901, 900, [S_FUTURE], "stall"),
    ("UNKNOWN 신호명(값공간 밖)",      901, 900, [S_UNKNOWN], "stall"),
]


def main():
    variant = sys.argv[1] if len(sys.argv) > 1 else "ref"
    if len(CASES) < MIN_CASES:
        print("VIOL harness: 케이스 표가 %d건 (최소 %d) — 표 공동화 의심"
              % (len(CASES), MIN_CASES))
        return 1
    bad = 0
    for cid, e, c, sig, exp in CASES:
        got = stall_verdict(e, c, sig, variant)
        if got != exp:
            print("  MISMATCH [%s] %s: expected=%s got=%s" % (variant, cid, exp, got))
            bad += 1
    if bad:
        print("  variant=%s 케이스 %d/%d 불일치" % (variant, bad, len(CASES)))
        return 1
    print("  variant=%s 케이스 %d건 전건 일치" % (variant, len(CASES)))
    return 0


sys.exit(main())
PY

run_variant() {
  local name="$1" variant="$2" expected="$3"
  local rc=0 out verdict
  out=$("$PYBIN" "$WORK/runner.py" "$variant" 2>&1) || rc=$?
  if [ "$rc" -eq 0 ]; then verdict="GREEN"; else verdict="RED"; fi
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

echo "── AC-8 / AC-9 stall predicate ──"

# 대조군 (INV-T4) — 정본 구현은 케이스 표 전건 PASS 여야 한다.
run_variant "baseline: ref 구현" ref GREEN

# ① 제거
run_variant "M1 제거: AND 진행신호 항 삭제(AC-8)"        mut-drop-signal-conjunct     RED
run_variant "M2 제거: 느린-정상 분기 삭제(AC-9, 1개 불인정)" mut-drop-slow-normal-branch RED
# ② 주입
run_variant "M3 주입: 판정불가를 stall 로 접음(EP)"       mut-indeterminate-as-stall   RED
run_variant "M4 주입: 경계 포함(elapsed >= ceiling)"      mut-inclusive-boundary       RED
run_variant "M5 주입: 신선도 무시(낡은 신호를 진행으로)"    mut-ignore-signal-freshness  RED
run_variant "M6 주입: 신호 값공간 개방(INV-L3 밖 수용)"     mut-open-signal-namespace    RED
# ③ 등가변형
run_variant "M7 등가변형: 시간 단위 s<->ms 정규화 삭제"     mut-no-unit-normalize        RED
run_variant "M8 등가변형: 타임스탬프 표기 정규화 삭제"       mut-no-ts-normalize          RED

echo "── 결과: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
