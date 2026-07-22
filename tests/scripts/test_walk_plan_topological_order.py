#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_walk_plan_topological_order.py

CFP-2782 AC-6b — walk_plan.py TOPOLOGICAL_ORDER 9→7 정합 (normative, Phase 2 승격).

deploy·deploy-review 2 lane plugin 물리 제거 후 codeforge family topological order 는
**7-tuple**(wrapper + 6 lane plugin)여야 한다. 기존 module frozen-assert
(`_EXPECTED_TOPOLOGICAL_ORDER`, scripts/lib/walk_plan.py `__main__`)는 **CI 미배선
dev-time tripwire** 였다(Change Plan §8.1/§8.5). 본 파일이 그 검증을 pytest 로 승격해
import-time 직접 assert + module self-test 실구동(distinct-marker) 양면으로 결박한다.

독립 oracle: EXPECTED_7 을 본 테스트가 스스로 고정(module 의 _EXPECTED 를 재수입하는
tautology 회피). module 의 _EXPECTED_TOPOLOGICAL_ORDER 는 `__main__` 지역 변수라 import
불가 — 대신 module 을 subprocess 로 실행해 그 내부 frozen-assert(TOPOLOGICAL_ORDER ==
_EXPECTED, 7-tuple) 통과를 stdout sentinel 로 확증.

주: 본 파일은 삭제 plugin 명(codeforge-deploy(-review))을 negative-assert 로 명명하므로
AC-3 zero-dangling 스캐너의 file-level allowlist(EXCL_FAKE)에 등재됨 — dangling ref 아님.
"""
import subprocess
import sys
from pathlib import Path

import walk_plan  # scripts/lib (tests/conftest.py sys.path 주입)

REPO_ROOT = Path(__file__).resolve().parents[2]
WALK_PLAN_PY = REPO_ROOT / "scripts" / "lib" / "walk_plan.py"

# 독립 oracle — CFP-2782 8-lane 정합 후 7-tuple (wrapper + 6 lane plugin). 순서 load-bearing.
EXPECTED_7 = [
    "codeforge",              # wrapper (최상위)
    "codeforge-requirements",
    "codeforge-design",
    "codeforge-review",
    "codeforge-develop",
    "codeforge-test",
    "codeforge-pmo",
]
# 물리 제거된 2 lane plugin — order 에 잔존 시 revert regression
DELETED_PLUGINS = ["codeforge-deploy", "codeforge-deploy-review"]


def test_topological_order_equals_seven_tuple():
    """TOPOLOGICAL_ORDER + get_topological_order() == 독립 7-tuple oracle (순서·멤버·카운트)."""
    assert walk_plan.TOPOLOGICAL_ORDER == EXPECTED_7, (
        "TOPOLOGICAL_ORDER != 7-tuple: %s" % walk_plan.TOPOLOGICAL_ORDER
    )
    assert walk_plan.get_topological_order() == EXPECTED_7, (
        "get_topological_order() != 7-tuple: %s" % walk_plan.get_topological_order()
    )


def test_topological_order_length_is_seven():
    """discriminating — 9-tuple revert(배포 2 plugin 재삽입) 시 RED."""
    assert len(walk_plan.TOPOLOGICAL_ORDER) == 7, (
        "TOPOLOGICAL_ORDER 길이 != 7 (9 revert 의심): %d" % len(walk_plan.TOPOLOGICAL_ORDER)
    )


def test_deleted_deploy_plugins_absent():
    """codeforge-deploy(-review) 는 order 및 derive LANE_PLUGINS 에서 부재."""
    order = walk_plan.get_topological_order()
    for plugin in DELETED_PLUGINS:
        assert plugin not in walk_plan.TOPOLOGICAL_ORDER, "%s 가 TOPOLOGICAL_ORDER 잔존" % plugin
        assert plugin not in order, "%s 가 get_topological_order() 잔존" % plugin
        assert plugin not in walk_plan.LANE_PLUGINS, "%s 가 derive LANE_PLUGINS 잔존" % plugin


def test_module_frozen_assert_passes_seven_tuple():
    """walk_plan.py __main__ 의 `_EXPECTED_TOPOLOGICAL_ORDER` frozen-assert(7-tuple)를 실 구동 검증.

    _EXPECTED_TOPOLOGICAL_ORDER 는 __main__ 지역이라 import 불가 → module 을 subprocess 로
    실행해 내부 `assert TOPOLOGICAL_ORDER == _EXPECTED_TOPOLOGICAL_ORDER` 통과를 확증.
    distinct-marker(subprocess fork 진정성, exit-code 단독 금지): exit 0 AND stdout sentinel
    "D7 동결, 7-tuple" 병행 assert — 미fork(파일 부재 등) 시 sentinel 부재로 genuine RED.
    """
    r = subprocess.run(
        [sys.executable, str(WALK_PLAN_PY)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert r.returncode == 0, (
        "walk_plan.py self-test 실패(frozen-assert RED 의심):\nSTDOUT:\n%s\nSTDERR:\n%s"
        % (r.stdout, r.stderr)
    )
    assert "D7 동결, 7-tuple" in r.stdout, (
        "frozen-assert sentinel 부재 — _EXPECTED_TOPOLOGICAL_ORDER 7-tuple 미검증(fork 진정성):\n%s"
        % r.stdout
    )
