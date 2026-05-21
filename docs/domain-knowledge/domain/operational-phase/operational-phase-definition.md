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
  - ADR-104  # normative SSOT — 본 파일의 모든 서술은 ADR-104 §결정 1·2·5 의 elaborate
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

## §1. release lifecycle 위치

### 전체 흐름

```
요구사항
  → 설계
  → 설계 리뷰
  → 구현
  → 구현 리뷰
  → 통합 테스트
  → 보안 테스트
  → 배포 (Deploy lane, ADR-087)
  → 배포 검토 (Deploy Review lane, ADR-088)
  → [운영 phase: ongoing 신호 회수]   ← 본 ADR-104 정의 영역
```

운영 phase 는 release lifecycle 의 **시간축 마지막 ongoing 단계**다 (ADR-104 §결정 1). 이 흐름에서 "배포"와 "배포검토"까지는 lane 이고, 배포검토 이후가 운영 phase 다.

### 각 단계의 성격

| 단계 | 성격 | 담당 | SSOT |
|---|---|---|---|
| 배포 (deploy) | Story-scoped — 배포 실행 (blue-green swap / atomic rollout) | DeployPLAgent + DeployWorkerAgent (ADR-087) | ADR-087 |
| 배포검토 (deploy-review) | Story-scoped, 한 번 끝나는 — production smoke / 성능 비교 / cutover 사후 검증 | DeployReviewPLAgent + DeployReviewWorkerAgent (ADR-088) | ADR-088 §결정 3 |
| **운영 phase** | **ongoing, 시간축에서 계속 도는** — 배포 때 약속한 성능·안정성이 실제 지켜지는지 지속 감시 | **mechanism layer** (monitor / alert / 자동 Issue) | **ADR-104** |

## §2. "한 번 끝나는" vs "계속 도는" — 경계

### 경계 기준

**"한 번 끝나는" = 배포검토**. 배포검토 lane 은 배포 완료 직후 1회 수행되는 검증이다:
- production smoke 테스트
- 배포 전후 성능 비교 (latency / throughput 점검)
- cutover 사후 검증 (ADR-088 §결정 3, L109 "한 번 끝나는")

배포검토 lane 이 PASS 를 반환하면 해당 lane 은 종료된다. 그 이후에 어떤 일이 일어나는지는 배포검토 lane 이 관할하지 않는다.

**"계속 도는" = 운영 phase**. 배포검토가 끝난 이후 시간이 흐르면서:
- 초기에는 보이지 않던 에러가 점진적으로 드러날 수 있다 (배포 직후보다 1시간, 1일 후 에러율이 높아질 수 있다)
- 트래픽 패턴이 변하면 latency burn rate 가 달라진다
- 다음 배포와의 regression 이 나중에야 발견될 수 있다
- 운영 환경에서 smoke / health check 는 지속적으로 필요하다

이 "계속 도는" 부분을 배포검토 lane 에 포함시킬 수 없다 — lane 은 종료 게이트가 있는 구조이기 때문에 (§3 참조).

### 두 영역은 disjoint

배포검토 와 운영 phase 는 disjoint 하다 (CLAUDE.md L84 forward-reference "한 번 끝나는 — 운영 phase 와 disjoint" 의 referent, ADR-104 §결정 1). 경계:

- 배포검토: 배포 완료 시점 → 배포검토 PASS/FAIL 반환 시점 (일회성)
- 운영 phase: 배포검토 PASS 이후 → (계속, 명시적 종료 없음)

## §3. lane 아님 — mechanism layer

### 근본 mismatch

codeforge 의 lane 은 **Story-scoped** 구조다:
- Story 가 들어가 (요구사항 → 설계 → ... → 보안테스트)
- 각 lane 의 PL 이 PASS/FAIL 을 반환하고
- Story 가 Phase 1 PR + Phase 2 PR 로 완료된다

이 구조에는 **종료 게이트** (phase-gate-mergeable, lane Evidence PASS) 가 있고, lane 은 종료 후 다음 lane 으로 넘어간다.

운영 phase 의 "계속 도는" 성격은 이 구조에 들어맞지 않는다:
- 어떤 Story 가 들어가야 하는가? (없다 — 운영 phase 는 특정 Story 에 귀속되지 않는다)
- 어떤 PL 이 PASS 를 반환하는가? (없다 — ongoing 이므로 종료가 없다)
- Phase 1 / Phase 2 PR 구조가 적용되는가? (적용되지 않는다)

만약 운영 phase 를 9번째 lane 으로 신설하면 ADR-023 lane count invariant (6→8 = scope 확장만 허용) 와 충돌하고, lane 의 종료-게이트 의미가 무너진다 (ADR-104 §결정 2 근거).

### mechanism layer 로의 실현

따라서 운영 phase 는 **mechanism layer** 로 실현된다:

| mechanism | 역할 | 시간 성격 |
|---|---|---|
| cron workflow | 주기적 신호 회수 (에러율 / health check 주기 실행) | 계속 도는 |
| filesystem signal | cron 결과 로컬 기록 (0 API call constraint 정합) | 계속 도는 |
| 자동 Issue 생성 | 임계 초과 시 GitHub Issue 자동 생성 → codeforge Story 후보 | event-driven |

정합 invariant (ADR-104 §결정 2):
- **lane count 변경 0** — 운영 phase 는 lane plugin 신설을 수반하지 않는다
- **`phase:운영` label 신설 불요** — `phase:*` label 은 Story-scoped lane 전용. 운영 신호 Issue 는 일반 Story/Epic 후보 label 체계
- **mechanism 실 구현 = 후속 Story carrier** — 실 구현 (workflow yml / script) 는 S4~S7 영역. 본 ADR-104 / 본 파일 은 "mechanism layer" 원칙만 declare

### "운영 phase 의 Story 단위"란 무엇인가

운영 phase 자체는 Story-scoped 가 아니지만, **"운영 phase mechanism 을 신설하는 작업"** 은 Story 다. 예:
- "에러율 임계 초과 시 자동 Issue 생성 workflow 구현" = S4 Story (Story-scoped)
- "latency burn rate cron 추가" = S5 Story (Story-scoped)

이 Story 들은 기존 8 lane 을 그대로 거친다 (요구사항 → ... → 보안테스트). 그 Story 가 배포되면 이후부터 **mechanism 이 ongoing 으로 돈다** (Story 는 끝나지만 mechanism 은 계속 돈다). 이것이 ongoing(시간축) ↔ Story flow(delta + 종료 게이트) mismatch 의 해소 방식이다.

## §4. 운영 phase scope

### 포함 (운영 phase 가 관할하는 것)

- 배포 이후 시간축 ongoing 신호 회수
- 에러율 / latency burn rate / regression / smoke·health 측정 (상세: `measurement-channel.md`)
- 신호 초과 시 자동 Issue 생성 → self-improving loop 입력 (상세: `self-improving-loop.md`)
- 자동 rollback 신호 회수 (S2 에서 정량 임계 정의 예정 — ADR-104 §결정 5 원칙 선언)

### 제외 (운영 phase 가 관할하지 않는 것)

| 제외 영역 | 이유 | 담당 |
|---|---|---|
| 배포 실행 절차 (blue-green swap / atomic rollout) | 배포 lane 영역 | ADR-087 / DeployPLAgent |
| 배포 직후 1회 smoke / 성능비교 / cutover 사후검증 | 배포검토 lane 영역 ("한 번 끝나는") | ADR-088 / DeployReviewPLAgent |
| 운영 실행 절차 결정 (OpsExecutionArchitect) | decision axis (별 Epic CFP-1079 예정) | CFP-1079 disjoint |
| 운영 phase mechanism 실 구현 (workflow yml / script) | S4~S7 Story carrier 영역 | S4~S7 |
| loop closure gate 실 구현 (dedup / max-depth / 사용자 gate) | S6 carrier | S6 |
| wrapper(codeforge 자체) 실측 | production 환경 부재 (wrapper-N/A invariant, `measurement-channel.md §3`) | N/A — declarative SSOT only |
| 정량 신호 임계 구체값 | S2 자동 rollback 정의 영역 (ADR-104 §결정 5 원칙 선언, 실 수치 0) | S2 |
