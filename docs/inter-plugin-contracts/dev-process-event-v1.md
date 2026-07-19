---
kind: registry
registry: dev-process-event
version: "1.0"
schema_version: dev-process-event-v1
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/dev-process-event-v1.md
date: 2026-07-15
authors:
  - DataEngineerAgent (CFP-2687 Phase 2 — Epic #2686 Story A. dev-process-event-v1 신설 carrier. ADR-155 설계 SSOT 구현. ADR-163 Amendment 2 + ADR-043 Amendment 4 동반)
related_adrs:
  - ADR-155  # dev-process observability substrate — 본 계약의 설계 SSOT (9 결정)
  - ADR-163  # measurement channel architecture — 9th Tier-3 channel (Amendment 2) + warm-tier + 5th boundary invariant
  - ADR-043  # telemetry privacy policy — redaction 계약 상속·확장 (Amendment 4: always-on 비대칭 + deny 6→7 + redacted-blob T-INFO-5)
  - ADR-104  # operational-phase definition — dev-process ⊥ operational-phase disjoint axis (scope-guard)
  - ADR-115  # runtime hook enforcement — record-only·non-blocking·exit0 상속
  - ADR-064  # evidence-gated symmetric ratchet — consumer opt-in-false 무약화 (α 비대칭)
  - ADR-031  # lane-spawn evidence — lane-coarse ↔ dev-process 상관 boundary
  - ADR-038  # progress visualization — lane_transition 최소 6-point 근거
  - ADR-039  # subagent default — Orchestrator-owned delegate writer monopoly
  - ADR-078  # living architecture doc — codeforge-family.md 갱신 의무
  - ADR-119  # research-before-claims — 정직 천장 (resource-safety / mining honest-degrade)
related_files:
  - docs/inter-plugin-contracts/stop-event-v1.md   # new-sibling (stop 이벤트 단독 소유)
  - docs/inter-plugin-contracts/spawn-event-v1.md   # new-sibling (per-agent spawn accounting 단독 소유)
  - docs/inter-plugin-contracts/fix-event-v1.md      # new-sibling (§10 FIX Ledger row monopoly)
  - docs/inter-plugin-contracts/review-verdict-v4.md # new-sibling (verdict 의미론 소유)
  - docs/inter-plugin-contracts/MANIFEST.yaml         # kind:registry comment (entry 미추가 — stop/spawn 선례)
  - docs/orchestrator-playbook.md                     # §15.1 8→9 channel boundary + §15.2 5th invariant (co-land)
  - scripts/lib/append_dev_process_event.py           # index append primitive — _ROW_KEYS = 본 §2 EXTERNAL code anchor (parity)
  - scripts/lib/query_dev_process_event.py            # mining/query port (raw typed rows + blob deref)
  - scripts/lib/dev_process_blob_store.py             # evidence-blob-store (capture_blob / deref_blob — sibling)
  - scripts/lib/redact_dev_process_content.py         # capture-time redaction (redact — sibling)
amendment_log: []
attribution:
  external_soft_align: "OpenTelemetry Logs Data Model / CloudEvents / ECS (typed append-only event) · W3C Trace Context (correlation ID) · git blob/IPFS CID (content-addressed blob) · gitleaks/crypto-shredding (redaction) · Elasticsearch ILM hot/warm/cold (retention). 전부 soft-align(map only) — 외부 OTel GenAI semconv 는 Development/unstable 이라 hard-freeze 대상 아님 (Story §6.4 R5). Sources = Story CFP-2687 §6.5."
---

# dev-process-event v1

> **정체 (AC-1)**: 본 계약 = codeforge 10-lane **개발 과정(dev-process)** 관측의 **증거 substrate + 계약**이다. 오직 A 범위 — **evidence substrate + contract ONLY**. **B(dev-process 지표 산출 알고리즘 — #2688)·C(self-gate verdict 판정 로직 — #2689)는 본 계약 범위 밖(NOT B metrics-aggregation, NOT C gate/verdict logic)**. 본 계약은 "무엇을 어떻게 안정적으로 남기나"만 정의하고, "그 값으로 무엇을 계산/판정하나"는 정의하지 않는다.
>
> **설계 SSOT = [ADR-155](../../archive/adr/ADR-155-dev-process-observability-substrate.md)** (9 결정) + change-plan `2026-07-15-cfp-2687-dev-process-observability-substrate.md`. 본 파일 = 그 설계의 Phase 2 실 계약 파일.
>
> **structural model**: kind:registry (`## 1. 목적` / `## 2. Schema` / `## 3. 항목` / `## 4. 변경 규칙`). stop/spawn-event 선례. **stop-event runtime 은 모델로 삼지 않는다** — stop-event 의 contract↔runtime 3-way drift(18↔5 field / sqlite↔jsonl / UTC↔KST)를 복사하지 않기 위함(§12 AC-23 honesty).

## 1. 목적

`docs/inter-plugin-contracts/dev-process-event-v1.md` = codeforge 관측성 스택 **Tier-3(persistent measurement) 의 9번째 channel**(ADR-163 §결정 1, Amendment 2 동반). lane 전이·프롬프트/입력·도구호출·verdict·diff·결점 findings·FIX 루프 전이·최종 산출물을 **하나의 typed append-only stream** 으로 통합한 evidence 계약이다.

기존 8 channel(stop/spawn 포함)은 전부 **content-blind**(numeric/enum/hash-only) — rich semantic content 를 흡수할 경로가 0 이므로 **통합 재해석 불가, 신설**(INV-4, ADR-155 §결정 1). new-sibling — 기존 계약 supersede 0.

### 1.1 2계층 구조 (INV-4 — rich-content ⊥ allow-list 화해, AC-7/15/18)

기존 stop/spawn-event 는 **allow-list-ONLY + anti-content**(transcript content·path 미저장 = T-INFO-5/8)이다. rich content 를 기존 row 에 필드 추가로 수용하면 v2.0 breaking + T-INFO-5 위반. 화해 = **2계층 분리**:

| tier | 표면 | 저장 원칙 |
|---|---|---|
| **index tier**(본 §2 이벤트 행) | allow-list-clean | enum / numeric / hash / 상관 ID / blob-ref / emit_source **only**. free-form content 본문 직접 저장 **0**. 기존 anti-content invariant(T-INFO-5/8) **무손상**. |
| **evidence-blob-store**(§6) | redacted content-addressed blob | capture-time redaction **후** content-addressed blob 저장. index 는 blob 의 hash(`blob_ref`) **참조만** 보유. free-form content 저장은 이 redacted-blob 표면으로만 허용(AC-15). |

**상충 지점 명시(AC-18)**: index=content-free ↔ Story 가 요구하는 rich content(프롬프트·diff·findings·산출물)는 index row 스키마로는 수용 불가 — 이 긴장을 2계층으로 화해한다(index 는 여전히 content-free, blob 은 redaction-후 산물 → no-conflict).

## 2. Schema (index tier — 18 필드 Allow-list ONLY)

각 index-tier row = **18 필드 Allow-list**(아래 표 순서·멤버 = §4 변경 규칙 SSOT). **free-form string content field 0개** — T-DPE-3/T-INFO-8 구조적 차단(rich content 는 §6 redacted-blob 표면으로만). 필드 적용성(applicability)은 event_type 별로 다르다(nullable 축 참조).

| # | 필드 | 타입 | nullable | 적용 event_type | 설명 |
|---|---|---|---|---|---|
| 1 | `event_id` | sha256 string | required | 전체 | idempotency invariant — **deterministic** `sha256(schema_version‖event_type‖emit_source‖story_key‖lane_label‖consumer_scope‖defect_id‖fix_id‖blob_ref‖seq)`. **timestamp 산입 제외**(재시도 멱등). random UUID 금지(§11.6). read-time dedup key |
| 2 | `schema_version` | const string | required | 전체 | `dev-process-event-v1` 고정 — 다중 계약 stream 판별 discriminator |
| 3 | `event_type` | enum (CLOSED 8) | required | 전체 | §3 8종 closed enum |
| 4 | `emit_source` | enum (CLOSED 2) | required | 전체 | `{hook, agent}` — capture 경로 discriminator(§결정 4, single-stream JOIN 보존) |
| 5 | `timestamp_utc` | ISO8601 UTC Z (ms) | required | 전체 | **UTC Z strict 저장, millisecond precision**(`2026-07-15T14:22:33.481Z`, `%Y-%m-%dT%H:%M:%S.%fZ` 3-digit). +00:00 / bare datetime 불허. KST 표시(ADR-079). monotonic 필요 시 **MAX(prev+1ms)**(change-plan §7.4 clock / Story §7.3 design literal). timezone 축(UTC 저장)은 stop=KST vs spawn=UTC 괴리 봉인, precision 축(ms)은 monotonic +1ms directive 지원 — 별개 축 |
| 6 | `story_key` | string | required | 전체 | 상관 ID **freeze** — e.g. `CFP-2687`. Public non-sensitive. SubagentStop source 부재 시 `""`(§edge) |
| 7 | `lane_label` | enum | required | 전체 | 상관 ID **freeze** — 11값(10 lane + `없음`, label-registry-v2 정합). closed-set. 미매칭 → `없음` |
| 8 | `consumer_scope` | enum (CLOSED 2) | required | 전체 | `{wrapper, consumer}` — α 비대칭 isolation marker(ADR-163 §결정 9) |
| 9 | `defect_id` | sha256 string \| null | nullable | defect_finding / fix_transition | 상관 ID **freeze** — `sha256(family‖type‖normalized-location)`, summary **제외**(wording-drift caveat). 그 외 event = null |
| 10 | `fix_id` | string \| null | nullable | fix_transition | 상관 ID **freeze** — per-defect 대응 **시도** 단위(lane 재진입 단위 아님). 1 §10 FIX row ↔ 1..N `fix_id`. 그 외 = null |
| 11 | `blob_ref` | sha256 string \| null | nullable | rich payload 보유 event | evidence-blob-store 참조 = `sha256(REDACTED bytes)` **NEVER raw**(INV-8a). bare 64-hex. blob 부재 = null |
| 12 | `redaction_applied` | bool | required | 전체 | audit — capture-time redaction 발동 여부. default false |
| 13 | `redaction_count` | int | required | 전체 | audit — 마스킹 발동 횟수. default 0 |
| 14 | `redaction_rules_fired` | enum array (CLOSED — §8.2) | required | 전체 | audit — 발동 규칙명 array. 값 어휘 SSOT = `redact_dev_process_content.RULE_NAMES`(§8.2). **매칭 secret 원문/hash 절대 미기록**(T-DPE-8). default `[]` |
| 15 | `defect_family` | enum (CLOSED 7) \| null | nullable | defect_finding / fix_transition | taxonomy — §5 CLOSED-7. 그 외 = null |
| 16 | `defect_type` | string (SEMI-OPEN) \| null | nullable | defect_finding / fix_transition | taxonomy — review-verdict-v4 type-derived ∪ `unknown-type`(fallback). 그 외 = null |
| 17 | `time_to_detection` | number \| `"unattributed"` \| null | nullable | defect_finding | taxonomy — **DERIVED measure**(ordinal lane-distance ∨ ts-delta). 도입점 불명 = `unattributed`. 그 외 = null |
| 18 | `detecting_lane` | enum (lane_label) \| null | nullable | defect_finding | taxonomy — 결점 검출 lane(lane_label enum, CLOSED). 그 외 = null |

> **Phase 2 = doc↔code parity SSOT**: 위 18 필드 순서·멤버 = `scripts/lib/append_dev_process_event.py` 의 `_ROW_KEYS`(Python-hardcoded EXTERNAL code anchor)와 **byte-consistent** 해야 한다. wave-2 parity self-test = 본 §2 table(동적 파싱) vs `_ROW_KEYS`(동적 파싱) 대조 — **born-drift = FAIL**(doc vs code, `check_self_context_telemetry_allowlist.py` S1 external-anchor 구조 선례).

### 2.1 declared allow-list (permitted index field names)

index tier 에 저장 가능한 필드명 allow-list(닫힌 목록). **§2 필드 ⊆ 본 allow-list**(wave-2 allow-list lint self-applies → born-green 의무). 아래 밖의 필드명은 index row 에 유입 금지 — free-form content 유입의 구조적 차단선:

```
event_id · schema_version · event_type · emit_source · timestamp_utc ·
story_key · lane_label · consumer_scope · defect_id · fix_id · blob_ref ·
redaction_applied · redaction_count · redaction_rules_fired ·
defect_family · defect_type · time_to_detection · detecting_lane
```

각 원소의 값 유형은 enum / numeric / sha256-hash / 상관 ID / blob-ref / emit_source discriminator 중 하나로만 제한된다(free-form content = 0, AC-7). append primitive 는 이 allow-list 밖 kwarg 를 **drop** 한다(content-blind — `append_dev_process_event.build_row`).

## 3. 항목 — event-type / noise / capture

### 3.1 event_type closed enum (8종 — AC-2/6)

```yaml
event_type:
  type: enum
  required: true
  closed: true      # 8 확정 — 9번째 추가 = §4 amendment 의무 (ADR-163 §결정 2)
  values:
    - lane_transition   # lane 전이 (agent-emit)
    - prompt_input      # 프롬프트/입력 (hook)
    - tool_call         # 도구호출 (hook: PreToolUse + PostToolUse net-new)
    - verdict           # 리뷰 verdict (agent-emit)
    - diff              # diff (hook: PostToolUse net-new)
    - defect_finding    # 결점 findings (agent-emit)
    - fix_transition    # FIX 루프 전이 (agent-emit, §10 monopoly)
    - final_artifact    # 최종 산출물 (agent-emit)
```

**lane_transition 최소 포함(AC-6)**: ADR-038 6-point lane 전이 **이상** — 진입 / PASS / FIX 검출 / 원인 판정 / 재진입 / 완료 6종을 최소 커버(그 이상 세분 허용, 미만 불가).

### 3.2 noise-discard closed list (5종 — AC-3)

계약이 폐기하는 noise = **닫힌 목록 5종**. "거의 전부 스크랩"의 compliance 폭주(기여자 프롬프트/로컬 경로/제3자 코드 무차별 캡처)를 구조적으로 차단한다(진단가치 0 = discard):

```yaml
noise_discard:
  closed: true      # 5 확정 — 6번째 추가 = §4 amendment 의무
  values:
    - progress_spinner            # 진행 스피너
    - streaming_token_duplication # 스트리밍 토큰 중복
    - dependency_install_log      # 의존성 설치 로그
    - unchanged_file_list         # 무변경 파일목록
    - low_value_verbose_output    # 진단가치 없는 verbose 출력
```

> **noise false-negative 주의(§edge)**: tool-call 결과 전부 noise 처리 시 diff 실패 원인 소실 / diff 0-byte·파일 0 을 noise 처리 시 "수정 시도했으나 무변경" 사실 소실 → 위 5종 **외** 는 discard 금지.

### 3.3 capture 경로 이원화 (emit_source discriminator — §결정 4)

| event_type | 경로 | Port | emit_source |
|---|---|---|---|
| prompt_input | hook (PreToolUse Agent) | A (hook-adapter) | `hook` |
| tool_call | hook (PreToolUse + PostToolUse net-new) | A | `hook` |
| diff | hook (PostToolUse net-new) | A | `hook` |
| lane_transition | agent-emit (Orchestrator) | B (agent-emit) | `agent` |
| verdict | agent-emit (review lane) | B | `agent` |
| defect_finding | agent-emit (review lane) | B | `agent` |
| fix_transition | agent-emit (Orchestrator §10 monopoly) | B | `agent` |
| final_artifact | agent-emit (lane) | B | `agent` |

- **single-stream JOIN 보존**: `emit_source` enum discriminator 로 capture path 를 정직 구분하되 stream 은 하나(2-channel 물리 분리 기각 — INV-3 JOIN 파괴 회피).
- **hook NON-ambient**: hook 은 lane ambient 를 알 수 없다 — `agent_type→lane` map(semi-open, 미등재 → `없음` fallback) 또는 agent-emit 직접 주입. Stop hook 에 lane ambient 기대 금지(dependency direction: hook→env only). 둘 다 부재 → lane=`없음` + vacuous status(consistent 위장 금지).

## 4. 변경 규칙

- **Allow-list ONLY (v1.x)**: §2 18 필드 외 새 필드 추가 = ADR-043 §결정 2 Amendment 의무 + 본 계약 version bump. optional field 추가 = MINOR(backward-compat, ADR-008 §결정 2). 필수 field 추가 / field 삭제 / enum 값 제거 = MAJOR(v2.0 BREAKING).
- **free-form string content field 도입 금지 (v1.x invariant)**: T-DPE-3/T-INFO-8 구조적 mitigation 보존. rich content 는 §6 redacted-blob 표면으로만.
- **event_type enum(8) / noise-discard(5) 변경**: additive = MINOR(Amendment 동반) / 값 제거 = MAJOR.
- **4 상관 ID freeze 변경**: 이름·scope·생성시점·안정성 규칙 변경 = **계약 amendment 의무**(B·C 병렬 전제 — freeze).
- **defect taxonomy 축 종류(closed/semi-open/derived) 변경**: family/lane closed-set 확장 = MINOR / type semi-open→closed 승격 = MAJOR / ttd derived→enum 승격 = MAJOR.
- **`_ROW_KEYS` parity**: §2 필드 순서·멤버는 `append_dev_process_event._ROW_KEYS` 와 항상 일치(born-drift = FAIL). 한쪽 변경 = 양쪽 동반 + amendment.
- **opt-in / always-on 정책 변경**: α 비대칭(wrapper always-on / consumer opt-in-false) 약화 = ADR-043/ADR-064 amendment 의무(BREAKING — privacy invariant 위반).
- **retention tier / blob 정량**: 수치(proposal)는 empirical 조정 = minor commentary. tier 개수·spill 방향 변경 = ADR-163 §결정 4 amendment.

## 5. 상관 ID freeze + 결점 taxonomy (B·C 공유 — AC-4/5)

### 5.1 4 상관 ID freeze 표 (FREEZE — 변경 = 계약 amendment 의무)

**B(집계 #2688)·C(판정 #2689) 병렬 전제** — 4종 ID 의 이름·scope·생성시점·안정성을 Phase 1 에서 freeze. **변경 시 본 계약 amendment 의무**(미확정 병렬 = 백필 부채):

| ID | 신규? | scope | 생성 시점 | 안정성 | 공유 |
|---|---|---|---|---|---|
| `story_key` | 재사용 | Story 전체 | Story 시작 (branch `cfp-NNN` derivable) | immutable | B·C freeze |
| `lane_label` | 재사용 | lane 전이 단위 | lane 진입 | label-registry enum. FIX 재진입 시 동일 label(구분 = `fix_id`) | B·C freeze |
| `defect_id` | **신규** | cross-lane 결점 identity | 최초 findings emit 시 | content-addressed `sha256(family‖type‖normalized-location)`, **summary 제외**(wording-drift caveat — 결정론 over-claim 금지) | B·C freeze |
| `fix_id` | **신규** | per-defect 대응 **시도** 단위 (lane 재진입 단위 아님) | FIX 개시 시 (agent-emit) | §10 Iter monopoly 불변 — 1 §10 row ↔ 1..N `fix_id` | B·C freeze |

`finding_id` = subordinate(anchor_id = verdict-scope 재사용). `defect_id ← finding_id` = N:1. D4 재발 = 동일 `defect_id` 에 distinct 검출.

### 5.2 결점 taxonomy 4-tuple (★정직 — 전부 closed enum 아님, over-claim 금지)

| 축 | 종류 | 값 |
|---|---|---|
| `defect_family` | **CLOSED 7** | correctness / security / performance / design-boundary / test-gap / doc-integrity / process-discipline |
| `defect_type` | **SEMI-OPEN** | review-verdict-v4 type-derived ∪ `unknown-type`(미분류 fallback) |
| `time_to_detection` | **DERIVED measure (enum 아님)** | ordinal — lane-distance ∨ ts-delta. 도입점 불명 = `unattributed` |
| `detecting_lane` | **CLOSED** | lane_label enum |

> **정직 천장(AC-4/5)**: "4-tuple 전부 closed enum" 은 **over-claim** — freeze 표기는 **family/lane = closed, type = semi-open, ttd = derived measure** 로 정확히 구분한다. `defect_type` 는 semi-open(미등재 값을 reject 하지 않고 `unknown-type` 로 흡수), `time_to_detection` 은 enum 이 아닌 파생 측정치. `defect_id` 가 summary 를 제외하는 이유 = 동일 결점의 wording drift 가 identity 를 흔들지 않게 하기 위함(결정론 over-claim 방지).

## 6. evidence-blob-store — content-addressed + redaction-선행 (AC-8/9)

큰 payload = content-addressed blob 참조. index 는 blob 의 hash(`blob_ref`)만 보유. blob store = 기존 계약에 없던 **신규 비밀 표면** → 자체 redaction·보존·참조 규약(§7/§8).

### 6.1 blob 규칙 (정량 — 수치 PROPOSAL, empirical Phase 2 defer)

| 항목 | 값 | 확정도 |
|---|---|---|
| hash 알고리즘 | **sha256** | 확정 |
| `blob_ref` 형식 | bare 64-hex lowercase sha256(REDACTED bytes) | 확정 |
| 크기 캡 임계 | index row inline 금지 임계 = **4 KB (proposal)** — 초과 payload 는 blob 로 spill | **PROPOSAL** |
| blob byte-cap | 단일 blob 상한 = **1 MB (proposal)**, 초과 = truncate + audit marker | **PROPOSAL** |
| spill 목적지 | index inline → evidence-blob-store loose blob(hot) → warm pack → cold(§7 tier→tier) | 방향 확정 / 수치 PROPOSAL |

> **수치 정직(ADR-119)**: 4 KB / 1 MB 등은 **proposal** — lock-in 금지, empirical 조정 = Phase 2 defer. "이 임계가 최적" 주장 안 함.

### 6.2 INV-8a / INV-8b (P0, 비협상 — AC-12 normative)

- **INV-8a (hash-over-redacted)**: `redact(in-memory, 원본 disk 미접촉)` → `blob_ref = sha256(REDACTED bytes)` **NEVER raw** → blob write(redacted, single). hash-over-unredacted 는 index 가 content-free 여도 `blob_ref` 가 **secret confirmation oracle**(후보 secret 를 sha256 해 blob_ref 대조 — T-DPE-2 P0) → hash-over-redacted 가 봉인.
- **INV-8b (blob-before-index)**: blob write → **THEN** index row(blob_ref 참조). 역순 = dangling evidence chain(T-DPE-5 P0 / AC-22).

## 7. retention 3-tier + AC-10∧AC-25 화해 (AC-25)

dev-process-channel-scoped 3-tier(ADR-163 §결정 4 hot+cold 2-tier 를 본 channel 에 한해 3-tier 확장 — Amendment 2):

| tier | 저장형태 | 조회 latency (expectation) | 보존 (expectation) | spill 전이 |
|---|---|---|---|---|
| **hot** | 구조화 JSONL index + loose blob | **ms** | 7–30d (proposal) | `age > hot_days` ∨ `blob-dir > cap` → warm |
| **warm** | 압축 pack + gz (index 무압축 유지) | **10s–100s ms** | ~90d (proposal) | `age > warm_days` → cold |
| **cold** | 아카이브 | **s** | policy-bound → evict + tombstone | — |

**spill 방향 = strict `hot → warm → cold`** (역방향/skip 금지). 수치(7–30d/90d/latency) = **PROPOSAL**(empirical Phase 2 defer, lock-in 금지 — ADR-119).

### 7.1 AC-10(append-only) ∧ AC-25(cold GC/압축) 화해 (latent contradiction 해소)

naive 구현 시 cold blob 삭제 → index `blob_ref` dangling. 화해 2축:

1. **tombstone**: cold blob 물리 삭제 시 index `blob_ref` **불변 유지**(참조 안 지움). append-only `blob-evicted` event/sidecar 가 `evicted_at`+tier 기록 → reader 는 silent 404 아닌 **eviction 증거**에 도달.
2. **content-preserving hash-verified transform**: warm/cold 압축은 물리 rewrite 이나 append-only 는 **논리 evidence stream** 에 적용 — decompress 시 byte-identical redacted 복원, `hash(decompressed) == blob_ref` **재검증 의무**, index row **절대 rewrite 안 함**. 불변 anchor = `blob_ref` 가 전 tier 관통(git loose→pack 동형).

> "in-place edit 금지"(AC-10) 는 **논리 스트림**(index row + blob_ref 불변)에 적용 — 물리 압축/eviction 은 hash-verified transform + tombstone 으로 append-only invariant 를 보존한다. 정정 방식 = 새 이벤트/sidecar 추가(overwrite 아님).

## 8. redaction + audit (write-time ONLY — AC-12/13/14)

### 8.1 redaction 경로 (write-time, 원본 비저장 — AC-12)

- **write-time(capture-time) ONLY** — **read-time redaction 은 계약 책임 아님**(reader 는 이미 redacted blob 만 본다).
- **원본 NOT stored** — redaction 이 blob write 에 **선행**(redaction precedes blob write). 원본 disk 미접촉(in-memory redact → hash → write, INV-8a).
- capture-time redaction 은 **wrapper always-on / consumer opt-in 두 scope 모두 선행**(§10 α 비대칭 — always-on 이 redaction 을 우회하지 못한다, INV-8).
- redaction 실 함수 = sibling `redact_dev_process_content.redact(raw) -> (redacted, audit)`(BlobDev 소유). 본 계약은 정책·형식만 정의.

### 8.2 deny-list + patterns (AC-13 — ADR-043 6→7 inherit)

토큰·키·쿠키·Authorization + **절대/home-prefixed 파일 경로** 를 마스킹, env dump·자격증명 subprocess 출력을 **기본 제외**:

| 규칙명 (`redaction_rules_fired` enum) | 대상 | 계보 |
|---|---|---|
| `api_key_credential` | API key / secret / token / password / bearer | ADR-043 §결정 3 상속 |
| `github_pat` | GitHub classic PAT (`ghp_…`) | 상속 |
| `github_fine_grained_pat` | GitHub fine-grained PAT (`github_pat_…`) | 상속 |
| `kr_rrn` | 한국 주민등록번호 13-digit | 상속 |
| `email` | RFC-5321 email | 상속 |
| `hex_high_entropy` | hash / cert fingerprint (hex≥32) | 상속 |
| `abs_or_home_path` | **절대/home-prefixed 경로**(`/home`·`/Users`·`/root`·Windows `C:\`·git-bash `/c/`) | **7번째(Amd4 신규)** — repo-relative 경로는 **보존**(diff 진단 신호 = public, 무차별 redact 시 noise false-negative) |
| `authorization_header` | Authorization 헤더 scheme+토큰 | Amd4 §D net-new 표면 |
| `cookie_header` | Cookie / Set-Cookie 헤더 | Amd4 §D |
| `cloud_key` | AWS/GCP/Slack 구조 키 + entropy-gated generic (gitleaks 보강) | Amd4 §D |
| `private_key_block` | PEM `PRIVATE KEY` block | Amd4 §D |
| `session_id` | session_id 대입 → sha256(truncate) 치환 (**raw 저장 금지** — T-DPE-6, `append_stop_event.py:73` bug 미복사) | Amd4 §D |
| `env_dump_excluded` | env dump 통째 제외 (capture-exclusion) | Amd4 §D |
| `credential_subprocess_excluded` | 자격증명 subprocess 출력 통째 제외 (capture-exclusion) | Amd4 §D |

> **SSOT (audit rule 어휘)**: `redaction_rules_fired` 값 어휘 = **`scripts/lib/redact_dev_process_content.RULE_NAMES`** — audit dict 를 emit 하는 redaction 모듈(producer)이 rule 어휘를 단일 소유한다. append primitive(`append_dev_process_event._REDACTION_RULES`)는 이 producer 어휘를 **import 로 gate**(복붙 drift 차단 — ADR-140; 미등재 이름은 index 유입 전 drop = allow-list-clean). 앞 6종 = ADR-043 §결정 3 상속 / 7번째 경로 + 후속 net-new(header·cloud·private-key·session·capture-exclusion) = Amendment 4 §D·§8.2 표면.
> **honest-ceiling(T-DPE-4)**: deny-list = **완전커버 아님**. 미커버 novel secret(신규 API key·비정형 자격증명)이 통과할 수 있다 — allow-list-clean index + per-event tier(prompt=최고) + entropy 임계(gitleaks) 심층방어이나 **residual 존재**를 명시(완전차단 over-claim 금지).

### 8.3 audit (AC-14 — mandatory-on-fire)

| 필드 | 타입 | 규칙 |
|---|---|---|
| `redaction_applied` | bool | redaction 발동 여부 |
| `redaction_count` | int | 마스킹 발동 횟수 |
| `redaction_rules_fired` | enum array (CLOSED — §8.2 SSOT) | 발동 규칙명만 — 값 어휘 = `redact_dev_process_content.RULE_NAMES`(§8.2 14종) |

> **T-DPE-8 (oracle 역전 차단, 비협상)**: audit 는 **규칙명 + 횟수만**. **매칭 secret 원문/hash 절대 미기록** — audit log 가 secret confirmation oracle 로 역전되는 것을 차단. `redaction_rules_fired` 는 §8.2 SSOT closed enum 밖 값을 drop(allow-list-clean).

### 8.4 resource-safety HONEST-CEILING (★ CFP-2646/2635 선례 — 무증거 단정 금지)

- redaction/capture hot-path 에 대해 **"ReDoS-safe / catastrophic-backtracking 0 / DoS-proof" 단정 금지**.
- 명시 가능한 것 = **born-safe bound 만**: byte-cap + line-cap + parse-timeout. capture 실패 = non-blocking exit 0(ADR-115). backpressure = size-cap + spill + disable.
- 정직 천장: **"bounded degradation, 임의입력 무해 아님"**. **proof = Phase 2 SecurityTest**(execution-backed). 무증거 안전 주장은 리뷰 반증 대상(self-ref 재발 방지).

## 9. mining/query 진입점 (AC-16/17)

| 항목 | 값 |
|---|---|
| 이름 | `scripts/lib/query_dev_process_event.py` — `query(**filters) -> list[dict]` |
| 입력 단위 | filter params — `story_key` / `lane_label` / `defect_id` / `fix_id` / `event_type` / time-window(`since`/`until`) |
| 반환 단위 | **raw typed event rows**(+ optional blob deref via `dev_process_blob_store.deref_blob`) |
| dedup | read-time dedup(`event_id`) — port 소유 |

- **AC-17 범위 배제**: 반환은 **집계 metric(B) 도 verdict 판정(C) 도 아니다** — raw typed rows 만. "지표 집계 방식"·"게이트 판정 규칙"을 포함하지 않는다. B(지표)·C(verdict)는 disjoint consumer(port 하류 무의존, storage 포맷 계약 표면 비노출 — reader port 뒤 격리).
- **mining honest-degrade(ADR-119)**: exact-count 주장 금지 — `rows_total`/`rows_deduped`/`duplicates_collapsed` 를 **관측치**로 emit(guaranteed-unique 아님). JSONL append-only 는 write-time UNIQUE 부재.

## 10. writer 권한 + telemetry 활성 정책

### 10.1 writer 권한 정합 표 (신규 ↔ 기존 — AC-20)

| 축 | 기존 (stop/spawn-event) | dev-process-event (신규) | 정합 |
|---|---|---|---|
| writer | Orchestrator-owned delegate subagent monopoly (ADR-039 §결정 3) | 동일 — Orchestrator-owned delegate writer (agent-emit) + hook-adapter(hook path) | **상속** |
| lane plugin 임의 write | policy_violation (defect) | 동일 | **상속** |
| record-only | hook_decision=record-only (block 금지) | 동일 (capture 는 판정 세우지 않음) | **상속** |
| non-blocking | 어떤 실패도 exit 0 (ADR-115) | 동일 — append 실패 = graceful degrade + return None, caller exit-0 | **상속** |
| graceful degradation | 5층 (ADR-115 §결정 5) | 상속 + capture-parse 6번째 domain | **상속·확장** |
| 0 API call | local I/O only | 동일 (blob=host-local, cross-host leak 금지) | **상속** |

### 10.2 telemetry 활성 비대칭 (α — AC-19)

- **wrapper-self dogfood scope = always-on** — codeforge family 자기 개발 계측이 Story 목적. always-on = **checkout-identity 파생**(user-settable bool 아님, T-DPE-9).
- **consumer 배포 scope = opt-in default-false** — consumer overlay extend-only(ADR-064 §결정 7), privacy invariant **무약화**. consumer floor 하방 override 불가.
- **두 scope 모두 capture-time redaction 선행**(§8.1 INV-8) — always-on 이더라도 redaction 우회 불가.
- **활성 gate 위치**: 활성 판정 + redact→capture_blob→append_event(INV-8b) orchestration 은 **HOOK/emit 계층**(HookDev, wave 2) 소관. index append primitive 는 gate-free mechanism(계약과 emit 계층이 정책을 강제).

## 11. 관계 매트릭스 (new-sibling — AC-11, normative non-overlap)

dev-process-event-v1 ↔ 기존 계약 = **supersede 아님, new-sibling**. event-ownership 경계 = **normative**(SoT 이중화 §5.4 차단):

| 기존 계약 | 관계 | event-ownership 경계 (normative) |
|---|---|---|
| **stop-event-v1** | new-sibling | stop 이벤트 accounting = stop-event-v1 **단독 소유**. dev-process 는 re-record 안 함 — `event_id` 상관 JOIN(cross-read 허용, payload 복제 금지) |
| **spawn-event-v1** | new-sibling | per-agent spawn token/cost = spawn-event-v1 **단독 소유**. dev-process lane 전이 이벤트는 spawn accounting 복제 안 함, `event_id` JOIN |
| **fix-event-v1 (§10 FIX Ledger)** | new-sibling | §10 FIX row append = Orchestrator monopoly 불변. dev-process `fix_id` FIX-전이 이벤트는 §10 accounting **재기록 안 함** — 1 §10 row ↔ 1..N `fix_id` 상관만 |
| **review-verdict-v4 / *-output-v1** | new-sibling | verdict/산출물 요약 accounting = 각 output 계약 소유. dev-process verdict 이벤트는 **semantic-evidence-aggregation**(어떤 verdict 가 났나 참조)이지 verdict 의미론 정의(C scope) 아님 |

> **5th boundary invariant (ADR-163 §15.2 amendment)**: dev-process-event = **semantic-evidence-aggregation** — 상관 ID cross-read(JOIN) **허용** / accounting payload re-record **금지**. 동일 의미를 두 channel 이 각자 기록하는 SoT 이중화를 구조적으로 차단.

## 12. 정직성 (honesty — AC-23/24)

### 12.1 기존 계약↔구현 드리프트 = FACT (AC-23)

- **stop-event-v1 drift 사실 기록**: 계약 **18-field sqlite@`.claude-work/measurement` / UTC** ↔ 실 구현 **5-field JSONL@`.claude/ledger` / KST** 드리프트가 **실재**한다(FACT).
- 본 신규 계약은 이 드리프트를 **자동 해소한다고 주장하지 않는다** — new-sibling 은 현실 위에 얹힌다. 기존 5-field 런타임을 즉시 승격하지 않는다.

### 12.2 D3/D4/D5 gap = motivation only (AC-24)

- D3(통합 계약 부재)·D4(cross-lane 결점 identity 부재)·D5(상관 ID freeze 부재) gap 은 **"왜 이 계약이 필요한가"의 근거로만** 사용.
- Phase 1(설계)·본 계약(Phase 2 landing) **만으로 gap 이 운영상 닫힌다고 선언하지 않는다** — **활성화 + 통합 + freeze** 로만 서술. landing ≠ activation(계약이 존재해도 실 capture 배선·활성은 별 wave).

### 12.3 scope-guard ⊥ ADR-104 (dev-process ⊥ operational-phase)

본 substrate 는 ADR-104 §결정 4 wrapper-N/A 를 건드리지도 약화하지도 않는다 — wrapper-N/A 는 **운영(production) phase 측정** 한정, dev-process observability(개발 과정 관측)는 **disjoint axis**. homonym 주의: `measurement-channel.md` 2 파일(operational-phase vs orchestrator-discipline)은 별개 도메인.

## 13. Phase 1 / Phase 2 scope

### Phase 1 (설계 — CFP-2687 Phase 1 PR, 완료)
- ADR-155 + change-plan + Story §3/§7 + `docs/architecture/codeforge-family.md` + ADR-163 Amd2 + ADR-043 Amd4.

### Phase 2 (본 계약 파일 + 실배선 — CFP-2687 Phase 2 PR)
- 본 `dev-process-event-v1.md` 계약 파일(kind:registry) + MANIFEST.yaml kind:registry comment(entry 미추가 — stop/spawn 선례) + playbook §15.1 8→9 row + §15.2 5th invariant(co-land).
- `scripts/lib/append_dev_process_event.py`(index append primitive, `_ROW_KEYS` = §2 code anchor) + `query_dev_process_event.py`(mining port).
- `dev_process_blob_store.py`(capture_blob/deref_blob) + `redact_dev_process_content.py`(redact) — sibling.
- PostToolUse hook 신설(net-new) + redact→capture_blob→append_event orchestration(emit 계층, INV-8b) + lint/self-test(계약==구현 parity + negative-control).

### Out-of-scope (B/C)
- **B(#2688)**: dev-process 지표 계산식·사이클타임 산식·FIX 반복수 집계 알고리즘.
- **C(#2689)**: gate/verdict 판정 규칙·임계·차단 동작·PASS/FAIL 의미.
- dashboard/UI, stop-event-v1 sqlite 전환·5→18-field 런타임 즉시 승격.

## 14. AC → 계약 섹션 매핑 (traceability)

| AC | 계약 섹션 | AC | 계약 섹션 |
|---|---|---|---|
| AC-1 (A scope only) | §1 정체 / §13 OOS | AC-14 (audit 필드·enum) | §8.3 |
| AC-2 (8 event append-only) | §3.1 | AC-15 (blob=redacted, no-conflict) | §1.1 / §6 |
| AC-3 (noise 5 closed) | §3.2 | AC-16 (mining 진입점) | §9 |
| AC-4 (4 상관 ID 정의) | §5.1 / §2 | AC-17 (no 집계·verdict) | §9 |
| AC-5 (freeze 표기) | §5.1 / §4 | AC-18 (allow-list↔rich 화해) | §1.1 |
| AC-6 (closed enum + 6-point) | §3.1 | AC-19 (활성 비대칭) | §10.2 |
| AC-7 (index allow-list clean) | §2 / §2.1 | AC-20 (writer 정합 표) | §10.1 |
| AC-8 (blob-ref 규칙) | §6.1 | AC-23 (drift FACT, no auto-resolve) | §12.1 |
| AC-9 (blob 정량) | §6.1 | AC-24 (gap motivation only) | §12.2 |
| AC-10 (append-only 정정) | §7.1 | AC-25 (retention 3-tier) | §7 |
| AC-11 (관계 매트릭스) | §11 | AC-21 (exit-0 non-blocking) | §10.1 (Phase 2 declared) |
| AC-12 (redaction write-time) | §8.1 / §6.2 | AC-22 (부분기록 식별) | §6.2 / §7.1 (Phase 2 declared) |
| AC-13 (deny-list 경로) | §8.2 | | |

## 15. Cross-references

- **ADR-155** — 본 계약 설계 SSOT(9 결정).
- **ADR-163** (measurement channel) — 9th channel(Amendment 2) + warm-tier + §15.2 5th boundary invariant.
- **ADR-043** (telemetry privacy) — redaction 상속·확장(Amendment 4: always-on 비대칭 + deny 6→7 + redacted-blob T-INFO-5 + audit).
- **ADR-104** — scope-guard(dev-process ⊥ operational-phase disjoint axis).
- **ADR-115** — record-only·non-blocking·exit0·graceful degradation 상속.
- **ADR-064** — consumer opt-in-false 무약화(α 비대칭).
- **ADR-031/038/039** — lane evidence boundary / lane_transition 6-point / writer monopoly.
- **ADR-119** — 정직 천장(resource-safety 무증거 단정 금지 / mining exact-count 주장 금지).
- **stop-event-v1 / spawn-event-v1 / fix-event-v1 / review-verdict-v4** — new-sibling(§11).
- **oh-my-claudecode (MIT)** — spawn-event 계보의 append/replay 패턴(간접 lineage).
