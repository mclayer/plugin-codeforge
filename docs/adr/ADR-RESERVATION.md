---
adr_number: null
title: ADR 번호 예약 레지스트리 (GitOpsAgent 전용 운영 레지스트리)
status: Active
category: governance
date: 2026-05-09
carrier_story: CFP-344
related_adrs:
  - ADR-050
related_files:
  - docs/parallel-work/section-ownership.yaml
  - templates/github-workflows/parallel-epic-conflict-check.yml
is_transitional: false
---

# ADR 번호 예약 레지스트리

## 상태

Active (2026-05-09) — ADR-050 §결정 1 구현. GitOpsAgent 전용 sequential append 레지스트리.

## 컨텍스트

복수 Orchestrator 세션이 동시에 서로 다른 에픽을 진행할 때 두 세션이 같은 ADR 번호로 파일을 생성하는 충돌이 발생한다 (ADR-048 중복 사례 실증). ADR-050 §결정 1에서 이 문제를 해결하기 위해 본 레지스트리를 신설했다.

**Write 주체**: GitOpsAgent 전용 (sequential append).
**충돌 해소**: 두 세션 동시 append → git merge positional conflict → GitOpsAgent가 adr_number 오름차순 re-sort.

## 결정

GitOpsAgent가 본 레지스트리를 통해 ADR 번호를 원자적으로 예약한다.

### 예약 절차

1. ArchitectAgent가 ADR 필요 신호 발신
2. GitOpsAgent가 마지막 `adr_number` + 1을 append → commit
3. ArchitectAgent가 예약된 번호로 `ADR-NNN-*.md` 생성
4. ADR merge 완료 후 `status: reserved → active`로 갱신

### 레지스트리 YAML 스키마

```yaml
reservations: []
# 형식:
# - adr_number: NNN
#   epic: CFP-XXX
#   status: reserved   # reserved | active | archived
#   reserved_at: ISO8601
```

## 결과

### 현재 예약 목록

| adr_number | epic | status | reserved_at |
|---|---|---|---|
| 50 | CFP-344 | active | 2026-05-09 |
| 51 | CFP-343 | active | 2026-05-09 |
| 54 | CFP-363 | active | 2026-05-10 |
| 55 | CFP-367 | reserved | 2026-05-10 |
| 56 | CFP-374 | active | 2026-05-11 |
| 57 | CFP-379 | reserved | 2026-05-11 |
| 58 | CFP-387 | active | 2026-05-11 |
| 59 | CFP-391 | reserved | 2026-05-11 |
| 60 | CFP-389 | active | 2026-05-11 |
| 61 | CFP-423 | active | 2026-05-12 |
| 62 | CFP-407 | active | 2026-05-12 |
| 63 | CFP-436 | active | 2026-05-12 |
| 64 | CFP-445 | active | 2026-05-12 |
| 65 | CFP-438 | active | 2026-05-13 |
| 66 | CFP-521 | active | 2026-05-13 |
| 67 | CFP-526 | active | 2026-05-13 |
| 68 | CFP-527 | active | 2026-05-13 |
| 69 | CFP-342 | active | 2026-05-13 (retroactive — CFP-570 renumber from collided ADR-050; ADR file = `ADR-069-multi-repo-story-key-system.md`) |
| 70 | CFP-578 | active | 2026-05-13 (ArchitectAgent inline append per CFP-578 chief author scope — GitOpsAgent self-write 영역 inline carrier 정합. ADR file = `ADR-070-codex-verify-before-trust.md`) |
| 71 | CFP-612 | active | 2026-05-13 (ArchitectAgent inline append per CFP-578 / ADR-070 chief author precedent. ADR file = `ADR-071-orchestrator-user-dialog-convergence.md`, status `reserved → active` 전환 2026-05-14 Phase 1) |
| 72 | CFP-620 | active | 2026-05-14 (mctrader 3-cycle post-mortem Epic — Story-1 anchor ADR. ADR file = `ADR-72-production-evidence-deputy-and-epic-cutover-gate.md`. status `reserved → active` 전환 2026-05-14 Phase 1 PR #651 merged) |
| 73 | CFP-622 | active | 2026-05-14 (Sentinel #4 strike #2 carrier — Orchestrator verify-before-assert. ADR-070 자매 ADR. ADR file = `ADR-073-orchestrator-verify-before-assert.md`) |
| 74 | CFP-708 | reserved | 2026-05-14 (ArchitectAgent inline append per CFP-578 / ADR-070 chief author precedent. CFP-477 retro §6 후보 3 `escalation_action: adr_draft_emitted` carrier — CLAUDE.md Amendment ref drift detection lint. ADR file = `ADR-074-claude-md-amendment-ref-drift-lint.md`) |

### 번호 해제 (archived)

ADR deprecated/superseded 시 해당 row `status: archived`. 번호 재사용 금지.

## 해소 기준

N/A — permanent policy

## 관련 파일

- [ADR-050](ADR-050-parallel-epic-conflict-coordination.md) — 본 레지스트리 결정의 carrier ADR
- `docs/parallel-work/section-ownership.yaml` — ADR-050 §결정 4 (locked 섹션 선언)
- `templates/github-workflows/parallel-epic-conflict-check.yml` — ADR-050 §결정 3 (자동 충돌 감지)
