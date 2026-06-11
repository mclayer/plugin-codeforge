# Changelog

## 1.10.1 — 2026-05-30

### Changed

- **[CFP-1845 follow-up] agent model 핀 → 별칭 전환 (opus/sonnet/haiku 항상 최신 지칭). frontmatter model field 5건. tier 분류 변경 0건. wrapper #1846 / #1847 연계. marketplace sibling sync 동반.**
  - `agents/ClaudeReviewAgent.md` · `agents/CodeReviewPLAgent.md` · `agents/DesignReviewPLAgent.md` · `agents/SecurityTestPLAgent.md` — `model: claude-opus-4-7` → `model: opus`
  - `agents/CodexReviewAgent.md` — `model: claude-haiku-4-5-20251001` → `model: haiku`
  - 본문/description 의 과거 버전 서술(frozen audit trail)은 무변경.

## 1.10.0 — 2026-05-23

### Changed

- **review-verdict-v4 v4.8 → v4.9 MINOR (canonical)** — CFP-604 retro F7 Wave 2 carrier ([CFP-1303](https://github.com/mclayer/plugin-codeforge/issues/1303)). Wave 1 [CFP-1291](https://github.com/mclayer/plugin-codeforge/issues/1291) (codeforge-review #42, MERGED 2026-05-23 09:23 KST) prose-only anchor 위 schema layer codify.
  - `findings[].parallel_anchors_checked` optional array field 신설 (additive backward-compat — `findings[].anchor_id` v4.1 pattern 답습)
  - 각 entry = `{file_line: string, pattern_type: enum 5종 closed-set, matched: bool}`
  - `pattern_type` 5종 enum closed-set: `local_remote` / `client_server` / `read_write` / `forward_reverse` / `enum_closure`
  - `matched: bool` 의미: true = parallel anchor 발견 + 동일 root cause class 확인 / false = 검색 evidence clean enumeration / field absent = 검색 미수행 (Wave 3 lint heuristic 영역)
  - **ADR-068 I-2 cross-module propagation completeness 의 review-verdict layer realization** (micro-scale parallel form — propagation matrix module-level vs `parallel_anchors_checked` finding-level disjoint axis)
  - `templates/review-pl-base.md` 영향 0 (이번 Wave 는 CodeReviewPLAgent.md 만 갱신)
  - **Wave 1 → Wave 2 → Wave 3 layered architecture**: Wave 1 prose anchor (CFP-1291) / Wave 2 schema codify (본 CFP-1303) / Wave 3 mechanical lint presence-grep heuristic (deferred-followup)
  - ADR-008 §결정 2 "새 선택 필드 추가" MINOR bump 정합. Runtime impact 없음 (기존 v4.8 consumer 가 본 신규 field 무시 가능)
  - 적용 lane: CodeReviewPL (primary) — Wave 1 CFP-1291 본문 정합 / DesignReviewPL + SecurityTestPL (optional)

### Updated

- **`agents/CodeReviewPLAgent.md`** — Wave 1 prose ("parallel anchors checked: [...]" inline marker) → Wave 2 schema YAML block format 갱신.
  - 5 pattern_type enum closed-set 표 (canonical schema 정합 — local_remote / client_server / read_write / forward_reverse / enum_closure)
  - finding output schema example v4.9 (anchor_id + parallel_anchors_checked array block)
  - field semantic 명시 (matched true/false/absent 3-state 구분)
  - Wave 1/2/3 layered architecture 표
  - ADR-068 I-2 cross-module propagation completeness 연결 단락
  - CFP-604 trigger evidence (LOCAL_AUTHOR ↔ REMOTE_AUTHOR pattern_count 2) 보존

### Out of scope (별 follow-up CFP)

- **Wave 3 mechanical lint** (`parallel_anchors_checked` field presence-grep heuristic on finding emit) — deferred-followup
- **5 other lane plugin sibling sweep** (requirements / design / develop / test / pmo v4.8 → v4.9 mirror) — CFP-1167 precedent 답습

### Sibling sync (ADR-010)

- canonical: 본 PR (codeforge-review `docs/inter-plugin-contracts/review-verdict-v4.md`)
- wrapper sibling: plugin-codeforge PR (별 atomic — `docs/inter-plugin-contracts/review-verdict-v4.md` + `MANIFEST.yaml` row)
- 5 other lane plugin 5개 (requirements/design/develop/test/pmo): 본 scope 외, 별 follow-up CFP (CFP-1117-S4 precedent 답습)

### Marketplace atomic invariant (ADR-063)

- mirrored field 4종 (name / version / description / author) atomic sync 의무 — plugin.json 1.9.1 → 1.10.0 MINOR + marketplace.json 동반 PR
- `marketplace_sync_declared: true` (verdict packet 의 explicit marker)

## 1.9.1 — 2026-05-23

### Added

- [CFP-1291] **CodeReviewPLAgent.md cross-anchor parity check step 추가** (CFP-604 retro F7 follow-up realized, minimum-viable Wave 1 declarative). finding 작성 시 parallel anchor enumeration 의무 + 5 patterns priority enumeration (LOCAL↔REMOTE / client↔server / read↔write / forward↔reverse / enum closure check) + finding output 안 `parallel anchors checked: [...]` inline marker prose 명시.
  - **Evidence (CFP-604)**: Phase 2 CodeReview Iter 1 = LOCAL_AUTHOR `check-version-bump-atomic.sh:76` catch 후 REMOTE_AUTHOR `check-version-bump-atomic.sh:213` (동일 root cause class) 미catch → CI 재발견 + FIX iter 2 continuation commit `85b6042` 필요. Pattern 1 (LOCAL↔REMOTE) parallel-site grep 미적용 결함.
  - **Wave 1 scope**: agent body prose + inline marker. **Wave 2 (deferred)**: review-verdict-v4 schema field `parallel_anchors_checked[]` 신설 = 별 sub-Story carrier (ADR-076/082/086 precedent 답습 — declarative first, mechanical schema second).

## 1.9.0 — 2026-05-21

### Changed
- review-verdict-v4 v4.7 → v4.8 MINOR (ADR-091 §결정 6 enforcement layer 3-tier 의 3번째 tier — review-verdict-v4 enum S4 carrier, CFP-1117 Story-4)
  - `findings[].type` enum 에 3 DDD finding type literal 추가: `bc_violation` (Bounded Context 위반 — Change Plan §3.D bounded_context_boundary 연결) / `aggregate_violation` (Aggregate 위반 — Change Plan §3.A affected_aggregates + ADR-091 §결정 3 Layer B real Aggregate 연결, ModuleArchitectAgent boundary axis unified 영역) / `ubiquitous_language_drift` (Ubiquitous Language drift — check-ubiquitous-language lint 연결)
  - ADR-091 §결정 7 INV-5 vocabulary theater 차단 forcing function 의 review-verdict finding 연결 (evidence #4)
  - additive only backward-compat invariant (기존 v4.7 consumer 가 3 신규 enum literal 무시 가능). ADR-008 §결정 2 "enum literal 추가" MINOR bump 정합. CFP-528 Amendment 1 (enum literal + 의미 1줄) pattern verbatim 답습.
  - DesignReviewPL + CodeReviewPL 양 lane emit. verdict-level boolean field 신설 0건 (findings[].type literal 확장만 — semantic accountability mechanism, §결정 6 3번째 tier rationale 정합).
- `templates/review-pl-base.md` §3 — DDD finding type 3 literal 종합 check table 추가 (DesignReview / CodeReview cross-validate, boundary-completeness / dimensional-empirical-gap dual-binding 패턴 답습)

### Note
- 5 sibling contract (requirements/design/develop/test/pmo v4.3) pre-existing drift = 본 S4 scope 외 (별 sweep CFP carrier)

## 1.8.0 — 2026-05-20

### Changed
- review-verdict-v4 v4.5 → v4.6 MINOR (canonical SSOT sync, ADR-010 sibling sync mirror from wrapper CFP-1086-S1)
  - `deputy_axis_restructure_self_check_passed` optional bool field 신설 (ADR-042 Amendment 8 + ADR-086 P7 framework self-application 첫 사례 carrier)
  - `boundary_completeness_self_check_passed` scope expansion (ADR-068 Amendment 2 wording SSOT chief tie-break ladder cross-ref)

`codeforge-review` plugin 릴리스 이력.

버전 체계: [Semantic Versioning 2.0.0](https://semver.org/lang/ko/). v1.0 이전은 minor bump도 breaking 가능.

## [1.7.0] - 2026-05-20

### CFP-698 — ADR-014 Amendment 4 + ADR-042 Amendment 7 cross-repo sibling sync (MINOR)

Wrapper Phase 1 PR (mclayer/plugin-codeforge#1035 `abcd92bf` CFP-676 merged 2026-05-19) Epic CFP-1026 Wave 2 Story-4 carrier. ADR-014 Amendment 4 (OpRiskArch → InfraOperationalArch rename + §7.4 primary/cross-ref shell evidence-driven 3-axis split) + ADR-042 Amendment 7 (DataMigrationArch → DataArch rename, 5+3 deputy matrix) 의 codeforge-review repo cross-repo sibling 반영. ADR-054 Category 2 doc-only fast-path. ADR-010 §4 wrapper-first allowed pattern 정합.

#### Changed (mechanical rename, 7 occurrence)

- `templates/review-checklists/design.md` — `OperationalRiskArchitectAgent` → `InfraOperationalArchitectAgent` (L5 + L71 + L89 = 3 occurrence) + `DataMigrationArchitectAgent` → `DataArchitectAgent` (L141 + L172 = 2 occurrence) + `DataMigrationArch` → `DataArch` (L31 + L196 = 2 occurrence)
- `agents/DesignReviewPLAgent.md` — L105 `DataMigrationArch` → `DataArch` (1 occurrence)

#### Added

- `templates/review-pl-base.md` — §8.6 audit gate normative 1-line append (pointer-existence vs policy-effectiveness disjoint axis, ADR-014 Amd 4 §결정 2 cross-ref shell 분류 정합). DesignReviewPL Story §8.6 (IntegrationTest contract pointer) audit 시 pointer 존재 mechanical check only invariant. policy 값 공백 PASS / pointer 부재 P1 FIX. boundary-completeness flag (ADR-068 I-3 unconditional guard placement).
- `docs/architecture/codeforge-review.md` — Governance ADR anchor 영역 §8.6 audit gate 1-line cross-ref (ADR-078 living architecture doc SSOT 정합).

#### Why

S1 CFP-676 wrapper#1035 `abcd92bf` merged 시점에 wrapper SSOT 만 갱신되어 codeforge-review repo 의 cross-repo sibling 반영 미완 상태. RequirementsPL ground truth verify (`OperationalRiskArchitectAgent` 6 occurrence × 2 file = 7, `DataMigrationArchitectAgent` 5 occurrence × 2 file). design-time existence layer (DesignReviewPL §8.6) + runtime enforcement layer (IntegrationTest §7.4, codeforge-test sibling) 의 2-layer split 정착으로 "정책 효력 (effectiveness) vs 정책 존재 (existence)" disjoint axis 명문화. 이전 root-cause confusion (pointer 부재 P1 vs policy 공백 PASS 구분 불가) 차단.

#### Compatibility

- **Wire**: deputy 명칭 rename = mandate scope 보존 (ADR-033 4 sub-item Container Docker 0 변경 invariant). §8.6 audit gate 1-line = 신규 normative (pointer mandatory). ratchet 강화 방향 (ADR-058 §결정 5 정합).
- **Marketplace sync**: 본 MINOR bump 의 marketplace.json mirror = ADR-063 atomic invariant 발효 (별 sync PR carrier).
- **Carrier**: CFP-698 (Epic CFP-1026 Wave 2 Story-4, sibling Story = codeforge-test 1.2.0).

## [1.6.0] - 2026-05-13

### CFP-582 — ADR-059 Amendment 2 / debate-protocol-v1 v1.2 sibling sync — review-pl-base.md cross-ref + 3 marker pattern verification (MINOR)

Wrapper Phase 1 PR (mclayer/plugin-codeforge CFP-582 — Wave 4 ADR-059 Amendment 2) 의 canonical sibling sync (ADR-010 §4 wrapper-first allowed pattern). DesignReview lane 의 review-verdict-v4 findings[] 와 Story §9 debate transcript 간 정합 검증 책무 명시화.

### CFP-597 — review-verdict-v4 canonical v4.4 → v4.5 MINOR bump (marketplace_sync_declared, ADR-063 Amendment 1)

ADR-063 Amendment 1 (CFP-597) carrier — ArchitectAgent Phase 1 marketplace sync proactive self-check 결과 explicit marker 신규 optional field 추가.

#### Added (CFP-582)

- `templates/review-pl-base.md` — `§11.5. debate-protocol-v1 v1.2 정합 (CFP-582 / ADR-059 Amendment 2)` 섹션 신설
- `templates/review-pl-base.md` §12 버전 이력 — v3.2 entry append

#### Added (CFP-597)

- **review-verdict-v4 canonical v4.4 → v4.5** — `marketplace_sync_declared: bool` optional field 신설 (ADR-063 §결정 9 SSOT, Amendment 1)
- `related_adrs[]` 에 `ADR-063` entry 추가 (marketplace atomic invariant)
- `authors[]` + `amendment_log[]` 에 CFP-597 v4.5 entry 추가

#### Compatibility

- **Wire**: review-pl-base.md prompt block 신설 + review-verdict-v4 v4.5 MINOR (새 optional field). v4.4 이전 consumer backward-compat.
- **marketplace sync**: mclayer/marketplace#91 (merged 선행 — ADR-063 §결정 2 ordering, CFP-597 codeforge-pmo 0.1.3 sync).

## [1.5.0] - 2026-05-13

### CFP-528 Wave 2B — review-verdict-v4 v4.4 canonical mirror + review-pl-base §3 I-5 rule (sibling sync)

ADR-010 sibling sync — wrapper Phase 1 PR mclayer/plugin-codeforge#575 (CFP-528 Wave 2B, ADR-068 Amendment 1 I-5 dimensional empirical grounding) 의 canonical mirror.

#### Added

- **review-pl-base.md §3 I-5 mechanical detection rule** — DesignReviewPL 가 §3 / §7 quantitative parameter (10 dimension enum: latency / scale / cardinality / throughput / cost / accuracy / lifecycle / volume / rate / count) 의 `[empirical-source]` annotation 부재 시 finding emit (severity P1, category `dimensional_empirical_gap`, type `"dimensional-empirical-gap"`). Trigger 4종 / Mitigation 4종 / Justification / Exemption 체계. CodeReviewPL Tier C cross-validate (impl hardcoded numeric vs ADR / Story empirical-source mismatch).
- **review-verdict-v4 canonical v4.3 → v4.4 mirror** — wrapper sibling (mclayer/plugin-codeforge#575) 변경 byte-identical mirror (ADR-010 sibling sync, canonical owner per ADR-001). `dimensional_empirical_self_check_passed: bool` field + `findings[].type: "dimensional-empirical-gap"` literal + §13 dimensional empirical grounding self-check 신설.

#### Sibling sync

- Source canonical: 본 PR 자체 (codeforge-review = review-verdict canonical owner per ADR-001 / ADR-010)
- Wrapper sibling: mclayer/plugin-codeforge#575 (이미 OPEN, 본 PR 가 sibling sync follow-up per ADR-010 §4 wrapper-first 절차)
- Marketplace sync: mclayer/marketplace 별 PR (codeforge-review 1.5.0, ADR-063 atomic invariant 선행 merge 의무)

#### Compatibility

- **Wire**: review-verdict-v4 schema MINOR (new optional field). v4.3 producer / v4.4 consumer 양방향 backward-compat.
- **Marketplace sync**: 별도 PR (ADR-063 atomic invariant — marketplace sync 선행 merge).

## [1.4.1] - 2026-05-13

### CFP-462-followup — phase-gate-mergeable workflow sync (PATCH)

EPIC-RESULTS CFP-462 §6 carrier #1. Wrapper PR #500 (CFP-499 / ADR-010 Amendment 4 sibling-pr label fast-pass) merge 후 sibling repo backport 누락 detection. CFP-438 4 PR merge 시 codeforge-review 에서 `phase-gate-mergeable` required check name mismatch ACTION_REQUIRED 실증 → branch protection 임시 변경 / 복원 우회 패턴 발생.

#### Changed

- `.github/workflows/phase-gate-mergeable.yml` — wrapper SSOT (`templates/github-workflows/phase-gate-mergeable.yml`) verbatim mirror. CFP-113/123/133/342/499 누락 전체 backport (old version 였음).

#### Why

ADR-010 sibling sync 의무. sibling-pr label fast-pass + CFP-113/123/133/342 정합.

#### Compatibility

- **Wire**: workflow file 만 변경. agent / contract / overlay 영향 없음.
- **Marketplace sync**: 본 PATCH bump 의 marketplace.json mirror 는 별도 후속 carrier.

## [1.4.0] - 2026-05-13

### CFP-438 — review-verdict v4.1 → v4.2 MINOR bump (mechanical_self_check_passed optional bool field, ADR-065 sibling sync)

Wrapper Phase 1 PR (mclayer/plugin-codeforge cfp-438 branch) ADR-065 신설에 대한 canonical sibling sync (ADR-010 §4 wrapper-first 정합). ArchitectAgent Phase 1 산출물 commit 직전 7-item mechanical sync self-check (non-marketplace 영역) 결과 explicit marker 도입.

#### Added

- `docs/inter-plugin-contracts/review-verdict-v4.md` v4.1 → v4.2 MINOR bump:
  - `frontmatter` — `contract_version: "4.1" → "4.2"` + `related_adrs` 에 `ADR-065` append + `authors` + `amendment_log` 의 v4.2 entry
  - `## 2. Schema` — `mechanical_self_check_passed: <bool>` optional field 신설 (design lane only, code/security lane optional/omit 가능)
  - `## 3. 4-step Orchestrator algorithm` step 1 — `mechanical_self_check_passed 채움` line 추가 (design lane only, ArchitectPLAgent forward)
  - `## 11. ArchitectAgent Phase 1 mechanical self-check (v4.2 — ADR-065 / CFP-438)` 신설 — 7-item 표 + Producer/Consumer 책무 + 적용 lane + marketplace 영역 분리 (ADR-063 cross-ref)

#### Changed

- `.claude-plugin/plugin.json` — version 1.3.0 → 1.4.0 MINOR (contract schema 변경, ADR-037 정합). description CFP-438 entry append.

#### Why

ADR-065 (wrapper) 의 sibling sync 의무 (ADR-010 §4) — canonical = 본 plugin, sibling = wrapper. ADR-008 §결정 2 "새 선택 필드 추가" = MINOR bump 정합. Runtime impact 없음 (기존 v4.1 consumer 가 본 필드 무시 가능, backward-compat). design lane producer (ArchitectPLAgent) 가 ArchitectAgent §5.5 self-check 결과를 verdict packet 에 forward — false 시 즉시 `pl_recommendation: FIX` + ArchitectAgent re-spawn FIX 루프.

#### Cross-ref

- Wrapper canonical ADR: [ADR-065](https://github.com/mclayer/plugin-codeforge/blob/main/docs/adr/ADR-065-architect-phase1-mechanical-self-check.md)
- plugin-codeforge-design sibling PR: ArchitectAgent §5.5 + ArchitectPLAgent verdict packet + change-plan §13 신설
- Wrapper Phase 1 PR (paired sibling): https://github.com/mclayer/plugin-codeforge/pulls

## [1.3.0] - 2026-05-11

### CFP-391 — debate-protocol-v1 sibling sync + review-verdict v4.0 → v4.1 MINOR bump

Wrapper Phase 1 PR (mclayer/plugin-codeforge#400) 의 debate-protocol-v1 도입에 대한 codeforge-review canonical sibling sync. wrapper Phase 2 PR (#?, CFP-391 Phase 2) merge 후 follow-up.

### Added

- `templates/review-pl-base.md` §3.0~§3.3 신규 sub-section — debate-protocol-v1 dispatch SOP (Adversarial debate, CFP-391 / ADR-059):
  - §3.0 Divergence detection — review-verdict-v4 `findings[].anchor_id` field 기반 union iteration + severity/recommendation 분류 알고리즘
  - §3.1 Debate dispatch — Round 0 init + Round 1~N (max 5) execution + min 3 force_continue + max 5 escalation + EC-2/EC-3/EC-4/EC-7 invariant 정합
  - §3.2 Anchor 재발 검사 — Story §9 scan + count >= 2 → AskUserQuestion escalation (ADR-059 §결정 4)
  - §3.3 Transcript 영속화 — Story §9 inline append + §10 FIX Ledger `debate_artifact_ref` field + ArchitectPLAgent re-spawn 4-step
- `docs/inter-plugin-contracts/review-verdict-v4.md` v4.0 → v4.1 MINOR bump — `findings[].anchor_id` optional field 추가 (debate-protocol-v1 stable identifier 의존). ADR-008 §결정 2 "새 선택 필드 추가" MINOR bump 정합. `amendment_log` 신규 entry 2개 추가 (v4.0 + v4.1).

### Why

- wrapper Phase 1 PR (CFP-391) 가 review-verdict-v4 sibling 측에 `findings[].anchor_id` placeholder field 추가 (FIX-1 of DesignReview Iteration 1) 했으나 canonical sync follow-up 의무 (ADR-010 §단계 절차) + ADR-008 SemVer MINOR bump 의무 (F-003 finding of DesignReview Iteration 2).
- review-pl-base.md §3.0~§3.3 추가 = DesignReviewPLAgent verdict 합성 알고리즘 의 lane-agnostic 부분 (Story 2 / CFP-392 / Requirements lane 도입 시에도 동일 SOP). codeforge-review canonical SSOT.

## [Unreleased] - sibling sync follow-up

### CFP-137 — review-verdict v4 canonical mirror (sibling sync follow-up)

Wrapper Phase 1 PR (mclayer/plugin-codeforge#284) 의 review-verdict v4 cutover 의 ADR-010 sibling sync follow-up. canonical (본 plugin) 측 v4 mirror 신설 + v3 status flip.

### Added

- `docs/inter-plugin-contracts/review-verdict-v4.md` (NEW, canonical) — wrapper sibling verbatim mirror. `pl_recommendation` 자체가 final verdict + 신규 `worker_dialog_rounds` field (Adversarial debate measurable verification). 4-step Orchestrator algorithm (v3 5-step → 4-step).

### Changed

- `docs/inter-plugin-contracts/review-verdict-v3.md` `status: Active → Archived` (v4 cutover, CFP-137 wrapper Phase 1 PR merge 시점). Frontmatter `superseded_by: review-verdict-v4` + ADR-044 cross-ref + CFP-137 author entry. Body annotation 갱신: 이전 DEPRECATED PASSTHROUGH (CFP-134 / ADR-035) 영역 = v4 cutover 시 종료 명시.

### Notes

- v4 ADR carrier = mclayer/plugin-codeforge `docs/adr/ADR-044-phase-scoped-sequential-team.md` (CFP-137). ADR ID 가 ADR-041 → ADR-044 retro-renumber 된 사유: CFP-276 (PR #279 merged) 가 ADR-041 = doc-location-registry 선점, PR #283 (open) 가 ADR-042 + ADR-043 점유. createdAt earlier wins.
- `templates/review-pl-base.md` v3 → v4 schema 갱신은 별도 follow-up PR — 본 PR 은 contract canonical 신설 + v3 archive 만 (CFP-137 sibling sync 1차 wave).
- ADR-011 inter-plugin-drift CI invariant: 본 PR merge 후 wrapper PR #284 의 `inter-plugin-drift (CFP-E)` check 가 PASS 로 flip (canonical 부재 → 존재).

## [1.1.0] - 2026-05-07

### CFP-128 / ADR-033 — Container security 1st-layer (trivy + hadolint)

SecurityTestPL 1st-layer 도구에 trivy (image / IaC 스캔) + hadolint (Dockerfile lint) 추가. `templates/review-pl-base.md` v3.0 → v3.1 — §3 Container security severity rule row append. ADR-033 §결정 4 (carrier — wrapper canonical).

### Added

- SecurityTestPL 1st-layer: trivy + hadolint findings ingestion (Dependabot / CodeQL / Secret Scanning 과 동렬)
- `templates/review-pl-base.md` §3 container security severity rule (P0: critical CVE in base image / hardcoded secret in Dockerfile / privileged user — P1: outdated base image / missing healthcheck / non-pinned digest)

### Changed

- `templates/review-pl-base.md` v3.0 → v3.1 (CFP-128 / ADR-033 §3 Container security severity rule row)

### Cross-ref

- ADR-033 §결정 4 (carrier — wrapper canonical)
- D3 sibling sync PR #17 (commit 0e89c1d) — SecurityTestPL 1st-layer + review-pl-base container security
- F4 (this PR) — codeforge-review version bump

### Compatibility

- **Wire**: review_verdict v3 schema 변경 없음 (additive only). 1st-layer ingestion 확장만
- **Migration**: consumer 측 trivy + hadolint workflow 가 없으면 findings 누락 (graceful degradation, 별도 CFP 로 consumer template 추가)

## [1.0.0] - 2026-04-29

### CFP-35 (codeforge ζ arc) — review_verdict v2 retrofit (BREAKING)

ζ arc 첫 lane plugin self-write 검증 단계 (codeforge parent spec CFP-31 §5.5). PL이 Story §9 + GitHub comment + gate label 을 자체 write — DocsAgent 경유 폐기.

### Changed (BREAKING)

- `agents/{Design,Code,SecurityTest}ReviewPLAgent.md` 권한 확장:
  - allow: `Edit(docs/stories/**)`, `mcp__github__add_issue_comment`, `mcp__github__issue_write`
  - deny: `docs/{change-plans,adr,domain-knowledge,retros,inter-plugin-contracts,superpowers}/**` 명시 (이전 `docs/**` 광역 deny → narrow path-scoped)
- `templates/review-pl-base.md` §5.4 — review_verdict schema v1 → v2 (writes_completed audit + summary_for_* 제거)
- `templates/review-pl-base.md` §5.5 — Self-write 절차 신설 (4 steps + Lane → gate label / next phase 매핑)

### Added

- `docs/inter-plugin-contracts/review-verdict-v2.md` — canonical v2 contract SSOT
- `.claude-plugin/plugin.json` v0.3.0 → v1.0.0 BREAKING

### Why

codeforge ζ arc parent spec CFP-31 §5.5: 첫 lane plugin self-write 검증으로 review v2 retrofit 채택. 이미 plugin이라 코드 이동 0, contract revise만으로 패턴 검증. 이후 codeforge-pmo (CFP-36) 등 lane plugin도 같은 패턴 따름.

### Compatibility

- **Wire**: codeforge core 가 v2 verdict 처리 (v0.22.0+ 부터). v0.21 이하 codeforge는 v1 verdict 기대 → 호환 불가
- **Migration**: codeforge 와 codeforge-review 동시 bump 의무 — codeforge v0.22.0 + codeforge-review v1.0.0 짝
- **Side-by-side v1 + v2**: 불가능. v1 contract 는 wrapper에서 Deprecated 표기 후 archive 예정 (6 CFP 후)
- **Marketplace sync 의무**: 두 plugin 모두 동시 sync 필수

## [0.3.0] - 2026-04-29

### Changed

Bundle 1 contract alignment — Codex 협업 gap review에서 확인된 review_verdict v1 contract와 PL/worker md 사이 silent drift 5건 해소 (review-only):

- `templates/review-pl-base.md` §2 — packet에 `contract_version: "1.0"` 필수 필드 추가 + lane×field 매트릭스 행 추가 (gap #3)
- `templates/review-pl-base.md` §3 — Worker verdict (`PASS|ISSUES|NO_SHIP|ESCALATE_PACKET_INCOMPLETE`) → review_verdict.status (`PASS|FIX|FIX_DISCRETIONARY`) 변환표 신설 (gap #1)
- `templates/review-pl-base.md` §3 — P3/unclassified severity 처리 규정 신설 (P3 → P2 downgrade, unclassified → drop or P2) (gap #5)
- `templates/review-pl-base.md` §5.4 — typed verdict YAML 출력 블록 신설 (contract-required 8 필드 명시) (gap #2)
- `agents/{Claude,Codex}ReviewAgent.md` — packet 검증에 `contract_version` 추가; lane=security `first_layer_findings` 부재 시 `ESCALATE_PACKET_INCOMPLETE`로 일관 (이전: 비차단 결손 표기) (gap #7, gap #3)
- `agents/{Design,Code,SecurityTest}ReviewPLAgent.md` — packet 예시에 `contract_version: "1.0"` 첫 줄 추가 (gap #3)
- `.github/workflows/invariant-check.yml` — 신규 step "Packet contract_version presence" 추가 (3 PL × YAML)

### Why

review_verdict v1 contract는 codeforge core SSOT지만 review plugin 측 PL/worker md가 contract 8 필드 중 일부를 silently 누락 emit하거나 enum 불일치를 노출. Codex 협업 gap review에서 7건 P1 drift 확인 — 본 v0.3.0이 review-only 5건 처리. 나머지 cross-repo coordination 2건(`mechanical_category` schema 추가, `next_gate_label` 자기모순 해소)은 별도 PR (Bundle 2).

### Compatibility

`codeforge core` >= 0.17.0 호환 그대로 유지 — contract version v1.0 위반 없음 (오히려 v1.0 enforcement 강화).

상세 plan: [`docs/superpowers/plans/2026-04-29-bundle-1-contract-alignment.md`](docs/superpowers/plans/2026-04-29-bundle-1-contract-alignment.md).

## [0.2.0] - 2026-04-28

### Added

- `.github/workflows/invariant-check.yml` — own invariant-check workflow (carryover from codeforge core CFP-29 Phase 1 추출). Review category enum parity (3 lane × SSOT/PL/Codex) + Severity overrides count + breakdown parity (3 lane × SSOT/PL) 검증.

## [0.1.0] - 2026-04-28

### Initial extract from codeforge core

[`mclayer/plugin-codeforge`](https://github.com/mclayer/plugin-codeforge) v0.16.0 (commit `1e75442a9cb3f0004cf75cd8e0b152745cba532a`)에서 lane-agnostic review subsystem 추출.

### Added (initial)

- `agents/DesignReviewPLAgent.md` (codeforge core 에서 이동)
- `agents/CodeReviewPLAgent.md` (이동)
- `agents/SecurityTestPLAgent.md` (이동)
- `agents/ClaudeReviewAgent.md` (이동, lane-agnostic worker)
- `agents/CodexReviewAgent.md` (이동, lane-agnostic worker)
- `templates/review-pl-base.md` (이동, 3 PL 공통 base SSOT)
- `templates/review-checklists/design.md` (이동)
- `templates/review-checklists/code.md` (이동)
- `templates/review-checklists/security.md` (이동)
- `overlay/hooks/session-start-deps-check.sh` (NEW — codeforge core 설치 verify)
- `overlay/hooks/regen-agents.sh` (NEW — codeforge core merge.py 재사용 패턴)
- `docs/adr/ADR-001-extracted-from-codeforge.md` (NEW — 추출 사실 + verdict v1 contract 동결 시점)
- `README.md` + `CHANGELOG.md`

### Why

CFP-25 Phase 1 strategic payoff. codeforge core revision 비용 절감 + ADR-001 lane-agnostic worker 통합을 plugin 경계로 보존. 상세는 codeforge core repo의 [CFP-29 design spec](https://github.com/mclayer/plugin-codeforge/blob/main/docs/superpowers/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md).

### Migration (from codeforge core monolith)

기존 codeforge consumer는 codeforge >= 0.17.0 + codeforge-review >= 0.1.0 두 plugin 모두 install 의무. 자세한 사항: codeforge core [migration-guide v0.16 → v0.17](https://github.com/mclayer/plugin-codeforge/blob/main/docs/migration-guide.md) 섹션.
