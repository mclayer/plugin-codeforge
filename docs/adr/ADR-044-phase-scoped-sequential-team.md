---
adr_number: 44
title: Phase-scoped sequential team SSOT (CFP-134 Epic Wave 2)
date: 2026-05-09
status: Proposed
category: orchestration
carrier_story: CFP-137
parent_epic: CFP-134
supersedes: null
amends: null
related_stories:
  - CFP-134
  - CFP-135
  - CFP-136
  - CFP-137
  - CFP-139
  - CFP-391  # Amendment 1 (2026-05-11) — dispatch_mode auto_on_divergence 추가
amendment_log:
  - date: 2026-05-11
    cfp: CFP-391
    summary: "§결정 2 dispatch_mode enum 에 auto_on_divergence 추가. ADR-059 carrier debate-protocol-v1 자동 발동 mode."
    affected_sections: ["§결정 2"]
    breaking: false
related_adrs:
  - ADR-009  # wrapper-only decomposition (Orchestrator 단일 lead 정합)
  - ADR-022  # Deprecated by ADR-035 — review-verdict v4 cutover 동기
  - ADR-024  # Story-scoped branch policy (Amendment 1 = hierarchical naming, ADR-040 동행)
  - ADR-031  # Lane-spawn evidence trail (§14 row append, hook 연계)
  - ADR-035  # Epic architecture SSOT (D2 phase-scoped agent teams 의 implementation level)
  - ADR-039  # Orchestrator subagent default (default subagent context vs enabled context 분기)
  - ADR-040  # Worktree convention (TeamCreate / Delete + worktree integration 의존)
related_files:
  - docs/orchestrator-playbook.md
  - docs/consumer-guide.md
  - docs/inter-plugin-contracts/review-verdict-v4.md
  - docs/inter-plugin-contracts/MANIFEST.yaml
  - docs/domain-knowledge/agent-teams/agent-teams-platform-capability.md
  - templates/team-spec-decompose.yaml
  - templates/team-spec-requirements.yaml
  - templates/team-spec-design.yaml
  - templates/team-spec-design-review.yaml
  - templates/team-spec-develop.yaml
  - templates/team-spec-code-review.yaml
  - templates/team-spec-security-test.yaml
  - templates/agent-teams-hook-samples/TeammateIdle.json.sample
  - templates/agent-teams-hook-samples/TaskCreated.json.sample
  - templates/agent-teams-hook-samples/TaskCompleted.json.sample
  - CLAUDE.md
---

# ADR-044: Phase-scoped sequential team SSOT

## 상태

**Proposed (2026-05-09)** — CFP-137 carrier, CFP-134 Epic Wave 2 (agent teams 적극 도입). Effective date = 본 ADR 가 포함된 wrapper Phase 1 PR merge timestamp + 사용자 측 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` settings.json 활성 + 신규 세션 재시작 (Story §4.3 prerequisite).

본 ADR 의 Epic-level architecture 결정 SSOT = [ADR-035](ADR-035-codeforge-agent-teams-epic-architecture.md) (D2 = Agent teams 적극 도입). 본 ADR = D2 의 **implementation level SSOT** — phase-scoped sequential team 의 lifecycle / team-spec yaml 7종 / hook 3종 / review-verdict v3 → v4 cutover / 5 권장 패턴 measurable verification 정의.

본 Story spec SSOT = [`mclayer/codeforge-internal-docs:wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-05-08-cfp-134-codeforge-agent-teams-epic-design.md) §4.3 (CFP-137 부분).

## 컨텍스트

사용자 directive (2026-05-08, CFP-134 Epic brainstorming):

> "agent teams 기능을 적극적으로 사용할 수 있도록... 토큰의 양 효율성은 중요하지 않다."

> "codex review와 sonnet decider를 codeforge의 일환으로 보는 것 같은데 그건 아니다. 사용자 stop이 너무 많아 내가 필요할 때마다만 요청하는 것이지 codeforge가 이를 반영해서 임의로 수행해서는 안된다."

### 현재 상태

- ADR-009 (wrapper-only decomposition, Adopted) — Orchestrator (top-level Claude 세션) 단일 lead invariant.
- ADR-022 (Sonnet decider 5-trigger 자동 발동) = **Deprecated by ADR-035** (CFP-134, 2026-05-08). 사용자 ad-hoc 호출 전용.
- ADR-024 + ADR-040 (Worktree convention) — `cfp-NNN[/<lane>[/<sub>]]` hierarchical naming + base directory + lifecycle hook contract.
- ADR-031 (Lane-spawn evidence trail) — Story §14 row append (Orchestrator self-write monopoly, Amendment 1 으로 delegate subagent 포함).
- ADR-035 (Epic architecture, Accepted) — D2 = Phase-scoped sequential team 적극 도입.
- ADR-039 (Orchestrator subagent default, Accepted) — default subagent context 의 always-spawn invariant. Inline whitelist 4-entry closed.
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env = Claude Code experimental feature 활성. TeamCreate / TeamDelete / SendMessage / TaskList / TeammateIdle hook 노출.
- `superpowers:using-git-worktrees` skill — worktree 가용 prerequisite.

### Gap

1. **Phase-scoped sequential team lifecycle SSOT 부재** — ADR-035 D2 결정 본문에 "lane 진입 시 TeamCreate, 완료 시 TeamDelete" 만 명시. lane 별 team-spec / teammate roster / hook subscription 미정의.
2. **team-spec yaml schema 부재** — 7 lane 의 teammate roster 정의 file 없음.
3. **hook 3종 (TeammateIdle / TaskCreated / TaskCompleted) 미등록** — 현재 `templates/.claude/hooks/` 에 SessionStart × 2 만.
4. **review-verdict v3 → v4 cutover 미수행** — ADR-022 Deprecated 후 v3 의 Sonnet decider 영역 (decision_state 7 state / sonnet_final_status / decider_decision_ref / write_errors step enum) 이 NO-OP passthrough. v4 MAJOR bump 가 정식 제거 carrier — 본 ADR scope.
5. **5 권장 패턴 measurable verification 미정식화** — Anthropic 권장 패턴 (Specialization / Parallelization / Adversarial / Cross-layer / Escalation) 이 codeforge lane 매핑 명시되었으나 (Story §2.2), AC-level metric 미정의.
6. **default subagent context vs agent teams enabled context 분기 fallback 미정의** — ADR-039 default invariant 와 본 ADR 의 enabled context 활용 사이 동작 fallback 부재.

## 결정 (8)

### 결정 1 — Phase-scoped sequential team lifecycle (ADR-035 D2 implementation)

매 lane 진입 시 Orchestrator 가 다음 sequence 수행:

```
1. Preflight check (CLAUDE.md "레인 진입 전 Preflight 체크 의무")
2. (CFP-139 후) GitOpsAgent SendMessage — lane worktree 준비
3. TeamCreate(team_spec=templates/team-spec-<lane>.yaml, worktree=<path>)
4. lane 진행:
   - Lane PL → teammate dispatch (TaskCreate)
   - teammate ↔ teammate SendMessage (Adversarial / Cross-layer 패턴)
   - PL 중재 + dedup → pl_recommendation
5. TeamDelete (in-flight teammate 완료 명시 wait)
6. Orchestrator self-write (Story §9 + GitHub gate label + phase transition)
7. FIX 시 → TEAM-FIX 새 team (parallel diagnosis)
```

**Lead = Orchestrator** (Story 전 기간 fixed, ADR-035 D2 + ADR-009 정합). Phase-scoped = lane 별 짧은 lifecycle (`/resume` no-resumption risk 회피, ADR-035 §결과 cross-ref).

**거절된 대안**:
- (B) Story-long single team — `/resume` 후 in-process teammate 미복원 위험. ADR-035 D2 §근거 정합.
- (C) Continuous team-of-teams — codeforge 정책 nested team 금지 (domain-knowledge entry §"re-entrancy 제약 3종"). team-spec yaml depth 1 강제.

### 결정 2 — team-spec yaml 7종 schema (Specialization 매핑 SSOT)

`templates/team-spec-<lane>.yaml` 7종 신설:

| File | Lane | Teammate count (default) | Teammate count (Codex on request) | Dispatch pattern |
|---|---|:-:|:-:|---|
| `team-spec-decompose.yaml` | Stage 0 (Epic 분해) | 2 (PMOAgent + Orchestrator) | 2 | sequential dialog |
| `team-spec-requirements.yaml` | 요구사항 | 4 (PL + Domain + Analyst + Researcher) | 4 | parallel sub-task fan-out |
| `team-spec-design.yaml` | 설계 | 8 (PL + chief + 6 deputy) | 8 (CONDITIONAL +2 Live deputy) | parallel deputy fan-out |
| `team-spec-design-review.yaml` | 설계 리뷰 | **2** (PL + Claude worker) | **3** (PL + Claude + Codex worker) | adversarial debate |
| `team-spec-develop.yaml` | 구현 | 5-7 (PL + QADev + role:dev × N) | 5-7 | cross-layer (dev ↔ QA) |
| `team-spec-code-review.yaml` | 구현 리뷰 | **2** (PL + Claude worker) | **3** (PL + Claude + Codex worker) | adversarial debate |
| `team-spec-security-test.yaml` | 보안 테스트 | **2** (PL + Claude worker) | **3** (PL + Claude + Codex worker) | adversarial + GitHub native 1차 layer 통합 |

(구현 테스트 lane = 1 agent TestAgent — team 미생성, 기존 single subagent 유지.)

**Schema (공통 base)**:

```yaml
lane: <lane-name>
teammates:
  - name: <agent-name>
    role: <PL | chief | deputy | worker | role:dev | QADev | Researcher | Analyst | Domain>
    system_prompt_path: <plugin-relative agent file path>
    model: <claude-opus-4-7 | claude-sonnet-4-6 | gpt-5-codex>
    spawn_mode: default | conditional
    dispatch_mode: default | user_request_only | auto_on_divergence  # NEW (Story §2.4 정합 / Amendment 1 CFP-391 — auto_on_divergence 추가)
    activation_condition: <expression — only when spawn_mode=conditional>
dispatch_pattern: parallel | sequential | adversarial | cross-layer | sequential-dialog
worktree_layout:
  per_teammate: bool                # true 시 각 teammate sub-worktree 보유
  base_worktree: cfp-NNN/<lane>     # parent (story root) 또는 lane sub-branch
hook_subscriptions:
  - TeammateIdle
  - TaskCreated
  - TaskCompleted
```

**dispatch_mode SSOT (Story §2.4)**: review lane 의 Codex worker = `dispatch_mode: user_request_only`. default roster = `PL + Claude worker` 2 teammate, Codex 는 사용자 explicit request 시 추가 → 3 teammate. memory `feedback_sonnet_decider_user_only.md` + ADR-022 Deprecated + 사용자 turn 7-8 directive 정합.

**Amendment 1 (2026-05-11, CFP-391 / ADR-059)** — `auto_on_divergence` 옵션 추가. ADR-059 에서 정의되는 `debate-protocol-v1` 발동 조건 — DesignReview lane 에서 Claude worker 와 Codex worker 가 동일 anchor 에 대해 (a) 서로 다른 severity 또는 (b) 서로 다른 recommendation 산출 시 자동 활성.

**우선순위 룰** (두 mode 동시 적용 시 effective mode 결정):

```
default  >  auto_on_divergence  >  user_request_only
```

- `default` 가 가장 강함 (항상 활성)
- `auto_on_divergence` = trigger 조건 (divergence) 만족 시 자동 활성
- `user_request_only` = 사용자 explicit request 만 (최약)
- 두 mode 가 동시 활성 시 더 강한 쪽이 effective. 예: `[user_request_only, auto_on_divergence]` 표기 worker 는 divergence 감지 시 자동 활성 + 사용자가 explicit request 안 한 상태에서도 발동.
- review lane Codex worker 의 권고 표기 = `dispatch_mode: [user_request_only, auto_on_divergence]` (Story 1 scope = DesignReview, Story 2 scope = Requirements 도 동일 패턴).

**`auto_on_divergence` trigger 의 lane-specific 정의**:

- DesignReview: review-verdict-v4 `findings[]` 동일 `anchor_id` 에 대해 (severity 또는 recommendation 불일치) — ADR-059 §결정 2
- Requirements (Story 2 / CFP-392 scope): RequirementsPL synthesis 와 Codex proactive check 간 semantic divergence — ADR-052 touchpoint #4 격상 Amendment 와 동행 (별도 Story)
- CodeReview / SecurityTest: deferred CFP-C scope

본 Amendment 자체는 BREAKING 아님 — `default | user_request_only` 기존 동작 보존 + enum 1 value 추가 (SemVer MINOR 정합 — ADR-008).

**거절된 대안**:
- (B) review lane default = `PL + Claude + Codex` (3 teammate) — 사용자 directive 정면 위배 (Codex review 자동 발동 = ad-hoc only).

### 결정 3 — Hook 3종 등록 + sample (TeammateIdle / TaskCreated / TaskCompleted)

`templates/agent-teams-hook-samples/` 에 신규 sample 3종 (path = wrapper repo standalone — `templates/.claude/hooks/` 디렉토리는 SessionStart 류 hook 의 standardized location, 본 agent teams 류 hook 은 별도 디렉토리에 분리해 consumer 가 명시 의식 후 install):

- `TeammateIdle.json.sample` — idle teammate detect → PL 에 nudge SendMessage 또는 TeamDelete 권유
- `TaskCreated.json.sample` — 새 task dispatch 시 Story §14 Lane Evidence row append (ADR-031 Amendment 1 정합 — Orchestrator-owned delegate write)
- `TaskCompleted.json.sample` — task outcome §14 row 채움 + (CFP-139 후) GitOpsAgent worktree merge trigger

**등록 mechanism**: consumer 측 `.claude/settings.json` `hooks.{TeammateIdle,TaskCreated,TaskCompleted}[]` 배열에 sample copy. consumer-guide §"Agent teams 적극 도입 (CFP-137)" 가 install 안내 — `cp templates/agent-teams-hook-samples/*.json.sample .claude/hooks/` 후 settings.json merge.

**Trigger 조건 (env-divergent)**:

| env | TeamCreate / SendMessage / hook | 동작 |
|---|---|---|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | 활성 | hook 3종 trigger 발화. team-spec yaml 본격 사용. |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0` 또는 미설정 | 미활성 | hook 3종 등록되어도 trigger 미발화. ADR-039 default subagent context fallback. team-spec yaml 미사용 (기존 one-shot Agent tool spawn 유지). |

### 결정 4 — review-verdict v3 → v4 MAJOR bump (Sonnet decider 영역 정식 제거 + worker_dialog_rounds 추가)

본 ADR carrier scope. v3 → v4 BREAKING:

- **제거 (NO-OP passthrough → 정식 제거)**:
  - `decision_state` 8-value enum 전체 (단순화: PL synthesis 후 Orchestrator self-write 단일 path)
  - `sonnet_final_status` field
  - `decider_decision_ref` field
  - `write_errors[].step` 의 Sonnet 영역 step enum (`fix_ledger_append`, `diagnosis_spawn` 의 `decider:claude_sonnet` semantics)
  - 5-step Orchestrator algorithm (review-verdict v3.md §6) — Sonnet 호출 step 3 제거 → 4-step 단순화

- **추가**:
  - `worker_dialog_rounds: int >= 0` — Adversarial debate 의 SendMessage round count (5 권장 패턴 Adversarial measurable verification, Story §5.1)
  - `pl_recommendation` (PASS / FIX / FIX_DISCRETIONARY) 가 final verdict 책무 단독 보유 (sonnet override marker 제거)

- **유지**:
  - `findings[]` schema (severity / category / file / line / evidence / suggestion)
  - `writes_completed{}` audit (Orchestrator self-write 결과)
  - `lane` / `story_key` / `iteration` / `contract_version: "4.0"`

**Cutover (Story §5.5 R3 default 채택)**: 즉시 cutover. consumer scope 0건 (mctrader debut audit 까지) 으로 backward compat 면제. wrapper Phase 1 PR merge 시:
- v3 sibling (wrapper repo) `status: Active → Archived` 동기 갱신
- v4 sibling (wrapper repo) `status: Active` 신설
- canonical sync (codeforge-review plugin) 는 sibling sync follow-up PR (ADR-010 §단계 절차 정합)
- `MANIFEST.yaml` `review_verdict.files[]` 에 v4 entry append + v3 status flip

**Migration guide**: v4 file 본문 §"v3 → v4 migration" 섹션에 verbatim — 수신자 (Orchestrator + Lane PL) 갱신 항목 명시.

**거절된 대안**:
- (B) deprecation period 6개월 — consumer scope 0이라 불필요. Story §5.5 R3 default 정합.

### 결정 5 — 5 권장 패턴 measurable verification 5종 (Story §5.1 정식화)

| 패턴 | codeforge 매핑 lane | Measurable verification | Lint / fixture 위치 |
|---|---|---|---|
| **Specialization** | 7 lane 전체 (teammate 좁은 system prompt) | team-spec yaml `system_prompt_path` 가 lane PL agent prompt line count 보다 적음 | subjective — Phase 2 e2e fixture spot-check |
| **Parallelization** | TEAM-DESIGN 6 deputy / 2 review worker 동시 | §14 Lane Evidence 의 `spawned_at` (deputy 6 row) 차이 < 60s | `scripts/check-lane-evidence.sh` lint 확장 (Phase 2 PR scope) |
| **Adversarial** | TEAM-{DESIGN,CODE,SECURITY}-REVIEW Claude vs Codex worker (Codex on request) | review-verdict v4 packet `worker_dialog_rounds: int >= 2` (Codex 활성 시) | review-verdict-v4 schema 신규 field (본 ADR 결정 4) |
| **Cross-layer** | TEAM-DEVELOP dev ↔ QA continuous coordination | develop-output v1 → v1.1 MINOR bump 후보 (`cross_layer_dialog_rounds: int >= 1`) | codeforge-develop sibling sync follow-up |
| **Escalation** | lane FIX 시 lane team → TEAM-FIX (parallel diagnosis) | §10 FIX Ledger row + §14 lane=`<원래>-fix-iter-N` row pair 동시 존재 | `scripts/check-fix-evidence.sh` 신설 후보 (Phase 2 deferred) |

본 5 metric 의 Phase 1 scope = schema 정의 (review-verdict v4 의 `worker_dialog_rounds` field 신설). 나머지 lint / fixture / develop-output bump = Phase 2 PR scope 또는 sibling sync follow-up.

### 결정 6 — `docs/orchestrator-playbook.md` §3 amendment

기존 §3 (lane spawn sequence + branch logic + FIX 진단 흐름) + §3.0 (ADR-039 spawn-default) + §3.5 (Worktree dispatch) 에 다음 sub-section 추가:

- **§3.6 TeamCreate / TeamDelete protocol** (env=1) — env 검증 + worktree path 주입 + teammate fan-out 사양 + in-flight wait
- **§3.7 SendMessage 사용 패턴** — Lane PL ↔ Worker continuous dialog 예시 (review lane Claude ↔ Codex debate)
- **§3.8 TeammateIdle nudge protocol** — idle 감지 시 PL 의 추가 dispatch 또는 TeamDelete 트리거
- **§3.9 env-divergent context fallback** — env=0 시 기존 one-shot Agent tool subagent 폴백 (ADR-039 default)

### 결정 7 — `docs/consumer-guide.md` § "Agent teams 적극 도입 (CFP-137)" 신설

본 ADR 후 consumer-guide 신규 subsection:

- prerequisite: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` settings.json env + 신규 세션 재시작
- env=0 fallback 동작 명시 (기존 one-shot subagent — ADR-039 정합)
- hook 3종 sample install 안내 (overlay merge 패턴 — SessionStart-codeforge-worktree-gc.json.sample 와 동일)
- **secret hygiene**: SendMessage body 에 secret (API key / DB credential 등) 미포함 의무 — sibling teammate 끼리 system prompt / tool output 공유. consumer 책임 영역.
- consumer 측 적용 가이드 (consumer Orchestrator 의 codeforge orchestration 시 본 정책 inheritance)

### 결정 8 — 5 권장 패턴 적용 시 default subagent context invariant 무손상

본 ADR 의 5 권장 패턴 적용 = agent teams enabled context (env=1) 한정. default subagent context (env=0 또는 미설정) = ADR-039 §결정 1 always-spawn invariant 무손상. 두 context 의 분기 SSOT = `docs/domain-knowledge/agent-teams/agent-teams-platform-capability.md` (CFP-137 신설 entry). hook 3종도 env=1 시에만 trigger 발화 — env=0 fallback = ADR-039 default 유지.

## 결과

### 긍정

- ADR-035 D2 implementation level SSOT 확보 — Phase-scoped sequential team lifecycle / team-spec yaml 7종 / hook 3종 / review-verdict v3 → v4 cutover 통합
- `/resume` no-resumption risk 회피 (Phase-scoped = lane 별 짧은 lifecycle)
- Lane PL ↔ Worker continuous dialog 가능 (SendMessage round) — 토큰 비효율 회피 (사용자 directive turn 5+8 정합)
- Adversarial debate measurable (worker_dialog_rounds field) — 5 권장 패턴 Adversarial 검증 가능
- review-verdict v4 단순화 (Sonnet decider 영역 정식 제거) — 8-value state machine → 4-step linear path
- env-divergent fallback (env=0 시 ADR-039 default) — backward compat 보장 (env=1 미활성 사용자 영향 0)
- ADR-009 wrapper-only invariant 무손상 (lead = Orchestrator 단일 fixed)
- ADR-039 always-spawn invariant 무손상 (env=0 default 유지, env=1 시 mechanism 만 enrich)

### 부정 / 비용

- **권장 3-5 명 초과** (Design 8명, Develop 5-7명) — 25 thread 한도 내. Specialization 패턴 정합으로 허용 (ADR-035 §결과 + Story §5.1 verification matrix).
- **Experimental status (agent teams)** — production stability 미보증. mitigation = Hotfix path 유지 + SessionStart hook env 검증 + env=0 fallback 영구 유지.
- **review-verdict v4 BREAKING** — consumer scope 0건이지만 기존 v3 NO-OP passthrough annotation 정리 + canonical sync follow-up PR 의무.
- **6 lane plugin sibling sync follow-up** — wrapper Phase 1 PR merge 후 6 PR pair (ADR-010 wrapper-first, Story §5.5 B1 default 채택).

### 위험

- **TeammateIdle hook 미발화 시 idle teammate 누적** → 25 thread 한도 초과. mitigation = TeamDelete 시 in-flight 명시 wait + script GC. 본 ADR §결정 1 lifecycle step 5 명시.
- **Rate limit hit 빈도 ↑ (다수 teammate 병렬 spawn)** — agent teams enabled 시 self-evident. mitigation = team-spec yaml `teammates[]` 수 제한 (Design 8명 / Develop 5-7명). default subagent context (env=0) 에서는 자연 mitigation (one-shot 순차).
- **Codex worker 사용자 미요청 시 default 미발화** — 사용자가 explicit request 누락 시 review lane Adversarial 패턴 미발화. mitigation = consumer-guide 안내 + review verdict packet 의 `worker_dialog_rounds` 가 0인 경우 PL 단독 합의 명시. Story §2.4 정합.
- **SendMessage secret 노출** — sibling teammate 끼리 system prompt / tool output 공유 (Anthropic platform behavior). mitigation = consumer-guide §"secret hygiene" 안내 + 본 ADR 결정 7 명시.

## 회피된 대안

| 대안 | 거부 이유 |
|---|---|
| **Story-long single team** | `/resume` 후 in-process teammate 미복원 위험 (도메인 지식 entry §"`/resume` risk"). Phase-scoped = lane 별 짧은 lifecycle 으로 mitigation. ADR-035 D2 §근거 정합. |
| **Nested team / team-of-teams** | codeforge 정책 nested team 금지 (re-entrancy 제약 3종). team-spec yaml depth 1 강제. |
| **6 lane plugin self-write 보유 sibling sync 동시 (Phase 1 PR pair)** | wrapper-first (ADR-010 §4 허용 패턴) 가 사용자 turn 11 directive ("worktree 해서 작업") + memory `feedback_internal_docs_branch_safety.md` + Story §5.5 B1 default 와 정합. 동시 7 PR pair 는 reviewer cognitive load + merge order race. wrapper-first 후 follow-up PR 6개 채택. |
| **review-verdict v4 deprecation period 6개월** | consumer scope 0이라 불필요 overhead. 즉시 cutover (Story §5.5 R3 default 채택) 가 단순. |

## ADR 정합성

- **ADR-009** (wrapper-only decomposition) — Orchestrator 단일 lead invariant 무손상 (§결정 1 lead 고정).
- **ADR-022** (Deprecated by ADR-035) — review-verdict v4 cutover 가 ADR-022 본문 잔재 cleanup 일부 (decision-packet-v2.1 / Sonnet decider 영역). 잔재 doc cleanup 은 본 ADR scope 외 (CFP-137 follow-up CFP).
- **ADR-024 + ADR-040** (worktree convention) — §결정 1 lifecycle step 2 (`(CFP-139 후) GitOpsAgent SendMessage`) 가 ADR-040 hook contract 정합.
- **ADR-031** (lane-spawn evidence) — §결정 3 hook 3종 (TaskCreated / TaskCompleted) 가 §14 row append mechanism. ADR-031 Amendment 1 (Orchestrator-owned delegate inclusion) 가 본 ADR 정합.
- **ADR-035** (Epic architecture) — D2 = Phase-scoped sequential team 의 implementation level SSOT 본 ADR. ADR-035 §amendment_log[0] = `planned → applied` flip (CFP-137 carrier 본 Story).
- **ADR-039** (Orchestrator subagent default) — env-divergent fallback (§결정 8). env=0 default subagent context = ADR-039 always-spawn invariant 유지. env=1 enabled context = mechanism enrichment (continuous dialog), ownership 무변.

## 외부 fact (도메인 지식 entry SSOT)

`docs/domain-knowledge/agent-teams/agent-teams-platform-capability.md` (CFP-137 신설) 가 외부 reference SSOT. Anthropic Claude Code experimental agent teams docs 의 verbatim transcribe 가 아니라 codeforge 내부 정책 SSOT — 외부 docs link rot risk 회피.

핵심 fact:
- TeamCreate / TeamDelete / SendMessage / TaskList / TeammateIdle hook = experimental feature, env=1 시 노출
- one-team-per-lead 강제 (codeforge 정책 + platform 동일)
- 재귀 spawn 금지 + nested team 금지 (codeforge 정책 SSOT)
- `/resume` 후 in-process teammate 미복원 — Phase-scoped sequential team 채택 motivation

## Out-of-scope

- 6 lane plugin agent prompt 갱신 (sibling sync follow-up PR — ADR-010 wrapper-first 절차)
- codeforge-review plugin canonical review-verdict-v4.md write (sibling sync follow-up — wrapper Phase 1 PR merge 후)
- develop-output v1 → v1.1 MINOR bump (cross-layer measurable verification, codeforge-develop sibling sync follow-up)
- `scripts/check-lane-evidence.sh` lint 확장 + `scripts/check-fix-evidence.sh` 신설 (Phase 2 PR scope 또는 follow-up CFP)
- Phase 2 PR e2e fixture (env=1 / env=0 dry-run 검증 row, team-spec yaml schema lint, review-verdict v4 schema migration test, hook 3종 trigger 검증)
- consumer 측 적용 본격 가이드 (별도 CFP — CFP-134 spec §8 out-of-scope)
- Hotfix path 의 agent teams 통합 (hotfix-playbook.md amendment 별도)
- ADR-022 본문 잔재 cleanup (CFP-137 follow-up CFP)

## 관련 파일

- [ADR-035 (Epic architecture)](ADR-035-codeforge-agent-teams-epic-architecture.md) — D2 implementation level carrier 본 ADR. §amendment_log[0] = `planned → applied` flip 동행.
- [ADR-039 (Orchestrator subagent default)](ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) — default subagent context invariant. env-divergent fallback 정합.
- [ADR-040 (Worktree convention)](ADR-040-worktree-convention.md) — TeamCreate / Delete + worktree integration hook contract.
- [ADR-031 (Lane-spawn evidence)](ADR-031-lane-spawn-evidence-trail.md) — hook 3종 (TaskCreated / TaskCompleted) 가 §14 row append mechanism.
- `docs/inter-plugin-contracts/review-verdict-v4.md` — 본 ADR 결정 4 carrier (wrapper sibling, canonical = codeforge-review plugin).
- `docs/inter-plugin-contracts/MANIFEST.yaml` — review_verdict.files[] v4 entry append.
- `docs/domain-knowledge/agent-teams/agent-teams-platform-capability.md` — 도메인 지식 entry SSOT.
- `templates/team-spec-{decompose,requirements,design,design-review,develop,code-review,security-test}.yaml` — 7 yaml.
- `templates/.claude/hooks/{TeammateIdle,TaskCreated,TaskCompleted}.json.sample` — 3 hook sample.
- `docs/orchestrator-playbook.md` — §3 amendment (§3.6-§3.9 신설).
- `docs/consumer-guide.md` — § "Agent teams 적극 도입 (CFP-137)" 신설.
- `CLAUDE.md` — "Agent teams enabled context 별도" 단락 expansion (1 paragraph stub → 본격 SSOT cross-ref).
- **CFP-134** — Epic carrier.
- **CFP-137** — 본 ADR carrier Story (Wave 2).
- **CFP-139** — GitOpsAgent (lifecycle 자동화 후속, Wave 3).
