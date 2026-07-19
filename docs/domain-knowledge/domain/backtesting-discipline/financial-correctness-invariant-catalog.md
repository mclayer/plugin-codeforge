---
kind: domain_fact
type: domain-knowledge
area: backtesting-discipline
topic_slug: financial-correctness-invariant-catalog
title: 백테스트 financial-correctness invariant catalog — 11 invariant + A/B 분류 + 7 Sins traceability (DomainAgent financial-invariant-0 shape 판정 근거)
status: Active
updated: 2026-06-28
carrier_story: CFP-2445
tags:
  - backtesting
  - financial-correctness
  - silent-corruption
  - lookahead-bias
  - survivorship-bias
  - financial-invariant-0
  - adr-042-amendment-17
related_adrs:
  - ADR-042  # Amendment 17 — DomainAgent financial-invariant-0 조건부 sonnet 정책 SSOT (본 catalog = D1 산출)
  - ADR-161  # DomainAgent write 권한 경로 docs/domain-knowledge/domain/** (concept/** deny)
  - ADR-058  # 약화 방향 sunset_justification evidence requirement (tier-flip 하향 evidence-gate)
  - ADR-057  # Codex 독립 review baseline 선례 (F1 measurement)
related_files:
  - archive/adr/ADR-042-agent-model-selection-policy.md  # Amendment 17 (정책 SSOT)
  - scripts/check-stakes-tier-gating.sh  # STAKES_FINANCIAL_INVARIANT_ZERO predicate (본 catalog 가 차단하는 invariant 매핑)
  - plugins/codeforge-requirements/agents/DomainAgent.md  # financial-invariant-0 shape mandate 표면 재정의 (본 catalog 참조)
  - docs/domain-knowledge/concept/stakes-gated-model-tier-baseline.md  # F1 evidence-gate (catalog cross-ref 누락 측정 입력)
---

# 백테스트 financial-correctness invariant catalog

## 정의

**백테스트 financial-correctness invariant** = 백테스트(과거 데이터 기반 거래 전략 모의 실행)가 "결과 숫자는 그럴듯한데 사실은 틀린" **silent corruption**(조용한 오염)에 빠지지 않기 위해 지켜야 하는 도메인 규율의 집합이다. 거의 모든 invariant 위반은 백테스트 수익을 *부풀린다*(낙관 편향) — 프로그램이 죽거나 예외를 던지는 게 아니라 "좋아 보이는 틀린 결과"를 만들어내므로 CI·단위 테스트·컴파일러가 잡지 못한다. 이 silent 성격이 financial invariant 식별을 **opus급 도메인 판단의 기본값**으로 만드는 근거다(결과 비접촉 작업 shape 에서만 해석 표면이 0 으로 떨어진다).

본 catalog 는 11 invariant 를 (a) 정의 (b) 오염 메커니즘 (c) 판단 깊이로 기술하고, 각 invariant 를 **부류 A(정적 falsifiable) / 부류 B(프로세스·메타데이터 의존)** 로 분류한다. ADR-042 Amendment 17 의 D1 산출물이며, DomainAgent 의 financial-invariant-0 shape 판정(2-predicate AND 조건부 sonnet)에서 "어떤 invariant 표면이 0 으로 떨어지는가"의 참조 SSOT 다.

## 컨텍스트

### 왜 catalog 인가 (financial-invariant-0 shape 판정의 입력)

ADR-042 Amendment 16(CFP-2432)이 Story-shape 조건부 model tier 를 InfraOperationalArchitectAgent 단독 flip 으로 v1 확정하며 **DomainAgent 는 v1 명시 제외 + follow-up CFP** 로 deferred 했다. 사유: low-stakes 4-AND shape(실자금 없음 ∧ cutover 없음 ∧ 신규 신뢰경계 없음 ∧ live 외부 API 없음)라도 **백테스트는 financial-correctness invariant 가 상존**한다 → DomainAgent 를 그대로 sonnet 으로 내리면 invariant 누설 risk(InfraOpArch 의 §7.4 stakes-coupled *물리적 dormant* 와 달리 정당성이 약하다).

Amendment 17(CFP-2445)이 그 자리를 채운다 — DomainAgent sonnet flip 조건 = **(4-AND low-stakes) AND (financial-invariant-0 shape)** 2-predicate AND. financial-invariant-0 은 stakes 4-AND 와 **orthogonal 한 financial-correctness 결과접촉 축**(DomainAgent 전용 별 predicate). 본 catalog 는 "financial-invariant-0 신호 각각이 어떤 invariant 를 차단하는가"를 정의해 그 predicate 의 falsifiable 근거를 제공한다.

### 자기 인용 backbone — 7 Sins of Quantitative Investing

본 catalog 의 invariant 식별 backbone = 업계 표준 **"7 Sins of Quantitative Investing"**(Luo et al., Deutsche Bank Quantitative Strategy) 의 7 항목:

1. survivorship bias
2. look-ahead bias
3. storytelling (사후 서사 적합)
4. data mining / overfitting (data-snooping)
5. transaction cost (turnover) 무시
6. outliers (극단치) 처리
7. asymmetric / unrealistic shorting cost

7 Sins backbone 전부 본 catalog INV 에 1:1 매핑된다 (의도적 제외 0 — `## 핵심 규칙` 의 traceability 표 참조). 학술 1차 grounding = López de Prado & Bailey *Deflated Sharpe Ratio* / *Probability of Backtest Overfitting*(시행 횟수 ↔ overfitting INV-6), CFA Level 2(survivorship / lookahead 정의), survivorship 정량 anchor = Elton-Gruber-Blake(1996).

> **자료 출처 grounding (ADR-119)**: 5-AND·A/B 분류·9→11 invariant·F1 survivorship 1.4% 는 요구사항 §6 Researcher 14 출처(López de Prado & Bailey 학술 1차 2종 + 7 Sins of Quantitative Investing 업계 표준 + CFA Level 2 + survivorship 정량 vendor 실측)로 cited grounding 완료, 요구사항리뷰 lane 외부사실 게이트 PASS. 본 catalog 는 요구사항 §6 cited 사실을 재사용한다(설계 lane 추가 외부 검증 불요).

## 핵심 규칙

### invariant catalog (11 invariant + A/B 분류)

각 행: (a) invariant 정의 / (b) 오염 메커니즘(어떻게 silent 하게 수익을 부풀리는가) / (c) 부류 A(정적 falsifiable) 또는 B(프로세스·메타데이터 의존) / opus 판단 강도.

| # | invariant | (a) 정의 | (b) 오염 메커니즘 (silent 부풀림) | 부류 | opus 판단 강도 |
|---|---|---|---|---|---|
| **INV-1** | Lookahead bias / future-leak | 시점 t 의 의사결정에 t 시점에 알 수 없는 미래 정보가 누설되지 않음 | 미래 가격·실적·정정값이 join/shift 오류로 과거 시점에 유입 → 비현실적 예지력으로 수익 급등 | **A** (시점 misalignment = 데이터 흐름 정적 패턴 falsifiable) | opus 필수 (코드 무증상, 시간 인과 추적) |
| **INV-2** | Survivorship bias | universe 가 "현재 살아남은 종목"만이 아니라 당시 존재한 전체 종목을 포함 | 상장폐지·청산 종목이 데이터셋에서 누락 → 살아남은 우량 종목만 backtest → 수익 과대 (mutual-fund 약 1.4%/년 — F1) | **B** (universe 완전성 = 데이터 출처·시점 메타데이터 의존) | opus 필수 (데이터 출처 신뢰 판단) |
| **INV-3** | Fee / commission / slippage / spread | 체결 비용(수수료·슬리피지·호가 스프레드)이 모델에 존재하고 값이 현실적 | 비용 0 또는 비현실적 저비용 가정 → 고회전 전략이 거짓 수익 (실제론 비용에 잠식) | **A** (모델 존재·값 = 정적 산술 falsifiable) + 모델 타당성은 opus | opus(모델 타당성) / sonnet(파라미터 검증) 2-층 |
| **INV-4** | PnL / position state 정합 | `equity = cash + Σ(holdings × mark)` 항등식 및 포지션 상태 전이 일관성 | 포지션 회계 버그(이중 계상·누락)로 equity 가 실제 자산과 괴리 → 거짓 수익/손실 | **A** (`equity = cash + Σ(holdings × mark)` 항등식 = 정적 단위테스트) | opus(정의·엣지) / sonnet(항등식 검증) 2-층 |
| **INV-5** | Point-in-time (PIT) data 정합 | 각 시점의 데이터가 그 시점에 실제 알려진 값(정정 전 원본·당시 universe) | 사후 정정된(restated) 재무·corporate-action-adjusted 가격을 과거 시점에 사용 → lookahead 동형 누설 | **B** (PIT 준수 = 시점 메타데이터·data lineage 없이 정적 falsify 불가) | opus 필수 (corporate-action·lineage) |
| **INV-6** | Regime change / overfitting / curve-fitting | 전략이 표본 외(out-of-sample) 일반화되며 과도한 시행으로 fitting 되지 않음 | 같은 데이터에 수많은 파라미터 조합 시행 → 우연히 좋은 조합 채택(data-snooping) → 표본 외 붕괴 | **B** (시행 횟수 추적 = 프로세스 invariant, 단일 산출물 정적 검사 불가) | opus 필수 (통계 일반화·표본 충분성 — Deflated Sharpe) |
| **INV-7** | Order fill 가정 (가격·시점·가능성) | 주문 체결 가정(체결가·체결 시점·체결 가능성)이 시장 미시구조에 부합 | 종가 즉시 무한 체결·미래 저가 체결 가정 → 비현실적 진입가로 수익 부풀림 (INV-1 강결합) | **A** (fill 규칙 = 정적 코드 패턴) + INV-1 강결합 | opus 필수 (시장 미시구조 + INV-1/8 결합) |
| **INV-8** | Capacity / market impact / liquidity | 주문 규모가 자산 유동성 대비 시장 충격을 일으키지 않거나 충격이 모델링됨 | 무한 유동성 가정 → 대규모 주문이 가격 영향 없이 체결된다고 가정 → 실전 미실현 수익 | **A**(impact 모델 존재) + **B**(자산별 유동성 데이터 의존) 혼합 | opus 필수 (impact 강도 = 자산별 유동성 도메인) |
| **INV-9** | 시간 경계 (funding/borrow, timezone, 거래시간) | funding·borrow 비용, timezone 정규화, 거래·점검 시간 경계가 정확 | timezone 오정렬·funding/borrow 비용 누락·거래시간 외 체결 가정 → 비용 누락·시점 오류 수익 | **A**(timezone 정규화 정적) + **B**(funding·점검 캘린더 메타데이터) 혼합 | opus(funding·점검 정책) / sonnet(UTC 정합) 2-층 |
| **INV-10** | **Storytelling / narrative-fit** (7 Sins #3) | 가설이 데이터 관측 *이전*에 사전 정의되며 사후 서사로 끼워맞추지 않음 | 백테스트 결과를 본 뒤 그럴듯한 이유를 사후 구성(data-snooping 의 서사 버전) → 표본 외 무효 | **B** (사후 서사 적합 = 방법론 메타, 정적 falsify 불가) | opus 필수 (가설 사전성·data-snooping 도메인) |
| **INV-11** | **Outliers / 비정상값 처리** (7 Sins #6) | 극단치·비정상 데이터 포인트의 처리 규칙이 명시되고 정당함 | 극단치를 무비판 포함(거짓 신호)하거나 무근거 제거(생존 편향 도입) → 수익 왜곡 | **A**(outlier 처리 규칙 정적) + **B**(극단치 정당성 도메인) 혼합 | opus(처리 정책 타당성) / sonnet(규칙 적용 검증) 2-층 |

### A/B 분류의 의의 (F3 / OQ-4)

- **부류 A (정적 falsifiable)** = lookahead 코드 패턴·fee 누락·PnL 산술처럼 **단일 산출물 정적 검사**(코드·diff·산술 항등식)로 falsify 가능. 향후 mechanical falsifiability gate(A-side 정적 검출)의 재사용 기반.
- **부류 B (프로세스·메타데이터 의존)** = PIT governance·시행 횟수·survivorship 완전성·storytelling 처럼 **시점 메타데이터·프로세스 추적 없이는 정적 falsify 불가**. 데이터 출처 신뢰·통계 일반화 같은 opus 도메인 판단이 본질적으로 필요.
- **financial-invariant-0 predicate 자체는 A-side 메커니즘**(Story 메타·경로로 결정론적 판정 — ADR-042 Amd17 §결정1)이나, invariant *식별/검증*은 A+B 전부를 cover(opus 도메인 판단). 둘은 **disjoint** — shape 판정(A-side)이 sonnet 가능 여부를 가르고, 가른 후 sonnet 이 cover 하는 mandate 표면은 financial-invariant-0 에선 0(결과 비접촉)이다.

### 7 Sins 1:1 traceability (의도적 제외 0)

| 7 Sins 항목 | 매핑 INV |
|---|---|
| survivorship bias | INV-2 |
| look-ahead bias | INV-1 |
| storytelling | **INV-10** (F2 편입) |
| data mining / overfitting | INV-6 |
| transaction cost (turnover) | INV-3 |
| outliers | **INV-11** (F2 편입) |
| asymmetric / unrealistic shorting cost | INV-9 (borrow 비용) · INV-3 (비용 분산) |

7 Sins backbone 전부 1:1 매핑 — 의도적 제외 0. INV-10(storytelling)·INV-11(outliers)은 9 invariant 초안에서 누락되었던 2종을 편입(F2 정정).

### F1 정정 — survivorship 정량 anchor

INV-2 survivorship 의 mutual-fund 정량 anchor = **Elton-Gruber-Blake(1996) 약 1.4%/년**(요구사항리뷰 dual-peer + PL 다출처 교차 = Oxford Academic *Review of Financial Studies* 9:4:1097 수렴, "확인 완료"). 요구사항 초안의 "0.9%" 단일 약출처(susanpotter.net)는 사실 오류로 기각했다. survivorship 1~4%/년 range, Sharpe 0.09→0.66 boost, PIT 1.5~2.0% 는 별도 출처로 grounding(F1 의 1.4% 단일 수치는 load-bearing 아님 — range 가 본질).

### financial-invariant-0 신호 ↔ 차단 invariant 매핑

ADR-042 Amd17 §결정1 의 5-AND 신호 각각이 차단하는 invariant(본 catalog 가 그 매핑의 SSOT):

| 신호 | 차단 invariant |
|---|---|
| 1. 결과-숫자 비접촉 (equity/PnL/position/체결가/universe/파라미터 생성·변형 안 함) | INV-3 / INV-4 / INV-7 / INV-8 / INV-10 / INV-11 |
| 2. 시간-인과 비접촉 (시계열 시점 정렬·join·window·리샘플 미접촉) | INV-1 / INV-5 |
| 3. 체결/비용 모델 비접촉 (fee·slippage·fill·funding 로직 미변경) | INV-3 / INV-7 / INV-9 |
| 4. data lineage 비접촉 (데이터 출처·정정·universe 구성 미변경) | INV-2 / INV-5 |
| 5. (보조) 변경 경로 (도메인 숫자 repo 밖 — 순수 렌더·infra·tooling·문서) | — (allow-list) |

5-AND 전부 참이어야 financial-invariant-0(불충족·불확실 = opus, fail-safe monotone).

## 경계

- **wrapper-self 비대상**: 본 catalog 는 *정책 carrier* 인 wrapper repo 에 codify 되나, financial-invariant-0 tier-flip 의 실 적용 대상은 **consumer 백테스트 프로젝트**(예: mctrader)다. wrapper-self Story 는 financial 결과 비접촉이지만 tier-flip 적용 roster 가 아니다.
- **advisory ≠ blocking gate**: A-side 정적 falsifiability 의 mechanical gate(blocking) 승격은 본 catalog 범위 밖 — 별 CFP(evidence 누적 후)다. 본 catalog 는 invariant 식별·분류 advisory 만 정의한다.
- **catalog ≠ 판정 엔진**: 실제 financial-invariant-0 5-AND 판정은 `scripts/check-stakes-tier-gating.sh` 의 `STAKES_FINANCIAL_INVARIANT_ZERO` predicate 책임(결정론 SSOT). 본 catalog 는 그 predicate 가 차단하는 invariant 의 정의·분류 입력만 제공 — 두 영역 disjoint.
- **DomainAgent write 권한 경로**: 본 파일은 `docs/domain-knowledge/domain/**` 하위(area=`backtesting-discipline`)다. `docs/domain-knowledge/concept/**`(ResearcherAgent 전용, ADR-161 deny)가 아닌 domain/ 만 DomainAgent 가 write 가능(OQ-7).

## 관련 ADR

- **ADR-042 Amendment 17** (CFP-2445) — DomainAgent financial-invariant-0 조건부 sonnet 정책 SSOT. 본 catalog = D1 산출물(11 invariant + A/B 분류 + shape 매핑). financial-invariant-0 = stakes 4-AND 와 orthogonal 한 financial-correctness 결과접촉 축.
- **ADR-042 Amendment 16** (CFP-2432) — Story-shape 조건부 model tier v1(InfraOpArch). §결정3 가 본 catalog codify 를 DomainAgent flip 의 선결조건으로 예약.
- **ADR-161** — DomainAgent write 권한 경로 `docs/domain-knowledge/domain/**`(concept/** deny). 본 catalog 위치 근거.
- **ADR-058 §결정5 / ADR-064 §결정7** — 약화 방향 sunset_justification evidence requirement(DomainAgent tier-flip 하향 evidence-gate). 본 catalog cross-ref 누락 = F1 미달 임계 ①.
- **ADR-057 §결정3** — Codex 독립 review baseline 선례(F1 measurement). 본 catalog = sonnet 산출물의 catalog cross-ref 완결성 측정 입력.

## 변경 이력

| 일자 (KST) | 변경 | carrier |
|---|---|---|
| 2026-06-28 | 신설 — 11 invariant(INV-1~11, F2 storytelling/outliers 편입) + A/B 분류(정적 falsifiable / 프로세스·메타데이터) + 7 Sins 1:1 traceability + F1 survivorship 1.4% 정정 + financial-invariant-0 신호↔invariant 매핑 | CFP-2445 (ADR-042 Amendment 17 Phase 2) |
