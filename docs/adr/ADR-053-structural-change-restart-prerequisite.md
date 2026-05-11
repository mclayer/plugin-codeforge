---
adr_number: 53
title: 구조적 변경 재구동 선행 의무 및 codeforge 변경 시 consumer 배포 포함
date: 2026-05-10
status: Accepted
category: orchestrator-policy
carrier_story: CFP-357
parent_epic: null
supersedes: null
amends: null
amendments: []
related_stories:
  - CFP-357
related_adrs:
  - ADR-016
  - ADR-039
related_files:
  - docs/orchestrator-playbook.md
  - CLAUDE.md
is_transitional: false
---

# ADR-053: 구조적 변경 재구동 선행 의무 및 codeforge 변경 시 consumer 배포 포함

## 상태

**Accepted (2026-05-10)** — CFP-357 carrier story.

## 컨텍스트

Orchestrator가 구조적 변경(CLAUDE.md 의미 변경, plugin 버전 업, settings 구조 변경, agent definition 변경 등)을 적용한 직후 재구동(세션 재시작) 없이 다음 작업을 수행하는 경우, 변경 전 환경에서 이후 작업이 실행되어 일관성이 깨진다는 문제가 관찰됨.

구체적으로:
- 새 skill 파일이 세션에 로드되지 않은 채로 작업이 진행됨
- 업데이트된 CLAUDE.md 정책이 현재 세션에 반영되지 않은 채로 레인 spawn이 발생함
- 변경된 agent definition이 적용되지 않은 상태에서 subagent가 구버전 역할로 동작함

또한 codeforge plugin 자체 변경의 경우, consumer 프로젝트에 배포되지 않은 상태에서 다음 Story 작업이 진행되면 consumer는 구버전 plugin 환경에서 실행됨. 이는 ADR-016 marketplace 동기화 의무와 연계되어 있으나, "언제 다음 작업을 진행해도 되는가"에 대한 명시적 blocking 규칙이 없었음.

## 결정

### D1. 구조적 변경 재구동 선행 의무

구조적 변경이 발생한 경우, 세션 재구동(재시작)을 완료한 후에만 다음 작업을 수행한다. 재구동 미완료 상태에서 다음 Story 작업 진입 = `policy_violation`.

**구조적 변경 유형 (다음 중 하나 이상 해당 시):**
- CLAUDE.md 의미 변경 (단순 typo 수정 제외)
- plugin 버전 업 (codeforge family 포함)
- settings.json 구조 변경 (hooks 추가/변경 포함)
- agent definition 변경 (신규 추가, 역할 재정의, 삭제)
- skill 파일 의미 변경

**판단 기준:**
- 변경이 현재 세션의 동작·정책·역할에 영향을 주는가 → 구조적 변경으로 분류
- 판단이 모호한 경우 재구동 쪽으로 분류 (안전 방향 원칙)

### D2. codeforge 변경 시 consumer 배포 포함

해당 구조적 변경이 codeforge plugin 자체의 변경인 경우, 재구동 범위에 consumer 배포 완료가 포함된다. consumer 배포 완료 전에는 consumer Story 작업 진입이 차단된다.

**consumer 배포 완료 기준 (모두 충족):**
1. marketplace sync PR open·merge 완료 (ADR-016 mirrored 필드 대상: `name`·`version`·`description`·`author`)
2. consumer 측 `/plugins install codeforge@mclayer` 실행 확인
3. `bash scripts/check-codeforge-version-drift.sh` PASS 확인

**거절된 대안:**
- (A) 비동기 배포 — 구버전 consumer에서 Story 시작 허용: ADR-016 의도(단일 진입점 integrity) 위반
- (B) 배포 완료 없이 다음 Story 진입 후 drift 경고만 표시: drift 발생 시 실질적 피해(오동작) 예방 불가

## 결과

- Orchestrator는 구조적 변경 직후 즉시 다음 작업을 시작할 수 없음 → 재구동 또는 배포 완료를 먼저 확인
- 재구동 필요 여부 판단이 모호한 경우 재구동 쪽으로 분류 (안전 방향)
- codeforge 변경 후 consumer 배포 전에는 consumer Story 작업 진입 차단
- playbook §1.1 체크리스트 + CLAUDE.md 세션 개시 의무 섹션에 반영

**문서 변경:**
- `docs/orchestrator-playbook.md` §1.1 체크리스트 항목 추가 — 구조적 변경 감지 시 재구동 blocking 조건
- `CLAUDE.md` "세션 개시 의무" 섹션 blocking 조건 추가 — codeforge 변경 후 consumer 배포 완료 확인

## 해소 기준

N/A — permanent policy



- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) — §1.1 체크리스트 구조적 변경 재구동 blocking 항목 추가
- [`CLAUDE.md`](../../CLAUDE.md) — 세션 개시 의무 섹션 blocking 조건 추가
