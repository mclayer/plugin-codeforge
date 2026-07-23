---
adr_number: 142
title: Orchestrator-self READ/synthesis/verbose-return context 규율 + self-context record-only 계측 — holder×mutation 격자 완성 (4th instance)
status: Accepted
category: governance
date: 2026-07-05
carrier_story: CFP-2572
is_transitional: false
related_adrs:
  - ADR-039   # 본 ADR = §결정 9 Read-axis advisory 천장의 Orchestrator-self realization (disjoint axis, §결정 2 whitelist 7번째 entry 신설 0)
  - ADR-044   # 본 ADR = §결정 11 thin-PL context boundary 의 holder generalization (lane-PL → Orchestrator-self)
  - ADR-043   # Amendment 3 (본 carrier) — self-context proxy 6-field record type allow-list 추가 (신규 proxy 3 + 상속 identity/version 3, numeric/enum/hash only, opt-in default-false 상속)
  - ADR-009   # wrapper-only single-lead — L6 nested read-worker offload 재검토 → DEFER (본 ADR §결정 6, 정책 유지)
  - ADR-060   # advisory→blocking evidence-gated ratchet — L1/L2/L3 승격 경로 상속
  - ADR-119   # research-before-claims — self-context 판정 = delegation proxy(ground-truth 아님) verbatim 기록 의무
  - ADR-136   # execution-liveness 3요건 — §8 신설 lint/telemetry self-test 근거 (Amendment 3 / CFP-2535)
  - ADR-134   # per-Story dispatch topology — L5 Story-boundary handoff build-on
  - ADR-139   # background-wait liveness gate — L5 sub-session handoff liveness 상속
  - ADR-120   # token-relocation-eligibility (정적 축소) — L3(동적 로드 빈도 규율)와 disjoint 보완축
amendment_log: []
related_files:
  - CLAUDE.md
  - docs/orchestrator-playbook.md
  - docs/inter-plugin-contracts/return-envelope-v1.md
  - docs/inter-plugin-contracts/spawn-event-v1.md
  - docs/domain-knowledge/concept/context-offloading-to-ephemeral-workers.md
  - docs/domain-knowledge/domain/agent-teams/agent-teams-platform-capability.md
---

# ADR-142: Orchestrator-self READ/synthesis/verbose-return context 규율 + self-context record-only 계측

## 상태

Accepted (2026-07-05 KST — CFP-2572 carrier, Epic CFP-2571 요구 #2). 장기 세션에서 최상위 Orchestrator(wrapper agent 0, ADR-009) 자기 prefix 의 superlinear 누적을, **READ / synthesis / verbose-return 흡수 축**까지 위임 규율을 확장해 해소하는 governance SSOT.

본 ADR 은 위임 통제의 **holder×mutation 2×2 격자**에서 유일하게 미배선인 4번째 사분면(holder=Orchestrator ∧ mutation=READ/synthesis/verbose-return)을 채운다. 나머지 3 사분면은 이미 CLOSED — lane-PL×WRITE(lane-self-write-boundary), lane-PL×READ(ADR-044 §결정11/CFP-2521), Orchestrator×WRITE(ADR-039 Amd9/CFP-2544). 본 ADR 은 그 두 READ/thin-holder 선행(ADR-044 §결정11)의 **holder 일반화** + ADR-039 §결정9 Read-axis 천장의 **Orchestrator-self realization** 이며, context-offloading concept 의 **4th instance**(rule-of-three 초과 → 신규 발명 아닌 확장, `docs/domain-knowledge/concept/context-offloading-to-ephemeral-workers.md`).

> **정직성 헌장 (hollow-gate 금지 — 완료 정의에 못박음).** 본 ADR 이 다루는 4축(READ-intent / synthesis-offload / verbose-return / self-context)은 대부분 **물리 하드게이트가 구조적으로 불가**하다. 각 lever 는 `[물리강제]` / `[measurement]` / `[advisory]` tier 를 verbatim 라벨하며, 게이트 언어("block"/"deny"/"강제")를 measurement/advisory 축에 적용하는 것을 금지한다. 본 Story 는 본질적으로 "계측 + 규율(discipline)" 이지 "READ 물리차단"이 아니다.

## 컨텍스트

### 근본원인 (Epic 실측 계승)

현행 위임 통제 3층(ADR-039 inline-write whitelist / CFP-2521 thin-PL / CFP-2544 hard-guard)이 **전부 WRITE(직접편집) 축에만** 물리 배선돼 있고, context 를 부풀리는 READ/synthesis/verbose-return 흡수 축은 무통제로 남았다. ADR-039 §결정9 가 "Read 축 = 영구 advisory 천장(Read-for-Q&A vs Read-as-modification 구별 불가)"로 자인했고, CFP-2544 hard-guard 는 Write/Edit/MultiEdit 3종만 커버한다.

누적원인 7종(요구사항 §1 verbatim): ① 분석용 다수 파일 직접 Read ② verbose lane 산출물 통째 흡수 ③ 매 lane/turn skill 본문 반복로드(20 skill = 2,875줄) ④ 회고·조사·synthesis 를 Orchestrator 직접 수행 ⑤ FIX 판정·root-cause inline ⑥ mirror/progress 텍스트 누적 ⑦ env=0 read-worker pre-spawn 중개 왕복.

### platform 사실 (요구사항리뷰 lane PASS 확정 — 이 위에 설계)

| # | 사실 | 판정 근거 |
|---|---|---|
| P1 | lead self-context **live per-turn 계측 표면 없음** | hook payload 에 token/context-size 필드 부재. `compact_boundary.preTokens`(coarse) + delegation-ratio proxy 만 |
| P2 | **per-Read intent 검출 infeasible** (path-deny 는 가능) | subagent frontmatter Read path-allowlist 없음; path-deny = permissions.deny + PreToolUse(Read) session-wide (대상 문제 아닌 관측 문제) |
| P3 | agent 반환 하드캡 = **UNDOCUMENTED / CANNOT-CONFIRM as reliable hard gate** (설계 lane 실측 override — 요구사항 `[verified]` 재검증) | `updatedToolOutput`(PostToolUse tool_response replace)는 tool-agnostic 로 **존재**하나 subagent 반환에 신뢰 적용 여부 문서화 0. subagent 완료 전용 이벤트 `SubagentStop` 은 `updatedToolOutput` **미지원**(additive `additionalContext` only, raw 텍스트 미보유) + **v2.1.198~ subagent background-default → Agent tool call 은 spawn-time resolve**(bulky 최종 텍스트 미보유 가능). 하드캡 gate 주장 = hollow-gate(ADR-119). 출처: code.claude.com/docs/en/hooks.md·sub-agents.md |
| P4 | nested subagent spawn = **FEASIBLE**(depth≤5, v2.1.172~) | ADR-009 wrapper-only single-lead 는 platform 불가 아닌 **정책 선택** |

물리강제 표면 = WRITE축(CFP-2544 소진) 한정. spawn-event 관측(delegation-ratio) = measurement. **L2 반환 하드캡 = 신뢰 substrate 부재(P3) → measurement + advisory 로만**. 그 외 READ/synthesis/self-context 축도 measurement/advisory.

## 결정

### 결정 1: holder×mutation 격자 완성 — Orchestrator-self READ/synthesis/verbose-return 규율 SSOT (신규 anchor ADR)

본 ADR 을 **독립 anchor SSOT** 로 신설한다(ADR-039/044 amendment 조합 아님). 근거: (a) context-offloading concept 4th instance = rule-of-three 초과 → 추출이 정합(premature abstraction 아님), (b) ADR-039+044 동시 amendment = scattered-SSOT/shotgun-surgery(단일 owner 부재), (c) **독립 anchor 가 READ-axis 결정을 ADR-039 WRITE-side whitelist 로부터 물리적으로 분리** → "7번째 whitelist entry" 오독이 **위치(location)로 구조적 불가**(어법만이 아니라). dependency 방향 = instances(ADR-039 §결정9 / ADR-044 §결정11) → anchor(본 ADR). ADR-039/044 에는 본 ADR 을 위로 가리키는 thin cross-ref stub 만 추가(재결정 금지).

**disjoint-axis 선언 (INV-C 보존)**: 본 ADR 의 READ/synthesis/verbose-return 축은 ADR-039 §결정2 inline-whitelist(현행 effective 6-entry closed = base-4(§결정2 표) + Amd2 entry5(§결정15) + Amd6 entry6(§결정18); inline 실행 예외 축 — read entry3·status entry4·merge-Codex entry6 포함이라 "write 전용" 아님)와 **완전 disjoint axis(다른 차원)**. **whitelist 7번째 entry 신설 0** — §결정2 closed enumeration 무변경. (ADR-039 §결정9 D3 / §결정16 / §결정17 의 "disjoint axis, N번째 entry 신설 0, closed enumeration 무변경" 어법 답습.)

### 결정 2: L1 — READ-offload default 승격 `[advisory / prompt-mandate]`

장수명 holder(Orchestrator)는 raw READ 를 자기 context 에 들이지 말고 read-worker 에 offload 후 high-signal 요약만 수신함을 **default 경로**로 승격한다. tier = **advisory / prompt-mandate** — per-read intent 하드 deny 는 P2(§결정9 천장)로 구조적 불가. 강제 mechanism 구분(요구사항 R7): (a) 도구 단위=tools/disallowedTools (b) 경로 단위=permissions.deny(session-wide) (c) per-subagent PreToolUse hook. native Read-path frontmatter allowlist 없음 전제.

**re-read persistence 트리거**(ADR-044 §결정11(c) 상속): 위임 판단 기준 = read 결과가 holder N+ 잔여 턴 잔존 여부(read-count 아님).

**trivial-read carve-out = CLOSED enumeration (Orchestrator-self, 신규)** — 무조건 offload = spawn 고정비 순손실(hollow-gate)이므로 면제 6항목을 closed 열거: (1) read-only Q&A 답변용 read(ADR-039 §결정2 entry3) (2) status/progress report 합성용 read(entry4) (3) Story §9/§10/§14/phase inline write 직전 확인 read(§결정15 entry5 정합) (4) merge-time Codex dispatch 판정 read(entry6 정합) (5) 단일 파일 1회성 사실 확인(값 1개, N+ 턴 미잔존) (6) lane spawn 직전 packet 구성용 발췌 read. **추가 = 본 ADR amendment 의무**(open-ended carve-out = hollow-gate anti-pattern, ADR-044 §결정11(b) 답습).

playbook §3.3:1169 "구체 내용은 Read/Glob/Grep 도구로 직접 접근" 문안 = 본 요구의 핵심 AS-IS 반증 문장 → "read-worker 위임 후 요약 수신(trivial carve-out 제외)"으로 반전(Phase 2, semantic breaking 1건).

### 결정 3: L2 — tight-summary 반환계약 `return-envelope-v1` (신설 = wrap, 기존 *_output-v1 확장 아님)

신규 범용 계약 `docs/inter-plugin-contracts/return-envelope-v1.md` 를 신설하되, 기존 `*_output-v1` / `review-verdict-v4` / `fix-event-v1` payload 를 **대체가 아닌 wrap(compose over)** 한다. envelope 이 **크기 상한 + raw 배제 + high-signal only** invariant 를 단독 소유하고, per-task payload schema 는 무변경. MANIFEST 1회 등록. 근거: cap/raw-배제 invariant 는 per-task payload schema 와 orthogonal + 34 반환계약 전체에 identical → DRY 단일 owner. per-contract cap 절 중복 = 매 신규 계약마다 silent 누락(= 본 Story 를 만든 바로 그 공백). wrap = additive/non-breaking + L2 하드캡의 **uniform 검사점 단일화**(`envelope.meta`, payload type 무관).

**구조**: `envelope.meta`{verdict, size_bytes, cap_bytes, over_cap:bool, mode:enum(concise|detailed), evidence_ref[]} + `envelope.payload`(기존 계약). raw diff/원문 **미포함** — evidence_ref pointer(경로:line)만.

**필수 raw 예외 (CLOSED)**: FIX diff / review verdict 원문 / research 인용 원천 3종 — 요약이 이들 대체 시 재작업으로 총 문맥 증가(§5.3 edge). 이 3종은 envelope 안 명시 pointer + on-demand 재fetch.

**강제 substrate 실측 결과 (설계 lane verify-before-trust override — hollow-gate 차단)**: 요구사항 §4.2 는 `PostToolUse(Agent)+updatedToolOutput` 를 하드캡 substrate `[verified]` 로 두었으나, 설계 lane 재검증(code.claude.com/docs 실측)이 이를 **반증**한다 — (a) `updatedToolOutput` 는 generic PostToolUse field 로 존재하나 **subagent 반환에 신뢰 적용됨은 문서화 0**, (b) subagent 완료 전용 이벤트 `SubagentStop` 의 decision-control 은 `updatedToolOutput` 를 **명시 배제**(additive `additionalContext` only — append 이지 replace/truncate 아님, raw 텍스트 미보유), (c) **v2.1.198~ subagent background-default** → `Agent` tool call 은 spawn-time 에 resolve(핸들 반환), bulky 최종 텍스트는 SubagentStop 경로로 후행 전달 → PostToolUse(Agent) 가 최종 텍스트를 보유하지 않을 수 있음. **결론: agent 반환 runtime 하드캡 = 신뢰 substrate 부재. "hard runtime cap via PostToolUse(Agent)" 게이트 주장 = hollow-gate(ADR-119) → 채택 금지.**

**L2 tier = `[measurement]` + `[advisory]` (하드캡 아님)**:
- `[measurement]` — `return-envelope-v1` schema **사후 파일-lint**(계약 문서 well-formed: cap 필드 + raw-배제 절 + MANIFEST 등록 검증). 이는 문서 구조 검증이지 runtime 반환 준수 강제가 **아님**(혼동 금지). fix-event-v1 이 문서 schema(파일)이지 inter-agent 반환 채널 schema 가 아닌 것과 동형(§4.2:187).
- `[advisory]` — **prompt-mandate tight-return**: worker spawn prompt 본문에 반환 상한 계약(verdict/evidence-ref only, raw 미포함, concise|detailed mode)을 명시. 유일하게 문서 확증된 lever 2종 = (i) subagent system-prompt/description 에 "짧은 반환" 지시(prompt-level, 미강제), (ii) SubagentStop `additionalContext` 로 경고 append(토큰 추가이지 cap 아님). 본 Story 자체가 이 규율을 dogfood(모든 deputy spawn 에 tight-return 계약 주입).
- **미래 재개방**: platform 이 foreground-synchronous 반환 하드캡을 문서화하거나 feature 로 제공 시 = ADR-060 evidence-gate 경유 별도 CFP + 본 §결정3 amendment. 현행 = `/feedback` feature-gap 후보로만 기록(추정 배선 금지).

**흡수 계측 = Agent-tool boundary 한정 (정직 scope)**: L7 반환-흡수 measurement(§결정4)는 Agent-tool 경계 반환만 관측. env=1 teammate→teammate SendMessage 반환은 Agent-tool 호출이 아니므로 **벗어난다**. env=0 pre-spawn 중개 double-hop 반환(누적원인 #7)은 mediation-hop 도 counting 대상(INV: mediation ≠ synthesis-in-lead escape).

### 결정 4: L7 — self-context record-only proxy 계측 `[measurement — 게이트 아님, hollow-gate 1순위]`

self-context 누적을 **record-only proxy telemetry** 로 남긴다. **live budget gate 아님**(P1 = live surface 미제공). substrate = 기존 SubagentStop-wired `spawn-event-v1` 채널 재사용(신규 hook 블록 0) + **ADR-043 allow-list amendment**(자매 carrier).

**안전 field schema (ADR-043 numeric/enum/hash only, T-INFO-5 정합 — SecurityArch 확정)**: `schema_version`(const), `session_id`(sha256), `turn_index`(int monotonic), `delegation_ratio`(float 0.0–1.0 coarse-round, proxy), `pre_tokens`(int bucketed, `compact_boundary.preTokens` 출처), `cause_category`(CLOSED enum, domain-agnostic: `read-heavy|synthesis-inline|fix-diagnosis|spawn-dispatch|skill-load|env0-mediation|other`). **FORBIDDEN**: file path / transcript 발췌 / tool_input body / free-form reason string. opt-in default-false 상속(always-on 금지) + **6-field record type**(신규 proxy 3: delegation_ratio·pre_tokens·cause_category + 상속 identity/version 3: schema_version·session_id·turn_index) 전부 **명시 allow-list 등재**(implicit add = §결정2/T-INFO-5 위반). consumer 전파 시 enum 값 domain-agnostic 의무.

**운영 posture (InfraOp 확정)**: **never-block + fail-VISIBLE** — record-only 이므로 telemetry 실패가 작업 halt 금지, 단 dropped event 는 구별 가능 trace(stderr/dropped-count) 남김(silent-success-on-error 금지 = born-broken 방지). **idempotency key = turn-id / compact_boundary event-id** + read-side dedup over distinct keys — 누적(Σ) proxy 이므로 hook 재fire/resume-rehydrate replay 시 budget 신호 팽창 차단(ADR-099 at-least-once 교훈).

**hollow-gate 1순위 verbatim 기록 의무 (ADR-119)**: delegation-ratio / preTokens = **proxy 이지 lead-self ground-truth 아님**(platform surface 부재). 어떤 self-context 판정도 게이트가 아니며, 상한식 `aN+b`(요구사항 AC-2)는 "테스트 대상 envelope"이지 "절감 floor 보장" 아님(concept:44 upper-bound). 계수 a/b/k = 실측 후 확정(사전 floor 박제 금지).

### 결정 5: L3 skill-load 규율 + L4 판정/synthesis offload + L5 Story-boundary handoff

- **L3 `[advisory / prompt-mandate]`**: platform 캐시 dedup UNVERIFIED(P-out-of-scope) → 세션 내 이미 로드된 skill 본문 재invoke 회피 + 상주 `available-skills` 요약 인덱스(system-reminder 이미 상주)로 lookup, 본문은 on-demand. 선례 = CFP-2234(skill 본문 크기 축소, disjoint 보완). ADR-120(정적 relocation)과 disjoint(동적 로드 빈도).
- **L4 `[measurement + spawn 관측]`**: FIX 판정·synthesis·조사·회고 = self-do 아닌 offload 기본 경로. **판정 compute offload = OK, §9 verdict / §10 FIX Ledger / §14 write ownership = Orchestrator monopoly 무변**(ADR-039 INV-E / ADR-044 §결정11 essential FIX-진단 carve-out 침범 금지 — offload 는 heavy synthesis 만, 1차 essential read 는 carve-out 잔존).
- **L5 `[검증된 경로 + handoff-integrity 계약]`**: Story/phase 경계에서 완료분 요약→external memory(Story file)→새 context 재개 handoff 를 1급 규약화(ADR-039 §결정19 2-level topology 재사용 + ADR-139 liveness gate). **handoff-integrity 계약(신규, 비-silent)**: sub-session handoff 시 **FIX 카운터 / §10 FIX Ledger / pin SHA** 상태를 명시 이관 — 무계약 handoff = 재개 무결성 붕괴(§5.3 edge). 상태 유실 시 fail-visible.

### 결정 6: L6 — dispatcher stance + ADR-009 재검토 결론 = nested read-worker offload DEFER

L6 = **env=1 opt-in dispatcher**(하드 default 보류) via ADR-039 §결정19 2-level lead-fixed topology + SendMessage. env=0 = ADR-044 §결정11(d) carrier(PL work-request 반환 → Orchestrator pre-spawn, self-spawn 금지) 무변. INV-1: env=0 carrier ≠ self-do escape-hatch.

**nested read-worker offload(누적원인 #7 왕복 제거) = DEFER, ADR-009 wrapper-only single-lead 정책 유지**. 근거(cost/benefit 비대칭): benefit = 7 원인 중 가장 약한 #7 의 marginal 왕복 제거 / cost = root INV-A(wrapper-only) 재개방 + experimental·disabled-by-default agent-teams 채택(**/resume 가 in-process teammate 미복원** → Epic 자체의 "장기 autonomous 견고화" 목표를 **역행** = self-defeating) + §5.6 Out-of-Scope 가 "중첩 subagent 증식" 명시 제외. platform-fact(nested spawn feasible depth≤5)는 본 ADR 에 기록 → **미래 evidence-gated Story 가 재개방 가능**. 재개방 조건: L7 계측이 env=0 원인 #7 을 dominant contributor 로 실증 AND env=0 fleet 이 primary 운영 mode 일 때. (설계 lane debate 평가 결과: adversarial debate **미발동** — genuine structural fork 아님, §5.6+INV-A+/resume hole 이 동일 방향(defer)으로 수렴, low-regret reversible 선택.)

### 결정 7: 자매 amendment + Phase 분리 + tier 정직 invariant

- **자매 ADR amendment (본 carrier)**: (a) **ADR-043 Amendment 3** — §결정4 self-context proxy **6-field record type** allow-list 추가(신규 proxy 3: delegation_ratio·pre_tokens·cause_category + 상속 identity/version 3: schema_version·session_id·turn_index, numeric/enum/hash only, opt-in default-false 상속, T-INFO-5 정합, MINOR). (b) **ADR-039 §결정9 cross-ref stub** — Orchestrator-self Read-axis realization = 본 ADR(disjoint, whitelist 무변경). (c) **ADR-044 §결정11 cross-ref stub** — holder generalization(lane-PL→Orchestrator) = 본 ADR.
- **Phase 분리**: Phase 1(설계 PR) = 본 ADR + change-plan + Story §3/§7 + 자매 stub. Phase 2(구현 PR) = `return-envelope-v1.md` 신설 + MANIFEST 등록 + L2 substrate 배선(가능 시) + L7 telemetry field + 3 self-test lint(§8) + playbook §3.3/§3.0 반전 + CLAUDE.md L1/L3 row + **stale doc 정정**(`docs/domain-knowledge/domain/agent-teams/agent-teams-platform-capability.md:66,87,154` "재귀 spawn 금지 platform inherent" → "ADR-009 wrapper-only 정책 trade-off, platform 은 nested spawn 허용 depth≤5" — 재귀-spawn 오단정 전파 원천 차단).
- **tier 정직 invariant (ratchet)**: 신규 4축(READ/return/synthesis/self-context)에 게이트 언어 적용 = 검사연극. 각 lever 는 자기 tier(`[물리강제]/[measurement]/[advisory]`)를 self-test 에서 자기 tier 만 assert(advisory bit 이 L2 enforcement 에 free-ride 금지). advisory→blocking 승격 = ADR-060 evidence-gate(PR≥20 + bypass 외 failure=0 + sibling merged) 경유만.
- **Story 3분할 권고 = N**(설계 lane → Orchestrator RECOMMENDATION, 자동 분할 아님): L1/L3(규율)·L2(계약)·L7(계측) 3축은 단일 anchor ADR + 공유 파일(CLAUDE.md/playbook) + L7 이 L1/L2 효과 판정의 선행(AC-1)로 tight-coupled. Phase 1/2 PR 분리가 이미 staging 제공. 3-way Story 분할은 anchor ADR 파편화 + 2×2-여집합 서사 단절 → 단일 Story B 유지 + §8 tier-라벨 규율로 advisory free-ride 차단이 정합.

## 근거 (Rationale)

### 채택/기각 대조

| 결정점 | 채택 | 기각 | 사유 |
|---|---|---|---|
| ADR 구조 | 신규 anchor ADR-142 | ADR-039+044 amendment 조합 | rule-of-three 초과 추출 + disjoint-by-location(7번째 entry 오독 구조적 불가) |
| L2 계약 | `return-envelope-v1` wrap (measurement+advisory) | per-`*_output-v1` cap 절 확장 / PostToolUse 하드캡 gate | DRY 단일 owner + 신규 계약 silent 누락 차단(=본 Story 원인). 하드캡 gate 기각 = substrate 미확증(P3, hollow-gate 차단) |
| L7 채널 | SubagentStop 재사용 + ADR-043 amend | 신규 lead-session hook 블록 | 신규 채널 최소(요구사항 §4.1) + 배선된 substrate 재사용 |
| L6 nested offload | DEFER + platform-fact 기록 | 즉시 채택 | /resume 미복원 = Epic 목표 역행 + §5.6 OOS + INV-A 재개방 비용 |

### 약화-evidence (ADR-058 §결정5 / ADR-064 §결정7 — is_transitional:false governance)

본 ADR = **강화 방향**(context 규율 신규 축 추가, 약화 0). ADR-039 §결정2 closed enumeration / ADR-044 §결정11 essential carve-out / ADR-043 opt-in default-false 무손상. 신규 tier 는 전부 advisory/measurement(즉시 blocking 0) — over-enforcement(hollow-gate) 와 over-infeasibility(구조적 불가 과대주장) 양방향 회피.

## 결과

### 긍정

- 장기 세션 Orchestrator prefix superlinear 누적의 4번째 사분면(READ/synthesis/verbose-return)을 규율·계측 대상으로 편입 → context pressure 관측 가능화(AC-1).
- return-envelope 단일 owner → 신규 반환계약의 cap 절 silent 누락 구조적 차단.
- concept 4th instance 정합(신규 개념 발명 0) + disjoint-by-location 으로 whitelist 오독 불가.

### 부정 (trade-off)

- 핵심 지표 대부분 measurement/advisory(물리강제 아님) — READ 통제는 정직하게 규율 tier. L7 self-context = proxy(ground-truth 아님). 유일 `[물리강제]` = disjoint-axis-whitelist-lint(ADR-integrity 정적 불변식, behavior 강제 아님).
- **L2 = runtime 하드캡 부재**(P3 실측 반증) — 반환 규율은 measurement(schema 파일-lint) + advisory(prompt-mandate tight-return)로만. platform feature-gap.
- 흡수 measurement = env=1 SendMessage 반환 미커버(Agent-tool boundary 한정) — 정직 scope 한계.
- 누적원인 #7(env=0 왕복)은 본 Story 미해소(DEFER) — 미래 evidence-gated Story.

### 영향 경계 (블라스트)

wrapper Orchestrator-self 축 한정. lane plugin 8종 CLAUDE.md / 6 SubAgent = 델타 0(lane-PL 은 CFP-2521 커버). consumer = ADR-043 opt-in default-false 상속으로 영향 0(telemetry 미활성 default). semantic breaking = playbook §3.3 반전 1건(Phase 2).

## 해소 기준

is_transitional:false permanent governance anchor. 약화 evidence-gate ratchet(ADR-064 §결정7 evidence-gated symmetric). sunset 해당 시 = holder×mutation 격자 자체 폐기 또는 platform 이 live self-context surface 제공 시 L7 proxy→direct 격상(별도 CFP + 본 ADR amendment). mechanical_enforcement = Phase 2 §8 self-test 3종(disjoint-axis-whitelist-lint 물리강제 / return-envelope-schema-lint measurement / self-context-telemetry-allowlist-lint measurement + emission-liveness fixture).

## 관련 파일

- `docs/inter-plugin-contracts/return-envelope-v1.md` (Phase 2 신설 — L2 wrap 계약)
- `docs/inter-plugin-contracts/spawn-event-v1.md` (Phase 2 — L7 self-context field, ADR-043 amend 동반)
- `docs/orchestrator-playbook.md` §3.0/§3.3 (Phase 2 — L1/L6 반전)
- `CLAUDE.md` (Phase 2 — L1 Read/Grep 문안 조정 + L3 skill-load row)
- `docs/domain-knowledge/domain/agent-teams/agent-teams-platform-capability.md` (Phase 2 — 재귀-spawn platform-inherent 오단정 정정 L66/87/154)
- `archive/adr/ADR-043-codeforge-telemetry-privacy-policy.md` (본 carrier — Amendment allow-list)
- `archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md` (본 carrier — §결정9 cross-ref stub)
- `archive/adr/ADR-044-phase-scoped-sequential-team.md` (본 carrier — §결정11 cross-ref stub)
