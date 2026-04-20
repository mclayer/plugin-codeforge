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
           │    ├── ImplementerAgent
           │    ├── RefactorAgent
           │    └── ReviewAgent
           └── InfraHeadAgent   # 인프라 솔루션 검토 (Linux → Kubernetes)
```

### 합의 규칙
- 설계 결정: ArchitectAgent 주도, CodeHead + InfraHead 검토
- 일반 구현: CodeHeadAgent 단독 판단 후 하위 팀 위임
- LeaderAgent가 작업 크기에 따라 합의 범위 결정

### InfraHeadAgent 원칙
- 항상 Docker 기반으로 설계 (K8s 전환 비용 최소화)
- 기능 추가 시마다 "인프라 레벨 해결 가능 여부" 먼저 검토
- 초기: 단일 Linux 서버 (systemd, 프로세스 관리)
- 목표: Kubernetes 마이그레이션

### CodeHeadAgent 원칙
- 기능 추가마다 Refactor 패스 강제 실행
- 패턴 일관성은 ReviewAgent가 최종 검증

## Trading Domain

- 대상: 암호화폐 전용
- 전략: 스캘핑 (단기, 고빈도)
- 실행: 완전 자율
- 주요 데이터: 실시간 가격 데이터, 호가창

### Trading Agent 구성 (구현 대상)
```
TradingOrchestrator
├── DataTeam
│   ├── PriceStreamAgent
│   └── OrderBookAgent
├── AnalysisTeam
│   ├── IndicatorAgent
│   └── SignalAgent
├── RiskTeam
│   └── RiskManagerAgent
└── ExecutionTeam
    ├── OrderAgent
    └── PositionAgent
```
