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

## Amendment 2 (CFP-371, 2026-05-10) — Epic-level 통합테스트 재정의

### 배경

ADR-055 §결정 1·3의 per-Story 통합테스트 구조는 두 가지 구조적 문제를 야기했다:

1. **중복 실행 비효율**: 동일 Epic의 Story마다 통합 테스트를 실행하면 Story Suite가 누적될수록 실행 시간이 증가. Story 4개 Epic이면 4회 전체 suite 실행.
2. **원인-결과 분리 불가**: Story별 실행 시 어느 Story의 변경이 기존 서비스를 깨뜨렸는지 파악하기 위해 수동 bisect 필요. Epic 완료 후 1회 실행하면 이 정보가 구조적으로 확보된다.

MCT 이력(MCT-107~111 silent rot, MCT-119 .env missing, MCT-121 runtime error)은 "테스트 통과 = 서비스 동작"이 아님을 반복 확인했다. 통합 테스트 게이트의 위치와 실행 단위 재정의가 근본 해결책이다.

### §결정 1 재정의 (v2): Epic-level 통합테스트 위치

**변경 전 (v1 — per-Story):**
```
Story N: ... → 구현리뷰 → CI gate → 통합테스트
```

**변경 후 (v2 — Epic-level):**
```
Epic 하위 Story 1: ... → 구현리뷰 → CI gate → PASS
Epic 하위 Story 2: ... → 구현리뷰 → CI gate → PASS
Epic 하위 Story N: ... → 구현리뷰 → CI gate → PASS
                                  ↓ 전체 PASS 확인
                  [Epic 통합테스트] — 1회 실행
                  Baseline Suite + Story Suite
                                  ↓
                  PASS → Epic 완료 / FAIL → 원인 Story FIX loop
```

**트리거 조건**: Epic 하위 `stories_in_scope` 전원 CI gate PASS 완료 시 Orchestrator가 IntegrationTestAgent 1회 spawn.
단일 Story Epic(non-Epic Story)은 해당 Story CI gate PASS 직후 동일 규칙 적용 (Epic-key = Story-key).

### §결정 3 재정의 (v2): IntegrationTestAgent mandate 확장

> *(기존 mandate 1~4 유지 — ADR-055 §결정 3 원문 참조. 아래 항목을 추가한다.)*

기존 mandate 1~4에 아래 항목 추가:

5. **Baseline Suite 실행**: `tests/integration/baseline/` 를 docker-compose.test.yml 환경에서 실행. consumer overlay `integration_test.baseline_suite_path` 로 경로 override 가능.

6. **Deployability 검증**: 서비스 스택 기동 전 4단계 순차 검증:
   - `.env` 필수 키 존재 여부 (consumer overlay `integration_test.required_env_keys` 기반)
   - container 기동 성공 (`docker-compose up --wait`)
   - DB 연결 가능 (health check endpoint 또는 connection test)
   - 서비스 health check endpoint 200 응답

7. **Story Suite 자동생성**: 이번 Epic의 각 Story §8.6 Integration Test Contract 를 읽어 `tests/integration/stories/<EPIC-KEY>/<STORY-KEY>/` 하위에 테스트 파일 자동생성. 각 테스트 함수에 `story_key = "CFP-XXX"` metadata 태깅 의무.

8. **Baseline 자동승격**: Epic 통합테스트 PASS 후 Orchestrator가 Story Suite를 Baseline Suite에 merge. `tests/integration/baseline/` 에 Story Suite 테스트 추가 commit.

9. **story_key blame**: Baseline 실패 시 `git log --follow` 로 컴포넌트 변경 Story 특정 → `responsible_stories` 집계.

> **§결정 7 예약**: ADR-055 범위 확장 검토 중 본 Amendment에서 할당되지 않음 — 후속 CFP 사용 예정.

### §결정 8 신설: Epic State Ledger (세션 연속성 보장)

Orchestrator는 Epic 진행 중 아래 위치에 상태 파일을 유지한다:

**파일 경로**: `.claude-work/epic-state/<EPIC-KEY>.yaml`

**스키마:**
```yaml
epic_key: string
epic_title: string
created_at: ISO8601
last_updated_at: ISO8601

stories:
  - story_key: string
    title: string
    status: "pending" | "requirements" | "design" | "design_review"
            | "implementation" | "code_review" | "ci_gate" | "ci_pass" | "fix_loop"
    current_lane: string
    pr_number: int | null
    fix_count: int

integration_test:
  status: "not_started" | "running" | "pass" | "fail" | "fix_loop"
  executed_at: ISO8601 | null
  verdict_ref: string | null        # test-verdict-v2.1 패킷 저장 경로

session_resume_hint: string | null  # 재시작 시 Orchestrator가 읽을 다음 액션 힌트
```

**Orchestrator 의무:**
- Epic 시작 시 파일 생성
- 각 Story lane 전환 시 해당 Story `status` 업데이트
- Epic 통합테스트 결과 반영 후 `integration_test` 섹션 업데이트
- 세션 시작 시 `.claude-work/epic-state/` 스캔 → `integration_test.status != "pass"` 또는 `stories[*].status != "ci_pass"` 인 파일 존재 시 사용자에게 resume 여부 확인

### §결정 9 신설: FIX 3-way 분기 — environment 브랜치 추가 (failure_type 4종, 카테고리 3종)

기존 FIX 루프는 `구현 원인` vs `설계 원인` 2-way였다. 통합테스트 FAIL에는 세 번째 원인이 존재한다:

| failure_type | 1차 가정 | FIX 담당 | ArchitectPL 판정 필요 |
|---|---|---|---|
| `regression` | 구현 원인 | DeveloperPL | Yes (설계 원인 가능) |
| `new_test` | 구현 원인 | DeveloperPL | Yes |
| `infra_setup` | 인프라 원인 | InfraEngineerAgent | No |
| `env_missing` | 환경 설정 누락 | InfraEngineerAgent or 사용자 | No |

`infra_setup` / `env_missing` 은 환경 카테고리로 같이 묶임. 설계·구현 변경 없이 인프라·환경 수정만으로 해결. ArchitectPL 판정 불필요. **FIX max: 3회** (전체 failure_type 공통).

### Amendment 2 미결 사항 (후속 CFP)

- **codeforge-design plugin**: TestContractArchitectAgent §8.6 Integration Test Contract 포맷에 `story_key` 태깅 요건 추가 — 별도 CFP
- **codeforge-test plugin**: IntegrationTestAgent mandate Epic-level 재작성 (Baseline Suite 관리, Story Suite 자동생성, deployability 검증, story_key blame, test-verdict-v2.1 반환) — 별도 CFP

## 관련 파일

- [ADR-048](ADR-048-ci-native-test-execution.md) — Amendment 1: §결정 4·5 변경
- [ADR-042](ADR-042-agent-model-selection-policy.md) — Amendment 3: IntegrationTestAgent Sonnet
- [test-verdict-v2](../inter-plugin-contracts/test-verdict-v2.md) — integration lane contract
- [test-verdict-v2.1](../inter-plugin-contracts/test-verdict-v2.md) — v2 → v2.1 Epic-level 필드 (CFP-371 / Amendment 2)
