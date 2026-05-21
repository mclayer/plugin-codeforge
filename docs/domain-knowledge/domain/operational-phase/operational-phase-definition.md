---
kind: domain_fact
type: domain-knowledge
area: operational-phase
topic_slug: operational-phase-definition
title: 운영 phase 전체 정의 narrative
status: Active
tags:
  - operational-phase
  - release-lifecycle
  - mechanism-layer
  - story-flow-mismatch
  - cfp-1190
related_adrs:
  - ADR-104  # normative SSOT — §결정 1·2·5 의 elaborate (본 파일 전체)
  - ADR-087  # Deploy lane 신설 — 운영 phase 의 release lifecycle 선행 단계
  - ADR-088  # Deploy Review lane 신설 — "한 번 끝나는" 검증 경계 SSOT (§결정 3, L109)
  - ADR-023  # lane plugin lifecycle — lane count invariant (운영 phase = 9번째 lane 아님)
  - ADR-045  # §D-9 retro pattern (loop 답습 source)
related_stories:
  - CFP-1190  # 본 carrier
  - CFP-1187  # umbrella Epic
created: 2026-05-22
updated: 2026-05-22
---

# 운영 phase 전체 정의 narrative

> **normative SSOT**: [`docs/adr/ADR-104-operational-phase-definition.md`](../../../adr/ADR-104-operational-phase-definition.md). 본 파일은 ADR-104 §결정 1·2·5 의 서술적 elaboration 이다 — 결정 자체는 ADR-104 가 확정한다.

## 정의

**운영 phase** = 배포검토(deploy-review) lane 이 끝난 *이후* 시간축에서 **지속(ongoing)** 으로 배포 때 약속한 성능·안정성이 실제 지켜지는지 신호를 회수하는 단계. "한 번 끝나는" 배포검토와 달리, 운영 phase 는 **계속 도는** 구조다 (ADR-104 §결정 1).

운영 phase 는 codeforge 의 **9번째 lane 이 아니다**. lane 은 "Story 가 들어가 종료 게이트를 통과하고 끝나는" Story-scoped delta 구조인데, 운영 phase 의 시간축 ongoing 성격은 이 구조에 들어맞지 않는다. 따라서 운영 phase 는 **mechanism layer** (monitor / alert / 자동 Issue 생성 — cron workflow / filesystem signal) 로 실현된다 (ADR-104 §결정 2).

## 컨텍스트

### release lifecycle 위치

```
요구사항
  → 설계 → 설계 리뷰
  → 구현 → 구현 리뷰
  → 통합 테스트 → 보안 테스트
  → 배포 (Deploy lane, ADR-087)
  → 배포 검토 (Deploy Review lane, ADR-088)
  → [운영 phase: ongoing 신호 회수]   ← ADR-104 정의 영역
```

운영 phase 는 release lifecycle 의 **시간축 마지막 ongoing 단계**다 (ADR-104 §결정 1).

### 각 단계의 성격

| 단계 | 성격 | SSOT |
|---|---|---|
| 배포 (deploy) | Story-scoped — blue-green swap / atomic rollout | ADR-087 |
| 배포검토 (deploy-review) | Story-scoped, 한 번 끝나는 — smoke / 성능 비교 / cutover 사후 검증 | ADR-088 §결정 3 |
| **운영 phase** | **ongoing, 계속 도는** — 배포 약속 이행 지속 감시 | **ADR-104** |

### 근본 mismatch — ongoing ↔ Story flow

codeforge 의 lane 은 Story-scoped 구조 (종료 게이트 포함). 운영 phase 의 "계속 도는" 성격은 이 구조에 들어맞지 않는다:

- 어떤 Story 가 들어가야 하는가? (없다 — 운영 phase 는 특정 Story 에 귀속되지 않는다)
- 어떤 PL 이 PASS 를 반환하는가? (없다 — ongoing 이므로 종료가 없다)

만약 운영 phase 를 9번째 lane 으로 신설하면 ADR-023 lane count invariant 와 충돌하고, lane 의 종료-게이트 의미가 무너진다.

**mismatch 해소**: "운영 phase 의 Story 단위" = mechanism 을 신설하는 작업 자체 (S4~S7 Story). 그 Story 가 배포되면 이후 mechanism 이 ongoing 으로 돈다. Story 는 끝나지만 mechanism 은 계속 돈다.

## 핵심 규칙

### mechanism layer 실현 (ADR-104 §결정 2)

| mechanism | 역할 | 시간 성격 |
|---|---|---|
| cron workflow | 주기적 신호 회수 (에러율 / health check 주기 실행) | 계속 도는 |
| filesystem signal | cron 결과 로컬 기록 (0 API call constraint 정합) | 계속 도는 |
| 자동 Issue 생성 | 임계 초과 시 GitHub Issue 자동 생성 → Story 후보 | event-driven |

### 정합 invariant

- **lane count 변경 0** — 운영 phase 는 lane plugin 신설을 수반하지 않는다 (ADR-023 정합)
- **`phase:운영` label 신설 불요** — `phase:*` label 은 Story-scoped lane 전용. 운영 신호 Issue 는 일반 Story/Epic 후보 label 체계
- **mechanism 실 구현 = 후속 Story carrier** — 실 구현 (workflow yml / script) 는 S4~S7 영역

### "한 번 끝나는" vs "계속 도는" 경계

**배포검토 (한 번 끝나는)**: 배포 완료 직후 1회 — production smoke / 성능 비교 / cutover 사후 검증. lane PASS 반환 후 종료 (ADR-088 §결정 3, L109).

**운영 phase (계속 도는)**: 배포검토 PASS 이후 시간이 흐르면서 지속. 초기에 보이지 않던 에러가 점진적으로 드러나고, 트래픽 패턴 변화에 따라 latency burn rate 가 달라지며, 다음 배포와의 regression 이 나중에야 발견될 수 있다.

## 경계

### 포함 (운영 phase 관할)

- 배포 이후 시간축 ongoing 신호 회수
- 에러율 / latency burn rate / regression / smoke·health 측정 (상세: `measurement-channel.md`)
- 신호 초과 시 자동 Issue 생성 → self-improving loop 입력 (상세: `self-improving-loop.md`)
- 자동 rollback 신호 회수 (S2 에서 정량 임계 정의 예정)

### 제외 (운영 phase 비관할)

| 제외 영역 | 담당 |
|---|---|
| 배포 실행 절차 (blue-green swap / atomic rollout) | ADR-087 / DeployPLAgent |
| 배포 직후 1회 smoke / 성능비교 / cutover 사후검증 | ADR-088 / DeployReviewPLAgent |
| 운영 실행 절차 결정 (OpsExecutionArchitect) | CFP-1079 disjoint |
| 운영 phase mechanism 실 구현 (workflow yml / script) | S4~S7 |
| loop closure gate 실 구현 (dedup / max-depth / 사용자 gate) | S6 |
| wrapper(codeforge 자체) 실측 | N/A — declarative SSOT only (wrapper-N/A invariant) |
| 정량 신호 임계 구체값 | S2 (ADR-104 §결정 5 원칙 선언, 실 수치 0) |

### 인접 영역 disjoint 표

| 영역 | 시간 성격 | 운영 phase 와의 관계 |
|---|---|---|
| 8 lane (요구사항~배포검토) | Story-scoped (delta + 종료 게이트) | disjoint — 운영 phase 는 lane 아님 |
| 배포검토 lane | 한 번 끝나는 (일회성) | disjoint — 배포검토 *이후* 가 운영 phase |
| **운영 phase** | **계속 도는 (ongoing)** | **본 파일 정의 영역** |
| 운영 실행 절차 결정 | decision axis | disjoint axis (CFP-1079 예정) |

## 관련 ADR

- [ADR-104](../../../adr/ADR-104-operational-phase-definition.md) — **normative SSOT** (운영 phase 1st-class 정의 — §결정 1·2·5)
- [ADR-087](../../../adr/ADR-087-deploy-lane-and-lifecycle-extension.md) — Deploy lane 신설 (선행 단계)
- [ADR-088](../../../adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md) — Deploy Review lane ("한 번 끝나는" + L81 운영 phase 별 Epic origin)
- [ADR-023](../../../adr/ADR-023-lane-plugin-lifecycle.md) — lane plugin lifecycle (lane count invariant)
- [ADR-045](../../../adr/ADR-045-story-retro-mandatory-trigger.md) — §D-9 retro pattern (self-improving loop 답습 source)

## 변경 이력

| 버전 | 날짜 | 변경 내용 | carrier |
|---|---|---|---|
| v1.0 | 2026-05-22 | 신설 — 운영 phase 전체 정의 narrative (CFP-1190 Phase 2) | CFP-1190 |
