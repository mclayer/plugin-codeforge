---
kind: domain_fact
type: domain-knowledge
area: agent-teams
topic_slug: agent-teams-platform-capability
title: Claude Code agent teams (experimental) platform capability + codeforge re-entrancy 제약
status: Active
tags:
  - agent-teams
  - platform-capability
  - re-entrancy
  - teamcreate
  - sendmessage
related_adrs:
  - ADR-009  # wrapper-only decomposition (Orchestrator 단일 lead 정합)
  - ADR-022  # Sonnet decider Deprecated (codeforge 1st-class vs ad-hoc 경계)
  - ADR-035  # codeforge agent teams Epic architecture (Phase-scoped sequential team SSOT carrier)
  - ADR-039  # subagent default for codeforge modification work (default subagent context 정의)
  - ADR-040  # worktree convention (agent teams + worktree integration 의존)
  - ADR-044  # Phase-scoped sequential team SSOT — 본 entry 의 platform 근거 ADR (CFP-137 carrier) + Amendment 1 (CFP-391 — dispatch_mode auto_on_divergence)
  - ADR-059  # debate-protocol-v1 carrier (CFP-391 v1.0 / CFP-582 v1.2) — Adversarial 패턴의 자동 발동 정책 SSOT
related_stories:
  - CFP-134  # Epic carrier
  - CFP-135  # ADR-022 deprecate foundation
  - CFP-136  # worktree infra prerequisite
  - CFP-137  # 본 entry 의 carrier
  - CFP-391  # Adversarial 패턴 자동 발동 (debate-protocol-v1 v1.0) — 5 권장 패턴 매핑 확장
  - CFP-582  # Adversarial 패턴 dispatch_mode 4번째 enum (blanket_cross_module_designlane) 추가 (Wave 4)
created: 2026-05-09
updated: 2026-05-13
---

# Claude Code agent teams (experimental) — platform capability + codeforge re-entrancy 제약

## Summary

Claude Code experimental `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 활성 시 사용 가능한 **agent teams platform capability** 와 codeforge 가 적용하는 **re-entrancy 제약 3종** SSOT. ADR-044 Phase-scoped sequential team 패턴의 platform 근거이며, default subagent context (ADR-039) 와의 분기 조건을 명시한다.

## Pattern

**codeforge Phase-scoped sequential team 패턴** (ADR-044):
- lane 진입 시 `TeamCreate(team-spec-<lane>.yaml)` → teammate fan-out
- lane 종결 시 `TeamDelete()` → 다음 lane TeamCreate 이전 완료
- re-entrancy 제약 3종: (1) 재귀 spawn 금지, (2) nested team 금지, (3) one-team-per-lead 강제

**env=0 fallback**: ADR-039 default subagent context (one-shot Agent tool spawn). TeamCreate / SendMessage / TaskCreate 미사용. team-spec yaml 미사용.

5 권장 패턴 매핑: Specialization (lane teammate system_prompt) / Parallelization (TEAM-DESIGN 6 SubAgent) / Adversarial (review Claude vs Codex — 두 가지 dispatch_mode 지원: (1) `user_request_only` — 사용자 explicit request 시, (2) `auto_on_divergence` — DesignReview lane 에서 finding 불일치 자동 감지 시 multi-round debate 발동 [debate-protocol-v1, CFP-391 / ADR-059]) / Cross-layer (TEAM-DEVELOP dev ↔ QA) / Escalation (lane FIX).

## Usage

agent teams enabled context 활성화:
1. `settings.json` 에 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 설정 + 세션 재시작
2. `templates/agent-teams-hook-samples/` 3종 hook install (`.claude/hooks/`)
3. lane 진입 시 `templates/team-spec-<lane>.yaml` 로 `TeamCreate` 호출
4. review lane Codex worker = `dispatch_mode: user_request_only` (default roster 제외 — 사용자 explicit request 시만 활성)
5. `/resume` 후 in-process teammate 미복원 risk → Phase-scoped short lifecycle 팀 채택 의무

## 정의

**Agent teams** 는 Claude Code 의 experimental feature 로, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env 활성 시 Lead session (Orchestrator) 이 **teammate** 라는 sibling agent 들을 한 team 으로 묶어 동시 spawn + 직접 통신 (SendMessage) + task 분배 (TaskList) 를 수행할 수 있게 하는 platform 기능. codeforge 의 default subagent context (ADR-039) 가 가지는 one-shot Agent tool spawn invariant 를 **agent teams enabled context** 에서 완화한다.

## 컨텍스트

codeforge 는 ADR-009 (wrapper-only decomposition) 이후 wrapper agent 0개 + 6 lane plugin × N agent 구조. 모든 spawn 은 wrapper Orchestrator 가 `Agent` tool 로 lane plugin agent 를 일회성 호출 — sub-agent 간 통신 부재, sub-agent recursive spawn 금지 (platform inherent). 본 invariant 가 `default subagent context 의 codeforge 정책 결정` (ADR-039 §결정 1).

agent teams 기능 도입 시점 (CFP-134 Epic + CFP-137 carrier) 에 본 invariant 의 **enabled context 분기** 가 필요해진다. enabled context 에서는 Lead 와 teammate 간 + sibling teammate 간 SendMessage 가 가능 — PL ↔ worker continuous dialog, Adversarial debate (Claude vs Codex worker), Cross-layer coordination (TEAM-DEVELOP 의 dev ↔ QA) 패턴이 codeforge orchestration 에 합류.

본 entry = codeforge family 의 agent teams 영역 도메인 지식 첫 SSOT. CFP-137 진입 직전 시점 (Wave 2) 신설.

## 핵심 platform API

| API | 의미 | codeforge 사용처 |
|---|---|---|
| `TeamCreate(team_spec, worktree?)` | 동기 team 생성 — teammate roster fan-out | 매 lane 진입 시 `templates/team-spec-<lane>.yaml` 로 호출 (CFP-137 §3.3) |
| `TeamDelete()` | 동기 team 종료 — in-flight teammate 완료 명시 대기 | lane 종결 시 + FIX iteration 진입 시 |
| `SendMessage(to, body)` | sibling teammate / 직상위 lead 와 직접 통신 | PL ↔ worker continuous dialog (Adversarial / Cross-layer 패턴) |
| `TaskList()` / `TaskCreate(...)` | teammate 별 task 분배 + 진행 tracking | PL 이 worker 에 dispatch 시 |
| `TeammateIdle` hook | idle teammate 감지 trigger | PL nudge 또는 TeamDelete 트리거 |
| `TaskCreated` / `TaskCompleted` hook | task lifecycle 추적 | Story §14 Lane Evidence row append 자동 (ADR-031 정합) |

## codeforge re-entrancy 제약 3종 (정책 SSOT)

agent teams enabled context 에서도 다음 3 제약 유지:

1. **재귀 spawn 금지** (Lead 와 teammate 모두) — platform inherent. teammate 는 추가 teammate 를 spawn 할 수 없음. 본 제약은 default context (Agent tool one-shot) 와 enabled context 양쪽 동일.
2. **Nested team 금지** (no team-of-teams) — codeforge 정책. teammate 가 자기 sub-team 을 만들지 못함.
3. **One-team-per-lead 강제** — codeforge 정책 (platform 도 동일 강제). Lead 가 동시에 1 team 만 보유 — 다음 lane team 생성 전 현 team `TeamDelete()` 의무.

본 3 제약이 codeforge 의 **Phase-scoped sequential team** 패턴 정당화 근거 (CFP-137 §3.1 lifecycle, ADR-035 D2).

## Default subagent context 와의 분기

| 항목 | Default subagent context (env=0 또는 미설정) | Agent teams enabled context (env=1) |
|---|---|---|
| spawn 단위 | `Agent` tool one-shot subagent | TeamCreate teammate fan-out |
| sub-agent 간 통신 | 불가 (Orchestrator round-trip 만) | SendMessage 가능 (sibling + 직상위) |
| Continuous dialog | 불가 (매 round Orchestrator 재 spawn) | 가능 (TaskCreate / SendMessage rounds) |
| Codex review / Sonnet decider | 사용자 ad-hoc 만 (ADR-022 Deprecated) | 사용자 ad-hoc 만 (동일) — Codex worker `dispatch_mode: user_request_only` |
| codeforge orchestration 위치 | ADR-039 carrier | ADR-035 + CFP-137 carrier |

env=0 fallback 동작은 모든 lane plugin agent prompt 가 명시 의무 — SessionStart hook 검증 + agent prompt 의 "default subagent context fallback" 분기 (CFP-137 §3.4 sibling-sync 책임).

## /resume 후 in-process teammate 미복원 risk

`/resume` 후 in-process teammate 는 미복원 — agent teams 의 stateful 가정 깨짐. 따라서 **Story-long single team 회피** + **lane 별 짧은 lifecycle team** (Phase-scoped sequential) 채택. 본 risk 는 ADR-035 §결정 D2 substantive decision 의 "sequential" 부분 직접 motivation. SessionStart hook (CFP-137 §3.7 또는 후속 CFP) 이 stale team manifest GC + worktree GC 통합 처리.

## 5 권장 패턴 매핑 (Anthropic agent design pattern → codeforge lane)

| 패턴 | codeforge 매핑 lane | 적용 evidence |
|---|---|---|
| Specialization | 7 lane teammate 좁은 system prompt | team-spec yaml `system_prompt_path` |
| Parallelization | TEAM-DESIGN 6 SubAgent / 2 review worker 동시 | §14 Lane Evidence `spawned_at` diff |
| Adversarial | DesignReview (`auto_on_divergence`) / DesignLane (`blanket_cross_module_designlane`, CFP-582) / Requirements (CFP-392 deferred) — debate-protocol-v1 v1.2 SSOT | review-verdict v4 packet `worker_dialog_rounds` + Story §9 `### Debate transcript: <anchor_id>` section (debate-protocol-v1 schema) + §10 FIX Ledger `debate_artifact_ref` 필드 (fix-event-v1 1.1) |
| Cross-layer | TEAM-DEVELOP 의 dev ↔ QA continuous coordination | develop-output `cross_layer_dialog_rounds` |
| Escalation | lane FIX 시 lane team → TEAM-FIX (parallel diagnosis) | §10 FIX Ledger + §14 fix-iter row pair |

상세 measurable verification = CFP-137 Story §5.1.

## 외부 reference 정합

본 entry 는 Anthropic Claude Code experimental agent teams docs 의 verbatim transcribe 가 아니라 **codeforge 내부 정책 SSOT** — codeforge 가 어떻게 platform capability 를 활용하는지 정의. 외부 docs link 안정성 미확정 (experimental feature) 이므로 외부 URL 은 본 entry 에 미포함 — codeforge family 내부 SSOT (CFP-134 spec / ADR-035 / 본 Story CFP-137) 가 1차 source.

## 관련 ADR / Story / 후속 작업

- **Carrier ADR**: ADR-035 (Epic 통합) + ADR-044 (CFP-137 Phase-scoped sequential team SSOT, Phase 1 PR 작성 예정).
- **Carrier Story**: CFP-137 (본 entry 도입), CFP-134 (Epic).
- **의존 ADR**: ADR-009 (Orchestrator 단일 lead), ADR-039 (default subagent context), ADR-040 (worktree integration), ADR-022 Deprecated (Codex / Sonnet 정체성 정정).
- **후속**: CFP-139 (GitOpsAgent — long-running teammate 패턴 도입 시 본 entry §"`/resume` risk" 재방문), CFP-141 후보 (gh-aw 와 codeforge 관계 분석 — out-of-scope priming).

## 핵심 규칙

1. **Phase-scoped sequential team** = lane 별 짧은 lifecycle (lane 진입 시 TeamCreate, 완료 시 TeamDelete). Story-long single team 회피 — `/resume` 후 in-process teammate 미복원 risk.
2. **Lead = Orchestrator** (Story 전 기간 fixed) — ADR-009 wrapper-only invariant 정합. Lead 변경 금지.
3. **One-team-per-lead 강제** — 다음 lane TeamCreate 전 현 team `TeamDelete()` 의무. nested team 금지 (no team-of-teams). 재귀 spawn 금지 (Lead 와 teammate 모두 — platform inherent + codeforge 정책).
4. **review lane Codex worker `dispatch_mode`** — default roster = `PL + Claude worker` 2 teammate. Codex worker 는 (a) 사용자 explicit request 시 활성 → 3 teammate (ADR-022 Deprecated / ADR-035 §결정 4 정합 — codeforge 가 Codex 를 1st-class component 로 자동 invoke 하지 않는 정책), (b) DesignReview lane 에서 사용자 explicit Codex request 후 Claude / Codex worker 가 동일 anchor 에 finding 불일치 산출 시 **자동으로 multi-round debate 진입** (`auto_on_divergence` mode, ADR-044 Amendment 1 / CFP-391 / ADR-059). 우선순위 `default > auto_on_divergence > user_request_only`. `auto_on_divergence` 자체는 Codex worker 신규 spawn 권한 부여 안 함 — 이미 활성된 두 worker 사이의 divergence 해소 자동 발동만.
5. **env-divergent fallback** — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0` (default 또는 미설정) 시 ADR-039 default subagent context (one-shot Agent tool spawn) 으로 fallback. SendMessage / TeamCreate / TaskCreate / TeammateIdle hook 모두 미발화. team-spec yaml 미사용.
6. **SendMessage secret hygiene** — sibling teammate 끼리 system prompt / tool output 공유. consumer 측 secret (API key / DB credential 등) 가 SendMessage body 또는 system prompt 안에 포함되면 sibling teammate 모두 노출. consumer-guide §1f 명시 의무.

## 경계

**codeforge 책임 영역 (in scope)**:
- team-spec yaml 7종 (`templates/team-spec-<lane>.yaml`) — teammate roster + dispatch_pattern + worktree_layout 정의
- hook 3종 sample (`templates/agent-teams-hook-samples/{TeammateIdle,TaskCreated,TaskCompleted}.json.sample`) — consumer install reference
- review-verdict v4 schema (`docs/inter-plugin-contracts/review-verdict-v4.md`) — `worker_dialog_rounds` field SSOT
- ADR-044 carrier (Phase-scoped sequential team SSOT)
- env-divergent fallback contract (env=1 enabled context vs env=0 default subagent context)

**Anthropic platform 책임 영역 (out of scope)**:
- TeamCreate / TeamDelete / SendMessage / TaskList API 자체 (codeforge 가 호출하되 동작은 platform 영역)
- Hook trigger timing (idle detection / task lifecycle)
- one-team-per-lead 강제 (platform + codeforge 양쪽 동일)
- 재귀 spawn 금지 (platform inherent)
- TeammateIdle detection 알고리즘
- 25 thread 한도 (platform-level)

**사용자 책임 영역 (consumer side)**:
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` settings.json 활성 + 신규 세션 재시작
- hook 3종 install (`.claude/hooks/` 디렉토리 + settings.json `hooks.{TeammateIdle,TaskCreated,TaskCompleted}[]` 배열 merge)
- Secret hygiene (SendMessage body 안 secret 미포함 의무)
- Codex worker explicit request (review lane 에서 ad-hoc 활성)

## 변경 이력

| 날짜 | 변경 | Carrier |
|---|---|---|
| 2026-05-09 | 초기 작성 (CFP-137 RequirementsPL lane) — 5 권장 패턴 매핑 + re-entrancy 제약 3종 + env-divergent fallback + `/resume` risk 명시 | CFP-137 (본 Story) |
| 2026-05-09 | doc-section-schema strict 정합 — `## 핵심 규칙` + `## 경계` + `## 변경 이력` 필수 섹션 추가 (CFP-137 ArchitectPL lane Phase 1 PR commit batch) | CFP-137 (본 Story) |
| 2026-05-11 | Adversarial 패턴 확장 (CFP-391 / ADR-059 / ADR-044 Amendment 1) — `dispatch_mode: auto_on_divergence` 추가, debate-protocol-v1 자동 발동 정책 명시, 5 권장 패턴 매핑 + 핵심 규칙 #4 + Adversarial row evidence (Story §9 transcript + §10 debate_artifact_ref) 업데이트. consumer-guide §1f 정합 | CFP-391 |
| 2026-05-13 | Adversarial 패턴 dispatch_mode 4번째 enum value `blanket_cross_module_designlane` 추가 (DesignLane internal blanket trigger — ArchitectPL + ArchitectAgent + 6 SubAgent). 5 권장 매핑 표 갱신. ADR-059 Amendment 2 carrier. | CFP-582 |
