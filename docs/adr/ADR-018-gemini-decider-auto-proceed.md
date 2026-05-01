---
adr_number: 18
title: Gemini Decider Auto-Proceed System (Phase 1 doc-only policy)
status: Accepted
category: Team & Process
date: 2026-05-01
related_files:
  - CLAUDE.md
  - docs/inter-plugin-contracts/decision-packet-v1.md
  - templates/story-page-structure.md
  - docs/adr/ADR-001-review-agent-unification.md
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md
  - docs/adr/ADR-009-wrapper-only-decomposition.md
  - docs/adr/ADR-013-codeforge-family-dogfood-out-policy.md
  - docs/adr/ADR-017-skill-override-path-enforcement.md
related_stories:
  - CFP-57
---

# ADR-018: Gemini Decider Auto-Proceed System (Phase 1 doc-only policy)

## 상태

Accepted (2026-05-01) — CFP-57 carrier, Phase 1 doc-only.

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

### 결정 5: 운영 정책

- Auth = `GEMINI_API_KEY` (paid Pro tier prerequisite). OAuth 비활성.
- 모델 = `gemini-2.5-pro-001` 고정. 변경 시 ADR.
- Cost = 자동 gate 없음. Phase 1 manual monitoring.
- Fallback matrix (timeout/quota/unauthorized/malformed/repeated/dual-failure) 6 row.
- Authority transfer = Gemini 실패 시 fallback 으로 임시 이관.

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

## ADR 영향

- ADR-001 file content 완전 무수정. scope clarification 본 ADR-018 §검토 의 대안 만 거주.
- ADR-008 — `decision-packet-v1` 신규 registry kind. MANIFEST.yaml 의 contracts list 변경 없음 (registry 는 lint scope 밖).
- ADR-009 — Phase 1 영향 없음 (agent count = 0 유지). Phase 2 시 별도 ADR (ADR-019+).
- ADR-013 + ADR-017 — 본 CFP-57 spec/plan 위치 = `<internal-docs>/wrapper/{specs,plans}/` 정합.
