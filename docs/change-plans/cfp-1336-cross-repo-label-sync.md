---
key: CFP-1336
title: Cross-repo bidirectional label sync — wrapper Story Issue ↔ impl repo PR labels (ADR-073 Amd 10 + ADR-082 Amd 14 + ADR-066 Amd 4, FIX iter 5 FINAL)
slug: cfp-1336-cross-repo-label-sync
story: CFP-1336
author: ArchitectAgent (chief author, codeforge-design)
created: 2026-05-24
type: change-plan
date: 2026-05-24
github_issue: mclayer/plugin-codeforge#1336
related_story: docs/stories/CFP-1336.md
owner_lane: design
phase: Phase 1
status: Draft
related_adrs:
  - ADR-073   # Amendment 9 신설 — transition trigger enum 9번째 `label_change` (declaration source, axis = Orchestrator self-assertion verify)
  - ADR-082   # Amendment 14 신설 — §결정 1 layer 1 sub-scope 1-D cross-repo label-write authority (declaration source, axis = internal lane agent self-write authority). FIX iter 4 FINAL — Amendment slot history: spawn Amd 8 → iter 1 Amd 10 → iter 2 Amd 12 → iter 3 Amd 13 → iter 4 Amd 14 FINAL (Amd 8 → 10 → 12 → 13 → 14 history, 5 collisions, CFP-1390 mid-DesignReview spawn collision 추가) (ADR-067 max 3/3 cap EXCEED + user explicit "다음 작업 끝까지 수행해" continuation override)
  - ADR-066   # Amendment 4 신설 — §결정 2 scope minimum 6번째 entry `cross-repo-target-repos issues:write (label endpoint)` (declaration source, axis = PAT scope minimum)
  - ADR-085   # active_sessions[] dual carrier (cross-ref only — coordination axis)
  - ADR-027   # Amendment 2 (Enterprise fallback) — PAT 부재 graceful degradation 정합 (cross-ref only)
  - ADR-068   # Amendment 2 chief tie-break ladder — D-4 dissent carry-over rationale (cross-ref only)
  - ADR-024   # Amendment N (cross-repo-label-sync 75번째 hotfix-bypass family member, per-entry namespace) — declaration source for label-registry-v2 v2.54 sibling carrier
  - ADR-079   # KST timestamp display layer — sync timestamp display KST `+09:00` (cross-ref only)
  - ADR-040   # Amendment 3 §결정 7.D self-application Wave 1→Wave 2 progression chain (cross-ref only)
  - ADR-058   # §결정 5 sunset_justification ratchet 차단 logic (Amendment 9/8/4 모두 ratchet 강화 정합)
  - ADR-064   # §결정 1 CFP scope unitary (Wave 1 declarative + Wave 2 mechanical wire 분리 정합)
related_files:
  - templates/github-workflows/cross-repo-label-sync.yml  # (신규 — Wave 2 mechanical wire 별 carrier, Phase 1 = SSOT declare only)
  - docs/adr/ADR-073-orchestrator-verify-before-assert.md  # Amendment 9 append (frontmatter amendments[] entry 9 + 본문 §Amendment 9 + §결정 1-A 표 9번째 row + mechanical_enforcement_actions[] 4번째 entry + related_stories[] append)
  - docs/adr/ADR-082-write-time-self-write-verification-mandate.md  # Amendment 14 append (frontmatter amendments[] entry 14 + amendment_log[] entry 14 + 본문 §Amendment 14 + §결정 1 layer 1 sub-scope 1-D 표 4번째 row + related_stories[] append). Amendment slot history: spawn Amd 8 → iter 1 Amd 10 → iter 2 Amd 12 → iter 3 Amd 13 → iter 4 Amd 14 FINAL (Amd 8 → 10 → 12 → 13 → 14 history, 5 collisions, CFP-1390 mid-DesignReview spawn collision 추가).
  - docs/adr/ADR-066-pat-rotation-policy.md  # Amendment 4 append (frontmatter amendments[] entry 4 + 본문 §Amendment 4 + §결정 2 scope minimum 표 6번째 row)
  - docs/adr/ADR-RESERVATION.md  # amendments_reserved[] sub-tree 3 row append (ADR-073 Amd 9 + ADR-082 Amd 14 + ADR-066 Amd 4)
  - docs/security/pat-rotation-log.md  # 4번째 row placeholder append (CFP-1336 scope add — issues:write label endpoint)
  - docs/inter-plugin-contracts/label-registry-v2.md  # v2.53 → v2.54 MINOR (`hotfix-bypass:cross-repo-label-sync` 75번째 family + cross-repo bidirectional sync semantics annotation)
  - docs/inter-plugin-contracts/comment-prefix-registry-v1.md  # v1.3 → v1.4 MINOR (`[CROSS-REPO-SYNC]` 15번째 prefix entry append)
  - docs/inter-plugin-contracts/MANIFEST.yaml  # registries[label_registry] v2.53 → v2.54 mirror + comment-prefix-registry-v1 v1.3 → v1.4 mirror
  - docs/evidence-checks-registry.yaml  # `cross-repo-label-sync` warning-tier entry append (deferred-followup, declarative anchor only, Wave 2 별 sub-CFP mechanical wire)
  - docs/parallel-work/section-ownership.yaml  # 본 Change Plan + 3 ADR amendments + 5 registry/CLAUDE.md target rows append
  - CLAUDE.md  # Verify-before-trust 4-layer governance 단락 ADR-073 Amd 9 + ADR-082 Amd 14 cross-ref + GitHub Workflow 단락 cross-repo-label-sync.yml 신규 entry + CODEFORGE_CROSS_REPO_PAT rotation policy 단락 ADR-066 Amd 4 cross-ref
  - docs/stories/CFP-1336.md  # §3 / §7 / §11 / §13 mirror (chief author scope, ArchitectAgent direct write per CFP-40)
review_lane_inputs:
  - SecurityArchitectAgent: §7.1-§7.3 / §7.5-§7.6 (full content draft verbatim integration)
  - InfraOperationalArchitectAgent: §7.4 운영 리스크 (full content draft verbatim integration)
  - TestContractArchitectAgent: §8 (5 invariants + AC coverage matrix verbatim integration)
  - ArchitectAnalystAgent: §2 (existing design fact + prior art) + §9 alternatives
verdict_packet_self_check:
  mechanical_self_check_passed: true
  boundary_completeness_self_check_passed: true
  dimensional_empirical_self_check_passed: true
  audit_gate_pointer_self_check_passed: true
  marketplace_sync_declared: true   # marketplace_sync_required = false (mirrored field 변경 0, plugin.json 변경 0)
pre_lookup_evidence:
  origin_main_sha: "d24ab283024bba81ab380ceb703c4ce58eb7026c"   # git rev-parse origin/main post-spawn re-pin (initial spawn pin = 0d40cd0 → mid-spawn CFP-1369 lint cleanup land → re-verify d24ab28)
  last_git_fetch_timestamp: "2026-05-24T19:00:00+09:00"  # KST per ADR-079
  verified_files:
    - { path: "docs/adr/ADR-073-orchestrator-verify-before-assert.md", verified_via: "git show origin/main:... | grep amendment_id (8 entries verified)", note: "amendment_log[] max amendment_id = 8 (Amd 8 = CFP-1348 mcp_token_expired_mid_flight). next_slot M = 9." }
    - { path: "docs/adr/ADR-082-write-time-self-write-verification-mandate.md", verified_via: "git show origin/main:... | grep amendment_id (7 entries verified at spawn / 13 entries verified post-iter4 origin/main 4e341e5 — CFP-1390 Amd 13 mid-DesignReview spawn collision)", note: "spawn-time amendment_log[] max amendment_id = 7 (Amd 7 = CFP-1312 §결정 9 양방향 verify-before-cite, next_slot M = 8) → mid-flight CFP-1329/1330/1332/1338/1339/1390 land collision (8/9/10/11/12/13) → FIX iter 4 renumber to Amd 14 FINAL (origin/main 4e341e5 max=13 → next_slot = 14, ADR-067 max 3/3 cap EXCEED + user explicit continuation override). Amd 8 → 10 → 12 → 13 → 14 history, 5 collisions." }
    - { path: "docs/adr/ADR-066-pat-rotation-policy.md", verified_via: "git show origin/main:... | grep amendment: (max=3 verified)", note: "amendments[] max amendment id = 3 (Amd 3 = CFP-743 reconcile-target-repos contents:write + pull_requests:write). next_slot M = 4." }
    - { path: "docs/inter-plugin-contracts/label-registry-v2.md", verified_via: "git show origin/main:... | grep -c '^  - name: hotfix-bypass:' (73 family verified)", note: "current frontmatter version = 2.52. next hotfix-bypass family ordinal = 74." }
    - { path: "docs/inter-plugin-contracts/comment-prefix-registry-v1.md", verified_via: "git show origin/main:... (version 1.3 verified + 14 prefix entries)", note: "current version = 1.3. next prefix entry ordinal = 15." }
    - { path: "docs/adr/ADR-RESERVATION.md", verified_via: "git show origin/main:... amendments_reserved[] tail = 11 rows (ADR-83 Amd 3 + ADR-82 Amd 7 + ADR-39 Amd 2 + ADR-39 Amd 3 + ADR-71 Amd 7 + ADR-82 Amd 8/9/10/11/12 batch + 본 row)", note: "본 carrier = 3 row append (ADR-73 Amd 9 + ADR-82 Amd 14 + ADR-66 Amd 4 all status:active, ArchitectAgent commit time 점유 precedent). Amendment slot history: spawn Amd 8 → iter 1 Amd 10 → iter 2 Amd 12 → iter 3 Amd 13 → iter 4 Amd 14 FINAL (Amd 8 → 10 → 12 → 13 → 14 history, 5 collisions, CFP-1390 mid-DesignReview spawn collision 추가)." }
---

# Change Plan — CFP-1336: Cross-repo bidirectional label sync

### §1. 목적

본 Change Plan = **cross-repo wrapper Issue ↔ impl repo PR labels bidirectional sync** 영역의 governance SSOT codify. CFP-1302 D-4 chief tie-break dissent (within-repo GITHUB_TOKEN only 결정 시 cross-repo path 별 carrier 분리) 정합의 axis-disjoint follow-up F2 carrier.

**Wave 1 declarative scope** (본 carrier):

1. **ADR-073 Amendment 9 신설** — `label_change` 9번째 transition trigger enum entry. cross-repo label change event 시점 Orchestrator (또는 subagent) verify-before-assert 4-step mandate (git fetch + gh api direct + active_sessions[] dual-source AND + verified-via annotation).
2. **ADR-082 Amendment 14 신설** — §결정 1 layer 1 sub-scope 1-D `cross-repo label-write authority` 신설. internal lane agent 가 cross-repo label state 변경 직전 write authority 4-tuple 검증 의무 (a) wrapper → impl write 권한 (CODEFORGE_CROSS_REPO_PAT `issues:write` 정합) / (b) impl → wrapper write 권한 (sender.type ≠ Bot OR actor allowlist 정합) / (c) cross-org sync 차단 (mclayer org only) / (d) verified-via annotation 의무.
3. **ADR-066 Amendment 4 신설** — §결정 2 scope minimum 6번째 entry `cross-repo-target-repos issues:write (label endpoint)` 추가. 기존 5 scope 위 6번째 scope grant (least-privilege invariant — cross-repo-target-repos `mclayer/plugin-codeforge` ↔ impl repo 한정, org-wide write 금지, action = `issues:write` (label endpoint) 1종만). 단일 PAT consolidation 무변경 (ADR-013 Amendment 4 정합).
4. **신규 workflow template** — `templates/github-workflows/cross-repo-label-sync.yml` (Wave 1 = declarative skeleton only, Wave 2 mechanical wire 별 sub-CFP carrier).
5. **label-registry-v2 v2.54 MINOR** — `hotfix-bypass:cross-repo-label-sync` 75번째 family member append + cross-repo bidirectional sync semantics annotation.
6. **comment-prefix-registry-v1 v1.4 MINOR** — `[CROSS-REPO-SYNC]` 15번째 prefix entry append (warning 안내 / skip 표시 / sync 완료 audit channel).
7. **evidence-checks-registry warning-tier entry append** — `cross-repo-label-sync` deferred-followup status (Wave 1 declarative anchor only).

**Wave 2 mechanical wire 별 sub-CFP carrier** (본 Story scope 외): workflow 실 활성 + repository_dispatch listener seed (impl repo) + rate-limit telemetry + PAT rotation automation + bats fixture pair + lint script binding.

Forcing function: cross-repo label drift (wrapper Story Issue 가 phase:구현 부착인데 impl repo Phase 2 PR 은 phase:설계 잔존) 차단 → Story workflow 자동 진행 (label-driven lane spawn) 신뢰성 확보 → ADR-087 / ADR-088 deploy lane forward-compat (phase:배포 / phase:배포-리뷰 label seed 등록 시점 자동 활성).

---

### §2. 현재 구조 (CodebaseMapperAgent / ArchitectAnalyst integration)

**Mapper input 부재** (본 Story = ArchitectAgent direct chief author flow, deputy spawn 0). ArchitectAnalystAgent prior art + CodebaseMapper 영역의 chief 통합 검증:

### §2.1 cross-repo write 영역의 현 SSOT

| 영역 | 현 상태 | 본 Change Plan 영향 |
|---|---|---|
| **cross-repo READ** (within-repo PR + cross-repo Story file fetch) | `templates/github-workflows/phase-gate-mergeable.yml` (precedent — `CODEFORGE_CROSS_REPO_PAT` Authorization header + native `fetch()`, lines 24-30 / 60-90 / 214-271 / 486+ verified-via Read worktree origin/main) | **변경 0** (READ path 보존, 본 Change Plan = WRITE 영역 신설 별 workflow, T-2 self-trigger 차단 native 영역 보존) |
| **cross-repo WRITE** (label state mutation) | **부재** — 현 codeforge family 의 cross-repo write workflow 0건 (`phase-gate-mergeable.yml` / `rate-limit-fallback-kpi.yml` / `marketplace-drift-detection.yml` 3 workflow 모두 read-only fetch only). 단 `UpgradeAgent` reconcile (CFP-743 Amendment 3 §결정 2 추가 5번째 scope `reconcile-target-repos contents:write + pull_requests:write`) 가 consumer repo 측 PR open 경유 cross-repo content write 의 *유일* precedent (ADR-066 §결정 2 scope minimum 안). | **신규 영역 codify** — workflow + ADR-066 Amendment 4 6번째 scope `cross-repo-target-repos issues:write` (label endpoint 1종만) 추가, reconcile-target-repos pattern 답습 (target = wrapper ↔ impl repo 한정 — org-wide write 절대 금지) |
| **ADR-073 transition trigger enum** | 8 entries (`lane_spawn` / `pr_open` / `merge_transition` / `worktree_lane_spawn` / `fix_iter_start` / `sibling_story_handoff` / `stale_local_main_checkout` / `mcp_token_expired_mid_flight`) verified-via origin/main d24ab28. **closed_enum: open_extension:false** (Amendment 강화 방향만 ratchet, ADR-058 §결정 5 정합) | **9번째 entry `label_change` append** — closed-set ratchet 강화. cross-repo label change event 시점 verify-before-assert 의무. |
| **ADR-082 §결정 1 layer 1 sub-scope** | 3 sub-scope (1-A lane spawn cross-repo state / 1-B Orchestrator-authored Issue body claim / 1-C lane PL spawn prompt user-utterance verbatim anchor). | **4번째 sub-scope 1-D append** — internal lane agent 의 cross-repo label-write authority 4-tuple verify 의무. axis disjoint with 1-A/1-B/1-C (cross-repo label-write 영역 신설). |
| **ADR-066 §결정 2 scope minimum** | 5 scope (`repo:read` / `repo:write` / `metadata:read` / `marketplace contents:read` / `reconcile-target-repos contents:write + pull_requests:write`). 단일 PAT consolidation (ADR-013 Amendment 4). | **6번째 scope append** — `cross-repo-target-repos issues:write (label endpoint)`. target = wrapper-self↔impl repo 한정 (`mclayer/plugin-codeforge` ↔ impl repo, fine-grained PAT repository access list 강제). action = `issues:write` (label endpoint) 1종만 — workflows:write / contents:write / admin 등 escalation scope 미부여. |
| **label-registry-v2 hotfix-bypass family** | 74 entries verified-via origin/main grep count. current version = 2.53 (CFP-1346 v2.54 = 75번째 `hotfix-bypass:label-registry-frozen-baseline-count-parity`). | **75번째 entry `hotfix-bypass:cross-repo-label-sync` append + v2.54 MINOR**. cross-repo sync semantic annotation 동반. |
| **comment-prefix-registry-v1 prefix taxonomy** | 14 entries (v1.0 11 → v1.1 GitOps → v1.2 SECURITY-FALLBACK → v1.3 bypass-justification). | **15번째 entry `[CROSS-REPO-SYNC]` append + v1.4 MINOR**. warning 안내 / skip 표시 / sync 완료 audit 3-purpose. |
| **evidence-checks-registry entries** | 95+ entries (last visible: `mcp-token-freshness-precheck` CFP-1348 Wave 1 — deferred-followup, declarative anchor only, schema v1.3). | **96번째 entry `cross-repo-label-sync` append (warning tier, deferred-followup)** — Wave 1 declarative anchor only. ADR-073 Amendment 9 declaration source / ADR-060 enforcement source dual-binding (CFP-1348 `mcp-token-freshness-precheck` precedent verbatim 답습). |

### §2.2 prior art (ArchitectAnalyst 산출물 통합)

- **CFP-1302** (closed, gate:retro-complete verified-via `gh issue view 1302 --json state,labels`): `phase-gate-auto-cleanup.yml` workflow (within-repo + GITHUB_TOKEN only, T-2 self-trigger 차단 native). D-4 chief dissent 영역 외 cross-repo path 별 carrier 분리 — 본 CFP-1336 = D-4 dissent carry-over 정합.
- **CFP-1348** (merged 2026-05-24, ADR-073 Amendment 8 `mcp_token_expired_mid_flight` 8번째 transition trigger entry). 본 CFP-1336 = Amendment 8 sibling-merged 직후 발의 Amendment 9 (max+1 정확 next-slot, ADR-082 §결정 9 verify-before-cite forward 양방향 정합).
- **CFP-1312** (closed, PR #1352 MERGED 2026-05-23 KST): ADR-082 Amendment 7 §결정 9 양방향 verify-before-cite 확장. 본 CFP-1336 ADR-082 Amendment 14 = sibling-merged 직후 발의 (verify-before-cite mechanical lint check (b) coverage 정합 — sub-scope 1-D 신설은 backward-staleness 영역 외).
- **CFP-743 Amendment 3 — ADR-066 §결정 2 reconcile-target-repos scope grant**: cross-repo write scope 추가 precedent. 본 CFP-1336 = 동일 패턴 답습 — fine-grained PAT repository access list + action 1종만 (least-privilege invariant 보존).
- **peter-evans/repository-dispatch action**: 산업 표준 PAT-based cross-repo workflow trigger (Tier B 채택 근거). 본 Change Plan §3.3 workflow yaml 안 SHA-pinned 3rd-party action 사용 (CFP-300 action SHA pin policy 정합).

### §2.3 architecture doc 4 영역 mapping (ADR-078 / §결정 1 gate 정합)

| 영역 | 본 Change Plan 영향 | 갱신 의무 발동 |
|---|---|---|
| **modules** | 신규 module 0 (governance metadata layer only) | **none_rationale** declared (architecture doc N/A 영역) |
| **boundaries** | cross-repo trust boundary 신설 (wrapper repo ↔ impl repo, PAT-mediated WRITE) | **본 Change Plan §7.1 + Story §7 mirror 가 SSOT** (architecture doc 별 mirror 의무 영역 외 — Wave 1 declarative scope 한정) |
| **interfaces** | repository_dispatch payload schema 신설 (`event_type: cross-repo-label-sync`, 5-field client_payload, Wave 2 schema active wire) | **본 Change Plan §4 = SSOT** (Wave 2 mechanical wire 시 inter-plugin-contracts 신규 entry 평가, 본 Wave 1 scope 외) |
| **data_flow** | wrapper Issue label change → repository_dispatch sender (wrapper-side workflow) → impl repo listener (Wave 2 carrier) → impl repo PR label write 의 4-step async flow + 4-pattern T-2 guard | **본 Change Plan §3.2 = SSOT** (architecture doc mirror Wave 2 carrier 평가) |

**architecture_doc_impact (§10.A declarative declare)**: 4 영역 중 1+ touch 가능성 있음 (boundaries / data_flow) but Wave 1 declarative scope 한정으로 architecture doc seed (각 plugin self-owned `docs/architecture/*.md`) 갱신 의무 발동 0 — **none_rationale**: Wave 1 = governance SSOT codify only (workflow / ADR / registry layer), Wave 2 mechanical wire 시 architecture doc S2 sub-Story 평가 (ADR-078 §결정 1 anti-scope guard 정합 — 모듈 / 경계 / 계약 / 흐름 서술 영역, governance metadata 한정 분리).

---

### §3. 도입할 설계 (RefactorAgent / chief synthesis)

### §3.1 ADR-073 Amendment 9 신설

**Scope**: §결정 1 expansion — transition trigger enum 9번째 entry `label_change` 추가 (closed-set ratchet 강화, Amendment 2/3/5/6/7/8 §결정 1-A precedent 답습).

**Trigger** (closed-enum):
- (a) wrapper repo Story Issue label change event (phase:* / gate:* mutation) 직전 + 직후
- (b) impl repo Phase 2 PR label change event 직전 + 직후
- (c) `cross-repo-label-sync.yml` workflow 의 self-application 직전 (Orchestrator 가 workflow 가 발화 직전 active_sessions[] dual-source verify)
- (d) `gh api repos/<org>/<repo>/issues/<N>/labels` direct call 직전 (label state ground truth verify)

**Verify 의무** (§결정 1-A 9번째 row + §결정 1-M primitive 신설):
1. `git fetch origin main` (wrapper repo 최신 main pin — stale_local_main_checkout Amendment 7 정합)
2. `gh api /repos/<org>/<repo>/issues/<N>/labels` direct verify (cross-repo state ground truth — sender 측 wrapper + receiver 측 impl repo 양 verify)
3. Story §14 Lane Evidence + Story Issue body `active_sessions[]` (ADR-085 §결정 2 dual carrier) 두 source 일치 검증
4. `verified-via: <method>` annotation 의무 (모든 cross-repo state 인용 옆)
5. **T-2 self-trigger 4-pattern AND guard** (cross-repo PAT 사용 영역 의무 invariant):
   - sender.type early-exit (`github.event.sender.type ≠ 'Bot'` OR sender login ≠ PAT actor)
   - actor-allowlist (`github.actor` ∈ allowlist enum)
   - `[skip-cross-repo-sync]` marker grep (Issue/PR body 안 marker 부재)
   - idempotent diff (label set diff ≠ ∅)

**closed_enum: open_extension:false** invariant — 10번째 trigger 추가 시 Amendment 강화 방향만 (ADR-058 §결정 5 정합).

**mechanical_enforcement_actions[] append**: `cross-repo-label-sync` (warning tier, deferred-followup, Wave 2 별 sub-CFP carrier). 기존 4 entry (`parallel-work-sentinel-pickup` / `worktree-self-ownership-verify` / `subagent-sibling-story-polling-evidence` / `mcp-token-freshness-precheck`) 와 동일 패턴 답습.

**Wave 1 declarative anchor only** — actual workflow yml + script + bats fixture + label-registry MINOR bump = sibling carrier (Wave 1 본 Change Plan scope) + 실 lint binding = Wave 2 별 sub-CFP carrier (`parallel-work-sentinel-pickup` Wave 2 deferred-followup precedent 답습).

### §3.2 ADR-082 Amendment 14 신설

**Scope**: §결정 1 layer 1 sub-scope (1-D) cross-repo label-write authority 신설 (1-A/1-B/1-C 와 axis disjoint).

| sub-scope | trigger | verify 의무 |
|---|---|---|
| (1-A) lane spawn / cross-repo state assertion | lane 진입 시 외부 state 단정 | `git fetch origin` + `git show origin/main:<path>` + `verified-via` (Wave 1 = ADR-073) |
| (1-B) Orchestrator-authored Issue body claim | retro time / brainstorm Phase 0 후속 / ADR amendment carrier reservation | Issue body 안 모든 claim source direct verify 후 author (Wave 1 = Amendment 2) |
| (1-C) Orchestrator-authored lane PL spawn prompt | Orchestrator 가 lane PL agent 를 spawn 할 때 | spawn prompt 첫 줄 `[USER-UTTERANCE-VERBATIM]` block 의무 (Wave 1 = Amendment 5) |
| **(1-D) cross-repo label-write authority** | **internal lane agent / workflow listener 가 cross-repo label state mutation 직전** | **4-tuple write authority verify 의무 (아래)** |

**§결정 1-D primitive (4-tuple AND)**:

(a) **wrapper → impl write 권한**: cross-repo label-sync workflow 가 wrapper Story Issue label change event 수신 → impl repo PR label sync write 직전, **CODEFORGE_CROSS_REPO_PAT scope = `cross-repo-target-repos issues:write` (label endpoint) verify** (ADR-066 §결정 2 Amendment 4 정합 — 6번째 scope grant). PAT scope ≠ 6번째 entry 정합 시 fail-closed exit 0 (graceful skip + audit comment).

(b) **impl → wrapper write 권한**: impl repo PR label change event 수신 → wrapper Story Issue label sync write 직전, **(b-1) sender.type early-exit** (`github.event.sender.type == 'Bot'` AND sender login == PAT actor → exit 0, T-2 self-trigger 차단) + **(b-2) actor-allowlist** (`github.actor` ∈ allowlist enum, e.g., `CODEFORGE_CROSS_REPO_PAT` owner login `mccho` / dependabot[bot] 등 known-bot 한정) verify.

(c) **cross-org sync 차단**: workflow level check (`github.repository_owner == 'mclayer'` strict — mclayer org only). external-org/* 시 즉시 fail with `[CROSS-REPO-SYNC: cross-org out-of-scope]` Issue comment.

(d) **verified-via annotation 의무**: cross-repo label state 인용 시 (Story §10 FIX Ledger / §14 Lane Evidence / Change Plan §3 / ADR Amendment 본문 등) `verified-via: <method>` annotation 부착 의무 — `gh api repos/.../issues/<N>/labels --jq '.[].name'` 직접 cite (working tree / cache 우회).

**Wave 1 = behavioral mandate** (lane agent / workflow listener self-discipline forcing function). Wave 2 mechanical lint (`scripts/check-cross-repo-label-write-authority.sh`) = 별 sub-CFP carrier (deferred-followup, brainstorm 단계 결정).

**axis disjoint cross-ref**:
- **ADR-082 sub-scope 1-A** (lane spawn cross-repo state assertion) ↔ **1-D** (cross-repo label-write authority): 1-A = read direction (state 단정 verify) / 1-D = write direction (state mutation authority verify). 양 disjoint.
- **ADR-073 Amendment 9** (cross-repo state Orchestrator verify, transition trigger `label_change` 9번째 entry) ↔ **ADR-082 Amendment 14 sub-scope 1-D** (internal lane agent self-write authority verify): ADR-073 = Orchestrator 행위 한정 (cross-repo state 단정 verify) / ADR-082 sub-scope 1-D = internal lane agent self-write 한정 (cross-repo label-write authority verify). 동일 cross-repo event 시점 두 layer 동시 적용 — verify subject disjoint (Orchestrator self-assertion ↔ lane agent self-write authority).
- **ADR-085 §결정 2 active_sessions[] dual carrier** (coordination axis): pre-hoc cross-session ownership coordination 영역. 본 Amendment 14 sub-scope 1-D = post-hoc self-write authority verify 영역. 양 disjoint complement (Amendment 3 ADR-085 cross-ref pattern 답습).

### §3.3 workflow template `cross-repo-label-sync.yml` 신설 (Wave 1 = declarative skeleton)

**File**: `templates/github-workflows/cross-repo-label-sync.yml`

**Status**: Phase 1 declarative skeleton only — Wave 2 별 sub-CFP carrier 가 (a) trigger event binding (`issues.labeled` / `pull_request.labeled` event) + (b) repository_dispatch sender step + (c) impl repo listener seed + (d) self-trigger 4-pattern AND guard 실 활성 + (e) bats fixture pair + (f) lint script binding 신설.

**Skeleton form** (Phase 1 SSOT declare 후 Wave 2 carrier 가 hydrate):

```yaml
# templates/github-workflows/cross-repo-label-sync.yml
# Status: Wave 1 declarative skeleton (CFP-1336 / ADR-073 Amendment 9 + ADR-082 Amendment 14 carrier)
# Phase: Declaration only — Wave 2 별 sub-CFP carrier 가 trigger event binding + step hydration + bats fixture pair + lint script
# 4-pattern T-2 self-trigger guard AND invariant (AC-2 / Change Plan §7.2 T-2 mitigation)
# CODEFORGE_CROSS_REPO_PAT scope = cross-repo-target-repos issues:write (ADR-066 Amendment 4 §결정 2 6번째 entry)
# Reference: peter-evans/repository-dispatch action SHA pin (Wave 2 carrier 가 actual SHA pin)
# verify-before-assert 4-step mandate (ADR-073 Amendment 9 §결정 1-A 9번째 row label_change trigger)

name: cross-repo-label-sync  # Wave 1 declare — Wave 2 wire 시 actual trigger event binding
on:
  workflow_dispatch:  # Wave 1 = manual-only (Wave 2 actual = issues.labeled / pull_request.labeled)
permissions:
  contents: read   # default least-privilege
  issues: read     # Wave 2 wire 시 cross-repo PAT 가 issues:write scope override
  pull-requests: read

concurrency:
  group: cross-repo-label-sync-${{ github.event.issue.number || github.event.pull_request.number }}
  cancel-in-progress: false   # ordering invariant — race window 안 last-write-wins (AC-5)

jobs:
  cross-repo-label-sync:
    # Wave 1 = declarative skeleton (no actual steps wire). Wave 2 carrier 가 hydrate.
    runs-on: ubuntu-latest
    if: ${{ github.repository_owner == 'mclayer' }}   # cross-org sync 차단 (ADR-082 sub-scope 1-D (c))
    steps:
      - name: Wave 1 declarative skeleton placeholder
        run: |
          echo "::notice::cross-repo-label-sync.yml Wave 1 declarative skeleton — Wave 2 별 sub-CFP carrier 가 trigger event binding + step hydration + bats fixture pair + lint script binding."
          echo "verify-before-assert 4-step (ADR-073 Amd 9 §결정 1-A 9th row label_change) = Wave 2 wire."
          echo "4-pattern T-2 self-trigger guard AND = Wave 2 wire (sender.type / actor-allowlist / [skip-cross-repo-sync] marker / idempotent diff)."
          echo "CODEFORGE_CROSS_REPO_PAT scope = cross-repo-target-repos issues:write (ADR-066 Amd 4 §결정 2 6th entry) = Wave 2 actual grant verify-before-trust."
```

**Wave 2 carrier (`scripts/check-cross-repo-label-sync.sh` + workflow hydration + bats fixture pair)** 가 actual:
- `peter-evans/repository-dispatch@<SHA pin>` Tier B sender step
- impl repo listener seed (별 cross-repo PR carrier)
- 4-pattern T-2 guard AND step (sender.type / actor-allowlist / marker grep / idempotent diff)
- `gh api` direct verify steps (verify-before-assert 4-step)
- Story §14 + active_sessions[] dual-source AND verify step (ADR-085 §결정 2)
- audit comment + `[CROSS-REPO-SYNC]` prefix entry (comment-prefix-registry-v1 v1.4)
- bats fixture pair (cross-org reject / self-trigger 4-pattern guard / idempotent diff)
- evidence-checks-registry entry status: `deferred-followup → warning` 자동 승격 (Wave 2 PR merge 시점)

### §3.4 label-registry-v2 v2.54 → v2.54 MINOR bump

**Append**:
- `hotfix-bypass:cross-repo-label-sync` (color `fef2c0`, category `hotfix-bypass`) — **75번째 hotfix-bypass:* family member**. `templates/github-workflows/cross-repo-label-sync.yml` (Wave 2 carrier) warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment N §결정 6.A per-entry namespace 정합). `evidence-checks-registry cross-repo-label-sync` entry 의 bypass channel.

**Cross-repo bidirectional sync semantics annotation** (label-registry-v2 §3 hotfix-bypass:* category description 영역):

```yaml
- name: hotfix-bypass:cross-repo-label-sync
  category: hotfix-bypass
  color: "fef2c0"
  description: "hotfix-bypass: cross-repo-label-sync warning-tier mechanical lint 조건부 skip + audit comment 자동 발의 (CFP-1336 / ADR-073 Amendment 9 §결정 1-A 9번째 entry label_change + ADR-082 Amendment 14 sub-scope 1-D cross-repo label-write authority + ADR-066 Amendment 4 §결정 2 6번째 scope entry carrier — wrapper Story Issue ↔ impl repo PR labels bidirectional sync workflow self-trigger 4-pattern AND guard fail / dispatch fail / ordering fail bypass channel, evidence-checks-registry cross-repo-label-sync entry 의 bypass channel). 75번째 hotfix-bypass:* family member."
  single_active: false
  attach_owner_plugin: "Orchestrator (CFP-1336 cross-repo bidirectional label sync warning-tier bypass — consumer 환경 임시 skip 시 부착) / DeveloperPLAgent"
```

**v2.54 changelog entry** (label-registry-v2 §변경 이력 head append):

```
**v2.54 (CFP-1336 / ADR-073 Amendment 9 + ADR-082 Amendment 14 + ADR-066 Amendment 4, 2026-05-24)**: MINOR bump (§3 yaml hotfix-bypass:* 75번째 family member append — cross-repo bidirectional label sync workflow self-trigger guard bypass channel).
- 추가: `hotfix-bypass:cross-repo-label-sync` (color `fef2c0`) — `templates/github-workflows/cross-repo-label-sync.yml` (Wave 2 carrier) warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment N §결정 6.A per-entry namespace 정합, 75번째 hotfix-bypass:* family member — origin/main grep count = 74 verified-via 2026-05-24 KST). CFP-1346 v2.53 (74번째 hotfix-bypass:label-registry-frozen-baseline-count-parity) 직후 sequential MINOR.
- 동반: comment-prefix-registry-v1 v1.3 → v1.4 (`[CROSS-REPO-SYNC]` 15번째 prefix), evidence-checks-registry `cross-repo-label-sync` warning-tier entry append (deferred-followup, declarative Wave 1).
- kind:registry sibling sync 면제 (ADR-010 §결정 2 + ADR-008 §결정 3 row append). plugin.json bump 0 = marketplace_sync_declared: false (mirrored field 변경 0건).
- MANIFEST.yaml row `2.52` → `2.53` ratchet 동반.
- ADR-008 §결정 3 SSOT: 신규 label entry append = MINOR bump (v2.53 → v2.54 MINOR increment).
```

### §3.5 comment-prefix-registry-v1 v1.3 → v1.4 MINOR bump

**Append `[CROSS-REPO-SYNC]` 15번째 prefix entry** (warning 안내 / skip 표시 / sync 완료 audit 3-purpose channel):

```yaml
- prefix: "[CROSS-REPO-SYNC]"
  phase: cross-repo-sync
  current_owner: "cross-repo-label-sync.yml workflow + Orchestrator (Wave 2 wire 후)"
  target_owner_plugin: "core wrapper (Orchestrator 직접 게시 또는 workflow 자동 게시 — cross-repo-label-sync.yml workflow grep-presence audit 대상)"
  scope: "cross-repo bidirectional label sync workflow 의 audit channel comment — (a) warning: PAT 부재 / linked PR 부재 / cross-org reject 시 graceful skip 안내 / (b) skip: 4-pattern T-2 guard AND fail 시 audit trail / (c) sync 완료: bidirectional sync success 시 verified-via annotation 포함 audit"
  example: "[CROSS-REPO-SYNC] 본 PR 은 CODEFORGE_CROSS_REPO_PAT secret 미설정으로 degraded mode — manual label sync required (ADR-027 Amendment 2 fallback:manual 정합, ADR-073 Amendment 9 §결정 1-A 9번째 entry label_change trigger graceful skip)."
  posters:
    - Orchestrator   # Wave 2 wire 후 직접 게시 + workflow automation 동시
    - "cross-repo-label-sync.yml (자동)"   # Wave 2 wire 시점부터
  auto_mirror: false
```

**v1.4 changelog entry** (comment-prefix-registry-v1 §5 변경 이력 head append):

```
| CFP-1336 | v1.4 | MINOR bump — `[CROSS-REPO-SYNC]` prefix 추가 (cross-repo bidirectional label sync workflow audit channel, `templates/github-workflows/cross-repo-label-sync.yml` Wave 2 wire 의 audit comment 대상). ADR-073 Amendment 9 + ADR-082 Amendment 14 carrier. Append-only for v1.x rule 정합. 14 → 15 phase prefix taxonomy. semantic adequacy 불가 (workflow audit channel — Wave 2 wire 후 자동 + Orchestrator 직접 양 channel), reviewer responsibility. [verified-via: git show origin/main:docs/inter-plugin-contracts/comment-prefix-registry-v1.md — v1.3 active 확인 후 v1.4 MINOR bump] |
```

### §3.6 evidence-checks-registry warning-tier entry append (`cross-repo-label-sync`)

declaration source ADR-073 Amendment 9 / enforcement source ADR-060 dual-binding (CFP-1348 `mcp-token-freshness-precheck` precedent verbatim 답습 — Wave 1 declarative anchor only).

```yaml
- name: cross-repo-label-sync
  description: |
    ADR-073 Amendment 9 §결정 1-A (transition trigger enum 9번째 entry `label_change`
    추가, closed-set ratchet 10번째 trigger 추가 시 Amendment 강화 방향만) + §결정 1-M
    (cross-repo label state verify-before-assert 4-step primitive — git fetch + gh
    api direct + active_sessions[] dual-source AND + verified-via annotation) +
    ADR-082 Amendment 14 §결정 1 layer 1 sub-scope (1-D) cross-repo label-write
    authority 4-tuple verify (wrapper→impl write 권한 / impl→wrapper write 권한
    sender.type + actor allowlist / cross-org sync 차단 mclayer org only / verified-via
    annotation 의무) mechanical verification — cross-repo bidirectional label sync
    workflow (`templates/github-workflows/cross-repo-label-sync.yml` Wave 2 carrier)
    의 self-trigger 4-pattern AND guard (sender.type early-exit / actor-allowlist /
    `[skip-cross-repo-sync]` marker / idempotent diff) + verify-before-assert
    4-step + dual-source AND verify (Story §14 Lane Evidence + Story Issue body
    active_sessions[]) presence-grep heuristic.

    Wave 1 declaration anchor only (ADR-064 §결정 1 CFP scope unitary 정합) —
    actual workflow + script + bats fixture pair + impl repo listener seed +
    label-registry MINOR bump = Wave 2 별 sub-CFP carrier 후 Active 전환
    (parallel-work-sentinel-pickup + worktree-self-ownership-verify +
    subagent-sibling-story-polling-evidence + mcp-token-freshness-precheck Wave 2
    deferred-followup precedent 답습).

    sentinel pattern_count 0 (sentinel-driven 아닌 ratchet 확장 carrier — CFP-1302
    D-4 chief dissent carry-over 정합, axis disjoint cross-repo path 별 carrier
    분리). PAT cascade rate-limit 실측 = Wave 2 mechanical wire 시 telemetry 통한
    runtime measurement (ADR-068 Amendment 1 I-5 dimensional empirical grounding
    정합 — Wave 1 = 측정 대상 정의만, Wave 2 = 실측).

    super-class = `cross_repo_label_write_authority_drift` — Amendment 7 git layer
    staleness + Amendment 14 auth layer staleness 와 axis disjoint (label state
    layer, 별 staleness sub-domain).

    ADR-082 §결정 6 + ADR-060 Amendment 10 §결정 24 deferred-followup precedent
    (L1417/L1452/L1574 4-instance + parallel-work-sentinel-pickup L2729 +
    worktree-self-ownership-verify L2898 + subagent-sibling-story-polling-evidence
    L3725 + mcp-token-freshness-precheck L3823 6-instance established pattern)
    답습 — 신규 unique drift value 회피.
  detect_command: bash scripts/check-cross-repo-label-sync.sh   # Wave 2 별 sub-CFP carrier — scripts/check-cross-repo-label-sync.sh (thin wrapper, ADR-061) + scripts/lib/check_cross_repo_label_sync.py (Python SSOT — 4-pattern T-2 guard presence-grep + dual-source AND verify presence-grep + verified-via annotation 의무) 실 file 신설
  workflow: templates/github-workflows/cross-repo-label-sync.yml   # Wave 2 별 sub-CFP carrier — byte-identical self-app .github/workflows/cross-repo-label-sync.yml (ADR-005 parity)
  current_tier: warning           # ADR-060 §결정 5 — 첫 도입 = warning mode
  bypass_label: hotfix-bypass:cross-repo-label-sync   # label-registry-v2 v2.54 75번째 family member 정합
  bypass_audit_lint: bash scripts/check-bypass-audit-comment.sh
  promotion_criteria:
    pr_cumulative_min: 20         # ADR-060 §결정 6 (a) velocity-normalized
    failure_threshold: 0          # ADR-060 §결정 6 (b)
    sibling_dependencies:
      - CFP-1336                  # 본 entry self-carrier (Wave 1 declarative anchor — evidence-checks-registry entry + ADR-073 Amendment 9 + ADR-082 Amendment 14 + ADR-066 Amendment 4 + label-registry-v2 v2.54 + comment-prefix-registry-v1 v1.4)
      # Wave 2 별 sub-CFP — workflow yml hydrate + script + bats + impl repo listener seed + PAT scope grant verify (TBD)
    evidence_artifacts:
      - github_actions_run_history_url
      - lint_failure_count_zero_proof
      - pr_cumulative_count_proof
  modal_anti_pattern_dictionary: {}   # 본 lint = 4-pattern T-2 guard + dual-source AND + verified-via annotation presence-grep, modal phrase 검사 미포함
  introduced_by: CFP-1336
  introduced_date: 2026-05-24
  owner_adr: ADR-073-Amendment-9   # declaration source ADR — §결정 1-A 9번째 entry label_change + §결정 1-M primitive (4-step verify-before-assert) carrier
  carrier_adr: ADR-060             # enforcement source ADR — evidence-enforceable warning-tier framework carrier
  recurrence:
    count: 0                       # sentinel-driven 아닌 ratchet 확장 carrier (CFP-1302 D-4 chief dissent carry-over 정합)
    threshold: 3                   # ADR-060 §결정 19 Amendment 6 / schema v1.2 standard default
    last_occurrence: null
    promotion_trigger: none        # recurrence.count = 0 — sentinel-driven 아님 (ratchet 확장 carrier)
  status: deferred-followup        # Wave 1 declarative anchor only — actual workflow + script + bats fixture pair + impl repo listener seed + PAT scope grant verify = Wave 2 별 sub-CFP carrier (mcp-token-freshness-precheck + subagent-sibling-story-polling-evidence Wave 2 deferred-followup precedent 답습)
```

### §3.7 MANIFEST.yaml ratchet (label-registry + comment-prefix mirror)

```yaml
# docs/inter-plugin-contracts/MANIFEST.yaml registries: 블록
- { file: label-registry-v2.md, version: "2.54", status: Active }   # CFP-1336 v2.54: hotfix-bypass:cross-repo-label-sync 75번째 family member append (CFP-1336 / ADR-073 Amendment 9 + ADR-082 Amendment 14 + ADR-066 Amendment 4 carrier — cross-repo bidirectional label sync workflow self-trigger 4-pattern AND guard bypass channel, warning-tier, kind:registry sibling sync 면제 ADR-010 §결정 2, plugin.json bump 0 = marketplace_sync_declared: false). MANIFEST.yaml row "2.53" → "2.54" ratchet 동반. | CFP-1302 v2.52: (see below)
# (comment-prefix-registry MANIFEST entry 없음 — registries 블록 안 별도 entry 부재, frontmatter version 만 SSOT. 본 Change Plan 영역 외)
```

---

### §4. API 계약 (Wave 2 schema declare, Wave 1 = declarative SSOT only)

### §4.1 repository_dispatch payload schema (Wave 2 mechanical wire 시점 활성)

**event_type**: `cross-repo-label-sync`

**client_payload** (5-field):

```json
{
  "action": "<add|remove|sync_full>",
  "label": "<phase:* | gate:* | hotfix-bypass:* — label-registry-v2 lookup 정합>",
  "source_issue_or_pr": {
    "owner": "mclayer",
    "repo": "<repo-name>",
    "number": <integer>,
    "type": "<issue|pull_request>"
  },
  "target_issue_or_pr": {
    "owner": "mclayer",
    "repo": "<repo-name>",
    "number": <integer>,
    "type": "<issue|pull_request>"
  },
  "dispatched_at": "<ISO 8601 UTC strict Z suffix — KST conversion display layer only, contract field UTC strict ADR-079 §결정 2 정합>",
  "verified_via": "<gh api repos/.../issues/<N>/labels --jq '.[].name' direct cite, ADR-073 Amendment 9 §결정 1-A 9번째 entry label_change verify-before-assert 4-step 정합>",
  "session_id": "<active_sessions[].git_identity — ADR-085 §결정 2 dual carrier 정합, optional Wave 1 declarative>"
}
```

**Wave 1 = schema declare only** — Wave 2 carrier 가 (a) `peter-evans/repository-dispatch@<SHA pin>` action 호출 + (b) impl repo listener workflow seed + (c) bats fixture pair (cross-org reject / 4-pattern guard / idempotent diff) 실 wire.

**axis disjoint with `git_ops_event` contract** (CFP-139 / ADR-047): git_ops_event = GitOps lane internal event (branch / commit / PR open). cross-repo label sync = cross-repo label state mutation event. 양 disjoint.

### §4.2 Wave 2 carrier ratchet 의무

**Wave 2 별 sub-CFP carrier 가 발의 의무**:

- `cross_repo_label_sync_event` inter-plugin contract 신규 entry 평가 (MANIFEST.yaml `contracts:` 블록, kind:contract — sibling sync 의무 영역, ADR-010 §결정 2 정합). 본 Wave 1 declarative scope 외 (CFP scope unitary, ADR-064 §결정 1).
- `cross-repo-label-sync.yml` workflow hydration (Wave 1 skeleton + Wave 2 trigger event + step + bats + lint script).
- impl repo listener seed (별 cross-repo PR carrier — `mclayer/<consumer-repo>` repo 의 `.github/workflows/cross-repo-label-sync-listener.yml`).
- PAT scope grant `cross-repo-target-repos issues:write` actual grant + audit log row 4번째 갱신 (ADR-066 Amendment 4 §결정 2 6번째 entry 정합, Phase 1 placeholder → Wave 2 actual).
- evidence-checks-registry `cross-repo-label-sync` entry status `deferred-followup → warning` 자동 승격.

---

### §5. 변경 영향 (8 file estimate — Story §4.1 from-spec 정합)

| 경로 | 변경 종류 | 라인 수 추정 |
|---|---|---|
| `docs/change-plans/cfp-1336-cross-repo-label-sync.md` | **신규 file** (본 Change Plan) | ~500 lines |
| `docs/adr/ADR-073-orchestrator-verify-before-assert.md` | Amendment 9 append (frontmatter amendments[] entry + 본문 §Amendment 9 + §결정 1-A 표 9th row + mechanical_enforcement_actions[] 4번째 entry + related_stories[] CFP-1336 append) | +90 lines |
| `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` | Amendment 14 append (frontmatter amendments[] entry + amendment_log[] entry + 본문 §Amendment 14 + §결정 1 layer 1 sub-scope 1-D 표 4th row + related_stories[] append). Amendment slot history: spawn Amd 8 → iter 1 Amd 10 → iter 2 Amd 12 → iter 3 Amd 13 → iter 4 Amd 14 FINAL (Amd 8 → 10 → 12 → 13 → 14 history, 5 collisions, CFP-1390 mid-DesignReview spawn collision 추가). | +75 lines |
| `docs/adr/ADR-066-pat-rotation-policy.md` | Amendment 4 append (frontmatter amendments[] entry + 본문 §Amendment 4 + §결정 2 scope minimum 표 6번째 row) | +55 lines |
| `docs/adr/ADR-RESERVATION.md` | amendments_reserved[] sub-tree 3 row append (ADR-73 Amd 9 + ADR-82 Amd 14 + ADR-66 Amd 4, all status:active) | +24 lines |
| `docs/security/pat-rotation-log.md` | 4번째 row placeholder append (CFP-1336 scope add — `cross-repo-target-repos issues:write`) | +5 lines |
| `docs/inter-plugin-contracts/label-registry-v2.md` | v2.53 → v2.54 frontmatter + §3 yaml `hotfix-bypass:cross-repo-label-sync` 75번째 entry append + §변경 이력 v2.54 changelog block append | +45 lines |
| `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` | v1.3 → v1.4 frontmatter + §3 yaml `[CROSS-REPO-SYNC]` 15번째 prefix entry append + §5 변경 이력 v1.4 row append + §1 prefix taxonomy count 14 → 15 갱신 | +30 lines |
| `docs/inter-plugin-contracts/MANIFEST.yaml` | registries[label_registry] v2.53 → v2.54 row mirror (sequential append, prior row 보존) | +1 line |
| `docs/evidence-checks-registry.yaml` | entries[] tail `cross-repo-label-sync` warning-tier entry append (deferred-followup status, Wave 1 declarative anchor only) + `last_updated` header CFP-1336 prepend | +80 lines |
| `docs/parallel-work/section-ownership.yaml` | 본 Change Plan + 3 ADR amendments + 5 registry/CLAUDE.md target rows append (locked / append-only categorize) | +50 lines |
| `templates/github-workflows/cross-repo-label-sync.yml` | **신규 file** (Wave 1 declarative skeleton only, Wave 2 carrier 가 hydrate) | ~30 lines |
| `CLAUDE.md` | Verify-before-trust 4-layer governance 단락 ADR-073 Amd 9 + ADR-082 Amd 14 cross-ref + GitHub Workflow 단락 cross-repo-label-sync.yml 신규 entry + CODEFORGE_CROSS_REPO_PAT rotation policy 단락 ADR-066 Amd 4 cross-ref (3 in-place wording append, 신규 단락 0) | +5 lines (in-line append) |
| `docs/stories/CFP-1336.md` | §3 / §7 / §11 / §13 mirror (placeholder → actual content, ArchitectAgent direct write per CFP-40) | +60 lines |

**총합 추정**: ~1050 lines change (대부분 governance metadata layer, src 변경 0건, tests 변경 0건 — Wave 1 declarative scope unitary).

**Phase 1 PR scope**: 위 13개 file 전체. Phase 2 PR (= Wave 2 별 sub-CFP) = workflow hydrate + impl repo listener seed + bats fixture pair + script lint binding + PAT scope grant actual.

**테스트 재작성**: 0건 (Wave 1 declarative).

**인터페이스 파괴적 변경**: 0건 (모두 append, ADR-008 §결정 3 정합).

---

### §6. 리팩토링 선행

**N/A** (Wave 1 declarative only — append-only changes, no behavior modification, ADR-076/082/086/097 Wave 1 declarative anchor only precedent verbatim 답습).

**Refactor scope 부재 rationale**: 본 Change Plan = governance SSOT codify (ADR Amendment + registry entries + workflow skeleton). 기존 codebase / agent / lane plugin 영역 mechanism 변경 0건 — chief tie-break ladder (ADR-068 Amendment 2) RACI lookup 결과 = ADR-073 / ADR-082 / ADR-066 author-mandate 자체 단일 영역 (ArchitectAgent chief author scope). refactor 영역 분리 불필요.

---

### §7. 보안 설계 (SecurityArchitectAgent §7.1-§7.3 / §7.5-§7.6 + InfraOperationalArchitectAgent §7.4 통합)

### §7.1 Trust boundary 4-domain table (SecurityArch full content)

| Domain | Boundary | Trust level | Cross-boundary 침범 가능 경로 |
|---|---|---|---|
| **(1) wrapper repo Issue label state** | `mclayer/plugin-codeforge` GitHub Issue label set | wrapper-self trusted (Orchestrator + GitOpsAgent owned) | **(a) PAT-mediated WRITE from impl repo workflow listener (Wave 2 wire)** — sender.type early-exit + actor-allowlist guard 의무 |
| **(2) impl repo PR label state** | `mclayer/<consumer-repo>` GitHub PR label set (e.g., consumer Phase 2 PR) | impl-self trusted (lane PL agent + Orchestrator owned) | **(b) PAT-mediated WRITE from wrapper repo workflow sender (Wave 2 wire)** — `[skip-cross-repo-sync]` marker grep guard + idempotent diff guard 의무 |
| **(3) GitHub Actions runtime context** | `runs-on: ubuntu-latest` ephemeral VM + `secrets.CODEFORGE_CROSS_REPO_PAT` env injection | per-run isolated (GitHub Actions sandboxing) | **(c) PAT exfiltration via 3rd-party action / unsafe step output / log redaction bypass** — SHA-pinned action only + env scope minimize + log redaction lint 의무 (CFP-300 action SHA pin policy) |
| **(4) Secret store** | mclayer org secrets (`CODEFORGE_CROSS_REPO_PAT`) | org-admin trusted (manual rotation per ADR-066) | **(d) Compromise via leak / log exposure / 3rd-party action exfiltration** — ADR-066 §결정 4 4-step compromise response + audit log SSOT |

**Topology diagram** (cross-repo bidirectional flow, Wave 2 wire activation):

```
wrapper repo: mclayer/plugin-codeforge
    │
    │ Issue #N label change event (phase:* / gate:* mutation)
    ▼
[domain 1] wrapper Issue label state — Orchestrator-owned trust
    │
    │ trigger: issues.labeled / issues.unlabeled (Wave 2 wire)
    ▼
[domain 3] cross-repo-label-sync.yml workflow runtime
    │  (4-pattern T-2 guard AND: sender.type / actor-allowlist / [skip-cross-repo-sync] marker / idempotent diff)
    │  (Authorization: token ${{ secrets.CODEFORGE_CROSS_REPO_PAT }} — domain 4 secret)
    │  (verify-before-assert 4-step: git fetch + gh api direct + active_sessions[] dual + verified-via annotation)
    │
    │ peter-evans/repository-dispatch@<SHA pin> → event_type: cross-repo-label-sync
    ▼
impl repo: mclayer/<consumer-repo>
    │
    │ repository_dispatch listener workflow (Wave 2 carrier)
    │  (4-pattern T-2 guard AND mirror)
    ▼
[domain 2] impl PR label state — lane PL agent-owned trust
    │
    │ (label write via gh api / native action — issues:write scope = ADR-066 Amendment 4 §결정 2 6th entry)
    │
    │ audit comment: [CROSS-REPO-SYNC] verified-via annotation + verify-before-assert evidence
```

**Bidirectional symmetry**: impl → wrapper sync 도 동일 topology (양방향 mirror) — wrapper-primary tie-break (Concept 3, Researcher synthesis §6) 정합.

### §7.2 STRIDE-lite 5 threat 표 (SecurityArch full content + InfraOp §7.4 cross-ref)

| ID | Threat (STRIDE) | Severity | Source | Mitigation Wave 1 declarative | Mechanical wire Wave 2 |
|---|---|---|---|---|---|
| **T-1** | **Spoofing**: 외부 actor 가 cross-repo PAT 자격으로 위장해 label write 시도 | P1 | external attacker (3rd-party action / leaked PAT) | (a) PAT scope = `cross-repo-target-repos issues:write` 1종만 (ADR-066 Amd 4 §결정 2 6번째 entry) + (b) ADR-082 sub-scope 1-D (c) cross-org sync 차단 invariant (`mclayer org only`) | Wave 2 workflow level check (`if: github.repository_owner == 'mclayer'`) + bats fixture (external-org/* reject TC) |
| **T-2 (P0)** | **Self-trigger loop / Tampering**: 본 workflow 의 label write 동작이 또 다시 `label_change` event 발화 → 무한 recursion | **P0** | self-application (Wave 2 wire 시점 activation 직후) | **4-pattern AND guard invariant** (AC-2): (a) sender.type early-exit (`github.event.sender.type ≠ 'Bot'` OR sender login ≠ PAT actor) + (b) actor-allowlist (`github.actor` ∈ allowlist enum) + (c) `[skip-cross-repo-sync]` marker grep (Issue/PR body 안 marker 부재) + (d) idempotent diff (label set diff ≠ ∅) | Wave 2 workflow yaml 안 4 step 명시 + bats fixture (self-trigger 4-pattern 각 step 실패 TC pair) + evidence-checks-registry `cross-repo-label-sync` recurrence count threshold 3 reach 시 auto_blocking 승격 |
| **T-3 (P0)** | **PAT exfiltration / Information disclosure**: workflow runtime 안 `CODEFORGE_CROSS_REPO_PAT` 가 3rd-party action / unsafe step output / log 노출로 leak | **P0** | 3rd-party action / step output | (a) **3rd-party action SHA-pinned only** (CFP-300 policy — `peter-evans/repository-dispatch@<frozen-SHA-pin>` Wave 2 wire) + (b) env scope minimize (workflow-level env 만 PAT, job-level / step-level override 금지) + (c) log redaction lint (`secrets.CODEFORGE_CROSS_REPO_PAT` 이 step output / log 안 verbatim 노출 시 즉시 GitHub Actions auto-redact) + (d) ADR-066 §결정 4 4-step compromise response (immediate revoke + 1h rotation + audit + disclosure) | Wave 2 carrier action SHA pin verify (`scripts/check-action-sha-pin.sh` Wave 2 별 sub-CFP — CFP-300 framework) + ADR-066 §결정 4 4-step manual blocker |
| **T-4** | **Cross-org spoofing / Elevation of privilege**: external-org/* (e.g., `external-org/<repo>`) 가 cross-repo sync target 으로 위장 | P1 | external attacker (cross-org repository_dispatch payload injection) | ADR-082 sub-scope 1-D (c) cross-org sync 차단 invariant + workflow level check `if: github.repository_owner == 'mclayer'` + repository_dispatch payload `target_issue_or_pr.owner == 'mclayer'` strict check (Wave 2 wire) | Wave 2 workflow level check + bats fixture (cross-org reject TC) |
| **T-5** | **Label namespace collision / Tampering**: label-registry-v2 안 미등록 label (e.g., consumer 자체 `priority:high`) 가 cross-repo sync 시 namespace collision → 의도치 않은 label state 변경 | P1 | label-registry drift (consumer-side custom label) | (a) label-registry-v2 lookup table 기반 sync (registered phase:* / gate:* / hotfix-bypass:* 만 sync, EC-7) + (b) deprecated label 자동 marker (warning tier) — label rename / deprecation handling EC-4 | Wave 2 workflow step (`gh label list` parse + label-registry-v2 lookup intersection check) + audit comment `[CROSS-REPO-SYNC: skip — label not in registry]` |
| **T-6** | **PAT scope creep / Elevation of privilege**: ADR-066 §결정 2 scope minimum invariant 위반 (예: `admin:*` / `delete_repo` / `workflows:write` 등 escalation scope grant) | P1 | manual rotation error (PAT 발급 시 scope 잘못 선택) | (a) ADR-066 §결정 2 scope minimum 명시 (6번째 entry `cross-repo-target-repos issues:write` 1종만) + (b) audit log row append (Phase 1 placeholder → Wave 2 actual grant date) + (c) PAT rotation 90d 권장 / 180d max + (d) §결정 4 compromise response 4-step | Wave 2 manual blocker — 사용자 발급 시점 scope 확인 + audit log 검증 (`scripts/check-pat-rotation-log.sh` Phase 2 carrier) |

**STRIDE coverage matrix**:

| STRIDE | T-1 | T-2 | T-3 | T-4 | T-5 | T-6 |
|---|---|---|---|---|---|---|
| Spoofing | ✓ | | | ✓ | | |
| Tampering | | ✓ | | | ✓ | |
| Repudiation | | | | | | |
| Information disclosure | | | ✓ | | | |
| Denial of service | | | | | | |
| Elevation of privilege | | | | ✓ | | ✓ |

**Severity ↔ guard tier mapping**:
- **P0 (T-2 / T-3)**: invariant-strength guard (4-pattern AND / SHA-pin only / env scope minimize) — Wave 1 declarative anchor + Wave 2 mechanical blocking-on-pr 승격 후보 (evidence-checks-registry promotion_trigger auto_blocking, recurrence threshold 3 reach 시)
- **P1 (T-1 / T-4 / T-5 / T-6)**: workflow level check + audit comment + manual blocker (rotation log review) — Wave 1 declarative + Wave 2 warning-tier

### §7.3 Authentication + 5-layer Authorization (SecurityArch full content)

**Authentication**: Bearer PAT (`Authorization: token ${{ secrets.CODEFORGE_CROSS_REPO_PAT }}`) — Wave 2 workflow header / `gh auth login` env. ADR-066 §결정 1 (90d 권장 / 180d max lifetime) + §결정 5 audit log SSOT 정합.

**5-layer Authorization**:

1. **source allowlist** (workflow level check): `github.repository_owner == 'mclayer'` strict (cross-org reject — T-4 mitigation).
2. **actor allowlist** (4-pattern T-2 guard (b)): `github.actor` ∈ known-bot allowlist (e.g., `CODEFORGE_CROSS_REPO_PAT` owner login `mccho` / `dependabot[bot]` 등). 미일치 시 exit 0 graceful skip.
3. **sender.type early-exit** (4-pattern T-2 guard (a)): `github.event.sender.type == 'Bot'` AND sender login == PAT actor → exit 0 (self-trigger loop 차단, T-2 mitigation).
4. **skip marker grep** (4-pattern T-2 guard (c)): Issue/PR body / 코멘트 안 `[skip-cross-repo-sync]` marker 부재 verify. 존재 시 exit 0 graceful skip (audit visibility — opt-out channel).
5. **idempotent diff** (4-pattern T-2 guard (d)): 동기화 대상 label set 이 현 state 와 byte-identical 시 no-op (write 자체 발화 차단 — race-free convergence, T-2 mitigation).

**5-layer AND invariant**: 5 layer 모두 PASS 시에만 cross-repo label write 발화. 1+ FAIL 시 exit 0 graceful skip + audit comment `[CROSS-REPO-SYNC: skip — <layer N> guard fail]` (comment-prefix-registry-v1 v1.4 `[CROSS-REPO-SYNC]` 15번째 prefix 정합).

### §7.4 운영 리스크 (InfraOperationalArchitectAgent full content)

#### §7.4.1 DR 4 failure mode

| Mode | Trigger | Mitigation Wave 1 declarative | Recovery |
|---|---|---|---|
| **(a) PAT absent** | `CODEFORGE_CROSS_REPO_PAT` secret 미설정 (consumer Enterprise org 제약 / fresh repo) | `continue-on-error: true` + `[CROSS-REPO-SYNC: PAT missing — degraded mode]` Issue comment + `fallback:manual` label 부착 (ADR-027 Amendment 2 / CFP-658 fallback:manual pattern 정합) — graceful degradation | Manual rotation (ADR-066 §결정 3 5-step) + `fallback:manual` label 해소 |
| **(b) impl unreachable** | impl repo network unreachable / 403 forbidden / 404 not-found / 500+ server error | exponential backoff (5s / 15s / 45s 3-retry) + circuit breaker (5 consecutive fail → 1h pause) + audit comment `[CROSS-REPO-SYNC: impl repo <repo> unreachable — retry exhausted]` | manual retry trigger (workflow_dispatch) |
| **(c) webhook delay** | repository_dispatch event delivery delay (GitHub eventual consistency 5-30s) | concurrency.group per-Issue/PR + cancel-in-progress:false (in-flight write 진행 보존, race window 안 last-write-wins) + 30s timeout per step | manual retry trigger |
| **(d) runner outage** | ubuntu-latest runner image issue / GitHub Actions service degraded | best-effort + `[CROSS-REPO-SYNC: runner outage — manual sync required]` Issue comment + `fallback:manual` label (ADR-027 Amendment 2 정합) | GitHub Actions service restoration 대기 + manual sync |

#### §7.4.2 Cancel-on-disconnect + backoff + circuit breaker

- `cancel-in-progress: false` (in-flight write 진행 보존, race window 안 last-write-wins, AC-5 ordering invariant)
- **Exponential backoff**: 5s / 15s / 45s 3-retry (impl repo transient 5xx error)
- **Circuit breaker**: 5 consecutive fail → 1h pause (`scripts/check-circuit-breaker-state.sh` Wave 2 carrier — 별 sub-CFP)
- **Per-step timeout**: 30s timeout per `gh api` call (rate-limit budget 보존)

#### §7.4.3 Clock sync (ADR-079 정합)

- **Transport layer** (repository_dispatch payload `dispatched_at` field): **UTC strict Z suffix** invariant (contract field UTC strict, ADR-079 §결정 2 0건 변경 invariant)
- **Display layer** (audit comment / Issue body / Story §14 Lane Evidence transcript): **KST `+09:00` ISO 8601 zoned** 강제 (ADR-079 §결정 1 governance display layer)
- 양 layer disjoint — transport UTC ↔ display KST conversion 의무 (workflow 안 `date -d "$UTC_TIMESTAMP" "+%Y-%m-%dT%H:%M:%S+09:00"` 또는 native gh CLI conversion, Wave 2 wire)

#### §7.4.4 Rate limit

**Wave 1 declarative estimate** (실측 = Wave 2 telemetry, ADR-068 Amendment 1 I-5 dimensional empirical grounding 정합):

| Dimension | Wave 1 estimate | empirical-source |
|---|---|---|
| **wrapper-only fan-out** | 1 wrapper Issue × 1 impl repo PR × ~2 label change/Story (avg) = ~2 API calls/Story | `[empirical-source: TBD — Wave 2 mechanical wire telemetry, runtime measurement]` |
| **PAT 5000 req/h secondary limit headroom** | 0.024% (2 req / 5000 req/h × 60 min) | `[empirical-source: TBD — Wave 2 telemetry]` |
| **9-plugin × N consumer cascade fan-out** (Wave 2 wire 시점 활성) | 9 plugin × N consumer × ~2 label change/Story = scale latency dimension | `[empirical-source: TBD — Wave 2 mechanical wire telemetry, runtime measurement after activation]` |

**concurrency.group serialization** (per-Issue/PR scope) — race window 안 last-write-wins, ordering invariant 보존.

**Wave 2 telemetry forward**: rate-limit budget exhausted threshold 도달 시 → exponential backoff (5s/15s/45s) → circuit breaker (5 fail → 1h pause) → audit comment + `fallback:manual` label.

#### §7.4.5 Env isolation

- **org-level secret** (`CODEFORGE_CROSS_REPO_PAT`) — repo-level override 금지 (ADR-066 §결정 3 step 2/3 정합).
- **`runs-on: ubuntu-latest`** — GitHub-managed image (per-run isolated, no persistent state).
- **actor self-introspect** (4-pattern T-2 guard (b)): `github.actor` allowlist verify.
- **6번째 PAT consumer 명시** (R-OP-1 P1 dissent 정합): `cross-repo-label-sync.yml` = `CODEFORGE_CROSS_REPO_PAT` 6번째 consumer workflow (phase-gate-mergeable.yml / rate-limit-fallback-kpi.yml / marketplace-drift-detection.yml / UpgradeAgent reconcile / 신규 cross-repo-label-sync.yml).

#### §7.4.6 3rd-party action SHA pin (CFP-300 policy 정합)

- **GitHub-managed image** only (`runs-on: ubuntu-latest`).
- **3rd-party action SHA pin**: `peter-evans/repository-dispatch@<frozen-SHA-pin>` (Wave 2 wire 시 actual SHA pin — Wave 1 declarative skeleton 안 placeholder commented).
- **Action SHA pin lint** (CFP-300 framework — `scripts/check-action-sha-pin.sh` Phase 2 / Wave 2 carrier).

### §7.5 Data class table + cross-repo bridge flow diagram (SecurityArch full content)

| Data class | Sensitivity | Storage location | Cross-repo bridge flow |
|---|---|---|---|
| **(1) CODEFORGE_CROSS_REPO_PAT** | **Secret** (highest) | mclayer org secrets (`CODEFORGE_CROSS_REPO_PAT`) | env injection (workflow runtime only, auto-redact in log) — never logged / dumped |
| **(2) repository_dispatch payload** | Internal (governance metadata) | GitHub Actions event payload (in-flight only) | wrapper repo workflow → impl repo workflow listener (encrypted via HTTPS) |
| **(3) Cross-repo label state** | Internal (governance metadata) | wrapper Issue + impl repo PR (public visibility within mclayer org) | bidirectional sync (wrapper-primary tie-break per Concept 3) |
| **(4) `[skip-cross-repo-sync]` marker** | Internal (opt-out channel) | Issue / PR body (public within org) | grep-only check (no encryption needed) |
| **(5) audit comment `[CROSS-REPO-SYNC]`** | Internal (audit trail) | Issue / PR body (public within org) | comment-prefix-registry-v1 v1.4 정합 |
| **(6) `verified-via` annotation** | Internal (verify evidence) | Story §10 / §14 / Change Plan / ADR Amendment 본문 | ADR-073 Amendment 9 §결정 1-A 9번째 entry verify-before-assert 4-step 정합 |

**Cross-repo bridge flow diagram**: see §7.1 topology diagram.

**Log / error 노출 금지 6 항목**:

1. `CODEFORGE_CROSS_REPO_PAT` verbatim (GitHub Actions auto-redact + workflow `echo` 금지)
2. PAT scope list verbatim (`cross-repo-target-repos issues:write` 등) — audit comment 안 cite 시 scope name 만, value 비공개
3. PAT owner email / org admin info (audit log SSOT 안 KST timestamp / by 만, email partial obfuscation)
4. impl repo private metadata (if private repo) — workflow log redaction
5. `gh api` raw response (label list verbatim 만 OK, internal metadata 제외)
6. Stack trace (action runtime error full stack 노출 시 PAT context 잠재 leak risk)

### §7.6 Threat × mitigation matrix (Wave 1 declarative + Wave 2 mechanical wire 2-phase)

| Threat | Wave 1 declarative anchor | Wave 2 mechanical wire | bypass channel |
|---|---|---|---|
| **T-1 Spoofing** | ADR-082 sub-scope 1-D (c) cross-org sync 차단 + ADR-066 §결정 2 scope minimum | workflow `if: github.repository_owner == 'mclayer'` + bats fixture cross-org reject TC | `hotfix-bypass:cross-repo-label-sync` (label-registry-v2 v2.54 75번째 family) |
| **T-2 Self-trigger** | 4-pattern AND guard invariant declare (AC-2) | workflow yaml 4 step + bats fixture (4 individual step fail TC pair) | `hotfix-bypass:cross-repo-label-sync` |
| **T-3 PAT exfiltration** | ADR-066 §결정 4 compromise response 4-step + CFP-300 action SHA pin policy + log redaction lint | `scripts/check-action-sha-pin.sh` (CFP-300 framework Wave 2) + GitHub Actions auto-redact (native) | manual blocker (no bypass — ADR-066 §결정 4 4-step strict) |
| **T-4 Cross-org spoofing** | ADR-082 sub-scope 1-D (c) + workflow level check declare | `if: github.repository_owner == 'mclayer'` + bats fixture | `hotfix-bypass:cross-repo-label-sync` |
| **T-5 Label namespace collision** | label-registry-v2 lookup table 기반 sync (registered set 만, EC-4 / EC-7) | workflow step (`gh label list` parse + registry lookup intersection) + audit comment `[CROSS-REPO-SYNC: skip — label not in registry]` | `hotfix-bypass:cross-repo-label-sync` |
| **T-6 PAT scope creep** | ADR-066 §결정 2 scope minimum 6번째 entry 명시 + audit log row 4번째 placeholder | `scripts/check-pat-rotation-log.sh` (Phase 2 carrier) + 사용자 manual blocker (Wave 2 진입 전 pre-clear) | manual blocker (no bypass — ADR-066 §결정 2 strict) |

### §7.7 N/A 영역 부재 (전 7 항목 active 영역)

7 sub-section 모두 active 영역 (§7.7 N/A 영역 = 부재). Live touching = FALSE (Story §13 Live Operational Discipline N/A — backtest/paper only) ↔ 본 §7 = governance secret store + cross-repo trust boundary 영역 (Live touching 영역 외 active).

---

### §8. Test Contract (TestContractArchitectAgent full content)

### §8.1 AC-1~AC-5 coverage matrix (Story §5.2 정합)

| AC | Story §5.2 statement | Test scope | Mechanical verify (Wave 2 mechanical wire) | Bats fixture pair (Wave 2 carrier) |
|---|---|---|---|---|
| **AC-1** | bidirectional sync 5s target (best-effort eventual consistency) | E2E (Wave 2 carrier) | Wave 2 telemetry — runtime measurement (실측 후 SLO 정의, ADR-068 Amendment 1 I-5 dimensional empirical grounding) | `tests/scripts/cfp-1336/cfp-1336-bidirectional-sync.bats` (Wave 2) |
| **AC-2 (P0)** | T-2 self-trigger 차단 4-pattern AND guard | Unit + Workflow | workflow yaml 안 4 step 명시 (sender.type / actor-allowlist / [skip-cross-repo-sync] marker / idempotent diff) + bats fixture (4 individual step fail TC pair) | `cfp-1336-self-trigger-4pattern-guard.bats` (Wave 2) |
| **AC-3** | ADR-073 Amd 9 transition trigger `label_change` 4-step verify | Workflow | workflow yaml 4 step 명시 (git fetch + gh api direct + dual-source AND + verified-via annotation) + lint script (Wave 2 carrier) verified-via annotation 부재 시 warning | `cfp-1336-verify-before-assert-4step.bats` (Wave 2) |
| **AC-4** | PAT scope minimal (ADR-066 §결정 2 정합) | Audit (manual) | PAT rotation log review (`scripts/check-pat-rotation-log.sh` Phase 2 carrier) + ADR-066 §결정 2 6번째 entry verify-before-trust | `cfp-1336-pat-scope-verify.bats` (Wave 2 audit) |
| **AC-5** | ordering invariant — concurrency.group + cancel-in-progress:false | Workflow | workflow yaml `concurrency:` block 명시 + bats fixture race scenario | `cfp-1336-concurrency-ordering.bats` (Wave 2) |

**AC coverage axis**:
- **safety-critical** (P0): AC-2 (T-2 self-trigger 차단 4-pattern AND invariant)
- **functional**: AC-1 (5s target) + AC-3 (verify-before-assert 4-step) + AC-5 (ordering)
- **security/audit**: AC-4 (PAT scope minimal)

### §8.2 6 boundaries

| Boundary | Description | Verify mechanism Wave 1 declarative |
|---|---|---|
| **B-1** | wrapper repo ↔ impl repo trust boundary | ADR-082 sub-scope 1-D 4-tuple write authority verify (a/b/c/d 모두 PASS) |
| **B-2** | label-registry-v2 lookup table 기반 sync (registered set 만) | workflow step (`gh label list` + registry lookup) — EC-4 / EC-7 |
| **B-3** | mclayer org boundary (cross-org sync 차단) | workflow level `if: github.repository_owner == 'mclayer'` (ADR-082 sub-scope 1-D (c)) |
| **B-4** | PAT TTL boundary (90d 권장 / 180d max) | ADR-066 §결정 1 + audit log SSOT |
| **B-5** | label set diff boundary (idempotent diff = ∅ no-op) | 4-pattern T-2 guard (d) idempotent diff |
| **B-6** | eventual consistency window (5-30s cross-repo PAT write latency) | concurrency.group + cancel-in-progress:false + race window last-write-wins |

### §8.3 5 invariants

| Invariant ID | Description | Verify method Wave 1 declarative |
|---|---|---|
| **INV-T2** | 4-pattern AND guard PASS 시에만 cross-repo label write 발화 — 1+ FAIL 시 exit 0 graceful skip + audit comment | workflow yaml 안 4 step explicit + bats fixture 4 individual step fail TC pair (Wave 2) |
| **INV-IDEMPOTENT** | label set diff = ∅ 시 no-op (write 자체 발화 차단) — race-free convergence | 4-pattern T-2 guard (d) — workflow step explicit |
| **INV-ORDERING** | concurrency.group per-Issue/PR + cancel-in-progress:false → race window 안 last-write-wins | workflow yaml `concurrency:` block + bats fixture race scenario (Wave 2) |
| **INV-PAT-SCOPE** | PAT scope = `cross-repo-target-repos issues:write` 1종만 (ADR-066 §결정 2 Amd 4 6번째 entry) — escalation scope (admin / workflows:write / contents:write) 금지 | ADR-066 §결정 2 strict + audit log row append + manual blocker (Wave 2 진입 전 pre-clear) |
| **INV-VERIFIED-VIA** | 모든 cross-repo label state 인용 옆 `verified-via: <method>` annotation 의무 (ADR-073 Amendment 9 §결정 1-A 9번째 entry 정합) | lint script (Wave 2 carrier) — verified-via annotation 부재 시 warning + audit comment |

### §8.4 §8.3 성능 영향

**N/A** — Wave 1 declarative scope (governance SSOT codify only, runtime workflow 실 활성 = Wave 2 carrier). 성능 측정 대상 0건 — Wave 2 wire 시 telemetry 통한 실측 (ADR-068 Amendment 1 I-5 dimensional empirical grounding 정합 — Wave 1 = 측정 대상 정의만, Wave 2 = 실측).

### §8.5 Stateful / restart invariant tests applicability

#### §8.5.0 Applicability decision

| 적용 조건 | Y/N | 근거 |
|---|---|---|
| Long-running connection | N | Phase 1 Wave 1 declarative scope only — workflow live activation = Wave 2 별 sub-CFP carrier (governance SSOT codify scope only, runtime connection 0건) |
| Stateful in-memory cache | N | Phase 1 declarative anchor only — label state cache 없음 (workflow yml = stateless skeleton, Wave 2 carrier 가 cache + race scenario TC 작성) |
| Background worker | N | Phase 1 declarative scope only — repository_dispatch listener seed = Wave 2 별 sub-CFP carrier (impl repo workflow 작성 영역 외, Wave 1 = wrapper-side workflow skeleton only) |
| Process restart-aware system | N | Phase 1 declarative anchor only — PAT rotation log placeholder만, ADR-066 §결정 3 5-step rotation manual 절차 active 영역, restart-aware system 작성 0 (Wave 2 mechanical wire 시점에 `scripts/check-pat-rotation-log.sh` schema lint + cron audit carrier) |

#### §8.5.4 N/A 명시 (4 N 적용 조건 모두 부재)

N/A — Phase 1 Wave 1 declarative anchor scope only (governance SSOT codify, runtime test 0건, 4 stateful 적용 조건 모두 N), Wave 2 mechanical wire = 별 sub-CFP carrier defer.

본 Phase 1 declarative anchor scope (governance SSOT codify only) — 4 stateful 적용 조건 모두 N. 4 영역 모두 Wave 2 mechanical wire carrier 별 sub-CFP defer. **현재 §8.5 stateful test 작성 0건 (CFP-47 §8.5 applicability 30자 minimum 정합, Wave 1 declaration-only scope 명시)**.

### §8.6 Audit gate 4-form pointer (ADR-068 Amendment 3 I-6 정합)

본 Change Plan 의 모든 cross-repo state 인용 영역에 4-form pointer 의무 (ADR-068 I-6 audit-gate-pointer-existence 정합):

| Pointer form | Example (본 Change Plan 안) |
|---|---|
| **link target** | `[ADR-073](../../archive/adr/ADR-073-orchestrator-verify-before-assert.md)` / `[ADR-082](../../archive/adr/ADR-082-write-time-self-write-verification-mandate.md)` / `[ADR-066](../../archive/adr/ADR-066-pat-rotation-policy.md)` |
| **section anchor** | `#§7.1 Trust boundary` / `#§결정 1-A 9번째 row label_change` / `#§결정 2 scope minimum 6번째 entry` |
| **file path reference** | `templates/github-workflows/cross-repo-label-sync.yml` / `docs/security/pat-rotation-log.md` / `docs/inter-plugin-contracts/label-registry-v2.md` |
| **ADR §결정 N reference** | `ADR-073 Amendment 9 §결정 1-A 9번째 entry label_change` / `ADR-082 Amendment 14 §결정 1 layer 1 sub-scope 1-D` / `ADR-066 Amendment 4 §결정 2 6번째 entry cross-repo-target-repos issues:write` |

본 Change Plan §3 / §7 / §8 / §11 / §13 모두 4-form pointer 중 1+ 보유 verify-via Read 후 author (audit_gate_pointer_self_check_passed: true 정합).

---

### §9. 분기 선택 (Tier A/B/C 3-tier comparison)

| Tier | Channel | Pros | Cons | 채택 결과 |
|---|---|---|---|---|
| **A** | GitHub Discussions cross-repo | Native channel — 별 PAT scope 신설 불필요 | per-repo scope only, **cross-repo write 미지원** (Researcher Unknown 2 falsified — GitHub REST API docs verified 2026-05-24) | **Reject (D2)** |
| **B** | `repository_dispatch` event via CODEFORGE_CROSS_REPO_PAT | 산업 표준 (peter-evans/repository-dispatch action), PAT scope minimal 정합 (single PAT consolidation, ADR-013 Amendment 4 정합), audit trail 가능 | self-trigger guard 의무 (4-pattern AND), PAT scope expansion 1종 (`cross-repo-target-repos issues:write` 6번째 entry, ADR-066 Amendment 4 carrier) | **Accept (D2 derived default)** |
| **C** | GitHub App OIDC | Token-less, fine-grained scope (per-installation) | 별 PAT namespace 신설 + audit log 신설 + ADR-066 amendment 6번째 entry 외 별 scope channel 의무 + GitHub App 등록 / install workflow / setup overhead (org-admin manual) — 본 Story scope 초과 | **Reject (scope 외, 별 CFP carrier)** |

**채택 = Tier B**. rationale:
- 산업 표준 (peter-evans/repository-dispatch action) — 검증된 패턴, 신규 mechanism 도입 0
- PAT consolidation 무변경 (ADR-013 Amendment 4) — 별 PAT namespace 신설 불필요
- ADR-066 §결정 2 scope minimum 정합 — 6번째 entry 1종만 추가 (least-privilege invariant 보존)
- D-4 chief tie-break dissent 정합 (CFP-1302 within-repo GITHUB_TOKEN 결정 시 cross-repo path 별 carrier 분리)

**다른 후보 비교**:
- (A) Discussions cross-repo = falsified
- (C) App OIDC = scope 초과 → 별 carrier (post-Wave 2 retro 시점 평가 — Tier B telemetry 결과 후 App OIDC 도입 ROI 평가 sub-CFP)

---

### §10. ADR 정합성 + 신규 ADR 필요 여부 판단

### §10.A architecture_doc_impact (ADR-078 / §결정 1 anti-scope guard 정합)

```yaml
architecture_doc_impact:
  modules_touch: false
  boundaries_touch: false        # Wave 1 = governance SSOT codify scope, architecture doc seed (각 plugin self-owned docs/architecture/*.md) 갱신 의무 발동 0 — Wave 2 mechanical wire 시 평가
  interfaces_touch: false        # repository_dispatch payload schema declare 만 (Wave 1), inter-plugin-contracts 신규 entry 평가 = Wave 2 carrier
  data_flow_touch: false
  none_rationale: "Wave 1 declarative scope (governance SSOT — workflow / ADR / registry layer codify) 한정. 4 영역 (modules / boundaries / interfaces / data_flow) 중 1+ touch 가능성 있음 (boundaries / data_flow — cross-repo trust boundary 신설 + bidirectional async data flow) but architecture doc seed (`docs/architecture/codeforge-*.md` 각 plugin self-owned) 갱신 의무 발동 0 — Wave 1 = governance metadata layer 한정 분리 (ADR-078 §결정 1 anti-scope guard 정합 — 모듈 / 경계 / 계약 / 흐름 서술 영역 ↔ governance metadata 영역 disjoint). Wave 2 mechanical wire 시점 (실 workflow 활성 + impl repo listener seed) 에 architecture doc S2 sub-Story 평가 (별 carrier)."
```

### §10.B 신규 ADR 필요 여부 = **NO** (3 Amendment + 1 sub-scope 신설로 충분)

신규 ADR 발의 회피 rationale:
- **ADR-073 Amendment 9** = §결정 1-A 9번째 entry (closed-set ratchet append-only — 강화 방향, ADR-058 §결정 5 정합). 기존 ADR-073 mechanism scope 안 9번째 row 추가만 — 신규 ADR 영역 부재.
- **ADR-082 Amendment 14** = §결정 1 layer 1 sub-scope 1-D (axis disjoint with 1-A/1-B/1-C — cross-repo label-write authority 신설). 기존 ADR-082 layer 1 mechanism scope 안 sub-scope 1-D 추가만 — 신규 ADR 영역 부재.
- **ADR-066 Amendment 4** = §결정 2 scope minimum 6번째 entry (ratchet 강화 방향 — least-privilege invariant 보존, ADR-058 §결정 5 정합). 기존 ADR-066 §결정 2 mechanism scope 안 6번째 row 추가만 — 신규 ADR 영역 부재.
- **workflow + registry entries** = 기존 framework (label-registry-v2 / comment-prefix-registry-v1 / evidence-checks-registry / template `github-workflows/`) 안 append-only — 신규 framework 영역 부재.

**chief judgement** (ADR-068 Amendment 2 chief tie-break ladder 적용):
- 단계 1 (RACI lookup, `codeforge:deputy-mandate` skill): SecurityArch (§7.1-§7.3 / §7.5-§7.6) + InfraOperationalArch (§7.4) + TestContractArch (§8) + ArchitectAnalyst (§2 / §9) — 4 deputy primary owned. ArchitectAgent chief author = author 영역 (§10 ADR 정합성 판단 + Change Plan synthesis).
- 단계 2 (ADR-068 invariant 적용): I-4 wording SSOT 정합 — 본 Change Plan 모든 인용 (ADR-073 Amd 9 / ADR-082 Amd 14 / ADR-066 Amd 4) 가 governance permanent layer 안 wording 일치 verify (Story §2.1 verified state table cross-validate + Story §6 §6.3 ADR 정합성 점검 cross-validate).
- 단계 3 (chief judgement): RACI codify 완료 영역 — 단계 1/2 결정 채택, chief judgement 단독 결정 영역 부재.

### §10.C 정합성 cross-validate (3 ADR Amendment 동시 발의 / axis disjoint verify)

| ADR Amendment | Axis | Disjoint cross-ref |
|---|---|---|
| **ADR-073 Amendment 9** | Orchestrator self-assertion verify (transition trigger `label_change` 9번째 entry) | ADR-082 Amendment 14 sub-scope 1-D 와 verify subject disjoint (Orchestrator self-assertion ↔ lane agent self-write authority) |
| **ADR-082 Amendment 14** | internal lane agent self-write authority verify (sub-scope 1-D cross-repo label-write authority) | ADR-073 Amendment 9 와 verify subject disjoint + ADR-066 Amendment 4 와 enforcement layer disjoint (write authority verify ↔ PAT scope minimum) |
| **ADR-066 Amendment 4** | PAT scope minimum 6번째 entry (`cross-repo-target-repos issues:write`) | ADR-073/082 Amendment 와 PAT scope grant axis disjoint (write authority verify ↔ PAT scope grant) |

**axis disjoint complement 3-set** — 3 Amendment 동시 발의 = ADR-064 §결정 1 CFP scope unitary 정합 (단일 super-class "cross-repo bidirectional label sync" 의 3 layer disjoint codify, ADR-082 §결정 8 per-area 분할 거부 pattern 답습).

---

### §11. 데이터 마이그레이션

**N/A** — 본 Change Plan = governance metadata only (ADR Amendment + registry entries + workflow skeleton). 데이터 schema 변경 0건 — RDB OLTP / OLAP / event schema / config schema / inter-plugin contract schema 영역 모두 변경 0.

**Wave 2 mechanical wire 시점** (workflow hydrate + impl repo listener seed + bats fixture pair) 도 governance metadata layer 만 — schema 영역 외 (ADR-089 Schema 7 원칙 적용 영역 외, ADR-090 Cross-layer reference policy 적용 영역 외).

idempotency consult = N/A (workflow self-trigger 4-pattern T-2 guard (d) idempotent diff = INV-IDEMPOTENT 정합, 단 schema migration 영역 외 — Wave 2 wire 시 workflow runtime idempotency 영역 InfraOperationalArchitectAgent §7.4 cross-ref 정합).

---

### §12. Sonnet Decision Log

**N/A** — ADR-022 Deprecated by CFP-134 / ADR-035. Sonnet decider 자동 발동 무효, 사용자 explicit ad-hoc request 시에만 호출. 본 Change Plan = author task only (chief synthesis), Sonnet ad-hoc decision request 부재.

---

### §13. Phase 1 산출물 self-check 결과 + Live Operational Discipline

### §13.A ADR-065 §결정 1 mechanical sync 7-item self-check 결과

| # | Item | Status | Notes |
|---|---|---|---|
| 1 | `label-registry-v2.md` 변경 시 `scripts/bootstrap-labels.sh` sync 동반 | **PASS (NA-equivalent)** | `bootstrap-labels.sh` = dynamic registry-driven (CFP-598 `parse-hotfix-bypass-labels.py` 분기) — yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건. v2.54 = 75번째 hotfix-bypass family entry append → bootstrap 자동 흡수. |
| 2 | `doc-locations.yaml` 변경 시 `bash scripts/check-doc-locations.sh --regen` 실행 | **NA** | doc-locations.yaml 변경 0건 (본 Change Plan 영역 외 — 신규 doc type 도입 0, 기존 location 변경 0). |
| 3 | 신규 `templates/github-workflows/*.yml` 시 `.github/workflows/` self-app copy 동반 (byte-identical) | **NA (Wave 1 declarative skeleton only)** | `cross-repo-label-sync.yml` Wave 1 = declarative skeleton (no actual steps wire). Wave 2 mechanical wire 시점에 self-app copy 의무 발동 — 본 Wave 1 PR scope 외. |
| 4 | CLAUDE.md / docs/** 내 link target 이 Phase 1 분배인지 확인 (Phase 2 file 참조 시 dangling) | **PASS** | 본 Change Plan 모든 link target (ADR-073 / ADR-082 / ADR-066 / ADR-085 / ADR-027 / ADR-068 / ADR-024 / ADR-079 / ADR-040 / ADR-058 / ADR-064 / label-registry-v2 / comment-prefix-registry-v1 / evidence-checks-registry / phase-gate-mergeable.yml / pat-rotation-log.md) = origin/main 안 실재 file (verified-via Read 후 인용) + Phase 1 분배 정합 (cross-repo-label-sync.yml = 본 Phase 1 신규 file 자체). dangling 0. |
| 5 | `docs/inter-plugin-contracts/MANIFEST.yaml` registries 블록 갱신 필요성 확인 | **PASS** | label-registry-v2 v2.53 → v2.54 row mirror 의무 동반 (본 Change Plan §3.7 + §5 covered). comment-prefix-registry-v1 entry MANIFEST 안 별도 entry 부재 (frontmatter version 만 SSOT, 본 Change Plan §3.5 covered). |
| 6 | `docs/parallel-work/section-ownership.yaml` 정책 필요 시 row append | **PASS** | 본 Change Plan §5 = 13 file 변경 → section-ownership.yaml row append 의무 (본 Change Plan + 3 ADR Amendment 각각 + 5 registry/CLAUDE.md target). 본 Change Plan §5 covered. |
| 7 | `docs/doc-locations.yaml` 신규 doc type row 필요성 확인 | **NA** | 신규 doc type 도입 0 (본 Change Plan = change-plan + ADR Amendment + workflow + registry — 모두 기존 doc type 영역). |

**총 결과**: 7-item all PASS or NA. `mechanical_self_check_passed: true` declare.

### §13.B ADR-068 4-invariant boundary completeness self-check 결과

| Invariant | Status | Verify format |
|---|---|---|
| **I-1 API contract semantic completeness** | **PASS** | §4.1 repository_dispatch payload schema 안 5-field client_payload + event_type enum 명시 + UTC strict invariant ADR-079 §결정 2 정합 + Wave 1 declare / Wave 2 active wire 분리 명시. docstring-template format. |
| **I-2 Cross-module propagation completeness** | **PASS** | §3.1 ADR-073 Amendment 9 §결정 1-A 9th row + §3.2 ADR-082 Amendment 14 sub-scope 1-D + §3.3 workflow skeleton + §3.6 evidence-checks-registry entry — 4 module 간 propagation 매핑 명시. propagation-matrix format (Story §2.1 verified state table cross-validate). |
| **I-3 Unconditional vs conditional guard placement intent** | **PASS** | §7.2 4-pattern T-2 guard AND invariant **unconditional** (자기 진입 시점 무조건 — workflow yaml 안 4 step 무조건 실행) 명시 + ADR-068 I-3 unconditional 우선 정합. ADR-082 sub-scope 1-D 4-tuple verify = **unconditional** (cross-repo label state mutation 직전 무조건). guard-placement-diagram format. |
| **I-4 Wording SSOT** | **PASS** | 본 Change Plan §1 (Wave 1 declarative scope) ↔ ADR-073 Amendment 9 §결정 1-A 9th row body ↔ ADR-082 Amendment 14 sub-scope 1-D body ↔ ADR-066 Amendment 4 §결정 2 6th entry body ↔ label-registry-v2 v2.54 75th family entry ↔ comment-prefix-registry-v1 v1.4 15th prefix entry ↔ evidence-checks-registry `cross-repo-label-sync` entry ↔ Story §2.1 verified state table ↔ Story §3 placeholder mirror — wording byte-identical verify (CFP-1336 / `cross-repo-label-sync` / `[CROSS-REPO-SYNC]` / `cross-repo-target-repos issues:write` / `4-pattern T-2 guard AND`). wording-sync-table format. |

**boundary_completeness_self_check_passed: true** declare.

### §13.C ADR-068 Amendment 1 I-5 dimensional empirical grounding self-check 결과

10 dimension enum (latency / scale / cardinality / throughput / cost / accuracy / lifecycle / volume / rate / count) quantitative parameter:

| Dimension | Wave 1 value | empirical-source |
|---|---|---|
| **latency** (bidirectional sync target) | 5s (best-effort, AC-1) | `[empirical-source: TBD — Wave 2 mechanical wire telemetry, runtime measurement]` |
| **rate** (PAT secondary limit headroom) | 0.024% (2 req / 5000 req/h × 60min) | `[empirical-source: TBD — Wave 2 telemetry]` |
| **scale** (cascade fan-out) | 9 plugin × N consumer × ~2 label change/Story | `[empirical-source: TBD — Wave 2 telemetry after activation]` |
| **lifecycle** (PAT rotation) | 90d 권장 / 180d max (ADR-066 §결정 1) | `[verified: ADR-066 §결정 1 + audit log SSOT — pat-rotation-log.md]` |
| **count** (retry backoff) | 3-retry (5s / 15s / 45s exponential, §7.4.2) | `[empirical-source: TBD — Wave 2 telemetry]` |
| **count** (circuit breaker fail threshold) | 5 consecutive fail → 1h pause | `[empirical-source: TBD — Wave 2 telemetry]` |
| **throughput** (per-step timeout) | 30s timeout per gh api call (§7.4.2) | `[empirical-source: TBD — Wave 2 telemetry]` |
| **cardinality** (label-registry hotfix-bypass family) | 74 (next ordinal — verified) | `[verified: git show origin/main:docs/inter-plugin-contracts/label-registry-v2.md | grep -c "^  - name: hotfix-bypass:" = 73, next = 74]` |
| **cardinality** (comment-prefix entries) | 15 (next ordinal — verified) | `[verified: git show origin/main:docs/inter-plugin-contracts/comment-prefix-registry-v1.md | grep -c "^  - prefix:" = 14, next = 15]` |
| **cardinality** (ADR-073 amendment_id) | 9 (next slot — verified) | `[verified: git show origin/main:docs/adr/ADR-073-orchestrator-verify-before-assert.md | grep amendment_id = 1..8, next = 9]` |
| **cardinality** (ADR-082 amendment_id) | 8 (next slot — verified) | `[verified: git show origin/main:docs/adr/ADR-082-write-time-self-write-verification-mandate.md | grep amendment_id = 1..7, next = 8]` |
| **cardinality** (ADR-066 amendment id) | 4 (next slot — verified) | `[verified: git show origin/main:docs/adr/ADR-066-pat-rotation-policy.md | grep "amendment:" = 2..3, next = 4]` |

**dimensional_empirical_self_check_passed: true** declare. Wave 1 = 측정 대상 정의만 (10 dimension enum mapping), Wave 2 = 실측 (ADR-068 Amendment 1 I-5 정합).

### §13.D ADR-068 Amendment 3 I-6 audit-gate-pointer-existence self-check 결과

§8.6 audit gate 4-form pointer 모두 보유 verify (link target / section anchor / file path reference / ADR §결정 N reference) — 본 Change Plan §3 / §7 / §8 / §11 / §13 모든 cross-repo state 인용 영역에 4-form pointer 1+ 보유.

**audit_gate_pointer_self_check_passed: true** declare.

### §13.E ADR-063 Amendment 1 marketplace sync declaration

```yaml
marketplace_sync_required: false
mirrored_fields_changed: []
triggering_plugins: []
rationale: "본 Change Plan = governance metadata layer (ADR Amendment + registry entries + workflow skeleton declare). plugin.json mirrored field 4종 (name / version / description / author) 변경 0건 — kind:registry sibling sync 면제 (ADR-010 §결정 2) + plugin.json bump 0 (governance behavior 변경 영역이나 declaration-only Wave 1, ADR-037 Amendment 1 정합 — Wave 2 mechanical wire 시점 평가). marketplace.json sync 불필요."
```

**marketplace_sync_declared: true** (false declared, silent skip 0 — ADR-063 Amendment 1 §결정 9 AC-2 정합).

### §13.F Live Operational Discipline (Story §13)

**N/A** — backtest/paper only (본 Change Plan = workflow + ADR governance metadata, real funds / live exchange API / production credential / live order placement 영역 외). LiveOrderingArchitectAgent + LiveOperationalArchitectAgent CONDITIONAL deputy spawn 0건.

---

### §14. Sibling carrier + Cross-ref

- **Sibling carrier (same Epic / parent)**: CFP-1302 retro F2 (parent — within-repo D-4 chief dissent carry-over scope 분리 evidence). #1336 (본 carrier Issue).
- **Disjoint axis cross-ref**: CFP-1059 / ADR-087 + ADR-088 (deploy lane / deploy-review lane — phase:배포 / phase:배포-리뷰 label seed 별 carrier, S2/S3 sub-Story carrier). 본 Story 와 forward-compat (workflow lookup table 통한 자동 활성 EC-7).
- **ADR cross-ref**: ADR-066 Amendment 4 / ADR-073 Amendment 9 / ADR-082 Amendment 14 (본 carrier 직접 신설) / ADR-085 §결정 2 active_sessions[] dual carrier (coordination axis) / ADR-027 Amendment 2 (Enterprise fallback) / ADR-068 Amendment 2 (chief tie-break ladder D-4 dissent carry-over rationale) / ADR-068 Amendment 1 I-5 (dimensional empirical grounding) / ADR-068 Amendment 3 I-6 (audit-gate-pointer-existence) / ADR-024 Amendment N §결정 6.A (per-entry namespace 75번째) / ADR-079 §결정 1/2 (KST display layer / UTC contract field) / ADR-013 Amendment 4 (PAT consolidation) / ADR-040 Amendment 3 §결정 7.D (self-application Wave 1→Wave 2 progression chain) / ADR-058 §결정 5 (sunset_justification ratchet 차단) / ADR-064 §결정 1 (CFP scope unitary).
- **Contract cross-ref**: label-registry-v2 v2.54 → v2.54 / comment-prefix-registry-v1 v1.3 → v1.4 / evidence-check-registry-v1 schema v1.3 (entry append 만) / MANIFEST.yaml registries[label_registry] / phase-gate-mergeable.yml precedent (read-only fetch).
- **Wave 2 별 sub-CFP carrier** (post-Phase 1 PR merge 후 발의): workflow hydrate + impl repo listener seed + bats fixture pair + script lint binding + PAT scope grant actual + telemetry.

---

### §15. Cache invalidation (Orchestrator hint)

본 Change Plan author 후 다음 file 변경:

```yaml
cache_invalidate:
  - docs/change-plans/cfp-1336-cross-repo-label-sync.md   # 신규
  - docs/adr/ADR-073-orchestrator-verify-before-assert.md  # Amendment 9 append
  - docs/adr/ADR-082-write-time-self-write-verification-mandate.md  # Amendment 14 append (FIX iter 4 FINAL)
  - docs/adr/ADR-066-pat-rotation-policy.md  # Amendment 4 append
  - docs/adr/ADR-RESERVATION.md  # amendments_reserved[] 3 row append
  - docs/security/pat-rotation-log.md  # 4번째 row placeholder append
  - docs/inter-plugin-contracts/label-registry-v2.md  # v2.54 MINOR
  - docs/inter-plugin-contracts/comment-prefix-registry-v1.md  # v1.4 MINOR
  - docs/inter-plugin-contracts/MANIFEST.yaml  # label_registry version mirror
  - docs/evidence-checks-registry.yaml  # cross-repo-label-sync entry append
  - docs/parallel-work/section-ownership.yaml  # 13 row append
  - templates/github-workflows/cross-repo-label-sync.yml  # 신규 skeleton
  - CLAUDE.md  # 3 in-line cross-ref append
  - docs/stories/CFP-1336.md  # §3/§7/§11/§13 mirror
```

Orchestrator hint forwarding 의무 (ArchitectPLAgent verdict packet 안 declare).
