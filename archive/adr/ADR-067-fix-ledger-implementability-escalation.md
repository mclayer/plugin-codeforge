---
adr_number: 67
title: fix-ledger implementability escalation + max FIX overflow handling
status: Active
category: governance
date: 2026-05-13
is_transitional: false
carrier_story: CFP-526
parent_epic: CFP-525
supersedes: []
amends: []
amendment_log:
  - date: 2026-05-17
    amendment: 1
    cfp: CFP-842
    summary: "§결정 4 cross-lane RESET 정책 의 mechanical 정확도 carrier — fix-event-v1 v1.2 → v1.3 MINOR bump (affected_scope enum + affected_paths_with_depth array optional fields). cross-module / cross-repo / cross-plugin scope 결정의 mechanical evidence 보존 + broken-link/path 정정 FIX 시 over-correction regression chain (CFP-770 §8 CR-005→CR-006→CR-007 lesson) 직접 차단. fix-event-depth-scope-presence warning-tier lint (advisory only) 동반."
    scope_change: "ratchet 강화 only — 기존 §결정 4 Pause-and-resume 의미 invariant 변경 0. scope-aware mechanical input 추가로 RESET decision evidence trail 보존."
    breaking: false
    backward_compat: true
  - date: 2026-05-21
    amendment: 2
    cfp: CFP-1125
    summary: "disjoint invariant 보존 declare amendment (ADR-076 sunset 후 carrier 이전) — 본 ADR-067 RESET semantics (§결정 4) = Story progression layer (Story §10 FIX Ledger RESET? column) 의 영구 architectural invariant 명시. ADR-076 sunset (walker paradigm 전환) 후 disjoint invariant (ADR-067 RESET = Story progression layer / ADR-076 snapshot = Upgrade transaction layer, cross-pollinate 금지) 의 carrier 가 본 ADR-067 amendment + Wave 1 Story-3 imperative-walker-protocol-v1 codify 로 이전. walker step pause/resume ≠ Story §10 FIX Ledger RESET column 마커 명시."
    scope_change: "declarative invariant preservation only — 기존 §결정 1-7 의미 invariant 변경 0. is_transitional: false 유지 (영구 architectural invariant, 본체 sunset 아님). β2 audit (#1113) Anchor 5 LOSSLESS 판정 carrier."
    breaking: false
    backward_compat: true
  - date: 2026-06-30
    amendment: 3
    cfp: CFP-2480
    summary: "FIX ground-truth replay ↔ max-FIX 카운터 disjoint 명문화 + fix-event-v1 v1.3 → v1.4 MINOR carrier (reproducer_command + replay_verdict 2 optional field). Epic CFP-2476 E3. 신규 §결정 8 — (1) replay FAIL(falsified, 여전히 RED) = 닫기 게이트(close 거부)지 max-FIX 3/3 카운터 소비 아님 (disjoint); 무한거부 backstop = fix-attempt 카운터 (실제 fix 시도 = §10 Iter 증가가 max-FIX 소진, replay 재실행 자체는 카운터 무관). (2) replay fail-mode 2축 분리 — (A) replay-verdict 축(여전히 RED) = fail-closed(닫기 거부, degrade 없음, fail-open reject — 수정이 실제로 안 됨); (B) Codex-미가용 축(replay 실행 자체 불가) = lane-time fail_open_then_record_with_marker (영구보류=delivery 마비 회피, merge-time #7 fail-closed-then-bounded-degrade 와 disjoint). (3) flaky false-RED = ADR-070 §결정 D9 undetermined 분기 → max-FIX 부당소진 차단. (4) reproducer schema 제약(repo-relative 게이트/테스트 호출만, raw shell free-string 금지 = stored-command injection vector 차단, SecurityArch THR-E3-2) + base SHA-pin (reproduce-before-fix 결정론) + INV-SEC-1 (PII/secret/credential/private-path 금지 — §결정 7 reasoning_carryover security invariant 동형 확장). (5) cross-lane RESET (§결정 4) 무관 declare — replay falsified 는 RESET? column 마커 미발동."
    scope_change: "ratchet 강화 only — 기존 §결정 1-7 의미 invariant 변경 0. fix-event-v1 v1.4 additive-optional column (v1.1~v1.3 선례 4회 정합) + max-FIX disjoint 명문화(약화 0 — replay 가 카운터를 소비하지 않음을 명시해 정직성·수렴 양립). is_transitional: false 유지. ADR-058 §결정 5 sunset_justification N/A (강화 방향)."
    breaking: false
    backward_compat: true
  - date: 2026-08-16
    amendment: 4
    cfp: CFP-2985
    summary: "ADR-181(검증 정의역 결손 규범) 적용 carrier — 4 축. (1) `원인 판정` 값공간 2값 → 6값 확장(`요구사항`·`환경`·`설계-리뷰`·`구현-리뷰` 추가, fix-event-v1 v1.6 MINOR) ∧ §결정 1 max-FIX 카운터 trigger lane 2종(`설계-리뷰`/`구현-리뷰`) **불변** — 두 축이 disjoint 임을 명문화(라우팅 값공간 확장이 카운터 정의역을 확장하지 않는다). 실측 근거 = enum 밖 4축이 92행(15.6%) 실사용 — 이탈이 아니라 값공간 설계 결함의 증상. (2) #2957 데드락 해소 — §결정 2 3 trigger 정성 all-miss ∧ dual metric hit 조합에 verdict 부재였던 구멍을 `escalate_to_user` 로 fail-closed 부여(§결정 3 의 reset 전건 '3 trigger 모두 miss + dual metric 모두 miss' 를 침범하지 않는 여집합 배정). (3) FIX 닫기 조건에 **검증 정의역 선언(P/V)** 추가 — `replay_verdict`(검증 강도) 를 대체하지 않고 범위 축으로 병렬 확장(§결정 8 disjoint 유지). 정의 SSOT = ADR-181 §결정 1, 재진술 금지. (4) `fix-event-depth-scope-presence` 유령 선언 **철회** [철회됨 — 2026-08-16, Amendment 4 §9.4] — §결정 4 Amendment 1 이 mechanical enforcement 로 선언했으나 registry 112 entry 중 0 · script 0 · workflow 0(firsthand). 대응 라벨 `hotfix-bypass:fix-event-depth-scope` 는 label-registry-v2 에서 `Retired` 마킹(삭제 아님) + 본 Story 신규 게이트의 우회 채널로 **비채택** 명시. ★ 설계리뷰 FIX Iter 1 보강 — §9.4 처분 5 로 **철회의 문면 도달 범위**를 정직 선언: 본 ADR 밖에 같은 유령을 현재형으로 기술하는 live 문면이 9곳(fix-event-v1 5 · orchestrator-playbook 1 · story-page-structure 1 · label-registry-v2 2) 실재하며 각각 carrier(D-1/D-25/D-5/D-21)로 배정. 본 ADR 이 '철회 완료' 라 말할 수 있는 범위는 자기 문면 + `related_adrs` live 주장 1건 제거까지이고 나머지 9곳은 carrier merge 전까지 생존한다(over-claim 차단)."
    scope_change: "ratchet 강화 방향 — 값공간 확장은 additive(기존 2값 유효 유지, 소급 정규화 0), 카운터 trigger lane 정의역 무변경(확장 0), 데드락 해소는 verdict 부재 구멍을 fail-closed 로 채움(기존 verdict 배정 변경 0), 닫기 조건은 기존 게이트 위에 축 추가(대체 0). 유령 선언 철회는 실효 강제력 0 이던 문면의 제거이므로 통제 약화 0 — ADR-058 §결정 5 역-ratchet 정의역 밖. is_transitional: false 유지."
    reinterpretation: true  # ADR-167 §결정 1(b) — 순수 additive 아님. 축 (4) 가 Amendment 1 의 factual premise("fix-event-depth-scope-presence 가 본 ADR 의 mechanical enforcement 로 집행 중") [철회됨 — 2026-08-16, Amendment 4 §9.4] 를 affirmatively-FALSE(registry 0 · script 0 · workflow 0, firsthand)로 판정하고 그 문단의 지위를 "집행 사실 → 철회된 선언"으로 재규정(supersede-in-part)하며 §결정 4 본문 문면을 실제로 치환한다. 선례 동형 = ADR-064 Amendment(:179) — 선행 amendment 의 mechanical enforcement 단정이 affirmatively-FALSE 화 → 해당 clause supersede-in-part 시 reinterpretation: true. 축 (1)(2)(3) 은 순수 additive 이며 true 는 축 (4) 귀속. self-declared — parity lint 는 presence/type 만 검사하고 재해석 의미 판정은 리뷰 축이다(ADR-167 §결정 7 honest ceiling).
    breaking: false
    backward_compat: true
  - date: 2026-08-18
    amendment: 5   # provisional "5+" — 산술 next 는 4 이나 미머지 브랜치 cfp-2985-fix-telemetry 가 amendment_id 4 선점 active (ADR-RESERVATION row firsthand). D-5a/AC-14 merge 직전 재계산 대상 — 선착 확정 · 후착 재계산 의무 · 결번 허용 · 충돌 금지.
    cfp: CFP-3017
    summary: "reasoning_carryover 길이 규범 producer cap → receiver floor 전환 (Q-2 사용자 확정, Story CFP-3017 §5.5): §결정 5 의 '≤2 lines (≤200 chars 권장)' 길이 권장 문면과 계약 fix-event-v1 의 max_length: 50/100 hard cap 을 모두 무효화(§2.4 축 1·2 — 제3의 처분)하고 receiver_min_accept: unbounded(숫자 아닌 열거 술어) + truncation_policy: marked-truncation-required(head 보존 + tail 절단 + 필수 sentinel + 원본 포인터 + 원본 크기, 절단 주체 = 수신자, 침묵 절단 금지)로 대체. + §2.4 축 5(발화 조건) 계약 문면 채택 — 보존 허용을 발화 조건 무관으로 확대(의무 발동 조건 비-debate max-FIX 3/3 은 무변경). + §결정 7 위생 invariant 정의역 확장 — disputed_claims(유지) + invariant_summary(위치 유래 협착 해소) + transcript_ref(포인터 — 금지 축 = private absolute-path) + lane_evidence.transcript(carrier = ADR-031 Amendment 4 sibling). fail-fast 유지 · 자동 redact 금지. + §결정 7 노출면 근거 정정(AC-19 무조건) — 'public PR description 자동 mirror' 철회, 실측 = cross-repo Issue comment mirror(carryover 미도달), 살아있는 근거 = consumer repo 공개성 단독, §8.4 형 내부 정합화(§8.4 머리 어구 'public PR mirror surface' 도 정정 대상). + AC-17(b) scope 분리 정의역 선언 — §결정 5 anti-anchoring 문장('Full transcript verbatim 회피') 무변경, 그 정의역(금지 객체 = debate transcript / 금지 슬롯 = transcript_ref 포인터 필드)만 선언하고 verdict relay 전달면(dispatch packet)은 정의역 밖 — 면 분리(감사면 = §10 원장 + review-verdict artifact + §9 전량 보존·변경 0 / 전달면 = finding 본문 + base SHA + 재현 명령, 직전 판정값 생략 — 재명명 금지)."
    scope_change: "혼합 방향 정직 기술 — 'ratchet 강화 only' 아님: ① 위생 invariant 정의역 확장(3 sub-field + transcript) + 노출면 근거 정정 = 강화 ② 길이 규범 = 방향 전환(생산자 상한 문면 소멸 + 수신자 수용 술어 신설 — 집행 실적 0 인 cap[기계 소비자 0 실측]의 실태 정합화라 실효 약화 0, 단 규범 문면상 생산자 제약은 제거됨) ③ §2.4 축 5 = 보존 허용 조건 확대(계약 기실무 문면 채택 — ADR 로 재동기화하면 채널이 좁아져 본 Story 목적과 정면 역행) ④ §결정 5 anti-anchoring 문장 = 무변경 + 정의역 선언 additive. evidence-gated symmetric ratchet — 확대 방향 evidence = 계약 v1.2~v1.5 실무 문면 + Story §5.5 Q-2 사용자 확정 + fact packet F-2 실측."
    breaking: false
    backward_compat: true
related_stories:
  - CFP-526
  - CFP-842   # Amendment 1 — fix-event-v1 v1.3 depth-aware scope MINOR bump carrier
  - CFP-1125  # Amendment 2 — disjoint invariant 보존 declare (ADR-076 sunset 후 carrier 이전)
  - CFP-2480  # Amendment 3 — FIX ground-truth replay ↔ max-FIX disjoint + fix-event-v1 v1.4 MINOR carrier (Epic CFP-2476 E3)
  - CFP-2985  # Amendment 4 — 원인 판정 값공간 6값 + 카운터 lane disjoint + #2957 데드락 해소 + 정의역 선언 닫기 조건 + 유령 선언 철회
  - CFP-3017  # Amendment 5+ (provisional) — receiver floor 전환 + §2.4 축 5 계약 채택 + §결정 7 위생 확장·근거 정정 + AC-17(b) 정의역 선언 (Epic #3016 E-1)
related_adrs:
  - ADR-008
  - ADR-024
  - ADR-031  # Amendment 5+ sibling — lane_evidence.transcript(Q-1) 동일 형상 처분 carrier (ADR-031 Amendment 4, CFP-3017)
  - ADR-039
  - ADR-050   # parallel-epic-conflict-coordination (file disambiguation — ADR-050 number 가 multi-repo-story-key 와 share)
  - ADR-052
  - ADR-054
  - ADR-058
  - ADR-059
  - ADR-060   # ★ Amendment 4 정정 — Amendment 1 은 본 ADR-060 을 warning-tier registry entry 의 host 로 지목했으나 그 entry 는 실재 0 이었고(firsthand) 그 지목은 §9.4 에서 철회됐다. 본 ADR-060 이 관련인 실 근거 = evidence-check tier 체계 자체(현행 host = ADR-171 재제정판)
  - ADR-063
  - ADR-064
  - ADR-070   # Amendment 3 — FIX-close verify-before-trust (replay_verdict = §결정 D9 3-상태 disposition 정합, E3 sibling)
  - ADR-119   # Amendment 3 — §결정 10② close-time wire 실현 ("수정됨=반증 후 단언")
  - ADR-181   # Amendment 4 owner_adr — 검증 정의역 결손(P⊋V) 규범. 본 ADR 은 그 FIX 닫기 조건 축의 적용 carrier
  - ADR-171   # Amendment 4 — 신규 게이트 tier·registry host (warning-first + 승격 3-AND)
  - ADR-155   # Amendment 4 — _ROW_KEYS closed allow-list (root_cause_class 원장 키 착지면)
  - ADR-156   # Amendment 4 — 집계 feed. pattern_status uncomputable_missing_key DEFAULT 경로 해소 대상
  - ADR-171   # Amendment 5+ — 신규 검사 warning tier 탄생 원칙 (blocking required context 신설 0)
  - ADR-180   # Amendment 5+ — read_cost 잔여 리스크 축 (floor 는 하한이지 상한 아님 — 팽창 미차단 정직 라벨)
  - ADR-182   # Amendment 5+ — 면 분리(리뷰/증적 정의역 분리) 선례 anchor (AC-17(b) 구조적 은닉)
related_files:
  - skills/fix-ledger-schema/SKILL.md
  - docs/inter-plugin-contracts/fix-event-v1.md
  - docs/orchestrator-playbook.md
  - docs/evidence-checks-registry.yaml   # [철회됨 — 2026-08-16, Amendment 4 §9.4] Amendment 1 은 여기에 fix-event-depth-scope-presence warning-tier entry 가 실재한다고 단언했으나 실측 0 건이었다. 본 파일이 관련인 실 근거 = Amendment 4 가 append 한 fix-ledger-conformance entry (owner_adr ADR-181)
  - CLAUDE.md
mechanical_enforcement_actions: []  # carrier=#2985 expiry=2026-09-15 [repo=mclayer/plugin-codeforge] — ★ 고정 토큰 형식 (ADR-181 §결정 5 ③-dt (ii), 설계리뷰 FIX Iter 4). 앞의 세 토큰(carrier / expiry / [repo=...])만이 기계 판정 입력이며 이하 산문은 판정 정의역 밖이다 — 이 선언은 ADR-181 §결정 5 ③-dt (ii) PFX 선두 앵커 술어로 실제 배선됐다(설계리뷰 FIX Iter 4, 판별 행 18). ADR-181 §결정 5 ③ 면제 경로 — Amendment 4(원인 판정 6값 + 정의역 선언 닫기 조건 + 유령 선언 철회)의 기계 강제는 Phase 2 이행(신규 checker fix-ledger-conformance + workflow twin + discriminating self-test = D-7/D-7b/D-10). ★ 면제 경로이므로 사다리 (다)("그 경로가 workflow run: 줄에 등장") 는 평가되지 않는다 — 본 줄은 "돌아가는 검사가 있다" 를 주장하지 않으며 주장하는 것은 만기가 박혀 있다는 사실뿐이다(ADR-181 §결정 5 면제 천장 문단). ①(registry entry 존재) = 같은 PR 의 docs/evidence-checks-registry.yaml row fix-ledger-conformance 로 충족. 만기 경과 시 면제 경로를 잃고 사다리 경로만 남으므로 부적법 전환된다(§결정 5 ③-exp 경과 판정 leg). ★ Amendment 1 이 mechanical enforcement 로 선언했던 fix-event-depth-scope-presence 는 §9.4 에서 철회됐다 [철회됨 — 2026-08-16, Amendment 4 §9.4] — 본 빈 리스트는 그 철회 후의 정직 상태다.
---

# ADR-067: fix-ledger implementability escalation + max FIX overflow handling

## 상태

Active (2026-05-13). carrier_story = CFP-526 (Epic-FIX-ESCALATION-prevention Wave 1, doc-only fast-path ADR-054). parent_epic = CFP-525.

## 컨텍스트

mctrader-hub Story MCT-150 (Stage 2 첫 Story, uploader hardening, 5 SP) Phase 2 진행 중 design-review ↔ code-review FIX cycle **4회** 발생 (max counter 3/3 도달 + ESCALATE Option A RESET, 2026-05-13 KST). 매 FIX 마다 이전 fix 의 정합 적용 결과로도 다음 review 가 새 dimensional finding 을 catch. 13 곳 wording desync (`hard_floor_breached` ↔ impl `hard_floor_blocked`) silent bug surface → caller (MCT-152 collector) MANUAL_GATE escalation path 누락 + RPO=0 invariant violation risk.

CFP-525 (Epic-FIX-ESCALATION-prevention) brainstorm spec 합의 framing:

- **H6 (systemic root cause)**: DesignLane 내부 adversarial debate 부재로 인한 convergence quality 미달. single-pass ArchitectAgent + sequential review topology 자체가 boundary completeness gap / dimensional extension anti-pattern / handoff wording drift 의 증상 surface.
- **RC#3 + RC#5 = remediation tracks (본 ADR scope)**: fix-ledger RESET 정책 명문화 + implementability reassessment 절차 + reasoning carryover field.

본 ADR 의 motivation 3 vector:

1. **사용자 directive (2026-05-13)** verbatim: "Arch ↔ design fix 3회 초과 시 타협이 어려웠던 부분을 기준으로 요건이 구현 가능한 수준인지 보수적으로 평가하도록 하고 필요한 경우 사용자에게 escalation 해야함." → reactive ESCALATE 패턴 → prescriptive deterministic trigger 전환.
2. **Researcher unknown unknown #1 — Information loss between FIX iterations**: ArchitectPL re-spawn 시 직전 finding 만 input, 전체 transcript 비주입 = architectural amnesia. §10 row reasoning carryover 부재가 직접 carrier.
3. **Codex D6 적대적 검토 발견**: full transcript verbatim 회피 (이전 framing 고정 차단). 3-part 구조 (invariant summary + disputed claims + transcript ref) 가 reasoning trail 보존 + 새 framing 가능성 양립.

본 ADR 의 placement context:

- **ADR-039 §결정 3 (Orchestrator §10 monopoly)** 와 정합. `reasoning_carryover` field 추가는 schema MINOR bump — append writer 주체 (Orchestrator) 영향 0.
- **ADR-059 §결정 3 (debate-protocol-v1 reasoning carryover via `debate_artifact_ref`)** 와 disjoint scope. debate 발동 FIX 시 = `debate_artifact_ref` / 비-debate FIX (max FIX 3/3 implementability reassessment) 시 = `reasoning_carryover`. EC-1 명세.
- **ADR-052 (Codex Proactive Check 6 touchpoints)** 와 의미 boundary 분리: 본 ADR = post-failure escalation (FIX 3/3 후), ADR-052 = pre-failure proactive check (Story §1-§6 완료 직후). 분리 근거 = trigger timing + carrier mechanism + verdict format 3 axis 모두 disjoint.
- **ADR-064 (결정 원칙 mandate)** 와 정합. 본 ADR 본문 forbid-list 8 어휘 (`임시 / 단계적 / 일단 / 우선[시간] / 잠정 / 가벼운 / minimal viable / quick win`) 0건 — 영구 governance 정책 선언.

## 결정

### 결정 1 — max FIX 3/3 도달 시 deterministic implementability reassessment trigger

Story 진행 중 동일 lane (`설계-리뷰` / `구현-리뷰`) FIX count 가 RESET 마커 이후 3 회 도달 (`current_count == 3`) AND 다음 FIX event 보고 수령 시점 (`current_count → 4` 진입 임박):

Orchestrator 는 **추가 FIX iteration 진입 이전** 다음 의무:

1. `codeforge:fix-ledger-schema` skill 호출 (max FIX 3/3 도달 패턴 매칭 확인)
2. ArchitectPLAgent re-spawn — implementability reassessment 의무 packet 전달
3. ArchitectPL verdict 수령 전까지 4번째 FIX iteration 자동 진입 금지 (reactive 패턴 차단 — ESCALATE Option A RESET 만으로 결정 위임 안 됨)

Trigger 범위 = `설계-리뷰` / `구현-리뷰` 2 lane (max_fix_per_cycle = 3 lane). `구현-테스트` / `보안-테스트` (max = ∞) 는 본 trigger 영역 외.

### 결정 2 — escalation 의무 trigger 3종 명문화

ArchitectPL implementability reassessment 수행 중 다음 3 조건 중 1 이상 hit 시 verdict = `escalate_to_user` 의무:

- **(i) design granularity inadequate**: ESCALATE root cause 가 "boundary 가 잘못 잡혀 동일 boundary 재시도가 무의미" — 3 FIX cycle 동안 동일 axis 의 결함이 surface area 만 다르게 재발 (예: mctrader-hub MCT-150 의 hard_floor wording 13 곳 ↔ MANUAL_GATE caller path 누락 패턴).
- **(ii) cross-module invariant 위반 without convergence path**: 3 FIX cycle 누적 P1 finding 의 영향 module 수 ≥ 3 (`cross_module_propagation`) AND convergence path (=동일 boundary 내 fix 로 해소 가능한 path) 미식별. mctrader-hub MCT-150 의 RPO=0 invariant + hard_floor wording SSOT 가 대표 사례.
- **(iii) DeveloperPL ↔ ArchitectPL N+1 round divergence 유지**: 직전 N rounds 의 양 PL verdict packet `pl_recommendation` divergence ≥ 2회 AND 다음 round 에서도 같은 axis 의 disagreement 가 reduce 되지 않을 것이 예측됨 (= 동일 axis 의 reviewer divergence 가 anchor 별도 ≥ 2회 — ADR-059 `anchor_recurrence_count` 패턴 정합).

3 trigger 평가는 **dual metric 정량 보조** (보수적 평가 SSOT — 결정 6 참조):

- `cumulative_P0 >= 2` OR `cumulative_P1 >= 5` OR `reviewer_divergence_count >= 2` 시 trigger (i/ii/iii) 후보 강격상.
- 정량 metric hit + 정성 trigger evaluation 결합 = escalation 의무.

3 trigger 모두 miss + 정량 metric 모두 miss 시 verdict = `reset_and_redesign` 가능 (결정 3).

### 결정 3 — ArchitectPL 재량 RESET vs escalation 결정 권한

max FIX 3/3 도달 + ArchitectPL reassessment 완료 시:

- 결정 2 의 3 trigger 모두 miss + dual metric 모두 miss = "보수적 평가 결과 현 boundary 재시도 가능 + 다음 round convergence 가능" → ArchitectPL verdict = `reset_and_redesign` 가능.
- Orchestrator 는 §10 row 의 `RESET?` column 에 `RESET <lane>` 마커 + ArchitectAgent 재spawn (Change Plan 갱신) 진행.
- ArchitectPL verdict packet 의 `reasoning_carryover` 3-part 의무 동반 (escalate / reset 무관, 이전 framing 고정 차단 forcing function — 결정 5).

### 결정 4 — cross-lane RESET 정책 — Pause and resume

implementability reassessment 진행 중 (또는 사용자 escalation 대기 중) cross-lane (보안-테스트 또는 구현-테스트) 신규 FIX 발생 시:

**채택: Pause-and-resume**. 현 escalation 일시 pause + 보안 (또는 구현-테스트) FIX 선행 수행 → 해당 lane PASS 후 escalation 재개. `RESET?` column 에 `"cross-lane-pause:<lane>"` 마커 명시 (예: `"cross-lane-pause:보안-테스트"`).

거부 옵션 — Bundled escalation: 보안 FIX 도 escalation packet 에 통합 → 사용자 결정 시 종합 검토. 거부 사유 (CFP-526 §7 ArchitectPL 채택):
- cross-lane reasoning bundling 시 reasoning_carryover SSOT 단일성 손상 (1 lane reasoning chain per row invariant 위반)
- 사용자 decision noise 증가 risk (multi-lane finding mix → 결정 영역 분산)
- `RESET?` column 시맨틱 확장 복잡도 증가 (`"cross-lane-bundle:<lane>"` value family 도입 필요)

Pause-and-resume 의 latency trade-off 는 acceptance — escalation 자체가 사용자 dialog 대기 시점이므로 cross-lane FIX latency 가 직접 critical path 영향 0.

#### Amendment 1 (CFP-842, 2026-05-17) — depth-aware scope mechanical 정확도 carrier

본 결정 4 의 cross-lane RESET 결정 input 의 mechanical evidence 보존 carrier — fix-event-v1 v1.2 → v1.3 MINOR bump 2 optional 필드 신설:

- **`affected_scope`** enum (`single-file` / `cross-module` / `cross-repo` / `cross-plugin`) — Orchestrator 가 FIX root cause 판정 직후 결정. RESET 결정 영향 표:

  | affected_scope | ArchitectPL 행동 |
  |---|---|
  | `single-file` | 동일 lane FIX iter 유지 (RESET 회피) |
  | `cross-module` | cross-lane RESET 적극 검토 (본 §결정 4 Pause-and-resume 발동 후보) |
  | `cross-repo` | cross-lane RESET + sibling sync 영역 진단 (ADR-010 정합) |
  | `cross-plugin` | cross-lane RESET + marketplace atomic invariant 진단 (ADR-063 정합) |

- **`affected_paths_with_depth`** array of `{path, depth}` — broken-link / path 정정 FIX 영역 한정 의무. `depth` = repo root 기준 dir depth. 정정 규칙 적용 범위 (예: `depth >= 2 then path adjust = '../../'`) 의 mechanical reasoning trace 보존 — CFP-770 §8 CR-005→CR-006→CR-007 over-correction regression chain lesson directly carrier (depth 정보 부재가 directly carrier 였음).

**ratchet 강화 only**: 본 §결정 4 의 Pause-and-resume 의미 invariant 변경 0 — mechanical input 추가만. backward-compat 100% (2 optional field, 기존 9-column row null 또는 column 생략 valid).

**mechanical enforcement**: ★ **없다 — 본 선언은 Amendment 4(CFP-2985) 에서 철회됐다.** 아래는 철회 기록이다.

> **[철회됨 — 2026-08-16, Amendment 4 §9.4]** Amendment 1(CFP-842) 은 이 자리에서
> `fix-event-depth-scope-presence` warning-tier lint 를 "mechanical enforcement" 로 **선언했고**,
> `hotfix-bypass:fix-event-depth-scope` label 부착 PR 을 lint skip + audit comment 채널로 **기술했으며**,
> SSOT 를 `docs/evidence-checks-registry.yaml` 로 **지목했다**. 그 선언은 실물과 대응하지 않았다 —
> firsthand 실측: registry entry **0** · script **0** · workflow **0** (Amendment 4 시점 registry 113 entry 전수).
> ⇒ `affected_paths_with_depth` 누락은 **어떤 기계 검사로도 적발되지 않으며**, 이 필드의 준수는
> 리뷰 판정 축이다(`declared`). 이 문단을 "검사가 있다" 의 근거로 인용하지 말 것.
> 대응 라벨은 `label-registry-v2.md` 에서 `Retired` 마킹 대상이다(삭제 아님 — Phase 2 D-21).

cross-ref:
- [`docs/inter-plugin-contracts/fix-event-v1.md`](../inter-plugin-contracts/fix-event-v1.md) v1.3 §2 Schema + §3 항목 (affected_scope / affected_paths_with_depth)
- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) §6.7 v1.3 depth-aware scope 의무
- [`templates/story-page-structure.md`](../../templates/story-page-structure.md) §10 column expansion

### 결정 5 — `reasoning_carryover` field 3-part structured 구조 + fix-event-v1 v1.2 MINOR bump

fix-event-v1 v1.1 → v1.2 MINOR bump — 9 번째 trailing optional column 추가:

```yaml
reasoning_carryover:
  type: "object | null"
  required: optional        # v1.2 신규, backward-compat 보장 (CFP-526)
  introduced_in: "1.2"
  schema:
    invariant_summary:
      type: string
      constraints: ["≤2 lines (≤200 chars 권장)"]
      description: "이번 FIX cycle 의 '타협 불가' axis 요약 (예: 'RPO=0 invariant + hard_floor wording cross-module SSOT')"
    disputed_claims:
      type: "list[string] | string"
      description: "직전 round 에서 합의되지 않은 핵심 disagreement 항목. 형식 자유 (list 또는 free-form)."
      security_invariant: "PII / secret / credential 포함 금지 — SecurityArchitect deputy SSOT (§7.5 정합)"
    transcript_ref:
      type: string
      description: |
        - debate 발동 시: Story §9 section anchor link 형식 (예: `#debate-transcript-F-001`) — 단 본 field 는 비-debate FIX 영역, debate_artifact_ref 와 disjoint
        - 비-debate FIX 시: Story §9 section anchor link (예: `#fix-3-architectpl-reassessment`) 또는 직전 verdict packet evidence path
        Full transcript verbatim 회피 (Codex D6 — 이전 framing 고정 차단)
  cross_ref:
    - docs/adr/ADR-067-fix-ledger-implementability-escalation.md (본 ADR §결정 5)
    - docs/inter-plugin-contracts/debate-protocol-v1.md (debate_artifact_ref consumer — disjoint scope)
```

3-part 구조 채택 근거 (옵션 a structured YAML keys over 옵션 b free-form 3-paragraph markdown):

- **검색 / diff 용이**: machine-readable keys 가 향후 lint / KPI extraction 의 forcing function (예: cross-Story disputed_claims pattern 통계).
- **migration 용이**: 7-column / 8-column / 9-column 3종 row 공존 (backward-compat) 시 9 번째 column parse 가 키 기반 deterministic.
- **결정 영역 일관성**: 본 codeforge 의 다른 contract field (예: `debate_artifact_ref` link 형식, `mechanical_self_check_passed` bool) 가 모두 structured — 패턴 정합.

`debate_artifact_ref` (v1.1, CFP-391) 와 `reasoning_carryover` (v1.2, 본 ADR) **disjoint scope**:

- debate 발동 FIX 시 = `debate_artifact_ref` 채움 + `reasoning_carryover = null` (debate transcript 가 이미 reasoning trail 보존)
- 비-debate FIX (max FIX 3/3 implementability reassessment) 시 = `debate_artifact_ref = null` + `reasoning_carryover` 의무
- 일반 FIX (max FIX 3/3 미도달, debate 미발동) = 양 field 모두 `null` 또는 column 생략 (backward-compat)

Producer = Orchestrator (FIX Ledger writer monopoly 유지 — CFP-32). ArchitectPL verdict packet 으로 reassessment 결과 전달 → Orchestrator 가 §10 row append.

### 결정 6 — ArchitectPL "보수적 평가" dual metric SSOT

사용자 directive verbatim ("타협이 어려웠던 부분을 기준으로 요건이 구현 가능한 수준인지 보수적으로 평가") 의 정량 SSOT:

**Dual metric** 채택 (단일 metric 의 cross-module gap evidence 누락 risk 회피):

- **Metric A — cumulative finding severity**:
  - `cumulative_P0 >= 2` (RESET 이후 누적 P0 count) → escalation trigger 후보 격상
  - OR `cumulative_P1 >= 5` (RESET 이후 누적 P1 count) → boundary completeness gap pattern signal
- **Metric B — reviewer divergence count**:
  - `reviewer_divergence_count >= 2` (동일 anchor 가 ≥ 2회 review 에서 divergent verdict — ADR-059 `anchor_recurrence_count` 패턴 정합)

Metric A OR Metric B 1+ hit = 결정 2 의 3 trigger (i/ii/iii) 후보로 강격상. 정성 trigger evaluation + 정량 dual metric 결합 → escalation 의무.

**Dual metric threshold corroboration evidence** (mctrader-hub MCT-150 §10 FIX trail, 2026-05-13):

| row | lane | finding 분포 | 누적 P0 | 누적 P1 | reviewer divergence |
|---|---|---|---|---|---|
| row 1 | design-review FIX#1 | P0=0 / P1=3 | 0 | 3 | 0 |
| row 2 | code-review FIX#2 | P0=2 / P1=3 (양 reviewer 동일 교차 일치) | 2 (≥2 threshold **hit**) | 6 (≥5 threshold **hit**) | 1 |
| row 3 | code-review FIX#3 | P0=NEW-1 + P1=NEW-1 (dimensional extension) | 3 | 7 | 2 (≥2 threshold **hit**) |
| row 4 | ESCALATE | P1=NEW-2 + P1=NEW-3 | 3 | 9 | 2 |

row 2 시점 = Metric A (cumulative P0≥2 AND cumulative P1≥5) 동시 hit. row 3 시점 = Metric B (reviewer_divergence_count≥2) 추가 hit. row 4 ESCALATE Option A RESET 도달 이전 row 2-3 시점에서 dual metric 충족 — 본 ADR §결정 1 deterministic trigger 가 land 되었다면 row 4 진입 이전 ArchitectPL implementability reassessment + 사용자 escalation 발동 가능했음. 본 case study evidence 가 dual metric threshold 의 ex-post calibration 근거.

거부 후보 metric:

- **(b) 영향 file count**: surface area proxy 일뿐, 동일 boundary 내 mechanical mirror (예: 13 곳 wording desync) 와 cross-boundary propagation 구분 불가.
- **(c) cross-module propagation 깊이**: 결정 2 (ii) trigger 정성 평가에 이미 흡수 — 정량 redundancy 회피.

### 결정 7 — `reasoning_carryover` security invariant

`disputed_claims` sub-field 본문에 PII / secret / credential / API key / private path 포함 금지 (SecurityArchitect SubAgent SSOT — §7.5 민감 데이터 분류 정합).

근거: §10 FIX Ledger = public PR description 에 자동 mirror (`fix-ledger-sync.yml` Action) — secret 노출 surface. ArchitectPL verdict packet 작성 시 사용자 escalation 대비 disputed_claims sub-field 의 모든 entry 가 design vocabulary level 로 abstraction 유지 의무.

위반 사례 발견 시 Orchestrator append 의무 차단 (자동 redact 금지 — fail-fast 후 ArchitectPL re-author).

## 결과

### Direct outputs

- **`docs/inter-plugin-contracts/fix-event-v1.md`** v1.1 → v1.2 MINOR bump — `reasoning_carryover` optional 9 번째 column 추가 + amendment_log row append + schema sub-section.
- **`skills/fix-ledger-schema/SKILL.md`** 본문 4 bullet 확장 — implementability reassessment 5-step (current_count==3 감지 / ArchitectPL spawn / verdict 수령 / RESET vs escalate / §10 append) + escalation 3 trigger 인용 + cross-lane RESET 정책 (Pause-and-resume) + `reasoning_carryover` field 설명.
- **`docs/orchestrator-playbook.md`** §6.4 보강 — `reasoning_carryover` schema + Orchestrator append 절차 / §6.5 보강 — ArchitectPL reassessment 절차 + dual metric / §6.6 보강 — parallel diagnosis 후 max FIX 3/3 trigger 자동 prepend.
- **`CLAUDE.md`** "FIX 루프" 단락 1 줄 cross-ref append (cap ≤320 정합).
- **`CHANGELOG.md`** Unreleased entry — fix-event-v1 v1.2 / ADR-067 신설 / skill 본문 확장 / playbook §6.4-6.6 보강.
- **`.claude-plugin/plugin.json`** + **`marketplace.json`** (sibling repo) — version 5.31.0 → 5.32.0 MINOR bump (atomic invariant ADR-063 정합).

### Indirect impact

- **Wave 4 (CFP-530, ADR-059 Amendment 1)**: debate-protocol-v1 §convergence_quality_invariant 정의 시 본 ADR §결정 5 의 `reasoning_carryover` ↔ `debate_artifact_ref` disjoint scope 가 prerequisite 정합 anchor.
- **codeforge family sibling sync**: kind:registry (fix-event-v1) = sibling sync 면제 (CLAUDE.md "Inter-plugin Contract" 단락 / ADR-010 정합). 단 sibling plugin (review / design / develop / pmo / test) 의 `templates/*.md` 본문이 fix-event-v1 v1.1 schema verbatim 인용한 경우 v1.2 column 갱신 필요 — DesignReview lane 검증 의무 (false closure 차단).
- **mctrader-hub MCT-151+**: codeforge upgrade 후 동일 failure class (4 FIX ESCALATE Option A pattern) 재발 감소 KPI signal — Epic-FIX-ESCALATION-prevention 의 acceptance criteria #5.
- **KPI measurement framework**: 후속 별도 carrier (CFP-525 acceptance criteria #4) 에서 본 ADR `reasoning_carryover` field 의 cross-Story 통계 (disputed_claims 빈발 axis / reviewer_divergence 빈발 anchor) extraction 의무. evidence-checks-registry-v1 entry 후보.

### Alternatives 검토 (3+ 검토)

대안 1 — **blanket auto-escalate at FIX 3/3**: max FIX 3/3 도달 = 즉시 사용자 escalation, ArchitectPL 재량 절차 0.

- 거부 사유: 사용자 escalation surface 과다 증가 — 일반 trivial FIX cycle (3 cycle 내 mechanical convergence 가능) 도 escalate → user attention 낭비. dual metric 정량 + 정성 trigger 평가가 reactive auto-escalate 대비 false-escalation rate 감소.

대안 2 — **PL 재량 only (현행 ESCALATE Option A RESET pattern)**:

- 거부 사유: 본 Story 의 직접 카탈리스트 사례 (MCT-150 4 FIX cycle). reactive 패턴 만으로는 silent bug 누적 risk + reasoning loss 누적 — 사용자 directive verbatim 의 "보수적 평가" SSOT 정량화 의무 미충족.

대안 3 — **사용자 immediate AskUserQuestion at FIX 1**:

- 거부 사유: codeforge governance 정합성 침해. FIX 1-2 cycle 은 normal convergence path — ArchitectPL synthesizer 책무 선행. 결정 원칙 (ADR-064) Trace 2 Rule 5 "AskUserQuestion 범위 제한 — 가치 판단 / 미공개 컨텍스트 2 종 한정" 정합 위배.

대안 4 — **ADR-052 Amendment 으로 흡수 (별도 ADR 미신설)**:

- 거부 사유 (Codex D9 권고 정합): ADR-052 = pre-failure proactive check (Story §1-§6 직후 6 touchpoint). 본 ADR = post-failure escalation (FIX 3/3 후 reassessment). trigger timing / carrier mechanism / verdict format 3 axis 모두 disjoint — Amendment 시 ADR-052 영역 의미 confusion + dimensional extension anti-pattern signal. 별도 ADR 분리가 governance 명료성 보존.

### 중복성 검토 결과 (Codex D9 권고 gate)

ADR-052 (Codex Proactive Check) / ADR-064 (결정 원칙) / ADR-039 (subagent default) 의 의미 중복 검증:

- **vs ADR-052**: 분리 (위 대안 4 거부 사유 동일). pre-failure proactive vs post-failure escalation 의 trigger / mechanism / format 3 axis disjoint.
- **vs ADR-064**: 분리. ADR-064 = Orchestrator 의 결정 제안 시점 normative (`Trace 1-4`). 본 ADR = ArchitectPL 의 max FIX 3/3 시 verdict format normative — 다른 agent + 다른 lifecycle phase + 다른 carrier.
- **vs ADR-039**: 정합 (충돌 없음). ADR-039 §결정 3 Orchestrator §10 monopoly invariant 유지 — `reasoning_carryover` field 추가는 schema MINOR bump, append writer 영향 0.

세 ADR 모두 본 ADR 의 related_adrs frontmatter 에 명시 (cross-ref forcing function).

## 해소 기준

N/A — permanent policy (`is_transitional: false`).

근거 (ADR-058 §결정 7 정합):

- 본 ADR 은 governance carrier 영구 정책 — fix-event-v1 schema 의 reasoning carryover invariant 는 codeforge 의 FIX 루프 reasoning preservation contract 의 SSOT.
- 향후 amendment 시 ADR-058 §결정 5 (amendment justification 의무) 정합 — `sunset_justification` 미적용 (transitional 아님), 대신 amendment scope 명시 의무.
- recursive sunset 회피 패턴 정합 사례: ADR-064 (결정 원칙 mandate), ADR-058 (sunset criteria mandate), ADR-013 (codeforge family dogfood-out), ADR-016 (marketplace registration), ADR-042 (agent model selection).

## Amendment 2 (CFP-1125 carrier) — walker paradigm 전환 후 disjoint invariant 보존 declare

본 ADR-067 RESET semantics (§결정 4) = Story progression layer (Story §10 FIX Ledger 의 `RESET?` column). CFP-1125 walker paradigm 전환 후에도 본 disjoint invariant (ADR-076 §결정 4 verbatim, "ADR-067 RESET = Story progression layer / ADR-076 snapshot = Upgrade transaction layer, cross-pollinate 금지") 는 본 ADR-067 본체에 영구 보존.

ADR-076 sunset 후 disjoint invariant 의 carrier = 본 ADR-067 amendment + Wave 1 Story-3 imperative-walker-protocol-v1 codify 안 명시 (walker step pause/resume ≠ Story §10 FIX Ledger RESET column 마커).

- **본 disjoint invariant 는 sunset 대상 아님** — `is_transitional: false` 유지 (영구 architectural invariant)
- ADR-076 sunset 후 declarative anchor 이전 = 본 ADR-067 amendment + walker schema ADR

**cross-ref**: [CFP-1125](https://github.com/mclayer/plugin-codeforge/issues/1125) + [β2 audit (#1113)](https://github.com/mclayer/plugin-codeforge/issues/1113) Anchor 5 LOSSLESS 판정.

### sunset_executed (CFP-1186, 2026-05-22) — disjoint invariant carry 영역 한정

**상태**: disjoint invariant carry 영역 Sunsetted — ADR-076 §결정 4 verbatim "ADR-067 RESET = Story progression layer / ADR-076 snapshot = Upgrade transaction layer, cross-pollinate 금지" 의 ADR-076 참조 sibling carrier 역할 이 imperative-walker-protocol-v1 으로 lossless carry 완료됨.

carry 증거 (β2 audit Anchor 5 LOSSLESS 확인):
- imperative-walker-protocol-v1 안 walker step pause/resume ≠ Story §10 FIX Ledger RESET column 마커 명시 — disjoint invariant 동일 의미로 carry
- ADR-076 sunset 후 disjoint invariant declarative anchor = 본 ADR-067 amendment (Amendment 2) + walker schema ADR 양 쪽 보존

**is_transitional 무변경**: `false` 유지 (ADR-067 본체 §결정 1-7 RESET semantics = Story progression layer 의 영구 architectural invariant. 본체 sunset 아님).

**본 sunset 영역 한정**: ADR-076 §결정 4 sibling carrier role 만 (= disjoint invariant 의 "ADR-076 쪽 선언 역할" carry). ADR-067 본체 §결정 1-7 FIX-loop RESET semantics 영역은 sunset 대상 아님 — 계속 유효.

**본 ADR 본문 삭제 금지**: Sunsetted = 해당 영역의 carry 완료 선언. 본문은 historical record 로 영구 보존.

## Amendment 3 (CFP-2480 carrier) — FIX ground-truth replay ↔ max-FIX disjoint + fix-event-v1 v1.4 MINOR

Epic CFP-2476 E3 (Codex 실행형 정책 게이트 팩 + FIX ground-truth replay). FIX "수정됨" close 를 원 reproducer 재실행 반증(외부 Retest)으로 강제하는 mechanism 이 본 ADR 의 max-FIX 카운터(§결정 1~3)와 어떻게 상호작용하는지 codify. 신규 §결정 8 추가 only — D1-D7 + Amendment 1/2 본문 의미 변경 0건.

### 결정 8 — FIX replay ↔ max-FIX 카운터 disjoint + replay fail-mode 2축 + reproducer security invariant

#### 8.1 replay FAIL ↔ max-FIX 카운터 disjoint (핵심)

FIX "수정됨" 닫기 = 원 finding 을 정당화한 reproducer 재실행 GREEN(외부 Retest, ADR-119 §결정 10② close-time wire) 반증 후에만 성립 (fix-event-v1 v1.4 `replay_verdict == PASS`). replay 가 여전히 RED(`falsified`)일 때 이는 **max-FIX 3/3 카운터를 소비하지 않는다** — replay 는 "닫기 전 검증 게이트" 지 새 FIX iteration 이 아니다.

- **disjoint 의미**: replay `falsified` = "현 iter 미완결(닫기 거부)" 이지 max 3/3 진입(`current_count → 4`, §결정 1 trigger) 이 아니다. replay 재실행 자체는 §10 row Iter 를 증가시키지 않는다.
- **무한거부 backstop = fix-attempt 카운터**: replay 가 반복 `falsified` 면 무한루프 위험은 max-FIX 가 아니라 **실제 fix 시도** (새 §10 row Iter)가 backstop 한다. DeveloperPL 이 새 fix 를 시도(새 Iter append)할 때마다 max-FIX(설계-리뷰/구현-리뷰 lane)가 소진되고, 그 카운터 3/3 도달 시 §결정 1~3 implementability reassessment 가 정상 발동한다. replay 게이트는 닫기 정직성만 담당.
- **§결정 1~3 무손상**: max-FIX trigger 범위(설계-리뷰/구현-리뷰 2 lane), escalation 의무 3종(§결정 2), RESET vs escalation 권한(§결정 3) 본문 의미 변경 0. replay 는 그 카운터의 입력도 출력도 아닌 disjoint axis (close-gate).

**사용자 trade-off 정합 (req §5.6 #2)**: disjoint = 정직성↑ but 무한거부 위험 / 카운터 소비 = 수렴 강제 but 정직성 약화. 채택 = **disjoint** (정직성 우선, §1 "주장 아닌 실측") + safety valve = fix-attempt 카운터(max-FIX)가 별도 채널로 수렴 강제. replay N회 `falsified` 반복 시 사용자 escalation 은 max-FIX implementability reassessment(§결정 2) 가 흡수.

#### 8.2 replay fail-mode 2축 분리 (InfraOp refinement)

replay 의 fail 은 두 disjoint 축이다 (혼동 시 게이트 hollow):

| 축 | 의미 | disposition | 근거 |
|---|---|---|---|
| **(A) replay-verdict 축** | 원 reproducer 가 여전히 RED (수정이 실제로 안 됨) | **fail-closed (닫기 거부), degrade 없음** (`replay_verdict: falsified`) | replay 본질 = "주장 아닌 실측"(§1). fail-open 하면 게이트 자체 hollow = #2322 self-attest 위조면 동형 hole → fail-open reject |
| **(B) Codex-미가용 축** | replay 실행 자체 불가 (Codex CLI/sandbox 미가용) | **lane-time `fail_open_then_record_with_marker`** (`[fix-replay-fallback: fail-mode=codex_unavailable, disposition=open]`) | 영구보류 = delivery 마비. lane-time ≠ 마지막 방어선 (ADR-070 Amd10/11 §D8/D9 동형) |

merge-time #7 의 `fail_closed_then_bounded_degrade`(ADR-070 §결정 D7)와 다름 — **#7 의 degrade 는 (B)축(Codex 미가용)용** 이고 **FIX replay (A)축은 degrade 대상이 아니다** (수정이 실제로 안 됨 → 닫기 거부가 정답, degrade 시 부당 close).

#### 8.3 flaky false-RED → undetermined (max-FIX 부당소진 차단)

replay 가 flaky(다회 결정론 미충족 또는 mixed)면 `replay_verdict: undetermined` (ADR-070 §결정 D9 undetermined 분기 동형) — quarantine 보류. 1회 GREEN close 금지(false-GREEN = §1 목적 정면 훼손 최위험) + mixed quarantine(false-RED = 진짜 고쳤는데 flaky 실패로 max-FIX 부당 소진 차단). 결정론 확인 횟수 = 설정값(`deterministic_runs_required`, 하드코딩 금지 — §8 Perf Baseline).

#### 8.4 reproducer security invariant (§결정 7 reasoning_carryover security invariant 동형 확장)

fix-event-v1 v1.4 `reproducer_command` (실패 명령 verbatim + base SHA) 는 public PR mirror surface 다 (fix-ledger-sync.yml → Story Issue comment mirror). §결정 7 reasoning_carryover security invariant 를 reproducer 영역으로 동형 확장:

- **schema 제약 (SecurityArch THR-E3-2 강한이의 반영)**: `reproducer_command.command` = **repo-relative 게이트/테스트 호출 형태만** (예: `bash scripts/check-plugin-version-bump-self.sh --self-test`). raw shell free-string 금지 = stored-command injection vector 차단 (Codex worker 발화 reproducer 가 inter-agent trust 경로로 더 위험 — Evgrafov 82.4% > direct 41.2%, ADR-070 X-4 cited).
- **base SHA-pin** (InfraOp): reproduce-before-fix 결정론 기준. replay 기준 = "원 finding SHA 의 자식(fix 포함) worktree HEAD 에서 원 reproducer 재실행" = retest (명령·입력 결정론 고정, 과거 시간여행 아님).
- **INV-SEC-1**: PII / secret / credential / API key / private absolute-path 금지 (repo-relative·환경독립 명령만). Orchestrator append 전 SCAN + 위반 시 fail-fast (자동 redact 금지, audit 가능성).
- **INV-SEC-2**: `replay_verdict` 동반 stdout 발췌는 exit + 모순 라인만 최소 (전체 dump 금지).

#### 8.5 cross-lane RESET (§결정 4) 무관 declare

replay close-gate 는 §결정 4 cross-lane RESET semantics 와 disjoint — replay `falsified` 는 §10 row 의 `RESET?` column 마커를 발동하지 않는다 (닫기 거부일 뿐 lane 카운터 리셋 아님). Pause-and-resume(§결정 4) 영역 무변경.

#### 8.6 declaration-only retain + ratchet 정합

- `mechanical_enforcement_actions: []` retain (replay close-time 자동 wire = Phase 2 / 후속 carrier, ADR-064 §결정 1 unitary). 결정 SSOT = `scripts/lib/fix_replay_disposition.py` (pure function + provenance + discriminating test, CI 미배선 — Story A/B 선례 동형 helper).
- ratchet 강화 방향 (max-FIX disjoint 명문화 + replay fail-mode 2축 + reproducer security invariant codify, 약화 0 — replay 가 카운터를 소비하지 않음을 명시해 정직성·수렴 양립). is_transitional: false 유지. ADR-058 §결정 5 sunset_justification N/A. ADR-070 Amendment 12 + ADR-119 §결정 10② + fix-event-v1 v1.4 sibling cross-ref.

## Amendment 4 (CFP-2985 carrier) — 값공간 확장 ∧ 카운터 disjoint · #2957 데드락 해소 · 정의역 선언 · 유령 선언 철회

> 본 Amendment 는 [ADR-181](ADR-181-verification-domain-deficit-normative.md) 의 **적용 carrier** 다.
> P/V/D 정의는 ADR-181 §결정 1 이 SSOT 이며 본 문서는 **인용만 하고 재진술하지 않는다**(ADR-181 §결정 4 접합부 규약).

### 9.1 `원인 판정` 값공간 6값 확장 ∧ §결정 1 카운터 trigger lane 불변 (disjoint 명문화)

`fix-event-v1` v1.6 에서 `원인 판정` enum 을 확장한다.

| 값 | 재진입 표적 | 신규 |
|---|---|---|
| `설계` | Change Plan 갱신 + 설계 리뷰부터 재실행 | 기존 |
| `구현` | Change Plan 유지 + 구현 commit append | 기존 |
| `요구사항` | 요구사항 lane 재진입 (문제 정의 오류) | ★ 신규 |
| `환경` | 환경·인프라 축 — 산출물 재작성 없음 | ★ 신규 |
| `설계-리뷰` | 설계 리뷰 자체의 판정 결함 | ★ 신규 |
| `구현-리뷰` | 구현 리뷰 자체의 판정 결함 | ★ 신규 |

- **채택 근거 (firsthand)**: enum 밖 4축이 실측 **92행(15.6%)** 실사용 중이다. 15.6% 는 이탈이 아니라
  **값공간 설계 결함의 증상**이다. 특히 `요구사항` 은 `skills/root-cause-decision/SKILL.md` 3rd rung 이
  1차 가정으로 **지시하는 값**이며(ADR-064 Amendment 13), 계약이 그 지시를 뒤늦게 따라가는 것이다.
- ★ **§결정 1 카운터 trigger lane 은 확장하지 않는다.** trigger 범위 = `설계-리뷰` / `구현-리뷰`
  **2 lane 무변경**(`max_fix_per_cycle = 3`). 두 축은 **disjoint** 다 —

  | 축 | 값공간 | 무엇을 결정하는가 |
  |---|---|---|
  | `원인 판정` (라우팅) | 6값 | 다음 iteration 이 **어느 lane 으로 재진입**하는가 |
  | max-FIX 카운터 trigger | 2 lane | **어느 lane 의 재진입 횟수**가 3/3 reassessment 를 유발하는가 |

  값이 `요구사항` 이면 요구사항 lane 으로 재진입하지만 **max-FIX 카운터는 소비하지 않는다**.
  이는 §결정 8 (replay 는 카운터를 소비하지 않는다) 와 **같은 형태의 disjoint** 이며 새 원리가 아니다.
- **소급 정규화 금지**: 기존 행은 재저작하지 않는다(append-only invariant, ADR-181 INV-A).
  집행은 ratchet baseline 동결 + 신규 행만 대상.

### 9.2 #2957 데드락 해소 — 정성 all-miss ∧ 정량 hit 조합의 verdict 부여

**구멍 (firsthand, 본 Amendment 이전)**: §결정 2 는 정성 trigger 3종과 dual metric 을 **결합**해
escalation 의무를 규정하고, §결정 3 은 `reset_and_redesign` 의 전건을
"3 trigger 모두 miss **+** dual metric 모두 miss" 로 규정한다. 따라서

- **정성 all-miss ∧ 정량 hit** 조합은 — §결정 2 의 "정량 metric hit + 정성 trigger evaluation 결합" 을
  충족하지 못해 escalation 의무가 성립하지 않고,
- 동시에 §결정 3 의 reset 전건("정량도 모두 miss")도 성립하지 않는다.

⇒ verdict 가 **어느 쪽으로도 배정되지 않는데** §결정 1 은 "verdict 수령 전까지 4번째 FIX iteration 자동 진입 금지"
를 강제한다. **verdict 부재 ∧ 진입 금지의 교집합 = 데드락**이며 mclayer/plugin-codeforge#2957 로 신고돼 있었다.

**해소 (fail-closed)**:

| 정성 trigger (i/ii/iii) | dual metric | verdict |
|---|---|---|
| 1+ hit | 무관 | `escalate_to_user` (기존, 무변경) |
| all-miss | 1+ hit | ★ **`escalate_to_user`** (본 Amendment 신설 — 종전 미배정) |
| all-miss | all-miss | `reset_and_redesign` 가능 (기존 §결정 3, 무변경) |

- **왜 escalate 인가 (안전 방향)**: 정량 신호(`cumulative_P0 >= 2` / `cumulative_P1 >= 5` /
  `reviewer_divergence_count >= 2`)가 켜졌다는 것은 **관측 가능한 누적 이상**이 있다는 뜻이고,
  정성 평가가 그것을 설명하지 못한다는 것은 **평가 술어가 현상을 못 덮는다**는 뜻이다.
  그 상태에서 reset 을 허용하면 "설명 못 하는 이상 위에서 같은 boundary 재시도" 가 되며,
  이는 §결정 2 (i) 이 겨냥한 실패 모드 그 자체다. ADR-181 INV-D(정의역 정직)의 직접 적용이다.
- **기존 배정 변경 0**: 위 표의 1행·3행은 종전과 동일하다. 본 Amendment 는 **여집합만** 채운다.
- `reasoning_carryover` 3-part 의무는 escalate/reset 무관 동반(§결정 5) — 본 분기도 동일.

### 9.3 FIX 닫기 조건에 검증 정의역 선언 추가 (§결정 8 확장 — 대체 0)

FIX "수정됨" close 시점에 아래 2 필드를 요구한다 (`fix-event-v1` v1.6 trailing optional column).

| 필드 | 내용 |
|---|---|
| `verification_domain_enumeration` | **열거 산출 명령** — site 목록이 아니라 목록을 산출한 명령. `reproducer_command` 의 schema 제약(repo-relative 게이트·테스트 호출, raw shell free-string 금지 — §결정 8 INV-SEC-1) 을 **상속** |
| `verification_domain_coverage` | `x 대 y` — 검사한 site 수 대 열거한 site 수. **확률이 아니라 정직한 미완성 표시** (`3 대 7` = 4개는 아직 안 봤다) |

- **`replay_verdict` 를 대체하지 않는다.** 두 축은 disjoint —
  `replay_verdict` = 검증 **강도**(고쳤다는 주장의 반증), 정의역 선언 = 검증 **범위**.
  §결정 8 의 "replay 는 max-FIX 카운터를 소비하지 않는다" disjoint 도 무변경이며,
  정의역 선언 역시 **카운터를 소비하지 않는다**(카운터 참조 0).
- **비율 임계 게이트를 두지 않는다** — 분모가 자기신고이므로 임계 판정은 조작 유인을 창출한다.
  **기록은 요구하되 임계 판정은 하지 않는다.** 잔존 유인(작게 열거할수록 유리)은 ADR-181 §결정 6
  "유인 이동은 제거가 아니다" 라벨과 함께 **미완화 수용**으로 기록한다.
- **완전성은 판정하지 않는다** — 열거가 전집합인지 여부는 class 동일성 술어 부재로 기계 판정 불가(`declared`).
  ADR-181 §결정 1 이 "금지 대상은 `D` 가 비어 있지 않은 것이 아니라 `D` 를 미선언 상태로 두는 것" 이라 규정한 그대로다.

### 9.4 `fix-event-depth-scope-presence` 유령 선언 철회 + 라벨 Retired

**실측 (firsthand @ wrapper `ecfe62d63`)**:

- 위 §결정 4 Amendment 1 본문이 `fix-event-depth-scope-presence` 를 **"mechanical enforcement"** 로 **선언했었다**
  (좌표 `:157` 은 merge-base `ecfe62d63` 기준이며, 현재 판에는 그 문면이 **부재**한다 — 아래 처분 1 이 치환했다).
- 그러나 `grep -c 'fix-event-depth-scope-presence' docs/evidence-checks-registry.yaml` → **0**
  (파일은 실재 — merge-base `ecfe62d63` 시점 112 entry / 본 Amendment 커밋 후 **113 entry**,
  증가분 1 = `fix-ledger-conformance`. `fix-event-depth-scope-presence` 는 **양 시점 모두 0**).
  script 0 · workflow 0.
- 반면 우회 라벨 `hotfix-bypass:fix-event-depth-scope` 는 `ADR-024:1305` **정식 등재** + 8-label macro bundle 편입.
  ⇒ **게이트는 없는데 그 게이트의 우회 채널만 있다.** 이것이 ADR-181 §결정 3 C-6 의 실물 반례다.

**처분**:

1. §결정 4 Amendment 1 의 "mechanical enforcement" 선언을 **철회**한다.
   ★ **철회는 본 Amendment 커밋에서 문면 치환으로 실집행됐다** — 선언만 남기면 그 자체가 유령이 된다.
   실집행 좌표 = merge-base `ecfe62d63` 의 `:157` 문단(= 본 Amendment 직전 head 의 `:169`)이며,
   해당 문단은 현재 `[철회됨 — 2026-08-16, Amendment 4 §9.4]` blockquote 로 치환돼 있다.
   재현: `git diff ecfe62d63 HEAD -- archive/adr/ADR-067-fix-ledger-implementability-escalation.md`
   에 **삭제 줄(`-` 접두)이 존재**해야 한다(순수 append 이면 철회 미집행이다). 등재가 아니라 철회인 이유 —
   등재하면 113번째 warning entry + script + workflow + self-test 를 만들고 ADR-171 §결정 6 의
   **PR 누적 20 warm-up 을 아무도 요구하지 않은 검사에 대해** 새로 시작해야 한다(ADR-181 §결정 7).
2. `hotfix-bypass:fix-event-depth-scope` 를 `label-registry-v2.md` 에서 **`Retired` 마킹**한다(삭제 아님 —
   삭제는 이력 소실). 게이트 없는 bypass 를 활성 상태로 남기면 C-6 도착이 영구화된다.
   현 시점 `.github/` 안 실 소비자(skip 로직) = **0** 이므로 이 라벨은 오늘 inert 하다.
   inert 한 것은 소비자가 없기 때문이지 안전 설계 때문이 아니며, 배선은 `if:` 1줄이다.
3. ★ **본 Story 신규 게이트(`fix-ledger-conformance`)의 우회 채널로 이 라벨을 채택하지 않음을 명시 선언**한다.
   이름 근접성 때문에 미래에 조용히 배선될 수 있고, 그때 C-6 이
   "라벨이 게이트보다 먼저 있었다" 에서 **"라벨이 게이트를 죽였다"** 로 실현된다.
4. 신규 게이트는 **bypass 라벨 없이 출시**한다. 생성 선행조건 = 그 게이트가 RED 를 낸 실 CI run 참조.
5. ★★ **철회의 문면 도달 범위를 정직 선언한다 (설계리뷰 FIX Iter 1 신설 — INV-D 자기적용)**.
   처분 1 은 **본 ADR 안의 문면**만 치환한다. 그러나 같은 유령을 **현재형으로 기술하는 문면이 본 ADR 밖에
   9곳 더 살아 있다**. 철회를 본 ADR 안에서만 하고 끝내면 "선언은 철회됐는데 그 선언을 인용하는 문서는
   그대로" 라는 상태가 되며, 이는 본 Amendment 가 고발하는 class 의 재생산이다.

   **전수 실측** [wrapper worktree `cfp-2985-fix-telemetry`, ★ **좌표 immutable ref = `ecfe62d63`**
   (merge-base — 아래 1~13 의 타 파일 줄번호는 전건 이 SHA 기준이며, carrier 가 merge 되면 이동한다.
   직전 판은 내부 계수에만 `adf99ed44` 를 병기하고 타 파일 좌표에는 아무 ref 도 안 달아 **같은 표 안에서
   비대칭**이었다 — 설계리뷰 FIX Iter 2 정정), 재현 =
   `grep -rn 'fix-event-depth-scope-presence' --include='*.md' --include='*.yaml' .`]:

   ★★ **직전 판의 표는 12행이었고 실측은 13이다 (설계리뷰 FIX Iter 2 정정 — 누락 1건 = 13행)**.
   누락 기전을 정확히 적는다: 직전 판의 열거는 결과에서 본 ADR 자신을 빼려고 **`grep -v 'ADR-067-fix-ledger'`
   (내용 필터)** 를 썼는데, `archive/adr/ADR-RESERVATION.md:710` 행의 **본문 안에**
   `verified-via Read worktree archive/adr/ADR-067-fix-ledger-implementability-escalation.md` 라는
   문자열이 들어 있어 **경로가 아니라 내용으로 매치돼 조용히 탈락**했다. 즉 배제 술어의 정의역이
   "파일 경로" 여야 하는데 "행 전체" 였다 — **본 Amendment 가 고발하는 검사-정의역 협착 그 class 의 자기 실례**다.
   정정된 술어 = 경로 기준 배제(`sed` 로 좌표만 추출 후 `grep -v '^./archive/adr/ADR-067-fix-ledger'`).
   계수 정합: 전체 매치 **25** − 본 ADR 내부 **12** = **13**.

   | # | site | 분류 | 처분 carrier |
   |---|---|---|---|
   | 1 | `docs/inter-plugin-contracts/fix-event-v1.md:29` | ★ live — registry entry 실재를 `related_files` 주석으로 단언 | D-1 (Phase 1) |
   | 2 | `docs/inter-plugin-contracts/fix-event-v1.md:87` | ★ live — "누락 = warning-tier lint **적발**" (현재형 검출 주장) | D-1 (Phase 1) |
   | 3 | `docs/inter-plugin-contracts/fix-event-v1.md:258` | ★ live — 동일 문면(schema 주석) | D-1 (Phase 1) |
   | 4 | `docs/inter-plugin-contracts/fix-event-v1.md:262` | ★ live — registry entry 단언 | D-1 (Phase 1) |
   | 5 | `docs/inter-plugin-contracts/fix-event-v1.md:388` | ★ live — 요약 목록의 lint 단언 | D-1 (Phase 1) |
   | 6 | `docs/orchestrator-playbook.md:2873` | ★ live — "누락 시 **적발**" | D-25 (Phase 1) |
   | 7 | `templates/story-page-structure.md:419` | ★ live — "누락 시 **적발**" | D-5 (Phase 1) |
   | 8 | `docs/inter-plugin-contracts/label-registry-v2.md:256` | ★ live — 부재 workflow `templates/github-workflows/fix-event-depth-scope-presence.yml` 를 현재형 carrier 로 기술 | D-21 (Phase 2) |
   | 9 | `docs/inter-plugin-contracts/label-registry-v2.md:1201` | ★ live — 부재 script + 부재 workflow 를 registry description 에서 현재형 기술 | D-21 (Phase 2) |
   | 10 | `docs/inter-plugin-contracts/fix-event-v1.md:363` | **동결 이력** — v1.2→v1.3 changelog 항목(dated) | 무접촉 |
   | 11 | `docs/inter-plugin-contracts/label-registry-v2.md:94` | **동결 이력** — Amendment 1 dated 서술 | 무접촉 |
   | 12 | `archive/prune-2026-06/CHECK-VERDICT.md:154` | **동결 이력** — archive 스냅샷 | 무접촉 |
   | ★ 13 | `archive/adr/ADR-RESERVATION.md:710` | **철회 기술** — 본 Amendment 4 의 예약 row 가 축 ④ 를 서술하며 대상을 이름으로 지목한다(이름을 지우면 무엇이 철회됐는지 알 수 없다). 동시에 registry row 는 append-only(INV-A)라 mutate 금지 | 무접촉 (직전 판 **누락** — 위 기전 참조) |

   **본 ADR 안 occurrence 의 분류** — 기준 판 = **`adf99ed44`**(본 처분 5 직전, immutable ref)이며
   그 시점 계수 = **10**. ★ 현재 판의 계수는 여기에 못박지 않는다 — **이 처분 5 문단 자신이 그 문자열을
   포함**하므로 세는 행위가 대상을 늘린다(고정 수치 = 즉시 stale). 재현 규칙 =
   `git show adf99ed44:archive/adr/ADR-067-fix-ledger-implementability-escalation.md` 에 대한 위 grep.
   분류: 동결 이력 = `:16`(Amendment 1 dated log entry —
   amendment_log 는 byte-frozen 이력이며 그 뒤의 Amendment 4 entry 가 철회를 기록하므로 연대기 자체가
   자기정정한다) / **철회 기술** = `:37`·`:39`·`:70`·`:173`·`:479`·`:483`·`:484`·`:486`(철회 대상을
   **이름으로 지목**해야 성립하는 문면 — 이름을 지우면 무엇이 철회됐는지 알 수 없다) / **live 주장** =
   `:57` 1건뿐이었고 본 Amendment 에서 **문면 치환으로 제거**했다.

   ★ **본 처분의 천장**: 위 1~9 의 실 정정은 각 carrier 행에서 일어나며 **본 ADR 은 그것을 지시할 뿐
   집행하지 않는다.** "철회 완료" 라고 적을 수 있는 범위는 본 ADR 문면 + `:57` 까지이고,
   나머지 9곳은 **carrier 가 merge 되기 전까지 살아 있다.** 이 문장을 지우면 over-claim 이 된다.

6. ★★ **`amendment_log` 배제 규칙 확정 + "전수" 주장의 정의역 정합 (설계리뷰 FIX Iter 3 — P0-D)**.

   **적발된 비대칭**: `:16`(Amendment 1 의 `amendment_log[].summary`)은 유령 lint 를 **현재형**으로
   보유한다 — 문면 말미 `… fix-event-depth-scope-presence warning-tier lint (advisory only) 동반.`
   이 줄은 §8.D 음성 leg 의 N1(본문 `**mechanical enforcement**:` 앵커)·N2(`related_*` 블록)
   **어디에도 안 걸려** N=0 GREEN 이 나온다. 반면 같은 class 인 `:70`(`related_files` 주석)은
   **Iter 1 에 정정됐다.** 즉 처리 비대칭이었고, 위 처분 5 는 "전수" 를 단언했다.
   **침묵하지 않고 택일해 선언한다.**

   | 선택지 | 판정 | 사유 |
   |---|---|---|
   | ① `amendment_log[].summary` 를 음성 leg 정의역에 **편입** + `:16` 정정 | ✗ | dated log entry 를 사후 편집하는 것은 **"과거 amendment 가 무엇을 선언했는가" 자체를 바꾸는 행위**다. Amendment 1 은 실제로 그 lint 를 동반한다고 선언**했다** — 그 사실을 지우면 왜 Amendment 4 가 철회를 해야 했는지 근거가 소멸한다. 철회의 올바른 형식은 원문 삭제가 아니라 **후속 entry 의 기록**이며 그것은 이미 `:37` 축 (4) 에 있다 |
   | ★ ② **배제 규칙 제정** (`amendment_log` = 동결 이력) | ★ **채택** | 아래 규칙 + 일관성 검증 |

   **채택 규칙 (기계 판정 가능)**:

   ```
   음성 leg 정의역 = ADR 파일의 다음 표면
     IN : 본문 산문 · related_adrs · related_files · mechanical_enforcement_actions trailing
     OUT: amendment_log[] 의 모든 필드 —  단, 배제는 merge-base 시점에 이미 존재하던 entry 한정
          (그 PR 이 신규 append 한 amendment_log entry 는 정의역 IN)
   ```

   ★★ **supersede — 위 블록은 이력이다 (설계리뷰 FIX Iter 7, 처분 8 이 정본)**. 위 `IN` 열거는
   **allow-list** 였고, 그 열거 4항 중 **도달 leg 이 실재하는 것은 2항뿐**이었다(firsthand — 아래 처분 8).
   즉 *"검사한다고 선언한 표면"* 과 *"검사가 도달하는 표면"* 이 갈렸고, 그것은 이 Story 가
   ADR-181 `INV-D` 로 정의한 **검증 정의역 결손(P ⊋ V)** 그 자체다.
   **정본 = 아래 처분 8 의 leg 별 정의역 표(deny-list).** 위 블록은 덮어쓰지 않고 남긴다 —
   덮어쓰면 무엇이 왜 바뀌었는지가 사라지고 같은 교환을 다음 라운드가 다시 한다.

   - **왜 `:70` 정정과 일관되는가**: `related_files` 는 **dated 가 아니고 append-only 도 아닌
     live 포인터 목록**이다. 읽는 사람은 그것을 "지금 이 ADR 이 가리키는 파일" 로 읽지
     "2026-05-17 에 그렇게 생각했던 기록" 으로 읽지 않는다. 반면 `amendment_log[]` 항목은
     `date` 필드를 **자기 안에 보유**하며 연대기로 읽힌다. **두 표면은 독자 계약이 다르다** —
     따라서 하나는 정정하고 하나는 배제하는 것이 비대칭이 아니라 **표면별 정합**이다.
   - **왜 merge-base 단서가 필요한가**: 단서 없이 `amendment_log` 전체를 배제하면
     **새 amendment_log entry 에 유령 주장을 심는 것이 회피구**가 된다. 배제 근거는
     "이미 동결된 이력" 이지 "log 라는 이름" 이 아니므로, 동결되지 않은(=이 PR 이 방금 쓴)
     entry 는 배제 사유가 성립하지 않는다. 기계 판정 = `git diff merge-base HEAD` 의 추가 줄 여부.
   - ★ **위 처분 5 의 "전수" 주장 정합**: 처분 5 의 전수는 **열거의 전수**(repo-wide grep 13 site
     분류)이고 §8.D 음성 leg 은 **검사의 정의역**이다. 두 축이 다르며 직전 판은 그 차이를 적지
     않아 "전수인데 왜 `:16` 을 안 잡나" 가 성립했다. 정정 = 처분 5 의 전수는
     **"열거 전수 ∧ 검사 정의역은 위 IN 집합"** 으로 읽는다. `:16` 은 **열거에는 포함**되고
     (분류 = 동결 이력) **검사 정의역에서는 배제**된다 — 그 두 사실이 동시에 참이다.
   - ★ **이 규칙의 천장 (`declared`)**: 배제는 "동결 이력은 정정 대상이 아니다" 라는 **저작 규약**에
     의존하며, 그 규약 자체를 기계가 검증하지는 않는다. 즉 누군가 `amendment_log` 를 사후 편집해도
     본 leg 은 침묵한다(그 축의 검출은 `adr-amendment-parity` 소관이며 본 검사가 아니다).

7. ★★★ **처분 6 의 merge-base 단서가 `실행 명령에 존재하지 않았다` — `N3` leg 신설
   (설계리뷰 FIX Iter 4 — P0-A, 3자 완전 수렴)**.

   **적발 (firsthand, 3 심사자 각자 독립 mutant 로 재현)**: 신규 `amendment_log` entry 에 현재형
   유령 주장을 심으면 **N1 = 0 ∧ N2 = 0 = GREEN 통과**한다. 3겹 원인:

   | # | 원인 | 실측 좌표 |
   |---|---|---|
   | ① | `amendment_log:` 가 **N2 의 sed 구간보다 앞**이라 구조적으로 바깥 | `amendment_log:` = `:12` / N2 구간 시작 `related_adrs:` = `:48` / `related_files:` = `:66` |
   | ② | 유령이 **4-space `summary:`** 안에 있어 `grep '^  - '` 에 미매치 | `:16` · `:37` |
   | ③ | ★ **`N3` leg 부재** — `git merge-base` 가 §8.D 실행 명령 **어디에도 없다** | 판정식이 `N1 + N2 == 0` |

   ★★ **정직 정산 — 위 처분 6 은 이 공격을 이름으로 지목하고 닫혔다고 단언했다.**
   처분 6 의 두 문장("배제는 merge-base 시점에 이미 존재하던 entry 한정" / "기계 판정 =
   `git diff merge-base HEAD` 의 추가 줄 여부")은 **규칙으로는 정확했으나 그것을 집행하는 leg 이
   저작되지 않았다.** 즉 **존재하지 않는 방어를 현재형으로 단언**했고, 그것이 본 ADR §결정 5 ②
   ("아직 존재하지 않는 enforcement 자산을 현재형으로 기술하지 않는다")가 금지하는 바로 그 형상이다.
   **처분 6 의 규칙은 유지하고, 그 규칙을 실행하는 leg 을 여기서 신설한다.**

   **`N3` leg (실행 가능 명령 — 의사코드 아님)**:

   ```bash
   cd <wrapper worktree>
   F=archive/adr/ADR-067-fix-ledger-implementability-escalation.md
   AL='/^amendment_log:/,/^related_stories:/p'
   git show ecfe62d63:"$F" | sed -n "$AL" > /tmp/base_al.txt   # merge-base 시점 동결 이력
   sed -n "$AL" "$F"                                > /tmp/head_al.txt
   # 이 PR 이 신규 append 한 줄만 남긴다 (-F 고정문자열 / -x 행 전체 일치 / -v 여집합)
   grep -Fxv -f /tmp/base_al.txt /tmp/head_al.txt \
     | grep 'fix-event-depth-scope-presence' | grep -vc '\[철회됨'
   ```

   판정식 = **`N1 + N2 + N3 == 0`** (각 `grep -c` 는 미매치 시 rc=1 이므로 rc 가 아니라 **출력 정수**로 판정).

   - **`D-LEG` L1 (입력원 리터럴)** — 입력원 = ① merge-base **`ecfe62d63`** ② 대상 파일 경로
     ③ 블록 경계 `^amendment_log:` ~ `^related_stories:` ④ 마커 리터럴 `[철회됨`.
     "merge-base 시점" 이라는 지시어가 아니라 **SHA·경로·앵커 리터럴**로 적는다.
   - **`D-LEG` L2 (판별 행)** — `mutantB`(신규 `amendment_log` entry 에 현재형 유령 주장 주입)를
     **Change Plan §8.D 대조군 표의 행으로 승격**한다. firsthand 실행 결과:

     | 트리 | N1 | N2 | **N3** | 구 판정식 (`N1+N2`) | 신 판정식 (`N1+N2+N3`) |
     |---|---|---|---|---|---|
     | HEAD | 0 | 0 | **0** | GREEN | **GREEN** |
     | `mutantB` | 0 | 0 | **1** | ★ **GREEN (회피 성공)** | ★ **RED** |

     ⇒ `N3` 이 빠지면 판정이 뒤집힌다 = 판별 행 성립.
   - ★ **`N3` 이 잡은 첫 대상은 이 PR 자신이었다 (firsthand)**: leg 을 신설하자마자 HEAD 에서
     **N3 = 2** 가 나왔다 — `:37`(Amendment 4 `summary`)과 `:39`(`reinterpretation` 주석)가
     유령 문자열을 담으면서 고정 마커 `[철회됨` 을 갖지 않았기 때문이다. 두 줄에 마커를 부여해
     **N3 = 0** 으로 청산했다. 규칙을 자기 문면에 먼저 적용한 결과이며, 적용하지 않았다면
     이 leg 은 **자기 PR 에서 RED 인 채로 문서에만 적힌 leg** 이 됐을 것이다.
   - ★ **`N3` 의 정직 천장 (`declared`)**: `N3` 은 **merge-base 에서 정의상 0** 이다(그 시점에는
     "신규 append 줄" 이 없다). 따라서 `N3` 의 항진 반증은 BASE 대조가 **아니라 `mutantB`** 가 맡는다 —
     이 사실을 적지 않으면 "BASE=0 · HEAD=0 이니 leg 이 돈다" 는 공허한 논증이 성립한다.
   - ★ **`N3` 의 정의역 천장 (`declared`)**: 본 leg 의 정의역은 **이 파일의 `amendment_log` 블록**이다.
     다른 ADR 의 `amendment_log` 에 같은 유령을 심는 경로는 미탐이며, 그 축은 Phase 2 checker
     (`adr-admission`, carrier `#2985` / 만기 2026-09-15)의 코퍼스 확장 소관이다.

8. ★★★ **처분 7 의 재설계(Iter 5)가 축을 `교환`해 회귀 2건을 냈다 — `N3` 합집합 확정
   (설계리뷰 FIX Iter 6 — P0, 3자 수렴)**.

   Iter 5 는 위 `N3` 을 **4축 재설계**했다 — ① 물리 줄 → **파싱값** ② 줄-집합 차분 →
   **entry-provenance(번호)** ③ 줄 → **출현** 단위 ④ 부분문자열 → **정확 토큰**.
   ③④ 는 순증이었으나 **①② 는 옛 축을 대체**했고, 그래서 옛 축이 덮던 영역을 그대로 잃었다.

   **적발 2건 (firsthand — 규정 문면을 그대로 구현해 재현)**:

   | # | 잃은 것 | 실측 |
   |---|---|---|
   | ① | **번호만 보므로 내용 변경을 못 본다** | 동결 entry(Amendment 1)의 `summary` 를 편집해 새 유령 주장을 삽입하면 번호는 그대로 `1` → 정의역 밖 → `N3 = 0`. **Iter 4 판(물리 줄)은 검출** |
   | ② | **파싱값만 보므로 YAML 주석을 못 본다** | 이 파일 frontmatter 의 유령 **물리 줄 출현 5** 대 **`amendment_log` 파싱값 출현 2** ⇒ **3건이 주석 전용**. **Iter 4 판은 검출** |

   ★★ **마커가 inert 였다 (결정적 실증)**: `reinterpretation:` 줄 주석의 철회토큰을 **제거해도**
   Iter 5 판 `N3` 은 **0 불변**이다 — 그 줄이 파싱값 정의역 밖이라 토큰이 판정에 아무 영향을 주지
   않았다. 즉 **처분 7 이 "청산했다" 고 적은 두 마커 중 하나는 장식**이었다.
   합집합 후에는 같은 조작이 **1 = RED** 를 낸다(**load-bearing 으로 전환**).

   **규정 (Iter 6 정본)** — `D-LEG` **L3-ⓐ**(축은 교환이 아니라 합집합) 이행:

   ```
   정의역 A := yaml.safe_load(frontmatter)["amendment_log"] 각 entry 의 스칼라 필드 파싱값
   정의역 B := frontmatter `^amendment_log:` ~ `^related_stories:` 구간 물리 줄 중
               merge-base(ecfe62d63) 의 같은 구간 줄 집합에 없는 줄     # 주석·비스칼라를 덮는다
   신규판정(A) := 번호 부재  ∪  번호 동일 ∧ 내용 상이(그 차이 필드의 base 대비 증분만)
   신규판정(B) := 줄-집합 차분
   주장단위   := 각 출현 (A·B 공통)      철회토큰 := 정확 토큰 형식 (처분 7 과 동일)
   판정       := N1 + N2 + N3a + N3b == 0
   ```

   - **"증분만" 인 이유**: 동결 entry 를 건드리면 그 entry 전체가 정의역에 들어오는 설계면,
     오타 수정 하나가 **동결 이력의 옛 출현 전부**를 live 주장으로 오탐한다.
   - ★★ **두 축의 맹점이 disjoint 하다** — `A` 는 주석을, `B` 는 byte-identical 복제와 줄 분할을
     못 본다. **그래서 합집합이 둘 다 닫고, 어느 축도 잉여가 아니다.**
   - ★ **`B` 는 Iter 4 판의 부활이 아니다** — 배제 단위를 **줄 → 출현**, 마커를 **부분문자열 →
     정확 토큰**으로 올린 채 되살린다. **회귀를 되돌리되 개선은 유지**한다.
   - **`D-LEG` L3-ⓑ (H-5 실행 기록)** — mutant 6종 x 3판 대조를 **같은 실행에서** 산출했다
     (Change Plan §8.D). 검출 집합: Iter 4 = `{2,5,6}` · Iter 5 = `{1,2,3,4}` ·
     **Iter 6 합집합 = `{1,2,3,4,5,6}`** ⇒ **`Iter6 ⊇ Iter4 ∪ Iter5`, 잃은 검출 0**.
     HEAD 는 합집합 후에도 **0**(자기 PR born-red 아님).
   - ★ **정직 정산 — 처분 7 도 "닫혔다" 고 단언했다.** 처분 7 의 4축은 **각각은 옳았고 조합이 틀렸다**:
     새 축이 더 강하다는 명제와 옛 축이 잡던 것을 다 잡는다는 명제가 **다르다는 것을 검사하지 않았다.**
     그 검사(H-5)는 Change Plan §8.2 에 **이미 규정돼 있었고 적용이 0회**였다 — 처방은 규칙 신설이 아니라
     **절차 배선**이며 ADR-181 §결정 5 ③-dt (0) `D-LEG` **L3** 로 못 박았다.
   - ★ **잔존 천장 (`declared`)**: 합집합이 닫은 것은 **표기·위치·단위·토큰·provenance 축**이며
     **의미 축**(유령을 동의어·의역으로 바꾼 주장)은 `A`·`B` 둘 다 미탐이다. 정의역도 여전히
     **이 파일**이며 코퍼스 확장은 Phase 2 소관(위 처분 7 천장 그대로 상속).

9. ★★★ **처분 6 의 `IN` 열거가 allow-list 였다 — 검사 정의역을 여집합(deny-list)으로 전환
   (설계리뷰 FIX Iter 7 — P0-A·P0-B, 3자 완전 수렴)**.

   **적발 (firsthand)**: 처분 6 은 `IN : 본문 산문 · related_adrs · related_files ·
   mechanical_enforcement_actions trailing` 을 **"채택 규칙(기계 판정 가능)"** 으로 선언했다.
   그 4항 중 **도달 leg 이 실재하는 것은 2항뿐**이었다.

   | 선언된 IN 표면 | 도달 leg | 실측 |
   |---|---|---|
   | `related_adrs` · `related_files` | N2 | 도달 ✓ |
   | `mechanical_enforcement_actions` trailing | ★ **없음** | N2 의 `grep '^  - '` 필터가 col-0 키 줄을 배제한다. 이 줄은 **repo 최장 산문 표면**이다 (firsthand 658자) |
   | **본문 산문** | ★ **없음** | N1 앵커 `^\*\*mechanical enforcement\*\*:` 매치 = **1줄**(`:170`)이고 **그 줄의 유령 출현은 0**(철회 문장으로 치환됨). 본문 유령 보유 줄 **9** 중 N1 도달 **0** |

   ★★ **이것이 이 Story 가 ADR-181 `INV-D` 로 정의한 검증 정의역 결손(P ⊋ V) 그 자체이며,
   `INV-D` 를 정의하는 PR 안에서 성립했다.** 3방향 오라클(제거·주입·표기등가) 전건에서
   `합 = 0 GREEN` 이 불변이었고, 대조군(`related_files` 주입 → RED)은 성립하므로 **오라클 항진이 아니라
   정의역 결손**이다.

   ★★★ **공통 뿌리 = "열거한 것만 본다"**. 처분 6 의 `IN`, N2 의 `^  - ` 필터, N1 의 앵커 —
   셋 다 **allow-list** 다. allow-list 는 **빠뜨린 것이 문면에 남지 않아 안 보이고**, deny-list 는
   **뺀 것이 문면에 남아 보인다.** 이 Story 가 반복 학습한 *"교환이 아니라 합집합"* 을
   **정의역 축**에 적용한 형태이며, P0-A·P0-B·7번째 회피 경로가 **한 처방으로 닫힌다.**

   **규정 (Iter 7 정본 — 처분 6 의 `IN`/`OUT` 열거를 supersede)**:

   ```
   FM     := 파일 선두 frontmatter 블록 (1행 `^---$` 부터 다음 단독 `^---$` 직전까지의 내부 물리 줄)
   E1     := `^amendment_log:` 줄부터 **그 뒤 첫 col-0 키 줄**(`^[A-Za-z_][A-Za-z0-9_.-]*:`) 직전까지
             종단 부재 시 E1 = 그 1줄만            # ★ supersede — 처분 10 P1-5 (분할 근거로 FM 끝까지)
             (명시 배제 사유: 이 구간은 N3a·N3b 가 전담한다 — 처분 8)

   N2 정의역 := FM − E1                            # ★ deny-list. 열거가 아니라 여집합
   N1 정의역 := 본문 물리 줄 중 `^\*\*mechanical enforcement\*\*:` 매치 줄
                                                   # ★ allow-list 잔존 — 원 선언 site. 아래 천장 참조
   N3a·N3b 정의역 := E1 (처분 8 그대로. ★ 단 `B` 의 신규판정은 아래 P0-C 로 집합 -> multiset 차분)

   주장단위  := N1·N2·N3b = 물리 줄 1개 / N3a = 스칼라 필드 값 1개
   철회토큰  := \[철회됨 — [0-9]{4}-[0-9]{2}-[0-9]{2}, Amendment [0-9]+ §[0-9]+(\.[0-9]+)*\]
   retracted := **단위 안 유령 출현 수 ≤ 단위 안 정확 철회토큰 수**      # ★ 어순 무관 (선치·후치 동등)
   live(단위) := max(0, 출현 수 − 토큰 수)
   판정      := N1 + N2 + N3a + N3b == 0
   ```

   - ★★ **P0-B 봉합 — 정확 토큰이 형제 leg 에 전파됐다.** 직전 판의 N1·N2 는 여전히
     `grep -vc '\[철회됨'`(부분문자열)이었고, `related_files` 에 `[철회됨 아님 — …]` 를 붙이면
     **전 leg 0 = GREEN** 이었다. 처분 7 이 `N3` 축에서 이미 봉합한 class 가 **형제에 미도달**해
     표면만 이동한 상태였다(Iter 2 가 스스로 결함이라 부른 형상). ⇒ N1·N2 를 **N3 와 동일한 정확 토큰**으로
     올린다. **firsthand 판별**: 위조 토큰 mutant = **1 RED** / 부분문자열 leg-off = **0 GREEN**.
   - ★★ **P1-2 봉합 — 마커 어순이 후치 전용이었다.** 처분 7·8 의 `retracted(i)` 는 구간
     `[occ_i, occ_{i+1})` 만 보므로 **마커가 유령 뒤에 와야만** 철회로 인정했다. 그런데 한국어 자연 어순은
     선치이고 **이 파일 `related_files` 의 현행 마커가 실제로 선치**다(firsthand). 후치 전용을 그대로 두고
     정확 토큰만 올렸다면 **자기 PR 이 born-red** 가 된다. ⇒ 단위를 **줄/필드 값 전체**로 올리고 판정을
     **출현 수 ≤ 마커 수**로 바꾼다 — 선치·후치를 모두 인정하면서 **경로 2(동거)의 1-마커-전체면제**는
     계속 막는다(마커 1 · 유령 2 = RED, firsthand).
   - ★ **7번째 회피 경로(`related_stories` 블록)가 같은 처방으로 닫힌다** — 이 블록은 N3b 종단 앞이고
     N2 시작 뒤라 **어느 정의역에도 없었다.** deny-list 는 여집합이므로 **열거를 고치지 않아도 포함**된다.
     이것이 allow-list → deny-list 전환의 실물 이득이다(firsthand: 주입 → **1 RED** / allow-list leg-off → **0 GREEN**).

   ★★ **선언 정의역 = 검사 정의역을 구조로 보장한다 (P0-A ② 처분 — 택일: 좁힘 + 넓힘 동시)**.
   직전 판은 정의역을 **leg 과 독립된 산문 열거**로 선언했고, 그래서 열거가 leg 을 앞질러 갈 수 있었다.
   ⇒ **선언을 leg 별로 분해**해 각 leg 이 자기 정의역을 스스로 선언하게 한다. 그러면
   *"선언했는데 도달 leg 0"* 이 **구조적으로 불가능**해진다(선언이 leg 에서 파생되므로).

   | leg | 정의역 (선언 = 검사) | 판별 입력 (firsthand) | 규정판 | leg-off |
   |---|---|---|---|---|
   | **N1** | 본문 중 `^\*\*mechanical enforcement\*\*:` 매치 줄 | 그 줄을 Amendment 1 원형으로 복원 | **1 RED** | 0 GREEN |
   | **N2** | `FM − E1` (**deny-list**) | ① mea trailing 산문에 유령 ② `related_stories` 에 유령 ③ 위조 토큰 | **각 1 RED** | 각 0 GREEN |
   | **N3a** | E1 파싱값 (신규·변경 entry) | 처분 8 mutant 1~6 | 처분 8 표 | 처분 8 표 |
   | **N3b** | E1 물리 줄 (base 구간 줄 집합 밖) | 처분 8 mutant 1~6 | 처분 8 표 | 처분 8 표 |

   ★★ **본문 산문은 검사 정의역에서 `좁힌다` — 침묵이 아니라 택일 선언**. 본문 전체를 deny-list 로
   넓히는 안을 **실행해 기각**했다 (firsthand):

   ★ **계수를 정수로 못박지 않는다 — 이 문단 자신이 본문에 유령을 추가하므로 세는 행위가 대상을 늘린다**
   (처분 5 가 같은 함정을 만난 자리와 동형). 기준 판 = **`ad3263910`**(본 처분 9 직전, immutable ref),
   재현 규칙 = 아래 명령. 그 시점 산출 = 유령 보유 줄 **9** / 정확 토큰 보유 **0** /
   본문 deny-list 판 HEAD 값 **9 = 즉시 born-red**.

   ```
   git show ad3263910:archive/adr/ADR-067-fix-ledger-implementability-escalation.md \
     | sed -n '74,$p' | grep -c 'fix-event-depth-scope-presence'     # 본문 = FM 종단(73행) 다음부터
   ```

   - 그 줄들에 마커를 박으려면 **실행 명령 리터럴 안**에 마커가 들어간다 — 그 중 한 줄은
     처분 7 의 **leg 명령 자신**(`grep -vc` 로 철회 토큰을 거르는 파이프라인)이고 둘은 census grep 이다.
     **명령을 훼손하지 않고는 마커를 박을 수 없다.**
   - 코드펜스 배제로 우회하는 안도 기각했다 — (a) 이 파일의 펜스는 **들여쓰기** 형태라
     `^```` 앵커가 **2/6 만 잡는다**(firsthand: `grep -c '^```'` → 2, `grep -cE '^[ ]+```'` → 6),
     (b) 더 결정적으로 **펜스·코드스팬 배제 자신이 회피구**다 — 유령을 백틱 안에 넣고 주장은 평문으로 쓰면
     면제된다. **배제 규칙이 공격자에게 열린 문이면 그것은 방어가 아니다.**
   - ⇒ **택일 = 좁힘.** 본문 산문은 **기계 검사 정의역 밖**이며 **열거 축**(처분 5 의 repo-wide grep
     13-site 분류) 소관이다. 이 분리는 처분 6 이 이미 세운 *"열거의 전수 ≠ 검사의 정의역"* 2축 구분의
     **적용**이며, 결함은 그 구분을 세워 놓고 `IN` 열거에 본문을 적은 것이었다.
   - ★ **독자 계약 근거 (처분 6 의 논거 계승)**: frontmatter 필드는 **선언면**(다른 도구가 선언으로 읽는 표면)
     이고 본문 §9.4 는 **서술면**(철회 서사)이다. 선언면의 유령은 **그 자체가 live 선언**이고,
     서술면의 유령은 **이름 지목**이다 — 표면별 정합이지 비대칭이 아니다.
   - ★ **잔여 (`declared`)**: 본문에 평문으로 live 주장을 심는 경로는 **N1 앵커에 걸리지 않으면 미탐**이다
     (firsthand: 본문 평문 mutant = **0 GREEN**). 지우고 인용하면 over-claim 이다.

   ★ **정상형 토큰은 유령 판정 대상이 아니다 (판별 행 고정)**: `carrier=` · `expiry=` · `[repo=` 는
   ADR-181 §결정 5 ③-dt 의 **면제 선언 토큰**이지 유령 문자열이 아니다. 셋만 담은 줄을 `related_files` 에
   주입한 mutant = **0 GREEN**(firsthand) — 즉 deny-list 확장이 **정상 표면을 오탐하지 않는다.**
   이 행이 없으면 *"넓혔으니 안전하다"* 가 검증되지 않은 채 남는다.

   ★ **E1 종단의 fail-closed 전환 — 판별은 `결합`이다 (정직 기재)**: 종단을 이름 `related_stories:` 에
   pin 하면 그 키가 사라졌을 때 배제가 frontmatter 를 **끝까지 삼킨다.** col-0 키 정규식으로 바꿔 닫았으나,
   **verdict 축 단독 판별 행은 0** 이다 — 삼켜진 구간을 **N3b 가 그대로 받아내기 때문**이다
   (firsthand: 종단키 제거 mutant = 규정판 **1 RED** / 이름-pin leg-off 도 **1 RED**).
   잔여 1경로(base E1 줄을 frontmatter 다른 위치에 **byte-identical 복제**)는 **도달 불가**다 —
   base E1 의 유령 보유·무마커 줄은 **1개**(4-space `summary:` 매핑 키)이고, 이를 frontmatter 내
   amendment_log 밖 **5개 위치에 삽입한 결과 5/5 가 YAML 파싱 실패**다(firsthand).
   ⇒ (0-d) `BLANK` 과 같은 **도달 불가 증명 보유** 부류이며, *"아직 안 찾은 것"* 이 아니다.
   ★ 단 이 증명은 **현행 base E1 내용에 결속**된다 — 미래 base 에 top-level 로도 유효한 형태의
   유령 보유 줄이 들어오면 도달 가능해진다(carrier `#2985` / 만기 `2026-09-15`).

   ★★★ **부수 발견 — `N3b` 의 줄-집합 차분이 7번째가 아니라 8번째 경로를 열어 두고 있었다
   (설계리뷰 FIX Iter 7 자체 발견, P0-C)**.

   위 처분 8 의 H-5 대조를 **Iter 7 판정식으로 재실행**하던 중, `경로 1 복제` 를 **키 경쟁에서 지도록**
   배치한 변종이 **전 leg 을 통과**했다 (firsthand):

   ```
   구성 = base amendment_log 의 유령 보유·무마커 줄을 신규 entry 의 **기존 summary 앞**에 삽입
     A(파싱값) : YAML 중복 키는 **뒤에 오는 값이 이긴다** -> Amendment 4 의 summary 파싱값 불변 -> 0
     B(줄집합) : 삽입 줄이 base 구간 줄 집합에 **있다** -> "신규 아님" -> 0
     => 합 0 = GREEN   (문면에는 유령이 보이는데 두 축 모두 놓친다)
   ```

   ★ **처분 8 의 `경로 1` 과 같은 이름이되 다른 배치**다 — 처분 8 이 실증한 복제는 중복 키가 **이기는**
   배치라 A 가 잡았고, **지는** 배치는 A 가 원리적으로 못 본다(파서가 버린 값이므로). 즉
   *"A 가 복제를 막는다"* 는 **배치 조건부 참**이었고 조건이 적혀 있지 않았다.

   **규정 (Iter 7 — `B` 의 신규판정만 교체, A 무접촉)**:

   ```
   신규판정(B) := 줄-**집합** 차분  ->  줄-**multiset** 차분
                  base 구간의 같은 줄 사본 수를 하나씩 소진하고 **초과 사본**을 신규로 센다
   ```

   - ★ **엄격 확대다 (L3-ⓐ)** — 집합 차분이 신규로 판정하던 줄은 multiset 차분도 전부 신규로 판정한다
     (base 사본 수 0 이면 초과 사본이므로). 따라서 **잃는 검출이 정의상 0** 이며, 늘어나는 것은
     *"base 에 있는 줄을 한 벌 더 복사한 경우"* 뿐이다.
   - ★★ **실행 대조 (firsthand — 처분 8 의 6 mutant 전건 재실행)**:

     | 입력 | 규정판 (multiset) | `B` 집합 차분 leg-off |
     |---|---|---|
     | HEAD | **0 GREEN** | 0 GREEN |
     | 1 복제 (키 경쟁 **패배** 배치) | ★ **1 RED** | ★ **0 GREEN** |
     | 2 동거 | 2 RED | 2 RED |
     | 3 분할 | 1 RED | 1 RED |
     | 4 위조 토큰 | 2 RED | 2 RED |
     | 5 동결 entry 편집 | 3 RED | 3 RED |
     | 6 신규 entry 주석 | 1 RED | 1 RED |

     ⇒ **판별 행 = `1 복제`** (verdict 축) · **회귀 0** (2~6 전건 불변) · **HEAD born-red 아님**.
   - ★★ **이 발견의 출처가 요점이다** — 심사가 아니라 **H-5 대조를 실제로 재실행한 행위**가 잡았다.
     `D-LEG` L3-ⓑ 가 요구하는 것이 *"전임 판이 잡던 것을 새 판도 잡는가"* 인데, 그 대조를 돌리려면
     **전임 mutant 를 다시 구성**해야 하고 그 과정에서 **구성의 자유도**(어디에 삽입하는가)가 드러났다.
     ⇒ **H-5 는 회귀 검사이면서 동시에 탐색 도구다.** 표를 옮겨 적기만 했다면 이 경로는 살아남았다.
   - ★ **잔여 (`declared`)**: multiset 차분은 **줄 단위**다. base 줄을 **한 글자 바꿔** 복제하면 초과 사본이
     아니라 신규 줄이 되어 **B 가 잡지만**, 반대로 base 에 없는 형태로 유령을 심으면서 A 도 피하는 조합은
     여전히 **의미 축 회피**(동의어·의역)로 열려 있다 — 처분 8 의 천장 그대로 상속.

   ★★ **`D-LEG` L3-ⓐ 준수 (축 제거 0)**: 본 처분은 **어느 leg 도 제거하지 않는다.** N1 은 도달 유령이
   0 이어도 **존치**하며(판별 입력 = 앵커 복원 mutant, 규정판 1 RED), N2 는 정의역이 **확대**되고,
   N3a·N3b 는 처분 8 그대로다. 바뀐 것은 **정의역의 표현 방식(열거 → 여집합)**·**마커 술어(부분문자열 →
   정확 토큰)**·**단위 판정(후치 구간 → 출현 수 ≤ 마커 수)** 셋이며 **전부 확대 방향**이다.

10. ★★★ **`형제 미도달` 이 4번째다 — leg 별 재구현을 폐지하고 단일 front-end 인스턴스화로 전환
    (설계리뷰 FIX Iter 8 — P0-A·P0-B, 3자 수렴 + Codex 비대칭 진단)**.

    **적발 (firsthand)**: 같은 class 가 라운드마다 **자리만 바꿔** 재발했다.

    | 라운드 | 봉합한 자리 | 형제 미도달 | 검출자 |
    |---|---|---|---|
    | Iter 5 | 정확 토큰 → `N3` 만 | `N1`·`N2` 는 부분문자열 잔존 | Iter 7 심사 |
    | Iter 7 | 축 합집합(파싱값 ∪ 물리 줄) → `N3` 만 | `N1`·`N2` 는 물리 줄 단일 축 | Iter 8 심사 (P0-A) |
    | Iter 7 | 파싱 실패 = RED 규정 | 그 규정을 집행하는 leg 이 형제에 없음 | Iter 8 심사 (P0-B) |

    ★★ **처방을 가리킨 것은 `비대칭` 이다** — 같은 기법(`3 분할`)이 `E1` 안에서는 **RED**(`N3a` 가
    파싱값 축을 보유)인데 자리만 `N2` 로 옮기면 **GREEN** 이었다. 같은 입력이 자리에 따라 갈리면
    결함은 그 leg 이 아니라 **leg 이 각자 정의역을 재구현하는 구조**에 있다.
    ⇒ **또 `형제에 전파` 하면 5번째가 온다.** 전파는 매번 열거이고, 열거는 이 처분 9 가 이미
    allow-list 로 지목해 폐기한 형상이다.

    **규정 (Iter 8 정본 — 처분 9 의 leg 별 정의역 표를 `front-end 파생`으로 재기술. 판정식 확장)**:

    ```
    FE(head_text, base_text)  =  단일 front-end. 정의역 추출·정규화를 여기서만 한다.
      ── 경계 (b1..b5) ──────────────────────────────────────────────────
      b1  head_text 가 정확히 `---` + 개행으로 시작       # BOM·선행 공백 불허
      b2  1행 이후 첫 단독 `^---$` 존재 = FM 종단
      b3  FM 텍스트가 YAML 로 파싱되고 결과가 mapping
      b4  FM 종단 다음 줄부터 첫 비-FM-형·비-공백 줄까지, FM-형 줄이 0
            FM-형 := `^[A-Za-z_][A-Za-z0-9_.-]*:` 또는 `^[ ]+- ` 또는 `^[ ]+[A-Za-z_][A-Za-z0-9_.-]*:`
      b5  base_text 존재 시 keys(FM_head) ⊇ keys(FM_base)     # top-level 키 보존
      b1·b2·b4·b5 위반 = `fm-boundary` / b3 위반 = `fm-parse-error`   # 둘 다 RED, skip 아님
      ── 정규화 (전 leg 공통 · 재구현 금지) ────────────────────────────
      occ(u)  := 단위 u 안 유령 문자열 출현 수
      tok(u)  := 단위 u 안 **정확 철회토큰** 출현 수   # 처분 9 정규식 그대로
      live(u) := max(0, occ(u) − tok(u))               # 어순 무관 (처분 9 그대로)
      ── 축 (전 leg 공통 · leg 은 region 만 고른다) ────────────────────
      units(region) := 축 P ∪ 축 V                     # ★ 합집합. leg 이 축을 고르지 않는다
        축 P := region 의 물리 줄 각각
        축 V := region 에 대응하는 파싱값의 str 스칼라 각각 (list·dict 재귀 하강)

    leg = region 선택 + FE 인스턴스화 (자기 정규화·자기 축 보유 금지)
      N0  := FE 경계 위반 시 1                          # ★ 신설 — 전체집합 무결성
      N1  := Σ live(u) for u in units(BODY ∩ `^\*\*mechanical enforcement\*\*:` 매치 줄)
      N2  := Σ live(u) for u in units(FM − E1)
      N3a := Σ live(u) for u in units(E1 신규·변경 entry)          # 처분 8 provenance 그대로
      N3b := Σ live(u) for u in units(E1 물리 줄 multiset 차분)     # 처분 9 P0-C 그대로
      판정 := N0 + N1 + N2 + N3a + N3b == 0
    ```

    - ★★ **`N0` = P0-B 봉합 (전체집합 경계 조작)**. 처분 9 의 deny-list 는 `N2 := FM − E1` 로
      **부분집합 선택만** 여집합화했고 **전체집합 `FM` 의 경계는 여전히 문면 allow-조건**이었다.
      `FM` 을 줄이면 `N2`·`N3a`·`N3b` 가 **함께** 줄어 유령이 살아 있는데 전 leg 0 = GREEN 이다.
      **firsthand 3 경로** — 이른 단독 `---`(FM 중간 삽입) · **선두 BOM**(`^---$` 불성립으로 FM 시작점이
      종단 줄로 밀림) · FM YAML 파싱 실패. 셋 다 규정판 **1 RED** / `N0` off **0 GREEN**,
      대조군(경계 조작만 제거하고 유령은 그대로) = **1 RED**.
    - ★★ **`b4` 와 `b5` 는 서로의 맹점을 덮는다 (교환 아님 — L3-ⓐ)**. `b4`(종단 직후 잔여 FM-형 줄)는
      **merge-base 가 없는 신규 파일**을 덮고 `b5`(키 보존)는 못 덮는다. `b5` 는 `---` 를 **비-FM-형 줄**
      (산문 연속행) 앞에 넣어 `b4` 의 스캔이 즉시 멈추는 배치를 덮고 `b4` 는 못 덮는다.
      **firsthand 판별 (각자 단독 판별 행 보유)** — `b4` off 에서 신규파일 mutant가 **RED → GREEN**,
      `b5` off 에서 비-FM-형 앞 삽입 mutant가 **RED → GREEN**, 둘 다 off 면 **두 mutant 모두 GREEN**.
    - ★★ **`③ fm-parse-error = RED, skip 아님` 이 여기서 처음 집행된다.** ADR-181 §결정 5 ③-dt (iii) 는
      이 규정을 이미 보유했으나 **본 §9.4 의 leg 중 어느 것도 그것을 실행하지 않았다**
      (`N3a` 가 `safe_load` 에 의존하면서 예외 시 무정의). 규정과 집행의 괴리가 P0-B 의 절반이며,
      front-end 로 올리면 **한 자리에서 집행되고 네 leg 이 그 판정을 상속**한다.
    - ★★ **형제 게이트에도 같은 class 가 실재한다 (firsthand, 정직 기재)**:
      `scripts/lib/check_doc_frontmatter.py` 는 FM 을 `text.split("\n---\n", 1)[0]` 로 자르므로
      **이른 단독 `---` 이 조용히 절단**하고(`:89`·`:160` 무보고 `continue`), 선두 BOM 은
      `text.startswith("---\n")` 불성립으로 `:47` **warning 후 continue** 한다. 본 처분은 그 게이트를
      고치지 않는다 — **본 §9.4 의 leg 집합에 대해서만** 닫으며, 형제 게이트 정정은 정의역 밖이다
      (carrier `#2985` / 만기 `2026-09-15`).
    - ★★ **축 합집합의 front-end 승격 = P0-A 봉합**. 처분 8 의 `A ∪ B` 는 **`N3` 안에서만** 성립했다.
      `units()` 로 올리면 **FM 을 region 으로 삼는 leg**(`N2`·`N3a`·`N3b`)이 같은 합집합을 **상속**한다.
      **firsthand 판별** — 처분 8 표의 `3 분할` 을 자리만 `E1` → `N2`(FM 안 이중인용 스칼라, 줄끝
      백슬래시)로 옮긴 mutant: 규정판 **1 RED** / 축 합집합 off **0 GREEN**.
      대조군(같은 주장 한 줄) = 규정판 **2 RED**(P·V 이중 계수) / 축 합집합 off **1 RED**.
      - ★★★ **문면 삭제 (처분 11, FIX Iter 9)** — 직전 판은 여기에 *"`N1`·`N2` 도 같은 합집합을
        상속하고 (…) **축을 고를 자유가 없다** — *형제 미도달* 이 구조적으로 불가능해진다"* 라고
        적었다. **`N1` 에 대해 거짓이므로 그 문장을 삭제했다**(철회는 문면 삭제로만 성립 — 이 Story 규율).
        **`N1` 의 region 은 BODY 이고 BODY 에는 파싱 계층이 없다** — 축 V 로 인스턴스화할 것이
        **구조적으로 없다**(공집합). **firsthand**: 앵커 줄 안에서 유령을 두 물리 줄로 분할하거나
        `<!---->` 로 splice 하면 `축P=0 축V=0` → **GREEN**, 대조군(한 줄) = `축P=1 축V=0` → **RED**.
        ⇒ front-end 승격이 실제로 준 것은 *"전 leg 이 축을 못 고른다"* 가 아니라
        **"파싱 계층을 가진 region 의 leg 이 축을 못 고른다"** 이다. 이것이 **두 번째로 반증된
        *구조적으로 불가능* 선언**이며(첫 번째 = 처분 9 합집합), 그 반복이 아래 처분 11 의 근거 1항이다.
    - ★ **재귀 하강으로 통일 — 처분 9 의 `N3` 하강 미규정 잔여가 닫힌다.** 처분 9 는 `A` 축을
      "entry 매핑의 1단계 값 중 str" 로 한정하고 중첩 컨테이너 도입 시를 **미규정 잔여**로 남겼다
      (carrier `#2985` / 만기 2026-09-15). `units()` 의 축 V 가 **list·dict 재귀 하강**이므로 그 잔여는
      **소멸**한다. 현행 스키마에 중첩이 0 이라 **HEAD 값은 불변**(born-red 아님, firsthand)이며,
      따라서 이것은 검증 불가능한 규정이 아니라 **판별 대상이 생기는 즉시 유효한 확대**다.
    - ★ **엄격 확대 (L3-ⓐ 축 제거 0)**: `N1`·`N2`·`N3a`·`N3b` 어느 것도 제거·축소되지 않았다.
      바뀐 것은 ⓐ 정규화·축의 **소재**(leg 각자 → front-end 단일) ⓑ `N0` **신설** ⓒ 축 V 하강 규칙
      **통일** 셋이며 전부 확대 방향이다. **회귀 0** — 처분 8·9 의 mutant 전건에서 verdict 불변(firsthand).
    - ★ **정직 기재 — exit 사유가 이동한 행이 1개 있다.** 처분 9 의 `m9`(E1 종단키 제거 + 유령)는
      규정판 verdict 가 **RED 로 동일**하나 사유가 `ghost-live`(N2) → **`fm-boundary`(N0)** 로 옮겼다.
      `b5` 가 top-level 키 소실을 먼저 물기 때문이며, `b5` off 에서는 다시 `N2` 가 받는다(**RED 유지**).
      **이중 방어**이지 검출 이동이 아니다 — 이 문장을 지우면 다음 심사가 표 대조에서 불일치를 재발견한다.
    - ★★★ **`E1` 종단 부재 처분 정정 — 배제가 아니라 분할이다 (P1-5, 처분 9 의 fail-closed 판을 supersede)**.
      처분 9 는 *"종단 부재 시 `E1` = 그 1줄만 (fail-closed — 배제가 frontmatter 를 삼키지 못한다)"* 로 뒀다.
      **그 판이 동결 이력을 오탐한다 (firsthand)**: `amendment_log` 블록을 FM 마지막 키로 옮기는
      **주장 불변 서식 변경**만으로 `N2 = 1 RED` 가 난다 — 옮겨진 블록이 `E1`(1줄) 밖으로 나와
      **provenance 가 없는 `N2`** 로 떨어지고, 거기서 base 동결 entry 의 무마커 유령이 live 로 셈되기 때문이다.
      ⇒ **종단 부재 시 `E1` := `amendment_log` ~ FM 끝**으로 되돌리되, 근거를 바꾼다:
      **`FM = (FM − E1) ⊎ E1` 는 배제가 아니라 분할**이며 **어느 물리 줄도 두 정의역 밖으로 못 나간다.**
      `E1` 은 오히려 **더 강한 검사**(provenance 보유)를 받으므로 삼킴이 fail-open 이 아니다.
      **firsthand 대조** — 서식 이동만: 분할판 **0 GREEN** / 처분 9 판 **1 RED**(오탐 재현) ·
      서식 이동 **+ 실 유령 주입**: 분할판 **1 RED**(진짜 주입은 잡는다) · 종단키 제거 + 유령: 분할판 **1 RED**(`fm-boundary`).
      - ★★ **리뷰 처방에서 이탈한 지점 (자기표시)**: 리뷰는 삼킴 방지를 **별도 leg `[e1-unterminated]` = RED**
        로 분리하라 했으나 **채택하지 않았다** — 코퍼스 실측상 `amendment_log` 가 FM 마지막 키인 ADR 이
        **174 중 28**(정상 배치)이라 그 leg 은 **28건을 false-RED** 로 만든다. 삼킴이 회피구가 되지 않는
        보장은 **분할 성질 + `b5`(키 보존)** 가 이미 제공한다.
      - ★ **"주입분 기여 0" 은 재현되지 않았다 (정직 기재)**: 리뷰는 오탐이 진짜 주입을 **가린다(계수가 같다)**
        고 적었으나 실측은 서식이동만 **1** → 실주입 추가 시 **2** 로 **기여 1** 이다. 오탐 자체는 재현되므로
        처분은 유지하되, 재현되지 않은 하위 주장을 그대로 인용하지 않는다.
    - ★ **`P1-4` 카운트 보존 이동 — 재현 실패 (정직 기재)**: 리뷰는 *"multiset 은 카운트 증가만 닫고
      보존 이동은 GREEN"* 이라 적었다. `E1` 안 유령 보유 줄을 같은 `E1` 안 다른 위치로 옮긴 mutant 를
      구성해 실행한 결과 **규정판·축합집합off·집합차분·(축합집합off ∧ 집합차분 = Iter 7 판) 전 열에서 `1 RED`**
      였다 — `N3b` 의 multiset 이 불변이어도 **`N3a` 의 entry-provenance 가 소유 entry 변화를 잡는다.**
      대조군(복제) = **2 RED**. ⇒ **이동 축은 이미 닫혀 있으며**, 남는 것은 *"파싱값도 multiset 도 불변인
      순수 재배열"* 인데 그것은 **주장 불변**이므로 GREEN 이 옳다(결함 아님). 재현되지 않은 지적을
      처분한 척하지 않는다 — 대신 위 이동 mutant 를 **회귀 입력으로 편입**한다.
    - ★ **입력 정규화도 front-end 소관 (P2-2 `NFC` 축)**: 유니코드 정규화 형식은 판정을 바꾸는 자유 변수다.
      **firsthand** — 이 파일 HEAD 는 NFC 이고, **NFD 로 정규화하면 정확 철회토큰 매치가 6 → 0** 이 되어
      **0 → 6 RED** 로 전면 false-RED 가 된다.
      ★ **계수 정정 (FIX Iter 9)** — 직전 판의 `7` 은 **실측 `6`** 이다(2 도구 교차 · 산출 명령 병기):

      ```
      F=archive/adr/ADR-067-fix-ledger-implementability-escalation.md
      grep -oE '\[철회됨 — [0-9]{4}-[0-9]{2}-[0-9]{2}, Amendment [0-9]+ §[0-9]+(\.[0-9]+)*\]' "$F" | wc -l
        -> 6
      python -c "...re.findall(정확 철회토큰, NFC 원문)..."   -> 6   ·   NFD 정규화 후 -> 0
      ```

      **결론 `0 → 6 RED` 는 무손상**이다 — 마커를 잃는 단위가 6 개이므로 뒤집히는 수도 6 이다.
      바뀐 것은 **좌변 계수 표기**뿐이며, `7` 은 어느 도구로도 재현되지 않았다. ⇒ front-end 가 입력을 **NFC 로 정규화**해 검사를
      정규화-불변으로 만든다(정규화 후 NFD 입력도 **0 GREEN**, `NFC` off 시 **6 RED** = 판별 행).
    - ★ **코드펜스 계수는 정수로 못박지 않는다 (P2-4)** — 처분 9 가 이 자리에 적은 `2/6` 은 **즉시 stale**
      이 됐다(이 처분 자신이 펜스를 추가하므로 — 처분 5 의 site 계수·(0-c) `leg` 외연과 **같은 계보**).
      ⇒ **재현 규칙 + immutable ref** 로 적는다. 기준 판 = **`ad3263910`**(처분 9 직전) 산출 = 열0 **2** /
      들여쓴 **6**. 현재 판 산출은 **아래 명령으로 얻는다** — 적는 즉시 틀리므로 여기 정수를 쓰지 않는다.

      ```
      grep -cE '^```'    archive/adr/ADR-067-fix-ledger-implementability-escalation.md   # 열0 펜스
      grep -cE '^[ ]+```' archive/adr/ADR-067-fix-ledger-implementability-escalation.md  # 들여쓴 펜스
      ```

      ★ **결론은 무변경**: 어느 산출이든 **열0 앵커가 전 펜스를 잡지 못한다**는 사실이 코드펜스 배제안의
      기각 근거이며, 그 근거는 계수의 특정 값이 아니라 **두 계수가 다르다는 것**에 결속된다.
    - ★ **잔여 (`declared`)**: ⓐ **의미 축 회피**(동의어·의역)는 처분 8 천장 그대로 미탐이다.
      ⓑ **본문 평문 live 주장**은 `N1` 앵커 밖이면 미탐이다(처분 9 의 좁힘 택일 — firsthand `0 GREEN`).
      ⓒ `b4` 는 **종단 직후 연속 구간**만 보므로, 빈 줄과 비-FM-형 줄을 앞세운 배치는 `b5` 에만 의존한다
      (신규 파일이면 `b5` 부재 = 미탐). 세 잔여를 지우고 인용하면 over-claim 이다.

11. ★★★★ **처분 11 (설계 FIX Iter 9) — 유령 leg 을 수용 기준에서 내리고 `declared` 관측 도구로 강등한다**

    **성격**: 이 처분은 축을 **더하지 않는다**. 처분 6~10 이 매 라운드 해 온 것(정의역 확대 · 토큰 정밀화 ·
    축 합집합 · front-end 승격)과 **반대 방향**이며, **약속을 실제 지킬 수 있는 크기로 맞추는 것**이다.
    Orchestrator 처분 = **B안**(사용자 escalation 반려 후 결착, 재논의 금지).

    | 축 | 처분 10 까지 | **처분 11 이후** |
    |---|---|---|
    | 유령 탐지 `N0`·`N1`·`N2`·`N3a`·`N3b` (산문 스캔) | 수용 기준 | ★ **`declared` 관측 도구** — 계속 실행·기록하되 **합격 판정에 쓰지 않는다** |
    | 수용 기준 | (iv) 결정표 ∧ 유령 leg | ★ **ADR-181 §결정 5 ③-dt (iv) 입장 조건 결정표 단독** |
    | 실 강제 | 없음 (Phase 1) | Phase 2 checker `fix-ledger-conformance` (carrier `#2985` / 만기 `2026-09-15`) |

    - **강등 ≠ 폐기.** mutant 코퍼스 · 대조표 · ablation 열은 **전부 존치**하며 계속 돌린다. H-5 가
      실증했듯 이 실행은 **탐색 도구로서 실제 결함을 냈고**(처분 9 의 P1-5, 처분 10 의 형제 미도달,
      이번 판의 조합 회피) 그 가치는 수용 기준 지위와 **무관**하다. 바뀌는 것은 산출에 합격/불합격을
      걸지 않는다는 것 하나다. **L3-ⓐ(축 제거 0) 위반 아님** — 제거된 leg 은 0 이다.

    **근거 4항**

    | # | 근거 |
    |---|---|
    | 1 | **산문 스캔 표면은 원리적으로 열려 있다.** 9 라운드에서 회피 경로 **10종** — BOM · CRLF · ZWSP · 줄접합 · YAML 중복키 · rename · 이른 `---` · 앵커 안 삽입 · **조합** · 열거자 밖 디렉터리. 그리고 *"구조적으로 불가능"* 선언 **2회**(처분 9 합집합 · 처분 10 front-end)가 **모두 다음 라운드에 반증**됐다 — 두 번째 반증이 바로 위 처분 10 의 삭제된 문장이다 |
    | 2 | **입장 조건(③)은 frontmatter 라는 닫힌 구조 위의 술어다** — 정의역이 유한·열거 가능하고 결정표로 판정이 고정된다. **기계 강제가 실제로 가능한 자리는 여기다** |
    | 3 | **이 ADR 자신의 정직 불변식** — *지킬 수 없는 경계를 지킨다고 선언하지 마라*(ADR-181 §결정 2 `INV-N`·§결정 6). 수용 기준에 둔 채로는 매 라운드 "닫혔다" 를 쓰게 되고 매 라운드 반증된다 |
    | 4 | **무한 축 추가 경주를 구조적으로 종료**한다 |

    **천장 — 무엇이 미탐인가 (이름으로 적는다)**

    | # | 미탐 경로 | 실측 |
    |---|---|---|
    | **T-1** | ★★ **조합 회피 일반 미탐** — `분할` ∧ `키경쟁 패배` 동시 적용 시 전 leg 통과. **각각 단독은 RED 1** | 단독 `RED 1`/`RED 1` · **조합 `GREEN 0`** · 대조군(한 줄) `RED 2` (firsthand). ★ **재료 두 개가 이미 자기 mutant 코퍼스 안**(`x1 분할` · `e1 복제`)에 있었는데 **H-5 가 하나씩만 돌려 안 드러났다** |
    | **T-2** | ★★ **`N1` 은 축 V 가 구조적 공집합** — BODY 에 파싱 계층 부재. 앵커 줄 **안**의 분할·`<!---->` splice 가 GREEN | 대조군(한 줄) `RED` / 분할 `GREEN` / splice `GREEN` (firsthand). 처분 10 의 *"N1 도 상속"* 문장은 **삭제** |
    | **T-3** | **의미 축 미탐**(동의어·의역) — 유령 문자열 자체가 앵커이므로 전 축 미탐 | 처분 8 천장 그대로. 닫힌 적 없음 |
    | **T-4** | **표기 축 잔여** — ZWSP(U+200B) · 주석 splice 는 **전 자리** 통과. NFC 정규화는 ZWSP 를 제거하지 않는다 | T-2 splice 열이 동형 |
    | **T-5** | **rename 회피** — provenance 키(`b5`·`D-ESCAPE`)가 **경로 동일성**에 결속 | 미실측 — **미탐 후보**로만 적는다(실측 없이 단정하지 않는다) |
    | **T-6** | **열거자 밖 디렉터리** — 정의역 열거자가 `archive/adr/ADR-*.md` 이므로 `plugins/*/docs/adr/` 등은 밖 | ADR-181 정의역 표 1행 |

    - ★ **`b5` 는 (iv) 표 안에 판별을 남긴다** — 유령 leg 의 `m9` 를 잡는 유일 축이었으므로, 강등 후에도
      입장 조건 결정표에 **행 42** 로 판별이 존치한다(ADR-181 (iv) 신설 행). `b2` 도 같은 이유로 **행 41**.
    - ★ **"이제 닫혔다" 류 문장을 §9.4 전역에서 제거·범위 정정했다.** 남은 서술은 전부
      *"이 mutant 는 이 판에서 RED 였다"* 형태의 **관측 기록**이며 경계 주장이 아니다.
    - ★ **Phase 2 실 checker 착지는 선택이 아니라 필수다** — 수용 기준이 표 단독이 되었으므로,
      표가 강제되지 않으면 이 ADR 의 기계 강제는 **0** 이다. carrier `#2985` / 만기 `2026-09-15`.

### 9.5 declaration-only retain + ratchet 정합

- `mechanical_enforcement_actions: []` retain — 실 checker(`check_fix_ledger_conformance.py` + workflow +
  discriminating self-test)는 **Phase 2**. carrier = `mclayer/plugin-codeforge#2985` / 만기 `2026-09-15`.
  이 `[]` 는 ADR-181 §결정 5 ③ 의 형식(carrier·만기 주석 병기)을 따르며, 동일 PR 에 registry entry 가 존재한다.
  **그 사이 구간에서 9.1~9.4 의 강제력은 0 이며 이는 선언이다** — 이 문장을 지우면 over-claim 이 된다.
- ratchet 강화 방향: 값공간 additive · 카운터 정의역 무변경 · verdict 여집합 fail-closed 충전 ·
  닫기 조건 축 추가 · 실효 0 이던 문면 제거. **약화 0** — ADR-058 §결정 5 역-ratchet 정의역 밖.
- `is_transitional: false` 유지.

## Amendment 5+ (CFP-3017 carrier, provisional) — receiver floor 전환 + 위생 정의역 확장 + 노출면 근거 정정 + verdict relay 정의역 선언

> **번호 provisional 선언 (D-5a/AC-14)**: 본 Amendment 번호 "5+" 와 아래 결정 번호 10 은 **잠정값**이다. amendment 4 슬롯 + 결정 9 서수는 미머지 브랜치 CFP-2985 가 선점 중임을 firsthand 실측했다 — 재현: `git show origin/cfp-2985-fix-telemetry:archive/adr/ADR-RESERVATION.md | grep -n -A4 "adr_number: 67"` (→ `amendment_id: 4 / reserved_by_cfp: CFP-2985 / status: active`) + `git show origin/cfp-2985-fix-telemetry:archive/adr/ADR-067-fix-ledger-implementability-escalation.md | grep -n "^### 9\."` (→ 결정 9 서수 `9.1`~`9.5` 점유). 확정 규칙 = **"claim 은 잠정, 착지가 확정"** — 선착은 자기 provisional 값 그대로 / **후착 재계산 = 의무(조건부 아님)**: merge 직전 origin/main fresh 3-way 재확인(① 본 파일 frontmatter `amendment_log` 실제 max ② `ADR-RESERVATION.md` 동일 `adr_number` 하 타 claimant row — 미머지 브랜치 포함 ③ 병렬 open PR 실측) 후 다르면 관련 문면 전부 갱신 / **결번 허용 · 충돌 금지** (선례: ADR-141 amendment 10 · adr_number 173 결번).

Epic #3016 E-1 (CFP-3017). 사용자 확정 Q-2 = `쓰는 쪽 상한 제거 + 받는 쪽 최소 수용량` (Story CFP-3017 §5.5, 2026-08-18 — 재논의 금지 설계 입력). 신규 §결정 10 추가 only — §결정 1~8 의 헤딩·본문은 무편집(이력 보존)이며, §결정 5 의 길이 권장 문면·발화 조건 축소 문면과 §결정 7 의 노출면 근거 문장이 아래 명시 범위에서 **본 Amendment 로 대체**된다.

### 결정 10 — receiver floor 전환 + 위생 정의역 확장 + 노출면 근거 정정 + verdict relay 정의역 선언 (번호 provisional — 상단 선언 참조)

#### 10.1 Q-2: producer cap → receiver floor 전환 (숫자 리터럴 0)

처분 대상 2겹 — (a) §결정 5 의 `invariant_summary` `constraints: ["≤2 lines (≤200 chars 권장)"]` soft 권장 문면 (b) 계약 fix-event-v1 §3 의 `max_length: 50` / `max_length: 100` hard cap (실 편집 = Phase 2). **§2.4 축 1·2 의 처분 = 제3의 처분(무효화)** — ADR 값으로의 재동기화도, 계약값 채택도 아니다. 양쪽 모두 아래 2-part 형상으로 대체된다:

| key | 값 | 성격 |
|---|---|---|
| `receiver_min_accept` | **`unbounded`** (숫자 아닌 열거 술어) | 검증 가능한 key 보존 — `max_length` 슬롯 1:1 치환. AC-1 (다) 분기 술어("생산자 상한 문면 부재 ∧ 수용 하한 규범 존재") 충족 |
| `truncation_policy` | **`marked-truncation-required`** | head 보존 + tail 절단 + **필수 sentinel + 원본 포인터 + 원본 크기**, 절단 주체 = **수신자**, **침묵 절단 금지** |

**숫자를 쓰지 않는 이유 3**: ① 실효 수용 창(집행면의 줄 위치·줄 길이 창)은 문서화된 적이 없고, 어떤 N 을 선언해도 그 창 아래에서 거짓이 된다 — receiver floor 규범은 실제 수신 코드의 처리 창이 N 이상일 때만 참이므로 순서를 뒤집으면 규범이 공허해진다 ② 오늘 폐지하는 50/100 이 정확히 "산문에 숫자를 박은 결과"다(전사 drift — Story §2.3: 50 은 `transcript_ref` inline fallback 값의 전이, 100 은 상류 antecedent 0) ③ 집행면 창이 바뀌어도 서술 술어는 낡지 않는다. ⇒ **p90/관측 max 근접 산정 기준 제안은 기각** — 숫자를 쓰지 않으므로 산정 기준 자체가 무의미하다.

**AC-1 「차등 근거 명시」= 차등 없음 (긍정 답변)**: 두 cap 의 유래가 서로 다르고 어느 쪽도 필드 성질에서 도출되지 않았다. 차등의 근거가 애초에 부재하므로, 관측된 median 차이(1.22× vs 0.83×)를 새 차등의 근거로 삼으면 **드리프트 값을 사후 정당화**하는 것이 된다. ⇒ 두 sub-field 동일 처분 — 침묵 통과가 아니라 "차등 근거 = 부재임을 실측으로 확정"한 답변이다.

**정직 라벨 (효과 상한 — AC-13)** — `tier = advisory (effect-ceiling)`:

> ★ 위 한 줄이 **본 ceiling 의 tier 선언 라인**이며 `check-tier-honesty.py` `LEVERS` lever `cfp3017-effect-ceiling` 의 `label_re` 앵커다(선례 형식 — `progress-commit` lever 의 `tier = advisory (ceiling)` 동형, 리터럴은 disjoint). Axis1 = 이 라인 present / Axis2 = **이 라인**에 긍정 enforcement 토큰 부재. 아래 서술 bullet 은 근거이지 tier 선언이 아니다.
- 기계 소비자 **0** — 재현: `git grep -lE "reasoning_carryover|invariant_summary|disputed_claims" 6cc9a3a7b -- plugins/ scripts/ .github/ hooks/` → rc=1. ⇒ floor 는 **advisory** — "집행된다"고 서술하지 않는다.
- **floor 는 하한이지 상한이 아니다** — ADR-180 `read_cost` 팽창을 막지 못한다. 유일 실질 완화책(포인터 외부화)은 `story-read-declaration-registry.yaml`(CFP-2986 in-flight 신설)에 하드 의존 ⇒ read_cost 상한 미해결은 **알려진 잔여 리스크로 명시 라벨**한다(Non-goal 로 은닉하지 않는다).
- **외부 표준 인용 폭**: *producer hard cap 부재* = 3/3 지지 / *receiver floor 채택* = **1/3(RFC 5424 §6.1)만** 지지 [source: https://datatracker.ietf.org/doc/html/rfc5424 — "Any transport receiver MUST be able to accept messages of up to and including 480 octets"]. OTel 은 producer-side opt-in unbounded-default(`AttributeValueLengthLimit` Default=Infinity)이지 receiver floor 아님 [source: https://opentelemetry.io/docs/specs/otel/common/]. A2A 는 **침묵**(지지도 반박도 아님) [source: https://a2a-protocol.org/latest/specification/]. "3 표준 전부 receiver floor" 서술 = 과대인용 — 금지.
- **disanalogy**: RFC 5424 의 receiver 는 고정 buffer·물리 truncate 연산을 가진 daemon 이다. 본 시스템의 "수신자"는 Story 파일 셀을 프롬프트로 읽는 LLM 이며 **truncate 연산이 시스템에 존재하지 않는다** — 길면 더 많은 토큰을 읽을 뿐(비용↑) 잘리지 않는다.

#### 10.2 §2.4 축 5 — 계약 채택 + 본 ADR 개정 (5축 중 유일하게 처분 방향이 다른 축)

Story §2.4 의 계약↔ADR 5축 어긋남 전건 처분 (AC-6 — 미분류 잔량 0):

| # | 축 | 처분 | 소재 |
|---|---|---|---|
| 1 | `invariant_summary` 길이 (4× 협착 + soft→hard) | **제3의 처분 — 무효화** (10.1 형상 대체) | 본 Amendment + 계약 Phase 2 |
| 2 | `disputed_claims` 길이 (상한 신설) | **제3의 처분 (1 과 동형)** | 동상 |
| 3 | `disputed_claims` 타입 (축소) | **재동기화** — 계약이 §결정 5 원값 `list[string] \| string` 복원 | 계약 Phase 2 (AC-3) |
| 4 | 보안 invariant (계약 누락) | **재동기화 + 원자 결합** — §결정 7 을 계약에 이식, 같은 PR (AC-4) | 계약 Phase 2 |
| 5 | 발화 조건 (**확대 — 방향 반대**) | **계약 채택 + 본 ADR 개정** (아래) | 본 Amendment |

**축 5 개정 내용**: §결정 5 의 disjoint scope 3분기 중 **보존을 금지·축소하는 부분** — "debate 발동 FIX 시 = `reasoning_carryover = null`" 및 "일반 FIX = 양 field 모두 null 또는 생략"의 **null 강제 해석** — 을 계약의 기실무 문면(*"debate_artifact_ref 와 직교 — debate 발동 여부와 무관하게 reasoning 보존 가능"*, fix-event-v1 §3)에 맞춰 개정한다: **어느 발화 조건에서도 보존 가능(허용 확대)**. **의무 발동 조건(비-debate max-FIX 3/3 시 `reasoning_carryover` 의무)은 무변경.**

**왜 축 1~4 방향(ADR 로 재동기화)이 아닌가**: 축 1~4 는 계약이 ADR 보다 좁거나 문면이 없어 ADR 쪽으로의 재동기화가 자연스럽다. 축 5 는 **반대 — 계약이 이미 넓다.** ADR 문면으로 재동기화하면 채널이 좁아져(비-debate max-FIX 3/3 한정 회귀) 본 Story 의 목적(carryover 손실 감축)과 **정면 역행**한다. 축 5(발화 조건 = WHEN)와 anti-anchoring(전달 내용 = WHAT, 10.4)은 **직교 sub-issue** 라 같은 처분을 강제하지 않는다.

#### 10.3 §결정 7 위생 invariant 정의역 확장 + fail-fast 유지

| 대상 | 처분 | 근거 |
|---|---|---|
| `disputed_claims` | 유지 | §결정 7 원 대상 |
| `invariant_summary` | **확장 YES** | 현행이 `disputed_claims` 단독인 것은 의도된 협착이 아니라 **위치 유래** — §결정 5 YAML 에서 `security_invariant:` 키가 `disputed_claims` sub-field 아래에만 달려 있다 |
| `transcript_ref` | **확장하되 형태 다름** | 포인터 필드 ⇒ 금지 축 = 값 전문이 아니라 **private absolute-path** (§8.4 INV-SEC-1 어휘 재사용, 신규 어휘 0) |
| `lane_evidence.transcript` (Q-1) | **확장 YES — 우선순위 최상** | carrier = **ADR-031 Amendment 4** (CFP-3017 sibling). 의무 주체를 §14 append 시점 Orchestrator 로 한정해 ADR-031 자기 정의역 배제선 무저촉 |

**transcript 최우선 근거 3**: ① required · 전 lane 전 spawn — 노출 빈도가 구조적으로 최대(`reasoning_carryover` 는 optional + 비-debate max-FIX 3/3 한정) ② 길이가 억제 수단으로 작동한 적 없음 — 재현: `git grep -c "transcript" 6cc9a3a7b -- scripts/check-lane-evidence.sh` → rc=1 (50자 cap 미집행) ③ 값의 성질이 더 위험 — 워커 발화 **원문 조각** vs 설계 어휘 요약.

**fail-fast 유지 · 자동 redact 금지 (근거 3)**: ① 자동 redact 는 검출 가능성을 전제하는데 그 전제가 거짓 — 유일 집행 detector `_validate_reproducer_command` 의 `_SECRET_TOKENS` 는 **인자 이름**(`--token`/`token=`/`password=`)을 매치하지 값 형태를 매치하지 않고, 산문 필드에는 인자 이름이 없다 ⇒ redact 대상 식별 자체가 불성립 — 식별 못 하는 것을 자동 치환하면 거짓 보증만 생긴다 ② redact 는 원장을 변조한다 — §10 은 audit trail 이고 본 ADR 원문이 `audit 가능성`을 사유로 든다 ③ cap 폐지는 이 선택의 입력이 아니다 — cap 은 detector 도 redactor 도 아니었다.

**정직 라벨**: fail-fast 는 현재 **저작 규율**이다 — 집행 코드 0, 재현: `git grep -n "SCAN-A" 6cc9a3a7b -- scripts/ .github/ hooks/` → rc=1. "기계 차단"·"100% 기계강제"로 서술하지 않는다. 위생 검사를 신설한다면 ADR-171 warning tier 로 태어난다.

#### 10.4 AC-17 (b) — scope 분리 정의역 선언 (§결정 5 anti-anchoring 문장 무변경)

**개정 0 선언**: §결정 5 `transcript_ref` description 말미 문장 — *"Full transcript verbatim 회피 (Codex D6 — 이전 framing 고정 차단)"* — 은 **문면 그대로 유지된다.** 본 Amendment 는 그 문장을 개정하지 않는다.

**정의역 선언 (additive)**: 그 문장의 금지 **객체** = debate/FIX transcript(직전 라운드 대화·판정 사고 과정 전문)이고, 금지 **슬롯** = `transcript_ref` **포인터 필드**(전문 인라인 대신 링크)다 — 문장의 실 소재가 §결정 5 YAML 의 `transcript_ref` sub-field `description:` 멀티라인 마지막 줄임을 실측으로 확인했다(재현: `git show 6cc9a3a7b:archive/adr/ADR-067-fix-ledger-implementability-escalation.md | grep -n "Full transcript verbatim"`). **verdict relay 전달면(리뷰 verdict → FIX 워커 dispatch packet)은 그 정의역 밖이다** — 전달면의 객체 = review finding 본문(수리 대상 site 사실), 슬롯 = dispatch packet. 객체·슬롯 둘 다 다르다.

★**정직 병기 (over-claim 차단 — 필수)**: 이 실측은 *"저촉 없음"의 증명이 아니다* — §결정 5 본문 상단이 3-part 구조 전체의 근거를 서술하므로 확대 해석 여지가 남는다. 요구사항 lane(Story §2.6)의 "정면 저촉" 판정을 **뒤집는 것이 아니라 폭을 좁히는** 실측이다.

**구조적 은닉 = 면 분리** (선례 2건 위 확장 — `transcript_ref` "전문은 §9, 포인터만 전달" + ADR-182 리뷰/증적 정의역 분리. 신규 개념 아님):

| 면 | 담는 것 | 변경 |
|---|---|---|
| **감사면** — §10 원장 + review-verdict artifact + §9 라운드 기록 | 직전 판정값(결론·점수·severity) **전량 보존** | **0** |
| **전달면** — dispatch packet | finding **본문** + base SHA + 재현 명령. 직전 판정값 **미포함** | 신설 (packet 구성 규칙) |

- **재명명 금지 — 생략이다**: 판정값을 다른 이름으로 감싸면 감사 시 **매핑 테이블**이 필요해지고 그 테이블이 새 결합점·새 유출면이 된다. 감사면에 원본이 있으므로 생략의 정보 손실은 0 이다.
- **왜 "지시"가 아니라 "구조"인가**: anchoring 은 실증된 편향이고 매개체는 **직전 점수·판정값**이며, 지시형 완화(conventional strategies)로는 제거되지 않는다 — *"can not be eliminated by conventional strategies"* [source: arXiv 2505.15392, Understanding the Anchoring Effect of LLM] + reference answer score bias [source: arXiv 2506.22316, Evaluating Scoring Bias in LLM-as-a-Judge]. 따라서 packet **구성 규칙**이 그 필드를 담지 않는다 — 읽는 쪽에 "무시하라"고 말하지 않는다.
- **부수 이득**: 전달면에서 판정값을 빼면 packet payload 가 줄어 spawn gate scan-cap 압박(THR-2)이 같은 방향으로 완화된다.

**수용기준 3행 (신설 packet 구성 규칙 — 투입물의 성질로 명명, 양성 ∧ 음성 같은 라운드 공존 의무)**:

| 대조군 | 투입물 | 기대 |
|---|---|---|
| 양성 | 은닉 설계를 적용한 dispatch 산출물 (직전 판정값 0 ∧ finding 본문·base SHA·재현 명령 완비) | GREEN |
| 음성 | 그 산출물에 직전 판정값 **1종**(결론 또는 점수 또는 severity) 재삽입 | RED |
| 배선 자기보호 | 전달면 구성 규칙 검사의 배선·호출 제거 | RED |

검사 실물 배선 = Phase 2 + **ADR-171 warning tier** — 현 시점 실효는 저작 규율이다 (fail-open·bypass 가능, 기계 강제 아님 — 정직 라벨).

#### 10.5 §결정 7 노출면 근거 정정 (AC-19 — 무조건, Q-2 분기 무관)

**철회**: §결정 7 근거 문장 *"§10 FIX Ledger = public PR description 에 자동 mirror (`fix-ledger-sync.yml` Action) — secret 노출 surface"* 는 실측과 다르다 — 실 미러 = `octokit.rest.issues.createComment` 에 의한 **Issue comment** (재현: internal-docs `.github/workflows/fix-ledger-sync.yml` 에 `grep -n "issues.createComment"`), 그리고 미러 파서는 `cells[0]`~`cells[6]` 만 참조하므로 `reasoning_carryover` 는 **미러에 도달하지 않는다**.

| 근거 | 참인가 | carryover 위생을 지지하는가 |
|---|---|---|
| ① wrapper repo 가 PUBLIC | 참 | **아니다** — wrapper `docs/stories/` 추적 0행이라 carryover 가 wrapper 추적면에 존재할 경로 없음 |
| ② Issue comment 미러가 PUBLIC 으로 나감 (PRIVATE→PUBLIC cross-repo egress) | 참 | **아니다** — carryover 는 미러에 안 실린다. ②가 지지하는 것은 `트리거`·`원인 판정`·`재실행 범위` 다 |
| ③ consumer repo 공개성은 프로젝트별 | 참 (구조적) | **그렇다 — 유일한 살아있는 근거. §결정 7 은 ③ 단독으로 선다** |

**①②를 carryover 근거로 재사용하는 것도 같은 class 의 재발이다** — AC-19 는 `PR description` 표현만 금지하지만, ①②를 뭉뚱그려 인용하면 §결정 7 이 두 번째 거짓 근거를 얻는다.

**대체 문안 (§8.4 형 채택)**: *"§10 FIX Ledger 는 cross-repo Issue comment 로 미러되며(`fix-ledger-sync.yml` → 대상 Story Issue), 또한 consumer 프로젝트에서는 Story 파일 자체가 공개 추적면에 놓일 수 있다. `reasoning_carryover` 에 대한 노출 근거는 **후자**다 — 현행 미러 파서는 앞쪽 셀만 참조하므로 carryover 는 미러에 도달하지 않는다."*

★**AC-19 는 새 저작이 아니다** — §8.4 의 괄호 `(fix-ledger-sync.yml → Story Issue comment mirror)` 가 이미 정확했다. 즉 본 ADR 안에 §결정 7 거짓 근거의 자기교정 판본이 이미 존재하며, 본 항은 **§8.4 형으로의 내부 정합화**다. 단 **§8.4 머리 어구 `public PR mirror surface` 도 정정 대상이다** — "PR mirror" 는 실측(Issue comment)과 다르고 "public" 은 wrapper-self 축에서 carryover 미도달이라 실 근거가 아니다. §8.4 의 그 어구는 위 대체 문안으로 읽는다 (INV-SEC-1/INV-SEC-2 의 금지 내용 자체는 무변경 — 노출면 **명명**만 정정).

**계보 전파**: 그 모호 어구를 계약이 이미 상속했다 — 재현: `git grep -nE "INV-SEC|public PR mirror" 6cc9a3a7b -- docs/inter-plugin-contracts/fix-event-v1.md`. 철회된 근거의 계보가 ADR 밖으로 번진 상태이며(선례상 v1.4 `reproducer_command` 가 동형 인용 1회 실발생), 본 Story Phase 2 가 그 계약 파일을 여는 PR 이므로 **같은 PR 안에서 §8.4 형으로 동반 정정**한다 (AC-4 원자 결합).

#### 10.6 경계 · declaration-only retain

- **형제 계약 일반화 = 범위 밖**: stop-event-v1 / decision-packet-v2 / test-verdict-v2 의 soft 권장(120~500 대역)으로의 producer→receiver 원칙 일반화는 관찰 보고 + 별 carrier — 본 1줄 note 가 전부다.
- `mechanical_enforcement_actions: []` retain — 신규 blocking required context 신설 0, 본 Amendment 파생 검사는 전부 ADR-171 warning tier 로 태어난다 (Phase 2 carrier). 효과 상한 정직 라벨: 본 Amendment 는 "라운드 수 감소"를 성과로 주장하지 않는다.
- §결정 1~4·6·8 무접촉 — max-FIX 카운터·RESET semantics·replay disjoint 의미 invariant 변경 0.

## 관련 파일

- [ADR-181](ADR-181-verification-domain-deficit-normative.md) — 본 Amendment 4 의 owner_adr (P/V/D 정의·불변식 SSOT).
- [`skills/fix-ledger-schema/SKILL.md`](../../skills/fix-ledger-schema/SKILL.md) — 본 ADR §결정 1 / §결정 4 / §결정 5 narrative SSOT 본문 (호출 시점 + 핵심 룰).
- [`docs/inter-plugin-contracts/fix-event-v1.md`](../inter-plugin-contracts/fix-event-v1.md) — 본 ADR §결정 5 schema SSOT (v1.2 MINOR bump).
- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) — 본 ADR §결정 1 / §결정 2 / §결정 6 narrative SSOT (§6.4-6.6 절차).
- [`CLAUDE.md`](../../CLAUDE.md) — "FIX 루프" 단락 cross-ref 1 줄 (cap ≤320 정합).
- [`docs/adr/ADR-008-inter-plugin-contract-versioning.md`](ADR-008-inter-plugin-contract-versioning.md) — fix-event-v1 v1.1 → v1.2 MINOR bump 정책 anchor.
- [`docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md`](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — §결정 3 Orchestrator §10 monopoly invariant.
- [`docs/adr/ADR-052-codex-proactive-check-touchpoints.md`](ADR-052-codex-proactive-check-touchpoints.md) — pre-failure proactive check 분리 anchor.
- [`docs/adr/ADR-058-adr-sunset-criteria-mandate.md`](ADR-058-adr-sunset-criteria-mandate.md) — `is_transitional: false` permanent policy 분류 anchor.
- [`docs/adr/ADR-059-debate-protocol-v1.md`](ADR-059-debate-protocol-v1.md) — `debate_artifact_ref` ↔ `reasoning_carryover` disjoint scope anchor.
- [`docs/adr/ADR-064-decision-principle-mandate.md`](ADR-064-decision-principle-mandate.md) — 결정 원칙 forbid-list 8 어휘 정합 anchor.
- mclayer/codeforge-internal-docs `wrapper/stories/CFP-526.md` — 본 ADR carrier Story (Wave 1 doc-only fast-path).
- mclayer/plugin-codeforge#525 — parent Epic carrier Issue (Epic-FIX-ESCALATION-prevention).
