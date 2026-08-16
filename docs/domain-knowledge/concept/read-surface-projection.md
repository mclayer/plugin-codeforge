---
kind: concept_definition
type: domain-knowledge
slug: read-surface-projection
title: Read-surface projection (기록면 완전성 ↔ 진입당 읽기면 축소의 분리)
status: Active
updated: 2026-08-15
carrier_story: CFP-2986
related_adrs:
  - ADR-161  # concept 파일 누적 소유 경로
  - ADR-039  # Orchestrator subagent default — read/compute offload
  - ADR-044  # lane-PL synthesizer context boundary
tags:
  - codeforge
  - context-management
  - audit-record
  - event-sourcing
  - progressive-disclosure
sources:
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://www.trychroma.com/research/context-rot
  - https://arxiv.org/abs/2307.03172
  - https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs
  - https://github.com/MicrosoftDocs/architecture-center/blob/main/docs/patterns/event-sourcing.md
  - https://www.eventsourcing.dev/first-principles/snapshots
  - https://arxiv.org/abs/2607.17598
  - https://docs.sonarsource.com/sonarcloud/improving/clean-as-you-code/
---

## 정의

append-only 감사 기록의 **기록면**(record surface — 무엇이 보존되는가)과 소비자가 1회 진입 시 실제로 컨텍스트에 적재하는 **읽기면**(read surface — 무엇이 읽히는가)을 서로 다른 변수로 분리하고, 크기 억제 압력을 **읽기면에만** 가하는 패턴. "지우지 않고 줄인다" 의 정확한 메커니즘 이름이며, 저장 비용이 아니라 **소비자의 attention budget** 을 절약 대상으로 삼는다.

기록면은 단조 증가해도 무방하다. 유계여야 하는 것은 `진입 횟수 × 진입당 읽기면` 이지 파일 크기가 아니다.

## 컨텍스트

LLM 소비자는 컨텍스트를 균일하게 쓰지 않는다. 관련 정보가 입력 중간에 있으면 앞뒤에 있을 때보다 성능이 유의하게 떨어지고(Liu et al. 2023, arXiv:2307.03172), 컨텍스트 창이 차기 훨씬 전부터 단순 검색·복제 과제에서도 정확도가 무너진다(Chroma, 2025-07). Anthropic 은 이를 "attention budget" 으로 명명하고 "desired outcome 가능성을 최대화하는 **최소한의 high-signal 토큰 집합**" 을 원칙으로 제시한다.

따라서 append-only 감사 기록을 소비자가 매번 통째로 읽는 구조에서는, 기록의 완전성(감사 요건)과 소비자의 판정 품질(정확도 요건)이 **직접 충돌**한다. read-surface projection 은 이 충돌을 두 면으로 쪼개 해소한다 — CQRS 가 write model 과 read model 을 쪼개고, event sourcing 이 스냅샷으로 replay 범위를 줄이되 스트림을 source of truth 로 남기는 것과 동형.

## 핵심 규칙

- **유계 대상은 읽기면**: 규약·게이트가 상한을 거는 변수 = 진입당 적재량. 기록면 총량에 상한을 걸면 정보 손실 금지 제약과 정면 충돌한다.
- **파생물 비정본 + 재생성 가능**: 인덱스·요약·스냅샷은 정본이 아니며 기록면에서 언제든 재생성 가능해야 한다. Microsoft 아키텍처 가이드가 "스냅샷은 최적화이지 이벤트 스트림의 대체가 아니다" 로 명시하는 규율과 동일. 파생물이 정본이 되는 순간 이 패턴은 손실 압축으로 전락한다.
- **인덱싱 깊이 상한 = 1 (flat only)**: 요약→요약 2단 계층은 실증적으로 이득 0이며 때로 정확도를 붕괴시킨다(He et al. 2026-07, ∞Bench: 2단 라우팅에서 En.MC 0.9126→0.6398). 1단 평면 인덱스만 채택.
- **LLM 생성 요약은 손실적**: 재귀 요약 파이프라인은 오류 증폭·환각에 취약하고, 문헌의 완화책은 "reader 에게 요약 대신 원문 passage 를 준다" 이다. 따라서 파생 요약은 **탐색 보조**로만 쓰고 판정 근거로 쓰지 않는다.
- **손실적 compaction 과의 구별**: Kafka log compaction 은 이름이 compaction 이지만 key 별 최신값만 남기고 이전 값을 폐기하는 **손실적** 기법이다. 정보 손실 금지 제약 아래에서는 채택 불가 — 이름 유사성으로 인한 오채택을 경계.

## 경계

- **In scope**: append-only 감사 기록의 기록면/읽기면 분리, 파생 뷰의 정본성 규율, 인덱싱 깊이 상한, 크기 규약의 적용 변수 선택.
- **Out of scope**:
  - 어느 섹션을 어떻게 쪼갤지의 **구체 설계 결정** — 설계 lane 소관. 본 concept 은 결정이 아니라 결정이 만족해야 할 개념 제약만 서술.
  - 실패·재시도 횟수 자체의 감축(진입 횟수 축) — disjoint axis.
  - 저장 비용·디스크 사용량 — 본 패턴의 절감 대상이 아님.
- **Anti-pattern**:
  - 기록면에 KB 상한 부과 → 정보 미기록 유인(Goodhart). 규칙이 타겟이 되면 측정치는 좋아지고 기록은 나빠진다.
  - 우회 경로 미설계 → 비공식 우회 발생. Amazon 6-pager 조차 appendix 를 **페이지 제한 없음**으로 공식 예외 처리한다.
  - 요약을 정본화 → 손실 압축(제약 위반).
  - 2단 이상 계층 인덱스 → 실증적 정확도 붕괴.

## 관련 ADR

- **ADR-161** — concept 파일 누적 경로 소유(본 파일의 carrier).
- **ADR-039 / ADR-044** — raw 를 장수명 holder 컨텍스트에 진입시키지 않는 offload 규율. 본 concept 은 그 축의 **문서면 대응물**(에이전트 위임이 아니라 문서 구조로 같은 비대칭을 얻는다).

## 변경 이력

- 2026-08-15 KST — 초기 작성(CFP-2986 요구사항 lane, ResearcherAgent). 개념 정립 단계 산출 — 설계 결정 미포함.
