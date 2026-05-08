---
type: domain-knowledge
area: orchestrator-discipline
topic: spawn-default
title: Subagent-default Orchestrator execution discipline (codeforge modification work)
related_adrs:
  - ADR-009  # wrapper-only decomposition (Orchestrator definition)
  - ADR-025  # stop discipline (motivation)
  - ADR-029  # phase execution visibility (narration interaction)
  - ADR-031  # lane-spawn evidence (§14 row append행위)
  - ADR-035  # agent teams Epic (subagent semantics)
  - ADR-038  # progress visualization TodoWrite (channel interaction)
related_stories:
  - CFP-275
created: 2026-05-08
---

# Subagent-default Orchestrator execution discipline

## 개념 정의

**Subagent-default discipline** 는 codeforge 를 이용한 **수정 작업** 진행 중 Orchestrator (top-level Claude 세션, ADR-009) 가 모든 work 을 `Agent` tool spawn 으로 수행하는 정책이다. "inline 으로 충분한가 vs subagent 가 나은가" 판단 분기 자체를 제거함으로써, 해당 분기가 유발하던 user-stop 패턴 (ADR-025 §결정 7 의 `policy_violation_subdecision`) 을 차단한다.

## 작동 원리

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

### 비-적용 (inline 필수)

- **사용자 dialog** — `AskUserQuestion` / 확답 step / 정보 요청 답변. subagent 는 one-shot 이라 dialog 불가능 (ADR-009 §결정 + CLAUDE.md "플랫폼 제약").
- **일반 Q&A / conversational 응답** — codeforge orchestration 외 영역.
- **재귀 spawn** — Orchestrator (top-level) 가 직접 Agent tool 호출, subagent 가 다시 Agent tool 호출 금지 (platform inherent — CLAUDE.md "플랫폼 제약" 룰 무변).

### 작업 vs 정보 답변 경계

| 사용자 메시지 패턴 | 분류 | Subagent 의무 |
|---|---|---|
| "X 진행" / "X 시작" / "X 적용" | 수정 작업 | ✅ 모든 sub-step subagent |
| "X 가 뭐냐" / "X 보여달라" | 정보 답변 | ❌ inline OK (단 file Read 가 발생하면 subagent) |
| "X 검토해줘" / "X 수정해줘" | 수정 작업 | ✅ |
| "X 어떻게 생각해" | conversational | ❌ inline OK |
| Yes/No 확답 | dialog | ❌ inline (subagent dialog 불가) |

모호 시 = **수정 작업 측 분류** (ADR-013 cutoff 정합 — 안전 방향).

### Inline 수행의 정의

"inline 수행" = Orchestrator 가 자체 turn 안에서 직접 tool 호출 (Read / Write / Edit / Bash / Grep / Glob / mcp__github__\* 등). Agent tool 경유하지 않음. 본 정책 하 codeforge 수정 작업에서는 금지.

"Subagent spawn" = `Agent` tool 호출 → 별도 Claude 세션 (subagent) 이 task 수행 → return. one-shot, continuous dialog 불가.

## 관련 용어

- **Orchestrator** (ADR-009): top-level Claude 세션. wrapper-only decomposition 후 codeforge core agent 0 개 — Orchestrator 가 6 lane plugin 의 agent 를 spawn.
- **Subagent**: Agent tool 로 spawn 된 별도 Claude 세션. one-shot, Agent tool 재호출 금지 (재귀 spawn limit), 서브에이전트 간 직접 통신 불가 (default subagent context — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0`).
- **Agent teams enabled context** (ADR-035, CFP-137 deferred): `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 시 sibling teammate 간 SendMessage 가능 + continuous dialog 가능. 본 정책의 "subagent" 는 default context 의 one-shot subagent 를 가리킴.
- **수정 작업 (modification work)**: 본 페이지 §"적용 범위" enumerated 행위.

## 주의점

### Sonnet decider trigger (ADR-022 Deprecated) 와의 conflict 부재

ADR-022 가 CFP-134 / ADR-035 로 Deprecated 처리됨 (2026-05-08). 본 정책은 ADR-022 의 5 trigger 자동 발동 패턴 무관. 사용자 ad-hoc Sonnet 호출 시에도 본 정책 적용 — Sonnet 호출 자체가 subagent spawn (Agent tool with `model: sonnet`) 이므로 자연 정합.

### Stop discipline (ADR-025) 와의 motivation 연결

ADR-025 Amendment 1 §결정 7 의 불법 stop 패턴 표 — "후보 A/B/C/D 중 어떤거?" / "큰 작업이라 확인 받겠습니다" / "Phase 1 완료, Phase 2 시작할까요?" — 모두 sub-decision stop. 본 정책은 이 패턴의 한 sub-class 인 **"이거 inline 으로 충분한가" stop** 을 정책 차원에서 제거.

본 정책은 ADR-025 의 5 종 whitelist 무변. 본 정책은 stop 발생 가능성을 줄이는 mechanism 이지 whitelist 자체를 변경하지 않는다.

### Phase execution visibility (ADR-029) 와의 interaction

ADR-029 §결정 5 "Writer: Orchestrator 단독" — sub-step narration 은 Orchestrator 가 stderr 1-line 으로 발생. 본 정책 하에서는 매 subagent spawn / return 가 narrate 대상이 됨. ADR-029 의 narration 책임은 Orchestrator 가 subagent return 받은 직후 발화 — subagent 측 narration 의무 X.

### Lane-spawn evidence (ADR-031) 와의 interaction

ADR-031 §결정 1 의 §14 row append 행위는 본 정책 하에서도 **Orchestrator self-write** 로 유지. 단 §14 row append 자체가 file write 행위이므로, append 작업도 subagent spawn 으로 수행 (즉 Orchestrator 가 "§14 row append 전용 subagent" 를 spawn 해 Edit tool 호출). lane plugin 측 변경 0 건 (ADR-031 §결과 invariant 무손상).

### TodoWrite (ADR-038) 와의 interaction

ADR-038 §결정 — TodoWrite 는 Orchestrator 단독 channel. 본 정책 하에서도 TodoWrite 호출 자체는 Orchestrator inline 행위 (file write 아님 — meta progress channel). TodoWrite 호출은 subagent spawn 의무 비-적용.

### 측정 가능성

- **stop-event-v1 ledger** (ADR-025 §결정 10, Phase 2 deferred) 의 `reason_class: policy_violation_subdecision` row 수 ↓ → 정책 효과 검증.
- 정책 적용 전후 Story 별 user-stop count 비교 가능 (Phase 2 측정 채널 도입 후).

## 참조

- [ADR-009](../../adr/ADR-009-wrapper-only-decomposition.md) — Orchestrator 정의
- [ADR-025](../../adr/ADR-025-stop-discipline-non-whitelist-as-defect.md) — stop discipline (motivation)
- [ADR-029](../../adr/ADR-029-phase-execution-visibility-expansion.md) — Orchestrator narration
- [ADR-031](../../adr/ADR-031-lane-spawn-evidence-trail.md) — §14 evidence write
- [ADR-035](../../adr/ADR-035-codeforge-agent-teams-epic-architecture.md) — agent teams Epic (subagent semantics 분기)
- [ADR-038](../../adr/ADR-038-progress-visualization-todowrite.md) — TodoWrite channel
- CLAUDE.md "오케스트레이션 규칙" §"Default subagent context" + "플랫폼 제약" — subagent 룰
