---
adr_number: 46
title: ResearcherAgent role redefinition — Concept formulation + Deep exploration + Requirement reshape mandate
date: 2026-05-09
status: Accepted
category: agent-design
carrier_story: null
supersedes: []
amends: null
amendment_log:
  - number: 1
    date: 2026-05-11
    adr: ADR-056
    summary: "domain/ vs concept/ 물리 디렉터리 분리 + PLAgent 합성 순서 명문화 + §6 compact summary"
related_stories: []
related_adrs:
  - ADR-013
  - ADR-037
  - ADR-042
related_files:
  - mclayer/plugin-codeforge-requirements/agents/ResearcherAgent.md
  - mclayer/plugin-codeforge-requirements/CLAUDE.md
  - mclayer/plugin-codeforge-requirements/.claude-plugin/plugin.json
  - .claude-plugin/plugin.json
  - CLAUDE.md
is_transitional: false
---

# ADR-046: ResearcherAgent role redefinition — Concept formulation + Deep exploration + Requirement reshape

## 상태

**Accepted (2026-05-09)** — ADR-013 dogfood-out waiver 발동, 정식 Story 7-lane flow 우회 (PR #287 / ADR-042 패턴 inherit).

## 컨텍스트

ADR-042 (Agent model selection policy, merged 2026-05-09T02:48:46Z, commit `5928749e`) §결정 2 가 ResearcherAgent 의 model tier 결정을 본 Story 까지 deferred 처리. ADR-042 핵심 원칙 — "Sonnet 으로 fully cover 가능 = role 재정의 시그널" — 의 직접 적용 대상.

현재 ResearcherAgent.md frontmatter description = "외부 지식 리서치 — 사용자 원문에서 자체 도출한 기술·선행사례 키워드 기반 타겟 조사, 연구원 수준 배경지식 축적" 이라는 keyword fetch 수준의 underdefined 정의. 사용자 articulation:

> "ResearcherAgent는 단순한 검색을 위한 Agent가 아니다. 요구사항을 분석하며 필요한 개념을 심층적으로 정립한 뒤 탐구하여 실제적인 요구사항으로 재편해야하는데 sonnet으로 대체 가능한 수준의 얕은 역할만 맡고 있다면 역할이 제대로 잡히지 않은 것이다."

Issue `plugin-codeforge-requirements#12` (구 lane repo issue — 현 `plugins/codeforge-requirements/`, repo 삭제됨 2026-06-12) 가 본 redesign 의 carrier issue.

본 ADR 는 Researcher 의 3 mandate (Concept formulation / Deep exploration / Requirement reshape concept-driven) 를 명료화하고, DomainAgent / RequirementsAnalyst 와의 4-way 협업 모델을 정합 보존하며, 산출 schema 와 mode policy 를 SSOT 화한다.

## 결정

### 결정 1: 3 mandate boundaries

| Mandate | Description | Boundary 정합 |
|---|---|---|
| **Concept formulation** | implicit 개념 / 도메인 가정 / 암묵 제약 식별 + 명시화 | Researcher exclusive (Domain/Analyst 영역 외) |
| **Deep exploration** | 외부 unknown unknowns + 학계·산업 선행사례 + 경쟁 솔루션 + standard 조사 | Researcher exclusive |
| **Requirement reshape (concept-driven)** | 원문 verbatim 보존 + concept-driven 관점 reshape (관계 retrieve / 실현 가능성 평가) | dimension 분리 ↔ Analyst (ambiguity-driven reshape) |

**Reshape dimension 분리 원칙**: Researcher 와 Analyst 가 같은 input (사용자 원문) 으로부터 서로 다른 dimension reshape 수행:

- Researcher: concept-driven (암묵 개념 / 도메인 가정 / 외부 관계 retrieve) → §6
- Analyst: ambiguity-driven (언어적 불확실성 / edge / 암묵 가정 확장) → §5

PL 이 두 산출 union → overlap dedup. 4-way 병렬 패턴 보존 (sequential 변경 X).

### 결정 2: 4-way collaboration model + Partial-known overlap zone

```
RequirementsPLAgent (synthesizer)
├── DomainAgent       — 사내 known knowns (partial coverage + gap 명시 가능)
├── ResearcherAgent   — concept formulation + external unknown unknowns + concept-driven reshape
└── RequirementsAnalyst — ambiguity / edge / 암묵 가정 → ambiguity-driven reshape
```

**Partial-known zone 처리**: DomainAgent (사내 partial + gap 명시) ↔ Researcher (외부 standard 부재 + concept gap-fill) 각각 자기 mandate 내에서 **독립 관점 보고**. PL 이 §2 / §6 dedup. 4-way 병렬 패턴 보존.

예시 (mctrader 도메인): KRW 거래소 trading 영역의 partial-known zone —

- DomainAgent: "사내 경험 = 5건의 KRW spot trading 운영 데이터 / gap = futures / cross-margin 영역"
- Researcher: "외부 standard = Binance / OKX limit order book algorithm 공식, KRW 시장 학계 연구 부재 (knowledge gap)"

PL 이 두 reading 을 §2 (도메인 분석) 와 §6 (외부 지식 배경) 에 dedup 분배.

### 결정 3: Output schema (Light structured 6-section + frontmatter)

`docs/stories/<KEY>.md §6` 갱신 의뢰의 schema:

**Frontmatter (metadata)**:

```yaml
---
mode: full | light | skip
reason: <skip/light 시 의무 — full 시 omit 가능>
concept_count: <implicit 개념 식별 건수>
external_source_count: <외부 reference 건수>
gap_count: <knowledge gap 건수>
---
```

**Body 6 sections**:

1. `## Concept formulation` — implicit 개념 list + 도메인 가정 + 암묵 제약 표면화
2. `## External knowledge map` — 학계 / 산업 선행사례 / 경쟁 솔루션 + 출처 URL (논문 / 표준 / 공급사 API spec / 시장 구조 자료까지)
3. `## Refined requirement` (concept-driven) — 원문 verbatim 보존 + 관계 retrieve + 실현 가능성 평가
4. `## Knowledge gap` — 외부 standard 부재 영역 + DomainAgent partial-known 에 보강 시그널
5. `## ADR 정합성 점검` — 기존 ADR · 도메인 제약 · 기술 관행과의 일치 / 주의 / 상충
6. `## PL 재질의 후보` — clarification 재스폰 hint (있을 시)

`mode: skip` 시도 §6 섹션 작성 의무 (각 section "외부 지식 보강 불필요 — 사유: <reason>" 명시) — Never-skippable invariant 보존.

### 결정 4: Mode policy — Researcher 자체 판단 + 적극 탐색 default skew

- **Authority**: Researcher 가 input (Story §1 + 관련 ADR + Project Config) 만으로 자체 mode 결정. PL override 없음.
- **Default skew**: full 측 배치 ("적극적으로 탐색하라" self-directive in agent prompt). skip / light 결정 시 명확한 사유 의무.
- **Never-skippable invariant 보존**: spawn 항상, 산출 mode 다름. mode=skip 도 유효한 관점 보고 (각 section reason 명시).
- **Sonnet 대수 불가 사유**: deep concept reasoning 책임 (ADR-042 §결정 1 (g) Opus tier criteria 충족 — "Deep research with reshape mandate").

### 결정 5: Opus tier rationale (ADR-042 cross-ref)

ADR-042 §결정 1 (g) Opus tier criteria — "Deep research with reshape mandate" — 본 ADR 가 정확한 mandate 충족 확인. Sonnet 대수 불가 사유 = deep concept reasoning 책임. multi-source synthesis 가 아닌 single-domain deep concept formulation 이라 ADR-042 §결정 1 (a) (PL synthesis) 와는 다른 row, 그러나 (g) 만큼 깊은 reasoning 요구. ADR-042 §결정 2 의 deferred fence 가 본 ADR 로 해소.

## 결과 (Consequences)

### 긍정

- Researcher 의 mandate 가 measurable signal (3 mandate boundary + Light structured 6-section schema + mode policy) 로 명료화 — Sonnet 대수 가능성 제거
- ADR-042 §결정 2 의 deferred fence 해소 (frontmatter `amendment_log[1]` + §결정 2 RESOLVED annotation)
- DomainAgent / RequirementsAnalyst 와의 4-way 병렬 dimension 분리 패턴 명시 — 향후 sub-agent role audit 시 reference

### 부정 / 트레이드오프

- partial-known overlap zone 처리에서 PL dedup overhead 가능 (DomainAgent partial coverage + Researcher knowledge gap 의 cross-ref) — 본 ADR 결정 2 의 "독립 관점 보고" 원칙 + 후속 follow-up CFP 후보 (DomainAgent schema partial_coverage flag 도입)
- Story 우회 (ADR-013 waiver) — 정상 Story flow 미지원 (KEY collision codeforge-internal-docs#99 + Action permission codeforge-internal-docs#98 미해결) 정상화 후 retroactive Story 부여 검토 가능

### Amendment 1 (ADR-056, 2026-05-11)

물리 디렉터리 분리(`domain/` vs `concept/`), PLAgent 합성 순서 명문화, §6 compact summary 추가.
상세: [ADR-056](ADR-056-domain-concept-knowledge-dir-separation.md)

## 대안 검토

| 대안 | 기각 사유 |
|------|----------|
| **Sequential pipeline (Analyst → Researcher)** | 4-way 병렬 패턴 결렬 + lane latency 증가 + RequirementsPL 의 spawn 패턴 변경 |
| **Researcher 전철 (Analyst overlap 삭제)** | RequirementsAnalyst 수명 압축 → 별도 Story 의 out-of-scope 위반 + 4-way 병렬 패턴 보존 가치 우선 |
| **Mode 개념 제거** | trivial Story 도 full schema 강제 → token cost 증가 + 사용자 directive "적극 탐색" 의미 약화 |
| **ADR-042 supersede by ADR-046 전체** | overkill — ADR-042 의 결정 1 / 결정 3 / 결정 4 영역은 본 Story 외, 무관 결정 supersede 위험 |
| **ADR-042 inline edit (amendment 없이)** | history trace 소실 — amendment_log 부재 시 향후 "왜 ADR-042 §결정 2 가 변했나" 추적 어려움 |

## ADR-013 dogfood-out waiver 사유

본 Story 는 정식 7-lane Story flow 우회 — 3 사유 (PR #287 / ADR-042 패턴 inherit):

1. **KEY collision** — story-init.yml Action 자동 KEY 할당이 wrapper 의 in-flight CFP-N 와 충돌. Tracked: [codeforge-internal-docs#99](https://github.com/mclayer/codeforge-internal-docs/issues/99)
2. **Action permission misconfiguration** — story-init.yml 의 PR creation step permission 결손. Tracked: [codeforge-internal-docs#98](https://github.com/mclayer/codeforge-internal-docs/issues/98)
3. **Cost asymmetry** — 본 ADR scope = ADR 1건 + agent file 재작성 + spec 1건. Phase 1 lane flow 진입 시 ~30 Opus agent invocation (요구사항 4 + 설계 8 + 설계리뷰 PL + 종합) — 본 Story 의 효과 (Researcher role 명료화) 와 비교 시 lane flow 자체 비용 negative

PR #287 (ADR-042) 와 동일 패턴 — ADR-013 waiver explicit invoke.

## 해소 기준

N/A — permanent policy

## 관련 파일

- 본 ADR
- [ADR-042](ADR-042-agent-model-selection-policy.md) — Agent model selection policy (frontmatter `amendment_log[1]` + §결정 2 annotation + §결정 1 (g) cleanup 동행)
- `mclayer/plugin-codeforge-requirements:agents/ResearcherAgent.md` — sibling PR target
- `mclayer/plugin-codeforge-requirements:CLAUDE.md` — sibling PR target
- [Spec PR #105](https://github.com/mclayer/codeforge-internal-docs/pull/105) — Stage 0 brainstorming SSOT (commit `02b676a` amendment 1 — ADR-046 carrier rename)

## 관련 ADR

- [ADR-013](ADR-013-codeforge-family-dogfood-out-policy.md) — dogfood-out waiver (본 ADR 발동 근거)
- [ADR-037](ADR-037-plugin-version-bump-rule.md) — plugin version bump rule (5.6.0 → 5.7.0 MINOR 정합)
- [ADR-042](ADR-042-agent-model-selection-policy.md) — Agent model selection policy (본 ADR 가 §결정 2 deferred fence 해소)
