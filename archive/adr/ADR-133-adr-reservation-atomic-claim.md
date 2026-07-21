---
adr_number: 133
title: "ADR-RESERVATION atomic claim 프로토콜 — 단일-셀 OCC(GitHub Contents API sha→409) artifact-slot-level 1차 방어 layer (#724 흡수, Epic CFP-2481 E3a)"
status: Accepted   # CFP-2563 (Amendment 2) 로 Proposed→Accepted 승격 — 실배선 authorize (R1 해소)
category: orchestration
date: 2026-06-30
carrier_story: CFP-2489
parent_epic: CFP-2481
supersedes: null
amends: null
amendments: [1, 2, 3]
amendment_log:
  - amendment_id: 1
    carrier_story: CFP-2491
    date: 2026-06-30  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 4", "§결정 5", "§결정 6", "§결정 8"]
    nature: ratchet-up  # E3b 구현 결정 record + §결정6 dead-gate 정정 보정 (강화 방향, ADR-058 §결정 5 면제)
    note: "E3b(CFP-2491, Epic CFP-2481 Phase B) 구현 결정 — (A1-1) §결정6 dead-gate 정정 보정: 두 copy 일괄 archive/adr/ → 비대칭(.github=archive/adr/ wrapper-self, templates=docs/adr/ consumer 정합 무변경) (A1-2) claimant identity field 신설(§결정4 상태전이 보강 — (adr_number,claimant) at-least-once idempotency key) (A1-3) claim-state branch protection mechanical(§결정5 ABA teeth — adr-reservation-state branch allow_force_pushes:false + required_linear_history:true) (A1-4) 언어=Python(ADR-061 §결정6 정합, Pattern A 알고리즘 무손상) + claim-state=별도 JSON artifact(2-channel 경계 보존, ADR-RESERVATION schema bump 0) (A1-5) EC-4 amendment_id slot deferred(§결정8(b) Q2 — adr_number only, amendment_id 확장 = ADR-082 Amd17 Wave-2 follow-up). strengthen direction (약화 surface 0)."
  - amendment_id: 2
    carrier_story: CFP-2563
    date: 2026-07-03  # KST per ADR-079 §결정 2
    decisions_touched: ["§결정 1", "§결정 2", "§결정 3", "§결정 6"]
    nature: ratchet-up  # 실배선 확정(built-but-unwired 해소) + 인용/wording 정정 (강화 방향, ADR-058 §결정 5 면제)
    note: "CFP-2563 실배선 — E3a/E3b 가 만든 primitive/test/stale-reclaim(8 파일)이 실 발급 flow 에 미배선(dead-machinery)이던 상태를 배선 설계로 종결. status Proposed→Accepted 승격(R1 해소). (A2-1) 발급 배선 R2 = claim(번호 직렬화 선행) → 반환번호로 ADR 파일 write → 기존 inline RESERVATION row append(ADR-070 chief scope 무손상). claim↔append disjoint 책무. templates/adr.md L124 Glob(docs/adr) max+1 = consumer default 유지(A1-1 asymmetry 보존), wrapper dogfood 발급만 claim 경유 cross-ref. (A2-2) 부트스트랩+protection R3 = adr-reservation-state branch seed {max_adr_number:<firsthand max>, claims:[]} + protection allow_force_pushes:false + required_linear_history:true + enforce_admins:true, required_pull_request_reviews·required_status_checks 미설정 의무(direct claim PUT deadlock 방지) + 부트스트랩 시 test-PUT smoke 확정. (A2-3) 인용 정정 A1-4 = ACM TOCS 1990 → ACM TOPLAS 12(3):463-492, 1990(dblp journals/toplas/HerlihyW90). (A2-4) §결정1 wording 정정 = If-Match/412 도메인 특수화 → OCC analog(body-sha + 409)(analog 이지 동일 메커니즘 아님 — 검증자 위치 body≠header, 409≠412). (A2-5) doc-reality gap 3곳 배선 대상 명시(playbook atomic 격상 허위 / template L124 cross-ref / ArchitectAgent.md claim 배선 현 0) — parallel-epic-conflict-check.yml L61 은 이미 정정 완료 재-scope 금지. (A2-6) uniqueness lint = warning tier(6-tuple 무변경, OCC=1차 차단·lint=2차 안전망). strengthen direction (약화 surface 0). canonical SSOT = Change Plan wrapper/change-plans/cfp-2563-adr-number-collision-resolution.md(internal-docs)."
  - amendment_id: 3
    carrier_story: CFP-2762
    date: 2026-07-21  # KST per ADR-079 §결정 2
    decisions_touched: ["§A2-6", "§결정 2", "§A2-1"]
    nature: ratchet-up  # digit-width canonical SSOT 문장화(소유 lint/template 축 결손 보완) + CFP-676 misattribution 정정 (강화 방향, ADR-058 §결정 5 면제)
    note: "CFP-2762 digit-width 통일 — ADR 파일명 3-digit zero-pad canonical(`ADR-NNN`) + frontmatter `adr_number` bare integer 를 SSOT 문장으로 codify(A3-1). 근거: §A2-6 uniqueness lint(`CANONICAL_PAD_WIDTH=3`) + §결정 2/A2-1 L271 `archive/adr/ADR-NNN-<slug>.md` write template 가 이미 3-digit 을 de-facto/lint 강제하나 SSOT 문장 결손 → 소유 축의 결손 보완(신규 standalone ADR = phantom). 유일 2-digit 파일명 이상치(번호 72) → `ADR-072` rename 정합(frontmatter adr_number:72 정수 불변 — rendering-only, 번호 invariant). CFP-676 misattribution 정정(A3-2): 구 lint 주석/서사의 'CFP-676 이 2-digit canonical 확정' 은 firsthand 반증 — CFP-676=agent-구조 Story(digit-width 정책 무), 실 근거 = ADR-068 I-4 wording-SSOT / Codex S-CFP676-ADR72-FORM P2. warning tier·§결정 본문 무변경(A3-3). strengthen direction(약화 surface 0). canonical SSOT = Change Plan wrapper/change-plans/cfp-2762-adr-digit-width-unification.md(internal-docs)."
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

**Accepted** (2026-07-03 KST, Amendment 2 / CFP-2563 로 Proposed→Accepted 승격 — 실배선 authorize, R1 해소). 최초 발의 = Proposed (2026-06-30 KST) — Epic CFP-2481 (Epic 병렬 실행 정형화) Phase A, E3a carrier (CFP-2489). **발의·설계만** — 구현(claim primitive script + race-guard 게이트 + mutation-RED)은 E3b carrier(CFP-2491). `Closes #724`. **실 발급 flow 배선(built-but-unwired 해소) = Amendment 2 (CFP-2563) 설계 + Phase 2 배선 carrier.**

본 ADR 는 ADR-050 §결정 1(사후 re-sort)을 **폐기하지 않고** 그 위에 사전 차단 1차 방어 layer 를 추가하는 **강화 ratchet** 이다(약화 surface 0). `is_transitional: false` — 영구 강화 방향.

> **category cross-ref (CFP-2753 정규화)**: primary `orchestration` — 본 결정 성격(병렬 세션 단일-셀 OCC = Orchestrator-level concurrency mechanism, 규칙4 단일 primary). 구 compound `orchestration/governance` 의 secondary 축 `governance`(ADR-RESERVATION registry governance)은 정보 손실 방지 위해 본문 cross-ref 로 보존. [verified: ADR-153 Amendment 1 A1-1]

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

**산업 정합(고유 발명 아님)**: GitHub Contents API `sha`→409 는 HTTP `If-Match`/ETag→412 의 **OCC analog**(body-sha + 409)이며, DynamoDB conditional write / etcd revision CAS / JPA `@Version` 와 동형 version-stamp OCC 다. ADR-036 의 "원자 보장을 외부 권위에 위임" 선례와도 정합.

> **Amendment 2 (CFP-2563) wording 정정 — A2-4**: 최초 "`If-Match`/412 의 도메인 특수화" 표현은 **계보 과대**(over-claim)다 — GitHub 은 검증자를 **요청 body 의 `sha` field** 로 받아 **409** 를 반환하는 반면, RFC 9110 `If-Match` 는 **request header** 로 받아 **412** 를 반환한다(검증자 위치 body≠header, 코드 409≠412). 두 메커니즘은 **OCC analog**(같은 낙관적 동시성 계열)이지 동일 메커니즘의 도메인 특수화가 아니다. 이후 §결정 전반·§7·Change Plan 은 "OCC analog(body-sha + 409)" 표기로 통일한다. (요구사항리뷰 §9.1 P3 advisory 수용.)

### §결정 2 — 실현 채널 hard-commit: GitHub Contents API PUT `sha`→409 retry (load-bearing 분기)

단일-셀 OCC 를 server-side atomic 으로 실현하는 REST 채널은 한정적이며, 이 선택이 설계의 load-bearing 분기다:

- **✅ Contents API `PUT /repos/{owner}/{repo}/contents/{path}` — 채택**: 요청에 기존 파일의 blob `sha` 를 mandatory 전달 → server 가 현재 SHA 와 비교 → **불일치 시 `409 Conflict`**, 일치 시에만 atomic 갱신. **REST-only 로 보장되는 진짜 단일-셀 OCC**(version stamp = blob SHA, validation = server-side SHA 비교).
- **❌ Git Refs API `PATCH /git/refs/{ref}` — 부적합**: `force` boolean 만 있고 **expected-old-SHA CAS-equality precondition 이 부재**하다. 즉 *"최고 ADR 번호 = N 일 때만 N+1 점유"* 라는 **단일 카운터값('최고=N일 때만 N+1') 직렬화**를 server-side conditional 로 실현할 수단이 없다(`force=false` 의 fast-forward 거부는 branch HEAD 단위 정합일 뿐, 단일 셀 카운터 직렬화가 아니다 — 공식문서가 거부 코드를 422/409 둘 다 listing 하므로 구체 HTTP 코드는 비단정). 따라서 단일-셀 OCC 는 Contents API `sha`→409 경로가 유일.

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

## 관련 파일

- `archive/adr/ADR-RESERVATION.md`
- `archive/adr/ADR-050-parallel-epic-conflict-coordination.md`
- `scripts/post-merge-telemetry.sh`
- `docs/domain-knowledge/domain/jsonl-write/race-condition-handling-pattern.md`
- `templates/github-workflows/parallel-epic-conflict-check.yml`
- `docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md`

## Amendment 1 — E3b 구현 결정 (CFP-2491, 2026-06-30 KST)

> E3b(CFP-2491, Epic CFP-2481 Phase B) 설계 lane 이 §결정6 우열(구현) 을 실현하며 확정한 구현 결정. strengthen direction(약화 surface 0). canonical SSOT = Change Plan `wrapper/change-plans/cfp-2491-adr-reservation-atomic-claim-race-guard.md`(internal-docs). 본 Amendment = ADR 본문 결정 보강·보정 cross-ref.

### A1-1 — §결정6 dead-gate 정정 보정: 비대칭 (correction, load-bearing)

§결정6 경계표 우열 verbatim "`parallel-epic-conflict-check.yml` L61 path 정정 (`docs/adr/` → `archive/adr/`)" 은 **두 copy 일괄 정정으로 읽히나 부정확**. firsthand 보정(verified-via `doc-locations.yaml` adr entry + 4-source 독립 수렴):

| copy | 실행 컨텍스트 | L61 정정 | 근거 |
|------|-------------|----------|------|
| `.github/workflows/parallel-epic-conflict-check.yml` | wrapper-self(plugin-codeforge) | `docs/adr/` → **`archive/adr/ADR-RESERVATION.md`** | wrapper(dogfood) ADR = `archive/adr/` |
| `templates/github-workflows/parallel-epic-conflict-check.yml` | consumer 배포본 | **무변경** (`docs/adr/` 유지) | consumer(single_repo) ADR = `docs/adr/` |

두 copy 는 현재 byte-identical 이나 정정 후 **의도적 분기**(context-specific 정합). byte-parity 강제 lint 부재(`check-wrapper-template-managed-coverage.sh` = `.claude/_overlay/` marker scope, 본 workflow 무관). consumer copy 를 `archive/adr/` 로 바꾸면 consumer dead-gate 신규 발생 — §결정6 의 "두 copy" 표현이 이 함정을 가렸다.

### A1-2 — claimant identity field (§결정4 상태전이 보강)

§결정4 상태전이 표(`unclaimed→claimed→committed`)에 **claimant 식별 field 부재** → at-least-once replay(crash-after-200) 시 self-claim 판정 불가. E3b claim state record 에 `claimant = {role}:{story_key}:{run_id}` 추가 의무. `(adr_number, claimant)` 2-tuple = idempotency key. 재실행 시 동일 tuple 발견 → self-claim → 200 간주(re-emit 없음). §11.6 idempotency / §8.5.3 replay 와 정합.

### A1-3 — claim-state branch protection mechanical (§결정5 ABA teeth)

§결정5 ABA 내성("append-only + 단조성 불변식")은 claim state 분리 시 가변 파일이면 무력. mechanical teeth 의무: `adr-reservation-state` branch 에 `allow_force_pushes: false` + `required_linear_history: true`. 없으면 force-push counter rewind 로 §결정5 가 선언으로만 존재. 클라이언트 불변식(`next<=max` reject + claims[] append-only)과 2층 방어.

### A1-4 — 구현 결정 3종 (Pattern A 무손상)

- **언어 = Python** `scripts/lib/adr-reservation-atomic-claim.py`(ADR-061 §결정6 정합). **Pattern A 알고리즘 무손상**(언어선택 ≠ §결정2 신규발명). HTTP = `subprocess`+`gh api`.
- **claim-state = 별도 JSON artifact**(state branch 위) — ADR-RESERVATION.md field 추가 0(2-channel 경계 보존 → schema_version bump 0).
- **stale reclaim = abandoned 마커 + 번호 재사용 금지 + gap 허용**(단조성 보존, ABA-safe. `source:` Herlihy & Wing "Linearizability: A Correctness Condition for Concurrent Objects" **ACM TOPLAS 12(3):463–492, 1990** §5 — Amendment 2 A2-3 정정: 최초 "ACM TOCS 1990" 은 오기, 정확 venue = ACM TOPLAS, dblp `journals/toplas/HerlihyW90` firsthand 확인). slot-level 신규 cron(Issue-level `reservation-cleanup.yml` 과 별개).

### A1-5 — EC-4 amendment_id slot scope = deferred (Q2 결정)

§결정8(b) "EC-4(amendment_id slot)도 동일 OCC primitive 커버 가능(구현=E3b)" 에 대해 **E3b scope = adr_number only, amendment_id deferred**(권장 default). §1 사용자 원문 = ADR-RESERVATION(adr_number) 중심. amendment_id 확장 = ADR-082 Amd17 Wave-2(`amendment-slot-reservation-check` 미존재 verified) 영역 중첩 → ADR-082 Amendment 동반 필요 → follow-up(같은 primitive 재사용, RefactorAgent reusability 축).

## Amendment 2 — 실 발급 flow 배선 확정 + 인용/wording 정정 (CFP-2563, 2026-07-03 KST)

> E3a(설계)·E3b(구현)가 OCC claim primitive·test·stale-reclaim(8 파일)을 완성했으나 **실 ADR 번호 발급 flow 에 미배선**(built-but-unwired / dead-machinery) 이던 상태를 CFP-2563 이 배선 설계로 종결한다. 본 Amendment = ① status Proposed→**Accepted** 승격(실배선 authorize, Story §3 R1 해소) ② 발급 배선 순서·부트스트랩·protection 확정 ③ 최초 발의문의 인용 오기·wording 계보 과대 정정. strengthen direction(약화 surface 0 — 기존 §결정 폐기·역전 0, 배선 실행 + 정정만). **canonical SSOT = Change Plan `wrapper/change-plans/cfp-2563-adr-number-collision-resolution.md`**(internal-docs). 모든 사실 firsthand(`git ls-tree origin/main` / `git show origin/main:<path>`). 추정값 lock-in 0.

### A2-1 — 발급 배선 순서 확정 (§결정 3 실현, R2)

발급 authoritative 번호원 = claim primitive(state-branch OCC). **배선 순서 = claim(번호 직렬화 선행) → 반환 번호로 ADR 파일 write → 기존 inline RESERVATION row append**. 세 단계는 책무 disjoint:

1. **claim** (claim 채널, §결정 3) — `adr-reservation-state` branch 에 OCC PUT 으로 다음 번호 atomic 점유. 이 단계가 lost-update(M2)를 발급 시점에 차단(race window 0).
2. **ADR 파일 write** (audit 채널) — claim 이 반환한 번호로 `archive/adr/ADR-NNN-<slug>.md` 작성.
3. **RESERVATION row append** (audit 채널) — 기존 ArchitectAgent inline append 경로 **무손상**(ADR-070 chief author scope 보존, §결정 3). claim(점유 직렬화) ↔ append(영속 기록)는 disjoint 책무이므로 claim 도입이 inline append 를 강제 우회·차단하지 않는다.

- **template asymmetry 보존(A1-1 정합)**: `templates/adr.md` 의 발급 절차 "`Glob(docs/adr/ADR-*.md)` 후 max+1" 은 **consumer default 로 유지**한다(consumer single_repo ADR = `docs/adr/`). wrapper(dogfood) 발급만 claim primitive 경유로 전환하며, template 은 그 cross-ref(wrapper 는 claim 경유, consumer 는 Glob max+1)만 명시한다. consumer 를 claim 경유로 강제하지 않는다(A1-1 wrapper/consumer 비대칭 원칙 상속).

### A2-2 — state branch 부트스트랩 + protection 6-요건 확정 (§결정 3/5 실현, R3, firsthand)

claim 채널 long-lived branch `adr-reservation-state` 를 다음으로 부트스트랩한다:

- **seed** = `{ "max_adr_number": <부트스트랩 시점 firsthand 최고 ADR 번호>, "claims": [] }`. seed 값은 **하드코딩 금지** — 부트스트랩 실행 시점에 `git ls-tree origin/main archive/adr/ | max(numeric)` 로 재산출한다. `[empirical-source: firsthand git ls-tree origin/main archive/adr]`. **현재(2026-07-03) firsthand max = 141**(`ADR-141-all-opus-single-tier.md` 존재, CFP-2560 merged). Story §4.2 의 "seed max=140" 은 ADR-141 merge 전 값으로 **이미 stale — 140 seed 시 next=141 재발급 collision** 발생하므로 채택 금지(A2 정정).
- **branch protection (mechanical, §결정 5 ABA teeth 확장)**:
  - `allow_force_pushes: false` (A1-3 상속 — counter rewind 차단)
  - `required_linear_history: true` (A1-3 상속 — 단조성 보존)
  - `enforce_admins: true` (admin 우회로 force-push 회피 차단)
  - **`required_pull_request_reviews` 미설정 의무** / **`required_status_checks` 미설정 의무** — claim 은 agent-session 이 Contents API 로 branch 에 **직접 PUT** 하는 채널이다. required-PR-review 를 걸면 direct push 가 `409 "changes must be made through a pull request"` 로 거부되어 **claim 자체가 구조적 deadlock** 에 빠진다. 따라서 이 두 항목은 **설정하지 않는 것이 load-bearing 요건**이다. `[empirical-source: GH006 protected-branch update rejection / GitHub community #39189 — required-PR-review 설정 시 direct push/PUT 거부; CFP-2563 부트스트랩 SMOKE test-PUT = 200 firsthand 실증 — required-PR-review·status-check 미설정 + enforce_admins:true 하에서 agent-session direct PUT 성립(deadlock 회피 확정)]`
- **부트스트랩 검증 = test-PUT smoke(실측 우선)**: 부트스트랩 직후 seed state 에 대해 conditional PUT(현재 sha 동봉)을 1회 실행해 agent-session PAT 가 보호 branch 에 실제로 write 가능한지 실측 확정한다(§7.4 운영 리스크 empirical smoke, 설계리뷰 이관 open item #1). **CFP-2563 Phase 2 부트스트랩 결과 = SMOKE 200(direct PUT 성립) — R3 deadlock-회피 empirically 확정.**

### A2-3 — 인용 정정 (A1-4 venue 오기)

Amendment 1 A1-4 의 `Herlihy & Wing "Linearizability" ACM TOCS 1990` 은 **오기**다. 정확 venue = **ACM TOPLAS 12(3):463–492, July 1990**("Linearizability: A Correctness Condition for Concurrent Objects", dblp `journals/toplas/HerlihyW90` firsthand 확인). A1-4 본문을 정정했다. **잔여 mirror 3곳**(`scripts/lib/adr-reservation-stale-reclaim.py` L15 / `.github/workflows/adr-reservation-stale-reclaim.yml` L9 / `templates/github-workflows/adr-reservation-stale-reclaim.yml` L9)은 코드/워크플로 주석의 동일 오기로, **본 ADR(citation SSOT) 정정을 mirror 하는 Phase 2 mechanical-sync 대상**(Phase 1 = 코드 write 권한 밖). Change Plan §11/§13 declare.

### A2-4 — §결정 1 wording 정정 (계보 과대 → OCC analog)

§결정 1 "산업 정합" 문단의 "`If-Match`/412 의 도메인 특수화" 표현을 **"OCC analog(body-sha + 409)"** 로 정정했다(§결정 1 본문 인용 참조). GitHub body-`sha`→409 와 RFC 9110 `If-Match`(header)→412 는 **검증자 위치·응답 코드가 다른 OCC analog** 이지 동일 메커니즘의 도메인 특수화가 아니다. §7·Change Plan 전반 동일 표기.

### A2-5 — doc-reality gap 3곳 (Phase 2 배선 대상, 설계 명세)

built-but-unwired 를 만든 doc-reality gap 3곳을 배선 대상으로 명시한다(실 배선 코드 = Phase 2):

| # | 위치 | 현 상태(firsthand) | Phase 2 배선 |
|---|------|-------------------|--------------|
| 1 | `docs/orchestrator-playbook.md` L2618 / L2623 | "E3a 가 atomic 격상" / "ADR 번호 append atomic 격상 = E3a" — **허위 서술**(atomic 격상은 배선 완료 시점에 성립, 현재 미배선) | 실상 반영 정정(배선 완료 후 "격상" 성립) |
| 2 | `plugins/codeforge-design/templates/adr.md` L124 | 발급 = "`Glob(docs/adr/...)` max+1"(consumer default), wrapper claim 경유 지시 부재 | wrapper=claim 경유 / consumer=Glob max+1 cross-ref (A2-1) |
| 3 | `plugins/codeforge-design/agents/ArchitectAgent.md` | claim primitive 호출 지시 **0건**(firsthand grep 0) | 발급 시 claim 호출 + claimant identity 주입 절차 |

> ⚠ **`parallel-epic-conflict-check.yml` L61 은 재-scope 금지** — 이미 `^(docs|archive)/adr/ADR-RESERVATION.md$` 통합 regex 로 **정정 완료**(firsthand: `.github` + `templates` 두 copy 모두 origin/main 에서 both-path 매치). Amendment 1 A1-1 의 asymmetric 정정이 실 구현에서 unified regex 로 landing 됨. 본 Story 는 L61 을 건드리지 않는다.

### A2-6 — uniqueness lint = warning tier (facet ③)

file명 ↔ frontmatter `adr_number` ↔ RESERVATION row **3-way** uniqueness lint(#2182 흡수)는 **warning tier** 로 신설한다(사용자 결정 5.5-A). OCC(§결정 2)가 발급-시점 **1차 차단**, lint 는 사후 **2차 안전망**(defense-in-depth). warning tier 이므로 branch protection 고정 6-tuple contexts **무변경**(ADR-060 warning-tier framework 정합). lint 는 **filename 번호 ∧ frontmatter `adr_number` 양쪽을 key** 로 잡고 mismatch 를 flag 한다(firsthand 발견 — filename-only lint 는 frontmatter-collision ADR-045 fm=43 / ADR-062 fm=61 을 누락). 상세 = Change Plan §3.3.

## Amendment 3 — ADR 파일명 digit-width canonical codify + CFP-676 misattribution 정정 (CFP-2762, 2026-07-21 KST)

> ADR corpus 유일 2-digit 파일명 이상치(번호 72)를 3-digit `ADR-072` 로 정합(rename + 전 참조 정규화)하며, 그동안 de-facto(전 corpus 3-digit) + lint(`CANONICAL_PAD_WIDTH=3`) 강제였으나 **SSOT 문장이 결손**이던 digit-width canonical 을 본 ADR(uniqueness lint + `ADR-NNN` write template 소유 host)에 codify 한다. strengthen direction(약화 surface 0). canonical SSOT = Change Plan `wrapper/change-plans/cfp-2762-adr-digit-width-unification.md`(internal-docs). 사실 firsthand.

### A3-1 — digit-width canonical SSOT 문장화

ADR 식별자 표기 규약을 다음으로 명문화한다(그동안 lint/template 이 강제하던 규칙의 SSOT 문장 보완):

- **파일명 = 3-digit zero-pad canonical** — `archive/adr/ADR-NNN-<slug>.md`(N < 100 도 zero-pad, 예 `ADR-072`). 문자열 sort == 숫자 sort 정합 + broken-link(`](ADR-0NN-...)` 링크가 실 파일과 정합) 위험 소거.
- **frontmatter `adr_number` = bare integer** — zero-pad 없는 정수(예 `adr_number: 72`). `normalize_number()`(§A2-6 lint)가 `0*(\d+)` 로 정수 정규화하므로 파일명 3-digit ↔ frontmatter bare int 는 정합(인접 ADR-073 = 파일 `ADR-073-*` ∧ fm `adr_number: 73` 관례 동형).
- **소유 축의 결손 보완(host 정당화)**: 본 규약은 §A2-6 이 소유한 3-way uniqueness lint(`CANONICAL_PAD_WIDTH=3`) + §결정 2/A2-1 이 소유한 `archive/adr/ADR-NNN-<slug>.md`(3-digit) write template 의 **downstream SSOT** 이므로 ADR-133 이 defensible host. 신규 standalone ADR = phantom(규칙이 이미 de-facto+lint 강제). ADR-068 I-4 = identifier wording-sync axis(철자 규율)이지 filename digit-width 정의 축 아님.
- **유일 이상치 정합**: CFP-2762 가 corpus 유일 2-digit 파일명(번호 72, ProductionEvidence Deputy ADR) → 3-digit `ADR-072` rename + 전 참조 word-boundary 정규화. **frontmatter `adr_number: 72` 정수 불변**(rendering-only 정규화 — 번호 72 invariant, §결정 내용/단조성/uniqueness 무영향).

### A3-2 — CFP-676 misattribution 정정 (firsthand 반증)

구 uniqueness lint 주석(`scripts/lib/check-adr-uniqueness-3way.py`)·CFP-2566 잔재의 **'CFP-676 이 2-digit canonical 확정'** 서술은 **firsthand 반증**된다:

- CFP-676 = design-lane agent 구조 재편 Story(모델 tier + mandate SSOT)이며 **자릿수 정책을 담지 않는다**(`git grep CFP-676` corpus 전부 agent-구조 scope).
- 구 2-digit 파일-form 정합의 실제 근거 = (a) **ADR-068 I-4 wording-SSOT**(그 ADR 을 실제 파일 form 으로 인용 — Codex S-CFP676-ADR72-FORM P2 발원) + (b) review-time **pattern_count 경계**(ADR-045 §D-9) — 기계 lint 아님. 별도 `ADR-072-*.md` forbidden 파일 규칙은 **부재**였다.
- 따라서 CFP-2762 = '굳건한 2-digit 정책의 reversal' 이 아니라 **고립 이상치 1건의 정합 방향 선택(3-digit 통일) + 기계 강제**다. renamed `ADR-072` 식별자 단락(구 stance = 'ADR-072 는 본 ADR 식별자 아님')도 본 통일로 정정.

### A3-3 — tier/게이트 무변경

- §A2-6 uniqueness lint = **warning tier 무변경**(branch protection contexts 무영향). 본 Amendment 는 lint 코드 로직 0 변경 — rename 이 zero-pad-drift finding 을 기계 해소, 주석 misattribution 1개 정정만.
- 기존 §결정 1~8 + Amendment 1/2 본문 **0건 변경**(append-only). digit-width 는 신규 §결정 아닌 소유 축 SSOT 보완.

## 변경 이력

- 2026-06-30 KST: 신규 발의 (CFP-2489, Epic CFP-2481 E3a). status Proposed. `Closes #724`.
- 2026-06-30 KST: Amendment 1 (CFP-2491, Epic CFP-2481 E3b). E3b 구현 결정 — dead-gate 비대칭 보정 / claimant identity / branch protection mechanical / Python·별도 artifact / EC-4 deferred. strengthen direction.
- 2026-07-03 KST: Amendment 2 (CFP-2563). status **Proposed→Accepted** 승격(실배선 authorize, R1 해소). 실 발급 flow 배선(A2-1 순서) + state branch 부트스트랩·protection 6-요건(A2-2, seed=firsthand max=141·required-PR-review 미설정 의무) + 인용 정정(A2-3 ACM TOCS→TOPLAS) + §결정1 wording 정정(A2-4 OCC analog) + doc-reality gap 3곳(A2-5) + uniqueness lint warning tier(A2-6). strengthen direction(약화 surface 0).
- 2026-07-21 KST: Amendment 3 (CFP-2762). ADR 파일명 3-digit zero-pad canonical + frontmatter bare int SSOT 문장화(A3-1, 소유 lint/template 축 결손 보완) + 유일 2-digit 이상치(번호 72) → `ADR-072` 정합(frontmatter adr_number:72 정수 불변) + CFP-676 misattribution 정정(A3-2, 실 근거 ADR-068 I-4 wording-SSOT). warning tier·§결정 본문 무변경(A3-3). strengthen direction(약화 surface 0).
