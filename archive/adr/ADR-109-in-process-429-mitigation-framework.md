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
