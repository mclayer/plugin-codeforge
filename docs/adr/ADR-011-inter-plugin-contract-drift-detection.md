---
adr_number: 11
title: Inter-plugin Contract Drift Detection — canonical/sibling 본문 verbatim 자동 검증
status: Proposed
category: Team & Process
date: 2026-04-30
related_files:
  - docs/superpowers/specs/2026-04-30-cfp-e-inter-plugin-contract-drift-detection-design.md (parent CFP)
  - docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md (§5 후속 ADR 의도 직접 충족)
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md
  - docs/inter-plugin-contracts/MANIFEST.yaml
  - scripts/check-inter-plugin-drift.sh (본 ADR 강제 lint)
  - .github/workflows/contract-lint.yml (job inter-plugin-drift)
related_stories:
  - CFP-E (본 ADR 신설 시점)
  - CFP-42 (parent — sibling backfill + ADR-010 도입)
  - CFP-D (parent — review_verdict v1 Archived 전환, drift skip 룰 도출)
---

# ADR-011: Inter-plugin Contract Drift Detection

## 상태

`Proposed` (2026-04-30) — CFP-E PR merge 시 `Accepted` 전환. 1회 drift catch + fix cycle 후 `Adopted`.

## 컨텍스트

ADR-010 §5 명시: "본문 verbatim drift 검출 (canonical SHA vs sibling SHA 비교) 은 후속 ADR 에서 결정". CFP-42 시점 도입한 lint 는 manifest completeness + orphan + frontmatter schema (ADR-010 reference 포함) + sibling marker 까지만 검증. 본문 verbatim 정합성은 author 의무 (수동 sync PR) — drift 누적 위험.

CFP-D 결과 v1 review_verdict 는 wrapper 단독 SSOT (canonical 부재) 로 확인 — drift 검사 대상에서 자동 skip 룰 필요.

## 결정

### 1. canonical live fetch 방식

- 매 wrapper PR/push 시 GitHub REST API (`GET /repos/{owner}/{repo}/contents/{path}`) 로 canonical 본문 fetch
- SHA snapshot 저장 안 함 (MANIFEST schema 변경 회피)
- GITHUB_TOKEN read-only 권한 (모든 lane plugin public)

### 2. 정규화 후 byte-verbatim 비교

전처리 5 단계:
1. Frontmatter 분리 (sibling/canonical 각각 본문만)
2. Sibling-only meta section 제거 (`**상위 SSOT 위치**:` 시작 단락)
3. Line ending 정규화 (CRLF → LF)
4. Trailing whitespace trim (각 줄)
5. Trailing newline 통일 (file 끝 \n 1개)

정규화 후 byte 일치 검사. 불일치 시 `difflib.unified_diff()` + `::error::` annotation.

### 3. PR/push trigger 만 (cron 미도입)

- 1 인 maintainer 환경, lane plugin 변경 = wrapper sync PR 항상 동반 가정
- `workflow_dispatch:` 추가 (수동 debug)
- cron 도입은 향후 maintainer 다인 환경 또는 lane only 변경 시나리오 빈발 시 별도 ADR

### 4. status=Archived 자동 skip + canonical 부재 처리

- MANIFEST entry 의 `status: Archived` → drift 검사 자동 skip ("skip (Archived)" 출력)
- `status: Active` 인데 canonical fetch 404 → `::error::` exit 1 (정합성 lint error)
- v1 review_verdict (CFP-D 후 Archived) 가 첫 수혜 사례

### 5. 강제 메커니즘

- 신규 GitHub Actions job `inter-plugin-drift (CFP-E)` 가 `contract-lint.yml` 에 추가
- main branch protection 의 required-status-check 에 등록 (CFP-E PR merge 후 1일 dogfood 후 사용자 직접 GitHub Settings UI 등록)
- drift 발견 시 PR merge 차단 (간접 강제 → 직접 강제 격상)

## 결과

### 위배 시 처리

- drift 발견 + status=Active: lint exit 1 → required check fail → PR merge 차단
- canonical 404 + status=Active: lint exit 1 (Active entry 의 canonical 부재는 정합성 결함)
- status=Archived: 자동 skip (review_verdict v1 패턴)
- 후속 ADR 또는 CFP 가 cron / cross-repo webhook 도입 시 본 ADR §3 갱신

### 선례·관계 ADR

- ADR-008 (versioning): 본 ADR 과 무관 (frontmatter 비교 안 함)
- ADR-010 (sibling sync): 본 ADR 이 §5 후속 ADR 직접 충족
- ADR-009 (wrapper-only decomposition): drift detection 이 wrapper-only 모델의 sibling backfill 정합성 보장

### 후속 영향

- 7번째 contract 추가 시: lane plugin canonical + wrapper sibling + MANIFEST entry → 본 lint 가 자동 검증
- 신규 contract major bump (v2 → v3): 양쪽 plugin 동시 release + 본 lint 가 sibling sync 강제

## 관련 파일

- [`scripts/check-inter-plugin-drift.sh`](../../scripts/check-inter-plugin-drift.sh) — 본 ADR 강제 lint
- [`scripts/test-check-inter-plugin-drift.sh`](../../scripts/test-check-inter-plugin-drift.sh) — 회귀 테스트 harness
- [`.github/workflows/contract-lint.yml`](../../.github/workflows/contract-lint.yml) — job `inter-plugin-drift`
- [`docs/inter-plugin-contracts/MANIFEST.yaml`](../inter-plugin-contracts/MANIFEST.yaml) — registry SSOT
- [`docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md`](ADR-010-inter-plugin-contract-sibling-sync.md) §5 — 본 ADR 의 motivation
