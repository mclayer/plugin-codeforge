---
kind: domain_fact
type: domain-knowledge
area: github-actions
topic_slug: workflow-idempotency-patterns
title: GitHub Actions workflow idempotency patterns — file marker / concurrency / opened-only filter / PAT-loop prevention
status: Active
tags:
  - github-actions
  - idempotency
  - concurrency
  - dedup
  - workflow-patterns
related_adrs:
  - ADR-036  # CFP-260 atomic Issue numbering — concurrency group precedent
related_stories:
  - CFP-280
  - CFP-260
  - CFP-275
created: 2026-05-09
updated: 2026-05-09
---

# GitHub Actions workflow idempotency patterns

## Summary

N+1 firing (opened + labeled dual-event) 또는 multi-run 환경에서 workflow 의 substantive work 가 1회만 실행되도록 보장하는 **4 종 dedup mechanism** 비교 SSOT. codeforge family workflow (특히 `story-init.yml`) 설계 시 (a) file-existence marker + (b) concurrency group 조합이 default 권장 패턴임을 명시한다.

## Pattern

4 종 dedup mechanism:

- **(a) File-existence marker**: `if: steps.check_file.outputs.exists == 'false'` — substantive work 이미 완료 여부를 산출물 파일 존재로 확인. idempotent re-run safe.
- **(b) Concurrency group**: `concurrency: group: story-init-${{ issue.number }}` — 동일 Issue 에 대한 concurrent run 직렬화. N+1 firing 으로 발화된 동시 run 이 1개만 proceed.
- **(c) opened-only filter**: `if: github.event.action == 'opened'` step-level guard — labeled event 에서 substantive work skip. 단독 사용 시 REST-filed Issue (opened label[] empty) 에서 skip.
- **(d) PAT-loop prevention**: `if: github.actor != 'github-actions[bot]'` — PAT 으로 commit/push 한 경우 workflow 재발화 방지.

codeforge 채택: (a) + (b) 조합 (CFP-280 `story-init.yml`). (c) 단독 = REST-filed Issue silent skip risk (issue-event-trigger-semantics.md N+1 firing law 참조).

## Usage

`story-init.yml` 형태의 label-conditional workflow 설계 시:
```yaml
on:
  issues:
    types: [opened, labeled]
concurrency:
  group: story-init-${{ github.event.issue.number }}
  cancel-in-progress: false
jobs:
  scaffold:
    if: contains(github.event.issue.labels.*.name, 'type:story')
    steps:
      - name: check existing file
        id: check_file
        run: |
          if [ -f "docs/stories/${{ env.KEY }}.md" ]; then
            echo "exists=true" >> $GITHUB_OUTPUT
          else
            echo "exists=false" >> $GITHUB_OUTPUT
          fi
      - name: scaffold
        if: steps.check_file.outputs.exists == 'false'
        run: # ... substantive work
```

## 정의

같은 logical trigger (Issue 생성 / PR 변경 / label apply 등) 이 여러 webhook event 로 발화될 때 workflow 가 1회만 substantive work 을 수행하도록 보장하는 **4 종 dedup mechanism** 의 비교 + 선택 기준. 본 페이지는 [issue-event-trigger-semantics](issue-event-trigger-semantics.md) 의 N+1 firing law 가 노출하는 dual-firing 문제에 대한 응답 영역을 정리한다.

## 컨텍스트

`story-init.yml` (CFP-280 carrier) 가 `on.issues.types: [opened, labeled]` 채택 시 — 같은 Issue 의 opened-event 1 + labeled-event N → workflow run N+1 회 발화. substantive work (branch 생성 / file write / PR open / Issue body update) 은 1회만 수행해야 하며, 후속 dual-firing 은 noop skip 의무. 본 페이지는 4 종 dedup mechanism (file existence marker / concurrency group / opened-only filter / PAT-loop prevention) 의 비교를 통해 CFP-280 채택 (file existence + concurrency group 조합) 의 정당화 근거를 정리한다.

선행 사례: CFP-260 / ADR-036 Option B 가 `story-init` workflow 에 `concurrency: group: story-init-${{ issue.number }}` 를 도입한 것은 본 페이지의 pattern (b) — 그러나 단독으로는 본 페이지 §"핵심 규칙 → Pattern (b)" 의 한계 영역에 해당하므로 CFP-280 가 pattern (a) 와 합성.

## 핵심 규칙

### Pattern (a) — File-existence marker (CFP-280 채택)

**Mechanism**: workflow run 의 substantive step 진입 직전에 target file 의 존재 여부를 검사. 존재하면 step skip (idempotent re-entry).

```yaml
- name: Skip if Story file already exists
  id: existence_check
  env:
    KEY: ${{ steps.key.outputs.key }}
  run: |
    if [[ -f "docs/stories/${KEY}.md" ]]; then
      echo "skip=true" >> "$GITHUB_OUTPUT"
    else
      echo "skip=false" >> "$GITHUB_OUTPUT"
    fi

- name: Substantive step
  if: steps.existence_check.outputs.skip != 'true'
  run: ...
```

**장점**:
- Idempotent guarantee — file system state 가 진실 source.
- Race window 0 (개별 workflow run 내부 sequencing — git checkout 후 file 상태 read).
- Manual recovery (CFP-275 패턴) 와 자연 정합 — manual scaffold 후 workflow re-run 도 skip.
- Half-complete (file 생성 후 PR 등 후속 step 실패) 시 자동 재시도 X — file existence = "초기화 완료" 정의 → manual recovery 영역 (CFP-280 AC-7).

**단점**:
- File 이 진실 source 이므로 workflow 외부에서 file 삭제 시 재 trigger 가능 (의도와 무관한 재실행 위험).
- substantive step 이 file 외 mutation (label / Issue body 등) 만 수행하는 경우 부적합 — file marker 가 진실 indicator 가 아님.

### Pattern (b) — Concurrency group (CFP-260 / ADR-036 Option B 단독, CFP-280 보강)

**Mechanism**: GitHub Actions 의 `concurrency` 키워드로 같은 group 의 run 을 직렬화 / 취소.

```yaml
concurrency:
  group: story-init-${{ github.event.issue.number }}
  cancel-in-progress: false
```

**장점**:
- 같은 Issue 의 reopen / rapid label transition race 직렬화.
- `cancel-in-progress: false` 설정 시 first-firing 보호 (이미 진행 중인 run 우선).
- workflow 외부 state 의존 없음 (GitHub Actions runner 자체 mechanism).

**단점**:
- **First-firing 직후 second-firing 의 substantive work 차단 못 함** — first-firing 의 commit 이 already on remote 상태에서 second-firing 도 동일 work 시도 → branch creation conflict / git push reject.
- 근본 dedup 아닌 ordering — substantive idempotency 는 별도 mechanism 필요 (CFP-280 가 pattern (a) 합성).

### Pattern (c) — Opened-only filter

**Mechanism**: `if: github.event.action == 'opened'` step-level guard. labeled-event 진입 시 무조건 noop.

**장점**:
- Implementation 가장 단순 — 추가 file system / external state 의존 0.

**단점**:
- **REST-filed Issue (label race) 시 silent skip** — opened event payload `issue.labels: []` → job-level `contains(labels, 'type:story')` guard 가 false → job 자체 진입 안 함. CFP-275 결함 본 form. CFP-280 미채택.

### Pattern (d) — PAT-loop prevention (이상 패턴)

**Mechanism**: workflow 자체가 발화시킨 후속 trigger (e.g. label apply → 자기 trigger) 를 차단.

GitHub native 동작:
- `GITHUB_TOKEN` 으로 label 추가 시 → 후속 workflow trigger 자동 차단 (action-in-action 무한 루프 보호 — GitHub native invariant).
- `PAT` 사용 시 → trigger 차단 부재 → 무한 루프 위험.

**장점**:
- GitHub Actions runner 자동 적용 (GITHUB_TOKEN 사용 시).
- 별도 idempotency mechanism 무관하게 자기 trigger 차단.

**단점**:
- 외부 trigger (사용자 / 다른 workflow / 다른 PAT) 차단 못 함.
- self-loop 만 다룸 — 본 페이지 §"컨텍스트" 의 dual-firing 문제와 별 영역.

### CFP-280 채택 조합 = (a) + (b) — 정당화

| Pattern 조합 | first-firing | second-firing (noop 의무) | manual recovery 정합 | 구현 cost |
|---|---|---|---|---|
| (a) 단독 | ✅ | ✅ (file 존재 → skip) | ✅ (manual scaffold 후 skip) | 1 step 추가 |
| (b) 단독 | ✅ (직렬화) | ❌ (substantive work 중복 시도) | ❌ | 1 block 추가 |
| (c) 단독 | ❌ (REST race) | N/A | ❌ | 1 line 추가 |
| **(a) + (b) (CFP-280)** | ✅ | ✅ + 직렬화 | ✅ | 2 mechanism 합성 |
| (a) + (b) + (c) | (c) 가 REST race 차단 | redundant | ❌ (REST path) | over-engineering |

CFP-280 = (a) + (b). pattern (b) 는 CFP-260 / ADR-036 Option B 잔존 — backward-compatible 합성. pattern (c) 명시적 미채택 — REST path 결함이 본 Story 의 origin defect.

## 경계

### 비-적용

- **PR-trigger workflow** — `on.pull_request.types: [opened, synchronize, reopened]` 의 dual-firing 은 별도 분석 영역 (synchronize event 가 substantive — N+1 law 와 다른 pattern).
- **Push trigger** — `on.push` 는 commit SHA 기반 — file existence marker 가 자연 idempotent 이지만 dual-firing 자체가 거의 없음 (push 1 = workflow run 1).
- **Schedule trigger** — `on.schedule` 는 cron — concurrency group 으로 충분, file marker 부적합 (cron run 마다 substantive work).

### 관련 용어 분류

- **Idempotent step**: 같은 input 으로 N 회 실행해도 동일 결과 보장하는 step. file existence marker 가 가장 단순한 enforcement.
- **Substantive step**: file write / GitHub state mutation / PR creation 등 외부 부작용을 가진 step. 본 페이지의 dedup 대상.
- **Dual-firing**: 같은 logical trigger 가 N+1 law 또는 reopen race 등으로 N 회 발화하는 현상. CFP-280 가 다루는 `[opened, labeled]` 채택 시 N=2 이상 가능.
- **Half-complete recovery**: file 생성 후 후속 step 실패 → manual recovery 의무 (자동 재시도 X). CFP-280 AC-7 결정.

## 관련 ADR

- [ADR-036](../../../../archive/adr/ADR-036-project-key-atomic-reservation.md) — CFP-260 atomic Issue numbering. concurrency group `story-init-${{ issue.number }}` 도입 — 본 페이지 pattern (b) 의 codeforge family precedent. CFP-280 가 pattern (a) 합성으로 (b) 단독 한계 보강.

## 변경 이력

- **2026-05-09** — 신규 작성 (CFP-280 carrier Story Phase 1 PR scope). PL synthesis grounded in Story file §6 Researcher 산출물 (§6.3 dedup pattern 4종 비교). chief author 가 inline drafts 미제공 — PL 이 SubAgent synthesis 로 보강.
