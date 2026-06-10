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
  - CFP-2141 (Amendment 1 — ADR 참조 상대경로 정규화)
is_transitional: false
amendment_log:
  - amendment: 1
    carrier_story: CFP-2141
    date: 2026-06-10
    scope: >-
      정규화에 6번째 단계 'ADR 참조 상대경로 정규화' 추가. mirror 는 schema/normative
      내용은 byte-verbatim 이되 ADR 참조 상대경로는 per-repo ADR 위치(lane=docs/adr,
      wrapper=archive/adr — #1973 이동)에 맞게 조정 허용. drift 검사의 path-normalize 가
      이 정책의 mechanical 구현. 검사 약화 아님 — surgical scope(../-시작 상대링크 한정,
      inline docs/adr + 절대 URL + 텍스트 mention 무손상), schema verbatim 유지.
    sunset_justification: 'N/A — is_transitional: false (permanent policy). false-positive 제거이며 검사 강도 비축소.'
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
- **`CODEFORGE_CROSS_REPO_PAT` secret** (fine-grained PAT, 6 lane plugin `contents:read` only) — lane plugin private repo 가정 (CFP-71 / 2026-05-03 amendment). PAT owner = mclayer org owner (mccho8865). expiration 후 갱신 의무.
- (이전 가정: "GITHUB_TOKEN + 모든 lane plugin public" — 실제 = 6/6 private 확인 후 가정 변경)

### 2. 정규화 후 byte-verbatim 비교

전처리 5 단계:
1. Frontmatter 분리 (sibling/canonical 각각 본문만)
2. Sibling-only meta section 제거 (`**상위 SSOT 위치**:` 시작 단락)
3. Line ending 정규화 (CRLF → LF)
4. Trailing whitespace trim (각 줄)
5. Trailing newline 통일 (file 끝 \n 1개)

정규화 후 byte 일치 검사. 불일치 시 `difflib.unified_diff()` + `::error::` annotation.

> **Amendment 1 (CFP-2141, 2026-06-10)**: 정규화에 6번째 단계 **ADR 참조 상대경로 정규화** 추가. 상세는 아래 [Amendment 로그](#amendment-로그) 참조.

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

## Amendment 로그

### Amendment 1 — ADR 참조 상대경로 정규화 (CFP-2141, 2026-06-10)

**배경.** #1973 에서 wrapper repo 의 ADR 가 `docs/adr/` → `archive/adr/` 로 이동했다. lane plugin repo 의 ADR 는 여전히 `docs/adr/` 에 위치한다. 그 결과 contract mirror 의 markdown ADR 참조 **상대링크 prefix** 가 repo 마다 정당하게 달라진다:

| 위치 | ADR 상대링크 prefix 예 |
|---|---|
| lane requirements/pmo canonical | `../adr/ADR-NNN-…` |
| design lane canonical (cross-repo 참조) | `../../../plugin-codeforge/docs/adr/ADR-NNN-…` |
| wrapper sibling | `../../archive/adr/ADR-NNN-…` |

이 prefix 차이를 verbatim 비교가 drift 로 오판해 CFP-E 가 만성 fail → 매 PR bypass 로 은퇴 못 하는 상태였다. wrapper mirror 를 canonical 과 byte-verbatim 으로 강제하면 wrapper 의 ADR 링크가 깨져 `check-markdown-links.py` 가 fail 한다 (wrapper ADR 은 `archive/adr/` 에 실재하므로 wrapper 링크는 `../../archive/adr/` 가 맞다). 즉 두 검사가 상호 모순.

**결정.** mirror 는 **schema/normative 내용은 byte-verbatim** 이되, **ADR 참조 상대경로는 per-repo ADR 위치(lane=`docs/adr`, wrapper=`archive/adr`)에 맞게 조정 허용**한다. drift 검사는 비교 직전 ADR 참조 상대경로 prefix 를 단일 토큰으로 정규화해 이 정당한 차이를 흡수한다.

**mechanical 구현.** `scripts/check-inter-plugin-drift.sh` 의 `normalize()` 에 6번째 단계 `normalize_adr_paths()` 추가. 정규식 `(?:\.\./)+(?:archive/|plugin-codeforge/docs/)?adr/(ADR-\d)` 으로 `../`-시작 상대경로 prefix + `adr/ADR-<숫자>` 만 `<ADR-REF>/ADR-…` 로 치환한다.

**검사 약화 아님 — surgical scope.** 다음은 명시적으로 **건드리지 않는다** (양쪽 repo byte-identical 이라 어차피 drift 0):
- 코드블록 안 inline `docs/adr/ADR-NNN` (`../` prefix 없음)
- 절대 URL `https://github.com/…/docs/adr/ADR-NNN`
- ADR 본문 텍스트 mention (`ADR-078` 등 경로 없는 언급)

schema 필드·contract_version·lane enum·산문 등 **다른 모든 내용은 그대로 verbatim 비교 유지**한다. 본 정규화는 실드리프트 은폐가 아니라 #1973 per-repo ADR 위치 이동이 만든 false-positive 제거다. (CFP-2141 PR 적용 시점에 design-output-v2 의 4 ADR cross-ref 줄 + requirements-output-v1 의 ADR-020 1 줄이 이 false-positive 였고, 그 외 실 drift 는 pmo-output-v1 의 `7 lane → 8 lane` factual 오류 1 건 — canonical 기준 정정.)

## 해소 기준

N/A — permanent policy

## 관련 파일

- [`scripts/check-inter-plugin-drift.sh`](../../scripts/check-inter-plugin-drift.sh) — 본 ADR 강제 lint
- [`scripts/test-check-inter-plugin-drift.sh`](../../scripts/test-check-inter-plugin-drift.sh) — 회귀 테스트 harness
- [`.github/workflows/contract-lint.yml`](../../.github/workflows/contract-lint.yml) — job `inter-plugin-drift`
- [`docs/inter-plugin-contracts/MANIFEST.yaml`](../inter-plugin-contracts/MANIFEST.yaml) — registry SSOT
- [`docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md`](ADR-010-inter-plugin-contract-sibling-sync.md) §5 — 본 ADR 의 motivation
