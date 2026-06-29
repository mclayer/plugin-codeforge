---
name: research-request-gate
description: lane 이 작업 *중* 외부사실 의존으로 막혔을 때(known-unknown 깊은 질문) Orchestrator 가 따르는 on-demand 깊은 조사 보충 절차. lane 이 scope-clear 조사 요청을 올림 → Orchestrator 가 문지기로 게이트 심사(scope 명확성 / shallow-vs-deep 문턱 / 흐린 요청 반려) → harness-native deep-research 실행(Orchestrator 전용) → cited 결과를 요청 lane 재spawn packet 으로 주입. 외부지식 충당 3-단계(ADR-124) 중 단계③ 의 on-demand 경로(review-time 게이트 S2/S3 와 disjoint). caller scope = Orchestrator preset 한정. ADR-126 SSOT / ADR-124 §결정 1·2·6 / ADR-039 §결정 1·2 정합. Amendment 1 (CFP-2459) — execute Codex 2차 출처 corroboration.
tools: Read
---

# codeforge:research-request-gate (CFP-2329 / Epic CFP-2324 S5 — 단계③ on-demand pull)

> lane 이 작업 *중* 외부사실 의존 known-unknown 으로 막혔을 때(예: 설계 결론이 어떤 외부 프로토콜·표준의 진위에 좌우되는데 얕은 자가조사(단계②)로는 닫히지 않을 때), Orchestrator 가 깊은 다출처 검증(deep-research)을 보충해 주는 절차. lane 은 **요청만 올리고**, 실행(deep-research 호출)은 Orchestrator 가 한다.
>
> 정책 SSOT = [ADR-126](../../archive/adr/ADR-126-on-demand-research-request-gate.md). 본 skill 은 그 정책의 **운영 절차 carrier**. 외부지식 충당 3-단계 모델 = [ADR-124](../../archive/adr/ADR-124-external-knowledge-provisioning-model.md) §결정 1, 깊은 검증 발동 게이트 = ADR-124 §결정 2, 외부사실 의존 휴리스틱 = ADR-124 §결정 6.
>
> **caller scope (ADR-039 §결정 1/2 경계 정합)**: 본 절차는 **Orchestrator preset 한정**. 임의 SubAgent 는 본 절차의 게이트 심사·deep-research 호출 비대상(deny) — lane(subagent)이 스스로 deep-research 를 호출(=spawn)하면 재귀-spawn limit 와 충돌하므로([ADR-039](../../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) 회피 대안 C "subagent → Agent tool 호출 금지"), lane 은 **요청만** 올린다. deep-research 실행은 spawn 독점 주체인 Orchestrator 의 행위 (jira-decision-channel "Orchestrator preset 한정, 임의 SubAgent deny" 선례 동형).

---

## 단계③ 의 두 경로 (review-time ↔ on-demand)

깊은 다출처 검증(ADR-124 §결정 1 단계③)은 두 경로로 진입한다. 본 skill 은 그 중 **on-demand** 경로 전담이다.

| 경로 | trigger | 주체 | 시점 | carrier |
|---|---|---|---|---|
| review-time(자동 게이트) | 요구사항리뷰 lane 진입 (자동) | RequirementsReviewPL → Claude/Codex dual-peer | 설계 진입 *전* | S2 (ADR-125) + S3 차등 (ADR-124 Amendment 1) |
| **on-demand(pull)** | lane 이 작업 *중* 외부사실 의존으로 막힘 | 임의 lane(요청) + Orchestrator(문지기·실행) | 작업 *중* | **본 skill (S5 / ADR-126)** |

> 두 경로는 trigger·주체·시점이 갈리는 **disjoint** 관계 (SSOT = [ADR-125](../../archive/adr/ADR-125-requirements-review-lane.md) §결정 6 "on-demand 경로(S5) 와 disjoint … 깊이의 차등 메커니즘 실구현은 S3 로 보존"). 같은 deep-research skill body 를 trigger·주체·시점만 달리 진입한다.

---

## 절차 추상 단계 (channel-agnostic)

on-demand 보충은 아래 **추상 단계**로 정의한다. 절차 본체는 mechanism 비의존이고, env=1 team-mode SendMessage / env=0 round-trip 의 mechanism 바인딩은 "mechanism 이중 경로" 절에만 둔다.

| 추상 단계 | 의미 | 책임 |
|---|---|---|
| `request` | lane 이 scope-clear 조사 요청을 올림 | lane (요청 형식) |
| `gate` | Orchestrator 가 문지기로 요청 심사 (3-규칙) | Orchestrator |
| `theater_check` | 외부사실 의존 게이트 + 검사연극 차단 (ADR-124 §결정 2/6 상속) | Orchestrator |
| `execute` | harness-native deep-research(1차 web) **+ Codex/GPT-5 독립 2차 출처** 호출 (Orchestrator 전용) | Orchestrator |
| `inject` | cited 결과를 요청 lane 재spawn packet 으로 주입 | Orchestrator |

---

## 1. lane 조사 요청 형식 (`request`)

lane 은 작업 중 외부사실 의존 known-unknown 으로 막혔을 때, 아래 형식으로 조사 요청을 올린다 (lane 은 요청만 — 실행 금지).

```
조사 요청: <lane>/<작업-anchor>          # 예: 설계/CFP-NNNN-§3
질문: <단일·평문 질문 1개>               # 다중 질문 금지 — scope 명확성 (게이트 규칙 ①)
얕은조사 불가 사유: <왜 단계②(얕은 자가조사)로 안 되는지 1~2줄>
외부사실 의존 지점: <결론이 어떤 외부지식의 진위에 좌우되는지>
```

- **단일 질문 의무** — 한 요청 = 한 질문. 묶음 질문은 scope 가 흐려져 게이트 ① 에서 반려된다.
- **얕은조사 불가 사유 의무** — 단계②(그 lane 의 자기 도구로 결정-범위 얕게 확인)로 닫히지 않는 이유를 명시. 이 사유가 부실하면 게이트 ② shallow-vs-deep 문턱에서 반려된다.
- **외부사실 의존 게이트 상속 (ADR-124 §결정 2)**: 질문이 외부지식(산업 표준·RFC·벤더 동작·CVE 등)의 진위에 의존해야 한다. 내부 코드·내부 규칙·팀 암묵지식만으로 닫히는 결론(ADR-124 §결정 6 "의존 X" row)에 deep-research 를 요청하면 **검사연극** → 반려 (theater_check 절).

---

## 2. Orchestrator 게이트 3-규칙 (`gate`)

Orchestrator = **문지기**(scope 심사 + 반려 판정)다. **조사 주제 기획자가 아니다** — demand 출처는 lane 이고, Orchestrator 는 요청의 적격성만 심사한다.

| 규칙 | 심사 | 반려 조건 |
|---|---|---|
| ① scope 명확성 | 단일·평문 질문인가, anchor·외부사실 의존 지점이 특정되는가 | 묶음 질문 / 모호한 범위 / anchor 부재 → 반려 |
| ② shallow-vs-deep 문턱 | 얕은 자가조사(단계②)로 처리될 일이 아닌가 | "얕은 셀프서비스로 충분" → 반려 |
| ③ 흐린 요청 반려 | ①② 충족하나 질문 자체가 흐린가 | 구체화 요구 후 재요청 |

**반려 사유 형식** (lane 에 되돌려보낼 때):

```
반려: <lane>/<작업-anchor> 조사 요청
사유: <규칙 ①|②|③ 중 위반 규칙 + 1줄 설명>
재요청 안내: <단일 질문으로 좁히기 | 얕은 자가조사(단계②)로 처리 | 외부사실 의존 지점 명시>
```

- 게이트 ② 반려 = "얕은 셀프서비스로 처리하라" 통보 (단계② 로 routing). 게이트 ①③ 반려 = lane 이 요청을 재구성해 다시 올림.
- 반려는 거버넌스 결손이 아니라 게이트의 정상 동작이다 — on-demand 게이트 자체가 검사연극 차단 장치다(theater_check 절).

---

## 3. 외부사실 의존 게이트 + 검사연극 금지 (`theater_check`)

게이트 3-규칙 통과 후에도, **결론이 외부사실에 의존하는 지점인지** 를 최종 확인한다 (ADR-124 §결정 2 외부사실 의존 게이트를 본 on-demand 경로에 상속).

- **외부사실 의존 판정 휴리스틱** (ADR-124 §결정 6, 인용 — 복붙 금지):
  - 의존 O (단계③ 적용): 팩트체크 / 벤더 동작 / 표준(RFC 등) / CVE·취약점 사실.
  - 의존 X (단계③ 미적용): 팀 암묵지식 / 내부 코드·규칙 사실 (repo·내부 축).
  - 경계(?): 시장정보 / 벤치마크 / StackOverflow 등 준-외부 출처 → ADR-125 §결정 6 운영 판정(단계② 우선, 리뷰어 재량 escalation)을 따른다.
- **검사연극(verification theater) 금지** — 내부근거-only 결론에 deep-research 를 강제하면 검사연극이다. SSOT = ADR-124 §결정 2 + ADR-119 §결정 6 "'조사했으므로 옳다' 단정 금지" (조사 = traceability + 정직성 수단이지 결론의 정당성 보증 아님). 본 절은 그 두 SSOT 를 **cross-ref** 하며 문구를 복붙하지 않는다(drift 회피).
- **code lane 웹금지 우회 차단 (ADR-124 Amendment 1 A1-3, [P0])** — 요청 lane 이 code(구현리뷰)면, deep 조사 결과를 주입해도 **code 리뷰 결론은 내부 코드 사실 축으로 닫힌다**. on-demand 가 code lane 의 web 전면금지(web 허용 lane = security + requirements-review + design 좁은 예외 3 종)를 깨는 우회로가 되어서는 안 된다 — code lane 의 작업중 막힘이 외부지식 의존이 아닌데 deep 조사를 끼워 넣으면 검사연극 + 대칭 붕괴다. (S3 차등 ↔ S5 on-demand 는 axis 가 다르다: S3 = 적용 깊이 차등 / S5 = 호출 경로 pull.)
- **abstention escape** — deep-research 가 출처를 확보하지 못하면 ADR-119 §결정 3.2 "확인 불가 / 추정" 명시 후 진행 (데드락 회피, ADR-124 §결정 6 상속).

---

## 4. deep-research 실행 (`execute`)

게이트 통과 시, Orchestrator 가 harness-native **deep-research** skill 을 호출한다 (Orchestrator 전용).

- **방법론 = harness 제공** — deep-research(다출처 web 조사 + adversarial 검증 + 출처 인용)는 Claude Code harness 가 제공하는 system skill 이다. 본 skill 은 방법론을 **재정의하지 않는다** — 호출 경로·게이트만 신설한다. lane별 차등 instantiate(보안테스트 web 단계 심화 / 설계리뷰 좁은 예외 / code lane web 금지 보존)는 S3(ADR-124 Amendment 1)가 이미 완료했다 (cross-ref only).
- **S3 차등 방법론과 정합** — 외부사실 의존 + 다출처 교차 + adversarial verify + 시의성(recency). on-demand 도 이 4 요소를 따른다 (ADR-124 Amendment 1 A1-1).
- **ADR-039 §결정 2 정합 (1줄 명문, AC-7)**: deep-research Skill 호출은 ADR-039 §결정 2 inline whitelist 에 **신규 entry 를 추가하지 않는다 (whitelist axis 비해당).** rate-limit-429-mitigation skill 선례(ADR-039 Amendment 4)와 동형 — **skill body 가 operational primitive 를 보유하되 inline whitelist 는 무손상.** Skill 호출 자체는 file/GitHub mutation 미발화 → §결정 1 "수정 작업" closed enum 비해당 → whitelist axis 와 disjoint. 상세 SSOT = ADR-126 §결정 2/3.

### 4.1 2차 출처 = Codex/GPT-5 독립 의견 (ADR-126 Amendment 1)

execute 는 1차 web 조사(harness-native deep-research)와 **별개로** Codex/GPT-5 에 독립 2차 의견을 수집해 corroboration(교차 일치/분기) 신호를 확보한다.

- **2차 출처 = Codex/GPT-5 독립 의견**: §3 theater_check 를 통과한 외부사실 의존 질문에 대해, harness-native deep-research(1차, web·해석자 Claude)와 **별개로** Codex/GPT-5 에 **의미-동등(semantic-equivalent) 질문**을 던져 독립 2차 의견을 수집한다. byte-verbatim 아님 — ADR-081 dispatch boilerplate(3 mandatory section + file-redirect)에 맞춘 prompt 재구성이 불가피하되 **질문 의미 보존 의무** (의미 drift 시 corroboration 비교 무효).
- **caller = Orchestrator 전용 (재귀가드)**: Codex 2차 출처 dispatch 는 `execute` 수행 주체인 **Orchestrator top-level inline 행위**다. **sub-agent(lane) 가 Codex 를 직접 호출 금지** — deep-research skill 호출 + codex:codex-rescue subagent spawn 둘 다 Orchestrator 행위(ADR-039 §결정 1, lane 자가-spawn 0). 신규 whitelist entry 0, 새 dispatch mechanism 0 (ADR-126 §결정 2/3 자체 재논증 재사용).
- **Codex dispatch 규약 상속 (AC-8)**: codex:codex-rescue + file-redirect dispatch(ADR-081 §D8) + network_scope declare(web 필요 시 web-fetch, 아니면 offline) + read-only(--write 미부착). 새 Codex 호출 경로 발명 0.
- **시점성 위계 = 발동 후 source-weighting (새 게이트 아님, A1-3)**: 아래는 execute 발동(theater_check 통과) *이후* 의 source-weighting 규칙이다 — "이 질문이 시간민감인가?" 를 매 조사 의무 체크박스화하면 검사연극(금지). 변동성(volatility) spectrum:
  - 변동성 **높음** (버전 번호·CVE·최신 API·가격·릴리스 일자 — cutoff 이후 빠르게 노후): **WebSearch = ground-truth anchor / Codex = 보조**. training-bound Codex 가 live-retrieval WebSearch 를 뒤집지 못한다.
  - 변동성 **낮음** (수학·안정 알고리즘·확립 표준(RFC)·이론·패턴): **동등 교차** (Codex training-bound 로도 valid).
  - 경계(예: "현재 best practice"): 시간민감으로 **보수 분류**.
  - **cutoff 날짜 하드코딩 금지** — "training-bound 모델은 cutoff 이후 변동성 높은 사실에 취약" 이라는 **방향성 부등식** 만 사용. 특정 날짜 값 박제 금지(모델 swap drift — cutoff 추적은 codex@openai-codex / OpenAI vendor OWNING, codeforge 는 USING 경계). 방향성: GPT-5 계열 cutoff < Claude 계열 cutoff [source: OpenAI dev docs / Story §6.3 — 날짜 값 박제 금지, 방향성만].
  - 판정 주체 = Orchestrator(execute 수행자).
- **Q-1 확정 (시간민감 + Codex web 불가)**: 변동성 높은 사실에서 Codex 가 web 못 하면 **Codex 교차 생략 + single-source** (stale training-bound 교차 = noise). 변동성 낮은 사실은 Codex training-bound 로도 교차 valid → 시점성 위계가 codex sandbox web 미지수(OWNING)를 자연 흡수(graceful degradation).
- **declarative-only 상속 (A1-4)**: Codex 2차 출처는 on-demand 발동 시에만 붙는다(매 Story/매 조사 강제 아님). 상시 강제화 = Codex API 한도 압박 + declarative-only 위배.

---

## 5. cited 결과 주입 (`inject`)

deep-research 의 cited 결과를 **요청 lane 의 재spawn prompt packet block** 으로 주입한다 (요청 lane 이 막힌 지점에서 결과를 받아 작업 재개).

```
[research-injection] 요청=<lane>/<작업-anchor>
  질문: <원 질문 1줄>
  결과(요약): <cited 결론 — 각 단정에 출처 병기>
  출처: <URL | 표준 번호 | 벤더 문서명 ...>
  corroboration: <corroborated | divergent | single-source> + 상태별 부가
  abstention: <출처 확보 불가 시 "확인 불가/추정" 명시 — 없으면 생략>
```

- **재주입 = 기존 packet-injection 동형** — cited 결과 packet 은 기존 FIX 재spawn + `pr_phase` packet 주입과 **동형**이다 (신규 주입 채널 발명 금지). 요청 lane 을 재spawn 하며 prompt packet 에 위 block 을 확장 주입한다.
- **각 단정에 출처 병기 (ADR-119)** — 주입되는 결과의 substantive 단정에는 `source: <URL|표준 번호|문서명>` 병기 의무. 출처 부재 시 "확인 불가 / 추정" 명시 (abstention escape).

### 5.1 corroboration 3-분류 (ADR-126 Amendment 1)

`corroboration:` 필드는 1차 출처(deep-research)와 2차 출처(Codex/GPT-5)의 교차 결과를 아래 3-상태로 분류한다.

| corroboration 상태 | 정의 | inject 처리 |
|---|---|---|
| `corroborated` | 양 출처(deep-research·Codex) 동일 결론 | 결론 + **"일치는 반증 부재이지 진리 증명 아님(공유 코퍼스 상관오류 가능)" 경고 의무 병기**. `corroborated` ≠ `[verified]` 무검증 승격 금지 |
| `divergent` | 둘 다 단정하나 상이 | 분기 **verbatim 병기** + 임의 채택 금지(다수결≠진리). 시점성 위계 tie-break, 미결 시 abstention |
| `single-source` (`secondary_unavailable`) | 한쪽만 응답(Codex 미가용/sandbox-block/web 불가) | deep-research 단독 결론 + `single-source` 표기. on-demand 실패 아님 — graceful degradation(ADR-070 `fallback_skip_with_marker` 정합) |

- **divergent ≠ abstention 구분 의무 (AC-3)**: divergent = 두 출처가 둘 다 단정하나 충돌 / abstention = 출처 부재("확인 불가/추정", ADR-119 §결정 3.2). 불일치를 전부 abstention 처리하거나 그 반대 = 오류.
- **divergence 최종 미결 = abstention 으로 닫음 (A1-4, Q-2)**: divergent 가 시점성 위계 tie-break 후에도 어느 쪽도 명백히 우세하지 않으면 abstention 으로 닫는다. **자동 추가조사(deep-research 재실행) 강제 안 함** (비용·latency·무한루프 리스크). 임의 채택 금지.
- **correlated error 경고 (false-corroboration)**: 두 LLM 이 공유 웹 코퍼스로 학습돼 둘 다 틀려도 일치할 수 있다(false-corroboration) [source: arXiv:2506.07962 ICML'25 / Story §6.1]. 그래서 `corroborated` 는 verify 대체가 아니다 (§5.2).

### 5.2 corroboration ↔ verify disjoint layer [P0 load-bearing] (ADR-126 Amendment 1 A1-2)

corroboration 은 trust 신호일 뿐 verify(반증 시도)의 자리가 아니다. 사실 축별로 verify 채널과 corroboration 의 자리가 갈린다.

| 사실 축 | verify 채널 | corroboration 의 자리 |
|---|---|---|
| repo 파일 사실 (Codex finding evidence: file content / ADR §결정 번호 / commit SHA) | ADR-070 file-Read-verify (Orchestrator own working dir Read/Grep) — **무변경, 본 경로 비대상** | — |
| 외부 web 사실 (표준·벤더 동작·CVE·이론) | ADR-119 출처 인용(§결정 1) + abstention(§결정 3.2). file-Read-verify **구조적 적용 불가 → 면제** | **보조 trust 신호**(corroborated/divergent/single-source) — verify 아님 |

**corroboration 은 verify 대체 아님(correlated error 로 false-corroboration 리스크). `corroborated` ≠ `[verified]` 무검증 승격 금지.** repo 파일 사실 verify 는 ADR-070 file-Read-verify 무변경 (cross-ref only, 본문 무변경).

### 5.3 #2166 disjoint cross-ref (ADR-126 Amendment 1 A1-5)

- #2166 = source-annotation **presence** lint(enforcement 축, "달았나"). 본 corroboration = **agreement 축**("맞나"). presence ≠ agreement → **disjoint**. #2166 **close 금지** (전 lane presence lint 라 더 넓음). 흡수 관계 = on-demand inject 가 `source:`/`abstention:` 병기로 #2166 presence 의무를 on-demand 경로에 한정 선제충족함을 cross-ref(mechanical lint 신설 0). #2166 URL = https://github.com/mclayer/plugin-codeforge/issues/2166

### mechanism 이중 경로 (env=1 / env=0 동등)

요청·주입 mechanism 은 team-mode 활성 여부에 따라 두 경로가 **동등 보장**된다 (playbook env=0/env=1 동등성 — registry §6.4 / playbook §3.6 답습, 신규 분기 발명 금지).

| env | `request` | `inject` |
|---|---|---|
| env=1 (team-mode, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) | lane teammate → Orchestrator(Lead) **SendMessage** 로 조사 요청 | Orchestrator → lane teammate SendMessage 또는 재spawn packet 주입 |
| env=0 (default subagent context, ADR-039) | lane subagent **return verdict** 에 조사 요청 표기 → Orchestrator 게이트 심사 (round-trip) | 게이트 통과 → deep-research 실행 → 요청 lane **재spawn** with packet 주입 (round-trip polyfill) |

- 두 경로는 **동등** — env=0 round-trip 은 env=1 SendMessage 의 polyfill 이며, 신규 분기를 발명하지 않는다. env=0 는 lane 막힘당 최소 1 추가 round-trip(latency/token 정성 trade-off — 토큰 효율보다 정확성 우선, ADR-035 §컨텍스트 정합).

---

## Cross-references

- [ADR-126](../../archive/adr/ADR-126-on-demand-research-request-gate.md) — 본 skill body 정책 SSOT (§결정 1-6: on-demand mechanism + ADR-039 정합 자체 재논증 + whitelist 무신설 + code lane web 금지 보존 + review-time disjoint + 검사연극 금지 상속) / **Amendment 1 (CFP-2459) — execute 2차 출처(Codex/GPT-5 의미-동등) + corroboration 3-분류 + corroboration↔verify disjoint**
- [ADR-124](../../archive/adr/ADR-124-external-knowledge-provisioning-model.md) — 외부지식 충당 3-단계 모델 (§결정 1 단계③ "리뷰 게이트(주) + on-demand(후순위)" / §결정 2 외부사실 의존 게이트 + 검사연극 금지 / §결정 6 외부사실 의존 휴리스틱 / Amendment 1 A1-3 code lane web 금지 [P0])
- [ADR-125](../../archive/adr/ADR-125-requirements-review-lane.md) — 요구사항리뷰 lane (§결정 6 on-demand(S5) ↔ review-time disjoint SSOT)
- [ADR-039](../../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — spawn = Orchestrator 전용(§결정 1) + closed inline whitelist(§결정 2, L145) + 회피 대안 C(lane 자가-spawn 불가) + Amendment 4(skill body primitive ↔ whitelist 무손상 선례)
- [ADR-119](../../archive/adr/ADR-119-research-before-claims.md) — §결정 1 외부 web 사실 출처 인용(verify 자리 대체) / §결정 3.2 abstention escape / §결정 6 검사연극 금지 SSOT
- [ADR-070](../../archive/adr/ADR-070-codex-verify-before-trust.md) — repo 파일 사실 verify 채널(file-Read-verify, 외부 web 사실은 구조적 적용 불가 → 면제 disjoint) + `fallback_skip_with_marker`(single-source graceful degradation 정합). cross-ref only — 본 경로 비대상(무변경)
- [ADR-081](../../archive/adr/ADR-081-codex-worker-prompt-boilerplate.md) — Codex 2차 출처 dispatch 규약 재사용(codex:codex-rescue + §D8 file-redirect + network_scope web-fetch enum declare + read-only). 신규 권한·새 dispatch mechanism 0
- [ADR-109](../../archive/adr/ADR-109-in-process-429-mitigation-framework.md) / `skills/rate-limit-429-mitigation/SKILL.md` — skill body 가 primitive 보유하되 whitelist 무손상 binding precedent (Amendment 4 경유)
- [#2166](https://github.com/mclayer/plugin-codeforge/issues/2166) — source-annotation presence lint(enforcement 축 "달았나"). corroboration = agreement 축("맞나") → disjoint. close 금지(전 lane presence lint 라 더 넓음)
- `skills/jira-decision-channel/SKILL.md` / `skills/review-responsibility/SKILL.md` — 추상 단계 표 + caller scope Orchestrator 한정 / 참조 테이블 형식 선례
