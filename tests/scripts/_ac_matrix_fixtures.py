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
import re
import shutil
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


# ── 적용성(applicability) AC-source writers (CFP-2609 §8.2 — ADR-145 §결정8) ──────
def write_ac_source_noac(path):
    """§5 present, AC 표 signature 부재 ∧ AC-ID 토큰 부재 → 비적용 positive(NO_AC_SURFACE)."""
    _write(path, "## §5. Acceptance Criteria\n\n(추적할 AC 없음 — marketplace sync / Epic close / sibling parity)\n")


def write_ac_source_degraded_token(path):
    """§5 에 산문 AC-ID 토큰 present ∧ parseable 표 부재 → degradation(UNDECIDABLE, anti-degradation)."""
    _write(path, "## §5. Acceptance Criteria\n\n산문으로 AC-1a 를 언급하나 항목화 표(id/source/tier signature) 부재.\n")


def write_ac_source_notoken_table(path):
    """§5 표 signature present ∧ ID 손상(XX-1, AC-ID 토큰 부재) → SURFACE_PRESENT→Hop1 malformed FAIL.

    ★ structural-signature keying(Codex P2): token-only keying 이면 비적용 PASS 로 새는 함정 fixture.
    """
    _write(
        path,
        "## §5. Acceptance Criteria\n\n| ID | source | tier | statement |\n|---|---|---|---|\n"
        "| XX-1 | derived | normative | given-when-then |\n",
    )


def write_ac_source_advonly(path):
    """§5 표 present + records well-formed + 0 normative(전부 declared/advisory) → 비적용-유사 PASS."""
    _write(
        path,
        "## §5. Acceptance Criteria\n\n| ID | source | tier | statement |\n|---|---|---|---|\n"
        "| AC-1 | user | advisory | given-when-then |\n| AC-2 | user | declared | given-when-then |\n",
    )


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
def _invoke(core, phase, ac_source=None, rtm=None, tests_root=None, rtm_not_yet=False,
            none_declaration=False, none_reason=None):
    """공유 저수준 invoker(run_gate/run_gate_core 공통) — CFP-2634 §결정9 none-flag 지원 포함.

    ac_source=None → --ac-source 생략(신규 optional 계약). none_declaration=True → --ac-applicability-none.
    none_reason 이 None 아니면(빈 문자열 포함) --none-reason 을 명시 전달(빈 사유도 신호로 전달 — AC-2 검증은
    core 담당). 반환 (returncode:int, output:str[stdout+stderr]).
    """
    argv = [sys.executable, core, "--phase", str(phase)]
    if ac_source is not None:
        argv += ["--ac-source", ac_source]
    if none_declaration:
        argv += ["--ac-applicability-none"]
    if none_reason is not None:
        argv += ["--none-reason", none_reason]
    if rtm_not_yet:
        argv += ["--rtm-not-yet"]
    elif rtm is not None:
        argv += ["--rtm", rtm]
    if tests_root is not None:
        argv += ["--tests-root", tests_root]
    proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def run_gate(phase, ac_source=None, rtm=None, tests_root=None, rtm_not_yet=False,
             none_declaration=False, none_reason=None):
    """게이트 CLI 구동. 반환 (returncode:int, output:str[stdout+stderr]).

    rtm_not_yet=True → --rtm-not-yet EXPLICIT 신호(Phase-1 RTM not-yet, rtm 생략). rtm 은 None 가능.
    ac_source=None → --ac-source 생략(신규 optional — CFP-2634 §결정9). none_declaration/none_reason =
    story_uri-absent 비적용 선언 플래그(CFP-2634 §결정9).
    """
    return _invoke(AC_TRACE_PY, phase, ac_source, rtm, tests_root, rtm_not_yet, none_declaration, none_reason)


def run_gate_core(core_py, phase, ac_source=None, rtm=None, tests_root=None, rtm_not_yet=False,
                   none_declaration=False, none_reason=None):
    """run_gate 와 동일하나 임의 core .py 경로 지정(mutation-kill 용). 반환 (returncode, output)."""
    return _invoke(core_py, phase, ac_source, rtm, tests_root, rtm_not_yet, none_declaration, none_reason)


def run_gate_none(reason=None, phase=1, ac_source=None, none_declaration=True, tests_root=None):
    """CFP-2634 §결정9 none-declaration 편의 래퍼(story_uri-absent 비적용 선언).

    both-absent 시뮬레이션 = none_declaration=False ∧ ac_source=None(둘 다 생략 — AC-1c).
    """
    return run_gate(phase, ac_source=ac_source, tests_root=tests_root, rtm_not_yet=True,
                     none_declaration=none_declaration, none_reason=reason)


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


def mutate_core(dst_dir, pattern, repl):
    """실 core + ac_id.py 를 dst_dir 로 복사하며 core 결정라인에 regex 치환 적용(portable in-process mutation).

    반환 (mutant_core_path:str, applied:bool). applied=False → diff 0(변조 미적용, INCONCLUSIVE 방지용).
    shell self-test 의 `mutate`/`run_mut_kill` 을 bash-비의존 python 으로 실현(Windows WSL-bash 부재 대응).
    """
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copy(os.path.join(AC_TRACE_LIB, "ac_id.py"), os.path.join(dst_dir, "ac_id.py"))
    with open(AC_TRACE_PY, encoding="utf-8") as fh:
        src = fh.read()
    mutated = re.sub(pattern, repl, src)
    dst = os.path.join(dst_dir, os.path.basename(AC_TRACE_PY))
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(mutated)
    return dst, (mutated != src)
