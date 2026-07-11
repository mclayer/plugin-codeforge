---
name: review-responsibility
description: Design/Code/Security 리뷰 책임 매트릭스. 6 lane(RequirementsReview·DesignLane·DesignReview·CodeReview·SecurityTest·DeployReview) 체크 항목 분담 테이블 + 요구사항리뷰 외부사실 의존 체크(실 trigger=CFP-2326 / ADR-125). 요구사항리뷰·설계리뷰·구현리뷰·보안테스트·배포리뷰 lane 진입 시 Orchestrator 호출 의무.
tools: Read
---

# Design / Code / Security 리뷰 책임 매트릭스

> 참조 테이블 skill — 내용을 읽고 lane 진입 전 체크 항목 분담을 확인하세요.

## 호출 시점

요구사항리뷰 lane 진입 시 (RequirementsReviewPL spawn 전 — CFP-2326 / ADR-125), 설계리뷰 lane 진입 시 (DesignReviewPL spawn 전), 구현리뷰 lane 진입 시 (CodeReviewPL spawn 전), 보안테스트 lane 진입 시 (SecurityTestPL spawn 전), 배포리뷰 lane 진입 시 (DeployReviewPLAgent spawn 전).

## 개요

네 레인의 체크 항목이 겹치지 않도록 분담. 한쪽에서 커버된 항목은 다른 쪽에서 재검토하지 않음.

**review verdict write 책임**: PL은 `pl_recommendation`만 작성, Orchestrator가 받아 final §9 write 수행 (ADR-022 Deprecated — Sonnet decider 자동 발동 무효).

## 책임 매트릭스

| 체크 항목 | DesignLane | DesignReview | CodeReview | SecurityTest (opt-in) | RequirementsReview |
|-----------|:----------:|:------------:|:----------:|:------------:|:------------:|
| Change Plan 완결성(§1-10 섹션 존재) | — | ✅ | — | — | — |
| ADR 정합성(§3·§7 위반 여부) | — | ✅ | — | — | — |
| CodebaseMapper ↔ Refactor 균형 | — | ✅ | — | — | — |
| API 계약 일관성 (라우트·스키마·타입) | — | ✅ | — | — | — |
| §8 Test Contract 타당성 | — | ✅ | — | — | — |
| **§8.5 Stateful / restart invariant 정의** | ✅ TestContractArch | ✅ DesignReview (감사) | — | StatefulTestAgent (검증) | — |
| **§8.5 누락 / vague N/A 사유** | — | ✅ **P0 차단** | — | — | — |
| 성능 baseline §8.3 프로토콜 타당성 | — | ✅ | — | — | — |
| **§7 Trust boundary 정의** | ✅ | (감사) | — | (검증) | — |
| **§7 Threat model (STRIDE-LITE)** | ✅ | (감사) | — | — | — |
| **§7 Auth/Authz 모델 결정** | ✅ | (감사) | — | (검증) | — |
| **§7 민감 데이터 분류·흐름** | ✅ | (감사) | — | (검증) | — |
| **§7 위협↔완화 매핑** | ✅ | (감사) | — | (검증) | — |
| **§7 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — | — |
| **§11 Schema 변경 영향** | ✅ | (감사) | — | (검증) | — |
| **§11 Migration 전략** | ✅ | (감사) | — | (검증) | — |
| **§11 Rollback 경로** | ✅ | (감사) | — | (검증) | — |
| **§11 Data integrity invariant** | ✅ | (감사) | — | (검증) | — |
| **§11 Backfill / 기존 데이터 처리** | ✅ | (감사) | — | (검증) | — |
| **§11 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — | — |
| **§7.4 DR / failover 경로** | ✅ InfraOperationalArch | (감사) | — | (검증) | — |
| **§7.4 Cancel-on-disconnect** | ✅ InfraOperationalArch | (감사) | — | (검증) | — |
| **§7.4 Clock sync (CONDITIONAL)** | ✅ InfraOperationalArch | (감사·N/A 사유) | — | (검증) | — |
| **§7.4 Rate limit / quota** | ✅ InfraOperationalArch | (감사) | — | (검증) | — |
| **§7.4 Env isolation** | ✅ InfraOperationalArch | (감사) | — | (검증) | — |
| **§7.4 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — | — |
| **§11 Idempotency (CONDITIONAL)** | ✅ ModuleArch | (감사·N/A 사유) | — | — | — |
| **§11 Idempotency 누락 / N/A 사유 부재** | — | ✅ **P0 차단** | — | — | — |
| 코드 ↔ Change Plan 변경 계획 준수 | — | — | ✅ | — | — |
| 코드 스타일·네이밍·가독성 | — | — | ✅ | — | — |
| 테스트 코드 품질 (커버리지·경계·mock 경계) | — | — | ✅ | — | — |
| 런타임 오류 가능성 (null·타입·race 일반) | — | — | ✅ | — | — |
| 레이어 경계·의존성 방향 준수 | — | 부분(패턴 수준) | 주(실구현) | — | — |
| Impl Manifest §8.5 ↔ 실제 파일 일치 | — | — | ✅ | — | — |
| **4 invariants cross-validate (ADR-068 §결정 2 dual-binding)**: I-1 API contract semantic completeness / I-2 cross-module propagation completeness / I-3 unconditional vs conditional guard placement intent / I-4 wording SSOT | ✅ (I-1~I-4 설계 author emit) | ✅ (I-1~I-4 문서 감사) | ✅ (I-1~I-4 구현 cross-validate) | — | — |
| **소유레포 선언됨 + 리뷰어 근거인용 attestation** (cross-repo 책임 배치 — 기계 hard-block(고아/중복/거친파생)은 메타불변식 게이트(`responsibility-topology-check`)가 처리, 사람은 *의미정합* attestation. ADR-131 §결정4 기계/사람 판정 분리 / ADR-119 검사연극 금지. 직접 선례 = GitHub CODEOWNERS — 파일경로↔owner 구조 매칭만 강제, owner 적절성은 리뷰어 위임) | — | ✅ **merge-blocking** | ✅ **merge-blocking** | — | — |
| Injection 공격 표면 (SQL·Command·Template·NoSQL) | — | — | — | ✅ | — |
| **Trust boundary 위반 (외부 입력 검증 누락)** | (설계) | — | — | ✅ (코드 준수 검증) | — |
| Credential / secret 노출 (hardcoded·log·error) | — | — | — | ✅ (1차: Secret Scanning) | — |
| **Auth / 세션 결함 (CSRF·session fixation·JWT 무결성)** | (설계) | — | — | ✅ (코드 준수 검증) | — |
| 암호학 오용 (weak algo·nonce reuse·ECB·hardcoded key) | — | — | — | ✅ | — |
| **민감 데이터 유출 (PII·금융·헬스 데이터 로그·응답)** | (설계 분류) | — | — | ✅ (런타임 노출 검증) | — |
| 의존성 CVE 스캔 | — | — | — | ✅ (1차: Dependabot) | — |
| 정적 분석 결함 | — | — | — | ✅ (1차: CodeQL) | — |
| 설정·배포 보안 (default credential·open port·TLS) | — | — | — | ✅ | — |
| Race / TOCTOU 보안 취약 | — | — | — | ✅ | — |
| **Container image base / multi-stage build 전략** | ✅ (Refactor + InfraOperationalArch) | ✅ (감사) | (구현 준수) | — | — |
| **Dockerfile syntax + best practice** | — | — | — | ✅ (1차: hadolint) | — |
| **Container image CVE / misconfig** | — | — | — | ✅ (1차: trivy) | — |
| **Compose service definition / health check / dep order** | — | (감사) | ✅ | — | — |
| **Container network mode / port exposure** | ✅ SecurityArch | (감사) | — | ✅ (코드 준수 검증) | — |
| **Container secret / env mount 전략** | ✅ SecurityArch | (감사) | — | ✅ (런타임 노출 검증) | — |
| **§7.4 Container restart policy / volume DR** | ✅ InfraOperationalArch | (감사) | — | (검증) | — |
| **요구사항 외부사실 의존성 식별** (외부 개념·시장·표준 의존 요구사항 표면화 — CFP-2326 / ADR-125, checklist `requirements.md` §1·5) | — | — | — | — | ✅ RequirementsReviewPL |
| **요구사항 외부지식 단정 검증** (외부사실 의존 결론 다출처 검증, 검사연극 금지 — ADR-124 결정 2 / ADR-125 결정 6, checklist `requirements.md` §2-5) | — | — | — | — | ✅ RequirementsReviewPL |
| **외부 표준/규제 누락 (RFC·법규·산업표준)** | — | — | — | — | ✅ (규제 위험 동반 시 P0) |
| **AC 외부검증가능성 / 시장·벤더 단정 출처** | — | — | — | — | ✅ (외부사실 의존 시 P1) |
| **AC 분해 완결성 (RO-1 — §1 원문 ↔ §5 AC diff + tier 배정 검증)** (구별되는 각 사용자 요건이 ≥1 AC 매핑 — 미매핑=review FIX 설계 진입 차단 + user-sourced AC tier 오분류 review-gate. 요구사항리뷰 3번째 disjoint 축, external-fact/internal-invariant 와 additive disjoint — CFP-2603 / ADR-145, checklist `requirements.md` "AC 분해 완결성 게이트") | — | — | — | — | ✅ RequirementsReviewPL |

## Lane 역할 요약 (CFP-2326 / ADR-125 후 — 5 → 6 review lane, RequirementsReview 신설)

- **RequirementsReview (CFP-2326 / [ADR-125](../../archive/adr/ADR-125-requirements-review-lane.md))**: 요구사항 산출물 (Story §1-7 + 사용자 원문 + 도메인 지식) 의 **외부사실 의존성** 게이트. Phase 1 내부 sub-gate (요구사항 → 요구사항리뷰 → 설계). 외부지식 충당 3-단계 (ADR-124) 중 단계③ 주 발동 lane. 작성측 ADR-052 touchpoint #4 self-check (단계②) 와 disjoint axis (리뷰측 producer 게이트, 단계③). RequirementsReviewPL → Claude/Codex dual-peer (WebSearch/WebFetch 허용 — 외부사실 검증). 검사연극 금지 (내부근거-only 결론에 외부조사 강제 금지). **3 disjoint 축** (external-fact 외부사실 / internal-invariant runtime-failure 변종 / **AC-decomposition-completeness** RO-1 §1↔§5 diff + user AC tier 배정 review-gate — CFP-2603 / ADR-145 additive, 기존 2축 무손상). PASS → gate:requirements-review-pass → phase:설계
- **DesignLane**: 설계 결정 (trust boundary·threat model·auth model·민감 데이터 흐름). SecurityArch 산출물 → ArchitectAgent §7 반영
- **DesignReview**: 문서(Change Plan + ADR) 감사. 실구현 코드 미검토. §7 완결성 감사
- **CodeReview**: 코드(src·config·deploy·tests). 일반 품질·런타임 결함·테스트 품질 중심
- **SecurityTest**: 코드 + 인프라 + 의존성. 1차 GitHub native (Dependabot/CodeQL/Secret Scanning), 2차 Claude/Codex
- **DeployReview (CFP-1059 / [ADR-088](../../archive/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md), Phase 1 declarative)**: production runtime 측정 + cutover 사후 검증 (위 4 review lane 모두와 disjoint axis — code-level / production-level 분리). 검증 3종 = (a) smoke (양방향 호환 — ADR-089 §결정 4) / (b) 성능 비교 (production runtime ↔ pre-deploy baseline, ADR-068 I-5 dimensional empirical grounding 정합 — `[empirical-source: ...]` annotation 의무) / (c) cutover 사후 검증 (ProductionEvidenceDeputy ownership 이관 codeforge-design CONDITIONAL → codeforge-deploy-review 정식, ADR-088 §결정 3). FAIL 시 FIX dispatch (DeveloperPL / ArchitectPL / RequirementsPL — debate-protocol-v1 multi-round adversarial debate 자동 발동 의무)
- 중복 지적 발생 시 해당 레인 ReviewPL이 dedup → severity 높은 쪽 채택

> **DeployReview ↔ 기존 4 review lane disjoint axis (ADR-088 §결정 2 / Lane 진입 시 review-responsibility skill 호출 의무)**:
> - DesignReview = ADR 정합 / 설계 보장성, code-level / production-level 미접근
> - CodeReview = 구현 품질, production runtime 측정 미접근
> - SecurityTest = code-level 보안 정합, production 환경 성능 측정 미접근
> - IntegrationTest (codeforge-test) = 시나리오 단위 정합 검증, production cutover 사후 검증 미접근
> - **DeployReview (본 신설 lane)** = production 환경 성능 측정 + cutover 사후 검증, 위 4 review lane 모두와 disjoint axis

## 깊은 검증(deep-research) 차등 적용 원칙 (ADR-124)

> **SSOT = [ADR-124](../../archive/adr/ADR-124-external-knowledge-provisioning-model.md)** (외부지식 충당 3-단계 모델 + Amendment 1 차등 실구현) + [ADR-125](../../archive/adr/ADR-125-requirements-review-lane.md) (요구사항리뷰 lane 신설 — 단계③ 주 발동 lane 의 게이트·배선). 본 절은 요약 mirror 이며, 충돌 시 ADR-124/ADR-125 가 우선한다. 실 게이트 trigger·phase 라벨·lane 배선 = CFP-2326 / ADR-125 (요구사항리뷰 lane: phase:요구사항-리뷰 + gate:requirements-review-pass). 깊은 검증 차등 실구현 = **CFP-2327 / ADR-124 Amendment 1 으로 실구현 완료** (보안테스트 2차 web 단계 심화 = 다출처+adversarial+시의성 / 설계리뷰 외부 기술선택 좁은 예외 = positive∩negative 양면 / code lane web 금지 전면 보존).

리뷰 게이트의 깊은 다출처 검증 (외부지식 충당 3-단계 중 단계③) 은 **무조건 발동이 아니다.**

- **외부사실 의존 게이트**: 리뷰 결론이 외부사실 (산업 표준·벤더 동작·표준 번호·CVE 등) 에 의존하는 곳에만 깊은 검증을 적용한다.
- **검사연극(verification theater) 금지**: 결론이 내부 코드·내부 규칙·팀 암묵지식만으로 닫히는 곳에서 깊은 외부조사를 강제하면 검사연극이다. ADR-119 §결정 6 verbatim — "'조사했으므로 옳다' 단정 금지" — 가 그 SSOT (조사 = traceability + 정직성 수단이지 결론의 정당성 보증 아님).

**lane별 깊은 검증 적합도 (목표 상태 to-be, 발동 잠재력 — 매 Story 강제 아님)**:

| lane | 적합도 (잠재력) | 근거 |
|---|---|---|
| 요구사항리뷰 | 高 (주) | 요구사항 결론이 외부 개념·시장·표준 사실에 가장 자주 의존 (실 wiring = CFP-2326 / ADR-125) |
| 보안테스트 | 高 (2차 web 단계 심화 = 강화) | 취약점·CVE·공급망 = 본질적 외부지식. 실구현 = CFP-2327 — 2차 워커 web 단계 다출처(NVD+GHSA+CISA KEV)+adversarial+시의성 (1차 자동도구 대체 아님, security.md §7.1-§7.3) |
| 설계리뷰 | 부분 (외부 기술선택만) | 외부 기술선택 결론에만 의존 — 내부근거-only 설계 정합성은 비대상. 실구현 = CFP-2327 — positive-list(라이브러리·프로토콜·알고리즘·성능모델) ∩ negative-list(ADR·boundary·계약·§8·섹션) 양면 휴리스틱 (design.md "외부 기술선택 검증") |
| 구현리뷰 | 低 (미적용) | 구현 품질·런타임 결함 = 내부 코드 사실 축. web 금지 전면 보존 (설계리뷰 좁은 예외와 비대칭 — CFP-2327 / ADR-124 Amd 1 A1-3) |
| 배포리뷰 | 미적용 | 배포·배포리뷰 2 lane = ADR-121 §결정 1 **폐지 결정(deprecated)** (deprecation 진행 중) + production 경험적 측정이라 단계③ 무의존 (적합도 等級 부여 안 함) |

> 적합도가 높다는 것은 그 lane 의 결론이 외부사실에 의존할 *잠재력* 이 높다는 뜻이지, 매 Story 마다 깊은 검증이 강제 발동된다는 뜻이 아니다 (실제 발동 = 외부사실 의존 게이트가 결정). 외부사실 의존 판정 휴리스틱 (O: 팩트체크·벤더·표준·CVE / X: 팀 암묵지식 / 경계?: 시장정보·벤치마크·StackOverflow — ADR-125 결정 6 운영 판정: 단계② 우선 + 리뷰어 재량 escalation) 상세 = ADR-124 결정 6 + ADR-125 결정 6.

> **Debut-audit measurable signal**: ✅ 0개 또는 ≥2개 row = [ADR-021](../../archive/adr/ADR-021-phase-gap-measurable-signal.md) R4 (Responsibility leak) detection source.
