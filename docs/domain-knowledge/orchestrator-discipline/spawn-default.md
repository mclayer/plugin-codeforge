---
type: domain-knowledge
area: orchestrator-discipline
topic_slug: spawn-default
title: Subagent-default Orchestrator execution discipline (codeforge modification work)
status: Active
tags:
  - orchestrator
  - subagent
  - spawn-policy
  - inline-whitelist
  - adr-039
related_adrs:
  - ADR-009  # wrapper-only decomposition (Orchestrator definition)
  - ADR-025  # stop discipline (motivation)
  - ADR-029  # phase execution visibility (narration interaction)
  - ADR-031  # lane-spawn evidence (§14 row append행위)
  - ADR-035  # agent teams Epic (subagent semantics)
related_stories:
  - CFP-275
created: 2026-05-08
updated: 2026-05-09
---

# Subagent-default Orchestrator execution discipline

## Summary

codeforge 수정 작업 중 Orchestrator 가 모든 work 을 `Agent` tool spawn (subagent) 으로 수행하는 **subagent-default discipline** SSOT. "inline 으로 충분한가 vs subagent 가 나은가" 판단 분기 자체를 제거하여 ADR-025 §결정 7 `policy_violation_subdecision` stop 발화 채널을 차단한다.

## Pattern

**Inline whitelist 4-entry** (subagent spawn 면제 — Orchestrator 직접 수행 허용):
1. 사용자 dialog (텍스트 응답)
2. TodoWrite scratchpad (progress visualization)
3. Read-only Q&A 답변 (Read / Grep / Glob only, no write)
4. Status report (lane 진행 현황 텍스트)

**Whitelist 외 모든 작업** = subagent spawn 의무 (Read/Write/Edit/Bash/Grep/Glob/mcp__github__\* 포함).

**에러 모드**: "이건 inline 으로 충분한가 vs subagent 가 나은가" 분기 판단 시도 자체가 `policy_violation_subdecision` — 분기 없이 항상 spawn.

## Usage

Orchestrator 코드 실행 전 체크리스트:
1. 현재 작업이 Inline whitelist 4-entry 중 하나인가? → Yes: inline OK. No: spawn 의무.
2. `Agent` tool 프롬프트에 `docs/stories/<KEY>.md` path 주입 → agent self-fetch.
3. 복수 독립 lane = 병렬 spawn (Track A ∥ Track B — playbook §3.1).
4. agent teams enabled context (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) 시: TeamCreate 패턴으로 전환 (ADR-044). whitelist invariant 유지.

## 정의

**Subagent-default discipline** 는 codeforge 를 이용한 **수정 작업** 진행 중 Orchestrator (top-level Claude 세션, ADR-009) 가 모든 work 을 `Agent` tool spawn 으로 수행하는 정책이다. "inline 으로 충분한가 vs subagent 가 나은가" 판단 분기 자체를 제거함으로써, 해당 분기가 유발하던 user-stop 패턴 (ADR-025 §결정 7 의 `policy_violation_subdecision`) 을 차단한다.

## 컨텍스트

본 정책은 ADR-009 (wrapper-only decomposition) 의 자연 확장이자 ADR-025 (stop discipline + Epic-level continuity) 의 motivation 직접 응답이다. wrapper Orchestrator 가 매 codeforge 수정 작업마다 발생시키던 "이건 inline 으로 충분한가 vs subagent 가 나은가" 결정 분기가 ADR-025 §결정 7 의 sub-decision stop 발화 채널로 작용해 왔다 (e.g. "후보 A/B/C/D 중 어떤거?", "큰 작업이라 확인 받겠습니다", "Phase 1 완료, Phase 2 시작할까요?"). 사용자 directive (2026-05-08, verbatim) "무조건 subagent만 하도록 하자. 그것 때문에 user stop이 자꾸 발생한다" + "codeforge를 이용한 수정 작업에서는 무조건 subagent이다" 가 본 정책의 직접 origin.

본 정책의 motivation 은 토큰 효율성 trade-off 수용을 전제로 한다 — 사용자 directive (ADR-035 §컨텍스트 verbatim) "agent teams 기능을 적극적으로 사용할 수 있도록... 토큰의 양 효율성은 중요하지 않다" 가 §"핵심 규칙" 의 always-spawn binary 정책 정당화 근거.

## 핵심 규칙

### 적용 범위 (codeforge orchestration scope)

본 정책은 **codeforge 를 이용한 수정 작업** 한정. 즉:

- file edit / write (`docs/**`, `src/**`, `templates/**` 등)
- GitHub state change (Issue / PR / comment / label / milestone / sub-issue)
- Story file write (§1-§14 어느 섹션이든)
- FIX Ledger append (§10 row append, fix-event-v1 contract)
- Lane-spawn evidence append (§14 row append, ADR-031)
- gate label transition (`gate:design-review-pass` 등)
- phase label transition (`phase:요구사항` → `phase:설계` 등)
- branch / PR creation / merge
- workflow yaml 수정·추가
- ADR / Change Plan / domain-knowledge 페이지 write
- trivial Read 1건 — **Read 도 subagent spawn 의무** (사용자 directive 명시)

### Inline 수행의 정의

"inline 수행" = Orchestrator 가 자체 turn 안에서 직접 tool 호출 (Read / Write / Edit / Bash / Grep / Glob / mcp__github__\* 등). Agent tool 경유하지 않음. 본 정책 하 codeforge 수정 작업에서는 금지.

"Subagent spawn" = `Agent` tool 호출 → 별도 Claude 세션 (subagent) 이 task 수행 → return. one-shot, continuous dialog 불가.

### 작업 vs 정보 답변 경계

| 사용자 메시지 패턴 | 분류 | Subagent 의무 |
|---|---|---|
| "X 진행" / "X 시작" / "X 적용" | 수정 작업 | ✅ 모든 sub-step subagent |
| "X 가 뭐냐" / "X 보여달라" | 정보 답변 | ❌ inline OK (단 file Read 가 발생하면 subagent) |
| "X 검토해줘" / "X 수정해줘" | 수정 작업 | ✅ |
| "X 어떻게 생각해" | conversational | ❌ inline OK |
| Yes/No 확답 | dialog | ❌ inline (subagent dialog 불가) |

모호 시 = **수정 작업 측 분류** (ADR-013 cutoff 정합 — 안전 방향).

### 측정 가능성

- **stop-event-v1 ledger** (ADR-025 §결정 10, Phase 2 deferred) 의 `reason_class: policy_violation_subdecision` row 수 ↓ → 정책 효과 검증.
- 정책 적용 전후 Story 별 user-stop count 비교 가능 (Phase 2 측정 채널 도입 후).

## 경계

### 비-적용 (inline 필수)

- **사용자 dialog** — `AskUserQuestion` / 확답 step / 정보 요청 답변. subagent 는 one-shot 이라 dialog 불가능 (ADR-009 §결정 + CLAUDE.md "플랫폼 제약").
- **일반 Q&A / conversational 응답** — codeforge orchestration 외 영역.
- **재귀 spawn** — Orchestrator (top-level) 가 직접 Agent tool 호출, subagent 가 다시 Agent tool 호출 금지 (platform inherent — CLAUDE.md "플랫폼 제약" 룰 무변).

### 관련 용어 분류

- **Orchestrator** (ADR-009): top-level Claude 세션. wrapper-only decomposition 후 codeforge core agent 0 개 — Orchestrator 가 6 lane plugin 의 agent 를 spawn.
- **Subagent**: Agent tool 로 spawn 된 별도 Claude 세션. one-shot, Agent tool 재호출 금지 (재귀 spawn limit), 서브에이전트 간 직접 통신 불가 (default subagent context — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0`).
- **Agent teams enabled context** (ADR-035, CFP-137 deferred): `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 시 sibling teammate 간 SendMessage 가능 + continuous dialog 가능. 본 정책의 "subagent" 는 default context 의 one-shot subagent 를 가리킴.
- **수정 작업 (modification work)**: 본 페이지 §"핵심 규칙 → 적용 범위" enumerated 행위.

### 다른 ADR 와의 interaction (비-충돌 영역)

**Sonnet decider trigger (ADR-022 Deprecated) 와의 conflict 부재** — ADR-022 가 CFP-134 / ADR-035 로 Deprecated 처리됨 (2026-05-08). 본 정책은 ADR-022 의 5 trigger 자동 발동 패턴 무관. 사용자 ad-hoc Sonnet 호출 시에도 본 정책 적용 — Sonnet 호출 자체가 subagent spawn (Agent tool with `model: sonnet`) 이므로 자연 정합.

**Stop discipline (ADR-025) 와의 motivation 연결** — ADR-025 Amendment 1 §결정 7 의 불법 stop 패턴 표 — "후보 A/B/C/D 중 어떤거?" / "큰 작업이라 확인 받겠습니다" / "Phase 1 완료, Phase 2 시작할까요?" — 모두 sub-decision stop. 본 정책은 이 패턴의 한 sub-class 인 **"이거 inline 으로 충분한가" stop** 을 정책 차원에서 제거. 본 정책은 ADR-025 의 5 종 whitelist 무변 — stop 발생 가능성을 줄이는 mechanism 이지 whitelist 자체를 변경하지 않는다.

**Phase execution visibility (ADR-029) 와의 interaction** — ADR-029 §결정 5 "Writer: Orchestrator 단독" — sub-step narration 은 Orchestrator 가 stderr 1-line 으로 발생. 본 정책 하에서는 매 subagent spawn / return 가 narrate 대상이 됨. ADR-029 의 narration 책임은 Orchestrator 가 subagent return 받은 직후 발화 — subagent 측 narration 의무 X.

**Lane-spawn evidence (ADR-031) 와의 interaction** — ADR-031 §결정 1 의 §14 row append 행위는 본 정책 하에서도 **Orchestrator self-write** 로 유지. 단 §14 row append 자체가 file write 행위이므로, append 작업도 subagent spawn 으로 수행 (즉 Orchestrator 가 "§14 row append 전용 subagent" 를 spawn 해 Edit tool 호출). lane plugin 측 변경 0 건 (ADR-031 §결과 invariant 무손상).

**TodoWrite scratchpad 와의 interaction** — TodoWrite tool surface = file write 아님 (Orchestrator turn meta channel — file system / GitHub state mutation 미발화). 본 정책 하에서도 TodoWrite 호출 자체는 Orchestrator inline 행위 (수정 작업 enumeration 미포함, ADR-039 §결정 2 Inline whitelist entry 2 standalone 정당화). TodoWrite 호출은 subagent spawn 의무 비-적용. (참고: ADR-038 = TodoWrite progress visualization 도입 informational reference, 본 분류의 normative dependency 아님.)

## 관련 ADR

- [ADR-009](../../adr/ADR-009-wrapper-only-decomposition.md) — wrapper-only decomposition. Orchestrator (top-level Claude 세션) 정의 + wrapper agent 0 개 invariant. 본 정책은 ADR-009 의 자연 확장 / explicit 격상.
- [ADR-025](../../adr/ADR-025-stop-discipline-non-whitelist-as-defect.md) — stop discipline + Epic-level continuity. §결정 7 의 `policy_violation_subdecision` sub-class "이거 inline 으로 충분한가" stop 을 mechanism level 에서 제거. 본 정책의 motivation source.
- [ADR-029](../../adr/ADR-029-phase-execution-visibility-expansion.md) — phase execution visibility expansion. Orchestrator stderr 1-line narration 의무. 매 subagent spawn / return 가 narrate 대상.
- [ADR-031](../../adr/ADR-031-lane-spawn-evidence-trail.md) — lane-spawn evidence trail. §14 row append ownership 무변 (Orchestrator monopoly), mechanism 만 spawn 으로 변경.
- [ADR-035](../../adr/ADR-035-codeforge-agent-teams-epic-architecture.md) — codeforge agent teams Epic. subagent semantics 분기 — 본 정책의 "subagent" = default subagent context (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0`) 의 one-shot subagent.

## 변경 이력

- **2026-05-08** — ArchitectAgent 신규 작성 (CFP-275 carrier Story Phase 1 PR scope, ADR-039 §결정 13 동일 PR commit batch).
- **2026-05-09** — frontmatter (status / topic_slug / updated 추가) + section schema (정의 / 컨텍스트 / 핵심 규칙 / 경계 / 관련 ADR / 변경 이력) 정합 (CFP-275 Iter 3 fix). 정책 wording 변경 없음 — content reflow only.
