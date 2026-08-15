#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""test_absolute_claim_ratchet.py — 절대주장 결박 게이트(diff-scoped ratchet)의 판별력 검사.

이 스위트가 잡아야 하는 것은 **게이트 자신의 사각**이다. 본 Story 는 새로 만든 게이트가
자기 사각을 가진 채 GREEN 인 상태를 두 번 통과시켰다(§8.7 비교기의 skipped 슬롯 ·
watchdog bound). 그래서 여기서는 통과 경로만이 아니라

  · 절대주장이 결박 없이 들어오면 **FAIL 이 나는가** (판별력)
  · 토큰이 없는 평범한 diff 에서 **위반이 나오지 않는가** (오탐 대조군)
  · 삭제 줄·문맥 줄을 추가 줄로 **오인하지 않는가** (파서 정의역)
  · 검사 로직을 무력화한 **mutant 가 이 스위트를 RED 로 만드는가** (검사연극 차단)

를 함께 고정한다. mutant 는 원본 소스를 텍스트 변형해 **메모리 안에서만** 적재하며,
변형 anchor 가 어긋나면(=변형이 조용히 미적용) 즉시 실패한다 — 적용되지 않은 mutation 이
"mutant 통과"로 계상되는 가짜 RED 를 막기 위해서다.
"""

import types
from pathlib import Path

import pytest

import _absolute_claim_ratchet as ACR

SRC_PATH = Path(ACR.__file__).resolve()
REPO_ROOT = Path(__file__).resolve().parents[2]

# 게이트가 스스로에게도 적용되는지 재는 자기 적용 정의역.
GATE_OWN_PATHS = (
    "tests/scripts/_absolute_claim_ratchet.py",
    "tests/scripts/test_absolute_claim_ratchet.py",
    ".github/workflows/absolute-claim-ratchet.yml",
)

# 어휘 고정 기대값. 아래 별칭은 위치 기반이라 순서가 바뀌어도 검사가 성립한다.
EXPECTED_TOKENS = ("손실 0", "잔여 0", "무손상", "무조건", "항상", "전건", "원자적", "불가능", "0건")  # [ceiling: 어휘 고정 기대값 리터럴 — 검사 대상의 mention 이며 주장이 아니다]

T_A = EXPECTED_TOKENS[4]
T_B = EXPECTED_TOKENS[2]


# ═══════════════════════════ diff fixture 빌더 ═══════════════════════════════════
def make_file_diff(path, added=(), removed=(), context=(), start_old=10, start_new=10):
    """단일 파일 unified diff 조각. 문맥 → 삭제 → 추가 순으로 배치한다."""
    body = [" " + c for c in context] + ["-" + r for r in removed] + ["+" + a for a in added]
    old_n = len(context) + len(removed)
    new_n = len(context) + len(added)
    return "\n".join([
        "diff --git a/%s b/%s" % (path, path),
        "index 1111111..2222222 100644",
        "--- a/%s" % path,
        "+++ b/%s" % path,
        "@@ -%d,%d +%d,%d @@" % (start_old, old_n, start_new, new_n),
        *body,
        "",
    ])


def claim_line(token, suffix=""):
    return "# 이 절차는 %s 성립한다%s" % (token, suffix)


SRC_FILE = "scripts/lib/example_module.py"
TEST_FILE = "tests/unit/test_example.py"


# ═══════════════════════════ 어휘 고정 ═══════════════════════════════════════════
def test_vocabulary_is_pinned():
    """어휘가 조용히 축소되면(=검사 정의역 축소) 이 검사가 먼저 깨진다."""
    assert set(ACR.TOKENS) == set(EXPECTED_TOKENS)
    assert len(ACR.TOKENS) == len(EXPECTED_TOKENS)


def test_vocabulary_is_korean_only():
    """영문 등가어는 이 repo 에서 오탐원이라 담지 않는다(`always()` 16 site 실측)."""
    for tok in ACR.TOKENS:
        assert any("가" <= ch <= "힣" or ch.isdigit() for ch in tok)
        assert not any("a" <= ch.lower() <= "z" for ch in tok)


# ═══════════════════════════ AC1 판별력 ══════════════════════════════════════════
def test_ac1a_unbound_claim_line_is_violation():
    """절대주장 줄을 테스트 변경 없이 추가 → FAIL."""
    diff = make_file_diff(SRC_FILE, added=[claim_line(T_A)])
    result = ACR.evaluate(diff)
    assert len(result["violations"]) == 1
    v = result["violations"][0]
    assert v.disposition == "unbound"
    assert v.path == SRC_FILE
    assert T_A in v.tokens


def test_ac1b_ceiling_marker_discharges_claim():
    """같은 줄에 `[ceiling: 사유]` 부착 → PASS."""
    diff = make_file_diff(SRC_FILE, added=[claim_line(T_A, "  # [ceiling: 실측 수단 부재 — 리뷰 판정]")])
    result = ACR.evaluate(diff)
    assert result["violations"] == []
    assert [c.disposition for c in result["claims"]] == ["ceiling"]


def test_ac1c_test_accompaniment_discharges_claim():
    """같은 diff 에 tests/** 변경 동반 → PASS (동반 강제 경로)."""
    diff = (make_file_diff(SRC_FILE, added=[claim_line(T_A)])
            + make_file_diff(TEST_FILE, added=["def test_something():", "    assert True"]))
    result = ACR.evaluate(diff)
    assert result["tests_touched"] is True
    assert result["violations"] == []
    assert [c.disposition for c in result["claims"]] == ["test-accompanied"]


# ═══════════════════════════ AC2 대조군 (오탐 0) ═════════════════════════════════
def test_ac2_control_plain_added_lines_yield_no_violation():
    """절대주장 토큰이 없는 평범한 추가 줄만 있는 diff → 위반 0 · claim 0."""
    diff = make_file_diff(SRC_FILE, added=[
        "def resolve(path):",
        "    # 경로를 정규화해서 돌려준다",
        "    return os.path.abspath(path)",
        "# 실패 시 사유를 남기고 호출자에게 위임한다",
    ])
    result = ACR.evaluate(diff)
    assert result["claims"] == []
    assert result["violations"] == []


def test_ac2_control_holds_without_test_accompaniment():
    """대조군은 동반 완화에 기대지 않는다 — strict 모드에서도 위반 0."""
    diff = make_file_diff(SRC_FILE, added=["    return sorted(set(paths))"])
    result = ACR.evaluate(diff, allow_test_accompaniment=False)
    assert result["violations"] == []


# ═══════════════════════════ 천장 각인 (패러프레이즈 FN) ═════════════════════════
# 토큰 목록 **밖**의 등가 표현. 어느 것도 TOKENS 의 문자열을 포함하지 않는다.
PARAPHRASES = (
    "이 경로에서 손실은 발생하지 않는다",
    "어떤 경우에도 깨지지 않는다",
    "예외 없이 성립하며 되돌릴 수 없다",
)


def test_paraphrased_absolute_claim_is_outside_detection_domain():
    """★ 이 테스트는 **결함을 잡지 않는다 — 천장을 각인한다.**

    검사기는 어휘 목록 매칭이라 같은 절대주장을 목록 밖 표현으로 쓰면 놓친다(FN).
    그 사실을 산문으로만 적어두면 이 게이트가 겨냥하는 바로 그 class(글로 쓴 단정이
    코드보다 넓다)를 검사기 자신이 저지르는 꼴이라, 못 잡는 범위를 assert 로 고정한다.

    ⇒ 누군가 검사기를 의미 축으로 넓히면 이 테스트가 **RED** 가 된다. 그때 해야 할 일은
      이 테스트를 지우는 게 아니라 모듈 docstring 의 천장 문구를 함께 갱신하는 것이다.
      (단일 문구 우연 통과가 아님을 보이려고 등가 표현을 여러 개 넣는다.)"""
    assert len(PARAPHRASES) >= 2
    for p in PARAPHRASES:
        assert ACR.match_tokens(p) == [], "등가 표현이 어휘에 걸리면 이 각인은 무의미하다: %r" % p
    diff = make_file_diff(SRC_FILE, added=["# " + p for p in PARAPHRASES])
    result = ACR.evaluate(diff, allow_test_accompaniment=False)
    assert result["claims"] == []
    assert result["violations"] == []


# ═══════════════════════════ [bound:] 강한 해소 ══════════════════════════════════
KNOWN = frozenset({"test_real_symbol", "TestRealClass"})
GHOST = "test_symbol_that_does_not_exist"


def test_bound_marker_with_existing_symbol_discharges():
    diff = make_file_diff(SRC_FILE, added=[claim_line(T_A, "  # [bound: test_real_symbol]")])
    result = ACR.evaluate(diff, allow_test_accompaniment=False, symbol_index=KNOWN)
    assert result["violations"] == []
    assert [c.disposition for c in result["claims"]] == ["bound"]


def test_bound_marker_with_missing_symbol_is_violation():
    """실재하지 않는 테스트 이름을 대는 것이 가장 값싼 우회라 미해소는 위반이다."""
    diff = make_file_diff(SRC_FILE, added=[claim_line(T_A, "  # [bound: %s]" % GHOST)])
    result = ACR.evaluate(diff, allow_test_accompaniment=False, symbol_index=KNOWN)
    assert len(result["violations"]) == 1
    assert result["violations"][0].disposition == "unresolved-bound"


def test_unresolved_bound_outranks_test_accompaniment():
    """미해소가 tests/** 동반으로 씻겨나가면 안 된다 (empty-ceiling 과 같은 원리)."""
    diff = (make_file_diff(SRC_FILE, added=[claim_line(T_A, "  # [bound: %s]" % GHOST)])
            + make_file_diff(TEST_FILE, added=["def test_x():", "    assert True"]))
    result = ACR.evaluate(diff, symbol_index=KNOWN)
    assert result["tests_touched"] is True
    assert len(result["violations"]) == 1
    assert result["violations"][0].disposition == "unresolved-bound"


def test_empty_ceiling_outranks_bound_marker():
    """우선순위 최상단은 empty-ceiling — 유효한 bound 가 함께 있어도 빈 마커가 이긴다."""
    diff = make_file_diff(SRC_FILE, added=[
        claim_line(T_A, "  # [ceiling:] [bound: test_real_symbol]")])
    result = ACR.evaluate(diff, allow_test_accompaniment=False, symbol_index=KNOWN)
    assert [c.disposition for c in result["claims"]] == ["empty-ceiling"]


def test_bound_marker_empty_or_malformed_symbol_is_violation():
    for marker in ("  # [bound:]", "  # [bound: 두 단어 아님]", "  # [bound: 9invalid]"):
        diff = make_file_diff(SRC_FILE, added=[claim_line(T_A, marker)])
        result = ACR.evaluate(diff, allow_test_accompaniment=False, symbol_index=KNOWN)
        assert len(result["violations"]) == 1, marker
        assert result["violations"][0].disposition == "unresolved-bound", marker


def test_symbol_index_defaults_to_fail_closed():
    """symbol_index 미제공 시 `[bound:]` 를 통과시키면 검증 없는 해소가 된다."""
    diff = make_file_diff(SRC_FILE, added=[claim_line(T_A, "  # [bound: test_real_symbol]")])
    result = ACR.evaluate(diff, allow_test_accompaniment=False)
    assert [c.disposition for c in result["claims"]] == ["unresolved-bound"]


def test_bound_resolution_is_ast_based_not_grep(tmp_path):
    """심볼 실재 판정은 `ast` 여야 한다 — grep 이면 주석·docstring·문자열 안 이름이 통과한다.

    수집기는 `check_ac_traceability_matrix.collect_test_symbols`(Hop3 born-missing) 재사용."""
    root = tmp_path / "tests"
    root.mkdir()
    (root / "test_sample.py").write_text(
        '"""docstring 안 이름: test_ghost_in_docstring"""\n'
        "# 주석 안 이름: test_ghost_in_comment\n"
        "MENTION = 'test_ghost_in_string'\n"
        "def test_real_symbol():\n"
        "    pass\n"
        "class TestRealClass:\n"
        "    def test_method_symbol(self):\n"
        "        pass\n",
        encoding="utf-8")
    syms = ACR.collect_bound_symbols(tests_root=str(root))
    assert syms is not None
    for real in ("test_real_symbol", "TestRealClass", "test_method_symbol"):
        assert real in syms, real
    for ghost in ("test_ghost_in_docstring", "test_ghost_in_comment", "test_ghost_in_string"):
        assert ghost not in syms, "grep 기반이면 통과했을 이름이 해소됐다: %s" % ghost


def test_missing_tests_root_is_undecidable_not_pass(tmp_path):
    """루트 부재는 통과가 아니라 판정불가(None) — 호출자가 fail-closed 로 다룬다."""
    assert ACR.collect_bound_symbols(tests_root=str(tmp_path / "없는디렉터리")) is None


# ═══════════════════════════ 빈 ceiling 마커 차단 ════════════════════════════════
def test_empty_ceiling_reason_is_violation():
    diff = make_file_diff(SRC_FILE, added=[claim_line(T_A, "  # [ceiling:]")])
    result = ACR.evaluate(diff)
    assert len(result["violations"]) == 1
    assert result["violations"][0].disposition == "empty-ceiling"


def test_punctuation_only_ceiling_reason_is_violation():
    """`[ceiling: -]` 류 형식만 갖춘 사유는 사유로 인정하지 않는다."""
    diff = make_file_diff(SRC_FILE, added=[claim_line(T_A, "  # [ceiling: --- ]")])
    result = ACR.evaluate(diff)
    assert len(result["violations"]) == 1
    assert result["violations"][0].disposition == "empty-ceiling"


def test_ceiling_marker_on_preceding_line_does_not_discharge():
    """마커는 **같은 줄**에만 적용된다 — 앞줄 마커로 아랫줄을 풀어주지 않는다.

    저자가 이 검사를 만들면서 실제로 먼저 걸린 형상이라 회귀로 고정한다."""
    diff = make_file_diff(SRC_FILE, added=[
        "# [ceiling: 앞줄에 달아둔 사유]",
        claim_line(T_A),
    ])
    result = ACR.evaluate(diff, allow_test_accompaniment=False)
    assert len(result["violations"]) == 1
    assert result["violations"][0].disposition == "unbound"


def test_empty_ceiling_outranks_test_accompaniment():
    """빈 마커는 tests/** 동반으로 씻겨나가지 않는다 — 아니면 규칙 ②가 사문이 된다."""
    diff = (make_file_diff(SRC_FILE, added=[claim_line(T_A, "  # [ceiling: ]")])
            + make_file_diff(TEST_FILE, added=["def test_x():", "    assert True"]))
    result = ACR.evaluate(diff)
    assert result["tests_touched"] is True
    assert len(result["violations"]) == 1
    assert result["violations"][0].disposition == "empty-ceiling"


# ═══════════════════════════ AC5 파서 정의역 ═════════════════════════════════════
def test_ac5_deleted_line_with_token_is_not_flagged():
    """삭제 줄(`-`)의 토큰은 추가로 계상하지 않는다."""
    diff = make_file_diff(SRC_FILE, removed=[claim_line(T_A)], added=["# 문장을 좁혔다"])
    result = ACR.evaluate(diff, allow_test_accompaniment=False)
    assert result["claims"] == []


def test_ac5_context_line_with_token_is_not_flagged():
    """문맥 줄(` `)의 토큰도 추가가 아니다."""
    diff = make_file_diff(SRC_FILE, context=[claim_line(T_B)], added=["# 새 주석"])
    result = ACR.evaluate(diff, allow_test_accompaniment=False)
    assert result["claims"] == []


def test_ac5_line_numbers_follow_new_file():
    """행번호는 새 파일 기준으로 문맥 줄만큼 전진한다."""
    diff = make_file_diff(SRC_FILE, context=["a = 1", "b = 2"],
                          added=[claim_line(T_A)], start_new=100)
    added = ACR.parse_added_lines(diff)
    assert [a.lineno for a in added] == [102]


def test_ac5_hunk_body_is_not_mistaken_for_file_header():
    """hunk **본문**의 `---`/`+++` 렌더를 파일 헤더로 오인하지 않는다.

    내용이 `--`/`++` 로 시작하는 줄은 diff 에서 `--- `/`+++ ` 로 렌더된다. 접두만 보고
    가르는 파서는 이 지점에서 경로를 잃거나 추가 줄을 통째로 놓친다."""
    diff = make_file_diff(SRC_FILE,
                          removed=["-- 옛 구분선"],
                          added=["++ 새 구분선 %s 유지된다" % T_A])
    result = ACR.evaluate(diff, allow_test_accompaniment=False)
    assert len(result["claims"]) == 1
    c = result["claims"][0]
    assert c.path == SRC_FILE, "본문 줄이 `+++ ` 헤더로 오인되면 경로가 오염된다"
    assert c.text.startswith("++ ")


def test_changed_paths_collects_both_sides():
    diff = (make_file_diff(SRC_FILE, added=["x = 1"])
            + make_file_diff(TEST_FILE, added=["y = 2"]))
    assert ACR.changed_paths(diff) == {SRC_FILE, TEST_FILE}


# ═══════════════════════════ mutant 하네스 ═══════════════════════════════════════
def load_mutant(replacements):
    """원본 소스를 텍스트 변형해 메모리 안에서만 적재한다.

    anchor 가 정확히 1회 등장하지 않으면 실패시킨다 — 변형이 조용히 미적용된 채
    "mutant 가 통과했다"고 계상되는 가짜 RED 를 막는다."""
    src = SRC_PATH.read_text(encoding="utf-8")
    for old, new in replacements:
        assert src.count(old) == 1, "mutation anchor 가 %d 회 등장: %r" % (src.count(old), old)
        src = src.replace(old, new)
    mod = types.ModuleType("acr_mutant")
    mod.__file__ = str(SRC_PATH)
    exec(compile(src, str(SRC_PATH), "exec"), mod.__dict__)
    return mod


def test_mutant_a_token_matching_disabled_is_red():
    """(a) 토큰 매칭 무력화 → AC1a 가 요구하는 위반이 사라진다."""
    mutant = load_mutant([("    return [t for t in tokens if t in text]", "    return []")])
    diff = make_file_diff(SRC_FILE, added=[claim_line(T_A)])
    assert len(ACR.evaluate(diff)["violations"]) == 1          # 원본: 잡는다
    assert mutant.evaluate(diff)["violations"] == []           # mutant: 놓친다 → AC1a RED


def test_mutant_b_empty_ceiling_accepted_is_red():
    """(b) `[ceiling:]` 사유 공백을 유효 천장으로 완화 → 빈 마커 우회가 뚫린다.

    empty-ceiling 분기를 죽이고 "마커가 있으면 천장"으로 느슨하게 만든 2-변형이다."""
    mutant = load_mutant([
        ("    if reason is not None and not reason:", "    if False:"),
        ("    if reason:", "    if reason is not None:"),
    ])
    diff = make_file_diff(SRC_FILE, added=[claim_line(T_A, "  # [ceiling:]")])
    assert len(ACR.evaluate(diff)["violations"]) == 1          # 원본: 빈 마커를 위반으로
    assert mutant.evaluate(diff)["violations"] == []           # mutant: 통과 → 해당 검사 RED


def test_mutant_c_deleted_lines_counted_as_added_is_red():
    """(c) 삭제 줄을 추가로 계상 → AC5 대조군이 없는 위반을 만든다."""
    mutant = load_mutant([
        ('            elif raw.startswith("-"):\n                old_rem -= 1',
         '            elif raw.startswith("-"):\n'
         '                out.append(AddedLine(path, new_lineno, raw[1:]))\n'
         '                old_rem -= 1'),
    ])
    diff = make_file_diff(SRC_FILE, removed=[claim_line(T_A)], added=["# 문장을 좁혔다"])
    assert ACR.evaluate(diff, allow_test_accompaniment=False)["claims"] == []
    assert len(mutant.evaluate(diff, allow_test_accompaniment=False)["claims"]) == 1


def test_mutant_d_symbol_existence_check_disabled_is_red():
    """(d) 심볼 실재 검증 무력화(문자열만 보고 통과) → 허구 심볼 우회가 뚫린다."""
    mutant = load_mutant([("        if bound and bound in symbols:", "        if bound:")])
    diff = make_file_diff(SRC_FILE, added=[claim_line(T_A, "  # [bound: %s]" % GHOST)])
    assert len(ACR.evaluate(diff, symbol_index=KNOWN)["violations"]) == 1     # 원본: 미해소 위반
    assert mutant.evaluate(diff, symbol_index=KNOWN)["violations"] == []      # mutant: 통과 → RED


def test_mutant_e_accompaniment_washes_unresolved_bound_is_red():
    """(e) 우선순위 역전 — 동반이 미해소를 씻게 하면 허구 심볼이 조용히 통과한다."""
    old = '        return "unresolved-bound", "%s (%s)" % (_R_UNRESOLVED, bound or "심볼 미기재")'
    new = ('        return ("test-accompanied", "동반") if (allow_test_accompaniment and tests_touched) '
           'else ("unresolved-bound", "%s (%s)" % (_R_UNRESOLVED, bound or "심볼 미기재"))')
    mutant = load_mutant([(old, new)])
    diff = (make_file_diff(SRC_FILE, added=[claim_line(T_A, "  # [bound: %s]" % GHOST)])
            + make_file_diff(TEST_FILE, added=["def test_x():", "    assert True"]))
    assert len(ACR.evaluate(diff, symbol_index=KNOWN)["violations"]) == 1
    assert mutant.evaluate(diff, symbol_index=KNOWN)["violations"] == []


# ═══════════════════════════ live: 브랜치 diff 실측 ══════════════════════════════
def _live_symbols():
    syms = ACR.collect_bound_symbols(str(REPO_ROOT))
    assert syms is not None, "tests/ 루트 미해소 — 판정불가"
    return syms


def test_live_symbol_index_resolves_real_symbols():
    """실 repo 수집이 비어 있지 않은지 — 빈 집합이면 모든 `[bound:]` 가 거짓 미해소가 된다."""
    syms = _live_symbols()
    assert "test_vocabulary_is_pinned" in syms
    assert len(syms) > 100



def _live_diff():
    diff = ACR.diff_text_from_git(str(REPO_ROOT))
    if diff is None:
        pytest.skip("origin/main 미해소 — 이 실행에서는 live 축을 **미판정**으로 둔다 "
                    "(CI 는 fetch-depth: 0 + base 해소 확인 step 으로 이 경로를 막는다)")
    return diff


def test_live_branch_diff_has_no_unbound_claim():
    """실 브랜치 diff 에 결박 없는 신규 절대주장이 없어야 한다 (게이트 본체)."""
    result = ACR.evaluate(_live_diff(), symbol_index=_live_symbols())
    detail = "\n".join(ACR.format_report(result, show_passed=False))
    assert result["violations"] == [], "결박 없는 신규 절대주장:\n" + detail


def test_live_gate_own_files_pass_strict_self_application():
    """자기 적용 — 게이트 자신의 파일은 **동반 완화 없이도**(strict) 통과해야 한다.

    동반 완화가 켜져 있으면 tests/** 를 건드리는 것만으로 자기 줄이 씻겨나가므로,
    자기 적용은 그 완화를 끈 상태로 재야 의미가 있다."""
    diff = _live_diff()
    present = ACR.changed_paths(diff) & set(GATE_OWN_PATHS)
    if not present:
        pytest.skip("게이트 자기 파일이 아직 diff 정의역 밖 (미커밋 또는 merge 후 실행)")
    result = ACR.evaluate(diff, allow_test_accompaniment=False, only_prefixes=GATE_OWN_PATHS,
                          symbol_index=_live_symbols())
    detail = "\n".join(ACR.format_report(result, show_passed=False))
    assert result["violations"] == [], "게이트 자기 파일의 미결박 절대주장:\n" + detail


def test_live_report_enumerates_accompaniment_discharges():
    """동반 강제로 통과한 줄도 리포트에 남는지 — 무증상 GREEN 을 만들지 않기 위한 검사."""
    result = ACR.evaluate(_live_diff(), symbol_index=_live_symbols())
    lines = ACR.format_report(result)
    n = sum(1 for c in result["claims"] if c.disposition == "test-accompanied")
    if n:
        assert any("동반 강제" in ln for ln in lines)
        assert sum(1 for ln in lines if ln.startswith("ok ")) >= n
