---
kind: concept_definition
type: domain-knowledge
slug: orchestrator-runtime-hook-enforcement
title: Orchestrator runtime hook enforcement (Stop / UserPromptSubmit / SubagentStart / SubagentStop)
status: Active
updated: 2026-05-27
carrier_story: CFP-1738
related_adrs:
  - ADR-039  # Orchestrator subagent default — runtime hooks 가 PR-time lint 보완하는 deterministic gate
  - ADR-071  # Orchestrator-user dialog convergence — UserPromptSubmit hook 의 context 주입 정석
  - ADR-073  # Orchestrator verify-before-assert — runtime gate 의 ground truth 확보 mechanism
related_files:
  - templates/.claude/hooks/  # codeforge wrapper 가 제공하는 hooks fixture set
  - docs/orchestrator-playbook.md  # §3.0 Inline whitelist + UserPromptSubmit context 주입 패턴
tags:
  - claude-code
  - hooks
  - runtime-enforcement
sources:
  - https://code.claude.com/docs/en/hooks
  - https://github.com/anthropics/claude-code/issues/10412
  - https://github.com/anthropics/claude-code/issues/55754
  - https://github.com/anthropics/claude-code/issues/54898
---

## 정의

Claude Code 의 turn-time lifecycle hook (Stop / SubagentStop / UserPromptSubmit / SubagentStart / PreToolUse) 을 통해
Orchestrator 의 LLM 행동(질문 발화 / subagent spawn / turn 종료 / context 재주입)을 PR-time lint 가 아닌 **런타임 결정론적 gate** 로
강제하려는 시도. codeforge 가 지금까지 "turn-final hook 부재 platform 한계" 라 가정해 포기했던 영역.

## 컨텍스트

codeforge 는 governance / behavioral discipline 을 두 layer 로 enforcement 한다:
- **PR-time lint** (workflow + bats) — `git push` 후 mechanical check, blocking-on-pr / blocking-on-merge tier
- **Behavioral directive** (CLAUDE.md / playbook / skill) — Orchestrator LLM 의 self-discipline, mechanical enforce 불가

CLAUDE.md 와 ADR-064 §결정 9 turn-final hook 부재 라 가정해 LLM behavior 의 turn-time enforcement 를 포기해 왔다. CFP-1738 (사용자 대화 품질 hook 내장 — reminder + check) 에서 Claude Code 공식 hooks 가 실제로 turn-time gate 를 지원함을 발견하면서 본 가정이 falsified 됐고, 이 doc 은 그 boundary 를 정확히 codify 한다.

## 핵심 규칙

Claude Code 공식 hooks reference 기준 turn-time hook 의 block 가능 여부:

| Hook | block 가능? | 차단 mechanism | 핵심 fact |
|---|---|---|---|
| Stop / SubagentStop | YES | top-level `decision:"block"` + `reason` (Claude 에게 전달) 또는 exit 2 / `continue:false` + `stopReason` (사용자만) | exit 2 가 turn 을 강제 continue |
| UserPromptSubmit | YES | exit 0 stdout = context 주입, `additionalContext` / `decision:"block"` + `suppressOriginalPrompt` | 매 turn 시작 context 주입 정석 |
| SubagentStart | **NO** | 차단 불가 — "Shows stderr to user only", observability/`additionalContext` only | **spawn 차단은 PreToolUse `Agent`/`Task` matcher `permissionDecision:"deny"` 가 정석** |
| PreToolUse (`Agent`/`Task` matcher) | YES | `permissionDecision:"deny"` + `permissionDecisionReason` | spawn-time deterministic gate |

## 경계

- **In scope**: Claude Code turn-time lifecycle hook (5 종 위 표). codeforge wrapper 가 `templates/.claude/hooks/` 로 consumer 에게 제공 가능한 영역.
- **Out of scope**:
  - LLM 응답 content 의 semantic validation (LLM-as-judge 영역, hook 으로 enforce 불가)
  - subagent 내부 행동 (subagent 는 자체 hooks 컨텍스트 — Orchestrator hooks 와 disjoint)
  - PR-time lint (별도 layer — workflow + bats, ADR-060 evidence-enforceable framework)
- **Anti-pattern**: SubagentStart 로 spawn 차단 시도 (block 불가 — PreToolUse `Agent`/`Task` matcher 사용 의무)

## 관련 ADR

- **ADR-039** Orchestrator subagent default for codeforge modification work — runtime hook 이 PR-time lint 의 보완 layer
- **ADR-071** Orchestrator-user dialog convergence — UserPromptSubmit hook 이 dialog frame mode context 주입 정석 mechanism
- **ADR-073** Orchestrator verify-before-assert — runtime hook 으로 ground truth 확보 시도 시 verify-before-trust 와 협력
- **CFP-1738** (carrier_story) — 사용자 대화 품질 hook 내장 (reminder + check), 본 concept 의 first applied case

## 변경 이력

- 2026-05-26 KST — 초기 작성 (CFP-1738 hooks 작업 중 research note)
- 2026-05-27 KST — codeforge concept_definition schema 정합 (frontmatter `status`/`updated` + 5-section structure: 컨텍스트 / 핵심 규칙 / 경계 / 관련 ADR / 변경 이력), CFP-1738 carrier_story link
