"""CFP-2985 RTM 8.1.1 — AC-1 (2) · AC-2 (5) 명명 테스트.

이름은 Change Plan 8.1.1 RTM 이 확정한 계약이다. **바꾸지 않는다** (게이트 Hop3 판정 단위).

각 테스트 = 3 leg 고정 형상
  (1) discriminating core : control 선통과(H-4) -> mutant 개별 RED(H-1 · H-6)
                            -> 등가변형 GREEN 유지(확대 방향 방어). 항상 실행된다.
  (2) 실물 leg (wrapper)  : wrapper repo 안 실 산출물 대조. 항상 실행된다.
  (3) 실물 leg (internal-docs) : CFP2985_INTERNAL_DOCS 주입 시에만. 미주입 = declared 천장.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _cfp2985_spec as S  # noqa: E402


# ---------------------------------------------------------------------------
# AC-1 술어 — fix-event-v1 계약 `원인 판정` 값공간
# ---------------------------------------------------------------------------
def contract_enum_values(text, key="원인 판정"):
    """계약 문서의 `"<key>":` 블록에서 `values` 리스트를 뽑는다 (블록형 ∧ 인라인형 둘 다).

    표기 앵커 결속 회피: `values: [a, b]` 인라인도 같은 값을 낸다.
    """
    lines = text.split("\n")
    key_pat = re.compile(r'^(\s*)"?%s"?\s*:\s*$' % re.escape(key))
    for i, ln in enumerate(lines):
        m = key_pat.match(ln)
        if not m:
            continue
        base = len(m.group(1))
        block = []
        for nxt in lines[i + 1:]:
            if nxt.strip() == "":
                block.append(nxt)
                continue
            indent = len(nxt) - len(nxt.lstrip())
            if indent <= base:
                break
            block.append(nxt)
        return _values_from_block(block)
    return []


def _values_from_block(block):
    for i, ln in enumerate(block):
        m = re.match(r"^\s*values\s*:\s*(.*)$", ln)
        if not m:
            continue
        tail = m.group(1).strip()
        if tail.startswith("["):
            inner = tail[1:tail.rindex("]")] if "]" in tail else tail[1:]
            return [v.strip().strip('"').strip("'") for v in inner.split(",") if v.strip()]
        vals = []
        for nxt in block[i + 1:]:
            if nxt.strip() == "":
                continue
            item = re.match(r"^\s*-\s+(.*)$", nxt)
            if not item:
                if re.match(r"^\s*\S+\s*:", nxt):
                    break
                continue
            v = re.sub(r"\s+#.*$", "", item.group(1)).strip().strip('"').strip("'")
            if v:
                vals.append(v)
        return vals
    return []


def offaxis_judged(text, axes=S.OFFAXIS_4, key="원인 판정"):
    """4축 각각이 `원인 판정` 블록 안에서 **판정**됐는가 -> {축: bool}.

    판정 = 채택(enum value 로 등재) OR 배제(같은 블록에 축 토큰 + 배제 마커 + 사유 본문).
    블록 **밖** 산문 언급은 판정이 아니다 (E-4 형 오통과 차단).
    """
    values = {S.norm_cell(v) for v in contract_enum_values(text, key)}
    block = _key_block(text, key)
    judged = {}
    for ax in axes:
        if ax in values:
            judged[ax] = True
            continue
        hit = False
        for ln in block:
            if ax not in ln:
                continue
            if re.search(r"(배제|제외|미채택|not adopted)", ln):
                reason = re.sub(r"^.*?(배제|제외|미채택|not adopted)\s*[:—\-]?\s*", "", ln).strip()
                if len(reason) >= 2:
                    hit = True
                    break
        judged[ax] = hit
    return judged


def _key_block(text, key):
    lines = text.split("\n")
    key_pat = re.compile(r'^(\s*)"?%s"?\s*:\s*$' % re.escape(key))
    for i, ln in enumerate(lines):
        m = key_pat.match(ln)
        if not m:
            continue
        base = len(m.group(1))
        block = []
        for nxt in lines[i + 1:]:
            if nxt.strip() == "":
                block.append(nxt)
                continue
            if len(nxt) - len(nxt.lstrip()) <= base:
                break
            block.append(nxt)
        return block
    return []


_CONTROL_V16 = '''
  "트리거":
    type: string

  "원인 판정":
    type: enum
    values:
      - 설계        # -> Change Plan 갱신
      - 구현        # -> commit append
      - 요구사항    # -> 요구사항 lane 재진입
      - 환경        # -> 인프라 처분
      - 설계-리뷰   # -> 설계리뷰 재실행
      - 구현-리뷰   # -> 구현리뷰 재실행
    decision_rule_ssot: skills/root-cause-decision/SKILL.md

  "재실행 범위":
    type: string
'''


def test_ac1_root_cause_values_enum_non_empty():
    """AC-1 leg1 — 계약 `원인 판정` 의 `values` 리스트가 non-empty 다.

    RTM: 5.3 verification "values 리스트 non-empty".
    mutant 정본 = Story 5.4 AC-1 (values 블록 삭제 -> RED / 인라인 표기 -> GREEN 유지).
    """
    real = S.wrapper_text(S.CONTRACT_FIX_EVENT_REL)
    assert real is not None, "%s 부재 — 판정불가" % S.CONTRACT_FIX_EVENT_REL

    pred = lambda t: len(contract_enum_values(t)) > 0  # noqa: E731

    # ★ 치환은 **`원인 판정` 블록 한정**이다. 파일 전체 첫 `values:` 를 건드리면 다른 키의
    #   블록을 깨고 대상 술어는 그대로 GREEN 이라 mutant 가 조용히 무효가 된다 (실측 1회).
    m_deleted = _mutate_values_block(real, "원인 판정", None)
    m_empty = _mutate_values_block(real, "원인 판정", "values: []")
    v_inline = _mutate_values_block(real, "원인 판정", "values: [설계, 구현]")

    # mutant 가 실제로 원문을 바꿨는지 먼저 확인 — 치환 실패한 mutant 를 RED 로 읽으면 무효 mutant 다.
    for nm, txt in (("삭제", m_deleted), ("빈 리스트", m_empty), ("인라인", v_inline)):
        assert txt != real, "mutant '%s' 주입 실패(원문 무변경) — 주입 실증 없이 해석 금지" % nm

    S.assert_discriminating(
        pred, real,
        mutants=[("values 블록 삭제", m_deleted), ("values 빈 리스트", m_empty)],
        green_variants=[("values 인라인 리스트 표기", v_inline)],
        label="AC-1/values-non-empty",
    )
    assert pred(real) is True, "실 계약의 `원인 판정` values 가 비었다"


def test_ac1_four_offaxis_verdict_statement_present():
    """AC-1 leg2 — 실측 enum-밖 4축(요구사항/환경/설계-리뷰/구현-리뷰) 각각에 판정 문면이 있다.

    RTM: 5.3 verification "실측 enum-밖 4축 각각 판정 문면 존재".
    검사 대상은 **문면 존재**이며 `92행 15.6%` 수치는 대조하지 않는다 (5.3 AC-1 명시 —
    정의역이 588 -> 698 로 이동했으므로 수치를 검사에 쓰면 born-red).
    """
    pred = lambda t: all(offaxis_judged(t).values())  # noqa: E731

    control = _CONTROL_V16
    mutants = []
    for ax in S.OFFAXIS_4:                       # H-6 — 축을 묶지 않고 하나씩 끈다
        mutants.append(("%s 축 판정 삭제" % ax,
                        re.sub(r"^\s*-\s*%s.*\n" % re.escape(ax), "", control, flags=re.M)))
    # 블록 **밖** 산문 언급만으로는 판정이 아니다.
    outside = re.sub(r"^\s*-\s*환경.*\n", "", control, flags=re.M) + "\n환경 축은 나중에 본다\n"
    mutants.append(("블록 밖 산문 언급만", outside))

    excluded = re.sub(r"^(\s*)-\s*환경.*\n",
                      r"\1  # 환경: 배제 — 인프라 원인은 FIX 루프가 아니라 별 경로다\n",
                      control, flags=re.M)
    green = [("배제 사유 형태 판정", excluded),
             ("값 백틱 장식", control.replace("- 요구사항", "- `요구사항`"))]

    for nm, txt in mutants + green:
        assert txt != control, "mutant/변형 '%s' 주입 실패(원문 무변경)" % nm

    S.assert_discriminating(pred, control, mutants, green, label="AC-1/offaxis-4")

    real = S.wrapper_text(S.CONTRACT_FIX_EVENT_REL)
    judged = offaxis_judged(real)
    missing = sorted(ax for ax, ok in judged.items() if not ok)
    assert not missing, (
        "실 계약 %s 에서 판정 문면이 없는 enum-밖 축: %s. "
        "Change Plan 5 의 D-1(fix-event-v1 v1.6 — enum 6값 + 판정 문면) 미착지 상태다."
        % (S.CONTRACT_FIX_EVENT_REL, missing)
    )


# ---------------------------------------------------------------------------
# AC-2 술어
# ---------------------------------------------------------------------------
# (a-4) 결속 명세 표 형상 — `상태` 가 `선언` 이면 fixture ID, `배제` 면 `EM ` 접두 카운터 (P-AG).
_A4_CONTROL = [
    {"id": "P-A", "상태": "선언", "결속": "`FX-A`"},
    {"id": "P-AB", "상태": "선언", "결속": "`FX-AB`"},
    {"id": "P-B", "상태": "배제", "결속": "`EM rows_epic_na`"},
    {"id": "P-C", "상태": "배제", "결속": "`EM rows_short`"},
]

EMIT_COUNTERS = ("rows_epic_na", "rows_short", "rows_unparsed_form",
                 "rows_adjacent_excluded", "rows_alias_unmatched")


def declared_rows_bound(rows):
    """`선언` 원소마다 fixture 결속이 실재하는가 (AC-2 (1) 의 결속 층)."""
    for r in rows:
        if S.norm_cell(r.get("상태", "")) != "선언":
            continue
        toks = re.findall(r"`([^`]+)`", r.get("결속", ""))
        toks = [t for t in toks if t.strip()]
        if not toks:
            return False
        if all(t.startswith("EM ") for t in toks):   # 방출 카운터는 fixture 결속이 아니다
            return False
    return True


def emit_counters_increase(before, after, keys=EMIT_COUNTERS):
    """`배제` 원소의 방출 카운터가 산출에 실재하고 fixture 주입 시 **상대 증가**하는가.

    절대값 pin 을 쓰지 않는다 (8.2 — 방출 카운터는 절대값 금지, 상대 증가만).
    """
    for k in keys:
        if k not in before or k not in after:
            return False
        if not isinstance(before[k], int) or not isinstance(after[k], int):
            return False
        if after[k] <= before[k]:
            return False
    return True


def pair_verdict(collect, positives, negatives):
    """positive 는 수집 ∧ negative 는 배제 — **같은 실행에서 동시에** 올바른가 (AC-2 (1)-b)."""
    got = set(collect())
    return all(p in got for p in positives) and all(n not in got for n in negatives)


def superset_oracle(collected, required):
    """존재 assert (등식 pin 아님) — 수직 성장은 GREEN 이어야 한다 (O-1' / O-2 철회 경위)."""
    return set(required) <= set(collected)


def test_ac2_declared_predicate_fixtures_all_red():
    """AC-2 (1) — (a-4) `선언` 원소마다 discriminating fixture 결속이 있고 전건 RED 다.

    RTM: 5.3 verification (1) "`선언` 원소 discriminating fixture 전건 RED".
    """
    mutants = [
        ("선언 행 결속 공란", _swap(_A4_CONTROL, "P-A", "결속", "")),
        ("선언 행 결속이 방출 카운터 타입", _swap(_A4_CONTROL, "P-AB", "결속", "`EM rows_short`")),
        ("선언 행 결속이 백틱 없는 산문", _swap(_A4_CONTROL, "P-A", "결속", "나중에 붙인다")),
    ]
    green = [
        ("복수 fixture 결속", _swap(_A4_CONTROL, "P-A", "결속", "`FX-A` · `FX-C`")),
        ("장식 붙은 상태값", _swap(_A4_CONTROL, "P-A", "상태", "**선언** (Iter 3 신설)")),
    ]
    S.assert_discriminating(declared_rows_bound, _A4_CONTROL, mutants, green,
                            label="AC-2/declared-fixture-binding")

    story = S.internal_docs_text(S.STORY_REL)
    if story is None:
        return
    rows = _a4_rows(story)
    assert rows, "Story 3.0(a-4) 소비 술어 표를 찾지 못했다 — 표 선택 술어 재확인 필요"
    unbound = [r["id"] for r in rows
               if S.norm_cell(r.get("상태", "")) == "선언" and not declared_rows_bound([r])]
    assert not unbound, "(a-4) `선언` 원소 중 fixture 결속 부재: %s" % unbound

    root = S.internal_docs_root()
    fixtures = root / "tests" / "fixtures" / "story_section10"
    assert fixtures.is_dir(), (
        "internal-docs %s 부재 — Change Plan 5 D-9(mutant 6방향 fixture) 미착지. "
        "결속 ID 는 선언됐으나 전건 RED 를 실증할 fixture 실물이 없다." % fixtures
    )


def test_ac2_excluded_predicate_emit_counters_increase():
    """AC-2 (1) — `배제` 원소는 fixture 대신 방출 카운터 5종이 실재하고 주입 시 증가한다.

    RTM: 5.3 verification (1) "`배제` 원소 방출 카운터 assert".
    """
    before = {k: 3 for k in EMIT_COUNTERS}
    after = {k: 4 for k in EMIT_COUNTERS}
    pred = lambda pair: emit_counters_increase(pair[0], pair[1])  # noqa: E731

    mutants = []
    for k in EMIT_COUNTERS:                       # H-6 — 카운터를 하나씩 끈다
        drop = dict(after)
        drop.pop(k)
        mutants.append(("카운터 %s 산출 부재" % k, (before, drop)))
        flat = dict(after)
        flat[k] = before[k]
        mutants.append(("카운터 %s 증가 0" % k, (before, flat)))
    dec = dict(after)
    dec["rows_short"] = before["rows_short"] - 1
    mutants.append(("카운터 감소", (before, dec)))

    green = [
        ("증가폭 상이 (절대값 비결속)", (before, {k: before[k] + i + 1
                                          for i, k in enumerate(EMIT_COUNTERS)})),
        ("base 가 0 인 코퍼스", ({k: 0 for k in EMIT_COUNTERS},
                                {k: 1 for k in EMIT_COUNTERS})),
    ]
    S.assert_discriminating(pred, (before, after), mutants, green,
                            label="AC-2/emit-counter-increase")

    story = S.internal_docs_text(S.STORY_REL)
    if story is None:
        return
    for k in EMIT_COUNTERS:
        assert k in story, "(a-4) 배제 축 방출 카운터 `%s` 가 Story 문면에 부재" % k


def test_ac2_real_corpus_positive_negative_pairs():
    """AC-2 (1)-b — 실 코퍼스 positive · negative 쌍 3종(P-AB · P-AE · P-B)이 동시에 옳다.

    RTM: 5.3 verification (1)-b. **정수 등식 pin 금지** — 존재/배제 쌍만 본다 (8.1 L3).
    """
    positives = ["CFP-1746.md:158", "CFP-1317-S3.md:379", "CFP-2249.md"]
    negatives = ["CFP-622.md:136", "CFP-2659.md:440", "CFP-1059.md"]
    pred = lambda got: pair_verdict(lambda: got, positives, negatives)  # noqa: E731

    control = list(positives) + ["CFP-2913.md:12"]
    mutants = [("positive 미수집(축소)", [p for p in positives if p != positives[0]]),
               ("negative 혼입(확대)", control + [negatives[0]]),
               ("전량 수집(무차별)", control + negatives),
               ("전량 미수집", [])]
    green = [("무관 행 추가 수집 (수직 성장)", control + ["CFP-9999.md:1"]),
             ("수집 순서 변경", list(reversed(control)))]
    S.assert_discriminating(pred, control, mutants, green, label="AC-2/corpus-pn-pairs")

    root = S.internal_docs_root()
    if root is None:
        return
    for coord in positives + negatives:
        fname = coord.split(":")[0]
        rc, out, _ = S.run_rc(["git", "cat-file", "-e", "%s:wrapper/stories/%s" % (S.CORPUS_SHA, fname)],
                              cwd=root)
        assert rc == 0, (
            "L3 코퍼스 %s 에 %s 부재 — 등재 쌍 좌표가 immutable SHA 에서 resolve 되지 않는다"
            % (S.CORPUS_SHA[:8], fname)
        )


def test_ac2_corpus_invariant_oracles_o1_o2():
    """AC-2 (2) — 코퍼스-불변 오라클 O-1' · O-2 가 **존재 assert** 로 성립한다.

    RTM: 5.3 verification (2). 등식 pin 을 쓰면 대상 파일 10 이 자라는 것만으로
    파서 정상 상태에서 RED 가 나고, 그 RED 를 끄는 가장 싼 방법이 파서를 다시
    좁히는 것(ratchet-in)이다 -> **부분집합 관계만** 본다.
    """
    o1 = ["CFP-2913#5", "CFP-2913#6", "CFP-2913#7", "CFP-2913#8", "CFP-2913#9"]
    o2 = ["CFP-966#2", "CFP-966#3", "CFP-966#4"]
    required = o1 + o2
    pred = lambda got: superset_oracle(got, required)  # noqa: E731

    control = list(required)
    mutants = [("O-1' 행 1건 누락", [x for x in required if x != "CFP-2913#7"]),
               ("O-2 행 1건 누락", [x for x in required if x != "CFP-966#3"]),
               ("전량 미수집", [])]
    green = [("수직 성장 (10 이 자람)", control + ["CFP-2913#10", "CFP-2913#11"]),
             ("무관 파일 행 추가", control + ["CFP-1234#1"])]
    S.assert_discriminating(pred, control, mutants, green, label="AC-2/oracles-o1-o2")

    root = S.internal_docs_root()
    if root is None:
        return
    for fname in ("CFP-2913.md", "CFP-966.md"):
        rc, _, _ = S.run_rc(["git", "cat-file", "-e",
                             "%s:wrapper/stories/%s" % (S.CORPUS_SHA, fname)], cwd=root)
        assert rc == 0, "오라클 대상 %s 가 %s 에 부재" % (fname, S.CORPUS_SHA[:8])


def test_ac2_sibling_site_regression_no_detection_loss():
    """AC-2 (3) — 봉합 후 형제 site 검출이 전건 보존된다 (H-5 검출 집합 대조).

    RTM: 5.3 verification (3) "봉합 판정 (나) 형제 site 회귀".
    합격 술어 = `신판 검출집합 ⊇ 전임 판 검출집합` 이 **실행으로** 확인됨.
    "새 축이 더 강하므로 옛 축은 불필요" 라는 논증만으로는 통과하지 않는다.
    """
    prev = {"site-a", "site-b", "site-c"}
    pred = lambda new: prev <= set(new)  # noqa: E731

    control = set(prev)
    mutants = [("형제 site 1건 검출 상실", prev - {"site-b"}),
               ("축 교환 (신설로 대체)", {"site-x", "site-y", "site-z"}),
               ("검출 0", set())]
    green = [("합집합 확장", prev | {"site-d"}),
             ("동일 집합 순서 무관", set(reversed(sorted(prev))))]
    S.assert_discriminating(pred, control, mutants, green, label="AC-2/h5-sibling-regression")

    root = S.internal_docs_root()
    if root is None:
        return
    parser = root / "scripts" / "lib" / "story_section10_parser.py"
    assert parser.is_file(), (
        "internal-docs %s 부재 — Change Plan 5 D-7(파서 primitive 추출) 미착지. "
        "전임 판 대비 검출 집합 대조를 같은 실행에서 돌릴 대상이 없다." % parser
    )


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------
def _mutate_values_block(text, key, replacement):
    """`"<key>":` 블록 **안의** `values:` 리스트만 치환/삭제한다.

    replacement=None -> 블록 삭제. 그 외 -> 그 한 줄로 대체 (인라인 표기 등).
    파일 전역 첫 `values:` 를 건드리는 순진한 치환은 무효 mutant 를 만든다.
    """
    lines = text.split("\n")
    key_pat = re.compile(r'^(\s*)"?%s"?\s*:\s*$' % re.escape(key))
    for i, ln in enumerate(lines):
        m = key_pat.match(ln)
        if not m:
            continue
        base = len(m.group(1))
        j = i + 1
        while j < len(lines):
            if lines[j].strip() == "":
                j += 1
                continue
            if len(lines[j]) - len(lines[j].lstrip()) <= base:
                return text                       # 블록 안에 values 없음
            vm = re.match(r"^(\s*)values\s*:\s*$", lines[j])
            if vm:
                vind = len(vm.group(1))
                k = j + 1
                while k < len(lines):
                    if lines[k].strip() == "":
                        k += 1
                        continue
                    if len(lines[k]) - len(lines[k].lstrip()) <= vind:
                        break
                    k += 1
                head = lines[:j]
                tail = lines[k:]
                mid = [] if replacement is None else [" " * vind + replacement]
                return "\n".join(head + mid + tail)
            j += 1
    return text


def _swap(rows, rid, field, value):
    out = []
    for r in rows:
        r2 = dict(r)
        if r2["id"] == rid:
            r2[field] = value
        out.append(r2)
    return out


def _a4_rows(story_text):
    """Story 3.0(a-4) 소비 술어 표 -> [{id, 상태, 결속, ...}] (헤더 3열 동시 보유로 선택)."""
    tables = S.select_tables(S.md_tables(story_text), ["상태", "결속", "채택값"])
    rows = []
    for header, body in tables:
        i_state = S.col_index(header, "상태")
        i_bind = S.col_index(header, "결속")
        i_adopt = S.col_index(header, "채택값")
        for cells in body:
            if not cells or len(cells) <= max(i_state, i_bind, i_adopt):
                continue
            rid = S.norm_cell(cells[0])
            if not re.match(r"^P-[A-Za-z0-9]+$", rid):
                continue
            rows.append({"id": rid, "상태": cells[i_state], "결속": cells[i_bind],
                         "채택값": cells[i_adopt]})
    return rows
