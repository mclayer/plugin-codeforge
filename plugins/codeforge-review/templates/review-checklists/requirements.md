# Requirements Review 체크리스트 (lane=requirements-review)

RequirementsReviewPLAgent가 ClaudeReviewAgent / CodexReviewAgent에 packet으로 주입하는 요구사항 리뷰 체크리스트. 두 워커가 **공통 입력**으로 사용. SSOT 분리는 [ADR-001](https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-001-review-agent-unification.md) 결정.

CFP-2326 / [ADR-125](https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-125-requirements-review-lane.md) 신설 (10번째 lane). 외부지식 충당 3-단계 ([ADR-124](https://github.com/mclayer/plugin-codeforge/blob/main/archive/adr/ADR-124-external-knowledge-provisioning-model.md)) 중 **단계③ (깊은 다출처 검증) 의 주 발동 lane**. 본 체크리스트는 요구사항 결론의 **외부사실 의존성** 을 설계 진입 전 독립 검증한다 (작성측 ADR-052 touchpoint #4 self-check (단계②) 와 disjoint axis — ADR-125 결정 4).

## 리뷰 대상 (scope_globs)

- `docs/stories/<KEY>.md` §1-§6 (요구사항 산출물 — use cases · AC · edge case · 암묵 가정)
- `docs/stories/<KEY>.md` §1 본문 (사용자 원문)
- `docs/domain-knowledge/*.md` (DomainAgent 도메인 렌즈 해석)
- `docs/stories/<KEY>.md` §3 관련 ADR (정합성 교차 입력)

## Category enum (출력 분류)

`external-standard-missing | prior-art-gap | ac-external-verifiability | market-vendor-claim-unsourced | external-fact-dependency | requirements-completeness | section-missing | ac-decomposition-completeness`

## Severity 자동 룰

- **외부사실 의존 결론에 출처/검증 부재** → P1 강제 (`external-fact-dependency`) — ADR-124 결정 2 외부사실 의존 게이트
- **외부 규제·표준(법규·RFC) 명백한 누락** → 사안별 (`external-standard-missing`) — 규제 미준수·법적 위험 동반 시 P0, 그 외 P1
- **AC 가 외부검증 불가능한데 외부사실 의존** → P1 (`ac-external-verifiability`)
- **시장·벤더 사실 단정에 출처 부재** → P1 (`market-vendor-claim-unsourced`) — 경계(?) 준-외부 출처는 ADR-125 결정 6 운영 판정 (단계② 우선 + 리뷰어 재량 escalation)
- **요구사항 명세 핵심 섹션 누락** (§1 목적 / §2 use case / AC) → P0 강제 (`section-missing`)
- **도메인 선행사례 조사 부재** (외부사실 의존 요구사항인데 established practice 미조사) → P1 (`prior-art-gap`)
- **미매핑 사용자 요건** (§1 원문 ↔ §5 AC diff 결과 unmapped) → P1 강제 (`ac-decomposition-completeness`) — review FIX, 설계 진입 차단 (RO-1, CFP-2603 / ADR-145 AC-1b 완결성)
- **AC tier 오분류** (user-sourced AC 를 advisory/declared 로 부당 강등 = fail-closed 강제 약화) → P1 (`ac-decomposition-completeness`) — RO-1 tier 배정 review-gate (Risk5)

### 검사연극 금지 (필수 — finding 발의 차단 룰)

- **내부근거-only 결론에 외부조사 강제 금지**: 결론이 내부 코드·내부 규칙·팀 암묵지식만으로 닫히는 곳에서 깊은 외부조사를 강제하는 finding 은 발의 금지. ADR-119 §결정 6 "'조사했으므로 옳다' 단정 금지" SSOT. 조사 = traceability + 정직성 수단이지 결론의 정당성 보증 아님.
- **매 Story 강제 발동 아님** (declarative-only): ADR-124 결정 3 적합도 표 (요구사항리뷰 = 高/주) 는 *발동 잠재력* 이지 매 Story 강제 발동이 아니다. 실제 발동 = 외부사실 의존 게이트가 결정.

## 체크리스트 (5축)

### 1. 외부 표준/규제 의존성 (`external-standard-missing`)

- 요구사항이 산업 표준·RFC·법규·규제에 닿는 지점이 식별되었는가
- 닿는 곳에서 해당 표준(번호·조항)이 인용·식별되었는가
- 규제 미준수 위험 (법적·컴플라이언스) 이 있으면 명시되었는가 → 위험 동반 시 P0

### 2. 도메인 선행사례 조사 (`prior-art-gap`)

- 동종 문제의 외부 선행사례·established practice 가 조사되었는가 (외부사실 의존 요구사항 한정)
- DomainAgent 도메인 지식이 외부 선행사례를 반영했는가
- 선행사례 부재로 reinvent 위험이 있는 결정이 표면화되었는가

### 3. AC 의 외부검증가능성 (`ac-external-verifiability`)

- Acceptance Criteria 가 외부사실 (벤더 동작·표준 수치·외부 API 응답 등) 에 의존하는가
- 의존하는 AC 의 외부사실이 외부검증 가능한가 (검증 경로·출처 명시)
- 외부검증 불가능한데 외부사실에 의존하는 AC → P1 (구현·테스트 단계에서 가정 붕괴 위험)

### 4. 시장·벤더 사실 단정의 출처 (`market-vendor-claim-unsourced`)

- 시장정보·벤더 동작·벤치마크 단정에 출처가 병기되었는가
- 출처 없는 단정이 요구사항 결정의 load-bearing 근거인가 (load-bearing 시 P1)
- 경계(?) 준-외부 출처 (시장정보·벤치마크·StackOverflow 등): ADR-125 결정 6 운영 판정 — 단계② (작성측 얕은 자가 조사) 우선. 단계③ 강제 발동 대상 아님. 단, 외부사실 의존 정도가 높다고 판단 시 리뷰어 재량 escalation 가능.

### 5. 외부사실 의존 판정 휴리스틱 적용 (`external-fact-dependency`, ADR-124 결정 6)

결론별 외부사실 의존 O/X/경계(?) 를 판정한다:

| 판정 | 예시 | 처리 |
|---|---|---|
| 의존 O | 팩트체크 / 벤더 동작 / 표준(RFC 등) / CVE·취약점 사실 | 깊은 검증 적용 — 출처/검증 부재 시 P1 |
| 의존 X | 팀 암묵지식 / 내부 코드·규칙 사실 | 깊은 외부조사 미적용 (검사연극 차단 — finding 발의 금지) |
| 경계 (?) | 시장정보 / 벤치마크 / StackOverflow 등 준-외부 출처 | 단계② 우선 (ADR-125 결정 6 운영 판정) + 리뷰어 재량 escalation |

- **abstention escape 정합**: 출처 확보 불가 시 ADR-119 §결정 3.2 "확인 불가/추정" 명시 후 진행 (데드락 회피). 출처 부재 자체보다 "출처 부재인데 확정 단정" 이 finding 대상.

## AC 분해 완결성 게이트 (RO-1 — 요구사항리뷰 3번째 disjoint 축, CFP-2603 / ADR-145)

> **additive disjoint 축** — 위 외부사실 의존 축 (체크리스트 5축) · runtime-failure internal-invariant 축 (`requirements-runtime-failure.md` 변종) 과 **disjoint 공존** (기존 2축 무손상·무재정의). 본 축은 외부조사를 요구하지 않는 **구조적 §1↔§5 diff** 이므로 위 검사연극 금지 룰 (내부근거-only 결론에 외부조사 강제 금지) 과 무충돌 — 대조 대상이 Story 내부 (§1 원문 ↔ §5 AC) 라 web 검증 미발동.

첫 hop (사용자 산문 → AC 민팅) 은 대조할 요건 인벤토리가 없어 기계 fail-closed 불가하다 (ADR-145 Hop0 / AC-1b `declared` tier). 요구사항리뷰 lane 이 이 hop 을 **human/review-verified obligation** 으로 방어한다.

### 의무 (non-skippable)

- **§1 verbatim 사용자 원문 ↔ §5 AC 목록 diff**: "구별되는 각 사용자 요건이 ≥1 AC 에 매핑됨" (AC-1b 완결성) 을 대조 검증한다.
- **미매핑 사용자 요건 발견 = review FIX** (`ac-decomposition-completeness`) — 설계 진입 차단. 사용자 원 요건이 애초에 AC 로 민팅되지 않으면 AC↔§8↔실파일 사슬이 전부 green 이어도 요건이 drop 되므로 (사용자 원 "5분/1시간 compactor" 사례가 정확히 이 hop 에 착지), 이 첫 hop 을 review 로 봉인한다.

### tier 배정 검증 (Risk5 — non-skippable)

- 각 AC 의 `tier` (normative / declared / advisory) 배정이 타당한지 검증한다. **user-sourced AC 를 advisory / declared 로 오분류하면 fail-closed 강제가 약화**되므로, RO-1 이 tier 배정 자체를 review-gate 한다.
- user 요건에서 유래한 AC 가 부당하게 advisory 로 강등된 정황 = review FIX (tier 오분류 = 강제 약화 = tampering).

### 성격 (기계 게이트 아님 — hollow-gate 금지)

- 대조 대상 (§1 산문) 이 비정형이라 기계 강제 불가. 게이트가 AC-1b 를 fail-closed 로 강제하는 **척하지 않는다** (ADR-145 §결정 1(b) 천장 정직 공개 — user→AC 분해완결성 미강제).
- defense-in-depth 3층 중 (a): (a) 본 RO-1 §1↔§5 diff + (b) AC-10 advisory 반복주장 신호 + (c) ADR-052 divergence (Codex proactive).

## 다음 게이트 (PASS 시)

- Orchestrator post-Sonnet이 `gate:requirements-review-pass` 라벨 부착
- phase:요구사항-리뷰 → **phase:설계** 전환 → 설계 lane (ArchitectPLAgent) 스폰
- Story file §9 "요구사항 리뷰 Iteration N" 누적

## Consumer overlay 확장

Consumer는 `.claude/_overlay/templates/review-checklists/requirements.md`에 도메인 특화 체크 항목을 추가할 수 있다. SessionStart hook이 base + overlay merge.
