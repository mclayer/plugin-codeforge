---
kind: concept_definition
type: domain-knowledge
slug: execution-based-review-verification
title: Execution-based review verification (agentic gate/test execution as ground-truth — execute-the-gate vs read-the-diff, Popper falsification 3rd mechanism)
status: Active
updated: 2026-06-30
carrier_story: CFP-2477
related_adrs:
  - ADR-119  # research-before-claims Amd 2 — 게이트 verdict ground-truth, 실패 진단 falsification (실행 검증의 정책 anchor)
  - ADR-052  # Codex proactive Touchpoint — Codex=신호원 dual-peer trigger origin 선례 (실행 dispatch 재사용)
  - ADR-077  # clarification 강제 재조사 — fact-check marker 무검증 승격 금지 invariant (실행 불일치 주장 = hypothesis default)
  - ADR-039  # Orchestrator subagent default — dispatch=lane worker Bash / Orchestrator inline (enforcement layer)
sources:
  - https://en.wikipedia.org/wiki/Static_program_analysis                                   # static = 실행 없이 분석 / dynamic = 실행 중 분석 (정의 SSOT)
  - https://en.wikipedia.org/wiki/Software_verification                                      # dynamic verification = Test 단계, 실행 중 behavior check
  - https://en.wikiquote.org/wiki/Edsger_W._Dijkstra                                         # "Program testing can show the presence of bugs, not their absence" (1969 NATO)
  - https://plato.stanford.edu/entries/popper/                                              # Popper 비대칭 — verify 불가, 단일 counter-instance falsify 가능
  - https://yuv.ai/blog/swe-agent-v2                                                         # SWE-agent — bash command + execute tests + iterate on test feedback (선행사례)
  - https://developers.openai.com/codex/concepts/sandboxing                                  # Codex CLI 3 sandbox mode (read-only / workspace-write / danger-full-access), default=workspace-write
  - https://developers.openai.com/codex/agent-approvals-security                             # Codex approval policy (on-request / untrusted / never) + sandbox 2-layer
  - https://genai.owasp.org/llmrisk/llm01-prompt-injection/                                  # OWASP LLM01:2025 Prompt Injection — repo content via injection
  - https://genai.owasp.org/llmrisk/llm062025-excessive-agency/                             # OWASP LLM06:2025 Excessive Agency — 권한·기능·자율성 확대 = 신규 공격면 (실행 검증 도입 = excessive permission/functionality 표준 닻)
  - https://arxiv.org/html/2601.17548v1                                                      # Prompt Injection on Agentic Coding Assistants — skills/tools/protocol 체계 분석
  - https://arxiv.org/abs/2507.06850                                                         # "The Dark Side of LLMs" (Evgrafov et al.) — peer-agent(inter-agent trust) 악성 명령 실행률 82.4% > direct prompt injection 41.2% (v1-v3, 17 LLM; v4 는 18 LLM·수치 개정)
  - https://dl.acm.org/doi/10.1145/3476105                                                  # Parry·Kapfhammer·Hilton·McMinn "A Survey of Flaky Tests" ACM TOSEM 2021 Vol.31(1) — flaky 비율(Google~41%·MS~26%) 1차 출처 survey
  - https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html            # Google flaky test 완화 (재실행 != fix)
  - https://www.atlassian.com/blog/atlassian-engineering/taming-test-flakiness-how-we-built-a-scalable-tool-to-detect-and-manage-flaky-tests  # quarantine 도구 산업 사례
  - https://en.wikipedia.org/wiki/Mutation_testing                                          # discriminating test = 변이 주입 후 RED 전환 여부로 adequacy 증명
  - https://arxiv.org/abs/2604.03196                                                         # "From Industry Claims to Empirical Reality" (MSR 2026) — CRA-only PR merge율 45.20% < human 68.37%, signal-to-noise 분석 (non-load-bearing 배경 — 실 repo 실행 능력 주장의 출처 아님)
---

## 정의

**Execution-based review verification** = 리뷰 시점에 PR 산출물·Story 단정을 *읽어서 비평* 하는 대신, repo 의 **게이트·테스트·체크 스크립트를 실제 실행** 해 그 실행 결과(ground-truth)를 PR/Story 의 주장과 대조하고 불일치를 finding 으로 보고하는 검증 방식. 정적 분석(코드를 실행하지 않고 분석)에 대비되는 동적 검증(코드를 실행해 동작을 관측)의 한 형태이며 (출처: Wikipedia Static program analysis; Software verification), AI 리뷰어 맥락에서는 LLM agent 가 read-only 비평가에서 **bash command 를 실제로 실행하는 행위자(agentic execution)** 로 전환하는 것이다 (출처: SWE-agent v2 — bash + execute tests + iterate).

핵심 비유 = **"게이트를 실행한다(execute-the-gate) vs diff 를 읽는다(read-the-diff)"**. 정적 diff 읽기는 "이 코드가 어떻게 *보이는가*" 만 말하고, 게이트 실제 실행은 "이 코드가 실제로 *무엇을 하는가*" 를 말한다 — 후자만이 ground-truth.

## 컨텍스트

CFP-2477 (Epic CFP-2476 의 E1 = 실행형 재리뷰) 동인 = CFP-2457 에서 관측된 dogfood 사실 — Codex 의 최대 ROI 가 "실 게이트 실행" 이었다(정적 diff 읽기가 놓친 ADR-037 version-bump P0 를 Codex 가 게이트 직접 실행으로 포착). 정적 읽기는 중간 yield, 실행 검증이 고-yield. 본 개념은 Codex peer(CodexReviewAgent)를 "diff/문서 비평가" → "게이트·테스트·체크 스크립트 실행 검증자" 로 전환한다 (사용자 §1 verbatim).

### Epic CFP-2476(= CFP-2457 후속) 3-mechanism family 내 위치 (핵심 구분)

같은 적대적 검증 철학(ADR-119 Amd 2)을 **서로 다른 mechanism** 으로 구현한 3 Story 로 구성된다 — 중복이 아니라 defense-in-depth. (Story A/B 는 선행 Epic CFP-2457 산물이고, E1 본 Story 는 그 후속 Epic CFP-2476 의 첫 Story 다 — Epic 계보 정합):

| Story | concept | mechanism | 무엇을 검증하나 |
|---|---|---|---|
| A (CFP-2458) | merge-time-adversarial-verification-gate | **review-of-output** | critic 이 *산출물(PR diff)* 을 읽고 반증 |
| B (CFP-2464) | mutation-based-hollow-gate-detection | **probe-the-detector** | *테스트 스위트* 에 변이 주입해 잡는지 |
| **E1 (CFP-2477, 본 개념)** | **execution-based-review-verification** | **execute-the-gate** | *게이트·체크 스크립트* 를 실제 실행해 단정과 대조 |

3 mechanism 은 직교한다 — A 는 diff 를 *읽고*, B 는 detector 를 *변이로 찌르고*, E1 은 게이트를 *실행* 한다. E1 은 "단정 vs 실행결과" 불일치를 잡는 유일한 축이다.

### 본 개념의 가치는 내부 dogfood 근거로 1차 정박한다

본 개념의 가치명제는 **codeforge 내부 dogfood 사실로 1차 정박** 한다 [verified: project_cfp_2457 memory — "C 구현리뷰: Codex 가 ADR-037 실 게이트 직접 실행 → under-bump P0(MINOR, Claude peer·PL 놓침) 포착"]. 즉 정적 diff 읽기(Claude peer + PL)가 놓친 version-bump P0 를 Codex 의 *실 게이트 실행* 만이 포착했다 — 이것이 "실행 검증 > 정적 읽기" 의 firsthand 증거이고, 본 개념의 결론은 이 내부 근거만으로 닫힌다.

외부 산업 현황(production AI 리뷰 도구가 정적 읽기 + 광역 context 에 머무는 경향)은 이 결론을 **장식적으로만 뒷받침하는 non-load-bearing 배경** 이다 — 결론의 근거가 아니다. SWE-agent 류 autonomous agent 는 sandbox 에서 bash + test 를 실행하나(출처: SWE-agent v2), 이는 *수정 agent* 이지 *리뷰 검증 agent* 가 아니다 — 즉 "실행을 리뷰 *검증* 에 쓰는" 선행사례는 드물고, CFP-2477 은 이 실행 검증을 리뷰 lane 에 도입한다. (참고: 산업 CRA 실증 연구로 arxiv 2604.03196 "From Industry Claims to Empirical Reality" (MSR 2026) 가 CRA-only PR 의 merge율이 human 대비 낮고 low-signal noise 가 많음을 보고하나, 이는 *리뷰 신호 품질* 분석이지 "agent 가 repo 코드를 실행 못 한다" 는 능력 주장의 출처가 아니다 — background only.)

## 핵심 규칙 (외부 개념 → invariant 매핑)

### X-1: Popper 비대칭 — 실행은 falsify 하지 verify 하지 않는다 (철학 anchor)

Dijkstra(1969 NATO): "Program testing can be a very effective way to show the presence of bugs, but it is hopelessly inadequate for showing their absence" (출처: Wikiquote Dijkstra). Popper 비대칭 — 보편 명제는 경험으로 verify 불가, **단일 counter-instance 가 falsify** (출처: SEP Popper). 

**함의**: 게이트 실행이 "단정 N개가 옳다" 를 *증명* 하지 못한다 — 그러나 단정 1개가 실행결과와 어긋나면 그 단정은 *반증* 된다. 본 개념의 인식론적 지위 = "확신 생성기" 가 아니라 "거짓 확신 파괴기". 사용자 §1 의 "Codex 가 실행해 거짓 확신을 깬다" 가 이 철학의 직접 표현. 따라서 실행이 GREEN 이어도 "PR 이 옳다" 단정 금지 — 실행이 RED 이거나 단정과 불일치할 때만 finding 으로 승격.

### X-2: 실행 대상 우선순위 = discriminating check (hollow check 실행 금지)

단순히 통과하는 게이트를 실행하는 것은 yield 가 낮다 — 통과는 X-1 상 무정보(verify 불가)다. 고-yield 대상 = **discriminating check**: 결함이 실제로 있으면 RED 로 뒤집히는 검사. mutation testing 의 정의가 이 기준 — 변이(결함) 주입 후 테스트가 RED 로 바뀌어야 그 검사가 진짜로 무언가를 검증함이 증명된다(출처: Wikipedia Mutation testing). assertion-free / `assertTrue(true)` 식 hollow check 는 실행해도 늘 GREEN → 실행 검증의 가치 0.

**함의**: 실행 대상 선택 휴리스틱(§1 이 설계로 미룸)은 외부 근거상 **discriminating power 우선** — PR 이 touch 한 체크 스크립트·테스트·관련 게이트 중 "결함이 있으면 깨질" 것을 우선. ADR-037 version-bump 게이트 류(bump 누락 시 RED)가 정확히 이 부류. 이 우선순위는 Story B(mutation hollow-gate)와 상보 — B 가 detector 자체의 discriminating power 를 검사한다면, E1 은 discriminating 한 detector 를 우선 실행한다.

### X-3: 비결정/flaky 실행 처리 = 재시도-후-finding, quarantine, 결정론 격리 (산업 표준)

실행 검증은 테스트가 결정론적이라 암묵 가정하나 flaky test 가 이를 깬다 — 대형 산업 조직에서 flaky 비율이 유의미하게 보고된다(Google ~41%·Microsoft ~26% — 1차 출처: Parry et al. "A Survey of Flaky Tests", ACM TOSEM 2021, DOI 10.1145/3476105). 산업 표준 관행 2축:

1. **재시도 ≠ 수정**: 재시도는 증상만 가린다 — "retries only hide the symptom, make it harder to tell when a failure is real" (출처: Mill build). 재시도는 *임시 quarantine* 일 뿐 fix 아님. Google: 재실행은 완화책이지 해결책 아님 (출처: Google Testing Blog).
2. **quarantine**: flaky 검출 시 merge/deploy 판정에서 제외 + owner + deadline (Microsoft: 6개월 내 18% 감소 보고; Atlassian: 전용 도구; "needs a retry to pass → quarantine immediately, owner+deadline, 2주 내 미수정 시 삭제", target flake rate <2%) (출처: Atlassian engineering; Parry et al. TOSEM 2021 survey 종합).
3. **결정론 격리(deterministic seeding)**: fixed clock 주입(now() 금지), randomness 를 seeded/fake 로 치환, remote dependency 를 fake/stub/mock 으로 격리 (출처: Semaphore / TestRail / Mindroast).

**함의**: 실행 결과가 RED 라도 곧장 finding 승격 금지 — **flaky 가능성 배제 후** 승격. 표준 관행 = (a) 동일 스크립트 다회 실행으로 결정론 확인 후 finding, (b) flaky 판정 시 finding 이 아니라 flaky-quarantine 신호로 분류. 이는 Story B M-3(flaky 오염) 와 동형 — flaky 가 false-RED(없는 결함 날조) + false-GREEN(있는 결함 은폐) 양방향 오염. flaky 미격리 시 실행 검증이 noise generator 로 전락(cry-wolf → 도구 폐기).

### X-4: 실행은 read-only sandbox 기본 — destructive command + prompt injection + excessive agency 차단 (보안)

LLM agent 가 repo 에서 명령을 실행하는 순간 두 위험이 활성화된다:

1. **prompt injection via repo content**: agent 가 소비하는 repo 내용(코드 주석, README, PR 본문, 클론한 파일)에 주입된 명령이 실행될 수 있다 — OWASP LLM01:2025 (출처: genai.owasp.org). "researchers demonstrated successful attacks via code comments in repositories the agent clones". LLM 은 instruction 과 data 를 구조적으로 구분 불가 — NLP 에 SQL parameterization 같은 architectural 해법 부재 (출처: arxiv 2601.17548 agentic coding assistant injection).
2. **destructive command (peer-agent 경로)**: peer-agent 가 요청한 악성 tool call 을 17 LLM 중 82.4%(inter-agent trust 경로)가 실행 — direct prompt injection 41.2% 보다 높다(출처: Evgrafov et al. "The Dark Side of LLMs", arxiv 2507.06850 v1-v3, vulnerability gradient: direct 41.2% < RAG backdoor 52.9% < inter-agent trust 82.4%; v4 는 18 LLM 으로 확장하며 수치를 개정). 즉 peer-agent dispatch 경로가 더 위험.

또한 실행 검증 도입 자체가 **agent 에게 임의 스크립트 실행 권한·기능을 부여** 하므로 OWASP **LLM06:2025 Excessive Agency** 의 공격면(excessive functionality / excessive permissions / excessive autonomy)을 신설한다 (출처: genai.owasp.org/llmrisk/llm062025-excessive-agency). → 최소권한(필요한 체크만 allowlist) + 고영향 행위 승인 게이트가 표준 완화책.

산업 sandbox 표준 = Codex CLI 의 3 mode 모델이 직접 참조점 (출처: developers.openai.com/codex/concepts/sandboxing):
- **`read-only`**: 파일 읽기만, 편집·명령 실행은 승인 필요.
- **`workspace-write`** (Codex default): workspace 내 읽기·편집·routine 명령, 그 경계 밖은 승인. network 는 agent phase 에서 기본 off.
- **`danger-full-access`**: sandbox 무력화 — 명시적으로 원할 때만.
- 보호 경로: `.git/`·`.codex/` 는 writable workspace 안에서도 write 차단(git hook·sandbox config 변조 방지). OS 격리 = macOS Seatbelt / Linux Landlock+Seccomp.

**함의**: 실행 검증의 안전 기본값 = **검증은 read-only / network-off / 비파괴 명령 + 검증된 체크만 allowlist(LLM06 최소권한)** 로. 게이트·테스트 *실행* 은 본질상 read-only 검증 행위여야지 repo 를 변형하면 안 된다(검증이 부작용을 남기면 ground-truth 가 오염). §1 이 보안을 명시하지 않았으나 외부 표준상 read-only sandbox + network-off + 최소권한이 요구사항 배경. `.git` 보호는 특히 중요 — 실행 검증이 git 상태를 바꾸면 후속 lane 오염.

### X-5: Codex = 신호원, ground-truth falsify 후 채택 (separation of duties 상속)

실행 결과조차 자동 채택 금지 — X-3 flaky·환경 차이(deps 미설치/OS 차이) 오염 가능. Story A C-2(implementer ≠ certifier) + Story B M-2 를 실행 축으로 상속: Codex 가 게이트를 실행해 불일치를 *보고* 하나, 그 finding 의 채택은 PL 이 직접 재실행(firsthand re-run)으로 falsify 한 후. §1 verbatim "Codex finding 은 여전히 ground-truth falsify 후 채택(verify-before-trust)". 

이는 ADR-077 I-4 fact-check marker 무검증 승격 금지와 동형 — Codex 의 "실행결과 vs 단정 불일치" 주장 = `[hypothesis]` default, PL 직접 재실행 검증 후만 `[verified]` 승격. MEMORY.md dogfood track record 양방향 실재 — Codex 가 Claude-miss P0 firsthand 포착(CFP-2457 version-bump)도, Codex false-pos 를 PL runtime-test 가 교정(CFP-2440/2449 각 2건)도 다수. 즉 실행 검증자도 신호원이지 판정자가 아니다.

### X-6: dispatch 경로 = lane worker Bash 또는 Orchestrator inline (ADR-039 정합)

§1 verbatim — "dispatch 는 lane worker Bash 또는 Orchestrator top-level inline". ADR-039 Orchestrator subagent default 정합 — lane worker 가 `node codex-companion.mjs` / `codex exec` 를 Bash 로 호출하거나, Orchestrator 가 inline 으로(whitelist). enforcement 기구(어느 경로를 언제) = 설계 lane 위임(개념 layer 아님). X-4 보안 기본값(read-only sandbox)은 어느 dispatch 경로든 불변.

## 경계

- **In scope**: 리뷰 시점 게이트·테스트·체크 스크립트의 실제 실행으로 단정을 falsify 하는 execution-based verification 의 개념 정립 + 실행 대상 우선순위(discriminating) + flaky 처리 표준 + sandbox 보안 기본값 + 신호원 승격 룰.
- **Out of scope**:
  - Story A(review-of-output) / Story B(probe-the-detector) — 같은 적대 검증 family, **다른 mechanism**. E1=execute-the-gate. 중복 아님, defense-in-depth.
  - 적용 lane 확장 범위(§1 = code-review lane 우선, 확장은 설계) + 실행 대상 선택 휴리스틱 구체 wiring + dispatch enforcement 기구(lane worker Bash matcher / Orchestrator inline whitelist) — 설계 lane 위임(개념 layer 아님).
  - FIX ground-truth replay(Epic E3) — 본 개념은 *리뷰 시점* 실행. FIX replay 는 별 Story.
- **Anti-pattern**: 실행결과 GREEN 을 "PR 옳음" 으로 단정(X-1 verify 불가). hollow check 실행으로 yield 0(X-2). flaky 미격리 RED 를 즉시 finding 승격(X-3 false-RED 날조 → cry-wolf). 실행을 full-access/network-on/파괴 명령으로(X-4 injection·destructive·excessive-agency). Codex 실행결과 무재현 자동 채택(X-5 separation 위반).

## 관련 ADR

- **ADR-119** Amd 2 — 게이트 verdict 를 내부 proxy 아닌 결과 ground-truth 로만 단정 + 실패 진단 falsification. 본 개념 = 그 정책의 *실행 기반* 충족 mechanism (carrier 동인).
- **ADR-052** — Codex proactive Touchpoint, Codex=신호원 dual-peer trigger origin 선례. 실행 dispatch 가 이 origin 을 execution 축으로 재사용.
- **ADR-077** I-4 — fact-check marker 무검증 승격 금지. 실행 불일치 주장 = hypothesis default, 재실행 falsify 후 verified 승격(X-5)의 재사용 anchor.
- **ADR-039** — Orchestrator subagent default. dispatch 경로(lane worker Bash / Orchestrator inline) enforcement 정합(X-6).
- **ADR-070 Amendment 11** (CFP-2477 설계 lane codify) — review-lane execution scope 확장 (§결정 D1 carve-out 정리: CodexReviewAgent 정적 인용 axis ↔ 실행 검증 결과 axis 분리) + 신규 §결정 D9 일반 실행검증 disposition (3-상태 + 다회 결정론 전제 + lane-time `fail_open_then_record_with_marker`). 본 개념 X-2/X-3/X-5 의 normative realization. **dispatch enforcement = `adversarial-review`(read-only turn) primary / `task --write` 예외, 실행 주체 = Codex CLI 자체 sandbox(read-only 기본/network-off/.git 보호) — lane worker own-Bash 아님** (X-4/X-6 설계 확정).
- **ADR-081 Amendment 11** (CFP-2477 설계 lane codify) — 신규 §결정 D13 execution dispatch (file-redirect, `review --focus`[dead] 교체) + §결정 D3 3-lane partition 에 execution ground-truth axis 추가. execution-dispatch-pattern-v1 (7-step E2/E3 재사용 인터페이스) SSOT = ADR-070 Amd11 B3 + ADR-081 Amd11 A3 + 본 개념 X-6.

## 변경 이력

- 2026-06-30 KST — 초기 작성 (CFP-2477 ResearcherAgent Mandate 1·2 산출물). static-vs-dynamic 검증 / Popper-Dijkstra 비대칭 / agentic execution(SWE-agent) / flaky 표준(TOSEM 2021 survey·Google·Microsoft·Atlassian) / Codex sandbox 3-mode / OWASP LLM01·LLM06 injection·excessive-agency cited. Epic CFP-2476(= CFP-2457 후속) 3-mechanism family(A review-of-output / B probe-the-detector / E1 execute-the-gate) 직교성 명시.
- 2026-06-30 KST — 요구사항리뷰 FIX(CFP-2477 P1/P2/P3): (P1) arxiv 2604.03196 에 귀속했던 verbatim "agents cannot execute repository code..." 가 해당 논문(abstract+PDF)·Sourcegraph 양쪽 부재(오귀속)로 삭제 — 가치명제를 내부 dogfood 근거(CFP-2457 version-bump P0, firsthand [verified])로 1차 정박하고 산업-gap 주장은 non-load-bearing 배경으로 강등. 2604.03196 은 CRA 신호품질 연구로서 background-only 재인용. (P2) 1차 출처 추적성 보강 — flaky 41%/26% → ACM TOSEM 2021(10.1145/3476105) survey 1차 ID, peer-agent 82.4%·direct 41.2% → arxiv 2507.06850(v1-v3, 17 LLM) 1차 ID, OWASP LLM06 Excessive Agency 닻 추가(X-4). (P3) family 캡션 Epic 계보 정합.
- 2026-06-30 KST — 설계 lane codify cross-ref (CFP-2477 E1): X-2~X-6 의 설계 위임 영역이 ADR-070 Amendment 11(§결정 D1 carve-out 정리 + §결정 D9 일반 실행검증 disposition) + ADR-081 Amendment 11(§결정 D13 execution dispatch + §결정 D3 execution axis)로 codify 됨. dispatch enforcement 확정 = adversarial-review/task + Codex CLI 자체 sandbox(read-only 기본/network-off) — lane worker own-Bash 아님. execution-dispatch-pattern-v1(7-step) = E2/E3 재사용 인터페이스 명문화. 관련 ADR 섹션에 Amd11 2건 추가.
