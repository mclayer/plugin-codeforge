---
adr_number: 19
title: Sonnet Decider Auto-Proceed Policy
status: Superseded
superseded_by: ADR-022
category: Team & Process
date: 2026-05-02
related_files:
  - CLAUDE.md
  - docs/inter-plugin-contracts/decision-packet-v2.md
  - templates/story-page-structure.md
  - docs/adr/ADR-018-gemini-decider-auto-proceed.md
  - docs/adr/ADR-001-review-agent-unification.md
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md
  - docs/adr/ADR-009-wrapper-only-decomposition.md
related_stories:
  - CFP-59
is_transitional: true
---

# ADR-019: Sonnet Decider Auto-Proceed Policy

## 상태

> **SUPERSEDED by ADR-022** (2026-05-02, 1-day succession). 본 ADR-019 = historical record. CFP-58 → CFP-59 → CFP-61 iterative refinement 결과 ADR-022 = active SSOT. 본문 결정 1-10 + Amendment 1 본문 무수정 (history record).

Accepted (2026-05-02) — CFP-59 carrier. Supersedes ADR-018 + Amendment 1 (CFP-58).

## 컨텍스트

CFP-57 (ADR-018 carrier, 2026-05-01) 가 Gemini 를 substantive choice 의 final decider 로 도입. CFP-58 (Amendment 1, 2026-05-02) 가 Gemini Plus subscription OAuth + Sonnet quota fallback 추가. CFP-58 merge 직후 운영 진단 (2026-05-02):

- Gemini Plus consumer 구독 ≠ CLI API quota 상승 (axis 분리 — Plus = consumer chat product, CLI quota 별도)
- Free OAuth quota throttle 즉시 발화 → CFP-58 의 Sonnet fallback path 가 매 substantive decision 마다 항시 활성
- Model ID `gemini-2.5-pro-001` 가 CLI 에서 invalid (404 응답) — model identifier 검증 자체 미해결
- 결과: CFP-57+58 의 Gemini decider 가 사실상 동작하지 않고 Sonnet fallback 만 발화

사용자 directive (2026-05-02):

> "결정은 gemini를 제거하고 sonnet을 통해 하도록하자."

추가 invariant:

> "decider 모델은 직전 리뷰나 대안을 도출한 모델과는 다른 모델이어야 한다."

본 ADR 의 핵심 결정:

1. Gemini 완전 제거 — CFP-58 의 fallback path 가 main path 로 promotion.
2. Claude Sonnet (`claude-sonnet-4-6`) = main decider via `Agent` tool runtime (Anthropic billing 내, 외부 auth 무관).
3. **Decider 모델 invariant 명문화** — decider ≠ option-generator / cross-reviewer / sanity-auditor (model-ID + role level).

## 결정

### 결정 1: 권한 hierarchy

| Role | Actor | Vendor |
|---|---|---|
| Implementer | Claude (Opus 4.7, controller 본세션) | Anthropic |
| Auditor | Codex (gpt-5.5 high) | OpenAI |
| **Decider** | **Claude Sonnet (`claude-sonnet-4-6`)** | Anthropic |
| Override | User (escalation whitelist 만) | — |

CFP-58 → CFP-59 변경: `Decider` 행 actor = Gemini → Claude Sonnet. Sonnet = always-decider (Claude+Codex 합의 무관, 항상 Sonnet call). 사용자 directive 정합.

### 결정 2: Stop point coverage (CFP-57 그대로 유지)

자동 trigger (4 종, decider 발화):

- (a) substantive 다중 선택지
- (b) FIX root-cause 불일치
- (c) Codex ambiguity
- (d-constraint) 제약 surfacing Q

User escalation whitelist (5 종):

- (d-intent) 사용자 의도 추정
- (e) lane FIX max 3
- 운영 prerequisite 실패 (Anthropic billing / Agent tool 가용성 등)
- destructive action
- denylist (보안 sensitive)

CFP-59 변경: 운영 prerequisite axis 가 Gemini auth (CFP-58) → Anthropic Sonnet API auth / Agent tool 가용성 (CFP-59) 로 이동. 항목 자체 변경 없음.

### 결정 3: Decision flow 7-step

1. **Claude blank-slate options 생성** — controller (Opus) 가 자기 입장 options 작성.
2. **Codex (codex-rescue) blank-slate options 생성** — Codex memory trigger 1 Round 1 발화 (parallel OK).
3. **Cross-review** — Claude·Codex 가 상대 옵션 검토 (recommendations + risks).
4. **Decision packet v2 구성** — `decider_decision` field 는 빈 상태 (decider 가 작성 예정).
5. **Sonnet call** — `Agent` tool with `model: sonnet` (또는 `claude-sonnet-4-6` 명시) — packet YAML 을 prompt 로 전달, 응답에서 pick + ranking + reasoning + confidence 회수. 응답 schema = packet `decider_decision` block.
   - **Decider context isolation**: Decider 가 받는 input = decision-packet-v2 YAML + decider prompt only. controller 의 full session history 전달 또는 의존 금지. 필요 context 는 packet `context` field 에 명시 embedding. Decider 는 packet 외부의 controller session memory 또는 prior turn 에 access 불가능 — full self-contained input 의무.
6. **Pick handling**:
   - pick ∈ Claude·Codex 합의 옵션 → auto-proceed
   - pick = 둘 다 reject 한 옵션 → Codex sanity audit 1 회 → PASS proceed / FAIL user escalation
7. **Logging** (결정 7) — Story §10 FIX Ledger (trigger b 시) + Story §12 Sonnet Decision Log + packet artifact full schema.

### 결정 4: Decider 모델 invariant (NEW core to ADR-019)

본 invariant 는 사용자 directive 에 의한 신규 정책 — single-model bias 차단 + option-gen / reviewer / decider 권한 분리 보장 + vendor diversity 부분 보존.

- **decider ≠ option-generator** — option-generator (Claude Opus / Codex) 가 자기 옵션 결정하면 self-bias.
- **decider ≠ cross-reviewer** — cross-reviewer 가 자기 review 결과 결정하면 review 무력화.
- **decider ≠ sanity-auditor** — sanity-auditor 가 audit 결과 결정하면 audit gate 무력화.
- **동일 vendor 다른 tier 허용** — Claude Opus (generator) + Claude Sonnet (decider) OK. tier 가 다르면 model 자체가 다른 instance 라 self-bias risk 낮음.
- **Enforcement = exact model-ID + role level** (vendor / family level 아님). model ID string-equality 가 1차 기준 — 명시: `claude-opus-4-7` (generator) ≠ `claude-sonnet-4-6` (decider) ≠ `gpt-5.5` (auditor).
- **변경 시 ADR amendment 의무**:
  - Opus → Opus 5 bump: Sonnet decider 그대로 OK (tier 분리 유지).
  - Sonnet 이 generator/reviewer 로 사용되기 시작: decider 를 Haiku 등 다른 tier 또는 외부 vendor 로 shift. ADR-019 amendment 의무.
  - Codex tier 변경 (gpt-5.5 → gpt-6 등): Sonnet decider 그대로 OK (Codex 는 다른 vendor 라 invariant 자동 충족).

**Codex sanity audit role classification**: Codex sanity audit (decision flow step 6b) = post-decider guardrail (primary decider 아님). sanity_auditor ≠ decider 이므로 invariant 만족. outcomes = sanity-PASS proceed 또는 sanity-FAIL user escalation only — sanity audit 가 decider 의 pick 을 수정하거나 새 pick 을 생성하지 않음.

**Decider read-only on cross_review**: Decider 는 packet `options[].cross_review` field 를 read 만 가능, write/modify 금지. cross-reviewer 정의 = packet 의 `cross_review` field 작성한 모델 (Claude / Codex). Sonnet 은 cross-reviewer 가 아님 (cross_review write 권한 없음) — invariant 만족. decider response 가 packet schema 상 `decider_decision` block 외 다른 field (예: `cross_review`) 를 수정한 경우 = malformed outcome 처리.

**Vendor / tier 정의**: Vendor = 모델 provider (Anthropic / OpenAI / Google). Tier = 같은 vendor 내 distinct model ID/capability class. ADR-019 가 명시 authorize 한 set: Claude Opus 4.7 (generator) + `claude-sonnet-4-6` (decider) + Codex gpt-5.5 high (auditor). 다른 vendor 의 임의 모델 또는 같은 vendor 의 미열거 tier 는 별도 ADR 의무.

### 결정 5: Decision packet v2 (decision-packet-v2)

ADR-008 SemVer: field rename = breaking change = MAJOR bump.

`docs/inter-plugin-contracts/decision-packet-v1.md` → status=Archived (frontmatter 만 변경, 본문 보존 history). 신규 `docs/inter-plugin-contracts/decision-packet-v2.md` (kind:registry, MANIFEST.yaml registry list comment 에 v1 Archived + v2 Active 표기).

**v2 의 v1 대비 변경 (breaking)**:

- `gemini_decision` → **`decider_decision`** (rename, semantic = "decider 의 pick", model-agnostic naming)
- `decider_decision.model: <model_name>` 필드 추가 — decider model 명시 (Phase 1 = `claude-sonnet-4-6`, 향후 변경 추적 용 + invariant verification)
- `attempts[].outcome` enum 갱신 — Gemini-specific 값 제거. v2 enum 7 values: `success` / `parse_failure` / `timeout` / `malformed` / `repeated_identical` / `user_override` / `decider_suspended`
- `attempts[]` timing fields 추가 — `agent_call_started_at` / `decider_response_received_at` / `notification_or_log_written_at` (AC-2 latency record)
- `authority_transfer.final_decider` enum 단순화: 2 values (`claude_sonnet | user`)
- `audit_result` (Story §12 컬럼) — enum 갱신 5 values: `direct` / `sanity-PASS` / `sanity-FAIL` / `decider-suspended` / `user-escalation`

SSOT = `docs/inter-plugin-contracts/decision-packet-v2.md`.

### 결정 6: 운영 정책

- **Auth 무관** — Sonnet 호출 = `Agent` tool runtime (Anthropic billing 내). 외부 API key / Plus subscription / Vertex AI / GCA 모두 prerequisite 아님 (CFP-58 의 axis 모두 제거). 외부 Anthropic API key path 또는 Claude Pro 구독 path 명시 안 함 — Agent tool runtime 만 의존. Agent tool quota / billing 한계 = 운영 prerequisite 카테고리 escalation.
- **모델**: `claude-sonnet-4-6` 고정. CLAUDE.md "Environment" 섹션 latest stable. 변경 시 ADR-019 amendment 의무 + decision-packet-v2 minor version note. Silent model swap 금지.
- **Cost**: Phase 1 = 자동 cost gate 없음. Anthropic 사용량 manual monitoring (사용자, console).
- **Fallback matrix** (Sonnet 자체 실패 처리, 단일 recursive 없는 path):

| 실패 유형 | 처리 |
|---|---|
| Sonnet API timeout / transient | 1 회 retry → 실패 시 user escalation. `attempts[].outcome = timeout` |
| Sonnet response malformed (non-YAML / schema-invalid) | `attempts[].outcome = parse_failure` 기록 + 1 retry with explicit YAML correction → second failure = `outcome = malformed` + user escalation |
| Repeated identical Sonnet error (≥2 회 동일 packet 동일 pick 실패) | user escalation. `attempts[].outcome = repeated_identical` |
| Codex sanity audit FAIL (override case) | user escalation. `audit_result = sanity-FAIL` |
| Sonnet API quota exhausted | `attempts[].outcome = decider_suspended` + `authority_transfer.final_decider = user` + `audit_result = user-escalation` + 운영 prerequisite 카테고리 escalation |
| Sonnet auth/runtime denial | `attempts[].outcome = decider_suspended` + 운영 prerequisite 카테고리 escalation |

(CFP-58 의 Gemini fallback chain — Codex audit gate (legacy) / Sonnet fallback / dual-failure 등 — 모두 제거. 단일 path: Sonnet → user.)

- **Authority transfer**: Sonnet = decider only when available. 실패 시 user (no recursive chain). authority transfer 발생 시 packet log `authority_transfer.occurred: true` + `final_decider: user` 명시.

### 결정 7: Logging & Audit

- **Story §10 FIX Ledger** — trigger b root-cause 시 `decider: claude_sonnet` 컬럼. 향후 decider 모델 변경 시 ADR-019 amendment + Story §10 row 의 컬럼 값 갱신.
- **Story §12 "Sonnet Decision Log"** (CFP-57 §12 "Gemini Decision Log" rename) — 7 컬럼 (`packet_id` / `trigger` / `options_count` / `decider_pick` / `override?` / `audit_result` / `timestamp`). `decider_pick` = `decider_decision.pick` 의 record (model-agnostic naming).
- **Detailed packet artifact** — `<internal-docs>/<plugin-folder>/decisions/<packet_id>.yaml` (decision-packet-v2 schema 준수, includes `decider_decision.model` field).
- **Audit policy** — 첫 5 packet scheduled self-audit (schema 검증 — `decider_decision.model` 필드 정확 record + invariant 충족 확인). 그 후 failure-driven only.

**Naming 일관성**: packet field 와 Story §10 / §12 row 모두 `claude_sonnet` 표기 일관 사용 (underscore form, model-aware naming).

### 결정 8: Phase boundary

- **Phase 1 = doc-only** — 본 ADR-019 maintenance only. agent / skill / 코드 추가 없음. Sonnet 호출 = controller 가 매 trigger 시점 발화하는 runtime tool call (`Agent` tool with `model: sonnet`).
- **Phase 2 = subagent ROI 평가** — 30+ packet 운영 후 별도 CFP. Sonnet 호출 wrapper script / sub-agent 정의 / 자동 invariant verification 등.
- **Phase 1 → Phase 2 transition authority** = 사용자 명시 승인 필수. ADR-019 acceptance criteria 충족 + 30+ packet + cost report.

### 결정 9: Suspend / reactivation

CFP-57 (ADR-018) 결정 8 패턴 generalized to Sonnet:

- 사용자 explicit suspension ("잠깐 끄자" / "Sonnet decider 정지" 등) → session/Story 단위 일시 중단 + log `decider_suspended`.
- Suspend 중 새 substantive trigger 발화 시 → packet 작성 + Claude·Codex 합의 임시 proceed (없으면 user).
- Reactivate 후 미결정 packet sequential 재처리.
- Suspend 후 reactivate 까지는 user escalation only (substantive trigger 발화해도 자동 decider 호출 차단).

`decider_suspended` enum 값 trigger:

- 사용자 explicit suspension
- Agent tool quota / billing 한계
- Agent tool auth / runtime denial
- Repeated decider infrastructure failure (≥2 회 연속 timeout / malformed / unauthorized)

### 결정 10: Migration / transition rules

- **V1 packet (CFP-57+58 archive)** — Archived state 유지, body frozen, rewrite 안 함. Inventory: CFP-57-001 (CFP-57 brainstorming archive) = historical only, no active in-flight.
- **ADR-019 acceptance 후 신규 packet** — v2 강제 (hard cutover).
- **In-flight v1 packet** (acceptance 전 생성) — v1.1 schema 그대로 완료 가능 (in-flight grace). ADR-019 acceptance 후 모든 신규 = v2.
- **V1 archived = body frozen** — `decision-packet-v1.md` status=Archived 후 schema body frozen — archival metadata (frontmatter `status` / `superseded_by`) / supersession link / typo-only correction 만 허용. 모든 behavioral change (enum 추가 / 필드 추가 / semantic 변경 등) = v2 에만.
- **ADR-018 supersession 강화** — frontmatter `status: Accepted` → `status: Superseded` + `superseded_by: ADR-019`. 본문 §상태 섹션 supersession line 추가 (visible note). 본문 결정 1-9 + Amendment 1 본문 무수정 (history record).
- **Non-decider Gemini 사용** — ADR-019 = decider path + 세션 prerequisite 에서 Gemini 제거. 향후 non-decider Gemini 사용 (별도 도구 / 보조 reviewer / Phase 2 ROI 결과 도입 등) = 별도 ADR 또는 Story-specific approval 의무.

## 검토한 대안

### 대안 A — ADR-018 Amendment 2 (in-place fix)

거부 사유:

- 변경 magnitude 가 amendment 패턴 한계 초과. CFP-58 의 Amendment 1 = 결정 5 본문 + 결정 9 신설 (2 sub-edit) 수준. CFP-59 = decider actor 자체 변경 (Gemini → Sonnet) + decision-packet MAJOR bump + 신규 invariant + 운영 정책 전면 단순화 (auth axis 4 종 제거).
- ADR-018 carrier title 자체 부적절 — "Gemini Decider Auto-Proceed Policy" 가 Sonnet decider 로 변경되면 title 의미 자체 모순. Amendment 2 로 처리하면 title-vs-content drift.
- New ADR-019 = cleaner history. 향후 reader 가 ADR-018 보면 "Gemini era policy (superseded)", ADR-019 보면 "Sonnet era policy (active)" 명확.
- CFP-56 precedent (ADR-013 Amendment + ADR-017 신설 분리) 와 정합 — 큰 magnitude 변경은 신규 ADR.

### 대안 B — decision-packet v1 retain (의미 재해석)

거부 사유:

- `gemini_decision` 필드명이 historical 마커 로 남아 future reader 혼란. "Sonnet decider 인데 왜 gemini_decision field 인가" 의문.
- v1.1 minor bump (CFP-58) 가 enum 확장으로 backward-compatible 했지만, field rename = breaking change 라 SemVer 룰 (ADR-008) 적용 시 MAJOR bump 필수.
- Field rename = mechanical refactor, 의미 손실 없음. v2 명확.
- v1 archive + v2 active = SemVer 정합 + history 보존.

### 대안 C — Sonnet 외 다른 Anthropic 모델 (Haiku / Opus 다른 tier)

거부 사유:

- **Haiku (`claude-haiku-4-6`)**: capability 부족 — substantive multi-option decision 에 reasoning depth 부족. Phase 1 의 brainstorming-grade decision 부적합.
- **Opus (controller 와 동일 tier)**: decider 모델 invariant 위반 — controller (Opus) = option-generator + cross-reviewer 라 Opus decider = self-bias risk. 같은 model instance 가 옵션 + 결정 둘 다 하면 sanity check 효과 없음.
- **Sonnet**: capability (substantive decision OK) + invariant (controller Opus 와 다른 tier) 둘 다 만족.

### 대안 D — Vendor diversity 위해 외부 모델 (Cohere / Mistral / Llama 등)

거부 사유:

- 추가 auth / API key / billing setup 의 ROI ≪ 단일 vendor 단순화. CFP-58 운영 진단 결과 외부 vendor 의존성 (Gemini) 이 main failure mode 였음.
- Codex 가 OpenAI vendor 보존 (audit/cross-review) — vendor diversity 일부 유지 (Anthropic + OpenAI).
- Phase 1 = doc-only 정책상 새 vendor 도입 = 추가 setup cost 만, capability 향상 없음. Phase 2 ROI 평가 시 재검토 가능.

### 대안 E — Sonnet decider + Gemini 보조 (dual-decider with vote)

거부 사유:

- 사용자 directive 명시 "Gemini 를 제거". dual 운영 = directive 위반.
- Dual-decider 운영 = 복잡도 증가 (vote 합의 / tie-breaking 룰 / 두 모델 모두 fail 시 fallback 등 추가 spec 의무).
- CFP-58 운영 진단 결과 Gemini 자체가 failure mode — 보조로 두어도 발화 시점 마다 quota / model ID 검증 실패 → 사실상 Sonnet 단독 운영 == CFP-59 단순화 의도와 동일 결과.
- 본 CFP 의 단순화 의도 위반.

## 결과

긍정:

- 사용자 stop 빈도 절감 유지 (CFP-57 의 motivation 보존). Sonnet 자동 결정.
- 외부 auth axis 4 종 제거 (`GEMINI_API_KEY` / Plus subscription / Vertex / GCA / OAuth login) — 단일 path 단순화. consumer plugin 설치 시 setup 부담 감소.
- Anthropic = controller (Opus) + decider (Sonnet) 단일 vendor — 외부 vendor 의존성 제거. Codex (OpenAI) 가 audit/cross-review 별 vendor 로 vendor diversity 일부 보존.
- Decider 모델 invariant 명문화 — single-model bias 방지 + 향후 모델 stack 변경 시 prompt 단계 review forcing.
- decision-packet v2 schema = model-agnostic naming (`decider_decision`) — 향후 decider 모델 변경 시 schema 변경 없이 protocol 본문만 갱신 가능.
- Phase 1 = doc-only 유지 — agent/code 추가 없음 (ADR-009 무영향).

부정:

- enforcement = Claude self-discipline (Phase 1 한정). protocol drift risk (CFP-57 와 동일).
- Anthropic 단일 vendor 의존성 — Anthropic Agent tool 가용성 = invariant. 가용성 실패 시 user escalation 만 가능.
- v2 schema MAJOR bump = breaking change. 운영 v1 in-flight packet 0 (CFP-57-001 archived) 라 migration cost 낮음.

후속:

- 30+ decision 후 Phase 2 subagent ROI 평가 (CFP-57 결정 7 그대로 유지).
- decision-packet v2 schema 운영 검증 후 v3 필요 여부 평가 (별도 CFP, ADR-008 룰 적용).
- 향후 모델 stack 변경 (Opus 5 / Sonnet 5 등) 시 ADR-019 amendment 또는 supersede.

## ADR 정합성

- **ADR-018** + Amendment 1 (CFP-58) — Superseded by ADR-019. file 변경 = status 줄 + 본문 supersession line만 (본문 결정 1-9 + Amendment 1 본문 무수정 history record).
- **ADR-008** — decision-packet v1 → v2 MAJOR bump (breaking change SemVer 정합). v1 archive + v2 active. MANIFEST.yaml registry list comment 갱신.
- **ADR-001** (review-agent-unification) — 영향 없음. review verdict 는 별도 axis, decider 정책 적용 대상 아님.
- **ADR-009** (wrapper-only-decomposition) — Phase 1 영향 없음 (agent count = 0 유지).
- **ADR-013 / ADR-016 / ADR-017** — 영향 없음.

## 해소 기준

**전이 분류**: Sonnet Decider Auto-Proceed (Gemini 후계). CFP-134 / ADR-035 Wave 1 에서 Deprecated — Sonnet decider 자동 발동 무효, 사용자 ad-hoc 호출만 허용.

**해소 evidence**:
- **metric**: Deprecated status (frontmatter)
- **who**: ADR-035 carrier
- **how**: CFP-134 Wave 1 merge (2026-05-08) — decider 자동 발동 채널 제거 + review-verdict v4 (ADR-044) cutover 완료

## 관련 파일

- `CLAUDE.md`
- `docs/inter-plugin-contracts/decision-packet-v2.md`
- `templates/story-page-structure.md`
- `docs/adr/ADR-018-gemini-decider-auto-proceed.md` (superseded)
- `docs/adr/ADR-001-review-agent-unification.md`
- `docs/adr/ADR-008-inter-plugin-contract-versioning.md`
- `docs/adr/ADR-009-wrapper-only-decomposition.md`
