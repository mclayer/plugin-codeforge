# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`mctrader` — 암호화폐 스캘핑 자동매매 프레임워크. Python 기반, 완전 자율 실행.

## Configuration

`settings.json`에 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 활성화됨.

## Development Agent Team

```
User
 └── PMAgent                              # 요건 접수, 팀 합의 관리
      ├── PMOAgent                         # 요건 단계 PL — Analyst/Researcher 종합, 통합 명세서 작성
      │    ├── DocsAgent                    # ADR, README, 요건 명세서, Change Plan 등 문서화 (조직상 PMO 산하, 기능상 전단계 스폰)
      │    ├── RequirementsAnalystAgent     # GPT-5.4 래퍼, 사용자 요건 확장 해석 (유스케이스·AC·엣지·암묵 가정)
      │    └── ResearcherAgent              # 도메인 웹 리서치 (Analyst 키워드 기반 타겟 조사)
      └── ArchitectAgent                   # 설계/패턴 결정 (PMOAgent 통합 명세서 입력), QADev 산출물 감사, FIX 원인 판정
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

**에이전트별 상세 원칙·역할·보고 포맷은 각 `.claude/agents/<AgentName>.md` 파일에서 정의한다 (SSOT).** CLAUDE.md는 오케스트레이션 규칙만 다루며 개별 에이전트 역할은 복제하지 않는다.

### 용어 정의
- **요건 단계**: PMAgent 요건 접수부터 PMOAgent 통합 명세서 확정까지
- **설계 단계**: ArchitectAgent가 Change Plan 확정 + DocsAgent가 `docs/change-plans/<slug>.md` 저장 완료까지
- **구현 단계**: QADev(tests/**) + Dev/Engineer(src/**, 인프라) 병렬 실행 + ArchitectAgent의 **QADev 매핑표 감사(구현 산출물 점검)** 까지
- **품질 단계**: **Step 1(QualityPL 리뷰 게이트)** + **Step 2(Tester pytest 게이트)** — 이 둘로만 한정
- **Change Plan**: `docs/change-plans/<slug>.md`에 저장되는 변경 계획서 (DocsAgent 담당, slug=kebab-case, Dev 스폰 전 저장 필수 — 생략 불허)
- **통합 요건 명세서**: `docs/requirements/<slug>.md`에 저장되는 PMOAgent 산출물 (복잡 요건 시 DocsAgent 경유 조건부 저장)

## 오케스트레이션 규칙

### 플랫폼 제약
**하위 에이전트는 Agent 툴을 사용할 수 없다 — 재귀 스폰 불가.** 모든 스폰은 최상위 Claude(오케스트레이터)가 직접 수행한다. 서브에이전트 간 직접 통신 불가 — 보고는 항상 오케스트레이터가 수령하고 다음 에이전트에 투입한다.

### 컨텍스트 전달 원칙 (모든 에이전트 스폰 공통)
오케스트레이터가 에이전트를 스폰할 때 컨텍스트를 **최대한 자세하게** 프롬프트에 포함한다. 요약·축약 지양, 외부 참조(ADR 번호·파일 경로만 언급)는 불충분. 외부 모델(GPT-5.4 등)이 레포를 자율 탐색하도록 방치하면 지연·토큰이 증가하고 분석 일관성이 떨어진다.

- **ADR이 관련되면 본문 verbatim 포함** — 번호만 언급 금지. `mcp__GitLab__get_issue`로 fetch 후 "## 상태 / ## 컨텍스트 / ## 결정 / ## 결과" 4개 섹션 모두 전달 (Deprecated/Superseded 상태도 명시)
- **관련 코드 경로는 현재 책임 요약과 함께** — 파일 경로만 나열 금지
- **관련 문서 발췌** — 원본 섹션 verbatim, 임의 요약 금지 ("{다른 섹션 생략}" 같은 표식으로 생략 범위 명시)
- **이전 스레드 합의사항** — 이미 확정된 사용자 답변·결정 명시 포함

컨텍스트 길이가 과도하면 관련성 높은 항목 우선 발췌하되 **임의 요약 금지** (섹션 단위 verbatim + 생략 범위 표식).

### PMAgent 선행 의무 (관문)
오케스트레이터는 PMOAgent / ArchitectAgent / 구현 에이전트 등 하위 에이전트를 스폰하기 전에 **반드시 PMAgent를 먼저 스폰**한다. PMAgent 출력:
1. 태스크 유형 분류
2. 필요 에이전트 목록 및 스폰 순서 (요건 단계 PMOAgent/Analyst, 구현 단계 QADev 포함 필수 명시)
3. 생략 가능 에이전트와 그 이유 (**아래 Never-skippable은 절대 불가**)

"작은 수정이라 생략" 판단은 오케스트레이터 권한 밖이다.

#### 절대 생략 불가 에이전트 (Never-skippable — 단계별)
PMAgent의 "생략 가능" 판단은 **아래 에이전트에 절대 적용할 수 없다**:

- **요건 단계 필수**
  - **`PMOAgent`** — 하위 중 하나라도 호출되면 필수 (종합 책임자)
  - **`RequirementsAnalystAgent`** — 기본 필수. PMAgent가 "요건 이미 명확" 명시 선언 시만 생략 가능
- **구현 단계 필수**
  - **`QADeveloperAgent`** — TDD 원칙상 모든 변경에 tests/** 작성 필수
- **품질 단계 필수**
  - **`QualityPLAgent`** — Claude/Codex severity 종합 필수 (Step 1 게이트)
  - **`ClaudeReviewerAgent`** — Claude 네이티브 리뷰 필수
  - **`CodexReviewerAgent`** — Codex 외부 리뷰 필수
  - **`TesterAgent`** — pytest 실행 필수 (Step 2 게이트)

PMAgent는 조건부 생략만 제안할 수 있다:
- **ResearcherAgent** — Analyst 산출물에 "Researcher 리서치 키워드"가 비어있을 때 (생략 판정자: PMOAgent)
- **EngineerPLAgent** 계열 — 인프라 변경이 없는 순수 코드 작업
- **DocsAgent** — ADR/요건 명세서/Change Plan 저장은 항상 필수, 그 외 README·가이드 등 문서 작업이 해당 요건에 포함되지 않을 때만 생략

### 스폰 시퀀스 (표준 — TDD 병렬 구현 + 순차 품질 게이트)

ArchitectAgent가 "EngineerPL 우선" 원칙에 따라 구현 담당 분기를 판단 후 계획서에 명시한다. QADev는 분기와 무관하게 계획서 전체를 대상으로 **한 번만** 스폰되어 Dev/Engineer와 **병렬** 진행된다.

```
─── 요건 단계 (PMOAgent 주도) ───
PMAgent (요건 접수)
 → PMOAgent
      ├── RequirementsAnalystAgent (필수)       # GPT-5.4 래퍼, 확장 명세서 작성
      └── ResearcherAgent (조건부, 키워드 존재 시)   # Analyst 키워드 기반 타겟 리서치
 → PMOAgent 통합 명세서 작성
      · 상충 발견 시 PMAgent 경유 사용자 에스컬레이션
      · "사용자 확인 필요" 항목이 남아있으면 PMAgent 경유 재확인
 → DocsAgent (조건부): docs/requirements/<slug>.md 저장

─── 설계 단계 (ArchitectAgent 단독, 분기 결정 포함) ───
PMOAgent 통합 명세서 → ArchitectAgent
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

**분기 선택 규칙**:
- 1순위 분기 A (EngineerPL) — 인프라 레벨 해결이 동등 이상 이득
- 2순위 분기 B (DevPL) — 코드 수정이 더 단순하거나 인프라 오버헤드가 큰 경우
- A+B 병렬 — 양측 수정이 동시에 필요한 경우
- **Change Plan에 분기 선택 근거 한 줄 기록** 필수
- 상세: [`ArchitectAgent.md`](.claude/agents/ArchitectAgent.md)

### FIX 루프 (순차 게이트 + 차별 카운터)

**트리거 조건 (OR):**
1. **Step 1 — QualityPL severity P0/P1** (Claude/Codex 합집합, 객관적 결함만; P2/P3는 통과)
2. **Step 2 — TesterAgent FAIL** (pytest 실패)

**처리 시퀀스 (모든 iteration 공통):**
```
FIX 트리거
  └── [Iteration]
       설계 단계: Architect ↔ Refactor → 계획서 갱신 + 분기(A/B/A+B) 재결정
                  · Architect가 실패 원인 판정 (코드 결함 vs 테스트 결함) → Dev 재구현/QADev 재작성 담당 명시
       구현 단계: 계획서 분기에 따라 Dev 또는 Engineer 재실행 (+ 필요 시 QADev 재작성)
       품질 재실행: 항상 Step 1부터 — QualityPL(Claude+Codex 병렬 재리뷰) → 통과 시 Tester 재실행
```

**카운터 규칙:**
- **Step 1 FIX 최대 3회** → 초과 시 PMAgent 경유 사용자 ESCALATE
- **Step 2 FIX 무제한** — 모든 테스트 PASS 될 때까지 반복 (사용자 interrupt로만 중단)
- **Step 2 FAIL 후 재진입한 Step 1에서 P0/P1 발견 시 Step 1 카운터 리셋** (재구현 결과는 새 리뷰 대상)
- **Step 2 반복 FAIL 시 Architect가 근본 원인 재분석하여 계획서 대폭 수정** (숫자 규칙 없음, Architect 책임)
- **품질 단계 재실행은 선택 아님** — 매 iteration Claude/Codex 재리뷰 + Tester 재실행 (이전과 다른 접근 + 누적 컨텍스트 전달)
- **설계 금지 원칙 유지** — Dev·Engineer·QADev는 새 계획서를 받아 구현만, 설계·분기 결정은 오직 Architect+Refactor 계획서 갱신으로

### Write 권한 구조 (path-scoped 강제)
권한은 **prose 금지**가 아닌 **각 agent md 파일 frontmatter의 path scoping** 으로 강제된다 (각 agent md = SSOT). 요약:
- **Dev 쓰기**: `BackendDeveloperAgent`(src/**) / `FrontendDeveloperAgent`(templates·static) / `QADeveloperAgent`(tests/**) / `DataEngineerAgent`·`ServerEngineerAgent`(분기 A 경로)
- **읽기 전용**: `RefactorAgent`, `ClaudeReviewerAgent`, `CodexReviewerAgent`, `TesterAgent`, `ResearcherAgent`, 모든 PL (PMAgent/PMOAgent/ArchitectAgent/DeveloperPLAgent/EngineerPLAgent/QualityPLAgent)
- **외부 도구 wrapper**: `RequirementsAnalystAgent` — `Bash(codex exec *)` 및 `/tmp/req-analysis-*` 임시 파일 정리만
- **문서 쓰기 전담**: `DocsAgent` — `.md` 파일 + GitLab MCP (ADR·요건 명세서·Change Plan)

개별 에이전트의 정확한 allow/deny 리스트는 해당 agent md frontmatter에서 확인한다.

### Codex CLI / 플러그인 필수
- **CodexReviewerAgent (Step 1)**: Codex 플러그인 필요 — 미설치 시 Step 1 진행 불가
- **RequirementsAnalystAgent (요건 단계)**: `codex` CLI (`/opt/homebrew/bin/codex` 또는 `$PATH` 내) 필요 — 미설치 시 요건 단계 진행 불가
- 어느 한 쪽이라도 미설치 시 오케스트레이터가 설치 안내 후 중단 보고. `SKIPPED` 경로 허용 안 함

### 병렬 스폰 권장 (superpowers:dispatching-parallel-agents)
- 구현 단계: QADev + 구현 분기(DevPL / EngineerPL / 양측) 병렬 스폰
- 품질 Step 1: ClaudeReviewerAgent + CodexReviewerAgent 병렬 스폰
- 파일 경합이 없는 읽기 작업 또는 경로 분리된 쓰기 작업만 병렬 허용

## ADR (Architecture Decision Records)

### GitLab Issues가 유일한 진실의 원천 (SSOT)
**모든 ADR은 GitLab Issues에 보관된다. CLAUDE.md에는 목록을 미러링하지 않는다.**
- 프로젝트: `mctrader1/mctrader` (project ID `81469985`)
- 조회: https://gitlab.com/mctrader1/mctrader/-/issues/?label_name[]=ADR
- 조회 도구: `mcp__GitLab__list_issues(project_id="81469985", labels=["ADR"])` / 상세 조회 `mcp__GitLab__get_issue(issue_iid=N)`

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
