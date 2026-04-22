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
      ├── ResearcherAgent                  # 암호화폐 트레이딩 도메인 해석 및 스펙 변환 (구 DomainPLAgent)
      └── ArchitectAgent                   # 설계/패턴 결정, 기술 최종 의사결정, QADev 산출물 감사, FIX 원인 판정
           ├── RefactorAgent                 # 설계 공동작업자 (분석·제안만, 코드 수정은 Dev 경유)
           ├── QADeveloperAgent              # TDD: 구현 단계에서 계획서 기반 tests/** 작성 (품질 단계 관여 없음)
           ├── DeveloperPLAgent              # 구현 가능성, 레이어 계약, 코드 품질 관리
           │    ├── FrontendDeveloperAgent
           │    └── BackendDeveloperAgent
           ├── EngineerPLAgent              # 인프라 솔루션 검토 (Linux → Kubernetes)
           │    ├── DataEngineerAgent        # 데이터 파이프라인 설계 및 구현
           │    └── ServerEngineerAgent      # Linux 서버 및 서버 엔지니어링 수행
           ├── QualityPLAgent               # Step 1 리뷰 게이트 — Claude/Codex severity 종합
           │    ├── ClaudeReviewerAgent      # Claude 네이티브 리뷰 (읽기 전용)
           │    └── CodexReviewerAgent       # 외부 Codex(GPT-5) 모델 리뷰 (필수, 읽기 전용)
           └── TesterAgent                   # Step 2 실행 게이트 — pytest 실행, PASS/FAIL 보고
```

**에이전트별 상세 원칙·역할·보고 포맷은 각 `.claude/agents/<AgentName>.md` 파일을 참조한다.** CLAUDE.md에는 복제하지 않는다.

### 설계와 구현의 분리 (SI 프로세스)
- **설계 단계**: ArchitectAgent + RefactorAgent가 **현재 코드 분석 + 변경 계획서(Change Plan) 작성**. 파일별 수정 범위·인터페이스·시그니처·이름까지 구현 상세를 확정한다. RefactorAgent는 **분석·제안만** 수행하며 실제 코드 수정은 Dev 경유
- **Change Plan 영구 보관**: 확정된 모든 변경 계획서는 **`docs/change-plans/<slug>.md`** 에 저장된다 (DocsAgent 담당, slug는 kebab-case 기능명). 추후 GitLab Wiki 이관 대비 SSOT. **Dev 스폰 전 저장 완료 필수 — 생략 불허**
- **구현 단계**: ArchitectAgent가 QADeveloperAgent(TDD)와 구현 분기(DevPL / EngineerPL / A+B 병렬)를 동시에 스폰. QADev는 `tests/**`만, Dev/Engineer는 `src/**` 및 인프라 자산만 쓰므로 파일 경합 없음. 구현 종료 시점에 ArchitectAgent가 QADev **매핑표(계획서 항목↔테스트 함수)를 감사**하여 품질 단계로 진입할지 결정
- **품질 단계 (순차 게이트)**:
  - Step 1 — QualityPLAgent가 Claude/Codex 리뷰 병렬 수집 후 severity 종합. P0/P1 발견 시 ArchitectAgent 회귀
  - Step 2 — TesterAgent가 pytest 실행. FAIL 시 ArchitectAgent 회귀 (재구현 후 Step 1부터 재실행)

## 오케스트레이션 규칙

### 플랫폼 제약
**하위 에이전트는 Agent 툴을 사용할 수 없다 — 재귀 스폰 불가.** 모든 스폰은 최상위 Claude(오케스트레이터)가 직접 수행한다. 서브에이전트 간 직접 통신 불가 — 보고는 항상 오케스트레이터가 수령하고 다음 에이전트에 투입한다.

### PMAgent 선행 의무 (관문)
오케스트레이터는 구현 에이전트(QADeveloperAgent / FrontendDeveloperAgent / BackendDeveloperAgent / DataEngineerAgent / ServerEngineerAgent 등)를 스폰하기 전에 **반드시 PMAgent를 먼저 스폰**한다. PMAgent 출력:
1. 태스크 유형 분류
2. 필요 에이전트 목록 및 스폰 순서 (구현 단계에 QADev 포함 필수 명시)
3. 생략 가능 에이전트와 그 이유 (**아래 Never-skippable은 절대 불가**)

"작은 수정이라 생략" 판단은 오케스트레이터 권한 밖이다.

#### 절대 생략 불가 에이전트 (Never-skippable — 단계별)
PMAgent의 "생략 가능" 판단은 **아래 에이전트에 절대 적용할 수 없다**:

- **구현 단계 필수**
  - **`QADeveloperAgent`** — TDD 원칙상 모든 변경에 tests/** 작성 필수
- **품질 단계 필수**
  - **`QualityPLAgent`** — Claude/Codex severity 종합 필수 (Step 1 게이트)
  - **`ClaudeReviewerAgent`** — Claude 네이티브 리뷰 필수
  - **`CodexReviewerAgent`** — Codex 외부 리뷰 필수
  - **`TesterAgent`** — pytest 실행 필수 (Step 2 게이트)

PMAgent는 ResearcherAgent·DocsAgent 등 외곽 에이전트의 조건부 생략만 제안할 수 있다.

### 스폰 시퀀스 (표준 — TDD 병렬 구현 + 순차 품질 게이트)

ArchitectAgent가 "EngineerPL 우선" 원칙에 따라 구현 담당 분기를 판단 후 계획서에 명시한다. QADev는 분기와 무관하게 계획서 전체를 대상으로 **한 번만** 스폰되어 Dev/Engineer와 **병렬** 진행된다.

```
─── 설계 단계 (ArchitectAgent 단독, 분기 결정 포함) ───
PMAgent → ResearcherAgent → ArchitectAgent
       ↔ RefactorAgent (공동: 기존 코드·인프라 분석·제안, 변경 계획서 수립)
       → Dev 경유 선행 리팩토링 실행 (Refactor는 edit 권한 없음 — 계획서에 Dev 담당 명시)
       → DocsAgent: Change Plan 저장

─── 구현 단계 (ArchitectAgent가 병렬 스폰 — QADev는 분기 독립 1회) ───
ArchitectAgent
 ├── QADeveloperAgent             # TDD: tests/** 작성 (계획서만 참조)
 └── 구현 분기
      - 분기 A (인프라/운영): EngineerPLAgent → DataEngineerAgent / ServerEngineerAgent
      - 분기 B (애플리케이션):  DeveloperPLAgent → Frontend/BackendDeveloperAgent
      - 분기 A+B 병렬:           양측 모두 필요 시 3라인 동시 스폰 (QADev + DevPL + EngineerPL)

구현 종료 시점:
 └── ArchitectAgent가 QADev 매핑표(계획서 항목↔테스트 함수)를 감사 → 공백 있으면 구현 단계 재개

─── 품질 단계 (순차 게이트, Never-skippable) ───
Step 1 (리뷰 게이트):
  QualityPLAgent
   ├── ClaudeReviewerAgent   (병렬 스폰)
   └── CodexReviewerAgent    (병렬 스폰)
  → severity 종합
     ├── P0/P1 발견 → ArchitectAgent 회귀 (FIX 루프, Step 1 카운터 증가)
     └── P2 이하만 / 이슈 없음 → Step 2 진입

Step 2 (실행 게이트):
  TesterAgent → pytest tests/** 전체 실행
     ├── FAIL → ArchitectAgent 회귀 (FIX 루프, Step 2 카운터 증가)
     │         재구현 후 Step 1부터 재실행 (Step 1 카운터 리셋)
     └── PASS → DocsAgent
```

**분기 선택 규칙** (ArchitectAgent.md 참조):
- 1순위 EngineerPL 경로 — 인프라 레벨 해결이 동등 이상 이득이면 분기 A
- 2순위 Developer 경로 — 코드 수정이 더 단순하거나 인프라 오버헤드가 큰 경우 분기 B
- A+B 병렬 — 양측 수정이 동시에 필요하면 ArchitectAgent가 계획서에 명시, 오케스트레이터가 병렬 스폰
- **Change Plan에 분기 선택 근거를 한 줄 기록** 필수

**공통 원칙**:
- RefactorAgent는 ArchitectAgent 직속 공동 작업자 — **분석·제안만** 수행. 선행 리팩토링도 Dev 경유로 실행
- QADeveloperAgent는 ArchitectAgent 직속. TDD 원칙: 계획서 기반 tests/** 먼저 작성, 품질 단계에는 관여하지 않음
- 설계는 ArchitectAgent 단독, 구현 단계는 계획서 준수
- 품질 게이트는 **순차** — Step 1 (QualityPL) 통과 후에만 Step 2 (Tester) 진입

### FIX 루프 (순차 게이트 + 차별 카운터)

**트리거 조건 (OR):**
1. **Step 1 — QualityPL severity P0/P1** (Claude/Codex 합집합, 객관적 결함만; P2/P3는 통과)
2. **Step 2 — TesterAgent FAIL** (pytest 실패)

**처리 시퀀스 (모든 iteration 공통):**
```
FIX 트리거
  └── [Iteration]
       ── 설계 단계 (필수) ──
       ├── ArchitectAgent ↔ RefactorAgent → 변경 계획서 갱신 + 분기(A/B/A+B) 재결정
       │   - Architect가 실패 원인(코드 결함 vs 테스트 결함) 판정, Dev 재구현 / QADev 재작성 담당 명시
       │   - QADev·Dev가 자체 필요 판단으로 재실행 범위 결정 가능 (Architect 지시 내)
       │
       ── 구현 단계 (계획서 분기 dispatch) ──
       ├── 분기 A (인프라 결함): EngineerPLAgent → DataEngineer/ServerEngineer (+ 필요 시 QADev 재작성)
       ├── 분기 B (앱 코드 결함): DevPL → Backend/Frontend (+ 필요 시 QADev 재작성)
       └── 분기 A+B (양측): 병렬 스폰 (+ 필요 시 QADev 재작성)
       │
       ── 품질 단계 재실행 (항상 Step 1부터) ──
       ├── QualityPLAgent → Claude + Codex 재리뷰 (병렬)
       └── Step 1 통과 후 → TesterAgent 재실행
```

**카운터 규칙:**
- **Step 1 FIX 카운터: 최대 3회** → 초과 시 PMAgent 경유 사용자 ESCALATE
- **Step 2 FIX 카운터: 무제한** — 모든 테스트가 PASS 될 때까지 반복 (사용자 interrupt로만 중단)
- **Step 2 FAIL 후 재진입한 Step 1에서 P0/P1 발견 시 Step 1 카운터는 리셋** (재구현 결과는 새 리뷰 대상)
- **Step 2 반복 FAIL 시 ArchitectAgent가 근본 원인을 재분석하여 계획서를 대폭 수정** (숫자 규칙 없음, Architect 책임)
- **4인 보고 재실행은 선택 아님** — 매 iteration Claude/Codex 재리뷰 + Tester 재실행 (이전과 다른 접근 + 누적 컨텍스트 전달, 리뷰어는 병렬 권장)
- **설계 금지 원칙 유지** — Dev·Engineer·QADev는 새 계획서를 받아 구현만, 설계·분기 결정은 오직 Architect+Refactor 계획서 갱신으로

### 합의 규칙
- 도메인 해석: ResearcherAgent → 오케스트레이터 → ArchitectAgent
- **설계 결정은 ArchitectAgent 단독** — 계획서의 파일·인터페이스·시그니처·API 계약 모두 확정. PL들은 실행 조율만 수행하며 설계 범위 확장·결함 발견 시 반드시 ArchitectAgent로 되돌린다
- **QADev 산출물 감사는 ArchitectAgent** — 구현 단계 종료 시 매핑표 수령 후 Step 1 진입 결정
- 품질 판단: Step 1은 QualityPLAgent가 severity 종합, Step 2는 Tester가 PASS/FAIL 보고. FIX 시 Architect+Refactor 계획서 갱신으로 에스컬레이션

### Write 권한 구조 (path-scoped 강제)
권한은 **prose 금지**가 아닌 **frontmatter의 path scoping**으로 강제된다:
- **`BackendDeveloperAgent`**: `Edit(src/**)` + `Write(src/**)` / deny `tests/**`, `templates/**`, `static/**`, `docs/**`
- **`FrontendDeveloperAgent`**: `Edit|Write(src/mctrader/dashboard/templates/**)` + `Edit|Write(src/mctrader/dashboard/static/**)` / deny `server.py`, `backtest_runner.py`, `domain/**`, `adapters/**`, `ports/**`, `cli/**`, `tests/**`
- **`QADeveloperAgent`**: `Edit|Write(tests/**)` / deny `Edit|Write(src/**)` (production 읽기만)
- **`RefactorAgent`**: **읽기 전용** (Edit/Write 모두 없음) — 분석·제안만. 선행 리팩토링 실행도 Dev(Backend/Frontend) 경유
- **PL/평가 레이어** (`PMAgent` / `ArchitectAgent` / `DeveloperPLAgent` / `EngineerPLAgent` / `QualityPLAgent` / `ResearcherAgent`): Write/Edit 전면 없음. 문서화 필요 시 DocsAgent 위임
- **읽기 전용 평가**: `ClaudeReviewerAgent` / `CodexReviewerAgent` / `TesterAgent` — 결함 발견 시 QualityPLAgent 또는 ArchitectAgent에 평가 전달, 변경은 Architect+Refactor 계획서 갱신으로만

### Codex 플러그인 필수
Codex 플러그인 미설치 시 **Step 1 진행 불가** — 오케스트레이터가 설치 안내 후 중단 보고. `SKIPPED` 경로 허용 안 함.

### 병렬 스폰 권장 (superpowers:dispatching-parallel-agents)
- 구현 단계: QADev + 구현 분기(DevPL / EngineerPL / 양측) 병렬 스폰
- 품질 Step 1: ClaudeReviewerAgent + CodexReviewerAgent 병렬 스폰
- 파일 경합이 없는 읽기 작업 또는 경로 분리된 쓰기 작업만 병렬 허용

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
