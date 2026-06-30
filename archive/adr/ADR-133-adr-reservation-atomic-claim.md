---
adr_number: 133
title: "ADR-RESERVATION atomic claim 프로토콜 — 단일-셀 OCC(GitHub Contents API sha→409) artifact-slot-level 1차 방어 layer (#724 흡수, Epic CFP-2481 E3a)"
status: Proposed
category: orchestration/governance
date: 2026-06-30
carrier_story: CFP-2489
parent_epic: CFP-2481
supersedes: null
amends: null
amendments: []
amendment_log: []
related_adrs:
  - ADR-050   # 강화 대상 — PR-level post-hoc re-sort 위에 artifact-slot-level pre-hoc atomic claim 1차 방어 layer 추가 (폐기 아닌 ratchet)
  - ADR-036   # 사고방식 상속 — server-side atomic 권위 위임 (KEY=Issue#). ADR-133 = ADR 번호에 OCC 적용
  - ADR-085   # 3-layer disjoint precedent — session-level pre-hoc. axis-disjoint 신규 ADR 정당화 선례 (ADR-050 과 disjoint 별 입도)
  - ADR-070   # chief author inline append precedent 정합 보존 의무 (claim 채널이 inline append 경로를 깨지 않음)
  - ADR-082   # Amendment 17 sub-scope 1-G (amendment_id slot pre-claim 4-tuple) 의 adr_number slot 일반화 — 중복 신설 아님
related_files:
  - archive/adr/ADR-RESERVATION.md
  - archive/adr/ADR-050-parallel-epic-conflict-coordination.md
  - scripts/post-merge-telemetry.sh
  - docs/domain-knowledge/domain/jsonl-write/race-condition-handling-pattern.md
  - templates/github-workflows/parallel-epic-conflict-check.yml
  - docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md
is_transitional: false
---

# ADR-133: ADR-RESERVATION atomic claim 프로토콜

## 상태

Proposed (2026-06-30 KST) — Epic CFP-2481 (Epic 병렬 실행 정형화) Phase A, E3a carrier (CFP-2489). **발의·설계만** — 구현(claim primitive script + race-guard 게이트 + mutation-RED)은 E3b carrier. `Closes #724`.

본 ADR 는 ADR-050 §결정 1(사후 re-sort)을 **폐기하지 않고** 그 위에 사전 차단 1차 방어 layer 를 추가하는 **강화 ratchet** 이다(약화 surface 0). `is_transitional: false` — 영구 강화 방향.

## 컨텍스트

### 문제 — read-modify-append lost-update race

복수 Orchestrator 세션(또는 병렬 dispatch 된 복수 ArchitectAgent)이 `archive/adr/ADR-RESERVATION.md` 의 마지막 ADR 번호 N 을 동시에 읽고 각자 N+1 을 자기 번호로 점유하면 **lost-update**(갱신 분실) — 둘 다 N+1 을 reserve 하고 한쪽이 분실된다. 동시성 제어 이론의 고전적 race 다.

```
세션 A: read N ─────────────► modify N+1 ─► append N+1 → commit
세션 B:    read N (동시) ────► modify N+1 ─► append N+1 → commit
결과:   둘 다 N+1 점유 → 한쪽 갱신 분실 (lost-update)
```

### Evidence — 3 carrier 누적 (과거 2 + 현재 LIVE 1)

| # | carrier | 사고 |
|---|---------|------|
| 1 | CFP-708 (Issue #708) | ArchitectAgent 병렬 dispatch 로 ADR-074 동시 reserve |
| 2 | CFP-709 (Issue #709) | (동시) ADR-074 동시 reserve → **수동 해소** (CFP-708=074 / CFP-709=075) |
| 3 | CFP-2469 (#2485 MERGED) | ADR-132 소비 후 **ADR-RESERVATION row 누락 lapse** — Epic CFP-2481 spec 의 ADR-번호 사전 예약 대응(위험 A)이 lapse 로 무력화된 **현재 LIVE 사례** |

carrier #1+#2 = CFP-708 retro §6 + CFP-709 retro §6 합산 escalation(pattern_count 2 threshold reach, `escalation_action: escalate_user`) → #724 carrier 격상. carrier #3 = 본 Epic 진행 중 spec 작성 시점에 실제로 발생한 lapse — 사전 예약 convention 만으로는 race/lapse 가 재발한다는 현재형 증거(registry rows 114/116-119/122-125/128/132 = 다수 lapse gap 존재, append 누락이 구조적 빈발).

### 근본원인 — 2-writer 공존 + mechanical atomic lock 부재

`archive/adr/ADR-RESERVATION.md` 의 write 주체는 선언상 GitOpsAgent 전용(ADR-050 §결정 1 SSOT)이나, 실측 row 다수(70/71/74/76/77/78/79/80/81/82...130/131)가 `ArchitectAgent inline append per CFP-578 / ADR-070 chief author precedent` 다 — **GitOpsAgent SSOT 영역과 ArchitectAgent chief author inline append 영역이 공존**하며 후자에 mechanical atomic lock 이 없다. 두 writer 가 mechanical 직렬화 없이 같은 카운터를 read-modify-append 하는 것이 race 진원이다.

### 제약 — GitHub 가 유일 공유 조율 채널

ADR-050 컨텍스트 verbatim: *"두 세션은 직접 통신이 불가능하므로 GitHub 가 유일한 공유 조율 채널이다."* 따라서:
- 메모리 공유 CAS(하드웨어 원자 명령)·OS filelock·전역 lock 서버 = **사용 불가**(세션 간 공유 메모리/파일시스템 없음).
- atomic claim 은 **GitHub server-side 원자 연산 위에서만** 구현 가능.

### 선례 — ADR-036 atomic 위임 사고방식 상속

ADR-036 "Project key atomic reservation"(KEY = `<PREFIX>-<Issue#>`)은 동형 read-modify-write race(`find/sort/max+1`)를 **GitHub Issue numbering server-side atomic 에 위임** → race window 0 으로 해소했다. 핵심 함의:

> **사용자 원문 "Epic Story slot 동시 점유 race" 는 ADR-036 으로 이미 해결됨.** Story KEY 는 Issue# 에 atomic 바인딩되어 race window 0 이다. 따라서 E3a 의 실 미해결 race 는 **ADR 번호 한정**이다. ADR 번호는 Issue# 와 분리된 별도 시퀀스(레지스트리 내부 카운터)라 Issue# 위임이 직접 적용되지 않고 별도 atomic primitive 가 필요하다. (단 "server-side atomic 권위에 위임" 사고방식은 그대로 상속 — §결정 2 가 이를 Contents API SHA OCC 로 실현.)

## 결정

### §결정 1 — 메커니즘 정명: OCC (CAS 는 단일-셀 특수형 비유)

본 race 의 정확한 동시성 제어 모델은 **OCC(Optimistic Concurrency Control, 낙관적 동시성 제어)** 다. 공유 메모리가 아닌 **공유 리소스**(GitHub repo)이므로 하드웨어 CAS(CPU 원자 명령)는 직접 적용 불가 — 비유로만 차용한다.

| 패러다임 | 본 race 적용 | 적합성 |
|----------|-------------|--------|
| Pessimistic lock | 번호 claim 전 전역 lock 선점 | **부적합** — 세션 간 공유 lock 서버 부재 |
| **OCC** | version stamp(blob SHA) 후 commit 시점 불일치 reject·재시도 | **적합 — 채택** — GitHub 가 version stamp 네이티브 제공 |
| CAS | "최고 번호 여전히 N 일 때만 N+1 swap" 원자 연산 | OCC 의 단일-셀(single-cell) 특수형 — 비유 차용 |

- **OCC** = lock 없이 자유롭게 읽고, 로컬에서 수정하고, commit 시점에 읽었던 version 이 그대로인지 server-side 검증(validation phase)해 불일치 시 abort+retry. 3-phase(read / validate / write).
- **사용자 원문 "CAS/optimistic-lock" 병기는 틀린 게 아니라** — 단일 카운터 값(ADR 번호)의 conditional update 라는 점에서 **CAS = OCC 의 단일-셀 특수형**이며 GitHub 환경에서는 동일 primitive(blob SHA conditional PUT)로 실현된다.

**산업 정합(고유 발명 아님)**: GitHub Contents API `sha`→409 는 HTTP `If-Match`/ETag→412 의 도메인 특수화이며, DynamoDB conditional write / etcd revision CAS / JPA `@Version` 와 동형 version-stamp OCC 다. ADR-036 의 "원자 보장을 외부 권위에 위임" 선례와도 정합.

### §결정 2 — 실현 채널 hard-commit: GitHub Contents API PUT `sha`→409 retry (load-bearing 분기)

단일-셀 OCC 를 server-side atomic 으로 실현하는 REST 채널은 한정적이며, 이 선택이 설계의 load-bearing 분기다:

- **✅ Contents API `PUT /repos/{owner}/{repo}/contents/{path}` — 채택**: 요청에 기존 파일의 blob `sha` 를 mandatory 전달 → server 가 현재 SHA 와 비교 → **불일치 시 `409 Conflict`**, 일치 시에만 atomic 갱신. **REST-only 로 보장되는 진짜 단일-셀 OCC**(version stamp = blob SHA, validation = server-side SHA 비교).
- **❌ Git Refs API `PATCH /git/refs/{ref}` — 부적합**: `force` boolean 만 있고 **expected-old-SHA CAS-equality precondition 부재**. 유일한 충돌 거부는 `force=false` 의 fast-forward 거부(HTTP 422)인데 이는 branch HEAD 단위라 *"최고 ADR 번호 = N 일 때만 N+1 점유"* 라는 **단일 카운터값 직렬화**를 실현하지 못한다. 따라서 단일-셀 OCC 는 Contents API `sha`→409 경로가 유일.

**신규 알고리즘 발명 금지 — Pattern A binding (RefactorAgent reusability 축)**: 본 채널은 codeforge 가 이미 `docs/domain-knowledge/domain/jsonl-write/race-condition-handling-pattern.md` Pattern A(GitHub Contents API SHA-based optimistic concurrency, **모든 cross-repo jsonl write 의무 패턴**)로 codify 한 것과 동일 primitive 다. **작동 참조구현 = `scripts/post-merge-telemetry.sh`** (Contents API conditional PUT `-f sha=$SHA` + HTTP 409 감지 + re-fetch SHA + jitter retry max 3 + 소진 시 fail). ADR-133 은 신규 알고리즘을 발명하지 않고 **이 Pattern A 를 ADR-RESERVATION.md 에 binding** 한다(E3b 가 재사용·일반화 구현).

### §결정 3 — 2-channel 분리: claim 채널(빠른 OCC) vs audit 채널(PR merge)

현 reservation append 는 **git-commit 채널**(chief author worktree → PR merge)인데 Contents API PUT 은 **long-lived branch 로의 직접 push** 다 — 두 채널이 다르다. 따라서 ADR-133 은 두 채널을 분리 명시한다(prior art Pattern B = long-lived branch + sequential merge queue 가 선례):

| 채널 | 대상 | 메커니즘 | 시점 |
|------|------|----------|------|
| **claim 채널** (빠른 OCC) | ADR 번호 atomic 점유 | 전용 long-lived state branch(예 `adr-reservation-state`)에 Contents API PUT `sha`→409 retry | claim 즉시 직렬화 (PR merge 무관) |
| **audit 채널** (느린 PR merge) | 실제 ADR 파일 + RESERVATION row 영속화 | 기존대로 chief author worktree → PR merge | review/merge 정상 경로 |

- claim 채널이 **race 차단의 1차 방어**(번호 점유 직렬화), audit 채널이 **영속 기록 + review**.
- **ADR-070 chief author inline append 정합 보존**: claim 채널은 ArchitectAgent 의 RESERVATION row inline append 경로를 **막지 않는다**. claim 채널이 점유 사실을 atomic 직렬화하고, audit 채널의 row append(inline 또는 GitOpsAgent)는 그 점유 결과를 영속화하는 후속 단계다 — write path 강제 경유로 inline append 를 깨면 ADR-070 chief author scope 와 충돌하므로, **claim 은 점유 직렬화 / append 는 기록**으로 책무 분리(E3b 가 정합 구현 — §Out-of-Scope).
- **단일 채널 trade-off(대안)**: claim·audit 를 한 채널(기존 git-commit + 강한 사후 게이트)로 유지하는 대안이 존재한다. 채택안(2-channel) 대비 장점 = 구현 단순(신규 branch 0)·write path 무변경, 단점 = claim 직렬화가 PR merge 시점까지 지연돼 race window 가 열린 채 유지(현 상태와 동일). 본 ADR 은 race window 즉시 차단을 우선해 2-channel 을 권장 1안으로 hard-commit 한다(§결정 7 권장/대안 참조).

### §결정 4 — claim ↔ commit 상태 전이 + 실패/취소 정책

ADR 번호 slot 의 lifecycle 상태 전이를 다음으로 정의한다(기존 RESERVATION enum `reserved | active | archived` 와 정합):

```
unclaimed ──claim(OCC PUT 성공)──► claimed ──ADR 파일 merge──► committed/active
              │                       │
              │ 409 reject            │ abandon (ADR 미작성)
              ▼                       ▼
        retry (다음 번호 재취득)   reserved 잔류 (회수 정책 = E3b)
```

| 상태 | 의미 | 진입 |
|------|------|------|
| `unclaimed` | 번호 미점유 | 초기 |
| `claimed` / `reserved` | OCC PUT 성공으로 atomic 점유 | claim 채널 PUT 200/201 |
| `committed` / `active` | ADR 파일 merge 완료 | audit 채널 PR merge |
| 실패 (409) | 다른 세션이 그 사이 점유 | OCC validation 불일치 → 다음 번호 재취득 재시도 |
| 취소 (abandon) | 점유 후 ADR 미작성 | `reserved` 잔류 (자동 회수 = E3b/후속, §결정 6) |

- **자동 회수(stale slot reclaim) 정책은 E3b/후속** — 본 ADR 은 상태 전이 모델만 명시하고, 회수 trigger·기준·실행은 구현 lane 결정으로 deferred(§Out-of-Scope).

### §결정 5 — ABA 내성: append-only 단조성 불변식

OCC 의 단일값 비교에는 **ABA 문제**가 도사린다 — client 가 값 A 를 읽고 그 사이 다른 client 가 A→B→A 로 되돌리면 첫 client 의 "여전히 A" 검증이 **변경 없음으로 오판**한다(값만 보고 이력을 안 봄). 표준 해법 = 단조 증가 version stamp.

**ADR-133 도메인 매핑**:
- blob SHA(내용 해시) **자체는 ABA 를 막지 못한다** — 바이트 복귀 시 hash 도 복귀(값-동등성 검사).
- **ABA 내성은 ADR-RESERVATION.md 의 append-only / 번호 단조 증가 불변식에서 온다** — 번호가 단조 증가하고 row 가 append-only 이면 A→B→A 내용 복귀가 구조적으로 발생하지 않는다(되돌림 없음).
- **claim 채널을 별도 state 파일로 분리할 경우(§결정 3)** 그 파일이 reset/rollback 가능하면 ABA 가 재현될 수 있다 → **claim state 의 독립 단조성 불변식(번호 되돌림 금지 + abandoned slot 재사용 정책)을 ABA 방어로 명시 의무**(구현 = E3b).

### §결정 6 — 구현 경계: 본 ADR = 설계만, E3b = 구현

본 ADR 은 **발의·설계만** — 동작/구현은 Epic CFP-2481 E3b carrier 다. 명확한 경계:

| 본 ADR (E3a, 설계) | E3b (구현) |
|--------------------|------------|
| OCC 정명 / Contents API 채널 hard-commit / 2-channel 분리 / 상태 전이 / ABA 불변식 / Pattern A binding 선언 | `scripts/lib/adr-reservation-atomic-claim.py` 신설 (Pattern A 일반화) |
| 권장 1안 + 대안 1안 §결정 기록 | claim primitive 동작 + claim↔append 정합 (ADR-070 inline append 보존) |
| (선언) blocking race-guard 게이트 정당성 | race-guard 게이트 + `tests/scripts/test_adr-reservation-atomic-claim.sh` mutation-RED |
| (명시만) stale-path dead-gate 존재 | `parallel-epic-conflict-check.yml` L61 path 정정 (`docs/adr/` → `archive/adr/`) |
| (명시만) stale slot 자동 회수 필요성 | 자동 회수 trigger·기준·실행 |

`mechanical_enforcement_actions: []` — 본 Phase 1 = declaration-only(검사 스크립트·required check 0 신설, 회귀 0). mechanical wire 는 E3b carrier(ADR-082 §결정 6 + ADR-070 §D5 declaration-only retain pattern 답습 — pattern_count ≥ 2 재발 시 후속 CFP MUST promote to mechanical lint).

### §결정 7 — 권장 1안 vs 대안 1안 (사용자 trade-off 영역 — #724 escalation 대응)

#724 자체결정 = `escalation_action: escalate_user`(mechanical lock vs convention trade-off = 사용자 결정 영역). 본 Story 는 발의·설계만이므로 chief author 가 권장 1안을 hard-commit 하고 trade-off 를 §결정에 기록한다(요구사항 lane hard-block 아님):

- **권장 1안 (채택) — mechanical OCC lock (2-channel)**: Contents API `sha`→409 claim 채널(§결정 3) + Pattern A binding(§결정 2). race window 를 점유 시점에 즉시 차단. 비용 = write path 일부 전환(claim/append 책무 분리로 ADR-070 inline append 정합 보존), 신규 long-lived branch 1.
- **대안 1안 — convention 강화 (현 sequential append + 강한 사후 re-sort)**: ADR-050 §결정 1 유지 + 사후 게이트(`parallel-epic-conflict-check.yml`)를 dead-path 정정 후 blocking 승격. 비용 0 write-path-change, 단 race window 가 merge 시점까지 열려 lapse 재발 위험 잔존(carrier #3 evidence).
- **비가역 escalate 조건**: 권장 1안의 mechanical lock 이 ADR-070 chief author inline append 를 깨는 **비가역 변경으로 판명되면** 그때 escalate_user(ask-trigger ③ 비가역·고비용). 본 설계는 claim/append 책무 분리로 inline append 를 보존하므로 비가역 충돌 미발생 — 설계리뷰 lane 이 정합 최종 확인.

### §결정 8 — 3-layer disjoint + ADR-082 일반화 경계

**(a) 3-layer disjoint — ADR-050 강화, 약화 아님**: 병렬 충돌 조율은 coordination 입도(granularity)가 서로 다른 3 layer 가 정합 공존한다:

| layer | ADR | 입도 | 시점 |
|-------|-----|------|------|
| 1 | ADR-050 | **PR-level** | post-hoc (사후 re-sort, non-blocking) |
| 2 | ADR-085 | **session-level** | pre-hoc (세션 ownership 사전 조율) |
| 3 | **ADR-133 (신규)** | **artifact-slot-level** | pre-hoc (ADR-번호 단일 slot atomic claim) |

ADR-133 은 ADR-085 의 4·5번째 sub-decision 이 아니라 **별 입도의 신규 layer** 다. ADR-085 가 ADR-050(PR-level)과 axis-disjoint 신규 ADR(status Accepted)로 채택된 선례를 답습 — 신규 ADR 정당화 근거. **ADR-050 §결정 1(post-hoc re-sort)·§결정 3(non-blocking) 약화 금지 — 1차 방어 layer 추가**(ratchet 보존).

**(b) ADR-082 Amendment 17 sub-scope 1-G 일반화 (중복 신설 아님)**: ADR-082 Amd 17 = `amendments_reserved[]`(ADR-RESERVATION sub-tree, CFP-1058) 의 `amendment_id` slot 을 chief author write 전 strict pre-claim 하는 **4-tuple primitive** 를 이미 codify 했다: (a) pre-reservation row pre-append 의무 / (b) spawn prompt `pre_reserved_amendment_slots` field / (c) reservation row ↔ actual write cross-verify / (d) `pre_reservation_verified` annotation. ADR-082 본문이 *"ADR number reservation(ADR-050 §결정 1)과 amendment slot reservation(Amd 17) = 동일 race coordination 패턴"* 명시.

> **ADR-133 = 이 4-tuple 을 `amendment_id` slot → `adr_number` slot 으로 일반화**한다(중복 신설 아님 — 기존 primitive 확장, RefactorAgent reusability 축). 단 ADR-082 Amd 17 Wave 1 = **declaration-only behavioral mandate** 이고 Wave 2 mechanical wire(`amendment-slot-reservation-check`)는 **실 workflow/script 파일 부재**(verified-via `git ls-tree -r origin/main` → 0 매치) = 동형 미완 layer. ADR-133 의 mechanical OCC(§결정 2)가 이 미완 layer 를 `adr_number` 축에서 실현한다(E3b). EC-4(amendment_id slot race)도 동일 OCC primitive 로 커버 가능(설계 scope 명시, 구현 = E3b).

## 결과

- ADR 번호 점유 race(lost-update)가 **claim 시점 atomic OCC 로 사전 차단**되어 carrier #1/#2(수동 해소) + #3(lapse) 유형의 사고가 구조적으로 제거된다(E3b 구현 후).
- ADR-050 §결정 1(post-hoc re-sort)은 보존되며 그 위에 artifact-slot-level 1차 방어 layer 가 추가된다 — defense-in-depth ratchet.
- **#724 흡수** — `Closes #724`. ancestry = CFP-708 retro §6 + CFP-709 retro §6 합산 escalation lineage(pattern_count 2 threshold reach).
- **본 ADR 산출 = ADR-133 문서 + ADR-RESERVATION row append** (plugin-codeforge). 코드 변경 0(E3a 설계만). contract/registry version bump 0(kind:contract/kind:registry frontmatter 미수정).
- **설계리뷰 lane 으로 넘기는 미해결 항목**(§결정 7 trade-off / claim↔append 정합 비가역성 / EC-4 amendment slot scope 포함 여부)은 설계리뷰가 최종 확인.

### 후속 carrier

- **E3b (구현)**: claim primitive script + race-guard 게이트 mutation-RED + stale-path dead-gate 정정 + stale slot 자동 회수.
- **E2**: parallel-work-sentinel mechanical wire / force-push HEAD-pin 가드(#1027).

## 관련 ADR

- **ADR-050** Parallel Epic Conflict Coordination — 강화 대상(PR-level post-hoc). 약화 금지, 1차 방어 layer 추가.
- **ADR-036** Project key atomic reservation — 사고방식 상속(server-side atomic 권위 위임). Story slot race 는 ADR-036 으로 이미 해결(E3a scope = ADR 번호 한정).
- **ADR-085** Multi-session collaboration protocol — session-level pre-hoc. axis-disjoint 신규 ADR 선례.
- **ADR-070** Codex verify-before-trust — chief author inline append precedent 정합 보존 의무.
- **ADR-082** Amendment 17 sub-scope 1-G — amendment_id slot pre-claim 4-tuple 의 adr_number slot 일반화 원천.

## 변경 이력

- 2026-06-30 KST: 신규 발의 (CFP-2489, Epic CFP-2481 E3a). status Proposed. `Closes #724`.
