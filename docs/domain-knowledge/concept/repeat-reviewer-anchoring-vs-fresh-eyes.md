---
kind: concept_definition
type: domain-knowledge
slug: repeat-reviewer-anchoring-vs-fresh-eyes
title: Repeat-reviewer anchoring vs fresh-eyes (동일 리뷰어 반복 회차의 검출력 부채)
status: Active
updated: 2026-08-12
carrier_story: CFP-2946
related_adrs:
  - ADR-119  # verify-before-trust / 판정면 규율 — 재검토 회차의 단정 기준
  - ADR-070  # dual-peer 리뷰 축 (독립 peer 2인)
  - ADR-081  # 리뷰 lane peer 독립성 축
  - ADR-125  # 요구사항리뷰 lane — 다출처 검증 단계
related_concepts:
  - agent-resumption-vs-respawn                # 재개 이득의 반대급부를 소유하는 disjoint 축
  - merge-time-adversarial-verification-gate   # 검출력을 세우는 반대 방향 기제
  - mutation-based-hollow-gate-detection       # 검출력 자체를 falsify 하는 방법론
  - vacuous-pass                               # 검출력 소실이 착지하는 실패 형태
tags:
  - codeforge
  - review-quality
  - cognitive-bias
  - anchoring
  - fresh-eyes
  - detection-power
sources:
  - https://ieeexplore.ieee.org/document/883793/
  - https://www.computer.org/csdl/proceedings-article/icse/2001/10500155/12OmNqFJhUe
  - https://web.eecs.umich.edu/~weimerw/p/weimer-fse2020-bias.pdf
  - https://github.com/Emad-Salehi/Developers-Cognitive-Biases-during-Code-Review
  - https://arxiv.org/html/2503.21455v1
---

## 정의

같은 리뷰어가 **같은 산출물을 여러 회차 반복 검토**할 때 발생하는 검출력(defect detection power) 손실 구조. 두 성분으로 분해된다.

- **anchoring(고착)**: 1회차에 형성한 판단 프레임이 후속 회차의 탐색 범위를 좁힌다. 리뷰어는 "내가 지난번에 본 것"과 "내가 지난번에 지적한 것"을 축으로 재탐색하며, 그 축 **밖**의 결함은 회차를 더해도 발견 확률이 오르지 않는다.
- **fresh-eyes 상실**: 새 리뷰어(또는 문맥이 리셋된 동일 리뷰어)는 이전 판단을 모르므로 탐색 분포가 독립적이다. 반복 회차에서 이 독립성이 사라지면, 회차 수가 늘어도 **관측면이 다중화되지 않는다** — 즉 회차 N+1 은 회차 N 의 재표집이지 새 표본이 아니다.

핵심 명제 = **"회차를 더하는 것 ≠ 관측면을 더하는 것"**. 같은 관측면에서의 반복은 검출력을 거의 늘리지 않으면서 비용은 선형으로 늘린다.

## 컨텍스트

이 구조는 소프트웨어 검사(inspection) 문헌에서 두 갈래로 확인된다.

**(1) 재검사(reinspection)의 수확 체감** — Biffl·Halling·Köhle 의 대규모 통제 실험(요구사항 문서를 31개 팀이 1차 검사 후 결함 제거, 이어 재검사)은 재검사의 **benefit 과 net gain 이 1차 검사보다 유의하게 낮다**고 보고한다. 다만 보수적 비용-편익 가정 아래서도 대부분 팀에서 **net gain 은 양(+)** 이었다. 즉 "2회차는 무가치"가 아니라 **"2회차의 한계 수익은 1회차보다 낮고, 그 크기가 도입 판단의 축"** 이다. *[verified — 출처: Biffl/Halling/Köhle, 재검사 cost-benefit 실험]*

**(2) 결함 추정의 독립성 전제** — capture-recapture 계열 결함 추정(리뷰어 A 발견 수 × B 발견 수 ÷ 중복 수)은 **두 리뷰어의 탐색이 독립**임을 전제한다. 관측면이 겹치면 추정이 붕괴한다. 이 전제는 codeforge 사내에서도 이미 실증적으로 깨진 적이 있다 — 3자 전원이 같은 결함을 놓친 사례에서 원인은 인원 부족이 아니라 **관측면 동일(다중화 이득 0)** 이었다.

**(3) 인지 편향의 실증 상태는 mixed** — 코드 리뷰에서 availability / anchoring 편향의 존재를 조사한 연구는 리뷰어가 이전 코멘트를 정보원으로 쓰면서도 **그것이 편향원이 될 수 있음을 스스로 경계**한다는 관찰을 남긴다. 편향의 존재를 단정적으로 확립한 것은 아니다. *[hypothesis — 편향 효과 크기는 단정 불가, 방향성만 채택]*

**(4) LLM 리뷰어의 회차 간 분산** — 동일 프롬프트·동일 코드베이스에 대한 반복 실행이 회차마다 다른 발견 집합을 낸다는 산업 관찰이 있다(예: 동일 3회 실행이 각각 다른 개수의 발견). 이는 fresh 세션이 anchor 를 리셋해 **탐색 분포를 재추첨**함을 시사한다. *[hypothesis — 단일 비학술 출처, 정량치 미채택]*

## 핵심 규칙

- **P1 — 반복 회차의 한계 수익은 체감한다**: N+1 회차의 기대 발견은 N 회차보다 작다. 이는 리뷰어를 재사용하든 새로 만들든 성립하는 기저 효과이며, 재사용은 여기에 anchoring 성분을 **추가**한다.
- **P2 — 검출력 다중화는 회차 수가 아니라 관측면 수의 함수다**: 독립 관측면을 늘려야 검출력이 는다. 같은 문맥을 이어받은 재개 회차는 관측면을 늘리지 않는다.
- **P3 — 부채는 회차 성격에 따라 비대칭이다**: 회차가 **이전 지적의 수정 확인**(narrow verification)이면 anchoring 은 오히려 자산이다(무엇을 확인해야 하는지 정확히 안다). 회차가 **미발견 결함의 재탐색**(broad re-detection)이면 anchoring 은 순부채다. 두 성격을 같은 채널로 처리하면 부채가 자산으로 위장된다.
- **P4 — 원인이 판독면 오류면 문맥 보존이 오염원이다**: 직전 회차가 잘못된 전제(낡은 파일·오해한 계약)를 붙잡고 있었다면, 그 문맥의 보존은 오류의 보존이다. 이 경우 재사용은 비용 절감이 아니라 **결함 고착 비용 지불**이다.
- **P5 — 검출력 주장은 falsify 후에만**: "재사용해도 검출력 동일"은 관측 가능한 반증 설계(예: 알려진 결함 seeding 후 재개 회차 vs fresh 회차의 검출 대조) 없이 단정 불가. 비용 절감은 계측으로 보이기 쉽고 검출력 손실은 보이지 않으므로, **비대칭 가시성** 자체가 판단을 왜곡한다.
- **P6 — 최소 1 독립 관측면 보존**: 비용 최적화가 전 회차·전 리뷰어를 재사용으로 덮으면 독립 peer 구조가 소멸한다. 어떤 최적화도 "독립 peer 최소 1"을 잠식하지 않는 것이 보수 안전 방향이다.

## 경계

- **In scope**: 동일 리뷰어가 같은 산출물을 반복 검토할 때의 검출력 손실 구조와 그 성분 분해. 재검사 수확 체감의 개념적 근거.
- **Out of scope**:
  - **재개 기제 자체의 비용·API 의미론** — `agent-resumption-vs-respawn` 소유(disjoint 축).
  - **peer 구성 정책의 실제 배선**(누가 몇 명, 어느 lane 에) — 리뷰 lane governance 영역.
  - **정량 효과 크기** — 본 concept 은 방향(체감·고착)만 확립한다. 사내 정량은 통제 실험 산출물이지 concept 의 내용이 아니다.
  - **인간 리뷰어 ↔ LLM 리뷰어 등가성** — 문헌은 인간 대상이며, LLM 에의 전이는 방향 시사이지 검증된 등가가 아니다. *[hypothesis]*
- **Anti-pattern**:
  - 회차 수 증가를 검출력 증가로 계상(P2 위반).
  - narrow verification 과 broad re-detection 을 같은 채널로 처리(P3 위반).
  - 비용 절감만 계측하고 검출력을 미계측한 채 "손실 없음" 단정(P5 위반 — 비대칭 가시성).
  - 전 회차 재사용으로 독립 peer 를 0 으로 만듦(P6 위반).
  - 판독면 stale 이 원인인 회차를 재개로 처리(P4 위반 — 오류 고착).

## 관련 ADR

- **ADR-119** research-before-claims — P5(검출력 주장 = falsify 후 단정)의 근거 규율.
- **ADR-070 / ADR-081** dual-peer 리뷰 축 — P6(독립 peer 최소 1 보존)이 잠식해서는 안 되는 기존 구조.
- **ADR-125** 요구사항리뷰 lane — 다출처·독립 검증이 관측면 다중화로 기능하는 선례.
- **CFP-2946**(carrier_story) — 재개 채널 도입 시 이 부채가 처음으로 결정면에 오른 case.

## 변경 이력

- 2026-08-12 KST — 초기 작성(CFP-2946 요구사항 lane, ResearcherAgent). 재검사 수확 체감 실험 + capture-recapture 독립성 전제 + 코드리뷰 편향 연구(mixed evidence) + LLM 회차 분산 관찰을 근거로 P1-P6 codify. 사내 "관측면 동일 → 다중화 이득 0" 선례와 접합.
