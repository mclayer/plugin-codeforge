---
adr_number: 165
title: Fleet-wide CI concurrency/trigger governance — 4-class taxonomy + KEEP/NARROW rubric
date: 2026-07-24
status: Accepted
category: tooling-infrastructure
carrier_story: CFP-2810
supersedes: null
amends: null  # new-sibling — 기존 concurrency 선례(ADR-026/036/063)를 폐기하지 않고 fleet-wide rubric 로 일반화. 기존 계약 supersede 0.
related_adrs:
  - ADR-026  # prior art — post-merge-followup cancel:false ("partial state — Issue close 절반" 방지, flip-forbidden 상속) + §5.F group repository-prefix intent
  - ADR-036  # prior art — story-init per-Issue unit-scoped concurrency (Class B 선례, Option B)
  - ADR-063  # prior art — marketplace-drift cron group + false, repository-level scope (Class C 선례)
  - ADR-065  # byte-parity ownership — templates↔.github self-app byte-identical owner (AC-9/AC-SEC 근거; ADR-005 아님)
  - ADR-130  # inherit-invariant — required check 가 path/branch-filter 로 skip → GitHub permanent-pending → merge 데드락. hub path-filter non-required 확인 규율 근거
  - ADR-136  # inherit-invariant (DISTINCT failure mode) — job-level if:hashFiles() born-invalid schema-load 실패 (permanent-pending 과 별개 실패 모드, 별도 cite)
  - ADR-125  # required 8-tuple contexts 무변경 anchor (concurrency = workflow-level 추가 → job/context 이름 무영향)
  - ADR-121  # required contexts 무변경 anchor (Wave 2)
  - ADR-060  # tier 무영향 — concurrency 추가 = tier/gate 무영향, 재승인 불요
  - ADR-133  # ADR 번호 atomic claim 프로토콜 — 본 ADR 번호(165) 예약 mechanism
related_stories:
  - CFP-2810
related_cfps:
  - CFP-2810  # carrier — CI 컴퓨팅 부하 절감 (concurrency 전면 배선 + 트리거 협소화 + internal-docs 허브 조건화)
related_files:
  - templates/github-workflows/  # concurrency 배선 대상 원본 (byte-parity 쌍 templates↔.github)
  - .github/workflows/invariant-check.yml  # byte-parity 강제 loop (Workflow parity diff -q, required 8-tuple)
  - tests/scripts/_cfp2810_crosswalk.py  # crosswalk manifest SSOT (128 rows, 셈 단일 authority)
is_transitional: false
mechanical_enforcement_actions: []  # Phase 2 배선(107 concurrency + 14 narrow + hub 5) + AC-1~AC-13/AC-SEC self-test 는 CFP-2810 §8 이행. 본 ADR = 배선 rubric 결정 SSOT.
---

# ADR-165: Fleet-wide CI concurrency/trigger governance — 4-class taxonomy + KEEP/NARROW rubric

## 상태

**Accepted** (2026-07-24 KST, CFP-2810 Phase 2 carrier). 발의 근거 = 2026-07-23 Orchestrator 14일 전수 census — private CI 71,709분/14일 중 65%(46,513분)가 변별 이벤트(FAIL) 0회 워크플로에서 소모. `Closes CFP-2810 설계 fork(§9)`.

## 컨텍스트

codeforge 자기 거버넌스 CI fleet(128 unique 워크플로 = shared 68 + templates-only 17 + .github-only 43)이 **게이트 판정력과 컴퓨팅 낭비를 같은 파일에 공존**시킨다. 14일 census: 65% 소모가 변별 이벤트 0 워크플로. concurrency 보유 워크플로는 14개(≈15%)뿐, 광폭 트리거(`labeled/unlabeled/edited`) 다수 → PR당 동일 게이트 10~20회 재발화. 러너 포화 시 15~40초 검사가 14~31분 큐 점유로 부풀음.

개별 선례는 존재하나(ADR-026 §5.D post-merge-followup / ADR-036 story-init / ADR-063 §13 E-6 cron) **fleet 전체 배선 rubric 이 부재** → drift·오분류 위험. 특히:
- group key 에 `${{ github.workflow }}` discriminator 누락 시 서로 다른 워크플로가 같은 ref 로 group 붕괴 → required run 상호 취소 → **게이트 영구 stranding**(가용성 = 보안 불변).
- required 워크플로에서 label 트리거 협소화 시 라벨 변경 재평가 불가 → 판정 우회.
- 외부 `checks.create` poster(phase-gate-mergeable)가 취소창에 노출되면 check-run in_progress 방치 → fail-closed 차단 회피.

핵심 제약(user-input 불변): **게이트를 하나도 제거하지 않고 낭비만 제거한다** — 게이트 제거 0 · required context 무변경 · 판정 로직 무변경 · byte-parity 유지.

## 결정

### 1. 4-class taxonomy (분류 축 = 부작용 유무, "PR-트리거 유무" 아님)

기존 concurrency 14개 중 cancel:true = branch-liveness-test **1건뿐**(부작용 없는 pytest). 확립된 실제 축 = **{순수 검증 → cancel:true / 부작용(PR·cron 무관) → cancel:false}**.

| class | 정의 | cancel-in-progress | group-key (locked literal) |
|---|---|---|---|
| **A. 순수 검증** | 부작용 0 lint/test/schema/presence (comment 보고-only = non-disqualifying, state-mutation 0 → 자격 유지) | `true` | `${{ github.workflow }}-${{ github.event.pull_request.number \|\| github.ref }}` |
| **B. per-unit side-effect** | PR/Issue 단위 파일·이슈·라벨 mutate | `false` | `${{ github.workflow }}-${{ github.event.pull_request.number \|\| github.event.issue.number }}` |
| **C. singleton cron** | ref 개념 없는 정기 실행 | `false` | `${{ github.workflow }}` (static) |
| **D. 외부 check-run poster carve-out** | `checks.create` 로 run 결론과 분리된 check-run POST | `false` (option a) | `${{ github.workflow }}-${{ github.event.pull_request.number \|\| github.ref }}` (A-shape group + false) |

- **혼합(M) 워크플로**(PR + push/schedule): `cancel-in-progress: ${{ github.event_name == 'pull_request' }}`(PR run = true / push·schedule run = false), group = A-shape(`|| github.ref`). 단 **PR-arm·push/schedule-arm 양쪽 모두 순수검증**(must-run-once side-effect 부재)이어야 `github.ref` 공유 그룹키 안전 — 위반 시 B/S/D 재분류(`github.ref` 공유 금지).

### 2. group-key 균일 규칙 (availability invariant)

모든 group 은 `${{ github.workflow }}` context expression 을 discriminator 로 포함(손-타이핑 slug 금지) — cross-workflow collapse 방지 + AC-3 bijection trivial + authoring drift 제거.

### 3. KEEP/NARROW trigger rubric

label/body/title/base 를 **판정 입력으로 소비**(코드 분기: `steps.bypass.outputs.bypass` / `pr.labels.map` / `github.event.label` / `pr.body` 파싱)하면 **KEEP**, 메시지 문자열에만 등장하면 **NARROW**(생략 default 금지 → explicit `[opened, synchronize, reopened]`, AC-4 grep 가능). 완전성 검증 = `on:` … `types:` 블록만(주석·job 로직 제외 — auto-phase-label 주석 "labeled" false-positive 차단).

### 4. inherit-invariant (required 항상 실행·보고)

required check 는 항상 실행·보고돼야 함 — path-filter 는 **non-required 에만** 적용(ADR-130 §4 permanent-pending), born-invalid schema-load 회피(ADR-136 §13, distinct failure mode). required 8-tuple 문자열 무변경(ADR-125/121). concurrency 취소·path-filter 가 required 를 미보고로 남기면 안 됨.

### 5. HF-1 option(a) carve-out precedent

외부 `checks.create` poster 가 in_progress→PATCH 창 부재(모든 create 가 단일 atomic `status:'completed'`)면 `cancel:false` 로 취소창 자체를 제거 — 런타임 채택-규칙 의존 회피. (phase-gate-mergeable: `checks.create` 2건 모두 atomic completed, `checks.update`/`in_progress` 0건 firsthand → option(a) documented-safe.)

## 결과

- **낭비 절감**: superseded run 자동 취소(A cancel:true) + 광폭 트리거 협소화(NARROW-14) + hub 조건화 → redundant run·API-call 순감소(신규 quota 위험 0, 감소 방향만).
- **게이트 무손상**: 4-class 균일 expression + AC-SEC surface byte-parity(추가된 concurrency + 편집된 on:types 를 제외한 top-level permissions/env/secrets + jobs 전체 byte-identical) + required 8-tuple 무변경 + byte-parity(templates↔.github) 유지.
- **drift 제거**: `${{ github.workflow }}` 균일 discriminator + crosswalk manifest(128 rows) 셈 단일 authority.
- **trade-off**: reusable `workflow_call`(W, 7) = caller-side 위임 · dispatch-only fixture(F, 1) = scope 제외 → 배선 밖(명시 exclusion anchor). unit-scoped(PR#/Issue#) key 는 Class B/D idempotency 의 load-bearing 요소 — "0 executions ≠ 1 execution"(missed-execution 비-recoverable), cancel:true weakening 또는 shared group 붕괴 = P0(AC-2 봉인).
- **revert 안전**: additive-only(concurrency 블록 + on:types 배열) → revert = 블록 제거 + 배열 원복, 판정 회귀 0.

## 관련 파일

- [ADR-026](ADR-026-post-merge-automation.md) §결정 5.D/§5.F — post-merge-followup cancel:false 선례(flip-forbidden) + group repository-prefix intent
- [ADR-036](ADR-036-project-key-atomic-reservation.md) §결정 5 — story-init per-Issue unit-scoped concurrency(Class B 선례)
- [ADR-063](ADR-063-marketplace-atomic-invariant.md) §결정 13 E-6 — marketplace-drift cron group+false, repository-level scope(Class C 선례)
- [ADR-065](ADR-065-architect-phase1-mechanical-self-check.md) §결정 1 — templates↔.github byte-parity ownership(AC-9/AC-SEC 근거; ADR-005 아님)
- [ADR-130](ADR-130-applicability-closure-integrity.md) §결정 4 — permanent-pending(path/branch-filter skip) inherit-invariant
- [ADR-136](ADR-136-frontend-quality-gate-standard.md) §결정 13 — born-invalid schema-load(DISTINCT failure mode) inherit-invariant
- [ADR-133](ADR-133-adr-reservation-atomic-claim.md) — 본 ADR 번호 atomic claim mechanism
- `templates/github-workflows/**` + `.github/workflows/**` — concurrency 배선 대상 fleet(byte-parity 쌍)
- `tests/scripts/_cfp2810_crosswalk.py` — crosswalk manifest SSOT (128 rows: class/cancel_spec/group_shape)

## 해소 기준

N/A — permanent policy (fleet CI concurrency/trigger 배선 rubric 상시 적용).
