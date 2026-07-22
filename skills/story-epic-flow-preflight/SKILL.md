---
name: story-epic-flow-preflight
description: Story flow / Epic flow / Cross-repo Epic / Preflight 결정 시 (lane 진입 prerequisite). 1 Story = 2 PRs 기본 구조, Epic flow, Cross-repo Epic centralization mode, 레인별 Preflight 체크 의무를 정의한다.
tools: Read
---

# Story / Epic Flow + Preflight 체크 (CFP-45 + ADR-020 + ADR-031 + CFP-1059 / ADR-087+088)

> 참조 테이블 skill — lane 진입 전 Story / Epic flow 패턴과 Preflight 체크 요건을 확인하세요.

## 레인 8개 · 단계 정의 (CFP-2782 / [ADR-121](../../archive/adr/ADR-121-deprecate-deploy-lanes.md) — deploy·deploy-review 2 lane 물리 제거로 10 → 8 lane. 선행 CFP-2326 / [ADR-125](../../archive/adr/ADR-125-requirements-review-lane.md) — 요구사항리뷰 신설)

```
[Story] 요구사항 → 요구사항 리뷰 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → [CI gate]  ← N회 반복
                                                                   ↓ 전체 Story PASS 후 1회 (Epic 묶음 모든 Story merged 후)
                                                           [Epic 통합테스트] → Epic close
```

모든 Story는 **full 8 레인 + CI gate** 통과 (CFP-2326 후 — 요구사항 리뷰 신설; CFP-2782 / ADR-121 후 — deploy·deploy-review 2 lane 물리 제거). 요구사항 리뷰는 Phase 1 내부 sub-gate (요구사항 §1-7 직후·설계 진입 전 — ADR-125 결정 1). **Fast-path 없음 (예외 0).** Hotfix 긴급경로(Minimal / Medium)도 폐지 — 운영 장애 시에도 정식 풀 플로우 무조건 거침. 긴급도는 우선순위 표기(`severity:critical` 라벨 / PR title)만, lane 생략 0 (ADR-127 §결정 3). **CI gate** = 구현 리뷰 PASS 후 Orchestrator가 `gh pr checks <PR_NUMBER> --required --watch --fail-fast` 를 백그라운드(Bash run_in_background)로 실행 — required check 만 대기 (전체 검사 대기 금지), watch 종료 시 자동 재개 → PASS 시 merge gate 진입 (`lanes.security_ai: true` consumer는 SecurityTestPL spawn 추가). required check 5분+ stuck 시 re-trigger 1회 → admin merge fallback + 사후 검증 + 결과 보고 자동 진행; required check 0건 repo 는 전체 watch fallback. FAIL 시 DeveloperPL 1차 진단 → ArchitectPL 최종 판정 → FIX loop (CFP-317 / ADR-048-ci-native-test-execution + Amendment 2).

## Story flow (default — single-repo Story 또는 Epic 외 1 child Story)

**1 Story = 2 PRs**:
- **Phase 1 PR** (요구사항 + 요구사항리뷰 + 설계 + 설계리뷰 lane): `docs/stories/<KEY>.md` §1-7 + `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md` (소비자 repo) / `archive/adr/ADR-NNN-<slug>.md` (plugin-codeforge wrapper 자기 — prune 이후 이동). **(internal-docs SSOT 적용 시, ADR-013 dogfood-out + amendment)**: change-plan 위치는 `<internal-docs-clone>/<plugin-folder>/change-plans/<slug>.md`. Codeforge family / dogfood Story 의 경우 본 path override. 또한 doc-only Story (예: ADR carrier 가 architecture decision SSOT 인 경우) 는 **별도 change-plan 면제** — ADR 가 §3 도입할 설계 SSOT 역할 충족 (ADR-013 정합).
- **Phase 2 PR** (구현 + 구현리뷰 + 구현테스트 + 보안테스트 lane): `src/**` + `tests/**` + `docs/stories/<KEY>.md` §8-11 append

**doc-only 단일 PR 폐지 (ADR-127 §결정 2)**: 모든 Story = Phase 1 PR + Phase 2 PR 분리 무조건. 구 "doc-only fast-path = 1 Story = 1 PR" 형태 폐지 — SSOT 문서만 바뀌는 변경도 정식 full 10 lane + Phase 1/2 분리. lane 이 검사할 산출물 target 이 부재한 lane 은 정식 분류상 `N/A — <사유>`(ADR-005 / ADR-127 §결정 5 3축 AND) — 단축이 아니라 정상 N/A.

## Epic flow (cross-repo 또는 multi-Story Epic)

**1 Epic = Phase 1 doc PR + N implementation PRs + Phase N+1 close PR** (N=3~5 일반적):
- **Phase 1 PR** (hub / owner repo): Epic doc + N child Story stub + Codex 7-area review aggregate
- **Phase 2 ~ Phase N PR**: 각 child Story 의 implementation. **Joint-phase narrow form 허용** (단일 child Story 가 1 phase 안에서 multi-repo joint PR 보유 가능, ADR-020 Amendment 1 §결정 9)
- **Phase N+1 close PR** (hub / owner repo): `EPIC-RESULTS-<KEY>.md` artifact + Epic Issue close
- Mid-Phase **spec amendment PR** 가능 (Codex push-back 발견 시)

**전환 자율 진행 (한 세션 내 — [ADR-071 §결정 22](../../archive/adr/ADR-071-orchestrator-user-dialog-convergence.md))**: 한 세션에서 Epic 을 여러 child Story 로 진행할 때, **child Story N→N+1 전환 (및 단일 Story Phase1→Phase2 전환) = 자동 이어서 진행이 default**. 전환 지점에서 무발화로 멈추거나(over-halt) "다음 Story 진행할까요?" 확인 질문(over-ask) 하지 마라 — 둘 다 §결정 15(3-touchpoint)·§결정 20(ask-trigger 3종) 어디에도 미해당인 부당한 멈춤. **정당한 멈춤 3종만 전환 지점에서도 보존**(억제 대상 아님): ① 요구 자체가 애매 / ② 진짜 가치 trade-off(default 비자명) / ③ 비가역·고비용. 이 norm 은 **§결정 18 session-swap("context 가득 → 별 세션") reflex 와 disjoint 축**(session-swap 재codify 아님 — cross-ref only). in-session 전환 한정이며 세션 재개(cold-resume) 확인 경로(playbook §3.12)는 별 경로로 무관.

## Cross-repo Epic — Centralization mode 의무 결정 (ADR-020 Amendment 1 / CFP-81)

- **Mode A (repo-local, ADR-020 v1 default)**: 각 작업 repo 가 자체 Story
- **Mode B (hub-centralized)**: 1 hub repo 가 모든 child Story (mctrader 패턴)
- parent Epic Issue + child Story (per mode) + `epic_dependencies` graph + Change Plan §3 contract pin + Mixed-mode 금지. 상세 [ADR-020](../../archive/adr/ADR-020-cross-repo-epic-pattern.md), playbook §3.4.

## 레인 진입 전 Preflight 체크 의무

각 레인 진입 직전 Orchestrator가 3개 체크 수행:
1. **phase 라벨 정합** — 현재 Story Issue 라벨이 해당 레인에 맞는 `phase:*` 보유 여부. **Phase label transition timing (add/remove + gate attach + timing signal) SSOT** = [playbook §9.7.1](../../docs/orchestrator-playbook.md#971-phase-label-transition-timing-cfp-1577--cfp-1539cfp-1540-batch-retro-41-1) (CFP-1577 — `phase:완료` precondition `gate:design-review-pass` AND `gate:retro-complete` 의무 포함)
2. **docs file 선행 섹션** — 해당 레인 진입 전 의무 섹션 (§1-7 Phase 1 완료 등) 존재 여부
3. **외부 의존성 가용** — MCP/CLI/plugin 상태 정상 여부

FAIL 시 block+report. 상세는 playbook §3B.

## 레인 진입 트리거 표

| 레인 | 진입 트리거 | 1차 self-write target | FIX max |
|---|---|---|---|
| 요구사항 | story-init.yml Action (Issue Forms 제출) | §1·§2·§5·§6 (RequirementsPL + 3 sub) | — |
| 요구사항 리뷰 | RequirementsPL synthesis 완료 (CFP-2326 / ADR-125) | §9 (RequirementsReviewPL Claude+Codex 종합) + `gate:requirements-review-pass` | 3 |
| 설계 | 요구사항 리뷰 PASS | §3·§7·§11 + change-plan + ADR-NNN (ArchitectAgent + 6 SubAgent) | — |
| 설계 리뷰 | ArchitectAgent verdict | §9 (DesignReviewPL Claude+Codex 종합) + `gate:design-review-pass` | 3 |
| 구현 | 설계 리뷰 PASS | §8·§8.5 + Phase 2 PR 첫 commit (DeveloperPL + QADev + N role:dev) | — |
| 구현 리뷰 | DeveloperPL ready | §9 (CodeReviewPL Claude+Codex 종합) | 3 |
| CI gate | 구현 리뷰 PASS | (Orchestrator inline `gh pr checks --required` 백그라운드 watch — ADR-048 Amd 2) | ∞ |
| 통합테스트 | **Epic 하위 전체 Story** CI gate PASS (1회) | `tests/integration/baseline/` + `tests/integration/stories/<EPIC-KEY>/` 동적 실행 | 3 |
| 보안 테스트 **(opt-in: lanes.security_ai: true)** | 통합테스트 PASS | §9 (SecurityTestPL 2-layer) + `gate:security-test-pass` | ∞ |

**통합테스트는 Epic-level 실행 (ADR-055 Amendment 2)**: Epic 하위 모든 Story CI gate PASS 후 Orchestrator가 IntegrationTestAgent 1회 spawn. Baseline Suite + Story Suite 동적 실행. FAIL 시 `responsible_stories` 집계 → 해당 Story FIX loop. 상세: [playbook §3.11–3.12](../../docs/orchestrator-playbook.md) + [ADR-055 Amendment 2](../../archive/adr/ADR-055-integration-test-lane-policy.md).

세부 spawn sequence · branch logic · FIX 진단 흐름 SSOT: [playbook §3](../../docs/orchestrator-playbook.md) + 각 lane plugin CLAUDE.md.
