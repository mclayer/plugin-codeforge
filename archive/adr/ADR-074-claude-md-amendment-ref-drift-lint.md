---
adr_number: 74
title: CLAUDE.md Amendment ref drift detection lint — cross-section coherence between ADR amendment_log and CLAUDE.md narrative
status: Proposed
category: governance
date: 2026-05-14
amended_by: CFP-1009  # Amendment 1 carrier — regex precision (option (b) Same-line strict pure)
amended_date: 2026-05-20
is_transitional: false
carrier_story: CFP-708
supersedes: []
amends: []
related_adrs:
  - ADR-012  # wrapper CLAUDE.md SSOT boundary — CLAUDE.md 본문이 본 lint scope target file
  - ADR-058  # ADR sunset criteria mandate — frontmatter amendment_log 가 drift 비교 SSOT (Amendment 1 sunset_justification 의무 source)
  - ADR-060  # Evidence-enforceable promotion framework — 본 lint 가 9번째 warning-tier entry
  - ADR-061  # Python script-writing convention — Amendment 1 의 외부 .py 답습 정합 source
  - ADR-063  # Marketplace atomic invariant — CFP-477 F-DR-001 detection 의 stale ref source (Amendment 2 §결정 11 → 실제 Amendment 3 §결정 13)
  - ADR-064  # Decision principle mandate — Amendment 1 의 derived default + 권장 1 + 대안 1 patterning source
  - ADR-065  # ArchitectAgent Phase 1 mechanical self-check — 7-item mechanical sync 의 자매 (cross-section coherence 확장)
  - ADR-068  # Boundary completeness invariants — I-4 wording SSOT 와 cousin (semantic 검증 vs mechanical 검증 분리)
  - ADR-082  # Write-time self-write verification mandate — Amendment 1 carrier (CFP-1009) §2.2 mid-author catch 의 scope (b) 실 사례
related_stories:
  - CFP-708  # 본 carrier
  - CFP-627  # 1차 evidence (pause-and-resume drift, CLAUDE.md line 296 stale)
  - CFP-477  # 2차 evidence (F-DR-001 P1 detection)
  - CFP-263  # doc-locations lint lineage (cross-section coherence pattern 답습)
  - CFP-1000  # Amendment 1 evidence (CFP-1000 1st false-pair occurrence — L189 phantom-ahead)
  - CFP-1001  # Amendment 1 escalation carrier (CFP-1001 retro pattern_count = 2 reach, ADR-045 §D-9 mandate)
  - CFP-1009  # Amendment 1 carrier (regex precision option (b) Same-line strict pure, post-Codex TP#2 FIX iter 1)
related_files:
  - CLAUDE.md
  - scripts/check-claude-md-amendment-ref.sh  # Phase 2 carrier
  - scripts/lib/check_claude_md_amendment_ref.py  # Amendment 1 primary algorithm touch
  - tests/scripts/check-claude-md-amendment-ref.bats  # Amendment 1 TC-6/7/8 carrier
  - templates/github-workflows/claude-md-amendment-ref-drift.yml  # Phase 2 carrier
  - .github/workflows/claude-md-amendment-ref-drift.yml  # Phase 2 self-app
  - docs/evidence-checks-registry.yaml  # Phase 2 row append (Amendment 1 invariant — tier 보존)
  - docs/inter-plugin-contracts/label-registry-v2.md  # Phase 2 hotfix-bypass label entry
mechanical_enforcement_actions:
  - name: claude-md-amendment-ref-drift-check
    target: CLAUDE.md ADR amendment cross-reference lines
    detection: bash scripts/check-claude-md-amendment-ref.sh
    enforcement_workflow: templates/github-workflows/claude-md-amendment-ref-drift.yml
    bypass_label: hotfix-bypass:claude-md-amendment-ref
    audit_lint: bash scripts/check-bypass-audit-comment.sh
    current_tier: warning  # ADR-060 §결정 5 — 첫 도입 default (Amendment 1 invariant — tier 변경 0)
amendment_log:
  - amendment: 1
    carrier_story: CFP-1009
    date: 2026-05-20
    summary: "Regex precision — option (b) Same-line strict pure. ±5-line cross-context window → same-line equality (line-equality only). False-pair root cause = cross-bullet contamination (both L189 phantom and L281 stale). Codex TP#2 mandatory touchpoint #2 catch reverted earlier (b+h) hybrid draft. bats TC-1/3/4/5 fixture rewrite (adjacent-line → same-line join) preserves assertion semantics. Address CFP-1000 (L189 phantom-ahead) + CFP-1001 (L281 stale-behind) pattern_count = 2 escalation. AC-1 (false-pair = 0) + AC-5 (test intent invariant + fixture-format adaptive) + AC-8 (self-amend, no new ADR)."
    sunset_justification: "N/A — ratchet-strengthen direction (precision 강화). scope 약화 0, false-pair retention 0, detection capability 0 weakening. ADR-058 §결정 5 strengthening direction invariant 정합."
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

CLAUDE.md 본문 안 ADR cross-ref 단락 (예: `**Marketplace ↔ plugin.json atomic invariant** = [ADR-063](ADR-063-marketplace-atomic-invariant.md) — ...`) 가 inline 에 "Amendment N (CFP-NNN)" 형태 reference 를 포함한다. 본 lint 는:

1. CLAUDE.md 안 모든 `ADR-NNN` link line 식별도 (markdown link 패턴 `[ADR-073](ADR-073-orchestrator-verify-before-assert.md)` regex)
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

1. **inline pattern 외 ADR reference**: link target 만 있고 "Amendment N" 명시 없는 line (예: `[ADR-073](ADR-073-orchestrator-verify-before-assert.md)`) → drift check skip (안전 — 명시적 stale 만 detect)
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

## Amendment 1 (CFP-1009, 2026-05-20 KST) — Regex precision: Same-line strict pure

> **REVISION NOTE (Amendment 1 FIX iter 1, 2026-05-20 23:30 KST)** — Codex TP#2 proactive review (ADR-052 Amendment 4 mandatory touchpoint #2 post-§3) returned 2 P1 findings. ADR-070 verify-before-trust empirical reproduction (Python regex `Amendment\s+(\d+)\s*\(CFP-\d+\)` on CLAUDE.md L185/189/279/281) confirmed **both TRUE POSITIVE**. Original drafted option = (b+h) Dual-anchor + historical reference. Revised option after FIX = **(b) Same-line strict pure**. 두 false-pair 모두 cross-bullet contamination (regex 매칭 cite 가 cross-bullet ±5 window 안 진입) mechanism, historical reference recognition (option h) 의 적용 영역 0 occurrence (L279/L281 의 self-cite 가 date-suffixed canonical form `(CFP-NNN, YYYY-MM-DD)` 으로 regex 자체가 미매칭).

### 배경

CFP-708 base lint 가 도입한 ±5-line cross-context window pairing 알고리즘 (Python helper L174~L194) 이 wrapper CLAUDE.md narrative 의 dense bullet structure 안에서 **cross-bullet contamination false-pair** 를 2 occurrence 생성. CFP-1001 retro (ADR-045 Amendment 5 §D-9 mandatory framing, pattern_count = 2 reach) 의 escalation_action `adr_draft_emitted` 결과 본 Amendment 발의.

**2 occurrence sentinel** (ArchitectPL Python regex empirical reproduction verified):

1. **CFP-1000 1st** — `CLAUDE.md L189` (TodoWrite narrative bullet, `[ADR-038](docs/adr/ADR-038-progress-visualization-todowrite.md)` literal markdown link) + ±5 window L184~L194 안 **L185** cite `**Amendment 6 (CFP-843)**` (canonical regex 매칭 form) → cross-pair → `ADR-038 Amendment 6 claim is phantom (ahead)` (ADR-038 frontmatter `amendments[]` length = 4) **false-pair (cross-context contamination)**.
2. **CFP-1001 2nd** — `CLAUDE.md L281` (Evidence-enforceable framework bullet, `[ADR-060](docs/adr/ADR-060-evidence-enforceable-promotion-framework.md)` literal markdown link) + ±5 window L276~L286 안 **L283** cite `**Amendment 1 (CFP-841)**` (canonical regex 매칭 form, ADR-082 narrative bullet 안) → cross-pair → `ADR-060 Amendment 1 claim is stale (behind)` (ADR-060 frontmatter `amendment_log[]` length = 14) **false-pair (cross-context contamination)**.

L281 line 자체의 self-cite `Amendment 1 (CFP-390, 2026-05-11)` 은 date-suffixed canonical form 으로 regex `\(CFP-\d+\)` 미매칭 (CFP-390 직후 `,` 가 따라옴) → lint algorithm 의 인식 영역 외, false-pair source 아님.

### §결정 9 — Algorithm precision: Same-line strict pure (option (b))

본 Amendment 가 도입하는 algorithm = **option (b) Same-line strict pure** (CFP-1009 Change Plan §3.1 채택, post-FIX iter 1):

```
for each line L in CLAUDE.md:
  for each [ADR-N](...) literal markdown link match on line L (regex \[ADR-(\d+)\]\([^)]+\)):
    for each "Amendment M (CFP-K)" canonical cite match on same line L (regex Amendment\s+(\d+)\s*\(CFP-\d+\)):
      pair (ADR-N, M, line=L) emit
      look up ADR-N frontmatter amendment_log[] / amendments[] length actual_count:
        case a — actual_count == 0 AND M > 0:
          → [DRIFT] no amendment_log
        case b — M == actual_count [latest]:
          → [OK matches latest]
        case c — M > actual_count [phantom-ahead]:
          → [DRIFT phantom (ahead)]
        case d — M < actual_count [stale-behind]:
          → [DRIFT stale (behind)]
```

**핵심 변경 1종**:

1. **±5 window → same-line strict** (option b 의 핵심) — Python helper L180~L182 region. `context_start = line_idx` / `context_end = line_idx + 1`. 11-line cartesian pairing 제거, line-equality only.

**변경 0건** (FIX iter 1 simplification):

- regex 변경 0 — `amend_re = Amendment\s+(\d+)\s*\(CFP-\d+\)` 보존 (current capture group 1 = Amendment N 의미 동일).
- helper 신설 0 — `_match_historical_amendment` / `_get_amendment_entries` 신설 제거. 기존 `_get_amendment_count` length-only API 보존.
- output classification 변경 0 — 기존 4종 분류 (`OK matches latest` / `DRIFT phantom (ahead)` / `DRIFT stale (behind)` / `DRIFT no amendment_log` + setup-error) 보존. 신규 `[OK historical]` 분류 도입 제거 (vacuous coverage).

### §결정 10 — sunset_justification (ADR-058 §결정 5 정합)

본 Amendment = **ratchet-strengthen direction** (false-pair precision 강화, scope 약화 0). 약화 영역 enumeration:

- detection capability 약화: **0** (legitimate phantom-ahead / stale-behind 모두 retain — TC-1 fixture 가 stale 시나리오 검증, post-rewrite GREEN).
- scope 축소: **0** (lint scope = wrapper CLAUDE.md 만 유지, consumer overlay 미진입 invariant 보존).
- tier 약화: **0** (warning tier 유지, blocking 미승격, evidence-checks-registry schema 변경 0).
- bypass label 약화: **0** (`hotfix-bypass:claude-md-amendment-ref` 보존).

→ **sunset_justification: "N/A — strengthening direction. ratchet 강화 (precision 강화, scope/detection/tier/bypass 모두 약화 0)."**

ADR-058 §결정 5 sunset_justification 의무 정합.

### §결정 11 — option choice rationale (ADR-064 §결정 3 룰 2, post-FIX iter 1)

**옵션 dump 금지 — 권장 1 안 + 대안 1 안 명시**:

- **권장 = option (b) Same-line strict pure** (본 §결정 9) — 두 false-pair (L189 + L281) 모두 cross-bullet contamination mechanism. same-line strict 만으로 두 false-pair 모두 해결 (link line 안 same-line canonical cite 0건 → 0 pair → drift 미출력). AC-1 (false-pair = 0) + AC-5 (test intent invariant + fixture-format adaptive) 동시 달성.
- **대안 = option (c) Per-ADR scope (semantic anchor binding)** — narrative bullet anchor ADR implicit semantic ownership. CLAUDE.md narrative complexity 향후 증가 시 신규 CFP 로 전환. CFP-1009 시점 multi-ADR same-line `[ADR-N]` literal link 0 occurrence → (c) 의 추가 가치 = 향후 future-proofing 만 (CFP-1009 §5.3 EC-7 carrier).
- **제외 = option (b+h) Dual-anchor with historical reference recognition** — original ArchitectAgent §2.2 초안의 hybrid option. ArchitectPL FIX iter 1 의 Python regex empirical reproduction 가 L279/L281 self-cite 가 date-suffixed canonical form 으로 regex 미매칭 임을 확인 → historical match 의 적용 영역 0 occurrence at current CLAUDE.md state → (h) layer vacuous → 제거. 향후 narrative author 가 date-suffix 없는 `Amendment N (CFP-K)` same-line self-reference 등장 시 신규 CFP 로 재발의.
- **제외 = option (a) Same-line strict 단독 (window ±5 → ±0) without (b) dual-anchor structure** — option (b) 와 본질적으로 동일하나 dual-anchor structure (link + cite paired emit) 명시성 부족. 본 Amendment 의 option (b) = (a) 의 same-line strict + (b) 의 dual-anchor emit pattern 명시.

### §결정 12 — fixture / TDD design (TC-6/7/8 신설 + TC-1/3/4/5 line-join rewrite, AC-3 + AC-5 정합)

본 Amendment 의 Phase 2 산출물 (CFP-1009 단일 PR scope) 안:

**A. 신규 bats test 3종 (AC-3)**:

- **TC-6 phantom-ahead (cross-context contamination 해결 verify)**: fixture CLAUDE.md 안 line A 의 `[ADR-A](...)` literal link + line A 안 same-line canonical cite 부재 + line A+2 narrative cite `Amendment N (CFP-X)` (N > ADR-A frontmatter length, ±5 window 안 cross-pair source) → option (b) same-line strict 적용 시 line A 0 pair generated → exit 0 + drift 미출력.
- **TC-7 stale-behind (cross-context contamination 해결 verify)**: fixture 안 line B 의 `[ADR-B](...)` literal link + line B 안 same-line canonical cite 부재 + line B+1 narrative cite `Amendment 1 (CFP-Y)` (B+1 = ±5 window 안) → option (b) 적용 시 line B 0 pair generated → exit 0 + drift 미출력.
- **TC-8 legitimate same-line drift verify**: fixture 안 line C 의 `[ADR-C](...)` literal link + line C 안 same-line canonical cite `Amendment 2 (CFP-Z)` + ADR-C frontmatter `amendment_log[]` length = 5 → option (b) 적용 시 same-line pair → `Amendment 2 < 5` → exit 1 + `[DRIFT stale (behind)]` 출력 (legitimate drift retained).

**B. TC-1/3/4/5 fixture line-join rewrite (AC-5 backward compat)**:

기존 (CFP-708 base) fixture 가 link line + cite line 의 adjacent-line form:

```
**Marketplace atomic invariant** = [ADR-063](docs/adr/ADR-063-...)
(Amendment 2 (CFP-631) §결정 11 신설 ...)
```

option (b) same-line strict 적용 시 0 pair → exit 0 → TC-1/3/4/5 backward FAIL. Phase 2 fixture rewrite (line-join):

```
**Marketplace atomic invariant** = [ADR-063](docs/adr/ADR-063-...) (Amendment 2 (CFP-631) §결정 11 신설 ...)
```

assertion semantics (exit code + drift message presence + ADR identifier mention) 보존. author 본래 narrative intent (link + cite = same bullet) 보존, single-bullet/multi-line layout → single-bullet/single-line layout 의 trivial re-format.

### §결정 13 — backward compatibility (AC-5 invariant, post-FIX iter 1)

TC-1 ~ TC-5 (CFP-708 base) 의 **test intent (assertion semantics)** 모두 보존 + **fixture-format** 은 same-line strict 적용 영역으로 rewrite. 두 차원의 backward compat dual condition:

- **TC-1 stale (post-rewrite)**: link + cite same-line + length=4 + claimed=2 → same-line pair → `Amendment 2 < 4` → `[DRIFT stale (behind)]` → exit 1 + drift message + ADR-063 mention (정합).
- **TC-2 latest**: 기존 fixture 도 link + cite same-line (verify-needed in Phase 2) — same-line strict 적용 시 latest match → `[OK]` → exit 0 (정합).
- **TC-3 no-amendment-log (post-rewrite)**: link + cite same-line + length=0 + claimed=1 → `Amendment 1 > 0` → drift (no amendment_log path) → exit 1 + ADR-999 mention (정합).
- **TC-4 multi-Amendment (post-rewrite)**: 20-line separation 보존 (각 sub-block 안 link + cite same-line) → ADR-060 cite `Amendment 2 (CFP-455)` length=8 → stale (M=2<8) → exit 1 + ADR-060 drift. ADR-999 cite `Amendment 1 (CFP-500)` length=1 → latest → `[OK]`. 종합 exit 1 (drift 1건 존재) + ADR-060 drift assertion (정합).
- **TC-5 setup-error (post-rewrite)**: link + cite same-line + ADR file 부재 → exit 2 + setup-error (정합).

→ AC-5 invariant 만족 (test intent + fixture-format dual condition).

### §결정 14 — Phase 분배 (CFP-1009 carrier scope, post-FIX simplification)

| 산출물 | Phase | 책임 | 비고 |
|---|---|---|---|
| 본 ADR-074 Amendment 1 (declarative SSOT, 본 단락) | Phase 1 | ArchitectAgent (direct write) | CFP-26 Phase 0a owner direct write 정합. |
| CFP-1009 Change Plan §3.1 (option (b) Same-line strict pure algorithm 정의) | Phase 1 | ArchitectAgent | wrapper `docs/change-plans/cfp-1009-amendment-ref-regex-precision.md`. |
| CFP-1009 Story file §3 reference + §7/§11/§13 N/A + §9.0 Codex TP#2 trail + §10 FIX Ledger row | Phase 1 | ArchitectPLAgent | internal-docs `wrapper/stories/CFP-1009.md`. |
| `scripts/lib/check_claude_md_amendment_ref.py` algorithm 정밀화 | Phase 2 | DeveloperAgent | ~5 lines (L180~L182 same-line strict edit). |
| `tests/scripts/check-claude-md-amendment-ref.bats` TC-1/3/4/5 line-join rewrite + TC-6/7/8 신설 | Phase 2 | QADeveloperAgent | ~150 lines (5 TC fixture rewrite ~30 + 3 신규 TC ~120). |

ADR-065 §결정 1 #4 (link target Phase 분배 — Phase 1 doc 안 Phase 2 file 참조 시 dangling 차단) 정합. 본 Amendment 1 본문 안 Phase 2 file 참조 모두 "Phase 2 carrier" 명시.

### Result — false-pair 0 + true-drift retention 정량 (post-FIX iter 1)

Phase 2 merge 후 AC-1 verify:

- **CLAUDE.md 현 (HEAD `6f54c64`) lint baseline (pre-fix)** — 4 lines: L185 OK / **L189 DRIFT phantom (ahead) `ADR-038 Amendment 6`** / L279 OK / **L281 DRIFT stale (behind) `ADR-060 Amendment 1`**.
- **post-fix expected output (option (b) Same-line strict pure)** — 1 line: L185 OK (link `[ADR-040]` + same-line canonical cite `Amendment 6 (CFP-843)` + frontmatter length=6 → latest match).
  - L189: link `[ADR-038]` + same-line canonical cite 0건 (`Amendment 4 vocab swap` / `Amendment 1 §결정 8` 모두 parenthetical CFP form 미충족, regex 미매칭) → 0 pair → 미출력.
  - L279: link `[ADR-068]` + same-line canonical cite 0건 (`Amendment 1 (CFP-528, 2026-05-13)` date-suffixed form regex 미매칭) → 0 pair → 미출력.
  - L281: link `[ADR-060]` + same-line canonical cite 0건 (`Amendment 1 (CFP-390, 2026-05-11)` date-suffixed form regex 미매칭) → 0 pair → 미출력.
- **false-pair count: 0** → AC-1 satisfied.
- **lint exit code post-fix: 0** (clean) — L185 OK only.
- **legitimate drift retain**: Phase 2 후 신규 legitimate stale 발생 시 (예: 새 ADR Amendment 도입 후 CLAUDE.md narrative `[ADR-N](...)` link + same-line canonical cite `Amendment M (CFP-X)` 의 M 가 frontmatter length 와 mismatch 시) → `[DRIFT stale (behind)]` 또는 `[DRIFT phantom (ahead)]` 정상 출력. 본 capacity = TC-8 / TC-1-rewrite verified.

---

## 관련 파일

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
