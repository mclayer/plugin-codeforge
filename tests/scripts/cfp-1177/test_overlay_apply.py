#!/usr/bin/env python3
# tests/scripts/cfp-1177/test_overlay_apply.py
# CFP-1177 Story-8 — apply_overlay_file TDD Python test helper
#
# ADR-061 정합: 외부 .py 파일 (heredoc-python 0)
# Sandbox: CBL_SKIP_ISSUE_CREATE=1
#
# 사용법:
#   python3 test_overlay_apply.py <walk_plan_dir> <tc_name>
#
# TC 목록:
#   prereq_apply_overlay_file   — apply_overlay_file 함수 존재 확인 (RED 시 실패)
#   prereq_overlay_result       — OverlayApplyResult dataclass 존재 확인 (RED 시 실패)
#   tc4_dataclass_fields        — OverlayApplyResult 5 필드 존재
#   tc4b_frozen                 — OverlayApplyResult frozen 검증
#   tc1_marker_inner            — MARKER_VALID — marker 안 wrapper wins
#   tc1b_marker_outer           — MARKER_VALID — marker 밖 consumer preserve
#   tc1c_integrity_ok           — MARKER_VALID — integrity_ok=True, loss_occurred=False
#   tc2_wholesale               — MARKER_NONE — wholesale wrapper mirror
#   tc2b_loss_report            — MARKER_NONE — loss_occurred=True, loss_report non-empty
#   tc2c_integrity_na           — MARKER_NONE — integrity_ok=True (N/A path)
#   tc6_merged_equals_wrapper   — MARKER_NONE merged_content = wrapper_content
#   tc3_roundtrip               — MARKER_VALID outside-preservation round-trip (discriminating)
#   tc3b_violation_reason       — MARKER_VALID integrity_violation_reason='' 정상 경로
#   tc8_integrity_fallback      — integrity_ok=False 경로 consumer fallback
#   tc5_dual_invariant          — MARKER_VALID loss_occurred=False + integrity_ok=True
#   tc7_signature               — base_content 파라미터 시그니처 호환
#   tc7b_unconditional_wrapper  — base_content by-design unconditional wrapper wins

import os
import sys

os.environ.setdefault("CBL_SKIP_ISSUE_CREATE", "1")


def load_module(walk_plan_dir: str):
    """walk_plan.py 를 sys.path 방식으로 임포트 (Python 3.14 호환)."""
    abs_dir = os.path.abspath(walk_plan_dir)
    if abs_dir not in sys.path:
        sys.path.insert(0, abs_dir)
    import walk_plan as mod
    return mod


def _run_tc(mod, tc_name: str) -> None:
    """지정된 TC 실행 — 실패 시 SystemExit(1) + 메시지."""

    # ── PREREQ ──────────────────────────────────────────────────────────────
    if tc_name == "prereq_apply_overlay_file":
        assert hasattr(mod, "apply_overlay_file"), \
            "apply_overlay_file 함수 미존재 — RED phase"
        print("PASS: apply_overlay_file 존재 확인")

    elif tc_name == "prereq_overlay_result":
        assert hasattr(mod, "OverlayApplyResult"), \
            "OverlayApplyResult dataclass 미존재 — RED phase"
        print("PASS: OverlayApplyResult 존재 확인")

    # ── TC-4: dataclass 5 필드 ──────────────────────────────────────────────
    elif tc_name == "tc4_dataclass_fields":
        import dataclasses
        R = mod.OverlayApplyResult
        fields = {f.name for f in dataclasses.fields(R)}
        for expected in ("merged_content", "loss_occurred", "loss_report",
                         "integrity_ok", "integrity_violation_reason"):
            assert expected in fields, f"{expected} 필드 없음. fields={fields}"
        assert "unknown_field_xyz" not in fields
        print("PASS TC-4: OverlayApplyResult 5 필드 확인")

    elif tc_name == "tc4b_frozen":
        R = mod.OverlayApplyResult
        instance = R(
            merged_content="test",
            loss_occurred=False,
            loss_report="",
            integrity_ok=True,
            integrity_violation_reason=""
        )
        try:
            instance.merged_content = "mutate"
            raise AssertionError("frozen dataclass 가 아님 — 돌연변이 허용됨")
        except Exception as e:
            if isinstance(e, AssertionError):
                raise
            print(f"PASS TC-4b: frozen 확인 ({type(e).__name__})")

    # ── TC-1: MARKER_VALID ──────────────────────────────────────────────────
    elif tc_name == "tc1_marker_inner":
        consumer = (
            "consumer-header: true\n"
            "# BEGIN wrapper-managed\n"
            "OLD_WRAPPER_CONTENT=old\n"
            "# END wrapper-managed\n"
            "consumer-footer: true"
        )
        wrapper = (
            "# BEGIN wrapper-managed\n"
            "NEW_WRAPPER_CONTENT=new\n"
            "# END wrapper-managed"
        )
        result = mod.apply_overlay_file(wrapper, consumer, base_content="")
        assert "NEW_WRAPPER_CONTENT=new" in result.merged_content, \
            f"marker 안 wrapper content 없음: {result.merged_content!r}"
        assert "OLD_WRAPPER_CONTENT=old" not in result.merged_content, \
            f"구 wrapper 내용 잔존: {result.merged_content!r}"
        print("PASS TC-1: marker 안 wrapper wins 확인")

    elif tc_name == "tc1b_marker_outer":
        consumer = (
            "consumer-header: true\n"
            "consumer-custom-setting: preserved\n"
            "# BEGIN wrapper-managed\n"
            "OLD_WRAPPER_CONTENT=old\n"
            "# END wrapper-managed\n"
            "consumer-footer: also-preserved"
        )
        wrapper = (
            "# BEGIN wrapper-managed\n"
            "NEW_WRAPPER_CONTENT=new\n"
            "# END wrapper-managed"
        )
        result = mod.apply_overlay_file(wrapper, consumer, base_content="")
        assert "consumer-header: true" in result.merged_content, \
            f"consumer header 유실: {result.merged_content!r}"
        assert "consumer-custom-setting: preserved" in result.merged_content, \
            f"consumer custom-setting 유실: {result.merged_content!r}"
        assert "consumer-footer: also-preserved" in result.merged_content, \
            f"consumer footer 유실: {result.merged_content!r}"
        print("PASS TC-1b: marker 밖 consumer preserve 확인")

    elif tc_name == "tc1c_integrity_ok":
        consumer = (
            "header: kept\n"
            "# BEGIN wrapper-managed\n"
            "inner: old\n"
            "# END wrapper-managed\n"
            "footer: kept"
        )
        wrapper = (
            "# BEGIN wrapper-managed\n"
            "inner: new\n"
            "# END wrapper-managed"
        )
        result = mod.apply_overlay_file(wrapper, consumer, base_content="")
        assert result.integrity_ok is True, \
            f"integrity_ok 기대 True, 실제 {result.integrity_ok}"
        assert result.loss_occurred is False, \
            f"loss_occurred 기대 False, 실제 {result.loss_occurred}"
        assert result.integrity_violation_reason == "", \
            f"integrity_violation_reason 기대 '', 실제 {result.integrity_violation_reason!r}"
        print("PASS TC-1c: integrity_ok=True, loss_occurred=False 확인")

    # ── TC-2: MARKER_NONE ───────────────────────────────────────────────────
    elif tc_name == "tc2_wholesale":
        consumer = "consumer-only-setting: value\nno-marker-here: true"
        wrapper = "wrapper-canonical: content\nmore-wrapper-content: here"
        result = mod.apply_overlay_file(wrapper, consumer, base_content="")
        assert result.merged_content == wrapper, \
            f"wholesale mirror 실패: 기대 {wrapper!r}, 실제 {result.merged_content!r}"
        print("PASS TC-2: wholesale mirror 확인")

    elif tc_name == "tc2b_loss_report":
        consumer = "no-marker-consumer: setting"
        wrapper = "wrapper-ssot: content"
        result = mod.apply_overlay_file(wrapper, consumer, base_content="")
        assert result.loss_occurred is True, \
            f"loss_occurred 기대 True, 실제 {result.loss_occurred}"
        assert len(result.loss_report) > 0, \
            "loss_report 비어 있음 (silent overwrite 금지 위반)"
        assert ("MARKER_NONE" in result.loss_report or
                "marker" in result.loss_report.lower()), \
            f"loss_report 에 marker 관련 내용 없음: {result.loss_report!r}"
        print("PASS TC-2b: loss_occurred=True, loss_report non-empty 확인")

    elif tc_name == "tc2c_integrity_na":
        consumer = "no-marker-consumer: setting"
        wrapper = "wrapper-ssot: content"
        result = mod.apply_overlay_file(wrapper, consumer, base_content="")
        assert result.integrity_ok is True, \
            f"MARKER_NONE 경로 integrity_ok 기대 True, 실제 {result.integrity_ok}"
        print("PASS TC-2c: MARKER_NONE integrity_ok=True 확인")

    # ── TC-6: merged == wrapper ─────────────────────────────────────────────
    elif tc_name == "tc6_merged_equals_wrapper":
        wrapper = "# canonical wrapper content\nkey: value\nother: line\n"
        consumer = "custom: consumer-only\n"
        result = mod.apply_overlay_file(wrapper, consumer)
        assert result.merged_content == wrapper, \
            f"merged_content != wrapper_content. 기대={wrapper!r}, 실제={result.merged_content!r}"
        assert "consumer-only" not in result.merged_content, \
            f"consumer-only 내용이 wholesale merge 에 잔존: {result.merged_content!r}"
        print("PASS TC-6: merged_content == wrapper_content 확인")

    # ── TC-3: round-trip integrity ──────────────────────────────────────────
    elif tc_name == "tc3_roundtrip":
        consumer = (
            "before-section: value1\n"
            "before-section-2: value2\n"
            "# BEGIN wrapper-managed\n"
            "inner-old: old-content\n"
            "more-inner: also-old\n"
            "# END wrapper-managed\n"
            "after-section: value3\n"
            "after-section-2: value4"
        )
        wrapper = (
            "# BEGIN wrapper-managed\n"
            "inner-new: new-content\n"
            "more-inner: also-new\n"
            "# END wrapper-managed"
        )
        result = mod.apply_overlay_file(wrapper, consumer, base_content="")
        merged_before, merged_after = mod._split_consumer_outer(result.merged_content)
        consumer_before, consumer_after = mod._split_consumer_outer(consumer)
        assert merged_before == consumer_before, \
            f"before 영역 불일치:\n기대={consumer_before!r}\n실제={merged_before!r}"
        assert merged_after == consumer_after, \
            f"after 영역 불일치:\n기대={consumer_after!r}\n실제={merged_after!r}"
        assert result.integrity_ok is True, \
            f"integrity_ok 기대 True, 실제 {result.integrity_ok}"
        print("PASS TC-3: outside-preservation round-trip byte-identical 확인")

    elif tc_name == "tc3b_violation_reason":
        consumer = (
            "section-a: keep\n"
            "# BEGIN wrapper-managed\n"
            "managed: old\n"
            "# END wrapper-managed\n"
            "section-b: keep"
        )
        wrapper = (
            "# BEGIN wrapper-managed\n"
            "managed: new\n"
            "# END wrapper-managed"
        )
        result = mod.apply_overlay_file(wrapper, consumer)
        assert result.integrity_violation_reason == "", \
            f"정상 경로 integrity_violation_reason 기대 '', 실제 {result.integrity_violation_reason!r}"
        print("PASS TC-3b: integrity_violation_reason='' 확인")

    # ── TC-8: integrity_ok=False abort-before-touch ─────────────────────────
    elif tc_name == "tc8_integrity_fallback":
        _original_merge = mod.merge_with_marker

        def _corrupt_merge(base_content, wrapper_content, consumer_content):
            merged, loss, report = _original_merge(
                base_content, wrapper_content, consumer_content)
            # outside 를 corrupted 로 교체하여 integrity check 실패 유도
            corrupted = merged.replace(
                "consumer-before: kept", "CORRUPTED-OUTSIDE: injected")
            return corrupted, loss, report

        mod.merge_with_marker = _corrupt_merge

        consumer = (
            "consumer-before: kept\n"
            "# BEGIN wrapper-managed\n"
            "inner: old\n"
            "# END wrapper-managed\n"
            "consumer-after: kept"
        )
        wrapper = (
            "# BEGIN wrapper-managed\n"
            "inner: new\n"
            "# END wrapper-managed"
        )

        try:
            result = mod.apply_overlay_file(wrapper, consumer, base_content="")
            if result.integrity_ok is False:
                # abort-before-touch: consumer_content fallback
                assert result.merged_content == consumer, (
                    "integrity violation consumer fallback fail: "
                    "expected consumer, got: " + repr(result.merged_content[:80])
                )
                assert len(result.integrity_violation_reason) > 0, \
                    "integrity_violation_reason empty (violation reason required)"
                print("PASS TC-8: integrity_ok=False path -- consumer fallback OK")
            else:
                # _corrupt_merge 가 outside 를 실제로 바꾸지 않았는지 재확인
                merged_before, merged_after = mod._split_consumer_outer(
                    result.merged_content)
                consumer_before, consumer_after = mod._split_consumer_outer(consumer)
                if merged_before == consumer_before and merged_after == consumer_after:
                    print("PASS TC-8 INFO: corrupt in marker-inside only, outside OK")
                else:
                    raise AssertionError(
                        "integrity check fail: outside corrupted but integrity_ok=True. "
                        "merged_before=" + repr(merged_before[:60]) +
                        " vs consumer_before=" + repr(consumer_before[:60])
                    )
        finally:
            mod.merge_with_marker = _original_merge

    # ── TC-5: 동시 만족 ─────────────────────────────────────────────────────
    elif tc_name == "tc5_dual_invariant":
        consumer = (
            "prefix: line\n"
            "# BEGIN wrapper-managed\n"
            "managed: old-v1\n"
            "# END wrapper-managed\n"
            "suffix: line"
        )
        wrapper = (
            "# BEGIN wrapper-managed\n"
            "managed: new-v2\n"
            "# END wrapper-managed"
        )
        result = mod.apply_overlay_file(
            wrapper, consumer, base_content="previous-base-content")
        assert result.loss_occurred is False, \
            f"loss_occurred 기대 False, 실제 {result.loss_occurred}"
        assert result.integrity_ok is True, \
            f"integrity_ok 기대 True, 실제 {result.integrity_ok}"
        assert "managed: new-v2" in result.merged_content, \
            f"새 inner content 없음: {result.merged_content!r}"
        print("PASS TC-5: loss_occurred=False + integrity_ok=True 동시 만족")

    # ── TC-7: 시그니처 호환 ─────────────────────────────────────────────────
    elif tc_name == "tc7_signature":
        import inspect
        sig = inspect.signature(mod.apply_overlay_file)
        params = sig.parameters
        for p in ("wrapper_content", "consumer_content", "base_content"):
            assert p in params, f"{p} 파라미터 없음. params={list(params)}"
        base_default = params["base_content"].default
        assert base_default == "", \
            f"base_content 기본값 기대 '', 실제 {base_default!r}"
        # 기본값으로 호출 가능 확인
        c = "# BEGIN wrapper-managed\ninner: old\n# END wrapper-managed"
        w = "# BEGIN wrapper-managed\ninner: new\n# END wrapper-managed"
        result = mod.apply_overlay_file(w, c)
        assert result.loss_occurred is False
        print("PASS TC-7: base_content 파라미터 시그니처 호환 확인")

    elif tc_name == "tc7b_unconditional_wrapper":
        consumer = (
            "header: kept\n"
            "# BEGIN wrapper-managed\n"
            "inner: old\n"
            "# END wrapper-managed\n"
            "footer: kept"
        )
        wrapper = (
            "# BEGIN wrapper-managed\n"
            "inner: new\n"
            "# END wrapper-managed"
        )
        r1 = mod.apply_overlay_file(wrapper, consumer, base_content="")
        r2 = mod.apply_overlay_file(
            wrapper, consumer, base_content="completely-different-base")
        assert r1.merged_content == r2.merged_content, \
            "base_content 값에 따라 결과가 달라짐 — unconditional wrapper wins 위반"
        print("PASS TC-7b: base_content by-design unconditional wrapper wins 확인")

    else:
        print(f"UNKNOWN TC: {tc_name}", file=sys.stderr)
        sys.exit(2)


def main():
    if len(sys.argv) < 3:
        print(f"사용법: {sys.argv[0]} <walk_plan_dir> <tc_name>", file=sys.stderr)
        sys.exit(2)
    walk_plan_dir = sys.argv[1]
    tc_name = sys.argv[2]

    try:
        mod = load_module(walk_plan_dir)
    except Exception as e:
        print(f"FAIL: walk_plan.py 로드 실패 — {e}", file=sys.stderr)
        sys.exit(1)

    try:
        _run_tc(mod, tc_name)
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
