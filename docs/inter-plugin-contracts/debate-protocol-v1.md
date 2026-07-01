---
kind: registry
registry: debate-protocol
version: "1.3"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/debate-protocol-v1.md
date: 2026-05-13
authors:
  - ArchitectAgent (CFP-391 carrier — ADR-059 protocol SSOT)
  - ArchitectAgent (CFP-533 — v1.1 MINOR bump, dispatch_mode field required 전환)
  - ArchitectAgent (CFP-582 — v1.2 MINOR bump, blanket_cross_module_designlane dispatch enum + convergence_quality_invariant block 신설)
  - ArchitectAgent (CFP-2534 — v1.3 MINOR bump, refactor lane consumer + blanket_refactor dispatch enum + role_assignment optional 필드. ADR-059 Amendment 3 동반)
version_history:
  - { version: "1.0", date: 2026-05-11, carrier: CFP-391, change: "initial — protocol schema + 라운드 정책 + termination + anti-sycophancy + reasoning carryover + lane-agnostic" }
  - { version: "1.1", date: 2026-05-13, carrier: CFP-533, change: "MINOR bump — dispatch_mode field optional → required + enum 3-value 명시화 (auto_on_divergence / mechanical_fast_path_inline / user_request_only). ADR-059 Amendment 1 동반." }
  - { version: "1.2", date: 2026-05-13, carrier: CFP-582, change: "MINOR bump — dispatch_mode enum 4번째 value blanket_cross_module_designlane 추가 + convergence_quality_invariant block 신설 (3 marker pattern: [COUNTERARGUMENT] / [ALTERNATIVE_PROPOSED] / [DEBATE_PURPOSE_STATEMENT]) + Touchpoint #2 carry-over schema. ADR-059 Amendment 2 동반. Epic-FIX-ESCALATION-prevention #525 close trigger." }
  - { version: "1.3", date: 2026-07-01, carrier: CFP-2534, change: "MINOR bump — trigger.lane enum 에 refactor 추가 + dispatch_mode enum 5번째 value blanket_refactor 추가 (divergence 감지 없이 자동 발동, cross_module_signal block 불요) + role_assignment optional 필드 신설 (default null = 대칭; refactor lane 은 codex=proponent/claude=opponent) + lane-specific divergence_type 에 refactor 항목 (structural 재사용). 기존 enum 값·필드 의미 변경 0 (additive strengthening, ADR-008 §결정 2). ADR-059 Amendment 3 동반. Epic CFP-2533 Story A." }
related_adrs:
  - ADR-059  # carrier (5 결정 + Amendment 1+2 — protocol 정의 + DesignReview 자동 발동 + reasoning carryover + anchor 재발 escalation + lane-agnostic + dispatch_mode enum 명시화 + DesignLane blanket + convergence_quality_invariant)
  - ADR-044  # team-spec dispatch_mode enum 확장 Amendment 1 — auto_on_divergence (별 layer)
  - ADR-052  # Codex proactive check Touchpoint #2 carry-over (Amendment 2 §결정 9)
  - ADR-008  # SemVer rule
  - ADR-010  # canonical/sibling sync 책임
related_files:
  - docs/inter-plugin-contracts/review-verdict-v4.md
  - docs/inter-plugin-contracts/fix-event-v1.md
  - docs/adr/ADR-059-debate-protocol-v1.md
  - docs/adr/ADR-044-phase-scoped-sequential-team.md
  - templates/team-spec-design-review.yaml
  - templates/story-page-structure.md
producers:
  - codeforge-review/DesignReviewPLAgent  # Story 1 scope (DesignReview)
  - codeforge-requirements/RequirementsPLAgent  # Story 2 scope (CFP-392, deferred)
  - codeforge-design/ArchitectPLAgent  # CFP-582 Wave 4 — DesignLane blanket trigger producer
  - "codeforge-pmo/PMOAgent  # refactor lane blanket_refactor producer — Story C 배선 예정 (Epic CFP-2533 Story C), Story A = 계약 표면 예약만"
consumers:
  - codeforge-design/ArchitectPLAgent  # FIX 루프 re-spawn 시 transcript 입력 수신
  - codeforge-design/ArchitectAgent  # re-run reasoning carryover 입력 수신
  - Orchestrator  # §10 FIX Ledger writer monopoly (debate_artifact_ref 채움)
  - "codeforge-design/RefactorAgent  # refactor debate transcript 수신 — Story C 배선 예정 (Epic CFP-2533 Story C), Story A = 계약 표면 예약만"
---

# debate-protocol-v1 registry

## 상위 SSOT 위치

본 파일이 canonical SSOT — wrapper-owned, lane-agnostic registry. 본 registry 는 sibling repo (codeforge-review / codeforge-design) 에서 verbatim mirror 없음 — wrapper canonical 1곳만 존재 (kind:registry 패턴, kind:contract 와 구분).

## 1. 목적

Codex ↔ Opus 두 워커가 lane 결정 지점에서 finding / judgment 불일치 (divergence) 를 산출할 때 발동하는 multi-round adversarial debate protocol 의 schema SSOT. **lane-agnostic** — 모든 lane (DesignReview / Requirements / 미래 CodeReview / SecurityTest) 에서 본 schema 재사용. lane-specific 트리거 조건은 각 lane plugin 이 별도 정의.

본 protocol carrier ADR = [ADR-059](../../archive/adr/ADR-059-debate-protocol-v1.md). 5 결정: (1) protocol 정의 (2) DesignReview 자동 발동 (3) reasoning carryover (4) anchor 재발 escalation (5) lane-agnostic registry.

### 1.1 주요 개념

| 용어 | 정의 |
|---|---|
| **divergence** | 두 워커의 동일 anchor 에 대한 finding / judgment 불일치. lane-specific 정의 (DesignReview = severity OR recommendation, Requirements = semantic) |
| **anchor** | divergence 발생 지점의 stable identifier. review-verdict-v4 finding 의 `anchor_id` field 사용 (일반적으로 `<file>:<line>` 또는 `§<section-ref>`) |
| **topic anchor** | Round 0 시점 쟁점 statement 원문. 라운드 N 입력 **최상단** prepend 강제 (U-shaped attention bias 완화 forcing function) |
| **role_lock** | Round 0 입장 fixed. 변경 시 명시적 `position_change: true` + 사유 명시 의무 |
| **POSITION_CHANGE 라벨** | role_lock 깨고 입장 전환 라운드 표시. anti-sycophancy 메커니즘 — 가짜 합의로 미분류 |
| **remaining_disagreements** | 매 라운드 출력 필수 필드. 비어있고 round < 3 = PL 이 "가짜 합의" 의심 → force_continue |
| **anchor_recurrence_count** | 같은 `anchor_id` 가 ArchitectAgent re-run 후 DesignReview 재진입 시 두 번째 debate 유발 = `>= 2` → 즉시 사용자 escalation |
| **reasoning carryover** | debate FIX 시 transcript 자체 (verdict 가 아닌) 를 ArchitectAgent re-run prompt 에 명시적 주입 |
| **dispatch_mode (team-spec layer)** | ADR-044 §결정 2 Amendment 1 — team roster level dispatch_mode (default / user_request_only / auto_on_divergence). 우선순위 `default > auto_on_divergence > user_request_only` |
| **dispatch_mode (protocol layer, v1.1 required field)** | ADR-059 Amendment 1 (CFP-533) — protocol activation level dispatch_mode (auto_on_divergence / mechanical_fast_path_inline / user_request_only). 우선순위 `auto_on_divergence > mechanical_fast_path_inline > user_request_only` |
| **mechanical_fast_path_inline** | divergence_detected: true + single-file scope + severity ≤ critical 시 inline FIX 분기. debate skip, PL inline 판정, transcript Story §9 append 면제, §10 FIX Ledger row append 의무 보존 (debate_artifact_ref = null) |
| **blanket_cross_module_designlane** | ADR-059 Amendment 2 (CFP-582) — DesignLane internal (ArchitectPL + ArchitectAgent + 6 SubAgent) 전면 적용. trigger = `touched_top_level_paths >= 2` OR `touched_lanes >= 2` (cross-module Story 정의). 우선순위 최상위. |
| **convergence_quality_invariant** | 3-tuple AND 충족 검증: `counterargument_present` AND `alternative_proposed_count >= 1` AND `debate_purpose_statement_present`. 미충족 시 `consensus_reached` 차단 + `force_continue` 강제 |
| **3 marker pattern** | debate transcript section header 의무 — `[COUNTERARGUMENT]` (Round 1+ 매 라운드 per worker) / `[ALTERNATIVE_PROPOSED]` (debate cumulative >= 1) / `[DEBATE_PURPOSE_STATEMENT]` (Round 0 only) |
| **Touchpoint #2 carry-over** | ADR-052 Amendment 4 (CFP-532) Codex proactive check 의 P0/P1 finding 을 debate Round 0 `codex_initial_position` 으로 verbatim forward. 이중 spawn 회피 |
| **blanket_refactor** | ADR-059 Amendment 3 (CFP-2534) — refactor lane (구현-리팩터링) 전면 적용. trigger = 리팩터링 활동 자체 = **divergence 감지 없이 무조건 발동** (cross_module_signal block 불요). 발동 방식(activation-manner)만 인코딩 — 발동 주기(cadence)는 Story C 배선(schema 미인코딩). 우선순위 = blanket 군 (ADR-059 §결정 7 SSOT). 두 blanket(blanket_cross_module_designlane / blanket_refactor)은 lane-disjoint(설계 lane vs refactor lane)라 무순서이나 total-order 는 결정론 표기 규약으로 고정. |
| **role_assignment** | ADR-059 Amendment 3 (CFP-2534) — **초기 편(direction) 배정** optional 필드. `{claude: opponent, codex: proponent} \| null` (default null = 대칭 = 기존 동작). role_lock 과 **orthogonal**: role_lock = 입장(position) 고정 / role_assignment = 찬성·반대 편(direction) 배정. refactor lane 은 codex=proponent(발굴)/claude=opponent(필요성 게이트). |
| **refactor lane (구현-리팩터링)** | ADR-059 Amendment 3 (CFP-2534) — 실제 머지된 코드를 대상으로 중복·재사용 리팩터링 지점을 Codex(찬성)↔Claude(반대) 적대 토론으로 도출하는 소비 lane. divergence_type = `structural` 재사용 (per-lane keying 으로 의미 확정). producer/consumer 실배선 = Story C. |

## 2. Schema

### 2.1 Trigger schema

```yaml
trigger:
  lane: design-review | design-lane | requirements | code-review | security-test | refactor
  detected_by: <PLAgent name — 예: DesignReviewPLAgent | ArchitectPLAgent>
  divergence_type: severity | recommendation | semantic | structural  # structural = blanket trigger (CFP-582)
  role_assignment:  # optional, default null (대칭 = 기존 동작). v1.3 — CFP-2534 / ADR-059 Amendment 3
    claude: proponent | opponent | null
    codex: proponent | opponent | null
    # refactor lane: {claude: opponent, codex: proponent}. role_lock(입장 고정)과 orthogonal — 초기 편(direction) 배정만.
  dispatch_mode: blanket_cross_module_designlane | blanket_refactor | auto_on_divergence | mechanical_fast_path_inline | user_request_only  # REQUIRED (v1.3 — blanket_refactor: CFP-2534 / ADR-059 Amendment 3; blanket_refactor = divergence 감지 없이 자동 발동, cadence 미인코딩(Story C))
  cross_module_signal:  # blanket_cross_module_designlane 시 required, v1.2
    touched_top_level_paths_count: int
    touched_lanes_count: int
    touched_lanes_list: [string]  # 예: ["design", "develop", "review"]
  anchor_id: <stable identifier — review-verdict-v4 finding.anchor_id>
  anchor_text: <쟁점 원문 — 매 라운드 입력 최상단에 강제 포함>
  detected_at: <ISO8601 UTC Z-suffix>
  claude_initial_position:
    statement: <원본 finding/judgment 추출>
    rationale: <근거>
    severity: P0 | P1 | P2 | null  # lane 에 따라 nullable
    recommendation: FIX | FIX_DISCRETIONARY | PASS | null
  codex_initial_position:
    statement: <원본 finding/judgment 추출>
    rationale: <근거>
    severity: P0 | P1 | P2 | null
    recommendation: FIX | FIX_DISCRETIONARY | PASS | null
    carry_over_source: <"touchpoint_2_architect_section_3" | "adhoc_spawn" | null — v1.2, blanket trigger 시 required>
```

**lane-specific divergence_type 정의**:

- DesignReview: `severity` OR `recommendation` — review-verdict-v4 `findings[]` 동일 `anchor_id`. ADR-059 §결정 2
- DesignLane (CFP-582 blanket): `structural` — cross-module Story 의 ArchitectPLAgent / ArchitectAgent / SubAgent 간 결정 영역. divergence detection 없이 자동 발동 (`touched_top_level_paths >= 2` OR `touched_lanes >= 2`).
- Requirements (Story 2 / CFP-392): `semantic` — RequirementsPL synthesis vs Codex proactive check 간 의미 차이
- Refactor (CFP-2534 blanket): `structural` **재사용** — 실제 머지 코드의 중복·재사용 divergence, `<file>:<line>` anchor. divergence detection 없이 자동 발동 (`blanket_refactor`). per-lane keying 으로 DesignLane structural 과 의미 구분 (DesignLane = 설계 산출물 structural / Refactor = 실코드 중복·재사용 structural). role_assignment = {codex: proponent, claude: opponent}. producer/consumer 실배선 = Story C.
- CodeReview / SecurityTest: deferred CFP-C

### 2.2 Round schema

```yaml
round:
  index: 0..5  # Round 0 = init, Round 1~5 = debate rounds
  emitted_at: <ISO8601 UTC>
  claude_position:
    statement: <input 텍스트>
    rationale: <근거>
    position_change: false | true
    position_change_reason: <texte — position_change true 시 의무>
    convergence_quality_markers:  # v1.2 — CFP-582 (per worker, worker writes)
      counterargument_present: bool  # Round 1+ 의무 (`[COUNTERARGUMENT]` section header)
      alternative_proposed_count: int (>=0)  # 본 라운드 `[ALTERNATIVE_PROPOSED]` section header 개수
      debate_purpose_statement_present: bool  # Round 0 의무 (`[DEBATE_PURPOSE_STATEMENT]` section header)
  codex_position:
    statement: <input 텍스트>
    rationale: <근거>
    position_change: false | true
    position_change_reason: <texte — position_change true 시 의무>
    convergence_quality_markers:  # v1.2 — CFP-582 (per worker, worker writes)
      counterargument_present: bool
      alternative_proposed_count: int (>=0)
      debate_purpose_statement_present: bool
  remaining_disagreements:
    - <쟁점 1 — 양측 미해결 항목>
    - <쟁점 2>
    # 비어있고 round < 3 시 PL 이 force_continue (adversarial prompt 재주입)
  pl_intermediate_judgment: continue | consensus_reached | force_continue
  pl_intermediate_judgment_reason: <texte>
  convergence_quality_invariant_check:  # v1.2 — CFP-582 (per round, PL writes)
    counterargument_present_both_workers: bool
    alternative_proposed_cumulative_count: int (>=0)  # debate cumulative 누적
    debate_purpose_statement_present_round_0_inherited: bool
    invariant_satisfied: bool  # 3-tuple AND 결과 — consensus_reached 발화 전 PL 가 검증
```

### 2.3 Termination schema

```yaml
termination:
  method: pl_llm_judgment | user_arbitration | anchor_recurrence
  terminated_at: <ISO8601 UTC>
  reason: <texte>
  final_verdict: PASS | FIX | FIX_DISCRETIONARY | ESCALATE
  dialog_rounds_count: 3..5  # min 3 / max 5 정합
  anchor_recurrence_count: 0..N
  pl_synthesis: <texte — PL 의 최종 verdict 정당화>
  convergence_quality_invariant_final:  # v1.2 — CFP-582 (PL writes)
    counterargument_present_all_rounds_both_workers: bool
    alternative_proposed_cumulative_count: int  # >=1 required for consensus_reached
    debate_purpose_statement_present_round_0: bool
    invariant_satisfied_at_termination: bool
    invariant_violation_action: null | "force_continue_round_N" | "verdict_downgraded_to_force_continue"
```

### 2.4 Round 0 입력 (initialization)

```yaml
round_0_input:
  anchor: <trigger.anchor_text — full text>
  claude_initial_position: <trigger.claude_initial_position 그대로>
  codex_initial_position: <trigger.codex_initial_position 그대로>
  system_prompt_appendix: |
    "Round 0 입장 유지 의무. 상대 주장의 근거가 결정적일 때만 입장 변경 허용 (position_change + reason 명시).
     remaining_disagreements 미해결 쟁점 빠짐없이 나열. 비어 있으면 가짜 합의로 간주."
  task: "Round 1 부터 반박 또는 보강 발화 시작. anchor 유지 의무. remaining_disagreements 명시 의무."
```

### 2.5 Round N 입력 (N >= 1)

```yaml
round_N_input:
  anchor: <round_0.anchor — 매 라운드 동일 verbatim, 입력 최상단 prepend 의무>
  transcript:
    - round_0: <serialized full content>
    - round_1: <serialized>
    - ...
    - round_{N-1}: <serialized>
  system_prompt_appendix: |
    "(Round 0 directive 와 동일 — verbatim 재주입)"
  pl_adversarial_prompt: <optional — force_continue 발동 시 PL 이 주입하는 반박 prompt>
  task: "Round N 입장 발화. anchor 이탈 금지. remaining_disagreements 갱신 의무. 상대 주장에 대한 명시적 반응 필수."
```

### 2.6 Output token budget 권고

매 라운드 worker 출력 권고 cap (PL 이 enforce):

- `statement`: <= 2000 token
- `rationale`: <= 3000 token
- 총 ~5000 token / round / worker

5 라운드 × 2 worker × 5K = 50K token (PL Opus 200K context 한도 내 안전). 초과 시 PL 이 worker 에게 condensation 요청 (1회 한정) 후 invalid 처리.

## 3. 항목

### 3.1 Anti-sycophancy 메커니즘

매 라운드 system prompt 에 강제 포함되는 directive (worker 별):

> "당신의 Round 0 입장을 유지하라. 상대 주장의 근거가 결정적일 때만 입장 변경 허용. 입장 변경 시 출력에 `position_change: true` + `position_change_reason` (텍스트 사유) 명시 의무. `remaining_disagreements` 배열은 의심 가는 미해결 쟁점을 빠짐없이 나열하라. 비어 있으면 가짜 합의로 간주된다."

**PL 검증 책무**:

1. 매 라운드 출력에서 `remaining_disagreements` 필드 존재 검증. 누락 시 invalid 처리 + 재발화 요청 (1회 한정 — EC-3)
2. `position_change: true` 인데 `position_change_reason` 누락 시 invalid 처리 + 재발화 요청 (1회 한정 — EC-4)
3. `remaining_disagreements` 비어있고 `dialog_rounds_count < 3` 시 `force_continue` + adversarial prompt 재주입 (EC-2)
4. 양측 동시 `position_change: true` 발화 시 가짜 합의 의심 — 결정적 근거 검증 후 force_continue (EC-5)
5. **3 marker pattern 검증 (v1.2 — CFP-582 / ADR-059 Amendment 2)**: 매 라운드 worker 출력의 `convergence_quality_markers` 검증. `counterargument_present == false` (Round 1+) 또는 `debate_purpose_statement_present == false` (Round 0) 시 invalid 처리 + 재발화 요청 (1회 한정 — EC-6) + 두 번째 부재 시 `force_continue` + adversarial prompt 재주입 ("debate 의 본질은 반론·대안 — 합의 도달 자체가 목적이 아니다").
6. **convergence_quality_invariant gate (v1.2 — CFP-582 / ADR-059 Amendment 2)**: PL 이 `consensus_reached` verdict 발화 전 3-tuple AND 충족 검증: `counterargument_present_all_rounds_both_workers == true` AND `alternative_proposed_cumulative_count >= 1` AND `debate_purpose_statement_present_round_0 == true`. 미충족 시 `consensus_reached` 차단 + `force_continue` 강제 + Story §9 transcript 에 `[convergence_invariant_violation]` marker append.

### 3.2 영속화 (Story §9 inline append)

- **위치**: Story §9 (Quality gate history) inline append. 독립 파일 신설 금지 — `doc-locations.yaml` 신규 doc_type 추가 불필요
- **Section header format**: `### Debate transcript: <anchor_id>` (Story §9 하위)
- **Section schema**: trigger / rounds / termination 3 block — 본 registry §2 (Schema) 정합
- **lint**: `check-doc-section-schema.sh` 가 Story §9 의 `### Debate transcript: ` prefix sub-section 인식 + 내부 schema 검증 (Phase 2 PR scope)
- **codeforge family Story (ADR-013 dogfood-out 적용)**: §9 = `<internal-docs-clone>/<plugin-folder>/stories/<KEY>.md §9`
- **consumer Story**: §9 = `docs/stories/<KEY>.md §9` (consumer repo 직접)

### 3.3 FIX 통합 (fix-event-v1 1.1 정합)

debate verdict = `FIX` 또는 `FIX_DISCRETIONARY` 시 다음 흐름 강제 (ADR-059 §결정 3 SSOT):

1. **transcript Story §9 append** — `### Debate transcript: <anchor_id>` sub-section (writer = DesignReviewPL via Orchestrator self-write delegate, ADR-039 Amendment 정합)
2. **§10 FIX Ledger row append** — Orchestrator self-write (fix-event-v1 1.1 contract):
   - `debate_artifact_ref` 필드 = `#debate-transcript-<anchor_id>` (Story §9 section anchor link)
3. **ArchitectPLAgent re-spawn** — prompt 에 debate transcript 명시적 주입 (verbatim, 요약 금지)
4. **ArchitectAgent re-run instruction**:
   > "양측 입장의 reasoning trail 을 반영해 redesign 하라. transcript 의 양보 / 반박 / 미해결 disagreement 를 모두 검토 후 새 change-plan / ADR 작성."
5. DesignReview re-entry (FIX-N+1) — Story §10 FIX Ledger 카운터 정합

### 3.4 Anchor 재발 escalation (ADR-059 §결정 4 SSOT)

DesignReview lane 진입 직전 PL 이 Story §9 scan 으로 anchor_id 재발 검출:

- `count(Story §9 의 "### Debate transcript: <anchor_id>" sub-section)` 산출
- `>= 2` 시 → debate Round 진입 없이 즉시 `termination.method = anchor_recurrence` + `AskUserQuestion` 발화
- PL 이 정리한 packet:
  - (a) topic_anchor 원문
  - (b) 이전 debate 최종 verdict + 양측 마지막 라운드 입장
  - (c) ArchitectAgent 가 적용한 redesign 요지
  - (d) 재발 finding 의 새 context (의미적으로 같은 쟁점인지 PL 판단 근거)
  - (e) 사용자 중재 옵션 제시

**EC-7 (entry §5.4 정합)**: ArchitectAgent 수정 후 동일 `anchor_id` 가 발화되었으나 **명확히 다른 쟁점** 으로 PL 판단 시 `anchor_recurrence_count` 증가 안 함. 모호 시 사용자 escalation 우선 (안전 방향).

### 3.5 AskUserQuestion escalation (max 5 미합의 시)

`dialog_rounds_count == 5` 도달 + 미합의 시 PL 이 다음 packet 으로 `AskUserQuestion` 발화:

```yaml
escalation_packet:
  topic_anchor: <full text>
  claude_last_position: <Round 5 발화>
  codex_last_position: <Round 5 발화>
  unresolved_disagreements: [<list>]
  trade_off_analysis: <PL 의 trade-off 정리>
  pl_tentative_recommendation: <optional — PL 의 잠정 권고>
  user_options:
    - "Claude 입장 채택 (FIX 또는 PASS)"
    - "Codex 입장 채택 (FIX 또는 PASS)"
    - "절충안 — PL 의 잠정 권고 채택"
    - "Story scope 재정의 — Requirements lane 회귀"
```

사용자 dialog 응답이 `termination.final_verdict` 결정.

### 3.6 env=0 / env=1 동작 동등성

| 항목 | env=1 (agent teams 활성) | env=0 (default subagent context) |
|---|---|---|
| Round dispatch | `SendMessage(to=worker, body=round_N_input)` continuous dialog | Orchestrator round-trip — 매 라운드 worker subagent one-shot spawn (transcript 누적 입력 첨부) |
| Round counter | platform-tracked + review-verdict-v4 `worker_dialog_rounds` 정합 | PL 자체 관리 + review-verdict-v4 `worker_dialog_rounds` 정합 |
| Topic anchor prepend | SendMessage body 안 prepend | Agent tool prompt 안 prepend |
| Transcript carryover | SendMessage body 안 누적 | Agent tool prompt 안 누적 |
| 토큰 cost | round 간 cache hit 가능 (5 min TTL) | 매 라운드 cold start (cache 미적용) — 비용 증가 |
| PL 검증 책무 | PL teammate 가 매 round 출력 수신 후 검증 | PL Orchestrator round-trip 안에서 검증 |

양쪽 동일 protocol schema 준수. env=0 fallback 의 토큰 비용 증가는 사용자 인식 의무 (consumer-guide §1f).

### 3.7 ADR-013 dogfood-out 정책 정합

codeforge family Story 의 debate transcript 위치 = `<internal-docs-clone>/<plugin-folder>/stories/<KEY>.md §9`. Consumer Story = `docs/stories/<KEY>.md §9`. 두 위치는 동일 schema 적용. `check-doc-section-schema.sh` 가 두 path 모두 lint scope 포함 (Phase 2 PR).

### 3.8 Producer / Consumer 책임 명시

- **Producer**:
  - `DesignReviewPLAgent` (Story 1 scope) — DesignReview lane 진입 시 divergence detection + Round dispatch + Termination 결정. transcript Story §9 write (Orchestrator self-write delegate)
  - `RequirementsPLAgent` (Story 2 scope, CFP-392) — Requirements lane 진입 시 동일 책무
- **Consumer**:
  - `ArchitectPLAgent` — FIX verdict 수신 시 ArchitectAgent re-spawn 입력 packet 안에 transcript 명시 주입
  - `ArchitectAgent` — re-run instruction 정합 (reasoning carryover)
  - `Orchestrator` — §10 FIX Ledger writer monopoly + `debate_artifact_ref` 필드 채움 + AskUserQuestion escalation 발화

### 3.9 dispatch_mode 결정 로직 (v1.1 — CFP-533 / ADR-059 Amendment 1)

`dispatch_mode` field 는 v1.1 부터 required. trigger schema 작성 시점 PL 이 다음 알고리즘으로 결정:

```
1. divergence detection 알고리즘 수행 (review-pl-base.md §3.0)
2. divergence_detected = false:
   → trigger schema 작성 안 함 (debate 미발동)
3. divergence_detected = true:
   3a. consumer / user ad-hoc explicit request 감지 시:
       → dispatch_mode = "user_request_only"
   3b. (a) single-file scope + (b) severity ≤ P1 모두 충족 시:
       → dispatch_mode = "mechanical_fast_path_inline"
       → debate Round 0 dispatch 안 함, PL inline 판정
       → transcript Story §9 append 면제 (debate 미발동)
       → §10 FIX Ledger row append 의무 보존 (debate_artifact_ref = null)
   3c. 미충족 (multi-file scope 또는 P0 critical):
       → dispatch_mode = "auto_on_divergence" (표준 multi-round debate)
       → §결정 1-5 표준 흐름 발효
```

**우선순위 룰**: `auto_on_divergence > mechanical_fast_path_inline > user_request_only`. 두 mode 동시 활성 가능 영역 (예: explicit user request + auto-divergence detection) 시 더 강한 쪽 effective.

**`mechanical_fast_path_inline` 조건 검증**:

- (a) single-file scope: `divergence anchor_id[*]` 추출 → file path 1개만 포함 (multi-file divergence 는 cross-file 영향 = 표준 debate 의무)
- (b) severity ≤ critical: `severity in {P1, P2}` (P0 critical 영역은 표준 debate 의무 — high-stake decision 영역)

조건 모호 시 fallback (auto_on_divergence) — 안전 방향 정합. PL inline judgment 의 audit anchor = Story §10 FIX Ledger row 의 resolution column (root_cause + fix verbose 기록 의무).

**ADR cross-ref**:

- ADR-059 §결정 6 (Amendment 1, CFP-533) — protocol-level dispatch_mode SSOT
- ADR-044 §결정 2 Amendment 1 — team-spec layer dispatch_mode (별 layer)
- ADR-064 active amendment — governance 강화 ratchet 방향 정합

## 4. 변경 규칙

### 4.1 SemVer 정책

- **MAJOR**: trigger schema / round schema / termination schema 의미 변경 (예: divergence_type enum 의 기존 값 의미 변경, dialog_rounds_count cap 변경)
- **MINOR**: optional 필드 추가 (예: `pl_intermediate_judgment` 의 새 enum value, rolling_summary 모드 도입). optional → required 필드 전환 (예: v1.1 dispatch_mode required 전환 — additive strengthening, ADR-008 §결정 2 정합)
- **PATCH**: 문서 보강, comment 추가

### 4.2 Sibling sync 정책

본 registry 는 `kind: registry` (wrapper-owned, lane-agnostic) — `kind: contract` 와 달리 lane plugin sibling mirror 없음. wrapper canonical 1곳만 존재. 따라서 sibling sync PR (ADR-010) 의무 없음. canonical 만 갱신.

### 4.3 관련

- [ADR-059](../../archive/adr/ADR-059-debate-protocol-v1.md) — carrier (5 결정)
- [ADR-044](../../archive/adr/ADR-044-phase-scoped-sequential-team.md) — dispatch_mode Amendment 1 (auto_on_divergence)
- [review-verdict-v4](review-verdict-v4.md) — `findings[].anchor_id` divergence surface + `worker_dialog_rounds` 측정 source
- [fix-event-v1 1.1](fix-event-v1.md) — `debate_artifact_ref` optional 필드 MINOR bump
- [story-page-structure.md](../../templates/story-page-structure.md) — Story §9 schema

