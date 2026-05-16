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
| trigger | `layer-3-keyword` (사용자 "추상" keyword) / `layer-4-n1` (같은 양상 다음 turn 재발) / `layer-4-m5` (escalation `AskUserQuestion`). retroactive baseline row 는 cell 에 `backfill (...)` marker 사용 — soft enum extension, schema/structure 무변경. |
| different_dimension_after_halt | Sub-mechanism 1 — "이전과 다르게 한 점" 1 줄 (재작성 직후 동일 row 갱신) |
| escalation_outcome | `layer-4-m5` trigger 시 사용자 답변 요약 (`AskUserQuestion` outcome). 다른 trigger 시 비어있음 |

## Incidents

| iter | timestamp | story_key | pattern_dimension | pattern_summary | trigger | different_dimension_after_halt | escalation_outcome |
|------|-----------|-----------|-------------------|-----------------|---------|-------------------------------|--------------------|
| 1 | 2026-05-14 22:36 | CFP-672 | 보고 형식 | stale SessionStart snapshot 을 ground truth 로 보고·진행 → parallel 세션 merge(`270ae26`) 미인지, ~30분 duplicate work | backfill (retroactive baseline — not realtime layer-3/4 detect) | N/A — backfill (no halt-rewrite cycle) |  |
| 2 | 2026-05-15 03:16 | CFP-701 | 보고 형식 | git log 0-hit 만으로 "정상 진행" 보고 → open PR ADR-claim scan 누락, ArchitectPL 단계 뒤늦은 ESCALATE (CFP-672 와 동일 dimension 재발) | backfill (retroactive baseline — not realtime layer-3/4 detect) | N/A — backfill (no halt-rewrite cycle) |  |
| 3 | 2026-05-15 12:00 | CFP-707 | 질문 자체 | multi-PR version field contention 을 묻지 않고 plugin.json bump 단정 진행 → cascade collision, Pause-and-resume | backfill (retroactive baseline — not realtime layer-3/4 detect) | N/A — backfill (no halt-rewrite cycle) |  |
| 4 | 2026-05-16T08:42:00+09:00 | CFP-750 | 보고 형식 | 백그라운드 task (codex:codex-rescue boroux55j) dispatch 후 liveness gate 부재로 ~2h silent hang 동안 Orchestrator 가 deputy idle notification 에 응답하며 "대기"만 수동 반복. Codex output mtime / content 미점검. 같은 dispatch-and-forget pattern 이 동일 세션 내 누적 (story-init §1 파서 silent empty #753, 팀원 inbox delivery gap). | layer-4-n1 | dispatch 시점부터 max-wait timeout + 능동 liveness 점검 (output mtime + content grep) + stall 시 fallback path 사전 정의로 차원 전환 (passive 대기 보고 → 능동 liveness gate). 사용자 발화 "멈춰있는거 같은데? 이런 일이 왜자꾸 반복되나 이거 개선해야할듯" = improvement directive → codeforge-improvement Story #763 carrier 발의로 normative 반영. | (codeforge-improvement Story #763 carrier 발의) |
| 5 | 2026-05-16T18:13:00+09:00 | CFP-750 Phase 2 | 보고 형식 | CFP-750 Phase 2 구현 lane 안 ack-pattern 9-10 dual instance 추가 — (9) DeveloperAgent 32분 무응답 (DeveloperPL 4 directive 무시, perf fix 미적용 lint script mtime 17:48 고정) = passive-non-response form / (10) passive-work-no-report WIP drift (DeveloperAgent + InfraEngineer sweep 12 file / workflow / plugin.json / registry 작업했으나 commit·보고 0, DeveloperPL ground-truth verify 후 적발) = passive-work form. cumulative CFP-750 session 안 ack-pattern 10 instance 도달 (Phase 1 lane 8 + Phase 2 구현 lane 2). Orchestrator Lead-conducted recovery (ad37af6 perf override + f621f27 atomic recovery + 57e8f8e ADR-037 sweep) 로 silent failure 차단. | layer-4-n1 (active-detect, DeveloperPL ground-truth verify 결과 Orchestrator escalate) | passive 보고 형식 mitigation → **구조적 enforcement hook 차원 전환** — turn-by-turn 사용자 dialog discipline (Iter 4 carrier) 으로는 부족, **mechanical timeout + required-progress-marker + commit-evidence verify** 가 필요. #763 framework Story scope 확장 후보 3종: (a) background-task-liveness-gate (Iter 4 carrier 영역) + (b) **agent-non-response-timeout** (9th carrier — agent dispatch 후 N분 progress-marker 부재 시 자동 escalate) + (c) **passive-work-detection** (10th carrier — agent worktree `git status` 자동 audit hook + 미commit WIP 자동 surface). dimension shift = "Orchestrator 자가 검열 self-discipline" → "agent-team structural enforcement (mechanical hook)" — ADR-071 Sub-mechanism 2 정합. | (CFP-750 Phase 2 merge 완료 후 #763 framework Story scope 확장 안건 후속 — Iter 4 carrier 보강 후보) |

<!-- 비어있는 table — Orchestrator 가 incident detect 시 row append.
     ADR-071 §결정 6 schema 준수. -->

## 관련 파일

- [ADR-071](adr/ADR-071-orchestrator-user-dialog-convergence.md) — carrier ADR
- [docs/orchestrator-playbook.md §3.14](orchestrator-playbook.md) — frame mode + 4 layer + sub-mechanism 본문 SSOT
- [skills/user-dialog-mode/SKILL.md](../skills/user-dialog-mode/SKILL.md) — frame mode + 4 layer lookup table
