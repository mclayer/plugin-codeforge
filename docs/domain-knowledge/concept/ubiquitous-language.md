---
kind: concept_definition
type: domain-knowledge
slug: ubiquitous-language
title: Ubiquitous Language — BC 안 공유 어휘 SSOT, drift detection forcing function
status: Active
updated: 2026-05-20
carrier_story: CFP-1117-S1
related_adrs:
  - ADR-091  # ArchitectLane DDD vocabulary governance — 본 개념의 normative SSOT (§결정 5 / §결정 6 / §결정 7)
  - ADR-068  # Boundary completeness invariants — I-4 wording SSOT 정합 (I-6 신설 후보 OQ-2)
  - ADR-064  # Decision principle mandate — Trace 1 forbid-list dictionary 확장 후보 (OQ-1)
related_files:
  - docs/glossary.md  # Ubiquitous Language entry SSOT (line 108-113)
  - docs/wording-dictionary.md  # negative forbid-list (anti-pattern 어휘) — 보완 관계
  - docs/domain-knowledge/concept/bounded-context.md  # BC sibling
tags:
  - ubiquitous-language
  - ddd
  - strategic-design
  - glossary-ssot
  - drift-detection
  - vocabulary-governance
---

# Ubiquitous Language

## 정의

`Ubiquitous Language` = **Bounded Context 안 모든 stakeholder (domain expert + developer + reviewer + agent) 공유 어휘 SSOT**. 코드 + 문서 + 회의에서 동일 용어 사용. BC 내부 limited (BC 사이는 Published Language 경유).

**한국어 표기**: `보편 언어` / `공용 언어` (영어 표기 권장 — 한국어 번역 비표준). SSOT = [`docs/glossary.md` Ubiquitous Language entry](../../glossary.md#ubiquitous-language).

DDD 의 핵심 invariant — Eric Evans 의 "Domain-Driven Design" (2003) 안 가장 강조된 building block. domain expert + developer 사이 translation cost 제거 + 코드 model = mental model.

## codeforge 의 Ubiquitous Language SSOT = `docs/glossary.md`

codeforge governance BC 의 Ubiquitous Language SSOT = [`plugin-codeforge/docs/glossary.md`](../../glossary.md) (ADR-091 Story-1 신규 산출).

**SSOT 적용 범위 (의무)**:
- agent file 본문 (15 agent in `plugin-codeforge-design/agents/`)
- ADR 본문 (`docs/adr/ADR-NNN-*.md`)
- Change Plan (`docs/change-plans/<KEY>-*.md`)
- Story file (`docs/stories/<KEY>.md`)
- inter-plugin contract registry (`docs/inter-plugin-contracts/`)
- skill file (`skills/<name>/SKILL.md`)
- CLAUDE.md (wrapper + lane plugin)
- 본 plugin-codeforge repo 안 모든 도메인 knowledge 문서 (`docs/domain-knowledge/`)

**verbatim 인용 의무**: 위 영역 안 모든 DDD 어휘는 본 glossary 정의 verbatim 인용 의무. paraphrase 금지 — glossary entry 본문 그대로 cite (link 또는 verbatim cut).

## glossary entry 의 의무 형식

각 entry 의무 4 field:

```markdown
### <Term Name>

**영어**: <Term name verbatim, 영어 표기>
**한국어**: <한국어 번역 또는 "영어 표기 권장 — 한국어 번역 비표준">
**정의**: <2-3 line definition, 도메인 정확성 우선>
**plugin-codeforge 적용 사례**: <codeforge governance BC 안 실 적용 사례, link reference>
```

복수 BC 동음이의 (예: Aggregate) 의 경우 2+ entry 분리 의무 — 각 BC 별 정의 + 동음이의 충돌 차단 명시.

## drift detection: `ubiquitous-language-drift-check`

ADR-091 §결정 6 의 lint mechanism. ADR-091 frontmatter `mechanical_enforcement_actions[]` 안 1번 entry.

**Mechanism (S3 신설)**:
- script: `scripts/check-ddd-vocabulary.sh` (Wave 1 wire)
- workflow: `templates/github-workflows/ubiquitous-language-drift.yml`
- tier: **warning** (ADR-060 framework 1차 도입, blocking-on-pr 미승격)
- evidence-checks-registry entry: `ubiquitous-language-drift-check` (warning tier 첫 row append)
- bypass label: `hotfix-bypass:ubiquitous-language-drift` (S3 신설, label-registry-v2 v2.37 → v2.38 MINOR bump)

**검사 logic**:
1. `Glob(docs/adr/**, docs/change-plans/**, docs/stories/**, plugin-codeforge-design/agents/**, skills/**)` 으로 모든 governance file 후보 수집
2. 각 file 안 DDD term (Aggregate / Bounded Context / Ubiquitous Language / Entity / Value Object / Domain Service / Domain Event / Application Service / Infrastructure / Repository / Factory / Specification / Module / Layered / Hexagonal / Clean / Onion / 4-Layer / Authority Pair / Subdomain Specialist 등) presence-grep
3. glossary.md 안 해당 term entry verbatim quote 또는 link cite 여부 확인
4. drift 발견 시 warning + comment trail

## wording-dictionary 와 차이 (positive SSOT ↔ negative forbid-list)

본 glossary ↔ `docs/wording-dictionary.md` 는 **보완 관계**:

| 영역 | 본 glossary.md | `docs/wording-dictionary.md` |
|---|---|---|
| **방향** | **positive SSOT** (term 정의 + 적용 사례) | **negative forbid-list** (anti-pattern 어휘 금지) |
| **검사** | `ubiquitous-language-drift-check` (term 사용 시 glossary cite 의무) | `decision-principle-vocab` + `wording-dictionary` (forbid-list 어휘 사용 차단) |
| **scope** | DDD term + codeforge governance BC 어휘 | 13 forbid-list 어휘 (ADR-064 Amendment 4) |
| **fail mode** | drift 감지 warning | usage 감지 warning + 정정 권고 |

**둘 다 의무**: positive SSOT 만 = forbid-list 부재로 anti-pattern 어휘 (예: "Big Ball of Mud" design intent 채택 표현) 표면화 안 됨 / forbid-list 만 = term 정의 SSOT 부재로 paraphrase drift 발생. 양쪽 동시 시공 (ADR-068 boundary completeness invariants precedent 답습 — 5 invariants 모두 적용해야 효과).

## 사례 cross-ref: Aggregate (governance ↔ application 동음이의 entry pair)

본 glossary.md 안 첫 동음이의 사례 — **Aggregate** 가 2 distinct entry 로 explicit separate:

| Entry | 정의 | 적용 BC |
|---|---|---|
| [`Aggregate (governance BC)`](../../glossary.md#aggregate-governance-bc) | supervised authority cluster (ArchitectPLAgent metaphor only) | codeforge governance BC |
| [`Aggregate (mctrader application BC)`](../../glossary.md#aggregate-mctrader-application-bc) | DDD Aggregate root in domain model (transactionally consistent) | mctrader application BC (별 SSOT) |

**Codex Q2 합의 (verbatim)**: "agent = process participant ≠ domain object" — codeforge governance BC 의 Aggregate 는 **metaphor only**. literal DDD Aggregate Root 아님. 본 동음이의 분리가 ADR-091 §결정 3 (2-layer explicit separate) 의 forcing function.

**downstream 시연 영역**: ADR-091 §결정 7 INV-5 의 evidence enumeration 5 영역 안 1번 (Story field 변경 evidence) — Story §ubiquitous_language 안 BC + Aggregate 명시 변경이 본 동음이의 차단의 mechanical realization.

## Vocabulary theater 차단 (ADR-091 §결정 7)

본 Ubiquitous Language SSOT 의 핵심 forcing function = **vocabulary theater 차단**.

> Vocabulary theater = 어휘 emit 만, decision flow 변경 0. agent 가 DDD 단어 emit 하면서 기존 implicit decision flow 유지 → document 만 향상 / runtime lesson 해소 = 0.

ADR-091 §결정 7 의 5 영역 evidence enumeration 의무:
1. Story field 변경 evidence
2. deputy spawn rationale 변경 evidence ("which subdomain under threat" 어휘 transition)
3. Change Plan DDD field 변경 evidence (§bounded_context_boundary + §affected_aggregates)
4. review-verdict finding 변경 evidence (`bc_violation` / `aggregate_violation` / `ubiquitous_language_drift` finding type 신설)
5. ADR acceptance criteria 변경 evidence

`ubiquitous-language-drift-check` lint = 위 5 영역의 mechanical 보완. drift 시 warning trail 누적 → ADR-060 framework 통한 blocking promotion gate 평가 (Wave 2 carrier, 별 CFP).

## Cross-reference

- [ADR-091 §결정 5](../../adr/ADR-091-architectlane-ddd-vocabulary-governance.md) — Bounded Context governance + 15 agent frontmatter field 의무
- [ADR-091 §결정 6](../../adr/ADR-091-architectlane-ddd-vocabulary-governance.md) — enforcement layer 3-tier (Agent prompt + Template lint + review-verdict enum)
- [ADR-091 §결정 7](../../adr/ADR-091-architectlane-ddd-vocabulary-governance.md) — Vocabulary theater 차단 forcing function INV-5
- [`docs/glossary.md`](../../glossary.md) — Ubiquitous Language entry SSOT
- [`docs/wording-dictionary.md`](../../wording-dictionary.md) — negative forbid-list (보완 관계)
- [`docs/domain-knowledge/concept/bounded-context.md`](bounded-context.md) — BC sibling
