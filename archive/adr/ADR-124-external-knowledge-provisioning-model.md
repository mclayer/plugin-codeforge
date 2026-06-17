---
adr_number: 124
title: 외부지식 충당 3-단계 모델 — 언제·누가 외부지식을 조달하는가 거버넌스
status: Accepted
category: governance
date: 2026-06-17
carrier_story: CFP-2325
parent_epic: "mclayer/plugin-codeforge#2324"
is_transitional: false
related_stories:
  - CFP-2325  # 본 ADR 신설 carrier (Epic CFP-2324 S1)
related_adrs:
  - ADR-046  # §결정 1·4 — Researcher 3 mandate 의 요구사항 lane 시점이 단계① 묶음. 본 ADR 은 적극 탐색 default skew 에 demand-anchored frame 을 더한 정밀화/강화 (약화 아님)
  - ADR-119  # §결정 5·6 — 원칙(보편) ↔ 실행(전담) 분리를 단계②③ lane-disjoint 정합으로 명문화. §결정 6 "조사했으므로 옳다 단정 금지" = 검사연극 금지 SSOT
  - ADR-056  # §결정 1·4·5 — concept/ 디렉터리 silo = by-design indirection (§6 compact summary single read surface). 결함 재규정 비대상
  - ADR-039  # §결정 1·2 — spawn = Orchestrator 전용 binary always-spawn + closed 4-entry whitelist. lane 개수 axis 와 disjoint (spawn mechanism 무변), amendment 불요
  - ADR-121  # §결정 1 — 배포·배포리뷰 2 lane 폐지 결정. 단계③ 배포리뷰 미적용 사유 (폐지 결정·deprecation 진행 중 + production 경험적 측정 무의존)
  - ADR-058  # §결정 5 — 약화 evidence-gate. 본 ADR 의 단계① 정밀화가 ratchet 강화 방향임을 보증
related_files:
  - archive/adr/ADR-124-external-knowledge-provisioning-model.md
  - skills/review-responsibility/SKILL.md  # 단계③ 매트릭스 요약 mirror (SSOT = 본 ADR)
  - CLAUDE.md  # 핵심 흐름 요구사항리뷰 lane 도입 근거 서술
amendments: []
amendment_log: []
---

# ADR-124: 외부지식 충당 3-단계 모델

## 상태

Accepted (2026-06-17 KST, CFP-2325 carrier — Epic [#2324](https://github.com/mclayer/plugin-codeforge/issues/2324) S1). `is_transitional: false` — 영구 거버넌스 결정 기록.

## 본질 선언

> **외부지식을 codeforge 흐름의 어디에서·누가 충당하는지를 3-단계로 규정한다.** ① 개념 정립·요구사항 재편 (요구사항 lane, ResearcherAgent) — 능동적 unknown-unknown 탐구, 좁은 just-in-case. ② 결정 범위에 한정한 얕은(shallow) 조사 (각 lane 자가 충당) — 결정 직전 known-unknown 의 즉응 보강. ③ 깊은(deep) 다출처 검증 (리뷰 게이트 + 후순위 on-demand) — adversarial 검증 + 출처 인용. 본 ADR 은 이 3-단계의 **경계·근거·적합도만** 박제하며, 실 게이트 trigger·lane 배선·차등 실구현은 후속 Story (S2~S5) 에서 다룬다.

## 어휘 충돌 회피 (필수 선언)

본 ADR 전체에서 "tier" 라는 영어 단어를 **쓰지 않고 "단계" 또는 "레벨"** 로 칭한다. 이유는 codeforge 안에 이미 같은 글자를 쓰는 두 개념이 있어 혼선을 막기 위함이다.

- model-tier (ADR-042 Agent model selection policy) — 에이전트가 쓰는 모델 등급 (Opus / Sonnet / Haiku 등).
- consumer Tier (consumer 도입 등급) — consumer 프로젝트의 도입 단계 분류.

본 ADR 의 "3-단계" 는 위 둘과 무관한 **외부지식 충당 시점·주체의 3 분기**다. Story §1 원문의 "3-tier provisioning" 표현은 본 ADR 안에서 전부 "외부지식 충당 3-단계" 로 재서술한다.

## 컨텍스트

codeforge 는 외부지식 (모델 training 으로는 보장되지 않는 산업·학계·표준·벤더·취약점 사실) 을 흐름의 여러 지점에서 다룬다. 그러나 "외부지식을 *언제 누가* 충당하는가" 의 거버넌스가 단일 SSOT 로 박제되지 않아, 충당 책임이 단계마다 암묵적이었다.

기존 자산은 다음과 같다.

| 기존 자산 | 다루는 것 | 공백 |
|---|---|---|
| ADR-046 (Researcher 3 mandate) | 요구사항 lane 의 개념 정립·심층 탐구·요구사항 재편 | 충당 *시점·주체* 의 단계 구분 부재 |
| ADR-119 (research-before-claims) | 외부지식 단정 전 조사 선행 + 출처 인용 + abstention | "원칙(보편)" 과 "실행(전담)" 분리는 명시했으나 (§결정 5), 단계별 충당 모델로 일반화되지 않음 |
| 각 lane 자가 조사 | 이미 실무에서 일어나는 결정-범위 얕은 조사 | 명문화·경계 부재 |

본 ADR 이 메우는 공백은 두 가지다.

1. **충당 모델 부재** — 외부지식을 능동 정립 (요구사항 단계) / 결정-범위 얕은 조사 (실무 단계) / 깊은 다출처 검증 (리뷰 단계) 의 3-단계로 구분하는 단일 SSOT 가 없었다.
2. **검증 깊이 임계 부재** — 얕은 조사 (②) 와 깊은 검증 (③) 의 분기 기준 (depth 임계) 이 어느 정도인지 박제되지 않았다.

## 결정

### 결정 1 — 외부지식 충당 3-단계 정식 규정

외부지식 충당을 세 단계로 규정한다. 각 단계는 충당 *시점* 과 *주체* 가 다르다.

| 단계 | 시점·위치 | 주체 | 성격 | 좁힘 원칙 |
|---|---|---|---|---|
| ① 개념 정립·요구사항 재편 | 요구사항 lane (흐름 진입부) | ResearcherAgent (ADR-046 3 mandate) | 능동적 unknown-unknown 탐구 — 암묵 개념·도메인 가정 표면화 + 외부 선행사례 조사 후 실현 가능한 요구사항으로 재편 | 좁은 just-in-case — 요구사항 reshape 에 필요한 만큼만 (ADR-046 §결정 4 default skew 의 demand-anchored 정밀화) |
| ② 결정-범위 얕은(shallow) 조사 | 각 lane 자가 충당 (이미 실무에서 발생) | 그 lane 의 에이전트 자신 (Researcher 산출물 인용 또는 자기 도구) | 반응적(reactive) known-unknown — 눈앞 결정 범위에 닿는 사실을 즉시 확인 | 결정 범위로 한정 — 결정에 필요 없는 폭은 조사하지 않음 |
| ③ 깊은(deep) 다출처 검증 | 리뷰 게이트 (주) + on-demand (후순위) | 리뷰 lane 의 검증 주체 | adversarial 검증 — 외부사실에 의존하는 리뷰 결론을 다출처로 교차 검증 + 출처 인용 | 외부사실 의존 지점으로 한정 (결정 2 게이트) |

**②(shallow) ↔ ③(deep) 분기 = 검증 깊이(depth) 임계**: 단계② 는 결정 직전 그 lane 이 자기 결정 범위에 한해 얕게 확인하는 것이고, 단계③ 은 리뷰 시점에 결론의 외부사실 의존을 다출처로 깊이 교차 검증하는 것이다. 두 단계의 분기 기준은 *조사 깊이(depth) 임계* 이며, 그 임계의 정량 trigger 설계는 본 ADR 범위 밖 (S2 게이트 설계 — 결정 5 참조).

**3축 disjoint 관계** (ADR-119 §결정 5 표 + ADR-046 §결정 1 boundary 실측 근거):

- ① ↔ ② = lane 축 + 깊이 축 (요구사항 lane 전담·깊음 ↔ 타 lane 자가·얕음).
- ① ↔ ③ = lane 축 (요구사항 lane ↔ 리뷰 lane).
- ② ↔ ③ = 깊이 축 (얕은 자가 조사 ↔ 깊은 다출처 검증).

### 결정 2 — 깊은 검증의 외부사실 의존 게이트 + 검사연극 금지

단계③ (깊은 다출처 검증) 은 **무조건 발동이 아니다.** 발동 게이트는 "리뷰 결론이 외부사실에 의존하는가" 이다.

- **외부사실에 의존하는 결론**: 그 결론이 산업 표준·벤더 동작·취약점 사실 등 외부지식의 진위에 좌우될 때 → 깊은 다출처 검증 적용.
- **외부사실에 의존하지 않는 결론**: 결론이 내부 코드·내부 규칙·팀 암묵지식만으로 닫히는 곳에서 깊은 외부조사를 강제하면 **검사연극(verification theater)** — 조사 행위 자체가 정당성의 가면이 되는 anti-pattern.

본 게이트는 ADR-119 에서 도출된다.

- ADR-119 §결정 1 (3 검증 대상 분리 matrix) — "외부 지식 주장" row 는 "WebSearch / WebFetch / 공식 문서 조사" 를 "substantive 단정 발화 전" 시점에만 적용한다. 즉 외부지식 단정이 걸려 있는 곳에만 조사가 의무다.
- ADR-119 §결정 6 verbatim — **"'조사했으므로 옳다' 단정 금지"** — 이 문장이 검사연극 금지의 SSOT 다. 조사는 traceability (출처 추적 가능성) + 정직성 (불확실성 명시) 확보 수단이지, 조사 자체가 결론의 정당성을 보증하지 않는다.

따라서 단계③ 의 깊은 검증은 외부사실 의존 지점에만 적용하고, 그 외에는 적용하지 않는다 (검사연극 차단).

### 결정 3 — lane별 깊은 검증 적합도 표 (목표 상태, 발동 잠재력 — 매 Story 강제 아님)

아래 표는 각 lane 에서 단계③ (깊은 다출처 검증) 의 **적합도(잠재력)** 를 박제한 *목표 상태(to-be)* 다. 적합도가 높다는 것은 그 lane 의 리뷰 결론이 외부사실에 의존할 *잠재력* 이 높다는 뜻이지, **매 Story 마다 깊은 검증이 강제 발동된다는 뜻이 아니다** (결정 2 의 외부사실 의존 게이트가 실제 발동을 결정한다 — ADR-119 §결정 8 declarative-only 패턴 정합).

| lane | 깊은 검증 적합도 (잠재력) | 근거 |
|---|---|---|
| 요구사항리뷰 | 高 (주) | 요구사항 결론이 외부 개념·시장·표준 사실에 가장 자주 의존 — 단계③ 의 주 발동 lane |
| 보안테스트 | 高 (기존 web 단계 심화 = 강화) | 취약점·CVE·공급망 사실은 본질적으로 외부지식 — 기존 web 조사 단계를 심화하는 강화 방향 |
| 설계리뷰 | 부분 (외부 기술선택만) | 외부 기술선택 (라이브러리·프로토콜·표준 채택) 결론에만 외부사실 의존. 내부 근거만으로 닫히는 설계 정합성 (ADR 위반·경계·계약 일관성) 은 내부근거-only 경계 보존 — 깊은 외부조사 비대상 |
| 구현리뷰 | 低 (미적용) | 구현 품질·런타임 결함·테스트 품질은 내부 코드 사실 축 — 외부지식 의존 거의 없음, 단계③ 미적용 |
| 배포리뷰 | 미적용 | 배포·배포리뷰 2 lane 은 ADR-121 §결정 1 로 **폐지 결정(deprecated)** 됨 (sunset 2026-07-13 예정, 물리 제거 = Epic #2217 Wave 2 미완 → 현재 deprecation 진행 중). 신규 spawn 비권장 + 배포리뷰는 본질적으로 production 환경의 경험적 측정 (성능·cutover 사후 검증) 이라 외부 다출처 조사에 의존하지 않음 → 적합도 等級 (高/低 등) 을 부여하지 않고 단계③ (깊은 다출처 검증) 적용 대상에서 "미적용" 으로 표기한다 |

> **배포리뷰 행 주의 (필수)**: 배포리뷰는 "적합도 낮음" 이 아니라 "미적용" 이다. 사유는 ① ADR-121 §결정 1 의 **폐지 결정(deprecated)** — sunset 2026-07-13 예정, Wave 2 물리 제거 미완 → 신규 spawn 비권장, ② 배포리뷰가 본질적으로 production 환경의 경험적 측정 (성능·cutover 사후 검증) 이라 단계③ (깊은 다출처 검증) 에 무의존 — 두 가지다. 적합도 等級 (高/低 등) 은 부여하지 않는다. 폐지된 ADR-088 의 현행 근거 인용은 금지한다 (ADR-088 = ADR-121 로 Superseded — stale source).

### 결정 4 — cross-ref 의무 (각 관계 명시)

본 ADR 은 기존 ADR 들을 합성한 거버넌스이며, 어느 기존 ADR 도 약화·재규정하지 않는다. 각 관계를 명시한다.

| 기존 ADR | 인용 지점 | 관계 |
|---|---|---|
| ADR-046 §결정 1·4 | 단계① | **scope 정밀화(강화)** — ADR-046 3 mandate (Concept formulation / Deep exploration / Requirement reshape) 의 요구사항-lane 시점을 단계① 으로 묶는다. §결정 4 의 "적극 탐색 default skew" 에 demand-anchored frame 을 더하는 것은 정밀화이며, Never-skippable invariant 무손상 (ADR-058 §결정 5 ratchet 강화 방향 정합). **"약화" frame 이 아니다.** |
| ADR-119 §결정 5·6 | 단계②③ + 검사연극 게이트 | §결정 5 의 "원칙(보편) ↔ 실행(전담)" 분리를 단계②③ 의 lane-disjoint 정합으로 명문화한다. "실행 전담 = 요구사항 lane 내 deep exploration (ResearcherAgent 전담)" 한정은 그대로 보존하며, 타 lane 은 인용으로 의무 이행 (단계②). §결정 5 표 자체는 흡수하지 않고 인용만 한다. §결정 6 "조사했으므로 옳다 단정 금지" = 검사연극 금지 SSOT (결정 2). |
| ADR-056 (`ADR-056-domain-concept-knowledge-dir-separation.md`) | 단계① 산출 경로 | `concept/` 디렉터리의 "직접 독자 없음" 구조는 **by-design** 이다 — §결정 4 의 §6 compact summary 가 단일 read surface 로 작동하는 indirection 이며 (PLAgent 가 매번 직접 Glob+Read 하는 부담을 제거), §결정 5 의 4중 강제로 소유 경계가 집행된다. **결함으로 재규정하지 않는다.** |
| ADR-039 §결정 1·2 | spawn mechanism | spawn = Orchestrator 전용 binary always-spawn (§결정 1) + closed 4-entry whitelist (§결정 2). 9번째 lane 추가는 spawn *대상의 enumeration 확장* 일 뿐 spawn *mechanism·whitelist* 변경이 아니므로 **disjoint axis** (lane 개수 ≠ spawn mechanism). ADR-039 영향 0 — amendment 불요. |
| ADR-121 §결정 1 | 단계③ 배포리뷰 | 배포·배포리뷰 2 lane 폐지. 단계③ 의 배포리뷰 "미적용" 사유 (결정 3). |

### 결정 5 — 범위 경계 (S1 한정)

본 ADR (Epic CFP-2324 S1) 은 **원칙·매트릭스·근거만** 박제한다. 아래는 모두 본 ADR 범위 밖이며 후속 Story 에서 다룬다 (scope creep 차단).

| 영역 | 담당 Story |
|---|---|
| 실 게이트 trigger·phase 라벨·lane 배선 (요구사항리뷰 lane 실 wiring, 8→9 카운트 hard-commit) | **S2** |
| 깊은 검증 (deep-research) 차등 실구현 | **S3** |
| ResearcherAgent 재초점 (단계① mandate 조정) | **S4** |
| on-demand 깊은 검증 경로 | **S5** |
| 단계②③ 깊이 임계의 정량 trigger (경계(?) 항목 최종 확정 포함 — 결정 6) | **S2** (게이트 설계) |

### 결정 6 — "외부사실 의존" 판정 휴리스틱 (operational 정의)

단계③ 발동 여부 (결정 2 게이트) 의 운영 판정을 위한 휴리스틱이다. 이는 ADR-119 §결정 1 matrix 의 "외부 지식 주장" row 를 운영 수준으로 instantiate 한 것이다.

| 판정 | 예시 | 외부사실 의존 |
|---|---|---|
| 의존 O | 팩트체크 / 벤더 동작 / 표준(RFC 등) / CVE·취약점 사실 | 있음 — 단계③ 적용 |
| 의존 X | 팀 암묵지식 / 내부 코드·규칙 사실 | 없음 (repo·내부 축, ADR-119 §결정 1 repo 사실 row) — 단계③ 미적용 |
| 경계 (?) | 시장정보 / 벤치마크 / StackOverflow 등 준-외부 출처 | 경계 — **최종 확정 deferral** |

- **경계(?) 항목**: 위 준-외부 출처가 단계② (얕은 자가 조사) 로 충분한지, 단계③ (깊은 다출처 검증) 까지 필요한지의 최종 확정은 본 ADR 에서 lock-in 하지 않는다. 이는 ②↔③ 깊이 임계 (결정 1) 설계와 결합되므로 **S2 게이트 설계에서 확정하도록 deferral** 한다.
- **abstention escape 정합**: 출처 확보 불가 시 ADR-119 §결정 3.2 의 "확인 불가/추정" 명시 후 진행 (데드락 회피) 을 그대로 따른다.

## 근거

- **충당 모델 단일화**: 외부지식 충당 책임을 시점·주체 기준 3-단계로 박제해, 단계마다 암묵적이던 "누가 언제 충당하는가" 를 명문화한다. 기존 ADR (046/119) 을 합성할 뿐 새 규범을 신설하지 않는다.
- **검사연극 차단**: 깊은 검증을 외부사실 의존 지점에만 적용해, 조사 행위가 정당성의 가면이 되는 anti-pattern (ADR-119 §결정 6) 을 차단한다.
- **약화 0 (ratchet 강화)**: 단계① 의 demand-anchored frame 은 ADR-046 §결정 4 의 적극 탐색 default skew 를 정밀화하는 강화 방향이며, Never-skippable invariant 무손상 (ADR-058 §결정 5 / ADR-064 §결정 7 정합).
- **disjoint 보존**: ADR-039 spawn mechanism, ADR-056 concept silo, ADR-121 배포 폐지 어느 것도 본 ADR 이 침범하지 않는다 (각 disjoint axis 명시).

## 결과

- 외부지식 충당 3-단계의 normative anchor 신설 — 요구사항리뷰 lane 도입 (S2~) 의 근거 SSOT.
- 단계③ (깊은 검증) 매트릭스의 SSOT = 본 ADR. `skills/review-responsibility/SKILL.md` 는 요약 mirror 만 두고 본 ADR 을 cross-ref 한다 (drift 회피).
- mechanical_enforcement_actions: [] — S1 declarative-only. 실 게이트 trigger·lane 배선·차등 실구현 = S2~S5 별 carrier (ADR-054 §결정 6.1 / ADR-119 §결정 8 declarative-only 패턴 정합).

## sunset_justification (ADR-058 §결정 5 — 약화 차단)

본 ADR 은 기존 거버넌스 (ADR-046/119) 의 합성·정밀화이며 약화 0 건이다. ADR-046 의 어느 mandate 도 삭제·완화하지 않고, ADR-119 의 어느 결정도 흡수·약화하지 않으며, 단계① 의 demand-anchored frame 은 적극 탐색 default skew 를 좁히지 않고 frame 만 더하는 강화 방향이다. is_transitional: false (permanent governance anchor). 원복은 별도 Story 의 명시 결정으로만 가능하며 그 경우에도 ADR-058 §결정 5 (약화 시 sunset_justification 의무) 를 따른다.

## 해소 기준

N/A — permanent policy. 후속 이행 추적 = Epic [#2324](https://github.com/mclayer/plugin-codeforge/issues/2324) (S2~S5).

## 관련 파일

- 본 ADR — 외부지식 충당 3-단계 + 깊은 검증 적합도 매트릭스 SSOT
- [ADR-046](ADR-046-researcher-role-redefinition.md) — Researcher 3 mandate (단계① 묶음, 정밀화 대상)
- [ADR-119](ADR-119-research-before-claims.md) — research-before-claims (§결정 5 원칙↔실행 분리 / §결정 6 검사연극 금지)
- [ADR-056](ADR-056-domain-concept-knowledge-dir-separation.md) — concept/ 디렉터리 by-design indirection
- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — spawn mechanism (disjoint axis)
- [ADR-121](ADR-121-deprecate-deploy-lanes.md) — 배포·배포리뷰 lane 폐지 (단계③ 배포리뷰 미적용 사유)
- `skills/review-responsibility/SKILL.md` — 단계③ 매트릭스 요약 mirror
- `CLAUDE.md` — 핵심 흐름 요구사항리뷰 lane 도입 근거 서술
