#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_ac_pr_markers.py
CFP-2659 F1 (Epic CFP-2602 / ADR-145 Amendment 5) Phase 2 — PR-body **마커 파싱 pure 모듈**
(`scripts/lib/ac_pr_markers.py`) 의 born-hollow 봉인 self-test.

배경: 마커 추출이 workflow(github-script) 안 인라인 정규식에만 살아 있던 동안은 **구동 불가**(machine-unit
로 실행할 표면 자체가 없음) → `- **story_uri**: <url>` 같은 실측 장식 변이가 false-red 를 냈다. F1 은 그
파싱 로직을 pure leaf 로 추출하고, 본 파일이 그 층을 **실 import·실 구동**으로 봉인한다.

함수명은 Change Plan §8.1 RTM 과 **1:1 고정**(Hop3 ast resolve 대상 — rename/오타 시 게이트 FAIL).

정직 천장 (§8.4): 본 self-test 가 봉인하는 것은 **파서 로직 층**뿐이다. 어댑터(github-script) → 모듈
wiring(execFileSync 호출 + stdout 파싱) 은 integration 층 = human-gate/canary 소관 — machine-unit 으로
위조하지 않는다(ADR-119 검사연극 금지). AC-4 는 두 workflow 자산의 byte-mirror 만 기계 검증한다.

forged-green 금지: 각 테스트는 실 모듈(`parse_pr_body`)을 구동하고 실 값으로 assert (mock/파일-입력 우회
/`assert True` 금지).
"""
import os
import tempfile
import time

import pytest
import yaml  # AC-1 — self-test workflow 배선 present 구조 검증(pyyaml, requirements.txt)

from _ac_marker_mutations import iter_mutants, load_module  # 공통 mutation helper (ADR-140)
from _ac_matrix_fixtures import AC_TRACE_LIB, REPO_ROOT  # sys.path 에 scripts/lib 주입(import 부수효과)
from ac_pr_markers import parse_pr_body  # ★실 pure leaf (Dev F1) — 실 import·실 구동
from check_ac_traceability_matrix import (  # AC-9 §5 self-gate parseability (적용성 verdict SSOT)
    APPLIC_SURFACE_PRESENT,
    classify_ac_source,
)

AC_MARKERS_PY = os.environ.get("AC_MARKERS_PY", os.path.join(AC_TRACE_LIB, "ac_pr_markers.py"))

STORY_URL = "https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/stories/CFP-2659.md"
RTM_URL = "https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/change-plans/cfp-2659.md"

_PREAMBLE = "## 요약\n\nF1 marker-format fix — PR body 마커 장식 tolerance.\n\n"


def _body(*lines):
    """실제 PR body 형태(전후 산문 포함)로 감싸 line-start anchor 를 실전 조건에서 검증."""
    return _PREAMBLE + "\n".join(lines) + "\n\n(이하 본문 계속)\n"


# ─────────────────────────────────────────────────────────────────────────────
# AC-1 — story_uri / rtm_uri 장식 tolerance (line-start anchored, bounded)
# ─────────────────────────────────────────────────────────────────────────────
def test_marker_plain_recognized():
    d = parse_pr_body(_body(f"story_uri: {STORY_URL}"))
    assert d["story_uri"] == STORY_URL
    assert d["both_absent"] is False
    assert d["none_declared"] is False


def test_marker_key_bold_recognized():
    d = parse_pr_body(_body(f"**story_uri**: {STORY_URL}"))
    assert d["story_uri"] == STORY_URL, "키-bold 마커 미인식 (false-red 벡터)"
    assert d["both_absent"] is False


def test_marker_list_bold_recognized():
    # ★실측 실패 벡터 — `- **story_uri**: <url>` (list + 키-bold). 구 인라인 정규식이 여기서 false-red.
    for bullet in ("-", "*"):
        d = parse_pr_body(_body(f"{bullet} **story_uri**: {STORY_URL}"))
        assert d["story_uri"] == STORY_URL, f"list({bullet})+bold 마커 미인식 (실측 false-red 벡터)"
        assert d["both_absent"] is False
    # 장식 없는 list 도 동형
    d = parse_pr_body(_body(f"- story_uri: {STORY_URL}"))
    assert d["story_uri"] == STORY_URL


def test_marker_value_bold_clean_capture():
    # 값-bold: 캡처에 trailing `**` 가 혼입되면 하류 fetch 가 404 → 위장된 false-red.
    d = parse_pr_body(_body(f"**story_uri: {STORY_URL}**"))
    assert d["story_uri"] == STORY_URL, "값-bold 마커 미인식"
    assert not d["story_uri"].endswith("*"), f"dirty capture (trailing `*` 혼입): {d['story_uri']!r}"
    # list + 값-bold 조합도 clean
    d2 = parse_pr_body(_body(f"- **story_uri: {STORY_URL}**"))
    assert d2["story_uri"] == STORY_URL
    assert not d2["story_uri"].endswith("*")


def test_marker_whitespace_variants_recognized():
    variants = [
        f"   story_uri: {STORY_URL}",              # 키앞 공백
        f"story_uri:     {STORY_URL}",             # 콜론뒤 다중 공백
        f"\tstory_uri:\t{STORY_URL}",              # 탭
        f"story_uri: {STORY_URL}   ",              # 값 뒤 trailing 공백
        f"-   **story_uri**:   {STORY_URL}  ",     # list+bold+공백 복합
    ]
    for line in variants:
        d = parse_pr_body(_body(line))
        assert d["story_uri"] == STORY_URL, f"공백 변이 미인식: {line!r} → {d['story_uri']!r}"
        assert d["both_absent"] is False


def test_rtm_uri_decoration_isomorphic():
    # rtm_uri 는 story_uri 와 **동형** tolerance 여야 한다 (한쪽만 고치면 false-red 잔존).
    d = parse_pr_body(_body(f"- **story_uri**: {STORY_URL}", f"- **rtm_uri**: {RTM_URL}"))
    assert d["rtm_uri"] == RTM_URL, "list+bold rtm_uri 미인식 (동형 위반)"
    assert d["story_uri"] == STORY_URL

    d2 = parse_pr_body(_body(f"**rtm_uri: {RTM_URL}**"))
    assert d2["rtm_uri"] == RTM_URL
    assert not d2["rtm_uri"].endswith("*"), f"rtm_uri dirty capture: {d2['rtm_uri']!r}"

    # rtm_uri 부재 = RTM not-yet EXPLICIT 신호 (None 이어야 — 빈 문자열 위장 금지)
    d3 = parse_pr_body(_body(f"story_uri: {STORY_URL}"))
    assert d3["rtm_uri"] is None


# ─────────────────────────────────────────────────────────────────────────────
# AC-2 — ac_applicability: none 선언 (장식 tolerance + 사유 캡처 + 값 판별)
# ─────────────────────────────────────────────────────────────────────────────
def test_none_marker_decorated_recognized():
    d = parse_pr_body(_body("- **ac_applicability**: none — marketplace sync"))
    assert d["none_declared"] is True, "list+bold none 마커 미인식"
    assert d["story_uri"] is None
    assert d["both_absent"] is False, "none 선언은 both_absent 를 해제해야 한다"

    # 값 판별 보존 — `none` 만 정의역. skip / n/a 는 none 아님(무단 확장 금지).
    for bogus in ("skip", "n/a", "N/A", "not-applicable"):
        b = parse_pr_body(_body(f"ac_applicability: {bogus}"))
        assert b["none_declared"] is False, f"'{bogus}' 를 none 으로 오인식 (값 판별 붕괴)"
        assert b["both_absent"] is True, f"'{bogus}' 는 유효 선언 아님 → both_absent 유지(fail-closed)"


def test_none_reason_captured():
    d = parse_pr_body(_body("ac_applicability: none — marketplace sync PR (추적 AC 없음)"))
    assert d["none_declared"] is True
    assert "marketplace sync" in d["none_reason"], f"사유 미캡처: {d['none_reason']!r}"

    # 값-bold 시 trailing `**` 미혼입 (사유 캡처도 clean)
    d2 = parse_pr_body(_body("- **ac_applicability: none — sibling parity sync**"))
    assert d2["none_declared"] is True
    assert d2["none_reason"].strip(), "값-bold none 사유 미캡처"
    assert not d2["none_reason"].rstrip().endswith("*"), f"none_reason dirty capture: {d2['none_reason']!r}"


def test_none_four_combination_regression():
    """ADR-145 §결정9 none 4-조합을 **추출면**에서 회귀 봉인.

    ★verdict(PASS/FAIL) 는 core(check_ac_traceability_matrix) 단일 소유 — 본 모듈은 기계적 추출 사실만
    보고한다. 따라서 여기서는 추출 필드만 assert 하고 PASS/FAIL 을 단정하지 않는다(both_absent ≠ verdict).
    """
    # ① none + 무사유 → none_declared True ∧ none_reason "" (core 가 AC-2 reason-guard 로 FAIL 판정할 입력)
    d1 = parse_pr_body(_body("ac_applicability: none"))
    assert d1["none_declared"] is True
    assert d1["none_reason"] == "", f"무사유인데 reason 이 채워짐: {d1['none_reason']!r}"

    # ② none + story_uri 병존(위장) → 둘 다 추출 ∧ both_absent False (precedence 는 core arbitrate)
    d2 = parse_pr_body(_body(f"- **story_uri**: {STORY_URL}", "- **ac_applicability**: none — 위장"))
    assert d2["story_uri"] == STORY_URL
    assert d2["none_declared"] is True
    assert d2["both_absent"] is False

    # ③ 둘 다 부재 → both_absent True (core distinct default guard 로 fail-closed)
    d3 = parse_pr_body(_body("마커 없는 평범한 본문입니다."))
    assert d3["story_uri"] is None
    assert d3["none_declared"] is False
    assert d3["both_absent"] is True

    # ④ none + 사유(정상 비적용) → none_declared True ∧ reason 비어있지 않음
    d4 = parse_pr_body(_body("ac_applicability: none — Epic close PR (추적 AC 없음)"))
    assert d4["none_declared"] is True
    assert d4["none_reason"].strip() != ""
    assert d4["both_absent"] is False


# ─────────────────────────────────────────────────────────────────────────────
# AC-3 — fail-closed 보존 + mutation-kill (born-hollow 봉인)
# ─────────────────────────────────────────────────────────────────────────────
def test_both_absent_fail_closed():
    d = parse_pr_body("## 요약\n\n마커가 전혀 없는 PR body.\n\n- 변경: 문서 오탈자\n")
    assert d["story_uri"] is None
    assert d["none_declared"] is False
    assert d["rtm_uri"] is None
    assert d["both_absent"] is True, "마커 0개인데 both_absent False = fail-closed 붕괴"


def test_mutation_g_decor_reverts_false_red():
    """G-DECOR: 장식 tolerance 무력화 → `- **story_uri**:` 가 미인식(RED)으로 뒤집혀야 kill.

    변조 미적용(diff 0) 또는 로드 가능 변조본 0 → INCONCLUSIVE → 명시적 fail (born-broken 방지).
    원본 GREEN ∧ 변조 RED 대조로 vacuous 아님을 같은 테스트 안에서 입증.
    """
    decorated = _body(f"- **story_uri**: {STORY_URL}")
    plain = _body(f"story_uri: {STORY_URL}")

    orig = load_module(AC_MARKERS_PY, "_orig_decor")
    assert orig.parse_pr_body(decorated)["story_uri"] == STORY_URL, "원본이 장식 마커 미인식 (GREEN 대조 실패)"

    with tempfile.TemporaryDirectory() as td:
        mutants = list(iter_mutants("decor", td, AC_MARKERS_PY))
        if not mutants:
            pytest.fail(
                "INCONCLUSIVE: G-DECOR 변조 미적용(diff 0 또는 broken mutant only) — "
                f"_ac_marker_mutations.CANDIDATES['decor'] 를 실 구현({AC_MARKERS_PY}) 에 재배선 필요"
            )
        killed = []
        for desc, path, mod in mutants:
            got = mod.parse_pr_body(decorated)["story_uri"]
            if got is None:  # 장식 tolerance 사라짐 = RED 로 뒤집힘
                # 타겟성 확인: plain 마커는 여전히 인식 (모듈 통째 파손이 아님)
                assert mod.parse_pr_body(plain)["story_uri"] == STORY_URL, (
                    f"변조본이 plain 마커까지 파손 — 타겟 변조 아님 ({desc})"
                )
                killed.append((desc, path))
        assert killed, (
            "G-DECOR mutant 미-kill: 장식 tolerance 를 제거해도 `- **story_uri**:` 가 여전히 인식됨 "
            "→ 인식이 tolerance 로직에 기인하지 않음(hollow 의심). "
            f"시도한 변조: {[m[0] for m in mutants]}"
        )


def test_mutation_g_cleancap_dirty_uri():
    """G-CLEANCAP: trailing `*` strip(clean capture) 무력화 → `**story_uri: url**` 캡처가 dirty 로 뒤집혀야 kill."""
    valbold = _body(f"**story_uri: {STORY_URL}**")

    orig = load_module(AC_MARKERS_PY, "_orig_cleancap")
    orig_uri = orig.parse_pr_body(valbold)["story_uri"]
    assert orig_uri == STORY_URL and not orig_uri.endswith("*"), f"원본 clean capture 실패: {orig_uri!r}"

    with tempfile.TemporaryDirectory() as td:
        mutants = list(iter_mutants("cleancap", td, AC_MARKERS_PY))
        if not mutants:
            pytest.fail(
                "INCONCLUSIVE: G-CLEANCAP 변조 미적용(diff 0 또는 broken mutant only) — "
                f"_ac_marker_mutations.CANDIDATES['cleancap'] 를 실 구현({AC_MARKERS_PY}) 에 재배선 필요"
            )
        killed = []
        for desc, path, mod in mutants:
            got = mod.parse_pr_body(valbold)["story_uri"]
            if got is None or got != STORY_URL:  # dirty(`url**`) 또는 미인식 = 뒤집힘
                killed.append((desc, path, got))
        assert killed, (
            "G-CLEANCAP mutant 미-kill: clean-capture 로직을 무력화해도 캡처가 여전히 clean "
            f"→ strip 이 결과에 기여하지 않음(hollow 의심). 시도한 변조: {[m[0] for m in mutants]}"
        )
        # dirty 로 뒤집힌 케이스가 1개 이상 (trailing `*` 혼입 실증)
        assert any(g is not None and g.endswith("*") for _d, _p, g in killed), (
            f"kill 은 됐으나 trailing `*` dirty 혼입 실증 없음 — 관측값: {[g for _d, _p, g in killed]}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC-4 — adapter 자산 mirror (wrapper self ↔ consumer template)
# ─────────────────────────────────────────────────────────────────────────────
def test_adapter_mirror_byte_identical():
    live = os.path.join(REPO_ROOT, ".github", "workflows", "ac-traceability-matrix.yml")
    tmpl = os.path.join(REPO_ROOT, "templates", "github-workflows", "ac-traceability-matrix.yml")
    assert os.path.isfile(live), f"live workflow 부재: {live}"
    assert os.path.isfile(tmpl), f"template mirror 부재: {tmpl}"
    with open(live, "rb") as fh:
        live_b = fh.read()
    with open(tmpl, "rb") as fh:
        tmpl_b = fh.read()
    assert live_b == tmpl_b, (
        "wrapper self(.github/workflows) ↔ consumer template(templates/github-workflows) byte-drift — "
        f"live={len(live_b)}B template={len(tmpl_b)}B (F1 fix 가 한쪽에만 착륙)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC-8 — legit PR 3부류 오차단(false-red) 없음
# ─────────────────────────────────────────────────────────────────────────────
def test_legit_pr_classes_not_false_red():
    # ① 비적용 PR (marketplace sync 류)
    d1 = parse_pr_body(_body("- **ac_applicability**: none — marketplace sync (추적 AC 없음)"))
    assert d1["none_declared"] is True and d1["both_absent"] is False
    assert d1["none_reason"].strip() != ""

    # ② applicable §5 PR (story_uri + rtm_uri 병기)
    d2 = parse_pr_body(_body(f"- **story_uri**: {STORY_URL}", f"- **rtm_uri**: {RTM_URL}"))
    assert d2["story_uri"] == STORY_URL and d2["rtm_uri"] == RTM_URL
    assert d2["both_absent"] is False

    # ③ marker-format 장식(값-bold) PR
    d3 = parse_pr_body(_body(f"**story_uri: {STORY_URL}**", f"**rtm_uri: {RTM_URL}**"))
    assert d3["story_uri"] == STORY_URL and not d3["story_uri"].endswith("*")
    assert d3["rtm_uri"] == RTM_URL and not d3["rtm_uri"].endswith("*")
    assert d3["both_absent"] is False


# ─────────────────────────────────────────────────────────────────────────────
# AC-9 — 본 Story 자신의 §5 가 게이트-parseable (self-gate dogfood)
# ─────────────────────────────────────────────────────────────────────────────
def test_section5_self_gate_parseable():
    """Story §5 표준 7-컬럼 표(`| id | statement | source | verification | coverage_required | phase | tier |`)
    가 게이트 core `classify_ac_source` 로 SURFACE_PRESENT 로 분류됨을 실 구동 확인 (§5 self-gate)."""
    section5 = (
        "## §5. Acceptance Criteria\n\n"
        "| id | statement | source | verification | coverage_required | phase | tier |\n"
        "|---|---|---|---|---|---|---|\n"
        "| AC-1 | Given `- **story_uri**: <url>` When 게이트 실행 Then 인식된다 | user | unit test |"
        " [design, §8_test] | 2 | normative |\n"
        "| AC-2 | Given none 마커 장식 When 파싱 Then none_declared | derived | unit test |"
        " [design, §8_test] | 2 | normative |\n"
    )
    verdict, records, note = classify_ac_source(section5)
    assert verdict == APPLIC_SURFACE_PRESENT, f"§5 게이트-parseable 아님 (verdict={verdict}, note={note})"
    assert len(records) == 2, f"AC 레코드 추출 실패: {records}"
    assert {r["id"] for r in records} == {"AC-1", "AC-2"}
    assert all(r["tier"] == "normative" for r in records)


# ─────────────────────────────────────────────────────────────────────────────
# AC-11 — malformed / prose / ReDoS (tolerance 확장이 false-green 을 열지 않음)
# ─────────────────────────────────────────────────────────────────────────────
def test_unbalanced_token_malformed_not_pass():
    # `story_uri**:` — 값 없는 unbalanced 토큰. 인식되면 안 되고(값 부재), both_absent 로 fail-closed.
    d = parse_pr_body(_body("story_uri**:"))
    assert d["story_uri"] is None, f"unbalanced 토큰을 마커로 오인식: {d['story_uri']!r}"
    assert d["both_absent"] is True, "malformed 마커가 both_absent 를 해제 = false-green 개방"

    # 값 없는 plain 도 동일
    d2 = parse_pr_body(_body("story_uri:"))
    assert d2["story_uri"] is None
    assert d2["both_absent"] is True

    # 장식만 남고 값 없는 변이
    d3 = parse_pr_body(_body("- **story_uri**:", "**rtm_uri**:"))
    assert d3["story_uri"] is None and d3["rtm_uri"] is None
    assert d3["both_absent"] is True


def test_prose_mention_not_matched():
    # line-start anchor — 산문 중간 언급은 마커 아님. (깨지면 false-green 악화)
    d = parse_pr_body(_body(f"여기서 story_uri: {STORY_URL} 필드가 필요합니다"))
    assert d["story_uri"] is None, f"산문 언급을 마커로 오인식: {d['story_uri']!r}"
    assert d["both_absent"] is True

    d2 = parse_pr_body(_body("이 PR 은 rtm_uri: 를 안 씁니다"))
    assert d2["rtm_uri"] is None, f"산문 rtm_uri 언급 오인식: {d2['rtm_uri']!r}"

    d3 = parse_pr_body(_body("설명: ac_applicability: none 이라는 마커를 쓰면 된다는 안내 문장"))
    assert d3["none_declared"] is False, "산문 안 none 언급을 선언으로 오인식 (false 비적용 = 게이트 우회)"

    # ── list-prefixed 산문 (F1 이 list 장식을 tolerant 하게 만들며 새로 생긴 인접 위험면) ──
    # 불변 명제: list-marker(`-`/`*`)와 bold(`**`)는 strip 하되, **strip 후 마커 키가 라인 선두일 때만**
    #   인식한다. strip 후 선두가 산문이면 미매치 — list-marker 를 벗겨낸 뒤 `.*` 를 허용하면(느슨한 anchor)
    #   list 안 산문이 false-green 으로 샌다. 아래 assert 가 그 회귀를 고정한다.
    d4 = parse_pr_body(_body(f"- 여기서 story_uri: {STORY_URL} 필드가 필요합니다"))
    assert d4["story_uri"] is None, f"list 안 산문을 마커로 오인식: {d4['story_uri']!r}"
    assert d4["both_absent"] is True

    d5 = parse_pr_body(_body(f"* 이 항목은 rtm_uri: {RTM_URL} 를 설명합니다"))
    assert d5["rtm_uri"] is None, f"list 안 산문 rtm_uri 오인식: {d5['rtm_uri']!r}"

    # list + bold 장식 + 산문 = 가장 헷갈리는 형태 (bold strip 후에도 선두가 산문 `주의:`)
    d6 = parse_pr_body(_body(f"- **주의**: story_uri: {STORY_URL} 는 예시입니다"))
    assert d6["story_uri"] is None, f"list+bold 산문을 마커로 오인식: {d6['story_uri']!r}"
    assert d6["both_absent"] is True

    d7 = parse_pr_body(_body("- 설명: ac_applicability: none 이라는 안내"))
    assert d7["none_declared"] is False, "list 안 none 언급을 선언으로 오인식 (게이트 우회)"

    # 대조군(타겟성) — 같은 list 문맥이라도 키가 선두면 정상 인식 (guard 가 list 전체를 죽이지 않음)
    d8 = parse_pr_body(_body(f"- story_uri: {STORY_URL}"))
    assert d8["story_uri"] == STORY_URL, "list 선두 마커까지 미인식 = 과잉 차단(false-red 재발)"


@pytest.mark.timeout(10)
def test_redos_bounded_timing():
    """adversarial `*` 폭주 입력에 대해 유한시간 완료 — catastrophic backtracking 부재 실측."""
    adversarial = [
        "*" * 10000 + "story_uri:",
        ("- " + "*" * 2000 + "story_uri\n") * 50,
        "- " + "*" * 5000 + ": " + "x" * 100,
        "\n".join(["- " + "*" * 500 + "story_uri**: " + STORY_URL for _ in range(200)]),
        "\n".join(["*" * 300 + "ac_applicability" + "*" * 300 + ": none" for _ in range(200)]),
        ("**" * 5000) + "story_uri: " + STORY_URL + ("**" * 5000),
        # C2 양방향 strip 경로 자극 — value-only-bold `*` 폭주(캡처 앞뒤 asterisk flood, 방향당 bounded strip).
        "story_uri: " + "*" * 10000 + "x" * 100 + "*" * 10000,
    ]
    for i, body in enumerate(adversarial):
        t0 = time.perf_counter()
        d = parse_pr_body(body)
        elapsed = time.perf_counter() - t0
        assert isinstance(d, dict) and "both_absent" in d, f"adversarial[{i}] 반환 계약 위반: {d!r}"
        assert elapsed < 1.0, f"adversarial[{i}] 파싱 {elapsed:.3f}s — ReDoS 의심(bounded 아님)"


# ═════════════════════════════════════════════════════════════════════════════
# CFP-2671 — value-only-bold 양방향 strip (`_strip_bold_decor` leading+trailing 대칭, C2)
#   함수명 = Change Plan §8.1 RTM 과 1:1 고정 (Hop3 ast resolve — rename/오타 시 게이트 FAIL).
# ═════════════════════════════════════════════════════════════════════════════
def test_self_test_workflow_wires_pr_markers():
    """AC-1 — self-test workflow 가 `test_ac_pr_markers.py` 를 day-1 hard-fail 스텝으로 배선.

    본 pytest 는 **배선 present 의 구조적 앵커**다: self-test workflow YAML 안에 이 파일을 실행하는
    스텝이 실재하고, 그 스텝(및 선행 스텝)에 `continue-on-error` 가 없어 실패가 곧 job red 로 전파됨을
    검증한다.

    정직 천장 (ADR-119 검사연극 금지): total de-wiring(워크플로에서 스텝/파일 자체가 삭제되는 경우)은 이
    구조 테스트가 **자기 탐지하지 못하는 bootstrap 한계**다 — YAML 부재/키 부재 시엔 assert 가 실패하나,
    "실제 CI 에서 N passed 로 green 이 났는가"라는 런타임 liveness 는 CI 로그 관측이 유일한 ground-truth 다.
    본 테스트는 그 관측을 대체하지 않는다 (구조 present ≠ 런타임 green).
    """
    wf = os.path.join(REPO_ROOT, ".github", "workflows", "ac-traceability-self-test.yml")
    assert os.path.isfile(wf), f"self-test workflow 부재: {wf}"
    with open(wf, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    # `test_ac_pr_markers.py` 를 실행하는 스텝을 담은 job 의 steps 리스트 + 스텝 index 를 찾는다.
    target_steps = None
    target_idx = None
    for job in (data.get("jobs") or {}).values():
        steps = job.get("steps") or []
        for i, s in enumerate(steps):
            if "test_ac_pr_markers.py" in (s.get("run") or ""):
                target_steps, target_idx = steps, i
                break
        if target_steps is not None:
            break

    assert target_steps is not None, (
        "self-test workflow 에 test_ac_pr_markers.py 실행 스텝 부재 (de-wiring)"
    )
    # day-1 hard-fail: 타겟 스텝 + 모든 선행 스텝에 continue-on-error 부재(실패가 job red 로 전파돼야 함).
    for s in target_steps[: target_idx + 1]:
        assert not s.get("continue-on-error"), (
            f"continue-on-error 스텝 존재 → self-test 실패가 job red 로 전파 안 됨: {s.get('name')!r}"
        )


def test_marker_value_only_bold_clean_capture():
    """AC-2 — value-only-bold(`story_uri: **url**`) 캡처가 양방향 strip 후 clean(leading·trailing 모두).

    C2 이전엔 trailing 만 strip 해 `**url**` → 캡처 `**url**` → `**url` 로 dirty-leading 이 샜다.
    """
    for line in (f"story_uri: **{STORY_URL}**", f"- story_uri: **{STORY_URL}**"):  # 값-bold / list+값-bold
        d = parse_pr_body(_body(line))
        assert d["story_uri"] == STORY_URL, f"value-only-bold 미-clean: {line!r} → {d['story_uri']!r}"
        assert not d["story_uri"].endswith("*"), f"dirty trailing: {d['story_uri']!r}"
        assert not d["story_uri"].startswith("*"), f"dirty leading: {d['story_uri']!r}"

    # 대조군 비회귀 — whole-marker-bold / plain 도 여전히 clean (양방향 strip 이 기존 경로 무회귀)
    dw = parse_pr_body(_body(f"**story_uri: {STORY_URL}**"))
    assert dw["story_uri"] == STORY_URL and not dw["story_uri"].endswith("*")
    dp = parse_pr_body(_body(f"story_uri: {STORY_URL}"))
    assert dp["story_uri"] == STORY_URL


def test_rtm_uri_value_only_bold_isomorphic():
    """AC-2 — rtm_uri value-only-bold 가 story_uri 와 **동형** clean (한쪽만 고치면 false-red 잔존)."""
    d = parse_pr_body(_body(f"rtm_uri: **{RTM_URL}**"))
    assert d["rtm_uri"] == RTM_URL, f"rtm_uri value-only-bold 미-clean: {d['rtm_uri']!r}"
    assert not d["rtm_uri"].endswith("*") and not d["rtm_uri"].startswith("*"), f"rtm_uri dirty: {d['rtm_uri']!r}"

    # story_uri value-only-bold 와 rtm_uri value-only-bold 병기 → 둘 다 clean(동형 확인)
    d2 = parse_pr_body(_body(f"story_uri: **{STORY_URL}**", f"rtm_uri: **{RTM_URL}**"))
    assert d2["story_uri"] == STORY_URL
    assert not d2["story_uri"].startswith("*") and not d2["story_uri"].endswith("*")
    assert d2["rtm_uri"] == RTM_URL
    assert not d2["rtm_uri"].startswith("*") and not d2["rtm_uri"].endswith("*")


def test_mutation_g_leadstrip_dirty_uri():
    """G-LEADSTRIP: leading `*` strip(양방향 clean capture 의 leading 절반) 무력화 →
    value-only-bold(`story_uri: **url**`) 캡처가 dirty-leading(`**url`)으로 뒤집혀야 kill.

    격리(타겟성): 동일 mutant 하에서 whole-marker-bold(`**story_uri: url**`, 캡처 `url**` = trailing-only)
      대조군은 **여전히 clean** — leading mutation 이 trailing 경로에 무영향임을 같은 테스트 안에서 입증.
    변조 미적용(diff 0)/로드 가능 변조본 0 → INCONCLUSIVE → 명시적 fail (born-broken 방지,
      test_mutation_g_cleancap_dirty_uri 패턴 답습).
    """
    value_only = _body(f"story_uri: **{STORY_URL}**")   # 캡처 `**url**` — leading+trailing 혼입
    whole_bold = _body(f"**story_uri: {STORY_URL}**")    # 캡처 `url**` — trailing-only(격리 대조)

    orig = load_module(AC_MARKERS_PY, "_orig_leadstrip")
    assert orig.parse_pr_body(value_only)["story_uri"] == STORY_URL, "원본 value-only-bold clean 실패 (GREEN 대조)"

    with tempfile.TemporaryDirectory() as td:
        mutants = list(iter_mutants("leadstrip", td, AC_MARKERS_PY))
        if not mutants:
            pytest.fail(
                "INCONCLUSIVE: G-LEADSTRIP 변조 미적용(diff 0 또는 broken mutant only) — "
                f"_ac_marker_mutations.CANDIDATES['leadstrip'] 를 실 구현({AC_MARKERS_PY}) 에 재배선 필요"
            )
        killed = []
        for desc, path, mod in mutants:
            got = mod.parse_pr_body(value_only)["story_uri"]
            if got is not None and got != STORY_URL and got.startswith("*"):  # dirty-leading 으로 뒤집힘
                # 격리 확인: trailing-only 대조군은 여전히 clean (leading mutation 이 trailing 무영향)
                assert mod.parse_pr_body(whole_bold)["story_uri"] == STORY_URL, (
                    f"변조본이 whole-marker-bold(trailing 경로)까지 파손 — 타겟 변조 아님 ({desc})"
                )
                killed.append((desc, path, got))
        assert killed, (
            "G-LEADSTRIP mutant 미-kill: leading strip 을 무력화해도 value-only-bold 캡처가 여전히 clean "
            f"→ leading strip 이 결과에 기여하지 않음(hollow 의심). 시도한 변조: {[m[0] for m in mutants]}"
        )


def test_value_only_decoration_empty_fail_closed():
    """AC-4 — 양방향 strip 이 빈값/과잉장식을 clean URI 로 흘려 false-green 을 열지 않음(fail-closed).

    ① 값 없는 장식-only(`story_uri: **`) → strip 후 빈 문자열 → None → both_absent(fail-closed).
    ② bounded=2 상한 초과 장식(`***url***`) → 상한 초과분 잔존 → clean URI 아님(`*url*`) → 하류 fetch fail-closed.
    """
    # ① 장식-only, 값 부재 → None ∧ both_absent
    d1 = parse_pr_body(_body("story_uri: **"))
    assert d1["story_uri"] is None, f"빈-값 장식이 URI 로 샘: {d1['story_uri']!r}"
    assert d1["both_absent"] is True, "장식-only(값 없음)인데 both_absent 미설정 = fail-closed 붕괴"

    # ② 3+ asterisk — bounded=2 상한 초과분 잔존 → clean URL 아님(하류 fail-closed, false-green 미개방)
    d2 = parse_pr_body(_body(f"story_uri: ***{STORY_URL}***"))
    assert d2["story_uri"] != STORY_URL, f"과잉장식이 clean URL 로 통과 = false-green 개방: {d2['story_uri']!r}"
    assert "*" in d2["story_uri"], f"상한 초과 asterisk 미잔존(예상 `*url*`): {d2['story_uri']!r}"
