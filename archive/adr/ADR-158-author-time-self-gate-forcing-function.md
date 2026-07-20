---
adr_number: 158
title: Author-time self-gate forcing function — 기존 required 기계 게이트를 리뷰 lane 진입 전 저작시점에 그 Story 자기 산출물에 선적용(shift-left) + 검출 결점 dev-process-event ledger emit (A substrate 소비 · B 하류 집계 · #2684 게이트 자기검증 disjoint)
status: Active
category: orchestration-discipline
date: 2026-07-16
carrier_story: CFP-2689
parent_epic: CFP-2686
supersedes: null
amends: null  # new-sibling — ADR-145(ac-traceability)/ADR-060(test-contract)/ADR-155(substrate) 본문 무변경. shift-left 실행시점 이동 + 결점 emit = 신규 discipline(단일 게이트 scope amendment 아님 — A/B new-sibling ADR-155/156 선례 동형)
related_stories:
  - CFP-2689     # 본 carrier (Epic #2686 Story C — 저작시점 self-gate)
  - CFP-2687     # 선행 substrate (Story A — ADR-155 dev-process-event-v1 emit port)
  - CFP-2688     # 병렬/선행 aggregator (Story B — ADR-156 dev-process metric aggregation, C emit consumer)
  - CFP-2686     # umbrella Epic
related_adrs:
  - ADR-155      # 강 의존 (substrate SSOT) — dev-process observability substrate + dev-process-event-v1. C = 신규 defect_finding producer 콜사이트, emit port 소비만(A 계약 0 수정)
  - ADR-156      # 강 인접 (하류 consumer) — dev-process metric aggregation. C defect_finding emit → B compute_selfref_recurrence 4-tuple + _capture_subject 소비. C=producer ⊥ B=aggregator(A OOS 표 상속)
  - ADR-145      # 강 의존 (shift-left 대상 게이트) — ac-traceability zero-drop. C 가 저작시점 앞당길 핵심 게이트(Phase-aware RTM Hop1/2/3). A/B late-catch 2회의 merge-gate 블로커
  - ADR-154      # 강 인접 (disjoint 경계 명시 의무) — hard-gate-self-verification(#2684 silent-green meta-gate). C(저작시점 self-적용) ⊥ #2684(게이트 자기검증) — false-conflation 방지
  - ADR-119      # 강 의존 (정직 천장 + 2 판정면) — self-gate PASS=outcome ground-truth(proxy 아님) / "결점 주입 완전 방지" over-claim 금지 / self-ref dogfood 8-11연속 이력 대응 / self-test 독립 oracle(CFP-2673 X⊆X tautology 금지)
  - ADR-115      # 강 의존 (record-only non-blocking exit-0) — C emit 실패 = graceful None, self-gate 흐름 무차단
  - ADR-163      # 배경 (measurement channel) — dev-process = 9th channel / 0-API-call / always-on α 비대칭 상속
  - ADR-060      # 배경 (test-contract lint 선례) — 신규 lint non-required day-1 + 대칭 fail-closed self-test 선례
  - ADR-151      # 배경 (selftest-execution-liveness inventory) — C self-test enroll(channel alive, bijection +1)
related_files:
  - archive/adr/ADR-RESERVATION.md                                # row 158 append (dual-key 3-leg)
  - archive/adr/ADR-155-dev-process-observability-substrate.md    # substrate SSOT (read-only 소비, 의미 변경 0)
  - archive/adr/ADR-156-dev-process-metric-aggregation-escalation-feed.md  # 하류 aggregator (read-only, 의미 변경 0)
  - archive/adr/ADR-145-ac-traceability-zero-drop-gate.md         # shift-left 대상 게이트(본문 무변경)
  - scripts/lib/emit_dev_process_event.py                         # A emit port (C 결점 emit 유일 진입점, 소비만·의미 변경 0)
  - scripts/lib/authoring_self_gate.py                            # 신규 self-gate runner (Phase 2 carrier)
  - docs/selftest-execution-liveness-inventory.yaml               # C self-test enroll +1 (Phase 2)
  - docs/architecture/codeforge-family.md                         # living-arch interfaces + data_flow + Open Decisions 갱신
is_transitional: false  # permanent process-discipline anchor — ADR-155/156(substrate/aggregation, is_transitional:false) 정합. 저작시점 shift-left forcing function + 결점 telemetry emit = future 재사용 permanent. 약화 방향 차단 ratchet(honest-ceiling 완화 / 실-게이트 invoke 강제 제거 / A-substrate 수정 = 약화 evidence-gate 의무)
sunset_justification: null  # is_transitional false — amendment 시 강화 방향만(대상 게이트 집합 확장 / dogfood 자기적용 강화 / honest-ceiling 강화). honest-ceiling 완화·over-claim 허용·실게이트 invoke 판정 대체 = 약화 방향 → ADR-058 §결정 5 약화 evidence requirement 의무
mechanical_enforcement_actions:   # Amendment 1 (CFP-2776) — declaration-only Phase 1 → mechanizable subset 실현. Phase-1 이력: 실 self-gate runner(authoring_self_gate.py 존치) + advisory lane-exit self-check + self-test = CFP-2689 §8-§11. pattern_count >= 2 재발 시 mechanical 승격 MUST(ADR-084 precedent) → 본 Amendment 1 이 malformed-VALUE subset scope 로 실현.
  - action: internal-docs-authoring-hop1-blocking-gate
    carrier: CFP-2776
    repo: mclayer/codeforge-internal-docs
    workflow: .github/workflows/ac-schema-authoring-gate.yml
    scope: ac-traceability Hop1 well-formedness (§5.3 AC id/source/tier/statement malformed-VALUE) — 저작 repo 저작시점 blocking
    tier: mechanical (blocking CI, fail-closed) — advisory authoring_self_gate.py 존치(defense-in-depth, 다른 시점 커버)
    promotion_basis: "family >= 2 (CFP-2566 malformed-enum VALUE = in-scope firsthand exemplar + CFP-2748/2751/2753 tier-choice mislabel = out-of-scope 관찰) → mechanizable subset(malformed-VALUE only) 실현. tier-choice mislabel = semantic 잔여(review-tier, ADR-145 AC-8 CEILING) — Goodhart over-claim 회피."
    telemetry_note: "telemetry(defect_finding dev-process-event emit) = advisory runner(authoring_self_gate.py) 소관; 본 blocking 게이트 = enforcement-only(emit 안 함, review-verdict payload 복제 0 — 5th boundary 무저촉)."
amendments:
  - by: "CFP-2776"
    amendment_id: 1
    date: "2026-07-20"
    scope: "advisory→mechanical 승격 정본화 — internal-docs 저작 repo 에 ac-traceability Hop1 well-formedness blocking CI 게이트(ac-schema-authoring-gate.yml) 배선. mechanical_enforcement_actions [] → populate. 결정 2 사전인가 clause(pattern_count>=2 재발 시 mechanical 승격 MUST) 실현 — malformed-VALUE subset scope. tier-choice mislabel = review-tier 잔여(honest ceiling 보존). branch-protection 7-tuple·wrapper ac-traceability-matrix.yml 무변경. advisory authoring_self_gate.py 존치(defense-in-depth)."
    sunset_justification: "null — is_transitional:false 강화 방향 ratchet(대상 게이트 집합 확장 internal-docs Hop1 추가 + dogfood 자기적용 강화). honest-ceiling 완화·over-claim·실게이트 invoke 판정 대체 아님 → ADR-058 §결정 5 약화 evidence requirement 미해당."
---

# ADR-158 — Author-time self-gate forcing function

## 상태

`Active` (2026-07-16 KST) — carrier_story = CFP-2689 (Epic #2686 Story C, A #2687 substrate + B #2688 aggregator 후속). ArchitectPLAgent chief author direct write (budget 제약 6-deputy fan-out 금지 → PL-direct 합성 + TestContract §8 born-GREEN inline consult, ADR-070/CFP-578 chief author precedent). ADR-079 KST `+09:00` ISO 8601 governance display 정합. status `reserved` 미경유 직접 `active` (chief author scope — ADR-155 row 155 / ADR-156 row 156 precedent 정합). 번호 발급 = OCC firsthand claim(ADR-133 §결정 4 fallback): `git ls-tree origin/main archive/adr/` numeric max = 156 ∧ open PR #2706(CFP-2700) = ADR-157 점유 → **157 collision → 158 claim collision-free** (dual-key 3-leg: filename `ADR-158-…` ∧ frontmatter `adr_number:158` ∧ ADR-RESERVATION row 158, 2026-07-16 KST).

## 컨텍스트

### 동기 — 구조/위치 conformance 결점이 리뷰를 통과하고 merge-gate 에서만 late 포착

Epic #2686 = codeforge 가 자기 10-lane 개발 과정을 계측·자기개선하는 arc. A(#2687)·B(#2688) 구축 중 **동일 실패모드가 3회 발생**(세션 firsthand):

1. A: RTM 표 부재 → doc-section-schema / ac-traceability merge-gate 블로커.
2. A: 계약 §4=변경규칙 위치 위반(doc-section-schema strict) merge-gate 블로커.
3. B: RTM §8.1.1 이 gate-parseable 아님(헤더 "명명 테스트" 부재·백틱 심볼 0·`tests/**` Python `test_*` 부재) → ac-traceability Phase-2 merge-gate 블로커.

매번 설계·구현 리뷰가 "RTM resolvable" 을 **advisory 판정**했으나 **실 게이트를 Phase-2 모드로 안 돌려서** 놓쳤고, 이미 required 인 기계 게이트(ac-traceability / doc-section-schema — branch-protection 7-tuple 소속)가 파이프라인 **최우측(merge-gate CI, 가장 늦음)** 에서만 결점을 잡아 설계·구현 리뷰 사이클을 낭비했다. 이 클래스 = **구조/위치 conformance = 리뷰 사각**(사람 리뷰가 기계 게이트를 대신 실행하지 않음).

self-referential dogfood 결점 8-11연속(CFP-2661~2684)이 같은 원리를 실증한다 — typed defect-signature 가 self-produced artifact 에서 반복 재발하며, "저작시점에 실패모드를 guardrail 로 주입" 하면 재발이 예방된다.

### Gap (Story C 가 메우는 것)

- **저작시점 실행 채널 부재** — 이미 required 인 기계 게이트를 리뷰 lane 진입 **전(저작 완료 직후)** 에 그 Story 실 아티팩트에 선실행하는 표준 절차·runner 가 없다. 리뷰는 그물(net)일 뿐 예방(forcing function)이 아니다.
- **결점 telemetry 채널 부재** — 저작시점 검출 결점을 A dev-process-event ledger 로 emit 해 B 가 self-ref 재발률로 집계할 producer 콜사이트가 없다(A substrate 의 defect_finding 채널은 dormant).

### 근본 긴장 3개 — 요구사항 lead 결정 상속

- **T1 (shift-left ⊥ 신규 게이트)** — C = 기존 required 게이트의 **실행 시점 이동**이지 신규 게이트 발명이 아니다. branch-protection 7-tuple 무변경(신규 required context 0). 신규 lint(있으면) = non-required day-1.
- **T2 (detecting_lane 표현 공백)** — A schema 의 `detecting_lane` = CLOSED lane_label enum(11값) 위 **nullable** 필드. `authoring-self-gate` 는 enum 비-멤버 → append `_norm_enum(..., None)` 이 `null`(None) 으로 coerce → 신호 소실. (`없음` 은 lane_label 전용 fallback — detecting_lane 은 `없음` 이 아니라 `null` 로 coerce, 비대칭). C 는 lane_label enum 을 단독 확장 불가(A/B 계약 수정 금지) → honest-degrade.
- **T3 (self-ref born-red 위험)** — self-gate 를 만드는 Story 이므로 자기 self-test 가 born-red/born-hollow 면 thesis 자체 반증. 독립 oracle + 대칭 fail-closed 강제.

## 결정

### 결정 1 — self-check 대상 conformance 축 = closed 게이트 집합 + runnable/defer 정직 분류

C self-gate 가 저작시점 실행하는 게이트 = 명시 집합(최소):

- `ac-traceability-matrix`(ADR-145, **Phase-aware** — RTM Hop1/2/3) — **runnable-now**(로컬 Python invoke, 단 Phase-2 Hop3 는 test symbol 존재 후).
- `doc-section-schema`(CFP-28 strict) — **runnable-now**.
- `doc-frontmatter-schema`(CFP-28 strict, category closed_enum 포함) — **runnable-now**.
- RTM format header signature(AC 컬럼 `ac`/`id` exact ∧ 테스트 컬럼 `명명 테스트`/`test` 포함 ∧ 백틱 `test_*` 심볼) — **runnable-now**.
- 동일 Story 신규 lint(있으면) — **runnable-now**.

각 게이트는 저작시점 실행 가능성으로 정직 분류한다 — **runnable-now**(로컬 결정론 실행) vs **deferred-to-CI**(cross-repo state / runtime measurement / CI-only 환경 종속). deferred 게이트를 저작시점-covered 로 silent 주장 금지(capability boundary 정직 — 결정 6).

### 결정 2 — 저작시점 발동 + advisory 강제 tier(실-게이트 invoke 강제, fail-open 정직)

- **발동 시점**: producing lane(요구사항/설계/구현) 저작 완료 직후, **리뷰 lane 진입 전**(per producing lane).
- **강제 모델 = advisory prompt-mandate + lane-exit self-check**(day-1). mechanical hook(PreToolUse/lane-exit) 아님 — 저작시점 실행은 저작자 컨텍스트(현 Story 실 아티팩트 경로)를 요구하므로 lane-내부 프로세스로 배선. **최소 불변식**: 리뷰 판정이 실 게이트 실행을 **대체 금지** — self-gate 는 대상 게이트의 실 로직을 정확 Phase 모드로 **invoke**(narrow re-implementation 금지)해야 한다(A/B miss 실원인 = Phase-2 모드 미실행).
- **정직 천장**: advisory 채택 → fail-open 정직 명시(prompt 미준수 = 원 흐름 무차단, #15897 류 mechanical 강제 아님). merge-gate(7-tuple required)가 여전히 최종 fail-closed backstop. mechanical hook 승격 = future(pattern_count ≥ 2 재발 시 follow-up, ADR-084 precedent).

### 결정 3 — 결점 emit = A emit port 소비만(defect_finding), A/B 계약 0 수정

C 검출 결점 = `emit_dev_process_event.emit(event_type="defect_finding", ...)` 로 emit. INV-8b(blob-before-index) + always-on α + record-only non-blocking exit-0(ADR-115) 상속. C 는 A substrate 파일(계약 / append·query·emit·blob·redact 포트 / ledger) + B aggregator(`aggregate_dev_process_event.py`)를 **0개 수정**하며 emit port 를 **소비만** 한다. emit shape = B `compute_selfref_recurrence` 4-tuple{`defect_family`,`defect_type`,`time_to_detection`,`detecting_lane`} + `defect_id` 호환 필수.

### 결정 4 — detecting_lane honest-degrade(F1 정합), first-class 표현은 A upstream flag

self-gate emit 의 `detecting_lane` = **저작 lane_label**(요구사항/설계/구현 등 CLOSED lane_label enum 의 유효 멤버) + 저작시점 성격은 `time_to_detection`(ordinal 근사)으로 표현. 비-멤버 문자열(`authoring-self-gate`)을 **emit 하지 않는다** — append `_norm_enum(detecting_lane, _LANE_LABELS, None)` 이 `null`(None) 으로 coerce(신호 소실; `없음` 은 lane_label 전용 fallback, detecting_lane 은 nullable → `null`). first-class `authoring-self-gate` 표현(label-registry-v2 lane_label 추가 MINOR / capture-mechanism 신규 index 필드)은 **A 소관 upstream amendment 후보로 flag 될 뿐 C 가 A 계약을 수정하지 않는다**. honest-degrade 실 semantic 비용(O1) = B `_capture_subject` 가 리뷰 lane 5종만 'lane'·`구현-테스트`만 'gate' 로 매핑 → 그 외 저작 lane 은 'undetermined' 분류(기계 게이트 검출 성격 소실) — 이 비용이 first-class 표현(A-amendment) 판단 근거.

### 결정 5 — self-test born-GREEN 2축(독립 oracle + 대칭 fail-closed) — dogfood 필수

C self-gate 의 self-test(Phase 2)는 두 축을 명시 충족한다:

- **(a) 독립 oracle** — self-gate 자기 계산 출력을 self-match 하지 않고 **사전-고정 독립 fixture** 로 기대값 검증(CFP-2673 X⊆X tautology 금지).
- **(b) 대칭 fail-closed** — known-bad 아티팩트(RTM row 누락 / §4 위치 오배치 / AC 표 header 손상 / invalid category) → RED, known-good → GREEN 의 **양방향** discriminating(present-null 비대칭 금지 — CFP-2680). production-code mutation → self-test RED → revert → GREEN(diff empty) negative-control.

축별 completeness = enum(대상 게이트 집합) · grandfather(없음 — 신규 discipline) · null(detecting_lane nullable 대칭) 명시.

### 결정 6 — honest-ceiling: 저작시점 검출 축 vs review-tier 잔여 축 정직 declare

- **저작시점 검출(self-gate 강제)** = 구조/위치 conformance — RTM format / doc-section 위치 / AC header signature / frontmatter category enum. 이것이 A/B late-catch 3회의 클래스.
- **저작시점 미검출(review-tier 잔여)** = semantic claim-accuracy — substrate 사실 정확성(예: detecting_lane coerce 서술 정확성) / AC 의미 완결성 / test-semantic 완결성. 기계 게이트는 이 축을 검출하지 못한다(ac-traceability §(i) test-semantic 완전성 미강제 상속).
- **over-claim 금지(ADR-119)**: "결점 주입 완전 방지" / "exact detection" / "정밀 detecting_lane" / "guaranteed-unique defect_id" 주장 금지. self-gate PASS = 실 게이트 실행 **outcome ground-truth**(internal proxy 아님, ADR-119 2 판정면). 실행한 게이트·검출/미검출 항목 정직 보고.

### 결정 7 — dogfood 자기적용(C 자기 산출물에 저작시점 선실행)

C self-gate 를 **C 자기 아티팩트**(본 Story §5.3 AC 표 header signature / Change Plan §8 RTM / doc-section 위치 / ADR frontmatter category)에 리뷰 lane 진입 **전** 실행 → 통과를 실행-backed 로 확인(self-ref born-red / dogfood 재범 예방). C = self-gate 를 만드는 Story 이므로 자기 아티팩트가 born-GREEN 이어야 thesis 성립.

### 결정 8 — branch-protection 7-tuple 무변경, 신규 lint non-required day-1

C 가 shift-left 하는 게이트는 이미 7-tuple required — merge-gate 에서 최종 강제. 신규 required context **0**. 신규 lint(있으면) = **non-required day-1** hard-fail CI 채널(B/CFP-2684 선례) + `selftest-execution-liveness-inventory.yaml` channel alive enroll(bijection +1).

### 결정 9 — 경계 선언(disjoint) + 5th boundary 무저촉

- **C ⊥ #2684(ADR-154 hard-gate-self-verification)** — #2684 = 게이트가 자기 검출력을 검증(silent-green meta-gate, "게이트가 진짜 잡나?"). C = 올바른 게이트를 내 산출물에 저작시점 선적용("잡히는 게이트를 리뷰 전에 나에게 돌린다"). 같은 "self-" 접두 disjoint 축.
- **C ⊥ #2322(gate provenance)** — provenance ≠ 저작시점 self-적용.
- **C ⊥ B(#2688/ADR-156, 집계)** — C=결점 producer(defect_finding emit) / B=aggregator(C emit 소비). A OOS 표 상속: C=gate/verdict 판정 규칙·임계·차단·PASS/FAIL 의미, B=지표 산식·집계.
- **C ⊥ A(#2687/ADR-155, substrate)** — C=emit port 소비만, A substrate 수정 금지.
- **5th boundary 무저촉** — C self-gate PASS/FAIL(내 아티팩트의 게이트 통과 여부) ≠ 리뷰 lane verdict(review-verdict-v4) payload 재기록. C 는 defect_finding(semantic-evidence)만 emit — verdict payload 복제 아님(SoT 이중화 차단).

## 결과

### 긍정

- 구조/위치 conformance 결점(A/B late-catch 3회 클래스)이 리뷰 lane 진입 **전** 저작시점에 예방 → 리뷰 사이클 재작업 비용 절감, merge-gate late-catch 소거.
- 검출 결점 telemetry → A ledger emit → B self-ref 재발률 집계 → Epic #2686 자기개선 loop 폐쇄(C = defect_finding 채널의 첫 live producer 후보).
- dogfood 자기적용 + 독립 oracle self-test = self-ref born-red 재발 예방(8-11연속 이력 대응).

### 부정 / 비용

- advisory 강제(day-1) → fail-open(prompt 미준수 = 무차단). merge-gate backstop 의존. mechanical 승격은 future.
- detecting_lane honest-degrade → 저작 lane_label emit 시 B `_capture_subject` 'undetermined' 분류(기계 게이트 검출 성격 소실). first-class 표현 = A-amendment 대기.
- self-gate 는 semantic claim-accuracy 미검출(review-tier 잔여) — 정직 천장.

### 정직 천장(ADR-119)

- self-gate PASS = 실 게이트 실행 outcome ground-truth(proxy 아님). "결점 주입 완전 방지"·"exact detection" over-claim 금지.
- detecting_lane = 저작 lane_label 근사(정밀 authoring-self-gate 표현 무보장). `defect_id` = `sha256(family‖type‖normalized-location)` best-effort(normalized-location 안정성 무보장 — A 정직 천장 상속).
- Phase 1 = 설계 SSOT(declaration-only). 실 runner + wiring + lint + self-test = Phase 2. landing ≠ activation(ledger dormant → "self-gate 실행" ≠ "결점 ledger emit 성공" 구분).

## Amendment 1 (2026-07-20 KST, carrier CFP-2776) — advisory→mechanical 승격 정본화

**동기**: 결정 2 가 advisory prompt-mandate + "pattern_count >= 2 재발 시 mechanical 승격 MUST" 를 사전인가했다. CFP-2566(malformed enum value `user→derived` = SOURCE_ENUM ∉, **in-scope firsthand exemplar**) + tier-choice mislabel 3회(CFP-2748/2751/2753) 관찰 → **family >= 2 조건 충족** → 승격 실현. 본 Amendment 은 그 사전인가 clause 의 실현이다(신규 ADR 발명 아님).

**승격 내용**: 저작 repo(`mclayer/codeforge-internal-docs`)에 ac-traceability **Hop1 well-formedness** 축을 **blocking CI 게이트**(`.github/workflows/ac-schema-authoring-gate.yml`)로 배선 — 저작시점(Phase-1)에 §5.3 AC 레코드의 malformed-enum VALUE 를 fail-closed 로 차단. 전체 self-gate 를 PreToolUse hook 으로 승격한 것이 아니라, 가장 재발이 잦은 **Hop1 well-formedness 축을 저작 repo CI blocking 으로 승격**(scoped 실현). 재사용(재구현 0): wrapper `scripts/lib/ac_id.py` 를 internal-docs 로 byte-identical 복사 + drift-guard(pinned-ref static-parse-only semantic-value parity)로 parity 강제.

**정직 천장(결정 6 상속, over-claim 금지)**: 승격 축 = **malformed-enum VALUE**(구조 well-formedness)만. **tier-choice mislabel**(valid enum 값을 의미상 잘못 선택 — 예 normative-should-be-declared)은 저작시점 미검출(review-tier 잔여, ADR-145 AC-8 CEILING + RO-1). CFP-2776 자신이 방금 tier-choice(자기 AC normative→declared, cross-repo Hop3 non-resolvability)를 했고 이는 본 게이트가 잡지 **않는** 축의 living proof다. "결점 주입 완전 방지"·"exact detection" over-claim 금지 — self-gate PASS = 실 게이트 실행 outcome ground-truth(proxy 아님).

**telemetry 경계(advisory B)**: telemetry(defect_finding dev-process-event emit)는 여전히 advisory runner(`authoring_self_gate.py`) 소관이며, 본 blocking 게이트는 **enforcement-only**(defect_finding emit 안 함, review-verdict payload 복제 0 — 결정 9 5th boundary 무저촉).

**경계 무변경**: branch-protection 7-tuple 무변경(결정 8) — internal-docs 게이트는 별 repo. advisory `authoring_self_gate.py` 존치(defense-in-depth, 다른 시점 커버). wrapper `ac-traceability-matrix.yml` 무변경.

**ratchet 방향**: 대상 게이트 집합 확장(internal-docs Hop1 추가) + dogfood 자기적용 강화(carrier Story CFP-2776 자기 §5.3 에 저작시점 선실행 = live CI PASS 실증) — `is_transitional: false` 강화-only ratchet 정합(약화 아님). §결정 1-9 무supersede·무rewrite(append-only).

**carrier**: internal-docs Phase 2 PR(D1-D4 runner/게이트/drift-guard + pytest self-test, **선행 land**) + 본 wrapper Phase 2 PR(순수 prose ADR + plugin.json bump). 설계 SSOT = Change Plan `wrapper/change-plans/2026-07-20-cfp-2776-dogfood-story-ac-well-formedness-hop1-gate.md` @ `78a15a45`.

## 관련 파일

- [ADR-155](ADR-155-dev-process-observability-substrate.md) — substrate SSOT(emit port 소비, 의미 변경 0)
- [ADR-156](ADR-156-dev-process-metric-aggregation-escalation-feed.md) — 하류 aggregator(C emit consumer, 의미 변경 0)
- [ADR-145](ADR-145-ac-traceability-zero-drop-gate.md) — shift-left 대상 게이트(본문 무변경)
- [ADR-154](ADR-154-hard-gate-self-verification-forcing-function.md) — disjoint 경계(게이트 자기검증 ≠ 저작시점 self-적용)
- [ADR-119](ADR-119-research-before-claims.md) — 정직 천장 + 2 판정면
- `scripts/lib/emit_dev_process_event.py` — A emit port(C 결점 emit 유일 진입점, 소비만)
- `scripts/lib/authoring_self_gate.py` — 신규 self-gate runner(Phase 2 carrier)
- `docs/selftest-execution-liveness-inventory.yaml` — C self-test enroll +1(Phase 2)
- `docs/architecture/codeforge-family.md` — living-arch interfaces + data_flow + Open Decisions
- `archive/adr/ADR-RESERVATION.md` — row 158 append(dual-key 3-leg)
- Change Plan: `wrapper/change-plans/2026-07-16-cfp-2689-authoring-self-gate.md`(internal-docs, 설계 SSOT)
- Story: `wrapper/stories/CFP-2689.md`(internal-docs) §3/§7/§8/§11
