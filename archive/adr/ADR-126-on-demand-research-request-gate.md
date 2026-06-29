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
  - CFP-2459  # Amendment 1 carrier — execute 단계 Codex 2차 출처 source-diversification + corroboration↔verify 경계 + 시점성 위계 + divergence abstention (Epic CFP-2457 Story C)
related_adrs:
  - ADR-039  # §결정 1·2 — spawn=Orchestrator 전용 binary always-spawn + closed inline whitelist (cardinality 비고정). 본 ADR 이 §결정 1/2 정합을 자체 재논증 (ADR-124 §결정 4 disjoint 논리는 lane 개수 axis 한정이라 차용 불가). Amendment 4 = skill body primitive ↔ whitelist 무손상 선례
  - ADR-124  # §결정 1 단계③ "리뷰 게이트(주) + on-demand(후순위)" / §결정 2 외부사실 의존 게이트 + 검사연극 금지 / §결정 5 "on-demand 깊은 검증 경로 = S5" 위임 / §결정 6 외부사실 의존 휴리스틱 / Amendment 1 A1-3 code lane web 금지 [P0]
  - ADR-125  # §결정 6 — on-demand(S5) ↔ review-time(S2/S3) disjoint SSOT. §결정 4 ADR-052 cross-ref(Amendment 격상 불요) 처리 선례 = 본 ADR 형식 판정 모델
  - ADR-109  # in-process 429 mitigation framework — skill body 가 operational primitive 보유하되 whitelist 무손상 (Amendment 4 경유 binding precedent)
  - ADR-046  # Amendment 2 — Researcher 재초점. 하류 기술수요 = review-time deep(S3) + on-demand(S5) 담당. 본 ADR = 그 하류 기술수요의 작업중 pull 채널
  - ADR-058  # §결정 5 — 약화 evidence-gate. 본 ADR = additive skill 신설 + cross-ref only, strengthen 방향 → sunset_justification null
  - ADR-119  # §결정 6 검사연극 금지 SSOT / §결정 3.2 abstention escape
  - ADR-037  # plugin version bump rule — 신규 skill = skills/ 자동 발견, marketplace 4필드 무영향, CLAUDE.md 레인 진입 표 미등재 → bump 불요
  - ADR-070  # Amendment 1 — verify-before-trust 적용 대상 = repo 파일 사실 한정 (Codex external worker output). 외부 web 사실 = file-Read-verify 구조적 미커버 → Amendment 1 이 disjoint layer 명시 (cross-ref only, ADR-070 본문 무변경). D1 scope = proactive 6 touchpoint + reactive, on-demand research path 는 ADR-126 owns
  - ADR-081  # Amendment 1 — Codex worker dispatch boilerplate (network_scope: web-fetch enum 이미 정의, CFP-963 Amendment 4 — 신규 권한 0) + file-redirect dispatch (D8) + substitution 3-enum 상속. on-demand 2차 출처 Codex dispatch 가 기존 규약 재사용
amendments:
  - Amendment 1  # CFP-2459 (Epic CFP-2457 Story C) — execute 단계 Codex 2차 출처 source-diversification + corroboration↔verify disjoint layer 경계 + 시점성 위계 (변동성 spectrum) + divergence abstention + #2166 disjoint cross-ref
related_files:
  - archive/adr/ADR-126-on-demand-research-request-gate.md
  - skills/research-request-gate/SKILL.md  # 본 ADR 정책의 운영 절차 carrier (Amendment 1 execute/inject 절 확장 = Phase 2)
  - skills/jira-decision-channel/SKILL.md  # caller scope Orchestrator 한정 선례
  - skills/rate-limit-429-mitigation/SKILL.md  # skill body primitive ↔ whitelist 무손상 선례
  - CLAUDE.md  # 결정·대화 원칙 절 1줄 cross-ref (레인 진입 표 미등재 — on-demand 는 lane 진입 아닌 작업중 mechanism)
amendment_log:
  - amendment: Amendment 1
    date: 2026-06-29
    carrier_story: CFP-2459
    parent_epic: "mclayer/plugin-codeforge#2457"
    summary: |
      execute 단계 내부의 source-diversification — harness-native deep-research(web, N=1) 에 Codex/GPT-5 독립 2차 출처를 더해 N=2 로 확장. 새 단계 0 (request→gate→execute→inject 4단계 골격 무변경), 새 권한 0 (Codex dispatch = ADR-081 web-fetch enum + file-redirect + substitution 3-enum 재사용, spawn = Orchestrator 전용 ADR-039 정합). 4 결정:
      ① execute 2차 출처 + corroboration 상태 3-분류 (corroborated / divergent / single-source) inject 주입 — divergent ≠ abstention 구분.
      ② corroboration ↔ verify disjoint layer 경계 [P0 load-bearing] — ADR-070 verify-before-trust 적용 대상 = repo 파일 사실 한정, 외부 web 사실은 file-Read-verify 구조적 미커버 → corroboration 은 verify *대체 아님* (correlated error 로 false-corroboration 리스크), 외부 web 사실 = ADR-119 출처 인용 + abstention 이 verify 자리 대체 + corroboration = 보조 trust 신호. corroborated 에 "일치는 반증 부재이지 진리 증명 아님" 경고 의무. ADR-070 cross-ref only (본문 무변경).
      ③ 시점성 위계 = 발동 후 source-weighting (새 게이트 아님) — 변동성 높음(버전·CVE·최신 API·가격)=WebSearch ground-truth-anchor·Codex 보조 / 변동성 낮음(수학·알고리즘·안정 표준·이론)=동등 교차. cutoff 날짜 하드코딩 금지 (방향성 부등식만). ADR-124 §결정 6 휴리스틱에 시점성 축 좁게 instantiate.
      ④ divergence 끝까지 미결 시 abstention 으로 닫음 (다수결≠진리, 자동 추가조사 강제 안 함) + #2166 (source-annotation presence lint, enforcement 축) disjoint cross-ref (close 아님).
    direction: strengthen  # execute 단계 출처 다양화 = 검증 capability 추가 (약화 0). 4단계 골격·권한·whitelist 무손상. ADR-070/124/081/039 무변경. ADR-058 §결정 5 약화 차단 정합.
    sunset_justification: null  # strengthen 방향 — execute 내부 source 확장 + disjoint layer 명시, 기존 결정 instantiate. is_transitional: false 유지.
---

# ADR-126: on-demand 깊은 조사 보충 경로 — research-request-gate 거버넌스

## Amendment 1 (CFP-2459, Epic CFP-2457 Story C) — execute 단계 Codex 2차 출처 + corroboration↔verify disjoint layer

> **새 단계 0 / 새 권한 0.** 본 amendment 는 §결정 1 의 on-demand 4단계(request → gate → execute → inject) 중 **`execute` 단계 *내부*의 source-diversification** 이다. `execute` 가 호출하는 harness-native deep-research(web, 해석자=Claude, N=1)에 **Codex/GPT-5 독립 2차 출처**를 더해 N=2 로 확장한다. 4단계 골격은 무변경(5번째 단계 신설 아님), Codex dispatch 권한은 기존 자산 재사용(ADR-081 `network_scope: web-fetch` enum + file-redirect dispatch §D8 + substitution 3-enum, 신규 권한 0), spawn 은 Orchestrator 전용(ADR-039 §결정 1 정합 — lane 자가-spawn 0). 방향은 **강화(strengthen)** — execute 단계의 검증 capability 를 늘리며 어느 기존 결정도 약화하지 않는다(ADR-070/124/081/039 무변경, A1-5).

> **carrier 형식 판정 (ArchitectPL §3 결정)**: 본 변경 = ADR-126 Amendment (신규 ADR 아님). §결정 1 의 on-demand mechanism 골격(4단계)을 바꾸지 않고 `execute` 서술만 확장하므로, ADR-126 **회피된 대안 B**("새 mechanism = 신규 ADR / instantiate = Amendment")의 *instantiate* 쪽에 해당한다. ADR-070 의 verify 경계 충돌은 **본 Amendment 가 disjoint layer 로 명시 + ADR-070 cross-ref**(ADR-070 본문 무변경)로 닫는다 — ADR-070 9번째 Amendment 신설은 회피(아래 A1-2 rationale). 결과 = touch ADR **1 개**(ADR-126), ADR-070/124/081 = cross-ref only. (사용자 "독립·경량" 선언 정합.)

### A1-1 — `execute` 단계 2차 출처 + corroboration 3-분류 inject

`execute` 단계는 외부사실 의존 질문(§결정 6 게이트 통과)에 대해, harness-native deep-research(1차, web·Claude)와 **별개로** Codex/GPT-5 에 **의미-동등 질문**을 던져 독립 2차 의견을 수집한다. 두 출처를 분류해 `inject` block 에 명시한다.

| corroboration 상태 | 정의 | inject 처리 |
|---|---|---|
| `corroborated` | 양 출처가 동일 결론 | 결론 + **"일치는 반증 부재이지 진리 증명 아님(공유 코퍼스 상관오류 가능)" 경고 의무 병기**(A1-2) |
| `divergent` | 둘 다 단정하나 상이 | 분기 verbatim 병기 + 임의 채택 금지(다수결≠진리). 시점성 위계(A1-3) tie-break, 미결 시 abstention(A1-4) |
| `single-source` (`secondary_unavailable`) | 한쪽만 응답 (Codex 미가용/sandbox-block/web 불가) | deep-research 단독 결론 + `single-source` 표기. on-demand 실패 아님 — graceful degradation(ADR-070 `fallback_skip_with_marker` 정합) |

- **divergent ≠ abstention 구분 의무**: `divergent` = 두 출처가 둘 다 단정하나 충돌 / `abstention` = 출처 부재("확인 불가/추정", ADR-119 §결정 3.2). 불일치를 전부 abstention 처리하거나 그 반대 = 오류.
- **의미-동등(semantic-equivalent) 질문**: byte-verbatim 아님 — Codex dispatch boilerplate(ADR-081 3 mandatory section + file-redirect)에 맞춘 prompt 재구성이 불가피하되 질문 *의미* 보존 의무. 의미 drift 시 corroboration 비교 무효.
- **caller = Orchestrator 전용**: Codex 2차 출처 dispatch 도 `execute` 수행 주체인 Orchestrator inline(ADR-039 §결정 1, lane 자가-spawn 금지). deep-research skill 호출 + codex:codex-rescue subagent spawn 둘 다 Orchestrator 행위 → §결정 2/3 자체 재논증 그대로 재사용(신규 whitelist entry 0, 새 dispatch mechanism 0).

### A1-2 — corroboration ↔ verify-before-trust disjoint layer [P0 load-bearing]

본 Amendment 의 핵심. **corroboration 은 ADR-070 file-Read-verify 의 대체가 아니다.**

- **ADR-070 의 verify 적용 대상 = repo 파일 사실 한정**: ADR-070 §결정 D1 의 verify-before-trust 는 "Codex finding evidence 의 factual ground truth = repo 내부 파일 사실(file content / ADR §결정 번호 / commit SHA)" 을 Orchestrator own working directory Read/Grep 로 확정하는 layer 다. **외부 web 사실(표준·벤더 동작·CVE)은 repo 밖이라 file Read verify 가 구조적으로 불가** — ADR-070 을 web 영역에 "그대로 상속"이라 쓰면 작동하지 않는 규약 = 검사연극.
- **correlated error 로 corroboration ≠ verify**: 두 출처(Claude·GPT-5)가 같은 web 오정보를 공유하면 둘 다 틀려도 `corroborated` 판정되는 **false-corroboration 리스크**가 실재한다(공유 공개 웹 코퍼스 → 부분 상관오류). 따라서 corroboration 은 진리 보증이 아니라 **"독립 분포가 동일 결론을 통과"의 보조 trust 신호**일 뿐이다. `corroborated` 를 `[verified]` 로 무검증 승격 금지.
- **외부 web 사실의 verify 자리 대체 채널**: 외부 web 사실은 ADR-070 file-Read-verify 를 **적용 면제**하고, 그 자리를 **ADR-119 출처 인용(§결정 1 "외부 지식 주장" row) + abstention(§결정 3.2)** 이 대체한다. corroboration(`corroborated`/`divergent`/`single-source`)은 이 위에 얹는 **보조** 신호다.
- **disjoint layer 매핑 (명시)**:

  | 사실 축 | verify 채널 | 본 Amendment 의 자리 |
  |---|---|---|
  | repo 파일 사실 (Codex finding evidence 등) | ADR-070 file-Read-verify (Orchestrator own dir Read/Grep) | 무변경 — 본 Amendment 비대상 |
  | 외부 web 사실 (표준·벤더·CVE) | ADR-119 출처 인용 + abstention (file-Read-verify 면제) | corroboration = **보조 trust 신호**(verify 아님) |

- **ADR-070 cross-ref only (본문 무변경)**: 본 Amendment 가 외부 web 사실 = ADR-070 적용 면제 disjoint layer 임을 **ADR-126 안에서 선언 + ADR-070 cross-ref** 한다. ADR-070 본문은 손대지 않는다(D1-D6 의미 변경 0). rationale = (i) 본 경계는 on-demand `execute` 경로의 성격(외부 web 사실 조사)이라 ADR-126 owns / (ii) ADR-070 D1 scope 는 명시적으로 "proactive 6 touchpoint + reactive" 채널이고 on-demand research path 는 그 enumeration 밖 새 context / (iii) touch ADR 1 개 유지(경량). **거절된 더 무거운 대안** = ADR-070 9번째 Amendment 신설(외부 web 사실 row 를 ADR-070 D1 scope 표에 추가) — ADR-070 D6.3 scope ratchet-up 선례상 가능하나, on-demand `execute` 의 web-fact verify 면제는 ADR-070 의 "Codex worker output 신뢰성" axis 가 아니라 ADR-126 의 "외부지식 조사 경로" axis 라 ADR-126 carrier 가 정합. (DesignReview 가 P0 로 이 경계 판정 재검 권장.)

### A1-3 — 시점성 위계 = 발동 후 source-weighting (새 게이트 아님)

시점성 위계는 **on-demand 발동(§결정 6 외부사실 의존 게이트 통과) *이후* 의 source-weighting 규칙**이다. 새 발동 게이트가 아니다 — "이 질문이 시간민감인가?" 를 매 조사 의무 체크박스로 만들면 검사연극이다.

- **변동성(volatility) spectrum** (이분법보다 정확):
  - 변동성 **높음** (버전 번호·CVE·최신 API·가격·릴리스 일자 — cutoff 이후 빠르게 노후): **WebSearch = ground-truth anchor / Codex = 보조**. Codex(training-bound)가 primary WebSearch(live retrieval) 를 뒤집지 못함.
  - 변동성 **낮음** (수학·안정 알고리즘·확립 표준(RFC)·이론·패턴): **동등 교차** (Codex training-bound 로도 valid).
  - 경계(예: "현재 best practice"): 시간민감으로 **보수 분류**.
- **cutoff 날짜 하드코딩 금지**: "training-bound 모델은 cutoff 이후 변동성 높은 사실에 취약" 이라는 **방향성 부등식**만 규약에 사용. 특정 cutoff 날짜 값을 박제하면 모델 swap 마다 drift(cutoff 추적 = codex@openai-codex / OpenAI vendor OWNING 도메인, codeforge 는 날짜 추적 불요 — USING 경계).
- **판정 주체 = Orchestrator**(execute 수행자). ADR-124 §결정 6 휴리스틱(의존 O/X/경계?)에 **시점성 축을 좁게 instantiate**(ADR-124 Amendment 1 A1-1 의 "시의성(recency)" 이 이미 단계③ 방법론에 존재 — 본 Amendment 는 그 recency 를 source-weighting 으로 명료화, 신규 규범 아님).
- **graceful degradation 정합**: Codex 가 web 못 하면 변동성 높은 사실은 당연히 WebSearch 단독 + `single-source` 표기(A1-1), 변동성 낮은 사실은 Codex training-bound 로도 교차 valid — 시점성 위계가 codex sandbox web 미지수(OWNING)를 자연 흡수한다.

### A1-4 — divergence 최종 미결 = abstention 으로 닫음

`divergent` 가 시점성 위계(A1-3) tie-break 후에도 어느 쪽도 명백히 우세하지 않으면 **abstention("확인 불가/추정", ADR-119 §결정 3.2)으로 닫는다.**

- **자동 추가조사 강제 안 함** — divergent 미결 시 deep-research 자동 재실행 루프를 강제하지 않는다(비용·latency·무한루프 리스크). 정직한 abstention 이 다수결(≠진리) 자동 채택보다 낫다.
- **임의 채택 금지** — divergent 를 임의로 한쪽 채택하면 다수결≠진리 위배. 분기 verbatim 병기 후 미결이면 닫는다.
- **declarative-only 상속**: Codex 2차 출처는 on-demand 발동 시에만 붙는다(매 Story/매 조사 강제 아님, §결정 6 declarative-only). 상시 강제화 = Codex API 한도 압박 + declarative-only 위배.

### A1-5 — #2166 disjoint cross-ref + 약화 0 (ADR-058 §결정 5)

- **#2166 = disjoint axis (흡수분 0, close 아님)**: [#2166](https://github.com/mclayer/plugin-codeforge/issues/2166) = research-before-claims **mechanical lint promotion**(`source:` annotation **presence** 검사 — "출처를 *달았는가*" 정적 enforcement 축, ADR-060 4-tier path, OPEN). 본 Amendment = **corroboration 축**("두 출처가 *일치하는가*" 런타임 교차). presence(있나) ≠ agreement(맞나) → disjoint. **#2166 close 금지**(전 lane presence lint 라 본 Amendment 의 on-demand inject 보다 넓음). 흡수 = on-demand `inject` 가 이미 `source:`/`abstention:` 병기로 #2166 의 presence 의무를 *on-demand 경로에 한정해* 선제 충족함을 #2166 에 cross-ref(mechanical lint 신설 아님).
- **약화 0건 (strengthen)**: `execute` 단계 source 확장(N=1→N=2) + disjoint layer 명시 = 검증 capability 추가. on-demand 4단계 골격·spawn 독점(ADR-039)·inline whitelist·ADR-070 verify 채널·ADR-124 단계③ 방법론·ADR-081 dispatch enum 모두 무변경. ADR-058 §결정 5 약화 차단 정합 → `sunset_justification: null`, `is_transitional: false` 유지.

### A1-6 — bump / mechanical_enforcement

- **plugin.json bump 불요**: 기존 skill 본문 수정(research-request-gate SKILL.md execute/inject 절 확장 = Phase 2) + ADR Amendment — 신규 skill 0, marketplace 4필드 무영향, CLAUDE.md 레인 진입 표 미등재(ADR-037 정합, §결정 ADR-126 결과 절 답습).
- **mechanical_enforcement_actions: [] (declaration-only)**: corroboration 동작은 prose 규약(ADR-126 선례 동형). 정량 KPI/일치율 측정 lint = OOS(후속). pattern_count ≥ 2 재발 시 follow-up CFP MUST promote(ADR-084 precedent).

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
| ADR-039 §결정 1·2 | spawn = Orchestrator 전용 + closed inline whitelist | 새 mechanism(요청→게이트→주입)이 §결정 1/2 와 정합하는지 *자체 논증* 부재 (ADR-124 §결정 4 disjoint 논리는 lane 개수 axis 한정이라 차용 불가) |

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

③ **따라서 §결정 1 binary always-spawn 무손상 + §결정 2 inline whitelist 무손상 (신규 entry 추가 0 — whitelist axis 비해당).**
①에 의해 §결정 1 spawn 독점이 보존되고(lane 자가-spawn 0, 실행은 Orchestrator), ②에 의해 §결정 2 inline whitelist 가 무손상이다(Skill 호출은 수정 작업 아니라 whitelist axis 비해당 — 신규 entry 추가 0). on-demand mechanism 은 ADR-039 의 두 invariant 어느 것도 약화·확장하지 않는다.

**(c) 결론** — ADR-039 §결정 1/2 는 본 ADR 의 새 mechanism 에 의해 **0 변경**이다. 이 정합은 ADR-124 §결정 4 의 lane-개수-axis disjoint 논리를 차용한 것이 아니라, 위 ①②③ 의 독립 논거로 자체 재논증된 것이다.

### 결정 3 — deep-research 호출 = whitelist 신규 entry 추가 0 (rate-limit Amendment 4 선례 동형)

Orchestrator 의 deep-research Skill 호출은 ADR-039 §결정 2 inline whitelist 에 **신규 entry 를 추가하지 않는다 (whitelist axis 비해당).** 이는 rate-limit-429-mitigation skill 선례(ADR-039 §결정 9 / Amendment 4)와 **동형**이다.

- Amendment 4 verbatim 요지: "§결정 2 inline whitelist closed 4-entry enumeration 무변경 (5번째 entry 신설 0 — chief 결정 … retry primitive 위치 = `codeforge:rate-limit-429-mitigation` skill body)". InfraOp 의 "ADR-039 신규 whitelist entry 신설" advocacy 는 REJECTED 됐다.
  - (단 ADR-039 §결정 15/Amendment 2 가 이후 5번째 entry 를 추가해 현행 whitelist = 5-entry — 본 인용은 Amendment 4 시점 라벨. 본 ADR 논거는 cardinality 무관 성립.)
- 동형 적용: research-request-gate skill body 가 on-demand 절차의 **operational primitive**(요청 형식·게이트 3-규칙·실행·주입)를 보유하되, ADR-039 §결정 2 inline whitelist 는 무손상이다(신규 entry 추가 0). Skill 호출은 mutation 미발화 → §결정 1 "수정 작업" 비해당(§결정 2 (b)②) → whitelist 신규 entry 추가 대상 아님.
- ADR-039 §결정 2 L145 verbatim "본 closed enumeration 가 future 'Skill 호출 / Glob / Grep / Read tool 분류 enum 확장' 압박을 차단" 과 정합 — Skill 호출은 whitelist enum 확장이 아니라 whitelist axis 외 행위(수정 작업 비해당)로 routing 된다.
- **1줄 명문**: deep-research Skill 호출 = whitelist 신규 entry 추가 0 (skill body = primitive, inline whitelist 무손상 — whitelist axis 비해당).

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
| ADR-039 §결정 1·2 | 결정 2·3 | **정합 자체 재논증 (무변경)** — disjoint 차용 불가 명시 후 독립 논거 3개로 §결정 1 spawn 독점 + §결정 2 inline whitelist 무손상(신규 entry 추가 0) 재논증. amendment 불요. |
| ADR-039 Amendment 4 | 결정 3 | **동형 선례** — skill body 가 operational primitive 보유하되 whitelist 신규 entry 추가 0. rate-limit → research-request 동형. |
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

### 대안 A — ADR-039 Amendment 으로 처리 (신규 inline whitelist entry 신설)

on-demand deep-research 호출을 ADR-039 §결정 2 inline whitelist 에 신규 entry 로 추가.

**거부 이유**:
- Skill 호출은 §결정 1 "수정 작업" closed enum 비해당(mutation 미발화) → §결정 2 whitelist axis 와 disjoint(§결정 2 (b)②). 신규 entry 신설은 whitelist axis 에 속하지 않는 행위를 axis 안으로 잘못 끌어들인다.
- ADR-039 Amendment 4 의 동형 선례(rate-limit skill body primitive ↔ whitelist 무손상, "5번째 entry REJECTED" verbatim — Amendment 4 시점 라벨)를 그대로 답습 — Skill 호출 enum 확장은 §결정 2 L145 가 명시적으로 차단한 압박이다.

채택 = 결정 3 (whitelist 신규 entry 추가 0, skill body = primitive).

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

본 ADR 은 additive skill 신설 + 기존 ADR cross-ref only 이며 약화 0 건이다. ADR-039 의 두 invariant(§결정 1 spawn 독점 / §결정 2 inline whitelist — 신규 entry 추가 0)는 무변경이고, ADR-124/125 의 어느 결정도 흡수·약화하지 않으며, 새 mechanism 은 기존 권한 경계의 합법적 조합이다. 따라서 strengthen 방향이며 sunset_justification 은 `null` (약화 evidence-gate 무관). is_transitional: false (permanent governance anchor). 원복은 별도 Story 의 명시 결정으로만 가능하며 그 경우에도 ADR-058 §결정 5 를 따른다.

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
