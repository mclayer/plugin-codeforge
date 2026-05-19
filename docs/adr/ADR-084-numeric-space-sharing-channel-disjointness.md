---
adr_number: 84
title: numeric-space-sharing channel disjointness invariant codification — inter-plugin contract level layer disjointness governance
status: Accepted
category: workflow-policy
date: 2026-05-19
carrier_story: CFP-989
parent_epic: null
supersedes: null
amends: null
amendments: []
amendment_log: []
related_stories:
  - CFP-989  # carrier (E-3 emission from EPIC-RESULTS-CFP-858.md §6.3 P-3 systemic cluster)
  - CFP-986  # first applied case (b6d7eb5 reconcile-protocol-v1 §4.12 + §4.13 classification↔severity disjoint clause)
related_adrs:
  - ADR-076  # reconcile-protocol-v1 declarative reconciliation (first applied case host — §4.12/§4.13)
  - ADR-082  # disjoint 4-layer 표 governance pattern source (layer disjointness 일반화 source)
  - ADR-068  # boundary completeness invariants I-1~I-5 (scope disjoint — ArchitectAgent self-check axis vs inter-plugin contract codify axis)
  - ADR-070  # Amendment 4 declaration-only retain precedent chain 4번째 instance (CFP-988)
  - ADR-081  # §결정 D6.e declaration-only retain precedent chain
  - ADR-064  # §self-application top-down ratchet (강화 방향만 허용) + §결정 1 CFP scope unitary
  - ADR-058  # §결정 5 sunset_justification ratchet (is_transitional 약화 차단)
  - ADR-054  # doc-only fast-path 단일 PR 적격
  - ADR-040  # Amendment 3 §결정 7.D normative ADR mechanical_enforcement_actions[] mandate (workflow-policy category 면제 정합)
  - ADR-045  # §D-9 cross-Story pattern forcing function origin (E-3 emission anchor)
  - ADR-008  # Inter-plugin Contract Versioning (affected contract MINOR bump 적격 분기 영역)
  - ADR-010  # Inter-plugin Contract Sibling Sync (kind:registry vs kind:contract 분기)
related_files:
  - docs/inter-plugin-contracts/reconcile-protocol-v1.md  # CFP-986 §4.12/§4.13 first applied case
  - docs/inter-plugin-contracts/severity-propagation-v1.md  # numeric severity propagation potential surface (audit 대상)
  - docs/inter-plugin-contracts/MANIFEST.yaml  # contract surface enumeration source
  - docs/domain-knowledge/domain/inter-plugin-contracts/numeric-space-disjointness.md  # 신규 narrative SSOT (본 ADR 동반 신설)
  - docs/adr/ADR-RESERVATION.md  # row 84 active (CFP-989)
  - CLAUDE.md  # cross-ref 1줄 추가 (영구 ADR section)
is_transitional: false
# Wave 1 = behavioral directive only (3-곳 명시 declare 의무 + DesignReview lane MUST flag).
# mechanical_enforcement_actions[] retain default = precedent chain 5번째 instance
# (ADR-070 §D5 → ADR-082 §결정 6 → ADR-081 §결정 D6.e → ADR-070 Amendment 4 D6.4 → 본 ADR-084).
# Sentinel clause: "if pattern_count ≥ 2 recurrence (CFP-986 b6d7eb5 외 추가 instance 1+ 발생),
# follow-up CFP MUST promote to mechanical lint" — ratchet-up direction promise 보존 +
# 실 추가 sample 발생 시 신속 promotion 영역 명시 (ADR-082 §결정 6 rationale 답습).
# workflow-policy category = ADR-040 Amendment 3 §결정 7.D normative 5 category enum 부재 면제 정합.
mechanical_enforcement_actions: []
sunset_justification: "N/A — permanent governance policy. ADR-064 §self-application top-down ratchet 정합 (ratchet 강화 방향 only — disjointness invariant codify scope 확장). ADR-058 §결정 5 약화 방향 발의 차단. is_transitional: false (영구 정책). sentinel clause 가 declaration-only retain 정당성 보존 + 실 pattern_count ≥ 2 reach 시 mechanical lint promotion 의무 명시."
pre_lookup_evidence:
  verified_files:
    - { path: "docs/adr/ADR-RESERVATION.md", verified-via: "git show 836fa0a:docs/adr/ADR-RESERVATION.md", note: "row 84 active (CFP-989), status reserved 미경유 직접 active (ADR-079/080/081/082/083 precedent 정합). ADR file slug = ADR-084-numeric-space-sharing-channel-disjointness.md 확정" }
    - { path: "docs/inter-plugin-contracts/reconcile-protocol-v1.md", verified-via: "git show b6d7eb5:docs/inter-plugin-contracts/reconcile-protocol-v1.md", note: "§4.12 classification_severity_disjoint_invariant + §4.13 classification_not_severity_clause first applied case verified (line 878/942 grep-presence)" }
    - { path: "docs/domain-knowledge/domain/inter-plugin-contracts/", verified-via: "ls direct", note: "directory 부재 → 본 ADR 동반 신설 (Q1-A default 시 narrative SSOT entry)" }
    - { path: "docs/doc-locations.yaml", verified-via: "Read line 135-149", note: "domain_knowledge entry pattern `<owner-repo>/docs/domain-knowledge/<area>/<topic>.md` — 신규 area `inter-plugin-contracts` 신설 적격 (CFP-946-A `codex-collaboration/` sub-tree 신설 precedent 동형)" }
    - { path: "docs/adr/ADR-082-write-time-self-write-verification-mandate.md", verified-via: "Read line 1-120", note: "§결정 1 disjoint 4-layer 표 governance pattern source + §결정 6 declaration-only retain rationale precedent + ADR-082 Amendment 1 (CFP-841) behavioral→mechanical 전환 5번째 instance precedent chain anchor" }
  origin_main_sha: "836fa0a"  # wrapper repo branch cfp-989-adr-084 tip
  last_git_fetch_timestamp: "2026-05-19T01:13:39+09:00"  # KST per ADR-079 §결정 2
---

# ADR-084: numeric-space-sharing channel disjointness invariant codification — inter-plugin contract level layer disjointness governance

## 상태

Accepted (2026-05-19 KST) — CFP-989 carrier. PMOAgent ADR-045 §D-9 cross_story_pattern_adr_trigger emission 산물 (EPIC-RESULTS-CFP-858.md §6.3 P-3 systemic cluster — single sample CFP-986, ADR-064 §결정 1 CFP scope unitary 정합 분리). doc-only fast-path (ADR-054 단일 PR).

## 본질 선언

inter-plugin contract 에서 두 (이상) channel 이 동일 numeric domain (integer / enum / ordinal) 을 encoding 으로 share 할 때, **encoding overlap 은 사실** 이고 **semantic overlap 은 금지** 다. 두 layer 의 disjointness 가 implicit 으로 남겨지면 defensible-misread → post-merge defect 패턴을 초대한다 (CFP-986 evidence). 본 ADR 이 충족되지 않으면 아래 §결정 mechanism 을 몇 개 쌓든 의미 없다 — 모든 §결정 은 본질을 보조하는 scaffolding.

기존 codeforge governance 의 layer disjointness layer 는 (1) **ADR-082 §결정 1 disjoint 4-layer 표** (super-class N-layer governance — Orchestrator verify-before-assert / Codex verify-before-trust / lane agent write-time verify / PMOAgent retro corpus pattern_count escalation, ArchitectAgent §3/§7 self-check axis) + (2) **ADR-068 4 → 5 semantic invariants** (I-1 API contract / I-2 cross-module propagation / I-3 guard placement / I-4 wording SSOT / I-5 dimensional empirical, ArchitectAgent self-check axis) 만 정의한다. **(3) inter-plugin contract level numeric-space encoding overlap vs semantic disjoint invariant codify layer = 명백한 도메인 공백** (verified-via: `git grep -rn "numeric-space" docs/adr/` + `git grep -rn "channel disjoint" docs/inter-plugin-contracts/` — CFP-986 b6d7eb5 single occurrence, 일반화 codify 부재). ADR-084 가 이 (3) layer 신설 anchor.

## 컨텍스트

### pattern corpus (1 sample — Issue #989 body verbatim + EPIC-RESULTS-CFP-858.md §6.3)

| # | Story | 발현 | 설명 |
|---|---|---|---|
| 1 | CFP-986 | reconcile-overlay.sh:490-491 over-propagation defect | detect-repo-kind classification exit (0=plugin / 1=consumer / 2=mixed / 3=unknown, 0-3 range) 과 severity 채널 `_S2_MAX_EXIT` (0=proceed / 1=abort / 2=degraded, 0-2 range) 가 numeric-space sharing — boundary 변환 함수 부재 시 unconditional `_ec → _S2_MAX_EXIT` 전파로 정상 consumer reconcile (classification=1) 이 false `result: FAILED` 기록. spec clarification `b6d7eb5` (§4.12 classification_severity_disjoint_invariant + §4.13 classification_not_severity_clause) 로 1차 해소. **현재 pattern_count = 1** (single sample). |

PMOAgent ADR-045 Amendment 5 §D-9 정량 임계값: pattern_count 1 + Epic CFP-858 retro emission (P-1 / P-2 / P-3 systemic cluster) → Mandatory framing + escalation_action `escalate_user` → 사용자 단일 generalization ADR 결정 (2026-05-19 KST).

### 현 SSOT 결격 영역

- **ADR-082** = lane agent §9 evidence / Phase 0 mapping / corpus enumeration write-time semantic truth verify → **lane agent write-time** 한정 (inter-plugin contract codify scope 미포함, verified-via: `git show 836fa0a:docs/adr/ADR-082-...md` §결정 1 layer disjoint 표).
- **ADR-068** = ArchitectAgent §3/§7 self-check 5 semantic invariants → **ArchitectAgent self-check axis** 한정 (inter-plugin contract codify boundary axis 다름 — Q1 분기 결정 영역, ADR-068 통일 self-check axis 분열 방지 의무).
- **본 super-class gap** = inter-plugin contract 안 두 channel 이 numeric domain encoding 을 share 할 때 disjointness invariant 가 implicit 으로 남는 영역 — ADR-082/068 scope 외.

## 결정

### D1. numeric-space-sharing channel 정의 (대상 범위 명시)

**numeric-space-sharing channel** 이란 두 (이상) inter-plugin contract channel (또는 schema field / enum field) 이 동일 numeric domain (integer / ordinal / enum integer encoding) 을 encoding 으로 share 하는 영역. 본 ADR 의무 발효 조건:

- **조건 A (encoding overlap fact)**: 두 channel 이 동일 numeric range (예: 둘 다 0-2 정수 사용) 를 encoding 으로 채택. **사실 진술** — 위반 대상 아님.
- **조건 B (semantic overlap forbidden)**: 두 channel 의 semantic 이 서로 disjoint (값 동등 ≠ 의미 동등). 의미 동등 = identity propagation 자동 허용, 의미 disjoint = boundary 변환 함수 explicit 명시 의무.
- **조건 C (cross-channel propagation 발생)**: channel A 의 value 가 channel B 의 value 로 propagate 되는 path 가 contract 본문에 존재 (직접 변환 / 간접 reduce / forward / chained).

조건 A + B + C **AND** 충족 시 본 ADR D2 의무 발효. 단일 contract 내 numeric-space 분리 (예: 동일 yaml 안 두 enum field 인데 의미 자명 disjoint + cross-propagation path 부재) = 본 ADR 의무 미발효 (EC-1).

### D2. disjointness invariant codification 의무 — 3-곳 명시 declare

D1 조건 충족 시 다음 **3-곳 모두 명시적 declare 의무** (ADR-076 Invariant 2 3-layer declare precedent 답습):

1. **inter-plugin contract 본문** (`docs/inter-plugin-contracts/<name>-v<N>.md` 안):
   - `## Numeric Space Disjointness` section (또는 동등 명시 anchor — `<channel-A>_<channel-B>_disjoint_invariant` clause)
   - 두 channel 의 numeric range / semantic 정의 / boundary 변환 함수 explicit 명시 (identity 도 명시 의무 — EC-4)
   - over-propagation 자동 결함 사례 (CFP-986 b6d7eb5 답습 — 1 단락 negative example)

2. **ADR 본문** (carrier ADR 의 §결정 N 또는 본 ADR-084 D3 retroactive validation 영역):
   - `[DISJOINT]` 또는 `[SHARED-semantic]` marker explicit annotation
   - 두 channel 이 disjoint 인 경우 `[DISJOINT]` (default) — boundary 변환 함수 명시 의무
   - 두 channel 이 의미 동등인 경우 `[SHARED-semantic]` — identity propagation 허용 명시 (드문 case, EC-4 boundary)

3. **domain-knowledge entry** (`docs/domain-knowledge/domain/inter-plugin-contracts/<topic>.md`):
   - narrative SSOT (rationale + sample fixture + 위반 시 failure mode + audit checklist)
   - 본 ADR-084 동반 신설 narrative entry = `numeric-space-disjointness.md` (single source of truth for 3-곳 declare obligation 운용 방식)

**3-곳 declare 의무가 ADR-084 의 enforcement primitive**. `mechanical_enforcement_actions[]` retain 정합 (D6.5 precedent chain 5번째 instance + sentinel clause).

### D3. CFP-986 b6d7eb5 first applied case retroactive validation

CFP-986 `b6d7eb5` (Tue May 18 20:56:38 2026 +0900) = 본 ADR-084 의 generalization 원점 fixture. retroactive validation result:

- **§4.12 `exit_code_contract.classification_severity_disjoint_invariant`** — 1번째 declare (inter-plugin contract 본문, D2-1):
  - channel A: `detect-repo-kind exit (0=plugin / 1=consumer / 2=mixed / 3=unknown, 0-3 range)` — classification semantic
  - channel B: `_S2_MAX_EXIT (0=proceed / 1=abort / 2=degraded, 0-2 range)` — severity semantic
  - 둘 다 small non-negative integer encoding (0-3 / 0-2 overlap range = 0-2) + semantic disjoint
  - **classification ≠ severity** explicit clause
- **§4.13 `degradation_propagation.s2_filter_abort.classification_not_severity_clause`** — boundary 변환 함수 explicit clause (D2-1):
  - `severity = (1 if (classification ∈ {1, 2}) AND filter_abort) else (2 if degraded) else 0` — not identity propagation
  - source channel max → target channel passthrough 자동 결함 차단

[verified — `git show b6d7eb5:docs/inter-plugin-contracts/reconcile-protocol-v1.md` line 878/942 grep-presence direct verify in current session]

본 §D3 retroactive validation = **ADR 본문 declare 1-시점** (D2-2 의 [DISJOINT] marker annotation 동형). D2-3 domain-knowledge entry 신설 (`numeric-space-disjointness.md`) = 본 ADR-084 동반 신설 (3-곳 declare 의무 충족).

**Q2-A default — retroactive validation only**: reconcile-protocol-v1 자체 cross-ref 갱신 불필요 (`b6d7eb5` 이미 D2-1 충족). ADR-084 가 generalization codify 만 하면 첫 instance 의 D2 충족 표면 보존.

### D4. DesignReview lane MUST flag (behavioral directive)

DesignReview lane 의 DesignReviewPL / DesignReviewAgent 는 **inter-plugin contract 의 신설 / 갱신 (kind:contract / kind:registry 모두)** touch 시 다음 audit 수행 의무:

- **Audit-A**: contract 본문 안 두 (이상) numeric field / enum field 가 동일 numeric range 를 encoding 으로 share 하는지 확인 (grep-presence — `range:` / `enum:` / `values:` 필드 numeric value 동등 비교)
- **Audit-B**: cross-channel propagation path 존재 시 boundary 변환 함수 explicit clause 가 contract 본문 안에 있는지 확인 (D2-1 충족 여부)
- **Audit-C**: 미충족 시 P1 finding emit — `finding.type: "numeric-space-disjointness-implicit"` + `finding.evidence: <field-A>+<field-B>+<numeric-range>+<propagation-path>` + suggested FIX = D2-1/2/3 3-곳 declare 추가

**Q3-A default — declaration-only retain**: D4 audit 은 behavioral directive only (ADR-040 Amendment 3 §결정 7.D `workflow-policy` category 부재 면제 정합, `mechanical_enforcement_actions[]` empty retain). 실 lint 도입 = D6 sentinel clause activation trigger 도달 시 carrier.

**`codeforge:review-responsibility` skill / codeforge-review CLAUDE.md DesignReviewPL 체크항목 행 추가** = Phase 2 follow-up carrier 영역 (본 Story scope = ADR 본문 codify 만, ADR-054 doc-only fast-path 단일 PR 정합 보존).

### D5. is_transitional: false (permanent — 약화 차단 ratchet)

본 ADR = permanent governance policy. `is_transitional: false` 영구 invariant 선언 (ADR-058 §결정 5 sunset_justification: null retain 정합).

- **약화 방향 차단**: D2 3-곳 declare 의무 축소 / D4 DesignReview MUST flag 행 제거 / D1 조건 A+B+C AND → OR 약화 = ADR-058 §결정 5 ratchet 차단 logic 발효.
- **강화 방향만 허용**: D6 sentinel clause activation 시 mechanical lint promotion / 추가 contract surface enumeration retroactive validation / D2 4-곳 declare scope 확장 (예: PR template row 추가) = 강화 방향 정합 ratchet-up amendment 적격 (ADR-064 §self-application top-down ratchet 정합).

### D6. mechanical_enforcement_actions[] retain default — precedent chain 5번째 instance + sentinel clause

**D6.1 retain default**: `mechanical_enforcement_actions: []` (empty list retain). ADR-040 Amendment 3 §결정 7.D normative 5 category enum (`governance` / `security` / `tooling-infrastructure` / `dogfood-out` / `lifecycle`) 부재 면제 정합 — 본 ADR-084 category = `workflow-policy` (5 enum 외).

**D6.2 declaration-only retain precedent chain 5번째 instance**:

| # | ADR | 영역 | declaration retain rationale |
|---|---|---|---|
| 1 | ADR-070 §D5 | Codex verify-before-trust mandate | 외부 worker output verify 의무 — behavioral directive 가 forcing function 보존 |
| 2 | ADR-082 §결정 6 | Write-time self-write verification mandate | super-class anchor — Wave 1 = behavioral mandate, mechanical scope (a)/(d) 만 Wave 2 (Amendment 1) 전환 |
| 3 | ADR-081 §결정 D6.e | Codex worker prompt boilerplate composition | 4 ad-hoc dispatch sub-decision 통합 — declarative anchor only |
| 4 | ADR-070 Amendment 4 D6.4 (CFP-988) | mandatory-real-execution-evidence STANDING | E-1 (DeveloperPL false-self-claim 4-lineage) STANDING 4-tuple — behavioral mandate 보존 |
| **5** | **본 ADR-084** | **inter-plugin contract level numeric-space disjointness codify** | **pattern_count 1 (CFP-986 single sample) — declaration-only retain + sentinel clause** |

**D6.3 sentinel clause (declaration-only retain 정당화 보존 조건)**:

> **if pattern_count ≥ 2 recurrence (CFP-986 `b6d7eb5` 외 추가 instance 1+ 발생), follow-up CFP MUST promote to mechanical lint** — DesignReview lane numeric-space audit forcing function 신설 (`scripts/check-numeric-space-disjointness.sh` 또는 동등) + evidence-checks-registry warning-tier entry (`hotfix-bypass:numeric-space-disjointness` family member append) + label-registry-v2 MINOR bump.

**lint surface 후보 (sentinel reach 시 carrier)**: contract YAML/MD 안 동일 numeric range 가 2+ enum field 등장 시 `## Numeric Space Disjointness` section grep-presence warning. false positive 영역 = 단일 contract 내 자명 분리 case (EC-1) — DesignReview MUST flag (D4) 와 분리 운용 (lint = 자동 grep, DesignReview = 인지 의존).

**D6.4 ratchet-up direction promise (sentinel reach 시 mechanical lint promotion 의무)**: ADR-082 §결정 6 retain rationale 답습 — declaration-only retain 정당성 보존 + 실 pattern_count ≥ 2 reach 시 신속 promotion 영역 명시. sunset_justification: null retain 영구 (ADR-058 §결정 5 약화 차단).

### D7. 거절된 대안 (Q1-A / Q2-A / Q3-A default 검토)

**D7.1 (Q1-B) ADR-068 I-6 invariant 추가 — 거절**:
- ADR-068 = ArchitectAgent §3/§7 self-check axis (semantic invariants — API contract / cross-module propagation / guard placement / wording / dimensional empirical).
- ADR-084 = inter-plugin contract codify boundary axis (numeric-space encoding layer + cross-channel propagation boundary).
- **scope disjoint** — I-6 추가 시 ADR-068 의 통일된 self-check axis 가 분열. ADR-068 5 invariants 는 모두 ArchitectAgent 단일 actor 의 single-author write-time self-check, ADR-084 D2 3-곳 declare 의무는 contract author + ADR author + domain-knowledge author 3 actor 분산.
- ADR-RESERVATION row 84 이미 active 점유 (`836fa0a`) — 신규 분리 path 가 sunk cost 정합.

**D7.2 (Q2-B) reconcile-protocol-v1 §4.12/§4.13 cross-ref 갱신 Phase 1 PR scope 포함 — 거절**:
- CFP-986 `b6d7eb5` first applied case = 이미 §4.12 / §4.13 안에 D2-1 충족 (classification_severity_disjoint_invariant + classification_not_severity_clause clause 존재).
- ADR-084 가 generalization codify 만 하면 첫 instance 의 D2 충족 표면 보존 — reconcile-protocol-v1 자체 cross-ref 갱신 불필요.
- scope expansion 회피 + ADR-054 doc-only fast-path 단일 PR 정합 보존. cross-ref 갱신 (다른 contract — severity-propagation-v1 등 — 안 numeric-space-sharing site enumerate) 은 분리 후속 CFP entry 적격 (sentinel reach 시 분리 carrier 적격).

**D7.3 (Q3-B) registry audit lint entry warning tier 즉시 신설 — 거절**:
- pattern_count 1 (CFP-986 single sample, recurrence 0 sample). 실 추가 sample 발생 시 (ADR-052 touchpoint(1-6) + severity(0-2) + ADR-067 max-FIX(0-3) 3-way cohabitation 등 후보 site — Researcher §6 enumerate 영역) 신속 promotion 영역 명시 sentinel clause 가 ratchet-up direction promise + 실 추가 sample 발생 시 신속 promotion 영역 명시로 충분.
- ADR-082 §결정 6 retain pattern 답습 (Wave 1 declaration-only → Wave 2 mechanical 전환, Amendment 1 CFP-841) — 5번째 instance 정합.
- D6.3 sentinel clause 가 약화 차단 보존 + declaration-only retain 정당성 보존 (ADR-064 §self-application top-down ratchet 정합).

## 결과

### 본 ADR-084 효력 (Effective)

- **신규 inter-plugin contract 작성 시** (kind:contract / kind:registry 모두): D1 조건 A+B+C AND 충족 시 D2 3-곳 명시 declare 의무 자동 적용. ArchitectAgent §3/§7 self-check 영역 + DesignReviewPL audit 영역 (D4 behavioral directive).
- **기존 inter-plugin contract retroactive validation**:
  - CFP-986 `b6d7eb5` first applied case = 본 ADR §D3 검증 완료 (3-곳 declare 충족 — §4.12 contract 본문 + 본 ADR §D3 ADR 본문 + 동반 신설 domain-knowledge entry).
  - 기타 contract (review-verdict-v4 severity / fix-event-v1 affected_scope / label-registry-v2 numeric metadata / severity-propagation-v1 numeric severity ↔ tier mapping 등) retroactive validation = **분리 후속 CFP carrier 영역** (sentinel clause D6.3 pattern_count ≥ 2 reach 시 mandatory).
- **DesignReview lane MUST flag**: D4 behavioral directive 발효 (Phase 2 follow-up `codeforge:review-responsibility` skill / codeforge-review CLAUDE.md DesignReviewPL 체크항목 행 추가 영역 — 본 Story scope 외).

### 비-효력 (Not effective)

- src/** / tests/** / scripts/** / templates/** / .github/workflows/** 변경 0건 (doc-only fast-path invariant, ADR-054 정합).
- marketplace.json mirrored 4 field 변경 0건 (`name` / `version` / `description` / `author`, ADR-063 atomic invariant 발효 0건).
- plugin.json version bump 0건 (doc-only fast-path).
- reconcile-protocol-v1 자체 cross-ref 갱신 0건 (Q2-A retroactive validation only).
- evidence-checks-registry warning tier entry 추가 0건 (Q3-A declaration-only retain — sentinel reach 시 분리 CFP carrier).
- label-registry-v2 MINOR bump 0건 (sentinel reach 시 동반).

## 해소 기준

N/A — permanent governance policy. ADR-058 §결정 5 sunset_justification: null retain (frontmatter 명시). 약화 방향 amendment 발의 차단 — D5 약화 차단 ratchet 정합. 강화 방향 amendment (D6.3 sentinel clause activation → mechanical lint promotion / D2 4-곳 declare scope 확장 등) = 정합 ratchet-up direction (ADR-064 §self-application top-down ratchet).

self-referential 주의: 본 ADR 의 해소기준 부재 선언 자체가 D1 조건 A+B+C 발효 대상 아님 (numeric-space-sharing channel 영역 미해당). ADR-082 §결정 6 EC-3 self-protection 동형.

## 관련 파일

- [ADR-076](ADR-076-declarative-reconciliation-upgrade.md) — reconcile-protocol-v1 declarative reconciliation (first applied case host §4.12/§4.13)
- [ADR-082](ADR-082-write-time-self-write-verification-mandate.md) — disjoint 4-layer 표 governance pattern source (super-class layer disjointness 일반화 source)
- [ADR-068](ADR-068-boundary-completeness-invariants.md) — boundary completeness invariants I-1~I-5 (scope disjoint — ArchitectAgent self-check axis vs inter-plugin contract codify axis, Q1 분기 결정 영역)
- [ADR-070](ADR-070-codex-verify-before-trust.md) — Amendment 4 declaration-only retain precedent chain 4번째 instance (CFP-988)
- [ADR-081](ADR-081-codex-worker-prompt-boilerplate.md) — §결정 D6.e declaration-only retain precedent chain
- [ADR-064](ADR-064-decision-principle-mandate.md) — §self-application top-down ratchet (강화 방향만 허용) + §결정 1 CFP scope unitary
- [ADR-058](ADR-058-adr-sunset-criteria-mandate.md) — §결정 5 sunset_justification ratchet (is_transitional 약화 차단)
- [ADR-054](ADR-054-doc-only-story-fast-path.md) — doc-only fast-path 단일 PR 적격 (본 Story flow 근거)
- [ADR-040](ADR-040-worktree-convention.md) — Amendment 3 §결정 7.D normative 5 category enum (workflow-policy 부재 → mechanical_enforcement_actions[] 면제 정합)
- [ADR-045](ADR-045-story-retro-mandatory-trigger.md) — §D-9 cross-Story pattern forcing function (본 carrier = E-3 emission, EPIC-RESULTS-CFP-858.md §6.3 P-3 systemic cluster)
- [ADR-008](ADR-008-inter-plugin-contract-versioning.md) — Inter-plugin Contract Versioning (affected contract MINOR bump 적격 분기 영역)
- [ADR-010](ADR-010-inter-plugin-contract-sibling-sync.md) — Inter-plugin Contract Sibling Sync (kind:registry vs kind:contract 분기)
- [ADR-RESERVATION.md](ADR-RESERVATION.md) — row 84 active (CFP-989)
- `docs/inter-plugin-contracts/reconcile-protocol-v1.md` — CFP-986 §4.12/§4.13 first applied case (b6d7eb5)
- `docs/domain-knowledge/domain/inter-plugin-contracts/numeric-space-disjointness.md` — narrative SSOT (본 ADR 동반 신설)
- `CLAUDE.md` — cross-ref 1줄 추가 (영구 ADR section, Phase 1 PR scope)
