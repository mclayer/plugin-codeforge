# CFP-14: ADR-003 도입 — SSOT drift 검출·회복 책임 3 layer 책임 분리

## 1. 사용자 요구사항 (verbatim — story-section-1-immutable.yml로 변경 차단)

CFP-13 PR #45 머지 직후 사용자 (autonomy mode 인가 연장):

> "merge하고 다음 작업. 모든 권한에 승인 없이 실행해"

CFP-12 §11에 명시된 ADR-003 잠정 후보 + CFP-13 §11 회고에 재명시:

> ADR-003 (조건부): invariant 자동화 / 환경 부트스트랩 / 사용자 가이드 3 layer 책임 분리 ADR (3 layer가 모두 자리잡았으니 ADR로 정리할 시점)

본 Story는 ADR-003을 status=Accepted로 도입.

(severity_overrides parity는 3 location phrasing이 모두 달라 string equality 불가 — 별도 design 필요로 본 Story scope 외)

## 2. 도메인 해석

본 Story의 도메인은 **사후 architecture 정합화**. CFP-1~13이 무계획적으로 만든 3 layer가 사후에 일관 architecture로 응축됨을 ADR-003으로 형식화.

- 도메인 제약: 신규 ADR은 새 결정 도입 ADR이지만 본 ADR-003은 **이미 존재하는 layer를 명시화**하는 retrospective formalization
- 암묵 가정: layer 3개는 ADR로 정리될 만큼 충분히 자리잡음 (CFP-11이 3 layer 필요성 직접 입증)
- 범위 경계: ADR-003 본문 + Q1-Q3 결정 기준 + CFP-1~13 사후 매핑. 향후 CFP-14+ layer 결정에 ADR-003 reference
- 우선순위: 향후 drift 검출 추가 시 layer 결정의 principled 기반

지식 공백: 없음 (CFP-1~13 모든 사례가 input).

## 3. 관련 ADR

- **ADR-001** (워커 통합): 무관
- **ADR-002** (footer pattern): 본 ADR이 §3.2 enforcement 사례 인용
- **ADR-003** (본 Story): 신규
- 향후 ADR-004+에서 layer architecture 변경 시 본 ADR을 supersede 또는 amend

## 4. 관련 코드 경로

| 경로 | 변경 유형 | 변경 후 책임 |
|------|-----------|--------------|
| `docs/adr/ADR-003-three-layer-drift-responsibility.md` | 신규 | 3 layer 책임 분리 결정 SSOT |
| `docs/stories/CFP-14.md` | 신규 | 본 Story file |
| `docs/change-plans/cfp-14-adr-003-three-layer-architecture.md` | 신규 | 본 Story Change Plan |

## 5. 요구사항 확장 해석

### 유스케이스

1. **새 drift 검출 책임 도입 시 layer 결정**: ADR-003 §2 Q1-Q3 답해 layer 선택. 잘못된 선택으로 false positive 회피
2. **layer 간 중복 회피 점검**: ADR-003 §3 "예외 2종" 외 중복은 drift로 분류 → 통합 PR
3. **CFP-1~13 사후 정합화**: §4 매핑표가 추가될 미래 CFP가 layer 결정 시 reference

### Acceptance Criteria

- [x] ADR-003 status=Accepted
- [x] 3 layer 책임 매트릭스 (lifecycle / 회복 메커니즘 / autonomy)
- [x] Q1-Q3 결정 tree 명시
- [x] 예외 2종 (reminder / enforcement) 명시 + 사례
- [x] CFP-1~13 사후 매핑 (9 row)
- [x] 다이어그램 (decision tree)
- [x] 대안 4종 (단일 layer × 3 + layer 4개 이상) 기각 사유

### 엣지 케이스

- **Q1-Q3 답이 모호한 case 발생**: ADR-003 §"부정/트레이드오프"에서 명시 — 본 ADR 변경 PR로 case 추가하는 evolution path 인정
- **새 layer (4번째) 필요성**: D 대안에서 "현재 3 layer로 모두 cover" 명시 + "4번째 필요 시 supersede or amend" 명시

### §5.5 사용자 확인 필요 (모두 본 세션에서 확인 완료)

- [✓] 사용자 자율 실행 모드 인가 연장
- [✓] CFP-12/13 §11에 명시된 ADR-003 후보 채택
- [✓] severity_overrides parity는 별도 design 필요로 본 Story scope 외 (string equality 불가)

## 6. 외부 지술 배경

본 변경은 plugin 내부 architecture 사후 정합화. 외부 지식 보강 불필요.

> "외부 지식 보강 불필요" 판정 사유: CFP-1~13 자체가 input, ADR pattern은 plugin 내부 SSOT.

ADR 정합성: ADR-001/002 무관, 본 ADR-003 신규. 통과.

## 7. 설계 서사

Change Plan: [`docs/change-plans/cfp-14-adr-003-three-layer-architecture.md`](../change-plans/cfp-14-adr-003-three-layer-architecture.md)

### 핵심 설계

ADR-003 본문이 SSOT — 본 Story file에서는 도입 motivation + 사후 정합화 가치만 기술.

### CodebaseMapper ↔ RefactorAgent 대립 결론

- **Mapper(보수)**: "CFP-1~13이 작동 중이면 ADR 없이도 진행 가능. 추상 결정은 over-engineering"
- **Refactor(혁신)**: "3 layer가 자리잡은 시점에 사후 정합화 안 하면 향후 layer 선택 결정 ad-hoc — 작은 cost로 큰 future debt 회피"
- **채택: Refactor 우세**. ADR 1개 추가는 minimal cost. 향후 CFP-15+가 layer 선택 시 Q1-Q3 reference로 즉시 활용 가능.

## 8. 개발 서사

### §8.1-8.4 산출물

**N/A — Plugin meta ADR 도입**.

### §8.5 Impl Manifest

| 파일 경로 | 변경 유형 | 담당 | 변경 줄 수 (대략) | 상위 요건 ref |
|-----------|-----------|------|-------------------|---------------|
| `docs/adr/ADR-003-three-layer-drift-responsibility.md` | 신규 | DocsAgent | 신규 ~140 | ADR-003 §결정 |
| `docs/stories/CFP-14.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |
| `docs/change-plans/cfp-14-adr-003-three-layer-architecture.md` | 신규 | DocsAgent | 신규 | Change Plan §5 |

## 9. 품질 게이트 이력

### §9.1-9.2 설계·구현 리뷰

**N/A** — Plugin meta ADR. PR review에서 reviewer 확인.

### §9.3 구현 테스트

**N/A** — 문서 산출물.

### §9.4 보안 테스트

**N/A**.

## 10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

**비어있음 — FIX 루프 미발생**.

## 11. 회고

**발견 1 — 사후 정합화는 ratchet 패턴의 자연 끝점**: CFP-1~13이 "한 layer씩 도입" 패턴이었다면 CFP-14는 "도입된 layer 3개를 architecture로 정리". 새 functionality 추가가 아닌 architecture sense-making — invariant 자동화 sprint의 자연 마무리.

**발견 2 — ADR pattern의 가치 입증**: ADR-002(footer) → CFP-8(automation), ADR-001(워커 통합) → CFP-9/13(mirror enforce). ADR이 narrative SSOT 역할 + invariant CI가 enforcement layer 역할로 자연 협력. ADR-003도 동일 패턴 — 향후 CFP가 ADR-003을 reference로 layer 결정.

**발견 3 — severity_overrides parity는 별도 design 필요**: CFP-9/13의 string equality 패턴이 안 통함 (3 location phrasing이 자유 텍스트). canonical string 강제하면 SSOT 본문이 부자연스러워짐. LLM-based semantic equivalence는 over-engineering. 본 Story scope 외 + 별도 Story 후보 (낮은 우선순위).

**향후 작업 (별도 Story)**:
- **CFP-15 (잠정)**: severity_overrides 정합 — canonical phrasing 도입 vs LLM-based 검증 vs invariant 미적용 선택
- **확장 후보**: lane=design/security 체크리스트의 "## 체크리스트" 섹션 자체 정합 (현재는 자유 형식, invariant 미적용)
