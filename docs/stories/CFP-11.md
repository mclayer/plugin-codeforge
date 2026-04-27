# CFP-11: [STORY] CFP-11 end-to-end 실증 — Issue Form workflow 자동 동작 첫 검증 (재시도)

- **Issue**: #41
- **Status**: phase:요구사항

## 1. 사용자 요구사항 (verbatim — story-section-1-immutable.yml로 변경 차단)

CFP-11 end-to-end 실증 — 본 Issue 자체가 test subject. Issue Form (story.yml) 제출 → story-init.yml workflow 자동 실행 → docs/stories/CFP-11.md template 자동 생성 + Phase 1 PR 자동 open이 정상 동작하는지 첫 실측한다.
scope:
1. story-init workflow 실행 성공 (yq install / next-key compute / body parse / branch create / commit / PR create / Issue body update 7 step 모두 PASS)
2. 자동 생성 docs/stories/CFP-11.md가 §1 verbatim + §2-11 placeholder 양식 준수
3. 자동 open Phase 1 PR이 type:story + phase:요구사항 label 부착, base=main, head=feat/CFP-11-<slug> 정상
4. Issue body가 docs link로 자동 갱신
5. 모든 단계 실측 후 본 Story file (§2-11)을 직접 채워넣고 Change Plan 작성, Phase 2 진행
self-application 정책의 마지막 미실증 layer — 정책(CFP-1) → 인프라(CFP-2) → 메타정합(CFP-4) → 자동화(CFP-5~10)까지 도입했지만 실제 사용자 → workflow 트리거는 첫 실행. 1인 maintainer 환경에서도 workflow가 의도대로 동작하는지 사전 검증.

## 2. 도메인 해석

*(DomainAgent 작성 예정 — placeholder)*

## 3. 관련 ADR

*(RequirementsPL 작성 예정 — placeholder)*

## 4. 관련 코드 경로

*(RequirementsPL 작성 예정 — placeholder)*

## 5. 요구사항 확장 해석

*(RequirementsAnalyst 작성 예정 — placeholder)*

## 6. 외부 지식 배경

*(Researcher 작성 예정 — placeholder)*

## 7. 설계 서사

*(Architect 작성 예정 — placeholder)*

## 8. 개발 서사

*(DeveloperPL 작성 예정 — Phase 2 PR에서)*

## 9. 품질 게이트 이력

*(Review/Test PL 작성 예정 — Phase 2 PR에서)*

## 10. FIX Ledger

| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|

*(FIX 발생 시 append)*

## 11. 회고

*(PMOAgent 작성 예정 — Story 완료 시)*
