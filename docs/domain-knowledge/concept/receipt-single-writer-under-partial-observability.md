---
kind: concept_definition
type: domain-knowledge
slug: receipt-single-writer-under-partial-observability
title: 수령 사실의 single-writer — 부분 관측(differential observability) 하에서 비단조 단언(negative assertion)을 발신자가 발행할 수 없는 이유
status: Active
updated: 2026-08-18
carrier_story: CFP-2994
# ★ 정정 전파 대상 (CFP-2994 M3 인벤토리 1급 항목) — 본 파일은 carrier Story 의 유일한 영구·cross-Story
#   artifact 다. Story 가 판정을 정정할 때마다 본 파일 전수 스윕이 의무이며, 미전파는 P0 로 취급한다.
#   근거 = CFP-2994 요구사항리뷰 Iter 3 P0 (Iter 1·2 재설계가 본 파일에 0% 전파된 채 main 착지 직전이었음).
correction_sweep_required: true
related_adrs:
  - ADR-170  # orchestrator↔subagent 기본규율 — Amendment 2 A2-4 가 receipt_state 도달-전용 경계의 확정 carrier (CFP-2994 설계 lane)
  - ADR-139  # background-wait liveness gate — Amendment 3 A3-4 (ii) 가 ADR-170 A2-4 와 paired 확정 carrier. INV-L4 가 verdict 권한을 lead 에 고정
  - ADR-073  # verify-before-assert — 관측 scope 초과 단언 금지의 상위 규범
  - ADR-119  # research-before-claims — 게이트 verdict = proxy 아닌 ground-truth
  - ADR-093  # 완료 보고 4-field schema — 수령 판정 3종(status/usage/본문)의 착지면
  - ADR-084  # 채번공간 disjointness — finding 증발 + 하류 계수 자기정합 실패형상 선례
related_concepts:
  - subagent-outcome-terminal-state-taxonomy   # outcome ⊥ termination_cause — 본 개념의 receipt_state 축과 disjoint subject (CFP-2994 AC-7 판정). 어휘 소유 관계가 아니라 축 분리 관계다
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
  - https://en.wikipedia.org/wiki/Negation_as_failure                                  # negation as failure (Clark 1978)
  - https://www.cs.ubc.ca/sites/default/files/tr/1977/TR-77-16.pdf                     # Reiter 1978 — closed-world assumption. NAF(Clark) 과 별 저자·별 논문 (CFP-2994 귀속 정정)
  - https://www.cs.utexas.edu/~EWD/transcriptions/EWD06xx/EWD687a.html                 # Dijkstra-Scholten — diffusing computation 종료 검출 (문헌 id = EWD687a)
  - https://en.wikipedia.org/wiki/Huang%27s_algorithm                                  # Huang weight-throwing — 가중치 보존 종료 검출 (정직성 무가정 아님 — 국소화)
  - https://www.cs.utexas.edu/~rossbach/cs380p/papers/Counters.html                    # CRDT G-Counter — ★ 본 개념의 형식 선례에서 제외됨(CFP-2994 P1-8). 현 선례 = G-Set (Shapiro et al. 2011 Spec 11)
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

Gray Failure(HotOS'17)는 "적어도 한 앱은 시스템이 unhealthy 하다고 관측하는데 관측자는 healthy 하다고 관측하는" 상태를 gray failure 로 정의하고, 그 핵심 특징을 **differential observability** 로 명명한다. 본 사건은 그 쌍대(dual)다 — 관측자(Orchestrator)는 "무도달"을, 당사자(PL)는 "전량 도달"을 관측했다.

> ★ **정정 (CFP-2994 요구사항리뷰 Iter 1 — 초판 과대 진술 `[refuted]`)**: 초판은 *"같은 논문의 처방이 곧 본 개념의 처방"* 이라 적고 **채널 불일치 declare 의무를 이 문헌의 published remedy 로 귀속**시켰다. **그 귀속은 성립하지 않는다.** 논문이 주는 것은 ① 현상의 **명명**(differential observability) ② *"bridging the gap between different components' perceptions"* 라는 **간극 해소의 필요성**까지이며, 그 처방의 형태는 **관측 통합(observation aggregation)** 이다. **「불일치를 은폐하지 않고 발화할 의무」는 논문에 없다.**
>
> ⇒ 정확한 위상: 논문 = **필요조건·1단계의 외부 근거**, **발화 의무는 본 개념의 신설분**이다. 신설분을 외부 문헌의 권위로 감싸면 그 조항은 반증 불가한 차용 권위를 얻게 되고, 이는 본 개념이 RSW-8 에서 금지하는 것(근거의 출처 계층 혼동)과 같은 계열이다.

### RSW-2 — 편측 표본 전칭 유도 = 개방 세계에 적용된 closed-world assumption

"내 inbox 에 없다 ⟹ 존재하지 않는다" 는 추론 규칙으로는 **negation as failure**(**Clark 1978**, *Negation as Failure*)이고, 그 규칙을 타당하게 만드는 **의미론적 전제**는 지식베이스가 **완전(complete)** 하다는 **closed-world assumption**(**Reiter 1978**, *On Closed World Data Bases*)이다. Orchestrator 의 inbox 는 완전한 지식베이스가 아니다. ∴ 이 추론은 논리적으로 무효이며, 개념적으로 "실수" 가 아니라 **정의역 위반**이다.

> ★ **귀속 정정 (CFP-2994 요구사항리뷰 Iter 1 `[refuted]`)**: 초판은 CWA 를 Clark 1978 에 함께 귀속시키는 형태로 서술했다. **NAF = Clark 1978 / CWA = Reiter 1978 로 별 저자·별 논문**이며, 본 건에 더 직접적인 것은 **CWA(Reiter)** 다 — 쟁점이 "추론 규칙을 썼는가" 가 아니라 "그 규칙을 정당화하는 완전성 전제가 이 정의역에서 성립하는가" 이기 때문이다.

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
| **CRDT G-Set** (Grow-only Set) | 각 주체가 자기 수령 사실을 **추가만** 한다. `remove` 가 **API 에 부재**해 「수령 → 미수령」 **역전이가 어휘에서 구조적으로 표현 불가** | Shapiro et al. 2011, Spec 11 — *"G-Set works even when the set of replicas is not known"* |
| Kafka | **consumer** 가 자기 offset 을 commit. group coordinator 가 소유권 상실 consumer 의 commit 을 **fence** | Kafka consumer offsets |
| AMQP / RabbitMQ | consumer ack 과 publisher confirm 은 **별개 기전** — *"consumer acknowledgements are not aware of publishers"* | RabbitMQ confirms |
| Erlang/OTP | 종료 신호는 링크된 **supervisor(부모)** 로 전달 | OTP processes |

> ★ **형식 선례 교체 (CFP-2994 요구사항리뷰 Iter 2 P1-8 — 초판 CRDT **G-Counter** `[refuted]`)**: 초판은 G-Counter 를 P-1 의 최강 형식 선례로 들며 *"소유자-전용성이 merge 규칙 자체에 내장"* 이라 서술했다. **논거 3건이 전부 붕괴한다** — ① 소유자-전용성의 담지자는 merge 가 아니라 **`update` 규약**(`let g = myID()`)이다. merge(pointwise max)는 **provenance 를 검사하지 않으므로** 남의 슬롯에 큰 값을 써서 병합시키는 위반이 **표현 가능**하다 ② 위조된 큰 값은 well-formed 이고 max 는 단조라 **한 번 흡수되면 영구 고착 = 증폭**(정정 불가)이다 — RSW-4 가 요구하는 **취소 가능성과 정면 충돌** ③ 원 논문 §2 가 *"We assume non-byzantine behaviour"* 를 명시 전제하며, G-Counter 는 **replica 집합이 well-known** 일 것을 요구하는데 본 개념의 정의역은 정확히 **그 가정이 깨진 곳**(관측 비대칭 ⇒ 상대 채널 열거 불가, 그리고 carrier Story 에서 roster 자체가 실 fan-out 집합과 불일치함이 확정됐다).
>
> ⇒ **정답 = G-Set**. 필요한 성질은 "슬롯 소유" 가 아니라 **「수령 → 미수령」 역전이의 어휘적 부재**이며, 원 사건이 정확히 그 역전이였다. **설계 함의**: 수령 원장을 grow-only 집합으로 두면 *"타 주체의 수령을 취소하는"* 연산이 **어휘에서 사라진다** — 금지 규범이 아니라 표현 불가능성으로 강제된다.
>
> ★ **근거 계층 declare**: 위 ③의 인용문은 원 논문 축자이나 본 파일 저자는 Shapiro 2011 원문을 firsthand 재조사하지 않았다(carrier Story 요구사항리뷰 lane 재검증 경유). 다만 **교체 판정 자체는 중계 사실에 의존하지 않는다** — ①(merge 의 provenance 미검사)과 ③ 후단(well-known replicas 가정 파손)은 본 개념 내부 사실만으로 성립한다.

### RSW-7 — 계수 항등식은 종료 검출(termination detection)의 특수형

fan-out 완결 판정은 **종료 검출** 문헌의 보존 불변식과 동형이다.

> ★★ **정정 (CFP-2994 요구사항리뷰 Iter 2 P2-2 — 초판 2항 판본은 산술적으로 거짓)**: 초판은 이 불변식을 `스폰 수 == 수령 수 + 미수령 수` 라는 **단일 2항 항등식**으로 적었다. **성립하지 않는다** — `미스폰`(애초에 스폰하지 않은 축)은 **roster 정의역**의 값인데 좌변 `스폰 수` 는 **spawned 정의역**이라, 한 항등식에 두 정의역이 혼합된다. carrier Story 의 실 원장에서 이 판본은 `0 == 0+0+0+7` 같은 **좌우 불일치**를 낳았다.
>
> **정확한 형태 = 2단 분해 (단 간 합산 금지)**:
>
> | 단 | 정의역 | 항등식 |
> |---|---|---|
> | **1단** | roster (선언된 fan-out 축 전수) | `roster == 스폰 + 미스폰 + 단-미상` |
> | **2단** | spawned (실제 스폰된 축) | `스폰 == 수령 + 미수령 + 미상` |
>
> ★ **정정 (CFP-2994 요구사항리뷰 RESET 후 Iter 3 · P1-C)**: 위 두 항등식의 항 이름에서 수식어 ` declare` 접미를 제거했다(`미스폰 declare` → **`미스폰`**, `미수령 declare` → **`미수령`**). carrier Story §5.3 의 규약 W-5 및 강제층 술어 EF-4 ⑥ 가 상태값 셀을 **CLOSED 5값 verbatim**(`수령`·`미수령`·`미상`·`미스폰`·`단-미상`)으로 성문하므로 `미스폰 declare` 는 **값역 밖**이며, 이 표기를 정본으로 두면 채택 원장이 born-broken 이 된다. 본 파일의 다른 `declare` 는 전부 **동사 용법**(불일치를 은폐하지 않고 발화할 의무 / 원 사건의 파괴적 지시 인용)이며 상태값 이름의 일부가 아니다.
>
> ★★ **정정 (CFP-2994 설계 lane 결정 C-7 — 4번째 항 `기타 종결` 은 도달 불가 dead term `[refuted]`)**: 위 2단 항등식은 초판에 `스폰 == 수령 + 미수령 + 미상 + 기타 종결` 이라는 **4-term** 으로 성문돼 있었다. **`기타 종결` 은 상태값 CLOSED 값역에 대응 값이 없다** — 바로 위 P1-C 정정이 **같은 파일에서** 이미 값역을 5값 verbatim(`수령`·`미수령`·`미상`·`미스폰`·`단-미상`)으로 못박았으므로, 이 4번째 항은 **어떤 원장 행으로도 채워질 수 없는 도달 불가 항**이었다. ⇒ **본 파일 안에 모순이 상주하고 있었다**(정정 전파를 자기 파일에서 먼저 완주하지 못한 두 번째 사례 — 첫 사례 = 「변경 이력」 2026-08-17 RESET 후 Iter 1 ①).
>
> **숨어 있던 이유 = 그 항이 항상 0 이기 때문이다.** [ceiling: 값역 도달성 논증 — 기타 종결 이 receipt_state CLOSED 5값 중 어느 값에도 대응하지 않는다는 사실에서 따라온다. 이 명제를 재는 검사기·test 자산은 internal-docs 소관이라 본 repo tests 정의역 밖] 도달 불가 항은 합에 0 만 기여하므로 항등식은 계속 성립했고, 독자도 검사기도 이상을 관측할 신호를 받지 못했다. 이것은 본 파일이 **RSW-8 에서 지목하는 누락 오류(errors of omission)의 자기 사례**다 — 빠진 것이 균형을 깨지 않으면 균형 검사는 그것을 잡지 못한다.
>
> ⇒ **정본 = 3-term** `스폰 == 수령 + 미수령 + 미상`. 이 제거는 **값역을 넘지 않고 산술을 바꾸지 않는다**(무손실) — 대안이던 「6번째 상태값 신설」은 carrier Story 의 **신규 어휘 0** 제약 위반이라 기각됐다.
>
> ★ **개념 층 신설 — INV-5**: 음성 검사(4-term 재삽입 시 RED)만 두면 **또 다른 dead term 의 신설이 무방비**다. 따라서 항 단위 금지가 아니라 성질 단위 불변식을 둔다 — ***항등식 term 전수가 상태값 값역에서 도달 가능하다.*** 이는 RSW-8 의 **독립 출처** 요건, RSW-7 의 **중첩 비합성** 요건과 같은 층의 **3번째 구성 요건**이며, 「도달 불가 항이 항등식의 검출력을 조용히 갉아먹는다」는 일반 형상을 닫는다.
>
> 근거 = `mclayer/codeforge-internal-docs` `wrapper/change-plans/cfp-2994-receipt-single-writer.md` **`## §3. 도입할 설계` → `### §3.4 Phase 2 필수 코드 항목 C-1~C-9 (Phase 3 검수 항목)` → `#### C-7 — ⑦ `기타 종결` 제거 + INV-5`** 절.
>
> **2단 좌변이 0 이면 그 항등식은 vacuous** 하며(무조건 참 = 검출력 0), 그 사실을 명시하지 않은 채 *"항등식 성립"* 을 근거로 쓰는 것은 `vacuous-pass` 형상이다. **`단-미상`** = 어느 단에 속하는지 자체가 판별 불가한 축(예: 스폰 주체가 기록자 본인이 아니어서 스폰 여부를 관측할 수 없는 축)을 위한 값으로, 한 방향으로 분모를 편향시키지 않기 위해 존재한다.

- **Dijkstra-Scholten (`EWD687a`)** — diffusing computation 에 initiator 를 뿌리로 하는 신장 트리를 유지. 각 노드는 미결 메시지의 **deficit counter** 를 갖고, **자기 자식이 전부 signal 을 보낸 뒤에만 부모에게 signal** 한다. initiator 의 counter 가 0 이 될 때만 종료를 선언한다.
- **Huang weight-throwing (1989)** — controlling agent 가 가중치 1 로 시작, 위임 시 가중치를 분할, idle 이 된 프로세스는 자기 가중치 전량을 반환. **총 가중치가 항상 1 로 보존**되며 controller 의 가중치가 1 로 복귀할 때가 종료. ★ **정직 정정 (CFP-2994 Iter 1)**: 이 기제는 **정직성 가정을 제거하지 않는다** — 각 프로세스가 자기 가중치를 정직하게 분할·반환한다는 전제가 필수이고 한 노드가 위조하면 총합 보존이 깨진다. 정확한 성질은 **「정직성 무가정」이 아니라 「정직성 요구의 국소화」**(조부가 손자를 몰라도 무해하나 **직부모의 프로토콜 이탈은 여전히 파괴적**)다.

**중요 함의 — 평면 계수는 중첩에 대해 합성되지 않는다.** PL 수준의 2항 계수는 손자 세대에 대해 아무 말도 하지 않는다. 중첩 fan-out 이 존재하면 (a) Dijkstra-Scholten 규율(자식 전원 완결 전 부모에게 완결 signal 금지) 또는 (b) Huang 가중치 보존 중 하나가 필요하다.

### RSW-8 — 항등식이 항진이 되지 않으려면 항이 독립 출처여야 한다

복식부기 시산표(trial balance)는 **누락 오류(errors of omission)를 잡지 못한다** — 거래가 통째로 빠지면 차변·대변이 함께 빠져 여전히 균형이 맞는다. 보상 오류(compensating errors)도 같다.

이것이 본 사건의 실패 형상과 **정확히 동일**하다: 4축이 애초에 없었던 것처럼 처리되면 스폰 수도 함께 줄어 항등식은 여전히 성립한다(자기정합). ∴

> **항등식의 각 항은 서로 독립인 출처에서 와야 한다.** 특히 `스폰 수` 는 보고 시점 당사자의 기억이 아니라 **스폰 시점에 독립적으로 방출된 기록**에서 와야 한다. 회계의 대응 처방이 외부 명세서 대조(external reconciliation)이고, 원격 증명의 대응 처방이 **RATS(RFC 9334)의 Attester ≠ Verifier 분리** — 자기 증명(self-attestation)은 그 자체로 신뢰의 근거가 아니다.

### RSW-9 — **무한 중첩** common knowledge 를 종결 조건으로 삼지 말 것 (축소 판정)

Halpern-Moses 는 비동기·비신뢰 채널에서 **common knowledge `C_G φ`(무한 중첩 지식)가 도달 불가능**함을 보였다(coordinated attack).

> ★★ **도출 축소 (CFP-2994 요구사항리뷰 Iter 1 — 초판 도출 `[refuted]`)**: 초판은 여기서 *"「송수신 양측이 무엇이 도달했는지 합의한다」를 설계 목표로 두면 증명된 불가능을 쫓게 된다"* 를 유도했다. **인용은 정확하나 도출이 무효**다:
> 1. 같은 논문이 *"weaker variants … attainable in many cases of interest"* 를 명시한다. (단 eventual common knowledge 의 도달 가능성은 **reliable broadcast 를 전제**하며, 본 개념의 정의역은 **그 전제의 성립 여부 자체가 쟁점**이다 — 따라서 이 근거는 단독으로는 불충분하다.)
> 2. **불가능성의 원천은 「비동기」가 아니라 「절대적 동시성」** 요구이며, 논문 §9 자신이 그 요구를 *"more than necessary in many particular applications"* 로 규정한다. 본 개념은 동시성을 요구하지 않는다 — **수령 사실의 사후 상호확인**이면 충분하다.
> 3. **범주 오류** — 본 개념이 필요로 하는 것은 `K_orch(PL 이 수령함)` = **1차 지식 `K¹`** 이고 HM 의 대상은 `C_G φ` = **무한 중첩**이다. 1차 지식의 도달 가능성을 무한 중첩의 불가능성으로 부정한 것이다. (근거 2·3 은 외부사실에 의존하지 않는 순수 논리라 **단독으로 도출 무효를 성립**시킨다.)
>
> ⇒ **실질 피해**: 이 조항은 **범위 조항**이었으므로, 무효 도출이 *"내가 받은 것은 이것이다. 네 채널은 네가 독립 확인하라"* 형태의 **1-round ack 기반 상호확인**(carrier Story 의 사용자 원문이 직접 제시한 비파괴 대안)까지 범위 밖으로 밀어낼 수 있었다. **1-round ack 은 무한 중첩이 아니며 도달 가능하다.**
>
> ⇒ **축소된 조항**: 배제 대상은 「양측 합의」 일반이 아니라 **「무한 중첩 `C_G φ` 를 lane 종결 조건으로 삼는 것」** 뿐이다.

그 한정 위에서, 실행 가능한 목표는:

1. 각 주체가 **자기 관점만** 공표하고(single-writer),
2. 불일치는 **은폐하지 않고 declare** 하며(★ **본 개념 신설분** — 위 RSW-1 정정 블록이 이 의무의 Gray Failure 논문 귀속을 철회했다. 논문이 주는 것은 현상 명명 + 간극 해소 필요성까지이고, 그 처방의 형태는 관측 통합이다),
3. 정합은 **제3의 독립 관측자**가 항등식으로 검사한다(Attester ≠ Verifier).

## 경계

- **In scope**: 다주체 fan-out 에서 수령 사실의 기록 권한, 부정 단언의 유효성 조건, 관측 비대칭의 명명·처방, 완결 판정 항등식의 구성 요건(독립 출처 · 중첩 합성 · 상태 열거 완전성).
- **Out of scope**:
  - **구체 라우팅 기전** — 어떤 통지가 어느 주체에게 가는지를 가르는 harness 내부 기전. 본 개념은 **라우팅 기전과 무관하게** 성립하도록 설계됐다(관측 비대칭을 전제로 한 방어). 기전 규명은 disjoint 축.
  - **subagent 종결상태 어휘** — *"subagent 가 어떻게·얼마나 잘 끝났나"* 계열(`outcome` / `termination_cause` / recovery-action)은 `subagent-outcome-terminal-state-taxonomy` 소유이며 본 개념은 그 축에 어휘를 신설하지 않는다.
    > ★★ **정정 (CFP-2994 요구사항리뷰 Iter 2·3 AC-7 판정 — 초판 서술의 부정 명제)**: 초판은 *"「미수령」의 enum 분류는 그 taxonomy **소유**이며 본 개념은 어휘를 **재사용**하고 신규 vocabulary 를 만들지 않는다"* 라고 적었다. **성립하지 않는다** — `수령`·`미수령`·`미상`·`미스폰`·`단-미상` 은 그 taxonomy 의 closed enum(`outcome`/`termination_cause`, 둘 다 `open_extension:false`) **값역 전부 밖**이므로, 문면대로면 **재사용해도 값역 위반, 안 해도 미정의 값 참조**로 양쪽이 막힌다.
    >
    > **정확한 관계 = disjoint subject (별 축)**. 판정 형식은 그 taxonomy 자신이 이미 1회 수행했다 — 같은 파일의 「경계」 절이 *"`reason_class`(**Orchestrator 가 왜 멈췄나**)는 subagent-termination 과 **disjoint subject**"* 라고 선언한다.
    >
    > | 축 | subject | 질문 |
    > |---|---|---|
    > | `outcome` | subagent | 산출이 쓸 만했나 |
    > | `termination_cause` | subagent | 어떻게 멈췄나 |
    > | `reason_class` | Orchestrator | 왜 멈췄나 |
    > | **`receipt_state`** (본 개념) | **수신자** | **무엇을 관측했나** |
    >
    > **결정적 구별 = 관측자 상대성.** `수령`/`미수령` 은 subagent 의 성질이 아니다 — 같은 subagent 의 같은 종료에 대해 **수신자마다 값이 다르다**(carrier 사건에서 4축은 Orchestrator 기준 `미수령` ∧ PL 기준 `수령` 이 **동시에 참**이었다). `outcome`/`termination_cause` 는 관측자와 무관한 단일 값을 갖는다. ⇒ **관측자 상대적인 축을 관측자 절대적인 축의 enum 에 밀어넣는 것이 곧 conflate** 이며, "3번째 divergent vocabulary 신설 금지" 가 실제로 금지하는 것을 오히려 범하게 된다.
    >
    > 그 금지의 scope 는 축자상 **outcome / recovery-action 계열 vocabulary** 한정이지 전 축에 대한 무제한 어휘 금지가 아니다. ⇒ **별 축 신설은 위반이 아니다.**
>
> ★★ **배치 확정 (CFP-2994 설계 lane — 초판의 「설계 lane 미결 문항」 해소)**: 초판은 이 자리에 *"`receipt_state` 를 **어느 문서에 성문할지**(본 파일 / 그 taxonomy 의 경계 절 / ADR carrier)는 carrier Story 의 설계 lane 미결 문항이다 — 판정은 확정, **배치는 미확정**"* 을 남겼다. **설계 lane 이 풀었다.** 그리고 답은 「문서 하나」가 아니었다 — **물음 자체가 세 층을 한 덩어리로 묶고 있었다.** 확정된 배치는 3층 분할이다.
>
> | 층 | 무엇을 성문하나 | 정본 |
> |---|---|---|
> | **경계 규범** | `receipt_state` 가 무엇을 기록할 수 **있는가** = **도달(arrival) 전용**. 허용 = 도달 여부 · 도달 채널 귀속 · 판정 근거 / **금지 = 충분성 · 품질 · 채택 가치** | `archive/adr/ADR-139-background-wait-liveness-gate.md` 의 **「Amendment 3」 → 「A3-4 — 경계 3항 (성문)」 (ii)** ∧ `archive/adr/ADR-170-orchestrator-subagent-default-inline-whitelist.md` 의 **「Amendment 2」 → 「A2-4 — receipt_state = 도달(arrival) 전용 경계」**. 두 조항이 서로를 paired 로 명시한다 |
> | **값역 · 표기 규약** | CLOSED 5값 · 원장 9열 signature · 표기 규약 W-1~W-8 · 착지 토큰 | **Story-local 문서 schema** — `mclayer/codeforge-internal-docs` `wrapper/change-plans/cfp-2994-receipt-single-writer.md` 의 **「§4.2 컨텍스트 · 이벤트 스키마 + 타입 정의」 (a)** ∧ **「§11.1 Schema 변경」**(4→5값 = MINOR 실발동). ★ **inter-plugin contract 아님** — 같은 문서 **「§13.C Cross-plugin coordination」** 이 *"MANIFEST 등재 대상 아님"* 으로 확정 |
> | **개념 서술 · anti-pattern** | **왜** 그 경계가 필요한가 · 위반 형상 | **본 파일 유지** — SSOT 이동 없음. 개념 층의 정본은 여기다 |
>
> **경계 규범이 개념 doc 이 아니라 ADR 로 간 이유**: 「받았다 ⇒ 쓸 만하다」 함의가 붙는 순간 그 field 는 **성과 verdict** 가 되고, verdict 판정 권한은 ADR-139 의 `INV-L4` 가 lead 에 고정한다(축자 = *"대기 주체 ↔ 판정 주체 분리"*). **도달-전용 경계는 INV-L4 를 침범하지 않는 유일한 형태**다. ⇒ 이 조항의 성질은 개념 서술이 아니라 **권한 경계**이며, 권한 경계의 정본은 규범 carrier 여야 한다.
>
> ★ **값역이 두 ADR 어디에도 없는 것은 drift 가 아니라 3층 분할의 귀결이다** `[verified]`. 정의역 = 위 두 ADR 전문 @ wrapper `03b7025b9` · 명령 = `git grep -c '<토큰>' 03b7025b9 -- archive/adr/ADR-139-*.md archive/adr/ADR-170-*.md` · 결과 = `단-미상` · `미스폰` · `9열` · `W-1` 전건 0 **이면서 같은 명령이 `receipt_state` · `INV-L4` 에는 hit 를 낸다**(양성 대조군 — 이 0 은 grep 사망이 아니다). 값역을 ADR 에서 찾지 못한 독자가 그것을 **누락으로 읽지 않도록** 여기 적어 둔다. [ceiling: 근거 3-tuple 이 같은 줄에 이미 병기됨 — 정의역(두 ADR 원문 @ 03b7025b9) · 명령(git grep -c) · 양성 대조군(같은 명령이 receipt_state 와 INV-L4 에는 hit). 사람이 재현할 수 있으나 본 repo tests 자산으로는 미배선]
>
> ★ **동명이의 주의 (전사 함정 — 본 파일이 직접 피한 자리)**: carrier Story 의 리뷰 축은 이 부재를 *"ADR-170 Amd 2 가 자기 scope 를 「§결정 2 enumeration 무변경」으로 명시하므로 ADR 은 enum carrier 가 아니다"* 로 설명한다. **그 문장을 이 파일에 그대로 옮기면 오귀속이 된다** — ADR-170 이 「무변경」이라 선언한 enumeration 은 **inline whitelist 7-entry** 이지 `receipt_state` 값역이 아니다. 두 enum 이 **같은 단어를 공유할 뿐 별개 대상**이며, 이는 본 파일이 RSW-2 에서 지목하는 **정의역 위반**의 어휘 판본이다. ⇒ 부재의 정본 근거는 위 3층 분할이지 그 인용문이 아니다.
  - **타임아웃 상수 값** — 대기 시간의 구체 수치는 운영 튜닝 영역. 본 개념은 "판정이 취소 가능하고 비파괴적일 것"만 요구한다(RSW-4).
- **Anti-pattern**:
  - 발신자가 수신자 채널에 대해 `state:assertion` 발행(RSW-6 월권).
  - **타 주체가 수행한 스폰에 대해 `미스폰` 을 단언**(RSW-6 의 스폰 상태 판본). 수령 상태의 single-writer 만 성문하고 **스폰 상태의 기록자를 비워 두면**, 파괴적 지시는 *"그 축들은 스폰 안 됐다 — 미스폰으로 계상하라"* 로 **정의역을 갈아타고 그대로 통과**한다. 스폰 여부를 관측할 수 없는 축의 정직한 값은 `미스폰` 이 아니라 **`단-미상`** 이다.
  - **정정을 산출물 경계 밖으로 전파하지 않음** — 어떤 판정을 문서 A 에서 정정하고 그 판정의 **부정 명제를 담은 문서 B**(개념 SSOT·설계 지시·어휘 범례)를 그대로 두면, B 가 영구 artifact 인 한 하류가 **정정 이전 판본을 조용히 승계**한다. 처방 = 정정 대상 artifact **인벤토리 + 매 정정마다 전수 스윕**.
  - 편측 표본에서 라우팅 전칭 규칙 유도(RSW-2 정의역 위반).
  - 시점 관측을 구조적 법칙으로 승격(RSW-3).
  - "미수령" 판정이 삭제·공란화 등 **파괴적** 후속을 유발(RSW-4 비가역 의심).
  - 항등식의 두 항을 **같은 주체의 같은 시점 기억**에서 도출(RSW-8 누락 오류 맹점 = 항진).
  - 평면 2항 계수를 중첩 fan-out 에 그대로 적용(RSW-7 비합성).
  - 검출을 하위 주체의 자발적 정직에 위임(RSW-8 self-attestation).

## 관련 ADR

> ★ **정정 (CFP-2994 설계 lane 정정 전파 스윕 — 초판 disclaimer 의 정의역 축소)**: 초판은 *"아래 ADR **원문을 읽지 않았다** … 매핑은 좌표 기반 **후보**이며, 확정 매핑은 요구사항리뷰·설계 lane 소관"* 을 **5건 전체**에 걸었다. 그 disclaimer 는 이제 **2건에서 해소, 4건에서 존속**한다 — 통째로 지우는 것은 over-claim 이다.
>
> | 상태 | ADR | 근거 |
> |---|---|---|
> | **확정 (firsthand 실독)** | **ADR-170** · **ADR-139** | 본 스윕이 wrapper `03b7025b9` 에서 두 파일 원문을 직접 읽고 조항 앵커를 대조했다. 설계 lane 이 배치를 확정했고(위 「경계」 절 3층 표) 두 조항이 서로를 paired 로 명시한다 |
> | **후보 존속 (미실독)** | ADR-073 · ADR-119 · ADR-093 · ADR-084 | 본 스윕의 정의역은 `receipt_state` 배치 문항이 지목한 2건뿐이다. 나머지 4건은 **읽지 않았고** 좌표 기반 후보로 남는다 |


- **ADR-170** `[확정 — firsthand]` — orchestrator↔subagent 기본규율. RSW-5(단조/비단조 분할)의 성문 carrier = **Amendment 2 「A2-5 — 메시지 종별: 단조 ⊥ 비단조 + 소유자 동의 요구」**(판정 술어를 라벨 열거가 아니라 **효과의 단조성**으로 두어 RSW-5 를 그대로 승계). RSW-6(권한 경계)의 성문 carrier = **Amendment 2 「A2-4」** 의 도달-전용 경계.
  ★ **정직 declare**: A2-5 · A2-3 는 자기 등급을 *"`normative` 이나 집행 표면 0"* 으로 명시한다(발화 채널에 hook matcher 0). ⇒ 본 개념이 ADR 로 성문됐다는 사실은 **사후 지목 가능성**을 뜻하지 사전 차단을 뜻하지 않는다 — RSW-4 가 요구하는 「비파괴·취소 가능」과 같은 등급의 정직 천장이다.
- **ADR-139** `[확정 — firsthand]` — background-wait liveness gate. **Amendment 3 「A3-4 — 경계 3항 (성문)」 (ii)** 가 `receipt_state` 를 **도달 전용**으로 한정하고, 그 근거로 `INV-L4`(대기 주체 ↔ 판정 주체 분리)가 verdict 권한을 lead 에 고정함을 든다. ★ 같은 Amendment 「A3-4」 (iii) 이 본 개념에 대한 **비자명한 보강**을 담는다 — depth ≥ 1 에서는 **전 주체가 worker ∧ receiver 를 겸하므로** 「worker 는 판정하지 않는다」와 「receiver 만 수령을 기록한다」가 같은 주체에 동시에 걸리고, ⇒ **규범 문구로는 분리를 지킬 수 없고 산출물 schema 의 field 분리로만 지켜진다**(수령 기록 field ⊥ verdict field, 기록자를 field 단위로 고정). 이는 본 파일 RSW-6 의 단일 주체 서술이 **중첩 fan-out 에서 겸직으로 무너지는 지점**을 메운다.
- **ADR-073** — verify-before-assert. RSW-2(관측 scope 초과 단언 금지)의 상위 규범.
- **ADR-119** — research-before-claims. "게이트 verdict = proxy 아닌 outcome ground-truth" 가 RSW-8(자기보고 ≠ 근거)과 동근.
- **ADR-093** — 완료 보고 4-field schema. 수령 판정 3종(완료 통지 status / usage 메트릭 / 본문 실재)이 착지하는 면.
- **ADR-084** — 채번공간 disjointness. "finding 이 통째로 증발하고 하류 계수는 항상 자기정합" 실패형상의 사내 선례 = RSW-8 의 실증.

## 변경 이력

- **2026-08-18 KST — CFP-2994 설계 lane 정정 전파 스윕 (§10.8 회부 이행 · `correction_sweep_required` 발동).** 설계 lane 이 소유권 경계를 지켜 본문을 고치지 않고 회부한 무효화 2건 + 본 스윕이 추가 발굴한 1건을 전파했다. ① **항등식 dead term 제거** — 2단 항등식이 `기타 종결` 을 포함한 4-term 이었으나 그 값은 상태값 CLOSED 값역에 **대응 값이 없다**. 바로 위 P1-C 정정이 **같은 파일에서** 값역을 5값 verbatim 으로 못박은 뒤였으므로 **본 파일 안에 모순이 상주**하고 있었고, **그 항이 항상 0 인 덕분에 숨어 있었다**(RSW-8 누락 오류의 자기 사례). [ceiling: 위 RSW-7 정정 블록의 값역 도달성 논증을 재기술한 것 — 근거는 그 절에 있고 본 줄은 이력 요약이다. 검사기·test 자산은 internal-docs 소관] 정본 = 3-term + **INV-5** 를 항 단위 금지가 아니라 성질 단위 불변식(*항등식 term 전수가 값역에서 도달 가능*)으로 개념층 신설. ② **「설계 lane 미결 문항」 해소** — `receipt_state` 배치가 **3층 분할**로 확정(경계 규범 = ADR 2건 / 값역·표기 = Story-local 문서 schema / 개념 서술 = 본 파일). 「어느 문서 하나에 넣을까」라는 물음 자체가 층을 섞고 있었다. ③ **본 스윕 추가 발굴** — 「관련 ADR」 절의 *"원문을 읽지 않았다 … 확정 매핑은 타 lane 소관"* disclaimer 가 ②를 정면으로 되돌리는 stale 표면이었다(그대로 두면 하류가 확정된 배치를 다시 후보로 읽는다). 정의역을 **2건 해소 / 4건 존속**으로 축소하고 **ADR-139 를 신규 등재**(초판은 frontmatter·본문 양쪽에서 이 carrier 를 통째로 누락). ★ **전사 함정 1건 회피**: 리뷰 축이 값역의 ADR 부재를 *"ADR-170 Amd 2 = §결정 2 enumeration 무변경"* 으로 설명하나, 그 enumeration 은 **inline whitelist 7-entry** 이지 `receipt_state` 값역이 아니다 — **같은 단어를 공유하는 별개 enum** 이라 그대로 옮기면 오귀속이 된다(RSW-2 정의역 위반의 어휘 판본). 부재 근거를 3층 분할로 교체하고 양성 대조군 동반 실측으로 pin 했다.
- **2026-08-17 KST — CFP-2994 요구사항리뷰 RESET 후 Iter 1 판정 반영 (잔여 P1 2건).** ① RSW-9 실행 목표 2항의 `(differential observability 처방)` 을 **본 개념 신설분** 표기로 교체 — `RSW-1` 정정 블록이 이미 철회한 「불일치 declare 의무 = Gray Failure 논문의 처방」 귀속을 **같은 파일이 재주장**하고 있었다. frontmatter `correction_sweep_required: true` 를 본 파일이 **자기 파일 내 스윕 미완주**로 위반한 형상이며, 리뷰가 실물 확인해 검출했다(정정 전파는 타 문서로 나가기 전에 자기 파일에서 먼저 완주해야 한다). ② CWA 출처 URL 교체 — 구 URL `cs.utexas.edu/~ear/cs378/CWA.pdf` 은 **HTTP 404**(실측), 신 URL `cs.ubc.ca/sites/default/files/tr/1977/TR-77-16.pdf` 은 **HTTP 200**(실측, Reiter, *On Closed World Data Bases*, UBC Technical Report TR-77-16). 귀속 문면(Clark 1978 ↔ Reiter 1978 분리)은 보존.
- **2026-08-17 KST — CFP-2994 요구사항리뷰 Iter 1~3 판정 전파 (P0 해소).** 본 파일은 carrier Story 의 유일한 영구·cross-Story artifact 인데 Iter 1·2 재설계가 **0% 전파된 채** main 착지 직전이었고, 그 결과 Story 결론의 **부정 명제 5건**을 담고 있었다. 전파 항목: ① 「종결상태 어휘는 taxonomy 소유·재사용」 → **disjoint subject(별 축 `receipt_state`) 판정**으로 교체 ② 2항 계수 항등식 → **2단 분해**(정의역 혼합이 산술적 거짓을 낳음) ③ 형식 선례 **G-Counter → G-Set**(논거 3건 붕괴 — provenance 미검사 / 위조값 영구 고착 / well-known replicas 가정 파손) ④ Halpern-Moses **도출 축소**(불가능성 원천 = 절대적 동시성, 본 건은 1차 지식 `K¹`) ⑤ 문헌 id `EWD687` → **`EWD687a`**. 추가 정정 2건(리뷰가 과잉 계상 방지로 유보했던 항목을 본 lane 이 firsthand 판정): ⑥ **Gray Failure** — 「declare 의무 = 논문의 published remedy」 귀속 철회(논문은 관측 통합까지, 발화 의무는 본 개념 신설분) ⑦ **NAF/CWA 귀속 분리**(Clark 1978 ↔ Reiter 1978). anti-pattern 3건 추가(스폰 상태 월권 / 정정 미전파). frontmatter 에 `correction_sweep_required` 명시 — 본 파일을 정정 전파 인벤토리의 1급 항목으로 등재.
- 2026-08-16 KST — 초기 작성 (CFP-2994 요구사항 lane, ResearcherAgent Mandate 1·2 산출물). differential observability(Gray Failure HotOS'17) · negation as failure/CWA(Clark 1978) · Chandy-Lamport 전역 스냅샷 · FLP + Chandra-Toueg completeness/accuracy · CALM 정리 · actor/object-capability 권한 경계 · CRDT G-Counter / Kafka offset / AMQP ack / Erlang OTP 산업 선례 · Dijkstra-Scholten + Huang 종료 검출 · 시산표 누락 오류 + RATS(RFC 9334) 독립 검증 · Halpern-Moses common knowledge 불가 를 cited 로 정립. 사내 선행 개념 `subagent-outcome-terminal-state-taxonomy` 어휘 재사용 명시(신규 vocabulary 금지).
