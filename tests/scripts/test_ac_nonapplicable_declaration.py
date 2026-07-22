#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_ac_nonapplicable_declaration.py
CFP-2634 Phase 2 (ADR-145 §결정9 — story_uri-absent ac-traceability applicability non-applicable
선언 경로) 의 **명명 테스트**(RTM authoritative — Change Plan cfp-2634 §8.1). 본 Story 자체가
dogfood: §8.1 이 명명한 normative 테스트(AC-1a/1b/1c/2/3/4/5/6/7/8/9/12)가 여기서 **실 def**(stub
아님)로 실재해야 게이트의 자기 Phase 2 PR 이 Hop3(§8↔실 symbol, ast resolve)를 통과한다. 함수명은
§8.1 과 1:1 정합(변경 금지).

AC-10/AC-11(advisory)는 명명 테스트 없음 — forged machine test 금지(§5.6 RO-1 / advisory routed,
CFP-2609 계승).

pytest 로 실행 가능(requirements.txt: pytest). 각 함수는 실제로 core/CLI 를 구동(assert_gate_*) 하거나
workflow/CLAUDE.md/audit-doc 실 파일을 검증(진짜 GREEN). subprocess fork 판정은 exit code 단독 아닌
도메인 sentinel 병행(assert_gate_fail — distinct-marker).

production 코드(scripts/lib/check_ac_traceability_matrix.py, .github/workflows/**)는 DeveloperAgent
가 병렬 착륙시킨다 — 본 QADev 가 작성한 시점에 미착륙 항목(story-init.yml story_uri emit,
branch-protection-audit.md canary 서술)은 RED 로 남을 수 있다(§8 계약 기반 선-작성, RED-first).
"""
import os
import tempfile

from _ac_matrix_fixtures import (  # 공통 helper (ADR-140)
    REPO_ROOT,
    assert_gate_fail,
    assert_gate_pass,
    mutate_core,
    run_gate,
    run_gate_core,
    run_gate_none,
    write_ac_source,
    write_ac_source_noac,
    write_rtm,
)

_WF_MATRIX = os.path.join(REPO_ROOT, ".github", "workflows", "ac-traceability-matrix.yml")
_WF_SELFTEST = os.path.join(REPO_ROOT, ".github", "workflows", "ac-traceability-self-test.yml")
_WF_TEMPLATE = os.path.join(REPO_ROOT, "templates", "github-workflows", "ac-traceability-matrix.yml")
_WF_STORY_INIT = os.path.join(REPO_ROOT, ".github", "workflows", "story-init.yml")
_CLAUDE_MD = os.path.join(REPO_ROOT, "CLAUDE.md")
_AUDIT_DOC = os.path.join(REPO_ROOT, "docs", "security", "branch-protection-audit.md")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _tmp(d, name):
    return os.path.join(d, name)


# ─────────────────────────────────────────────────────────────────────────────
# AC-1a (normative) — story_uri present PR = 기존 신호 C(§5 fetch) 경로가 여전히 core 에 도달
#   (구 premature single-line hard-fail 이 none-routing 을 가리지 않음).
# ─────────────────────────────────────────────────────────────────────────────
def test_story_uri_present_reaches_core():
    body = _read(_WF_MATRIX)
    # 구 premature single-line hard-fail(story_uri 부재 = 즉시 실패) 잔존 시 none-선언 경로가
    #   adapter 단에서 아예 진입 불가 — AC-1a 위반(비적용 선언 경로 자체가 dead code 화).
    assert "story_uri marker 부재 (PR body) — non-suppressible" not in body, (
        "구 premature single-line hard-fail 잔존 — story_uri 부재만으로 즉시 실패하면 "
        "ac_applicability:none 비적용 선언 경로가 도달 불가(AC-1a 위반)"
    )
    # none-routing(adapter thin router → core) 배선 존재
    assert "applicability_none" in body, "none-routing(applicability_none output) 부재 — adapter thin router 미배선"
    # story_uri-present 경로 자체는 여전히 core 를 관통(short-circuit 아님) — 매핑 시 PASS, 미매핑 시 FAIL.
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = _tmp(d, "ac.md"), _tmp(d, "rtm.md")
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        write_rtm(rtm, [("AC-1a", "normative", "test_x")])
        assert_gate_pass(*run_gate(1, ac, rtm))
        write_rtm(rtm, [("AC-1a", "normative", None)])
        assert_gate_fail(*run_gate(1, ac, rtm))


# ─────────────────────────────────────────────────────────────────────────────
# AC-1b (normative) — --ac-applicability-none --none-reason "<non-empty>" WITHOUT --ac-source
#   → in-job exit 0(비적용 PASS), 출력에 "비적용" 공개(over-strict 아님).
# ─────────────────────────────────────────────────────────────────────────────
def test_nonapplicable_declaration_in_job_pass():
    rc, out = run_gate_none("marketplace-sync — 추적 AC 없음")
    assert_gate_pass(rc, out)
    assert "비적용" in out, f"비적용 positive 공개 부재\n{out}"
    # phase 2 변형도 동일하게 PASS(매트릭스 phase 1·2 동형)
    with tempfile.TemporaryDirectory() as d:
        rc2, out2 = run_gate_none("marketplace-sync — 추적 AC 없음", phase=2, tests_root=d)
        assert_gate_pass(rc2, out2)


# ─────────────────────────────────────────────────────────────────────────────
# AC-1c (normative) — NEITHER --ac-source NOR --ac-applicability-none(both-absent) → exit 1
#   (distinct default guard, silent default-PASS 금지 — AC-2 reason-guard 와 별개 축).
# ─────────────────────────────────────────────────────────────────────────────
def test_both_absent_fail_closed():
    assert_gate_fail(*run_gate_none(None, none_declaration=False))


# ─────────────────────────────────────────────────────────────────────────────
# AC-2 (normative) — --none-reason "" (또는 공백) → exit 1 (none-무사유, auditability 의무).
# ─────────────────────────────────────────────────────────────────────────────
def test_none_without_reason_fail():
    assert_gate_fail(*run_gate_none(""))
    assert_gate_fail(*run_gate_none("   "))


# ─────────────────────────────────────────────────────────────────────────────
# AC-3 (normative) — --ac-source <normative≥1> + none 선언 = none-위장 FAIL(surface overrides none).
#   discriminating companion: NO_AC_SURFACE §5 + none 선언 = 병존-무해 PASS.
# ─────────────────────────────────────────────────────────────────────────────
def test_none_spoof_with_normative_ac_fail():
    with tempfile.TemporaryDirectory() as d:
        ac = _tmp(d, "ac.md")
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        assert_gate_fail(*run_gate(1, ac, none_declaration=True, none_reason="위장", rtm_not_yet=True))
        ac2 = _tmp(d, "ac2.md")
        write_ac_source_noac(ac2)
        assert_gate_pass(*run_gate(1, ac2, none_declaration=True, none_reason="병존", rtm_not_yet=True))


# ─────────────────────────────────────────────────────────────────────────────
# AC-4 (normative) — story-init 이 codeforge-family PR body 에 story_uri: 를 immutable-SHA ref 로 emit
#   (transient feature-branch ref 아님).
# ─────────────────────────────────────────────────────────────────────────────
def test_story_init_emits_story_uri_permanent_ref():
    body = _read(_WF_STORY_INIT)
    assert "story_uri:" in body, "story-init 이 PR body 에 story_uri: 를 emit 하지 않음(AC-4)"
    # immutable-SHA 사용(commit API .commit.sha + COMMIT_SHA 변수 조립) — transient ref 금지
    assert ".commit.sha" in body, "immutable-SHA API 필드(.commit.sha) 사용 부재"
    assert "COMMIT_SHA" in body, "COMMIT_SHA 변수 사용 부재(immutable ref 조립)"
    assert "blob/${BRANCH}" not in body, "transient feature-branch blob ref(blob/${BRANCH}) 사용 — 비영구 ref 위반"
    assert "blob/feat/" not in body, "transient feature-branch blob ref(blob/feat/) 사용 — 비영구 ref 위반"


# ─────────────────────────────────────────────────────────────────────────────
# AC-5 (normative) — required 등록 ordering invariant: 매트릭스/self-test/template 워크플로가
#   self-register 하지 않음(절차 검증, CFP-2609 test_required_registration_ordering 계승).
# ─────────────────────────────────────────────────────────────────────────────
def test_required_registration_ordering_no_self_register():
    # 등록 act = Orchestrator post-merge gh api (forged machine test 금지). 워크플로의 **실행 단계**
    #   (run/uses)가 self-register 하지 않음을 검증 — ordering invariant(self-test green → own-PR green →
    #   THEN 등록) born-broken 선차단. 서술 주석의 개념 언급은 조작이 아니므로 전체-라인 주석은 제외.
    def _executable(body):
        return "\n".join(ln for ln in body.splitlines() if not ln.lstrip().startswith("#"))

    for wf_path in (_WF_MATRIX, _WF_SELFTEST, _WF_TEMPLATE):
        exe = _executable(_read(wf_path))
        assert "branches/main/protection" not in exe, \
            f"{wf_path}: 워크플로 실행 라인이 branch-protection self-register (chicken-egg)"
        assert "required_status_checks" not in exe, \
            f"{wf_path}: 워크플로 실행 라인이 required_status_checks 조작 (ordering invariant 위반)"


# ─────────────────────────────────────────────────────────────────────────────
# AC-6 (normative) — 6→7 등록 doc parity: 기존 6 contexts 보존 + ac-traceability-matrix 추가
#   (live GET parity 는 post-register — 본 테스트는 doc 측 SSOT 검증).
# ─────────────────────────────────────────────────────────────────────────────
def test_seven_tuple_doc_live_parity():
    claude = _read(_CLAUDE_MD)
    # CFP-2782 (ADR-121 Wave 2): `Verify deploy lane presence` context 제거(9→8). 잔존 required context 보존 확인.
    preserved = [
        "phase-gate-mergeable",
        "invariant-check",
        "doc frontmatter schema (CFP-28 — strict)",
        "doc section schema (CFP-28 — strict)",
        "check-gate",
    ]
    for ctx in preserved:
        assert ctx in claude, f"CLAUDE.md 브랜치 보호 표에 기존 context '{ctx}' 부재 (보존 위반)"
    assert "ac-traceability-matrix" in claude, "CLAUDE.md 에 ac-traceability-matrix context 부재"
    assert "8-tuple" in claude, "CLAUDE.md 8-tuple 명문 부재"


# ─────────────────────────────────────────────────────────────────────────────
# AC-7 (normative) — 등록 전 canary 는 genuine(실 no-story_uri PR)이어야 하며 synthetic 조작 금지,
#   rollback-ready 절차 보유(procedural — 문서 서술 검증).
# ─────────────────────────────────────────────────────────────────────────────
def test_canary_genuine_not_synthetic():
    body = _read(_AUDIT_DOC)
    assert "genuine 비적용 no-story_uri canary" in body, \
        "branch-protection-audit.md 에 genuine 비적용 no-story_uri canary 절차 명문 부재"
    assert "synthetic" in body, "synthetic(조작) canary 금지 명문 부재"
    assert "rollback-ready" in body, "rollback-ready 절차 명문 부재"


# ─────────────────────────────────────────────────────────────────────────────
# AC-8 (normative) — 비적용 선언 self-test 3경로(reason-guard/spoof-guard/both-absent-guard) discriminating
#   mutation-kill 로 born-hollow 봉인 실증. in-process(bash 비의존, Windows 대응).
# ─────────────────────────────────────────────────────────────────────────────
def test_nonapplicable_selftest_discriminating():
    """AC-8 — none-declaration 3 결정라인이 discriminating mutation-kill 로 봉인됨을 실증.

    3 결정라인: reason-guard(`if not (none_reason and none_reason.strip()):`) /
    spoof-guard(`if none_declaration and ac_source_path is None:`) /
    both-absent-guard(`if ac_source_path is None and not none_declaration:`).
    각 base(원본 exit1) → mut(변조 exit0=leak) 로 KILL 을 실증하고, diff==0(변조 미적용)이면
    INCONCLUSIVE 로 배제(applied assert).

    ★ 공개 천장: 비적용 선언 PASS(reason-guard 통과 후 exit0) 경로 자체는 orig-exit0 이라 직접
    mutation-kill(exit1→exit0) 대상이 될 수 없다 — 이 PASS 가 reason-gated(vacuous 아님)임은 아래
    positive reachability 확인 + M-NONE-REASON companion(빈 사유 FAIL 이 mutation 으로 leak) 으로
    load-bearing 하게 증명한다. "완전 봉인" hard-claim 은 하지 않는다(정직 천장, ADR-119).
    """
    with tempfile.TemporaryDirectory() as d:
        # positive reachability — 비적용 선언 PASS 도달(skip REACHABLE, over-strict 아님).
        assert_gate_pass(*run_gate_none("real reason"))

        # M-NONE-REASON — reason-guard 무력화 → none+빈사유가 PASS 로 leak 해야 kill
        mut_reason, applied_reason = mutate_core(
            os.path.join(d, "mut_reason"),
            r"if not \(none_reason and none_reason\.strip\(\)\):",
            "if False:  # MUT-NONE-REASON",
        )
        assert applied_reason, "M-NONE-REASON mutation 미적용(diff 0) — INCONCLUSIVE(kill 무효)"
        base_rc, base_out = run_gate_none("")
        assert base_rc == 1, f"원본이 none+빈사유를 FAIL 로 못 잡음(exit {base_rc}) — 반증 전제 붕괴\n{base_out}"
        mut_rc, _ = run_gate_core(mut_reason, 1, none_declaration=True, none_reason="", rtm_not_yet=True)
        assert mut_rc == 0, f"reason-guard 무력화가 KILL 안 됨(mut exit {mut_rc}, 기대 0=leak) — 봉인 미실증"

        # M-SPOOF — spoof-guard 무력화 → normative+none 위장이 PASS 로 leak 해야 kill
        ac_spoof = _tmp(d, "ac_spoof.md")
        write_ac_source(ac_spoof, [("AC-1a", "derived", "normative")])
        mut_spoof, applied_spoof = mutate_core(
            os.path.join(d, "mut_spoof"),
            r"if none_declaration and ac_source_path is None:",
            "if none_declaration:  # MUT-SPOOF",
        )
        assert applied_spoof, "M-SPOOF mutation 미적용(diff 0) — INCONCLUSIVE(kill 무효)"
        base_rc2, base_out2 = run_gate(1, ac_spoof, none_declaration=True, none_reason="위장", rtm_not_yet=True)
        assert base_rc2 == 1, f"원본이 위장(normative+none)을 FAIL 로 못 잡음(exit {base_rc2}) — 반증 전제 붕괴\n{base_out2}"
        mut_rc2, _ = run_gate_core(mut_spoof, 1, ac_spoof, none_declaration=True, none_reason="위장", rtm_not_yet=True)
        assert mut_rc2 == 0, f"spoof-guard 무력화가 KILL 안 됨(mut exit {mut_rc2}, 기대 0=leak) — 봉인 미실증"

        # M-BOTHABSENT — both-absent-guard 무력화 → 둘다부재가 PASS(또는 crash 아닌 exit0)로 leak 해야 kill
        mut_bothabsent, applied_bothabsent = mutate_core(
            os.path.join(d, "mut_bothabsent"),
            r"if ac_source_path is None and not none_declaration:",
            "if False:  # MUT-BOTHABSENT",
        )
        assert applied_bothabsent, "M-BOTHABSENT mutation 미적용(diff 0) — INCONCLUSIVE(kill 무효)"
        base_rc3, base_out3 = run_gate_none(None, none_declaration=False)
        assert base_rc3 == 1, f"원본이 both-absent 를 FAIL 로 못 잡음(exit {base_rc3}) — 반증 전제 붕괴\n{base_out3}"
        mut_rc3, _ = run_gate_core(mut_bothabsent, 1, none_declaration=False, rtm_not_yet=True)
        assert mut_rc3 == 0, f"both-absent-guard 무력화가 KILL 안 됨(mut exit {mut_rc3}, 기대 0=leak) — 봉인 미실증"


# ─────────────────────────────────────────────────────────────────────────────
# AC-9 (normative) — adapter(.github/workflows) ↔ template(templates/github-workflows) byte-identical
#   (wrapper-self repo-guard 무손상).
# ─────────────────────────────────────────────────────────────────────────────
def test_adapter_template_byte_identical():
    assert _read(_WF_MATRIX) == _read(_WF_TEMPLATE), \
        f"{_WF_MATRIX} ↔ {_WF_TEMPLATE} byte-identical 위반 — adapter/template sync 누락"
    for wf_path in (_WF_MATRIX, _WF_TEMPLATE):
        body = _read(wf_path)
        assert "github.repository == 'mclayer/plugin-codeforge'" in body, f"{wf_path}: repo-guard(F1) 부재"


# ─────────────────────────────────────────────────────────────────────────────
# AC-10 (advisory) — 마커 값 'none' 외(skip/n-a/false 등) 미인식 정책은 advisory: 명명 테스트 없음
#   (forged machine test 금지, §5.6 RO-1 / CFP-2609 계승). §8.1 이 named test 를 지정하지 않았다면
#   여기서도 신규 stub 을 발명하지 않는다.
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# AC-11 (advisory) — none 병존(story_uri+none) UX 안내 문구 품질 등은 advisory: 명명 테스트 없음
#   (동일 근거 — forged machine test 금지).
# ─────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# AC-12 (normative) — fetch 실패(story_uri resolve 불가)는 비적용 PASS 로 흡수되지 않고 판정불가
#   FAIL. adapter 는 resp.ok 가드 + 영구 ref convention(transient 금지)을 명문 보유(§결정8 F 상속).
# ─────────────────────────────────────────────────────────────────────────────
def test_none_fetch_fail_transient_ref_fail():
    with tempfile.TemporaryDirectory() as d:
        # (a) core — source-absent(fetch-fail 대리): 판정불가 FAIL, 비적용 PASS 흡수 금지
        assert_gate_fail(*run_gate(1, os.path.join(d, "does-not-exist.md"), rtm_not_yet=True))
    # (b) static — adapter 가 resp.ok 가드 + 영구 ref convention + transient 언급 보유
    body = _read(_WF_MATRIX)
    assert "if (!resp.ok)" in body, "resp.ok 가드 부재(fetch-fail 판정불가 처리 누락)"
    assert "영구 ref" in body, "영구 ref convention 명문 부재"
    assert "transient" in body, "transient ref 금지 명문 부재"
