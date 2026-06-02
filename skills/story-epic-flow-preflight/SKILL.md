---
name: story-epic-flow-preflight
description: Story flow / Epic flow / Cross-repo Epic / Preflight 결정 시 (lane 진입 prerequisite). 1 Story = 2 PRs 기본 구조, Epic flow, Cross-repo Epic centralization mode, 레인별 Preflight 체크 의무를 정의한다.
tools: Read
---

# Story / Epic Flow + Preflight 체크 (CFP-45 + ADR-020 + ADR-031 + CFP-1059 / ADR-087+088)

> 참조 테이블 skill — lane 진입 전 Story / Epic flow 패턴과 Preflight 체크 요건을 확인하세요.

## 레인 8개 · 단계 정의 (CFP-1059 / [ADR-087](../../docs/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) + [ADR-088](../../docs/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md) — 6 → 8 lane 확장)

```
[Story] 요구사항 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → [CI gate]  ← N회 반복
                                                                   ↓ 전체 Story PASS 후 1회
                                                           [Epic 통합테스트]
                                                                   ↓ Epic 묶음 모든 Story merged 후
                                                           [배포] → [배포 리뷰] → Epic close
```

모든 Story는 **full 8 레인 + CI gate** 통과 (CFP-1059 후 — 배포 + 배포 리뷰 신설). Fast-path 없음 (단 **Hotfix 경로** 2종은 예외 — 운영 장애 대응, 사후 감사 의무. 상세는 [`docs/hotfix-playbook.md`](../../docs/hotfix-playbook.md)). **CI gate** = 구현 리뷰 PASS 후 Orchestrator가 `gh pr checks <PR_NUMBER> --watch`로 GitHub CI 결과 polling (최대 30분 timeout). PASS 시 merge gate 진입 (`lanes.security_ai: true` consumer는 SecurityTestPL spawn 추가). FAIL 시 DeveloperPL 1차 진단 → ArchitectPL 최종 판정 → FIX loop (CFP-317 / ADR-048-ci-native-test-execution).

**배포 lane (Phase 1 declarative — CFP-1059 / ADR-087)**: Epic 묶음 종료 후 (모든 Story merged) Orchestrator → DeployPLAgent 자동 trigger. 변경 repo enumeration + DeployWorkerAgent N 병렬 dispatch (repo 단위). 배포 매커니즘 = blue-green + atomic swap + 3-시간 보존 + 자동 rollback (단일 매커니즘 고정). FAIL 시 자동 rollback + FIX dispatch. 활성 조건 = consumer `project.yaml` 안 `deploy:` block 등록 + codeforge-deploy plugin install (opt-in).

**배포 리뷰 lane (Phase 1 declarative — CFP-1059 / ADR-088)**: 배포 lane PASS 직후 mandatory. DeployReviewPLAgent (Opus + debate-protocol-v1 trigger 의무) 검증 3종 = smoke / 성능 비교 / cutover 사후 검증. ProductionEvidenceDeputy ownership 이관 (codeforge-design CONDITIONAL → codeforge-deploy-review 정식). 성능 미충족 시 multi-round adversarial debate 자동 발동 (RequirementsPL ↔ ArchitectPL ↔ DeveloperPL).

## Story flow (default — single-repo Story 또는 Epic 외 1 child Story)

**1 Story = 2 PRs**:
- **Phase 1 PR** (요구사항 + 설계 + 설계리뷰 lane): `docs/stories/<KEY>.md` §1-7 + `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md`. **(internal-docs SSOT 적용 시, ADR-013 dogfood-out + amendment)**: change-plan 위치는 `<internal-docs-clone>/<plugin-folder>/change-plans/<slug>.md`. Codeforge family / dogfood Story 의 경우 본 path override. 또한 doc-only Story (예: ADR carrier 가 architecture decision SSOT 인 경우) 는 **별도 change-plan 면제** — ADR 가 §3 도입할 설계 SSOT 역할 충족 (ADR-013 정합).
- **Phase 2 PR** (구현 + 구현리뷰 + 구현테스트 + 보안테스트 lane): `src/**` + `tests/**` + `docs/stories/<KEY>.md` §8-11 append

**doc-only fast-path (ADR-054 적용 시)**: **1 Story = 1 PR** — Phase 1/2 분리 없음. 단일 PR에 요구사항·설계·경량 설계리뷰 결과 포함; Story file §1·§2·§11 필수, §3~§10은 `N/A — doc-only fast-path (ADR-054)` 선언 의무.

## Epic flow (cross-repo 또는 multi-Story Epic)

**1 Epic = Phase 1 doc PR + N implementation PRs + Phase N+1 close PR** (N=3~5 일반적):
- **Phase 1 PR** (hub / owner repo): Epic doc + N child Story stub + Codex 7-area review aggregate
- **Phase 2 ~ Phase N PR**: 각 child Story 의 implementation. **Joint-phase narrow form 허용** (단일 child Story 가 1 phase 안에서 multi-repo joint PR 보유 가능, ADR-020 Amendment 1 §결정 9)
- **Phase N+1 close PR** (hub / owner repo): `EPIC-RESULTS-<KEY>.md` artifact + Epic Issue close
- Mid-Phase **spec amendment PR** 가능 (Codex push-back 발견 시)

## Cross-repo Epic — Centralization mode 의무 결정 (ADR-020 Amendment 1 / CFP-81)

- **Mode A (repo-local, ADR-020 v1 default)**: 각 작업 repo 가 자체 Story
- **Mode B (hub-centralized)**: 1 hub repo 가 모든 child Story (mctrader 패턴)
- parent Epic Issue + child Story (per mode) + `epic_dependencies` graph + Change Plan §3 contract pin + Mixed-mode 금지. 상세 [ADR-020](../../docs/adr/ADR-020-cross-repo-epic-pattern.md), playbook §3.4.

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
| 설계 | RequirementsPL verdict | §3·§7·§11 + change-plan + ADR-NNN (ArchitectAgent + 6 SubAgent) | — |
| 설계 리뷰 | ArchitectAgent verdict | §9 (DesignReviewPL Claude+Codex 종합) + `gate:design-review-pass` | 3 |
| 구현 | 설계 리뷰 PASS | §8·§8.5 + Phase 2 PR 첫 commit (DeveloperPL + QADev + N role:dev) | — |
| 구현 리뷰 | DeveloperPL ready | §9 (CodeReviewPL Claude+Codex 종합) | 3 |
| CI gate | 구현 리뷰 PASS | (Orchestrator inline `gh pr checks` polling — 30분 timeout) | ∞ |
| 통합테스트 | **Epic 하위 전체 Story** CI gate PASS (1회) | `tests/integration/baseline/` + `tests/integration/stories/<EPIC-KEY>/` 동적 실행 | 3 |
| 보안 테스트 **(opt-in: lanes.security_ai: true)** | 통합테스트 PASS | §9 (SecurityTestPL 2-layer) + `gate:security-test-pass` | ∞ |

**통합테스트는 Epic-level 실행 (ADR-055 Amendment 2)**: Epic 하위 모든 Story CI gate PASS 후 Orchestrator가 IntegrationTestAgent 1회 spawn. Baseline Suite + Story Suite 동적 실행. FAIL 시 `responsible_stories` 집계 → 해당 Story FIX loop. 상세: [playbook §3.11–3.12](../../docs/orchestrator-playbook.md) + [ADR-055 Amendment 2](../../docs/adr/ADR-055-integration-test-lane-policy.md).

세부 spawn sequence · branch logic · FIX 진단 흐름 SSOT: [playbook §3](../../docs/orchestrator-playbook.md) + 각 lane plugin CLAUDE.md.
