---
adr_number: 74
title: CLAUDE.md Amendment ref drift detection lint — cross-section coherence between ADR amendment_log and CLAUDE.md narrative
status: Proposed
category: governance
date: 2026-05-14
is_transitional: false
carrier_story: CFP-708
supersedes: []
amends: []
related_adrs:
  - ADR-012  # wrapper CLAUDE.md SSOT boundary — CLAUDE.md 본문이 본 lint scope target file
  - ADR-058  # ADR sunset criteria mandate — frontmatter amendment_log 가 drift 비교 SSOT
  - ADR-060  # Evidence-enforceable promotion framework — 본 lint 가 9번째 warning-tier entry
  - ADR-063  # Marketplace atomic invariant — CFP-477 F-DR-001 detection 의 stale ref source (Amendment 2 §결정 11 → 실제 Amendment 3 §결정 13)
  - ADR-065  # ArchitectAgent Phase 1 mechanical self-check — 7-item mechanical sync 의 자매 (cross-section coherence 확장)
  - ADR-068  # Boundary completeness invariants — I-4 wording SSOT 와 cousin (semantic 검증 vs mechanical 검증 분리)
related_stories:
  - CFP-708  # 본 carrier
  - CFP-627  # 1차 evidence (pause-and-resume drift, CLAUDE.md line 296 stale)
  - CFP-477  # 2차 evidence (F-DR-001 P1 detection)
  - CFP-263  # doc-locations lint lineage (cross-section coherence pattern 답습)
related_files:
  - CLAUDE.md
  - scripts/check-claude-md-amendment-ref.sh  # Phase 2 carrier
  - templates/github-workflows/claude-md-amendment-ref-drift.yml  # Phase 2 carrier
  - .github/workflows/claude-md-amendment-ref-drift.yml  # Phase 2 self-app
  - docs/evidence-checks-registry.yaml  # Phase 2 row append
  - docs/inter-plugin-contracts/label-registry-v2.md  # Phase 2 hotfix-bypass label entry
mechanical_enforcement_actions:
  - name: claude-md-amendment-ref-drift-check
    target: CLAUDE.md ADR amendment cross-reference lines
    detection: bash scripts/check-claude-md-amendment-ref.sh
    enforcement_workflow: templates/github-workflows/claude-md-amendment-ref-drift.yml
    bypass_label: hotfix-bypass:claude-md-amendment-ref
    audit_lint: bash scripts/check-bypass-audit-comment.sh
    current_tier: warning  # ADR-060 §결정 5 — 첫 도입 default
---

# ADR-074: CLAUDE.md Amendment ref drift detection lint

## 상태

`Proposed` (2026-05-14, carrier CFP-708 Phase 1)

## 컨텍스트

### 배경: 2 occurrence drift evidence (≥ 2 threshold reach)

**Occurrence 1 — CFP-627 (2026-05-14, pause-and-resume drift)**

CFP-627 Phase 1 PR #643 가 ADR-063 Amendment 3 §결정 13 (marketplace drift scheduled detection 4th defense layer) 신설. 그 결과 CLAUDE.md line 296 ADR-063 단락 안 "Amendment 2 §결정 11" cross-ref 가 **stale ref** 가 되었음 (실제 = Amendment 3 §결정 13). CLAUDE.md 본문 업데이트는 별도 PR (CFP-477) 에서 cleanup 으로 처리.

**Occurrence 2 — CFP-477 (2026-05-15, DesignReview F-DR-001 P1 detection)**

CFP-477 Phase 1 DesignReview 가 사후 발견:

> F-DR-001 (P1): CLAUDE.md line 296 ADR-063 단락 "Amendment 2 §결정 11" stale ref — 실제 Amendment 3 §결정 13. CFP-627 merge 시점 mechanical sync 누락.

**Root cause class**: `claude-md-amendment-ref-drift` (CFP-477 retro §5 행 4 — pattern_count 2 / threshold ≥ 2 reach / escalation_action `adr_draft_emitted`).

### 문제 정의

CLAUDE.md 본문은 plugin governance / policy 의 narrative SSOT 이며, ADR cross-ref 단락이 다수 존재한다. ADR 가 Amendment N 으로 진화하면 (`amendment_log` row append) CLAUDE.md 안 해당 cross-ref 단락도 동기 갱신되어야 한다. 그러나:

- **CLAUDE.md 갱신 = manual narrative drift fix** — ArchitectAgent / Orchestrator 가 직접 Edit, mechanical action 부재
- **ADR amendment 와 CLAUDE.md cross-ref 가 별도 PR 진행** — atomic invariant 부재
- **별도 PR 안 main forward window** — CFP-477 retro §5 행 1 (4-wave rebase friction) 와 결합 시 사후 drift 보장

CFP-263 (doc-locations lint) lineage 의 cross-section coherence lint pattern 을 답습하여 **PR-time mechanical lint** 로 drift 감지 의무를 도입한다.

### 결정 안 candidate 2종 비교

| Candidate | 영역 | 권장 여부 |
|---|---|---|
| **(A) 신규 ADR (본 ADR-074)** | cross-section coherence lint 별도 governance ADR. CFP-263 doc-locations lint lineage 답습 — 별도 ADR pattern (ADR-041 doc-locations registry / ADR-065 mechanical self-check 와 같은 family) | **권장** — domain coherent (별도 도메인 SSOT) |
| (B) ADR-060 Amendment N | Evidence-enforceable framework 의 새 entry 영역 amendment. framework SSOT 자체 amendment | **기각** — framework SSOT 자체 amendment 아니고 새 entry instantiation. ADR-060 amendment_log 가 framework 의 자연스러운 사용 사례 entry 추가 only (ADR-060 Amendment 4/5/6/7 패턴) — 본 lint 는 framework 의 사용 사례이지만 owner_adr 자체가 분리 도메인 (cross-section coherence) 이므로 별도 ADR carrier 적절 |

ADR-064 §결정 3 룰 1 derived default 적용 = (A) 권장.

## 결정

### §결정 1 — CLAUDE.md ADR amendment cross-ref drift mechanical lint 도입 (PR-time warning tier)

본 lint 가 detect 하는 drift pattern:

CLAUDE.md 본문 안 ADR cross-ref 단락 (예: `**Marketplace ↔ plugin.json atomic invariant** = [ADR-063](docs/adr/ADR-063-marketplace-atomic-invariant.md) — ...`) 가 inline 에 "Amendment N (CFP-NNN)" 형태 reference 를 포함한다. 본 lint 는:

1. CLAUDE.md 안 모든 `ADR-NNN` link line 식별도 (markdown link 패턴 `[ADR-073](docs/adr/ADR-073-orchestrator-verify-before-assert.md)` regex)
2. 같은 line 안 inline 패턴 매칭: `Amendment (\d+)` (예: `Amendment 3 §결정 13`)
3. 해당 ADR file frontmatter `amendment_log[]` 길이 fetch
4. inline reference 최대 Amendment N ≤ amendment_log length 검증 (stale = N > length, drift detect)
5. mismatch 시 warning 발화 (advisory, blocking 아님)

**효과**: CLAUDE.md narrative 가 ADR amendment 진행과 mechanical 하게 동기 검증. ArchitectAgent / Orchestrator 가 사후 보강해야 하는 cross-section coherence 의 PR-time detect.

### §결정 2 — lint scope = PR-time (pull_request event), scheduled cron 미도입

- **권장 = PR-time** (`pull_request` event, `paths: [CLAUDE.md, docs/adr/**]`) — fast feedback. drift 가 PR diff evidence 안 즉시 노출.
- 대안 = scheduled cron (CFP-627 marketplace drift detection 패턴). **기각** — drift = PR-time evidence 직접 visible (ADR amendment 변경 PR 동일하거나 다른 PR 어느 쪽이든 PR 시점 visible). scheduled 필요성 부재.

### §결정 3 — tier = warning (첫 도입, ADR-060 §결정 5 default 정합)

ADR-060 §결정 5 정합: 첫 도입 = warning tier. blocking-on-pr 승격은 별도 carrier (CFP-NNN). 승격 gate AND condition (ADR-060 §결정 6):

- `pr_cumulative_min: 20`
- `failure_threshold: 0` (warning mode 안 bypass 외 failure = 0)
- `sibling_dependencies: []` (현재 sibling carrier 부재)

`current_tier: warning` 첫 등록 후, 누적 PR ≥ 20 + clean run + 별도 promotion carrier merge 시 blocking-on-pr 승격 평가.

### §결정 4 — hotfix-bypass label = `hotfix-bypass:claude-md-amendment-ref` (per-entry namespace)

ADR-024 Amendment 3 §결정 6.A.1 per-entry namespace 정합. label-registry-v2 family 신규 entry append (`hotfix-bypass:claude-md-amendment-ref`). GitHub label 50자 제한 정합 (32자, OK). `check-bypass-audit-comment.sh` reuse pattern (1st-19th entry 동일).

### §결정 5 — owner_adr / carrier_adr 분리

- **owner_adr**: ADR-074 (본 ADR — cross-section coherence 도메인 SSOT)
- **carrier_adr**: ADR-060 (Evidence-enforceable framework SSOT)

evidence-checks-registry entry 등록 시 두 field 정합. `adr-sunset-criteria` (owner_adr: ADR-058 / carrier_adr: ADR-060) pattern 답습.

### §결정 6 — Phase 분배 (본 ADR Phase 1 PR scope vs Phase 2 mechanical artifact scope)

| 산출물 | Phase | 책임 |
|---|---|---|
| 본 ADR-074 (declarative SSOT) | Phase 1 | ArchitectAgent |
| Story CFP-708 §1-§7 | Phase 1 | ArchitectAgent (RequirementsPL skip — Issue body comprehensive + retro evidence base) |
| Change Plan §1-§13 | Phase 1 | ArchitectAgent |
| CLAUDE.md cross-ref expansion (1-3L) | Phase 1 | ArchitectAgent |
| `scripts/check-claude-md-amendment-ref.sh` | Phase 2 | DeveloperPL |
| `templates/github-workflows/claude-md-amendment-ref-drift.yml` | Phase 2 | DeveloperPL |
| `.github/workflows/claude-md-amendment-ref-drift.yml` (byte-identical self-app) | Phase 2 | DeveloperPL |
| `docs/evidence-checks-registry.yaml` row append (warning tier) | Phase 2 | DeveloperPL |
| `docs/inter-plugin-contracts/label-registry-v2.md` `hotfix-bypass:claude-md-amendment-ref` family member append (PATCH bump) | Phase 2 | DeveloperPL |
| `tests/check-claude-md-amendment-ref.bats` 5+ TC | Phase 2 | QADev |

ADR-065 §결정 1 #4 (link target Phase 분배 — Phase 1 PR doc 안 Phase 2 file 참조 시 dangling 차단) 정합 — 본 ADR-074 본문 안 Phase 2 file 참조는 모두 "Phase 2 carrier" 명시.

### §결정 7 — lint detection algorithm 의 false positive 안전망 (ADR-058 §결정 7 보안 ADR default false 정합)

Stale ref detect 의 false positive 영역 명시:

1. **inline pattern 외 ADR reference**: link target 만 있고 "Amendment N" 명시 없는 line (예: `[ADR-073](docs/adr/ADR-073-...md)`) → drift check skip (안전 — 명시적 stale 만 detect)
2. **multi-Amendment inline**: 같은 line 안 `Amendment 2 / Amendment 3` 처럼 다중 reference → 모두 amendment_log length 비교 (모두 stale 아님 확인). false positive 부재.
3. **frontmatter amendment_log 부재 ADR**: 신규 ADR 또는 amendment 0건 ADR → `Amendment N` reference 0건 자연스러움. mismatch 0 (false positive 부재).
4. **stale ref 에서 Amendment N = length 도 PASS**: 정확히 length 와 일치하면 PASS (latest amendment reference 정상).

### §결정 8 — sibling lint 와의 분리 운영

- **ADR-065** (mechanical syntactic 7-item) — Phase 1 산출물 commit 직전 self-check (label-registry sync / doc-locations regen / workflow self-app / link target / MANIFEST / section-ownership / doc-locations row). **Author-time self-check** (verdict packet `mechanical_self_check_passed: bool`).
- **ADR-068** (semantic 4-invariant + I-5 dimensional empirical) — Phase 1 산출물 §3/§7 semantic 검증 (API contract / cross-module propagation / guard placement / wording SSOT / quantitative empirical). **Author-time self-check** (verdict packet `boundary_completeness_self_check_passed` + `dimensional_empirical_self_check_passed`).
- **본 ADR-074** (mechanical cross-section coherence) — **CI-time (PR-time) lint** (CLAUDE.md narrative ↔ ADR amendment_log drift detect). Author-time 의무 아님 (post-commit CI mechanical detect).

3 ADR 가 author-time self-check (ADR-065/068) vs CI-time lint (ADR-074) layer 분리.

## 결과

### 긍정

- **Cross-section coherence drift 의 mechanical detect** — 2 occurrence (CFP-627 + CFP-477) reproduce 패턴 차단. 사후 보강 cost 의 PR-time evidence 회수.
- **CFP-263 doc-locations lint lineage 확장** — cross-section coherence lint family 확장 (별도 ADR pattern, ADR-041 doc-locations registry / ADR-065 mechanical self-check 와 같은 family member).
- **ADR-060 framework 9번째 warning-tier entry 등록** — framework 의 자연스러운 사용 사례 entry 추가 (CFP-481 / CFP-506 / CFP-610 / CFP-628 등 패턴 답습).
- **별도 ADR pattern boundary 명확화** — author-time self-check (ADR-065/068) vs CI-time lint (ADR-074) layer 분리. cross-validate path.

### 부정 / trade-off

- **첫 도입 = warning tier (advisory only)** — blocking-on-pr 승격까지 PR 누적 ≥ 20 + clean run 의무. 별도 promotion carrier 의존.
- **regex 기반 pattern matching 의 한계** — `Amendment N` inline 패턴 외 다른 reference style (예: "Amendment 2nd revision") detect 미커버. 본 §결정 1 regex 가 SSOT pattern.
- **non-marketplace 영역 한정** — marketplace.json sync 영역은 ADR-063 SSOT (cross-ref only). 중복 codification 회피 (ADR-065 §결정 5 boundary 정합).

### 영향 받는 file / layer

- `CLAUDE.md` 본문 — 본 lint 의 detect target (모든 ADR cross-ref 단락)
- `docs/adr/ADR-NNN-*.md` frontmatter `amendment_log[]` — 본 lint 의 SSOT comparison source
- `scripts/check-claude-md-amendment-ref.sh` — Phase 2 carrier (mechanical lint script)
- `templates/github-workflows/claude-md-amendment-ref-drift.yml` — Phase 2 carrier (workflow yaml)
- `docs/evidence-checks-registry.yaml` — Phase 2 carrier (9번째 warning-tier row append)
- `docs/inter-plugin-contracts/label-registry-v2.md` — Phase 2 carrier (`hotfix-bypass:claude-md-amendment-ref` family member append)

## 해소 기준

**N/A — permanent policy.**

본 ADR = `is_transitional: false` (governance permanent ADR). ADR-058 §결정 7 정합 (governance default presumption = false). cross-section coherence drift 자체가 영구 lint 영역 — sunset 영역 부재. blocking tier 승격 / supersede 의 경우만 별도 ADR 신설.

## 승격 gate (ADR-060 §결정 6)

본 entry 의 warning → blocking-on-pr 승격 평가 조건:

| Gate | 의무 | 측정 source |
|---|---|---|
| `pr_cumulative_min: 20` | PR 누적 ≥ 20 | `evidence-checks-registry.yaml` entry promotion_criteria field |
| `failure_threshold: 0` | bypass 외 failure = 0 (clean run 만) | GitHub Actions run history (`hotfix-bypass:claude-md-amendment-ref` label PR 제외) |
| `sibling_dependencies: []` | 현재 sibling carrier 부재 — 추후 carrier 진입 시 append | promotion carrier PR description |

**승격 carrier**: 별도 CFP-NNN (본 Story 외). ADR-058 §결정 5 ratchet 정합 (강화 방향 only).

## 사후 cross-ref

### 관련 ADR

- [ADR-012](ADR-012-wrapper-claudemd-ssot-boundary.md) — wrapper CLAUDE.md SSOT boundary. 본 lint 의 target file 정의.
- [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) — ADR sunset criteria mandate. frontmatter `amendment_log[]` 가 본 lint 의 comparison SSOT.
- [ADR-060](ADR-060-evidence-enforceable-promotion-framework.md) — Evidence-enforceable framework. 본 lint 가 9번째 warning-tier entry (carrier_adr).
- [ADR-063](ADR-063-marketplace-atomic-invariant.md) — Marketplace atomic invariant. CFP-477 F-DR-001 detection 의 stale ref source (Amendment 2 §결정 11 → 실제 Amendment 3 §결정 13).
- [ADR-065](ADR-065-architect-phase1-mechanical-self-check.md) — ArchitectAgent Phase 1 mechanical self-check. 자매 — author-time 7-item sync (ADR-065) vs CI-time cross-section coherence (ADR-074) layer 분리.
- [ADR-068](ADR-068-boundary-completeness-invariants.md) — Boundary completeness invariants. cousin — semantic completeness (ADR-068) vs mechanical drift (ADR-074) 분리.

### 관련 Story

- [CFP-708](https://github.com/mclayer/plugin-codeforge/issues/708) — 본 carrier (Phase 1 ADR + Phase 2 mechanical artifact).
- [CFP-627](https://github.com/mclayer/plugin-codeforge/issues/627) — 1차 evidence (pause-and-resume drift).
- [CFP-477](https://github.com/mclayer/plugin-codeforge/issues/477) — 2차 evidence (F-DR-001 P1 detection + retro §6 후보 3 ADR draft 발의).
- [CFP-263](https://github.com/mclayer/plugin-codeforge/issues/263) — doc-locations lint lineage 답습 (cross-section coherence lint pattern carrier).

### 관련 파일

- `CLAUDE.md` (본 lint target — wrapper plugin governance SSOT)
- `scripts/check-claude-md-amendment-ref.sh` (Phase 2 — Bash + python regex + jq amendment_log length parse)
- `templates/github-workflows/claude-md-amendment-ref-drift.yml` (Phase 2 — `pull_request` trigger)
- `.github/workflows/claude-md-amendment-ref-drift.yml` (Phase 2 — byte-identical self-app, ADR-005)
- `docs/evidence-checks-registry.yaml` (Phase 2 — 9번째 warning-tier entry row append)
- `docs/inter-plugin-contracts/label-registry-v2.md` (Phase 2 — `hotfix-bypass:claude-md-amendment-ref` family member append, PATCH bump)
- `tests/check-claude-md-amendment-ref.bats` (Phase 2 — 5+ TC: stale detect / latest match PASS / no-amendment-log PASS / multi-Amendment inline / bypass label skip)
