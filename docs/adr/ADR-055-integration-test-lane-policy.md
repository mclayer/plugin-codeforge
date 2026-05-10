---
adr_number: 55
title: Integration Test Lane — codeforge-test 통합테스트 전용 부활 (CFP-367)
status: Accepted
category: architecture
date: 2026-05-10
carrier_story: CFP-367
related_adrs:
  - ADR-048  # codeforge-test deprecated (이 ADR로 Amendment)
  - ADR-042  # agent model tier (Amendment 3)
  - ADR-023  # Lane plugin lifecycle
  - ADR-015  # §8.5 Stateful test CONDITIONAL
supersedes: null
superseded_by: null
amends: null
---

# ADR-055: Integration Test Lane — codeforge-test 통합테스트 전용 부활

## 상태

Accepted — CFP-367 (2026-05-10)

## 컨텍스트

ADR-048(CFP-317)이 codeforge-test lane을 deprecated하고 테스트 책임을 QADeveloperAgent + CI gate로 위임한 결과 세 가지 구조적 공백이 발생했다:

1. **설계 레이어**: §8 Test Contract에 통합 테스트 범위 명세 없음 — 컴포넌트 경계·다중 서비스 시나리오 미정의
2. **에이전트 레이어**: QADeveloperAgent(Haiku 4.5 tier)가 단위 테스트만 작성 — `tests/integration/` 없이 PR 제출 가능
3. **리뷰 게이트**: CodeReviewPL이 통합 테스트 부재를 blocking하지 않음

결과: Story "완료" 판정 후에도 컴포넌트 경계·다중 서비스 연동이 실제 검증되지 않은 채로 deliver됨.

핵심 필요: 통합 테스트 파일 추가가 아니라, **파이프라인이 컴포넌트 경계 동작 보증을 deliverable 조건으로 강제**해야 한다.

## 결정

### §결정 1: 파이프라인에 통합테스트 lane 추가

```
요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → [CI gate] → 통합테스트 → 보안테스트(opt-in)
```

CI gate PASS 이후, 보안테스트 이전 위치. ADR-048 §결정 5의 5-lane → **6-lane** (Amendment).

### §결정 2: codeforge-test plugin 통합테스트 전용 부활

ADR-048 §결정 4의 deprecated 결정을 **Amendment**한다:
- `codeforge-test` plugin: Deprecated → **Active (통합테스트 전용)**
- StatefulTestAgent: deprecated 유지 (§8.5 CONDITIONAL, CI 매핑 별도 CFP)
- IntegrationTestAgent 신규 추가 (§결정 3)
- `test_verdict` contract: v1(Archived 유지) + v2(Active, §결정 6)

### §결정 3: IntegrationTestAgent 신설

- **Mandate**: 동적 통합 테스트 전담 에이전트
  1. `§8.6 Integration Test Contract`(TestContractArchitectAgent 산출물) 기반으로 `tests/integration/<story-key>/` 하위 테스트 파일 작성
  2. `tests/integration/` 전체 suite를 docker-compose.test.yml 환경에서 **동적 실행** (내부 컴포넌트 정적 mock 금지)
  3. regression PASS 확인: 기존 전체 기능 재점검
  4. 신규 Story 시나리오를 suite에 추가해 누적 커버리지 확장

- **동적 테스트 원칙**: 시스템 내부 컴포넌트를 정적 mock으로 대체 금지. 외부 의존성(Bithumb API 등 제어 불가 시스템)은 WireMock 허용 (계약 기반 테스트).

- **Spawn 주체**: Orchestrator (CI gate PASS 직후)
- **모델 tier**: Sonnet (ADR-042 Amendment 3) — 컴포넌트 경계 판단·외부 의존성 설계 필요
- **출력물**: `tests/integration/<story-key>/test_*.py`, `test-verdict-v2` contract 패킷, Story §9 integration test 섹션

### §결정 4: §8.6 Integration Test Contract 신설

TestContractArchitectAgent(설계 lane deputy)가 작성. Story가 컴포넌트 경계 2개 이상 포함 시 **필수**:
- 경계 유형, 커버리지 목표(Given/When/Then), 환경 의존성, 실행 격리 전략, 동적 테스트 요건
- 미작성 시 설계리뷰에서 P1 blocking

### §결정 5: InfraEngineerAgent docker-compose.test.yml 의무

구현 lane에서 InfraEngineerAgent의 산출물에 `docker-compose.test.yml` 추가 의무:
- test DB (독립 컨테이너, seed 포함)
- external API WireMock 컨테이너
- 서비스 간 network isolation

§8.6 환경 의존성 미반영 시 DeveloperPL blocking.

### §결정 6: test-verdict-v2 contract

integration lane 전용 결과 패킷. test-verdict-v1 Archived 유지. 스키마: `docs/inter-plugin-contracts/test-verdict-v2.md`.

## 결과

### 긍정적 효과

- 매 Story마다 전체 통합 테스트 suite 실행 → 누적 regression 커버리지
- 컴포넌트 경계·다중 서비스 연동을 deliverable 조건으로 강제
- IntegrationTestAgent(Sonnet)가 경계 판단 수행 → QADev Haiku tier 부담 없음

### 트레이드오프

- pipeline 길이 증가: CI gate 이후 통합 테스트 lane 추가 → Story lead time 증가
- codeforge-test plugin 재활성화 필요 (Phase 2 작업)
- docker-compose.test.yml 유지 비용: InfraEngineerAgent 추가 산출물

### 미결 사항 (후속 CFP)

- §8.5 Stateful test의 CI 매핑 재정의 (본 ADR 범위 외)
- marketplace.json sync PR (ADR-016) — codeforge-test 재활성화 시 mirror 의무
- consumer mctrader 최초 적용 시 `tests/integration/` 초기 suite 범위 정의 필요

## 관련 파일

- [ADR-048](ADR-048-ci-native-test-execution.md) — Amendment 1: §결정 4·5 변경
- [ADR-042](ADR-042-agent-model-selection-policy.md) — Amendment 3: IntegrationTestAgent Sonnet
- [test-verdict-v2](../inter-plugin-contracts/test-verdict-v2.md) — integration lane contract
