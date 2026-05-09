---
kind: registry
registry: stop-event
version: "1.0"
status: Active
authors:
  - Claude (CFP-283 carrier — ADR-042 §결정 2 schema codification)
related_adrs:
  - ADR-025  # stop discipline (§결정 10 deferred slot 채움)
  - ADR-029  # phase execution visibility (sanitize policy cross-ref)
  - ADR-039  # subagent default (§결정 9 deferred carrier)
  - ADR-042  # measurement channel architecture (본 schema SSOT)
  - ADR-043  # telemetry privacy policy (Allow-list ONLY + Deny-list regex)
related_files:
  - docs/orchestrator-playbook.md  # §15 4-channel boundary table
  - docs/inter-plugin-contracts/MANIFEST.yaml  # comment line 5 — kind:registry 분류 명시
  - docs/inter-plugin-contracts/fix-event-v1.md  # cold tier proxy (§10 FIX Ledger row)
  - docs/project-config-schema.md  # telemetry block schema
---

# stop-event v1

## 1. 목적

ADR-039 effective enforcement 측정을 위한 stop event ledger schema machine-readable SSOT. ADR-025 §결정 10 deferred slot (CFP-73 / CFP-275) 가 본 registry 신설 (CFP-283) 로 채움 — Orchestrator user-stop / decider escalation / policy_violation 발생 시 ledger row append → Phase 2 ROI-driven enforcement 의 발동 trigger 데이터 확보.

**kind:registry 분류** (kind:contract 회피, sibling sync overhead 0건 — CodebaseMapperAgent 권고). MANIFEST.yaml entry 미추가 — comment line 5 갱신만 (`stop-event-v1` kind:registry 명시).

## 2. Schema (16 field — Allow-list ONLY)

각 ledger row entry:

| 필드 | 타입 | 설명 | Sanitize |
|---|---|---|---|
| `event_id` | sha256 string | idempotency invariant — `sha256(packet_id \|\| actor \|\| event_type \|\| timestamp_iso8601)` | hash (raw 부재) |
| `schema_version` | string | `stop-event-v1` 고정 | — |
| `timestamp` | ISO8601 UTC | monotonic — `2026-05-09T14:22:33Z` | — |
| `story_key` | string | e.g. `CFP-283` (KEY prefix overlay 정합) | non-sensitive (public) |
| `phase_label` | enum | `phase:요구사항` ~ `phase:완료` (label-registry-v1) | non-sensitive |
| `lane_label` | enum | 요구사항 / 설계 / 설계-리뷰 / 구현 / 구현-리뷰 / 구현-테스트 / 보안-테스트 / 없음 | non-sensitive |
| `reason_class` | enum (4종) | `user_stop_legitimate` / `decider_escalation_required` / `policy_violation` / `policy_violation_rate_limit_induced` | non-sensitive |
| `reason_class_subclass` | string | free-form, e.g. `policy_violation_subdecision` (≤120자 권장) | **Deny-list regex 6 pattern redact** (ADR-043 §결정 3) |
| `actor` | sha256 hash | top-level Claude session ID hash (raw 금지) | hash (raw 부재) |
| `iter` | int (optional) | FIX iteration counter mirror (§10 row Iter 정합) | non-sensitive |
| `decider_pick` | enum | PASS / FIX / N/A | non-sensitive |
| `override_marker` | bool (optional) | decider override 발생 여부 (PL pl_recommendation ≠ Sonnet pick) | non-sensitive |
| `recovery_action` | enum | retry / escalate / abort | non-sensitive |
| `outcome` | enum | success / failure / partial | non-sensitive |
| `consumer_scope` | enum | `wrapper` / `consumer` (ADR-042 §결정 9 isolation marker) | non-sensitive |
| `parent_event_id` | sha256 reference (optional) | nested spawn attribution chain (Researcher §6.3 dedup) — Phase 2 spawn-event-v1 land 시 cross-ref | hash (raw 부재) |

## 3. Allow-list ONLY enforcement (ADR-043 §결정 2)

**16 field 외 capture 금지**. 추가 field capture = BREAKING change → ADR-042 §결정 2 + ADR-043 §결정 2 amendment 의무.

근거:
- Allow-list = future expansion 시 explicit ADR review 강제 (silent expansion 차단)
- Deny-list 단독 = unknown unknown 위험 (새 PII pattern 미식별 시 leak)
- 2-layer defense in depth (Allow-list + Deny-list, §4)

## 4. Deny-list regex (capture 통과 후 2차 안전망)

`reason_class_subclass` (free-form string field) 등 string 필드에 capture 시점 redact regex 적용:

| Pattern | Regex | 대상 | Placeholder |
|---|---|---|---|
| API key / credential | `(api[_-]?key\|secret\|token\|password\|bearer)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}` | OAuth / API token / DB credential | `[REDACTED:credential]` |
| GitHub PAT | `ghp_[A-Za-z0-9]{36}` | classic GitHub Personal Access Token | `[REDACTED:gh-pat]` |
| GitHub fine-grained PAT | `github_pat_[A-Za-z0-9_]{82}` | fine-grained PAT | `[REDACTED:gh-fg-pat]` |
| 한국 주민번호 | `\d{6}[-\s]?\d{7}` | 13-digit 한국 주민등록번호 | `[REDACTED:krrn]` |
| Email | `[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}` | RFC-5321 email | `[REDACTED:email]` |
| Hex≥32 | `[a-f0-9]{32,}` | hash / private key / TLS cert fingerprint | `[REDACTED:hex]` |

**Match → redact** (`[REDACTED:<rule_name>]` placeholder), **NOT block** — capture 자체는 진행 (정합성 보장 — schema validation 통과).

## 5. event_id 산출식 (idempotency invariant)

```python
import hashlib

def event_id(packet_id: str, actor: str, event_type: str, timestamp_iso8601: str) -> str:
    """
    Idempotency invariant: 동일 event 재시도 시 hardware-level reject (UNIQUE INDEX).
    application-level retry 안전 (network retry / hook retry / spawn retry).
    """
    payload = f"{packet_id}||{actor}||{event_type}||{timestamp_iso8601}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

`UNIQUE INDEX (event_id)` sqlite hardware-level enforcement (ADR-042 §결정 4) — duplicate row insert reject.

`packet_id` = 본 stop event 가 발생한 context 의 packet ID (e.g. decision-packet-v2.1 packet_id, sub-step packet ID, FIX iteration packet ID). 부재 시 `packet_id = "no-packet"` fallback (capture 가능 — schema validation 통과).

## 6. reason_class enum (4종)

| Enum value | 의미 | 발생 contexts |
|---|---|---|
| `user_stop_legitimate` | 합법 stop (whitelist 5종 — ADR-025 §결정 4) | user environment 변경 의무 / destructive action 직전 / unprecedented 상황 / decider escalation_required=true / 작업 단위 완료 후 final report |
| `decider_escalation_required` | decider escalation 발화 (Sonnet decider escalation_required=true) | substantive choice 5 trigger 中 unable-to-decide / packet incomplete / spawn failure |
| `policy_violation` | 정책 위반 (defect — ADR-025 / ADR-039) | sub-decision stop ("inline 으로 충분한가" 류) / Epic level continuity 위반 / Phase boundary 사이 stop |
| `policy_violation_rate_limit_induced` | rate-limit cascade 강제 stop (ADR-039 §결정 9 second-order risk — DomainAgent §2.4 4번째 후보) | Anthropic API rate-limit 으로 강제 stop. ADR-039 enforcement 가 token burn 증가 → rate-limit 빈도 증가 cascade detection |

5번째 enum 추가 = ADR-042 §결정 2 amendment 의무 (BREAKING change).

## 7. Append rules

```yaml
append_rules:
  writer:
    - "Orchestrator-owned delegate subagent (ADR-039 §결정 3 mechanism = subagent OK, ownership = Orchestrator)"
    - "lane plugin agent 가 자체 임의 ledger write = policy_violation (defect)"
    - "fix-event-v1 contract Amendment (CFP-275, 2026-05-08) 패턴 정합 — Orchestrator 정의 = top-level Claude 세션 + Orchestrator 가 spawn 한 delegate subagent 모두 포함"

  storage:
    hot_tier:
      type: sqlite
      path: ".claude-work/measurement/stop-event.sqlite"  # consumer overlay storage_path 로 override
      mode: WAL  # write-ahead log
      retention: 14d  # default (range: 7-30, consumer overlay retention_hot_days override)
      file_mode: "0600"  # T-INFO-2 mitigation (Phase 2 hook 구현 시 의무)
    cold_tier:
      type: markdown
      path: "docs/stories/<KEY>.md §10"  # FIX Ledger row proxy
      proxy_rule: "reason_class: policy_violation row 가 cold tier proxy. 별도 cold tier file 신설 안 함."

  ordering:
    - "append-only — sqlite trigger (BEFORE UPDATE/BEFORE DELETE → ROLLBACK) hardware enforcement"
    - "monotonic timestamp — clock skew 시 MAX(prev_ts + 1ms) rule"
    - "schema_version 필수 — 누락 시 reject (raise) NOT silent corruption"

  idempotency:
    rule: "UNIQUE INDEX (event_id) sqlite hardware enforcement"
    retry_safety: "동일 event 재시도 시 hardware-level reject. application-level retry 안전."
    nested_spawn_dedup: "parent_event_id reference + chain dedup (Phase 2 aggregate script). Researcher §6.3 nested spawn double-count anti-pattern 대응."

  trigger_sources:
    - "Orchestrator user-stop 발화 시 (whitelist 5종 OR policy_violation defect)"
    - "Sonnet decider escalation_required=true response"
    - "Anthropic API rate-limit error (cascade detection — policy_violation_rate_limit_induced)"

  opt_in_default_false:
    rule: "telemetry.enabled: false default (ADR-043 §결정 1 invariant)"
    wrapper_dogfood_exception: "CODEFORGE_DOGFOOD_TELEMETRY=1 explicit env flag 시만 always-on"
    consumer_silent_always_on: "금지 — consumer 측 default false 위반 시 policy_violation"

operational_constraints:
  zero_api_call:
    rule: "0 API call constraint (ADR-042 §결정 8 / OperationalRiskArchitect §7.4.4 P0)"
    rationale: "measurement = measure 대상 amplify 금지. local I/O only. Anthropic API / GitHub API / external service 호출 금지."
    violation: "policy_violation + immediate hot-fix"

  best_effort_50ms_ceiling:
    rule: "append latency p99 ≤50ms (TestContractArch §8.3 perf baseline)"
    overflow_action: "telemetry disable (graceful degradation, NOT error escalation)"

  isolation:
    wrapper_path: "mclayer/plugin-codeforge checkout 의 .claude-work/measurement/stop-event.sqlite"
    consumer_path: "각 consumer repo 의 .claude-work/measurement/stop-event.sqlite"
    cross_host_leak: "금지 (T-INFO-4 P0 위협 — GitHub CLI 비판 사례 대응). Phase 2 cross-host DAP 통합 = ADR-043 §결정 5 deferred."
```

## 8. 변경 규칙

- **Append-only for v1.x**: 16 field 외 새 필드 추가 = ADR-042 §결정 2 + ADR-043 §결정 2 amendment 의무 (BREAKING change → v2.0). Allow-list ONLY enforcement 위반.
- **reason_class enum 추가**: 5번째 enum 도입 시 = ADR-042 §결정 2 amendment 의무 (BREAKING).
- **Deny-list regex 6 pattern 변경**: 추가 / 삭제 = minor (v1.0 → v1.1, BREAKING 아님 — sanitize 강화 / 약화 방향만 다름).
- **storage backend 변경 (sqlite → 다른 DB)**: ADR-042 §결정 4 amendment 의무 (BREAKING — JSONL 회피 사유 + DataMigrationArch substantive 권고 재평가).
- **opt-in default 변경 (false → true)**: ADR-043 §결정 1 amendment 의무 (BREAKING — privacy invariant 위반).

## 9. Phase 1 / Phase 2 scope

### Phase 1 (CFP-283 본 PR)

- 본 schema file 신설 (kind:registry)
- MANIFEST.yaml comment line 5 갱신 (`stop-event-v1` 추가 명시)
- 4-channel boundary table @ playbook §15 (Reserved 해제)
- consumer overlay telemetry block schema
- ADR-042 + ADR-043 신설

### Phase 2 (deferred follow-up CFP)

- Telemetry hook 구현 (Python script `scripts/telemetry-append.py` / sqlite migration script)
- Aggregate script (raw → §10 FIX Ledger row mirror / dashboard 형식 변환)
- spawn-event-v1 신설 (§14 dedup script 동반 의무)
- Cross-host telemetry 통합 (Divvi Up DAP / aggregate report)
- ADR-029 §결정 2 sanitize SSOT 통합 commit (ADR-043 §결정 4 cross-ref)
- Rule-based hook (PreToolUse on Write / Edit / mcp__github__* — inline write detect)

ROI gating prerequisite: post-merge-counters.jsonl 30+ run (ADR-026 §결정 3 패턴 / ADR-042 §결정 11).

## 10. Cross-references

- **ADR-042** (codeforge measurement channel architecture) — 본 schema SSOT (§결정 2 16-field schema)
- **ADR-043** (codeforge telemetry privacy policy) — Allow-list ONLY (§결정 2) + Deny-list regex (§결정 3) + opt-in default false (§결정 1)
- **ADR-025** (stop discipline) — §결정 10 deferred slot 채움 (Amendment)
- **ADR-029** (phase execution visibility) — narration vs ledger boundary (4-channel @ playbook §15)
- **ADR-031** (lane-spawn evidence) — §14 lane coarse vs spawn-event sub-step boundary (spawn-event-v1 deferred)
- **ADR-038** (TodoWrite) — boundary 차단 (TodoWrite 호출은 ledger record 대상 아님)
- **ADR-039** (subagent default) — §결정 9 deferred carrier
- **fix-event-v1** — cold tier proxy (§10 FIX Ledger row append, `reason_class: policy_violation` row)
- **docs/orchestrator-playbook.md §15** — 4-channel observability boundary table
- **docs/project-config-schema.md** — telemetry block schema (opt-in default false)
- **docs/consumer-guide.md** § "Telemetry opt-in" — opt-in 안내
- **docs/domain-knowledge/orchestrator-discipline/measurement-channel.md** — 도메인 정의 + cross-ADR boundary 설명
