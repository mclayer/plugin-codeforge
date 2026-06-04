---
kind: concept_definition
type: domain-knowledge
slug: additive-merge-pattern
title: Additive-merge pattern — long-running Story mid-flight main churn 정합 (label-registry PATCH bump / evidence-registry tail append / cross-section additive)
status: Active
updated: 2026-05-17
carrier_story: CFP-896
related_adrs:
  - ADR-076  # 선언적 reconciliation upgrade flow SSOT — §4.7 overlay_reconcile_implementation_binding marker-aware 2-way 패턴 anchor
  - ADR-039  # Orchestrator subagent default + §결정 14 `pre-spawn-pin` mandate (CFP-895) — 본 pattern 의 forcing function 짝
  - ADR-064  # decision principle mandate — §결정 4 parallel default (mid-flight churn 가능 원인)
  - ADR-073  # verify-before-assert — 모든 rebase 결정 전 HEAD 고정 invariant
  - ADR-077  # clarification 강제 재조사 전파 — 4-layer disjoint 패턴 N-layer 확장 anchor
related_stories:
  - CFP-785  # Story-3 Epic A — 3× 추월 rebase 첫 누적 (CFP-722/751/777/795/810/745/819 추월)
  - CFP-848  # Story-5 Epic A — 2× rebase (FIX Iter1 stale-base 65901ac5→eafc726 + mid-flight CFP-841 추월 a0a9da1)
  - CFP-896  # 본 concept doc 물리 작성 carrier (Epic A close follow-up CFP)
tags:
  - additive-merge
  - long-running-story
  - mid-flight-rebase
  - label-registry-patch
  - evidence-registry-tail-append
  - cross-section-additive
  - parallel-session-overtake
---

# Additive-merge pattern

## 정의

`additive-merge pattern` = **long-running Story (다수 시간 lifecycle) 가 mid-flight 에서 main branch 의 advancement 를 만났을 때, parallel session 들이 main 에 추가한 entries 를 wholesale 손실 없이 보존하면서 본 Story 의 변경을 추가하는 rebase strategy**.

핵심 invariant 3종:

1. **label-registry monotone PATCH bump** — main 이 v2.N 으로 advanced 시 본 branch 는 v2.N+1 / v2.N+2 / ... 로 monotonic 증가. 절대 v2.M (M < N) 되돌아가지 않음.
2. **evidence-registry tail append** — main 이 entry K 신설 후 advanced 시 본 branch 는 entry K 보존 + 본 Story entry append (tail).
3. **cross-section conflict resolution = additive (not destructive)** — section A 가 main 에서 row 1개 추가되었고 본 branch 가 row 2개 추가했으면, 결과 = row 3개 (both preserved).

## 컨텍스트

### 발의 trigger — 2× 누적 pattern (CFP-896 §1 verbatim)

| Story | 실행 시간 | mid-flight rebase | 추월 PR |
|---|---|---|---|
| CFP-785 (Story-3, Epic A) | 다수 시간 | 3× 추월 rebase | CFP-722 / CFP-751 / CFP-777 / CFP-795 / CFP-810 / CFP-745 / CFP-819 |
| CFP-848 (Story-5, Epic A) | 4+ 시간 | 2× rebase | FIX Iter1 stale-base (`65901ac5`→`eafc726`) + mid-flight (`eafc726`→`a0a9da1`, CFP-841 추월) |

본 pattern 은 2× 누적 (ADR-045 §D-9 ≥ 2 threshold reach) — codify 가치 도달. PMO retro Story-5 §6 NEW pattern 2 carry-over.

### Pattern 의 본질

main branch high-churn 환경 (codeforge family monorepo 다수 parallel session 운영 중) 에서, 본 Story 의 lifecycle 이 다른 Story 들 보다 길 때 발생. Story 분할 path (Path B) 로 회피 가능하지만 — full 6 lane Story 의 자연 길이 (요구사항 + 설계 + 리뷰 + 구현 + 리뷰 + 보안 + merge gate) 가 이미 분할 한계. 따라서 codify 가치 = additive-merge 의 일관 자동화.

## 핵심 규칙

### I-1: label-registry monotone PATCH bump

`docs/inter-plugin-contracts/label-registry-v2.md` frontmatter `version: "2.N"` 의 N 은 **monotonic increment**. mid-flight rebase 시:

- main 의 v2.N+K 가 본 branch 가 작성한 v2.M (M ≤ N) 을 추월한 상태 → 본 branch 는 **N+K+1** 로 PATCH bump (M 으로 되돌리기 금지)
- 본 branch 가 작성한 family member entry (label-registry §3 yaml block) + main 의 새 family member 모두 보존 (양쪽 entry 보존, count = N+K+1 위치 정합)

**위반 패턴 (anti-pattern)** — wholesale rebase 시 `git checkout --theirs` 또는 `--ours` 단순 선택으로 어느 한쪽 entries clobber. 본 invariant 위반 시 main 의 다른 Story entries 손실 → governance drift.

### I-2: evidence-registry tail append

`docs/evidence-checks-registry.yaml` 의 `entries[]` list 는 **append-only tail**:

- main 이 entry K 추가 (Story X carrier) → 본 branch 는 K 보존 + 본 Story entry append (tail position)
- 절대 entry K 삭제 / 본 Story entry 를 K 위치에 insert (위치 충돌) 금지

**위반 패턴** — rebase 시 본 Story entry 를 main entry K 앞에 insert. 결과 = K 의 위치 변경 → 후속 entry numbering 의존 코드 (parse_hotfix_bypass_labels.py 등 yaml 순서 의존 lookup) 에 hidden bug.

### I-3: cross-section additive resolution

여러 section (label-registry §3 yaml block / evidence-registry entries[] / CHANGELOG 각 section / playbook §3.0.N 등) 의 conflict 시:

- **additive merge** (양쪽 row/entry 모두 보존) 이 default
- destructive choice (한쪽 row 삭제) 은 명시적 의미 검토 후에만 허용 — 동일 anchor 에 conflict (예: 같은 §결정 N 번호) 시 ADR-076 §결정 8 stale 게이트 / parallel-epic-conflict-check.yml 의 merge-order label 로 sequencing

## 경계

### vs `declarative reconciliation upgrade` (ADR-076 §4.7)

본 pattern 과 ADR-076 §4.7 overlay_reconcile_implementation_binding (marker-aware 2-way / wholesale_mirror_with_user_visible_loss_report) 는 다른 영역:

| 차원 | additive-merge pattern (본 개념) | declarative reconciliation (ADR-076 §4.7) |
|---|---|---|
| 적용 layer | git rebase (Story progression) | codeforge upgrade transaction (overlay reconcile) |
| 대상 | wrapper repo 의 `docs/inter-plugin-contracts/*.md` + `docs/evidence-checks-registry.yaml` + section-locked files | consumer repo 의 overlay (skill / agent / hook) |
| trigger | mid-flight main churn (parallel Story merge) | codeforge upgrade run |
| disjoint layer | Story progression layer | upgrade transaction layer (ADR-076 §결정 4 RESET disjoint layer invariant) |

ADR-076 §결정 4 의 4-layer disjoint 패턴 N-layer 확장과 동형 (ADR-077 §결정 5 4-layer counter disjoint 와 같은 구조).

### vs Story 분할 (Path B in Issue #896)

본 pattern 채택 = mid-flight rebase 일관 자동화. Story 분할 path 는 **orthogonal future concern** — 본 pattern 이 작동하지 않는 case (예: 동일 SSOT 의 의미적 conflict, 단순 line append 아님) 가 발생하면 Story 자체를 작게 분할 검토. 즉 본 pattern = 1차 선택, 분할 = 2차 선택.

### vs ADR-039 §결정 14 (CFP-895 `pre-spawn-pin`)

ADR-039 §결정 14 = branch creation 시점 의무 (pre-action). 본 pattern = rebase 시점 의무 (mid-action). 양 패턴 짝 — `pre-spawn-pin` 으로 stale-base 발생 자체를 차단하고, 발생 시 (parallel session main churn 자연 발생) additive-merge 로 손실 0 정합.

## 메커니즘 cross-ref

| 메커니즘 | normative anchor |
|---|---|
| `pre-spawn-pin` (branch creation 시점) | ADR-039 §결정 14 + playbook §3.0.16 |
| parallel-epic-conflict-check (cross-section detection) | `templates/github-workflows/parallel-epic-conflict-check.yml` (ADR-050) |
| label-registry PATCH bump (additive) | 본 개념 I-1 |
| evidence-registry tail append (additive) | 본 개념 I-2 |
| cross-section additive resolution | 본 개념 I-3 |
| verify-before-assert (rebase 결정 전 HEAD 고정) | ADR-073 §결정 1 |
| 4-layer counter disjoint (cross-pollinate 금지) | ADR-077 §결정 5 |

## 관련 ADR

- [ADR-076](../../../archive/adr/ADR-076-declarative-reconciliation-upgrade.md) — §4.7 marker-aware 2-way / wholesale_mirror 패턴의 long-running rebase 영역 확장 anchor (인접 도메인)
- [ADR-039](../../../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — §결정 14 `pre-spawn-pin` mandate (CFP-895) — 본 pattern 의 짝
- [ADR-064](../../../archive/adr/ADR-064-decision-principle-mandate.md) — §결정 4 parallel default (mid-flight churn 의 원인)
- [ADR-073](../../../archive/adr/ADR-073-orchestrator-verify-before-assert.md) — HEAD 고정 before rebase decision
- [ADR-077](../../../archive/adr/ADR-077-clarification-forced-reinvestigation-propagation.md) — §결정 5 4-layer disjoint N-layer 확장 anchor

## 변경 이력

| 일자 | 변경 | carrier |
|---|---|---|
| 2026-05-17 | 신규 작성 — 2× 누적 (CFP-785 / CFP-848) 후 codify | CFP-896 |

## 운영 시그널

- mid-flight rebase 의 monotone PATCH bump 위반 = label-registry-v2.md `version:` frontmatter 의 N 값이 main 보다 작게 set 되어 있는지 grep-detect (별 follow-up CFP 영역 — 후속 mechanical lint)
- evidence-registry tail append 위반 = main 에 존재하던 entry name 이 본 PR diff 안 deletion 으로 나타나는지 detect (별 follow-up CFP)
- 본 concept doc = narrative codification 만; mechanical enforcement 는 후속 carrier (현재 시점 — manual reviewer responsibility + Orchestrator self-discipline)

## verified-via (ADR-073)

- PINNED_MAIN_HEAD = `7593d5c4ec7175e0c5c28297fcc11c62b3dbf6d6` (post-CFP-894 merge — branch parent verified)
- CFP-785 / CFP-848 commit lineage (memory `project_epic_ab_clarification_rescan_pause.md` Story-3 / Story-5 추월 evidence)
- PMO retro Story-5 §6 NEW pattern 2 (PR #588 merge `1c3f6143`)
- Issue #896 §1 verbatim 2× 누적 표
