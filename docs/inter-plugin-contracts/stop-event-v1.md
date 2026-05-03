---
kind: registry
registry: stop-event
version: "1.0"
status: Active
authors:
  - Claude (CFP-73 — ADR-025 sibling, wrapper-owned passive stop ledger schema)
related_adrs:
  - ADR-025
  - ADR-022 (CFP-61 — Sonnet decider, 5 trigger + 5 종 user escalation whitelist)
  - ADR-021 (CFP-60 — phase-gap measurable signal, R1+R3 detection source 보강)
  - ADR-008 (SemVer 룰)
related_files:
  - docs/adr/ADR-025-stop-discipline-non-whitelist-as-defect.md (carrier ADR)
  - docs/orchestrator-playbook.md (§15 Stop event ledger 의무 narrative SSOT — 본 registry 와 cross-ref)
  - CLAUDE.md (kind:registry list)
---

# stop-event-v1 — Wrapper-owned passive stop ledger

## 1. 목적

ADR-025 의무 ledger. Orchestrator 가 사용자에게 "진행 confirm" / "선택 의뢰" / "결정 대기" 발화한 모든 시점을 passive 로 기록. PMOAgent retro 시 reason_class 분포 분석 → ADR-022 Phase 2 ROI 평가 (30+ event 후) input. ADR-025 §결정 2 의 "whitelist 외 stop = policy_violation defect" 추적 채널.

## 2. Schema

### 2.1 Storage

- 위치: `<internal-docs>/<plugin-folder>/stop-events.jsonl` (append-only JSONL)
- plugin_folder = `wrapper` / `requirements` / `design` / `develop` / `test` / `pmo` / `review` (codeforge family) / consumer name (e.g., `mctrader-hub`)
- consumer overlay path: `<consumer-repo>/.codeforge/stop-events.jsonl`

### 2.2 Schema body

```yaml
stop_event:
  contract_version: "1.0"
  timestamp: <ISO8601>
  plugin_folder: <string>
  story_key: <STORY_KEY> | null   # null if pre-Story (e.g., session bootstrap)
  lane: requirements | design | design-review | implementation | code-review | implementation-test | security-test | meta | null
  reason_class:
    - intent_ambiguity         # whitelist (d-intent) — 사용자 의도 추정 필요
    - lane_fix_max             # whitelist (e2) — lane FIX max 3 도달
    - prereq_failure           # whitelist — 의존성 / GitHub MCP / billing 등
    - destructive_action       # whitelist — git force / DB drop / file delete
    - denylist_security        # whitelist — 보안 sensitive
    - user_override            # User Override authority (ADR-022 §결정 1) — Sonnet pick 무시 사용자 직접 결정
    - policy_violation         # ADR-025 신규 — whitelist 외 stop = defect
  summary: <markdown, 1-line>
  sonnet_decider_invoked: <bool>     # true if Sonnet 호출 발생, false if user direct stop
  packet_id: <string> | null         # decision-packet v2.1 발화 시 link
```

## 3. 항목

### 3.1 reason_class 분류 가이드 (7 종)

| reason_class | 발화 정당화 | ADR 정합 |
|---|---|---|
| `intent_ambiguity` | 사용자 의도 ambiguous, 추정 필요 | ADR-022 §결정 2 (d-intent whitelist) |
| `lane_fix_max` | lane FIX max 3 도달 | ADR-022 §결정 2 (e2 whitelist) |
| `prereq_failure` | 운영 prerequisite 실패 (GitHub MCP / billing / Anthropic Agent tool) | ADR-022 §결정 2 |
| `destructive_action` | git force-push / DB drop / file delete (reversibility 낮음) | ADR-022 §결정 2 |
| `denylist_security` | 보안 sensitive (credential / secret 노출 위험) | ADR-022 §결정 2 |
| `user_override` | Sonnet decider pick 후 사용자 명시적 다른 결정 | ADR-022 §결정 1 (User Override hierarchy) |
| `policy_violation` | 위 6 종 미해당 stop — Orchestrator incorrect stop (defect) | ADR-025 §결정 2 |

### 3.2 발화 시점 (4 카테고리, ADR-025 §결정 2 + playbook §15.1)

1. 사용자 직접 응답 대기 (clarifying question / confirm prompt)
2. Sonnet decider 호출 직전 / 직후 의사결정 보고
3. Lane transition 또는 PR merge 직전 confirm 요청
4. User Override 발생 (Sonnet pick 후 사용자 다른 결정)

### 3.3 plugin_folder enum (codeforge family + consumer)

- `wrapper` (mclayer/plugin-codeforge)
- `requirements` (mclayer/plugin-codeforge-requirements)
- `design` (mclayer/plugin-codeforge-design)
- `develop` (mclayer/plugin-codeforge-develop)
- `test` (mclayer/plugin-codeforge-test)
- `pmo` (mclayer/plugin-codeforge-pmo)
- `review` (mclayer/plugin-codeforge-review)
- consumer-specific: `mctrader-hub` / `<other-consumer-name>` (overlay path)

## 4. 변경 규칙

### 4.1 Write rule (passive only)

- Orchestrator 가 stop event 발화 시점에 directly append. **새로운 user prompt / confirm 추가 금지** (Codex Cat 6 finding 3 paradox 차단).
- Writer = wrapper Orchestrator only. Lane plugin self-emit 금지 (Phase 1 scope; lane plugin event emission contract = S3, 후속 CFP).
- summary 작성 시 PII / credential / token / 절대경로 sanitize 의무.
- Append-only JSONL — rollback 안 함. Incorrect entry 발견 시 후속 row 로 correction note 추가 (override 안 함).

### 4.2 Read rule

- PMOAgent 가 sprint retro 또는 30+ event 누적 시 read.
- ROI report 의무 위치: `<internal-docs>/<plugin-folder>/retros/<sprint>.md` "Stop event analysis" section.
- ADR-022 §결정 8 Phase 2 transition gate input (30+ packet + cost report 의무 충족).

### 4.3 Boundary (Phase 1 scope, ADR-025 §결정 4)

- ✅ wrapper Orchestrator passive write
- ✅ ledger schema 정의 + read rule
- ❌ enforcement hook / refusal logic (Phase 2 ROI 평가 후, 별도 CFP)
- ❌ lane plugin self-emit (S3, 후속 CFP)
- ❌ review-verdict v3 schema 확장 (S2, 후속 CFP)

### 4.4 Versioning

- v1.0 = initial. Additive minor bump (v1.1+) = backward-compat (e.g., reason_class enum 추가, plugin_folder enum 확장).
- BREAKING (v2.0+) = ADR-008 SemVer 룰 (sibling sync 의무 ADR-010, single canonical 위치 = wrapper).

### 4.5 ADR 정합성

- **ADR-025** §결정 2: whitelist 외 stop = `policy_violation` reason_class. §결정 1 trust model invariant 가 본 ledger 의 발화 시점 결정 (Sonnet pick → 자동 진행, confirm 묻기 = defect).
- **ADR-022** §결정 11 Phase 1 trust model = no enforcement hook 정합.
- **ADR-022** §결정 1 User Override authority = `user_override` reason_class 별도 카테고리 (defect 아닌 정당 권한).
- **ADR-021** R1-R4 detection: stop-event ledger 가 R1 (Missing agent finding repeat) + R3 (Phase gap propagate) source 보강.
