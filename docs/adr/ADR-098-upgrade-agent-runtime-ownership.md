---
adr_number: 98
title: UpgradeAgent runtime ownership — codeforge-pmo 흡수 (신규 lane plugin 거부) + model tier 재평가 의무 declare
status: Accepted
category: governance
date: 2026-05-21
carrier_story: CFP-1140 (CFP-1111-W1-S2)
parent_epic: CFP-1111
related_stories:
  - CFP-1140     # 본 carrier (CFP-1111 Wave 1 Story-2, ADR-098 sub-Story sequential — ADR-097 8d1888b merged 후속)
  - CFP-1111     # umbrella Epic
related_adrs:
  - ADR-097      # paradigm replacement governance anchor — 본 ADR sibling (7-bundle), ownership boundary 도입의 governance context
  - ADR-076      # declarative reconciliation upgrade — UpgradeAgent runtime SSOT (paradigm replace 진행 중), 본 ADR = ownership boundary codify only
  - ADR-042      # agent model selection policy — UpgradeAgent model tier 재평가 의무 anchor (§결정 2/§결정 3 정합)
  - ADR-023      # lane plugin lifecycle — 신규 codeforge-upgrade lane plugin 거부 근거 (8-plugin family blast radius)
  - ADR-044      # phase-scoped sequential team — cross-cutting agent (PMOAgent sibling) 흡수 패턴 정합
related_files:
  - docs/adr/ADR-097-paradigm-replacement-governance-anchor.md  # sibling carrier (7-bundle)
  - docs/adr/ADR-076-declarative-reconciliation-upgrade.md      # UpgradeAgent runtime SSOT cross-ref
  - docs/adr/ADR-042-agent-model-selection-policy.md            # model tier 재평가 의무 cross-ref
  - docs/adr/ADR-RESERVATION.md                                 # row 98 reserved → active 전환
mechanical_enforcement_actions: []  # declaration-only Wave 1 — ADR-097 §결정 0 / ADR-082 §결정 6 / ADR-070 §D5 retain pattern 답습 (ownership boundary = 저빈도 governance event, mechanical lint 비용 > 효용; UpgradeAgent runtime 실 구현 = Wave 2 Story-4 CFP-1155 영역. pattern_count >= 2 재발 시 follow-up CFP MUST promote)
is_transitional: false  # permanent policy — UpgradeAgent ownership boundary 는 영구 거버넌스 정책 (cross-cutting agent 귀속). 약화 방향 차단 ratchet (ADR-058 §결정 5 정합)
sunset_justification: null  # is_transitional false — sunset 기준 부재 + amendment 시 ratchet 강화 방향만 허용
amendment_log: []
---

# ADR-098 — UpgradeAgent runtime ownership

## 상태

`Accepted` (2026-05-21 KST) — CFP-1140 carrier (CFP-1111 Wave 1 Story-2, ADR-098 sub-Story — ADR-097 `8d1888b` merged 후속 sequential). ArchitectAgent direct write per ADR-070 / CFP-578 chief author precedent. ADR-079 KST `+09:00` ISO 8601 zoned governance display layer 정합. status `reserved → active` 전환 = 본 commit time (ADR-097 row 97 / ADR-083 row 83 chief author scope precedent 정합).

## 컨텍스트

### 동인

CFP-1155 (Wave 2 Story-4) 가 declarative reconciliation upgrade flow (ADR-076) 의 runtime carrier 인 **UpgradeAgent** + CLI runtime 을 도입할 예정이다. UpgradeAgent 의 mandate = codeforge family upgrade transaction 의 runtime 실행 — desired state (wrapper SSOT) ↔ current state (consumer overlay + plugin install) reconcile (changelog walk + plan + apply, ADR-076 3 mode `dry-run` / `snapshot` / `transaction` 정합).

그러나 CFP-1155 이 UpgradeAgent 를 실제 도입하기 전, **이 agent 가 어느 lane 에 귀속되는가** (ownership boundary) 가 미정 상태다. ownership 미결 시 CFP-1155 의 runtime 구현이 ad-hoc lane 배치로 흐를 risk — 특히 "신규 codeforge-upgrade lane plugin 신설" 유혹이 8-plugin family blast radius 를 동반한다 (ADR-023 lane plugin lifecycle 발동).

본 ADR 은 UpgradeAgent runtime 의 **ownership boundary 만 codify** 한다. UpgradeAgent 의 실 runtime 책임 추가 (codeforge-pmo CLAUDE.md UpgradeAgent runtime mandate 본문) 는 Wave 2 Story-4 (CFP-1155) 영역이며 본 ADR scope 외 — 본 ADR = ownership 귀속 결정 + model tier 재평가 의무 declare only (runtime spec ≠ 본 ADR).

> verified-via: gh issue view 1155 (CFP-1155 = "[CFP-1111-W2-S4] UpgradeAgent walker runtime 재정의", CLOSED — UpgradeAgent runtime 실 carrier = Wave 2 Story-4) + gh issue view 703 (CFP-703 = "Codex worker role-play structural issue", UpgradeAgent 무관 stale ref). NOTE: CLAUDE.md `## ADR` 후속 Wave carrier 단락은 "Wave 2 Story-3 (CFP-703 UpgradeAgent + CLI runtime)" stale 표기 잔존 — CLAUDE.md 정정 = 별 follow-up (#1169 scope = imperative-walker-protocol-v1 + ADR-098).
> verified-via: Read docs/adr/ADR-042-agent-model-selection-policy.md (L226-230 §결정 3 — "신규 agent 도입 또는 기존 agent model tier 변경은 별도 ADR amendment 또는 본 ADR cross-ref ADR 의무" + L150-154 §결정 2 invariant "Sonnet 으로 fully cover 가능 = role 재정의 시그널")

### Paradigm replacement 7-bundle 안 위치

본 ADR 은 ADR-097 §결정 0 가 명시한 **CFP-1111 Wave 1 Story-2 7-bundle (ADR-092~098)** 의 7번째 carrier — paradigm replacement 의 governance anchor 묶음 중 "UpgradeAgent ownership" 영역을 codify 한다 (ADR-097 §결정 0 audit trail: "changelog SSOT / 4-field 보고 schema / fallback 정책 / sunset metric 표준화 / manifest schema / 본 anchor / **UpgradeAgent ownership**" 7번째 항목 verbatim). declarative → imperative 의 실 paradigm shift 는 후속 Epic (별 carrier) 에서 진행되며, 본 ADR 은 그 전환의 runtime 주체 (UpgradeAgent) 가 어느 lane 에 귀속될지를 미리 박아두는 ownership anchor 다.

## 결정

### §결정 0 — preamble: 3 carry-over 보존 declare

본 ADR 신설 시점에 다음 3 carry-over invariant 를 명시 보존한다 (ADR-097 §결정 0 동형 — ownership boundary 결정이 인접 governance layer 를 약화하지 않음을 박아두는 anchor):

1. **closed_enum open_extension:false 보존** — §결정 1 ownership 결정 enum (a) PMO 흡수 / (b) 신규 lane plugin 은 closed-set 2-value. ownership 후보 확장 (예: 신규 lane 외 제3 귀속 옵션) 은 본 ADR amendment (강화 방향, ADR-058 §결정 5 sunset_justification 의무) 로만 가능 — runtime ad-hoc 확장 금지.
2. **ADR-026 Amendment 5 PR-gate layer 독립 보존** — UpgradeAgent 가 도입될 때 (CFP-1155) 도 phase-gate-mergeable / post-merge-followup 등 PR-gate mechanical layer (ADR-026) 를 우회하지 않는다. ownership 결정은 "agent 귀속 lane" 결정이지 "PR gate" 면제 아님 (disjoint layer).
3. **ADR-067 disjoint invariant 보존** — Story progression layer (max FIX 3/3 RESET cap) ↔ upgrade transaction layer (UpgradeAgent runtime) 는 disjoint (ADR-076 §ADR-067 disjoint layer cross-ref 답습). UpgradeAgent 의 upgrade transaction 진행이 ADR-067 RESET 룰을 변경하지 않는다.

### §결정 1 — UpgradeAgent ownership = codeforge-pmo 흡수 (K-3 결정)

CFP-1155 (Wave 2 Story-4) 가 도입할 UpgradeAgent runtime 의 ownership = **codeforge-pmo lane 흡수** [권장 / 채택].

**ownership enum (closed-set 2-value, §결정 0 open_extension:false 정합)**:

| 옵션 | 결정 | 근거 |
|---|---|---|
| **(a) codeforge-pmo 흡수** | **채택 [권장]** | codeforge-pmo lane 의 **cross-cutting agent semantic 확장** — UpgradeAgent = PMOAgent sibling (cross-cutting = 모든 레인에 걸쳐 작동하는 agent, CLAUDE.md `## Development Agent Team` 정의 정합). upgrade transaction = lane-agnostic family-wide 작업 (특정 Story lane 게이트 비개입) → cross-cutting lane (codeforge-pmo) 가 자연스러운 귀속. single-repo scope 유지 (신규 plugin 도입 0). ADR-044 phase-scoped sequential team 의 cross-cutting agent 패턴 정합 (PMOAgent + GitOpsAgent + DialogFidelityAgent sibling). |
| **(b) 신규 codeforge-upgrade lane plugin** | **거부 / defer** | **8-plugin family blast radius** — 신규 lane plugin 신설 시 ADR-023 lane plugin lifecycle 발동 + 5+ artifact 동시 변경 (marketplace.json + plugin.json×8 + CHANGELOG×8 + atomic upgrade script + 3-way version invariant). cross-cutting agent 1종 도입에 lane plugin 단위 비용 = 과잉. ADR-064 §결정 1 best-effort + ADR-023 비용 정합 — 신규 lane plugin = paradigm replacement scope 가 아닌 incremental agent 추가 영역. |

**채택 결정 (a) PMO 흡수 = single-repo scope 유지**: UpgradeAgent 를 codeforge-pmo cross-cutting agent 로 흡수하면 신규 plugin family member 도입 0 — 8-plugin family 의 marketplace / version / atomic upgrade artifact 가 그대로 (blast radius 0). PMOAgent (Epic 창설 / Story retro / cross-Story pattern) 의 cross-cutting 책임에 upgrade transaction runtime 이 자연스럽게 합류 (양자 모두 lane-agnostic family-wide).

**ownership boundary codify only (runtime mandate ≠ 본 ADR)**: 본 §결정 은 UpgradeAgent 가 codeforge-pmo 에 귀속됨을 박아둘 뿐, UpgradeAgent 의 실 runtime mandate 본문 (changelog walk 절차 / plan 생성 / apply transaction / 3 mode 동작) 을 codeforge-pmo CLAUDE.md 에 추가하는 것은 **Wave 2 Story-4 (CFP-1155) 영역**이며 본 ADR scope 외. 본 ADR = ownership 귀속 결정 anchor (boundary), CFP-1155 = runtime 실 구현 (mandate body).

### §결정 2 — model tier 재평가 의무 (ADR-042 정합)

UpgradeAgent 도입 시 ADR-042 model selection policy 의 3-tier 분류 (Opus / Sonnet / Haiku) 적용 의무. 본 ADR 은 **model tier 재평가 의무를 declare** 하며, 실 tier 확정은 Wave 2 Story-4 (CFP-1155) 영역이다 (UpgradeAgent runtime mandate body 가 확정돼야 mandate depth 근거 tier 결정 가능).

**재평가 axis (ADR-042 §결정 1 매트릭스 정합 — Wave 2 결정 입력)**:

- UpgradeAgent mandate = **changelog walk + plan + apply** (ADR-076 3 mode runtime). 이 mandate 의 reasoning depth 가 ADR-042 §결정 1 어느 tier criteria 에 부합하는지가 tier 결정자 — multi-source synthesis (다중 ADR/contract changelog dedup + reconcile plan 종합 판정) 깊이면 Opus, structured 명세 기반 mechanical apply (입력 명세가 충분히 structured + 오류 CI/transaction rollback 즉시 감지) 면 Haiku, single-mandate 실행이면 Sonnet.
- **§결정 2 invariant 정합 (ADR-042 — "Sonnet 으로 fully cover 가능 = role 재정의 시그널")**: UpgradeAgent tier 결정 시 단순 비용 최소화 (Haiku reflex) 가 아니라 mandate depth 정합 판정 의무. Sonnet 으로 fully cover 가능한 얕은 mandate 만 가지면 role 재정의 시그널.
- **ADR-042 §결정 3 신규 agent ADR 의무 정합**: UpgradeAgent = 신규 agent 도입 → ADR-042 cross-ref ADR amendment 의무 (본 ADR 이 그 cross-ref anchor — 단 실 tier 확정 + ADR-042 amendment_log entry append 는 CFP-1155 carrier). ADR-023 lane plugin lifecycle 와 함께 작동 — codeforge-pmo 흡수 (신규 lane plugin 아님) 이므로 lane plugin MINOR bump 는 codeforge-pmo 단독 (8-plugin family 동시 bump 아님).

본 ADR = **model tier 재평가 의무 declare only** — tier 값 (Opus/Sonnet/Haiku) 자체는 본 ADR 에서 결정하지 않는다 (Wave 2 Story-4 mandate body 확정 후 ADR-042 amendment 로 carry).

### §결정 3 — runtime SSOT cross-ref (ADR-076 paradigm replace 정합)

UpgradeAgent runtime 의 SSOT = **ADR-076** (declarative reconciliation upgrade flow). 본 ADR 은 runtime spec 을 codify 하지 않는다 (ownership boundary only).

**SSOT cross-ref 주의 (paradigm replace 진행 중)**:

- **reconcile-protocol-v1 = Deprecated** (CFP-1125, v1.13). UpgradeAgent runtime 의 schema/protocol SSOT 를 인용할 때 reconcile-protocol-v1 을 1st-class SSOT 로 citation 금지 — Deprecated registry.
- **runtime SSOT = ADR-076** (declarative reconciliation upgrade flow, **paradigm replace 진행 중**). ADR-097 §결정 1 paradigm replacement 정의 정합 — declarative reconciliation (ADR-076) 을 imperative changelog walk paradigm 으로 전환하는 후속 Epic 검토 영역 (CFP-1111 Wave 1 umbrella scope). UpgradeAgent runtime 의 실 paradigm (declarative 잔존 vs imperative 전환) 은 그 후속 Epic 가 확정 — 본 ADR 은 어느 paradigm 이든 UpgradeAgent = codeforge-pmo 귀속 (§결정 1) 이라는 ownership 만 박아둔다 (paradigm-agnostic ownership anchor).
- **ADR-098 = ownership boundary codify only**: runtime spec (changelog walk 알고리즘 / reconcile plan schema / apply transaction 동작) 은 본 ADR 비포함. 본 ADR 은 (1) UpgradeAgent 어느 lane 귀속 (§결정 1) (2) model tier 재평가 의무 (§결정 2) (3) runtime SSOT 가 ADR-076 임을 cross-ref (본 §결정 3) 3개만 codify.

## 결과

### 긍정

- UpgradeAgent 도입 (CFP-1155) 전 ownership boundary 선결 — runtime 구현이 ad-hoc lane 배치로 흐를 risk 차단. codeforge-pmo cross-cutting 흡수 결정 박제로 신규 lane plugin 신설 유혹 (8-plugin blast radius) 사전 차단.
- single-repo scope 유지 — 8-plugin family marketplace / version / atomic upgrade artifact blast radius 0 (PMO 흡수).
- model tier 재평가 의무 declare 로 CFP-1155 이 단순 비용 최소화 (Haiku reflex) 가 아닌 mandate depth 정합 tier 결정 강제 (ADR-042 §결정 2 invariant 정합).
- runtime SSOT (ADR-076) cross-ref 명시 + reconcile-protocol-v1 Deprecated 경계 박제 — paradigm replace 진행 중 stale SSOT citation 차단.

### 부정 / trade-off

- UpgradeAgent runtime mandate body 미확정 상태에서 ownership 만 선결 — model tier 가 Wave 2 Story-4 까지 미정 (declare only). 완화 = §결정 2 재평가 axis 명시로 Wave 2 결정 입력 미리 박제 (ad-hoc 재논쟁 차단).
- codeforge-pmo lane 의 cross-cutting agent semantic 확대 (PMOAgent + GitOpsAgent + DialogFidelityAgent + UpgradeAgent 4종) — lane 책임 다축화 risk. 완화 = upgrade transaction 도 lane-agnostic family-wide 작업 (PMO cross-cutting 정의 정합) 이므로 semantic drift 아님 (axis 동질).
- ownership boundary = 저빈도 governance event — 본 anchor 의 실 적용 빈도 낮음 (UpgradeAgent 1종 귀속 결정). 그러나 anchor 부재 시 CFP-1155 runtime 구현이 ad-hoc lane 배치 + 신규 plugin 신설 유혹에 노출 = governance 비용. anchor 도입 1회성 비용이 future ownership 재논쟁 차단 (trade-off 정당).
- `mechanical_enforcement_actions: []` (declaration-only Wave 1) — UpgradeAgent ownership 의 mechanical enforcement 부재. pattern_count >= 2 재발 (ownership boundary 위반) 시 follow-up CFP MUST promote (ADR-082 §결정 6 retain rationale 답습).

## 해소 기준

N/A — permanent policy (`is_transitional: false`). UpgradeAgent runtime ownership boundary = 영구 거버넌스 정책 (cross-cutting agent 귀속). 약화 방향 차단 ratchet (ADR-058 §결정 5 정합).

amendment 시 sunset_justification 의무 — ratchet 강화 방향만 허용 (예: ownership enum closed-set 강화 / model tier 재평가 mechanical 승격 / UpgradeAgent runtime mandate cross-ref 정밀화). 약화 방향 (예: ownership enum open_extension true 다운그레이드 / 신규 lane plugin 거부 결정 revert / model tier 재평가 의무 면제) 은 ADR-058 §결정 5 sunset_justification 의무로 차단.

본 ADR 은 ADR-058 §결정 7 보안 ADR presumption 영역 아님 (category = governance, 보안 ADR default `false` presumption 무관).

## 관련 파일

- `docs/adr/ADR-097-paradigm-replacement-governance-anchor.md` — 본 ADR sibling (CFP-1111 Wave 1 Story-2 7-bundle), ownership boundary 도입의 governance context (§결정 0 audit trail 7번째 항목)
- `docs/adr/ADR-076-declarative-reconciliation-upgrade.md` — UpgradeAgent runtime SSOT (paradigm replace 진행 중), 본 ADR = ownership boundary codify only (cross-ref)
- `docs/adr/ADR-042-agent-model-selection-policy.md` — UpgradeAgent model tier 재평가 의무 anchor (§결정 2 invariant / §결정 3 신규 agent ADR 의무 cross-ref)
- `docs/adr/ADR-023-lane-plugin-lifecycle.md` — 신규 codeforge-upgrade lane plugin 거부 근거 (8-plugin family blast radius, cross-ref)
- `docs/adr/ADR-044-phase-scoped-sequential-team.md` — cross-cutting agent (PMOAgent sibling) 흡수 패턴 정합 (cross-ref)
- `docs/adr/ADR-RESERVATION.md` — row 98 reserved → active 전환
