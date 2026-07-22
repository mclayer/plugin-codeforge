---
adr_number: 144
title: Orchestrator 자율성 stop taxonomy 3축 모델 + decision-null pause(vague-pause) 신설 + 자율화 정직 상한
status: Accepted
category: governance
date: 2026-07-05
carrier_story: CFP-2573
supersedes: []
related_adrs:
  - ADR-025  # stop discipline whitelist/illegal — L1 realization (§결정 7 표 vague-pause 행 + §결정 10 subclass, Amendment 3)
  - ADR-071  # user-dialog convergence — L2 realization (§결정 22 scope 일반화 + consumer 전파, Amendment 14)
  - ADR-139  # background-wait liveness gate — L3 substrate + realization (§결정 4 강화, Amendment 1)
  - ADR-142  # Orchestrator-self context discipline — 정직성 헌장 tier 모델 상속 (§결정 7)
  - ADR-115  # runtime hook enforcement — Stop/SubagentStop record-only, block 금지 하드 제약
  - ADR-043  # telemetry privacy — opt-in default-false (L5/L6 제약)
  - ADR-163  # measurement channel architecture — stop-event schema SSOT (L5 근거)
  - ADR-009  # wrapper-only single-lead — L3 topology 재편 경계
  - ADR-039  # subagent default — §결정 19 lead force-resume (L3 recovery anchor)
  - ADR-054  # 신규 ADR 도입 = full-lane 강제 — D-A NEW carrier 정당화 실 근거지 (new-vs-amendment 기준)
  - ADR-064  # §결정 7 evidence-gated ratchet 보조 — 신규-carrier 기준 아님 (§결정 1 = 4-어휘 운영 정의; new-vs-amendment 근거지는 ADR-054)
  - ADR-134  # per-Story dispatch topology — L3 Story-boundary handoff build-on
  - ADR-038  # TodoWrite progress viz — marker≠liveness (재사용 금지)
related_concepts:
  - orchestrator-runtime-hook-enforcement
is_transitional: false
---

# ADR-144: Orchestrator 자율성 stop taxonomy 3축 모델 + decision-null pause(vague-pause) 신설 + 자율화 정직 상한

## 상태

Accepted (2026-07-05 KST) — CFP-2573 carrier (Epic CFP-2571 요구 #1 scoped 계승). Orchestrator 정지(stop) 분류의 3축 척추(spine)를 1급 SSOT 로 확립하고, 그 위에 결정-공백(decision-null) 정지 class 를 신설한다. 강화(ratchet↑) 방향 — 기존 stop 규율 3층(ADR-025 whitelist/illegal · ADR-071 touchpoint/ask-trigger · stop-event-v1 reason_class)을 폐지·축소하지 않고, 그것들이 암묵 전제하던 축을 명시화 + 미명명 class 1개를 추가한다. 약화 surface 0.

## 컨텍스트

데뷔 이후 반복 호소: "애매한 stop 이 너무 많다"(회고 정량 부당:정당 = 10:2, repo-외 회고 산출물 grounding — Story §2.5 정직 고지). 최다 재발 = 전환·경계 over-ask("진행할까요?"), "행동만 교정" 3회 실패 → **규칙 자체 변경 필요** 신호.

**진짜 누락 축 = "결정 payload = 0"** (Story §2.1 도메인 판정, `[verified]`): 기존 stop taxonomy 3층은 전부 **"결정 payload > 0"을 암묵 전제**하고 그 위에서 "누가 결정/정당한가"만 분류한다. ADR-025 §결정 7 illegal 5패턴은 전부 특정 sub-decision 을 묻는 정지, ADR-071 ask-trigger 3종도 전부 결정 분기다. "한 숨 쉬어가자"류는 이 축과 **직교** — 묻는 것·결정할 것이 0 인 정지라 어느 셀에도 없다(origin/main `git grep vague.?pause|한숨|decision-null` = 0, GAP-3 CONFIRMED).

**이 척추(3축 모델)의 부재가 P10 delivery-gap 을 대화 stop 과 혼동시킨 진원**이다(Story §2.4 domain-gap #1). delivery-gap 은 liveness 축(비의지적 mechanical stall)인데 대화 축(의지적 발화 정지)으로 오분류하면 "묻지 마" 규칙으로 고치려다 무효가 된다 — 실제 해소는 force-resume 뿐(ADR-139).

**platform 상한(닫히지 않는 blind-spot)**: over-halt/vague-pause **순간**엔 correct lever 가 부재하다 — Stop/SubagentStop 은 fire 하나 block 금지(ADR-115 §결정 2, platform-broken #10412/#55754) + 정당/부당 정지 구분 불가, PreToolUse(Agent)·UserPromptSubmit 은 그 순간 fire 안 함, plain-text turn-end 라 tool-mediation 부재. `anthropics/claude-code#15872` 는 AskUserQuestion 에 *알림 hook* 추가 요청(CLOSED/NOT_PLANNED)이지 *차단* 요청이 아님(요구사항리뷰 CONFIRMED) — blind-spot 결론(pre-utterance hard-block 불가)은 옳으나 유일 근거는 아니다. ∴ **물리 하드게이트 구조적 불가**. 가용 = 예방(fire 하는 창 priming) + 측정(record-only 사후). "자율화 = 물리차단 아닌 확률저감·예방·측정"(Story A 도메인 제약).

## 결정

### 결정 1 — stop taxonomy 3축 모델 (SSOT — the missing spine)

Orchestrator 정지를 **3개 직교 축**으로 분류한다. 각 축 = 다른 SSOT · 다른 remediation:

| 축 | 정의 | 하위/판정 | SSOT | remediation |
|---|---|---|---|---|
| **A. 대화발화 (volitional)** | 사용자向 의지적 발화 정지 | **A1 = payload > 0** (ask-trigger 정당 + §결정 7 illegal 부당·기명) · **A2 = payload = 0** (decision-null — §결정 2) | ADR-071 §15/§20/§22, ADR-025 §결정 7 | 규칙(advisory/priming) |
| **B. liveness (non-volitional)** | background-wait mechanical stall (비의지적) | INV-L1~L4 (wall-clock ceiling / fail-open 금지 / 0byte≠stall / lead 소유) | ADR-139 | lead force-resume (대화규칙 아님) |
| **C. session-lifecycle (정당)** | 정당 lifecycle 경계 | whitelist 5종 · handoff | ADR-025 whitelist 5, ADR-142 L5 handoff | 유지 (정당) |

**배정규칙**: `volitional 발화? No → 축 B/C(mechanical) / Yes → 정당 lifecycle 경계? Yes → 축 C / No → payload > 0? Yes = A1, No = A2(vague-pause)`.

**★핵심 경고 codify (오분류 1순위)**: **P10 delivery-gap idle 은 축 B(liveness)이지 축 A(대화)가 아니다.** 자식 완료 통지가 parent 아닌 lead 로 surface(ADR-039 §결정 19 구조한계) → Orchestrator 가 멈추기로 *선택*한 게 아니라 통지 미도달로 갇힘 = non-volitional. 대화규칙("묻지 마")으로 고치면 **무효**, force-resume 로만 해소(§결정 4). 전환·경계 over-ask(최다 재발) → A1(기명), vague-pause → A2(미명명, §결정 2 신설 대상).

본 3축 모델은 taxonomy 를 **재정의하지 않는다** — 세 축 각각의 기존 SSOT 를 그대로 인용하고, 그동안 암묵이던 "축" 자체를 명시화할 뿐이다.

### 결정 2 — decision-null pause 신설 class (L1)

상위개념 **decision-null(결정-공백) 정지** 를 신설한다. 2형:

- **silent form = over-halt** (무발화 — ADR-071 §결정 22 ASM-2 가 blind-spot 으로 부분 명명, = GAP-2)
- **verbalized form = vague-pause / "한 숨 쉬어가자"** (발화하나 payload 0 — 완전 미명명, = GAP-3·핵심)
- → over-halt(무발화)·vague-pause(발화)는 **같은 축(payload=0)의 두 form**.

**discriminant**: `vague-pause ⟺ (잔여작업 有 ∧ 결정 payload = 0 ∧ volitional 발화)`. vs ask-trigger(payload > 0) / vs 완료보고(terminal) / vs P10 delivery-gap(mechanical stall = 비의지적, 마지막 조건이 갈라냄).

**tier = `[advisory]`** (taxonomy 명명·규율 — runtime hard-deny 불가, plain-text turn-end 라 tool-mediation 부재). **Realization = ADR-025 Amendment 3**: §결정 7 illegal-stop 표에 `vague-pause` 행 추가 + §결정 10 subclass enum 에 `policy_violation_vague_pause` 등재. over-suppression 방어 = "ask-trigger 3종 미해당 + 결정 내용 0" 판별조건이 정당 멈춤(특히 touchpoint (a) 결과-명세 모호 = P12)과 명확히 구분되게 명시.

### 결정 3 — 자명-진행 priming scope 확장 (L2)

ADR-071 §결정 22 의 전환 지점 reminder scope 를 **"모든 자명-진행 지점"**(전환 + lane 경계 + 완료-후 + vague-pause 금지 포함)으로 일반화한다.

- **tier = `[advisory / priming]`.**
- **기존 hook TEXT 확장** — 신규 hook 신설 금지. 2채널(UserPromptSubmit user-turn 창 = `hooks/story-transition-autonomy-reminder.py` + PreToolUse(Agent) autonomous 창 = `hooks/pretooluse-agent-spawn-gate`) 모두 TEXT broaden.
- **ask-trigger 3종 carve-out verbatim 보존** (over-suppression 차단).
- **NEVER block** — GAP-1/GAP-2 순간엔 어떤 hook 도 fire 안 함(documented blind-spot). "over-halt 를 막는다" 주장 금지.
- **Realization = ADR-071 Amendment 14.** hook 의 public identity(파일명 · hooks.json 5번째 entry · run-hook.cmd · §22.7 back-refs) 무변경 — 한 hook 의 TEXT 를 넓혀도 concern 은 여전히 하나(autonomous-progress priming) = one-concern-per-hook 정합. §22.7 "shared reminder-base 추출 금지"의 의미 = cross-hook **CODE** abstraction 금지(YAGNI/fail-isolation, hook 은 self-contained stdlib zero cross-import 유지)이지 TEXT-scope 금지가 아니다.

### 결정 4 — delivery-gap = 축 B liveness 규율 강화 (L3) + topology reform 정직 판정

delivery-gap(P10)은 **축 B(liveness)** 규율로만 해소된다(§결정 1). tier = detection `[measurement]`(output-mtime/marker 관측) + recovery `[advisory]`(lead-owned discretionary). **`[물리강제]` 아님** — SubagentStop block 금지(ADR-115) + INV-L4 lead 판정.

**(i) realizable NOW (본 Story scope) — Realization = ADR-139 Amendment 1** (Codex peer + RefactorAgent CONVERGED, PL judged consensus VALID):
- 구조 규율 codify: **"PL 은 spawn-then-blind-wait 금지 — 수집(collect)은 auto-wake 되는 LEAD 가 소유하거나 LEAD 로 handoff"** + named lead-collect routine(interface seam) + PL-background-yield idle **detection** marker.
- observer = LEAD(hook 아님). stall = wall-clock ceiling **AND** no-progress-marker(mtime + content + task-notification). 0-byte 단독 ≠ stall(INV-L3 재확인). INV-L2 fail-open 금지(stall ≠ PASS, verdict == "PASS" 명시일 때만 PASS).
- 인프라 신규 불요 — CFP-2549 로 substrate 기배선, 문구 강화만.

**(ii) DEFER-escalate (paradigm-scope, 본 Story scope 아님)**: full auto-wake-parent dispatcher(env=1, "타이머 만료 → 자동 SendMessage(parent 깨우기)")는 substrate 부재 + ADR-142 §결정 6 이 env=1 dispatcher 를 fresh DEFER + `/resume` in-process teammate 미복원. narrative defer 로 chief authority 에 routed. recurrence anchor `L3-delivery-gap::(a)` — ≥2 Story 재-제안 시 escalate. **자동 followup 발의 안 함**(3문 게이트).

**정직 앵커(hollow-gate 금지)**: 본 Story 실행 세션에서 delivery-gap force-resume 를 **5~6회 재현**(요구사항 lane 4회 + 리뷰 lane 1~2회, falsifiable 실증). 본 ADR 은 이를 **자동 교정한다고 주장하지 않는다** — force-resume 는 lead-owned discretionary 로 유지된다.

### 결정 5 — stop-event passive telemetry aggregate (L5, GAP-7)

stop-event 원장 aggregate 경로를 신설한다. **tier = `[measurement]` strict record-only** — `hook_decision="record-only"` 불변, non-blocking.

- **신규 `scripts/lib/aggregate_stop_event.py`**(GAP-7 실체 = 부재) — `.claude/ledger/stop-event.jsonl`(실 구현 경로) 를 읽어 per-reason_class count + 부당(`policy_violation*`)/정당(`user_stop_legitimate` · `decider_escalation_required`) 비율 산출.
- **reason_class 자동분류 = 불가(CONFIRMED)** → 채움 = **PMO retro sidecar mapping**(stop_reason → reason_class 를 별도 artifact 로; 원장 IN-PLACE EDIT 절대 안 함 — record-only INV ADR-115 §2 + ADR-072 policy/evidence disjoint). aggregate 는 optional classification-map 지원: map 有 → ratio, map 無 → per-stop_reason frequency(honest degrade).
- **★HONESTY(binding)**: 실 원장은 전부 5-field(reason_class 부재) → 실 aggregate = backfill 전까지 all-unclassified → aggregate 는 **"분류 없인 정량 불가 (측정 ≠ 분류)" honesty 서술을 반드시 emit**. "10:2 실측" / "telemetry 가 stop 을 줄인다" 주장 금지(측정만).
- **dedup = row-hash**(canonical JSON `sort_keys` → sha256; event_id 부재 → forward-compat + canonicalization). honest under-count caveat — 동일-초 별개 이벤트 병합 불가피 → `rows_total`/`rows_deduped`/`duplicates_collapsed` emit, exact-count 주장 금지.
- edge: malformed → skip+count / empty → zero-count exit 0 / window → tz-aware ISO parse.
- runtime Stop hook 은 5-field 유지(runtime capture widen 금지). **Realization = stop-event-v1 contract MINOR bump**(aggregate slot un-defer + 계약↔구현 정직 정합, 필드 추가 0).

### 결정 6 — consumer 전파 (L6)

vague-pause 금지 norm + 확장 reminder TEXT 를 consumer 로 전파한다. **tier = `[advisory]`.**

- reminder TEXT 확장을 `hooks/hooks.json` 배선으로 두면 plugin 설치 시 consumer 자동전파(overlay 변경 0, CFP-2456 skip-offer 선례 동형).
- reminder TEXT 는 **STATIC**(runtime value interpolation 금지, no PII).
- consumer **telemetry sharing** = opt-in default-false 보존(ADR-043 §결정 1).
- **정직 nuance(binding)**: 로컬 ledger append 는 wrapper+consumer 양쪽에서 이미 ungated(기존 CFP-1743 behavior, ADR-043 §결정 1 always-on 강제는 Phase 2 deferred=doc-only) — 이건 새 flip 아님. wrapper always-on ≠ global default flip. "(e) consumer telemetry opt-in"은 sharing/collection intent 한정으로 정확하며, 로컬 append 가 ungated 인 점은 정직히 명기한다. §결정 1(ADR-043) full runtime compliance 주장 금지.

### 결정 7 — 자율화 정직 상한 + tier honesty meta-gate (ADR-142 §결정 7 상속)

- **GAP-1(pre-utterance hard-block) / GAP-2(over-halt 실시간 검출) 는 닫히지 않는다** — platform 한계(#15872 / #10412 / #55754). **정직 문서화만**, hollow-gate 금지. "닫았다" 주장 시 산출물 결함.
- **AC-6 meta-gate**: 본 Story 산출 lever 전부 `[물리강제]` / `[measurement]` / `[advisory]` 라벨 verbatim 부착. self-test 는 **각 lever 가 자기 tier 만 assert** — measurement/advisory 축에 "block/deny/강제" 언어가 출현하면 tier-honesty lint RED.
- **tier = `[measurement]`(tier-라벨 정적 lint) + meta.** advisory→blocking 승격은 ADR-060 evidence-gate 만.
- 유일한 `[물리강제]` = §결정 7 표(ADR-025) 에 vague-pause entry 존재 여부를 검사하는 **정적 lint** — 이는 **ADR-문서 integrity 검사이지 behavior 강제가 아니다**(Story §2.3). 그 외 전 lever = advisory/measurement.

### 결정 8 — tool-mediated ask deny (C lever): observed, not built

PreToolUse(AskUserQuestion) `permissionDecision:"deny"` 로 **tool-mediated ask 하위부류**만 부분 lever 가능하나, 본 ADR 은 이를 핵심 AC 로 **채택하지 않는다**:

- 지배적 vague-pause = plain-text turn-end(가로챌 tool 부재) → 대부분 미커버.
- PreToolUse(AskUserQuestion) deny 는 fragile — #12031(활성 시 AskUserQuestion 결과 stripping), #40506(`claude -p` 비대화형 미발화).
- ∴ hard lever 화 = hollow-gate. **관찰만 기록**(dogfood open-question), 핵심 AC 비대상(Story §5.6 #7). 요구사항리뷰 게이트가 사후 이 하위부류를 surface 하면 그때 재평가.

## 결과

- (+) **liveness/대화 축 혼동 종결** — 3축 척추 명시로 P10 오분류 진원 제거. delivery-gap = 축 B 로 못박아 대화규칙 오적용 차단.
- (+) **미명명 class 신설** — decision-null(over-halt silent / vague-pause verbalized) 상위개념 + discriminant 로 GAP-3(핵심 uncovered) 명명.
- (+) **SSOT 단일 anchor** — 다ADR 걸침(025/071/139/142/115/043/042)을 본 ADR 이 anchor, sibling amendment(ADR-025 Amd3 / ADR-071 Amd14 / ADR-139 Amd1) + contract MINOR bump 로 realization 분산.
- (−) **GAP-1/GAP-2 미폐쇄** — platform 한계로 over-halt(무발화) 실시간 검출·pre-utterance hard-block 영구 불능. 본 Story 는 예방(advisory) + 측정(measurement)까지만 정직하게 목표한다.
- (−) **10:2 정량 = 측정 목표 아님** — 현상 서술로만 취급, hard floor 박제 안 함(baseline-first). passive hook 은 정당/부당 자동 분류 불가 → 채움은 PMO retro sidecar.
- (−) L5 aggregate = record-only measurement — blocking 승격은 ADR-060 evidence-gate 후.

## 비대상 (out-of-scope)

- GAP-1/GAP-2 hard-block 주장(pre-utterance runtime deny — 구조적 불가). AC 로 세우면 hollow-gate.
- Stop/SubagentStop force-continue/block(ADR-115 §결정 2 platform-broken #10412/#55754 — 절대 금지).
- reason_class 를 passive hook 에서 justified/unjustified 로 자동 semantic 분류(불가 — sidecar/retro-time 만).
- 정당 멈춤 3종(ask-trigger) 축소·재정의, ask-trigger enum · 3-touchpoint enum member 추가(ADR-071 closed-enum 무손상 상속).
- tool-mediated AskUserQuestion deny hard lever 화(§결정 8 — 관찰만).
- full auto-wake-parent dispatcher(env=1) 구현(§결정 4 (ii) DEFER-escalate, narrative defer).
- #797 accumulation-layer lint 흡수·발의(참조만 — 3문 게이트 대상, 자동 followup 금지).
- phase-gate plumbing 갭(별도 축 — gate plumbing ≠ 대화 stop, 관찰만 — Story §7.0 #7).

## 해소 기준

N/A — permanent policy. 강화(ratchet↑) 방향 governance anchor — sunset 대상 아님(ADR-058 §결정 5 강화 방향 면제). platform blind-spot(GAP-1/2) 이 미래 Claude Code feature 로 닫히면 §결정 7 정직 상한은 amendment 로 강화(hard lever 승격 evidence-gate)만 가능, 약화 경로 없음.

## 관련 파일

- `archive/adr/ADR-025-stop-discipline-non-whitelist-as-defect.md` §결정 7 / §결정 10 — L1 realization (Amendment 3)
- `archive/adr/ADR-071-orchestrator-user-dialog-convergence.md` §결정 22 — L2 realization (Amendment 14)
- `archive/adr/ADR-139-background-wait-liveness-gate.md` §결정 4 — L3 realization (Amendment 1)
- `docs/inter-plugin-contracts/stop-event-v1.md` §5 — L5 aggregate slot un-defer + 계약↔구현 정직 정합 (MINOR bump)
- `scripts/lib/aggregate_stop_event.py` — L5 신규 aggregate (Phase 2, GAP-7 실체)
- `hooks/story-transition-autonomy-reminder.py` / `hooks/pretooluse-agent-spawn-gate` — L2 2채널 TEXT 확장 (Phase 2)
- `hooks/hooks.json` — L6 consumer 전파 배선 (Phase 2)
- `docs/domain-knowledge/concept/orchestrator-runtime-hook-enforcement.md` — turn-time hook block 가능 매트릭스 (Stop payload stop-reason 부재 nuance)
