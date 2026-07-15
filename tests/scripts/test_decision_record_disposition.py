# -*- coding: utf-8 -*-
"""tests/scripts/test_decision_record_disposition.py

CFP-2697 / Epic #2696 (canary artifact D6) — decision-record disposition oracle +
reference-integrity guard 의 **Python(pytest) 실현**. 기존 bash self-test
(`test_check-decision-record-disposition.sh`)와 **dual realization**(CFP-2684 .sh + .py 선례):

  - .sh self-test 는 그대로 존치(구동/CI 계약). 본 .py 는 **peer** 로 추가된다.
  - 목적: required `ac-traceability-matrix` 게이트의 Hop3 가 named test 를 Python `ast` 로 resolve
    할 때(오직 `*.py` 스캔, `*.sh` 미스캔) RTM 이 명명한 test 함수가 실재함을 확인 가능케 한다.

두 모듈은 read-only reference — 본 self-test 는 어떤 production 코드도 수정하지 않는다:
  oracle = scripts/lib/decision_record_disposition.py  (classify + 3 ablatable axis fn)
  guard  = scripts/lib/reference_integrity_guard.py    (run_guard 4-check conjunction)

anti-overfit(비협상): fixture 는 대표 literal(장르 exercise)이지 fixture-신원(file==X) 아님.
  oracle 은 라인 FEATURE(referent·tense·cardinal 축)로만 판정 — 본 self-test 도 신원 하드코딩 0.

정직 천장(ADR-119): 축 load-bearing(ablation flip) + 계약 verdict 일치까지 실증한다.
  "oracle 이 모든 실세계 decision-record 를 완전 분류한다"는 hard-claim 은 하지 않는다.

import-robust: 파일 위치 기준 상대경로로 scripts/lib 를 sys.path 에 얹어 pytest·직접 python 양쪽 구동.
guard test 는 전부 hermetic tempfile 위에서 돈다(live repo tree 비의존).
"""

import os
import sys
import shutil
import tempfile

# ── import-robust: 테스트 파일 기준 상대경로로 scripts/lib 를 sys.path 에 삽입 ──
_LIB = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "lib")
sys.path.insert(0, _LIB)
# guard test 는 hermetic temp 을 쓰지만, __file__ 기준 repo_root 도 산출(계약 준수 상수).
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

import decision_record_disposition as m  # noqa: E402
import reference_integrity_guard as g    # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# 대표 literal (장르 exercise — fixture-신원 하드코딩 0). UTF-8 본문에 직접 임베드.
#   ★ 반드시 UTF-8 파일 안 리터럴로 유지 — 셸 heredoc 경유 시 Windows cp949 로 한글 토큰이
#     깨져 cardinal_bound(예 "무변경"/"불변") 매칭이 false 가 된다(회귀 방지 주석).
# ─────────────────────────────────────────────────────────────────────────────
# AC10 phantom-norm/cardinal class — present-normative cardinal embed → correct.
AC10_LINE = "branch protection 6-tuple contexts 무변경"

# P-1/2/3 (positive → correct): referent=bp-context-count ∧ present-normative ∧ cardinal embed.
P1 = "wrapper 의 required_status_checks contexts 는 6-tuple 로 불변 유지"
P2 = "branch protection 6-tuple contexts 무변경 (gate 매핑 무손상)"
P3 = "required contexts MUST remain 6-tuple across the phase-gate 등록"

# N-1 homonym (referent ≠ bp-context-count): metric tuple → no_action.
N1 = "성능 metric 3-tuple 은 불변 baseline 으로 유지 (산술 evidence 별개)"
# N-2 dated history: dated ∧ live= 스냅샷 ∧ HELD → no_action(보존).
N2 = "2026-07-12 당시 required contexts 6-tuple 불변 확정 (live=6-tuple, HELD) 잔존"


def _disp(text, **kw):
    return m.classify(text, **kw)["disposition"]


def _build_repo(files):
    """hermetic temp repo 생성 — {rel_path: content} 를 UTF-8 로 기록하고 root 반환."""
    root = tempfile.mkdtemp(prefix="cfp2697_py_")
    for rel, content in files.items():
        p = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
    return root


# ═════════════════════════════════════════════════════════════════════════════
# oracle — disposition replay (§8.1 Part A 대응, RTM AC10/AC12/AC13/AC14)
# ═════════════════════════════════════════════════════════════════════════════
def test_ac10_phantom_norm_class_detected():
    """AC10 — present-normative cardinal-embed 라인(phantom-norm/cardinal class)이 correct 로 검출."""
    res = m.classify(AC10_LINE)
    assert res["disposition"] == "correct"
    # phantom-norm/cardinal class 근거: referent=bp-context-count ∧ cardinal_bound True.
    assert res["axes"]["referent"] == m.REFERENT_BP_CONTEXT_COUNT
    assert res["axes"]["cardinal_bound"] is True


def test_ac12_oracle_replay_positive():
    """AC12 — P-1/P-2/P-3 대표 literal 이 전부 correct 로 replay(positive oracle)."""
    for label, text in (("P-1", P1), ("P-2", P2), ("P-3", P3)):
        got = _disp(text)
        assert got == "correct", "%s expected correct, got %s" % (label, got)


def test_ac13_homonym_referent_no_action():
    """AC13 — N-1 homonym(metric 3-tuple, referent ≠ bp-context-count) → no_action."""
    res = m.classify(N1)
    assert res["disposition"] == "no_action"
    # referent 축이 bp-context-count 가 아님(동음이의)임을 명시적으로 확인.
    assert res["axes"]["referent"] != m.REFERENT_BP_CONTEXT_COUNT


def test_ac14_dated_history_no_action():
    """AC14 — N-2 dated 이력(live=6-tuple, HELD) → no_action(원문 보존)."""
    res = m.classify(N2)
    assert res["disposition"] == "no_action"
    assert res["axes"]["dated_historical"] is True


# ═════════════════════════════════════════════════════════════════════════════
# mutation-kill — 축 ablation flip (§8.1 Part B 대응, RTM M1/M2/M3)
#   각 축을 ablate 하면 verdict 가 wrong 값으로 flip 함을 assert = 축 load-bearing 실증.
#   ablation 후 반드시 원 함수 restore(try/finally) — 후속 test 오염 0.
# ═════════════════════════════════════════════════════════════════════════════
def test_m1_referent_blind_kill():
    """M1 — axis_referent 를 상시 in-scope 로 ablate 하면 N-1 homonym 이 correct 로 flip(referent 축 load-bearing)."""
    before = _disp(N1)
    assert before == "no_action"
    orig = m.axis_referent
    try:
        m.axis_referent = lambda *a, **k: m.REFERENT_BP_CONTEXT_COUNT
        after = _disp(N1)
    finally:
        m.axis_referent = orig
    assert after == "correct", "referent-blind ablation must flip N-1 to correct, got %s" % after
    # 원복 확인 — 실 axis 로 다시 no_action.
    assert _disp(N1) == "no_action"


def test_m2_tense_blind_kill():
    """M2 — axis_tense 를 상시 not-dated 로 ablate 하면 N-2 dated 가 correct 로 flip(tense 축 load-bearing)."""
    before = _disp(N2)
    assert before == "no_action"
    orig = m.axis_tense
    try:
        m.axis_tense = lambda *a, **k: False
        after = _disp(N2)
    finally:
        m.axis_tense = orig
    assert after == "correct", "tense-blind ablation must flip N-2 to correct, got %s" % after
    assert _disp(N2) == "no_action"


def test_m3_cardinal_blind_kill():
    """M3 — axis_cardinal_bound 를 상시 no-cardinal 로 ablate 하면 P-1/2/3 가 no_action 으로 flip(cardinal 축 load-bearing)."""
    before = {k: _disp(t) for k, t in (("P-1", P1), ("P-2", P2), ("P-3", P3))}
    assert all(v == "correct" for v in before.values())
    orig = m.axis_cardinal_bound
    try:
        m.axis_cardinal_bound = lambda *a, **k: False
        after = {k: _disp(t) for k, t in (("P-1", P1), ("P-2", P2), ("P-3", P3))}
    finally:
        m.axis_cardinal_bound = orig
    for k in ("P-1", "P-2", "P-3"):
        assert after[k] == "no_action", "cardinal-blind must flip %s to no_action, got %s" % (k, after[k])
    # 원복 확인.
    assert _disp(P1) == "correct" and _disp(P2) == "correct" and _disp(P3) == "correct"


# ═════════════════════════════════════════════════════════════════════════════
# guard — reference-integrity 4-check (§8.1 Part C 대응, RTM AC15/AC19/AC11/AC20)
#   전부 hermetic tempfile 위에서 구동(live repo tree 비의존).
# ═════════════════════════════════════════════════════════════════════════════
def test_ac15_guard_edit_external_id_invariant():
    """AC15 — edit(correct) 은 external-id 를 invariant 로 취급: 인용된 external-id 가 resolve 되면 통과,
    orphan(미resolve)이면 실패. required workflow 가 그 id 를 인용함도 확인."""
    root = _build_repo({
        # required-context workflow 가 external-id(ADR-777)를 인용 = 그 id 는 invariant.
        ".github/workflows/phase-gate-mergeable.yml":
            "jobs:\n  check-gate:\n    steps:\n      - run: echo 'cite ADR-777'\n",
        # ADR-777 이 실재 파일로 resolve(참조 orphan 0).
        "archive/adr/ADR-777-canary.md": "# ADR-777\n\n본문.\n",
        # 대상 파일(구조 유효한 markdown).
        "docs/note.md": "# note\n\n- item\n",
    })
    try:
        # (a) external-id 보존(resolvable) → edit 통과.
        ok = g.run_guard(
            {"file": "docs/note.md", "external_ids": ["ADR-777"], "row": None},
            "correct", repo_root=root,
        )
        assert ok["pass"] is True
        assert ok["external_id_invariant"] is True
        # required workflow 가 external-id 를 인용함(=invariant) 을 별도 확인.
        assert ok["checks"]["external_id_scan"]["external_id_cited"] is True

        # (b) external-id orphan(미resolve) → edit 실패 = external-id 를 invariant 로 강제.
        orphan = g.run_guard(
            {"file": "docs/note.md", "external_ids": ["ADR-999"], "row": None},
            "correct", repo_root=root,
        )
        assert orphan["pass"] is False
        assert orphan["external_id_invariant"] is False
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_ac19_guard_delete_conjunction():
    """AC19 — delete 는 4-check 전부(¬parse ∧ inbound=0 ∧ external-id-safe ∧ structure-intact) 일 때만 통과.
    (a) 한 check 위반(external-id cited / inbound>0) → pass False + recommend strip_normativity.
    (b) clean delete → pass True. 4-check conjunction 이 실제로 gate 함을 실증."""
    # (a1) external-id 가 required workflow 에 인용됨 → external_id_safe=False.
    root1 = _build_repo({
        ".github/workflows/phase-gate-mergeable.yml":
            "jobs:\n  check-gate:\n    steps:\n      - run: echo ADR-777\n",
    })
    try:
        r = g.run_guard(
            {"file": "docs/foo.md", "external_ids": ["ADR-777"], "row": None},
            "delete", repo_root=root1,
        )
        assert r["pass"] is False
        assert r.get("recommend") == "strip_normativity"
        assert r["delete_conjunction"]["external_id_safe"] is False
    finally:
        shutil.rmtree(root1, ignore_errors=True)

    # (a2) 다른 곳이 이 row(§결정 42)를 인용 → inbound_count>0 → no_inbound=False.
    root2 = _build_repo({
        "archive/other.md": "참조: 여기 어딘가 §결정 42 를 언급한다\n",
    })
    try:
        r = g.run_guard(
            {"file": "docs/bar.md", "body": "이 문장은 §결정 42 를 인용한다", "row": None},
            "delete", repo_root=root2,
        )
        assert r["pass"] is False
        assert r.get("recommend") == "strip_normativity"
        assert r["delete_conjunction"]["no_inbound"] is False
    finally:
        shutil.rmtree(root2, ignore_errors=True)

    # (b) clean delete — parse 0 ∧ inbound 0 ∧ external-id 0 ∧ structure intact → pass True.
    root3 = _build_repo({
        "docs/keep.md": "unrelated content\n",
    })
    try:
        r = g.run_guard(
            {"file": "docs/clean.md",
             "body": "이 라인은 branch protection 6-tuple 무변경 서술만 있고 외부 id 없음",
             "row": None},
            "delete", repo_root=root3,
        )
        assert r["pass"] is True
        # conjunction 네 갈래 전부 참임을 명시 확인.
        assert r["disposition"] == "delete"
    finally:
        shutil.rmtree(root3, ignore_errors=True)


def test_ac11_mirror_byte_parity():
    """AC11 — mirror-pair byte-parity (positive-control, divergence-kill):
    실제 templates/github-workflows ↔ .github/workflows 미러 쌍으로 검증한다.
    동일 바이트 → parity True, 미러 한쪽 1바이트 변조 → parity False (진짜 divergence 검출).

    ※ FIX-1: 이전 판(templates/a↔templates/b)은 guard 의 `.git` prefix 버그(`.github` 를 삼킴)를
      *우회*하는 hollow 테스트였다. 가드가 `.github/` 를 정확히 포함하도록 정정된 뒤, 본 테스트는
      실제 미러 root(.github/workflows ↔ templates/github-workflows)에서 divergence 를 검출한다."""
    basename = "mirror-parity-probe.yml"
    body = "jobs:\n  x:\n    steps:\n      - run: echo hi\n"
    root = _build_repo({
        ".github/workflows/%s" % basename: body,
        "templates/github-workflows/%s" % basename: body,
    })
    try:
        # 동일 바이트 → parity True. 미러 쌍(.github ↔ templates)이 실제로 pairing 되어야 한다.
        res_eq = g.mirror_pair_byte_parity(basename, root)
        assert res_eq["parity"] is True, res_eq
        pairs = [p for p in res_eq["pairs"]]
        assert len(pairs) == 2, pairs
        # 미러가 정말 .github 와 templates 양쪽을 잡았는지 확인 (버그였으면 .github 누락).
        assert any(".github/workflows/" in p for p in pairs), pairs
        assert any("templates/github-workflows/" in p for p in pairs), pairs

        # .github 쪽 1바이트 변조 주입 → 진짜 divergence → parity False.
        with open(os.path.join(root, ".github", "workflows", basename), "a", encoding="utf-8", newline="\n") as fh:
            fh.write("#")  # 1바이트 추가 (미러 divergence)
        res_ne = g.mirror_pair_byte_parity(basename, root)
        assert res_ne["parity"] is False, res_ne
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_ac20_two_branch_replay():
    """AC20 — 두 disposition branch 모두 재현 가능(deterministic):
    correction-branch 라인 → correct(2회 동일), delete-branch guard → verdict 2회 동일."""
    # correction branch — 2회 replay 안정.
    d1 = _disp(AC10_LINE)
    d2 = _disp(AC10_LINE)
    assert d1 == d2 == "correct"

    # delete branch — hermetic clean delete, 2회 호출 verdict 동일(deterministic).
    root = _build_repo({"docs/keep.md": "unrelated\n"})
    try:
        target = {"file": "docs/clean.md",
                  "body": "branch protection 6-tuple 무변경 서술만, 외부 id 없음",
                  "row": None}
        r1 = g.run_guard(target, "delete", repo_root=root)
        r2 = g.run_guard(target, "delete", repo_root=root)
        assert r1["pass"] == r2["pass"] == True  # noqa: E712 (verdict 동일 + 참임 동시 명시)
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
    print("CFP-2697 D6 .py peer — %d passed / %d failed / %d total"
          % (passed, failed, passed + failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(_run_all_direct())
