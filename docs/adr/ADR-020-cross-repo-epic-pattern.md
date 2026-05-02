---
adr: ADR-020
title: Cross-repo Epic 패턴
date: 2026-05-02
status: Accepted
category: orchestration
carrier_story: CFP-60
supersedes: null
superseded_by: null
---

# ADR-020: Cross-repo Epic 패턴

## 컨텍스트

mctrader 6-repo 의 첫 cross-repo Epic (MCT-12) 진행 시 현재 wrapper SSOT (CLAUDE.md "1 Story = 2 PRs" + playbook §3) 가 단일 repo 가정 — cross-repo PR sequencing / contract version sync / Story file location / merge 순서 / rollback 절차 부재.

Codex audit (2026-05-02, gpt-5.5 high) #6 FAIL: "retrospective 발견은 계약 불일치와 임시방편 PR 순서를 초래함. proactive 권장 — CFP-60 선행".

## 결정

### 결정 1: Epic owner repo 자유 결정 + 도메인 ADR collocate

cross-repo Epic 의 parent Issue 위치 = consumer 가 명시. wrapper 강제 X.

- doc-only hub repo 권장 (예: mctrader-hub)
- consumer 가 `epic_owner_repo` field 로 명시 의무
- **Epic owner repo = consumer 의 doc-only hub 일 경우, 도메인 ADR 도 같은 repo 에 collocate** (single source of truth — cross-repo 도메인 결정의 분산 방지)

### 결정 2: Child Story 위치 = 작업 repo 자체 + Epic Issue body link 수집

각 작업 repo 의 `docs/stories/<KEY>.md` 자체 보유 (consumer default). dogfood-out 정책 (ADR-013) 은 codeforge family 만 적용 — consumer 자유.

- **Parent Epic Issue body** = child Story Issue 들의 `<owner>/<repo>#<issue>` link 모음 보유 (Epic 진행 추적의 single entry point)
- 예: `mclayer/mctrader-hub#11` (Epic) body 에 `mclayer/mctrader-market#1`, `mclayer/mctrader-market-bithumb#1`, ... link 5 개

### 결정 3: Story §1 메타 에 `epic_dependencies` field 추가 (optional)

Format:

```yaml
epic_dependencies:
  - type: hard_block | design_parallel | impl_parallel
    target: <KEY>
    repo: <owner/repo>
```

Type 정의:
- `hard_block`: blocking dependency (target merge 전 본 Story 작업 불가)
- `design_parallel`: 설계 동시 진행 가능 (구현은 target 후)
- `impl_parallel`: 구현 동시 진행 가능 (target merge 와 무관)

### 결정 4: Change Plan §3 contract pin 의무

Consumer Story 의 Change Plan §3 에 명시:

```yaml
consumes:
  <producer-repo-or-package>: <SemVer-range>
```

예: `mctrader-market: ^1.0.0`. Producer repo 의 SemVer release tag 와 align.

### 결정 5: Topological merge order (PMOAgent enforce)

Dependency graph 의 topological order 따라 merge. PMOAgent Epic 진행 시 enforce — `hard_block` 위반 detected 시 Epic 차단.

### 결정 6: Rollback 룰

Producer repo merge 후 consumer 가 break 시:
1. Producer revert PR open
2. 모든 affected consumer 의 contract pin downgrade PR open
3. Producer 가 fix 후 새 minor SemVer release
4. Consumer pin upgrade

### 결정 7: 단일 repo Story (cross-repo 아닌) 적용 룰

본 결정들 모두 backward compatible — 단일 repo Story (예: CFP-1 ~ CFP-59) 는 `epic_dependencies: []` + `epic_owner_repo: null` 명시 (또는 omit, default 동일 효과).

## 거부된 대안

### 대안 A: 1 Story = N PR across N repos

- 단일 Story 가 N repo 의 PR 모두 reference
- 거부 사유: codeforge wrapper 의 "1 Story = 2 PRs" 패턴 깨짐. 기존 lane progression 메커니즘과 충돌. PR scope 분리 어려움

### 대안 B: Cross-repo Story 통합 monorepo 강제

- 모든 cross-repo 작업을 monorepo 로 강제
- 거부 사유: consumer 자유 침해. mctrader 의 6 repo 분리 의도 (market interface 별도 repo 등) 와 충돌

### 대안 C: PR sequencing 자동화 (GitHub Actions)

- Producer PR merge 시 consumer PR 자동 업데이트 / merge
- 거부 사유: 본 CFP-60 scope 초과. 향후 별도 CFP 후보 (CFP-NN — auto-sequencing)

## 결과

- mctrader Epic MCT-12 진행 가능 (5 child Story MCT-13 ~ MCT-17)
- 단일 repo Story 영향 없음 (backward compatible)
- 향후 plugin family 외 consumer 도 cross-repo Epic 진행 가능

## 관련 파일

- [`CLAUDE.md`](../../CLAUDE.md) (cross-references update)
- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) §3 (cross-repo Epic 섹션 신설)
- [`docs/inter-plugin-contracts/requirements-output-v1.md`](../inter-plugin-contracts/requirements-output-v1.md) (epic_dependencies field 추가)
- [`docs/inter-plugin-contracts/label-registry-v1.md`](../inter-plugin-contracts/label-registry-v1.md) (audit:* + category:* label 추가)
- [ADR-013](ADR-013-codeforge-family-dogfood-out-policy.md) (dogfood-out policy — consumer 자유 결정 root)
- [ADR-021](ADR-021-phase-gap-measurable-signal.md) (phase-gap measurable signal — debut-audit triage 의 한 축)
