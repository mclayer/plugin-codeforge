---
kind: domain_fact
type: domain-knowledge
area: governance-principle
topic_slug: decision-style
title: codeforge 결정 원칙 — 결정 내용·결정 제시·적용 속도 행동 패턴 SSOT
status: Active
tags:
  - decision-principle
  - forbid-list
  - derived-default
  - parallel-default
  - top-down-ratchet
  - adr-064
related_adrs:
  - ADR-039  # subagent default (Trace 4 모체)
  - ADR-052  # Codex proactive check (CFP-446 Amendment 2 target)
  - ADR-054  # doc-only fast-path (full-lane 강제 anchor)
  - ADR-058  # sunset criteria mandate (ratchet 차단)
  - ADR-060  # evidence-enforceable framework (CFP-449 진입 base)
  - ADR-063  # marketplace atomic invariant (version bump 적용)
  - ADR-064  # 본 페이지의 normative carrier
related_stories:
  - CFP-445
  - CFP-446
  - CFP-449
created: 2026-05-12
updated: 2026-05-12
---

# codeforge 결정 원칙 — 행동 패턴 + 적용 사례 SSOT

## 정의

**codeforge 결정 원칙 (decision-style)** 은 [ADR-064](../../../adr/ADR-064-decision-principle-mandate.md) 의 결정 원칙 normative SSOT 를 행동 패턴 + 운영 사례로 풀어낸 SSOT 다. ADR-064 가 normative 룰 자체를 정의하면, 본 페이지는 그 룰을 실행할 때의 패턴 / 예시 / 운영 사례 / cross-ref 를 정리한다.

본 페이지는 3 갈래 (Trace) 의 통합 SSOT 다:

- **Trace 1 — 결정 내용**: 4 어휘 운영 + forbid-list dictionary + CFP scope unitary
- **Trace 2 — 결정 제시**: derived default / 옵션 dump 차단 / 식별자 사전 요약 / 질문 brevity / `AskUserQuestion` 범위
- **Trace 4 — 적용 속도**: subagent parallel default + Epic lifecycle 압축 KPI + sequential 강제 3 사유

`decision-style` 의 정의 외연은 codeforge 가 결정 제안 시점 (proposing-time) 에 발생시키는 모든 결정 행동 — 결정 내용 자체 (Trace 1) / 결정을 사용자에게 제시하는 방식 (Trace 2) / 결정을 실행에 옮기는 속도 (Trace 4) — 이 3 종 행동의 통합 행동 패턴이다.

## 컨텍스트

본 SSOT 정립 동인은 사용자 directive 3 건 누적 (2026-05-11 ~ 2026-05-12) 이다:

1. **2026-05-11 directive 1** — "best-effort / broad coverage / full-scope / active amendment 4 어휘를 결정 운영에 적용하라" (Trace 1 원천).
2. **2026-05-11 directive 2** — "식별자만 던지지 말고 핵심 요약을 대화 내에 먼저 제시 후 질문하라" (Trace 2 원천 — memory `feedback_explain_before_ask` 의 normative 승격 요청).
3. **2026-05-12 directive 3** — "당연한 질문은 묻지 말고 derived default 로 진행하라. `AskUserQuestion` 은 진짜 가치 판단·미공개 컨텍스트 영역만 발화" (Trace 2 룰 1·5 원천 — memory `feedback_question_quality` 의 normative 승격 요청).

발생 동인 3 종:

- **의사결정 menu 의 normative 부재** — 4 어휘 운영 패턴 / forbid-list dictionary / CFP scope unitary 룰이 codeforge SSOT 어디에도 정립되지 않은 상태에서 ad-hoc 사용자 발화에 의존.
- **사용자 대화 표면 UX gap** — Orchestrator 가 식별자 dump / 옵션 dump / 당연한 질문 패턴을 반복 발생시켜 사용자 인지 부담 누적.
- **Epic open→close lifecycle 최적화 필요** — multi-task spawn 시점에 sequential bias 가 의도치 않게 발생, Amdahl's Law speedup curve 의 parallel portion P 를 축소 → Epic lifecycle 압축 기회 손실.

본 페이지는 위 3 directive 의 normative 승격 결과물 — memory ephemeral 한계 (single-session scope + consumer 비전파) 를 SSOT 영구화로 해소.

## 핵심 규칙

### Trace 1 — 결정 내용

#### 4 어휘 운영적 정의 (ADR-064 §결정 1)

| 어휘 | 운영 패턴 |
|---|---|
| best-effort | 결정 제안 시점에 도달 가능한 최선의 안 채택. "추후 보완" 핑계로 약화 옵션 채택 = 본 원칙 위반 |
| broad coverage | 결정 menu 작성 시점에 side effect / edge case / 외연 영역까지 후보 포함. AWS Well-Architected 5 pillar review 패턴 |
| full-scope | 결정 scope 가 도메인 전체 즉시 적용. partial / opt-in 분기 차단 |
| active amendment | 강화 방향 amendment 적극 발의. 약화 방향은 ADR-058 §결정 5 sunset_justification 의무로 차단 (top-down ratchet) |

#### Forbid-list dictionary (ADR-064 §결정 2)

다음 8 어휘를 결정 제안 시점 menu 에서 제거 의무.

| 어휘 | 운영 사례 |
|---|---|
| 임시 | "임시 패치", "임시 결정" — 사후 audit 의존 패턴 |
| 단계적 | "단계적 도입" — CFP scope unitary 룰 위반 |
| 일단 | "일단 도입 후 보완" — best-effort 위반 |
| 우선 (시간) | "임시 결정 우선 채택 후 보완" — best-effort 위반. 일반 우선순위 (1순위 priority) 는 외연 |
| 잠정 | "잠정 결정" — active amendment 의무 위반 |
| 가벼운 | "가벼운 버전" — full-scope 위반 |
| minimal viable | "minimal viable 안" — full-scope 위반 (단, MVP 자체는 product domain 어휘 — proposing-time 시 결정 후보 영역에서만 forbid) |
| quick win | "quick win 옵션" — broad coverage 위반 |

**lint scope** ([CFP-449](https://github.com/mclayer/plugin-codeforge/issues/449) warning tier, ADR-060 §결정 5 정합):
- `docs/adr/**`
- `docs/change-plans/**`
- `CLAUDE.md`
- `docs/orchestrator-playbook.md`
- `templates/**`

**Exempt channel**: `hotfix-bypass:decision-principle-vocab` label (ADR-024 Amendment 3 정합, audit-trailed exception channel).

**False positive 회피**: dictionary 본문 영역 또는 외부 인용 (사용자 발화 verbatim) 영역에서 본 어휘 등장은 외연 허용.

#### 결정 시점 외연

본 원칙은 proposing-time (결정 제안 시점) 한정. 사후 운영 영역 (deployment 후 incident response / hotfix 발화 / Live touching emergency) 은 외연 — §"경계" out-of-scope 참조.

#### Top-down ratchet (CFP scope unitary 룰, ADR-064 §결정 5)

한 CFP 안 "경량 → full" 단계 채택 금지. 별개 CFP 분리는 허용.

| 허용 패턴 | 차단 패턴 |
|---|---|
| `CFP-N v0.1` + `CFP-N+1 v1.0` 가 독립 brainstorm + 독립 Story + 독립 PR | "본 CFP 의 v0.1 만 도입, v1.0 은 후속 작업" 식 단계 분기 |
| Implementation cost 분해 = PMOAgent vertical slice (한 CFP 안 sub-task) | "비용 부담 회피용 가벼운 prototype 후 본격" 식 분기 |
| Epic 분해 = 여러 child Story (각 독립 brainstorm + Story) | 단일 Story 안 "Phase 1 부분 적용 후 Phase 2 본격" 식 분기 |

### Trace 2 — 결정 제시

#### Derived default 기본값 적용 (ADR-064 §결정 3 룰 1)

Orchestrator 가 `AskUserQuestion` 발화 의도 시 다음 분기:

```
컨텍스트 (사용자 명시 + memory + Story file + ADR 인용) 로
합리적 default 도출 가능?
  YES → AskUserQuestion 생략. derived default 직접 declare + 결과 보고
  NO  → AskUserQuestion 발화 (단 §결정 3 룰 5 범위 적용)
```

**예외 영역** (derived default 도출 회피 의무):
- 가치 판단 (사용자 선호도 / 가치 판단 기준 / 도메인 의도)
- 미공개 컨텍스트 (Orchestrator 가 알 수 없는 사용자 측 정보 — 외부 시스템 상태 / 사용자 일정 등)

#### 옵션 dump 금지 (ADR-064 §결정 3 룰 2)

| 차단 패턴 | 허용 패턴 |
|---|---|
| "A / B / C / D / E / F 6 옵션 중 선택해 주세요" | "권장 = A (사유 1 문장). 대안 = B (사유 1 문장)" |
| 식별자 (ADR / CFP / 파일 path) 사전 요약 없이 식별자 dump | 식별자 + 핵심 요약 1 문장 사전 제시 후 진입 |
| jargon 5+ 단어 한 turn 안 발화 | 5+ jargon 시 brainstorm Phase 0 영역으로 격상 |

3+ 후보는 brainstorm 영역 (별도 Phase 0).

#### 식별자 사전 요약 (ADR-064 §결정 3 룰 3)

memory `feedback_explain_before_ask` 의 normative 승격. 사용자 발화 directive 2 (2026-05-12) 의 직접 해소.

| 패턴 | 허용/차단 |
|---|---|
| "ADR-064 적용해" (요약 부재) | 차단 — 식별자 dump |
| "ADR-064 (결정 원칙 mandate — forbid-list 8 어휘 + parallel default) 적용해" | 허용 — 식별자 + 1 문장 요약 |
| "CFP-446 (Codex pre-review iterative reformulation, ADR-052 Amendment 2) 진행해" | 허용 |

#### `AskUserQuestion` 진짜 가치 판단 한정 (ADR-064 §결정 3 룰 5)

본 도구 발화는 2 종 한정:

- 가치 판단 영역 (룰 1 예외 영역과 동일)
- 미공개 컨텍스트 영역

derived default 도출 가능 영역에서 `AskUserQuestion` 발화 = ADR-064 위반.

#### 질문 brevity (ADR-064 §결정 3 룰 4)

- 질문 = 1 문장 단위
- 다중 질문 시 numbered list (최대 3 항목)
- 컨텍스트 길이 < 핵심 질문 길이 유지

memory `feedback_question_quality` 의 normative 승격.

### Trace 4 — 적용 속도

#### Subagent 병렬 default (ADR-064 §결정 4)

Orchestrator multi-task spawn 결정 시:

```
Multi-task spawn (2+ independent task)?
  YES → Sequential 강제 3 사유 평가
    state dependency? YES → sequential
    shared resource? YES → sequential
    ordering invariant? YES → sequential
    3 사유 모두 NO → DEFAULT = PARALLEL (단일 메시지 다중 Agent tool call)
  NO → 단일 spawn
```

Sequential 선택 시 spawn prompt 또는 commit message 에 사유 1 종 명시 의무. ADR-039 §결정 7 `policy_violation_subdecision` 결정 영역 확장.

본 룰은 ADR-039 + Amdahl's Law + Critical Path Method + MapReduce shuffle dependency 표준 패턴 정합.

#### Sequential 강제 3 사유 dictionary

| 사유 | 운영 사례 |
|---|---|
| state dependency | RequirementsPL §6 외부 사례 조사 → §5 확장 요구사항 합성. ArchitectAgent §3 ADR 결정 → §7 설계 서사 |
| shared resource | 동일 file (예: `CLAUDE.md`) write 충돌 / 동일 GitHub label 변경 / 동일 branch commit / ADR 번호 sequential append |
| ordering invariant | FIX Ledger row append (시간 순) / ADR-RESERVATION row append (번호 순) / commit chain |

#### Epic lifecycle 측정 (open→close KPI)

Trace 4 measurable signal:

- **데이터 출처**: `EPIC-RESULTS-<KEY>.md` artifact frontmatter `opened_at` / `closed_at` timestamp delta (현재 `templates/epic-results.md` frontmatter 에 두 field 부재 — CFP-β 가 PMOAgent owner path 에 field 신설 의무)
- **Dashboard 구축**: 본 carrier 외연 — CFP-β 별도 follow-up (frontmatter field 신설 + dashboard 구축 일체)
- **Baseline / target 정의**: dashboard 구축 후 evidence-enforceable framework (ADR-060) 점진 승격 — warning → blocking-on-pr → blocking-on-merge

본 KPI 는 외부 분산 시스템 영역의 throughput metric 와 정합 — Amdahl's Law speedup curve 가 이론적 anchor.

#### 외부 선행 사례

| 사례 | 패턴 | 본 SSOT 와의 관계 |
|---|---|---|
| Amdahl's Law | speedup = 1 / ((1-P) + P/N) | parallel default 의 이론적 anchor — sequential bias 가 P 를 의도치 않게 축소 |
| Critical Path Method (CPM) | DAG longest path = lifecycle 하한 | Epic lifecycle = lane spawn DAG critical path. parallel default 적용 시 non-critical path 압축 |
| MapReduce / Spark shuffle dependency | shuffle 시에만 sequential | sequential 강제 3 사유 dictionary 외부 선행 사례 |

### 적용 사례 (운영 사례)

#### Self-application — 본 Story (CFP-445) 자체

본 Story 자체가 결정 원칙 self-application:

- §1 사용자 directive 4 회 누적 = normative SSOT 정립 동인 (memory ephemeral 한계 해소)
- §3 RequirementsPL §2-§6 ↔ §7 ArchitectPL §7-§11 = state dependency = sequential (lane 진행 자체)
- 3 SubAgent (CodebaseMapper / Refactor / TestContractArch) spawn = parallel (state dependency 부재)
- Architect §7 → DesignReview = state dependency = sequential
- CFP-446 + CFP-449 = state dependency 부재 = parallel-eligible sibling Story (본 Story merge 후 동시 진행 가능)

#### 위반 사례 차단 — Phase 0 brainstorming

본 Story 직전 brainstorming 영역에서 발생한 옵션 dump 사례:

| 위반 | 차단 패턴 |
|---|---|
| "옵션 A / B / C / D / E / F 6 종 제시" | 권장 1 안 + 대안 1 안 (최대 2) — 3+ 후보는 Phase 0 별도 |
| "ADR-039 / ADR-058 / ADR-060 / ADR-052 / ADR-054 식별자 dump" | 각 식별자 + 1 문장 요약 사전 제시 |
| "임시로 도입 후 본격 적용" (verbatim 인용 — dictionary 외연 영역) | forbid-list dictionary 적용 — menu 자체에서 제거 |

본 사례는 `feedback_explain_before_ask` + `feedback_question_quality` memory entry 의 normative 승격 동인.

## 경계

### In-scope (본 SSOT 적용 영역)

- **proposing-time 결정 menu** — codeforge 가 결정 제안 시점 (brainstorming Phase 0 / ADR 결정 작성 / Change Plan §3 작성 / Story §7 설계 서사 작성 / Orchestrator multi-task spawn 결정 / `AskUserQuestion` 발화 결정 등) 에 발생시키는 모든 결정 행동.
- **governance carrier scope** — wrapper + 6 lane plugin + consumer overlay 가 codeforge 정책 framework 안에서 발생시키는 결정 행동 일체.

### Out-of-scope (본 SSOT 적용 외 영역)

- **사후 운영 emergency channel** — deployment 후 incident response / 운영 장애 hotfix / Live touching emergency 영역. 본 결정 원칙은 proposing-time 한정이며, 사후 emergency 채널은 ADR-058 `is_transitional: true` 안전망 / `hotfix-bypass:*` label family (ADR-024 Amendment 3) / Hotfix playbook (`docs/hotfix-playbook.md`) 가 owner.
- **ADR-058 안전망 ADR 영역** — `is_transitional: true` 선언 ADR 의 안전망 적용 영역. 본 원칙의 4 어휘 운영 + forbid-list 는 ADR-058 §해소 기준 충족 후 ratchet 가능, 안전망 상태 자체는 외연.
- **Hotfix-bypass label family** — `hotfix-bypass:*` label 부착 PR 은 본 원칙 lint advisory 면제 (per-entry namespace, audit-trailed exception channel — ADR-060 §결정 4 정합).
- **Live touching emergency** — Live system (DB primary / production deploy / payment system 등) touching 영역의 emergency rollback / kill-switch 발화. ADR-014 + ADR-030 + LiveOps / LiveOrdering SubAgent SSOT 영역.
- **Product domain MVP 어휘** — proposing-time 결정 후보 영역 외 product domain 영역의 MVP 어휘는 본 forbid-list 외연.

## 관련 ADR

- [ADR-039](../../../adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — subagent default. Trace 4 의 모체 — multi-task spawn 시 parallel default 룰은 ADR-039 §결정 7 `policy_violace_subdecision` 결정 영역의 자연 확장.
- [ADR-058](../../../adr/ADR-058-adr-sunset-criteria-mandate.md) — ADR 해소 기준 mandate. `is_transitional: true` 안전망 외연 분리 + Trace 1 의 top-down ratchet active amendment 원칙 차단 forcing function (§결정 5 `sunset_justification`).
- [ADR-060](../../../adr/ADR-060-evidence-enforceable-promotion-framework.md) — evidence-enforceable framework. CFP-449 carrier 가 본 SSOT 의 forbid-list lint 를 4-tier (warning → blocking-on-pr → blocking-on-merge → hotfix-bypass) 점진 승격 framework 안으로 진입시키는 base.
- [ADR-052](../../../adr/ADR-052-codex-proactive-check-touchpoints.md) — Codex proactive check. CFP-446 carrier 가 본 SSOT 의 Trace 2 룰 (식별자 사전 요약 + 옵션 dump 차단) 을 touchpoint #1 iterative reformulation pre-review 영역에 적용.
- [ADR-054](../../../adr/ADR-054-doc-only-story-fast-path.md) — doc-only fast-path. CFP scope unitary 룰의 full-lane 강제 근거 — 신규 ADR 도입 Story = full-lane 의무 (모호 시 full-lane 안전 방향).
- [ADR-064](../../../adr/ADR-064-decision-principle-mandate.md) — 결정 원칙 mandate. 본 페이지의 normative carrier.
- [ADR-063](../../../adr/ADR-063-marketplace-atomic-invariant.md) — marketplace atomic invariant. version bump 정합 — codeforge family 7 plugin sibling sync 시 본 SSOT 의 active amendment 룰 (강화 방향 amendment) 직접 적용.

## 변경 이력

- **2026-05-12** — 신설 (CFP-445 carrier, ADR-064). Trace 1+2+4 normative SSOT 정립. 사용자 directive 3 건 누적 (2026-05-11 ~ 2026-05-12) 의 memory ephemeral 한계 해소 — SSOT 영구화. DesignReviewPL Iter 2 FIX (T6-F01/F02/F03 + DR-F001/F002) 반영 후 Iter 3 doc-section-schema 6 필수 섹션 (정의 / 컨텍스트 / 핵심 규칙 / 경계 / 관련 ADR / 변경 이력) 정합 — content 손실 0, re-structure only.
