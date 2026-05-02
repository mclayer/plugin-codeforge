---
adr: ADR-023
title: Lane plugin lifecycle — add / deprecate / rename governance
date: 2026-05-02
status: Accepted
category: governance
carrier_story: CFP-51
supersedes: null
superseded_by: null
---

# ADR-023: Lane plugin lifecycle — add / deprecate / rename governance

## 컨텍스트

[ADR-009](ADR-009-wrapper-only-decomposition.md) 가 wrapper-only decomposition 후 6 lane plugin (codeforge-{requirements,design,review,develop,test,pmo}) composition 정의. [ADR-016](ADR-016-marketplace-registration-policy.md) 가 marketplace 동기화 의무. 단 lane plugin 자체의 lifecycle 절차 (add / deprecate / rename) 부재 → 미래 변경 시 case-by-case 결정 필요 + drift 위험.

본 ADR = lane plugin lifecycle 6 결정 형식화. doc-only 정책.

## 결정

### 결정 1: Add (신규 lane plugin 추가)

새 lane plugin 추가 의무 절차:

1. **CFP Story 작성** — 신규 lane plugin 의 책임 / agent 구성 / 7 lane sequence 내 위치 명시
2. **ADR-NNN-add-`<lane-name>`.md 작성** — wrapper repo (`mclayer/plugin-codeforge/docs/adr/`)
3. **신규 plugin repo 생성** — `mclayer/plugin-codeforge-<lane-name>` (private 또는 public, family 일관성)
4. **Marketplace 등록** — `mclayer/marketplace/marketplace.json` 의 plugins 배열에 신규 entry 추가 (ADR-016 mirrored field)
5. **Wrapper CLAUDE.md update** — composition map 표 (Lane plugin / Agent count) 에 신규 row + dependency 9종 list 갱신
6. **Internal-docs structure** — `<plugin-folder>/{specs,plans,stories,decisions,retros,change-plans}/` 디렉터리 생성 ([ADR-013](ADR-013-codeforge-family-dogfood-out-policy.md))
7. **Inter-plugin contract** — 신규 lane plugin 이 producer 인 contract (예: `<lane>-output-v1.md`) wrapper 의 sibling 작성 ([ADR-010](ADR-010-inter-plugin-contract-sibling-sync.md))

### 결정 2: Deprecate (lane plugin 제거)

Lane plugin deprecation 의무 절차:

1. **CFP Story 작성** — deprecation rationale / migration path / 영향 받는 contract / 후속 lane plugin 흡수 계획
2. **Deprecation period** — 최소 1 month (consumer 측 migration 시간) — 솔로 운영 시 사용자 본인 결정으로 단축 가능 (CFP Story 에 명시 의무)
3. **ADR-NNN-deprecate-`<lane-name>`.md 작성** — supersedes 가 있으면 명시
4. **Marketplace removal** — `mclayer/marketplace/marketplace.json` 에서 entry 제거 (ADR-016 sync)
5. **Plugin repo 처리** — archive (delete X — git history 보존)
6. **Inter-plugin contract** — 해당 lane plugin 이 producer 인 contract 의 status `Active` → `Archived`
7. **Wrapper update** — CLAUDE.md composition map / dependency 9종 list / 7 lane sequence 갱신

### 결정 3: Rename (lane plugin 이름 변경)

Rename 의무 절차:

1. **CFP Story 작성** — rename rationale + backward compatibility plan
2. **ADR-NNN-rename-`<old-name>`-`<new-name>`.md 작성**
3. **GitHub repo rename** — `gh api` 또는 web UI (자동 redirect 보장)
4. **Marketplace update** — name field 동기화 (ADR-016 mirrored field)
5. **Wrapper CLAUDE.md update** — composition map + dependency list + 7 lane sequence
6. **Internal-docs `<plugin-folder>` rename** — `git mv`
7. **Inter-plugin contract** — name reference update (sibling sync)

### 결정 4: Version 변경 (major / minor / patch)

Lane plugin 의 SemVer version bump (ADR-008 inter-plugin contract versioning 와 별개 — plugin 자체 SemVer):

- **Patch / minor**: lane plugin maintainer 직접 (CFP 불필요)
- **Major**: CFP Story 작성 의무 + breaking change migration plan

### 결정 5: Marketplace mirrored field 항상 sync

[ADR-016](ADR-016-marketplace-registration-policy.md) 의 mirrored field (name / version / description / author) 는 lane plugin → marketplace 즉시 sync 의무. **CFP-50 (parity CI, follow-up) 가 자동 검증**.

### 결정 6: Lifecycle CFP 의 fast-path 여부

Add / Deprecate / Rename 모두 **full CFP Story** (Phase 1 + Phase 2 PR) 의무. Hotfix 경로 없음. 이유:
- lane plugin 변경 = wrapper composition map + marketplace + contract 다중 영향 → 정밀 audit 필요
- 단 Hotfix-style "긴급 deprecation" 시나리오 (보안 결함 등) = 별도 CFP 후보 (본 ADR scope 외)

doc-only Story (예: 본 CFP-51) 의 Phase 2 = **N/A** ([ADR-005](ADR-005-na-standardization.md) standardization).

## 거부된 대안

### 대안 A: ADR 없이 case-by-case 결정

- 거부 사유: drift / inconsistency 위험. 본 ADR 의 trigger (CFP-49 follow-up).

### 대안 B: ADR-009 amendment (wrapper-only decomposition 안에 lifecycle 통합)

- 거부 사유: ADR-009 = composition decision. lifecycle = process. 분리가 명확.

### 대안 C: Lifecycle 자동화 (GitHub Actions 가 add / deprecate workflow 자동화)

- 거부 사유: 본 ADR scope 초과. 향후 CFP 후보. ADR 부터 우선.

## 결과

- 미래 lane plugin add / deprecate / rename 시 절차 명확
- Marketplace drift 위험 감소 (ADR-016 + CFP-50 enforce)
- mctrader 데뷔 평가 발견 ("신규 specialty agent 필요") 시 본 ADR 따라 add 진행 가능

## 관련 파일

- [`CLAUDE.md`](../../CLAUDE.md) (Development Agent Team 섹션 — cross-reference)
- [ADR-009](ADR-009-wrapper-only-decomposition.md) — wrapper-only decomposition (composition root)
- [ADR-016](ADR-016-marketplace-registration-policy.md) — marketplace registration policy
- [ADR-013](ADR-013-codeforge-family-dogfood-out-policy.md) — internal-docs structure root
- [ADR-010](ADR-010-inter-plugin-contract-sibling-sync.md) — sibling sync 정책
- ADR-022 (cfp-61 in flight, Sonnet Review-Verdict Decider — separate scope)
- CFP-50 (parity CI follow-up) — 결정 5 enforcement
