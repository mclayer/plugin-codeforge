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

## Summary

[ADR-064](../../../adr/ADR-064-decision-principle-mandate.md) 의 결정 원칙 normative SSOT 를 행동 패턴 + 운영 사례로 풀어낸 SSOT. ADR-064 가 normative 룰 자체를 정의하면, 본 페이지는 그 룰을 실행할 때의 패턴 / 예시 / 운영 사례 / cross-ref 를 정리한다.

본 페이지는 다음 3 갈래로 구성:

- §1 결정 내용 (Trace 1) — 4 어휘 운영 + forbid-list dictionary + CFP scope unitary
- §2 결정 제시 (Trace 2) — derived default / 옵션 dump 차단 / 식별자 사전 요약 / 질문 brevity / `AskUserQuestion` 범위
- §3 적용 속도 (Trace 4) — subagent parallel default + Epic lifecycle 압축 KPI + sequential 강제 3 사유

## §1. 결정 내용 (Trace 1)

### 4 어휘 운영적 정의 — ADR-064 §결정 1

| 어휘 | 운영 패턴 |
|---|---|
| best-effort | 결정 제안 시점에 도달 가능한 최선의 안 채택. "추후 보완" 핑계로 약화 옵션 채택 = 본 원칙 위반 |
| broad coverage | 결정 menu 작성 시점에 side effect / edge case / 외연 영역까지 후보 포함. AWS Well-Architected 5 pillar review 패턴 |
| full-scope | 결정 scope 가 도메인 전체 즉시 적용. partial / opt-in 분기 차단 |
| active amendment | 강화 방향 amendment 적극 발의. 약화 방향은 ADR-058 §결정 5 sunset_justification 의무로 차단 (top-down ratchet) |

### Forbid-list dictionary — ADR-064 §결정 2

다음 8 어휘를 결정 제안 시점 menu 에서 제거 의무.

| 어휘 | 운영 사례 |
|---|---|
| 임시 | "임시 패치", "임시 결정" — 사후 audit 의존 패턴 |
| 단계적 | "단계적 도입" — CFP scope unitary 룰 (§1 후반) 위반 |
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

### CFP scope unitary 룰 — ADR-064 §결정 5

한 CFP 안 "경량 → full" 단계 채택 금지. 별개 CFP 분리는 허용.

| 허용 패턴 | 차단 패턴 |
|---|---|
| `CFP-N v0.1` + `CFP-N+1 v1.0` 가 독립 brainstorm + 독립 Story + 독립 PR | "본 CFP 의 v0.1 만 도입, v1.0 은 후속 작업" 식 단계 분기 |
| Implementation cost 분해 = PMOAgent vertical slice (한 CFP 안 sub-task) | "비용 부담 회피용 가벼운 prototype 후 본격" 식 분기 |
| Epic 분해 = 여러 child Story (각 독립 brainstorm + Story) | 단일 Story 안 "Phase 1 부분 적용 후 Phase 2 본격" 식 분기 |

## §2. 결정 제시 (Trace 2)

### Derived default 우선 — ADR-064 §결정 3 (룰 1)

Orchestrator 가 `AskUserQuestion` 발화 의도 시 다음 분기:

```
컨텍스트 (사용자 명시 + memory + Story file + ADR 인용) 로
합리적 default 도출 가능?
  YES → AskUserQuestion 생략. derived default 직접 declare + 결과 보고
  NO  → AskUserQuestion 발화 (단 §결정 3 룰 5 범위 적용)
```

**예외 영역** (derived default 도출 회피 의무):
- 가치 판단 (사용자 선호도 / 우선순위 / 도메인 의도)
- 미공개 컨텍스트 (Orchestrator 가 알 수 없는 사용자 측 정보 — 외부 시스템 상태 / 사용자 일정 등)

### 옵션 dump 금지 — ADR-064 §결정 3 (룰 2)

| 차단 패턴 | 허용 패턴 |
|---|---|
| "A / B / C / D / E / F 6 옵션 중 선택해 주세요" | "권장 = A (사유 1 문장). 대안 = B (사유 1 문장)" |
| 식별자 (ADR / CFP / 파일 path) 사전 요약 없이 식별자 dump | 식별자 + 핵심 요약 1 문장 사전 제시 후 진입 |
| jargon 5+ 단어 한 turn 안 발화 | 5+ jargon 시 brainstorm Phase 0 영역으로 격상 |

3+ 후보는 brainstorm 영역 (별도 Phase 0).

### 식별자 사전 요약 — ADR-064 §결정 3 (룰 3)

memory `feedback_explain_before_ask` 의 normative 승격. 사용자 발화 directive 2 (2026-05-12) 의 직접 해소.

| 패턴 | 허용/차단 |
|---|---|
| "ADR-064 적용해" (요약 부재) | 차단 — 식별자 dump |
| "ADR-064 (결정 원칙 mandate — forbid-list 8 어휘 + parallel default) 적용해" | 허용 — 식별자 + 1 문장 요약 |
| "CFP-446 (Codex pre-review iterative reformulation, ADR-052 Amendment 2) 진행해" | 허용 |

### 질문 brevity — ADR-064 §결정 3 (룰 4)

- 질문 = 1 문장 단위
- 다중 질문 시 numbered list (최대 3 항목)
- 컨텍스트 길이 < 핵심 질문 길이 유지

memory `feedback_question_quality` 의 normative 승격.

### `AskUserQuestion` 범위 제한 — ADR-064 §결정 3 (룰 5)

본 도구 발화는 다음 2 종 한정:

- 가치 판단 영역 (룰 1 예외 영역과 동일)
- 미공개 컨텍스트 영역

derived default 도출 가능 영역에서 `AskUserQuestion` 발화 = ADR-064 위반.

## §3. 적용 속도 (Trace 4)

### Subagent parallel default — ADR-064 §결정 4

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

### Sequential 강제 3 사유 dictionary

| 사유 | 운영 사례 |
|---|---|
| state dependency | RequirementsPL §6 외부 사례 조사 → §5 확장 요구사항 합성. ArchitectAgent §3 ADR 결정 → §7 설계 서사 |
| shared resource | 동일 file (예: `CLAUDE.md`) write 충돌 / 동일 GitHub label 변경 / 동일 branch commit / ADR 번호 sequential append |
| ordering invariant | FIX Ledger row append (시간 순) / ADR-RESERVATION row append (번호 순) / commit chain |

### Epic open→close KPI

Trace 4 measurable signal:

- **데이터 출처**: `EPIC-RESULTS-<KEY>.md` artifact frontmatter `opened_at` / `closed_at` timestamp delta
- **Dashboard 구축**: 본 carrier 외연 — CFP-β (잠재) 별도 follow-up
- **Baseline / target 정의**: dashboard 구축 후 evidence-enforceable framework (ADR-060) 점진 승격 — warning → blocking-on-pr → blocking-on-merge

본 KPI 는 외부 분산 시스템 영역의 throughput metric 와 정합 — Amdahl's Law speedup curve 가 이론적 anchor.

### 외부 선행 사례

| 사례 | 패턴 | 본 SSOT 와의 관계 |
|---|---|---|
| Amdahl's Law | speedup = 1 / ((1-P) + P/N) | parallel default 의 이론적 anchor — sequential bias 가 P 를 의도치 않게 축소 |
| Critical Path Method (CPM) | DAG longest path = lifecycle 하한 | Epic lifecycle = lane spawn DAG critical path. parallel default 적용 시 non-critical path 압축 |
| MapReduce / Spark shuffle dependency | shuffle 시에만 sequential | sequential 강제 3 사유 dictionary 외부 선행 사례 |

## 적용 사례 (운영 사례)

### Self-application — 본 Story (CFP-445) 자체

본 Story 자체가 결정 원칙 self-application:

- §1 사용자 directive 4 회 누적 = normative SSOT 정립 동인 (memory ephemeral 한계 해소)
- §3 RequirementsPL §2-§6 ↔ §7 ArchitectPL §7-§11 = state dependency = sequential (lane 진행 자체)
- 3 deputy (CodebaseMapper / Refactor / TestContractArch) spawn = parallel (state dependency 부재)
- Architect §7 → DesignReview = state dependency = sequential
- CFP-446 + CFP-449 = state dependency 부재 = parallel-eligible sibling Story (본 Story merge 후 동시 진행 가능)

### 위반 사례 차단 — Phase 0 brainstorming

본 Story 직전 brainstorming 영역에서 발생한 옵션 dump 사례:

| 위반 | 차단 패턴 |
|---|---|
| "옵션 A / B / C / D / E / F 6 종 제시" | 권장 1 안 + 대안 1 안 (최대 2) — 3+ 후보는 Phase 0 별도 |
| "ADR-039 / ADR-058 / ADR-060 / ADR-052 / ADR-054 식별자 dump" | 각 식별자 + 1 문장 요약 사전 제시 |
| "임시로 도입 후 본격 적용" | forbid-list dictionary 적용 — menu 자체에서 제거 |

본 사례는 `feedback_explain_before_ask` + `feedback_question_quality` memory entry 의 normative 승격 동인.

## Cross-reference SSOT 분산

```
ADR-064            = normative 결정 SSOT (결정 룰 자체)
decision-style.md  = 본 페이지 — 행동 패턴 + 적용 사례 SSOT
CLAUDE.md          = wrapper 진입점 cross-link (인용 위치)
playbook           = 절차 SSOT (Orchestrator 실행 절차)
story.yml          = Issue Form forcing function (decision_principle_compliance 체크박스)
CFP-449 lint       = mechanical enforcement (ADR-060 warning tier)
CFP-446            = touchpoint #1 iterative reformulation (ADR-052 Amendment 2)
```

각 SSOT 자기 영역 정의 — 중복 0. amendment 시 5 위치 동시 갱신 (ADR-053 구조적 변경 재구동 의무 정합).

## 관련 파일

- [ADR-064](../../../adr/ADR-064-decision-principle-mandate.md) — 본 페이지의 normative carrier
- [ADR-039](../../../adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — subagent default (Trace 4 모체)
- [ADR-058](../../../adr/ADR-058-adr-sunset-criteria-mandate.md) — ratchet 차단 forcing function
- [ADR-060](../../../adr/ADR-060-evidence-enforceable-promotion-framework.md) — evidence-enforceable framework
- `../orchestrator-discipline/spawn-default.md` — ADR-039 subagent default discipline (Trace 4 직접 인접)
- `CLAUDE.md` (wrapper) — wrapper 진입점 cross-link
- `docs/orchestrator-playbook.md` — 절차 SSOT
- `templates/github-issue-forms/story.yml` — Issue Form forcing function
