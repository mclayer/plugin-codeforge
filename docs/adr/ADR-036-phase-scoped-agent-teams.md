---
adr_number: 36
title: Phase-scoped sequential agent teams policy (CFP-134 Epic)
status: Proposed
category: Team & Process
date: 2026-05-08
related_files:
  - docs/adr/ADR-009-wrapper-only-decomposition.md
  - docs/adr/ADR-035-worktree-convention.md
  - docs/orchestrator-playbook.md
  - docs/inter-plugin-contracts/review-verdict-v4.md
  - templates/team-spec-*.yaml
  - docs/consumer-guide.md
parent_epic: CFP-134
carrier_story: CFP-137
---

# ADR-036: Phase-scoped sequential agent teams policy

## 상태

**Proposed (2026-05-08)** — CFP-137 carrier, CFP-134 Epic Wave 2 (agent teams policy). CFP-136 (worktree convention, ADR-035) Accepted 후 본 ADR 진입. Effective date = Phase 2 wrapper PR merge timestamp (ADR-031 §14 freeze pattern 재사용 — 본 effective date 이전 Phase 1 PR open 된 Story = grandfather, retroactive 강제 없음).

## 컨텍스트

사용자 directive (2026-05-08 conversation, claude-opus-4-7 wrapper session):

> agent teams 기능을 적극적으로 사용할 수 있도록 ... 토큰의 양 효율성은 중요하지 않다.

> 서로 의존적이지 않은 작업은 병렬 실행하고 worktree해서 작업해도 되겠지?

Claude Code agent teams (experimental, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) 활용 — Lane PL ↔ Lane PL coordination + Lane PL ↔ Worker continuous dialog + Parallel diagnosis + Worktree isolation 통합. 기존 ADR-009 (wrapper-only decomposition) 의 "subagent one-shot" 제약 (PL ↔ 서브 continuous dialog 불가 → PL 이 Orchestrator 에 재 spawn 의뢰) 회피.

### 현재 상태

- 모든 lane spawn = one-shot subagent (Agent tool 단발 호출). PL ↔ worker dialog 부재 → 매 round trip 마다 Orchestrator 경유.
- ADR-022 (Sonnet decider 5-trigger 자동 발동) — 본 Epic D1 결정으로 deprecate 대상 (사용자 ad-hoc only).
- Worktree convention (ADR-035, CFP-136) Wave 1 prerequisite — file isolation SSOT.

### Platform 제약 (verified)

- **One team per lead**: 동시 2 teams 불가. Lead 가 team A 보유 중에 team B 생성 시 platform reject.
- **No nested teams**: teammate 가 자기 team 못 만듦. team 의 lead 는 1 hop 만.
- **Lead is fixed**: mid-session 변경 불가. team create 시점의 lead = 영구 고정.
- **No session resumption**: in-process teammates `/resume` 후 사라짐. Session 재개 시 team state lost.
- **Best practice 3-5 teammates**: 6+ teammate 시 lead coordination overhead 급증.
- **25 thread limit**: 동일 session 내 thread 누적 ≤ 25.

### Gap

- one-team-per-lead 제약 하에서 7 lane × parallel team 동시 보유 불가능.
- Lane 진입 시점 dynamic team composition (Live touching 시 deputy +2) 처리 mechanism 부재.
- review-verdict 의 PL synthesis only / decider field (ADR-022 잔재) 가 본 Epic D1 결정과 충돌.

## 결정

### 결정 1 — Phase-scoped sequential team

1 lane 진입 = 1 team create → lane 완료 = TeamDelete → 다음 lane = 새 team. one-team-per-lead 제약 회피의 유일한 안전 패턴.

```
[Lane N 진입]
  ├── Orchestrator: TeamCreate(lane=N, members=[PL, worker1, worker2, ...])
  ├── Lane PL ↔ workers continuous dialog (SendMessage / TaskList)
  ├── Lane 완료 → final verdict
  └── Orchestrator: TeamDelete(lane=N)
[Lane N+1 진입]
  └── 새 team create (composition 다름)
```

**근거**: 7 lane 동시 team 보유 시 platform one-team-per-lead reject. sequential team = 안전 + lifecycle 명확. 토큰 비용 ~7x baseline 은 사용자 explicit 무관 directive (turn 5).

### 결정 2 — Lane × Team composition

| Team | 시점 | 멤버 수 | 구성 |
|---|---|---|---|
| **TEAM-DECOMPOSE** | Stage 1 (Epic 분해 필요 시) | 2 | Orchestrator + PMOAgent |
| **TEAM-REQUIREMENTS** | Phase 1 — 요구사항 lane | 4 | RequirementsPL + DomainAgent + RequirementsAnalyst + Researcher |
| **TEAM-DESIGN** | Phase 1 — 설계 lane | 8 (Live touching 시 +2 = 10) | ArchitectPL + ArchitectAgent (chief) + 6 deputy (CodebaseMapper / Refactor / SecurityArch / OpRiskArch / TestContractArch / DataMigrationArch) [+ LiveOps + LiveOrdering CONDITIONAL] |
| **TEAM-DESIGN-REVIEW** | Phase 1 — 설계 리뷰 lane | 3 | DesignReviewPL + ClaudeReviewWorker + CodexReviewWorker |
| **TEAM-DEVELOP** | Phase 2 — 구현 lane | 5–7 (preset 따라) | DeveloperPL + QADev + N role:dev (preset 결정) |
| **TEAM-CODE-REVIEW** | Phase 2 — 구현 리뷰 lane | 3 | CodeReviewPL + ClaudeReviewWorker + CodexReviewWorker |
| **TEAM-TEST** | Phase 2 — 구현 테스트 lane | 1 (no team — single agent) | TestAgent (one-shot, team 미생성) |
| **TEAM-SECURITY-TEST** | Phase 2 — 보안 테스트 lane | 3 | SecurityTestPL + ClaudeReviewWorker + CodexReviewWorker |
| **TEAM-RETRO** | Phase 2 close — 의무 자동 spawn (CFP-138) | 2 | PMOAgent + RetroSynthesizer |
| **TEAM-FIX** | FIX iteration — ad-hoc parallel diagnosis | 3–5 | DeveloperPL + ArchitectPL + (relevant deputy / worker) |

**근거**: best practice 3–5 teammate 준수 (TEAM-DESIGN 8–10 = exception, ArchitectAgent chief 가 sub-coordinator 역할). TEAM-TEST 1명 = team overhead ROI 없음. TEAM-RETRO = CFP-138 의무화 (사용자 turn 9).

### 결정 3 — 5 권장 패턴 적용

Anthropic agent teams docs 의 5 권장 패턴 mapping:

| 패턴 | 본 Epic 적용 |
|---|---|
| **Specialization** | TEAM-DESIGN 의 6 deputy = 각 sub-domain 전문화 (security / op-risk / test contract / data migration / codebase mapper / refactor) |
| **Parallelization** | TEAM-FIX 의 DeveloperPL + ArchitectPL parallel diagnosis (CFP-19 R4 패턴) |
| **Adversarial-Debate** | TEAM-DESIGN-REVIEW / TEAM-CODE-REVIEW / TEAM-SECURITY-TEST 의 Claude vs Codex worker = independent finding → PL synthesis |
| **Cross-layer** | TEAM-DESIGN 의 ArchitectAgent chief ↔ deputy = chief-deputy 2 layer (chief 가 §3 author, deputy 가 §7 / §11 sub-section author) |
| **Escalation** | TEAM-FIX 가 lane plugin team 에서 escalate 받아 cross-lane diagnosis |

**Anti-pattern 회피**:
- *too many teammates*: TEAM-DESIGN 8–10 = ArchitectAgent chief 가 sub-coordinator 역할 분담으로 mitigation. 11+ 멤버 team 금지.
- *sequential as parallel*: SendMessage 가 sequential dialog 인 점 인지 — 실 parallel 작업은 worktree 별 isolated dispatch.
- *same file edit*: ADR-035 worktree isolation 으로 file 충돌 0 보장.
- *lead doing work*: Lane PL = synthesis + dispatch 만, content authoring 은 worker 위임.
- *no sync points*: 매 lane 종료 시 final verdict = sync point. TEAM-FIX 종료 시 root-cause decision = sync point.

### 결정 4 — Worktree integration (ADR-035 정합)

각 teammate = 자기 worktree (file 충돌 0). Orchestrator 가 lane spawn 직전 worktree 생성 + path 주입.

```
on_team_create_pre   → GitOpsAgent (CFP-139) creates worktrees per teammate
                       (ADR-035 §결정 3 lifecycle hook)
on_team_create_post  → each teammate spawned with cwd = worktree_path
on_team_delete_pre   → GitOpsAgent merges worktrees → lane sub-branch (sequential)
on_team_delete_post  → GitOpsAgent prunes worktrees
```

worktree path = `${HOME}/.claude/worktrees/<repo-name>/<branch-name-flatten>` (ADR-035 §결정 1). Lane sub-branch naming = `cfp-NNN/lane/<lane-name>` (ADR-035 §결정 2). 각 deputy / worker = `cfp-NNN/lane/<lane>/<sub>` 별도 worktree.

**근거**: ADR-035 의 prerequisite 충족 — phase-scoped agent teams 가 lane parallel spawn 시 file isolation 의무.

### 결정 5 — review-verdict v4 (decider field 제거)

기존 review-verdict v3 의 PL synthesis only + Sonnet decider auto-invoke 패턴은 ADR-022 deprecate (CFP-134 D1) 으로 무효. v4 schema 신규:

```yaml
# review-verdict-v4 (PL = final author, decider field removed)
version: 4
lane: design-review | code-review | security-test
iteration: <N>
findings: [...]
pl_recommendation: PASS | FIX | FIX_DISCRETIONARY  # = final verdict
# decider field REMOVED (v3 → v4 BREAKING)
# sonnet_final_status field REMOVED
```

PL = final pl_recommendation 직접 작성 (PL synthesis only 무효 — CFP-134 D1 정정). Sonnet decider auto-invoke 무효 (ADR-022 Superseded).

**Versioning**: v3 → v4 = BREAKING (decider field 제거). [ADR-008](ADR-008-inter-plugin-contract-versioning.md) major bump. Sibling sync (codeforge-review canonical → wrapper sibling) — [ADR-010](ADR-010-inter-plugin-contract-sibling-sync.md) 절차.

**근거**: 사용자 turn 7-8 directive — "Codex review / Sonnet decider 는 codeforge 1st-class 가 아니라 사용자 ad-hoc only". 본 Epic D1 deprecate 와 정합.

### 결정 6 — Codex / Sonnet = 사용자 ad-hoc only

codeforge agent teams 의 영구 멤버 아님. 사용자 explicit request 시에만 ad-hoc spawn:

- **Codex**: `codex:rescue` skill (사용자 explicit 호출). codeforge lane 자동 발동 금지.
- **Sonnet**: Agent tool with `model: claude-sonnet-4-6` (사용자 explicit 호출). 본 ADR 의 어느 team 에도 영구 멤버로 포함 안 됨.

**근거**: 사용자 turn 7 명시 — "사용자 stop이 너무 많아 내가 필요할 때마다만 요청하는 것이지 codeforge가 이를 반영해서 임의로 수행해서는 안된다". memory 3 항목 (`feedback_codex_review_auto_proceed.md` / `feedback_no_clarification_default.md` / `feedback_decider_protocol.md`) 동시 삭제 (CFP-134 D1).

### 결정 7 — 환경 변경 의무

사용자 settings.json 에 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env 의무. consumer-guide.md 안내 + SessionStart hook 검증 (env 미설정 시 warning + 본 ADR link 제시).

```jsonc
// .claude/settings.json or ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**근거**: experimental feature → opt-in 명시. CFP-138 retro 의무화 / CFP-139 GitOpsAgent 도 본 env 의존.

## 결과

### 긍정

- **Lane PL ↔ Worker continuous dialog 가능**: SendMessage / TaskList 로 round trip Orchestrator 경유 제거. PL 이 worker 에 follow-up Q 직접 가능.
- **Cross-lane SendMessage coordination**: TEAM-FIX 가 DeveloperPL ↔ ArchitectPL 직접 dialog. CFP-19 R4 parallel diagnosis 의 자연스러운 구현.
- **Parallel diagnosis (FIX iteration)**: TEAM-FIX 의 ad-hoc 3–5 멤버 = root-cause 신속 수렴.
- **Worktree isolation = file 충돌 0**: ADR-035 정합으로 multi-worker file 동시 write 안전.
- **Token cost ~7x baseline (사용자 무관 directive)**: turn 5 명시 — "토큰의 양 효율성은 중요하지 않다".

### 부정 / 비용

- **Token cost ~7x baseline**: best-case Story 1개 = team × 7 lane × 3-8 멤버 × continuous dialog round. 사용자 acceptable directive.
- **Experimental status**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` flag = production stability 모니터링 의무. Anthropic 이 flag 제거 / API 변경 시 본 ADR amendment 필요.
- **25 thread limit**: 동일 session 내 thread 누적 추적 의무. 한도 초과 시 Orchestrator 가 lane 진입 전 force compaction trigger.
- **Lead fixed 제약**: Orchestrator = 영구 lead. Story 중간 Orchestrator 교체 불가 (session 재시작 의무).

### 위험

- **No session resumption**: `/resume` 후 in-process teammates 사라짐 → 진행 중 lane state lost. Mitigation = (a) lane 종료 시점에 §14 Lane Evidence row append (ADR-031), (b) `/resume` 후 lane re-entry 시 team 재생성, (c) GitOpsAgent (CFP-139) 가 worktree state 보존.
- **Platform reject (one-team-per-lead)**: 본 결정 1 sequential team 으로 회피. 단 GitOpsAgent (CFP-139) 가 long-running teammate 로 전 phase 보유 — 본 ADR §결정 1 sequential 적용 안 됨, GitOpsAgent 는 Orchestrator 가 lead 로 보유 (sub-team 생성 불가).
- **Best practice 위반 (TEAM-DESIGN 8-10)**: ArchitectAgent chief 가 sub-coordinator → 11+ 시 본 ADR amendment 의무.

## 대안 고려

| 대안 | 채택 안 한 이유 |
|---|---|
| **Permanent multi-team (모든 lane team 동시 보유)** | one-team-per-lead 제약 위반. platform reject. |
| **PL 구조 제거 (모든 agent 가 lead)** | 사용자 turn 6 질문 → turn 8 답변에서 "적극 도입" = 기존 PL 구조 유지. PL = team lead 자연스러운 mapping. |
| **One-shot subagent 유지 (현재 패턴)** | 사용자 turn 5 directive 명시 위배. PL ↔ worker dialog 부재 통증 지속. |
| **Sonnet / Codex permanent team member** | 사용자 turn 7 directive 위배 — ad-hoc only. ADR-022 deprecate 정합. |
| **Conservative partial 도입 (일부 lane 만 team)** | 본 Epic D2 = "적극 도입". partial 은 사용자 directive 부합 안 됨. |

## 관련 ADR

- [ADR-009 (wrapper-only decomposition)](ADR-009-wrapper-only-decomposition.md) — wrapper agent 0 개 invariant 정합 (본 ADR = 인프라 / lifecycle 정책, agent 추가 아님).
- [ADR-035 (worktree convention)](ADR-035-worktree-convention.md) — file isolation prerequisite. 본 ADR §결정 4 가 ADR-035 lifecycle hook 의존.
- [ADR-022 (Sonnet review-verdict decider)](ADR-022-sonnet-review-verdict-decider.md) — CFP-134 D1 deprecate 대상. 본 ADR §결정 5 + §결정 6 정합.
- [ADR-031 (lane spawn evidence)](ADR-031-lane-spawn-evidence-trail.md) — 위험 mitigation (no session resumption) 의 Lane Evidence row 패턴 차용.
- [ADR-008 (inter-plugin contract versioning)](ADR-008-inter-plugin-contract-versioning.md) — review-verdict v3 → v4 BREAKING bump 룰.
- [ADR-010 (sibling sync)](ADR-010-inter-plugin-contract-sibling-sync.md) — review-verdict v4 canonical/sibling 절차.
- **CFP-134** — Epic carrier (worktree infrastructure + agent teams + GitOpsAgent + retro 의무화).
- **CFP-136** — ADR-035 carrier Story (worktree infra Wave 1, prerequisite).
- **CFP-137** — 본 ADR carrier Story (agent teams Wave 2).
- **CFP-138** — retro 의무화 (TEAM-RETRO 자동 spawn).
- **CFP-139** — GitOpsAgent (lifecycle 자동화, 본 ADR §결정 4 hook 구현).

## 관련 파일

- [`docs/adr/ADR-009-wrapper-only-decomposition.md`](ADR-009-wrapper-only-decomposition.md) — wrapper agent 0개 invariant.
- [`docs/adr/ADR-035-worktree-convention.md`](ADR-035-worktree-convention.md) — worktree base directory + naming + lifecycle.
- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) — §3 lane spawn sequence (본 ADR effective 후 team-based 으로 갱신).
- [`docs/inter-plugin-contracts/review-verdict-v4.md`](../inter-plugin-contracts/review-verdict-v4.md) — v3 → v4 BREAKING bump (decider field 제거).
- [`templates/team-spec-*.yaml`](../../templates/) — 9 team composition fixture (TEAM-DECOMPOSE / TEAM-REQUIREMENTS / TEAM-DESIGN / TEAM-DESIGN-REVIEW / TEAM-DEVELOP / TEAM-CODE-REVIEW / TEAM-SECURITY-TEST / TEAM-RETRO / TEAM-FIX).
- [`docs/consumer-guide.md`](../consumer-guide.md) — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env 안내.
