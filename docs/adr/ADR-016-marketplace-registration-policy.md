---
adr_number: 16
title: Marketplace registration policy for codeforge plugin family (narrow scope)
status: Accepted
category: Team & Process
date: 2026-05-01
related_files:
  - mclayer/marketplace/.claude-plugin/marketplace.json
  - mclayer/marketplace/README.md
  - .claude-plugin/plugin.json (codeforge wrapper + 6 lane plugins)
related_stories:
  - CFP-49
related_adrs:
  - ADR-008 (inter-plugin contract versioning)
  - ADR-010 (canonical / sibling sync within plugin repos)
  - ADR-013 (codeforge family dogfood-out policy)
---

# ADR-016: Marketplace registration policy for codeforge plugin family (narrow scope)

## 상태

Accepted (2026-05-01) — CFP-49 carrier. ADR-010 (canonical/sibling sync within plugin repos) 의 외부 marketplace 측 짝.

## 컨텍스트

CFP-31~40 (ζ arc) 에서 codeforge wrapper 가 wrapper-only 로 decomposition 되고 6 lane plugin (codeforge-{requirements, design, develop, test, review, pmo}) 이 별도 repo 로 spawn. 이후 각 plugin 의 `.claude-plugin/plugin.json` 변경이 `mclayer/marketplace/marketplace.json` 에 반영 안 되는 drift 누적 (CFP-46 / CFP-47 양쪽 모두). CLAUDE.md 의 "Marketplace cross-repo 동기화 의무" SSOT 는 sync 의무만 명시 — 등록 자격 / sync trigger / forward-looking 정책 / out-of-scope 가 모두 미정의.

ADR-010 은 inter-plugin contract canonical/sibling sync 만 cover (within plugin repos 끼리). `mclayer/marketplace` 는 별도 repo (3rd party 측) 라 ADR-010 scope 외.

CFP-49 가 즉시 drift 해소 sweep 진행 — 그 PR 의 carrier ADR 로 본 ADR-016 도입. **단, scope 를 narrow 하게 한정** — registration 자격 / mirrored field SSOT / sync trigger 만. 깊은 governance (parity audit 자동화 / unregister flow / lifecycle policy / cross-repo CI) 는 명시적으로 후속 CFP scope 로 deferred.

## 결정

### 결정 1: 등록 대상

codeforge family 7 plugin 모두 marketplace 등록 — wrapper (codeforge) + 6 lane plugin (codeforge-{requirements, design, develop, test, review, pmo}). 자격 기준:

- 각 plugin 의 `.claude-plugin/plugin.json` 존재
- repo public (`mclayer/plugin-codeforge-<name>` 또는 wrapper 의 경우 `mclayer/plugin-codeforge`)
- `/plugins install <name>@mclayer` 로 install 가능

신규 plugin 추가 시 본 자격 기준 충족 검증 후 등록. 자격 미충족 plugin (private / draft / 미공개) 등록 금지.

### 결정 2: Mirrored field SSOT

각 plugin 의 `.claude-plugin/plugin.json` 이 SSOT. `marketplace.json` 은 mirror only. 4 mirrored field:

- `name`
- `version`
- `description`
- `author`

drift 발생 시 plugin.json 측 진실 — `marketplace.json` 측이 plugin.json 을 따라 update.

`source` 필드 (`source.source` + `source.repo`) 는 marketplace.json 자체 가 SSOT (mirror 대상 아님 — repo 위치는 marketplace 가 결정).

`keywords` 필드 등 비-mirrored 필드는 marketplace.json 자체에서 선택적으로 유지 가능 (plugin.json 과 sync 의무 없음).

### 결정 3: Sync trigger

mirrored field 4종 중 하나라도 변경 시 즉시 sync PR (`mclayer/marketplace` 에). codeforge family plugin PR 머지 직후 sync PR open·merge 의무 — drift 누적 차단.

비-mirrored field (예: `keywords`) 만 변경 시 sync 면제 (CFP-49 spec §1.3 + CLAUDE.md "Marketplace cross-repo 동기화 의무" 의 narrow boundary).

### 결정 4: 신규 lane plugin 발생 시 (forward-looking)

codeforge family 에 신규 lane plugin spawn 시 — 해당 lane 신설 Story (CFP) 내 marketplace 등록 의무 포함. 별도 follow-up Story 분리 안 함. 등록은 spawn Story 의 Phase 2 PR 에 포함되거나 직후 sync PR 로.

본 CFP-49 시점에는 해당 사항 없음 (모든 6 lane 등록 완료) — forward-looking 정책으로만 enshrine.

### 결정 5: 명시 out-of-scope

다음 governance 항목은 본 ADR-016 scope 외 — 후속 CFP 후보:

- **Parity audit 자동화** — CI / scheduled job 으로 marketplace.json ↔ plugin.json mirrored field drift 자동 검출 (CFP-50 후보)
- **Unregister flow** — lane plugin deprecation / archival 시 marketplace 제거 절차 (CFP-51 후보)
- **Lifecycle policy** — version range / minimum version / breaking change marketplace 알림 정책
- **Cross-repo CI** — Branch protection / required check 로 sync PR 강제

위 항목들은 발생 시 별도 CFP 발의.

## 결과

### 긍정

- CFP-45 dogfood 정책 만족 — mirrored field 변경 = Story-mandated change 인 만큼 ADR carrier 동반
- Drift 즉시 차단 정책 enshrine — sync trigger (결정 3) 가 향후 CFP 의 marketplace 의무 명확
- Forward-looking 정책 (결정 4) 으로 신규 lane plugin spawn 시 누락 위험 차단
- Out-of-scope 명시 (결정 5) 로 governance 공백 인지 + 후속 CFP 후보 list

### 부정

- Parity audit 자동화 부재 — 본 ADR 후에도 sync PR open 누락 시 manual audit 만 가능. 후속 CFP 까지 risk 잔존
- Unregister flow 부재 — 미래에 lane plugin deprecate 시 별도 결정 필요
- Narrow scope 가 governance "spotty" 인상 줄 수 있음 (전체 lifecycle policy 부재)

### Trade-offs

- **본 ADR 의 narrow scope vs 깊은 governance ADR**: 솔로 dev + 트레이딩 dev 임박 상황에서 깊은 governance 작성 = scope creep. narrow ADR 이 즉시 closure + 후속 CFP 명시로 governance 공백 audit 가능
- **결정 4 forward-looking enshrine vs 발생 시 ADR**: 미래 lane spawn 시 누락 risk 차단을 위해 본 ADR 에 enshrine. 단, 정책 변경 (예: lane 등록 시 별도 Story 분리) 시 본 ADR supersede 필요

## 거부된 대안

### 대안 A: Pure execution (no new ADR)

CFP-49 가 ADR 없이 ADR-008 / ADR-010 + CLAUDE.md 인용만으로 진행.

**거부 사유**: CFP-45 정책상 fragile — Story 가 ADR 기대하는데 부재 시 dogfood 위반 risk. "신규 ADR 결정 / 기존 ADR 변경" 강제 카테고리에 marketplace 정책이 들어가는지 모호 — 안전 측 = ADR 작성.

### 대안 B: Broader governance ADR

Registration + parity audit + unregister + lifecycle 통합 ADR.

**거부 사유**: yak-shaving — parity CI / unregister / lifecycle 가 명시 후속 CFP scope. 솔로 dev + 트레이딩 dev 임박 상황에서 깊은 governance 작성 = scope creep. 본 ADR 의 narrow scope 가 즉시 closure + governance 공백 audit 명확.

### 대안 C: Deferred ADR stub

최소 placeholder + 후속 CFP (parity CI / governance 분리) 로 deferred.

**거부 사유**: deferred = 후속 CFP 와 사실상 동일하면서 ADR overhead 추가. 가치 vs 비용 균형 안 맞음. narrow ADR 이 차라리 더 명확한 결정 enshrine.

## 후속 CFP 후보

본 ADR 결정 5 (out-of-scope) 에 명시된 항목들의 follow-up CFP:

- **CFP-50 (잠정)**: Cross-repo parity CI — marketplace.json ↔ plugin.json drift 자동 검증
- **CFP-51 (잠정)**: Lane plugin lifecycle / unregister flow governance ADR

본 CFP-49 머지 후 별도 issue 로 발의 (사용자 판단).

## 관련 파일

- 본 ADR
- [CFP-49 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-05-01-cfp-49-marketplace-resync-sweep.md) (internal-docs)
- [CFP-49 change-plan](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/change-plans/cfp-49-marketplace-resync-sweep.md) (internal-docs)
- [ADR-008](ADR-008-inter-plugin-contract-versioning.md) — inter-plugin contract versioning (mirrored field SemVer 룰의 inter-plugin 측 짝)
- [ADR-010](ADR-010-inter-plugin-contract-sibling-sync.md) — canonical / sibling sync (within plugin repos)
- [ADR-013](ADR-013-codeforge-family-dogfood-out-policy.md) — dogfood-out monorepo (spec/plan/change-plan 위치)
- `mclayer/marketplace/.claude-plugin/marketplace.json` — 정책 enforcement target
- `mclayer/marketplace/README.md` — 등재 플러그인 표 mirror
