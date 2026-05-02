---
kind: registry
registry: comment-prefix
version: "1.0"
status: Active
authors:
  - Claude (CFP-32 codification — CFP-31 ζ arc parent design 기반)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-009 (Wrapper-only core + writer-distributed lane plugins, CFP-31 신설 예정)
related_files:
  - agents/DocsAgent.md (이전 narrative SSOT — 본 registry 신설 후 cross-ref로 변경)
  - docs/orchestrator-playbook.md
---

# comment-prefix-registry v1

## 1. 목적

GitHub Issue 코멘트의 phase prefix (10종 + Orchestrator Preflight 1종 = 총 11종) machine-readable SSOT. ζ arc 진행에 따라 lane plugin이 자기 lane prefix로 직접 코멘트 게시 시점에 단일 형식·시맨틱·posters 보장.

## 2. Schema

각 prefix entry:

| 필드 | 타입 | 설명 |
|---|---|---|
| prefix | string | Bracket 형식 (예: `[설계]`) |
| phase | string | 레인 식별자 (requirements / design / design-review / implementation / code-review / test / security-test / pmo / fix / completed / preflight) |
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
```

## 4. 변경 규칙

- **Append-only for v1.x**: 새 prefix 추가는 minor bump (v1.0 → v1.1). 기존 prefix 삭제 또는 이름 변경은 v2.0 BREAKING (ADR-008 versioning 룰)
- **Owner transition**: ζ arc 진행에 따라 `current_owner` (DocsAgent) → `target_owner_plugin`으로 이전. 이전 시점은 해당 lane plugin 추출 CFP에 명시 (예: `[설계]` prefix는 CFP-40에서 codeforge-design으로 이전)
- **Posters 갱신**: 기존 prefix에 새 agent 추가는 minor (v1.1). agent 이름 변경(예: rename)도 minor — alias 매핑으로 호환성 유지
- **`[FIX #N]` 자동 mirror**: `fix-ledger-sync.yml` CI Action이 §10 commit 감지 시 자동. agent는 직접 게시 금지 (fallback 시 DocsAgent 사용)
- **Format 위반 enforcement**: lane plugin이 본 registry 외 prefix 또는 형식으로 게시 시 향후 CFP-33 contract harness가 lint catch

## 5. 변경 이력

| CFP | 변경 내용 |
|---|---|
| CFP-32 | 초기 codification — 11 prefix taxonomy (ζ arc 진행 CFP-31~CFP-40 기반) |
| CFP-35 | review verdict 3 prefix (`[설계-리뷰]` / `[구현-리뷰]` / `[보안-테스트]`) current_owner → DesignReviewPL / CodeReviewPL / SecurityTestPL (review-verdict-v2 self-write) |
| CFP-61 | review verdict 3 prefix current_owner 재정의: DesignReviewPLAgent / CodeReviewPLAgent / SecurityTestPLAgent → **Orchestrator post-Sonnet** (ADR-022 review-verdict 5-step step 4). PL 은 packet return only — comment post 권한 제거. target_owner_plugin = core wrapper 잔류 |
