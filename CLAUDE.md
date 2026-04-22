# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`mctrader` — 암호화폐 스캘핑 자동매매 프레임워크. Python 기반, 완전 자율 실행.

## Configuration

`settings.json`에 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 활성화됨.

## Development Agent Team

```
User
 └── PMAgent                              # 요건 해석, 작업 범위 조율, 팀 합의 관리
      ├── DocsAgent                        # ADR, README 등 작업 전반의 문서화 담당
      ├── DomainPLAgent                    # 암호화폐 트레이딩 도메인 해석 및 스펙 변환
      └── ArchitectAgent                   # 설계/패턴 결정, 기술 최종 의사결정
           ├── RefactorAgent                 # Clean Architecture 리팩토링 (설계 개선 직속 도구)
           ├── DeveloperPLAgent             # 구현 가능성, 레이어 계약, 코드 품질 관리
           │    ├── FrontendDeveloperAgent
           │    └── BackendDeveloperAgent
           ├── QualityPLAgent               # 품질 PL — 3인 의견 종합 + 디버그 루프 결정
           │    ├── QADeveloperAgent         # 테스트 코드 작성 전담
           │    ├── CodexReviewerAgent       # 외부 Codex(GPT-5) 모델 리뷰
           │    └── TesterAgent              # pytest 실행 전담
           └── EngineerPLAgent              # 인프라 솔루션 검토 (Linux → Kubernetes)
                ├── DataEngineerAgent        # 데이터 파이프라인 설계 및 구현
                └── ServerEngineerAgent      # Linux 서버 및 서버 엔지니어링 수행
```

**에이전트별 상세 원칙·역할·보고 포맷은 각 `.claude/agents/<AgentName>.md` 파일을 참조한다.** CLAUDE.md에는 복제하지 않는다.

## 오케스트레이션 규칙

### 플랫폼 제약
**하위 에이전트는 Agent 툴을 사용할 수 없다 — 재귀 스폰 불가.** 모든 스폰은 최상위 Claude(오케스트레이터)가 직접 수행한다. 서브에이전트 간 직접 통신 불가 — 보고는 항상 오케스트레이터가 수령하고 다음 에이전트에 투입한다.

### PMAgent 선행 의무 (관문)
오케스트레이터는 구현 에이전트(FrontendDeveloperAgent/BackendDeveloperAgent/RefactorAgent 등)를 스폰하기 전에 **반드시 PMAgent를 먼저 스폰**한다. PMAgent 출력:
1. 태스크 유형 분류
2. 필요 에이전트 목록 및 스폰 순서
3. 생략 가능 에이전트와 그 이유

"작은 수정이라 생략" 판단은 오케스트레이터 권한 밖이다.

### 스폰 시퀀스 (표준)
```
PMAgent → DomainPLAgent → ArchitectAgent
       → [RefactorAgent]  ← ArchitectAgent가 설계 개선 필요 판단 시 선제 호출
       → DeveloperPLAgent → Frontend/BackendDeveloperAgent
       → [RefactorAgent]  ← 구현 후 패스 (Clean Architecture 강제)
       → [Quality Gate]
       → DocsAgent
```
RefactorAgent는 ArchitectAgent 직속 도구로, 설계 개선 목적의 **선제 리팩토링**과 구현 완료 후 **후행 리팩토링** 양쪽에 호출될 수 있다.

### Quality Gate (4단계)
```
Step 1: 3인 보고 수집 (오케스트레이터가 병렬/순차 스폰)
 ├── QADeveloperAgent      → 테스트 작성 + 커버리지 gap 보고
 ├── CodexReviewerAgent    → Codex 외부 리뷰 (--wait, same-pass 집계)
 └── TesterAgent           → pytest 실행 + PASS/FAIL 구조화 보고

Step 2: 종합 판단
 └── QualityPLAgent        → 3인 보고를 프롬프트에 투입받아 PASS / FIX / ESCALATE 결정
```

### QualityPLAgent FIX 루프 (자동)
`FIX` 판단 시 오케스트레이터가 최대 3회 반복:
```
ArchitectAgent(수정 방향) → Dev(구현) → [선택: Refactor/QADev/Codex 재스폰]
                           → TesterAgent → QualityPLAgent(재종합)
```
- QualityPLAgent가 **단일 판단자** — TesterAgent FAIL만으로 루프 트리거하지 않음
- 매 iteration 이전과 다른 접근을 취함
- 3회 초과 → ESCALATE (사용자에게 보고)
- PASS → DocsAgent 단계로 진행

### 합의 규칙
- 도메인 해석: DomainPLAgent → 오케스트레이터 → ArchitectAgent
- 설계 결정: ArchitectAgent 주도
- 구현 결정: 각 PL 자율
- 품질 판단: QualityPLAgent 단독, FIX 시 ArchitectAgent 에스컬레이션

### Write 권한 없는 에이전트
PMAgent / ArchitectAgent / DeveloperPLAgent / EngineerPLAgent / QualityPLAgent / DomainPLAgent는 Write 권한이 없다. 문서화가 필요하면 **DocsAgent 스폰으로 위임**한다.

## ADR (Architecture Decision Records)

### GitLab Issues가 유일한 진실의 원천 (SSOT)
**모든 ADR은 GitLab Issues에 보관된다. CLAUDE.md에는 목록을 미러링하지 않는다.**
- 프로젝트: `mctrader1/mctrader` (project ID `81469985`)
- 조회: https://gitlab.com/mctrader1/mctrader/-/issues/?label_name[]=ADR
- MCP: `mcp__GitLab__list_issues(project_id="81469985", labels=["ADR"])`
- CLI: `glab issue list --label ADR`

### 규칙
- 세션 시작 시 GitLab의 `label=ADR` 이슈 목록을 먼저 조회, 결정 사항을 번복하지 않는다
- 설계 결정 시마다 신규 ADR 이슈 생성 (번호 = 기존 최대 + 1)
- ADR에 반하는 구현 시 사용자 확인 후 해당 ADR 상태 업데이트 (Deprecated / Superseded by #NNN)

### 생성 기준
라이브러리/프레임워크 선택 · 아키텍처 패턴 결정 · 데이터 저장·처리 방식 · 인프라/배포 방식 · 전략 도메인 핵심 개념.

### 이슈 포맷
```
제목: ADR-NNN: <결정 제목>   레이블: ADR
본문:
## 상태           Accepted | Deprecated | Superseded by #NNN
## 컨텍스트       왜 이 결정이 필요했는가
## 결정           무엇을 어떻게 결정했는가
## 결과           ✅ 장점 / ⚠️ 단점 / TO-DO
## 다이어그램     classDiagram | sequenceDiagram | graph LR/TD
## 관련 파일      코드 경로
```

## Domain Knowledge

- [OrderBook/Trade 시각화 스펙](docs/guides/orderbook-trade-visualization-spec.md)

## Trading Domain

- 대상: 암호화폐 전용
- 전략: 스캘핑 (단기, 고빈도)
- 실행: 완전 자율
- 주요 데이터: 실시간 가격 데이터, 호가창
