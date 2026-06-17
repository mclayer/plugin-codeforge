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
  - number: 2
    date: 2026-06-17
    carrier_story: CFP-2328
    parent_epic: "mclayer/plugin-codeforge#2324"
    summary: "Mandate 2 demand-anchored 재초점(정밀화) — 개념 정립 지원 + unknown-unknown proactive 발굴 초점 재배치 + ①③ 작성자 역할(Concept formulation / Requirement reshape) 강조 + concept/ silo close-loop 명문화(독자 = 미래 Story 의 Researcher 자신) + §6 외부지식 하류 도달 주 채널 = Section 5 Refined Requirements(reshape) 정정 + ADR-046 §결정3 6-section schema ↔ ResearcherAgent.md 현행 drift 정합. downstream 기술자료 제공 책임은 삭제 아니라 S2(ADR-125 단계③)/S5(on-demand)로 이관 — strengthen 방향."
    direction: strengthen
    sunset_justification: null
related_stories:
  - CFP-2328
related_adrs:
  - ADR-013
  - ADR-037
  - ADR-042
  - ADR-124
  - ADR-125
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

### Amendment 2 (CFP-2328, 2026-06-17) — Mandate 2 demand-anchored 재초점 + concept silo close-loop

**carrier**: CFP-2328 (Epic `mclayer/plugin-codeforge#2324` S4). **`direction: strengthen`, `sunset_justification: null`.**

ADR-124 §결정 1 이 외부지식 충당을 3-단계로 정식 규정하면서 단계① (개념 정립·요구사항 재편) 의 주체를 본 ADR 의 Researcher 3 mandate 로 식별했고, §결정 5 표가 "ResearcherAgent 재초점 (단계① mandate 조정)" 을 S4 로 deferral 했다 (`ADR-124:199`). 본 Amendment 가 그 S4 row 를 이행한다.

#### Mandate 2 demand-anchored 재초점 (정밀화 — 약화 아님)

§결정 1 표의 Mandate 2 (Deep Exploration — 외부 unknown unknowns) 의 *초점*을 **"개념 정립 지원 + unknown-unknown proactive 발굴"** 로 재배치한다. 외부 선행사례·표준·경쟁 솔루션 조사는 **개념 정립(Mandate 1)·요구사항 재편(Mandate 3) 을 *지원*하는 한도** 안에서 수행한다 (demand-anchored). 이는 ADR-124 §결정 4 가 명시한 "§결정 4 적극 탐색 default skew 에 demand-anchored frame 을 더하는 것은 정밀화이며 '약화' frame 이 아니다" 와 정합한다 (`ADR-124:185`). Never-skippable invariant (§결정 4) 무손상, ADR-058 §결정 5 ratchet 강화 방향 정합.

3-mandate 골격은 무손상 — Mandate 1/3 의 구조·boundary, Mandate 2 의 mandate 자체는 보존하고 *초점*만 demand-anchored 로 정밀화한다.

#### downstream 이관 명시 (약화 0 증명)

외부 기술자료를 하류 lane 에 *제공*하는 책임은 본 Amendment 가 *삭제*하지 않는다. 그 책임은 외부지식 충당 3-단계 (ADR-124 §결정 1) 의 후속 단계로 *이관*됐다:

- **단계③ (S2 — ADR-125 요구사항리뷰 lane)**: 외부사실 의존 결론의 깊은 다출처 검증 (리뷰측 독립 producer 게이트). `ADR-125:101` / `ADR-125:148`.
- **S5 (on-demand 경로)**: 깊은 검증 on-demand 차등 메커니즘 (`ADR-124:199` deferral 경계, `ADR-125:154`).

따라서 본 Amendment 는 책임 *재배치*이지 책임 *삭제*가 아니다 — strengthen 방향, `sunset_justification: null`.

#### ①③ 작성자 역할 강조 + 외부지식 하류 도달 주 채널 정정

Researcher 의 비-중복 (Sonnet 대수 불가) 가치 = **① Concept formulation (개념 정립 / unknown-unknown proactive 발굴)** + **③ Requirement reshape (요구사항 재편)**. 즉 Researcher 는 외부 기술자료를 *수집·전달*하는 검색기가 아니라, 그것을 재료로 개념을 정립하고 요구사항을 *재편(reshape)* 하는 *작성자* 다.

외부지식이 하류 lane 에 도달하는 **주 채널 = ③ reshape = §6 Section 5 (Refined Requirements)** — 외부지식을 요구사항 텍스트에 *녹여* 전달한다. **concept/ silo 의 직접 열람이나 §6 raw dump 가 주 채널이 아니다.** §6 의 6-section schema (§결정 3) 자체는 무변경이며, Section 6 (Concept Summary) 는 PL 합성 보조 (single-read-surface — `ADR-056:79` §결정 4) 역할을 보존한다. "§6 이 하류 *기술수요*를 충당한다" 는 기대는 제거한다 (그 수요는 위 단계③/S5 가 담당).

#### concept silo close-loop (CL-1 = (가))

`concept/` 디렉터리의 "직접 독자 없음" 구조는 ADR-056 §결정 4/5 가 정의한 **by-design indirection** 이며 ADR-124 §결정 4 가 "결함으로 재규정하지 않는다" 로 못박았다 (`ADR-124:187`, `ADR-056:79`). 본 Amendment 는 이 by-design 보존을 무손상으로 둔 채 **read-loop 만 추가**해 silo 를 닫는다:

- **독자 = 미래 Story 의 Researcher 자신**. 누적된 `concept/` 자산이 다음 Story 의 Researcher 에게 "이미 정립된 개념" 으로 재공급된다 (close-loop).
- 이 read 는 **Mandate 2 재초점에 구조적으로 결합**된다 — 단순 "실행 초입 Glob 1-step" 절차가 아니라, *기존 concept/ 자산 = unknown-unknown 발굴·개념 정립의 출발점* 이라는 mandate-aligned 동기로 read 한다 (stateless one-shot·incentive 부재·토큰비용 3중 장벽을 mandate 결합으로 돌파).
- **토큰 회피**: §6 Section 6 compact summary 를 역방향 재사용 (raw concept 파일 대신 요약 우선 read) + Mode policy `skip`/`light` 시 read 면제. concept/ 소유 (ResearcherAgent 단독 write) 는 무변경 — 소유 재배치 0, close-loop read 만 추가 (= strengthen). ADR-056 §결정 1/4/5 무손상.

#### §6 schema drift 정합 (CL-2)

§결정 3 의 6-section schema 와 `ResearcherAgent.md` 현행 6-section 출력 표현이 함께 정합됨을 명시한다 (이중 SSOT drift 해소). 본 Amendment 는 section 개수·이름을 *재설계*하지 않는다 — schema *정합* (drift 해소) 만 수행하며 §결정 3 과 일치를 유지한다.

#### cross-ref

- ADR-124 §결정 1·4·5 (외부지식 3-단계 / 단계① demand-anchored 정밀화 / S4 deferral) — `ADR-124:139`, `ADR-124:185`, `ADR-124:199`.
- ADR-125 단계③ (하류 깊은 검증 이관처) — `ADR-125:101`, `ADR-125:148`.
- ADR-056 (`ADR-056-domain-concept-knowledge-dir-separation.md`) §결정 1/4/5 (concept silo by-design, 무손상) — `ADR-056:79`.
- ADR-058 §결정 5 (약화 evidence-gate — ratchet 강화 방향 보증).

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
- [ADR-124](ADR-124-external-knowledge-provisioning-model.md) — 외부지식 충당 3-단계 (Amendment 2 가 단계① S4 재초점 이행 — §결정 4 demand-anchored 정밀화 anchor)
- [ADR-125](ADR-125-requirements-review-lane.md) — 요구사항리뷰 lane (Amendment 2 의 downstream 기술자료 검증 이관처 단계③)
