---
adr_number: 30
title: Live Epic lane-entry policy + real-funds gate
date: 2026-05-05
status: Accepted
category: governance
carrier_story: CFP-123
supersedes: null
is_transitional: false
---

# ADR-030: Live Epic lane-entry policy + real-funds gate

## 상태

Accepted (2026-05-05). carrier_story = CFP-123. Resolves issue #156 (mctrader debut audit P0 — Lane Progression gap).

## 컨텍스트

mctrader Live mode Epic Phase 1 audit (Codex gpt-5.5 high, 2026-05-04) 가 P0 gap 도출:

> 현재 phase-gate-mergeable Action 의 gate label = `gate:design-review-pass` / `gate:security-test-pass` 만 존재. ADR-008 D4 의 "real KRW exposure 허용" 조건 (3-condition AND: `mode==live + --confirm-live + isolated runtime`) 을 codeforge lane-level gate 로 표현하는 mechanism 부재.

**Live touching Story** (CLAUDE.md 정의: real funds / live exchange API / production credential / live order placement 중 하나 이상 touching) 는 §13 Live Operational Discipline schema 의무 + LiveOpsDeputy + LiveOrderingDeputy CONDITIONAL active. 현재까지 codeforge 는 이 의무를 Story-level (§13 schema 작성) 로만 강제, **PR-level mergeable gate 로 enforce 안 됨**.

mctrader Live mode Epic 이 first consumer test case — Phase 2 PR merge 직전 운영 prerequisite (mode flag · confirmation · runtime isolation) 검증 mechanism 이 필요. Phase 1 (require-only) 구간에 본 gate 도입.

## 결정 요약

5 결정 freeze. carrier Story = CFP-123. label-registry-v1 v1.2 → v1.3 minor bump.

### 결정 1 — 신규 label `gate:live-entry-pass` 정의

label-registry-v1.md 의 `gate:*` 카테고리 에 신규 항목 추가:

```yaml
- name: gate:live-entry-pass
  category: gate
  color: "0e8a16"
  description: "Live Epic lane-entry pass — 3-condition AND (mode==live + --confirm-live + isolated runtime) 충족"
  single_active: false
  attach_owner_plugin: "wrapper Orchestrator (post-Sonnet review-verdict step 4)"
```

`scripts/bootstrap-labels.sh` 도 동일 항목 추가 (idempotent `gh label create`). label-registry-v1 v1.3 minor bump (additive, ADR-008 SemVer 정합).

### 결정 2 — Live touching Story 식별 mechanism

Story file frontmatter 또는 PR body 에서 Live touching 여부 식별:

- **Story file frontmatter**: `live_touching: true` (Live touching Story 작성 시 명시 의무)
- **PR body marker**: `live_touching: true` (Phase 2 PR body 에 명시)
- **CONDITIONAL deputy presence**: §13 schema 가 작성됨 + LiveOpsDeputy / LiveOrderingDeputy 산출물 존재 → 자동 detect (Phase 2 보강)

Phase 1 = frontmatter / PR body marker explicit declare 의무. Phase 2 = §13 schema presence 자동 detect (별도 CFP).

### 결정 3 — phase-gate-mergeable.yml 가 본 gate 추가 검증

`templates/github-workflows/phase-gate-mergeable.yml` 의 `// 5. Determine required gate by file change scope` 블록 확장:

- Story / PR 가 `live_touching: true` 일 때 + phase 가 `phase:보안-테스트` (Phase 2 PR merge gate) 일 때
  - 기존 `gate:security-test-pass` 외에 `gate:live-entry-pass` 추가 의무
  - 두 gate 모두 부재 = `action_required` (PR merge block)
- Live touching = false (default) Story = 기존 gate 만 검증 (변경 없음)
- PR 가 동시에 여러 `gate:*` label 을 carry 하므로 membership check (label list 안에 required gate 가 있는가) 적용 — strict-equality 단일 gate label 비교 시 false-fail.

**Phase 2 PR 의 phase 라벨 = `phase:보안-테스트`** (보안 테스트 lane PASS 직후 부착, Phase 2 PR merge gate). `phase:구현-리뷰` 적용 안 함 — 구현 리뷰 PASS 시점은 보안 테스트 진입 전.

### 결정 4 — 3-condition AND 정의 SSOT 분리

본 ADR 는 **gate label + workflow validation mechanism** 만 정의. 실제 3-condition AND 검증 로직 (`mode==live` flag 확인 / `--confirm-live` 사용자 confirmation / isolated runtime 검증) 은 consumer-side CI workflow 또는 hook 책임 — 본 wrapper 는 **gate label 의 부착 / 부재 만 검증**.

Consumer 측 Live mode Epic 작업 시:
- 3-condition 검증 통과 시 → consumer CI 가 `gate:live-entry-pass` 부착
- consumer-side 검증 protocol = ADR-008 D4 SSOT (mctrader) — wrapper 무관

Codeforge wrapper = **gate gate** (gate 가 부착됐는지만 검증). 검증 로직 = consumer.

### 결정 5 — phase-gate-mergeable.yml 가 fast-pass / Story 미바인딩 PR 영향 차단

본 gate 가 추가되어도 기존 fast-pass 동작 (type:epic / doc-only PR) 은 변경 없음:

- type:epic label PR → fast-pass (변경 없음)
- doc-only PR → fast-pass (변경 없음)
- Story 미바인딩 PR (no story_uri / no Issue link) → 기존 file-based heuristic (Live touching detect 불가능 → gate:live-entry-pass 검증 skip)
- Story 바인딩 + live_touching=true + Phase 2 PR → gate:live-entry-pass 추가 검증

## 대안 검토

### 대안 A — Live mode Epic 전체 자동 차단 (lane-entry refusal)

Live touching Story 가 phase:보안-테스트 진입 시 자동 block, 사용자 explicit 승인 없이 진행 불가.

- **장점**: 강력한 enforcement
- **단점**: Story-level Block mechanism 이 phase-gate-mergeable scope 초과. 별도 hook + CI 통합 필요. Phase 1 trust model (ADR-022 §결정 11) 정합 위배 위험.
- **거부 이유**: Phase 1 = require-only, Phase 2 = enforce. 본 ADR 는 Phase 1 적용.

### 대안 B — Story §13 schema presence 자동 detect

§13 Live Operational Discipline schema 가 Story file 에 written 되어있으면 자동 Live touching 판정.

- **장점**: explicit declare 부담 없음
- **단점**: phase-gate-mergeable Action 이 cross-repo Story file fetch + §13 section parse 필요 — 복잡도 증가. Story 작성 timing 과 PR creation timing 의 race condition.
- **거부 이유**: Phase 1 = explicit marker, Phase 2 = §13 detect (별도 CFP).

### 대안 C — Real-funds gate 만 정의, Live entry gate 분리

`gate:real-funds-pass` (실제 자금 사용) 만 신설, Live API connect 만 하는 case (paper trading on live API) 는 미보호.

- **장점**: scope minimal
- **단점**: Live API connect 자체가 boundary risk (rate limit / IP ban / credential leak). real-funds 보다 넓은 boundary 필요.
- **거부 이유**: Live touching = umbrella term (4 sub-trigger 중 하나만으로도 active). 1 gate 로 통합 처리.

**채택 = 본 ADR §결정 1-5** (단일 `gate:live-entry-pass` + Phase 1 explicit marker).

## 결과

### 영향 file (wrapper repo)

- `docs/adr/ADR-030-live-entry-gate-policy.md` (본 file)
- `docs/inter-plugin-contracts/label-registry-v1.md` — gate:live-entry-pass 항목 추가 (v1.2 → v1.3)
- `scripts/bootstrap-labels.sh` — gate:live-entry-pass 생성 line 추가
- `templates/github-workflows/phase-gate-mergeable.yml` — Live touching detection + gate validation 확장
- `CLAUDE.md` — Lane gate label list (3 gate)

### 비-영향

- 6 lane plugin (codeforge-{requirements,design,develop,test,review,pmo}) 변경 없음 (gate 부착 = Orchestrator 단독, ADR-022 §결정 4 정합)
- ADR-008 D4 (mctrader 3-condition AND) 변경 없음 — consumer-side SSOT 그대로
- Non-Live touching Story 동작 무변화

### Reversibility

- Yes — `gate:live-entry-pass` label 삭제 + workflow validation 블록 제거 = 기존 동작 복원
- ADR revert 시 label-registry v1.3 → v1.2 (BREAKING — `gh label delete` 필요, 후속 cleanup PR 의무)

## Out-of-scope

- Consumer-side 3-condition AND 검증 로직 (ADR-008 D4 SSOT — consumer 책임)
- Story §13 schema presence 자동 detect (Phase 2, 별도 CFP)
- `gate:live-entry-pass` 의 Phase 2 enforcement (require-only Phase 1 → enforce Phase 2 단계 분리, 별도 CFP)
- Live touching Story 외 일반 Story 영향 (변경 없음)

## 해소 기준

N/A — permanent policy

## 관련 파일

- `docs/inter-plugin-contracts/label-registry-v1.md` — gate:live-entry-pass 항목
- `scripts/bootstrap-labels.sh` — bootstrap idempotent create
- `templates/github-workflows/phase-gate-mergeable.yml` — Live touching detection + gate validation
- `CLAUDE.md` — gate label list
- `docs/orchestrator-playbook.md` §3·§6 — Live touching Story flow (별도 follow-up 으로 §13 detect 통합)

## 관련 ADR

- ADR-008 D4 (mctrader Live mode 3-condition AND) — consumer-side SSOT, 본 ADR gate validation 의 prerequisite
- ADR-016 (marketplace registration) — gate label 변경 시 sibling sync 의무
- ADR-022 §결정 4 (review-verdict ownership) — gate 부착 = Orchestrator 단독 정합
- ADR-024 (Story-scoped branch policy) — 본 ADR carrier Story = CFP-123
