---
kind: registry
registry: spawn-event
version: "1.1"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/spawn-event-v1.md
date: 2026-06-24
authors:
  - ArchitectAgent (CFP-2393 — Epic CFP-2391 S3, OMC-adopt per-agent replay/cost. spawn-event-v1 신설 carrier. ADR-163 (measurement) Amendment 1 + ADR-043 Amendment 2 동반)
related_adrs:
  - ADR-163  # codeforge measurement channel architecture — §결정 1 boundary 표 (8th channel) + §결정 3 보류 해제 (Amendment 1) + §결정 13 amendment 의무 이행 + §결정 8 0-API/50ms + §결정 9 isolation
  - ADR-043  # codeforge telemetry privacy policy — §결정 1 opt-in default false + §결정 2 Allow-list ONLY + §결정 3 Deny-list regex (Amendment 2: spawn-event field 추가 + T-INFO-5 transcript hard invariant + T-INFO-7 sha256 identity)
  - ADR-031  # lane-spawn evidence — §14 Lane Evidence (lane-coarse) ↔ spawn-event-v1 (per-agent fine) boundary
  - ADR-038  # progress visualization TodoWrite — boundary 차단 (meta-cognitive scratchpad ≠ accounting)
  - ADR-039  # subagent default — §결정 3 Orchestrator-owned write monopoly (writer 정의)
  - ADR-115  # runtime hook enforcement policy — block 금지 + graceful degradation 5층 inherit
  - ADR-119  # research-before-claims — attribution 불가 시 unattributed/unsupported 정직 표기 근거 (검증-후-단언)
related_files:
  - docs/inter-plugin-contracts/fix-event-v1.md  # 동형 structural model (kind:registry §1/§2/§3/§4 skeleton — drift 회피 위해 stop-event-v1 runtime 가 아닌 본 contract 를 모델로 채택)
  - docs/inter-plugin-contracts/stop-event-v1.md  # sibling Tier-3 ledger (단 contract↔runtime drift 주의 — Change Plan §2.4)
  - docs/inter-plugin-contracts/MANIFEST.yaml  # kind:registry comment line — entry 미추가 (stop-event 선례)
  - docs/orchestrator-playbook.md  # §15.1 8-channel boundary table + §15.2 4번째 boundary invariant + §14.12 관계 note
  - docs/project-config-schema.md  # telemetry.channels.spawn_event flag schema
  - docs/domain-knowledge/domain/orchestrator-discipline/measurement-channel.md  # 도메인 정의 cross-ref
amendment_log:
  - "Amendment 3 (CFP-2572, 2026-07-05) — self-context-v1 6-field record type 추가 (§2.1 신설, L7 Orchestrator self-context proxy). 동일 spawn-event.jsonl channel 공유 + schema_version discriminator 구분. version 1.0 → 1.1 MINOR (additive record type, ADR-008 §결정 2). SSOT = ADR-043 Amendment 3 / ADR-142 §결정 4. 19-field spawn row schema 무변경 (별 record type)."
attribution:
  source: oh-my-claudecode (MIT, https://github.com/Yeachan-Heo/oh-my-claudecode)
  scope: "per-agent registry 개념(token_usage/cost_usd/tool_usage field 구조) + replay event 종류(agent_start/agent_stop/tool/file_touch/mode_change) + 경과시간 keyed 패턴 차용. enforcement(COST_LIMIT_USD intervention) / HUD UI / model routing 은 비-차용 (측정·관측만, ADR-163 §결정 10 measurement-vs-fix boundary)."
---

# spawn-event v1

> **출처 표기 (Epic CFP-2391 공통 제약)**: 본 contract 의 per-agent registry 개념 + replay 모델 = **oh-my-claudecode(MIT) 차용** (https://github.com/Yeachan-Heo/oh-my-claudecode). 차용 경계 = frontmatter `attribution.scope` SSOT. enforcement(COST_LIMIT intervention)는 차용 제외 — codeforge 는 측정·관측만 (ADR-163 §결정 10).
>
> **structural model pin**: 본 contract 는 **`fix-event-v1.md` 동형** (kind:registry §1목적/§2Schema/§3항목/§4변경규칙) 으로 author 됐다. **`stop-event-v1` runtime (`scripts/lib/append_stop_event.py`) 은 모델로 삼지 않는다** — stop-event 의 contract↔runtime 3-way drift (계약 18 field vs runtime 5 field, 계약 sqlite vs runtime JSONL, 계약 sha256 actor vs runtime raw session_id; Change Plan §2.4 / §7) 를 복사하지 않기 위함. spawn-event 는 contract 가 곧 runtime spec 의 SSOT 이며, Phase 2 구현은 본 §3 append_rules 를 byte-faithful 하게 따른다.

## 1. 목적

`docs/inter-plugin-contracts/spawn-event-v1.md` = codeforge 관측성 스택 **Tier 3 (persistent measurement) 의 8번째 channel** = per-agent token/cost attribution ledger 의 row schema + append rule + idempotency + replay event-type machine-readable SSOT.

attribution 단위 = **Agent tool spawn 1회 = subagent 1개 = spawn-event row 1개**. §14 Lane Evidence(lane-coarse) 보다 fine, TodoWrite(meta-cognitive) 와 disjoint.

본 channel 은 codeforge 설계 공간에서 **이미 예약된(named) future channel** 의 보류 해제다 — 진공의 신개념이 아니다:
- ADR-163(measurement) §결정 3 = spawn-event-v1 신설 보류 → 본 contract 가 **Amendment 1** 로 해제.
- ADR-163(measurement) §결정 13 = "spawn-event-v1 신설 시 §결정 1 boundary 표 갱신 + §결정 3 supersede(Amendment N) + §14↔spawn-event dedup script 신설 의무" → 본 contract 가 amendment 의무 이행.
- ADR-043 §결정 1 = "future: spawn-event-v1 등 = opt-in default false" → inherit 확정 (ADR-043 **Amendment 2**).
- ADR-163(measurement) Out-of-scope = "Token attribution model = spawn-event-v1 deferred 와 동반 deferred" → 본 contract 가 해제.

### 1.1 §14.12 ↔ spawn-event-v1 역할 분리 (boundary declaration — double-count 아님)

playbook §14.12 "Spawn-level token telemetry mini-table"(Issue #300) 와 본 channel 은 **역할 분리(role separation)** 관계이지 이중 기록(double-count)이 아니다 (Refactor HIGH 채택):

| 축 | §14.12 mini-table | spawn-event-v1 (본 contract) |
|---|---|---|
| Tier | Tier 1 ephemeral | Tier 3 persistent |
| 목적 | quota 분석 (§8.2 예산 대비 실적 추적) | per-agent **회계(accounting)** + replay 재구성 |
| 저장 | `.claude-work/progress/<KEY>.md` (gitignored) | host-local ledger (opt-in, retention) |
| lifecycle | Story-only (post-merge `_archive/`) | persistent append-only |
| 신뢰도 표기 | `?` placeholder (미노출 시) | `attribution_confidence` enum (1급 상태) |

§14.12 는 spawn-event land 이후에도 **Tier-1 quota-only 채널로 잔존**한다 (deprecate 안 함 — playbook §14.12 "관계" note). 두 채널의 disjoint = playbook §15.2 **4번째 boundary invariant** 로 명문화. cross-write 금지 — 한쪽이 다른 쪽을 읽거나 mirror 하지 않는다(50ms ceiling + cross-channel coupling 회피, §3 append_rules).

## 2. Schema (19개 필드 Allow-list ONLY — enum / numeric / hash 만, free-form string 부재)

각 spawn-event ledger row entry = **19개 필드 Allow-list** (아래 표 19 row, §4 변경 규칙 SSOT). **free-form string field 0개** (T-INFO-8 SecurityArch — Deny-list 가 no-op 이 되도록 구조적 차단; Deny-list inherit 는 defense-in-depth 로 선언만, §4):

| 필드 | 타입 | 필수 | 설명 | Sanitize |
|---|---|---|---|---|
| `event_id` | sha256 string | required | idempotency invariant — **deterministic** `sha256(session_id_hash \|\| agent_id_hash \|\| spawn_seq)` (random UUID 금지 — InfraOpArch §11.6). 동일 spawn 재시도 read-time dedup key | hash (raw 부재) |
| `schema_version` | string | required | `spawn-event-v1` 고정 | — |
| `timestamp` | ISO8601 UTC | required | **UTC Z strict** — `2026-06-24T14:22:33Z`. +00:00 / bare datetime 불허 (fix-event-v1 §4 / stop-event-v1 정합) | — |
| `story_key` | string | required | e.g. `CFP-2393` (KEY prefix overlay 정합). Public non-sensitive | non-sensitive (public) |
| `lane_label` | enum | required | 요구사항 / 요구사항-리뷰 / 설계 / 설계-리뷰 / 구현 / 구현-리뷰 / 구현-테스트 / 보안-테스트 / 배포 / 배포-리뷰 / 없음 (label-registry-v2 정합 — 10 lane + 없음). closed-set | non-sensitive |
| `agent_type` | enum (semi-open) | required | spawn 된 subagent 종류 (e.g. `ArchitectPLAgent` / `DomainAgent` / `DeveloperAgent`). **Public non-PII** (SecurityArch — Allow-list safe). **value set = roster-derived + `unknown-agent` fallback (semi-open, NOT strict closed-set)** — value ∈ (`templates/` agent roster ∪ consumer `project.yaml` roster); roster 미등재 = `unknown-agent` fallback (정확 closed-set 이 아닌 이유 = 미등재 값을 reject 하지 않고 fallback bucket 으로 흡수. Deny-list 불요 — fallback 이 free-form leak 차단). **lint(§8.1)은 enum membership reject 검증 아님** — `unknown-agent` 가 fallback 으로 존재함을 검증 (lint-vs-reality gap 회피) | non-sensitive |
| `attribution_confidence` | enum | required | `{attributed, unattributed, unsupported}`. **default = `unattributed`** (token source 정확도 미보장 시 — F2 transcript undercount caveat). `attributed` = 정확 source 확보 / `unattributed` = source 부정확·불가 (token field = null) / `unsupported` = 플랫폼이 token surface 미제공. **추정치 저장 금지** (ADR-119 검증-후-단언) | non-sensitive |
| `input_tokens` | int \| null | optional | OMC `SubagentInfo.token_usage.input_tokens` 차용. `attribution_confidence != attributed` 시 **null** (추정 합산 금지). numeric only | non-sensitive (count) |
| `output_tokens` | int \| null | optional | OMC 차용. 위 동일 (null when not attributed) | non-sensitive (count) |
| `cache_creation_input_tokens` | int \| null | optional | OMC 차용 (Anthropic prompt-caching 1.25× tier). null when not attributed | non-sensitive (count) |
| `cache_read_input_tokens` | int \| null | optional | OMC 차용 (0.1× tier). null when not attributed | non-sensitive (count) |
| `cost_usd` | number \| null | optional | `token × pricing(local constant)` 파생 (T-TAMP-1 — 0 API, pricing table = 로컬 상수). `attribution_confidence != attributed` 시 null (unattributed token → unattributed cost). numeric only | non-sensitive |
| `duration_ms` | int \| null | optional | spawn→stop elapsed (OMC `tool_usage.duration_ms` 차용). numeric only | non-sensitive |
| `tool_call_count` | int \| null | optional | subagent 의 tool 호출 횟수 (OMC tool_usage array length 차용). numeric only | non-sensitive |
| `actor` | sha256 hash | required | top-level Claude session ID **hash** (raw 금지 — T-INFO-7 SecurityArch P1). **stop-event runtime 의 raw session_id 패턴 복사 금지** (append_stop_event.py line 73 bug). | hash (raw 부재) |
| `parent_event_id` | sha256 reference \| null | optional | nested spawn attribution chain (subagent 가 또 spawn 시 이중계산 방지 — F4 / claude-code#5904). read-time chain dedup key. raw 부재 | hash (raw 부재) |
| `consumer_scope` | enum | required | `{wrapper, consumer}` (ADR-163 §결정 9 isolation marker) | non-sensitive |
| `event_type` | enum | required | replay event 종류 (OMC session-replay 차용) — `{agent_start, agent_stop, tool, file_touch, mode_change}`. closed-set. attribution row = `agent_stop` 가 primary (token/cost 확정 시점) | non-sensitive |
| `elapsed_seconds` | number \| null | optional | replay 경과초 keyed (OMC `agent-replay-*.jsonl` 차용) — Story/세션 시작 기준 상대 시각. replay 재구성 정렬 key. numeric only | non-sensitive |

**Allow-list ONLY enforcement**: 위 19 field 외 capture 금지. 추가 field = BREAKING (ADR-043 §결정 2 Amendment 의무, §4). **free-form string field 부재** = T-INFO-8 구조적 mitigation (Deny-list 적용 대상 0건, 단 §4 에 inherit 선언 — defense in depth).

§2 row markdown 형식 예시 (attribution 가능 case + 불가능 case 양쪽):

```markdown
| event_id | schema_version | timestamp | story_key | lane_label | agent_type | attribution_confidence | input_tokens | output_tokens | cost_usd | duration_ms | actor | parent_event_id | consumer_scope | event_type | elapsed_seconds |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| <sha256> | spawn-event-v1 | 2026-06-24T10:15:00Z | CFP-2393 | 설계 | ArchitectPLAgent | unattributed | null | null | null | 42300 | <sha256> | null | wrapper | agent_stop | 915.4 |
| <sha256> | spawn-event-v1 | 2026-06-24T10:16:10Z | CFP-2393 | 설계 | CodebaseMapperAgent | attributed | 18420 | 5210 | 0.214 | 38100 | <sha256> | <parent-sha256> | wrapper | agent_stop | 985.0 |
```

> Phase 1 = doc-only (실 row 미작성 — §5). 위 numeric 값은 schema 형식 예시이며 **실측 token/cost 가 아니다**. unattributed row 의 token/cost = `null` (추정치 저장 금지).

## 2.1 self-context-v1 record type (ADR-043 Amendment 3 — L7 Orchestrator self-context proxy)

**별개 record type** — 위 §2 의 19-field spawn row 와 **다른** row schema 이며, **동일 `spawn-event.jsonl` channel 을 공유**한다. 두 record type 은 `schema_version` **discriminator** 로 구분된다 (`spawn-event-v1` = 19-field spawn row / `self-context-v1` = 아래 6-field lead-self aggregate row). 본 record 는 장기 세션 Orchestrator(lead-self)의 context 누적을 **record-only proxy telemetry** 로 남긴다. substrate = 기존 SubagentStop-wired 채널 재사용 (신규 hook 블록 0). 실 emission 은 Phase 2 (본 §2.1 = allow-list POLICY 편입 — ADR-043 Amendment 3 §근거 (C)).

### 2.1.1 self-context 6 field (numeric / enum / hash only)

| 필드 | 타입 | 필수 | 설명 | Sanitize |
|---|---|---|---|---|
| `schema_version` | const string | required | `self-context-v1` 고정 — 19-field spawn row 와의 **discriminator** | — |
| `session_id` | sha256 hash | required | top-level Claude session ID **hash** (raw session_id 저장 금지 — T-INFO-7 상속) | hash (raw 부재) |
| `turn_index` | int | required | monotonic turn 카운터 | non-sensitive (count) |
| `delegation_ratio` | float 0.0–1.0 | required | inline 대비 spawn 위임 비율 (coarse-round). **proxy** — lead-self ground-truth 아님 | non-sensitive (ratio) |
| `pre_tokens` | int | required | bucketed 정수. source = `compact_boundary.preTokens` (transcript raw 미도달 — T-INFO-5) | non-sensitive (bucketed count) |
| `cause_category` | enum (CLOSED) | required | `{read-heavy, synthesis-inline, fix-diagnosis, spawn-dispatch, skill-load, env0-mediation, other}` — **domain-agnostic 고정 closed-set** | non-sensitive |

**FORBIDDEN** (T-INFO-8 구조적 차단): file path / transcript 발췌 / tool_input body / free-form reason string. `cause_category` enum 값은 consumer file-path / BC 명 / prompt text 에서 **파생 금지** — domain-agnostic 고정 closed-set (SecurityArch 확정, 특정 consumer 도메인 노출 surface 0).

### 2.1.2 inherit 선언 (spawn-event-v1 privacy 정책 상속)

- **opt-in default-false** (§3 opt_in_default_false 상속) — always-on 금지. `telemetry.enabled: false` + channel default false.
- **Deny-list inherit** (§4 defense-in-depth) — self-context 6 field 도 free-form string field 0개이므로 적용 0건, 선언만.
- **T-INFO-5** transcript content / path 미저장 상속 — `pre_tokens` 는 `compact_boundary` 정수만, transcript raw 는 row 에 도달하지 않는다.
- **T-INFO-7** sha256 identity — `session_id` 는 hash (raw session_id 미저장).

### 2.1.3 operational posture (never-block + fail-VISIBLE)

- `hook_decision = record-only` (Amendment 1 §결정 2 non-blocking 상속) — **never-block**: telemetry 실패가 작업을 halt 하지 않는다.
- **fail-VISIBLE**: dropped event 는 stderr / dropped-count 로 **구별 가능한 trace** 를 남긴다. **silent-success-on-error 금지** (조용히 성공 위장 금지 — ADR-119).
- **idempotency-key** = turn-id / `compact_boundary` event-id + **read-side dedup** — 누적 Σ proxy 의 replay 팽창(중복 집계) 차단.

### 2.1.4 hollow-gate 1순위 (ADR-119 검증-후-단언)

`delegation_ratio` / `pre_tokens` 는 **proxy 이지 lead-self ground-truth 가 아니다** (platform 이 live per-turn self-context surface 미제공 — P1). **어떤 self-context 판정도 게이트가 아니다. record-only.** 본 record 로 gate / block / deny 를 세우지 않는다 (ADR-142 tier 정직 invariant — L7 = record-only proxy).

### 2.1.5 disjoint-axis note

self-context proxy telemetry 는 layer-1 delegation-ratio substrate 를 **재사용**한다. 이는 **record-only measurement 이지 whitelist entry 가 아니다** — ADR-039 §결정 2 inline-whitelist(inline-vs-spawn mechanism 축)와 **disjoint axis** (그 6-entry closed enumeration 무침범).

## 3. 항목

```yaml
spawn_event_schema:
  event_id:
    type: sha256 string
    required: true
    constraints:
      - "deterministic — sha256(session_id_hash || agent_id_hash || spawn_seq). random UUID 금지 (InfraOpArch §11.6 — at-least-once 재시도 시 동일 event 동일 id)"
      - "read-time dedup key (JSONL append-only — DB UNIQUE 부재 OK, aggregate/replay 시점 dedup)"

  schema_version:
    type: string
    required: true
    const: "spawn-event-v1"

  timestamp:
    type: ISO8601
    required: true
    constraints:
      - "UTC strict — Z suffix 필수 (예: 2026-06-24T14:22:33Z). +00:00 / bare datetime 불허"
      - "millisecond precision optional"

  story_key:
    type: string
    required: true

  lane_label:
    type: enum
    required: true
    values: [요구사항, 요구사항-리뷰, 설계, 설계-리뷰, 구현, 구현-리뷰, 구현-테스트, 보안-테스트, 배포, 배포-리뷰, 없음]
    note: "label-registry-v2 lane enum 정합 (10 lane + 없음, 11 값). closed-set — 신규 lane 추가 시 ADR-043 §결정 2 Amendment 동반"
    stop_event_alignment: "spawn-event lane_label = 11 값 registry 정합(현행). stop-event 측 lane_label 표현은 stale — **stop-event lane_label alignment = Phase 2 deferred** (stop-event 영역 over-reach 회피, 본 spawn-event Story scope 외). spawn-event 는 이 stale 을 복사하지 않음."

  agent_type:
    type: "enum (semi-open — roster-derived + unknown-agent fallback)"
    required: true
    value_set: "(templates/ agent roster ∪ consumer project.yaml roster) ∪ {unknown-agent}"
    note: |
      Public non-PII (SecurityArch — Allow-list safe).
      **semi-open enum (NOT strict closed-set)**: value ∈ (templates/ agent roster ∪ consumer project.yaml dev/lane roster).
      roster 미등재 = `unknown-agent` fallback — 미등재 값을 reject 하지 않고 fallback bucket 으로 흡수.
      이 fallback 이 free-form string leak 을 구조적 차단 (Deny-list 불요).
      **strict closed-set 이 아닌 이유**: roster 가 lane plugin/consumer overlay 로 진화하므로 정확 enumeration 을 contract 가 freeze 할 수 없음 → roster-derived 동적 + fallback semi-open 으로 lint-vs-reality gap 회피.
    lint_target: "Phase 2 §8.1 lint 은 enum membership reject 검증이 아니라 `unknown-agent` fallback 존재 + roster-derived 규칙 명시를 검증 (semi-open semantics 반영)"

  attribution_confidence:
    type: enum
    required: true
    values: [attributed, unattributed, unsupported]
    default: unattributed
    rule: |
      attributed   = 정확 token source 확보 시에만. token/cost field 값 기록.
      unattributed = source 부정확(transcript undercount — gille.ai 100-174x input / 10-17x output) 또는 불가. token/cost = null.
      unsupported  = 플랫폼이 token surface 미제공 (SubagentStop payload 직접엔 token 부재). token/cost = null.
      **추정치 저장 절대 금지** (ADR-119 검증-후-단언). naive transcript-sum = unattributed 로 분류 (attributed 아님).
      derivation fn 은 정확 source 미확보 시 unattributed 를 반환 (default = unattributed, NOT 0 / NOT 추정).

  token_fields:  # input_tokens / output_tokens / cache_creation_input_tokens / cache_read_input_tokens
    type: "int | null"
    required: false
    source: "OMC SubagentInfo.token_usage 4 field 차용 (oh-my-claudecode MIT)"
    rule: "attribution_confidence == attributed 일 때만 numeric. 그 외 null. 추정 합산 금지."

  cost_usd:
    type: "number | null"
    required: false
    rule: "token × local pricing constant 파생 (T-TAMP-1 — 0 API call, pricing = 로컬 상수 table). unattributed token → unattributed cost (null). model pricing stale 리스크 = pricing constant 갱신은 별 maintenance (Phase 2)"

  duration_ms:
    type: "int | null"
    required: false
    source: "OMC tool_usage.duration_ms 차용"

  tool_call_count:
    type: "int | null"
    required: false

  actor:
    type: sha256 hash
    required: true
    rule: |
      top-level Claude session ID 의 sha256 hash. **raw session_id 저장 금지** (T-INFO-7 SecurityArch P1).
      stop-event runtime (append_stop_event.py line 73) 의 raw session_id 패턴을 **복사하지 않는다** — contract sha256 모델 채택.
      (stop-event runtime raw bug 자체의 수정 = 별 follow-up, 본 contract scope 외 — InfraOpArch 3문 게이트)

  parent_event_id:
    type: "sha256 reference | null"
    required: false
    rule: "nested spawn (subagent → subagent) 이중계산 방지 chain. read-time chain dedup (aggregate/replay 시점). Researcher §6.3 / claude-code#5904 anti-pattern 대응"

  consumer_scope:
    type: enum
    required: true
    values: [wrapper, consumer]

  event_type:
    type: enum
    required: true
    values: [agent_start, agent_stop, tool, file_touch, mode_change]
    source: "OMC session-replay event 종류 차용 (oh-my-claudecode MIT)"
    note: "attribution row primary = agent_stop (token/cost 확정 시점). agent_start/tool/file_touch/mode_change = replay 재구성 detail event"

  elapsed_seconds:
    type: "number | null"
    required: false
    source: "OMC agent-replay-*.jsonl 경과초 keyed 차용"
    note: "Story/세션 시작 기준 상대 시각 — replay 재구성 정렬 key (절대 timestamp 와 별개)"

append_rules:
  writer:
    - "Orchestrator-owned delegate subagent 만 (ADR-039 §결정 3 — mechanism = subagent OK, ownership = Orchestrator)"
    - "lane plugin agent 가 자체 임의 ledger write = policy_violation (defect). spawn-event 도 stop-event 와 동일 monopoly inherit"
    - "**write 지점 = SubagentStop hook single-write (option i)** — PreToolUse(Agent) spawn-gate 에 ledger write 추가 금지 (Refactor HIGH — spawn-gate 의 'filesystem touch 0' SRP 위반). 2-phase open/close 미채택"

  write_mechanism:
    storage:
      type: JSONL  # append-only (stop-event runtime 와 동일 — sqlite 계약 理想 미채택, drift 회피)
      path: "${CLAUDE_PROJECT_DIR}/.claude/ledger/spawn-event.jsonl"  # consumer overlay telemetry.storage_path 로 override (단 wrapper dir 로 escape 금지 — InfraOpArch §7.4.5)
      storage_path_override_rule: |
        **telemetry.storage_path override = parent dir 대체 규칙 (per-channel 별 default, basename 고정)**:
          - spawn-event 의 basename = `spawn-event.jsonl` **고정** (override 가 basename 을 바꾸지 않음). override 값은 **parent dir 만** 대체한다 → 최종 path = `<storage_path>/spawn-event.jsonl`.
          - spawn-event default parent = `.claude/ledger/` (storage_path 미지정 시).
          - stop-event(sqlite) default parent = `.claude-work/measurement/` (basename = `stop-event.sqlite`). storage_path 미지정 시 이 default.
          - **per-channel 별 default 가 다름** — `telemetry.storage_path` 는 양 channel 에 동일 적용된다 (지정 시 두 channel 의 parent dir 을 함께 대체, 각자 자기 basename 유지). 미지정 시 각 channel 의 위 default parent 사용.
          - escape 금지: override 값이 wrapper checkout dir 로 escape 금지 (InfraOpArch §7.4.5 / ADR-163 §결정 9 isolation). project-config-schema.md telemetry.storage_path comment 정합.
      note: "JSONL 채택 사유 = (1) DB UNIQUE 부재여도 deterministic event_id + read-time dedup 로 idempotency 충분 (InfraOpArch §11.6) (2) stop-event runtime 와 동형 = 운영 패턴 검증됨. sqlite 는 stop-event 계약 理想이나 runtime 미구현 = drift — spawn-event 는 contract=runtime 일치 우선"
      pattern_a_disclaimer: "**host-local ledger ≠ Pattern A 대상**. race-condition-handling-pattern.md 의 Pattern A(SHA-based optimistic concurrency) 는 cross-repo Contents API write(post-merge-counters.jsonl) 전용 — host-local O_APPEND per-row(spawn-event/stop-event)에는 적용하지 않는다. Tier-3 ledger 라고 전부 Pattern A 가 아니다 (write 토폴로지로 갈림: cross-repo=Pattern A 의무, host-local=O_APPEND kernel-atomic 로 충분). measurement-channel.md Tier-3 분기 note 정합."
    append_io:
      rule: "**O_APPEND per-row** — os.open(path, O_APPEND | O_CREAT) 1 row write (InfraOpArch H1 권고). stop-event runtime 의 read-modify-write(whole-file read + append + os.replace) 패턴 복사 금지 — 병렬 spawn 동시 SubagentStop 시 lost-update race (append_stop_event.py _atomic_append). os.replace 는 torn-write 막지만 lost-update 못 막음"
    file_mode: "0600 (Unix); Windows = ACL 영역 외 no-op"

  idempotency:
    rule: "deterministic event_id (random UUID 금지) + read-time dedup (aggregate/replay 시점, append-time 아님)"
    nested_spawn_dedup: "parent_event_id chain — nested spawn 이중계산 방지 (read-time)"
    section14_dedup: "**§14 Lane Evidence ↔ spawn-event dedup script = ADR-163 §결정 13 precondition AC (Phase 2 의무)**. §14 row count(lane spawn coarse) 와 spawn-event row count(per-agent) 정합 검증. dedup = aggregate/read-time script 책임 (append-time 아님 — cross-channel coupling + 50ms 위반 회피, Refactor MED)"
    lane_context_limitation: |
      **SubagentStop trigger 에 story_key / lane_label source 부재 (플랫폼 한계 — F-CR-002)**:
      SubagentStop hook 가용 source = CLAUDE_SESSION_ID / CLAUDE_PROJECT_DIR / CLAUDE_PLUGIN_ROOT env
      + payload(stop_reason / subagent_completed / subagent_type|agent_type / agent_id) 뿐.
      story_key / lane_label 은 env·payload 어디에도 없음 (sibling stop-event runtime 도 동일 미수령).
      → SubagentStop single-write 경로로 append 되는 row 는 story_key="" / lane_label="없음" (default fallback).
      **dedup gate 의 silent-vacuous 회피**: ledger row 가 전부 lane_label="없음" (대조 가능 lane 0) 인 경우
      dedup 는 "consistent" 가 아니라 **"vacuous" status** 를 emit 한다 (정합 PASS 위장 금지 — ADR-119 검증-후-단언).
      lane-context writer (lane plugin agent 가 spawn-time 에 lane_label 을 주입하는 별 채널) 가 가용해지기
      전까지 meaningful §14 ↔ spawn-event reconcile 은 불가 — vacuous 가 정상 상태. **dedup gate 를 lane-context
      writer 가용 시점까지 명시 defer 할지 = 설계 결정 (ArchitectPLAgent 판정 대상, Change Plan §8 갱신 후보).**

  opt_in_default_false:
    rule: "telemetry.enabled: false default + telemetry.channels.spawn_event: false default (ADR-043 §결정 1 inherit — wrapper / consumer 동일 trust model)"
    wrapper_dogfood: "Phase 1 = wrapper dogfood 도 default false + 사용자 explicit opt-in 의무 (always-on enforcement = 별 Phase 2 CFP)"
    silent_always_on: "금지 — default false 위반 시 policy_violation"

operational_constraints:
  zero_api_call:
    rule: "0 API call (ADR-163 §결정 8) — Anthropic/GitHub/external API 호출 금지. token source = transcript_path 파싱 또는 SDK total_cost_usd (Phase 2 실측 후 택일), pricing = 로컬 상수. local I/O only"
    rationale: "measurement = measure 대상 amplify 금지 (CRITICAL)"

  best_effort_50ms_ceiling_plus_transcript_overflow:
    rule: "append latency p99 ≤50ms (ADR-163 §결정 8). **단 50ms ceiling 은 free-inherit 아님** — transcript parse 는 stop-event 가 없던 net-new unbounded I/O (TestContractArch §8.3 / InfraOpArch H2)"
    overflow_contract:  # MANDATORY (InfraOpArch H2)
      - "bounded read (byte cap / line cap) + parse timeout"
      - "overflow / timeout 시 → attribution_confidence: unattributed (block 아님, token/cost = null)"
      - "0 API call 유지 (overflow 시에도)"
    lazy_attribution_recommendation: "SubagentStop = pointer(transcript ref hash) 만 기록, token sum 은 replay/aggregate cold-path 에서 (InfraOpArch H2 권고) — append hot-path 50ms 보호"

  transcript_privacy_hard_invariant:  # T-INFO-5 SecurityArch P0 (NEW) — HARD
    rule: |
      spawn-event row 는 **numeric aggregate + enum + hash 만** 저장한다.
      **transcript content 절대 미저장. transcript_path 값 절대 미저장** (path = session-id 포함 — leak surface).
      derivation fn 은 numeric only 반환 (구조적 mitigation — content/path 가 row 에 도달하는 경로 자체 부재).
      stop-event 는 이 surface 를 마주한 적 없음 (subagent-stop 이 transcript 미read) — spawn-event net-new P0.

  isolation:  # ADR-163 §결정 9 / InfraOpArch §7.4.5
    wrapper_path: "mclayer/plugin-codeforge checkout 의 .claude/ledger/spawn-event.jsonl"
    consumer_path: "각 consumer repo 의 .claude/ledger/spawn-event.jsonl"
    cross_host_leak: "금지 (T-INFO-4 P0). storage_path override 가 wrapper dir 로 escape 금지. cross-host DAP 통합 = ADR-043 §결정 5 Phase 2 deferred"

  block_forbidden_graceful_degradation:  # ADR-115 §결정 2·5 inherit + 6th domain
    rule: "hook layer attribution 이 spawn/stop 을 block 금지. exit 0 invariant"
    degradation_5layer_inherit: "ADR-115 §결정 5 5층 graceful degradation MANDATORY inherit"
    sixth_domain: "**transcript-parse 를 6번째 degradation domain 으로 추가** (InfraOpArch) — parse 실패/timeout/overflow → unattributed + exit 0"
```

## 4. 변경 규칙

- **Allow-list ONLY (v1.x)**: §2 의 19 field 외 새 field 추가 = ADR-043 §결정 2 Amendment 의무 + 본 contract version bump. optional field 추가 = MINOR (ADR-008 §결정 2 — backward-compat, v1.0 reader skip 가능). 필수 field 추가 / field 삭제 / enum 값 제거 = MAJOR (v2.0 BREAKING).
- **free-form string field 도입 금지 (v1.x invariant)**: T-INFO-8 구조적 mitigation 보존. 만약 free-form string field 가 불가피하면 = ADR-043 §결정 3 Deny-list regex 6 pattern 적용 의무 + Amendment. (현 v1.0 = free-form 0건 → Deny-list no-op, 단 **inherit 선언** — defense in depth: 향후 string field 도입 시 자동 적용 대상).
- **enum 값 추가**: `lane_label` / `agent_type` / `event_type` / `attribution_confidence` enum 확장 = additive 면 MINOR (ADR-043 §결정 2 Amendment 동반). enum 값 제거 = MAJOR.
- **storage backend 변경 (JSONL → sqlite)**: ADR-163 §결정 4 amendment 의무 (BREAKING — 단 spawn-event 는 contract=runtime JSONL 일치가 §3 invariant. stop-event sqlite 계약 理想으로 align 하려면 stop-event runtime 도 동반 migration 필요 = 별 Epic).
- **opt-in default 변경 (false → true)**: ADR-043 §결정 1 amendment 의무 (BREAKING — privacy invariant 위반).
- **timestamp 형식**: UTC Z strict (§3). +00:00 / bare datetime 불허 — clarification 변경 = minor commentary.
- **record type 추가 (self-context-v1 등)**: 동일 channel 을 공유하는 별 record type 추가 = **MINOR** (§2 19-field spawn row Allow-list 무변경, discriminator `schema_version` 로 분기 — additive, ADR-008 §결정 2). CFP-2572 v1.0 → v1.1 (§2.1 self-context-v1 6-field record type 추가 — ADR-043 Amendment 3 / ADR-142 §결정 4). self-context record 도 free-form string field 0개 (numeric / enum / hash only) → T-INFO-8 구조적 mitigation 상속, Deny-list no-op inherit.

## 5. Phase 1 / Phase 2 scope

### Phase 1 (CFP-2393 본 PR — doc-only, stop-event 선례 ADR-163 §결정 12)

- 본 schema file 신설 (kind:registry)
- MANIFEST.yaml kind:registry comment line 갱신 (spawn-event 명시 — **entry 미추가**, stop-event 선례)
- playbook §15.1 8번째 channel row + §15.2 4번째 boundary invariant (§14.12 ↔ spawn-event role-separation) + §14.12 "관계" note
- project-config-schema.md `channels.spawn_event: false` 활성 (comment → 정식 schema)
- measurement-channel.md 도메인 doc 갱신 (Phase 2 deferred → landed Tier-3 8th channel)
- codeforge-family.md Open Decisions Pending 갱신 (ADR-112 per-Epic gate)
- ADR-163(measurement) Amendment 1 + ADR-043 Amendment 2

### Phase 2 (별 후속 PR — append/replay/dedup/lint)

- `append_spawn_event.py` 신설 — **O_APPEND per-row** (stop-event runtime read-modify-write 패턴 미복사, H1) + token source 실측·택일 (transcript_path 파싱 vs SDK total_cost_usd) + overflow contract (bounded read + timeout + unattributed) + sha256 actor + transcript content/path 미저장 (T-INFO-5)
- SubagentStop hook 확장 — agent_id/agent_type capture (현 subagent-stop = stop_reason 만 추출, net-new wiring) + lazy attribution(pointer only) 권고
- replay 재구성 script — 기존 JSONL ledger + §14 + §10 read + 시간순(elapsed_seconds keyed) merge. **새 저장계층 미신설**
- **§14 ↔ spawn-event dedup script** (ADR-163 §결정 13 precondition AC)
- lint — kind:registry frontmatter / §1-§4 schema / Allow-list ONLY / attribution_confidence invariant / contract↔runtime parity(§2.4 drift 해소 후 reference pin) / idempotency
- pricing constant table (로컬, 0 API)

ROI gating prerequisite: ADR-163 §결정 11 (post-merge-counters.jsonl 30+ run) — **단 본 Story 는 Epic CFP-2391 directive 가 deferral 을 supersede** (ADR-163 Amendment 1 §근거 ROI gate 처리 참조).

### self-context-v1 record type (CFP-2572 / ADR-043 Amendment 3 — Phase 1 doc-only)

- §2.1 self-context-v1 6-field record type = **allow-list POLICY 편입** (ADR-043 Amendment 3). L7 Orchestrator self-context proxy — 동일 spawn-event.jsonl channel 공유, `schema_version` discriminator 로 19-field spawn row 와 분기.
- **record-only proxy** — `delegation_ratio` / `pre_tokens` 는 lead-self ground-truth 가 아니다 (platform live per-turn self-context surface 부재 P1). 어떤 self-context 판정도 게이트가 아니며 gate/block/deny 를 세우지 않는다 (ADR-142 tier 정직 invariant).
- 실 emission (append/dedup) = Phase 2 (본 §2.1 = POLICY declare, spawn-event-v1 contract bump 시 field-set count reconciliation 확정 — ADR-043 Amendment 3 §근거).

## 6. Cross-references

- **ADR-163** (measurement channel architecture) — §결정 1 boundary 표 8th channel(Amendment 1) / §결정 3 보류 해제(Amendment 1) / §결정 13 amendment 의무 이행 / §결정 8 0-API·50ms / §결정 9 isolation
- **ADR-043** (telemetry privacy policy) — §결정 1 opt-in default false / §결정 2 Allow-list(Amendment 2) / §결정 3 Deny-list inherit / T-INFO-5 transcript hard invariant + T-INFO-7 sha256 (Amendment 2)
- **stop-event-v1** — sibling Tier-3 ledger. **단 structural model 아님** (contract↔runtime drift 회피 — Change Plan §2.4 / §7). spawn-event 는 fix-event-v1 동형
- **fix-event-v1** — structural model (kind:registry §1/§2/§3/§4 skeleton)
- **playbook §15** — 8-channel observability boundary table + §15.2 4번째 boundary invariant
- **playbook §14.12** — Spawn-level token telemetry mini-table (Tier-1 quota-only — role separation, §1.1)
- **ADR-031** — §14 Lane Evidence (lane-coarse) ↔ spawn-event (per-agent) boundary + dedup
- **ADR-119** — attribution_confidence unattributed default 의 검증-후-단언 근거 + §2.1 self-context proxy hollow-gate 정직 표기
- **ADR-142** §결정 4 — L7 Orchestrator self-context proxy record type (§2.1 self-context-v1) carrier. return-envelope-v1 (§결정 3) sibling
- **ADR-043 Amendment 3** — self-context-v1 6-field allow-list 편입 + inherit 선언 (opt-in default-false / Deny-list / T-INFO-5 / T-INFO-7) + record-only posture
- **oh-my-claudecode (MIT)** — per-agent registry + replay event 종류 + 경과초 keyed 차용 (frontmatter attribution SSOT)
