---
adr_number: 107
title: Plugin declarative seed wrapper-SSOT-byte-parity 의무 + Design lane 진입 전 plugin 1.0.0 feasibility check (drift detection process)
status: Active
category: governance
date: 2026-05-24
carrier_story: CFP-1317-S3
parent_epic: CFP-1317
supersedes: null
amends: null
amendments:
  - amendment_id: 1
    date: 2026-05-25
    carrier_story: CFP-1367
    summary: "Wave 2 mechanical wire — mechanical_enforcement_actions[] 0→2 (plugin-declarative-seed-byte-parity-check + design-lane-plugin-feasibility-check). declaration-only Wave 1 → enforcement layer ratchet 강화 (ADR-058 §결정 5 정합, sunset_justification 면제). F1+F2 통합 carrier — same parent_epic CFP-1317, same retro internal-docs#811 fe8524a §6 follow-up F1+F2 HIGH 통합 권고 정합. ADR-082 Amd 1 (CFP-841) + ADR-070→CFP-963 + ADR-086 declaration-only Wave 1 → Wave 2 mechanical wire precedent 답습."
amendment_log:
  - amendment_id: 1
    date: 2026-05-25T17:00:00+09:00
    summary: "mechanical_enforcement_actions[] 0→2 wire (plugin-declarative-seed-byte-parity-check + design-lane-plugin-feasibility-check)"
    sunset_justification: "N/A — ratchet 강화 방향 (declaration-only Wave 1 → mechanical wire Wave 2 enforcement layer, invariant 강화 + scope 0건 축소, ADR-058 §결정 5 정합 약화 evidence-gate 면제)"
    carrier_story: CFP-1367
    parent_epic: CFP-1317
    pattern_count_evidence: "§결정 1 byte-parity = 6 (G-1/G-3/G-6 super-class) / §결정 2 feasibility = 3 (ADR-082 verification gap Wave A S1 incidents) — 양 axis threshold N=2 의 1.5~3배 초과"
    precedent_chain:
      - "ADR-070 → CFP-963 codex-network-scope-presence (declaration-only Wave 1 → Wave 2 mechanical wire)"
      - "ADR-082 → Amendment 1 (CFP-841) corpus-claim-verify + cross-plugin-ownership-verify (통합 2-entry Wave 2 wire 패턴)"
      - "ADR-086 deferred-followup carrier (declaration-only Wave 1 정합)"
related_adrs:
  - ADR-087   # 본 ADR 의 super-class carrier (Wave A S1 Amendment 1 + Wave A S2 plugin file d-B redirect — drift detection 적용 대상 영역)
  - ADR-088   # deploy review lane (drift detection sibling layer)
  - ADR-082   # write-time self-write verification mandate (verify-before-trust internal lane agent layer — 본 ADR §결정 2 feasibility check 의 plugin-side analog precedent)
  - ADR-073   # Orchestrator verify-before-assert (lane_spawn trigger 4-source polling — 본 ADR §결정 2 의 wrapper-side precedent)
  - ADR-070   # Codex verify-before-trust (external worker output verify — declaration-only Wave 1 precedent)
  - ADR-086   # deputy creation decision framework (declaration-only Wave 1 precedent)
  - ADR-045   # §D-9 cross_story_pattern_adr_trigger carrier (escalation_action: adr_draft_emitted 의무 충족 carrier — pattern_count=6)
  - ADR-068   # boundary completeness invariants (I-1 schema mapping 완전성 + I-4 wording SSOT chief tie-break ladder Amendment 2)
  - ADR-058   # sunset criteria mandate (ratchet 강화 방향, sunset_justification 면제)
  - ADR-076   # declarative reconciliation upgrade flow (wrapper SSOT ↔ consumer overlay reconcile 패턴 — 본 ADR 의 plugin-side analog 도메인 inspiration)
  - ADR-064   # decision principle mandate (Amendment 5 self-application top-down ratchet 정합)
  - ADR-054   # doc-only fast-path Category 2 (본 carrier Story 적격성)
related_stories:
  - CFP-1317-S3  # 본 carrier (Wave B 마지막 Story)
  - CFP-1317-S1  # Wave A — ADR-087 Amendment 1 carrier (BG-1~4 비적격 표 + §결정 9 신설 — 본 ADR 의 super-class 영역 wrapper SSOT codify)
  - CFP-1317-S2  # Wave A — plugin file d-B redirect carrier (single-SSOT precedent — 본 ADR §결정 1 path B 채택 evidence)
is_transitional: false
mechanical_enforcement_actions:
  - plugin-declarative-seed-byte-parity-check  # F1 axis — Amendment 1 (CFP-1367) wire, evidence-checks-registry warning tier deferred-followup → Phase 2 mechanical wire Active
  - design-lane-plugin-feasibility-check       # F2 axis — Amendment 1 (CFP-1367) wire, evidence-checks-registry warning tier deferred-followup → Phase 2 mechanical wire Active
sunset_justification: null
---

# ADR-107: Plugin declarative seed wrapper-SSOT-byte-parity 의무 + Design lane 진입 전 plugin 1.0.0 feasibility check (drift detection process)

## 상태

Active (2026-05-24 KST) — 6회 누적 G-1/G-3/G-6 동형 plugin 1.0.0 declarative seed drift super-class 차단 mechanism layer 신설. ADR-045 §D-9 `cross_story_pattern_adr_trigger` (pattern_count=6, threshold N=2 의 3배 초과, escalation_action=adr_draft_emitted) 의무 충족 carrier.

## 컨텍스트

mctrader CFP-1059 배포 lane 첫 consumer adoption (`mctrader#1265` 진행 중) 에서 4 결함 escalate (mctrader#1272, Wave A S1+S2 Story files §1 verbatim carrier):

- (a)+(b) ADR-087 §결정 5/9 영역 — Wave A S1 (CFP-1317-S1) ADR-087 Amendment 1 carrier (`72680a8b7701a1079e8e0caa78b03f48ad72332` merged)
  - (a) BG-1~4 비적격 4-tuple 표 미명시 (`STATEFUL_DAEMON_BG_NEEDED` / `WRITER_LEASE_REQUIRED` / `EXTERNAL_PORT_BINDING` / `MULTI_PROCESS_FENCING_REQUIRED`)
  - (b) §결정 9 6 sub-section (writer-lease / fencing pattern) 신설 영역
- (c)+(d) codeforge-deploy plugin file 영역 — Wave A S2 (CFP-1317-S2) plugin d-B 채택 (`8842ec1b2617f2cc7e7106589d8888f048c75fd5` merged)
  - (c) `mclayer/plugin-codeforge-deploy/templates/deploy-mechanism.md` (현 `plugins/codeforge-deploy/templates/`, 구 repo 삭제됨 2026-06-12) plugin 1.0.0 baseline 영역
  - (d) **= 6회째 누적 G-1/G-3/G-6 동형 drift super-class** — plugin 1.0.0 declarative seed (templates/deploy-mechanism.md 9-flat field) ↔ wrapper SSOT (`docs/project-config-schema.md` 5-nested) 구조 mismatch

### pattern_count history (ADR-045 §D-9 Mandatory framing line 417 정합)

| Sub-class | Source | Severity |
|---|---|---|
| G-1 | mctrader debut 영역 — initial declarative seed drift occurrence | super-class 1 |
| G-3 | history sub-class 2 — declarative seed drift recurrence | super-class 2 |
| G-6 | mctrader#1272 (d) — 본 incident (Wave A S2 d-B redirect resolved, 본 ADR-107 carrier source) | super-class 3 (6번째 occurrence cumulative) |

→ **threshold N=2 의 3배 초과 (pattern_count=6)**. ADR-045 §D-9 `escalation_action` enum 2-value (`escalate_user` / `adr_draft_emitted`) 중 default `adr_draft_emitted` 채택 — 본 ADR-107 carrier.

### Wave A inheritance (drift detection 적용 source evidence)

- **S1 wrapper SSOT codify**: ADR-087 Amendment 1 (`amendment_log[] 0→1`, sunset_justification=null ratchet 강화 방향 정합 ADR-058 §결정 5) + §결정 5.2 BG-1~4 4-tuple 비적격 표 + §결정 9 신설 6 sub-section + 도메인 entry 2 신설 (`stateful-daemon-bg-eligibility.md` + `single-writer-fencing-pattern.md`)
- **S2 plugin file d-B 채택**: single-SSOT redirect (9-flat schema block 완전 제거, body redirect to wrapper SSOT `docs/project-config-schema.md`) — chief tie-break ladder result (ADR-068 I-4 Amendment 2): 3중 concur (Researcher 5/5 prior art + PL d-B + I-4 invariant d-B)

본 ADR-107 = Wave A 2 source 의 generalized mechanism — 1 incident 의 specific resolution 을 정책 level layer 로 codify.

## 결정

### 결정 1: Plugin declarative seed wrapper-SSOT-byte-parity 의무

wrapper SSOT (`docs/project-config-schema.md` 등 wrapper-canonical schema document) ↔ plugin templates/* declarative seed file (예: `mclayer/plugin-codeforge-deploy/templates/deploy-mechanism.md`) 의 schema 구조 **byte-parity 의무**.

**byte-parity 영역 enum**:
- frontmatter field 구조 (key name / nesting structure / required vs optional)
- section heading 구조 (heading level / order / required sections)
- field enumeration (예: deploy mechanism nested key `deploy.mechanism` / `deploy.swap_window_seconds` 등)
- semantic 의미 (key 이름이 같으면 의미도 동일 — 동일 어휘 disjoint 의미 차단)

**drift 발견 시 처리 path 2-enum**:

| Path | 적용 영역 | 처리 |
|---|---|---|
| **Path A — mirror update** | wrapper SSOT 변경 직후 plugin seed 미반영 영역 (drift source = wrapper-side) | plugin seed 를 wrapper SSOT 정합으로 갱신 (mirror 패턴 — Helm chart README.md auto-generated from values.yaml 동형) |
| **Path B — single-SSOT deprecate** | plugin seed 가 outdated 또는 wrapper SSOT 와 구조 mismatch 영역 (drift source = mirror 실증 실패 신호, 6회 누적) | plugin seed 를 deprecate (frontmatter `is_deprecated: true` + `single_source: wrapper`) + body redirect (Wave A S2 d-B precedent — 9-flat schema block 완전 제거 + redirect link to wrapper SSOT) |

**Path B 권고** (Wave A S2 chief tie-break ladder Step 2 ADR-068 I-4 HIT — 3중 concur: Researcher 5/5 prior art Helm / K8s CRD / Terraform provider / Cargo + PL d-B + I-4 invariant d-B). mirror-SSOT 는 drift 실증 실패 evidence (6회 누적) — single-SSOT 가 default 권장.

**wrapper SSOT canonical anchor 명시 의무**: ADR-107 §결정 1 path 채택 시 wrapper SSOT file path 명시 (예: `docs/project-config-schema.md`) — plugin file frontmatter 안 `single_source: <wrapper SSOT abs path>` field codify 의무.

### 결정 2: Design lane 진입 전 plugin 1.0.0 feasibility check 의무

ArchitectAgent §3 작성 시 cross-repo plugin 영역 fact claim (file existence / mechanism 가정 / API 표면 / schema 구조) **의무 verify-before-trust direct query**.

**검증 영역 enum (closed-set)**:

| 영역 | 검증 mechanism | source ADR |
|---|---|---|
| file existence | `gh api repos/<plugin>/contents/<path>` direct Read | ADR-073 Amendment 2 lane_spawn trigger 4-source polling |
| directory structure | `gh api repos/<plugin>/contents/<dir>` → tree traversal | ADR-073 Amendment 2 |
| mechanism wire status | declare-only (mechanical_enforcement_actions[] = []) vs actual workflow yml seed (`templates/github-workflows/*.yml`) — direct Read 의무 | ADR-082 §결정 1 layer 2 |
| schema structure | frontmatter / section heading / field enumeration direct Read + byte-parity 비교 (본 ADR §결정 1 정합) | ADR-068 I-1 schema mapping 완전성 |
| cross-repo state freshness | sibling plugin commit SHA / branch state direct query (`gh api repos/<plugin>/commits/<branch> --jq .sha`) | ADR-073 Amendment 2 + MEMORY pin HEAD SHA first |

**verify 결과 ↔ ArchitectAgent §3 claim mismatch 시 의무**:
- Story §10 FIX Ledger row append (fix-event-v1 v1.3 `fix_event_type: design_finding`)
- 정정 재spawn 또는 inline edit (Wave A S1 ArchitectAgent self-report mismatch incident precedent — pattern_count=3 ADR-082 escalation candidate)
- `[verified-via: <verify mechanism>]` annotation 의무 부착 (ADR-082 §결정 2 scope (b) 정합)

**plugin-side analog 영역**: 본 §결정 2 = ADR-073 Amendment 2 (Orchestrator wrapper-side lane_spawn 4-source polling) 의 plugin-side analog. wrapper-side 는 worktree FF / origin/main SHA pin / Issue state poll 의무 — plugin-side 는 plugin 1.0.0 direct query (file / dir / mechanism / schema / state) 의무.

### 결정 3: declaration-only Wave 1 (mechanical_enforcement_actions[] = [])

본 ADR-107 = **Wave 1 declaration-only** — `mechanical_enforcement_actions: []` (empty). mechanical enforcement layer (lint workflow / pre-commit hook / Phase 2 CI) = **별 Wave 2 carrier (deferred-followup)**.

**Precedent answer**:

| ADR | declaration-only Wave 1 패턴 | Wave 2 carrier |
|---|---|---|
| ADR-070 (Codex verify-before-trust) | `mechanical_enforcement_actions: []` retain (§D5) | CFP-963 (codex-network-scope-presence) 12번째 warning-tier entry |
| ADR-082 (write-time self-write verification mandate) | `mechanical_enforcement_actions: []` Wave 1 known-limitation | Amendment 1 (CFP-841) — behavioral→mechanical 전환 2-entry (corpus-claim-verify / cross-plugin-ownership-verify) |
| ADR-086 (deputy creation decision framework) | `mechanical_enforcement_actions: []` declaration-only Wave 1 | 별 CFP carrier (deferred-followup) |
| **ADR-107 (본 ADR)** | `mechanical_enforcement_actions: []` declaration-only Wave 1 | **pattern_count >= 2 재발 시 follow-up CFP MUST promote** (ADR-082 §결정 6 rationale 답습) |

**rationale**: pattern_count=6 evidence 가 governance ratchet 강화 anchor codify 의 1차 mandate — mechanical enforcement layer 는 Wave 2 별 carrier 가 spec/plan + bats fixture + workflow yml + evidence-checks-registry row 동시 atomic codify (declaration-only Wave 1 가 wire 의 정합 source).

### 결정 4: ADR-058 §결정 5 정합 — ratchet 강화 방향, sunset_justification 면제

본 ADR-107 신설 = **governance ratchet 강화 방향** (drift detection process 신규 mandate — invariant 신설, 약화 방향 0건).

ADR-058 §결정 5 sunset_justification rule = **약화 방향 evidence-gate**. ratchet 강화 = **의무 면제**.

**`is_transitional: false`** — permanent governance ratchet (ADR-058 §결정 5 정합). `sunset_justification: null` (frontmatter 명시).

**ADR-064 §self-application top-down ratchet 정합**: ADR-064 Amendment 5 normative 승격 — ratchet 강화 방향 monotonic-increasing governance. 본 ADR-107 = 6회 누적 drift super-class 차단 layer 신설 = monotonic-increasing 의 부분.

### 결정 5: cross-Story pattern adr trigger 6-field block (ADR-045 §D-9 Amendment 6 의무 충족)

본 ADR-107 신설 = `cross_story_pattern_adr_trigger` Story §10 (CFP-1317-S3) 박제 의무 충족 — Story file §10 또는 `__metadata` 영역에 다음 yaml block codify 의무:

```yaml
cross_story_pattern_adr_trigger:
  pattern_name: "plugin-declarative-seed-drift"
  super_class: "G-1 / G-3 / G-6 동형"
  pattern_count: 6
  threshold: 2
  escalation_action: "adr_draft_emitted"
  adr_emitted: "ADR-107"
  carrier_story: "CFP-1317-S3"
  evidence_source: "mctrader#1272 (d) + Wave A S1+S2 Story files §2 + Epic #1317 body verbatim"
  detection_kst: "2026-05-24T00:14:00+09:00"
```

**6-field 의무 (ADR-045 §D-9 Amendment 6 정합)**: pattern_name / super_class / pattern_count / threshold / escalation_action / adr_emitted (carrier_story / evidence_source / detection_kst = optional sub-field).

## 결과

- plugin declarative seed wrapper-SSOT-byte-parity 의무 (§결정 1) + Design lane 진입 전 plugin 1.0.0 feasibility check 의무 (§결정 2) mechanism layer 차단 anchor codify
- Wave 1 declaration-only (mechanical layer = 별 Wave 2 carrier)
- 7 industry prior art (Helm chart values.schema.json / K8s CRD OpenAPI v3 schema / Terraform provider schema lock / Cargo Cargo.lock workspace pin / K8s controller reconcile loop / Terraform plan dry-run / Ansible check mode) precedent 답습 정합 — Researcher 5/5 + 3/3 (S2 §6 inheritance + 본 ADR §결정 1+2 권고 합의)
- 6회 누적 super-class drift 차단 — ADR-045 §D-9 cross_story_pattern_adr_trigger forcing function 의무 충족 carrier (escalation_action: adr_draft_emitted, threshold N=2 의 3배 초과)
- Epic #1317 close trigger 활성 — S3 Phase 1 PR merge 후 post-merge-followup.yml + retro-mandatory.yml 자동 발동, Epic-level PMOAgent retro file 신설

## 해소 기준


N/A — permanent policy
N/A — permanent governance ratchet (`is_transitional: false`). ADR-058 §결정 5 ratchet 강화 방향 sunset_justification 면제 영역.

## 관련 파일

- `docs/project-config-schema.md` — wrapper canonical schema SSOT (본 ADR §결정 1 byte-parity source anchor — `deploy.*` schema 5-nested form)
- `mclayer/plugin-codeforge-deploy/templates/deploy-mechanism.md` — Wave A S2 d-B precedent (single-SSOT deprecate path B 채택 evidence, 9-flat schema block 완전 제거 → redirect)
- `docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md` — Wave A S1 Amendment 1 carrier (BG-1~4 비적격 표 + §결정 9 6 sub-section)
- `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` — declaration-only Wave 1 precedent (mechanical_enforcement_actions: [] Wave 1 + pattern_count >= 2 재발 시 follow-up CFP MUST promote rationale)
- `docs/adr/ADR-073-orchestrator-verify-before-assert.md` — Amendment 2 lane_spawn trigger 4-source polling — 본 ADR §결정 2 feasibility check 의 wrapper-side precedent
- `docs/adr/ADR-045-story-retro-mandatory-trigger.md` — §D-9 cross_story_pattern_adr_trigger Amendment 6 schema source — 본 ADR-107 신설 의무 충족 carrier (pattern_count=6)
- `docs/adr/ADR-068-boundary-completeness-invariants.md` — I-1 schema mapping 완전성 + I-4 wording SSOT chief tie-break ladder Amendment 2 — 본 ADR §결정 1 byte-parity 영역 정합
- `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` — §결정 5 ratchet 강화 방향 sunset_justification 면제 정합
- `CLAUDE.md` — cross-ref token append 영역 (line cap 319/320 margin 1 보존, 본문 변경 0 invariant)
- `wrapper/stories/CFP-1317-S3.md` — carrier Story file (internal-docs repo, RequirementsPLAgent + ArchitectAgent self-write)
- `wrapper/stories/CFP-1367.md` — Amendment 1 carrier Story file (mechanical_enforcement_actions[] 0→2 wire, Wave 2)
- `scripts/check-plugin-declarative-seed-byte-parity.sh` + `scripts/lib/check_plugin_declarative_seed_byte_parity.py` — F1 axis Phase 2 lint script (Amendment 1 wire 영역)
- `scripts/check-design-lane-plugin-feasibility.sh` + `scripts/lib/check_design_lane_plugin_feasibility.py` — F2 axis Phase 2 lint script (Amendment 1 wire 영역)
- `templates/github-workflows/plugin-declarative-seed-byte-parity-check.yml` + `templates/github-workflows/design-lane-plugin-feasibility-check.yml` — F1+F2 warning-tier workflow (Amendment 1 wire 영역)
- `docs/evidence-checks-registry.yaml` — 2 entry append (`plugin-declarative-seed-byte-parity-check` + `design-lane-plugin-feasibility-check`, warning tier deferred-followup → Active)
- `docs/inter-plugin-contracts/label-registry-v2.md` — 2 new family member (`hotfix-bypass:plugin-declarative-seed-byte-parity` 90번째 + `hotfix-bypass:design-lane-plugin-feasibility` 91번째, v2.65 → v2.66 MINOR bump)

## Amendment 1 — Wave 2 mechanical wire (CFP-1367, 2026-05-25 KST)

### Trigger

CFP-1317 Epic close 후 retro internal-docs#811 fe8524a §6 follow-up F1+F2 HIGH 통합 권고 정합. 본 ADR §결정 3 (declaration-only Wave 1) 본문 verbatim "pattern_count >= 2 재발 시 follow-up CFP MUST promote" rationale (ADR-082 §결정 6 답습) 충족 — 양 axis 모두 threshold 초과:

| Axis | pattern_count | threshold | 초과 배수 |
|---|---|---|---|
| §결정 1 byte-parity | 6 (G-1/G-3/G-6 super-class, mctrader#1272 (d) carrier closure) | 2 | 3.0x |
| §결정 2 feasibility | 3 (ADR-082 verification gap Wave A S1 ArchitectAgent 누적 3 sub-class) | 2 | 1.5x |

### 변경

`mechanical_enforcement_actions: []` → `['plugin-declarative-seed-byte-parity-check', 'design-lane-plugin-feasibility-check']` (frontmatter field 갱신 + `amendments[]` array row append + `amendment_log[]` row append).

본 ADR 본문 §결정 1+2+3+4+5 = **0건 변경** (사용자 directive verbatim: "Bundle B = ADR-107 본 ADR 본문 0 변경 — Amendment 시에만 변경"). Amendment 헤더 + 관련 파일 row append 만.

### Phase 1 + Phase 2 분리 (ADR-054 Category 2 부적격)

본 carrier Story CFP-1367 = NOT doc-only fast-path (lint script src + workflow yml + bats fixture 변경 영역 포함). Phase 1 + Phase 2 분리 의무:

- **Phase 1 PR (declarative seed)**: 본 ADR-107 Amendment 1 + `docs/evidence-checks-registry.yaml` 2 entry append + `docs/inter-plugin-contracts/label-registry-v2.md` 2 entry + MINOR bump + Story §1-§6 baseline
- **Phase 2 PR (mechanical wire)**: 2 lint script + 2 workflow yml + 2 bats fixture + Story §7-§14 update + bats RED→GREEN stash proof (ADR-082 §결정 11.A 정합)

### ratchet 방향 + sunset_justification 면제 (ADR-058 §결정 5 정합)

본 Amendment = **governance ratchet 강화 방향** (declaration-only → mechanical enforcement layer wire, invariant 강화 + scope 0건 축소). ADR-058 §결정 5 rule = **약화 방향 evidence-gate**, 강화 = 면제. `is_transitional: false` retain (permanent governance ratchet).

`sunset_justification: "N/A — ratchet 강화 방향"` (amendment_log row 안 명시, 강화 evidence-gate 면제).

### precedent answer (declaration-only Wave 1 → Wave 2 mechanical wire 패턴 답습)

| ADR | Wave 1 anchor | Wave 2 mechanical wire | wire 영역 |
|---|---|---|---|
| ADR-070 | declaration-only `mechanical_enforcement_actions: []` retain (§D5) | CFP-963 codex-network-scope-presence | 12번째 warning-tier entry (evidence-checks-registry) |
| ADR-082 | Wave 1 known-limitation `mechanical_enforcement_actions: []` | Amendment 1 (CFP-841) corpus-claim-verify + cross-plugin-ownership-verify | 2-entry 통합 wire (본 ADR-107 Amendment 1 패턴 inspiration) |
| ADR-086 | declaration-only Wave 1 | 별 CFP carrier (deferred-followup) | sibling deferred 패턴 정합 |
| **ADR-107 (본 Amendment 1)** | declaration-only Wave 1 `mechanical_enforcement_actions: []` | **CFP-1367 — plugin-declarative-seed-byte-parity-check + design-lane-plugin-feasibility-check** | **2-entry 통합 wire (ADR-082 Amendment 1 정합)** |

### Wave 3+ scope (별 follow-up CFP carrier)

본 Amendment 1 scope 외 (Story §5.4 Out-of-Scope 정합):
- F1 / F2 blocking-on-pr 승격 = 별 follow-up CFP (Wave 4 evidence accumulation 후 ADR-060 §결정 6 AND condition 충족)
- F1 scope 확장 (다른 plugin templates/* file mapping) = 별 follow-up CFP (Wave 3 byte-parity scope 확장)
- F2 heuristic 정교화 (regex 확장 + 추가 evidence channel) = 별 follow-up CFP (Wave 3 heuristic tuning)
- threshold tuning = evidence-based Wave 3 별 carrier
