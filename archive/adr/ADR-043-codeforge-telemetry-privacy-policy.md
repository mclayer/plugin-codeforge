---
adr_number: 43
title: Codeforge telemetry privacy policy
date: 2026-05-09
status: Accepted
category: orchestration-discipline
carrier_story: CFP-283
supersedes: null
amends: ADR-029  # §결정 2 sanitize policy 적용 범위 확장 (narration → ledger 통합 SSOT)
related_adrs:
  - ADR-025  # stop discipline (stop-event-v1 deferred slot)
  - ADR-029  # phase execution visibility (sanitize policy SSOT 통합)
  - ADR-039  # subagent default (Phase 1 trust model precedent)
  - ADR-042  # measurement channel architecture (sibling — privacy concern 분리)
  - ADR-115  # runtime hook enforcement policy (hook_source / hook_decision field origin — Amendment 1 carrier)
  - ADR-142  # Orchestrator-self context 규율 (Amendment 3 carrier — self-context proxy field set allow-list 확장)
  - ADR-155  # dev-process observability substrate (Amendment 4 carrier — dev-process-event redaction 표면 상속·확장)
related_stories:
  - CFP-283
  - CFP-1744
  - CFP-2572
related_cfps:
  - CFP-283
  - CFP-1744
  - CFP-2572
related_files:
  - docs/inter-plugin-contracts/stop-event-v1.md
  - docs/project-config-schema.md
  - docs/consumer-guide.md
  - docs/domain-knowledge/orchestrator-discipline/measurement-channel.md
is_transitional: false
amendment_log:
  - amendment: 1
    date: 2026-05-27
    carrier_story: CFP-1744
    summary: "§결정 2 Allow-list 16 → 18 field 확장 — hook_source (enum: stop/subagent-stop) + hook_decision (enum: record-only) 2 optional field 추가 (stop-event-v1 v1.1 MINOR bump 동반). ADR-115 §결정 2 block 금지 binding constraint 정합. MINOR 영역 (optional field 추가 = backward-compat, ADR-008 SemVer 정합)."
  - amendment: 2
    date: 2026-06-24
    carrier_story: CFP-2393
    summary: "spawn-event-v1 telemetry channel 확정 (Epic CFP-2391 S3). §결정 1 future→current (spawn-event-v1 = current opt-in channel) + §결정 2 Allow-list 에 spawn-event-v1 19-field set 추가 (별 channel Allow-list, enum/numeric/hash only — free-form string 0건) + §결정 3/4/5 inherit 선언 + **T-INFO-5 transcript content/path HARD invariant** (NEW privacy decision — spawn-event 가 transcript content/transcript_path 절대 미저장, numeric only) + **T-INFO-7 sha256 identity** (actor/parent_event_id sha256 hash, raw 금지 — spawn-event 한정. stop-event runtime raw bug 수정은 본 Amendment 미위임, 별 follow-up). MINOR (additive field set + inherit + privacy 강화 방향, ADR-008 SemVer)."
  - amendment: 3
    date: 2026-07-05
    carrier_story: CFP-2572
    summary: "§결정 2 Allow-list 에 self-context proxy record type 추가 (ADR-142 §결정 4 carrier — Orchestrator lead-self context 규율 L7). record-only proxy field 6종: schema_version(const) / session_id(sha256) / turn_index(int monotonic) / delegation_ratio(float 0.0–1.0 coarse) / pre_tokens(int bucketed, compact_boundary.preTokens 출처) / cause_category(CLOSED enum, domain-agnostic 7-value). numeric/enum/hash only — free-form string 0건 (T-INFO-8 정합) + transcript content/path 미저장 (T-INFO-5 상속) + opt-in default-false 상속 + hook_decision=record-only (Amendment 1 §결정 2 non-blocking). lead-self proxy = ground-truth 아님(ADR-119 verbatim). 정확한 spawn-event-v1 contract field-set 통합·count reconciliation = Phase 2 contract bump 확정. MINOR (additive record type + inherit + privacy 강화 방향, ADR-008 SemVer)."
  - amendment: 4
    date: 2026-07-15
    carrier_story: CFP-2687
    summary: "dev-process-event-v1 telemetry channel privacy 확정 (Epic #2686 Story A, ADR-155 sibling). dev-process-event 는 stop/spawn 이 마주한 적 없는 rich-content(프롬프트/diff/tool-call/findings/산출물) 를 evidence-blob-store 에 저장하는 net-new leak surface 를 마주한다. (A) §결정 1 always-on 비대칭 codify — wrapper-self dogfood scope=always-on(checkout-identity 파생, user-settable bool 아님) / consumer scope=opt-in default-false 무약화(ADR-064 §결정7 extend-only, T-DPE-9 consumer floor 하방 override 불가) + INV-8 redaction-precedes-always-on(always-on 이 redaction 우회 불가). (B) §결정 2 dev-process-event index tier 별도 channel allow-list — enum/numeric/hash/상관ID/blob-ref only, free-form content 0(T-INFO-8), emit_source discriminator. (C) §결정 3 deny-regex 6→7종 — 절대/home-prefixed 경로 pattern 신규(repo-relative 경로는 보존 — diff 진단 신호 public) + Authorization/Cookie 헤더 + cloud-key(gitleaks 차용) + env dump·자격증명 subprocess = capture 제외. (D) Amd2 §D 확장 — redacted-blob tier = T-INFO-5 no-conflict 신규 표면(INV-8a hash-over-redacted / INV-8b blob-before-index / T-DPE-2 hash-oracle 봉인 / audit enum redaction_applied·count·rules_fired, 매칭 secret 원문/hash 절대 미기록 T-DPE-8). resource-safety honest-ceiling — 무증거 ReDoS-safe 단정 금지, born-safe bound(byte/line cap+timeout)만, proof=Phase 2 SecurityTest. MINOR (additive channel allow-list + deny-regex 확장 + privacy 강화 방향, ADR-008 SemVer)."
mechanical_enforcement_actions: []
---

# ADR-043: Codeforge telemetry privacy policy

## 상태

**Accepted (2026-05-09)** — carrier_story = CFP-283. ADR-042 sibling Phase 1 PR. Privacy policy SSOT 단일화 — narration (ADR-029) + ledger (ADR-042) sanitize 통합.

## 컨텍스트

### 사용자 발의 + cross-cutting concern 분리 근거

CFP-283 ADR-039 §결정 9 deferred measurement channel slot 처리 시 SecurityArch substantive 적극 권고:

- **Privacy = cross-cutting concern**. ADR-042 architectural decision + ADR-043 policy decision 분리가 maintainability ↑.
- **재사용성** — future ledger 신설 (spawn-event-v1 land 시 / 향후 어떤 telemetry 든) 동일 정책 inherit 가능.
- **SSOT 통합** — ADR-029 §결정 2 sanitize policy (narration scope) + 본 ADR ledger sanitize 통합 = 단일 privacy ADR 가 narration + ledger sanitize SSOT.

### 외부 fact (Researcher §6.5 verbatim)

- **GitHub CLI opt-out 비판 사례** — default-on telemetry + post-hoc opt-out = trust 위반 (https://github.com/cli/cli/issues/9897 등 community 이슈)
- **Divvi Up DAP (IETF)** — distributed aggregation protocol — raw event 미공유, aggregate 만 share (https://divviup.org/) — Phase 2 cross-host 통합 reference
- **arxiv 2507.06350 LDP (Local Differential Privacy)** — agent telemetry 도메인 LDP 적용 사례 — Phase 2 dashboard cold tier sanitize 참고

### Gap

1. **Codeforge family privacy SSOT 부재** — ADR-029 §결정 2 sanitize policy 가 narration scope 한정. ledger sanitize 정책 codification 부재 (CFP-283 신설 없으면 ledger 도입 불가능).
2. **Opt-in default false invariant 미codification** — ADR-039 Phase 1 doc-only trust model 패턴 정합 의무지만 별도 ADR 부재.
3. **Allow-list vs Deny-list 기준 미정의** — sanitize 책임 (capture 시점 / aggregate 시점) 불명.
4. **Cross-host telemetry 통합 정책 부재** — wrapper-vs-consumer ledger isolation (ADR-042 §결정 9) 부재 시 raw event leak 위험.
5. **PII / secret pattern 미열거** — 한국 도메인 (주민번호) / API key / GitHub PAT / email 등 redact 대상 미codification.

## 결정 (5)

### 결정 1 — Opt-in default false invariant (모든 telemetry channel 적용)

**모든 codeforge telemetry channel** (current: stop-event-v1 / future: spawn-event-v1 등) = opt-in default false.

- consumer overlay `.claude/_overlay/project.yaml` `telemetry.enabled: false` (default).
- per-channel granular flag (`telemetry.channels.<channel>: false` default).
- global `enabled: false` 시 모든 channel disabled (override 불가능 — global gate).
- **wrapper dogfood always-on enforcement**: Phase 2 enforcement CFP 시 도입 (env flag / hook / runtime validation 모두 본 ADR scope 외 — Phase 1 doc-only strict invariant 보존). Phase 1 = wrapper dogfood 도 default false + 사용자 explicit opt-in 의무 (consumer 와 동일 trust model).

위반 시 (default false 인데 ledger write 발생) = `policy_violation` (defect). lint = TestContractArch §8.4 후보 5 (opt-in default false invariant — ADR-042 §검증 채널 cross-ref).

근거:
- consumer 측 silent telemetry = trust 위반 (GitHub CLI opt-out 비판 precedent)
- ADR-039 Phase 1 doc-only trust model 패턴 정합
- 사용자 명시 directive 없는 한 measurement opt-in = 사용자 자율

### 결정 2 — Allow-list ONLY field whitelist (capture 시점)

**Capture 시점 sanitize = Allow-list ONLY**. stop-event-v1 schema field (ADR-042 §결정 2 enumerated + CFP-1744 Amendment 1) 외 field capture 금지:

```
event_id / schema_version / timestamp / story_key / phase_label / lane_label /
reason_class / reason_class_subclass / actor / iter / decider_pick /
override_marker / recovery_action / outcome / consumer_scope / parent_event_id /
hook_source / hook_decision
```

**v1.0 (CFP-283 origin, 16 field)**:
```
event_id / schema_version / timestamp / story_key / phase_label / lane_label /
reason_class / reason_class_subclass / actor / iter / decider_pick /
override_marker / recovery_action / outcome / consumer_scope / parent_event_id
```

**Amendment 1 (CFP-1744, 2026-05-27) — 18 field 확장**:
- `hook_source`: enum `{"stop", "subagent-stop"}` optional — emit 한 hook 종류 (non-sensitive)
- `hook_decision`: enum `{"record-only"}` optional — non-blocking marker (non-sensitive)

추가 field capture = MINOR change (optional field) 또는 BREAKING change (필수 field) → ADR-042 amendment 의무 + 본 ADR-043 §결정 2 갱신 의무 (cross-ref). optional field 추가 = MINOR (ADR-008 §결정 2 정합 — v1.0 reader 가 skip 가능).

근거:
- Allow-list = future expansion 시 explicit ADR review 강제 (silent expansion 차단)
- Deny-list 단독 = unknown unknown 위험 (새 PII pattern 미식별 시 leak)
- Allow-list + Deny-list 2-layer (defense in depth) = §결정 3

### 결정 3 — Deny-list regex (capture 통과 후 2차 안전망 — defense in depth)

Allow-list 18 field 중 (v1.0 origin 16 + v1.1 Amendment 1 2 optional) `reason_class_subclass` (free-form string) / `actor` (session ID hash) / `recovery_action` 등 string field 의 capture 시점 redact regex:

| Pattern | Regex | 대상 |
|---|---|---|
| API key / credential | `(api[_-]?key\|secret\|token\|password\|bearer)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}` | OAuth / API token / DB credential |
| GitHub PAT | `ghp_[A-Za-z0-9]{36}` | classic GitHub Personal Access Token |
| GitHub fine-grained PAT | `github_pat_[A-Za-z0-9_]{82}` | fine-grained PAT |
| 한국 주민번호 | `\d{6}[-\s]?\d{7}` | 13-digit 한국 주민등록번호 |
| Email | `[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}` | RFC-5321 email |
| Hex≥32 | `[a-f0-9]{32,}` | hash / private key / TLS cert fingerprint |

**Match → redact** (`[REDACTED:<rule_name>]` placeholder), **NOT block**. capture 자체는 진행 (정합성 보장 — schema validation 통과).

scope 적용:
- **stop-event-v1 ledger** (본 ADR primary scope) — capture 시점 regex 적용
- **stderr narration** (ADR-029 §결정 2 SSOT 통합) — narration 발화 시점 regex 적용 (기존 ADR-029 §결정 2 sanitize policy 가 본 ADR-043 §결정 3 으로 SSOT 통합)

future ledger (spawn-event-v1 land 시) = 본 §결정 3 동일 적용 의무.

### 결정 4 — Sanitize SSOT 통합 (ADR-029 §결정 2 amends)

ADR-029 §결정 2 (phase narration sanitize policy) sanitize 적용 범위 = **narration (stderr) + telemetry ledger (본 ADR-043 §결정 3 정합) 양쪽 unified SSOT**. CFP-283 carrier 로 ADR-029 §결정 2 Amendment 1 (2026-05-09) land — ADR-029 frontmatter `amendment_log[]` entry 추가 + 본문 amendment paragraph 명시.

근거:
- privacy = cross-cutting concern (narration + ledger 동일 정책)
- single source of truth = update / audit 비용 ↓
- ADR-029 narration scope 한정 SSOT 가 ledger 신설 시 분기 — 분기 회피

**SSOT 분담**:
- ADR-029 §결정 2 (Amendment 1 후) = format / 한국어 lane / stderr-only invariant + sanitize 적용 범위 (narration + ledger 양쪽) SSOT
- 본 ADR-043 §결정 3 = sanitize Deny-list regex 6 pattern + Allow-list ONLY 18 field SSOT (v1.0 16 + v1.1 Amendment 1 2 optional)

양쪽 SSOT 변경 시 sync 의무 (cross-ref invariant). future ledger (spawn-event-v1 land 시) = 본 §결정 4 가 정의하는 unified scope 자동 inherit.

### 결정 5 — Wrapper-vs-consumer ledger isolation + Phase 2 cross-host DAP deferred

ADR-042 §결정 9 cross-ref:

- **Phase 1 invariant**: wrapper / consumer ledger storage path 분리. cross-host raw event leak 금지 (T-INFO-4 SecurityArch P0 위협 대응).
- **Phase 2 deferred**: cross-host telemetry 통합 (Divvi Up DAP / aggregate report 형식) — 별도 후속 CFP. raw event 미공유 + aggregate 만 share 가 default.

LDP (Local Differential Privacy, arxiv 2507.06350) = Phase 2 dashboard cold tier 적용 후보 (현재 미적용 — Phase 1 scope 외).

본 §결정 = SecurityArch P0 위협 T-INFO-4 (consumer cross-host) 대응.

## 회피된 대안

### 대안 A — Privacy 정책을 ADR-042 §결정 5-6 inline (별도 ADR-043 미신설)

**거부 이유** (SecurityArch substantive 적극 권고 verbatim):
- privacy = cross-cutting concern (future ledger 신설 시 재사용)
- ADR-029 §결정 2 sanitize policy SSOT 와 통합 가능 (단일 privacy ADR)
- ADR-042 = architectural decision, ADR-043 = policy decision — SSOT 분리가 maintainability ↑

채택 = 본 ADR-043 sibling Phase 1 PR.

### 대안 B — Deny-list ONLY (Allow-list 미적용)

**거부 이유**:
- unknown unknown 위험 (새 PII pattern 미식별 시 leak)
- Allow-list = future expansion 시 explicit ADR review 강제

채택 = §결정 2 Allow-list ONLY + §결정 3 Deny-list 2-layer.

### 대안 C — Opt-in default true (always-on with post-hoc opt-out)

**거부 이유**:
- GitHub CLI opt-out 비판 precedent
- ADR-039 Phase 1 doc-only trust model 패턴 정합 위반

채택 = §결정 1 default false (wrapper / consumer 동일 trust model — Phase 1 doc-only strict). wrapper dogfood always-on enforcement (env flag / hook / runtime validation) = Phase 2 follow-up CFP.

### 대안 D — Phase 1 즉시 cross-host DAP 통합

**거부 이유**:
- DAP / LDP 구현 복잡도 ↑↑
- raw event leak 위험 (Phase 1 ROI 미충분 시 over-engineering)
- ADR-042 §결정 11 ROI gating 패턴 정합 (30+ post-merge-counters run 후)

채택 = §결정 5 Phase 2 deferred.

## 외부 fact (Researcher §6.5 reference)

1. **GitHub CLI opt-out 비판** — community 이슈 (default-on telemetry + post-hoc opt-out = trust 위반)
2. **Divvi Up DAP (IETF)** — https://divviup.org/ — distributed aggregation, raw event 미공유
3. **arxiv 2507.06350 LDP** — Local Differential Privacy 적용 사례 (Phase 2 reference)
4. **OWASP Logging Cheat Sheet** — sensitive data redaction patterns (https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

## 검증 채널

본 ADR 의 검증 채널 (TestContractArch §8.4 정합):

1. **Opt-in default false invariant lint** — `docs/project-config-schema.md` `telemetry.enabled: false` default + consumer-guide § "Telemetry opt-in" cross-ref 존재.
2. **Allow-list ONLY enforcement lint** — stop-event-v1 schema 18 field 외 추가 시 lint FAIL (BREAKING change → ADR-042 + ADR-043 amendment 의무).
3. **Deny-list regex coverage lint** — 6 redact pattern 정합 검증.
4. **ADR-029 §결정 2 amendment invariant** — ADR-029 frontmatter `amendment_log[]` CFP-283 entry 존재 + ADR-029 §결정 2 본문 Amendment 1 paragraph 존재 + ADR-043 §결정 4 cross-ref link 양방향 정합 (CFP-283 carrier Amendment 1, 2026-05-09 land 완료).
5. **wrapper-vs-consumer isolation lint** — ledger storage path 분리 (wrapper `mclayer/plugin-codeforge` vs consumer repo).

5 후보 모두 = follow-up CFP (Phase 2 enforcement 도입 시 동반 land — 분리 land = partial enforcement 의미 없음, Phase 1 trust model 정합 — ADR-042 §검증 채널 SSOT 정합). 후속 CFP 번호 = post-merge-counters.jsonl 30+ run ROI 평가 후 발의 시 할당 (current 미배정).

## 결과

### 영향 file (wrapper repo)

- `docs/adr/ADR-043-codeforge-telemetry-privacy-policy.md` (본 file)
- `docs/inter-plugin-contracts/stop-event-v1.md` (Allow-list ONLY 18 field 적용 + Deny-list regex 명시 (v1.1 Amendment 1 후))
- `docs/project-config-schema.md` (telemetry block — opt-in default false)
- `docs/consumer-guide.md` § "Telemetry opt-in" (default false 명시)
- `docs/domain-knowledge/orchestrator-discipline/measurement-channel.md` (privacy 정책 cross-ref)
- `docs/adr/ADR-029-phase-execution-visibility-expansion.md` (Amendment 1 — frontmatter `amendment_log[]` + §결정 2 amendment paragraph, sanitize 적용 범위 narration → narration + ledger unified SSOT, CFP-283 carrier 2026-05-09 land 완료)

### 비-영향

- 6 lane plugin 변경 0건 (privacy policy = wrapper / consumer Orchestrator scope)
- inter-plugin contract 6 변경 0건
- ADR-031 §14 lane evidence write monopoly 무변
- Story §10 FIX Ledger 무변

### Reversibility

- Yes — 본 ADR `status: Deprecated` + Allow-list ONLY 정책 revert 시 Phase 1 trust model 복원
- Deny-list regex 6 pattern 추가 / 삭제 = minor (정책 자체 reversibility 영향 없음)

## Out-of-scope

- Phase 2 cross-host DAP 통합 — §결정 5 deferred
- LDP cold tier sanitize — Phase 2 dashboard CFP
- (ADR-029 §결정 2 본문 amendment commit = CFP-283 carrier 로 본 Phase 1 안에서 land 완료, Out-of-scope 제거)
- Telemetry hook 구현 (sqlite write) — ADR-042 §결정 12 deferred
- Token attribution model — ADR-042 §결정 3 spawn-event 보류 와 동반 deferred
- 외부 telemetry vendor 연동 (Datadog / Honeycomb / OpenTelemetry collector) — Phase 2 dashboard CFP

## 관련 ADR

- **ADR-029** (phase execution visibility) — **amends** 관계. §결정 2 sanitize policy 적용 범위 확장 (narration → narration + ledger unified SSOT) — CFP-283 carrier Amendment 1 (2026-05-09) land 완료. ADR-029 §결정 2 = format / scope SSOT, 본 ADR §결정 3 = Deny-list regex / Allow-list 18 field SSOT (v1.0 16 + Amendment 1 2 optional).
- **ADR-042** (measurement channel architecture) — **sibling Phase 1 PR**. ADR-042 §결정 5-6 verbatim cross-ref. architecture vs policy 분리.
- **ADR-039** (subagent default) — Phase 1 doc-only trust model 패턴 precedent. §결정 1 opt-in default false 정당화 근거.
- **ADR-025** (stop discipline) — stop-event-v1 deferred slot context.
- **ADR-013** (codeforge family dogfood-out policy) — wrapper dogfood always-on exception 정당화 (codeforge family 자체 development scope).
- **ADR-024** (Story-scoped branch policy) — 본 Story branch 명명.

## 해소 기준

N/A — permanent policy

## 관련 파일

- `docs/inter-plugin-contracts/stop-event-v1.md` (Allow-list 18 field + Deny-list regex 적용 — v1.1 Amendment 1 후)
- `docs/project-config-schema.md` (telemetry block — opt-in default false)
- `docs/consumer-guide.md` § "Telemetry opt-in"
- `docs/domain-knowledge/orchestrator-discipline/measurement-channel.md`
- `docs/adr/ADR-042-codeforge-measurement-channel-architecture.md` (sibling)
- `docs/adr/ADR-115-runtime-hook-enforcement-policy.md` (hook_source / hook_decision field origin — Amendment 1 carrier)
- `mclayer/codeforge-internal-docs:wrapper/stories/CFP-283.md`
- `mclayer/codeforge-internal-docs:wrapper/stories/CFP-1744.md`
- `mclayer/codeforge-internal-docs:wrapper/change-plans/cfp-283-adr-039-measurement-channel.md`

## Amendment 1 (CFP-1744, 2026-05-27) — Allow-list 16 → 18 field 확장

### 배경

CFP-1740 Epic Story-3 (#1743) 가 `hooks/stop` + `hooks/subagent-stop` 신설 시 ledger row 에 `hook_source` / `hook_decision` 두 field 를 실 기록 (scripts/lib/append_stop_event.py). 해당 field 가 ADR-043 §결정 2 Allow-list (16 field) 에 미포함 → schema SSOT 와 실 구현 gap 발생. Story-4 (#1744) carrier 로 Allow-list 정식 확장.

### Amendment 내용

**§결정 2 Allow-list 16 → 18 field 갱신**:
- `hook_source`: enum `{"stop", "subagent-stop"}` optional (non-sensitive) — emit 한 hook 종류. ADR-115 §결정 2 non-blocking 2종 분기 정합. 부재 시 `"stop"` 해석 (backward-compat default).
- `hook_decision`: enum `{"record-only"}` optional (non-sensitive) — non-blocking marker. ADR-115 §결정 2 block 금지 binding constraint. closed-set 1-value, 확장 시 별 CFP + 본 Amendment 갱신 의무.

### 근거

- **MINOR 영역 정합** (ADR-008 SemVer §결정 2): optional field 추가 = backward-compat. v1.0 reader 가 unknown field skip 가능 → BREAKING change 아님.
- **non-sensitive 분류 (ADR-043 §결정 3 Deny-list 미적용)**: `hook_source` = enum 2-value (stop/subagent-stop), `hook_decision` = enum 1-value (record-only) — PII / credential pattern 0건. Deny-list regex 6 pattern 중 어느 것도 매치 불가. Sanitize = non-sensitive 취급 (§결정 3 pass-through).
- **ADR-115 §결정 2 block 금지 binding constraint 정합**: `hook_decision: "record-only"` 는 non-blocking marker. block(continue):false 발화 금지 invariant 의 schema-level 명시.
- **ADR-064 §결정 7 evidence-gated symmetric ratchet 정합**: 강화 방향 (field 확장 = ratchet ↑). 근거 evidence = Story-3 (#1743) ledger row 실 작성 (hooks/stop + hooks/subagent-stop) = pattern_count 의 실 구현 carrier.

### 비-영향

- §결정 1 (opt-in default false) 무변경
- §결정 3 (Deny-list regex 6 pattern) 무변경 — `hook_source` / `hook_decision` non-sensitive 분류로 Deny-list 적용 0건
- §결정 4 (sanitize SSOT 통합) 무변경
- §결정 5 (wrapper-vs-consumer isolation) 무변경

## Amendment 2 (CFP-2393, 2026-06-24) — spawn-event-v1 telemetry channel 확정

### 배경

Epic CFP-2391 S3 (OMC-adopt per-agent replay/cost observability) 가 spawn-event-v1 ledger (per-agent token/cost attribution) 를 신설한다. 본 ADR §결정 1 이 이미 "future: spawn-event-v1 등 = opt-in default false" 로 named 한 channel 의 확정이다. 차용원 = oh-my-claudecode(MIT). 신규 contract = [`docs/inter-plugin-contracts/spawn-event-v1.md`](../../docs/inter-plugin-contracts/spawn-event-v1.md). ADR-042(measurement) Amendment 1 sibling. spawn-event 는 transcript_path 파싱이 token source 후보라 stop-event 가 마주한 적 없던 **new privacy surface** (transcript content / path) 를 마주한다 — 본 Amendment 가 그 hard invariant 를 codify.

### Amendment 내용

**(A) §결정 1 future → current** — spawn-event-v1 = 더 이상 "future" 가 아닌 **current opt-in channel**. consumer overlay `telemetry.channels.spawn_event: false` default. global `telemetry.enabled: false` 시 disabled (global gate inherit). wrapper dogfood 도 Phase 1 = default false + 사용자 explicit opt-in 의무 (consumer 와 동일 trust model).

**(B) §결정 2 Allow-list 에 spawn-event-v1 field set 추가** — spawn-event-v1 은 stop-event-v1 (18 field) 와 **별 channel 별 Allow-list** 를 가진다. spawn-event-v1 Allow-list 19 field (SSOT = spawn-event-v1.md §2):
```
event_id / schema_version / timestamp / story_key / lane_label / agent_type /
attribution_confidence / input_tokens / output_tokens / cache_creation_input_tokens /
cache_read_input_tokens / cost_usd / duration_ms / tool_call_count / actor /
parent_event_id / consumer_scope / event_type / elapsed_seconds
```
**전부 enum / numeric / hash — free-form string field 0건** (T-INFO-8 SecurityArch — Deny-list 가 no-op 이 되도록 구조적 차단). field 추가 = 본 §결정 2 Amendment 의무 (Allow-list ONLY enforcement).

**(C) §결정 3 / §결정 4 / §결정 5 inherit 선언** — spawn-event-v1 은:
- §결정 3 Deny-list regex 6 pattern = **inherit 선언** (defense in depth). 현 v1.0 = free-form string 0건이라 적용 0건이나, 향후 string field 도입 시 자동 적용 대상 (silent bypass 금지).
- §결정 4 sanitize SSOT 통합 (ADR-029 §결정 2 unified narration+ledger scope) = future ledger 자동 inherit (§결정 4 명문) — spawn-event 적용.
- §결정 5 wrapper-vs-consumer isolation = inherit. storage_path override 가 wrapper dir 로 escape 금지 (InfraOpArch §7.4.5). cross-host DAP 통합 = Phase 2 deferred.

**(D) T-INFO-5 transcript content/path HARD invariant (NEW privacy decision)** — spawn-event-v1 의 token source 후보 = transcript_path 파싱 (SubagentStop payload 직접엔 token 부재). 이로 인해 **transcript content + transcript_path 가 new leak surface**. HARD invariant:
- spawn-event row 는 **numeric aggregate + enum + hash 만** 저장. **transcript content 절대 미저장. transcript_path 값 절대 미저장** (path = session-id 포함).
- 구조적 mitigation = derivation fn 이 numeric only 반환 (content/path 가 row 에 도달하는 경로 자체 부재).
- stop-event 는 이 surface 를 마주한 적 없음 (subagent-stop 이 transcript 미read) — spawn-event net-new P0. 본 §결정 = SecurityArch T-INFO-5 P0 대응.

**(E) T-INFO-7 sha256 identity (spawn-event 한정)** — `actor` (top-level session ID) + `parent_event_id` (nested spawn chain) = **sha256 hash, raw 금지**. spawn-event-v1 은 stop-event-v1 contract (sha256 actor) 모델을 따르고 **stop-event runtime (append_stop_event.py line 73 raw session_id) 패턴을 복사하지 않는다**.
- **명시 경계**: 본 Amendment 는 **stop-event runtime 의 raw session_id bug 수정을 위임하지 않는다** — 그것은 별 follow-up (3문 게이트 통과 시 발의). 본 Amendment 는 spawn-event 가 sha256 을 쓴다는 것만 mandate.

### 근거

- **§결정 1 자체가 spawn-event-v1 을 named** — "future: spawn-event-v1 등". 본 Amendment 는 named future channel 의 확정이지 신개념 도입 아님. 신규 ADR 미신설 (privacy SSOT 단일화 — 대안 A reject 정합).
- **MINOR 영역 정합** (ADR-008 SemVer §결정 2): channel 별 Allow-list field set 추가 (additive) + inherit 선언 + privacy invariant 강화(ratchet ↑) = backward-compat. BREAKING 아님.
- **privacy = cross-cutting concern** (본 ADR 컨텍스트) — spawn-event 가 동일 정책 inherit 가능하도록 ADR-042 와 분리한 설계 의도의 실현 첫 사례.
- **T-INFO-5 net-new surface 의 정직 codify** — transcript parse 가 unbounded I/O + content leak 양쪽 위험 (InfraOpArch H2 + SecurityArch T-INFO-5). content/path 미저장은 schema-level hard invariant 로 박제 (구조적 차단).

### 비-영향

- §결정 2 stop-event-v1 18 field Allow-list 무변경 (spawn-event 는 별 channel Allow-list).
- §결정 3 Deny-list regex 6 pattern 자체 무변경 (spawn-event 는 free-form 0건 → 적용 0건, inherit 선언만).
- §결정 4 sanitize SSOT 통합 무변경 (자동 inherit scope 확장만).
- §결정 5 isolation 정책 무변경 (적용 확장만).
- ADR-043 Amendment 1 (hook_source / hook_decision) 무변경.
- stop-event-v1 runtime raw session_id bug = 본 Amendment 미위임 (별 follow-up).

## Amendment 3 (CFP-2572, 2026-07-05) — self-context proxy record type (ADR-142 §결정 4 carrier)

### 배경

ADR-142 (Orchestrator-self READ/synthesis/verbose-return context 규율) §결정 4 = 장기 세션 Orchestrator self-context 누적을 **record-only proxy telemetry** 로 남긴다. platform 이 live per-turn self-context surface 를 미제공(P1)하므로 **live budget gate 가 아닌** coarse proxy (`compact_boundary.preTokens` + delegation-ratio) 만 가능하다. substrate = 기존 SubagentStop-wired spawn-event-v1 채널 재사용(신규 hook 블록 0). 본 Amendment 가 그 proxy field set 의 §결정 2 allow-list 편입을 codify.

### Amendment 내용

**(A) §결정 2 Allow-list 에 self-context proxy record type 추가** — spawn-event-v1 channel 내 lead-self aggregate record. field 6종 (numeric/enum/hash only):
```
schema_version(const "self-context-v1") / session_id(sha256) / turn_index(int, monotonic) /
delegation_ratio(float 0.0–1.0, coarse-round, proxy) / pre_tokens(int, bucketed, compact_boundary.preTokens 출처) /
cause_category(CLOSED enum: read-heavy|synthesis-inline|fix-diagnosis|spawn-dispatch|skill-load|env0-mediation|other)
```
**FORBIDDEN**: file path / transcript 발췌 / tool_input body / free-form reason string (T-INFO-8 구조적 차단). `cause_category` enum 값은 consumer file-path / BC 명 / prompt text 에서 파생 금지 = **domain-agnostic** 고정 closed-set (SecurityArch 확정).

**(B) inherit 선언** — §결정 1 opt-in default-false 상속(always-on 금지) + §결정 3 Deny-list inherit + T-INFO-5 transcript content/path 미저장 상속(pre_tokens 은 compact_boundary 정수만, transcript raw 미도달) + T-INFO-7 sha256 identity(session_id). `hook_decision=record-only`(Amendment 1 §결정 2 non-blocking) — telemetry 실패가 작업 halt 금지, dropped event 는 stderr/dropped-count trace(silent-success-on-error 금지). idempotency key = turn-id/compact_boundary event-id + read-side dedup(누적 proxy replay 팽창 차단).

**(C) hollow-gate 1순위 verbatim (ADR-119)** — delegation_ratio / pre_tokens = **proxy 이지 lead-self ground-truth 아님**(platform surface 부재). 어떤 self-context 판정도 게이트가 아니다. record-only.

### 근거

- **§결정 1 이 이미 "future: spawn-event-v1 등" named** — 본 Amendment 는 그 channel 의 lead-self variant 추가이지 신규 privacy SSOT 신설 아님(대안 A reject 정합, 신규 ADR 미신설).
- **MINOR 정합** (ADR-008 §결정 2): additive record type + inherit + privacy 강화(ratchet ↑) = backward-compat.
- **정확한 field-set 통합/count reconciliation = Phase 2** spawn-event-v1 contract bump 시 확정 (본 Amendment = allow-list POLICY 결정, 실 emission = Phase 2).

### 비-영향

- §결정 2 stop-event-v1 18 field + spawn-event-v1 19 field Allow-list 무변경 (self-context = 별 record type, allow-list 확장만).
- §결정 3/4/5 정책 무변경 (inherit scope 확장만).
- ADR-043 Amendment 1/2 무변경.
- L7 은 record-only proxy — 게이트/블록/deny 언어 적용 0건 (ADR-142 tier 정직 invariant).

## Amendment 4 (CFP-2687, 2026-07-15) — dev-process-event-v1 telemetry privacy (always-on 비대칭 + blob deny-pattern + redacted-blob T-INFO-5)

### 배경

Epic #2686 Story A (CFP-2687) 가 `dev-process-event-v1`(신규 ADR-155 sibling) telemetry channel 을 신설한다. stop-event(numeric/enum/hash) · spawn-event(numeric aggregate) 는 rich content 를 마주한 적 없으나 dev-process-event 는 **프롬프트/diff/tool-call/findings/최종산출물 rich content** 를 evidence-blob-store 에 저장한다 = **net-new leak surface**(blob store). 본 Amendment 는 그 privacy 규약을 §결정 1/2/3 + Amd2 §D 에 attach 해 codify. 실 redaction fn/blob store = Phase 2(본 Story §8-§11), 본 Amendment = 정책 결정.

### Amendment 내용

**(A) §결정 1 always-on 비대칭 codify** — dev-process-event 는 §결정 1 opt-in default-false 를 **비대칭**으로 확정:
- **wrapper-self dogfood scope = always-on** — codeforge family 자기 개발 계측이 Story 목적. always-on = **checkout-identity 파생**(consumer overlay 의 user-settable bool 아님). ADR-042 §결정 6 "wrapper dogfood always-on = Phase 2 follow-up" 를 CFP-2687 이 carrier.
- **consumer 배포 scope = opt-in default-false 무약화** — ADR-064 §결정 7 extend-only. `telemetry.channels.dev_process_event: false` default. global `telemetry.enabled: false` 시 disabled(global gate inherit). **T-DPE-9**: consumer floor 하방 override 불가(always-on 이 consumer 로 전파 금지).
- **INV-8 redaction-precedes-always-on(비협상 floor)**: always-on 이더라도 capture-time redaction 이 항상 선행 — always-on 이 redaction 을 **우회하지 못한다**.
- **always-on 4중 bound**: (1) wrapper-self 한정(consumer opt-in-false) (2) capture ≠ exfiltration — blob host-local + 0-API + cross-host leak 금지 = **host 절대 미이탈**(VS Code/GitHub CLI telemetry 논쟁 본질 = 전송; host-local 미전송은 다른 위험 프로파일) (3) redaction-precedes-always-on floor (4) transparency notice 권고(기여자 대상 NOTICE).

**(B) §결정 2 dev-process-event index tier 별도 channel allow-list** — dev-process-event 는 stop-event(18)·spawn-event(19)·self-context(6)와 **별 channel allow-list**(SSOT = dev-process-event-v1.md §2, Phase 2). index tier = **enum / numeric / hash / 상관 ID(story/lane/defect/fix) / blob-ref / `emit_source`(enum {hook,agent}) only** — free-form content 본문 **0건**(T-INFO-8 구조적 차단, Deny-list no-op 되도록). rich content 는 evidence-blob-store 표면(redacted blob)으로만 도달. field 추가 = 본 §결정 2 Amendment 의무.

**(C) §결정 3 Deny-list regex 6 → 7종 (경로 pattern 신규)** — dev-process rich content 는 로컬 파일 경로를 자주 포함(diff/tool-call) → 신규 7번째 pattern + 헤더/cloud-key 보강:

| Pattern | 대상 | 비고 |
|---|---|---|
| (기존 6종) | API key/credential · GitHub PAT · fine-grained PAT · 주민번호 · Email · Hex≥32 | ADR-043 §결정 3 상속 |
| **절대/home-prefixed 경로 (신규 7번째)** | `/home` · `/Users` · `/root` · Windows `C:\` · git-bash `/c/` prefix 경로만 redact | **repo-relative 경로는 보존**(diff 진단 신호 = public; 무차별 redact 시 §5.4 noise false-negative — 실패 원인 소실) |
| Authorization / Cookie 헤더 | tool-call HTTP 헤더 dump | dev-process net-new |
| cloud-key (gitleaks 차용) | AWS/GCP/Azure key pattern + entropy 임계 보강 | `source: github.com/gitleaks/gitleaks` |

- **env dump · 자격증명 subprocess 출력 = capture 제외**(기본, blob 미도달).
- **per-event-type redaction tier(SecurityArch D-2)**: prompt = 최고 tier(최고 compliance 위험) / diff·tool-call = 표준 / verdict·findings = 대체로 enum blob 불요(dissent 반영 — 계약 §redaction 서술).

**(D) Amendment 2 §D 확장 — redacted-blob tier T-INFO-5 no-conflict 신규 표면** — 기존 Amd2 §D(spawn-event transcript content/path HARD invariant)와 no-conflict 인 **redacted-blob 표면** codify:
- **INV-8a (hash-over-redacted, P0)**: redact(in-memory, 원본 disk 미접촉) → `blob_ref = sha256(REDACTED bytes)` **NEVER raw** → blob write(redacted). **T-DPE-2 hash-oracle(P0)**: hash-over-unredacted 는 index content-free 여도 `blob_ref` 가 secret confirmation oracle → hash-over-redacted 가 봉인.
- **INV-8b (blob-before-index, P0)**: blob write → THEN index row(blob_ref). 역순 = dangling evidence chain.
- **audit enum(AC-14)**: `redaction_applied`(bool) / `redaction_count`(int) / `redaction_rules_fired`(closed enum array). **T-DPE-8(P1)**: audit 에 매칭 secret **원문/hash 절대 미기록**(규칙명+횟수만 — audit 이 oracle 로 역전 방지). mandatory-on-fire.
- **session_id = sha256만**(raw 금지 — append_stop_event.py:73 runtime raw session_id bug 미복사, spawn-event T-INFO-7 sha256 선례 답습).
- **no-conflict 논증**: 기존 T-INFO-5(index content/path 미저장) 무손상 — index 는 여전히 content-free(blob-ref hash only), blob 은 redaction-후 산물. 2계층 분리로 anti-content invariant 와 rich-capture 화해(ADR-155 §결정 1).
- **resource-safety honest-ceiling(★self-ref 8연속 방지 — CFP-2635/2646 재발)**: 계약 redaction 섹션에 "ReDoS-safe / DoS-guard / catastrophic-backtracking 0" **무증거 단정 금지**(리뷰 반증). born-safe bound(byte-cap + line-cap + parse-timeout)만 명시, "bounded degradation, 임의입력 무해 아님" 정직 천장. proof = Phase 2 SecurityTest execution-backed.

### 근거

- **§결정 1 이 이미 "future ledger 자동 inherit" 명문** — dev-process-event 는 그 named-future channel 의 확정(신규 privacy SSOT 신설 아님 — 대안 A reject 정합, 신규 privacy ADR 미신설. architectural SSOT = ADR-155, privacy 는 본 ADR-043 확장).
- **MINOR 정합**(ADR-008 SemVer): additive channel allow-list + deny-regex 확장(6→7) + privacy invariant 강화(ratchet ↑) = backward-compat.
- **net-new blob surface 의 정직 codify** — rich-content blob 은 stop/spawn 이 마주한 적 없는 leak surface. redaction-선행 + hash-over-redacted + blob-before-index 를 schema-level hard invariant 로 박제(ADR-119 정직 천장 — 무증거 안전 단정 금지).

### 비-영향

- §결정 1 opt-in default-false 기본 정책 무변경 — dev-process 는 **비대칭 확정**(wrapper always-on 추가, consumer default-false 무약화).
- §결정 2 stop-event 18 / spawn-event 19 / self-context 6 field allow-list 무변경 (dev-process = 별 channel allow-list).
- §결정 3 기존 6 deny-regex pattern 무변경 (7번째 경로 pattern additive).
- §결정 4/5 (sanitize SSOT / isolation) inherit — dev-process 자동 적용, 정책 자체 무변경.
- Amendment 1/2/3 무변경. stop-event-v1 runtime raw session_id bug = 본 Amendment 미위임(별 follow-up).
