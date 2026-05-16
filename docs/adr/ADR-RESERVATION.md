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
| 74 | CFP-708 | active | 2026-05-14 (ArchitectAgent inline append per CFP-578 / ADR-070 chief author precedent. CFP-477 retro §6 후보 3 `escalation_action: adr_draft_emitted` carrier — CLAUDE.md Amendment ref drift detection lint. ADR file = `ADR-074-claude-md-amendment-ref-drift-lint.md`, status `reserved → active` 전환 2026-05-15 Phase 1 PR #711 merged) |
| 75 | CFP-709 | active | 2026-05-14 (Defense-in-depth sublayer registry — ADR-063 §결정 5 본문 표 sublayer enumeration 영역 의 kind:registry 분리. 3 carrier 누적 마찰 evidence: CFP-441/447/477. ADR file = `ADR-075-defense-in-depth-sublayer-registry.md`) |
| 76 | CFP-701 | active | 2026-05-15 (CFP-699 Epic Wave 1 Story-1 carrier — declarative reconciliation upgrade flow SSOT. ADR-074 / ADR-075 (CFP-708 / CFP-709 chronological precedence resolution per PR #712 verbatim, 2026-05-15) 점유 결과 CFP-701 = ADR-076 swap. User-confirmed Branch A (2026-05-15 KST, codeforge:user-dialog-mode skill 경유). ArchitectAgent inline append per ADR-070 / CFP-578 chief author precedent. ADR file = `ADR-076-declarative-reconciliation-upgrade.md`. Note: ADR-74/75 row append 는 CFP-708/709 carrier 책임 — 본 row 는 CFP-701 단독 self-write.) |
| 77 | CFP-759 | active | 2026-05-16 KST (GitOpsAgent sequential append — 요구사항 레인 clarification 강제 재조사 전파 정책 SSOT. RequirementsPL clarification 답변 수신 시 전 에이전트 재조사 강제 + 조건부 PMO 합류 + design-reading fan-out + stale 게이트 + 안전 envelope 정책 anchor ADR. status `reserved → active` 전환 2026-05-16 KST Story-1 Phase 1 — ADR file = `ADR-077-clarification-forced-reinvestigation-propagation.md`. ArchitectAgent direct write per CFP-759 chief author scope — ADR-070 / CFP-578 precedent.) |
| 78 | Epic B (사안 3, TBD CFP) | reserved | 2026-05-16 KST (GitOpsAgent sequential append — 설계 레인 영속 구조 설계 문서 유지 정책 SSOT. 설계 레인이 Story key 독립 살아있는 구조 설계 문서를 매 실행 갱신 + 게이트 + 드리프트 체크, Change Plan 델타와 상보적 현재 상태 SSOT anchor ADR.) |
| 79 | CFP-770 | active | 2026-05-16 KST (ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent — KST timestamp display mandate (Layer-bounded) SSOT. governance display layer 영속 artifact 시각 = KST `+09:00` ISO 8601 zoned 강제 / contract field layer (7 contract + Story §14 schema field) = UTC strict 0건 변경 invariant. status `reserved` 미경유 직접 `active` (Epic 비소속 단일 Story carrier, ADR-077 row 77 precedent 정합). ADR file = `ADR-079-kst-timestamp-display-mandate.md`. Phase 2 mechanical lint = CFP-771 (blocks-on CFP-770) Amendment 1 carrier.) |
| 80 | CFP-751 | active | 2026-05-16 KST (Orchestrator Lead-conducted per ADR-070 / CFP-578 precedent — Agent role terminology canonical standardization SSOT: "deputy" 일반 명사 → "SubAgent" canonical form, `*DeputyAgent` 고유 식별자 + `codeforge:deputy-mandate` skill name + "Deputy mandate 매트릭스" 개념명 보존. Class-A (general noun, 치환) vs Class-B (identifier/concept, 보존) 분류 규칙. cross-plugin sibling sync 적용 (ADR-010, codeforge-design plugin). 사용자 directive: "deputy라는 표현을 쓰는데... agent로 못박아라" + "남발하지만 않으면 된다. 기존 Deputy로 명명한 Agent 명은 두고 SubAgent로 치환 가능한 경우". forbid-list 아님 (ADR-064 카테고리 a 미등록 — 용어 표준화 가이드라인). status `reserved` 미경유 직접 `active` (ADR-079 row 79 precedent 정합). ADR file = `ADR-080-agent-role-terminology-deputy-subagent.md`.) |

### 번호 해제 (archived)

ADR deprecated/superseded 시 해당 row `status: archived`. 번호 재사용 금지.

## 해소 기준

N/A — permanent policy

## 관련 파일

- [ADR-050](ADR-050-parallel-epic-conflict-coordination.md) — 본 레지스트리 결정의 carrier ADR
- `docs/parallel-work/section-ownership.yaml` — ADR-050 §결정 4 (locked 섹션 선언)
- `templates/github-workflows/parallel-epic-conflict-check.yml` — ADR-050 §결정 3 (자동 충돌 감지)
