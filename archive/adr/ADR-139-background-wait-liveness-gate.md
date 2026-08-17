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
  # ★ Amendment 2 = CFP-2929 예약 (브랜치 `origin/cfp-2929-codex-dispatch-collection`, open PR #2955 — 커밋 `8eabf3d8a`
  #   [CFP-2929] Phase 2(구현) T0: ADR-139 Amendment 2 (§결정 8) 가 선점). 본 Amendment 3 은 그 slot 을 양보하고 다음 번호를 쓴다.
  #   renumber 요구 안 함 — ADR-082 Amd36 1-Y §A ascending 정렬만 의무 (선례 = ADR-141 Amd 10).
  - amendment_id: 3
    date: "2026-08-18"
    carrier_story: CFP-2994
    reinterpretation: false  # ADR-167 §결정 1(b) — 순수 additive. INV-L1~L4 · §결정 1~7 · detection≠recovery · 2안 presence lint 전부 본문 문언 무변경이며, 본 Amendment 는 이 ADR 이 **다루지 않았던 객체**(수령 사실)를 처음 규정한다(신규 객체 축 첫 entry). ★ 특히 A3-3 이 성문하는 바가 정확히 「재해석 아님」이다 — 반증된 것은 §결정 7 이 **말한 적 없는** 암묵 추론이지 §결정 7 의 의미가 아니며, 그래서 문면을 *"ADR-139 가 틀린 전제를 깔았다"* 가 아니라 *"ADR-139 가 침묵한 경계선에서 오적용이 발생했다"* 로 고정했다. self-declared, 리뷰 판정 축 (parity lint 는 presence/type 만 검사).
    direction: strengthen
    issue: https://github.com/mclayer/plugin-codeforge/issues/2994
    summary: |
      **P-1(수령 사실의 single-writer) ↔ INV-L4 정의역 분리** — 신규 객체 축의 첫 entry(약화 아님).
      (A) **축자 모순 0** — INV-L4 축자는 스코프를 *"liveness 게이트"* 로 자기 한정하고 「수령/inbox」 어휘 0건 `[verified]`
      ⇒ 본 건과 축자 모순 없음. INV-L1~L4 · §결정 1~7 · detection≠recovery · 2안 presence lint 전부 **무변경**.
      (B) **분리선 = verdict ↔ 수령**. verdict = 유인 有 · **타자 검증 가능** ⇒ INV-L4 의 LEAD 판정 권한 정당.
      수령(receipt) = 유인 無 · 타자 검증 **물리적으로 불가**(상대 inbox 열거 수단 부재) ⇒ 소유자만 기록자.
      두 객체가 disjoint 하므로 본 Amendment 는 INV-L4 를 완화하지 않고 **다루지 않던 객체를 처음 규정**한다
      (ADR-064 §결정 7 evidence-gated symmetric ratchet — 강화 방향).
      (C) ★ **정밀화 — 본 Story 초판 전제도 반증됐다** `[verified]`: *"LEAD 시야가 더 완전"* 이라는 문구는 §결정 7 전문에
      **아예 없다**(해당 어휘 0건). §결정 7 의 근거는 nursery 패턴(부모가 소유+수집)뿐이다. ⇒ 정확한 문면 =
      *"ADR-139 가 틀린 전제를 깔았다"* 가 **아니라** *"ADR-139 가 침묵한 경계선에서 오적용이 발생했다"*.
      암묵 추론 사슬(collect 소유 = LEAD ⇒ LEAD 시야 = 완전 ⇒ receipt 까지 override)의 인과 태그 = `[hypothesis]` **유지**
      (확정 승격 근거 미발견).
      (D) **경계 3항** — ① INV-L4 객체 표 verbatim 인용 + 무변경 declare ② `receipt_state` = **도달 전용**
      (존재·귀속 허용 / 충분성·품질 금지 — 함의가 붙는 순간 INV-L4 침범) ③ depth ≥ 1 에서 **전 주체가 worker ∧ receiver 를
      겸한다** ⇒ disjointness 를 규범 문구가 아니라 **산출물 schema** 가 지킨다.
      (E) **CFP-2929 Amd 2 §결정 8 과 semantic disjoint** — 그 Amendment 는 §결정 7(i) named lead-collect seam 의
      **배선(mechanism)** 축이고 본 Amendment 는 seam 이 **무엇을 재정할 수 있는가(authority)** 축이다. 「수령/inbox/통지 도달」
      어휘 0건 `[verified]`. 같은 §결정 7 을 참조하나 **반대 방향이 아니다** — 오독 차단용 cross-ref.
      (F) **amendment slot 충돌 오라클 교훈** (본 건 발생지) — 3 오라클이 각자 실재 claim 을 놓쳤다: registry 미등재 ·
      open PR 없는 미머지 브랜치 · 컨테이너/항목 키 dialect 이원성. 유일 건전 오라클 = **커밋 축**
      `git log --all --not origin/main -- <adr-path>`. 정직 한계 = fetch 신선도 의존 ∧ 미푸시 로컬은 정의역 밖 ⇒
      **"origin 반영분 전수"** 로만 declare, **"collision-free 확정" 금지**.
      (G) **라우팅 기전 판별 불가 유지** — 통지 라우팅 분할 기전 후보 3종은 판별 열쇠(「조상 생존 중 손자 완료」 대조 관측)가
      4 iteration 전부 부재하여 **확정 승격 금지**. §결정 19(ADR-170) stall 마찰 정직 기술과 동일 등급.
    sunset_justification: null   # 강화 방향 (신규 객체 축[수령 사실] 첫 entry 추가 = ratchet↑, INV-L1~L4 완화 0) — ADR-058 §결정 5 약화 evidence-gate 비대상.
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

## Amendment 3 (CFP-2994 — P-1 수령-사실 single-writer ↔ INV-L4 정의역 분리)

> **[Amendment 3 / CFP-2994, 2026-08-18 KST]** 축 = **authority**(누가 어떤 사실의 기록자인가). 본 Amendment 는
> **INV-L1~L4 · §결정 1~7 · detection ≠ recovery · 2안 presence lint 를 1 byte도 변경하지 않는다.** 추가되는 것은
> 본 ADR 이 지금까지 **다루지 않았던 객체**(수령 사실)에 대한 첫 규정이다. carrier = CFP-2994.
>
> ★ **CFP-2929(Amendment 2, §결정 8)와 disjoint** — 그 Amendment 는 §결정 7(i) named lead-collect seam 의 **배선(mechanism)**
> 축이고, 본 Amendment 는 그 seam 이 **무엇을 재정할 수 있는가(authority)** 축이다. 두 Amendment 가 같은 §결정 7 을 참조하나
> **반대 방향이 아니다.** 근거 = CFP-2929 Amd 2 문면에 「수령 / inbox / 통지 도달」 어휘 0건 `[verified — 커밋 8eabf3d8a 문면 대조]`.

### A3-1 — 축자 모순 0 (선결 확인)

CFP-2994 요구사항 lane 이 *"P-1 ↔ INV-L4 정면 충돌"* 로 접수했으나, **축자 모순은 없다** `[verified]`:

> **INV-L4 (게이트 소유 = Orchestrator/lead 고정)**: liveness 게이트 개입 주체 = Orchestrator/lead. worker 자가-spawn 금지
> (`plugins/codeforge-review/CLAUDE.md:46` "워커는 직접 다른 subagent 스폰 불가"). 대기 주체 ↔ 판정 주체 분리
> (worker self-attestation 차단, 신뢰 경계). 값 순서 불변식: `timeout N < liveness max-wait` (호출부 timeout 이 먼저 터져
> marker 를 남기고 게이트가 그 이후 관측 — 역순 금지).

— 본 파일 **`## 결정` 절 `**INV-L4 (게이트 소유 = Orchestrator/lead 고정)**` 항** **verbatim 인용, 무변경 declare**.
대조 규칙 = `git grep -n '대기 주체 ↔ 판정 주체 분리' -- archive/adr/ADR-139-*.md`
(위 blockquote 안의 `plugins/codeforge-review/CLAUDE.md:46` 는 **인용 대상 원문의 일부**이므로 손대지 않는다 — 무변경 declare 준수).

★ **행 번호 앵커 금지 (자기 사례)**: 초판은 이 자리를 `…-gate.md:71` 로 앵커했고, **같은 브랜치의 형제 hunk**(Amendment 3 블록
자신의 삽입)가 그 행을 밀어내 포인터가 거짓이 됐다 — 현 `:71` = `## 상태` 절 `Accepted (…)` 줄. **인용 내용은 참**이었고
(INV-L4 축자 일치 · 삭제 0줄) **포인터만 거짓**이었다. 규약 = §A3-8.

축자가 스코프를 *"liveness 게이트"* 로 **자기 한정**하고 「수령 / inbox」 어휘가 0건이므로, INV-L4 는 본 건이 다루는 객체에 대해
**아무 말도 하지 않는다**. 충돌은 축자가 아니라 **암묵 추론**에서 발생했다(A3-3).

### A3-2 — 분리선 = **verdict ↔ 수령**

| 객체 | 유인 | 타자 검증 가능성 | ⇒ 기록자 |
|---|---|---|---|
| **verdict** (성과 판정 · liveness 판정) | 있다 (자기 유리하게 진술할 동기) | **가능** — 산출물·marker·rc 로 대조 | **LEAD** (INV-L4 정당) |
| **receipt** (수령 사실) | 없다 (자기 수령을 부정할 동기 부재) | **물리적으로 불가** — 상대 inbox 열거 수단 부재 | **수신 주체 단독** |

두 객체는 **disjoint** 하다. 따라서 「수령 사실의 기록자 = 수신 주체」 규정은 INV-L4 의 **예외가 아니라 그 정의역 밖의 신설
entry** 다. 어떤 worker 도 본 규정을 통해 **자기 성과 verdict 권한을 얻지 않는다** — ADR-102 · ADR-058 §결정 5 저촉 없음.

**방향성 정직 기술**: 이 분리로 **약화되는 것은 없고**, 규정되는 것은 지금까지 어느 주체도 소유하지 않던 사실뿐이다
(ADR-064 §결정 7 symmetric ratchet 상 **강화 방향**).

### A3-3 — 정밀화: ADR-139 은 **틀린 전제를 깔지 않았다** — 침묵한 경계선에서 오적용이 났다

★ CFP-2994 초판은 *"§결정 7 이 「LEAD 시야가 더 완전」을 미명시 전제로 깔았고 본 건이 그것을 반증한다"* 로 적었다.
**그 문구는 §결정 7 전문에 아예 없다** `[verified — 해당 어휘 0건]`. §결정 7 이 제시한 근거는 **nursery 패턴**
(*"structured-concurrency nursery 정설 — 부모가 소유+수집"*) **하나뿐**이다.

⇒ **정확한 문면**:

- ✗ *"ADR-139 가 틀린 전제를 깔았다"*
- ✓ *"ADR-139 가 침묵한 경계선에서 오적용이 발생했다"*

오적용의 추론 사슬 = `collect 소유 = LEAD` ⇒ `LEAD 시야 = 완전` ⇒ `receipt 까지 override 가능`. 두 번째·세 번째 화살표는
**ADR-139 이 발화한 적 없다**. 인과 태그 = **`[hypothesis]` 유지** — 이 사슬이 실제 오적용의 원인이었다는 것은 사후 재구성이며
확정 승격 근거를 찾지 못했다.

★ 이 정정 자체가 CFP-2994 의 지배 결함 class(*"검사 정의역이 주장 범위와 어긋난다"*)의 발현이다 — 초판은 **실재하지 않는 문구를
반증 대상으로 지목**했다.

### A3-4 — 경계 3항 (성문)

**(i) INV-L4 무변경 declare** — A3-1 의 verbatim 인용이 정본이며 본 Amendment 는 그 4 객체(개입 주체 / worker 자가-spawn 금지 /
대기↔판정 분리 / 값 순서 불변식)를 **손대지 않는다**.

**(ii) `receipt_state` = 도달(arrival) 전용** — 허용 = 산출물 도달 여부 · 도달 채널 귀속 · 판정 근거. **금지 = 충분성 · 품질 ·
채택 가치**. 「받았다 ⇒ 쓸 만하다」 함의가 붙는 순간 그 field 는 성과 verdict 가 되고 INV-L4 를 침범한다. paired = ADR-170
Amendment 2 §A2-4.

**(iii) depth ≥ 1 에서 전 주체가 worker ∧ receiver 를 겸한다** — lane PL 은 Orchestrator 에 대해 worker 이면서 자기 SubAgent 에
대해 receiver 다. 따라서 **「worker 는 판정하지 않는다」와 「receiver 만 수령을 기록한다」가 같은 주체에게 동시에 걸린다.**
⇒ disjointness 를 **규범 문구로는 지킬 수 없다**(겸직을 금지할 방법이 없다). 지키는 표면은 **산출물 schema** 다 — 수령 기록
field 와 verdict field 를 **서로 다른 field 로 분리**하고 각 field 의 기록자를 field 단위로 고정한다. 규범은 그 schema 를
요구할 뿐 겸직을 막지 않는다.

### A3-5 — amendment slot 충돌 오라클 교훈 (본 건 발생지)

본 Amendment 의 번호 확정 과정에서 *"양측 amendment 0건"* 초기 단정이 **ADR-139 에서 거짓**이었다. 충돌 검출 오라클 3종이
**각자 실재하는 claim 을 놓쳤다**:

| # | 오라클 | 놓친 것 | 협착 기전 |
|---|---|---|---|
| O-1 | `ADR-RESERVATION.md` `amendments_reserved[]` 조회 | **양 claim 전부** | registry 는 **등재된 것만** 안다 — 미준수가 registry 를 조용히 stale 로 만든다 |
| O-2 | open PR 열거 | **cfp-2948** (원격 브랜치 실재 ∧ open PR 없음) | 정의역 = *"PR 이 열린 작업"* — PR 없는 미머지 브랜치는 정의역 밖 |
| O-3 | frontmatter 단일 키 grep | **ADR-139 의 기존 Amd 1** | corpus 에 키 dialect 이원성 — 컨테이너(`amendment_log` ⊥ `amendments`) ∧ 항목(`- amendment:` ⊥ `- amendment_id:`). ★ 본 건 두 carrier 가 정확히 서로 다른 형식을 쓴다 |

**유일하게 건전했던 오라클 = 커밋 축 sweep**:

```
git fetch origin && git log --all --not origin/main --oneline -- archive/adr/ADR-NNN-<slug>.md
```

dialect 무관 · PR 유무 무관. registry · open-PR 은 **corroboration** 으로만 쓴다.

★ **정직 한계 (over-claim 금지)**: 커밋 축도 `--not origin/main` 기준이라 **(a) origin fetch 신선도에 의존**하고
**(b) 미푸시 로컬 브랜치는 정의역 밖**이다. ⇒ 산출 가능한 진술은 **"origin 반영분 전수"** 뿐이며 **"collision-free 확정" 은
말할 수 없다**. 이것이 본 Story 가 추적하는 class 의 자기 적용이다 — 오라클의 정의역을 그 오라클의 주장 범위와 일치시킨다.

**배선 발의 아님** — 위 3-오라클 합집합을 기계 검사로 배선하는 것은 `ADR-133 A1-5`(EC-4 amendment_id slot = deferred)가
**의도적 비용/편익 유예**로 이미 declare 했고 `ADR-082 Amd17 Wave-2` follow-up 이 추적 중이다. 데이터포인트 2건으로 그 유예를
뒤집을 근거가 부족하므로 **신규 Issue 발의 0** — 절차 gotcha 기록에 그친다.

### A3-6 — 라우팅 기전: 판별 불가 유지 (정직 천장 — 승격 금지)

원 사건에서 SubAgent 완료 통지가 두 갈래로 갈린 **기전**은 규명되지 않았다. 후보 3종(스폰 방식 / 백그라운드 여부 / 에이전트
종별 등)의 **판별 열쇠 = 「조상 생존 중 손자 완료」 대조 관측**이며 그 관측은 **4 iteration 전부 부재**하다.
⇒ **확정 승격 금지.** 본 Amendment 의 규정(A3-2)은 기전과 **독립**이다 — 관측 비대칭을 전제로 한 방어이므로 기전 미상인
상태에서도 무해하지만, **기전이 밝혀지면 더 싼 근본 처방이 나올 수 있다**. ADR-170 §결정 19 의 stall 마찰 정직 기술과 동일 등급.

### A3-7 — 부수: provenance 정정 회부 (본 Amendment 는 편집하지 않음)

본 ADR frontmatter `related_adrs` 의 `ADR-054  # ... (new-vs-amendment 기준)` 주석은 **ADR-054 가 그 기준을 담지 않는다**는
점에서 오귀속이다 `[verified — ADR-054 = Story 처리 flow(doc-only fast-path) ADR]`. ★ 이 항목은 Amendment 1 carrier CFP-2573 이
커밋 `b41807812`(*"F1 NEW-carrier provenance 정정 (ADR-064 §결정1 → ADR-054)"*)로 **한 번 이미 정정한 자리**이며, 그 정정이
**기준을 담지 않는 문서로 옮긴 것**이다 — **정정이 권위 있게 읽혀 재검증을 막은 사례**. 본 Amendment 는 기존 행을 **편집하지 않고
회부**한다(Amd 1 블록 무변경 원칙 + carrier scope 밖). 처분 = CFP-2994 Change Plan §10 기록 + Orchestrator 회부.

★★ **회부 대상 = 3 site 전수 (초판의 「frontmatter 1곳」 지목은 과소계수)**: frontmatter 만 고치면 **본문 산문이 오귀속을 계속
발화**하고, 그러면 A3-7 이 스스로 경고한 *"정정이 권위 있게 읽혀 재검증을 막은 사례"* 가 **한 번 더 재생산**된다
(CFP-2573 `b41807812` 이 이미 1회 그렇게 실패한 자리). 회부 목록은 **행 번호로 앵커하지 않고 절·성격으로 지목**한다(§A3-8).
재측정 = `grep -n 'ADR-054' archive/adr/ADR-139-background-wait-liveness-gate.md`
— 정의역 한정 = **본 §A3-7 · §A3-8 블록 자신의 언급은 회부 대상이 아니다**(회부 기록 자체이므로).

| # | site (절 · 성격) | 오귀속 형태 |
|---|---|---|
| 1 | `frontmatter related_adrs` — `ADR-054` 항 인라인 주석 | **직접** — *"new-vs-amendment 기준"* 을 ADR-054 에 귀속 |
| 2 | `frontmatter related_adrs` — `ADR-064` 항 인라인 주석 | **파생** — *"… 기준 부재 → ADR-054 참조"* 로 redirect (1 을 고쳐도 이 행이 살아남으면 오귀속이 유지된다) |
| 3 | **`## 컨텍스트` 절 본문 산문**(직교성·1급 mandate 단락) | **직접 · frontmatter 밖** — *"(ADR-054 신규 ADR 도입 = full-lane 강제 — …)"*. ★ **이 site 가 정확히 「frontmatter 만 고치면 남는 것」** |

**정정 방향 (회부 payload)**: 세 site 의 실 근거지는 ADR-054 가 아니라 **ADR-064 §결정 1 도 아니다** — 두 문서 어느 쪽도
new-vs-amendment 판정 기준을 담지 않는다는 것이 본 항의 관측이다. ⇒ 회부 처분은 *"근거지를 제3의 문서로 다시 옮기는 것"* 이
아니라 **「기준 문서 부재」를 명시하고 본 ADR 의 신규-carrier 정당화를 §컨텍스트 직교성 논증 자체에 귀속**시키는 것이다
(ADR-054 는 *Story 처리 flow* cross-ref 로만 잔존). 실 write = 요구사항/Orchestrator 소관.

### A3-8 — B-7 인용 규약의 PUBLIC 산출물 전파 (본 Amendment 신설 규율)

CFP-2994 가 확정한 **B-7 인용 규약**(문서 grep 산출값 성문 금지 · 정본 = 재측정 명령 + 기준 SHA)은 PRIVATE Story·Change Plan
에만 성문돼 있었고 **PUBLIC wrapper 산출물로 전파되지 않았다**. 그 결과 본 Amendment 저작 중 **자기 브랜치의 형제 hunk 가
자기 인용 포인터를 깨뜨렸다**(§A3-1 · ADR-170 §A2-4 두 site). 규약을 ADR 산출물에도 적용한다.

1. **행 번호 앵커 금지** — 같은 파일·같은 브랜치 안에서도 형제 편집이 행을 이동시킨다. 정본 = **heading 앵커 + 축자 문자열**,
   또는 불변이 필요하면 **merge-base SHA pin**(`git show <sha>:<path>`). 검증 = 각 `<path>:<N>` 인용에 대해 해당 행이 인용
   문자열을 포함하는지 대조.
2. **문서 grep 산출값 성문 금지** — 「N곳」·「0-hit」류 계수를 본문에 적지 않는다. 정본 = **재측정 명령 + 정의역 한정**
   (정의역을 명시하지 않으면 명령의 범위와 주장의 범위가 어긋나 그 자체가 본 Story 의 지배 결함 class 가 된다).
3. **SSOT 종속 declare** — 파생화 처방의 SSOT 는 `ADR-182` §결정 4 가 **#2988 단일**로 못박았다. 따라서 B-7 은 **병렬 SSOT 가
   아니라 그 처방의 lane-local 적용**이며, 본 §A3-8 은 **재정의가 아니라 적용 선언**이다(이중/삼중 SSOT 회피).
4. **정직 천장** — 본 규약은 **저작 규율이며 기계 게이트가 없다**. 「기계 강제」·「차단」으로 표기 금지. 위반은 리뷰에서만 잡힌다.
