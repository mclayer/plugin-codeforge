---
kind: registry
registry: comment-prefix
version: "1.3"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/comment-prefix-registry-v1.md
date: 2026-05-17
authors:
  - Claude (CFP-32 codification — CFP-31 ζ arc parent design 기반)
  - CFP-139 (2026-05-09) — v1.0 → v1.1 MINOR bump (`[GitOps]` prefix 추가, ADR-047)
  - CFP-658 (2026-05-14) — v1.1 → v1.2 MINOR bump (`[SECURITY-FALLBACK]` prefix 추가, ADR-027 Amendment 2)
  - CFP-845 (2026-05-17) — v1.2 → v1.3 MINOR bump (`[bypass-justification]` prefix 추가, ADR-024 Amendment 8 §결정 6.A.4 carrier)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-009 (Wrapper-only core + writer-distributed lane plugins, CFP-31 신설 예정)
  - ADR-047 (GitOpsAgent — CFP-139, [GitOps] prefix carrier)
  - ADR-027 Amendment 2 (Action-blocked fallback — CFP-658, [SECURITY-FALLBACK] prefix carrier)
  - ADR-024 Amendment 8 (bypass-as-norm-mutation 후속 escalation — CFP-845 §결정 6.A.4, [bypass-justification] prefix carrier)
related_files:
  - agents/DocsAgent.md (이전 narrative SSOT — 본 registry 신설 후 cross-ref로 변경)
  - docs/orchestrator-playbook.md
---

# comment-prefix-registry v1.3

## 1. 목적

GitHub Issue 코멘트의 phase prefix (11종 + Orchestrator Preflight 1종 + GitOps 1종 + SECURITY-FALLBACK 1종 + bypass-justification 1종 = 총 14종, v1.3) machine-readable SSOT. ζ arc 진행에 따라 lane plugin이 자기 lane prefix로 직접 코멘트 게시 시점에 단일 형식·시맨틱·posters 보장.

## 2. Schema

각 prefix entry:

| 필드 | 타입 | 설명 |
|---|---|---|
| prefix | string | Bracket 형식 (예: `[설계]`) |
| phase | string | 레인 식별자 (requirements / design / design-review / implementation / code-review / test / security-test / pmo / fix / completed / preflight / **gitops** — v1.1 신규 / **security-fallback** — v1.2 신규 / **bypass-justification** — v1.3 신규) |
| current_owner | string | CFP-32 시점 코멘트 게시 주체 |
| target_owner_plugin | string | ζ arc 완료 후 owner plugin (또는 "core wrapper 잔류") |
| posters | array&lt;string&gt; | 본 prefix 사용 권한이 있는 agent 또는 Action |
| auto_mirror | bool | CI Action이 자동 mirror 하는가 (true: `[FIX #N]`만) |

## 3. 항목

```yaml
prefixes:
  - prefix: "[요구사항]"
    phase: requirements
    current_owner: DocsAgent
    target_owner_plugin: codeforge-requirements (CFP-37 후)
    posters:
      - RequirementsPLAgent
      - DomainAgent
      - RequirementsAnalystAgent
      - ResearcherAgent
    auto_mirror: false

  - prefix: "[설계]"
    phase: design
    current_owner: DocsAgent
    target_owner_plugin: codeforge-design (CFP-40 후)
    posters:
      - ArchitectPLAgent
      - ArchitectAgent
      - CodebaseMapperAgent
      - RefactorAgent
      - SecurityArchitectAgent
      - TestContractArchitectAgent
      - DataMigrationArchitectAgent
    auto_mirror: false

  - prefix: "[설계-리뷰]"
    phase: design-review
    current_owner: "(CFP-35) DesignReviewPLAgent → (CFP-61) Orchestrator post-Sonnet"
    target_owner_plugin: "core wrapper (Orchestrator 직접 게시 — review-verdict final write, CFP-61 / ADR-022)"
    posters:
      - Orchestrator  # review verdict final write (CFP-61 / ADR-022 §결정 3 step 4)
      # DesignReviewPLAgent, ClaudeReviewAgent, CodexReviewAgent — packet return only (no comment post, CFP-61)
    auto_mirror: false

  - prefix: "[구현]"
    phase: implementation
    current_owner: DocsAgent
    target_owner_plugin: codeforge-develop (CFP-39 후)
    posters:
      - DeveloperPLAgent
      - DeveloperAgent
      - DataEngineerAgent
      - InfraEngineerAgent
      - QADeveloperAgent
      - "<role:dev overlay/preset 에이전트>"
    auto_mirror: false

  - prefix: "[구현-리뷰]"
    phase: code-review
    current_owner: "(CFP-35) CodeReviewPLAgent → (CFP-61) Orchestrator post-Sonnet"
    target_owner_plugin: "core wrapper (Orchestrator 직접 게시 — review-verdict final write, CFP-61 / ADR-022)"
    posters:
      - Orchestrator  # review verdict final write (CFP-61 / ADR-022 §결정 3 step 4)
      # CodeReviewPLAgent, ClaudeReviewAgent, CodexReviewAgent — packet return only (no comment post, CFP-61)
    auto_mirror: false

  - prefix: "[구현-테스트]"
    phase: test
    current_owner: DocsAgent
    target_owner_plugin: codeforge-test (CFP-38 후)
    posters:
      - TestAgent
    auto_mirror: false

  - prefix: "[보안-테스트]"
    phase: security-test
    current_owner: "(CFP-35) SecurityTestPLAgent → (CFP-61) Orchestrator post-Sonnet"
    target_owner_plugin: "core wrapper (Orchestrator 직접 게시 — review-verdict final write, CFP-61 / ADR-022)"
    posters:
      - Orchestrator  # review verdict final write (CFP-61 / ADR-022 §결정 3 step 4)
      # SecurityTestPLAgent, ClaudeReviewAgent, CodexReviewAgent — packet return only (no comment post, CFP-61)
    auto_mirror: false

  - prefix: "[PMO]"
    phase: pmo
    current_owner: DocsAgent
    target_owner_plugin: codeforge-pmo (CFP-36 후)
    posters:
      - PMOAgent
    auto_mirror: false

  - prefix: "[FIX #N]"
    phase: fix
    current_owner: "fix-ledger-sync.yml CI Action (자동 mirror)"
    target_owner_plugin: "(CI Action 유지 — plugin 무관)"
    posters:
      - "fix-ledger-sync.yml (자동)"
      - "DocsAgent (fallback only — Action 실패 시)"
    auto_mirror: true

  - prefix: "[완료]"
    phase: completed
    current_owner: DocsAgent
    target_owner_plugin: "(CI 위임 가능 — CFP-34 검증 후 결정)"
    posters:
      - DocsAgent
    auto_mirror: false

  - prefix: "[<진입 레인>] Orchestrator: Preflight {PASS|FAIL}"
    phase: preflight
    current_owner: Orchestrator
    target_owner_plugin: "(core wrapper 잔류 — Orchestrator 직접 게시)"
    posters:
      - Orchestrator
    auto_mirror: false

  - prefix: "[GitOps]"                         # NEW in v1.1 (CFP-139 / ADR-047)
    phase: gitops
    current_owner: codeforge-pmo (GitOpsAgent self-write)
    target_owner_plugin: codeforge-pmo
    posters:
      - GitOpsAgent
    auto_mirror: false

  - prefix: "[SECURITY-FALLBACK]"              # NEW in v1.2 (CFP-658 / ADR-027 Amendment 2)
    phase: security-fallback
    current_owner: "SecurityArch deputy + Orchestrator (manual fallback path audit channel)"
    target_owner_plugin: "core wrapper (Orchestrator 직접 게시 — manual fallback audit-trailed channel)"
    scope: "fallback:manual label 부착 PR 의 audit-trailed channel comment — workflow-permission-blocked 사유 명시 의무"
    example: "[SECURITY-FALLBACK] 본 PR 은 enterprise default_workflow_permissions:read 차단으로 Action 자동화 우회 — Trigger (A) bootstrap.fallback_mode=action_blocked 정합 (CFP-658 §결정 6.A)"
    posters:
      - Orchestrator   # manual fallback path audit comment final write
      - SecurityArchitectAgent   # deputy review packet 안 audit rationale (PL 경유 Orchestrator 게시)
    auto_mirror: false

  - prefix: "[bypass-justification]"           # NEW in v1.3 (CFP-845 / ADR-024 Amendment 8 §결정 6.A.4)
    phase: bypass-justification
    current_owner: "PR author + Orchestrator (hotfix-bypass:* label 부착 시 narrative audit trail)"
    target_owner_plugin: "core wrapper (Orchestrator 직접 게시 또는 PR author 자율 게시 — bypass-justification-marker.yml workflow grep-presence lint 대상)"
    scope: "hotfix-bypass:* label 부착 PR 의 narrative audit trail mechanical enforce — `^\\[bypass-justification\\]` prefix top-level PR comment 존재 의무 (review comment 제외). semantic adequacy 불가 (grep-only) — reviewer responsibility, false-positive risk 명시"
    example: "[bypass-justification] 본 PR 은 `hotfix-bypass:wording-dictionary` 부착 사유 = 표 안 (a) 카테고리 `별` standalone 사용 (CFP-672 Amendment 5 정합, mechanical lint 가 표 column header 와 freestanding `별` 미구분 false-positive). 정당 예외 declare."
    posters:
      - "<PR author>"            # 자율 게시 (hotfix-bypass:* label 부착자 책임)
      - Orchestrator             # PR author 가 보충 필요 시 추가 게시 (자율 audit 보강)
    auto_mirror: false
```

## 4. 변경 규칙

- **Append-only for v1.x**: 새 prefix 추가는 minor bump (v1.0 → v1.1). 기존 prefix 삭제 또는 이름 변경은 v2.0 BREAKING (ADR-008 versioning 룰)
- **Owner transition**: ζ arc 진행에 따라 `current_owner` (DocsAgent) → `target_owner_plugin`으로 이전. 이전 시점은 해당 lane plugin 추출 CFP에 명시 (예: `[설계]` prefix는 CFP-40에서 codeforge-design으로 이전)
- **Posters 갱신**: 기존 prefix에 새 agent 추가는 minor (v1.1). agent 이름 변경(예: rename)도 minor — alias 매핑으로 호환성 유지
- **`[FIX #N]` 자동 mirror**: `fix-ledger-sync.yml` CI Action이 §10 commit 감지 시 자동. agent는 직접 게시 금지 (fallback 시 DocsAgent 사용)
- **Format 위반 enforcement**: lane plugin이 본 registry 외 prefix 또는 형식으로 게시 시 향후 CFP-33 contract harness가 lint catch

## 5. 변경 이력

| CFP | Version | 변경 내용 |
|---|---|---|
| CFP-32 | v1.0 | 초기 codification — 11 prefix taxonomy (ζ arc 진행 CFP-31~CFP-40 기반) |
| CFP-35 | v1.0 | review verdict 3 prefix (`[설계-리뷰]` / `[구현-리뷰]` / `[보안-테스트]`) current_owner → DesignReviewPL / CodeReviewPL / SecurityTestPL (review-verdict-v2 self-write) |
| CFP-61 | v1.0 | review verdict 3 prefix current_owner 재정의: DesignReviewPLAgent / CodeReviewPLAgent / SecurityTestPLAgent → **Orchestrator post-Sonnet** (ADR-022 review-verdict 5-step step 4). PL 은 packet return only — comment post 권한 제거. target_owner_plugin = core wrapper 잔류 |
| **CFP-139** | **v1.1** | **MINOR bump** — `[GitOps]` prefix 추가 (GitOpsAgent self-write 영역, codeforge-pmo plugin sibling teammate). ADR-047 carrier. Append-only for v1.x rule 정합. 11 → 12 phase prefix taxonomy. |
| **CFP-658** | **v1.2** | **MINOR bump** — `[SECURITY-FALLBACK]` prefix 추가 (manual fallback path audit-trailed channel, fallback:manual label 부착 PR scope). ADR-027 Amendment 2 carrier. Append-only for v1.x rule 정합. 12 → 13 phase prefix taxonomy. label-registry-v2 v2.12 changelog declaration ↔ comment-prefix-registry-v1 entry 양 channel 정합 (`F-CDX-004` 해소). [verified-via: git show origin/main:docs/inter-plugin-contracts/comment-prefix-registry-v1.md] |
| **CFP-845** | **v1.3** | **MINOR bump** — `[bypass-justification]` prefix 추가 (hotfix-bypass:* label 부착 PR 의 narrative audit trail mechanical enforce carrier, ADR-024 Amendment 8 §결정 6.A.4). Append-only for v1.x rule 정합. 13 → 14 phase prefix taxonomy. `bypass-justification-marker.yml` workflow (CFP-845 Phase 2 carrier) 의 grep-presence lint 가 본 prefix 단일 source. semantic adequacy 불가 (grep-only) — false-positive risk 명시, reviewer responsibility. self-meta loop 회피 = `hotfix-bypass:bypass-justification-marker` 부착 PR (38번째 family member, ADR-024 Amendment 8) 은 marker presence check skip. [verified-via: git show origin/main:docs/inter-plugin-contracts/comment-prefix-registry-v1.md — v1.2 active 확인 후 v1.3 MINOR bump] |
