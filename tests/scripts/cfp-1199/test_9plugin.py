#!/usr/bin/env python3
# tests/scripts/cfp-1199/test_9plugin.py
# CFP-1199 F1 — 9-plugin family reconciliation TDD Python 테스트 헬퍼
#
# ADR-061 정합: 외부 .py 파일 (heredoc-python 0)
# ADR-061 convention: 외부 .py, bats 가 python3 호출
# Sandbox: CBL_SKIP_ISSUE_CREATE=1
#
# 사용법:
#   python3 test_9plugin.py <walk_plan_dir> <tc_name>
#
# TC 목록:
#   prereq_module_importable     — walk_plan.py import 가능 확인
#   tc1_topological_count_9      — len(get_topological_order()) == 9
#   tc2_wrapper_first            — get_topological_order()[0] == "codeforge"
#   tc3_deploy_present           — "codeforge-deploy" 포함
#   tc4_deploy_review_present    — "codeforge-deploy-review" 포함
#   tc5_deploy_after_pmo         — deploy 두 lane 이 pmo 이후 위치
#   tc6_deploy_tier2             — classify_tier("codeforge-deploy") == TIER_2_LANE
#   tc7_deploy_review_tier2      — classify_tier("codeforge-deploy-review") == TIER_2_LANE
#   tc8_topological_exact_9      — TOPOLOGICAL_ORDER 9개 항목 정확히 일치 (중복/누락 0)
#   tc9_resolve_deploy_prereq    — deploy lane의 wrapper min_prereq 포함 9-plugin manifest 정상 resolve

import os
import sys

os.environ.setdefault("CBL_SKIP_ISSUE_CREATE", "1")


def load_module(walk_plan_dir: str):
    """walk_plan.py 를 sys.path 방식으로 임포트."""
    abs_dir = os.path.abspath(walk_plan_dir)
    if abs_dir not in sys.path:
        sys.path.insert(0, abs_dir)
    import walk_plan as mod
    return mod


def _run_tc(mod, tc_name: str) -> None:
    """지정된 TC 실행 — 실패 시 AssertionError."""

    # ── PREREQ ─────────────────────────────────────────────────────────────
    if tc_name == "prereq_module_importable":
        assert hasattr(mod, "TOPOLOGICAL_ORDER"), \
            "TOPOLOGICAL_ORDER 상수 미존재 — walk_plan.py 구조 확인 필요"
        assert hasattr(mod, "get_topological_order"), \
            "get_topological_order 함수 미존재"
        assert hasattr(mod, "classify_tier"), \
            "classify_tier 함수 미존재"
        print("PASS: walk_plan.py import + 필수 심볼 존재 확인")

    # ── TC-1: 9-plugin family 총 수 ────────────────────────────────────────
    elif tc_name == "tc1_topological_count_9":
        order = mod.get_topological_order()
        # 양성: 9개 정확히
        assert len(order) == 9, (
            f"TOPOLOGICAL_ORDER 길이 기대 9, 실제 {len(order)}: {order}\n"
            "CFP-1199: codeforge-deploy + codeforge-deploy-review 추가 필요 (ADR-087/088)"
        )
        # 음성: 7개 이하 아님 (구형 7-plugin 상태 차단)
        assert len(order) != 7, \
            "TOPOLOGICAL_ORDER 가 여전히 7-plugin — CFP-1199 D1 미적용"
        print(f"PASS TC-1: len(get_topological_order()) == 9")

    # ── TC-2: wrapper 가 첫 번째 ───────────────────────────────────────────
    elif tc_name == "tc2_wrapper_first":
        order = mod.get_topological_order()
        assert order[0] == "codeforge", (
            f"topological order 첫 번째 기대 'codeforge', 실제 '{order[0]}' "
            "(ADR-096 §결정 2 DAG invariant: wrapper 먼저)"
        )
        # 음성: deploy lane 이 첫 번째가 아님
        assert order[0] != "codeforge-deploy", \
            "codeforge-deploy 가 wrapper 보다 앞에 위치 — DAG 사이클 위반"
        print("PASS TC-2: get_topological_order()[0] == 'codeforge'")

    # ── TC-3: codeforge-deploy 포함 ────────────────────────────────────────
    elif tc_name == "tc3_deploy_present":
        order = mod.get_topological_order()
        assert "codeforge-deploy" in order, (
            f"'codeforge-deploy' 미포함 — CFP-1199 D1 미적용 (ADR-087 신설 lane). "
            f"현재 order: {order}"
        )
        print("PASS TC-3: 'codeforge-deploy' TOPOLOGICAL_ORDER 포함 확인")

    # ── TC-4: codeforge-deploy-review 포함 ────────────────────────────────
    elif tc_name == "tc4_deploy_review_present":
        order = mod.get_topological_order()
        assert "codeforge-deploy-review" in order, (
            f"'codeforge-deploy-review' 미포함 — CFP-1199 D1 미적용 (ADR-088 신설 lane). "
            f"현재 order: {order}"
        )
        print("PASS TC-4: 'codeforge-deploy-review' TOPOLOGICAL_ORDER 포함 확인")

    # ── TC-5: deploy 두 lane 이 pmo 이후 위치 (보수 lifecycle 순서) ───────
    elif tc_name == "tc5_deploy_after_pmo":
        order = mod.get_topological_order()
        assert "codeforge-pmo" in order, \
            "codeforge-pmo 가 TOPOLOGICAL_ORDER 에 없음"
        assert "codeforge-deploy" in order, \
            "codeforge-deploy 가 TOPOLOGICAL_ORDER 에 없음"
        assert "codeforge-deploy-review" in order, \
            "codeforge-deploy-review 가 TOPOLOGICAL_ORDER 에 없음"

        idx_pmo = order.index("codeforge-pmo")
        idx_deploy = order.index("codeforge-deploy")
        idx_deploy_review = order.index("codeforge-deploy-review")

        # 양성: deploy 두 lane 이 pmo 이후
        assert idx_deploy > idx_pmo, (
            f"codeforge-deploy (index {idx_deploy}) 가 "
            f"codeforge-pmo (index {idx_pmo}) 보다 앞에 있음 — "
            "보수 lifecycle 순서 위반 (ADR-087/088 DAG 결정)"
        )
        assert idx_deploy_review > idx_pmo, (
            f"codeforge-deploy-review (index {idx_deploy_review}) 가 "
            f"codeforge-pmo (index {idx_pmo}) 보다 앞에 있음"
        )
        # 양성: deploy-review 가 deploy 이후 (배포 전 리뷰 불가 — lifecycle 순서)
        assert idx_deploy_review > idx_deploy, (
            f"codeforge-deploy-review (index {idx_deploy_review}) 가 "
            f"codeforge-deploy (index {idx_deploy}) 보다 앞에 있음 — "
            "deploy 먼저, deploy-review 후행 invariant 위반"
        )
        print(
            f"PASS TC-5: pmo({idx_pmo}) → deploy({idx_deploy}) → "
            f"deploy-review({idx_deploy_review}) 순서 정합"
        )

    # ── TC-6: codeforge-deploy → TIER_2_LANE ──────────────────────────────
    elif tc_name == "tc6_deploy_tier2":
        result = mod.classify_tier("codeforge-deploy")
        assert result == mod.TIER_2_LANE, (
            f"classify_tier('codeforge-deploy') 기대 TIER_2_LANE({mod.TIER_2_LANE!r}), "
            f"실제 {result!r} — TOPOLOGICAL_ORDER 확장 시 LANE_PLUGINS 자동 정합 확인 필요"
        )
        # 음성: TIER_1_WRAPPER 아님
        assert result != mod.TIER_1_WRAPPER, \
            "codeforge-deploy 가 TIER_1_WRAPPER 로 잘못 분류됨 (wrapper 는 'codeforge' 만)"
        print(f"PASS TC-6: classify_tier('codeforge-deploy') == TIER_2_LANE")

    # ── TC-7: codeforge-deploy-review → TIER_2_LANE ───────────────────────
    elif tc_name == "tc7_deploy_review_tier2":
        result = mod.classify_tier("codeforge-deploy-review")
        assert result == mod.TIER_2_LANE, (
            f"classify_tier('codeforge-deploy-review') 기대 TIER_2_LANE({mod.TIER_2_LANE!r}), "
            f"실제 {result!r}"
        )
        assert result != mod.TIER_1_WRAPPER, \
            "codeforge-deploy-review 가 TIER_1_WRAPPER 로 잘못 분류됨"
        print(f"PASS TC-7: classify_tier('codeforge-deploy-review') == TIER_2_LANE")

    # ── TC-8: TOPOLOGICAL_ORDER 9개 항목 정확히 일치 (중복/누락 0) ────────
    elif tc_name == "tc8_topological_exact_9":
        order = mod.get_topological_order()
        expected_set = {
            "codeforge",
            "codeforge-requirements",
            "codeforge-design",
            "codeforge-review",
            "codeforge-develop",
            "codeforge-test",
            "codeforge-pmo",
            "codeforge-deploy",         # ADR-087 신설
            "codeforge-deploy-review",  # ADR-088 신설
        }
        actual_set = set(order)
        # 양성: 두 집합 일치
        assert actual_set == expected_set, (
            f"TOPOLOGICAL_ORDER 집합 불일치.\n"
            f"  누락: {expected_set - actual_set}\n"
            f"  초과: {actual_set - expected_set}"
        )
        # 양성: 중복 없음
        assert len(order) == len(actual_set), (
            f"TOPOLOGICAL_ORDER 중복 항목 존재: {order}"
        )
        print(f"PASS TC-8: TOPOLOGICAL_ORDER 9개 항목 정확히 일치 (중복/누락 0)")

    # ── TC-9: 9-plugin manifest로 deploy lane min_prereq 정상 resolve ─────
    elif tc_name == "tc9_resolve_deploy_prereq":
        # deploy lane 이 wrapper min_prereq 를 선언한 9-plugin manifest
        family_min_prereq = {
            "codeforge-requirements": {"codeforge": ">=5.0.0"},
            "codeforge-design": {"codeforge": ">=5.0.0"},
            "codeforge-review": {"codeforge": ">=5.0.0"},
            "codeforge-develop": {"codeforge": ">=5.0.0"},
            "codeforge-test": {"codeforge": ">=5.0.0"},
            "codeforge-pmo": {"codeforge": ">=5.0.0"},
            "codeforge-deploy": {"codeforge": ">=5.0.0"},          # ADR-087 신설
            "codeforge-deploy-review": {"codeforge": ">=5.0.0"},   # ADR-088 신설
        }
        consumer_pin = {
            "codeforge": "5.3.0",
            "codeforge-requirements": "5.3.0",
            "codeforge-design": "5.3.0",
            "codeforge-review": "5.3.0",
            "codeforge-develop": "5.3.0",
            "codeforge-test": "5.3.0",
            "codeforge-pmo": "5.3.0",
            "codeforge-deploy": "5.3.0",
            "codeforge-deploy-review": "5.3.0",
        }
        mismatches = mod.resolve_min_prereq_topological(family_min_prereq, consumer_pin)
        # 양성: 모든 버전 충족 → mismatch 없음
        assert mismatches == [], (
            f"9-plugin manifest resolve 에서 예상치 못한 mismatch: {mismatches}"
        )
        # 음성: RuntimeError (사이클) 없이 정상 완료 확인
        assert isinstance(mismatches, list)
        print("PASS TC-9: 9-plugin manifest deploy lane min_prereq resolve 정상 (acyclic)")

    else:
        print(f"UNKNOWN TC: {tc_name}", file=sys.stderr)
        sys.exit(2)


def main():
    if len(sys.argv) < 3:
        print(f"사용법: {sys.argv[0]} <walk_plan_dir> <tc_name>", file=sys.stderr)
        sys.exit(2)
    walk_plan_dir = sys.argv[1]
    tc_name = sys.argv[2]

    try:
        mod = load_module(walk_plan_dir)
    except Exception as e:
        print(f"FAIL: walk_plan.py 로드 실패 — {e}", file=sys.stderr)
        sys.exit(1)

    try:
        _run_tc(mod, tc_name)
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
