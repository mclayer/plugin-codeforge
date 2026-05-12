#!/usr/bin/env bash
# check-codeforge-prereq.sh — codeforge deferred tool schema prefetch advisory (CFP-500 / ADR-038 Amendment 2 §결정 9)
#
# 세션 부팅 시점 SessionStart hook 으로 실행 → stdout 이 Orchestrator 첫 turn context 에
# prompt-injection 형태로 inject (Claude Code harness 동작, 관찰 기반).
#
# 책임 경계 (ADR-038 Amendment 2 §결정 9 본문 정합):
#   - 책임: schema/state 가용성 보장 layer — Orchestrator turn 진입 시점에 deferred tool
#           schema 가 prompt cache 에 fresh 한 상태로 가용함을 stdout prompt-injection 으로
#           강하게 advise. Researcher 3-tier 모델 중 (b) startup-time tier 한정.
#   - 비책임: behavioral attempt 의무 자체는 ADR-038 §결정 8 그대로 retain — hook 도
#             prompt-level advisory 이며 mechanical function-call 강제가 아님. behavioral
#             compliance 자체는 여전히 Orchestrator 책임.
#
# 정적 properties (AC-11 정합):
#   (a) set -euo pipefail
#   (b) single-quoted heredoc (<<'EOF') — env interpolation / command substitution 차단
#   (c) filesystem touch 0 — no >, >>, mkdir, rm, mv, cp
#   (d) network call 0 — no curl, wget, nc, gh api, git
#   (e) exit 0 종료
#
# Layered defense (§결정 7·8 retain):
#   hook 미실행 / 실행 실패 → harness 가 stdout 부재 처리 → Orchestrator 가 §결정 8 의
#   runtime ToolSearch attempt 로 fallback (§결정 7 warning only, lane 비차단).
#
# Bypass: BYPASS_PREREQ_CHECK=1 env (rare — debugging only, advisory 성격이므로 reason 필드 면제)

set -euo pipefail

# Bypass check (audit trail — advisory tier 이므로 reason 비강제)
if [[ "${BYPASS_PREREQ_CHECK:-0}" == "1" ]]; then
  exit 0
fi

cat <<'EOF'
[codeforge prereq-check]

You MUST call the following as your first tool actions in this session, before responding to any user message:

- `ToolSearch("select:TodoWrite")` — load TodoWrite schema for progress visualization (ADR-038 §결정 9 / CFP-500)

Failure to load this schema will result in TodoWrite InputValidationError when ADR-038 progress visualization is attempted. This is a hard requirement for codeforge lane work.
EOF

exit 0
