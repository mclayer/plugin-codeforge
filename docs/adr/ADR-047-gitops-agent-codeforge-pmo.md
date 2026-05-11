---
adr_number: 47
title: GitOpsAgent — cross-cutting git ops agent in codeforge-pmo plugin (CFP-139 / CFP-134 Wave 3)
status: Proposed
category: agent-design
date: 2026-05-09
carrier_story: CFP-139
parent_epic: CFP-134
related_files:
  - docs/inter-plugin-contracts/git-ops-event-v1.md  # NEW (PR #265 wrapper sibling done — Phase 2 PR pair canonical)
  - docs/inter-plugin-contracts/pmo-output-v1.md  # v1.0 → v1.1 MINOR bump (worktree_manifest)
  - docs/inter-plugin-contracts/comment-prefix-registry-v1.md  # v1.0 → v1.1 (`[GitOps]` prefix)
  - docs/inter-plugin-contracts/MANIFEST.yaml  # kind:contract 6 → 7 entry
  - templates/story-page-structure.md  # §10.5 Git Ops Log schema (PR #265 done)
  - CLAUDE.md  # Development Agent Team 표 — codeforge-pmo agent count 1 → 2
related_stories:
  - CFP-134  # parent Epic (codeforge agent teams 적극 도입)
  - CFP-136  # hard_block (worktree infrastructure SSOT)
  - CFP-137  # hard_block (agent teams + SendMessage + Phase-scoped team SSOT)
  - CFP-139  # 본 ADR carrier
related_adrs:
  - ADR-008  # Inter-plugin contract versioning
  - ADR-009  # wrapper-only decomposition (invariant 무손상)
  - ADR-010  # Inter-plugin contract sibling sync
  - ADR-013  # codeforge family dogfood-out
  - ADR-024  # Story-scoped branch (cfp-NNN[/<lane>[/<sub>]] hierarchy)
  - ADR-035  # codeforge agent teams Epic SSOT (D-2 / D-3 foundation 결정)
  - ADR-039  # Orchestrator subagent default (env=0 fallback)
  - ADR-040  # Worktree convention SSOT (Amendment 1 cross-ref)
  - ADR-044  # Phase-scoped sequential team
supersedes: null
superseded_by: null
amends:
  - ADR-035 (Wave 3 amendment_log[] amendment_id=3 추가 — D-2 worktree convention + D-3 GitOpsAgent foundation 결정 implementation level)
  - ADR-040 (Amendment 1 — GitOpsAgent hook 실행 주체 명시, Phase 2 PR scope finalize)
is_transitional: false
---

# ADR-047: GitOpsAgent — cross-cutting git ops agent in codeforge-pmo plugin

## 상태

**Proposed (2026-05-09)** — CFP-139 carrier. CFP-134 Epic 의 Wave 3 child Story (CFP-136 worktree infrastructure + CFP-137 agent teams hard_block 후 진입). Phase 1 PR (#265) merge 시 `Accepted` 전환.

본 ADR 의 spec SSOT = [`mclayer/codeforge-internal-docs:wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md) §4.4 (CFP-139 부분).

본 ADR 의 Change Plan = [`mclayer/codeforge-internal-docs:wrapper/change-plans/cfp-139-gitops-agent.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/change-plans/cfp-139-gitops-agent.md).

## 컨텍스트

사용자 directive 2026-05-08 (CFP-134 brainstorming spec turn 3 + turn 10, verbatim):

**Turn 3** (design):
> "PMOAgent가 Epic과 Story 단위 등 하위 구조를 나누면 GitRepoAgent가 해당하는 브랜치를 생성하고 작업하는 agent에 넘겨주는 것이다. 또 충돌이 일어났을 경우 PMOAgent 또는 다른 PL Agent와 통신하여 충돌을 해결하는 역할도 수행할 수 있다."

**Turn 10** (confirm):
> "진짜 GitOpsAgent 안필요해? 이정도면 있는게 나을텐데" → 채택

### 현재 상태 (CFP-136 + CFP-137 완료 가정)

- **CFP-136** (worktree infrastructure SSOT) closed — `templates/scripts/worktree-{create,merge,prune}.sh` + `check-worktree-stale.sh` + `worktree-path-util.sh` 5종 + SessionStart hook + cross-platform path util 정합. ADR-040 SSOT.
- **CFP-137** (agent teams 적극 도입) closed — TeamCreate / TeamDelete / SendMessage / Phase-scoped sequential team + 7 `templates/team-spec-<lane>.yaml` + ADR-044 Accepted.
- 두 인프라 layer 갖춰진 상태.

### Gap

1. **TeamCreate 직전 N 개 worktree 동시 생성 책임 부재** — 현 상태 = Orchestrator inline (책임 비대화). N=3-5 teammate 동시 spawn 시 race condition 회피 mechanism 부재.
2. **TeamDelete 직전 sequential merge orchestration 부재** — sub-worktree → lane branch race condition 회피 sequential merge 책임자 부재.
3. **충돌 escalation 흐름 ad-hoc** — Orchestrator 가 lane PL ↔ deputy 협의 중재 (turn 3 verbatim "PMOAgent 또는 다른 PL Agent와 통신하여 충돌을 해결" 의도 미반영).
4. **FIX iteration worktree 재구성 수동** — `cfp-NNN/fix-iter-<N>` branch + worktree 자동 생성 책임자 부재.
5. **Stale worktree GC SessionStart hook 만 (능동 cleanup 부재)** — ADR-040 §결정 5 의 "Note: gh API check 는 GitOpsAgent 진입 시 ADR amendment" 미충족.
6. **§10.5 Git Ops Log audit trail 부재** — Orchestrator 가 worktree event 추적 visibility 부재.

## 결정 (D-1 ~ D-8)

### D-1 — GitOpsAgent file 위치 = codeforge-pmo plugin 단독 (대안 A 채택)

**결정**: GitOpsAgent file = `mclayer/plugin-codeforge-pmo/agents/GitOpsAgent.md` 단독. PMOAgent 와 sibling teammate (같은 plugin 안 2번째 agent).

**거절된 대안**:
- (B) wrapper agent 신설 — ADR-009 invariant (wrapper-only decomposition, agent 0개) 위반. 기각.
- (C) 신규 plugin codeforge-gitops 신설 — 7번째 lane plugin overhead, single-purpose plugin = scope creep. lane plugin lifecycle (ADR-023) overhead 정당화 부족. 기각.
- (D) Orchestrator inline 유지 (현 상태) — 사용자 turn 3 design 의 "PMOAgent → GitRepoAgent → 작업 agent" flow 명시 의도 미반영 + 책임 비대화. 기각.

**근거**:
- PMOAgent 와 같은 plugin 안 sibling teammate 로 자연스러운 SendMessage 협업 (turn 3 verbatim "PMOAgent → GitRepoAgent → 작업 agent" flow 정합)
- ADR-009 wrapper-only invariant 무손상 (lane plugin 영역, wrapper agent 0개 유지)
- PMOAgent (Epic / Story 분해) + GitOpsAgent (branch tree / worktree lifecycle) = 2 cross-cutting agent 의 자연스러운 책임 분담
- single-purpose plugin (codeforge-gitops) overhead 회피 — codeforge family lane plugin 6개 유지

### D-2 — GitOpsAgent agent file schema (10 responsibility + peer_communication + permissions allow/deny)

**결정**: codeforge-pmo plugin `agents/GitOpsAgent.md` 신설. 10 responsibility + peer_communication + permissions allow/deny 명시:

```yaml
agent_name: GitOpsAgent
plugin: codeforge-pmo
role: Cross-cutting git operations orchestrator
spawn_pattern: long-running teammate (Story 전 기간 active — agent teams enabled context only)
peer_communication:
  - PMOAgent (sibling teammate, 같은 codeforge-pmo plugin)
  - All lane PL agents (sibling teammate, 다른 plugin — phase-scoped team active 시)
  - Orchestrator (lead)
permissions:
  allow:
    - Bash(scripts/worktree-*.sh)        # CFP-136 worktree script 호출
    - Bash(git worktree *)               # native git worktree
    - Bash(git branch *)
    - Bash(git merge --ff-only *)
    - Edit(.claude-work/worktree-manifest.yaml)
    - Edit(docs/stories/**)              # Story §10.5 self-write only
    - mcp__github__add_issue_comment     # [GitOps] prefix comment
    - SendMessage                        # peer 통신
  deny:
    - Agent                              # 재귀 spawn 금지 (NFR-2)
    - Edit(src/**)                       # implementation 영역 금지
    - Edit(docs/adr/**)                  # ADR write 금지 (chief author 영역)
    - Bash(git push *)                   # remote operation 금지
    - Bash(git fetch *)
    - Bash(git pull *)
```

**Responsibilities (10)**:
1. PMOAgent 분해 결과 (Epic→Story→sub_task hierarchy) SendMessage 수령
2. Hierarchical branch tree 생성 (`cfp-NNN[/<lane>[/<sub>]]` — ADR-024 Amendment 1 SSOT)
3. TeamCreate 직전 worktree N 개 동시 생성 + teammate cwd 보고 (CFP-136 script 호출, ADR-040 §결정 3 hook)
4. TeamDelete 직전 sub-worktree → lane branch sequential merge orchestration
5. 충돌 감지 시 lane PL teammate SendMessage (single-lane) 또는 PMOAgent escalation (cross-lane semantic)
6. FIX iteration worktree 재구성 (`cfp-NNN/fix-iter-<N>` branch + worktree)
7. Stale worktree 능동 detect + cleanup (7일+ + closed Story + origin absent — ADR-040 §결정 5 cross-ref)
8. Cross-platform path handling (Windows / macOS / Linux 일관 — ADR-040 §결정 4)
9. Worktree manifest write (`.claude-work/worktree-manifest.yaml` — pmo-output v1.1 worktree_manifest field source)
10. Story §10.5 "Git Ops Log" append (audit trail — append-only invariant, CFP-32 monopoly 패턴 mirror)

**거절된 대안**:
- (b) responsibility 5 추가 (예: PR creation / branch protection 자동화) — Orchestrator / lane PL 영역 침해. 기각.
- (c) responsibility 5 축소 (예: Stale GC 만 SessionStart hook 영역으로 분리) — turn 3 design 의 통합 책임자 의도 미반영. 기각.

**근거**: turn 3 verbatim 의 "PMOAgent 분해 → GitRepoAgent branch 생성 → 작업 agent" flow + "충돌 시 PMOAgent / lane PL 협업" 의도 정합. 10 responsibility = 단일 SendMessage 단위로 atomic, 재귀 spawn 금지 (NFR-2) 정합 — 모든 작업이 bash script + SendMessage 만으로 수행 가능.

### D-3 — git-ops-event-v1 신설 (codeforge-pmo canonical + wrapper sibling, ADR-010)

**결정**: 신규 inter-plugin contract `git-ops-event-v1` — codeforge-pmo canonical + wrapper sibling. ADR-010 sibling sync 정합.

**Event types (6)**:
- `WORKTREE_CREATE` — TeamCreate 직전 발화. payload: `{team_id, branch, worktree_path, teammate_id}`
- `WORKTREE_PRUNE` — TeamDelete 후 발화. payload: `{team_id, branch, worktree_path, prune_ok}`
- `BRANCH_MERGE_OK` — sub-worktree → lane branch sequential merge 성공
- `BRANCH_MERGE_CONFLICT` — 충돌 감지 시. payload: `{conflict_files[], peer_recipient, escalation_reason}`
- `BRANCH_TREE_DECOMPOSE` — PMOAgent 분해 결과 수령 후 branch tree 생성
- `STALE_GC` — SessionStart hook (7일+ + origin absent worktree gc)

**Schema = YAML frontmatter** (id, schema_version, plugin, kind, status) + §1 Producer (codeforge-pmo / GitOpsAgent) + §2 Consumer (Orchestrator + PMOAgent + lane PL) + §3 Schema (envelope + 6 event_type) + §4 변경 규칙 (ADR-008 SemVer + sibling sync ADR-010) + §5 Writer / Consumer boundary.

**MANIFEST.yaml**: kind:contract 6 → 7 entry append.

**상태**: PR #265 (`cfp-139-gitops-agent` branch) 에서 wrapper sibling + MANIFEST.yaml 7번째 entry 신설 완료. canonical (codeforge-pmo plugin) sync = Phase 2 PR pair scope.

**거절된 대안**:
- (b) git_ops_event 를 pmo-output v1.1 안 sub-schema 로 통합 — schema 단일 surface 비대화 + Producer (PMOAgent vs GitOpsAgent) 혼재 우려. 기각.

**근거**: ADR-010 sibling sync 정책 정합. 신규 contract = canonical (producer plugin) + wrapper sibling 의 dual file SSOT.

### D-4 — Story §10.5 Git Ops Log schema 신설 (templates/story-page-structure.md)

**결정**: `templates/story-page-structure.md` §10.5 신설 — GitOpsAgent self-write append-only ledger.

**Schema** (verbatim — git-ops-event-v1 §2.Markdown row 형식 정합):

```markdown
| Iter | 시각 | event_type | parent → child | outcome | triggered_by | ledger_entry |
|------|------|------------|----------------|---------|--------------|--------------|
| 1 | 2026-05-08T10:15:00Z | WORKTREE_CREATE | cfp-139 → cfp-139-gitops-agent | SUCCESS | Orchestrator | — |
| 2 | 2026-05-08T11:42:00Z | BRANCH_MERGE_OK | cfp-139/design → cfp-139 | SUCCESS | DesignReviewPL | — |
| 3 | 2026-05-08T14:20:00Z | BRANCH_MERGE_CONFLICT | cfp-139/impl/api → cfp-139/impl | CONFLICT | DeveloperPL | "src/api.ts:120-145" |
```

**Owner**: GitOpsAgent (codeforge-pmo plugin) — `Edit(docs/stories/**)` 권한 (D-2 permissions allow-list).

**Append-only invariant**: row 삭제·수정 금지 (CFP-32 monopoly 패턴 mirror — §10 FIX Ledger Orchestrator monopoly 와 동일 invariant). 위반 시 `check-doc-section-schema.sh` warning (Phase 1) → P0 승격 follow-up CFP candidate.

**상태**: PR #265 에서 templates/story-page-structure.md §10.5 schema 신설 완료.

**거절된 대안**:
- (b) §10 FIX Ledger 안 통합 (별도 row 종류로 mix) — Orchestrator monopoly invariant (CFP-32) 위반. 기각.

**근거**: Owner / writer 분리 — §10 = Orchestrator monopoly, §10.5 = GitOpsAgent monopoly. 동일 file 안 section-level 분리로 race condition 회피 (§5.2 EC-2).

### D-5 — pmo-output-v1 → v1.1 MINOR bump (worktree_manifest optional field)

**결정**: `docs/inter-plugin-contracts/pmo-output-v1.md` schema_version "1.0" → "1.1" — `worktree_manifest` optional field 추가:

```yaml
worktree_manifest:                # NEW in v1.1, optional (required: false)
  story_key: CFP-NNN
  base_path: ${HOME}/.claude/worktrees/<repo>/
  worktrees:
    - branch: cfp-NNN/<lane>/<sub>
      path: <absolute>
      teammate_id: <id>
      created_at: ISO8601
      pruned_at: ISO8601 | null
```

**MINOR bump 근거** (ADR-008): 신규 optional field 추가 (consumer 후방 호환). v1.0 producer 가 worktree_manifest 미포함 시에도 schema valid.

**Authoritative SSOT**: `.claude-work/worktree-manifest.yaml` (GitOpsAgent self-write 영역). pmo-output v1.1 worktree_manifest field = read-only mirror — PMOAgent 가 GitOpsAgent SendMessage 결과 받아 자기 contract 에 mirror (sibling teammate 협업 결과 통합).

**Sibling sync** (ADR-010): wrapper sibling + canonical (codeforge-pmo) 동시 갱신 의무. canonical = Phase 2 PR pair 영역.

**MANIFEST.yaml**: pmo_output entry version "1.0" → "1.1" 갱신 + status: Active 유지 (NO Archive — MINOR backward compat).

**거절된 대안**:
- (b) MAJOR bump v2.0 — 기존 field 삭제 / rename 없음 (additive minor 충분). 기각.

**근거**: ADR-008 SemVer (additive minor). consumer breaking 없음 — 기존 field 유지 + 신규 optional field.

### D-6 — comment-prefix-registry-v1 patch bump (`[GitOps]` prefix 추가)

**결정**: `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` v1.0 → v1.1 patch bump (현재 `version: "1.0"` → "1.1" — append-only for v1.x rule 정합).

**신규 prefix entry**:

```yaml
- prefix: "[GitOps]"
  phase: gitops
  current_owner: codeforge-pmo (GitOpsAgent self-write)
  target_owner_plugin: codeforge-pmo
  posters:
    - GitOpsAgent
  auto_mirror: false
```

**근거**: GitOpsAgent 가 PR / Issue comment 시 `[GitOps]` prefix 사용 — phase prefix taxonomy 11 → 12. comment-prefix-registry §변경 규칙 "Append-only for v1.x" 정합.

**충돌 검사**: 기존 11 prefix (요구사항 / 설계 / 설계-리뷰 / 구현 / 구현-리뷰 / 구현-테스트 / 보안-테스트 / PMO / FIX #N / 완료 / Preflight) 와 충돌 없음.

### D-7 — wrapper CLAUDE.md "Development Agent Team" 표 sync

**결정**: wrapper `CLAUDE.md` "Development Agent Team" composition map 표에서 `codeforge-pmo` row 갱신:

**Before**: `| Cross-cutting | codeforge-pmo | 1 (PMOAgent) | ... |`
**After**: `| Cross-cutting | codeforge-pmo | 2 (PMOAgent + GitOpsAgent) | ... |`

**근거**: codeforge-pmo plugin 의 agent count 가 1 → 2 (GitOpsAgent 신설). Composition map SSOT 정합. 다른 lane row 무영향.

### D-8 — Sibling sync 의무 = codeforge-pmo plugin Phase 2 PR pair (ADR-010)

**결정**: ADR-010 sibling sync 정책 정합 — wrapper Phase 1 PR (#265) 와 codeforge-pmo plugin Phase 2 PR same Story 안 atomic merge 의무.

**Sibling 영역 (Phase 2 PR scope)**:
- codeforge-pmo `agents/GitOpsAgent.md` — NEW (10 responsibility + peer_communication + permissions allow/deny)
- codeforge-pmo `CLAUDE.md` — "Self-write 책임" 표에 GitOpsAgent row + agent count 1 → 2 + PMOAgent ↔ GitOpsAgent 협업 도식
- codeforge-pmo `docs/inter-plugin-contracts/git-ops-event-v1.md` — canonical (wrapper sibling verbatim mirror)
- codeforge-pmo `docs/inter-plugin-contracts/pmo-output-v1.md` — canonical v1.1 (wrapper sibling verbatim mirror)
- ADR-040 Amendment 1 finalize (GitOpsAgent hook 실행 주체 명시) — Phase 2 PR pair scope

**거절된 대안**:
- (b) wrapper-only PR — codeforge-pmo plugin 정합 부재 시 GitOpsAgent agent file invalid (mandate amendment 미반영, agent 가 자기 역할 trigger 모름). 기각.

**근거**: ADR-010 cross-plugin sibling sync 정합. Wrapper Phase 1 PR #265 = contract / template / wrapper CLAUDE.md sync + ADR-047. codeforge-pmo Phase 2 PR pair = agent file 신설 + plugin CLAUDE.md amendment + canonical contract sync + ADR-040 Amendment 1 finalize.

## 대안 검토

### 대안 A — GitOpsAgent in codeforge-pmo plugin (채택 — D-1)

- 채택 사유: §결정 D-1 verbatim. PMOAgent 와 sibling teammate, ADR-009 invariant 무손상, turn 3 design flow 정합.

### 대안 B — Wrapper agent 신설 (β)

- wrapper repo 의 `agents/` 디렉토리에 GitOpsAgent.md 추가
- 거부 사유: ADR-009 §결정 1 (wrapper-only decomposition, agent 0개) violation. ζ arc end-state 일관성 파괴.

### 대안 C — 신규 plugin codeforge-gitops (γ)

- 7번째 lane plugin 신설 (single-purpose, GitOpsAgent 단독 plugin)
- 거부 사유:
  - lane plugin lifecycle (ADR-023) overhead 정당화 부족 (10 responsibility = 단일 plugin 단위 비대화 미해당)
  - codeforge family 6 lane plugin → 7 plugin = scope creep
  - PMOAgent ↔ GitOpsAgent 협업 (turn 3 design verbatim) 이 cross-plugin SendMessage = ADR-044 §결정 1 정합 가능하지만 같은 plugin sibling teammate 보다 자연스러움 약화

### 대안 D — Orchestrator inline 유지 (δ)

- 현 상태 (Orchestrator 가 worktree create / merge / conflict escalation 직접 inline 처리)
- 거부 사유:
  - Orchestrator 책임 비대화 (이미 토큰 예산 owner + 모든 spawn 책임)
  - 사용자 turn 3 design 의 "PMOAgent → GitRepoAgent → 작업 agent" flow 명시 의도 미반영
  - 사용자 turn 10 confirm "있는게 나을텐데" verbatim 거부

## 결과

긍정:
- ADR-035 D-2 + D-3 Foundation 결정 implementation 충족 (CFP-134 Wave 3)
- 사용자 directive (turn 3 + turn 10) verbatim 정합
- ADR-009 wrapper-only invariant 무손상 (wrapper agent 0개 유지)
- ADR-010 sibling sync 패턴 정합 (canonical + sibling dual file SSOT)
- PMOAgent + GitOpsAgent = 2 cross-cutting agent 자연스러운 책임 분담 (cross-plugin SendMessage 회피)
- env=0 fallback 동작 정의 (NFR-5 — default subagent context backward compat)
- worktree management orchestrator 책임 위임 → Orchestrator 토큰 예산 절약
- audit trail visibility (Story §10.5 ledger + git-ops-event-v1 contract)

부정:
- agent teams enabled context (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) prerequisite — env=0 시 미spawn (NFR-5 fallback)
- codeforge-pmo plugin agent count 1 → 2 = wrapper CLAUDE.md / consumer-guide sync 의무 (D-7 + Phase 2 follow-up CFP scope)
- Phase 2 PR pair sibling sync 의무 (codeforge-pmo plugin canonical + agent file + plugin CLAUDE.md) — ADR-010 절차 follow
- Phase 2 e2e fixture = trace log only (Q2 default A) — actual env=1 live test 후속 CFP defer (mctrader debut audit 까지)

### Reversibility

Yes. Rollback 경로 (Change Plan §5.2 verbatim):

1. **즉시 disable** (env-level): `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0` 설정 → GitOpsAgent 미spawn (env=0 fallback 진입). 모든 worktree management = Orchestrator inline 복귀.
2. **단계적 revert**:
   - codeforge-pmo `agents/GitOpsAgent.md` 삭제
   - codeforge-pmo `CLAUDE.md` self-write 책임 표 GitOpsAgent row revert + agent count 2 → 1
   - codeforge-pmo `docs/inter-plugin-contracts/git-ops-event-v1.md` canonical 삭제
   - codeforge-pmo `docs/inter-plugin-contracts/pmo-output-v1.md` v1.1 → v1.0 revert
   - wrapper `docs/inter-plugin-contracts/git-ops-event-v1.md` sibling 삭제
   - wrapper `docs/inter-plugin-contracts/MANIFEST.yaml` 7번째 entry 삭제
   - wrapper `docs/inter-plugin-contracts/pmo-output-v1.md` v1.1 → v1.0 revert
   - wrapper `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` v1.1 → v1.0 revert (`[GitOps]` prefix 삭제)
   - wrapper `CLAUDE.md` "Development Agent Team" 표 revert (agent count 2 → 1)
   - wrapper `templates/story-page-structure.md` §10.5 section 삭제
   - 본 ADR-047 status: Accepted → Deprecated
3. 이미 작성된 Story §10.5 row 보존 (audit trail 유지 — append-only invariant 정합)
4. 이미 생성된 worktree (`.claude/worktrees/**`) leave as-is — SessionStart hook (CFP-136 stale GC) 가 7일+ origin absent 검출 후 자연 cleanup

## Out-of-scope

- **Phase 2 e2e fixture = actual env=1 agent teams enabled live test** — Q2 default A 정합 (trace log only, mctrader debut audit 까지 follow-up CFP defer)
- **Consumer-side `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 안내 가이드** — `docs/consumer-guide.md` 후속 안내 별도 sibling sync follow-up CFP
- **PR creation / branch protection 자동화** — Orchestrator / lane PL 영역 침해, GitOpsAgent permissions deny-list 정합
- **Stale GC max parallel worktree count config** — Phase 2 follow-up CFP 후보 (예: 16 max parallel), 본 ADR scope 외
- **§10.5 lint P0 승격** — 현재 `check-doc-section-schema.sh` warning level. 별도 follow-up CFP 가능
- **새 event_type 추가** (예: `worktree_gc_bypassed`, `fix_iter_worktree_create`) — git-ops-event-v1 §변경 규칙 정합 별도 MINOR bump CFP

## 해소 기준

N/A — permanent policy

## 관련 파일

- `docs/inter-plugin-contracts/git-ops-event-v1.md` (NEW — wrapper sibling, PR #265 done)
- `docs/inter-plugin-contracts/pmo-output-v1.md` (v1.0 → v1.1 MINOR bump)
- `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` (v1.0 → v1.1 patch)
- `docs/inter-plugin-contracts/MANIFEST.yaml` (kind:contract 6 → 7 entry + pmo_output version 갱신)
- `templates/story-page-structure.md` §10.5 신설 (PR #265 done)
- `CLAUDE.md` "Development Agent Team" 표 codeforge-pmo row 갱신
- `<internal-docs>/wrapper/change-plans/cfp-139-gitops-agent.md` (Change Plan)
- `<internal-docs>/wrapper/stories/CFP-139.md` §3 / §7 / §11 채움 + frontmatter status: phase:설계 + plan
- (Phase 2 PR pair) codeforge-pmo `agents/GitOpsAgent.md` (NEW)
- (Phase 2 PR pair) codeforge-pmo `CLAUDE.md` Self-write 책임 표 amendment
- (Phase 2 PR pair) codeforge-pmo `docs/inter-plugin-contracts/git-ops-event-v1.md` (canonical sync)
- (Phase 2 PR pair) codeforge-pmo `docs/inter-plugin-contracts/pmo-output-v1.md` (canonical v1.1 sync)
- `docs/adr/ADR-040-worktree-convention.md` Amendment 1 finalize (Phase 2 PR pair scope)

## 관련 ADR

- **ADR-008** Inter-plugin contract versioning: 본 ADR 의 git-ops-event-v1 신설 (initial v1.0) + pmo-output v1.1 MINOR bump + comment-prefix-registry v1.1 patch bump 모두 SemVer 정합.
- **ADR-009** wrapper-only decomposition: 본 ADR = codeforge-pmo plugin 의 2번째 agent 신설. wrapper agent 0개 invariant 무손상. ζ arc end-state 일관성 보존.
- **ADR-010** Inter-plugin contract sibling sync: 본 ADR 의 git-ops-event-v1 + pmo-output v1.1 = canonical (codeforge-pmo) + wrapper sibling 의무 sync. Phase 2 PR pair 절차 정합.
- **ADR-013** codeforge family dogfood-out: 본 ADR carrier Story (CFP-139) + Change Plan (cfp-139-gitops-agent.md) = `mclayer/codeforge-internal-docs:wrapper/` 영역. dogfood-out 정합.
- **ADR-024 + Amendment 1** Story-scoped branch policy: GitOpsAgent 가 branch 생성 시 hierarchical naming `cfp-NNN[/<lane>[/<sub>]]` SSOT 사용. main 직접 push 차단 invariant 무손상.
- **ADR-035** codeforge agent teams Epic SSOT: 본 ADR = D-2 worktree convention + D-3 GitOpsAgent foundation 결정 implementation. amendment_log[] 에 `amendment_id: 3 (CFP-139)` 추가 의무 (codeforge-pmo Phase 2 PR pair scope).
- **ADR-039** Orchestrator subagent default: env=0 fallback (default subagent context) 시 GitOpsAgent 미spawn → Orchestrator inline 복귀. NFR-5 정합.
- **ADR-040** Worktree convention SSOT: GitOpsAgent 가 호출하는 worktree script + base path / branch hierarchy / cross-platform path = ADR-040 §결정 1-4 verbatim. Amendment 1 (GitOpsAgent hook 실행 주체 명시) Phase 2 PR pair scope 에서 finalize.
- **ADR-044** Phase-scoped sequential team: GitOpsAgent = long-running teammate (Story 전 기간 active). agent teams enabled context (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) prerequisite. SendMessage scope 제약 정합 — peer = PMOAgent + lane PL + Orchestrator 만, lane plugin deputy / worker SendMessage 금지.
