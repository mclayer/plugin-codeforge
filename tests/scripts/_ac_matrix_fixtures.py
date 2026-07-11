#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/_ac_matrix_fixtures.py — shared fixture/CLI helper for the AC-traceability
zero-drop gate named tests (CFP-2603 G1 / ADR-145).

공통화(ADR-140 hygiene): AC-source(§5 표)·RTM(§8.1 표)·tests-root(ast symbol) 구성 + CLI 구동 +
distinct-marker aware assert 를 단일 모듈에 모아 test_ac_traceability_matrix.py 가 재사용한다.

underscore prefix = pytest 미수집(테스트 아님). 게이트 collect_test_symbols 가 walk 하나 def 이름이
`test_` 아니어서 AC 매핑 대상 아님(무해).
"""
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))

# 테스트-더블 주입점 — 기본 = 실 Dev-A core (CI·synthesis). reference oracle override 가능.
AC_TRACE_LIB = os.environ.get("AC_TRACE_LIB", os.path.join(REPO_ROOT, "scripts", "lib"))
AC_TRACE_PY = os.environ.get("AC_TRACE_PY", os.path.join(AC_TRACE_LIB, "check_ac_traceability_matrix.py"))

# ac_id API import (SSOT leaf) — sys.path 주입
if AC_TRACE_LIB not in sys.path:
    sys.path.insert(0, AC_TRACE_LIB)

SENTINEL = "ac-traceability-matrix"  # 도메인 sentinel (distinct-marker)


# ── fixture builders (Dev-A 실 파서 포맷: §5/§8 마크다운 표) ──────────────────
def write_ac_source(path, rows):
    """rows = [(id, source, tier), ...] → `## §5` + id/source/tier 표."""
    lines = ["## §5. Acceptance Criteria", "", "| ID | source | tier | statement |", "|---|---|---|---|"]
    for rid, src, tier in rows:
        lines.append(f"| {rid} | {src} | {tier} | given-when-then |")
    _write(path, "\n".join(lines) + "\n")


def write_ac_source_empty(path):
    _write(path, "## §5. Acceptance Criteria\n\n| ID | source | tier |\n|---|---|---|\n")


def write_ac_source_countonly(path):
    _write(path, "## §5. Acceptance Criteria\n\nacceptance_criteria_count: 3 (항목화 목록 없음 — 산문만)\n")


def write_rtm(path, rows):
    """rows = [(ac, tier, test), ...]; test=None → (명명 테스트 없음), 'TODO' → plain, else backtick."""
    lines = ["## §8. Test Contract", "", "### §8.1 RTM", "", "| AC | tier | 명명 테스트 | 검증 |", "|---|---|---|---|"]
    for ac, tier, test in rows:
        if test is None:
            cell = "(명명 테스트 없음)"
        elif test == "TODO":
            cell = "TODO"
        else:
            cell = f"`{test}`"
        lines.append(f"| {ac} | {tier} | {cell} | v |")
    _write(path, "\n".join(lines) + "\n")


def write_rtm_notable(path):
    _write(path, "## §8. Test Contract\n\n(RTM 표 미선언 — 미선언 §8)\n")


def write_rtm_placeholder(path):
    _write(path, "## §8. 개발 서사\n\n*(DeveloperPL 작성 예정 — Phase 2 PR에서)*\n")


def make_tests_root(root, def_names):
    """root 아래 test_gen.py 에 `def <name>(): assert True` 정의 + test_unrelated 1개."""
    os.makedirs(root, exist_ok=True)
    body = ["def test_unrelated():", "    pass", ""]
    for name in def_names:
        body.append(f"def {name}():")
        body.append("    assert True")
        body.append("")
    _write(os.path.join(root, "test_gen.py"), "\n".join(body))


def make_tests_root_comment_only(root, name):
    """name 이 주석/docstring/문자열 안에만 존재(실 def 없음) — F-ORACLE-GUARD."""
    os.makedirs(root, exist_ok=True)
    _write(
        os.path.join(root, "test_gen.py"),
        f"# planned: {name} (아직 실 def 아님)\n"
        f'"""{name} appears only in a docstring"""\n'
        f'_note = "{name}"\n'
        "def test_unrelated():\n    pass\n",
    )


def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


# ── CLI runner + distinct-marker asserts ─────────────────────────────────────
def run_gate(phase, ac_source, rtm, tests_root=None):
    """게이트 CLI 구동. 반환 (returncode:int, output:str[stdout+stderr])."""
    argv = [sys.executable, AC_TRACE_PY, "--phase", str(phase), "--ac-source", ac_source, "--rtm", rtm]
    if tests_root is not None:
        argv += ["--tests-root", tests_root]
    proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def assert_gate_pass(rc, out):
    assert rc == 0, f"expected PASS(exit 0), got {rc}\n{out}"


def assert_gate_fail(rc, out):
    """distinct-marker: exit 1 단독 판정 금지 — 도메인 sentinel ∧ Traceback 부재 병행 assert."""
    assert rc == 1, f"expected fail-closed(exit 1), got {rc}\n{out}"
    assert SENTINEL in out, f"도메인 sentinel '{SENTINEL}' 부재 — gate-verdict 아님(crash 의심)\n{out}"
    assert "Traceback (most recent call last)" not in out, f"python Traceback 감지 (crash≠gate-verdict)\n{out}"


def assert_gate_nonzero(rc, out):
    """non-PASS(fail-closed) — 정확한 코드 무관(argparse choices=exit2 등 수용)."""
    assert rc != 0, f"expected non-zero fail-closed, got {rc}\n{out}"
