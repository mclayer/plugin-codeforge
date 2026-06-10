---
adr_number: 117
title: Fable 5 surgical 모델 tier 채택 (chief author / 장기 agentic / 적대적 심판 한정)
status: Accepted
category: governance
date: 2026-06-10
carrier_story: CFP-2134
is_transitional: false
amends: null
supersedes: null
related_adrs:
  - ADR-057  # Orchestrator Opus 필수 mandate + Sonnet→Opus rate-limit fallback — 본 ADR §결정 5 (Orchestrator 제외) 정합
related_stories:
  - CFP-2134  # carrier (Cross-repo Fable 5 채택 Epic — foundation)
related_files:
  - docs/consumer-guide.md
mechanical_enforcement_actions: []   # 신규 lint/sentinel 0 — model alias 적용은 각 lane plugin 의 에이전트 frontmatter (별 lane PR) 가 SSOT. Claude Code 버전 floor 는 런타임 spawn 실패로 자가 강제 (미인식 ID = silent fallback 없이 fail).
---

# ADR-117: Fable 5 surgical 모델 tier 채택 (chief author / 장기 agentic / 적대적 심판 한정)

## 상태

Accepted (2026-06-10 KST — CFP-2134 carrier). Cross-repo Fable 5 채택 Epic 의 foundation 설계 결정. 본 ADR 은 정책 SSOT 이며, 실제 `model: fable` alias 적용은 각 lane plugin 의 에이전트 frontmatter 변경(별 lane PR — design / develop / review / requirements)으로 실현된다.

## 컨텍스트

Claude Fable 5(`claude-fable-5`, 2026-06-09 GA)는 Anthropic 일반 공개 최강 모델이다. Opus 4.8 대비 long-horizon 작업·SW 엔지니어링·적대적 추론에서 우위를 보인다.

비용·프로파일 사실:
- **가격**: $10 / $50 per MTok(input / output) = Opus 4.8($5 / $25)의 **정확히 2배**.
- **thinking 프로파일**: Opus 4.8 과 동일(adaptive on / extended 없음) → `opus` → `fable` 교체 시 thinking 능력 손실 0.

문제는 "2배 비용을 어디까지 정당화하는가"이다. codeforge 는 0 core 에이전트 wrapper 로, 8 lane plugin 의 ~30+ 에이전트가 역할별로 fan-out 된다. 역할의 성격은 이질적이다:
- 일부는 **long-horizon chief author / 장기 agentic 코딩 / 적대적 심판**(긴 컨텍스트·다단계 추론·대립 검증) — Fable 의 우위가 직접 발현.
- 다수는 **단기 구조적 advocate / 빠른 분류 / 외부 모델 위임 래퍼 / GitOps·worker** — long-horizon 이점이 발현될 표면이 작아 2배 비용 대비 효용이 낮다.

전체 일괄 채택(opus→fable 전면)은 후자 군까지 2배 비용을 물리므로 비효율이고, 3~4개 minimal pilot 은 채택 범위가 너무 좁아 효용 검증이 불충분하다. 따라서 capability 상승이 비용을 정당화하는 역할만 **외과적(surgical)으로** 골라 적용한다.

추가 제약: `model: fable` alias 는 Claude Code v2.1.170+ 에서만 인식된다. 미만 버전은 미인식 model ID 를 **조용히 fallback 하지 않고 spawn 자체를 실패**시킨다 — consumer 호환성 floor 를 명시할 의무가 발생한다.

## 결정

### 결정 1: surgical 채택 대상 10 에이전트에만 `model: fable` 적용

capability 상승이 2배 비용을 정당화하는 역할 = **chief author / 장기 agentic 코딩 / 적대적 심판**. 적용 대상 10개:

| lane | 에이전트 | 분류 근거 |
|---|---|---|
| design | Architect | chief author (설계 서사 multi-source synthesis) |
| design | ArchitectPL | 장기 검수 + deputy fan-out 통합 |
| design | SecurityArch | 적대적 보안 설계 추론 |
| develop | Developer | 장기 agentic 코딩 |
| develop | DeveloperPL | 장기 agentic 코딩 통합 |
| review | ClaudeReview | 적대적 심판 |
| review | CodeReviewPL | 적대적 심판 (구현 리뷰 verdict) |
| review | DesignReviewPL | 적대적 심판 (설계 리뷰 verdict) |
| review | SecurityTestPL | 적대적 심판 (보안 테스트 verdict) |
| requirements | Researcher | long-horizon 외부 지식 종합 |

### 결정 2: 제외 기준 — 단기 구조적 / 빠른 / 위임 / worker 역할

다음 군은 제외한다(현행 모델 유지) — Fable 의 long-horizon 이점이 2배 값을 정당화하지 못한다:
- **좁은 구조적 advocate**: ModuleArch · APIContractArch · Refactor · CodebaseMapper · ArchitectAnalyst (단일 mandate advocacy, 설계 시점 구조 결정).
- **빠른 haiku 군**: 빠른 분류·경량 처리 역할.
- **GPT-5.4 위임 래퍼**: RequirementsAnalyst · CodexReview (실제 추론은 외부 Codex/GPT-5.4 가 수행, 래퍼는 위임만).
- **deploy / test worker**: 단기 실행 worker.
- **confluence-sync · GitOps**: 기계적 sync / git ops.
- **PMO · Dialog · Continuity · Feasibility · Domain**: 단기 구조적 역할.

### 결정 3: 호환성 floor — Claude Code 최소 버전 2.1.170

`model: fable` alias 는 Claude Code v2.1.170+ 에서만 인식된다(미인식 ID = silent fallback 없이 spawn 실패). 따라서 **codeforge 최소 Claude Code 버전 = 2.1.170**. consumer-guide §"필수 의존성" 에 명시한다. 2.1.170 미만 consumer 는 본 결정 1 의 10 에이전트(design / develop / review / requirements lane) spawn 이 실패한다.

### 결정 4: 풀 ID 아닌 alias `fable` 사용

풀 ID(`claude-fable-5`)가 아닌 alias `fable` 을 frontmatter 에 기재한다 — 버전 업그레이드(Fable 5.x → 차기) 자동 추적 best-practice. Orchestrator `opus` alias 관행과 동형.

### 결정 5: Orchestrator 모델 제외 — 현행 `opus` 유지

최상위 세션(Orchestrator) 모델은 현행 `opus`(ADR-057 mandate)를 유지한다. Fable Orchestrator 채택은 비용·세션 전반 영향이 별개 차원이므로 **별 결정 사안**으로 분리한다 — 본 ADR scope 외.

## 해소 기준

N/A — permanent policy. 본 ADR 은 모델 tier 선택 정책의 상시 기준으로, sunset 대상이 아니다. 단, 모델 세대 전환(차기 최강 모델 GA / Opus·Fable 가격 구조 변동 / Orchestrator Fable 채택 별 결정)이 발생하면 본 ADR 을 amend 하여 surgical 대상·floor 버전을 재산정한다.

## 근거 (Rationale)

- 옵션 A(opus 전체 → fable 전면 교체) **기각** — 단기 구조적 opus 에이전트(ModuleArch / APIContractArch / Refactor 등)까지 2배 비용을 물리나 long-horizon 이점 발현 표면이 작아 비용 대비 효용이 낮다.
- 옵션 B(minimal pilot 3~4개) **기각** — 채택 범위가 너무 좁아 chief author / 장기 코딩 / 적대적 심판 3 축의 효용을 동시에 검증하기 불충분하다.
- 옵션 C(surgical 10 에이전트 채택) **채택** — capability 상승이 2배 비용을 정당화하는 역할만 외과적으로 골라 적용. thinking 손실 0(프로파일 동일)이라 교체 부작용 없음. 제외 군은 현행 모델 유지로 비용 중립.

## 영향 / 후속

- **lane PR(별 PR)**: design / develop / review / requirements 4 lane plugin 의 해당 에이전트 frontmatter `model:` 를 `fable` 로 변경 — 각 lane plugin repo 의 별 PR(본 wrapper foundation PR OOS).
- **marketplace sync**: plugin.json 메타 변경(version) 동반 시 ADR-063 atomic invariant 에 따라 marketplace sync PR 선행(본 Epic 범위).
- **consumer 호환성**: 2.1.170 미만 consumer 는 해당 lane 에이전트 spawn 실패 — consumer-guide floor 명시로 사전 고지.
- **Orchestrator Fable 채택**: 별 결정 사안(§결정 5) — 향후 별 ADR/CFP.
