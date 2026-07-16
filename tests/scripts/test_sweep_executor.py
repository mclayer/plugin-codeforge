# -*- coding: utf-8 -*-
"""tests/scripts/test_sweep_executor.py

CFP-2698 / Epic #2696 (canary artifact D6, Story A TOOL ROBUSTENING) — `sweep_executor.py`
(plan → apply 일괄 적용 엔진)의 hermetic TDD self-test.

대상(read-only reference — 본 self-test 는 production 코드를 수정하지 않는다):
  scripts/lib/sweep_executor.py — `plan(manifest, ...)` / `apply(plan_records, ...)`

커버리지(Story CFP-2698 §8 Test Contract):
  ① correct → value-fix (stale `\\d+-tuple` → `<live_count>-tuple`, 나머지 바이트 보존)
  ② strip   → byte-preserving moot-mark append (원본 값 불변 + 마커만 추가)
  ③ delete  → guard-gated: anchorless(§결정/#anchor 없음) delete 는 guard 불통과 →
              apply() 가 strip 으로 자동 downgrade
  ④ no_action → skip(무편집)
  ⑤ idempotency — 재적용 시 추가 편집 0
  ⑥ fail-closed — guard 불통과(orphan external-id) → surfaced 기록 + 무편집
  ⑦ TG-6 — batch-per-file(파일마다 독립 guard 재검증, 1회로 합쳐지지 않음)
  ⑧ TG-7 — AC-5: plan() 산출 레코드는 항상 비어있지 않은 rationale 을 갖는다

anti-overfit(비협상): manifest 는 {file, line} **데이터**로만 다루고, 파일 신원을 엔진 코드에
  하드코딩하지 않는다(엔진 자체) — 본 self-test 의 hermetic fixture 도 장르 exercise 문자열이지
  fixture-신원 암기 검증이 아니다(§10 오라클 axis 자체는 이미 test_decision_record_disposition.py 가
  ablation-kill 로 실증했으므로, 본 파일은 plan/apply 배선(engine wiring) 에 집중한다).

정직 천장(ADR-119): plan/apply 배선 계약(batch-per-file, guard-gate, idempotency, fail-closed)까지
  실증한다. "모든 decision-record 편집을 완전 안전하게 처리한다"는 hard-claim 은 하지 않는다.

import-robust: 파일 위치 기준 상대경로로 scripts/lib 를 sys.path 에 얹어 pytest·직접 python 양쪽 구동.
전부 hermetic tempfile 위에서 구동(live repo tree 비의존, newline="\\n" 고정).
"""

import os
import shutil
import sys
import tempfile

# ── import-robust: 테스트 파일 기준 상대경로로 scripts/lib 를 sys.path 에 삽입 ──
_LIB = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "lib")
sys.path.insert(0, _LIB)

import sweep_executor as sx  # noqa: E402


def _build_repo(files):
    """hermetic temp repo 생성 — {rel_path: content} 를 UTF-8(newline="\\n") 로 기록하고 root 반환."""
    root = tempfile.mkdtemp(prefix="cfp2698_sx_")
    for rel, content in files.items():
        p = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
    return root


def _read(root, rel):
    with open(os.path.join(root, *rel.split("/")), "r", encoding="utf-8") as fh:
        return fh.read()


# ─────────────────────────────────────────────────────────────────────────────
# 대표 fixture (장르 exercise — fixture-신원 하드코딩 0)
#   records_a.md L1 = correct(값-정정) / L2 = no_action(homonym, skip)
#   records_b.md L1 = strip(불변-반증) / L2 = delete 후보(guard 불통과 → strip downgrade)
# ─────────────────────────────────────────────────────────────────────────────
_RECORDS_A = (
    "required contexts MUST remain 6-tuple across the phase-gate 등록\n"
    "성능 metric 3-tuple 은 불변 baseline 으로 유지 (산술 evidence 별개)\n"
)
_RECORDS_B = (
    "wrapper 의 required_status_checks contexts 는 6-tuple 로 불변 유지\n"
    '"legacy-check" 는 phase-gate 의 5-tuple contexts 안에 있었다\n'
)

# 실 SSOT 아님 — live-count=7 threading 대조용 fake context 집합("legacy-check" 는 포함하지 않음).
_FAKE_LIVE_7 = {
    "check-gate", "invariant-check", "ac-traceability-matrix", "deploy-lane-presence",
    "doc-frontmatter-category-test", "doc-schema-check", "doc-section-schema",
}


def _build_main_repo():
    return _build_repo({
        "docs/records_a.md": _RECORDS_A,
        "docs/records_b.md": _RECORDS_B,
    })


def _plan_and_apply(root, *, live_count=7):
    manifest = [
        {"file": "docs/records_a.md", "line": 1},
        {"file": "docs/records_a.md", "line": 2},
        {"file": "docs/records_b.md", "line": 1},
        {"file": "docs/records_b.md", "line": 2},
    ]
    records = sx.plan(
        manifest, repo_root=root, live_required_contexts=_FAKE_LIVE_7, dated_provider=None
    )
    result = sx.apply(records, repo_root=root, live_count=live_count)
    return records, result


# ═════════════════════════════════════════════════════════════════════════════
# plan() — disposition→action 매핑 + AC-5 rationale
# ═════════════════════════════════════════════════════════════════════════════
def test_plan_action_mapping_per_disposition():
    """plan() 이 4 라인 각각을 올바른 action(correct/skip/strip/delete)으로 매핑함을 확인."""
    root = _build_main_repo()
    try:
        manifest = [
            {"file": "docs/records_a.md", "line": 1},
            {"file": "docs/records_a.md", "line": 2},
            {"file": "docs/records_b.md", "line": 1},
            {"file": "docs/records_b.md", "line": 2},
        ]
        records = sx.plan(
            manifest, repo_root=root, live_required_contexts=_FAKE_LIVE_7, dated_provider=None
        )
        by_key = {(r["file"], r["line"]): r for r in records}
        assert by_key[("docs/records_a.md", 1)]["action"] == "correct"
        assert by_key[("docs/records_a.md", 1)]["disposition"] == "correct"
        assert by_key[("docs/records_a.md", 2)]["action"] == "skip"
        assert by_key[("docs/records_a.md", 2)]["disposition"] == "no_action"
        assert by_key[("docs/records_b.md", 1)]["action"] == "strip"
        assert by_key[("docs/records_b.md", 1)]["disposition"] == "strip_normativity"
        assert by_key[("docs/records_b.md", 2)]["action"] == "delete"
        assert by_key[("docs/records_b.md", 2)]["disposition"] == "delete"
        # delete 후보는 anchorless(§결정/#anchor 없음) → guard 불통과(has_semantic=False, DBM-1).
        assert by_key[("docs/records_b.md", 2)]["guard_pass"] is False
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_tg7_ac5_rationale_always_nonempty():
    """TG-7 (AC-5) — plan() 이 산출하는 모든 레코드는 비어있지 않은 rationale 문자열을 갖는다
    (skip/correct/strip/delete 전 action 유형에 대해)."""
    root = _build_main_repo()
    try:
        _, result_records = None, None
        manifest = [
            {"file": "docs/records_a.md", "line": 1},
            {"file": "docs/records_a.md", "line": 2},
            {"file": "docs/records_b.md", "line": 1},
            {"file": "docs/records_b.md", "line": 2},
        ]
        records = sx.plan(
            manifest, repo_root=root, live_required_contexts=_FAKE_LIVE_7, dated_provider=None
        )
        assert len(records) == 4
        assert all(isinstance(r["rationale"], str) and len(r["rationale"]) > 0 for r in records), records
        # action 유형이 최소 3종 이상 섞여 있어야(단일 action 만 비어있지-않음을 우연히 만족한 게 아님).
        actions = {r["action"] for r in records}
        assert len(actions) >= 3, actions
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ═════════════════════════════════════════════════════════════════════════════
# apply() — correct/strip/delete-downgrade/no_action 편집 semantics + TG-6 batch-per-file
# ═════════════════════════════════════════════════════════════════════════════
def test_apply_correct_value_fix_byte_preserving_rest():
    """① correct → stale `6-tuple` 이 `<live_count>-tuple`(7)로 치환되고, 나머지 텍스트는 보존된다."""
    root = _build_main_repo()
    try:
        _records, result = _plan_and_apply(root, live_count=7)
        content = _read(root, "docs/records_a.md")
        assert "7-tuple" in content
        assert "6-tuple" not in content.splitlines()[0]
        assert "required contexts MUST remain 7-tuple across the phase-gate 등록" in content
        assert result["applied"]["correct"] == 1
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_apply_strip_byte_preserving_moot_mark():
    """② strip → 원본 바이트(값 `6-tuple` 포함) 는 그대로 보존되고, 라인 끝에 효력박탈 마커만 append."""
    root = _build_main_repo()
    try:
        _records, result = _plan_and_apply(root, live_count=7)
        content = _read(root, "docs/records_b.md")
        lines = content.splitlines()
        # L1 = strip 대상 — 원본 값(6-tuple) 보존 + 마커 append.
        assert "6-tuple" in lines[0]
        assert sx._MOOT_MARKER.strip() in lines[0]
        assert lines[0].startswith(_RECORDS_B.splitlines()[0])
        assert result["applied"]["strip"] >= 1
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_apply_delete_guard_gated_downgrades_to_strip():
    """③ delete → anchorless(§결정/#anchor 없음) 대상은 guard 불통과(has_semantic=False, DBM-1) →
    apply() 가 삭제 대신 strip(byte-preserving moot-mark)으로 자동 downgrade한다(fail-closed cascade)."""
    root = _build_main_repo()
    try:
        _records, result = _plan_and_apply(root, live_count=7)
        content = _read(root, "docs/records_b.md")
        lines = content.splitlines()
        # L2 (delete 후보)는 삭제되지 않고 여전히 존재 + 원본 텍스트 보존 + 마커 append.
        assert len(lines) == 2, "delete 가 실제 삭제됐다면 라인 수가 줄었어야(그러나 downgrade 되어야 함)"
        assert '"legacy-check"' in lines[1]
        assert "5-tuple" in lines[1]
        assert sx._MOOT_MARKER.strip() in lines[1]
        assert result["applied"]["delete"] == 0
        assert result["applied"]["strip"] == 2  # L1(직접 strip) + L2(delete→strip downgrade)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_apply_no_action_skip_no_edit():
    """④ no_action(homonym) → skip, 무편집. records_a.md L2 원문이 정확히 보존된다."""
    root = _build_main_repo()
    try:
        _records, result = _plan_and_apply(root, live_count=7)
        content = _read(root, "docs/records_a.md")
        lines = content.splitlines()
        assert lines[1] == _RECORDS_A.splitlines()[1]
        # records_a L2(no_action) 만 skip — L1=correct/records_b L1=strip/L2=delete→strip downgrade
        # 이므로 이 4-라인 manifest 안에서 순수 skip 은 정확히 1건.
        assert result["applied"]["skip"] == 1, result["applied"]
    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_tg6_batch_per_file_guard_reverified_independently():
    """TG-6 — apply() 는 파일 단위 batch 로 편집하며, 각 배치마다 독립적으로 guard(구조 무결성) 를
    재검증한다(1회로 뭉뚱그려지지 않음). Positive-control: 2-파일 manifest → batches 길이는 정확히 2
    (파일 수와 일치) — guard 가 파일마다 개별 실행됐음을 실증."""
    root = _build_main_repo()
    try:
        _records, result = _plan_and_apply(root, live_count=7)
        batches = result["batches"]
        assert len(batches) == 2, batches
        files_seen = [b["file"] for b in batches]
        assert files_seen == ["docs/records_a.md", "docs/records_b.md"]
        for b in batches:
            assert "guard_pass" in b
            assert b["guard_pass"] is True  # 두 파일 모두 편집 후에도 구조 무결.
            assert b["edits"] > 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ═════════════════════════════════════════════════════════════════════════════
# ⑤ idempotency — 재적용 시 추가 편집 0
# ═════════════════════════════════════════════════════════════════════════════
def test_idempotency_reapply_zero_additional_edits():
    """⑤ 동일 manifest 로 plan()+apply() 를 재실행하면 추가 편집이 0 이다(재실행 안전) —
    correct(이미 정정됨) / strip·delete-downgrade(이미 마커 있음) 모두 idempotent."""
    root = _build_main_repo()
    try:
        _plan_and_apply(root, live_count=7)  # 1차 적용
        before_a = _read(root, "docs/records_a.md")
        before_b = _read(root, "docs/records_b.md")

        _records2, result2 = _plan_and_apply(root, live_count=7)  # 2차 적용(재실행)

        after_a = _read(root, "docs/records_a.md")
        after_b = _read(root, "docs/records_b.md")
        assert after_a == before_a, "재실행 시 records_a.md 바이트가 변하면 안 됨(idempotency 위반)"
        assert after_b == before_b, "재실행 시 records_b.md 바이트가 변하면 안 됨(idempotency 위반)"
        for b in result2["batches"]:
            assert b["edits"] == 0, "2차 적용은 파일마다 추가 편집이 0 이어야: %s" % result2["batches"]
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ═════════════════════════════════════════════════════════════════════════════
# ⑥ fail-closed — guard 불통과(orphan external-id) → surfaced + 무편집
# ═════════════════════════════════════════════════════════════════════════════
def test_apply_fail_closed_orphan_external_id_surfaces_no_edit():
    """⑥ correct 대상이 orphan external-id(ADR-9999, 실재 파일 없음)를 인용하면 guard 가 external-id
    invariant 위반으로 불통과 → apply() 는 편집하지 않고 surfaced 에 기록한다(fail-closed)."""
    root = _build_repo({
        "docs/failclosed.md":
            "required contexts MUST remain 6-tuple across the phase-gate 등록 (참고 ADR-9999)\n",
    })
    try:
        manifest = [{"file": "docs/failclosed.md", "line": 1}]
        records = sx.plan(manifest, repo_root=root, live_required_contexts=None, dated_provider=None)
        assert records[0]["action"] == "correct"
        assert records[0]["guard_pass"] is False, (
            "orphan ADR-9999 참조는 external-id invariant 위반으로 guard 불통과여야: %s" % records[0]
        )

        result = sx.apply(records, repo_root=root, live_count=7)
        content = _read(root, "docs/failclosed.md")
        assert "6-tuple" in content, "guard 불통과 시 편집 없이 원본 값이 보존돼야"
        assert "7-tuple" not in content
        assert result["applied"]["correct"] == 0
        assert len(result["surfaced"]) == 1
        assert result["surfaced"][0]["file"] == "docs/failclosed.md"
        assert result["surfaced"][0]["line"] == 1
        assert "guard 불통과" in result["surfaced"][0]["reason"]
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
    print("CFP-2698 sweep_executor self-test — %d passed / %d failed / %d total"
          % (passed, failed, passed + failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(_run_all_direct())
