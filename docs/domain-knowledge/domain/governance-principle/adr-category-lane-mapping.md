---
title: ADR Category → Lane Bucket Mapping Rule SSOT
status: Active
category: governance
created: 2026-05-25
carrier_story: CFP-1523
parent_carrier: CFP-1493 (Sub-B S2.3 partial complete, PR #1520 MERGED — 잔여 real backfill 영역)
related_adrs:
  - ADR-054  # doc-only fast-path
  - ADR-058 §결정 5  # sunset_justification + is_transitional: false governance ratchet 강화
  - ADR-060  # evidence-enforceable promotion framework (declarative_layer Wave 1 → 별 Wave 2 wire)
  - ADR-064 §결정 5  # CFP scope unitary
  - ADR-068 I-4  # wording SSOT (case-normalization invariant)
  - ADR-068 I-3  # unconditional vs conditional guard placement intent
  - ADR-076  # declarative reconciliation upgrade flow (drift detection cross-ref)
  - ADR-082 §결정 1 layer 1-A  # write-time self-write verification mandate (ADR corpus direct grep verified)
  - ADR-091 §결정 1/2/4  # DDD vocabulary governance + Published Language content duplication 금지
  - ADR-091 §3.1  # SecurityArch / InfraOperationalArch / ModuleArch deputy mandate cross-ref
  - ADR-100  # Confluence doc SSOT 인정 (SoR-docs layer scope)
  - ADR-101  # verify-before-trust Confluence REST (Phase 2 execution time dual-layer verify mandatory)
  - ADR-103  # git→Confluence sync mechanism (MCP-direct deviation channel governance baseline)
  - CFP-1126  # AggregateArch + ModuleArch 통합 (Amendment 10) — ModuleArch unified mandate primary advocate
  - CFP-1086  # 4-way RACI matrix → 3-way (S5 deputy-mandate scope)
deferred_followup_cfps:
  - FU-1523-1  # scripts/check-adr-category-lane-coverage.sh warning tier lint 실 wire + evidence-checks-registry yaml row append (declarative_layer → mechanical wire)
  - FU-1523-2  # Confluence IA tree drift detection lint (scripts/check-confluence-ia-drift.sh + 24h cron + Issue auto-create, S2.5 lineage)
ddd_layer:
  bounded_context: codeforge-governance
  ddd_terms:
    - "Published Language"        # docs/confluence-ia-tree.yaml + 본 file = codeforge governance BC published language (consumer-facing IA tree SSOT)
    - "Open Host Service (OHS)"   # Confluence space CFP = OHS pattern (consumer single entry point governance corpus 접근)
  glossary_ref: docs/glossary.md
is_transitional: false
sunset_criteria: N/A — permanent governance ratchet (ADR-058 §결정 5 정합, lane mapping rule SSOT = closed-set invariant)
---

# ADR Category → Lane Bucket Mapping Rule SSOT

## 1. Purpose (Why)

본 file = codeforge governance corpus (ADR 117 file + inter-plugin-contracts 30 file + Consumer Guide 1 file = 148 legacy page) Confluence space `CFP` IA tree migration 시 **category → lane bucket deterministic mapping rule SSOT**.

**Origin**: CFP-1493 Sub-B S2.3 partial complete (PR #1520 MERGED) 후 잔여 148 page real backfill carrier (CFP-1523). 4 DERIVED DEFAULT (DD-1 Diátaxis quadrant axis / DD-2 partial defer carrier scope 보존 / DD-3' MCP cascade 6-call atomic / DD-4 category → lane mapping rule SSOT) 의 DD-4 SSOT body.

**Ground truth note (F-DR-001 verify-before-trust)**: Story §1 USER-UTTERANCE-VERBATIM "142 page (ADR 111 + IPC 30 + Consumer Guide 1)" = stale local main 시점 사실 (Phase 0 시점 local cwd file count 111). Ground truth verified-via `git -C <wrapper-worktree> ls-files docs/adr/ADR-*.md | wc -l = 117` (2026-05-25T13:30:00+09:00 KST) — ADR 117 file + IPC 30 file + Consumer Guide 1 file = 148 legacy page. Pivot 정정 = Story §2.1 row 4 (verify-before-trust pivot row). Story §1 IMMUTABLE 정합 (story-section-1-immutable.yml).

**Consumer mental model 정합**: codeforge consumer project 의 governance corpus 학습자 (Confluence space CFP entry point) — lane 별 ADR navigate. flat `docs/adr/` (117 file) 안 lane-irrelevant ADR 가 lane bucket 안 숨겨짐 (per-ADR ad-hoc annotation 0, category SSOT = automated lane filter).

**Maintenance sustainability**: 신규 ADR 작성 시 frontmatter `category:` field 만 채우면 자동 lane bucket 분배 (option (b) 채택 — option (a) ADR frontmatter `lane:` field 신설 = 0/117 greenfield 회피).

## 2. Authority (Who decides) — DDD pattern mapping

**Primary advocate** = `ModuleArchitectAgent` (CFP-1126 unified mandate — module-level + aggregate-level boundary 통합). boundary axis 위협 (148 page lane bucket allocation = code module-level boundary placement rule 영역).

**chief tie-break ladder applied** (ADR-068 Amendment 2 / CFP-1086 4-way RACI → 3-way):
- D-1/D-2/D-3 = Stage 1 (primary axis matrix) — ModuleArch primary single-axis
- D-4 (CI lint mechanism) = Stage 2 (RACI lookup) — Cell 2.2 ModuleArch × InfraOp → InfraOp = CONSULT, ArchitectAgent self-handle
- D-5 (dry-run gate mandate) = Stage 2 — Cell 3.2 ModuleArch × TestContract → TestContract = CONSULT, ArchitectAgent self-handle

**Axis disjoint 정합**: 5 decision 모두 ModuleArch primary axis + 2 decision (D-4/D-5) consult overlay → boundary axis 단일 advocate invariant.

## 3. SSOT location precedence (ADR-091 §결정 4)

본 file = lane_mapping_rule narrative SSOT. cross-ref pointer locations:

| Location | Role | Content |
|---|---|---|
| `docs/domain-knowledge/domain/governance-principle/adr-category-lane-mapping.md` (본 file) | **SSOT primary (narrative body)** | mapping rule 전체 정의 + rationale + governance ratchet |
| `docs/confluence-ia-tree.yaml` `lane_mapping_rule:` field | **cross-ref pointer (yaml field)** | `ssot_ref: docs/domain-knowledge/domain/governance-principle/adr-category-lane-mapping.md` + `closed_enum: [<16 normalized enum>]` field 만 (narrative body 영역 0) |

Published Language content duplication 금지 (ADR-091 §결정 4) 정합 — 단일 owner location.

## 4. Mapping Rule — 18 unique enum × 16 effective canonical buckets × 8 lane bucket × cross-cutting fallback

> **case-normalization invariant (ADR-068 I-4 wording SSOT, F-DR-004 wording clarification)**:
>
> - **18 unique enum** (literal `yaml closed_enum` entries) = ADR corpus frontmatter `category:` field 안 18 distinct case-sensitive string (`docs/confluence-ia-tree.yaml` `lane_mapping_rule.closed_enum:` 18-entry literal SSOT)
> - **16 effective canonical buckets** (case-fold normalize) = lowercase canonical normalization 후 2 쌍 case-collision merge (`Architecture`(5)+`architecture`(3) → `architecture` 8 / `Process`(1)+`process`(1) → `process` 2) = 16 distinct canonical bucket
>
> **FU-1523-1 lint algorithm**: input frontmatter value 를 lowercase normalize 한 후 closed_enum membership check (case-fold during check). `case_fold_during_check: true` field (yaml lane_mapping_rule) = mechanical anchor.
>
> Capitalized 형식 legacy ADR frontmatter retain (rewrite = 별 carrier). lowercase canonical 의무 (신규 ADR 작성 시).

### 4.1 16 normalized enum mapping table

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
| 12 | `workflow-policy` | 5 | **codeforge-pmo** bucket ADR anchor (page_id 2130897) | wrapper-governance bucket cross-ref (cross-cutting policy) | workflow policy = PMO lane primary (GitOpsAgent + DialogFidelityAgent ownership) |
| 13 | `orchestrator-policy` | 1 | **wrapper-governance** bucket (cross-cutting) | codeforge-design bucket ADR anchor cross-ref | Cross-cutting fallback — Orchestrator policy = lane-agnostic governance |
| 14 | `audit` | 1 | **wrapper-governance** bucket (cross-cutting) | codeforge-pmo bucket cross-ref | Cross-cutting fallback — audit policy = lane-agnostic governance + PMO retro audit cross-ref |
| 15 | `team & process` (canonical `Team & Process` retain) | 27 | **wrapper-governance** bucket (cross-cutting) | codeforge-pmo bucket cross-ref (cross-cutting workflow) | Cross-cutting fallback — team workflow process governance (workflow-policy super-class) |
| 16 | `plugin architecture` (canonical `Plugin Architecture` retain) | 1 | **codeforge-design** bucket ADR anchor (page_id 2163571) | 모든 lane bucket cross-ref note (cross-cutting plugin architecture) | ModuleArch unified mandate primary (CFP-1126) — plugin architecture = design lane primary |
| 17 | `plugin distribution & consumer onboarding` (canonical retain) | 2 | **wrapper-governance** bucket (cross-cutting) | codeforge-deploy bucket (2098413) + codeforge-deploy-review bucket (2065914) cross-ref | Cross-cutting fallback + deploy lane cross-ref (ADR-087/088 CFP-1059) |
| 18 | `infrastructure` (canonical `Infrastructure` retain) | 1 | **codeforge-design** bucket ADR anchor (page_id 2163571) | codeforge-develop bucket cross-ref | InfraOperationalArch deputy (ADR-091 §3.1) — design primary |

**Total ADR coverage**: 117 ADR file 안 110+ file `^category:` field 보유. 7 file `^category:` field 부재 (early ADRs) = 별 retroactive backfill carrier (본 carrier scope 외).

### 4.2 inter-plugin-contracts (30 file) + Consumer Guide (1 file) mapping

| File 영역 | Primary lane bucket | Rationale |
|---|---|---|
| `docs/inter-plugin-contracts/` 30 file (9 contract: review_verdict / requirements_output / design_output / develop_output / test_verdict / pmo_output / git_ops_event / deploy_output / deploy_review_output + 7 registry: label-registry / debate-protocol / evidence-check-registry / severity-propagation / parallel-dispatch-protocol-v1 / imperative-walker-protocol-v1 + comment-prefix / fix-event) | **cross-cutting** bucket (page_id 2130942 `inter-plugin-contracts Registry`) — D-3 cross-cutting fallback | 모든 IPC = lane-agnostic published language (ADR-091 §결정 4 cross-plugin shared kernel). 9 contract = canonical_repo per-plugin SSOT (해당 lane bucket IPC sub-anchor cross-ref) but Confluence IA bucket primary = cross-cutting (consumer mental model 정합). |
| Consumer Guide page (1 file) | **wrapper-governance** bucket (page_id 2163807) | how-to quadrant (Diátaxis Action+Application) — consumer-facing single entry point. CFP-1493 partial 산출 재사용 — wrapper-governance bucket primary, lane-agnostic. |

### 4.3 Multi-lane ADR / cross-cutting ADR edge cases (Story §5.3 정합)

본 mapping rule = primary owner lane bucket + cross-ref note 패턴. 3 edge case:

1. **Multi-lane ADR** (예: ADR-082 verify-before-trust 4-layer = governance + 모든 lane 정합) — primary = wrapper-governance bucket (D-3 fallback) + 모든 lane bucket ADR anchor cross-ref note
2. **lane-agnostic IPC** (예: `review-verdict-v4` = design-review + code-review + security-test 3 lane 공통) — shared kernel bucket (cross-cutting `inter-plugin-contracts Registry`) primary + 해당 lane bucket IPC sub-anchor cross-ref
3. **ADR cross-cutting** (예: ADR-091 DDD vocabulary = ArchitectLane primary but 다른 lane 도 cross-ref) — primary owner lane bucket (예: 설계 lane) anchor + cross-ref note

## 5. closed-set invariant + future Amendment procedure (ADR-058 §결정 5)

### 5.1 closed-set invariant

본 mapping rule = **18 unique enum (case-normalized 16) closed-set** (`open_extension: false`). 신규 ADR frontmatter `category:` field = 본 16 enum 안 의무.

**Rationale**: CFP-1525 schema drift 패턴 답습 차단 (closed-enum order drift = 14 occurrence sentinel evidence). 신규 enum 출현 시 별 ADR Amendment 의무 (ratchet 강화 evidence 동반).

### 5.2 future Amendment procedure (별 ADR Amendment)

신규 category enum 도입 결정 시 다음 절차 의무:
1. 별 sub-CFP 발의 + ADR-058 §결정 5 sunset_justification 3-tuple (metric / who / how) 명시
2. 본 file Amendment N (lowercase canonical enum 추가 + Primary lane bucket + cross-ref + rationale)
3. `docs/confluence-ia-tree.yaml` `lane_mapping_rule.closed_enum:` field row append + `schema_version` MINOR bump
4. FU-1523-1 `scripts/check-adr-category-lane-coverage.sh` lint Amendment row coverage 자동 검증 (실 wire 후)
5. ADR-091 §결정 4 Published Language content duplication 금지 invariant 정합 — 단일 owner location 보존

## 6. Diátaxis quadrant alignment (Story AC-4)

| Anchor | Diátaxis quadrant | Consumer mental model |
|---|---|---|
| ADR anchor (lane bucket 안) | **Explanation** (Cognition+Acquisition) | 학습자 — design decision rationale 학습 |
| IPC anchor (cross-cutting Registry 안 + 해당 lane bucket sub-anchor) | **Reference** (Cognition+Application) | 구현자 — contract schema lookup |
| Consumer Guide bucket (wrapper-governance) | **How-to** (Action+Application) | 신규 consumer — 플러그인 설치 task-oriented |
| Living Architecture anchor (lane bucket 안, lane plugin self-owned) | **Explanation** (primary) | 운영자 — arc42 §3+§5+C4 Container+Component 학습 |

## 7. Cascade execution plan (Story AC-2/AC-3 cross-ref)

Phase 2 PR 안 6 MCP call atomic execution:

| Step | MCP Call | Target | parentId |
|---|---|---|---|
| 1 | `getConfluencePage(id="2097153")` | Legacy `adr` bucket (root) | (fetch body verbatim) |
| 2 | `updateConfluencePage(id="2097153", parentId="<lane_bucket_id_per_category>", body=<verbatim>)` | Move `adr` bucket → lane bucket per primary mapping | per §4.1 표 row 1-18 |
| 3 | `getConfluencePage(id="2129949")` | Legacy `inter-plugin-contracts` bucket (root) | (fetch body verbatim) |
| 4 | `updateConfluencePage(id="2129949", parentId="2130942", body=<verbatim>)` | Move IPC bucket → cross-cutting `inter-plugin-contracts Registry` | per §4.2 표 row 1 |
| 5 | `getConfluencePage(id="<consumer_guide_id>")` | Legacy Consumer Guide bucket (root) — Phase 2 execution time discovery | (fetch body verbatim) |
| 6 | `updateConfluencePage(id="<consumer_guide_id>", parentId="2163807", body=<verbatim>)` | Move Consumer Guide → wrapper-governance bucket | per §4.2 표 row 2 |

**Cascade primitive** (Confluence native): parent page move → children parent_id 변경 0 + 새 위치 자동 따라감 (Atlassian Community cross-ref, Story §2.1 row 3 `[verified]`). 148 children 자동 cascade (F-DR-001 — ADR 117 + IPC 30 + Consumer Guide 1 ground truth).

**Dry-run gate (D-5 mandate)**: Phase 2 PR 시작 시 1 page dry-run pre-check 의무 (test space or throwaway page) — cascade preserve 확인 후 3 root parent atomic 진입.

**Fallback (D-5 escape hatch)**: cascade 실패 시 REST direct `PUT /wiki/rest/api/content/{id}/move/{position}/{targetId}` per-page batch (body 미요구 path param only) — 284 MCP call worst-case 시나리오. ADR-061 §결정 1 multi-line Python 외부 file 의무.

**ADR-101 dual-layer verify** (Story §4.3.1 row 7b governance baseline): Phase 2 execution time MCP `getConfluencePage` / `updateConfluencePage` / `getPagesInConfluenceSpace` 응답 ground-truth dual-layer verify 의무.

## 8. Deferred-followup CFP (FU-1523-1 / FU-1523-2 declare)

### FU-1523-1 — CI lint mechanism mechanical wire

**Scope**: `scripts/check-adr-category-lane-coverage.sh` warning tier lint + `templates/github-workflows/adr-category-lane-coverage.yml` workflow + `docs/evidence-checks-registry.yaml` row append + `hotfix-bypass:adr-category-lane-coverage` family member append.

**Mechanism**: frontmatter `^category:` 값 (case-normalized lowercase) 이 본 file §4.1 `closed_enum` 안에 존재 여부 verify. 미존재 시 warning 발화 + 별 ADR Amendment 의무 안내.

**ADR-060 framework Wave 1 → Wave 2 wire pattern 답습**: declarative_layer 본 carrier (CFP-1523) → mechanical wire 별 sub-CFP (FU-1523-1).

### FU-1523-2 — Confluence IA tree drift detection lint

**Scope**: `scripts/check-confluence-ia-drift.sh` warning tier lint + `templates/github-workflows/confluence-ia-drift-detection.yml` 24h cron + workflow_dispatch + Issue auto-create + `hotfix-bypass:confluence-ia-drift-detection` family member append.

**Mechanism**: git tracked `docs/confluence-ia-tree.yaml` (desired state) ↔ Confluence space CFP actual parent_id state (current state) drift 검출. drift > 7 day 시 Issue auto-create.

**ADR-076 declarative reconciliation pattern 정합** (desired/current/converge). `marketplace-drift-detection.yml` pattern 답습.

## 9. Cross-ref summary

- **Story CFP-1523 §3.0 D-1/D-2/D-3** — 본 file = SSOT primary location 결정 산출 (governance-principle/ domain-knowledge body)
- **Story CFP-1523 §3.1** — 본 file §4.1 mapping table = Story §3.1 verbatim duplicate avoided (Story = section anchor pointer + reasoning, 본 file = SSOT primary)
- **`docs/confluence-ia-tree.yaml` `lane_mapping_rule:` field** — `ssot_ref:` cross-ref pointer + `closed_enum: [<16 enum>]` field
- **CFP-1493 PR #1520 MERGED** — parent carrier (S2.3 partial complete, 3 cross-cutting bucket 신설 — wrapper-governance / ADR Registry / inter-plugin-contracts Registry page_id 활용)
- **ADR-091 §결정 1/2/4** — DDD vocabulary governance + Published Language content duplication 금지 invariant
- **CFP-1126 / ADR-042 Amendment 10** — ModuleArch unified mandate primary advocate (boundary axis 단일 advocate)
