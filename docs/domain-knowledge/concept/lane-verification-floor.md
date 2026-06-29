---
kind: concept_definition
type: domain-knowledge
slug: lane-verification-floor
title: Lane verification floor (≥1 independent peer = separation-of-duties / Codex = ceiling-not-floor / honest degrade ≠ silent skip / fan-out observability)
status: Active
updated: 2026-06-29
carrier_story: CFP-2471
related_adrs:
  - ADR-044  # review lane dispatch_mode SSOT — Codex ad-hoc-only, default roster = PL + Claude worker (floor 충족자 = Claude peer)
  - ADR-094  # honest degrade — silent degraded (a) 거부 / hybrid degraded+warning (c) 채택. dual-peer 2→1 degrade 의 동형 anchor
  - ADR-119  # research-before-claims Amd 2 — 게이트 verdict = outcome ground-truth (self-audit verdict 무효 근거)
  - ADR-128  # 완료 단계 정식화 — local-only warning-tier + behavioral precondition (W3 게이트 tier 상속)
related_concepts:
  - merge-time-adversarial-verification-gate  # SoD(implementer≠certifier) + cross-model diversity + critic=신호원 anchor (sibling)
  - orchestrator-runtime-hook-enforcement     # SubagentStart=관측만 / PreToolUse Agent matcher=강제 (fan-out enforcement layer)
  - deferred-followup-recovery-forcing-function  # forced-no-silent-skip + visibility≠resolution (forcing-function family 자매)
  - mutation-based-hollow-gate-detection      # hollow-gate 차단 — 게이트 자기 무결성(meta-hollow-gate)
tags:
  - verification-floor
  - separation-of-duties
  - dual-peer
  - honest-degrade
  - fan-out-observability
  - forcing-function
  - cross-model-diversity
sources:
  - https://slsa.dev/spec/v1.0/levels                                  # SLSA two-person review / implementer ≠ certifier (separation of duties anchor)
  - https://en.wikipedia.org/wiki/Separation_of_duties                 # SoD / four-eyes principle 일반 정의
  - https://en.wikipedia.org/wiki/N-version_programming                # cross-model diversity = 독립 corroboration (Chen & Avizienis 1977)
  - https://en.wikipedia.org/wiki/Graceful_degradation                 # graceful degradation — 부분 가용성 하락 시 honest 동작
---

## 정의

**Lane verification floor** = codeforge 의 어떤 검증 lane 이 발화하는 verdict 가 유효하려면 충족해야 하는 **최소 검증 강도** = **≥1 independent peer (implementer ≠ certifier, separation of duties)**. 즉 구현/판단 주체가 스스로 자기 산출을 인증하는 0-peer self-audit verdict 는 floor 미달로 무효. 이 floor 는 세 축으로 강제된다 — (1) self-audit(0-peer) verdict 무효(축①), (2) dual-peer(2nd peer = Codex) 미가용 시 single-peer 로 내려가되 **honest degrade**(가시 marker + 사유, silent 금지)(축②), (3) deputy/role:dev fan-out 미spawn 의 관측·강제(축③). 검증 *강도/존재* 의 메타 layer 이며, 검증 *내용*(무엇을 찾았나)은 review-verdict-v4 / merge-time-adversarial-gate 의 disjoint 소관이다.

## 컨텍스트

CFP-2471(Epic CFP-2468 Track W / W3) 동인 = mctrader(첫 비-dogfood consumer) 데뷔 감사에서 드러난 **검증 불균질** — simulator fidelity-critical 코드가 2-peer 없이 self-audit 단독 머지, dual-peer 가 Codex 미가용 시 silent 하게 single-peer 로 degrade, 설계 deputy(InfraOp 등)·sonnet 구현자 fan-out 이 실 spawn 0 정황. 이 셋은 "검증이 가장 필요한 곳에서 검증이 빠지는" 동일 class 의 결함이며, retro 에만 남고 codeforge-improvement 로 승격되지 못했다. Track M(mctrader 교정) 착수 전 강제력을 먼저 복구하는 토대.

핵심 firsthand 결함 (CFP-2471 §4):
- **문서 모순**: `plugins/codeforge-review/templates/review-pl-base.md:573-574` "CodexReviewAgent 미설치 시 lane 진입 불가·`SKIPPED` 불허"(degrade 금지) ↔ `templates/team-spec-code-review.yaml:14-16,33-39` "default roster = PL + Claude worker, Codex = user_request_only"(conditional·single-peer default). 전자는 Codex 를 필수워커로, 후자는 ad-hoc ceiling 으로 본다.
- **spawn 관측 mechanism 의 구멍**: `scripts/check-lane-evidence.sh` 의 fan-out 관측(`--check-parallelization`)이 (a) `lane: 설계` 한정, (b) advisory(FAIL 아님), (c) <6 deputy row = silent SKIP, (d) deputy roster 가 stale(구 이름 CodebaseMapper/OpRiskArch/DataMigrationArch ↔ 현 6 permanent 불일치) — mctrader InfraOp 미spawn 미검출의 mechanism 근원.

## 핵심 규칙

### R-1: floor = SoD(≥1 independent peer), Codex 는 floor 아닌 ceiling

검증 floor 의 본질은 "두 모델이 본다"가 아니라 **implementer ≠ certifier**(SLSA two-person review / four-eyes). floor 충족자 = ClaudeReviewAgent (default roster 상존). Codex 는 cross-model diversity 이득을 더하는 **ceiling**(2nd peer) — ADR-044 §결정2 가 Codex review 자동발동을 ad-hoc-only 로 두는 것과 무충돌(disjoint axis). "검증 floor 강제"를 "Codex 강제"로 해석하면 ADR-044 위반이자 사용자 의도 오독.

### R-2: self-audit(0-peer) verdict 무효 (축①)

구현/판단 주체가 스스로 발화한 PASS = ground-truth 미확보(ADR-119 Amd 2 — verdict 는 internal proxy 아닌 outcome ground-truth). SoD 위반. floor 미달로 무효·차단(silent 통과 불허). self-audit 이 유일 가능한 정당 케이스(wrapper-self dogfood 면제 등)는 ADR-031 Amd 2 §14 면제처럼 **honest 면제 marker** 가 silent skip 보다 우선.

### R-3: dual-peer degrade = honest, ≠ silent, ≠ skip (축②)

2nd peer(Codex) 미가용 시 single-peer(Claude) 로 degrade 는 정상 경로(floor 는 여전히 충족 — R-1). 단 ADR-094 동형 — (a) silent degraded 거부(silent harm), (c) degraded mode 작동 + **가시 warning/marker + 사유 강제 기록** 채택. silent 2→1 (표식 없는 degrade) = 게이트 차단 대상. `review-pl-base.md:574` 의 "진입 불가·SKIPPED 불허"는 "**silent degrade 금지**"로 재해석 — single-peer honest degrade 는 진입 불가가 아니라 정식 floor 충족.

### R-4: fan-out 미spawn = 관측 baseline + 선택적 강제 (축③)

설계 lane 6 permanent deputy(SecurityArch/InfraOperationalArch/TestContractArch/DataArch/ModuleArch/APIContractArch) / 구현 lane role:dev roster(sonnet 구현자 포함) 의 실 spawn 수가 기대 미만이면 관측·경고. platform 의 observability↔enforcement 분리(orchestrator-runtime-hook-enforcement) — SubagentStart hook = block 불가(관측만), PreToolUse `Agent` matcher = block 가능(강제). 기대 roster 는 **shape-aware**(CONDITIONAL LiveOps/LiveOrdering/ProductionEvidence + N/A deputy 의 applicability 반영) — 정당한 N/A skip 을 false-block 하면 cry-wolf.

### R-5: 게이트 자기 무결성 (meta-hollow-gate 차단)

"검증을 강제하는 게이트"가 자신은 silent SKIP 으로 빠지면(현 check-lane-evidence: <6 row silent SKIP + design 한정 + advisory) self-defeating. 게이트의 SKIP 도 honest 표식 의무. stale roster 정정(현 6 permanent)이 강화의 선결 — stale 이면 현 deputy 를 매칭 못 해 미spawn 검출 자체가 실패.

### R-6: lane별 floor 차등 허용

security lane floor 는 ≥1 peer 보다 높을 수 있음 — packet 에 1차 native layer(Dependabot/CodeQL/Secret/Push) inline + dependency manifest 필수(`ClaudeReviewAgent.md:48`). 균일 floor vs lane별 차등은 설계 결정.

## 경계

- **In scope**: lane 검증의 *강도/존재* floor 개념 + 3 축(self-audit/degrade/fan-out) + honest degrade 규칙 + observability↔enforcement layer 분리.
- **Out of scope**:
  - 검증 *내용* 품질 (review-verdict-v4 finding taxonomy / merge-time-adversarial-gate critic 출력 — disjoint layer).
  - deputy 산출물 *유효성* (spawn 됐으나 stall = spawn 관측으로 안 잡힘 — W3 는 강도/존재이지 산출 품질 아님).
  - degrade·미spawn 누적 KPI / dashboard.
  - enforcement mechanism 의 구체 wiring(PR-time lint / PreToolUse hook / behavioral) — 설계 lane 위임.
- **Anti-pattern**: floor 를 "Codex 강제"로 오독(ADR-044 위반). silent degrade(ADR-094 (a) silent harm). 게이트 자기 silent-SKIP(meta-hollow-gate). stale roster 로 미spawn 검출 무력화. 기대 roster 에 N/A deputy 포함해 false-block(cry-wolf).

## 관련 ADR

- **ADR-044** §결정2 — Codex ad-hoc-only / default roster = PL + Claude worker. floor 충족자 = Claude peer 의 근거 (R-1).
- **ADR-094** — honest degrade((a) silent 거부 / (c) degraded+warning 채택). dual-peer 2→1 degrade 의 동형 anchor (R-3).
- **ADR-119** Amd 2 — 게이트 verdict = outcome ground-truth. self-audit verdict 무효의 근거 (R-2).
- **ADR-128** — local-only warning-tier + behavioral precondition. W3 게이트 tier 상속 (branch protection 6-tuple 무변경).

## 변경 이력

- 2026-06-29 KST — 초기 작성 (CFP-2471 RequirementsPL 합성 — DomainAgent firsthand framing + ADR-044/094/119/128 직접 Read grounding). SoD(SLSA) / cross-model diversity(N-version) / graceful degradation cited.
