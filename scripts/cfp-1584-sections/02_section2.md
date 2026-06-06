## 2. 사용자(Human) 상호작용 규약

### 2.1 blocking wait 진입 기준

다음 중 하나 이상 충족 시 Orchestrator는 **즉시 진행 중단**하고 사용자 응답 대기 상태로 전이:

- RequirementsPLAgent 통합 명세서에 "사용자 확인 필요" 체크박스 미해소 항목 존재 (Story file §5.5)
- RequirementsPLAgent 상충 조정 실패 (Domain·Analyst·Researcher 세 관점 결론 충돌, ADR 위반 혐의 등)
- ArchitectAgent (chief author)가 "기존 API의 breaking change 불가피" 보고 → ArchitectPLAgent 검수 후 사용자 ESCALATE
- DesignReviewPL ESCALATE 판정 (설계 리뷰 FIX 3회 초과)
- CodeReviewPL ESCALATE 판정 (구현 리뷰 FIX 3회 초과)
- ArchitectPLAgent가 "테스트 반복 FAIL — 근본 원인 재분석 후에도 해소 불가" 보고
- 사용자 요구사항 범위·우선순위·예산이 프롬프트에서 해석 불가

### 2.2 사용자 응답 수령 시 재스폰 대상 판정

| 응답 종류 | 재스폰 대상 | 전달할 컨텍스트 |
|-----------|------------|----------------|
| "사용자 확인 필요" 답변 | RequirementsPLAgent | 답변 내용 + 기존 Story file 경로 |
| ADR 갱신 승인 | ArchitectAgent (ADR direct write) → RequirementsPLAgent | ArchitectAgent가 ADR 업데이트 후 RequirementsPLAgent 재호출 (CFP-26 Phase 0a) |
| breaking change 승인 | ArchitectPLAgent (chief author 재스폰 의뢰) | ADR 후보 추가 지시 + Change Plan 재수립 |
| 설계 리뷰 ESCALATE 후 judgment | ArchitectPLAgent (재진입) | 사용자 지시를 Change Plan 갱신 입력으로 전달 → chief author 재스폰. 설계 리뷰 카운터 **리셋** |
| 구현 리뷰 ESCALATE 후 judgment | ArchitectPLAgent | 동일 — 구현 리뷰 카운터 리셋 |
| 테스트 반복 FAIL 판단 | ArchitectPLAgent | 사용자 지시 근본 원인 가설 + Change Plan 대폭 수정 허가 |
| 요구사항 범위·우선순위 변경 | Orchestrator 자체 | Story Issue 재분해 또는 기존 Story scope 수정 → RequirementsPLAgent 재스폰 |

> **ADR-077 §결정 1/2 cross-ref (CFP-759 Story-1, origin/main)**: "사용자 확인 필요" 답변 = clarification 강제 재조사 trigger SSOT. 위 표 §272 행 "요구사항 범위·우선순위 변경" 경로는 ADR-077 §결정 2 가 trigger SSOT cross-ref (**§272 흡수(absorb)되며 대체(replace) 아님** — "Story 재분해" invariant 의미 보존). 강제 fan-out 6 절차 = §4.4.1.

### 2.3 사용자 ESCALATE 프롬프트 표준 형식

```
⚠️ 사용자 판단 요청 (ESCALATE)

[상황]
- Story: <KEY> — {한 줄 요약}
- 현재 단계: {phase:설계-리뷰 / phase:구현-리뷰 / phase:구현-테스트 / phase:보안-테스트}
- 트리거: {설계 리뷰 3회 FIX / 구현 리뷰 3회 FIX / 테스트 반복 FAIL / ADR 충돌 / breaking change / clarification 재조사 cap 5 초과 → escalation_class: scope_redefinition_required (NOT failure / NOT abort — ADR-077 §결정 6 escape valve, recheck_counter RESET to 0, §10 FIX Ledger 무기록)}

[시도 이력]
1. Iteration 1: {수정 방향} → {결과}
2. Iteration 2: {수정 방향} → {결과}
3. ...

[남은 이슈]
- {객관적 blocking 결함 목록}

[가능한 선택지]
- (A) {선택 A — 트레이드오프 서술}
- (B) {선택 B}
- (C) 요구사항 자체 재해석 — 범위 축소 / ADR 갱신 / 포기

[Orchestrator 의견]
{선택 A 권장 등, 근거 1-2줄}

다음 행동을 지시해주세요.
```

응답 전까지 Orchestrator는 **스폰 중단**. 사용자 응답 수령 시 §2.2 표로 재진입.

### 2.4 사용자 지시 vs 내부 판단 충돌

- **사용자 지시가 항상 우선**. CLAUDE.md 규칙·ADR·본 playbook은 사용자 명시 지시에 의해 override 가능
- 단, 사용자 지시가 ADR과 충돌하면 **ADR 갱신 의사 확인** 후 진행 (암묵적 위반 금지)
- 프로젝트 고유의 **안전 제약**(consumer overlay가 도메인별 명시한 invariant·검증 규칙 등)은 사용자가 명시적으로 해제하지 않는 한 유지

---

