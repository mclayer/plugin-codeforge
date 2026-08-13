---
adr_number: 109
title: in-process Anthropic infra 429 surgical mitigation framework
status: Accepted
is_transitional: false
category: tooling-infrastructure
date: 2026-05-24
related_files:
  - skills/rate-limit-429-mitigation/SKILL.md
  - mclayer/codeforge-internal-docs/plugin-codeforge/change-plans/cfp-1354-in-process-429-mitigation.md
  - docs/kpi/429-incident.json
  - docs/kpi/429-incident-history.jsonl
  - templates/github-workflows/429-incident-telemetry.yml
  - templates/team-spec-decompose.yaml
  - templates/team-spec-requirements.yaml
  - templates/team-spec-design.yaml
  - templates/team-spec-design-review.yaml
  - templates/team-spec-develop.yaml
  - templates/team-spec-code-review.yaml
  - templates/team-spec-security-test.yaml
related_stories:
  - CFP-1354
  - CFP-2823   # Amendment 1 carrier — §결정 1 감지집합 session/usage-limit class 편입 + fable-리밋 failover 합성
related_adrs:
  - ADR-039
  - ADR-044
  - ADR-057
  - ADR-064
  - ADR-067
  - ADR-068
  - ADR-082
  - ADR-097
  - ADR-104
  - ADR-106
  - ADR-108
  - ADR-141   # Amendment 1 — fable-리밋 opus failover override carrier (§결정 3 step2 dead slot re-tenant)
mechanical_enforcement_actions:
  - 429-retry-evidence-presence
  - debate-parallel-cap-check
  - deputy-stagger-check
amendments:
  - amendment: 1
    carrier_story: CFP-2823
    date: 2026-07-24
    scope: >-
      §결정 1 detection closed-set 을 base 4-tuple 에서 session/usage-limit class 2 literal
      편입해 확장 — `session limit`(확정, 2026-07-24 실관측 `You've hit your session limit`)
      + `usage limit`(추정·미실측, fail-open — 요구사항-named 개념 커버, 유일 firsthand 등장 =
      본 ADR §컨텍스트 §1:54 부정 문맥 "not your usage limit") = base 4 + class 2 = 6 literal.
      실관측 세션 한도 문자열이 base 4-tuple 과 substring 0/4 불일치(firsthand 반증)라 확장
      필수. 3→4 확장 선례(§결정 1 "Server is temporarily limiting" 편입, L97) 동형 — 별도
      enum 신설 아님, 단일 §결정 1 closed-set 확장, literal-substring `no regex wildcard`
      invariant 유지. §결정 1 base 4-tuple = byte-intact 보존(rewrite 0). 동반 = fable-리밋
      opus failover 의 ADR-109 합성 배치(§결정 3 step2 dead slot[구 ADR-057 §결정 2, moot]
      re-tenant + fable step1 bypass + cascade depth fable→opus hop count-in) — carrier =
      ADR-141 Amendment 6(SSOT), 본 amendment 는 감지집합 확장 SSOT + 합성 배치 codify.
      529(§결정 6)는 disjoint 유지(failover 감지집합 NOT-IN, `429`≠`529`). 상세 = 본문
      `## Amendment 1`.
    sunset_justification: >-
      N/A — §결정 1 closed-set invariant("5번째 pattern 추가 = 본 ADR Amendment 의무")의
      정확 이행이자 ratchet 강화 방향(감지 집합 확대, 약화 0). ADR-109 §해소 기준
      "N/A permanent policy — sunset_justification 면제" 상속(ADR-058 §결정 5 / ADR-064
      §결정 7 evidence-gated symmetric ratchet 강화 방향 정합).
  - amendment: 2
    carrier_story: CFP-2944
    date: 2026-08-12
    reinterpretation: true   # §결정 1/Amd1 감지집합의 *지위* 를 "판정 primary"에서 "비망라 fast-path"로 재해석 (문면·code-fence byte 무변경, 열거 내용 무변경) + §결정 5 "user manual resume only"의 정의역을 재시도 축 한정으로 재해석. self-declared — 의미 판정은 리뷰 lane 축.
    scope: >-
      한도류 신호 판정의 primary 를 §결정 1/Amendment 1 closed-set 열거에서 **의미론적
      판별식 D** 로 이관한다(열거는 비망라 fast-path 로 강등, code-fence byte 무변경 ·
      재열거 0 · 경쟁 enum 0). 구성: (b) **D-0 발신자 전제** — 판정 정의역 = 본 세션
      harness agent 실행 계층이 발신한 종료·오류 신호 한정, 타 벤더 API 한도(GitHub 등)는
      정의역 밖(firsthand: GitHub `API rate limit exceeded for user ID 12345.` = 6-literal
      1/6 매칭 → 전제 없이는 Anthropic 축 처방이 오착지). (c) 입력 표면 scope 불변식을
      판별식 본체에 부착(playbook §3.0.12b 문언을 fast-path 절에서 판정 절차 전체로 승격).
      (d)(e) D-i~D-iii 3항 + **4치 출력**(D-out-1 자기해소 / D-out-2 액션의존 /
      D-out-3 확정 부정 / D-indeterminate 평가 불확정). (f) negative control 2방향
      (N-a 비한도류 · N-b 자기해소 아님). (g) **판정 신호 원문 verbatim 기록 금지**
      (§결정 10 redaction matrix 확장 — 분류 결과·limb·근거 1줄만). (h) D-out-1
      자기확증 반증 축. (i) **§결정 5 축 한정 개정** — "자동 재시도 금지"(bounded retry
      상한) 보존, "작업 진행 중단"만 분리 + remedy 단조 비용 사다리 R0~R4(신규 재시도
      예산 0). 상세 = 본문 `## Amendment 2`.
    sunset_justification: >-
      N/A — is_transitional: false permanent policy 유지(§해소 기준 무변경). 방향 =
      **양방향 ratchet, 각 방향 firsthand evidence 동반**(ADR-064 §결정 7 evidence-gated
      symmetric ratchet): ① 감지 *대상 클래스* 확대(강화) 근거 = 현행 제품 문면 4/4
      6-literal 미매칭 firsthand 반증 ② 감지 *정의역* 축소(D-0 발신자 전제 = 오탐 제거)
      근거 = 타 벤더 문자열 1/6 매칭 firsthand reproducer + ADR-141 A6-6 "오탐 = 더 높은
      리스크(opus 낭비 + 실결함 은폐)" 자기선언. §결정 1 closed-set invariant("5번째
      pattern 추가 = Amendment 의무")는 **미발동** — 본 Amendment 는 literal 을 추가하지
      않는다(열거 무증감).
---

# ADR-109: in-process Anthropic infra 429 surgical mitigation framework

## 상태

`Accepted` (2026-05-24 KST) — CFP-1354 (Epic CFP-1353 Story A) chief author direct write per ADR-070 / CFP-578 chief author precedent. Sibling Story B (#1355) = OS-level external session auto-resume disjoint axis (ADR-110 reserved).

## 컨텍스트

사용자 발화 verbatim (Story §1, story-section-1-immutable 강제):

> codeforge의 개선이나 consumer 프로젝트 작업 중 API Limit이 걸리는 때가 있다. 이 때 limit이 풀리면 자동 시작했으면 좋겠는데
> 그리고 이런 에러가 발생하는 것도 해결해야 한다.
> API Error: Server is temporarily limiting requests (not your usage limit) · Rate limited

본 발화 = 2 axis disjoint mechanism layer (Epic CFP-1353 split):

- **Axis A (본 ADR-109 / Story A scope)**: in-process Orchestrator throttle — Claude Code session alive context, Anthropic infra 429 surgical mitigation. 사용자 발화 "이런 에러가 발생하는 것도 해결" 영역
- **Axis B (sibling ADR-110 / Story B scope)**: OS-level external session auto-resume — session dead context. 사용자 발화 "limit이 풀리면 자동 시작" 영역

기존 SSOT cover:

- **ADR-057 §결정 2** — Sonnet → Opus model substitution fallback (max 1회, cross-model axis). 본 ADR 와 **disjoint axis** (within-model timing axis).
- **ADR-039 §결정 2** — Inline whitelist closed 4-entry enumeration (L99-L110). 5번째 entry "429 retry inline allowed" 신설 압박 명시 차단.
- **ADR-064 §결정 4 Trace 4** — multi-task spawn default = parallel (amendment_log L14-L15 + L97-L98 parallel-dispatch-prompt-check binding).
- **ADR-067** — max FIX 3/3 cap (§10 FIX Ledger). 429 retry ≠ FIX (운영 phase telemetry axis disjoint).
- **ADR-097 §결정 1** — paradigm replacement closed-set 3 조건 AND (9+ ADR sunset / 단일 atomic Epic / wholesale replacement). 본 ADR = 4 ADR amendment + 1 신설 sunset 0 → carve-out 비대상.
- **ADR-104 / ADR-106** — 운영 phase 1st-class 정의 + 운영 metric → PMOAgent input 회로.
- **ADR-108** — label-registry forcing function (description text `"Nth hotfix-bypass:* family member"` raw grep count parity).

기존 영역 부재 (GAP):

- **Detection 4-tuple SSOT**: ADR-057 / playbook §3.0.12 / skill body = 3 source 분산. 사용자 발화 verbatim `"Server is temporarily limiting"` = 어디에도 등장 0 (verified Grep).
- **Backoff curve normative**: empirical-source annotation (ADR-068 I-5) 의무 영역 부재.
- **Sequential composition**: same-model retry (within-model) → ADR-057 §결정 2 cross-model fallback escalation 합성 부재.
- **Circuit breaker 3-window AND**: 429 cascade 영역 자동 차단 정책 부재.
- **§10 vs §14 boundary**: 429 retry telemetry → §10 FIX Ledger 오용 시 ADR-067 RESET contamination risk.
- **Secret redaction matrix**: KPI commit 시 org_id / account_id 누설 영역 unconditional invariant 부재.
- **Retry primitive 위치**: Orchestrator inline (ADR-039 closed 4-entry 압박) vs skill body (closed 4-entry 보호) 결정 영역.

본 ADR = 위 7 GAP normative SSOT carrier — 10 §결정 통합 codify.

## 결정

### §결정 1 — Detection 4-tuple (single SSOT)

429 rate-limit detection = 다음 4 pattern any-match (closed-set, no regex wildcard):

```
"rate limit"
"quota exceeded"
"429"
"Server is temporarily limiting"
```

- **Single SSOT**: 본 §결정 1 = detection enum 단일 source. ADR-057 §결정 2 / `codeforge:rate-limit-429-mitigation` skill body / `docs/orchestrator-playbook.md` §3.0.12 = consumer cross-ref only (중복 정의 차단).
- **4-tuple expansion rationale**: 사용자 발화 verbatim `"Server is temporarily limiting"` (Story §1) = 기존 3-pattern SSOT 미커버 (ArchitectAnalyst gap closure verified Grep — `"Server is temporarily limiting"` = 기존 SSOT 어디에도 등장 0).
- **closed-set invariant**: 5번째 pattern 추가 시 본 ADR Amendment 의무 (ratchet 강화 방향, ADR-064 §결정 7 정합).

### §결정 2 — Exp-backoff curve + Retry-After header 우선

- **Backoff curve**: full jitter `random_uniform(0, base * 2^attempt)` with `base=1s`, single attempt cap = 60s, total max attempts = 6 (1s → 2s → 4s → 8s → 16s → 32s nominal, jittered)
  - **empirical-source** (ADR-068 I-5 dimensional empirical grounding 정합): [verified-via: AWS Architecture Blog "Exponential Backoff And Jitter" Marc Brooker 2015-03-04, https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/] — full jitter algorithm verbatim 답습 (no-overlap retry distribution, contention avoidance proven)
- **Retry-After header 우선**: Anthropic `anthropic-ratelimit-*-reset` header 또는 `Retry-After` header presence 시 exp-backoff override
  - **empirical-source**: [verified-via: RFC 7231 §7.1.3 + Anthropic public docs https://docs.anthropic.com/en/api/rate-limits] — delta-seconds 또는 HTTP-date format

### §결정 3 — Sequential composition (same-model retry → cross-model fallback)

429 detection 시 retry sequence:

1. **Same-model retry 1회** (within-model timing axis, 본 ADR 신설) — §결정 2 exp-backoff 적용
2. **실패 시 → ADR-057 §결정 2 model fallback** (Sonnet → Opus, max 1회, cross-model substitution axis disjoint cross-ref)
3. **Opus 도 429 → 6 attempts soak** (§결정 2 max 6 attempts cap) → §결정 4 circuit breaker open
4. **Cascade depth ≥ 2 → §결정 5 user manual resume only** (ADR-057 §결정 2 "자동 재시도 금지" invariant 정합)

**ADR-057 §결정 2 invariant 보존 cross-ref**: 본 §결정 3 = within-model timing axis (same-model retry 우선) — ADR-057 §결정 2 cross-model substitution axis 와 sequential composition 정합. ADR-057 amendment 0 (cross-ref only).

### §결정 4 — Circuit breaker 3-window AND

Circuit breaker open trigger = 3 window 모두 충족 (AND):

| Window | Threshold | Source |
|---|---|---|
| Fast | 5건 / 1min | `docs/kpi/429-incident-history.jsonl` rolling window |
| Medium | 10건 / 5min | 동상 |
| Slow | 3건 / 1 week | `docs/kpi/429-incident.json` weekly aggregate |

- **[hypothesis]**: 본 3-window threshold = baseline 추정. Phase 2 telemetry refine 의무 (post-deploy actual incident rate 측정 후 사용자 확인 — ADR-068 I-5 dimensional empirical grounding 정합).
- **circuit breaker open 후**: §결정 5 cascade depth ≥ 2 처리 (user manual resume only).

### §결정 5 — Cascade depth ≥ 2 → user manual resume only

`cascade_depth` 정의 = 단일 user request 안 retry sequence 의 nested cascade level. depth ≥ 2 (예: same-model 429 → Opus fallback → Opus 429 → 2차 retry burst) 시:

- **자동 재시도 금지** (ADR-057 §결정 2 invariant verbatim 답습)
- **user manual resume only** — `AskUserQuestion` escalation 또는 사용자 turn 대기
- **`docs/kpi/429-incident-history.jsonl` `cascade_depth` field append-only event log** (ADR-106 운영 metric → PMOAgent input 회로 정합)

### §결정 6 — 429 vs 529 disjoint 분기

- **429** (Anthropic rate limit) = §결정 1 4-tuple detection + §결정 2 exp-backoff
- **529** (Anthropic overloaded) = retry 무의미, **longer cooldown 60s base max 300s** (5x longer cap)
  - **rationale**: 529 = service-wide overload signal (single retry sequence 영역 외, sustained high load 영역). exp-backoff 적용 시 cascade amplification risk → longer cooldown invariant.
  - **detection**: HTTP 529 status code (`"529"` substring 별도 detection enum 추가 영역 = 본 §결정 6 — §결정 1 4-tuple disjoint axis)

### §결정 7 — Retry primitive 위치 = skill body (ADR-039 closed 4-entry 보호)

Retry sequence 자체 implementation 위치 = `codeforge:rate-limit-429-mitigation` skill body 안 3-step procedure (탐지 / 대기 / 재시도). Orchestrator inline whitelist (ADR-039 §결정 2 closed 4-entry: 사용자 dialog / TodoWrite scratchpad / Read-only Q&A 답변 / Status report) 확장 0건.

- **rationale**: ADR-039 §결정 2 L110 verbatim "5번째 카테고리 추가 = ADR-039 amendment 의무. 본 closed enumeration 가 future '429 retry inline allowed' 압박을 차단" — closed enumeration 보호 우선 (RefactorAgent pattern 2 권고 + chief 결정 정합).
- **ADR-039 §결정 9 신설** (CFP-1354 Amendment N): §결정 2 4-entry 무변경 + §결정 9 carryover sunset_justification — rate-limit second-order risk 측정 = 본 §결정 7 + §결정 8 흡수.
- **alternative reject**: ADR-039 5번째 entry "429 retry inline allowed" 추가 = chief REJECT (InfraOp D-13 advocacy REJECTED, 본 결정 + ADR-039 Amendment N 정합).

### §결정 8 — Telemetry SSOT (§14 Lane Evidence marker + KPI dual-tier)

#### §결정 8.1 §14 Lane Evidence marker

`transcript` field 의무 marker:

```
[429-auto-retry: count=<N>, final_status=<success|failed>]
```

- regex (mechanical lint `429-retry-evidence-presence` warning tier, declaration-only Wave 1):

```
\[429-auto-retry: count=\d+, final_status=(success|failed)\]
```

#### §결정 8.2 KPI dual-tier

- `docs/kpi/429-incident.json` — weekly aggregate (cron, `rate-limit-fallback.json` precedent 답습)
- `docs/kpi/429-incident-history.jsonl` — append-only event log (ADR-106 `operational-signal-history.jsonl` precedent 답습)
- **schema**: §결정 10 secret redaction matrix 정합

### §결정 9 — §10 FIX Ledger vs §14 telemetry axis disjoint (ADR-067 RESET contamination 차단)

- **§10 FIX Ledger** = governance FIX root cause classification (ADR-067 max FIX 3/3 cap + RESET counter)
- **§14 Lane Evidence** = lane-spawn evidence audit trail (ADR-031 §결정 1)
- **429 incident marker** (`[429-auto-retry: count=N, final_status=...]`) = **§14 only** (운영 phase metric, ADR-104 정합)
- **§10 row append 금지**: 429 retry → fix:* label 미부착 + ADR-067 RESET counter 영향 0 (invariant 보존)
- **boundary violation 차단 invariant**: 본 §결정 9 = ADR-067 RESET contamination 차단 정합 (운영 phase telemetry vs governance FIX disjoint axis 명시 의무)

### §결정 10 — Secret redaction matrix (unconditional invariant ADR-068 I-3)

| 데이터 | 분류 | 처리 |
|---|---|---|
| `org_id` | Secret | **strip (collection-time)** — unconditional invariant (ADR-068 I-3 defense-in-depth) |
| `account_id` | Secret | 동상 strip |
| `session_uuid` | Internal | hash (SHA-256 truncated 8-byte) |
| `api_endpoint` | Internal | mask (domain only, path strip) |
| `timestamp` | Public | verbatim (KST `+09:00` ISO 8601, ADR-079 §결정 2) |
| `error_message` | Internal | verbatim (4-tuple enum match only, no user prompt verbatim) |
| `retry_count` / `cascade_depth` / `final_status` / `lane` / `agent_role` (enum) | Public | verbatim |

- **Retention**: 90일 raw event JSONL + 영구 weekly aggregate JSON (dual-tier — ADR-058 §결정 5 sunset_justification 면제, governance 영구 보존)
- **unconditional invariant rationale** (ADR-068 I-3 정합): org_id / account_id 수집 자체 금지 (defense-in-depth) — 후속 redaction step 의존 0 (collection-time strip)

## 결과

### 긍정

- **사용자 발화 cover**: `"Server is temporarily limiting"` 4-tuple detection + 5 sub-area surgical mitigation framework 신설 (Story §1 verbatim 영역 정합)
- **ADR-039 closed 4-entry invariant 보존**: 5번째 entry 신설 0 (RefactorAgent pattern 2 권고 + chief 결정)
- **ADR-057 §결정 2 invariant 보존**: cross-model substitution axis 무변경, within-model timing axis disjoint cross-ref
- **ADR-067 RESET contamination 차단**: §결정 9 §10 vs §14 boundary 명시 의무
- **ADR-068 I-5 dimensional empirical grounding 정합**: backoff curve empirical-source = AWS Marc Brooker 2015 + threshold 3건 [hypothesis] Phase 2 refine
- **ADR-082 §결정 6 retain pattern 답습**: `mechanical_enforcement_actions: []` declaration-only Wave 1 (pattern_count ≥ 2 재발 시 follow-up CFP MUST promote)

### 부정·trade-off

- **3 mechanical_enforcement_actions warning tier deferred-followup**: actual mechanical wire = Phase 2 sibling sub-Story carrier (Phase 1 PR scope 외)
- **`[hypothesis]` threshold (§결정 4 circuit breaker 3-window)**: Phase 2 telemetry refine 의무 = post-deploy actual incident rate 측정 후 사용자 확인 (immediate value 제한)
- **Retry primitive 위치 = skill body**: Orchestrator inline 0건 = retry overhead = skill spawn cost (mitigation: skill body decision tree caching, Phase 2 refine 영역)

### 영향 받는 코드·레이어·운영 경계

- **Orchestrator** (top-level Claude session) — detection 4-tuple match logic (ADR-039 inline whitelist 1번 entry 사용자 dialog scope 안 verify-before-trust, Story §2.1 verified state table 1st applied dogfood case 답습)
- **`codeforge:rate-limit-429-mitigation` skill body** — 3-step procedure (탐지 / 대기 / 재시도) + decision tree (Phase 0 brainstorm sequential 2-batch fallback)
- **§14 Lane Evidence transcript writer** — marker regex schema 정합
- **KPI artifact writer** (`docs/kpi/429-incident.json` + `429-incident-history.jsonl`) — §결정 10 redaction matrix 적용
- **debate-protocol-v1 v1.2 `pause_condition`** (declarative) — round N+1 진입 직전 cascade detection (별 carrier, version bump 결정 영역)
- **7 team-spec yaml** — `parallel_spawn_cap` + `spawn_stagger_ms` + `cascade_circuit_breaker` 3 field 신설 (ADR-044 Amendment N, atomic sibling sync)

## 해소 기준

N/A — permanent policy

`is_transitional: false` 영역 (Anthropic infra 429 = 운영 영구 fact, 사용자 plan upgrade 영역 disjoint). ADR-058 §결정 7 보안 ADR default presumption `false` 정합. ADR-064 §결정 7 evidence-gated symmetric ratchet 정합 — 강화 방향 (5 sub-area normative SSOT 신설), 약화 0건. sunset_justification 면제.

## 관련 파일

- [skills/rate-limit-429-mitigation/SKILL.md](../../skills/rate-limit-429-mitigation/SKILL.md) — §결정 7 retry primitive 위치 SSOT
- `mclayer/codeforge-internal-docs/plugin-codeforge/change-plans/cfp-1354-in-process-429-mitigation.md` — Phase 1 Change Plan carrier (dogfood-out per ADR-013, `doc-locations.yaml change_plan dogfood variant` 정합)
- `docs/kpi/429-incident.json` (Phase 2 scope) — §결정 8.2 weekly aggregate KPI
- `docs/kpi/429-incident-history.jsonl` (Phase 2 scope) — §결정 8.2 append-only event log
- `templates/github-workflows/429-incident-telemetry.yml` (Phase 2 scope) — telemetry workflow warning tier
- `templates/team-spec-*.yaml` (7 file) — ADR-044 Amendment N `parallel_spawn_cap` + `spawn_stagger_ms` + `cascade_circuit_breaker` field 신설
- [ADR-039](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — §결정 7 closed 4-entry 보호 + Amendment N §결정 9 carryover sunset_justification
- [ADR-044](ADR-044-phase-scoped-sequential-team.md) — Amendment N team-spec yaml schema 확장
- [ADR-057](ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) — §결정 3 sequential composition cross-ref (cross-model substitution axis disjoint)
- [ADR-064](ADR-064-decision-principle-mandate.md) — §결정 4 Trace 4 Amendment N surgical exception channel
- [ADR-067](ADR-067-fix-ledger-implementability-escalation.md) — §결정 9 RESET contamination 차단 cross-ref
- [ADR-068](ADR-068-boundary-completeness-invariants.md) — I-3 defense-in-depth (§결정 10) + I-5 dimensional empirical grounding (§결정 2)
- [ADR-082](ADR-082-write-time-self-write-verification-mandate.md) — §결정 6 retain pattern 답습 (declaration-only Wave 1)
- [ADR-097](ADR-097-paradigm-replacement-governance-anchor.md) — closed-set 3 조건 AND 미충족 (paradigm replacement 비대상)
- [ADR-104](ADR-104-operational-phase-definition.md) — 운영 phase 1st-class 정의
- [ADR-106](ADR-106-operational-signal-pmo-input-circuit.md) — 운영 metric → PMOAgent input 회로
- [ADR-108](ADR-108-label-registry-v2-frozen-baseline-description-carry-drift.md) — label-registry forcing function (description text raw grep count parity)

## Amendment 1 (CFP-2823 — session/usage-limit class 감지집합 편입 + fable-리밋 failover 합성)

**날짜**: 2026-07-24 KST · **carrier**: CFP-2823 · **방향**: ratchet **강화**(§결정 1 detection closed-set 확대, 약화 0). 본 Amendment 가 §결정 1 closed-set invariant("5번째 pattern 추가 = 본 ADR Amendment 의무")의 정확 이행이다. **§결정 1 base 4-tuple 은 byte-intact 보존**(rewrite 0) — 본 Amendment 가 class 2 literal 을 추가할 뿐이다. fable-리밋 opus failover 의 규범 SSOT = [ADR-141](ADR-141-all-opus-single-tier.md) Amendment 6; 본 Amendment 는 그 감지 SSOT + framework 합성 배치를 codify 한다.

### (a) 확장 rationale (firsthand 반증)

실관측 리밋 문자열 (2026-07-24, CFP-2823 진행 중 fable PL 이 세션 리밋으로 mid-run 조기종료하며 발화):

```
Agent terminated early due to an API error: You've hit your session limit · resets 10:20pm (Asia/Seoul)
```

이 문자열은 §결정 1 base 4-tuple(`rate limit` / `quota exceeded` / `429` / `Server is temporarily limiting`)과 substring **0/4 불일치**(firsthand — reproducer `any(p in s for p in base)` = exit 1 RED). 즉 §결정 1 이 사용자 요구(사용량/세션 한도 감지, CFP-2823 §1)를 **미커버**한다. → session/usage-limit class 를 §결정 1 closed-set 에 편입해야 커버된다.

### (b) 확장 감지집합 (본 Amendment = 확장 SSOT)

session/usage-limit 포함 detection = 다음 6 literal any-match (closed-set, no regex wildcard — §결정 1 invariant 승계):

```
"rate limit"
"quota exceeded"
"429"
"Server is temporarily limiting"
"session limit"
"usage limit"
```

- 앞 4 literal = **§결정 1 base 4-tuple, byte-frozen**(순서·문자 무변경). 뒤 2 literal = **본 Amendment 1 신규 class 2**: `"session limit"`(확정 — 2026-07-24 실관측) + `"usage limit"`(추정·미실측 — 요구사항-named 개념 커버, fail-open; (f) 참조).
- **별도 enum 신설 아님** — 단일 §결정 1 closed-set 확장(3→4 확장 선례[§결정 1 "Server is temporarily limiting" 편입, L97] 동형). literal-substring `no regex wildcard` invariant 유지(정규식 wildcard 도입 0).

### (c) enum single-SSOT 강화 (G1)

본 code-fence(6 literal) = detection enum 단일 source. `codeforge:rate-limit-429-mitigation` skill body / `docs/orchestrator-playbook.md` §3.0.12 / ADR-141 Amendment 6 = **prose cross-ref only**(중복 정의 0, §결정 1 "Single SSOT" 규율 승계). AC-4 discriminating check fixture 는 본 code-fence 를 **파싱해 enum source 로** 사용한다 — 하드코딩 사본 금지(fixture-vs-SSOT drift 차단).

### (d) fable-리밋 failover 합성 배치

ADR-141 Amendment 6(규범 SSOT)의 fable-리밋 opus failover 를 본 framework 에 합성한다:

- **§결정 3 step2 dead slot re-tenant** — step2(cross-model substitution)가 cross-ref 하던 구 ADR-057 §결정 2(sonnet rate-limit→opus)는 ADR-141 로 moot/dead 라 구조적으로 비어 있다. fable 브랜치가 신규 trigger(fable 리밋)로 그 slot 을 re-tenant(부활 아님 — ADR-057 Superseded 유지).
- **fable step1 bypass** — fable 리밋 시 step1(fable same-model exp-backoff soak)을 건너뛰고 step2(fable→opus)로 즉시 직행(Option A 즉시전환 — ADR-141 A6-2 근거 3층: reset long-horizon / 별개 pool / Retry-After trap). opus 착지 **후** 비로소 §결정 2 exp-backoff / §결정 3 step1·3·4 가 opus 를 same-model 로 재정박.
- **cascade depth count-in** — fable→opus hop = `cascade_depth` **1(COUNTS)**. opus 착지 후 opus 자기 within-model soak 은 미증가. opus soak 소진 후 cascade ≥ 2 = §결정 5 user manual resume only.
- **§14 격리** — failover = §14 전용 태그 `[rate-limit-failover:fable→opus]`(§결정 9 §10 FIX Ledger 금지 상속, 기존 §결정 8 `[429-auto-retry: ...]` 및 dead 태그 `[rate-limit-fallback:sonnet→opus]`/`[model-unavailable-fallback:fable→opus]` 와 비합산·별도 measurement).

### (e) 529 disjoint 재확인

529(`529` / `overloaded`) = pool-agnostic service-wide overload → **failover 감지집합 NOT-IN**. §결정 6(429 vs 529 disjoint — longer cooldown 60s→300s)이 correct handler 이며, 529 에 failover 적용 시 §결정 6 "cascade amplification risk" 정합으로 futile+amplifying. literal `429` ≠ `529`(substring 무접점) 확인 — 529 는 본 Amendment 확장 감지집합에 편입하지 않는다(운영 근거 = pool-agnostic overload, 단순 "enum 밖" 아님).

### (f) `usage limit` negated-context 정직 note + `429` over-match wart

- **`usage limit` = 추정·미실측** — 실관측 runtime 문자열은 `session limit` 뿐(`usage limit` 관측 0건, discriminating check 무기여). 유일 firsthand 등장 = 본 ADR §컨텍스트 §1(L54)의 **부정 문맥** `Server is temporarily limiting requests (not your usage limit)`. 부정 문맥 substring 매칭은 무해하나(fail-open bounded) literal 선정 근거는 부실 — 요구사항-named 개념(사용량 한도, CFP-2823 §1 intake 결정 3) 커버용으로 유지(over-inclusion 무해·bounded). 설계리뷰/구현 lane corroborate 대상.
- **`429` bare-substring over-match** — `429` 는 무관 문자열(예: `error 10429`)에 substring 매칭될 수 있는 bounded wart. no-regex-wildcard invariant 와 tension(좁히려면 word-boundary 필요하나 wildcard 금지)이나, 현재는 fail-open bounded 로 수용(§결정 1 base 이미 동일 성질). 좁힐지는 설계 재량.
- **case-sensitivity gap** — closed-set 대소문자 구분 substring 이라 `Session Limit`(대문자) 형태는 miss 가능. 실관측은 소문자 `session limit` 이라 현 위험 낮음 — literal 선정·case-fold 여부는 설계리뷰 escalate 후보(CFP-2823 §5.7).

## Amendment 2 (CFP-2944 — 한도류 신호 판별식 D primary 이관 + 발신자 전제(D-0) + §결정 5 축 분리)

**날짜**: 2026-08-12 KST · **carrier**: CFP-2944 · **status**: Proposed (Phase 1 draft — 착지 전) · **방향**: **양방향 ratchet**(감지 대상 클래스 확대[강화] ⊕ 감지 정의역 축소[오탐 제거], 각 방향 firsthand evidence 동반 — ADR-064 §결정 7).

**본 Amendment 가 하지 않는 것 (선언 우선)**: §결정 1 base 4-tuple 및 **Amendment 1 (b) 6-literal code-fence = byte 무변경**. literal 추가·삭제·순서 변경 0, 재열거 0, 경쟁 enum 신설 0. 따라서 §결정 1 closed-set invariant("5번째 pattern 추가 시 Amendment 의무")는 **미발동**이다. 본 Amendment 는 열거를 건드리지 않고 **판정 primary 를 열거 밖 상위 규칙으로 이관**한다.

### (a) 문제 — 열거 완전성 가정의 firsthand 반증

Amendment 1 은 감지집합을 4→6 literal 로 확장했으나 "열거로 닫힌다"는 가정 자체는 유지했다. CFP-2944 요구사항 lane 이 본 ADR code-fence 를 **파싱해**(하드코딩 사본 0) `any(p in s for p in lits)` 를 실행한 결과:

| 문자열 | 출처 | 6-literal any-match |
|---|---|---|
| `You've reached your Fable 5 limit. Run /usage-credits to continue` | CFP-2944 리뷰 PL 실사망 문구 (firsthand) | **0/6** |
| `Approaching 5-hour limit.` | 공식 support 12466728 | **0/6** |
| `5-hour limit reached - resets [time].` | 공식 support 12466728 (`blocking error message` 로 규정) | **0/6** |
| `5-hour limit resets [time] - continuing with usage credits.` | 공식 support 12466728 | **0/6** |
| `You've hit your session limit · resets 10:20pm (Asia/Seoul)` | 2026-07-24 실관측 (**대조군**) | 1/6 (`session limit`) |

제품 문면은 모델명·한도 창 길이·플랜에 따라 변하는 **가변 표층**이고 열거는 그 표층의 과거 스냅샷이다. 열거가 primary 인 한 §결정 3·ADR-141 Amendment 6 의 remedy 는 **실사례에서 점화되지 않는다**. 이는 같은 SSOT 의 같은 병리 3번째 발현(3→4→6 확장)이며, 4번째 확장(7번째 literal)으로는 닫히지 않는다.

### (b) D-0 발신자 전제 — 판정 정의역 (신설)

**D-0 (전제)**: 본 판정 절차의 정의역 = **본 세션 harness 가 실행하는 agent 계층이 발신한 종료·오류 신호**(Anthropic API/harness 발). 타 서비스·타 벤더 API 의 한도 신호(GitHub·외부 SaaS 등)는 **정의역 밖**이며 각자의 소관 통제로 라우팅된다.

- **firsthand reproducer (정의역 없이 발생하는 오착지)**: GitHub REST primary 한도 문면 `API rate limit exceeded for user ID 12345.` 은 6-literal 중 `rate limit` 에 **1/6 매칭**한다. §결정 1/Amendment 1 의 매칭은 즉시 확정이므로, D-0 이 없으면 **GitHub 한도가 Anthropic 축 처방**(fable→opus failover · usage credits · §결정 2 backoff)으로 착지한다 — 무효 조치 + 실결함 은폐.
- **D-0 은 fast-path 에도 소급 적용된다** — 즉 §결정 1/Amendment 1 감지집합의 **적용 전제**다. code-fence 는 무변경이며(전제는 fence 밖 prose), 열거는 D-0 을 통과한 신호에 대해서만 평가된다.
- **방향 정직**: 이는 감지 **정의역의 축소**(오탐 제거)다. 약화가 아니라 정확도 강화로 판정하는 근거 = ADR-141 A6-6 자기선언 — "오탐 = 더 높은 리스크(opus 낭비 + 실결함 은폐)".

### (c) 입력 표면 scope 불변식 — 판정 절차 전체에 부착

`docs/orchestrator-playbook.md` §3.0.12b 의 scope 문언은 현재 **6-literal fast-path 절에만** 소속되어 판별식을 덮지 못한다. 본 Amendment 는 이를 판정 절차 전체(fast-path ∪ 판별식 D)의 불변식으로 승격한다 — 원문 생략 없는 full-block 인용:

> **감지** = ADR-109 §결정1 Amendment 1 감지집합 any-match(6 literal — base 4-tuple + `session limit` + `usage limit`). enum authoritative SSOT = ADR-109 §결정1 Amendment 1 code-fence(**cross-ref only — 재열거 금지, 중복 정의 0**). scope 불변식 = error/termination notification 표면 한정(subagent substantive output 본문 NOT — false-positive hazard). 발동 표면 2종 = (a) spawn-시점 거부 ∪ (b) mid-run 조기종료(`Agent terminated early ...` task-notification).

**승격 후 scope (판정 절차 전체 적용)**: 판정 입력으로 허용되는 표면 = (a) spawn-시점 거부 ∪ (b) mid-run 조기종료 task-notification **2종 한정**. **비허용 표면**: subagent substantive output 본문 / 도구 반환 텍스트(PR·Issue 본문·WebFetch·외부 워커 출력·repo 파일) / 사용자 외 제3자가 내용을 통제할 수 있는 임의 텍스트. 본 scope 는 판별식 D 가 열거보다 **넓은 문면**을 받아들이기 때문에 오히려 더 엄격히 요구된다 — 넓은 판정면 ⊕ 무경계 입력면 = 분류 입력 주입 취약(CFP-2944 §7 T6).

### (d) 판별식 D (primary)

D-0 을 충족하고 (c) scope 표면에서 도착한 종료·오류 신호가 다음 3항을 **전부** 충족하면 한도류로 분류한다:

| 항 | 내용 |
|---|---|
| **D-i 자원 소진 지시** | 신호가 사용량·한도·요금제 자원의 소진 또는 경계 도달을 지시한다. 모델명·한도 창 길이·플랜명은 **가변 표층**(`Fable 5 limit` / `5-hour limit` / `session limit`) — 특정 문면에 의존하지 않는다. 여기서 "창" = **한도 리셋 창**(5시간 rolling·주간)이며 **컨텍스트 창(context window)과 무관**하다(컨텍스트 창 초과 = D-i 불충족, 요청 형상 축) |
| **D-ii 작업 결함 무관** | 원인이 요청 내용의 결함(로직 오류·입력 오류·권한 오류·모델 미존재)이 아니라 **자원 가용성**이다 |
| **D-iii 회복 가능** | 시간 경과 또는 대체 자원(usage credits · 별개 모델 pool · 과금 전환)으로 해소 가능한 class 다 |

**fast-path 의 지위 (강등 — 폐지 아님)**: §결정 1/Amendment 1 6-literal = **비망라 기계 fast-path**. 매칭 = 한도류 **확정**(D-i~iii 재평가 불요, 단 D-0·(c) scope 는 여전히 전제) → 착지 분기는 (e) 로 재판정. **미매칭은 "한도 아님"을 의미하지 않는다** — 미매칭 시 판별식 D 로 판정을 계속한다.

### (e) D 의 출력 = 4치 (라우팅 표)

| 출력 | 성립 조건 | 라우팅 | 그 입력 클래스를 이미 지배하는 통제 |
|---|---|---|---|
| **D-out-1 한도류·자기해소** | D 충족 ∧ remedy 가 **이미 활성화된 대체 자원**(활성 credits 잔액·별개 모델 pool)이거나 Orchestrator 액션 없이 배경에서 해소 | 의지적 정지 사유 아님 — 계속 | 없음 (본 축이 채우는 공백) |
| **D-out-2 한도류·액션의존** | D 충족 ∧ remedy 실행이 **사용자·관리자 액션**(활성화·결제·cap 인상)에 의존 | 1회 통지 → 대기·중단 금지 → 제어 회복 시 계속 | ADR-025 §결정 6 whitelist #1(User environment 변경 의무 = 정당 통지) — 통지는 **보존**, "통지 후 무기한 대기"만 금지 |
| **D-out-3 한도류 아님 (확정된 부정)** | N-a 해당 **또는** D 3항 중 1+ 가 **명확히** 미충족 | 본 축 무개입 — 각 축 기존 소관 | ADR-057 §결정 4 · §결정 6(529 cooldown) · ADR-117 §결정 3 |
| **D-indeterminate 평가 불확정** | fast-path 미매칭 ∧ D 3항을 확정 평가할 수 없음(정보 부족·문면 모호) ∧ N-a 미해당 | **미분류** — remedy 라우팅 무개입(아래 배타 지배 인용), 의지적 정지 사유로도 삼지 않음 | `docs/orchestrator-playbook.md:528` / `ADR-057:149` — 미분류 → **failover 미발동 + task-failure 분류**(silent fallback 금지) |

**`시간 경과` 의 위치 (외연 겹침 해소)**: `시간 경과` 는 remedy **선택지**가 아니라 Orchestrator 액션 없이 흐르는 **배경 해소 사실**이다. 따라서 D-out-1 의 성립 조건에 배경 사실로 기술되며 D-out-2 의 "액션 의존" limb 과 겹치지 않는다("고른다"는 행위가 없으므로 remedy 선택 축에 등장하지 않는다).

**D-out-3 ⊥ D-indeterminate (disjoint 못박기)**: 전자는 "한도류가 아님"이 **확정**된 상태, 후자는 **판정 자체가 확정되지 않은** 상태다. 둘을 합치면 "모르는 것"이 "아니라고 확정된 것"으로 흘러 자동 처방이 붙는다 — 이 경계가 본 Amendment 가 여는 유일한 신규 상태이며, 그 상태의 remedy 라우팅은 위 표의 배타 지배 통제가 그대로 유지한다(본 Amendment 는 인용만 하고 개정하지 않는다).

### (f) negative control — 2 방향

- **(N-a) 한도류 자체가 아님 → D-out-3**: model-unavailable · floor 미달(버전 문제 — 시간·credits 로 해소 불가, D-iii 불충족) / `stop_reason: refusal`(D-ii 불충족) / 로직·입력·권한 오류(D-ii 불충족) / **컨텍스트 창 초과**(요청 형상 축 — D-i 불충족) / `529`·`overloaded`(별개 축 — §결정 6 cooldown) / **타 벤더 API 한도**(D-0 정의역 밖 — GitHub primary·secondary rate limit 등). (N-a) 가 있어야 판별식이 "모든 실패를 한도로 읽는" 반대 방향 오분류로 번지지 않는다.
- **(N-b) 한도류이나 자기해소 아님 → D-out-2 필수(D-out-1 금지)**: usage credits **미활성**/활성화 액션 필요(`Enable usage credits to continue using Claude` — support 11145838)가 유일한 공식 anchor 보유 사례. 구조 동형 후보(결제 수단 실패 · 구독 만료 · 조직 spend cap 도달 · **주간 한도**)는 `[미검증 — 구조 동형 후보, 공식 anchor 미확보]` 로 표기하며 제품 사실로 단정하지 않는다(ADR-119). 판정 기준은 문면이 아니라 **구조적 술어** — "remedy 실행 주체가 Orchestrator 인가, 사람인가". 사람이면 D-out-2.

### (g) 기록 규약 — 판정 신호 원문 verbatim 기록 금지 (§결정 10 확장)

§결정 10 redaction matrix 는 `error_message` 를 `verbatim (4-tuple enum match only, ...)` 로 규정한다. 판별식 D 로 분류된 신호는 정의상 **matched literal 이 부재**하므로 그 규정의 정의역 밖이며, 감사를 유지하려 원문 기록으로 흐르면 §결정 10 과 충돌한다. 본 Amendment 는 다음을 규약한다:

- **기록 허용 3요소**: ① 분류 결과(`D-out-1|D-out-2|D-out-3|D-indeterminate`) ② 판정 limb(어느 항이 성립/불성립인지) ③ 근거 요약 **1줄**(모델-클래스·자원 축의 추상 서술).
- **금지**: 신호 **원문 verbatim** / plan·model tier 문면(`Fable 5 limit` → "모델-클래스 한도 도달" 로 추상화) / credits 잔액·금액 / 결제·과금 식별자 / `org_id`·`account_id`(§결정 10 기존 금지 승계).
- **근거**: 본 규약이 늘리는 기록 트래픽의 착지면에는 **공개 표면**이 포함된다(§14 lane evidence → PR body 미러, `docs/kpi/*.jsonl` 커밋). 기존 deny-list regex 는 로컬 원장 경로에만 적용되므로 공개 착지면에는 redact 층이 부재하다 — 자동 redaction 층 신설 대신 **저작 규율**로 막고 그 한계를 (l) 에 정직 declare 한다.
- matched literal(6중 1)은 닫힌 값공간이라 기록 허용(Amendment 1 auditability 권고 무손상).

### (h) D-out-1 자기확증 반증 축

D-iii(회복 가능)는 **예측**이므로 반증 축이 없으면 D-out-1 이 무한 자기확증한다. 다음을 재판정 의무로 둔다: **동일 신호가 연속 2회 이상 D-out-1 로 판정됐는데 작업이 전진하지 않으면** 자기해소 가정이 반증된 것으로 보고 D-iii 불충족을 재평가한다(→ D-out-2 또는 D-out-3/D-indeterminate). `연속 2회` 임계는 **임의 선택**이다 — 반증 축의 *존재* 가 요구사항이고 값은 운영 관측으로 조정 가능하다(정직 declare).

### (i) §결정 5 축 한정 개정 — 재시도 중단 ⊥ 작업 중단

§결정 5 의 현행 문언은 다음과 같다 — **생략 없는 인용**(§결정 5 본문 전건 = intro 조건절 1 + bullet 3):

> `cascade_depth` 정의 = 단일 user request 안 retry sequence 의 nested cascade level. depth ≥ 2 (예: same-model 429 → Opus fallback → Opus 429 → 2차 retry burst) 시:
>
> - **자동 재시도 금지** (ADR-057 §결정 2 invariant verbatim 답습)
> - **user manual resume only** — `AskUserQuestion` escalation 또는 사용자 turn 대기
> - **`docs/kpi/429-incident-history.jsonl` `cascade_depth` field append-only event log** (ADR-106 운영 metric → PMOAgent input 회로 정합)

**보존(무변경)**: `cascade_depth` 정의 · depth ≥ 2 판정 · **자동 재시도 금지**(bounded retry 상한 = 비용 폭주·429 cascade 증폭 가드) · `AskUserQuestion` escalation 경로 · KPI append.

**축 분리(개정)**: `user manual resume only` 의 정의역은 **재시도(동일 호출 재발행) 축 한정**이다. 이 조항은 "그 시점 이후 Orchestrator 의 모든 작업 진행이 사용자 turn 을 기다려야 한다"는 뜻이 **아니다**. cascade 상한 소진 후에도 — ① 실패한 호출의 재발행은 금지되고 ② **남은 독립 작업으로의 전진은 계속**된다. "사용자 turn 대기"는 재시도 재개의 조건이지 작업 진행의 조건이 아니다.

**remedy 단조 비용 사다리 (예산 곱셈 차단)**: 한도 축이 미확정인 상태에서 유비용 remedy 를 순차로 여러 개 시도하면 예산이 곱해진다. 따라서 remedy 는 다음 사다리로만 진행한다:

| rung | 내용 | 비용 | 진입 조건 |
|---|---|---|---|
| R0 축 재판정 | fast-path → 판별식 D → 4치 출력 | 0 | 항상 첫 단계 |
| **R1 전진(forward)** | 실패 호출을 재발행하지 않고 **남은 독립 작업**으로 진행 | 0 | 항상 |
| R2 1회 통지 | remedy 주체가 사람이면 whitelist #1 통지 1회 후 R1 복귀 | 0 | D-out-2 |
| R3 canonical remedy | 축이 **확정된 경우에만** 그 축 고유 remedy **정확히 1종** | 유비용 (기존 상한 내) | 축 확정 ∧ 해당 축에 remedy 실재 |
| R4 낙하 | R3 실패 시 두 번째 유비용 remedy 로 가지 **않고** R0→R1/R2 로 낙하 | 0 | R3 소진 |

- **I-1 예산 곱셈 차단**: 유비용 rung(R3) 진입은 **축 확정이 전제조건**이다. 축이 확정되면 remedy 는 1종으로 결정되므로 "여러 개 시도"가 구조적으로 불가하고, 미확정(D-indeterminate)이면 R3 자체가 닫힌다(위 (e) 배타 지배 통제).
- **I-2 전진 ≠ 재시도**: 재시도 counter 는 **동일 호출 재발행**을 센다. R1 전진은 다른 작업이므로 backoff·cascade·per-spawn 어느 counter 도 증가시키지 않는다. 본 Amendment 는 **어떤 경로에도 신규 재시도 예산을 추가하지 않는다**(신규 counter 0).
- 무변경 확인: §결정 2 backoff max 6/60s/≤75s · Retry-After override · §결정 3 sequential composition · §결정 4 CB 3-window · §결정 6 529 cooldown · ADR-141 Amendment 6 per-spawn 1회 · 미분류 재spawn 0 · Amendment 7 cap-down.

### (j) 정직 천장 (over-claim 금지)

1. **D 는 모델 판정이다** — 기계 검증 표면이 없다. fast-path 만 기계적이고 D-0·D-i~D-iii·4치 라우팅은 prompt-mandate(advisory)다. "판별식 도입 = 감지 100%" 주장 금지.
2. 본 Amendment 는 **비의지적 종료를 0 으로 만들지 않는다** — 한도 순간 토큰 발화 불가 구간·in-flight 즉사는 정의역 밖(OOS)이다.
3. 감지 미탐(D 미충족 낙하)의 안전 방향 = **failover 미발동**(현행 동작 degrade) 유지 — fail-open bounded, 회귀 0.
4. (g) 기록 규약은 **저작 규율**이며 공개 착지면의 자동 redaction 층이 아니다. 규율 미준수 시 유출 가능성은 잔존한다(수용 리스크, 명시 declare).

### Cross-ref

- §결정 1 / Amendment 1 (b) — 감지집합 code-fence(**byte 무변경 · cross-ref only**). 본 Amendment 는 그 열거의 *지위* 만 재해석한다.
- §결정 5 — (i) 축 한정 개정 대상. §결정 2/3/4/6 = 무변경.
- §결정 10 — (g) redaction matrix 확장(비-enum 신호 기록 규약).
- [ADR-141](ADR-141-all-opus-single-tier.md) Amendment 6 A6-3(a) / Amendment 8 — Orchestrator 세션 축 재개봉(본 Amendment 는 감지·재시도 축, Amendment 8 은 행위 규범 축).
- [ADR-025](ADR-025-stop-discipline-non-whitelist-as-defect.md) Amendment 4 — 한도류 신호 발 의지적 정지의 stop-discipline 착지(본 Amendment = 판정, ADR-025 = 정지 적법성). **§A4-8 = 본 carrier 저작물 전체의 자기적용 결박 총칙** — 판정문 verbatim SSOT 1곳, 본 Amendment 는 pointer 만 둔다. 본 Amendment 의 문면 축 술어((i) full-block 인용 규율 · (j) 천장 서술)도 그 dry-run 대상이며 결과는 Story `CFP-2944` §7.16 에 기록된다(런타임 축 술어 — D-0 · 판별식 D · remedy 사다리 — 는 정의역이 신호·행동이라 문면 자기적용 대상이 아니다).
- [ADR-057](ADR-057-orchestrator-opus-mandate-and-sonnet-opus-fallback.md) §결정 4 / `docs/orchestrator-playbook.md:528` — 미분류 remedy 라우팅 **배타 지배**(인용만, 개정 0).
- [ADR-119](ADR-119-research-before-claims.md) — 외부 제품 사실 인용 규율(공식 anchor 미확보 항목의 `[미검증]` 표기).
