---
adr_number: 67
title: fix-ledger implementability escalation + max FIX overflow handling
status: Active
category: governance
date: 2026-05-13
is_transitional: false
carrier_story: CFP-526
parent_epic: CFP-525
supersedes: []
amends: []
amendment_log:
  - date: 2026-05-17
    amendment: 1
    cfp: CFP-842
    summary: "§결정 4 cross-lane RESET 정책 의 mechanical 정확도 carrier — fix-event-v1 v1.2 → v1.3 MINOR bump (affected_scope enum + affected_paths_with_depth array optional fields). cross-module / cross-repo / cross-plugin scope 결정의 mechanical evidence 보존 + broken-link/path 정정 FIX 시 over-correction regression chain (CFP-770 §8 CR-005→CR-006→CR-007 lesson) 직접 차단. fix-event-depth-scope-presence warning-tier lint (advisory only) 동반."
    scope_change: "ratchet 강화 only — 기존 §결정 4 Pause-and-resume 의미 invariant 변경 0. scope-aware mechanical input 추가로 RESET decision evidence trail 보존."
    breaking: false
    backward_compat: true
  - date: 2026-05-21
    amendment: 2
    cfp: CFP-1125
    summary: "disjoint invariant 보존 declare amendment (ADR-076 sunset 후 carrier 이전) — 본 ADR-067 RESET semantics (§결정 4) = Story progression layer (Story §10 FIX Ledger RESET? column) 의 영구 architectural invariant 명시. ADR-076 sunset (walker paradigm 전환) 후 disjoint invariant (ADR-067 RESET = Story progression layer / ADR-076 snapshot = Upgrade transaction layer, cross-pollinate 금지) 의 carrier 가 본 ADR-067 amendment + Wave 1 Story-3 imperative-walker-protocol-v1 codify 로 이전. walker step pause/resume ≠ Story §10 FIX Ledger RESET column 마커 명시."
    scope_change: "declarative invariant preservation only — 기존 §결정 1-7 의미 invariant 변경 0. is_transitional: false 유지 (영구 architectural invariant, 본체 sunset 아님). β2 audit (#1113) Anchor 5 LOSSLESS 판정 carrier."
    breaking: false
    backward_compat: true
  - date: 2026-06-30
    amendment: 3
    cfp: CFP-2480
    summary: "FIX ground-truth replay ↔ max-FIX 카운터 disjoint 명문화 + fix-event-v1 v1.3 → v1.4 MINOR carrier (reproducer_command + replay_verdict 2 optional field). Epic CFP-2476 E3. 신규 §결정 8 — (1) replay FAIL(falsified, 여전히 RED) = 닫기 게이트(close 거부)지 max-FIX 3/3 카운터 소비 아님 (disjoint); 무한거부 backstop = fix-attempt 카운터 (실제 fix 시도 = §10 Iter 증가가 max-FIX 소진, replay 재실행 자체는 카운터 무관). (2) replay fail-mode 2축 분리 — (A) replay-verdict 축(여전히 RED) = fail-closed(닫기 거부, degrade 없음, fail-open reject — 수정이 실제로 안 됨); (B) Codex-미가용 축(replay 실행 자체 불가) = lane-time fail_open_then_record_with_marker (영구보류=delivery 마비 회피, merge-time #7 fail-closed-then-bounded-degrade 와 disjoint). (3) flaky false-RED = ADR-070 §결정 D9 undetermined 분기 → max-FIX 부당소진 차단. (4) reproducer schema 제약(repo-relative 게이트/테스트 호출만, raw shell free-string 금지 = stored-command injection vector 차단, SecurityArch THR-E3-2) + base SHA-pin (reproduce-before-fix 결정론) + INV-SEC-1 (PII/secret/credential/private-path 금지 — §결정 7 reasoning_carryover security invariant 동형 확장). (5) cross-lane RESET (§결정 4) 무관 declare — replay falsified 는 RESET? column 마커 미발동."
    scope_change: "ratchet 강화 only — 기존 §결정 1-7 의미 invariant 변경 0. fix-event-v1 v1.4 additive-optional column (v1.1~v1.3 선례 4회 정합) + max-FIX disjoint 명문화(약화 0 — replay 가 카운터를 소비하지 않음을 명시해 정직성·수렴 양립). is_transitional: false 유지. ADR-058 §결정 5 sunset_justification N/A (강화 방향)."
    breaking: false
    backward_compat: true
related_stories:
  - CFP-526
  - CFP-842   # Amendment 1 — fix-event-v1 v1.3 depth-aware scope MINOR bump carrier
  - CFP-1125  # Amendment 2 — disjoint invariant 보존 declare (ADR-076 sunset 후 carrier 이전)
  - CFP-2480  # Amendment 3 — FIX ground-truth replay ↔ max-FIX disjoint + fix-event-v1 v1.4 MINOR carrier (Epic CFP-2476 E3)
related_adrs:
  - ADR-008
  - ADR-024
  - ADR-039
  - ADR-050   # parallel-epic-conflict-coordination (file disambiguation — ADR-050 number 가 multi-repo-story-key 와 share)
  - ADR-052
  - ADR-054
  - ADR-058
  - ADR-059
  - ADR-060   # Amendment 1 carrier — fix-event-depth-scope-presence warning-tier evidence-checks-registry entry
  - ADR-063
  - ADR-064
  - ADR-070   # Amendment 3 — FIX-close verify-before-trust (replay_verdict = §결정 D9 3-상태 disposition 정합, E3 sibling)
  - ADR-119   # Amendment 3 — §결정 10② close-time wire 실현 ("수정됨=반증 후 단언")
related_files:
  - skills/fix-ledger-schema/SKILL.md
  - docs/inter-plugin-contracts/fix-event-v1.md
  - docs/orchestrator-playbook.md
  - docs/evidence-checks-registry.yaml   # Amendment 1 — fix-event-depth-scope-presence warning-tier entry
  - CLAUDE.md
mechanical_enforcement_actions: []
---

# ADR-067: fix-ledger implementability escalation + max FIX overflow handling

## 상태

Active (2026-05-13). carrier_story = CFP-526 (Epic-FIX-ESCALATION-prevention Wave 1, doc-only fast-path ADR-054). parent_epic = CFP-525.

## 컨텍스트

mctrader-hub Story MCT-150 (Stage 2 첫 Story, uploader hardening, 5 SP) Phase 2 진행 중 design-review ↔ code-review FIX cycle **4회** 발생 (max counter 3/3 도달 + ESCALATE Option A RESET, 2026-05-13 KST). 매 FIX 마다 이전 fix 의 정합 적용 결과로도 다음 review 가 새 dimensional finding 을 catch. 13 곳 wording desync (`hard_floor_breached` ↔ impl `hard_floor_blocked`) silent bug surface → caller (MCT-152 collector) MANUAL_GATE escalation path 누락 + RPO=0 invariant violation risk.

CFP-525 (Epic-FIX-ESCALATION-prevention) brainstorm spec 합의 framing:

- **H6 (systemic root cause)**: DesignLane 내부 adversarial debate 부재로 인한 convergence quality 미달. single-pass ArchitectAgent + sequential review topology 자체가 boundary completeness gap / dimensional extension anti-pattern / handoff wording drift 의 증상 surface.
- **RC#3 + RC#5 = remediation tracks (본 ADR scope)**: fix-ledger RESET 정책 명문화 + implementability reassessment 절차 + reasoning carryover field.

본 ADR 의 motivation 3 vector:

1. **사용자 directive (2026-05-13)** verbatim: "Arch ↔ design fix 3회 초과 시 타협이 어려웠던 부분을 기준으로 요건이 구현 가능한 수준인지 보수적으로 평가하도록 하고 필요한 경우 사용자에게 escalation 해야함." → reactive ESCALATE 패턴 → prescriptive deterministic trigger 전환.
2. **Researcher unknown unknown #1 — Information loss between FIX iterations**: ArchitectPL re-spawn 시 직전 finding 만 input, 전체 transcript 비주입 = architectural amnesia. §10 row reasoning carryover 부재가 직접 carrier.
3. **Codex D6 적대적 검토 발견**: full transcript verbatim 회피 (이전 framing 고정 차단). 3-part 구조 (invariant summary + disputed claims + transcript ref) 가 reasoning trail 보존 + 새 framing 가능성 양립.

본 ADR 의 placement context:

- **ADR-039 §결정 3 (Orchestrator §10 monopoly)** 와 정합. `reasoning_carryover` field 추가는 schema MINOR bump — append writer 주체 (Orchestrator) 영향 0.
- **ADR-059 §결정 3 (debate-protocol-v1 reasoning carryover via `debate_artifact_ref`)** 와 disjoint scope. debate 발동 FIX 시 = `debate_artifact_ref` / 비-debate FIX (max FIX 3/3 implementability reassessment) 시 = `reasoning_carryover`. EC-1 명세.
- **ADR-052 (Codex Proactive Check 6 touchpoints)** 와 의미 boundary 분리: 본 ADR = post-failure escalation (FIX 3/3 후), ADR-052 = pre-failure proactive check (Story §1-§6 완료 직후). 분리 근거 = trigger timing + carrier mechanism + verdict format 3 axis 모두 disjoint.
- **ADR-064 (결정 원칙 mandate)** 와 정합. 본 ADR 본문 forbid-list 8 어휘 (`임시 / 단계적 / 일단 / 우선[시간] / 잠정 / 가벼운 / minimal viable / quick win`) 0건 — 영구 governance 정책 선언.

## 결정

### 결정 1 — max FIX 3/3 도달 시 deterministic implementability reassessment trigger

Story 진행 중 동일 lane (`설계-리뷰` / `구현-리뷰`) FIX count 가 RESET 마커 이후 3 회 도달 (`current_count == 3`) AND 다음 FIX event 보고 수령 시점 (`current_count → 4` 진입 임박):

Orchestrator 는 **추가 FIX iteration 진입 이전** 다음 의무:

1. `codeforge:fix-ledger-schema` skill 호출 (max FIX 3/3 도달 패턴 매칭 확인)
2. ArchitectPLAgent re-spawn — implementability reassessment 의무 packet 전달
3. ArchitectPL verdict 수령 전까지 4번째 FIX iteration 자동 진입 금지 (reactive 패턴 차단 — ESCALATE Option A RESET 만으로 결정 위임 안 됨)

Trigger 범위 = `설계-리뷰` / `구현-리뷰` 2 lane (max_fix_per_cycle = 3 lane). `구현-테스트` / `보안-테스트` (max = ∞) 는 본 trigger 영역 외.

### 결정 2 — escalation 의무 trigger 3종 명문화

ArchitectPL implementability reassessment 수행 중 다음 3 조건 중 1 이상 hit 시 verdict = `escalate_to_user` 의무:

- **(i) design granularity inadequate**: ESCALATE root cause 가 "boundary 가 잘못 잡혀 동일 boundary 재시도가 무의미" — 3 FIX cycle 동안 동일 axis 의 결함이 surface area 만 다르게 재발 (예: mctrader-hub MCT-150 의 hard_floor wording 13 곳 ↔ MANUAL_GATE caller path 누락 패턴).
- **(ii) cross-module invariant 위반 without convergence path**: 3 FIX cycle 누적 P1 finding 의 영향 module 수 ≥ 3 (`cross_module_propagation`) AND convergence path (=동일 boundary 내 fix 로 해소 가능한 path) 미식별. mctrader-hub MCT-150 의 RPO=0 invariant + hard_floor wording SSOT 가 대표 사례.
- **(iii) DeveloperPL ↔ ArchitectPL N+1 round divergence 유지**: 직전 N rounds 의 양 PL verdict packet `pl_recommendation` divergence ≥ 2회 AND 다음 round 에서도 같은 axis 의 disagreement 가 reduce 되지 않을 것이 예측됨 (= 동일 axis 의 reviewer divergence 가 anchor 별도 ≥ 2회 — ADR-059 `anchor_recurrence_count` 패턴 정합).

3 trigger 평가는 **dual metric 정량 보조** (보수적 평가 SSOT — 결정 6 참조):

- `cumulative_P0 >= 2` OR `cumulative_P1 >= 5` OR `reviewer_divergence_count >= 2` 시 trigger (i/ii/iii) 후보 강격상.
- 정량 metric hit + 정성 trigger evaluation 결합 = escalation 의무.

3 trigger 모두 miss + 정량 metric 모두 miss 시 verdict = `reset_and_redesign` 가능 (결정 3).

### 결정 3 — ArchitectPL 재량 RESET vs escalation 결정 권한

max FIX 3/3 도달 + ArchitectPL reassessment 완료 시:

- 결정 2 의 3 trigger 모두 miss + dual metric 모두 miss = "보수적 평가 결과 현 boundary 재시도 가능 + 다음 round convergence 가능" → ArchitectPL verdict = `reset_and_redesign` 가능.
- Orchestrator 는 §10 row 의 `RESET?` column 에 `RESET <lane>` 마커 + ArchitectAgent 재spawn (Change Plan 갱신) 진행.
- ArchitectPL verdict packet 의 `reasoning_carryover` 3-part 의무 동반 (escalate / reset 무관, 이전 framing 고정 차단 forcing function — 결정 5).

### 결정 4 — cross-lane RESET 정책 — Pause and resume

implementability reassessment 진행 중 (또는 사용자 escalation 대기 중) cross-lane (보안-테스트 또는 구현-테스트) 신규 FIX 발생 시:

**채택: Pause-and-resume**. 현 escalation 일시 pause + 보안 (또는 구현-테스트) FIX 선행 수행 → 해당 lane PASS 후 escalation 재개. `RESET?` column 에 `"cross-lane-pause:<lane>"` 마커 명시 (예: `"cross-lane-pause:보안-테스트"`).

거부 옵션 — Bundled escalation: 보안 FIX 도 escalation packet 에 통합 → 사용자 결정 시 종합 검토. 거부 사유 (CFP-526 §7 ArchitectPL 채택):
- cross-lane reasoning bundling 시 reasoning_carryover SSOT 단일성 손상 (1 lane reasoning chain per row invariant 위반)
- 사용자 decision noise 증가 risk (multi-lane finding mix → 결정 영역 분산)
- `RESET?` column 시맨틱 확장 복잡도 증가 (`"cross-lane-bundle:<lane>"` value family 도입 필요)

Pause-and-resume 의 latency trade-off 는 acceptance — escalation 자체가 사용자 dialog 대기 시점이므로 cross-lane FIX latency 가 직접 critical path 영향 0.

#### Amendment 1 (CFP-842, 2026-05-17) — depth-aware scope mechanical 정확도 carrier

본 결정 4 의 cross-lane RESET 결정 input 의 mechanical evidence 보존 carrier — fix-event-v1 v1.2 → v1.3 MINOR bump 2 optional 필드 신설:

- **`affected_scope`** enum (`single-file` / `cross-module` / `cross-repo` / `cross-plugin`) — Orchestrator 가 FIX root cause 판정 직후 결정. RESET 결정 영향 표:

  | affected_scope | ArchitectPL 행동 |
  |---|---|
  | `single-file` | 동일 lane FIX iter 유지 (RESET 회피) |
  | `cross-module` | cross-lane RESET 적극 검토 (본 §결정 4 Pause-and-resume 발동 후보) |
  | `cross-repo` | cross-lane RESET + sibling sync 영역 진단 (ADR-010 정합) |
  | `cross-plugin` | cross-lane RESET + marketplace atomic invariant 진단 (ADR-063 정합) |

- **`affected_paths_with_depth`** array of `{path, depth}` — broken-link / path 정정 FIX 영역 한정 의무. `depth` = repo root 기준 dir depth. 정정 규칙 적용 범위 (예: `depth >= 2 then path adjust = '../../'`) 의 mechanical reasoning trace 보존 — CFP-770 §8 CR-005→CR-006→CR-007 over-correction regression chain lesson directly carrier (depth 정보 부재가 directly carrier 였음).

**ratchet 강화 only**: 본 §결정 4 의 Pause-and-resume 의미 invariant 변경 0 — mechanical input 추가만. backward-compat 100% (2 optional field, 기존 9-column row null 또는 column 생략 valid).

**mechanical enforcement**: `fix-event-depth-scope-presence` warning-tier lint (advisory only, blocking-on-pr 미승격) — broken-link/path FIX 인데 `affected_paths_with_depth` 누락 시 적발. `hotfix-bypass:fix-event-depth-scope` label 부착 PR = lint skip + audit comment 자동 발의. SSOT = [`docs/evidence-checks-registry.yaml`](../evidence-checks-registry.yaml).

cross-ref:
- [`docs/inter-plugin-contracts/fix-event-v1.md`](../inter-plugin-contracts/fix-event-v1.md) v1.3 §2 Schema + §3 항목 (affected_scope / affected_paths_with_depth)
- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) §6.7 v1.3 depth-aware scope 의무
- [`templates/story-page-structure.md`](../../templates/story-page-structure.md) §10 column expansion

### 결정 5 — `reasoning_carryover` field 3-part structured 구조 + fix-event-v1 v1.2 MINOR bump

fix-event-v1 v1.1 → v1.2 MINOR bump — 9 번째 trailing optional column 추가:

```yaml
reasoning_carryover:
  type: "object | null"
  required: optional        # v1.2 신규, backward-compat 보장 (CFP-526)
  introduced_in: "1.2"
  schema:
    invariant_summary:
      type: string
      constraints: ["≤2 lines (≤200 chars 권장)"]
      description: "이번 FIX cycle 의 '타협 불가' axis 요약 (예: 'RPO=0 invariant + hard_floor wording cross-module SSOT')"
    disputed_claims:
      type: "list[string] | string"
      description: "직전 round 에서 합의되지 않은 핵심 disagreement 항목. 형식 자유 (list 또는 free-form)."
      security_invariant: "PII / secret / credential 포함 금지 — SecurityArchitect deputy SSOT (§7.5 정합)"
    transcript_ref:
      type: string
      description: |
        - debate 발동 시: Story §9 section anchor link 형식 (예: `#debate-transcript-F-001`) — 단 본 field 는 비-debate FIX 영역, debate_artifact_ref 와 disjoint
        - 비-debate FIX 시: Story §9 section anchor link (예: `#fix-3-architectpl-reassessment`) 또는 직전 verdict packet evidence path
        Full transcript verbatim 회피 (Codex D6 — 이전 framing 고정 차단)
  cross_ref:
    - docs/adr/ADR-067-fix-ledger-implementability-escalation.md (본 ADR §결정 5)
    - docs/inter-plugin-contracts/debate-protocol-v1.md (debate_artifact_ref consumer — disjoint scope)
```

3-part 구조 채택 근거 (옵션 a structured YAML keys over 옵션 b free-form 3-paragraph markdown):

- **검색 / diff 용이**: machine-readable keys 가 향후 lint / KPI extraction 의 forcing function (예: cross-Story disputed_claims pattern 통계).
- **migration 용이**: 7-column / 8-column / 9-column 3종 row 공존 (backward-compat) 시 9 번째 column parse 가 키 기반 deterministic.
- **결정 영역 일관성**: 본 codeforge 의 다른 contract field (예: `debate_artifact_ref` link 형식, `mechanical_self_check_passed` bool) 가 모두 structured — 패턴 정합.

`debate_artifact_ref` (v1.1, CFP-391) 와 `reasoning_carryover` (v1.2, 본 ADR) **disjoint scope**:

- debate 발동 FIX 시 = `debate_artifact_ref` 채움 + `reasoning_carryover = null` (debate transcript 가 이미 reasoning trail 보존)
- 비-debate FIX (max FIX 3/3 implementability reassessment) 시 = `debate_artifact_ref = null` + `reasoning_carryover` 의무
- 일반 FIX (max FIX 3/3 미도달, debate 미발동) = 양 field 모두 `null` 또는 column 생략 (backward-compat)

Producer = Orchestrator (FIX Ledger writer monopoly 유지 — CFP-32). ArchitectPL verdict packet 으로 reassessment 결과 전달 → Orchestrator 가 §10 row append.

### 결정 6 — ArchitectPL "보수적 평가" dual metric SSOT

사용자 directive verbatim ("타협이 어려웠던 부분을 기준으로 요건이 구현 가능한 수준인지 보수적으로 평가") 의 정량 SSOT:

**Dual metric** 채택 (단일 metric 의 cross-module gap evidence 누락 risk 회피):

- **Metric A — cumulative finding severity**:
  - `cumulative_P0 >= 2` (RESET 이후 누적 P0 count) → escalation trigger 후보 격상
  - OR `cumulative_P1 >= 5` (RESET 이후 누적 P1 count) → boundary completeness gap pattern signal
- **Metric B — reviewer divergence count**:
  - `reviewer_divergence_count >= 2` (동일 anchor 가 ≥ 2회 review 에서 divergent verdict — ADR-059 `anchor_recurrence_count` 패턴 정합)

Metric A OR Metric B 1+ hit = 결정 2 의 3 trigger (i/ii/iii) 후보로 강격상. 정성 trigger evaluation + 정량 dual metric 결합 → escalation 의무.

**Dual metric threshold corroboration evidence** (mctrader-hub MCT-150 §10 FIX trail, 2026-05-13):

| row | lane | finding 분포 | 누적 P0 | 누적 P1 | reviewer divergence |
|---|---|---|---|---|---|
| row 1 | design-review FIX#1 | P0=0 / P1=3 | 0 | 3 | 0 |
| row 2 | code-review FIX#2 | P0=2 / P1=3 (양 reviewer 동일 교차 일치) | 2 (≥2 threshold **hit**) | 6 (≥5 threshold **hit**) | 1 |
| row 3 | code-review FIX#3 | P0=NEW-1 + P1=NEW-1 (dimensional extension) | 3 | 7 | 2 (≥2 threshold **hit**) |
| row 4 | ESCALATE | P1=NEW-2 + P1=NEW-3 | 3 | 9 | 2 |

row 2 시점 = Metric A (cumulative P0≥2 AND cumulative P1≥5) 동시 hit. row 3 시점 = Metric B (reviewer_divergence_count≥2) 추가 hit. row 4 ESCALATE Option A RESET 도달 이전 row 2-3 시점에서 dual metric 충족 — 본 ADR §결정 1 deterministic trigger 가 land 되었다면 row 4 진입 이전 ArchitectPL implementability reassessment + 사용자 escalation 발동 가능했음. 본 case study evidence 가 dual metric threshold 의 ex-post calibration 근거.

거부 후보 metric:

- **(b) 영향 file count**: surface area proxy 일뿐, 동일 boundary 내 mechanical mirror (예: 13 곳 wording desync) 와 cross-boundary propagation 구분 불가.
- **(c) cross-module propagation 깊이**: 결정 2 (ii) trigger 정성 평가에 이미 흡수 — 정량 redundancy 회피.

### 결정 7 — `reasoning_carryover` security invariant

`disputed_claims` sub-field 본문에 PII / secret / credential / API key / private path 포함 금지 (SecurityArchitect SubAgent SSOT — §7.5 민감 데이터 분류 정합).

근거: §10 FIX Ledger = public PR description 에 자동 mirror (`fix-ledger-sync.yml` Action) — secret 노출 surface. ArchitectPL verdict packet 작성 시 사용자 escalation 대비 disputed_claims sub-field 의 모든 entry 가 design vocabulary level 로 abstraction 유지 의무.

위반 사례 발견 시 Orchestrator append 의무 차단 (자동 redact 금지 — fail-fast 후 ArchitectPL re-author).

## 결과

### Direct outputs

- **`docs/inter-plugin-contracts/fix-event-v1.md`** v1.1 → v1.2 MINOR bump — `reasoning_carryover` optional 9 번째 column 추가 + amendment_log row append + schema sub-section.
- **`skills/fix-ledger-schema/SKILL.md`** 본문 4 bullet 확장 — implementability reassessment 5-step (current_count==3 감지 / ArchitectPL spawn / verdict 수령 / RESET vs escalate / §10 append) + escalation 3 trigger 인용 + cross-lane RESET 정책 (Pause-and-resume) + `reasoning_carryover` field 설명.
- **`docs/orchestrator-playbook.md`** §6.4 보강 — `reasoning_carryover` schema + Orchestrator append 절차 / §6.5 보강 — ArchitectPL reassessment 절차 + dual metric / §6.6 보강 — parallel diagnosis 후 max FIX 3/3 trigger 자동 prepend.
- **`CLAUDE.md`** "FIX 루프" 단락 1 줄 cross-ref append (cap ≤320 정합).
- **`CHANGELOG.md`** Unreleased entry — fix-event-v1 v1.2 / ADR-067 신설 / skill 본문 확장 / playbook §6.4-6.6 보강.
- **`.claude-plugin/plugin.json`** + **`marketplace.json`** (sibling repo) — version 5.31.0 → 5.32.0 MINOR bump (atomic invariant ADR-063 정합).

### Indirect impact

- **Wave 4 (CFP-530, ADR-059 Amendment 1)**: debate-protocol-v1 §convergence_quality_invariant 정의 시 본 ADR §결정 5 의 `reasoning_carryover` ↔ `debate_artifact_ref` disjoint scope 가 prerequisite 정합 anchor.
- **codeforge family sibling sync**: kind:registry (fix-event-v1) = sibling sync 면제 (CLAUDE.md "Inter-plugin Contract" 단락 / ADR-010 정합). 단 sibling plugin (review / design / develop / pmo / test) 의 `templates/*.md` 본문이 fix-event-v1 v1.1 schema verbatim 인용한 경우 v1.2 column 갱신 필요 — DesignReview lane 검증 의무 (false closure 차단).
- **mctrader-hub MCT-151+**: codeforge upgrade 후 동일 failure class (4 FIX ESCALATE Option A pattern) 재발 감소 KPI signal — Epic-FIX-ESCALATION-prevention 의 acceptance criteria #5.
- **KPI measurement framework**: 후속 별도 carrier (CFP-525 acceptance criteria #4) 에서 본 ADR `reasoning_carryover` field 의 cross-Story 통계 (disputed_claims 빈발 axis / reviewer_divergence 빈발 anchor) extraction 의무. evidence-checks-registry-v1 entry 후보.

### Alternatives 검토 (3+ 검토)

대안 1 — **blanket auto-escalate at FIX 3/3**: max FIX 3/3 도달 = 즉시 사용자 escalation, ArchitectPL 재량 절차 0.

- 거부 사유: 사용자 escalation surface 과다 증가 — 일반 trivial FIX cycle (3 cycle 내 mechanical convergence 가능) 도 escalate → user attention 낭비. dual metric 정량 + 정성 trigger 평가가 reactive auto-escalate 대비 false-escalation rate 감소.

대안 2 — **PL 재량 only (현행 ESCALATE Option A RESET pattern)**:

- 거부 사유: 본 Story 의 직접 카탈리스트 사례 (MCT-150 4 FIX cycle). reactive 패턴 만으로는 silent bug 누적 risk + reasoning loss 누적 — 사용자 directive verbatim 의 "보수적 평가" SSOT 정량화 의무 미충족.

대안 3 — **사용자 immediate AskUserQuestion at FIX 1**:

- 거부 사유: codeforge governance 정합성 침해. FIX 1-2 cycle 은 normal convergence path — ArchitectPL synthesizer 책무 선행. 결정 원칙 (ADR-064) Trace 2 Rule 5 "AskUserQuestion 범위 제한 — 가치 판단 / 미공개 컨텍스트 2 종 한정" 정합 위배.

대안 4 — **ADR-052 Amendment 으로 흡수 (별도 ADR 미신설)**:

- 거부 사유 (Codex D9 권고 정합): ADR-052 = pre-failure proactive check (Story §1-§6 직후 6 touchpoint). 본 ADR = post-failure escalation (FIX 3/3 후 reassessment). trigger timing / carrier mechanism / verdict format 3 axis 모두 disjoint — Amendment 시 ADR-052 영역 의미 confusion + dimensional extension anti-pattern signal. 별도 ADR 분리가 governance 명료성 보존.

### 중복성 검토 결과 (Codex D9 권고 gate)

ADR-052 (Codex Proactive Check) / ADR-064 (결정 원칙) / ADR-039 (subagent default) 의 의미 중복 검증:

- **vs ADR-052**: 분리 (위 대안 4 거부 사유 동일). pre-failure proactive vs post-failure escalation 의 trigger / mechanism / format 3 axis disjoint.
- **vs ADR-064**: 분리. ADR-064 = Orchestrator 의 결정 제안 시점 normative (`Trace 1-4`). 본 ADR = ArchitectPL 의 max FIX 3/3 시 verdict format normative — 다른 agent + 다른 lifecycle phase + 다른 carrier.
- **vs ADR-039**: 정합 (충돌 없음). ADR-039 §결정 3 Orchestrator §10 monopoly invariant 유지 — `reasoning_carryover` field 추가는 schema MINOR bump, append writer 영향 0.

세 ADR 모두 본 ADR 의 related_adrs frontmatter 에 명시 (cross-ref forcing function).

## 해소 기준

N/A — permanent policy (`is_transitional: false`).

근거 (ADR-058 §결정 7 정합):

- 본 ADR 은 governance carrier 영구 정책 — fix-event-v1 schema 의 reasoning carryover invariant 는 codeforge 의 FIX 루프 reasoning preservation contract 의 SSOT.
- 향후 amendment 시 ADR-058 §결정 5 (amendment justification 의무) 정합 — `sunset_justification` 미적용 (transitional 아님), 대신 amendment scope 명시 의무.
- recursive sunset 회피 패턴 정합 사례: ADR-064 (결정 원칙 mandate), ADR-058 (sunset criteria mandate), ADR-013 (codeforge family dogfood-out), ADR-016 (marketplace registration), ADR-042 (agent model selection).

## Amendment 2 (CFP-1125 carrier) — walker paradigm 전환 후 disjoint invariant 보존 declare

본 ADR-067 RESET semantics (§결정 4) = Story progression layer (Story §10 FIX Ledger 의 `RESET?` column). CFP-1125 walker paradigm 전환 후에도 본 disjoint invariant (ADR-076 §결정 4 verbatim, "ADR-067 RESET = Story progression layer / ADR-076 snapshot = Upgrade transaction layer, cross-pollinate 금지") 는 본 ADR-067 본체에 영구 보존.

ADR-076 sunset 후 disjoint invariant 의 carrier = 본 ADR-067 amendment + Wave 1 Story-3 imperative-walker-protocol-v1 codify 안 명시 (walker step pause/resume ≠ Story §10 FIX Ledger RESET column 마커).

- **본 disjoint invariant 는 sunset 대상 아님** — `is_transitional: false` 유지 (영구 architectural invariant)
- ADR-076 sunset 후 declarative anchor 이전 = 본 ADR-067 amendment + walker schema ADR

**cross-ref**: [CFP-1125](https://github.com/mclayer/plugin-codeforge/issues/1125) + [β2 audit (#1113)](https://github.com/mclayer/plugin-codeforge/issues/1113) Anchor 5 LOSSLESS 판정.

### sunset_executed (CFP-1186, 2026-05-22) — disjoint invariant carry 영역 한정

**상태**: disjoint invariant carry 영역 Sunsetted — ADR-076 §결정 4 verbatim "ADR-067 RESET = Story progression layer / ADR-076 snapshot = Upgrade transaction layer, cross-pollinate 금지" 의 ADR-076 참조 sibling carrier 역할 이 imperative-walker-protocol-v1 으로 lossless carry 완료됨.

carry 증거 (β2 audit Anchor 5 LOSSLESS 확인):
- imperative-walker-protocol-v1 안 walker step pause/resume ≠ Story §10 FIX Ledger RESET column 마커 명시 — disjoint invariant 동일 의미로 carry
- ADR-076 sunset 후 disjoint invariant declarative anchor = 본 ADR-067 amendment (Amendment 2) + walker schema ADR 양 쪽 보존

**is_transitional 무변경**: `false` 유지 (ADR-067 본체 §결정 1-7 RESET semantics = Story progression layer 의 영구 architectural invariant. 본체 sunset 아님).

**본 sunset 영역 한정**: ADR-076 §결정 4 sibling carrier role 만 (= disjoint invariant 의 "ADR-076 쪽 선언 역할" carry). ADR-067 본체 §결정 1-7 FIX-loop RESET semantics 영역은 sunset 대상 아님 — 계속 유효.

**본 ADR 본문 삭제 금지**: Sunsetted = 해당 영역의 carry 완료 선언. 본문은 historical record 로 영구 보존.

## Amendment 3 (CFP-2480 carrier) — FIX ground-truth replay ↔ max-FIX disjoint + fix-event-v1 v1.4 MINOR

Epic CFP-2476 E3 (Codex 실행형 정책 게이트 팩 + FIX ground-truth replay). FIX "수정됨" close 를 원 reproducer 재실행 반증(외부 Retest)으로 강제하는 mechanism 이 본 ADR 의 max-FIX 카운터(§결정 1~3)와 어떻게 상호작용하는지 codify. 신규 §결정 8 추가 only — D1-D7 + Amendment 1/2 본문 의미 변경 0건.

### 결정 8 — FIX replay ↔ max-FIX 카운터 disjoint + replay fail-mode 2축 + reproducer security invariant

#### 8.1 replay FAIL ↔ max-FIX 카운터 disjoint (핵심)

FIX "수정됨" 닫기 = 원 finding 을 정당화한 reproducer 재실행 GREEN(외부 Retest, ADR-119 §결정 10② close-time wire) 반증 후에만 성립 (fix-event-v1 v1.4 `replay_verdict == PASS`). replay 가 여전히 RED(`falsified`)일 때 이는 **max-FIX 3/3 카운터를 소비하지 않는다** — replay 는 "닫기 전 검증 게이트" 지 새 FIX iteration 이 아니다.

- **disjoint 의미**: replay `falsified` = "현 iter 미완결(닫기 거부)" 이지 max 3/3 진입(`current_count → 4`, §결정 1 trigger) 이 아니다. replay 재실행 자체는 §10 row Iter 를 증가시키지 않는다.
- **무한거부 backstop = fix-attempt 카운터**: replay 가 반복 `falsified` 면 무한루프 위험은 max-FIX 가 아니라 **실제 fix 시도** (새 §10 row Iter)가 backstop 한다. DeveloperPL 이 새 fix 를 시도(새 Iter append)할 때마다 max-FIX(설계-리뷰/구현-리뷰 lane)가 소진되고, 그 카운터 3/3 도달 시 §결정 1~3 implementability reassessment 가 정상 발동한다. replay 게이트는 닫기 정직성만 담당.
- **§결정 1~3 무손상**: max-FIX trigger 범위(설계-리뷰/구현-리뷰 2 lane), escalation 의무 3종(§결정 2), RESET vs escalation 권한(§결정 3) 본문 의미 변경 0. replay 는 그 카운터의 입력도 출력도 아닌 disjoint axis (close-gate).

**사용자 trade-off 정합 (req §5.6 #2)**: disjoint = 정직성↑ but 무한거부 위험 / 카운터 소비 = 수렴 강제 but 정직성 약화. 채택 = **disjoint** (정직성 우선, §1 "주장 아닌 실측") + safety valve = fix-attempt 카운터(max-FIX)가 별 채널로 수렴 강제. replay N회 `falsified` 반복 시 사용자 escalation 은 max-FIX implementability reassessment(§결정 2) 가 흡수.

#### 8.2 replay fail-mode 2축 분리 (InfraOp refinement)

replay 의 fail 은 두 disjoint 축이다 (혼동 시 게이트 hollow):

| 축 | 의미 | disposition | 근거 |
|---|---|---|---|
| **(A) replay-verdict 축** | 원 reproducer 가 여전히 RED (수정이 실제로 안 됨) | **fail-closed (닫기 거부), degrade 없음** (`replay_verdict: falsified`) | replay 본질 = "주장 아닌 실측"(§1). fail-open 하면 게이트 자체 hollow = #2322 self-attest 위조면 동형 hole → fail-open reject |
| **(B) Codex-미가용 축** | replay 실행 자체 불가 (Codex CLI/sandbox 미가용) | **lane-time `fail_open_then_record_with_marker`** (`[fix-replay-fallback: fail-mode=codex_unavailable, disposition=open]`) | 영구보류 = delivery 마비. lane-time ≠ 마지막 방어선 (ADR-070 Amd10/11 §D8/D9 동형) |

merge-time #7 의 `fail_closed_then_bounded_degrade`(ADR-070 §결정 D7)와 다름 — **#7 의 degrade 는 (B)축(Codex 미가용)용** 이고 **FIX replay (A)축은 degrade 대상이 아니다** (수정이 실제로 안 됨 → 닫기 거부가 정답, degrade 시 부당 close).

#### 8.3 flaky false-RED → undetermined (max-FIX 부당소진 차단)

replay 가 flaky(다회 결정론 미충족 또는 mixed)면 `replay_verdict: undetermined` (ADR-070 §결정 D9 undetermined 분기 동형) — quarantine 보류. 1회 GREEN close 금지(false-GREEN = §1 목적 정면 훼손 최위험) + mixed quarantine(false-RED = 진짜 고쳤는데 flaky 실패로 max-FIX 부당 소진 차단). 결정론 확인 횟수 = 설정값(`deterministic_runs_required`, 하드코딩 금지 — §8 Perf Baseline).

#### 8.4 reproducer security invariant (§결정 7 reasoning_carryover security invariant 동형 확장)

fix-event-v1 v1.4 `reproducer_command` (실패 명령 verbatim + base SHA) 는 public PR mirror surface 다 (fix-ledger-sync.yml → Story Issue comment mirror). §결정 7 reasoning_carryover security invariant 를 reproducer 영역으로 동형 확장:

- **schema 제약 (SecurityArch THR-E3-2 강한이의 반영)**: `reproducer_command.command` = **repo-relative 게이트/테스트 호출 형태만** (예: `bash scripts/check-plugin-version-bump-self.sh --self-test`). raw shell free-string 금지 = stored-command injection vector 차단 (Codex worker 발화 reproducer 가 inter-agent trust 경로로 더 위험 — Evgrafov 82.4% > direct 41.2%, ADR-070 X-4 cited).
- **base SHA-pin** (InfraOp): reproduce-before-fix 결정론 기준. replay 기준 = "원 finding SHA 의 자식(fix 포함) worktree HEAD 에서 원 reproducer 재실행" = retest (명령·입력 결정론 고정, 과거 시간여행 아님).
- **INV-SEC-1**: PII / secret / credential / API key / private absolute-path 금지 (repo-relative·환경독립 명령만). Orchestrator append 전 SCAN + 위반 시 fail-fast (자동 redact 금지, audit 가능성).
- **INV-SEC-2**: `replay_verdict` 동반 stdout 발췌는 exit + 모순 라인만 최소 (전체 dump 금지).

#### 8.5 cross-lane RESET (§결정 4) 무관 declare

replay close-gate 는 §결정 4 cross-lane RESET semantics 와 disjoint — replay `falsified` 는 §10 row 의 `RESET?` column 마커를 발동하지 않는다 (닫기 거부일 뿐 lane 카운터 리셋 아님). Pause-and-resume(§결정 4) 영역 무변경.

#### 8.6 declaration-only retain + ratchet 정합

- `mechanical_enforcement_actions: []` retain (replay close-time 자동 wire = Phase 2 / 후속 carrier, ADR-064 §결정 1 unitary). 결정 SSOT = `scripts/lib/fix_replay_disposition.py` (pure function + provenance + discriminating test, CI 미배선 — Story A/B 선례 동형 helper).
- ratchet 강화 방향 (max-FIX disjoint 명문화 + replay fail-mode 2축 + reproducer security invariant codify, 약화 0 — replay 가 카운터를 소비하지 않음을 명시해 정직성·수렴 양립). is_transitional: false 유지. ADR-058 §결정 5 sunset_justification N/A. ADR-070 Amendment 12 + ADR-119 §결정 10② + fix-event-v1 v1.4 sibling cross-ref.

## 관련 파일

- [`skills/fix-ledger-schema/SKILL.md`](../../skills/fix-ledger-schema/SKILL.md) — 본 ADR §결정 1 / §결정 4 / §결정 5 narrative SSOT 본문 (호출 시점 + 핵심 룰).
- [`docs/inter-plugin-contracts/fix-event-v1.md`](../inter-plugin-contracts/fix-event-v1.md) — 본 ADR §결정 5 schema SSOT (v1.2 MINOR bump).
- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) — 본 ADR §결정 1 / §결정 2 / §결정 6 narrative SSOT (§6.4-6.6 절차).
- [`CLAUDE.md`](../../CLAUDE.md) — "FIX 루프" 단락 cross-ref 1 줄 (cap ≤320 정합).
- [`docs/adr/ADR-008-inter-plugin-contract-versioning.md`](ADR-008-inter-plugin-contract-versioning.md) — fix-event-v1 v1.1 → v1.2 MINOR bump 정책 anchor.
- [`docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md`](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — §결정 3 Orchestrator §10 monopoly invariant.
- [`docs/adr/ADR-052-codex-proactive-check-touchpoints.md`](ADR-052-codex-proactive-check-touchpoints.md) — pre-failure proactive check 분리 anchor.
- [`docs/adr/ADR-058-adr-sunset-criteria-mandate.md`](ADR-058-adr-sunset-criteria-mandate.md) — `is_transitional: false` permanent policy 분류 anchor.
- [`docs/adr/ADR-059-debate-protocol-v1.md`](ADR-059-debate-protocol-v1.md) — `debate_artifact_ref` ↔ `reasoning_carryover` disjoint scope anchor.
- [`docs/adr/ADR-064-decision-principle-mandate.md`](ADR-064-decision-principle-mandate.md) — 결정 원칙 forbid-list 8 어휘 정합 anchor.
- mclayer/codeforge-internal-docs `wrapper/stories/CFP-526.md` — 본 ADR carrier Story (Wave 1 doc-only fast-path).
- mclayer/plugin-codeforge#525 — parent Epic carrier Issue (Epic-FIX-ESCALATION-prevention).
