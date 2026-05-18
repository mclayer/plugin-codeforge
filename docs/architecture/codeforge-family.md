---
title: codeforge family 전체 구조 (wrapper + 6 lane plugin)
last_captured: 2026-05-18
kind: architecture_doc
---

> **목표 invariant (ADR-078 §결정 1 verbatim)**: 코드 직접 read 없이 architecture_doc 1개 read 로 전체 구조 (모듈 + 경계 + 인터페이스 + 데이터 흐름) 파악.

<!-- 본 file = wrapper repo 1회 seed (CFP-920 / Epic B Story-2). 누적 현재 상태 SSOT.
     6 lane plugin self-owned architecture_doc 는 Epic 후속 별 CFP (Q-SEED-1 derived default). -->

## 모듈

codeforge = Claude Code 범용 SW 개발 오케스트레이션 플러그인 family. **wrapper (codeforge) = 0 core agent** (wrapper-only, ADR-009 ζ arc) — Orchestrator (top-level Claude 세션) 가 6 lane plugin 의 agent 를 spawn.

`[verified: CLAUDE.md @ 126fa6ab Development Agent Team table — agent counts cross-checked]` — 6 lane plugin + agent composition:

| 모듈 (plugin) | 책임 | agent 구성 |
|---|---|---|
| **codeforge** (wrapper) | family identity + cross-cutting policy SSOT + skill pointer. agent 0개 (Orchestrator 가 lane plugin agent spawn) | 0 (wrapper-only) |
| **codeforge-requirements** | 요구사항 레인 — 사용자 요구 접수 → 통합 요구사항 명세 | 7 (PL + DomainAgent + RequirementsAnalyst + Researcher + ChangeImpactAgent + FeasibilityAgent + ContinuityAgent) |
| **codeforge-design** | 설계 레인 — Change Plan + ADR 확정 | 8 (PL + ArchitectAgent chief + 6 SubAgent) |
| **codeforge-review** | 설계리뷰 / 구현리뷰 / 보안테스트 레인 — 산출물 검수 | 5 (3 PL + 2 worker) |
| **codeforge-develop** | 구현 레인 — TDD 구현 + QA | 5 (PL + QADev + 3 role:dev core) + preset/overlay 동적 |
| **codeforge-test** | 통합테스트 레인 — Epic-level 통합 검증 | 1 (IntegrationTestAgent) |
| **codeforge-pmo** | Cross-cutting — Epic 창설 / Story 회고 / Git ops | 3 (PMOAgent + GitOpsAgent + DialogFidelityAgent) |

> 각 lane plugin agent 역할·동작 = 해당 plugin CLAUDE.md SSOT. 본 표 = composition map (모듈 단위, 라인 수준 0건).

## 경계

**Lane self-write boundary** (각 모듈이 직접 갱신하는 Story file 섹션 — `codeforge:lane-self-write-boundary` SSOT 요약):

| 모듈 | self-write 영역 |
|---|---|
| codeforge-requirements | Story §2 · §5 · §6 |
| codeforge-design | Story §3 · §7 · §11 + `docs/change-plans/**` + `docs/adr/**` |
| codeforge-develop | Story §8 · §8.5 + Phase 2 PR |
| codeforge-pmo | Story §11(retro 영역) + `docs/retros/**` |
| Orchestrator | Story §9 (final verdict) · §10 (FIX Ledger, fix-event-v1 monopoly) · §14 (Lane Evidence) · phase 전환 label |

**owner agent direct write** (CFP-26 Phase 0a): `docs/{change-plans,adr,domain-knowledge,retros,architecture}/**` = owner agent 직접 write (Orchestrator monopoly 영역과 disjoint).

**scope partition**: dogfood artifacts (specs/plans/retros/stories/change-plans) = `mclayer/codeforge-internal-docs` monorepo SSOT (ADR-013). wrapper repo = policy/template/script SSOT. consumer overlay (`.claude/_overlay/`) = 정책 확장만 가능 (축소 불가).

## 인터페이스 계약

모듈 간 계약 surface = `docs/inter-plugin-contracts/` (canonical = producer plugin repo, wrapper = sibling sync mirror — ADR-010). `[verified: MANIFEST.yaml @ 126fa6ab]`:

**kind:contract (7)** — lane 간 산출물 핸드오프 surface:

| contract | producer plugin | 용도 |
|---|---|---|
| review_verdict | codeforge-review | 리뷰 verdict packet (pl_recommendation) |
| requirements_output | codeforge-requirements | 요구사항 synthesis |
| design_output | codeforge-design | 설계 산출물 |
| develop_output | codeforge-develop | 구현 산출물 |
| test_verdict | codeforge-test | 통합테스트 verdict |
| pmo_output | codeforge-pmo | Epic/retro 산출물 |
| git_ops_event | codeforge-pmo | GitOpsAgent 이벤트 |

**kind:registry (sibling sync 면제 — ADR-010 §결정 2)**: label-registry-v2 / debate-protocol-v1 / evidence-check-registry-v1 / severity-propagation-v1 / parallel-dispatch-protocol-v1 / defense-in-depth-sublayer-registry-v1 / reconcile-protocol-v1 + chain-managed (comment-prefix-registry / fix-event-v1).

> 계약 schema field-level 상세 = 각 contract file SSOT + `MANIFEST.yaml`. 본 섹션 = surface enumeration (계약 이름 + SSOT pointer, 라인 수준 0건). version 값은 MANIFEST.yaml SSOT 가 권위 (본 doc 누적 현재 상태 — version drift 회피 위해 본 섹션 version literal 미박제).

## 데이터 흐름

**Story lane spawn flow** (Orchestrator 가 lane 진입 시 해당 lane plugin PL 1개 spawn — non-skippable):

```
사용자 요구 접수
  → 요구사항 lane (codeforge-requirements:RequirementsPLAgent) → Story §1-§6 synthesis
  → 설계 lane (codeforge-design:ArchitectPLAgent) → Change Plan + ADR + Story §7/§11
  → 설계리뷰 lane (codeforge-review:DesignReviewPLAgent) → review_verdict
  → 구현 lane (codeforge-develop:DeveloperPLAgent) → Phase 2 PR
  → 구현리뷰 lane (codeforge-review:CodeReviewPLAgent) → review_verdict
  → CI gate (phase-gate-mergeable) → merge
  → [Epic 종료 시] 통합테스트 lane (codeforge-test:IntegrationTestAgent) → test_verdict
```

**Cross-cutting 흐름** (Story lane 게이트 비개입, 독립 spawn):
- PMOAgent — Epic 창설 / Story 완료 retro (Phase 2 PR merge 후 5분 grace 자동 trigger, ADR-045)
- GitOpsAgent — parallel epic conflict 검사 + scope_manifest intersection
- DialogFidelityAgent — Orchestrator ↔ 사용자 dialog 3-anchor read-only verify

**artifact propagation**:
- Story file (`internal-docs/wrapper/stories/<KEY>.md`) = lane 간 컨텍스트 SSOT (각 lane self-fetch)
- Change Plan (`docs/change-plans/<slug>.md`) = Story별 변경 델타 (1회, Story key 종속)
- architecture_doc (`docs/architecture/`) = 누적 현재 상태 (영속, Story key 독립) — Change Plan 과 disjoint 상보 (ADR-078 §결정 3)
- ADR (`docs/adr/`) = 단일 결정 단위 (불변)
- EPIC-RESULTS (`internal-docs/<plugin>/retros/`) = Epic close 1회 evidence aggregate

> 본 흐름 = lane spawn / event / artifact propagation 수준. 함수 호출 trace / 변수 전달 라인 0건 (anti-scope guard 준수).

---

### anti-scope guard (ADR-078 §결정 1 verbatim — 작성자 필독)

본 doc 은 **구조 수준 only**. 4종 패턴 금지: (1) 클래스/함수/변수 라인 단위 열거 (2) import graph 라인-level (3) 함수 signature/parameter/return type (4) src/ 1:1 디렉터리 dump. 라인 수준 필요 시 = 코드/Change Plan/ADR 영역.
