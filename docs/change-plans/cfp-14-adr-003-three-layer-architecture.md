---
title: ADR-003 도입 — 3 layer drift 책임 분리 (CFP-13 후속)
slug: cfp-14-adr-003-three-layer-architecture
status: draft
author: ClaudeOrchestrator (CFP-13 §11 후속)
reviewers: [user]
related_adrs: [ADR-003]
created: 2026-04-27
story: CFP-14
---

## §1. 목적

CFP-1~13이 무계획적으로 만든 3 layer (CI invariant / SessionStart 부트스트랩 / 사용자 가이드)를 ADR-003으로 사후 정합화. 향후 drift 검출 책임 추가 시 layer 결정 기준 (Q1-Q3) 명시.

### 수용 기준

- ADR-003 status=Accepted
- 3 layer 책임 매트릭스 + Q1-Q3 결정 tree
- 예외 2종 (reminder / enforcement) 명시 + 사례
- CFP-1~13 사후 매핑 9 row
- 대안 4종 기각 사유

## §2. 현재 구조 분석

### 2.1 3 layer 누적 도입 history

| CFP 범위 | Layer 도입 |
|----------|-----------|
| CFP-5 | CI invariant 첫 step (workflow parity / version / agent count) |
| CFP-6 | (validate_config.py 확장 — SessionStart 일부) |
| CFP-7~10 | CI invariant Step 4-7 (4종 추가) |
| CFP-11 | end-to-end 실증 → 3 layer 모두 필요함 입증 |
| CFP-12 | SessionStart 부트스트랩 layer 도입 (check-bootstrap.sh + bootstrap-labels.sh) + 사용자 가이드 §2g 신설 |
| CFP-13 | CI invariant Step 6 → 3 lane 확장 |

### 2.2 layer 결정 기준 부재

CFP-12에서 환경 drift (org permission)를 SessionStart에 둔 이유는 즉흥 결정 — "PR-time에 검증 못 함, manual fix 필요". 향후 새 drift 종류 도입 시 동일 즉흥 결정 반복하면 layer 선택 inconsistency 위험.

### 2.3 CFP-11이 입증한 3 layer 필요성

3 drift 발견 모두 다른 layer 책임:
- sed Korean → CI catch via test (PR #40)
- org permission → SessionStart only catch 가능
- label 부재 → 가이드 + SessionStart reminder

3 layer 모두 필요함이 사례로 입증된 시점 = ADR-003 도입 적기.

### 2.4 Mapper 변호 근거

기존 ad-hoc 진행 보존 입장: "CFP-1~13이 작동 중. ADR 없이도 진행 가능. 추상 결정은 over-engineering"

## §3. 도입할 설계

### 3.1 Mapper vs Refactor 대립 결론

채택: **Refactor 우세**.

근거:
- 3 layer는 이미 존재 — 본 ADR은 명시화만 (cost minimal)
- 향후 CFP-15+ layer 결정에 Q1-Q3 reference 즉시 활용
- 사후 정합화가 ratchet 패턴의 자연 끝점 — invariant 자동화 sprint 마무리
- Mapper의 over-engineering 우려는 ADR 1개 추가가 future debt 회피 대비 작음

### 3.2 ADR-003 §결정 구조

ADR-003 본문은 4 section:
1. **Layer 책임 매트릭스** — 3 layer × 5 차원(대상/검증 시점/회복/실패 비용/대표 산출물)
2. **Q1-Q3 결정 기준** — 새 drift 책임 도입 시 layer 선택 tree
3. **중복 회피 원칙** — 동일 drift는 1 layer만 (예외 2종 명시)
4. **CFP-1~13 사후 매핑** — 9 row reference

### 3.3 ADR-003 §대안 기각 사유

| 대안 | 기각 사유 |
|------|----------|
| A. CI invariant only | 환경 drift 검증 불가능 (CFP-11 입증) |
| B. SessionStart only | 코드 drift는 PR block 필요 (main 보호) |
| C. 가이드 only | CFP-11 입증 — 사용자 attention drop fail |
| D. 4 layer 이상 | YAGNI — 현재 3 layer로 cover, 4번째 필요 시 supersede |

### 3.4 ADR 정합성

- ADR-001/002 무관
- ADR-003 신규
- 향후 layer architecture 변경 시 본 ADR을 supersede 또는 amend

## §4. API 계약

본 Story는 ADR 도입 — 외부 API 변경 없음.

문서적 contract: 향후 CFP가 layer 결정 시 ADR-003 §2 Q1-Q3 reference 강제 (review 시 reviewer가 확인).

## §5. 변경 계획 (파일 단위)

| 파일 경로 | 변경 유형 | 담당 | 상태 |
|-----------|-----------|------|------|
| `docs/adr/ADR-003-three-layer-drift-responsibility.md` | 신규 | DocsAgent | 작성 완료 |
| `docs/stories/CFP-14.md` | 신규 | DocsAgent | 작성 완료 |
| `docs/change-plans/cfp-14-adr-003-three-layer-architecture.md` | 신규 (본 파일) | DocsAgent | 작성 중 |

## §6. 리팩토링 선행 작업

**없음**. 사후 정합화 ADR.

## §8. Test Contract

### §8.1 커버리지 계획

**N/A — 문서 산출물**.

### §8.2 경계 조건·invariant

- ADR-003 §대안에서 "Q1-Q3가 모호한 case 발생 시 본 ADR 변경 PR" 명시 — evolution path 보존
- "예외 2종"이 expand 가능 시 supersede or amendment 명시

### §8.3 Perf Baseline

**N/A**.

## §9. 분기 선택

**단일 PR**. Phase 1/2 분리 면제 (메타 ADR 도입).

본 PR base는 `main`. CFP-13 머지 완료.

## §10. ADR 대상 여부 + 기존 ADR 정합성

- **ADR-003 신규 도입** — 본 Story가 그 도입
- ADR-001/002 무관, 결정 변경 없음

CFP-1~13 retrospective formalization — 추가 ADR 불요.
