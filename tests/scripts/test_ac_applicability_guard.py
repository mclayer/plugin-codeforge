#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""tests/scripts/test_ac_applicability_guard.py
CFP-2609 (Epic CFP-2602 G1 완결) Phase 2 / ADR-145 Amendment 1 §결정 8 — per-PR applicability 가드의
**명명 테스트**(RTM authoritative — Change Plan cfp-2609 §8.1). 본 Story 자체가 dogfood: §8.1 이 명명한
10개 normative 테스트(AC-1a/1b/2..9/11)가 여기서 **실 def**(stub 아님)로 실재해야 게이트의 자기 Phase 2
PR 이 Hop3(§8↔실 symbol, ast resolve)를 통과한다. 함수명은 §8.1 과 1:1 정합(변경 금지).

AC-10(advisory)는 명명 테스트 없음 — forged machine test 금지(§5.6 RO-1 / advisory routed).

pytest 로 실행 가능(requirements.txt: pytest). 각 함수는 실제로 core/CLI 를 구동(assert_gate_*) 하거나
workflow/CLAUDE.md 실 파일을 검증(진짜 GREEN). subprocess fork 판정은 exit code 단독 아닌 도메인
sentinel 병행(assert_gate_fail — distinct-marker).
"""
import os

from _ac_matrix_fixtures import (  # 공통 helper (ADR-140)
    REPO_ROOT,
    assert_gate_fail,
    assert_gate_nonzero,
    assert_gate_pass,
    mutate_core,
    run_gate,
    run_gate_core,
    write_ac_source,
    write_ac_source_advonly,
    write_ac_source_countonly,
    write_ac_source_degraded_token,
    write_ac_source_empty,
    write_ac_source_noac,
    write_ac_source_notoken_table,
    write_rtm,
    write_rtm_placeholder,
)

_WF_MATRIX = os.path.join(REPO_ROOT, ".github", "workflows", "ac-traceability-matrix.yml")
_WF_SELFTEST = os.path.join(REPO_ROOT, ".github", "workflows", "ac-traceability-self-test.yml")
_WF_TEMPLATE = os.path.join(REPO_ROOT, "templates", "github-workflows", "ac-traceability-matrix.yml")
_CLAUDE_MD = os.path.join(REPO_ROOT, "CLAUDE.md")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _tmp(d, name):
    return os.path.join(d, name)


import tempfile  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# AC-1a (normative) — 비적용 positive 확정(resolve 성공 ∧ 0 normative) → in-job genuine PASS(exit 0)
# ─────────────────────────────────────────────────────────────────────────────
def test_applicability_nonapplicable_in_job_pass():
    with tempfile.TemporaryDirectory() as d:
        ac = _tmp(d, "ac.md")
        # (a) §5 present, AC 표·AC-ID 토큰 부재 → 비적용 PASS (skip REACHABLE — over-strict 아님)
        write_ac_source_noac(ac)
        rc, out = run_gate(1, ac, rtm_not_yet=True)
        assert_gate_pass(rc, out)
        assert "비적용" in out, f"비적용 positive 공개 부재\n{out}"
        # (b) §5 섹션 자체 부재 → 비적용 PASS
        write_ac_source_noac(ac)  # (재확인용)
        with open(ac, "w", encoding="utf-8") as fh:
            fh.write("## §3. 무언가\n\n내용(§5 자체 부재)\n")
        assert_gate_pass(*run_gate(1, ac, rtm_not_yet=True))
        # (c) records present · 0 normative(전부 declared/advisory) → 비적용-유사 PASS
        write_ac_source_advonly(ac)
        assert_gate_pass(*run_gate(1, ac, rtm_not_yet=True))
        # (d) phase 2 도 동일하게 비적용 PASS (매트릭스 phase 1·2 동형)
        write_ac_source_noac(ac)
        assert_gate_pass(*run_gate(2, ac, rtm_not_yet=True, tests_root=d))


# ─────────────────────────────────────────────────────────────────────────────
# AC-1b (normative) — 적용(≥1 normative 선언) ∧ §8 미매핑 → exit non-0 (fail-closed FAIL 보존)
# ─────────────────────────────────────────────────────────────────────────────
def test_applicable_unmapped_fails():
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = _tmp(d, "ac.md"), _tmp(d, "rtm.md")
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        write_rtm(rtm, [("AC-1a", "normative", None)])  # 명명 테스트 없음 → 미매핑
        assert_gate_fail(*run_gate(1, ac, rtm))
        # 매핑하면 PASS (검출력이 scope 정정으로 약화되지 않음 입증)
        write_rtm(rtm, [("AC-1a", "normative", "test_x")])
        assert_gate_pass(*run_gate(1, ac, rtm))


# ─────────────────────────────────────────────────────────────────────────────
# AC-2 (normative) — 판정불가(degraded) 어떤 경로도 "비적용 skip" 흡수 금지 (anti-degradation)
# ─────────────────────────────────────────────────────────────────────────────
def test_undecidable_never_skips():
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = _tmp(d, "ac.md"), _tmp(d, "rtm.md")
        write_rtm(rtm, [("AC-1a", "normative", "test_x")])
        # (a) 산문 AC-ID 토큰 present ∧ parseable 표 부재 = degradation → FAIL
        write_ac_source_degraded_token(ac)
        assert_gate_fail(*run_gate(1, ac, rtm_not_yet=True))
        # (b) ★structural-signature keying: 표 signature present ∧ ID 손상(XX-1, 토큰 부재) → FAIL (NO_AC_SURFACE 아님)
        write_ac_source_notoken_table(ac)
        assert_gate_fail(*run_gate(1, ac, rtm_not_yet=True))
        # (c) count-only(acceptance_criteria_count: N, 항목화 표 부재) → FAIL (CFP-2603 무손상)
        write_ac_source_countonly(ac)
        assert_gate_fail(*run_gate(1, ac, rtm_not_yet=True))
        # (d) 빈-AC(§5 표 present, 0 rows) → FAIL (F-AC7-a 재개방 금지)
        write_ac_source_empty(ac)
        assert_gate_fail(*run_gate(1, ac, rtm_not_yet=True))
        # (e) ac-source 파일 부재(fetch 실패 대리) → FAIL
        assert_gate_fail(*run_gate(1, _tmp(d, "does-not-exist.md"), rtm_not_yet=True))
        # (f) 적용 PR + rtm placeholder(§8 "작성 예정") → FAIL (not-yet 와 구분)
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        write_rtm_placeholder(rtm)
        assert_gate_fail(*run_gate(1, ac, rtm))


# ─────────────────────────────────────────────────────────────────────────────
# AC-3 (normative) — 신호 non-suppressible: 적용 PR 이 마커/tier 조작으로 비적용 위장 불가
# ─────────────────────────────────────────────────────────────────────────────
def test_signal_non_suppressible():
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = _tmp(d, "ac.md"), _tmp(d, "rtm.md")
        # resolved §5 에 normative AC 가 present 하는 한, §8 미추적 = 적용 판정(FAIL) 도달 —
        #   "비적용 skip" 으로 흡수되지 않음(신호 = authoritative §5 content, PR-body 마커 아님).
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        write_rtm(rtm, [("AC-1a", "normative", None)])
        assert_gate_fail(*run_gate(1, ac, rtm))
        # rtm-not-yet(phase1) 조차 Hop1 통과 후 not-yet PASS 이지 "비적용" 이 아니다 — normative 는 여전히
        #   추적 대상(phase2 에서 RTM 필수 → FAIL): 위장 불가.
        assert_gate_fail(*run_gate(2, ac, rtm_not_yet=True, tests_root=d))
        # 유일한 비적용 도달 = §5 normative AC 물리 제거(고가시). 제거하면 비적용 PASS 이나 이는 은닉 아님.
        write_ac_source_noac(ac)
        assert_gate_pass(*run_gate(1, ac, rtm_not_yet=True))


# ─────────────────────────────────────────────────────────────────────────────
# AC-4 (normative) — Phase-1 rtm_uri 부재 = not-yet-applicable PASS (placeholder fallback false-fail 제거)
# ─────────────────────────────────────────────────────────────────────────────
def test_phase1_rtm_absent_ok():
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = _tmp(d, "ac.md"), _tmp(d, "rtm.md")
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        # (a) phase1 + rtm-not-yet EXPLICIT + normative → Hop1 only PASS
        assert_gate_pass(*run_gate(1, ac, rtm_not_yet=True))
        # (b) not-yet ≠ placeholder: 적용 PR + rtm placeholder(§8 "작성 예정") → FAIL (fallback 흡수 아님)
        write_rtm_placeholder(rtm)
        assert_gate_fail(*run_gate(1, ac, rtm))
        # (c) phase2 + rtm-not-yet → FAIL (RTM 은 Phase-2 필수 산출물)
        assert_gate_nonzero(*run_gate(2, ac, rtm_not_yet=True, tests_root=d))


# ─────────────────────────────────────────────────────────────────────────────
# AC-5 (normative) — 적용성 가드 = 항상 실행 in-job(paths 필터 부재 + job-level if-skip 부재) — F-1/F-2/F-3
# ─────────────────────────────────────────────────────────────────────────────
def test_no_paths_filter_always_runs():
    import yaml

    for wf_path in (_WF_MATRIX, _WF_TEMPLATE):
        d = yaml.safe_load(_read(wf_path))
        on_block = d.get(True, d.get("on"))  # YAML 1.1 'on:' → boolean True key quirk
        assert on_block is not None, f"{wf_path}: on 트리거 부재"
        pr = on_block["pull_request"]
        # paths / paths-ignore 필터 부재 (required-pending 함정 F-3)
        assert isinstance(pr, dict), f"{wf_path}: pull_request 트리거 형태 예상외"
        assert "paths" not in pr and "paths-ignore" not in pr, f"{wf_path}: paths 필터 존재 (F-3 위반)"
        job = d["jobs"]["ac-traceability-matrix"]
        # job-level if = repo-guard 만 (적용성 기반 skip 아님, F-2)
        assert "github.repository" in job["if"], f"{wf_path}: repo-guard if 부재"
        assert "applicab" not in job["if"].lower() and "story_uri" not in job["if"], \
            f"{wf_path}: job-level if 가 적용성 skip 사용 (F-2 위반)"
        # 게이트-run step 에 적용성 skip if 부재 (in-job exit code 판정만)
        for step in job["steps"]:
            step_if = str(step.get("if", ""))
            assert "story_uri" not in step_if and "applicab" not in step_if.lower(), \
                f"{wf_path}: step-level 적용성 skip 발견 — in-job exit-code 판정이어야"


# ─────────────────────────────────────────────────────────────────────────────
# AC-6 (normative) — story_uri 영구 ref 실 fetch·내용 검증(마커 존재≠형식통과) + 404 단일원인 처리 부재
# ─────────────────────────────────────────────────────────────────────────────
def test_story_uri_real_content_verify():
    body = _read(_WF_MATRIX)
    # 실 내용 fetch (contents API + base64 decode) — 마커 존재만으로 형식통과 아님
    assert "fetchDoc" in body and "api.github.com/repos/" in body, "cross-repo 실 fetch 부재"
    assert "Buffer.from(file.content" in body, "base64 실 내용 decode 부재 (형식통과만)"
    # resp.ok 가드 — 404 3-class 단일원인 처리 금지 (auth-masking vs ref-missing vs 5xx 전부 FAIL)
    assert "if (!resp.ok)" in body, "resp.ok 가드 부재 (404 conflation 위험)"
    assert "판정불가=FAIL" in body, "non-ok=판정불가 FAIL 명문 부재 (skip 흡수 위험)"
    # 영구 ref convention 명문 (transient feature ref 금지)
    assert "영구 ref" in body and "transient" in body, "story_uri 영구-ref convention 명문 부재"
    # frontmatter parse 실패(Class B) = post-fetch 판정불가 FAIL
    assert "frontmatter 부재" in body, "Class B(frontmatter parse) 판정불가 처리 부재"


# ─────────────────────────────────────────────────────────────────────────────
# AC-7 (normative) — 적용성 self-test 3경로 discriminating mutation-kill 실증(born-hollow 봉인)
# ─────────────────────────────────────────────────────────────────────────────
def test_applicability_selftest_discriminating():
    """AC-7 — self-test 가 3경로를 discriminate + mutation-kill 로 born-hollow 를 봉인함을 실증.

    in-process(bash 비의존, 이식성 — Windows WSL-bash 부재 대응) 실현. 상보 shell self-test
    (test_check-ac-traceability-matrix.sh, ac-traceability-self-test.yml step)이 F-APPLIC-* 6종 +
    Mutation A-F/NOTOKEN 전량을 CI 로 별도 실행하며, 본 named test 는 그 discrimination 의 핵심을
    실 core CLI 로 재확인해 AC-7 을 Hop3 실 symbol 로 실재화한다.

    (1) 3경로 discrimination: 비적용→exit0 / 적용-미추적→exit1 / §5-empty→exit1.
    (2) mutation-kill(NOTOKEN, Codex P2 structural-signature keying): core `if has_sig:` 를 무력화하면
        손상표(XX-1, 표 signature present·AC-ID 토큰 부재)가 비적용 PASS 로 새야(leak) 함 —
        원본 exit1 → 변조 exit0 = KILL. diff-0(변조 미적용)=INCONCLUSIVE 배제. born-hollow 봉인 실증.
    """
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = _tmp(d, "ac.md"), _tmp(d, "rtm.md")
        # (1) 3경로 discrimination (실 core)
        write_ac_source_noac(ac)
        assert_gate_pass(*run_gate(1, ac, rtm_not_yet=True))            # 비적용 → PASS
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        write_rtm(rtm, [("AC-1a", "normative", None)])
        assert_gate_fail(*run_gate(1, ac, rtm))                         # 적용-미추적 → FAIL
        write_ac_source_empty(ac)
        assert_gate_fail(*run_gate(1, ac, rtm))                         # §5-empty → FAIL
        # (2) mutation-kill (NOTOKEN — structural-signature keying)
        write_ac_source_notoken_table(ac)                              # 표 signature present + XX-1(토큰 부재)
        base_rc, base_out = run_gate(1, ac, rtm_not_yet=True)
        assert base_rc == 1, f"원본이 손상표(XX-1)를 FAIL 로 못 잡음(exit {base_rc}) — 반증 전제 붕괴\n{base_out}"
        mut_core, applied = mutate_core(os.path.join(d, "mut"), r"if has_sig:", "if False:  # MUT-NOTOKEN")
        assert applied, "mutation 미적용(diff 0) — INCONCLUSIVE(born-broken 방지, kill 무효)"
        mut_rc, _ = run_gate_core(mut_core, 1, ac, rtm_not_yet=True)
        assert mut_rc == 0, f"has_sig 무력화(token-only keying)가 KILL 안 됨(mut exit {mut_rc}, 기대 0=leak) — 봉인 미실증"


# ─────────────────────────────────────────────────────────────────────────────
# AC-8 (normative) — required 등록 ordering invariant: 워크플로가 self-register 하지 않음(절차 검증)
# ─────────────────────────────────────────────────────────────────────────────
def test_required_registration_ordering():
    # 등록 act = Orchestrator post-merge gh api (forged machine test 금지). 워크플로의 **실행 단계**
    #   (run/uses)가 self-register 하지 않음을 검증 — ordering invariant(self-test green → own-PR green →
    #   THEN 등록) born-broken 선차단. 서술 주석의 개념 언급(required_status_checks / continue-on-error 등)은
    #   조작이 아니므로 전체-라인 주석은 제외하고 실행 라인만 검사한다(naive 전체-문자열 매칭 = prose false-flag).
    #   실 self-register step(run: gh api …/branches/main/protection …)은 실행 라인이므로 여전히 검출된다.
    def _executable(body):
        return "\n".join(ln for ln in body.splitlines() if not ln.lstrip().startswith("#"))

    for wf_path in (_WF_MATRIX, _WF_SELFTEST, _WF_TEMPLATE):
        exe = _executable(_read(wf_path))
        assert "branches/main/protection" not in exe, f"{wf_path}: 워크플로 실행 라인이 branch-protection self-register (chicken-egg)"
        assert "required_status_checks" not in exe, f"{wf_path}: 워크플로 실행 라인이 required_status_checks 조작 (ordering invariant 위반)"
    # self-test 워크플로 = non-required + day-1 hard-fail (own-PR green 산출 채널이지 등록 아님)
    selftest = _read(_WF_SELFTEST)
    assert "continue-on-error" not in _executable(selftest), "self-test day-1 hard-fail 위반 (실행 라인 continue-on-error)"
    assert "ac-traceability-self-test" in selftest, "self-test job 명 부재"


# ─────────────────────────────────────────────────────────────────────────────
# AC-9 (normative) — 6→7 등록 = 기존 6 contexts 보존 + ac-traceability-matrix 추가 (doc parity SSOT)
# ─────────────────────────────────────────────────────────────────────────────
def test_seven_tuple_preserves_six():
    claude = _read(_CLAUDE_MD)
    original_six = [
        "phase-gate-mergeable",
        "invariant-check",
        "doc frontmatter schema (CFP-28 — strict)",
        "doc section schema (CFP-28 — strict)",
        "check-gate",
        "Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)",
    ]
    for ctx in original_six:
        assert ctx in claude, f"CLAUDE.md 브랜치 보호 표에 기존 context '{ctx}' 부재 (6 보존 위반)"
    assert "ac-traceability-matrix" in claude, "CLAUDE.md 에 ac-traceability-matrix(7번째 context) 부재"
    # doc SSOT 가 7-tuple 임을 명문 (live 승격 대상 = doc parity)
    assert "7-tuple" in claude, "CLAUDE.md 7-tuple 명문 부재"


# ─────────────────────────────────────────────────────────────────────────────
# AC-11 (normative) — 회귀 금지: fail-closed 핵심(적용-미추적=FAIL) + F-AC7-a + wrapper-self repo-guard 무손상
# ─────────────────────────────────────────────────────────────────────────────
def test_no_regression_failclosed_core():
    with tempfile.TemporaryDirectory() as d:
        ac, rtm = _tmp(d, "ac.md"), _tmp(d, "rtm.md")
        # (a) 적용-미추적(normative unmapped) = FAIL 보존
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        write_rtm(rtm, [("AC-1a", "normative", None)])
        assert_gate_fail(*run_gate(1, ac, rtm))
        # (b) 빈-AC(§5 표 0 rows) = F-AC7-a FAIL 재개방 금지
        write_ac_source_empty(ac)
        write_rtm(rtm, [("AC-1a", "normative", "test_x")])
        assert_gate_fail(*run_gate(1, ac, rtm))
        # (c) malformed id = Hop1 FAIL
        write_ac_source(ac, [("AC-1A", "derived", "normative")])
        write_rtm(rtm, [("AC-1A", "normative", "test_x")])
        assert_gate_fail(*run_gate(1, ac, rtm))
        # (d) Phase2 born-missing = FAIL
        write_ac_source(ac, [("AC-1a", "derived", "normative")])
        write_rtm(rtm, [("AC-1a", "normative", "test_missing_sym")])
        assert_gate_fail(*run_gate(2, ac, rtm, tests_root=d))
    # (e) wrapper-self repo-guard(F1) 무손상 — consumer born-broken 방지
    for wf_path in (_WF_MATRIX, _WF_TEMPLATE):
        body = _read(wf_path)
        assert "github.repository == 'mclayer/plugin-codeforge'" in body, \
            f"{wf_path}: wrapper-self repo-guard(F1) 부재 — consumer 오탐 위험"
