# -*- coding: utf-8 -*-
"""tests/scripts/test_dated_block_mapper.py

CFP-2698 / Epic #2696 (canary artifact D6, Story A TOOL ROBUSTENING) — DBM-3
`scripts/lib/dated_block_mapper.py` 의 pure-unit TDD self-test.

대상(read-only reference — 본 self-test 는 production 코드를 수정하지 않는다):
  scripts/lib/dated_block_mapper.py — `dated_line_numbers(text)` + `make_dated_provider(repo_root)`

커버리지:
  ① `## YYYY-MM-DD` 헤더 region 경계 — region 은 동일-이하 레벨 헤더(또는 EOF)에서 종료되고,
     더 깊은(하위) 레벨 헤더는 region 을 끊지 않는다.
  ② frontmatter `amendments[].date` → `## Amendment N` region 판정 — date 필드가 있어야만
     Amendment 헤더 region 이 dated 로 잡힌다(date 필드 없으면 미판정).
  ③ dated 신호가 전혀 없는 문서 → 빈 집합.
  ④ TG-4 mutation-kill — amendment-region 판정 축(`_has_dated_amendments_frontmatter`)이
     load-bearing 함을 ablation 으로 실증.

anti-overfit(비협상): 본 self-test 는 파일 신원(경로/특정 라인 번호)을 하드코딩하지 않는다 —
  전부 hermetic 텍스트 fixture 위에서 `_line_of()` 로 라인 번호를 동적으로 찾아 assert 한다.

정직 천장(ADR-119): region 경계 규칙 + amendment-frontmatter 축 load-bearing 까지 실증한다.
  "모든 decision-record 문서의 dated 신호를 완전 검출한다"는 hard-claim 은 하지 않는다.

import-robust: 파일 위치 기준 상대경로로 scripts/lib 를 sys.path 에 얹어 pytest·직접 python 양쪽 구동.
"""

import os
import sys

# ── import-robust: 테스트 파일 기준 상대경로로 scripts/lib 를 sys.path 에 삽입 ──
_LIB = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "lib")
sys.path.insert(0, _LIB)

import dated_block_mapper as dbm  # noqa: E402


def _line_of(text, needle):
    """text 안에서 needle 을 포함하는 첫 라인의 1-indexed 라인 번호 반환(없으면 AssertionError)."""
    for i, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return i
    raise AssertionError("needle not found in text: %r" % needle)


# ─────────────────────────────────────────────────────────────────────────────
# 대표 fixture (장르 exercise — 파일 신원 하드코딩 0)
# ─────────────────────────────────────────────────────────────────────────────
# (a) `## YYYY-MM-DD` region + (b) frontmatter amendments[].date → `## Amendment N` region.
TEXT_MIXED = (
    "---\n"
    "title: sample\n"
    "amendments:\n"
    "  - number: 3\n"
    "    date: 2026-05-01\n"
    "    summary: something\n"
    "---\n"
    "\n"
    "## 결정 1\n"
    "\n"
    "일반 내용 라인 A\n"
    "일반 내용 라인 B\n"
    "\n"
    "## 2026-06-20 과거 기록\n"
    "dated 라인 C\n"
    "dated 라인 D\n"
    "\n"
    "## Amendment 3\n"
    "amendment 라인 E\n"
    "amendment 라인 F\n"
    "\n"
    "## 결정 2\n"
    "일반 내용 라인 G\n"
)

# region 경계 전용 — 하위(깊은) 헤더는 안 끊고, 동일-레벨 헤더에서 끊김.
TEXT_BOUNDARY = (
    "## 2026-06-20 dated 최상위\n"
    "\n"
    "dated 라인 1\n"
    "\n"
    "### 하위 섹션 (레벨3, 종료 아님)\n"
    "\n"
    "dated 라인 2 (여전히 dated, 하위섹션 포함)\n"
    "\n"
    "## 다음 동일레벨 헤더 (종료)\n"
    "\n"
    "undated 라인 3\n"
)

# dated 신호 전무 — 빈 집합 기대.
TEXT_NO_DATED = (
    "---\n"
    "title: sample\n"
    "---\n"
    "\n"
    "## 결정 1\n"
    "일반 내용\n"
)

# amendments 리스트는 있으나 date 필드가 전혀 없음 → Amendment region 미판정.
TEXT_AMEND_NO_DATE = (
    "---\n"
    "title: sample\n"
    "amendments:\n"
    "  - number: 1\n"
    "    summary: no date field here\n"
    "---\n"
    "\n"
    "## Amendment 1\n"
    "amendment 라인 무날짜\n"
)


# ═════════════════════════════════════════════════════════════════════════════
# ① 혼합 fixture — 날짜-헤더 region ∧ frontmatter-driven amendment region 둘 다 잡힘
# ═════════════════════════════════════════════════════════════════════════════
def test_date_header_region_captured():
    """`## YYYY-MM-DD` 헤더 region(헤더 라인 포함, 본문 라인 포함)이 dated_line_numbers 에 잡힌다."""
    dated = dbm.dated_line_numbers(TEXT_MIXED)
    header_line = _line_of(TEXT_MIXED, "## 2026-06-20")
    body_c = _line_of(TEXT_MIXED, "dated 라인 C")
    body_d = _line_of(TEXT_MIXED, "dated 라인 D")
    assert header_line in dated
    assert body_c in dated
    assert body_d in dated


def test_amendment_region_captured_when_frontmatter_dated():
    """frontmatter amendments[].date 존재 시 `## Amendment N` region(헤더+본문)이 dated 로 잡힌다."""
    dated = dbm.dated_line_numbers(TEXT_MIXED)
    amend_header = _line_of(TEXT_MIXED, "## Amendment 3")
    amend_e = _line_of(TEXT_MIXED, "amendment 라인 E")
    amend_f = _line_of(TEXT_MIXED, "amendment 라인 F")
    assert amend_header in dated
    assert amend_e in dated
    assert amend_f in dated


def test_undated_regions_excluded():
    """일반(날짜 없는) `## 결정 N` region 라인은 dated 집합 밖(선행/후행 둘 다)."""
    dated = dbm.dated_line_numbers(TEXT_MIXED)
    undated_a = _line_of(TEXT_MIXED, "일반 내용 라인 A")
    undated_g = _line_of(TEXT_MIXED, "일반 내용 라인 G")
    assert undated_a not in dated
    assert undated_g not in dated


# ═════════════════════════════════════════════════════════════════════════════
# ② region 경계 — 동일-이하 레벨 헤더에서 종료, 하위(깊은) 헤더는 안 끊음
# ═════════════════════════════════════════════════════════════════════════════
def test_region_boundary_deeper_header_does_not_close():
    """dated region 안의 하위(더 깊은) 레벨 헤더(`###`)는 region 을 끊지 않는다 — 그 아래 본문도 dated."""
    dated = dbm.dated_line_numbers(TEXT_BOUNDARY)
    top_header = _line_of(TEXT_BOUNDARY, "## 2026-06-20 dated 최상위")
    dated_1 = _line_of(TEXT_BOUNDARY, "dated 라인 1")
    sub_header = _line_of(TEXT_BOUNDARY, "### 하위 섹션")
    dated_2 = _line_of(TEXT_BOUNDARY, "dated 라인 2")
    assert top_header in dated
    assert dated_1 in dated
    assert sub_header in dated
    assert dated_2 in dated


def test_region_boundary_same_level_header_closes():
    """동일 레벨(`##`) 헤더를 만나면 이전 region 이 종료되고, 그 헤더 자체·이후 라인은 dated 밖."""
    dated = dbm.dated_line_numbers(TEXT_BOUNDARY)
    next_header = _line_of(TEXT_BOUNDARY, "## 다음 동일레벨 헤더")
    undated_3 = _line_of(TEXT_BOUNDARY, "undated 라인 3")
    assert next_header not in dated
    assert undated_3 not in dated


# ═════════════════════════════════════════════════════════════════════════════
# ③ negative control — dated 신호 전무 / amendments 있으나 date 필드 없음
# ═════════════════════════════════════════════════════════════════════════════
def test_no_dated_signal_yields_empty_set():
    """날짜-헤더도 없고 frontmatter amendments 도 없는 문서 → dated_line_numbers 는 빈 집합."""
    assert dbm.dated_line_numbers(TEXT_NO_DATED) == set()


def test_amendments_without_date_field_not_dated():
    """frontmatter `amendments:` 리스트는 있으나 원소 중 `date:` 필드가 전혀 없으면 `## Amendment N`
    region 은 dated 로 판정되지 않는다(빈 집합) — date 필드가 판정을 gate 함을 확인."""
    dated = dbm.dated_line_numbers(TEXT_AMEND_NO_DATE)
    assert dated == set()
    # 명시적으로 Amendment 헤더 라인 자체도 빠짐을 확인.
    amend_header = _line_of(TEXT_AMEND_NO_DATE, "## Amendment 1")
    assert amend_header not in dated


# ═════════════════════════════════════════════════════════════════════════════
# ④ TG-4 mutation-kill — amendment-region 판정 축 load-bearing 실증
# ═════════════════════════════════════════════════════════════════════════════
def test_tg4_amendment_region_detection_load_bearing():
    """TG-4 — frontmatter amendments[].date → `## Amendment N` region 판정 축이 load-bearing 함을
    mutation-kill 로 실증. Mutation proof: dbm._has_dated_amendments_frontmatter 를 상시 False 로
    ablate 하면 Amendment region 라인들이 dated 집합에서 빠짐(RED flip) — date-header 축(독립)은
    영향받지 않음을 함께 확인해 두 축의 분리(disjoint)도 실증한다."""
    before = dbm.dated_line_numbers(TEXT_MIXED)
    amend_header = _line_of(TEXT_MIXED, "## Amendment 3")
    amend_e = _line_of(TEXT_MIXED, "amendment 라인 E")
    date_header = _line_of(TEXT_MIXED, "## 2026-06-20")
    assert amend_header in before
    assert amend_e in before

    orig = dbm._has_dated_amendments_frontmatter
    try:
        dbm._has_dated_amendments_frontmatter = lambda *a, **k: False  # ablate: 상시 미판정
        after = dbm.dated_line_numbers(TEXT_MIXED)
    finally:
        dbm._has_dated_amendments_frontmatter = orig

    assert amend_header not in after, (
        "ablation 후 Amendment region 헤더 라인이 dated 집합에서 빠져야(RED): %s" % after
    )
    assert amend_e not in after, (
        "ablation 후 Amendment region 본문 라인이 dated 집합에서 빠져야(RED): %s" % after
    )
    # date-header 축(독립)은 amendment 판정 ablation 과 무관하게 여전히 dated.
    assert date_header in after

    # 원복 확인.
    restored = dbm.dated_line_numbers(TEXT_MIXED)
    assert amend_header in restored
    assert restored == before


# ═════════════════════════════════════════════════════════════════════════════
# make_dated_provider — 파일 경로 기반 provider 계약(True / None, never False)
# ═════════════════════════════════════════════════════════════════════════════
def test_make_dated_provider_true_and_none_contract():
    """make_dated_provider 의 provider(path, lineno) 는 dated region 안이면 True, 그 외(밖/미판정/
    읽기 실패)면 None 을 반환한다(never False — additive 근거 계약)."""
    import shutil
    import tempfile

    root = tempfile.mkdtemp(prefix="cfp2698_dbm_")
    try:
        target = os.path.join(root, "sample.md")
        with open(target, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(TEXT_MIXED)
        provider = dbm.make_dated_provider(root)

        date_header = _line_of(TEXT_MIXED, "## 2026-06-20")
        undated_a = _line_of(TEXT_MIXED, "일반 내용 라인 A")

        assert provider("sample.md", date_header) is True
        result_undated = provider("sample.md", undated_a)
        assert result_undated is None  # dated 밖 = None(False 아님 — additive 계약)

        # 파일 부재 → 읽기 실패 → None.
        assert provider("nonexistent.md", 1) is None
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ─────────────────────────────────────────────────────────────────────────────
# 직접 python 실행 경로(pytest 부재 시) — 전 test_ 함수 구동 + 요약.
# ─────────────────────────────────────────────────────────────────────────────
def _run_all_direct():
    tests = sorted(
        (name, obj)
        for name, obj in globals().items()
        if name.startswith("test_") and callable(obj)
    )
    passed, failed = 0, 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print("  PASS %s" % name)
        except Exception as exc:  # noqa: BLE001 (self-test 러너 — 모든 실패 표면화)
            failed += 1
            print("  FAIL %s :: %r" % (name, exc))
    print("")
    print("CFP-2698 dated_block_mapper self-test — %d passed / %d failed / %d total"
          % (passed, failed, passed + failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(_run_all_direct())
