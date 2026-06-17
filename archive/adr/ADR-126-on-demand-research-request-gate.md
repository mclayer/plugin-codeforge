---
adr_number: 126
title: on-demand 깊은 조사 보충 경로 — research-request-gate 거버넌스 (단계③ on-demand)
status: Accepted
category: governance
date: 2026-06-18
carrier_story: CFP-2329
parent_epic: "mclayer/plugin-codeforge#2324"
is_transitional: false
related_stories:
  - CFP-2329  # 본 ADR 신설 carrier (Epic CFP-2324 S5 — 마지막 child)
related_adrs:
  - ADR-039  # §결정 1·2 — spawn=Orchestrator 전용 binary always-spawn + closed 4-entry inline whitelist. 본 ADR 이 §결정 1/2 정합을 자체 재논증 (ADR-124 §결정 4 disjoint 논리는 lane 개수 axis 한정이라 차용 불가). Amendment 4 = skill body primitive ↔ whitelist 무손상 선례
  - ADR-124  # §결정 1 단계③ "리뷰 게이트(주) + on-demand(후순위)" / §결정 2 외부사실 의존 게이트 + 검사연극 금지 / §결정 5 "on-demand 깊은 검증 경로 = S5" 위임 / §결정 6 외부사실 의존 휴리스틱 / Amendment 1 A1-3 code lane web 금지 [P0]
  - ADR-125  # §결정 6 — on-demand(S5) ↔ review-time(S2/S3) disjoint SSOT. §결정 4 ADR-052 cross-ref(Amendment 격상 불요) 처리 선례 = 본 ADR 형식 판정 모델
  - ADR-109  # in-process 429 mitigation framework — skill body 가 operational primitive 보유하되 whitelist 무손상 (Amendment 4 경유 binding precedent)
  - ADR-046  # Amendment 2 — Researcher 재초점. 하류 기술수요 = review-time deep(S3) + on-demand(S5) 담당. 본 ADR = 그 하류 기술수요의 작업중 pull 채널
  - ADR-058  # §결정 5 — 약화 evidence-gate. 본 ADR = additive skill 신설 + cross-ref only, strengthen 방향 → sunset_justification null
  - ADR-119  # §결정 6 검사연극 금지 SSOT / §결정 3.2 abstention escape
  - ADR-037  # plugin version bump rule — 신규 skill = skills/ 자동 발견, marketplace 4필드 무영향, CLAUDE.md 레인 진입 표 미등재 → bump 불요
related_files:
  - archive/adr/ADR-126-on-demand-research-request-gate.md
  - skills/research-request-gate/SKILL.md  # 본 ADR 정책의 운영 절차 carrier
  - skills/jira-decision-channel/SKILL.md  # caller scope Orchestrator 한정 선례
  - skills/rate-limit-429-mitigation/SKILL.md  # skill body primitive ↔ whitelist 무손상 선례
  - CLAUDE.md  # 결정·대화 원칙 절 1줄 cross-ref (레인 진입 표 미등재 — on-demand 는 lane 진입 아닌 작업중 mechanism)
amendment_log: []
---

# ADR-126: on-demand 깊은 조사 보충 경로 — research-request-gate 거버넌스

## 상태

Accepted (2026-06-18 KST, CFP-2329 carrier — Epic [#2324](https://github.com/mclayer/plugin-codeforge/issues/2324) S5, 마지막 child). `is_transitional: false` — 영구 거버넌스 결정 기록.

## 본질 선언

> **외부지식 충당 3-단계 모델(ADR-124 §결정 1)의 단계③(깊은 다출처 검증)의 두 경로 중 on-demand(pull) 경로의 실 mechanism 과 게이트 절차를 신설한다.** lane 이 작업 *중* 외부사실 의존 known-unknown 으로 막혔을 때, "lane 이 scope-clear 조사 요청을 올림 → Orchestrator 가 문지기로 게이트 심사 → harness-native deep-research 실행(Orchestrator 전용) → cited 결과를 요청 lane 재spawn packet 으로 주입" 의 경유 구조를 박제한다. **새 mechanism 이지만 새 권한은 0** — 모든 단계가 기존 권한 경계(spawn = Orchestrator 전용 / Skill 호출 = Orchestrator inline whitelist 무손상 / 주입 = packet 동형)의 합법적 조합이다. 본 ADR 의 핵심 논증은 그 "새 mechanism = 기존 invariant 의 합법적 조합" 을 ADR-039 §결정 1/2 에 대해 **자체 재논증**(§결정 2)하는 것이다.

## 어휘 충돌 회피 (필수 선언)

- "단계①②③" = ADR-124 외부지식 충당 3-단계 (model-tier / consumer Tier 와 무관 — ADR-124 어휘 충돌 회피 절 계승).
- "on-demand" = lane 이 작업 *중* 막혔을 때 깊은 조사를 끌어오는(pull) 경로 (review-time 자동 게이트와 대비).
- "deep-research" = Claude Code harness 가 제공하는 native system skill (다출처 web 조사 + adversarial 검증 + 출처 인용). codeforge 자체 구현 아님 — repo `skills/` 에 파일 부재 (실측 확정), 호출 경로만 본 ADR 이 신설.

## 컨텍스트

ADR-124(S1)가 외부지식 충당 3-단계를 박제하며 단계③(깊은 다출처 검증)을 두 경로로 식별했다 — **리뷰 게이트(주) + on-demand(후순위)** (ADR-124 §결정 1 표 단계③ 행). 리뷰 게이트 경로는 S2(ADR-125 요구사항리뷰 lane) + S3(ADR-124 Amendment 1 차등 실구현)으로 이행 완료됐다. on-demand 경로는 ADR-124 §결정 5 표가 명시적으로 **S5 로 위임**했다 ("on-demand 깊은 검증 경로 = S5").

본 ADR(S5, Epic 마지막 child)이 그 on-demand 경로의 실 mechanism + 게이트 절차를 신설한다.

| 기존 자산 | 다루는 것 | 본 ADR 이 메우는 공백 |
|---|---|---|
| ADR-124 §결정 1 단계③ 행 | "리뷰 게이트(주) + on-demand(후순위)" 분기 식별 | on-demand 경로의 *실 mechanism* 미구현 |
| ADR-125 §결정 6 | on-demand(S5) ↔ review-time disjoint 명문 | on-demand 의 요청 형식·게이트·실행·주입 절차 부재 |
| ADR-039 §결정 1·2 | spawn = Orchestrator 전용 + closed 4-entry whitelist | 새 mechanism(요청→게이트→주입)이 §결정 1/2 와 정합하는지 *자체 논증* 부재 (ADR-124 §결정 4 disjoint 논리는 lane 개수 axis 한정이라 차용 불가) |

## 결정

### 결정 1 — on-demand 단계③ 경로 정식 신설 (요청 → 게이트 → 실행 → 주입)

ADR-124 §결정 1 단계③ 행 "리뷰 게이트(주) + on-demand(후순위)" 의 **on-demand 행** 을 본 ADR 이 carrier 한다. on-demand 경로의 실 mechanism 을 4 단계로 규정한다.

| 단계 | 행위 | 주체 |
|---|---|---|
| `request` | lane 이 scope-clear 조사 요청(단일 질문 + 얕은조사 불가 사유 + 외부사실 의존 지점)을 올림 | lane (요청만) |
| `gate` | Orchestrator 가 문지기로 게이트 3-규칙 심사 | Orchestrator |
| `execute` | harness-native deep-research skill 호출 | Orchestrator (전용) |
| `inject` | cited 결과를 요청 lane 재spawn packet block 으로 주입 | Orchestrator |

**Orchestrator 게이트 3-규칙** (게이트 = 문지기, 조사 주제 기획자 아님 — demand 출처 = lane):

1. **scope 명확성 검증** — 단일·평문 질문 / anchor·외부사실 의존 지점 특정 여부. 묶음 질문·모호 범위 = 반려.
2. **shallow-vs-deep 문턱** — 얕은 자가조사(단계②)로 처리될 일이면 "얕은 셀프서비스로 처리" 통보(반려).
3. **흐린 요청 반려** — ①② 충족하나 질문이 흐리면 구체화 요구 후 재요청.

반려는 거버넌스 결손이 아니라 게이트의 정상 동작이다 — on-demand 게이트 자체가 검사연극 차단 장치(§결정 6). 운영 절차 SSOT = `skills/research-request-gate/SKILL.md`.

### 결정 2 — ADR-039 §결정 1/2 정합 자체 재논증 [P0 핵심]

본 §결정이 본 ADR 의 핵심이다. ADR-124 §결정 4 의 disjoint 논리를 **차용하지 않고** 새 mechanism 의 성격에 맞춰 ADR-039 §결정 1/2 와의 정합을 처음부터 재논증한다.

**(a) ADR-124 §결정 4 disjoint 논리는 차용 불가 (명시).**

ADR-124 §결정 4 표 ADR-039 행은 "9번째 lane 추가는 spawn *대상의 enumeration 확장* 일 뿐 spawn *mechanism·whitelist* 변경이 아니므로 disjoint axis (lane 개수 ≠ spawn mechanism). ADR-039 영향 0 — amendment 불요" 라고 논증한다. 이 논거는 **lane *개수* axis 한정**이다. S5 는 lane 개수를 늘리는 것이 아니라 **새 mechanism(요청 → 게이트 → 주입)을 도입**한다. 따라서 ADR-124 §결정 4 의 disjoint 문장을 재인용하는 것만으로는 S5 의 ADR-039 정합을 보증할 수 없다 — 새 mechanism 의 성격에 맞춘 독립 논거가 필요하다.

**(b) 자체 재논증 (독립 논거 3 개).**

① **lane 자가-spawn 불가 → "lane 은 요청만, 실행은 Orchestrator" = 기존 invariant 의 합법적 귀결 (새 권한 0).**
ADR-039 §결정 1 은 spawn = Orchestrator 전용이고, 회피 대안 C 는 "subagent → Agent tool 호출 금지"(lane subagent 가 스스로 spawn 불가)를 명문화한다. lane(subagent)이 스스로 deep-research 를 호출(=spawn)하면 재귀-spawn limit 와 직접 충돌한다. 따라서 "lane 은 요청만 올리고 실행(deep-research 호출)은 spawn 독점 주체인 Orchestrator 가 한다" 는 구조는 **새 제약·새 권한이 아니라 기존 invariant 의 자연 귀결**이다. on-demand mechanism 은 ADR-039 §결정 1 의 spawn 독점을 침범하지 않고 오히려 그 위에서 작동한다.

② **Orchestrator 의 deep-research Skill 호출은 §결정 1 "수정 작업" closed enum 비해당 → §결정 2 whitelist axis 와 disjoint.**
ADR-039 §결정 1 의 "수정 작업" 은 closed enumeration(file edit/write / GitHub state change / Story file write / FIX Ledger / lane evidence / gate·phase label / workflow yaml / ADR·Change Plan·domain write / trivial Read)이다. Skill 호출 자체는 file system·GitHub state mutation 을 **발화하지 않는다** → §결정 1 "수정 작업" closed enum 에 해당하지 않는다. 따라서 Skill 호출은 §결정 2 inline whitelist 의 평가 axis(수정 작업을 inline 으로 할 것인가 spawn 위임할 것인가)와 **disjoint** 이다. (deep-research 호출의 *결과*로 발생하는 codeforge 측 mutation — Story 갱신·요청 lane 재spawn — 은 별도 행위로 각자 spawn / inline-whitelist 규율을 따른다. 호출 자체와 결과 mutation 의 분리.)

③ **따라서 §결정 1 binary always-spawn 무손상 + §결정 2 closed 4-entry whitelist 무손상.**
①에 의해 §결정 1 spawn 독점이 보존되고(lane 자가-spawn 0, 실행은 Orchestrator), ②에 의해 §결정 2 closed 4-entry whitelist 가 무손상이다(Skill 호출은 수정 작업 아니라 whitelist axis 비해당). on-demand mechanism 은 ADR-039 의 두 invariant 어느 것도 약화·확장하지 않는다.

**(c) 결론** — ADR-039 §결정 1/2 는 본 ADR 의 새 mechanism 에 의해 **0 변경**이다. 이 정합은 ADR-124 §결정 4 의 lane-개수-axis disjoint 논리를 차용한 것이 아니라, 위 ①②③ 의 독립 논거로 자체 재논증된 것이다.

### 결정 3 — deep-research 호출 = whitelist 5번째 entry 무신설 (rate-limit Amendment 4 선례 동형)

Orchestrator 의 deep-research Skill 호출은 ADR-039 §결정 2 inline whitelist 의 **5번째 entry 를 신설하지 않는다.** 이는 rate-limit-429-mitigation skill 선례(ADR-039 §결정 9 / Amendment 4)와 **동형**이다.

- Amendment 4 verbatim 요지: "§결정 2 inline whitelist closed 4-entry enumeration 무변경 (5번째 entry 신설 0 — chief 결정 … retry primitive 위치 = `codeforge:rate-limit-429-mitigation` skill body)". InfraOp 의 "ADR-039 5번째 entry 신설" advocacy 는 REJECTED 됐다.
- 동형 적용: research-request-gate skill body 가 on-demand 절차의 **operational primitive**(요청 형식·게이트 3-규칙·실행·주입)를 보유하되, ADR-039 §결정 2 closed 4-entry whitelist 는 무손상이다. Skill 호출은 mutation 미발화 → §결정 1 "수정 작업" 비해당(§결정 2 (b)②) → whitelist 5번째 entry 신설 대상 아님.
- ADR-039 §결정 2 L145 verbatim "본 closed enumeration 가 future 'Skill 호출 / Glob / Grep / Read tool 분류 enum 확장' 압박을 차단" 과 정합 — Skill 호출은 whitelist enum 확장이 아니라 4 entry 외 행위(수정 작업 비해당)로 routing 된다.
- **1줄 명문**: deep-research Skill 호출 = whitelist 5번째 entry 무신설 (skill body = primitive, closed 4-entry 무손상).

### 결정 4 — on-demand 가 code lane 웹금지(ADR-124 Amendment 1 A1-3)를 우회로로 깨지 않음

on-demand 경로 신설이 **구현리뷰(code lane)의 web 전면금지를 흔들지 않는다.**

- ADR-124 Amendment 1 A1-3 [P0] = code lane 워커의 WebSearch/WebFetch 전면 금지 유지, web 허용 lane = `security` + `requirements-review` + (design 좁은 예외) 3 종.
- 요청 lane 이 code(구현리뷰)이면, deep 조사 결과를 주입해도 **code 리뷰 결론은 내부 코드 사실 축으로 닫힌다**(구현 품질·런타임 결함·테스트 품질 = 외부지식 의존 거의 없음, ADR-124 §결정 3 근거). code lane 의 작업중 막힘이 외부지식 의존이 아닌데 on-demand deep 조사를 끼워 넣으면 검사연극 + 대칭 붕괴다.
- on-demand 가 web 금지 lane 에 web 조사를 우회 주입하는 채널이 되어서는 안 된다 — web 허용 lane 3 종 경계는 on-demand 경로에서도 불변이다.
- S3 차등 ↔ S5 on-demand 의 axis 분리: S3 = 적용 깊이 차등(게이트 시점 자동) / S5 = 호출 경로(작업중 pull). 같은 deep-research 를 쓰되 axis 가 다르며, 둘 다 code lane web 금지를 보존한다.

### 결정 5 — review-time deep(S2/S3) ↔ on-demand(S5) disjoint

단계③ 의 두 경로는 **disjoint** 다 (SSOT = ADR-125 §결정 6 "on-demand 경로(S5) 와 disjoint … 깊이의 차등 메커니즘 실구현은 S3 로 보존").

| 축 | review-time(자동 게이트) | on-demand(pull) |
|---|---|---|
| trigger | 요구사항리뷰 lane 진입 (자동) | lane 이 작업 *중* 외부사실 의존으로 막힘 |
| 주체 | RequirementsReviewPL → Claude/Codex dual-peer | 임의 lane(요청) + Orchestrator(문지기·실행) |
| 시점 | 설계 진입 *전* | 작업 *중* |
| carrier | S2(ADR-125) + S3 차등(ADR-124 Amendment 1) | S5(본 ADR-126) |

같은 deep-research skill body 를 trigger·주체·시점만 달리 진입한다 — 단계③ 의 "두 얼굴". 두 경로는 서로 다른 axis 를 cover 하며 중복·충돌하지 않는다.

### 결정 6 — 외부사실 의존 게이트 + 검사연극 금지 상속

on-demand 발동은 **무조건이 아니다** — ADR-124 §결정 2 외부사실 의존 게이트를 본 경로에 상속한다.

- **외부사실 의존 게이트** — 결론이 외부지식(산업 표준·RFC·벤더 동작·CVE 등)의 진위에 의존하는 곳에만 deep-research 적용. 내부 코드·내부 규칙·팀 암묵지식만으로 닫히는 결론(ADR-124 §결정 6 "의존 X" row)에 deep-research 를 강제하면 **검사연극**.
- **검사연극 금지 SSOT** = ADR-124 §결정 2 + ADR-119 §결정 6 "'조사했으므로 옳다' 단정 금지" (조사 = traceability + 정직성 수단이지 결론의 정당성 보증 아님). 본 ADR 은 두 SSOT 를 cross-ref 하며 문구를 복붙하지 않는다(drift 회피).
- **외부사실 의존 휴리스틱** (ADR-124 §결정 6 인용) — 의존 O(팩트체크/벤더/표준/CVE) / 의존 X(팀 암묵지식/내부 코드·규칙) / 경계(?)(시장정보·벤치마크·StackOverflow → ADR-125 §결정 6 운영 판정: 단계② 우선, 리뷰어 재량 escalation).
- **abstention escape** — 출처 확보 불가 시 ADR-119 §결정 3.2 "확인 불가 / 추정" 명시 후 진행 (데드락 회피, ADR-124 §결정 6 상속).
- **declarative-only** — on-demand 는 매 Story 강제 발동이 아니다. 실제 발동 = lane 작업중 외부사실 의존 막힘 시에만 (ADR-124 §결정 3 적합도 = 발동 *잠재력* / ADR-119 §결정 8 declarative-only 패턴 정합).

## cross-ref 표 (각 관계 명시)

본 ADR 은 기존 ADR 들을 합성한 거버넌스이며, 어느 기존 ADR 도 약화·재규정하지 않는다.

| 기존 ADR | 인용 지점 | 관계 |
|---|---|---|
| ADR-039 §결정 1·2 | 결정 2·3 | **정합 자체 재논증 (무변경)** — disjoint 차용 불가 명시 후 독립 논거 3개로 §결정 1 spawn 독점 + §결정 2 closed 4-entry whitelist 무손상 재논증. amendment 불요. |
| ADR-039 Amendment 4 | 결정 3 | **동형 선례** — skill body 가 operational primitive 보유하되 whitelist 5번째 entry 무신설. rate-limit → research-request 동형. |
| ADR-124 §결정 1 | 결정 1 | **carrier** — 단계③ 행 "리뷰 게이트(주) + on-demand(후순위)" 의 on-demand 행 실 mechanism. |
| ADR-124 §결정 4 | 결정 2(a) | **차용 불가 명시** — disjoint 논리(lane 개수 axis)는 새 mechanism 도입인 S5 에 차용 불가. (인용은 하되 논거로 쓰지 않음.) |
| ADR-124 §결정 5 | 본질 선언·컨텍스트 | **위임 carrier** — "on-demand 깊은 검증 경로 = S5" 명시 위임의 이행. |
| ADR-124 §결정 2·6 + Amendment 1 A1-3 | 결정 4·6 | **상속** — 외부사실 의존 게이트 + 검사연극 금지 + code lane web 금지[P0] 보존. |
| ADR-125 §결정 6 | 결정 5 | **disjoint SSOT** — on-demand ↔ review-time trigger·주체·시점 분리. §결정 4 ADR-052 cross-ref 처리 선례 = 본 ADR 형식 판정 모델. |
| ADR-109 (Amendment 4 경유) | 결정 3 | **binding precedent** — skill body = primitive, whitelist 무손상. |
| ADR-046 Amendment 2 | 컨텍스트 | **하류 pull 채널** — 하류 기술수요(review-time deep S3 + on-demand S5) 중 작업중 pull 채널이 본 ADR. |
| ADR-119 §결정 6 / §결정 3.2 | 결정 6 | **검사연극 금지 SSOT / abstention escape**. |
| ADR-058 §결정 5 | sunset_justification | **약화 차단** — additive skill + cross-ref only, strengthen 방향, null. |

## 회피된 대안

### 대안 A — ADR-039 Amendment 으로 처리 (5번째 inline whitelist entry 신설)

on-demand deep-research 호출을 ADR-039 §결정 2 inline whitelist 의 5번째 entry 로 추가.

**거부 이유**:
- Skill 호출은 §결정 1 "수정 작업" closed enum 비해당(mutation 미발화) → §결정 2 whitelist axis 와 disjoint(§결정 2 (b)②). 5번째 entry 신설은 whitelist axis 에 속하지 않는 행위를 axis 안으로 잘못 끌어들인다.
- ADR-039 Amendment 4 의 동형 선례(rate-limit skill body primitive ↔ whitelist 무손상, 5번째 entry REJECTED)를 그대로 답습 — Skill 호출 enum 확장은 §결정 2 L145 가 명시적으로 차단한 압박이다.

채택 = 결정 3 (whitelist 5번째 entry 무신설, skill body = primitive).

### 대안 B — ADR-124 Amendment 으로 처리 (신규 ADR 미신설)

on-demand 경로를 ADR-124 Amendment 2 로 처리 (S3 가 ADR-124 Amendment 1 으로 처리한 것과 동형).

**거부 이유**:
- S3(Amendment 1)는 §결정 3 적합도 표·§결정 2 게이트·§결정 6 휴리스틱을 lane 산출물에 **instantiate** 만 한 것(신규 규범 0)이라 Amendment 성격이 맞았다. 반면 S5 는 **새 mechanism(요청 → 게이트 → 주입)을 도입**하고 ADR-039 §결정 1/2 정합을 자체 재논증해야 하는 성격이라 Amendment 보다 신규 ADR 이 적합하다.
- ADR-125(S2)가 같은 Epic 에서 ADR-052 를 "의미 변경 0 → Amendment 격상 불요, cross-ref 만"(ADR-125 §결정 4)으로 처리하고 자신은 신규 ADR 로 신설한 선례를 직접 답습 — 새 경로·새 mechanism 신설은 신규 ADR.

채택 = 신규 ADR-126 (ADR-039/124 둘 다 cross-ref only, Amendment 불요).

## 근거

- **단계③ on-demand 경로 mechanism 단일화**: ADR-124 §결정 1 이 식별하고 §결정 5 가 S5 로 위임한 on-demand 행을 실 mechanism 으로 박제. 기존 거버넌스(ADR-039/124/125)를 합성할 뿐 새 권한을 신설하지 않는다.
- **ADR-039 정합 자체 재논증(P0)**: ADR-124 §결정 4 의 lane-개수-axis disjoint 논리를 차용하지 않고, 새 mechanism 의 성격에 맞춰 lane 자가-spawn 불가 + Skill 호출 mutation 미발화의 독립 논거로 §결정 1/2 무손상을 재논증.
- **검사연극 차단**: on-demand 게이트 자체가 검사연극 차단 장치(외부사실 의존 막힘에만 발동, 얕은조사로 될 일 반려). code lane web 금지[P0] 보존으로 대칭 붕괴 차단.
- **약화 0 (ratchet 강화)**: additive skill 신설 + cross-ref only. ADR-039 무변경, ADR-124/125 무약화. ADR-058 §결정 5 / ADR-064 §결정 7 정합.

## 결과

- 외부지식 충당 단계③ on-demand 경로의 normative anchor 신설 — Epic CFP-2324 의 마지막 child 로 단계③ 두 경로(review-time + on-demand) 모두 실 mechanism 화 완료.
- 운영 절차 SSOT = `skills/research-request-gate/SKILL.md`. 본 ADR = 정책 결정 SSOT (skill 은 cross-ref).
- ADR-039 §결정 1/2 = 0 변경 (자체 재논증으로 무손상 입증). amendment 불요.
- mechanical_enforcement_actions: [] — doc-only 거버넌스/skill 신설 (실행 코드 0). 발동 = declarative-only (외부사실 의존 게이트가 실 발동 결정). pattern_count ≥ 2 재발 시 follow-up CFP MUST promote (ADR-084 precedent).
- wrapper plugin.json bump = 불요 — 신규 skill 은 skills/ 자동 발견(plugin.json enumerate 0) + marketplace 4필드(name/version/description/author) 무영향 + CLAUDE.md 레인 진입 표 미등재(결정·대화 원칙 절 1줄 cross-ref 만) (ADR-037 정합).

## sunset_justification (ADR-058 §결정 5 — 약화 차단)

본 ADR 은 additive skill 신설 + 기존 ADR cross-ref only 이며 약화 0 건이다. ADR-039 의 두 invariant(§결정 1 spawn 독점 / §결정 2 closed 4-entry whitelist)는 무변경이고, ADR-124/125 의 어느 결정도 흡수·약화하지 않으며, 새 mechanism 은 기존 권한 경계의 합법적 조합이다. 따라서 strengthen 방향이며 sunset_justification 은 `null` (약화 evidence-gate 무관). is_transitional: false (permanent governance anchor). 원복은 별도 Story 의 명시 결정으로만 가능하며 그 경우에도 ADR-058 §결정 5 를 따른다.

## 해소 기준

N/A — permanent policy. Epic [#2324](https://github.com/mclayer/plugin-codeforge/issues/2324) (S1~S5) 가 본 ADR 으로 완결 (마지막 child).

## 관련 파일

- 본 ADR — on-demand 깊은 조사 보충 경로 + research-request-gate 거버넌스 SSOT
- `skills/research-request-gate/SKILL.md` — 본 ADR 정책의 운영 절차 carrier
- [ADR-124](ADR-124-external-knowledge-provisioning-model.md) — 외부지식 충당 3-단계 모델 (단계③ on-demand 위임 모법)
- [ADR-125](ADR-125-requirements-review-lane.md) — 요구사항리뷰 lane (review-time ↔ on-demand disjoint SSOT)
- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — spawn mechanism + inline whitelist (자체 재논증 대상)
- [ADR-119](ADR-119-research-before-claims.md) — 검사연극 금지 SSOT / abstention escape
- `skills/jira-decision-channel/SKILL.md` / `skills/rate-limit-429-mitigation/SKILL.md` — caller scope / skill body primitive 선례
