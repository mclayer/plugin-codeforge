## 15. 4-channel observability boundary (ADR-042 §결정 1, CFP-283)

Codeforge observability stack 의 channel 별도 책임 분리 normative SSOT. Tier 1 (ephemeral) / Tier 2 (committed lane-coarse) / Tier 3 (persistent measurement) 으로 stratify, 각 channel 의 Granularity / Storage / Owner / Lifecycle 명시 — boundary race + double-count 차단 invariant.

### 15.1 7-channel boundary table

| Channel | Tier | Granularity | Storage | Owner | Lifecycle |
|---|---|---|---|---|---|
| **stderr narration** ([ADR-029](adr/ADR-029-phase-execution-visibility-expansion.md)) | 1 ephemeral | sub-step | scrollback | Orchestrator | session-only |
| **TodoWrite scratchpad** ([ADR-038](adr/ADR-038-progress-visualization-todowrite.md)) | 1 ephemeral | meta-cognitive | tool surface | Orchestrator | turn-only |
| **`.claude-work/progress/<KEY>.md` cache** (CFP-20) | 1 ephemeral | per-Story coarse | fs cache | Orchestrator | Story-only (post-merge mv `_archive/`) |
| **Story §10 FIX Ledger** (CFP-32 / [fix-event-v1](inter-plugin-contracts/fix-event-v1.md)) | 2 committed | discrete FIX event | git commit | Orchestrator monopoly | persistent (append-only) |
| **Story §14 Lane Evidence** ([ADR-031](adr/ADR-031-lane-spawn-evidence-trail.md)) | 2 committed | lane spawn coarse | git commit | Orchestrator monopoly | persistent (append-only) |
| **post-merge-counters.jsonl** ([ADR-026](adr/ADR-026-post-merge-automation.md)) | 3 persistent | post-merge action outcome | git commit | post-merge-followup.yml | persistent (append-only, opt-in) |
| **stop-event-v1 ledger** ([ADR-042 §결정 2](adr/ADR-042-codeforge-measurement-channel-architecture.md), [stop-event-v1](inter-plugin-contracts/stop-event-v1.md)) | 3 persistent | discrete stop event | hot tier (sqlite/JSONL) + cold tier (markdown) | Orchestrator-owned delegate subagent | hot 7-30d / cold persistent / opt-in default false |

### 15.2 Boundary 차단 invariant (3)

- **TodoWrite ↔ stop-event-v1 boundary**: TodoWrite 호출은 stop-event-v1 ledger record 대상 아님 ([ADR-038](adr/ADR-038-progress-visualization-todowrite.md) standalone 정당화 — meta-cognitive scratchpad, file system / GitHub state mutation 미발화). boundary 차단.
- **§14 ↔ spawn-event-v1 boundary**: spawn-event-v1 신설 보류 ([ADR-042 §결정 3](adr/ADR-042-codeforge-measurement-channel-architecture.md)) — 본 boundary race 회피. Phase 2 spawn-event land 시 dedup script 신설 의무 (§14 row count 와 spawn-event lane=spawn type count 정합 검증).
- **§10 ↔ stop-event-v1 boundary**: stop-event-v1 의 `reason_class: policy_violation` row 가 §10 FIX Ledger row append 의 proxy. dedup 책임 = aggregate script (Phase 2). cold tier 별도 file 신설 안 함 — §10 가 cold tier proxy.

### 15.3 5번째 measurement channel 추가 invariant

5번째 measurement channel (Tier 3) 추가 = [ADR-042](adr/ADR-042-codeforge-measurement-channel-architecture.md) amendment 의무. 본 closed enumeration 가 future "X tool 호출도 ledger record" 류 압박을 차단 — 모두 7-channel 의 어느 하나로 routing 또는 ADR amendment 발의.

### 15.4 Privacy / opt-in 정책 SSOT

stop-event-v1 ledger 의 privacy / opt-in / sanitize 정책 = [ADR-043 (codeforge telemetry privacy policy)](adr/ADR-043-codeforge-telemetry-privacy-policy.md) SSOT. 핵심 invariant 3:

- **opt-in default false** (consumer overlay `telemetry.enabled: false` default)
- **Allow-list ONLY 16 field whitelist** (capture 시점 — stop-event-v1 schema 16 field 외 capture 금지)
- **Deny-list regex 6 pattern** (capture 통과 후 2차 안전망 — API key / GitHub PAT / 한국 주민번호 / email / hex≥32 / GitHub fine-grained PAT)

### 15.5 0 API call constraint + measurement-vs-fix scope boundary

- **0 API call constraint** ([ADR-042 §결정 8](adr/ADR-042-codeforge-measurement-channel-architecture.md)) — telemetry instrumentation = local I/O only. Anthropic API / GitHub API / external service 호출 금지. measurement = measure 대상 amplify 금지 (CRITICAL invariant).
- **measurement-vs-fix scope boundary** ([ADR-042 §결정 10](adr/ADR-042-codeforge-measurement-channel-architecture.md)) — CFP-283 scope = measurement only. throttling / backoff / circuit breaker / rule-based hook = 별도 후속 CFP.
- **ROI gating** ([ADR-042 §결정 11](adr/ADR-042-codeforge-measurement-channel-architecture.md)) — Phase 2 enforcement 발동 prerequisite = post-merge-counters.jsonl 30+ run 누적 ([ADR-026 §결정 3](adr/ADR-026-post-merge-automation.md) 패턴 정합).

### 15.6 Cross-references

- [ADR-042](adr/ADR-042-codeforge-measurement-channel-architecture.md) — measurement channel architecture (본 §15 SSOT)
- [ADR-043](adr/ADR-043-codeforge-telemetry-privacy-policy.md) — telemetry privacy policy (sibling)
- [stop-event-v1](inter-plugin-contracts/stop-event-v1.md) — kind:registry 16-field schema
- [project-config-schema.md](project-config-schema.md) — telemetry block schema (opt-in default false)
- [consumer-guide.md](consumer-guide.md) § "Telemetry opt-in" — consumer 측 안내
- [docs/domain-knowledge/domain/orchestrator-discipline/measurement-channel.md](domain-knowledge/domain/orchestrator-discipline/measurement-channel.md) — 도메인 정의 + cross-ADR boundary 설명

---

