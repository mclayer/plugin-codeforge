---
kind: concept_definition
type: domain-knowledge
slug: agent-resumption-vs-respawn
title: Agent resumption vs re-spawn (세션 내 재개 ↔ 재생성 — warm-continuation 의 이득·부채 비대칭)
status: Active
updated: 2026-08-12
carrier_story: CFP-2946
related_adrs:
  - ADR-141  # tier cap-down / failover — fresh-spawn-only shape 의 근거 (Amd 6 A6-2 / Amd 7 A7-2)
  - ADR-170  # Story-scope 위임 재정의 — depth 0→1→2 실작동 (재귀 spawn = 정책축이지 플랫폼축 아님)
  - ADR-119  # research-before-claims — 재개 성공 판정 = outcome ground-truth (Amd 2 ④)
  - ADR-044  # phase-scoped sequential team — lane-PL lifecycle / dispatch 축
  - ADR-043  # spawn-event-v1 — 재개 회차 관측 substrate
  - ADR-163  # measurement — dev-process-event / stop-event 축분리 선례
related_concepts:
  - context-offloading-to-ephemeral-workers    # 단수명 소멸이 이득이던 축 ↔ 본 concept 은 그 소멸을 되돌리는 축 (정확히 반대 방향 trade)
  - subagent-outcome-terminal-state-taxonomy   # 재개 적격 판정의 입력 = 직전 회차 outcome / termination_cause
  - vacuous-pass                               # SendMessage success:true 만 믿는 재개 판정 = false-green 계열
tags:
  - codeforge
  - agent-lifecycle
  - warm-start
  - context-continuity
  - dispatch-channel
  - cost-asymmetry
sources:
  - https://code.claude.com/docs/en/sub-agents
  - https://code.claude.com/docs/en/cross-session-messaging
  - https://docs.langchain.com/oss/python/langgraph/persistence
  - https://openai.github.io/openai-agents-python/sessions/
  - https://microsoft.github.io/autogen/stable//user-guide/agentchat-user-guide/tutorial/state.html
  - https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html
---

## 정의

이미 종료한 subagent 를 **자기 transcript 째 되살려 다음 회차를 잇는 것**(resumption / warm continuation)과, 같은 역할의 새 인스턴스를 **빈 컨텍스트로 다시 만드는 것**(re-spawn / cold start)을 구별하는 개념. 두 경로는 "같은 일을 하는 두 방법"이 아니라 **서로 다른 비용·리스크 프로파일을 가진 별개 dispatch 기제**다.

- **re-spawn (cold)**: 컨텍스트 0 에서 시작 → 호출자가 task packet 을 매번 재구축해야 하고, 인스턴스 기동 고정비(codeforge 에서는 per-agent hook 직렬 지연세)를 매번 지불한다. 대신 **직전 회차의 판단이 전혀 남지 않는다**.
- **resumption (warm)**: 이전 회차의 전체 대화·도구호출·추론이 보존된 채 이어짐 → packet 재구축·기동 고정비를 회피한다. 대신 **직전 회차의 판단이 전부 남는다**.

핵심 명제 = **"보존되는 것과 오염되는 것은 같은 것이다"**. 재개가 아끼는 자산(직전 문맥)과 재개가 짊어지는 부채(직전 문맥에 대한 고착)는 물리적으로 동일한 토큰이다. 따라서 재개는 순이득 최적화가 아니라 **축이 다른 교환**이며, "언제 재개하고 언제 버리는가"의 적격 판정 없이는 도입 자체가 의미를 갖지 못한다.

## 컨텍스트

외부 컴퓨팅에서 이 대립은 반복 등장하는 well-established 패턴이다. 본 concept 은 그 대응 개념군을 codeforge 문제(FIX 루프 회차 간 리뷰어 재사용)에 매핑한다.

| 외부 개념 | 대응 관계 | codeforge 매핑 |
|---|---|---|
| **warm start vs cold start** (serverless) | 인스턴스 기동 고정비 회피 ↔ 잔존 상태 오염 | hook 직렬 지연세 회피 ↔ 직전 회차 판단 잔존 |
| **connection pooling** | 재사용 전 상태 리셋(reset) 의무 | 재개 메시지가 무엇을 리셋 선언해야 하는가 |
| **session affinity / sticky session** | 같은 대상에 계속 붙임 → 캐시 적중 ↔ 부하 편중·장애 전파 | 같은 리뷰어 고정 → 문맥 적중 ↔ 오판 고착 |
| **checkpoint / restore (CRIU)** | 스냅샷 복원 = 상태 재구성 비용 0 ↔ 스냅샷이 낡으면 복원이 곧 stale 주입 | transcript 복원 ↔ HEAD 이동 후 stale 판독 |
| **actor model mailbox** | 액터는 살아있고 메시지가 상태를 전이 | `SendMessage(to: name)` = 메일박스 투입 |
| **cache invalidation** | 유효기간·무효화 규칙이 캐시 자체보다 어렵다 | 재개 적격 조건 = 무효화 규칙 |

프레임워크 선행사례도 같은 축으로 갈린다 — LangGraph 는 thread_id + checkpointer 로 노드 단위 스냅샷을 남겨 재개하고, OpenAI Agents SDK 는 Session 이 이전 항목을 다음 턴 앞에 prepend 하며, AutoGen 은 `save_state`/`load_state` 로 상태를 직렬화하되 **재사용 전 `on_reset()` 리셋을 별도 의무로 둔다**. 세 프레임워크 모두 "상태를 이어붙이는 기제"와 "이어붙인 상태를 언제 버리는가"를 **분리된 API 로 노출**한다는 공통점이 있다 — 재개 채널만 만들고 리셋/적격 축을 만들지 않는 설계는 선행사례에서 벗어난다.

## 핵심 규칙

- **R1 — 재개는 최적화이지 정확성 기제가 아니다**: 재개 실패는 fresh re-spawn 으로 fallback 해야 하며(fail-open), 재개 성공을 전제로만 성립하는 산출은 만들지 않는다. 재개가 불가능해져도 lane 은 정상 진행 가능해야 한다.
- **R2 — 재개 성공 판정 = outcome ground-truth (전달 성공 아님)**: 메시지 전송 API 의 성공 반환값은 **수신·재개·작업재개의 증거가 아니다**. 실제 재개 여부는 재개된 agent 의 산출로만 판정한다. 전송 성공을 재개 성공으로 읽는 것은 false-green(ADR-119 Amd 2 ④ / `vacuous-pass` 계열).
- **R3 — 보존 = 오염 (동일 토큰 양면성)**: 재개가 아끼는 문맥과 재개가 고착시키는 판단은 같은 토큰이다. 따라서 이득(비용)만 계상하고 부채(검출력)를 계상하지 않은 재개 도입 판단은 반쪽이다.
- **R4 — 적격 판정은 무효화 규칙이다 (cache invalidation 동형)**: "언제 재개 가능한가"는 부수 조건이 아니라 본체다. 최소 3 축 — ① 실행 파라미터 동일성(모델 tier 등 인스턴스 정체성) ② 직전 회차 종결 건전성(`subagent-outcome-terminal-state-taxonomy` 의 outcome / termination_cause) ③ 보존된 판단이 여전히 유효한가(원인이 "판독면 stale" 이면 보존 문맥 자체가 오염원).
- **R5 — 재개 메시지는 delta 를 명시해야 한다 (restore ≠ refresh)**: 복원된 transcript 는 정의상 **과거 시점의 세계**다. 재개 메시지는 그 사이 무엇이 변했는지(코드 HEAD·재판독 의무 대상·시각 앵커)를 명시적으로 주입해야 하며, 그렇지 않으면 재개는 stale 판독을 *구조적으로* 재생산한다.
- **R6 — 재개 chain 은 무한하지 않다 (fidelity decay)**: 재개를 거듭하면 누적 transcript 가 자라고, 자동 압축(auto-compaction)·중간 소실(lost-in-the-middle) 계열 열화가 개입한다. "full context preserved" 는 **압축 경계 이전까지만 참**이다. 압축 경계가 기계 관측 가능하면 그것을 재개 적격의 하드 축으로 쓸 수 있다.
- **R7 — 재개는 ownership 을 옮기지 않는다**: 재개는 dispatch 기제(누가 언제 호출되나)이지 authorship 기제(누가 무엇을 write 하나)가 아니다. 재개 도입이 write 경계·원장 append 독점을 변경한다면 그것은 별개 결정이다.
- **R8 — 이름은 주소이지 정체성이 아니다**: 이름 기반 주소는 재사용될 수 있다. 이름 충돌 시의 동작(거절 / 오배달 / 최신 우선)이 무엇인지에 따라 naming 규약의 **목적**이 달라진다 — 오배달을 막는 것이 목적인지, 단지 주소 유일성 확보가 목적인지 구별해야 한다.

## 경계

- **In scope**: 세션 내에서 종료한 worker 를 되살려 다음 회차를 잇는 dispatch 기제의 개념·이득·부채·적격 판정 축. 외부 대응 개념 매핑.
- **Out of scope**:
  - **리뷰 품질 축의 정량 trade-off** — 동일 리뷰어 반복이 검출력에 미치는 영향은 disjoint concept(`repeat-reviewer-anchoring-vs-fresh-eyes`)이 소유. 본 concept 은 그 부채가 *존재한다*는 구조만 서술한다.
  - **write 경계 / 원장 ownership** — R7 대로 disjoint 축.
  - **재귀 spawn 허용 여부(depth)** — 누가 spawn 할 수 있나는 위임 정책 축(ADR-170)이며 재개 축과 독립.
  - **cross-session(세션 경계 밖) 재개** — 세션 간 메시징은 별개 기능면이며 전달 의미론·가용성 조건이 다르다. 본 concept 은 세션 내 축만 정의한다.
  - **특정 harness 버전의 API 동작** — 버전 의존 사실은 concept 이 아니라 Story 의 `[verified]` 실측 대상. 본 concept 에 버전 수치를 박제하지 않는다.
- **Anti-pattern**:
  - 전송 API 의 `success:true` 를 재개 성공으로 채택(R2 위반 — false-green).
  - 적격 조건 없이 "항상 재개"(R4 위반 — 오염 고착).
  - 재개를 의무 경로로 승격해 fallback 을 제거(R1 위반 — 최적화의 정확성 기제 참칭).
  - 재개 메시지에 delta 없이 "이어서 해줘"만 전달(R5 위반 — stale 판독 구조적 재생산).
  - 무한 재개 chain(R6 위반 — summary-of-summary 열화).
  - 비용 절감치만 계상하고 검출력 부채를 미계상한 도입 판정(R3 위반).

## 관련 ADR

- **ADR-141** Amendment 6 / 7 — fresh-spawn-only shape(모델 tier 재해석 함정 차단)의 SSOT. 재개 채널이 tier 경계를 건드리는 순간 본 ADR 의 집행면과 교차한다.
- **ADR-170** §결정 19 — Story-scope 위임 재정의. "재귀 spawn 금지"가 정책축이지 플랫폼축이 아님을 확정한 선례로, 본 concept 의 "플랫폼 제약 ↔ 자체 정책" 구분 규율과 동형.
- **ADR-119** research-before-claims — R2(재개 성공 = outcome ground-truth)의 근거. Amendment 2 ④ 가 "internal proxy 아닌 outcome 으로만 PASS 단정"을 이미 codify.
- **ADR-044** phase-scoped sequential team — lane-PL lifecycle / dispatch 축의 기존 소유자.
- **ADR-043** spawn-event-v1 — 재개 회차 vs fresh 회차 대조를 위한 관측 substrate.
- **ADR-163** measurement — 관측 채널 축분리 선례(always-on 채널과 opt-in 채널의 판별력 차이).
- **CFP-2946**(carrier_story) — 본 concept 의 first codified case(FIX 루프 리뷰어 재개 채널).

## 변경 이력

- 2026-08-12 KST — 초기 작성(CFP-2946 요구사항 lane, ResearcherAgent). 외부 대응 개념군(warm/cold start · connection pooling · session affinity · checkpoint-restore · actor mailbox · cache invalidation) + 프레임워크 선행사례(LangGraph / OpenAI Agents SDK / AutoGen) 매핑. R1-R8 codify.
