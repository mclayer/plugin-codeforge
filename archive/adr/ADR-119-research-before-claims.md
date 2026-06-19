---
adr_number: 119
title: "research-before-claims — 외부 지식 grounding mandate (자료 조사 선행 + 출처 인용 + abstention)"
status: Accepted
category: governance
date: 2026-06-11
carrier_story: CFP-2162
parent_epic: "mclayer/plugin-codeforge#2161"
supersedes: null
amends: null
amendments:
  - amendment: 1
    date: 2026-06-15
    cfp: CFP-2284
    summary: "§결정 9 신설 — 제안·보고 grounding 확장: §결정 1~8 의 substantive 주장(claim) 검증 후 단언을 substantive 제안(proposal)·보고(report) 로 확장. 제안 필요성 3문 게이트(① 깨졌나·강제 요인 ② 이득>비용·리스크 ③ 관찰자 없어도 할 일 — 셋 다 YES 아니면 발의 금지) + 완료보고 정직성(작업 상태 단정 = §결정 1 ② 실측 대상, 재검증 후에만 단언, 추측성 backlog 패딩 금지). Orchestrator + 전 lane PL/agent(PMOAgent retro PROMOTE 포함) 적용 + consumer 자동 상속(§결정 7) + Phase 1 declarative-only(§결정 8). CLAUDE.md 형제 bullet + consumer-guide §7.4 cross-ref + skills 2종 cross-ref 동반."
    is_transitional: false
    sunset_justification: "N/A — permanent governance. ADR-064 top-down ratchet 정합(Amendment 1 = research-before-claims 를 claim→proposal/report 로 확장, 강화 방향 only). ADR-058 §결정 5 약화 차단 통과."
  - amendment: 2
    date: 2026-06-19
    cfp: CFP-2347
    summary: "§결정 10 신설 — 검증-후-단언을 두 미적용 판정면으로 확장: ① 게이트 verdict('PASS/정상') ② 실패 진단('근본 원인=X'). 둘 다 substantive 단정인데 표면 신호 섣부른 단정(premature judgment)이 허용되던 공백. 경제 논거 = bounded 선제 검증 > unbounded 헛발질(비대칭 비용), 진단면 비대칭 결정규칙(file:line invariant 1개 > '확인함 OK' N개)과 동형. ① 게이트 outcome 판정면 실 wire = child S2/S3(게이트 verdict = 외부 관측 end-outcome ground truth, internal liveness proxy 아님 — §결정 1 row2 운영 outcome 확장 + accumulation-class 리스크 발현조건 기반 관측 창). 실 측정 주체 = consumer post-deploy CI/관측(ADR-121 §결정 3 위임 — codeforge 배포/배포리뷰 lane 은 ADR-121 로 폐지). ② 진단 falsification 판정면 실 wire = child S4/S5(runtime 실패 진단 = acted-on 전 falsification 통과 + 요구사항 lane 재진입). 단 root-cause 사다리 3rd rung('문제정의 오류→요구사항 lane 재진입')은 신규 개념 — 현 root-cause-decision 사다리는 2-rung(구현↔설계)이고 ADR-064 §결정 7(evidence-gated symmetric ratchet)은 ratchet 방향 규칙이지 진단 사다리 아님. 3rd rung 신설 = child S4(#2350). 재진입 lane carrier = ADR-125(status: Proposed). Phase 1 declarative-only(§결정 8 정합, umbrella anchor) — 실 wire = child Story S2~S5(ADR-060 4-tier). consumer 자동 상속(§결정 7). incident: mctrader-data#447 / collector#25."
    is_transitional: false
    sunset_justification: "N/A — permanent governance, 강화 방향 only(검증 적용면 확장, 약화 0). ADR-058 §결정 5 약화 차단 통과 + ADR-064 §결정 7 additive ratchet 정합."
related_stories:
  - CFP-2162
  - CFP-2284  # Amendment 1 §결정 9 carrier — 제안 필요성 게이트 + 완료보고 정직성
  - CFP-2347  # Amendment 2 §결정 10 carrier — 게이트 verdict + 실패 진단 두 판정면 확장 (Epic #2346 umbrella anchor)
related_adrs:
  - ADR-073  # Orchestrator verify-before-assert — repo/cross-repo 사실 axis (disjoint 보완 대상)
  - ADR-070  # Codex 외부 워커 output verify (외부 "워커" ↔ 외부 "지식" axis disjoint)
  - ADR-071  # 사용자 dialog convergence (표현 layer — 본 ADR 의 factual grounding 과 disjoint)
  - ADR-082  # lane agent write-time self-write verify (4-layer disjoint 표 원조)
  - ADR-085  # multi-session coordination (5-layer disjoint 표 — 본 ADR 이 verbatim 답습 + 6번째 row)
  - ADR-046  # Researcher 3 mandate (deep exploration 실행 전담 경계 — §결정 5 보존)
  - ADR-039  # §결정 2 inline whitelist (적용 면제 경계 재사용) + §결정 7 consumer inheritance 패턴
  - ADR-054  # §결정 6.1 declarative seed fast-path (본 ADR Wave 1 declarative-only 적격 근거)
  - ADR-058  # §결정 5 ratchet (약화 amendment sunset_justification 의무)
  - ADR-060  # 4-tier enforcement promotion framework (mechanical 승격 경로)
  - ADR-064  # §결정 7 evidence-gated symmetric ratchet (Amendment 2 = additive ratchet 강화 방향 정합 — 약화 0). 주: root-cause 사다리 3rd rung 은 ADR-064 미존재 개념 — 현 root-cause-decision 사다리는 2-rung(구현↔설계, skills/root-cause-decision/SKILL.md), 3rd rung 신설 = child S4(#2350)
  - ADR-014  # §7.4 operational AC — Amendment 2 §결정 10 ① 게이트 outcome-signal 선언 schema(§7.4.7, child S2)의 운영 AC 측 정합 (실측 아닌 설계-시점 선언)
  - ADR-125  # 요구사항리뷰 lane (status: Proposed — 미수락 시 재진입 lane 미발효, child S4 가 Amendment carrier) — Amendment 2 §결정 10 ② runtime 실패 진단 시 문제정의 재검증 lane
  - ADR-121  # deploy 위임 — Amendment 2 §결정 10 ① 게이트 outcome 실 측정 주체 = consumer post-deploy CI/관측(ADR-121 §결정 3 위임). codeforge 배포/배포리뷰 lane 은 ADR-121 로 폐지됨(측정 주체 아님) — 위임 경계 정합 용도
  - ADR-015  # stateful soak — Amendment 2 §결정 10 ① accumulation/lifetime-class 리스크 발현조건 기반 관측 창(soak) 도출 근거
related_files:
  - CLAUDE.md
  - docs/orchestrator-playbook.md
  - docs/consumer-guide.md
mechanical_enforcement_actions: []  # Wave 1 declarative-only — 실 wire(lint/registry) = 후속 carrier CFP full-lane 의무 (ADR-054 §결정 6.1)
wave_2_wire_carrier: "Epic #2161 S2 (agent mandate 확장) + 후속 lint CFP (ADR-060 4-tier 경로)"
is_transitional: false
---

# ADR-119: research-before-claims — 외부 지식 grounding mandate

## 상태

Accepted (2026-06-11 KST, CFP-2162 carrier). `is_transitional: false` — 영구 정책 (governance carrier).

## 본질 선언

> **모든 주체 (wrapper Orchestrator + consumer Orchestrator + 전 lane agent) 가 외부 지식을 단정 발화할 때, 자료 조사를 선행하고 출처를 인용하며, 확인 불가 시 "확인 불가/추정" 을 명시할 의무.**

위 본질 선언이 본 ADR 의 anchor (ADR-073 anchor-first 패턴 답습). 모델 training 지식은 한계 (cutoff / 환각 / 산업 변화) 를 내재 — 외부 지식 기반 주장을 출처 없이 단정하는 행위가 금지 대상이다. 지식의 *사용* (사고 / 추론) 자체는 금지 아님.

## 컨텍스트

### 사용자 directive (Story CFP-2162 §1 verbatim 발췌)

> "codeforge에서 개발이든 리팩터링이든 요구사항 분석이든 모든 것들이 검증된 다음 수행되어야 한다. 너가 알고 있는 지식 중에서는 한계가 너무 많기 때문에 모든 주장에는 자료 조사가 선행되고 그것을 기반으로 나와의 대화가 이루어져야 한다. 정식 반영해야 하고 consumer에도 적용해야 한다."

### 기존 SSOT 공백

기존 verify 거버넌스는 전부 *repo/내부 사실* 또는 *coordination* axis — 외부 *지식* axis 부재 (Story CFP-2162 §2.3 gap-1, 사내 선례 0건):

- ADR-073 = Orchestrator cross-repo state/assumption 실측 (git/GitHub ground truth)
- ADR-070 = 외부 워커 (Codex) output 검증 — 외부 "워커" ≠ 외부 "지식"
- ADR-082 = lane agent self-write write-time 검증
- ADR-071 = 사용자 dialog 표현 layer
- CLAUDE.md "검증 후 단언" = cross-repo + 외부 워커 2 대상만 (1문장 과소정의)

### 산업 근거 (외부 출처 — Story CFP-2162 §6 조사 결과 인용)

본 원칙 = 산업·학계의 기성립 개념 3종의 codeforge 거버넌스 instantiation:

1. **Grounding** — 모델 출력을 training 패턴이 아닌 외부 retrieve 사실에 근거 ([arxiv 2512.12117 Citation-Grounded Code Comprehension](https://arxiv.org/abs/2512.12117), [AWS Prescriptive Guidance — Grounding and RAG](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-serverless/grounding-and-rag.html))
2. **Citation mandate** — 응답에 원본 출처 인용 강제 = traceability ([ClarityArc — AI Hallucination and Grounding](https://www.clarityarc.com/insights/ai-hallucination-grounding-citation))
3. **Abstention / confidence calibration** — 증거 thin 시 불확실성 정직 표현 ([arxiv 2511.11500 — Honesty over Accuracy](https://arxiv.org/pdf/2511.11500), [arxiv 2604.03904 — I-CALM](https://arxiv.org/abs/2604.03904), [LLM-Honesty-Survey 2025-TMLR](https://github.com/SihengLi99/LLM-Honesty-Survey))

prompt-based 정책 directive 만으로도 환각 risk 감소 가능 ([arxiv 2604.03904](https://arxiv.org/html/2604.03904v1)) — 본 ADR 의 Phase 1 declarative 접근의 외부 근거.

## 결정

### §결정 1 — 3 검증 대상 분리 matrix

검증 대상은 본질이 다른 3종 — 단일 "검증" 으로 뭉개지 않는다 (도구 × 시점 × 실패 시 행동):

| 검증 대상 | 검증 도구 | 시점 | 검증 불가/실패 시 행동 |
|---|---|---|---|
| **외부 지식 주장** ("X 기술은 Y 로 동작" / "산업 표준은 Z") | WebSearch / WebFetch / 공식 문서 조사 | substantive 단정 발화 전 | 출처 확보 불가 → "확인 불가/추정" 명시 (§결정 3 abstention) |
| **repo·cross-repo 사실 주장** ("X file §N 부재" / "Y issue closed") | Read / Grep / `git fetch` + `git show origin/main:<path>` / `gh api` — ADR-073 §결정 1 4-의무 그대로 | 단정 발화 전 | 실측 불가 → 단정 금지 + 확인 절차 명시 |
| **확인 불가 영역** (외부 runtime state / 미래 동작 / 측정 불가) | 도구 없음 | 주장 시점 | "확인 불가/추정" 명시 후 진행 허용 (데드락 회피) |

repo 사실 row 는 ADR-073 의 기존 mandate cross-ref — 본 ADR 이 **흡수하지 않는다** (§결정 4 layer disjoint).

### §결정 2 — 적용 경계 = 기존 경계 재사용 (substantive 주장 한정)

"모든 주장" 의 문자적 100% 적용 (trivial 상태 보고 포함) = 운영 마비. 적용 경계 = **기존 경계 2종 재사용, 신규 경계 신설 0**:

- ADR-039 §결정 2 inline whitelist 4-entry 면제 영역 그대로 (사용자 대화 / TodoWrite / 읽기전용 Q&A 답변 / 상태 보고) — 주: "단순 file stat (line count / section exist)" 면제는 본 whitelist entry 가 아니라 ADR-073 §결정 1 파생 ("단정 발화 시만 verify 의무")
- ADR-073 §결정 1 "단정 발화 시만" 원칙 그대로 — 사고/추론/가설 명시 단계는 면제, *단정* 이 trigger

### §결정 3 — 출처 인용 의무 + abstention escape

1. **출처 인용**: 외부 지식 단정 시 출처 (URL / 공식 문서명 / 표준 번호) 인용 의무. ADR-073 `verified-via` annotation 의 외부 지식 확장형 — `source: <URL|문서명>` 병기.
2. **인용 = traceability 목적**: 출처 *인용* 의무이지 출처 *진실성 보증* 의무 아님. 추적 가능성 확보가 목적.
3. **abstention escape**: 조사 불가 / 출처 부재 / 측정 불가 영역 = "확인 불가" 또는 "추정" 명시 후 진행 허용. grounding 불가 영역에서 작업 차단 금지 (데드락 회피).
4. **조사 무한루프 차단**: 의무 = "조사 선행" 이지 "조사 완전성 보장" 아님 (§한계 명시).

### §결정 4 — Layer disjoint 6-layer 표 (super-class anchor)

ADR-085 §결정 1 5-layer 표 verbatim 답습 + 6번째 row "External knowledge grounding" 신설. 기존 layer 흡수/통합 금지 (ADR-073 §결정 3 layer 침범 금지 정합):

| Layer | ADR | verify 대상 / scope |
|---|---|---|
| Orchestrator cross-repo state / assumption verify | ADR-073 | Orchestrator 행위 한정 — cross-repo state + assumption 기술 시 `git fetch` + `git show origin/main:<path>` direct verify + `verified-via` annotation |
| external worker (Codex) output verify | ADR-070 | 외부 worker output 한정 — Codex finding evidence ground truth 를 Orchestrator direct file Read 로 verify, mismatch 시 verdict reject |
| internal lane agent self-write verify | ADR-082 | lane agent §9 evidence / Phase 0 mapping / corpus enumeration write-time — 작성 값 자체가 사실과 일치하는가 source direct verify 후 write |
| retro corpus enumeration (PMOAgent §5 pattern_count) | ADR-045 §D | retro pattern aggregation — cross-Story pattern_count ≥ threshold 검출 시 ADR escalation forcing function |
| Multi-session coordination | ADR-085 | 복수 Claude Code session ownership / 분담 / handoff coordination — cross-session pre-hoc coordination axis |
| **External knowledge grounding (본 ADR)** | **ADR-119** | **모델 training 지식 기반 외부 지식 단정 — 자료 조사 (WebSearch / WebFetch / 공식 문서) 선행 + 출처 인용, 조사 불가 시 abstention 명시. knowledge axis** |

6번째 row = **axis 자체가 다름**: layer 1-4 verify axis 의 ground truth = git/GitHub state (실측 가능), layer 5 coordination axis, layer 6 knowledge axis 의 ground truth = 외부 문헌 (조사+인용 가능, 실측 불가). ADR-073 §결정 2 M3 slot 비사용 사유 = 그 super-class ("stale source 인용 anti-pattern") 는 staleness mechanism 전용 — training-knowledge 한계는 type mismatch.

**거절된 대안**:
- (D-A) ADR-073 Amendment 20 으로 통합 — §결정 2 super-class type mismatch (staleness ≠ knowledge limit) + ADR-073 §결정 3 D3-C (통합 super ADR 거절) 정합 위반
- (D-B) ADR-073 §결정 2 M3 strike append — M3 슬롯은 staleness 영역 future strike 전용 (M1/M2 와 동질 mechanism 만 append 가능)
- (D-C) ADR 없이 CLAUDE.md/playbook 만 확장 — normative SSOT 부재 → 3 문서 간 drift 무중재 + consumer 상속 anchor 부재

### §결정 5 — ADR-046 역할 분리 경계 (원칙 보편 ↔ 실행 전담)

본 원칙의 격상이 ADR-046 (Researcher 3 mandate) 경계를 **암묵 침범하지 않는다** — 명시 분리:

| 축 | 내용 | SSOT |
|---|---|---|
| **원칙 (보편)** | 외부 지식 단정 전 조사 선행 + 출처 인용 의무 = 전 주체 (Orchestrator + 전 lane agent) | 본 ADR-119 |
| **실행 (전담)** | 요구사항 lane 내 deep exploration (외부 unknown unknowns / 산업 선행사례 조사) 실행 = ResearcherAgent 전담 — 타 요구사항 lane agent 는 Researcher §6 산출물 *인용* 으로 의무 이행 | ADR-046 §결정 1 (보존, 무변경) |
| **도구 권한** | agent 정의 파일 (`agents/*.md`) 의 WebSearch/WebFetch 부여 변경 = **본 ADR scope 외** | Epic #2161 S2 별 Story |

Orchestrator 자신의 사용자 대화 중 외부 지식 주장 = 자체 조사 도구 사용 가능 — ADR-046 의 exclusive 경계는 요구사항 lane 내 4-way 분업 경계이지 Orchestrator 도구 금지가 아님 (ADR-046 §결정 1 boundary 열 "Domain/Analyst 영역 외" 실측 근거). 본 항은 기존 보유 도구 사용의 확인이지 **신규 도구 권한 부여가 아니다** — agent 도구 권한 변경 = 전부 S2 scope (위 표 3행).

### §결정 6 — grounding 불완전성 한계 명시 (과잉 약속 금지)

본 원칙은 **무오류를 보장하지 않는다**. properly implemented grounding 도 환각을 부분 감소시킬 뿐이며 grounded 출력도 주어진 evidence 를 misrepresent 할 수 있다 ([SAS — RAG governance](https://blogs.sas.com/content/sascom/2025/11/25/the-strategic-imperative-governance-for-retrieval-augmented-generation/), [ClarityArc](https://www.clarityarc.com/insights/ai-hallucination-grounding-citation)). 본 ADR 의 목적 = **traceability (출처 추적 가능성) + 정직성 (불확실성 명시)** 확보 — "조사했으므로 옳다" 단정 금지.

### §결정 7 — consumer 자동 상속 (overlay 축소 불가)

본 정책 = wrapper Orchestrator + consumer Orchestrator (mctrader 등) 모두 적용. consumer 가 codeforge family plugin 을 사용하는 시점부터 inheritance — ADR-039 §결정 7 패턴 verbatim 답습. `docs/consumer-guide.md` §7.4 가 SSOT cross-ref.

- consumer overlay 로 본 원칙 **축소 불가** (확장만 가능 — CLAUDE.md overlay invariant "overlay 는 정책을 확장만 가능, 축소 불가")
- 약화 = wrapper ADR-119 amendment 경로만 — evidence-grounded justification 의무 (ADR-064 §결정 7 evidence-gated symmetric ratchet + ADR-058 §결정 5 sunset_justification)
- Phase 1 trust model — 자동 enforcement hook 부재 (ADR-039 §결정 8 패턴)

### §결정 8 — enforcement 경로 (Phase 1 declarative-only)

- 본 ADR = **Wave 1 declarative-only**. `mechanical_enforcement_actions: []` — lint / registry / hook wire 0.
- mechanical 승격 = ADR-060 4-tier promotion framework 경로 (warning-tier entry → 승격 gate) — 후속 carrier CFP full-lane 의무 (ADR-054 §결정 6.1 boundary invariant).
- agent 정의 파일 변경 0건 — Epic #2161 S2 별 Story (본 ADR 은 S2 의 normative anchor 역할만).

### §결정 9 — 제안·보고 grounding 확장 (Amendment 1 / CFP-2284): 필요성 게이트 + 완료보고 정직성

§결정 1~8 의 검증 대상은 *주장(claim)* 이었다. 본 Amendment 는 동일 grounding 원칙을 *제안(proposal)·보고(report)* 로 확장한다 (CFP-2284 carrier). 검증 부족이 거짓 주장으로 새듯, 필요성 검증 부족은 가짜·불필요 follow-up 으로, 상태 검증 부족은 미검증 완료 단언으로 샌다.

- **확장 명제**: §결정 1~8 의 "substantive 주장(claim) 검증 후 단언" 을 **substantive 제안(proposal)·보고(report)** 로 확장. **발견 ≠ 필요** — 관찰을 티켓/제안으로 자동 외부화 금지. Orchestrator = firehose (관찰 전부 방류) 아닌 filter (필요한 것만 통과).
- **제안 필요성 3문 게이트**: 작업 제안 (대화 제안 + GitHub Issue/follow-up 발의 공통) 발의 *전* 적용 —
  1. 실제로 깨졌거나 강제 요인(forcing function)이 있는가
  2. 이득 > 비용·리스크 인가
  3. 관찰자 없어도 직접 할 일인가
  **셋 다 YES 아니면 제안/발의 금지** — 기껏해야 "관찰됨·미조치 + 사유" 1줄 기록 (티켓 외부화 아님).
- **완료 보고 정직성**: 작업 상태 단언 ("완료" / "잔여" / "필요함") = §결정 1 ② (repo·cross-repo 사실) 실측 대상 → **재검증 (Read/Grep/실측) 후에만 단언**. 완료 보고에 추측성·미검증 backlog 패딩 금지 (검증 없이 "이것도 필요할 듯" 나열 = 가짜 잔여 생성).
- **적용 주체**: Orchestrator + 모든 lane PL/agent. 특히 PMOAgent retro follow-up 발의 — ADR-045 §D-11 4-option decision tree 의 **PROMOTE 결정도 본 3문 게이트 선통과 의무** (pattern_count 도달 ≠ 무조건 발의).
- **consumer 자동 상속**: §결정 7 정합 — consumer Orchestrator·PMOAgent 자동 적용, overlay 축소 불가 (확장만 가능). cross-ref anchor = `docs/consumer-guide.md` §7.4.
- **enforcement**: §결정 8 정합 **Phase 1 declarative-only** — mechanical lint 미신설. 필요성(necessity) 은 기계 비탐지 영역 (behavioral directive), lint 신설 = over-build. 향후 필요 시 별도 CFP (ADR-060 4-tier 승격 경로).

### §결정 10 — 판정면 grounding 확장 (Amendment 2 / CFP-2347): 게이트 verdict + 실패 진단 두 미적용 면

§결정 1~9 의 검증-후-단언은 *claim·proposal·report* 면을 덮었으나 **두 판정면이 누락**됐다 — ① **게이트 verdict** ("PASS / 정상") ② **실패 진단** ("근본 원인 = X"). 둘 다 substantive 단정인데 현재 *표면 신호로 섣부른 단정* (premature judgment) 이 허용된다. 본 Amendment 는 동일 grounding 원칙을 이 두 면으로 확장한다 (Epic #2346 umbrella anchor — 본 ADR §결정 10 = root anchor, 실 wire = child Story S2~S5).

- **확장 명제**: §결정 1~9 의 "substantive claim/proposal/report 검증 후 단언" 을 **게이트 verdict 면 + 실패 진단 면** 으로 확장. 두 면 모두 "표면 신호 섣부른 단정" 이라는 단일 약점의 두 발현.
- **정당화 (경제 논거)**: bounded 선제 검증 (예: 1h) > unbounded 헛발질 (예: 10h) — **무조건 이득** (비대칭 비용). 이 비대칭은 진단면의 **비대칭 결정규칙** (file:line 으로 짚힌 위반 invariant 1개 > "확인함 OK" N개) 과 **동형** — 프로세스 레벨 (선제 검증 vs 헛발질) 과 증거 레벨 (반증 1개 vs 안심 N개) 의 같은 원리.
- **incident 근거**: consumer 수집기가 전 lane PASS 했으나 제품 사망 — 게이트가 internal proxy (loop-lag / fence / CPU) green 으로 PASS (진짜 outcome = downstream 적재 성장은 미측정), 진단은 표면 증상 ("lease-thrash") 으로 원인 단정 (코드·invariant 미실측) → 약 10h 3회 헛수정. (evidence: mctrader-data#447 / collector#25)

#### ① 게이트 verdict 판정면

게이트의 PASS 조건은 **외부 관측 가능 end-outcome (ground truth)** 이어야 하며 internal liveness proxy 가 아니다 — §결정 1 row2 ("repo·cross-repo 사실 = 실측") 의 **운영 outcome 확장** (실측 대상이 코드 사실 → 운영 결과로 확대). loop-lag / fence / CPU 같은 internal liveness 지표가 green 이어도 진짜 outcome (downstream 적재 성장 등) 이 미측정이면 PASS 단정 금지.

- **outcome 의 실 측정 주체 = consumer post-deploy CI / 관측** (ADR-121 §결정 3 위임). codeforge 의 배포 / 배포리뷰 lane 은 ADR-121 로 **폐지** 됐으므로 outcome 측정 주체가 아니다. wrapper 측 = 설계-시점 **outcome-signal 선언 schema** (ADR-014 §7.4.7, child S2) — 게이트가 어떤 end-outcome 을 PASS 조건으로 선언하는가의 *설계* 이지 runtime 실측이 아니다.
- accumulation / lifetime-class 리스크 (누적·수명 의존 실패) 의 관측 창 (soak) 은 **발현조건 기반** 으로 도출 — 고정 단창 (fixed window) 금지. 리스크가 발현되는 조건 (누적량 / 경과 시간 / 자원 고갈점) 을 먼저 식별하고 그 조건이 재현되는 길이로 관측 창을 잡는다 (ADR-015 stateful soak 정합).
- 게이트 outcome 판정면의 실 wire = **S2 (#2348) / S3 (#2349)** (구체 mechanical 경로는 child 설계 lane 위임).

#### ② 실패 진단 판정면

runtime 실패의 진단 ("원인 = X") 은 acted-on (수정 착수) **전에 falsification 을 통과** 해야 한다 — 표면 증상에서 원인으로 직행하는 섣부른 단정 차단:

- **가설 격리** — 기존 진단을 검증 대상 가설 (prohibited prior) 로 격리 (가설을 정답 아닌 *반증 대상* 으로 숨김 — 확증 편향 차단).
- **다양한 독립 falsifier** — 단일 신호 아닌 서로 독립인 반증 시도 복수.
- **generative invariant sweep** — 실패 경로의 long-lived mutable 구조 열거 + bound / lifetime / ordering invariant 명시 + 코드 보존 여부 실측.
- **비대칭 규칙** — file:line 으로 짚힌 위반 invariant 1개 > "확인함 OK" N개 (위 동형 비대칭).
- runtime 실패는 FIX loop (구현 ↔ 설계 왕복) 가 아니라 **요구사항 lane 재진입** 으로 문제정의 자체를 재검증한다. 현 root-cause-decision 사다리는 **2-rung (구현 ↔ 설계)** 이다 (`skills/root-cause-decision/SKILL.md` — 요구사항 / 문제정의 rung 부재). 본 Amendment 의 child Story **S4 (#2350)** 가 **3번째 rung ('문제정의 오류 → 요구사항 lane 재진입') 을 신설** 한다 (= 신규 개념, 기존 ADR 미존재). 재진입 lane carrier = **ADR-125 (status: Proposed — 미수락 시 재진입 lane 미발효, child S4 가 Amendment carrier)**. ADR-064 §결정 7 (evidence-gated symmetric ratchet) 은 본 Amendment 의 *강화 방향 ratchet 정합* 근거이지 root-cause 진단 사다리가 아니다 (ADR-064 에 사다리 / rung 개념 미존재).
- 진단 falsification 판정면의 실 wire = **S4 (#2350) / S5 (#2351)** (구체 mechanical 경로는 child 설계 lane 위임).

#### enforcement / 경계

- **Phase 1 declarative-only** (§결정 8 정합) — 본 §결정 10 = umbrella anchor, mechanical lint **미신설**. 실 wire 는 child Story S2~S5 (ADR-060 4-tier promotion 경로 — warning-tier entry → 승격 gate).
- **consumer 자동 상속** (§결정 7 정합) — consumer Orchestrator·전 lane 자동 적용, overlay 축소 불가 (확장만 가능).

#### 거절된 대안

- (D-A) 게이트면 (① A/B) 과 진단면 (② C/D) 을 **별 원칙으로 분리** — 거절. 둘 다 "표면 신호 섣부른 단정" 이라는 단일 약점의 두 발현이라 한 umbrella (§결정 10) 가 정합. 분리 시 동형 비대칭 (프로세스 ↔ 증거 레벨) 이 두 ADR 로 쪼개져 SSOT 가 갈림.

**ADR-058 §결정 5 / ADR-064 §결정 7 정합**: 본 Amendment = additive ratchet **강화 방향** (검증 적용면 claim/proposal/report → verdict/diagnosis 로 확장) → sunset_justification = "N/A — permanent governance, 강화 방향 only". 약화 0.

## 결과

- 외부 지식 axis 의 normative anchor 신설 — 기존 5-layer 거버넌스가 6-layer 로 완결
- CLAUDE.md "검증 후 단언" 1문장 과소정의 해소 (3-way 분기)
- consumer 자동 상속 — wrapper/consumer 동일 원칙
- 비용: substantive 외부 지식 주장 시 조사 latency 추가 (§결정 2 경계 + repo 사실 외부조사 불요 분리로 완화)

## 해소 기준

N/A — permanent policy.

## 관련 파일

- [`CLAUDE.md`](../../CLAUDE.md) — "검증 후 단언" bullet 3-way 확장 (cross-ref anchor)
- [`docs/orchestrator-playbook.md`](../../docs/orchestrator-playbook.md) §3.0.9 — 외부 지식 row + ADR-119 cross-ref
- [`docs/consumer-guide.md`](../../docs/consumer-guide.md) §7.4 — consumer 상속 조항 (신설)
