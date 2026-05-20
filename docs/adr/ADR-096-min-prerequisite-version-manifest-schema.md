---
adr_number: 96
title: min_prerequisite_version manifest schema — cross-tier (lane plugin → wrapper) 의존 표현 + topological resolve + mismatch lint
status: Accepted
category: tooling-infrastructure
date: 2026-05-21
carrier_story: CFP-1139 (CFP-1111-W1-S2)
parent_epic: CFP-1111
related_stories:
  - CFP-1139     # 본 carrier (CFP-1111 Wave 1 Story-2, 7-slot bundle 5/7)
  - CFP-1111     # umbrella Epic
related_adrs:
  - ADR-097      # paradigm replacement governance anchor — 본 7-bundle sibling, 정합 모델
  - ADR-076      # declarative reconciliation upgrade — desired/current/converge 3-layer + reconcile-protocol-v1 carrier (manifest 의 desired state 일부)
  - ADR-094      # consumer 구형 버전 fallback 정책 — mismatch 시 trigger 되는 sister (manifest schema ↔ Fallback trigger)
  - ADR-016      # marketplace registration policy — family 7 plugin 단일 진입점 + plugin.json mirrored field (manifest field 부착 surface)
related_files:
  - .claude-plugin/plugin.json                    # 7 plugin (wrapper + 6 lane) min_prerequisite_version field 신설 surface
  - .claude/_overlay/project.yaml                  # consumer codeforge version_pin dual carrier
  - docs/adr/ADR-094-consumer-legacy-version-fallback-policy.md  # mismatch → Fallback trigger sister
  - docs/adr/ADR-RESERVATION.md                    # row 96 reserved → active 전환
mechanical_enforcement_actions: []  # declaration-only Wave 1 — ADR-082 §결정 6 / ADR-070 §D5 retain pattern 답습 (manifest schema 도입 declare 영역, mismatch lint = warning tier wire 는 후속 sub-CFP Phase 2 carrier; pattern_count >= 2 재발 시 follow-up CFP MUST promote)
is_transitional: false  # permanent policy — cross-tier 의존 표현 manifest schema 는 codeforge family 7 plugin 구조가 유지되는 한 영구. 약화 방향 차단 ratchet (ADR-058 §결정 5 정합)
sunset_justification: null  # is_transitional false — sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용
amendment_log: []
---

# ADR-096 — min_prerequisite_version manifest schema

## 상태

`Accepted` (2026-05-21 KST) — CFP-1139 carrier (CFP-1111 Wave 1 Story-2, 7-slot bundle 5/7). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-083 row 83 CFP-899 precedent 정합 — chief author scope). ADR-094 (consumer 구형 버전 Fallback 정책) sister within W1-S2 — manifest mismatch 가 ADR-094 Fallback trigger 의 입력.

## 컨텍스트

### 동인

codeforge family 는 **7 plugin** (wrapper + 6 lane: codeforge-{requirements,design,develop,review,test,pmo}) 이 단일 marketplace 진입점 (ADR-016) 으로 노출된다. 각 lane plugin 은 wrapper 의 normative policy (CLAUDE.md SSOT / inter-plugin contract / skill) 에 의존하지만, **lane plugin 이 wrapper 의 특정 minimum 버전을 요구하는 cross-tier 의존을 표현할 mechanism 이 부재**했다.

구체 문제: wrapper 가 6.0.0 으로 breaking change (예: review-verdict 계약 major bump) 를 내보낸 뒤, consumer 가 wrapper 는 5.x 에 고정 (`version_pin`) 한 채 lane plugin 만 신규 버전으로 install 하면, lane plugin 이 전제하는 wrapper API 가 부재한 silent mismatch 가 발생한다. 현재 이 mismatch 는 install 시점에 감지되지 않고 runtime 에서 모호한 실패로 표면화한다.

ADR-076 declarative reconciliation 은 wrapper SSOT = desired state / consumer overlay + plugin install = current state 로 정의한다. 그러나 desired state 안에 "이 lane plugin 이 동작하려면 wrapper 가 최소 어떤 버전이어야 하는가" 라는 **cross-tier prerequisite** 은 1st-class 로 표현되지 않았다. 본 ADR 이 이 prerequisite 을 manifest schema field 로 codify 한다.

> verified-via: Read docs/adr/ADR-097-paradigm-replacement-governance-anchor.md (정합 모델 — frontmatter 형식 + §결정 0 preamble 3 carry-over 구조 + §해소 기준 permanent phrase 형식)
> verified-via: Read docs/adr/ADR-016-marketplace-registration-policy.md (L1-39 — family 7 plugin 단일 진입점 + plugin.json mirrored field 4종 name/version/description/author)
> verified-via: Read docs/adr/ADR-076-declarative-reconciliation-upgrade.md (L1-9 frontmatter — desired/current/converge 3-layer + reconcile-protocol-v1 carrier)
> verified-via: Read docs/adr/ADR-RESERVATION.md (L129 row 94 ADR-094 Fallback sister / L133 row 96 ADR-096 K-8 dual carrier reservation verbatim)

### 정합 baseline

본 ADR 은 ADR-097 (paradigm replacement governance anchor) 와 동일 7-bundle (CFP-1111 Wave 1 Story-2) sibling 이며, ADR-097 의 frontmatter 형식 + §결정 0 preamble 3 carry-over 구조 + §해소 기준 permanent phrase 형식을 정합 모델로 답습한다. 단 category 가 다르다 — ADR-097 = `governance`, 본 ADR = `tooling-infrastructure` (manifest schema = 도구/인프라 영역).

## 결정

### §결정 0 — preamble: 3 carry-over 보존 declare

본 ADR 신설 시점에 다음 3 carry-over invariant 를 명시 보존한다 (manifest schema 가 인접 governance layer 를 약화하지 않음을 박아두는 anchor):

1. **closed_enum open_extension:false 보존** — §결정 1 manifest field 의 carrier 위치 (consumer project.yaml + plugin plugin.json dual) 는 closed-set 2-carrier. carrier 확장은 본 ADR amendment (강화 방향, ADR-058 §결정 5 sunset_justification 의무) 로만 가능 — runtime ad-hoc 확장 금지.
2. **ADR-026 Amendment 5 PR-gate layer 독립 보존** — manifest schema 도입/변경도 phase-gate-mergeable / post-merge-followup 등 PR-gate mechanical layer (ADR-026) 를 우회하지 않는다. manifest field 변경 = plugin.json mirrored 영역 인접 (ADR-016 / ADR-063 atomic invariant) 이지만 PR gate 면제 아님 (disjoint layer).
3. **ADR-067 disjoint invariant 보존** — Story progression layer (max FIX 3/3 RESET cap) ↔ upgrade transaction layer (manifest resolve) 는 disjoint. min_prerequisite_version mismatch resolve 가 ADR-067 RESET 룰을 변경하지 않는다 (ADR-076 §ADR-067 disjoint layer cross-ref 답습).

### §결정 1 — min_prerequisite_version manifest schema (K-8 dual carrier)

**cross-tier 의존 표현 mechanism**: lane plugin (codeforge-{requirements,design,develop,review,test,pmo}) 이 wrapper (codeforge) 의 최소 버전을 요구하는 의존을 manifest field 로 표현한다.

**K-8 결정 = consumer `.claude/_overlay/project.yaml` + plugin `plugin.json` dual carrier** (closed-set 2-carrier, §결정 0 open_extension:false 정합):

| carrier | 위치 | field | 역할 |
|---|---|---|---|
| **plugin 측 (publisher 선언)** | 각 lane plugin `.claude-plugin/plugin.json` | `min_prerequisite_version: { codeforge: ">=6.0.0" }` | publisher 가 "이 lane plugin 이 동작하려면 wrapper 가 최소 6.0.0 이상" 을 선언 (desired-state 의 cross-tier prerequisite) |
| **consumer 측 (current-state pin)** | consumer `.claude/_overlay/project.yaml` | `codeforge.version_pin.version` (ADR-076 §결정 9 sibling block) | consumer 가 실제 install 한 wrapper 버전 pin (current state) |

**dual carrier rationale (K-8)**: publisher 선언 (plugin.json) 단독으로는 consumer 의 실 install 버전을 알 수 없고, consumer pin (project.yaml) 단독으로는 lane plugin 이 무엇을 요구하는지 알 수 없다. 두 carrier 의 교집합 비교 (publisher 요구 range ↔ consumer pin 실값) 가 mismatch detection 의 입력이다 (§결정 3). 단일 carrier 는 cross-tier 의존의 양 끝을 표현 못함.

**semver range 표현**: `min_prerequisite_version` 의 value 는 plugin name → semver range string 의 map. range 표현은 npm `engines` field semantics 정합 (`>=6.0.0`, `>=6.0.0 <7.0.0` 등 standard semver range). consumer pin 실값이 range 를 만족하면 PASS, 미만이면 mismatch (§결정 3). wrapper 자신의 plugin.json 은 cross-tier 의존 부재 (top of dependency tree) — wrapper `min_prerequisite_version` field 는 빈 map 또는 생략 (lane plugin 만 wrapper 를 prerequisite 으로 가짐, lane → wrapper 단방향).

manifest schema 자체는 ADR-076 desired state enumeration 의 cross-tier prerequisite 차원 — 기존 desired state 11 영역 (CFP-898/CFP-821 ratchet) 에 "cross-tier version prerequisite" 을 declare 차원으로 부착 (Wave 1 declaration-only, mechanical wire 후속).

### §결정 2 — topological resolve (lane → wrapper walk ordering)

7 plugin (wrapper + 6 lane) 의 `min_prerequisite_version` 의존 그래프는 **topological sort** 로 resolve 한다.

**의존 그래프 구조**: lane plugin → wrapper 단방향 cross-tier 의존 (6 lane 각각이 wrapper 를 prerequisite 으로 가짐). wrapper 는 의존 없음 (root). 따라서 topological order = `[wrapper, ...6 lane]` — wrapper 가 먼저 resolve 되어 버전이 확정된 뒤, 각 lane plugin 의 `min_prerequisite_version: { codeforge: <range> }` 이 확정된 wrapper 버전에 대해 검증된다.

**resolver 정합**: Cargo MSRV (minimum supported rust version) resolver + npm `engines` field 의 의존 walk ordering 정합. Cargo MSRV 처럼 — root (wrapper) 의 버전을 먼저 고정하고, 그 위 dependent (lane plugin) 의 minimum requirement 를 충족 여부로 walk. cross-tier (lane → wrapper) 단방향이므로 cycle 부재 (DAG invariant) — topological sort 가 항상 성립.

**mismatch = ADR-94 Fallback trigger (sister)**: topological walk 중 어느 lane plugin 의 `min_prerequisite_version: { codeforge: <range> }` 을 consumer 의 wrapper version_pin 실값이 **미만**으로 충족 못하면, 그 시점이 ADR-094 (consumer 구형 버전 Fallback 정책) 의 trigger 다. resolve 는 mismatch 를 검출만 하고, 검출 후 처리 (degraded mode / hybrid grace / 호환 범위 판정) 는 ADR-094 SSOT 로 위임 (disjoint — 본 ADR = detection schema, ADR-094 = detection 후 정책).

### §결정 3 — mismatch lint (warning tier, ADR-060)

`min_prerequisite_version` mismatch detection 은 **warning tier** lint 다 (ADR-060 evidence-enforceable promotion framework 4-tier enum 중 `warning`).

**lint 로직**: consumer install wrapper version (project.yaml `codeforge.version_pin.version`) 이 어느 lane plugin 의 `min_prerequisite_version: { codeforge: <range> }` 을 미만으로 충족 못하면 (`consumer_pin < plugin_min_prerequisite`) → mismatch 검출 → **ADR-094 Fallback (hybrid grace)** 안내.

**warning tier rationale**: Wave 1 declaration-only (`mechanical_enforcement_actions: []`) — manifest schema 가 막 도입되는 시점이므로 blocking 은 false-block risk (구형 consumer 정상 운영 중 차단) 가 효용 초과. warning 으로 mismatch 를 가시화 + ADR-094 Fallback 경로 안내가 1차 적정 강도. mechanical wire (warning lint script + workflow) 는 후속 sub-CFP Phase 2 carrier — pattern_count >= 2 mismatch 재발 시 follow-up CFP MUST promote (ADR-082 §결정 6 retain rationale 답습). tier 승격 (warning → blocking-on-pr 등) 은 ADR-060 §승격 gate AND condition (PR 누적 ≥ 20 + bypass 외 failure = 0 + sibling Story merged) 충족 시.

**ADR-094 와 disjoint binding**: 본 §결정 = mismatch *detection* (schema 비교 로직 + tier). mismatch *후 정책* (호환 범위 / degraded mode / hybrid grace 폭) = ADR-094 SSOT. 양 ADR 은 manifest schema (본 ADR) ↔ Fallback trigger (ADR-094) doc link level cross-ref 로 연결 (sister within W1-S2).

## 결과

### 긍정

- cross-tier (lane plugin → wrapper) 의존을 1st-class manifest field 로 표현 — 기존 부재했던 silent version mismatch 영역을 declare 차원으로 codify.
- dual carrier (publisher plugin.json + consumer project.yaml) 로 의존의 양 끝 (요구 range + 실 install pin) 을 모두 표현 — 단일 carrier 의 표현 불완전성 해소.
- topological resolve (Cargo MSRV + npm engines 정합) 로 7 plugin 의존 walk ordering 표준화 — DAG invariant (lane → wrapper 단방향, cycle 부재).
- mismatch → ADR-094 Fallback trigger 의 입력 표준화 — detection (본 ADR) / 처리 (ADR-094) disjoint binding 으로 layer 명확.

### 부정 / trade-off

- Wave 1 declaration-only — mismatch lint 의 mechanical wire 부재 (`mechanical_enforcement_actions: []`). manifest schema 도입만 declare, warning lint script + workflow 는 후속 sub-CFP Phase 2 carrier. 완화 = pattern_count >= 2 재발 시 follow-up CFP MUST promote.
- dual carrier 동기화 부담 — publisher 가 plugin.json `min_prerequisite_version` 을 bump 할 때 consumer 가 project.yaml pin 을 인지/조정해야 하는 cross-repo coordination. 완화 = mismatch warning lint (§결정 3) 가 가시화 + ADR-094 Fallback 이 grace window 제공 (즉시 차단 아님).
- semver range 표현의 publisher 정확성 의존 — publisher 가 실 prerequisite 보다 느슨/엄격하게 range 를 선언하면 false-pass/false-block. 완화 = inter-plugin contract major bump (ADR-008) 시 min_prerequisite_version 동반 bump 의무 (후속 Amendment 영역, Wave 1 declaration scope 밖).

## 해소 기준

N/A — permanent policy (manifest schema). cross-tier 의존 표현 manifest schema = codeforge family 7 plugin 구조가 유지되는 한 영구 정책. 약화 방향 차단 ratchet (ADR-058 §결정 5 정합).

amendment 시 sunset_justification 의무 — ratchet 강화 방향만 허용 (예: dual carrier mechanical sync wire / mismatch lint warning → blocking tier 승격 / inter-plugin contract major bump 시 min_prerequisite 동반 bump 의무 codify). 약화 방향 (예: carrier 2 → 1 축소 / mismatch lint 제거 / closed_enum open_extension true 다운그레이드) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

본 ADR 은 ADR-058 §결정 7 보안 ADR presumption 영역 아님 (category = tooling-infrastructure, 보안 ADR default `false` presumption 무관).

## 관련 파일

- `.claude-plugin/plugin.json` — 각 lane plugin (6종) `min_prerequisite_version: { codeforge: <range> }` field 신설 surface (publisher 측 carrier)
- `.claude/_overlay/project.yaml` — consumer `codeforge.version_pin.version` pin (consumer 측 carrier, ADR-076 §결정 9 sibling block)
- `docs/adr/ADR-094-consumer-legacy-version-fallback-policy.md` — mismatch → Fallback trigger sister (manifest schema ↔ Fallback trigger, doc link level cross-ref)
- `docs/adr/ADR-097-paradigm-replacement-governance-anchor.md` — 본 7-bundle sibling 정합 모델 (frontmatter + §결정 0 preamble 구조)
- `docs/adr/ADR-076-declarative-reconciliation-upgrade.md` — desired/current/converge 3-layer (manifest = desired state cross-tier prerequisite 차원, cross-ref)
- `docs/adr/ADR-016-marketplace-registration-policy.md` — family 7 plugin 단일 진입점 + plugin.json mirrored field (manifest field 부착 surface, cross-ref)
- `docs/adr/ADR-RESERVATION.md` — row 96 reserved → active 전환
