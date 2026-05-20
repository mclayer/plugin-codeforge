---
adr_number: 92
title: Changelog SSOT location — codeforge family 7 plugin per-plugin self-owned CHANGELOG.md + walker aggregate view + drift detection
status: Accepted
category: tooling-infrastructure
date: 2026-05-21
carrier_story: CFP-1135 (CFP-1111-W1-S2)
parent_epic: CFP-1111
related_stories:
  - CFP-1135      # 본 carrier (CFP-1111 Wave 1 Story-2, 7-slot bundle 1/7)
  - CFP-1111      # umbrella Epic
related_adrs:
  - ADR-097       # paradigm replacement governance anchor — 본 7-bundle sibling (sub-Story #1 sequential first), CFP scope unitary 면제 channel
  - ADR-076       # declarative reconciliation upgrade — changelog walk paradigm 의 upstream paradigm anchor (cross-ref)
  - ADR-016       # marketplace registration policy — codeforge family 7 plugin scope + mirrored field versioning 정합
  - ADR-054       # doc-only fast-path — changelog SSOT location 정책 = 신규 ADR 도입 governance behavior 변경 영역 (fast-path 비대상)
related_files:
  - CHANGELOG.md                                    # wrapper self-owned changelog (per-plugin SSOT 첫 사례)
  - .claude-plugin/plugin.json                      # version drift detection 대상 (per-plugin changelog 마지막 entry ↔ plugin.json version 정합)
  - docs/adr/ADR-RESERVATION.md                     # row 92 reserved → active 전환
mechanical_enforcement_actions: []  # declaration-only Wave 1 — ADR-097 §결정 0 / ADR-082 §결정 6 / ADR-070 §D5 retain pattern 답습 (drift detection lint = §결정 2 declare, mechanical wire 별 sub-CFP carrier; pattern_count >= 2 재발 시 follow-up CFP MUST promote)
is_transitional: false  # permanent policy — changelog SSOT location 은 영구 정책 (per-plugin self-owned location 자체는 변경 저빈도 event 이나 anchor 는 future 재사용 permanent). 약화 방향 차단 ratchet (ADR-058 §결정 5 정합)
sunset_justification: null  # is_transitional false — sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용
amendment_log: []
---

# ADR-092 — Changelog SSOT location

## 상태

`Accepted` (2026-05-21 KST) — CFP-1135 carrier (CFP-1111 Wave 1 Story-2, 7-slot ADR bundle 1/7). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-083 row 83 CFP-899 precedent 정합 — chief author scope).

## 컨텍스트

### 동인

codeforge family 는 wrapper + 6 lane plugin (codeforge-{requirements,design,develop,review,test,pmo}) 7 개로 구성되며 ([ADR-016](ADR-016-marketplace-registration-policy.md) family scope), consumer project 는 overlay 메커니즘으로 이를 설치해 사용한다. governance evolution 의 기록 — 각 plugin 의 version bump 별 변경 내역 (changelog) — 이 **어디에 SSOT 로 존재하는가**가 본 ADR 의 대상 영역이다.

changelog location 이 명시 SSOT 로 codify 되지 않으면 다음 drift 가 발생한다:

- changelog 가 wrapper 한곳에 집중되면 lane plugin self-write boundary ([lane-self-write-boundary](../../skills/codeforge-lane-self-write-boundary/SKILL.md) 정책) 와 충돌 — lane plugin 변경 내역을 wrapper Orchestrator 가 대신 기록해야 하는 cross-plugin write 발생.
- changelog 가 산재하면 consumer 가 "내가 설치한 7 plugin 의 통합 변경 내역"을 한눈에 볼 단일 진입점 부재.
- changelog ↔ `plugin.json` `version` field 가 독립 갱신되면 version drift (changelog 마지막 entry version ≠ plugin.json version) — stale changelog install.

본 ADR 은 changelog SSOT location 을 **per-plugin self-owned `CHANGELOG.md`** 로 codify 하고, aggregate view 는 런타임 walker 합집합 (SSOT 아님) 으로 분리하며, version drift detection lint 를 declare 한다.

> verified-via: Read docs/adr/ADR-016-marketplace-registration-policy.md (L3 title "Marketplace registration policy for codeforge plugin family" + L10 related_files "codeforge wrapper + 6 lane plugins" — family scope 7 plugin verbatim)
> verified-via: Read docs/adr/ADR-076-declarative-reconciliation-upgrade.md (L1-8 frontmatter — adr_number 76 / title "선언적 reconciliation upgrade flow SSOT" / category governance / is_transitional true — paradigm anchor 정합)

### 본 ADR 의 위치 (7-bundle 안)

본 ADR 은 CFP-1111 Wave 1 Story-2 의 7-slot ADR sibling bundle 의 **1/7 (changelog SSOT location)** 이다. sibling carrier = ADR-093 (4-field 완료 보고 schema) / ADR-094 (consumer legacy fallback) / ADR-095 (9 ADR sunset metric 표준화) / ADR-096 (min_prerequisite_version manifest schema) / ADR-097 (paradigm replacement governance anchor, sub-Story #1 sequential first, merged 8d1888b) / ADR-098 (UpgradeAgent runtime ownership). 본 ADR 의 changelog SSOT location 은 [ADR-095](ADR-095-sunset-metric-standardization.md) (9 ADR sunset metric 표준화) 의 **metric mining source** 로 사용된다 (§결정 1 aggregate view + §관련 파일 cross-ref).

> verified-via: Read docs/adr/ADR-RESERVATION.md (L125 row 92 — "changelog SSOT location anchor. CFP-1111 Wave 1 Story-2 carrier (7-slot bundle 1/7) ... ADR-095 (9 ADR sunset metric 표준화) sister within W1-S2 (changelog metric mining 의존)" + L131 row 95 — "ADR-092 (changelog SSOT) cross-ref (metric mining source)" verbatim)

## 결정

### §결정 0 — preamble: 3 carry-over 보존 declare

본 ADR 신설 시점에 다음 3 carry-over invariant 를 명시 보존한다 (changelog SSOT location 결정이 인접 governance layer 를 약화하지 않음을 박아두는 anchor):

1. **closed_enum open_extension:false 보존** — changelog SSOT location 결정 (§결정 1) 의 enum (per-plugin self-owned `CHANGELOG.md`) 은 closed-set. SSOT location 변경 (예: monorepo 집중 / 외부 changelog 서비스 위임) 은 본 ADR amendment (강화 방향, ADR-058 §결정 5 sunset_justification 의무) 로만 가능 — runtime ad-hoc 확장 금지.
2. **ADR-026 Amendment 5 PR-gate layer 독립 보존** — changelog drift detection lint (§결정 2) 는 phase-gate-mergeable / post-merge-followup 등 PR-gate mechanical layer (ADR-026) 를 우회하지 않는다. drift detection 은 warning tier advisory layer 이며 PR gate 와 disjoint.
3. **ADR-067 disjoint invariant 보존** — Story progression layer (max FIX 3/3 RESET cap) ↔ changelog SSOT location 정책 layer 는 disjoint. changelog 갱신이 ADR-067 RESET 룰을 변경하지 않는다 ([ADR-076](ADR-076-declarative-reconciliation-upgrade.md) §ADR-067 disjoint layer cross-ref 답습).

### §결정 1 — changelog SSOT location = per-plugin self-owned `CHANGELOG.md` (K-4 결정)

codeforge family 7 plugin × consumer overlay 의 changelog SSOT location 을 다음으로 codify 한다:

**K-4 결정 = (a) per-plugin `CHANGELOG.md` self-owned** [권장 — 7 plugin self-write boundary 정합].

- **wrapper + 6 lane plugin 각자 own `CHANGELOG.md`** — 각 plugin repo 의 changelog 는 해당 plugin self-write boundary 안에서만 갱신된다 (cross-plugin write 부재). 이는 lane plugin self-write boundary 정책 + [ADR-016](ADR-016-marketplace-registration-policy.md) family scope 7 plugin 정합. plugin version bump (mirrored field `version` — ADR-016) 와 같은 PR 안에서 해당 plugin 의 `CHANGELOG.md` entry append.
- **consumer overlay = 별 changelog 미보유** — consumer overlay (`.claude/_overlay/`) 는 자체 changelog 를 두지 않는다. consumer 는 wrapper changelog walk 의 **입력** (설치된 plugin version 집합) 으로 참여하며, 별 changelog SSOT 를 신설하지 않는다 (consumer = 정책 축소 불가 + 신규 SSOT 신설 비대상).
- **aggregate view = walker 가 7 plugin changelog 합집합 생성 (런타임, SSOT 아님)** — "내가 설치한 7 plugin 의 통합 변경 내역" 단일 진입점은 walker (런타임 도구) 가 7 plugin `CHANGELOG.md` 를 합집합 (union) 으로 조립해 제공한다. 이 aggregate view 는 **derived view 이지 SSOT 아님** — SSOT 는 어디까지나 per-plugin `CHANGELOG.md` 7 source. aggregate 는 매 호출 시 재생성 (영속 file 아님), drift 발생 불가 (derived).

| 대상 | changelog 보유 | SSOT 여부 | 갱신 주체 |
|---|---|---|---|
| wrapper plugin | `CHANGELOG.md` self-owned | **SSOT** | wrapper self-write (version bump PR) |
| 6 lane plugin 각각 | `CHANGELOG.md` self-owned | **SSOT** | 해당 lane plugin self-write |
| consumer overlay | 미보유 | N/A | (walker 입력으로만 참여) |
| aggregate view (7 합집합) | 런타임 walker 산출 | derived view (SSOT 아님) | walker 런타임 재생성 |

대안 (면제 비대상): (b) wrapper 단일 집중 changelog — lane plugin cross-plugin write 발생 → self-write boundary 위배. (c) 외부 changelog 서비스 위임 — codeforge dogfood-out 정합 부재 + 단일 진입점 의미 약화. K-4 = (a) 채택 이유 = 7 plugin self-write boundary 정합 + derived aggregate 로 단일 진입점 보존 (양립).

> verified-via: Read docs/adr/ADR-RESERVATION.md (L125 row 92 — "codeforge family 7 plugin × consumer overlay 의 changelog SSOT location / generation ownership / drift detection lint normative SSOT codify" verbatim)

### §결정 2 — drift detection: changelog ↔ plugin.json version drift (warning tier)

changelog ↔ `plugin.json` `version` drift detection lint 을 declare 한다 ([ADR-060](ADR-060-evidence-enforceable-promotion-framework.md) evidence-enforceable framework warning tier):

- **check 내용**: 각 plugin 의 `CHANGELOG.md` 마지막 (최신) entry 의 version ↔ 해당 plugin `.claude-plugin/plugin.json` `.version` field 정합 (equality). mismatch = drift 신호.
- **tier = warning** (ADR-060 4-tier enum 의 `warning` — advisory). drift 검출 시 경고 emit, PR gate block 미발동 (§결정 0 carry-over 2 — PR-gate layer disjoint). 승격 (warning → blocking) 은 ADR-060 승격 gate (PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged) 충족 후 별 amendment.
- **mechanical wire = Wave 1 부재** (`mechanical_enforcement_actions: []` declaration-only). 본 ADR 은 drift detection 을 **declare** 하고, 실 lint 구현 (`scripts/` + `templates/github-workflows/`) 은 별 sub-CFP carrier (ADR-097 §결정 0 / ADR-082 §결정 6 retain pattern 답습 — pattern_count >= 2 재발 시 follow-up CFP MUST promote to mechanical lint).

본 drift detection 은 [ADR-016](ADR-016-marketplace-registration-policy.md) mirrored field (`version`) versioning + [ADR-063](ADR-063-marketplace-atomic-invariant.md) marketplace ↔ plugin.json atomic invariant 와 disjoint axis — ADR-063 = (plugin.json + CHANGELOG.md + marketplace.json) 3-file atomic coordination 의무 (version bump 시 동시 갱신), 본 §결정 2 = changelog 최신 entry version ↔ plugin.json version 사후 정합 detection (advisory). 양자 cross-ref (atomic coordination 의무 + 사후 drift detection 보완).

## 결과

### 긍정

- changelog SSOT location 1st-class codify — per-plugin self-owned `CHANGELOG.md` 가 7 plugin self-write boundary 와 정합 (cross-plugin write 0건).
- aggregate view (walker 합집합) 로 "통합 변경 내역" 단일 진입점 보존 — derived view 이므로 drift 발생 불가 (SSOT 산재 ↔ 단일 진입점 양립).
- consumer overlay 별 changelog 미보유 declare — consumer 정책 축소 불가 + 신규 SSOT 폭발 차단.
- changelog ↔ plugin.json version drift detection declare — ADR-016/ADR-063 versioning layer 보완 (사후 detection).
- [ADR-095](ADR-095-sunset-metric-standardization.md) (9 ADR sunset metric 표준화) 의 metric mining source 제공 — changelog SSOT 가 sunset metric 집계 입력으로 재사용.

### 부정 / trade-off

- per-plugin changelog 산재 = aggregate 조립 비용 (walker 런타임). 완화 = aggregate 는 derived (영속 file 부재) + walker 단일 도구 SSOT (산재해도 단일 entry point 보존).
- drift detection mechanical enforcement Wave 1 부재 (`mechanical_enforcement_actions: []`) — drift 가 manual review 의존. 완화 = §결정 2 lint declare + pattern_count >= 2 재발 시 follow-up CFP MUST promote (ADR-082 §결정 6 retain rationale 답습).
- changelog SSOT location 변경 = 저빈도 governance event — 본 anchor 의 실 적용 빈도 낮음. 그러나 anchor 부재 시 매 changelog 정책 논쟁마다 ad-hoc 재논쟁 = governance 비용. anchor 도입이 1회성 비용으로 future 재논쟁 차단 (trade-off 정당).

## 해소 기준

N/A — permanent policy (is_transitional: false). changelog SSOT location = 영구 tooling-infrastructure 정책. 약화 방향 차단 ratchet (ADR-058 §결정 5 정합).

amendment 시 sunset_justification 의무 — ratchet 강화 방향만 허용 (예: drift detection warning → blocking 승격 / aggregate view mechanical 정합 강화 / SSOT location enum 강화). 약화 방향 (예: per-plugin self-owned → wrapper 집중 다운그레이드 / drift detection 제거 / closed_enum open_extension true 다운그레이드) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

본 ADR 은 ADR-058 §결정 7 보안 ADR presumption 영역 아님 (category = tooling-infrastructure, 보안 ADR default `false` presumption 무관).

## 관련 파일

- `CHANGELOG.md` — wrapper self-owned changelog (per-plugin SSOT 첫 사례, §결정 1)
- `.claude-plugin/plugin.json` — version drift detection 대상 (§결정 2, changelog 마지막 entry version ↔ plugin.json `.version` 정합)
- `docs/adr/ADR-RESERVATION.md` — row 92 reserved → active 전환
- `docs/adr/ADR-097-paradigm-replacement-governance-anchor.md` — 본 7-bundle sibling (sub-Story #1 sequential first), CFP scope unitary 면제 channel (cross-ref)
- `docs/adr/ADR-095-sunset-metric-standardization.md` — 9 ADR sunset metric 표준화, 본 changelog SSOT 를 metric mining source 로 사용 (sister cross-ref)
- `docs/adr/ADR-076-declarative-reconciliation-upgrade.md` — changelog walk paradigm 의 upstream paradigm anchor (cross-ref)
- `docs/adr/ADR-016-marketplace-registration-policy.md` — codeforge family 7 plugin scope + mirrored field `version` versioning 정합 (cross-ref)
