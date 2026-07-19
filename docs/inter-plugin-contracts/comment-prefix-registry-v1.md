---
kind: registry
registry: comment-prefix
version: "1.5"
status: Active
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/comment-prefix-registry-v1.md
date: 2026-05-25
authors:
  - Claude (CFP-32 codification — CFP-31 ζ arc parent design 기반)
  - CFP-139 (2026-05-09) — v1.0 → v1.1 MINOR bump (`[GitOps]` prefix 추가, ADR-160)
  - CFP-658 (2026-05-14) — v1.1 → v1.2 MINOR bump (`[SECURITY-FALLBACK]` prefix 추가, ADR-027 Amendment 2)
  - CFP-845 (2026-05-17) — v1.2 → v1.3 MINOR bump (`[bypass-justification]` prefix 추가, ADR-024 Amendment 8 §결정 6.A.4 carrier)
  - CFP-1336 (2026-05-24) — v1.3 → v1.4 MINOR bump (`[CROSS-REPO-SYNC]` prefix 추가, ADR-073 Amendment 9 + ADR-082 Amendment 14 + ADR-066 Amendment 4 carrier — cross-repo bidirectional label sync workflow audit channel)
  - CFP-1368 (2026-05-25) — v1.4 → v1.5 MINOR bump (`[codex-sandbox-fallback]` + `[codex-substitution-scope-declared]` 2-entry atomic append, ADR-052 Amendment 14 + ADR-070 Amendment 8 + ADR-081 Amendment 7 carrier — codex worker substitution path audit channel, PIVOT-5 NEW Codex TP#4 F-5 self-stale catch by FIX iter 1 ground truth re-verify)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-009 (Wrapper-only core + writer-distributed lane plugins, CFP-31 신설 예정)
  - ADR-160 (GitOpsAgent — CFP-139, [GitOps] prefix carrier)
  - ADR-027 Amendment 2 (Action-blocked fallback — CFP-658, [SECURITY-FALLBACK] prefix carrier)
  - ADR-024 Amendment 8 (bypass-as-norm-mutation 후속 escalation — CFP-845 §결정 6.A.4, [bypass-justification] prefix carrier)
  - ADR-073 Amendment 9 (cross-repo bidirectional label sync verify-before-assert mandate — CFP-1336, [CROSS-REPO-SYNC] prefix carrier)
  - ADR-082 Amendment 14 (§결정 1 layer 1 sub-scope 1-D cross-repo label-write authority — CFP-1336, [CROSS-REPO-SYNC] prefix paired sibling)
  - ADR-066 Amendment 4 (§결정 2 scope minimum 6번째 entry cross-repo-target-repos issues:write — CFP-1336, [CROSS-REPO-SYNC] prefix paired sibling PAT scope grant layer)
  - ADR-052 Amendment 14 (CFP-1286 Wave 2 mechanical wire — codex-fallback-subclass-tally lint activation, CFP-1368 carrier, [codex-sandbox-fallback] + [codex-substitution-scope-declared] 2-prefix codify)
  - ADR-070 Amendment 8 (fail-mode enum 8 → 9 확장 codex_truncated_no_verdict 9번째 value, CFP-1286 declaration-source carrier — CFP-1368 lint logic SSOT cross-validate target)
  - ADR-081 Amendment 7 (Codex worker prompt boilerplate composition + verify-before-trust scope 5 sub-scope SSOT, CFP-1286 declaration-source carrier — CFP-1368 lint logic SSOT cross-validate target)
related_files:
  - agents/DocsAgent.md (이전 narrative SSOT — 본 registry 신설 후 cross-ref로 변경)
  - docs/orchestrator-playbook.md
  - templates/github-workflows/cross-repo-label-sync.yml (CFP-1336 Wave 2 carrier — [CROSS-REPO-SYNC] prefix 자동 게시 source)
  - templates/github-workflows/codex-fallback-tally-check.yml (CFP-1368 Wave 2 carrier — [codex-sandbox-fallback] + [codex-substitution-scope-declared] prefix 검출 source)
  - scripts/lib/check_codex_fallback_tally.py (CFP-1368 Wave 2 carrier — lint logic SSOT cross-validate with comment-prefix-registry-v1 v1.5)
---

# comment-prefix-registry v1.5

## 1. 목적

GitHub Issue 코멘트의 phase prefix (11종 + Orchestrator Preflight 1종 + GitOps 1종 + SECURITY-FALLBACK 1종 + bypass-justification 1종 + CROSS-REPO-SYNC 1종 + codex-sandbox-fallback 1종 + codex-substitution-scope-declared 1종 = 총 17종, v1.5) machine-readable SSOT. ζ arc 진행에 따라 lane plugin이 자기 lane prefix로 직접 코멘트 게시 시점에 단일 형식·시맨틱·posters 보장.

## 2. Schema

각 prefix entry:

| 필드 | 타입 | 설명 |
|---|---|---|
| prefix | string | Bracket 형식 (예: `[설계]`) |
| phase | string | 레인 식별자 (requirements / design / design-review / implementation / code-review / test / security-test / pmo / fix / completed / preflight / **gitops** — v1.1 신규 / **security-fallback** — v1.2 신규 / **bypass-justification** — v1.3 신규 / **cross-repo-sync** — v1.4 신규 / **codex-sandbox-fallback** — v1.5 신규 / **codex-substitution-scope-declared** — v1.5 신규) |
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
      - ModuleArchitectAgent
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

  - prefix: "[GitOps]"                         # NEW in v1.1 (CFP-139 / ADR-160)
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

  - prefix: "[CROSS-REPO-SYNC]"                 # NEW in v1.4 (CFP-1336 / ADR-073 Amendment 9 + ADR-082 Amendment 14 + ADR-066 Amendment 4)
    phase: cross-repo-sync
    current_owner: "cross-repo-label-sync.yml workflow + Orchestrator (CFP-1336 Wave 2 wire 후 자동 게시)"
    target_owner_plugin: "core wrapper (Orchestrator 직접 게시 또는 cross-repo-label-sync.yml workflow 자동 게시 — workflow grep-presence audit 대상)"
    scope: "cross-repo bidirectional label sync workflow (wrapper Story Issue ↔ impl repo PR labels) 의 audit channel comment — (a) warning: PAT 부재 / linked PR 부재 / cross-org reject 시 graceful skip 안내 / (b) skip: 4-pattern T-2 self-trigger guard AND fail (sender.type / actor-allowlist / `[skip-cross-repo-sync]` marker / idempotent diff) 시 audit trail / (c) sync 완료: bidirectional sync success 시 verified-via annotation 포함 audit. ADR-073 Amendment 9 §결정 1-A 9번째 entry `label_change` verify-before-assert 4-step + ADR-082 Amendment 14 sub-scope 1-D 4-tuple write authority verify + ADR-066 Amendment 4 §결정 2 6번째 entry PAT scope grant 정합."
    example: "[CROSS-REPO-SYNC] 본 PR 은 CODEFORGE_CROSS_REPO_PAT secret 미설정으로 degraded mode — manual label sync required (ADR-027 Amendment 2 fallback:manual 정합, ADR-073 Amendment 9 §결정 1-A 9번째 entry label_change trigger graceful skip + verify-before-assert 4-step 정합)."
    posters:
      - Orchestrator                                  # Wave 2 wire 후 직접 게시 (audit 보강 + manual sync 안내)
      - "cross-repo-label-sync.yml (자동)"             # Wave 2 wire 시점부터 workflow 자동 audit comment
    auto_mirror: false

  - prefix: "[codex-sandbox-fallback]"          # NEW in v1.5 (CFP-1368 / ADR-052 Amendment 14 + ADR-070 Amendment 8 + ADR-081 Amendment 7)
    phase: codex-sandbox-fallback
    current_owner: "core wrapper (Orchestrator 직접 게시 — ADR-052 Amendment 8 fallback_skip_with_marker substitution path 활성 시 Story §10 안 audit trail marker, 1 회/spawn)"
    target_owner_plugin: "core wrapper (Orchestrator monopoly — fix-event-v1 contract ADR-039 §결정 7 §10 invariant 정합)"
    scope: "ADR-052 Amendment 8 fallback_skip_with_marker substitution path 활성 시 Story §10 안 audit trail marker. fail-mode enum 9-set (ADR-070 §결정 D1 SSOT cross-ref: api_missing / version_skew / enterprise_blocked / gh_api_network_blocked / manual_substitution_declared / inline_orchestrator_verify_only / subagent_recursion_blocked / dispatch_stall_or_stream_timeout / codex_truncated_no_verdict) 안 1 value 인용 의무. **lint logic source-of-truth** = `scripts/lib/check_codex_fallback_tally.py` (CFP-1368 Wave 2 carrier) — codex-fallback-subclass-tally check 의 mechanical SSOT cross-validate target. 10번째 enum candidate `codex_sandbox_path_blocked` = Out-of-scope (별 follow-up CFP, ADR-064 §결정 1 scope unitary). semantic adequacy 검증 불가 (grep-only) — reviewer responsibility, false-positive risk 명시."
    example: "[codex-sandbox-fallback: codex_truncated_no_verdict] Codex worker `Touchpoint #2 ArchitectAgent §3 review` spawn 후 output 0 bytes / 1 tool_use / 173s / 57767 tokens → empty verdict. ADR-052 Amendment 8 `fallback_skip_with_marker` substitution path 활성 — verdict 없이 fail-mode 박제 + Orchestrator inline verify 진행."
    posters:
      - Orchestrator                                  # ADR-052 Amendment 8 fallback_skip_with_marker 활성 시 직접 게시 (substitution path 1 회/spawn)
    auto_mirror: false

  - prefix: "[codex-substitution-scope-declared]" # NEW in v1.5 (CFP-1368 / ADR-052 Amendment 14 + ADR-070 Amendment 8 + ADR-081 Amendment 7)
    phase: codex-substitution-scope-declared
    current_owner: "core wrapper (Orchestrator 직접 게시 — ADR-052 Amendment 8 manual_substitution_declare substitution path 활성 시 Story §10 안 audit trail marker, 1 회/spawn)"
    target_owner_plugin: "core wrapper (Orchestrator monopoly — fix-event-v1 contract ADR-039 §결정 7 §10 invariant 정합)"
    scope: "ADR-052 Amendment 8 manual_substitution_declare substitution path 활성 시 Story §10 안 audit trail marker. substitution scope enum 3-set (inline_orchestrator_verify default / manual_substitution_declare / fallback_skip_with_marker — ADR-052 Amendment 8 SSOT cross-ref) 안 1 value 인용 의무. **lint logic source-of-truth** = `scripts/lib/check_codex_fallback_tally.py` (CFP-1368 Wave 2 carrier) — codex-fallback-subclass-tally check 의 mechanical SSOT cross-validate target. inline_orchestrator_verify (default behavior) = marker 부재 case — declare 의무 없음 (Story §10 invariant 정합). semantic adequacy 검증 불가 (grep-only) — reviewer responsibility, false-positive risk 명시."
    example: "[codex-substitution-scope-declared: manual_substitution_declare] Codex TP#4 spawn 후 Orchestrator 가 ADR-052 line 812 + ls docs/observability/+kpi/ + wc comment-prefix-registry-v1.md + grep codex markers + grep bypass-justification 5건 ground truth direct file Read verify 후 5 finding resolution status manual-decided. inline_orchestrator_verify default 영역 외 — Codex TP#4 finding semantic 가 Story file multiple sections cross-cutting 영역."
    posters:
      - Orchestrator                                  # ADR-052 Amendment 8 manual_substitution_declare 활성 시 직접 게시 (substitution path 1 회/spawn)
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
| **CFP-139** | **v1.1** | **MINOR bump** — `[GitOps]` prefix 추가 (GitOpsAgent self-write 영역, codeforge-pmo plugin sibling teammate). ADR-160 carrier. Append-only for v1.x rule 정합. 11 → 12 phase prefix taxonomy. |
| **CFP-658** | **v1.2** | **MINOR bump** — `[SECURITY-FALLBACK]` prefix 추가 (manual fallback path audit-trailed channel, fallback:manual label 부착 PR scope). ADR-027 Amendment 2 carrier. Append-only for v1.x rule 정합. 12 → 13 phase prefix taxonomy. label-registry-v2 v2.12 changelog declaration ↔ comment-prefix-registry-v1 entry 양 channel 정합 (`F-CDX-004` 해소). [verified-via: git show origin/main:docs/inter-plugin-contracts/comment-prefix-registry-v1.md] |
| **CFP-845** | **v1.3** | **MINOR bump** — `[bypass-justification]` prefix 추가 (hotfix-bypass:* label 부착 PR 의 narrative audit trail mechanical enforce carrier, ADR-024 Amendment 8 §결정 6.A.4). Append-only for v1.x rule 정합. 13 → 14 phase prefix taxonomy. `bypass-justification-marker.yml` workflow (CFP-845 Phase 2 carrier) 의 grep-presence lint 가 본 prefix 단일 source. semantic adequacy 불가 (grep-only) — false-positive risk 명시, reviewer responsibility. self-meta loop 회피 = `hotfix-bypass:bypass-justification-marker` 부착 PR (38번째 family member, ADR-024 Amendment 8) 은 marker presence check skip. [verified-via: git show origin/main:docs/inter-plugin-contracts/comment-prefix-registry-v1.md — v1.2 active 확인 후 v1.3 MINOR bump] |
| **CFP-1336** | **v1.4** | **MINOR bump** — `[CROSS-REPO-SYNC]` prefix 추가 (cross-repo bidirectional label sync workflow audit channel, `templates/github-workflows/cross-repo-label-sync.yml` Wave 2 wire 의 audit comment 대상). ADR-073 Amendment 9 + ADR-082 Amendment 14 + ADR-066 Amendment 4 paired sibling carrier — 3 ADR Amendment 동시 발의 axis disjoint complement 3-set (verify subject layer ADR-073 Amd 9 ↔ write authority layer ADR-082 Amd 14 ↔ PAT scope grant layer ADR-066 Amd 4). Append-only for v1.x rule 정합. 14 → 15 phase prefix taxonomy. 3-purpose channel (warning / skip / sync 완료 audit) — Wave 2 wire 후 cross-repo-label-sync.yml workflow 자동 게시 + Orchestrator 직접 게시 양 channel. CFP-1302 D-4 chief tie-break dissent carry-over F2 carrier. [verified-via: git show origin/main:docs/inter-plugin-contracts/comment-prefix-registry-v1.md — v1.3 active 확인 + 14 prefix entry count 후 v1.4 MINOR bump, 2026-05-24 KST origin/main d24ab28] |
| **CFP-1368** | **v1.5** | **MINOR bump (2-entry atomic append)** — `[codex-sandbox-fallback]` + `[codex-substitution-scope-declared]` 2 prefix 동시 추가 (ADR-052 Amendment 8 substitution path 3-enum cross-matrix audit channel — fallback_skip_with_marker activation + manual_substitution_declare activation 양 marker, 1 회/spawn invariant). ADR-052 Amendment 14 (CFP-1286 Wave 2 mechanical wire) + ADR-070 Amendment 8 (fail-mode enum 9-set declaration source) + ADR-081 Amendment 7 (Codex worker prompt boilerplate verify-before-trust scope) paired sibling carrier. Append-only for v1.x rule 정합. 15 → 17 phase prefix taxonomy (2-entry batch atomic, single MINOR bump 영역). **lint logic SSOT cross-validate** — `scripts/lib/check_codex_fallback_tally.py` (CFP-1368 Wave 2 carrier) 의 mechanical source-of-truth (codex-fallback-subclass-tally check). PIVOT-5 NEW Q5 (a) atomic 채택 — registry MISSING (Codex TP#4 F-5 self-stale 203 lines/v1.3 claim 정정 by Orchestrator FIX iter 1 ground truth re-verify, actual 219 lines/v1.4 active + grep codex markers 0 matches → register codify mandatory) 영역 closing-the-loop. self-meta loop 회피 = `hotfix-bypass:codex-fallback-tally` 부착 PR (90~92번째 family member depending on sibling Bundle B coordination — CFP-1306=v2.66 / CFP-1367=v2.67 / CFP-1368=v2.68 sequence) 안 lint step skip. [verified-via: git show origin/main:docs/inter-plugin-contracts/comment-prefix-registry-v1.md — v1.4 active 확인 + 15 prefix entry count + grep both codex markers = 0 matches MISSING 후 v1.5 MINOR bump 2-entry atomic, 2026-05-25 KST origin/main 249a30f] |
