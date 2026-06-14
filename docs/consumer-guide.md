# Consumer Guide — 플러그인 적용 가이드

이 플러그인(`codeforge`)을 consumer 프로젝트에서 사용하는 방법.

## 0. 사전 요구사항

- **GitHub Team plan** (Sub-issues, Projects v2, CODEOWNERS, Branch protection 사용)
- 권한: GitHub repo admin (Branch protection·CODEOWNERS·Actions 설정)
- gh CLI 설치 + 인증 (`gh auth login`)

## 1. 설치

### 1a. 플러그인 설치 (marketplace 경유)

```bash
/plugins install codeforge@<marketplace>
/plugins install github@claude-plugins-official
/plugins install codex@openai-codex
/plugins install superpowers@claude-plugins-official
/plugins install claude-md-management@claude-plugins-official
```

또는 로컬 경로 설치(개발 중인 플러그인 테스트 시):

```bash
/plugins install /path/to/codeforge-repo
```

설치 확인:

```bash
ls ~/.claude/plugins/cache/<marketplace>/codeforge/<version>/agents/
# ArchitectAgent.md  DeveloperAgent.md  ...
```

### 1b. 필수 의존성

`CLAUDE.md` §"세션 개시 의무"에 명시. 미설치 시 플러그인 동작 불가:

- **Claude Code 버전**: v2.1.170 이상 필수 — codeforge 일부 에이전트가 `model: fable`(Claude Fable 5)을 사용하며, 2.1.170 미만에서는 해당 에이전트 spawn 이 실패한다 ([ADR-117](../archive/adr/ADR-117-fable-5-surgical-model-tier.md)). (dormant — 2026-06-14 CFP-2241: 현재 wrapper self 는 미 정부 제약으로 surgical 10 에이전트를 `model: opus` 임시 override 해 fable 미사용 상태다(ADR-117 Amendment 1). floor 정책은 원복 대비 보존 — 제약 해제·fable 환원 시 본 버전 floor 가 즉시 재유효.)
- **MCP**: `github` 인증 완료 (`/mcp` 인증)
- **플러그인 4종**: `codex@openai-codex`, `superpowers@claude-plugins-official` ([integration SSOT](superpowers-integration.md)), `claude-md-management@claude-plugins-official`, `github@claude-plugins-official`
- **CLI 2종**: `codex`, `gh` (`gh auth login` 인증)

### 1c. 권장 플러그인 (선택)
- `pyright-lsp`, `context7`, `commit-commands`, `pr-review-toolkit`

### 1d. Plugin install 의무 — `enabledPlugins` ↔ `installed_plugins.json` (CFP-132 / Issue #238)

**중요**: `~/.claude/settings.json` 의 `enabledPlugins[<id>] = true` 만으로는 agent / skill 노출 불충분합니다. Claude Code 는 세션 시작 시 `~/.claude/plugins/installed_plugins.json` 을 읽어 plugin 을 discovery — `installed_plugins.json` 에 entry 가 없으면 `enabledPlugins=true` 라도 agent 미노출.

**증상**: 설치 후 `subagent_type` 리스트에 `codeforge-design:*` / `codeforge-review:*` 등 미노출 → "왜 ArchitectPL agent 가 없지?".

**올바른 절차**:

```bash
# enabledPlugins=true 만 토글 — 부족
# (settings.json 수동 편집 OR /config 토글)

# /plugin install 명시 실행 — installed_plugins.json entry 추가
/plugin install codeforge@<marketplace>
/plugin install codeforge-requirements@<marketplace>
/plugin install codeforge-design@<marketplace>
/plugin install codeforge-review@<marketplace>
/plugin install codeforge-develop@<marketplace>
/plugin install codeforge-test@<marketplace>
/plugin install codeforge-pmo@<marketplace>
/plugin install codex@openai-codex
/plugin install superpowers@claude-plugins-official
/plugin install claude-md-management@claude-plugins-official
/plugin install github@claude-plugins-official
```

새 세션 시작 시 11 plugin agent 모두 노출 확인 — 미노출 시 `~/.claude/plugins/installed_plugins.json` entry 부재 점검.

**자동 검증**: SessionStart hook (`overlay/hooks/check_bootstrap.py`) 가 `REQUIRED_PLUGINS` 11종 verify, 누락 시 stderr WARN 출력 (CFP-103). 본 WARN 메시지를 보면 `/plugin install` 누락이 원인 — 위 명령 실행으로 해결.

### 1e. Pre-push lint hook (선택, 권장 — CFP-132 / Issue #236)

**문제**: 매 phase production push 후 CI 의 ruff/pyright fail → fix → push 사이클 반복 (4-round 평균) → GitHub Actions 비용 폭증.

**해결**: pre-push hook 으로 push 전 lint 자동 실행 — fail 시 push 차단 + 로컬 fix 유도.

**Install (수동)**:

```bash
# Option A: .git/hooks/pre-push 직접 cp
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/pre-push.sh.example .git/hooks/pre-push
chmod +x .git/hooks/pre-push

# Option B: core.hooksPath 사용 (.githooks/ 디렉터리 commit 가능)
mkdir -p .githooks
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/pre-push.sh.example .githooks/pre-push
chmod +x .githooks/pre-push
git config core.hooksPath .githooks
```

**Manual 실행 (hook 미사용 시)**:

```bash
# PR open 전 의무
bash scripts/check-lint.sh           # 검사
bash scripts/check-lint.sh --fix     # ruff auto-fix 적용
```

`scripts/check-lint.sh` 는 pyproject.toml (ruff + pyright) / package.json (eslint + tsc) 자동 detect, 없으면 silent skip.

**Bypass (긴급 push)**: `git push --no-verify`

**Rollback**: `rm .git/hooks/pre-push` 또는 `git config --unset core.hooksPath`

**Windows 환경 caveat**: `.venv/Scripts/Activate.ps1` 경로 권한 / WSL bash 호출 issue 시 manual 실행 fallback. 자세한 워크어라운드는 별도 follow-up CFP.

### 1f. Agent teams 적극 도입 (CFP-137 / [ADR-044](../archive/adr/ADR-044-phase-scoped-sequential-team.md))

> **Optional**: agent teams 적극 도입 = wrapper / consumer Orchestrator 모두 적용 가능. 활성 시 Phase-scoped sequential team + SendMessage continuous dialog + Adversarial debate 패턴 사용 가능. 비활성 시 ADR-039 default subagent context (one-shot Agent tool) fallback — 본 CFP-137 도입 전 동작과 동일.

**Prerequisite**:

```jsonc
// ~/.claude/settings.json (또는 ${CLAUDE_PROJECT_DIR}/.claude/settings.json)
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

설정 후 **신규 세션 재시작** 의무. env=0 또는 미설정 시 = ADR-039 default subagent context — 본 CFP-137 의 SendMessage / TeamCreate / TaskCreate / TeammateIdle 모두 미발화, hook 등록되어도 trigger 0.

**Hook 3종 install** (CFP-137 / ADR-044 §결정 3):

```bash
# Sample 3종 install (ADR-044 §결정 3 path)
mkdir -p .claude/hooks
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/agent-teams-hook-samples/TeammateIdle.json.sample \
   .claude/hooks/TeammateIdle.json
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/agent-teams-hook-samples/TaskCreated.json.sample \
   .claude/hooks/TaskCreated.json
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/agent-teams-hook-samples/TaskCompleted.json.sample \
   .claude/hooks/TaskCompleted.json

# settings.json hooks.{TeammateIdle,TaskCreated,TaskCompleted}[] 배열에 merge
# (overlay/hooks/merge.py 또는 수동 편집)
```

**Codex worker dispatch 정책 (ADR-044 §결정 2 SSOT + Amendment 1)**:

review lane (TEAM-DESIGN-REVIEW / TEAM-CODE-REVIEW / TEAM-SECURITY-TEST) 의 Codex worker = `dispatch_mode: user_request_only`. **Default roster = `PL + Claude worker` 2 teammate**. Codex worker 는 사용자 explicit request 시에만 활성 (예: "codex 와 opus 로 심층 리뷰 후 ..." 와 같은 ad-hoc 발화). codeforge 가 자동 invoke 하지 않음 — ADR-022 Deprecated (CFP-134) 정합.

**Amendment 1 (CFP-391 / [ADR-059](../archive/adr/ADR-059-debate-protocol-v1.md))** — `dispatch_mode` enum 에 `auto_on_divergence` 추가 (debate-protocol-v1 발동 mode). 우선순위 룰: `default > auto_on_divergence > user_request_only` — 두 mode 동시 적용 시 더 강한 쪽 effective.

**Multi-round Adversarial Debate (debate-protocol-v1 / CFP-391)**:

사용자가 explicit request 로 Codex worker 를 활성화 → review-verdict-v4 finding 합성 직전 Claude / Codex worker 가 동일 anchor 에 대해 **(a) 서로 다른 severity 또는 (b) 서로 다른 recommendation (FIX vs PASS)** 발화 시 DesignReviewPL 이 자동으로 multi-round debate 발동. consumer overlay 로 비활성화 불허 (codeforge 정책 — opt-out 은 별도 CFP carrier 도입 시 검토).

**라운드 정책**: min 3 / soft default 4 / max 5 라운드. 평균 3~4 라운드 합의 도달 (사용자 실증 + 선행 연구 정합 — Du et al. 2023 / Liang et al. 2023). max 5 미합의 시 `AskUserQuestion` 으로 사용자 dialog escalation.

**Anti-sycophancy 메커니즘**: `remaining_disagreements` 필드 강제 + role_lock + 반대 입장 강제 유지 prompt + `POSITION_CHANGE` 라벨 의무. 가짜 합의 차단 forcing function.

**Reasoning carryover (FIX verdict 시)**: debate transcript 가 Story §9 에 inline append 되고 ArchitectAgent re-run prompt 에 verbatim 주입 — 양측 양보 / 반박 / 미해결 disagreement 가 redesign 입력으로 보존. §10 FIX Ledger row 의 `debate_artifact_ref` 필드 (fix-event-v1 1.1, optional) 가 transcript section anchor link 보유.

**Token 비용 의식**:

- `env=1` (agent teams 활성): round 간 cache 5 min TTL 활용 — 비용 최적
- `env=0` (default subagent context, codeforge default): 매 라운드 Orchestrator round-trip — cold start cache miss 누적 → 비용 증가 의식 필요
- 매 라운드 worker 출력 cap ~5K token × 2 worker × 5 round = 50K token (Opus PL 200K context 한도 내)
- max 5 라운드 cap = 비용 폭증 차단 forcing function. 5 라운드 cap 초과 = AskUserQuestion 사용자 중재

**Anchor 재발 escalation**: ArchitectAgent 수정 후 DesignReview 재진입 시 동일 anchor 가 두 번째 debate 유발 = 즉시 `AskUserQuestion` 사용자 escalation. AI 합의 불가능 시그널 — 사용자 중재 의무.

**Story 2 (CFP-392) 진입 예정**: Requirements lane 확장 — RequirementsPL synthesis 와 Codex proactive check 간 semantic divergence 자동 debate. 본 Story 1 (CFP-391) merge 후 별도 plan 으로 진입. CodeReview / SecurityTest lane 적용은 deferred CFP-C scope.

**Secret hygiene 의무 (ADR-044 §결정 7)**:

agent teams enabled context 의 SendMessage 는 **sibling teammate 끼리 system prompt / tool output 공유** (Anthropic platform behavior). consumer 측 secret (API key / DB credential / service account token 등) 가 SendMessage body 또는 system prompt 안에 포함되면 sibling teammate 모두 노출. 의무:

- **SendMessage body 에 secret 미포함** — 예: `SendMessage(to=Worker, body="API key XYZ123 사용해서 ...")` 금지. 대신 `SendMessage(to=Worker, body="환경변수 API_KEY 사용 — 자세한 값 미공유")` 패턴.
- **System prompt template 안에 secret 미포함** — agent file (`agents/<AgentName>.md`) 안 secret literal 금지. `${CLAUDE_PROJECT_DIR}/.env` 또는 환경변수 indirect reference 만.
- **Tool output sanitization** — 외부 API 호출 후 response 안 secret-like literal (e.g., bearer token) 이 SendMessage 로 propagate 되지 않도록 worker level 에서 mask.

**Re-entrancy 제약 3종 (codeforge 정책 SSOT)**:

agent teams enabled context 에서도 다음 3 제약 유지 (`docs/domain-knowledge/domain/agent-teams/agent-teams-platform-capability.md` SSOT):
1. 재귀 spawn 금지 (Lead 와 teammate 모두 — platform inherent)
2. Nested team 금지 (no team-of-teams)
3. One-team-per-lead 강제 — 다음 lane TeamCreate 전 현 team `TeamDelete()` 의무

**Disable / rollback**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0` 또는 unset → ADR-039 default subagent context fallback. hook 3종 install 되어도 trigger 미발화. Phase-scoped sequential team 은 자연 무효화 — 기존 one-shot Agent tool spawn 패턴.

**상세 SSOT**:
- Policy: [ADR-044](../archive/adr/ADR-044-phase-scoped-sequential-team.md) (CFP-137 carrier)
- Epic context: [ADR-035](../archive/adr/ADR-035-codeforge-agent-teams-epic-architecture.md) D2
- Domain knowledge: [docs/domain-knowledge/domain/agent-teams/agent-teams-platform-capability.md](domain-knowledge/domain/agent-teams/agent-teams-platform-capability.md)
- Default fallback: [ADR-039](../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md)
- Worktree integration: [ADR-040](../archive/adr/ADR-040-worktree-convention.md)
- review-verdict v4 schema: [docs/inter-plugin-contracts/review-verdict-v4.md](inter-plugin-contracts/review-verdict-v4.md)

### 1g. CODEFORGE_CROSS_REPO_PAT rotation policy (CFP-521 / [ADR-066](../archive/adr/ADR-066-pat-rotation-policy.md))

codeforge family 가 사용하는 `CODEFORGE_CROSS_REPO_PAT` (cross-repo Story binding + KPI internal-docs clone — CFP-450 / ADR-013 Amendment 4 consolidation) 의 lifetime / rotation / compromise response 정책. 정책 SSOT = [ADR-066](../archive/adr/ADR-066-pat-rotation-policy.md), audit log SSOT = [`docs/security/pat-rotation-log.md`](security/pat-rotation-log.md).

**Rotation cadence**:

- 권장 rotation = 90 days (분기별 회전)
- 최대 lifetime = 180 days (반기 회전 강제)
- 자동 만료 reminder workflow = Phase 2 carrier (별도 CFP, ADR-066 §결정 6)

**Scope minimum** (least privilege, ADR-066 §결정 2):

- `repo:read` — internal-docs read scan (KPI workflow)
- `repo:write` — cross-repo Issue comment / sub-issue link (phase-gate-mergeable)
- `metadata:read` — basic repo access

`admin:org` / `delete_repo` / `workflow` 등 광역 scope 부여 금지.

**Rotation 절차 (5-step, ADR-066 §결정 3)**:

1. New PAT 발급 — GitHub Personal access tokens, 위 scope, expiration ≤ 90 days
2. mclayer org secrets 갱신 — `Settings > Secrets > Actions > CODEFORGE_CROSS_REPO_PAT` (org level)
3. repo verification — marketplace + codeforge-internal-docs org secret 가시성 확인 (구 lane repo 8개 = 2026-06-12 GitHub archive, CFP-2178 S6 — fine-grained PAT 전환 시 access list 에서 제외 권고: `docs/security/pat-rotation-log.md`)
4. 1-2 PR 테스트 — phase-gate-mergeable 또는 KPI workflow active PR 동작 확인
5. 이전 PAT revoke — GitHub Personal access tokens settings + audit log row append

**Compromise response (leak / suspected leak 시 4-step, ADR-066 §결정 4)**:

1. **Immediate revoke** — GitHub UI > Personal access tokens > Revoke 즉시 (T+0)
2. **Within 1h rotation** — New PAT 발급 + 위 5-step (T+1h 까지)
3. **Audit 영향 범위 검토** — 영향 받은 workflow run / Issue comment / PR comment 검토 (`gh api` 활용)
4. **Disclosure 판단** — private repo data leak 가능성 시 즉시 사용자 / 외부 통보 의무

**Audit log**:

- 위치: [`docs/security/pat-rotation-log.md`](security/pat-rotation-log.md)
- Schema: `rotated_at (KST) | by | reason | expiration | revoked_at`
- 사용자 manual entry 의무 (PAT 발급 절차 자체가 GitHub UI 의존, ADR-066 §결정 5)
- Rotation 시 새 row append + 이전 row 의 `revoked_at` 갱신

**Consumer overlay 영향** (ADR-066 §결정 7):

본 정책은 codeforge family 의 `CODEFORGE_CROSS_REPO_PAT` 에 한정. Consumer project 가 자체 cross-repo PAT 사용 시:

- `.claude/_overlay/project.yaml` `security.pat_rotation_cadence_days` 필드로 cadence override 가능 — **강화 방향만** (90 days 미만 short rotation 허용, 90 days 초과 weaken 금지)
- Consumer 자체 PAT 의 audit log 는 consumer repo `docs/security/` (overlay 영역, codeforge 강제 안 함)
- Compromise response 4-step 은 consumer 도 동일 절차 권장

> **작업 규칙 (normative — CFP-341)**: 모든 변경 작업(lane spawn + ad-hoc)은 worktree 안에서 수행. 원본 clone directory 직접 편집 금지. `bash templates/scripts/worktree-create.sh <branch> origin/main` 으로 worktree 생성 후 작업 시작. 상세 [playbook §3.0.10](orchestrator-playbook.md).

### 1h. Action 차단 환경 fallback (CFP-658 / [ADR-027 Amendment 2](../archive/adr/ADR-027-consumer-adoption-protocol.md))

GitHub Enterprise org 의 admin policy 가 `default_workflow_permissions: read` cap 설정 시 — codeforge 6 핵심 workflow 가 silent skip. consumer workaround 금지 (ADR-039 inline whitelist) 와 codeforge 의무 사용 (ADR-027) 의무 충돌 해소를 위한 **manual fallback path** 의무.

#### 활성 trigger 2종 (hybrid, 우선순위 (C) > (A))

**(A) Declarative — environment default**:

`.claude/_overlay/project.yaml` 에 `bootstrap.fallback_mode: action_blocked` enable:

```yaml
bootstrap:
  fallback_mode: action_blocked  # default: auto
```

영구 차단 환경 default. Orchestrator 가 매 Story spawn 시 본 flag 검증 — true 시 자동 manual fallback path 활성.

**(C) Explicit ad-hoc — per-Issue override**:

Issue 발의자 또는 Orchestrator 가 `fallback:manual` label 부착. 일시 outage / 사용자 explicit 선택 시. environment default 와 무관 활성 (per-Issue override > env default).

#### Consumer runbook

1. `.claude/_overlay/project.yaml` 의 `bootstrap.fallback_mode: action_blocked` 설정 (영구 차단 환경)
2. 신규 Story Issue 발의 시 `type: story + phase:요구사항` label 부착 — Orchestrator 가 fallback path 자동 진입
3. RequirementsPL / ArchitectPL 가 manual `bash templates/scripts/manual-story-init-fallback.sh <ISSUE_NUMBER>` 호출 (Phase 2 carrier — 본 script 신설 후 활성)
4. 4 required check (phase-gate-mergeable + doc frontmatter + doc section + invariant-check) 통과 의무 — admin override 차단 (`enforce_admins: true` ratchet 유지, CFP-70)
5. `fallback:manual` label 부착 PR description 의 checklist 의무:

```markdown
## Manual fallback checklist
- [ ] Issue body §1 verbatim copy (byte-identical 검증)
- [ ] KEY = PREFIX-${ISSUE_NUMBER} (ADR-036 atomic)
- [ ] Branch existence_check (`gh api repos/<owner>/<repo>/branches/<branch>`)
- [ ] PR opened via `gh pr create`
- [ ] phase:요구사항 label 부착
- [ ] `fallback:manual` label 부착
```

#### 2-PAT 모델 (consumer 영역)

| PAT name | Scope | 용도 |
|---|---|---|
| `CODEFORGE_CROSS_REPO_PAT` (기존) | repo + read:org | phase-gate-mergeable.yml + rate-limit-fallback-kpi.yml (§1g rotation policy) |
| `CODEFORGE_FALLBACK_PAT` (신설) | repo only | manual fallback path 전용 — write:packages / admin:* 금지 |

namespace 분리 = fallback path 침해 시 blast radius 최소화. ADR-066 90 days rotation 정합 (`docs/security/pat-rotation-log.md` audit entry 의무).

상세 SSOT: [domain-knowledge `workflow-blocked-manual-fallback.md`](domain-knowledge/domain/github-actions/workflow-blocked-manual-fallback.md) + [ADR-027 §결정 6](../archive/adr/ADR-027-consumer-adoption-protocol.md) + [orchestrator-playbook §"fallback decision tree"](orchestrator-playbook.md).

### 1i. Enterprise environment setup (CFP-661 / Wave 3 of Epic CFP-431)

§1h 의 fallback path 는 **권한 차단 환경 대응**. 본 절은 **enterprise admin 권한 보유 환경에서 prerequisite 활성 운영** 의 SSOT — fallback 회피 정상 경로.

#### prerequisite 활성 단계

GitHub Enterprise org 의 admin policy 가 `default_workflow_permissions: read` cap 을 설정한 경우, codeforge 의 `story-init.yml` 외 5 workflow 가 silent skip 한다. consumer admin 이 다음 활성 의무:

1. **repo Settings → Actions → General → "Workflow permissions" 영역**:
   - `Read and write permissions` 선택 (default `Read repository contents and packages permissions` 에서 전환)
   - `Allow GitHub Actions to create and approve pull requests` 체크박스 활성

2. **CLI 등가 명령** (자동화 운영용):

   ```bash
   gh api --method PUT repos/<owner>/<repo>/actions/permissions/workflow \
     -f default_workflow_permissions=write \
     -F can_approve_pull_request_reviews=true
   ```

3. **확인 명령** (current state 검증):

   ```bash
   gh api repos/<owner>/<repo>/actions/permissions/workflow
   # 기대 응답: {"default_workflow_permissions":"write","can_approve_pull_request_reviews":true}
   ```

#### Graceful degradation 자동 활성 (권한 차단 환경)

위 prerequisite 미충족 시 `story-init.yml` 의 `Create Phase 1 PR` step (line 230-248) 이 `continue-on-error: true` 로 실패 흡수 → 후속 `Post manual PR fallback comment` step 이 Issue comment 로 manual fallback path 안내 자동 게시 (CFP-661 graceful degradation, ADR-054 doc-only fast-path scope). 이때 §1h 의 Wave 1 fallback path (`bootstrap.fallback_mode: action_blocked` declarative 또는 `fallback:manual` per-Issue label) 가 대체 진입점으로 활성 — Story init 진행 무중단.

#### Enterprise admin 결정 매트릭스

| 조건 | 권장 결정 | 대응 |
|---|---|---|
| Org admin 권한 보유 + cap 변경 가능 | prerequisite 활성 | 정상 workflow 경로 (PR auto-create) |
| Org admin 권한 보유 + cap 변경 정책상 차단 | fallback path 활성 | `bootstrap.fallback_mode: action_blocked` declarative (영구) |
| Org admin 권한 부재 + 일시 차단 | per-Issue override | `fallback:manual` label 부착 (per-Issue ad-hoc) |
| Org admin 권한 부재 + 영구 차단 | fallback path declarative + manual fallback 운영 표준화 | §1h 4 step runbook |

#### Sunset criteria

본 graceful degradation 메커니즘은 enterprise org cap 정책 회피 reactive 안전망. 해소 기준:
- **metric**: GitHub `default_workflow_permissions` API 가 org level inheritance broadcast 지원 + consumer org admin 이 일괄 default `write` 전환 — 90% 신규 consumer install 에서 prerequisite 활성 default
- **who**: consumer org admin (codeforge 외부)
- **how**: rollout audit (`docs/security/enterprise-prerequisite-rollout.md` log 신설 — Phase 2 carrier)

상세 cross-ref: §1h Action 차단 환경 fallback + [ADR-027 Amendment 2 §결정 6](../archive/adr/ADR-027-consumer-adoption-protocol.md) + [`templates/github-workflows/story-init.yml`](../templates/github-workflows/story-init.yml) line 230-273 (graceful degradation step pair).

### 1j. Windows external session auto-resume (opt-in, CFP-1355 / [ADR-110](../archive/adr/ADR-110-external-runtime-wrapper-ssot-boundary.md))

Anthropic API rate-limit 도달로 Claude Code session 이 종료된 후, rate-limit 창이 만료되면 자동으로 session 을 재개합니다. **Windows Task Scheduler** 기반 OS-level wrapper 로 in-process Orchestrator 영역 외 복구를 제공.

#### 사전 요구사항

- **Windows 10 1809+** (Task Scheduler XML schema 1.2 support)
- Administrator 권한 (Task Scheduler task registration)
- Claude CLI 설치 + 인증 완료

#### 설치 (opt-in)

```powershell
# PowerShell admin 권한으로 실행
cd <codeforge-clone-path>
powershell -ExecutionPolicy RemoteSigned -File scripts/install-codeforge-resume.ps1
```

설치 완료 후 결과 메시지:

```
=== Installation Complete ===
Wrapper installed to: C:\Program Files\codeforge\codeforge-session-resume.ps1
Task name: codeforge-auto-resume

To enable auto-resume in your project:
  1. Edit .claude/_overlay/project.yaml
  2. Add: runtime:
           auto_resume:
             enabled: true
```

#### 활성화

`.claude/_overlay/project.yaml` 에 다음 추가:

```yaml
runtime:
  auto_resume:
    enabled: true
```

#### 동작 원리

1. **초기 상태**: session 종료 시 마지막 session UUID 를 `%LOCALAPPDATA%\codeforge\last-session.txt` 에 저장
2. **주기적 확인** (10분 마다): `claude --print "noop"` 실행 → rate-limit reset 시간 헤더 파싱
3. **reset 대기**: reset 시간까지 기다렸다가 자동 resume 시도 (`claude --resume <uuid>`)
4. **재시도**: 실패 시 최대 3회 재시도 → 3회 초과 시 Windows Toast notification 으로 수동 재개 안내

#### 비활성화 (kill-switch)

```powershell
# Task Scheduler 작업 삭제
schtasks /Delete /TN "codeforge-auto-resume" /F

# 또는 Task Scheduler GUI 에서 직접 삭제
# → 작업 스케줄러 → codeforge → codeforge-auto-resume 우클릭 → 삭제
```

#### 로그 확인

auto-resume 작업 로그 위치:

```powershell
# 최근 로그 조회
Get-Content "$env:LOCALAPPDATA\codeforge\resume.log" -Tail 50
```

#### 제한사항 & 향후 roadmap

- **현재**: Windows 전용 (PowerShell 5.1+ Task Scheduler)
- **Linux/macOS**: bash equivalent (systemd timer / launchd) = Phase 2 sub-CFP carrier — 향후 지원 예정
- **다중 사용자 머신**: 현재 단일 사용자 가정. 다중 사용자 환경 = Phase 2 carrier (`project.yaml runtime.multi_user: bool`)
- **ghost session 방지**: local namespace mutex (Local\CodeforgeResumeWrapper) 로 중복 실행 차단

상세: [ADR-110 External-runtime-wrapper SSOT boundary](../archive/adr/ADR-110-external-runtime-wrapper-ssot-boundary.md) (§결정 1-10 normative codify) · [`docs/domain-knowledge/domain/runtime/external-session-auto-resume.md`](domain-knowledge/domain/runtime/external-session-auto-resume.md)

### 1k. Pre-push auto-rebase hook (opt-in, CFP-477)

baseline drift cadence 가 work cadence 를 초과하는 작업 환경 (codeforge family active development 등) 에서 pre-push 시점 branch behind detection + 4-line guidance abort 으로 rebase friction 완화.

본 hook 은 **advisory abort** 만 수행 — 직접 rebase 실행하지 않음. user 가 guidance 따라 manual rebase + 재 push.

**Installation** (opt-in):

```bash
cp templates/.claude/hooks/pre-push-auto-rebase.sh.sample .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

**Activation** (env-driven, default off):

```bash
export PRE_PUSH_AUTO_REBASE=1
git push origin <branch>
# branch behind origin/main 시 → abort + 4-line guidance
```

**Bypass** (one-off):

```bash
PRE_PUSH_AUTO_REBASE=0 git push origin <branch>
```

**4-line guidance 해석**:
1. `BEHIND` 메시지 — 현재 branch 가 origin/main 보다 N 커밋 뒤처짐
2. rebase 권고 — `git fetch origin main && git rebase origin/main`
3. 충돌 시 — `git rebase --abort` 후 수동 resolve → 재시작
4. bypass — `PRE_PUSH_AUTO_REBASE=0 git push <args>` (one-off)

**Rollback**: `rm .git/hooks/pre-push` 또는 `PRE_PUSH_AUTO_REBASE=0` 환경변수 설정.

Cross-ref: [ADR-063 §결정 5](../archive/adr/ADR-063-marketplace-atomic-invariant.md) sublayer (pre-push auto-rebase guidance) · CFP-447 `pre-push.sh.sample` (sibling atomic invariant hook).

### 1l. Overlay 영역 reconcile (CFP-745 / [ADR-076](../archive/adr/ADR-076-declarative-reconciliation-upgrade.md))

codeforge upgrade 후 `.claude/_overlay/` 영역의 wrapper-managed content 를 consumer customization 을 보존하면서 선언적 3-way merge 로 갱신. **`bash scripts/reconcile-overlay.sh`** 단일 명령으로 overlay 영역 reconcile 완료 (사용자 결정 분기 0 — reconcile-protocol-v1 §결정 `user_decision_branches: 0`).

#### 사용법

```bash
# 기본 (--apply mode): overlay 영역 3-way merge reconcile 실행
bash scripts/reconcile-overlay.sh

# dry-run: 변경 preview (filesystem touch 0)
bash scripts/reconcile-overlay.sh --dry-run

# rollback: 직전 snapshot 에서 복원 (Story-3 snapshot infra 재사용)
bash scripts/reconcile-overlay.sh --rollback
```

#### 동작 원리 (base×marker 2×2 dispatch, ADR-076 §결정 1 Kustomize-inspired)

| base 상태 | marker/sidecar | 동작 |
|---|---|---|
| BASE_OK (snapshot 존재) | MARKER_VALID | 3-way merge (base / wrapper-new / consumer-current) — marker 안 wrapper 갱신, marker 밖 consumer 보존 |
| BASE_ABSENT (첫 reconcile) | MARKER_VALID | marker-aware 2-way first-reconcile — marker 안 wrapper mirror, marker 밖 consumer byte-identical 보존 |
| (base 무관) | MARKER_NONE | wholesale mirror + loss report (preservation scope 부재 → ADR-027 §결정 7.C) |
| BASE_CORRUPT | (무관) | abort-before-touch (partial state 0) |

#### Customization 보존 원칙 (EPIC-AC-4 silent overwrite 0)

- **D4 marker block** (`# BEGIN/END wrapper-managed` — ADR-027 §결정 7.A.1) **안** = wrapper SSOT mirror (codeforge upgrade 전파)
- **marker 밖** = consumer customization byte-identical preserve (reconcile 후 변경 0 invariant)
- **.json 파일**: sidecar manifest `.claude/_overlay/.wrapper-managed-manifest.json` 의 `managed_paths` (RFC 6901 JSON Pointer) 경로만 wrapper mirror, 그 외 consumer key 보존
- **loss 발생 시**: `=== LOSS REPORT ===` stdout 출력 + exit nonzero (consumer 인지 의무 채널)

#### Sidecar manifest (.json 파일 managed key 선언)

```bash
cat .claude/_overlay/.wrapper-managed-manifest.json
```

```json
{
  "schema_version": "1",
  "managed_paths": [
    "/hooks/SessionStart/0/command",
    "/permissions/allow/-"
  ]
}
```

`managed_paths` 는 RFC 6901 JSON Pointer 형식 — wrapper mirror 할 key-path 만 기재. 나머지 consumer JSON key 는 reconcile 후에도 그대로 보존.

#### D4 marker block 없는 파일 (기존 consumer overlay 마이그레이션)

```bash
# D4 marker block 추가 (retroactive wrap)
bash scripts/migrate-existing-customization.sh .claude/_overlay/settings.yml

# 추가 후 reconcile
bash scripts/reconcile-overlay.sh
```

`migrate-existing-customization.sh` 는 기존 파일 전체를 `# BEGIN wrapper-managed` ... `# END wrapper-managed` 로 wrap — 이후 reconcile 에서 3-way merge 경로 활성.

#### 실행 빈도 / 트리거

- codeforge family upgrade (`bash scripts/atomic-upgrade-7-plugins.sh`) 자동 후행 (Story-4 §10 post-atomic gate 정합)
- 수동 ad-hoc: `bash scripts/reconcile-overlay.sh --dry-run` 으로 preview 후 `--apply`
- SessionStart hook 내 자동 실행 = 미권장 (성능 영향 — overlay reconcile = ad-hoc upgrade-time 전용)

참조: [reconcile-protocol-v1 §4.7](inter-plugin-contracts/reconcile-protocol-v1.md) · [ADR-076](../archive/adr/ADR-076-declarative-reconciliation-upgrade.md) · [ADR-027 §결정 7.A.1](../archive/adr/ADR-027-consumer-adoption-protocol.md)

### 1m. ModuleArchitect deputy applicability + migration tool (aggregate-level, CFP-1086 / CFP-1126 / [ADR-042 Amendment 8](../archive/adr/ADR-042-agent-model-selection-policy.md) / [ADR-086](../archive/adr/ADR-086-deputy-creation-decision-framework.md))

codeforge-design lane 의 **ModuleArchitectAgent** (aggregate-level — 구 AggregateArchitectAgent, CFP-1126 / ADR-042 Amd 10 통합) 가 본 consumer 영역에 적용되는지 결정. RDB OLTP aggregate invariant 변호자. 2 field 자율 override (default 적용 — 의도적으로 강제 안 함).

#### `aggregate_arch.applicable` (CONDITIONAL spawn)

```yaml
# .claude/_overlay/project.yaml
aggregate_arch:
  applicable: true    # bool, default true
  migration_tool: alembic    # 9-enum, default alembic
```

**`applicable: true` (default)** — 대부분 consumer 가 RDB OLTP schema 제어권 보유. 설계 lane 진입 시 ModuleArch deputy parallel spawn 활성 (aggregate-level 포함). 6 permanent deputy (SecurityArch / InfraOperationalArch / TestContractArch / DataArch / **ModuleArch** (aggregate-level 포함) / APIContractArch) 모두 활성. mctrader 예시 — RDB OLTP (PostgreSQL + SQLAlchemy + Alembic) + 빅데이터 OLAP (Parquet + DuckDB) 양 영역 보유 → applicable=true.

**`applicable: false`** — ModuleArch deputy (aggregate-level) 미spawn. 다음 consumer 영역에서 선택:

- **frontend-only project** — RDB schema 부재 (예: pure SPA / static site)
- **API-only project** — 외부 RDB consume only, schema 제어권 없음 (예: third-party API client)
- **external-managed RDB** — consumer 가 schema 제어권 없음 (예: SaaS managed DB, customer-managed DB)

`false` 시 6 permanent deputy + 3 sub-tuple = 9 SubAgent (vs default 10) parallel spawn. ArchitectAgent chief 가 RDB OLTP 영역 결정 안내 skip + 사유 명시.

#### `aggregate_arch.migration_tool` (9-enum override)

**Tool layer (consumer override)** — RDB 마이그레이션 도구 선택:

| enum | 적용 stack |
|---|---|
| `alembic` (default) | Python + SQLAlchemy (mctrader reference) |
| `prisma-migrate` | Node.js + Prisma |
| `typeorm` | Node.js + TypeORM |
| `goose` | Go + database/sql |
| `golang-migrate` | Go + golang-migrate/migrate |
| `flyway` | Java + Flyway |
| `liquibase` | Java + Liquibase |
| `sqlx-migrate` | Rust + sqlx |
| `custom` | 9 enum 외 도구 (consumer-defined) |

**정책 layer (stack-agnostic, wrapper 강제)** — Alembic 정책 7 원칙은 모든 tool 에 적용:

1. 양방향 호환 (backward + forward compat)
2. 확장-정리 분리 (expand-then-contract)
3. reverse (rollback path)
4. smoke (smoke test 의무)
5. cross-repo (multi-repo coordination)
6. 백업 (data backup before destructive change)
7. hard limit (max migration size / lock duration)

본 7 원칙 = ModuleArchitectAgent (aggregate-level) 의 mandate (consumer overlay 가 약화 불가). Tool 만 override 자유.

#### 미정의 시 동작

`aggregate_arch` 섹션 자체가 없으면 default 적용 (`applicable: true`, `migration_tool: alembic`). codeforge wrapper 강제 안 함 (consumer 자율). `applicable: true` default 가 안전한 fallback — 대부분 backend project 가 RDB OLTP schema 보유.

#### Write boundary (§4b 정합)

`aggregate_arch.*` field = **consumer-authored only**. 모든 codeforge agent (ModuleArchitectAgent 포함) 는 본 field write 금지. ModuleArchitectAgent (aggregate-level) = consumer overlay value 를 spawn-time Context Packet 으로 수신 후 mandate 결정에 반영 (read-only).

참조: [ADR-042 Amendment 8](../archive/adr/ADR-042-agent-model-selection-policy.md) (7+3+1 roster + AggregateArch 신설) · [ADR-086](../archive/adr/ADR-086-deputy-creation-decision-framework.md) (Deputy 신설 결정 framework P7) · `agents/AggregateArchitectAgent.md` (codeforge-design plugin) · [project-config-schema §aggregate_arch 섹션 설명](project-config-schema.md)

### 1n. 배포 — consumer GitHub Actions/Environments 완전 위임 (CFP-2227 / [ADR-121](../archive/adr/ADR-121-deprecate-deploy-lanes.md)) + 구 Deploy lane (Deprecated)

> **Deprecated ([ADR-121](../archive/adr/ADR-121-deprecate-deploy-lanes.md), D-day 2026-06-13 KST / sunset 2026-07-13 KST — D+1 calendar month)** — 아래 "구 Deploy lane + Deploy Review lane 서술" 의 배포 매커니즘 (codeforge-deploy / codeforge-deploy-review 2 lane, ADR-087 + ADR-088) 은 폐지 결정 확정. sunset 경과 후 Wave 2 (Epic #2217 S5/S6) 가 물리 제거하며, 그때 본 §1n 의 Deprecated 단락도 삭제된다. 신규 consumer 는 아래 "배포 위임 모델"만 따른다.

#### 배포 위임 모델 (ADR-121 §결정 2·3)

배포 = consumer repo 의 **GitHub Actions + GitHub Environments (dev/stg/prd) 단독**. codeforge agent 는 배포를 수행하지 않는다 (배포 권한 0 — ADR-121 §결정 B). wrapper 제공물 = 위임 템플릿만 (seed workflow 2종 + 본 가이드 — ADR-121 §결정 3).

설정 6-step:

1. **GitHub Environments 3개 생성** — repo Settings → Environments → New environment: `dev` / `stg` / `prd` (이름 = seed yml 의 `environment:` key 와 동일 의무).
2. **stg→prd 승인 게이트 (required reviewers)** — prd 승인 차단은 **repo 설정**이 수행하며 workflow yml 내부에 차단 로직을 두지 않는다 (ADR-121 §결정 2 invariant):
   - **UI 경로 (primary)**: Settings → Environments → `prd` → **Required reviewers** 체크 + reviewer 지정 (최대 6명). 이후 `environment: prd` job 은 승인 전 시작되지 않는다.
   - **REST API fallback** (UI 접근 불가 환경): `PUT /repos/{owner}/{repo}/environments/prd` — 예: `gh api -X PUT repos/{owner}/{repo}/environments/prd --input - <<< '{"reviewers":[{"type":"User","id":<user_id>}]}'` (source: GitHub REST API "Deployments → Environments → Create or update an environment" — https://docs.github.com/en/rest/deployments/environments)
3. **환경별 secrets/variables 격리** — Settings → Environments → 각 환경 → Environment secrets/variables. 환경 namespace 분리 invariant: prd secret 은 `environment: prd` job 에서만 주입 (dev/stg job 노출 0).
4. **Deployment branch policy** — `prd` 환경 → Deployment branches → "Selected branches" → `main` 한정 (feature branch 발 prd 배포 차단).
5. **seed 2종 복사** — `templates/github-workflows/consumer-deploy-seed.yml` (build → deploy-dev → deploy-stg → deploy-prd 3-environment job chain) + `templates/github-workflows/post-deploy-smoke.yml` (healthcheck poll + 핵심 시나리오 curl) 을 consumer `.github/workflows/` 로 복사 후 placeholder (build/deploy step + healthcheck URL + smoke 시나리오) 를 채운다 (§1l overlay reconcile 정합). smoke FAIL = workflow 실패 → 다음 환경 promote 차단. 자동 rollback 0 — 사람 판단 (ADR-121 §결정 C 소실 수용).
6. **schema migration 순서** — expand→contract 순서는 아래 "Schema 변경 7 원칙" 단락 + [ADR-089](../archive/adr/ADR-089-schema-change-7-principles.md) cross-ref (재서술 0). ADR-089 는 배포 매커니즘 변경과 독립으로 존치 (ADR-121 §결정 E).

#### Schema 변경 7 원칙 (CFP-1059 / [ADR-089](../archive/adr/ADR-089-schema-change-7-principles.md)) — 존치

schema 변경 mandatory invariant (배포 매커니즘 독립 — ADR-121 §결정 E 존치) — DB schema / inter-plugin contract / API contract / event schema / config schema 변경 시 ChangePlan §11 self-check 표 의무 (S2 carrier mechanical wire):

1. **양방향 호환** — backward + forward 양방향 호환 (신·구 버전 traffic mix window 보장)
2. **expand-contract 분리** — expand (column add / enum extend / 새 entity) ≠ contract (column drop / enum reduce / 기존 entity 제거) PR 분리 의무
3. **reverse** — 모든 schema 변경 = 역방향 migration script 의무
4. **양방향 smoke** — `bidirectional-smoke.yml` workflow (PR-time + scheduled cron)
5. **cross-repo** — multi-layer 변경 시 cross-layer 의존 매핑 (ADR-090 §결정 1 영역)
6. **backup** — production data 변경 시 pre-migration snapshot 의무
7. **hard limit** — column 100+ / row 1억+ / lock 5분+ / depth 3+ 영역 `[empirical-source: TBD]` annotation 의무 (ADR-068 I-5 정합)

#### Cross-layer 참조 정책 (CFP-1059 / [ADR-090](../archive/adr/ADR-090-cross-layer-reference-policy.md))

multi-layer architecture (RDB / 빅데이터 / API / service repo) 운영 consumer 대상:

- **의존 매핑** = 자동 감지 (deps / volume / ORM / contract MANIFEST) + 사용자 declare hybrid
- **layer 별 분리 정책** = RDB strict / 빅데이터 lenient / API strict / event strict / config lenient
- **변경 순서 invariant**: expand = source-first (upstream layer 먼저 변경) / contract = leaf-first (downstream layer 먼저 변경)
- **한쪽 실패** = 묶음 전체 rollback (atomic invariant)

#### 구 Deploy lane + Deploy Review lane 서술 (Deprecated — CFP-1059 / [ADR-087](../archive/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) + [ADR-088](../archive/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md), 이력 보존)

codeforge 가 6 → 8 lane 으로 확장 (CFP-1059) — Epic 묶음 종료 후 자동 배포 + production cutover 사후 검증 lane 추가. **Phase 1 declarative** — 본 단락 안 declarative anchor. 실 DeployPLAgent / DeployReviewPLAgent spawn = lane plugin seed (codeforge-deploy / codeforge-deploy-review) 신설 후 활성 (별 sub-Story carrier). **ADR-121 로 폐지 — sunset 2026-07-13 KST 후 Wave 2 물리 제거 대상.**

##### 활성 조건 (opt-in)

`.claude/_overlay/project.yaml` 안 `deploy:` block 등록 + codeforge-deploy + codeforge-deploy-review plugin install. 양자 부재 시 = Epic 종료 후 `phase:보안-테스트` terminal (CFP-1059 이전 default 동작 유지, breaking 0).

##### 배포 매커니즘 (ADR-087 §결정 5 고정)

- **blue-green deployment**: 신버전 (green) container 가 production network 진입 → healthcheck poll → atomic swap (Traefik label flip) → 구버전 (blue) graceful shutdown.
- **atomic swap**: Traefik routing label 단일 transaction flip (혹은 manual reverse proxy if `traefik.enabled=false`). 0-downtime 보장.
- **3-시간 보존**: atomic swap 후 구버전 container 3 시간 유지 (rollback window). 3 시간 경과 시 cleanup.
- **자동 rollback**: healthcheck 실패 / 성능 미달 / smoke 실패 시 atomic swap revert + Story §10 FIX Ledger append.

##### 인프라 stack (mctrader debut)

- **Docker** (multi-host container orchestration, no Kubernetes)
- **GitHub Actions** (build + push to Docker Hub)
- **Docker Hub** (image registry — `acme/<image>:<tag>` SSOT)
- **SSH pull** (배포 host 가 Docker Hub 로부터 image pull)
- **1Password Connect** (secret provider primary — `OP_CONNECT_HOST` + `OP_CONNECT_TOKEN`)
- **Traefik** (reverse proxy traffic 분배 — label-based atomic swap)

##### Deploy Review lane 검증 3종 (ADR-088 §결정 2)

- **smoke 검증** (양방향 호환 — ADR-089 §결정 4 + `bidirectional-smoke.yml` workflow): blue ↔ green 양 버전 traffic mix window 안 schema 호환 검증.
- **성능 비교** (production runtime measure ↔ pre-deploy baseline): latency / throughput / error rate 3-tuple measure. ADR-068 I-5 dimensional empirical grounding 정합 (`[empirical-source: ...]` annotation 의무).
- **cutover 사후 검증** (ProductionEvidenceDeputy ownership 이관 — codeforge-design CONDITIONAL → codeforge-deploy-review 정식 — ADR-088 §결정 3).

##### Write boundary (§4b 정합 — 구 `deploy.*` field)

`deploy.*` field = **consumer-authored only**. 모든 codeforge agent (DeployPLAgent / DeployWorkerAgent / DeployReviewPLAgent / DeployReviewWorkerAgent + ProductionEvidenceDeputy 포함) 는 본 field write 금지. agent = consumer overlay value 를 spawn-time Context Packet 으로 수신 후 배포 sequence 결정에 반영 (read-only).

참조: [ADR-087](../archive/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) · [ADR-088](../archive/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md) · [ADR-089](../archive/adr/ADR-089-schema-change-7-principles.md) · [ADR-090](../archive/adr/ADR-090-cross-layer-reference-policy.md) · [project-config-schema §deploy 섹션 설명](project-config-schema.md)

### 1o. Confluence migration 셋업 (opt-in, CFP-1668 / [ADR-100 Amendment 2](../archive/adr/ADR-100-confluence-doc-ssot-recognition.md) + [ADR-111 Amendment 2](../archive/adr/ADR-111-confluence-mirror-classification-policy.md))

consumer 측 Confluence doc-mirror 셋업 4-step SOP. **opt-in** — `atlassian.confluence.*` block 부재 시 비활성, 기존 git-only governance 유지 (breaking 0).

Skill 진입점: `codeforge:confluence-migration` (분산 자료 단일 lookup-table).

공통 invariant 7건 (consumer scope 동일 적용, ADR-100 Amendment 2 + ADR-111 Amendment 2):

1. **git = SoR-work** — git repo 가 진실의 원천. Confluence 에서 직접 edit 금지.
2. **Confluence = SoR-docs readable mirror** — 단방향 git→Confluence.
3. **3-anchor verify** — content property: git-source sha256 / native version / sync commit SHA.
4. **mark engine path = retain_for_future** — 현재 MCP-direct 운영 중 (#1320 secret 주입 후 mark engine 활성).
5. **Issue-only retain 5 영역** — Story file / FIX Ledger / Lane Evidence / decision packet / spawn prompt = Confluence mirror 0 (ratchet 강화).
6. **mirror 대상 closed-enum 5** — `adr` / `architecture_doc` / `change_plan` / `domain_knowledge` / `orchestrator_playbook`.
7. **consumer ⊆ wrapper SYMMETRIC subset** — 확장 0 invariant (신규 타입 = ADR-111 Amendment 필요).

#### Step 1 — space 결정

consumer 결정 분기:

- **(a) consumer 자기 Confluence space 생성** (derived default — ownership 명확, parent_id collision 회피)
  - 예: `MCT` (mctrader) / `PROJ` (generic consumer)
  - 권장: 별도 space 가 governance isolation 최적
- **(b) wrapper `CFP` space 안 sub-tree** (cross-org space sharing 정합)
  - 소규모 consumer / cross-org space 계약 있는 경우
  - wrapper admin 에게 parent page 생성 요청 필요

#### Step 2 — IA tree instantiate

`docs/confluence-ia-tree.yaml` schema 1.2 `per_consumer_instantiate_template` section 활용:

```yaml
# .claude/_overlay/confluence-ia-tree-consumer.yaml  (또는 consumer repo 안)
schema_version: "1.2"

space:
  key: <CONSUMER-SPACE-KEY>          # 예: MCT
  id: "<numeric-id>"                 # Confluence space numeric ID
  name: <Consumer Display Name>      # 예: "mctrader"
  cloud_id: "<cloud-uuid>"           # Confluence Cloud 인스턴스 UUID
  instance: <instance-hostname>      # 예: myorg.atlassian.net
  root_homepage_id: "<numeric-id>"   # space root homepage page ID

ia_axis: per-plugin-top-level-plus-cross-cutting-sibling   # wrapper 패턴 답습

deviation_path:
  active: mcp-direct                 # 현재 표준 path (mark engine = retain_for_future)
  rationale: "<consumer-specific rationale>"

mark_engine_path:
  status: retain_for_future
  dependency: "<CONSUMER_ATLASSIAN_API_TOKEN env key>"
```

#### Step 3 — mirror 대상 선택

closed-enum 5 의 subset 선택 + `project.yaml` 갱신:

```yaml
# .claude/_overlay/project.yaml
atlassian:
  enabled: true
  confluence:
    base_url: "https://<instance>.atlassian.net"
    space_key: <CONSUMER-SPACE-KEY>
    instance: <instance-hostname>              # 예: myorg.atlassian.net
    homepage_id: "<numeric-id>"                # Step 2 에서 확인한 root_homepage_id
    mirror_targets: [adr, architecture_doc]    # closed-enum 5 의 subset 선택
                                               # [adr, architecture_doc, change_plan, domain_knowledge, orchestrator_playbook]
    api_token_env: CONSUMER_ATLASSIAN_API_TOKEN
    user_email_env: CONSUMER_ATLASSIAN_USER_EMAIL
    per_doc_type_override:                     # optional — per-doc-type parent page 오버라이드
      adr:
        parent_page_id: "<numeric-id>"
```

**mirror_targets 선택 기준**:

| 타입 | 권장 | 비고 |
|---|---|---|
| `adr` | 권장 | 설계 결정 이력 공유 — governance hub |
| `architecture_doc` | 권장 | 살아있는 구조 설계 문서 (ADR-078) |
| `change_plan` | 선택 | 변경 계획 공유 필요 시 |
| `domain_knowledge` | 선택 | 도메인 지식 공유 필요 시 |
| `orchestrator_playbook` | 선택 | consumer-facing playbook 공유 필요 시 |

#### Step 4 — 첫 push dry-run

> **주의**: `scripts/confluence-sync-3anchor.py` 는 **wrapper-only** 내부 도구 — consumer 배포 자산에 포함되지 않으므로 consumer 가 직접 호출하면 안 됨. consumer 가 받는 Confluence 관련 자산은 `templates/github-workflows/` 의 워크플로우 **3종**뿐:
> - `confluence-doc-sync.yml` — mark engine git→Confluence push (ADR-103 §결정 1)
> - `confluence-drift-detection.yml` — 사후 3-anchor drift verify
> - `issue-design-content-confluence-link.yml`

**dry-run (권장 1순위 — 워크플로우 경로)**:

GitHub Actions UI 에서 `confluence-doc-sync.yml` → **Run workflow** → `full_sync: false` (또는 기본값) 로 실행. 워크플로우 내부에서 mark `--dry-run` flag 가 적용된 경우 실제 Confluence 업데이트 없이 렌더링 결과만 출력함.

> mark `--dry-run` flag 공식 동작: "resolve page and ancestry, show resulting HTML and exit" — 실제 Confluence write 0. mark 버전에 따라 flag 가 워크플로우에 wire 되어 있는지 확인 (`confluence-doc-sync.yml` 내 `mark` 호출 라인 참조).

**apply (실제 push)**:

GitHub Actions UI 에서 `confluence-doc-sync.yml` → **Run workflow** → `full_sync: true` 로 실행.

dry-run 결과 검증:
- mapping table (git path → Confluence page) 정합 확인
- 3-anchor drift verify 는 `confluence-drift-detection.yml` 워크플로우 실행으로 수행 (sha256 / version / commit SHA)
- fail 시 → ADR-101 verify-before-trust path (응답 검증 의무)

#### Step 4b — non-greenfield consumer: title 정합 사전 검증 (apply 전 필수 gate)

**대상**: Wave 1 도입 이전에 MCP-direct 등으로 이미 curated 제목 page 를 Confluence 에 적재한 consumer. git markdown H1 ≠ Confluence page 기존 제목 인 경우, mark `title-from-h1` 모드로 sync 하면 기존 page 를 update 하는 대신 **신규(중복) page 를 대량 생성**할 수 있음 → live space 비가역 오염.

**Gate: dry-run create-vs-update 검증 통과 없이 apply 금지.**

1. **판정** — dry-run 출력에서 각 page 의 처리 결과를 확인:
   - `create` 로 잡히는 page = title drift 신호 (기존 page 와 제목이 불일치하여 신규 page 로 인식).
   - 신규 consumer (Confluence 기존 page 없음) 는 전부 `create` 가 정상.
   - **기존 page 가 있는 consumer 에서 `create` 가 잡히면 title 불일치 → 아래 정합 절차 필수**.

2. **정합 방법 (택1, apply 전 의무)**:
   - **(a) markdown 헤더 주입** — git markdown 파일 상단에 mark 메타데이터 헤더 추가:
     ```markdown
     <!-- Title: <Confluence-에-있는-기존-curated-제목> -->
     ```
     이렇게 하면 H1 과 무관하게 Confluence 기존 page 제목으로 page 를 찾아 update.
   - **(b) Confluence page 제목 rename** — Confluence 에서 기존 page 제목을 git markdown H1 과 일치하도록 변경. 이후 `title-from-h1` 로 정상 update.

3. **검증** — 정합 방법 적용 후 dry-run 재실행. 해당 page 가 `create` → `update` 로 바뀌면 정합 완료.

**SOP gate 명시**: dry-run 에서 기존 page 가 모두 `update` 로 확인된 후에만 apply 진행. mass-duplication 발생 후 복구는 Confluence REST API 개별 삭제 필요 — 사전 차단 우선.

#### Issue-only retain 영역 (ADR-111 Amendment 2 §결정 2 — consumer 동일 적용)

다음 5 영역 = **Confluence mirror 절대 금지** (ratchet 강화):

1. **Story file** (`docs/stories/<KEY>.md`)
2. **FIX Ledger** (Story file §10 sub-section)
3. **Lane Evidence** (Story file §14 sub-section)
4. **decision packet** (`decisions/<packet_id>.yaml`)
5. **spawn prompt** (ephemeral, session-scoped)

#### Write boundary (§4b 정합)

`atlassian.confluence.*` field = **consumer-authored only**. 모든 codeforge agent 는 본 block write 금지. sync agent (ADR-103 carrier) = read-only (consumer overlay value 수신 후 sync 대상 결정).

참조: [ADR-100](../archive/adr/ADR-100-confluence-doc-ssot-recognition.md) · [ADR-111](../archive/adr/ADR-111-confluence-mirror-classification-policy.md) · [ADR-099](../archive/adr/ADR-099-atlassian-allow-redefinition.md) · [ADR-101](../archive/adr/ADR-101-verify-before-trust-confluence-rest.md) · [ADR-103](../archive/adr/ADR-103-git-confluence-sync-mechanism.md) · [project-config-schema §atlassian 섹션 설명](project-config-schema.md) · skill `codeforge:confluence-migration`

## 2. Consumer 프로젝트 구조 초기화

```
<consumer-project>/
├── .claude/
│   ├── _overlay/                       # 프로젝트 특화 overlay (편집 대상)
│   │   ├── project.yaml                # GitHub·labels structured 상수
│   │   ├── CLAUDE.md                   # 프로젝트 narrative
│   │   └── agents/
│   │       ├── DomainAgent.md          # 도메인 전문가 특화
│   │       ├── DataEngineerAgent.md    # 데이터 계층 특화
│   │       └── ...                     # 필요한 에이전트만
│   ├── agents/                         # GENERATED (hook 산출물, gitignore)
│   ├── settings.json                   # SessionStart hook 등록
│   └── settings.local.json             # (선택) 로컬 오버라이드
├── .github/
│   ├── workflows/                      # Plugin 워크플로우 7종 consumer-distributable (수동 cp, CFP-94)
│   ├── ISSUE_TEMPLATE/                 # Plugin Issue Forms 5종 (audit + bug + story + discussion + codeforge-improvement) + config.yml
│   ├── PULL_REQUEST_TEMPLATE.md        # Plugin PR template
│   └── CODEOWNERS                      # architect/domain-expert team 매핑
├── docs/
│   ├── stories/                        # GENERATED (story-init.yml Action 산출 — CFP-65 F2 Phase 1 복원)
│   ├── adr/                            # ADR markdown (ArchitectAgent direct write)
│   ├── change-plans/                   # Architect Change Plan (ArchitectAgent direct write)
│   └── domain-knowledge/               # Domain KB (계층, DomainAgent direct write)
├── CLAUDE.md                           # GENERATED (hook 산출물, gitignore 또는 commit)
├── .claude-work/                       # consumer overlay scratch (gitignore)
└── ...
```

### 2.0. 5분 quickstart (RECOMMENDED — single-command setup, CFP-125)

새 consumer project 에서 처음 codeforge 적용 시 단일 명령 setup + 검증:

```bash
# Setup (idempotent, --dry-run 으로 사전 검증 가능)
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/bootstrap-consumer.sh
  # 8 단계: pre-check / plugin install reminder / overlay scaffold / settings.json /
  #         workflows+forms+CODEOWNERS / labels / consumer-scripts.manifest / summary

# Verify
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-debut-readiness.sh
  # 4 verification: check_bootstrap.py (8 sub-check) / plugin 11종 / project.yaml schema / settings.json 3 hook
```

Windows:

```powershell
pwsh -File ${env:CLAUDE_PLUGIN_ROOT}/codeforge/scripts/bootstrap-consumer.ps1
pwsh -File ${env:CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-debut-readiness.ps1
```

**PASS 시**: 첫 Story Issue Form 제출 가능. `gh issue create --template story.yml` (또는 GitHub UI 의 New Issue → Story).

**KEY 사전 확보 (선택, ADR-036 / CFP-260 — Option B)**: brainstorming 시점에 KEY 미리 확보가 필요하면 `gh issue create --template cfp-reserve.yml` (또는 GitHub UI New Issue → "CFP key reservation"). 받은 Issue # 가 KEY 가 됨 (`<PREFIX>-<#>`, 예: TM-247). spec 작성 후 label `phase:reservation` → `phase:요구사항` + `type:story` 로 promote 시 story-init.yml 자동 트리거. 30 일 미진행 시 `reservation-cleanup.yml` 가 자동 close.

**Version drift 검사 (선택, ADR-037 / CFP-262 / CFP-273 — 권장)**: consumer 가 stale codeforge plugin 으로 작업 진입 시 silent corruption 위험. SessionStart hook 으로 자동 검사 권장.

**Activate (cp 방식, CFP-273)**:

```bash
# Sample hook config 복사 (overlay/hooks/merge.py 가 settings.json 에 자동 merge)
mkdir -p .claude/_overlay/.claude/hooks/
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/.claude/hooks/SessionStart-codeforge-drift.json.sample \
   .claude/_overlay/.claude/hooks/SessionStart-codeforge-drift.json
```

**Manual 실행 (hook 미사용 시)**:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-codeforge-version-drift.sh
# Exit 0 = no drift / MINOR / PATCH (작업 진행)
# Exit 1 = MAJOR drift (hard-stop, /plugins update <name> 의무)
# Exit 2 = prerequisite missing (gh CLI / jq / awk / gh auth status)
```

**Severity → action (ADR-037 cross-ref)**:
- **MAJOR** = hard-stop blocking → `/plugins update <name>` 의무 + Orchestrator 재 spawn
- **MINOR** = warning + auto-proceed → 작업 진행, 사용자에게 update 권유
- **PATCH** = info only → 작업 진행, log 만

**Bypass (긴급 / network 부재 시)**: `BYPASS_VERSION_DRIFT=1 BYPASS_VERSION_DRIFT_REASON='<text>'`. reason field non-empty 의무 (audit trail).

**FAIL 시**: stderr 의 안내 따라 manual fix 또는 §2a-§2h manual fallback 절차 활용. `--dry-run` 으로 변경 미적용 사전 진단, `--reset` 으로 state marker 삭제 + clean 재시도.

**Recovery**:
- Default semantic = `--resume` (`.claude/_overlay/.bootstrap-state.json` marker 인식 + 재개점부터)
- `--force` — marker 무시 모든 단계 재시도 (cp -n 안전망 보존)
- `--reset` — marker 삭제 + clean state from scratch (사용자 확인 prompt 의무)
- 기존 `.claude/settings.json` 는 자동 backup `.claude/settings.json.bak.<ts>` (단계 4 시)

**Plugin install 안내**: `bootstrap-consumer.sh` 가 누락 plugin 11종 listing stdout 출력 — 실 install 은 platform-level (Claude Code `/plugins install` 명령 사용자 직접 실행 의무).

---

### §2g.1 codeforge per-plugin walk CLI (CFP-1170 / ADR-097 + ADR-092 + ADR-096)

> **CFP-1170 (CLI Walk Tier 분리) 변경**: `scripts/codeforge-upgrade.sh` 는 **deprecation shim** 으로 재정의됨 — `scripts/walk-single-plugin.sh` 로 자동 redirect (1 release grace, warning stderr emit). 신규 사용 시 `walk-single-plugin.sh` 직접 사용 권장.
>
> **Transitional 경로 안내 (CFP-744 #752, ArchitectPL Phase 1)**: consumer 의 manual upgrade (`/plugins update` 수작업 + CHANGELOG 수기 + `_overlay/CLAUDE.md` 갱신) 는 **현재 transitional 정상 경로**다. CFP-744 Phase 2 (AC-10 `consumer-scripts.manifest` 등록 + AC-11 `--repo` consumer_repo_root flag + AC-12 §2g.2 end-to-end flow 섹션) merge 시 consumer 자기 repo canonical upgrade flow 배포로 해소된다 (#752 = CFP-744 tracker, Phase 2 merge 시 close).

codeforge **per-plugin** changelog walk 의 진입점. plugin 1개 단위 walk / plan / apply / rollback 4 mode 제공. 7-plugin family atomic 운영은 §2g.2 `walk-bundle-7-plugins.sh` 사용 권장.

```bash
# 1) walk — changelog 변경 내역 확인 (filesystem touch 0)
bash scripts/walk-single-plugin.sh --walk --plugin codeforge
#    → Stage 1: changelog walk 결과 출력 (TOPOLOGICAL 순서 준수 — wrapper first)

# 2) plan — walk + min_prereq topological resolve dry-run (filesystem touch 0)
bash scripts/walk-single-plugin.sh --plan --plugin codeforge
#    → changelog entries + prerequisite 충족 여부 미리보기 (apply 미실행)

# 3) apply — UpgradeAgent 에 위임 packet 출력 (transaction mode)
bash scripts/walk-single-plugin.sh --apply --plugin codeforge
#    → UpgradeAgent spawn 위임 packet 출력 (snapshot → reconcile → sanity 단일 transaction)
#    → --repo <path> 로 consumer_repo_root 명시 가능 (미지정 시 script 부모 디렉터리 fallback)

# 4) rollback — snapshot 복원 위임 packet 출력
bash scripts/walk-single-plugin.sh --rollback 5.74.0 --plugin codeforge
#    → 해당 version snapshot_restore 위임 packet 출력 (snapshot retention = 최근 5개)

# --channel 옵션 (소문자만 valid — 대문자 reject)
bash scripts/walk-single-plugin.sh --walk --plugin codeforge --channel beta
```

> **deprecated shim**: `scripts/codeforge-upgrade.sh` 는 위 `walk-single-plugin.sh` 로 redirect 하는 shim. 실행 시 stderr 에 deprecation warning 출력 후 walk-single-plugin.sh 에 위임함. 1 release grace 후 shim 제거 예정.

**FAMILY membership**: `codeforge` / `codeforge-requirements` / `codeforge-design` / `codeforge-review` / `codeforge-develop` / `codeforge-test` / `codeforge-pmo` 7개. `codex` / `superpowers` 는 구조적 배제 (FAMILY 비구성원 → reject exit 1).

**핵심 동작 보증**: ① mode 정확히 1개 의무 (--walk/--plan/--apply/--rollback 중 1) ② walk/plan = filesystem touch 0 ③ apply = UpgradeAgent 위임 packet (all-or-rollback atomic) ④ --repo dir = 실재 git repo 아니면 abort-before-touch (exit 2) ⑤ marker block (`# BEGIN/END wrapper-managed`) 3-way merge — marker 안 = wrapper SSOT, 밖 = consumer customization 보존. marker 미도입 = wholesale + loss report (silent overwrite 0).

**PAT 요구사항 (ADR-066 Amendment 3)**: reconcile PR open 은 `CODEFORGE_CROSS_REPO_PAT` 에 `reconcile-target-repos contents:write + pull_requests:write` scope 필요 (consumer reconcile 대상 repo 한정 — org-wide write 아님). 상세 = [ADR-066 §결정 2](../archive/adr/ADR-066-pat-rotation-policy.md) + §1.f PAT rotation 정책.

---

### §2g.2 consumer 자기 repo 7-plugin atomic walk end-to-end flow (CFP-1170 / CFP-744 Wave 2 Story-4 / ADR-097 + ADR-037 Amendment 1 / #752 해소)

> **CFP-1170 (CLI Walk Tier 분리) 변경**: `scripts/atomic-upgrade-7-plugins.sh` 는 **deprecation shim** 으로 재정의됨 — `scripts/walk-bundle-7-plugins.sh` 로 자동 redirect (1 release grace, warning stderr emit). 신규 사용 시 `walk-bundle-7-plugins.sh` 직접 사용 권장.

§2g.1 은 per-plugin walk CLI 명세다. 본 §2g.2 는 consumer 가 **자기 repo 를 reconcile target 으로 지정**해 codeforge family **7 plugin (wrapper + 6 lane) 을 단일 topological walk + per-family atomic transaction 으로 upgrade** 하는 end-to-end 경로다 (#752 consumer-distribution 완전 해소 — CFP-744 Phase 2 land 시점).

**(a) 배포 경로 (bootstrap-consumer.sh Stage 7 mirror)**

CFP-744 Phase 2 이후 `templates/consumer-scripts.manifest` 에 다음 6 script 가 등록된다:

```
scripts/codeforge-upgrade.sh        # per-plugin upgrade CLI (deprecation shim → walk-single-plugin.sh)
scripts/codeforge-upgrade.ps1       # per-plugin upgrade CLI (PowerShell, parity)
scripts/lib/path_normalize.py       # §4.5 path 정규화 헬퍼 (sh↔ps1 공유)
scripts/lib/walk_plan.py            # walk + plan Python SSOT (ADR-061 외부 .py — changelog walk / prereq resolve / marker merge)
scripts/walk-single-plugin.sh       # per-plugin walk CLI (CFP-1170 신규 진입점)
scripts/walk-bundle-7-plugins.sh    # per-family 7-plugin topological walk + atomic transaction (CFP-1170 신규 진입점)
```

> **atomic-upgrade-7-plugins.sh**: CFP-1170 이후 deprecation shim — `walk-bundle-7-plugins.sh` 로 redirect. 신규 배포에서 제외되나 기존 consumer 호환을 위해 1 release grace 동안 shim 유지.

`scripts/bootstrap-consumer.sh` Stage 7 가 이 manifest 를 consumer repo `scripts/` 로 1:1 mirror → consumer 는 자기 repo 에서 위 script 에 직접 접근 가능 (별도 수동 복사 불요).

**(b) consumer_repo_root 지정 (`--repo <path>`)**

consumer 가 자기 repo 를 reconcile target 으로 명시 지정한다. resolve 우선순위: `--repo <path>` (명시) > `CODEFORGE_REPO_ROOT` env > script 자기 부모 (미지정 시 fallback — 현 동작 보존, backward-compat). `--repo` 는 mode 인자와 **순서 무관** (orthogonal). 지정 path 가 실재 git repo 아니면 (오타 / 다른 repo / non-git 디렉터리) **abort-before-touch** (filesystem 1 byte 도 변경 전 차단, per-family snapshot 무생성).

**(c) walk → plan → apply → 사후 0-drift 자동 검증**

```bash
# 1) 7-plugin topological walk (filesystem touch 0, snapshot 무생성)
bash scripts/walk-bundle-7-plugins.sh --walk --repo /path/to/your-consumer-repo
#    → FAMILY 7 plugin 전부 TOPOLOGICAL 순서 per-entry transcript 출력

# 2) plan — min_prereq topological resolve dry-run (filesystem touch 0)
bash scripts/walk-bundle-7-plugins.sh --plan --repo /path/to/your-consumer-repo
#    → changelog entries + prerequisite 충족 여부 미리보기

# 3) per-family atomic transaction 적용
#    idempotency pre-check (7 plugin 이미 최신 = no-op 정상 종료)
#    → per-family pre-atomic snapshot → 7 plugin per-plugin reconcile
#    → 사후 0-drift 검증 (codeforge family 7 only — codex/superpowers 제외)
#    → drift 0 = commit / drift > 0 또는 부분 실패 = 전체 7 plugin atomic rollback
bash scripts/walk-bundle-7-plugins.sh --apply --repo /path/to/your-consumer-repo
```

> **deprecated shim**: `scripts/atomic-upgrade-7-plugins.sh` 는 위 `walk-bundle-7-plugins.sh` 로 redirect 하는 shim. 실행 시 stderr 에 deprecation warning 출력 후 walk-bundle-7-plugins.sh 에 위임함. 1 release grace 후 shim 제거 예정.

사후 0-drift 검증은 ADR-037 Amendment 1 invariant 다 — atomic walk `--apply` 완료 직후 7 plugin installed 고정값 ↔ marketplace SSOT drift = 0 (none) 이어야 한다. `atomic-upgrade-zero-drift` evidence-check entry (warning tier) 가 이 정합을 추적한다. 검증 scope = codeforge family 7 plugin 한정 (`codex`/`superpowers` 외부 marketplace 제외 — F-002 옵션 A 7-name loop 구조적 배제, false transaction-fail 0).

**(d) rollback (per-family snapshot)**

```bash
# 직전 per-family pre-atomic snapshot 복원 (7 plugin 일괄 — partial state 0)
bash scripts/walk-bundle-7-plugins.sh --rollback --repo /path/to/your-consumer-repo
```

per-family rollback 은 7 plugin 을 직전 snapshot 시점으로 **일괄** 복원한다 (per-plugin 부분 rollback 없음). snapshot retention = 최근 5개 (FIFO evict). snapshot tar 손상 / checksum 검증 실패 시 silent partial-state 0 — 명시적 escalation (사용자에게 corrupt + 수동 복구 필요 보고). 정상 flow 의 사용자 결정 분기 0 invariant 는 유지 (abort 도 prompt 0).

**(e) transitional → canonical 전환**

§2g.1 머리 "Transitional 경로 안내" 의 manual upgrade (`/plugins update` 수작업 + CHANGELOG 수기 + `_overlay/CLAUDE.md` 갱신) 는 본 §2g.2 canonical flow 가 land 된 시점부터 canonical 경로로 supersede 된다. consumer 는 본 §2g.2 flow 를 우선 사용하고, manual 경로는 환경 제약 (script mirror 미배포 등) 시 fallback 으로만 사용한다 (transitional 정상 경로 — degraded mode 아님).

---

### §2g.3 codeforge channel CLI + migration tool (CFP-932 Wave 4 sub-Epic #1 Story-2 / ADR-076 §결정 9 + reconcile-protocol-v1 v1.8)

codeforge family 7 plugin (wrapper + 6 lane plugin) 은 **release channel** 차원을 갖는다 — version specifier 와 독립적인 추적 트랙 (어떤 maturity track 을 따르는가). channel 은 family 단위로 atomic 하게 고정되며 (per-plugin override 불가), consumer 는 1회 선언으로 7 plugin 을 동시에 동일 channel 로 resolve 한다 (사용자 결정 분기 0 invariant 보존).

**3-tier 선택 가이드** (ADR-076 §결정 9.1):

| tier | risk class | 권장 사용자 | 의미 |
|---|---|---|---|
| `stable` | **LOW** (production impact: none) | developer self-service OK | 기본값 (default). 검증 완료된 current active channel |
| `beta` | **MEDIUM** (observable but reversible) | developer + reviewer awareness 충분 | opt-in incremental track |
| `canary` | **HIGH** (production-impact tier) | **admin 권장** (ADR-076 §결정 9.4) | preview + production cutover 영향. consumer CODEOWNERS auto-review path 권장 (consumer-side governance — codeforge wrapper enforcement 0) |

> **canary tier admin advisory**: `canary` tier 선언은 production-impact 결정이다. consumer org 는 `.claude/_overlay/project.yaml codeforge.channel.tier: canary` 변경 PR 을 CODEOWNERS auto-review path (admin 검토) 로 게이트할 것을 권장한다. silent canary uptake (developer self-service via PR edit) 차단 = consumer governance gate 책임.

**channel CLI 사용법** (`codeforge.channel.tier` 미선언 시 derived default `stable`):

```bash
# consumer overlay 의 codeforge.channel.tier resolve (CLI --channel 미지정, per-plugin walk)
bash scripts/walk-single-plugin.sh --walk --plugin codeforge

# CLI 로 명시 channel 고정 (overlay 보다 우선 — CLI override 시 stdout 에 visible 출력)
bash scripts/walk-single-plugin.sh --apply --plugin codeforge --channel beta

# 7-plugin family atomic channel walk (mixed channel 감지 시 abort-before-touch)
bash scripts/walk-bundle-7-plugins.sh --apply --channel stable
```

> **deprecated shim**: `scripts/codeforge-upgrade.sh --channel ...` 와 `scripts/atomic-upgrade-7-plugins.sh --channel ...` 는 각각 `walk-single-plugin.sh` / `walk-bundle-7-plugins.sh` 로 redirect 하는 shim — 1 release grace 동안 동작 유지. 신규 사용 시 walk CLI 직접 사용 권장.

CLI `--channel` 명시값은 consumer overlay `codeforge.channel.tier` 보다 우선한다 (`--repo` 우선순위 패턴 동형). 충돌 시 stdout 에 `CLI override: overlay=<X> → CLI=<Y>` 가 visible 출력된다 (사용자 결정 분기 0 invariant 보존 — prompt 없이 가시화만). **override 대상이 `canary` tier 인 경우** stderr 에 `[PRODUCTION-IMPACT WARNING]` 가 추가 emit 된다 (production-impact 결정의 가시성 보강 — 진행은 정상, abort 없음).

**migration tool — 기존 consumer (channel 미선언) 의 tier 역추론**:

```bash
# 현 install plugin.json version → channel tier 역추론 + project.yaml block 제안 (출력만, write 0)
bash scripts/infer-channel-from-version.sh
```

`infer-channel-from-version.sh` 는 현 install plugin.json `.version` 을 registry marketplace.json `channels[*].versions[]` membership 로 역추론하여 적합한 `codeforge.channel.tier` 를 **제안 출력만** 한다 (stdout). **consumer project.yaml 을 직접 write 하지 않는다** (ADR-027 §4b consumer-authored write boundary 절대 invariant — agent/script write 0). consumer 는 stdout block 을 검토 후 `.claude/_overlay/project.yaml` 에 수동 paste 한다 (human-in-the-loop gate). 매칭 tier 가 없으면 (registry channels[] 미populate 등) `unknown` + `stable` 권장을 출력한다 (graceful — 정상 transitional 동작).

**channel drift 자동 감지**: `channel-drift-detection.yml` workflow (24h cron + manual `workflow_dispatch`) 가 3-tuple drift — (a) consumer `codeforge.channel.tier` ↔ (b) 실 install plugin.json `.version` ↔ (c) registry marketplace.json `channels[*].versions[]` membership — 를 감지하여 drift 시 Issue auto-create (signature dedup) 한다. warning-first failure mode (CI block 0, advisory Issue). `hotfix-bypass:channel-drift-detection` label 로 조건부 skip 가능 (audit comment 자동 발의 동반).

---

### §2g.4 canary promotion criteria 4-tuple gate (CFP-991 Wave 4 sub-Epic #1 Story-4 / ADR-72 Amendment 3 + ADR-076 §결정 9.6 + reconcile-protocol-v1 v1.11 §4.14)

§2g.3 channel CLI 가 `codeforge.channel.tier: canary` 활성 후, consumer 는 **canary → beta → stable promotion** 경로를 따른다. 본 §2g.4 는 promotion gate 평가 시점의 **4-tuple evidence quad** (functional + security + monitoring + testing) measurement source SSOT 와 consumer obligation 을 정의한다 (wrapper Tier-1 declare-time scope 외 — consumer canary tier 활성 Story carrier 영역).

**4-tuple measurement source SSOT** (ADR-076 §결정 9.6 / reconcile-protocol-v1 v1.11 §4.14):

| Sub | measurement source | gate_state enum |
|---|---|---|
| **functional** | consumer Story functional test pass-rate (bats GREEN ratio + integration test PASS evidence) | `pass` / `fail` / `n_a` |
| **security** | consumer Story SecurityTestPLAgent verdict + ProductionEvidenceDeputy spawn evidence | `pass` / `fail` / `n_a` |
| **monitoring** | consumer production-side monitoring metric (Prometheus rate / WAL sample / drainage rate) | `pass` / `fail` / `n_a` |
| **testing** | consumer Story IntegrationTestAgent verdict (Epic-level baseline) | `pass` / `fail` / `n_a` |

**aggregation rule**: 4 sub all `pass` OR (`pass` + `n_a` 조합) = promotion gate proceed / 1+ `fail` = promotion abort (warning_first → blocking_on_pr fallback orthogonality, ADR-060 §결정 5 default).

**4 industry exemplar (verbatim SSOT cite, ADR-076 §결정 9.6)**:
- **Chrome 3-channel** primary — Stable / Beta / Canary (Chrome 4-channel 변종 도입 0건 invariant)
- **npm dist-tag** 보조 — latest / next / canary
- **Rust 3-channel** 보조 — stable / beta / nightly
- **K8s 3-stage** 보조 — GA / Beta / Alpha
- 추가 reference (sub-bullet): K8s KEP-5241 Implementing User Friendly Production Readiness (2024-12) / AWS CodeDeploy Blue-Green Linear/Canary deployment / Helm release lifecycle

**consumer obligation** (Tier-2 admin-tier 권장 advisory, wrapper enforcement 0):

1. **canary tier 활성 PR 의 CODEOWNERS auto-review** — `.claude/_overlay/project.yaml codeforge.channel.tier: canary` 변경 PR 을 admin tier 검토 경로로 게이트 (ADR-076 §결정 9.4 silent canary uptake mitigation 정합)
2. **promotion gate label 부착 의무** — canary → beta promotion PR open 시 `gate:channel-canary-promotion` label 부착 (label-registry-v2 v2.35 entry, attach_owner_plugin: consumer_repo_only invariant) + 4-tuple evidence quad measurement 결과 PR body 안 명시
3. **4-tuple evidence quad measurement 의무 (Tier-2 runtime)** — ProductionEvidenceDeputy spawn 영역 (consumer Live touching Epic carrier, ADR-72 §결정 1 정합)
4. **single-aggregator bypass 금지** (ADR-070 §결정 D6 / CFP-988 Amendment 4 mandatory-real-execution-evidence STANDING 4-tuple): (a) CR-own discriminating revert / (b) reconcile-integration path / (c) DevPL pasted stdout 미신뢰 / (d) single-aggregator/single-unit bypass forbidden — real execution evidence direct verify 의무

**canary promotion criteria 자동 lint** (warning tier): `canary-promotion-criteria.yml` workflow (PR-open + workflow_dispatch 2-trigger split, ADR-72 §결정 5 production-cutover-evidence.yml byte-pattern 답습) 가 PR 의 4-tuple measurement source + family_7_atomic_canary_pin three_way_match + enum closed-set invariant 자동 verify. warning-first failure mode (CI block 0, advisory). `hotfix-bypass:canary-promotion-criteria` label 로 조건부 skip 가능 (audit comment 자동 발의 동반, label-registry-v2 v2.35 43번째 hotfix-bypass family member).

**wrapper-self-app exemption (Tier-1, ADR-72 §결정 6 invariant)**: wrapper plugin 자체 = production cutover 영역 외 (plugin = code 0 + runtime behavior 0 + production deploy state 부재). wrapper PR 의 triple-AND fast-PASS 조건 (`production_cutover_touching=true AND repo=wrapper AND code_change=0`) 충족 시 promotion criteria check 영구 fast-PASS — consumer canary tier 활성 Story 만 Tier-2 runtime measurement 영역.

**downgrade 경로 (canary → beta → stable demotion)**: §2g.4 = forward path (promotion) 한정. downgrade asymmetry marker = `reconcile-protocol-v1 v1.11 §4.14 downgrade_asymmetry_marker.status: placeholder_reserve` field 영역 (Story-5 carrier 별 CFP, §4.8 version_handshake placeholder_reserve→active 단독 promotion 선례 답습).

---

### §2h.1 SessionStart prereq-check hook 자동 활성 (CFP-475 / ADR-038 Amendment 3 이후)

Codeforge orchestration 의 critical path tool 인 **TodoWrite** 는 Claude Code harness 의 **deferred tool** — turn 0 시점에 schema 가 노출되지 않아 `ToolSearch("select:TodoWrite")` 로 lazy-fetch 해야 호출 가능. CFP-475 / ADR-038 Amendment 3 이후 **plugin-root `hooks/hooks.json` 에 자동 등록** — 별도 consumer `.claude/settings.json` 등록 절차 불필요.

Consumer 가 `/plugins install codeforge@mclayer` 만 수행하면 plugin-root `hooks/hooks.json` 의 `SessionStart` entry 가 자동 활성된다 (Claude Code 공식 spec — plugin install 시점에 plugin-root `hooks/hooks.json` discovery + auto-load). **별도 `.claude/settings.json` 등록 절차 불필요**.

**기존 consumer migration**: `.claude/settings.json` 안 `hooks.SessionStart[]` array 에 `check-codeforge-prereq.sh` 호출 entry 가 잔존하면 plugin-root 활성과 중복 (one-channel rule 위반). **권장 cleanup 절차**:

1. `.claude/settings.json` 의 `hooks.SessionStart[]` 안 `command` 가 `check-codeforge-prereq.sh` 를 포함한 entry 1건 삭제 (육안 확인 — 자동 lint 는 자기거버넌스 prune 으로 제거됨, one-channel rule 자체는 유효)
2. Claude Code 세션 재시작 → 첫 turn `additionalContext` 안 `ToolSearch select:TodoWrite` substring 발화 확인

**Bypass (advisory)**: 환경별 사유로 prereq-check 발화 제어 시 — `BYPASS_CODEFORGE_PREREQ=1` env 설정 시 hook short-circuit (stdout empty + harness injection 0 + stderr 1-line audit echo). 기존 `BYPASS_PREREQ_CHECK=1` 도 1 release 동안 호환 유지 (deprecation warning stderr 출력, 후속 CFP 제거 예정).

**Sample file 처리** (`templates/.claude/hooks/SessionStart-codeforge-prereq-check.json.sample`): CFP-475 부터 deprecated. 본 sample 은 1 release grace 후 별도 CFP 에서 삭제 — 그때까지 기존 등록 reference 보존용으로만 잔존.

**Layered defense (fallback retain)**:
- hook 미활성 / 실행 실패 → harness 가 stdout 부재 처리 → Orchestrator 가 runtime `ToolSearch("select:TodoWrite")` attempt 로 fallback (ADR-038 §결정 8 retain)
- runtime fallback 도 실패 → 경고 출력 후 작업 계속 (lane 차단 없음, §결정 7 layered defense retain): `⚠️ TodoWrite 스키마 로드 실패 — 레인 진행 표시 불가 (warning only)`

**책임 경계** — hook = schema 가용성 advisory layer 한정. mechanical function-call 강제 아님 — behavioral compliance 자체는 여전히 Orchestrator 책임 (Researcher 3-tier 중 (b) layer 한정).

---

### §2h.2 bootstrap-labels workflow 자동 install (CFP-662 / ADR-060 Amendment 10 §결정 24 이후)

Consumer repo 의 첫 PR open 시점에 codeforge 필수 label set (`phase:*` / `gate:*` / `type:*` / `hotfix-bypass:*` / `severity:*` / `audit:*` / `component:*`) 부재 시 `phase-gate-mergeable` CI check 가 초회 실행 FAIL — 본 영역 해소 carrier (RETRO-MCT-104, mctrader-data PR #14 2026-05-09 evidence).

**자동 install 절차** (codeforge plugin install 직후 1회):

1. `/plugins install codeforge@mclayer` 수행 (plugin-root `hooks/hooks.json` `SessionStart` entry 자동 활성).
2. Consumer repo 의 `.claude/_overlay/` 활성 시 — SessionStart `regen-agents.sh` 가 매 세션 시 `cp -n` (no-clobber) 으로 신규 workflow file 자동 propagate (CFP-110 + §2c manifest-driven loop).
3. `.github/workflows/bootstrap-labels.yml` 부재 시 — §2c `cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/*.yml .github/workflows/` glob copy 가 자동 포함 (별도 절차 불필요).
4. 첫 PR open 시점에 workflow trigger → `scripts/bootstrap-labels.sh` 1회 실행 → 부재 label set 자동 주입 → 후속 lane (요구사항 / 설계 / 설계-리뷰 / 구현 / 구현-리뷰 / 구현-테스트 / 보안-테스트) 모두 보호.

**Workflow 동작 spec** (Phase 2 PR carrier):

| 영역 | 값 |
|---|---|
| Trigger | `on.pull_request.types: [opened]` only (synchronize / labeled / reopen 미발화 — PAT-loop prevention) |
| Concurrency | `bootstrap-labels-${{ github.event.pull_request.number }}` per-PR dedup |
| continue-on-error | `true` (warning tier first entry, chicken-and-egg deadlock 회피, first-PR-ever 보호) |
| Script invocation | `bash ${{ github.workspace }}/scripts/bootstrap-labels.sh` (idempotent 3-fallback chain) |
| Primary token | `${{ secrets.CODEFORGE_CROSS_REPO_PAT }}` (CFP-450 / ADR-066 — 90 day rotation) |
| Fallback token | `${{ secrets.GITHUB_TOKEN }}` (PAT 부재 / scope 부족 시 silent advisory) |
| Permissions | top-level `issues: write` + `pull-requests: write` (least privilege, ADR-060 Amendment 8 정합) |
| Required check | branch protection `required_status_checks.contexts` **미부착** (warning advisory only) |

**Bypass (advisory)**: 본 workflow 가 임의 사유로 발화 차단 필요 시 — `hotfix-bypass:bootstrap-labels` label 부착 시 workflow conditional skip + audit comment 자동 발의 (`scripts/check-bypass-audit-comment.sh` 1st-19th entry 동일 패턴, label-registry-v2 v2.14 PATCH 20번째 family member). PR description `### Bypass reason` 섹션 기재 필수.

**Edge Cases**:
1. **CRITICAL**: `.github/workflows/bootstrap-labels.yml` 부재 시 — §2c manifest-driven loop 수행 의무 (workflow file copy 누락 시 phase-gate-mergeable 여전히 실패).
2. `CODEFORGE_CROSS_REPO_PAT` scope 부족 → silent fail + warning advisory (SecurityTestPL 수동 fallback 의무).
3. bootstrap-labels.sh PyYAML 미설치 (Windows / minimal env) → CFP-598 fallback warning (silent skip 금지).
4. label-registry-v2 version bump 후 workflow re-trigger 의무 = 별 Story 후속 scope 외 (Multi-family drift 패턴 검증).

**책임 경계** — bootstrap-labels workflow = PR-time precondition check tier 한정 (ADR-060 §결정 5 default warning). mechanical enforcement 강제 아님 — `continue-on-error: true` warning advisory only. 실제 enforce 승격 (warning → blocking-on-pr) 은 ADR-060 §결정 6 AND condition (PR 누적 ≥ 20 + bypass 외 failure = 0) 충족 시 별 carrier Story 발의 후.

**Cross-ref**: ADR-060 Amendment 10 §결정 24 SSOT (`docs/adr/ADR-060-evidence-enforceable-promotion-framework.md`) + label-registry-v2 v2.14 entry (`docs/inter-plugin-contracts/label-registry-v2.md`) + evidence-checks-registry `bootstrap-labels-precondition` entry (`docs/evidence-checks-registry.yaml`).

---

### §2h.3 사용자 대화 품질 hook (UserPromptSubmit + Stop) 자동 활성 (CFP-1738)

Orchestrator 가 사용자에게 **codeforge 내부 식별자**(ADR/CFP 번호·§결정·내부 코드네임·계약명)를 풀이 없이 써서 이해를 방해하는 것을 막는 2개 hook. **일반 기술 용어**(hook / worktree / schema / latency 등)는 대상 아님 — 사용자가 엔지니어라는 전제.

| Hook | 파일 | 동작 | 의존성 |
|---|---|---|---|
| UserPromptSubmit | `hooks/plain-language-reminder` | 답변 발화 직전 3규칙(평범하게 / 불필요한 질문 금지 / 구조로 전달)을 컨텍스트에 주입 (예방) | 없음 (순수 bash) |
| Stop | `hooks/plain-language-check` → `plain-language-check.py` | 직전 답변에 내부 식별자가 임계치 이상이면 `decision=block` → 평범하게 재작성 유도 | python (없으면 통과) |

**자동 활성**: `/plugins install codeforge@mclayer` 만 하면 plugin-root `hooks/hooks.json` 의 UserPromptSubmit + Stop entry 가 자동 활성 (별도 `.claude/settings.json` 등록 불필요).

**설정 (consumer 환경변수)**:

| env | 기본 | 효과 |
|---|---|---|
| `BYPASS_PLAIN_LANGUAGE=1` | off | 두 hook 모두 끔 |
| `PLAIN_LANG_JARGON_THRESHOLD=N` | `1` | 검사 발동 임계치 (1 = 내부 식별자 1개라도 발견 시 재작성) |
| `PLAIN_LANG_EXTRA_PATTERNS=re1,re2` | (없음) | consumer 고유 용어 정규식 추가 (쉼표 구분, 잘못된 정규식은 무시) |

**한계 (명시)**: Stop hook 은 답이 화면에 표시된 **후** 작동 → 잡소리를 "안 보이게" 막지 못하고 "노출 즉시 재작성"하게 만든다. 진짜 0 노출은 Orchestrator 규율 + reminder hook 의 사전 주입이 책임. mechanical 강제 아님 (Stop block 은 재작성 유도이며 사용자 입력 차단이 아님).

**fail-safe**: python 부재 / 파싱 오류 / 예외 시 검사를 건너뛰고 통과 — 사용자 작업을 막지 않음.

---

### §2h.4 한영 키보드 레이아웃 자동 변환 추론 hook (CFP-1751)

사용자가 한영 전환 키를 누르지 못해 잘못된 레이아웃으로 입력했을 때(예: `dkssudgktpdy` 는 두벌식 한글 키보드에서 `안녕하세요` 의 키 시퀀스 — 영문 모드였음), 두벌식 ↔ QWERTY 매핑 변환을 시도해 Orchestrator 가 의미를 추정하고 답변할 수 있게 한다.

| Hook | 파일 | 동작 |
|---|---|---|
| UserPromptSubmit (추가 entry) | `hooks/korean-english-recovery` → `korean-english-recovery.py` | 양방향 변환 시도 → 품질 점수 임계치 이상이면 `additionalContext` 로 추정 결과 주입. Orchestrator 가 변환 의미로 답변하고 첫 줄에 "한영전환으로 읽음: <원문> → <변환문>" 통보. |

**자동 활성**: `/plugins install codeforge@mclayer` 만 하면 plugin-root `hooks/hooks.json` UserPromptSubmit 의 두 번째 entry 로 자동 활성. python 부재 시 통과(fail-safe).

**설정 (consumer 환경변수)**:

| env | 기본 | 효과 |
|---|---|---|
| `BYPASS_KOREAN_ENGLISH_RECOVERY=1` | off | 비활성화 |

**탐지 기준 (heuristic, false positive 회피)**:
- eng→kor: 입력이 두벌식 매핑 가능한 ASCII letter 비율 ≥ 80% + 변환 결과의 합성 음절 비율 ≥ 70%
- kor→eng: 입력의 Hangul 음절 비율 ≥ 70% + 변환 결과가 영어 vowel 분포(0.20~0.60) 내 letter 비율 ≥ 80%
- 1~3자 짧은 단독 단어 / 의미 명확한 문장 → 변환 안 시도

**한계**:
- `UserPromptSubmit` hook 은 사용자 원문을 수정할 수 없음 → `additionalContext` 주입만. Orchestrator 가 통보 후 진행 (사용자 정정 가능).
- 양쪽 모두 의미 있을 때는 더 높은 품질 점수 후보를 우선 추정. 틀리면 사용자가 한 마디로 정정.
- heuristic 기반 → false positive/negative 가능. 첫 줄 통보가 즉시 정정 경로.

**fail-safe**: python 부재 / 파싱 오류 / 예외 시 검사를 건너뛰고 통과 — 사용자 입력 차단하지 않음.

---

### §2h.5 Runtime hook presence 등록 의무 및 evidence gate (CFP-1745 / ADR-115)

Codeforge 가 올바르게 동작하려면 `hooks/hooks.json` 에 아래 4개 hook entry 가 존재해야 한다. `/plugins install codeforge@mclayer` 를 수행하면 plugin-root `hooks/hooks.json` 이 자동 활성화되어 **별도 등록 절차 없이** 4 entry 가 포함된다.

| Hook 종류 | 역할 | ADR-115 §결정 |
|---|---|---|
| `UserPromptSubmit` | 사용자 프롬프트 제출 직후 Orchestrator 행동 규율 주입 (plain-language-reminder / korean-english-recovery / userprompt-submit) | §결정 2 |
| `PreToolUse[matcher:Agent]` | Agent tool 발동 직전 spawn gate (pretooluse-agent-spawn-gate) | §결정 3 |
| `Stop` | Orchestrator 응답 완료 직후 발화 품질 검사 (plain-language-check / stop) | §결정 5 |
| `SubagentStop` | subagent 완료 직후 ledger 기록 (subagent-stop) | §결정 5 |

**등록 확인 방법**:

```bash
bash scripts/check-runtime-hook-presence.sh all
```

4 hook 모두 `OK` 출력 시 정상. `WARNING` 출력 시 hook 부재 — `/plugins install codeforge@mclayer` 재실행으로 복구.

**Evidence gate (CFP-1745 / ADR-115 + ADR-060)**:

`runtime-hook-presence.yml` workflow 가 PR-time 에 4 hook entry presence 를 자동 검증한다 (warning tier — non-blocking). 4 evidence-check entry 는 단일 bypass family `hotfix-bypass:runtime-hook-presence` 를 공유.

**한계 및 알려진 버그 (platform bug #10412)**:

Stop / SubagentStop hook 이 plugin-deploy 후 간헐적으로 발화 중단될 수 있다. 이는 Claude Code harness 의 platform 버그 (#10412) 로, hook 파일이 존재함에도 trigger 가 누락되는 현상이다. 발생 시:

1. `hooks/hooks.json` 에 해당 entry 가 있는지 확인 (`bash scripts/check-runtime-hook-presence.sh stop`)
2. entry 가 있는데도 발화 안 되면 platform bug #10412 — `/plugins reinstall codeforge@mclayer` 시도
3. PR 이 runtime-hook-presence lint 로 차단될 경우 `hotfix-bypass:runtime-hook-presence` label 부착 후 진행

**`overlay/hooks/userprompt-reminder.{sh,ps1}` deprecated (1 release grace)**:

기존 consumer 가 `.claude/_overlay/hooks/userprompt-reminder.sh` 또는 `.ps1` 로 등록한 경우 — plugin-root `hooks/hooks.json` 첫 번째 `UserPromptSubmit` entry 와 중복. 1 release grace 기간 안에 아래 절차로 cleanup 권장:

1. `.claude/_overlay/hooks/userprompt-reminder.{sh,ps1}` 파일 제거
2. `.claude/settings.json` `hooks.UserPromptSubmit[]` 안 해당 entry 삭제 (있는 경우)
3. `bash scripts/check-runtime-hook-presence.sh userprompt` 로 plugin-root entry 정상 활성 확인

---

### §2i. 3-way version atomic 고정 설정 (CFP-820 / ADR-063 Amendment 5 §결정 15)

Consumer repo 에서 **codeforge version 을 고정** 하고 PR-time 에 publisher ↔ registry ↔ consumer 3-way 버전 일치를 자동 검증하는 선택 기능이다.

**동작 원리**:
- **publisher** = `.claude-plugin/plugin.json` `.version`
- **registry** = `mclayer/marketplace` `.claude-plugin/marketplace.json` `.plugins[codeforge].version`
- **consumer** = `.claude/_overlay/project.yaml` `codeforge.version_pin.version`
- `version-3way-atomic.yml` workflow 가 PR-time 에 3개 값 byte-identical 비교 (blocking-on-pr tier)

**설정 절차**:

1. `.claude/_overlay/project.yaml` 에 아래 블록 추가:

```yaml
codeforge:
  version_pin:
    version: "5.82.0"  # 현재 설치된 codeforge 버전으로 치환
```

2. `version-3way-atomic.yml` workflow 가 `.github/workflows/` 에 복사되어 있는지 확인 (§2c manifest-driven loop 수행 시 자동 포함).

3. PR 머지 후 `check-3way-version-parity.sh` 수동 실행으로 현재 상태 verify:

```bash
bash scripts/check-3way-version-parity.sh
```

**Fallback (고정 미선언)**: `codeforge.version_pin` 블록 부재 시 workflow 는 **warning-first exit 0** (orthogonality invariant — 고정 미선언 ≠ 버전 불일치). 버전 고정이 필요하지 않으면 생략 가능.

**codeforge upgrade 후 고정값 갱신**: `/plugins update codeforge@mclayer` 수행 후 `project.yaml` 의 `codeforge.version_pin.version` 값도 새 버전으로 갱신 의무. `version-3way-atomic.yml` 이 불일치 감지 시 PR blocking.

**Bypass (24시간 이내 sync 의무)**: 긴급 상황에서 일시 bypass 가 필요한 경우 PR 에 `hotfix-bypass:version-3way-atomic` label 부착 → 24시간 이내 3-way sync 완료 + label 제거 의무 (ADR-024 Amendment 3 hotfix-bypass family 정합).

**Cross-ref**: ADR-063 Amendment 5 §결정 15/16 SSOT + `docs/evidence-checks-registry.yaml` `version-3way-atomic` entry + `label-registry-v2` v2.24 + `scripts/check-3way-version-parity.sh` + `scripts/read_version_pin.py`.

### §2j. Production cutover surface 진입 (CFP-954 / ADR-72 §결정 1 + §결정 5)

Consumer repo Story 가 **production cutover surface** (real funds / live exchange API / production credential / live order placement) 에 진입하는 경우의 governance discipline + ProductionEvidenceDeputy 발동 trigger.

**동작 원리 (5 layer)**:
- **L1 mandate declare** = wrapper plugin 자체 (CFP-632 Phase 1 + CFP-954 mandate activation declare) — ADR-72 §결정 1-7 SSOT
- **L2 trigger axis** = Live touching + production cutover both → 9 SubAgent (6 permanent + LiveOps + LiveOrdering + ProductionEvidence) spawn 의무 (ADR-72 §결정 3)
- **L3 evidence quad** = bucket prefix listing / WAL sample / drainage rate / cadence trigger 4중 (ADR-72 §결정 5)
- **L4 EPIC CLOSED gate** = PMOAgent retro epic_close_gate (Sibling Story-4 plugin-codeforge-pmo#18 carrier — 구 lane repo issue, repo 삭제됨 2026-06-12, 현 `plugins/codeforge-pmo/`. Story-3 = warning tier, blocking-on-pr 승격 = follow-up CFP-Z' carrier)
- **L5 user explicit go-ahead** = Phase 1 PR open 전 사용자 명시 confirm 의무 (production-touching label 부착 + Story frontmatter `production_cutover_touching: true` dual-source AND, ADR-72 §결정 6 wrapper-self-app N/A invariant 정합)

**4 prerequisite measurement source mechanical anchor 4-tuple (Change Plan §3.5 + ADR-72 amendment_log Amendment 2)**:

| Anchor | Measurement source | 측정 방식 |
|---|---|---|
| MS-1 `live_touching` | Story file frontmatter (`live_touching: bool`) | `yaml.safe_load` (grep parse 금지, CFP-699 CR-821-6 strict-verify 정합) |
| MS-2 `production_cutover_touching` | Story frontmatter AND GitHub label `production-touching` (dual-source AND) | dual-source mismatch = fail-loud Issue auto-create dedup signature |
| MS-3 `marketplace_publish_touching` | `git diff plugin.json .version` + `marketplace.json channels[]` field touch | Story-4 carrier — Phase 1 declare-time = best-effort detection |
| MS-4 `consumer_impact_blast_radius` | `marketplace.json plugins[codeforge].channels[]` consumer count proxy | ADR-068 I-5 dimensional empirical anchor (proxy approximation, exact count = consumer survey 영역 OOS) |

**설정 절차 (consumer Story 영역)**:

1. **Story §1 frontmatter 작성** — `live_touching: true` + `production_cutover_touching: true` 양 field 명시.
2. **GitHub Issue 부착** — `production-touching` label 부착 (사용자 직접 OR Orchestrator 자동 부착).
3. **사용자 explicit go-ahead** — Phase 1 PR open 전 사용자 명시 confirm 의무 (Story body 안 `[user-input]` marker 정합).
4. **ArchitectPL deputy spawn** — Live touching + production cutover both = ProductionEvidence + LiveOps + LiveOrdering 3 CONDITIONAL SubAgent both spawn (총 9 SubAgent).
5. **`production-cutover-evidence.yml` workflow trigger** — PR-open 시 evidence verify 자동 발동 (warning tier `continue-on-error: true`, blocking 0).
6. **EPIC CLOSED gate** — PMOAgent retro epic_close_gate 안 4-evidence-quad 명시 의무 (Sibling Story-4 carrier — production cutover Epic close 시점 evidence quad lint warning tier).

**Wrapper-self-app exemption (ADR-72 §결정 6 정합)**:
- wrapper plugin 자체 (`mclayer/plugin-codeforge` repo) = production cutover 영역 외 (code 0 + runtime behavior 0 + production deploy state 부재) — ProductionEvidenceDeputy spawn N/A
- Tier-1 declare-time exemption (repo=wrapper) = frontmatter/amendment_log/cross-ref presence verify only (실 4-evidence-quad measurement skip)
- Tier-2 runtime (repo=consumer) = 실 4-evidence-quad measurement 의무

**Bypass (24시간 이내 sync 의무)**: `hotfix-bypass:prod-cutover-deputy-evidence` label 부착 시 workflow skip + `[bypass-justification]` PR comment marker 의무 (CFP-845 framework 자동 cover, ADR-024 Amendment 8 §결정 6.A.4 정합).

**CODEFORGE_CROSS_REPO_PAT (5번째 consumer)**: production-cutover-evidence.yml 은 same-repo Story file + label 만 inspect (cross-repo PAT 사용 0건 권고) — wrapper-self-app N/A 영역 cross-repo inspect 의무 부재. 단 Tier-2 (consumer Story 영역) 가 marketplace.json `channels[]` consumer count proxy 측정 시 PAT 사용 가능 (ADR-066 audit log entry update 의무 — 5번째 consumer 명시).

**Cross-ref**: ADR-72 §결정 1-7 SSOT + ADR-055 Amendment 3 (Epic-level integration test baseline first activation) + ADR-076 §결정 9.4 (canary tier production-impact authority advisory) + `label-registry-v2` v2.33 (`production-touching` entry + `production-impact` category) + `docs/evidence-checks-registry.yaml` 2 entry (`production-cutover-deputy-spawn-evidence` + `epic-cutover-gate-evidence-quad-check`, warning tier) + `templates/github-workflows/production-cutover-evidence.yml` + `scripts/check-production-cutover-evidence.sh` + `docs/domain-knowledge/domain/production-cutover/` (4 industry exemplars empirical anchor: K8s / Chrome / AWS CodeDeploy / Helm rollback).

---

§2.1 ~ §2.7 = manual / advanced fallback (script 미작동 시 / 부분 customize 필요 시).

---

### 2.0a Optional Stage 0 — pre-Issue brainstorming (recommended for non-trivial Story)

복잡한 요구사항 (cross-cutting / 새 도메인 / 모호한 scope) 인 경우, Issue Form 제출 전 `superpowers:brainstorming` skill 로 scope 를 먼저 정리할 수 있습니다 ([ADR-034](../archive/adr/ADR-034-pre-issue-brainstorming-stage.md), [orchestrator-playbook §1.2.0](orchestrator-playbook.md)). 산출 spec 의 결론 요약을 Issue Form `user-original` 필드에, spec path 를 `spec_link` 필드에 입력하면 codeforge requirements lane 이 그 텍스트를 입력으로 받아 분석을 시작합니다. 작은 chore / 명료한 요구사항이면 생략 가능 — Stage 0 는 옵션입니다 (CI 강제 없음).

Spec 저장 위치:
- **Consumer project**: `docs/superpowers/specs/YYYY-MM-DD-<slug>-design.md` (skill default)
- **Plugin repo dogfood (codeforge family)**: `<internal-docs>/<plugin-folder>/specs/YYYY-MM-DD-cfp-NNN-<slug>-design.md` ([ADR-013](../archive/adr/ADR-013-codeforge-family-dogfood-out-policy.md) / [ADR-017](../archive/adr/ADR-017-skill-override-path-enforcement.md) enforced)

In-lane brainstorming (DomainAgent / RequirementsPL 가 lane 내부에서 호출) 과는 다른 단계 — [superpowers-integration.md §2](superpowers-integration.md) 참조.

#### 미초기화 (greenfield) consumer 의 첫 진입 — bootstrap-first 안내 (ADR-027 Amendment 10 / §결정 13, CFP-2243)

아직 codeforge 가 초기화되지 않은 프로젝트 (greenfield) 에서 사용자가 codeforge 사용을 선언(설계/brainstorm/스토리 요청)하면, codeforge 는 brainstorming 으로 바로 진행하기 **전에** 초기화가 필요함을 먼저 안내합니다. 여기서 **greenfield(미초기화) = 다음 4 가지 모두 부재** (detect-repo-kind truth-table 기준 단일 정의, ADR-027 §결정 13.B SSOT):

- `.claude-plugin/plugin.json` 부재 (plugin/mixed repo 아님 — 있으면 detect plugin(exit 0)/mixed(exit 2) → gate 침묵)
- `.claude/_overlay/project.yaml` 부재 (consumer 초기화 안 됨)
- `docs/adr/` 부재
- `archive/adr/` 부재

(앞 2 부재 = `detect-repo-kind` `unknown`(exit 3) 의 정확한 등가. 이 4 부재 정의는 wrapper 훅·`codeforge:brainstorm` skill 의 미초기화 판정과 byte-동일.) 안내 절차:

1. **미초기화 상태 surface** — wrapper plugin UserPromptSubmit 훅 (`hooks/bootstrap-first-gate`, 설치 즉시 활성) 이 정적 안내를 context 에 inject. 사용자 입력을 차단하지 않습니다 (warning only).
2. **초기화 권고** — `scripts/bootstrap-consumer.sh` 실행을 안내. **GitHub remote 가 없으면 자동으로 repo 를 만들지 않습니다** — `gh repo create` 명령과 필요 상태를 보여 주고 사용자 확인 후 진행합니다.
3. **초기화 없이 진행 선택 가능** — 사용자가 "초기화 없이 진행" 을 명시하면 그대로 brainstorming 으로 진행합니다 (Stage 0 옵션성 보존 — [ADR-034](../archive/adr/ADR-034-pre-issue-brainstorming-stage.md) D1).

이 안내는 brainstorm 진입 자체를 막지 않습니다. 초기화를 먼저 권고할 뿐입니다. 초기화 완료 consumer (project.yaml 존재) 에서는 발화하지 않습니다.

---

### 2.1 (manual fallback) 초기 복사

```bash
# consumer project root에서
mkdir -p .claude/_overlay/agents
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/_overlay/README.md .claude/_overlay/
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/_overlay/project.yaml.example .claude/_overlay/project.yaml

```

(§2a anchor 보존 — 외부 link 호환)

### 2.2 (manual fallback) `.claude/settings.json` 설정 — 3 hook 등록 (CFP-103 + CFP-104 + CFP-106 정합)

`templates/settings.json.example` 정합 NESTED schema. 3 hook 등록 의무 — SessionStart × 2 (regen-agents + check-bootstrap) + UserPromptSubmit × 1 (userprompt-reminder). FLAT schema (기존 §2b 잔존, CFP-125 fix 전) 는 invalid — Claude Code parser silent skip 가능성.

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/regen-agents.sh" }
        ]
      },
      {
        "hooks": [
          { "type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/check-bootstrap.sh" }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          { "type": "command", "command": "bash ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/userprompt-reminder.sh" }
        ]
      }
    ]
  }
}
```

**Windows variant** (PowerShell wrapper, `templates/settings.json.example` `_windows_note` 정합):

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "pwsh -File ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/regen-agents.ps1" }] },
      { "hooks": [{ "type": "command", "command": "pwsh -File ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/check-bootstrap.ps1" }] }
    ],
    "UserPromptSubmit": [
      { "hooks": [{ "type": "command", "command": "pwsh -File ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/userprompt-reminder.ps1" }] }
    ]
  }
}
```

**Hook 역할**:
- SessionStart `regen-agents.sh` (CFP-65) — overlay agents 자동 merge
- SessionStart `check-bootstrap.sh` (CFP-103) — 8 sub-check (workflow 권한 / label / plugin / consumer workflows / forms / CODEOWNERS)
- UserPromptSubmit `userprompt-reminder.sh` (CFP-104) — 변경 착수 prompt 검출 시 reminder inject

(§2b anchor 보존 — 외부 link 호환. CFP-125 Phase 2 PR 가 §2b FLAT → NESTED schema fix.)

### 2c. GitHub repo 셋업 (Plugin 권장 워크플로우 + Forms + CODEOWNERS)

```bash
# Workflow 7개 복사 (consumer-distributable):
#   phase-gate-mergeable + phase-label-invariant + story-init + story-section-1-immutable
#   + fix-ledger-sync + subissue-from-impl-manifest + story-section-schema (CFP-94)
mkdir -p .github/workflows
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/*.yml .github/workflows/

# CFP-97 + CFP-109 + CFP-110: consumer-distributable scripts manifest-driven copy.
# Manifest format: <script-path>[:<dependent-workflow-path>]
# (CFP-109 — workflow path optional, used by SessionStart Check 4 for degraded suppression).
#
# CFP-110: SessionStart hook (regen-agents.sh) 가 매 세션 시 자동 install (cp -n no-clobber)
# — 본 manual loop 는 fallback (hook 미작동 / 첫 install 전 / opt-out 시).
# Plugin update 시 신규 manifest entry 는 자동 propagate.
while IFS= read -r line; do
    # trim leading/trailing whitespace
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    case "$line" in '#'*|'') continue ;; esac
    # CFP-109: parse script-path before optional `:<workflow>` suffix
    script_path="${line%%:*}"
    # path traversal guard (CFP-97 P1 + CFP-112 leading-dash) — applied to script_path only
    case "$script_path" in
        /*) echo "manifest absolute-path entry rejected: $line" >&2; continue ;;
        *..*) echo "manifest traversal entry rejected: $line" >&2; continue ;;
        -*) echo "manifest leading-dash entry rejected: $line" >&2; continue ;;
    esac
    mkdir -p "$(dirname "$script_path")"
    cp "${CLAUDE_PLUGIN_ROOT}/codeforge/${script_path}" "${script_path}"
    chmod +x "${script_path}"
done < "${CLAUDE_PLUGIN_ROOT}/codeforge/templates/consumer-scripts.manifest"

# Issue Forms 5개 복사 (audit + bug + story + discussion + codeforge-improvement) + config.yml
# CFP-821 D1 fan-out: templates/.github/ISSUE_TEMPLATE/ SSOT (ADR-027 Amendment 5 §결정 9)
mkdir -p .github/ISSUE_TEMPLATE
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/.github/ISSUE_TEMPLATE/*.yml .github/ISSUE_TEMPLATE/

# PR template 복사
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-pr-template.md .github/PULL_REQUEST_TEMPLATE.md

# CODEOWNERS 복사 + team placeholder 치환
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/CODEOWNERS.template .github/CODEOWNERS
# editor에서 @ORG/ARCHITECT_TEAM, @ORG/DOMAIN_EXPERT_TEAM을 자기 organization team으로 치환
```

#### Path A (default — full distribution) vs Path B (degraded distribution) (CFP-86)

mctrader debut audit Issue [#181](https://github.com/mclayer/plugin-codeforge/issues/181) P1-6 finding: 위 7 workflow (CFP-94 후 — 6 → 7) 모두 복사가 default 이나 (Path A), 실제 mctrader-hub 는 **2 workflow 만 보유 (Path B)**. SSOT 미문서화 → invariant 보장 기대치 mismatch.

**Path A (full)**: 7 workflow 모두 보유 — 모든 invariant 자동 enforce.
**Path B (degraded)**: 일부 workflow 부재 — manual compensating check 의무.

##### Workflow 별 invariant 영향

| Workflow | 부재 시 lost invariant | Manual compensating check (Path B) |
|---|---|---|
| `story-init.yml` | Issue Form → Story file + Phase 1 PR 자동 생성 | `gh issue create` 수동 + `docs/stories/<KEY>.md` 수동 작성 + Phase 1 PR 수동 open |
| `phase-label-invariant.yml` | single-active phase label enforce | PR review 시 phase label 1개만 boolean check (script 또는 manual) |
| `phase-gate-mergeable.yml` | phase gate ↔ PR mergeable status | PR merge 직전 phase 라벨 + gate 라벨 manual verify |
| `story-section-1-immutable.yml` | §1 변조 금지 | PR diff 의 `## §1` line range manual review |
| `fix-ledger-sync.yml` | §10 row append → Issue label mirror + comment | §10 row 추가 commit 시 수동 `[FIX #N]` Issue comment + `fix:<lane>-retry` label 부착 |
| `subissue-from-impl-manifest.yml` | §8.5 Impl Manifest → file-level sub-issue 자동 생성 | §8.5 commit 후 수동 `gh sub-issue create` per file |
| `story-section-schema.yml` (CFP-94) | Story file §1-§13 schema lint (Implementation strict + Epic condensed) | PR review 시 수동 section schema 검증 또는 `bash scripts/check-story-section-schema.sh` 로컬 실행 (CFP-97 manifest 경유 copy) |

**mctrader-hub 현재 상태 (2026-05-04 audit)**:
- ✅ `phase-gate-mergeable.yml`
- ✅ `phase-label-invariant.yml`
- ❌ 4 workflow 부재 (Path B 운영 중) — 수동 compensating check 가 자율적

##### Path A ↔ Path B cutover 절차

**Path A → Path B (degrade)**:
1. 부재할 workflow yml 명시 (PR description 에 reason)
2. 본 §2c 표 의 manual compensating check 활성화
3. consumer overlay `.claude/_overlay/project.yaml` 의 `workflow_distribution: full | degraded` field 갱신 (CFP-86 Phase 2 — 별도 follow-up CFP)

**Path B → Path A (upgrade)**:
1. `cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/<missing>.yml .github/workflows/`
2. (CFP-97) `<missing>.yml` 가 의존 script 보유 시 (예: `story-section-schema.yml` ↔ `scripts/check-story-section-schema.sh`) §2c manifest-driven loop 동시 실행
3. CI 가 신규 invariant 발견 시 backlog Story 로 변환 (예: 누락된 §10 row → Story 작성)
4. `workflow_distribution` field = `full`

##### git history audit signal

mctrader-hub git log 에 `chore: codeforge consumer setup (Path B — degraded distribution)` commit 존재 (2026-04-25 시점). 본 CFP-86 = ex post SSOT 화 — 이미 emerge 한 패턴 명시.

### 2d. GitHub Labels 생성 (gh CLI 일괄)

> **CFP-12 자동화** (권장 — consumer 1 repo): `bash scripts/bootstrap-labels.sh [<org>/<repo>]` — 아래 18 label을 idempotent로 일괄 생성. SessionStart hook의 `check-bootstrap.sh`가 부재 시 자동 안내.

> **CFP-120 (codeforge family setup)**: codeforge family 7 repo (wrapper + 6 lane) 모두 label 부트스트랩 = `bash scripts/bootstrap-codeforge-family.sh [--org <org>]` (default org: `mclayer`). lane plugin contributor 가 처음 setup 할 때 의무. label 부재 시 cross-repo Story binding PR 의 phase + gate label apply 가 `'phase:설계-리뷰' not found` 로 실패.

수동 명령으로 진행하려면:

```bash
ORG_REPO="<your-org>/<your-repo>"

# Type labels
gh label create "type:epic" --color "3E4B9E" --repo "$ORG_REPO"
gh label create "type:story" --color "0E8A16" --repo "$ORG_REPO"
gh label create "type:bug" --color "D73A4A" --repo "$ORG_REPO"
gh label create "type:audit" --color "FBCA04" --repo "$ORG_REPO"
gh label create "impl-manifest" --color "C2E0C6" --repo "$ORG_REPO"

# Phase labels (single-active, phase-label-invariant.yml Action이 강제)
for phase in "요구사항" "설계" "설계-리뷰" "구현" "구현-리뷰" "구현-테스트" "보안-테스트"; do
  gh label create "phase:$phase" --color "FEF2C0" --repo "$ORG_REPO"
done

# Gate labels (review pass)
gh label create "gate:design-review-pass" --color "C2E0C6" --repo "$ORG_REPO"
gh label create "gate:security-test-pass" --color "C2E0C6" --repo "$ORG_REPO"

# Fix labels (cumulative)
for lane in "설계-리뷰" "구현-리뷰" "구현-테스트" "보안-테스트"; do
  gh label create "fix:${lane}-retry" --color "F9D0C4" --repo "$ORG_REPO"
done

# Hotfix / audit
gh label create "hotfix:minimal" --color "FF5722" --repo "$ORG_REPO"
gh label create "hotfix:critical" --color "B71C1C" --repo "$ORG_REPO"
gh label create "audit:post-hotfix" --color "FBCA04" --repo "$ORG_REPO"
```

### 2e. Branch protection (main)

#### 다인 contributor 팀 (default — review gate 강제)

```bash
gh api -X PUT repos/$ORG_REPO/branches/main/protection \
  -F required_status_checks='{"strict":true,"contexts":["phase-gate-mergeable"]}' \
  -F required_pull_request_reviews='{"required_approving_review_count":1,"require_code_owner_reviews":true}' \
  -F enforce_admins=false \
  -F restrictions=null
```

#### 단일 author / 1-2인 팀 (solo-dev 권장)

단일 author 가 sole CODEOWNER 이면 GitHub 정책 (`Cannot approve your own pull request`) 으로 self-approve 불가능 → 모든 PR 영구 deadlock. 다음 완화 분기 권장:

```bash
gh api -X PUT repos/$ORG_REPO/branches/main/protection \
  -F required_status_checks='{"strict":true,"contexts":["phase-gate-mergeable"]}' \
  -F required_pull_request_reviews='{"required_approving_review_count":0,"require_code_owner_reviews":false}' \
  -F enforce_admins=false \
  -F restrictions=null
```

`phase-gate-mergeable` status check 는 그대로 강제 — review-gate 만 완화. 팀 합류 시 위 다인 모드로 전환.

#### 이미 deadlock 상태인 경우 (workaround — standard flow 아님)

`enforce_admins=false` + repo admin 권한 보유자가 admin override:

```bash
gh pr merge --admin --squash <PR-number>
```

본 명령은 **escape-hatch** 이며 정상 flow 가 아님. solo-dev 모드 시 위 권장 분기 적용 후 일반 `gh pr merge --squash` 사용.

#### Branch protection 활성화 시 worktree lifecycle

`phase-gate-mergeable` + PR required check 활성화 시 Story root worktree 정리 순서:

```
git push → PR 생성 → gh pr view <N> --json mergedAt (non-null 확인) → git worktree remove
```

- **pre-merge cleanup 금지**: Phase 2 PR merge 확인 전 `git worktree remove` 실행 = policy violation (ADR-040 Amendment 2).
- **merge 확인 명령**: `gh pr view <PR_NUMBER> --json mergedAt --jq .mergedAt` → non-null 이면 merge 완료.
- **protection 감지**: `gh api "repos/$(gh repo view --json nameWithOwner --jq .nameWithOwner)/branches/main" --jq '.protected'` — `true` 면 직접 merge 금지, PR-only.
- solo-dev (`required_approving_review_count:0`) + `enforce_admins=false` 환경에서도 동일 순서 적용. `phase-gate-mergeable` check 통과 후 자동 merge 가능하나, worktree 정리는 항상 `mergedAt` 확인 후.

#### Branch protection manifest drift 확인 + operator 적용 절차 (CFP-821 D2)

CFP-821 Phase 2 이후 `templates/scripts/setup-branch-protection.sh` (FORM (b) dry-run helper)를 사용해 drift를 확인할 수 있다.

**사용법** (manifest dry-run preview — GitHub API write 0):

```bash
# Wrapper SSOT manifest + 현재 API state 비교 (read-only GET만 수행)
bash templates/scripts/setup-branch-protection.sh --dry-run

# 합성 manifest 파일로 출력 (operator 검토용)
bash templates/scripts/setup-branch-protection.sh --manifest-out /tmp/bp-manifest.yaml
```

**종료 코드**: 0 = no drift / 2 = drift detected (informational, CI fail 아님) / 1 = error

**실제 branch protection 등록 (operator manual — Administration:write 권한 필요)**:

```bash
# ADR-024 Amendment 2 §결정 C step 2: consumer admin operator가 수동 적용
gh api -X PUT repos/$ORG_REPO/branches/main/protection \
  -F required_status_checks='{"strict":true,"contexts":["phase-gate-mergeable","invariant-check","doc frontmatter schema (CFP-28 — strict)","doc section schema (CFP-28 — strict)"]}' \
  -F required_pull_request_reviews='{"required_approving_review_count":0,"require_code_owner_reviews":false}' \
  -F enforce_admins=true \
  -F restrictions=null
```

> **FORM (b) constraint**: `setup-branch-protection.sh` 자체는 API write를 수행하지 않는다 (Administration:write credential 불요). 실제 등록은 consumer org admin의 기존 권한으로 수행한다. drift-check.yml (weekly cron)이 망각한 경우를 재감지하는 safety net 역할을 한다. [ADR-066 §결정 2 무변경 — F-P1-A 해소]

#### phase-gate-mergeable label mapping (CFP-479)

`phase-gate-mergeable.yml` Action 이 적용하는 phase × gate 매핑은 codeforge wrapper 의 정식 SSOT — consumer 도 동일 invariant 적용. 정식 표 SSOT = [`docs/orchestrator-playbook.md` §9.7](https://github.com/mclayer/plugin-codeforge/blob/main/docs/orchestrator-playbook.md) (wrapper repo). 본 단락은 consumer 운영 시 자주 마주치는 anomaly mirror.

**핵심 anomaly (CFP-342 fix)**:

- `phase:구현` / `phase:구현-리뷰` (Phase 2 PR) 에서 **`gate:design-review-pass`** 요구 — 직관적으로 기대되는 `gate:code-review-pass` 가 아님.
- 이유: codeforge 는 별도 `gate:code-review-pass` label 미도입. 구현 리뷰 PASS = phase progression only (gate label 무부착). 설계 리뷰 gate label 가 Phase 1 → Phase 2 전 구간 단일 mergeable 게이트 역할 수행.
- CFP-342 verbatim: "Phase 2 PR 도 gate:design-review-pass 요구 — gate:code-review-pass 가 아닌" (workflow yml `templates/github-workflows/phase-gate-mergeable.yml` line 199-202 inline comment).

**전체 매핑 표** (workflow yml line 195-208 verbatim 기반):

| Phase label (PR 부착) | Required gate label | 근거 (CFP) |
|---|---|---|
| `phase:설계` / `phase:설계-리뷰` | `gate:design-review-pass` | CFP-113 |
| `phase:구현` / `phase:구현-리뷰` | **`gate:design-review-pass`** (anomaly) | CFP-342 |
| `phase:구현-테스트` | (gate 무, CI inline polling) | CFP-317 / ADR-048 |
| `phase:보안-테스트` | `gate:security-test-pass` | (`lanes.security_ai: true` opt-in 시에만) |
| (Story binding 부재) | `gate:design-review-pass` (legacy heuristic) | workflow line 207 |

Live touching Story 의 보안-테스트 phase 는 추가로 `gate:live-entry-pass` 요구 (ADR-030). Consumer 가 phase / gate label taxonomy 를 변경하지 않는 한 본 매핑은 그대로 적용.

**CFP-1302 추가**: phase 전환 시 prior gate label 자동 cleanup 은 별 workflow `phase-gate-auto-cleanup.yml` (SRP 분리) 가 담당. multi-gate `required` shape = `{phase, gates: string[]}` array (semantic 변경 0, syntactic 강화). `hotfix-bypass:auto-cleanup-stale-gate` label 부착 시 auto-cleanup skip (consumer 영역에서 manual decision 의무 시 사용). 정식 SSOT = playbook §9.7.

### 2f. 보안 보강 활성화 (consumer settings)

GitHub repo settings 또는 gh api로:
- **Dependabot alerts** + **Dependabot security updates** (자동 PR)
- **CodeQL** (default setup 권장)
- **Secret Scanning** + **Push Protection**

이는 SecurityTestPL의 1차 layer로 활용된다.

### 2g. Workflow permissions (org-level) — **반드시 설정**

**`story-init.yml` workflow 가 Phase 1 PR 을 자동 open 하므로 GitHub Actions 에 PR 생성 권한 필요**. CFP-11 end-to-end 실증에서 발견된 bootstrap drift — org admin 권한 필요 (1회 설정).

> **CFP-65 F2 Phase 1 복원**: CFP-45 가 `story-init.yml` 을 internal-docs 로 이동한 후 CFP-65 가 single-repo flavor 로 plugin templates 에 복귀. consumer 첫 사용 시 본 설정 1회 활성화 필수.

**Web UI**:
1. https://github.com/organizations/`<your-org>`/settings/actions
2. **Workflow permissions** → "Read and write permissions" 선택
3. **"Allow GitHub Actions to create and approve pull requests"** 체크
4. Save

**CLI** (admin:org scope 필요, `gh auth refresh -h github.com -s admin:org` 후):

```bash
gh api -X PUT orgs/<your-org>/actions/permissions/workflow \
  -f default_workflow_permissions=write \
  -F can_approve_pull_request_reviews=true
```

미설정 시: `story-init.yml` 의 `Create Phase 1 PR` step 이 다음 에러로 fail:
```
GitHub Actions is not permitted to create or approve pull requests (createPullRequest)
```
(branch + docs file 은 commit·push 되지만 PR auto-open 실패. 수동 `gh pr create` 로 복구 가능하나 자동화 가치 손실)

> **§1 invariant 자동 강제**: CFP-67 (F2 Phase 2 split 1/2) 후 `story-section-1-immutable.yml` 자동 강제. §1 변경 PR 시 자동 reject — 정당한 정정은 PR 제목 `[bypass-section-1]` + CODEOWNERS architect team approval 절차 (§7 Q7 참조).

> **자연어 upgrade 발화 진입점 (CFP-1104 / [ADR-071 Amendment 5](../archive/adr/ADR-071-orchestrator-user-dialog-convergence.md) §결정 16)**: consumer 가 자연어로 `codeforge upgrade` (또는 한글 `codeforge 업그레이드`) 발화 시 Orchestrator 가 [orchestrator-playbook §3.16.1](orchestrator-playbook.md) per 자동 실행 — cwd 자동 주입 + overlay channel resolve + dry-run → apply 자동 reflex, 사용자 확인 분기 0 (ADR-076 invariant `user_decision_branches: 0` dialog 단계 enforcement).

### 2h. `.gitignore`에 추가

```gitignore
# codeforge plugin — generated files
.claude/agents/
.claude-work/
CLAUDE.md    # core+overlay merge 결과면 gitignore. 수동 커밋 원하면 제외.
```

### 2i. Strict mode opt-in (CFP-127 / ADR-032 amendment 1) — RECOMMENDED for mctrader 6-repo

기본 동작 (default): `check_bootstrap.py` 가 drift 발견 시 stderr 경고만 출력, exit 0 (ADR-027 §결정 2 Tertiary trigger LLM-trust 정합). 신규 consumer 가 lane orchestration 진입 가능하지만 enforcement layer 가 silent 로 누락될 위험.

**Strict mode opt-in**: `bootstrap.strict_mode: true` (project.yaml) 활성 시 adoption-critical drift 4종 발견 → exit 1 + Orchestrator 사용자 escalation. mctrader 6-repo first opt-in target 권장.

#### 2i-1. 점진 도입 4 단계 (Cold-start 회피)

신규 strict opt-in 시 4종 drift 동시 발견 시 escalation flood 회피하기 위한 **점진 단계** (각 단계별 PASS 확인 후 다음 진행):

```bash
# 단계 1: Plugin install (8 critical = wrapper + 6 lane + superpowers)
/plugins install codeforge@<marketplace>
/plugins install codeforge-requirements@<marketplace>
# ... 6 lane plugin 모두
/plugins install superpowers@claude-plugins-official

# 단계 1 verify:
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-debut-readiness.sh
# Check 2 PASS 확인

# 단계 2: settings.json hook 등록 (3 hook = SessionStart × 2 + UserPromptSubmit × 1)
# §2.2 (또는 §2b legacy) 의 NESTED schema 정합 cp:
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/settings.json.example .claude/settings.json
# 단계 2 verify:
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-debut-readiness.sh
# Check 4 PASS 확인

# 단계 3: project.yaml 작성 + validation
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/_overlay/project.yaml.example .claude/_overlay/project.yaml
# editor 에서 <REPLACE> 값 치환
python3 ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/validate_config.py .claude/_overlay/project.yaml
# 단계 3 verify:
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-debut-readiness.sh
# Check 1 + 3 PASS 확인

# 단계 4: labels bootstrap (10 critical = phase:* 7 + gate:* 3)
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/bootstrap-labels.sh <org>/<repo>
# 단계 4 verify:
bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-debut-readiness.sh
# 모든 4 check PASS 확인

# 단계 5: strict_mode opt-in 활성
# .claude/_overlay/project.yaml 에 추가:
#   bootstrap:
#     strict_mode: true
git add .claude/_overlay/project.yaml
git commit -m "chore: opt-in bootstrap.strict_mode (CFP-127 / ADR-032)"
```

#### 2i-2. 3 mechanism + 우선순위 (CLI > env > yaml)

| Priority | Mechanism | 명령 | 적용 범위 |
|---|---|---|---|
| 1 (highest) | CLI flag | `bash check-bootstrap.sh --strict` / `python check_bootstrap.py --strict` | per-invocation |
| 2 | Env | `CODEFORGE_STRICT_BOOTSTRAP=1` | shell session |
| 3 (lowest) | YAML | `bootstrap.strict_mode: true` (project.yaml) | persistent project-level |

"Most explicit wins" — CLI flag set 시 env / yaml 무시.

#### 2i-3. Strict-eligible drift 5종 (CFP-660 4 → 5 확장)

| # | Drift | Detection |
|---|---|---|
| (a) | `.claude/_overlay/project.yaml` 부재 | file presence |
| (b) | plugin 8 critical (wrapper + 6 lane + superpowers) 미설치 | `~/.claude/plugins/installed_plugins.json` parse |
| (c) | `.claude/settings.json` 의 SessionStart × 2 + UserPromptSubmit × 1 hook 미등록 | json hooks parse + command grep |
| (d) | phase:* (7) + gate:* (3) = 10 critical label 부재 | `gh label list` |
| **(e)** | **consumer `.github/workflows/*.yml` SHA / 핵심 line drift vs wrapper templates (CFP-660 / ADR-032 amendment 2)** | **`check_workflow_version_drift` (check 10) — Tier 1 SHA-256 + Tier 2 core marker (concurrency / on / permissions)** |

(e) STRICT_ELIGIBLE_WORKFLOWS 영역 (7 file): `phase-gate-mergeable.yml` / `phase-label-invariant.yml` / `story-init.yml` / `story-section-1-immutable.yml` / `subissue-from-impl-manifest.yml` / `fix-ledger-sync.yml` / `story-section-schema.yml`. lane orchestration semantics 영향 직접인 file 만.

Non-eligible (warning-only 유지): workflow permissions / consumer-scripts manifest drift / consumer .github/workflows/ file (Path B degraded 정합) / Issue forms / CODEOWNERS / 기타 advisory.

##### (e) Drift 복구 절차 (sweep)

drift 발견 시 즉시 sweep cp:

```bash
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/*.yml .github/workflows/
git add .github/workflows/
git commit -m "chore: sync .github/workflows from wrapper templates (CFP-660 drift recovery)"
```

또는 strict mode 임시 비활성 (revert 표 참조). 또는 **per-Issue bypass**: `hotfix-bypass:workflow-version-drift` label 부착 (audit-trailed channel, ADR-024 Amendment 3 §결정 6.A).

`scripts/sync-consumer-workflows.sh` sweep helper = **별 CFP carrier** (issue #467 sibling 후보, 본 Story scope 외 — single-Story 영역 보존).

#### 2i-4. Revert procedure

False-positive 발생 또는 strict mode 비활성 필요 시:

| Mechanism | Disable 명령 |
|---|---|
| CLI flag | flag 미사용 (next invocation) |
| Env | `unset CODEFORGE_STRICT_BOOTSTRAP` |
| YAML | `bootstrap.strict_mode: false` 또는 field 삭제 + commit |

#### 2i-5. ADR-027 §결정 3 Bypass 와 동시 작동

`HOTFIX_BYPASS_CODEFORGE=1 + HOTFIX_BYPASS_REASON="<reason>"` 양 env set → strict mode 활성 무관 hook self skip. Bypass priority HIGHEST.

emergency hotfix / lane invariant override 시 사용. `docs/hotfix-playbook.md` 사유 등재 의무 + post-bypass audit Issue 자동 생성.

## 3. Overlay 작성

### 3a. `.claude/_overlay/project.yaml` — objective SSOT 상수

GitHub 좌표·CODEOWNERS·Discussions·Milestone·labels 등 structured 상수를 작성. Schema 전체 명세: [`project-config-schema.md`](project-config-schema.md).

```yaml
project:
  name: <your-project>

github:
  org: <your-org>
  repo: <your-repo>
  default_branch: main
  pr_title_prefix_template: "[{key}] {title}"
  story_key_prefix: <PREFIX>      # e.g. TM
  codeowners:
    architect_team: "@<your-org>/architects"
    domain_expert_team: "@<your-org>/domain-experts"
  discussions:
    domain_kb_category: "Domain Q&A"
  milestone:
    epic_naming_pattern: "Epic-{key}-{slug}"

labels:
  components:
    - <component-1>   # e.g. api
    - <component-2>   # e.g. ui

progress_narration_verbosity: full  # full | lane_only
```

`progress_narration_verbosity` 는 phase 진행 narration 출력량을 조절한다. 기본값 `full` 은 ADR-029 기준 sub-step narration 까지 출력하는 opt-in 기본 동작이고, consumer 가 더 조용한 CFP-20 기존 동작을 원하면 `lane_only` 로 opt-out 하여 lane boundary event 만 출력한다.

주 소비자: RequirementsPLAgent · DomainAgent · PMOAgent · ArchitectPLAgent 및 각 lane plugin. 에이전트는 이 파일을 `Read`로 직접 참조.

SessionStart hook이 자동으로 `validate_config.py`를 실행해 schema 준수를 검증. 위반 시 hook abort. 수동 검증:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/validate_config.py \
    .claude/_overlay/project.yaml
```

### 3a-multi-repo. Multi-repo story key system 활성화 (선택, CFP-342 / [ADR-069](../archive/adr/ADR-069-multi-repo-story-key-system.md))

> **Opt-in only** — single-repo consumer 또는 기존 multi-repo hub-flat 운영 (예: mctrader MCT-1~111 cluster) 은 본 섹션 skip 가능. 부재 시 single-repo flat 모드 유지 (기존 동작 보존).

#### 적용 시나리오

Multi-repo consumer (1 governance hub repo + N implementation repo) 가 ADR-020 Mode B (hub-centralized) 패턴을 사용하면서 다음 페인 포인트 해소를 원할 때:

1. **가독성 손상**: hub flat key 만으로 어느 impl repo 작업인지 식별 불가 (예: `MCT-107` 만 보면 어느 repo?)
2. **Locality 위반**: impl repo 구현 상세가 hub 에 cluster — 작업 히스토리가 코드와 분리

본 시스템 활성화 시 hub story (governance) + repo story (impl) 분리 + counter 자동 발급 + bidirectional linking.

#### 활성화 절차

**Step 1**: hub repo 의 `.claude/_overlay/project.yaml` 에 `codeforge.stories` 블록 추가:

```yaml
# CFP-342 / ADR-069 — Multi-repo story key system
codeforge:
  stories:
    hub:
      key_pattern: "{prefix}-{seq:03d}"
      story_dir: docs/stories
      template: hub-story.md
    repo_key_pattern: "{prefix}-{seq:03d}"
    counters:
      path: .codeforge/counters.json
      lock: file
    repos:
      - name: <hub-repo>
        role: governance
        story_dir: docs/stories
        creates_repo_stories: false
      - name: <impl-repo-1>
        role: implementation
        path: <local-absolute-path>
        github: <owner>/<impl-repo-1>
        story_dir: docs/stories
        components: [<comp1>, <comp2>]
      - name: <impl-repo-2>
        role: implementation
        path: <local-absolute-path>
        github: <owner>/<impl-repo-2>
        story_dir: docs/stories
        components: [<comp3>]
```

**Step 2**: `.codeforge/counters.json` 신규 생성 (hub repo root, committed):

```json
{
  "version": 1,
  "prefix": "<your-prefix>",
  "counters": {
    "<hub-repo>":   { "next": <existing-max + 1> },
    "<impl-repo-1>": { "next": 1 },
    "<impl-repo-2>": { "next": 1 }
  },
  "reservations": {}
}
```

**Step 3**: `validate_config.py` schema check 통과 확인:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/codeforge/overlay/hooks/validate_config.py \
    .claude/_overlay/project.yaml
```

#### Story 작성 시 영향

**Hub story** (cross-repo 조율):
- 위치: `<hub-repo>/docs/stories/<KEY>.md`
- Frontmatter: `story_scope: hub` + `delegates: []`
- 본문: `templates/hub-story.md` (Background / Direction / Delegation / Acceptance Gates / Links)

**Repo story** (단일 impl repo 구현):
- 위치: `<impl-repo>/docs/stories/<KEY>.md`
- Frontmatter: `story_scope: repo` + `repo: <impl-repo>` + `hub_story: <HUB-KEY> | null` + `hub_repo: <hub-repo> | null`
- 본문: `templates/repo-story.md` (Background / Implementation Scope / Technical Design / AC / Test Plan / Links)

**Cross-repo 참조**: `{repo-name}#{KEY}` GitHub 스타일 (예: `mctrader-data#MCT-001`).

#### Backward compat — 기존 legacy story

기존 hub flat story (예: mctrader MCT-1 ~ MCT-111) 는 변경 0:
- **Rename / move 절대 금지**
- `story_scope` frontmatter 자동 추가 X — touched 시 author manual 옵트인
- Agent 가 frontmatter 부재 detect → `legacy-hub` 묵시 처리 (= hub repo 작업)

#### Mode B 자동화 정합

본 시스템 = ADR-020 Amendment 1 §결정 8 Mode B (hub-centralized) 의 **automation backbone**. Mode B 를 manual 운영하던 consumer 는 본 시스템 활성화로 file 위치 결정 / counter 발급 / bidirectional linking 자동화 가능. Mode A (repo-local) consumer 도 `codeforge.stories.repos[].role: implementation` + `creates_repo_stories: true` 로 활용 가능.

상세 SSOT: [ADR-069](../archive/adr/ADR-069-multi-repo-story-key-system.md), [ADR-020](../archive/adr/ADR-020-cross-repo-epic-pattern.md) Amendment 3.

> **Phase 2 mechanism (별도 follow-up CFP)**: counter 자동 발급 / Story 자동 라우팅 / agent target repo 결정 자동화는 별도 CFP scope. Phase 1 (본 schema land 후) 는 manual 운영 (consumer 가 직접 counter 갱신 + file 작성).

### 3b. `.claude/_overlay/CLAUDE.md` 예시 (narrative 컨텍스트)

CLAUDE.md overlay에는 **서술 컨텍스트만** (도메인 소개·기술 스택 선택 근거·경로 관습 설명). Objective 상수는 project.yaml에 있음.

```markdown
## Project

`<your-project>` — <한 줄 프로젝트 설명>. <기술 스택> 기반.

SSOT 상수는 `.claude/_overlay/project.yaml` 참조.

## Domain

<프로젝트 도메인 한 줄 서술>

## 기술 스택 (선택 근거)

- 언어: <선택 이유 포함>
- 저장소: <선택 이유>
- 배포: <선택 이유>

## 경로 관습

- `src/<your-domain>/...` — 도메인 로직
- `src/adapters/...` — 외부 시스템 어댑터
- 기타 프로젝트 관습
```

### 3c. Preset 임포트 (선택)

프로젝트 shape이 플러그인 preset과 맞으면 preset agents를 overlay로 복사.

```bash
cp -r ${CLAUDE_PLUGIN_ROOT}/codeforge/presets/webapp/agents/*.md \
      .claude/_overlay/agents/
```

상세는 [`plugins/codeforge-develop/presets/README.md`](../plugins/codeforge-develop/presets/README.md) 참조.

### 3d. `.claude/_overlay/agents/<Name>.md` 예시

프로젝트 특화 정보가 필요한 에이전트만 overlay 작성. 대부분 에이전트는 core만으로 충분.

#### `.claude/_overlay/agents/DomainAgent.md`

```markdown
### 도메인 소스

- Domain Knowledge: `docs/domain-knowledge/<your-area>/...`
- ADR 카테고리 (frontmatter `category:`): `<project-domain-category>`
- 도메인 코드 경로: `src/<your-project>/domain/**`
- 도메인 용어: <용어1>, <용어2>, <용어3>

### 우선순위 원칙
- <예: 지연 민감 / 데이터 일관성 / 보안 / 장애 복구 등>
```

### 3z. Docker-first Infra 채택 (CFP-128 / ADR-033)

framework default = Docker-first ([ADR-033](../archive/adr/ADR-033-docker-first-infra-engineering.md)). InfraEngineerAgent 가 Story 의 §5 변경 계획 에 따라 다음 산출물 생성:

- `Dockerfile` (multi-stage build — deps / builder / runner 분리)
- `compose.yml` (service definition + healthcheck + volume + network)
- `.dockerignore` (build context 축소)

#### 3z.1 `infra_strategy` override (project.yaml)

3 enum value 중 1개 선택 (default = `docker_first`):

```yaml
# .claude/_overlay/project.yaml
infra_strategy: docker_first  # default — Dockerfile + compose + .dockerignore
# infra_strategy: legacy_systemd  # legacy systemd unit / launchd plist (deprecated, opt-in only)
# infra_strategy: none            # library / config-only repo (Docker artifact 미적용)

infra_strategy_extras:
  k8s_preset_enabled: false     # presets/k8s/ activate 여부 (codeforge-develop)
```

scripts/check-container-strategy.sh 가 lint:
- `docker_first` 채택 + Dockerfile / compose.yml 부재 → exit 1
- `legacy_systemd` / `none` → skip

#### 3z.2 K8s preset opt-in

production K8s 환경 사용 시 `k8s_preset_enabled: true` + 다음 절차:

```bash
# K8s manifest skeleton 적용 (codeforge-develop presets/k8s/ 에서 templates 참조)
cp ${CLAUDE_PLUGIN_ROOT}/codeforge-develop/presets/k8s/*.yaml.template k8s/
# 각 template 의 placeholder ({app_name} / {namespace} / {image_ref}) 치환
```

Single-host docker compose 환경 = K8s preset 비활성 (`false`, default). 90% consumer 에 적합.

#### 3z.3 container-image-scan workflow 호출

본 plugin 의 `templates/github-workflows/container-image-scan.yml` reusable workflow 를 consumer build pipeline 에서 호출:

```yaml
# .github/workflows/build.yml (consumer 측)
jobs:
  build-image:
    # ... build + push to registry ...
    outputs:
      image-ref: ${{ steps.push.outputs.image-ref }}
  scan:
    needs: build-image
    uses: ./.github/workflows/container-image-scan.yml
    with:
      image-ref: ${{ needs.build-image.outputs.image-ref }}
      severity: "CRITICAL,HIGH"
      ignore-unfixed: true
```

trivy + hadolint 자동 실행. SecurityTestPL 1st-layer 의 일부 (CFP-128 / ADR-033 §결정 4).

#### 3z.4 기존 consumer follow-on Epic 패턴

ADR-033 effective date (Phase 2 wrapper PR merge) 이전 Phase 1 PR open 된 Story = grandfather (legacy 산출물 유지). retroactive 강제 없음. 컨테이너화 코드 작업 = **별도 Epic** (consumer 워크스페이스에서 수행, ADR-020 Mode B hub-centralized 권장 — mctrader 패턴):

1. Epic Issue (consumer hub repo) — 컨테이너화 scope + child Story decomposition (per repo)
2. 각 child Story 가 자체 Phase 1 + Phase 2 PR 시퀀스
3. Epic close PR (`EPIC-RESULTS-<KEY>.md` artifact)

mctrader 5 repo (Tier B-extended) = 첫 follow-on Epic 후보 (CFP-128 spec §3.4.1 / Story §11 회고 pointer).

#### 3z.5 통합테스트 환경 설정 (CFP-367 / ADR-055)

IntegrationTestAgent (CI gate 이후 lane 6) 가 동적 통합테스트를 실행하려면 **`docker-compose.test.yml`** 이 레포 루트에 있어야 한다.

**빠른 시작**:

```bash
cp ${CLAUDE_PLUGIN_ROOT}/codeforge-develop/presets/docker-compose.test.yml .
```

그 후 프로젝트 스택에 맞게 수정:
- `app` service: 실제 Dockerfile로 교체
- `test-db`: DB 엔진·포트 수정
- `wiremock`: 외부 API 없으면 제거

**CI workflow**: `templates/github-workflows/test.yml` 을 consumer `.github/workflows/test.yml` 로 복사 후 runner/path 수정. unit-tests (항상 실행) + integration-tests (docker-compose.test.yml 존재 시 실행, 없으면 warning + skip) 2 job 구성.

**§8.6 Integration Test Contract**: Story 에 컴포넌트 경계가 2개 이상 있으면 `docs/stories/<KEY>.md §8.6` 이 **필수**:

```yaml
### §8.6 Integration Test Contract
boundary_type: component_internal | multi_service | both
coverage_targets:
  - scenario: "경계 동작 검증"
    given: "유효한 요청이 들어올 때"
    when: "서비스 경계를 넘어 호출되면"
    then: "DB 기록 + 후속 이벤트 발행"
environment_dependencies:
  db: "PostgreSQL test DB seed"
  external_api: "외부 REST API WireMock stub"
  services: ["app", "test-db", "wiremock"]
isolation_strategy: ephemeral container
dynamic_test_required: true
```

면제 Story: `N/A — 단일 모듈 내부 로직만 변경` 형식으로 명시.

**통합테스트 누적 구조**:

```
tests/integration/
├── conftest.py              # 공통 fixture (누적 append 허용)
├── CFP-100/
│   └── test_order_boundary.py
├── CFP-101/
│   └── test_market_feed.py
...
```

각 Story마다 `tests/integration/<story-key>/` 디렉터리 아래 테스트 추가. IntegrationTestAgent 가 매 Story마다 전체 suite 실행 (regression 검증). 정책 SSOT: [ADR-055](../archive/adr/ADR-055-integration-test-lane-policy.md).

## 4. 첫 실행 검증

### 4a. Claude Code 세션 시작

프로젝트 디렉토리에서 `claude` 실행. SessionStart hook이 자동으로 `.claude/agents/*.md`와 `CLAUDE.md` 생성.

### 4b. 의존성 점검

세션 개시 즉시 Orchestrator가 의존성 체크 결과 출력. 6개 워크플로우·3개 Forms·CODEOWNERS 부재 시 알림.

### 4c. 첫 Story 생성

GitHub UI 에서 Issue 생성 → "Story" 템플릿 선택 → 사용자 요구사항 입력 → 제출.

`story-init.yml` Action 이 자동 (CFP-65 F2 Phase 1 — single-repo flavor):

1. project.yaml `github.story_key_prefix` fetch
2. 다음 KEY 번호 계산 (`docs/stories/<PREFIX>-N.md` 스캔)
3. `docs/stories/<KEY>.md` 생성 (§1=verbatim 입력, §2-11=placeholder)
4. Phase 1 PR 자동 open (architect team CODEOWNERS auto-review)
5. Issue body 를 docs file 링크로 갱신
6. (optional) Epic Milestone / Component label 부착

이후 Claude Code 세션을 재시작하거나 prompt 에 "Story `<KEY>` 진행" 이라고 입력하면 Orchestrator 가 활성 Story 를 감지해 RequirementsPLAgent 스폰.

> **F2 Phase 2 split 종료** (CFP-68): §1 변경 차단 (`story-section-1-immutable.yml` — CFP-67) ✅ + FIX Ledger label sync (`fix-ledger-sync.yml` — CFP-67) ✅ + Impl Manifest 자동 sub-issue + GraphQL addSubIssue (`subissue-from-impl-manifest.yml` — CFP-68) ✅. F2 (#116) Phase 2 모든 caveat 해소.

## 5. Workflow

Consumer 프로젝트에서 요구사항을 GitHub Issue Form으로 입력하면 플러그인이 0 core (wrapper-only) + distributed agent (8 lane plugin) + `role: dev` 동적 roster · 8 레인 구조로 자율 실행:

```
요구사항 → 설계 → 설계 리뷰 → 구현 → 구현 리뷰 → 통합 테스트 → 보안 테스트 → 배포 → 배포 리뷰
```

**Story flow (default — single-repo Story 또는 Epic 외 1 child Story)** — **1 Story = 2 PRs**:
- **Phase 1 PR** (요구사항+설계+설계리뷰): docs only
- **Phase 2 PR** (구현+구현리뷰+구현테스트+보안테스트): code + docs append

> **PR description `Closes/Fixes/Resolves` keyword 정책 (CFP-292 / Issue #299)**:
> - **Phase 1 PR MUST NOT** use `Closes #NNN`, `Fixes #NNN`, `Resolves #NNN` — GitHub 이 PR merge 시 해당 keyword 를 감지하여 Issue 를 자동 close 하므로, Phase 2 PR merge 전에 Story Issue 가 premature close 됨.
> - Phase 1 PR 에서는 `Related: #NNN` 사용.
> - **Phase 2 PR** 에서만 `Closes #NNN` 사용 (정상 auto-close 트리거).
> - **Cross-PR conflict resolution**: 동일 Story 의 복수 PR (Phase 1 + follow-up spec amendment 등) 이 충돌할 경우, base PR 을 먼저 merge 한 후 충돌 PR 을 `git rebase origin/main` 으로 merged base 위로 rebase, conflict 해소 후 merge. `git merge` 방향 역전 금지.

**Epic flow (cross-repo 또는 multi-Story Epic, CFP-82)** — **1 Epic = Phase 1 doc PR + N implementation PRs + close PR**:
- **Phase 1 PR** (hub / owner repo): Epic doc + child Story stubs + Codex 7-area review aggregate
- **Phase 2 ~ Phase N PR**: 각 child Story implementation. Joint-phase narrow form 허용 (1 Story 가 1 phase 안 multi-repo joint PR 보유 가능, ADR-020 Amendment 1)
- **Phase N+1 close PR** (hub / owner repo): `EPIC-RESULTS-<KEY>.md` Epic close artifact (location SSOT: [`docs/doc-locations.yaml`](doc-locations.yaml) `epic_results` row, [ADR-041](../archive/adr/ADR-041-doc-location-registry.md))
- Mid-Phase **spec amendment PR** 가능 (Codex push-back 발견 시)

mctrader 진행 중 Epic 예시:

| Epic | Phase 1 (hub) | Phase 2~N (impl) | close PR | total PR |
|---|---|---|---|---|
| MCT-25 RiskGate full | hub#41 | data#1 + engine#1/#2/#3 | hub#42 | 6 |
| MCT-32 Order rate limit | hub#48 | engine#4/#5/#6 + market-bithumb#1 | hub#49 | 6 |
| MCT-48 Paper Runtime | hub#64 | engine#10/#11/#12 + web#1/#2 + spec amend hub#72 | (in flight) | 7+ |

상세 오케스트레이션 규칙은 [`orchestrator-playbook.md`](orchestrator-playbook.md).

#### EPIC-RESULTS 파일 위치 + migration guide (ADR-041 Amendment 1)

EPIC-RESULTS-`<EPIC_KEY>`.md canonical location = [`docs/doc-locations.yaml`](doc-locations.yaml) `epic_results` row ([ADR-041](../archive/adr/ADR-041-doc-location-registry.md), Amendment 1 — CFP-288):

- **Mode A (owner repo)**: `<owner-repo>/docs/retros/EPIC-RESULTS-<EPIC_KEY>.md`
- **Mode B/C (hub repo)**: `<hub-repo>/docs/retros/EPIC-RESULTS-<EPIC_KEY>.md`
- **dogfood (codeforge family)**: `<internal-docs>/<plugin-folder>/retros/EPIC-RESULTS-<EPIC_KEY>.md`

**기존 root 위치 파일이 있는 경우 migration 패턴:**

```bash
# 1. docs/retros/ 디렉터리 생성 (없으면)
mkdir -p docs/retros

# 2. 기존 root 파일 일괄 이동
for f in EPIC-RESULTS-*.md; do
  git mv "$f" "docs/retros/$f"
done

# 3. inbound link 갱신 — Story file §11, design doc 등
grep -rn "EPIC-RESULTS-" docs/ | grep -v "docs/retros/" \
  | awk -F: '{print $1}' | sort -u
# 위 출력 파일에서 링크를 docs/retros/EPIC-RESULTS-*.md 로 갱신

# 4. 빈 디렉터리 정리 (docs/results/ 등 drift dir 존재 시)
rmdir docs/results 2>/dev/null || true
```

**Story file §11 link path (Mode B same-repo):**
```markdown
[EPIC-RESULTS-<KEY>.md](../../docs/retros/EPIC-RESULTS-<KEY>.md)
```

**Cross-repo / dogfood:** 절대 GitHub URL 사용 (예: `https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/retros/EPIC-RESULTS-<KEY>.md`)

### 5.1 Cross-repo Epic — Centralization mode 선택 (multi-repo consumer)

multi-repo consumer (예: mctrader 의 6 repo) 의 cross-repo Epic 진행 시 [ADR-020 Amendment 1](../archive/adr/ADR-020-cross-repo-epic-pattern.md) (CFP-81) 의 mode 결정 의무:

| Mode | child Story 위치 | 채택 조건 |
|---|---|---|
| **A: Repo-local** (ADR-020 v1 default) | 각 작업 repo 의 `docs/stories/<KEY>.md` | Implementation repo 가 자체 storyboard 운영 / repo 별 자율 lifecycle |
| **B: Hub-centralized** | 1 hub repo 가 모든 child Story 보유, implementation repo 는 code PR 만 | Doc-only hub repo 존재 + 도메인 ADR collocate (mctrader 패턴) |

---

> **post-merge-followup workflow (CFP-476 / ADR-026 Amendment 1)**: `templates/required-workflows-spec.yaml` 정의 `target: all` enterprise required workflow — 모든 codeforge consumer 자동 상속. terminal-phase gate (`phase:보안-테스트` if `lanes.security_ai: true`, `phase:구현-테스트` if `false`, fail-closed default `phase:보안-테스트`) 가 consumer `.codeforge/project.yaml` 또는 `.claude/_overlay/project.yaml` 의 `lanes.security_ai` field 를 read. Issue close trigger 는 dual-source AND (PR body close keyword regex ∩ Issue closedByPullRequestsReferences) — false-positive close 차단 (CFP-391/412/455 systemic issue 해소). 상세 SSOT = ADR-026 Amendment 1 §결정 5.A.

### lanes.security_ai opt-in (선택)

기본값 `false` — 5-lane + CI gate 모드로 동작. SecurityTestPL (Claude+Codex AI 보안 분석) 없음.

`true`로 설정하면 CI gate PASS 후 SecurityTestPL이 추가로 spawn됨:

```yaml
# .claude/_overlay/project.yaml
lanes:
  security_ai: true
```

**권장 상황**: 외부 노출 API / 금융 데이터 처리 / 개인정보 취급 시스템.
**불필요 상황**: 내부 네트워크 전용 시스템 / solo-dev 프로젝트 (기본값 유지).

GitHub native 보안 도구 (Dependabot / CodeQL / Secret Scanning)는 `security_ai` 설정과 무관하게 항상 동작. GitHub repo 설정에서 별도 활성화 필요:
- Settings → Security → Enable Dependabot alerts
- Settings → Security → Enable Code scanning (CodeQL)
- Settings → Security → Enable Secret scanning

**Mixed-mode 금지** — 단일 Epic 내 mode 일관 유지. 다른 Epic 은 다른 mode 가능.

**Joint-phase narrow form 허용** (ADR-020 Amendment 1 §결정 9): 단일 child Story 가 1 phase 안에서 multi-repo joint PR 보유 가능 (예: foundation Story 의 data + engine 동시 변경). 모든 PR 가 동일 Story key + 동일 phase label + topological merge order. mctrader MCT-26 = 사용 사례.

**Mid-Epic 신규 repo 추가**: 기존 mode 유지 default. Mode 전환 필요 시 Epic 분할 또는 재시작 (consumer 명시 ESCALATE). 상세 = playbook §3.4 + ADR-020 Amendment 1 §결정 8.

### 5.2 Framework Migration Epic Pattern (CFP-316 / ADR-047)

codeforge framework 자체가 진화(신규 SubAgent, §section 변경, ADR 변경 등)할 때 기존 진행 중인 Stories/Change Plans에 retrofit이 필요하다. 이를 위한 패턴. 정책 SSOT: [ADR-047](../archive/adr/ADR-047-framework-migration-epic-pattern.md).

#### Framework Delta Event 4-Type

codeforge framework 변경이 consumer에 영향을 줄 수 있는 이벤트의 공식 분류. PMOAgent가 감지 후 5분 이내에 Version Delta Review를 수행한다 ([playbook §13.1a](orchestrator-playbook.md)).

| Type | 설명 | PMOAgent 반응 |
|------|------|---------------|
| **Type A — Version bump** | consumer 프로젝트의 codeforge version bump | patch: advisory review / minor·major: Migration Epic 후보 |
| **Type B — ADR 변경** | Story 구조/lane 동작에 영향을 주는 신규·실질적 ADR 변경 (inter-plugin contract schema MAJOR bump, GitHub workflow fixture 변경 등) | 영향 범위 평가 후 Migration Epic 여부 결정 |
| **Type C — Deputy 변경** | 신규 SubAgent 추가 또는 SubAgent mandate 변경 (새 필수 §section 발생) | 진행 중 Story에 새 §section 추가 Migration Story 생성 |
| **Type D — Bootstrap 변경** | ADR-027/ADR-032 enforcement 변경 | consumer-guide 업데이트 + bootstrap 재검증 Migration Story |

**Type B 범위 주의**: inter-plugin contract MINOR/PATCH bump, workflow cosmetic fix는 advisory-only (Migration Epic 후보 아님). MAJOR bump 또는 story-init.yml 등 구조 변경만 해당.

#### Migration Epic Pattern

Migration Epic = [ADR-020 Cross-Repo Epic Pattern](../archive/adr/ADR-020-cross-repo-epic-pattern.md)의 codeforge framework-specific 적용.

**ADR-020 Mode 결정**:
- **Mode B (hub-centralized)**: consumer가 hub repo를 운영하는 경우 (예: mctrader-hub) — 기본값
- **Mode A (repo-local)**: single-repo consumer
- Mixed-mode 금지 (ADR-020 §결정 Amendment 1 정합)

#### Migration Epic §5 tiered template

delta 크기에 따라 필수 §section이 다르다. PMOAgent가 Tier를 결정하고 사용자 확인 optional.

| Delta 크기 | 필수 §section | 면제 (N/A 허용) |
|------------|---------------|-----------------|
| **Small** (1-2 ADR 변경, 새 SubAgent 없음) | §1 + §4 | §2, §3, §5 (N/A 사유 1줄) |
| **Medium** (새 SubAgent mandate, 새 §section 추가) | §1 + §2 + §3 + §4 | §5 (N/A 허용) |
| **Large** (breaking change, §structure 재편) | §1 + §2 + §3 + §4 + §5 | — |

**Tier 충돌 시 우선순위**: 동일 delta에서 여러 Tier 기준이 충돌하면 — (1) 새 SubAgent 추가 ≻ (2) 새 §section 추가 ≻ (3) ADR 수 기준으로 상위 Tier 적용.

**§section 설명**:
- **§1 Framework Delta Summary**: codeforge 버전 범위, 변경된 ADR 목록, 신규/변경 SubAgent, 변경된 §section
- **§2 Affected Artifact Inventory**: 진행 중 Stories + Change Plans + ADRs + hooks + labels 영향 목록
- **§3 Deputy Migration Notes**: SubAgent별 domain-specific retrofit 가이드
- **§4 Migration Story Backlog**: PMO-owned 순서화된 remediation Story 목록 + AC
- **§5 Completion Gate** (3 invariant):
  - Gate-1 Bootstrap PASS: ADR-027/032 enforcement 재검증 통과
  - Gate-2 Affected Story §section 갱신 완료: §2 inventory 모든 Story가 새 §section schema 준수
  - Gate-3 ADR alignment 확인: §1 변경 ADR 모두 Accepted + 영향 prior ADR cross-ref 갱신

#### Deputy Migration Notes 포맷

신규/변경 SubAgent mandate 발생 시 해당 SubAgent가 게시하는 retrofit 가이드 포맷:

```
## Migration Note: <deputy name> — <version-or-adr-ref>

**변경 사항**: <1줄 요약>
**기존 §X 보유 Story 적용**: <retrofit 가이드 2-5줄>
**N/A 조건**: <해당 없는 경우>
```

**CONDITIONAL SubAgent 적용**: LiveOpsDeputy / LiveOrderingDeputy owned §section (§13, §11 ledger invariant) 변경 시 — Live-active consumer에만 Migration Notes 적용 의무. Live-inactive consumer는 N/A (사유 1줄).

### 5.3 Debut evaluation protocol (첫 번째 consumer 적용 시)

codeforge 를 처음 적용하는 consumer 프로젝트는 **매 Story Phase 2 PR merge 후** 아래 7-카테고리 평가를 수행해 wrapper repo 개선 backlog 로 피드백한다.

**평가 7 카테고리**:
1. **Lane progression** — 8 lane 자연스럽게 통과 여부, 막힌 lane 식별
2. **Phase 별 gap / 과부하** — 특화 agent 누락 / 기존 agent 과부하 / 단계 누락·통합 필요성
3. **Decision table** — 원인 판정 decision table 모호 row, 새 row 필요 여부
4. **6 SubAgent mandate** — design lane SubAgent 의 도메인 부족 부분
5. **Workflow invariant** — GitHub Actions 강제 필요 항목 누락
6. **Template** — Story §1-§12 / Change Plan §1-§11 / ADR 템플릿 부족 필드
7. **Inter-plugin contract** — schema 부족 여부

**발견 사항 처리**:
- (b) 보완 권장 / (c) 차단 발견 시 → `mclayer/plugin-codeforge` GitHub Issue 등록
- label: `codeforge-improvement`, `from-<consumer-name>-debut`
- Issue body = 평가 발췌 + CFP proposal 형태
- consumer 작업 자체는 계속 진행 (비차단)

## 6. FAQ

### Q1. Overlay에 스칼라 필드(name, description, model)가 들어가면?

**merge.py가 abort**한다. 스칼라는 core-only.

### Q2. `.claude/agents/*.md`를 직접 편집하면?

SessionStart hook이 다음 실행 시 덮어쓴다. 편집하려면 `.claude/_overlay/agents/` 또는 플러그인 core agents/를 수정.

### Q3. Core 에이전트 자체를 바꾸고 싶다 (버그 수정·새 규칙 추가)

**플러그인 repo에 PR**. Core는 모든 consumer의 SSOT.

### Q4. 플러그인 업그레이드 시 overlay 호환성

core의 에이전트 섹션 구조·frontmatter 키가 바뀌면 overlay가 깨질 수 있다. 플러그인 버전 변경 시 [`migration-guide.md`](migration-guide.md) 참조.

### Q5. `codex` / `gh` 미설치 상태에서 시작하면?

세션 시작 시 의존성 체크가 blocking wait 상태로 전환되며 설치 요청. 설치 전까지 어떤 작업도 진행 안 함.

### Q6. GitHub Workflow 파일이 plugin과 drift된 경우?

SessionStart hook이 plugin templates SHA와 consumer `.github/workflows/` 사본 SHA 비교 후 알림. 자동 덮어쓰기 안 함. consumer가 검토 후 갱신:

```bash
diff -u ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/<file>.yml \
        .github/workflows/<file>.yml
# 차이 검토 후
cp ${CLAUDE_PLUGIN_ROOT}/codeforge/templates/github-workflows/<file>.yml .github/workflows/
```

### Q7. §1 변조 금지 invariant를 정당하게 위반해야 할 때 (예: 오타 수정)

`story-section-1-immutable.yml` Action이 자동 reject한다. 정당한 정정을 위한 bypass:

1. 별도 PR을 docs only로 open
2. **PR 제목**에 `[bypass-section-1]` 추가 (대소문자 무관, 정규식 매칭)
3. **architect team CODEOWNERS** 멤버 1명 이상 GitHub PR APPROVED review
4. Action이 두 조건 충족 시 자동 PASS, 부족 시 명확한 사유 코멘트 + status fail로 안내

요건:
- `.github/CODEOWNERS`에 `docs/stories/** @<org>/<architect-team>` 매핑 존재 (없으면 bypass 작동 불가)
- architect team에 GitHub repo `read` 이상 권한

운영 빈도 0에 가까워야 함 (주로 사용자 원문 명백한 오타 정정).

## 7. Sonnet Decider 정책 — DEPRECATED (CFP-134 / ADR-035, 2026-05-08)

**DEPRECATED 2026-05-08 (CFP-134 Epic / ADR-035, CFP-135 carrier)**: Codex review / Sonnet decider 는 codeforge 1st-class component 가 아니라 **사용자 ad-hoc 도구** 로 정정. codeforge 자동 invoke 없음. consumer Orchestrator 도 동일 — Sonnet decider 자동 발동 무효. 사용자 explicit request (e.g., "이 결정은 Codex+Opus 양쪽 옵션 받고 Sonnet 으로 정리해줘") 시에만 ad-hoc invoke 가능. 이전 본 §의 5 trigger 자동 발동 + Phase 1 trust model directive + Phase 2 instrumentation 계획 모두 무효.

Architecture decision SSOT = [`docs/adr/ADR-035-codeforge-agent-teams-epic-architecture.md`](../archive/adr/ADR-035-codeforge-agent-teams-epic-architecture.md) (Epic CFP-134). ADR-022 status = Deprecated. 본 § 의 2026-05-08 이전 내용은 `docs/adr/ADR-022-sonnet-review-verdict-decider.md` body history record 로 보존.

### review-verdict 흐름 (post-deprecate)

각 review iteration (DesignReview / CodeReview / SecurityTest) 의 final gate = **PL pl_recommendation** (PASS / FIX / FIX_DISCRETIONARY) 직접 적용. PL 이 자기 lane synthesis 후 Story §9 / GitHub comment / gate label / phase transition 모두 직접 write. Sonnet final pick 자동 발화 없음.

### 사용자 ad-hoc Sonnet 호출

특정 substantive 결정에서 사용자가 명시 요청 시 한정:

> "이 결정은 Codex 와 Opus 로 옵션 받고 Sonnet 으로 정리해줘"

또는 동등 wording. 이 경우 Orchestrator 가 ad-hoc Sonnet invoke (Agent tool with model:sonnet). decision-packet schema 의무 아님 — 사용자 prompt 자유 형식. Story §12 Sonnet Decision Log row append (사용자 요청 evidence 명시).

## 7.0 Subagent default (codeforge orchestration) — ADR-039

> consumer Orchestrator (예: mctrader Orchestrator / 추후 다른 consumer) 도 본 정책 inheritance — wrapper [ADR-039](../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) Phase 1 trust model + [playbook §3.0](orchestrator-playbook.md) normative SSOT 의 직접 적용. 본 subsection = consumer-side cross-ref anchor.

### 7.0.1 결정 stmt (consumer 적용)

consumer 가 codeforge family plugin (wrapper + 6 lane plugin) 을 사용하는 시점부터, consumer Orchestrator 의 **모든 codeforge 수정 작업** = Agent tool spawn (subagent) 으로 수행. inline 수행 = Inline whitelist 4-entry 외 영역 금지.

### 7.0.2 Inline whitelist (wrapper playbook §3.0 inheritance)

| # | Category | 설명 |
|---|---|---|
| 1 | 사용자 dialog | `AskUserQuestion` / 확답 step / 정보 요청 답변 |
| 2 | TodoWrite scratchpad | progress visualization marker (file write 아님) |
| 3 | Read-only Q&A 답변 | 사용자 정보 요청 응답 (state report / option enumeration / 도메인 설명) |
| 4 | Status report | Phase 완료 / Story close / final report (작업 단위 1번) |

**Skill 호출** (`superpowers:*`) = Inline (file write 아님 — meta wrapper). Skill 내부 individual tool call (Read / Edit / Write / mcp__github__\* / Agent / Bash) level 에서 spawn 분류 발동.

### 7.0.3 Dialog turn separation 의무

consumer Orchestrator 도 동일 — 사용자 dialog (entry 1) 와 dialog 직후 state change (file edit / GitHub state / Story write / FIX Ledger / label transition 등) 는 **별도 turn / message**. 한 메시지 안 inline write + dialog 동시 수행 = `policy_violation`.

### 7.0.4 Phase 1 trust model (enforcement hook 없음)

매 consumer Orchestrator 행위 시 본 §7.0 + wrapper [ADR-039](../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) + [playbook §3.0](orchestrator-playbook.md) reading 의무. 자동 enforcement 부재 — wrapper Phase 1 trust model 패턴 정합 (ADR-025 / ADR-029 precedent — Phase 1 doc-only trust pattern).

### 7.0.5 Consumer 측 활성 directive (Phase 1 trust model — enforcement scope 만 directive 의존)

**정책 normative status** = consumer 가 codeforge family plugin 을 사용하는 시점부터 **항상 적용** (§7.0.1 결정 stmt). directive 발화 여부와 무관 — 정책 자체 normative.

**Enforcement scope 만 Phase 1 trust model 적용** = directive 부재 시 자동 enforcement hook 부재. 즉 정책은 발효되지만, consumer Orchestrator 자체 인지 (본 §7.0 + ADR-039 reading) 가 1차 안전망. Phase 2 자동 enforcement (hook / telemetry, §7.0.6) 도입 전까지 implementation 책임 = consumer Orchestrator 자체.

consumer 측 사용자 활성 directive 권장 (wrapper directive 패턴 mirror — 자체 인지 강화 채널):

> "이 프로젝트에서도 codeforge plugin Subagent default (ADR-039) 적용해서 모든 수정 작업 = subagent spawn 으로 수행해라."

또는 동등 wording. directive 발화 시 consumer Orchestrator 정책 인지 reinforced — 그러나 발화 부재 시에도 정책 normative 적용 보존 (wrapper Phase 1 trust model 패턴 정합 — ADR-025 §결정 9 / ADR-029 / ADR-039 §결정 7 동일).

### 7.0.6 Phase 2 instrumentation (후속)

stop-event-v1 ledger / inline write detect hook / spawn cost telemetry — wrapper [ADR-039 §결정 9](../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) deferred follow-up CFP. consumer-side 측정도 wrapper 와 동시 도입.

### 7.0.7 Telemetry opt-in (CFP-283 / ADR-042 / ADR-043)

**Phase 1 wrapper-only doc + schema land** — measurement channel 도입 (stop-event-v1 ledger schema 신설). 모든 telemetry channel = **opt-in default false** invariant. Phase 1 = doc-only — telemetry hook 구현 / enforcement mechanism 모두 Phase 2 follow-up CFP.

#### Opt-in default false invariant

consumer 측 silent telemetry = trust 위반 (GitHub CLI opt-out 비판 precedent — Researcher §6.5). consumer overlay `.claude/_overlay/project.yaml` `telemetry.enabled: false` (default). 사용자 명시 opt-in 발화 의무 — directive 부재 시 ledger write 발생 = `policy_violation` (defect, ADR-043 §결정 1).

#### 활성 절차 (consumer 측)

```yaml
# .claude/_overlay/project.yaml
telemetry:
  enabled: true                              # global gate (opt-in 발화)
  channels:
    stop_event: true                         # stop-event-v1 ledger 활성
  storage_path: ".claude-work/measurement/"  # default (override 가능)
  retention_hot_days: 14                     # default (range: 7-30)
```

global `enabled: false` 시 모든 channel disabled (override 불가능 — global gate). per-channel granular flag (`channels.stop_event`) = 부분 활성 가능.

#### Wrapper-vs-consumer ledger isolation (ADR-042 §결정 9 / ADR-043 §결정 5)

ledger storage path 분리 invariant:

- **Wrapper dogfood**: `mclayer/plugin-codeforge` checkout 의 `.claude-work/measurement/stop-event.sqlite`
- **Consumer**: 각 consumer repo (mctrader 등) 의 `.claude-work/measurement/stop-event.sqlite`

**cross-host raw event leak 금지** (T-INFO-4 SecurityArch P0 위협 대응). Phase 2 cross-host 통합 (Divvi Up DAP / aggregate report) = 별도 후속 CFP.

#### Privacy 정책 SSOT

- **Allow-list ONLY 16 field whitelist** (capture 시점 — stop-event-v1 schema 16 field 외 capture 금지)
- **Deny-list regex 6 pattern** (capture 통과 후 2차 안전망 — defense in depth):
  - API key / credential
  - GitHub PAT (classic + fine-grained)
  - 한국 주민번호
  - email
  - hex≥32 (hash / private key)
- **0 API call constraint** — telemetry instrumentation = local I/O only. Anthropic API / GitHub API / external service 호출 금지 (measurement = measure 대상 amplify 금지, ADR-042 §결정 8).
- **best-effort 50ms ceiling** — append latency p99 ≤50ms (overflow 시 graceful degradation).

상세 SSOT = [ADR-043 (codeforge telemetry privacy policy)](../archive/adr/ADR-043-codeforge-telemetry-privacy-policy.md).

#### Phase 2 deferred items

- Telemetry hook 구현 (Python script `scripts/telemetry-append.py` / sqlite migration script) — Phase 2 follow-up CFP
- Aggregate script (raw → §10 FIX Ledger row mirror / dashboard 형식 변환)
- spawn-event-v1 신설 (§14 ↔ spawn-event dedup script 동반 의무)
- Cross-host telemetry 통합 (Divvi Up DAP / aggregate report)
- Rule-based hook (PreToolUse on Write / Edit / mcp__github__* — inline write detect)
- **Wrapper dogfood always-on enforcement mechanism** — Phase 1 doc-only invariant 유지 (env flag / hook / runtime validation 모두 Phase 2). 적용 범위 (wrapper repo `mclayer/plugin-codeforge` checkout 만) 는 Phase 2 enforcement CFP 시 별도 정의.

ROI gating prerequisite = post-merge-counters.jsonl 30+ run 누적 (ADR-026 §결정 3 패턴 / ADR-042 §결정 11).

## 7.1 Stop discipline + Epic-level continuity (ADR-025 + Amendment 1 + Amendment 2)

Stop discipline 정책 (ADR-025) 의 **trust model invariant** 와 **Epic-level continuity** 직접 적용. Amendment 2 (2026-05-08, CFP-135) 정정 후 — actor 표기 remap (Sonnet → PL pl_recommendation / 직전 사용자 directive). 정책 자체 (whitelist 외 stop = defect) 무손상.

### "Decider decides ⇒ Orchestrator proceeds without user confirmation" (ADR-025 §결정 1, Amendment 2 정정 후)

Decider 의 actor 분류:
- **review-verdict 단**: PL `pl_recommendation` (PASS / FIX / FIX_DISCRETIONARY) = decider
- **작업 단위 단 (Epic / Story / backlog)**: 사용자 직전 directive = decider
- **사용자 explicit ad-hoc Sonnet request**: 사용자 directive ⇒ Sonnet 임시 invoke (codeforge 자동 발동 무효)

Decider PASS / FIX / pick 결정 후 Orchestrator 가 사용자에게 "진행할까요?" / "이대로 가도 됩니까?" 묻는 것은 **whitelist 외 stop = `policy_violation` (defect)** 분류. 이전 ~~"Sonnet decides ⇒ ..."~~ 표기는 ADR-022 Deprecated 후 actor remap.

### Epic-level continuity (CFP-80 / ADR-025 Amendment 1, 2026-05-04)

**사용자 메시지 받은 시점 = 작업 단위 식별**:

| 사용자 메시지 패턴 | 작업 단위 | Continuity 의무 |
|---|---|---|
| "다음 작업 있나" + 1+ 후보 존재 | 모든 후보 / backlog 처리 단위 | backlog 모든 issue / Story 자동 통과 + 1번 final report |
| "X 진행" (X = Epic 명시) | Epic 의 7 phase + 모든 child Story | child Story 모두 Phase 1 + Phase 2 PR cycle 자동 통과 + 1번 final report |
| "X 진행" (X = Story 명시) | Story 의 Phase 1 + Phase 2 PR cycle | 양 PR cycle 자동 통과 + 1번 final report |
| 명시 선택 ("a" / "C" / "ok" / "진행하자") | 직전 메시지의 후보 또는 진행 path | path 끝까지 자동 진행 |
| 정보 요청 ("X 보여달라") | 정보 답변 단위 | 답변 + stop 없음 |

### 합법 stop whitelist (5종 strict — 본 외 모든 stop = defect)

1. **User environment 변경 의무** (PAT 발급 / API key / 외부 서비스 가입 / 자금 입금 / 1Password setup 등)
2. **Destructive action 직전** (force push / DB drop / 설정 영구 변경 / production first 동작)
3. **진정 unprecedented / unscoped 영역** (새 organizational decision)
4. **Decider escalation 결정** — PL pl_recommendation = `ESCALATE_PACKET_INCOMPLETE` 또는 사용자 ad-hoc Sonnet 호출 시 escalation_required=true (Amendment 2 정정 후, 이전 ~~"Codex+Sonnet decider 의 escalation 결정 (`decider_decision.escalation_required=true`)"~~)
5. **작업 단위 완료 후 final report** (1번)

### 불법 stop 패턴 (반드시 회피)

| Pattern | Defect 사유 |
|---|---|
| "후보 A/B/C/D 중 어떤거?" | sub-decision 자동 처리 의무 — PL pl_recommendation / 직전 사용자 directive 자동 진행 (Amendment 2 정정 후, 이전 ~~"Codex+Sonnet 자동 처리 의무"~~) |
| "큰 작업이라 확인 받겠습니다" | token cost 추정 = 사용자 의도 아님 |
| "Phase 1 완료, Phase 2 시작할까요?" | 1 Story / Epic 안의 sub-step (decision unit 분리 violation) |
| "5 sub-CFP 중 첫 번째 완료, 다음 진행할까요?" | backlog 단위면 5 모두 처리 |
| "final report 후 다음 작업 후보 결정 받음" | backlog 안 끝났으면 자동 발굴 + 진행 |

### Result 보고 형식 (1번)

작업 단위 전체 완료 후 1번 final report — sub-step 별 완료 시각 / 소요 시간 / decider pick (PL pl_recommendation 또는 사용자 ad-hoc Sonnet pick) / override marker 포함 (Amendment 2 정정 후, 이전 ~~"Sonnet pick"~~). 사용자 redirect 가능성 명시 (단 본인이 stop 안 함).

### Consumer 측 활성 directive (Phase 1 trust model — enforcement scope 만 directive 의존)

**정책 normative status** = consumer 가 codeforge family plugin 을 사용하는 시점부터 **항상 적용** (ADR-025 §결정 1 / Amendment 1). directive 발화 여부와 무관 — Stop discipline + Epic-level continuity 정책 자체 normative.

**Enforcement scope 만 Phase 1 trust model 적용** = directive 부재 시 자동 enforcement hook 부재 (§7.0.6 / Phase 2 instrumentation 도입 전까지). 즉 정책은 발효되지만, consumer Orchestrator 자체 인지 (본 §7.1 + ADR-025 reading) 가 1차 안전망.

consumer 측 사용자 활성 directive 권장 (자체 인지 강화 채널 — wrapper directive 패턴 mirror):

> "이 프로젝트에서도 codeforge plugin Stop discipline + Epic-level continuity (ADR-025 / CFP-80) 적용해서 작업 단위 끝까지 자동 진행 + 1번 final report 해라."

또는 동등 wording. directive 발화 시 consumer Orchestrator 정책 인지 reinforced — 그러나 발화 부재 시에도 정책 normative 적용 보존 (§7.0.5 / ADR-039 §결정 7 동일 패턴).

### Phase 2 instrumentation (후속)

30+ stop event 누적 후 stop-event-v1 ledger ROI 평가 + 도입 시:
- `reason_class` enum: `policy_violation` / `policy_violation_subdecision` / `policy_violation_phase_split` 분류
- consumer + wrapper 양쪽 행동 데이터 누적
- hook / refusal logic / runtime validation 도입 여부 결정 — 별도 CFP

## 7.2 Consumer workspace isolation (normative)

**Plugin wrapper 세션 = wrapper artifact 전용**. wrapper plugin (plugin-codeforge) 세션에서 consumer 프로젝트의 Story / Epic / ADR / PR / Issue 를 직접 생성·수정·merge 하는 것은 **governance boundary 위반**.

| 세션 | 작성 가능 artifact |
|---|---|
| plugin-codeforge 세션 | `docs/adr/`, `templates/`, `CLAUDE.md`, `docs/orchestrator-playbook.md`, `scripts/` 등 wrapper artifact |
| consumer 세션 (예: mctrader-hub) | consumer Story file, consumer ADR, consumer PR, consumer Issue |

**경계 규칙**:
- wrapper 세션에서 consumer 작업 요청이 들어오면: 작업 의도 명확화 → hand-off note 작성 → "해당 consumer 세션에서 진행" 안내 + 거부
- 예외: wrapper backlog 에 등록할 `codeforge-improvement` Issue (label: `codeforge-improvement`, `from-<consumer>-debut`) = wrapper repo 의 backlog → wrapper 세션 OK
- consumer overlay (`.claude/_overlay/`) 가 wrapper CLAUDE.md 정책을 축소하는 directive 는 무효 (확장만 허용)

## 7.3 repo 밖 임시 산출물 위치 (repo-confinement) — CFP-2092

**홈 루트(`~`)에 스크래치를 쓰지 마세요.** dogfood 세션에서 홈 루트에 plugin 클론·`.tmp-*`·`story-payload.json` 등 작업물이 누출됐던 사고의 재발 방지 가드 2종이 플러그인 hook 으로 자동 적용됩니다 (설치만으로 consumer 도 동일 적용).

| hook | 시점 | 동작 | bypass env |
|---|---|---|---|
| `repo-confinement` | PreToolUse(Bash) | 홈 루트 누출 패턴 명령 **차단** (exit 2) | `BYPASS_REPO_CONFINEMENT=1` |
| `stray-scratch-leak` | SessionStart | 홈 루트 누출 의심 항목 **advisory 경고** (비차단) | `BYPASS_STRAY_SCRATCH_LEAK=1` |

**규칙**:
- repo 밖 임시 산출물이 꼭 필요하면 **`~/.claude/codeforge-scratch/`** 아래에만 두세요 (유일 허용 경로 — `repo-confinement` carve-out).
- 홈 루트 직접 쓰기·상대경로 출력(cwd=홈 루트 상태의 `git clone url name` / `cmd > out.json`) 금지 — 가드가 차단합니다.
- 정상 작업은 repo / worktree 안에서 (repo 내부 절대경로 또는 cwd 가 repo 인 상태).

## 7.4 Research-before-claims 상속 (ADR-119)

wrapper [ADR-119](../archive/adr/ADR-119-research-before-claims.md) 의 research-before-claims 원칙은 consumer 가 codeforge family plugin 을 사용하는 시점부터 consumer Orchestrator 에 자동 상속된다 (ADR-039 §결정 7 inheritance 패턴 — §7.0.1 과 동일 구조).

- 핵심 의무 = 외부 지식 단정 전 자료 조사 + 출처 인용 / repo·cross-repo 사실 단정 전 실측 (cross-repo 는 `git fetch` 후 origin/main 실제 확인 — `git show origin/main:<path>`, wrapper ADR-073 패턴) / 확인 불가 시 "확인 불가/추정" 명시(abstention) 후 진행 — 3-way matrix 상세 = ADR-119 §결정 1 SSOT (본 절 = cross-ref anchor, 재서술 금지)
- consumer overlay 로 본 원칙 축소 불가 — 확장만 가능. 약화 = wrapper ADR-119 amendment 경로만 (evidence-gated, ADR-064 §결정 7)
- Phase 1 trust model — 자동 enforcement hook 부재, consumer Orchestrator 자체 인지가 1차 안전망 (§7.0.4 패턴)

## 7.5. CI Terminal State Classification (CFP-106 fix #144)

PR / GitHub Actions 결과 처리 가이드. fresh consumer (mctrader debut 등) 가 `SUCCESS` 만 wait 하는 naive polling 으로 사용자 stop 발생하던 패턴 해결.

### Terminal state 분류 + 자동 action

| state | conclusion / mergeable | 자동 action | 사용자 보고 |
|---|---|---|---|
| **SUCCESS** | conclusion=success | admin merge (또는 normal merge) | 1줄 또는 통합 보고 |
| **FAILURE** | conclusion=failure | `gh run view --log-failed` → fix → push → re-watch | root cause 1줄 |
| **ACTION_REQUIRED (known)** | conclusion=action_required + known list 등재 | admin merge (#143 fast-pass 후 무관) | 보고 X |
| **ACTION_REQUIRED (unknown)** | conclusion=action_required + 미등재 | 사용자 보고 + 진단 | 의무 |
| **NEUTRAL / SKIPPED** | conclusion=neutral/skipped | 무시 | 보고 X |
| **BLOCKED + MERGEABLE=true** | mergeStateStatus=BLOCKED + mergeable=MERGEABLE | admin merge (enforce_admins toggle 기법) | 보고 X |
| **BLOCKED + MERGEABLE=false** | mergeStateStatus=BLOCKED + mergeable!=MERGEABLE | rebase 시도 → fail 시 보고 | 시도 후 fail 보고 |
| **UNKNOWN** | 기타 | 사용자 보고 | 의무 |

### CI watch 명령 패턴 (POSIX bash)

```bash
# 모든 terminal state 자동 분류 (SUCCESS / FAILURE / ACTION_REQUIRED / BLOCKED).
# `gh pr checks --watch` 가 8 = ACTION_REQUIRED, 0 = success.
# required check 만 대기 (`--required` — ADR-048 Amendment 2, 전체 검사 대기 금지).
# required check 0건 repo (branch protection 미설정) 는 `--required` 제거 — 기존 전체 watch fallback.
# 백그라운드 실행 권고: 본 loop 는 Bash run_in_background 로 실행 (세션 비블로킹, 종료 시 자동 재개).
until gh pr checks "$PR" --repo "$REPO" --required --watch --interval 10 >/dev/null 2>&1 || ec=$? \
      && { [ "$ec" -eq 0 ] || [ "$ec" -eq 8 ]; }; do sleep 5; done
echo "[ci-watch] terminal state reached, exit=$ec"
```

### Known ACTION_REQUIRED 패턴

| 패턴 | 원인 | 자동 action |
|---|---|---|
| `phase-gate-mergeable` on type:epic 라벨 PR | (resolved CFP-106 #143 fast-pass) → 자동 success | (의도 fast-pass — admin merge 불필요) |
| `phase-gate-mergeable` on doc-only PR (`docs/`/`wrapper/`/`templates/`/`scripts/`/`.github/`/`.claude-plugin/`/`.claude/_overlay/`/`.codeforge/`/`scope_manifests/`/`*.md` 등) | (resolved CFP-106 #143 + CFP-758 fast-pass) → 자동 success | (의도 fast-pass) |
| `phase-gate-mergeable` on post-merge-fix 라벨 PR (3-조건 AND 충족) | (CFP-795 / ADR-026 Amendment 4 §결정 6 fast-pass) → 자동 success | (의도 fast-pass — 아래 절차 참조) |
| 기타 ACTION_REQUIRED | 사전 등재 X | 사용자 보고 + 진단 |

### post-merge-fix exemption 사용법 (CFP-795 / ADR-026 Amendment 4)

cross-repo Story land_order 후 safe defect 발견 시 (MCT-183 류 — byte-equivalence INV 위반, lint auto-fix 의도치 않은 적용 등) 아래 절차로 admin override 없이 hotfix PR 을 land 할 수 있다.

**전제 조건** (3가지 모두 필수):
1. 정정 대상 원 PR 이 이미 MERGED 상태
2. hotfix PR 이 신규 코드·로직 추가 없는 safe defect 정정
3. 정정 대상 원 PR 이 보안 영역 (`docs/adr/ADR-*.md` 보안 분류 / `docs/security/`) 미접촉

**Orchestrator 절차**:

```bash
# 1. hotfix PR body 에 marker 기재
story_uri: https://github.com/<hub-owner>/<hub-repo>/blob/main/<plugin>/stories/<KEY>.md
corrects_pr: <owner>/<repo>#<N>     # 정정 대상 원 MERGED PR

# 2. hub Story §10 FIX Ledger row append (Orchestrator monopoly — fix-event-v1)
#    현재 hotfix PR 번호 포함 의무 (예: mclayer/mctrader-data#71)

# 3. hotfix PR 에 post-merge-fix label 수동 부착
#    fix-event-v1 §10 row 작성 완료 후 부착 (순서 의무)

# → phase-gate-mergeable CI 가 3-조건 AND 자동 검증 → fast-pass success
```

**consumer hub repo 화이트리스트**: dogfood default = `github.com/mclayer/codeforge-internal-docs`. consumer hub repo 가 다른 경우 (1) `.claude/_overlay/project.yaml` 에 `phase_gate.allowed_hub_repos[]` 로 선언 (2) codeforge-upgrade 후 `bash scripts/inject-allowed-hub-repos.sh` 실행 (idempotent, ADR-116 확장-only 정합 — 축소 불가). 자동 wire 미활성 시 manual step. `docs/hotfix-playbook.md §6` 상세 참조.

**EC-2 경계**: `post-merge-fix` ≠ `hotfix:minimal` (별 경로). `hotfix:minimal` = 운영 장애 단일 파일 수정, 보안테스트 필수. `post-merge-fix` = cross-repo land_order 정정 전용, 보안 non-touch 역참조 시 보안테스트 실질 N/A.

### enforce_admins toggle 기법 (BLOCKED + MERGEABLE 케이스)

```bash
gh api "repos/$REPO/branches/main/protection/enforce_admins" -X DELETE
gh pr merge "$PR" --repo "$REPO" --admin --squash --delete-branch
gh api "repos/$REPO/branches/main/protection/enforce_admins" -X POST
```

> **Note**: enforce_admins toggle 은 admin 권한 + branch protection 보존 의무. PR merge 직후 즉시 복원 (window <1초).

## 8. 트러블슈팅

| 증상 | 원인 | 대응 |
|------|------|------|
| `regen-agents.sh: merge.py not found` | PLUGIN_ROOT 해석 실패 | `CLAUDE_PLUGIN_ROOT` 환경변수 확인 |
| `ERROR: overlay scalar mismatch at '.name'` | overlay frontmatter에 core와 다른 name 지정 | overlay의 name 필드 제거 |
| `ERROR: PyYAML required` | python3 환경에 PyYAML 없음 | `pip install pyyaml` 또는 venv 설정 |
| Agent가 overlay 내용을 따르지 않음 | 생성된 `.claude/agents/<Name>.md` 확인 | `cat .claude/agents/<Name>.md` → overlay body 실제 존재하는지 점검 |
| `gh: command not found` | gh CLI 미설치 | https://cli.github.com/ 참고해 설치 |
| GitHub MCP 미인증 | OAuth 만료 | `/mcp` 재인증 |
| story-init.yml Action 실패 | yq 미설치 또는 project.yaml 누락 / `github.story_key_prefix` 부재 | Action 로그 확인. yq 는 ubuntu-latest 표준 미보장 — Python fallback parser 가 두 번째 단계로 작동. project.yaml `github.story_key_prefix` 필수 |
| story-section-1-immutable.yml fail | §1 변경 + bypass marker 부재 | PR 제목 `[bypass-section-1]` 추가 + CODEOWNERS architect team APPROVED review (§7 Q7 절차) |
| fix-ledger-sync.yml mirror 안 됨 | §10 표 형식 위반 | `fix-event-v1` schema 준수 — 7 column (Iter / 시각 / 레인 / 트리거 / 원인 판정 / 재실행 범위 / RESET?). Iter = 1-indexed integer |
| subissue-from-impl-manifest.yml fail | §8.5 표 형식 위반 또는 `addSubIssue` GraphQL 권한 부재 | §8.5 첫 column = file path (각 row 1 sub-issue). GitHub Sub-issue 기능은 GraphQL beta — `issues:write` 권한 + repo 가 sub-issue feature flag 활성화 필요. 미작동 시 fallback = `core.warning` 만 — sub-issue 자체는 생성됨 (parent link 만 누락) |
| Phase-gate-mergeable check 통과 안 됨 | phase + gate 라벨 미부착 | lane plugin (DesignReviewPL·SecurityTestPL)이 라벨 부착했는지 확인. phase-label-invariant.yml가 자동 single-active 강제하므로 새 phase 라벨만 추가하면 됨 |
| §1 변경 PR이 reject됨 | story-section-1-immutable.yml | Q7 참조 |
| sub-issue 자동 생성 안 됨 | §8.5 매핑표 형식 오류 또는 `addSubIssue` GraphQL beta 변경 | Action 로그 확인. fallback으로 DeveloperPL이 `mcp__github__sub_issue_write` 수동 호출 |
