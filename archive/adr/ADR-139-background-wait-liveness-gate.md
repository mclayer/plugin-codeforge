---
adr: ADR-139
title: background-wait liveness gate — codeforge-owned background subagent 대기 유한성 1급 원리
status: Accepted
date: 2026-07-02
supersedes: []
superseded_by: []
carrier_story: CFP-2549
related_adrs:
  - ADR-081  # §D14 Codex companion wall-clock ceiling — 본 ADR 이 일반화하는 codex-특정 선례 인스턴스
  - ADR-039  # spawn/lead 토폴로지 — §결정 19 lead force-resume/TaskStop 개입 책임 (본 ADR liveness 게이트 개입 축의 spawn-권한 기반)
  - ADR-119  # §결정 10 outcome-honesty — fail-open 금지 origin SSOT (본 ADR 상속)
  - ADR-038  # 6-point lane 전이 marker best-effort — liveness signal 로 재사용 안 함 (marker≠liveness)
  - ADR-115  # SubagentStop record-only — gating 금지 (본 ADR 는 관측/ledger 용도만, blocking 승격 안 함)
  - ADR-043  # spawn-event opt-in default-false — telemetry always-on 전제 금지 (본 ADR 관측층은 telemetry 의존 안 함)
  - ADR-064  # §결정 1 신규 ADR = full 10-lane / §결정 7 evidence-gated symmetric ratchet — 본 ADR 신규 carrier 정당화
  - ADR-060  # warning-tier lint 승격 evidence-gate — 2안 presence lint tier
  - ADR-061  # §결정 1 Python-SSOT + thin shell wrapper — 2안 lint 구조 패턴
amendments: []
---

# ADR-139: background-wait liveness gate

## Status

Accepted (2026-07-02, carrier CFP-2549, dogfood wrapper-self).

## Context

codeforge Orchestrator/lane-PL 이 background subagent/worker 응답을 기다릴 때 **wall-clock 상한 + liveness 관측이 없으면 stall 이 무한 대기로 번진다.**

CFP-2545 (ADR-081 Amendment 12 §결정 D14) 가 codex-companion 브로커 경로(`node codex-companion.mjs adversarial-review --wait`)의 무한 대기를 wall-clock ceiling + fail-open 금지 + Orchestrator liveness 게이트로 해소했으나, 이는 **한 인스턴스**일 뿐이다. 근본 문제는 **모든 codeforge-owned background subagent 대기**에 존재한다.

**의존 체인 (결론-배선 갭)**: CFP-750 (Iter4 ~2h silent hang) → #763 (Iter5 3후보 `background-task-liveness-gate` + `agent-non-response-timeout` + `passive-work-detection` **발의만·미배선**) → CFP-2545 (§D14 codex-companion 만 배선) → **CFP-2549 (전 subagent 일반화)**. 재발 근본 = 결론냈으나 mechanical hook 미배선.

**직접 증거 (firsthand — CFP-2545 실행 세션 + 본 CFP-2549 요구사항/설계 lane 자체)**:
- lane PL background-yield 반복: 자식 spawn 후 "턴 종료" → parent(PL) 무한 정지 구조. 자식 완료 통지가 parent 아닌 lead(main) 로 surface (ADR-039 §결정 19 구조적 한계).
- DeveloperAgent 0-byte output → stall 오판 (실제 완주 중).
- **본 CFP-2549 설계 lane 실증**: ArchitectPL 이 6 deputy fan-out 후 background-yield → 6 deputy 중 4 가 lead 로 delivery-gap surface, PL context 미도달 → lead 개입(force-resume/조립) 필연. 본 Story 의 존재 이유를 설계 lane 이 자기 재현.

**contract-level 공백 (핵심 구현 gap)**: `docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md` §6.3 `pl_integration_review.worker_outcomes: list # [PASS | FIX-N | CRASH]` — **INCONCLUSIVE/STALL verdict value 부재**. 같은 §6.3 주석 "crash recovery / fail-mode protocol = 별 CFP follow-up scope" 로 timeout/fail-mode protocol 을 명시 defer. CFP-2549 = 그 deferred follow-up carrier.

## 두 직교 축 (본 ADR 의 도메인 근거)

| 축 | 질문 | 실패 형태 | SSOT |
|---|---|---|---|
| **adequacy(충분성)** — hollow-gate | 게이트가 *충분히* 검사하는가 | reached-but-dead / green-but-dead | ADR-060 |
| **liveness(생동성)** — 본 ADR | 대기/게이트가 *유한 시간* 내 결론에 도달하는가 | stall / 무한 대기 | 본 ADR-139 |

직교성(상호 미함의): adequate-but-not-live (완벽 커버해도 deadline 부재로 stall) / live-but-not-adequate (5초 유한 종료해도 대상 미검사 = hollow). 한 축 방어가 다른 축 미대체 → **별도 1급 mandate 필요** = 본 신규 ADR carrier 근거 (ADR-064 §결정 1 Amendment-first 예외 — 직교 1급 신개념 + 다ADR 걸침 SSOT 산란 방지).

## 결정

### 결정 1 — background-wait liveness gate 4 불변식 (INV-L1~L4)

codeforge Orchestrator/lane-PL 이 codeforge-owned background subagent/worker 응답을 대기할 때 다음 4 불변식이 성립해야 한다:

- **INV-L1 (wall-clock ceiling 존재)**: 대기 지점에 명시적 max-wait 상한 존재 (하드코딩/env/문서 중 하나로 특정 가능, 암묵 무한 금지). stall 판정 = outcome ground-truth 기반, internal proxy(loop-lag/CPU) 금지 (ADR-119 §결정 10 ① 상속). **max-wait 값 = 발현조건 기반 관측 창** (자식 정상 최대 무출력 span 근거, 고정 단창 금지).
- **INV-L2 (fail-open 금지)**: stall ≠ PASS. stall = outcome 미측정 → verdict = **inconclusive** (PASS 자동승격 금지, PASS-only-if-explicit: verdict == "PASS" 명시 문자열일 때만 PASS). 부분 stall (다수 자식 중 일부) → ANY(inconclusive) → 전체 inconclusive. **origin SSOT = ADR-119 §결정 10 outcome-honesty** (본 ADR 는 이를 background-wait 면으로 상속·확장; ADR-081 §D14 는 codex-companion 로의 동일 상속 선례 인스턴스).
- **INV-L3 ("0-byte ≠ stall" 구분)**: 판정 = wall-clock ceiling(시간 축) + progress-marker(진행 축, output mtime + content grep + task-notification) 결합. 0-byte stdout 단독으로 stall 단정 금지 (완주 중 0-byte 가능 — G1 known-unknown). 3-state(진행/미획득/stall).
- **INV-L4 (게이트 소유 = Orchestrator/lead 고정)**: liveness 게이트 개입 주체 = Orchestrator/lead. worker 자가-spawn 금지 (`plugins/codeforge-review/CLAUDE.md:46` "워커는 직접 다른 subagent 스폰 불가"). 대기 주체 ↔ 판정 주체 분리 (worker self-attestation 차단, 신뢰 경계). 값 순서 불변식: `timeout N < liveness max-wait` (호출부 timeout 이 먼저 터져 marker 를 남기고 게이트가 그 이후 관측 — 역순 금지).

### 결정 2 — detection ≠ recovery 분리 (K8s liveness probe / OTP supervisor 표준)

liveness 게이트 = **detection layer** (stall 판정). recovery 정책(재시작 vs 포기 vs alert)은 **별도 layer**. LLM subagent spawn 재시작은 비용·비결정성 보유 (ADR-057 fallback 교차) → default recovery = 해당 task 만 re-dispatch (`parallel-dispatch-protocol-v1` I-6.5 정합), stall 은 inconclusive marker + 다음 step 진행 (blocking recovery 강제 아님).

source: K8s liveness probe cardinal rule (외부 의존성 검사 금지, 대상 진행성만) [https://kubernetes.io/docs/concepts/workloads/pods/probes/]. Erlang OTP supervisor (heartbeat 누락 → escalating recovery, detection≠recovery 분리) [https://www.erlang.org/doc/system/design_principles.html].

### 결정 3 — false-positive 조기 회수 방지 (total-deadline vs idle-timeout 2축 병용)

살아있는 worker 를 stall 로 오판해 조기 TaskStop(E4) 하지 않도록 **2축 병용**:
- **total-deadline**: 대기 시작부터 절대 경과 상한 (gRPC deadline 동형) = max-wait ceiling.
- **idle-timeout**: 진행 침묵 상한. progress-marker(mtime/notification) 갱신 시 idle 창 reset → 느리지만 진행 중인 worker 오kill 방지.

source: Envoy/Akka idle vs max timeout 2축 표준 (false-positive 오kill 방지) [https://www.envoyproxy.io/docs/envoy/latest/faq/configuration/timeouts]. 확인: 구체 수치는 codeforge 도메인 empirical 미실증 — env-override 로 조정 가능하게 두고 default 는 추정값 명시.

### 결정 4 — 병행 형상 (1안 강제층 + 2안 정적 회귀층)

§D14 선례(문서규율 + lint 병행) 정합:
- **1안 (Orchestrator 규율, 강제층)**: `docs/orchestrator-playbook.md` 규율을 "모든 codeforge-owned background subagent 대기"로 일반화 — max-wait ceiling 정량 + progress-marker 관측 + stall 시 lead force-resume(SendMessage)/TaskStop 유한종료 + fail-open 금지(inconclusive) + Orchestrator 소유. ADR-039 §결정 19 lead-intervention 을 정량 mechanical liveness 게이트로 일반화.
- **2안 (presence-grep lint, 정적 회귀층 — execution-backed self-test 동반 의무)**: presence-grep 단독은 hollow-gate 위험 (CFP-2545 교훈). **execution-backed self-test 필수** — 실제 max-wait 초과 시 유한종료 + inconclusive 실증 (RED→GREEN discriminating, 가드 제거 mutation → RED 전환 증명). ADR-060 warning-tier 착지 (§결정 9 evidence-gate 미충족 시 blocking 승격 금지, ADR-039 §결정 9 advisory 천장 정합). ADR-115 SubagentStop record-only 무손상 (본 lint 는 관측/ledger 용도, blocking gating 아님). ADR-043 telemetry opt-in 무손상 (presence lint 는 telemetry 의존 없음).

### 결정 5 — contract 반영 (parallel-dispatch-protocol-v1)

`parallel-dispatch-protocol-v1.md` §6.3 `worker_outcomes` enum 에 **INCONCLUSIVE** value 추가 (`[PASS | FIX-N | CRASH | INCONCLUSIVE]`) + timeout/fail-mode protocol 최소 섹션(background-wait liveness gate 4 불변식 cross-ref) 신설. §6.3 주석의 "crash recovery / fail-mode protocol = 별 CFP follow-up scope" defer 를 CFP-2549 로 해소. registry MINOR bump (v1.0 → v1.1, kind:registry sibling_sync_exempt 유지 — ADR-008/ADR-010 registry 면제).

### 결정 6 — sibling Amendment set (doc-only, 본 ADR-139 Phase 1 PR 동봉 가능)

본 ADR-139 이 carrier SSOT 이나, 인접 ADR 에 cross-ref Amendment 동반 (전부 강화 방향 doc-only, src/tests 무변경):

| ADR | Amendment | 내용 |
|---|---|---|
| ADR-081 | Amendment 13 | §D14 (companion 특정) → ADR-139 cross-ref (companion 은 background-wait liveness gate 의 first instance 임을 declare, §D14 본문 무변경) |
| ADR-039 | Amendment 9 (§결정 20 신설) | background subagent spawn liveness = ADR-139 cross-ref (§결정 19 lead force-resume/TaskStop 개입 축의 정량 게이트化 — §결정 9 slot 침범 아님, 신규 §결정 20). §결정 2 inline whitelist 6-entry 무손상, §결정 1 binary always-spawn 무변경 |
| ADR-115 | (선택) §결정 1 hook tier 표에 "background subagent liveness = spawn-gate(PreToolUse Agent) 계층 + SubagentStop record-only 무손상" 1줄 cross-ref | SubagentStop block 금지 invariant 재확인 |
| ADR-119 | (선택) §결정 10 fail-open 금지 → ADR-139 INV-L2 instantiation cross-ref | origin SSOT 명시 |

## 거절된 대안

- **(A) ADR-039 Amendment 9 (§결정 20) carrier**: §결정 19(lead-intervention)는 spawn-topology 축이고 liveness 정량 게이트는 별 축 → §결정 20 신설해도 ADR-039 scope(subagent-default spawn) 초과. spawn-권한 기반으로만 cross-ref (Amendment 9 는 sibling 으로 채택 — 아래).
- **(B) ADR-081 Amendment 13 (§D14 generalize) carrier**: ADR-081 = Codex worker prompt boilerplate + invocation SSOT scope. 일반 subagent(harness-managed, prompt boilerplate 무관)엔 scope mismatch. §D14 pattern 일반화 cross-ref 만 sibling 으로 채택.
- **(C) 기계 훅(PreToolUse/SubagentStop) blocking 강제**: hooks.json 에 **PreToolUse "Agent" matcher → `pretooluse-agent-spawn-gate` 훅 존재** (origin/main 실측) — 그러나 이는 **spawn 시점** 게이트라 **wait-elapsed 축 부재** (대기 *중* liveness 판정 불가). SubagentStop = async false **record-only** (ADR-115 §결정 2 — Stop/SubagentStop `block(continue)` = platform 결함으로 신뢰 불가, GitHub #10412/#55754 evidence, block 절대 금지). PostToolUse 부재. ADR-039 §결정 9 advisory 천장("완주중 무출력 vs hang" semantic 구별 불가). → 2안 presence lint 는 warning-tier 정적층만, blocking 강제 아님. **§결정 9 slot 침범 금지** (아래).
- **(E) ADR-039 §결정 9 hook slot 채움**: §결정 9 deferred slot = "Orchestrator inline write detect hook (PreToolUse on Write/Edit/mcp__github__*)" — **inline-write-detect 축**이지 background-wait liveness(완료 감지) 축이 아니다 (완전 별개 축). §결정 9 에 liveness 게이트를 밀어 넣으면 scope 오염 → 이후 진짜 inline-write-detect hook 구현 시 confusion. 본 ADR liveness 원리는 §결정 9 를 **채우지 않는다**.
- **(D) marker(ADR-038) 를 liveness signal 재사용**: ADR-038 6-point marker = best-effort non-blocking (§결정 7), liveness 판정 신뢰층 부적합 → progress-marker 는 output mtime + content grep 별도 관측 (marker≠liveness).

## Consequences

- (+) liveness 축 1급 mandate 확립 — adequacy 축과 직교 방어. #763 Iter4/5 결론-배선 갭 종결.
- (+) SSOT 단일 carrier — 다ADR 걸침(039/081/119/038/115/043/064)을 본 ADR 이 anchor, sibling cross-ref 로 분산 방지.
- (−) max-wait 구체 수치 empirical 미실증 (추정값) — env-override + Phase 2 관측 후 조정. consumer overlay 는 보수 방향(max-wait 축소)만, 무한대 재정의 차단 hardcap 권고.
- (−) 2안 lint = warning-tier — blocking 승격은 ADR-060 evidence-gate(PR 누적 ≥20 + bypass 외 failure 0 + sibling merged) 후.
