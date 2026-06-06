## 4. 병렬 스폰 판단

### 4.1 병렬 가능 조건 (AND)

1. **경로 분리**: 쓰기 대상 파일 경로가 겹치지 않음 (path-scoped 권한으로 보장)
2. **입력 독립**: 한쪽 산출물이 다른 쪽 입력이 아님
3. **완료 대기 가능**: 모든 병렬 에이전트 완료 후 종합 판단 가능

### 4.1.1 결정 원칙 mandate — parallel default + sequential 강제 3 사유 (ADR-064)

[ADR-064](../docs/adr/ADR-064-decision-principle-mandate.md) §결정 4 가 §4.1 의 normative 강화 — multi-task spawn default 는 **parallel** (단일 메시지 다중 Agent tool call). sequential 선택은 다음 3 사유 중 1 종 명시 의무. 3 사유 모두 부재 = default parallel.

| Sequential 강제 사유 | 운영 사례 |
|---|---|
| **state dependency** | task N+1 이 task N 출력 (Story file section / ADR 번호 / 합의 결과) 입력 의존 — 예: ArchitectAgent §3 ADR 결정 → §7 설계 서사 |
| **shared resource** | 동일 file write / 동일 GitHub label 변경 / 동일 branch commit / ADR 번호 sequential append — 예: ADR-RESERVATION row append |
| **ordering invariant** | 출력 ordering 자체가 의미 — 예: FIX Ledger row append (시간 순), commit chain |

본 룰은 ADR-039 §결정 7 `policy_violation_subdecision` 결정 영역 확장 — sequential 선택 시 spawn prompt 또는 commit message 에 사유 1 종 명시. derived default 가 부재한 영역 = AskUserQuestion 발화 의무 (ADR-064 §결정 3 룰 5 정합).

#### 결정 제안 시점 self-check checklist

Orchestrator 가 결정 제안 (brainstorm Phase 1 / writing-plans / Issue Form 제출 / lane spawn prompt 작성) 직전 다음 5 항목 self-check:

1. **forbid-list 어휘 회피** — 결정 menu 후보 텍스트에 ADR-064 §결정 2 dictionary 8 어휘 등장 여부 확인 (dictionary 본문 / 외부 인용 영역 제외). 등장 시 대체 어휘로 reformulation.
2. **Derived default 도출** — 컨텍스트 (사용자 명시 + memory + Story file + ADR 인용) 로 합리적 default 도출 가능 시 `AskUserQuestion` 생략, derived default 직접 declare.
3. **식별자 사전 요약** — ADR / CFP / 코드 식별자 인용 시 핵심 결정 1 문장 요약 사전 제시.
4. **옵션 수 제한** — 후보가 2+ 이면 권장 1 + 대안 1 (최대 2). 3+ 후보 = brainstorm Phase 0 영역으로 격상.
5. **CFP scope unitary 확인** — 한 CFP 안 "경량 → full" 단계 분기 회피. 별개 CFP 분리 채택.

### 4.2 표준 병렬 패턴

| 패턴 | 구성 | 조건 충족 |
|------|------|----------|
| **요구사항 레인** | DomainAgent ∥ Analyst ∥ Researcher | 셋 모두 공통 입력만 수신, 타 산출물 미참조 → 입력 독립. PL이 통합 단계에서 dedup·상충 조정 |
| **설계 레인** | CodebaseMapper ∥ Refactor ∥ SecurityArchitect ∥ TestContractArch ∥ DataMigrationArchitect | 다섯 다 원 소스(코드·ADR·Change Plan 초안) 직접 독해, 타 산출물 미참조 → 입력 독립. ArchitectAgent (chief author)가 교차 검토 → ArchitectPLAgent 검수 |
| **설계 리뷰** | ClaudeReviewAgent ∥ CodexReviewAgent (lane=design packet) | 읽기 전용, 정규화 스키마 동일 |
| **구현 리뷰** | ClaudeReviewAgent ∥ CodexReviewAgent (lane=code packet) | 동일 |
| **보안 테스트** | ClaudeReviewAgent ∥ CodexReviewAgent (lane=security packet) | 동일. 워커는 lane-agnostic, PL이 packet으로 도메인 분기 |
| **구현** | DevPL(`role: dev` roster 병렬) + QADev(tests/**) | 쓰기 경로 분리 — roster 전체 의존성 없는 한 병렬 |

### 4.3 병렬 일부 실패 시

- **모두 완료 대기**가 원칙 — iteration 낭비 방지
- 예외: ClaudeReview가 [P0]를 즉시 내면 Codex 대기 없이 FIX 진입 가능 — 단 Codex 완료 후 결과 병합해 Story file §9에 기록

### 4.4 Clarification 재조사 채널 (요구사항·설계 레인 공통)

#### 4.4.0 4-layer counter disjoint 표 (ADR-077 §결정 5)

4개의 별개 반복 카운터가 codeforge에 병존한다. 카운터 간 합산·cap 공유는 cross-pollinate 금지 normative (ADR-077 §결정 5 + ADR-067 cross-lane 합산 금지 정합).

| layer | 채널 | 카운터/한도 | owner | §10 합산 |
|---|---|---|---|---|
| 1. scope 정교화 | 재조사 카운터 | `recheck_counter_cap = 5` (ADR-077 §결정 4, ESCALATE 초과) | RequirementsPL (§9.0) | 금지 |
| 2. 품질 게이트 | §10 FIX Ledger | lane별 max 3 (ADR-067) | Orchestrator monopoly (fix-event-v1) | — (본 채널) |
| 3. PL재량 재스폰 | §4.4.2 2회 한도 | 동일 에이전트 2회 (초과 시 ESCALATE §2.3) | PL (RequirementsPL/ArchitectPL) | 금지 |
| 4. adversarial 합의 | debate round counter | min 3 / max 5 (ADR-059 debate-protocol-v1) | DesignReviewPL | 금지 |

본 표 = ADR-077 §결과 절 4-layer cross-declare 의 2번째 cross-declare 위치 (1번째 = ADR-077 §결정 5/§결과 절, 3번째 = requirements-output contract schema = Story-4 carrier).

#### 4.4.1 사용자 clarification 답변 수령 시 강제 fan-out 6 절차 (ADR-077 §결정 1/2/7/10)

사용자가 "사용자 확인 필요" 답변을 제공한 시점 = dirty 이벤트. 다음 절차를 **무조건 실행** (PL 재량 분기 · "변화없음 → 통합만" skip 금지):

1. clarification 답변 수령 = dirty 이벤트 (**value-equality skip 비차용 invariant** — 답변 내용이 이전과 의미상 동치여도 skip 금지, ADR-077 §결정 1).
2. envelope coalesce: 답변 burst → debounce (P-1) → max-wait ceiling 도달 시 강제 → 단일 fan-out (coalesce 단위 1). **정량값 = ADR-077 §결정 4 정량 표 cross-ref (본문 평문 박제 금지 — TBD marker 정합, ADR-068 Amendment 1 I-5)**.
3. 6 sub-agent **parallel always-executable** fan-out (ADR-077 §결정 10 / ADR-064 §결정 4 parallel default — sequential 3 사유 [state dependency / shared resource / ordering invariant] 부재 시 default parallel): DomainAgent(§2) + RequirementsAnalyst(§5) + Researcher(§6) + FeasibilityAgent(§4.2) + ContinuityAgent(§4.3) + ChangeImpactAgent(§4.1).
4. **조건부 PMO 가산**: 답변 영향이 Epic/Story 구조 도달 시 PMOAgent 합류 (재분해). contrapositive invariant "PMO 합류 미발동 = Epic 구조 무변경" (ADR-077 §결정 2 P-5 closed enum SSOT). ADR-045 retro trigger와 origin disjoint.
5. **정보 무결성 invariant (ADR-077 §결정 7 — SecurityArch P1)**: 재조사 sub-agent는 `prior_output_ref` 의 fact-check marker 4종 (`[verified]` / `[hypothesis]` / `[fact-check-pending]` / `[user-input]`) + reverse-explicit `[verification-out-of-scope: <사유>]` 를 **verbatim 보존**. `[hypothesis]` / `[fact-check-pending]` → `[verified]` **무검증 승격 금지** (ADR-052 Amendment 3 무손상). marker 부재 = 암묵 `[hypothesis]` default 유지.
6. PL 재종합 (ADR-056 합성 순서: §5 Analyst → §2 Domain → §6 Researcher → PL) + 재조사 카운터 §9.0 기록 (§10 FIX Ledger 합산 금지 — §4.4.0 layer 1).

#### 4.4.2 PL 재량 재스폰 절차 (layer 3 — §4.4.1 clarification-driven fan-out과 trigger origin disjoint)

서브 에이전트는 one-shot 실행이라 PL↔서브 continuous dialog 불가. PL(RequirementsPL 또는 ArchitectPLAgent)이 병렬 결과 통합 중 추가 질의가 필요하면:

1. PL이 Orchestrator에 재스폰 요청 페이로드 전달:
   - 대상 에이전트명
   - 이전 본인 출력 pointer (Story file 참조 또는 메모리 slice)
   - clarification context (무엇을 추가로 묻는가, 왜)
   - 범위 제한 (전면 재분석 vs 특정 섹션 보강)
2. Orchestrator가 해당 에이전트를 **신규 스폰** — frontmatter에 `rspawn_reason` + `prior_output_ref` 기록
3. 에이전트가 이전 출력을 참조 + 추가 범위만 분석해 보강 산출물 반환
4. PL이 재수령 후 통합 단계 반복
5. 재스폰 이력은 **Story file §9.0 "Clarification 재스폰 이력"** 에 append (RequirementsPL 직접 §9.0 append — codeforge-requirements self-write). §10 FIX Ledger와 분리 — 재스폰은 게이트 실패 아니며 GitHub `fix:*` 라벨 미추가

**무제한 재스폰 금지** — 동일 에이전트 2회 재스폰 이후에도 미해소면 사용자 ESCALATE로 전환 (§2.3).

---

