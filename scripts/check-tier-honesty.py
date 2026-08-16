#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# CFP-2573 / ADR-144 §결정 7 — tier 정직 meta-gate lint (AC-6). self-lever measurement.
# tier: [measurement]
#
# 자기주제 (사활): measurement/advisory tier lever 는 자기 tier 만 주장해야 한다. 그 lever 의
#   tier-선언 라인에 긍정 enforcement 언어("block/deny/강제/물리차단")가 출현하면 tier 거짓 =
#   본 lint RED. "block 금지"(= blocking is forbidden) 같은 정직한 부정 서술은 정상 (closed-set
#   토큰만 매칭 — 단순 block/deny 단어 grep 금지). ADR-144 §결정 7 상속(ADR-142 §결정 7).
#
# lever REGISTRY (명시 테이블) — 각 lever = (name, expected_tier, artifact, label_re, label_desc):
#   | lever                | expected_tier | artifact                                            |
#   | vague-pause          | advisory      | archive/adr/ADR-025-...md (vague-pause 행 [advisory]) |
#   | reminder             | advisory      | hooks/story-transition-autonomy-reminder.py         |
#   | aggregate            | measurement   | scripts/lib/aggregate_stop_event.py                 |
#   | presence-lint(L3)    | measurement   | scripts/lib/check_subagent_wait_liveness_presence.py|
#   | tier-honesty(self)   | measurement   | scripts/check-tier-honesty.py                       |
#   | progress-commit      | advisory      | archive/adr/ADR-178-...md (§결정 8-1 ceiling 라벨 행) |
#
# 검사 2축:
#   Axis1 (verbatim tier 라벨 존재): 각 lever artifact 에 expected_tier 라벨 문자열 present. 부재 → RED.
#   Axis2 (enforcement-language 부재): tier-선언 라인(label_re 매칭 라인)에 긍정 enforcement 토큰
#     (closed set) 출현 시 RED. measurement/advisory lever 전부 대상.
#
# 정당 예외: vague-pause 회귀 lint 의 [물리강제] doc-integrity 라벨은 lever registry 대상 아님
#   (그 라벨은 문서 integrity lint 기제이지 stop-behavior lever 아님 — registry 에 넣지 않는다).
#
# home_marker = 6 lever artifact. 전부 부재 시 no-op(consumer). ReDoS-safe (라인 단위, 단일 .* 리터럴 tail).
#
# Usage:
#   check-tier-honesty.py             # repo root 기준 6 lever artifact 검사
#   check-tier-honesty.py --self-test # inline fixture mutation oracle (CI step)
# Exit: 0 = PASS / no-op, 1 = tier 정직 위반, 2 = setup error.

import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

MAX_SCAN_LINE = 8192  # ReDoS 안전 상한 (라인 truncate — 실 tier-선언 라인 << 8192)

# ── tier 라벨 문자열 (상수 — fixture/registry 는 이 상수를 참조해 라벨↔enforcement 리터럴 juxtaposition 회피) ──
MEAS_LABEL = "tier: [measurement]"
ADVP_LABEL = "tier: [advisory / priming]"
VP_ADV_LABEL = "[advisory]"
# ADR-178 §결정 8-1 advisory ceiling 라벨 (CFP-2966 Phase 2 — §결정 8-4 registry 등재)
PC_ADV_LABEL = "tier = advisory (ceiling)"

# ── tier-선언 라인 discriminator (label_re) — 매칭 라인 = 그 lever 의 tier 선언 bounded region ──
MEAS_RE = re.compile(r"tier:\s*\[measurement\]")
ADVP_RE = re.compile(r"tier:\s*\[advisory / priming\]")
# vague-pause lever 는 §결정 7 표 행(같은 라인에 vague-pause 앵커 + [advisory] 라벨) — 단일 .* (ReDoS-safe)
VP_RE = re.compile(r"vague-pause.*\[advisory\]")
# progress-commit lever 는 ADR-178 §결정 8-1 의 ceiling 라벨 라인 — 고정 리터럴 (quantifier 0)
PC_RE = re.compile(r"tier = advisory \(ceiling\)")

# ── 긍정 enforcement 토큰 (closed set) — 좁게 정의: "block 금지"/"deny 안 함" 부정 서술은 미매칭 ──
ENFORCEMENT_TOKENS = ["hard-block", "물리강제", "물리 차단", "강제 차단", "permissionDecision", "blocking-on-pr"]

# ── lever REGISTRY ──
LEVERS = [
    {
        "name": "vague-pause",
        "expected_tier": "advisory",
        "artifact": os.path.join("archive", "adr", "ADR-025-stop-discipline-non-whitelist-as-defect.md"),
        "label_re": VP_RE,
        "label_desc": "vague-pause 행 [advisory]",
    },
    {
        "name": "reminder",
        "expected_tier": "advisory",
        "artifact": os.path.join("hooks", "story-transition-autonomy-reminder.py"),
        "label_re": ADVP_RE,
        "label_desc": ADVP_LABEL,
    },
    {
        "name": "aggregate",
        "expected_tier": "measurement",
        "artifact": os.path.join("scripts", "lib", "aggregate_stop_event.py"),
        "label_re": MEAS_RE,
        "label_desc": MEAS_LABEL,
    },
    {
        "name": "presence-lint",
        "expected_tier": "measurement",
        "artifact": os.path.join("scripts", "lib", "check_subagent_wait_liveness_presence.py"),
        "label_re": MEAS_RE,
        "label_desc": MEAS_LABEL,
    },
    {
        "name": "tier-honesty",
        "expected_tier": "measurement",
        "artifact": os.path.join("scripts", "check-tier-honesty.py"),
        "label_re": MEAS_RE,
        "label_desc": MEAS_LABEL,
    },
    # CFP-2966 Phase 2 / ADR-178 §결정 8-4 — progress-commit 규범의 advisory ceiling 라벨 등재.
    # Axis1 = §결정 8-1 ceiling 라벨 presence / Axis2 = 그 라벨 라인의 enforcement 토큰 부재.
    # NOTE: ADR-178 §결정 8-2 는 "100% 기계강제"·"hard-gate" 를 **금지-언급 맥락**으로 담고 있으나,
    #   Axis2 정의역은 label_re 매칭 라인(= §결정 8-1 단일 라인) 뿐이라 그 서술 라인은 스캔 대상이 아니다
    #   (ADR-025 lever 가 같은 표 행 안에서 "runtime hard-deny 불가" 부정 서술을 담고도 GREEN 인 것과 동형 —
    #    closed-set 긍정 토큰만 매칭하므로 정직한 부정·금지 서술은 미매칭).
    {
        "name": "progress-commit",
        "expected_tier": "advisory",
        "artifact": os.path.join(
            "archive", "adr", "ADR-178-subagent-progress-commit-preservation.md"),
        "label_re": PC_RE,
        "label_desc": PC_ADV_LABEL,
    },
]


def scan_lever_content(lever, content):
    """단일 lever artifact content 검사. violations 리스트 반환 (빈 = PASS).

    Axis1: label_re 매칭 라인(tier-선언 라인) ≥1. 부재 → RED.
    Axis2: tier-선언 각 라인에 ENFORCEMENT_TOKENS 출현 시 RED (자기 tier 만 주장).
    """
    violations = []
    label_re = lever["label_re"]
    anchor_lines = []
    for i, raw in enumerate(content.splitlines(), start=1):
        line = raw if len(raw) <= MAX_SCAN_LINE else raw[:MAX_SCAN_LINE]
        if label_re.search(line):
            anchor_lines.append((i, line))
    # Axis1 — verbatim tier 라벨 존재
    if not anchor_lines:
        violations.append(
            f"[{lever['name']}] Axis1 위반 — tier 라벨 '{lever['label_desc']}' verbatim 부재 "
            f"({lever['artifact']}, expected_tier={lever['expected_tier']}). ADR-144 §결정 7."
        )
        return violations
    # Axis2 — tier-선언 라인 enforcement-language 부재
    for i, line in anchor_lines:
        for tok in ENFORCEMENT_TOKENS:
            if tok in line:
                violations.append(
                    f"[{lever['name']}] Axis2 위반 — tier-선언 라인 {i} 에 긍정 enforcement 토큰 "
                    f"'{tok}' 출현. measurement/advisory lever 는 자기 tier 만 주장 (긍정 block/deny/강제 금지). "
                    f"ADR-144 §결정 7 tier honesty."
                )
    return violations


def run_lint():
    present = [l for l in LEVERS if os.path.exists(l["artifact"])]
    if not present:
        print(f"[tier-honesty] {len(LEVERS)} lever artifact 전부 부재 — honest no-op (PASS, consumer degradation).")
        return 0
    all_violations = []
    for lever in LEVERS:
        if not os.path.exists(lever["artifact"]):
            all_violations.append(
                f"[{lever['name']}] Axis1 위반 — lever artifact 부재: {lever['artifact']} "
                f"(wrapper home 인데 lever 유실 → tier 라벨 검증 불가). ADR-144 §결정 7."
            )
            continue
        try:
            with open(lever["artifact"], "r", encoding="utf-8") as fh:
                content = fh.read()
        except (OSError, UnicodeDecodeError) as e:
            all_violations.append(f"[{lever['name']}] read error: {lever['artifact']}: {e}")
            continue
        all_violations.extend(scan_lever_content(lever, content))
    if all_violations:
        print("[tier-honesty] FAIL — tier 정직 meta-gate 위반 (ADR-144 §결정 7):")
        for v in all_violations:
            print("  " + v)
        return 1
    print(f"[tier-honesty] PASS — {len(LEVERS)} lever 전부 자기 tier 라벨 verbatim 존재 + "
          "measurement/advisory lever 에 긍정 enforcement 언어 0 (tier 정직 meta-gate).")
    return 0


def self_test():
    # mutation oracle (hollow 금지): 실제 스캔 함수(scan_lever_content) 호출 후 판정 대조 (presence-grep oracle 아님).
    # 라벨↔enforcement 리터럴 juxtaposition 회피 위해 fixture 는 상수({MEAS_LABEL} 등)를 참조 (self-scan false-positive 차단).
    meas_lever = {"name": "meas-fixture", "expected_tier": "measurement", "artifact": "<fixture>",
                  "label_re": MEAS_RE, "label_desc": MEAS_LABEL}
    advp_lever = {"name": "advp-fixture", "expected_tier": "advisory", "artifact": "<fixture>",
                  "label_re": ADVP_RE, "label_desc": ADVP_LABEL}
    vp_lever = {"name": "vp-fixture", "expected_tier": "advisory", "artifact": "<fixture>",
                "label_re": VP_RE, "label_desc": VP_ADV_LABEL}
    pc_lever = {"name": "pc-fixture", "expected_tier": "advisory", "artifact": "<fixture>",
                "label_re": PC_RE, "label_desc": PC_ADV_LABEL}

    green_meas = f"# banner\n# {MEAS_LABEL} self-lever\nbody line\n"
    green_advp = f'"""docstring\n{ADVP_LABEL}\n(NEVER block — deny/block 안 함)\n"""\n'
    green_vp = f"| 한 숨 쉬어가자 (vague-pause) | decision-null | `{VP_ADV_LABEL}` runtime hard-deny 불가 |\n"
    red_strip_meas = "# banner no label\nbody line\n"                         # 라벨 strip
    red_inject_meas = f"# {MEAS_LABEL} " + "물리강제" + " 차단 주입\n"          # measurement lever 물리강제 주입
    red_inject_advp = f"# {ADVP_LABEL} " + "blocking-on-pr" + " 강제 주입\n"    # advisory lever blocking-on-pr 주입
    # ADR-178 progress-commit lever (§결정 8-4). GREEN 은 같은 ADR 이 다른 라인에서 "hard-gate 금지" 를
    # 서술해도 Axis2 정의역(label_re 매칭 라인) 밖이라 무영향임을 함께 실증한다.
    green_pc = (f"1. **{PC_ADV_LABEL}.** 준수는 저작 규율이며 실준수는 비-PR-enforceable 이다.\n"
                "2. \"100% 기계강제\" · \"hard-gate\" 를 표방하는 서술을 금지한다.\n")
    red_strip_pc = "1. **tier 라벨 없음.** 준수는 저작 규율이다.\n"
    red_inject_pc = f"1. **{PC_ADV_LABEL}** " + "물리강제" + " 주입\n"

    cases = [
        ("GREEN: measurement lever 정상", meas_lever, green_meas, 0),
        ("GREEN: advisory reminder lever 정상 (부정 서술 block 금지 = 정상)", advp_lever, green_advp, 0),
        ("GREEN: vague-pause 행 [advisory] 정상", vp_lever, green_vp, 0),
        ("RED: 라벨 strip (measurement tier 라벨 제거)", meas_lever, red_strip_meas, 1),
        ("RED: measurement lever 에 물리강제 긍정주입", meas_lever, red_inject_meas, 1),
        ("RED: advisory lever 에 blocking-on-pr 긍정주입", advp_lever, red_inject_advp, 1),
        ("GREEN: ADR-178 progress-commit ceiling 라벨 정상 (같은 문서의 hard-gate 금지 서술은 무영향)",
         pc_lever, green_pc, 0),
        ("RED: ADR-178 ceiling 라벨 strip", pc_lever, red_strip_pc, 1),
        ("RED: ADR-178 ceiling 라벨 라인에 물리강제 긍정주입", pc_lever, red_inject_pc, 1),
    ]
    failed = []
    for name, lever, text, expect in cases:
        violations = scan_lever_content(lever, text)
        got = 1 if violations else 0
        status = "OK" if got == expect else "MISMATCH"
        if got != expect:
            failed.append((name, expect, got))
        print(f"  [{status}] {name} (expect exit {expect}, got {got})")
    if failed:
        print(f"[self-test] FAIL — {len(failed)} case mismatch")
        return 1
    print(f"[self-test] PASS — {len(cases)}/{len(cases)} case (mutation oracle: 라벨 strip + "
          "물리강제 주입 + blocking-on-pr 주입 discriminating).")
    return 0


def main(argv):
    args = argv[1:]
    if "--self-test" in args:
        return self_test()
    if args:
        print(f"[tier-honesty] setup note: 인자 무시 (repo root 기준 5 lever 검사): {args}", file=sys.stderr)
    return run_lint()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
