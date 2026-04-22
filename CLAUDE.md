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
           ├── QualityPLAgent               # 품질 PL — 4인 의견 종합 + 디버그 루프 결정
           │    ├── QADeveloperAgent         # 테스트 코드 작성 전담 (tests/**만 Write)
           │    ├── ClaudeReviewerAgent      # Claude 네이티브 리뷰 (읽기 전용)
           │    ├── CodexReviewerAgent       # 외부 Codex(GPT-5) 모델 리뷰 (필수, 읽기 전용)
           │    └── TesterAgent              # pytest 실행 전담 (읽기 전용)
           └── EngineerPLAgent              # 인프라 솔루션 검토 (Linux → Kubernetes)
                ├── DataEngineerAgent        # 데이터 파이프라인 설계 및 구현
                └── ServerEngineerAgent      # Linux 서버 및 서버 엔지니어링 수행
```

**에이전트별 상세 원칙·역할·보고 포맷은 각 `.claude/agents/<AgentName>.md` 파일을 참조한다.** CLAUDE.md에는 복제하지 않는다.

### 설계와 구현의 분리 (SI 프로세스)
- **설계 단계**: ArchitectAgent + RefactorAgent가 **현재 코드 분석 + 변경 계획서(Change Plan) 작성**. 파일별 수정 범위·인터페이스·시그니처·이름까지 구현 상세를 확정한다
- **구현 단계**: DeveloperPLAgent 이하(Frontend/BackendDeveloperAgent)는 계획서 그대로 **코드 작성만** 수행. 설계 의사결정 금지, 계획서 결함 발견 시 즉시 ArchitectAgent에 에스컬레이션
- **품질 단계**: QualityPLAgent 계열이 QADev / Claude / Codex / Tester 4인 보고 종합

## 오케스트레이션 규칙

### 플랫폼 제약
**하위 에이전트는 Agent 툴을 사용할 수 없다 — 재귀 스폰 불가.** 모든 스폰은 최상위 Claude(오케스트레이터)가 직접 수행한다. 서브에이전트 간 직접 통신 불가 — 보고는 항상 오케스트레이터가 수령하고 다음 에이전트에 투입한다.

### PMAgent 선행 의무 (관문)
오케스트레이터는 구현 에이전트(FrontendDeveloperAgent/BackendDeveloperAgent/RefactorAgent 등)를 스폰하기 전에 **반드시 PMAgent를 먼저 스폰**한다. PMAgent 출력:
1. 태스크 유형 분류
2. 필요 에이전트 목록 및 스폰 순서
3. 생략 가능 에이전트와 그 이유 (**Quality Gate 5인은 생략 불가 — 아래 참조**)

"작은 수정이라 생략" 판단은 오케스트레이터 권한 밖이다.

#### 절대 생략 불가 에이전트 (Never-skippable)
PMAgent의 "생략 가능" 판단은 **아래 에이전트에 절대 적용할 수 없다**:
- **`QADeveloperAgent`** — 모든 변경에 테스트 계획 실행 필수
- **`ClaudeReviewerAgent`** — Claude 네이티브 리뷰 필수
- **`CodexReviewerAgent`** — Codex 외부 리뷰 필수
- **`TesterAgent`** — pytest 실행 필수
- **`QualityPLAgent`** — 4인 보고 종합 판단 필수

PMAgent는 DomainPL·DocsAgent 등 외곽 에이전트의 조건부 생략만 제안할 수 있다.

### 스폰 시퀀스 (표준 — 통합 게이트 + 구현 분기)

ArchitectAgent가 "EngineerPL 우선" 원칙에 따라 구현 담당을 판단 후 계획서에 명시한다. **Quality Gate는 분기와 무관하게 통합 5인 게이트** (QADev·Claude·Codex·Tester가 코드 + 인프라 모두 검증).

```
─── 설계 단계 (ArchitectAgent 단독, 분기 결정 포함) ───
PMAgent → DomainPLAgent → ArchitectAgent
       ↔ RefactorAgent (공동: 기존 코드·인프라 분석, 변경 계획서 수립)
       → RefactorAgent (선행 리팩토링, 필요 시)

─── 구현 단계 (계획서대로 — 담당 분기는 ArchitectAgent가 결정) ───
  분기 A (인프라/운영): EngineerPLAgent → DataEngineerAgent / ServerEngineerAgent
  분기 B (애플리케이션): DeveloperPLAgent → Frontend/BackendDeveloperAgent
  분기 A+B 병렬: ArchitectAgent가 양측 모두 지시한 경우 Dev와 EngineerPL 계열 병렬 스폰

─── 품질 단계 (통합 5인 게이트, Never-skippable, 분기 A·B·A+B 공통) ───
       → [Quality Gate: QADev + Claude + Codex + Tester → QualityPL]
         · QADev: tests/unit, tests/integration, tests/infra 모두 담당
         · Claude/Codex: 코드 + 인프라 파일(config, service, scripts) 모두 리뷰
         · Tester: pytest tests/** 전체 실행
       → DocsAgent
```

**분기 선택 규칙** (ArchitectAgent.md 참조):
- 1순위 EngineerPL 경로 — 인프라 레벨 해결이 동등 이상 이득이면 분기 A
- 2순위 Developer 경로 — 코드 수정이 더 단순하거나 인프라 오버헤드가 큰 경우 분기 B
- A+B 병렬 — 양측 수정이 동시에 필요하면 ArchitectAgent가 계획서에 명시, 오케스트레이터가 병렬 스폰
- **Change Plan에 분기 선택 근거를 한 줄 기록** 필수

**공통 원칙**:
- RefactorAgent는 ArchitectAgent 직속 공동 작업자. **변경 계획서 작성** + **선행 리팩토링 실행** 단계 참여
- Quality Gate 5인은 분기와 무관하게 생략 불가 (never-skippable)
- 설계는 ArchitectAgent 단독, 구현 단계는 계획서 준수

### Quality Gate (2단계 — 4인 보고 모두 필수)
```
Step 1: 4인 보고 수집 (모두 필수, SKIPPED 불허, 병렬 권장)
 ├── QADeveloperAgent      → tests/**만 작성, src/** 읽기만 + gap 평가 보고
 ├── ClaudeReviewerAgent   → Claude 네이티브 리뷰 + severity (P0~P3) 태그 보고
 ├── CodexReviewerAgent    → Codex 외부 리뷰 (--wait) + severity 정규화된 보고
 └── TesterAgent           → pytest 실행 + PASS/FAIL 구조화 보고

Step 2: 종합 판단
 └── QualityPLAgent        → 4인 보고를 프롬프트에 투입받아 PASS / FIX / ESCALATE 결정
                            (Claude·Codex 리뷰 합집합으로 severity 평가)
```

**Codex 플러그인 필수**: 미설치 시 Quality Gate 진행 불가, 오케스트레이터가 설치 안내 후 중단 보고. QualityPL 산하 4인은 **src/** 쓰기 권한 없음** (QADev만 tests/** 쓰기 가능) — 평가만 수행하고 변경은 Architect+Refactor 계획서 갱신으로만 이루어진다.

### QualityPLAgent FIX 루프 (자동 — 설계 선행 + 분기 인식)
`FIX` 판단 시 오케스트레이터가 최대 3회 반복 (매 iteration 동일 시퀀스):
```
Step 1 (설계): ArchitectAgent ↔ RefactorAgent → 변경 계획서 갱신
               · 새 수정 담당을 명시: Dev 계열 / EngineerPL 계열 / 양측 병렬

Step 2 (구현): 계획서의 담당 분기에 따라 오케스트레이터가 dispatch
   - 분기 A (인프라 결함): EngineerPLAgent → DataEngineer/ServerEngineer
   - 분기 B (앱 코드 결함): DeveloperPL → Backend/Frontend
   - 분기 A+B (양측): 병렬 스폰

Step 3 (품질): QADev + Claude + Codex + Tester 4인 모두 재실행 → QualityPLAgent 재종합
```
- **설계 금지 원칙 유지** — Dev·Engineer는 새 계획서를 받아 구현만. Quality 계열은 평가만. 설계·분기 결정은 오직 Architect+Refactor의 계획서 갱신으로
- **분기 이관 필수** — QualityPL은 원 분기(A/B/A+B)를 계획서에서 참조해 ArchitectAgent에 전달. Architect가 새 분기 결정 가능
- **4인 재실행은 선택 아님** — 매 iteration 모두 돌린다 (이전과 다른 접근 + 누적 컨텍스트 전달, 리뷰어는 병렬)
- QualityPLAgent가 **단일 판단자** — TesterAgent FAIL만으로 루프 트리거하지 않음
- 3회 초과 → ESCALATE (사용자에게 보고)
- PASS → DocsAgent 단계로 진행

### 합의 규칙
- 도메인 해석: DomainPLAgent → 오케스트레이터 → ArchitectAgent
- **설계 결정은 ArchitectAgent 단독** — 계획서의 파일·인터페이스·시그니처·API 계약 모두 확정. PL들은 실행 조율만 수행하며 설계 범위 확장·결함 발견 시 반드시 ArchitectAgent로 되돌린다
- 품질 판단: QualityPLAgent 단독, FIX 시 Architect+Refactor 계획서 갱신으로 에스컬레이션

### Write 권한 구조 (path-scoped 강제)
권한은 **prose 금지**가 아닌 **frontmatter의 path scoping**으로 강제된다:
- **`BackendDeveloperAgent`**: `Edit(src/**)` + `Write(src/**)` / deny `tests/**`, `templates/**`, `static/**`, `docs/**`
- **`FrontendDeveloperAgent`**: `Edit|Write(src/mctrader/dashboard/templates/**)` + `Edit|Write(src/mctrader/dashboard/static/**)` / deny `server.py`, `backtest_runner.py`, `domain/**`, `adapters/**`, `ports/**`, `cli/**`, `tests/**`
- **`QADeveloperAgent`**: `Edit|Write(tests/**)` / deny `Edit|Write(src/**)` (production 읽기만)
- **`RefactorAgent`**: `Edit(src/**)`만 (파일 생성 `Write` 없음) / deny `tests/**`, `docs/**`, `.claude/**`, `config/**`, `deploy/**`, `scripts/**` — 파일 분리·신규 모듈은 BackendDev/FrontendDev 담당
- **PL/평가 레이어** (`PMAgent` / `ArchitectAgent` / `DeveloperPLAgent` / `EngineerPLAgent` / `QualityPLAgent` / `DomainPLAgent`): Write/Edit 전면 없음. 문서화 필요 시 DocsAgent 위임
- **읽기 전용 평가**: `ClaudeReviewerAgent` / `CodexReviewerAgent` / `TesterAgent` — 결함 발견 시 QualityPLAgent에 평가 전달, 변경은 Architect+Refactor 계획서 갱신으로만

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
