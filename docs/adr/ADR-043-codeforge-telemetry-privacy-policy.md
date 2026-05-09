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
related_stories:
  - CFP-283
related_cfps:
  - CFP-283
related_files:
  - docs/inter-plugin-contracts/stop-event-v1.md
  - docs/project-config-schema.md
  - docs/consumer-guide.md
  - docs/domain-knowledge/orchestrator-discipline/measurement-channel.md
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
- **wrapper dogfood exception**: codeforge family 자체 development 만 always-on 허용 — explicit env flag (`CODEFORGE_DOGFOOD_TELEMETRY=1`) 의무. consumer 측 silent always-on 금지.

위반 시 (default false 인데 ledger write 발생) = `policy_violation` (defect). lint = TestContractArch §8.4 후보 5 (opt-in default false invariant — ADR-042 §검증 채널 cross-ref).

근거:
- consumer 측 silent telemetry = trust 위반 (GitHub CLI opt-out 비판 precedent)
- ADR-039 Phase 1 doc-only trust model 패턴 정합
- 사용자 명시 directive 없는 한 measurement opt-in = 사용자 자율

### 결정 2 — Allow-list ONLY 16 field whitelist (capture 시점)

**Capture 시점 sanitize = Allow-list ONLY**. stop-event-v1 schema 16 field (ADR-042 §결정 2 enumerated) 외 field capture 금지:

```
event_id / schema_version / timestamp / story_key / phase_label / lane_label /
reason_class / reason_class_subclass / actor / iter / decider_pick /
override_marker / recovery_action / outcome / consumer_scope / parent_event_id
```

추가 field capture = BREAKING change → ADR-042 amendment 의무 + 본 ADR-043 §결정 2 갱신 의무 (cross-ref).

근거:
- Allow-list = future expansion 시 explicit ADR review 강제 (silent expansion 차단)
- Deny-list 단독 = unknown unknown 위험 (새 PII pattern 미식별 시 leak)
- Allow-list + Deny-list 2-layer (defense in depth) = §결정 3

### 결정 3 — Deny-list regex (capture 통과 후 2차 안전망 — defense in depth)

Allow-list 16 field 중 `reason_class_subclass` (free-form string) / `actor` (session ID hash) / `recovery_action` 등 string field 의 capture 시점 redact regex:

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

ADR-029 §결정 2 (phase narration sanitize policy) = **본 ADR-043 §결정 3 으로 SSOT 통합**. ADR-029 frontmatter `superseded_by_partial: ADR-043` 마킹 권장 (cross-ref invariant — 양쪽 SSOT 변경 시 sync 의무).

근거:
- privacy = cross-cutting concern (narration + ledger 동일 정책)
- single source of truth (ADR-043) = update / audit 비용 ↓
- ADR-029 narration scope 한정 SSOT 가 ledger 신설 시 분기 — 분기 회피

ADR-029 §결정 2 본문 = 본 ADR amends 후 1줄 cross-ref 잔존 (`Sanitize policy SSOT = ADR-043 §결정 3` link).

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

채택 = §결정 1 default false + wrapper dogfood explicit env flag.

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
2. **Allow-list ONLY enforcement lint** — stop-event-v1 schema 16 field 외 추가 시 lint FAIL (BREAKING change → ADR-042 + ADR-043 amendment 의무).
3. **Deny-list regex coverage lint** — 6 redact pattern 정합 검증.
4. **ADR-029 §결정 2 cross-ref invariant** — ADR-029 → ADR-043 §결정 3 cross-ref link 존재.
5. **wrapper-vs-consumer isolation lint** — ledger storage path 분리 (wrapper `mclayer/plugin-codeforge` vs consumer repo).

후보 1 + 후보 2 = Phase 1 PR scope. 후보 3-5 = follow-up CFP.

## 결과

### 영향 file (wrapper repo)

- `docs/adr/ADR-043-codeforge-telemetry-privacy-policy.md` (본 file)
- `docs/inter-plugin-contracts/stop-event-v1.md` (Allow-list ONLY 16 field 적용 + Deny-list regex 명시)
- `docs/project-config-schema.md` (telemetry block — opt-in default false)
- `docs/consumer-guide.md` § "Telemetry opt-in" (default false 명시)
- `docs/domain-knowledge/orchestrator-discipline/measurement-channel.md` (privacy 정책 cross-ref)
- `docs/adr/ADR-029-phase-execution-visibility-expansion.md` (§결정 2 sanitize policy SSOT 통합 cross-ref — Phase 2 follow-up CFP, 본 Phase 1 scope 외 — see Phase 2 follow-up)

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
- ADR-029 §결정 2 본문 SSOT 통합 commit — Phase 2 follow-up CFP (본 Phase 1 = ADR-043 신설 only, ADR-029 amend commit 은 별도 lite scope follow-up)
- Telemetry hook 구현 (sqlite write) — ADR-042 §결정 12 deferred
- Token attribution model — ADR-042 §결정 3 spawn-event 보류 와 동반 deferred
- 외부 telemetry vendor 연동 (Datadog / Honeycomb / OpenTelemetry collector) — Phase 2 dashboard CFP

## 관련 ADR

- **ADR-029** (phase execution visibility) — **amends** 관계. §결정 2 sanitize policy 가 본 ADR §결정 3 으로 SSOT 통합 (Phase 2 follow-up CFP commit).
- **ADR-042** (measurement channel architecture) — **sibling Phase 1 PR**. ADR-042 §결정 5-6 verbatim cross-ref. architecture vs policy 분리.
- **ADR-039** (subagent default) — Phase 1 doc-only trust model 패턴 precedent. §결정 1 opt-in default false 정당화 근거.
- **ADR-025** (stop discipline) — stop-event-v1 deferred slot context.
- **ADR-013** (codeforge family dogfood-out policy) — wrapper dogfood always-on exception 정당화 (codeforge family 자체 development scope).
- **ADR-024** (Story-scoped branch policy) — 본 Story branch 명명.

## 관련 파일

- `docs/inter-plugin-contracts/stop-event-v1.md` (Allow-list 16 field + Deny-list regex 적용)
- `docs/project-config-schema.md` (telemetry block — opt-in default false)
- `docs/consumer-guide.md` § "Telemetry opt-in"
- `docs/domain-knowledge/orchestrator-discipline/measurement-channel.md`
- `docs/adr/ADR-042-codeforge-measurement-channel-architecture.md` (sibling)
- `mclayer/codeforge-internal-docs:wrapper/stories/CFP-283.md`
- `mclayer/codeforge-internal-docs:wrapper/change-plans/cfp-283-adr-039-measurement-channel.md`
