---
adr_number: 42
title: Codeforge measurement channel architecture
date: 2026-05-09
status: Accepted
category: orchestration-discipline
carrier_story: CFP-283
supersedes: null
amends: ADR-025  # §결정 10 deferred slot 채움 (stop-event-v1)
related_adrs:
  - ADR-025  # stop discipline + Epic-level continuity (§결정 10 deferred slot 채움)
  - ADR-026  # post-merge automation (post-merge-counters.jsonl 30+ run ROI gate)
  - ADR-029  # phase execution visibility (narration vs ledger boundary)
  - ADR-031  # lane-spawn evidence (§14 lane coarse vs spawn-event sub-step boundary)
  - ADR-038  # progress visualization TodoWrite (boundary 차단 — 측정 대상 아님)
  - ADR-039  # subagent default (§결정 9 deferred Phase 2 measurement)
  - ADR-043  # telemetry privacy policy (sibling — privacy concern 분리)
related_stories:
  - CFP-283
related_cfps:
  - CFP-283
  - CFP-275  # ADR-039 carrier — Phase 2 deferred follow-up
  - CFP-73   # stop discipline carrier (precedent — stop-event-v1 deferred slot)
related_files:
  - docs/inter-plugin-contracts/stop-event-v1.md
  - docs/inter-plugin-contracts/MANIFEST.yaml
  - docs/orchestrator-playbook.md  # §15 4-channel boundary table
  - docs/project-config-schema.md  # telemetry block schema
  - docs/consumer-guide.md  # §7.0.7 telemetry_enabled flag 안내
  - docs/domain-knowledge/orchestrator-discipline/measurement-channel.md
  - docs/change-plans/cfp-283-adr-039-measurement-channel.md  # internal-docs SSOT (ADR-013)
  - docs/inter-plugin-contracts/spawn-event-v1.md  # Amendment 1 (CFP-2393) — spawn-event-v1 신설 carrier
is_transitional: false
amendment_log:
  - amendment: 1
    date: 2026-06-24
    carrier_story: CFP-2393
    summary: "§결정 3 spawn-event-v1 보류 해제 (supersede) + §결정 1 4-channel boundary 표 8번째 channel (spawn-event-v1) 추가 + Out-of-scope token attribution deferral 해제 + §결정 13 amendment 의무 이행 (§14↔spawn-event dedup script Phase 2 commitment). Epic CFP-2391 S3 directive 가 §결정 3 보류근거 #3 (30+ run ROI gate) 를 supersede — OMC-adopt per-agent replay/cost observability. Phase 1 = doc-only (stop-event 선례 §결정 12). 신규 ADR 미신설 (§결정 1 self-amendment 의무 + §결정 13 'Amendment N 신설' 명시 정합)."
  - amendment: 2
    date: 2026-07-15
    carrier_story: CFP-2687
    summary: "dev-process-event-v1 = 9번째 Tier-3 persistent channel 확정 (Epic #2686 Story A, 신규 ADR-155 sibling). (A) §결정 1 8→9 channel boundary 표 dev-process-event-v1 row 추가 + playbook §15.1 8→9 row Phase 2 co-land(계약 파일과 동반, dangling 회피) + §15.2 5th boundary invariant(dev-process = semantic-evidence-aggregation, 상관ID JOIN 허용 / accounting payload re-record 금지 — SoT 이중화 차단). (B) warm-tier 추가 — §결정 4 hot+cold 2-tier 를 dev-process-channel-scoped 3-tier(hot→warm→cold strict)로 확장 (stop-event 자체 무변경, dev-process channel 한정). (C) §결정 11 ROI-gate supersede 명문화 — Epic #2686 directive 가 30+ run ROI evidence deferral 을 supersede. 30+ run ROI evidence 미확보(firsthand 미검증) 정직 명기, silent-skip 금지 (Amd1 CFP-2393 byte-동형 template [verified: ADR-042:455]). Phase 1 = doc-only (신규 ADR-155 설계 SSOT + 본 amendment). MINOR (additive channel row + tier 확장 + directive supersede 명문화, ADR-008 SemVer)."
---

# ADR-042: Codeforge measurement channel architecture

## 상태

**Accepted (2026-05-09)** — carrier_story = CFP-283. Phase 1 wrapper-only doc + schema land + opt-in default false. Phase 2 enforcement (rule-based hook / stop-event auto-fire / inline write detect) = deferred follow-up CFP, ROI gating after 30+ post-merge-counters.jsonl run (ADR-026 §결정 3 패턴 정합).

본 ADR 의 implementation plan SSOT = [`wrapper/change-plans/cfp-283-adr-039-measurement-channel.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/change-plans/cfp-283-adr-039-measurement-channel.md) (internal-docs SSOT, ADR-013 dogfood-out). 본 ADR = 정책 결정 SSOT.

## 컨텍스트

### 사용자 발의 + ADR-039 §결정 9 inheritance

CFP-275 ADR-039 §결정 9 명시: Phase 2 enforcement / measurement = deferred follow-up CFP. 4 deferred items:

1. **stop-event-v1 ledger** (ADR-025 §결정 10 deferred slot)
2. **Orchestrator inline write detect hook** (PreToolUse on Write / Edit / mcp__github__*)
3. **spawn cost telemetry** (token / latency 정량 측정)
4. **rate-limited cascade detection** (`policy_violation_rate_limit_induced` second-order risk)

CFP-283 = ADR-039 §결정 9 의 4 deferred items 중 **measurement channel slot only** 처리 (enforcement hook = Phase 2 후속 CFP). measurement-vs-fix scope boundary = OperationalRiskArchitect substantive constraint (§7.4 / §결정 12).

### 4-channel observability stack (CodebaseMapperAgent 분석)

기존 codeforge observability stack 3-tier:

- **Tier 1 ephemeral**: stderr narration (ADR-029) / TodoWrite (ADR-038) / `.claude-work/progress/<KEY>.md` cache (CFP-20)
- **Tier 2 committed lane-coarse**: Story §14 Lane Evidence (ADR-031) / Story §10 FIX Ledger (CFP-32 fix-event-v1)
- **Tier 3 persistent measurement**: post-merge-counters.jsonl (ADR-026 lite scope) / **stop-event-v1 deferred slot** (현재 미정) / **spawn-event-v1 부재** (현재 미정)

본 ADR = **Tier 3 persistent measurement 의 architectural codification** + stop-event-v1 schema slot 채움 + spawn-event-v1 신설 보류 결정 (§결정 10).

### Gap

1. **Measurement channel 부재** — ADR-039 effective enforcement 검증을 위한 quantitative ledger 가 부재. Phase 1 doc-only trust model 의 ROI 평가 불가능.
2. **stop-event-v1 schema 미확정** — ADR-025 §결정 10 deferred slot 가 현재 placeholder. CFP-73 Phase 2 deferral 이후 ~6 month gap.
3. **§14 ↔ spawn-event boundary 미정의** — §14 Lane Evidence (lane coarse) 와 spawn-event (sub-step granular) 가 신설 시 dual-write race + double-count 위험 (Refactor B1 HIGH).
4. **Privacy / opt-in 정책 부재** — consumer 측 silent telemetry = trust 위반 (GitHub CLI opt-out 비판 사례, Researcher §6.5). default-off 정책 codification 의무.
5. **0 API call constraint 미정의** — measurement channel 자체가 measure 대상 (ADR-039 enforcement) 을 amplify (token burn / rate-limit cascade) 시 second-order risk → measurement-vs-fix scope boundary 위반 (OperationalRiskArchitect §7.4 substantive).

## 결정 (13)

### 결정 1 — 4-channel observability boundary 정의 (kind:registry SSOT @ playbook §15)

본 ADR = **4-channel boundary 표** 를 wrapper [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) §15 (현재 Reserved) 에 normative SSOT 로 land. 4 channel 분리:

| Channel | Tier | Granularity | Storage | Owner | Lifecycle |
|---|---|---|---|---|---|
| **stderr narration** (ADR-029) | 1 ephemeral | sub-step | scrollback | Orchestrator | session-only |
| **TodoWrite scratchpad** (ADR-038) | 1 ephemeral | meta-cognitive | tool surface | Orchestrator | turn-only |
| **`.claude-work/progress/<KEY>.md` cache** (CFP-20) | 1 ephemeral | per-Story coarse | fs cache | Orchestrator | Story-only (post-merge mv `_archive/`) |
| **Story §10 FIX Ledger** (CFP-32 / fix-event-v1) | 2 committed | discrete FIX event | git commit | Orchestrator monopoly | persistent (append-only) |
| **Story §14 Lane Evidence** (ADR-031) | 2 committed | lane spawn coarse | git commit | Orchestrator monopoly | persistent (append-only) |
| **post-merge-counters.jsonl** (ADR-026) | 3 persistent | post-merge action outcome | git commit | post-merge-followup.yml | persistent (append-only, opt-in) |
| **stop-event-v1 ledger** (본 ADR §결정 2) | 3 persistent | discrete stop event | hot tier (sqlite/JSONL) + cold tier (markdown) | Orchestrator-owned delegate subagent | hot 7-30d / cold persistent / opt-in default false |

**Boundary 차단 invariant**:
- **TodoWrite ↔ stop-event-v1**: TodoWrite 호출은 stop-event-v1 ledger record 대상 아님 (ADR-038 standalone 정당화 — meta-cognitive scratchpad, file system / GitHub state mutation 미발화). boundary 차단.
- **§14 ↔ spawn-event-v1**: spawn-event-v1 신설 보류 (§결정 10) — 본 boundary race 회피.
- **§10 ↔ stop-event-v1**: stop-event-v1 의 `reason_class: policy_violation` row 가 §10 FIX Ledger row append 의 proxy. dedup 책임 = aggregate script (Phase 2).

5번째 measurement channel 추가 = ADR-042 amendment 의무. 본 closed enumeration 가 future "X tool 호출도 ledger record" 류 압박을 차단.

### 결정 2 — stop-event-v1 신규 contract 신설 (kind:registry, ADR-025 §결정 10 deferred slot 채움)

`docs/inter-plugin-contracts/stop-event-v1.md` 신규 file (kind:registry — kind:contract 회피, sibling sync overhead 0건). schema:

- **lifecycle**: initiate → classify → append → aggregate
- **reason_class enum** (4 종 confirmed): `user_stop_legitimate` / `decider_escalation_required` / `policy_violation` / `policy_violation_rate_limit_induced` (ADR-039 §결정 9 second-order risk cascade — DomainAgent §2.4 4번째 후보 채택)
- **schema field** (16 field, Allow-list ONLY — ADR-043 §결정 2 정합):
  - `event_id` (sha256(packet_id || actor || event_type || timestamp_iso8601), idempotency invariant)
  - `schema_version` (`stop-event-v1`)
  - `timestamp` (ISO8601 UTC monotonic)
  - `story_key` (e.g. `CFP-283`)
  - `phase_label` (e.g. `phase:설계`)
  - `lane_label` (enum: 요구사항 / 설계 / 설계-리뷰 / 구현 / 구현-리뷰 / 구현-테스트 / 보안-테스트 / 없음)
  - `reason_class` (enum 4 종, 위)
  - `reason_class_subclass` (free-form string, e.g. `policy_violation_subdecision`)
  - `actor` (top-level Claude session ID hash, no raw)
  - `iter` (FIX iteration counter mirror, optional)
  - `decider_pick` (enum: PASS / FIX / N/A)
  - `override_marker` (bool, optional)
  - `recovery_action` (enum: retry / escalate / abort)
  - `outcome` (enum: success / failure / partial)
  - `consumer_scope` (enum: wrapper / consumer)
  - `parent_event_id` (sha256 reference, attribution chain — Researcher §6.3 nested spawn dedup)

**Allow-list ONLY enforcement**: 16 field 외 capture 금지 (ADR-043 §결정 2 verbatim). Schema lint (TestContractArch §8.4 후보 1) 가 검증.

### 결정 3 — spawn-event-v1 신설 보류 (Refactor B1 HIGH partial 채택)

spawn-event-v1 신규 contract = **본 Story scope 제외**. 별도 후속 CFP (현재 미할당) 처리. 보류 근거 3:

1. **§14 ↔ spawn-event-v1 dual-write race** (CodebaseMapperAgent 분석 + Refactor B1 HIGH) — 두 channel 동시 write 시 boundary 모호. aggregate script 가 §14 row count 와 spawn-event lane=spawn type count 정합 검증 필요 (overhead).
2. **Aggregate script 로 충분** (Refactor 권고) — spawn count metric 은 §14 Lane Evidence row count + post-merge-counters.jsonl 의 lane spawn outcome 으로 도출 가능. raw spawn-event ledger 신설 = ROI 미확정.
3. **30+ post-merge-counters.jsonl run ROI 평가 후 결정** (ADR-026 §결정 3 패턴 정합) — 현재 ROI 미충분.

본 §결정 = Mapper §14 schema 무변경 invariant + Refactor scope minimization 적극 변호 + DataMigrationArch §11.5 retroactive 미적용 패턴 정합.

### 결정 4 — Hot tier default = sqlite (DataMigrationArch substantive 권고)

stop-event-v1 hot tier (raw 7-30d) 저장소 default = **sqlite**. JSONL 채택 안 함. 근거 (DataMigrationArch substantive 적극 권고):

- **WAL mode** = atomic transaction + concurrent read 안전 (multi-Story 동시 진행 가정).
- **append-only invariant** = sqlite trigger 로 enforcement 가능 (`BEFORE UPDATE`/`BEFORE DELETE` → ROLLBACK).
- **idempotency** = `UNIQUE INDEX (event_id)` 로 hardware-level enforcement (§결정 2 event_id sha256 + §11.6).
- **schema migration** = sqlite ALTER TABLE expand-contract 패턴 가능 (DataMigration §11.2).
- **JSONL 회피 사유** = grep 가능성만 ↑, append race / corruption recovery / idempotency 모두 application-level 책임 → 운영 risk ↑.

cold tier (persistent) = `docs/stories/<KEY>.md §10` FIX Ledger row append (기존 fix-event-v1 contract 재사용 — `reason_class: policy_violation` row 가 stop-event-v1 cold tier proxy). 별도 cold tier file 신설 안 함 (Phase 1 scope 축소).

Storage path: `.claude-work/measurement/stop-event.sqlite` (consumer overlay `telemetry.storage_path` 로 override 가능).

### 결정 5 — Allow-list ONLY 16 field whitelist + Deny-list regex (SecurityArch P0 위협 대응)

Sanitize policy = **Allow-list ONLY**. 16 field (§결정 2 enumerated) 외 capture 금지. 추가 보강:

- **Deny-list regex** (Allow-list 통과 후 2차 안전망 — defense in depth):
  - API key / credential pattern (`(api[_-]?key|secret|token|password|bearer)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}`)
  - 한국 주민번호 (`\d{6}[-\s]?\d{7}`)
  - email (`[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}`)
  - hex≥32 (`[a-f0-9]{32,}`)
  - GitHub PAT (`ghp_[A-Za-z0-9]{36}` / `github_pat_[A-Za-z0-9_]{82}`)
- **Match → redact** (`[REDACTED:<rule>]` placeholder), **NOT block** — capture 자체는 진행, 정합성 보장.

본 §결정 = SecurityArch P0 위협 3종 (T-INFO-1 / T-INFO-4 / T-ELEV-1) 대응 + ADR-043 §결정 2-4 cross-ref. ADR-029 §결정 2 sanitize policy 적용 범위 확장 (narration → ledger).

### 결정 6 — Opt-in default false invariant (ADR-043 §결정 1 cross-ref)

`telemetry.enabled` global flag default = **false**. 근거:

- consumer 측 silent telemetry = trust 위반 (GitHub CLI opt-out 비판 precedent — Researcher §6.5).
- ADR-039 Phase 1 doc-only trust model 패턴 정합 (Phase 1 trust = enforcement hook 부재).
- Wrapper dogfood (codeforge family 자체 development) always-on 적용 = **Phase 2 enforcement CFP 시 도입** (env flag / hook / runtime validation 모두 본 ADR scope 외 — Phase 1 doc-only strict invariant 보존). Phase 1 = wrapper dogfood 도 default false + 사용자 explicit opt-in 의무 (consumer 와 동일 trust model).

flag 위반 시 (default false 인데 ledger write 발생) = `policy_violation` (defect). 별도 lint = TestContractArch §8.4 후보 5 (opt-in default false invariant).

상세 privacy policy = ADR-043 (별도 sibling Phase 1 PR). 본 §결정 = invariant codification only — wording 충돌 시 ADR-043 SSOT.

### 결정 7 — 2-layer telemetry flag schema (Refactor B2 HIGH 채택, scope 축소)

consumer overlay `.claude/_overlay/project.yaml` schema 확장:

```yaml
telemetry:
  enabled: false  # global flag (default false, §결정 6)
  channels:
    stop_event: false  # stop-event-v1 ledger (default false)
  storage_path: ".claude-work/measurement/"  # default
  retention_hot_days: 14  # default 14d (Researcher §6.6 InfluxData multi-tier 중간값)
```

per-channel granular flag (`channels.stop_event`) = 부분 활성 가능. global `enabled: false` 시 모든 channel disabled (override 불가능 — global gate).

future channel (spawn-event-v1 land 시) = `channels.spawn_event` 추가. 본 schema 가 future expansion 안전 (Refactor scope 축소 + 확장성 양립).

`docs/project-config-schema.md` 갱신 의무 (Change Plan §5).

### 결정 8 — 0 API call constraint (OperationalRiskArchitect P0 substantive)

Telemetry instrumentation = **0 API call** (Anthropic API / GitHub API / external service 호출 금지). 근거:

- **measurement = measure 대상 amplify 금지** (CRITICAL invariant — OpRiskArch §7.4.4). 측정 자체가 token burn / rate-limit cascade 유발 시 measurement-vs-fix scope boundary 위반.
- **Best-effort 50ms ceiling** (OpRiskArch §7.4.2) — append latency p99 ≤50ms (TestContractArch §8.3 perf baseline).
- **Local I/O only** = sqlite append (single transaction) + file system write. Network I/O 부재.

위반 시 (telemetry 가 외부 API 호출) = `policy_violation` + immediate hot-fix.

### 결정 9 — Wrapper-vs-consumer ledger isolation (OperationalRiskArchitect §7.4.5)

ledger storage path 분리:

- **Wrapper dogfood**: `mclayer/plugin-codeforge` checkout 의 `.claude-work/measurement/stop-event.sqlite`
- **Consumer**: 각 consumer repo 의 `.claude-work/measurement/stop-event.sqlite`

cross-host 통합 (DAP / aggregate report) = **Phase 2 deferred** (ADR-043 §결정 5 cross-ref). Phase 1 isolation invariant = consumer raw event 가 wrapper repo 로 leak 금지 (T-INFO-4 SecurityArch P0 위협 대응).

### 결정 10 — Measurement-vs-fix scope boundary (OperationalRiskArchitect P0 substantive)

본 CFP-283 scope = **measurement only**. throttling / backoff / circuit breaker / rule-based hook = 별도 후속 CFP. 근거:

- **scope creep 차단** — measurement channel 도입 + enforcement 동시 land = OpRiskArch §7.4 substantive 위반 (production-readiness 미충분).
- **30+ event capture 후 ROI 평가** (Phase 2 trigger — ADR-026 §결정 3 패턴) — current ROI 미확정.

본 §결정 = OpRiskArch P0 적극 이의 채택.

### 결정 11 — ROI gating: post-merge-counters.jsonl 30+ run prerequisite (ADR-026 §결정 3 패턴)

Phase 2 enforcement (rule-based hook / inline write detect / stop-event auto-fire / rate-limit cascade detection) = ROI gate prerequisite:

- post-merge-counters.jsonl (ADR-026) **30+ run 누적 후** ROI 평가 (ADR-026 §결정 3 SSOT).
- ROI metric = (1) inline_violation_count 변화 추세 (2) policy_violation_subdecision stop frequency (3) token cost burn 정량 baseline.
- ROI 충분 (subjective threshold — Sonnet decider Phase 2 ROI 패턴 정합 — ADR-022 §결정 11) 시 follow-up CFP 발의.

본 §결정 = Refactor ROI gating 적극 권고 채택.

### 결정 12 — Phase 1 wrapper-only land scope

Phase 1 PR scope (본 Story):

- `docs/adr/ADR-042-codeforge-measurement-channel-architecture.md` (본 file)
- `docs/adr/ADR-043-codeforge-telemetry-privacy-policy.md` (sibling Phase 1 PR — 별도 ADR)
- `docs/inter-plugin-contracts/stop-event-v1.md` 신설 (kind:registry)
- `docs/inter-plugin-contracts/MANIFEST.yaml` comment update (kind:registry 명시 — entry 추가 안 함)
- `docs/orchestrator-playbook.md` §15 4-channel boundary table content (Reserved 해제)
- `docs/project-config-schema.md` telemetry block schema (§결정 7)
- `docs/consumer-guide.md` § "Telemetry opt-in" 신규 subsection (§7.0.7 권장)
- `docs/domain-knowledge/orchestrator-discipline/measurement-channel.md` 신설
- `wrapper/change-plans/cfp-283-adr-039-measurement-channel.md` (internal-docs SSOT)

**비-Phase 1 scope** (deferred):

- Telemetry hook 구현 (Python script `scripts/telemetry-append.py` 또는 sqlite migration script) = Phase 2 follow-up CFP
- 6 lane plugin 변경 0건 (ADR-039 §결정 5 invariant 보존)
- inter-plugin contract 6 (requirements_output / design_output / review_verdict v3 / test_verdict / develop_output / pmo_output) 변경 0건

### 결정 13 — Spawn-event-v1 미래 도입 시 본 ADR amendment 의무

spawn-event-v1 신설 시 (Phase 2 후속 CFP):

- 본 ADR 의 **§결정 1 4-channel boundary 표 갱신 의무** (5th channel 추가 → boundary race 재평가).
- 본 ADR 의 **§결정 3 보류 결정 supersede** (`Amendment N` 신설).
- §14 ↔ spawn-event dedup script 신설 의무 (Refactor B1 HIGH precondition).

본 §결정 = future expansion path normative 정합 보장.

## 회피된 대안

### 대안 A — spawn-event-v1 즉시 land

Refactor B1 HIGH 변호 — spawn count metric 즉시 capture.

**거부 이유** (§결정 3 verbatim):
- §14 ↔ spawn-event dual-write race (CodebaseMapperAgent 분석)
- aggregate script (§14 + post-merge-counters.jsonl 합산) 로 spawn count 도출 가능
- 30+ post-merge-counters run ROI 평가 후 결정 (Refactor 자체 ROI 권고와 정합)

채택 = §결정 3 보류 + 후속 CFP.

### 대안 B — Hot tier default = JSONL

JSONL 채택 시 grep / cat 가능성 ↑.

**거부 이유** (§결정 4 verbatim):
- append race / corruption recovery / idempotency 모두 application-level 책임 → 운영 risk ↑
- DataMigrationArch substantive 적극 권고 (sqlite WAL mode + UNIQUE INDEX (event_id))

채택 = §결정 4 sqlite default.

### 대안 C — Privacy policy 를 본 ADR-042 §결정 추가 (sibling ADR-043 미신설)

privacy / opt-in / sanitize 정책을 본 ADR §결정 5-6 에 inline.

**거부 이유** (SecurityArch substantive 적극 권고):
- privacy = cross-cutting concern (future ledger 신설 시 재사용 — spawn-event-v1 / 향후 어떤 telemetry 든 동일 정책 inherit)
- ADR-029 §결정 2 sanitize policy SSOT 와 통합 가능 (단일 privacy ADR 가 narration + ledger sanitize 통합)
- ADR-042 = architectural decision, ADR-043 = policy decision — SSOT 분리가 maintainability ↑

채택 = ADR-043 sibling Phase 1 PR (별도 ADR).

### 대안 D — Telemetry opt-in default = true (always-on)

Wrapper dogfood + consumer 모두 always-on.

**거부 이유** (§결정 6 verbatim):
- GitHub CLI opt-out 비판 precedent (default-on telemetry + post-hoc opt-out = trust 위반)
- ADR-039 Phase 1 doc-only trust model 패턴 정합 위반
- consumer 측 silent telemetry = trust 위반 (Researcher §6.5)

채택 = §결정 6 default false (wrapper / consumer 동일 trust model — Phase 1 doc-only strict). wrapper dogfood always-on enforcement (env flag / hook) = Phase 2 follow-up CFP.

### 대안 E — Phase 1 즉시 enforcement (rule-based hook)

PreToolUse hook 으로 inline write detect → 즉시 차단.

**거부 이유** (§결정 10 verbatim):
- ADR-025 / ADR-029 / ADR-039 의 Phase 1 trust model precedent 위반
- measurement-vs-fix scope creep — OpRiskArch §7.4 substantive 위반
- ROI gate prerequisite (post-merge-counters 30+ run) 부재

채택 = §결정 10 measurement only + §결정 11 ROI gating.

## 외부 fact (Researcher §6 reference)

본 ADR 의 §결정 정당화 + 회피된 대안 reject 근거의 외부 데이터 (Story §6 verbatim):

1. **OpenTelemetry GenAI Semantic Conventions** — https://opentelemetry.io/docs/specs/semconv/gen-ai/
   - `gen_ai.*` namespace SSOT — codeforge schema = inspired-only (strict adopt 안 함, namespace 충돌 회피)
2. **Anthropic Prompt Caching** — https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
   - `usage` 4 필드 (input / output / cache_creation 1.25× / cache_read 0.1×) 전체 합산 의무 — **본 ADR scope 외** (spawn-event-v1 deferred — token attribution 은 Phase 2)
3. **Claude Code Issue #5904 — nested spawn double-count anti-pattern** — https://github.com/anthropics/claude-code/issues/5904
   - parent_spawn_id reference + chain dedup — §결정 2 `parent_event_id` field 정당화
4. **InfluxData multi-tier downsampling** — https://www.influxdata.com/blog/downsampling-influxdb/
   - Hot (7-30d raw) / Warm (90d 1-min downsample) / Cold (trend only) — 본 ADR scope = Hot tier only (§결정 4 default 14d)
5. **Privacy-preserving telemetry**:
   - GitHub CLI opt-out 비판 사례 — §결정 6 default-off 정당화
   - Divvi Up DAP (IETF distributed aggregation, https://divviup.org/) — §결정 9 cross-host 통합 Phase 2 reference
   - arxiv 2507.06350 LDP — Phase 2 dashboard cold tier sanitize 참고

**Fact gap**:
- spawn latency 정량 데이터 부재 (Anthropic 정성 언급만, ADR-039 §6.F gap 잔존) — §결정 11 30+ run ROI gate 가 mitigation
- "always-spawn" binary 정책 + measurement channel 결합의 학계/산업 case study 검색 0건 — wrapper-specific design choice

## 검증 채널

본 ADR 의 검증 채널 = doc lint + schema lint (TestContractArch §8.4 산출물 verbatim — Change Plan §8.4):

1. **stop-event-v1 schema lint** — `scripts/check-doc-frontmatter.sh` chain 확장. kind:registry frontmatter / 16-field schema enumeration / reason_class enum 4종 정합 검증.
2. **MANIFEST.yaml comment lint** — `scripts/check-inter-plugin-contracts.sh` 가 kind:registry vs kind:contract 분류 정합 검증 (stop-event-v1 = kind:registry, MANIFEST entry 미추가 invariant).
3. **4-channel boundary table presence lint** — playbook §15 의 7-row boundary table 존재 검증 (`scripts/check-doc-section-schema.sh` 확장).
4. **opt-in default false invariant** — project-config-schema.md `telemetry.enabled: false` default + consumer-guide § "Telemetry opt-in" cross-ref 존재 검증.
5. **Allow-list ONLY enforcement** — stop-event-v1 schema 의 16 field 외 추가 시 lint FAIL (BREAKING change → ADR amendment 의무).

**현재 Phase 1 PR scope 안 lint 도입** = **0 후보 land** (doc-only invariant 보존). 5 후보 모두 = follow-up CFP (Phase 2 enforcement 도입 시 동반 land — 분리 land = partial enforcement 의미 없음, Phase 1 trust model 정합). 후속 CFP 번호 = post-merge-counters.jsonl 30+ run ROI 평가 후 발의 시 할당 (current 미배정).

## 결과

### 영향 file (wrapper repo)

- `docs/adr/ADR-042-codeforge-measurement-channel-architecture.md` (본 file)
- `docs/adr/ADR-043-codeforge-telemetry-privacy-policy.md` (sibling Phase 1 PR)
- `docs/inter-plugin-contracts/stop-event-v1.md` 신설 (kind:registry)
- `docs/inter-plugin-contracts/MANIFEST.yaml` comment line 5 갱신 (stop-event-v1 추가 명시)
- `docs/orchestrator-playbook.md` §15 (Reserved 해제 — 4-channel boundary table content)
- `docs/project-config-schema.md` §2 schema 확장 (telemetry block)
- `docs/consumer-guide.md` § "Telemetry opt-in" 신규 subsection
- `docs/domain-knowledge/orchestrator-discipline/measurement-channel.md` 신설

### 비-영향

- 6 lane plugin (codeforge-{requirements,design,review,develop,test,pmo}) 변경 없음 (ADR-039 §결정 5 lane plugin 0 변경 invariant 정합)
- Inter-plugin contract 6 (requirements_output / design_output / review_verdict v3 / test_verdict / develop_output / pmo_output) 변경 0건
- design lane 6 SubAgent + 2 CONDITIONAL SubAgent 변경 0건
- Stop discipline (ADR-025) 5 종 whitelist 무변 — stop-event-v1 = ADR-025 §결정 10 deferred slot 채움, whitelist 자체 변경 X
- ADR-031 §14 lane evidence write monopoly 무변 (ownership 무변)
- Story §10 FIX Ledger Orchestrator monopoly 무변 (cold tier proxy 재사용 — 신규 channel 신설 X)
- TodoWrite 흐름 무변 (boundary 차단 — §결정 1 invariant)
- ADR-039 §결정 9 4 deferred items 중 measurement channel slot only 처리 — 다른 3 items (inline write detect hook / spawn cost telemetry / rate-limited cascade detection) 미적용

### Reversibility

- Yes — 본 ADR `status: Deprecated` 전환 + 영향 file revert 시 ADR-039 §결정 9 deferred 상태 복원
- ADR-022 → ADR-035 precedent 패턴 (status flip + Deprecated marker + 회피 doc edit)
- stop-event-v1 contract = `status: Deprecated` 마킹 + sqlite ledger file 삭제 (consumer 측 opt-in 이라 silent revert 가능)

## Out-of-scope

- Phase 2 enforcement (rule-based hook / inline write detect / stop-event auto-fire / rate-limit cascade detection) — §결정 10 + §결정 11 deferred
- spawn-event-v1 신규 contract — §결정 3 보류
- Telemetry hook 구현 (Python script / sqlite migration) — Phase 2 follow-up CFP
- Cross-host telemetry 통합 (Divvi Up DAP / DAP aggregate report) — ADR-043 §결정 5 Phase 2 deferred
- Dashboard / cold tier downsampling — Phase 2 dashboard CFP
- 6 lane plugin agent 의 telemetry 의무 stamping — ADR-039 §결정 5 lane plugin 0 변경 invariant
- Token attribution model (Anthropic API usage 4 필드 합산) — spawn-event-v1 deferred 와 동반 deferred

## 관련 ADR

- **ADR-025** (stop discipline + Epic-level continuity) — **amends** 관계. §결정 10 deferred slot (stop-event-v1) 가 본 ADR §결정 2 로 채움.
- **ADR-026** (post-merge automation) — §결정 3 30+ run ROI 평가 패턴. 본 ADR §결정 11 가 동일 패턴 채택.
- **ADR-029** (phase execution visibility) — §결정 2 sanitize policy 적용 범위 확장 (narration → ledger). §결정 5 cross-ref.
- **ADR-031** (lane-spawn evidence trail) — §14 lane coarse vs spawn-event-v1 (deferred) sub-step boundary. §결정 1 boundary 표 SSOT.
- **ADR-038** (progress visualization TodoWrite) — boundary 차단 (TodoWrite 호출은 ledger record 대상 아님). §결정 1 invariant.
- **ADR-039** (subagent default) — §결정 9 deferred Phase 2 measurement 4 items 중 measurement channel slot 처리. carrier ADR.
- **ADR-043** (telemetry privacy policy) — sibling Phase 1 PR. privacy / opt-in / sanitize 정책 별도 ADR. §결정 5-6 cross-ref.
- **ADR-013** (codeforge family dogfood-out policy) — spec / plan 위치 internal-docs override. 본 ADR Story spec / plan 도 internal-docs SSOT.
- **ADR-024** (Story-scoped branch policy) — 본 Story branch 명명 (`cfp-283-adr-039-measurement-channel`).

## 해소 기준

N/A — permanent policy

## 관련 파일

- `docs/inter-plugin-contracts/stop-event-v1.md` (신설 — kind:registry, §결정 2 schema)
- `docs/inter-plugin-contracts/MANIFEST.yaml` (comment 갱신, §결정 12)
- `docs/orchestrator-playbook.md` §15 (Reserved 해제, §결정 1 4-channel boundary table)
- `docs/project-config-schema.md` (telemetry block schema, §결정 7)
- `docs/consumer-guide.md` § "Telemetry opt-in" (신규, §결정 6)
- `docs/domain-knowledge/orchestrator-discipline/measurement-channel.md` (신설)
- `docs/adr/ADR-043-codeforge-telemetry-privacy-policy.md` (sibling Phase 1 PR)
- `mclayer/codeforge-internal-docs:wrapper/stories/CFP-283.md`
- `mclayer/codeforge-internal-docs:wrapper/change-plans/cfp-283-adr-039-measurement-channel.md`

## Amendment 1 (CFP-2393, 2026-06-24) — spawn-event-v1 보류 해제 + token attribution deferral 해제

### 배경

Epic CFP-2391 S3 (OMC-adopt per-agent replay/cost observability) 가 spawn-event-v1 신설을 carrier 한다. 본 ADR §결정 13 이 명시한 amendment 의무 ("spawn-event-v1 신설 시 §결정 1 boundary 표 갱신 + §결정 3 보류 결정 supersede(`Amendment N` 신설) + §14↔spawn-event dedup script 신설 의무") 의 이행이다. 차용원 = oh-my-claudecode(MIT, https://github.com/Yeachan-Heo/oh-my-claudecode). 신규 contract = [`docs/inter-plugin-contracts/spawn-event-v1.md`](../../docs/inter-plugin-contracts/spawn-event-v1.md) (kind:registry v1.0). Phase 1 = doc-only (§결정 12 stop-event 선례 정합).

### Amendment 내용

**(A) §결정 3 (spawn-event-v1 신설 보류) supersede** — 보류 해제. **원 §결정 3 본문은 보존**(이력) 하되 본 Amendment 가 supersede 한다. spawn-event-v1 = 본 Amendment 로 land. 원 보류근거 3 의 처리:
- 보류근거 #1 (§14↔spawn-event dual-write race) → spawn-event-v1 contract §3 `append_rules.idempotency.section14_dedup` 이 **§14↔spawn-event dedup script 를 Phase 2 precondition AC 로 commit** (read-time dedup, append-time 아님 — cross-channel coupling 회피). race 자체는 SubagentStop single-write(option i) + O_APPEND per-row 로 구조적 차단.
- 보류근거 #2 (aggregate script 로 충분) → per-agent token/cost attribution + replay 재구성은 §14 row count + post-merge-counters.jsonl 로 도출 **불가** (lane-coarse, token granularity 부재). spawn-event = 별 channel 필요성이 Epic directive 로 확정.
- 보류근거 #3 (30+ post-merge-counters run ROI gate) → **아래 §근거 의 ROI gate 처리 참조**.

**(B) §결정 1 4-channel boundary 표 8번째 channel 추가** — boundary 표에 spawn-event-v1 row 추가:

| Channel | Tier | Granularity | Storage | Owner | Lifecycle |
|---|---|---|---|---|---|
| **spawn-event-v1 ledger** (본 Amendment 1) | 3 persistent | per-agent spawn (subagent 1개 = row 1개) | hot tier JSONL (`.claude/ledger/spawn-event.jsonl`) | Orchestrator-owned delegate subagent | persistent append-only / opt-in default false |

playbook §15.1 8-channel boundary table SSOT 동반 갱신 (§결정 1 land 위치). boundary 차단 invariant 에 **§14.12 ↔ spawn-event-v1 role-separation** 4번째 invariant 추가 (Tier-1 quota-only mini-table vs Tier-3 persistent accounting — double-count 아닌 역할 분리). playbook §15.2 동반.

**(C) Out-of-scope "Token attribution model" deferral 해제** — 원 Out-of-scope line "Token attribution model (Anthropic API usage 4 필드 합산) — spawn-event-v1 deferred 와 동반 deferred" 해제. **단 정확도 caveat 명시**: transcript JSONL `usage.input_tokens` 는 streaming placeholder 로 input 100-174x / output 10-17x undercount (verified-via https://gille.ai/en/blog/claude-code-jsonl-logs-undercount-tokens/). 따라서 token attribution 은 "정확 source 확보 시에만 attributed, 그 외 unattributed (추정치 저장 금지)" = spawn-event-v1 contract `attribution_confidence` enum default `unattributed` 가 강제 (ADR-119 검증-후-단언). 0 API call constraint(§결정 8) 하 pricing = 로컬 상수.

**(D) §결정 13 amendment 의무 이행 commit** — §14↔spawn-event dedup script = spawn-event-v1 contract §3 `append_rules.idempotency.section14_dedup` 이 Phase 2 precondition AC 로 명문 commit. (Phase 1 = doc-only — script 실 구현은 Phase 2.)

### 근거

- **§결정 13 자체가 amendment 경로를 지정** — "Amendment N 신설" 명시. 신규 ADR 미신설 (§결정 1 self-amendment 의무 + §결정 13 정합). 본 Amendment 가 첫 amendment (frontmatter `amendment_log` 신규 — 본 ADR 의 첫 amendment).
- **30+ run ROI gate (보류근거 #3) 처리 — 정직 기록**: 본 Story 시점에 post-merge-counters.jsonl 30+ run 누적 ROI 평가의 **충족 evidence 는 본 lane 에서 실측 미확보** (firsthand 미검증). 그러나 보류 해제 정당화 = **Epic CFP-2391 S3 directive 가 deferral 을 supersede** — 사용자/Epic 의 명시 우선순위 결정이 ROI gate 의 subjective threshold (ADR-022 §결정 11 Sonnet decider 패턴) 를 대체. ROI gate 는 "ROI 미확정 시 보류" 의 *default* 였고, Epic directive 는 그 default 를 명시적으로 override 하는 상위 결정이다. (silent skip 금지 — ArchitectAnalyst FLAG 정합. ROI gate 미평가 사실을 숨기지 않고 directive supersede 로 명문화.)
- **Phase 1 doc-only 정합** (§결정 12) — stop-event-v1 선례. 실 hook/append/replay/dedup script = Phase 2.

### 비-영향

- §결정 2 (stop-event-v1 schema) 무변경 — spawn-event 는 별 contract.
- §결정 4 (stop-event hot tier sqlite) 무변경 — spawn-event 는 JSONL (contract=runtime 일치 우선, drift 회피 — spawn-event-v1 §3 / Change Plan §2.4). stop-event 자체의 sqlite↔JSONL drift 정정은 본 Amendment scope 외 (별 follow-up — 3문 게이트).
- §결정 5/6/7/8/9/10/11 (Allow-list / opt-in / 2-layer flag / 0-API·50ms / isolation / measurement-vs-fix / ROI) = spawn-event-v1 inherit (변경 없음, 적용 확장만).
- 6 lane plugin / inter-plugin contract 6 변경 0건 (§결정 12 비-Phase 1 scope 정합).
- stop-event-v1 contract 무변경 (spawn-event 가 sibling 로 추가될 뿐).

## Amendment 2 (CFP-2687, 2026-07-15) — dev-process-event-v1 9th Tier-3 channel + warm-tier + ROI-gate supersede 명문화

### 배경

Epic #2686 Story A (CFP-2687, 선행) 가 codeforge 자기-개선 관측의 **기반 증거층 + 계약(observability substrate + evidence contract)** 을 신설한다. 신규 통합 계약 `dev-process-event-v1`(lane 전이·프롬프트·tool-call·diff·verdict·findings·FIX 전이·최종산출물 8종을 하나의 typed append-only stream 으로 통합) = codeforge observability stack 의 **9번째 Tier-3 persistent channel**. 설계 SSOT = 신규 [ADR-155](ADR-155-dev-process-observability-substrate.md). 본 Amendment 는 §결정 1 channel boundary 표 갱신(§결정 13 amendment 의무 정합) + §결정 4 warm-tier 확장 + §결정 11 ROI-gate supersede 명문화 3건을 codify. Phase 1 = doc-only(§결정 12 stop-event 선례 — 실 계약 파일·capture 배선 = Phase 2).

### Amendment 내용

**(A) §결정 1 8→9 channel boundary 표 dev-process-event-v1 row 추가** — 8-channel boundary 표(playbook §15.1 SSOT)에 9번째 row:

| Channel | Tier | Granularity | Storage | Owner | Lifecycle |
|---|---|---|---|---|---|
| **dev-process-event-v1 ledger** (본 Amendment 2 / ADR-155) | 3 persistent | typed dev-process event (8 type: lane전이/prompt/tool-call/diff/verdict/findings/FIX전이/최종산출물) | 2계층 — hot JSONL index (`.claude/ledger/dev-process-event.jsonl`) + evidence-blob-store (content-addressed redacted blob) | Orchestrator-owned delegate (Port B agent-emit) + hook-adapter (Port A) | 3-tier hot/warm/cold / wrapper always-on · consumer opt-in default false |

- **playbook §15.1 8→9 row + §15.2 5th invariant = Phase 2 co-land**(신규 `dev-process-event-v1.md` 계약 파일과 동반 — Phase 1 에 playbook row 추가 시 Phase 2 계약 파일 참조 = dangling link, mechanical self-check 2d 회피). 본 Amendment 는 결정(9th channel 편입)을 codify, 물리 row 는 계약 파일 co-land.
- **§15.2 5th boundary invariant (신규)**: **dev-process-event = semantic-evidence-aggregation** — 상관 ID cross-read(JOIN) **허용** / accounting payload re-record **금지**. stop/spawn/fix/output 계약의 accounting 을 dev-process 가 복제하면 SoT 이중화(ADR-155 §5.4). dev-process 는 "무엇이 있었나(어떤 stop/spawn/verdict 가 났나)"를 상관 ID 로 참조(JOIN)하되 그 payload 를 재기록하지 않는다.
- **관측 사실(정직)**: §결정 1 body 표 제목은 현재 "4-channel"(원 land 시점 명칭) + 7 row 이고, 8번째(spawn-event Amd1)·9번째(본 Amd2)는 amendment 절에 각각 1-row 로 추가돼 있다 — body 표 제목/row 통합 정합은 playbook §15.1(channel count SSOT)이 권위이며, 본 Amendment 가 body 표 제목 drift 를 자동 정정한다고 주장하지 않는다(별도 정합 작업 영역).

**(B) warm-tier 추가 — dev-process-channel-scoped 3-tier** — §결정 4 는 stop-event hot(sqlite/JSONL)+cold(§10 FIX Ledger proxy) 2-tier. 본 Amendment 는 **dev-process-event-v1 channel 에 한해** hot→warm→cold 3-tier 로 확장(ADR-155 §결정 6):
- hot = 구조화 JSONL index + loose blob (ms, 7-30d proposal)
- warm = 압축 pack + gz, index 무압축 유지 (10s–100s ms, ~90d proposal)
- cold = 아카이브 (s, policy-bound → evict + tombstone)
- 방향 strict hot→warm→cold(역방향/skip 금지). **stop-event/spawn-event 자체 tier 무변경** — warm 확장은 dev-process channel 한정(다른 channel 로 전파 안 함). 수치(7-30d/90d/cap)는 **proposal**(empirical Phase 2 defer, lock-in 금지 — ADR-119).

**(C) §결정 11 ROI-gate supersede 명문화** — §결정 11(post-merge-counters.jsonl 30+ run ROI gate prerequisite)를 Epic #2686 directive 가 supersede(Amd1 CFP-2393 §근거 byte-동형 template [verified: ADR-042:455] — "Epic directive 가 ROI deferral 을 supersede 한 선례"):
- **정직 명기(silent-skip 금지)**: 본 Story 시점에 post-merge-counters.jsonl 30+ run 누적 ROI evidence 는 **본 lane 에서 firsthand 미확보**(미검증). 그러나 Epic #2686 directive("자기측정이 Story 목적" + dormant substrate 활성화)가 ROI gate 의 subjective threshold(ADR-022 §결정 11 패턴)를 override 하는 상위 결정. ROI gate 는 "ROI 미확정 시 보류"의 *default* 였고 Epic directive 가 그 default 를 명시 override.
- Story A 동기(self-referential dogfood 결점 7연속 + content-blind ledger 7,122 rows firsthand)가 곧 ROI 정당화. ROI gate 미평가 사실을 숨기지 않고 directive supersede 로 명문화(ArchitectAnalyst FLAG 정합).

### 근거

- **§결정 13 자체가 amendment 경로 지정** — "spawn-event-v1 신설 시 §결정 1 boundary 표 갱신" 의 dev-process-event(9th channel) 확장 동형. 신규 개념(dev-process substrate)의 architectural 근거 = 신규 ADR-155(§결정 1 self-amendment vs 신규 ADR — 신규 substrate 는 신규 ADR 이 타당, boundary 표 갱신만 본 Amendment).
- **MINOR 영역 정합**(ADR-008 SemVer): additive channel row + tier 확장(channel-scoped) + directive supersede 명문화 = backward-compat. 기존 8 channel / stop·spawn tier 무변경.
- **ROI supersede = Amd1 선례 답습** — 정직 명기(미확보 firsthand) + directive override 명문화. silent-skip 금지.

### 비-영향

- §결정 2~10 (stop-event schema / hot tier sqlite / Allow-list / opt-in / 2-layer flag / 0-API·50ms / isolation / measurement-vs-fix) 무변경 — dev-process-event 는 별도 channel(ADR-155 SSOT).
- stop-event-v1 / spawn-event-v1 contract 무변경 (dev-process 가 new-sibling 로 추가, ADR-155 §결정 2 관계 매트릭스).
- 8 channel 기존 row 무변경 (9번째 additive).
- 6 lane plugin / inter-plugin contract 변경 0건 (Phase 1 doc-only).
- warm-tier = dev-process channel 한정 — 다른 Tier-3 channel(stop/spawn/post-merge) tier 정책 무전파.
