---
adr_number: 14
title: Operational Risk SSOT Distribution — codeforge-design plugin owns §7.4 schema, wrapper owns matrix/decision rows
status: Adopted
category: Architecture
date: 2026-04-30
related_files:
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md
  - docs/adr/ADR-009-wrapper-only-decomposition.md
  - docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md
  - docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md
  - docs/inter-plugin-contracts/design-output-v2.md
---

## 상태

Adopted (2026-04-30) — CFP-46 PR-A 머지 시점 채택.

## 컨텍스트

CFP-44 (wrapper CLAUDE.md SSOT 압축) + CFP-45 (codeforge-internal-docs dogfood-out) 직후, 사용자가 향후 진행할 암호화폐 트레이딩 시스템 use case 에 대한 plugin 적합성 검토 요청. Claude + Codex 협력 분석으로 H1-H19 발견. 사용자 우선순위 명시:

> "플러그인을 경량화하는건 어디까지나 모든 기능이 만족할 정도로 잘 수행되는 것을 전제로 한다. 더 복잡한 요건을 해결하기 위한 명령 증가는 피하지 않는다."

H 분류:
- 보편 (CFP-46/47 흡수): H1 latency / H4 long-running stream / H5 rate limit / H7 web E2E / H8 clock sync / H11 idempotency / H13 env isolation / H14 DR
- 도메인 특화 (CFP-48 흡수): H2 / H3 / H6 / H9 / H10 / H12 / H15
- Codex 추가 risk: H16 ADR-012 exception creep / H17 deputy 경계 분쟁 / H18 CONDITIONAL noise / H19 contract drift

H1 / H5 / H8 / H11 / H13 / H14 가 design lane 흡수 부분 — 본 CFP-46 대상. operational risk 가 보안 강화 (SecurityArch mandate) 도 데이터 무결성 (DataMigrationArch mandate) 도 아닌 production-readiness 자체 축이라는 Codex Round 2 권고 채택.

## 결정

1. **§7.4 운영 리스크 schema 자체** = codeforge-design plugin SSOT
   - 5 항목: DR / Cancel-on-disconnect / Clock sync (CONDITIONAL) / Rate limit / Env isolation
   - 위치: codeforge-design `templates/change-plan.md` + agent file `agents/operational-risk-architect.md`
   - Owner: 신설 OperationalRiskArchitectAgent (6번째 deputy)

2. **wrapper SSOT 보유 영역** = 다음 3개만 (ADR-012 §3 4번째 예외)
   - 책임 매트릭스 §7.4 / §11 idempotency 행
   - 원인 판정 decision table §7.4 / §11 idempotency 행
   - 6 deputy mandate 경계 매트릭스 (cross-lane scope)

3. **§11 Idempotency invariant (CONDITIONAL)** = DataMigrationArch primary, OperationalRiskArchitect consult
   - 적용 조건: 재시도 / 외부 side effect / 장기 워크플로우 / migration script
   - N/A 사유 패턴: batch-only / read-only / sync-only RPC

4. **CONDITIONAL "N/A allowed with justification" 조항** (H18 차단)
   - Change Plan §7.4 또는 §11 에 `N/A — <사유 1줄>` 명시 시 면제
   - 사유 부재 시 P0 차단 (DesignReview 책임)
   - lint regex 강제 (PR-G)

5. **design-output contract BREAKING bump** = v1 → v2 (ADR-008 룰)
   - schema 변경: §7.4 5 sub-item 추가 + §11 idempotency CONDITIONAL 추가 + 6 deputy 산출물 통합 표 추가
   - 양쪽 plugin 동시 bump (ADR-008) + sibling sync (ADR-010)
   - carrier ADR = 본 ADR-014

## 결과

**달성**:
- design lane 6 deputy 로 운영 리스크 mandate 단일 책임 배치 (H17 분쟁 차단)
- wrapper §7.4 행 추가에도 ADR-012 boundary 형해화 차단 (4번째 예외 좁게 명명, H16 차단)
- 트레이딩 / 분산 / 외부 stream 의존 production system 의 보편 invariant 자동 적용
- consumer overlay 부담 도메인 특화에만 한정

**비용**:
- design lane plugin agent 7 → 9 (PL + chief + 6 deputy), ArchitectPL 통합 token cost ~5-10k 증가
- wrapper / codeforge-design 동시 BREAKING bump (5 wrapper bump → 6, design contract v1 → v2)
- 7 PR 묶음
- ADR-012 정신 유지 의무 — 향후 §7.X / §11.X 추가 시마다 짝꿍 개정 의무

**검증**:
- PR-G lint 가 §7.4 schema regex + CONDITIONAL N/A 사유 검출 강제
- PR-D agent file frontmatter 가 mandate 매트릭스와 cross-validation (수동 spot-check)
- design-output v2 sibling sync (ADR-010) — canonical/sibling diff 0
- wrapper grep test (spec §5.2) PASS

## 거부된 대안

- **(b) SecurityArchitect mandate 확장** — 위협 모델링 (adversarial) 과 신뢰성 운영 (operational) 혼재 / mandate 비대 / 깊이 손실
- **(c) 5 deputy 분산** (DR/disconnect → SecurityArch / idempotency → DataMigrationArch / clock → TestContractArch) — 매번 책임 판단 / mandate 경계 모호 / H17 책임 공백
- **자연 확장 (ADR-012 변경 없음)** — H16 exception creep / boundary 형해화
- **ADR-012 큰 개정 (§7 전체 wrapper SSOT)** — CFP-44 압축 의도 무력화
- **overlay-only 처리** — 사용자 우선순위 ("기능 완결성 > 경량화") 위반

## 관련 파일

- 본 ADR
- [ADR-008 Inter-plugin Contract Versioning](ADR-008-inter-plugin-contract-versioning.md)
- [ADR-010 Inter-plugin Contract Sibling Sync](ADR-010-inter-plugin-contract-sibling-sync.md)
- [ADR-012 Wrapper CLAUDE.md SSOT Boundary](ADR-012-wrapper-claudemd-ssot-boundary.md) (§3 4번째 예외 짝꿍 개정 — PR-B)
