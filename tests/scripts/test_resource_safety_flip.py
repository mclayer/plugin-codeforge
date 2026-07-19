#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/scripts/test_resource_safety_flip.py — CFP-2650 Phase 2 flip self-test.

CFP-2650 = `resource-safety-claim-proof-presence` 게이트를 warning → blocking-on-pr 로 승격
(CFP-2594 flip model 동형). 본 self-test 은 승격 산출물이 계약대로 착지했는지 discriminating
(mutation-backed) 하게 검증한다.

authoritative RTM = Change Plan §8.1 (internal-docs). 7 symbol (6 normative + 1 declared):
  1. test_promotion_corpus_clean_no_red_flip                     (AC-1)  normative
  2. test_blocking_flip_continue_on_error_removed_both_workflows (AC-2)  normative
  3. test_registry_tier_blocking_with_provenance                 (AC-2)  normative
  4. test_workflow_pair_byte_identical                           (AC-2)  normative
  5. test_branch_protection_seven_tuple_unchanged                (AC-2)  normative (doc-declared tier)
  6. test_honesty_ceiling_presence_not_truth_preserved           (AC-7)  normative
  7. test_no_stale_warning_self_description_post_flip            (R1)    declared

TDD red-first: 각 normative test 는 positive-control(실 산출물 검증) + mutation-control(in-memory/
temp mutant 에 결함 주입 → 검출 helper 가 flag 함을 assert) 을 함께 담아 positive assertion 이
load-bearing(vacuous 아님) 임을 증명한다. 실 repo 파일은 절대 변형하지 않는다(in-memory/temp only).
모든 assertion 은 2-axis(실행 return/parsed-state + substring/구조) — presence-grep-only 금지.
"""

import hashlib
import json
import os
import pathlib
import re
import sys
import tempfile

# ac-traceability Hop3 tests-root = `tests`; 파일 위치 tests/scripts/ → parents[2] = repo root.
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

WF_GITHUB = REPO_ROOT / ".github" / "workflows" / "resource-safety-claim-proof-presence.yml"
WF_TEMPLATE = REPO_ROOT / "templates" / "github-workflows" / "resource-safety-claim-proof-presence.yml"
REGISTRY = REPO_ROOT / "docs" / "evidence-checks-registry.yaml"
AUDIT = REPO_ROOT / "docs" / "security" / "branch-protection-audit.md"
LINT_PY = REPO_ROOT / "scripts" / "lib" / "check_resource_safety_claim_proof.py"
LINT_SH = REPO_ROOT / "scripts" / "check-resource-safety-claim-proof.sh"
BASELINE = REPO_ROOT / "docs" / "resource-safety-claim-baseline.yaml"

# 게이트 job/entry name (branch-protection 7-tuple 에 편입되면 안 되는 이름 — surfacing ≠ required).
GATE_NAME = "resource-safety-claim-proof-presence"

# CFP-2650 승격 후 wrapper required_status_checks contexts (7-tuple 무변경 — surfacing 은 required 편입 아님).
EXPECTED_SEVEN = (
    "phase-gate-mergeable",
    "invariant-check",
    "doc frontmatter schema (CFP-28 — strict)",
    "doc section schema (CFP-28 — strict)",
    "check-gate",
    "Verify deploy lane presence (Phase 2 wire — ADR-087 Amd 2)",
    "ac-traceability-matrix",
)


# ─────────────────────── shared helpers (non-test — `_` prefix) ──────────────────

def _import_lint():
    """scripts/lib 를 sys.path 에 얹고 lint 모듈 import (public: scan_corpus/load_baseline/subtract_baseline)."""
    libdir = str(REPO_ROOT / "scripts" / "lib")
    if libdir not in sys.path:
        sys.path.insert(0, libdir)
    import check_resource_safety_claim_proof as lint  # noqa: E402
    return lint


def _find_entry(node, name):
    """registry(dict/list 중첩) 를 재귀 순회해 name 일치 dict entry 반환 (구조 변화에 robust)."""
    if isinstance(node, dict):
        if node.get("name") == name:
            return node
        for value in node.values():
            found = _find_entry(value, name)
            if found is not None:
                return found
    elif isinstance(node, list):
        for item in node:
            found = _find_entry(item, name)
            if found is not None:
                return found
    return None


def _has_active_coe(text):
    """비-주석 라인에 활성 `continue-on-error: true` (blocking-on-pr flip 이면 부재해야 함) 존재 여부."""
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        if re.match(r"^\s*continue-on-error:\s*true", line):
            return True
    return False


def _tier_ok(entry):
    """registry entry 가 blocking-on-pr tier + CFP-2650 provenance 를 보유하는지 (predicate)."""
    return (
        entry.get("current_tier") == "blocking-on-pr"
        and entry.get("promoted_by") == "CFP-2650"
        and bool(entry.get("promoted_date"))
    )


def _extract_seven_tuple(md_text):
    """audit doc 에서 backtick-wrapped JSON 배열 중 ac-traceability-matrix 를 포함한 것(=live 7-tuple) 추출."""
    for candidate in re.findall(r"`(\[[^`]*\])`", md_text):
        try:
            arr = json.loads(candidate)
        except (ValueError, TypeError):
            continue
        if isinstance(arr, list) and "ac-traceability-matrix" in arr:
            return arr
    return None


def _seven_ok(contexts):
    """required contexts 가 정확히 7개이고 게이트 job name 이 편입되지 않았는지 (predicate)."""
    return len(contexts) == 7 and GATE_NAME not in contexts


# honesty-ceiling(AC-7): affirmative-context 에서 금지된 hard-claim 폐집합. 부인(denial) 동반 시 EXEMPT.
_FORBIDDEN_AFFIRMATIVE = (
    "over-claim 봉인",
    "완전 방지",
    "완전 봉인",
    "truth 강제",
    "거짓 차단 보장",
)
# 금지구 직후 window 안 부인 marker (있으면 정직한 부인문 = EXEMPT). lint _DENIAL_MARKERS 철학 답습.
_DENIAL_NEAR = ("아님", "아니", "부재", "없", "않", "미강제", "금지")


def _affirmative_forbidden_hits(text, window=24):
    """금지 hard-claim 구가 부인 marker 동반 없이(=affirmative) 등장하는 위치 목록. 빈 목록 = 정직."""
    hits = []
    for phrase in _FORBIDDEN_AFFIRMATIVE:
        start = 0
        while True:
            idx = text.find(phrase, start)
            if idx == -1:
                break
            after = text[idx + len(phrase): idx + len(phrase) + window]
            if not any(d in after for d in _DENIAL_NEAR):
                hits.append((phrase, idx, after))
            start = idx + len(phrase)
    return hits


def _stale_workflow_lines(text):
    """flip 후 남으면 안 되는 stale warning-tier 자기서술 workflow 라인. `::warning::`(GHA severity) +
    `warning → blocking`(승격 방향 문구)는 정당 → EXCLUDE."""
    stale_markers = ("Tier: warning", "warning tier", "— warning")
    bad = []
    for line in text.splitlines():
        if "::warning::" in line:
            continue
        if "warning → blocking" in line or "warning→blocking" in line:
            continue
        for marker in stale_markers:
            if marker in line:
                bad.append((marker, line))
    return bad


def _stale_lint_lines(text):
    """lint py/sh 의 enforcement-tier 자기서술이 stale warning 인 라인. `::warning::` + 승격 방향 문구 EXCLUDE."""
    stale_markers = ("warning tier", "warning-tier", "warning mode")
    bad = []
    for line in text.splitlines():
        if "::warning::" in line:
            continue
        if "warning → blocking" in line or "warning→blocking" in line:
            continue
        for marker in stale_markers:
            if marker in line:
                bad.append((marker, line))
    return bad


# ─────────────────────── AC-1 ────────────────────────────────────────────────────

def test_promotion_corpus_clean_no_red_flip():
    """AC-1: 승격 시점 실 코퍼스가 clean → blocking flip 이 신규 red 유발 0.

    POS: scan_corpus(REPO_ROOT) → subtract_baseline == 0 new-over-claim (실 lint 실행 return-value).
    MUT: bare safety-claim(ReDoS-safe, proof/ceiling 무동반) temp .py 를 explicit_files 로 스캔 →
         findings >= 1 (red-flip 검출됨) — positive 0 이 vacuous 가 아님을 입증.
    """
    lint = _import_lint()

    # --- POS: 실 코퍼스 clean (axis1: scanned>0 실행 사실 / axis2: new==0 parsed count) ---
    scanned, raw_findings = lint.scan_corpus(str(REPO_ROOT))
    baseline_keys = lint.load_baseline(str(BASELINE))
    new_findings, grandfathered = lint.subtract_baseline(raw_findings, baseline_keys)
    assert scanned > 0, "코퍼스가 스캔되지 않음 (honest no-op 아닌 실 코퍼스 존재해야 AC-1 유의미)"
    assert len(new_findings) == 0, (
        "승격 시점 new-over-claim 존재 = blocking flip 이 red 유발 (AC-1 위반): %r" % (new_findings[:5],)
    )
    assert grandfathered >= 0  # subtract 계약 sanity (grandfather = legacy 동결)

    # --- MUT: bare over-claim 주입 (실 repo 무변형 — temp file) → 검출 load-bearing 입증 ---
    with tempfile.TemporaryDirectory() as tmp:
        mut = os.path.join(tmp, "mut_overclaim.py")
        with open(mut, "w", encoding="utf-8", newline="\n") as fh:
            fh.write('r"""module docstring"""\n')
            fh.write("# note: this parser is ReDoS-safe here\n")
        mut_scanned, mut_findings = lint.scan_corpus(str(REPO_ROOT), explicit_files=[mut])
        assert mut_scanned == 1
        assert len(mut_findings) >= 1, "bare over-claim mutant 미검출 = 검출 helper 무력 (assertion vacuous)"
        assert any(f[2] == "ReDoS-safe" for f in mut_findings), (
            "mutant 의 claim token(ReDoS-safe) 미검출: %r" % (mut_findings,)
        )


# ─────────────────────── AC-2 (blocking flip mechanics) ──────────────────────────

def test_blocking_flip_continue_on_error_removed_both_workflows():
    """AC-2: 두 workflow(.github + templates) 모두 활성 continue-on-error 제거 = blocking surfacing.

    POS: _has_active_coe(WF_GITHUB) is False AND _has_active_coe(WF_TEMPLATE) is False.
    MUT (Decision Table R2/R3): 실 텍스트에 job-level / step-level continue-on-error:true 를 각각
         재삽입 → 두 mutant 모두 _has_active_coe True (job-only·step-only 재유입 각각 RED).
    """
    gh_text = WF_GITHUB.read_text(encoding="utf-8")
    tpl_text = WF_TEMPLATE.read_text(encoding="utf-8")

    # --- POS (axis1: predicate False / axis2: 파일 실재 read) ---
    assert _has_active_coe(gh_text) is False, ".github workflow 에 활성 continue-on-error 잔존 (flip 미완)"
    assert _has_active_coe(tpl_text) is False, "templates workflow 에 활성 continue-on-error 잔존 (flip 미완)"

    # --- MUT R2: job-level 재삽입 ---
    job_anchor = "  %s:\n" % GATE_NAME
    assert job_anchor in gh_text, "job anchor 부재 — mutant anchor 무효"
    job_mut = gh_text.replace(job_anchor, job_anchor + "    continue-on-error: true\n", 1)
    assert job_mut != gh_text
    assert _has_active_coe(job_mut) is True, "job-level continue-on-error 재유입 미검출 (R2 RED 실패)"

    # --- MUT R3: step-level 재삽입 ---
    step_anchor = "        id: lint\n"
    assert step_anchor in gh_text, "step anchor 부재 — mutant anchor 무효"
    step_mut = gh_text.replace(step_anchor, step_anchor + "        continue-on-error: true\n", 1)
    assert step_mut != gh_text
    assert _has_active_coe(step_mut) is True, "step-level continue-on-error 재유입 미검출 (R3 RED 실패)"


def test_registry_tier_blocking_with_provenance():
    """AC-2: evidence-checks-registry 의 게이트 entry = blocking-on-pr + CFP-2650 provenance.

    POS: current_tier=='blocking-on-pr' AND promoted_by=='CFP-2650' AND promoted_date 비어있지 않음.
    MUT: current_tier='warning' 변형 / promoted_by 삭제 변형 → predicate 각각 RED.
    """
    import yaml  # lazy — tests 3/6 만 yaml 의존
    reg = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    entry = _find_entry(reg, GATE_NAME)

    # --- POS (axis1: parsed dict 필드 / axis2: provenance 필드 presence) ---
    assert entry is not None, "registry 에서 %s entry 미발견" % GATE_NAME
    assert entry.get("current_tier") == "blocking-on-pr", (
        "current_tier != blocking-on-pr: %r" % entry.get("current_tier")
    )
    assert entry.get("promoted_by") == "CFP-2650", "promoted_by != CFP-2650: %r" % entry.get("promoted_by")
    assert "promoted_date" in entry and entry.get("promoted_date"), "promoted_date 부재/빈값"
    assert _tier_ok(entry) is True

    # --- MUT: tier 되돌림 / provenance 삭제 → predicate RED ---
    mut_tier = dict(entry)
    mut_tier["current_tier"] = "warning"
    assert _tier_ok(mut_tier) is False, "warning tier 되돌림 미검출 (predicate vacuous)"

    mut_prov = dict(entry)
    mut_prov.pop("promoted_by", None)
    assert _tier_ok(mut_prov) is False, "promoted_by 삭제 미검출 (provenance predicate vacuous)"


def test_workflow_pair_byte_identical():
    """AC-2: .github ↔ templates workflow byte-identical (ADR-005 mirror parity).

    POS: sha256(WF_GITHUB bytes) == sha256(WF_TEMPLATE bytes).
    MUT: WF_GITHUB bytes 에 1 byte append / last-byte flip → sha 가 template 과 divergence.
    """
    gh_bytes = WF_GITHUB.read_bytes()
    tpl_bytes = WF_TEMPLATE.read_bytes()
    tpl_sha = hashlib.sha256(tpl_bytes).hexdigest()

    # --- POS (axis1: sha 동등 / axis2: 두 파일 실재 read) ---
    assert hashlib.sha256(gh_bytes).hexdigest() == tpl_sha, "workflow pair byte-divergence (ADR-005 위반)"

    # --- MUT: 1-byte 변형 2종 → divergence 검출 ---
    appended = gh_bytes + b"X"
    assert hashlib.sha256(appended).hexdigest() != tpl_sha, "1-byte append 미검출 (sha 비교 vacuous)"
    flipped = bytearray(gh_bytes)
    flipped[-1] ^= 0x01
    assert hashlib.sha256(bytes(flipped)).hexdigest() != tpl_sha, "last-byte flip 미검출 (sha 비교 vacuous)"


def test_branch_protection_seven_tuple_unchanged():
    """AC-2 (doc-declared tier semantics — live API 아닌 audit-doc 선언): required 7-tuple 무변경.

    POS: audit doc 의 7-tuple 이 정확히 7 context 이며 EXPECTED_SEVEN 와 집합 일치 AND 게이트 job
         name 이 편입되지 않음 (surfacing ≠ required-context 편입).
    MUT: 게이트 job name 을 추가한 8-list → predicate RED (job-name ∈ required = 위반).
    """
    md_text = AUDIT.read_text(encoding="utf-8")
    seven = _extract_seven_tuple(md_text)

    # --- POS (axis1: len/predicate / axis2: 집합 일치 + 게이트 미편입) ---
    assert seven is not None, "audit doc 에서 7-tuple 배열 추출 실패"
    assert len(seven) == 7, "required contexts 가 7개 아님: %d개 %r" % (len(seven), seven)
    assert set(seven) == set(EXPECTED_SEVEN), "7-tuple 내용 변경 감지: %r" % (sorted(seven),)
    assert GATE_NAME not in seven, "게이트 job 이 required 편입됨 (surfacing ≠ required 위반)"
    assert _seven_ok(seven) is True

    # --- MUT: 게이트 required 편입(7→8) → predicate RED ---
    mut_eight = list(seven) + [GATE_NAME]
    assert _seven_ok(mut_eight) is False, "게이트 required 편입(8-tuple) 미검출 (predicate vacuous)"


# ─────────────────────── AC-7 (honesty ceiling) ──────────────────────────────────

def test_honesty_ceiling_presence_not_truth_preserved():
    """AC-7: 승격 산출물이 honesty-ceiling(presence ≠ truth) 언어 보존 + 금지 hard-claim 부재.

    POS: 산출물(두 workflow + registry entry description + lint py) 집합 텍스트가 honesty-ceiling
         언어(ADR-151 / presence ≠ truth / bounded degradation) 포함 AND affirmative 금지구 0.
         (workflow/py/registry 의 `'완전 봉인' 아님`·`'완전 봉인' hard-claim 부재` 는 부인문 → 미flag.)
    MUT: affirmative 금지구('over-claim 봉인 보장') 를 workflow 사본에 주입 → predicate RED.
    """
    import yaml  # lazy
    reg = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    entry = _find_entry(reg, GATE_NAME)
    assert entry is not None
    entry_desc = entry.get("description", "")

    gh_text = WF_GITHUB.read_text(encoding="utf-8")
    tpl_text = WF_TEMPLATE.read_text(encoding="utf-8")
    py_text = LINT_PY.read_text(encoding="utf-8")
    collective = "\n".join([gh_text, tpl_text, entry_desc, py_text])

    # --- POS axis1: honesty-ceiling 언어 보존 ---
    assert "ADR-151" in collective, "honesty-ceiling 근거(ADR-151) 소실"
    assert any(m in collective for m in ("presence ≠ truth", "honesty ceiling", "bounded degradation")), (
        "honesty-ceiling 언어(presence ≠ truth / bounded degradation) 소실"
    )
    # --- POS axis2: affirmative 금지 hard-claim 부재 (부인문 EXEMPT) ---
    pos_hits = _affirmative_forbidden_hits(collective)
    assert pos_hits == [], "affirmative 금지 hard-claim 검출 (honesty ceiling 위반): %r" % (pos_hits,)

    # --- MUT: affirmative 금지구 주입 → RED ---
    mut_text = gh_text + "\n# 이 게이트는 over-claim 봉인 보장 GUARANTEE\n"
    mut_hits = _affirmative_forbidden_hits(mut_text)
    assert len(mut_hits) >= 1, "affirmative 금지구 주입 미검출 (predicate vacuous)"
    assert any(h[0] == "over-claim 봉인" for h in mut_hits), "주입 금지구 token 미검출: %r" % (mut_hits,)


# ─────────────────────── R1 (declared) ───────────────────────────────────────────

def test_no_stale_warning_self_description_post_flip():
    """R1 (declared): flip 후 stale warning-tier 자기서술 부재 + comment-step dead-path 부재.

    POS: workflow line 1 = '(blocking-on-pr)' 포함·'(warning mode)' 미포함; workflow/lint py/sh 에
         stale warning-tier 자기서술 라인 0(`::warning::` GHA severity·`warning → blocking` 방향 EXCLUDE);
         comment step 조건이 !cancelled()(또는 failure()) 포함 = flip 후 dead-path 아님.
    MUT (preferred): 'Tier: warning' 주입 → _stale_workflow_lines RED.
    """
    gh_text = WF_GITHUB.read_text(encoding="utf-8")
    tpl_text = WF_TEMPLATE.read_text(encoding="utf-8")
    py_text = LINT_PY.read_text(encoding="utf-8")
    sh_text = LINT_SH.read_text(encoding="utf-8")

    # --- POS axis1: workflow surface (line 1 + stale-line 0) ---
    gh_lines = gh_text.splitlines()
    assert gh_lines, "workflow 비어있음"
    assert "(blocking-on-pr)" in gh_lines[0], "workflow line 1 에 (blocking-on-pr) 부재: %r" % gh_lines[0]
    assert "(warning mode)" not in gh_lines[0], "workflow line 1 에 stale (warning mode) 잔존"
    assert _stale_workflow_lines(gh_text) == [], "stale warning-tier workflow 라인 잔존(.github): %r" % (
        _stale_workflow_lines(gh_text),
    )
    assert _stale_workflow_lines(tpl_text) == [], "stale warning-tier workflow 라인 잔존(templates): %r" % (
        _stale_workflow_lines(tpl_text),
    )

    # --- POS axis1: lint surface (py + sh enforcement-tier 자기서술 stale 0) ---
    assert _stale_lint_lines(py_text) == [], "lint py 에 stale warning-tier 자기서술 잔존: %r" % (
        _stale_lint_lines(py_text),
    )
    assert _stale_lint_lines(sh_text) == [], "lint sh 에 stale warning-tier 자기서술 잔존: %r" % (
        _stale_lint_lines(sh_text),
    )

    # --- POS axis2: comment step dead-path 부재 (조건에 !cancelled()/failure() 포함) ---
    cond_lines = [ln for ln in gh_lines if "steps.lint.outcome == 'failure'" in ln]
    assert len(cond_lines) >= 1, "comment step 조건 라인 부재"
    for ln in cond_lines:
        assert ("!cancelled()" in ln) or ("failure()" in ln), (
            "comment step 조건이 bare 'steps.lint.outcome == failure' = flip 후 dead-path: %r" % ln
        )

    # --- MUT: stale 'Tier: warning' 주입 → RED ---
    mut_text = gh_text + "\n# Tier: warning (stale mutant)\n"
    mut_bad = _stale_workflow_lines(mut_text)
    assert len(mut_bad) >= 1, "stale 'Tier: warning' 주입 미검출 (predicate vacuous)"
    assert any(m[0] == "Tier: warning" for m in mut_bad), "주입 stale marker 미검출: %r" % (mut_bad,)
