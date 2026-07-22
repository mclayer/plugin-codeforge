---
adr_number: 108
title: label-registry-v2 description text family member count raw-grep forcing function (frozen baseline ↔ derived view dual-frame)
status: Active
category: governance
date: 2026-05-24
carrier_story: CFP-1346
parent_epic: null
supersedes: null
amends: null
amendments: []
amendment_log:
  - amendment_id: 1
    status: Active
    date: 2026-05-24
    cfp: CFP-1346
    summary: 초안 신설 — dual-frame Event Sourcing/CQRS normative codify (frozen historical narrative + dynamic forcing function) + label-registry-frozen-baseline-count-parity warning-tier lint mechanical_enforcement_actions 1 entry declare (Phase 2 wire = sibling sub-Story carrier).
related_adrs:
  - ADR-008   # inter-plugin contract versioning + §결정 2 v1.x backward-compatible 변경 룰 (additive entry append = MINOR bump 정합, 본 ADR-108 = append axis 의 description text count sub-axis 신설)
  - ADR-010   # §결정 3 kind:registry scope limitation (kind:contract MANIFEST scope 외 — label-registry-v2 = kind:registry → ADR-108 발효 후에도 sibling sync 면제 retain)
  - ADR-058   # sunset criteria mandate (§결정 5 sunset_justification 면제 — ratchet 강화 방향)
  - ADR-060   # evidence-enforceable promotion framework (4-tier — warning-tier deferred-followup 첫 entry)
  - ADR-064   # decision principle mandate (§결정 5 CFP scope unitary + §결정 7 evidence-gated symmetric ratchet)
  - ADR-073   # Orchestrator verify-before-assert (forcing function = verify-before-trust grep-count sub-scope axis-instantiation)
  - ADR-082   # write-time self-write verification mandate (axis disjoint sibling — author claim verify axis ≠ description text count parity axis)
  - ADR-045   # §D-9 cross_story_pattern_adr_trigger pattern_count ≥ 2 reach Mandatory escalation_action: adr_draft_emitted carrier
  - ADR-107   # Plugin declarative seed drift detection (adjacent concept — plugin file declarative seed drift vs description text count drift, sibling carrier pattern 답습 — collision rebase ratchet precedent row 107)
related_adrs_amendments:
  - ADR-082 Amendment 7   # CFP-1312 verify-before-cite 양방향 (sibling axis — 본 ADR-108 description text count parity write-time verify 의 대칭 backward-staleness lint)
related_stories:
  - CFP-1346   # 본 carrier (standalone Story, parent_epic null)
related_files:
  - docs/inter-plugin-contracts/label-registry-v2.md
  - docs/inter-plugin-contracts/MANIFEST.yaml
  - docs/evidence-checks-registry.yaml
  - scripts/check-label-registry-frozen-baseline-count-parity.sh  # Phase 2 wire target
  - templates/github-workflows/label-registry-frozen-baseline-count-parity.yml  # Phase 2 wire target
  - .github/workflows/label-registry-frozen-baseline-count-parity.yml  # Phase 2 wire target self-app
  - tests/scripts/cfp-1346/check-label-registry-frozen-baseline-count-parity.bats  # Phase 2 wire target
is_transitional: false
mechanical_enforcement_actions:
  - label-registry-frozen-baseline-count-parity
sunset_justification: null
---

# ADR-108: label-registry-v2 description text family member count raw-grep forcing function (frozen baseline ↔ derived view dual-frame)

## 상태

Active (2026-05-24 KST) — ADR-045 §D-9 `cross_story_pattern_adr_trigger` (pattern_count=2, threshold N=2 reach, escalation_action=adr_draft_emitted) Mandatory ADR escalation 산물. CFP-604 retro F6 (sentinel #1, label-registry-v2 description text "70번째" frozen baseline) + CFP-1302 retro §5.1 (sentinel #2, "73번째" frozen baseline 후 raw active 차이) 2회 누적 동형 drift super-class 차단 mechanism layer 신설.

## 컨텍스트

### Drift super-class 정의

label-registry-v2.md `§3 yaml block` 안 `hotfix-bypass:*` entry description text 의 "N번째 hotfix-bypass:* family member" claim 은 **append 시점 raw active concrete grep count** 박제 (frozen baseline) 의 형태로 codify 되어 있다. 이 claim 은 **derived metric** (현재 시점 raw active hotfix-bypass:* entry 개수) 의 snapshot 인데, 후속 append 시점 (sister Story 가 새 entry 추가 시) source-of-truth 가 갱신되지 않아 derived view 와 frozen citation 간 drift 가 누적된다.

### 사용자 원문 (CFP-1346 사용자 verbatim — story-section-1-immutable.yml 보호)

> Mandatory ADR escalation — CFP-1302 retro §5.1 pattern_count=2 reach (anchor `label-registry-v2-frozen-baseline-description-carry-drift`).
>
> scope: codeforge convention 영역의 label-registry-v2.md description text frozen baseline (append 시점 raw grep count) vs raw grep count drift 결정. 신규 ADR file + ADR-RESERVATION row + mechanical_enforcement_actions[] (lint script + workflow + bats fixture) + future append rule (description count = raw grep count post-append forcing function).

### 2회 누적 evidence (ADR-045 §D-9 cross_story_pattern_adr_trigger Mandatory reach)

| Sentinel # | Story | description text frozen baseline | 박제 시점 | raw active baseline post-append |
|---|---|---|---|---|
| **#1** | CFP-604 (retro F6 Wave 2 carrier) | `architect-marketplace-self-check` entry: `"70번째 hotfix-bypass:* family member"` (label-registry-v2.md L1503) | v2.51 baseline (CFP-604 append 시점) | 70 (CFP-604 frozen baseline) |
| **#2** | CFP-1302 (retro §5.1) | `auto-cleanup-stale-gate` entry: `"73번째 hotfix-bypass:* family member"` (label-registry-v2.md L1511) | v2.52 baseline (CFP-1302 append 시점) | 73 (CFP-1302 frozen baseline) |

post-CFP-1302 시점 raw active hotfix-bypass:* entry = **73** (verified via `grep -c '^  - name: hotfix-bypass:'`). CFP-604 시점 "70번째" claim 은 **frozen audit trail** 정합 (당시 70개 baseline). CFP-1302 시점 "73번째" claim 도 **frozen audit trail** 정합 (당시 73개 baseline, 사이에 2개 append). pattern_count=2 → ADR-045 §D-9 Mandatory escalation 의무 충족.

### Researcher dual-frame Event Sourcing/CQRS framing

(Researcher Section 6 cite [hypothesis] — Phase 0 brainstorm input):

- **Event Sourcing (Fowler 2005)** ↔ **frozen baseline citation**: immutable event log + derived state. Append-only ledger entry immutable (append 시점 박제), aggregate metric (current cumulative count) = derived view.
- **CQRS (Young 2010)** ↔ **derived view vs source-of-truth**: write model (entry list = label-registry-v2 §3 yaml block) vs read model (count = raw grep). SQL `COUNT(*) OVER ()` window function 정합.
- **Property-based testing invariant** ↔ **forcing function via mechanical lint**: `description_claim_N == raw_grep(yaml).count` (단, append-time write-time invariant 한정 — historical entry retroactive 영역 외).

### Drift 도메인 경계 (3-axis disjoint)

| Axis | 영역 | SSOT carrier |
|---|---|---|
| **A. version field SSOT** | label-registry-v2.md frontmatter `version: "2.52"` + MANIFEST.yaml row `version: "2.52"` | Additive-merge pattern I-1 (frontmatter version monotonic invariant) |
| **B. version drift (frontmatter ↔ MANIFEST)** | INV-1 parity lint (`check_inter_plugin_contracts_parity.py`) | ADR-065 Amendment 4 |
| **C. description text count claim** (본 ADR-108) | label-registry-v2.md §3 yaml entry `description: "... N번째 hotfix-bypass:* family member"` 안 count claim 의 박제 시점 raw grep count 정합 | **본 ADR-108** (axis C 신설 carrier — 미codified disjoint axis) |

본 ADR-108 = **axis C** (3번째 disjoint axis) 신설 carrier. axis A (version SSOT) + axis B (INV-1 parity) 는 기 정의 영역, 본 Story scope 외.

## 결정

### 결정 1 — SSOT axis dual-frame normative codify (frozen historical narrative + dynamic forcing function 분리)

label-registry-v2.md `§3 yaml block` 안 `hotfix-bypass:*` entry description text 의 "N번째 hotfix-bypass:* family member" claim 영역을 **dual-frame Event Sourcing/CQRS 패턴** 으로 normative codify:

**(A) Historical narrative = frozen audit trail** (Event Sourcing immutable event log 정합):
- Prior entry description text "N번째" citation = append 시점 박제 raw active count (frozen-at-append-time invariant)
- 후속 append 시점 retroactive cleanup 금지 (historical narrative audit trail 보존)
- wording-dictionary "박제" / "frozen" forbid 의 정상 영역 **아님** — historical event payload immutable per Event Sourcing pattern (ADR-064 Amendment 5 per-word scope decoupling 정합 — governance ADR amendment_log 박제 forbid 영역과 disjoint sub-scope, wording-dictionary 카테고리 (a) `별` standalone scope `docs/adr/**` + `docs/change-plans/**` + `CLAUDE.md` + `docs/orchestrator-playbook.md` + `templates/**` 5 영역 한정과 axis disjoint)

**(B) NEW entry (append-time) = description text count = raw grep count post-append** (CQRS derived view / property invariant 정합):
- 신규 entry append 시점 작성하는 description text 의 "N번째 hotfix-bypass:* family member" citation = `grep -c '^  - name: hotfix-bypass:' docs/inter-plugin-contracts/label-registry-v2.md` post-append count 정합 의무 (forcing function rule)
- write-time invariant — 작성 시점 raw active grep count + new entry = post-append count 검증

본 dual-frame 분리 = **"frozen ↔ dynamic" 양자택일 false dichotomy 해소** (Researcher §6 Refined Requirement R-1 정합).

### 결정 2 — Forcing function rule (append-time write-time invariant)

label-registry-v2.md `§3 yaml block` 안 신규 `hotfix-bypass:*` entry append 시 다음 invariant 충족 의무:

```
description text "N번째 hotfix-bypass:* family member" 안 N
==
grep -c '^  - name: hotfix-bypass:' docs/inter-plugin-contracts/label-registry-v2.md  (post-append count)
```

**Write-time invariant**:
- ArchitectAgent / Orchestrator / GitOpsAgent 등 author 가 신규 entry append 시 commit 직전 raw grep count 재verify 의무
- mismatch detect 시 author 직접 정정 (description text N 갱신)
- Phase 2 wire = `label-registry-frozen-baseline-count-parity` warning-tier lint 가 mechanical pre-screen

**Retroactive 영역 외** (결정 1 (A) historical narrative 정합):
- Prior frozen entry retroactive cleanup 금지
- 신규 append-time entry 만 본 forcing function 적용

### 결정 3 — Mechanical enforcement (warning-tier lint 1 entry)

`mechanical_enforcement_actions: [label-registry-frozen-baseline-count-parity]` (1 entry, warning-tier, deferred-followup Wave 1 — Phase 2 sibling sub-Story carrier wire):

| 영역 | 산출물 | Phase |
|---|---|---|
| lint script | `scripts/check-label-registry-frozen-baseline-count-parity.sh` | Phase 2 wire |
| Python core logic (선택) | `scripts/lib/check_label_registry_frozen_baseline_count_parity.py` (regex precision 복잡 시 ADR-061 §결정 1 정합 — multi-line Python > 5줄 시 외부 .py 의무) | Phase 2 wire |
| workflow | `templates/github-workflows/label-registry-frozen-baseline-count-parity.yml` + `.github/workflows/<same>.yml` self-app byte-identical (ADR-005 + ADR-065 §결정 1 row 3) | Phase 2 wire |
| bats fixture | `tests/scripts/cfp-1346/check-label-registry-frozen-baseline-count-parity.bats` | Phase 2 wire |
| evidence-checks-registry entry | `docs/evidence-checks-registry.yaml` — `label-registry-frozen-baseline-count-parity` row append | Phase 1 (본 Story) |
| bypass label | `hotfix-bypass:label-registry-frozen-baseline-count-parity` — **74번째 hotfix-bypass:* family member** (META self-application 1st applied case) | Phase 1 (본 Story) |
| tier | `warning` (ADR-060 framework 19 entry precedent 답습 — default 새 entry pattern) | Phase 1 declare |

**lint regex precision** (false_positive 차단 — Researcher §6.3 knowledge gap 2 정합):
- Catch pattern (exact form): `\d+번째 hotfix-bypass:\* family member`
- False positive boundary: prior frozen entry description "5번째 verdict-level optional bool field" / "4번째 tier" 등 non-`hotfix-bypass:*` count semantic 영역 미catch

### 결정 4 — Historical cleanup hybrid Option C (prior frozen 유지 + 신규 append 만 forcing function)

- prior frozen entries (45번째 / 47번째 / 70번째 / 73번째 등 frozen-at-append 시점 박제, ADR-064 Amendment 5 historical narrative audit trail 보존 영역) **retroactive 정정 0건**
- 신규 append-time entry 만 결정 2 forcing function 적용
- destructive historical sweep 영역 외 — 필요 시 별도 follow-up CFP carrier (사전 evidence accumulate 후)

근거: Event Sourcing immutable event log 정합 (결정 1 (A)), historical audit trail 보존 의무 (governance accountability).

### 결정 5 — ADR axis disjoint ADR-082 (axis 분리 정당, sequential composition cross-ref OK)

본 ADR-108 = description text count parity axis (write-time **output** anchor — label-registry-v2.md §3 yaml entry description text 안 N number citation).

vs **ADR-082** = author claim verify axis (write-time **input** anchor — USER-UTTERANCE-VERBATIM block citation / spawn prompt 안 fact claim).

| Axis | Anchor | Scope |
|---|---|---|
| ADR-082 §결정 1 layer 1 sub-scope 1-C | write-time INPUT anchor | spawn prompt USER-UTTERANCE-VERBATIM block 안 user fact claim verify |
| ADR-108 §결정 2 forcing function | write-time OUTPUT anchor | label-registry-v2.md §3 yaml entry description text 안 N number citation verify |

axis 분리 정당 — sequential composition cross-ref OK (ADR-082 verify-before-trust pattern 의 axis-instantiation 가능 영역). Amendment N 동반 0 (ADR-082 본문 무변경 invariant).

**ADR-082 Amendment 7 sibling axis** (CFP-1312 — §결정 9 verify-before-cite scope 양방향 확장):
- ADR-082 Amd 7 = backward-staleness lint (prior cite reference 가 후속 fact 갱신 시점 stale 인지 backward verify)
- ADR-108 = forward-parity lint (write-time fact citation 이 post-append raw fact 와 parity 인지 forward verify)
- 양 axis = verify-before-trust 의 사실 input layer 의 대칭 pair — 별도 follow-up CFP carry-over carrier 가능 영역 (description count parity 가 verify-before-cite specific axis instantiation 후보, 본 ADR-108 scope 외)

### 결정 6 — META self-application invariant (1st applied case dogfood loop close)

본 ADR-108 rule 의 **1st applied case = 본 Story (CFP-1346) Phase 1 PR**:

- 본 Phase 1 PR 동반 신규 label-registry-v2.md entry append: `hotfix-bypass:label-registry-frozen-baseline-count-parity` (74번째 family member)
- description text 안 citation 의무 = `"74번째 hotfix-bypass:* family member"` (post-CFP-1302 v2.52 baseline raw active 73 + new 1 = 74)
- ArchitectAgent commit 직전 raw grep count 재verify 의무 (collision rebase ratchet 시 N 갱신)

**dogfood loop close**: ADR-108 신설 의무 ↔ 본 Story 자체 = 1st applied case + Phase 2 wire 후 self-check PASS (메타 self-application pattern — memory `feedback_meta_self_application_pattern` 정합).

근거: META self-application 부재 시 본 ADR 의 normative authority degrade (Story introduces template/codification change → apply to carrier Story itself as 1st applied case → dogfood loop close).

**Normative carrier 갱신 (post-CFP-1329 / ADR-082 Amendment 8 §결정 10.D)**: META self-application pattern 은 ADR-082 §결정 10.D (CFP-1329 carrier, 2026-05-24 KST) 가 normative codify — pattern_count=2 reach (CFP-1016 1st applied + CFP-1340 §결정 15 2nd applied) + CFP-1329 Amendment 8 = 3rd applied case. **본 CFP-1346 ADR-108 §결정 6 = 4th applied case** (label-registry-v2.md §3 entry append + description text "74번째" claim 정합 = self-evidence). ADR-082 §결정 10.D = super-class normative anchor / 본 ADR-108 §결정 6 = sub-class instance carrier (description text count parity axis sub-domain).

## 결과

### 긍정

- pattern_count=2 ADR-045 §D-9 Mandatory escalation 의무 충족 (CFP-604 + CFP-1302 동형 drift super-class 차단)
- Researcher dual-frame Event Sourcing/CQRS framing 으로 false dichotomy ("frozen ↔ dynamic") 해소
- Phase 2 lint mechanical 차단 — append-time write-time invariant verify-before-trust pattern axis-instantiation
- META self-application 1st applied case 로 dogfood loop close (memory pattern 정합)
- Historical narrative audit trail 보존 (Event Sourcing immutable event log 정합)

### 부정 / Trade-off

- Phase 2 wire 까지 mechanical detection 부재 (declaration-only Wave 1 — ADR-082 §결정 6 retain pattern 답습 / ADR-070 / ADR-086 precedent)
- 본 ADR scope = label-registry-v2 단독 carrier — 다른 inter-plugin contract registry (review-verdict-v4 12 occ / evidence-checks 4 / MANIFEST 3 / debate-protocol 3 / comment-prefix 1) = pattern_count=0 영역 별도 follow-up CFP carrier (evidence-gated unitary per ADR-064 §결정 5 정합 — CFP scope unitary 보호)
- Author 가 raw grep count 재verify 의무 lock-in (cognitive overhead — Phase 2 lint 가 mitigate)

### 영향 받는 코드·레이어·운영 경계

- `docs/inter-plugin-contracts/label-registry-v2.md` — 신규 entry append 시 description text format 정합 의무
- `docs/inter-plugin-contracts/MANIFEST.yaml` — label-registry-v2 row version bump 동반 (additive MINOR)
- `docs/evidence-checks-registry.yaml` — `label-registry-frozen-baseline-count-parity` entry row append (Phase 1)
- `CLAUDE.md` — ADR-108 cross-ref 단락 + 20번째 warning entry 명시
- Phase 2 (sibling sub-Story carrier wire): `scripts/check-label-registry-frozen-baseline-count-parity.sh` + workflow + bats fixture
- 본 ADR scope 외 (별도 follow-up CFP carrier): cross-contract applicability (review-verdict-v4 등 8 other contract) + ADR-082 sibling axis carry-over (verify-before-cite specific axis instantiation 후보)

## 해소 기준

N/A — permanent policy (`is_transitional: false`).

근거: ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 본 ADR 은 ratchet 강화 방향 (pattern_count=2 reach → Mandatory escalation). ADR-058 §결정 5 sunset_justification 면제 영역 (강화 방향 적용 evidence 보유, 약화 evidence requirement 영역 외).

## 관련 ADR

- **ADR-008** (inter-plugin contract versioning + §결정 2 v1.x backward-compatible 변경 룰) — additive entry append = MINOR bump 정합, 본 ADR-108 = append axis 의 description text count sub-axis 신설
- **ADR-010** (§결정 3 kind:registry scope limitation — kind:contract MANIFEST scope 외) — label-registry-v2 = kind:registry → ADR-108 발효 후에도 sibling sync 면제 retain
- **ADR-058** (sunset criteria mandate / Amendment 1 §결정 5) — `is_transitional: false` ratchet 강화 방향 → sunset_justification 면제
- **ADR-060** (evidence-enforceable promotion framework 4-tier) — `label-registry-frozen-baseline-count-parity` warning-tier entry (19 → 20 entry)
- **ADR-064** (decision principle mandate §결정 5 CFP scope unitary + §결정 7 evidence-gated symmetric ratchet) — 본 ADR scope = label-registry-v2 단독 carrier (evidence-gated unitary)
- **ADR-073** (Orchestrator verify-before-assert) — 본 ADR 의 forcing function = verify-before-trust grep-count sub-scope axis-instantiation
- **ADR-082** (write-time self-write verification mandate §결정 1 layer 1 sub-scope 1-C) — axis disjoint sibling (author claim verify ↔ description text count parity)
- **ADR-082 Amendment 7** (CFP-1312 — §결정 9 verify-before-cite 양방향 확장) — sibling axis (forward-parity ↔ backward-staleness 대칭 pair) — 별도 follow-up CFP carry-over carrier 평가 영역
- **ADR-045** (§D-9 cross_story_pattern_adr_trigger pattern_count ≥ 2 reach escalation_action: adr_draft_emitted) — 본 ADR carrier origin
- **ADR-107** (Plugin declarative seed drift detection — 2026-05-24 KST active) — adjacent concept, **axis disjoint** (ADR-107 = plugin file declarative seed drift vs ADR-108 = description text count drift). sibling carrier pattern 답습 (collision rebase ratchet precedent row 107 → 108 next sequential)

## 관련 CFP

- **CFP-1346** (본 carrier — standalone Story, parent_epic null)
- **CFP-604** (retro F6 Wave 2 carrier — sentinel #1)
- **CFP-1302** (retro §5.1 — sentinel #2, pattern_count=2 reach Mandatory escalation 산물)
- **CFP-1312** (ADR-082 Amendment 7 sibling axis carrier — forward-parity ↔ backward-staleness 대칭 pair 평가 영역)
- **CFP-1317-S3** (ADR-107 carrier — collision rebase ratchet precedent row 107)

## 관련 파일

- `docs/inter-plugin-contracts/label-registry-v2.md` — 본 ADR-108 의무 적용 대상 (§3 yaml block 안 hotfix-bypass:* entry description text)
- `docs/inter-plugin-contracts/MANIFEST.yaml` — label-registry-v2 row version bump (additive MINOR)
- `docs/evidence-checks-registry.yaml` — `label-registry-frozen-baseline-count-parity` row append (Phase 1)
- `scripts/check-label-registry-frozen-baseline-count-parity.sh` — Phase 2 wire target lint script
- `templates/github-workflows/label-registry-frozen-baseline-count-parity.yml` + `.github/workflows/<same>.yml` self-app — Phase 2 wire target workflow
- `tests/scripts/cfp-1346/check-label-registry-frozen-baseline-count-parity.bats` — Phase 2 wire target bats fixture
- `CLAUDE.md` — ADR-108 cross-ref 단락 + 20번째 warning entry
- `C:/workspace/mclayer/codeforge-internal-docs/plugin-codeforge/stories/CFP-1346.md` — 본 carrier Story file (dogfood-out, internal-docs repo)
- `C:/workspace/mclayer/codeforge-internal-docs/plugin-codeforge/change-plans/cfp-1346-frozen-baseline-description-count-parity.md` — Phase 1 Change Plan
