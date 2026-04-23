# CLAUDE.md

Claude Code용 오케스트레이션 규칙. 에이전트 상세는 각 `.claude/agents/<Name>.md` (SSOT).

## Project
`mctrader` — 암호화폐 스캘핑 자동매매 프레임워크. Python, 완전 자율 실행. `settings.json`에 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.

## Development Agent Team (21 에이전트 · 6 레인)

```
(Human) 사용자                       # 외부 행위자 — 요구사항 제공·blocking 질문 응답·ESCALATE 수신
   ↓ 요구사항 전달
Orchestrator                        # 최상위 Claude 세션 — 모든 스폰·토큰 예산 소유
 ├── [요구사항] PMOAgent
 │    ├── PMAgent                     # 도메인 요구사항 해석 컨설턴트 (스캘핑·실시간·리스크)
 │    ├── DocsAgent                   # 문서화 단독 writer + 표준 SSOT
 │    ├── RequirementsAnalystAgent    # GPT-5.4 래퍼 (codex exec)
 │    └── ResearcherAgent             # 도메인 웹 리서치 (조건부)
 │
 ├── [설계] ArchitectAgent
 │    ├── CodebaseMapperAgent         # 기존 코드 변호자 (보수)
 │    └── RefactorAgent               # 리팩터링 옹호자 (혁신)
 │    ※ QADev는 조직상 여기 계약(§8 소유자) but 실행은 구현 레인에서 DevPL 산하
 │
 ├── [설계 리뷰] DesignReviewPLAgent
 │    ├── ClaudeDesignReviewAgent     # Claude 네이티브 설계 리뷰
 │    └── CodexDesignReviewAgent      # Codex(GPT-5) 설계 리뷰
 │
 ├── [구현] DeveloperPLAgent
 │    ├── BackendDeveloperAgent       # src/**
 │    ├── FrontendDeveloperAgent      # templates/static
 │    ├── DataEngineerAgent           # storage·exchanges·collector·schemas
 │    ├── ServerEngineerAgent         # deploy·config·scripts (systemd)
 │    └── QADeveloperAgent            # tests/** (Change Plan §8 Test Contract 이행)
 │
 ├── [구현 리뷰] CodeReviewPLAgent
 │    ├── ClaudeCodeReviewAgent       # Claude 네이티브 코드 리뷰
 │    └── CodexCodeReviewAgent        # Codex(GPT-5) 코드 리뷰
 │
 └── [테스트] TestAgent               # Orchestrator 직속 pytest 최종 게이트
```

**주체 명칭**:
- **Orchestrator** = 최상위 Claude 세션 (모든 Agent 툴 스폰, 토큰 예산 소유)
- **(Human) 사용자** = 인간 행위자

## 레인 6개 · 단계 정의

```
요구사항 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → 테스트
```

모든 Story는 **full 6 레인** 통과. Fast-path 없음.

- **요구사항**: Orchestrator가 사용자 요건 접수 → Jira Story 생성 → DocsAgent가 Confluence Story 페이지 생성(§1-2) → PMOAgent(PMAgent + Analyst + Researcher 조건부) 통합 명세서 확정 → Story 페이지 §3-6 갱신
- **설계**: Architect가 CodebaseMapper(변호자) → Refactor(혁신자) 순 스폰 → 대립 조정 → Change Plan 확정 (§8 Test Contract 포함) → DocsAgent가 `docs/change-plans/<slug>.md` 저장 + Story 페이지 §7 미러링
- **설계 리뷰**: DesignReviewPL이 Claude/Codex 설계 리뷰 종합 → PASS 시 구현 진입 / FIX 시 Architect 회귀 (최대 3회)
- **구현**: Orchestrator가 QADev + DeveloperPL 병렬 스폰. DevPL 산하 4 Dev는 의존성 없는 한 **모두 병렬**. Architect는 stateless 재스폰되어 매핑표 감사
- **구현 리뷰**: CodeReviewPL이 Claude/Codex 코드 리뷰 종합 → PASS 시 테스트 진입 / FIX 시 DeveloperPL 1차 진단 → Architect 최종 판정 (최대 3회)
- **테스트**: TestAgent pytest (기능 → 성능 순차). ALL PASS 시 완료 / FAIL 시 DeveloperPL 1차 진단 → Architect 최종 판정 (무제한)

## 오케스트레이션 규칙

> **Orchestrator 행동 SSOT**: [`docs/orchestrator-playbook.md`](docs/orchestrator-playbook.md) — 세션 생명주기, 사용자 상호작용, 스폰 프롬프트 템플릿, 병렬 스폰 판단, Story 페이지 동기화 체크리스트, FIX 상태 머신, 세션 재개 복원, 토큰 예산, 트러블슈팅.

### 플랫폼 제약
하위 에이전트는 Agent 툴 사용 불가 — 재귀 스폰 금지. 모든 스폰은 최상위 Claude가 직접. 서브에이전트 간 직접 통신 불가 (Orchestrator 경유).

### 컨텍스트 전달 (Confluence Story 페이지 SSOT)

각 Jira Story마다 **Confluence Story 페이지**가 컨텍스트 단일 출처(SSOT). 에이전트 프롬프트에는 **Story 페이지 URL만 주입**하고, 필요한 내용은 에이전트가 직접 `mcp__atlassian__getConfluencePage(pageId=N)`로 fetch.

**Story 페이지 위치**:
- Parent: `https://mctrader.atlassian.net/wiki/spaces/MCTRADER/pages/589846/Stories` (pageId=589846)
- 각 Story: `MCTRADER-N: <제목>` 페이지 1개
- 생성·갱신 전담: **DocsAgent**

**섹션 갱신 의뢰 경로**: 각 에이전트는 Orchestrator 경유 DocsAgent에 "Story 페이지 MCTRADER-N 섹션 {X}에 다음 내용 추가" 의뢰. 직접 write 하는 에이전트는 DocsAgent 단독.

섹션 규격·단계별 책임 상세는 [`.claude/agents/DocsAgent.md`](.claude/agents/DocsAgent.md) 참조.

### Never-skippable 에이전트

- **요구사항**: **PMOAgent**, **RequirementsAnalystAgent** (Orchestrator가 "요건 이미 명확" 명시 시만 생략)
- **설계**: **ArchitectAgent**, **CodebaseMapperAgent**, **RefactorAgent**
- **설계 리뷰**: **DesignReviewPLAgent**, **ClaudeDesignReviewAgent**, **CodexDesignReviewAgent**
- **구현**: **DeveloperPLAgent**, **QADeveloperAgent**
- **구현 리뷰**: **CodeReviewPLAgent**, **ClaudeCodeReviewAgent**, **CodexCodeReviewAgent**
- **테스트**: **TestAgent**

조건부 생략: ResearcherAgent(PMO 판정 — Analyst 키워드 비어있을 때), PMAgent(PMO 판정), Backend/Frontend/DataEng/ServerEng(Change Plan이 해당 영역 미변경 시). DocsAgent는 모든 단계에서 필수 (write 창구).

### 스폰 시퀀스

```
[요구사항] Orchestrator → PMOAgent → (PMAgent 도메인 해석 + Analyst + Researcher 조건부) → PMOAgent 통합
        · 상충 시 Orchestrator 경유 사용자 에스컬레이션
        · "사용자 확인 필요" 항목은 blocking wait
        · 통합 명세서는 Confluence Story 페이지 §3-6에 DocsAgent 경유 반영

[설계] Orchestrator → ArchitectAgent
        ├── CodebaseMapperAgent (as-is 변호)
        └── RefactorAgent (to-be 혁신)
        → Architect 대립 조정 → Change Plan 확정 (§8 Test Contract 포함)
        → DocsAgent 저장 + Story 페이지 §7 미러링

[설계 리뷰] Orchestrator → DesignReviewPLAgent
        ├── ClaudeDesignReviewAgent
        └── CodexDesignReviewAgent  (병렬)
        → severity 종합 → PASS or FIX (최대 3회)
        · FIX: Orchestrator 경유 Architect 회귀 → Change Plan 갱신 → 설계 리뷰 재실행

[구현] Orchestrator가 병렬 스폰
        ├── DeveloperPLAgent
        │    ├── BackendDeveloperAgent
        │    ├── FrontendDeveloperAgent
        │    ├── DataEngineerAgent
        │    └── ServerEngineerAgent
        └── QADeveloperAgent (조직상 Architect 계약 이행자, 실행상 구현 레인 병렬)
        → 4 Dev는 의존성 없는 한 병렬
        → DeveloperPL 완료 보고 → Orchestrator가 Architect를 stateless 재스폰해 매핑표 감사
        → 감사 PASS 시 Orchestrator가 구현 리뷰 레인 진입

[구현 리뷰] Orchestrator → CodeReviewPLAgent
        ├── ClaudeCodeReviewAgent
        └── CodexCodeReviewAgent  (병렬)
        → severity 종합 → PASS or FIX (최대 3회)
        · FIX: Orchestrator 경유 DeveloperPL 1차 원인 진단 → Architect 최종 판정
          · 설계 원인 판정 시: Change Plan 갱신 → 설계 리뷰부터 재실행
          · 구현 원인 판정 시: 구현만 재실행 → 구현 리뷰 재실행

[테스트] Orchestrator → TestAgent
        · 모드 1 (기능): tests/unit tests/integration tests/infra
        · 모드 2 (성능): tests/perf -- baseline 대비 mean 10% 이상 악화 시 FAIL
        · ALL PASS → DocsAgent (최종 완료) → Jira Story 완료 전이
        · FAIL → Orchestrator 경유 DeveloperPL 1차 진단 → Architect 최종 판정 (구현 원인 / 설계 원인)
          · 설계 원인: Change Plan 갱신 → 설계 리뷰부터 재실행
          · 구현 원인: 구현만 재실행 → 구현 리뷰 재실행
          · 재진입한 구현 리뷰에서 P0/P1 발견 시 구현 리뷰 카운터 리셋 (테스트 FIX는 무제한)
```

### FIX 루프

**트리거**:
- 설계 리뷰 P0/P1 → Architect 회귀
- 구현 리뷰 P0/P1 → DeveloperPL 1차 진단 → Architect 최종 판정
- 테스트 FAIL → DeveloperPL 1차 진단 → Architect 최종 판정

**카운터 (Jira 라벨 count 단일 — Orchestrator 세션 메모리 제거)**:
- **설계 리뷰 FIX 최대 3회** (`fix:설계-리뷰-retry` 라벨 count) → 초과 시 Orchestrator 경유 사용자 ESCALATE
- **구현 리뷰 FIX 최대 3회** (`fix:구현-리뷰-retry` 라벨 count)
- **테스트 FIX 무제한** (`fix:테스트-retry` 라벨 count)
- **테스트 FAIL 후 재진입한 구현 리뷰**에서 P0/P1 발견 시 구현 리뷰 카운터 리셋 (재구현 결과는 새 리뷰 대상)
- **수평 호출 금지** — ReviewPL/TestAgent/Architect/DeveloperPL 간 직접 호출 금지, 모든 게이트 재실행·회귀 요청은 Orchestrator 경유

**카운터 접근**: Orchestrator가 FIX 판정 시마다 `searchJiraIssuesUsingJql(jql="key=MCTRADER-N")` + label count로 fresh 조회. 세션 메모리 저장 없음. 컨텍스트 압축·세션 재개 시에도 복원 로직 불필요.

### 원인 판정 decision table (구현 리뷰·테스트 FAIL 시)

**프로세스**: DeveloperPL 1차 원인 진단 → Orchestrator 경유 → Architect 최종 판정 + evidence pack(Change Plan 버전 + 리뷰 findings + 테스트 로그) 첨부 의무. Story 페이지 §10에 누적.

| Failure 유형 | 1차 가정 | 설계 원인 escalate 조건 |
|---|---|---|
| Unit test FAIL | 구현 | 테스트 사양이 Change Plan 계약과 불일치 |
| Integration test FAIL | 구현 | 모듈 경계·계약 위반 |
| Infra test FAIL | 구현 | 배포/환경 요구 Change Plan 누락 |
| 성능 test FAIL | **설계** | 단순 최적화로 해결되면 구현 |
| Code review P0 보안 | 구현 | trust boundary 설계 오류 |
| Code review P0 아키텍처 | **설계** | 레이어·의존성 방향 위반 |
| **Code review P1 품질** | **설계** | — (품질 이슈는 설계 지침·패턴 부재에서 기인) |

- **설계 원인 판정 시**: Change Plan 갱신 → 설계 리뷰 레인부터 재실행
- **구현 원인 판정 시**: Change Plan 유지, 구현만 재실행 → 구현 리뷰 재실행

### Review severity 종합 규칙 (DesignReviewPL / CodeReviewPL 공유)

**Dedup**:
- 같은 파일·라인·카테고리(또는 섹션·ADR) finding은 1건 병합
- severity는 두 리뷰 중 **높은 쪽 채택**

**종합 판정**:
| 조건 | 판정 |
|------|------|
| P0 ≥ 1건 | **FIX (최우선)** |
| P1 ≥ 2건 | **FIX** |
| P1 = 1건 | **FIX 재량** (근거 포함 Orchestrator 전달) |
| P2만 | **PASS** |

**Noise 분류**: ReviewPL이 1차 `valid/noise` 분류 → Architect가 noise 재배정 가능 (과정을 Jira 코멘트 의무 기록).

### CodebaseMapper ↔ Refactor 이념 대립

- **CodebaseMapperAgent** = **기존 코드 변호자** (보수). "기존 패턴 유지, 변경 영향 최소화"가 기본 입장
- **RefactorAgent** = **리팩터링 옹호자** (혁신). "결합도 감소, 인터페이스 분리, 패턴화"가 기본 입장
- Architect가 Mapper → Refactor **순 스폰** (as-is 앵커 먼저, 개선안 뒤)
- 두 관점 충돌 시 Architect가 결정 근거와 함께 Change Plan §2(현재 구조)와 §3(도입할 설계)에 명시
- DesignReviewPL이 "Mapper 변호 근거 일축 여부 / Refactor 과잉 제안 여부" 교차 체크

### CodebaseMapper Freshness

- **매 설계 레인 진입 시 재스폰** (이전 Story 산출물 재사용 금지)
- 리뷰·테스트에서 설계 레인 복귀 시에도 재스폰 (구현 레인에서 코드 변경 전제)

### Architect 라이프사이클 (stateless 재스폰)

- 매 트리거마다 Orchestrator가 신규 스폰 — 세션 유지 없음
- Story 페이지 §1-8 재로딩으로 컨텍스트 복원
- 토큰 비용: 재스폰 당 ~5-10k tokens. FIX 3회 가정 시 15-30k overhead (playbook §8 참조)

### Write 권한 (path-scoped — 각 agent md frontmatter가 SSOT)
- **Write 권한 있음**: BackendDev(src/**), FrontendDev(templates·static), QADev(tests/**), DataEng(storage·exchanges·collector·schemas), ServerEng(deploy·config·scripts), **DocsAgent(Jira·Confluence·docs/** 모든 문서)**
- **읽기 전용**: CodebaseMapper, Refactor, DesignReviewPL, ClaudeDesignReview, CodexDesignReview, CodeReviewPL, ClaudeCodeReview, CodexCodeReview, TestAgent, Researcher, ArchitectAgent, DeveloperPLAgent, PMOAgent, PMAgent, RequirementsAnalyst
- **외부 도구 wrapper**: RequirementsAnalyst(Bash(codex exec *)), CodexDesignReview·CodexCodeReview(Bash(node *))

### 문서 write 단독 writer 원칙

**DocsAgent만이 Jira·Confluence·docs/** write 가능**. 20 에이전트는 모두 write 권한 없음. 문서 작업은 전원 Orchestrator 경유 DocsAgent에 의뢰.

- 이전 "전원 직접 Jira 기록" 방침(commit 04a6f00)은 **폐기**
- 문서화 표준(Jira 코멘트 포맷, Story 페이지 섹션 규격, Change Plan 템플릿, ADR 템플릿)은 [`.claude/agents/DocsAgent.md`](.claude/agents/DocsAgent.md) SSOT
- 다른 에이전트 md에는 "문서화 표준은 DocsAgent.md 참조" 1줄만

### Codex CLI / 플러그인 필수
- CodexDesignReviewAgent, CodexCodeReviewAgent: Codex 플러그인
- RequirementsAnalyst: `codex` CLI
- 미설치 시 해당 레인 진행 불가, Orchestrator가 설치 안내 후 중단

### 병렬 스폰 권장
- 요구사항: PMAgent + Analyst + Researcher (Analyst 선행 필수, 나머지 병렬 가능)
- 구현: QADev + DevPL의 4 Dev (의존성 없는 한 모두 병렬)
- 리뷰: Claude + Codex 병렬 (Design/Code 각 레인)

## ADR (Confluence Pages SSOT)

- Space: `MCTRADER` / 루트 페이지 `ADR` / 6개 카테고리 parent 하위
- 카테고리: Team & Process / Architecture / Data & Storage / Infrastructure / Dashboard & UX / Trading Strategy
- 목록: `mcp__atlassian__searchConfluenceUsingCql(cql="label='adr' AND space='MCTRADER'")`
- 상세: `mcp__atlassian__getConfluencePage(pageId=N)`
- 세션 시작 시 ADR 목록 조회, 결정 사항 번복 금지
- 설계 결정마다 신규 ADR 생성 (번호 = 기존 최대 + 1)
- 신규 ADR은 결정 성격에 맞는 카테고리 페이지의 child로 생성

### 생성 기준
라이브러리·프레임워크 선택 / 아키텍처 패턴 / 데이터 저장·처리 / 인프라·배포 / 전략 도메인 핵심 개념

### DesignReview ADR 정합성 체크 (필수)

DesignReviewPL 프롬프트에 명시:
- Story 페이지 §3에서 관련 ADR 목록 fetch
- Change Plan 결정이 ADR 결정을 **위반**하는가 explicit 검토
- 위반 발견 시 **P0 severity 고정**
- 설계 의도가 ADR 변경이면 "신규 ADR 필요" 발견사항으로 기록 (신규 ADR 없이 ADR 변경 금지)

### 페이지 템플릿
제목 `ADR-NNN: <결정>` + label `adr` + 상단 메타데이터 테이블(번호/상태/카테고리/결정일/관련파일).
본문 섹션: `## 상태 / ## 컨텍스트 / ## 결정 / ## 결과 / ## 다이어그램(Mermaid) / ## 관련 파일`

## 버그 기록 (Jira)
- 프로젝트: `MCTRADER` (키 = 카테고리 구분 없음, label로 분류)
- 신규 버그: DocsAgent가 `mcp__atlassian__createJiraIssue(projectKey="MCTRADER", issueTypeName="작업", labels=["bug", <component>])`
- 해결 시: DocsAgent가 `mcp__atlassian__transitionJiraIssue`로 "완료" 전이

## Jira 워크플로우 (MCTRADER 프로젝트)

사용자 요구사항 접수부터 PR merge까지의 모든 의사결정·협업을 Jira에 영속 기록. 쓰기는 DocsAgent 단독.

### 계층
- **Epic** = 사용자 요구사항 1건. Orchestrator가 PMOAgent 스폰 직전 DocsAgent 경유 생성
- **Story** = PR 1건 (= Change Plan 1건). Orchestrator(필요 시 PMO 조언) scope 분해 시 확정된 독립 작업 단위만 생성

### 상태 + Phase Label 방식

Jira 기본 3-state 유지(`해야 할 일`/`진행 중`/`완료`). 단계는 **phase label**로 표현.

```
[생성] status=해야 할 일 → phase:요구사항 label 부여 + 진행 중 전이
  ↓ PMO 통합 명세서 확정
[phase:요구사항 → phase:설계]
  ↓ Architect Change Plan 확정
[phase:설계 → phase:설계-리뷰]
  ↓ 설계 리뷰 PASS
[phase:설계-리뷰 → phase:구현]
  ↓ 구현 완료 + 매핑표 감사 PASS
[phase:구현 → phase:구현-리뷰]
  ↓ 구현 리뷰 PASS
[phase:구현-리뷰 → phase:테스트]
  ↓ PR merged (GitHub for Jira 자동 전이)
status=완료
```

### Transition ID
- `해야 할 일` → 11 / `진행 중` → 21 / `완료` → 31

### FIX 루프 라벨 규칙
- **설계 리뷰 P0/P1**: `phase:설계-리뷰 → phase:설계` + `fix:설계-리뷰-retry` 라벨 추가 + `[FIX #N] ArchitectAgent: <원인>` 코멘트 (DocsAgent 기록)
- **구현 리뷰 P0/P1**: `phase:구현-리뷰 → phase:구현` + `fix:구현-리뷰-retry` 라벨 추가 + `[FIX #N] ArchitectAgent: 구현 원인 / 설계 원인` 판정 코멘트
- **테스트 FAIL**: `phase:테스트 → phase:구현` + `fix:테스트-retry` 라벨 추가 + Architect 판정 코멘트

카운터는 Jira 라벨 count 단일. 세션 메모리 저장 없음.

### 코멘트 규칙 (DocsAgent 단독 기록)

형식·phase prefix 8종은 [`.claude/agents/DocsAgent.md`](.claude/agents/DocsAgent.md) SSOT 참조. 다른 에이전트는 Orchestrator에 기록 요청만 수행, DocsAgent가 실행.

### GitHub 연계
- 모든 구현 커밋: `[MCTRADER-N] <type>: <summary>` prefix
- PR 제목: `[MCTRADER-N] <Story 요약>`
- PR 본문: `Jira: https://mctrader.atlassian.net/browse/MCTRADER-N` 상단 포함
- GitHub for Jira 앱이 PR merge 시 Story 자동 `완료` 전이

### Labels 체계

**신 체계 (2026-04-24 이후 신규 티켓)**:
- `phase:*` (현재 단계 1개): `phase:요구사항`, `phase:설계`, `phase:설계-리뷰`, `phase:구현`, `phase:구현-리뷰`, `phase:테스트`
- `fix:*` (누적): `fix:설계-리뷰-retry`, `fix:구현-리뷰-retry`, `fix:테스트-retry`
- `component:*`: `component:collector`, `component:dashboard`, `component:strategy`, `component:backtest`
- `adr:NNN`
- `bug`

**Legacy 라벨 (2026-04-24 이전 기존 이슈)**:
- `phase:요건`, `phase:리뷰-step1`, `phase:테스트-step2`, `fix:step1-retry`, `fix:step2-retry`, `branch:A`, `branch:B`, `branch:A+B`
- 기존 이슈는 **legacy 라벨 유지** (감사 이력). 마이그레이션 하지 않음. 신규 티켓부터 v2 라벨 적용.
- `migrated-from-repo` 라벨 이슈(2026-04-23 이관분)는 v2 체계 외 legacy로 분류.

### 대시보드 JQL 예시
- 현재 구현 리뷰 중: `project = MCTRADER AND labels = "phase:구현-리뷰"`
- 현재 설계 리뷰 중: `project = MCTRADER AND labels = "phase:설계-리뷰"`
- FIX 대상: `project = MCTRADER AND labels in ("fix:설계-리뷰-retry", "fix:구현-리뷰-retry", "fix:테스트-retry")`
- Story 전체: `project = MCTRADER AND issuetype = 작업 AND statusCategory != Done`

### 원문 위치
Jira는 **워크플로우 상태·이벤트 로그**만. 구조화된 원문은 각 도구 유지:
- **요구사항·컨텍스트·서사**: Confluence Story 페이지 (`Stories` parent, pageId=589846). 섹션 1-11
- **설계 실행 명세**: `docs/change-plans/<slug>.md` (Git-versioned). Story 페이지 §7 요약 미러링
- **설계 결정(ADR)**: Confluence `ADR` 트리. Story 페이지 §3에서 인용
- **코드 리뷰 원문**: GitHub PR 설명·코멘트. Story 페이지 §9에 요약 집계

## Confluence Story 페이지 규약 요약

- Space `MCTRADER` / parent `Stories` (pageId=589846) / 각 Story `MCTRADER-N: <제목>` 페이지 1개
- Template `_Template: Story Page` (pageId=753705) 복제해 신규 생성
- DocsAgent가 생성·섹션 갱신 전담
- 세부 규약·섹션 책임: [`.claude/agents/DocsAgent.md`](.claude/agents/DocsAgent.md) SSOT

## Domain Knowledge
- [OrderBook/Trade 시각화 스펙 (Confluence)](https://mctrader.atlassian.net/wiki/spaces/MCTRADER/pages/589826)

## Trading Domain
암호화폐 · 스캘핑(단기·고빈도) · 완전 자율 실행 · 실시간 가격·호가창
