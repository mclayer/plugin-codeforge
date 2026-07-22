---
kind: domain_fact
type: domain-knowledge
area: governance-principle
topic_slug: semantics-change-sentinel
title: Semantics-change sentinel — carrier-surface-meaning-shift-during-in-flight-work pattern + recall-first honest ceiling (CFP-2786 / Epic #2783 Child B)
status: Active
date: 2026-07-22
updated: 2026-07-22
carrier_story: CFP-2786
owner_adr: ADR-085
tags:
  - semantics-change
  - carrier-surface
  - meaning-shift-during-in-flight-work
  - sentinel-pattern
  - recall-first
  - honest-ceiling
  - advisory
related_adrs:
  - ADR-085       # owner_adr — Multi-session collaboration protocol (carrier surface narrative anchor)
  - ADR-060       # carrier_adr — Evidence-enforceable promotion framework (registry entry carrier)
  - ADR-090       # cross-layer impact + TIME-axis disjoint (intra-PR vs cross-PR-temporal)
  - ADR-119       # research-before-claims — presence != truth honest ceiling
  - ADR-151       # honesty ceiling — 안전성 claim 정직(수치 SLA 미강제)
  - ADR-005       # byte-identical workflow parity (template <-> .github pair)
  - ADR-061       # thin wrapper convention (bash dispatch -> Python SSOT)
related_stories:
  - CFP-2786      # 본 codify carrier (Epic #2783 Child B)
  - CFP-2784      # 형제 위상축 sentinel (rebase staleness, FU-1588-R) — disjoint 대칭 companion
is_transitional: false
sunset_criteria: |
  N/A — permanent governance sentinel. 본 sentinel = governance/policy carrier surface 의 의미가
  in-flight 작업 중 바뀔 때 발생하는 inherent race window 영역 SSOT. multi-session distributed
  work 환경(위상축 sentinel 과 동일 환경)이 사라지지 않는 한 sunset 영역 외.
---

# Semantics-change sentinel — carrier-surface-meaning-shift-during-in-flight-work pattern

본 file = codeforge governance corpus 의 **`carrier-surface-meaning-shift-during-in-flight-work`** sentinel pattern SSOT. 형제 위상축 sentinel(`rebase-staleness-sentinel.md`, CFP-2784)과 **대칭 companion** 이며, 두 sentinel 은 4-way disjoint(subject / surface / primitive / trigger-origin)로 완전히 분리된다.

## 정의

### 의미축 vs 위상축 — "위상 fresh != 의미 fresh"

위상축 sentinel 은 "내 브랜치가 main 대비 몇 커밋 뒤처졌나"(commit-count-behind)를 측정한다. 그런데 뒤처진 커밋 수가 0이어도(위상 fresh) 내가 의존하던 governance 규칙의 **뜻**이 바뀌었을 수 있다(의미 stale). 의미축 sentinel 은 반대 질문을 던진다:

> **"뒤처진 커밋이 내가 의존하던 규칙의 뜻을 바꿨나?"**

이는 자연어 처리의 **Word Sense Disambiguation(WSD, 단어 의미 중의성 해소)** 과 동형이다 — 같은 토큰(예: 어떤 ADR 참조, 어떤 계약 이름)이 시점에 따라 다른 의미를 가리킬 수 있고, 표면 문자열이 같다고 해서 지시 대상(referent)이 같다는 보장이 없다. 의미축 sentinel 은 governance carrier surface 를 건드린 변경(carrier touch)을 1차 필터로 표면화하고, 그 carrier 를 참조하는 in-flight 작업이 있으면 "재검토 필요" 신호를 낸다.

### 단일 신호 — tier 카탈로그 없음

의미축은 **"재검토 필요" 단일 advisory 신호**만 방출한다. 위상축의 4-tier mitigation(auto-merge / pre-emptive rebase / wait+retry / handoff)과 달리, 의미 변경은 "다음에 무엇을 하라"를 기계가 처방할 수 없다 — 실제 의미가 바뀌었는지, 바뀌었다면 하류 작업을 어떻게 조정할지는 사람의 2차 판정 몫이다. 따라서 tier 카탈로그(등급 매핑)는 존재하지 않는다.

- **anchor_overlap** — carrier 가 참조하는 ADR/Story anchor 와 in-flight 작업이 참조하는 anchor 의 교집합 (primary recall signal).
- **path_overlap** — carrier touched 경로와 in-flight 작업이 언급한 경로의 교집합 (recall floor).
- **lane_overlap** — carrier 가 건드린 lane/plugin 과 in-flight 작업이 참조한 lane 의 교집합 (recall floor).

세 신호를 각각 **분리 관측한 뒤 top-level OR**(SEPARATE-OR-top)로 합쳐 "재검토 필요" 여부를 정한다. 세 신호 중 하나라도 겹치면 candidate 로 표면화한다.

### honest ceiling — presence != truth (선언)

carrier touch = **candidate surface** 이지 verdict 가 아니다. touch != 의미변경. carrier 파일이 바뀌었다는 사실은 "의미가 바뀌었을 수도 있다"는 후보 신호일 뿐, 실제로 규칙의 뜻이 바뀌었는지(current_tier flip / §결정 신설 / required-context 증감 등 2차 diff-content 판정)는 사람이 판단한다. "모든 의미 의존을 검출한다"는 hard-claim 은 금지한다 — 의미 의존은 undecidable 이며, 본 게이트는 완전 검출을 단정하지 않는다(ADR-119 / ADR-151 상속).

## 컨텍스트

### 왜 carrier-surface 를 live 로 파생하는가

carrier surface(어떤 파일이 governance 의미를 담는가)를 하드코딩 list 로 박으면, governance 자산이 늘어날 때마다 sentinel 이 stale drift 부채를 진다. 그래서 본 sentinel 은 surface 를 **live SSOT 파일에서 파생**한다 — 이미 존재하는 registry/registry-like 자산이 진실의 원천이고, sentinel 은 그것을 읽어 후보 표면을 구성한다.

### 형제 위상축과의 관계

위상축(CFP-2784)과 의미축(CFP-2786)은 같은 multi-session distributed work 환경(복수 Orchestrator 세션 + worktree-first isolated workspace + Story-scoped feature branch)에서 발생하지만, **관측 대상이 disjoint** 하다. 위상축은 "몇 커밋 뒤처졌나"(count, 위상)를, 의미축은 "뒤처진 것이 규칙 뜻을 바꿨나"(referent, 의미)를 본다. 두 sentinel 은 코드 재사용(구조 복제)은 하되 서로를 import 하지 않는다(독립 재구현).

## 핵심 규칙

### 규칙 1 — carrier-surface derivation (Q2 live SSOT, 하드코딩 list 0)

carrier surface = `(kind, value)` 후보 표면(kind ∈ {exact, prefix, glob}). 아래 3원천에서 live 파생하며, 파싱 실패 시 gap 을 정직하게 기록한다:

| 원천 | 파생 규칙 | drift 회피 |
|---|---|---|
| `docs/doc-locations.yaml` | dogfood adr path(`archive/adr/`) prefix 추출 | 파싱 실패 시 fallback prefix + gap note |
| `docs/evidence-checks-registry.yaml` | 각 `workflow:` 값 → exact anchor + registry 파일 자체 exact(current_tier flip = 의미변경) | live 파생 — registry 자산 증가 자동 추종 |
| structural governance anchors | `CLAUDE.md` / `plugins/*/CLAUDE.md` / `docs/inter-plugin-contracts/` / `templates/` / `docs/domain-knowledge/domain/governance-principle/` / `docs/wording-dictionary.md` / `docs/security/branch-protection-audit.md` / `docs/doc-locations.yaml` | frozen policy-enum 아님 — 디렉토리 존재 자체가 live signal |

2차 diff-content discriminant(current_tier flip / §결정 신설 / required-context 증감)은 사람 몫이며, sentinel 은 1차 후보 표면화까지만 한다.

### 규칙 2 — carrier touch != 의미변경 (2차 판정 = 사람)

carrier touch 는 후보 필터일 뿐이다. sentinel 이 "matched" 로 표면화한 candidate 라도, 실제 의미가 바뀌었는지는 하류 사람 게이트가 판정한다. 이 규율은 hard-claim 금지(honest ceiling)의 실행 형태다.

### 규칙 3 — born-broken 계약 (mechanical wire 배선 3점)

본 sentinel 의 mechanical wire 는 born-broken(태생 결함) 회피를 위해 아래 3점을 동반 배선한다:

1. **discriminating self-test** — mutation 생존 0. cross-match 의 OR→AND 변이(M3a), narrowing 제거→all-in-flight 변이(M3b) 등이 self-test 에서 잡혀야 한다.
2. **hard-fail workflow job** — self-test 를 warning-tier gate workflow 안에 배선(RED swallowed)하지 않고, `continue-on-error` 부재의 별 hard-fail job(`semantic-staleness-detection-test`)으로 분리(RED = exit 1 차단).
3. **bijection** — Python SSOT + thin wrapper(ADR-061) + byte-identical workflow pair(ADR-005 template <-> .github) + self-test + registry entry 가 1:1 대응(누락 0).

### 규칙 4 — recall-first honest ceiling (수치 SLA 부재)

의미축은 **recall >> precision** 방향이다. 근거:

- **비용 비대칭**: 의미 변경을 놓쳐(false-negative) 하류 작업이 stale 규칙 위에 지어지는 비용 >> 무관 후보를 표면화(false-positive)해 사람이 1초 확인하는 비용.
- **하류 사람 게이트**: candidate 는 사람에게 향하는 advisory 이지 자동 차단이 아니므로, over-surfacing 의 실 피해가 작다.
- **presence != truth**: 완전 검출을 단정하지 않으므로, precision 을 높이려 recall 을 깎는 방향은 금지된다.

따라서 recall/precision 회귀 **수치 SLA 는 부재**(invariant-only, INV-RECALL-FIRST 방향). "모든 의미 의존을 잡는다"는 주장은 undecidable 이므로 금지한다.

## 경계

### disjoint 4-way (위상축 sentinel 과의 분리 계약)

| 축 | 위상축(CFP-2784) | 의미축(CFP-2786) |
|---|---|---|
| **subject** | 몇 커밋 뒤처졌나(count) | 뒤처진 것이 규칙 뜻을 바꿨나(referent) |
| **surface** | commit graph(HEAD..origin/main) | governance carrier surface(ADR/계약/template 등) |
| **primitive** | rev-list count | carrier touch classify + anchor/path/lane cross-match |
| **trigger-origin** | 위상 stale(뒤처짐) | 의미 stale(뜻 변경) |

### ADR-090 TIME-axis disjoint

ADR-090 cross-layer impact 축은 **intra-PR**(한 PR 안 layer 간 영향)을 본다. 본 sentinel 은 **cross-PR-temporal**(다른 in-flight PR 이 시점에 걸쳐 참조하는 carrier 의 의미)을 본다 — 시간 축이 다르다. 두 축은 어휘·관측 대상이 겹치지 않는다.

### vocabulary-disjoint 3 structural contract

의미축 sentinel 은 위상축·cross-layer 어휘를 방출하지 않는다(structural contract):

1. tier 어휘(`recommended_tier`, `tier1`/`tier2` value, tier 등급 카탈로그) 미출현 — 의미축은 단일 신호.
2. count 어휘(commit-count-behind 류) 미출현 — 의미축은 referent overlap 관측.
3. cross-layer 어휘(`TOUCHED_SCHEMA` / `touched_frontend` / `touched_backend` 류) 미출현 — 의미축은 anchor/path/lane overlap.

### Scope out (본 sentinel 영역 외)

- **2차 의미 판정** — 실제로 규칙 뜻이 바뀌었는지(diff-content 판정)는 사람 몫(honest ceiling).
- **자동 조정/수정** — candidate 표면화만, 어떤 mutation 도 스스로 실행하지 않음(read-only).
- **위상축 관측** — commit-count-behind 는 형제 sentinel(CFP-2784) 소관.
- **single-session sequential 환경** — race window inherent 아님(multi-session 환경 전제).

## 관련 ADR

- **ADR-085** (Multi-session collaboration protocol) — owner_adr. governance carrier surface 가 세션 간 공유되는 협업 축의 narrative anchor. 본 sentinel = 그 축의 의미-stale race window instance.
- **ADR-060** (Evidence-enforceable promotion framework) — carrier_adr. registry entry(`semantics-change-sentinel`) mechanical wire 의 framework host.
- **ADR-090** (Cross-layer impact / dependency-order) — TIME-axis disjoint 근거(intra-PR vs cross-PR-temporal).
- **ADR-119** (research-before-claims) — presence != truth honest ceiling 상속. carrier touch = candidate 이지 verdict 아님.
- **ADR-151** (honesty ceiling) — 안전성/완전성 claim 정직. 수치 SLA 미강제, undecidable 완전검출 hard-claim 금지.
- **ADR-005** (byte-identical self-application) — template <-> .github workflow pair byte-parity.
- **ADR-061** (thin wrapper convention) — bash dispatch -> Python SSOT 배선.

## 변경 이력

| 일자 (KST) | 변경 | Carrier | 비고 |
|---|---|---|---|
| 2026-07-22 | 신설 (semantics-change sentinel SSOT — 의미축 정의 + carrier-surface live 파생 + disjoint 4-way/TIME-axis/vocabulary-disjoint 3 + 단일 신호(tier 카탈로그 없음) + born-broken 계약 3점 + recall-first honest ceiling) + mechanical wire(Python SSOT + thin wrapper + byte-identical workflow pair + discriminating self-test) | CFP-2786 | Epic #2783 Child B. 형제 위상축 sentinel(CFP-2784, rebase-staleness-sentinel.md)의 대칭 companion (4-way disjoint, import 0 독립 재구현). warning-tier 비차단. |
