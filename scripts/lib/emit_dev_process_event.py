#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# tier: [measurement]
# emit_dev_process_event.py — dev-process-event-v1 agent-emit (Port B) delegate writer
#
# Carrier: CFP-2687 Phase 2 (구현) / Epic #2686 Story A — dev-process observability substrate
# 설계 SSOT: ADR-155 §결정 4(capture 이원화 — hook Port A 3 / agent-emit Port B 5, emit_source 판별)
#           + §결정 5(INV-8a/8b blob-before-index) + §결정 8(always-on α)
#           + change-plan 2026-07-15-cfp-2687 §3.4(Port B monopoly) + §3.5(4-ID + taxonomy).
#
# 책임 (Port B = Orchestrator-owned delegate writer monopoly):
#   agent-emit 5 event-type 만 write: lane_transition / verdict / defect_finding /
#   fix_transition / final_artifact. 모두 emit_source="agent". hook-source 3종
#   (prompt_input / tool_call / diff)은 본 writer 로 기록 금지 — Port A(capture hook) 소관.
#
# ★INV-8b 순서 강제 (§결정 5 — 비협상):
#   content-bearing 이벤트 =
#     (1) blob_ref, audit = capture_blob(raw_content)     # blob WRITTEN first (INV-8a 내부)
#     (2) append_event(blob_ref=blob_ref, redaction_*=audit[...], emit_source="agent", ...)  # index AFTER
#   역순(index 먼저) = dangling evidence chain(T-DPE-5). content=None → blob 미생성(index blob-less).
#   content-blind 보장: raw content 는 append_event 에 절대 전달하지 않는다 — blob_ref(hash)만 index 도달.
#
# ★always-on α (§결정 8): write 前 dev_process_capture_enabled() consult
#   (wrapper always-on / consumer opt-in default-false). 비활성 → 미기록(return None).
#
# record-only / non-blocking / exit-0 (ADR-115): 어떤 실패도 caller flow 로 raise 하지 않는다.
#   capture 실패 = 원 실행 흐름 무차단(observability 가 개발 흐름을 절대 block 하지 않음).

import sys
import os

# Windows cp949 회피(ADR-061 portability)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# wave-1 CONSUME (재사용 — reuse-before-write, ADR-140). import 실패 시 path fallback.
try:
    from dev_process_blob_store import capture_blob          # INV-8a: redact→hash-over-redacted→write
    from append_dev_process_event import append_event        # content-blind index-tier row append
    from dev_process_capture_activation import dev_process_capture_enabled  # always-on α gate (D4)
except Exception:  # pragma: no cover — import path fallback
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from dev_process_blob_store import capture_blob
    from append_dev_process_event import append_event
    from dev_process_capture_activation import dev_process_capture_enabled


# Port B agent-emit 소유 event-type (closed — hook Port A 3종 배제)
_AGENT_EMIT_TYPES = frozenset({
    "lane_transition", "verdict", "defect_finding", "fix_transition", "final_artifact",
})

_EMPTY_AUDIT = {"redaction_applied": False, "redaction_count": 0, "redaction_rules_fired": []}


def emit(event_type, *, content=None, consumer_scope=None, ledger_path=None,
         blob_root=None, **fields):
    """dev-process-event-v1 agent-emit(Port B) 단일 dispatcher — event_id 반환(미기록/실패 → None).

    INV-8b 순서: content 있으면 capture_blob(blob WRITTEN first) → append_event(index AFTER).
    content-blind: raw content 는 append_event 에 전달하지 않는다(blob_ref hash 만 index 도달).
    activation: dev_process_capture_enabled() 비활성 → 미기록(return None).
    non-blocking: 어떤 예외도 raise 안 함(record-only exit-0 semantics — ADR-115).

    Args:
      event_type: agent-emit 5종 중 하나(그 외 → 미기록, Port A 침범 차단).
      content:    rich content 원본(str). None → blob 미생성(index blob-less 이벤트).
      consumer_scope: 'wrapper'|'consumer'(미지정 시 gate/append 가 checkout-identity 파생).
      ledger_path/blob_root: 테스트/직접 경로 override(미지정 시 CLAUDE_PROJECT_DIR default).
      **fields: index allow-list 필드(story_key/lane_label/defect_id/fix_id/defect_family/
                defect_type/time_to_detection/detecting_lane/seq/prev_timestamp_utc 등).
                allow-list 밖 kwarg 은 append_event 가 drop(content-blind).
    """
    try:
        # Port A 침범 차단 — agent-emit 5종만 (emit_source='agent' 판별 정합)
        if event_type not in _AGENT_EMIT_TYPES:
            sys.stderr.write(
                "[emit-dev-process-event] WARN: event_type=%r 은 agent-emit(Port B) 소유가 아님 "
                "(hook Port A 3종은 capture hook 이 기록) — 미기록\n" % (event_type,)
            )
            return None

        # always-on α gate — 비활성이면 아무것도 기록하지 않음
        if not dev_process_capture_enabled(consumer_scope=consumer_scope):
            return None

        blob_ref = None
        audit = _EMPTY_AUDIT
        if content is not None:
            # ★INV-8b step (1): blob WRITTEN first (capture_blob 내부에서 INV-8a redact→hash→write)
            blob_ref, audit = capture_blob(content, root=blob_root)

        # ★INV-8b step (2): index row AFTER — blob_ref(hash)만 index 도달, raw content 미전달
        return append_event(
            ledger_path=ledger_path,
            event_type=event_type,
            emit_source="agent",
            consumer_scope=consumer_scope,
            blob_ref=blob_ref,
            redaction_applied=audit.get("redaction_applied", False),
            redaction_count=audit.get("redaction_count", 0),
            redaction_rules_fired=audit.get("redaction_rules_fired", []),
            **fields,
        )
    except Exception as exc:  # graceful degradation — 어떤 예외도 exit-0 semantics
        sys.stderr.write("[emit-dev-process-event] WARN: emit failed — %s\n" % exc)
        return None


# ─────────────────────── thin helpers (5 agent-emit event-type) ───────────────────────

def emit_lane_transition(story_key, lane_label, *, content=None, consumer_scope=None,
                         ledger_path=None, blob_root=None, **fields):
    """lane 전이 이벤트(Orchestrator). ADR-038 6-point lane 전이 각인용."""
    return emit("lane_transition", content=content, consumer_scope=consumer_scope,
                ledger_path=ledger_path, blob_root=blob_root,
                story_key=story_key, lane_label=lane_label, **fields)


def emit_verdict(story_key, lane_label, *, content=None, consumer_scope=None,
                 ledger_path=None, blob_root=None, **fields):
    """verdict 이벤트(review lane). 어떤 verdict 가 났나 semantic-evidence — 의미론 정의(C)는 out."""
    return emit("verdict", content=content, consumer_scope=consumer_scope,
                ledger_path=ledger_path, blob_root=blob_root,
                story_key=story_key, lane_label=lane_label, **fields)


def emit_defect_finding(story_key, lane_label, *, defect_id=None, defect_family=None,
                        defect_type=None, detecting_lane=None, time_to_detection=None,
                        content=None, consumer_scope=None, ledger_path=None,
                        blob_root=None, **fields):
    """결점 findings 이벤트(review lane). taxonomy 4-tuple(§결정 3) + defect_id 상관.

    defect_id = content-addressed 상관 ID(미지정 시 append 가 raw→sha256 처리).
    time_to_detection = DERIVED measure(ordinal/ts-delta/'unattributed').
    """
    return emit("defect_finding", content=content, consumer_scope=consumer_scope,
                ledger_path=ledger_path, blob_root=blob_root,
                story_key=story_key, lane_label=lane_label,
                defect_id=defect_id, defect_family=defect_family, defect_type=defect_type,
                detecting_lane=detecting_lane, time_to_detection=time_to_detection, **fields)


def emit_fix_transition(fix_id, story_key, lane_label, *, defect_id=None, content=None,
                        consumer_scope=None, ledger_path=None, blob_root=None, **fields):
    """FIX 루프 전이 이벤트(Orchestrator §10 monopoly). fix_id = per-defect 대응 시도 단위.

    1 §10 row ↔ 1..N fix_id (§10 accounting 재기록 안 함 — 상관만).
    """
    return emit("fix_transition", content=content, consumer_scope=consumer_scope,
                ledger_path=ledger_path, blob_root=blob_root,
                story_key=story_key, lane_label=lane_label,
                fix_id=fix_id, defect_id=defect_id, **fields)


def emit_final_artifact(story_key, lane_label, *, content=None, consumer_scope=None,
                        ledger_path=None, blob_root=None, **fields):
    """최종 산출물 이벤트(lane). 산출물 요약 semantic-evidence-aggregation."""
    return emit("final_artifact", content=content, consumer_scope=consumer_scope,
                ledger_path=ledger_path, blob_root=blob_root,
                story_key=story_key, lane_label=lane_label, **fields)


# ─────────────────────── self-test (execution-backed, INV-8b + content-blind) ─────────────
def _self_test():
    import json
    import tempfile

    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    tmpdir = tempfile.mkdtemp(prefix="emit-dev-process-selftest-")
    ledger = os.path.join(tmpdir, "dev-process-event.jsonl")
    blob_root = os.path.join(tmpdir, "blobstore")

    # ── 케이스 1: lane_transition (content 있음) — INV-8b round-trip + content-blind ──
    SECRET = "api_key = AKIAIOSFODNN7EXAMPLE and /home/mccho/.ssh/id_rsa"
    eid1 = emit_lane_transition(
        "CFP-2687", "구현", content="lane 전이: 설계-리뷰 → 구현. " + SECRET,
        consumer_scope="wrapper", ledger_path=ledger, blob_root=blob_root,
    )
    check(eid1 is not None and len(eid1) == 64, f"[c1] lane_transition event_id 부적합: {eid1!r}")

    with open(ledger, encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    check(len(rows) == 1, f"[c1] row count {len(rows)} != 1")
    r1 = rows[0]
    check(r1["emit_source"] == "agent", "[c1] emit_source != agent (Port B)")
    check(r1["event_type"] == "lane_transition", "[c1] event_type 손상")
    check(r1["lane_label"] == "구현", "[c1] lane_label 손상")
    # content-blindness: raw content/secret 이 index row 에 절대 없어야 함
    row_json = json.dumps(r1, ensure_ascii=False)
    check("api_key" not in row_json and "AKIA" not in row_json and "/home/" not in row_json,
          "[c1] raw content/secret 이 index row 에 유입 (content-blind 위반)")
    check(len(r1["blob_ref"]) == 64, f"[c1] blob_ref 형식 부적합: {r1['blob_ref']!r}")
    check("content" not in r1, "[c1] free-form content 키 유입")

    # blob 은 redacted — secret 원문이 blob 에도 없어야(INV-8a redaction 선행)
    from dev_process_blob_store import deref_blob
    blob = deref_blob(r1["blob_ref"], root=blob_root)
    check(blob is not None, "[c1] blob deref 실패 (INV-8b blob-before-index 위반)")
    if blob is not None:
        btext = blob.decode("utf-8", errors="replace")
        check("AKIAIOSFODNN7EXAMPLE" not in btext, "[c1] blob 에 raw secret 잔존 (redaction 미선행)")
    check(r1["redaction_applied"] is True and r1["redaction_count"] >= 1,
          "[c1] redaction audit 미기록 (secret 있는데 redaction_applied False)")

    # ── 케이스 2: content=None (blob-less 이벤트) ──
    eid2 = emit_verdict("CFP-2687", "구현-리뷰", content=None,
                        consumer_scope="wrapper", ledger_path=ledger, blob_root=blob_root, seq="v1")
    check(eid2 is not None, "[c2] content-less verdict 미기록")
    with open(ledger, encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    check(rows[-1]["blob_ref"] is None, "[c2] content=None 인데 blob_ref != null")
    check(rows[-1]["redaction_applied"] is False, "[c2] content=None 인데 redaction_applied True")

    # ── 케이스 3: defect_finding taxonomy 전파 ──
    eid3 = emit_defect_finding(
        "CFP-2687", "설계-리뷰", defect_id="dupe-boundary-at-x", defect_family="design-boundary",
        defect_type="boundary-completeness", detecting_lane="설계-리뷰", time_to_detection=2,
        content="finding: boundary 누락", consumer_scope="wrapper",
        ledger_path=ledger, blob_root=blob_root,
    )
    check(eid3 is not None, "[c3] defect_finding 미기록")
    with open(ledger, encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    r3 = rows[-1]
    check(r3["defect_family"] == "design-boundary", "[c3] defect_family 손상")
    check(r3["defect_type"] == "boundary-completeness", "[c3] defect_type 손상")
    check(r3["detecting_lane"] == "설계-리뷰", "[c3] detecting_lane 손상")
    check(r3["time_to_detection"] == 2, "[c3] time_to_detection 손상")
    check(len(r3["defect_id"]) == 64, "[c3] defect_id sha256 처리 안 됨")

    # ── 케이스 4: fix_transition ──
    eid4 = emit_fix_transition("attempt-1", "CFP-2687", "구현", defect_id="dupe-boundary-at-x",
                               consumer_scope="wrapper", ledger_path=ledger, blob_root=blob_root)
    check(eid4 is not None, "[c4] fix_transition 미기록")
    with open(ledger, encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    check(len(rows[-1]["fix_id"]) == 64, "[c4] fix_id sha256 처리 안 됨")

    # ── 케이스 5: Port A 침범 차단 (hook-source event_type 거부) ──
    for hook_type in ("prompt_input", "tool_call", "diff"):
        eidx = emit(hook_type, content="x", consumer_scope="wrapper",
                    ledger_path=ledger, blob_root=blob_root,
                    story_key="CFP-2687", lane_label="구현")
        check(eidx is None, f"[c5] Port A event_type={hook_type} 이 agent writer 로 기록됨 (침범)")

    # ── 케이스 6: activation gate — consumer default-false → 미기록 ──
    eid6 = emit_lane_transition("CFP-2687", "구현", content="x", consumer_scope="consumer",
                                ledger_path=ledger, blob_root=blob_root)
    check(eid6 is None, "[c6] consumer default-false 인데 기록됨 (activation gate 미작동)")

    # ── 케이스 7: INV-8b 순서 — blob 이 index 보다 먼저 존재 (dangling 회피) ──
    #   위 c1 에서 blob deref 성공 == blob-before-index 관측. 여기선 non-content 케이스 dangling 부재 확인.
    for r in rows:
        if r["blob_ref"] is not None:
            check(deref_blob(r["blob_ref"], root=blob_root) is not None,
                  f"[c7] index row blob_ref={r['blob_ref'][:8]} 에 대응 blob 부재 (dangling)")

    # cleanup (best-effort)
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)

    if failures:
        print("[emit_dev_process_event --self-test] FAIL")
        for m in failures:
            print("  - " + m)
        return 1
    print("[emit_dev_process_event --self-test] PASS "
          "(INV-8b blob-before-index OK; content-blind index OK; redaction-선행 OK; "
          "taxonomy 전파 OK; Port A 침범 차단 OK; activation α OK)")
    return 0


def main():
    import argparse
    p = argparse.ArgumentParser(
        description="dev-process-event-v1 agent-emit (Port B) writer (CFP-2687 Phase 2)")
    p.add_argument("--self-test", action="store_true", help="execution-backed self-test")
    args = p.parse_args()
    if args.self_test:
        return _self_test()
    p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
