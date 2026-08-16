---
kind: concept_definition
type: domain-knowledge
slug: receipt-single-writer-under-partial-observability
title: 수령 사실의 single-writer — 부분 관측(differential observability) 하에서 비단조 단언(negative assertion)을 발신자가 발행할 수 없는 이유
status: Active
updated: 2026-08-16
carrier_story: CFP-2994
related_adrs:
  - ADR-170  # orchestrator↔subagent 기본규율 — 발신자 권한 경계의 성문 후보 carrier
  - ADR-073  # verify-before-assert — 관측 scope 초과 단언 금지의 상위 규범
  - ADR-119  # research-before-claims — 게이트 verdict = proxy 아닌 ground-truth
  - ADR-093  # 완료 보고 4-field schema — 수령 판정 3종(status/usage/본문)의 착지면
  - ADR-084  # 채번공간 disjointness — finding 증발 + 하류 계수 자기정합 실패형상 선례
related_concepts:
  - subagent-outcome-terminal-state-taxonomy   # outcome ⊥ termination_cause — "미수령" 의 종결상태 어휘를 이 taxonomy 가 이미 소유
  - vacuous-pass                                # 대상 0건 vacuous truth ↔ 항목 자체가 소실되어 항등식이 항진이 되는 형상
  - claim-to-evidence-audit                     # 자기보고 grounding — self-attestation 한계 축 공유
  - additive-merge-pattern                      # additive(단조) 우선 / destructive 선택은 명시 검토 후에만 — 같은 단조성 규율의 git layer 판본
tags:
  - partial-observability
  - differential-observability
  - single-writer
  - negative-assertion
  - monotonicity
  - calm-theorem
  - failure-detector
  - termination-detection
  - conservation-identity
  - fan-out
sources:
  - https://www.microsoft.com/en-us/research/wp-content/uploads/2017/06/paper-1.pdf   # Gray Failure (HotOS'17) — differential observability
  - https://cacm.acm.org/research/keeping-calm/                                        # CALM 정리 — 단조성 ⟺ coordination-free 일관성
  - https://arxiv.org/abs/1901.01930                                                   # Keeping CALM (arXiv)
  - https://lamport.azurewebsites.net/pubs/chandy.pdf                                  # Chandy-Lamport 분산 스냅샷 — 전역상태 = 지역상태 + 채널상태
  - https://www.cs.utexas.edu/~lorenzo/corsi/cs380d/papers/p225-chandra.pdf            # Chandra-Toueg — unreliable failure detector, completeness/accuracy
  - https://groups.csail.mit.edu/tds/papers/Halpern/JACM90.pdf                         # Halpern-Moses — common knowledge 도달 불가
  - https://en.wikipedia.org/wiki/Negation_as_failure                                  # negation as failure / closed-world assumption
  - https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD687.html                  # Dijkstra-Scholten — diffusing computation 종료 검출
  - https://en.wikipedia.org/wiki/Huang%27s_algorithm                                  # Huang weight-throwing — 가중치 보존 종료 검출
  - https://www.cs.utexas.edu/~rossbach/cs380p/papers/Counters.html                    # CRDT G-Counter — replica 별 슬롯 소유
  - https://www.rabbitmq.com/docs/confirms                                             # consumer ack ⊥ publisher confirm
  - https://www.rfc-editor.org/rfc/rfc9334.html                                        # RATS — Attester ≠ Verifier
  - https://www.accountingtools.com/articles/trial-balance-errors.html                 # 누락 오류는 시산표가 못 잡음
  - https://code.claude.com/docs/en/sub-agents                                         # Claude Code subagent — nesting / background 완료 통지
---

# 수령 사실의 single-writer (receipt single-writer under partial observability)

## 정의

**어떤 채널의 수령 사실(receipt)은 그 채널의 수신 주체만이 기록자이며, 그 채널을 관측할 수 없는 발신자는 수령 사실에 대한 부정 단언(negative assertion)을 발행할 수 없다.**

세 층으로 분해된다.

1. **부분 관측(partial observability)** — 다주체 시스템에서 각 주체는 자기 지역 상태만 직접 알고, 타 주체의 inbox 를 열거할 수단이 없다. 한 관측자의 침묵은 타 채널에 대해 **아무 정보도 갖지 않는다**.
2. **비단조 단언(negative assertion)** — "너는 X 를 받지 않았다" 는 부정문이며 **비단조(non-monotonic)** 다. 반면 "이 내용을 전달한다" 는 사실을 추가만 하므로 **단조(monotonic)** 다.
3. **기록자 단일화(single-writer)** — 비단조 단언은 그 사실의 소유자(수신자)만 발행할 수 있다. 발신자의 비단조 단언은 **월권(ambient authority)** 이며 무효다.

본 개념의 근본 명제 = **"내 채널의 침묵 ≠ 전역 부재"**. 이를 어기면 발신자의 선의의 중계가 수신자의 실재 내용을 삭제하는 **파괴적 지시**로 변질된다.

## 컨텍스트

### 발현 (CFP-2994 carrier — consumer repo `mclayer/mctrader` Story #2105 요구사항 lane)

`RequirementsPLAgent` 가 6 SubAgent 를 fan-out 했고 완료 통지가 두 갈래로 갈렸다 — 3건은 Orchestrator 채널로만, 4건(계 ~790k tok, 축당 ~200k 로 도달 3축보다 약 10배 중량)은 PL 채널로만 도달했다. Orchestrator 는 자기 채널 도달 3건에서 "손자 통지는 Orchestrator 로 라우팅된다" 는 전칭 규칙을 유도하고, 그 규칙 하에서 "내 채널 무도달 = 전역 무도달" 로 환원해 PL 에게 **"4축은 미수령으로 declare 하라"** 는 파괴적 지시를 발행했다. PL 이 순종했다면 6 관점 중 4 관점이 게이트 입력에서 증발하고 **하류 계수는 전부 자기정합**이었을 것이다(4축이 애초에 없었던 것처럼 보이므로 불일치가 남지 않는다). 실제 복구 = PL 의 자진 신고 1건. 기계적 검출 장치 0.

> 위 반사실("순종했다면 증발")은 **실증되지 않았다** — PL 이 실제로는 정정했다. 본 개념은 그 반사실을 확정으로 승격하지 않는다.

### 왜 개념 정립이 필요한가

이 형상은 이 lane·이 Story 한정이 아니다. **fan-out 을 하는 모든 orchestrator↔PL 쌍**이 (a) 구조적 관측 비대칭 (b) 평문으로 표현 가능한 파괴적 지시 (c) 하위 주체의 자발적 정직에만 의존하는 검출 — 세 조건을 공유한다. 그리고 이 셋은 전부 분산 시스템 문헌에 **이미 이름이 있는** 문제이므로, 신규 발명이 아니라 **채택**으로 처리해야 한다.

## 핵심 규칙

### RSW-1 — 관측 비대칭의 정식 명칭 = differential observability

Gray Failure(HotOS'17)는 "적어도 한 앱은 시스템이 unhealthy 하다고 관측하는데 관측자는 healthy 하다고 관측하는" 상태를 gray failure 로 정의하고, 그 핵심 특징을 **differential observability** 로 명명한다. 본 사건은 그 쌍대(dual)다 — 관측자(Orchestrator)는 "무도달"을, 당사자(PL)는 "전량 도달"을 관측했다. 같은 논문의 처방이 곧 본 개념의 처방이다: *"different components' perceptions of what constitutes failure"* 사이의 간극을 메우는 것. 즉 **채널 불일치 declare 의무는 이 문헌의 published remedy 이지 codeforge 의 발명이 아니다.**

### RSW-2 — 편측 표본 전칭 유도 = 개방 세계에 적용된 closed-world assumption

"내 inbox 에 없다 ⟹ 존재하지 않는다" 는 **negation as failure**(Clark 1978)이며, 지식베이스가 **완전(complete)** 하다는 **closed-world assumption** 아래서만 타당하다. Orchestrator 의 inbox 는 완전한 지식베이스가 아니다. ∴ 이 추론은 논리적으로 무효이며, 개념적으로 "실수" 가 아니라 **정의역 위반**이다.

### RSW-3 — 스냅샷의 법칙 승격 = 전역상태를 지역상태 1개로 구성하려는 시도

Chandy-Lamport(1985)에서 **전역 스냅샷 = 모든 프로세스의 지역상태 + 채널의 in-transit 메시지 상태**다. 채널 상태를 빼면 일관 절단(consistent cut)이 아니다. 본 사건에서 미도달 4축은 정확히 **in-transit 메시지**였고, Orchestrator 는 지역상태 1개 + 채널상태 0 으로 "전역 상태"를 구성했다. Chandy-Lamport 알고리즘이 존재하는 이유 자체가 **지역 관측 하나로 전역 상태를 유도할 수 없기 때문**이다.

### RSW-4 — "죽었다 vs 느리다" 구별 불가 = FLP + unreliable failure detector

비동기 시스템에서 정지한 프로세스와 매우 느린 프로세스는 **구별 불가능**하다(FLP 1985). Chandra-Toueg(JACM 1996)는 이를 우회하는 오라클로 failure detector 를 도입하고 두 속성으로 분해한다:

| 속성 | 내용 | 성질 |
|---|---|---|
| **completeness** | 실제로 죽은 프로세스는 결국 의심된다 (놓치지 않음) | liveness |
| **accuracy** | 살아있는 프로세스를 의심하지 않는다 (오판 안 함) | safety |

동기 가정 없이 perpetual accuracy 는 불가 → **eventually perfect(◇P)** 계열이 현실 해법이며, 그 핵심은 **의심이 취소 가능(revocable)** 하다는 것이다.

**∴ 본 개념이 요구하는 것**: "미수령" 판정은 **취소 가능해야 하며, 파괴적 후속 조치를 유발해서는 안 된다.** 내용을 삭제하는 의심은 취소 가능하지 않다.

### RSW-5 — additive ↔ assertion 구분의 근거 = CALM 정리

CALM(Consistency As Logical Monotonicity, Hellerstein·Alvaro): **어떤 문제가 일관되고 coordination-free 한 분산 구현을 갖는 것은 그것이 단조일 때 그리고 오직 그때뿐이다.** 단조 = 입력집합 S ⊆ T 이면 P(S) ⊆ P(T).

- `relay:additive`("이 내용을 전달한다") = 사실 추가 = **단조** → 조율(coordination) 없이 안전.
- `state:assertion`("너는 X 를 받지 않았다") = 부정 = **비단조** → CALM 에 의해 **조율을 요구**한다.

그 요구되는 조율이 정확히 "소유자에게 물어보기" = single-writer 다. ∴ 메시지 종별 구분은 임의 관례가 아니라 **단조/비단조 분할**이며, 판정 규칙은 다음 한 줄로 환원된다:

> **inter-agent 메시지가 무언가를 부정·철회·덮어쓰면 소유자의 동의가 필요하고, 추가만 하면 필요 없다.**

### RSW-6 — 발신자는 수신자 상태에 권한이 없다 (actor / object-capability)

actor model 에서 액터는 **자기 사적 상태만** 수정할 수 있고 타 액터에는 메시지로만 영향을 준다. object-capability 는 **ambient authority 부재**를 요구한다(Miller, *Robust Composition*; *Capability Myths Demolished*). "미수령으로 declare 하라" 는 수신자 사적 상태에 대한 ambient authority 행사다.

산업 구현이 이 경계를 일관되게 지킨다:

| 시스템 | 수령 사실의 기록자 | 근거 |
|---|---|---|
| CRDT G-Counter | replica i 는 슬롯 i 만 증가, merge = pointwise max | Shapiro et al. 2011 |
| Kafka | **consumer** 가 자기 offset 을 commit. group coordinator 가 소유권 상실 consumer 의 commit 을 **fence** | Kafka consumer offsets |
| AMQP / RabbitMQ | consumer ack 과 publisher confirm 은 **별개 기전** — *"consumer acknowledgements are not aware of publishers"* | RabbitMQ confirms |
| Erlang/OTP | 종료 신호는 링크된 **supervisor(부모)** 로 전달 | OTP processes |

### RSW-7 — 계수 항등식은 종료 검출(termination detection)의 특수형

fan-out 완결 판정 `스폰 수 == 수령 수 + 미수령 수` 는 **종료 검출** 문헌의 보존 불변식과 동형이다.

- **Dijkstra-Scholten (EWD687)** — diffusing computation 에 initiator 를 뿌리로 하는 신장 트리를 유지. 각 노드는 미결 메시지의 **deficit counter** 를 갖고, **자기 자식이 전부 signal 을 보낸 뒤에만 부모에게 signal** 한다. initiator 의 counter 가 0 이 될 때만 종료를 선언한다.
- **Huang weight-throwing (1989)** — controlling agent 가 가중치 1 로 시작, 위임 시 가중치를 분할, idle 이 된 프로세스는 자기 가중치 전량을 반환. **총 가중치가 항상 1 로 보존**되며 controller 의 가중치가 1 로 복귀할 때가 종료.

**중요 함의 — 평면 계수는 중첩에 대해 합성되지 않는다.** PL 수준의 2항 계수는 손자 세대에 대해 아무 말도 하지 않는다. 중첩 fan-out 이 존재하면 (a) Dijkstra-Scholten 규율(자식 전원 완결 전 부모에게 완결 signal 금지) 또는 (b) Huang 가중치 보존 중 하나가 필요하다.

### RSW-8 — 항등식이 항진이 되지 않으려면 항이 독립 출처여야 한다

복식부기 시산표(trial balance)는 **누락 오류(errors of omission)를 잡지 못한다** — 거래가 통째로 빠지면 차변·대변이 함께 빠져 여전히 균형이 맞는다. 보상 오류(compensating errors)도 같다.

이것이 본 사건의 실패 형상과 **정확히 동일**하다: 4축이 애초에 없었던 것처럼 처리되면 스폰 수도 함께 줄어 항등식은 여전히 성립한다(자기정합). ∴

> **항등식의 각 항은 서로 독립인 출처에서 와야 한다.** 특히 `스폰 수` 는 보고 시점 당사자의 기억이 아니라 **스폰 시점에 독립적으로 방출된 기록**에서 와야 한다. 회계의 대응 처방이 외부 명세서 대조(external reconciliation)이고, 원격 증명의 대응 처방이 **RATS(RFC 9334)의 Attester ≠ Verifier 분리** — 자기 증명(self-attestation)은 그 자체로 신뢰의 근거가 아니다.

### RSW-9 — "양측 합의" 를 목표로 삼지 말 것 (common knowledge 도달 불가)

Halpern-Moses 는 비동기·비신뢰 채널에서 **common knowledge 가 실질적으로 도달 불가능**함을 보였다(coordinated attack). ∴ "송수신 양측이 무엇이 도달했는지 합의한다" 를 설계 목표로 두면 **증명된 불가능**을 쫓게 된다. 실행 가능한 목표는 그것이 아니라:

1. 각 주체가 **자기 관점만** 공표하고(single-writer),
2. 불일치는 **은폐하지 않고 declare** 하며(differential observability 처방),
3. 정합은 **제3의 독립 관측자**가 항등식으로 검사한다(Attester ≠ Verifier).

## 경계

- **In scope**: 다주체 fan-out 에서 수령 사실의 기록 권한, 부정 단언의 유효성 조건, 관측 비대칭의 명명·처방, 완결 판정 항등식의 구성 요건(독립 출처 · 중첩 합성 · 상태 열거 완전성).
- **Out of scope**:
  - **구체 라우팅 기전** — 어떤 통지가 어느 주체에게 가는지를 가르는 harness 내부 기전. 본 개념은 **라우팅 기전과 무관하게** 성립하도록 설계됐다(관측 비대칭을 전제로 한 방어). 기전 규명은 disjoint 축.
  - **종결상태 어휘** — "미수령"·"중단"·"무산출" 의 enum 분류는 `subagent-outcome-terminal-state-taxonomy`(outcome ⊥ termination_cause) 소유. 본 개념은 그 어휘를 **재사용**하며 신규 vocabulary 를 만들지 않는다.
  - **타임아웃 상수 값** — 대기 시간의 구체 수치는 운영 튜닝 영역. 본 개념은 "판정이 취소 가능하고 비파괴적일 것"만 요구한다(RSW-4).
- **Anti-pattern**:
  - 발신자가 수신자 채널에 대해 `state:assertion` 발행(RSW-6 월권).
  - 편측 표본에서 라우팅 전칭 규칙 유도(RSW-2 정의역 위반).
  - 시점 관측을 구조적 법칙으로 승격(RSW-3).
  - "미수령" 판정이 삭제·공란화 등 **파괴적** 후속을 유발(RSW-4 비가역 의심).
  - 항등식의 두 항을 **같은 주체의 같은 시점 기억**에서 도출(RSW-8 누락 오류 맹점 = 항진).
  - 평면 2항 계수를 중첩 fan-out 에 그대로 적용(RSW-7 비합성).
  - 검출을 하위 주체의 자발적 정직에 위임(RSW-8 self-attestation).

## 관련 ADR

> 본 파일 작성 시점에 ResearcherAgent 는 외부 개념 축 전담으로 아래 ADR **원문을 읽지 않았다**. 아래 매핑은 CFP-2994 입력 패킷이 제공한 좌표 기반 **후보**이며, 확정 매핑은 요구사항리뷰·설계 lane 소관이다.

- **ADR-170** — orchestrator↔subagent 기본규율. RSW-5(단조/비단조 분할) · RSW-6(권한 경계)의 성문 carrier 후보.
- **ADR-073** — verify-before-assert. RSW-2(관측 scope 초과 단언 금지)의 상위 규범.
- **ADR-119** — research-before-claims. "게이트 verdict = proxy 아닌 outcome ground-truth" 가 RSW-8(자기보고 ≠ 근거)과 동근.
- **ADR-093** — 완료 보고 4-field schema. 수령 판정 3종(완료 통지 status / usage 메트릭 / 본문 실재)이 착지하는 면.
- **ADR-084** — 채번공간 disjointness. "finding 이 통째로 증발하고 하류 계수는 항상 자기정합" 실패형상의 사내 선례 = RSW-8 의 실증.

## 변경 이력

- 2026-08-16 KST — 초기 작성 (CFP-2994 요구사항 lane, ResearcherAgent Mandate 1·2 산출물). differential observability(Gray Failure HotOS'17) · negation as failure/CWA(Clark 1978) · Chandy-Lamport 전역 스냅샷 · FLP + Chandra-Toueg completeness/accuracy · CALM 정리 · actor/object-capability 권한 경계 · CRDT G-Counter / Kafka offset / AMQP ack / Erlang OTP 산업 선례 · Dijkstra-Scholten + Huang 종료 검출 · 시산표 누락 오류 + RATS(RFC 9334) 독립 검증 · Halpern-Moses common knowledge 불가 를 cited 로 정립. 사내 선행 개념 `subagent-outcome-terminal-state-taxonomy` 어휘 재사용 명시(신규 vocabulary 금지).
