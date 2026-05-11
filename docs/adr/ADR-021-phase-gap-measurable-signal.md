---
adr_number: 21
title: Phase-gap measurable signal — debut-audit 카테고리 #2 backing
date: 2026-05-02
status: Accepted
category: audit
carrier_story: CFP-60
supersedes: null
superseded_by: null
is_transitional: false
---

# ADR-021: Phase-gap measurable signal — debut-audit 카테고리 #2 backing

## 상태

Accepted (2026-05-02)

## 컨텍스트

데뷔 평가 카테고리 #2 (mctrader debut Codex 평가 7 카테고리 중 "phase 별 gap + 과부하 모니터링") 가 사용자 명시 (2026-05-02) "특화 agent 포함해서 codeforge 의 모든 phase 의 gap 이나 과부하" 일반화 적용. 단 Codex audit (2026-05-02, gpt-5.5 high) #5 FAIL: "missing agent / overload / phase gap / responsibility leak 모두 정의 없이 쓰이면 매 Story 마다 noise성 Issue 발생, #1 (Lane progression) 과 중복 → 데뷔 평가 자체 신뢰 불가".

본 ADR = #2 카테고리의 mechanical / reproducible measurable signal 4 룰 정의.

## 결정

### 결정 1: 4 룰 (R1-R4) detection rule + threshold

| Rule | Detection | Source data | WARN (b) | FAIL (c) |
|---|---|---|---|---|
| **R1 Missing agent** | Story §10 FIX Ledger 의 `트리거` 컬럼 에서 같은 카테고리 finding 이 N 회 반복 + 사용자 manual review 제공 evidence 존재 | Story §10 + manual review log | ≥3 회 | ≥5 회 |
| **R2 Overload** | 1 agent 가 Change Plan §3 + §7 + §11 중 N 개 sub-section 동시 작성 + 해당 Story FIX iteration ≥M | Change Plan author 메타 + Story §10 FIX 횟수 | 2 sub + FIX 2 | 3 sub + FIX 3 |
| **R3 Phase gap** | 동일 finding 이 review lane → test lane → security lane 으로 propagate | Story §9 review lane verdict + 후속 lane finding cross-reference | 1 회 propagate | ≥2 회 propagate |
| **R4 Responsibility leak** | CLAUDE.md 책임 매트릭스 grep 결과 ✅ 0 개 또는 ✅ 2+ 개인 row 발견 | CLAUDE.md 책임 매트릭스 정적 분석 | 1 row 발견 | ≥2 row 발견 |

### 결정 2: Detection mechanism = bash script + Codex prompt template

- bash script: `scripts/check-debut-audit-signals.sh` (4 룰 mechanical detection)
- Codex prompt template: detection script 결과 + Story §10 / Change Plan / 책임 매트릭스 source 첨부 → Codex 가 해석 (b/c 판정 + ADR-NNN proposal draft)

### 결정 3: Threshold calibration = Epic MCT-12 5 Story 후 retrospective

본 ADR 의 threshold 숫자 (≥3 / 2 sub + FIX 2 등) = 첫 calibration 가설. mctrader Epic MCT-12 의 5 Story (MCT-13 ~ MCT-17) 진행 후 retrospective 에서 조정 가능 (ADR-021 amendment).

### 결정 4: Detection script 매트릭스 정적 분석 frequency

- R4 (책임 매트릭스 grep) = 책임 매트릭스 변경 시만 (CLAUDE.md PR diff 에 책임 매트릭스 포함 시) — 효율
- R1-R3 = 매 Story Phase 2 PR merge 직후 (debut-audit gate 시점)

### 결정 5: R1 evidence 추적 = Markdown comment 형식

R1 의 "사용자 manual review 제공 evidence" = Story §10 FIX Ledger row 의 `비고` 컬럼 (선택 추가) 에 `evidence: <markdown text>` 형식.

### 결정 6: R2 author 메타 추적 = Change Plan §3/§7/§11 frontmatter

Change Plan §3 / §7 / §11 의 본문 시작 부분에 `<!-- author: <agent-name> -->` HTML comment 추가 의무 (Phase 2 implementation 시 ArchitectAgent + 6 deputy 작성 시 자동 삽입).

## 거부된 대안

### 대안 A: 정성 평가 only (사용자 직관 판단)

- 거부 사유: Codex 평가 = 외부 audit 의무. 정성 평가는 사용자 의존 + reproducible X. Codex audit #5 FAIL 의 root cause

### 대안 B: PMOAgent 자동 평가

- PMOAgent 가 codeforge 자체 평가
- 거부 사유: Self-reference (PMOAgent 가 본인 데뷔 평가 못함). 외부 audit (Codex) 가 적정

### 대안 C: 4 룰 외 추가 룰 (예: R5 contract drift / R6 deprecated agent 호출 등)

- 거부 사유: 본 CFP-60 scope 초과. 향후 retrospective 에서 추가 후보. YAGNI

## 결과

- 데뷔 평가 카테고리 #2 가 mechanical + reproducible 평가 가능
- Codex audit #5 FAIL 차단
- 향후 다른 consumer 데뷔 평가 (mctrader 외) 도 동일 4 룰 적용 가능

## 해소 기준

N/A — permanent policy

## 관련 파일

- [`scripts/check-debut-audit-signals.sh`](../../scripts/check-debut-audit-signals.sh) (Phase 2 — detection script)
- [`scripts/test-check-debut-audit-signals.sh`](../../scripts/test-check-debut-audit-signals.sh) (Phase 2 — test harness)
- `scripts/test-fixtures/cfp-60-debut-audit-signals/` (Phase 2 — fixtures)
- [`docs/inter-plugin-contracts/debut-audit-triage-v1.md`](../inter-plugin-contracts/debut-audit-triage-v1.md) (카테고리 트리아지 룰)
- [`docs/inter-plugin-contracts/label-registry-v1.md`](../inter-plugin-contracts/label-registry-v1.md) (audit:* + category:* label)
- [ADR-020](ADR-020-cross-repo-epic-pattern.md) (cross-repo Epic 패턴 — 함께 carrier CFP-60)
