---
title: Orchestrator Communication Incidents (Layer 4 누적 file)
status: Active
category: governance
date: 2026-05-14
carrier_story: CFP-612
related_adrs:
  - ADR-071
schema_version: "1.0"
---

# Orchestrator Communication Incidents

> Layer 4 누적 detection file ([ADR-071 §결정 6](adr/ADR-071-orchestrator-user-dialog-convergence.md)).
> owner = Orchestrator 단독 monopoly. append-only. cross-Story 영속 (Story 종료 시 reset 없음).
> M=5 max threshold 누적 시 사용자 escalation (`AskUserQuestion` 발화).
> reset 정책: manual archive only (yearly file rotate 또는 별 row delineator marker — 사용자 explicit reset request 시).

## Lifecycle 룰

1. **append-only** — Orchestrator 단독 row append. lane plugin / sub-agent / 사용자 manual edit 금지.
2. **cross-Story 영속** — Story 종료 시 row reset 없음. M=5 카운터 = lifetime 영속.
3. **pattern_dimension 분류** — [ADR-071 §결정 4](adr/ADR-071-orchestrator-user-dialog-convergence.md) 4 차원 enum 만 허용 (표현 / 결정 구조 / 보고 형식 / 질문 자체).
4. **사용자 escalation 후 다음 incident** — pattern_dimension 강제 전환 (sub-mechanism 2 정합).
5. **manual reset** — 사용자 explicit reset request 시에만 archive (별 file 분리 또는 row delineator marker 추가).
6. **scope** = wrapper repo only. consumer 측은 자기 repo 의 `docs/orchestrator-communication-incidents.md` 별 lifecycle.

## Schema

| Column | 의미 |
|---|---|
| iter | 누적 incident sequential id (전체 file 기준, 1 부터) |
| timestamp | KST ISO8601 |
| story_key | 발생 시점 active Story KEY (cross-Story 추적, 예: `CFP-612`) |
| pattern_dimension | 4 차원 enum (표현 / 결정 구조 / 보고 형식 / 질문 자체) |
| pattern_summary | 어떤 양상이 detect 됐는지 1 줄 |
| trigger | `layer-3-keyword` (사용자 "추상" keyword) / `layer-4-n1` (같은 양상 다음 turn 재발) / `layer-4-m5` (escalation `AskUserQuestion`) |
| different_dimension_after_halt | Sub-mechanism 1 — "이전과 다르게 한 점" 1 줄 (재작성 직후 동일 row 갱신) |
| escalation_outcome | `layer-4-m5` trigger 시 사용자 답변 요약 (`AskUserQuestion` outcome). 다른 trigger 시 비어있음 |

## Incidents

| iter | timestamp | story_key | pattern_dimension | pattern_summary | trigger | different_dimension_after_halt | escalation_outcome |
|------|-----------|-----------|-------------------|-----------------|---------|-------------------------------|--------------------|

<!-- 비어있는 table — Orchestrator 가 incident detect 시 row append.
     ADR-071 §결정 6 schema 준수. -->

## 관련 파일

- [ADR-071](adr/ADR-071-orchestrator-user-dialog-convergence.md) — carrier ADR
- [docs/orchestrator-playbook.md §3.14](orchestrator-playbook.md) — frame mode + 4 layer + sub-mechanism 본문 SSOT
- [skills/user-dialog-mode/SKILL.md](../skills/user-dialog-mode/SKILL.md) — frame mode + 4 layer lookup table
