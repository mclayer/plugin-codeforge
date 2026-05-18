---
title: Codex substitution path — decision tree narrative
area: codex-collaboration
introduced_by: CFP-946-A
parent_epic: CFP-946
status: active
date: 2026-05-18
related_adrs:
  - ADR-052  # Amendment 8 — 6 touchpoint × 3-enum cross-matrix
  - ADR-070  # §결정 D1 expansion (Amendment 3) — substitution path 3-enum normative anchor
  - ADR-081  # §결정 D2 — verify-before-trust 5 sub-scope
related_files:
  - docs/adr/ADR-052-codex-proactive-check-touchpoints.md
  - docs/adr/ADR-070-codex-verify-before-trust.md
  - docs/adr/ADR-081-codex-worker-prompt-boilerplate.md
  - docs/domain-knowledge/domain/codex-collaboration/README.md
---

# Codex substitution path — decision tree narrative

본 페이지 = Codex worker spawn 결정 시점의 substitution path 3-enum 선택 decision tree narrative (CFP-946-A carrier). 결정 본문 SSOT = [ADR-070 §결정 D1 expansion](../../../adr/ADR-070-codex-verify-before-trust.md) + [ADR-052 Amendment 8](../../../adr/ADR-052-codex-proactive-check-touchpoints.md).

## §1. decision tree (substitution path 선택)

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

## §2. fail-mode enum 6 종 (fallback_skip_with_marker 채택 시)

| fail-mode | 운영적 정의 |
|---|---|
| `api_missing` | codex@openai-codex plugin 미설치 / codex CLI binary 부재 |
| `version_skew` | codex CLI version 이 codeforge wrapper 요구 version 과 mismatch (예: codex-companion runtime contract version mismatch) |
| `enterprise_blocked` | enterprise org 정책으로 codex CLI 외부 API 호출 차단 |
| `gh_api_network_blocked` | Codex worker 의 own working directory 안 `gh api` invocation 이 network policy 로 차단 |
| `manual_substitution_declared` | Orchestrator 가 사전에 manual_substitution_declare 채택 + 본 spawn skip 결정 (cascade) |
| `inline_orchestrator_verify_only` | Codex worker 의 추가 finding 없이 Orchestrator inline verify 만으로 sufficient — Codex spawn cost 회피 derived default |

## §3. 6 touchpoint × 3-enum 운영 매트릭스 (ADR-052 Amendment 8 §A1 cross-ref)

ADR-052 Amendment 8 §A1 표 = SSOT. 본 §3 = 운영 narrative 만:

### §3.1 Touchpoint #1 Pre-question Review

- **default** = `inline_orchestrator_verify` (질문 초안 = Orchestrator 자체 발화, Codex review 결과 reformulation)
- **manual_substitution_declare 채택** = 질문 초안 인용 source 가 cross-repo / sibling plugin file (sandbox 영역 외)
- **fallback_skip_with_marker 채택** = Codex CLI 미가용 / sandbox network-block 확정 (Orchestrator 가 단독 발화, ADR-064 §결정 9 3-check self-check 만으로 진행)

### §3.2 Touchpoint #2 Design Synthesis Check (mandatory)

- **default** = `inline_orchestrator_verify` (§3 Change Plan = Orchestrator 의 own worktree 안 file)
- **manual_substitution_declare 채택** = Change Plan 또는 ADR 본문 cross-repo state 인용 시 (예: marketplace.json mirrored field 인용, internal-docs/wrapper/specs/ 인용)
- **fallback_skip_with_marker 채택** = EC-1 recursive substitution cascade (본 Story-A 자체 Phase 1 PR DesignReview lane 의 reentrant — substitution path 3-enum codification carrier 자체가 재발동 시 fallback skip 채택)

### §3.3 Touchpoint #3 Development Rescue

- **default** = `inline_orchestrator_verify` (구현 블로커 evidence = own worktree)
- **manual_substitution_declare 채택** = 구현 블로커 evidence 가 worktree 외 영역 (sibling plugin 코드 / cross-repo CI log)
- **fallback_skip_with_marker 채택** = 일반적으로 발생 0 — DeveloperPLAgent 가 own worktree scope 안

### §3.4 Touchpoint #4 Requirements Output Review (multi-round debate)

- **default** = `inline_orchestrator_verify` (RequirementsPL synthesis = Story file own own internal-docs path)
- **manual_substitution_declare 채택** = Codex finding 의 fact-check sub-criterion (cross-repo state verification, [ADR-052 Amendment 3](../../../adr/ADR-052-codex-proactive-check-touchpoints.md) §A2 표 row 4) 인 경우
- **fallback_skip_with_marker 채택** = 일반적으로 발생 0 — Story §1-§6 = internal-docs path 가 sandbox 영역 외 → ADR-052 Amendment 5 verbatim 첨부 의무 (debate-protocol-v1 Round 0 input verbatim 첨부 의무 정합)

### §3.5 Touchpoint #5 FIX Root Cause 2nd Opinion

- **default** = `inline_orchestrator_verify` (review findings = own worktree)
- **manual_substitution_declare 채택** = review findings evidence pack 안 cross-repo file path 인 경우
- **fallback_skip_with_marker 채택** = Codex CLI 미가용 / D4 사용자 escalation 직접 진입 (Codex 2nd opinion skip)

### §3.6 Touchpoint #6 ADR Draft Review

- **default** = `inline_orchestrator_verify` (ADR draft = own worktree 의 docs/adr/ path)
- **manual_substitution_declare 채택** = ADR cross-ref ADR 본문 (sibling plugin docs/adr/ path) 인용 시
- **fallback_skip_with_marker 채택** = EC-1 recursive substitution cascade (본 ADR-052 Amendment 8 자체 작성 시점 — manual_substitution_declare 사전 declare 의무, ADR-070 Amendment 3 작성 시도 EC-2 cascade depth ≥ 2 시 Orchestrator ESCALATE)

## §4. verify-before-trust 5 sub-scope 무조건 적용 (ADR-081 §결정 D2)

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

## §5. KPI deferred (post-merge follow-up CFP carrier)

substitution_count + verify_failure_rate 정량 측정 (threshold=5 / 15%) = post-merge follow-up CFP carrier 영역. 본 narrative + ADR-070 §결정 D1 expansion + ADR-052 Amendment 8 의무 = prose tally only (Story §10 marker grep count, lint 없음).

threshold 도달 시 (`substitution_count ≥ 5` OR `verify_failure_rate ≥ 15%`):

- mechanical lint 도입 검토 (ADR-070 §D5 declaration-only retain 재평가 trigger)
- `docs/kpi/codex-substitution.json` artifact + monthly cron workflow
- `codex-substitution-presence` warning-tier entry (`docs/evidence-checks-registry.yaml`)

## §6. 관련 페이지

- [`README.md`](README.md) — Codex Collaboration narrative SSOT hub
- [ADR-052 Amendment 8](../../../adr/ADR-052-codex-proactive-check-touchpoints.md) — 6 touchpoint × 3-enum cross-matrix SSOT
- [ADR-070 §결정 D1 expansion](../../../adr/ADR-070-codex-verify-before-trust.md) — substitution path 3-enum normative anchor SSOT
- [ADR-081 §결정 D2](../../../adr/ADR-081-codex-worker-prompt-boilerplate.md) — verify-before-trust 5 sub-scope SSOT
- [playbook §3.10](../../../orchestrator-playbook.md) — Codex Proactive Check dispatch + substitution path 3-enum + 결과 처리 SSOT
