---
adr_number: 48
title: CI-native 테스트 실행 — TestAgent 제거 + SecurityTestPL opt-in (CFP-317)
status: Accepted
category: architecture
date: 2026-05-09
carrier_story: CFP-317
related_adrs:
  - ADR-023  # Lane plugin lifecycle
  - ADR-008  # Inter-plugin contract versioning
  - ADR-039  # Orchestrator subagent default
supersedes: null
superseded_by: null
amends: null
amended_by: ADR-055
amended_date: "2026-05-10"
is_transitional: false
---

# ADR-048: CI-native 테스트 실행 — TestAgent 제거 + SecurityTestPL opt-in

## 상태

Accepted — CFP-317 (2026-05-09)

## 컨텍스트

codeforge 7-lane 중 두 lane이 GitHub CI로 대체 가능한 역할을 수행하고 있었음:

1. **구현 테스트 lane**: TestAgent가 consumer overlay `run-tests.sh`를 호출하나, 이 명령은 GitHub CI와 동일. 테스트 코드도 없는 상태에서 실행 에이전트만 있는 구조는 본말이 전도됨.
2. **보안 테스트 lane**: 1차 layer(Dependabot/CodeQL/Secret Scanning)는 이미 GitHub native. 2차 layer AI 분석은 solo/내부 시스템 consumer에게 과도한 overhead.

첫 번째 consumer(mctrader)는 내부 네트워크 전용 시스템이며 GitHub Actions CI 워크플로가 전무한 상태. codeforge가 테스트를 "실행"하기 전에 테스트를 "개발"하는 역할을 강화해야 함.

## 결정

### §결정 1: 구현 테스트 lane 제거 — QADeveloperAgent가 test.yml 작성

TestAgent / StatefulTestAgent spawn 폐지. QADeveloperAgent 의무 확장:
- 기존: 테스트 코드(`tests/`) 작성
- 추가: `.github/workflows/test.yml` 생성 또는 갱신 (consumer `project.yaml` `tests.runner` 기반)
- 추가: performance baseline 파일 생성/갱신

### §결정 2: CI gate — Orchestrator inline polling

구현 리뷰 PASS 후 Orchestrator가 `gh pr checks <PR_NUMBER> --watch` 실행 (최대 30분 timeout). read-only inline whitelist 예외 적용 (ADR-039 §결정 Inline whitelist 정합).

- PASS + `lanes.security_ai: false` (default) → merge gate 진입
- PASS + `lanes.security_ai: true` → SecurityTestPL spawn
- FAIL → `gh run view --log-failed` 로그 수집 → DeveloperPL 1차 진단 → ArchitectPL 최종 판정 → FIX loop

### §결정 3: SecurityTestPL opt-in 격하

SecurityTestPL은 기본 미spawn. `project.yaml` `lanes.security_ai: true` 설정 시에만 활성. agent 파일은 codeforge-review plugin 내 보존 (삭제 안 함). `gate:security-test-pass` 라벨은 `security_ai: true` consumer에서만 필수 게이트.

### §결정 4: codeforge-test plugin deprecated (ADR-023 lifecycle)

`codeforge-test` plugin을 Deprecated 선언. `test_verdict` contract v1을 Archived. consumer overlay `run-tests.sh` / `run-perf.sh` 파일은 더 이상 필요 없음.

### §결정 5: 7-lane → 5-lane + CI gate

공식 lane 아키텍처:
```
요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → [CI gate]
```
보안 테스트 lane은 `security_ai: true` consumer에서만 선택적으로 추가.

## 결과

### 긍정적

- 테스트 코드 개발이 codeforge의 1st-class 책임이 됨 (실행 전 작성 선행)
- consumer가 codeforge 없이도 CI로 테스트 자동 실행 가능
- 7-lane overhead 감소 — 특히 solo/내부 시스템 consumer에서 실질적 단순화
- security AI overhead를 opt-in으로 격하해 소규모 consumer 진입장벽 완화

### 부정적/트레이드오프

- `test_verdict` typed contract 소멸 → FIX routing이 `gh` raw 출력 파싱 의존
- `gh pr checks` polling = 최대 30분 대기 가능 (CI 실행 시간 포함)
- SecurityTestPL 사용 consumer는 `project.yaml` 명시적 opt-in 필요

## 해소 기준

N/A — permanent policy

## 관련 파일

- CLAUDE.md: 7-lane → 5-lane 선언 + 레인 표 수정
- `docs/project-config-schema.md`: `lanes.security_ai` 필드 추가
- `docs/consumer-guide.md`: overlay 파일 제거 + opt-in 섹션 신설
- `docs/orchestrator-playbook.md`: CI gate 절차 추가
- `templates/github-workflows/phase-gate-mergeable.yml`: security_ai 조건부 heuristic
- `docs/inter-plugin-contracts/test-verdict-v1.md`: status Archived
- `plugin-codeforge-test`: Deprecated 선언 (구 lane repo — 현 `plugins/codeforge-test/`, repo 삭제됨 2026-06-12)

---

## Amendment 1 — codeforge-test 통합테스트 전용 부활 (CFP-367 / ADR-055)

**날짜**: 2026-05-10

### 변경 사항

**§결정 4 변경**: ~~codeforge-test plugin deprecated~~ → **codeforge-test plugin 통합테스트 전용 부활**
- StatefulTestAgent: deprecated 유지
- IntegrationTestAgent: 신규 추가 (ADR-055 §결정 3)
- `test_verdict` contract: v1(Archived 유지) + v2(Active, ADR-055 §결정 6)

**§결정 5 변경**: ~~5-lane + CI gate~~ → **6-lane + CI gate**

```
요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → [CI gate] → **통합테스트** → 보안테스트(opt-in)
```

### 원 결정 유지

§결정 1 (QADeveloperAgent test.yml 의무), §결정 2 (CI gate inline polling), §결정 3 (SecurityTestPL opt-in)은 변경 없음.
