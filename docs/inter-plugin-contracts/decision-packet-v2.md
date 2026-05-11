---
kind: registry
registry: decision-packet
version: "2.1"
status: Deprecated
deprecated_by: CFP-134
deprecated_date: 2026-05-08
deprecated_reason: "ADR-022 deprecate 의무 동반 — Sonnet decider 5-step packet schema 무효 (codeforge 자동 invoke 안 함). 사용자 ad-hoc Sonnet 호출 시 본 schema 비-의무 (사용자 prompt 자유 형식)."
supersedes: docs/inter-plugin-contracts/decision-packet-v1.md
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/decision-packet-v2.md
date: 2026-05-08
authors:
  - Claude (CFP-59 author — spec § 2.6 codification)
  - Codex (gpt-5.5 high) — Round 1 spec audit
  - User (mccho) — directive 2026-05-02 (Gemini 제거, Sonnet decider)
  - CFP-135 (2026-05-08) — Deprecated annotation
related_adrs:
  - ADR-022 (carrier — CFP-61 Sonnet decider comprehensive policy) [Deprecated 2026-05-08, CFP-134]
  - ADR-035 (codeforge agent teams Epic — D1 ADR-022 deprecate)
  - ADR-019 (superseded by ADR-022 — CFP-59 Sonnet decider auto-proceed)
  - ADR-018 (superseded — CFP-57 + Amendment 1 CFP-58)
  - ADR-008 (parent — versioning rule, v1 → v2 MAJOR bump per breaking change SemVer 룰)
related_files:
  - CLAUDE.md
  - templates/story-page-structure.md
---

> **DEPRECATED (2026-05-08, CFP-134 / ADR-035)**: ADR-022 가 Deprecated 처리되어 본 decision-packet v2.1 schema 의 5-step Sonnet decider invocation 영역 (trigger enum / `review_lane_context` block / `decider_decision` / `attempts[]` / `audit_result` 등) 자동 발동 무효. codeforge 가 자동 invoke 안 함. 사용자 ad-hoc Sonnet 호출 시 본 schema 의무 아님 — 사용자 prompt 자유 형식 가능. v3 MAJOR bump 후속 deferred (CFP-137 또는 별도 CFP carrier — 정식 schema 제거 / 신규 ad-hoc-only schema 도입). 본문 history record 보존.
>
> Architecture decision SSOT = [ADR-035](../adr/ADR-035-codeforge-agent-teams-epic-architecture.md) (Epic CFP-134).

# decision-packet v2.1

## 1. 목적

CFP-59 (ADR-019) → CFP-61 (ADR-022) Sonnet decider auto-proceed system 의 decision packet schema. Claude+Codex 가 생성한 옵션 set + cross-review + 사용자 context 를 Claude Sonnet (`claude-sonnet-4-6`) decider 에 전달할 때의 정형 format. Decider 응답·sanity audit·retry/fallback 결과 까지 누적 기록.

**(CFP-135 Deprecated 후)**: 본 schema 자동 발동 무효 — frontmatter 위 deprecation note 참조.

본 registry 는 wrapper-owned (registry kind, lint scope 밖). MANIFEST.yaml 의 contracts list 에 등록하지 않음.

**v1 → v2 MAJOR bump per ADR-008**: backward-incompatible breaking change. `gemini_decision` → `decider_decision` rename, enum 단순화, `model` field 추가, AC-2 timing fields 추가. v1.0 + v1.1 archived state 유지 (body frozen). 신규 packet 은 v2 schema 강제 (hard cutover, ADR-019 acceptance 후).

## 2. Schema

```yaml
packet_id: <story_key>-<3-digit seq>     # globally unique, format CFP-NN-NNN
content_hash: <sha256>                    # normalized options + context hash (decider_decision 제외)
trigger: option-formulation | fix-root-cause | codex-ambiguity | brainstorming-constraint | review-verdict
story_key: CFP-NN
seq: 1                                    # Story 내 순번
context:
  background: <verbatim user request + 직전 분기 history>
  constraints: <repo SSOT / ADR refs / domain context>
options:                                  # 3+ 옵션 가능
  - id: <option id e.g. A, B, ..., Y_prime>
    source: claude | codex | both
    rationale: <generator analysis, multi-paragraph>
    cross_review: <other LLM view, agree/disagree + reasoning>  # Decider read-only
recommendations:
  claude: <option id>
  codex: <option id>
  divergence: <if claude != codex, why; null if agree>
decider_decision:                         # filled in step 5 of decision flow (renamed from gemini_decision)
  model: <model ID, e.g., claude-sonnet-4-6>  # NEW v2 field — invariant verification + history tracking
  pick: <option id>
  ranking: [<id>, <id>, ...]              # 모든 옵션 순위
  reasoning: <multi-paragraph>
  confidence: high | medium | low
  override_required: bool                 # true if pick rejected by both Claude+Codex
sanity_audit:                             # filled in step 6b only (override case)
  result: PASS | FAIL
  notes: <Codex sanity audit reasoning>
attempts:                                 # retry / resume 시 append
  - n: 1
    timestamp: <ISO8601>
    agent_call_started_at: <ISO8601>      # NEW v2 field — Agent tool invocation submission timestamp (AC-2 latency)
    decider_response_received_at: <ISO8601>  # NEW v2 field — parseable response 회수 timestamp (AC-2 latency)
    notification_or_log_written_at: <ISO8601>  # NEW v2 field — user notification 또는 §12/packet log append (whichever first) timestamp (AC-2 latency)
    outcome: success | parse_failure | timeout | malformed
              | repeated_identical | user_override | decider_suspended | packet_requires_review_reopen
authority_transfer:                       # quota/auth 실패 시
  occurred: bool
  final_decider: claude_sonnet | user     # v2 enum simplified (gemini / codex_legacy 제거)
fallback_unavailable: bool                # decider 사용 불가 + Codex sanity audit 도 차단 시
```

## 3. 항목 정의

### 3.1 packet identity

- `packet_id`: Story KEY + 3-digit zero-padded seq (예: `CFP-59-001`). globally unique across all Story sessions. concurrent Story session 운영 시 별도 packet artifact / Story §12 log / `content_hash` field 유지 의무 — packet_id collision 발생 시 packet 재생성 + suffix `-<timestamp>` 추가.
- `content_hash`: options + context 정규화 후 SHA-256 (decider_decision 제외). "같은 packet" 정의 = packet_id + content_hash 동시 일치. content 변경 시 새 packet 발급. packet artifact 무결성 검증 용.

### 3.2 trigger enum (CFP-57 + CFP-61)

- `option-formulation`: substantive 다중 선택지 (stop point a)
- `fix-root-cause`: FIX Ledger 원인 판정 Claude vs Codex 불일치 (stop point b)
- `codex-ambiguity`: Codex 가 결론 회피 — **option-formulation 단계 한정 (CFP-61 scope narrowing)**, review-verdict 흐름의 worker ambiguity 는 별도 trigger (`packet_requires_review_reopen` outcome routing)
- `brainstorming-constraint`: brainstorming clarifying Q 의 d-constraint sub-class (stop point d-constraint)
- `review-verdict`: **NEW (CFP-61)** — 매 review iteration 종료 후 Sonnet final pick (PASS|FIX). review_lane_context block required.

### 3.3 options

- `source`: 옵션 작성자 (`claude` / `codex` / `both` — 양 LLM 가 동일 옵션 생성 시).
- `rationale`: 옵션 생성자 분석 multi-paragraph.
- `cross_review`: 상대 LLM 의 평가 (agree/disagree + 근거). **Decider read-only** — Sonnet 은 read 만 가능, write/modify 금지 (decider 모델 invariant — ADR-019 결정 4).

### 3.4 decider_decision (NEW v2 — model field 추가)

- `model`: decider 모델 ID. Phase 1 = `claude-sonnet-4-6` 고정. silent model swap 차단 — controller 가 pre-call 검증 + post-response `decider_decision.model` 검증 (mismatch 시 `outcome: malformed` 처리, AC-4 정합).
- `pick`: options[].id 중 하나.
- `ranking`: 모든 옵션 순위 (pick 포함).
- `reasoning`: multi-paragraph.
- `confidence`: enum {high, medium, low}.
- `override_required`: pick 이 Claude+Codex 둘 다 reject 한 옵션이면 true → step 6b sanity audit 진입.

### 3.5 attempts

- 매 retry / resume / fallback 시 append.
- **AC-2 timing fields** (NEW v2):
  - `agent_call_started_at` — controller Agent-tool invocation submission ISO8601 timestamp.
  - `decider_response_received_at` — parseable response 회수 ISO8601 timestamp.
  - `notification_or_log_written_at` — user notification 또는 §12/packet log append (whichever first) ISO8601 timestamp.
  - PASS 조건: response latency (`decider_response_received_at` - `agent_call_started_at`) ≤ 30s + notification latency (`notification_or_log_written_at` - `decider_response_received_at`) ≤ 10s.
  - 위반 시 packet artifact 에 `latency_violation: true` + 위반 axis 추가 record (informational, 운영 진행 차단 안 함).
- `outcome` enum 8 values (CFP-61 v2.1 추가):
  - 7 values from v2 그대로
  - `success` — Sonnet 정상 응답 + schema 정합
  - `parse_failure` — non-YAML / schema-invalid 응답 (1 회 retry 대상, retry with explicit YAML correction prompt)
  - `timeout` — Sonnet API timeout / transient (1 회 retry 후 user)
  - `malformed` — retry 후에도 schema-invalid → user escalation (또는 pre-call planned model ≠ response 의 model 인 경우)
  - `repeated_identical` — ≥2 회 동일 packet 동일 pick 반복 실패
  - `user_override` — 사용자 mid-flow 직접 결정
  - `decider_suspended` — 사용자 explicit suspension / Agent tool quota / billing / auth/runtime denial / repeated infrastructure failure
  - `packet_requires_review_reopen` — **NEW (CFP-61)**: Sonnet 응답 = PACKET_REQUIRES_REVIEW_REOPEN. ReviewPL 재 spawn (per `(story_key, lane, iteration)` 1 회 한도). 두 번째 신호 시 user escalation.

### 3.6 authority_transfer

- Sonnet 실패 시 `occurred: true` + `final_decider` 변경. 단일 recursive 없는 path: Sonnet → user.
- `final_decider` enum 2 values:
  - `claude_sonnet` — primary decider (model-aware naming retained — `decider_decision.model` field 와 redundant 하지만 history-friendly)
  - `user` — Sonnet failure / sanity-FAIL / repeated 등 escalation

### 3.7 fallback_unavailable

- Decider 사용 불가 (Sonnet quota / auth) + Codex sanity audit 도 차단 시 true. 사용자 escalation + packet draft 첨부.

### 3.8 review_lane_context (NEW v2.1, trigger=review-verdict 시 required)

```yaml
review_lane_context:
  review_verdict_contract_version: "3.0"
  lane: design | code | security
  story_key: <STORY_KEY>
  iteration: <int>
  pl_recommendation: PASS | FIX | FIX_DISCRETIONARY | ESCALATE_PACKET_INCOMPLETE
  findings_hash: <sha256>
  source_packet_ref:
    artifact_path: <internal-docs path or wrapper sibling path>
    content_sha256: <sha256 of review-verdict-v3 yaml>
    github_issue_or_pr_ref: <optional, populated when binding GitHub Issue/PR — format owner/repo#number>
```

**Validation rules**:
- trigger=review-verdict 시 review_lane_context 모든 required field populated
- findings_hash = canonicalized review-verdict-v3 findings[] SHA-256 (deterministic JSON serialization, sort keys, no whitespace)
- Orchestrator MUST verify findings_hash before invoking Sonnet
- mismatch 시 packet malformed → user escalation
- source_packet_ref.content_sha256 = review-verdict-v3 yaml 의 SHA-256
- github_issue_or_pr_ref populated 시점 = Phase 1 PR / Phase 2 PR open 후 review iteration 진행 중. PR open 전 (요구사항 / 설계 lane) absent.

## 4. 변경 규칙 (영향 / 라이프사이클)

### 4.1 라이프사이클

- **생성**: Claude 본세션 (controller) 이 trigger 발화 시 schema 따라 수동 YAML 작성 (Phase 1 doc-only). controller 가 schema 따라 작성 → `Agent` tool with `model: sonnet` invocation.
- **저장**: `<internal-docs>/<plugin-folder>/decisions/<packet_id>.yaml` (full schema), Story §12 (요약 1 row).
- **Retention**: Story closure 까지. closure 후 archive 정책 후속 (별도 CFP).
- **Audit**: 첫 5 packet scheduled self-audit (schema 검증 — `decider_decision.model` 정확 record + invariant 충족), 그 후 failure-driven only.

### 4.2 v1 → v2 transition

- ADR-019 acceptance 후 신규 packet = v2 강제 (hard cutover).
- ADR-019 acceptance 전 생성된 v1 packet = v1.1 schema 그대로 완료 가능 (in-flight grace).
- v1 in-flight packet 가 v2 acceptance 시점 에 미완료 인 경우 — 해당 packet 내 outcome 그대로 v1.1 enum 으로 close, 다음 packet 부터 v2 적용.
- 기존 v1 artifact = Archived historical record (rewrite 안 함, explicit migration request 시 외 — 향후 v1 → v2 retroactive migration 필요 시 별도 CFP).
- Inventory at ADR-019 acceptance: CFP-57-001 (CFP-57 brainstorming archive) = historical only, no active in-flight.

### 4.3 First-5 review-verdict packet self-audit checklist (CFP-61 추가)

각 packet 별 다음 11 checklist 통과 의무:

- [ ] decider_decision.model = claude-sonnet-4-6 (model-ID exact match)
- [ ] Sonnet 응답이 §4.5.3 schema 준수 (decision / reasoning_summary / confidence + PACKET_REQUIRES_REVIEW_REOPEN 시 packet_gap_summary)
- [ ] review-verdict-v3 findings / pl_recommendation / decision_state populated
- [ ] decision-packet-v2.1 review_lane_context 모든 required field populated
- [ ] findings_hash verification 성공 (canonicalized findings[] hash 일치)
- [ ] source_packet_ref.content_sha256 = review-verdict-v3 yaml SHA256 일치
- [ ] Sonnet response = packet_requires_review_reopen 으로 routing 시 (Sonnet-authored finding 0 건)
- [ ] Story §9 (PASS/FIX) / §10 (FIX) / §12 (모든 trigger) write 완결
- [ ] override marker format 준수
- [ ] reopen budget enforcement (per (story_key, lane, iteration) ≤ 1)
- [ ] decision-packet artifact yaml = decision-packet v2.1 schema 정확 준수

11 checklist 1 건이라도 fail = user escalation. 5 packet 모두 통과 후 = failure-driven only.

## 5. 검증 (Acceptance Criteria — ADR-019 §5.5 SSOT mirror)

### AC-1: Trace delivery

첫 substantive decision 발생 시점 에 다음 3 trace 모두 작성:

- chat notification (controller-authored summary, ≤200 chars 또는 적절한 길이)
- Story §12 row 1건 (`audit_result` enum 값 정확)
- packet artifact 1건 (`<internal-docs>/<plugin-folder>/decisions/<packet_id>.yaml` — decision-packet-v2 schema 준수, `decider_decision.model: claude-sonnet-4-6` 정확 record)

3 trace 누락 = 정책 위반, post-merge follow-up commit 의무.

### AC-2: Latency target

Sonnet invocation 시작 후:

- 측정 정의: AC-2 측정 = `agent_call_started_at` 부터 `decider_response_received_at` 까지 ≤ 30s, `decider_response_received_at` 부터 `notification_or_log_written_at` 까지 ≤ 10s.
- timing fields packet artifact record 의무 (§3.5).
- PASS 조건: response latency ≤ 30s (timeout retry 1 회 포함 1 분 한도) + notification/log latency ≤ 10s.
- 위반 시 packet artifact 에 `latency_violation: true` + 위반 axis (`response` / `notification`) 추가 record.

### AC-3: v2 schema 운영 검증 + hard cutover

첫 substantive decision 시:

- packet artifact 의 `decider_decision.pick` field record
- `decider_decision.model: claude-sonnet-4-6` 정확 record
- `attempts[].outcome` enum value 가 v2 7 values 중 하나
- Story §12 row 의 `audit_result` 컬럼 = v2 5 values 중 하나
- 4 항목 모두 PASS 시 v2 schema 운영 검증 PASS. 1 개라도 누락 / 잘못된 value = schema deviation 처리 (manual fix + Story §10 row 기록).
- **Hard cutover**: ADR-019 acceptance 후 첫 packet 은 v2 schema 강제. v2 acceptance 후 v1 schema 사용한 신규 packet = AC-3 자동 FAIL.

### AC-4: Decider 모델 invariant 검증 + 검증 timing

모든 decision 의 packet 에:

- `decider_decision.model` field 명시
- 해당 model 이 controller (Opus 본세션) / Codex / sanity-auditor 중 어느 것 과도 일치하지 않음 (invariant 충족, model-ID 단위)
- Phase 1 = `claude-sonnet-4-6` 고정이라 사실상 invariant 자동 충족, 향후 모델 변경 시 검증 의무.

검증 timing:

- **Pre-call**: controller 가 Agent invocation 전 planned decider model (예: `claude-sonnet-4-6`) 검증 — invariant set (controller / Codex / sanity-auditor model-ID 와 비교) 충족 확인.
- **Post-response**: Agent response parse 후 `decider_decision.model` field 검증 — pre-call planned model 과 일치 확인.
- **Mismatch 처리**: 첫 occurrence = `outcome: malformed` (planned ≠ response 의 model). 1 회 retry 후 mismatch persistent = user escalation. silent model swap 차단.

### AC-5: ROI 측정 metrics

30+ packet 운영 record 의무 metrics (Phase 1 → Phase 2 transition 평가 input):

- `model` — `decider_decision.model` 값 (Phase 1 = `claude-sonnet-4-6` 단일)
- `attempts_count` — `attempts[]` array length (retry 발화 횟수 포함)
- `latency` — AC-2 의 response / notification 두 axis (median / p95)
- `retry_count` — `attempts_count - 1` (첫 attempt 제외)
- `escalation_outcome` — `direct` / `sanity-PASS` / `sanity-FAIL` / `decider-suspended` / `user-escalation` 분포
- `approximate_controller_agent_call_count` — controller 가 Agent tool invoke 한 횟수 (per-trigger budget signal 와 정합)

30 packet 후 summary metrics 의무:

- proceed rate = (direct + sanity-PASS) / total
- escalation rate = (sanity-FAIL + decider-suspended + user-escalation) / total
- median / p95 latency (response axis + notification axis)
- operational cost notes (Anthropic console 의 Sonnet 사용량, 사용자 manual 입력)

본 metrics = Phase 2 subagent ROI 평가 input. 30 packet 미만 시 metrics partial record OK, 평가 보류.

## 6. Versioning

### v2.1 (2026-05-02 — CFP-61 ADR-022)

backward-compatible MINOR bump (ADR-008 SemVer additive):
- `trigger` enum + `review-verdict`
- `attempts[].outcome` + `packet_requires_review_reopen`
- `review_lane_context` 신규 optional block (trigger=review-verdict 시 required)
- First-5 review-verdict packet self-audit checklist (§4.3)

v2.0 reader backward-compat 유지 (모르는 enum value + optional block 무시).

### v1.0 (2026-05-01 — CFP-57 ADR-018 carrier)

초기 schema. attempts.outcome 13 enum + authority_transfer.final_decider 3 enum (gemini / codex_legacy / user).

### v1.1 (2026-05-02 — CFP-58 ADR-018 Amendment 1)

backward-compatible enum 확장 (ADR-008 SemVer minor bump):
- `attempts[].outcome` + `quota_sonnet_fallback`
- `authority_transfer.final_decider` + `claude_sonnet`

### v2.0 (2026-05-02 — CFP-59 ADR-019)

**MAJOR bump per ADR-008 SemVer (breaking change)**:

- `gemini_decision` → `decider_decision` rename (semantic = decider 의 pick, model-agnostic naming)
- `decider_decision.model` field 추가 (invariant verification + history tracking)
- `attempts[]` AC-2 timing fields 추가 (`agent_call_started_at` / `decider_response_received_at` / `notification_or_log_written_at`)
- `attempts[].outcome` enum 갱신 — Gemini-specific 값 제거 (`quota_exhausted`, `quota_sonnet_fallback`, `gemini_suspended`, `dual_failure`, `schema_terminal_failure`, `parse_terminal_failure`, `invalid_packet`, `unauthorized`). v2 7 values: `success` / `parse_failure` / `timeout` / `malformed` / `repeated_identical` / `user_override` / `decider_suspended`.
- `authority_transfer.final_decider` enum 단순화 (v1.1 multi-value → v2 `claude_sonnet | user` 2 values)
- `audit_result` (Story §12 컬럼) enum 단순화: 5 values (`direct` / `sanity-PASS` / `sanity-FAIL` / `decider-suspended` / `user-escalation`)

v1 status=Archived (frozen body), v2 status=Active.
