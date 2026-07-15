---
adr_number: 155
title: Dev-process observability substrate + dev-process-event-v1 evidence contract
date: 2026-07-15
status: Active
category: orchestration-discipline
carrier_story: CFP-2687
supersedes: null
amends: null  # new-sibling — 기존 stop-event-v1 / spawn-event-v1 / fix-event-v1 무변경 (관계 매트릭스 §결정 2)
related_adrs:
  - ADR-042  # measurement channel architecture — 9th Tier-3 channel (Amendment 2 동반 carrier)
  - ADR-043  # telemetry privacy policy — redaction 계약 상속 (Amendment 4 동반 carrier)
  - ADR-104  # operational-phase definition — wrapper-N/A ⊥ dev-process disjoint axis (§결정 9 scope-guard)
  - ADR-115  # runtime hook enforcement — record-only·non-blocking·exit0 상속
  - ADR-064  # evidence-gated symmetric ratchet — consumer opt-in-false 무약화 (α 비대칭)
  - ADR-013  # dogfood-out — change-plan/story internal-docs SSOT
  - ADR-078  # living architecture doc — codeforge-family.md 갱신 의무
  - ADR-119  # research-before-claims — 정직 천장 (resource-safety / mining honest-degrade)
related_stories:
  - CFP-2687
related_cfps:
  - CFP-2687  # Epic #2686 Story A (선행 substrate + evidence contract)
  - CFP-2688  # Epic #2686 Story B (dev-process 지표 산출 — 본 substrate consumer)
  - CFP-2689  # Epic #2686 Story C (결점 self-gate verdict — 본 substrate consumer)
related_files:
  - docs/inter-plugin-contracts/dev-process-event-v1.md  # 신규 통합 계약 (Phase 2 실 파일 — 본 ADR 이 설계 SSOT)
  - docs/inter-plugin-contracts/MANIFEST.yaml  # kind:registry comment 갱신 (Phase 2)
  - docs/orchestrator-playbook.md  # §15.1 8→9 channel boundary table (Phase 2 co-land — 계약 파일과 동반)
  - archive/adr/ADR-042-codeforge-measurement-channel-architecture.md  # Amendment 2 sibling
  - archive/adr/ADR-043-codeforge-telemetry-privacy-policy.md  # Amendment 4 sibling
  - docs/architecture/codeforge-family.md  # interfaces + data_flow + Open Decisions 갱신
is_transitional: false
mechanical_enforcement_actions: []  # Phase 1 = 설계 SSOT (계약 스키마 lint / self-test / parity = Phase 2). ADR-082 §결정 6 retain pattern — Phase 2 carrier = 본 Story §8-§11.
---

# ADR-155: Dev-process observability substrate + dev-process-event-v1 evidence contract

## 상태

**Active (2026-07-15)** — carrier_story = CFP-2687 (Epic #2686 Story A, 선행). Phase 1 = 설계 SSOT (ADR + change-plan + Story §3/§7 + 아키텍처 doc). **실 `dev-process-event-v1.md` 계약 파일 + capture 배선 + blob store + mining script + lint/self-test = Phase 2** (본 Story §8-§11). B(지표 산출 #2688)·C(self-gate verdict #2689) = out-of-scope — 본 ADR 은 substrate·증거계약만 codify.

번호 발급 = **GH_TOKEN 부재로 OCC atomic claim primitive 미실행 → ADR-133 §결정 4 fallback**(`git fetch origin main` + `git ls-tree --name-only origin/main archive/adr/` numeric max = ADR-154, 149 orphan gap, 155 collision-free, 2026-07-15 KST). rows 153/154 동일 fallback 선례. dual-key 3-leg 정합: filename `ADR-155-dev-process-observability-substrate.md` ∧ frontmatter `adr_number: 155` ∧ ADR-RESERVATION row 155.

## 컨텍스트

### 동기 — dormant substrate + content-blind ledger

Epic #2686 = codeforge 가 **자기 자신의 10-lane 개발 과정을 계측**(dev-process self-observability)하려는 자기-개선 arc. 근본 결함 = 관측 substrate 는 설계됐으나(ADR-042/043 + stop-event-v1 v1.2 + spawn-event-v1) **활성화되지 않았고**(Phase-1-doc-only + ROI-gate 뒤 deferred), 실 런타임 ledger 는 **5-field content-blind**(lane/defect/fix/story 상관 0, rich-capture 미활성 — 실 활성 `.claude/ledger/stop-event.jsonl` 7,122 rows firsthand). 최근 self-referential dogfood 결점 7연속 재발이 곧 ROI 정당화 — 계측 부재로 "무엇이 왜 반복되나"를 재구성할 증거층이 없다.

### Gap (Story A 가 메우는 것)

1. **통합 evidence 계약 부재** — 기존 6 event 계약은 각자 1 event-type 만 커버(stop=stop, spawn=spawn, fix=FIX). lane 전이·프롬프트·tool-call·diff·verdict·findings·최종산출물을 **하나의 typed append-only stream** 으로 통합한 계약이 없다.
2. **cross-lane 결점 identity 부재** — anchor_id(review-verdict)는 verdict-scope, cross-lane 결점 추적 ID(defect_id) 아님. 결점 재발 집계(B의 D4 축)의 identity 축 부재.
3. **상관 ID freeze 부재** — B(집계)·C(판정)가 병렬 전제로 공유할 story/lane/defect/fix 4종 ID 의 이름·scope·생성시점·안정성 규칙이 미확정. 미확정 병렬 = 백필 부채.
4. **rich-content vs allow-list 긴장** — 기존 stop/spawn-event 는 allow-list-ONLY + anti-content(numeric/enum/hash-only, transcript content·path 미저장 = T-INFO-5/8). rich content 를 기존 row 에 필드 추가로 수용하면 v2.0 breaking + T-INFO-5 위반.
5. **보존등급 부재** — hot/cold 2-tier 만 존재(ADR-042 §결정 4), 압축 아티팩트 warm tier 부재. 큰 payload content-addressed blob 저장 표면 부재.

### 근본 긴장 3개 — 요구사항 lead 결정(INV-4/α) 상속

- **INV-4 (2계층 화해)**: index 는 allow-list-clean 유지(기존 anti-content 무손상), rich content 는 별도 redacted blob store(신규 표면). no-conflict — index 는 content-free, blob 은 redaction-후 산물.
- **α (always-on 비대칭)**: wrapper-self dogfood = always-on(계측이 목적), consumer = opt-in default-false(ADR-064 §결정 7 extend-only, privacy 무약화). always-on 이더라도 capture-time redaction 항상 선행(INV-8).
- **INV-1 (dev-process ⊥ operational-phase)**: ADR-104 wrapper-N/A 는 운영 phase 측정 한정 — dev-process observability 와 disjoint axis(§결정 9 scope-guard).

## 결정 (9)

### 결정 1 — dev-process-event-v1 신규 통합 계약 (kind:registry, new-sibling, 9th Tier-3 channel)

`docs/inter-plugin-contracts/dev-process-event-v1.md` 신규 file (kind:registry — kind:contract 회피, sibling sync overhead 0, stop/spawn-event 선례). codeforge observability stack 의 **9번째 Tier-3 persistent channel**(ADR-042 §결정 1, Amendment 2 동반). 기존 8 channel(stop/spawn 포함)은 전부 content-blind — rich semantic content 를 흡수할 경로가 0 이므로 **통합 재해석 불가, 신설 필요**(INV-4). 2계층 구조:

1. **index tier (이벤트 행)** — allow-list clean. enum / numeric / hash / 상관 ID / blob-ref only. free-form content 본문 직접 저장 **0**. 기존 anti-content invariant(T-INFO-5/8) **무손상**.
2. **evidence-blob-store (rich content 표면)** — capture-time redaction 후 content-addressed blob 저장. 이벤트 행은 blob 의 hash 참조(`blob_ref`)만 보유. blob store = 기존 계약에 없던 **신규 비밀 표면** → 자체 redaction·보존·참조 규약을 계약이 정의(§결정 5, ADR-043 Amendment 4).

Phase 1 = 계약 설계 SSOT(본 ADR). **실 `dev-process-event-v1.md` 파일 = Phase 2**(§결정 12 stop-event 선례 — doc-first, 실 배선 defer). 기존 hook/append 런타임 = Phase 1 무변경(content-blind INV 보존).

### 결정 2 — 관계 매트릭스: new-sibling event-ownership 분해 (normative non-overlap)

dev-process-event-v1 ↔ 기존 계약 관계 = **supersede 아님, new-sibling**. 관계 매트릭스를 계약 §관계 섹션 + 본 §결정에 normative 로 명시(SoT 이중화 §5.4 차단):

| 기존 계약 | 관계 | event-ownership 경계 (normative) |
|---|---|---|
| stop-event-v1 | new-sibling | stop 이벤트 = stop-event-v1 단독 소유. dev-process 는 stop 이벤트 accounting 을 **re-record 하지 않음** — 필요 시 `event_id` 상관으로 JOIN(cross-read 허용, payload 복제 금지) |
| spawn-event-v1 | new-sibling | per-agent spawn token/cost = spawn-event-v1 단독 소유. dev-process lane 전이 이벤트는 spawn accounting 을 복제하지 않고 `event_id` JOIN |
| fix-event-v1 (§10 FIX Ledger) | new-sibling | §10 FIX row append = Orchestrator monopoly 불변. dev-process 의 `fix_id` FIX-전이 이벤트는 §10 accounting 을 **재기록하지 않음** — 1 §10 row ↔ 1..N `fix_id` 상관만 |
| review-verdict-v4 / *-output-v1 | new-sibling | verdict/산출물 요약 accounting = 각 output 계약 소유. dev-process verdict 이벤트는 semantic-evidence-aggregation(어떤 verdict 가 났나 참조)이지 verdict 의미론 정의(C scope) 아님 |

**5th boundary invariant (ADR-042 §15.2 amendment)**: dev-process-event = **semantic-evidence-aggregation** — 상관 ID cross-read(JOIN) 허용 / accounting payload re-record 금지. 동일 의미를 두 channel 이 각자 기록하는 SoT 이중화(§5.4)를 구조적으로 차단.

### 결정 3 — 4 상관 ID freeze + 결점 taxonomy 4-tuple (B·C 공유, 정직 천장)

**4 상관 ID (freeze — 변경 시 계약 amendment 의무, B·C 병렬 전제)**:

| ID | 신규? | scope | 생성 시점 | 안정성 |
|---|---|---|---|---|
| `story_key` | 재사용 | Story 전체 | Story 시작 (hook-derivable: `CLAUDE_PROJECT_DIR`/branch `cfp-NNN`) | immutable |
| `lane_label` | 재사용 | lane 전이 단위 | lane 진입 | label-registry enum, FIX 재진입 시 동일 label(구분 = `fix_id`) |
| `defect_id` | **신규** | cross-lane 결점 identity | 최초 findings emit 시 | content-addressed `sha256(family ‖ type ‖ normalized-location)`, summary **제외**(wording drift caveat — 결정론 over-claim 금지) |
| `fix_id` | **신규** | per-defect 대응 **시도** 단위 (lane 재진입 단위 아님) | FIX 개시 시 (agent-emit) | §10 Iter monopoly 불변 — 1 §10 row ↔ 1..N `fix_id` |

`finding_id` = subordinate(anchor_id = verdict-scope 재사용). `defect_id ← finding_id` = N:1. D4 재발 = 동일 `defect_id` 에 `finding_id > 1`(distinct per 검출).

**결점 taxonomy 4-tuple (★정직 — 전부 closed enum 아님, over-claim 금지)**:

| 축 | 종류 | 값 |
|---|---|---|
| `family` | **CLOSED 7** | correctness / security / performance / design-boundary / test-gap / doc-integrity / process-discipline (exact 멤버 = 본 §결정 ratification) |
| `type` | **SEMI-OPEN** | review-verdict-v4 type-derived ∪ `unknown-type`(미분류 fallback) |
| `time_to_detection` | **DERIVED measure (enum 아님)** | ordinal — lane-distance ∨ ts-delta. 도입점 불명 = `unattributed` |
| `detecting_lane` | **CLOSED** | lane_label enum |

"4-tuple 전부 closed enum" 은 over-claim — `type` 은 semi-open, `time_to_detection` 은 derived measure. 이 정직 천장을 계약이 명시(AC-4/5 freeze 표기 = family/lane closed, type semi-open, ttd derived).

### 결정 4 — capture 경로 이원화 (hook 3 / agent-emit 5 + emit_source discriminator)

capture 는 두 Port 로 이원화하되 **single event stream**(JOIN 보존):

| event type | 경로 | Port |
|---|---|---|
| 프롬프트/입력 | hook (PreToolUse Agent) | A (hook-adapter) |
| tool-call | hook (PreToolUse + **PostToolUse net-new**) | A |
| diff | hook (**PostToolUse net-new**) | A |
| lane 전이 | agent-emit (Orchestrator) | B (agent-emit) |
| verdict | agent-emit (review lane) | B |
| findings | agent-emit (review lane) | B |
| FIX 전이 | agent-emit (Orchestrator §10 monopoly) | B |
| 최종 산출물 | agent-emit (lane) | B |

- **Port A (hook-adapter)** — PostToolUse hook 신설 = Phase 2. hook 은 NON-ambient — lane 은 `agent_type→lane` map(semi-open, 미등재→"없음" fallback) 또는 agent-emit 직접 주입. Stop hook 에 lane ambient 기대 금지(dependency direction: hook→env only).
- **Port B (agent-emit)** — Orchestrator-owned delegate writer monopoly.
- **`emit_source` enum {hook, agent}** = index discriminator field(allow-list-clean). single-stream JOIN 보존 + capture path 정직 구분. 2-channel 물리 분리는 기각(INV-3 JOIN 파괴).

### 결정 5 — evidence-blob-store: content-addressed + redaction-선행 (INV-8a/b)

큰 payload = content-addressed blob 참조. 계약이 정량 규칙 명시(AC-8/9). **비협상 순서(SecurityArch P0)** — 5 P0 위협 = T-DPE-1~5 (STRIDE-LITE 10-threat 집합의 P0 층, enumeration SSOT = change-plan §7.1 표, count=10):

- **INV-8a (T-DPE-1 redaction-order + T-DPE-2 hash-over-redacted)**: redact(in-memory, 원본 disk 미접촉) → `blob_ref = sha256(REDACTED bytes)` (**NEVER raw**) → blob write(redacted, single). hash-over-unredacted 는 index 가 content-free 여도 `blob_ref` 가 secret confirmation oracle 이 됨(T-DPE-2 hash-oracle P0) → hash-over-redacted 가 봉인.
- **INV-8b (T-DPE-5 blob-before-index)**: blob write → THEN index row(blob_ref). 역순 = dangling evidence chain(AC-22).
- **index allow-list-only (T-DPE-3, T-INFO-8 구조 차단) + novel-secret 심층방어 (T-DPE-4 — honest-ceiling: deny-list 완전커버 아님, residual 명시)** + 상세 blob deny-pattern / audit enum / always-on bound = ADR-043 Amendment 4(privacy SSOT). T-DPE-6~10(P1: transcript·cross-host·audit-oracle·consumer-override·DoS) = 동 SSOT.

### 결정 6 — retention 3-tier (hot/warm/cold) + AC-10∧AC-25 화해 (append-only ∧ GC 모순 해소)

dev-process-channel-scoped 3-tier(ADR-042 §결정 4 hot+cold 2-tier 를 본 channel 에 한해 3-tier 확장 — Amendment 2 (b)):

| tier | 저장형태 | latency | 보존 | spill 전이 |
|---|---|---|---|---|
| hot | 구조화 JSONL index + loose blob | ms | 7-30d (proposal) | age > hot_days ∨ blob-dir > cap → warm |
| warm | 압축 pack + gz (index 무압축 유지) | 10s–100s ms | ~90d (proposal) | age > warm_days → cold |
| cold | 아카이브 | s | policy-bound → evict+tombstone | 역방향/skip 금지 (strict hot→warm→cold) |

**★AC-10(append-only) ∧ AC-25(cold GC/압축) latent contradiction 화해** (InfraOp P0-1 — naive 구현 시 cold blob 삭제 → index blob_ref dangling):

1. **tombstone**: cold blob 물리 삭제 시 index `blob_ref` **불변 유지**(참조 안 지움). append-only "blob-evicted" event/sidecar 가 `evicted_at`+tier 기록 → reader 는 silent 404 아닌 **eviction 증거**에 도달.
2. **content-preserving hash-verified transform**: warm/cold 압축은 물리 rewrite 이나 append-only 는 **논리 evidence stream** 에 적용. decompress 시 byte-identical redacted 복원, `hash(decompressed) == blob_ref` 재검증 의무, index row 절대 rewrite 안 함. 불변 anchor = `blob_ref` 가 전 tier 관통(git loose→pack 동형).

"in-place edit 금지" 는 **논리 스트림**(index row + blob_ref 불변)에 적용 — 물리 압축/eviction 은 hash-verified transform + tombstone 으로 append-only invariant 를 보존한다.

### 결정 7 — mining/query 진입점 (raw typed rows, B/C disjoint consumer)

`scripts/lib/query_dev_process_event.py`(aggregate_stop_event 선례). 입력 = filter params(story/lane/defect/fix/event_type/time-window). 반환 = **raw typed event rows + blob deref**(집계 metric / verdict 아님 — AC-17). B(지표)·C(verdict)는 disjoint consumer — port 하류 무의존. read-time dedup(event_id) = port 소유. ports & adapters — storage 포맷 계약 표면 비노출(reader port 뒤 격리, drift 봉쇄). aggregate-level(RDB) N/A — file-based(§11 RDB N/A).

### 결정 8 — always-on 비대칭 (α) + Phase 1 doc-only / Phase 2 실배선

- **wrapper-self dogfood scope = always-on** — codeforge family 자기 개발 계측이 Story 목적. always-on = checkout-identity 파생(user-settable bool 아님). ADR-042 §결정 6 "wrapper dogfood always-on = Phase 2 follow-up" 를 본 Story 가 carrier.
- **consumer 배포 scope = opt-in default-false** — consumer overlay extend-only(ADR-064 §결정 7), privacy invariant **무약화**. consumer floor 하방 override 불가(T-DPE-9).
- **always-on 4중 bound + redaction-선행 floor + resource-safety honest-ceiling** = ADR-043 Amendment 4 SSOT.
- Phase 1 = 계약 설계(정책 anchor). Phase 2 = 실 capture 배선(PostToolUse hook + append primitive + blob store + redaction fn).

### 결정 9 — scope-guard ⊥ ADR-104 (dev-process ⊥ operational-phase, false-block 차단)

**신규 substrate 는 ADR-104 §결정 4 wrapper-N/A 를 건드리지도 약화하지도 않는다** — wrapper-N/A 는 **운영(production) phase 측정에만** 적용(배포된 consumer 앱 런타임 신호), dev-process observability(개발 과정 관측)는 **disjoint axis** 로 그 공백을 메운다. homonym 주의: `measurement-channel.md` 파일 2개(operational-phase area vs orchestrator-discipline area)는 별개 도메인 — 같은 이름이 유발하는 착시(firsthand: measurement-channel.md operational-phase 판 = "배포된 앱 런타임" 정의). 이 scope-guard 부재 시 설계리뷰가 "wrapper runtime 0 → 측정 불가" broad-오독으로 false-block.

## 회피된 대안

### 대안 A — 기존 stop-event-v1 확장 (경로 B)

stop-event-v1 에 content 필드 추가.

**거부 이유**: v2.0 breaking + T-INFO-5 위반(transcript content 미저장 HARD invariant) + 5-field 런타임 괴리 확대 + 다중 계약 breaking. Refactor firsthand — 경로 A(new-sibling)가 최소변경(기존 anti-content invariant 무손상).

### 대안 B — hook / agent-emit 2-channel 물리 분리

capture path 별로 별도 event stream 2개.

**거부 이유**: single-stream JOIN 파괴(INV-3) — B·C 가 상관 ID 로 cross-read 불가. 채택 = §결정 4 `emit_source` discriminator(single stream + path 정직 구분).

### 대안 C — index 에 rich content 직접 저장 (blob store 미신설)

이벤트 행에 프롬프트/diff 본문 직접 저장.

**거부 이유**: anti-content invariant 위반 + secret 표면 폭증 + index grep 시 leak. 채택 = §결정 1 2계층(index allow-list-clean + redacted blob hash 참조).

### 대안 D — retention 2-tier 유지 (warm 미신설)

hot/cold 만.

**거부 이유**: 압축 아티팩트 등급 부재로 hot→cold 급락(조회 latency 붕괴) 또는 hot 무한 팽창. 채택 = §결정 6 3-tier(hot→warm→cold strict).

## 외부 fact (Story §6 verified — ClaudeReviewAgent firsthand fetch)

본 ADR 의 설계 정당화 외부 사실(Story §6.5 Sources, firsthand 검증 — ADR-119 정합):

1. **append-only typed event log** — OpenTelemetry Logs Data Model / CloudEvents / ECS `source: opentelemetry.io/docs/specs/otel/logs/data-model/`
2. **안정 상관 ID** — W3C Trace Context (Recommendation, 2021-11-23) `source: w3.org/TR/trace-context/`
3. **content-addressed blob + spill** — git blob(sha) / IPFS CID `source: docs.ipfs.tech/concepts/content-addressing/`
4. **capture-time redaction denylist** — gitleaks `source: github.com/gitleaks/gitleaks`; crypto-shredding(키 폐기) `source: verraes.net/2019/05/eventsourcing-patterns-throw-away-the-key/`
5. **hot/warm/cold retention** — Elasticsearch ILM hot/warm/cold/frozen/delete + rollover `source: elastic.co/guide/en/elasticsearch/reference/current/index-lifecycle-management.html`
6. **high-signal vs full capture** — OTel sampling `source: opentelemetry.io/docs/concepts/sampling/` — "거의 전부 보존" ≠ 전량 스크랩, high-signal 증거계약
7. **dev-process self-instrumentation** — DORA 현행 다지표 + OTel GenAI semconv(Development/experimental·불안정 → 외부 soft-align only, hard-freeze 대상 아님 — §6.4 R5)

## 검증 채널

Phase 2 carrier(본 ADR = 설계 SSOT, `mechanical_enforcement_actions: []` — ADR-082 §결정 6 retain pattern). Phase 2 lint/self-test 후보:

1. **계약==구현 honesty self-test** — anti-tautology oracle. Phase 1 = **doc-internal cross-section consistency**(`index fields ⊆ allow-list` = 같은 계약 문서 두 섹션, 둘 다 author-controlled·외부 oracle 부재 → doc-internal consistency check 이지 tautology 완전면역 아님). **진짜 독립 oracle = Phase 2 code-anchor** — 계약 §2 table(동적 파싱) vs append `_ROW_KEYS`(Python-hardcoded EXTERNAL code anchor, 동적 파싱) parity(doc vs code), `check_self_context_telemetry_allowlist.py` S1(=`_ALLOWLIST_6` 하드코딩 code anchor)이 예시하는 external-anchor 구조. self-test 는 impl 존재 시 parity non-skippable(impl-present skip 변형 제거) — 단 이는 기존 check_spawn_event `_check_runtime_parity` impl-존재 branch(`check_spawn_event_schema.py:217-224`, import 성공 시 mismatch RED)와 **동형이지 신규 봉인 아님**. **impl-ABSENT born-drift**(계약만 있고 append impl 부재로 parity 자체가 skip, `:199-201`)는 이 self-test 가 **봉인하지 못한다** → 방어는 **§8.10 activation-manifest(landing≠activation)로 위임**(change-plan §8.2↔§8.10 상호참조). "hole 을 닫는다/봉인" over-claim 금지(self-ref 정직).
2. **negative-control (discriminating RED)** — RC1 index free-form 추가→allow-list RED / RC2 상관ID 제거→freeze RED / RC3 noise 6번째→closed RED / RC4 AC-23 드리프트 서술 제거→honesty RED.
3. **born-red 방지** — 신규 lint(있으면) 자기 계약 파일 born-green, presence-grep false oracle 금지(execution-backed).

(Phase 1 self-test 상세 = 본 Story change-plan §8 + Story §8-미러. 실 lint = Phase 2 dev-process-event-v1.md 계약 파일 co-land.)

## 결과

### 영향 (Phase 1 — 본 Story)

- `archive/adr/ADR-155-dev-process-observability-substrate.md` (본 file)
- `archive/adr/ADR-042-*.md` Amendment 2 (9th channel + warm-tier + ROI supersede)
- `archive/adr/ADR-043-*.md` Amendment 4 (always-on 비대칭 + blob deny-pattern + redacted-blob T-INFO-5)
- `archive/adr/ADR-RESERVATION.md` row 155
- change-plan + Story §3/§7 + `docs/architecture/codeforge-family.md`(interfaces/data_flow/Open Decisions)

### 비-영향 (Phase 1)

- 기존 hook/append 런타임(`append_stop_event.py`·`append_spawn_event.py`) 무변경 — content-blind INV 보존
- 기존 6 event 계약 본문(new-sibling — supersede 0)
- label-registry / branch-protection 7-tuple(신규 required context 0 — 추정, 설계 확인)
- consumer opt-in privacy(α 무약화)
- 기존 stop-event-v1 계약↔구현 드리프트(18↔5 field) = 본 계약이 **자동 해소한다고 주장 안 함**(AC-23) — new-sibling 은 현실 위에 얹힌다

### Phase 2 (본 Story §8-§11 + B·C)

- 실 `dev-process-event-v1.md` 계약 파일 + MANIFEST comment + playbook §15.1 8→9 row(계약과 co-land, dangling 회피)
- PostToolUse hook 신설 + append primitive(O_APPEND) + evidence-blob-store + redaction fn + mining script + lint/self-test

### Reversibility

- Yes — 본 ADR `status: Deprecated` + 영향 file revert 시 dormant substrate 상태 복원. 기존 계약 무변경이라 revert blast radius = 신규 계약 표면 한정.

## Out-of-scope

- **B (지표 산출 #2688)** — dev-process 지표 계산식·사이클타임 산식·FIX 반복수 집계 알고리즘
- **C (self-gate verdict #2689)** — gate/verdict 판정 규칙·임계·차단 동작·PASS/FAIL 의미
- dashboard / UI / 운영 리포트 레이아웃
- stop-event-v1 sqlite 전환·5→18-field 런타임 즉시 승격
- "Phase 1 만으로 D3/D4/D5 gap 운영상 해소" 주장(활성화+통합+freeze 로만 서술 — AC-23/24)

## 해소 기준

N/A — permanent substrate policy (약화 방향 차단 ratchet, is_transitional: false)

## 관련 ADR

- **ADR-042** (measurement channel architecture) — 9th Tier-3 channel. Amendment 2 sibling(§결정 1 8→9 + warm-tier + ROI supersede). §15.2 5th boundary invariant.
- **ADR-043** (telemetry privacy policy) — Amendment 4 sibling. redaction 계약(INV-8a/b deny-pattern·audit·always-on bound·redacted-blob T-INFO-5) SSOT.
- **ADR-104** (operational-phase definition) — §결정 9 scope-guard. wrapper-N/A(운영 phase) ⊥ dev-process(개발 과정) disjoint axis.
- **ADR-115** (runtime hook enforcement) — capture 실패 = record-only·non-blocking·exit 0 상속(AC-21/22).
- **ADR-064** (evidence-gated symmetric ratchet) — §결정 7 consumer opt-in-false 무약화(α 비대칭 consumer 측 근거).
- **ADR-013** (dogfood-out) — change-plan/story internal-docs SSOT.
- **ADR-078** (living architecture doc) — codeforge-family.md 갱신 의무(인터페이스/데이터흐름/Open Decisions).
- **ADR-119** (research-before-claims) — 정직 천장(resource-safety 무증거 ReDoS-safe 금지 / mining exact-count 주장 금지).

## 관련 파일

- `docs/inter-plugin-contracts/dev-process-event-v1.md` (신규 — Phase 2 실 파일, 본 ADR 이 설계 SSOT)
- `docs/inter-plugin-contracts/MANIFEST.yaml` (kind:registry comment — Phase 2)
- `docs/orchestrator-playbook.md` §15.1 (8→9 channel boundary table — Phase 2 co-land)
- `archive/adr/ADR-042-codeforge-measurement-channel-architecture.md` (Amendment 2)
- `archive/adr/ADR-043-codeforge-telemetry-privacy-policy.md` (Amendment 4)
- `docs/architecture/codeforge-family.md` (interfaces/data_flow/Open Decisions)
- `mclayer/codeforge-internal-docs:wrapper/stories/CFP-2687.md`
- `mclayer/codeforge-internal-docs:wrapper/change-plans/2026-07-15-cfp-2687-dev-process-observability-substrate.md`
