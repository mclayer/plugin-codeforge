---
adr: ADR-139
adr_number: 139
category: governance
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
  - ADR-054  # 신규 ADR 도입 = full-lane 강제 — 본 ADR 신규 carrier 정당화 실 근거지 (new-vs-amendment 기준)
  - ADR-064  # §결정 7 evidence-gated symmetric ratchet — 강화 방향 보조 근거 (신규-carrier 기준 아님; §결정 1 = 4-어휘 운영 정의로 new-vs-amendment 기준 부재 → ADR-054 참조)
  - ADR-060  # warning-tier lint 승격 evidence-gate — 2안 presence lint tier
  - ADR-061  # §결정 1 Python-SSOT + thin shell wrapper — 2안 lint 구조 패턴
amendments:
  - amendment_id: 1
    date: "2026-07-05"
    carrier_story: CFP-2573
    issue: https://github.com/mclayer/plugin-codeforge/issues/2573
    summary: |
      §결정 4 (1안 강제층) delivery-gap 규율 강화 (§결정 7 신설) — ADR-144 §결정 4(L3) realization. delivery-gap(P10) = stop taxonomy 축 B(liveness, 비의지적 mechanical stall)로 재확인(대화 축 아님, ADR-144 §결정 1 ★핵심 경고). 강화 내용: (i) 구조 규율 "PL 은 spawn-then-blind-wait 금지 — 수집(collect)은 auto-wake 되는 LEAD 가 소유하거나 LEAD 로 handoff" + named lead-collect routine(interface seam) + PL-background-yield idle detection marker. observer = LEAD(hook 아님). stall = wall-clock ceiling AND no-progress-marker(mtime + content + task-notification), 0-byte 단독 ≠ stall(INV-L3 재확인), INV-L2 fail-open 금지(stall ≠ PASS). (ii) full auto-wake-parent dispatcher(env=1)는 substrate 부재 + ADR-142 §결정 6 fresh DEFER + /resume in-process teammate 미복원 → narrative DEFER-escalate(recurrence anchor L3-delivery-gap::(a), ≥2 Story 재-제안 시 escalate, 자동 followup 발의 안 함). 정직 앵커 — 본 Story 세션 delivery-gap force-resume 5~6회 재현(falsifiable), 자동 교정 주장 안 함. 인프라 신규 불요(CFP-2549 substrate 기배선, 문구 강화만). tier = detection [measurement] + recovery [advisory](lead-owned discretionary), [물리강제] 아님(SubagentStop record-only ADR-115 §결정 2 + INV-L4 lead 판정). 강화(ratchet↑) 방향 — INV-L1~L4 · detection≠recovery · 2안 presence lint 전부 무변경, 신규 §결정 1개 추가만.
    sunset_justification: null   # 강화 방향 (background-yield 규율 강화 = forcing function 추가 ratchet) — ADR-058 §결정 5 약화 evidence-gate 비대상. INV-L1~L4 무손상.
  - amendment_id: 2
    date: "2026-08-11"
    carrier_story: CFP-2929
    issue: https://github.com/mclayer/plugin-codeforge/issues/2929
    summary: |
      §결정 8 신설 — (i) INV-L4 값 순서 불변식의 정의역을 2-timer(timeout N / liveness max-wait)에서
      4계층(harness 도구 호출 수명 A / GNU timeout N+K / liveness max-wait C / late-collect 부재 판정 하한 D)으로
      확장하고 "내측이 외측 잔여 예산에서 파생" 규칙을 명문화 (Google SRE Book Ch.22 deadline propagation (b)(c) 앵커).
      ★ A 는 고정 상한이 아니라 호출별 파라미터(default 120s / max 600s)임을 정정 기재 — 내측 가드는 도달 불가가 아니라
      A_eff 를 명시 전달하지 않은 것이 결함이다. (ii) §결정 7(i) 의 "named lead-collect routine(interface seam)" 을
      codex dispatch 경로에 실현 — 고정 경로 dispatch manifest(claim-check) + LEAD 호출 named routine.
      §결정 7(ii) full auto-wake-parent dispatcher DEFER 무변경(recurrence anchor L3-delivery-gap::(a) 유지) —
      본 routine 은 LEAD 가 호출하는 discretionary seam 이지 자동 기상 장치가 아니다. ADR-115 C2 record-only 무손상.
      (iii) OP-1 부재 판정 하한 신설 — dispatch_start + N + K + margin 이전의 산출물 부재는 INV-L3 3-state 의
      '미획득(in-flight)' 이지 stall 이 아니며 재dispatch 를 금지한다(2-state 접기 = false-positive 조기 회수, §결정 3 정합).
      (ii-b) 고정 경로 claim-check 의 필수 동반 통제 3층 명문화 — 좌표 고정은 회차 귀속을 상실시키므로
      (1) 슬롯 강제 비움 (2) 판정 입력의 dispatch 귀속 (3) 호출자 제공 하한 을 함께 요구한다. 자기참조 신선도 검사는
      manifest 자신의 staleness 를 원리적으로 검출하지 못한다(외부 기준점 필수).
      INV-L1~L4 문면·detection≠recovery·2안 presence lint 전부 무변경 — 신규 §결정 1개 추가 + 정의역 확장만.
    sunset_justification: null   # 강화 방향 (정의역 확장 + seam 실현 + false-positive 하한 추가 = ratchet↑) — ADR-058 §결정 5 약화 evidence-gate 비대상. INV-L1~L4 무손상.
    reinterpretation: false  # ADR-167 §결정 1(b) parity marker (신규 entry 필수 필드) — INV-L1~L4 문면·detection≠recovery·2안 presence lint 무변경, 신규 §결정 8 append + INV-L4 정의역 확장(적용 대상 추가)이지 §결정 1-7 본문 의미의 소급 재해석 아님. self-declared, 진위 = 리뷰 판정 축(parity lint 는 presence/type 만 검사). effective_count(heading 0 / fm entry 2) = 2 < N=10 → 재제정 트리거 무발동.
---

# ADR-139: background-wait liveness gate

## 상태

Accepted (2026-07-02, carrier CFP-2549, dogfood wrapper-self).

## 컨텍스트

codeforge Orchestrator/lane-PL 이 background subagent/worker 응답을 기다릴 때 **wall-clock 상한 + liveness 관측이 없으면 stall 이 무한 대기로 번진다.**

CFP-2545 (ADR-081 Amendment 12 §결정 D14) 가 codex-companion 브로커 경로(`node codex-companion.mjs adversarial-review --wait`)의 무한 대기를 wall-clock ceiling + fail-open 금지 + Orchestrator liveness 게이트로 해소했으나, 이는 **한 인스턴스**일 뿐이다. 근본 문제는 **모든 codeforge-owned background subagent 대기**에 존재한다.

**의존 체인 (결론-배선 갭)**: CFP-750 (Iter4 ~2h silent hang) → #763 (Iter5 3후보 `background-task-liveness-gate` + `agent-non-response-timeout` + `passive-work-detection` **발의만·미배선**) → CFP-2545 (§D14 codex-companion 만 배선) → **CFP-2549 (전 subagent 일반화)**. 재발 근본 = 결론냈으나 mechanical hook 미배선.

**직접 증거 (firsthand — CFP-2545 실행 세션 + 본 CFP-2549 요구사항/설계 lane 자체)**:
- lane PL background-yield 반복: 자식 spawn 후 "턴 종료" → parent(PL) 무한 정지 구조. 자식 완료 통지가 parent 아닌 lead(main) 로 surface (ADR-039 §결정 19 구조적 한계).
- DeveloperAgent 0-byte output → stall 오판 (실제 완주 중).
- **본 CFP-2549 설계 lane 실증**: ArchitectPL 이 6 deputy fan-out 후 background-yield → 6 deputy 중 4 가 lead 로 delivery-gap surface, PL context 미도달 → lead 개입(force-resume/조립) 필연. 본 Story 의 존재 이유를 설계 lane 이 자기 재현.

**contract-level 공백 (핵심 구현 gap)**: `docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md` §6.3 `pl_integration_review.worker_outcomes: list # [PASS | FIX-N | CRASH]` — **INCONCLUSIVE/STALL verdict value 부재**. 같은 §6.3 주석 "crash recovery / fail-mode protocol = 별도 CFP follow-up scope" 로 timeout/fail-mode protocol 을 명시 defer. CFP-2549 = 그 deferred follow-up carrier.

## 두 직교 축 (본 ADR 의 도메인 근거)

| 축 | 질문 | 실패 형태 | SSOT |
|---|---|---|---|
| **adequacy(충분성)** — hollow-gate | 게이트가 *충분히* 검사하는가 | reached-but-dead / green-but-dead | ADR-060 |
| **liveness(생동성)** — 본 ADR | 대기/게이트가 *유한 시간* 내 결론에 도달하는가 | stall / 무한 대기 | 본 ADR-139 |

직교성(상호 미함의): adequate-but-not-live (완벽 커버해도 deadline 부재로 stall) / live-but-not-adequate (5초 유한 종료해도 대상 미검사 = hollow). 한 축 방어가 다른 축 미대체 → **별도 1급 mandate 필요** = 본 신규 ADR carrier 근거 (ADR-054 신규 ADR 도입 = full-lane 강제 — 직교 1급 신개념 + 다ADR 걸침 SSOT 산란 방지. ADR-064 §결정 1 은 4-어휘 운영 정의로 new-vs-amendment 기준 부재 — 신규-carrier 근거지 아님; §결정 7 evidence-gated ratchet 만 강화 방향 보조).

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

`parallel-dispatch-protocol-v1.md` §6.3 `worker_outcomes` enum 에 **INCONCLUSIVE** value 추가 (`[PASS | FIX-N | CRASH | INCONCLUSIVE]`) + timeout/fail-mode protocol 최소 섹션(background-wait liveness gate 4 불변식 cross-ref) 신설. §6.3 주석의 "crash recovery / fail-mode protocol = 별도 CFP follow-up scope" defer 를 CFP-2549 로 해소. registry MINOR bump (v1.0 → v1.1, kind:registry sibling_sync_exempt 유지 — ADR-008/ADR-010 registry 면제).

### 결정 6 — sibling Amendment set (doc-only, 본 ADR-139 Phase 1 PR 동봉 가능)

본 ADR-139 이 carrier SSOT 이나, 인접 ADR 에 cross-ref Amendment 동반 (전부 강화 방향 doc-only, src/tests 무변경):

| ADR | Amendment | 내용 |
|---|---|---|
| ADR-081 | Amendment 13 | §D14 (companion 특정) → ADR-139 cross-ref (companion 은 background-wait liveness gate 의 first instance 임을 declare, §D14 본문 무변경) |
| ADR-039 | Amendment 10 (§결정 20 신설) | background subagent spawn liveness = ADR-139 cross-ref (§결정 19 lead force-resume/TaskStop 개입 축의 정량 게이트化 — §결정 9 slot 침범 아님, 신규 §결정 20). §결정 2 inline whitelist 6-entry 무손상, §결정 1 binary always-spawn 무변경 |
| ADR-115 | (선택) §결정 1 hook tier 표에 "background subagent liveness = spawn-gate(PreToolUse Agent) 계층 + SubagentStop record-only 무손상" 1줄 cross-ref | SubagentStop block 금지 invariant 재확인 |
| ADR-119 | (선택) §결정 10 fail-open 금지 → ADR-139 INV-L2 instantiation cross-ref | origin SSOT 명시 |

### 결정 7 — PL background-yield no-blind-wait discipline (Amendment 1, CFP-2573)

> **[Amendment 1 / CFP-2573, 2026-07-05 KST]** ADR-144(stop taxonomy) §결정 4(L3) realization. delivery-gap(P10) 은 stop taxonomy **축 B(liveness — 비의지적 mechanical stall)** 이지 축 A(대화)가 아니다(ADR-144 §결정 1 ★핵심 경고). 대화규칙("묻지 마")으로 고치면 무효 — 본 §결정 4 규율(1안 강제층)로만 해소. 본 §결정 7 = §결정 4 의 delivery-gap 면 강화(재발명 아님 — CFP-2549 substrate 기배선, 문구 강화).

**(i) realizable NOW — 구조 규율 codify**:

- **PL 은 spawn-then-blind-wait 금지**. 자식을 spawn 하고 background-yield 한 뒤 결과 수집을 blind 하게 기다리는 형상 = delivery-gap 진원(자식 완료 통지가 parent 아닌 lead 로 surface, ADR-039 §결정 19 구조한계). 수집(collect)은 **auto-wake 되는 LEAD 가 소유**하거나 LEAD 로 handoff 한다(structured-concurrency nursery 정설 — 부모가 소유+수집, ADR-139 §결정 2 정합).
- **named lead-collect routine(interface seam)**: 대기/수집 지점을 명명된 lead-owned 루틴으로 표면화 — PL 이 turn-yield 하는 지점에 "누가 이 background 작업을 collect 하는가" 를 명시 seam 으로 둔다(암묵 blind-wait 금지).
- **PL-background-yield idle detection marker**: PL 이 background-yield 로 idle 진입한 시점을 관측 가능한 marker 로 남긴다(observer = **LEAD**, hook 아님).
- **stall 판정 (INV-L1~L3 상속)**: stall = wall-clock ceiling(시간 축) **AND** no-progress-marker(진행 축 = output mtime + content grep + task-notification). **0-byte stdout 단독 ≠ stall**(INV-L3 — 완주 중 0-byte 가능). **INV-L2 fail-open 금지** — stall ≠ PASS, verdict == "PASS" 명시 문자열일 때만 PASS.
- recovery = **lead force-resume/collect** = lead-owned discretionary(INV-L4). tier = detection `[measurement]` + recovery `[advisory]`, **`[물리강제]` 아님**(SubagentStop record-only ADR-115 §결정 2 무손상).

**(ii) DEFER-escalate (paradigm-scope, 본 Story scope 아님)**: full auto-wake-parent dispatcher(env=1, "타이머 만료 → 자동 SendMessage(parent 깨우기)") 는 substrate 부재 + ADR-142 §결정 6 이 env=1 dispatcher 를 fresh DEFER + `/resume` in-process teammate 미복원. narrative defer 로 chief authority 에 routed. recurrence anchor `L3-delivery-gap::(a)` — ≥2 Story 재-제안 시 escalate. **자동 followup 발의 안 함**(3문 게이트).

**정직 앵커(hollow-gate 금지)**: 본 Story(CFP-2573) 실행 세션에서 delivery-gap force-resume 를 **5~6회 재현**(요구사항 lane 4회 + 리뷰 lane 1~2회, falsifiable 실증 — Story §9.0). ADR-139 기배선에도 parent PL auto-resume 부재 재현 = 본 §결정 7 필요성의 same-session 실증. 본 §결정은 delivery-gap 을 **자동 교정한다고 주장하지 않는다** — force-resume 는 lead-owned discretionary 로 유지된다.

### 결정 8 — 4계층 시간 전순서 + named lead-collect seam 실현 + 부재 판정 하한 (Amendment 2, CFP-2929)

> **[Amendment 2 / CFP-2929, 2026-08-11 KST]** §결정 1 INV-L4 의 **정의역 확장**(2-timer → 4계층)과 §결정 7(i)
> named lead-collect routine 의 **codex dispatch 경로 실현**. INV-L1~L4 문면 무변경 — 본 §결정은 그 위 append 강화다.

**(i) 4계층 전순서 + 파생 규칙 (INV-L4 정의역 확장)**

| 층 | 기호 | 정의 | 소유 |
|---|---|---|---|
| A | `A_eff` | harness 도구 호출 수명 (호출별 파라미터, default 120s / **max 600s**) | 호출자 |
| B | `N`, `K` | GNU `timeout --kill-after=K N` | dispatch 셸 |
| C | `C` | liveness max-wait (stall 판정) | Orchestrator/lead |
| D | `D` | late-collect **부재 판정 하한** | lead collect 루틴 |

전순서: `N < N+K ≤ A_eff ≤ 600s` **∧** `N+K < D = N+K+margin ≤ C`.

**파생 규칙(독립 하드코딩 금지)**: 내측 상한은 외측 잔여 예산에서 파생한다 — `A_eff := N + K + assembly_margin` 을
**호출 시점에 명시 전달**하고, `C := N + K + margin` 으로 도출한다. `N` 을 상수로 두고 `A_eff` 를 방치하면
"명시된 가드가 도달 전에 수집이 끊기는" 형상이 된다.
[source: Google SRE Book Ch.22 Addressing Cascading Failures — Deadline Propagation (b) 내측 = 외측 잔여 예산 파생,
(c) 잔여 부족 시 착수 금지]

★ **정정 기재**: A 를 "고정 120초 상한"으로 읽으면 "내측 가드는 구조적으로 도달 불가" 라는 **거짓 결론**이 나온다.
A 는 호출별 파라미터이며 상한은 600s 다 — 결함은 도달 불가가 아니라 **A_eff 를 전달하지 않은 것**이다.

★ **정직 등급**: `A_eff` 전달은 **도구 호출 인자**이므로 파일 검사로 런타임 준수를 강제할 수 없다 —
**advisory ceiling**(ADR-143 동형). 기계 검증 가능 범위 = 문면 presence + **값 정합**(`N+K+margin ≤ 600` ∧ `N < C`).

**(ii) named lead-collect seam 의 실현 형태**

§결정 7(i) 이 선언한 "named lead-collect routine(interface seam)" 은 **선언만으로는 배선되지 않는다**(declared-not-bound).
실현 형태를 다음으로 고정한다:

- **고정 경로 dispatch manifest** (claim-check) — dispatch 는 **codex 호출 이전에** 자기 산출물 좌표(결과 경로 · 시작 시각 ·
  상한 값)를 lead 가 알 수 있는 **고정 경로**에 기록한다. 셸 내부에서만 생성되는 값(예: `epoch-PID` 파일명)에 결과 좌표가
  갇히면 lead 는 완성된 결과를 **찾을 수 없다**.
- ★ **고정 경로의 대가 = 회차 귀속 상실 (필수 동반 통제)** — 좌표를 고정하는 순간 그 자리의 파일이 **이번 dispatch 것이라는
  보장이 사라진다**(이전 회차 자기 산출물이 잔존). "그 자리에 있으니 이번 것"은 **무근거 등식**이며, 잔재 삼중조가 서로
  내부정합이면 **자기참조 신선도 검사(기준 시각을 그 manifest 에서 읽는 형태)는 원리적으로 무력**하다. 따라서 고정 경로
  claim-check 를 채택하는 구현은 다음 3층을 **함께** 배선해야 한다:
  **(1) dispatch 직전 고정 좌표 슬롯 강제 비움** (실패 = fail-closed, dispatch 미착수)
  **(2) 판정 입력의 dispatch 귀속** (예: exit-code stamp 에 dispatch 식별자 동반 — 불일치·부재 = 판정 입력 미상 = fail-closed)
  **(3) 호출자 제공 회차 토큰의 동등 비교** (lead 가 dispatch 기동 **전에 1회 발급**한 회차 유일 토큰을 **dispatch 와
  collect 양쪽에 같은 값으로** 넘기고, manifest 에 기록된 값과 **일치하지 않으면 거부**) — manifest **자신의**
  staleness 는 manifest 내부 값으로 검출할 수 없으므로 **외부 기준점이 필수**다.
  ★ **기준점은 *시각 하한* 이 아니라 *회차 토큰* 으로 둘 것** — 시각 하한(`dispatch_start ≥ caller 값`) 형태는
  ① 판정이 **순서 추론**이라 "얼마나 이른 값인가"에 좌우되고 ② 그 자유도를 메우려 floor·skew·discriminator 등
  **미실증 상수 군**을 달아야 하며 ③ 호출자가 *그럴듯한 다른 과거값* 을 넘기면 **수락(fail-open)** 된다.
  동등 비교는 셋을 동시에 없앤다 — 위반 시 **불일치 → 거부(fail-closed)** 로 방향이 역전되고 상수가 0 이 된다.
  ★ **토큰 규약을 normative 로 규정할 것** — (a) **dispatch 기동 전 1회 발급** (b) **dispatch 주입값과 collect
  인자가 동일 값** (c) 재호출(replay) 시 **원 회차 값 유지** (d) **회차 간 재사용·collect 시점 재발급 금지**.
  (b)(d) 위반은 수집을 **전건 거부**로 붕괴시키는데, fixture 가 올바른 값을 쓰면 **GREEN 인 채 배포**된다 —
  따라서 **규약 위반을 모사하는 mutant 를 반드시 둘 것**.
  세 층이 덮는 시나리오는 **서로 다르며 대체 불가**다: (1) = 토큰 **규약 위반**(동일 값 재사용) ∧ 비움 이후 사망 /
  (2) = 동일 좌표 경쟁(비움이 이미 지나간 뒤의 뒤늦은 stamp — **같은 회차 두 프로세스라 (3)으로는 못 가름**) /
  (3) = **비움 이전 사망**(비움이 아예 안 돈 경우).
  ★ **정직 declare 의무** — 토큰 **재사용 ∧ 비움 이전 사망** 이 겹친 조합은 **세 층 어느 것도 덮지 못한다**.
  토큰 값의 회차 유일성은 호출자 책임이며 **기계 강제 불가(advisory)** 다(형식 검증은 값의 *신선함* 을 보지 못한다).
  동등 비교로 **위반형이 "verbatim 재사용" 하나로 좁아지지만 제거되지는 않는다** — 이 잔여를 "완전 봉인" 이나
  "구성적 폐쇄" 라 적지 않는다.
- **LEAD 호출 named routine** — 수집은 이름 붙은 lead-owned 루틴으로 표면화한다. 이 루틴은 **discretionary** 이며
  **자동 기상 장치가 아니다**. §결정 7(ii) full auto-wake-parent dispatcher 는 **DEFER 유지**
  (recurrence anchor `L3-delivery-gap::(a)`, ≥2 Story 재제안 시 escalate).
- **소비의 멱등성** — 결과 소비는 원자적 rename 등으로 **최대 1회**임이 구조적으로 보장돼야 한다.
  ★ **그 rename 의 반환값을 검사할 것** — 미검사 rename 위에 세운 "최대 1회" 는 **실패 시 조용히 거짓**이 되며,
  봉인되지 않은 산출물은 다음 회차의 잔재 전건이 된다. 실패에 **명명된 fail-closed 처분**을 둔다.
- **좌표 파일의 write 는 원자적일 것** — 고정 좌표 manifest 를 평문 리다이렉트로 쓰면 "write 중 사망 = 절단 레코드"
  상태를 **스스로 만든다**. temp+rename 으로 그 상태를 애초에 만들지 않는다(상태를 만든 뒤 분기를 늘리는 것보다 낫다).
- **collector 가 소비하는 수치 필드는 *첫 산술 이전* 에 타입·자릿수를 결박할 것** — 상한 없는 정수 술어는
  셸 비교(`[ -lt ]`/`[ -gt ]`)에서 **rc=2 를 내고 `else` 로 흘러 fail-open** 이 되며, 산술 확장 대안은 **silent wrap** 한다.
- **판정 authority 단일** — inline 경로와 late-collect 경로는 **동일한 재검증 helper·동일한 verdict 판정 규칙**을 공유한다.
  두 벌 구현은 fail-open 우회로가 된다. 판정 입력(예: 자식 exit code)이 late-collect 시점에 **미상**이면
  **fail-closed inconclusive** — 미상을 PASS 로 해석하지 않는다(INV-L2 상속).
- tier = detection `[measurement]` + recovery `[advisory]`, **`[물리강제]` 아님** (ADR-115 §결정 2 record-only 무손상).
  collect 을 blocking 물리강제로 요구하는 것은 ADR-115 C2 위반이다.

**(iii) 부재 판정 하한 (false-positive 조기 회수 방지 — §결정 3 정합)**

산출물 **부재**를 stall 로 판정할 수 있는 최소 시각을 명시한다:

```
부재-stall 판정 하한 D = dispatch_start + N + K + margin
```

- `D` **이전**의 부재는 INV-L3 3-state 의 **'미획득(in-flight)'** 이며 **stall 이 아니다** → **재dispatch 금지**.
- 근거: 호출부 `timeout` 이 자식의 **직접 부모**일 때 `--kill-after=K` 경과 시점에 종료가 보장되므로,
  late-write 지평은 `N+K` 로 유계다.
- ★ 3-state 를 2-state("실재 → 수집 / 부재 → stall")로 접는 절차는 **INV-L3 위반**이며,
  §결정 3 이 막으려던 false-positive 조기 회수를 그대로 재생산한다.

**정직 앵커(hollow-gate 금지)**: 본 Amendment 의 (ii)(iii)은 실 사례로 발동됐다 — CFP-2929 요구사항 lane 에서
리뷰 워커의 **비자발적 백그라운드 이동이 4회** 발생했고 **그중 1회가 그 워커의 오단정을 유발**했다(결과가 실재하는데
소비되지 않아 판정까지 오염). 본 §결정은 delivery-gap 을 **자동 교정한다고 주장하지 않는다** —
collect 은 lead-owned discretionary 로 유지된다.

## 거절된 대안

- **(A) ADR-039 Amendment 10 (§결정 20) carrier**: §결정 19(lead-intervention)는 spawn-topology 축이고 liveness 정량 게이트는 별도 축 → §결정 20 신설해도 ADR-039 scope(subagent-default spawn) 초과. spawn-권한 기반으로만 cross-ref (Amendment 10 은 sibling 으로 채택 — 아래).
- **(B) ADR-081 Amendment 13 (§D14 generalize) carrier**: ADR-081 = Codex worker prompt boilerplate + invocation SSOT scope. 일반 subagent(harness-managed, prompt boilerplate 무관)엔 scope mismatch. §D14 pattern 일반화 cross-ref 만 sibling 으로 채택.
- **(C) 기계 훅(PreToolUse/SubagentStop) blocking 강제**: hooks.json 에 **PreToolUse "Agent" matcher → `pretooluse-agent-spawn-gate` 훅 존재** (origin/main 실측) — 그러나 이는 **spawn 시점** 게이트라 **wait-elapsed 축 부재** (대기 *중* liveness 판정 불가). SubagentStop = async false **record-only** (ADR-115 §결정 2 — Stop/SubagentStop `block(continue)` = platform 결함으로 신뢰 불가, GitHub #10412/#55754 evidence, block 절대 금지). PostToolUse 부재. ADR-039 §결정 9 advisory 천장("완주중 무출력 vs hang" semantic 구별 불가). → 2안 presence lint 는 warning-tier 정적층만, blocking 강제 아님. **§결정 9 slot 침범 금지** (아래).
- **(E) ADR-039 §결정 9 hook slot 채움**: §결정 9 deferred slot = "Orchestrator inline write detect hook (PreToolUse on Write/Edit/mcp__github__*)" — **inline-write-detect 축**이지 background-wait liveness(완료 감지) 축이 아니다 (완전 별개 축). §결정 9 에 liveness 게이트를 밀어 넣으면 scope 오염 → 이후 진짜 inline-write-detect hook 구현 시 confusion. 본 ADR liveness 원리는 §결정 9 를 **채우지 않는다**.
- **(D) marker(ADR-038) 를 liveness signal 재사용**: ADR-038 6-point marker = best-effort non-blocking (§결정 7), liveness 판정 신뢰층 부적합 → progress-marker 는 output mtime + content grep 별도 관측 (marker≠liveness).

## 결과

- (+) liveness 축 1급 mandate 확립 — adequacy 축과 직교 방어. #763 Iter4/5 결론-배선 갭 종결.
- (+) SSOT 단일 carrier — 다ADR 걸침(039/081/119/038/115/043/064)을 본 ADR 이 anchor, sibling cross-ref 로 분산 방지.
- (−) max-wait 구체 수치 empirical 미실증 (추정값) — env-override + Phase 2 관측 후 조정. consumer overlay 는 보수 방향(max-wait 축소)만, 무한대 재정의 차단 hardcap 권고.
- (−) 2안 lint = warning-tier — blocking 승격은 ADR-060 evidence-gate(PR 누적 ≥20 + bypass 외 failure 0 + sibling merged) 후.

## 관련 파일

- `docs/orchestrator-playbook.md` — 1안 강제층(background-wait liveness 공통 규약 + §3.10/§4.5.2 cross-ref) 배선 대상 (Phase 2)
- `scripts/lib/liveness_check_base.py` + `scripts/lib/check_subagent_wait_liveness_presence.py` + `scripts/check-subagent-wait-liveness-presence.sh` (thin wrapper, ADR-061 §결정 1) — 2안 정적 회귀층 lint (Ports&Adapters, Phase 2)
- `tests/scripts/test_check-subagent-wait-liveness-presence.sh` — §8 execution-backed self-test (Phase 2)
- `docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md` — §6.3 worker_outcomes INCONCLUSIVE enum + fail-mode 섹션 (v1.0→v1.1, Phase 2)
- `archive/adr/ADR-081-codex-worker-prompt-boilerplate.md` §결정 D14 — 본 ADR 이 일반화하는 codex-특정 선례
- `archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md` §결정 19 — lead-intervention anchor
- `archive/adr/ADR-119-research-before-claims.md` §결정 10 — fail-open 금지 origin SSOT (상속)
- `docs/orchestrator-communication-incidents.md` Iter 4/5 — #763 재발 arc evidence
- `plugins/codeforge-review/agents/CodexReviewAgent.md` — dispatch manifest + rc stamp (§결정 8 (ii) claim-check 실현, CFP-2929)
- `plugins/codeforge-review/scripts/codex-late-collect.sh` — named lead-collect routine (§결정 8 (ii), CFP-2929)
- `plugins/codeforge-review/templates/review-pl-base.md` §10 — collect = LEAD 소유 규범이 named routine 을 지목 (CFP-2929)
