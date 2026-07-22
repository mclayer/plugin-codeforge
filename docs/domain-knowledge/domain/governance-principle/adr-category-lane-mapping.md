---
kind: domain_fact
type: domain-knowledge
area: governance-principle
topic_slug: adr-category-lane-mapping
title: ADR Category → Lane Bucket Mapping Rule — Diátaxis quadrant secondary axis (DD-4)
status: Active
date: 2026-05-25
updated: 2026-07-18
carrier_story: CFP-1523
parent_carrier: CFP-1493 (Sub-B S2.3 partial complete, PR #1520 MERGED — 잔여 real backfill 영역)
tags:
  - lane-filter-rule
  - diataxis-quadrant
  - confluence-ia-tree
  - adr-category-enum
  - case-fold-normalize
  - closed-set-invariant
related_adrs:
  - ADR-054   # doc-only fast-path
  - ADR-058   # ADR sunset criteria mandate (§결정 5 sunset_justification + is_transitional: false governance `ratchet` 강화)
  - ADR-060   # evidence-enforceable promotion framework (declarative_layer Wave 1 → 별 Wave 2 wire)
  - ADR-064   # decision principle mandate (§결정 5 CFP scope unitary)
  - ADR-068   # boundary completeness invariants (I-3 unconditional vs conditional + I-4 wording SSOT case-normalization)
  - ADR-076   # declarative reconciliation upgrade flow (drift detection cross-ref)
  - ADR-082   # write-time self-write verification mandate (§결정 1 layer 1-A ADR corpus direct grep)
  - ADR-091   # ArchitectLane DDD vocabulary governance (§결정 1/2/4 Published Language content duplication 금지 + §3.1 deputy mandate)
  - ADR-100   # Confluence doc SSOT recognition (SoR-docs layer scope)
  - ADR-101   # verify-before-trust Confluence REST (Phase 2 execution time dual-layer verify mandatory)
  - ADR-103   # git→Confluence sync mechanism (MCP-direct deviation channel governance baseline)
related_stories:
  - CFP-1523
  - CFP-1493
  - CFP-1494
  - CFP-1495
  - CFP-1086   # 4-way RACI matrix → 3-way (S5 deputy-mandate scope)
  - CFP-1126   # AggregateArch + ModuleArch 통합 (Amendment 10) — ModuleArch unified mandate primary advocate
deferred_followup_cfps:
  - CFP-2615  # SUPERSEDED by CFP-2680 (ADR-153) — membership-enforcement 를 기존 required doc-frontmatter surface(check_doc_frontmatter.py CATEGORY_VALID) 위 fail-closed 로 실현. standalone warning-tier lint 미빌드(membership-scoped supersede, coverage/mapping-accuracy 축 OOS). shrink carrier=CFP-2682 → 실현 CFP-2753 (정규화+grandfather machinery 은퇴 완료)
  - FU-1523-2  # Confluence IA tree drift detection lint (scripts/check-confluence-ia-drift.sh + 24h cron + Issue auto-create, S2.5 lineage)
ddd_layer:
  bounded_context: codeforge-governance
  ddd_terms:
    - "Published Language"        # docs/confluence-ia-tree.yaml + 본 file = codeforge governance BC published language (consumer-facing IA tree SSOT)
    - "Open Host Service (OHS)"   # Confluence space CFP = OHS pattern (consumer single entry point governance corpus 접근)
  glossary_ref: docs/glossary.md
is_transitional: false
sunset_criteria: N/A — permanent governance `ratchet` (ADR-058 §결정 5 정합, lane mapping rule SSOT = closed-set invariant)
---

# ADR Category → Lane Bucket Mapping Rule — Diátaxis quadrant secondary axis (DD-4)

## 정의

본 file = codeforge governance corpus (ADR 117 file + inter-plugin-contracts 30 file + Consumer Guide 1 file = 148 legacy page) Confluence space `CFP` IA tree migration 시 **category → lane bucket deterministic mapping rule SSOT**.

핵심 정의 3종:

- **18 unique enum** (literal `yaml closed_enum` entries) = ADR corpus frontmatter `category:` field 안 18 distinct case-sensitive string (`docs/confluence-ia-tree.yaml` `lane_mapping_rule.closed_enum:` 18-entry literal SSOT)
- **16 effective canonical buckets** (case-fold normalize) = lowercase canonical normalization 후 2 쌍 case-collision merge (`Architecture`(5)+`architecture`(3) → `architecture` 8 / `Process`(1)+`process`(1) → `process` 2) = 16 distinct canonical bucket
- **6 lane bucket** = Confluence space CFP 안 lane plugin 별 parent page (codeforge-design / codeforge-develop / codeforge-review / codeforge-test / codeforge-pmo / codeforge-requirements) + cross-cutting wrapper-governance bucket + cross-cutting inter-plugin-contracts Registry bucket (구 deploy·deploy-review bucket = ADR-121 / CFP-2782 배포 2 lane 물리 제거)

**Diátaxis quadrant secondary axis (DD-4)**: primary axis = Diátaxis quadrant (Cognition+Acquisition / Cognition+Application / Action+Acquisition / Action+Application), secondary axis = lane bucket (mechanical filter rule, per-ADR ad-hoc annotation 0).

## 컨텍스트

**Origin**: CFP-1493 Sub-B S2.3 partial complete (PR #1520 MERGED) 후 잔여 148 page real backfill carrier (CFP-1523). 4 DERIVED DEFAULT (DD-1 Diátaxis quadrant axis / DD-2 partial defer carrier scope 보존 / DD-3' MCP cascade 6-call atomic / DD-4 category → lane mapping rule SSOT) 의 DD-4 SSOT body.

**Ground truth note (F-DR-001 verify-before-trust)**: Story §1 USER-UTTERANCE-VERBATIM "142 page (ADR 111 + IPC 30 + Consumer Guide 1)" = stale local main 시점 사실 (Phase 0 시점 local cwd file count 111). Ground truth verified-via `git -C <wrapper-worktree> ls-files docs/adr/ADR-*.md | wc -l = 117` (2026-05-25T13:30:00+09:00 KST) — ADR 117 file + IPC 30 file + Consumer Guide 1 file = 148 legacy page. Pivot 정정 = Story §2.1 row 4 (verify-before-trust pivot row). Story §1 IMMUTABLE 정합 (story-section-1-immutable.yml).

**Consumer mental model 정합**: codeforge consumer project 의 governance corpus 학습자 (Confluence space CFP entry point) — lane 별 ADR navigate. flat `docs/adr/` (117 file) 안 lane-irrelevant ADR 가 lane bucket 안 숨겨짐 (per-ADR ad-hoc annotation 0, category SSOT = automated lane filter).

**Maintenance sustainability**: 신규 ADR 작성 시 frontmatter `category:` field 만 채우면 자동 lane bucket 분배 (option (b) 채택 — option (a) ADR frontmatter `lane:` field 신설 = 0/117 greenfield 회피).

**Authority (Who decides) — DDD pattern mapping**:

Primary advocate = `ModuleArchitectAgent` (CFP-1126 unified mandate — module-level + aggregate-level boundary 통합). boundary axis 위협 (148 page lane bucket allocation = code module-level boundary placement rule 영역).

**chief tie-break ladder applied** (ADR-068 Amendment 2 / CFP-1086 4-way RACI → 3-way):

- D-1/D-2/D-3 = Stage 1 (primary axis matrix) — ModuleArch primary single-axis
- D-4 (CI lint mechanism) = Stage 2 (RACI lookup) — Cell 2.2 ModuleArch × InfraOp → InfraOp = CONSULT, ArchitectAgent self-handle
- D-5 (dry-run gate mandate) = Stage 2 — Cell 3.2 ModuleArch × TestContract → TestContract = CONSULT, ArchitectAgent self-handle

Axis disjoint 정합: 5 decision 모두 ModuleArch primary axis + 2 decision (D-4/D-5) consult overlay → boundary axis 단일 advocate invariant.

**SSOT location precedence (ADR-091 §결정 4)**: 본 file = lane_mapping_rule narrative SSOT. cross-ref pointer locations:

| Location | Role | Content |
|---|---|---|
| `docs/domain-knowledge/domain/governance-principle/adr-category-lane-mapping.md` (본 file) | **SSOT primary (narrative body)** | mapping rule 전체 정의 + rationale + governance `ratchet` ("강화 방향만 허용 + 약화 차단" — ADR amendment top-down rule) |
| `docs/confluence-ia-tree.yaml` `lane_mapping_rule:` field | **cross-ref pointer (yaml field)** | `ssot_ref: docs/domain-knowledge/domain/governance-principle/adr-category-lane-mapping.md` + `closed_enum: [<16 normalized enum>]` field 만 (narrative body 영역 0) |

Published Language content duplication 금지 (ADR-091 §결정 4) 정합 — 단일 owner location.

## 핵심 규칙

### 규칙 1 — case-normalization invariant (ADR-068 I-4 wording SSOT, F-DR-004 wording clarification)

- 18 unique enum (case-sensitive) ↔ 16 effective canonical buckets (case-fold) 분리
- **CFP-2615 lint algorithm**: input frontmatter value 를 lowercase normalize 한 후 closed_enum membership check (case-fold during check). `case_fold_during_check: true` field (yaml lane_mapping_rule) = mechanical anchor
- Capitalized 형식 legacy ADR frontmatter retain (rewrite = 별 carrier). lowercase canonical 의무 (신규 ADR 작성 시)

### 규칙 2 — 16 normalized enum mapping table

| # | Category (lowercase canonical) | Count | Primary lane bucket | Cross-ref lane buckets | Rationale |
|---|---|---|---|---|---|
| 1 | `governance` | 44 | **wrapper-governance** bucket (cross-cutting, page_id 2163807) | 모든 lane bucket ADR anchor cross-ref note | Cross-cutting fallback rule (D-3) — Published Language content duplication 금지 + Tertiary stakeholder (cross-lane corpus 통합 view) entry point |
| 2 | `security` | 2 | **codeforge-review** bucket ADR anchor (page_id 2065761) | codeforge-design ADR anchor (2163571) cross-ref | SecurityArch primary deputy (ADR-091 §3.1) — design lane threat boundary + review lane security-test |
| 3 | `orchestration` | 7 | **codeforge-design** bucket ADR anchor (page_id 2163571) | codeforge-pmo bucket (2130897) cross-ref | Orchestrator-level mechanism = design lane primary |
| 4 | `tooling-infrastructure` | 8 | **codeforge-design** bucket ADR anchor (page_id 2163571) | codeforge-develop ADR anchor (2098305) cross-ref | InfraOperationalArch deputy (ADR-091 §3.1) — design primary + implementation cross-ref |
| 5 | `lifecycle` | 2 | **wrapper-governance** bucket (cross-cutting) | codeforge-design bucket ADR anchor cross-ref | Cross-cutting fallback — process governance lifecycle (paradigm replacement etc., lane-agnostic policy) |
| 6 | `dogfood-out` | 0 (예약) | **wrapper-governance** bucket (cross-cutting) | 모든 lane bucket cross-ref note | Cross-cutting fallback — lane-agnostic governance pattern |
| 7 | `agent-tier` | 0 (예약) | **codeforge-design** bucket ADR anchor (page_id 2163571) | 모든 lane bucket cross-ref note | agent model selection policy = design lane primary (ADR-042 family) |
| 8 | `process` (incl. `Process`) | 2 (1+1 collision) | **wrapper-governance** bucket (cross-cutting) | codeforge-pmo bucket cross-ref | Cross-cutting fallback — workflow process governance, PMO cross-ref |
| 9 | `architecture` (incl. `Architecture`) | 8 (3+5 collision) | **codeforge-design** bucket ADR anchor (page_id 2163571) | 모든 lane bucket cross-ref note | ModuleArch unified mandate primary (CFP-1126) — module/aggregate boundary advocacy = design lane primary |
| 10 | `agent-design` | 4 | **codeforge-design** bucket ADR anchor (page_id 2163571) | 모든 lane bucket cross-ref note | agent design = design lane primary (ArchitectPL + deputy roster ownership) |
| 11 | `orchestration-discipline` | 3 | **codeforge-design** bucket ADR anchor (page_id 2163571) | codeforge-pmo bucket cross-ref | Orchestrator discipline = design lane primary + PMO governance cross-ref |
| 12 | `workflow-policy` | 5 | **codeforge-pmo** bucket ADR anchor (page_id 2130897) | wrapper-governance bucket cross-ref (cross-cutting policy) | workflow policy = PMO lane primary (GitOpsAgent ownership) |
| 13 | `orchestrator-policy` | 1 | **wrapper-governance** bucket (cross-cutting) | codeforge-design bucket ADR anchor cross-ref | Cross-cutting fallback — Orchestrator policy = lane-agnostic governance |
| 14 | `audit` | 1 | **wrapper-governance** bucket (cross-cutting) | codeforge-pmo bucket cross-ref | Cross-cutting fallback — audit policy = lane-agnostic governance + PMO retro audit cross-ref |
| 15 | `team & process` (canonical `Team & Process` retain) | 27 | **wrapper-governance** bucket (cross-cutting) | codeforge-pmo bucket cross-ref (cross-cutting workflow) | Cross-cutting fallback — team workflow process governance (workflow-policy super-class) |
| 16 | `plugin architecture` (canonical `Plugin Architecture` retain) | 1 | **codeforge-design** bucket ADR anchor (page_id 2163571) | 모든 lane bucket cross-ref note (cross-cutting plugin architecture) | ModuleArch unified mandate primary (CFP-1126) — plugin architecture = design lane primary |
| 17 | `plugin distribution & consumer onboarding` (canonical retain) | 2 | **wrapper-governance** bucket (cross-cutting) | wrapper-governance bucket (cross-cutting) | Cross-cutting fallback — 배포는 consumer 위임 (ADR-121 / CFP-2782 deploy lane 물리 제거, 구 ADR-087/088 Superseded) |
| 18 | `infrastructure` (canonical `Infrastructure` retain) | 1 | **codeforge-design** bucket ADR anchor (page_id 2163571) | codeforge-develop bucket cross-ref | InfraOperationalArch deputy (ADR-091 §3.1) — design primary |

**Total ADR coverage**: 117 ADR file 안 110+ file `^category:` field 보유. 7 file `^category:` field 부재 (early ADRs) = 별 retroactive backfill carrier (본 carrier scope 외).

### 규칙 3 — inter-plugin-contracts (30 file) + Consumer Guide (1 file) mapping

| File 영역 | Primary lane bucket | Rationale |
|---|---|---|
| `docs/inter-plugin-contracts/` 30 file (7 contract: review_verdict / requirements_output / design_output / develop_output / test_verdict / pmo_output / git_ops_event + 7 registry: label-registry / debate-protocol / evidence-check-registry / severity-propagation / parallel-dispatch-protocol-v1 / imperative-walker-protocol-v1 + comment-prefix / fix-event) | **cross-cutting** bucket (page_id 2130942 `inter-plugin-contracts Registry`) — D-3 cross-cutting fallback | 모든 IPC = lane-agnostic published language (ADR-091 §결정 4 cross-plugin shared kernel). 7 contract = canonical_repo per-plugin SSOT (해당 lane bucket IPC sub-anchor cross-ref) but Confluence IA bucket primary = cross-cutting (consumer mental model 정합). |
| Consumer Guide page (1 file) | **wrapper-governance** bucket (page_id 2163807) | how-to quadrant (Diátaxis Action+Application) — consumer-facing single entry point. CFP-1493 partial 산출 재사용 — wrapper-governance bucket primary, lane-agnostic. |

### 규칙 4 — Multi-lane ADR / cross-cutting ADR edge cases (Story §5.3 정합)

본 mapping rule = primary owner lane bucket + cross-ref note 패턴. 3 edge case:

1. **Multi-lane ADR** (예: ADR-082 verify-before-trust 4-layer = governance + 모든 lane 정합) — primary = wrapper-governance bucket (D-3 fallback) + 모든 lane bucket ADR anchor cross-ref note
2. **lane-agnostic IPC** (예: `review-verdict-v4` = design-review + code-review + security-test 3 lane 공통) — shared kernel bucket (cross-cutting `inter-plugin-contracts Registry`) primary + 해당 lane bucket IPC sub-anchor cross-ref
3. **ADR cross-cutting** (예: ADR-091 DDD vocabulary = ArchitectLane primary but 다른 lane 도 cross-ref) — primary owner lane bucket (예: 설계 lane) anchor + cross-ref note

### 규칙 5 — closed-set invariant (ADR-058 §결정 5 + ADR-064 §결정 5)

본 mapping rule = **18 unique enum (case-normalized 16) closed-set** (`open_extension: false`). 신규 ADR frontmatter `category:` field = 본 16 enum 안 의무.

**Rationale**: CFP-1525 schema drift 패턴 답습 차단 (closed-enum order drift = 14 occurrence sentinel evidence). 신규 enum 출현 시 별 ADR Amendment 의무 (`ratchet` 강화 evidence 동반).

**Future Amendment procedure (별 ADR Amendment)**: 신규 category enum 도입 결정 시 다음 절차 의무:

1. 별 sub-CFP 발의 + ADR-058 §결정 5 sunset_justification 3-tuple (metric / who / how) 명시
2. 본 file Amendment N (lowercase canonical enum 추가 + Primary lane bucket + cross-ref + rationale)
3. `docs/confluence-ia-tree.yaml` `lane_mapping_rule.closed_enum:` field row append + `schema_version` MINOR bump
4. CFP-2615 `scripts/check-adr-category-lane-coverage.sh` lint Amendment row coverage 자동 검증 (실 wire 후)
5. ADR-091 §결정 4 Published Language content duplication 금지 invariant 정합 — 단일 owner location 보존

### 규칙 6 — Diátaxis quadrant alignment (Story AC-4)

| Anchor | Diátaxis quadrant | Consumer mental model |
|---|---|---|
| ADR anchor (lane bucket 안) | **Explanation** (Cognition+Acquisition) | 학습자 — design decision rationale 학습 |
| IPC anchor (cross-cutting Registry 안 + 해당 lane bucket sub-anchor) | **Reference** (Cognition+Application) | 구현자 — contract schema lookup |
| Consumer Guide bucket (wrapper-governance) | **How-to** (Action+Application) | 신규 consumer — 플러그인 설치 task-oriented |
| Living Architecture anchor (lane bucket 안, lane plugin self-owned) | **Explanation** (primary) | 운영자 — arc42 §3+§5+C4 Container+Component 학습 |

### 규칙 7 — Cascade execution plan (Story AC-2/AC-3 cross-ref)

Phase 2 PR 안 6 MCP call atomic execution:

| Step | MCP Call | Target | parentId |
|---|---|---|---|
| 1 | `getConfluencePage(id="2097153")` | Legacy `adr` bucket (root) | (fetch body verbatim) |
| 2 | `updateConfluencePage(id="2097153", parentId="<lane_bucket_id_per_category>", body=<verbatim>)` | Move `adr` bucket → lane bucket per primary mapping | per 규칙 2 표 row 1-18 |
| 3 | `getConfluencePage(id="2129949")` | Legacy `inter-plugin-contracts` bucket (root) | (fetch body verbatim) |
| 4 | `updateConfluencePage(id="2129949", parentId="2130942", body=<verbatim>)` | Move IPC bucket → cross-cutting `inter-plugin-contracts Registry` | per 규칙 3 표 row 1 |
| 5 | `getConfluencePage(id="<consumer_guide_id>")` | Legacy Consumer Guide bucket (root) — Phase 2 execution time discovery | (fetch body verbatim) |
| 6 | `updateConfluencePage(id="<consumer_guide_id>", parentId="2163807", body=<verbatim>)` | Move Consumer Guide → wrapper-governance bucket | per 규칙 3 표 row 2 |

**Cascade primitive** (Confluence native): parent page move → children parent_id 변경 0 + 새 위치 자동 따라감 (Atlassian Community cross-ref, Story §2.1 row 3 `[verified]`). 148 children 자동 cascade (F-DR-001 — ADR 117 + IPC 30 + Consumer Guide 1 ground truth).

**Dry-run gate (D-5 mandate)**: Phase 2 PR 시작 시 1 page dry-run pre-check 의무 (test space or throwaway page) — cascade preserve 확인 후 3 root parent atomic 진입.

**Fallback (D-5 escape hatch)**: cascade 실패 시 REST direct `PUT /wiki/rest/api/content/{id}/move/{position}/{targetId}` per-page batch (body 미요구 path param only) — 284 MCP call worst-case 시나리오. ADR-061 §결정 1 multi-line Python 외부 file 의무.

**ADR-101 dual-layer verify** (Story §4.3.1 row 7b governance baseline): Phase 2 execution time MCP `getConfluencePage` / `updateConfluencePage` / `getPagesInConfluenceSpace` 응답 ground-truth dual-layer verify 의무.

### 규칙 8 — Deferred-followup CFP (CFP-2615 / FU-1523-2 declare)

#### CFP-2615 — CI lint mechanism mechanical wire — **SUPERSEDED by CFP-2680 (ADR-153)**

> **Superseded (2026-07-14, membership-scoped)**: CFP-2680 (ADR-153) 이 본 CFP-2615 membership-enforcement intent 를 **기존 required doc-frontmatter surface** (`scripts/lib/check_doc_frontmatter.py` `CATEGORY_VALID` block) 위 **fail-closed** 로 실배선했다. 아래 원안(standalone warning-tier `scripts/check-adr-category-lane-coverage.sh` + 전용 workflow)은 **미빌드** — CFP-2591 §2.4 "warning 강제피로" 회피 위해 required 표면 편승으로 대체. supersede 는 **membership-scoped**: category→lane *coverage/mapping-accuracy* 축은 OOS 유지(본 게이트 미강제, over-claim 금지 — ADR-119 / ADR-153 §결정 3). 선재 compound 3건(ADR-131/132/133)은 `FROZEN_BASELINE_3` grandfather(shrink-only)로 임시 격리됐다가 **CFP-2753 (ADR-153 Amendment 1, 2026-07-18)** 이 규칙4대로 정규화(131→`governance` / 132→`security` / 133→`orchestration`) + secondary 축 본문 cross-ref 보존 후 allowlist 전량 shrink → grandfather machinery 은퇴(anti-regression guard 로 대체). durable defense = fail-closed CATEGORY_VALID membership 무변경.

**원안 Scope (미빌드)**: `scripts/check-adr-category-lane-coverage.sh` warning tier lint + `templates/github-workflows/adr-category-lane-coverage.yml` workflow + `docs/evidence-checks-registry.yaml` row append + `hotfix-bypass:adr-category-lane-coverage` family member append.

**실현 Mechanism (CFP-2680)**: frontmatter `category:` 값(case-fold)이 `docs/confluence-ia-tree.yaml lane_mapping_rule.closed_enum`(동적 read) 안에 존재 여부를 기존 required 게이트 `doc frontmatter schema (CFP-28 — strict)` 표면에서 fail-closed verify. 미존재 시 exit 1 + 검출값 + `ADR Amendment` + `sunset_justification` 안내.

**ADR-060 framework Wave 1 → Wave 2 wire pattern**: declarative_layer 본 carrier (CFP-1523) → mechanical wire 별 sub-CFP (CFP-2615) → **required-surface fail-closed 실배선 (CFP-2680 / ADR-153, warning→required 강화)**.

#### FU-1523-2 — Confluence IA tree drift detection lint

**Scope**: `scripts/check-confluence-ia-drift.sh` warning tier lint + `templates/github-workflows/confluence-ia-drift-detection.yml` 24h cron + workflow_dispatch + Issue auto-create + `hotfix-bypass:confluence-ia-drift-detection` family member append.

**Mechanism**: git tracked `docs/confluence-ia-tree.yaml` (desired state) ↔ Confluence space CFP actual parent_id state (current state) drift 검출. drift > 7 day 시 Issue auto-create.

**ADR-076 declarative reconciliation pattern 정합** (desired/current/converge). `marketplace-drift-detection.yml` pattern 답습.

## 경계

### Scope in (본 mapping rule 적용 영역)

- ADR 117 file frontmatter `category:` field 안 18 unique enum (case-normalized 16) → lane bucket allocation
- inter-plugin-contracts 30 file → cross-cutting `inter-plugin-contracts Registry` bucket primary
- Consumer Guide 1 file → wrapper-governance bucket primary
- Multi-lane ADR / lane-agnostic IPC / ADR cross-cutting edge case 3종 → primary owner + cross-ref note 패턴
- 신규 ADR 작성 시 frontmatter `category:` lowercase canonical enum 의무 (closed-set invariant)
- 신규 enum 도입 결정 시 별 ADR Amendment + sunset_justification 3-tuple 의무

### Scope out (본 mapping rule 영역 외)

- **ADR 신설 0** — 본 carrier (CFP-1523) = doc-only fast-path (ADR-054), 별 ADR Amendment 0건 (governance `ratchet` 강화 영역 외)
- **RDB OLTP 영역 외** — Aggregate boundary / 트랜잭션 경계 / Alembic 정책 = ModuleArch unified mandate but RDB OLTP-specific 결정 영역 (CFP-1126 ModuleArch boundary axis 단일 advocate 흡수, 본 lane mapping 영역 외)
- **Live touching N/A** — 본 carrier = governance corpus IA tree migration, live ordering / live deploy 영역 외 (LiveOps/LiveOrdering deputy CONDITIONAL spawn 0건)
- **production cutover N/A** — 본 carrier = doc-only migration, ProductionEvidenceDeputy spawn 영역 외 (codeforge-design CONDITIONAL deputy scope 외, ADR-072)
- **per-ADR `lane:` field 신설 = reject** — option (a) (per-ADR ad-hoc annotation) = 0/117 greenfield 회피, category field SSOT = automated lane filter 채택 (option (b))
- **legacy ADR frontmatter rewrite = 별 carrier** — Capitalized 형식 (Architecture / Process / Team & Process / Plugin Architecture / Infrastructure) retain, lowercase canonical normalize 의무 = 신규 ADR 작성 시점만
- **`docs/adr/` 7 file `^category:` field 부재** = early ADRs retroactive backfill = 별 carrier (본 scope 외)
- **mechanical wire (CFP-2615 / FU-1523-2 실 implementation)** = 별 sub-CFP carrier (declarative_layer 본 file 만, ADR-060 framework Wave 1 → Wave 2 wire pattern)

## 관련 ADR

- **ADR-054** (doc-only fast-path) — 본 carrier (CFP-1523) classification 근거 (SSOT 문서 변경 + 기존 ADR Amendment 0 + src/tests 무변경)
- **ADR-058** (ADR sunset criteria mandate) §결정 5 — sunset_justification 3-tuple 의무 (`ratchet` 약화 evidence-gated, 본 file `is_transitional: false` permanent governance `ratchet`)
- **ADR-060** (evidence-enforceable promotion framework) — CFP-2615 / FU-1523-2 declarative_layer → mechanical wire Wave 1 → Wave 2 pattern 답습
- **ADR-064** (decision principle mandate) §결정 5 — CFP scope unitary (16-enum closed-set 안 신규 enum 도입 = 별 sub-CFP 의무)
- **ADR-068** (boundary completeness invariants) I-3 unconditional vs conditional guard placement + I-4 wording SSOT case-normalization invariant
- **ADR-076** (declarative reconciliation upgrade flow) — FU-1523-2 desired/current/converge pattern + `marketplace-drift-detection.yml` byte-pattern 답습
- **ADR-082** (write-time self-write verification mandate) §결정 1 layer 1-A — 본 file `^category:` field 117 ADR corpus direct grep verified (`git -C <wrapper-worktree> ls-files docs/adr/ADR-*.md | wc -l = 117`)
- **ADR-091** (ArchitectLane DDD vocabulary governance) §결정 1/2/4 — DDD vocabulary governance + Published Language content duplication 금지 + §3.1 SecurityArch / InfraOperationalArch / ModuleArch deputy mandate cross-ref
- **ADR-100** (Confluence doc SSOT recognition) — SoR-docs layer scope 본 file = codeforge governance BC published language
- **ADR-101** (verify-before-trust Confluence REST) — Phase 2 execution time MCP `getConfluencePage` / `updateConfluencePage` / `getPagesInConfluenceSpace` 응답 dual-layer verify 의무
- **ADR-103** (git→Confluence sync mechanism) — MCP-direct deviation channel governance baseline (본 carrier = MCP-direct cascade 6 call atomic 채택, CI mirror loop 영역 외)

## 변경 이력

| 일자 (KST) | 변경 | Carrier | 비고 |
|---|---|---|---|
| 2026-05-25 | 신설 (DD-4 SSOT body — 18 unique enum × 16 effective canonical buckets × 8 lane bucket mapping + cross-cutting fallback + case-fold normalize + closed-set invariant + Diátaxis quadrant alignment) | CFP-1523 | parent_carrier CFP-1493 Sub-B S2.3 partial complete (PR #1520 MERGED) 잔여 real backfill carrier. ground truth verified `git ls-files docs/adr/ADR-*.md = 117` (2026-05-25T13:30:00+09:00 KST). FIX iter 2 — frontmatter `kind: domain_fact` + `area: governance-principle` + `topic_slug: adr-category-lane-mapping` + `updated: 2026-05-25` schema 정합 + 6 section schema (정의 / 컨텍스트 / 핵심 규칙 / 경계 / 관련 ADR / 변경 이력) 재배치 (정보 손실 0, 기존 mapping body 전부 보존). |
| 2026-07-14 | 규칙 8 CFP-2615 sub-section supersede 반영(CFP-2680/ADR-153 이 membership-enforcement 를 기존 required doc-frontmatter surface CATEGORY_VALID 위 fail-closed 로 실현, standalone warning-tier lint 미빌드 = membership-scoped supersede) + frontmatter deferred_followup_cfps CFP-2615 항목 정합 | CFP-2680 | 3-surface 정합(confluence-ia-tree.yaml deferred_followup_lint + 본 file 규칙 8 + frontmatter) — one-place-only=SSOT drift 회피(census-floor). coverage/mapping-accuracy 축 OOS 유지. shrink carrier CFP-2682. |
| 2026-07-18 | 규칙 8 grandfather 은퇴 반영(CFP-2753/ADR-153 Amd1 이 compound 3건 ADR-131→governance/132→security/133→orchestration 정규화 + secondary cross-ref 보존 후 FROZEN_BASELINE_3 allowlist 전량 shrink → machinery 은퇴, anti-regression guard 대체) + frontmatter deferred_followup_cfps 주석·shrink_carrier 정합 | CFP-2753 | 3-surface 정합(confluence-ia-tree.yaml shrink_carrier + 본 file 규칙 8/frontmatter + ADR-153 Amd1) — census-floor SSOT drift 회피. durable defense = fail-closed CATEGORY_VALID membership 무변경. |

## Cross-ref summary

- **Story CFP-1523 §3.0 D-1/D-2/D-3** — 본 file = SSOT primary location 결정 산출 (governance-principle/ domain-knowledge body)
- **Story CFP-1523 §3.1** — 본 file 규칙 2 mapping table = Story §3.1 verbatim duplicate avoided (Story = section anchor pointer + reasoning, 본 file = SSOT primary)
- **`docs/confluence-ia-tree.yaml` `lane_mapping_rule:` field** — `ssot_ref:` cross-ref pointer + `closed_enum: [<16 enum>]` field
- **CFP-1493 PR #1520 MERGED** — parent carrier (S2.3 partial complete, 3 cross-cutting bucket 신설 — wrapper-governance / ADR Registry / inter-plugin-contracts Registry page_id 활용)
- **ADR-091 §결정 1/2/4** — DDD vocabulary governance + Published Language content duplication 금지 invariant
- **CFP-1126 / ADR-042 Amendment 10** — ModuleArch unified mandate primary advocate (boundary axis 단일 advocate)

