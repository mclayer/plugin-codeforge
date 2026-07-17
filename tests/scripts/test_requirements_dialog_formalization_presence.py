#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CFP-2725 Phase 2 / Change Plan §8 RTM — 4 normative AC 확정 배선 presence lint paired self-test.

대상 lint (scripts/lib/, read-only — src 미수정):
  AC-5  check_design_entry_signoff_predicate.py       — 설계 진입 preflight sign-off predicate 앵커
  AC-6  check_decision_channel_confirm_routing.py      — 원격 결정 채널 최종 확정 routing 앵커
  AC-7  check_confirmation_record_schema_resume.py     — 확정 기록 schema + 세션 재개 복원 앵커
  AC-21 check_lane_sequence_review_before_confirm.py   — lane 시퀀스 + review-pass-before-confirm 앵커

각 테스트 함수 = 완결 paired self-test (POS + NEG-hollow + TARGET-GUARD 를 1함수 안에 전부):
  POS          전 target + 전 anchor 를 독립 tmp fixture 에 실 상대경로로 배치 → lint --root <tmp> exit 0
  NEG(hollow)  target 마다 그 첫 anchor 제거 → exit != 0 + 부재 anchor 리터럴이 stdout (원인 결박, false-oracle 방지)
               2-target lint 은 target[1] anchor-drop 경로도 discriminating 검증(F2 정정 — hollow-gate 갭 봉인)
  TARGET-GUARD 빈 트리(target 전 부재) → exit != 0 + 'target 부재' 도메인 sentinel stdout

oracle = 실 lint subprocess exit code + 도메인 stdout substring (하드코딩 기대 금지 — false-oracle 0).
subprocess fork 진정성(distinct-marker 의무): exit code 단독 판정 금지 — POS/NEG/TARGET-GUARD 전부
  도메인 stdout sentinel 을 병행 assert. lint 미fork/impl 부재 시 interpreter exit 2 + 빈 stdout →
  sentinel assert 가 자연 실패하여 silent false-positive(우연한 exit code 일치) 를 차단한다.

born-red 회피: 주 assertion 은 전부 독립 tmp fixture — 실 repo 문서 landing 상태(병렬 dev lane 이 앵커
  landing 중)에 비의존. 본 self-test 는 문서 landing 여부가 아니라 lint 로직 자체를 검증한다.
tautology 회피: 실 repo 문서 미복사 — 최소 합성 마크다운 fixture(필수 anchor 리터럴만).

정직 라벨(over-claim 금지): 본 self-test 는 lint 의 presence 검증(governance 문서 anchor 가 landed
  되었는지)까지만 검증한다 — "user actually confirmed(사용자가 실제로 확정했는지)"는 검증 대상 아님
  (NOT testable, advisory ceiling; lint docstring 과 정합).
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB = REPO_ROOT / "scripts" / "lib"


def _run_lint(script_name, root):
    """실 lint 을 subprocess 로 fork — (returncode, stdout, stderr) 반환. 도메인 sentinel 병행 검증용."""
    return subprocess.run(
        [sys.executable, str(LIB / script_name), "--root", str(root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _write(root, rel, body):
    """tmp fixture root 아래 rel(실 상대경로) 에 UTF-8/LF 로 body write (CRLF 0)."""
    p = root / Path(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8", newline="\n")


def _fixture_body(anchors):
    """최소 합성 마크다운 — 필수 anchor 리터럴만 포함(전문 복제 불요 · tautology 회피)."""
    out = ["# QADev 독립 self-test fixture (실 repo 문서 미복사)\n\n"]
    out += [f"- anchor: {a}\n" for a in anchors]
    return "".join(out)


def _assert_paired(script, targets, tmp_path):
    """POS + NEG(hollow) per-target + TARGET-GUARD assertion — 도메인 stdout sentinel 병행(distinct-marker).

    NEG(hollow): 각 target index 별로 그 target 의 첫 anchor 를 drop 한 fixture → exit != 0 +
      부재 anchor stdout 결박. drop_idx=0 = 기존 target[0] NEG(무손상 계승). 2-target lint 은
      drop_idx=1 로 target[1] anchor-drop 경로도 discriminating 검증(F2 정정 — target[1]
      hollow-gate 경로 미행사 갭 봉인).
    """
    # ── POS: 전 target + 전 anchor → exit 0 ──
    pos = tmp_path / "pos"
    for rel, anchors in targets:
        _write(pos, rel, _fixture_body(anchors))
    r = _run_lint(script, pos)
    assert r.returncode == 0, (
        f"POS expect exit 0, got {r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}"
    )
    # distinct-marker: PASS 도메인 sentinel 병행(미fork 시 빈 stdout → 실패).
    assert "PASS" in r.stdout, f"POS stdout 에 PASS sentinel 미검출\nstdout={r.stdout}"

    # ── NEG(hollow-gate): target 마다 그 target 의 첫 anchor 제거 → exit != 0 + 부재 anchor stdout 결박 ──
    for drop_idx in range(len(targets)):
        dropped_rel, dropped_anchors = targets[drop_idx]
        dropped_anchor = dropped_anchors[0]
        neg = tmp_path / f"neg{drop_idx}"
        for i, (rel, anchors) in enumerate(targets):
            keep = [a for a in anchors if not (i == drop_idx and a == dropped_anchor)]
            _write(neg, rel, _fixture_body(keep))
        r = _run_lint(script, neg)
        assert r.returncode != 0, (
            f"NEG[target{drop_idx}:{dropped_rel}] expect nonzero, got 0\nstdout={r.stdout}"
        )
        # distinct-marker: 부재 anchor 리터럴이 stdout 에(원인 결박 — exit-code-only false-positive 차단).
        assert dropped_anchor in r.stdout, (
            f"NEG[target{drop_idx}:{dropped_rel}] stdout 에 부재 anchor '{dropped_anchor}' "
            f"미검출(원인 미결박)\nstdout={r.stdout}"
        )

    # ── TARGET-GUARD: 빈 트리(target 전 부재) → exit != 0 + 'target 부재' 도메인 sentinel ──
    guard = tmp_path / "guard"
    guard.mkdir()
    r = _run_lint(script, guard)
    assert r.returncode != 0, f"TARGET-GUARD expect nonzero, got 0\nstdout={r.stdout}"
    # distinct-marker: target-existence guard 도메인 sentinel(미fork 시 interpreter 에러 → 실패).
    assert "target 부재" in r.stdout, (
        f"TARGET-GUARD stdout 에 'target 부재' sentinel 미검출\nstdout={r.stdout}"
    )


# ─────────────────────────── AC-5 ───────────────────────────
def test_design_entry_preflight_signoff_predicate_present(tmp_path):
    """AC-5: 설계 진입 preflight design-entry sign-off predicate 확정 배선 presence lint self-test."""
    _assert_paired(
        "check_design_entry_signoff_predicate.py",
        [("docs/orchestrator-playbook.md",
          ["user-final-sign-off-resolved", "advisory ceiling"])],
        tmp_path,
    )


# ─────────────────────────── AC-6 ───────────────────────────
def test_decision_channel_confirm_routing_present(tmp_path):
    """AC-6: 원격 결정 채널 최종 확정 payload + terminal routing 확정 배선 presence lint self-test."""
    _assert_paired(
        "check_decision_channel_confirm_routing.py",
        [("skills/jira-decision-channel/SKILL.md",
          ["최종 확정 payload", "user-final-confirmation-driven"])],
        tmp_path,
    )


# ─────────────────────────── AC-7 ───────────────────────────
def test_confirmation_record_schema_and_resume_restore_present(tmp_path):
    """AC-7: 확정 기록 schema(Story §5.5) + 세션 재개 복원 확정 배선 presence lint self-test (2 target)."""
    _assert_paired(
        "check_confirmation_record_schema_resume.py",
        [
            ("templates/story-page-structure.md", ["확정 발화 verbatim", "양채널 mirror"]),
            ("skills/session-recovery/SKILL.md", ["확정 상태 복원", "미해소 질문 목록"]),
        ],
        tmp_path,
    )


# ─────────────────────────── AC-21 ───────────────────────────
def test_lane_sequence_review_before_confirm_precondition_present(tmp_path):
    """AC-21: lane 시퀀스 + review-pass-before-confirm precondition 확정 배선 presence lint self-test (2 target)."""
    _assert_paired(
        "check_lane_sequence_review_before_confirm.py",
        [
            ("docs/orchestrator-playbook.md",
             ["phase:요구사항-리뷰", "user-final-sign-off-resolved"]),
            ("archive/adr/ADR-159-requirements-lane-enrichment-and-design-entry-signoff.md",
             ["design-entry"]),
        ],
        tmp_path,
    )
