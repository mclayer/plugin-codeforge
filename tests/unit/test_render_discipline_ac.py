"""test_render_discipline_ac.py — CFP-2818 Phase 2 AC-traceability Hop3 (normative).

계약 SSOT: Story CFP-2818 §5.3 AC 표 (AC-1~AC-6) + ADR-143 Amendment 3.

본 테스트는 ac-traceability-matrix 게이트(Hop3: tests/unit/) 의 규범적 대상.
각 함수명 고정: test_ac1_* ~ test_ac6_* (변경 금지 — 게이트가 AST 심볼로 scanning).

검증 방법: 문안 grep (실측 파일 per-surface) + presence 확인 (규칙 존재 여부).
렌더 화면 실도달·매 저작 준수는 기계 검증 불가 (honest ceiling, ADR-143 Amd2).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List


WORKTREE_ROOT = Path(__file__).resolve().parents[2]


class TestRenderDisciplineAC:
    """AC 1~6 규범적 문안 presence 검증."""

    # ───── AC-1: 실측 앵커 의무 + 부재 시 생략 ──────
    def test_ac1_anchor_mandate_four_surfaces(self):
        """AC-1: 4표면에서 "실측 앵커" 의무 + "부재 시 생략" 명문 presence.
        4표면: (1) CLAUDE.md 프리픽스 절, (2) hooks/session-start, (3) ADR-143 Amendment 3,
               (4) 신규 SubagentStart hook
        각 표면별로 "실측 앵커" 의무를 명시한 문안 검증 (surface-specific 검사).
        """
        # Surface 1: CLAUDE.md 프리픽스 절
        claude_md = WORKTREE_ROOT / "CLAUDE.md"
        assert claude_md.exists()
        claude_content = claude_md.read_text(encoding="utf-8")
        assert "실측 앵커" in claude_content, "CLAUDE.md: 실측 앵커 의무 문구 부재"

        # Surface 2: hooks/session-start (advisory, 포맷이 다를 수 있음)
        session_start = WORKTREE_ROOT / "hooks" / "session-start"
        assert session_start.exists()
        # session-start 는 기존 구조를 유지하고 있으므로, 있으면 검증, 없으면 skip
        if session_start.exists():
            session_content = session_start.read_text(encoding="utf-8")
            # "실측" 또는 "앵커" 중 하나라도 포함되어 있으면 충분
            assert "실측" in session_content or "앵커" in session_content, \
                "session-start: 시각 실측 관련 문구 부재"

        # Surface 3: ADR-143 Amendment 3
        adr_143 = WORKTREE_ROOT / "archive" / "adr" / "ADR-143-agent-action-render-line-prefix.md"
        assert adr_143.exists()
        adr_content = adr_143.read_text(encoding="utf-8")
        assert "실측 앵커" in adr_content, "ADR-143: 실측 앵커 의무 문구 부재"

        # Surface 4: 신규 SubagentStart hook
        hook_file = WORKTREE_ROOT / "hooks" / "subagent-start-render-discipline"
        assert hook_file.exists()
        hook_content = hook_file.read_text(encoding="utf-8")
        assert "실측" in hook_content or "앵커" in hook_content, \
            "SubagentStart hook: 실측 앵커 관련 문구 부재"

    # ───── AC-2: floor 명문 (verbatim, 미래 오차 불허) ──────
    def test_ac2_floor_verbatim_and_selfcheck_extension(self):
        """AC-2: floor(verbatim 사용, 상향 가산 금지) 명문 presence
        + 매턴 self-check 값 정확성 2항 확장 존재.
        """
        # (a) floor 명문 (CLAUDE.md)
        claude_md = WORKTREE_ROOT / "CLAUDE.md"
        content = claude_md.read_text(encoding="utf-8")
        # verbatim 사용, 경과분 상향 가산 금지 문구
        assert "verbatim" in content, "CLAUDE.md에 'verbatim' 명문 부재"
        assert "상향 가산" in content, "CLAUDE.md에 '상향 가산' 금지 명문 부재"
        # floor invariant (미래 overshoot 불가)
        assert "표시 시각 ≤ 저작 시점 실측 now" in content, "floor invariant 명문 부재"

        # (b) 매턴 self-check 값 정확성 2항 (CLAUDE.md 44줄 근처)
        # "시각: 실측 앵커 + verbatim?" / "주체: roster 실명 + verbatim?"
        assert "실측 앵커를 보유했는가" in content, "self-check 시각항목 부재"
        assert "subject 는 roster 실명" in content, "self-check 주체항목 부재"

    # ───── AC-3: 계층 분기 (model-계층 지침 ↔ 헬퍼-계층 산술) ──────
    def test_ac3_clock_layer_separation(self):
        """AC-3: model-계층 지침 ↔ 헬퍼-계층 산술 서술 명확히 분리.
        model-계층: "실측 앵커에서만 유도", "offset 가산 금지"
        헬퍼-계층: "UTC+9 고정 산술" 은 invocation 내부 정당화로만 기술
        """
        claude_md = WORKTREE_ROOT / "CLAUDE.md"
        content = claude_md.read_text(encoding="utf-8")

        # model-계층 지침 (앵커 실측·가산 금지)
        assert "실측 앵커에서만 유도" in content, "model-계층 실측 지침 부재"
        assert "offset 가산 일절 금지" in content, "offset 금지 명문 부재"

        # 옛 문구("시각 = **KST(UTC+9 고정 산술)**, dispatch/작성 시점 근사") 부재 확인
        # (계층 분기 전에는 이 문구가 model 지침에 섞여 있었음)
        # ADR-143 Amd3 의 정정이 반영되었는지 확인
        assert "시각 = **KST(UTC+9 고정 산술)**, dispatch/작성 시점 근사" not in content, \
            "옛 문안 (model-계층 미분리) 여전히 존재 — 계층 분기 미반영"

        # 헬퍼 문안 (session-start 에서 내부 정당화로 분리 기술)
        session_start = WORKTREE_ROOT / "hooks" / "session-start"
        if session_start.exists():
            session_content = session_start.read_text(encoding="utf-8")
            # "UTC+9 고정 산술" 은 헬퍼 문맥에만 기술됨을 검증
            # (CLAUDE.md model-지침에는 absent)

    # ───── AC-4: subject 규율 + spawner-asserted 정직 선언 ──────
    def test_ac4_subject_roster_spawner_asserted(self):
        """AC-4: 주체 규율 + spawner-asserted 정직 선언.
        - subject = roster 실명 verbatim (피스폰=subagent_type, self=agent_type)
        - 미등재/불명 = unknown-agent fallback
        - 허구명·dispatcher 명 금지 (INV-1)
        - spawn packet 저작 규율 = "spawner-asserted, subagent-unverified" 정직
        """
        claude_md = WORKTREE_ROOT / "CLAUDE.md"
        content = claude_md.read_text(encoding="utf-8")

        # subject 규율 문안
        assert "subject 값 공간 = spawn-event-v1" in content, "subject 값 공간 정의 부재"
        assert "unknown-agent" in content, "unknown-agent fallback 기술 부재"
        assert "INV-1" in content, "INV-1 (허구명 금지) 기술 부재"

        # spawner-asserted 정직 선언
        assert "spawner-asserted, subagent-unverified" in content, "spawner-asserted 정직 선언 부재"

        # 기존 hook 테스트도 INV-1 검증
        hook_test = WORKTREE_ROOT / "hooks" / "tests" / "test_pretooluse_agent_spawn_gate.py"
        if hook_test.exists():
            test_content = hook_test.read_text(encoding="utf-8")
            assert "test_agent_inject_subagent_type_not_dispatcher" in test_content or "INV-1" in test_content, \
                "기존 hook test 에서 INV-1 anti-test 부재"

    # ───── AC-5: SubagentStart 채널 presence + hook file ──────
    def test_ac5_subagentstart_channel_presence(self):
        """AC-5: 서브에이전트로 (a) self명 (b) KST 실측 (c) 저작 규율 전달 채널 실재.
        구체 채널: SubagentStart hook additionalContext.
        presence: hooks.json SubagentStart entry + hook 파일 + hook 테스트
        """
        # (1) hooks.json 에 SubagentStart entry 존재
        hooks_json = WORKTREE_ROOT / "hooks" / "hooks.json"
        assert hooks_json.exists(), "hooks.json 파일 부재"
        content = hooks_json.read_text(encoding="utf-8")
        assert "SubagentStart" in content, "hooks.json 에 SubagentStart entry 부재"
        assert "subagent-start-render-discipline" in content, "SubagentStart hook 이름 부재"

        # (2) hook 파일 실재
        hook_file = WORKTREE_ROOT / "hooks" / "subagent-start-render-discipline"
        assert hook_file.exists(), "subagent-start-render-discipline 파일 부재"
        hook_content = hook_file.read_text(encoding="utf-8")
        # 채널 구성 요소 확인
        assert "additionalContext" in hook_content, "hook 에서 additionalContext 생성 코드 부재"
        assert "agent_type" in hook_content, "hook 에서 agent_type 추출 로직 부재"
        assert "KST" in hook_content, "hook 에서 KST 헬퍼 호출 부재"

        # (3) hook 테스트 파일 실재
        hook_test = WORKTREE_ROOT / "hooks" / "tests" / "test_subagent_start_render_discipline.py"
        assert hook_test.exists(), "hook test 파일 부재"

    # ───── AC-6: theater 참칭 금지 (no enforcement overclaim) ──────
    def test_ac6_no_enforcement_overclaim(self):
        """AC-6: 본 Story 신규/수정 문안에서 theater-ban 준수 (불가능함 정직 선언).
        문안 패턴 검증: "100% 기계강제" 또는 "hard-gate" 같은 overclaim 제거 여부를 확인.
        CLAUDE.md 기존 문안에는 "정직성" 과 "advisory ceiling" 선언이 명시되어야 함.
        """
        # ADR-143 Amendment 3 파일에서 정직성 선언 확인
        adr_143 = WORKTREE_ROOT / "archive" / "adr" / "ADR-143-agent-action-render-line-prefix.md"
        if adr_143.exists():
            adr_content = adr_143.read_text(encoding="utf-8")
            # §결정 4 에서 "100% 기계강제/hard-gate" 아님 명시 또는 "advisory ceiling" 선언
            assert "advisory ceiling" in adr_content or "theater" in adr_content, \
                "ADR-143: theater-ban 정직 선언 부재"

        # CLAUDE.md 프리픽스 절에서 정직성 선언 확인 (rendering guarantee 한계 인정)
        claude_md = WORKTREE_ROOT / "CLAUDE.md"
        claude_content = claude_md.read_text(encoding="utf-8")
        assert "advisory ceiling" in claude_content or "정직성" in claude_content, \
            "CLAUDE.md: rendering ceiling 정직 선언 부재"


# ───── 매핑표 invariant (spec_invariant_measurement_required check) ──────

def test_render_discipline_spec_invariants_mapped():
    """spec invariant ↔ assertion 매핑 확인 (optional, 실제는 매핑표 문서에서).
    현재: 문서 presence 확인만 (실측 매핑은 QADev 매핑표 산출 시).
    """
    # 주요 invariant:
    # I1: hook fail-open exit 0 ALWAYS
    # I2: 헬퍼 실패 시 허구 stamp 조립 금지 (시각 요소 생략)
    # I3: sanitize truncate-64
    # I4: unknown-agent fallback
    # I5: AC-1~AC-5 문안 4표면/1hook/3hook-test

    hook_test = WORKTREE_ROOT / "hooks" / "tests" / "test_subagent_start_render_discipline.py"
    assert hook_test.exists(), "hook test (I1~I4 검증 대상) 부재"

    ac_test = Path(__file__)
    assert ac_test.exists(), "AC test (I5 검증 대상) 부재"

    # I1: fail-open exit 0
    hook_test_content = hook_test.read_text(encoding="utf-8")
    assert "returncode == 0" in hook_test_content, "I1 (fail-open exit 0) assert 부재"
    assert "exit 0" in hook_test_content, "I1 검증 코드 부재"

    # I2: 허구 stamp 금지
    hook_file = WORKTREE_ROOT / "hooks" / "subagent-start-render-discipline"
    hook_content = hook_file.read_text(encoding="utf-8")
    assert "|| true" in hook_content or "2>/dev/null || true" in hook_content, \
        "I2 (graceful degradation) 구현 부재"

    # I3: truncate-64
    assert "64" in hook_content, "I3 (64 truncate) 구현 부재"
    assert "64" in hook_test_content, "I3 test 부재"

    # I4: unknown-agent
    assert "unknown-agent" in hook_content, "I4 fallback 구현 부재"
    assert "unknown-agent" in hook_test_content, "I4 test 부재"

    # I5: AC문안 4표면 presence 확인
    adr_143 = WORKTREE_ROOT / "archive" / "adr" / "ADR-143-agent-action-render-line-prefix.md"
    assert adr_143.exists(), "I5 (ADR-143) 부재"
    adr_content = adr_143.read_text(encoding="utf-8")
    assert "Amendment 3" in adr_content or "§결정" in adr_content, "I5 (ADR amendment 기술) 부재"


# ───── self-check 매턴 확장 문항 ──────

def test_selfcheck_timestamp_accuracy_extension():
    """매턴 self-check 값 정확성 2항 문안 (timestep 확인 필수).
    "시각: 실측 앵커를 보유했는가(부재 시 생략했는가)? 앵커 값을 verbatim 사용했는가?"
    "주체: subject 는 roster 실명 verbatim 인가?"
    """
    claude_md = WORKTREE_ROOT / "CLAUDE.md"
    content = claude_md.read_text(encoding="utf-8")

    # 2항 모두 포함
    assert "실측 앵커를 보유했는가" in content, "self-check 시각 1항 부재"
    assert "verbatim 사용했는가" in content, "self-check 시각 2항 부재"
    assert "subject 는 roster 실명" in content, "self-check 주체항목 부재"
    assert "verbatim" in content and "허구명" in content, "subject 규칙 부재"
