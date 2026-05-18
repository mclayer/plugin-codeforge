---
kind: domain_fact
type: domain-knowledge
area: codex-collaboration
topic_slug: substitution-scope-decision-tree
title: Codex substitution path — decision tree narrative (3-enum 선택 anchor)
status: Active
tags:
  - codex
  - substitution-scope
  - decision-tree
  - sandbox-boundary
  - verify-before-trust
related_adrs:
  - ADR-052
  - ADR-070
  - ADR-081
related_stories:
  - CFP-946-A
  - CFP-946
  - CFP-578
related_files:
  - docs/adr/ADR-052-codex-proactive-check-touchpoints.md
  - docs/adr/ADR-070-codex-verify-before-trust.md
  - docs/adr/ADR-081-codex-worker-prompt-boilerplate.md
  - docs/domain-knowledge/domain/codex-collaboration/README.md
created: 2026-05-18
updated: 2026-05-18
introduced_by: CFP-946-A
parent_epic: CFP-946
date: 2026-05-18
---

# Codex substitution path — decision tree narrative

본 페이지 = Codex worker spawn 결정 시점의 substitution path 3-enum 선택 decision tree narrative (CFP-946-A carrier). 결정 본문 SSOT = [ADR-070 §결정 D1 expansion](../../../adr/ADR-070-codex-verify-before-trust.md) + [ADR-052 Amendment 8](../../../adr/ADR-052-codex-proactive-check-touchpoints.md).

## 정의

Codex worker spawn 결정 시점에 Orchestrator 가 substitution path 3-enum (`inline_orchestrator_verify` / `manual_substitution_declare` / `fallback_skip_with_marker`) 중 1 을 선택하는 **decision tree**. 선택 기준 = Codex CLI 가용성 + sandbox boundary 의 finding evidence scope (sandbox 안 vs 외) + reentrant 위험.

## 컨텍스트

CFP-578 (3 occurrence sentinel, 2026-05) → ADR-070 신설 (verify-before-trust mechanism). CFP-946 (8 occurrence sentinel, 2026-05-18, 2.67x reach) → 본 페이지 carrier (CFP-946-A) = substitution path 3-enum normative codify. 8 occurrence 의 root cause 분류 (정책 vs trigger vs verify) 중 **정책 영역** = substitution scope 의 decision tree 명시 부재 → 본 페이지 = 그 gap mitigation.

## 핵심 규칙

```
Codex worker spawn 결정 시점:

  Step 1: Codex CLI 가용성 확인
    ├─ Codex CLI 가용 + sandbox network-block 없음
    │     └─→ Step 2 진입
    └─ Codex CLI 미가용 OR sandbox network-block 확정 OR reentrant 위험 (8+ occurrence sentinel)
          └─→ enum 3: fallback_skip_with_marker
              + Story §10 marker `[codex-sandbox-fallback: <fail-mode>]`
              + Orchestrator 가 substitution 후속 동작 단독 수행
              + verify-before-trust 5 sub-scope 全 적용 (ADR-081 §결정 D2)

  Step 2: verify task scope 분석
    ├─ finding evidence 영역 = Orchestrator working directory 안 (sandbox 영역 안)
    │     └─→ enum 1: inline_orchestrator_verify (default)
    │         + Story §10 marker 면제 (default behavior)
    │         + Orchestrator file Read / Glob / Grep direct verify
    └─ finding evidence 영역 = sandbox 영역 외 (internal-docs / sibling repo / cross-plugin path)
          └─→ enum 2: manual_substitution_declare
              + Story §10 marker `[codex-substitution-scope-declared: <scope-enum>]`
              + Codex spawn prompt `task` field 본문 또는 sub-field `substitution_scope` 명시
              + ADR-052 Amendment 5 verbatim 첨부 의무 동반 (sandbox 영역 외 file 전체)
```

**핵심 invariant**: substitution path 어느 case 채택해도 verify-before-trust 5 sub-scope 무조건 적용 (ADR-081 §결정 D2). substitution path 선택 = WHEN/HOW, verify scope = WHAT (disjoint axis).

### fail-mode enum 6 종 (fallback_skip_with_marker 채택 시)

| fail-mode | 운영적 정의 |
|---|---|
| `api_missing` | codex@openai-codex plugin 미설치 / codex CLI binary 부재 |
| `version_skew` | codex CLI version 이 codeforge wrapper 요구 version 과 mismatch |
| `enterprise_blocked` | enterprise org 정책으로 codex CLI 외부 API 호출 차단 |
| `gh_api_network_blocked` | Codex worker 의 own working directory 안 `gh api` invocation 이 network policy 로 차단 |
| `manual_substitution_declared` | Orchestrator 가 사전에 manual_substitution_declare 채택 + 본 spawn skip 결정 (cascade) |
| `inline_orchestrator_verify_only` | Codex worker 의 추가 finding 없이 Orchestrator inline verify 만으로 sufficient — Codex spawn cost 회피 derived default |

## 경계

본 페이지 scope = substitution path 3-enum decision tree narrative (운영 SSOT). scope **외**:

- ADR-070 §결정 D1 expansion 본문 (normative anchor) = `docs/adr/ADR-070-codex-verify-before-trust.md` SSOT
- ADR-052 Amendment 8 6 touchpoint × 3-enum cross-matrix 본문 = `docs/adr/ADR-052-codex-proactive-check-touchpoints.md` SSOT
- ADR-081 §결정 D2 verify-before-trust 5 sub-scope 본문 = `docs/adr/ADR-081-codex-worker-prompt-boilerplate.md` SSOT
- mechanical lint / KPI dashboard 구현 = CFP-946-B carrier (별 Story) + post-merge follow-up CFP (KPI deferred)

## 6 touchpoint × 3-enum 운영 매트릭스 (ADR-052 Amendment 8 §A1 cross-ref)

ADR-052 Amendment 8 §A1 표 = SSOT. 본 섹션 = 운영 narrative 만:

### Touchpoint #1 Pre-question Review

- **default** = `inline_orchestrator_verify` (질문 초안 = Orchestrator 자체 발화, Codex review 결과 reformulation)
- **manual_substitution_declare 채택** = 질문 초안 인용 source 가 cross-repo / sibling plugin file (sandbox 영역 외)
- **fallback_skip_with_marker 채택** = Codex CLI 미가용 / sandbox network-block 확정 (Orchestrator 가 단독 발화)

### Touchpoint #2 Design Synthesis Check (mandatory)

- **default** = `inline_orchestrator_verify` (§3 Change Plan = Orchestrator 의 own worktree 안 file)
- **manual_substitution_declare 채택** = Change Plan 또는 ADR 본문 cross-repo state 인용 시
- **fallback_skip_with_marker 채택** = EC-1 recursive substitution cascade

### Touchpoint #3 Development Rescue

- **default** = `inline_orchestrator_verify` (구현 블로커 evidence = own worktree)
- **manual_substitution_declare 채택** = 구현 블로커 evidence 가 worktree 외 영역
- **fallback_skip_with_marker 채택** = 일반적으로 발생 0

### Touchpoint #4 RequirementsPL Multi-round Divergence (mandatory)

- **default** = `inline_orchestrator_verify` (RequirementsPL synthesis = Story file own own internal-docs path)
- **manual_substitution_declare 채택** = Codex finding 의 fact-check sub-criterion (cross-repo state verification) 인 경우
- **fallback_skip_with_marker 채택** = 일반적으로 발생 0

### Touchpoint #5 FIX Root Cause 2nd Opinion

- **default** = `inline_orchestrator_verify` (review findings = own worktree)
- **manual_substitution_declare 채택** = review findings evidence pack 안 cross-repo file path 인 경우
- **fallback_skip_with_marker 채택** = Codex CLI 미가용 / D4 사용자 escalation 직접 진입

### Touchpoint #6 ADR Draft Review

- **default** = `inline_orchestrator_verify` (ADR draft = own worktree 의 docs/adr/ path)
- **manual_substitution_declare 채택** = ADR cross-ref ADR 본문 (sibling plugin docs/adr/ path) 인용 시
- **fallback_skip_with_marker 채택** = EC-1 recursive substitution cascade

## verify-before-trust 5 sub-scope 무조건 적용 (ADR-081 §결정 D2)

substitution path 3-enum 어느 case 채택해도 Orchestrator verify-before-trust 5 sub-scope 무조건 적용 — 결정 본문 SSOT = ADR-081 §결정 D2.

```
substitution_path ∈ {inline_orchestrator_verify, manual_substitution_declare, fallback_skip_with_marker}:
    ↓
verify-before-trust 5 sub-scope:
    1. file scope grep+quote
    2. dir scope recursive grep+count
    3. cross-repo gh api+commit SHA
    4. grep count claim active vs historical 차원
    5. ADR §결정 번호 정확성

(어느 substitution path 채택하든 5 sub-scope verify 의무 면제 0)
```

## KPI deferred (post-merge follow-up CFP carrier)

substitution_count + verify_failure_rate 정량 측정 (threshold=5 / 15%) = post-merge follow-up CFP carrier 영역. 본 narrative + ADR-070 §결정 D1 expansion + ADR-052 Amendment 8 의무 = prose tally only (Story §10 marker grep count, lint 없음).

threshold 도달 시 (`substitution_count >= 5` OR `verify_failure_rate >= 15%`):

- mechanical lint 도입 검토 (ADR-070 §D5 declaration-only retain 재평가 trigger)
- `docs/kpi/codex-substitution.json` artifact + monthly cron workflow
- `codex-substitution-presence` warning-tier entry (`docs/evidence-checks-registry.yaml`)

## 관련 ADR

- [ADR-052 Amendment 8](../../../adr/ADR-052-codex-proactive-check-touchpoints.md) — 6 touchpoint × 3-enum cross-matrix SSOT
- [ADR-070 §결정 D1 expansion (Amendment 3)](../../../adr/ADR-070-codex-verify-before-trust.md) — substitution path 3-enum normative anchor SSOT
- [ADR-081 §결정 D2](../../../adr/ADR-081-codex-worker-prompt-boilerplate.md) — verify-before-trust 5 sub-scope SSOT
- [ADR-064 §결정 1](../../../adr/ADR-064-decision-principle-mandate.md) — CFP scope unitary (Story-A normative ≠ Story-B mechanical)
- [ADR-073](../../../adr/ADR-073-orchestrator-verify-before-assert.md) — Orchestrator verify-before-assert layer disjoint

## 관련 페이지

- [`README.md`](README.md) — Codex Collaboration narrative SSOT hub
- [playbook §3.10](../../../orchestrator-playbook.md) — Codex Proactive Check dispatch + substitution path 3-enum + 결과 처리 SSOT

## 변경 이력

| 시각 (KST) | 변경 | Author | Note |
|---|---|---|---|
| 2026-05-18 KST | 신설 (CFP-946-A Phase 1) | ArchitectAgent (codeforge-design@mclayer) | substitution path 3-enum normative codify + 6 touchpoint cross-matrix 운영 narrative. CFP-578 (3 occurrence) -> CFP-946 (8 occurrence, 2.67x reach) 의 정책 영역 mitigation. domain_fact schema (CFP-28) 정합 frontmatter + 6 required sections. |
