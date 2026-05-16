---
adr_number: 004
title: 설계 lane 재구조화 — ArchitectPLAgent + SecurityArchitectAgent 도입
status: Accepted
category: Team & Process
date: 2026-04-27
related_files:
  - agents/ArchitectPLAgent.md
  - agents/ArchitectAgent.md
  - agents/SecurityArchitectAgent.md
  - agents/CodebaseMapperAgent.md
  - agents/RefactorAgent.md
  - templates/change-plan.md
  - CLAUDE.md
is_transitional: false
---

## 상태
Accepted (2026-04-27)

## 컨텍스트

CodeForge v0.10.0까지 설계 lane은 ArchitectAgent가 PL+chief designer 양 역할을 겸직하고, CodebaseMapperAgent(보수/변호자)와 RefactorAgent(혁신/옹호자)의 대립을 조정해 Change Plan을 작성했다.

사용자가 보안 테스트 lane을 직접 경험하면서 두 가지 비대칭을 발견했다:

1. **보안 설계 공백**: trust boundary·auth model·threat model 등 보안 결정은 ArchitectAgent가 implicit하게 책임지지만, Mapper·Refactor 어느 SubAgent도 보안 관점을 표현하지 않음. 결과 trust boundary·auth 오설계는 보안 테스트 lane에서 처음 발견되어 가장 비싼 FIX 회귀 발생
2. **PL 부재 비대칭**: 다른 lane은 모두 PL agent가 있는데 (RequirementsPL, DesignReviewPL, DeveloperPL, CodeReviewPL, TestAgent, SecurityTestPL) 설계 lane만 ArchitectAgent가 PL 역할 겸직

추가로 Codex CLI(GPT-5)를 통한 독립 감사에서 ArchitectAgent의 책임 공백 7건이 식별되었으며, Top-3 중 #3 "FIX 루프 무견제성" — Architect가 author이면서 동시에 FIX 최종 판정자라 conflict of interest 구조가 있음.

## 결정

설계 lane을 다음 4-deputy 구조로 재편한다:

```
ArchitectPLAgent (신설)                                  # PL: supervisor + judge
 ├── ArchitectAgent (강등, 본업 보존)                    # Chief Author: Change Plan §1-§10 + ADR draft
 ├── CodebaseMapperAgent (기존)                          # 보수 — as-is 변호자
 ├── RefactorAgent (기존)                                # 혁신 — 결합도/구조 옹호자
 └── SecurityArchitectAgent (신설)                       # 위협 — trust boundary/auth/data 변호자
```

### 책임 분담 (Architect-heavy authoring)

- **ArchitectPLAgent**: SubAgent 4인 supervisor + draft 검수 + FIX 루프 최종 판정자. 글을 직접 쓰지 않음
- **ArchitectAgent (SubAgent)**: Chief author. Change Plan §1-§10 전체 + 신규 ADR draft + §8 Test Contract author. Mapper/Refactor/SecurityArch 산출물을 입력으로 통합
- **SecurityArchitectAgent**: 위협 모델·trust boundary·auth·data 설계 변호자. Change Plan §7 보안 설계 author 입력 제공

### 부수 결정

1. **Change Plan template §7 보안 설계 신설** (현 §7은 빈 placeholder, 자연스러운 슬롯)
2. **신규 ADR draft 작성 책임을 ArchitectAgent에 명문화** (Codex #7 — 회색지대 해소)
3. **FIX 루프 1차 진단 → ArchitectPL 판정** (DeveloperPL 1차, ArchitectPL 최종) — Codex #3 무견제성 해소
4. **책임 매트릭스에 Design lane 신규 컬럼 추가** — trust boundary 등 보안 카테고리는 시점 분리: 설계(SecurityArch) vs 구현 검증(SecurityTest)

## 결과

### 긍정적
- shift-left 보안: trust boundary·auth 결정이 설계 단계에서 1급 시민으로 가시화 → 보안 테스트 lane FIX 회귀 비용 감소
- PL 라인업 대칭성 회복 — 7-lane + 2-cross-cutting 모두 PL agent 보유
- FIX 판정 conflict of interest 해소 (author ≠ judge)
- 4-deputy 3-way 대립 (보수/혁신/공격자) → 더 균형 잡힌 설계
- ADR draft 책임 명문화 → 회색지대 제거

### 부정적
- 설계 lane 토큰 비용 증가: 기존 (Architect + Mapper + Refactor) 3-agent → 신규 (ArchitectPL + Architect + Mapper + Refactor + SecurityArch) 5-agent. 1 Story당 10-20k 토큰 추가 추정
- ArchitectPLAgent의 검수 부담 — SubAgent 4인 산출물 통합·교차 체크 책임
- Change Plan template 변경 → consumer가 신규 Story부터 §7 채워야 함 (단 N/A 권한으로 docs-only Story는 1줄 처리)

### 후속 조치 (별도 CFP)

Codex 감사 #1·#2·#4-#6 (TestContractArch / DataMigrationArch / 관측성·API호환·SLO checklist)는 본 ADR 범위 외 — 후속 CFP-18+ 분리.

- **#1 = CFP-18 + ADR-006으로 해소**: TestContractArchitectAgent (5번째 SubAgent, §8 Test Contract author input) 신설. 상세는 [ADR-006](ADR-006-testcontract-architect.md) 및 [CFP-18](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/stories/CFP-18.md) 참조.

## 해소 기준

N/A — permanent policy



설계 lane 재편 (CLAUDE.md 다이어그램 SSOT 참조):

```
[설계 lane — Before v0.11.0]
ArchitectAgent (PL + Chief Designer)
 ├── CodebaseMapperAgent
 └── RefactorAgent

[설계 lane — After v0.11.0]
ArchitectPLAgent (PL: supervisor + FIX judge)
 ├── ArchitectAgent (Chief Author)
 ├── CodebaseMapperAgent
 ├── RefactorAgent
 └── SecurityArchitectAgent
```

## 관련 파일

- `agents/ArchitectPLAgent.md` (신설)
- `agents/SecurityArchitectAgent.md` (신설)
- `agents/ArchitectAgent.md` (refocus)
- `agents/CodebaseMapperAgent.md`, `agents/RefactorAgent.md` (상위 갱신)
- `agents/DesignReviewPLAgent.md`, `agents/DeveloperPLAgent.md` (escalation 경로 갱신)
- `templates/change-plan.md` (§7 신설)
- `templates/review-checklists/design.md` (§7 차단 항목)
- `CLAUDE.md` (다이어그램·매트릭스·FIX decision table·스폰 시퀀스)
- `docs/orchestrator-playbook.md` (스폰 prompt·FIX state machine)
