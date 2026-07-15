# -*- coding: utf-8 -*-
"""authoring_self_gate.py 검증 — Epic #2686 Story C(CFP-2689) Phase 2 self-gate self-test.

QADev **단독 저작** (독립 oracle). DeveloperAgent 가 landed 한 `scripts/lib/authoring_self_gate.py`
를 **import 해 검증**하되, 기대값(oracle)은 DeveloperAgent 스크립트를 mirror 하지 않고
**사전-고정 독립 fixture + 하드코딩 기대 verdict** 로 작성한다.

설계 SSOT (firsthand Read):
  - Story CFP-2689 §5.3 AC-1~18 + §8.1.1 RTM + §8.6 born-GREEN 2축.
  - Change Plan 2026-07-16-cfp-2689 §8.1.1 RTM(authoritative) + §8.6.
  - ADR-158 (author-time self-gate forcing function) 결정 1~9 (in-repo, Phase-1 doc-assertion anchor).

born-GREEN 2축 (ADR-158 결정 5 / Story §8.6 — 반드시 준수):
  (a) 독립 oracle — self-gate 자기 계산 출력 self-match 금지. 사전-고정 known-good/known-bad
      fixture 를 QADev 가 직접 구성하고 기대 verdict 를 하드코딩(CFP-2673 X⊆X tautology 회피).
      본 파일의 기대값(VALID_LANE_LABELS / CLOSED_7_FAMILIES / "PASS"/"FAIL")은 계약 SSOT 에서
      직접 유래한 하드코딩 상수이며 module under test 에서 import 하지 않는다.
  (b) 대칭 fail-closed — known-good→GREEN ∧ known-bad→RED 양방향(present-null 비대칭 금지,
      CFP-2680). known-good 이 실제로 PASS 함도 assert(한쪽만 검증 금지).

Windows/CI 안전: fixture write = newline="\n"(CRLF 금지). tmp override(tmp_path) — 실 ledger 무오염.
실행: python -m pytest tests/unit/test_authoring_self_gate.py -v
"""

import json
import os
import subprocess
import sys

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# module under test import (sys.path 에 scripts/lib 삽입 — RTM Hop3 ast-resolvable 대비)
# ─────────────────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))  # tests/unit → tests → repo root
_LIB = os.path.join(_REPO_ROOT, "scripts", "lib")
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)

import authoring_self_gate as asg  # noqa: E402
from authoring_self_gate import (  # noqa: E402
    run_authoring_self_gate,
    SelfGateResult,
    Defect,
    gate_ac_traceability,
    gate_rtm_format_signature,
    gate_doc_section_schema,
    gate_doc_frontmatter_schema,
)
from emit_dev_process_event import emit_defect_finding  # noqa: E402  (A emit port — 소비만)
from aggregate_dev_process_event import compute_selfref_recurrence  # noqa: E402  (B 하류 consumer)

# ADR-158 (in-repo, 항상 checkout 됨 — Phase-1 doc-assertion anchor)
ADR158 = os.path.join(_REPO_ROOT, "archive", "adr",
                      "ADR-158-author-time-self-gate-forcing-function.md")
INVENTORY = os.path.join(_REPO_ROOT, "docs", "selftest-execution-liveness-inventory.yaml")
CLAUDE_MD = os.path.join(_REPO_ROOT, "CLAUDE.md")

# cross-repo (internal-docs) — presence-guarded(로컬 present / CI ubuntu absent → guard)
_INTERNAL = os.path.normpath(os.path.join(_REPO_ROOT, "..", "..",
                                          "codeforge-internal-docs", "cfp-2689-p2"))
CHANGE_PLAN = os.path.join(_INTERNAL, "wrapper", "change-plans",
                           "2026-07-16-cfp-2689-authoring-self-gate.md")
STORY = os.path.join(_INTERNAL, "wrapper", "stories", "CFP-2689.md")

# A/B substrate 파일 basenames (§4.1 MUST NOT touch — AC-6). 이 파일들 0 수정이 계약.
AB_SUBSTRATE_BASENAMES = frozenset({
    "append_dev_process_event.py", "query_dev_process_event.py",
    "emit_dev_process_event.py", "dev_process_blob_store.py",
    "redact_dev_process_content.py", "aggregate_dev_process_event.py",  # B aggregator
    "dev-process-event-v1.md",  # A 계약
})

# 7-tuple branch-protection required contexts (CLAUDE.md SSOT — AC-6/16 무변경 확인, 독립 하드코딩)
SEVEN_TUPLE_CONTEXTS = (
    "phase-gate-mergeable", "invariant-check",
    "doc frontmatter schema (CFP-28 — strict)", "doc section schema (CFP-28 — strict)",
    "check-gate", "Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)",
    "ac-traceability-matrix",
)

# ═════════════════════════════════════════════════════════════════════════════
# 독립 oracle 상수 (사전-고정 — 계약 SSOT 유래, module under test 에서 import 금지)
#   VALID_LANE_LABELS = dev-process-event-v1 label-registry-v2 (11값). detecting_lane 유효 멤버 판정.
#   CLOSED_7_FAMILIES = append_dev_process_event _DEFECT_FAMILIES(CLOSED-7). 새 family 발명 부재 판정.
# ═════════════════════════════════════════════════════════════════════════════
VALID_LANE_LABELS = frozenset({
    "요구사항", "요구사항-리뷰", "설계", "설계-리뷰", "구현", "구현-리뷰",
    "구현-테스트", "보안-테스트", "배포", "배포-리뷰", "없음",
})
CLOSED_7_FAMILIES = frozenset({
    "correctness", "security", "performance", "design-boundary",
    "test-gap", "doc-integrity", "process-discipline",
})

# ═════════════════════════════════════════════════════════════════════════════
# 사전-고정 독립 fixture 내용 (QADev 직접 구성 — DeveloperAgent embedded fixture 를 mirror 하지 않음:
#   story_key/AC-ID/test 심볼명/statement 전부 독립. known-good ∧ known-bad 쌍.)
# ═════════════════════════════════════════════════════════════════════════════
FX_GOOD_AC_SOURCE = """---
story_key: CFP-9001
---
# QADev Independent Fixture Story
## 5. 요구사항 확장 해석
### 5.3 Acceptance Criteria
| id | statement | source | tier |
|---|---|---|---|
| AC-1 | 시스템은 유효한 입력을 정상 경로로 수용한다 | user | normative |
"""

# known-good RTM: normative AC-1 → 명명 테스트 매핑(백틱). phase-1 PASS, phase-2 = symbol 실재 시 PASS.
FX_GOOD_RTM = """# QADev Independent Fixture Change Plan
## §8. Test Contract
### §8.1.1 RTM
| AC | tier | 명명 테스트 |
|---|---|---|
| AC-1 | normative | `test_qadev_indep_present` |
"""

# known-bad: normative AC-1 이 RTM 에 미매핑(row 누락) → ac-traceability Hop2 RED.
FX_BAD_RTM_MISSING_ROW = """# QADev Independent Fixture Change Plan
## §8. Test Contract
### §8.1.1 RTM
| AC | tier | 명명 테스트 |
|---|---|---|
| AC-2 | normative | `test_qadev_other` |
"""

# known-bad: §8 자체 부재 → rtm-format-signature RED(위치 미해결).
FX_BAD_RTM_NO_SECTION = """# QADev Independent Fixture Change Plan
## §7. 보안
내용.
"""

# known-bad(§4 위치 오배치 / AC header 손상): §5 에 산문 AC-1 선언 있으나 parseable 표 부재
#   → ac-traceability UNDECIDABLE RED(anti-degradation).
FX_BAD_AC_CORRUPT_HEADER = """---
story_key: CFP-9001
---
# QADev Fixture Story
## 5. 요구사항 확장 해석
### 5.3 Acceptance Criteria
AC-1 은 유효 입력을 수용해야 한다(표 없이 산문만 — header 손상).
"""

# Phase-2-only-detectable RTM: AC-1 → born-missing 심볼(tests-root 에 없으면 Phase-2 Hop3 RED,
#   Phase-1 은 Hop3 skip → PASS). AC-7 discriminating fixture.
FX_RTM_HOP3 = """# QADev Independent Fixture Change Plan
## §8. Test Contract
### §8.1.1 RTM
| AC | tier | 명명 테스트 |
|---|---|---|
| AC-1 | normative | `test_qadev_born_missing_sym` |
"""

FX_GOOD_ADR = """---
adr_number: 9001
title: QADev Fixture ADR
status: Active
category: orchestration-discipline
date: 2026-07-16
---
# ADR-9001 — QADev Fixture
## 상태
Active.
## 컨텍스트
context.
## 결정
decision.
## 결과
result.
## 관련 파일
files.
"""

# known-bad: `## 결정` 섹션 부재 → doc-section-schema RED(§4 위치/필수 섹션 위반 동형).
FX_BAD_ADR_MISSING_SECTION = """---
adr_number: 9001
title: QADev Fixture ADR
status: Active
category: orchestration-discipline
date: 2026-07-16
---
# ADR-9001 — QADev Fixture
## 상태
Active.
## 컨텍스트
context.
## 결과
result.
## 관련 파일
files.
"""

# known-bad: category invalid(closed_enum 밖) → doc-frontmatter-schema RED.
FX_BAD_ADR_INVALID_CATEGORY = """---
adr_number: 9001
title: QADev Fixture ADR
status: Active
category: nonexistent-qadev-category-zzz
date: 2026-07-16
---
# ADR-9001 — QADev Fixture
## 상태
Active.
## 컨텍스트
context.
## 결정
decision.
## 결과
result.
## 관련 파일
files.
"""


# ─────────────────────────────────────────────────────────────────────────────
# helper (test_ 접두 금지 — RTM Hop3 은 test_ac* 18심볼만 매핑)
# ─────────────────────────────────────────────────────────────────────────────
def _w(path, content):
    """fixture write — newline='\\n'(CRLF 금지, Windows/CI lint false-FAIL 회피)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    return path


def _adr_under_owner(tmp_path, name, content):
    """ADR fixture 를 owner-prefix(archive/adr) 하위에 배치 → doc 게이트 per-artifact 매칭."""
    return _w(os.path.join(str(tmp_path), "archive", "adr", name), content)


def _tests_root_with(tmp_path, subdir, symbol=None):
    """tests-root 디렉터리 생성. symbol 지정 시 그 심볼 정의 .py, 아니면 무관 심볼만."""
    d = os.path.join(str(tmp_path), subdir)
    os.makedirs(d, exist_ok=True)
    body = "def %s():\n    pass\n" % symbol if symbol else "def test_placeholder_only():\n    pass\n"
    _w(os.path.join(d, "some_test.py"), body)
    return d


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _git(repo_root, *args):
    try:
        p = subprocess.run(["git", "-C", repo_root, *args],
                           capture_output=True, text=True, timeout=60)
        return p.returncode, p.stdout
    except Exception:
        return None, ""


def _changed_files(repo_root):
    """base(merge-base origin/main) 대비 변경(tracked, 커밋+워킹트리) 파일 경로 set + base."""
    rc, base = _git(repo_root, "merge-base", "HEAD", "origin/main")
    base = base.strip() if rc == 0 and base.strip() else None
    if base is None:
        for ref in ("origin/main", "main"):
            rc2, o = _git(repo_root, "rev-parse", ref)
            if rc2 == 0 and o.strip():
                base = ref
                break
    changed = set()
    if base:
        for args in (("diff", "--name-only", base), ("diff", "--name-only", base, "HEAD")):
            rc3, o = _git(repo_root, *args)
            if rc3 == 0:
                changed |= {ln.strip() for ln in o.splitlines() if ln.strip()}
    return changed, base


# =============================================================================
# Phase 1 — 정의·경계·대상 doc-assertion (anchor = ADR-158 in-repo, 항상 checkout)
# =============================================================================
def test_ac1_scope_shift_left_not_aggregate():
    """AC-1(normative,P1): scope = C 예방/self-적용/shift-left, A(substrate)·B(집계) 배제 doc-assertion."""
    adr = _read(ADR158)
    # shift-left / 저작시점 self-적용 (C 정체)
    assert "저작시점" in adr, "ADR-158 에 저작시점(shift-left) scope 서술 부재"
    assert "shift-left" in adr, "ADR-158 에 shift-left 명시 부재"
    assert ("자기 산출물" in adr or "self-적용" in adr), "ADR-158 에 self-적용(자기 산출물) scope 부재"
    # A(substrate 재구축) 배제 + B(집계/aggregator) 배제 경계 — C ⊥ A ∧ C ⊥ B
    assert "소비만" in adr, "A substrate 소비만(재구축 배제) 경계 서술 부재"
    assert ("aggregator" in adr or "집계" in adr), "B 집계 배제(producer⊥aggregator) 경계 서술 부재"
    assert ("producer" in adr and ("⊥ B" in adr or "C ⊥ B" in adr or "B=aggregator" in adr)), \
        "C=결점 producer ⊥ B=aggregator disjoint 경계 부재"


def test_ac2_target_gate_set_and_runnable_classification():
    """AC-2(normative,P1): 대상 게이트 집합 열거 + runnable-now/deferred-to-CI 정직 분류 서술."""
    adr = _read(ADR158)
    for gate in ("ac-traceability-matrix", "doc-section-schema", "doc-frontmatter-schema"):
        assert gate in adr, "ADR-158 결정1 대상 게이트 집합에 %s 미열거" % gate
    assert ("RTM format" in adr or "RTM 표 header" in adr or "header signature" in adr), \
        "RTM format header signature 게이트 미열거"
    assert "runnable-now" in adr and "deferred-to-CI" in adr, \
        "runnable-now / deferred-to-CI 정직 분류 서술 부재"
    # module 구조: GATE_RUNNABILITY 가 대상 4 게이트를 runnable-now 로 분류
    gr = asg.GATE_RUNNABILITY
    for gate in ("ac-traceability-matrix", "doc-section-schema",
                 "doc-frontmatter-schema", "rtm-format-signature"):
        assert gr.get(gate) == "runnable-now", "GATE_RUNNABILITY[%s] != runnable-now" % gate
    assert "deferred-to-CI" in gr.values(), "GATE_RUNNABILITY 에 deferred-to-CI 정직 카테고리 부재"


def test_ac3_trigger_point_and_enforcement_tier():
    """AC-3(normative,P1): 발동 시점(저작 완료 직후·리뷰 前) + advisory tier + fail-open + 실게이트 invoke 강제."""
    adr = _read(ADR158)
    assert ("리뷰 lane 진입 전" in adr or "리뷰 lane 진입 **전**" in adr
            or "저작 완료 직후" in adr), "발동 시점(저작 완료 직후·리뷰 前) 서술 부재"
    assert "advisory" in adr, "advisory 강제 tier 서술 부재"
    assert "fail-open" in adr, "fail-open 정직 서술 부재"
    # 리뷰 판정이 실 게이트 실행을 대체 금지(A/B miss 실패모드) + 실 로직 invoke
    assert "invoke" in adr, "실 게이트 invoke 강제 서술 부재"
    assert ("대체 금지" in adr or "대체" in adr), "리뷰 판정 실게이트 대체 금지 서술 부재"


def test_ac4_detecting_lane_honest_degrade_no_invalid_enum(tmp_path):
    """AC-4(normative,P1): honest-degrade 서술 + Phase-2 emit detecting_lane ∈ 유효 enum('authoring-self-gate' 부재)."""
    # part 1 — doc-assertion (ADR-158 결정 4)
    adr = _read(ADR158)
    assert "honest-degrade" in adr, "detecting_lane honest-degrade 서술 부재"
    assert "authoring-self-gate" in adr, "비-멤버 문자열 경계 서술(authoring-self-gate) 부재"
    assert "emit 하지 않는다" in adr, "invalid enum(authoring-self-gate) emit 금지 서술 부재"

    # part 2 — Phase-2 emit: 실행해 emit 될 detecting_lane 이 유효 enum 멤버 확인(독립 oracle=VALID_LANE_LABELS)
    res = run_authoring_self_gate(
        [_adr_under_owner(tmp_path, "ADR-9001-bad.md", FX_BAD_ADR_MISSING_SECTION)],
        ac_source=_w(os.path.join(str(tmp_path), "ac.md"), FX_GOOD_AC_SOURCE),
        rtm=_w(os.path.join(str(tmp_path), "rtm.md"), FX_BAD_RTM_MISSING_ROW),
        phase=2, emit=False,
    )
    assert res.failed, "known-bad 입력인데 결점 0 (born-hollow 위험)"
    for d in res.failed:
        assert d.detecting_lane in VALID_LANE_LABELS, \
            "detecting_lane=%r 이 유효 lane_label enum 밖" % d.detecting_lane
        assert d.detecting_lane != "authoring-self-gate", \
            "비-멤버 문자열 'authoring-self-gate' 를 detecting_lane 으로 emit(신호 소실)"
    # round-trip: 실 append 가 valid enum 을 null 로 coerce 하지 않음(=진짜 enum 멤버) 확증
    d = res.failed[0]
    ledger = os.path.join(str(tmp_path), "ac4_ledger.jsonl")
    eid = emit_defect_finding(
        "CFP-9001", d.detecting_lane, defect_id=d.defect_id, defect_family=d.defect_family,
        defect_type=d.defect_type, detecting_lane=d.detecting_lane,
        time_to_detection=d.time_to_detection, content="ac4", consumer_scope="wrapper",
        ledger_path=ledger, blob_root=os.path.join(str(tmp_path), "ac4_blob"),
    )
    assert eid, "wrapper always-on emit 미기록(round-trip 불가)"
    row = json.loads(_read(ledger).splitlines()[0])
    assert row["detecting_lane"] is not None, \
        "append 가 detecting_lane 을 null coerce — 유효 enum 멤버 아님(신호 소실)"
    assert row["detecting_lane"] == d.detecting_lane and row["detecting_lane"] in VALID_LANE_LABELS


def test_ac5_disjoint_boundary_2684_2322_5th():
    """AC-5(normative,P1): 경계(#2684 ADR-154 / #2322 / 5th boundary) cross-ref 확인."""
    adr = _read(ADR158)
    assert "ADR-154" in adr, "#2684(ADR-154) cross-ref 부재"
    assert ("#2684" in adr or "2684" in adr), "#2684 boundary 참조 부재"
    assert ("#2322" in adr or "2322" in adr or "provenance" in adr), "#2322(gate provenance) 경계 부재"
    assert "5th boundary" in adr, "5th boundary 경계 서술 부재"
    assert ("review-verdict-v4" in adr and "재기록" in adr), \
        "self-gate PASS/FAIL ≠ review-verdict-v4 payload 재기록 명시 부재"


def test_ac6_ab_substrate_zero_edit_and_7tuple_unchanged():
    """AC-6(normative,P1): git diff A/B 파일 empty + 7-tuple 무변경(git 실측 + CLAUDE.md SSOT)."""
    # doc-assertion — ADR-158 결정 3: A/B 0개 수정 + emit port 소비만
    adr = _read(ADR158)
    assert "0개 수정" in adr, "A/B substrate 0개 수정 서술 부재"
    assert "소비만" in adr, "emit port 소비만 서술 부재"

    # 7-tuple 무변경 — CLAUDE.md branch-protection SSOT
    cm = _read(CLAUDE_MD)
    for ctx in SEVEN_TUPLE_CONTEXTS:
        assert ('"%s"' % ctx) in cm, "7-tuple required context %r 부재(변조?)" % ctx
    assert '"authoring-self-gate"' not in cm, \
        "신규 required context 'authoring-self-gate' 추가됨(7-tuple 무변경 위반)"

    # git 실측 — A/B substrate 파일 0 수정(available 시). 미가용 → doc/7-tuple 로 여전히 유효.
    changed, base = _changed_files(_REPO_ROOT)
    if base is not None:
        touched_ab = {c for c in changed
                      if os.path.basename(c.replace("\\", "/")) in AB_SUBSTRATE_BASENAMES}
        assert not touched_ab, "A/B substrate 파일 수정 검출(계약 위반): %s" % sorted(touched_ab)


def test_ac17_runnable_vs_ci_defer_classification(tmp_path):
    """AC-17(normative,P1): runnable/defer 분류 + silent-covered 주장 부재(capability boundary 정직)."""
    adr = _read(ADR158)
    assert "runnable-now" in adr and "deferred-to-CI" in adr, "runnable/defer 분류 부재"
    assert "silent" in adr, "silent-covered 주장 금지(capability boundary 정직) 서술 부재"
    # 실행-backed: phase=2 & tests_root 부재 → Hop3 를 silent-covered 하지 않고 skipped_ci_defer 로 정직 공개
    res = run_authoring_self_gate(
        [], ac_source=_w(os.path.join(str(tmp_path), "ac.md"), FX_GOOD_AC_SOURCE),
        rtm=_w(os.path.join(str(tmp_path), "rtm.md"), FX_RTM_HOP3),
        phase=2, tests_root=None, emit=False,
    )
    assert res.skipped_ci_defer, "phase=2 tests_root 부재인데 defer 미공개(silent-covered 위험)"
    assert any(d.get("hop") == "Hop3" or "Hop3" in str(d.get("reason", ""))
               for d in res.skipped_ci_defer), "Hop3 deferred-to-CI 정직 공개 부재"


# =============================================================================
# Phase 2 — 실행·emit·self-test·dogfood (fixture replay / self-test, 독립 oracle)
# =============================================================================
def test_ac7_real_gate_invoke_phase2_mode(tmp_path):
    """AC-7(normative,P2): Phase-2-only-detectable fixture(RTM Hop3 born-missing) → 실 게이트 invoke 검출.

    독립 oracle(하드코딩 기대): {phase1:PASS, phase2_missing:FAIL, phase2_present:PASS}.
    Phase-1 은 Hop3 skip 하여 born-missing 을 놓치고, Phase-2 모드만 검출한다(A/B miss = Phase-2 미실행).
    """
    ac = _w(os.path.join(str(tmp_path), "ac.md"), FX_GOOD_AC_SOURCE)
    rtm = _w(os.path.join(str(tmp_path), "rtm_hop3.md"), FX_RTM_HOP3)
    tr_missing = _tests_root_with(tmp_path, "tr_missing", symbol=None)  # born-missing 심볼 부재
    tr_present = _tests_root_with(tmp_path, "tr_present", symbol="test_qadev_born_missing_sym")

    v_phase1, _ = gate_ac_traceability(ac, rtm, phase=1)
    v_phase2_missing, _ = gate_ac_traceability(ac, rtm, phase=2, tests_root=tr_missing)
    v_phase2_present, _ = gate_ac_traceability(ac, rtm, phase=2, tests_root=tr_present)

    assert v_phase1 == "PASS", "Phase-1 이 Hop3 born-missing 을 잘못 검출(기대 PASS=Hop3 skip)"
    assert v_phase2_missing == "FAIL", "Phase-2 모드가 RTM Hop3 born-missing 을 미검출(A/B miss 재범)"
    assert v_phase2_present == "PASS", "symbol 실재인데 Phase-2 FAIL(RED→GREEN discriminating 실패)"


def test_ac8_negative_control_known_bad_red_green(tmp_path):
    """AC-8(normative,P2): known-bad(RTM row 누락/§4 위치 오배치/AC header 손상/invalid category) → RED, fix → GREEN.

    독립 oracle + 대칭 fail-closed: 각 결점류가 known-bad→RED ∧ known-good→GREEN 양방향 discriminating.
    """
    ac_good = _w(os.path.join(str(tmp_path), "ac_good.md"), FX_GOOD_AC_SOURCE)
    ac_corrupt = _w(os.path.join(str(tmp_path), "ac_corrupt.md"), FX_BAD_AC_CORRUPT_HEADER)
    rtm_good = _w(os.path.join(str(tmp_path), "rtm_good.md"), FX_GOOD_RTM)
    rtm_missing = _w(os.path.join(str(tmp_path), "rtm_missing.md"), FX_BAD_RTM_MISSING_ROW)

    # (1) RTM row 누락 → Hop2 RED / 매핑 채우면 GREEN
    assert gate_ac_traceability(ac_good, rtm_missing, phase=1)[0] == "FAIL", "RTM row 누락 미검출"
    assert gate_ac_traceability(ac_good, rtm_good, phase=1)[0] == "PASS", "known-good RTM 이 GREEN 아님"

    # (2) AC 표 header 손상(산문 선언 + 표 부재) → UNDECIDABLE RED / 정상 표면 GREEN
    assert gate_ac_traceability(ac_corrupt, rtm_good, phase=1)[0] == "FAIL", "AC header 손상 미검출"
    assert gate_ac_traceability(ac_good, rtm_good, phase=1)[0] == "PASS", "정상 AC 표면이 GREEN 아님"

    # (3) §4 위치 오배치 동형(ADR 필수 섹션 누락) → doc-section RED / 정상 ADR GREEN
    bad_adr = _adr_under_owner(tmp_path, "ADR-9001-missing.md", FX_BAD_ADR_MISSING_SECTION)
    good_adr = _adr_under_owner(tmp_path, "ADR-9001-good.md", FX_GOOD_ADR)
    assert gate_doc_section_schema(bad_adr)[0] == "FAIL", "ADR 필수 섹션 누락(§4 위치 위반 동형) 미검출"
    assert gate_doc_section_schema(good_adr)[0] == "PASS", "정상 ADR doc-section 이 GREEN 아님"

    # (4) invalid category → doc-frontmatter RED / 정상 category GREEN (pyyaml 필요 — 부재 시 skip)
    if _yaml_here():
        bad_cat = _adr_under_owner(tmp_path, "ADR-9001-badcat.md", FX_BAD_ADR_INVALID_CATEGORY)
        v_bad = gate_doc_frontmatter_schema(bad_cat)[0]
        # confluence-ia-tree.yaml 실재 시에만 category closed_enum 검사 → RED. 부재 시 PASS(정직 skip).
        if os.path.isfile(os.path.join(_REPO_ROOT, "docs", "confluence-ia-tree.yaml")):
            assert v_bad == "FAIL", "invalid category(closed_enum 밖) 미검출"
        assert gate_doc_frontmatter_schema(good_adr)[0] == "PASS", "정상 category frontmatter 가 GREEN 아님"


def test_ac9_emit_shape_b_aggregator_compatible(tmp_path):
    """AC-9(normative,P2): emit shape {family,type,ttd,detecting_lane}+defect_id → B compute_selfref_recurrence round-trip 소비."""
    res = run_authoring_self_gate(
        [], ac_source=_w(os.path.join(str(tmp_path), "ac.md"), FX_GOOD_AC_SOURCE),
        rtm=_w(os.path.join(str(tmp_path), "rtm.md"), FX_BAD_RTM_MISSING_ROW),
        phase=1, emit=False,
    )
    assert res.failed, "known-bad(RTM row 누락)인데 결점 0"
    d = res.failed[0]
    # emit shape 4-tuple + defect_id 채워짐
    assert d.defect_family in CLOSED_7_FAMILIES
    assert isinstance(d.defect_type, str) and d.defect_type
    assert isinstance(d.time_to_detection, int)
    assert d.detecting_lane in VALID_LANE_LABELS
    assert isinstance(d.defect_id, str) and len(d.defect_id) == 64

    # 실 emit port 로 동일 defect_id 2회 write(tmp ledger override — 실 ledger 무오염) → B 소비
    ledger = os.path.join(str(tmp_path), "ledger.jsonl")
    blob = os.path.join(str(tmp_path), "blob")
    for _ in range(2):
        eid = emit_defect_finding(
            "CFP-9001", d.detecting_lane, defect_id=d.defect_id, defect_family=d.defect_family,
            defect_type=d.defect_type, detecting_lane=d.detecting_lane,
            time_to_detection=d.time_to_detection, content="rt", consumer_scope="wrapper",
            ledger_path=ledger, blob_root=blob,
        )
        assert eid and len(eid) == 64, "wrapper emit 미기록"
    rows = [json.loads(ln) for ln in _read(ledger).splitlines() if ln.strip()]
    assert len(rows) == 2 and all(r["event_type"] == "defect_finding" for r in rows)
    r0 = rows[0]
    assert r0["defect_family"] == d.defect_family and r0["defect_family"] in CLOSED_7_FAMILIES
    assert r0["detecting_lane"] == d.detecting_lane  # append 가 valid enum preserve(null coerce 아님)
    assert len(r0["defect_id"]) == 64

    # B round-trip — compute_selfref_recurrence 가 4-tuple 로 소비(동일 defect_id 2회 → recurrence 1)
    out = compute_selfref_recurrence(rows, {})
    assert out["distinct_defect_ids"] == 1
    assert out["recurrence_count"] == 1, "B aggregator 가 emit 을 4-tuple 로 소비 못함(round-trip 실패)"
    key = "%s|%s|%s|%s" % (d.defect_family, d.defect_type, d.time_to_detection, d.detecting_lane)
    assert key in out["recurrence_profiles_4tuple"], "4-tuple profile 키 미생성(shape 불호환)"


def test_ac10_emit_failure_graceful_none(tmp_path, monkeypatch):
    """AC-10(normative,P2): emit 포트 예외 주입 → None, self-gate exit 정상(무차단). mock-seam 동반 assertion."""
    calls = {"n": 0}

    def _raising(*a, **k):
        calls["n"] += 1
        raise RuntimeError("injected emit port failure")

    # 실 ledger 무오염 보장(만약을 위해 CLAUDE_PROJECT_DIR → tmp) + 포트 예외 주입
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setattr(asg, "_emit_defect_finding", _raising)
    monkeypatch.setattr(asg, "_EMIT_PORT_AVAILABLE", True)

    res = run_authoring_self_gate(
        [_adr_under_owner(tmp_path, "ADR-9001-bad.md", FX_BAD_ADR_MISSING_SECTION)],
        ac_source=_w(os.path.join(str(tmp_path), "ac.md"), FX_GOOD_AC_SOURCE),
        rtm=_w(os.path.join(str(tmp_path), "rtm.md"), FX_BAD_RTM_MISSING_ROW),
        phase=1, emit=True, consumer_scope="wrapper",
    )
    # 동반 assertion — 예외 주입이 실제 발동했고(mock-seam 검증), graceful None 으로 흡수됨
    assert calls["n"] >= 1, "주입한 emit 포트가 호출되지 않음(mock-seam 미검증)"
    assert res.failed, "결점이 있어야 emit 시도됨(전제)"
    assert res.emit_attempted is True
    assert res.emitted and all(e is None for e in res.emitted), \
        "emit 포트 예외인데 event_id 가 None 이 아님(graceful None 위반)"
    assert len(res.emitted) == len(res.failed), "emitted↔failed 길이 불일치"
    # exit 정상(무차단) — 여기 도달 자체가 non-blocking 증명 + 실 ledger 미생성
    assert not os.path.isfile(os.path.join(str(tmp_path), ".claude", "ledger",
                                           "dev-process-event.jsonl"))


def test_ac11_inactive_alpha_run_but_emit_none(tmp_path, monkeypatch):
    """AC-11(normative,P2): inactive-α/포트 미가용 → 게이트 실행+보고 but emit=None, stats 로 측정≠emit 구분."""
    bad_adr = _adr_under_owner(tmp_path, "ADR-9001-bad.md", FX_BAD_ADR_MISSING_SECTION)
    ac = _w(os.path.join(str(tmp_path), "ac.md"), FX_GOOD_AC_SOURCE)
    rtm = _w(os.path.join(str(tmp_path), "rtm.md"), FX_BAD_RTM_MISSING_ROW)

    # (A) 포트 미가용 → _emit_one 이 즉시 None. 게이트는 실행+보고.
    monkeypatch.setattr(asg, "_EMIT_PORT_AVAILABLE", False)
    monkeypatch.setattr(asg, "_emit_defect_finding", None)
    res = run_authoring_self_gate([bad_adr], ac_source=ac, rtm=rtm, phase=1,
                                  emit=True, consumer_scope="wrapper")
    assert res.failed, "게이트가 결점 검출(실행+보고)해야 함"
    assert res.ran_gates, "self-gate 실행됨(ran_gates 비어있지 않음)"
    assert all(e is None for e in res.emitted), "포트 미가용인데 emit None 아님"
    st = res.stats()
    assert st["self_gate_ran"] is True, "측정(self_gate_ran) True 여야"
    assert st["emit_success_count"] == 0, "emit 성공 0 이어야(측정≠emit)"
    assert st["emit_none_count"] == len(res.emitted)
    assert "measurement_note" in st and "≠" in st["measurement_note"], "측정≠emit 구분 note 부재"

    # (B) inactive-α 실 포트 경로 — consumer default-false → 실 port 가 activation gate 로 None(무기록)
    monkeypatch.undo()
    monkeypatch.delenv("CODEFORGE_DEV_PROCESS_CAPTURE", raising=False)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    ledger = os.path.join(str(tmp_path), "inactive_ledger.jsonl")
    eid = emit_defect_finding("CFP-9001", "구현", defect_id="a" * 64, defect_family="doc-integrity",
                              defect_type="unknown-type", detecting_lane="구현", time_to_detection=0,
                              content="inactive", consumer_scope="consumer",
                              ledger_path=ledger, blob_root=os.path.join(str(tmp_path), "b"))
    assert eid is None, "consumer default-false(inactive-α)인데 emit 성공(activation gate 미작동)"
    assert not os.path.isfile(ledger), "inactive-α 인데 ledger write 발생(측정≠emit 위장)"


def test_ac12_dogfood_self_application_pass(tmp_path):
    """AC-12(normative,P2): C 자기 산출물(ADR-158[+Change Plan/Story]) self-gate 실행 → PASS(결점 0)."""
    assert os.path.isfile(ADR158), "ADR-158(in-repo dogfood anchor) 부재"
    # cross-repo(internal-docs) present 시 ac_source/rtm 포함, absent(CI)면 ADR-158 doc 게이트만.
    ac_source = STORY if os.path.isfile(STORY) else None
    rtm = CHANGE_PLAN if os.path.isfile(CHANGE_PLAN) else None
    res = run_authoring_self_gate([ADR158], ac_source=ac_source, rtm=rtm, phase=1, emit=False)
    assert res.ran_gates, "dogfood self-gate 가 아무 게이트도 실행 안 함(born-hollow)"
    assert res.failed == [], \
        "C 자기 산출물 self-gate 결점 검출(born-red dogfood): %s" % [
            (d.gate, d.summary[:120]) for d in res.failed]


def test_ac13_outcome_not_proxy_no_overclaim(tmp_path):
    """AC-13(normative,P2): outcome-vs-proxy + over-claim wording 부재(module/docstring)."""
    src = _read(os.path.join(_LIB, "authoring_self_gate.py"))
    # outcome ground-truth(proxy 아님) 정직 프레이밍 present
    assert "ground-truth" in src and "proxy 아님" in src, "outcome-vs-proxy(ADR-119 2 판정면) 프레이밍 부재"
    assert "honest-degrade" in src, "honest-degrade 천장 표기 부재"
    # over-claim positive wording 부재 grep (금지 어휘의 positive 형)
    for banned in ("완전히 방지", "완전 방지", "exact detection",
                   "정밀 detecting", "guaranteed-unique", "guaranteed unique"):
        assert banned not in src, "over-claim wording %r 가 module 에 존재" % banned
    # 실행 산출도 outcome 근거 stats(ceiling) 노출
    res = run_authoring_self_gate(
        [], ac_source=_w(os.path.join(str(tmp_path), "ac.md"), FX_GOOD_AC_SOURCE),
        rtm=_w(os.path.join(str(tmp_path), "rtm.md"), FX_GOOD_RTM), phase=1, emit=False,
    )
    st = res.stats()
    assert "ceiling" in st and "ground-truth" in st["ceiling"], "stats ceiling 에 outcome ground-truth 부재"


def test_ac14_selftest_independent_oracle_mutation_revert(tmp_path):
    """AC-14(normative,P2): 독립 oracle(사전-고정 하드코딩 기대 verdict) + mutation-revert(known-bad→RED ∧ known-good→GREEN 양방향).

    독립 oracle 증명 — 기대값은 gate 자기계산이 아니라 사전-고정 하드코딩("PASS"/"FAIL", self-match 아님).
    mutation-revert — good RTM → GREEN, 변형(AC-1 매핑 제거) → RED, 원복 → GREEN(byte-identical=diff empty 개념).
    """
    ac = _w(os.path.join(str(tmp_path), "ac.md"), FX_GOOD_AC_SOURCE)
    rtm = os.path.join(str(tmp_path), "rtm_mut.md")

    # known-good → GREEN (독립 하드코딩 기대 "PASS")
    _w(rtm, FX_GOOD_RTM)
    good_bytes = open(rtm, "rb").read()
    assert gate_ac_traceability(ac, rtm, phase=1)[0] == "PASS", "known-good 이 GREEN 아님(present-null 비대칭 금지)"

    # mutation(fixture) → RED (독립 하드코딩 기대 "FAIL") — production code 무변경
    _w(rtm, FX_BAD_RTM_MISSING_ROW)
    assert gate_ac_traceability(ac, rtm, phase=1)[0] == "FAIL", "mutation(AC-1 미매핑) 이 RED 아님(discriminating 실패)"

    # revert → GREEN + byte-identical(diff empty 개념)
    _w(rtm, FX_GOOD_RTM)
    assert open(rtm, "rb").read() == good_bytes, "revert 후 byte-identical 아님(diff empty 위반)"
    assert gate_ac_traceability(ac, rtm, phase=1)[0] == "PASS", "revert 후 GREEN 복원 실패"


def test_ac15_defect_family_closed7_no_invention(tmp_path):
    """AC-15(declared,P2): 검출 결점의 defect_family ∈ CLOSED-7, 새 family 발명 부재."""
    # 여러 게이트 family 커버 — doc-integrity(doc-section) + test-gap/doc-integrity(ac-traceability Hop2)
    res = run_authoring_self_gate(
        [_adr_under_owner(tmp_path, "ADR-9001-bad.md", FX_BAD_ADR_MISSING_SECTION)],
        ac_source=_w(os.path.join(str(tmp_path), "ac.md"), FX_GOOD_AC_SOURCE),
        rtm=_w(os.path.join(str(tmp_path), "rtm.md"), FX_BAD_RTM_MISSING_ROW),
        phase=1, emit=False,
    )
    assert len(res.failed) >= 2, "다중 게이트 결점(doc-section + ac-traceability) 기대"
    families = {d.defect_family for d in res.failed}
    assert families <= CLOSED_7_FAMILIES, \
        "CLOSED-7 밖 family 발명: %s" % (families - CLOSED_7_FAMILIES)
    assert "doc-integrity" in families, "구조/위치 conformance → doc-integrity 미분류"


def test_ac16_new_lint_nonrequired_inventory_enroll():
    """AC-16(declared,P2): 7-tuple 무변경 + inventory enroll(bijection +1, channel alive)."""
    # 7-tuple 무변경 — 신규 required context 0
    cm = _read(CLAUDE_MD)
    for ctx in SEVEN_TUPLE_CONTEXTS:
        assert ('"%s"' % ctx) in cm, "7-tuple context %r 부재" % ctx
    assert '"authoring-self-gate"' not in cm, "신규 required context 추가(7-tuple 무변경 위반)"
    # inventory enroll — C self-test channel alive
    assert os.path.isfile(INVENTORY), "selftest-execution-liveness-inventory.yaml 부재"
    inv = _read(INVENTORY)
    assert "test_authoring-self-gate.sh" in inv, "C self-test inventory enroll(self_test) 부재"
    assert "authoring-self-gate-test.yml" in inv, "C self-test execution_channel(channel alive) 부재"


def test_ac18_defect_id_best_effort_honesty(tmp_path):
    """AC-18(declared,P2): defect_id = sha256 형식 산출 + honesty note(무보장, guaranteed-unique 미주장)."""
    # 동일 경로/내용 2회 실행 → 결정성(content-addressed on normalized-location) 검증.
    ac = _w(os.path.join(str(tmp_path), "ac.md"), FX_GOOD_AC_SOURCE)
    rtm = _w(os.path.join(str(tmp_path), "rtm.md"), FX_BAD_RTM_MISSING_ROW)
    res = run_authoring_self_gate([], ac_source=ac, rtm=rtm, phase=1, emit=False)
    assert res.failed
    d = res.failed[0]
    # sha256 형식(64-hex lowercase)
    assert isinstance(d.defect_id, str) and len(d.defect_id) == 64
    assert all(c in "0123456789abcdef" for c in d.defect_id), "defect_id 가 sha256 hex 형식 아님"
    # 결정성(같은 입력 경로/내용 → 같은 id) — best-effort content-addressed
    res2 = run_authoring_self_gate([], ac_source=ac, rtm=rtm, phase=1, emit=False)
    assert res2.failed and res2.failed[0].defect_id == d.defect_id, "동일 입력 defect_id 비결정적"
    # honesty note — best-effort/무보장(guaranteed-unique 미주장)
    assert ("best-effort" in d.honesty_note or "무보장" in d.honesty_note), "defect_id honesty note 부재"
    src = _read(os.path.join(_LIB, "authoring_self_gate.py"))
    assert "무보장" in src, "module 에 identity 무보장(honest-ceiling) 표기 부재"


# ─────────────────────────────────────────────────────────────────────────────
def _yaml_here():
    try:
        import yaml  # noqa: F401
        return True
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
