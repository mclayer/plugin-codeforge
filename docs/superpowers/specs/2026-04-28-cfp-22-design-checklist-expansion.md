---
spec_id: cfp-22
title: DesignReview checklist 확장 — Codex audit #4·#5·#6 (관측성·API 호환·SLO)
status: Approved
date: 2026-04-28
authors:
  - Orchestrator (synthesis)
  - CodexReviewAgent (#4·#5·#6 audit, GPT-5)
related_adrs:
  - ADR-001 (review unification)
  - ADR-004 (ArchitectPL + SecurityArch §"후속 조치")
related_files:
  - templates/review-checklists/design.md
  - agents/DesignReviewPLAgent.md
  - agents/CodexReviewAgent.md
  - CHANGELOG.md
  - .claude-plugin/plugin.json
---

## 0. 사용자 원문 (verbatim)

> 다음 작업 수행해 (CFP series autonomous progression — Codex audit #4·#5·#6 deferred queue, LOW risk single-file 변경)

## 1. 컨텍스트

ADR-004 §"후속 조치" + v0.11.0 sprint 회고 §2.1에서 명시한 Codex audit 후속 항목:

- **#4 관측성 (Observability)**: log·metric·trace 결정이 설계 시점에 누락 — 운영 단계에서 incident 대응 어려움
- **#5 API 호환 (API Compatibility)**: API 변경 시 backward/forward compatibility 결정 누락 — consumer 영향 미식별
- **#6 SLO (Service Level Objective)**: 가용성·지연·throughput 목표가 설계 시점에 미정의 — 성능 baseline §8.3과 별개로 운영 SLO 부재

본래 CFP-20에 묶였으나 CFP-20이 Live Progress Dashboard로 repurpose되어 본 항목 unassigned 상태. v0.11.0 sprint retro §"우선순위 2"에서 LOW risk + single-file 변경 평가됨 — `templates/review-checklists/design.md` 한 파일 + parity mirror 2 곳.

## 2. 결정 — 묶기 (single CFP)

ADR-004 §"긍정적" 결과 "shift-left … FIX 회귀 비용 감소" 논거가 #4·#5·#6에 동등하게 적용. 새 deputy 도입(SecurityArch / TestContractArch / DataMigrationArch 패턴) **불필요** — 3 항목 모두 기존 §3 도입할 설계 / §4 API 계약 / §6 리팩토링 선행 영역에 자연스럽게 통합 가능. **체크리스트 audit 항목으로만 추가** (검사 강화 — 새 §섹션 신설 안 함).

### 2.1 신규 audit 섹션 (design.md)

기존 §"§7 보안 설계 감사" 패턴 동형으로 3 신규 audit 추가:

#### §4 API 호환 감사 (Codex #5)
- API 변경 (route / schema / response code) 시 backward compatibility 결정 명시
- Breaking change 시 versioning 전략 명시 (URL prefix / Accept header / OpenAPI version)
- Deprecation timeline (sunset notice / parallel run / migration window)
- Consumer 통보 채널 (CHANGELOG / migration-guide / API docs)

#### §3·§4 관측성 감사 (Codex #4)
- 신규/변경 컴포넌트의 관측성 결정 명시 (log level·구조화 / metric 종류 / trace span)
- 핵심 비즈니스 이벤트 emit 지점 명시 (예: 결제 완료 / 인증 실패 / 외부 호출 실패)
- 민감 데이터 redact 정책 (SecurityArch §7.4와 cross-ref)
- error response의 trace ID·correlation ID 전파

#### §3 SLO 감사 (Codex #6)
- 가용성 목표 (예: 99.9%) + 측정 방법 (synthetic / 실 트래픽)
- 지연 목표 (p50·p95·p99 latency)
- Throughput 목표 (rps / 동시 connection)
- §8.3 성능 baseline (mean 10% 회귀 차단)와 별개 — SLO는 운영 목표, baseline은 회귀 감지

§7 보안 설계 / §11 데이터 마이그레이션 패턴과 다르게 — **3 audit는 별도 §섹션 author input 요구 없이 chief author가 §3·§4·§6에 통합**. 새 deputy 없음, 새 §section 없음.

### 2.2 Severity 자동 룰 추가

design.md "Severity 자동 룰" 절에 3건 P0 (선택적), 3건 P1 추가:

P0 (선택적 — 해당 영역 변경 있을 때만):
- **API breaking change에 versioning 전략 부재** → P0 강제 (`api-compatibility`)
- **외부 입력 컴포넌트에 관측성 결정 부재** → P0 강제 (`observability`) — boundary 컴포넌트만 P0, 내부 함수는 P1
- **공개 API · SLA 대상 서비스에 SLO 부재** → P0 강제 (`slo-missing`) — 내부 도구는 P1

P1 (잠재 — 모든 Story):
- **API 변경 시 deprecation timeline 미정의** → P1 (`api-compatibility`)
- **신규 컴포넌트 metric 종류 미명시** → P1 (`observability`)
- **SLO 목표 측정 방법 부재** → P1 (`slo-missing`)

### 2.3 Category enum 확장

`api-compatibility | observability | slo-missing` 3개 추가. 기존 8 (CFP-21에서 `data-migration` 추가됨) → 11 카테고리.

### 2.4 N/A 권한

각 항목별 N/A 권한 (SecurityArch §7.6 / DataMigrationArch §11.6 패턴 동형):
- API 변경 없는 Story → API 호환 N/A
- 외부 boundary 변경 없는 Story → 관측성 N/A (단 신규 외부 호출은 의무)
- 내부 도구·plugin meta Story → SLO N/A

N/A 사유 부재 시 P1 (P0 차단 아님 — 보안/마이그레이션과 다른 strict level).

## 3. Non-BREAKING 영향

기존 Change Plan template §1-§11 구조 유지. 3 audit는 검사 강화만 — 신규 §섹션 없음, deputy 추가 없음.

영향:
- `templates/review-checklists/design.md`: §"§7 보안 설계 감사" 다음 §"API 호환 감사" + §"관측성 감사" + §"SLO 감사" 3 절 추가 + Category enum + Severity 자동 룰 갱신
- `agents/DesignReviewPLAgent.md`: category_enum 3개 추가 + severity_overrides P0 3건 + P1 3건
- `agents/CodexReviewAgent.md`: lane=design prompt category enum + auto-P0 3건 추가
- `CHANGELOG.md`: v0.14.1 entry (Non-BREAKING — checklist 확장)
- `.claude-plugin/plugin.json`: 0.14.0 → 0.14.1 (patch bump)

총 5 파일.

## 4. ADR 영향

신규 ADR 없음 — checklist 확장은 SSOT 갱신 수준이라 별도 ADR 불필요. ADR-004 §"후속 조치" #4·#5·#6 closure cross-ref만.

## 5. Test Contract 후보 (§8)

본 CFP는 plugin meta paradox이라 자기 적용 안 함. §8 N/A.

invariant-check.yml 자동 검증:
- Step 6: lane=design category enum (Claude/CodexReview) ↔ design.md SSOT — 3개 신규 카테고리 4 곳 parity
- Step 8: severity overrides count (design.md ↔ DesignReviewPL severity_overrides YAML) parity

## 6. 보안 영향 (§7)

Trust boundary 변화 없음. 관측성 audit가 SecurityArch §7.4 민감 데이터 cross-ref 강화 (log redaction). 새 외부 호출 / 권한 추가 없음.

## 7. 후속

본 CFP 머지 후 v0.14.1 release. 다음 deferred:
- ADR-008 §section ownership model (BREAKING — N=6 deputy 안정화 후)
- 추가 Codex audit follow-up (필요 시 발견)

## 8. 참고

- ADR-004 §"후속 조치" Codex #4·#5·#6: [docs/adr/ADR-004-architectpl-securityarch-restructure.md](../../adr/ADR-004-architectpl-securityarch-restructure.md)
- v0.11.0 sprint 회고 §"우선순위 2": [docs/retros/2026-04-27-v0.11.0-sprint-close.md](../../retros/2026-04-27-v0.11.0-sprint-close.md)
