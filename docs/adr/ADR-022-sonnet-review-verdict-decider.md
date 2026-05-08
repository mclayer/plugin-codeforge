---
adr_number: 22
title: Sonnet Decider — Comprehensive Policy (Triggers + Consumer Scope + Review-Verdict)
status: Deprecated
deprecated_by: CFP-134
deprecated_date: 2026-05-08
deprecated_reason: "Codex review / Sonnet decider 가 codeforge 1st-class component 가 아닌 사용자 ad-hoc 도구로 framing 정정 (CFP-134 Epic). 본 정책 (5 trigger 자동 발동) 무효 — 후속 ADR 가 명시적 'Supersedes' 안 함, 'codeforge family 결정 deprecate' 가 정확."
category: Team & Process
date: 2026-05-02
related_files:
  - CLAUDE.md
  - docs/inter-plugin-contracts/review-verdict-v3.md
  - docs/inter-plugin-contracts/decision-packet-v2.md
  - templates/story-page-structure.md
  - docs/consumer-guide.md
  - docs/orchestrator-playbook.md
  - docs/adr/ADR-019-sonnet-decider-auto-proceed.md
  - docs/adr/ADR-018-gemini-decider-auto-proceed.md
  - docs/adr/ADR-001-review-agent-unification.md
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md
  - docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md
related_stories:
  - CFP-61
---

# ADR-022: Sonnet Decider — Comprehensive Policy

## 상태

**DEPRECATED 2026-05-08 (CFP-134 Epic, ADR-035)**: Codex review / Sonnet decider 가 codeforge 1st-class component 가 아니라 사용자 ad-hoc 도구로 정정. 본 ADR 의 5 trigger 자동 발동 + 5-step Orchestrator algorithm 무효. 사용자 explicit request 시에만 ad-hoc invoke. 본 ADR body history record 보존 (Supersession 미사용 — 후속 ADR 가 명시적 'Supersedes' 안 함, 'codeforge family 결정 deprecate' 가 정확). Architecture decision SSOT 는 ADR-035 (Epic CFP-134).

Accepted (2026-05-02) — CFP-61 carrier. **Supersedes ADR-019** (1-day succession).

**Supersession map**: ADR-018 → ADR-019 → ADR-022 (CFP-58 / CFP-59 / CFP-61 iterative refinement under explicit user directive). 본 ADR-022 = active SSOT — ADR-018 + ADR-019 = historical record.

## 컨텍스트

CFP-59 (ADR-019, 2026-05-02 same-day) introduced Sonnet (`claude-sonnet-4-6`) as final decider for 4 substantive triggers (option-formulation / FIX root-cause / Codex ambiguity / brainstorming-constraint), via `Agent` tool with `model: sonnet`. ADR-019 is silent on consumer scope; only `feedback_codex_review_auto_proceed.md` memory restricts auto-proceed to "codeforge plugin family only".

**User directive (2026-05-02, post-CFP-59 merge)**:

> "consumer도 대상이 되어야 하고 리뷰 등 정해진 모든 과정 후에 sonnet이 이를 바탕으로 종합해서 결정하는 프로세스가 진행되는 것이다."

Two policy expansions:

1. **Consumer scope**: ADR-019 active in consumer projects too (currently scoped to codeforge-family via memory only).
2. **Review-verdict trigger 5**: every review iteration (DesignReview / CodeReview / SecurityTest) → Sonnet final pick (PASS/FIX), not just PL judgment.

## 결정

### 결정 1 — Authority hierarchy

ADR-019 §결정 1 그대로:

| Role | Actor | Vendor |
|---|---|---|
| Implementer | Claude (Opus 4.7, controller 본세션) | Anthropic |
| Auditor | Codex (gpt-5.5 high) | OpenAI |
| **Decider** | **Claude Sonnet (`claude-sonnet-4-6`)** | Anthropic |
| Override | User (escalation whitelist 만) | — |

### 결정 2 — Stop point coverage (NEW trigger 5 추가)

**자동 trigger 5 종** (decider 발화):

- (a) substantive 다중 선택지
- (b) FIX root-cause 불일치
- (c) Codex ambiguity — **scope narrowing (CFP-61)**: option-formulation 단계 한정 (substantive choice 의 options proposal 시 Codex 가 옵션 결정 못하는 ambiguity). review-verdict 흐름의 worker (CodexReviewAgent) finding severity ambiguity 는 본 trigger 미발화 — `packet_requires_review_reopen` 으로 routing 처리 (§결정 3 step 3). ADR-019 §결정 2 의 "Codex ambiguity" 광의 정의 → ADR-022 narrowing.
- (d-constraint) 제약 surfacing Q
- **(e) review-verdict — NEW**: 매 review iteration (DesignReview / CodeReview / SecurityTest) 종료 후 Sonnet final pick (PASS/FIX). worker ambiguity 는 본 trigger 의 packet 흐름 내에서 reopen mechanism 으로 처리 (별도 trigger c packet 미발화).

**User escalation whitelist 5 종** (그대로):

- (d-intent) 사용자 의도 추정
- (e2) lane FIX max 3 (review trigger 와 별개 카테고리, naming clash 회피 위해 e2)
- 운영 prerequisite 실패 (Anthropic billing / Agent tool 가용성)
- destructive action
- denylist (보안 sensitive)

### 결정 3 — Decision flow per trigger

**기존 4 trigger (a/b/c/d-constraint)** = ADR-019 §결정 3 7-step 그대로 (Claude options → Codex options → cross-review → packet → Sonnet → pick handling → logging).

**신규 trigger 5 (review-verdict)** = 5-step algorithm:

```
1. ReviewPL spawn → workers (Claude+Codex parallel) → dedup → review-verdict-v3 packet (no writes)
   ├── findings + pl_recommendation 작성
   ├── decision_state = pending_sonnet (or blocked_packet_incomplete if pl_recommendation=ESCALATE_PACKET_INCOMPLETE)
   └── return to Orchestrator
2. Orchestrator: decision-packet-v2.1 작성 (trigger: review-verdict, review_lane_context populated, findings_hash verified)
3. Orchestrator: Agent tool with model:sonnet 호출 → 응답 parse (§결정 5.3 Sonnet 응답 schema)
   ├── decision=PASS|FIX → sonnet_final_status 채움, decision_state=decided, step 4 로 진행
   ├── decision=PACKET_REQUIRES_REVIEW_REOPEN → decision_state=review_reopen_requested, ReviewPL 재 spawn (1 회 한도 per (story_key,lane,iteration))
   └── timeout/malformed (Codex P1 #4) → decision_state=decider_timeout
       └── Story §9 / §10 append 차단. §12 row append (decider_pick=<none>, audit_result=user-escalation, attempts[].outcome=timeout|malformed)
4. Orchestrator self-write (decision_state=decided 일 때만):
   ├── Story §9 append (lane iteration result) — append-only, never rolled back
   ├── GitHub Issue/PR comment ([<lane>-리뷰] / [보안-테스트] prefix) via mcp__github__add_issue_comment
   ├── PASS 시: gate:*-pass label + phase:* 다음 단계 전환 via mcp__github__issue_write
   └── Story §12 Sonnet Decision Log row append
   
   **Partial-write policy (Codex P1 #5)**: 각 sub-step 별 idempotent retry (initial + 2 retry = 3 회 한도, Codex Round 2 gap fix). 실패 시 `writes_completed.<field>=false` + `write_errors[]` populate, decision_state=write_partial. **any required write 가 retry 한도 후에도 false 잔존 시 user escalation** (모든 required 가 아닌 1 건이라도 잔존 시 — Codex Round 2 gap fix wording 명확화). Story §9 + §12 는 append-only — 이미 append 된 내용 rollback 안 함. 외부 복구 후 다음 spawn 사이클에 missing write 재시도 가능 (write_partial → write_complete 전환).
5. FIX 시 (sonnet_final_status=FIX):
   ├── Story §10 FIX Ledger append (decider: claude_sonnet, override marker if pl_recommendation != sonnet_final_status)
   ├── fix-ledger-sync.yml Action mirror (auto)
   ├── DeveloperPL + ArchitectPL parallel diagnosis spawn (CFP-19 R4)
   
   **Spawn-failure policy (Codex P1 #6)**: §10 append 성공 + diagnosis spawn 실패 시 — §10 row 유지 (append-only), §12 append (audit_result=user-escalation, spawn_status=failed), 1 회 retry → second failure = user escalation. spawn 성공할 때까지 §10 row 는 "open FIX with no diagnosis" 상태로 visible.
```

### 결정 4 — Decider 모델 invariant (보강)

ADR-019 §결정 4 그대로 유지:

- decider ≠ option-generator (Claude Opus / Codex)
- decider ≠ cross-reviewer (Claude+Codex 의 cross_review)
- decider ≠ sanity-auditor (Codex sanity audit gate)
- 동일 vendor 다른 tier 허용
- Enforcement = exact model-ID + role level

**신규 sub-clause (trigger 5 한정)**:

> "For trigger 5 `review-verdict`, Claude Sonnet is the final decider over ReviewPL-provided review evidence. Sonnet does not become a review worker or ReviewPL: it must not perform primary file inspection, generate the review finding set, alter severity normalization, or replace ReviewPL dedup. Its authority is limited to selecting the final gate outcome (`PASS` | `FIX`) from the packet evidence."

**Edge case**:

> "If Sonnet reasoning identifies a potential missing issue in the packet, that item is not a review finding until routed back to ReviewPL via `packet_requires_review_reopen` enum value. Orchestrator must not publish Sonnet reasoning content as a review finding directly."

**Permitted action**: Sonnet may cite packet insufficiency or evidence inconsistency and return `FIX` or `packet_requires_review_reopen`; both route through Orchestrator-owned retry/escalation flow. Sonnet does not write findings.

**Trigger 5 contract-fixed options (Codex P2 #1)**: For trigger 5 review-verdict, the option set is contract-fixed as exactly `PASS` and `FIX` (binary). Sonnet must not add, remove, rename, or synthesize options. `PACKET_REQUIRES_REVIEW_REOPEN` is a control-plane signal (route back to ReviewPL via `packet_requires_review_reopen` outcome), not a third option. This invariant guarantees `decider ≠ option-generator` even though Sonnet selects from a 2-element option set — the selection is bounded by the contract, not generated by Sonnet.

### 결정 5 — Schema versioning

#### 결정 5.1 — review-verdict v3 (BREAKING)

Canonical at `mclayer/plugin-codeforge-review/docs/inter-plugin-contracts/review-verdict-v3.md`.

```yaml
review_verdict:
  contract_version: "3.0"            # BREAKING marker
  lane: design | code | security
  story_key: <STORY_KEY>
  iteration: <int>
  
  findings:                          # v2 그대로 (배열, severity/category/file/evidence/suggestion)
    - severity: P0 | P1 | P2
      category: <packet category_enum 중 하나>
      file: <path>
      line: <int>
      evidence: <markdown>
      suggestion: <markdown>
  
  pl_recommendation: PASS | FIX | FIX_DISCRETIONARY | ESCALATE_PACKET_INCOMPLETE  # NEW (was status)
  
  # NEW state machine — explicit lifecycle (Codex spec audit P1 #1)
  decision_state: pending_sonnet | decided | blocked_packet_incomplete | decider_timeout | decider_suspended | review_reopen_requested | write_partial | write_complete
  
  sonnet_final_status: PASS | FIX                                                  # required only when decision_state=decided | write_partial | write_complete
  decider_decision_ref:                                                            # required only when decision_state=decided | write_partial | write_complete
    packet_id: <story_key>-<3-digit-seq>
    model: claude-sonnet-4-6
  
  write_errors:                                                                    # NEW — populated when decision_state=write_partial (Codex P1 #5)
    - step: story_section_9 | phase_comment | gate_label_attached | phase_label_transitioned | fix_ledger_append | diagnosis_spawn
      error_class: github_mcp_timeout | edit_conflict | mcp_auth_failure | other
      retry_count: <int>
  
  writes_completed:                  # 의미 재정의 — Orchestrator self-write audit (CFP-61 한정)
    story_section_9: <bool>
    phase_comment: <bool>
    gate_label_attached: <bool>
    phase_label_transitioned: <bool>
    fix_ledger_append: <bool>        # FIX 시 only
    diagnosis_spawn: <bool>          # FIX 시 only
```

**`decision_state` 필드 의미** (Codex P1 #1):

| state | 의미 | sonnet_final_status / decider_decision_ref |
|---|---|---|
| `pending_sonnet` | Orchestrator 가 packet 작성, Sonnet 호출 전 | absent |
| `blocked_packet_incomplete` | pl_recommendation=ESCALATE_PACKET_INCOMPLETE, Sonnet 호출 차단 | absent |
| `decider_timeout` | Sonnet 호출 retry 모두 timeout | absent |
| `decider_suspended` | Sonnet quota / auth / runtime denial → user authority | absent |
| `review_reopen_requested` | Sonnet 응답 = packet_requires_review_reopen, ReviewPL 재 spawn 대기 | absent |
| `decided` | Sonnet pick 완료, write 시작 전 | populated |
| `write_partial` | Sonnet pick 완료 + 일부 write 실패 (write_errors 채워짐) | populated |
| `write_complete` | 모든 required write 성공 | populated |

**`write_partial` → `write_complete` 전환 (Codex Round 2 신규 gap fix)**: user/operator 가 외부 시스템 복구 후 (예: GitHub MCP 재인증, 라벨 부착 수동) Orchestrator 가 다음 spawn 사이클에 본 verdict 의 missing write 재시도 가능. `writes_completed` 의 모든 required field = true 로 갱신되면 `decision_state=write_complete` 로 transition. retry 누적 한도 = 각 sub-step 별 3 회 (initial + 2 retry). 한도 초과 시 user escalation (decision_state=write_partial 잔존 + Story §10 / §12 에 final state mark).

**v2 → v3 변경 요약**:

| 영역 | v2 | v3 |
|---|---|---|
| `status` 필드 | PL final (PASS/FIX/FIX_DISCRETIONARY/ESCALATE) | **제거** |
| `pl_recommendation` | (없음) | NEW — PL advisory (PASS/FIX/FIX_DISCRETIONARY/ESCALATE) |
| `sonnet_final_status` | (없음) | NEW — Sonnet binary (PASS\|FIX) |
| `decider_decision_ref` | (없음) | NEW — Sonnet packet link (model 필드 포함) |
| `writes_completed` audit | PL self-write 결과 | **Orchestrator** self-write 결과 |

`ESCALATE_PACKET_INCOMPLETE` semantics (v3 한정): pre-decision escalation. Orchestrator detects 시 Sonnet 호출 차단 → user escalation. `sonnet_final_status` 미작성.

`packet_requires_review_reopen` 은 `pl_recommendation` 또는 `sonnet_final_status` 의 enum 값이 아닌 별도 escalation marker — Orchestrator 가 Sonnet 응답 parse 시 인식 + ReviewPL 재 spawn 트리거. 본 marker 는 결정 5.2 packet `decider_decision.outcome` enum 으로 표현.

#### 결정 5.2 — decision-packet v2.1 (MINOR additive)

Wrapper registry (`mclayer/plugin-codeforge/docs/inter-plugin-contracts/decision-packet-v2.md` body 갱신, version → 2.1).

**enum 확장**:

```yaml
trigger: option-formulation | fix-root-cause | codex-ambiguity | brainstorming-constraint | review-verdict  # +1
```

**신규 optional block** (trigger=review-verdict 시 required):

```yaml
review_lane_context:
  review_verdict_contract_version: "3.0"
  lane: design | code | security
  story_key: <STORY_KEY>
  iteration: <int>
  pl_recommendation: PASS | FIX | FIX_DISCRETIONARY | ESCALATE_PACKET_INCOMPLETE
  findings_hash: <sha256>                    # canonicalized findings[] hash (Codex P1 #2)
  source_packet_ref:                          # NEW — structured object (was scalar, Codex P1 #2)
    artifact_path: <internal-docs path or wrapper sibling path>
    content_sha256: <sha256 of review-verdict-v3 yaml>
    github_issue_or_pr_ref: <optional — see population rule below>
```

**`github_issue_or_pr_ref` population rule (Codex Round 2 gap fix)**: 본 field 는 review-verdict 가 GitHub Issue / PR 와 직접 binding 된 시점 (Phase 1 PR 또는 Phase 2 PR open 후 review iteration 진행 중) 에 populated. value format = `<owner>/<repo>#<number>` (예: `mclayer/plugin-codeforge#113`). PR open 전 (요구사항 / 설계 lane 진입 전) review-verdict 발화 시 absent. 향후 GitHub state 추적 (Issue close / PR merge) 시 cross-ref source 로 사용.

**Findings hash 의무 (Codex P1 #2)**: Orchestrator MUST verify `findings_hash` against canonicalized `findings[]` (deterministic JSON serialization, sort keys, no whitespace) BEFORE invoking Sonnet. Mismatch 시 packet malformed → user escalation. Orchestrator MUST persist both `findings_hash` 와 `source_packet_ref.content_sha256` in §12 packet artifact metadata.

**`attempts[].outcome` enum 갱신** (review-verdict 추가 outcome):

```yaml
attempts[].outcome: success | parse_failure | timeout | malformed | repeated_identical | user_override | decider_suspended | packet_requires_review_reopen
```

신규 `packet_requires_review_reopen` outcome: Sonnet 응답이 packet 불완전 / 재 review 필요 신호 시. Orchestrator 가 ReviewPL 재 spawn (per `(story_key, lane, iteration)` 1 회 한도 — Codex P1 #7. 두 번째 발화 시 user escalation. 다음 iteration N+1 은 자체 reopen budget 1 회 보유).

ADR-008 SemVer 정합:
- enum 값 추가 (additive) = MINOR
- optional block 추가 (additive, default absent) = MINOR
- existing v2 reader = backward compatible (모르는 trigger 값 + optional block 무시)

#### 결정 5.3 — Sonnet 응답 schema (trigger 5 한정, Codex P1 #3)

trigger 5 review-verdict Sonnet 호출 시 응답 (Agent tool with model:sonnet) 은 아래 schema 따름:

```yaml
decision: PASS | FIX | PACKET_REQUIRES_REVIEW_REOPEN
reasoning_summary: <markdown, 1-3 paragraphs>
confidence: high | medium | low
packet_gap_summary: <markdown, optional — required when decision=PACKET_REQUIRES_REVIEW_REOPEN>
```

**Mapping rules (Orchestrator parse)**:

| Sonnet response `decision` | review-verdict `sonnet_final_status` | packet `attempts[].outcome` | review-verdict `decision_state` |
|---|---|---|---|
| `PASS` | `PASS` | `success` | `decided` (then → `write_complete` or `write_partial`) |
| `FIX` | `FIX` | `success` | `decided` (then → `write_complete` or `write_partial`) |
| `PACKET_REQUIRES_REVIEW_REOPEN` | (absent) | `packet_requires_review_reopen` | `review_reopen_requested` |

**Parse failure**: response 가 위 schema 미준수 시 `attempts[].outcome=parse_failure` + 1 회 retry with explicit YAML correction prompt → second failure = `outcome=malformed` + user escalation (review-verdict `decision_state=decider_timeout` 으로 logging — timeout 카테고리에 포함).

### 결정 6 — 운영 정책

ADR-019 §결정 6 그대로 + trigger 5 추가:

- Sonnet 호출 = `Agent` tool runtime (Anthropic billing 내). 외부 auth 무관.
- 모델: `claude-sonnet-4-6` 고정.
- Cost: Phase 1 자동 cost gate 없음. Phase 2 ROI 평가에서 review-verdict 호출 빈도 (Story 평균 4-7 회) 별도 측정.
- Fallback matrix (ADR-019 §결정 6 그대로 + `packet_requires_review_reopen` 추가):

| 실패 유형 | 처리 |
|---|---|
| Sonnet API timeout / transient | 1 회 retry → 실패 시 user escalation. `attempts[].outcome = timeout` |
| Sonnet response malformed | `attempts[].outcome = parse_failure` 기록 + 1 retry → second failure = `outcome = malformed` + user escalation |
| Repeated identical Sonnet error (≥2 회 동일 packet 동일 pick 실패) | user escalation. `attempts[].outcome = repeated_identical` |
| Codex sanity audit FAIL (override case) | user escalation. `audit_result = sanity-FAIL` |
| Sonnet API quota exhausted | `attempts[].outcome = decider_suspended` + `authority_transfer.final_decider = user` + 운영 prerequisite escalation |
| Sonnet auth/runtime denial | `attempts[].outcome = decider_suspended` + 운영 prerequisite escalation |
| **packet 불완전 (Sonnet response 가 review reopen 신호)** | `attempts[].outcome = packet_requires_review_reopen` + ReviewPL 재 spawn (per `(story_key, lane, iteration)` 1 회 한도, Codex P1 #7) → 같은 tuple 의 두 번째 신호 시 user escalation. 다음 iteration N+1 은 자체 reopen budget 1 회 보유 |

### 결정 7 — Logging & Audit

#### 결정 7.1 — Story §10 FIX Ledger

trigger=review-verdict + sonnet_final_status=FIX 시 Orchestrator append:

```
| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| N    | ISO8601 | 설계-리뷰 | DesignReviewPL P0 × 2 | 설계 (decider:claude_sonnet, override:pl_recommendation=PASS sonnet_final=FIX) | Change Plan §3 재작성 | — |
```

`원인 판정` 컬럼 evidence:
- 정상 (PL≡Sonnet): `<원인>` (decider:claude_sonnet)
- Override (PL≠Sonnet): `<원인>` (decider:claude_sonnet, override: pl_recommendation=<X> sonnet_final=<Y>)

**Append-only resolution rule (Codex P2 #2)**: §10 row 는 append-only (CFP-32 monopoly). Iteration N FIX → iteration N+1 PASS 시점에 row N 이 mutate 되지 않음 (RESET 마커도 추가 안 함 — 같은 cycle 내 PASS 회복은 단순히 §9 의 다음 iteration PASS row 로 표현 + phase/gate label transition 으로 외부 visible). RESET 마커는 별도 lane 의 cascading retry 때만 사용 (예: 구현-테스트 FAIL 로 인해 구현-리뷰 RESET).

#### 결정 7.2 — Story §12 Sonnet Decision Log

trigger enum 5 종 모두 동일 row format. review-verdict trigger 행:

```
| packet_id | trigger | options_count | decider_pick | override? | audit_result | timestamp |
|-----------|---------|---------------|--------------|-----------|--------------|-----------|
| CFP-NN-NNN | review-verdict | 2 | FIX | yes (pl: PASS) | direct | ISO8601 |
```

- `options_count` = 2 (review-verdict 시, PASS|FIX 이진 선택지). Trigger 5 의 option set = contract-fixed (PASS|FIX) — Sonnet 가 추가 / 삭제 / rename / synthesize 금지 (결정 4 invariant 정합, Codex P2 #1).
- `decider_pick` = `sonnet_final_status`. blocked / timeout / suspended / reopen 케이스 = `<none>` 또는 `<blocked>` 명시 (아래 표 참조).
- `override?` = (pl_recommendation reduce binary != sonnet_final_status). FIX_DISCRETIONARY → FIX 로 reduce 시 override 아님 (PL 도 issue 인지). PASS → FIX 또는 FIX → PASS 시 override.
- `audit_result` enum 그대로 (direct / sanity-PASS / sanity-FAIL / decider-suspended / user-escalation) + 신규 `review-reopen` (packet_requires_review_reopen 발화 시)

**Failure-state §12 row format (Codex P1 #4 + P1 #8)** — decision_state ≠ decided 인 케이스:

| decision_state | options_count | decider_pick | override? | audit_result | reason 컬럼 |
|---|---|---|---|---|---|
| `blocked_packet_incomplete` | 0 | `<blocked>` | n/a | user-escalation | `pl_recommendation:ESCALATE_PACKET_INCOMPLETE` |
| `decider_timeout` | 2 | `<none>` | n/a | user-escalation | `attempts[].outcome:timeout` (또는 malformed) |
| `decider_suspended` | 2 | `<none>` | n/a | decider-suspended | `attempts[].outcome:decider_suspended` (Sonnet quota / auth) |
| `review_reopen_requested` | 2 | `<none>` | n/a | review-reopen | `attempts[].outcome:packet_requires_review_reopen` |
| `write_partial` (decided 후 write 일부 실패) | 2 | `<sonnet_final_status>` | (정상) | user-escalation | `write_errors[].step:<failed step>` |

`<blocked>` / `<none>` 은 literal placeholder string 으로 §12 row 에 기재 (machine-readable enum value).

#### 결정 7.3 — Detailed packet artifact

`<internal-docs>/<plugin-folder>/decisions/<packet_id>.yaml` (decision-packet v2.1 schema 준수, includes `review_lane_context` block when trigger=review-verdict).

#### 결정 7.4 — Audit policy

**첫 5 review-verdict packet scheduled self-audit (Codex P2 #3)** — 각 packet 별 다음 checklist 통과 의무:

- [ ] `decider_decision.model = claude-sonnet-4-6` (model-ID exact match)
- [ ] Sonnet 응답이 결정 5.3 schema 준수 (decision / reasoning_summary / confidence + PACKET_REQUIRES_REVIEW_REOPEN 시 packet_gap_summary)
- [ ] review-verdict-v3 `findings` / `pl_recommendation` / `decision_state` 모두 populated
- [ ] decision_packet-v2.1 `review_lane_context` 모든 required field populated (lane / story_key / iteration / pl_recommendation / findings_hash / source_packet_ref 3 sub-field)
- [ ] `findings_hash` verification 성공 (canonicalized findings[] hash 와 일치)
- [ ] `source_packet_ref.content_sha256` 가 review-verdict-v3 yaml 의 실제 SHA256 과 일치
- [ ] Sonnet response 가 finding 추가 시도 검출 시 `packet_requires_review_reopen` 으로 routing (Sonnet-authored finding 0 건 — Story §9 / §10 / §12 에 Sonnet 가 작성한 finding row 부재)
- [ ] Story §9 (PASS/FIX 모두) / §10 (FIX 시) / §12 (모든 trigger) write 완결 — `writes_completed` 모든 required field = true
- [ ] override marker format 준수 (decider:claude_sonnet + pl_recommendation/sonnet_final 명시 if PL≠Sonnet)
- [ ] reopen budget enforcement — 같은 (story_key, lane, iteration) tuple 의 reopen 발화 ≤ 1
- [ ] 본 packet artifact (`<internal-docs>/<plugin-folder>/decisions/<packet_id>.yaml`) 가 decision-packet-v2.1 schema 정확히 준수

위 11 checklist 중 1 건이라도 fail 시 user escalation. 첫 5 packet 모두 통과 후 = failure-driven audit only (schema 위반 / model-ID 불일치 / write 실패 등 trigger).

### 결정 8 — Phase boundary

- **Phase 1 = doc-only** — ADR-022 maintenance only. agent / skill / 코드 추가 없음. review-verdict trigger Sonnet 호출 = controller (Opus, top-level Claude session) runtime tool call (`Agent` tool with `model: sonnet`).
- **Phase 2 = ROI 평가 + instrumentation** — 30+ packet (4 기존 trigger + 5 review-verdict 합산) 운영 후 별도 CFP. consumer enforcement hook / refusal logic / runtime validation 도입 여부 결정. 토큰 비용 분석 (review-verdict 호출 빈도 Story 평균 4-7 회 × Sonnet call cost).
- **Phase 1 → Phase 2 transition** = 사용자 명시 승인 + 30+ packet + cost report.

### 결정 9 — Suspend / reactivation

ADR-019 §결정 9 그대로 + review-verdict trigger 포함:

- 사용자 explicit suspension ("잠깐 끄자" / "Sonnet decider 정지") → session/Story 단위 일시 중단. review-verdict trigger 발화 시 PL 1차 판단 (pl_recommendation) 으로 임시 proceed.
- Suspend 중 review-verdict 발화 시 → packet 작성 + PL recommendation 그대로 사용 + Story §10/§12 에 `decider_suspended` mark.
- Reactivate 후 미결정 packet sequential 재처리.

### 결정 10 — Migration / transition rules

- **review-verdict v2 → v3 hard cutover** — ADR-022 acceptance 후 신규 review-verdict 모두 v3. v2 Archived (status=Archived, body frozen — decision-packet v1 → v2 precedent 동일).
- **In-flight v2 verdict** (acceptance 전 생성) — v2 schema 그대로 완료. ADR-022 acceptance 후 신규 verdict 모두 v3 강제.
- **decision-packet v2 → v2.1 in-place minor bump** — schema body 갱신, archive 안 함 (additive minor 라 v2 reader backward-compat).

### 결정 11 — Consumer scope (NEW)

- ADR-022 § 적용 범위 = **codeforge-family + consumer**.
- consumer-guide.md 신규 §"Sonnet Decider 정책" 섹션 — 사용자가 consumer Orchestrator 에 명시 directive 발화 의무 (Phase 1 trust model).
- Plugin CLAUDE.md 의 "Sonnet Decider" 섹션이 consumer Orchestrator session 의 정책 source — consumer 가 plugin install 시 자동 받음.
- Phase 1 enforcement = trust model:
  - Plugin CLAUDE.md doc 만으로 정책 정의
  - Hook / refusal logic / runtime validation 없음
  - 사용자 directive (consumer 측 사용자) 가 reactivate 의무
- Phase 2 enforcement = ROI-driven instrumentation (30+ packet 후 평가).

**Consumer integration count UNVERIFIED**: 본 spec 작성 시점 review-verdict v2 schema 의존 consumer 수 미확인. Phase 1 plan author 의무로 verify (mctrader-hub 6 repo + 기타 dogfood-out consumer). 결과는 Plan 문서 또는 Story §11 에 기록.

## 검토한 대안

### 대안 A — ADR-019 Amendment 2

거부 사유:
- magnitude (consumer scope + review trigger + schema v3) 가 ADR-019 §대안 A precedent 거부 logic 동일.
- ADR-019 title "Sonnet Decider Auto-Proceed Policy" 가 review-verdict 까지 cover 시 title-content drift.

### 대안 B — ADR-020 신설 (ADR-019 active 유지, trigger 5 별도)

거부 사유:
- ADR-019 ↔ ADR-020 cross-ref 의무 + 사용자 정책 SSOT 분산.
- 사용자 explicit choice (γ) supersede.

### 대안 C — ADR-022 supersede (본 ADR — 채택)

채택 사유:
- 사용자 directive (γ) 정합.
- Single active ADR for Sonnet decider 정책.
- supersession map mitigation 으로 history noise 처리.

(KEY allocation: CFP-60 = cross-repo Epic carrier, ADR-020 + ADR-021 = CFP-60 carriers — 본 작업 = CFP-61 / ADR-022 numbering gap 정상.)

## 결과

긍정:
- 사용자 stop 빈도 절감 (review-verdict 까지 자동 결정).
- review-verdict synthesis ownership ≠ final gate write authority — clean separation.
- decision-packet v2.1 MINOR additive — backward compat.
- consumer scope explicit — Phase 1 trust model + Phase 2 ROI-driven instrumentation.

부정:
- ADR-019 1-day supersession — history noisy. mitigation = supersession map.
- review-verdict v3 BREAKING — consumer integration 영향 (UNVERIFIED, Phase 1 author 의무).
- Sonnet 호출 빈도 ↑ (review iteration 평균 4-7 회/Story) — Phase 2 ROI 평가에서 측정.
- Orchestrator write 책임 ↑ — single point. 단 Orchestrator 가 이미 §10 / general docs/** / packet artifact monopoly 보유로 일관성 ↑.

## ADR 정합성

- ADR-019 — Superseded by ADR-022 (별도 supersession PR 의무 — Task 18).
- ADR-018 — Superseded by ADR-019, historical record.
- ADR-001 — review unification scope refinement only (review-verdict 영역의 final gate write authority 만 Orchestrator 로 transfer, worker dispatch / dedup 그대로 PL).
- ADR-008 — review-verdict v2 → v3 BREAKING + decision-packet v2 → v2.1 MINOR (SemVer 정합).
- ADR-010 — sibling sync 의무 (PR 1 canonical → PR 2 wrapper sibling).
- ADR-013 — dogfood-out (Phase 1A internal-docs first).

## 관련 파일

- `CLAUDE.md`
- `docs/inter-plugin-contracts/review-verdict-v3.md`
- `docs/inter-plugin-contracts/decision-packet-v2.md`
- `templates/story-page-structure.md`
- `docs/consumer-guide.md`
- `docs/orchestrator-playbook.md`
- `docs/adr/ADR-019-sonnet-decider-auto-proceed.md`
- `docs/adr/ADR-018-gemini-decider-auto-proceed.md`
- `docs/adr/ADR-001-review-agent-unification.md`
- `docs/adr/ADR-008-inter-plugin-contract-versioning.md`
- `docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md`
