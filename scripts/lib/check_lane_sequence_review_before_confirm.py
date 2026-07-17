#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/lib/check_lane_sequence_review_before_confirm.py

CFP-2725 Phase 2 / Change Plan §8 RTM AC-21 — 요구사항→요구사항리뷰→확정→설계 lane 시퀀스 +
review-pass-before-confirm precondition 확정 배선 presence lint. Python SSOT engine
(thin wrapper = scripts/check-lane-sequence-review-before-confirm.sh, ADR-061 §결정 1).

목적:
  design-entry 확정 gate 가 요구사항리뷰 PASS 후·설계 진입 직전에 위치함(review-pass-before-confirm)
  + 해당 lane 시퀀스/전이 매핑이 각 governance 문서에 landed 되어 있는지(회귀/드리프트 방어)를
  정적으로 검사.
  검사 대상 (2 target — 둘 다 존재 + 각 anchor 존재해야 PASS):
    docs/orchestrator-playbook.md → `phase:요구사항-리뷰` / `user-final-sign-off-resolved`
    archive/adr/ADR-159-requirements-lane-enrichment-and-design-entry-signoff.md → `design-entry`

★ target-existence guard (repo 기본 관례와 의도적 이탈 — 근거 명문화):
  repo 기본 presence lint 관례 = target 부재 시 "honest no-op exit 0"(consumer degradation).
  본 lint 은 그 정반대 = **target 파일 부재 = exit 1 (FAIL)**. 근거:
    (1) 본 4-lint 은 wrapper-self 전용 — target = wrapper 소유 governance 문서(항상 존재).
        따라서 부재 = consumer degradation 이 아니라 회귀/오배선(vacuous PASS 금지).
    (2) Change Plan §8 RTM 이 target-existence guard(대상 부재=FAIL)를 명시 요구.
  → consumer 배포 금지: 워크플로 job 은 `if: github.repository == 'mclayer/plugin-codeforge'`
    로 guard(wrapper-self only), consumer-scripts.manifest 미등재.

hollow-gate guard (병행):
  target 존재하나 anchor 리터럴 부재 = exit 1 (born-hollow/드리프트 검출).
  "전 target 존재 + 전 anchor 존재" 만 exit 0.

정직 라벨 (advisory ceiling — over-claim 금지):
  presence(문서 anchor 존재)는 testable — 그러나 "사용자가 실제로 확정했는지"는 NOT testable.
  본 lint 은 advisory/warning tier(merge 미차단). 기계 강제 100% 아님.

CLI 계약 (QADev self-test 가 이 계약에 의존):
  python3 check_lane_sequence_review_before_confirm.py [--root <repo_root>] [--self-test]
    --root      : 검사 root (default = 스크립트 기준 repo root, CWD 독립). QADev fixture 검증용.
    --self-test : inline pos/neg fixture 자기검증(독립 임시 트리 — self-match tautology 회피).

Exit code:
  0 = PASS (전 target 존재 + 전 anchor 존재)
  1 = 위반 (target 부재[existence guard] 또는 anchor 부재[hollow/드리프트])
  2 = setup error (root 부재 / 읽기 실패 등 예외)

?젙洹쒖떇 誘몄궗?슜: 리터럴 `in` substring 검사 (정규식 backtracking 부재), 문서 단위 스캔.
"""

import argparse
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

LINT_NAME = "lane-sequence-review-before-confirm"

# REQUIRED (target_rel_path, [anchor_literals]) — Change Plan §8 RTM AC-21 확정 배선 anchor (2 target).
REQUIREMENTS = [
    ("docs/orchestrator-playbook.md", ["phase:요구사항-리뷰", "user-final-sign-off-resolved"]),
    ("archive/adr/ADR-159-requirements-lane-enrichment-and-design-entry-signoff.md", ["design-entry"]),
]

EXIT_PASS = 0       # 전 target 존재 + 전 anchor 존재
EXIT_VIOLATION = 1  # target 부재(existence guard) 또는 anchor 부재(hollow/드리프트)
EXIT_SETUP = 2      # 예외 (root 부재 / 읽기 실패 등)


def _default_root():
    """스크립트 위치(scripts/lib/) 기준 repo root (상위 2단계). CWD 독립."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def scan(root):
    """REQUIREMENTS 검사 → 실패 메시지 리스트 (빈 리스트 = PASS).

    target-existence guard: target 파일 부재 = FAIL (vacuous PASS 금지 — wrapper-self 전용).
    hollow-gate guard: target 존재하나 anchor 리터럴 부재 = FAIL (born-hollow/드리프트).
    읽기 실패 등 예외는 상위(run)로 전파 → exit 2 (setup-error).
    """
    failures = []
    for rel, anchors in REQUIREMENTS:
        path = os.path.join(root, *rel.split("/"))
        if not os.path.isfile(path):
            failures.append(f"FAIL: target 부재: {rel}")
            continue
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        for anchor in anchors:
            if anchor not in text:  # 리터럴 substring — ?젙洹쒖떇 誘몄궗?슜 (backtracking 부재)
                failures.append(f"FAIL: anchor 부재: {anchor} in {rel}")
    return failures


def run(root):
    try:
        failures = scan(root)
    except Exception as exc:  # 읽기 실패 / 예상외 오류 = setup-error
        print(f"[{LINT_NAME}] setup error: {exc}", file=sys.stderr)
        return EXIT_SETUP
    if failures:
        print(f"[{LINT_NAME}] FAIL — lane 시퀀스 + review-pass-before-confirm 확정 배선 presence 위반 "
              "(Change Plan §8 RTM AC-21 / target-existence + hollow-gate guard):")
        for msg in failures:
            print(f"  {msg}")
        print("  advisory/warning tier — merge 미차단. presence(문서 anchor 존재)는 testable — "
              "'사용자가 실제로 확정했는지'는 NOT testable (over-claim 금지).")
        return EXIT_VIOLATION
    print(f"[{LINT_NAME}] PASS — 전 target 존재 + 전 anchor 존재 ({len(REQUIREMENTS)} target). "
          "presence 는 testable, user actually confirmed 는 NOT testable (advisory tier).")
    return EXIT_PASS


def self_test():
    """독립 임시 fixture 트리로 pos/neg 판별 (self-match drift-0 tautology 회피 — 실 repo 미read).

    케이스:
      GREEN        전 target+anchor 존재 → exit 0
      RED anchor   REQUIREMENTS[0] 첫 anchor 결손 → exit 1 (hollow-gate 검출)
      RED target   REQUIREMENTS[0] target 파일 미생성 → exit 1 (target-existence guard)
    """
    import tempfile
    import shutil

    def build(root, mutate):
        for rel, anchors in REQUIREMENTS:
            if mutate == ("drop-target", rel):
                continue  # target 파일 미생성 (부재 케이스)
            keep = list(anchors)
            if mutate == ("drop-anchor", rel):
                keep = keep[1:]  # 첫 anchor 제거 (결손 주입)
            path = os.path.join(root, *rel.split("/"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            body = "독립 self-test fixture 본문 (tautology 회피 · 실 repo 미참조).\n"
            body += "".join(f"{a}\n" for a in keep)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(body)

    target0 = REQUIREMENTS[0][0]
    cases = [
        ("GREEN: 전 target+anchor 존재", None, EXIT_PASS),
        ("RED: anchor 결손 (hollow-gate 검출)", ("drop-anchor", target0), EXIT_VIOLATION),
        ("RED: target 부재 (existence guard)", ("drop-target", target0), EXIT_VIOLATION),
    ]
    failed = []
    for name, mutate, expect in cases:
        tmp = tempfile.mkdtemp(prefix=f"selftest-{LINT_NAME}-")
        try:
            build(tmp, mutate)
            got = EXIT_VIOLATION if scan(tmp) else EXIT_PASS
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        status = "OK" if got == expect else "MISMATCH"
        if got != expect:
            failed.append(name)
        print(f"  [{status}] {name} (expect exit {expect}, got {got})")
    if failed:
        print(f"[{LINT_NAME}] self-test FAIL — {len(failed)} case mismatch")
        return 1
    print(f"[{LINT_NAME}] self-test PASS — {len(cases)}/{len(cases)} case "
          "(RED→GREEN discriminating: anchor 결손 + target 부재 둘 다 exit 1).")
    return EXIT_PASS


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=f"{LINT_NAME} — 확정 배선 anchor presence lint (advisory/warning tier, wrapper-self 전용)."
    )
    parser.add_argument("--root", default=None,
                        help="repo root (default: 스크립트 기준 repo root — CWD 독립). QADev fixture 검증용.")
    parser.add_argument("--self-test", action="store_true",
                        help="inline pos/neg fixture 자기검증 (독립 임시 트리).")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    root = args.root if args.root is not None else _default_root()
    if not os.path.isdir(root):
        print(f"[{LINT_NAME}] setup error: root 디렉터리 부재: {root}", file=sys.stderr)
        return EXIT_SETUP
    return run(root)


if __name__ == "__main__":
    sys.exit(main())
