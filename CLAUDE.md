# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`mctrader` — 암호화폐 스캘핑 자동매매 프레임워크. Python 기반, 완전 자율 실행.

## Configuration

`settings.json`에 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 활성화됨.

## Development Agent Team

```
User
 └── PMAgent                  # 요건 해석, 작업 범위 조율, 팀 합의 관리
      ├── TesterAgent          # pytest 실행 전담 + 실패 시 디버그 루프 트리거
      ├── DocsAgent            # ADR, README 등 작업 전반의 문서화 담당
      ├── DomainPLAgent        # 암호화폐 트레이딩 도메인 해석 및 스펙 변환
      └── ArchitectAgent       # 설계/패턴 결정, 기술 최종 의사결정
           ├── DeveloperPLAgent  # 구현 가능성, 레이어 계약, 코드 품질 관리
           │    ├── FrontendDeveloperAgent
           │    ├── BackendDeveloperAgent
           │    ├── RefactorAgent
           │    └── QAAgent      # 테스트 코드 작성 전담 (실행은 TesterAgent)
           └── EngineerPLAgent     # 인프라 솔루션 검토 (Linux → Kubernetes)
                ├── DataEngineerAgent  # 데이터 파이프라인 설계 및 구현
                └── ServerEngineerAgent  # Linux 서버 및 서버 엔지니어링 수행
```

### 오케스트레이션 제약 (플랫폼 한계)

**하위 에이전트는 Agent 툴을 사용할 수 없다** — 재귀 스폰 불가.
따라서 실제 팀 실행 구조는 다음과 같다:

```
최상위 Claude (오케스트레이터)
 ├── PMAgent 스폰               → 요건 해석, 작업 분해, 스폰 계획 보고
 ├── DomainPLAgent 스폰         → 도메인 스펙 결정
 ├── ArchitectAgent 스폰        → 설계 결정
 ├── DeveloperPLAgent 스폰      → 구현 계획 + 병렬 스폰 전략
 ├── FrontendDeveloperAgent 스폰 → UI/템플릿 구현
 ├── BackendDeveloperAgent 스폰  → 서버/도메인 구현
 ├── RefactorAgent 스폰         → 리팩토링
 ├── QAAgent 스폰               → 테스트 코드 작성
 ├── TesterAgent 스폰           → pytest 실행 → FAIL 시 디버그 루프 진입
 └── DocsAgent 스폰             → ADR 등록, 문서화
```

### TesterAgent 디버그 루프 (자동 실행)

TesterAgent가 FAIL을 보고하면 오케스트레이터는 아래 루프를 자동 실행한다. 사용자 확인 불필요.

```
TesterAgent FAIL 보고
  └── [Iteration 1~3]
       ├── ArchitectAgent 스폰  → 실패 컨텍스트 분석, 수정 에이전트 및 수정 방향 지시
       ├── BackendDeveloperAgent 또는 FrontendDeveloperAgent 스폰  → 수정 구현
       └── TesterAgent 재스폰   → pytest 재실행

  → 3회 반복 후에도 FAIL: 사용자에게 에스컬레이션 (루프 종료)
  → PASS 달성: 루프 종료, 다음 단계 진행
```

**루프 규칙:**
- ArchitectAgent는 매 iteration마다 이전 실패 원인과 수정 내용을 누적 컨텍스트로 받는다
- 동일한 수정을 반복하면 안 됨 — ArchitectAgent는 이전 시도와 다른 접근을 취해야 한다
- 최대 3회 초과 시 루프를 강제 종료하고 실패 내용을 사용자에게 보고한다

PMAgent는 "스폰하는 관리자"가 아니라 **요건 해석 + 작업 분해 컨설턴트**다.

### PMAgent 스폰 의무 규칙 (관문 역할)

**오케스트레이터는 구현 에이전트(FrontendDeveloperAgent, BackendDeveloperAgent, RefactorAgent 등)를 스폰하기 전에 반드시 PMAgent를 먼저 스폰해야 한다.**

PMAgent의 출력물은 다음을 포함한다:
1. 태스크 유형 분류 (버그 수정 / 기능 추가 / 리팩토링 / 인프라 등)
2. 필요한 에이전트 목록 및 스폰 순서
3. 생략 가능한 에이전트와 그 이유 (생략은 PMAgent가 결정, 오케스트레이터 임의 생략 금지)

오케스트레이터는 PMAgent가 승인한 스폰 시퀀스를 따라야 하며, 임의로 단계를 건너뛸 수 없다.
"작은 수정이니 PMAgent 생략" 판단은 오케스트레이터 권한 밖이다.

### 합의 규칙
- 도메인 해석: DomainPLAgent → 최상위 오케스트레이터 → ArchitectAgent에 전달
- 설계 결정: ArchitectAgent 주도, 결과를 최상위 오케스트레이터에 보고
- 구현 결정: 각 PL(DeveloperPLAgent, EngineerPLAgent) 자율 판단, 상위 에스컬레이션 없음

### DocsAgent 원칙
- ADR 이슈 작성 및 업데이트 담당
- README, 설계 문서 등 작업 중 발생하는 모든 문서화 수행
- PMAgent의 결정 사항을 문서로 기록하고 최신 상태 유지
- PMAgent, ArchitectAgent, DeveloperPLAgent, EngineerPLAgent, DomainPLAgent는 Write 권한이 없으므로 문서화가 필요하면 DocsAgent를 스폰해 위임한다

### EngineerPLAgent 원칙
- Docker 사용 안 함 — Linux 단일 서버 + systemd만 사용 (Write 권한 없음, 문서화는 DocsAgent 위임)
- 기능 추가 시마다 "인프라 레벨 해결 가능 여부" 먼저 검토
- 초기: 단일 Linux 서버 (systemd, 프로세스 관리)
- 목표: Kubernetes 마이그레이션

### DataEngineerAgent 원칙
- WebSocket 수집, Parquet 저장, DuckDB 쿼리 등 데이터 파이프라인 전담
- EngineerPLAgent의 인프라 결정을 데이터 계층에서 구현
- 스키마 버전 관리 및 파티션 전략 책임

### ServerEngineerAgent 원칙
- Linux 서버 설정, systemd 서비스 관리, 네트워크/보안 설정 수행
- EngineerPLAgent의 인프라 결정을 서버 레벨에서 구현
- 서버 모니터링, 로그 관리, 성능 튜닝 담당

### DeveloperPLAgent 원칙
- 기능 추가마다 Refactor 패스 강제 실행
- 패턴 일관성은 QAAgent가 최종 검증
- **테스트 계획 적극 수행**: 구현 계획서 작성 시 신규/변경 테스트 목록을 함께 산출한다
- **BackendDeveloperAgent + QAAgent 병렬 가능성 탐색 필수**: BackendDeveloperAgent가 구현을 수행하는 동안 QAAgent가 테스트를 병렬 작성할 수 있는지 검토한다. 아래 조건을 충족하면 병렬 스폰을 권장한다:
  - 구현 인터페이스(시그니처, 포트, 스키마)가 BackendDeveloperAgent 착수 전에 확정된 경우
  - 테스트 대상이 신규 파일이거나, 기존 테스트와 파일 충돌이 없는 경우
  - 병렬 수행이 불가한 경우(파일 충돌 등) 이유를 명시하고 BackendDeveloperAgent 완료 후 QAAgent 스폰
- **QAAgent 완료 후 TesterAgent 스폰**: QAAgent가 테스트 작성을 완료하면 반드시 TesterAgent를 스폰해 pytest를 실행한다

### QAAgent 원칙
- **테스트 코드 작성 전담** — pytest 실행은 TesterAgent 담당, QAAgent는 작성만 한다
- Developer 에이전트 병렬 수행 시: 확정된 인터페이스·스키마 기반으로 **테스트 코드 선작성**
- Developer 에이전트 순차 수행 시: 구현 결과 검토 후 **신규/변경 코드에 대한 UnitTest 작성**
- **"테스트 없어서 검증 불가" 불허**: 테스트가 없으면 만들어서 작성한다
- 신규 함수·클래스·포트는 무조건 UnitTest 작성, 변경 로직은 엣지 케이스 포함 테스트 추가
- 커버리지 gap 발견 시 즉시 테스트 작성 후 TesterAgent 스폰을 오케스트레이터에 요청한다

### TesterAgent 원칙
- pytest 실행만 담당 — 테스트 코드 수정·소스 코드 수정 모두 금지
- 실행 후 PASS/FAIL 구조화 보고: 실패 시 테스트명·에러유형·관련 소스 경로 포함
- FAIL 보고는 오케스트레이터의 ArchitectAgent 디버그 루프 트리거 신호다

## ADR (Architecture Decision Records)

### 필수 규칙
- **설계 결정을 내릴 때마다 ADR 이슈를 생성한다** (GitLab: `mctrader1/mctrader`, project ID: `81469985`)
- 새 세션 시작 시 기존 ADR을 먼저 확인하고, 결정된 사항을 번복하지 않는다
- ADR에 반하는 방향으로 구현할 때는 반드시 사용자 확인 후 ADR을 업데이트한다

### ADR 생성 기준
다음 중 하나라도 해당하면 ADR 이슈 생성:
- 라이브러리/프레임워크 선택 (왜 A를 택하고 B를 버렸는가)
- 아키텍처 패턴 결정 (레이어 구조, 인터페이스 설계)
- 데이터 저장/처리 방식 선택
- 인프라/배포 방식 결정
- 전략 도메인 핵심 개념 확정

### ADR 이슈 포맷
```
제목: ADR-NNN: <결정 제목>
레이블: ADR
본문:
## 상태
Accepted | Deprecated | Superseded by #NNN

## 컨텍스트
왜 이 결정이 필요했는가

## 결정
무엇을 어떻게 결정했는가

## 결과
- ✅ 장점
- ⚠️ 단점/주의사항
- TO-DO: 후속 작업

## 다이어그램
결정에 따라 아래 중 적합한 형식으로 Mermaid 다이어그램 첨부:
- 아키텍처/클래스 구조 → classDiagram
- 데이터 흐름/이벤트 순서 → sequenceDiagram
- 인프라/배포 구성 → graph LR 또는 graph TD

## 관련 파일
코드 경로
```

### 기존 ADR 목록 (GitLab Issues)
- [#1 ADR-001](https://gitlab.com/mctrader1/mctrader/-/work_items/1) — Hexagonal Architecture 채택
- [#2 ADR-002](https://gitlab.com/mctrader1/mctrader/-/work_items/2) — OrderBook Diff-only 저장
- [#3 ADR-003](https://gitlab.com/mctrader1/mctrader/-/work_items/3) — Parquet + DuckDB (Redis 미사용)
- [#4 ADR-004](https://gitlab.com/mctrader1/mctrader/-/work_items/4) — 백테스트 우선 개발
- [#5 ADR-005](https://gitlab.com/mctrader1/mctrader/-/work_items/5) — Queue Position Model
- [#6 ADR-006](https://gitlab.com/mctrader1/mctrader/-/work_items/6) — Bithumb 우선 + 멀티 거래소 추상화
- [#7 ADR-007](https://gitlab.com/mctrader1/mctrader/-/work_items/7) — 틱띠기 OrderBook Imbalance 전략
- [#8 ADR-008](https://gitlab.com/mctrader1/mctrader/-/work_items/8) — Linux + systemd 인프라
- [#9 ADR-009](https://gitlab.com/mctrader1/mctrader/-/work_items/9) — QueuePositionModel lifecycle 메서드 포트 공식화
- [#10 ADR-010](https://gitlab.com/mctrader1/mctrader/-/work_items/10) — Dashboard Web Interface (FastAPI + Jinja2 + Bootstrap 5)
- [#11 ADR-011](https://gitlab.com/mctrader1/mctrader/-/work_items/11) — 서버사이드 타임존 변환 (zoneinfo + cookie 기반 선택)
- [#12 ADR-012](https://gitlab.com/mctrader1/mctrader/-/work_items/12) — Collector 프로세스 수명주기 추상화 (collectorctl + systemd/launchd)
- [#13 ADR-013](https://gitlab.com/mctrader1/mctrader/-/work_items/13) — 백테스트 진행률 추적 패턴 (ProgressReporter 포트 + 하이브리드 진행률)
- [#15 ADR-014](https://gitlab.com/mctrader1/mctrader/-/work_items/15) — 에이전트 팀 구조 재편 (Developer 계열 분리)
- [#16 ADR-015](https://gitlab.com/mctrader1/mctrader/-/work_items/16) — 시각화 뷰 레이어 도입 (Ladder/Tape/Imbalance 아키텍처)
- [#17 ADR-016](https://gitlab.com/mctrader1/mctrader/-/work_items/17) — TesterAgent 신설 및 자동 디버그 루프 도입

## Domain Knowledge / 도메인 지식

### 시각화 스펙
- [OrderBook/Trade 시각화 스펙](docs/guides/orderbook-trade-visualization-spec.md) — L2 호가창/체결 도메인 정의, 뷰 모델 스키마, 스캘핑 시각화 3종 스펙

## Trading Domain

- 대상: 암호화폐 전용
- 전략: 스캘핑 (단기, 고빈도)
- 실행: 완전 자율
- 주요 데이터: 실시간 가격 데이터, 호가창

