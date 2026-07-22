---
adr_number: 78
title: 살아있는 구조 설계 문서 (living architecture doc) 유지 정책 SSOT
status: Active
category: governance
date: 2026-05-18
is_transitional: false
carrier_story: CFP-919
parent_epic: CFP-756
supersedes: []
amends: []
amendment_log:
  - amendment: 1
    date: 2026-05-18
    carrier: CFP-923
    summary: |
      mechanical_enforcement_actions [] → [architecture-drift] — Epic B Story-4 S4 carrier
      (architecture_doc drift mechanical lint warning-tier wire). §결정 4 "드리프트 체크"
      의무의 mechanical actuator binding. ADR-040 Amendment 3 §결정 7.D self-application
      invariant 정합 — 본 ADR 신설 시 P-S4 mechanism 위임 declared, S4 carrier (CFP-923)
      merge 후 actual wire 동반. evidence-checks-registry.yaml `architecture-drift` entry
      warning-tier + `hotfix-bypass:architecture-drift` 43번째 label family member 동반.
    direction: strengthening
    sunset_justification: |
      N/A — ratchet 강화 only (declarative-only [] → 1 entry 추가, mechanical enforcement
      ratchet up). ADR-058 §결정 5 sunset_justification mandate 적용 영역 외 (약화 방향
      아님). 약화 시 sunset_justification 3-tuple 의무.
  - amendment: 2
    date: 2026-05-24
    carrier: CFP-1425
    summary: |
      Living Architecture page Confluence mirror authoritative 격상 + per-Epic 현행화
      mandate + 5-anchor "시스템 현황" section schema codify + diagram-as-code 의무 +
      cross-link discipline + mechanical_enforcement_actions [architecture-drift] →
      [architecture-drift, living-architecture-update] (append). Mega-Epic CFP-1415
      Sub-C bundle (CFP-1418) S3.1 carrier. ADR-111 (Confluence-mirror classification
      policy SSOT, §결정 1 closed-enum 2번째 대상 = Living Architecture page) + ADR-100
      (Confluence doc SSOT 인정, §결정 1 partial extend) + ADR-103 (git→Confluence sync
      mechanism owner) cross-ref. ADR-078 의 4 영역 closed-enum (모듈/경계/인터페이스
      계약/데이터 흐름) 약화 0건 (additive extension only) — 5-anchor section schema 는
      4 영역 위에 reading orientation layer 추가 (arc42 §3 Context & Scope / arc42 §5
      Building Block View / C4 Container / C4 Component / Open Decisions Pending,
      open_extension: false closed-enum). ArchitectAnalystAgent dual-read path 의무
      (git read primary LLM-친화 + Confluence read fallback LOSSY/ADF divergence 대비,
      Epic-A 발견 LOSSY 1건 evidence). per-Epic 현행화 mandate = 매 Epic merge 후 (또는
      Phase 1 PR merge 시 — granularity Phase 2 lane gate wire 시 결정) ArchitectAgent
      chief author 의 해당 plugin Living Architecture page 갱신 의무, 미반영 시 design
      lane verdict FIX (mechanical wire = S3.5 / CFP-1429 carrier review-verdict-v4
      v4.10). mechanical_enforcement_actions `living-architecture-update` =
      declaration-only Wave 1 (ADR-082 §결정 6 + ADR-070 §D5 retain pattern 답습,
      Phase 2 wire = S3.5 carrier).
    direction: strengthening
    sunset_justification: |
      N/A — ADR-058 §결정 5 면제 (ratchet 강화 방향: Confluence mirror authoritative
      격상 + per-Epic 현행화 mandate codify + 5-anchor section schema 신설 + diagram-as-
      code 의무 + cross-link discipline + mechanical_enforcement_actions 1 entry append).
      ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 (강화 = closed-enum 도입
      + reading orientation layer 추가, 약화 0건 — 4 영역 closed-enum 의미 보존 + per-
      Epic 현행화는 기존 "매 실행 갱신" 의무 강화 명시화). is_transitional: false 유지
      (permanent governance ratchet). 약화 방향 (예: 5-anchor section schema 축소 /
      per-Epic 현행화 의무 약화 / Confluence mirror authoritative 격상 reversal) 은 ADR-
      058 §결정 5 sunset_justification 의무로 evidence-gate 통과 요구.
related_stories:
  - CFP-919  # 본 Story carrier — Story-1 (anchor only, ADR + doc 타입 신설)
  - CFP-756  # Epic B parent — 설계 레인 영속 구조 설계 문서 유지 정책
  - CFP-1425  # Amendment 2 carrier — Mega-Epic CFP-1415 Sub-C bundle (CFP-1418) S3.1 (Living Architecture Confluence mirror authoritative + per-Epic 현행화 mandate + 5-anchor section schema)
  - CFP-1415  # Mega-Epic parent — Confluence-as-derived-mirror governance standardization (Amendment 2 carrier 의 umbrella)
related_adrs:
  - ADR-041  # Doc Location Registry — architecture_doc 14번째 entry append-only mechanism
  - ADR-076  # 선언적 reconciliation upgrade flow SSOT — desired/current/converge 3-layer 패턴 재사용 (도메인 disjoint, 패턴 동형)
  - ADR-077  # Clarification 강제 재조사 전파 정책 SSOT — Epic A soft 피의존 enabler (본 ADR 본문 미수정 invariant)
  - ADR-058  # ADR 해소 기준 의무 — is_transitional:false permanent invariant 정합
  - ADR-054  # doc-only Story fast-path — 본 Story = 신규 ADR 도입 → full-lane 강제 (fast-path 제외)
  - ADR-013  # Codeforge family dogfood-out — Story file = internal-docs wrapper/stories/CFP-919.md
  - ADR-064  # Decision principle mandate — derived default (Q1/Q2/Q3 안전 방향) + forbid-list + parallel default
  - ADR-050  # Parallel epic conflict coordination — ADR-RESERVATION row 78 sequential transition
  - ADR-040  # Worktree convention + Amendment 3 §결정 7.D — mechanical_enforcement_actions:[] declarative-only 정합
  - ADR-065  # ArchitectAgent Phase 1 mechanical sync self-check — 7-item ratchet 정합 (architecture_doc lint 영역 = S4 carrier 분리)
  - ADR-068  # Boundary completeness invariants — 4 semantic + I-5 dimensional empirical (본 Story governance 영역 → I-5 exempt)
  - ADR-070  # Codex verify-before-trust — Touchpoint #2 ArchitectAgent §3 완료 직후 mandatory dispatch
  - ADR-073  # Orchestrator verify-before-assert — fact claim marker 5종 의무 + cross-repo state 단정 verify
  - ADR-082  # Write-time self-write verification mandate — internal lane agent §3 / §7 / corpus enumeration verify
  - ADR-100  # Confluence doc SSOT 인정 — §결정 1 partial extend (git SoR-work ↔ Confluence SoR-docs disjoint axis). Amendment 2 = Living Architecture page 영역에 Confluence mirror authoritative 격상 (ADR-100 §결정 1 enumeration carrier = ADR-111 closed-enum 4 대상 중 Living Architecture page = 2번째 대상)
  - ADR-103  # git→Confluence sync mechanism — sync direction (단방향 git→Confluence) + write boundary (sync agent 단일 진입점). Amendment 2 의 mirror 대상 sync 책임 owner
  - ADR-111  # Confluence-mirror classification policy SSOT — §결정 1 closed-enum 4 대상 (ADR / Living Architecture / Change Plan / Domain Knowledge) 중 2번째 대상 = 본 ADR-078 carrier. §결정 3 IA axis (per-plugin top-level) + §결정 4 diagram-as-code + §결정 5 cross-link discipline. Amendment 2 = ADR-111 §결정 1/3/4/5 의 Living Architecture page 영역 instantiate
related_files:
  - docs/doc-locations.yaml                # architecture_doc 14번째 entry append
  - docs/doc-location-registry.md          # auto-regen (round-trip identical)
  - docs/adr/ADR-RESERVATION.md            # row 78 `reserved → active` 전환
  - CLAUDE.md                              # ADR 단락 + Doc Location Registry 단락 cross-ref
  - docs/architecture/                     # 후속 Story-2 (#920) seed 영역 + Amendment 2 Sub-C S3.3 / CFP-1427 8 lane plugin Living Arch seed 5-anchor expand 영역
  - templates/architecture-doc.md          # 후속 Story-2 (#920) template carrier (본 Story 비-생성) + Amendment 2 5-anchor schema 적용 영역 (Sub-C S3.3 carrier)
  - scripts/check-architecture-drift.sh    # 후속 Story-4 (#923) lint carrier (본 Story 비-생성)
  - templates/github-workflows/architecture-drift.yml  # 후속 Story-4 (#923) workflow carrier (본 Story 비-생성)
  - templates/github-workflows/living-architecture-update.yml  # Amendment 2 mechanical wire (Sub-C S3.5 / CFP-1429 carrier, 본 Amendment 2 scope 외)
  - scripts/check-living-architecture-update.sh  # Amendment 2 lint carrier (Sub-C S3.5 / CFP-1429, 본 Amendment 2 scope 외)
mechanical_enforcement_actions:
  - architecture-drift          # Amendment 1 (CFP-923, 2026-05-18) — S4 carrier wire 완료 (ADR-060 framework warning-tier entry, hotfix-bypass:architecture-drift 43번째 family member)
  - living-architecture-update  # Amendment 2 (CFP-1425, 2026-05-24) — Sub-C S3.5 / CFP-1429 carrier deferred-followup (Phase 2 wire = review-verdict-v4 v4.10 MINOR `living_architecture_updated: bool` + lint workflow + bats fixture + evidence-checks-registry warning-tier row + hotfix-bypass:living-architecture-update family member). ADR-082 §결정 6 + ADR-070 §D5 + ADR-111 §결정 5 retain pattern 답습 (Wave 1 declare / Wave 2 wire). pattern_count >= 2 재발 시 follow-up CFP MUST promote to blocking tier.
# Amendment 1 (CFP-923, 2026-05-18) — S4 carrier (architecture_doc drift mechanical lint) wire
# 완료. ADR-040 Amendment 3 §결정 7.D self-application invariant 충족 (declared → active wire).
# 후속 mechanism (S3 lane gate verdict carrier `architecture_doc_updated: bool` design-output-v2
# v2.4 + S2 template schema lint) 은 별 carrier 발의 영역 — 본 entry 와 disjoint axis.
# Amendment 2 (CFP-1425, 2026-05-24) — `living-architecture-update` declaration-only Wave 1 append.
# §결정 4 "per-Epic 현행화 mandate" 의 mechanical actuator binding (review-verdict-v4 v4.10
# MINOR `living_architecture_updated: bool` carrier). 실 wire = Sub-C S3.5 / CFP-1429 carrier
# (templates/github-workflows/living-architecture-update.yml + scripts/check-living-architecture-
# update.sh + bats fixture + evidence-checks-registry row + label-registry-v2 hotfix-bypass:
# living-architecture-update family member). ADR-040 Amendment 3 §결정 7.D self-application
# invariant 정합 — declare 시점 1 entry append + 후속 carrier (S3.5) 명시.
---

# ADR-078: 살아있는 구조 설계 문서 (living architecture doc) 유지 정책 SSOT

## 상태

**Active (2026-05-18 KST)** — CFP-919 (Epic B Story-1) carrier. parent_epic CFP-756 (설계 레인 영속 구조 설계 문서 ADR-078 Epic).

`is_transitional: false` — permanent architecture invariant. codeforge 설계 레인 영속 SSOT 유지 정책 영구 invariant (ADR-058 §결정 7 governance default presumption 정합).

## 컨텍스트

### 직접 동인 (Epic #756 §Epic 목적 verbatim)

codeforge 설계 레인 산출물은 현재 **Story별 변경분(Change Plan)** + **결정 단위(ADR)** 뿐. *전체 구조를 담은·Story key 독립적인·영속 설계 문서* 가 doc 분류 (epic_results / story_file / adr / change_plan / retro / domain_knowledge / spec / plan / decision_packet / inter_plugin_contract / evidence_check_registry / upgrade_events / kpi_artifact) **어디에도 없음**. 따라서 요구사항 레인의 design-reading 에이전트(Epic A, ADR-077)나 인간이 "기존 설계"를 알려면 코드 / ADR / change-plan 을 직접 훑어야 한다.

본 ADR 는 **살아있는 구조 설계 문서 (living architecture SSOT)** 를 신규 영속 doc 타입으로 신설하고, 설계 레인이 매 실행마다 이를 유지하도록 게이트 + 드리프트 체크 정책 anchor 를 도입한다.

### 도메인 disjoint 분석

| 인접 doc type | scope | 본 ADR architecture_doc 와의 disjoint |
|---|---|---|
| `adr` | 단일 의사결정 (불변) | "왜 결정" vs "지금 어떻게" |
| `change_plan` | Story별 변경 델타 | before/after delta vs after only (누적 현재 상태) |
| `domain_knowledge` | 외부 시스템 사실 | 내부 구조 vs 외부 도메인 |
| `epic_results` | Epic close 1회 evidence | 누적 영속 vs 1회 archive |
| `inter_plugin_contract` | plugin 경계 (OUT) | plugin 내부 모듈/경계 |

**결론**: 기존 13 doc_types 와 disjoint → 14번째 신설 정당화 (Story file §2.2 RequirementsPL synthesis 정합, Orchestrator verify-before-trust 정정: 현재 main entry count = 13 / 신규 = 14th).

### 외부 prior art 정합 (ResearcherAgent §6.1 cross-ref)

| 외부 anchor | 본 ADR 와의 관계 |
|---|---|
| **arc42** (12 섹션 software architecture template) | 본 ADR §결정 1 의 4 영역 = arc42 의 subset (모듈 = Building Block View / 경계 = Context & Scope / 인터페이스 계약 = Solution Strategy + Crosscutting / 데이터 흐름 = Runtime View). 라인 수준 (Glossary / Quality Requirements 등) 제외. |
| **C4 model** (Simon Brown) — Context / Container / Component / Code | 본 ADR = Context + Container + Component level. **Code level 제외** (anti-scope guard 정합). |
| **ADR** (Michael Nygard 2011) — 단일 결정 단위 (불변) | 본 ADR 의 architecture_doc = 누적 현재 상태 (가변). 양 SSOT 상보 관계 (§결정 3 명문화). |

### 패턴 prior art (codeforge 내부)

| 내부 anchor | 본 ADR 의 재사용 |
|---|---|
| **ADR-076** (선언적 reconciliation upgrade flow) | desired / current / converge 3-layer pattern (Helm-inspired, ADR-076 §결정 1) — upgrade 도메인 → **설계 lane 도메인 확장** (§결정 2). |
| **ADR-041** (Doc Location Registry) | 신규 doc type 도입 mechanism = `docs/doc-locations.yaml` row append + `scripts/check-doc-locations.sh --regen` auto-regen (본 Story §관련 코드 경로 정합). |
| **ADR-077** (Clarification 강제 재조사) | Epic A enabler 관계 — design-reading 에이전트가 architecture_doc 1개를 read 하면 충분 (코드/ADR/change-plan 직접 훑기 비용 elimination). |

## 결정

### 결정 1 — architecture_doc 도메인 정의 (4 영역 closed-enum + anti-scope guard)

**정의**: `architecture_doc` = `docs/architecture/` 경로 하 영속 markdown SSOT. Story key 독립 (고정 경로) + 누적 *현재 상태* 영역 only.

**경로 invariant**: `docs/architecture/` (각 plugin self-owned — single_repo + dogfood variant 양 지원, Q1 derived default 정합).

**4 영역 closed-enum** (라인 수준 금지 anti-scope guard):

1. **모듈** — plugin / package / module-level structural unit.
2. **경계** — plugin 간 boundary + scope partition + responsibility partition.
3. **인터페이스 계약** — inter-plugin contract surface (kind:contract + kind:registry SSOT cross-ref).
4. **데이터 흐름** — input → transform → output dataflow (lane spawn / event / artifact propagation level).

**anti-scope guard** (closed enum 외 모든 영역 금지):

- 클래스 / 함수 / 변수 라인 단위 (= "코드에 한 단계 더한 것" 전락 위험, Epic §위험신호 §1 carrier)
- 의존성 import graph 라인-level
- 함수 signature / parameter list / return type

**목표 invariant**: 코드 직접 read 없이 architecture_doc 1개 read 로 전체 구조 (모듈 + 경계 + 인터페이스 + 데이터 흐름) 파악.

### 결정 2 — ADR-076 declarative reconciliation 3-layer pattern 재사용 (도메인 확장)

ADR-076 가 codeforge upgrade 도메인에 채택한 `desired state / current state / converge` 3-layer mapping 을 **설계 lane 도메인으로 확장**:

| ADR-076 layer (upgrade 도메인) | 본 ADR architecture_doc mapping (설계 도메인) |
|---|---|
| Desired state = wrapper SSOT | `docs/architecture/` 영속 markdown 본문 (현재 도달한 design 상태 SSOT) |
| Current state = consumer overlay + plugin install | 실제 `src/` `templates/` `scripts/` 코드 구조 (live source) |
| Converge = upgrade transaction | Change Plan merge ArchitectAgent self-write 게이트 (S3 carrier) |

**ADR-076 본문 미수정 invariant** (cross-ref only) — 본 ADR 가 ADR-076 의 amendment 가 아니라 패턴 재사용 새로운 anchor.

**외부 prior art (ResearcherAgent §6.2 cross-ref)**:

- Kubernetes resource model + controller pattern (declarative desired state + controller reconciliation loop)
- Helm chart + values.yaml + render (ADR-076 §결정 1 "Helm-inspired" verbatim precedent)
- Terraform plan / apply (drift detection — S4 lint 영역 precedent)

발명 비용 0 (well-established external + 내부 ADR-076 패턴 동형).

### 결정 3 — Change Plan 과 상보 관계 명문화 (anchor only, S2 구체 field 위임)

**상보 관계**:

- `architecture_doc` (본 ADR) = 누적 **현재 상태** SSOT (영속, Story key 독립)
- `change_plan` (ADR-041 / CFP-7) = Story별 **변경 델타** SSOT (1회, Story key 종속)

**의무 invariant**: 기존 Change Plan 작성 의무 (codeforge-design lane ArchitectAgent owner_agent, doc-locations.yaml change_plan entry) 와 충돌 없음. 양 SSOT 가 disjoint 영역 (델타 vs 누적) 으로 동시 작성.

**구체 cross-ref field** (예: Change Plan §N 에 architecture_doc 영역 mapping field 신설 / drift detection annotation 의무 / template binding) = **S2 (#920) carrier 위임** (Q2 derived default 정합 — S1 = anchor 1줄 명시 only).

본 ADR 본문 = "두 SSOT 의 상보 관계가 정책으로 박혔다" 명시 only — 구체 mechanism = S2 wait.

### 결정 4 — 설계 레인 유지 의무 anchor only (mechanism = S3/S4 위임)

**의무 anchor**:

1. **게이트 의무**: 설계 레인 (codeforge-design plugin 의 ArchitectAgent chief author / ArchitectPLAgent) 이 매 실행마다 Change Plan merge 를 `docs/architecture/` 4 영역에 반영. 미반영 시 design lane verdict FIX.
2. **드리프트 체크 의무**: architecture_doc 본문 vs 실제 코드 구조 mechanical drift 감지. drift detected 시 PR warning (Phase 1) → 후속 tier escalation.

**Mechanism 위임** (본 ADR 본문 비-결정, P-N enumeration § "후속 Story 위임" SSOT):

- 게이트 mechanism (ArchitectAgent self-write 확장 + design_output contract field 신설 여부 + review-verdict-v4 carrier field) = **P-S3 (#921) carrier**
- 드리프트 lint detection scope + tier + workflow + evidence-registry entry + hotfix-bypass label = **P-S4 (#923) carrier**
- template schema 4 섹션 mechanical enforce 룰 + `docs/architecture/` 초기 seed = **P-S2 (#920) carrier**

본 ADR 결정 4 = "이 의무가 정책 SSOT 로 박혔다" 선언 only — mechanism 구체화 책임 위임 enumeration.

## 결과

### 즉시 효과 (Phase 1 PR merge 후)

1. `docs/doc-locations.yaml` 14번째 entry `architecture_doc` 등록 → `scripts/check-doc-locations.sh --full` PASS (round-trip identical, AC-2/AC-3).
2. ADR-RESERVATION row 78 `reserved → active` 전환 (ADR-050 §결정 1 sequential append 정합).
3. CLAUDE.md ADR 단락 + Doc Location Registry 단락 cross-ref append (~5 line, claude-md-line-cap workflow PASS).
4. Epic A (ADR-077) design-reading 에이전트가 본 ADR-078 enabler 로 cross-ref 가능 (ADR-077 본문 미수정 — Q3 derived default 정합).

### 후속 Story 위임 (P-N enumeration)

| Sub-story | Issue | scope | sequential trigger |
|---|---|---|---|
| **P-S2** | #920 | template schema 4 섹션 mechanical enforce 룰 + `docs/architecture/` 초기 seed (현 codeforge 구조 1회 캡처) | S1 state dependency (doc 타입 정의 선행 의무) |
| **P-S3** | #921 | lane gate + ArchitectAgent self-write 확장 + design_output contract field 신설 여부 + review-verdict-v4 carrier field | S1+S2 state dependency (doc 타입 + template 선행) |
| **P-S4** | #923 | drift lint detection scope + tier 결정 + workflow + evidence-registry row + hotfix-bypass label | S1+S2 state dependency (검사 대상 doc + 스키마 선행) |

### Cross-cutting 효과 (Epic 종료 후, Wave 4+)

- Epic A (ADR-077) RequirementsPL design-reading fan-out 비용 reduction (코드/ADR/change-plan 직접 훑기 → architecture_doc 1개 read).
- 신규 contributor onboarding 비용 reduction (codeforge 구조 1 file read).
- codeforge upgrade flow (ADR-076) 의 desired state enumeration § 안 architecture_doc 영역 포함 (Wave 4 sub-Epic #882 multi-version channel scope).

## Amendment 2 (2026-05-24 KST, CFP-1425) — Living Architecture Confluence mirror authoritative + per-Epic 현행화 mandate + 5-anchor "시스템 현황" section schema

### 동인 (Mega-Epic CFP-1415 Sub-C bundle (CFP-1418) S3.1)

사용자 직접 발화 (2026-05-24 KST, USER-UTTERANCE-VERBATIM): "내가 이전에 Github Issues에 남겨야 하는 설계문서 제외하고는 confluence에 옮기자고 했는데 지켜지고 있나? 또 이를 위한 표준이 수립되어 있나?" + (FOLLOW-UP) "응 그리고 기존 설계문서도 모두 옮기는 방향으로. confluence의 문서 저장 방식은 사용자 친화적으로. 그 구조 중에 매 에픽마다 수정하는 시스템 전체 설계 문서는 반드시 저장되어서 Architect 중 as-is 설계를 확인하는 agent가 한눈에 보기 좋게 정리하는 시스템 현황 section이 존재해야하고 architect는 매번의 시스템 작업 수정마다 이 architect를 현행화해야 한다."

본 Amendment 2 = 사용자 발화 verbatim 3 요구사항의 normative codify:
1. **"매 에픽마다 수정하는 시스템 전체 설계 문서"** → per-Epic 현행화 mandate (§Amendment 2 결정 2).
2. **"한눈에 보기 좋게 정리하는 시스템 현황 section"** → 5-anchor "시스템 현황" section schema (§Amendment 2 결정 3).
3. **"매번의 시스템 작업 수정마다 이 architect를 현행화"** → ArchitectAgent (chief author) 현행화 의무 (§Amendment 2 결정 2 + mechanical wire = S3.5 / CFP-1429 carrier).

선행 Sub-A S1.1 (CFP-1419 / ADR-111) 가 Confluence-mirror classification policy SSOT 를 closed-enum 4 mirror 대상 + 5 Issue-only retain 면제 영역으로 codify 했고, 본 Amendment 2 = ADR-111 §결정 1 closed-enum 4 대상 중 **2번째 대상 = Living Architecture page** 의 instantiate.

### Amendment 2 결정 1 — Living Architecture page Confluence mirror authoritative readable source 격상

ADR-078 §결정 1 의 `docs/architecture/` 영속 markdown SSOT (git source) 위에 **Confluence mirror authoritative readable source 격상**:

| layer | source-of-record | 의미 | 변경 source |
|---|---|---|---|
| **git = SoR-work** | per-plugin `docs/architecture/` (9 plugin family — wrapper + 8 lane plugin) | **변경의 source of record** — PR / commit / review gate / CODEOWNERS 결재가 거치는 정식 변경 채널 (ADR-013 §결정 1 KEEP invariant 보존) | 보존 (§결정 1 4 영역 closed-enum 약화 0건) |
| **Confluence = SoR-docs** | Confluence per-plugin top-level page (ADR-111 §결정 3 IA axis) authoritative readable | **doc 의 authoritative readable source** — 읽는 사람이 정식으로 참조하는 권위 readable 사본 + ArchitectAnalystAgent as-is 설계 확인 1차 lookup target | 추가 (본 Amendment 2) |

**ArchitectAnalystAgent dual-read path 의무**: as-is 설계 확인 시 (1) git read primary (LLM 친화 — 마크다운 plain text fenced code block diagram-as-code 정합) + (2) Confluence read fallback (LOSSY / ADF divergence 대비 — Epic-A 발견 LOSSY 1건 evidence). 양 channel divergence 감지 시 git source 가 authoritative (SoR-work invariant) — Confluence 측은 readable mirror 가 stale (sync agent re-trigger).

**sync direction = 단방향 git → Confluence** (ADR-100 §결정 1 disjoint axis 정합 — git = SoR-work / Confluence = SoR-docs readable mirror). write boundary = ADR-103 sync agent 단일 진입점 (Confluence → git 역방향 inbound webhook 0).

**sync source repo 다중성 (CFP-949 정합)**: per-plugin self-owned `docs/architecture/` 는 wrapper + 6 lane plugin repo 가 각각 SSOT (CFP-949 Sub-Epic 6 lane plugin self-owned architecture doc seed merged). sync source = wrapper repo + codeforge-{requirements, design, develop, review, test, pmo} repo. ADR-103 sync mechanism = 2-repo source resolver precedent 답습.

### Amendment 2 결정 2 — per-Epic 현행화 mandate (ArchitectAgent chief author 의무)

**의무**: 매 Epic merge 후 (또는 Phase 1 PR merge 시 — granularity 결정 = S3.5 / CFP-1429 lane gate wire 시점 결정) ArchitectAgent (chief author) 의 해당 plugin Living Architecture page 갱신 의무. 미반영 시 design lane verdict FIX.

**granularity 결정 위임**: Epic merge granularity vs Phase 1 PR merge granularity 의 trade-off = **Phase 2 lane gate wire 시점 (S3.5 / CFP-1429) 결정 위임** (본 Amendment 2 = mandate anchor only — mechanism 구체화 책임 위임). 후보:
- **Epic-level granularity**: 매 Epic close 후 (PMOAgent retro trigger 시점 정합 — ADR-045) — 갱신 비용 ↓ + per-Epic 시점 명확 / drift window ↑ (Epic 안 다중 Story 진행 중 stale)
- **Phase 1 PR-level granularity**: 매 Phase 1 PR merge 후 — drift window ↓ / 갱신 비용 ↑ (Story 마다 갱신)

**기존 §결정 4 "게이트 의무" 강화 명시화**: ADR-078 §결정 4 "설계 레인이 매 실행마다 Change Plan merge 를 `docs/architecture/` 4 영역에 반영. 미반영 시 design lane verdict FIX" 의무를 본 Amendment 2 = **per-Epic 시점 + ArchitectAgent chief author 책임 명시화** (의미 약화 0건 — invariant strengthen).

**mechanical actuator** (Phase 2 wire = S3.5 / CFP-1429 carrier):
- review-verdict-v4 v4.10 MINOR `living_architecture_updated: bool` field 신설
- lint workflow `templates/github-workflows/living-architecture-update.yml` (Phase 2 wire)
- bats fixture (Phase 2 wire)
- evidence-checks-registry warning-tier row (Phase 2 wire)
- label-registry-v2 `hotfix-bypass:living-architecture-update` family member (Phase 2 wire)

### Amendment 2 결정 3 — 5-anchor "시스템 현황" section schema (closed-enum, open_extension: false)

ADR-078 §결정 1 의 4 영역 closed-enum (모듈 / 경계 / 인터페이스 계약 / 데이터 흐름) 위에 **reading orientation layer 추가**. ArchitectAnalystAgent as-is 설계 확인 시 자연 lookup target 으로 작동하는 5-anchor mandatory section:

| # | anchor | 의미 | 외부 prior art (ADR-078 §컨텍스트 cross-ref) |
|---|---|---|---|
| 1 | **arc42 §3 — Context & Scope** | 시스템 외부 경계 + 외부 시스템 / actor / interface — 현 시스템이 무엇과 상호작용하는가 | arc42 12 섹션 template §3 (Context and Scope) verbatim subset |
| 2 | **arc42 §5 — Building Block View** | 모듈 / package / 내부 component decomposition — 현 시스템 구조 (ADR-078 §결정 1 4 영역 중 모듈 + 경계 instantiate) | arc42 12 섹션 template §5 (Building Block View) verbatim subset |
| 3 | **C4 Container** | runtime container (process / service / app) topology — deployment unit + 통신 protocol | C4 model (Simon Brown) Container level verbatim |
| 4 | **C4 Component** | container 내부 component (logical unit) — 책임 + 인접 component 관계 | C4 model (Simon Brown) Component level verbatim (Code level 제외 — ADR-078 §결정 1 anti-scope guard 정합) |
| 5 | **Open Decisions Pending** | ADR 미합의 + Wave 미작성 + placeholder 상태 집중 표시 — design lane 진입 시 모호성 즉시 visible | codeforge native (ArchitectPL design lane 진입 시 자연 lookup target) |

**4 영역 closed-enum 약화 0건 invariant**: 본 5-anchor schema = 4 영역 closed-enum (모듈 / 경계 / 인터페이스 계약 / 데이터 흐름) **위에 reading orientation layer 추가**. 4 영역 → 5-anchor 의 mapping:
- 모듈 ↔ arc42 §5 Building Block View + C4 Component
- 경계 ↔ arc42 §3 Context & Scope + C4 Container
- 인터페이스 계약 ↔ C4 Container (통신 protocol) — inter-plugin contract surface
- 데이터 흐름 ↔ C4 Container + C4 Component (runtime data flow)
- (신규 5번째 = Open Decisions Pending — 4 영역 외 design lane state visibility)

4 영역 closed-enum 의미 보존 + reading layer 추가 = additive extension (closed-enum 약화 0건).

**open_extension: false closed-enum invariant**: 5-anchor 확장 (예: arc42 §6 Runtime View / arc42 §8 Crosscutting Concepts 추가) 시 별도 CFP carrier 의무. 본 Amendment 2 = 5-anchor 박제 (사용자 발화 "한눈에 보기 좋게 정리하는 시스템 현황 section" 의 mechanism 정합 — 추가 anchor 시 "한눈" reading cost ↑).

### Amendment 2 결정 4 — diagram-as-code 의무 (Mermaid / PlantUML 우선, Confluence native macro 회피)

ADR-111 §결정 4 (diagram-as-code 의무) 의 Living Architecture page 영역 instantiate:

- **diagram-as-code 의무**: 5-anchor section schema (특히 arc42 §3 Context / arc42 §5 Building Block / C4 Container / C4 Component) 의 모든 diagram = Mermaid / PlantUML fenced code block (markdown source 안 직접 embed). Confluence native macro (drawio / Gliffy / Lucidchart) 회피.
- **근거**: (1) git SSOT 보존 — git diff / PR review 가능 (2) ADF round-trip lossy 회피 — Confluence storage format ↔ markdown round-trip safe (3) LLM 친화 — ArchitectAnalystAgent dual-read path git primary 정합 (text-based fenced code block 자연 parsing).

### Amendment 2 결정 5 — cross-link discipline (git anchor + Confluence anchor 양쪽 link 의무)

ADR-111 §결정 5 (cross-link discipline) 의 Living Architecture page 영역 instantiate:

- Living Architecture page git source frontmatter `confluence_anchor: <full URL>` field optional (frontmatter 부재 시 body cross-link footer)
- Living Architecture page 안 ADR / Story 인용 시 git anchor + Confluence anchor 양쪽 link 의무 (역방향 — Confluence Living Architecture page 안 ADR / Story 인용 시 동일)
- ADR-068 I-4 wording SSOT 확장 — single SSOT principle (양 channel 동시 가시화 의무 — 한쪽 link 만 노출 시 다른 channel staleness window 인지 비용 폭발)

### Amendment 2 결정 6 — mechanical_enforcement_actions append (declaration-only Wave 1)

`mechanical_enforcement_actions[]` 에 `living-architecture-update` entry append (declaration-only Wave 1 — 실 wire = Sub-C S3.5 / CFP-1429 carrier):

```yaml
mechanical_enforcement_actions:
  - architecture-drift          # Amendment 1 (CFP-923, 2026-05-18) — S4 carrier wire 완료
  - living-architecture-update  # Amendment 2 (CFP-1425, 2026-05-24) — Sub-C S3.5 / CFP-1429 carrier deferred-followup
```

**Phase 2 wire 영역** (Sub-C S3.5 / CFP-1429 carrier — 본 Amendment 2 scope 외):
- review-verdict-v4 v4.10 MINOR `living_architecture_updated: bool` field schema codify (ADR-008 §결정 2 MINOR 정합)
- `templates/github-workflows/living-architecture-update.yml` workflow + `scripts/check-living-architecture-update.sh` lint
- bats fixture
- evidence-checks-registry warning-tier row append
- `hotfix-bypass:living-architecture-update` label-registry-v2 family member

**ADR-082 §결정 6 + ADR-070 §D5 + ADR-111 §결정 5 retain pattern 답습**: Wave 1 declare / Wave 2 wire. pattern_count >= 2 재발 시 follow-up CFP MUST promote to blocking tier.

### Amendment 2 결정 7 — carrier-preserved 정정 (ADR-097 §결정 3 정합)

본 Amendment 2 가 ADR-078 의 4 영역 closed-enum 약화 0건 (additive extension only — 5-anchor section schema 가 4 영역 위에 reading orientation layer 추가). is_transitional retain `false` (permanent governance ratchet). sunset_justification: null (ratchet 강화 방향 — ADR-058 §결정 5 면제).

**약화 방향 evidence-gate** (ADR-058 §결정 5 + ADR-064 §결정 7 Amendment 8 evidence-gated symmetric ratchet 정합):
- 약화 방향 예시 (sunset_justification 의무): 5-anchor section schema 축소 / per-Epic 현행화 의무 약화 / Confluence mirror authoritative 격상 reversal / diagram-as-code 의무 제거 / cross-link discipline 의무 약화
- 강화 방향 예시 (sunset_justification 면제): 5-anchor 확장 (별도 CFP carrier 의무) / per-Epic 현행화 granularity 강화 (Phase 1 PR-level) / Confluence mirror authoritative 격상 강화 / diagram-as-code 의무 강화

### Amendment 2 즉시 효과 (Phase 1 PR merge 후)

1. ADR-078 frontmatter `amendment_log[]` row append (amendment 2, CFP-1425, 2026-05-24 KST) — `is_transitional: false` retain + `sunset_justification: null` retain.
2. ADR-078 frontmatter `mechanical_enforcement_actions[]` append `living-architecture-update` (declaration-only Wave 1).
3. ADR-078 frontmatter `related_stories[]` append CFP-1425 + CFP-1415 (Mega-Epic parent).
4. ADR-078 frontmatter `related_adrs[]` append ADR-100 (Confluence doc SSOT 인정) + ADR-103 (git→Confluence sync mechanism) + ADR-111 (Confluence-mirror classification policy SSOT).
5. Mega-Epic CFP-1415 scope_manifest `planned_adrs` 안 "ADR-078 Amendment 2" carrier_story field update (`CFP-1425`).

### Amendment 2 후속 Story 위임 (Sub-C bundle CFP-1418)

| Sub-story | Issue | scope | sequential trigger |
|---|---|---|---|
| **S3.2** | (별도 CFP carrier) | ADR-108 신설 — Confluence mirror sync mechanism 결정 영역 (ADR-103 위에서 Living Architecture page-specific sync 패턴) | S3.1 state dependency (본 Amendment 2 선행) |
| **S3.3** | CFP-1427 | 8 lane plugin Living Arch seed (`docs/architecture/codeforge-{requirements,design,develop,review,test,pmo,deploy,deploy-review}.md` + wrapper `docs/architecture/codeforge-family.md` 5-anchor expand) | S3.1 state dependency (5-anchor schema 선행) |
| **S3.4** | (별도 CFP carrier) | ArchitectAnalystAgent dual-read path 실 wire (codeforge-design plugin ArchitectAnalystAgent.md self-write 확장 + git primary + Confluence fallback) | S3.1+S3.3 state dependency (schema + seed 선행) |
| **S3.5** | CFP-1429 | mechanical wire — review-verdict-v4 v4.10 MINOR `living_architecture_updated: bool` + lint workflow + bats fixture + evidence-checks-registry row + hotfix-bypass label family member | S3.1+S3.3+S3.4 state dependency (mandate + seed + dual-read path 선행) |

## 거절된 대안

### 대안 1 — Story key 종속 architecture_doc

`docs/architecture/<KEY>.md` 형식으로 Story key 별 architecture doc 작성.

**거절 사유**: Story key 종속 시 Change Plan / Story file 와 도메인 disjoint 가 불명확 (Story 종속 = 1회 archive 영역 = change_plan / epic_results 영역). 본 ADR core invariant = **Story key 독립 + 누적 현재 상태** (Epic §확정 설계 §1 verbatim).

### 대안 2 — Wrapper canonical 1개 architecture_doc (각 plugin 분산 X)

`mclayer/plugin-codeforge/docs/architecture/codeforge-family.md` 1 file 에 7 plugin 전체 구조 통합.

**거절 사유**: 각 plugin = self-contained lane (codeforge-{requirements, design, develop, review, test, pmo}) 영역. wrapper canonical 1 file 시 cross-plugin sync 비용 ↑ + per-plugin lane self-write boundary 위배 (CFP-722 §13.A 정합). Q1 derived default = **각 plugin self-owned** (single_repo + dogfood variant 양 지원). User 정정 시 본 ADR Amendment carrier 발의.

### 대안 3 — 라인 수준 (클래스/함수) 허용 architecture_doc

closed-enum 4 영역 + 클래스 list + 함수 signature 까지 포함.

**거절 사유**: 라인 수준 허용 시 갱신 즉시 stale + "코드에 한 단계 더한 것" 전락 (Epic §확정 설계 §2 verbatim + §위험신호 §1 carrier). 도메인 disjoint 약화 (architecture_doc → code structure mirror = 무의미). anti-scope guard 강제로 retain.

### 대안 4 — Change Plan 본문 안에 architecture diff 통합 (별 doc type X)

`architecture_doc` 신설 대신 기존 Change Plan §N 안에 "architecture before / after" 섹션 추가.

**거절 사유**: Change Plan = Story별 변경 델타 = Story key 종속. 본 ADR core invariant = Story key 독립 누적 SSOT. 도메인 mismatch — Change Plan 누적 read 시 N Story 후 unbounded read cost.

## 해소 기준

**N/A — permanent policy.**

ADR-058 §결정 7 default presumption `false` (governance / security ADR) 정합. codeforge 설계 레인 영속 SSOT 유지 정책 영구 invariant — 약화 / 폐기 시점 비-가시.

**Amendment ratchet 차단** (ADR-058 §결정 5 정합): 본 ADR Amendment 시 `sunset_justification` 의무 (ratchet 약화 시 sunset_justification 3-tuple 필수).

## 관련 파일

### Phase 1 직접 touch (본 Story Phase 1 PR)

- [`docs/doc-locations.yaml`](../doc-locations.yaml) — architecture_doc 14번째 entry append
- [`docs/doc-location-registry.md`](../doc-location-registry.md) — auto-regen
- [`docs/adr/ADR-RESERVATION.md`](ADR-RESERVATION.md) — row 78 `reserved → active` 전환
- [`CLAUDE.md`](../../CLAUDE.md) — ADR 단락 + Doc Location Registry 단락 cross-ref

### 후속 Story 위임 (본 Story 비-touch)

- `docs/architecture/` — S2 (#920) seed 영역
- `templates/architecture-doc.md` — S2 (#920) template carrier
- `mclayer/plugin-codeforge-design/` — S3 (#921) lane gate carrier (현 `plugins/codeforge-design/`, 구 repo 삭제됨 2026-06-12)
- `scripts/check-architecture-drift.sh` — S4 (#923) lint carrier
- `templates/github-workflows/architecture-drift.yml` — S4 (#923) workflow carrier
- `docs/evidence-checks-registry.yaml` — S4 (#923) row append carrier

### Cross-ref ADR

- [ADR-041](ADR-041-doc-location-registry.md) — Doc Location Registry mechanism precedent
- [ADR-076](ADR-076-declarative-reconciliation-upgrade.md) — declarative reconciliation 3-layer pattern source
- [ADR-077](ADR-077-clarification-forced-reinvestigation-propagation.md) — Epic A enabler 관계 (본 ADR 본문 미수정)
- [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) — is_transitional:false permanent invariant 정합
- [ADR-040](ADR-040-worktree-convention.md) Amendment 3 §결정 7.D — `mechanical_enforcement_actions: []` declarative-only 정합
- [ADR-070](ADR-070-codex-verify-before-trust.md) — Touchpoint #2 mandatory dispatch (본 Phase 1 lane 진입 시 적용)
- [ADR-082](ADR-082-write-time-self-write-verification-mandate.md) — ArchitectAgent §3 / §7 / corpus enumeration verify
