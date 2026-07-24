---
kind: concept_definition
type: domain-knowledge
slug: render-line-display-sublayer
title: Render line display sub-layer — 비영속 화면 표시 sub-layer의 값 획득 규율 (시각·주체) + model-authored primary / hook fail-open backup + 렌더 도달 honest ceiling
status: Active
updated: 2026-07-24
carrier_story: CFP-2818
related_adrs:
  - ADR-143  # carrier — Agent 수행 액션 렌더 줄 프리픽스 규약 SSOT (Amendment 3 = 값 정확성 저작 규율). 본 concept = 그 sub-layer 개념의 domain-knowledge mirror
  - ADR-119  # research-before-claims — 미래 시각·허구 주체 = fabrication 동류. 값 획득 규율의 규범적 뿌리 (강화 방향 원용)
  - ADR-079  # KST 표기 mandate — render line = 제3 ephemeral-UI sub-layer EXEMPT. 표기(notation) 축과 disjoint co-exist
related_concepts:
  - kst-display-invariant   # 값 무변환·표기(notation) 단계 SSOT — 본 concept(값 획득·상류 단계)와 disjoint upstream/downstream 경계
tags:
  - render-line-display-sublayer
  - ephemeral-ui
  - zero-persist
  - model-authored-primary
  - hook-fail-open-backup
  - trusted-time-anchor
  - registered-principal-identity
  - honest-ceiling
sources:
  - https://datatracker.ietf.org/doc/html/rfc5424   # §6.2.3 TIMESTAMP NILVALUE MUST / §6.2.5 APP-NAME NILVALUE — 값 획득 불가 시 생략(NILVALUE) 표준 선례
  - https://opentelemetry.io/docs/specs/otel/logs/data-model/   # ObservedTimestamp — origin clock 불명 시 관측자 실측 앵커로 대체
  - https://opentelemetry.io/docs/concepts/resources/   # service.name / unknown_service — 주체 미제공 시 명시적 unknown fallback
  - https://github.com/anthropics/claude-code/issues/34530   # harness system context = 날짜만 주입(시각 HH:MM 미주입, Closed as not planned)
---

## 정의

**Render line display sub-layer** = harness UI 가 Agent 스폰·도구호출·Orchestrator 상태 줄을 렌더하는 **비영속(ephemeral) 화면 표시 sub-layer**. 프리픽스 `[<주체명>] MM/DD HH:MM - <내용>` 가 표시되는 계층이며, 두 가지 근본 성질로 정의된다:

1. **zero-persist** — 이 sub-layer 에 표시되는 값은 어떤 커밋 산출물·계약 필드·영속 artifact 로도 흘러가지 않는다. 화면에 한 번 렌더되고 사라지는 표시 전용 계층이다 (이 경계를 넘어 persist 경로로 새면 관할 위반).
2. **표시된 값의 정확성 = 두 상류(값 획득) 규율의 하류 결과** — 화면에 도달하는 프리픽스는 (a) 시각 (b) 주체명 두 값을 담으며, 그 정확성은 표시 계층이 아니라 **값이 획득되는 상류 단계**에서 결정된다.

본 개념의 신규 정의 표면은 **정확히 2영역**으로 한정한다 (그 외는 기존 named 조각 cross-ref, 재정의 0): **값 획득 — 시각**(trusted-time-anchor) / **값 획득 — 주체**(registered-principal-identity). 표기(notation) 형식 자체는 [kst-display-invariant](kst-display-invariant.md) 소관이며 본 개념은 그 **상류(값이 어디서 오는가)** 만 다룬다.

## 컨텍스트

프리픽스 규약(ADR-143 §결정 2 포맷)은 3세대에 걸쳐 "프리픽스가 화면에 **뜨느냐**"(존재·도달)를 확립했다. 그 위에 남은 4세대 축이 "프리픽스가 도달시키는 **값이 정확한가**"이며, 본 개념이 그 값 정확성의 도메인 SSOT다.

- **Amendment 2 이후 계층 배치**: 화면 렌더에 실제 도달하는 유일 통로 = **model-authored primary**(모델이 `description`·prose 에 직접 저작). PreToolUse hook 의 기계 주입(`updatedInput`)은 도구 **실행 입력 계층**만 치환하고 화면 렌더 줄에는 미도달 → **hook = fail-open backup** 으로 강등.
- **결함의 뿌리**: 값 정확성(시각·주체)을 결정론적으로 보증하던 채널(hook per-dispatch 실측 stamp)이 화면 통로에서 backup 으로 내려가며, 화면 도달 채널(model-authored)에는 정확성 보증이 빠졌다. 그 공백에서 두 증상이 나온다 — (i) 시각은 실측 앵커 없이 지어내지거나(harness 는 날짜만 주입 — 모델은 읽을 시계가 없음) 이미-KST 로컬 시각에 +9 를 재가산해 미래가 되고, (ii) 주체명은 모델이 자기 정체를 알 구조적 경로가 없어 틀린다.
- 헬퍼(`kst-render-stamp` 계열)·hook 2종의 산출값은 정확하다. 결함은 코드가 아니라 **model-authored 저작 규율의 공백**에 있다 — 코드 수정이 아니라 값 획득 규율의 명문화가 처방이다.

## 핵심 규칙

### R-1: 값 정확성은 상류(값 획득)에서 결정, 표시 계층은 그 하류

표시 sub-layer 는 값을 **만들지 않고 렌더만** 한다. 시각·주체 두 값의 진위는 아래 §값 획득 두 절이 규율하며, 표시 계층은 그 결과를 그대로 렌더한다. 따라서 "미래 시각·허구 주체" 결함은 표시 계층 버그가 아니라 **상류 값 획득 규율 위반**으로 진단해야 한다.

### R-2: model-authored primary / hook fail-open backup (2계층 상보)

- **primary** = model-authored 저작. 화면 렌더에 도달하는 유일 통로이므로, 값 정확성의 1차 책임은 저작 시점 모델에 있다 (attempt-obligation).
- **backup** = hook 기계 주입. 발화 시점 헬퍼를 실행해 정확한 시각·주체를 산출하나 **실행 입력 계층 한정**(화면 미도달) — fail-open(주입 실패 시 원본 유지, never wrong-value). backup 은 실행-계층 정확성 목적으로 유효 잔존하되, 화면 개선 효과는 0이다.

### R-3: 렌더 도달 honest ceiling (P0 불가침)

표시 sub-layer 의 화면 도달은 **기계 게이트로 강제할 수 없다** — 렌더 줄은 ephemeral 이고, 화면 표시를 변환·검증할 upstream render-transform hook 이 부재하기 때문이다. 따라서:

- 값 정확성 규율은 **advisory ceiling**(저작 규율 + self-check backstop)로 결함을 **감소**시킬 뿐 **제거하지 못한다**.
- **"100% 기계강제"·"hard-gate 로 못박음" 류 서술은 하지 않는다** — 그런 hard-claim 은 검사연극(ADR-119 §결정 6)이자 위양성. 본 개념은 "구조적 값 획득 규율 + 저작 저감 + 잔여 정직 공개"로만 재약속한다.
- 실행-계층(hook backup)의 정확성과 화면-계층(model 저작)의 정확성은 **disjoint 축** — 실행 계층이 정확해도 화면은 model 원본을 렌더한다. 두 계층을 혼동한 "화면 개선" 주장 금지.

## 값 획득 — 시각

표시 시각의 **유일 신뢰 원천 = 실측 앵커**다 (trusted-time-anchor). 모델은 wall-clock 접근이 없고 harness 는 날짜만 주입(HH:MM 미주입)하므로, 실측 앵커 없이 시각을 저작하면 구조적 fabrication 이다. [source: anthropics/claude-code#34530]

- **실측 앵커 1회 + verbatim floor**: 세션(또는 활성화 turn)당 시각 헬퍼를 1회 실행해 KST 앵커를 얻고, 프리픽스에는 그 **앵커 값을 verbatim** 으로 쓴다. 경과분 **상향 가산·반올림 금지**. 앵커는 저작 이전에 측정되므로 구조적으로 `앵커 ≤ now` — verbatim 사용 시 미래 overshoot 가 정의상 불가능해진다(floor). 미래 시각 = 정의상 오류(표시 시각 > 실측 now 불가).
- **시각원 계층 분기 (+9 재가산 차단)**: 시각 값은 **헬퍼(또는 SubagentStart·spawn packet 으로 주입된 실측치) 앵커에서만** 유도한다. 로컬 clock read·암산 offset 가산 일절 금지. "UTC+9 고정 산술"은 헬퍼 내부(절대 UTC read 존재)의 정당화일 뿐이며, 모델이 이미-KST 인 로컬 시각에 이를 재적용하면 정확히 +9h 미래가 된다. tz 변환은 헬퍼 단일 경로에 격리한다.
- **재실측 trigger (control-yield 4종)**: 앵커는 stale 될 수 있다. 제어를 (재)획득한 매 활성화 turn 시작 시, timestamp 프리픽스 최초 저작 전 헬퍼를 1회 재실행한다 — (T1) park/child-대기 복귀 (T2) 세션 resume·cold-resume (T3) 공백 후 lane·컨텍스트 전환 (T4) 임의 suspension 복귀. **수치 상한 게이트는 두지 않는다** — 모델은 앵커 후 경과를 실측할 시계가 없어 "X분 초과" 판정이 model-uncheckable(검사연극)이기 때문. 약 10분 soft 경계는 비규범 참고치일 뿐이다.
- **부재 시 생략 (생략 > fabrication)**: 실측 앵커를 확보하지 못하면 시각 요소를 **생략**한다 — `[<주체명>] MM/DD - <내용>`(날짜는 harness date-only 주입으로 가용) 또는 시각 전체 생략. 허구 값 기입 금지. 이는 canonical 포맷의 대체가 아니라 앵커-부재 한정 additive 변형이다. 오정보보다 정보 부재가 우월하다. [source: RFC 5424 §6.2.3 — 시각 획득 불가 시 NILVALUE **MUST**; OTel ObservedTimestamp — origin 시각 불명 시 관측자 실측 앵커로 대체]

## 값 획득 — 주체

표시 주체명의 **유일 신뢰 값 공간 = 등록 roster principal 실명**이다 (registered-principal-identity). 모델은 자기 정체를 알 구조적 경로가 없으면 주체명을 틀리므로, 주체명은 저작 시점 창작이 아니라 전달받은 실명의 사본이어야 한다.

- **roster 실명 verbatim**: 주체명은 `spawn-event-v1` `agent_type`(roster-derived) 실명만 사용한다. 스폰 헤더 = 피스폰 에이전트의 `subagent_type` verbatim / leaf 도구호출 = self 의 `agent_type`. 자가 작명·역할 서술어·타 에이전트명·dispatcher(Orchestrator)명 오부착 금지.
- **explicit unknown fallback**: roster 에 없거나 self명을 알 수 없으면 **허구 identity 를 발명하지 않고** 명시적 `unknown-agent` 로 표기한다. 알 수 없음을 알 수 없음으로 표시하는 것이 그럴듯한 거짓 이름보다 우월하다. [source: OTel Resources — service.name 미제공 시 `unknown_service` 강제; RFC 5424 §6.2.5 — APP-NAME 불명 시 NILVALUE]
- **spawner-asserted 정직 선언**: spawn packet 으로 주입된 self명은 spawner 가 주장한 값(spawner-asserted)이지 subagent 가 자체 검증한 값이 아니다(subagent-unverified). 조립 계층은 self명을 모델 컨텍스트에 기계 주입하지 않으므로, 주입 self명의 진위는 "검증됨"으로 참칭하지 않고 정직하게 spawner-asserted 로 둔다. 값은 Agent 호출 `subagent_type` 의 verbatim 사본으로 규율한다.

## 경계

### 값 획득(상류) ↔ 값 무변환·표기(하류) — [kst-display-invariant](kst-display-invariant.md) 와 disjoint

두 개념은 **같은 프리픽스 값의 서로 다른 단계**를 규율하며 disjoint upstream/downstream 축이다:

| 단계 | 개념 | 규율 대상 |
|---|---|---|
| 상류 — 값 획득 | **render-line-display-sublayer** (본 개념) | 시각이 어느 시계에서/주체가 어느 roster 에서 오는가 (진위·출처) |
| 하류 — 표기(notation) | **kst-display-invariant** | 획득된 값을 어떻게 적는가 — 값 무변환, 표기 형식만 강제 |

- **경계의 실증(+9 재가산)**: 모델이 로컬 시각을 읽어 +9 를 재적용하는 결함은 두 개념의 교차점이다. 이는 (a) 값 획득 규율 위반(헬퍼 앵커가 아닌 로컬 clock read)이면서 (b) kst-display-invariant 가 금지하는 값 변환(표기 단계에서 값을 바꿈)을 흉내낸다. 두 개념 모두 처방은 같은 방향 — 표기 계층은 값을 변환하지 않고(하류), 값은 헬퍼 단일 경로 실측에서만 온다(상류).
- **표기 EXEMPT 재확인**: render line 의 compact `MM/DD HH:MM` 형식은 ADR-079 §결정 6 로 제3 ephemeral-UI sub-layer EXEMPT — 본 개념은 형식이 아닌 **값의 정확성(출처)** 만 다루며, ADR-079 표기 mandate 와 disjoint co-exist 한다.

### disjoint 축 (재유입 봉인)

- **⊥ 표기 형식(ADR-079 / kst-display-invariant)**: notation 규칙은 별 SSOT. 본 개념 = 값 획득 상류만.
- **⊥ render 도달 기계 게이트**: 화면 도달 강제 불가(honest ceiling, R-3). 값 획득 규율은 advisory ceiling — normative 기계강제 격상 금지.
- **⊥ hook 실행-입력 계층**: hook backup 의 값 정확성은 실행 계층 한정(화면 미도달). 본 개념의 화면 값 정확성과 disjoint(R-2).
- **⊥ TodoWrite / prose 상태보고 / description-less 도구**: 표시 sub-layer 프리픽스 밖 표면 — 본 개념 무관(구조적 제외).

## 관련 ADR

- **ADR-143** (carrier) — Agent 수행 액션 렌더 줄 프리픽스 규약 SSOT. §결정 2 포맷 · §결정 1 INV-1(subject) · Amendment 2 model-authored primary / hook fail-open backup · Amendment 3 값 정확성 저작 규율(시각 floor·생략형·주체 실명). 본 concept = 그 sub-layer 개념의 domain-knowledge mirror이며, ADR-143 frontmatter `related_concepts` 의 참조를 해소한다.
- **ADR-119** — research-before-claims / anti-fabrication. 미래 시각·허구 주체 = fabrication 동류 → 값 획득 규율의 규범적 뿌리(강화 방향으로만 원용). honest ceiling(R-3)의 검사연극 차단 근거(§결정 6).
- **ADR-079** — KST 표기 mandate. render line = 제3 ephemeral-UI sub-layer EXEMPT. 표기(하류) 축과 값 획득(상류) 축의 disjoint co-existence.

**참조 파일**:
- [ADR-143: Agent 수행 액션 렌더 줄 프리픽스 규약](../../../archive/adr/ADR-143-agent-action-render-line-prefix.md) — carrier SSOT (§결정 2 포맷 · Amendment 2 model-authored primary/hook fail-open backup · Amendment 3 값 정확성 저작 규율)
- [kst-display-invariant](kst-display-invariant.md) — 표기(하류) 단계 concept — 값 무변환·표기 형식 SSOT

## 변경 이력

| 일자(KST) | Story | 변경 |
|---|---|---|
| 2026-07-24 | CFP-2818 | 신규 — 비영속 화면 표시 sub-layer 개념 SSOT. zero-persist + model-authored primary / hook fail-open backup + 렌더 도달 honest ceiling(기계강제 불가·advisory ceiling) 정의. 값 획득 2절(시각 = 실측 앵커 verbatim floor·control-yield 재실측·부재 시 생략 / 주체 = roster 실명·explicit unknown·spawner-asserted 정직 선언) 흡수. kst-display-invariant(표기·하류)와 disjoint upstream 경계 명시. ADR-143 dangling related_concepts 참조 해소. |
