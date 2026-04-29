---
adr_number: 10
title: Inter-plugin Contract Sibling Sync — canonical/sibling 책임 + sync 트리거 + drift 처리 정책
status: Proposed
category: Team & Process
date: 2026-04-29
related_files:
  - docs/superpowers/specs/2026-04-29-cfp-42-inter-plugin-contract-sibling-backfill-design.md (parent CFP)
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md (versioning 룰 — 본 ADR 과 함께 모든 contract frontmatter 에 인용 의무)
  - docs/adr/ADR-009-wrapper-only-decomposition.md (ζ arc 결과 — 본 ADR 의 P0 gap 출처)
  - docs/inter-plugin-contracts/MANIFEST.yaml (contract 완결성 SSOT)
  - docs/inter-plugin-contracts/review-verdict-v2.md (선례 패턴)
---

## 상태

Proposed (2026-04-29) — CFP-42 Phase 1 PR merge 시 Accepted 전환. CFP-42 Phase 2 PR merge 시 Adopted 전환.

## 컨텍스트

ζ arc (CFP-31 parent · CFP-29~CFP-40 추출) 가 6 lane plugin 으로 분리되며 5 신규 inter-plugin `kind: contract` 표면을 lane plugin 들의 `docs/inter-plugin-contracts/` 에 canonical 로 신설:
- `requirements-output-v1` (codeforge-requirements)
- `design-output-v1` (codeforge-design)
- `develop-output-v1` (codeforge-develop)
- `test-verdict-v1` (codeforge-test)
- `pmo-output-v1` (codeforge-pmo)

ADR-009 본문 §51 은 "Inter-plugin contract 6종 보유" 라고 단언하지만, 실제 wrapper repo 의 [docs/inter-plugin-contracts/](../inter-plugin-contracts/) 에는 5 파일 — 그중 3 은 `kind: registry`, 2 는 `kind: contract` (review-verdict v1+v2). 즉 5 lane output sibling reference 가 wrapper 에 backfill 안 된 상태로 ζ arc 종료.

CFP-35 (review-verdict v2 retrofit) 는 이미 "**canonical at lane plugin repo + sibling at wrapper repo**" 패턴을 도입 ([review-verdict-v2.md:19-22](../inter-plugin-contracts/review-verdict-v2.md#L19-L22)) — 본 ADR 은 이 패턴을 5 신규 contract 에 일반화하고, 향후 누락이 재발하지 않도록 명시적 정책으로 동결.

## 결정

### 1. Canonical 위치 룰

- `kind: contract` 의 canonical 은 **producer plugin** repo 의 `docs/inter-plugin-contracts/<contract-name>-v<N>.md`
- 현재 producer 분포: 5 lane output 은 각 lane plugin, review_verdict 는 codeforge-review

### 2. Sibling 위치 룰

- wrapper repo `docs/inter-plugin-contracts/<contract-name>-v<N>.md` 가 sibling reference (consumer 1차 진입점)
- sibling 본문은 canonical 과 verbatim 일치. 부가 정보는 본문 시작의 "**상위 SSOT 위치**" 섹션 (review-verdict-v2 패턴)
- sibling frontmatter 에 `related_adrs ∋ "ADR-008"` (versioning 룰) + `related_adrs ∋ "ADR-010"` (본 ADR) 의무

### 3. MANIFEST.yaml = kind:contract registry SSOT

wrapper repo `docs/inter-plugin-contracts/MANIFEST.yaml` 가 모든 `kind: contract` 파일을 enumerate. 신규 contract 추가 절차:

1. lane plugin 에 canonical 작성 (ADR-008 versioning 룰 준수)
2. wrapper MANIFEST.yaml 에 entry 추가
3. wrapper sibling file 작성 (canonical 본문 verbatim mirror + 상위 SSOT 위치 섹션 + 본 ADR 인용 frontmatter)
4. 본 ADR 본문 불변 — MANIFEST 만 갱신

`kind: registry` 파일 (cross-cutting protocol — comment-prefix-registry, fix-event, label-registry) 은 본 MANIFEST 범위 밖. 기존 `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` 가 검증.

### 4. Sync 트리거

- canonical 변경 PR merge 직후 wrapper sibling sync PR open · merge 의무 (CFP-24 marketplace cross-repo sync 정책 동질)
- canonical PR body 또는 Story §11 에 "wrapper sibling sync PR 후속 의무" 명시
- author 의무 (본 ADR 시점) — CI 자동 차단은 후속 ADR (drift detection 도입 시점)

### 5. Drift 검출 정책

- 본 ADR 시점: manifest completeness + orphan + frontmatter schema (ADR-010 reference 포함) + sibling marker — `scripts/check-inter-plugin-contracts.sh` lint
- 본문 verbatim drift 검출 (canonical SHA vs sibling SHA 비교) 은 후속 ADR 에서 결정

## 결과

### 위배 시 처리

- lint FAIL: PR merge 차단 (필수 status check — wrapper repo CI)
- canonical 변경 후 sibling sync PR 누락: 다음 wrapper PR 가 lint manifest mismatch 로 차단 (간접 강제)
- 후속 ADR 에서 drift detection workflow 도입 시 직접 강제 가능

### 선례·관계 ADR

- ADR-008: 모든 contract frontmatter 에 함께 인용 의무. 본 ADR 은 ADR-008 의 versioning 룰을 전제로 한 sync 정책 layer
- ADR-009: ζ arc decomposition 결과 → 본 ADR 의 P0 gap 출처

### 후속 영향

- 7번째·8번째 contract 추가 시 4단계 절차 + lint 자동 차단의 이중 안전망 작동
- 향후 wrapper-canonical `kind: contract` (cross-cutting typed schema) 등장 시 MANIFEST schema 에 `role` 필드 도입 — 본 ADR 갱신 또는 신규 ADR

## 관련 파일

- [docs/inter-plugin-contracts/MANIFEST.yaml](../inter-plugin-contracts/MANIFEST.yaml) — registry SSOT
- [docs/inter-plugin-contracts/review-verdict-v2.md](../inter-plugin-contracts/review-verdict-v2.md) — 선례 패턴
- [scripts/check-inter-plugin-contracts.sh](../../scripts/check-inter-plugin-contracts.sh) — 본 ADR 강제 lint
- [docs/adr/ADR-008-inter-plugin-contract-versioning.md](ADR-008-inter-plugin-contract-versioning.md)
- [docs/adr/ADR-009-wrapper-only-decomposition.md](ADR-009-wrapper-only-decomposition.md)
