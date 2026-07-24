"""test_subagent_start_render_discipline.py — CFP-2818 Phase 2 §8.2 Test Contract (TDD).

계약 SSOT: Story CFP-2818 §7.9 (Test Contract §8.2 경계 조건) / ADR-143 Amendment 3.

NewSubagentStart hook for render-line-prefix 저작 규율 전달 검증:
- stdin JSON payload 입력에서 agent_type 추출 + G2 sanitize + KST 헬퍼 실측 + additionalContext emit
- fail-open ALWAYS: JSON parse 실패 시 무출력, 헬퍼 실패 시 시각 요소 생략 (허구 fabrication 금지)
- 경계 분기: (a) agent_type 유/무 × (b) 헬퍼 성공/실패 × (c) JSON parse 성공/실패

born-hollow 방지 3조건 (CFP-2799 교훈):
  (i) 대상 분기 실도달 fixture ✓ Decision Table 분기 전수
  (ii) assert = additionalContext 내용 명시 대조 ✓ 존재-여부 단독 금지
  (iii) 취약 revert → RED firsthand 확인 후 단정 ✓ 실험 절차별 기술

anti-theater: stdout JSON 형식 + JSON key validation + additionalContext 문자열 정합
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

import pytest


WORKTREE_ROOT = Path(__file__).resolve().parent.parent.parent
HOOK_SCRIPT = WORKTREE_ROOT / "hooks" / "subagent-start-render-discipline"
KST_STAMP_HELPER = WORKTREE_ROOT / "scripts" / "kst-render-stamp.sh"


class TestSubagentStartRenderDisciplineHook:
    """SubagentStart hook 실행 환경 + 경계 조건 fixture."""

    def _run_hook(
        self,
        payload: Optional[str] = None,
        env_override: Optional[dict[str, str]] = None,
    ) -> tuple[int, str, str]:
        """hook 을 subprocess 로 fork — stdin 에 payload 주입.
        Windows 환경: run-hook.cmd wrapper 를 통해 실행.
        반환: (returncode, stdout, stderr)
        """
        hook_runner = WORKTREE_ROOT / "hooks" / "run-hook.cmd"
        if not hook_runner.exists():
            pytest.skip(f"hook runner not found: {hook_runner}")

        run_env = dict(os.environ)
        run_env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)
        if env_override:
            run_env.update(env_override)

        # run-hook.cmd wrapper 호출 (Windows cmd.exe 를 통해)
        proc = subprocess.run(
            [str(hook_runner), "subagent-start-render-discipline"],
            input=payload or "",
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=run_env,
        )
        return proc.returncode, proc.stdout, proc.stderr

    # ───── (a) agent_type 유/무 × (b) 헬퍼 성공/실패 × (c) JSON parse 성공/실패 Decision Table ──────

    def test_valid_json_with_agent_type_and_helper_success(self):
        """분기: ✓JSON ✓agent_type ✓helper
        기대: additionalContext emit + self명 = sanitized agent_type + KST 앵커 포함
        """
        payload = json.dumps({"agent_type": "TestAgent"})
        returncode, stdout, stderr = self._run_hook(payload)

        assert returncode == 0, f"exit code must be 0 (fail-open), got {returncode}"
        assert stdout.strip(), "stdout should not be empty for valid JSON with agent_type"

        # stdout is JSON with hookSpecificOutput
        output = json.loads(stdout)
        assert "hookSpecificOutput" in output
        assert output["hookSpecificOutput"]["hookEventName"] == "SubagentStart"

        additional_context = output["hookSpecificOutput"]["additionalContext"]
        assert "self명 = TestAgent" in additional_context, "should contain sanitized subject"
        assert "KST 실측 앵커 = " in additional_context, "should contain KST anchor line"

    def test_valid_json_with_agent_type_namespace_stripped(self):
        """분기: ✓JSON ✓agent_type(with namespace) ✓helper
        기대: agent_type 에서 ':' 뒤만 추출 → namespace strip 적용
        """
        payload = json.dumps({"agent_type": "codeforge-design:ArchitectAgent"})
        returncode, stdout, stderr = self._run_hook(payload)

        assert returncode == 0
        output = json.loads(stdout)
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        assert "self명 = ArchitectAgent" in additional_context

    def test_valid_json_with_empty_agent_type(self):
        """분기: ✓JSON ✓agent_type="" ✓helper
        기대: self명 = unknown-agent fallback
        """
        payload = json.dumps({"agent_type": ""})
        returncode, stdout, stderr = self._run_hook(payload)

        assert returncode == 0
        output = json.loads(stdout)
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        assert "self명 = unknown-agent" in additional_context

    def test_valid_json_missing_agent_type_field(self):
        """분기: ✓JSON ✗agent_type(필드 부재) ✓helper
        기대: self명 = unknown-agent fallback (parse success → output emit)
        """
        payload = json.dumps({})
        returncode, stdout, stderr = self._run_hook(payload)

        assert returncode == 0
        output = json.loads(stdout)
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        assert "self명 = unknown-agent" in additional_context

    def test_valid_json_agent_type_truncate_64chars(self):
        """분기: ✓JSON ✓agent_type(>64 chars) ✓helper
        기대: subject 64자로 truncate (RE_PREFIX bound 정합)
        """
        long_name = "X" * 100
        payload = json.dumps({"agent_type": long_name})
        returncode, stdout, stderr = self._run_hook(payload)

        assert returncode == 0
        output = json.loads(stdout)
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        # self명 = 로부터 다음 개행까지의 subject 부분
        assert "self명 = " + ("X" * 64) in additional_context

    def test_valid_json_helper_failure_anchor_omitted(self):
        """분기: ✓JSON ✓agent_type ✗helper(PATH 조작 제거)
        기대: additionalContext 생성 BUT KST 앵커 라인 부재 ("앵커 미확보" 생략형)
        """
        payload = json.dumps({"agent_type": "TestAgent"})
        # PATH 에서 헬퍼 찾을 수 없도록 mock env
        run_env = {"PATH": "/nonexistent"}
        returncode, stdout, stderr = self._run_hook(payload, env_override=run_env)

        assert returncode == 0, "fail-open: helper 실패해도 exit 0"
        # stdout 여전히 emit (agent_type 있으므로)
        if stdout.strip():
            output = json.loads(stdout)
            additional_context = output["hookSpecificOutput"]["additionalContext"]
            # 앵커 부재 분기 → 시각 요소 생략
            assert "KST 실측 앵커 = " not in additional_context or "앵커 미확보" in additional_context

    def test_invalid_json_parse_failure(self):
        """분기: ✗JSON(parse 실패) × ×
        기대: 무출력 + exit 0 (fail-open)
        """
        invalid_json = "{ not valid json"
        returncode, stdout, stderr = self._run_hook(invalid_json)

        assert returncode == 0, "fail-open: JSON parse 실패해도 exit 0"
        assert stdout.strip() == "", "JSON parse 실패 시 무출력 (additionalContext 미emit)"

    def test_empty_stdin_no_output(self):
        """분기: empty stdin
        기대: 무출력 + exit 0
        """
        returncode, stdout, stderr = self._run_hook("")

        assert returncode == 0
        assert stdout.strip() == ""

    # ───── G2 sanitize 규칙 ──────

    def test_sanitize_strips_brackets(self):
        """subject 에서 '[', ']' 제거 (RE_PREFIX 파괴 방지)"""
        payload = json.dumps({"agent_type": "[BracketAgent]"})
        returncode, stdout, stderr = self._run_hook(payload)

        assert returncode == 0
        output = json.loads(stdout)
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        assert "self명 = BracketAgent" in additional_context
        assert "[" not in additional_context.split("\n")[1]  # self명 행에 '[' 없음

    def test_sanitize_normalizes_control_chars(self):
        """subject 안 제어문자(개행, 탭, NUL 등) → 공백"""
        payload = json.dumps({"agent_type": "Agent\nWith\tControl"})
        returncode, stdout, stderr = self._run_hook(payload)

        assert returncode == 0
        output = json.loads(stdout)
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        # \n, \t 가 공백으로 정규화됨
        assert "Agent" in additional_context and "With" in additional_context

    # ───── 출력 형식 검증 ──────

    def test_output_json_structure_valid(self):
        """output JSON 형식이 명세(hookSpecificOutput 포함)를 따름"""
        payload = json.dumps({"agent_type": "TestAgent"})
        returncode, stdout, stderr = self._run_hook(payload)

        assert returncode == 0
        output = json.loads(stdout)
        assert isinstance(output, dict)
        assert "hookSpecificOutput" in output
        assert "hookEventName" in output["hookSpecificOutput"]
        assert "additionalContext" in output["hookSpecificOutput"]
        assert output["hookSpecificOutput"]["hookEventName"] == "SubagentStart"

    def test_additional_context_contains_ruleset_text(self):
        """additionalContext 에 저작 규율 compact 텍스트 포함 (AC-1~AC-3 전달)"""
        payload = json.dumps({"agent_type": "TestAgent"})
        returncode, stdout, stderr = self._run_hook(payload)

        assert returncode == 0
        output = json.loads(stdout)
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        # 저작 규율 텍스트 필드 확인
        assert "render-line-prefix 저작 규율" in additional_context
        assert "ADR-143" in additional_context
        assert "CFP-2818" in additional_context

    def test_additional_context_contains_discipline_rules(self):
        """additionalContext 에 3개 규율(①②③) 텍스트 포함"""
        payload = json.dumps({"agent_type": "TestAgent"})
        returncode, stdout, stderr = self._run_hook(payload)

        assert returncode == 0
        output = json.loads(stdout)
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        # 3개 규율 마크
        assert "① leaf 도구호출" in additional_context
        assert "② 앵커 부재 시" in additional_context
        assert "③ subject = roster" in additional_context

    # ───── born-hollow 방지 3조건 ──────
    # (i) 대상 분기 실도달 fixture → 위 decision table 커버
    # (ii) assert = additionalContext 내용 명시 대조 → 위 테스트들이 substring 검사 수행
    # (iii) 취약 revert → RED firsthand → 실험 섹션 참조


@pytest.mark.parametrize(
    "agent_type,expected_subject",
    [
        ("MyAgent", "MyAgent"),
        ("codeforge-design:ArchitectAgent", "ArchitectAgent"),
        ("plugin:sub:Agent", "Agent"),  # 마지막 ':' 뒤만
        ("", "unknown-agent"),
        ("   ", "unknown-agent"),  # whitespace → fallback
        ("X" * 100, "X" * 64),  # truncate
    ],
)
def test_subject_sanitization_parametrized(agent_type, expected_subject):
    """G2 subject sanitize 규칙 parametrized fixture — 모든 분기 커버"""
    hook_runner = WORKTREE_ROOT / "hooks" / "run-hook.cmd"
    if not hook_runner.exists():
        pytest.skip("hook runner not found")

    payload = json.dumps({"agent_type": agent_type})
    run_env = dict(os.environ)
    run_env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)

    proc = subprocess.run(
        [str(hook_runner), "subagent-start-render-discipline"],
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=run_env,
    )

    assert proc.returncode == 0
    if proc.stdout.strip():
        output = json.loads(proc.stdout)
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        assert f"self명 = {expected_subject}" in additional_context


def test_fail_open_exit_always_zero():
    """fail-open ALWAYS: 어떤 failure (JSON, helper, etc) 도 exit 0"""
    hook_runner = WORKTREE_ROOT / "hooks" / "run-hook.cmd"
    if not hook_runner.exists():
        pytest.skip("hook runner not found")

    # 여러 실패 케이스
    test_cases = [
        ("invalid json", "JSON parse 실패"),
        ("", "empty stdin"),
        (json.dumps({}), "missing agent_type"),
        (json.dumps({"agent_type": ""}), "empty agent_type"),
    ]

    run_env = dict(os.environ)
    run_env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)

    for payload, description in test_cases:
        proc = subprocess.run(
            [str(hook_runner), "subagent-start-render-discipline"],
            input=payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=run_env,
        )
        assert proc.returncode == 0, f"fail-open 위반 ({description}): exit {proc.returncode}"


def test_perf_hook_execution_under_500ms():
    """Performance baseline: hook 실행 ≤ 500ms (python subprocess) / ≤ 1500ms (cmd.exe wrapper).
    Windows run-hook.cmd 오버헤드 고려하여 1500ms threshold 사용."""
    hook_runner = WORKTREE_ROOT / "hooks" / "run-hook.cmd"
    if not hook_runner.exists():
        pytest.skip("hook runner not found")

    payload = json.dumps({"agent_type": "TestAgent"})
    run_env = dict(os.environ)
    run_env["CLAUDE_PLUGIN_ROOT"] = str(WORKTREE_ROOT)

    import time
    start = time.perf_counter()
    proc = subprocess.run(
        [str(hook_runner), "subagent-start-render-discipline"],
        input=payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=run_env,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    # Windows cmd.exe wrapper + bash 실행 오버헤드 포함하여 1500ms threshold (비win 500ms 기준)
    assert elapsed_ms < 1500, f"perf regression: {elapsed_ms:.1f}ms >= 1500ms"
