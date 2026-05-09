---
adr_number: 52
title: Codex Proactive Check — 6 Touchpoints
date: 2026-05-09
status: Proposed
category: workflow-policy
carrier_story: CFP-354
parent_epic: null
supersedes: null
amends: null
amendments: []
related_stories:
  - CFP-354
related_adrs:
  - ADR-039
  - ADR-034
  - ADR-044
related_files:
  - docs/orchestrator-playbook.md
  - docs/superpowers-integration.md
  - CLAUDE.md
---

# ADR-052: Codex Proactive Check — 6 Touchpoints

## 상태

**Proposed (2026-05-09)** — CFP-354 carrier story.

## 컨텍스트

Orchestrator(Claude)가 설계 레인 등에서 "꼬임" 현상이 발생한다:
- 6 deputy 산출물 통합 시 모순·순환 논리·누락이 생겨도 스스로 포착 불가
- AskUserQuestion 품질이 낮으면 모든 레인의 사용자 결정이 부정확해짐
- FIX root cause 판정이 단일 판정자(ArchitectPLAgent)에 의존 — 오판 시 레인 2~3개 재실행
- RequirementsPLAgent §1-§6 통합 후 설계 진입 전 독립 검증 없음

기존 `codex:rescue`는 **사후 대응(reactive)** 채널 — stuck 상황에서만 호출. 이 ADR은 **사전 예방(proactive)** 채널을 별도로 정의한다.

## 결정

### D1. Codex Proactive Check = Orchestrator inline dispatch

Orchestrator가 6개 touchpoint에서 `Agent(subagent_type="codex:codex-rescue")` 를 proactive check 용도로 자동 dispatch. 기존 codex:rescue(reactive) 와 채널 분리.

**거절된 대안**:
- (A) CodexReviewAgent 재사용: review lane 전용 설계 패턴 경계 침범
- (B) codex:rescue 확장: reactive 의미 희석, proactive/reactive 혼합으로 디버깅 어려움

### D2. 6개 touchpoint 전부 자동 활성

모든 touchpoint는 트리거 조건 충족 시 항상 자동 dispatch. opt-in 없음. 단, #3(Dev Rescue)는 "FIX 2+ 반복 동일 이슈" 조건이 트리거.

### D3. ProactiveCheckPacket v1 스키마

```yaml
touchpoint: <1|2|3|4|5|6>
purpose: <한 줄 목적>
context:
  lane: <requirements|design|develop|orchestrator>
  story_key: <CFP-NNN>
  artifacts: <첨부 산출물>
task: <Codex에게 요청할 구체적 작업>
```

출력: `{findings: [{severity: P0|P1|P2, description}], recommendation: PROCEED|ADDRESS_FIRST, rationale}`

### D4. #5 FIX Root Cause 불일치 = 사용자 에스컬레이션

Codex와 ArchitectPLAgent 판정 불일치 시 자동 proceed 금지 — 사용자가 최종 판정.

## 결과

- 6개 touchpoint playbook §3.10에 문서화
- Orchestrator 행동 변화: 각 트리거 시점에 codex:codex-rescue dispatch 의무화
- codex:rescue(reactive) 채널 동작 변경 없음
- CodexReviewAgent 역할 변경 없음
- 문서 전용 변경 (코드/agent file 변경 0건)

## 관련 파일

- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) — §3.10 신설 (6개 touchpoint 상세)
- [`docs/superpowers-integration.md`](../superpowers-integration.md) — §2 표 6행 추가 (24→30 호출 지점)
- [`CLAUDE.md`](../../CLAUDE.md) — 오케스트레이션 규칙 섹션 Codex Proactive Check 정책 blockquote 추가
