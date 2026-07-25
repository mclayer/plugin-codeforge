---
adr_number: 125
title: 요구사항리뷰 lane 신설 — 9번째 lane 의 게이트·라벨·배선 (ADR-124 S2 이행)
status: Proposed
category: governance
date: 2026-06-17
carrier_story: CFP-2326
parent_epic: "mclayer/plugin-codeforge#2324"
is_transitional: false
related_stories:
  - CFP-2326  # 본 ADR 신설 carrier (Epic CFP-2324 S2)
  - CFP-2350  # Amendment 2 carrier — runtime-failure internal-invariant falsification 변종 (Epic #2346 진단축 C, ADR-064 Amd 13 sibling)
  - CFP-2725  # Amendment 3 carrier — 결정 A(확정 위치 = 리뷰 PASS 후·설계 진입 전 정밀화) + 결정 B(내부 시스템 적합성 4번째 disjoint 축). ADR-159 SSOT 짝
related_adrs:
  - ADR-124  # S1 anchor — 외부지식 충당 3-단계 모델. 본 ADR 은 그 §결정 5 S2 row (요구사항리뷰 lane 실 wiring + 8→9 hard-commit) 의 이행 carrier. ②(작성측 self-check)↔③(리뷰측 producer 게이트) 깊이축 disjoint
  - ADR-052  # disjoint cross-ref (Amendment 아님) — touchpoint #4 작성측 synthesis self-check (단계②) ↔ 요구사항리뷰 lane producer 게이트 (단계③) 의 disjoint axis. "Requirements lane = synthesis not producer" 와 정합 (리뷰 lane 은 별개 producer)
  - ADR-059  # debate-protocol-v1 lane-agnostic — debate trigger.lane 식별자 분리 (requirements / requirements-review)
  - ADR-001  # lane-agnostic review subsystem 재사용 — RequirementsReviewPL = base 재사용, 신규 worker 신설 0
  - ADR-031  # §14 LANES 배열 — 7종 → 8종 ("요구사항-리뷰" 추가), wrapper-self Amendment 2 면제
  - ADR-063  # marketplace atomic invariant — codeforge-review plugin.json MINOR bump (description mirrored field 변경) marketplace sync 의무
  - ADR-064  # fast-pass ratchet invariant — guard additive, 비-요구사항리뷰 PR fast-pass 무손상 (INV-1)
  - ADR-039  # spawn mechanism disjoint axis — lane 개수 확장 = spawn 대상 enumeration 확장이지 spawn mechanism·whitelist 변경 아님, amendment 불요 (ADR-124 결정 4 답습)
  - ADR-049  # native Issue Type cutover — phase:* 라벨 single-active invariant 정합 (phase:요구사항-리뷰 추가)
  - ADR-119  # Amendment 2 — §결정 10 ② 실패 진단 판정면 umbrella anchor. runtime-failure 변종이 그 진단면을 요구사항리뷰 lane 측 falsification 게이트로 instantiate (외부사실 축과 disjoint 한 internal-invariant 축)
  - ADR-068  # Amendment 2 — I-8 standing invariant-surface. falsification packet 의 invariant-surface 입력 = I-8 surface (generative invariant sweep enumeration 완전성 보강)
  - ADR-159  # Amendment 3 — 요구사항 lane enrichment 일급 + design-entry 확정 gate SSOT (본 Amendment = lane 시퀀스·확정 위치·내부적합 검증축 짝)
  - ADR-071  # Amendment 3 — 짝 (발화 frequency 축 §결정 15/23, ADR-071 Amendment 15). 확정 발화 touchpoint
  - ADR-077  # Amendment 3 — 짝 (terminal event + counter + 리뷰-후 rewind, ADR-077 Amendment 1). 리뷰-후 rewind 의 리뷰 lane 대상
  # ADR-064 (Amendment 2 — §결정 13 root-cause 3rd rung sibling carrier) + ADR-124 (Amendment 2/3 — §결정 6 외부사실 휴리스틱 무약화, internal-invariant·내부적합 축 = 외부지식 3-단계 모델 internal 아날로그, cross-ref only) = 이미 위 related_adrs 등재
related_files:
  - archive/adr/ADR-125-requirements-review-lane.md
  - plugins/codeforge-review/agents/RequirementsReviewPLAgent.md
  - plugins/codeforge-review/templates/review-checklists/requirements.md
  - .github/workflows/phase-gate-mergeable.yml
  - templates/labels/base-labels.tsv
  - .github/workflows/auto-phase-label.yml
  - docs/inter-plugin-contracts/label-registry-v2.md
  - docs/inter-plugin-contracts/review-verdict-v4.md
  - plugins/codeforge-review/templates/review-pl-base.md
  - CLAUDE.md
  - docs/architecture/codeforge-family.md
amendments:
  - number: 1
    by: "CFP-2341"
    date: "2026-06-18"
    title: "lane 카운트 off-by-one 정정 — 8→9 가 아니라 9→10"
  - number: 2
    by: "CFP-2350"
    date: "2026-06-19"
    title: "runtime-failure 변종 신설 — internal-invariant ground-truth falsification 축 (외부사실 mandate 와 disjoint)"
  - number: 3
    by: "CFP-2725"
    date: "2026-07-17"
    title: "결정 A(사용자 최종 확정 = 리뷰 PASS 후·설계 진입 전 위치 정밀화) + 결정 B(내부 시스템 적합성 4번째 disjoint 검증 축 — Amd2 internal-invariant 선례 답습)"
amendment_log:
  - by: "CFP-2341"
    date: "2026-06-18"
    scope: "Amendment 1 — lane 카운트 off-by-one 정정. 본문(제목·§결정 1·근거)이 요구사항리뷰를 '9번째 lane', 카운트 전이를 '8→9 hard-commit' 으로 기술했으나 이는 기존 lane enumeration off-by-one 에서 비롯된 오기다. 기존 lane 시퀀스(요구사항·설계·설계리뷰·구현·구현리뷰·통합테스트·보안테스트·배포·배포리뷰)는 실제로 9개이고 기계 SSOT templates/labels/base-labels.tsv 의 lane phase 라벨은 요구사항리뷰 추가 후 10개다 → 정본 카운트 = 10 (요구사항리뷰 = 10번째로 추가된 lane, 전이 = 9→10). §결정 1 의 lane 신설 결정 자체(위치·additive 신설·기존 lane 무손상·branch protection required contexts 무변경)는 무변경 — 카운트 표기 수치만 정정(약화 0). 전파: CLAUDE.md '10 레인' + docs/architecture/codeforge-family.md '10 lane' 정합. label-registry-v2.md description 내 '9번째 lane' 문자열은 다음 registry version bump 시 일괄 정정(deferred, 기능 영향 0)."
    sunset_justification: "본 Amendment 는 약화가 아니라 표기 오기 정정이다 — 정책·게이트·라벨·배선 변경 0건, 수치 표기(9번째→10번째, 8→9→9→10)만 정본화한다. ADR 본체 status = Proposed 유지, §결정 1~6 의미 불변. additive 정정이므로 ratchet 강화 방향이며 sunset 대상이 아니다. 원의도(요구사항리뷰 additive lane 신설)는 무손상 — 카운트 정합만 보강. ADR-058 §결정 5 self-application (Amendment 시 sunset_justification 의무) 정합."
  - by: "CFP-2350"
    date: "2026-06-19"
    scope: |
      Amendment 2 — runtime-failure Story 변종 신설. 요구사항리뷰 lane 은 현재 외부사실 의존 검증(§결정 6, ADR-124 단계③) 축이다. 본 Amendment 는 runtime-failure Story 변종을 추가 — internal code/invariant ground-truth falsification 축(외부지식이 아니라 내부 코드·invariant). ADR-124 외부지식 3-단계 모델의 internal-invariant 아날로그다.
      ADR-064 Amendment 13(§결정 13 root-cause 사다리 3rd rung — 문제정의 오류 → 요구사항 lane 재진입)의 sibling carrier. runtime-failure Story 재진입 시 요구사항리뷰 lane 이 falsification 게이트로 instantiate: 기존 dual-peer(Claude+Codex) + debate-protocol 재사용(신규 worker 0, ADR-001 lane-agnostic), packet = {코드,증상,outcome-contract,invariant-surface}(가설 숨김 — hypothesis-withheld). 비대칭 verdict 규칙 = file:line 위반 invariant 1개 > "OK" N개(ADR-064 §결정 13 규율과 동일, 게이트 verdict 레벨).
      외부사실 축과 disjoint(ADR-124 §결정 6 무약화) — 외부사실 검증(표준/CVE)과 internal-invariant 검증은 별개 축, 공존(외부사실 mandate 대체·약화 0). review-verdict-v4 의 runtime-failure/invariant-violation verdict enum + 비대칭 self-check field 추가 = 별도 carrier Phase 2 defer(review-verdict-v4.md 무수정 — 본 Story 미접촉, 병렬 충돌 회피). RequirementsReviewPL/Claude/CodexReviewAgent checklist 배선 = Phase 2 defer. 본 Amendment = declarative 선언만.
      §결정 1~6 + Amendment 1 무수정(additive only). ratchet 강화 방향(축 추가 = 검증 표현력 확장, scope 약화 0).
    direction: strengthen
    sunset_justification: "본 Amendment 는 약화가 아니라 additive 축 신설이다 — 기존 외부사실 의존 검증 축(§결정 6, ADR-124 단계③)을 대체·약화하지 않고 internal-invariant ground-truth falsification 축을 별개 axis 로 추가(공존). §결정 1~6 + Amendment 1 의미 불변, 기존 dual-peer/debate-protocol 재사용(신규 worker 0). review-verdict-v4 / checklist 배선 = Phase 2 defer(본 Story 무수정). additive 강화 방향이므로 sunset 대상이 아니다. ADR-058 §결정 5 self-application(Amendment 시 sunset_justification 의무) + ADR-064 §결정 7 evidence-gated symmetric ratchet 강화 방향 정합. 원복은 별 Story 의 명시 결정으로만 가능하며 그 경우에도 ADR-058 §결정 5 약화 evidence-gate 를 따른다."
  - by: "CFP-2725"
    date: "2026-07-17"
    scope: |
      Amendment 3 — 요구사항 lane 사용자 대화 프로세스 정식화 (신규 ADR-159 의 lane 시퀀스·확정 위치·내부적합 검증축 짝). Amendment 2 의 additive-disjoint-axis 패턴 답습. 2부:
      (결정 A) **§결정 1 위치 정밀화 — 사용자 최종 확정 checkpoint = 요구사항리뷰 PASS 후·설계 진입 전**: 요구사항리뷰 lane 신설(§결정 1) 위 = Phase 1 내부 sub-gate. 본 Amendment 는 그 시퀀스에 사용자 최종 확정 checkpoint 의 정밀 위치(요구사항리뷰 PASS 후·설계 진입 직전)를 명문화한다 — `요구사항(why대화+enrichment) → 요구사항리뷰(외부사실+내부적합) → 사용자 최종 확정 → 설계`. **lane count 10 무변경 · required contexts 무변경 invariant 상속**(Amendment 1 lane 카운트 정본 10 + §결정 2 required contexts 무변경). 확정 gate = sub-gate 순서 정밀화이지 lane 추가 아님. BABOK approve-after-verify+validate 입력-의존성 정합. 배선 = Phase 1 playbook preflight advisory(ADR-159 결정 3), 신규 phase 라벨/required context = Phase 1 채택 금지(advisory ceiling).
      (결정 B) **§결정 6 scope 확장 — 외부사실 only → 외부사실 + 내부 시스템 적합성 (4번째 disjoint 축)**: 요구사항리뷰 lane 의 검증 scope 에 "내부 시스템 적합성" 독립 검증 축을 추가한다 — dual-peer(Claude/Codex)가 설계문서(ADR·Change Plan)·과거 Story·ADR 을 Read 대조로 아키텍처 구현가능성·과거 결정 충돌·중복을 검증. 이는 Amendment 2 (internal-invariant ground-truth falsification 축, runtime-failure 한정)의 **scope 일반화** — 그 additive-disjoint-axis 패턴의 3번째 disjoint 축(일반 내부적합, runtime-failure 한정 아님). **검사연극 비충돌(born-broken 방지, 명세 필수)**: 내부적합 축 = repo-내부 문서 Read 기반(WebSearch 강제 아님 — 외부사실 축 도구 WebSearch 와 tool-disjoint), declarative-only null-valid(적합 이슈 0건 = 정상 PASS, 억지 결함 조작 금지), 작성측 Feasibility(§4.2)/Continuity(§4.3) 자가분석과 disjoint 2차(generator≠verifier, §결정 4 disjoint 동형), hypothesis-withheld packet(작성측 진단 숨김 — Amd2 packet 규율 상속). ADR-125:142 검사연극 금지 원문 = "내부-only 결론에 외부조사 강제" 만 금지 — 내부문서 Read 정합검증은 대상 아님.
      §결정 1~6 + Amendment 1/2 무수정(additive only). ratchet 강화 방향(축 추가 = 검증 표현력 확장 + 확정 위치 정밀화, scope 약화 0). review-verdict category literal(`internal-fitness-*`) 신설 + RequirementsReviewPLAgent/requirements.md checklist 배선 + phase 라벨 wiring = **Phase 2 defer**(review-verdict-v4.md / checklist 무수정 — 본 Story 미접촉, 병렬 충돌 회피). 본 Amendment = declarative 선언만. 신규 ADR-159 SSOT / ADR-071 Amendment 15(발화 frequency) / ADR-077 Amendment 1(terminal event·counter·리뷰-후 rewind) 짝. ADR-124 amendment 불요 — Amd2 도 ADR-124 cross-ref 만 처리(내부적합 = 외부지식 3-단계 internal 아날로그).
    direction: strengthen
    sunset_justification: "본 Amendment 는 약화가 아니라 additive 축 신설 + 위치 정밀화다 — 결정 A(확정 checkpoint 위치 정밀화)는 §결정 1 lane 신설·§결정 2 required contexts 무변경 invariant 를 상속(lane count 10 무변경, sub-gate 순서 정밀화이지 lane 추가 아님). 결정 B(내부 시스템 적합성 축)는 기존 외부사실 의존 검증 축(§결정 6)을 대체·약화하지 않고 disjoint axis 로 추가(공존) — Amendment 2 internal-invariant 축의 scope 일반화. §결정 1~6 + Amendment 1/2 의미 불변, 기존 dual-peer/debate-protocol 재사용(신규 worker 0), 검사연극 비충돌(repo Read 기반·WebSearch 비강제·declarative-only null-valid). review-verdict-v4/checklist/phase 라벨 배선 = Phase 2 defer(본 Story 무수정). additive 강화 방향이므로 sunset 대상 아니다. ADR-058 §결정 5 self-application + ADR-064 §결정 7 evidence-gated symmetric ratchet 강화 방향 정합. 원복은 별 Story 명시 결정으로만 가능하며 그 경우에도 ADR-058 §결정 5 약화 evidence-gate 를 따른다."
  - by: "CFP-2782"
    date: "2026-07-22"
    scope: |
      Amendment 4 — canonical 작업레인 수 10 → 8 (authority = ADR-121 deploy·deploy-review 2 lane 물리 제거). Amendment 1 이 정본화한 canonical=10(요구사항리뷰 추가 후)에서 deploy·deploy-review 2 lane 이 CFP-2782/ADR-121 로 물리 제거되어 canonical=8 로 갱신 — 최종 8 lane = 요구사항 · 요구사항리뷰 · 설계 · 설계리뷰 · 구현 · 구현리뷰 · 통합테스트 · 보안테스트.
      REQUIRED mechanical-sync carrier 항 (check_lane_count_ssot.py docstring 이 지정한 의무): N-range 검출 regex flip — "8" 을 stale flag set 에서 제외(canonical화) + "10" 을 stale flag set 에 편입(두 자리 alternation, 상수 bump 아님) + self-test fixture 반전(§8.1/§8.2 SSOT: F-DET-2 "8 레인" FLAG→no-FLAG / F-EXIT-0 "10 레인" no-FLAG→FLAG / F-TRANS-2 "10번째 lane"→"8번째" / Mutation-5 anchor). 실 script/fixture 편집 = Phase 2 구현 scope(scripts/lib/check_lane_count_ssot.py + wrapper + test) — 본 Amendment 는 canonical SSOT 값 갱신 + mechanical-sync 의무 명문화.
      Amendment 1 canonical=10(요구사항리뷰 추가 시점) = frozen 역사 기록(0건 변경, Event Sourcing). §결정 1~6 + Amendment 1/2/3 의미 불변 — lane 신설 결정 자체 무변경, 수치 SSOT(10→8)만 갱신. ADR 본체 status = Proposed 유지.
    direction: corrective
    sunset_justification: "canonical lane count 10 → 8 = ADR-121 deploy·deploy-review 2 lane 물리 제거 반영(numeric SSOT sync). 요구사항리뷰 lane §결정 1~6 게이트·라벨·worker 무손상 — lane 신설 결정 자체 무변경, 수치 표기만 정본화. count 하향은 정책 약화가 아니라 상위 ADR-121 로 제거된 lane 의 SSOT 반영(reflect-upstream). ADR-058 §결정 5 / ADR-064 §결정 7 정합 — governance surface(요구사항리뷰 게이트) 약화 0. is_transitional: false 유지. 원복(deploy lane 재도입)은 별 Story 명시 결정으로만 가능하며 그 경우에도 ADR-058 §결정 5 약화 evidence-gate 를 따른다."
---

# ADR-125: 요구사항리뷰 lane 신설 (9번째 lane)

## 상태

Proposed (2026-06-17 KST, CFP-2326 carrier — Epic [#2324](https://github.com/mclayer/plugin-codeforge/issues/2324) S2). `is_transitional: false` — 영구 거버넌스 결정 기록. 본 ADR 은 [ADR-124](ADR-124-external-knowledge-provisioning-model.md) §결정 5 의 **S2 row (요구사항리뷰 lane 실 wiring + 8→9 카운트 hard-commit + 게이트 설계)** 의 이행 carrier 다.

## 본질 선언

> **요구사항리뷰를 9번째 lane 으로 신설한다.** 위치 = Phase 1 내부 sub-gate (요구사항 §1-7 직후, 설계 진입 전 — `요구사항 → 요구사항리뷰 → 설계`). 외부지식 충당 3-단계 (ADR-124 결정 1) 중 **단계③ (깊은 다출처 검증) 의 주 발동 lane**. 작성측 self-check (ADR-052 touchpoint #4, 단계②) 와 리뷰측 독립 producer 게이트 (본 lane, 단계③) 는 깊이축에서 disjoint 한 2-layer 로 공존한다. 본 ADR 은 게이트 trigger·phase 라벨·branch protection·lane 배선·review-verdict enum 확장을 hard-commit 하며, deep-research 차등 실구현 (S3) / Researcher 재초점 (S4) / on-demand 깊은 검증 (S5) 은 본 ADR 범위 밖 (ADR-124 결정 5 deferral 경계 보존).

## 컨텍스트

ADR-124 (S1) 가 외부지식 충당 3-단계를 박제하면서, 단계③ (깊은 다출처 검증) 의 **주 발동 lane = 요구사항리뷰** 로 식별했으나, 그 lane 의 실 게이트 trigger·라벨·배선·8→9 카운트는 의도적으로 S2 로 deferral 했다 (ADR-124 §결정 5 표). 본 ADR 은 그 S2 row 를 이행한다.

기존 흐름은 `요구사항 → 설계 → 설계리뷰 → 구현 → ...` 의 8 lane 이었다. 요구사항 산출물 (Story §1-§6 + 사용자 원문) 은 외부 개념·시장·표준 사실에 가장 자주 의존하지만, 설계 진입 전 그 외부사실 의존성을 독립 검증하는 게이트가 없었다. 작성측 ADR-052 touchpoint #4 (Codex proactive self-check) 가 작성 *직후* 결정-범위 얕은 보강을 하지만, 이는 **작성 주체 자신의 self-check (단계②)** 이지 독립 검증 주체의 깊은 검증 (단계③) 이 아니다.

본 ADR 이 메우는 공백:

1. **9번째 lane 부재** — 요구사항 결론의 외부사실 의존성을 설계 진입 전 검증하는 독립 게이트가 없었다.
2. **게이트 wiring 부재** — phase 라벨·branch protection required gate·fast-pass guard·review-verdict enum 이 요구사항리뷰 lane 을 인식하지 못했다.

## 결정

### 결정 1 — 요구사항리뷰 lane 신설 (Phase 1 내부 sub-gate, 8→9 hard-commit)

요구사항리뷰를 **9번째 lane** 으로 신설한다. lane 시퀀스 = `요구사항 → 요구사항리뷰 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 통합테스트 → 보안테스트 → 배포 → 배포리뷰`.

- **위치 = Phase 1 내부 sub-gate**: 요구사항 §1-7 산출 직후, 설계 lane 진입 전. 설계리뷰가 Phase 1 말미 sub-gate 인 선례와 정합 (Phase 1 PR 안에서 요구사항·요구사항리뷰가 함께 처리되는 구조).
- **8 → 9 lane hard-commit**: ADR-124 §결정 5 가 S2 로 deferral 했던 카운트 hard-commit 을 본 ADR 이 확정한다. 기존 8 lane 무손상 — additive 신설.
- **lane 개수 ≠ plugin 개수**: 본 신설은 신규 plugin 을 만들지 않는다. `codeforge-review` 1 plugin 이 이미 설계리뷰·구현리뷰·보안테스트 3 lane 을 host 하며, 요구사항리뷰가 4번째 host lane 이 된다 (1 plugin 다 lane). plugin 개수 = 8 무변경 (ADR-118 D3).

### 결정 2 — branch protection required gate = phase-gate-mergeable.yml 내부 required.gates 배열 (required contexts 무변경)

요구사항리뷰 게이트는 **advisory 가 아니라 required** 다. 단, branch protection contexts (CLAUDE.md "브랜치 보호" SSOT) 은 무변경이다.

- 실 enforce = `phase-gate-mergeable.yml` 의 `required = { phase, gates: [...] }` 평가 내부에 `phase:요구사항-리뷰 → gate:requirements-review-pass` 매핑 branch 추가 (결정 3). 이미 required 인 `check-gate` job 의 내부 평가 분기 확장이므로, GitHub branch protection `required_status_checks.contexts` 은 건드리지 않는다.
- 근거: branch protection contexts 변경은 CFP-1808 Amendment 2 가 ratchet 증가로 확정한 required context baseline 을 건드리는 민감 surface 다. 기존 6 lane gate 가 모두 동일 `phase-gate-mergeable` context 1개로 enforce 되는 패턴 (per-lane context 신설 0) 을 답습한다 — 신규 lane gate 도 같은 context 내부 분기로 흡수.

### 결정 3 — fast-pass guard 설계 (해법 A — guard ∧ required branch 쌍, INV-1~4)

`phase-gate-mergeable.yml` 에 **2개 변경을 쌍으로** 적용한다. 해법 B (required block else fall-through 단독) 는 required contexts 변경을 수반하므로 금지하고, 해법 A 를 채택한다.

1. **fast-pass guard** (`isDocOnly` 계산 직후): `phase:요구사항-리뷰` 부착 ∧ `gate:requirements-review-pass` 미부착 → `isDocOnly = false` 강제 (fast-pass 제외, required block 으로 fall-through). **additive** — 다른 PR 의 `isDocOnly` 무변경 (ADR-064 ratchet 보존).
2. **required block phase branch** (현재 require 평가의 else 보다 위에 신규 branch 삽입): `phaseLabel === 'phase:요구사항-리뷰' || phaseLabel === '요구사항-리뷰' → required = { phase, gates: ['gate:requirements-review-pass'] }`. **누락 시 else → gate:design-review-pass 오요구 = wrong-gate deadlock** 이므로 반드시 쌍으로 적용.

4-invariant (게이트 정합성):

| Invariant | 의미 | 보장 |
|---|---|---|
| **INV-1 (ratchet)** | 비-요구사항리뷰 PR 의 fast-pass 불변 | guard 가 `phase:요구사항-리뷰` 부착 PR 만 좁게 target — 다른 PR 의 `isDocOnly` 경로 무손상 (ADR-064 §결정 7 ratchet 강화 방향) |
| **INV-2 (no-deadlock)** | gate 부착 시 success 종착 경로 보장 | required branch 가 `gate:requirements-review-pass` 1개만 요구 — 부착 시 `gateOk=true` → success |
| **INV-3 (no wrong-gate)** | else → design-review-pass 오요구 차단 | required block 에 요구사항-리뷰 전용 branch 를 else *위에* 삽입 (else 도달 불가) |
| **INV-4 (enforce)** | gate 미부착 시 action_required | guard 로 fast-pass 제외 + required branch 로 gate:requirements-review-pass 요구 → 미부착 시 `gateOk=false` → action_required |

**gate comment evidence** (CFP-133 일관성): `lanePrefixForGate` 맵에 `'gate:requirements-review-pass': '[요구사항-리뷰]'` 추가 (P1). comment regex 가 `PASS|N/A` 인식 — label 미부착 autonomous mode 에서 PR comment evidence 로 gate 인정 (기존 design/security gate 와 동형).

**fast-pass invariant 무손상 명시**: 본 guard 는 fast-pass OR-gate (isEpicLabel ∨ isSiblingPr ∨ isDocOnly ∨ isPostMergeFix ∨ isChoreOnly) 자체를 약화하지 않는다. `isDocOnly` 1개를 요구사항리뷰 부착-미pass 조합에서만 좁게 false 로 강제할 뿐, 다른 4 source 와 다른 PR 의 isDocOnly 는 무변경 (ADR-064 ratchet invariant).

### 결정 4 — 작성↔리뷰 disjoint axis (②↔③ 깊이축, ADR-052 Amendment 불요)

ADR-052 touchpoint #4 (작성측 Codex proactive synthesis self-check, **단계②**) 와 요구사항리뷰 lane (리뷰측 독립 producer 게이트, **단계③**) 는 **disjoint axis** 로 공존한다.

- **단계② (작성측)**: 요구사항 작성 주체 (RequirementsPL + codex-proactive-check) 가 작성 직후 결정-범위 얕은 보강을 한다. ADR-052 "Requirements lane = synthesis not producer" 와 정합 — 작성 lane 은 synthesis 주체.
- **단계③ (리뷰측)**: 요구사항리뷰 lane 의 독립 검증 주체 (RequirementsReviewPL → Claude/Codex dual-peer) 가 외부사실 의존 결론을 깊이 다출처 검증한다. 리뷰 lane 은 **producer** (작성 lane 의 synthesis 와 별개 axis — 검증 산출물을 생산).
- **debate trigger.lane 분리**: 작성 = `requirements`, 리뷰 = `requirements-review` (별개 lane 식별자). ADR-059 debate-protocol-v1 lane-agnostic 정합 — trigger.lane 식별자가 작성/리뷰로 분리되어 채널이 섞이지 않는다.
- **ADR-052 silent override 금지**: 본 lane 신설은 ADR-052 touchpoint #4 를 대체·약화하지 않는다 (두 채널 공존). ADR-052 의 의미 변경 0건이므로 **ADR-052 는 Amendment 격상 불요** — 본 ADR 이 ADR-052 를 cross-ref 만 한다. (ADR-052 본문 무수정.)

### 결정 5 — review-verdict enum 확장 + RequirementsReviewPL base 재사용 (ADR-001 lane-agnostic)

요구사항리뷰 lane 은 기존 lane-agnostic review subsystem (ADR-001) 을 재사용한다 — **신규 worker 신설 0건**.

- **review-verdict enum 확장**: `lane: design | code | security` → `requirements-review` 추가. 리뷰 lane 식별자 = `requirements-review` (작성 lane `requirements` 아님 — 본 lane 은 리뷰 producer). review-verdict-v4.md + review-pl-base.md §2 양쪽 + (조건부) review-verdict-v3.md. CodexReviewAgent / ClaudeReviewAgent 의 lane-conditional hard-check 에 `requirements-review` branch 추가 (MINOR — story_key 필수 + 요구사항 산출물 Read 가능).
- **RequirementsReviewPL = base 재사용**: 신규 PL agent (`RequirementsReviewPLAgent.md`) 는 `templates/review-pl-base.md` SSOT 를 참조하고 lane-specific 4가지 (워커 packet · FIX 카운터 · 검증 스코프 · 다음 게이트) 만 본문에 명시 (DesignReviewPL 패턴 답습). worker = 기존 ClaudeReviewAgent ∥ CodexReviewAgent dual-peer 그대로.
- **ADR-052 정합**: ADR-052 "Requirements lane = synthesis not producer" 는 *작성 lane* 의 진술이다. 요구사항리뷰 lane 은 *리뷰 lane* 이므로 producer 다 (별개 axis — 결정 4 disjoint). 충돌 0건.

### 결정 6 — 깊은 검증 발동 = ADR-124 결정 2 외부사실 의존 게이트 (검사연극 금지, declarative-only)

요구사항리뷰 lane 의 깊은 다출처 검증 (단계③) 발동은 **무조건이 아니다** — ADR-124 결정 2 의 외부사실 의존 게이트를 본 lane 에 instantiate 한다.

- **외부사실 의존 게이트**: 리뷰 결론이 외부지식 (산업 표준·RFC·법규·벤더 동작·CVE 등) 에 의존하는 곳에만 깊은 검증을 적용한다. 결론이 내부 코드·내부 규칙·팀 암묵지식만으로 닫히면 깊은 외부조사를 강제하지 않는다 (**검사연극 금지** — ADR-119 §결정 6 "'조사했으므로 옳다' 단정 금지" SSOT).
- **매 Story 강제 아님 (declarative-only)**: ADR-124 결정 3 의 적합도 표 (요구사항리뷰 = 高/주) 는 *발동 잠재력* 이지 매 Story 강제 발동이 아니다 (ADR-119 §결정 8 declarative-only 패턴 정합). 실제 발동 = 외부사실 의존 게이트가 결정.
- **②↔③ 깊이 임계 + 경계(?) 항목 운영 판정**: ADR-124 결정 6 휴리스틱 (의존 O: 팩트체크·벤더·표준·CVE / X: 팀 암묵지식·내부 코드 / 경계(?): 시장정보·벤치마크·StackOverflow 등 준-외부 출처) 을 인용한다. ADR-124 가 경계(?) 항목의 *최종 확정* 을 S2 게이트 설계에 deferral 했으므로, 본 ADR (S2 게이트 설계) 가 **운영 판정** 을 다음과 같이 lock-in 한다 (scope creep 회피):
  - **경계(?) 준-외부 출처 = 단계② (작성측 얕은 자가 조사) 우선**. 단계③ 강제 발동 대상이 아니다.
  - 다만 리뷰어 재량으로 단계③ escalation 가능 (외부사실 의존 정도가 높다고 판단 시). 이 escalation 은 강제가 아니라 리뷰어 판단 — 검사연극 차단과 정합.
  - 이 운영 판정은 깊은 검증의 *차등 실구현* (S3) / on-demand 경로 (S5) 와 disjoint — 본 ADR 은 "언제 발동하는가" 의 게이트 판정만 확정하고, 깊이의 차등 메커니즘 실구현은 S3 로 보존.
- **abstention escape 정합**: 출처 확보 불가 시 ADR-119 §결정 3.2 "확인 불가/추정" 명시 후 진행 (데드락 회피).

## cross-ref 의무 (각 관계 명시)

본 ADR 은 기존 ADR 들의 이행·재사용이며, 어느 기존 ADR 도 약화·재규정하지 않는다.

| 기존 ADR | 인용 지점 | 관계 |
|---|---|---|
| ADR-124 §결정 5 (S2 row) + 결정 6 | 결정 1·6 | **이행 carrier** — S1 anchor 가 deferral 한 S2 영역 (lane wiring + 8→9 hard-commit + 게이트 설계 + 경계(?) 운영 판정) 의 실현. deferral 경계 (S3/S4/S5) 무침범. |
| ADR-052 (touchpoint #4) | 결정 4 | **disjoint cross-ref (Amendment 아님)** — 작성측 self-check (단계②) ↔ 리뷰측 producer 게이트 (단계③) 의 깊이축 disjoint. ADR-052 의미 변경 0 → Amendment 격상 불요. ADR-052 본문 무수정. |
| ADR-059 (debate-protocol-v1) | 결정 4·5 | **lane-agnostic 재사용** — debate trigger.lane 식별자 분리 (requirements / requirements-review). protocol 무변경. |
| ADR-001 (review-agent-unification) | 결정 5 | **lane-agnostic 재사용** — RequirementsReviewPL = base 재사용, 신규 worker 신설 0. |
| ADR-031 §14 LANES | related_files | LANES 배열 7종 → 8종 ("요구사항-리뷰" 추가). wrapper-self dogfood §14 면제 (ADR-031 Amendment 2) 이므로 본 변경은 lane name set SSOT 정합 목적. |
| ADR-063 (marketplace atomic) | bump | codeforge-review plugin.json MINOR bump (1.12.3 → 1.13.0, 신규 agent surface). description = mirrored field 변경 → marketplace sync 의무 (실 sync = Orchestrator/GitOps). |
| ADR-064 §결정 7 (fast-pass ratchet) | 결정 3 | INV-1 — guard additive, 비-요구사항리뷰 PR fast-pass 무손상 (ratchet 강화 방향). |
| ADR-039 §결정 1·2 (spawn mechanism) | — | **disjoint axis** — 9번째 lane 추가 = spawn 대상 enumeration 확장이지 spawn mechanism·closed 4-entry whitelist 변경 아님. ADR-039 영향 0 — amendment 불요 (ADR-124 결정 4 답습). |
| ADR-049 (native Issue Type) | label | phase:* 라벨 single-active invariant 정합 — phase:요구사항-리뷰 single_active:true 추가. |
| CFP-1808 Amendment 2 (branch protection contexts) | 결정 2 | **무변경** — branch protection contexts 무손상, required gate 는 phase-gate-mergeable 내부 평가 분기로만 enforce. |

## 근거

- **요구사항 외부사실 검증의 독립 게이트**: 요구사항 결론이 외부 개념·시장·표준 사실에 가장 자주 의존하므로 (ADR-124 결정 3 적합도 高/주), 설계 진입 전 독립 검증 게이트가 ADR-124 의 단계③ 를 실 enforce 한다.
- **2-layer 공존 (검사연극 차단)**: 작성측 self-check (단계②) 와 리뷰측 깊은 검증 (단계③) 의 disjoint 2-layer 가 작성 주체의 self-bias 를 독립 검증으로 보완하되, 외부사실 의존 게이트 (결정 6) 로 무조건 발동을 차단해 검사연극을 막는다.
- **재사용 (신설 최소)**: ADR-001 lane-agnostic review subsystem 재사용 — 신규 worker 0, base 재사용, enum additive 확장. 기존 자산 최대 활용.
- **약화 0 (ratchet 강화)**: additive lane 신설 — 기존 8 lane·게이트·라벨 무손상 (결정 1·3 INV-1). branch protection required contexts 무변경 (결정 2).
- **scope 경계 보존**: 게이트 wiring (S2) 만 hard-commit, 깊은 검증 차등 실구현 (S3) / Researcher 재초점 (S4) / on-demand 경로 (S5) 미침범 (ADR-124 결정 5 deferral 경계).

## 결과

- 요구사항리뷰 lane 의 게이트·라벨·배선 SSOT 신설 — ADR-124 단계③ 주 발동 lane 의 실 wiring.
- mechanical_enforcement_actions: phase-gate-mergeable.yml guard + required branch + lanePrefixForGate / base-labels.tsv 3 row / auto-phase-label.yml LANE_MAP / label-registry-v2 3 entry / review-verdict enum 확장 / RequirementsReviewPLAgent + requirements.md checklist / codeforge-review plugin.json bump (1.13.0).
- 깊은 검증 차등 실구현 (S3) / Researcher 재초점 (S4) / on-demand 경로 (S5) = 별 carrier (ADR-124 결정 5 deferral 경계 보존).

## Amendment 1 (2026-06-18) — CFP-2341 — lane 카운트 off-by-one 정정 (8→9 가 아니라 9→10)

### 성격

본 Amendment 는 **표기 정정**(오기 수정)이다. ADR 본체 status 는 **Proposed 유지** — 결정 1~6 의 정책·게이트·라벨·배선은 불변이며, 본 Amendment 는 lane 카운트 *표기 수치* 만 정본화한다 (약화 0건, additive 정정).

### 컨텍스트

본 ADR 본문(제목·§결정 1·근거)은 요구사항리뷰를 **"9번째 lane"**, 카운트 전이를 **"8→9 hard-commit"** 으로 기술했다. 그러나 이는 기존 lane enumeration 의 off-by-one 에서 비롯된 오기다.

- 기존 lane 시퀀스(요구사항 · 설계 · 설계리뷰 · 구현 · 구현리뷰 · 통합테스트 · 보안테스트 · 배포 · 배포리뷰)를 실제로 세면 **9개**다.
- 기계 SSOT 인 `templates/labels/base-labels.tsv` 의 lane phase 라벨(`phase:reservation` 은 non-lane 제외)은 요구사항리뷰 추가 *전* **9개** · 추가 *후* **10개**다.
- 따라서 정본 카운트 = **10** — 요구사항리뷰 = **10번째로 추가된 lane**, 카운트 전이 = **9→10**.

### 결정

본 Amendment 이후 정본 lane 카운트 = **10**. 요구사항리뷰 = 10번째 lane, 카운트 전이 표기 = `9→10`.

- **§결정 1 의 lane 신설 결정 자체는 무변경**: 요구사항리뷰의 위치(`요구사항 → 요구사항리뷰 → 설계`), additive 신설, 기존 lane 무손상, branch protection required contexts 무변경은 그대로다. 본 Amendment 는 카운트 표기 수치(`9번째 lane` → `10번째 lane`, `8→9` → `9→10`)만 정정한다 (약화 0).
- **본문 원 서술 보존**: 본 ADR 본문의 기존 "9번째 lane" / "8→9" 서술은 원 결정 기록 보존 차원에서 그대로 두고, 본 Amendment 가 정정·supersede 한다. 제목·§결정 1 본문은 수정하지 않는다.

### 전파

- **CLAUDE.md** 핵심 흐름 = "10 레인" 시퀀스로 정합 (CFP-2341).
- **docs/architecture/codeforge-family.md** = "10 lane" (in-scope 문장 + mermaid 노드 "10번째 lane" + Story lane spawn flow 카운트) 정합 (CFP-2341).
- **`docs/inter-plugin-contracts/label-registry-v2.md`** 의 라벨 description 내 "9번째 lane" 문자열은 **다음 registry version bump 시 일괄 정정 대상** (deferred — 기능 영향 0, contract version 무손상). 본 Amendment 는 정정 의무만 명시하고 즉시 변경은 하지 않는다.

### 해소 기준

N/A — 표기 정정은 영속이다. 본 Amendment 이후 정본 카운트 = 10 으로 고정.

## Amendment 2 (2026-06-19) — CFP-2350 — runtime-failure 변종 신설 (internal-invariant ground-truth falsification 축)

### 성격

본 Amendment 는 **additive 축 신설** 이다 (약화 아님). 요구사항리뷰 lane 의 현 mandate (외부사실 의존 검증, §결정 6 / [ADR-124](ADR-124-external-knowledge-provisioning-model.md) 단계③) 와 **disjoint 한 internal-invariant ground-truth 축** 을 추가한다. §결정 1~6 + Amendment 1 의미 불변. ADR 본체 status = **Proposed 유지**.

본 Amendment 는 [ADR-064](ADR-064-decision-principle-mandate.md) Amendment 13 (§결정 13 root-cause 사다리 3rd rung — 문제정의 오류 → 요구사항 lane 재진입) 의 **sibling carrier** 다 — ADR-064 가 root-cause 사다리 측 wire, 본 Amendment 가 요구사항리뷰 lane 측 falsification 게이트 측 wire (disjoint axis 두 짝).

### 컨텍스트

요구사항리뷰 lane 은 §결정 6 에서 **외부사실 의존 검증** (산업 표준·RFC·법규·벤더 동작·CVE 등) 을 mandate 로 박제했다 (ADR-124 단계③ 의 주 발동 lane). 그러나 [ADR-119](ADR-119-research-before-claims.md) §결정 10 ② (실패 진단 판정면) 가 박제한 **runtime 실패 진단의 falsification** 영역은 외부지식이 아니라 **내부 코드·invariant 의 ground-truth** 에 의존한다 [cited_adr: ADR-119 §결정 10 ②, cited_value: "runtime 실패의 진단 ('원인 = X') 은 acted-on (수정 착수) 전에 falsification 을 통과해야 한다", verify_status: verified — worktree Read ADR-119 §결정 10 ② (실패 진단 판정면)]. 이 internal-invariant 축은 §결정 6 의 외부사실 축과 검증 대상이 다르다 (외부지식 진위 vs 내부 코드·invariant 보존 여부).

ADR-124 외부지식 충당 3-단계 모델 (단계① 능동 정립 / 단계② 얕은 자가 조사 / 단계③ 깊은 다출처 검증) 은 **외부지식** 의 충당 모델이다. 본 Amendment 의 internal-invariant 축은 그 모델의 **internal-invariant 아날로그** — 같은 "충당 / 검증" 구조를 내부 코드·invariant 의 ground-truth 에 적용한 것이다 (외부지식 모델 대체·약화 0건, 별개 axis 공존).

본 Amendment 가 메우는 공백:

1. **runtime-failure 재진입 시 검증 주체 부재** — ADR-064 §결정 13 이 runtime 실패 Story 를 요구사항 lane 재진입으로 전환하나, 요구사항리뷰 lane 이 그 재진입을 internal-invariant falsification 게이트로 instantiate 하는 변종이 없었다.
2. **internal-invariant 축의 lane 게이트 부재** — 외부사실 게이트 (§결정 6) 는 있으나, 내부 코드·invariant ground-truth 의 falsification 게이트가 요구사항리뷰 lane 에 명시되지 않았다.

### 결정

요구사항리뷰 lane 에 **runtime-failure 변종** 을 신설한다 — 외부사실 mandate 와 disjoint 한 internal-invariant ground-truth falsification 축.

#### 1. 변종 instantiate (기존 자산 재사용, 신규 worker 0)

runtime-failure Story 재진입 (ADR-064 §결정 13 트리거 충족 — 표면 증상-anchored 진단 또는 escalation 종점 후 반복 FAIL) 시, 요구사항리뷰 lane 이 falsification 게이트로 instantiate 된다:

- **기존 dual-peer 재사용**: Claude + Codex (ClaudeReviewAgent ∥ CodexReviewAgent) dual-peer 그대로. [ADR-001](ADR-001-review-agent-unification.md) lane-agnostic — **신규 worker 신설 0건** (§결정 5 재사용 원칙 답습).
- **debate-protocol 재사용**: [ADR-059](ADR-059-debate-protocol-v1.md) debate-protocol-v1 lane-agnostic 그대로 (trigger.lane = `requirements-review`). protocol 무변경.
- **packet = hypothesis-withheld 4-tuple**: 리뷰 packet = `{코드, 증상, outcome-contract, invariant-surface}` — **가설을 숨긴다** (hypothesis-withheld). 기존 진단 (Orchestrator / lane 의 원인 단정) 은 packet 에서 제외되어, 리뷰 lane 이 가설을 정답이 아닌 반증 대상으로 다룬다 (확증 편향 차단, ADR-064 §결정 13 재진입 규율 1 prohibited prior 와 동일). invariant-surface 입력 = [ADR-068](ADR-068-boundary-completeness-invariants.md) I-8 standing invariant-surface [cited_adr: ADR-068 I-8, cited_value: "S4 가 정의하는 falsifier 입력 ({코드, 증상, outcome-contract, invariant-surface} 4-tuple) 중 invariant-surface 입력 = 본 I-8 surface", verify_status: verified — worktree Read ADR-068 I-8 declaration (Amendment 6)].

#### 2. 비대칭 verdict 규칙 (게이트 verdict 레벨)

요구사항리뷰 verdict 는 **비대칭** 이다 — 증상을 설명하는 **file:line 으로 짚힌 위반 invariant 1개 > "OK" N개**. 단일 falsification 이 N attestation 을 이긴다 (Popper 비대칭). ADR-064 §결정 13 재진입 규율 3 (비대칭 결정규칙) 과 동일하되, 본 Amendment 는 그것을 **게이트 verdict 레벨** 로 적용한다 (ADR-064 = 사다리 진단 레벨 / 본 Amendment = lane 게이트 verdict 레벨, 같은 규칙의 두 적용면) [cited_adr: ADR-119 §결정 10 ②, cited_value: "비대칭 규칙 — file:line 으로 짚힌 위반 invariant 1개 > '확인함 OK' N개", verify_status: verified — worktree Read ADR-119 §결정 10 ② (실패 진단 판정면)].

#### 3. 외부사실 축과 disjoint (ADR-124 §결정 6 무약화)

internal-invariant 축은 §결정 6 외부사실 축과 **disjoint** 하게 공존한다:

- **외부사실 축** (§결정 6 / ADR-124 §결정 6 의존 O row) = 산업 표준·RFC·CVE·벤더 동작 등 외부지식 진위 검증 [cited_adr: ADR-124 §결정 6, cited_value: "의존 O | 팩트체크 / 벤더 동작 / 표준(RFC 등) / CVE·취약점 사실 | 있음 — 단계③ 적용", verify_status: verified — worktree Read ADR-124 §결정 6 (외부사실 의존 휴리스틱)].
- **internal-invariant 축** (본 Amendment) = 내부 코드·invariant 의 bound/lifetime/ordering ground-truth 의 falsification.
- 본 변종은 외부사실 mandate 를 **대체·약화하지 않는다** — 두 축 공존 (ADR-124 §결정 6 의미 변경 0건). runtime-failure Story 는 internal-invariant 축으로, 외부사실 의존 결론은 외부사실 축으로 — 같은 lane 의 disjoint 두 검증 mode.

#### 4. enforcement = Phase 1 declarative-only (review-verdict-v4 / checklist 배선 = Phase 2 defer)

본 Amendment = declarative 선언만이다. mechanical wire 는 별 carrier Phase 2 defer:

- **review-verdict-v4 enum**: `review-verdict-v4.md` 의 runtime-failure / invariant-violation verdict enum + 비대칭 self-check field 추가 = **Phase 2 별 carrier defer**. `review-verdict-v4.md` **무수정** (본 Story 미접촉 — 병렬 force-push 충돌 회피, review-verdict-v4 는 sibling Story 들이 공유하는 single-owner contract file).
- **checklist 배선**: `RequirementsReviewPLAgent.md` / `requirements.md` checklist 의 runtime-failure 변종 절차 배선 + ClaudeReviewAgent / CodexReviewAgent 의 runtime-failure branch = **Phase 2 defer**.

declaration-only Wave 1 retain 패턴 답습 (ADR-082 §결정 6 / ADR-070 §D5 / ADR-076 §결정 1 정합).

### cross-ref (Amendment 2)

| ADR | 인용 지점 | 관계 |
|---|---|---|
| ADR-064 §결정 13 (Amendment 13) | 결정 1·2 | **sibling carrier** — root-cause 사다리 3rd rung (문제정의 오류 → 요구사항 lane 재진입). 본 Amendment = 그 재진입의 요구사항리뷰 lane 측 falsification 게이트 (disjoint axis 두 짝). |
| ADR-119 §결정 10 ② (실패 진단 판정면) | 컨텍스트·결정 2 | **instantiation** — runtime 실패 진단 falsification umbrella anchor 를 요구사항리뷰 lane 게이트로 instantiate. ADR-119 본문 무수정. |
| ADR-068 I-8 (standing invariant-surface) | 결정 1 | **재사용** — falsification packet 의 invariant-surface 입력 = I-8 surface. ADR-068 본문 무수정. |
| ADR-124 §결정 6 (외부사실 휴리스틱) | 결정 3 | **disjoint 무약화** — 외부사실 축과 internal-invariant 축 disjoint 공존. ADR-124 의미 변경 0 → 본 Amendment 가 cross-ref 만. |
| ADR-001 (review-agent-unification) | 결정 1 | **lane-agnostic 재사용** — dual-peer 신규 worker 0. |
| ADR-059 (debate-protocol-v1) | 결정 1 | **lane-agnostic 재사용** — trigger.lane = requirements-review. protocol 무변경. |

### 해소 기준

N/A — permanent (additive 축 신설). 본 Amendment 이후 요구사항리뷰 lane = 외부사실 축 + internal-invariant 축 2-mode 공존. mechanical wire (review-verdict-v4 enum / checklist 배선) 추적 = Epic [#2346](https://github.com/mclayer/plugin-codeforge/issues/2346) Phase 2 carrier.

## Amendment 3 (2026-07-17) — CFP-2725 — 결정 A(사용자 확정 위치 정밀화) + 결정 B(내부 시스템 적합성 4번째 disjoint 검증 축)

### 성격

본 Amendment 는 **additive 축 신설 + 위치 정밀화** 다 (약화 아님). 신규 [ADR-159](ADR-159-requirements-lane-enrichment-and-design-entry-signoff.md) (요구사항 lane enrichment 일급 + design-entry 확정 gate SSOT) 의 **lane 시퀀스·확정 위치·내부적합 검증축 짝**. §결정 1~6 + Amendment 1/2 의미 불변. ADR 본체 status = **Proposed 유지**. direction: strengthen; sunset_justification = frontmatter amendment_log 근거 문자열(non-null — additive 축 신설 + 위치 정밀화라 sunset 대상 아님을 명시, Amendment 1/2 동일 non-null 패턴).

본 Amendment 는 **Amendment 2 (CFP-2350 — internal-invariant ground-truth falsification 축) 의 additive-disjoint-axis 패턴을 답습**한다 (그 패턴의 결정적 선례). 신규 [ADR-071](ADR-071-orchestrator-user-dialog-convergence.md) Amendment 15 (발화 frequency 축) + [ADR-077](ADR-077-clarification-forced-reinvestigation-propagation.md) Amendment 1 (terminal event·counter·리뷰-후 rewind) 의 **sibling** 이다.

### 컨텍스트

ADR-159 이 요구사항 lane 에 사용자 최종 확정(design-entry gate)을 도입하면서 두 공백이 드러났다:

1. **확정 checkpoint 위치의 순서 역설**: 사용자 최종 확정을 요구사항 lane 끝(리뷰 전)에 두면 "확정 후 리뷰가 내용 변경 → 확정 무효화" 순서 역설이 발생한다 (BABOK approve 가 미검증 요건 위에서 작동하는 입력-의존성 위배). §결정 1 의 lane 시퀀스에 확정 checkpoint 의 정밀 위치가 미명시.
2. **내부적합 검증 주체 부재 (확증편향 갭)**: 요구사항리뷰 lane 은 §결정 6 에서 외부사실 의존성만 검증한다. "이 시스템에 적합한가"(현 아키텍처 구현가능성·과거 ADR/Story 충돌·중복) = 작성측 Feasibility(§4.2)/Continuity(§4.3) 자가분석만 = generator≠verifier 미분리 확증편향 갭. Amendment 2 가 이미 disjoint 내부 축(internal-invariant, runtime-failure 한정)을 신설했으므로, 일반 내부적합은 그 패턴의 3번째 disjoint 축으로 자연 확장 가능.

### 결정

#### 결정 A — §결정 1 위치 정밀화: 사용자 최종 확정 = 요구사항리뷰 PASS 후·설계 진입 전

§결정 1 의 lane 시퀀스에 사용자 최종 확정 checkpoint 의 정밀 위치를 명문화한다:

- **위치**: `요구사항(why대화+enrichment+§1-7) → 요구사항리뷰(외부사실+내부적합) → **사용자 최종 확정** → 설계`. 확정 = 요구사항리뷰 PASS 후·설계 진입 직전 (요구사항 lane exit 아님 — design-entry gate).
- **lane count 10 무변경 · required contexts 무변경 invariant 상속**: 확정 checkpoint = sub-gate 순서 정밀화이지 lane 추가 아님. Amendment 1(lane 카운트 정본 10) + §결정 2(branch protection required contexts 무변경) invariant 그대로 상속. 배선 = phase:요구사항-리뷰 → phase:설계 전이 경계 (기존 gate 뒤 anchoring).
- **BABOK 입력-의존성 정합**: 요구사항리뷰(verify+validate) 산출을 사용자 최종 확정(approve)이 입력으로 받는다 (`source: iiba.org BABOK 7.2/7.3/5.5` — approve 는 verified+validated 요건 위에서만 작동). 순서 역설 원천 해소(확정 후 리뷰 변경 → 확정 무효 제거).
- **배선 tier**: Phase 1 = playbook 설계 진입 preflight advisory(predicate `user-final-sign-off-resolved`, ADR-159 결정 3). 신규 phase 라벨/gate AND/required context = Phase 1 채택 금지(advisory ceiling — ADR-159 결정 6). 단일 sign-off(요구사항 → 요구사항리뷰 전이는 별도 확정 gate 무요구, 설계 진입 직전 확정이 유일).

#### 결정 B — §결정 6 scope 확장: 외부사실 only → 외부사실 + 내부 시스템 적합성 (4번째 disjoint 축)

요구사항리뷰 lane 의 검증 scope 에 **내부 시스템 적합성 독립 검증 축** 을 추가한다 (Amendment 2 internal-invariant 축의 scope 일반화).

##### 1. 내부적합 축 instantiate (기존 자산 재사용, 신규 worker 0)

- **기존 dual-peer 재사용**: Claude + Codex (ClaudeReviewAgent ∥ CodexReviewAgent) dual-peer 가 설계문서(ADR·Change Plan)·과거 Story·ADR 을 Read 대조로 검증한다 — 아키텍처 구현가능성·과거 결정 충돌·중복. [ADR-001](ADR-001-review-agent-unification.md) lane-agnostic — **신규 worker 신설 0건**(§결정 5 / Amendment 2 재사용 원칙 답습).
- **debate-protocol 재사용**: [ADR-059](ADR-059-debate-protocol-v1.md) lane-agnostic (trigger.lane = `requirements-review`). protocol 무변경.
- **hypothesis-withheld packet**: 작성측 진단(Feasibility/Continuity 자가분석 결론)을 packet 에서 숨긴다 — 리뷰 lane 이 작성측 결론을 반증 대상으로 다룬다 (확증편향 차단, Amendment 2 packet 규율 상속).

##### 2. 검사연극 비충돌 (born-broken 방지 — 명세 필수)

내부적합 축은 "검사연극 금지"(§결정 6 / ADR-119 §결정 6)와 **비충돌**해야 한다:

- **repo-내부 문서 Read 기반 (WebSearch 강제 아님)**: 내부적합 = 설계문서·과거 Story·ADR 의 실제 Read 대조. 외부사실 축의 도구(WebSearch)와 **tool-disjoint**. ADR-124/125 검사연극 금지 원문(`ADR-125:142`) = "내부-only 결론에 외부 웹조사 강제" 만 금지 — 내부문서 Read 로 내부정합 검증은 그 금지 대상 아님.
- **declarative-only null-valid**: 대조할 설계문서·과거결정 없는 신규 영역 = 자연 N/A(null-valid). 적합 이슈 0건 = 정상 PASS — 억지 결함 조작 금지(강제 발굴 금지).
- **disjoint 2차 (generator ≠ verifier)**: 작성측 Feasibility(§4.2)/Continuity(§4.3) 자가분석과 disjoint 한 2차 독립 검증 (§결정 4 disjoint axis 동형). 작성측 = 단계②(자가분석), 리뷰측 dual-peer = 단계③(독립 재검증).

##### 3. 외부사실 축과 disjoint (ADR-124 §결정 6 무약화)

내부적합 축은 §결정 6 외부사실 축과 **disjoint** 하게 공존한다 — 외부사실 검증(표준/CVE/벤더)과 내부적합 검증(아키텍처 구현가능성·과거 결정 정합)은 별개 axis, 외부사실 mandate 대체·약화 0. ADR-124 §결정 6 의미 변경 0 → 본 Amendment 가 ADR-124 를 **cross-ref 만** 한다 (Amendment 불요 — Amd2 도 ADR-124 cross-ref 만 처리, 내부적합 = 외부지식 3-단계 모델 internal 아날로그).

##### 4. enforcement = Phase 1 declarative (배선 = Phase 2 defer)

본 결정 = declarative 선언만이다. mechanical wire 는 별 carrier Phase 2 defer:

- **review-verdict category literal**: `review-verdict-v4.md` 의 `internal-fitness-*` verdict enum(필요 시) + severity_overrides = **Phase 2 defer**. `review-verdict-v4.md` **무수정**(본 Story 미접촉 — 병렬 force-push 충돌 회피). literal 신설 형식 = 설계 결정(Amd2 선례 확인 후).
- **checklist·agent 배선**: `RequirementsReviewPLAgent.md`(내부적합 축 owner 절 + category_enum) / `requirements.md` checklist(내부 시스템 적합성 게이트 절) 배선 = **Phase 2 defer**. axis 분리 명시 필수(작성측 §4.1/§4.2 단계② ↔ 리뷰측 internal-fitness 단계③ 독립 재검증 — §결정 4 disjoint 동형).
- **phase 라벨 wiring**: 결정 A 의 확정 checkpoint phase 라벨/gate 배선 = Phase 2 defer (Phase 1 = playbook preflight advisory).

declaration-only Wave 1 retain 패턴 답습 (Amendment 2 §4 / ADR-082 §결정 6 / ADR-070 §D5 정합).

### cross-ref (Amendment 3)

| ADR | 인용 지점 | 관계 |
|---|---|---|
| ADR-159 | 결정 A·B | **SSOT 짝** — 요구사항 lane enrichment 일급 + design-entry 확정 gate 본체. 본 Amendment = lane 시퀀스·확정 위치·내부적합 검증축 wiring. |
| ADR-125 Amendment 2 (internal-invariant 축) | 결정 B | **결정적 선례** — additive-disjoint-axis 패턴(runtime-failure 한정 internal-invariant). 결정 B = 그 패턴의 scope 일반화(3번째 disjoint 축, 일반 내부적합). |
| ADR-071 Amendment 15 (§결정 23) | 결정 A | **sibling** — 발화 frequency 축(design-entry gate 발화 touchpoint). disjoint axis. |
| ADR-077 Amendment 1 | 결정 A | **sibling** — 리뷰-후 확정 rewind 의 리뷰 lane 대상(내용 수정 동반 확정 시 요구사항리뷰 rewind). |
| ADR-124 §결정 6 (외부사실 휴리스틱) | 결정 B | **disjoint 무약화** — 외부사실 축과 내부적합 축 disjoint 공존. ADR-124 의미 변경 0 → cross-ref 만 (Amendment 불요). |
| ADR-119 §결정 6 (검사연극 금지) | 결정 B | **정합** — 내부적합 축 = repo Read 기반·declarative-only null-valid, 검사연극 비충돌. |

### 해소 기준

N/A — permanent (additive 축 신설 + 위치 정밀화). 본 Amendment 이후 요구사항리뷰 lane = 외부사실 축 + internal-invariant 축(Amd2) + 일반 내부적합 축(본 Amendment) 공존, 사용자 최종 확정 = 요구사항리뷰 PASS 후·설계 진입 전. mechanical wire (review-verdict-v4 `internal-fitness-*` / checklist 배선 / phase 라벨) 추적 = CFP-2725 Phase 2 carrier.

## Amendment 4 (2026-07-22) — CFP-2782 — canonical 작업레인 수 10 → 8

### 성격

본 Amendment 는 **canonical lane count 정본 갱신** 이다 — Amendment 1 이 정본화한 canonical=10 에서, CFP-2782 / [ADR-121](ADR-121-deprecate-deploy-lanes.md) 의 deploy·deploy-review 2 lane 물리 제거를 반영해 **canonical=8** 로 갱신한다. ADR-121(별개 주제 ADR)은 본 ADR-125 의 numeric SSOT 를 단독 재정의할 권위가 없으므로, `check_lane_count_ssot.py` docstring 이 지정한 **REQUIRED mechanical-sync carrier** = 본 Amendment 4 가 그 carrier 역할을 수행한다. ADR 본체 status = Proposed 유지. §결정 1~6 + Amendment 1/2/3 의미 불변.

### 최종 8 lane

요구사항 → 요구사항리뷰 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 통합테스트 → 보안테스트. (deploy·deploy-review 2 lane 제거 — ADR-121.)

### REQUIRED mechanical-sync carrier (docstring 의무)

`scripts/lib/check_lane_count_ssot.py` 의 canonical=10 + N-range 검출 regex 를 다음으로 flip (실 편집 = Phase 2 구현 scope):

- **canonical 10 → 8**.
- **N-range regex flip**: stale flag set 에서 "8" 제외(canonical화) + "10" 편입(두 자리 = alternation `(?:10|[679])` + capture-group 구조 변경 + lookbehind/trailing digit-boundary 재배치 — 상수 bump 아님).
- **self-test fixture 반전**(§8.1/§8.2): F-DET-2 "8 레인" FLAG→no-FLAG / F-EXIT-0 "10 레인" no-FLAG→FLAG / F-TRANS-2 "10번째 lane"→"8번째" / Mutation-5 anchor regex 갱신 강제.

### frozen 이력

Amendment 1 의 canonical=10(요구사항리뷰 추가 시점 정본) = **frozen 역사 기록** (byte 0건 변경, Event Sourcing — 그 시점 카운트 결정 보존).

### cross-ref (Amendment 4)

| ADR | 관계 |
|---|---|
| ADR-121 | canonical count 10→8 authority (deploy·deploy-review lane deprecate) |
| ADR-125 Amendment 1 | canonical=10 정본화 — frozen 역사 (본 Amendment 가 10→8 갱신) |
| ADR-072 Amendment 5 | ProductionEvidenceDeputy RELOCATE (sibling — 동일 CFP-2782) |

## sunset_justification (ADR-058 §결정 5 — 약화 evidence-gate)

본 ADR 은 약화 0건이다. **additive lane 신설** — 기존 8 lane·게이트·라벨·worker 무손상이며, branch protection required contexts 무변경, ADR-052 touchpoint #4 무약화 (disjoint 공존), ADR-001 worker 신설 0 (재사용). ADR-124 deferral 경계 (S3/S4/S5) 무침범. is_transitional: false (permanent governance anchor). 원복은 별도 Story 의 명시 결정으로만 가능하며 그 경우에도 ADR-058 §결정 5 (약화 시 sunset_justification 의무) 를 따른다.

## 해소 기준

N/A — permanent policy. 후속 이행 추적 = Epic [#2324](https://github.com/mclayer/plugin-codeforge/issues/2324) (S3~S5).

## 관련 파일

- 본 ADR — 요구사항리뷰 lane 게이트·라벨·배선 SSOT (ADR-124 S2 이행)
- [ADR-124](ADR-124-external-knowledge-provisioning-model.md) — 외부지식 충당 3-단계 (S1 anchor, deferral 경계)
- [ADR-052](ADR-052-codex-proactive-check-touchpoints.md) — Codex proactive touchpoint #4 (작성측 disjoint cross-ref, Amendment 불요)
- [ADR-059](ADR-059-debate-protocol-v1.md) — debate-protocol-v1 (lane-agnostic, trigger.lane 분리)
- [ADR-001](ADR-001-review-agent-unification.md) — lane-agnostic review subsystem (worker 재사용)
- `plugins/codeforge-review/agents/RequirementsReviewPLAgent.md` — 신규 lane PL
- `plugins/codeforge-review/templates/review-checklists/requirements.md` — 외부사실 의존 체크리스트
- `.github/workflows/phase-gate-mergeable.yml` — fast-pass guard + required branch + lanePrefixForGate
- `templates/labels/base-labels.tsv` + `docs/inter-plugin-contracts/label-registry-v2.md` — 3 신규 라벨
- `CLAUDE.md` — 핵심 흐름 9 레인 시퀀스
- `docs/architecture/codeforge-family.md` — Living Architecture (lane count 8→9 step)
