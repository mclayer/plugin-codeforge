---
kind: concept_definition
type: domain-knowledge
slug: context-offloading-to-ephemeral-workers
title: Context offloading to ephemeral workers (장수명 context-holder ↔ 단수명 worker 비용 비대칭)
status: Active
updated: 2026-06-30
carrier_story: CFP-2521
related_adrs:
  - ADR-039  # Orchestrator subagent default — read/compute offload 의 root mechanism (rule-of-three 1st instance)
  - ADR-044  # Phase-scoped sequential team — lane-PL synthesizer lifecycle + §결정 11 thin-PL context boundary mandate (3rd instance carrier)
  - ADR-009  # wrapper-only decomposition — PL self-spawn 금지 (env=0 위임 = Orchestrator 경유)
  - ADR-043  # spawn-event-v1 ledger — delegation-ratio proxy 측정 substrate (opt-in default-false)
  - ADR-060  # evidence-gated promotion — advisory→blocking 승격 경로
tags:
  - codeforge
  - orchestrator-discipline
  - cost-asymmetry
  - synthesizer
  - context-management
sources:
  - https://www.anthropic.com/engineering/built-multi-agent-research-system
  - https://docs.claude.com/en/docs/claude-code/best-practices
---

## 정의

장수명(long-lived) context-holder 에이전트가 raw context(파일 전문 / 명령 출력)를 자기 컨텍스트 prefix 에 보유하는 대신, **단수명(ephemeral) worker** 에게 read/compute 를 offload 하고 **요약만 수신**하는 패턴. 비용 절감의 원천 = "장수명 prefix 잔존" vs "단수명 소멸" 의 **비대칭**이지, worker 가 더 싼 모델이라서가 아니다. Anthropic 공식 orchestrator-worker / context-offloading 패턴의 codeforge governance 적용형.

## 컨텍스트

codeforge 의 PL(Project Lead) 에이전트는 정의상 worker 산출물을 dedup·중재·통합하는 **thin synthesizer** 다. 그러나 장수명 세션(예: DeveloperPL 162턴 prefix, peak 228k)에서 PL 이 파일을 직접 read 하면, 그 raw 가 PL 의 **누적 cache_read**(≈ Σ_t 턴-시점 prefix 크기 ≈ O(turns × avg_context))에 superlinear 비용으로 남는다. PL 이 직접 읽지 않고 ephemeral worker 에 offload 하면 그 read 는 PL prefix 에 **아예 진입하지 않는다** — worker context 가 1-read→요약→소멸하기 때문이다.

CFP-2521 비용 진단(2026-06-30 로컬 세션 로그): DeveloperPL 비용 94%=컨텍스트 보유(cache_read 65% + cache_creation 29%), 그 컨텍스트의 97%=PL 직접 read(Read 52.9% + Bash 38.7%), worker 합성 1.4%. 즉 thin synthesizer 정의를 벗어나 **fat self-implementer** 로 동작 중(설계-런타임 gap). 본 concept 은 그 비용 비대칭의 메커니즘을 codify 한다.

**rule-of-three 도달**(추출 가치 확정): (1) ADR-039 — Orchestrator 가 모든 수정 작업을 subagent 로 spawn(read/compute 를 main 세션 밖으로) · (2) DeveloperPLAgent.md — lane-PL = synthesizer(worker 에 위임, raw 미보유) · (3) CFP-2521 — DeveloperPL READ/COMPUTE 경계 mandate(ADR-044 §결정 11). 3 instance 가 동일 비용 비대칭에 의존 → 타 lane PL 재사용 가능.

## 핵심 규칙

- **synthesizer_port**: context-holder 의 input = {합성 입력(plan / Story / worker 요약)}, output = {합성 산출(manifest / PR / verdict)}. raw_file_contents / bash_output 는 holder 컨텍스트 prefix 에 진입 금지.
- **비용 비대칭의 축(R4)**: long-lived-prefix-persistence(holder 의 N턴 prefix) vs short-lived-disappearance(worker 1-read→소멸). model tier 동일해도 절감 성립 — 절감 원천은 누적 재독 회피이지 cheaper-model 아님.
- **위임 트리거 = re-read persistence(read-count 아님)**: read 결과가 holder 의 N+ 잔여 턴에 잔존하면 offload 이득(누적 prefix 비용 회피). 1회성 trivial read(잔여 턴 미잔존)는 회피 재독 ≈ 0 → spawn 고정비 > 이득 → **순손실**(R5 trivial-read 면제 비협상 — 무조건 offload = hollow-gate).
- **essential carve-out(closed)**: holder 가 직접 read 해야 성립하는 기능(예: 1차진단 / worker-prompt 합성 발췌 / spec cross-validate / SHA self-pin)은 offload 대상에서 제외 — closed enumeration(open-ended = hollow-gate).
- **절감 framing = direction certain, magnitude upper-bound**: offloaded read 가 prefix 미진입은 구조적으로 확실(방향). 그러나 magnitude 는 harness auto-compact(default-on) + context-editing(opt-in)이 superlinearity 를 cap 하므로 upper-bound 모델이지 floor 아님 — 정량은 실측(spawn-event-v1 `cache_creation_input_tokens`) 후 확정.

## 경계

- **In scope**: 장수명 context-holder(PL / Orchestrator)의 read/compute 를 ephemeral worker 로 offload 하는 governance 규약. 비용 비대칭의 메커니즘 서술.
- **Out of scope**:
  - **worker spawn 권한**(누가 worker 를 spawn 하나) — env 별로 분리(env=1 = holder SendMessage / env=0 = Orchestrator pre-spawn). lane-PL 은 **self-spawn 불가**(re-entrancy 3종 + ADR-009 wrapper-only) — offload 의 "위임"은 PL self-spawn 이 아니라 work-request 반환 + Orchestrator pre-spawn(env=0).
  - **WRITE 경계**(누가 어느 경로를 write 하나) — `lane-self-write-boundary` 영역(disjoint axis). 본 concept = READ/COMPUTE 경계.
  - **parallel-exploration 토큰 증가**(Anthropic "multi-agent ~15× more tokens") — 그것은 **새 work** 발생(disjoint). 본 concept = read **재배치**(같은 work 를 holder prefix 밖으로 이동, 새 탐색 0).
- **Anti-pattern**:
  - open-ended carve-out(essential read 무한 예외) = hollow-gate.
  - 무조건 offload(trivial read 포함) = spawn 고정비 순손실.
  - "PL spawns workers"(env=0) = ADR-009 wrapper-only 위반(self-spawn 금지).
  - magnitude floor `박제`(예: "40-85% 보장") = estimate lock-in(upper-bound 모델 위반).

## 관련 ADR

- **ADR-039** Orchestrator subagent default — read/compute 를 main 세션 밖으로 offload 하는 root mechanism(rule-of-three 1st instance). §결정 9 deferred slot 에 thin-PL self-read advisory detection(CFP-2521 Amendment 8).
- **ADR-044** Phase-scoped sequential team — lane-PL synthesizer lifecycle + env 분기 SSOT. §결정 11(thin-PL context boundary mandate, CFP-2521 Amendment 5) = 본 concept 의 3rd instance carrier.
- **ADR-009** wrapper-only decomposition — PL self-spawn 금지(env=0 offload = Orchestrator 경유).
- **ADR-043** spawn-event-v1 ledger — delegation-ratio proxy 측정 substrate(opt-in default-false).
- **ADR-060** evidence-gated promotion — offload 위반 검출 advisory→blocking 승격 경로(PR≥20 + bypass외 failure=0 + sibling merged).
- **CFP-2521**(carrier_story) — DeveloperPL thin-synthesizer 컨텍스트 경계 강제(본 concept 의 first codified case).

## 변경 이력

- 2026-06-30 KST — 초기 작성(CFP-2521 Phase 1 설계 lane). rule-of-three 도달(ADR-039 + DeveloperPLAgent.md + CFP-2521) + D2 carrier 결정 잠김 후 작성(`박제` 회피 — Story §6.2 보류 조건 해소).
