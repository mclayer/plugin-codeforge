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
related_stories:
  - CFP-919  # 본 Story carrier — Story-1 (anchor only, ADR + doc 타입 신설)
  - CFP-756  # Epic B parent — 설계 레인 영속 구조 설계 문서 유지 정책
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
related_files:
  - docs/doc-locations.yaml                # architecture_doc 14번째 entry append
  - docs/doc-location-registry.md          # auto-regen (round-trip identical)
  - docs/adr/ADR-RESERVATION.md            # row 78 `reserved → active` 전환
  - CLAUDE.md                              # ADR 단락 + Doc Location Registry 단락 cross-ref
  - docs/architecture/                     # 후속 Story-2 (#920) seed 영역 (본 Story 비-생성)
  - templates/architecture-doc.md          # 후속 Story-2 (#920) template carrier (본 Story 비-생성)
  - scripts/check-architecture-drift.sh    # 후속 Story-4 (#923) lint carrier (본 Story 비-생성)
  - templates/github-workflows/architecture-drift.yml  # 후속 Story-4 (#923) workflow carrier (본 Story 비-생성)
mechanical_enforcement_actions:
  - architecture-drift   # Amendment 1 (CFP-923, 2026-05-18) — S4 carrier wire 완료 (ADR-060 framework warning-tier entry, hotfix-bypass:architecture-drift 43번째 family member)
# Amendment 1 (CFP-923, 2026-05-18) — S4 carrier (architecture_doc drift mechanical lint) wire
# 완료. ADR-040 Amendment 3 §결정 7.D self-application invariant 충족 (declared → active wire).
# 후속 mechanism (S3 lane gate verdict carrier `architecture_doc_updated: bool` design-output-v2
# v2.4 + S2 template schema lint) 은 별 carrier 발의 영역 — 본 entry 와 disjoint axis.
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
- `mclayer/plugin-codeforge-design/` — S3 (#921) lane gate carrier
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
