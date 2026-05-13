---
name: review-responsibility
description: Design/Code/Security 리뷰 책임 매트릭스. 4 lane(DesignLane·DesignReview·CodeReview·SecurityTest) 체크 항목 분담 테이블. 설계리뷰·구현리뷰·보안테스트 lane 진입 시 Orchestrator 호출 의무.
tools: Read
---

# Design / Code / Security 리뷰 책임 매트릭스

> 참조 테이블 skill — 내용을 읽고 lane 진입 전 체크 항목 분담을 확인하세요.

## 호출 시점

설계리뷰 lane 진입 시 (DesignReviewPL spawn 전), 구현리뷰 lane 진입 시 (CodeReviewPL spawn 전), 보안테스트 lane 진입 시 (SecurityTestPL spawn 전).

## 개요

네 레인의 체크 항목이 겹치지 않도록 분담. 한쪽에서 커버된 항목은 다른 쪽에서 재검토하지 않음.

**review verdict write 책임**: PL은 `pl_recommendation`만 작성, Orchestrator가 받아 final §9 write 수행 (ADR-022 Deprecated — Sonnet decider 자동 발동 무효).

## 책임 매트릭스

| 체크 항목 | DesignLane | DesignReview | CodeReview | SecurityTest (opt-in) |
|-----------|:----------:|:------------:|:----------:|:------------:|
| Change Plan 완결성(§1-10 섹션 존재) | — | ✅ | — | — |
| ADR 정합성(§3·§7 위반 여부) | — | ✅ | — | — |
| CodebaseMapper ↔ Refactor 균형 | — | ✅ | — | — |
| API 계약 일관성 (라우트·스키마·타입) | — | ✅ | — | — |
| §8 Test Contract 타당성 | — | ✅ | — | — |
| **§8.5 Stateful / restart invariant 정의** | ✅ TestContractArch | ✅ DesignReview (감사) | — | StatefulTestAgent (검증) |
| **§8.5 누락 / vague N/A 사유** | — | ✅ **P0 차단** | — | — |
| 성능 baseline §8.3 프로토콜 타당성 | — | ✅ | — | — |
| **§7 Trust boundary 정의** | ✅ | (감사) | — | (검증) |
| **§7 Threat model (STRIDE-LITE)** | ✅ | (감사) | — | — |
| **§7 Auth/Authz 모델 결정** | ✅ | (감사) | — | (검증) |
| **§7 민감 데이터 분류·흐름** | ✅ | (감사) | — | (검증) |
| **§7 위협↔완화 매핑** | ✅ | (감사) | — | (검증) |
| **§7 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — |
| **§11 Schema 변경 영향** | ✅ | (감사) | — | (검증) |
| **§11 Migration 전략** | ✅ | (감사) | — | (검증) |
| **§11 Rollback 경로** | ✅ | (감사) | — | (검증) |
| **§11 Data integrity invariant** | ✅ | (감사) | — | (검증) |
| **§11 Backfill / 기존 데이터 처리** | ✅ | (감사) | — | (검증) |
| **§11 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — |
| **§7.4 DR / failover 경로** | ✅ OpRiskArch | (감사) | — | (검증) |
| **§7.4 Cancel-on-disconnect** | ✅ OpRiskArch | (감사) | — | (검증) |
| **§7.4 Clock sync (CONDITIONAL)** | ✅ OpRiskArch | (감사·N/A 사유) | — | (검증) |
| **§7.4 Rate limit / quota** | ✅ OpRiskArch | (감사) | — | (검증) |
| **§7.4 Env isolation** | ✅ OpRiskArch | (감사) | — | (검증) |
| **§7.4 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — |
| **§11 Idempotency (CONDITIONAL)** | ✅ DataMigrationArch | (감사·N/A 사유) | — | — |
| **§11 Idempotency 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — |
| 코드 ↔ Change Plan 변경 계획 준수 | — | — | ✅ | — |
| 코드 스타일·네이밍·가독성 | — | — | ✅ | — |
| 테스트 코드 품질 (커버리지·경계·mock 경계) | — | — | ✅ | — |
| 런타임 오류 가능성 (null·타입·race 일반) | — | — | ✅ | — |
| 레이어 경계·의존성 방향 준수 | — | 부분(패턴 수준) | 주(실구현) | — |
| Impl Manifest §8.5 ↔ 실제 파일 일치 | — | — | ✅ | — |
| **4 invariants cross-validate (ADR-068 §결정 2 dual-binding)**: I-1 API contract semantic completeness / I-2 cross-module propagation completeness / I-3 unconditional vs conditional guard placement intent / I-4 wording SSOT | ✅ (I-1~I-4 설계 author emit) | ✅ (I-1~I-4 문서 감사) | ✅ (I-1~I-4 구현 cross-validate) | — |
| Injection 공격 표면 (SQL·Command·Template·NoSQL) | — | — | — | ✅ |
| **Trust boundary 위반 (외부 입력 검증 누락)** | (설계) | — | — | ✅ (코드 준수 검증) |
| Credential / secret 노출 (hardcoded·log·error) | — | — | — | ✅ (1차: Secret Scanning) |
| **Auth / 세션 결함 (CSRF·session fixation·JWT 무결성)** | (설계) | — | — | ✅ (코드 준수 검증) |
| 암호학 오용 (weak algo·nonce reuse·ECB·hardcoded key) | — | — | — | ✅ |
| **민감 데이터 유출 (PII·금융·헬스 데이터 로그·응답)** | (설계 분류) | — | — | ✅ (런타임 노출 검증) |
| 의존성 CVE 스캔 | — | — | — | ✅ (1차: Dependabot) |
| 정적 분석 결함 | — | — | — | ✅ (1차: CodeQL) |
| 설정·배포 보안 (default credential·open port·TLS) | — | — | — | ✅ |
| Race / TOCTOU 보안 취약 | — | — | — | ✅ |
| **Container image base / multi-stage build 전략** | ✅ (Refactor + OpRiskArch) | ✅ (감사) | (구현 준수) | — |
| **Dockerfile syntax + best practice** | — | — | — | ✅ (1차: hadolint) |
| **Container image CVE / misconfig** | — | — | — | ✅ (1차: trivy) |
| **Compose service definition / health check / dep order** | — | (감사) | ✅ | — |
| **Container network mode / port exposure** | ✅ SecurityArch | (감사) | — | ✅ (코드 준수 검증) |
| **Container secret / env mount 전략** | ✅ SecurityArch | (감사) | — | ✅ (런타임 노출 검증) |
| **§7.4 Container restart policy / volume DR** | ✅ OpRiskArch | (감사) | — | (검증) |

## Lane 역할 요약

- **DesignLane**: 설계 결정 (trust boundary·threat model·auth model·민감 데이터 흐름). SecurityArch 산출물 → ArchitectAgent §7 반영
- **DesignReview**: 문서(Change Plan + ADR) 감사. 실구현 코드 미검토. §7 완결성 감사
- **CodeReview**: 코드(src·config·deploy·tests). 일반 품질·런타임 결함·테스트 품질 중심
- **SecurityTest**: 코드 + 인프라 + 의존성. 1차 GitHub native (Dependabot/CodeQL/Secret Scanning), 2차 Claude/Codex
- 중복 지적 발생 시 해당 레인 ReviewPL이 dedup → severity 높은 쪽 채택

> **Debut-audit measurable signal**: ✅ 0개 또는 ≥2개 row = [ADR-021](../../docs/adr/ADR-021-phase-gap-measurable-signal.md) R4 (Responsibility leak) detection source.
