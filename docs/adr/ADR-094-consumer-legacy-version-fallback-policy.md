---
adr_number: 94
title: Consumer 구형 버전 Fallback 정책 — min_prerequisite_version 미만 consumer 의 hybrid grace period degraded mode SSOT
status: Accepted
category: tooling-infrastructure
date: 2026-05-21
carrier_story: CFP-1137 (CFP-1111-W1-S2)
parent_epic: CFP-1111
related_stories:
  - CFP-1137     # 본 carrier (CFP-1111 Wave 1 Story-2, ADR-094 sub-Story)
  - CFP-1111     # umbrella Epic
related_adrs:
  - ADR-097      # paradigm replacement governance anchor — 7-bundle sibling carrier 정합 모델
  - ADR-076      # declarative reconciliation upgrade — desired/current/converge paradigm, version_pin block 1st-class 정의 anchor
  - ADR-093      # 보고 schema 호환 — Fallback degraded mode 보고 schema cross-ref (sibling carrier)
  - ADR-096      # manifest schema — min_prerequisite_version field SSOT ↔ Fallback trigger source (sibling carrier)
related_files:
  - docs/adr/ADR-076-declarative-reconciliation-upgrade.md  # version_pin / channel block + upgrade transaction layer cross-ref
  - docs/adr/ADR-RESERVATION.md                             # row 94 reserved → active 전환
mechanical_enforcement_actions: []  # declaration-only Wave 1 — ADR-097 §결정 0 / ADR-082 §결정 6 / ADR-070 §D5 retain pattern 답습 (behavioral directive only, grace window 만료 hard-fail = 저빈도 lifecycle event, mechanical lint 비용 > 효용; pattern_count >= 2 재발 시 follow-up CFP MUST promote)
is_transitional: false  # permanent policy — consumer 구형 버전 Fallback 정책은 영구 lifecycle 정책. 약화 방향 차단 ratchet (ADR-058 §결정 5 정합)
sunset_justification: null  # is_transitional false — sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용
amendment_log: []
---

# ADR-094 — Consumer 구형 버전 Fallback 정책

## 상태

`Accepted` (2026-05-21 KST) — CFP-1137 carrier (CFP-1111 Wave 1 Story-2, ADR-094 sub-Story). dependency = ADR-097 (sub#1) merge 후 sequential. ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-097 row 97 / ADR-083 row 83 precedent 정합 — chief author scope).

## 컨텍스트

### 동인

codeforge family 는 wrapper plugin + consumer overlay + plugin install 의 declarative reconciliation paradigm (ADR-076) 으로 동작한다. consumer 는 자기 repo 의 `.claude/_overlay/project.yaml` `codeforge.version_pin` / `codeforge.channel` 로 설치 버전을 고정한다 (ADR-076 §결정 9 channel taxonomy).

sibling ADR-096 이 wrapper manifest schema 에 **`min_prerequisite_version`** field 를 도입한다 — wrapper 가 정상 작동을 보장하는 consumer 측 최소 버전 floor. consumer 가 이 floor 미만 버전을 유지하면 wrapper 의 일부 governance behavior (예: 신규 schema field 의존 lint / 신규 contract version 의존 lane gate) 가 더 이상 보장되지 않는다.

여기서 정책 공백이 발생한다: **consumer 가 min_prerequisite_version 미만 버전을 유지할 때 wrapper 는 어떻게 동작하는가.** 정책 부재 시 두 극단이 나타난다:

- **silent degraded** — wrapper 가 조용히 일부 기능을 끄고 계속 작동. consumer 는 자기 환경이 degraded 인지 인지 못함 (silent harm). mctrader-data#81 류 silent partial 결함 class 와 동형.
- **hard fail** — wrapper 가 즉시 작동 거부. consumer 는 upgrade 전까지 전면 차단 (productivity cliff — grace 없는 break).

본 ADR 은 이 두 극단의 중간 — **hybrid grace period** — 를 wrapper Fallback 정책 SSOT 로 codify 한다. K8s deprecation policy matrix (stable feature 12개월 / Beta 9개월 grace) 를 baseline 으로 채택한다.

> verified-via: Read docs/adr/ADR-076-declarative-reconciliation-upgrade.md (L7-9 frontmatter is_transitional: true + amendment_log Amendment 1 §결정 9 channel taxonomy 3-tier + version_pin disjoint invariant 본문 — consumer 측 버전 고정 mechanism 의 1st-class 정의)
> verified-via: Read docs/adr/ADR-097-paradigm-replacement-governance-anchor.md (L1-25 frontmatter + §결정 0 3 carry-over 형식 — 본 7-bundle sibling carrier 정합 모델)
> verified-via: mcp__github__issue_read mclayer/plugin-codeforge#1137 (Issue body §결정 key decision K-6 (c) hybrid grace period [권장 — K8s deprecation 정합, ADR-95 metric baseline GA 12mo/Beta 9mo align] + §결정 0 preamble 3 carry-over)

### sibling carrier 정합 (verify-via)

본 ADR 은 CFP-1111 Wave 1 Story-2 의 7-ADR sibling carrier 묶음 (ADR-092~098) 중 하나다. ADR-093 (보고 schema 호환) / ADR-096 (manifest schema, min_prerequisite_version field SSOT) 은 본 ADR 과 병렬 sibling carrier 로 진행 중이며, 본 ADR 작성 시점에 file 미존재 가능. cross-ref 는 doc link level — file 신설 완료 후 단방향 link target 정합 (sibling sequential merge order 안). manifest field SSOT = ADR-096 (본 ADR 은 trigger source 만 인용, field 정의 미중복).

## 결정

### §결정 0 — preamble: 3 carry-over 보존 declare

본 ADR 신설 시점에 다음 3 carry-over invariant 를 명시 보존한다 (Fallback 정책이 인접 governance layer 를 약화하지 않음을 박아두는 anchor — ADR-097 §결정 0 형식 답습):

1. **closed_enum open_extension:false 보존** — Fallback mode 3 enum (§결정 1 (a)/(b)/(c)) 은 closed-set. mode 확장 (4번째 enum) 은 본 ADR amendment (강화 방향, ADR-058 §결정 5 sunset_justification 의무) 로만 가능 — runtime ad-hoc 확장 금지.
2. **ADR-026 Amendment 5 PR-gate layer 독립 보존** — Fallback 정책의 grace window / degraded mode 는 phase-gate-mergeable / post-merge-followup 등 PR-gate mechanical layer (ADR-026) 를 우회하지 않는다. Fallback 은 "consumer 버전 floor" layer 이지 "wrapper PR gate" layer 아님 (disjoint layer).
3. **ADR-067 disjoint invariant 보존** — Story progression layer (max FIX 3/3 RESET cap) ↔ consumer Fallback grace window layer 는 disjoint. grace window 의 시간 경과가 ADR-067 RESET 룰을 변경하지 않는다 (ADR-076 §ADR-067 disjoint layer cross-ref 답습).

### §결정 1 — Fallback mode: (c) hybrid grace period 채택

consumer 가 min_prerequisite_version (ADR-096) 미만 버전을 유지할 때 wrapper Fallback 정책 = **3 mode enum 중 (c) hybrid grace period** [채택]. closed-set (§결정 0 open_extension:false 정합):

| mode | 정의 | 판정 |
|---|---|---|
| **(a) gap 허용 (silent degraded)** | wrapper 가 조용히 일부 기능 비활성 + 계속 작동, consumer 측 통지 없음 | **거부** — silent harm. consumer 가 degraded 상태를 인지 못함 (mctrader-data#81 silent partial 결함 class 동형). honest reporting (ADR-076 Amendment 3 result fidelity) 정신 위배 |
| **(b) 명시 break (hard fail)** | wrapper 가 floor 미만 감지 즉시 전면 작동 거부 | **거부** — grace 없는 productivity cliff. consumer 가 upgrade 완료 전까지 전면 차단 (운영 단절) |
| **(c) hybrid grace period** | floor 미만 감지 시 grace window (§결정 2 정량) 안 **degraded mode 작동 + warning 보고**, window 종료 후 hard fail | **채택** — K8s deprecation policy matrix 정합. silent harm (a) 회피 (warning 보고 의무) + productivity cliff (b) 회피 (grace window 안 작동 보장) |

**(c) 동작 semantic**:

- **grace window 안**: wrapper 는 degraded mode 로 작동한다 — floor 미만으로 보장 불가능한 신규 behavior 만 비활성, 나머지 governance 기능은 정상 유지. **매 작동 시 warning 보고 의무** (silent 금지) — degraded 상태 + 잔여 grace 기간 + 권장 upgrade target 명시. 보고 schema 는 ADR-093 (보고 schema 호환) cross-ref.
- **grace window 종료 후**: hard fail — floor 미만 consumer 에서 wrapper 작동 거부. consumer 는 upgrade 후 재개. grace window 가 (b) hard fail 의 사전 통지 + 유예 layer 로 작동 (cliff 완화).

**Fallback trigger source**: floor 미만 판정의 비교 기준 = consumer 측 설치 버전 (plugin install `.version` / `codeforge.version_pin`) ↔ wrapper manifest `min_prerequisite_version` (ADR-096 SSOT). trigger source field 정의는 ADR-096 SSOT — 본 ADR 은 trigger 발동 후의 wrapper behavior 정책만 codify (field 정의 미중복, manifest schema ↔ Fallback trigger 분리).

### §결정 2 — grace window 정량: GA 12개월 / Beta 9개월

grace window 길이 = K8s deprecation policy verbatim baseline 채택:

| feature class | grace window | baseline 근거 |
|---|---|---|
| **GA-equivalent (stable feature)** | 12개월 | K8s deprecation policy — GA(stable) API 의 deprecation grace 최소 12개월 verbatim |
| **Beta-equivalent** | 9개월 | K8s deprecation policy — Beta API 의 deprecation grace 최소 9개월 verbatim |

feature class 판정 = wrapper behavior 가 의존하는 channel tier (ADR-076 §결정 9 channel taxonomy — stable / beta / canary) 에 정합. stable tier 의존 behavior = GA-equivalent (12개월), beta tier 의존 behavior = Beta-equivalent (9개월). canary tier = grace window 적용 외 (canary 는 본질적으로 unstable, HIGH risk class — ADR-076 §결정 9 production-impact awareness 정합. canary 의존 behavior floor 미만 = grace 없이 즉시 degraded warning, hard fail timing 은 별 carrier).

**ADR-095 sunset metric baseline align**: 본 grace window 정량 (12개월 / 9개월) 은 sibling ADR-095 (sunset metric 표준화) 의 metric baseline 과 align — sunset 측정 window 와 Fallback grace window 가 동일 K8s deprecation policy 기준점을 공유한다 (cross-cutting baseline 일관성, doc link level cross-ref).

grace window 시작점 = wrapper 가 해당 consumer 환경에서 floor 미만을 **최초 감지한 시점** (degraded warning 첫 발화 timestamp, ADR-079 KST `+09:00` zoned display layer 정합). window 길이는 closed 정량 — 연장은 본 ADR amendment (강화 방향) 로만.

## 결과

### 긍정

- consumer 구형 버전 Fallback 의 1st-class 정책 획득 — 정책 공백 (silent degraded vs hard fail 양 극단) 해소.
- silent harm (a) 회피 (degraded mode warning 보고 의무) + productivity cliff (b) 회피 (grace window 안 작동 보장) — 두 극단의 trade-off 균형.
- K8s deprecation policy matrix verbatim baseline (12개월 / 9개월) 채택으로 정량값의 ad-hoc magic number 회피 — industry exemplar 인용 (ADR-068 I-5 dimensional empirical grounding 정합, lifecycle dimension empirical source = K8s deprecation policy).
- ADR-095 sunset metric baseline 과 동일 K8s 기준점 공유 — cross-cutting baseline 일관성.

### 부정 / trade-off

- degraded mode 의 "어떤 behavior 를 비활성하는가" 경계가 Wave 1 declaration-only — 정확한 per-behavior degraded scope 는 후속 carrier (별 CFP) 가 enumeration. Wave 1 은 grace period 정책 anchor 만 codify.
- grace window 만료 hard-fail 의 mechanical enforcement Wave 1 부재 (`mechanical_enforcement_actions: []`) — degraded warning 발화 / window 만료 hard-fail 은 behavioral directive (ADR-097 §결정 0 / ADR-082 §결정 6 / ADR-070 §D5 retain pattern 답습). pattern_count >= 2 재발 시 follow-up CFP MUST promote to mechanical lint.
- grace window 시작점 (최초 감지 시점) 의 영속화 mechanism 이 consumer 환경별 state 의존 — Wave 1 은 정책 정량만, state 영속화 runtime 은 후속 carrier.

## 해소 기준

N/A — permanent policy (is_transitional: false). consumer 구형 버전 Fallback 정책 = 영구 lifecycle 정책. 약화 방향 차단 ratchet (ADR-058 §결정 5 정합).

amendment 시 sunset_justification 의무 — ratchet 강화 방향만 허용 (예: grace window 정량 강화 / degraded scope per-behavior enumeration 강화 / grace 만료 hard-fail mechanical 승격). 약화 방향 (예: grace window 연장으로 hard-fail 무력화 / Fallback mode (a) silent degraded 로 다운그레이드 / closed_enum open_extension true 다운그레이드) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

본 ADR 은 ADR-058 §결정 7 보안 ADR presumption 영역 아님 (category = tooling-infrastructure, 보안 ADR default `false` presumption 무관).

## 관련 파일

- `docs/adr/ADR-096-*.md` — wrapper manifest schema, min_prerequisite_version field SSOT ↔ Fallback trigger source (sibling carrier, cross-ref)
- `docs/adr/ADR-093-*.md` — degraded mode warning 보고 schema 호환 (sibling carrier, cross-ref)
- `docs/adr/ADR-095-*.md` — sunset metric 표준화, grace window baseline align (sibling carrier, doc link level cross-ref)
- `docs/adr/ADR-076-declarative-reconciliation-upgrade.md` — version_pin / channel block (§결정 9) + upgrade transaction layer cross-ref
- `docs/adr/ADR-097-paradigm-replacement-governance-anchor.md` — 7-bundle sibling carrier 정합 모델 (§결정 0 3 carry-over 형식 답습)
- `docs/adr/ADR-RESERVATION.md` — row 94 reserved → active 전환
