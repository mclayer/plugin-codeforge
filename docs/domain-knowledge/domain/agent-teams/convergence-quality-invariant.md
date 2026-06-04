---
kind: domain_fact
type: domain-knowledge
area: agent-teams
topic_slug: convergence-quality-invariant
title: debate-protocol-v1 convergence_quality_invariant — 3-tuple semantic 합의 품질 invariant
status: Active
tags:
  - agent-teams
  - debate-protocol-v1
  - convergence-quality
  - anti-sycophancy
  - adversarial
related_adrs:
  - ADR-059  # debate-protocol-v1 carrier — Amendment 2 (CFP-582 §결정 8) 가 본 invariant 도입
  - ADR-052  # Codex Proactive Check touchpoints — Touchpoint #2 carry-over 와 동등 reasoning carryover 영역
related_files:
  - docs/inter-plugin-contracts/debate-protocol-v1.md
  - docs/adr/ADR-059-debate-protocol-v1.md
  - docs/adr/ADR-052-codex-proactive-check-touchpoints.md
  - docs/domain-knowledge/domain/agent-teams/agent-teams-platform-capability.md
related_stories:
  - CFP-391  # debate-protocol-v1 v1.0 도입 (Adversarial 패턴 자동 발동)
  - CFP-582  # 본 invariant 도입 carrier (Wave 4)
created: 2026-05-13
updated: 2026-05-13
authors:
  - DomainAgent (CFP-582 Wave 4)
---

# debate-protocol-v1 convergence_quality_invariant — 3-tuple semantic 합의 품질 invariant

## Summary

debate-protocol-v1 v1.2 (CFP-582 / ADR-059 Amendment 2 §결정 8) 가 도입한 **convergence_quality_invariant** = multi-round adversarial debate 의 매 라운드 발화에서 의무 검증되는 3-tuple semantic signal. 기존 anti-sycophancy 메커니즘 (remaining_disagreements / role_lock / topic anchor prepend / POSITION_CHANGE) 이 syntactic / structural level 의 합의 검증을 담당했다면, 본 invariant 는 **발화 내용의 semantic depth** 를 검증한다. MCT-150 retro (sycophancy 사례 evidence) 의 systemic 차단 forcing function.

## Pattern

매 debate round 발화 (Claude worker / Codex worker / PL synthesis) 는 다음 3-tuple 모두 만족해야 한다:

| Field (stable base name) | 의미 | Measurable signal | 적용 round 영역 |
|---|---|---|---|
| `counterargument_present` | 직전 라운드 반대 worker 의 핵심 반론을 인용 + 자기 입장에서 explicit 응답 | round 본문 안에 `[COUNTERARGUMENT]` marker block 1+ 개 + 직전 라운드 worker 발화 anchor reference | round 1+ (round 0 statement 는 면제) |
| `alternative_proposed` | 반대 worker 가 제시한 대안을 reject (rebut + 사유) 또는 자기 대안 발의 | round 본문 안에 `[ALTERNATIVE_PROPOSED]` marker block 1+ 개 (count = `alternative_proposed_count`) | round 1+ |
| `debate_purpose_statement_present` | 본 라운드 발화 목적 (어느 쟁점에 합의 / 어디서 입장 유지 / 무엇이 미해결) 1 문장 명문화 | round 본문 안에 `[DEBATE_PURPOSE_STATEMENT]` marker block 1 개 (단일 라인) | 모든 round (round 0 statement 포함) |

위 base name 은 4-SSOT (CLAUDE.md L222 / ADR-059 §결정 8 + §3.1 #6 / debate-protocol-v1 v1.2 §2.2 + §2.3 / 본 page) 공통 stable name. scope suffix 변형 — per-worker per-round: base 자체 + `_count` (count field). PL writes per-round: `_both_workers` / `_cumulative_count` / `_present_round_0_inherited`. Termination: `_all_rounds_both_workers` / `_cumulative_count` (>=1) / `_present_round_0`.

3-tuple AND 검증 = 모두 true 일 때만 라운드 발화 유효. 단 1 개라도 false = `convergence_invariant_violation` flag set + PL force_continue 강제.

## Usage

debate-protocol-v1 v1.2 SSOT 의 `convergence_quality_invariant` block (registry yaml `Round payload` 섹션 추가 schema) 가 정확한 marker syntax / PL 검증 알고리즘 / FIX integration 흐름을 정의한다. 본 page 는 의미·관계·WHY 중심.

PL 검증 흐름:
1. 각 round 종료 직후 PL 이 3-tuple 추출 (marker grep 기반)
2. 1+ false 시 → `convergence_invariant_violation: true` + `force_continue: true` round payload field set → 발화 worker 에 adversarial prompt 재주입 (해당 missing field 명시)
3. force_continue 발동 round 는 min 3 / max 5 round counter 에 미포함 (재발화 동일 round 번호 유지)
4. Story §9 transcript section append 시 `[convergence_invariant_violation]` marker 가 verbatim 보존 — fact-check 가능

## 정의

**convergence_quality_invariant** = adversarial debate 의 단순 round-count 합의가 아닌 **발화 내용 자체의 합의 품질** 을 보장하는 3-tuple semantic invariant. anti-sycophancy 영역 SSOT 확장 layer (기존 syntactic layer 와 orthogonal).

3 marker pattern (정확한 syntax 의무):
- `[COUNTERARGUMENT]` — 반대 worker 핵심 반론 인용 + 응답 block 시작 marker
- `[ALTERNATIVE_PROPOSED]` — 대안 발의 또는 대안 reject 사유 block 시작 marker
- `[DEBATE_PURPOSE_STATEMENT]` — 라운드 발화 목적 단일 라인 marker

대소문자 정확히 일치 의무 (mechanical lint Phase 2 scope).

## 컨텍스트

MCT-150 retro evidence: AI worker 들이 multi-round debate 안에서 round-count min 3 미달 시점에서 "동의합니다 / 합의 도달" 발화로 round 마감 → 실제 입장 변경 reasoning trail 부재 (sycophancy). 기존 anti-sycophancy 4 메커니즘 (remaining_disagreements 채움 강제 / role_lock / topic anchor verbatim prepend / POSITION_CHANGE 라벨 의무) 이 **syntactic level** 차단 — round-count, role 일관성, topic drift, position-change marker 자체는 검증.

그러나 syntactic level 통과 발화도 **semantic depth 부재** 가능 (반론 인용 없이 자기 입장 재진술 / 대안 미발의 + reject reasoning 부재 / 라운드 목적 모호). 본 invariant 가 semantic level forcing function 으로 보강.

ADR-059 Amendment 2 §결정 8 carrier — CFP-582 Wave 4 의 DesignLane blanket debate 도입과 분리된 anti-sycophancy 강화 축. MCT-150 외 RETRO 다수 evidence 가 systemic super-class 시그널 — CFP-582 가 lateral expansion 책임.

## 핵심 platform API

본 invariant 는 debate-protocol-v1 registry yaml level schema 영역이며 platform API (TeamCreate / SendMessage / TaskCreate) 와 직접 binding 없음. PL 의 round payload 처리 알고리즘 layer 에서 mechanical 검증.

| Surface | 의미 | 호출 시점 |
|---|---|---|
| Round payload `convergence_quality_invariant` block (yaml) | 3-tuple bool field + 3 marker count + `convergence_invariant_violation` flag | 매 round 발화 직후 PL 자동 채움 |
| PL `force_continue` 발동 | invariant false 시 동일 round 재발화 강제 (round counter 미증가) | 매 round 검증 직후 |
| Story §9 transcript `[convergence_invariant_violation]` 보존 | 위반 round 발화 verbatim + violation marker append | transcript section 작성 시 |
| `scripts/check_debate_convergence_quality.py` (Phase 2, 별 Story) | mechanical lint — 3 marker presence + grep based AND 검증 | PR diff 안 Story §9 transcript section 검증 |

## codeforge re-entrancy 제약 3종 (정책 SSOT)

본 invariant 는 re-entrancy 제약 직접 영향 없음. env=1 (agent teams enabled) / env=0 (default subagent context) 양쪽 동일 적용 — env=0 polyfill round-trip 시에도 PL 이 each round 입력 후 3-tuple 검증 의무.

## Default subagent context 와의 분기

| 항목 | env=0 polyfill | env=1 SendMessage continuous dialog |
|---|---|---|
| 3-tuple marker 작성 책무 | worker subagent system prompt 안 명시 + each round one-shot spawn 시 prompt 안 verbatim 의무 | worker teammate system prompt 안 명시 + SendMessage payload 안 verbatim |
| PL 검증 시점 | each round one-shot return 직후 inline grep | each round SendMessage receive 직후 PL teammate context 안 grep |
| force_continue 발동 비용 | 토큰 비용 increment 1 round 추가 spawn | SendMessage round-trip 1회 추가 |
| Story §9 transcript 보존 | 동일 (PL self-write) | 동일 (PL self-write) |

## /resume 후 in-process teammate 미복원 risk

본 invariant 는 round payload 영역 — `/resume` 후 in-flight teammate 미복원 시 동일 round 발화 재현 불가 → debate 자체 abort 및 새 debate 시작 가정. 본 invariant 별도 risk 추가 없음. ADR-035 §결정 D2 Phase-scoped sequential team 정책 정합.

## 5 권장 패턴 매핑

본 invariant 는 5 권장 패턴 중 **Adversarial** 패턴 영역만 적용. Specialization / Parallelization / Cross-layer / Escalation 패턴에는 미적용 (단순 발화 / dispatch 영역, semantic 합의 검증 불필요).

## 기존 anti-sycophancy 메커니즘과의 관계

본 invariant 는 기존 메커니즘과 **orthogonal** 관계 — 별도 layer 보강이며 대체 / 통합 아님. 4 메커니즘 + 본 invariant = 5 layer 직교 합의 품질 보장 stack.

| 기존 메커니즘 | Layer | 검증 대상 | 본 invariant 와의 관계 |
|---|---|---|---|
| `remaining_disagreements` 채움 강제 | syntactic | round payload 필드 존재 + 비어있지 않음 (round < 3 시) | orthogonal — disagreement list 채움 자체는 검증, 채워진 내용 semantic depth 는 본 invariant 책임 |
| role_lock + 반대 입장 강제 prompt | syntactic | worker 가 round 중 자기 role 유지 + 반대 입장 prompt 주입 | orthogonal — role 일관성 검증, role 안 발화 semantic depth 는 본 invariant 책임 |
| topic anchor verbatim prepend (round 0 statement) | syntactic | round N 입력 최상단 verbatim 포함 (U-shaped attention bias) | orthogonal — topic drift 차단, topic 안 합의 품질 은 본 invariant 책임 |
| `POSITION_CHANGE` 라벨 의무 (입장 변경 시) | syntactic | 입장 변경 발생 시 명시 marker 부착 | orthogonal — 변경 fact 자체 marker, 변경 reasoning depth 는 본 invariant `[COUNTERARGUMENT]` + `[ALTERNATIVE_PROPOSED]` 가 담당 |

5 layer AND 검증 = 모두 통과 시 round 발화 정상. 기존 4 layer 통과 + 본 invariant false 시 → 본 invariant force_continue 만 발동 (기존 layer 별도 trigger 아님).

## mechanical lint (Phase 2, 별 Story)

본 invariant 의 mechanical enforcement = Phase 2 carrier (별 Story 후속) — `scripts/check_debate_convergence_quality.py` 신설:
- Story §9 transcript section 안 `### Debate transcript: <anchor_id>` block 추출
- 각 round 발화 안 3 marker (`[COUNTERARGUMENT]` / `[ALTERNATIVE_PROPOSED]` / `[DEBATE_PURPOSE_STATEMENT]`) presence + count 검증
- false detect 시 PR warning (evidence-checks-registry-v1.1 entry 등록 — tier `warning` 첫 도입)
- bypass label = `hotfix-bypass:debate-convergence-quality` (ADR-024 Amendment 3 정합)

본 page 시점에서는 PL inline 검증 단계 — round payload 안 self-report bool field + Story §9 transcript verbatim marker 만 보장. lint script 미존재 (별 Story carrier).

## 외부 reference 정합

본 invariant 의 inspiration = Anthropic agent design literature 의 adversarial debate 영역 + multi-agent reasoning trail integrity 연구 + MCT-150 codeforge family 내부 retro evidence. 외부 verbatim transcribe 아님 — codeforge 내부 정책 SSOT. 외부 docs link 미포함.

## 관련 ADR / Story / 후속 작업

- **Carrier ADR**: ADR-059 Amendment 2 §결정 8 (CFP-582 Wave 4) — 본 invariant schema 정의 + force_continue 정책
- **Carrier Story**: CFP-582 (Wave 4 Phase 1 — 본 page 도입)
- **의존 ADR**: ADR-052 (Codex Proactive Check Touchpoint #2 reasoning carryover 영역 동등 SSOT — verdict packet field marker 의무 영역 유사)
- **의존 contract**: debate-protocol-v1 v1.2 (registry yaml schema), review-verdict-v4 v4.4 (PL synthesis 영역 marker 의무 정합 영역)
- **후속**:
  - Phase 2 carrier (별 Story) — `scripts/check_debate_convergence_quality.py` mechanical lint 신설 + evidence-checks-registry-v1.1 entry 등록 (warning tier 첫 도입)
  - 후속 carrier — `[POSITION_CHANGE]` 라벨 의무와 본 invariant 의 통합 review (orthogonal vs convergent layer 결정 재방문)

## 핵심 규칙

1. **3-tuple AND 검증** — `counterargument_present` + `alternative_proposed` (count >= 1) + `debate_purpose_statement_present` 3 모두 true 일 때만 round 발화 유효. 1 false = `convergence_invariant_violation` flag set + force_continue 강제 (동일 round 재발화). PL scope variant — per-round `*_both_workers` / termination `*_all_rounds_both_workers` (registry §2.2 + §2.3 정합).
2. **3 marker 정확한 syntax 의무** — `[COUNTERARGUMENT]` / `[ALTERNATIVE_PROPOSED]` / `[DEBATE_PURPOSE_STATEMENT]` 대소문자 정확히 일치. round 본문 안 marker block 으로 명시. PL 검증 + mechanical lint (Phase 2) 양쪽 동일 syntax 의존.
3. **PL 검증 책무** — Orchestrator / lane PL 이 each round 발화 직후 3-tuple 추출 + `convergence_invariant_violation` flag set 책임. worker self-report 의 sycophancy 우회 차단.
4. **force_continue 발동 시 round counter 미증가** — invariant false 시 동일 round 재발화. min 3 / max 5 round 정책 영향 없음 (재발화 = round counter 변화 없음).
5. **Story §9 transcript verbatim 보존** — `[convergence_invariant_violation]` marker 포함 발화 verbatim transcript 보존 의무. fact-check / retro / sibling Story reference 가능.
6. **기존 anti-sycophancy 메커니즘과 orthogonal** — 4 syntactic layer (remaining_disagreements / role_lock / topic anchor / POSITION_CHANGE) 와 본 semantic layer 는 별도 검증 layer. 본 invariant false 만 force_continue 발동 — 기존 layer 별도 trigger 아님.
7. **lateral expansion 의무** — DesignReview / DesignLane blanket / Requirements / CodeReview / SecurityTest 모든 debate 영역에 동일 적용. Adversarial 패턴 lane-agnostic invariant.

## 경계

**codeforge 책임 영역 (in scope)**:
- debate-protocol-v1 registry yaml `convergence_quality_invariant` block schema (3-tuple field + marker count + violation flag)
- PL 검증 알고리즘 (round payload 채움 + force_continue 발동)
- Story §9 transcript marker verbatim 보존
- ADR-059 Amendment 2 §결정 8 carrier (정책 SSOT)
- 3 marker syntax 의무 (대소문자 정확 일치)

**AI worker 책임 영역 (out of scope)**:
- 3 marker block 작성 의무 (worker system prompt 안 명시 — 매 round 발화 시 의무 포함)
- semantic depth 실제 충족 (PL 은 marker presence 만 검증 — depth 실제 quality 는 worker reasoning trail 영역)
- counterargument 인용 정확성 (worker 가 직전 round verbatim 인용 책무)

**Phase 2 carrier 책임 영역 (별 Story)**:
- mechanical lint script (`scripts/check_debate_convergence_quality.py`)
- evidence-checks-registry-v1.1 entry 등록 (warning tier)
- `hotfix-bypass:debate-convergence-quality` label 도입
- CI workflow integration

## 변경 이력

| 날짜 | 변경 | Carrier |
|---|---|---|
| 2026-05-13 | 초기 작성 — debate-protocol-v1 v1.2 convergence_quality_invariant SSOT 도입. 3-tuple semantic invariant 정의 + PL 검증 책무 + 기존 anti-sycophancy 4 메커니즘 과 orthogonal 관계 명시 + Phase 2 mechanical lint 후속 carrier 예약. ADR-059 Amendment 2 §결정 8 carrier. | CFP-582 (Wave 4) |

## 참조

- [ADR-059 Amendment 2 §결정 8](../../../../archive/adr/ADR-059-debate-protocol-v1.md)
- [debate-protocol-v1 v1.2 registry yaml](../../../inter-plugin-contracts/debate-protocol-v1.md)
- [ADR-052 Codex Proactive Check Touchpoint #2](../../../../archive/adr/ADR-052-codex-proactive-check-touchpoints.md)
- [agent-teams-platform-capability](agent-teams-platform-capability.md)
