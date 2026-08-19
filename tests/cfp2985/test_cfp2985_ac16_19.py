"""CFP-2985 RTM 8.1.1 — AC-16 (4) · AC-17 (4) · AC-18 (1) · AC-19 (3) 명명 테스트.

AC-16 = 8.1 **L4 집계 축**. leg1/leg2/leg3 + I4. leg3 이 1 요구의 유일한 실질 충족 leg 이며
        leg1·leg2 만 GREEN 이면 "집계된다" 는 거짓이다 (`pattern_count` 는 분포가 아니라
        최대 group 크기 scalar) — 부분 통과를 인정하지 않는다.
AC-17 = 연기 항목 표 선택 · carrier/만기 pairing · 대상 0 vacuous 금지 · 파서 정의역 mutant 4·5·6.
AC-18 = `declared` — 소비 술어 목록 전집합 여부의 천장 문면 presence.
AC-19 = (a-4) 표 위생 3 leg (상태 정규화 · 채택값/실물근거 · 결속 타입 정합).
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _cfp2985_spec as S  # noqa: E402

DEFERRAL_HEADERS = ("phase", "carrier", "만기")


def _trend_rows(with_substrate=True, causes=("설계", "구현", "설계")):
    rows = []
    for i, c in enumerate(causes):
        r = {"timestamp_utc": "2026-08-1%dT00:00:00Z" % (i % 9),
             "event_type": "fix", "story_key": "CFP-298%d" % i}
        if with_substrate:
            r["anchor_id"] = "§5.3"
            r["root_cause_class"] = c
        rows.append(r)
    return rows


def _trend(rows):
    import aggregate_dev_process_event as agg
    return agg.compute_trend(rows, {})


# ---------------------------------------------------------------------------
# AC-16 — L4 집계 축
# ---------------------------------------------------------------------------
def test_ac16_leg1_pattern_status_not_uncomputable():
    """AC-16 leg1 — 원인 substrate 가 있으면 `pattern_status != 'uncomputable_missing_key'`.

    RTM: 8.1 L4 (AC-16 leg1) / 5.3 verification 3-leg 대조 중 첫 leg.
    핵심 mutant (5.4 AC-16 mutant2) = **원인 키를 원장에서 제거한 상태로 집계 실행** ->
    `uncomputable_missing_key` 재현 = VD-6 silent drop 의 직접 재현.
    """
    pred = lambda rows: _trend(rows).get("pattern_status") != "uncomputable_missing_key"  # noqa: E731
    control = _trend_rows(True)
    mutants = [
        ("원인 키 제거 (root_cause_class)",
         [{k: v for k, v in r.items() if k != "root_cause_class"} for r in control]),
        ("anchor 키 제거 (AND 게이트 falsify)",
         [{k: v for k, v in r.items() if k != "anchor_id"} for r in control]),
        ("원인 키를 None 으로",
         [dict(r, root_cause_class=None) for r in control]),
        ("행 자체가 0", []),
    ]
    green = [
        ("원인값 종류 1종만", _trend_rows(True, causes=("설계",))),
        ("원인값 6값 전부", _trend_rows(True, causes=("설계", "구현", "요구사항",
                                                     "환경", "설계-리뷰", "구현-리뷰"))),
    ]
    S.assert_discriminating(pred, control, mutants, green, label="AC-16/leg1-pattern-status")


def test_ac16_leg2_pattern_count_non_null():
    """AC-16 leg2 — `pattern_count` 가 non-null 이다.

    RTM: 8.1 L4 (AC-16 leg2).
    ★ leg2 단독으로는 1 요구를 충족하지 않는다 — `pattern_count` 는 원인별 분포가 아니라
      **최대 group 크기 scalar** 다. 실질 충족 leg 은 leg3 다 (5.3 AC-16 명시).
    """
    pred = lambda rows: _trend(rows).get("pattern_count") is not None  # noqa: E731
    control = _trend_rows(True)
    mutants = [
        ("원인 키 제거", [{k: v for k, v in r.items() if k != "root_cause_class"} for r in control]),
        ("anchor 키 제거", [{k: v for k, v in r.items() if k != "anchor_id"} for r in control]),
        ("두 키 모두 None", [dict(r, anchor_id=None, root_cause_class=None) for r in control]),
    ]
    green = [
        ("단일 story_key", [dict(r, story_key="CFP-2985") for r in control]),
        ("행 확장", control + _trend_rows(True, causes=("환경",))),
    ]
    S.assert_discriminating(pred, control, mutants, green, label="AC-16/leg2-pattern-count")


def test_ac16_leg3_root_cause_distribution_non_empty():
    """AC-16 leg3 — top-level 에 원인값 -> 건수 map 이 실재하고 non-empty 다.

    RTM: 8.1 L4 (AC-16 leg3). 대상 필드명 = `root_cause_distribution` (4.4 신설).
    ★ **`has_rcc` 단독 gate** — AND 게이트 밖이다 (3.3). anchor 가 없어도 분포는 나와야 한다.
      leg1·leg2 는 GREEN 인데 leg3 만 실패하면 **FAIL** 이며 부분 통과를 인정하지 않는다.
    """
    def pred(rows):
        d = _trend(rows).get("root_cause_distribution")
        return isinstance(d, dict) and len(d) > 0

    control = _trend_rows(True)
    mutants = [
        ("원인 키 제거",
         [{k: v for k, v in r.items() if k != "root_cause_class"} for r in control]),
        ("원인 키 전건 None", [dict(r, root_cause_class=None) for r in control]),
        ("행 자체가 0", []),
    ]
    green = [
        ("anchor 부재 (AND 게이트 밖 실증)",
         [{k: v for k, v in r.items() if k != "anchor_id"} for r in control]),
        ("원인값 1종만", _trend_rows(True, causes=("구현",))),
        ("원인값 6값 전부", _trend_rows(True, causes=("설계", "구현", "요구사항",
                                                     "환경", "설계-리뷰", "구현-리뷰"))),
    ]
    S.assert_discriminating(pred, control, mutants, green, label="AC-16/leg3-distribution")

    # 분포는 **건수 map** 이어야 한다 — 값이 세어지지 않으면 map 만 있고 집계는 없다.
    dist = _trend(_trend_rows(True, causes=("설계", "설계", "구현")))["root_cause_distribution"]
    assert dist.get("설계") == 2 and dist.get("구현") == 1, (
        "분포가 건수를 세지 않는다: %r" % dist)

    # 정규화 후 집계 — 장식·대소문자 변형이 분포를 쪼개면 안 된다 (5.4 AC-16 mutant3).
    decorated = _trend_rows(True, causes=("설계", "**설계**", " 설계 "))
    dd = _trend(decorated)["root_cause_distribution"]
    assert len(dd) == 1 and sum(dd.values()) == 3, (
        "장식·공백 변형이 분포를 쪼갠다 (정규화 후 집계여야 한다): %r" % dd)


def test_ac16_i4_honesty_invariant_direction():
    """AC-16 I4 — 정직 invariant 의 **방향이 반전**돼 있다 (negative-domain 대조군 보존).

    RTM: 8.1 L4 (I4 assert) — Change Plan 5 D-14.
    반전 전 I4 는 "uncomputable 이 DEFAULT 여야 정직" 이었다. substrate 가 실재하는 지금
    그 방향을 유지하면 **집계가 되는 것이 위반**이 된다. 반전 후:
      (a) substrate 有 ∧ computable  -> 위반 아님
      (b) substrate 有 ∧ uncomputable -> **위반** (silent drop)
      (c) substrate 無 ∧ uncomputable -> 위반 아님 (negative-domain 대조군 보존 — 정직-null)
    """
    import check_dev_process_aggregate_honesty as hon

    fn = getattr(hon, "check_pattern_uncomputable_default", None)
    assert callable(fn), (
        "honesty 체커에서 I4 검사 함수를 찾지 못했다 — Change Plan 5 D-14 대상 함수 부재")

    def i4_violations(trend_snap):
        out = []
        fn({"trend": trend_snap}, out)
        return [v for v in out if "I4" in v or "pattern" in v]

    computable = {"pattern_status": "computable", "pattern_count": 2,
                  "root_cause_distribution": {"설계": 2}}
    uncomputable_with_substrate = {"pattern_status": "uncomputable_missing_key",
                                   "pattern_count": None,
                                   "root_cause_distribution": {"설계": 2}}
    uncomputable_no_substrate = {"pattern_status": "uncomputable_missing_key",
                                 "pattern_count": None, "root_cause_distribution": {}}

    assert not i4_violations(computable), (
        "(a) substrate 有 ∧ computable 인데 I4 가 위반을 냈다 — 반전 미착지 (D-14). "
        "이 방향이면 '집계가 되는 것' 자체가 위반이 된다.")
    assert i4_violations(uncomputable_with_substrate), (
        "(b) substrate 有 ∧ uncomputable 인데 I4 가 침묵했다 — silent drop 미검출")
    assert not i4_violations(uncomputable_no_substrate), (
        "(c) substrate 無 ∧ uncomputable 은 정직-null 이다 — negative-domain 대조군이 파괴됐다")


# ---------------------------------------------------------------------------
# AC-17 — 연기 항목 표
# ---------------------------------------------------------------------------
def select_deferral_tables(text):
    """대상 표 = 헤더가 `Phase` ∧ `carrier` ∧ `만기` **세 열을 동시 보유** (P-R).

    컬럼명 하나(`Phase`)로 고르면 뜻이 다른 동음이의 컬럼을 가진 표가 혼입된다
    (5.3 의 `phase` = AC 검증 단계 / 5 의 `Phase` = 변경 착지 단계 — E-10 실측).
    """
    return S.select_tables(S.md_tables(text), DEFERRAL_HEADERS)


def phase2_rows(tables):
    """선택된 표에서 `Phase` 열 값이 `^2` 인 행 (접두 매칭, fail-closed)."""
    out = []
    for header, rows in tables:
        i_ph = S.col_index(header, "phase")
        if i_ph < 0:
            continue
        for cells in rows:
            if len(cells) > i_ph and S.norm_cell(cells[i_ph]).startswith("2"):
                out.append((header, cells))
    return out


def carrier_duedate_paired(header, cells):
    i_c, i_d = S.col_index(header, "carrier"), S.col_index(header, "만기")
    if i_c < 0 or i_d < 0 or len(cells) <= max(i_c, i_d):
        return False
    return bool(S.CARRIER_RE.search(cells[i_c])) and bool(S.DUEDATE_RE.search(cells[i_d]))


_DEF_CTL = (
    "| # | 파일 | 변경 | Phase | carrier | 만기 |\n"
    "|---|---|---|---|---|---|\n"
    "| D-1 | a.md | x | 1 | — | — |\n"
    "| D-7 | b.py | y | 2 | `#2985` | 2026-09-15 |\n"
    "| D-8 | c.py | z | 2 (선언은 1) | `#2985` | 2026-09-15 |\n"
)
_AC_TABLE = (
    "| AC | statement | source | verification | owner | phase | tier |\n"
    "|---|---|---|---|---|---|---|\n"
    "| AC-1 | s | user | v | design | 2 | normative |\n"
)


def test_ac17_deferral_table_selection_predicate():
    """AC-17 leg1 — 대상 **표** 선택이 3열 동시 보유로 판정된다.

    RTM: 5.3 verification "표 선택(헤더 `Phase` ∧ `carrier` ∧ `만기` 동시 보유)".
    """
    pred = lambda t: len(select_deferral_tables(t)) == 1  # noqa: E731
    control = _DEF_CTL
    mutants = [
        ("carrier 열 제거",
         control.replace(" | carrier | 만기 |", " | 만기 |").replace(
             "|---|---|---|---|---|---|", "|---|---|---|---|---|").replace(
             " | `#2985` | 2026-09-15 |", " | 2026-09-15 |")),
        ("만기 열 제거",
         control.replace(" | carrier | 만기 |", " | carrier |").replace(
             "|---|---|---|---|---|---|", "|---|---|---|---|---|").replace(
             " | `#2985` | 2026-09-15 |", " | `#2985` |")),
        ("동음이의 AC 표만 존재 (Phase 열만 보유)", _AC_TABLE),
        ("표 자체가 없음", "산문만 있다\n"),
    ]
    green = [
        ("동음이의 AC 표가 같은 문서에 공존 (자동 배제)", control + "\n" + _AC_TABLE),
        ("열 순서 변경",
         control.replace("| # | 파일 | 변경 | Phase | carrier | 만기 |",
                         "| # | Phase | carrier | 만기 | 파일 | 변경 |")),
        ("헤더 장식", control.replace("| Phase |", "| **Phase** |")),
    ]
    for nm, txt in mutants[:2]:
        assert txt != control, "mutant '%s' 주입 실패" % nm
    S.assert_discriminating(pred, control, mutants, green, label="AC-17/table-selection")

    plan = S.internal_docs_text(S.PLAN_REL)
    if plan is None:
        return
    tables = select_deferral_tables(plan)
    assert tables, "Change Plan 에서 연기 항목 표(3열 동시 보유)를 찾지 못했다"


def test_ac17_phase2_row_carrier_and_due_date_pairing():
    """AC-17 leg2 — `Phase` 열이 `^2` 인 행은 carrier 와 만기를 **동시** 보유한다.

    RTM: 5.3 verification "`Phase` 열 `^2` 행에 `#\\d+` ∧ `\\d{4}-\\d{2}-\\d{2}` 동시 존재".
    """
    def pred(text):
        rows = phase2_rows(select_deferral_tables(text))
        return bool(rows) and all(carrier_duedate_paired(h, c) for h, c in rows)

    control = _DEF_CTL
    mutants = [
        ("carrier 칸 공란", control.replace("| 2 | `#2985` | 2026-09-15 |", "| 2 |  | 2026-09-15 |")),
        ("만기 칸 공란", control.replace("| 2 | `#2985` | 2026-09-15 |", "| 2 | `#2985` |  |")),
        ("carrier 가 번호 없는 산문",
         control.replace("| 2 | `#2985` | 2026-09-15 |", "| 2 | 나중에 | 2026-09-15 |")),
        ("만기가 날짜 형식 아님",
         control.replace("| 2 | `#2985` | 2026-09-15 |", "| 2 | `#2985` | TBD |")),
        ("Phase 2 행 0 (vacuous)",
         "| # | 파일 | 변경 | Phase | carrier | 만기 |\n|---|---|---|---|---|---|\n"
         "| D-1 | a.md | x | 1 | — | — |\n"),
    ]
    green = [
        ("접두 매칭 (2 (선언은 1))", control),
        ("carrier 표기 변형 (백틱 없음)", control.replace("`#2985`", "#2985")),
        ("Phase 1 행은 정의역 밖", control + "| D-9 | d.md | w | 1 | — | — |\n"),
    ]
    for nm, txt in mutants:
        assert txt != control, "mutant '%s' 주입 실패" % nm
    S.assert_discriminating(pred, control, mutants, green, label="AC-17/carrier-duedate")

    plan = S.internal_docs_text(S.PLAN_REL)
    if plan is None:
        return
    rows = phase2_rows(select_deferral_tables(plan))
    bad = [c[0] for h, c in rows if not carrier_duedate_paired(h, c)]
    assert not bad, "Phase 2 행 중 carrier·만기 미보유: %s" % bad


def test_ac17_zero_target_row_exits_non_zero():
    """AC-17 leg3 — 대상 행이 0 이면 **그 자체로** 비-zero exit 다 (vacuous 방지).

    RTM: 5.3 verification "대상 행이 0 이면 그 자체로 비-zero exit".
    ★ 이 leg 이 없으면 표를 비우는 것만으로 GREEN 을 살 수 있다 — 이 Story 가
      "좁은 독법 기각(대상 0행 = vacuous GREEN 재도입)" 으로 명시 배격한 경로다.
    """
    def pred(text):
        """대상 행 0 = 위반(False). 0 을 GREEN 으로 두지 않는다."""
        return len(phase2_rows(select_deferral_tables(text))) > 0

    control = _DEF_CTL
    mutants = [
        ("Phase 2 행 전건 제거",
         "| # | 파일 | 변경 | Phase | carrier | 만기 |\n|---|---|---|---|---|---|\n"
         "| D-1 | a.md | x | 1 | — | — |\n"),
        ("표 전체 제거", "산문만 있다\n"),
        ("표는 있으나 데이터 행 0",
         "| # | 파일 | 변경 | Phase | carrier | 만기 |\n|---|---|---|---|---|---|\n"),
        # ★ 두 Phase 2 행을 **둘 다** 1 로 내려야 유효한 mutant 다. 한 행만 바꾸면 나머지가
        #   대상으로 남아 술어가 옳게 True 를 내고, 그것을 "생존" 으로 읽으면 정반대 결론이 된다
        #   (본 하네스가 1회 자기검출 — 접두 매칭 행 `2 (선언은 1)` 이 남아 있었다).
        ("Phase 열 값을 전부 1 로",
         control.replace("| 2 | `#2985` | 2026-09-15 |", "| 1 | — | — |")
                .replace("| 2 (선언은 1) | `#2985` | 2026-09-15 |", "| 1 | — | — |")),
    ]
    green = [
        ("대상 행 1건", control.replace("| D-8 | c.py | z | 2 (선언은 1) | `#2985` | 2026-09-15 |\n", "")),
        ("대상 행 다수", control),
    ]
    for nm, txt in mutants:
        assert txt != control, "mutant '%s' 주입 실패" % nm
    S.assert_discriminating(pred, control, mutants, green, label="AC-17/zero-target-vacuous")

    plan = S.internal_docs_text(S.PLAN_REL)
    if plan is None:
        return
    assert pred(plan), "Change Plan 연기 항목 표의 Phase 2 대상 행이 0 — vacuous GREEN"


def test_ac17_parser_domain_mutants_4_5_6_red():
    """AC-17 leg4 — 파서 정의역 규칙 (i)~(v) 상속: mutant 4·5·6 이 전건 RED 다.

    RTM: 5.3 verification "파서 정의역 규칙 (i)~(v) 상속 -> mutant 4·5·6 적용".
    mutant 정본 (5.4) = 4 비숫자 첫 셀 · 5 표 중간 빈 줄 · 6 중첩 하위표.
    AC-17 의 verification 자체가 마크다운 표를 파싱하므로 `N/A — Phase 1 표 축` 마킹은 철회됐다.
    """
    def target_row_ids(text):
        return {S.norm_cell(c[0]) for _h, c in phase2_rows(select_deferral_tables(text))}

    base = target_row_ids(_DEF_CTL)
    assert base == {"D-7", "D-8"}, "대조군 대상 행 집합이 기대와 다르다: %r" % base

    # mutant 4 — 첫 셀 표기 제약 없음 (비숫자·기호 첫 셀도 데이터 행이다).
    m4 = _DEF_CTL.replace("| D-7 |", "| — |").replace("| D-8 |", "| 2-b |")
    ids4 = target_row_ids(m4)
    assert len(ids4) == 2, (
        "mutant 4 (비숫자 첫 셀) 에서 대상 행이 사라졌다 — 첫 셀 표기 제약이 파서에 남아 있다: %r" % ids4)

    # mutant 5 — 표 중간 빈 줄. 빈 줄은 표를 끊으므로 **뒤쪽 행이 누락되면 RED** 다.
    m5 = _DEF_CTL.replace("| D-7 | b.py | y | 2 | `#2985` | 2026-09-15 |\n",
                          "| D-7 | b.py | y | 2 | `#2985` | 2026-09-15 |\n\n")
    ids5 = target_row_ids(m5)
    assert "D-8" not in ids5, (
        "mutant 5 (표 중간 빈 줄) 가 판별력을 갖지 못했다 — 빈 줄 뒤 행이 그대로 수집됐다. "
        "빈 줄이 컬럼 앵커를 파괴하는 사실이 노출되지 않으면 이 mutant 는 hollow 다")
    assert "D-7" in ids5, "빈 줄 **앞** 행까지 잃으면 파서가 과도하게 끊는다"

    # mutant 6 — 중첩 하위표 삽입. 하위표(3열 미보유)는 선택되지 않고, 그 **뒤** 행은 살아야 한다.
    sub = ("\n| 근거 | 값 |\n|---|---|\n| x | y |\n\n")
    m6 = _DEF_CTL.replace("| D-8 |", sub + "| # | 파일 | 변경 | Phase | carrier | 만기 |\n"
                                            "|---|---|---|---|---|---|\n| D-8 |")
    ids6 = target_row_ids(m6)
    assert "D-8" in ids6 and "D-7" in ids6, (
        "mutant 6 (중첩 하위표) 뒤 행이 누락됐다 — 하위표가 부모 정의역을 삼킨다: %r" % ids6)
    assert len(select_deferral_tables(m6)) == 2, (
        "하위표가 대상 표로 잘못 선택됐다 (3열 미보유인데 선택됨)")


# ---------------------------------------------------------------------------
# AC-18 — declared 천장
# ---------------------------------------------------------------------------
def test_ac18_predicate_enumeration_ceiling_present():
    """AC-18 (declared) — "소비 술어 목록이 전집합인지는 기계 판정 불가" 천장이 실재한다.

    RTM: 5.3 verification "기계 판정 불가(정적 전수 열거 술어 부재 = 정지 문제 근사) ·
    천장 문면 presence 만 검사".
    AC-19 와 disjoint — AC-19 = 목록 **안** 위생 / AC-18 = 목록 **밖** 천장.
    """
    axis = ("술어", "전수 열거", "정지 문제", "소비")
    neutral = "다른 무엇인가는 기계 판정 불가 — 근거가 없다.\n"
    assert not any(tok in neutral for tok in axis), "무관 문장 mutant 가 축 토큰을 담았다"

    reason = "구현이 소비하는 술어의 정적 전수 열거가 정지 문제 근사라 불가하다"
    control = "본 목록은 기계 판정 불가 — %s.\n" % reason
    mutants = [
        ("천장 문면 삭제", "본 목록은 33행이다.\n"),
        ("사유 없이 불가만", "본 목록은 기계 판정 불가.\n"),
        ("축 토큰 없는 일반 불가 문장", neutral),
        ("전집합 주장으로 대체", "본 목록은 술어 전집합임을 기계 판정한다.\n"),
        ("공란", ""),
    ]
    green = [
        ("표기 변형", "본 목록은 판정 불가 : %s\n" % reason),
        ("사유 확장", control + "그래서 이 항목은 declared 다.\n"),
    ]

    from test_cfp2985_ac07_10 import ceiling_statement_present  # 동일 술어 재사용 (단일 정의처)
    S.assert_discriminating(lambda t: ceiling_statement_present(t, axis),
                            control, mutants, green, label="AC-18/ceiling-presence")

    story = S.internal_docs_text(S.STORY_REL)
    if story is None:
        return
    hits = [ln for ln in story.split("\n") if ceiling_statement_present(ln + "\n", axis)]
    assert hits, "Story 에 AC-18 천장 문면(불가 선언 + 사유)이 없다"


# ---------------------------------------------------------------------------
# AC-19 — (a-4) 표 위생
# ---------------------------------------------------------------------------
STATUS_CLOSED_SET = ("선언", "배제")


def status_closed_set_ok(rows):
    """ⓐ `상태` 값이 **정규화 후** closed-set 정확 일치 (P-AD)."""
    if not rows:
        return False
    return all(S.norm_cell(r.get("상태", "")) in STATUS_CLOSED_SET for r in rows)


_VOID_RE = re.compile(r"^\s*(null|none|n/?a|tbd|-{1,2}|—|–|\?+)\s*$", re.I)


def _void(cell):
    """공허 셀 — 빈 문자열뿐 아니라 대시·null 류도 **공허**다.

    ★ 5.3 AC-19 는 "셀이 **공허**하거나" 라고 적었지 "빈 문자열이거나" 라고 적지 않았다.
      빈 문자열만 보면 `—` 한 글자로 채운 행이 통과한다 (본 하네스가 mutant 로 자기검출).
    """
    v = S.norm_cell(str(cell))
    return (not v) or bool(_VOID_RE.match(v))


def adopted_and_evidence_non_empty(rows):
    """ⓑ `채택값` 과 `실물 근거` 가 **각각 별개 컬럼**이며 둘 다 non-empty."""
    if not rows:
        return False
    for r in rows:
        if "채택값" not in r or "실물 근거" not in r:
            return False
        if _void(r.get("채택값", "")) or _void(r.get("실물 근거", "")):
            return False
    return True


def binding_type_matches_status(rows):
    """ⓒ `결속` non-empty ∧ `상태` 와 타입 정합 (P-AG).

    `EM ` 접두 토큰 = 방출 카운터 타입, 아니면 fixture ID 타입.
    `배제` 행은 전 토큰이 `EM ` 접두를 **의무** 부착한다.
    ★ `EM ` 은 셀 표기 marker 이지 방출 키 이름의 일부가 아니다.
    """
    if not rows:
        return False
    for r in rows:
        toks = [t.strip() for t in re.findall(r"`([^`]+)`", r.get("결속", "")) if t.strip()]
        if not toks:
            return False
        st = S.norm_cell(r.get("상태", ""))
        if st == "배제" and not all(t.startswith("EM ") for t in toks):
            return False
        if st == "선언" and any(t.startswith("EM ") for t in toks):
            return False
    return True


_A4 = [{"id": "P-A", "상태": "선언", "채택값": "재귀 glob", "실물 근거": "CFP-1746.md:158",
        "결속": "`FX-A`"},
       {"id": "P-B", "상태": "배제", "채택값": "epic 배제", "실물 근거": "CFP-1059.md:231",
        "결속": "`EM rows_epic_na`"}]


def _mut(rows, rid, field, value):
    return [dict(r, **({field: value} if r["id"] == rid else {})) for r in rows]


def _drop(rows, rid, field):
    return [{k: v for k, v in r.items() if not (r["id"] == rid and k == field)} for r in rows]


def test_ac19_a4_status_closed_set_after_normalization():
    """AC-19 ⓐ — `상태` 가 정규화(P-AD) 후 closed-set 정확 일치 (`미선언`·`오선언` 잔존 0).

    RTM: 5.3 verification ⓐ.
    ★ 이 AC 는 도입 시점 자기 산출물에서 RED 였다 — 정규화 술어를 **선언 없이 소비**해
      27행 중 17행이 `★ **선언 (Iter 3 신설)` 형으로 closed-set 밖이었다. 정규화가 곧 계약이다.
    """
    mutants = [
        ("미선언 잔존", _mut(_A4, "P-A", "상태", "미선언")),
        ("오선언 잔존", _mut(_A4, "P-A", "상태", "오선언")),
        ("closed-set 밖 값", _mut(_A4, "P-B", "상태", "보류")),
        ("상태 공란", _mut(_A4, "P-A", "상태", "")),
        ("행 0 (vacuous)", []),
    ]
    green = [
        ("선두 별표 + 볼드 장식", _mut(_A4, "P-A", "상태", "★ **선언**")),
        ("괄호 주석 후행", _mut(_A4, "P-A", "상태", "선언 (Iter 3 신설)")),
        ("장식 + 괄호 동시", _mut(_A4, "P-B", "상태", "★ **배제** (Iter 5)")),
        ("공백 패딩", _mut(_A4, "P-A", "상태", "  선언  ")),
    ]
    S.assert_discriminating(status_closed_set_ok, _A4, mutants, green,
                            label="AC-19/status-closed-set")

    story = S.internal_docs_text(S.STORY_REL)
    if story is None:
        return
    rows = _a4_rows_full(story)
    assert rows, "Story 3.0(a-4) 표를 찾지 못했다"
    bad = [(r["id"], r["상태"]) for r in rows
           if S.norm_cell(r["상태"]) not in STATUS_CLOSED_SET]
    assert not bad, "(a-4) `상태` closed-set 밖 행: %s" % bad


def test_ac19_a4_adopted_value_and_evidence_non_empty():
    """AC-19 ⓑ — `채택값` 과 `실물 근거` 가 각각 별개 컬럼이며 둘 다 non-empty 다.

    RTM: 5.3 verification ⓑ.
    """
    mutants = [
        ("채택값 공란", _mut(_A4, "P-A", "채택값", "")),
        ("실물 근거 공란", _mut(_A4, "P-B", "실물 근거", "")),
        ("채택값 컬럼 자체 부재 (병합 컬럼)", _drop(_A4, "P-A", "채택값")),
        ("실물 근거 컬럼 자체 부재", _drop(_A4, "P-B", "실물 근거")),
        ("두 값이 대시", _mut(_mut(_A4, "P-A", "채택값", "—"), "P-A", "실물 근거", "—")),
        ("행 0 (vacuous)", []),
    ]
    green = [
        ("근거가 파일:줄 좌표", _mut(_A4, "P-A", "실물 근거", "CFP-622.md:136")),
        ("근거가 재현 명령", _mut(_A4, "P-A", "실물 근거", "`grep -n x y.md`")),
        ("채택값이 장문", _mut(_A4, "P-A", "채택값", "2축 조합 (컬럼명 ∧ 지배 heading)")),
    ]
    S.assert_discriminating(adopted_and_evidence_non_empty, _A4, mutants, green,
                            label="AC-19/adopted-evidence")

    story = S.internal_docs_text(S.STORY_REL)
    if story is None:
        return
    rows = _a4_rows_full(story)
    assert rows, "Story 3.0(a-4) 표를 찾지 못했다"
    bad = [r["id"] for r in rows if not adopted_and_evidence_non_empty([r])]
    assert not bad, "(a-4) `채택값`·`실물 근거` 공허 행: %s" % bad


def test_ac19_a4_binding_type_matches_status():
    """AC-19 ⓒ — `결속` 이 non-empty 이며 `상태` 와 타입 정합이다 (P-AG).

    RTM: 5.3 verification ⓒ.
    `선언` -> discriminating fixture ID / `배제` -> 방출 카운터명(`EM ` 접두 의무).
    """
    mutants = [
        ("결속 공란", _mut(_A4, "P-A", "결속", "")),
        ("선언 행에 방출 카운터 타입", _mut(_A4, "P-A", "결속", "`EM rows_short`")),
        ("배제 행에 fixture ID 타입", _mut(_A4, "P-B", "결속", "`FX-B`")),
        ("배제 행 토큰 일부만 EM 접두", _mut(_A4, "P-B", "결속", "`EM rows_short` · `FX-B`")),
        ("백틱 없는 산문 결속", _mut(_A4, "P-A", "결속", "나중에 붙인다")),
        ("행 0 (vacuous)", []),
    ]
    green = [
        ("선언 행 복수 fixture", _mut(_A4, "P-A", "결속", "`FX-A` · `FX-C`")),
        ("배제 행 복수 카운터",
         _mut(_A4, "P-B", "결속", "`EM rows_epic_na` · `EM rows_short`")),
    ]
    S.assert_discriminating(binding_type_matches_status, _A4, mutants, green,
                            label="AC-19/binding-type")

    story = S.internal_docs_text(S.STORY_REL)
    if story is None:
        return
    rows = _a4_rows_full(story)
    assert rows, "Story 3.0(a-4) 표를 찾지 못했다"
    bad = [r["id"] for r in rows if not binding_type_matches_status([r])]
    assert not bad, "(a-4) `결속` 타입 부정합 행: %s" % bad


def _a4_rows_full(story_text):
    """(a-4) 소비 술어 표 -> [{id, 상태, 채택값, 실물 근거, 결속}]."""
    out = []
    for header, body in S.select_tables(S.md_tables(story_text),
                                        ["상태", "결속", "채택값", "실물 근거"]):
        idx = {k: S.col_index(header, k)
               for k in ("상태", "결속", "채택값", "실물 근거")}
        if min(idx.values()) < 0:
            continue
        for cells in body:
            if not cells or len(cells) <= max(idx.values()):
                continue
            rid = S.norm_cell(cells[0])
            if not re.match(r"^P-[A-Za-z0-9]+$", rid):
                continue
            out.append({"id": rid, **{k: cells[i] for k, i in idx.items()}})
    return out
