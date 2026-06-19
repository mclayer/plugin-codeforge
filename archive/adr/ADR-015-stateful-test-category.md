---
adr_number: 15
title: Stateful / restart invariant test category — codeforge-test 2 agent split + §8.5 CONDITIONAL
status: Adopted
category: Architecture
date: 2026-04-30
related_stories:
  - CFP-47 (parent — Stateful / restart invariant test category 신설)
  - CFP-2349 (Amendment 1 — §8.5.1 long-running invariant tests 의 soak 지속 시간을 accumulation/lifetime-class 리스크에 대해 '발현조건 기반(manifestation-derived)'으로 도출 강제, 고정 단창 금지. Epic #2346 감지축 B, ADR-119 §결정 10 ① 의 §8.5 테스트 측 instantiation. Phase 1 declarative-only)
related_files:
  - docs/superpowers/specs/2026-04-30-cfp-47-stateful-test-category-design.md (parent spec — internal-docs)
  - docs/adr/ADR-014-operational-risk-ssot-distribution.md (CFP-46 design-side 짝)
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md (additive minor 룰)
  - docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md (in-place sibling sync)
amendments:
  - ADR-119  # Amendment 2 §결정 10 ① — accumulation/lifetime-class 리스크 발현조건 기반 관측 창(soak) 도출의 §8.5 테스트 측 instantiation
  - ADR-014  # Amendment 1 — §7.4.7 outcome-signal ③ 발현조건 임계(Amendment 7)와 soak 임계 연결
is_transitional: false
---

## 상태

Adopted (2026-04-30) — CFP-47 carrier. CFP-46 ADR-014 (Operational Risk SSOT) 의 검증-side 짝 정형화.

## 컨텍스트

CFP-46 (ADR-014) 가 §7.4 운영 리스크 5 sub-item + §11.6 idempotency CONDITIONAL 을 설계 단계에서 정형화 (OperationalRiskArchitectAgent 6th SubAgent 신설 + design-output v1→v2 BREAKING bump). 그러나 검증 단계 (codeforge-test lane) 는 여전히 functional/integration/infra/perf 4 카테고리만 보유. 결과:

- §7.4 boundary 가 코드에서 시간 흐름 + 재시작 차원에서 지켜지는가 검증할 카테고리 부재
- §11.6 idempotency invariant 의 replay 동작 검증 mechanism 부재
- 트레이딩 시스템 등 production-readiness 시스템의 long-running connection / stateful cache / background worker / process restart 시나리오가 §8 에서 invisible

사용자 의도 (2026-04-30): "기능 완결성 > 경량화. 트레이딩 시스템에서 데이터 스트림 production 안정성 + 백테스팅 + 라이브 거래 웹페이지 — production-readiness invariant 검증 카테고리 필수."

## 결정

### 결정 1 — §8.5 CONDITIONAL sub-section 신설 (codeforge-design template)

`change-plan.md` §8 Test Contract 에 `§8.5 Stateful / restart invariant tests (CONDITIONAL)` 신규 sub-section 추가. CFP-46 §11.6 dual 패턴 (CONDITIONAL + N/A 사유 강제). 적용 조건 4종 (long-running connection / stateful cache / background worker / process restart-aware) 중 1+ Y 이면 §8.5.1+ 본문 필수, 4종 모두 N + substantive reason 이면 §8.5 N/A 허용.

### 결정 2 — TestContractArchitectAgent mandate 확장 (신규 SubAgent 미도입)

design lane 5th SubAgent TestContractArchitectAgent 가 §8.5 도 author. 신규 SubAgent 도입 안 함 — design lane 6 SubAgent 유지 (CodebaseMapper / Refactor / SecurityArch / OperationalRiskArch / TestContractArch / DataMigrationArch). §8.5 는 §8 도메인 자연 확장이므로 cross-domain 신설 명분 없음.

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
- design lane 6 SubAgent 유지 (TestContract mandate 확장만)
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
- **(γ) StatefulTestArchitectAgent 신설** (design lane 7th SubAgent): TestContractArch 와 분리. 거부 — §8 도메인 내부 cross-domain 신설 명분 부재 (CFP-46 OpRiskArch cross-domain 명분 부재). Codex 동의
- **TestPL 도입**: 거부 — CFP-38 ζ arc 단순성 유지. 향후 chaos integration / 3+ test agent 도입 시 별도 CFP
- **design-output v3 BREAKING bump**: 거부 — §7/§11 sub-numbering shift 없음 + deputies_results 변경 없음 + 신규 SubAgent 없음 = 순수 additive. v2.1 minor in-place 가 적합
- **chaos / fault injection 통합** (option c): 거부 — chaos infra 의존 (Toxiproxy / chaos-mesh / faketime) opinionated. CFP-48 overlay `domain_critical_invariants[]` 로 분리

## 해소 기준

N/A — permanent policy



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
- [CFP-47 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-30-cfp-47-stateful-test-category-design.md) (internal-docs)
- [ADR-014](ADR-014-operational-risk-ssot-distribution.md) — CFP-46 design-side 짝
- [ADR-008](ADR-008-inter-plugin-contract-versioning.md) — additive minor 룰
- [ADR-010](ADR-010-inter-plugin-contract-sibling-sync.md) — in-place sibling sync

## Amendment 1 (CFP-2349, 2026-06-19): §8.5.1 long-running invariant tests soak 지속 시간 = 발현조건 기반(manifestation-derived) 도출 강제 (고정 단창 금지 — 차단형 declarative)

> **형식 주의**: 본 ADR-015 의 첫 amendment. body `## Amendment N` section 방식 (sibling ADR-014 Amendment 1~7 동일 패턴 답습 — frontmatter amendment_log field 부재, `related_stories` Amendment 1 row + `amendments:` ADR cross-ref list 만). ADR-042 (frontmatter amendment_log id 방식) 와 format 상이.

### 동기 (incident 근거)

Epic #2346 (감지축 B) S3 (CFP-2349) carrier — [ADR-119](ADR-119-research-before-claims.md) Amendment 2 §결정 10 ① (게이트 verdict = 외부 관측 가능 end-outcome ground-truth, internal liveness proxy 아님 — verified via worktree Read ADR-119 §결정 10 "#### ① 게이트 verdict 판정면") 의 **§8.5 테스트 측 instantiation** (① 게이트 verdict 판정면의 §8.5 테스트 측 instantiation — child S2 #2348 = 같은 §결정 10 ① 의 §7.4 운영 AC 측 instantiation 과 disjoint).

- **결함 발현 메커니즘**: 누수·monotone 미회수 같은 **accumulation / lifetime-class 결함** (누적·수명 의존 실패) 은 누적 임계 도달 후에야 발현된다. 짧은 soak (≤ 수분) 은 임계 미도달로 green PASS → 제품 사망. 실 incident — WAL monotone 미회수 → 8 MiB lifetime cap → 약 30 분+ 경과 후 silent death (정량 출처 = escalation #2345 / mctrader-data#447, Epic #2346 incident body; ADR-119 §결정 10 ① incident 요약 — "consumer 수집기 전 lane PASS 했으나 제품 사망" — 과 정합). 임계 예시값 `≥ 8 MiB/shard` 는 [ADR-014](ADR-014-operational-risk-ssot-distribution.md) Amendment 7 §7.4.7 outcome-signal ③ 발현조건 임계의 예시.
- **기존 §8.5.1 schema 공백**: 본 ADR-015 결정 1 의 §8.5.1 "long-running invariant tests" 본문의 "지속 시간 (부하 시나리오 지속)" 은 자유서술 (예시만) 이라 임계 미도출 가능 — 고정 단창 (fixed short window) 으로 작성돼도 schema PASS. accumulation/lifetime-class 리스크에 대해 이 단창은 임계 미도달 = 거짓 green.

따라서 §8.5.1 의 soak 지속 시간은 accumulation/lifetime-class 리스크에 대해 **발현조건 기반 (manifestation-derived)** 으로 도출돼야 하며 고정 단창이 아니다 — ADR-119 §결정 10 ① ("accumulation / lifetime-class 리스크의 관측 창 (soak) 은 발현조건 기반 도출 — 고정 단창 금지", verified via worktree Read ADR-119 §결정 10 "#### ① 게이트 verdict 판정면") 의 ① 게이트 verdict 판정면의 §8.5 테스트 측 instantiation 실현. 본 Amendment 1 = §8.5.1 **internal 확장만** (신규 §8.5.5+ sub 신설 0) — 결정 1 의 §8.5.1 schema 위에 soak-derivation 의무를 additive 로 강화.

본 Amendment 1 = ADR-015 결정 1~5 본문 변경 0건 — §8.5.1 schema 를 internal 확장 (codeforge-design plugin canonical 본문 = Phase 2 sibling, 본 wrapper SSOT = 결정 1/5 §8.5.1 schema 의무 확장 declare 만). `is_transitional: false` 유지.

### 결정 1 — §8.5.1 soak 지속 시간 = 발현조건 기반 도출 (manifestation-derived, 차단형 declarative)

§8.5.0 applicability 표 (결정 1) 가 1+ Y 이고 long-lived mutable 구조가 **accumulation / lifetime-class 리스크** (capacity 회계 monotone·미회수 / 무한 누적 / lifetime cap) 에 해당할 때, §8.5.1 long-running invariant tests 의 soak 지속 시간 (부하 시나리오 지속) 은 아래 3-rule 로 도출한다:

1. **manifestation-derived (발현조건 임계까지 구동)**: accumulation/lifetime-class invariant (예: capacity 회계 monotone·미회수, 무한 누적, lifetime cap) 의 soak 는 **발현조건 임계까지 구동** 한다 — "N 분 고정" 이 아니라 "임계 누적량 도달까지". 그 임계 = [ADR-014](ADR-014-operational-risk-ssot-distribution.md) Amendment 7 (§7.4.7 outcome-signal 선언 의무) 의 **outcome-signal ③ 발현조건 임계** 와 연결 (verified via worktree Read ADR-014 **Amendment 7 §결정 1** outcome-signal 3요소 표 ③ 행 "발현조건 임계 — accumulation/lifetime-class 리스크가 드러나는 누적량", 예시 `≥ 8 MiB/shard flush 누적`). 즉 §7.4.7 이 설계-시점 선언한 발현조건 임계가 §8.5.1 soak 의 구동 종점.
2. **duration floor fallback (정량 임계 미도출 시 hard fallback)**: 발현조건 임계를 정량 도출 불가한 경우 (비결정·환경의존) **duration floor** (설계가 정한 최소 지속, 예 ≥ 30 분) 로 hard fallback + "발현조건 미상" 리스크를 §8.5.1 본문에 명시. floor 도 미충족하는 고정 단창 (≤ 수분 등) 금지 — manifestation-derived 임계 OR duration floor 둘 중 하나는 반드시 충족.
3. **§8.5.0 applicability 와 연결 (해당 여부 본문 명시)**: 어떤 long-lived mutable 구조가 monotone / lifetime 리스크인가 (accumulation/lifetime-class 해당 여부 판정) 를 §8.5.1 본문에 명시한다 — §8.5.0 applicability 결정 (결정 1) 의 1+ Y 사유와 cross-ref. S4 (#2350) / S5 (#2351) 의 invariant-surface (실패 경로 long-lived mutable 구조 enumeration — ADR-119 §결정 10 ② "generative invariant sweep" 정합, verified via worktree Read ADR-119 §결정 10 "#### ② 실패 진단 판정면") 와 cross-ref 예정.

**ADR-119 §결정 10 ① instantiation 위치**: 본 Amendment 1 = "accumulation-class 리스크 발현조건 기반 관측 창" 의 **§8.5 테스트 측 실현** (① 게이트 verdict 판정면의 §8.5 테스트 측 instantiation — 게이트 verdict 가 외부 관측 가능 end-outcome 의 monotone 진행을 충분 길이 soak 로 검증). child S2 (#2348, ADR-014 Amendment 7) 의 같은 §결정 10 ① 의 §7.4 운영 AC 측 instantiation (설계-시점 outcome-signal 선언) 과 disjoint — S2 = "어떤 임계를 PASS 조건으로 선언" (설계면), 본 S3 = "그 임계까지 soak 를 구동해 검증" (테스트면).

### 결정 2 — 측정 = consumer 환경, wrapper-self declarative (실측 면제)

- **outcome 의 실 측정 주체 = consumer 환경** (실 부하·soak 실행 환경 — StatefulTestAgent 가 consumer CI 에서 실행). codeforge wrapper-self Story 는 runtime 0 (governance Story, 실 부하 / soak 측정 환경 부재).
- **wrapper-self (dogfood) = declarative**: soak 도출 규칙 (manifestation-derived 임계 OR duration floor 선언) 의 **schema 존재만 의무, 실측 면제** ([ADR-005](ADR-005-plugin-self-application-na-standardization.md) `plugin-meta-na` 정합 — sibling ADR-014 Amendment 7 결정 3 답습, verified via worktree Read ADR-014 Amendment 7 결정 3 wrapper-self declarative). 즉 wrapper-self = soak-derivation 규칙 schema 가 §8.5.1 에 존재하는가만 declarative check, 실 soak 구동 면제.
- **non-deferrable 경계**: soak-derivation 의 **존재·구조** (manifestation-derived 임계 OR duration floor 둘 중 하나 명시) 는 설계 시점 hard (공백 = 위반) — 실측 임계 숫자만 `[empirical-source: <ref> | TBD]` defer 허용 (ADR-014 Amendment 7 결정 3 non-deferrable 패턴 답습). 즉 "soak 지속을 고정 단창으로만 작성하고 발현조건/floor 미명시" 는 §8.5.1 위반이지만 "임계 = TBD (실측 전)" 은 정상.

### 결정 3 — enforcement = Phase 1 declarative-only

- **Phase 1 (본 Amendment 1, declarative anchor)**: ADR-015 결정 1/5 의 §8.5.1 schema 의무 확장 — soak-derivation 규칙 (manifestation-derived OR duration floor) 선언 의무 codify. mechanical enforce 부재.
- **Phase 2 (별 carrier defer)**: (a) change-plan `templates/change-plan.md` §8.5.1 body mirror (codeforge-design canonical) (b) `scripts/check-doc-section-schema.sh` 에 soak-derivation lint (accumulation/lifetime-class 해당 Story 의 §8.5.1 이 manifestation-derived 임계 OR duration floor 명시 없이 고정 단창만 작성 시 FAIL) — 모두 **별 sub-carrier defer** ([ADR-119](ADR-119-research-before-claims.md) §결정 8 declarative-only / [ADR-060](ADR-060-evidence-enforceable-promotion-framework.md) 4-tier promotion 경로 / 결정 5 §8.5.0 applicability lint 패턴 답습, verified via worktree Read ADR-119 §결정 8 enforcement 경로 + §결정 10 "enforcement / 경계" Phase 1 declarative-only).

### 기존 정책 변경 0건 (ADR-015 본문)

본 Amendment 1 = ADR-015 결정 1~5 본문 변경 0건. 변경 = (a) 본 `## Amendment 1` body section (b) `related_stories` frontmatter 신설 (CFP-47 parent row + CFP-2349 Amendment 1 row) (c) `amendments:` frontmatter ADR list 신설 (ADR-119 / ADR-014 cross-ref). §8.5 CONDITIONAL sub-section 신설 (결정 1) + TestContractArch mandate 확장 (결정 2) + codeforge-test 1→2 agent split (결정 3) + additive minor bump (결정 4) + §8.5 applicability 강제 lint (결정 5) 모두 정책 변경 0건. `is_transitional: false` 무변경.

ratchet 강화 방향 (§8.5.1 soak 지속 시간에 발현조건 기반 도출 의무 additive — 결정 1 의 자유서술 "지속 시간" 위에 manifestation-derived 강제, 고정 단창 차단으로 scope 명시 확장, [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) §결정 5 정합) → sunset_justification 불필요 (강화 방향 only, 약화 0).

### Cross-references

- ADR-119 Amendment 2 §결정 10 ① (게이트 verdict = 외부 관측 가능 end-outcome ground truth + accumulation/lifetime-class 리스크 발현조건 기반 관측 창 soak — 고정 단창 금지. 본 §8.5.1 soak-derivation 이 그 §8.5 테스트 측 instantiation. verified via worktree Read ADR-119 §결정 10 "#### ① 게이트 verdict 판정면", ADR-119 frontmatter related_adrs ADR-015 row "stateful soak — accumulation/lifetime-class 리스크 발현조건 기반 관측 창(soak) 도출 근거")
- ADR-014 Amendment 7 §결정 1 (§7.4.7 outcome-signal 3요소 ③ 발현조건 임계 — 본 §8.5.1 soak 의 구동 종점 임계 source. verified via worktree Read ADR-014 **Amendment 7 §결정 1** outcome-signal 3요소 표 ③ 행)
- ADR-119 §결정 10 ② (generative invariant sweep — 실패 경로 long-lived mutable 구조 enumeration + lifetime invariant 명시. 결정 1 rule 3 의 invariant-surface cross-ref, S4 #2350 / S5 #2351 예정. verified via worktree Read ADR-119 §결정 10 "#### ② 실패 진단 판정면")
- ADR-121 (deploy/deploy-review 2 lane 폐지 — outcome 실 측정 주체 = consumer 환경 위임, wrapper-self runtime 0 declarative. 결정 2 정합)
- ADR-005 (plugin self-application NA — wrapper-self declarative 면제 정합)
- ADR-060 (4-tier enforcement promotion framework — Phase 2 soak-derivation lint 승격 경로)
- ADR-058 §결정 5 sunset_justification (ratchet 강화 방향 only — 약화 0)

cross-ref: Epic #2346 §감지축 B (S3) / Story CFP-2349 §3 / ADR-119 Amendment 2 §결정 10 ①.
