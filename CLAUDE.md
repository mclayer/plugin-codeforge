# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`mctrader` — 암호화폐 스캘핑 자동매매 프레임워크. Python 기반, 완전 자율 실행.

## Configuration

`settings.json`에 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 활성화됨.

## Development Agent Team

```
User
 └── LeaderAgent              # 요건 해석, 작업 범위 조율, 팀 합의 관리
      ├── DomainExpertAgent    # 암호화폐 트레이딩 도메인 해석 및 스펙 변환
      └── ArchitectAgent       # 설계/패턴 결정, 기술 최종 의사결정
           ├── CodeHeadAgent    # 구현 가능성 및 코드 품질 관점
           │    ├── DeveloperAgent
           │    ├── RefactorAgent
           │    └── ReviewAgent
           └── InfraHeadAgent   # 인프라 솔루션 검토 (Linux → Kubernetes)
                └── DataEngineerAgent  # 데이터 파이프라인 설계 및 구현
```

### 합의 규칙
- 설계 결정: ArchitectAgent 주도, CodeHead + InfraHead 검토
- 일반 구현: CodeHeadAgent 단독 판단 후 하위 팀 위임
- LeaderAgent가 작업 크기에 따라 합의 범위 결정

### InfraHeadAgent 원칙
- Docker 사용 안 함 — Linux 단일 서버 + systemd만 사용
- 기능 추가 시마다 "인프라 레벨 해결 가능 여부" 먼저 검토
- 초기: 단일 Linux 서버 (systemd, 프로세스 관리)
- 목표: Kubernetes 마이그레이션

### DataEngineerAgent 원칙
- WebSocket 수집, Parquet 저장, DuckDB 쿼리 등 데이터 파이프라인 전담
- InfraHeadAgent의 인프라 결정을 데이터 계층에서 구현
- 스키마 버전 관리 및 파티션 전략 책임

### CodeHeadAgent 원칙
- 기능 추가마다 Refactor 패스 강제 실행
- 패턴 일관성은 ReviewAgent가 최종 검증

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

## Trading Domain

- 대상: 암호화폐 전용
- 전략: 스캘핑 (단기, 고빈도)
- 실행: 완전 자율
- 주요 데이터: 실시간 가격 데이터, 호가창

