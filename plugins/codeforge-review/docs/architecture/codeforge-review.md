---
title: codeforge-review lane 구조 (설계리뷰 / 구현리뷰 / 보안테스트 — 산출물 검수)
last_captured: 2026-05-18
kind: architecture_doc
family_ref: ../../../plugin-codeforge/docs/architecture/codeforge-family.md#모듈
---

> **목표 invariant (ADR-078 §결정 1 verbatim)**: 코드 직접 read 없이 architecture_doc 1개 read 로 전체 구조 (모듈 + 경계 + 인터페이스 + 데이터 흐름) 파악.

<!-- 본 file = lane plugin self-owned seed (CFP-971 / Sub-Epic CFP-949 Wave 2 / Epic CFP-756 / ADR-078).
     누적 현재 상태 SSOT — Story key 독립, 고정 경로. 델타 = Change Plan SSOT (disjoint, ADR-078 §결정 3).
     family-level structure = family_ref (wrapper repo seed) 참조. 본 doc 은 lane internal 구조만 채운다.
     review lane = 3 lane (DesignReview / CodeReview / SecurityTest) 공유 — PL 이 lane-specific packet 으로 도메인 주입. -->

## 모듈

codeforge-review = **3 review lane (설계리뷰 + 구현리뷰 + 보안테스트) 산출물 검수** 책임 plugin. **5 agent — 3 lane-specific PL + 2 lane-agnostic worker** 구성. PL ↔ worker 패턴 (ADR-001 통합 후) — 워커는 lane-agnostic 단일 model, PL 이 packet 으로 도메인(checklist / scope / category enum / severity override) 주입. `[verified: lane plugin CLAUDE.md @ 5b12053f "Architecture — PL + Worker 패턴" + agents/ tree direct enumeration]`:

| 모듈 (agent) | tier | 책임 |
|---|---|---|
| **DesignReviewPLAgent** | PL (설계리뷰 lane) | 설계 lane 산출물 (Change Plan + ADR + Story §3/§7/§11) 검수 — packet builder + verdict 종합. dedup → severity 종합 → `review_verdict_packet` 구성. **Synthesis only** (Story §9 / GitHub comment / gate label / phase transition 은 Orchestrator monopoly) |
| **CodeReviewPLAgent** | PL (구현리뷰 lane) | Phase 2 PR commit 검수 — 코드 품질 / 테스트 정합 / Change Plan §3-§7 적합성. PL 책임 = synthesis only (동일 패턴) |
| **SecurityTestPLAgent** | PL (보안테스트 lane) | 보안 검증 lane — WebSearch/WebFetch 허용 (security lane 전용) + GitHub native 1차 layer fetch 의무 (worker spawn 전) |
| **ClaudeReviewAgent** | Worker (lane-agnostic) | PL packet 수신 → checklist 항목 수행 → finding return. lane 도메인은 packet 으로 주입 (worker 본문 hard-coded 0건). **Codex 와 필수 peer 병렬** |
| **CodexReviewAgent** | Worker (lane-agnostic) | 동일 packet 수신 → 독립 관점 finding return. ADR-070/081 verify-before-trust + boilerplate 적용. **Claude 와 필수 peer 병렬** |

**공통 base** `templates/review-pl-base.md` = 3 PL 공유 SSOT (severity 종합 / dedup / noise 분류 / 보고 형식 / escalation / FIX Ledger / 워커 의존성). 각 PL md 본문은 lane-specific 4 항목만 (checklist packet · FIX 카운터 정책 · 검증 스코프 · 다음 게이트).

**3 lane checklist** = `templates/review-checklists/{design,code,security}.md` — 각 lane 의 항목 + 자동 P0 룰. PL 이 packet `checklist_path` 로 worker 전달.

> 각 agent prompt / lifecycle 상세 = 해당 `agents/<Name>.md` SSOT. 본 표 = 모듈 단위 책임 enumeration (라인 수준 0건).

## 경계

**Lane self-write boundary** (`[verified: lane plugin CLAUDE.md @ 5b12053f "Architecture — PL + Worker 패턴" + "Drift-avoidance discipline"]` — `codeforge:lane-self-write-boundary` SSOT 정합):

| 경계 영역 | owner |
|---|---|
| review_verdict_packet 구성 (PL synthesis only) | DesignReviewPLAgent / CodeReviewPLAgent / SecurityTestPLAgent (3 PL 각 lane 별) |
| GitHub comment `[설계리뷰]` / `[구현리뷰]` / `[보안테스트]` prefix 발화 | Orchestrator (CFP-61 / ADR-022 — PL packet 받아 최종 write) |
| Story §9 (lane verdict mirror) | Orchestrator (PL packet 수령 후 최종 write, lane plugin self-write 영역 외) |
| `phase:설계-리뷰 → phase:구현` / `phase:구현-리뷰 → phase:보안테스트` / `phase:보안테스트 → phase:완료` transition label | Orchestrator |
| `templates/review-pl-base.md` (공통 SSOT) / `templates/review-checklists/*.md` / `agents/*.md` runtime SSOT | 본 lane plugin maintainer |
| `docs/architecture/codeforge-review.md` (본 doc) | 본 lane plugin maintainer (매 Change Plan merge 시 4 H2 영역 갱신 의무, ADR-078 §결정 1) |

**Drift-avoidance discipline 경계** (lane plugin CLAUDE.md 명시):

- **공통 로직 inlining 금지** — `templates/review-pl-base.md` 의 severity 종합 / dedup / FIX Ledger 로직을 PL md 본문에 다시 인라이닝 금지. 항상 base 템플릿 cross-ref.
- **Worker 호출 규약 invariant** — Packet 누락 시 즉시 `ESCALATE_PACKET_INCOMPLETE` 반환 / 워커 상호 미참조 / 워커 직접 다른 subagent spawn 불가 / WebSearch+WebFetch 는 `lane=security` 만 허용 / security PL 은 worker spawn 전 GitHub native 1차 layer fetch 의무.
- **Claude/Codex 단독 fallback 불허** — 둘 다 필수 peer, 단독 1개로 verdict 작성 금지.

**3-lane 책임 분담 매트릭스** (`codeforge:review-responsibility` skill SSOT 요약):

| Review lane | 검증 영역 |
|---|---|
| DesignReview (DesignReviewPLAgent) | 설계 lane 산출물 문서 감사 — Change Plan §1-§13 완결성 / ADR 정합성 / Story §3/§7/§11 mirror / ADR-065 mechanical self-check / ADR-068 boundary completeness self-check |
| CodeReview (CodeReviewPLAgent) | Phase 2 PR 구현 품질 — 코드 quality / 테스트 정합 / Change Plan §3-§7 implementation 적합성 / style+history disjoint (ADR-081 §결정 D6 3-lane partition) |
| SecurityTest (SecurityTestPLAgent) | 보안 검증 — 위협 모델 적용 / 외부 입력 검증 / 권한 위임 review / secret 노출 / `live-secret-policy.yml` 정합 |
| DesignLane (codeforge-design, 본 lane 외) | 설계 결정 자체 (review lane 영역 외) — 중복 지적 시 ReviewPL dedup → severity 높은 쪽 채택 |

**Cross-cutting gate boundary**:

- **Codex Proactive Check Touchpoint #2** (ADR-052 Amendment 4) — ArchitectAgent §3 직후 mandatory. 본 lane 직접 발동 아님 (Orchestrator dispatch) 이지만 worker 산출물 = 후행 review lane 검수 input 영향.
- **`debate-protocol-v1` divergence trigger** — DesignReviewPLAgent 가 동일 `anchor_id` 에 대해 worker 간 severity / verdict 발산 감지 시 multi-round adversarial debate 자동 발동 (host 책임). ADR-059 Amendment 2 Wave 4 blanket trigger (`blanket_cross_module_designlane`) 도 본 PL 이 호스팅.
- **`hotfix-bypass:*` exception channel** — 본 lane verdict 가 evidence-check warning tier 우회 라벨 적용 시 audit-trailed exception 인지 검증 (ADR-024 Amendment 3).

**Disjoint scope** (ADR-078 §결정 3):

- 본 doc = lane internal 누적 현재 상태, Story key 독립
- review_verdict_packet = Story별 verdict 산출 (Story key 종속, 1회/lane)
- ADR = 단일 결정 단위, 불변
- 본 doc ↔ review_verdict_packet = 상보 disjoint (구조 vs 산출)

**Scope partition**:

- dogfood artifacts (specs/plans/retros/stories/change-plans) = `mclayer/codeforge-internal-docs/codeforge-review/**` monorepo SSOT (ADR-013, lane plugin CLAUDE.md "Dogfood policy").
- 본 plugin repo = runtime SSOT 만 (agents/* + templates/* + 2 shell hook + `docs/inter-plugin-contracts/review-verdict-v4.md` canonical).

## 인터페이스 계약

lane 간 + lane 내부 계약 surface — kind:contract producer / kind:registry host / governance ADR anchor. 계약 schema field-level / version literal 미박제 (`MANIFEST.yaml` SSOT 가 권위, drift 회피).

**Producer (kind:contract)** — 본 lane 이 생성:

| contract | role | SSOT pointer |
|---|---|---|
| `review_verdict` | 3 PL (Design/Code/SecurityTest) → Orchestrator 핸드오프 packet — `pl_recommendation` enum (PASS / FIX / FIX_DISCRETIONARY / ESCALATE_PACKET_INCOMPLETE) + `findings[]` (severity + type + anchor_id) + 4 boolean self-check carrier field (mechanical / boundary / dimensional / marketplace_sync_declared) | `docs/inter-plugin-contracts/review-verdict-v4.md` (canonical = 본 plugin repo) + wrapper sibling sync mirror (ADR-010) |

**Host (kind:registry — sibling sync 면제, ADR-010 §결정 2)** — 본 lane 이 발동 / 참여:

| registry | 본 lane 역할 |
|---|---|
| `debate-protocol-v1` | DesignReviewPLAgent = divergence_detected 시 multi-round adversarial debate host. 4-value `dispatch_mode` 우선순위 `auto_on_divergence > blanket_cross_module_designlane > mechanical_fast_path_inline > user_request_only`. min 3 / soft 4 / max 5 round. anti-sycophancy invariant (POSITION_CHANGE marker + role_lock + `remaining_disagreements` 매 라운드 출력). transcript → Story §9 append → §10 FIX Ledger `debate_artifact_ref` carry |
| `parallel-dispatch-protocol-v1` | 3 PL = 2 worker (Claude + Codex) **parallel spawn** 계약. peer-필수 invariant (단독 fallback 0). sequential 강제 사유 3종 부재 — default parallel (ADR-064 Trace 4) |
| `severity-propagation-v1` | review-verdict-v4 `findings[].severity` ↔ label-registry-v2 `severity:*` ↔ evidence-checks-registry `current_tier` 3-way bidirectional binding consumer + producer (PL 가 finding severity 결정 → label / tier propagate trigger) |

**Consumer (kind:contract)** — 본 lane 이 수신:

| contract | producer plugin | 용도 |
|---|---|---|
| `design_output` | codeforge-design | DesignReviewPLAgent input — Change Plan + ADR + Story §3/§7/§11 mirror 검수 |
| `develop_output` | codeforge-develop | CodeReviewPLAgent input — Phase 2 PR commit + Story §8/§8.5 검수 |

**Governance ADR anchor**:

- **ADR-001** (Review/Test 워커 에이전트 통합) — 3 lane × 2 vendor → 2 lane-agnostic worker. PL packet 으로 도메인 분리 + worker model 단일화 base anchor.
- **ADR-052** (Codex Proactive Check 6 touchpoint) — Touchpoint #2 mandatory dispatch (CFP-532 Amendment 4) / Touchpoint #4 multi-round adversarial debate (RequirementsPL § 영역 자체 redo). 본 lane = downstream 의 worker 산출물 검수 책임 + Codex calibration evidence 누적 (`codex_fp_tally` Story §10 prose marker).
- **ADR-059** (debate-protocol-v1) — host 책임 anchor. v1.2 = blanket_cross_module_designlane (Wave 4 cross-module Story 자동 활성) + `convergence_quality_invariant` 3 marker AND (counterargument_present / alternative_proposed / debate_purpose_statement_present).
- **ADR-068** (boundary completeness invariants, semantic) — DesignReviewPL + CodeReviewPL **dual-binding cross-validate** anchor. I-1 API contract semantic / I-2 cross-module propagation / I-3 guard placement intent / I-4 wording SSOT / I-5 dimensional empirical grounding 5 invariants self-check 결과 review-verdict-v4 carrier field (`boundary_completeness_self_check_passed` / `dimensional_empirical_self_check_passed`) verify.
- **ADR-070** (Codex verify-before-trust, 4-layer governance Layer 2) — CodexReviewAgent output ground truth 를 Orchestrator direct file Read 로 verify, mismatch 시 verdict reject + Story §10 false positive count tally + override rationale 명시.
- **ADR-081** (Codex worker prompt boilerplate) — CodexReviewAgent spawn prompt 본문 3 mandatory section (dogfood-out Story path / lane stage / sandbox boundary) + verify-before-trust scope 5 sub-scope + 3-lane partition (Codex factual citation / DesignReview boundary completeness / CodeReview style+history disjoint). severity calibration (D6) bidirectional binding evidence.
- **DesignReviewPL §8.6 audit gate** (ADR-014 Amendment 4 §결정 2): IntegrationTest contract pointer 존재 mechanical check only. policy 값 공백 PASS invariant. 상세는 `templates/review-pl-base.md` §8.6 + `templates/review-checklists/design.md` 분담 표. carrier = CFP-698 (Epic CFP-1026 W2 S4).

> 본 섹션 = surface enumeration (계약 이름 + SSOT pointer, 라인 수준 0건). 계약 schema field-level 상세 + version 값 = 각 contract file + MANIFEST.yaml SSOT (drift 회피 위해 본 doc version literal 미박제).

## 데이터 흐름

**3-lane review spawn flow** (Orchestrator 가 각 review lane 진입 시 해당 lane plugin PL 1개 spawn — non-skippable):

```
[upstream] design_output 수신 (codeforge-design → DesignReview lane)
  ↓
Orchestrator → DesignReviewPLAgent spawn (lane PL, one-shot per attempt)
  │
  ├─ packet 구성 (checklist_path = templates/review-checklists/design.md + scope + category enum)
  │
  ├─ 한 메시지에 2 worker 병렬 dispatch (parallel-dispatch-protocol-v1):
  │     ├─ ClaudeReviewAgent (input: packet + design artifact)  → finding[]
  │     └─ CodexReviewAgent  (input: packet + design artifact)  → finding[] (+ verify-before-trust 5 sub-scope ground truth annotation)
  │
  ├─ 2 worker return (one-shot, stateless) — 독립 관점 finding[] PL 에 input
  │
  ├─ PL synthesis: dedup (anchor_id collapse) → severity 높은 쪽 채택 → noise 분류 → review_verdict_packet 초안
  │
  ├─ divergence_detected check (동일 anchor_id 에 severity / FIX vs PASS 발산)
  │     │
  │     ├─ no divergence → review_verdict_packet emit
  │     │
  │     └─ divergence detected → debate-protocol-v1 발동 (host = DesignReviewPL)
  │           ├─ min 3 / soft 4 / max 5 round adversarial debate
  │           ├─ anti-sycophancy invariant (POSITION_CHANGE / role_lock / remaining_disagreements)
  │           ├─ blanket_cross_module_designlane (touched_top_level_paths ≥ 2 OR touched_lanes ≥ 2) 시 자동 활성
  │           ├─ convergence_quality_invariant 3 marker AND verify (counterargument / alternative / debate_purpose)
  │           ├─ consensus → review_verdict_packet emit + transcript → Story §9 append
  │           └─ max round 미합의 → AskUserQuestion escalation
  │
  ├─ Codex verify-before-trust (ADR-070) — Codex finding ground truth Orchestrator direct verify
  │     ├─ verified ✓ → finding 보존
  │     └─ mismatch → finding reject + Story §10 false positive tally + override rationale
  │
  └─ review_verdict_packet (pl_recommendation enum + findings + 4 boolean self-check carrier) emit
        │
        ▼
Orchestrator 수령 → Story §9 final verdict + GitHub comment `[설계리뷰]` + `phase:설계-리뷰 → phase:구현` label transition
  │
  ├─ pl_recommendation: PASS → 다음 lane (codeforge-develop) 핸드오프
  ├─ pl_recommendation: FIX → §10 FIX Ledger row append (fix-event-v1 monopoly) → ArchitectPLAgent re-spawn
  ├─ pl_recommendation: FIX_DISCRETIONARY → 사용자 판단 trigger
  └─ pl_recommendation: ESCALATE_PACKET_INCOMPLETE → 상위 lane 재spawn
```

**CodeReview lane / SecurityTest lane** — 동일 패턴 (PL + 2 worker parallel + verdict synthesis) 이지만 lane-specific 차이:

- **CodeReview**: input = `develop_output` (Phase 2 PR + Story §8/§8.5) / checklist = `templates/review-checklists/code.md` / `style+history disjoint` invariant (ADR-081 §결정 D6 3-lane partition) / output label transition = `phase:구현-리뷰 → phase:보안테스트`
- **SecurityTest**: input = Phase 2 PR + security-relevant artifact / checklist = `templates/review-checklists/security.md` / WebSearch+WebFetch 허용 (security lane 전용) / GitHub native 1차 layer fetch 의무 (worker spawn 전) / output label transition = `phase:보안테스트 → phase:완료`

**FIX 루프 데이터 흐름** (max FIX 3/3, ADR-067):

- review_verdict `pl_recommendation: FIX` → Orchestrator §10 FIX Ledger row append → 원인 lane re-spawn (DesignReview FIX = ArchitectPL / CodeReview FIX = DeveloperPL 1차 진단 + ArchitectPL 최종 판정 / SecurityTest FIX = 동일 패턴)
- debate-protocol-v1 발동 시 transcript = Story §9 append → §10 FIX Ledger `debate_artifact_ref` carry → 원인 lane re-spawn 시 verbatim 입력 (reasoning carryover 보장)
- max 3 도달 시 = ArchitectPL implementability reassessment (ADR-067 §결정 3) — RESET / escalate / Pause 분기

**artifact propagation**:

- Story file (`internal-docs/codeforge-review/stories/<KEY>.md`) = lane 컨텍스트 SSOT (PL self-fetch, lane plugin self-write 영역 없음 — Story §9 final verdict 는 Orchestrator monopoly write)
- review_verdict_packet (transient artifact, in-memory) = Orchestrator 가 packet 수령 후 Story §9 final write + GitHub comment + label transition
- debate transcript = Story §9 append (Orchestrator write, lane plugin agent read-only)
- 본 doc (architecture_doc) = 누적 현재 상태 (영속, Story key 독립) — 매 Change Plan merge 시 4 H2 영역 갱신 의무 (ADR-078 §결정 1)

> 본 흐름 = lane spawn / event / artifact propagation 수준. 함수 호출 trace / 변수 전달 라인 0건 (anti-scope guard 준수).

---

### ADR-076 declarative reconciliation 3-layer cross-ref

본 lane 의 architecture_doc 운용은 [ADR-076](../../../plugin-codeforge/docs/adr/ADR-076-declarative-reconciliation-upgrade.md) declarative reconciliation 3-layer 패턴을 도메인 disjoint 로 답습 (ADR-078 §결정 2 명시):

- **desired state** = 본 doc 의 4 H2 closed-enum (모듈 + 경계 + 인터페이스 계약 + 데이터 흐름) 누적 현재 상태 SSOT
- **current state** = lane plugin agent file (`agents/{DesignReviewPLAgent,CodeReviewPLAgent,SecurityTestPLAgent,ClaudeReviewAgent,CodexReviewAgent}.md`) + `templates/review-pl-base.md` 공통 + `templates/review-checklists/*.md` + `CLAUDE.md` (runtime 실제 동작)
- **converge** = ArchitectAgent self-write 확장 (Sub-Epic CFP-949 S3 carrier `mclayer/plugin-codeforge-design` — 구 lane repo, 현 `plugins/codeforge-design/`, repo 삭제됨 2026-06-12 — ADR-082 §결정 1 mechanism) + design lane verdict gate (drift lint CFP-923 detection class d, Wave 4 carrier)

> 본 cross-ref = 패턴 답습. 도메인 (upgrade flow ↔ review lane) 은 disjoint. wording SSOT = ADR-076 본문 + ADR-078 §결정 2.

---

### anti-scope guard (ADR-078 §결정 1 verbatim — 작성자 필독)

본 doc 은 **구조 수준 only**. closed-enum 4 영역 외 다음 4종 패턴은 **금지** (라인 수준 허용 시 갱신 즉시 stale + "코드에 한 단계 더한 것" 전락 — Epic §위험신호 §1):

1. **클래스 / 함수 / 변수 라인 단위 열거** — 클래스 list, 변수 enumeration 금지.
2. **의존성 import graph 라인-level** — import 관계 라인 단위 그래프 금지.
3. **함수 signature / parameter list / return type** — API 의 line-level 시그니처 금지.
4. **코드 mirror** — `agents/` · `templates/` 구조를 1:1 복사한 디렉터리 트리 dump 금지.

→ 위 4종이 필요하면 그것은 코드 / Change Plan / ADR 영역. architecture_doc 은 "코드 read 없이 구조 파악" 목표만 만족하면 된다.
