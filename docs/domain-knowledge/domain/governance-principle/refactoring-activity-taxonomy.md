---
kind: domain_fact
type: domain-knowledge
area: governance-principle
topic_slug: refactoring-activity-taxonomy
title: 리팩터링 2활동 분류 — 설계 리팩터링 vs 구현 리팩터링 시점·메커니즘 분리 원리
status: Active
tags:
  - refactoring
  - design-lane
  - advocacy-architecture
  - refactor-agent
  - activity-taxonomy
  - prevention-layer
related_adrs:
  - ADR-042  # Amendment 13 (CFP-2364 — (d)reusability 1급 축 신설) / Amendment 18+ (CFP-2533 Story B — 소관 이동)
  - ADR-086  # Deputy 신설 결정 framework (axis disjoint)
  - ADR-091  # ArchitectLane DDD vocabulary governance
  - ADR-138  # 설계 리팩터링 결정 방식 debate 격상 (결정 방식 행 GAP fill)
  - ADR-140  # 작성-시점 예방 hygiene 제3 dimension 편입 (예방 층 신설 — 리팩터링 활동 아님·직교)
related_stories:
  - CFP-2364  # Amendment 13 carrier — (d)reusability RefactorAgent 1급 축 신설
  - CFP-2369  # Amendment 14 carrier — 측정 연동 mechanical wire
  - CFP-2533  # Epic carrier — 리팩터링 2활동 분리 (Story B = RefactorAgent 축 재편)
  - CFP-2543  # 설계 리팩터링 debate 격상 — 결정 방식 행 GAP fill
  - CFP-2557  # 제3 dimension(작성-시점 예방 hygiene) 편입 carrier — ADR-140
created: 2026-07-01
updated: 2026-07-02
---

# 리팩터링 2활동 분류 — 설계 리팩터링 vs 구현 리팩터링

## 정의

codeforge 설계-lane 에이전트 advocacy 아키텍처에서 "리팩터링"은 단일 활동이 아니다. **발동 시점·관측 대상·메커니즘**이 근본적으로 다른 두 활동으로 구분된다.

| 구분 | 설계 리팩터링 | 구현 리팩터링 | 작성-시점 예방 hygiene (제3 dimension — 리팩터링 아님·예방, ADR-140) |
|---|---|---|---|
| **발동 시점** | 설계 단계 — 코드 존재 전·설계 스케치 단계 | 구현 완료 후 — 실코드 위에서 계측 | 구현 중 — 코드를 쓰는 그 순간 (검출 이전) |
| **관측 대상** | 구조적 결함 (결합도·경계·패턴) | 중복 (clone·DRY 위반) — 코드 블록 반복 계측 | 관측·계측 없음 — 유입 예정 신규 코드 (재사용 기회·신규 중복·응집/결합 준수) |
| **발화 주체** | RefactorAgent (설계-lane inline, 매 Story) | 구현 리팩터링 triage (Epic-close 1회 배치) | role:dev 워커 self-discipline ($DEVSET 6 md + DeveloperPL spawn packet — ADR-140 §결정 3) |
| **결정 방식 (decision mechanism)** | Codex(proponent·발제)↔Claude(opponent·반대) debate — `blanket_designrefactor`, 설계-time per-Story, verdict judge = ArchitectAgent chief, 3분기(now/defer/drop). anchor `<설계 요소>::<구조 축>` per-Story (ADR-138) | Codex(proponent)↔Claude(opponent) Epic-close execute-and-falsify triage — `blanket_refactor`, verdict judge = PMOAgent, 3분기(now/defer/drop). anchor `<file>:<line>` content-hash cross-Epic drop-ledger (ADR-137) | debate/triage 아님 — declaration-only Wave 1: dev declaration → 기존 dup-local/dup-boundary P1 사후 falsify 2단 (ADR-140 §결정 6) |
| **메커니즘** | 구조 advocacy — 코드 없이도 위반 판단 가능 | 계측 기반 — duplication ratio / rule-of-three 실측 필요 | 행위 규율 — reuse-before-write 탐색 + 신규 중복 유입 차단 + Change Plan 지침 내 응집/결합 준수 (계측 없음) |
| **속하는 축** | (a) Decoupling / (b) Pattern / (c) Interface separation + repo-분해 구조 escalation | (d) Reusability — 중복 제거·공통 추출·DRY/WET | hygiene 4항 — 재사용 탐색 선행 / 신규 중복 유입 금지 / 응집·결합 Change Plan 지침 내 준수 / 임의 구조 재설계 금지(상한) |

> **제3 dimension 주의 (ADR-140 §결정 1)**: 작성-시점 예방 hygiene 은 Fowler refactoring(behavior-preserving 사후 변환)이 **아니다** — 변환 대상 코드가 아직 없는 시점의 유입 차단 규율이라 "제3의 리팩터링 활동"이 아닌 **직교 예방 dimension** 이다. 2활동 분류(설계/구현 리팩터링)는 무변경. 예방(작성-시점) → 검출(리뷰 dup P1·설계 debate) → 정리(Epic-close triage) 의 layered defense 관계.

## 컨텍스트

Epic CFP-2533 은 "리팩터링"을 관측 시점 기준으로 두 활동으로 분리한다. Amendment 13 (CFP-2364) 이 (d) Reusability 를 RefactorAgent 1급 축으로 신설했고, Amendment 14 (CFP-2369) 가 측정을 mechanical wire 했으나, (d) 축의 *측정* 성격은 실코드 관측 의존이라 설계 단계 inline advocacy 위치와 부정합이었다. Story B (CFP-2539) 가 그 부정합을 소관 이동으로 해소한다.

### 소관 이동 연대기 (ADR-042)

- **Amendment 13 (CFP-2364, 2026-06-19)**: (d) Reusability를 RefactorAgent 1급 축으로 신설. ISO/IEC 25010 Maintainability 5축 중 Reusability gap 충당.
- **Amendment 14 (CFP-2369, 2026-06-19)**: (d) 측정 연동 Phase-2 mechanical wire — `check-duplication-ratio.sh` warning-tier CI 구동.
- **CFP-2533 Story B (2026-07-01, ADR-042 Amendment 18)**: (d) Reusability *측정* 축을 설계-lane inline(RefactorAgent)에서 구현 리팩터링 triage(Epic-close 배치)로 소관 이동. repo-분해 구조 escalation 축은 RefactorAgent 설계-시점 존치. **폐지(deprecate) 아님** — 발동 주체·시점·메커니즘의 재배치. 축 자체는 구현 리팩터링 안에서 존속.

## 핵심 규칙

### 설계 리팩터링 (구조 3축 + repo-분해 구조 escalation)

**(a) Decoupling, (b) Pattern, (c) Interface separation** + **repo-분해 구조 escalation**은 코드 없이도 구조적으로 판단할 수 있다.

- God Class 후보: 책임 수 / 의존 방향 설계 스케치에서 식별 가능
- Hexagonal 패턴 미준수: 레이어 경계 설계에서 확인 가능
- 포트 없는 직접 타입 의존: 인터페이스 설계 다이어그램에서 확인 가능
- repo-분해: 응집 cluster → 별 deploy/ownership 단위 분리는 macro-boundary 로 설계 스케치에서 관측 가능

이 축들은 구현 코드가 존재하면 더 정밀해지지만, **설계 단계에서 이미 경고 발화가 가능**하다. 따라서 RefactorAgent가 설계-lane inline에서 매 Story advocacy를 수행하는 것이 도메인 정합이다.

### 구현 리팩터링 ((d) Reusability 측정 축)

**(d) Reusability** — 중복 제거·공통 추출·DRY/WET — 는 실코드 없이 선험적으로 존재할 수 없다.

**핵심 원리**: 중복(clone)은 코드 블록이 3회 이상 반복돼야 rule-of-three가 발동하고, duplication ratio는 코드 라인 대비 수치다. 설계 단계에서는 "공통화 잠재력"을 추론할 수 있을 뿐, falsifiable 계측(duplication ratio 수치)은 구현 후에야 가능하다.

이 시점 의존성이 (d) 축의 소관 이동 근거다:
- 설계-lane inline에서 발화 → 계측 근거 없이 추론에 의존 (ADR-119 research-before-claims 위반 위험)
- 구현 완료 후 triage → `check-duplication-ratio.sh` 실측 수치 기반 falsifiable 발화 가능 (Epic-close Codex↔Claude execute-and-falsify triage)

### 작성-시점 예방 hygiene (제3 dimension — ADR-140, CFP-2557)

예방 층은 role:dev 워커가 코드를 쓰는 순간의 행위 규율이다 — hygiene 4항(재사용 탐색 선행 / 신규 중복 유입 금지 / 응집·결합 Change Plan 지침 내 준수 / 임의 구조 재설계 금지 상한). 계측하지 않으므로 "(d) 측정 축은 실코드 관측 의존" premise(위 구현 리팩터링 절)와 무모순 — Amd18 측정-이관 결정을 뒤집지 않는다 (사후 계측 ⊥ 사전 억제). 실행 SSOT = $DEVSET 6 agent md + DeveloperPL spawn packet, 정책 SSOT = ADR-140. dev authority 경계 무변경(설계 금지·에스컬레이션 경로 존치, ADR-140 §결정 7).

### 관련 용어

- **rule-of-three**: 동일·유사 코드 블록 3회 이상 반복 시 공통화 제안 트리거. **이중 용법 주의 (ADR-140 §결정 4)** — ① 검출-트리거 용법(본 정의): 실코드 계측 후 3회 도달 시 공통화 *제안* (구현 리팩터링 소관) ② 예방 용법: 작성-시점에는 정량 임계(3회)의 기계적 전진배치를 **금지**하고 "reuse-before-write 탐색 습관 + over-DRY(성급한 추상화) 금지 균형"으로만 번역 — 2번째 작성 시 1번째 존재를 탐색해 공통화 가치를 *판단*(추출 강제 아님). 같은 용어, 정반대 방향(검출 ⊥ 억제) — 혼용 금지
- **duplication ratio**: 중복 라인 비율 (CFP-2369 `check-duplication-ratio.sh` warning-tier 산출)
- **advocacy**: 설계-lane SubAgent의 압력 식별·제안 역할 (경계 확정 = ModuleArch authority, 불변)
- **axis disjoint**: RefactorAgent advocacy ↔ ModuleArchitectAgent boundary authority의 orthogonal 분리 (CFP-2364 codify — (d) 이관 후에도 (a)(b)(c) + repo-분해 전체에 상속됨)

## 경계

- **소관 이동 ≠ 폐지**: (d) reusability 개념 자체를 없애는 것이 아니다. "설계 단계 inline advocacy" → "구현 후 triage 배치"로 위치를 바꾸는 것이다.
- **axis disjoint 불변**: (d) 측정 축 제거 후 RefactorAgent.md의 disjoint 표현에서 reusability 측정을 제거하더라도, "RefactorAgent advocacy ↔ ModuleArch boundary authority" 이분 원칙은 (a)(b)(c) 구조 3축 + repo-분해 전체에 계속 적용된다. (a)(b)(c)에서도 module boundary consult 표식이 필요한 경우가 존재한다 (예: 결합도 해소 시 module boundary 판단이 필요한 경우).
- **repo-분해는 존치, 측정 축만 이관**: repo-level 분해(macro-structural boundary)는 설계-시점 관측 가능이라 RefactorAgent 존치. 중복/재사용 *측정*(실코드 관측 의존)만 구현 리팩터링(Story C)으로 이동. 두 축은 관측 시점·대상 disjoint.
- **CodebaseMapper 무영향**: Mapper는 fact source 변호자(file structure / API surface / dependency graph)이며 advocacy axis 재편과 무관하다. Mapper의 역할은 RefactorAgent의 축 구성에 종속되지 않는다.

## 관련 ADR

- ADR-042 §Amendment 13/14/18 — (d) Reusability 신설 · 측정 연동 · 측정 축 소관 이동 결정 SSOT
- ADR-086 — Deputy 신설 결정 framework (axis disjoint lens; 측정 축 축소 = explicit scope 열거 → FULL self-application)
- ADR-091 §결정 1 — RefactorAgent DDD pattern mapping (frozen 표 + CFP-2539 역주석)
- `plugins/codeforge-design/agents/RefactorAgent.md` — 현행 SSOT (구조 3축 + repo-분해 구조 escalation)
- `plugins/codeforge-design/agents/CodebaseMapperAgent.md` — fact source 변호자 역할 (불변)
- ADR-138 — 설계 리팩터링 결정 방식 Codex↔Claude debate 격상 (결정 방식 = blanket_designrefactor debate, verdict judge = ArchitectAgent chief, anchor per-Story). GAP fill carrier — 결정 방식 행 신설.
- ADR-140 — 작성-시점 예방 hygiene 제3 dimension 편입 (예방 층 신설 — 리팩터링 활동 아님·직교). $DEVSET dev md + packet 착지, rule-of-three 이중 용법 분리, declaration-only Wave 1.

## 변경 이력

- 2026-07-01 (CFP-2533 Story B / CFP-2539) — 신규 작성. 리팩터링 2활동 분류(설계 리팩터링 vs 구현 리팩터링) 시점·메커니즘 분리 원리 codify. RefactorAgent (d)reusability 측정 축 → 구현 리팩터링(Story C) 소관 이동 + repo-분해 구조 escalation 존치 (ADR-042 Amendment 18) 도메인 근거 SSOT.
- 2026-07-01 (CFP-2543 / ADR-138) — "결정 방식 (decision mechanism)" 행 신설 (GAP fill): 설계 리팩터링 = blanket_designrefactor debate(verdict judge=ArchitectAgent chief, per-Story) / 구현 리팩터링 = blanket_refactor triage(verdict judge=PMOAgent, cross-Epic). 두 활동 결정 방식 대칭화.
- 2026-07-02 (CFP-2557 / ADR-140) — 제3 dimension(작성-시점 예방 hygiene) 열 신설 (CFP-2543 dimension 확장 동형): 예방 층 = 리팩터링 활동 아닌 직교 예방 dimension (Fowler behavior-preserving 비해당, 2활동 분류 무변경). rule-of-three 이중 용법(검출 트리거 ⊥ 예방 탐색 습관) 분리 note. layered defense(예방→검출→정리) 관계 명시.
