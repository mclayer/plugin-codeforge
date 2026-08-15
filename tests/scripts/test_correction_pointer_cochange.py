#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""test_correction_pointer_cochange.py — co-change 게이트의 판별력 검사.

── 착지 조건 = **반사실 실증** ────────────────────────────────────────────────
  직전 게이트(ADR-177)는 자기 천장 각인을 미착지로 남겼고, 그게 정확히 그 게이트가
  겨냥하는 class 의 자기 발현이었다. 여기서는 **실재하는 두 커밋의 실제 diff** 로
  방향을 각인한다 — 합성 diff 로 대체하지 않는다.

    · `8266e0e82` (ADR-172 Amendment 4 저작, 앞 절 포인터 0)  → **RED**
    · `b41e69af9` (A3-2 정정 포인터 봉합)                      → **GREEN**

  두 diff 는 `fixtures/correction_pointer_cochange/*.patch` 에 **git 출력 그대로**
  동결돼 있다(post-image 도 함께). 동결한 이유는 squash-merge 로 두 SHA 가 사라져도
  반사실이 남게 하기 위함이며, live git 이 있는 환경에서는
  `test_frozen_fixture_matches_live_git` 이 동결본과 실물의 일치를 매번 대조한다
  (동결이 실물에서 떨어져 나가는 것을 막는 drift 오라클).

── 천장 각인 ──────────────────────────────────────────────────────────────────
  모듈 docstring 의 정직 천장 ①②⑤⑦⑧ 은 산문으로만 두지 않고 아래
  `test_ceiling_*` 가 assert 로 각인한다. 검사기를 그 방향으로 넓히면 해당 테스트가
  RED 가 되어 천장 문서 갱신이 강제된다. ⑧(행번호 포인터 stale)은 각인이 공허해지지
  않도록 **선확인**(표본이 절 ID 문법에 0 match)과 **대조군**(같은 뒤집기를 절 ID 로
  앵커하면 잡힌다)을 함께 건다.
"""

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _correction_pointer_cochange as sut               # noqa: E402
from _absolute_claim_ratchet import parse_added_lines    # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "correction_pointer_cochange"
ADR172 = "archive/adr/ADR-172-local-scheduled-task-residue-observation.md"

RED_SHA = "8266e0e82"     # Amendment 4 저작 — 앞 절 포인터 0
GREEN_SHA = "b41e69af9"   # A3-2 정정 포인터 봉합

SYNTH_PATH = "archive/adr/ADR-999-synthetic.md"


# ═══════════════════════════ 합성 케이스 빌더 ════════════════════════════════════
def build(entries, path=SYNTH_PATH):
    """`[(kind, text)]` → `(post_image, diff_text)`. kind ∈ {`ctx`, `add`, `del`}.

    `del` 줄은 post-image 에 담기지 않는다. 문서 전체를 hunk 하나로 낸다 — 문맥 줄
    처리까지 같이 태우기 위해서다."""
    post = [t for k, t in entries if k in ("ctx", "add")]
    body, oc, nc = [], 0, 0
    for k, t in entries:
        if k == "ctx":
            body.append(" " + t); oc += 1; nc += 1
        elif k == "add":
            body.append("+" + t); nc += 1
        elif k == "del":
            body.append("-" + t); oc += 1
        else:
            raise ValueError(k)
    diff = "\n".join(
        ["diff --git a/%s b/%s" % (path, path), "--- a/%s" % path, "+++ b/%s" % path,
         "@@ -1,%d +1,%d @@" % (oc, nc)] + body) + "\n"
    return "\n".join(post) + "\n", diff


def synth(sec1_body=None, amendment_body=(), tail=()):
    """대조·mutant 용 합성 ADR 한 벌.

    `sec1_body` = `§결정 1` 절에 넣을 `[(kind, text)]` (기본 = 문맥 줄 하나)."""
    sec1 = sec1_body if sec1_body is not None else [("ctx", "첫 결정 본문.")]
    entries = [
        ("ctx", "# ADR-999: 합성 대조 문서"),
        ("ctx", ""),
        ("ctx", "## 결정"),
        ("ctx", ""),
        ("ctx", "### §결정 1 — 첫 결정"),
        ("ctx", ""),
    ]
    entries += sec1
    entries += [
        ("ctx", ""),
        ("ctx", "### §결정 2 — 둘째 결정"),
        ("ctx", ""),
        ("ctx", "둘째 결정 본문."),
        ("ctx", ""),
        ("add", "## Amendment 1 (합성) — 정정"),
        ("add", ""),
        ("add", "### A1-1 — 정정 절"),
        ("add", ""),
    ]
    entries += [("add", t) for t in amendment_body]
    entries += list(tail)
    return build(entries)


def run(post_image, diff, path=SYNTH_PATH, **kw):
    return sut.evaluate(diff, {path: post_image}, **kw)


def violated_ids(result):
    return sorted({c.sec_id for c in result["violations"]})


# ═══════════════════════════ fixture 적재 ════════════════════════════════════════
def load_fixture(sha):
    """동결 반사실 → `(diff_text, {path: post_image})`."""
    diff = (FIXTURES / ("%s.patch" % sha)).read_text(encoding="utf-8")
    post = (FIXTURES / ("%s.postimage.txt" % sha)).read_text(encoding="utf-8")
    return diff, {ADR172: post}


def _git(*args):
    return subprocess.run(["git", "-C", str(REPO_ROOT), *args],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def sha_available(sha):
    return _git("rev-parse", "--verify", "--quiet", sha + "^{commit}").returncode == 0


# ═══════════════════════ 착지 조건 — 반사실 2건 (실 diff) ════════════════════════
def test_counterfactual_amendment4_authoring_is_red():
    """`8266e0e82` = Amd 4 가 A3-2·A3-4 를 뒤집으며 그 절에 표식을 남기지 않은 실물.

    이 커밋이 RED 가 아니면 게이트는 겨냥한 재발을 놓친 것이다."""
    diff, images = load_fixture(RED_SHA)
    result = sut.evaluate(diff, images)
    assert result["violations"], "Amendment 4 저작 diff 가 통과했다 — 겨냥한 재발 미검출"
    assert violated_ids(result) == ["A3-2", "A3-4", "A3-5"], violated_ids(result)
    assert not result["undecidable"]


def test_counterfactual_pointer_repair_is_green():
    """`b41e69af9` = A3-2 절 말미에 정정 포인터를 넣은 봉합 커밋. 통과해야 한다."""
    diff, images = load_fixture(GREEN_SHA)
    result = sut.evaluate(diff, images)
    assert result["violations"] == [], sut.format_report(result)
    assert not result["undecidable"]
    # 봉합의 실체 = 피인용 절 A3-2 가 같은 diff 에서 편집됐다는 것.
    assert any(c.sec_id == "A3-2" and c.disposition == "cochanged" for c in result["citations"])


@pytest.mark.parametrize("sha,expect_red", [(RED_SHA, True), (GREEN_SHA, False)])
def test_frozen_fixture_matches_live_git(sha, expect_red):
    """동결본이 실물 git 출력에서 떨어져 나가지 않았는지 대조 (drift 오라클).

    SHA 가 없는 환경(squash-merge 이후 main 등)에서는 이 대조만 건너뛴다 — 반사실
    판정 자체는 위 두 테스트가 동결본으로 **항상** 수행한다 [ceiling: 그 두 테스트에 skip 분기가 없다는 구조 서술 — 같은 파일에서 확인되는 mention 이다]
    (그러므로 SHA 소멸이 커버리지 손실로 이어지지 않는다)."""
    if not sha_available(sha):
        pytest.skip("SHA %s 미해소 — drift 대조만 생략(반사실 판정은 동결본이 수행)" % sha)
    live_diff = _git("diff", "--no-color", "--no-ext-diff", "-U0",
                     "%s^...%s" % (sha, sha), "--", ADR172).stdout
    live_post = _git("show", "%s:%s" % (sha, ADR172)).stdout
    frozen_diff, frozen_images = load_fixture(sha)
    assert live_diff.replace("\r\n", "\n") == frozen_diff, "동결 diff 가 실물과 어긋났다: %s" % sha
    assert live_post.replace("\r\n", "\n") == frozen_images[ADR172], \
        "동결 post-image 가 실물과 어긋났다: %s" % sha
    result = sut.evaluate(live_diff, {ADR172: live_post})
    assert bool(result["violations"]) is expect_red


def test_live_git_full_commit_verdicts_match():
    """실 git 축(경로 필터 없이 커밋 전체)에서도 같은 방향인지 확인."""
    if not (sha_available(RED_SHA) and sha_available(GREEN_SHA)):
        pytest.skip("반사실 SHA 미해소 — 동결본 경로가 판정을 수행한다")
    red = sut.run_git(str(REPO_ROOT), RED_SHA + "^", RED_SHA)
    green = sut.run_git(str(REPO_ROOT), GREEN_SHA + "^", GREEN_SHA)
    assert red is not None and green is not None
    assert violated_ids(red) == ["A3-2", "A3-4", "A3-5"], sut.format_report(red)
    assert green["violations"] == [], sut.format_report(green)


# ═══════════════════════ 대조군 — 오탐 0 ═════════════════════════════════════════
def test_control_ordinary_doc_diff_without_section_ids():
    """절 ID 인용이 없는 평범한 문서 diff → 위반 0."""
    post, diff = synth(amendment_body=[
        "이 절은 표기를 다듬는다. 앞 절을 지목하지 않는다.",
        "숫자 2026-08-15 와 경로 `scripts/lib/x.py` 는 절 ID 가 아니다.",
    ])
    result = run(post, diff)
    assert result["violations"] == [], sut.format_report(result)
    assert result["citations"] == []


def test_control_non_section_id_tokens_are_not_citations():
    """`ADR-172` · `CFP-2949` · `AC-4` 는 절 ID 문법이 아니다 (선두 문자 규칙)."""
    ids = sut.cited_ids("ADR-172 와 CFP-2949 와 AC-4 와 2026-08-15 를 적는다", own_adr=999)
    assert [i for i, foreign in ids if not foreign] == []


def test_control_citation_outside_amendment_scope_is_out_of_domain():
    """Amendment 밖(`§결정 2` 안)에서 앞 절을 참조하는 줄은 인용 정의역 밖이다.

    같은 세대 교차참조를 정정으로 오인하면 평범한 ADR 저작이 전부 걸린다."""
    post, diff = build([
        ("ctx", "# ADR-999: 합성"),
        ("ctx", ""),
        ("ctx", "### §결정 1 — 첫 결정"),
        ("ctx", ""),
        ("ctx", "첫 결정 본문."),
        ("ctx", ""),
        ("ctx", "### §결정 2 — 둘째 결정"),
        ("ctx", ""),
        ("add", "이 결정은 §결정 1 의 전제를 그대로 쓴다."),
    ])
    result = run(post, diff)
    assert result["violations"] == []
    assert result["citations"] == []


def test_control_path_outside_domain_is_ignored():
    """`archive/adr/` 밖 경로는 기본 정의역에 없다."""
    post, diff = synth(amendment_body=["§결정 1 을 뒤집는다."])
    diff = diff.replace(SYNTH_PATH, "docs/change-plans/CFP-999.md")
    result = sut.evaluate(diff, {"docs/change-plans/CFP-999.md": post})
    assert result["violations"] == []


# ═══════════════════════ 핵심 판정 ══════════════════════════════════════════════
def test_stale_backward_citation_is_violation():
    """Amendment 블록이 선행 `§결정 1` 을 지목했는데 그 절이 무편집 → 위반."""
    post, diff = synth(amendment_body=["§결정 1 의 결론을 뒤집는다."])
    result = run(post, diff)
    assert violated_ids(result) == ["§결정 1"]


def test_cochanged_backward_citation_passes():
    """같은 diff 에서 `§결정 1` 절이 편집되면 통과."""
    post, diff = synth(
        sec1_body=[("ctx", "첫 결정 본문."), ("add", "> ★ 후속 A1-1 이 이 절을 정정한다.")],
        amendment_body=["§결정 1 의 결론을 뒤집는다."])
    result = run(post, diff)
    assert result["violations"] == [], sut.format_report(result)


def test_forward_citation_is_not_a_violation():
    """뒤 절을 가리키는 것이 곧 정정 포인터다 — 요구 대상이 아니다."""
    post, diff = synth(
        amendment_body=["뒤의 A1-2 가 이어받는다."],
        tail=[("add", ""), ("add", "### A1-2 — 이어받는 절"), ("add", ""), ("add", "본문.")])
    result = run(post, diff)
    assert result["violations"] == []
    assert any(c.sec_id == "A1-2" and c.disposition == "forward" for c in result["citations"])


def test_sub_lettered_section_id_resolves():
    """`A1-2-a` 꼴 소절 ID 도 해소된다."""
    post, diff = build([
        ("ctx", "# ADR-999: 합성"),
        ("ctx", ""),
        ("ctx", "## Amendment 1 (합성) — 정정"),
        ("ctx", ""),
        ("ctx", "#### A1-2-a — 소절"),
        ("ctx", ""),
        ("ctx", "소절 본문."),
        ("ctx", ""),
        ("ctx", "### A1-3 — 뒤 절"),
        ("ctx", ""),
        ("add", "앞의 A1-2-a 를 뒤집는다."),
    ])
    result = run(post, diff)
    assert violated_ids(result) == ["A1-2-a"]


def test_unresolved_section_id_is_not_a_violation():
    """이 문서에 없는 절 ID 는 판정하지 않는다 (타 문서 지목·오타)."""
    post, diff = synth(amendment_body=["§결정 99 를 뒤집는다."])
    result = run(post, diff)
    assert result["violations"] == []
    assert any(c.disposition == "unresolved" for c in result["citations"])


def test_foreign_adr_prefixed_citation_is_out_of_domain():
    """`ADR-171 §결정 1` 은 이 문서의 `§결정 1` 이 아니다."""
    post, diff = synth(amendment_body=["ADR-171 §결정 1 을 근거로 삼는다."])
    result = run(post, diff)
    assert result["violations"] == []
    assert any(c.disposition == "foreign" for c in result["citations"])


def test_own_adr_prefixed_citation_is_kept():
    """자기 번호를 명시한 `ADR-999 §결정 1` 은 자기 절 지목으로 센다."""
    post, diff = synth(amendment_body=["ADR-999 §결정 1 을 뒤집는다."])
    result = run(post, diff)
    assert violated_ids(result) == ["§결정 1"]


# ═══════════════════════ 삭제 줄 · 문맥 줄 정밀도 ═══════════════════════════════
def test_deleted_line_is_not_a_citation_source():
    """삭제된 줄에 남아 있던 절 ID 인용으로 위반을 만들지 않는다."""
    post, diff = synth(amendment_body=[], tail=[("del", "§결정 1 을 뒤집는다.")])
    result = run(post, diff)
    assert result["violations"] == []
    assert result["citations"] == []


def test_context_line_is_not_a_citation_source():
    """문맥 줄(미변경)에 있는 인용도 대상이 아니다 — 정의역은 추가 줄이다."""
    post, diff = build([
        ("ctx", "# ADR-999: 합성"),
        ("ctx", ""),
        ("ctx", "### §결정 1 — 첫 결정"),
        ("ctx", ""),
        ("ctx", "첫 결정 본문."),
        ("ctx", ""),
        ("ctx", "## Amendment 1 (합성) — 정정"),
        ("ctx", ""),
        ("ctx", "§결정 1 을 뒤집는다."),          # 기존 재고 — 정의역 밖
        ("add", "표기만 다듬는 새 줄."),
    ])
    result = run(post, diff)
    assert result["violations"] == []
    assert result["citations"] == []


def test_deletion_inside_cited_section_counts_as_cochange():
    """지워서 한 정정이 거짓 위반이 되지 않게, 삭제 위치도 편집 증거로 센다."""
    post, diff = synth(
        sec1_body=[("ctx", "첫 결정 본문."), ("del", "이 문장은 틀렸으므로 지운다.")],
        amendment_body=["§결정 1 의 결론을 뒤집는다."])
    result = run(post, diff)
    assert result["violations"] == [], sut.format_report(result)


def test_blank_added_line_is_not_cochange_evidence():
    """공백만 있는 추가 줄은 편집 증거가 아니다.

    실물 근거: `8266e0e82` 의 `:377` 빈 줄이 A3-5 슬라이스 꼬리에 들어가 그 절에
    헛된 편집 공로를 줄 뻔했다."""
    post, diff = synth(
        sec1_body=[("ctx", "첫 결정 본문."), ("add", "   ")],
        amendment_body=["§결정 1 의 결론을 뒤집는다."])
    result = run(post, diff)
    assert violated_ids(result) == ["§결정 1"]


def test_blank_line_credit_would_have_hidden_a3_5():
    """공백 줄을 증거로 세면 실물 `8266e0e82` 의 A3-5 위반이 사라진다 (근거 각인)."""
    diff, images = load_fixture(RED_SHA)
    baseline = sut.evaluate(diff, images)
    assert "A3-5" in violated_ids(baseline)

    orig = sut.section_is_cochanged

    def lax(span, added_linenos, deleted_anchors):      # 공백 줄도 증거로 세는 판본
        a, b = span
        added, deleted, _ = sut.walk_diff(diff)
        allno = {x.lineno for x in added if x.path == ADR172}
        return any(a <= n < b for n in allno) or orig(span, set(), deleted_anchors)

    sut.section_is_cochanged = lax
    try:
        lax_result = sut.evaluate(diff, images)
    finally:
        sut.section_is_cochanged = orig
    assert "A3-5" not in violated_ids(lax_result), "공백 줄 완화가 A3-5 를 가리지 못했다 — 근거 재확인 필요"


# ═══════════════════════ mutant — 판정 요소가 load-bearing 인가 ══════════════════
#
# mutant 은 "검사기를 망가뜨리면 통과하더라" 로 그치지 않는다 — 망가뜨린 상태에서
# **위 반사실 테스트를 그대로 다시 돌려** 그것이 실제로 RED 가 되는지 확인한다.
# 대조군 없이 "mutant 이 0 을 냈다" 만 적으면, 그 0 이 판정 실패인지 정상 통과인지
# 구분되지 않는 hollow 오라클이 된다.
def _flips_to_red(discriminating_test):
    """지정한 반사실 테스트가 지금 상태에서 RED 가 되는가."""
    try:
        discriminating_test()
    except AssertionError:
        return True
    return False


def test_mutant_section_id_extraction_weakened_is_killed(monkeypatch):
    """(a) 절 ID 추출 무력화 — `A<n>-<m>` 갈래 제거 → 반사실 RED 테스트가 RED."""
    monkeypatch.setattr(sut, "_SECTION_ID_RE", re.compile(r"§결정\s*\d+(?:\.\d+)?"))
    diff, images = load_fixture(RED_SHA)
    assert sut.evaluate(diff, images)["violations"] == []
    assert _flips_to_red(test_counterfactual_amendment4_authoring_is_red), \
        "mutant 이 살아남았다 — 절 ID 추출이 판정에 실리지 않는다는 뜻"


def test_mutant_section_id_extraction_disabled_is_killed(monkeypatch):
    """(a2) 절 ID 추출 전면 무력화 → 반사실 RED 테스트가 RED."""
    monkeypatch.setattr(sut, "_SECTION_ID_RE", re.compile(r"(?!x)x"))
    diff, images = load_fixture(RED_SHA)
    assert sut.evaluate(diff, images)["violations"] == []
    assert _flips_to_red(test_counterfactual_amendment4_authoring_is_red)


def test_mutant_cochange_always_true_is_killed(monkeypatch):
    """(b) 무편집 판정을 언제나 '편집됨' 으로 완화 → 반사실 RED 테스트가 RED."""
    monkeypatch.setattr(sut, "section_is_cochanged", lambda span, added, deleted: True)
    diff, images = load_fixture(RED_SHA)
    assert sut.evaluate(diff, images)["violations"] == []
    assert _flips_to_red(test_counterfactual_amendment4_authoring_is_red)


def test_mutant_direction_guard_removed_is_killed(monkeypatch):
    """(c) 방향 가드 제거 → 봉합 커밋이 거짓 RED 가 되어 GREEN 테스트가 RED.

    전방 참조가 곧 정정 포인터이므로, 방향 가드는 통과 경로를 지탱하는 요소다."""
    monkeypatch.setattr(sut, "is_preceding", lambda target, citing: True)
    diff, images = load_fixture(GREEN_SHA)
    mutant = sut.evaluate(diff, images)
    assert set(violated_ids(mutant)) >= {"A4-2", "A4-3", "A5-3"}, violated_ids(mutant)
    assert _flips_to_red(test_counterfactual_pointer_repair_is_green)


def test_mutant_amendment_scope_dropped_is_killed(monkeypatch):
    """(d) 인용 정의역 울타리(Amendment 범위) 제거 → 대조군 테스트가 RED."""
    monkeypatch.setattr(sut, "in_any_span", lambda lineno, spans: True)
    assert _flips_to_red(test_control_citation_outside_amendment_scope_is_out_of_domain)


def test_mutant_blank_line_credit_is_killed(monkeypatch):
    """(e) 공백 줄을 편집 증거로 세는 완화 → 공백 줄 테스트가 RED."""
    monkeypatch.setattr(
        sut, "section_is_cochanged",
        lambda span, added, deleted: True if added or deleted else False)
    assert _flips_to_red(test_blank_added_line_is_not_cochange_evidence)


def test_mutants_are_not_vacuous():
    """대조군 — mutant 를 걸지 않은 상태에서는 위 반사실 테스트가 모두 통과한다.

    이것이 없으면 `_flips_to_red` 가 mutant 때문에 RED 인지, 원래부터 RED 인지
    구분되지 않는다(무조건-true 오라클 차단). [ceiling: '무조건-true' 는 이 대조군이 막는 실패 양태의 이름이며 주장이 아니다 — mention]"""
    assert not _flips_to_red(test_counterfactual_amendment4_authoring_is_red)
    assert not _flips_to_red(test_counterfactual_pointer_repair_is_green)
    assert not _flips_to_red(test_control_citation_outside_amendment_scope_is_out_of_domain)
    assert not _flips_to_red(test_blank_added_line_is_not_cochange_evidence)


# ═══════════════════════ 선례 재사용 결박 (drift 차단) ═══════════════════════════
@pytest.mark.parametrize("sha", [RED_SHA, GREEN_SHA])
def test_walk_added_lines_match_ratchet_parser(sha):
    """본 모듈의 walk 가 내는 추가 줄이 ADR-177 선례 파서와 동일한지 대조.

    삭제 위치까지 필요해 walk 를 따로 걷지만, 추가 줄 축에서 선례와 갈라지면
    두 게이트가 서로 다른 diff 를 보게 된다."""
    diff, _ = load_fixture(sha)
    mine, _deleted, _touched = sut.walk_diff(diff)
    theirs = parse_added_lines(diff)
    assert [(a.path, a.lineno, a.text) for a in mine] == \
           [(a.path, a.lineno, a.text) for a in theirs]


def test_walk_added_lines_match_ratchet_parser_on_synthetic_context_diff():
    """문맥·삭제 줄이 섞인 diff 에서도 선례와 일치."""
    _post, diff = build([
        ("ctx", "머리말"), ("del", "지운 줄"), ("add", "새 줄"), ("ctx", "꼬리말"),
        ("add", "+++ 로 시작하는 내용 줄"), ("add", "--- 로 시작하는 내용 줄"),
    ])
    mine, _d, _t = sut.walk_diff(diff)
    theirs = parse_added_lines(diff)
    assert [(a.path, a.lineno, a.text) for a in mine] == \
           [(a.path, a.lineno, a.text) for a in theirs]
    assert [a.text for a in mine][-2:] == ["+++ 로 시작하는 내용 줄", "--- 로 시작하는 내용 줄"]


def _load_extract_adr_section():
    """구현리뷰 iter5 가 정정한 쪽 helper 를 파일 경로로 적재."""
    p = REPO_ROOT / "tests" / "integration" / "test_scheduled_task_ac_matrix.py"
    spec = importlib.util.spec_from_file_location("_ac_matrix_for_reuse_check", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.extract_adr_section


def test_two_section_helpers_agree_on_adr172():
    """절 슬라이싱 선례 2종이 같은 결과를 내는지 — 본 게이트는 그 규칙을 재사용한다.

    `impl_manifest.extract_section` (본 게이트가 import) 과
    `test_scheduled_task_ac_matrix.extract_adr_section` (iter5 F-CR5-02 정정본)이
    갈라지면, 본 게이트가 재사용한다고 적은 근거가 무너진다."""
    extract_section = sut._load_extract_section()
    extract_adr_section = _load_extract_adr_section()
    text = (REPO_ROOT / ADR172).read_text(encoding="utf-8")
    headings = [h for h in sut.build_heading_index(text) if h.sec_id]
    assert len(headings) >= 20, "ADR-172 절 표본이 너무 적다 — 대조 근거 부족"
    for h in headings:
        assert extract_section(text, h.raw) == extract_adr_section(text, h.raw), h.raw[:60]


def test_section_span_terminates_at_higher_level_heading():
    """h2 흡수 금지 — `###` 절이 뒤따르는 `##` 절을 삼키지 않는다 (iter5 결함 회귀)."""
    text = "\n".join([
        "# 문서", "", "### A1-9 — 마지막 소절", "", "본문.", "",
        "## 결과", "", "결과 본문.", ""]) + "\n"
    heads = sut.build_heading_index(text)
    target = next(h for h in heads if h.sec_id == "A1-9")
    start, end = sut.section_span(text, target)
    assert (start, end) == (3, 7), (start, end)


# ═══════════════════════ silent-skip 차단 ═══════════════════════════════════════
def test_unresolvable_base_ref_returns_none():
    """base ref 미해소는 빈 diff(통과)가 아니라 `None`(미판정)이다."""
    assert sut.diff_text_from_git(str(REPO_ROOT), "refs/heads/__no_such_ref__") is None
    assert sut.run_git(str(REPO_ROOT), "refs/heads/__no_such_ref__") is None


def test_main_exits_base_unresolved_on_missing_base(capsys):
    """CLI 는 미판정을 종료코드 %d 로 드러낸다 — 조용한 0 이 아니다.""" % sut.EXIT_BASE_UNRESOLVED
    rc = sut.main(["--repo-root", str(REPO_ROOT), "--base-ref", "refs/heads/__no_such_ref__"])
    assert rc == sut.EXIT_BASE_UNRESOLVED
    assert "미판정" in capsys.readouterr().out


def test_missing_postimage_is_undecidable_not_pass():
    """post-image 를 못 읽으면 통과가 아니라 미판정으로 남는다."""
    _post, diff = synth(amendment_body=["§결정 1 을 뒤집는다."])
    result = sut.evaluate(diff, {})                      # 본문 미제공
    assert result["undecidable"], "본문 부재가 조용히 통과했다"
    assert result["violations"] == []


def test_exit_codes_are_distinct():
    assert len({sut.EXIT_OK, sut.EXIT_VIOLATION, sut.EXIT_BASE_UNRESOLVED}) == 3


# ═══════════════════════ 정직 천장 각인 (모듈 docstring ①②⑤⑦) ══════════════════
def test_ceiling1_any_edit_in_cited_section_passes():
    """천장 ① — co-change 는 pointer 가 아니다.

    피인용 절에 **정정과 무관한** 오탈자 수정 한 줄만 넣어도 통과한다. 검사기를
    "그 편집이 포인터인가" 까지 넓히면 이 테스트가 RED 가 되어 천장 갱신이 강제된다."""
    post, diff = synth(
        sec1_body=[("ctx", "첫 결정 본문."), ("add", "오탈자를 고쳤다. (포인터 아님)")],
        amendment_body=["§결정 1 의 결론을 뒤집는다."])
    result = run(post, diff)
    assert result["violations"] == []
    assert any(c.sec_id == "§결정 1" and c.disposition == "cochanged"
               for c in result["citations"])


def test_ceiling2_overturn_without_section_id_is_undetected():
    """천장 ② — 절 ID 없이 뒤집으면 미검출 (ADR-177 패러프레이즈 FN 과 동형·상속)."""
    post, diff = synth(amendment_body=[
        "위의 첫 결정은 사실 틀렸다. 그 표는 여기서 통째로 대체된다.",
    ])
    result = run(post, diff)
    assert result["violations"] == []
    assert result["citations"] == []


def test_ceiling5_amendment_level_reference_is_not_a_section_id():
    """천장 ⑤ — `Amd 2` · `Amendment 2` 는 절 ID 로 세지 않는다.

    실물 근거: `b41e69af9` 의 A5-3 서술이 A4-3 의 오지목 문구 *"Amd 2 본문"* 을
    따옴표로 **인용**한다 — 지목과 인용을 구분할 수단이 없어 정의역에서 뺐다."""
    ids = [i for i, foreign in sut.cited_ids("Amd 2 본문과 Amendment 3 을 적는다", 999)]
    assert ids == []
    diff, images = load_fixture(GREEN_SHA)
    text = images[ADR172]
    assert "Amd 2 본문" in text
    assert sut.evaluate(diff, images)["violations"] == []


def test_ceiling7_reference_only_citation_over_triggers():
    """천장 ⑦ — 참조만 해도 걸린다 (반대 방향 오발화, 실측 `§결정 4` 재현).

    Amendment 안에서 앞 절을 근거로 *인용*만 해도 co-change 를 요구한다. 이 구분은
    어휘·의미 판정을 요구하므로 하지 않는다 — 대신 위반 목록을 **후보 목록**으로
    읽어야 한다는 사실을 여기 각인한다."""
    post, diff = synth(amendment_body=[
        "이 정정은 §결정 1 의 「신규 플래그 0건」 정신을 그대로 따른다.",  # 뒤집기가 아님 [ceiling: 합성 fixture 문자열 리터럴 — 실측 §결정 4 오발화를 재현하려 ADR-172 어투를 모사한 mention]
    ])
    result = run(post, diff)
    assert violated_ids(result) == ["§결정 1"], "천장 ⑦ 이 해소됐다면 문서를 갱신하라"


# 행번호 앵커 표본 — 어느 것도 절 ID 문법(`A<n>-<m>` · `§결정 N`)의 문자열을 담지 않는다.
LINE_POINTERS = (
    "위 표의 근거는 `:289`-`:306` 과 `:416` 에 있다 — 그 전제를 뒤집는다.",
    "앞의 `:117` 이 세운 결론을 여기서 대체한다.",
    "정정 대상 = 이 파일 :412 · :585 두 줄.",
)


def test_ceiling8_line_number_pointer_is_outside_detection_domain():
    """★ 이 테스트는 **결함을 잡지 않는다 — 천장 ⑧ 을 각인한다.**

    정정 포인터를 행번호로 앵커하면 후속 커밋이 앞쪽에 문단을 넣을 때 좌표가 밀려
    썩는데, 이 검사는 그 좌표를 **읽지 못한다** — `_SEC_ID_ALT` 의 값 공간이
    `A<n>-<m>` · `§결정 N` 두 형태뿐이라 `:NNN` 이 아예 들어 있지 않다.

    각인을 공허하지 않게 하는 두 장치:
      · **선확인** — 표본이 절 ID 문법에 0 match 임을 먼저 assert 한다. 표본이 우연히
        절 ID 를 담고 있었다면 아래 「위반 0」은 천장이 아니라 그냥 오류였을 것이다.
      · **대조군** — 같은 뒤집기를 *절 ID* 로 앵커하면 위반으로 잡힌다. 대조군이 없으면
        「위반 0」이 천장 때문인지 합성 케이스가 애초에 무해해서인지 구분되지 않는다.

    ⇒ 누군가 검사기를 좌표 축으로 넓히면 이 테스트가 **RED** 가 된다. 그때 할 일은 이
      테스트를 지우는 게 아니라 모듈 docstring 의 천장 ⑧ 을 함께 갱신하는 것이다.
      각인은 검출이 아니라 **넓힐 때 알려주는 장치**다."""
    # ① 선확인 — 표본 어느 줄도 절 ID 문법에 걸리지 않는다.
    assert len(LINE_POINTERS) >= 2
    for p in LINE_POINTERS:
        assert sut._SECTION_ID_RE.findall(p) == [], \
            "행번호 표본이 절 ID 문법에 걸리면 이 각인은 무의미하다: %r" % p
        assert sut.cited_ids(p, own_adr=999) == [], p

    # ② 대조군 — 같은 뒤집기를 절 ID 로 앵커하면 검사기가 잡는다.
    ctl_post, ctl_diff = synth(amendment_body=["§결정 1 의 결론을 뒤집는다."])
    assert violated_ids(run(ctl_post, ctl_diff)) == ["§결정 1"], \
        "대조군이 안 잡히면 아래 「위반 0」은 천장의 증거가 아니다"

    # ③ 각인 — 좌표가 **지금은 정확해도** 검사기 눈에 보이지 않는다.
    #    포인터 `:N` 은 합성 문서에서 실제 `§결정 1` 헤딩 줄을 가리키도록 계산한다
    #    (저작 시점엔 옳았던 실물 좌표의 재현).
    probe_post, _ = synth(amendment_body=list(LINE_POINTERS))
    sec1_lineno = next(i for i, l in enumerate(probe_post.splitlines(), start=1)
                       if l.startswith("### §결정 1"))
    post, diff = synth(amendment_body=list(LINE_POINTERS)
                       + ["앞 절(`:%d`)의 결론을 뒤집는다." % sec1_lineno])
    assert post.splitlines()[sec1_lineno - 1].startswith("### §결정 1"), \
        "포인터가 실제 §결정 1 헤딩을 가리키지 않으면 실물 재현이 아니다"
    result = run(post, diff)
    assert result["citations"] == [], sut.format_report(result)
    assert result["violations"] == []


def test_ceiling_domain_excludes_cross_repo_paths():
    """천장 ③ — Change Plan · Story 는 다른 repo 소재라 이 축이 도달하지 않는다."""
    assert sut.DEFAULT_PREFIXES == ("archive/adr/",)
    post, diff = synth(amendment_body=["§결정 1 을 뒤집는다."])
    other = "docs/stories/CFP-999.md"
    result = sut.evaluate(diff.replace(SYNTH_PATH, other), {other: post})
    assert result["violations"] == []


def test_report_enumerates_cochange_passes():
    """무증상 GREEN 금지 — ④로 통과한 건을 리포트가 드러낸다 (천장 ① 가시화)."""
    diff, images = load_fixture(GREEN_SHA)
    report = "\n".join(sut.format_report(sut.evaluate(diff, images)))
    assert "cochanged" in report
    assert "판정하지 않는다" in report
