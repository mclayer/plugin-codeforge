---
adr_number: 14
title: Operational Risk SSOT Distribution — codeforge-design plugin owns §7.4 schema, wrapper owns matrix/decision rows
status: Adopted
category: Architecture
date: 2026-04-30
related_stories:
  - CFP-46 (parent — Operational Risk Architect 신설 + §7.4 SSOT 분산)
  - CFP-128 (amends — Docker-first §7.4 mandate 4 항목 확장)
related_files:
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md
  - docs/adr/ADR-009-wrapper-only-decomposition.md
  - docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md
  - docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md
  - docs/adr/ADR-033-docker-first-infra-engineering.md
  - docs/inter-plugin-contracts/design-output-v2.md (created in PR-E canonical / PR-F sibling)
amendments:
  - ADR-033
is_transitional: false
---

## 상태

Adopted (2026-04-30) — CFP-46 PR-A 머지 시점 채택.

## 컨텍스트

CFP-44 (wrapper CLAUDE.md SSOT 압축) + CFP-45 (codeforge-internal-docs dogfood-out) 직후, 사용자가 향후 진행할 암호화폐 트레이딩 시스템 use case 에 대한 plugin 적합성 검토 요청. Claude + Codex 협력 분석으로 H1-H19 발견. 사용자 우선순위 명시:

> "플러그인을 경량화하는건 어디까지나 모든 기능이 만족할 정도로 잘 수행되는 것을 전제로 한다. 더 복잡한 요건을 해결하기 위한 명령 증가는 피하지 않는다."

H 분류:
- 보편 (CFP-46/47 흡수): H1 latency / H4 long-running stream / H5 rate limit / H7 web E2E / H8 clock sync / H11 idempotency / H13 env isolation / H14 DR
- 도메인 특화 (CFP-48 흡수): H2 / H3 / H6 / H9 / H10 / H12 / H15
- Codex 추가 risk: H16 ADR-012 exception creep / H17 SubAgent 경계 분쟁 / H18 CONDITIONAL noise / H19 contract drift

H1 / H5 / H8 / H11 / H13 / H14 가 design lane 흡수 부분 — 본 CFP-46 대상. operational risk 가 보안 강화 (SecurityArch mandate) 도 데이터 무결성 (DataMigrationArch mandate) 도 아닌 production-readiness 자체 축이라는 Codex Round 2 권고 채택.

## 결정

1. **§7.4 운영 리스크 schema 자체** = codeforge-design plugin SSOT
   - 5 항목: DR / Cancel-on-disconnect / Clock sync (CONDITIONAL) / Rate limit / Env isolation
   - 위치: codeforge-design `templates/change-plan.md` + agent file `agents/operational-risk-architect.md`
   - Owner: 신설 OperationalRiskArchitectAgent (6번째 SubAgent)

2. **wrapper SSOT 보유 영역** = 다음 3개만 (ADR-012 §3 4번째 예외)
   - 책임 매트릭스 §7.4 / §11 idempotency 행
   - 원인 판정 decision table §7.4 / §11 idempotency 행
   - 6 SubAgent mandate 경계 매트릭스 (cross-lane scope)

3. **§11 Idempotency invariant (CONDITIONAL)** = DataMigrationArch primary, OperationalRiskArchitect consult
   - 적용 조건: 재시도 / 외부 side effect / 장기 워크플로우 / migration script
   - N/A 사유 패턴: batch-only / read-only / sync-only RPC

4. **CONDITIONAL "N/A allowed with justification" 조항** (H18 차단)
   - Change Plan §7.4 또는 §11 에 `N/A — <사유 1줄>` 명시 시 면제
   - 사유 부재 시 P0 차단 (DesignReview 책임)
   - lint regex 강제 (PR-G)

5. **design-output contract BREAKING bump** = v1 → v2 (ADR-008 룰)
   - schema 변경: §7.4 5 sub-item 추가 + §11 idempotency CONDITIONAL 추가 + 6 SubAgent 산출물 통합 표 추가
   - 양쪽 plugin 동시 bump (ADR-008) + sibling sync (ADR-010)
   - carrier ADR = 본 ADR-014

## 결과

**달성**:
- design lane 6 SubAgent 로 운영 리스크 mandate 단일 책임 배치 (H17 분쟁 차단)
- wrapper §7.4 행 추가에도 ADR-012 boundary 형해화 차단 (4번째 예외 좁게 명명, H16 차단)
- 트레이딩 / 분산 / 외부 stream 의존 production system 의 보편 invariant 자동 적용
- consumer overlay 부담 도메인 특화에만 한정

**비용**:
- design lane plugin agent 7 → 8 (PL + chief + 6 SubAgent), ArchitectPL 통합 token cost ~5-10k 증가
- wrapper plugin major bump v5 → v6, design contract v1 → v2
- 7 PR 묶음
- ADR-012 정신 유지 의무 — 향후 §7.X / §11.X 추가 시마다 짝꿍 개정 의무

**검증**:
- PR-G lint 가 §7.4 schema regex + CONDITIONAL N/A 사유 검출 강제
- PR-D agent file frontmatter 가 mandate 매트릭스와 cross-validation (수동 spot-check)
- design-output v2 sibling sync (ADR-010) — canonical/sibling diff 0
- wrapper grep test (spec §5.2) PASS

## 거부된 대안

결정은 (a) 신설 OperationalRiskArchitect — 아래 (b)~(e) 거부:

- **(b) SecurityArchitect mandate 확장** — 위협 모델링 (adversarial) 과 신뢰성 운영 (operational) 혼재 / mandate 비대 / 깊이 손실
- **(c) 5 SubAgent 분산** (DR/disconnect → SecurityArch / idempotency → DataMigrationArch / clock → TestContractArch) — 매번 책임 판단 / mandate 경계 모호 / H17 책임 공백
- **(d) 자연 확장 (ADR-012 변경 없음)** — H16 exception creep / boundary 형해화
- **(e) ADR-012 큰 개정 (§7 전체 wrapper SSOT)** — CFP-44 압축 의도 무력화
- **overlay-only 처리** — 사용자 우선순위 ("기능 완결성 > 경량화") 위반

## 해소 기준

N/A — permanent policy

## 관련 파일

- 본 ADR
- [ADR-008 Inter-plugin Contract Versioning](ADR-008-inter-plugin-contract-versioning.md)
- [ADR-009 Wrapper-only Decomposition](ADR-009-wrapper-only-decomposition.md) — ζ arc parent (5 SubAgent 구조 출처)
- [ADR-010 Inter-plugin Contract Sibling Sync](ADR-010-inter-plugin-contract-sibling-sync.md)
- [ADR-012 Wrapper CLAUDE.md SSOT Boundary](ADR-012-wrapper-claudemd-ssot-boundary.md) (§3 4번째 예외 짝꿍 개정 — PR-B)

## Amendment 1 (CFP-77 — 2026-05-04): CONDITIONAL SubAgent 추가 (LiveOps + LiveOrdering)

### 동기

mctrader Live mode Epic Phase 1 audit (Codex gpt-5.5 high) 발견 — ADR-008 D8 (kill switch policy) + D10 (OperationEvent / incident response) + ADR-002 D11 (executor/live.py order lifecycle ownership) 의 design-time 단일 ownership owner 부재. OpRiskArch 는 §7.4 설계-시점 policy 정의만 담당 — 실시간 operator 개입 흐름 + Live order lifecycle 은 별도 ownership 필요.

### 결정 6: CONDITIONAL SubAgent 도입

본 ADR-014 결정 1 (6 SubAgent) 가 6 permanent → **6 permanent + 2 CONDITIONAL** 로 확장:

- **LiveOpsDeputy** (CONDITIONAL — Live touching Story 만): operator approval + kill switch policy + incident response + OperationEvent 관련 §13 Live Operational Discipline ownership
- **LiveOrderingDeputy** (CONDITIONAL — Live touching Story 만): ADR-002 D11 order lifecycle / partial fill semantics / cancel race / rejection mapping / ledger reconcile invariant

CONDITIONAL trigger: Story 가 real funds / live exchange API / production credential / live order placement 중 하나 이상 touching. ArchitectPLAgent 가 Story 의 §13 CONDITIONAL trigger 검토 후 6 → 8 SubAgent parallel spawn 결정.

### 결정 7: Token / cost 영향

- Backtest/Paper-only Story = 6 SubAgent spawn (변경 없음, token 영향 0)
- Live touching Story = 8 SubAgent spawn (~25% token 증가, ArchitectPL 통합 token 추가)
- mctrader 기준: 4 prior Epic (MCT-12/18/25/32) 모두 Backtest/Paper — 8 SubAgent 활성 0회
- Live mode Epic (MCT-41+) 진입 후 child Story 의 ~50% 가 Live touching 추정 (engine LiveExecutor / Bithumb Live API / kill switch / ledger reconcile)

### 결정 8: agent file 신설 = follow-up CFP

본 CFP-77 = mandate 매트릭스 + ADR amendment 만 (정책 ground). agent file (`agents/live-ops-deputy.md` / `agents/live-ordering-deputy.md`) 신설 = follow-up CFP-78 (codeforge-design plugin 측 작업). agent file 부재 시 Live touching Story spawn 시 ArchitectPLAgent 가 fallback (현재 패턴 — OperationalRiskArchitectAgent + 추가 chief authoring).

### 결정 9: Sibling sync 의무 (ADR-010)

design-output-v2 contract 가 §13 추가 시 schema bump 필요 — design-output-v3 (BREAKING). 단 본 CFP-77 = matrix 정의만 → contract bump 안 함. agent file 신설 (CFP-78) 시 contract 검토.

### Cross-references

- mctrader Live Mode Epic (mctrader-hub#56)
- mclayer/plugin-codeforge#157 (LiveOpsDeputy candidate) + #158 (LiveOrderingDeputy candidate) — CFP-77 처리
- ADR-022 §결정 11 (consumer-side Sonnet decider Phase 1 trust model)
- CFP-76 (Story §13 Live Operational Discipline schema)

## Amendment 2 (CFP-378, 2026-05-11)

### 결정 1 — LiveOps/LiveOrdering reconciliation 소유 경계 (AC-2)
LiveOpsDeputyAgent = 외부 venue 진실 owner (거래소 잔고·audit trail·operator approval verdict).
LiveOrderingDeputyAgent = 내부 상태머신 수렴 owner (엔진 8-state lifecycle·partial fill·cancel race).
적용 범위: reconciliation invariant 영역만. 두 에이전트의 나머지 mandate는 Amendment 1 그대로 유지.

도형:
```
LiveOps  → 외부 venue source-of-truth owner (drift verdict authority)
                ↓ verdict
[reconciliation invariant]
                ↑ mapping
LiveOrdering → 내부 상태머신 수렴 owner (engine 8-state)
```

drift threshold 위반 시 verdict authority = LiveOps. mapping author authority = LiveOrdering. 두 SubAgent 산출물 cross-ref 의무.

### 결정 2 — §11.6 idempotency cell author rule (AC-3)
DataMigrationArchitectAgent = §11.6 cell primary author (Change Plan §11.6 본문 작성).
OperationalRiskArchitectAgent = N줄 memo input 제공자 (markdown quote `>` block, 3-5줄, §7.4.2 disconnect 짝 cross-ref 포함).
ArchitectAgent chief author가 memo와 cell 본문 통합 시 DataMigrationArch primary 우선 (충돌 시).

### 결정 3 — §7 env secret ownership 경계 (AC-4)
SecurityArchitectAgent = credential threat owner (§7.5: vault path / runtime injection / key permission scope / secret 노출 위협).
OperationalRiskArchitectAgent = environment containment owner (§7.4.5: env isolation / staging-prod 분리 / IP allowlist / network mode boundary).
두 소유권이 같은 secret에 겹칠 경우: SecurityArch가 threat 측면, OpRiskArch가 containment 측면 각각 작성 후 ArchitectAgent 통합.

NIST SP 800-190 (Container Security) + CIS Docker Benchmark 의 secrets management ↔ environment isolation 분리 control category 정합.

### Cross-references
- CFP-378 Story (mclayer/plugin-codeforge#378)
- CFP-378 Change Plan §3 / §10
- CFP-378 5 agent file 갱신 (codeforge-design plugin Phase 2 PR)
- deputy-mandate skill cell sub-cell annotation (codeforge wrapper Phase 2 PR)

## Amendment 3 (CFP-633, 2026-05-14): ProductionEvidenceDeputy boundary axis 명시

### 동기

CFP-632 (Story-1 anchor) 가 ProductionEvidenceDeputy (3rd CONDITIONAL SubAgent) 신설.
신설 SubAgent 의 mandate scope (production evidence quad owner / EPIC CLOSED gate
검증 / post-cutover wiring inspection) 가 OperationalRiskArchitectAgent §7.4 mandate
(DR / Cancel-on-disconnect / Clock sync / Rate limit / Env isolation) 와 5/7 cell
(71%) overlap 발견 — Fix-3 H17 (SubAgent mandate boundary 분쟁) 재발 risk.

### 결정 6.1: Boundary axis 명시 (CFP-632 mitigation)

OperationalRiskArchitectAgent 와 ProductionEvidenceDeputyAgent 의 책임 경계 axis:

> **policy SSOT (OperationalRiskArch §7.4 — DR / disconnect / clock / rate / env
> 의 invariant 정의) vs evidence SSOT (ProductionEvidenceDeputy production grounding
> subsection — invariant 충족 실측 명시)**

적용 범위:
- §7.4.2 Cancel-on-disconnect / §7.4.4 Rate limit = OpRiskArch primary (정책 정의),
  ProductionEvidence cross-ref (실측 evidence)
- §7.4.1 DR / §7.4.3 Clock sync / §7.4.5 Env isolation = 양 측 consult (policy +
  evidence 양 axis 동시 작성, ArchitectAgent chief author 통합)
- EPIC CLOSED gate 검증 / Post-cutover wiring inspection = ProductionEvidence
  primary (§7.4 reference 만)

### 결정 6.2: Verdict packet field 신설 (review-verdict-v4 carrier)

`findings[].owner_axis_kind: "policy" | "evidence" | "consult"` enum 신설 의무
(별도 CFP carrier — review-verdict-v4 MINOR bump). policy = SSOT 정의 axis (e.g.
OpRiskArch §7.4 invariant 정의) / evidence = production grounding axis (e.g.
ProductionEvidence 실측 명시) / consult = 양 axis 동시 작성 cell.

**의미축 분리 원칙 (ADR-72 §결정 8 ↔ 본 §결정 6.2)**: 본 `owner_axis_kind` 는
**axis 분류 영역** (policy / evidence / consult — boundary axis 의 mandate scope
구분). ADR-72 §결정 8 의 `owner_deputy_kind: "production_evidence"` 는 **SubAgent
identity 영역** (어느 SubAgent 가 owner 인가 — 8 → 9 SubAgent enum 확장). 두 field 는
disjoint semantic axis 보유 — `owner_deputy_kind` 는 누가, `owner_axis_kind` 는
어떤 책임축. 양 field 동시 carrier CFP-Z (review-verdict-v4 v4.5 → v4.6 MINOR
bump) 에서 동시 신설 의무 (single PR atomic add).

| Field | Axis | Enum value 예시 | 신설 carrier |
|---|---|---|---|
| `owner_deputy_kind` (ADR-72 §결정 8) | SubAgent identity (누가 owner) | `production_evidence` (8 → 9 SubAgent 확장) | CFP-Z review-verdict-v4 v4.6 MINOR |
| `owner_axis_kind` (본 §결정 6.2) | mandate scope axis (어떤 책임) | `policy` / `evidence` / `consult` | CFP-Z review-verdict-v4 v4.6 MINOR (동일 PR 동시 add) |

ArchitectPL dedup 시 사용 패턴 예시: `findings[N].owner_deputy_kind = "production_evidence"`
+ `findings[N].owner_axis_kind = "evidence"` = ProductionEvidenceDeputy 가 evidence
axis 측면에서 보고한 finding (vs. policy axis = OpRiskArch primary).

### 결정 6.3: Amendment 2 §결정 3 ↔ ADR-72 §결정 2 5번째 cell 3-way 충돌 처리

Amendment 2 §결정 3 (env secret ownership 경계) 는 §7.4.5 Env isolation 의 단독
owner 를 OperationalRiskArchitectAgent (containment owner) 로 정의 (SecurityArch
threat owner 와 분리). 본 Amendment 3 §결정 6.1 (적용 범위 두 번째 bullet) 는
§7.4.5 Env isolation 을 OpRiskArch + ProductionEvidence "양 측 consult" cell 로
분류. 두 결정의 ownership 정의가 외형적으로 충돌 — 본 §결정 6.3 이 3-way axis 분리로
해소:

| Axis | Owner | Scope |
|---|---|---|
| **Threat axis** (Amendment 2 §결정 3 SecurityArch owner) | SecurityArchitectAgent | §7.5 vault path / runtime injection / key permission scope / secret 노출 위협 |
| **Containment axis** (Amendment 2 §결정 3 OpRiskArch owner — policy SSOT 측면) | OperationalRiskArchitectAgent | §7.4.5 env isolation / staging-prod 분리 / IP allowlist / network mode boundary 의 정책 정의 |
| **Evidence axis** (Amendment 3 §결정 6.1 ProductionEvidence consult — evidence SSOT 측면) | ProductionEvidenceDeputyAgent | §7.4.5 env isolation 의 production 실측 grounding (env config 실측 + IP allowlist 실효 verify + network boundary 실측 evidence 명시) |

해소 원리: Amendment 2 §결정 3 는 **policy + threat 2-axis 분리** 시점 (OpRiskArch
single-owner containment policy). Amendment 3 §결정 6.1 는 **policy + evidence
2-axis 분리** 시점 (OpRiskArch policy + ProductionEvidence evidence consult).
3-axis 통합 = threat (SecurityArch) + containment policy (OpRiskArch) + containment
evidence (ProductionEvidence) — 동일 §7.4.5 cell 안 3 axis 가 disjoint mandate scope
보유. ProductionEvidence consult 는 OpRiskArch single-owner containment policy 를
대체하지 않음 — policy SSOT 정의는 OpRiskArch 단독 유지, evidence SSOT 명시만
ProductionEvidence 추가 (Amendment 1 §결정 6 CONDITIONAL SubAgent 패턴 reuse — 단독
owner mandate 와 consult mandate 양립).

ArchitectAgent chief author 통합 시 우선순위: containment policy 본문 = OpRiskArch
primary (Amendment 2 §결정 3 정합). Production cutover Story 에서 evidence subsection
= ProductionEvidence primary (Amendment 3 §결정 6.1 정합). threat 본문 = SecurityArch
§7.5 primary.

### Cross-references

- ADR-72 §결정 4 (boundary axis 1줄 명시 — 본 Amendment 양 방향 cross-ref)
- ADR-72 §결정 8 (`owner_deputy_kind` SubAgent identity field — 본 §결정 6.2 `owner_axis_kind` axis 분류 field 와 disjoint semantic axis. 양 field 동시 carrier CFP-Z review-verdict-v4 v4.5 → v4.6 MINOR bump 단일 PR atomic add 의무)
- [CFP-632 Story §5 EC-3](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/stories/CFP-632.md#%EC%97%A3%EC%A7%80-%EC%BC%80%EC%9D%B4%EC%8A%A4-edge-case-3) (Fix-3 H17 재발 risk mitigation — `### 엣지 케이스 (Edge Case 3)` heading 하위 EC-3 bullet, internal-docs main HEAD)
- ADR-014 Amendment 1 §결정 6 (CONDITIONAL SubAgent 도입 패턴 reuse)
- ADR-014 Amendment 2 §결정 1 (owner authority 분리 패턴 reuse)
- ADR-014 Amendment 2 §결정 3 충돌 처리 (env containment OpRiskArch 단독 owner — Amendment 3 의 양 측 consult 와 충돌. policy axis 단독성 영역 외 evidence axis 분리 명시 — 본 Amendment 3 §결정 6.3 3-way axis 분리로 해소)

## Amendment 4 (CFP-676, 2026-05-19): OperationalRiskArchitect → InfraOperationalArchitect rename + §7.4 primary/cross-ref shell 분류 + ProductionEvidence dual-spawn disjoint axis

> **형식 주의 (EC-5)**: 본 ADR-014 의 amendment 는 body `## Amendment N` section 방식 (frontmatter amendment_log field 부재 — frontmatter `amendments: [ADR-033]` 만). ADR-042 (frontmatter amendment_log id 방식) 와 format 상이. 본 Amendment 4 = Amendment 1/2/3 동일 body section 방식.

### 동기

CFP-1026 Epic Story-1 (W1 backbone) 이 design lane agent 구조 재편 정책 SSOT 를 단일 atomic carrier 로 확정. OperationalRiskArchitectAgent → InfraOperationalArchitectAgent rename ([ADR-042](ADR-042-agent-model-selection-policy.md) Amendment 7 CFP-676 atomic carrier) 에 따라 본 ADR-014 의 wrapper SSOT 3 영역 (책임 매트릭스 §7.4/§11 행 + 원인 판정 decision table §7.4/§11 행 + SubAgent mandate 경계 매트릭스 — 결정 2 정합) 의 매트릭스 deputy 명칭 갱신 + §7.4 primary / cross-ref shell 분류 명문화 + ProductionEvidence dual-spawn disjoint axis 명시.

본 Amendment 4 = **wrapper SSOT 3 영역 매트릭스 갱신만** ([ADR-012](ADR-012-wrapper-claudemd-ssot-boundary.md) §3 4번째 예외 — 결정 2 정합). §7.4 schema 자체 정의 (5 sub-item + Container 4 항목) = codeforge-design plugin SSOT (결정 1 정합) — 실 schema 변경은 W2 S3 codeforge-design sibling Story 영역, 본 S1 무변경.

### 결정 1 — OperationalRiskArchitect → InfraOperationalArchitect rename (mandate scope 보존)

OperationalRiskArchitectAgent → **InfraOperationalArchitectAgent** rename. mandate scope **무변경** — §7.4 (DR / Cancel-on-disconnect / Clock sync CONDITIONAL / Rate limit / Env isolation) + Container Docker 4 항목 (ADR-033 amend — restart policy / volume DR / health check / network mode boundary) 그대로 계승. rename 사유 = design lane agent 구조 재편 (mctrader debut evidence) 의 명칭 일관성 — operational risk 가 infra 운영 축 (Docker-first 컨테이너 운영 + DR + env isolation) 의 primary owner 임을 명칭에 반영. **순삭제 0** (deputy 제거 아님 — rename).

본 결정 1 의 §7.4 schema 실 정의 (5 sub + Container 4 항목 본문) = codeforge-design plugin canonical (`agents/infra-operational-architect.md` rename = W2 S3 sibling PR). 본 ADR-014 wrapper SSOT = 책임 매트릭스 row deputy 명칭 갱신만 (CLAUDE.md "Deputy mandate 매트릭스" + skills/deputy-mandate/SKILL.md — CFP-676 S1 동시 갱신).

### 결정 2 — §7.4 primary 4-sub + cross-ref shell 2-sub 분류 (evidence-driven 3-axis split)

InfraOperationalArchitect §7.4 의 6 sub 를 **primary 4-sub** (정책 값 설계 시점 결정 가능) + **cross-ref shell 2-sub** (policy 값 측정 후 결정 — evidence-driven) 로 분류:

| §7.4 sub | 분류 | InfraOperationalArchitect 책임 | 비고 |
|---|---|---|---|
| §7.4.1 DR | **primary** | backup / restore / failover policy 설계 시점 결정 | ProductionEvidence consult (실측 evidence — ADR-72 §결정 2 정합) |
| §7.4.3 Clock sync (CONDITIONAL) | **primary** | tolerance budget 설계 시점 결정 | ProductionEvidence consult (drift 실측) |
| §7.4.5 Env isolation | **primary** | staging-prod 분리 / IP allowlist / network mode boundary containment policy | SecurityArch threat axis + ProductionEvidence evidence axis 3-way (Amendment 2 §결정 3 + Amendment 3 §결정 6.3 정합 — 본 Amendment 4 무변경) |
| §7.4.6 Container Docker | **primary** | restart policy / volume DR / health check / network mode boundary (ADR-033 4 항목) | InfraEngineer (codeforge-develop, Haiku) 구현 분담 |
| §7.4.2 Cancel-on-disconnect | **cross-ref shell** | policy 값 미결정 — evidence-driven design 3-axis split | Phase 1 = 측정 대상 정의 + §8.6 IntegrationTest contract pointer / Phase 2 = 측정 / Phase 1 follow-up PR = 실측값으로 policy 결정 |
| §7.4.4 Rate limit | **cross-ref shell** | policy 값 미결정 — evidence-driven design 3-axis split | 동일 3-axis split |

**evidence-driven 3-axis split (§7.4.4 / §7.4.2)**:
- **Axis 1 (Phase 1)**: 측정 대상 정의 + §8.6 IntegrationTest contract pointer 정의 — DesignReviewPL audit 영역
- **Axis 2 (Phase 2)**: 실측 수행 — FIX 루프와 disjoint (측정 단계, 실패 분류 아님)
- **Axis 3 (Phase 1 follow-up PR)**: 실측값으로 policy 결정

**§7.4.4/§7.4.2 policy 공백 = FIX root-cause decision table 과 disjoint** (측정 대상이지 실패 원인 아님 — Story §2.2 PL 판정 정합). audit gate = DesignReviewPL 이 §8.6 cross-ref pointer **존재만 mandatory check** (policy 값 공백 자체는 PASS — pointer 누락만 FIX). 본 disjointness 명문화 = Story §5.2 AC-3 정합.

### 결정 3 — ProductionEvidenceDeputy ↔ InfraOperationalArchitect disjoint axis (dual-spawn 가능)

InfraOperationalArchitect (rename 후) 와 ProductionEvidenceDeputyAgent ([ADR-72](ADR-72-production-evidence-deputy-and-epic-cutover-gate.md) §결정 1 3번째 CONDITIONAL SubAgent) 의 책임 경계 axis 계승 (Amendment 3 §결정 6.1 boundary axis 무변경 — rename 만 반영):

> **policy SSOT (InfraOperationalArchitect §7.4 — DR / disconnect / clock / rate / env / container 의 invariant 정의) vs evidence SSOT (ProductionEvidenceDeputy production grounding subsection — invariant 충족 실측 명시)**

- InfraOperationalArchitect = **상시 운영 리스크 설계 결정** owner (§7.4 design-time policy SSOT — Backtest/Paper 포함 모든 Story 의 6 permanent SubAgent 중 1)
- ProductionEvidenceDeputy = **production cutover evidence gate** owner (production state 실측 — CONDITIONAL, Live touching OR production cutover Story 한정, ADR-72 §결정 3)

**dual-spawn 가능성 + wrapper-self-app N/A 명문화** (Epic #1026 ProductionEvidence boundary 단락 SSOT):
- **consumer production cutover Story** 에서 InfraOperationalArchitect + ProductionEvidence **dual-spawn 가능** — 영역 disjoint (design-time policy vs runtime-evidence). ADR-72 §결정 3 "SubAgent spawn both 의무" (production cutover = 9 SubAgent: 6 permanent + LiveOps + LiveOrdering + ProductionEvidence) 정합. 한쪽만 spawn 금지 (boundary axis 정합 검증 의무).
- **wrapper-self-app 시 ProductionEvidence N/A** (ADR-72 §결정 6 + [ADR-005](ADR-005-plugin-self-application-na-standardization.md) `plugin-meta-na` 정합 — codeforge dogfood Epic = production cutover 부재. CFP-954 precedent). 본 CFP-676 자체 = wrapper governance Story (code 0 + runtime behavior 0) → InfraOperationalArchitect (6 permanent 상시) 만, ProductionEvidence N/A.

Amendment 2 §결정 3 (env secret ownership: SecurityArch threat / OpRiskArch containment) + Amendment 3 §결정 6.3 (3-way axis 분리: threat / containment policy / containment evidence) = **본 Amendment 4 무변경** (rename 만 반영 — OpRiskArch → InfraOperationalArchitect, ownership axis 정의 그대로 계승). semantic regression 0 (Codex S-CFP676-ADR014-AMD4-SCOPE P1 — Amendment 3 policy/evidence disjointness 보존 invariant).

### 결정 4 — ADR-033 Docker-first 4 sub-item 보존 invariant (semantic regression 금지)

본 Amendment 4 는 `## Amended by ### CFP-128 / ADR-033` section 의 Container 관련 4 항목 (restart policy / volume DR / health check / network mode boundary) **0건 변경 invariant**. ADR-033 §결정 5 의 §7.4 OpRiskArch mandate 확장 4 항목은 InfraOperationalArchitect rename 후에도 §7.4.6 Container Docker sub (결정 2 표) 로 그대로 계승 — ProductionEvidence folding 또는 cross-ref shell 강등 0건. Amendment 4 = rename + primary/shell 분류 + dual-spawn axis 명시만, ADR-033 4 sub-item semantic 손상 0 (Codex S-CFP676-ADR014-AMD4-SCOPE P1 binding).

### 결정 5 — InfraArchitect 신설 철회 cross-ref (ADR-042 Amendment 7 SSOT)

별도 InfraArchitectAgent (AWS / K8s / multi-host topology 전담) 신설 = 철회. SSOT = ADR-042 Amendment 7 § "InfraArchitect 신설 철회 명문화". 사유 요약: Docker-first ([ADR-033](ADR-033-docker-first-infra-engineering.md)) + AWS / K8s 없음 — InfraOperationalArchitect §7.4.6 Container + InfraEngineer (codeforge-develop Haiku) 2-agent 분담 충분. 미래 AWS / K8s / multi-host topology 도입 시 carrier 재발의 trigger (미도입 결정 — ratchet 위반 아님, ADR-058 §결정 5 sunset_justification 불필요).

### 기존 정책 변경 0건 (ADR-014 본문)

본 Amendment 4 = ADR-014 결정 1~5 본문 변경 0건. 변경 = (a) 본 `## Amendment 4` body section (b) deputy 명칭 rename 반영 (OpRiskArch → InfraOperationalArchitect — wrapper SSOT 3 영역 매트릭스). §7.4 schema 자체 codeforge-design SSOT (결정 1) + wrapper SSOT 3 영역 한정 (결정 2) + §11 idempotency CONDITIONAL (결정 3) + N/A allowed 조항 (결정 4) + design-output BREAKING bump (결정 5 — 본 CFP-676 contract bump 0건, agent file = W2 S3) 모두 정책 변경 0건. ratchet 강화 방향 (rename + primary/shell 분류 명문화 — scope 명시 확장, ADR-058 §결정 5 정합) → sunset_justification 불필요.

### Cross-references

- ADR-042 Amendment 7 (CFP-676 atomic carrier — OperationalRiskArch → InfraOperationalArchitect rename model tier SSOT)
- ADR-72 §결정 1/§결정 3/§결정 6 (ProductionEvidenceDeputy ↔ InfraOperationalArchitect disjoint axis + wrapper-self-app N/A)
- ADR-72 mirror cross-ref 단락 (CFP-676 — 양 방향 cross-ref)
- ADR-014 Amendment 2 §결정 3 + Amendment 3 §결정 6.1/6.3 (env secret 3-way axis — 본 Amendment 4 무변경 계승)
- ADR-033 §결정 5 (Docker-first §7.4 4 항목 — 본 Amendment 4 보존 invariant)
- CLAUDE.md "Deputy mandate 매트릭스 (codeforge-design lane)" + skills/deputy-mandate/SKILL.md (CFP-676 S1 동시 갱신 — 6 → 5 permanent + 3 CONDITIONAL)
- CFP-676 Story §1 verbatim + Change Plan §3.1 (deputy 재편 논리)

## Amended by

### CFP-128 / ADR-033 — Docker-first Infra Engineering (2026-05-07)

[ADR-033](ADR-033-docker-first-infra-engineering.md) §결정 5 가 본 ADR-014 의 §7.4 OpRiskArch mandate 를 확장. 4 새 항목 추가:

1. **Container restart policy** — `always` / `on-failure` / `unless-stopped` / `no` 결정 + 근거. compose service 별도 명시.
2. **Volume DR** — anonymous vs named volume vs bind mount 의 data persistence 전략. backup strategy. host path leak 방지.
3. **Health check tuning** — `interval` / `timeout` / `retries` / `start_period`. service dependency 의 `condition: service_healthy` 사용.
4. **Network mode boundary** — bridge (default) / host / overlay / macvlan 결정. internal service 의 host 노출 금지.

amendment 형태: ADR-014 의 SSOT distribution 결정 자체 (codeforge-design plugin canonical / wrapper matrix sibling) 는 그대로 유효. §7.4 schema 의 5 sub (DR / Cancel-on-disconnect / Clock sync CONDITIONAL / Rate limit / Env isolation) 외에 Container 관련 4 항목 cell annotation 으로 추가. supersede 아님.

OpRiskArch 의 cell annotation update SSOT = wrapper CLAUDE.md § "Deputy mandate 매트릭스" §7.4 row (CFP-128 spec §3.2.3). codeforge-design canonical 변경 = OperationalRiskArchitectAgent.md (sibling sync PR per ADR-010, CFP-128 scope 내).

cross-ref: CFP-128 spec §3.4 / Change Plan §3.5 / Story §3.1.
