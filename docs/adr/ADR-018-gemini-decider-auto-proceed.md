---
adr_number: 18
title: Gemini Decider Auto-Proceed System (Phase 1 doc-only policy)
status: Superseded
superseded_by: ADR-019
category: Team & Process
date: 2026-05-01
related_files:
  - CLAUDE.md
  - docs/inter-plugin-contracts/decision-packet-v1.md
  - docs/inter-plugin-contracts/MANIFEST.yaml
  - templates/story-page-structure.md
  - docs/adr/ADR-001-review-agent-unification.md
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md
  - docs/adr/ADR-009-wrapper-only-decomposition.md
  - docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md
  - docs/adr/ADR-017-skill-override-path-enforcement.md
related_stories:
  - CFP-57
  - CFP-58
---

# ADR-018: Gemini Decider Auto-Proceed System (Phase 1 doc-only policy)

## 상태

Accepted (2026-05-01) — CFP-57 carrier, Phase 1 doc-only.

**Amendment 1 (2026-05-02) — CFP-58**: Auth = OAuth via Gemini Plus (API key 제거), Fallback row "Quota exhausted" = Claude Sonnet (`claude-sonnet-4-6`) decider + 사용자 알림 + auto-proceed. decision-packet-v1 v1.1 minor bump (enum 확장 backward-compatible). Codex audit gate (legacy) fallback deprecated (실제 invocation 사라짐).

**Superseded (2026-05-02) by ADR-019** — CFP-59. ADR-018 + Amendment 1 (CFP-58) 모두 historical record 로 보존. ADR-018 본문 무수정 (cross-link 도 추가 안 함). 신규 packet / 결정 시 ADR-019 SSOT 사용.

## 컨텍스트

CFP-57 사용자 directive: "최종 결정은 gemini가 하게 될 것이다. claude와 codex는 대안 생성 + 교차리뷰. gemini가 결정한대로 설계." Motivation: Claude 가 substantive decision 마다 사용자 stop 발생 → 개발 시간 폭증.

기존 Codex audit auto-proceed gate (memory `feedback_codex_review_auto_proceed.md`) 는 PASS = proceed / FAIL = fix / ambiguity = user 모델. Codex 가 옵션 작성+선택 모두 책임지면서 Claude+Codex 불일치 시 사용자 escalation 발생. Gemini 도입으로 (1) Claude·Codex 동급 contributor + (2) Gemini 단일 final decider → 불일치 stop 제거.

## 결정

### 결정 1: 권한 hierarchy

| Role | Actor |
|---|---|
| Implementer | Claude (Opus 4.7) |
| Auditor | Codex (gpt-5.5 high) |
| Decider | Gemini (gemini-2.5-pro-001) |
| Override | User (escalation whitelist 만) |

Gemini = always-decider (Claude+Codex 합의 무관, 항상 Gemini call). 사용자 directive "그 내용 모두를 gemini에게 전달하여 gemini가 결정한대로" 정합.

### 결정 2: Stop point coverage

자동: (a) substantive 다중 선택지 / (b) FIX root-cause 불일치 / (c) Codex ambiguity / (d-constraint) 제약 surfacing Q.

User (escalation whitelist): (d-intent) intent-clarifying / (e) lane FIX max 3 / 운영 prerequisite 실패 / denylist (보안 sensitive).

(d) sub-class 분리: constraint-surfacing = "선택 가능한 제약 surfacing" (test scope / formatting / artifact placement). intent-clarifying = "사용자 미발화 product direction / 가치관 / 정책 / risk appetite". 모호 시 d-intent 분류 (안전 측).

### 결정 3: Decision flow

7 step: Claude blank-slate options → Codex blank-slate options → cross-review → packet 구성 → Gemini call → pick handling (direct vs Codex sanity audit override) → log.

### 결정 4: Decision packet schema

`decision-packet-v1` (kind:registry) 신설. SSOT = `docs/inter-plugin-contracts/decision-packet-v1.md`.

### 결정 5: 운영 정책 (Amendment 1 적용)

- **Auth** = OAuth via Gemini CLI Plus subscription (default). API key 제거 (Phase 1 prerequisite 아님). `Plus subscription` = `gemini-2.5-pro-001` access + 충분 quota 가 보장되는 모든 paid tier (SKU 명 무관 — controller 가 model access + quota 만 invariant 검증). 세션 개시 의무 표 (CLAUDE.md) `GEMINI_API_KEY` → `gemini auth status` Plus 확인 으로 교체.
- **모델**: `gemini-2.5-pro-001` 고정 (변경 시 ADR).
- **Cost**: Phase 1 = 자동 cost gate 없음. operator (사용자) 가 Gemini console manual monitoring.
- **Fallback matrix** (Amendment 1 — 2 row 갱신):

| 실패 유형 | 처리 |
|---|---|
| Gemini API timeout / transient 5xx | 1 retry → Claude·Codex 합의안 auto-proceed (없으면 user) |
| **Quota exhausted (Amendment 1 갱신)** | **Claude Sonnet (`claude-sonnet-4-6`) 가 final pick + 즉시 사용자 알림 + auto-proceed (no-stop)**. packet `attempts[].outcome = quota_sonnet_fallback` + `authority_transfer.final_decider = claude_sonnet` + Story §12 row `audit_result = sonnet-fallback`. 상세 = 결정 9. |
| Unauthorized / config 오류 / OAuth invalid (Plus subscription expire/cancel) | user (prerequisite issue) |
| Malformed Gemini response | 1 retry → 실패 시 user escalation |
| Repeated identical Gemini error (≥2 회 동일 packet-id 동일 pick 실패) | user escalation |
| Sonnet 도 quota / unauthorized / dual_failure | user escalation + `attempts[].outcome = dual_failure` + `fallback_unavailable = true` |

- **Authority 변동 명시**: Gemini = 최종 결정자 only when available. quota 실패 시 → Sonnet (Amendment 1). auth/transient 실패 시 → user. authority transfer 발생 시 packet log `authority_transfer.occurred: true` + `final_decider` 명시.

### 결정 6: Logging

- Story §10 FIX Ledger: `decider: gemini` 컬럼 추가 (선택).
- Story §12 신규 "Gemini Decision Log" (per-Story append-only, 7 컬럼: packet_id / trigger / options_count / gemini_pick / override? / audit_result / timestamp).
- Detailed packet artifact = `<internal-docs>/<plugin-folder>/decisions/<packet_id>.yaml`.
- Audit = 첫 5 packet scheduled self-audit (schema 검증) → 그 후 failure-driven only.

### 결정 7: Phase boundary

- Phase 1 (CFP-57) = doc-only. agent / skill / 코드 추가 없음.
- Phase 2 (별도 후속 CFP) = subagent / skill 도입 ROI 평가. 30+ packet + cost report + 사용자 명시 승인 필수.

### 결정 8: Suspend / reactivation

사용자 명시 표현 ("잠깐 끄자" 등) → session/Story 단위 일시 중단. suspend 중 새 stop point 발생 시 packet 작성 + Claude·Codex 합의 임시 proceed (없으면 user) + log `gemini_suspended`. reactivate 후 미결정 packet sequential 재처리.

### 결정 9: Sonnet quota fallback + 사용자 알림 protocol (Amendment 1)

Gemini quota exhausted 시 (Plus subscription quota 한계 도달) Claude Sonnet (`claude-sonnet-4-6`) 가 임시 final decider 역할. controller (Claude Opus 본세션) 가 `Agent` tool with `model: sonnet` 호출 — decision-packet 을 prompt 로 전달, pick + ranking + reasoning + confidence 회수.

**Sonnet 호출 prompt** (CFP-58 spec §2.3 SSOT):

```
You are acting as the Sonnet quota-fallback decider for ADR-018 Amendment 1.
Gemini Plus quota is exhausted; you make the final pick instead.

Decision packet (decision-packet-v1.1):
<packet YAML>

Output (YAML):
  pick: <option id>
  ranking: [<id>, ...]
  reasoning: <multi-paragraph>
  confidence: high | medium | low
```

응답 schema 는 packet `gemini_decision` block 과 동일 (단, 의미상 "decider pick" — Gemini 가 아닌 Sonnet, schema 변경 없이 같은 field 재활용).

**Runtime invocation 명시**: Sonnet fallback = controller 가 매 quota exhausted 시점 발화하는 runtime tool call. Phase 1 = doc-only 정책 (결정 7) 정합 — agent file / skill / 코드 추가 또는 수정 없음.

**사용자 알림 protocol** (3 trace 동시 작성):

1. **Chat message** (user-facing, controller-authored summary, ≤200 chars):
   ```
   Gemini quota exhausted. Sonnet fallback: pick=<id>, confidence=<level>. Reasoning: <controller-authored summary>. Full packet: <internal-docs path>.
   ```
2. **Story §12 row 추가**: `audit_result = sonnet-fallback` (신규 enum 값)
3. **Packet artifact full schema**: `<internal-docs>/<plugin-folder>/decisions/<packet_id>.yaml` — `attempts[].outcome: quota_sonnet_fallback` + `authority_transfer.final_decider: claude_sonnet`

알림 직후 자동 진행 (no-stop). 사용자 추후 packet review 가능.

**user override race 처리**: 알림 직후 자동 진행 동안 사용자 chat 응답 시 — 다음 irreversible action (file write / commit / PR creation) 시작 전이면 사용자 응답 우선 (Sonnet pick 폐기 + `attempts[].outcome: user_override`), 이후면 새 corrective instruction 으로 처리 (rollback 안 함).

**Sonnet 자체 실패 처리**:
- timeout / malformed: 1 retry → 실패 시 dual_failure + user escalation
- quota / unauthorized: 즉시 dual_failure + user escalation
- override_required (Claude+Codex 둘 다 reject): CFP-57 결정 3 step 6b (Codex sanity audit) 동일 적용 — sanity-PASS proceed / sanity-FAIL user

**Reasoning summary 의미**: chat message 의 reasoning = controller 가 Sonnet multi-paragraph reasoning 을 읽고 재구성한 요약 (truncation 아님). full reasoning 은 packet artifact 에 보존.

**Repeated fallback threshold**:
- 1 Story 내 N=3 회 발생 → Story §12 footer `repeated-fallback-warning: 3+` annotation + Phase 2 ROI/cost review trigger input
- 1 session 내 N=5 회 → 추가 chat 알림 (Gemini quota usage rate 검토 권고). 자동 진행 유지
- N=10 회 → escalation whitelist 의 운영 prerequisite 카테고리 진입 (사용자 stop, Plus subscription 사용량 검토 의무)

**Acceptance criteria** (CFP-58 spec §5.5 SSOT):
- AC-1: 3 trace 모두 작성 (chat + Story §12 row + packet artifact)
- AC-2: latency target — Sonnet invocation 30 초 이내 + 사용자 알림 10 초 이내
- AC-3: v1.1 schema 운영 검증 — 첫 fallback 시 신규 enum 3 값 (`quota_sonnet_fallback` / `claude_sonnet` / `sonnet-fallback`) 정확 record
- AC-4: repeated threshold (위 N=3/5/10 단계)

## 검토한 대안

### 대안 A — Scope = Trigger 1 만

거부: 사용자 stop 절감 효과 미흡. Trigger 6 root-cause 불일치 stop 잔존.

### 대안 C — 모든 substantive choice sub-step

거부: Trigger 2·3·4·5·7 본질이 "결정" 아닌 "audit/list". Codex 본래 역할 침해. quota·latency 폭증.

### 대안 D — Lane review PL verdict 까지

거부: ADR-001 대규모 재작성 cost ≫ benefit. review verdict 는 quality gate (단일 산출물 통과) 이지 옵션 선택 아님. ADR-001 review-verdict-v2 는 본 정책 적용 대상 아님 — review verdict 는 lane PL 종합, 본 decider 는 substantive choice (트리거 1/6) 만.

### 대안 — Gemini = tie-breaker only

거부: 사용자 directive "그 내용 모두를 gemini에게 전달하여 gemini가 결정한대로" 와 충돌.

### 대안 — Implementation 옵션 1 (Doc-only 영구)

거부: enforcement 약함 (Claude self-discipline). 운영 cost 데이터 없이 결정 영구화 risk.

### 대안 — Implementation 옵션 2 (즉시 subagent)

거부: premature. Phase 1 운영 evidence 없이 신규 plugin / pmo 침해 cost ≫ benefit. Codex Round 1 axis 17 D 권장 위반.

## 검토한 대안 (Amendment 1 — CFP-58)

### Amendment 1 대안 A — API key + OAuth 둘 다 지원 (precedence rule)

거부: 사용자 directive 명시적 API key 미사용. dual-path = spec 복잡도 증가, ROI 낮음.

### Amendment 1 대안 B — Sonnet 대신 Opus (controller 자체) 가 fallback decider

거부: 사용자 명시 "claude sonnet 모델". controller != decider 분리 보존 (controller = orchestration, decider = 모델 호출).

### Amendment 1 대안 C — Codex audit gate (CFP-57 기존) 유지

거부: 사용자 directive 가 명시적으로 Sonnet 지정. Codex auditor 역할 보존 (final pick 권한 임시 부여 회피).

### Amendment 1 대안 D — 사용자 escalation (Sonnet 안 부르고 user)

거부: no-stop mode 위반. 사용자 motivation 정확히 반대 — "사용자 stop 최소화".

## 결과

긍정:
- 사용자 stop 빈도 절감 (기존 Codex Round 1+2 후 사용자 결정 → Gemini 자동 결정).
- "Claude·Codex 동급 + Gemini 결정" hierarchy 가 사용자 directive 정합.
- Phase 1 doc-only — risk 낮음. agent/code 추가 없음 (ADR-009 무영향).
- Phase 2 transition = 데이터 driven.

부정:
- enforcement = Claude self-discipline (Phase 1 한정). protocol drift risk.
- paid Pro tier prerequisite — 사용자 cost 발생.
- packet 수동 작성 overhead (Phase 2 자동화 후 완화).

후속:
- 30+ decision 후 §4.1 Open Items 결정 (cost cap / Phase 2 ROI / escalation whitelist 정량 / packet schema v2 필요성).

## ADR 정합성

- ADR-001 file content 완전 무수정. scope clarification 본 ADR-018 §검토 의 대안 만 거주.
- ADR-008 — `decision-packet-v1` 신규 registry kind. MANIFEST.yaml 의 contracts list 변경 없음 (registry 는 lint scope 밖).
- ADR-009 — Phase 1 영향 없음 (agent count = 0 유지). Phase 2 시 별도 ADR (ADR-019+).
- ADR-013 + ADR-017 — 본 CFP-57 spec/plan 위치 = `<internal-docs>/wrapper/{specs,plans}/` 정합.

## 관련 파일

- `CLAUDE.md`
- `docs/inter-plugin-contracts/decision-packet-v1.md`
- `docs/inter-plugin-contracts/MANIFEST.yaml`
- `templates/story-page-structure.md`
- `docs/adr/ADR-001-review-agent-unification.md`
- `docs/adr/ADR-008-inter-plugin-contract-versioning.md`
- `docs/adr/ADR-009-wrapper-only-decomposition.md`
- `docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md`
- `docs/adr/ADR-017-skill-override-path-enforcement.md`
