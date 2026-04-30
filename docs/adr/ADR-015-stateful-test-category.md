---
adr_number: 15
title: Stateful / restart invariant test category — codeforge-test 2 agent split + §8.5 CONDITIONAL
status: Adopted
category: Architecture
date: 2026-04-30
related_files:
  - docs/superpowers/specs/2026-04-30-cfp-47-stateful-test-category-design.md (parent spec — internal-docs)
  - docs/adr/ADR-014-operational-risk-ssot-distribution.md (CFP-46 design-side 짝)
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md (additive minor 룰)
  - docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md (in-place sibling sync)
---

## 상태

Adopted (2026-04-30) — CFP-47 carrier. CFP-46 ADR-014 (Operational Risk SSOT) 의 검증-side 짝 정형화.

## 컨텍스트

CFP-46 (ADR-014) 가 §7.4 운영 리스크 5 sub-item + §11.6 idempotency CONDITIONAL 을 설계 단계에서 정형화 (OperationalRiskArchitectAgent 6th deputy 신설 + design-output v1→v2 BREAKING bump). 그러나 검증 단계 (codeforge-test lane) 는 여전히 functional/integration/infra/perf 4 카테고리만 보유. 결과:

- §7.4 boundary 가 코드에서 시간 흐름 + 재시작 차원에서 지켜지는가 검증할 카테고리 부재
- §11.6 idempotency invariant 의 replay 동작 검증 mechanism 부재
- 트레이딩 시스템 등 production-readiness 시스템의 long-running connection / stateful cache / background worker / process restart 시나리오가 §8 에서 invisible

사용자 의도 (2026-04-30): "기능 완결성 > 경량화. 트레이딩 시스템에서 데이터 스트림 production 안정성 + 백테스팅 + 라이브 거래 웹페이지 — production-readiness invariant 검증 카테고리 필수."

## 결정

### 결정 1 — §8.5 CONDITIONAL sub-section 신설 (codeforge-design template)

`change-plan.md` §8 Test Contract 에 `§8.5 Stateful / restart invariant tests (CONDITIONAL)` 신규 sub-section 추가. CFP-46 §11.6 dual 패턴 (CONDITIONAL + N/A 사유 강제). 적용 조건 4종 (long-running connection / stateful cache / background worker / process restart-aware) 중 1+ Y 이면 §8.5.1+ 본문 필수, 4종 모두 N + substantive reason 이면 §8.5 N/A 허용.

### 결정 2 — TestContractArchitectAgent mandate 확장 (신규 deputy 미도입)

design lane 5th deputy TestContractArchitectAgent 가 §8.5 도 author. 신규 deputy 도입 안 함 — design lane 6 deputy 유지 (CodebaseMapper / Refactor / SecurityArch / OperationalRiskArch / TestContractArch / DataMigrationArch). §8.5 는 §8 도메인 자연 확장이므로 cross-domain 신설 명분 없음.

### 결정 3 — codeforge-test 1→2 agent split

TestAgent (functional/integration/infra/perf 유지) + **StatefulTestAgent (NEW)** (long-running fixture orchestration · fork-and-kill restart helper · time-window invariant assertion · idempotency replay verification · graceful shutdown verification). TestPL 미도입 — Orchestrator 가 둘을 직접 spawn (병렬 — §8.5 적용 시), 각자 독립 verdict return. CFP-38 ζ arc test lane 단순성 결정 유지.

### 결정 4 — 양 contract additive minor in-place bump

- **design-output v2.0 → v2.1**: in-place 갱신, sections_authored 에 §8.5 entry 추가. deputies_results 변경 없음. 신규 v3 file 신설 X
- **test-verdict v1.0 → v1.1**: in-place 갱신, stateful_invariant_results optional 필드 추가. 기존 functional fields 변경 없음. 신규 v1.1 file 신설 X

ADR-008 룰 — additive minor 는 backward-compat (consumer 부재 필드 무시 가능).

### 결정 5 — §8.5 applicability 강제 lint (substantive reason)

`scripts/check-doc-section-schema.sh` 에 §8.5.0 체크표 검증 추가:
- 1+ Y 인데 §8.5.1+ 본문 부재 → FAIL
- 4 N 인데 §8.5 N/A 본문 부재 → FAIL
- 4 N + N/A 본문 vague (단순 "not applicable" / "해당 없음" / 길이 < 30자) → FAIL
- 4 fixture (passing-y-applies / passing-n-substantive / failing-y-no-section / failing-n-vague)

vague reason 차단 정규식 + 30자 minimum (CFP-46 의 10자보다 강화 — applicability decision 은 더 신중한 결정 요구).

## 결과

### 달성

- §7.4 / §11.6 의 검증-side 짝 완성 — DR/disconnect/clock/rate/env/idempotency 가 시간+재시작 차원에서 검증
- 트레이딩 시스템 production-readiness invariant universal core 보유 (CFP-48 overlay 가 chaos 확장)
- design lane 6 deputy 유지 (TestContract mandate 확장만)
- consumer 영향 zero — 모든 bump minor (additive)
- TestAgent ↔ StatefulTestAgent ownership 매트릭스 명시 (TestPL 부재 보완)
- decision table 4 row granular split (cache/queue/restart/replay 별도 path)

### 비용

- design-output / test-verdict 양 contract minor bump (in-place)
- codeforge-test 1→2 agent (CLAUDE.md self-write 표 + 신규 agent file)
- wrapper plugin.json 5.1.0 → 5.2.0 (marketplace sync 는 CFP-49 sweep 에 포함)
- §8.5 applicability 표 작성 의무 — 모든 신규 Story 의 §8 author 가 4 조건 명시 결정

### 검증

- 가상 시나리오 "WebSocket reconnect cascade test" — §8.5.1 long-running invariant 본문 + StatefulTestAgent 실행 ✓
- 가상 시나리오 "주문 idempotency replay test" — §8.5.3 + §11.6 cross-ref + StatefulTestAgent 실행 ✓
- 가상 시나리오 "내부 docs 수정 only" — §8.5.0 4 N + substantive reason → §8.5 N/A ✓
- §8.5.0 vague N/A fixture FAIL 검증 ✓

## 거부된 대안

- **(α) 단일 TestAgent mode-switch**: 1 agent 가 functional + stateful 두 mode 처리. 거부 — file responsibility 흐려짐 (codeforge plugin 자체 원칙 위반), Codex review prompt blur 지적
- **(γ) StatefulTestArchitectAgent 신설** (design lane 7th deputy): TestContractArch 와 분리. 거부 — §8 도메인 내부 cross-domain 신설 명분 부재 (CFP-46 OpRiskArch cross-domain 명분 부재). Codex 동의
- **TestPL 도입**: 거부 — CFP-38 ζ arc 단순성 유지. 향후 chaos integration / 3+ test agent 도입 시 별도 CFP
- **design-output v3 BREAKING bump**: 거부 — §7/§11 sub-numbering shift 없음 + deputies_results 변경 없음 + 신규 deputy 없음 = 순수 additive. v2.1 minor in-place 가 적합
- **chaos / fault injection 통합** (option c): 거부 — chaos infra 의존 (Toxiproxy / chaos-mesh / faketime) opinionated. CFP-48 overlay `domain_critical_invariants[]` 로 분리

## 다이어그램

```
Before (CFP-46 후, CFP-47 시점):
codeforge-design (6 deputy):
├── CodebaseMapperAgent
├── RefactorAgent
├── SecurityArchitectAgent
├── OperationalRiskArchitectAgent (CFP-46 신설)
├── TestContractArchitectAgent (§8.1-§8.4 author)  ← §8.5 미존재
└── DataMigrationArchitectAgent

codeforge-test (1 agent):
└── TestAgent (functional/integration/infra/perf)  ← stateful 미보유

Change Plan §8:
├── §8.1 커버리지
├── §8.2 invariant
├── §8.3 perf baseline
└── §8.4 N/A 권한                                    ← §8.5 미존재

After (CFP-47 완료):
codeforge-design (6 deputy 유지):
├── ...
└── TestContractArchitectAgent (§8.1-§8.5 author)   ← §8.5 mandate 확장

codeforge-test (2 agent):
├── TestAgent (functional/integration/infra/perf)
└── StatefulTestAgent (long-running + restart invariant)  ← NEW

Change Plan §8:
├── §8.1-§8.4 (기존)
└── §8.5 Stateful / restart invariant (CONDITIONAL)  ← NEW
    ├── §8.5.0 Applicability decision (4 Y/N + substantive reason)
    ├── §8.5.1 Long-running invariant tests
    ├── §8.5.2 Process restart recovery tests
    ├── §8.5.3 Idempotency replay tests (§11.6 active 시)
    └── §8.5.4 N/A 명시
```

## 관련 파일

- 본 ADR
- [CFP-47 spec](../superpowers/specs/2026-04-30-cfp-47-stateful-test-category-design.md) (internal-docs)
- [ADR-014](ADR-014-operational-risk-ssot-distribution.md) — CFP-46 design-side 짝
- [ADR-008](ADR-008-inter-plugin-contract-versioning.md) — additive minor 룰
- [ADR-010](ADR-010-inter-plugin-contract-sibling-sync.md) — in-place sibling sync
