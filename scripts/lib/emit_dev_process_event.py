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
    from append_dev_process_event import _LANE_LABELS as _KNOWN_LANE_LABELS  # CLI fail-VISIBLE 검증 재사용
    from dev_process_capture_activation import dev_process_capture_enabled  # always-on α gate (D4)
except Exception:  # pragma: no cover — import path fallback
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from dev_process_blob_store import capture_blob
    from append_dev_process_event import append_event
    from append_dev_process_event import _LANE_LABELS as _KNOWN_LANE_LABELS
    from dev_process_capture_activation import dev_process_capture_enabled


# Port B agent-emit 소유 event-type (closed — hook Port A 3종 배제)
_AGENT_EMIT_TYPES = frozenset({
    "lane_transition", "verdict", "defect_finding", "fix_transition", "final_artifact",
})

_EMPTY_AUDIT = {"redaction_applied": False, "redaction_count": 0, "redaction_rules_fired": []}

# ─── seq 채번 causal-state 어휘 (D1/D3 — CFP-2817 계약 §4 seq 규율 SSOT) ────────────
# transition_kind = ADR-038 6-point 전이 종류 토큰. scripts/jira-channel/progress-format.sh
#   6-token 재사용(신규 어휘 발명 0 — D3). 단일 code anchor 로 "진입" vs "lane_entry" 이형
#   토큰이 동일 6-point 상태를 다른 seq 로 흩어 AC-4/AC-9 dedup 붕괴시키는 실패모드를 예방.
_TRANSITION_KINDS = frozenset({
    "enter", "pass", "fix-detected", "cause", "re-enter", "complete",
})
# FIX 사이클 전이 3종 — fix_iter 필수(미상 시 ESCALATE, silent fallback 금지 — CFP-2817 P2-2).
_FIX_TRANSITION_KINDS = frozenset({"fix-detected", "cause", "re-enter"})


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
    """verdict 이벤트. **호출자 = Orchestrator(-owned delegate)**(AC-7, ADR-039 §결정3 writer
    monopoly); semantic 발생원 = review lane(packet 반환만 — 직접 emit = policy_violation).
    어떤 verdict 가 났나 semantic-evidence — 의미론 정의(C)는 out."""
    return emit("verdict", content=content, consumer_scope=consumer_scope,
                ledger_path=ledger_path, blob_root=blob_root,
                story_key=story_key, lane_label=lane_label, **fields)


def emit_defect_finding(story_key, lane_label, *, defect_id=None, defect_family=None,
                        defect_type=None, detecting_lane=None, time_to_detection=None,
                        content=None, consumer_scope=None, ledger_path=None,
                        blob_root=None, **fields):
    """결점 findings 이벤트. **호출자 = Orchestrator(-owned delegate)**(AC-7, ADR-039 §결정3);
    semantic 발생원 = review lane(결점 packet 반환만 — 직접 emit = policy_violation).
    taxonomy 4-tuple(§결정 3) + defect_id 상관.

    defect_id = content-addressed 상관 ID(미지정 시 append 가 raw→sha256 처리).
    defect_type = review-verdict-v4 closed vocab 파생만(자유텍스트 금지 — OBJ-1: semi-open index 는
                  redaction 미적용 유일 content 채널이므로 caller 가 closed vocab 을 강제한다).
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
    """최종 산출물 이벤트. **호출자 = Orchestrator(-owned delegate)**(AC-7, ADR-039 §결정3);
    semantic 발생원 = lane. 산출물 요약 semantic-evidence-aggregation."""
    return emit("final_artifact", content=content, consumer_scope=consumer_scope,
                ledger_path=ledger_path, blob_root=blob_root,
                story_key=story_key, lane_label=lane_label, **fields)


# ─────────────────────── derive_seq (6번째 pure helper — seq 채번 SSOT, 0 I/O) ──────────
def derive_seq(transition_kind, *, fix_iter=None, reset_generation=None, ordinal=None):
    """causal-state 파생 seq — **pure 함수, 0 I/O(원장 read 금지·§10 파일 read 금지)**.

    seq = event_id(§2 field1) 산입 disambiguator(계약 §4 seq 규율 SSOT). index row 에 미persist.
    caller(Orchestrator)가 이미 보유한 causal state 를 typed parameter 로 주입 —
    원장 tail-read·primitive 내부 채번·random-UUID 는 **전부 at-least-once 멱등 붕괴**라 배제한다
    (재시도가 다른 원장 상태 관측 → 다른 seq → 중복 행 + read-time dedup 무력화).

    Args:
      transition_kind: ADR-038 6-point 전이 종류 토큰(_TRANSITION_KINDS 6종, progress-format.sh
                       재사용). 필수 — 미상/미등재 토큰 = ValueError(visible-over-silent,
                       이형 토큰 drift 로 인한 dedup 붕괴 예방 — §6 단일 code anchor).
      fix_iter:        해당 FIX 사이클의 §10 FIX Ledger Iter 값(Orchestrator 가 §10 row 쓰기 직전
                       보유한 causal state — §10 persisted 필드 아님). FIX 계열 전이 3종
                       (fix-detected/cause/re-enter)에는 **필수**.
      reset_generation: 해당 lane 의 §10 RESET 마커 누적 세대(RESET 경계 재발 disambiguation, F-DR-1).
      ordinal:         동일 (transition_kind, fix_iter, reset_generation) 내 복수 시도
                       (verdict 복수발생·동일 Iter defect 재검출)의 attempt 서브카운터.

    Returns:
      결정론적 seq 문자열. 동일 입력 → 동일 문자열(멱등, INV-1) / 상이 입력 → 상이 문자열(소실0, INV-2).

    Raises (실패방향 원칙 — INV-3, visible duplicate ≫ silent loss):
      ValueError:
        - transition_kind 미상/미등재(6-token 밖) — silent seq collapse 방지.
        - FIX 계열 전이인데 fix_iter 미상 — **ESCALATE 우선**(§10 FIX Ledger/session-recovery §7.4
          복원, 복원 불가 = 사용자 ESCALATE). coarse-fallback(transition_kind 단독) 및 seq 성분
          silent drop 금지(CFP-2817 P2-2). 재시도가 다른 값을 얻어 silent loss 되는 경로 차단.

    세션 재기동 재구성(INV-4): 두 입력 모두 dev-process 원장이 **아닌** Story 파일에서 복원
      (fix_iter=§10 FIX Ledger Iter / transition_kind=phase label+§10) — 원장 1행도 안 읽고 재계산 가능.
      순수함수라 재계산 결과가 attempt 마다 동일(EventStoreDB expectedVersion 동형 조건 구조적 충족).
    """
    tk = None if transition_kind is None else str(transition_kind).strip()
    if not tk or tk not in _TRANSITION_KINDS:
        raise ValueError(
            "derive_seq: transition_kind=%r 미상/미등재 — 6-token(%s) 중 하나 필수. "
            "이형 토큰 silent 흡수 = 동일 6-point 상태의 seq drift → dedup 붕괴(AC-4/AC-9) → "
            "visible-over-silent 원칙상 raise (계약 §4 seq 규율 ③)."
            % (transition_kind, "/".join(sorted(_TRANSITION_KINDS)))
        )
    if tk in _FIX_TRANSITION_KINDS and fix_iter is None:
        raise ValueError(
            "derive_seq: transition_kind=%r 는 FIX 사이클 전이 — fix_iter 필수. fix_iter 미상 시 "
            "§10 FIX Ledger/session-recovery §7.4 복원, 복원 불가 = ESCALATE. coarse-fallback"
            "(transition_kind 단독)·seq 성분 silent drop 금지 — 재시도 silent loss 차단(P2-2, 계약 §4 ③)."
            % tk
        )

    def _n(v):  # int 성분 정규화 — None→'' (미persist·복원가능), 그 외 int coerce(비-int = visible ValueError)
        return "" if v is None else str(int(v))

    # 라벨링 join — 성분 경계 명확(fix_iter=1,ordinal=None ≠ fix_iter=None,ordinal=1 구조적 구분)
    return "kind=%s|iter=%s|reset=%s|ord=%s" % (
        tk, _n(fix_iter), _n(reset_generation), _n(ordinal),
    )


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

    # ── 케이스 8: derive_seq — 결정성(INV-1)·distinctness(INV-2)·실패방향 raise(INV-3) ──
    check(derive_seq("enter") == derive_seq("enter"), "[c8] derive_seq 비결정적 (INV-1 위반)")
    check(derive_seq("enter") != derive_seq("pass"),
          "[c8] 상이 transition_kind 인데 동일 seq (INV-2 소실0 위반)")
    check(derive_seq("re-enter", fix_iter=1) != derive_seq("re-enter", fix_iter=2),
          "[c8] 상이 fix_iter 인데 동일 seq (재진입 disambiguation 실패)")
    check(derive_seq("re-enter", fix_iter=1, reset_generation=0)
          != derive_seq("re-enter", fix_iter=1, reset_generation=1),
          "[c8] 상이 reset_generation 인데 동일 seq (RESET 경계 재발 봉인 실패, F-DR-1)")
    check(derive_seq("cause", fix_iter=1, ordinal=1) != derive_seq("cause", fix_iter=1, ordinal=2),
          "[c8] 상이 ordinal 인데 동일 seq (복수 시도 disambiguation 실패)")
    for bad in ("", None, "진입", "lane_entry"):
        try:
            derive_seq(bad)
            check(False, f"[c8] 미등재 transition_kind={bad!r} 에도 raise 안 함 (visible-over-silent 위반)")
        except ValueError:
            pass
    try:
        derive_seq("re-enter")  # FIX 계열인데 fix_iter 미상 → ESCALATE
        check(False, "[c8] FIX 전이 fix_iter 미상인데 raise 안 함 (P2-2 ESCALATE 위반)")
    except ValueError:
        pass
    # 재진입 seq 를 emit 에 적용 → 별개 전이 2행 생존(INV-2 소실0, 재진입 discriminating)
    lt_ledger = os.path.join(tmpdir, "reentry.jsonl")
    e_enter = emit_lane_transition("CFP-2817", "구현", consumer_scope="wrapper",
                                   ledger_path=lt_ledger, seq=derive_seq("enter"))
    e_reenter = emit_lane_transition("CFP-2817", "구현", consumer_scope="wrapper",
                                     ledger_path=lt_ledger, seq=derive_seq("re-enter", fix_iter=1))
    check(e_enter is not None and e_reenter is not None and e_enter != e_reenter,
          "[c8] state-derived seq 재진입 event_id collapse (AC-4 소실 방향)")

    # ── 케이스 9: D6-a CLI dispatch — emit() 경유 lane_transition round-trip ──
    cli_ledger = os.path.join(tmpdir, "cli.jsonl")
    rc = main([
        "lane-transition", "--story-key", "CFP-2817", "--lane-label", "구현",
        "--transition-kind", "enter", "--consumer-scope", "wrapper", "--ledger-path", cli_ledger,
    ])
    check(rc == 0, "[c9] CLI lane-transition exit != 0 (record-only 위반)")
    if os.path.isfile(cli_ledger):
        with open(cli_ledger, encoding="utf-8") as f:
            crows = [json.loads(ln) for ln in f if ln.strip()]
        check(len(crows) == 1 and crows[0]["emit_source"] == "agent"
              and crows[0]["event_type"] == "lane_transition",
              "[c9] CLI lane-transition 행이 emit_source=agent lane_transition 로 append 안 됨")
    else:
        check(False, "[c9] CLI lane-transition 이 ledger 를 생성하지 않음")

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
          "taxonomy 전파 OK; Port A 침범 차단 OK; activation α OK; "
          "derive_seq 결정성/distinctness/실패방향 OK; D6-a CLI dispatch OK)")
    return 0


# ─────────────────────── CLI (D6-a — Orchestrator 호출 표면, emit() 경유) ──────────────
#   불변 제약(CFP-2817 §3.6): (1) emit() 경유 필수 — append_event/그 CLI 직접호출 금지(REC-2:
#   emit() 만이 activation gate·Port-A 침범 차단·INV-8b+redaction·emit_source=agent 고정 4종 강제).
#   (2) --timestamp 인자 부재(AC-13) — 시각은 always primitive 내부 UTC. --prev-timestamp-utc 는
#   monotonic clamp 용 직전 행 값 전달만(시각 계산 아님). (3) seq = derive_seq() 파생만(단일 SSOT —
#   caller hand-rolled seq flag 미노출, 이형 토큰 drift 예방). append `_build_parser` 어휘 재사용.

def _add_common_emit_args(sp):
    """3 서브커맨드 공통 arg — append `_build_parser` 어휘 재사용(--story-key/--lane-label/
    --consumer-scope/--ledger-path) + seq causal-state flag(--transition-kind/--fix-iter/
    --reset-generation/--ordinal). --timestamp 부재(AC-13)."""
    sp.add_argument("--story-key", required=True, help="story_key — e.g. CFP-2817 (명시 주입, ambient 금지 — AC-11)")
    sp.add_argument("--lane-label", required=True, help="lane_label closed enum (미매칭 → 없음)")
    sp.add_argument("--transition-kind", required=True, choices=sorted(_TRANSITION_KINDS),
                    help="ADR-038 6-point 전이 토큰(seq 파생 — progress-format.sh 재사용)")
    sp.add_argument("--fix-iter", type=int, default=None,
                    help="§10 FIX Ledger Iter (FIX 계열 전이 필수 — 미상 시 ESCALATE)")
    sp.add_argument("--reset-generation", type=int, default=None, help="§10 RESET 마커 누적 세대(F-DR-1)")
    sp.add_argument("--ordinal", type=int, default=None, help="동일 (kind,iter,reset) 내 attempt 서브카운터")
    sp.add_argument("--consumer-scope", default=None, help="consumer_scope {wrapper, consumer}")
    sp.add_argument("--ledger-path", default=None, help="ledger jsonl full path override (test/직접)")
    sp.add_argument("--content", default=None,
                    help="rich content 원본(참조전용/최소-blob 선호 — 미지정 시 blob-less index)")
    sp.add_argument("--prev-timestamp-utc", default=None,
                    help="직전 행 timestamp (monotonic clamp 전용 — 시각 계산 아님, AC-13)")


def _build_parser():
    import argparse
    p = argparse.ArgumentParser(
        description="dev-process-event-v1 agent-emit (Port B) writer (CFP-2687 A / CFP-2817 배선)")
    p.add_argument("--self-test", action="store_true", help="execution-backed self-test")
    sub = p.add_subparsers(dest="command")

    lt = sub.add_parser("lane-transition", help="ADR-038 6-point lane 전이 emit (Orchestrator)")
    _add_common_emit_args(lt)

    vd = sub.add_parser("verdict", help="리뷰 verdict emit (Orchestrator — semantic 발생원=review lane)")
    _add_common_emit_args(vd)

    df = sub.add_parser("defect-finding", help="결점 findings emit (Orchestrator — semantic 발생원=review lane)")
    _add_common_emit_args(df)
    df.add_argument("--defect-id", default=None, help="content-addressed 상관 ID(raw → sha256)")
    df.add_argument("--defect-family", default=None, help="taxonomy CLOSED-7")
    df.add_argument("--defect-type", default=None,
                    help="review-verdict-v4 closed vocab 파생만(자유텍스트 금지 — OBJ-1)")
    df.add_argument("--detecting-lane", default=None, help="결점 검출 lane (lane_label enum)")
    df.add_argument("--time-to-detection", default=None, help="DERIVED measure (numeric | unattributed)")
    return p


def _dispatch_emit(args):
    """서브커맨드 → derive_seq() 파생 seq → emit() 경유. record-only exit-0, fail-VISIBLE(WARN)."""
    try:
        seq = derive_seq(args.transition_kind, fix_iter=args.fix_iter,
                         reset_generation=args.reset_generation, ordinal=args.ordinal)
    except ValueError as exc:
        # 실패방향 원칙 — 채번 불확실은 silent 대체 없이 가시화 후 미기록(lane 진행 무차단, ADR-115).
        sys.stderr.write("[emit-dev-process-event] WARN: seq 채번 불가 — %s "
                         "(미기록·fail-VISIBLE, lane 진행 무차단)\n" % exc)
        return 0

    # fail-VISIBLE (AC-3, silent-success 금지): 미인식 lane_label 은 append 가 '없음' 으로 graceful
    # fallback 하나 그 fallback 은 silent (lane 귀속 소실 → AC-6/AC-11 훼손). 여기서 WARN 로 가시화한다.
    # ★Windows 실 세션 주의: shell(Git Bash/PowerShell) 을 통과한 한국어 argv 는 byte-mangle 가능
    #   (원인 = shell↔argv 인코딩, 코드 아님). 이 WARN 이 그 mangling 을 조기 표면화한다. lane 진행 무차단.
    if args.lane_label not in _KNOWN_LANE_LABELS:
        sys.stderr.write(
            "[emit-dev-process-event] WARN: lane_label=%r 미인식 (알려진 lane enum 밖) — append 가 '없음' "
            "으로 fallback (lane 귀속 소실 위험, AC-6/AC-11). Windows shell 한국어 argv mangling 가능성 "
            "점검 요망. lane 진행 무차단(record-only).\n" % (args.lane_label,))

    common = dict(content=args.content, consumer_scope=args.consumer_scope,
                  ledger_path=args.ledger_path, seq=seq,
                  prev_timestamp_utc=args.prev_timestamp_utc)

    if args.command == "lane-transition":
        eid = emit_lane_transition(args.story_key, args.lane_label, **common)
    elif args.command == "verdict":
        eid = emit_verdict(args.story_key, args.lane_label, **common)
    elif args.command == "defect-finding":
        eid = emit_defect_finding(
            args.story_key, args.lane_label,
            defect_id=args.defect_id, defect_family=args.defect_family,
            defect_type=args.defect_type, detecting_lane=args.detecting_lane,
            time_to_detection=args.time_to_detection, **common)
    else:  # pragma: no cover — argparse 가 command 를 강제하므로 도달 불가
        sys.stderr.write("[emit-dev-process-event] WARN: unknown command %r\n" % args.command)
        return 0

    if eid:
        print(eid)
    else:
        # None = 비활성 gate / Port-A 침범 / append 실패 4상황 미구별 — fail-VISIBLE(D2-d 보조 규율).
        sys.stderr.write("[emit-dev-process-event] WARN: emit 미기록 (None 반환 — 비활성 gate / "
                         "Port-A 침범 / append 실패 중 하나). lane 진행 무차단.\n")
    return 0


def main(argv=None):
    p = _build_parser()
    args = p.parse_args(argv)
    if args.self_test:
        return _self_test()
    if not getattr(args, "command", None):
        p.print_help()
        return 0
    return _dispatch_emit(args)


if __name__ == "__main__":
    sys.exit(main())
