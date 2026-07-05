#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-2573 / ADR-144 §결정 2/7 + ADR-025 Amendment 3 — vague-pause taxonomy presence lint (L1 방어층)
# ADR-061 §결정 1 Python-SSOT 패턴 (thin wrapper = scripts/check-vague-pause-taxonomy-presence.sh)
#   + §결정 11 ReDoS-safe (라인 단위 스캔, 리터럴 substring — nested quantifier 부재)
#
# tier 문서화 (본 파일 = 자기주제 정직성 명시):
#   - vague-pause 정지 CLASS = tier: [advisory]  (명명·예방까지 — plain-text turn-end·tool-mediation 부재로
#       runtime hard-deny 불가, ADR-144 §결정 1/2 축 A2 payload=0). NEVER block: 본 lint 은 관측/검사만.
#   - 본 lint 기제 = [물리강제] doc-integrity  (ADR-025 문서에 taxonomy 등재가 존재하는지 검사하는
#       정적 integrity lint 이지 behavior 강제가 아니다 — ADR-144 §결정 7 유일 [물리강제] = 문서 integrity).
#
# 목적:
#   ADR-025 Phase 1 이 landed 시킨 vague-pause taxonomy 2 등재의 회귀(삭제/드리프트) 방어:
#     (a) §결정 7 illegal-stop 표 vague-pause 행 ("한 숨 쉬어가자" + decision-null discriminant + [advisory])
#     (b) §결정 10 reason_class subclass enum 의 policy_violation_vague_pause
#   이 삭제/드리프트하면 vague-pause class 가 taxonomy 에서 소실되므로 정적으로 회귀를 잡는다.
#
# 검사 (리터럴 presence — anchored substring):
#   (1) `vague-pause`               — §결정 7 illegal 표 vague-pause 행 discriminant 앵커
#   (2) `decision-null`             — decision-null pause discriminant 문구 (축 A2 payload=0 판별)
#   (3) `policy_violation_vague_pause` — §결정 10 subclass enum 등재
#   위 3 리터럴 중 하나라도 부재 시 exit 1.
#
# home_marker = ADR-025 파일 존재. 파일 부재(consumer) 시 honest no-op exit 0 —
#   hollow-gate vs consumer 구분: wrapper 만 archive/adr/ADR-025 를 보유하므로 파일 부재 = consumer degradation.
#
# Usage:
#   check_vague_pause_taxonomy_presence.py            # 인자 0개 = 기본 대상(ADR-025) 스캔
#   check_vague_pause_taxonomy_presence.py <path>...  # 파일 또는 디렉터리 (디렉터리 = ADR-025 탐색)
#   check_vague_pause_taxonomy_presence.py --self-test # inline fixture RED/GREEN 판별 (CI step)
#
# Exit code:
#   0 = PASS (3 리터럴 전부 존재) 또는 honest no-op (ADR-025 부재 = consumer)
#   1 = 위반 (3 리터럴 중 1+ 부재)
#   2 = setup error (인자 경로 미존재)
#
# ReDoS-safe: 리터럴 `in` substring 검사 (정규식 backtracking 부재), 라인/문서 단위 스캔.

import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# home_marker (wrapper governance sentinel — consumer 부재 시 honest no-op)
ADR025_BASENAME = "ADR-025-stop-discipline-non-whitelist-as-defect.md"
HOME_MARKER = os.path.join("archive", "adr", ADR025_BASENAME)

# 필수 taxonomy 리터럴 (anchored substring — ReDoS-safe)
REQUIRED_TOKENS = [
    "vague-pause",                    # §결정 7 illegal 표 vague-pause 행
    "decision-null",                  # discriminant 문구 (decision-null pause)
    "policy_violation_vague_pause",   # §결정 10 subclass enum
]


def scan_content(text):
    """text 안에 REQUIRED_TOKENS 전부 존재하는지 검사. 부재 토큰 리스트 반환 (빈 리스트 = PASS)."""
    missing = []
    for tok in REQUIRED_TOKENS:
        if tok not in text:
            missing.append(tok)
    return missing


def _resolve_target(args):
    """검사 대상 ADR-025 파일 경로 반환 (없으면 None = consumer no-op)."""
    if not args:
        return HOME_MARKER if os.path.exists(HOME_MARKER) else None
    for a in args:
        if os.path.isfile(a):
            if os.path.basename(a) == ADR025_BASENAME:
                return a
        elif os.path.isdir(a):
            cand = os.path.join(a, HOME_MARKER)
            if os.path.exists(cand):
                return cand
    return None


def self_test():
    # GREEN = 3 리터럴 전부 존재. RED mutation = vague-pause 행 삭제 / discriminant 삭제 / subclass 삭제.
    green = (
        '| "한 숨 쉬어가자" 류 (vague-pause — Amendment 3) | decision-null pause (verbalized) | `[advisory]` |\n'
        "- `policy_violation_vague_pause` (subclass enum)\n"
    )
    red_row_deleted = (
        # vague-pause 행 전체 삭제 → `vague-pause` + `decision-null` 소실 (subclass 만 잔존)
        "- `policy_violation_vague_pause` (subclass enum)\n"
    )
    red_discriminant_deleted = (
        # vague-pause 행 존치하나 decision-null discriminant 소실
        '| "한 숨 쉬어가자" 류 (vague-pause — Amendment 3) | (discriminant 소실) | `[advisory]` |\n'
        "- `policy_violation_vague_pause` (subclass enum)\n"
    )
    red_subclass_deleted = (
        # §결정 10 subclass 소실 (vague-pause 행은 존치)
        '| "한 숨 쉬어가자" 류 (vague-pause — Amendment 3) | decision-null pause (verbalized) | `[advisory]` |\n'
    )
    cases = [
        ("GREEN: 3 taxonomy 리터럴 전부 존재", green, 0),
        ("RED: vague-pause 행 삭제 (vague-pause + decision-null 소실)", red_row_deleted, 1),
        ("RED: decision-null discriminant 삭제", red_discriminant_deleted, 1),
        ("RED: policy_violation_vague_pause subclass 삭제", red_subclass_deleted, 1),
    ]
    failed = []
    for name, text, expect in cases:
        missing = scan_content(text)
        got = 1 if missing else 0
        status = "OK" if got == expect else "MISMATCH"
        if got != expect:
            failed.append((name, expect, got))
        print(f"  [{status}] {name} (expect exit {expect}, got {got}; missing={missing})")
    if failed:
        print(f"[self-test] FAIL — {len(failed)} case mismatch")
        return 1
    print(f"[self-test] PASS — {len(cases)}/{len(cases)} case (RED→GREEN discriminating 검증)")
    return 0


def main(argv):
    args = argv[1:]
    if "--self-test" in args:
        return self_test()
    # 인자 경로 유효성 (setup error 구분)
    for a in args:
        if not os.path.exists(a):
            print(f"[vague-pause-taxonomy-presence] setup error: 경로 미존재: {a}", file=sys.stderr)
            return 2
    target = _resolve_target(args)
    if target is None:
        print("[vague-pause-taxonomy-presence] ADR-025 파일 부재 — honest no-op "
              "(PASS, consumer degradation). vague-pause taxonomy 는 wrapper governance 전용.")
        return 0
    try:
        with open(target, "r", encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"[vague-pause-taxonomy-presence] setup error: 읽기 실패: {target}: {e}", file=sys.stderr)
        return 2
    missing = scan_content(text)
    if missing:
        print("[vague-pause-taxonomy-presence] FAIL — ADR-025 vague-pause taxonomy 등재 회귀 감지 "
              "(ADR-144 §결정 2/7 / ADR-025 Amendment 3):")
        for tok in missing:
            print(f"  부재 리터럴: `{tok}` — §결정 7 vague-pause 행 또는 §결정 10 subclass 소실/드리프트 가능.")
        return 1
    print(f"[vague-pause-taxonomy-presence] PASS — {target} 에 vague-pause taxonomy 3 리터럴 전부 존재 "
          "(§결정 7 행 + decision-null discriminant + §결정 10 subclass).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
