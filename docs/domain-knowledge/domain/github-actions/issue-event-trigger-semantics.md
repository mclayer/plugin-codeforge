---
kind: domain_fact
type: domain-knowledge
area: github-actions
topic_slug: issue-event-trigger-semantics
title: GitHub Actions issue event trigger semantics — REST vs Web UI label timing
status: Active
tags:
  - github-actions
  - issue-events
  - webhook
  - label-timing
  - n-plus-one-firing
related_adrs:
  - ADR-036  # CFP-260 atomic Issue numbering — REST event ordering 의존
related_stories:
  - CFP-280
  - CFP-275
created: 2026-05-09
updated: 2026-05-09
---

# GitHub Actions issue event trigger semantics

## Summary

GitHub REST API or Web UI Issue Form submit 시 발화하는 webhook event 의 **N+1 firing law** 와 `issue.labels` field timing 차이 SSOT. codeforge `story-init.yml` 등 label-conditional workflow 설계 시 `[opened, labeled]` 조합 + step-level guard 가 의무임을 명시한다.

## Problem

`on.issues.types: [opened]` 단독 trigger 는 REST-filed Issue 에서 `issue.labels` 가 항상 `[]` 인 채로 발화 — label-conditional job guard 가 false → silent skip. `labeled` event 는 29s 후 별도 발화하지만 trigger 에 미포함 시 workflow 미실행. CFP-280 이 `[opened, labeled]` 합성 + step-level file-existence dedup 으로 해소.

## Usage

codeforge workflow 가 label-conditional trigger 를 설계할 때:
1. `on.issues.types: [opened, labeled]` 조합 채택 (REST + Web UI 양쪽 대응)
2. Job/step level guard: `if: contains(github.event.issue.labels.*.name, 'type:story')` 또는 file-existence marker 로 dedup
3. `concurrency: group: story-init-${{ github.event.issue.number }}` 로 dual-firing 직렬화

상세 선택 기준은 [workflow-idempotency-patterns](workflow-idempotency-patterns.md) 참조.

## 정의

GitHub REST API `POST /repos/{owner}/{repo}/issues` 호출 또는 Web UI Issue Form submit 시 GitHub 가 발화하는 webhook event 의 발화 순서·payload 차이·workflow trigger 매핑 법칙. 본 페이지는 codeforge family workflow 가 `on.issues.types` 를 결정할 때 의존하는 **N+1 firing law** 와 그 운영 함의를 정리한다.

## 컨텍스트

CFP-275 Story 발의 시 발견된 결함이 origin 이다. `mclayer/codeforge-internal-docs:.github/workflows/story-init.yml` 의 trigger `on.issues.types: [opened]` 는 `mcp__github__issue_write` (REST) 로 filed 된 type:story Issue 를 silent skip 했다. 원인 = `opened` event payload 의 `issue.labels` field 가 server-side label 적용 이전 snapshot (REST path 에서는 거의 항상 `[]`) → `if: contains(labels, 'type:story')` job-level guard 가 false → job skip → 후속 `labeled` event 가 29s 후 발화하지만 trigger 미수용. 결과: REST-filed Story 마다 manual scaffold (CFP-275 패턴, Issue #9 precedent) recovery 의존.

본 결함의 근본 원인은 GitHub 의 event 발화 모델 자체이며, codeforge family workflow 6 종 중 `story-init.yml` (Phase 1 Story file 자동 생성) 과 `phase-label-invariant.yml` (label 변경 invariant 검증) 이 직접 의존. 후자는 본 N+1 firing law 를 이미 인지한 패턴 (`types: [labeled, unlabeled]` + step-level `if: github.event.action == 'labeled'`), 전자는 미인지 — CFP-280 가 `[opened, labeled]` 채택 + step-level guard 도입으로 해소.

## 핵심 규칙

### N+1 firing law

Issue 생성 시 attach 되는 label 개수 N → GitHub 가 발화하는 event = `opened` 1 + `labeled` N. label N 개를 한 번의 REST call 에서 `labels: [...]` 파라미터로 함께 전달해도 동일 — server-side 가 issue 생성 commit 후 label apply 를 별도 transaction 으로 처리하기 때문이다.

| Trigger source | `opened` payload `issue.labels` | `labeled` events 발화 | 발화 latency (관측치) |
|---|---|---|---|
| REST API (`POST /repos/{owner}/{repo}/issues` with labels) | `[]` (거의 항상) | N 개, 후행 | ~10-60s (CFP-275 case 29s) |
| Web UI Issue Form submit | `[]` 또는 partial (race) | N 개, 후행 | ~5-30s |
| `gh issue create --label X --label Y` | `[]` | N 개 | REST 와 동일 |
| `mcp__github__issue_write` (현 wrapper 권장 path) | `[]` | N 개 | REST 와 동일 |

**모든 source 가 동일 N+1 sequence** — Web UI 도 client-side label state 가 동시 attach 되어 보이지만 server 내부적으로는 동일 pattern.

### `on.issues.types` 매트릭스 + 결함 패턴

| `on.issues.types` 설정 | REST-filed Issue | Web UI Issue | 결함 패턴 |
|---|---|---|---|
| `[opened]` 단독 | ❌ silent skip (label race) | △ race-prone | CFP-275 / story-init.yml 결함 본 form |
| `[labeled]` 단독 | ✅ trigger | ✅ trigger | label 변경 시마다 false trigger |
| `[opened, labeled]` + step-level guard | ✅ + idempotency 의무 | ✅ + idempotency 의무 | dual-firing → file existence guard / concurrency 필수 |
| `[opened, labeled, unlabeled]` | ✅ | ✅ | label 제거 시도 false trigger 추가 |

**CFP-280 채택 = `[opened, labeled]` + step-level guard** — REST + Web UI 양쪽 path 커버 + dual-firing 은 file existence guard (CFP-280 idempotency step) 가 흡수.

### Step-level guard 표준 패턴

`on.issues.types: [opened, labeled]` + 다음 guard step 으로 무관 label 변경 (component:* / area:*) false trigger 차단:

```yaml
if: github.event.action == 'opened' || (github.event.action == 'labeled' && contains(github.event.issue.labels.*.name, 'type:story') && contains(github.event.issue.labels.*.name, 'phase:요구사항'))
```

opened-event 시는 무조건 진입 (이후 file existence guard 가 actual scaffold 결정), labeled-event 시는 required label 전체 set 갖춘 시점에만 진입.

### PAT vs GITHUB_TOKEN 행동 차이

`GITHUB_TOKEN` 으로 label 추가 시 → 후속 workflow trigger 차단 (action-in-action 무한 루프 보호 — GitHub native invariant). 본 N+1 law 영역에서 implication = workflow 가 자체 label 변경 시 재 trigger 안 됨 (dedup 자연 정합).

`PAT` (Personal Access Token) 사용 시 → trigger 차단 부재 → 무한 루프 위험. codeforge family workflow 는 GITHUB_TOKEN 권장 (default behavior 채택, CFP-280 정책 동일).

### REST event timing 외부 reference

- GitHub Actions docs — [Events that trigger workflows / `issues`](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#issues)
- GitHub REST API — [Create an issue (`POST /repos/{owner}/{repo}/issues`)](https://docs.github.com/en/rest/issues/issues#create-an-issue) — `labels` 파라미터 행동
- GitHub Community discussion — REST-vs-WebUI label sync timing 사례 보고 (latency 변동 큼, server load 의존)

## 경계

### 비-적용

- **`on.issues.types: [closed, reopened, edited, deleted, transferred, pinned, ...]`** — 본 페이지의 N+1 law 는 Issue 생성 시점 한정. 다른 lifecycle event 는 별도 mechanism (state transition / property mutation).
- **`on.pull_request.types`** — PR 생성 event 는 별도 N+1 분석 영역 (label race 영향 동일하나 본 페이지 scope 외, 별도 페이지 후속 작성 가능).
- **GitHub Apps webhook 직접 수신** — `octokit` direct webhook receiver 는 raw event 수신 → 본 페이지의 trigger 매핑 매트릭스 비-적용 (raw event sequence 만 의존).

### 관련 용어 분류

- **Event payload `issue.labels`**: webhook delivery 시 GitHub 가 capture 한 snapshot. server-side mutation timing 과 부분 race 가능.
- **Trigger 매핑**: `on.issues.types` 의 declared types 에 발화 event 가 match 시 workflow run 생성. job-level `if:` + step-level `if:` 가 secondary filter.
- **Idempotency guard**: dual-firing (opened + labeled 양쪽 trigger) 시 first-firing 결과를 second-firing 이 redundantly 적용 안 하도록 차단하는 mechanism. CFP-280 채택 = file existence (`docs/stories/<KEY>.md`).
- **Concurrency group**: `concurrency: { group: <expr>, cancel-in-progress: bool }` — 같은 group 의 동시 run 직렬화. CFP-260 / ADR-036 Option B 의 `story-init-${{ issue.number }}` 가 본 패턴 채택.

### Race window 분석

CFP-275 case 의 29s latency 는 lower bound 아닌 sample. server load / concurrent webhook delivery 압력 / label N 변동에 따라 0s ~ 분 단위까지 가능. workflow design 시는 **N+1 sequence 자체** 를 invariant 로 가정하고 latency 는 unbounded 로 처리해야 함. file existence guard / concurrency group 이 latency 영향을 흡수하는 mechanism.

## 관련 ADR

- [ADR-036](../../../adr/ADR-036-project-key-atomic-reservation.md) — CFP-260 GitHub atomic Issue numbering. `KEY = PREFIX-${{ issue.number }}` 로 file-system scan + max+1 race 제거. opened event payload 의 `issue.number` 의존 — N+1 firing law 의 `opened` event 가 atomic 한 sequence position 보장 (label race 와 별 영역).

## 변경 이력

- **2026-05-09** — 신규 작성 (CFP-280 carrier Story Phase 1 PR scope). PL synthesis grounded in Story file §6 Researcher 산출물 (§6.1 N+1 firing law / §6.2 PAT vs GITHUB_TOKEN / §6.3 dedup pattern 4종 / §6.4 reference). chief author 가 inline drafts 미제공 — PL 이 SubAgent synthesis 로 보강.
