# -*- coding: utf-8 -*-
r"""
tests/scripts/test_decision_record_disposition_deathmarker.py
CFP-2799 — death-marker/amendment 광의 corpus oracle 확장 self-test (§8.C AC ↔ test 매핑).

normative AC(AC-1/2/4/5/6/8/9/11) = pytest `def test_*`(ac-traceability Hop3 tests-root).
declared AC(AC-3/12) = pytest facet + 절차. discriminating mutation-kill(over/under-detect,
amendment_log-off, bare-xref, census-dispatch-off, exclusion-off) 은 CI-run `.sh` 채널
(test_decision-record-disposition-deathmarker.sh) — .py-only born-dormant 회피(#2635/#881).

born-alive: 실 소스 모듈 import·구동 + 실 assertion(any mask 0). anti-overfit: fixture =
대표 literal, 파일 신원 하드코딩 0.
"""
import json
import os
import subprocess
import sys
import tempfile

import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_LIB = os.path.join(_REPO_ROOT, "scripts", "lib")
if _LIB not in sys.path:
    sys.path.insert(0, _LIB)

import dated_block_mapper as dbm  # noqa: E402
import decision_record_disposition as oracle  # noqa: E402
import decision_record_disposition_deathmarker as dm  # noqa: E402
import sweep_executor  # noqa: E402


# ── 대표 fixture (literal 문자열 — 신원 하드코딩 0) ────────────────────────────
_LIVE_DEATH = "이 규칙은 폐기되었으며 더 이상 적용하지 않는다"
_DEATH_EN = "this legacy contract is deprecated and no longer honored"
_HOMONYM_SUNSET = "sunset_justification: 이 게이트는 evidence-gate audit 근거를 요구한다"
_BARE_XREF_ITEM = "- ADR-033"
_FM_KEY = "status: deprecated"

_FM_AMENDMENT_LOG = (
    "---\n"
    "title: t\n"
    "amendment_log:\n"
    "  - entry: x\n"
    "---\n"
    "# Doc\n"
    "\n"
    "## Amendment 1\n"
    "\n"
    "이 개정 라인은 dated ratchet 결정기록이다\n"
)
_FM_SELF_SLUG = (
    "---\n"
    "title: t\n"
    "amendments:\n"
    "  - ADR-127-Amendment-1-CFP-2456\n"
    "---\n"
    "## Amendment 1\n"
    "본문\n"
)
_FM_BARE_XREF = "---\ntitle: t\namendments:\n  - ADR-033\n  - ADR-041\n---\n본문\n"
_FM_DICT_DATE = "---\ntitle: t\namendments:\n  - date: 2026-01-01\n    ref: CFP-1\n---\n본문\n"


def _write(tmp_path, name, text):
    p = os.path.join(str(tmp_path), name)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return p


# ─────────────────────────────────────────────────────────────────────────────
# AC-11 (normative) — bare-ADR-xref → NOT dated (homonym over-detection 방지)
# ─────────────────────────────────────────────────────────────────────────────
def test_bare_xref_not_dated():
    assert dbm._is_bare_xref_amendments(_FM_BARE_XREF) is True
    assert dbm._has_dated_amendments_frontmatter(_FM_BARE_XREF) is False
    assert dbm.dated_line_numbers(_FM_BARE_XREF) == set()
    # positive control: dict+date / self-slug / amendment_log 는 dated
    assert dbm._has_dated_amendments_frontmatter(_FM_DICT_DATE) is True
    assert dbm._has_dated_amendments_frontmatter(_FM_SELF_SLUG) is True
    assert dbm._has_dated_amendments_frontmatter(_FM_AMENDMENT_LOG) is True


def test_dbm_amendment_log_broadens_amendment_region():
    # amendment_log: 문서의 ## Amendment N region 이 dated 로 커버되어야(78 ADR 다수파).
    dated = dbm.dated_line_numbers(_FM_AMENDMENT_LOG)
    lines = _FM_AMENDMENT_LOG.splitlines()
    amd_idx = next(i for i, l in enumerate(lines, 1) if l.startswith("## Amendment"))
    assert amd_idx in dated, "amendment_log 문서의 Amendment region 이 dated 여야 함: %s" % sorted(dated)


# ─────────────────────────────────────────────────────────────────────────────
# candidate predicate — homonym prefilter + self-reflag-exempt
# ─────────────────────────────────────────────────────────────────────────────
def test_deathmarker_candidate_positive():
    assert dm._is_deathmarker_candidate(_LIVE_DEATH) is True
    assert dm._is_deathmarker_candidate(_DEATH_EN) is True


def test_deathmarker_candidate_homonym_reject():
    assert dm._is_deathmarker_candidate(_HOMONYM_SUNSET) is False  # sunset_justification 필드명
    assert dm._is_deathmarker_candidate(_BARE_XREF_ITEM) is False  # bare ADR xref
    assert dm._is_deathmarker_candidate(_FM_KEY) is False          # frontmatter key


def test_self_reflag_exempt():
    marked = _LIVE_DEATH + sweep_executor._DEATH_MARKER
    assert dm._is_deathmarker_candidate(marked) is False  # 마커 보유 → census 후보 아님(§11.6/T2)
    moot = _LIVE_DEATH + sweep_executor._MOOT_MARKER
    assert dm._is_deathmarker_candidate(moot) is False


# ─────────────────────────────────────────────────────────────────────────────
# AC-4 (normative) — 불확실(undated death) → no_action fail-closed
# ─────────────────────────────────────────────────────────────────────────────
def test_uncertain_fail_closed_no_action():
    r = dm.classify_deathmarker(_LIVE_DEATH, dated_context=None)
    assert r["disposition"] == oracle.DISPOSITION_NO_ACTION
    assert r["pl_review"] is True  # 결정 불가 → PL 회부(surface), auto-correct 아님
    assert r["disposition"] in dm.DISPOSITIONS


def test_dated_death_preserved_not_pl_review():
    r = dm.classify_deathmarker(_LIVE_DEATH, dated_context=True)
    assert r["disposition"] == oracle.DISPOSITION_NO_ACTION
    assert r["pl_review"] is False  # dated 이력 안 death = 보존(INV-R2), 회부 불요


# ─────────────────────────────────────────────────────────────────────────────
# AC-1 (normative) — census: 기계 결정가능 분류 or PL-review 버킷 surface
# AC-3 (declared)  — no-blind-apply: pl_review_bucket 존재 + needs_disposition 미투입
# ─────────────────────────────────────────────────────────────────────────────
def test_census_deathmarker_amendment_classify_or_pl_bucket(tmp_path):
    fixture = (
        "# Doc\n\n"
        + _LIVE_DEATH + "\n\n"
        + _HOMONYM_SUNSET + "\n\n"
        + "## 2026-01-01 이력\n\n"
        + "이 블록의 규칙도 폐기되었다\n"
    )
    path = _write(tmp_path, "a.md", fixture)
    provider = dbm.make_dated_provider(str(tmp_path))
    dc = dm.build_domain_classifiers()
    rep = oracle._census_over_files(
        [path], dated_provider=provider, domain_classifiers={"deathmarker": dc["deathmarker"]}
    )
    assert "pl_review_bucket" in rep
    # undated live death → pl_review 버킷; dated 이력 안 death → 보존(버킷 미포함)
    bucket_lines = {e["line"] for e in rep["pl_review_bucket"]}
    live_line = 3
    assert live_line in bucket_lines, "undated death → pl_review 버킷: %s" % rep["pl_review_bucket"]
    # AC-3 no-blind-apply: death domain 은 needs_disposition(blind apply feed) 미투입
    assert rep["needs_disposition"] == [], "death domain blind auto-apply 배선 금지"
    # homonym(sunset_justification) 은 후보 아님 → 버킷에 없음
    homonym_line = 5
    assert homonym_line not in bucket_lines


def test_no_blind_apply_pl_review_bucket_present(tmp_path):
    path = _write(tmp_path, "b.md", "# D\n\n" + _DEATH_EN + "\n")
    dc = dm.build_domain_classifiers()
    rep = oracle._census_over_files([path], domain_classifiers={"deathmarker": dc["deathmarker"]})
    assert isinstance(rep["pl_review_bucket"], list)
    assert len(rep["pl_review_bucket"]) >= 1
    assert rep["needs_disposition"] == []


# ─────────────────────────────────────────────────────────────────────────────
# AC-2 (normative) — INV-R2: dated amendment_log 라인 apply 후 byte-unchanged
# ─────────────────────────────────────────────────────────────────────────────
def test_inv_r2_dated_amendment_log_byte_unchanged(tmp_path):
    path = _write(tmp_path, "adr.md", _FM_AMENDMENT_LOG)
    before = open(path, "rb").read()
    provider = dbm.make_dated_provider(str(tmp_path))
    # cardinal apply pipeline: dated amendment 라인은 tuple 부재 → manifest 진입조차 안 함.
    rep = oracle._census_over_files([path], dated_provider=provider)
    manifest = [{"file": os.path.basename(path), "line": e["line"]}
                for e in rep["needs_disposition"] if "line" in e]
    plan = sweep_executor.plan(manifest, repo_root=str(tmp_path), live_required_contexts={"a"})
    sweep_executor.apply(plan, repo_root=str(tmp_path), live_count=1)
    after = open(path, "rb").read()
    assert before == after, "INV-R2 불가침 — dated amendment_log 라인 byte 위조 금지"


# ─────────────────────────────────────────────────────────────────────────────
# AC-8 (normative) — 멱등: apply 2회차 edit 0
# AC-6 (normative) — exclusion 재처리 0
# ─────────────────────────────────────────────────────────────────────────────
def test_idempotent_apply_second_run_edit0(tmp_path):
    # strip-eligible cardinal 라인(6-tuple 불변 주장, live=7 → strip)
    line = "wrapper 의 required_status_checks contexts 는 6-tuple 로 불변 유지"
    path = _write(tmp_path, "c.md", "# D\n\n" + line + "\n")
    live = {"a", "b", "c", "d", "e", "f", "g"}
    rep = oracle._census_over_files([path], live_required_contexts=live)
    manifest = [{"file": os.path.basename(path), "line": e["line"]}
                for e in rep["needs_disposition"] if "line" in e]
    plan = sweep_executor.plan(manifest, repo_root=str(tmp_path), live_required_contexts=live)
    r1 = sweep_executor.apply(plan, repo_root=str(tmp_path), live_count=7)
    # 2회차: 같은 plan 재실행 → edit 0 (마커/정정 idempotent)
    plan2 = sweep_executor.plan(manifest, repo_root=str(tmp_path), live_required_contexts=live)
    r2 = sweep_executor.apply(plan2, repo_root=str(tmp_path), live_count=7)
    total2 = r2["applied"]["correct"] + r2["applied"]["strip"] + r2["applied"]["delete"]
    assert total2 == 0, "idempotent — 2회차 edit 0 이어야: %s" % r2["applied"]


def test_exclusion_8class_reprocess_edit0(tmp_path):
    # composition root exclusion(--exclude-line) 로 라인 제외 → 재처리 0
    import importlib.util
    sweep_cli = os.path.join(_REPO_ROOT, "scripts", "decision-record-sweep.py")
    line = "wrapper contexts 는 6-tuple 로 불변 유지"
    path = _write(tmp_path, "d.md", "# D\n\n" + line + "\n")
    before = open(path, "rb").read()
    key = "%s:3" % os.path.basename(path)
    rc = subprocess.call(
        [sys.executable, sweep_cli, "--mode", "apply",
         "--live-contexts", "a,b,c,d,e,f,g",
         "--repo-root", str(tmp_path), "--exclude-line", key,
         os.path.basename(path)],
        cwd=str(tmp_path), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    assert rc == 0
    after = open(path, "rb").read()
    assert before == after, "exclusion 라인은 재처리(edit) 0 이어야(AC-6)"


# ─────────────────────────────────────────────────────────────────────────────
# AC-5 (normative) — 재census 결정적 재현(같은 config → 같은 settled-set, drift 0)
# ─────────────────────────────────────────────────────────────────────────────
def test_recensus_settled_manifest_reproducible_drift0(tmp_path):
    fixture = "# D\n\n" + _LIVE_DEATH + "\n\n" + _DEATH_EN + "\n"
    path = _write(tmp_path, "e.md", fixture)
    dc = dm.build_domain_classifiers()
    r1 = oracle._census_over_files([path], domain_classifiers={"deathmarker": dc["deathmarker"]})
    r2 = oracle._census_over_files([path], domain_classifiers={"deathmarker": dc["deathmarker"]})
    key1 = sorted((e["file"], e["line"]) for e in r1["pl_review_bucket"])
    key2 = sorted((e["file"], e["line"]) for e in r2["pl_review_bucket"])
    assert key1 == key2, "재census drift 0(결정적 재현)"


# ─────────────────────────────────────────────────────────────────────────────
# AC-9 (normative) — guard 4-check 통과분만 strip/downgrade (guard-fail → fail-closed skip)
# ─────────────────────────────────────────────────────────────────────────────
def test_guard_4check_pass_only_strip_downgrade(tmp_path):
    line = "wrapper 의 required_status_checks contexts 는 6-tuple 로 불변 유지"
    path = _write(tmp_path, "g.md", "# D\n\n" + line + "\n")
    before = open(path, "rb").read()
    # guard_pass False → 편집 skip(fail-closed, INV-R1)
    plan_fail = [{"file": "g.md", "line": 3, "action": "strip", "guard_pass": False,
                  "disposition": "strip_normativity", "rationale": "x"}]
    r_fail = sweep_executor.apply(plan_fail, repo_root=str(tmp_path), live_count=7)
    assert open(path, "rb").read() == before, "guard-fail → no edit(fail-closed)"
    assert r_fail["applied"]["strip"] == 0
    # guard_pass True → strip 적용(marker append, bytes 보존)
    plan_pass = [{"file": "g.md", "line": 3, "action": "strip", "guard_pass": True,
                  "disposition": "strip_normativity", "rationale": "x"}]
    r_pass = sweep_executor.apply(plan_pass, repo_root=str(tmp_path), live_count=7)
    assert r_pass["applied"]["strip"] == 1
    assert sweep_executor._MOOT_MARKER in open(path, encoding="utf-8").read()


def test_parser_scan_argv_fallback_case_fix(tmp_path):
    """CFP-2799 FIX iter1 (SecurityTestPL P2-② CWE-178): check_parser_scan argv-fallback 가
    lowercased line 에서 대문자 ADR base 를 case-정정해 감지(구 dead-branch 회귀 방지)."""
    import reference_integrity_guard as g
    os.makedirs(os.path.join(str(tmp_path), "scripts"))
    os.makedirs(os.path.join(str(tmp_path), "archive", "adr"))
    with open(os.path.join(str(tmp_path), "archive", "adr", "ADR-127-foo.md"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("# ADR-127\nbody\n")
    with open(os.path.join(str(tmp_path), "scripts", "runner.sh"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("#!/bin/bash\npython tool.py archive/adr/ADR-127-foo.md\n")
    res = g.check_parser_scan({"file": "archive/adr/ADR-127-foo.md"}, str(tmp_path))
    assert res["body_parsed"] is True, "ADR argv 라인 감지(case dead-branch 정정) 실패"


def test_parser_scan_no_redos_bound(tmp_path):
    """CFP-2799 FIX iter1 (SecurityTestPL P2-① CWE-1333): check_parser_scan 가 64KB
    non-ws repeat-anchor corpus 라인에서 bounded(<2.0s) — linear substring(구 `\\S*.*` 제거)."""
    import time
    import reference_integrity_guard as g
    os.makedirs(os.path.join(str(tmp_path), "scripts"))
    os.makedirs(os.path.join(str(tmp_path), "archive", "adr"))
    with open(os.path.join(str(tmp_path), "archive", "adr", "ADR-127-foo.md"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("# ADR-127\nbody\n")
    with open(os.path.join(str(tmp_path), "scripts", "patho.sh"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("python " + "adr-" * 16000 + "\n")
    t0 = time.perf_counter()
    g.check_parser_scan({"file": "archive/adr/ADR-127-foo.md"}, str(tmp_path))
    elapsed = time.perf_counter() - t0
    assert elapsed < 2.0, "check_parser_scan adversarial corpus %.3fs — ReDoS 잔존" % elapsed


def test_guard_index_invariance_byte_identical():
    import reference_integrity_guard as g
    idx = g.build_reference_index(_REPO_ROOT)
    # 실 corpus target 몇 개(§결정 anchor 보유 라인)
    import glob
    targets = []
    for f in sorted(glob.glob(os.path.join(_REPO_ROOT, "archive", "adr", "ADR-13*.md")))[:4]:
        rel = os.path.relpath(f, _REPO_ROOT).replace("\\", "/")
        with open(f, encoding="utf-8") as fh:
            for i, ln in enumerate(fh.read().splitlines(), 1):
                if "§결정" in ln:
                    targets.append({"file": rel, "row": i})
                    break
    assert targets, "샘플 target 확보 실패"
    for t in targets:
        for disp in ("delete", "strip_normativity"):
            g0 = g.run_guard(dict(t), disp, repo_root=_REPO_ROOT)
            g1 = g.run_guard(dict(t), disp, repo_root=_REPO_ROOT, index=idx)
            assert g0["pass"] == g1["pass"]
            assert (g0["checks"]["inbound_scan"]["inbound_count"]
                    == g1["checks"]["inbound_scan"]["inbound_count"])


# ─────────────────────────────────────────────────────────────────────────────
# AC-12 (declared) — classify() core git diff = 0 (additive sibling/module 상속)
# ─────────────────────────────────────────────────────────────────────────────
def test_classify_core_git_diff_zero():
    # origin/main 의 classify() core(def classify → SMOKE_CASES 경계) 와 현재가 byte-identical.
    src = os.path.join("scripts", "lib", "decision_record_disposition.py")
    try:
        base = subprocess.check_output(
            ["git", "show", "origin/main:%s" % src.replace("\\", "/")],
            cwd=_REPO_ROOT, stderr=subprocess.DEVNULL,
        ).decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        pytest.skip("origin/main 조회 불가(오프라인 CI 등): %s" % exc)

    def _extract_classify(text):
        out, capture = [], False
        for ln in text.splitlines():
            if ln.startswith("def classify("):
                capture = True
            if capture:
                out.append(ln)
            if ln.startswith("SMOKE_CASES = ("):
                break
        return "\n".join(out)

    with open(os.path.join(_REPO_ROOT, src), encoding="utf-8") as fh:
        cur = fh.read()
    assert _extract_classify(base) == _extract_classify(cur), \
        "classify() core 는 additive 확장에도 diff=0 이어야(AC-12 비협상)"
