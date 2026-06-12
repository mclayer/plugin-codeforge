---
title: Orchestrator Playbook
status: active
owner: Orchestrator (= 최상위 Claude 세션)
created: 2026-04-23
updated: 2026-05-25
related:
  - CLAUDE.md
  - agents/RequirementsPLAgent.md
  - agents/DomainAgent.md
  - agents/PMOAgent.md
  - agents/ArchitectAgent.md
  - agents/DeveloperPLAgent.md
  # DocsAgent 부재 — CFP-40 final delete (ζ arc 완료)
  # Review subsystem (codeforge-review plugin, CFP-29 Phase 1 추출):
  - codeforge-review:agents/DesignReviewPLAgent.md
  - codeforge-review:agents/CodeReviewPLAgent.md
  - codeforge-review:agents/SecurityTestPLAgent.md
---

> **[ARCHIVED — Confluence-as-derived-mirror migration complete (CFP-1584 Phase 2 100% delivered, 2026-05-25 KST)]**
>
> This document has been split into §-level Confluence pages under bucket [CFP-1494 S2.4 carrier page (id=2130966)](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2130966). Git source remains the **SSOT** per [ADR-103 §결정 1/2](../archive/adr/ADR-103-git-confluence-sync-mechanism.md) (sync direction: git → Confluence). Confluence pages are **derived mirror**, NOT source of truth. Cross-ref: [ADR-100 §결정 1](../archive/adr/ADR-100-confluence-doc-ssot-recognition.md) (Confluence SoR-docs partial extend), [ADR-076](../archive/adr/ADR-076-declarative-reconciliation-upgrade.md) (cascade closure), [ADR-054](../archive/adr/ADR-054-doc-only-story-fast-path.md) (doc-only fast-path).
>
> **Sub-pages pushed (19 of 19)** — CFP-1584 Phase 2 directive × 19 contract 100% delivered (cumulative: prior PR #1626 7/19 + capacity-batched [CFP-1630](https://github.com/mclayer/plugin-codeforge/issues/1630) Batch 1 [#1636](https://github.com/mclayer/plugin-codeforge/pull/1636) + Batch 2 [#1643](https://github.com/mclayer/plugin-codeforge/pull/1643) + Batch 3 [#1650](https://github.com/mclayer/plugin-codeforge/pull/1650) + Batch 4 final 12/19):
>
> | § | title | Confluence id | URL |
> |---|---|---|---|
> | §1 | 세션 생명주기 | 2066024 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2066024/1) |
> | §2 | 사용자(Human) 상호작용 규약 | 2098442 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2098442/2+Human) |
> | §3 | 스폰 시퀀스 + 프롬프트 템플릿 | 2098466 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2098466/3) |
> | §3B | Preflight 체크 (lane 진입 직전) | 2098490 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2098490/3B+Preflight+lane) |
> | §4 | 병렬 스폰 판단 | 2131011 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2131011/4) |
> | §5 | docs/stories file 동기화 | 2163913 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2163913/5+docs+stories+file) |
> | §6 | FIX 루프 상태 머신 | 2098557 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2098557/6+FIX) |
> | §7 | 세션 재개(resume) 복원 절차 | 2131032 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2131032/7+resume) |
> | §8 | 토큰 예산 모니터링 + 세션 회고 | 2131053 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2131053/8) |
> | §9 | 트러블슈팅 플레이북 | 2098535 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2098535/9) |
> | §10 | Hotfix 경로 | 2098515 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2098515/10+Hotfix) |
> | §11 | Cross-agent write coordination | 2163935 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2163935/11+Cross-agent+write+coordination) |
> | §12 | Orchestrator 컨텍스트 패킷 | 2163955 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2163955/12+Orchestrator) |
> | §13 | PMOAgent 프로젝트 관리 (Cross-cutting) | 2066052 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2066052/13+PMOAgent+Cross-cutting) |
> | §14 | §0 Live Progress (CFP-20) | 2098588 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2098588/14+0+Live+Progress+CFP-20) |
> | §15 | 4-channel observability boundary | 2131073 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2131073/15+4-channel+observability+boundary) |
> | §16 | Post-merge automation flow | 2131093 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2131093/16+Post-merge+automation+flow) |
> | §17 | Inter-plugin contract sibling sync 절차 | 2131113 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2131113/17+Inter-plugin+contract+sibling+sync) |
> | 부록 A+B | 관련 문서 + 개정 이력 | 2066075 | [link](https://mclayer.atlassian.net/wiki/spaces/CFP/pages/2066075/A+B) |
>
> **Out-of-scope axis (별 carry-over, axis disjoint)**:
> - **CRITICAL Step 0** — pre-spawn-pin (134KB, §.N-level split) — [CFP-1617](https://github.com/mclayer/plugin-codeforge/issues/1617) (size limit axis ≠ Phase 2 directive axis)
> - **Probe artifact cleanup**: `_probe_1kb_CFP-1584` (id=2163892) — Confluence push capability sentinel, cleanup deferred to follow-up housekeeping CFP
>
> Page id mapping SSOT: [`docs/confluence-ia-tree.yaml`](confluence-ia-tree.yaml) `playbook_split_pages[]` field. Each entry's `push_attempt_status` field reports per-entry state (19 success + 17 deferred_mcp_disconnect for Step 0 §.N split = CFP-1617 carry-over).
>
> Mega-Epic context: [CFP-1415](https://github.com/mclayer/plugin-codeforge/issues/1415) (CLOSED 2026-05-24, Confluence-as-derived-mirror governance).

# Orchestrator Playbook

최상위 Claude 세션(이하 **Orchestrator**)의 행동 SSOT. 사용자(Human)가 제공한 요구사항을 받아 **0 core 에이전트 (wrapper-only)** + 6 lane plugin (codeforge-{review,pmo,requirements,test,develop,design}) + role:dev roster를 조정하는 모든 규약을 담는다.

**CFP-29 Phase 1 (BREAKING v0.17.0) 이후**: 5 review agent (Design/Code/SecurityTest PL + Claude/Codex worker)는 별도 plugin codeforge-review (현 모노레포 `plugins/codeforge-review/`, 구 plugin-codeforge-review repo 삭제됨 2026-06-12)로 추출됨. Orchestrator는 본 playbook의 관점에서 이들을 **외부 plugin agent**로 spawn하며, 결과는 `review_verdict v3` typed contract ([`docs/inter-plugin-contracts/review-verdict-v3.md`](inter-plugin-contracts/review-verdict-v3.md))로 수령한다 (v2 는 CFP-61 / ADR-022 시점 Archived, v1 은 CFP-D 시점 Archived — historical records).

`CLAUDE.md`는 "무엇이 있는가(에이전트 목록·레인·권한 경계)"를 정의하고, 본 playbook은 "어떻게 움직이는가(생명주기·스폰·복원·에스컬레이션)"를 정의한다.

---

## 1. 세션 생명주기

### 1.1 세션 개시 체크리스트

사용자 요구사항 접수 직후 아래를 순서대로 수행한다. 하나라도 생략하면 이후 단계에서 컨텍스트 drift·중복 작업 발생.

**0. 필수 의존성 확인 (모든 작업 선행 · 의무)**

   세션이 다른 장비 또는 다른 환경에서 시작될 가능성을 전제로 아래 5종을 모두 검증한다. 누락 시 자동 복구 가능한 것은 즉시 복구, 불가능한 것은 사용자에게 요구. 복구 완료 전까지 **모든 작업 중단**.

   **0a. GitHub MCP (필수 · 1종)**
   - deferred tool 리스트에 `mcp__github__*` 노출 여부 확인 (최소 `issue_write`, `issue_read`, `add_issue_comment`, `create_or_update_file`, `create_pull_request`)
   - 미노출 시 `~/.claude/mcp-needs-auth-cache.json` Read → `plugin:github:github` 키 존재 시 "needs auth" 확정
   - → 사용자에게 `/mcp` 재인증 요청
   - GitHub은 본 플러그인 핵심 의존성 (Issue/PR·docs file·sub-issue·Milestone 전부)이므로 우회·스킵 불가
   **GitHub 도구 우선순위 (CLAUDE.md §세션 개시 의무 mirror)**: MCP 노출 후 모든 GitHub 작업 = `mcp__github__*` 우선. `gh` CLI = MCP 미커버 영역 전용 fallback (milestone CRUD / Discussions / GraphQL / label 부트스트랩). MCP 미노출 상태에서 gh 우회 금지.

   **0b. 필수 플러그인 4종**
   - 대상: `codex@openai-codex`, `superpowers@claude-plugins-official`, `claude-md-management@claude-plugins-official`, `github@claude-plugins-official`
   - 확인: `~/.claude/settings.json`의 `enabledPlugins[<id>] == true` + `~/.claude/plugins/cache/<marketplace>/<plugin>/` 디렉토리 존재
   - **자동 복구**: cache 있으나 `enabledPlugins == false`인 경우 → `~/.claude/settings.json` 직접 Edit해 `true` 토글 + 세션 재시작 안내 (새 세션에서 반영)
   - **사용자 요구**: cache 부재 시 → `/plugins install <id>` 실행 요청 + 응답 대기

   **0c. 필수 CLI 2종 (codex + gh)**
   - `which codex` + `which gh` 실행
   - `gh auth status` 실행 (인증 만료 검증)
   - 미설치·인증 만료 시 설치 또는 `gh auth login` 가이드 제시 + 사용자 응답 대기

   **0d. consumer 리포 GitHub 셋업 검증** (blocking 아님)
   - `.github/workflows/`에 plugin 권장 6개 워크플로우 (`story-init.yml`, `phase-label-invariant.yml`, `story-section-1-immutable.yml`, `subissue-from-impl-manifest.yml`, `phase-gate-mergeable.yml`, `fix-ledger-sync.yml`) 부재 또는 SHA drift 검사
   - `.github/ISSUE_TEMPLATE/{story,bug,audit}.yml` 부재 검사
   - `.github/PULL_REQUEST_TEMPLATE.md` 부재 검사
   - `.github/CODEOWNERS` 부재 또는 architect/domain-expert team 매핑 누락 검사
   - 부재·drift 시 알림만 (자동 복사·자동 commit 안 함). 사용자가 `cp <plugin-templates>/...` 실행 안내

   **0e. 권장 플러그인 4종 (blocking 아님)**
   - 대상: `pyright-lsp`, `context7`, `commit-commands`, `pr-review-toolkit`
   - 노출·활성 여부 1회 확인, 미설치·비활성 시 권유 메시지만 제시하고 진행 허용

   **0f. codeforge plugin family version drift 검사 (CFP-262 / ADR-037)**
   - 9 plugin 의 installed version vs marketplace.json latest 비교
   - 실행: `bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-codeforge-version-drift.sh`
   - Severity → action mapping (ADR-037 surface table cross-ref):
     - **MAJOR drift** = hard-stop blocking → 모든 codeforge 작업 중단 + `/plugins update <name>` 의무 + Orchestrator 재 spawn
     - **MINOR drift** = warning + auto-proceed → 작업 진행, 사용자에게 update 권유
     - **PATCH drift** = info only → 작업 진행, log 만
   - **자동화**: consumer 측 `.claude/_overlay/.claude/hooks/` 에 SessionStart hook 등록 권장 (consumer-guide 참조)
   - **Bypass**: `BYPASS_VERSION_DRIFT=1` + `BYPASS_VERSION_DRIFT_REASON=<text>` env 시 우회 (audit trail 의무)
   - **MAJOR drift 의 의미**: ADR-037 정의 = breaking change (consumer migration 필요) — stale version 유지 시 silent corruption 위험. hard-stop 정당화.

   **0g. 구조적 변경 재구동 선행 의무 (ADR-053)**

   직전 세션에서 아래 구조적 변경 중 하나라도 발생했던 경우, 세션 재구동 완료 여부를 먼저 확인한다.

   구조적 변경 대상:
   - CLAUDE.md 의미 변경 (typo·형식 수정 제외)
   - plugin 버전 업
   - settings 구조 변경 (enabledPlugins·env·hooks 등)
   - agent definition 변경 (역할·모델·spawn 조건 포함)
   - skill 파일 의미 변경

   **확인 절차**:
   - 세션이 구조적 변경 반영 후 새로 시작된 것인지 확인. 동일 세션 내 변경 직후 연속 작업 = 재구동 미완료로 간주.
   - 미완료 시: 사용자에게 세션 재구동(새 Claude Code 세션 시작) 요청 후 **모든 작업 중단**.

   해당 변경이 **codeforge plugin 자체 변경**인 경우, 세션 재구동 확인에 더해 consumer 배포 완료 여부를 추가 확인한다:
   - [ ] marketplace sync PR merge 완료 (ADR-016 — `mclayer/marketplace` `plugins[name=codeforge]` mirrored 필드 동기)
   - [ ] consumer `/plugins install codeforge@mclayer` 완료
   - [ ] `bash ${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-codeforge-version-drift.sh` PASS

   위 조건 미충족 시 다음 작업 진입 금지 (`policy_violation` — ADR-053).

   **0h. 확인 결과 사용자 통보 형식**
   ```
   🔍 세션 개시 의존성 점검
   - GitHub MCP: ✅ 노출 / ❌ 미인증 → /mcp 재인증 필요
   - codex 플러그인: ✅ / ❌ cache 부재 → /plugins install codex@openai-codex
   - superpowers 플러그인: ✅ (integration SSOT: [`docs/superpowers-integration.md`](superpowers-integration.md))
   - claude-md-management 플러그인: ✅
   - github 플러그인: ✅
   - codex CLI: ✅ /opt/homebrew/bin/codex / ❌ 미설치 → brew install 권장
   - gh CLI: ✅ + 인증 OK / ❌ → gh auth login 안내
   - consumer 리포 .github/ 셋업: 6 워크플로우 / 3 forms / PR template / CODEOWNERS — N개 누락 (안내만)
   - (권장 플러그인: 4/4 활성 / 일부 비활성 — 진행에 영향 없음)
   - 구조적 변경 재구동 (ADR-053): ✅ 해당 없음 / ⚠️ 재구동 필요 → 새 세션 시작 후 작업 재개 / ❌ codeforge 배포 미완 → marketplace sync + /plugins install 후 재개
   - SessionStart prereq-check hook (0i, ADR-038 Amendment 2 §결정 9): ✅ hook 등록 + 첫 turn TodoWrite 스키마 prefetch 지시 수신 / ⚠️ hook 미등록 → runtime ToolSearch 폴백 가동 / ⚠️ ToolSearch 실패 → 표시 불가 경고 후 계속 (§결정 7 layered defense)

   [블로커 X건 — 복구 완료 전 대기]
   ```

   **0a-prime. worktree 정리 — eager 완료 시점 (primary) + 주기 backstop (CFP-427 / ADR-040 §결정 5)**

   worktree 정리 = 2-경로 (GitOpsAgent 소유 — agents/GitOpsAgent.md §5 SSOT):
   - **primary (eager)**: Story/Epic 완료 회고 시점에 GitOpsAgent 가 완료 Story worktree(들)을 mergedAt 확인 후 경로 기반 제거 (§1.2/§1.3 완료 flow). deterministic — 정상 완료분은 여기서 정리.
   - **backstop (주기적)**: 크래시·중단으로 회고를 못 거친 orphan 전용. `templates/scripts/check-worktree-stale.sh` — 조건 = age 7d+ AND merged PR (**squash-aware**: 병합 PR headRefOid 이후 추가 commit 0) AND clean (임시파일 제외) AND not-locked. preview = `GC_DRY_RUN=1`. bypass = `BYPASS_WORKTREE_GC=1`.

   > 과거 SessionStart hook 동기 호출은 **제거됨** — worktree 90+ 동기 스캔으로 세션 시작 지연. 또 GitHub post-merge automation 은 클라우드 러너라 로컬 worktree 미접근 → 로컬 세션 완료 시점이 유일한 deterministic 정리 지점. 주기 backstop 은 수동/스케줄 호출.

   **0i. Deferred tool 스키마 선제 로드 — SessionStart hook tier (ADR-038 Amendment 2 §결정 9, CFP-500)**

   Enforcement layer 위임: 본 항목의 의무는 **SessionStart hook tier (b)** 로 격상되었다 (Researcher 3-tier 모델). 구체적 prefetch 실행은 consumer `.claude/settings.json` `hooks.SessionStart[]` 에 등록된 `SessionStart-codeforge-prereq-check.json.sample` 이 helper script `${CLAUDE_PLUGIN_ROOT}/codeforge/scripts/check-codeforge-prereq.sh` 의 stdout 을 Orchestrator 첫 turn context 에 prompt-injection 형태로 inject 함으로써 수행한다. Orchestrator 는 turn 0 에 hook stdout 의 지시에 따라 `ToolSearch("select:TodoWrite")` 호출.

   **선행 attempt (2회 실패 history — tier escalation 동기)**:
   - CFP-375 (ADR-038 Amendment 1 §결정 8) — runtime advisory tier · 실패
   - CFP-385 (CLAUDE.md 0i 인라인 명시) — 동일 layer · 실패
   - CFP-500 (본 격상, 3rd attempt) — SessionStart hook tier

   **Layered defense (§결정 7·8 retain — fallback)**:
   - **(b) PRIMARY** — SessionStart hook stdout 가 첫 turn 에 prompt-injection
   - **(c) FALLBACK** — hook 미등록 / 실행 실패 시 Orchestrator 가 runtime ToolSearch attempt (§결정 8 retain)
   - **Failure handling** — runtime fallback 도 실패 시 경고 출력 후 작업 계속 (lane 차단 없음, §결정 7 retain): `⚠️ TodoWrite 스키마 로드 실패 — 레인 진행 표시 불가 (warning only)`

   **책임 경계** — hook = schema/state 가용성 advisory layer 한정. mechanical function-call 강제 아님 — behavioral compliance 자체는 여전히 Orchestrator 책임 (Researcher 3-tier 중 (b) layer 한정, ADR-038 Amendment 2 §결정 9 본문).

   **초기 preload list = TodoWrite 단독** (보수적 minimum). `prereq_tools[]` 확장 surface 는 별도 CFP measurable 도입 의도 후 확장.

   **0ii. Windows external session auto-resume (CFP-1355 / [ADR-110](../archive/adr/ADR-110-external-runtime-wrapper-ssot-boundary.md))**

   **Consumer opt-in** — Windows Task Scheduler wrapper (PowerShell `codeforge-session-resume.ps1` + `codeforge-auto-resume.xml` template) 자동 session 재개. rate-limit 도달로 session 종료 후, reset window 만료 시 `claude --resume` 자동 invoke. `scripts/install-codeforge-resume.ps1` (admin) 로 설치, `.claude/_overlay/project.yaml` `runtime.auto_resume.enabled: true` toggle 로 활성. Linux/macOS = Phase 2 sub-CFP carrier. docs/consumer-guide.md §1j 참조.

   **Wrapper dogfooding** — wrapper repo 자체 `.claude/settings.json` 에 본 hook 등록 의무 (Story §5.2 AC-1a / AC-8 (4)). consumer 측 등록 절차는 `docs/consumer-guide.md` § "Session start hooks" 참조.

1. **메모리 로드**: `~/.claude/projects/<workspace-hash>/memory/MEMORY.md` — 이전 세션 feedback·project·reference 기록 확인
2. **활성 Story 조회**: `mcp__github__list_issues(state='open', labels=['type:story'])`
3. **ADR 목록 확인**: 세션 내 첫 설계 결정 직전에만 `Glob(docs/adr/ADR-*.md)` + `Grep` (frontmatter category·status 필터)
4. **태스크 분류**:
   - 신규 요구사항 → §1.2 신규 세션 플로우 (또는 §1.2.0 Stage 0 옵션)
   - resume (활성 Story 존재) → §7 세션 재개 복원 절차

### 1.2.0 Stage 0 (선택, recommended for non-trivial Story) — pre-Issue brainstorming

복잡한 요구사항 (cross-cutting / 새 도메인 / 모호한 scope) 인 경우 Issue Form 제출 전 `superpowers:brainstorming` skill 로 사전 scoping 가능. **옵션 — CI 강제 없음** ([ADR-034](../archive/adr/ADR-034-pre-issue-brainstorming-stage.md)).

**KEY 사전 확보 (CFP-260 / ADR-036 — 권장)**: brainstorming 시작 직전 `cfp-reserve.yml` Issue Form 으로 1-line title 만 발의 → 받은 Issue # 가 KEY 가 됨 (`CFP-<#>`). spec / Phase 1 PR / Phase 2 PR 모두 이 KEY 인용 가능 — race-free + cross-session collision 방지. 30 일 미진행 시 `reservation-cleanup.yml` 가 자동 close.

```
[권장] 사용자 또는 Orchestrator 가 cfp-reserve.yml Issue Form 발의
  ├─ Issue 생성 직후 # 발급 = KEY 확정 (예: Issue #260 → CFP-260)
  └─ KEY 를 brainstorming spec / branch 명 / commit message 에 인용 가능

사용자 또는 Orchestrator 가 superpowers:brainstorming skill 호출
  ├─ Skill 가 spec 산출:
  │    consumer:    docs/superpowers/specs/<YYYY-MM-DD>-<slug>-design.md
  │    plugin repo: <internal-docs>/<plugin-folder>/specs/<YYYY-MM-DD>-cfp-NNN-<slug>-design.md
  │      (ADR-013 / ADR-017 enforced — default path 금지)
  ├─ spec 작성 후 reservation Issue body 갱신 + label promote:
  │    phase:reservation → phase:요구사항 + type:story (또는 type:epic)
  │    user-original 필드 = 요약 본문 (§1 verbatim source)
  │    spec_link 필드 (ADR-034 / Phase 2) = spec file path 또는 URL
  └─ promote 시 story-init.yml 트리거 → KEY = PREFIX-<Issue#> (ADR-036) → branch + Phase 1 PR 자동 생성
```

Stage 0 미사용 시 (작은 chore / 사용자 의도 명료) — §1.2 직접 진입 (KEY 는 story.yml Form 제출 시점에 자동 발급).

`superpowers:brainstorming` 의 in-lane 호출 (DomainAgent / RequirementsPL) 은 본 Stage 0 와 별개 단계 — [`docs/superpowers-integration.md`](superpowers-integration.md) §2 SSOT 참조. Pre-Issue 시나리오의 호출점은 §2 표 의 `wrapper / Orchestrator (or human) / pre-Issue scoping (Stage 0)` row.

### 1.2 신규 세션 플로우

```
사용자 요구사항 접수
  ↓
Orchestrator 태스크 분류 (Epic/Story 단위 분해)
  ↓
PMOAgent 가 GitHub Milestone 직접 생성 (Epic — 사용자 요구사항 1건 단위, Bash gh api repos/*/milestones*)
  + PMOAgent 가 Epic Issue 직접 생성 (label: type:epic, body: narrative description, milestone 매핑 — codeforge-pmo self-write)
  ↓
Epic 창설 직후:
  └─ PMOAgent 스폰 (Scope 분해 자문 — 의존성·우선순위·병렬/순차 판정)

Story별 반복 (선택지 1: 사용자가 GitHub Issue Forms로 생성):
  ├─ 사용자가 GitHub UI에서 Issue Form (story.yml) 제출
  ├─ story-init.yml Action 자동 실행:
  │    1. <KEY_PREFIX>-N 다음 번호 계산
  │    2. docs/stories/<KEY>.md 생성 (§1=verbatim, §2-11=placeholder)
  │    3. Phase 1 PR 자동 open (architect team CODEOWNERS auto-review)
  │    4. Issue body를 docs link로 변환
  │    5. Label phase:요구사항 부착
  └─ Orchestrator가 자동 감지 → RequirementsPLAgent 스폰 (요구사항 레인 시작)

Story별 반복 (선택지 2: Orchestrator가 사용자 prompt에서 직접 분해):
  ├─ RequirementsPLAgent 가 GitHub Issue 직접 생성 (label: type:story + phase:요구사항, milestone — codeforge-requirements self-write)
  ├─ story-init.yml Action 또는 Orchestrator 가 docs/stories/<KEY>.md 생성 + Phase 1 PR 수동 open
  └─ RequirementsPLAgent 스폰

Story 완료 직후:
  ├─ PMOAgent 스폰 (회고 감사 + FIX Ledger 리뷰 + ADR 후보 검토)
  └─ GitOpsAgent 스폰 (완료 Story worktree eager 정리 — mergedAt 확인 후 경로 기반 제거, 회고와 동시/직후)
```

### 1.3 세션 종료 조건

- **정상 완료**: 보안 테스트 레인 PASS → PMOAgent 가 Story file §11 직접 self-write (codeforge-pmo) + Phase 2 PR `Closes #N` 머지 → Issue 자동 close → 세션 회고 (§8.3) + **GitOpsAgent 가 완료 Story worktree eager 정리** (mergedAt 확인 후 경로 기반 제거, 회고와 동시/직후 — primary 정리 경로) → 종료
- **blocking wait**: PMOAgent "사용자 확인 필요" 체크박스 미해소 → 사용자 질문 제시 후 세션 대기 (§2)
- **ESCALATE**: 설계 리뷰·구현 리뷰 FIX 3회 초과 또는 ArchitectPLAgent 판단 근본 한계 → 구조화된 에스컬레이션 보고 후 판단 대기

### 1.4 Phase label progression invariant (CFP-85)

mctrader debut audit Issue [#181](https://github.com/mclayer/plugin-codeforge/issues/181) P1-5 finding: closed Story Issues 가 종종 `phase:요구사항` 등 초기 phase 에 정체 — phase progression 미수행. **본 invariant 가 lane plugin self-write 의무 명시화**:

각 lane PASS verdict 시 phase 라벨 transition **반드시 수행**:

| 현재 phase | PASS 시 transition | enforcer |
|---|---|---|
| `phase:요구사항` | → `phase:설계` | RequirementsPLAgent (codeforge-requirements) |
| `phase:설계` | → `phase:설계-리뷰` | ArchitectAgent (codeforge-design) |
| `phase:설계-리뷰` | → `phase:구현` | **Orchestrator** (CFP-61 / ADR-022 5-step step 4 — review-verdict trigger e final write) |
| `phase:구현` | → `phase:구현-리뷰` | DeveloperPL (codeforge-develop) |
| `phase:구현-리뷰` | → `phase:구현-테스트` | **Orchestrator** (CFP-61 / ADR-022 5-step) |
| `phase:구현-테스트` | → `phase:통합-테스트` | **Orchestrator** (ADR-048 CI gate inline → IntegrationTestAgent spawn) |
| `phase:통합-테스트` | → `phase:보안-테스트` (lanes.security_ai: true 시만) 또는 → `phase:배포` (CFP-1059 후 — 배포 lane 가용 시) | **Orchestrator** (ADR-055 IntegrationTestAgent PASS 후) |
| `phase:보안-테스트` | → `phase:배포` (CFP-1059 후) 또는 terminal (배포 lane 미가용 시) | **Orchestrator** + `gate:security-test-pass` 부착 |
| **`phase:배포`** (신설 — CFP-1059 / ADR-087) | → `phase:배포-리뷰` (DeployPLAgent PASS 후) | **Orchestrator** + `gate:deploy-pass` 부착 (DeployPLAgent 자기 진단 PASS 후, Phase 1 declarative — 실 lane plugin seed 후 활성) |
| **`phase:배포-리뷰`** (신설 — CFP-1059 / ADR-088) | terminal (Epic 묶음 close 시점) | **Orchestrator** + `gate:deploy-review-pass` 부착 (DeployReviewPLAgent smoke/성능/cutover 3종 PASS 후, Phase 1 declarative) |

**Issue close 의무**:
- Issue close 시 phase label = `phase:보안-테스트` (terminal) 가 default
- early-close (Epic 종료 / 중복 / Out-of-scope reclassify 등) 시 phase 라벨 `early-close:<reason>` 명시 의무
- phase progression 미완 채로 close = `policy_violation` defect 추적 (ADR-025 stop discipline metric 과 동일 source)

**Audit trail (CFP-85 신규)**:
- Story file §9.x = Gate evidence row 의무 (story-page-structure.md §9 enrichment)
- EPIC-RESULTS-<EPIC_KEY>.md §10 = PR gate evidence 표 (CFP-83 신규)
- 두 source 합쳐 audit reproducibility 보장 — GitHub API 라벨 verify 가 향후 막혀도 file evidence 로 phase progression audit 가능

**Phase 2 follow-up (별도 CFP)**: `phase-label-invariant.yml` Action 강화 — Issue close 시 phase 라벨 = terminal state (`phase:보안-테스트`) 또는 `early-close:<reason>` 부재 시 reject. lint-level enforcement.

---

## 2. 사용자(Human) 상호작용 규약

### 2.1 blocking wait 진입 기준

다음 중 하나 이상 충족 시 Orchestrator는 **즉시 진행 중단**하고 사용자 응답 대기 상태로 전이:

- RequirementsPLAgent 통합 명세서에 "사용자 확인 필요" 체크박스 미해소 항목 존재 (Story file §5.5)
- RequirementsPLAgent 상충 조정 실패 (Domain·Analyst·Researcher 세 관점 결론 충돌, ADR 위반 혐의 등)
- ArchitectAgent (chief author)가 "기존 API의 breaking change 불가피" 보고 → ArchitectPLAgent 검수 후 사용자 ESCALATE
- DesignReviewPL ESCALATE 판정 (설계 리뷰 FIX 3회 초과)
- CodeReviewPL ESCALATE 판정 (구현 리뷰 FIX 3회 초과)
- ArchitectPLAgent가 "테스트 반복 FAIL — 근본 원인 재분석 후에도 해소 불가" 보고
- 사용자 요구사항 범위·우선순위·예산이 프롬프트에서 해석 불가

### 2.2 사용자 응답 수령 시 재스폰 대상 판정

| 응답 종류 | 재스폰 대상 | 전달할 컨텍스트 |
|-----------|------------|----------------|
| "사용자 확인 필요" 답변 | RequirementsPLAgent | 답변 내용 + 기존 Story file 경로 |
| ADR 갱신 승인 | ArchitectAgent (ADR direct write) → RequirementsPLAgent | ArchitectAgent가 ADR 업데이트 후 RequirementsPLAgent 재호출 (CFP-26 Phase 0a) |
| breaking change 승인 | ArchitectPLAgent (chief author 재스폰 의뢰) | ADR 후보 추가 지시 + Change Plan 재수립 |
| 설계 리뷰 ESCALATE 후 judgment | ArchitectPLAgent (재진입) | 사용자 지시를 Change Plan 갱신 입력으로 전달 → chief author 재스폰. 설계 리뷰 카운터 **리셋** |
| 구현 리뷰 ESCALATE 후 judgment | ArchitectPLAgent | 동일 — 구현 리뷰 카운터 리셋 |
| 테스트 반복 FAIL 판단 | ArchitectPLAgent | 사용자 지시 근본 원인 가설 + Change Plan 대폭 수정 허가 |
| 요구사항 범위·우선순위 변경 | Orchestrator 자체 | Story Issue 재분해 또는 기존 Story scope 수정 → RequirementsPLAgent 재스폰 |

> **ADR-077 §결정 1/2 cross-ref (CFP-759 Story-1, origin/main)**: "사용자 확인 필요" 답변 = clarification 강제 재조사 trigger SSOT. 위 표 §272 행 "요구사항 범위·우선순위 변경" 경로는 ADR-077 §결정 2 가 trigger SSOT cross-ref (**§272 흡수(absorb)되며 대체(replace) 아님** — "Story 재분해" invariant 의미 보존). 강제 fan-out 6 절차 = §4.4.1.

### 2.3 사용자 ESCALATE 프롬프트 표준 형식

```
⚠️ 사용자 판단 요청 (ESCALATE)

[상황]
- Story: <KEY> — {한 줄 요약}
- 현재 단계: {phase:설계-리뷰 / phase:구현-리뷰 / phase:구현-테스트 / phase:보안-테스트}
- 트리거: {설계 리뷰 3회 FIX / 구현 리뷰 3회 FIX / 테스트 반복 FAIL / ADR 충돌 / breaking change / clarification 재조사 cap 5 초과 → escalation_class: scope_redefinition_required (NOT failure / NOT abort — ADR-077 §결정 6 escape valve, recheck_counter RESET to 0, §10 FIX Ledger 무기록)}

[시도 이력]
1. Iteration 1: {수정 방향} → {결과}
2. Iteration 2: {수정 방향} → {결과}
3. ...

[남은 이슈]
- {객관적 blocking 결함 목록}

[가능한 선택지]
- (A) {선택 A — 트레이드오프 서술}
- (B) {선택 B}
- (C) 요구사항 자체 재해석 — 범위 축소 / ADR 갱신 / 포기

[Orchestrator 의견]
{선택 A 권장 등, 근거 1-2줄}

다음 행동을 지시해주세요.
```

응답 전까지 Orchestrator는 **스폰 중단**. 사용자 응답 수령 시 §2.2 표로 재진입.

### 2.4 사용자 지시 vs 내부 판단 충돌

- **사용자 지시가 항상 우선**. CLAUDE.md 규칙·ADR·본 playbook은 사용자 명시 지시에 의해 override 가능
- 단, 사용자 지시가 ADR과 충돌하면 **ADR 갱신 의사 확인** 후 진행 (암묵적 위반 금지)
- 프로젝트 고유의 **안전 제약**(consumer overlay가 도메인별 명시한 invariant·검증 규칙 등)은 사용자가 명시적으로 해제하지 않는 한 유지

---

## 3. 스폰 시퀀스 + 프롬프트 템플릿

### 3.0 Orchestrator execution mode — Default subagent (수정 작업) (ADR-039)

> **NORMATIVE SSOT (ADR-039 §결정 1·2 codification)**. 본 §3.0 = wrapper / consumer Orchestrator 의 매 codeforge 수정 작업 행위 직전 reading 의무 영역. 본 단락이 4 SSOT doc cross-ref tree 의 root.

#### §3.0.1 결정 stmt

codeforge 수정 작업 = Orchestrator default **subagent spawn**. "inline 으로 충분한가 vs subagent 가 나은가" 결정 분기 **자체 금지** — branch logic 제거 = ADR-025 §결정 7 `policy_violation_subdecision` 발화 채널 차단.

#### §3.0.2 수정 작업 정의 (closed enumeration — ADR-039 §결정 1)

- file edit / write (`docs/**`, `src/**`, `templates/**` 포함)
- GitHub state change (Issue / PR / comment / label / milestone / sub-issue / branch / merge)
- Story file write (§1-§14 어느 섹션이든)
- FIX Ledger §10 row append (fix-event-v1 contract — Amendment: Orchestrator-owned delegate subagent 포함)
- Lane-spawn evidence §14 row append (ADR-031 — Amendment 1: Orchestrator-owned delegate subagent 포함)
- gate label transition (`gate:design-review-pass` 등)
- phase label transition (`phase:요구사항` → `phase:설계` 등)
- workflow yaml 수정·추가
- ADR / Change Plan / domain-knowledge 페이지 write
- **trivial Read 1건 도 spawn 의무** (사용자 verbatim 명시 — Story CFP-275 AC-3 trivial-threshold-zero)

#### §3.0.3 Inline whitelist (closed 4-entry — ADR-039 §결정 2)

| # | Category | 설명 | Mechanism rationale |
|---|---|---|---|
| 1 | 사용자 dialog | `AskUserQuestion` / 확답 step / 정보 요청 답변 (Yes/No / 옵션 선택) | Subagent one-shot 이라 continuous dialog 자체 mechanism 불가능 (ADR-009 §결정 + "플랫폼 제약") |
| 2 | TodoWrite scratchpad | progress visualization marker write | TodoWrite = file write 아님, Orchestrator scratchpad / meta progress channel — 수정 작업 enumeration 미포함 |
| 3 | Read-only Q&A 답변 | 사용자 정보 요청 응답 (state report / option enumeration / 도메인 설명) | 수정 작업 아님 — codeforge orchestration scope 외 |
| 4 | Status report | Phase 완료 / Story close / final report | 수정 작업 아님 (read-only synthesis) — ADR-025 Amendment 1 §결정 11 의 "1번 final report" |

4 entry **외** 의 모든 codeforge orchestration 행위 = subagent spawn 의무. **모호 시 = 수정 작업 측 분류** (안전 방향 — ADR-013 cutoff precedent 정합). 5번째 카테고리 추가 = ADR-039 amendment 의무.

**Skill 호출 분류 (Change Plan §3.0.2 mirror)**: Skill 호출 (`superpowers:brainstorming` / `writing-plans` / `verification-before-completion` / `executing-plans` / `dispatching-parallel-agents` 등) = **Inline** (5번째 entry 추가 X — closed 4-entry 보존). Skill = wrapper around tool calls (file write / GitHub state mutation 자체 미발화 — meta wrapper). Skill 내부 individual tool call (Read / Edit / Write / mcp__github__\* / Agent / Bash) level 에서 spawn 분류 발동 — ADR-039 §결정 1 자연 routing.

#### §3.0.4 Dialog turn separation (Story CFP-275 AC-5 / Change Plan §3.0.1 — normative)

사용자 dialog (Inline whitelist entry 1) 와 dialog 직후 state change (subagent spawn 의무 영역 — file edit / GitHub state / Story write / FIX Ledger / label transition 등) 는 **별도 turn / message** 로 분리한다. 한 메시지 안에서 inline write + dialog 동시 수행 = `policy_violation`.

#### §3.0.5 구현 실행 방식 — Subagent-Driven 자동 선택 (CFP-358 / CFP-374)

`superpowers:executing-plans` 또는 `superpowers:subagent-driven-development` 스킬 실행 중 "구현 실행 방식 선택" 프롬프트(Subagent-Driven vs Inline Execution)가 발생하면, `AskUserQuestion`으로 사용자에게 묻지 않고 **자동으로 Subagent-Driven 경로를 선택**해 진행한다.

**스킬 지시 우선순위 override (CFP-374)**: 스킬 파일이 `AskUserQuestion`을 호출하도록 지시하더라도, 이 §3.0.5 정책이 스킬 내용보다 우선한다. 스킬을 로드한 후 "구현 실행 방식" 선택지를 발견하면:
1. `AskUserQuestion` 호출 없이 해당 단계를 건너뛴다.
2. Subagent-Driven 경로로 **직접 진입**한다.
3. 사용자에게 선택을 묻는 어떤 형태의 확인도 하지 않는다.

이 정책은 wrapper + 모든 consumer에 동일 적용. behavioral directive → memory 저장 금지 (normative) 케이스 — playbook이 enforcement SSOT.

**Generalized normative SSOT (ADR-064 §결정 10, Amendment 3 CFP-637)**: 본 §3.0.5 (Subagent-Driven 자동 선택) 와 동일 패턴 (skill body 안 AskUserQuestion 지시 override) 은 **ADR-064 §결정 10 Skill body ↔ CLAUDE.md normative priority precedence** 로 generalize. CLAUDE.md normative > ADR > skill body > external skill body. 본 §3.0.5 = §결정 10 의 specific case (CFP-358 / CFP-374 carrier), §결정 10 = 전체 skill body 영역 generalized precedence (codeforge:brainstorm Phase 1 dialog reflex / superpowers:brainstorming checklist 등 포함).

#### §3.0.6 Ownership ≠ Mechanism 분리 (ADR-039 §결정 3 + §결정 12)

본 정책은 **mechanism (어떻게 수행)** 변경. **ownership (누가 작성권)** 무변.

- Orchestrator monopoly ownership (유지 — invariant 무손상):
  - Story §10 FIX Ledger row append (CFP-32 / fix-event-v1 contract)
  - Story §14 Lane Evidence row append (ADR-031 / CFP-126)
  - review-verdict v3 final write (Story §9 / GitHub comment / gate label / phase transition)
  - branch protection / CI workflow / cross-plugin schema templates
- Mechanism (변경): 위 ownership 영역의 file write / GitHub state change 도 **subagent spawn 으로 수행**. Orchestrator 가 "§10 row append 전용 subagent" / "§14 row append 전용 subagent" / "label transition 전용 subagent" 를 spawn 해 Edit / mcp__github__\* tool 호출.

**Orchestrator 정의 확장 (ADR-031 Amendment 1 + fix-event-v1 Amendment, CFP-275)**: "Orchestrator self-write" / "Writer monopoly v1: Orchestrator 단독" = top-level Claude 세션 + **Orchestrator 가 §10/§14 row append 전용으로 spawn 한 delegate subagent** 모두 포함. lane plugin agent 가 자체 임의 §10/§14 직접 append 는 여전히 금지 (lane plugin spawn ≠ Orchestrator-owned delegate spawn).

#### §3.0.7 Phase 1 doc-only trust model (ADR-039 §결정 8)

매 Orchestrator 행위 시 (1) ADR-039 / (2) 본 §3.0 / (3) CLAUDE.md "Default subagent context (수정 작업)" / (4) consumer-guide § "Subagent default (codeforge orchestration)" / (5) hotfix-playbook 1줄 reading 시 자체 인지. 자동 enforcement 부재. ADR-025 / ADR-029 precedent 정합 (Phase 1 doc-only trust pattern).

Phase 2 enforcement (stop-event-v1 ledger / inline write detect hook / spawn cost telemetry / rate-limited error second-order risk 측정) = ADR-039 §결정 9 deferred follow-up CFP.

#### §3.0.8 Cross-ref

- **Policy SSOT**: [ADR-039](../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) (amends ADR-009)
- **Motivation**: [ADR-025](../archive/adr/ADR-025-stop-discipline-non-whitelist-as-defect.md) §결정 7 (`policy_violation_subdecision`)
- **Narration interaction**: [ADR-029](../archive/adr/ADR-029-phase-execution-visibility-expansion.md) (매 spawn / return narrate 의무)
- **§14 evidence**: [ADR-031](../archive/adr/ADR-031-lane-spawn-evidence-trail.md) Amendment 1 (Orchestrator-owned delegate inclusion)
- **§10 FIX Ledger**: [fix-event-v1](../docs/inter-plugin-contracts/fix-event-v1.md) Amendment (Orchestrator-owned delegate inclusion)
- **TodoWrite scratchpad**: TodoWrite tool surface 자체 standalone 정당화 (file write 아님 — meta progress channel). ADR-041 = informational reference, normative dep 아님 (PR #277 머지 order 무관).
- **Subagent semantics 분기**: [ADR-035](../archive/adr/ADR-035-codeforge-agent-teams-epic-architecture.md) (default subagent context 의 one-shot subagent — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0`)
- **Consumer scope**: [consumer-guide.md § "Subagent default (codeforge orchestration)"](consumer-guide.md)
- **Hotfix scope**: [hotfix-playbook.md](hotfix-playbook.md) (exception 없음 — 사용자 verbatim "무조건")

#### §3.0.9 Pre-action fact verification (normative — wrapper + all consumers)

Orchestrator 가 사용자에게 substantive path 를 제시하거나 외부 system 동작을 인용하기 전, 아래 6-item self-audit 의무:

| 항목 | verify 도구 | skip 금지 조건 |
|---|---|---|
| 인용 file / 디렉터리 실제 존재 여부 | `Glob` / `Bash ls` | path 를 사용자에게 제시하는 모든 경우 |
| workflow / Action trigger 조건 | `Read` | "자동으로 X 가 일어남" 주장 전 |
| schema / config 실제 fields | `Read` | structured contract 인용 전 |
| GitHub Issue / state | `mcp__github__issue_read` | Issue 상태 주장 전 |
| 사용자 환경 state | `Read ~/.claude/settings.json` 또는 `Bash which` | 설치 여부·인증 상태 주장 전 |
| 외부 지식 / 산업 표준 / 기술 동작 일반론 | `WebSearch` / `WebFetch` / 공식 문서 | training 지식 기반 단정 발화 전 — 출처 인용 의무 |

**외부 지식 grounding (ADR-119)**: 위 표 6번째 항목의 normative SSOT = [ADR-119](../archive/adr/ADR-119-research-before-claims.md) — 외부 지식 주장 = 자료 조사 선행 + 출처 인용, repo 사실 = 실측 (ADR-073), 확인 불가 = "확인 불가/추정" 명시(abstention) 후 진행. 본 절 = cross-ref anchor (상세 중복 서술 금지).

**Hedging 금지 신호 (이 단어 응답에 등장 시 verify 의무)**:
- "should be" / "보통" / "~로 추정" / "~일 것" / 외부 system 동작 가정

**Subagent 답 weak signal**: subagent 응답에 "추정" / "확인 필요" / "공식 미기재" 등장 시 main session 에서 fact 직접 검증.

5초 cost verify 로 방지 가능한 사실은 추론으로 답변 금지.

#### §3.0.10 Internal-docs branch safety (normative — codeforge dogfood 작업 시)

`codeforge-internal-docs` working directory 는 외부 프로세스(사용자 IDE / 별도 터미널 / 별도 Claude 세션)가 언제든 branch 를 switch 할 수 있다. 매 commit 전 의무:

1. **Branch verify — 단독 Bash call (chained 금지)**:
   ```bash
   git -C c:/workspace/mclayer/codeforge-internal-docs branch --show-current
   ```
   출력이 intended branch 와 일치 확인. 불일치 시 즉시 stash + checkout intended branch.

2. **Push 전 dry-run — 단독 Bash call**:
   ```bash
   git -C c:/workspace/mclayer/codeforge-internal-docs push --dry-run origin <branch>
   ```
   `main -> main` 출력 시 즉시 abort + branch verify.

3. **Chained `&&` 명령에서 branch verify 금지**: `git branch --show-current` 는 항상 exit 0 → verify 결과와 무관하게 다음 단계 진행. verify = 반드시 단독 call + 출력 확인 후 다음 call.

4. **main / master force push 절대 금지**. 사고 발생 시: cherry-pick → correct branch → push (force push X).


#### §3.0.11 Worktree-first mandate (normative — wrapper + all consumers)

모든 coding work 는 git worktree 안에서 수행. 원본 working directory(`git checkout <branch>`) 직접 편집 금지.

- **Story 시작 시**: `bash templates/scripts/worktree-create.sh cfp-NNN origin/main` 선행 → cwd = worktree path
- **Subagent spawn 시**: prompt 에 `Working dir: <worktree-path>` 명시 — lane spawn (§3.5) 과 ad-hoc spawn 동일. **추가 `git -C <worktree_abs_path>` directive (ADR-040 Amendment 6 / CFP-843)**: 모든 file operation (git command + Write/Edit absolute path, forward-slash 정규형) 을 worktree abs path 기준 강제 — harness cwd reset gap 차단 (§3.5 SSOT)
- **Ad-hoc 작업 포함**: lane spawn 외 일반 subagent spawn, 사용자 직접 작업 모두 동일 적용
- **Consumer 동일 적용**: consumer project 에서 codeforge 사용 시 동일 rule
- **위반 판정**: 원본 working directory 에서 file edit/write/bash 수행 = stop discipline 위반 (ADR-025 §결정 2 `policy_violation`)

인프라 SSOT: ADR-040 (CFP-136). Script: `bash templates/scripts/worktree-create.sh <branch> <base-ref>`.

#### §3.0.12 Rate-limit Fallback (ADR-057)

Agent tool이 Sonnet subagent spawn 결과로 rate-limit 에러를 반환하면:

1. 동일 입력 패킷으로 `model: opus` 재spawn (1회 한정)
2. 재spawn 성공 시 §14 Lane Evidence row에 `[rate-limit-fallback:sonnet→opus]` 태그 추가 후 정상 진행
3. Opus도 실패 시 사용자에게 상황 통지 → 대기 (자동 재시도 루프 금지)

판별 기준: Agent tool result에 "rate limit", "quota exceeded", "429" 포함 시 rate-limit로 분류.

#### §3.0.13 PR description `## Lane evidence` manual append 정책 (CFP-507)

Phase 2 PR description 안 `## Lane evidence` row append 시 Orchestrator (또는 Orchestrator-owned delegate subagent — §3.0.6 정합) 가 아래 3-step 절차를 준수한다. 본 정책은 CFP-490 (#490, merged) §7.5 origin investigation 의 carrier — codeforge-develop sibling plugin DeveloperPLAgent body composition convention (`agents/DeveloperPLAgent.md` "Phase 2 PR body composition convention" section) 와 짝.

**3-step 절차**:

1. **기존 heading 존재 check** — `grep '^## Lane evidence' <PR description body>` 또는 GitHub MCP `mcp__github__pull_request_read` 로 PR body fetch 후 line-prefix match
2. **존재 시 row 만 append** — 기존 `## Lane evidence` heading 다음 lane row 7개 영역 안 적절 lane row 의 status 갱신 (`<PASS|SKIPPED|FIX|ESCALATED|BYPASS>`). **heading 재추가 금지** — 두 번째 `## Lane evidence` heading 발생 시 `lane-evidence-check.yml` 5a duplicate guard 발화 (CFP-490 §결정 1 정합)
3. **부재 시 heading + 7-row template inject** — `## Lane evidence` heading + 7-row format (wrapper `templates/github-pr-template.md` SSOT line 79 verbatim 정합):
   ```
   ## Lane evidence

   - 요구사항: <PASS|SKIPPED|FIX|ESCALATED|BYPASS>
   - 설계: <PASS|SKIPPED|FIX|ESCALATED|BYPASS>
   - 설계-리뷰: <PASS|SKIPPED|FIX|ESCALATED|BYPASS>
   - 구현: <PASS|SKIPPED|FIX|ESCALATED|BYPASS>
   - 구현-리뷰: <PASS|SKIPPED|FIX|ESCALATED|BYPASS>
   - 구현-테스트: <PASS|SKIPPED|FIX|ESCALATED|BYPASS>
   - 보안-테스트: <PASS|SKIPPED|FIX|ESCALATED|BYPASS>
   ```

**동시 동기화 의무 (ADR-031 정합)**: Story §14 Lane Evidence row append 와 PR description row append 는 **동일 turn / 단일 spawn cycle** 안에서 동시 처리. 두 영역 drift 시 §14 = SSOT (ADR-031 §결정 3 enforcement layer 우선), PR description 은 mirror.

**위반 시 guard 발화**: `lane-evidence-check.yml` workflow 의 5a tie-break case A/B/C (CFP-490 §결정 1) 가 duplicate `## Lane evidence` heading 또는 7-row format 위반을 detect → PR 차단 + audit comment. Bypass channel = `hotfix-bypass:lane-evidence-check` label (ADR-024 Amendment 3 정합).

**Cross-ref**:
- codeforge-develop `agents/DeveloperPLAgent.md` "Phase 2 PR body composition convention" — agent body composition layer
- wrapper `templates/github-pr-template.md` line 79 — heading 형식 SSOT
- ADR-031 §결정 3 — §14 Lane Evidence enforcement layer
- CFP-490 §결정 1 — `lane-evidence-check.yml` 5a guard tie-break

#### §3.0.14 Stop-time 평문 정리 + 표현 맥락 파악·문장 구조 self-check (Amendment 2 신설, CFP-610)

ADR-064 §결정 3 룰 6 + §결정 9 의 playbook-side 운영 매뉴얼. SSOT = [ADR-064 §결정 3 룰 6 / §결정 9](../archive/adr/ADR-064-decision-principle-mandate.md). CLAUDE.md "Stop-time 평문 정리 (Trace 5)" 단락 = summary mirror.

**룰 6 — 표현 발화 전 self-check**:

Orchestrator 가 사용자 응답 발화 직전 다음 4 항목 self-check:
1. 직전 turn 의 핵심 결정 / 미해결 분기점
2. 사용자 발화 요지 (지금 무엇을 묻는가 / 무엇을 지시하는가)
3. 현재 진행 단계 (Phase 0 brainstorm / Phase 1 dialog / Phase 2 implementation / spec 작성 / FIX 루프 / lane spawn 등)
4. 문장 구조 — cold reader 가독성 (완전한 문장 / jargon 사전 점검 ([`docs/wording-dictionary.md`](../docs/wording-dictionary.md) 카테고리 a/b) / 식별자 평문 요약 (룰 3 정합) / 다중 분기 numbered list 분리 (룰 4 정합))

실패 signal — 사용자 frustration 발화 (예: "이게 무슨 말이냐") 시 retro audit 의무 (PMOAgent retro file §wording-discipline 표).

**§결정 9 — Stop-time 300자 평문 정리 + Question quality 3-check (Amendment 3 강화, CFP-637)**:

Orchestrator 가 사용자 dialog turn 종료 시 다음 의무:

**(a) 300자 ± 50자 평문 정리**:
- 포함 항목: 직전 turn 핵심 결정 / 다음 step / 미해결 분기
- 생략 가능: tool_use only turn (TodoWrite / Read Q&A 답변 / Status report 평문 자체) — ADR-039 Inline whitelist 4-entry 정합
- 적용 범위: wrapper + 모든 consumer (CLAUDE.md L208 normative 정합)

**(b) Question quality 3-check (Amendment 3 신설, CFP-637)** — 질문 형식 / 결정 option 발화 직전 self-check:

1. 가치 판단 영역인가? (사용자 선호도 / 가치 판단 기준 / 미공개 컨텍스트 요구)
2. derived default 자명한가? (Epic body / Story context / ADR / 사용자 직전 발화 누적)
3. 1-option 만 있는데 묻는 것 아닌가? (옵션 분기 자체가 무의미한 영역)

판정 로직: 위 3 중 1+ "묻지 말아야 함" → **발화 금지**, derived default declare + 결과 보고 + 진행 (사용자 정정 의무).

7 anti-pattern P1-P7 차단 carrier (Epic CFP-635 body §Anti-pattern enumeration verbatim):
- **P1**: Implementation detail 결정 묻기 (ADR scope / version bump option 등 derive 가능 영역)
- **P2**: Skill body 가이드라인 무비판 수렴 (skill body 가 normative 보다 우선시) — §결정 10 carrier
- **P3**: 1-option 만 있는데 "그대로 진행할지?" 묻기
- **P4**: Confirm-of-confirm ("진행해" 직후 또 묻기)
- **P5**: Status report 가 사실은 질문 ("미해결 분기" implicit confirm)
- **P6**: 3-option 자동 발사 (numbered list reflex)
- **P7**: Continuous "진행해" 패턴 인지 실패 (5+ turn 연속에도 dialog format 시작)

**강제 강도**: behavioral directive only — mechanical enforce 불가 (turn-final hook 부재). retro audit signal (PMOAgent retro file §wording-discipline + §over-questioning 표) + sunset gate metric (frustration 발화 0건 / 3 Story 누적). sister Story CFP-638 = Continuous "진행해" 패턴 partial mechanical detect carrier.

**Continuous "진행해" 패턴 detect (Amendment 3 sister, CFP-638)** — Orchestrator self-check (mechanical hook layer 부재 시 1차 안전망):

직전 N (≥3) user turn 안 다음 pattern 누적 detection:
- "진행해" / "그대로" / "계속" / "ok" / "yes" / "go" / "맞아" / "맞다"

3+ 연속 → 후속 turn 의 dialog format (numbered list / decision option / "권장 = ..." 형식) 발화 자동 차단. **declare + 결과 보고 only** (사용자 정정 의무, §결정 3 룰 1 정합).

5+ 연속 누적 → strong brevity signal. 후속 turn 은 numbered list 자체 발화 금지 (§결정 9 3-check 의 1+ 자동 trigger).

mechanical layer: `docs/evidence-checks-registry.yaml` entry `stop-time-continuous-confirm-detect` (CFP-638, warning tier, advisory only — turn-final hook 부재 platform 한계). retro audit signal SSOT = PMOAgent retro file §over-questioning 표 — Story 단위 frustration count + "진행해" repetition trace tracking.

미래 mechanical hook 도입 = 별도 CFP follow-up (PreToolUse / PostToolUse hook 안 AskUserQuestion / numbered list output detection, platform hook capability 확장 의존).

**wording dictionary 참조**: [`docs/wording-dictionary.md`](../docs/wording-dictionary.md) — 카테고리 (a) forbid + 카테고리 (b) 평문 정의 의무 entry SSOT.

**§결정 10 — Skill body ↔ normative precedence (Amendment 3 신설, CFP-637)**:

**Priority order**: CLAUDE.md normative > ADR > skill body > external (superpowers / claude-plugins-official / 외부 plugin) skill body.

skill body 안 "AskUserQuestion" / "사용자 confirm" / "확인" / "묻기" / dialog format 지시는 §결정 3 룰 1 (Derived default) + §결정 9 3-check 보다 후순위. derived default 자명 영역에서 skill body 지시 무시 의무.

Implementation pattern:
1. Skill 호출 시 skill body 안 AskUserQuestion / confirm 지시 발견
2. §결정 9 3-check 적용 — derived default 자명한가?
3. 자명 → skill body 지시 무시, derived default declare + 진행
4. 비자명 + 진짜 가치 판단 영역 → skill body 지시 적용 (AskUserQuestion 발화 허용)

Generalized precedent (CFP-358 / CFP-374):
- CFP-358 `superpowers:executing-plans` "구현 실행 방식 선택" → Subagent-Driven 자동 선택 (§3.0.5)
- CFP-374 `superpowers:subagent-driven-development` 동일

첫 applied case = `skills/codeforge-brainstorm/SKILL.md` Phase 1 dialog reflex 차단 (Amendment 3 Story B). cross-plugin sister Story CFP-639 = `superpowers:brainstorming` upstream PR carrier (wrapper 측 mitigation = 본 §결정 10 normative override 명시로 covered).

**적용 범위**: wrapper + 모든 consumer + 모든 skill (codeforge:* / superpowers:* / claude-plugins-official:* / 외부 plugin skill).

#### §3.0.15 Parallel Dispatch Protocol (CFP-609 / ADR-064 Amendment 1)

Orchestrator 가 lane PL agent spawn 시 **plan task DAG 분석 결과를 spawn prompt 에 기재** 의무. ADR-064 §결정 4 (Trace 4) "Orchestrator multi-task spawn default = parallel" normative declaration 의 execution-time enforcement carrier.

**SSOT** = [`docs/inter-plugin-contracts/parallel-dispatch-protocol-v1.md`](inter-plugin-contracts/parallel-dispatch-protocol-v1.md) (kind:registry, wrapper canonical, sibling sync 면제). 본 §3.0.14 = registry SSOT 의 1줄 요약 + 4 의무 항목 + 6 enum + 4-분기 cross-ref (DRY 구조 — verbatim mirror 차단).

**4 의무 항목** (Orchestrator → PL spawn prompt — registry §4 full schema):

1. plan DAG 분석 결과 batch list verbatim 기재 (registry §4.1)
2. PL 에 자율 병렬 권한 명시 — `pl_autonomous_parallel_authority: required` 3-value enum 중 `required` default (registry §4.2)
3. sequential 의무 영역만 명시 — 6 enum 중 해당만 (registry §4.3)
4. file-level conflict resolution 패턴 기재 — same-file-different-method / same-file-different-section / same-file-same-method (registry §4.4)

**6 sequential mandate enum** (close-set — full SSOT: registry §3):

`tdd_red_phase` / `schema_migration` / `adr_reservation_append` / `fix_ledger_append` / `sibling_sync_ordering` / `marketplace_sync_ordering`

**PL 자율 병렬 결정 tree 4-분기** (full SSOT: registry §5):

1. plan 의 parallel_with hint 있음 → multi-instance 병렬
2. parallel_with hint 부재 + 파일 disjoint + interface 의존 0 → 자율 병렬 (default)
3. same-file-different-method + commit atomic 분리 capability 보유 → 병렬 + merge 시점 sync (capability 부재 시 4번 fallback)
4. same-file-same-method 또는 schema_migration → sequential 의무 (6 enum 중 해당 명시)

**위반 시**: ADR-064 §결정 4 위반. spawn prompt 에 sequential 선택 사유 명시 없이 sequential dispatch = ADR-039 §결정 7 `policy_violation_subdecision` 발화 채널.

**Mechanical enforcement**: `parallel-dispatch-prompt-check` warning tier lint (ADR-060 evidence-enforceable framework 정합) — `scripts/check-parallel-dispatch-prompt.sh` + `templates/github-workflows/parallel-dispatch-prompt-check.yml` (`continue-on-error: true`, bypass label `hotfix-bypass:parallel-dispatch-prompt`).

**env=0 / env=1 동등성** (registry §6.4):
- env=0 (default subagent context, ADR-039) — Orchestrator round-trip polyfill, PL 이 batch N task multi-instance subagent dispatch 1 round trip 안에 spawn
- env=1 (agent teams, ADR-044) — TeamCreate + SendMessage continuous dialog, Lead ↔ Worker

**Cross-ref**:
- ADR-064 §결정 4 Trace 4 + Amendment 1 — normative SSOT + implementation contract carrier
- ADR-039 §결정 7 `policy_violation_subdecision` — 위반 발화 채널
- ADR-044 §결정 2 `dispatch_mode` enum — env=1 직교 차원
- ADR-056 — team-spec-requirements 6-way teammates (CFP-609 absorb)
- ADR-060 — evidence-enforceable promotion framework (warning tier entry)
- §12 spawn prompt template — `[Parallel Dispatch Hint]` block 기재 의무 (registry §4.1 verbatim)

#### §3.0.16 — DeveloperPL + branch-creating subagent pre-spawn-pin mandate (CFP-895 / ADR-039 Amendment 1)

ADR-039 §결정 14 (Amendment 1) 의 Orchestrator-side codification. DeveloperPL 또는 새 branch 를 생성하는 subagent (codeforge-develop:DeveloperAgent / role:dev 등) 가 Phase 2 PR open 또는 cross-repo paired PR open 시 stale base 회피 mandate.

**Orchestrator 의 의무 절차** (subagent return 직후):

1. **post-spawn verify** — `mcp__github__pull_request_read get` 의 `head.sha` parent commit 을 `mcp__github__list_commits sha=main perPage=1` (또는 `gh api repos/<owner>/<repo>/commits/main --jq .sha`) 와 비교.
2. **mismatch detection** — branch HEAD parent ≠ current origin/main 이면 stale-base → 즉시 **FIX trigger** (구현-side, RESET=NO).
3. **re-dispatch 의무** — 동일 subagent 재spawn 시 prompt 에 (a) explicit current-main-HEAD SHA (Orchestrator 가 방금 고정한 값) + (b) "self-reset 금지 / 기존 작업 content 보존, only rebase the base" + (c) 추가 mid-flight churn 대비 "rebase 시 main HEAD 재고정 (parallel session advance 가능)" 명시.
4. **§10 FIX Ledger row append** — stale-base rebase iteration = Orchestrator monopoly write (fix-event-v1 contract, CFP-32). 형식 = `구현 (Orchestrator verify-before-trust, 구현리뷰 이전 적발)` lane.

**근거 evidence**: CFP-699/CFP-702/CFP-848 3차 누적 (ADR-039 Amendment 1 §결정 14 표).

**SubAgent prompt Step 0 의무** — Orchestrator 가 DeveloperPL spawn 시 packet 에 다음 Step 0 명시:

```text
## CRITICAL Step 0 — pre-spawn-pin (mandatory, ADR-039 §결정 14)

Branch 생성 직전:
```bash
git fetch origin
MAIN_HEAD=$(git rev-parse origin/main)
echo "PINNED_MAIN_HEAD=$MAIN_HEAD"
```

모든 후속 branch 생성 + rebase + PR open 시 본 SHA 사용. self-claim / packet reference / local HEAD / memory SHA 무조건 신뢰 금지. mid-flight main churn 가능 — rebase 시점에 재고정 의무.
```

**Cross-ref**: ADR-039 §결정 14 / §결정 9 (Amendment 1 enforcement Phase 2 hook 격상 경로) / [[feedback_verify_pin_head_sha]] / [[feedback_no_permission_prompts]] / codeforge-develop:`agents/DeveloperPLAgent.md` "PR 생성 Pre-flight Guard" Step 0 확장 (CFP-895 paired PR).

### 3.1 9 레인 + Cross-cutting 스폰 순서 (요약, CFP-1059 / [ADR-087](../archive/adr/ADR-087-deploy-lane-and-lifecycle-extension.md) + [ADR-088](../archive/adr/ADR-088-deploy-review-lane-and-production-evidence-transfer.md) — 7 → 9 lane 확장)

> **Phase 1 declarative**: 본 §3.1 의 배포 / 배포 리뷰 lane spawn 시퀀스 = declarative anchor (CFP-1059 Story-1). 실 DeployPLAgent / DeployReviewPLAgent spawn = lane plugin seed (codeforge-deploy / codeforge-deploy-review) 신설 후 활성 — 별 sub-Story carrier 영역.

```
[Cross-cutting 트리거]
Epic 창설:  Orchestrator → PMOAgent (Scope 분해 자문)
Story 완료: Orchestrator → PMOAgent (회고 감사 + ADR 후보 검토)
Epic 묶음 완료 (모든 Story merged): Orchestrator → DeployPLAgent 자동 trigger (Epic close → Deploy cascade, ADR-026 Amendment N 동반)

[Story 내부 9 레인 — CFP-1059 ADR-087/088 — 6 → 8 단계 확장 + Cross-cutting PMOAgent]
요구사항:    Orchestrator → RequirementsPLAgent(DomainAgent ∥ Analyst ∥ Researcher 병렬, 셋 다 non-skippable) → PL dedup·상충 조정 → Story file §3-6 갱신
설계:        Orchestrator → ArchitectPLAgent → (CodebaseMapper ∥ Refactor ∥ SecurityArchitect ∥ TestContractArch ∥ ModuleArchitect 병렬) → ArchitectAgent (chief author) 통합 → ArchitectPLAgent 검수 → Change Plan 확정
                         → ArchitectAgent direct write (docs/change-plans/<slug>.md + docs/adr/ADR-NNN-<slug>.md) + ArchitectAgent 가 Story file §3/§7/§11 직접 self-write (codeforge-design self-write 표)
설계 리뷰:   Orchestrator → DesignReviewPLAgent (lane=design packet 작성) → packet return (no writes — CFP-61 / ADR-022)
             **[D2-A CFP-2111] pr_phase 판정 + 주입 절차 (ReviewPL packet 작성 전 선행)**:
             Orchestrator 가 ReviewPL 에 packet 작성 의뢰 시, PR 의 `pr_phase` 를 결정론적으로 판정해 packet 에 주입한다.
             - **판정 방법 (primary — 결정론적)**: PR 변경 파일 전체를 아래 repo-specific 정밀 docs allowlist 와 비교.
               - **internal-docs repo**: `wrapper/stories/**` · `wrapper/change-plans/**` · `wrapper/domain-knowledge/**`
               - **wrapper repo**: `docs/stories/**` · `docs/change-plans/**` · `docs/domain-knowledge/**` · `archive/adr/**`
               - 변경 파일 전체가 allowlist 한정이고 구현 코드 0 → `pr_phase: phase1_docs`
               - allowlist 외 경로 1건이라도 포함 → `pr_phase: phase2_impl` (보수 default)
               - **bare `*.md` catch-all 금지**: `agents/**` · `templates/**` · `scripts/**` · `.github/**` 등 구현 산출물 .md 를 phase1_docs 로 역방향 오판 방지.
             - **보조 cross-check**: Story phase 라벨 (`phase:요구사항`/`phase:설계` = Phase 1, `phase:구현` 이후 = Phase 2). 파일 패턴과 불일치 시 파일 패턴 우선.
             - 판정 결과를 packet 의 `pr_phase` optional 필드에 주입 (`review_packet` schema v1.1 — `plugins/codeforge-review/templates/review-pl-base.md §2`).
             **review-verdict 5-step algorithm (CFP-61 / ADR-022 §결정 3)**:
             1. ReviewPL spawn → workers (ClaudeReviewAgent ∥ CodexReviewAgent 병렬) → dedup → review-verdict-v3 packet 작성 (no writes)
                ├── findings + pl_recommendation 작성
                ├── decision_state = pending_sonnet (or blocked_packet_incomplete if pl_recommendation=ESCALATE_PACKET_INCOMPLETE)
                └── return to Orchestrator
             2. Orchestrator: decision-packet-v2.1 작성 (trigger: review-verdict, review_lane_context populated, findings_hash verified)
             3. Orchestrator: Agent tool with model:sonnet 호출 → 응답 parse (§4.5.3 Sonnet 응답 schema)
                ├── decision=PASS|FIX → sonnet_final_status 채움, decision_state=decided, step 4 로 진행
                ├── decision=PACKET_REQUIRES_REVIEW_REOPEN → decision_state=review_reopen_requested, ReviewPL 재 spawn (1 회 한도 per (story_key,lane,iteration))
                └── timeout/malformed (Codex P1 #4) → decision_state=decider_timeout
                    └── Story §9 / §10 append 차단. §12 row append (decider_pick=<none>, audit_result=user-escalation, attempts[].outcome=timeout|malformed)
             4. Orchestrator self-write (decision_state=decided 일 때만):
                ├── Story §9 append (lane iteration result) — append-only, never rolled back
                ├── GitHub Issue/PR comment (lane-specific prefix per comment-prefix-registry-v1) via mcp__github__add_issue_comment
                ├── PASS 시: gate:*-pass label + phase:* 다음 단계 전환 via mcp__github__issue_write
                └── Story §12 Sonnet Decision Log row append
                
                **Partial-write policy (Codex P1 #5)**: 각 sub-step 별 idempotent retry (initial + 2 retry = 3 회 한도, Codex Round 2 gap fix). 실패 시 `writes_completed.<field>=false` + `write_errors[]` populate, decision_state=write_partial. **any required write 가 retry 한도 후에도 false 잔존 시 user escalation** (모든 required 가 아닌 1 건이라도 잔존 시 — Codex Round 2 gap fix wording 명확화). Story §9 + §12 는 append-only — 이미 append 된 내용 rollback 안 함. 외부 복구 후 다음 spawn 사이클에 missing write 재시도 가능 (write_partial → write_complete 전환).
             5. FIX 시 (sonnet_final_status=FIX):
                ├── Story §10 FIX Ledger append (decider: claude_sonnet, override marker if pl_recommendation != sonnet_final_status)
                ├── fix-ledger-sync.yml Action mirror (auto)
                └── DeveloperPL + ArchitectPL parallel diagnosis spawn (CFP-19 R4)
                
                **Spawn-failure policy (Codex P1 #6)**: §10 append 성공 + diagnosis spawn 실패 시 — §10 row 유지 (append-only), §12 append (audit_result=user-escalation, spawn_status=failed), 1 회 retry → second failure = user escalation. spawn 성공할 때까지 §10 row 는 "open FIX with no diagnosis" 상태로 visible.
                         → PASS 시 **2 트랙 병렬** (R7):
                            · Track A: Orchestrator post-Sonnet self-write (gate:design-review-pass 라벨 부착 + Phase 1 PR mergeable) → merge
                            · Track B: DeveloperPL spawn → Change Plan §5·§8 fetch + 첫 commit draft 준비 (PR open 보류)
                         → Track A merge 완료 시 Track B가 즉시 mcp__github__create_pull_request 호출
                         → 동시에 Orchestrator가 background SecurityTestPL prefetch 의뢰 → .claude-work/cache/<KEY>-sec1.json 생성
구현:        Orchestrator → (DeveloperPLAgent(role:dev roster 병렬) ∥ QADev) → 완료 보고
                         → §8.5 Impl Manifest DeveloperPL 이 직접 self-write (codeforge-develop self-write 표, R5)
                         → Orchestrator가 ArchitectPLAgent stateless 재스폰 → 매핑표 감사 (chief author 보조)
                         → §8.5 commit 시 subissue-from-impl-manifest.yml 자동 sub-issue 생성
구현 리뷰:   Orchestrator → CodeReviewPLAgent (lane=code packet 작성) → packet return (no writes — CFP-61 / ADR-022)
             **[D2-A CFP-2111] pr_phase 판정·주입**: 위 설계-리뷰 §D2-A 절차 동일 적용 (PR 변경 파일 패턴 → `pr_phase: phase2_impl` 보수 default).
             → Orchestrator가 한 메시지에 (ClaudeReviewAgent ∥ CodexReviewAgent) dispatch → PL 종합 → PASS/FIX (R3, R2)
             → PASS/FIX 결정: review-verdict 5-step algorithm 적용 (위 설계-리뷰 동일 흐름, lane=code, [구현-리뷰] prefix)
                         FIX 시 mechanical_category 자격 확인 → fast-path 또는 정상 cycle (R11)
구현 테스트: CI gate (ADR-048) — Orchestrator inline 수행:
                         `gh pr checks <PR_NUMBER> --watch` (timeout 30분)
                         → PASS + lanes.security_ai: false (default): merge gate 진입
                         → PASS + lanes.security_ai: true: SecurityTestPL spawn
                         → FAIL: `gh run view --log-failed` 수집 → FIX loop (DeveloperPL 1차 진단 → ArchitectPL 최종 판정)
통합 테스트: (Epic 하위 전체 Story CI gate PASS 후 1회 실행 — **상세: §3.11**)
보안 테스트: Orchestrator → SecurityTestPLAgent (lanes.security_ai: true 시만, lane=security packet 작성, 1차 layer cache hit/miss 확인)
             **[D2-A CFP-2111] pr_phase 판정·주입**: 위 설계-리뷰 §D2-A 절차 동일 적용.
             1차 layer: .claude-work/cache/<KEY>-sec1.json hit 시 inline 첨부 (R10) / miss 시 PL이 직접 fetch
             2차 layer: PL이 packet return → Orchestrator가 한 메시지에 (ClaudeReviewAgent ∥ CodexReviewAgent) dispatch → PL 종합 → PASS/FIX (R3, R2)
                         → PASS/FIX 결정: review-verdict 5-step algorithm 적용 (위 설계-리뷰 동일 흐름, lane=security)
                         → PASS 시 Orchestrator post-Sonnet self-write (gate:security-test-pass 라벨 부착) → Phase 2 PR mergeable
완료:        Phase 2 PR merge (`Closes #<Story Issue>`) → Issue 자동 close → PMOAgent 가 Story §11 직접 self-write (codeforge-pmo)
             → PMOAgent (회고)

[Epic 묶음 완료 후 — CFP-1059 / ADR-087+088, Phase 1 declarative]
배포:        Orchestrator → DeployPLAgent (codeforge-deploy plugin Phase 1 declare — 실 spawn = lane plugin seed 후) → 변경 repo enumeration + DeployWorkerAgent N 병렬 dispatch (repo 단위)
             각 repo 배포 sequence: blue-green 신호 → green deploy → healthcheck poll → atomic swap (Traefik label flip) → 3-시간 보존 timer → 자동 rollback 결정
             → §12 배포 manifest (codeforge-deploy self-write)
             FAIL (healthcheck / atomic swap / secret lookup): 자동 rollback + Story §10 FIX Ledger append (Orchestrator) + DeveloperPL 또는 ArchitectPL 1차 진단 routing
배포 리뷰:   Orchestrator → DeployReviewPLAgent (codeforge-deploy-review plugin Phase 1 declare, debate-protocol-v1 trigger 의무) → 검증 3종 병렬:
             - smoke 검증 (양방향 호환 — ADR-089 §결정 4 + bidirectional-smoke.yml workflow)
             - 성능 비교 (production runtime measure ↔ pre-deploy baseline — ADR-068 I-5 dimensional empirical grounding 정합)
             - cutover 사후 검증 (ProductionEvidenceDeputy ownership 이관 — codeforge-design CONDITIONAL → codeforge-deploy-review 정식)
             → §13 배포 검증 evidence (codeforge-deploy-review self-write)
             FAIL: 성능 미충족 / smoke 실패 시 FIX dispatch (DeveloperPL / ArchitectPL / RequirementsPL — debate-protocol-v1 multi-round adversarial debate 가능)
             PASS: Orchestrator self-write (gate:deploy-review-pass label + phase:완료 전환) → Epic 묶음 close
```

**Lane-specific write targets (Step 4 GitHub comment / label / phase 매핑)**:

| Lane | Comment prefix | Gate label (PASS) | Phase 다음 단계 |
|---|---|---|---|
| 설계-리뷰 | `[설계-리뷰]` | `gate:design-review-pass` | `phase:구현` |
| 구현-리뷰 | `[구현-리뷰]` | (none — flow continues) | `phase:구현-테스트` |
| 보안-테스트 | `[보안-테스트]` | `gate:security-test-pass` | (PR mergeable) |

상세 SSOT: comment-prefix-registry-v1 (CFP-61 갱신 — review verdict 작성자 = Orchestrator post-Sonnet) + label-registry-v1.

#### CI gate (구현 리뷰 PASS 후 — ADR-048)

구현 리뷰 PASS 직후 Orchestrator inline 수행 (read-only whitelist 예외):

```bash
gh pr checks <PR_NUMBER> --watch
```

- **timeout**: 30분. 초과 시 사용자에게 보고 후 대기.
- **PASS + `lanes.security_ai: false`** (default): merge gate 진입.
- **PASS + `lanes.security_ai: true`**: SecurityTestPL spawn (codeforge-review plugin).
- **FAIL**: 아래 명령으로 실패 로그 수집 후 FIX loop 진입.

```bash
gh run view --log-failed
```

FIX routing: DeveloperPL 1차 진단 (`gh run view` 출력 첨부) → ArchitectPL 최종 판정 → §10 FIX Ledger append.

**Worktree dispatch**: 매 lane spawn 시 worktree 자동 생성 — 상세는 §3.5

상세 분기 규칙은 CLAUDE.md "스폰 시퀀스" 섹션과 각 에이전트 md 참조.

### §3.11 Epic 통합테스트 게이트 (ADR-055 Amendment 2)

**트리거 조건**: Epic 하위 `stories_in_scope` 모든 Story의 CI gate PASS 확인.
단일 Story(non-Epic)는 해당 Story CI PASS 직후 동일 규칙 적용.

#### §3.11.1 IntegrationTestAgent spawn 패킷

```yaml
agent: IntegrationTestAgent (codeforge-test plugin, Sonnet tier)
context_packet:
  epic_key: <EPIC-KEY>
  stories_in_scope: [<STORY-KEY-1>, <STORY-KEY-2>, ...]
  story_8_6_contracts:
    - story_key: <KEY>
      contract_path: "docs/stories/<KEY>.md#§8.6"
  baseline_suite_path: <consumer overlay integration_test.baseline_suite_path>
  required_env_keys: <consumer overlay integration_test.required_env_keys>
  docker_compose_test_path: "docker-compose.test.yml"
```

#### §3.11.2 IntegrationTestAgent 실행 순서

1. **Deployability 검증** (실패 시 즉시 env_missing/infra_setup FIX 분기):
   - `.env` 필수 키 존재 확인
   - `docker-compose -f docker-compose.test.yml up --wait`
   - DB 연결 테스트
   - 각 서비스 health check endpoint 200 확인

2. **Story Suite 자동생성**: 각 Story §8.6 계약 읽기 → `tests/integration/stories/<EPIC-KEY>/<STORY-KEY>/test_*.py` 생성 (story_key metadata 태깅)

3. **Baseline Suite 실행**: `<baseline_suite_path>/` 전체 실행

4. **Story Suite 실행**: `tests/integration/stories/<EPIC-KEY>/` 전체 실행

5. **test-verdict-v2.1 패킷 생성** → Orchestrator에 반환

#### §3.11.3 결과 라우팅

| pl_recommendation | 처리 |
|---|---|
| `PASS` | Baseline 자동승격 → Epic State Ledger `integration_test.status = "pass"` → 보안테스트(opt-in) or Epic 완료 |
| `FIX` | `responsible_stories` 의 각 Story → failure_type별도 FIX loop (§결정 9) → FIX 완료 후 재spawn (max 3회) |
| `ESCALATE_PACKET_INCOMPLETE` | §8.6 누락 → TestContractArchitectAgent 의뢰, docker-compose 부재 → InfraEngineerAgent 의뢰 → 보완 후 재spawn |

#### §3.11.4 Baseline 자동승격 (PASS 시)

**IntegrationTestAgent 자체 수행** — Orchestrator inline 금지 (git commit 권한 = agent 소유).

```bash
# IntegrationTestAgent Mandate 7 (agent 내부 수행):
mkdir -p tests/integration/baseline/<STORY-KEY>
cp tests/integration/stories/<EPIC-KEY>/<STORY-KEY>/test_*.py \
   tests/integration/baseline/<STORY-KEY>/
# SUITE_TYPE = "story" → "baseline" 메타데이터 갱신 후:
git add tests/integration/baseline/
git commit -m "test(baseline): <EPIC-KEY> Story Suite 자동승격 — N개 케이스 추가"
```

Orchestrator는 verdict `pl_recommendation: PASS` 수령 후 Epic State Ledger `integration_test.status = "pass"` 만 갱신.

---

### §3.12 Epic State Ledger (ADR-055 Amendment 2 §결정 8)

Orchestrator는 Epic 진행 중 `.claude-work/epic-state/<EPIC-KEY>.yaml` 에 상태를 유지한다.

#### 파일 경로 규약

```
.claude-work/epic-state/
  CFP-NNN.yaml        # Epic 1개 = 파일 1개
```

#### Ledger 스키마

```yaml
epic_key: string                    # e.g. "CFP-373"
status: pending | in_progress | pass | fail
lock_holder: string | null          # 현재 write 중인 세션 ID (UUID 권장). null = unlocked
ledger_version: int                 # write 시마다 +1 (낙관적 CAS 용)
last_updated: ISO8601               # 마지막 write timestamp (KST `+09:00` zoned — display layer, ADR-079 §결정 2)
session_resume_hint: string | null  # 세션 재시작 시 다음 액션 힌트

stories:
  - key: string                     # e.g. "CFP-373-S1"
    status: pending | in_progress | ci_pass | fix_loop | done
    current_lane: string            # e.g. "구현리뷰"
    pr_number: int | null
    fix_count: int                  # 기본값: 0

integration_test:
  status: not_started | running | pass | fail | escalate
  verdict_ref: string | null        # test-verdict-v2.1 패킷 저장 경로 또는 GitHub comment URL
  last_run_at: ISO8601 | null
  rerun_count: int                  # 기본값: 0
```

**lock 사용 규칙**: Orchestrator는 ledger write 직전 `lock_holder`를 자신의 세션 ID로 설정, write 완료 후 `null`로 해제. 이미 non-null인 경우 5초 대기 후 재확인 (단일 Orchestrator 세션이 정상 케이스 — non-null 지속 시 stale lock, 강제 해제 후 진행).

#### Orchestrator 상태 업데이트 의무

| 이벤트 | 업데이트 필드 |
|---|---|
| Epic 생성 | 파일 초기화 (`stories` 목록 + `status: pending`) |
| Story lane 전환 | `stories[i].status`, `stories[i].current_lane` |
| Story PR 생성 | `stories[i].pr_number` |
| CI gate PASS | `stories[i].status = "ci_pass"` |
| FIX loop 진입 | `stories[i].fix_count++` |
| 통합테스트 시작 | `integration_test.status = "running"` |
| 통합테스트 완료 | `integration_test.status`, `verdict_ref` |

#### 세션 재시작 Resume 절차

세션 개시 체크리스트(§1.1) Step 0 이후:

1. `.claude-work/epic-state/` 디렉터리 스캔
2. `integration_test.status != "pass"` 또는 `stories[*].status != "ci_pass"` 인 파일 존재 시 사용자에게 진행 중인 Epic 목록 표시 → "이 Epic을 이어서 진행할까요?" 확인
3. 승인 시: `session_resume_hint` 읽어 다음 액션 결정 → 해당 Story/lane부터 재개
4. 거부 시: 신규 작업 대기

---

### 3.2 에이전트 프롬프트 표준 템플릿

**공통 블록** (모든 에이전트 스폰 포함):

```
[컨텍스트]
- Story Issue: #<N> (label: phase:<현재 라벨>)
- Story SSOT: docs/stories/<KEY>.md
- 참조 섹션: §{X}, §{Y}
- 관련 ADR (직접 제약 있을 때만 verbatim):
  {ADR 번호 + 1줄 요약}

[작업 지시]
{에이전트별 구체 지시 — 산출물·경계·완료 기준}

[복귀 보고 형식]
- TL;DR 1-3줄 + 상세 본문
- GitHub Issue 코멘트: 각 lane plugin 이 자기 phase prefix 로 직접 mcp__github__add_issue_comment 호출
  · 기록 형식: `[<phase>] <AgentName>: <요약>` + 상세 본문 + 원문 링크
- 산출물 경로: {파일 경로 또는 Story file 섹션 N 직접 Edit (각 lane plugin self-write 표)}

[제약]
- 문서화 표준은 각 lane plugin CLAUDE.md self-write 표 참조 — 자기 owner section 외 직접 write 금지
- {에이전트 권한·책임 경계 추가}
```

**에이전트별 특이 블록**:

| 에이전트 | 추가 블록 |
|----------|----------|
| **PMOAgent** | 스폰 트리거 명시 (Epic 창설 / Story 완료 / 사용자 요청), 감사 범위 지정 |
| **RequirementsPLAgent** | DomainAgent · Analyst · Researcher **병렬** 스폰 지시 (셋 다 non-skippable). 세 결과 dedup·상충 조정 후 Story file §3-6 반영. Clarification 재스폰 의뢰 권한 |
| **DomainAgent** | 사용자 원문 verbatim (Story file §1 복사) + 4소스 fetch 경로 (`docs/domain-knowledge/**` Glob+Read, `docs/adr/**` 도메인 카테고리, <domain-paths>/**, §1 원문). 타 에이전트 산출물 미수신 — 독립 키워드 자체 도출 |
| **RequirementsAnalystAgent** | 공통 입력(Story §1 + ADR)만 수신, 타 에이전트 해석 미포함. Ambiguity 키워드 섹션 생성 의무. codex CLI 필수 |
| **ResearcherAgent** | 사용자 원문에서 외부 기술·선행사례 관점 키워드 자체 도출, 타 에이전트 산출물 미수신. "조사 불필요" 판정도 명시 반환 (null skip 금지) |
| **ArchitectPLAgent** | 설계 lane PL. **6 permanent SubAgent** (SecurityArch / InfraOperationalArch / TestContractArch / DataArch / **ModuleArch** (aggregate-level 포함 — 구 AggregateArch, CFP-1126 통합) / **APIContractArch** — CFP-1086 / ADR-042 Amd 8, CFP-1126 / ADR-042 Amd 10) + 3 4-tuple sub-tuple (CodebaseMapper / Refactor / ArchitectAnalyst) flat spawn 후 ArchitectAgent (chief author) 통합 의뢰 → draft 검수. **CONDITIONAL SubAgent 추가 spawn 분기**: (a) ModuleArch applicability — `project.yaml aggregate_arch.applicable: false` 시 미spawn (frontend-only / API-only / external-managed consumer, CFP-1086 P2). (b) Live touching Story → +LiveOps + LiveOrdering. (c) Production cutover 영향 Story (Change Plan §13 `production_cutover_touching: true`) → +ProductionEvidence (CFP-632 / [ADR-72](../archive/adr/ADR-72-production-evidence-deputy-and-epic-cutover-gate.md)). Live touching + production cutover both = **최대 12 SubAgent** (6 permanent + 3 sub-tuple + LiveOps + LiveOrdering + ProductionEvidence). FIX 최종 판정자 (구현 리뷰·구현 테스트·보안 테스트 FAIL 시). Stateless 재스폰. **chief tie-break ladder 3 단계** (ADR-068 Amd 2): RACI lookup → ADR-068 invariant → chief judgement. **Deputy 신설 결정 framework** (ADR-086): axis 분석 + 5-checklist self-app + deferred carrier path. write queue 의뢰 권한 |
| **ArchitectAgent** | Change Plan §1-§13 chief author + ADR draft author + §8 Test Contract author + §11 데이터 마이그레이션 author. ArchitectPLAgent 산하 SubAgent. 입력 = **6 permanent SubAgent + 3 sub-tuple** 산출물 (Mapper / Refactor / ArchitectAnalyst / SecurityArch / InfraOperationalArch / TestContractArch / DataArch / ModuleArch / APIContractArch) + Story §1-7. `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md` + Story §3/§7/§11 **직접 write** (CFP-26 Phase 0a + codeforge-design self-write 표). Clarification 재스폰 의뢰 권한 |
| **CodebaseMapperAgent** | as-is 변호 역할 (4-tuple sub-tuple component). 매 설계 레인 진입 시 7 permanent deputy + Refactor + ArchitectAnalyst 와 병렬 재스폰, base_sha/scope_paths frontmatter. 타 SubAgent 산출물 미수신 — 원 소스 직접 독해 |
| **DataArchitectAgent** (CFP-1086 mandate 축소 — RDB OLTP 영역 제거 → 빅데이터 OLAP only) | 빅데이터 OLAP 영역 advocate. 매 설계 레인 진입 시 6 permanent deputy 와 병렬 재스폰. Parquet 파일 / 객체저장소 / DuckDB / streaming pipeline / 백필 / 시계열 집계 → chief author 가 Change Plan §3 OLAP + §11 OLAP 에 통합. RDB OLTP 영역은 ModuleArch primary 로 분리 (CFP-1086 / ADR-042 Amd 8, CFP-1126 / ADR-042 Amd 10) |
| *(AggregateArchitectAgent — CFP-1126 / ADR-042 Amd 10 폐기, ModuleArchitectAgent 로 boundary axis 통합)* | — |
| **APIContractArchitectAgent** (CFP-1086 신설 — skeleton at S1 / body 심화 = S2 별 PR) | API transport contract advocate. 매 설계 레인 진입 시 7 permanent deputy 와 병렬 재스폰. REST/GraphQL/gRPC/WebSocket + API versioning + DTO + OpenAPI/GraphQL schema + contract testing → chief author 가 Change Plan §3 API + §8 contract testing 에 통합. mandate body 심화 = Story-2 carrier (sequential prerequisite — S1 skeleton 위에 작성) |
| **ModuleArchitectAgent** (CFP-1086 — CodeArch rename + mandate 정정; CFP-1126 / ADR-042 Amd 10 — aggregate-level boundary axis 통합, 구 AggregateArch 폐기) | §3 code module-level 구조 + RDB OLTP aggregate invariant advocate. 매 설계 레인 진입 시 6 permanent deputy 와 병렬 재스폰. layered / hexagonal / clean / DDD bounded context module placement / module boundary / dependency direction + aggregate boundary / 트랜잭션 경계 / persistence-bound / Alembic 정책 7 원칙 → chief author 가 Change Plan §3 code + §11.1-§11.6 RDB OLTP 에 통합. consumer overlay `project.yaml aggregate_arch.migration_tool` 9-enum override (alembic default). CONDITIONAL applicability: `project.yaml aggregate_arch.applicable: false` 시 미spawn (CFP-1086 P2) |
| **RefactorAgent** | to-be 혁신 역할 (4-tuple sub-tuple component). 타 SubAgent 산출물 미수신, 원 소스 직접 독해. "잠재 변호 논리 예상" 섹션으로 self-identify한 충돌 지점 제출 (chief author 가 Mapper 실제 변호와 대조) |
| **ArchitectAnalystAgent** (CFP-1026 신설 — PriorArtAgent conceptual rename) | 변경 전 기존 설계 분석 단일 축 (4-tuple sub-tuple component). 매 설계 레인 진입 시 7 permanent deputy + Mapper + Refactor 와 병렬 재스폰. ADR / Change Plan / Story §3/§7/§11 분석 → chief author 가 Change Plan §2 컨텍스트 에 통합 |
| **SecurityArchitectAgent** | 설계 lane 보안 SubAgent (보안 boundary·auth·credential·crypto 전담; 운영 리스크는 InfraOperationalArch). 타 SubAgent 산출물 미수신, 원 소스 직접 독해. trust boundary·auth 모델·credential 흐름·암호학 결정에 대한 보안 설계 권고 산출 → chief author 가 Change Plan §7 (보안 설계 섹션, §7.1-§7.3·§7.5-§7.6; 외부 입력 무관 시 §7.7 N/A) 에 통합 |
| **InfraOperationalArchitectAgent** (CFP-1026 — OperationalRiskArch rename) | 설계 lane 운영 SubAgent (CFP-46 신설 — DR / cancel-on-disconnect / clock sync / rate limit / env isolation **design-time SSOT** 전담). 타 SubAgent 산출물 미수신, 원 소스 직접 독해. 운영 리스크 정책 결정 산출 → chief author 가 Change Plan §7.4 (6 sub-items 포함 Container) 에 통합 + §11.6 Idempotency CONDITIONAL 에 ModuleArch 와 consult (CFP-1086 — ModuleArch primary, InfraOpArch transactional 의미만 협업). **boundary axis** (CFP-632 / ADR-72 §결정 4): policy SSOT (본 SubAgent §7.4 invariant 정의) vs evidence SSOT (ProductionEvidenceDeputy production grounding subsection 실측 명시) 분리 |
| **ProductionEvidenceDeputyAgent** (CONDITIONAL — production cutover 영향 Story 만, CFP-632 / ADR-72) | 설계 lane production-grounding SubAgent. trigger = Change Plan §13 `production_cutover_touching: true` 선언 OR Live touching + production cutover both. 타 SubAgent 산출물 미수신, 원 소스 직접 독해. 책임 3종: (1) production evidence quad owner (bucket prefix listing + WAL sample + drainage rate + L2/L3 cadence trigger 4중) (2) EPIC CLOSED gate 검증 (3) post-cutover wiring inspection (compose.yml env / production deploy state / collector emit schema 실측 ↔ 가설 mismatch surface). chief author가 Change Plan §7.4 production grounding subsection 추가 + EPIC close PR retro epic_close_gate 의무. InfraOperationalArch §7.4 와 boundary axis 분리 (design-time policy vs runtime-evidence). Mandate matrix 7 cell overlap 71% — 양 측 consult 5 cell |
| **QADeveloperAgent** | Change Plan §8 Test Contract 입력. 매핑표 반환 의무 |
| **`role: dev` 에이전트** (DeveloperAgent·DataEng·InfraEng·preset·overlay) | 계획서 변경 금지 — 결함 발견 시 즉시 DevPL→ArchitectPLAgent 에스컬레이션 |
| **DesignReviewPLAgent** (codeforge-review plugin) | lane=design packet 작성 (codeforge-review plugin (plugins/codeforge-review/) 의 `templates/review-checklists/design.md` 인용 + scope_globs + category_enum + severity_overrides). Claude/Codex 통합 워커 병렬 스폰 후 종합. ADR 정합성 체크 P0 고정 |
| **CodeReviewPLAgent** | lane=code packet 작성. Claude/Codex 통합 워커 병렬 스폰 후 종합. DesignReviewPL과 공통 severity 규칙 (base 템플릿 SSOT) |
| **SecurityTestPLAgent** | (lanes.security_ai: true 시만) 1차 layer = Dependabot/CodeQL/Secret Scanning 결과 `gh api repos/*` 로 fetch → packet에 inline 첨부. 2차 layer = lane=security packet으로 Claude/Codex 통합 워커 병렬 스폰 후 종합. CI gate PASS 이후 진입 |
| **ClaudeReviewAgent / CodexReviewAgent** | lane-agnostic 워커 ([ADR-001](../archive/adr/ADR-001-review-agent-unification.md)). 호출 PL이 review packet으로 도메인(체크리스트·스코프·category enum·severity 자동 룰) 주입. packet 누락 시 ESCALATE 반환 — generic fallback 금지. 정규화 스키마 P0/P1/P2/P3 + lane 필드 반환. CodexReviewAgent는 codex-companion.mjs 실행 |
| *(DocsAgent — 부재, CFP-40 final delete. ζ arc 완료 후 각 lane plugin self-write 로 분산)* | — |

### 3.3 컨텍스트 주입 정책

- **Story file 경로 + 참조 섹션 번호**가 기본 — verbatim 복사 지양
- ADR **직접 제약**인 경우에만 프롬프트에 verbatim 포함
- 배경 참조 ADR은 Story file §3 링크로 충분
- 코드 경로는 Story file §4에 요약, 구체 내용은 `Read`/`Glob`/`Grep` 도구로 직접 접근

### 3.4 Cross-repo Epic 패턴 ([ADR-020](../archive/adr/ADR-020-cross-repo-epic-pattern.md) + Amendment 1 + 2)

mctrader 등 multi-repo consumer 의 cross-repo Epic 진행 시.

#### Epic 시작
1. consumer 가 Epic owner repo 결정 (doc-only hub repo 권장 — 예: mctrader-hub)
2. **Centralization mode 결정** ([ADR-020 Amendment 1](../archive/adr/ADR-020-cross-repo-epic-pattern.md) + Amendment 2 CFP-122):
   - **Mode A (repo-local)**: 각 작업 repo 가 자체 `docs/stories/<KEY>.md`. Implementation repo 가 자율 storyboard 운영 시.
   - **Mode B (hub-centralized)**: 1 hub repo 가 모든 child Story 보유, implementation repo 는 code PR 만. Doc-only hub + 도메인 ADR collocate 시 (mctrader 패턴).
   - **Mode C (mechanical Epic, NEW Amendment 2)**: Mode B special case. Phase 2-N 모든 PR 가 동일 mechanical content (file copy 동일 + acceptance 동일 + Sonnet 무발화 + parent Epic §5 표 enumerate). child Story Issue / per-lane spec 생략 허용. CFP-120 / CFP-121 Phase 2 사용 사례. PR body marker `mode: mechanical` 의무.
   - Mixed-mode 금지 — 단일 Epic 내 모드 일관 유지 (다른 Epic 은 다른 mode 가능).
3. parent Epic Issue 생성 (owner repo)
4. child Story 생성 — 선택된 mode 에 따라 hub 또는 각 작업 repo. Story §1 메타에 `epic_dependencies` graph 명시:
   ```yaml
   epic_dependencies:
     - type: hard_block | design_parallel | impl_parallel
       target: <KEY>
       repo: <owner/repo>
   ```
5. Change Plan §3 에 `consumes: { <producer>: <SemVer> }` 버전 고정 의무

#### Epic 진행
- **Topological merge order**: dependency graph 따라 producer 먼저 → consumer 나중
- `hard_block` 위반 detected 시 Epic 차단 (PMOAgent enforce)
- `design_parallel` / `impl_parallel` = 동시 진행 허용
- **Joint-phase PR 허용** (ADR-020 Amendment 1 §결정 9): 단일 Story 가 1 phase 안에서 multi-repo joint PR 보유 가능 (예: foundation Story 의 data + engine 동시 변경). 모든 PR 가 동일 Story key reference + dependency graph topological merge.

#### Epic Rollback
producer merge 후 consumer break 시:
1. Producer revert PR open
2. 모든 affected consumer 의 contract 버전 하향 고정 PR
3. Producer fix → 새 minor SemVer release
4. Consumer 버전 고정 갱신

#### Epic close — `EPIC-RESULTS-<EPIC_KEY>.md` artifact 의무 (CFP-83)

Epic close PR (Phase N+1) 동반 작성:

- **위치**: [`docs/doc-locations.yaml`](doc-locations.yaml) `epic_results` row 참조 ([ADR-041](../archive/adr/ADR-041-doc-location-registry.md)) — Mode A/B/C → `<scope>/docs/retros/` / dogfood → `<internal-docs>/<plugin-folder>/retros/` (Amendment 1 — CFP-288)
- **Template**: [`templates/epic-results.md`](../templates/epic-results.md) — 14 섹션 의무 (§1 child Story summary / §2 Phase decomposition / §3 Blocking AC / §4 Calibration AC / §5 Demonstration AC / §6 Codex review aggregate / §7 자율 결정 요약 (Sonnet decider) / §8 Out-of-scope / §9 CI iteration 통계 + 사용자 stop trigger 횟수 / §10 PR gate evidence / §11 후속 candidate 우선순위 / §12 debut-audit metric / §13 통계 / §14 결론)
- **작성자**: PMOAgent self-write (codeforge-pmo lane plugin owner)
- **mctrader 사례**: `mctrader-hub/docs/retros/EPIC-RESULTS-MCT-*.md` (Amendment 1 — root → docs/retros/)
- **§9 stop trigger 횟수** = ADR-025 + Amendment 1 (CFP-73 / CFP-80) stop discipline metric. 합법 stop whitelist 5종 외 stop = `policy_violation` defect 추적.
- **§10 PR gate evidence** = 향후 audit 시 GitHub API 라벨 verify fall-back evidence (Issue #181 P1-5 partial 해소)

#### Cross-references
- [ADR-020](../archive/adr/ADR-020-cross-repo-epic-pattern.md) + Amendment 1 + 2 (cross-repo Epic 패턴 SSOT — Mode A / B / C + Joint-phase narrow form)
- [requirements-output-v1.1](../docs/inter-plugin-contracts/requirements-output-v1.md) (Story §1 epic_dependencies field schema)
- [`consumer-guide.md`](consumer-guide.md) §5.1 (consumer 측 mode 선택 안내 — Mode A/B 비교표)

### §3.4.1 Multi-repo Story Routing (CFP-342 / ADR-069)

`project.yaml`의 `codeforge.stories.repos[]` 블록이 선언된 consumer에서 Orchestrator가 Story 작업 대상 repo를 결정하는 절차. [ADR-069](../archive/adr/ADR-069-multi-repo-story-key-system.md) §결정 4 SSOT.

#### Agent target repo 결정 우선순위 (4-step)

```
1. Frontmatter primary — story_scope: repo + repo: <name>
   → project.yaml repos[] 에서 name 매핑 → 해당 impl repo 직접 지정

2. Hub fallback — story_scope: hub
   → project.yaml 에서 role: governance repo 조회 → hub repo 작업

3. Component fallback (legacy / frontmatter 부재)
   → Issue label 'component:<name>' 검색
   → project.yaml repos[].components 매핑 검색
   → 단일 match → 해당 impl repo
   → N(>=2) match → ESCALATE (ambiguous)

4. ESCALATE — 1-3 모두 실패
   → Orchestrator 경유 사용자 명시 요청 (§2.3 ESCALATE 형식)
```

**Backward compat**: Story frontmatter 에 `story_scope` 없는 기존 Story (`legacy-hub`) 는 step 3 → component fallback 진입. component 매핑 부재 시 hub repo 묵시 처리 (단일 hub repo 가정).

#### Project Config Packet 확장

lane spawn 시 Orchestrator 가 subagent 에 주입하는 Project Config Packet ([§12 참조](#12-project-config-packet))에 `codeforge.stories` slice 추가:

```yaml
# Project Config Packet 추가 항목 (codeforge.stories 활성 시)
codeforge_stories_active: true
hub_repo: <name>                      # role: governance repo name
hub_github: <owner/repo>              # hub GitHub 좌표
repos:                                # impl repo 목록
  - name: <name>
    role: implementation
    path: <local-path>
    github: <owner/repo>
    story_dir: <story-dir>
    components: [<component>, ...]
counters_path: <path>                 # .codeforge/counters.json 위치
```

#### Story 생성 결정 로직

| 작업 유형 | 결정 | Story 위치 |
|---|---|---|
| Cross-repo 조율 (N repo 동시 영향) | Hub story 생성 (story_scope: hub) | hub repo / docs/stories/<KEY>.md |
| 단일 impl repo 작업 | Repo story 생성 (story_scope: repo) | <impl-repo-path>/docs/stories/<KEY>.md |
| Cross-repo + 구현 동시 | Hub story 먼저 → 각 impl repo story (delegates[]) | hub + impl 각자 |
| Legacy flat key (frontmatter 부재) | legacy-hub 처리 → hub repo | hub repo / docs/stories/<KEY>.md |

#### Bidirectional linking 의무 (AC-8)

- Hub story `delegates[]` 의 각 entry → 해당 repo story file 존재 여부 확인 (warn-only, block 아님)
- Repo story `hub_story` + `hub_repo` → hub story file 존재 여부 확인 (warn-only)
- Drift 발견 시: `[multi-repo-routing] WARN: delegate drift — <repo>#<KEY> 미존재` 형식으로 알림

#### Counter 발급 (Phase 2 자동화 — 현재 Phase 1 = manual)

Phase 1 (현재): 사용자가 `.codeforge/counters.json` 직접 관리. Orchestrator는 counter 값 읽어 KEY 결정 후 사용자에게 increment 안내.

Phase 2 (follow-up CFP): `scripts/codeforge-story-counter.py` 자동 발급 (file lock + atomic rename + reconciliation).

#### Cross-references
- [ADR-050](../archive/adr/ADR-020-cross-repo-epic-pattern.md) §결정 4 (Agent target repo 결정 priority SSOT)
- [ADR-020](../archive/adr/ADR-020-cross-repo-epic-pattern.md) Amendment 3 (본 시스템 = Mode B automation layer)
- [`consumer-guide.md`](consumer-guide.md) §3 (multi-repo story key 활성화 가이드)
- [`overlay/_overlay/project.yaml.example`](../overlay/_overlay/project.yaml.example) (codeforge.stories 블록 예시)

### §3.4.2 Parallel epic coordination (ADR-050 + Amendment 1 CFP-534)

복수 Orchestrator 세션 (두 개 이상 Claude Code 창) 이 서로 다른 Epic 을 병렬 진행할 때 충돌 조율 의무 SSOT.

**Epic Scope Manifest 작성 의무**: Phase 1 시작 시 Orchestrator 가 Epic Issue body 에 `<!-- scope_manifest -->` 블록 작성. GitOpsAgent 가 다른 open 에픽과 교집합 검사.

**필드 의미** (Amendment 1, CFP-534 — 3 신규 field 추가):

| Field | 의미 | 충돌 라벨 |
|---|---|---|
| `planned_adrs[]` | 예약 ADR 번호 (ADR-RESERVATION.md sequential append) | `conflict:adr-number` |
| `planned_files[]` | 예상 변경 파일 경로 | `conflict:file-overlap` |
| `planned_claude_md_sections[]` | CLAUDE.md / playbook 섹션 (section-ownership.yaml lookup) | `conflict:section-locked` |
| `planned_inter_plugin_contracts[]` (신규) | inter-plugin-contracts file 경로 (`MANIFEST.yaml` 포함) | `conflict:contract-overlap` |
| `planned_label_registry_bumps[]` (신규) | label-registry-v2.md version bump 의도 (`kind: MAJOR\|MINOR\|PATCH` + `scope`) | `conflict:registry-bump-overlap` |
| `cross_section_conflict_detection` (신규, default false) | cross-section 검사 활성 flag — true 시 frontmatter 3-location 의미 충돌 사전 경고 | (activation flag — 라벨 부여 0건) |

**GitOpsAgent intersection 검사 동작** (Amendment 1):

1. `parallel-epic-conflict-check.yml` workflow 가 변경 파일 lookup → `conflict:*` 라벨 자동 부여.
2. GitOpsAgent 가 양쪽 PR 에 `[GitOps]` prefix WARN comment 자동 발의 — 충돌 영역 / 상대 PR / merge-order / 권장 조치 명시.
3. lower CFP 번호 PR = `merge-order:1` 부여, 후순위 PR = `merge-order:2` + rebase 지시.
4. 미해결 시 PMOAgent sibling SendMessage → cross-Story hotspot 패턴 감지 → ADR 후보 발의 가능.

**Sentinel evidence (CFP-534)**: 2026-05-13 KST CFP-521 v2.4 vs CFP-429 v2.5 가 `docs/inter-plugin-contracts/label-registry-v2.md` frontmatter 3-location (`version` / `bumped_at` / `amendments[]` row) 동시 수정 → manual 15분 추가 + risk. Amendment 1 = 해당 사고 재발 방지 carrier.

**Cross-references**: [ADR-050](../archive/adr/ADR-050-parallel-epic-conflict-coordination.md) Amendment 1 / `templates/github-workflows/parallel-epic-conflict-check.yml` / `plugins/codeforge-pmo/agents/GitOpsAgent.md` §3.5 / `docs/parallel-work/section-ownership.yaml`.

### §3.5 Worktree dispatch (CFP-136 / ADR-040)

매 lane spawn 시 Orchestrator 가 worktree 생성 후 sub-agent 에 cwd 주입. file 충돌 0 보장.

**Lifecycle**:

1. **lane spawn 직전**:
   ```bash
   bash templates/scripts/worktree-create.sh cfp-NNN/<lane> origin/main
   # → returns worktree path: $HOME/.claude/worktrees/<repo>/cfp-NNN-<lane>
   ```
   하위 sub-task (SubAgent / role:dev) 가 있으면 sub-worktree 추가:
   ```bash
   bash templates/scripts/worktree-create.sh cfp-NNN/<lane>/<sub> cfp-NNN/<lane>
   ```

2. **sub-agent spawn 시**: prompt 에 `Working dir: <worktree-path>` 명시. sub-agent 가 cd 해서 작업.
   - **`git -C <worktree_abs_path>` 강제 directive (ADR-040 Amendment 6 / CFP-843)**: spawn prompt 에 "All file operations MUST target `<worktree_abs_path>` — git command = `git -C <worktree_abs_path> <subcommand>` (상대경로 git 호출 금지), Write/Edit tool = absolute path rooted at `<worktree_abs_path>`, path 정규형 = forward slash (cross-platform MSYS Git Bash 정합)" 1줄 의무. 근거: harness 가 bash 호출 간 cwd 를 reset → 상대경로 git/tool 호출이 main repo root 로 resolve → agent-internal write 가 main working tree 에 landing (CFP-825 §3 RC-1 동근원).

3. **sub-agent return 후**: Orchestrator 또는 sub-agent 가 자기 sub-branch 에 commit. Sequential merge:
   ```bash
   bash templates/scripts/worktree-merge.sh cfp-NNN/<lane> cfp-NNN/<lane>/<sub1> cfp-NNN/<lane>/<sub2>
   ```

4. **lane 완료 후**: parent (story root) branch 으로 merge:
   ```bash
   bash templates/scripts/worktree-merge.sh cfp-NNN cfp-NNN/<lane>
   ```

5. **Story 완료 후 (회고 시점, GitOpsAgent eager 정리 — primary 경로)**: 모든 sub-worktree prune. Orchestrator 가 완료 회고 단계에서 GitOpsAgent 를 dispatch (PMOAgent 회고와 동시/직후, agents/GitOpsAgent.md §5a):
   ```bash
   bash templates/scripts/worktree-prune.sh cfp-NNN/<lane>/<sub>
   bash templates/scripts/worktree-prune.sh cfp-NNN/<lane>
   ```
   Story root worktree 는 **PR merge 확인 후** prune:
   ```bash
   # 1) branch protection 감지
   PROTECTED=$(gh api "repos/$(gh repo view --json nameWithOwner --jq .nameWithOwner)/branches/main" --jq '.protected')
   # PROTECTED=true → merge 시도 금지, push → PR → mergedAt 확인 순서 필수
   # PROTECTED=false → local merge 후 바로 cleanup 가능

   # 2) PR merge 확인 (non-null mergedAt = merged) — PROTECTED=true 시 필수
   gh pr view <PR_NUMBER> --json mergedAt --jq .mergedAt

   # 3) mergedAt 확인 후 cleanup
   MAIN_ROOT=$(git -C "$(git rev-parse --git-common-dir)/.." rev-parse --show-toplevel)
   cd "$MAIN_ROOT"
   git worktree remove "$HOME/.claude/worktrees/<repo>/cfp-NNN"
   git worktree prune
   git branch -d cfp-NNN
   ```
   **branch-protected repo** (`PROTECTED=true`): push → PR 생성 → `mergedAt` 확인 → cleanup 순서 강제 (ADR-040 Amendment 2). pre-merge `git worktree remove` = policy violation.

**Conflict 처리**:
- worktree-merge.sh 가 conflict detect 시 exit code 2
- Orchestrator 가 conflict 받으면 chief author / 충돌 SubAgent sub-agent 재 spawn (cwd = parent worktree)
- 또는 PMOAgent escalation (CFP-139 GitOpsAgent 도입 후)

**주기 backstop (orphan 안전망 — eager 정리를 못 거친 worktree 전용)**:
- `bash templates/scripts/check-worktree-stale.sh` — **수동/스케줄 호출** (과거 SessionStart 동기 호출은 시작 지연으로 제거됨)
- 조건 = age 7d+ AND merged PR (**squash-aware**: 병합 PR headRefOid 이후 추가 commit 0) AND clean (임시파일 제외) AND not-locked
- preview = `GC_DRY_RUN=1` / bypass = `BYPASS_WORKTREE_GC=1`

**Cross-platform**:
- Windows: `${HOME}\.claude\worktrees\<repo>\<branch-flat>` (PowerShell or Bash via Git for Windows)
- macOS / Linux: `~/.claude/worktrees/<repo>/<branch-flat>`
- Path 변환은 `worktree-path-util.sh` 함수 (`is_windows`, `to_posix_path`).

**Marketplace sync PR proactive dispatch (CFP-597 / [ADR-063](../archive/adr/ADR-063-marketplace-atomic-invariant.md) Amendment 1)**:

Orchestrator 가 Phase 2 PR open 시점에 Change Plan §13 안 `marketplace_sync_required: true` declare 감지 시 GitOpsAgent (codeforge-pmo) spawn. spawn prompt:

**artifacts (verbatim 첨부, [ADR-070](../archive/adr/ADR-070-codex-verify-before-trust.md) verify-before-trust mandate)**:
- Change Plan §13 sub-row (`marketplace_sync_required` + `mirrored_fields_changed[]` + `triggering_plugins[]`)
- triggering plugin name + 변경된 mirrored field enum

**GitOpsAgent §3.6 행위** (codeforge-pmo sibling, Phase 2 carrier):
1. `mclayer/marketplace` repo worktree 신설 — branch `cfp-NNN`, base `main`
2. `.claude-plugin/marketplace.json` 안 해당 plugin entry 의 mirrored field 갱신 (`mirrored_fields_changed[]` 기준)
3. marketplace PR open — title `[CFP-NNN] Sibling sync — <plugin> <version> mirrored field update`
4. PR body 안 `Closes <triggering-plugin-PR>` cross-reference
5. ADR-063 §결정 2 ordering 정합 — marketplace PR 선행 merge 의무

dispatch trigger: Phase 2 PR carrier (Orchestrator monopoly, ADR-039 subagent default 정합). lane 위치 = codeforge-pmo (GitOpsAgent home, sibling plugin). reactive `check-marketplace-parity.sh` channel = defense-in-depth 보존.

**의존성**:
- ADR-024 amendment 1 (hierarchical branch convention)
- ADR-040 (worktree convention SSOT)
- CFP-137 (agent teams 적극 도입) — 본 §3.5 의 use case full
- CFP-139 (GitOpsAgent) — Orchestrator 의 worktree management 책임을 GitOpsAgent 로 이관 (Wave 3)
- CFP-597 (ADR-063 Amendment 1) — marketplace sync PR proactive dispatch trigger

#### §3.5.1 Parallel work sentinel polling (CFP-966 / [ADR-073 Amendment 2](../archive/adr/ADR-073-orchestrator-verify-before-assert.md))

> **NORMATIVE — ADR-073 Amendment 2 §결정 1-A/1-B/1-C declarative anchor**. lane spawn 직전 (§3.5 step 1) 시점에 적용되는 mid-flight parallel race 차단 polling 의무. mechanical wire (lint script + workflow + hook json sample) = sibling Story-2 CFP-967 carrier — 본 §3.5.1 = behavioral directive + declarative anchor (declaration-only-Wave-1 status).

**동인 (sentinel evidence)**: 2026-05-18 KST same-day 2/2 parallel race incidents — CFP-953 (first, label-based search miss → CFP-932 carrier miss) + CFP-946 (second, 11분 gap Epic close miss → PR #962 "Closes #946" 충돌). long-running Orchestrator session 의 turn-0-only SessionStart snapshot staleness 영역.

**Transition trigger enum 3종 (closed set)** — 각 transition 직전 polling 의무:

| ID | 발화 시점 | Polling 의무 |
|----|---|---|
| `lane_spawn` | lane 진입 직전 (§3.5 step 1 — Agent tool spawn 직전) | title-based search + Epic state poll + HEAD compare |
| `pr_open` | PR open 직전 (`gh pr create` 직전, Phase 1 / Phase 2 / retro PR) | 동일 3-step + sibling Story PR list cross-ref |
| `merge_transition` | PR merge 직전 (`gh pr merge` 직전) + 직후 (gate label / phase label transition 직전) | 동일 3-step + Epic state final poll (close eligibility check) |

closed enum — 4번째 trigger 추가 = ADR-073 Amendment 강화 방향만 (ADR-058 §결정 5 / ADR-064 §결정 7 top-down ratchet 정합).

**HEAD compare pattern (verify-before-trust 4-layer governance Layer 1)** — 매 transition trigger 직전 3-step 의무:

```bash
# Step 1 — title-based search (memory rule 6 의무, CFP-953 incident carrier)
gh issue list --search "<keyword>" --state all --json number,title,labels,closedAt
# label-based search 만 (rule 6 위반) → CFP-953 incident reproduction risk

# Step 2 — Epic state poll (memory rule 7 의무, CFP-946 incident carrier)
gh issue view <epic_number> --json state,closedAt,closedBy,labels
# polling 직전 5+ min 경과 session state cache (TodoWrite / Story §0 / .claude-work/progress) 무조건 stale 가정

# Step 3 — HEAD compare sibling commits (mid-flight race 차단)
PRIOR_HEAD=<session state cache 의 pinned HEAD — stale 가능>
CURRENT_HEAD=$(git ls-remote origin <branch> | cut -f1)   # direct verify (재고정)
gh api repos/{owner}/{repo}/compare/${PRIOR_HEAD}...${CURRENT_HEAD} --jq '.commits[].sha'
```

**Cold start `session_start` 보강**: session 첫 turn additionalContext 안 active CFP context list + open Epic state list + current branch HEAD vs origin/main delta 3-item preload (SessionStart hook tier 위임 — Story-2 CFP-967 `templates/.claude/hooks/SessionStart-parallel-work-poll.json.sample` mechanical wire). additionalContext = layer 1 fallback 만 — actual sustained polling = 매 transition trigger 직전 §3.5.1 3-step.

**Sustained in-session polling 의무**: turn-0-only SessionStart hook 한계 해소 — long-running session 안 매 transition trigger 직전 HEAD SHA 재고정 의무 (session state cache stale 무조건 가정).

**Cross-ref**:
- [ADR-073 Amendment 2](../archive/adr/ADR-073-orchestrator-verify-before-assert.md) §결정 1-A/1-B/1-C — declarative anchor SSOT
- `docs/evidence-checks-registry.yaml` `parallel-work-sentinel-pickup` entry — warning tier (declaration-only-Wave-1, recurrence count 2 / threshold 3 / promotion_trigger auto_blocking)
- [`docs/domain-knowledge/domain/orchestrator-discipline/parallel-work-sentinel-polling.md`](../docs/domain-knowledge/domain/orchestrator-discipline/parallel-work-sentinel-polling.md) — narrative SSOT (sentinel batch + escalation matrix)
- memory rule 6 (title-based search 의무, CFP-953 carrier) + rule 7 (Epic 진행 중 polling 의무, CFP-946 carrier) — declarative cross-ref normative anchor
- sibling Story-2 [CFP-967](https://github.com/mclayer/plugin-codeforge/issues/967) — mechanical wire (script + hook + workflow + bats), sequential (Story-1 merge 후)

#### §3.5.2 Cross-repo worktree target authority verify (CFP-1578 / [ADR-082 Amendment 21](../archive/adr/ADR-082-write-time-self-write-verification-mandate.md) §결정 1 sub-scope 1-J)

> **NORMATIVE — ADR-082 Amendment 21 §결정 1 layer 1 sub-scope (1-J) declarative anchor**. chief author / lane agent / Orchestrator 가 spawn prompt 작성 또는 직접 file write 직전 cross-repo worktree target authority verify-before-write 의무. mechanical wire (lint script + workflow + hook json sample + bats fixture) = 별 sub-CFP Wave 2 carrier — 본 §3.5.2 = behavioral directive + declarative anchor (Wave 1 declaration-only).

**동인 (sentinel evidence)**: CFP-1539+CFP-1540 batch retro §4.1 #2 — PMOAgent retro spawn 시 internal-docs PR target 작성 시 wrapper repo plugin-codeforge worktree 안에서 `git worktree add` 시도 후 정정 발생. wrapper repo worktree mis-target 첫 catch occurrence. ADR-013 dogfood-out internal-docs SSOT path (Story file + Change Plan + retro = internal-docs) + ADR-040 worktree convention (repo 단위 worktree 분리) 정합 영역 codify 부재. paired sibling = CFP-1559 Amendment 20 (Issue body stale claim pre-screen super-class, axis disjoint — content verify vs target authority verify, 동시 발의 race).

**4-tuple primitive (cross-repo write-target boundary mandate)** — spawn prompt 작성 또는 직접 file write 직전 4 의무:

| ID | Primitive | 동작 |
|----|---|---|
| (a) | worktree target authority verify-before-write | `git -C <worktree_abs_path> remote -v` 실행 → expected repo (예: wrapper plugin-codeforge vs internal-docs) 와 actual remote URL 일치 확인. mismatch 시 write 차단 + sentinel 발화 |
| (b) | spawn prompt 안 `worktree_target_repo: <expected-repo-name>` field | write-target authority anchor block 형식 명시 (sub-scope 1-C `[USER-UTTERANCE-VERBATIM]` + 1-E `[PRE-SPAWN-ORIGIN-MAIN-SHA]` block precedent 답습). enum = `wrapper` / `internal-docs` / `marketplace` / `consumer-<name>` |
| (c) | cross-repo 작업 sequence 시 명시적 worktree switch | wrapper repo worktree 안에서 internal-docs PR 생성 시도 금지 (repo 단위 worktree 분리, ADR-040 정합). cross-repo write 필요 시 별도 worktree explicit create + cwd switch + write 의무 |
| (d) | verified-via annotation `worktree_target_authority_verified: <bool>` | spawn prompt 안 명시 (write-time semantic truth verify, annotation 부재 시 sentinel 발화) |

**Verify pattern (verify-before-trust 4-layer governance Layer 3 — ADR-082 sub-scope 1-J)**:

```bash
# Step 1 — worktree target repo authority verify (mandate (a))
ACTUAL_REMOTE_URL=$(git -C <worktree_abs_path> remote get-url origin)
# expected = wrapper plugin-codeforge → "mclayer/plugin-codeforge"
# expected = internal-docs → "mclayer/codeforge-internal-docs"

# Step 2 — expected target enum 일치 verify (mandate (a))
EXPECTED_REPO="wrapper"   # spawn prompt field (b) 에서 declare
case "$EXPECTED_REPO" in
  wrapper) EXPECTED_URL_PATTERN="mclayer/plugin-codeforge" ;;
  internal-docs) EXPECTED_URL_PATTERN="mclayer/codeforge-internal-docs" ;;
  marketplace) EXPECTED_URL_PATTERN="mclayer/marketplace" ;;
  consumer-*) EXPECTED_URL_PATTERN="mclayer/${EXPECTED_REPO#consumer-}" ;;
esac
if ! echo "$ACTUAL_REMOTE_URL" | grep -q "$EXPECTED_URL_PATTERN"; then
  echo "ERROR: worktree target mismatch — expected $EXPECTED_REPO ($EXPECTED_URL_PATTERN), got $ACTUAL_REMOTE_URL"
  exit 1
fi

# Step 3 — cross-repo write 시 별 worktree switch (mandate (c))
# wrapper worktree 안에서 internal-docs PR 생성 시도 = mismatch → step 2 차단
# 필요 시 internal-docs 별 worktree 생성:
# git -C /path/to/internal-docs-repo worktree add <internal-docs-worktree> <branch>
```

**Cold start sentinel**: session 첫 turn 직후 active worktree list scan + worktree↔expected-repo 매핑 확인 (SessionStart hook tier 위임 — Wave 2 sub-CFP `templates/.claude/hooks/SessionStart-worktree-target-verify.json.sample` mechanical wire). actual sustained verify = 매 spawn prompt 작성 또는 file write 직전 §3.5.2 mandate.

**Cross-ref**:
- [ADR-082 Amendment 21](../archive/adr/ADR-082-write-time-self-write-verification-mandate.md) §결정 1 layer 1 sub-scope (1-J) — declarative anchor SSOT
- [ADR-040 worktree convention](../archive/adr/ADR-040-worktree-convention.md) — namespace 표준 (`${HOME}/.claude/worktrees/<repo-name>/<branch-flat>`) + worktree-first normative 정합
- [ADR-013 dogfood-out internal-docs SSOT](../archive/adr/ADR-013-codeforge-family-dogfood-out-policy.md) — Story file + Change Plan + retro = internal-docs / src + tests + workflow + ADR + CLAUDE.md = wrapper plugin-codeforge
- `docs/evidence-checks-registry.yaml` `worktree-target-authority-verify` entry — warning tier deferred-followup (Wave 2 sub-CFP wire)
- paired sibling CFP-1559 Amendment 20 — Issue body stale claim pre-screen super-class, axis disjoint (content verify vs target authority verify, 동시 발의 race)
- 동인: CFP-1539+CFP-1540 batch retro §4.1 #2 — worktree mis-target 첫 catch carrier

#### §3.5.3 Version race coordination sequential merge orchestration (CFP-1603 / [ADR-045 §D-9](../archive/adr/ADR-045-story-retro-mandatory-trigger.md) pattern_count 2 escalation_resolved_carrier)

> **NORMATIVE — ADR-045 §D-9 forcing function 산출 declarative anchor** (escalation_action: `escalate_user`, escalation_resolved_carrier: CFP-1603). same-day multi-Story plugin.json version bump 영역 의 race resolution sequence orchestration codify. mechanical wire (workflow lint + bats fixture) = 별 sub-CFP Wave 2 carrier — 본 §3.5.3 = behavioral directive + declarative anchor (Wave 1 declaration-only).

**동인 (sentinel evidence, pattern_count 2 reach)**:

| # | Occurrence | Story batch | Race semantic |
|---|---|---|---|
| 1 | Wave 2 batch (2026-05-25 KST 전반) | CFP-1559 PATCH (6.7.3) + CFP-1540 (sentinel script cp949 fix) | sentinel script invocation reliability fix sibling (race coordination axis disjoint — first occurrence carrier) |
| 2 | Wave 3 batch (2026-05-25 KST 후반) | CFP-1580 MINOR (6.8.0) + CFP-1559 rebase (6.7.3 → 6.8.1) | 양 PR same base SHA (6.7.2) target → race resolution sequence: #1580 선행 merge (MINOR > PATCH per ADR-037 §결정 1) → #1559 rebase 6.7.3 → 6.8.1 PATCH + marketplace sibling sync |

ADR-045 §D-9 pattern_count ≥ threshold 2 reach = Mandatory framing 발동 영역 (PMOAgent retro 산출 evidence). 본 carrier = `escalation_action: escalate_user` resolution (declarative-only Wave 1 codify), Wave 2 mechanical wire = 별 sub-CFP.

**Race detection criteria (same-base-SHA primitive)**:

| ID | Criterion | Trigger |
|----|---|---|
| (a) | same-base-SHA + same-mirrored-field | 복수 Story (동일 또는 별도 Orchestrator session) plugin.json `.version` field bump target 이 동일 base SHA (예: 6.7.2) 인 경우 — sentinel polling §3.5.1 `lane_spawn` / `pr_open` transition trigger 직전 HEAD compare step 에서 자연스럽게 detect |
| (b) | same-day multi-Story batch | session boundary 와 무관 — 동일 base SHA target 시 race 활성 (ADR-040 worktree convention 정합, Story 단위 worktree 분리) |
| (c) | marketplace sibling sync trigger 동반 여부 | mirrored field (`name` / `version` / `description` / `author`) 변경 시 marketplace sibling PR 동반 — ADR-063 §결정 2 ordering 활성. 변경 0 시 sequential ordering 4-step → 2-step 축소 (mandate 5 fallback) |

**Sequential merge orchestration sequence — 4-step (full path, marketplace sibling sync 동반 시)**:

```
선행 PR (MINOR, 예 6.8.0) + 후행 PR (PATCH, 예 6.7.3) same base SHA 6.7.2 target

Step 1 — 선행 marketplace sibling PR merge (선행 PR mirrored field MINOR mirror)
  · marketplace.json `.plugins[name=codeforge].version` 6.7.2 → 6.8.0 sync
  · ADR-063 §결정 2 ordering 정합 — marketplace PR 선행 merge

Step 2 — 선행 plugin PR merge (MINOR 6.8.0)
  · plugin.json `.version` 6.7.2 → 6.8.0 atomic (3-file invariant ADR-063 §결정 1)
  · CHANGELOG.md `[Unreleased]` → `[6.8.0]` released entry transition

Step 3 — 후행 plugin PR rebase + version bump 재계산 (6.7.3 → 6.8.1)
  · git rebase origin/main (base SHA 6.7.2 → 6.8.0)
  · plugin.json `.version` 6.7.3 → 6.8.1 재bump (SemVer monotonic invariant: PATCH 6.7.3 < MINOR 6.8.0 < PATCH rebased 6.8.1)
  · CHANGELOG.md `[Unreleased]` merge conflict resolve — chronological append (선행 6.8.0 entry 위, 후행 entry 아래) OR 후행 별 sub-section
  · 후행 marketplace sibling PR (PATCH rebased 6.8.1 mirror) rebase 동반

Step 4 — 후행 marketplace sibling PR merge → 후행 plugin PR merge (PATCH 6.8.1)
  · marketplace.json `.plugins[name=codeforge].version` 6.8.0 → 6.8.1 sync
  · plugin.json `.version` 6.8.1 atomic
```

**Sequential merge orchestration sequence — 2-step (marketplace sibling sync 부재 축소 path)**:

```
선행 PR + 후행 PR mirrored field 변경 0건 (예: doc-only fast-path Story batch)

Step 1 — 선행 plugin PR merge
  · plugin.json 변경 0, CHANGELOG.md `[Unreleased]` entry 추가

Step 2 — 후행 plugin PR rebase + merge
  · git rebase origin/main (선행 PR merge commit 포함)
  · CHANGELOG.md `[Unreleased]` merge conflict resolve — chronological append
  · plugin.json bump 0건 (race coordination orchestration 자체는 mirrored field 변경 0 시에도 적용 — base SHA 변경 시 후행 PR rebase 의무)
```

**ordering invariant (MINOR > PATCH > PATCH per ADR-037 §결정 1 정합)**:

```
race resolution priority:
  MAJOR > MINOR > PATCH

동일 surface category (예: PATCH + PATCH) race 시:
  lower CFP 번호 선행 merge (ADR-050 §3.4.2 patterns 답습)

후행 PR rebase 후 bump 재계산:
  base 변경분 + 후행 PR 변경분 합산 → SemVer monotonic 보장
  · MINOR + PATCH = MINOR rebased to MINOR.MINOR+1.0 OR PATCH (semantic preserve)
  · PATCH + PATCH = PATCH rebased to next PATCH
  · MAJOR + MINOR = MAJOR rebased to MAJOR.MINOR+1.0 (ADR-063 Amendment 7 §결정 18 9-plugin atomic MAJOR scope 정합 시 atomic bundle 의무)
```

**Race resolution example (Wave 3 evidence verbatim, 2026-05-25 KST)**:

| Step | Actor | Action | Resulting state |
|------|---|---|---|
| 1 | Orchestrator | sentinel polling §3.5.1 `pr_open` transition direct verify | #1580 (MINOR 6.8.0) + #1559 (PATCH 6.7.3) both target base 6.7.2 — race detected |
| 2 | Orchestrator | ADR-037 §결정 1 ordering decide — MINOR 선행 | #1580 first merge order assigned |
| 3 | GitOpsAgent (codeforge-pmo §3.6) | marketplace sibling PR #1580-marketplace open + merge | marketplace.json 6.8.0 sync |
| 4 | Orchestrator | #1580 plugin PR merge | plugin.json 6.7.2 → 6.8.0, CHANGELOG `[Unreleased]` → `[6.8.0]` |
| 5 | Orchestrator | #1559 rebase + version bump 재계산 | plugin.json 6.7.3 → 6.8.1, CHANGELOG `[Unreleased]` entry chronological append |
| 6 | GitOpsAgent | marketplace sibling PR #1559-marketplace rebase + merge | marketplace.json 6.8.0 → 6.8.1 sync |
| 7 | Orchestrator | #1559 plugin PR merge | plugin.json 6.8.0 → 6.8.1 atomic |

**Wave 2 mechanical wire carrier (declaration-only Wave 1 retain — Wave 2 별 sub-CFP)**:

- workflow lint — same-day multi-Story plugin.json version bump 영역 sequential merge ordering 자동 verify (별 sub-CFP, evidence-checks-registry `version-race-coordination-ordering` entry 후보)
- bats fixture — race resolution scenario coverage (MINOR+PATCH / PATCH+PATCH / MAJOR+MINOR / marketplace 부재 축소 4 case)
- `mechanical_enforcement_actions: []` declaration-only-Wave-1 (ADR-082 §결정 6 + ADR-070 §D5 retain pattern 답습)

**Cross-ref**:

- [ADR-037 §결정 1 plugin version bump rule](../archive/adr/ADR-037-plugin-version-bump-rule.md) — SemVer monotonic invariant + Option β core rule (Lenient base, 12 surface category) upstream policy SSOT
- [ADR-063 §결정 1/§결정 2 marketplace atomic invariant](../archive/adr/ADR-063-marketplace-atomic-invariant.md) — 3-file atomic invariant + marketplace sibling sync ordering upstream policy SSOT
- [ADR-045 §D-9 cross_story_pattern_adr_trigger](../archive/adr/ADR-045-story-retro-mandatory-trigger.md) — forcing function SSOT (pattern_count threshold 2 → escalate_user → 본 §3.5.3 codify carrier)
- [ADR-050 §3.4.2 Parallel epic coordination](../archive/adr/ADR-050-parallel-epic-conflict-coordination.md) — Epic-scope conflict detection (axis disjoint, PR-level post-hoc) cross-ref
- §3.5.1 Parallel work sentinel polling — race detection mechanism (sentinel polling `pr_open` / `merge_transition` transition trigger 가 race detect)
- [ADR-024 §3 sequence-of-singletons](../archive/adr/ADR-024-story-scoped-branch-policy.md) — trunk-based branching axis (release branch 부재, main-direct PR sequential)
- §3.6 marketplace sync PR proactive dispatch (CFP-597 / ADR-063 Amendment 1) — GitOpsAgent §3.6 행위 (sibling axis disjoint, marketplace sibling sync proactive dispatch vs race resolution sequence orchestration)
- 동인: ADR-045 §D-9 pattern_count 2 reach (Wave 2 + Wave 3 batch sentinel evidence) escalation_resolved_carrier

### §3.6 TeamCreate / TeamDelete protocol (CFP-137 / [ADR-044](../archive/adr/ADR-044-phase-scoped-sequential-team.md))

> **Activation**: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` env 활성 시에만 본 §3.6 적용. env=0 또는 미설정 시 = ADR-039 default subagent context fallback (§3.0 + 기존 §3.1 one-shot Agent tool 패턴).

매 lane 진입 시 Orchestrator (영구 lead) 가 다음 sequence 수행:

```
1. Preflight check (§3B)
2. (CFP-139 후) GitOpsAgent SendMessage — lane worktree 준비 (§3.5 lifecycle)
3. TeamCreate(team_spec=templates/team-spec-<lane>.yaml, worktree=<path>)
   - team-spec yaml 7종 SSOT (ADR-044 §결정 2)
   - Codex worker dispatch_mode=user_request_only — 사용자 explicit request 시에만 활성
4. lane 진행:
   - Lane PL → teammate dispatch (TaskCreate)
   - teammate ↔ teammate SendMessage (Adversarial / Cross-layer 패턴)
   - PL 중재 + dedup → pl_recommendation
5. TeamDelete (in-flight teammate 완료 명시 wait — TeamDelete 시점에 in-flight task 가 있으면 platform 이 자동 wait, Orchestrator 는 추가 polling 미필요)
6. Orchestrator self-write (Story §9 + GitHub gate label + phase transition — review-verdict v4 4-step algorithm)
7. FIX 시 → TEAM-FIX 새 team (parallel diagnosis: DeveloperPL + ArchitectPL)
```

**Lead = Orchestrator** (Story 전 기간 fixed). One-team-per-lead 강제 — 다음 lane TeamCreate 전 현 team `TeamDelete()` 의무.

**team-spec yaml 7종**: `templates/team-spec-{decompose,requirements,design,design-review,develop,code-review,security-test}.yaml`. 구현 테스트 lane = CI gate (ADR-048, team 미생성 — Orchestrator inline `gh pr checks`).

### §3.7 SendMessage 사용 패턴

> **Activation**: env=1 시에만 SendMessage 발화. env=0 시 fallback = Orchestrator round-trip (PL ↔ worker continuous dialog 부재).

**Adversarial debate 패턴** (TEAM-{DESIGN,CODE,SECURITY}-REVIEW, Codex worker 활성 시):

```
1. PL → ClaudeReviewAgent: "primary review pass — 모든 finding 수집"
2. ClaudeReviewAgent → PL: findings packet (round 1)
3. PL → CodexReviewAgent: "Claude packet 검수 + 누락 찾기"
4. CodexReviewAgent → ClaudeReviewAgent (직접 SendMessage): "P1 #3 finding 의 evidence 부족 — file:line cite 추가"
5. ClaudeReviewAgent → CodexReviewAgent: "evidence 추가, 또한 P0 #2 도 보강"
6. PL ↔ both workers: dedup + severity 합의
7. PL → Orchestrator: review-verdict v4 packet (worker_dialog_rounds = 5, ADR-044 §결정 5 measurable)
```

**Cross-layer 패턴** (TEAM-DEVELOP, dev ↔ QA):

```
1. PL → QADev: "Impl Manifest 매핑표 작성"
2. QADev → PL: 매핑표 v1
3. PL → role:dev (e.g., SoftwareDeveloperAgent): "feature X 구현"
4. role:dev → QADev (직접 SendMessage): "test fixture <path> 의 boundary case 추가 권유"
5. QADev → role:dev: "fixture 갱신 — invariant 가 valid 한지 확인 required"
6. PL → develop-output v1.1 packet (cross_layer_dialog_rounds = 2, ADR-044 §결정 5 measurable — codeforge-develop sibling sync follow-up)
```

**Sequential-dialog 패턴** (Stage 0 [TEAM-DECOMPOSE], TEAM-DECOMPOSE):
- PMOAgent + (CFP-139 후) GitOpsAgent 단순 sequential — Adversarial 부재.

### §3.8 TeammateIdle nudge protocol

> **Activation**: env=1 시에만 TeammateIdle hook 발화.

idle teammate 감지 시 platform 이 본 hook trigger:

```
[Hook fires]
  └─ PL 수신: idle teammate name + last_task_completed_at
       ├─ option A: PL → idle teammate SendMessage (추가 task dispatch)
       │   예: TEAM-DESIGN 의 RefactorAgent idle 시 "추가 boundary 검토"
       └─ option B: PL → Orchestrator SendMessage: "TeamDelete 권유 — 모든 teammate finished"
            └─ Orchestrator → TeamDelete (in-flight wait + worktree merge orchestration)
```

Sample hook = `templates/agent-teams-hook-samples/TeammateIdle.json.sample` (ADR-044 §결정 3). Phase 2 PR scope = nudge logic + script 실제 구현.

### §3.9 env-divergent context fallback (default ↔ enabled context 분기)

| env | 동작 |
|---|---|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` | §3.6 + §3.7 + §3.8 활성. team-spec yaml 7종 본격 사용. SendMessage / TaskCreate / TeammateIdle hook 발화. |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0` 또는 미설정 | ADR-039 default subagent context fallback. Orchestrator 가 lane PL 1개만 spawn (one-shot Agent tool). PL 이 sub-agent 재 spawn 매 round Orchestrator 경유. SendMessage / TeamCreate / TaskCreate / TeammateIdle hook 미발화. team-spec yaml 미사용. review-verdict v4 의 worker_dialog_rounds = 0 (Adversarial 패턴 mechanism level 부재). |

**Backward compat 보장**: env=0 사용자 = 본 CFP-137 도입 후에도 ADR-039 + 기존 §3.1 one-shot 패턴 그대로 동작. 본 CFP-137 의 Phase 1 PR merge 시점에 env=0 사용자 영향 0.

**Hook 등록 의무 (env 무관)**: `templates/agent-teams-hook-samples/{TeammateIdle,TaskCreated,TaskCompleted}.json.sample` 3종 sample 은 consumer 측 `.claude/hooks/` 로 install 가능 — env=0 시 trigger 미발화이지만 install 자체는 무해 (Anthropic platform 이 env 기반 자동 분기). consumer-guide §"Agent teams 적극 도입 (CFP-137)" install 안내 정합.

---

### §3.10 Codex Proactive Check (CFP-354 / [ADR-052](../archive/adr/ADR-052-codex-proactive-check-touchpoints.md))

Orchestrator가 6개 touchpoint에서 `codex:codex-rescue` subagent를 **proactive check** 용도로 자동 dispatch. 기존 `codex:rescue`(사후 대응 — stuck 시) 채널과 분리.

**Dispatch 패턴**:

```text
Agent(subagent_type="codex:codex-rescue", prompt=<ProactiveCheckPacket>)
```

**Codex CLI worker check file-redirect dispatch mandate** (CFP-1244 / [ADR-081 Amendment 6](../archive/adr/ADR-081-codex-worker-prompt-boilerplate.md) §결정 D8 + [ADR-052 Amendment 12](../archive/adr/ADR-052-codex-proactive-check-touchpoints.md)):

codeforge Orchestrator/lane 이 Codex CLI worker check 를 invoke 할 때 (Codex CLI v0.125.0 확인):

1. **file-redirect invocation 의무** — composed worker prompt (D1.A-D 4 mandatory boilerplate field 포함) 를 file 로 write 후 file-redirect 형식 `codex exec --sandbox read-only < <promptfile>` 로 invoke. direct stdin-pipe (prompt 를 stdin 직접 pipe) / inline-arg invocation 금지 — TTY 부재 sandbox 안 0-byte stall (>5min) systemic 원인 (CFP-1187 운영 phase Epic S4/S5 early stall evidence).
2. **result-via-file 수신 + synchronous block-wait 금지** — Codex worker 결과는 output file 경유 수신. Orchestrator 는 Codex stream 을 bounded window 초과 synchronous block-wait 금지 — bounded window 초과 시 다음 step 진행 후 result file pickup (CFP-1187 S7 ArchitectPL stream idle-timeout after 40 tool_uses → redo evidence 차단).
3. **stall / stream idle-timeout 시 substitution** — file-redirect invocation 후에도 stall / stream idle-timeout 발생 시 substitution path `fallback_skip_with_marker` 진입 + Story §10 marker `[codex-sandbox-fallback: dispatch_stall_or_stream_timeout]` (fail-mode enum 8번째 value, ADR-070 Amendment 7 / ADR-052 Amendment 12).

dispatch invocation mandate 본문 SSOT = ADR-081 §결정 D8.

**ProactiveCheckPacket 스키마**:

```yaml
touchpoint: <1|2|3|4|5|6>
purpose: <한 줄 목적>
context:
  lane: <requirements|design|develop|orchestrator>
  story_key: <CFP-NNN>
  artifacts: <첨부 산출물 — verbatim content 의무, CFP-578 / ADR-070 §결정 D2 + ADR-052 Amendment 5>
task: <Codex에게 요청할 구체적 작업>
```

**`artifacts` 필드 verbatim 첨부 의무** (CFP-578 / [ADR-070](../archive/adr/ADR-070-codex-verify-before-trust.md) §결정 D2 + [ADR-052 Amendment 5](../archive/adr/ADR-052-codex-proactive-check-touchpoints.md)):

Codex worker spawn prompt 안 file path reference 만 사용 금지. 모든 file content 가 verify task scope 인 경우 prompt payload 안 verbatim 첨부 필수 — Codex sandbox file system access 실패 (CFP-506 / CFP-520 / CFP-530 3 회 reproduce sentinel) systemic 원인 차단.

| verbatim 첨부 대상 | 영역 |
|---|---|
| 사용자 §1 원문 | story-section-1-immutable.yml SSOT, 변조 금지 invariant 정합 |
| Story §2-§6 / §7 PL synthesis 본문 | sandbox 영역 외 (internal-docs path) |
| 관련 ADR / Change Plan 본문 | sandbox 영역 외 가능성 (cross-repo / cross-plugin path) |
| cross-repo state | sibling plugin file / marketplace.json / contract MANIFEST 등 |

**partial 첨부 허용 (cap 초과 시)**: file content cap 초과 시 (token 비용 risk) → verify 대상 영역만 verbatim 첨부 + 나머지 file path reference 표시 + `[partial: lines NN-NN]` marker 의무.

**verify-before-trust 결과 처리 단계** (CFP-578 / [ADR-070](../archive/adr/ADR-070-codex-verify-before-trust.md) §결정 D1 / D3):

Codex worker 결과 수신 후 Orchestrator 는 finding evidence 의 ground truth 를 own working directory 안 Read / Glob / Grep 으로 verify 의무:

1. Codex finding evidence (인용 본문 / file path / line number / commit SHA / contract version 등) 추출
2. Orchestrator direct file Read / Glob / Grep 으로 evidence 영역 ground truth 확정
3. **mismatch 검출 시 verdict reject** + Story §10 FIX Ledger row append (false positive count tally, fix-event-v1 contract `[codex-false-positive]` sub-tag — schema MINOR bump 별도 carrier) + Orchestrator override rationale 명시 (4 종 verbatim: Codex evidence + Orchestrator Read 결과 + mismatch 영역 + reject 후속 동작)
4. **match 검출 시 finding accept** → recommendation / severity 기반 후속 동작 (PROCEED / ADDRESS_FIRST) 진입

**결과 처리** (touchpoint #2 **mandatory** 분기 — CFP-532 / [ADR-052 Amendment 4](../archive/adr/ADR-052-codex-proactive-check-touchpoints.md), 나머지 5 touchpoint **optional** 유지, verify-before-trust 단계 통과 후):

| recommendation | findings | 처리 (touchpoint #2 **mandatory**) | 처리 (touchpoint #1/#3/#4/#5/#6 optional) |
|---|---|---|---|
| PROCEED | — | 그대로 다음 단계 | 그대로 다음 단계 |
| ADDRESS_FIRST | P0 포함 | 해당 agent findings 반영 후 재진행 (blocking) | 동일 |
| ADDRESS_FIRST | P1-only | **inline FIX 의무 (skip 차단)** | Orchestrator 판단으로 skip 가능 → story §10 기록 |
| ADDRESS_FIRST | P2-only | Orchestrator 판단으로 Story §10 deferred 기록 가능 | 동일 |
| 판정 불일치 (#5 전용) | — | N/A (#5 = optional) | 사용자 에스컬레이션 |
| verify mismatch 검출 (모든 touchpoint) | — | finding reject + Story §10 false positive count tally + override rationale (ADR-070 §결정 D3) | 동일 |

**Boilerplate composition SSOT (CFP-819 / [ADR-081](../archive/adr/ADR-081-codex-worker-prompt-boilerplate.md) + ADR-052 Amendment 6)**: Codex worker prompt 본문 3 mandatory section (dogfood-out Story path verbatim / lane stage 표기 = current_lane + phase / sandbox boundary = sandbox_outside_paths) + verify-before-trust scope 5 sub-scope 분리 (file scope grep+quote / dir scope recursive grep+count / cross-repo gh api+commit SHA / grep count claim active vs historical 차원 / ADR §결정 번호 정확성) + 3-lane partition 표 (Codex factual citation 영역 / DesignReviewPL boundary completeness 영역 [ADR-068 4 invariants + Amd 1 I-5] / CodeReviewPL post-impl style + historical reference 보존성 영역 disjoint scope) = ADR-081 SSOT. declaration-only retain (ADR-070 §D5 precedent), mechanical lint 부재.

**Substitution scope 3-path enum (CFP-946-A / [ADR-052 Amendment 8](../archive/adr/ADR-052-codex-proactive-check-touchpoints.md) + [ADR-070](../archive/adr/ADR-070-codex-verify-before-trust.md) §결정 D1 expansion / Amendment 3)**: Codex worker spawn 결정 시점에 substitution scope explicit declare 의무 — 운영적 substitution behavior 의 normative codification. 9 occurrence sentinel (CFP-756 Epic close retro Sentinel #4 strike #8) 산물.

| Enum value | semantics | 적용 trigger | Story §10 marker (의무) |
|---|---|---|---|
| `inline_orchestrator_verify` (default) | Orchestrator 가 own working directory file Read 로 ground truth 확정 후 Codex finding accept/reject | Codex worker output 정상 수신 (sandbox network-block 없음) + finding evidence 영역 = Orchestrator working directory 안 | (면제 — default, marker 부재 = 암묵 default) |
| `manual_substitution_declare` | Codex worker spawn 직전 substitution scope 명시 declare (spawn prompt `task` field 또는 sub-field `substitution_scope` + Story §10 marker carrier) | sandbox 영역 외 file (internal-docs / sibling repo / cross-plugin path) verify task 필요 시 | `[codex-substitution-scope-declared: <scope-enum>]` (1 회/spawn) |
| `fallback_skip_with_marker` | Codex worker spawn 자체 skip + Orchestrator 가 substitution 후속 동작 단독 수행 (verify-before-trust 5 sub-scope 全 적용) | Codex CLI 미가용 / sandbox network-block 확정 / `codex exec` dispatch stall 또는 stream idle-timeout / 8+ occurrence sentinel reentrant 위험 영역 | `[codex-sandbox-fallback: <fail-mode>]` (1 회/spawn, fail-mode enum 8 종 = `api_missing` / `version_skew` / `enterprise_blocked` / `gh_api_network_blocked` / `manual_substitution_declared` / `inline_orchestrator_verify_only` / `subagent_recursion_blocked` / `dispatch_stall_or_stream_timeout` — 8번째 = CFP-1244 / ADR-070 Amendment 7 / ADR-052 Amendment 12) |

**verify-before-trust 5 sub-scope 무조건 적용**: substitution path 3-enum 어느 case 채택해도 Orchestrator verify-before-trust 5 sub-scope (file scope grep+quote / dir scope recursive grep+count / cross-repo gh api+commit SHA / grep count claim active vs historical 차원 / ADR §결정 번호 정확성, [ADR-081 §결정 D2](../archive/adr/ADR-081-codex-worker-prompt-boilerplate.md)) 무조건 적용. substitution = "Codex worker substitution" 이지 verify-before-trust 면제 아님.

**6 touchpoint × 3-enum cross-matrix**: 각 touchpoint 의 default + manual_substitution_declare trigger + fallback_skip_with_marker trigger = [ADR-052 Amendment 8](../archive/adr/ADR-052-codex-proactive-check-touchpoints.md) §A1 표 SSOT.

**narrative SSOT**: [`docs/domain-knowledge/domain/codex-collaboration/`](../docs/domain-knowledge/domain/codex-collaboration/) (ADR-052/070/081 cross-ref hub + substitution scope decision tree).

#### §3.10.1-bis Graceful degradation step pair (a)(b)(c) (CFP-963 / [ADR-081 Amendment 4](../archive/adr/ADR-081-codex-worker-prompt-boilerplate.md) §결정 D1.D body 확장 + [ADR-060 Amendment 14](../archive/adr/ADR-060-evidence-enforceable-promotion-framework.md) §결정 28 carrier)

ADR-081 Amendment 4 §결정 D1.D body 확장 (`sandbox_network_required: <bool>` → `network_scope: <4-tier enum>`: `offline` / `repo-fetch-only` / `web-fetch` / `offline_substitution_declared`) 이 codex worker spawn-prompt boilerplate 의 4-tier declaration 영역 codify. 본 sub-section = Codex CLI 미가용 / sandbox network-block 확정 / 8+ occurrence sentinel reentrant 위험 영역의 **graceful degradation step pair (a)(b)(c)** 명시 — fail-mode 8-enum 의 mechanical detection layer SSOT (신규 enum value 0, 기존 8-enum 재사용 — `api_missing` / `version_skew` / `enterprise_blocked` / `gh_api_network_blocked` / `manual_substitution_declared` / `inline_orchestrator_verify_only` / `subagent_recursion_blocked` / `dispatch_stall_or_stream_timeout`).

**step (a) — Codex spawn 직전 detect (fail-mode 8-enum membership)**:

Orchestrator 가 Codex worker spawn (Agent tool spawn / SendMessage to codex worker) **직전** 다음 3 detect probe 수행 — fail-mode 8-enum 의 spawn-time-detectable subset (api_missing / version_skew / enterprise_blocked) detection:

| Detect probe | mechanism | fail-mode binding |
|---|---|---|
| `codex --help 2>&1 \| grep -q -- '--allow-network'` 실패 | Codex CLI 자체 미가용 — codex@openai-codex plugin 미설치 / PATH 영역 외 | `api_missing` |
| `codex --version 2>&1` semver parse 실패 또는 minimum required version 미달 | Codex CLI version skew — `--allow-network` flag syntax 또는 `sandbox.network_access` config syntax 미지원 | `version_skew` |
| `gh api /rate_limit 2>&1` HTTP 403 (enterprise org policy gate) | enterprise org network egress 정책 차단 — codex CLI 자체는 가용하나 외부 HTTP 403 | `enterprise_blocked` |

3 detect probe 모두 PASS = step (b) inline_orchestrator_verify default path (substitution 비활성, 정상 Codex spawn). 1+ probe 실패 = step (b) `offline_substitution_declared` declare path 진입.

**step (b) — `network_scope: offline_substitution_declared` declare + verify-before-trust 5 sub-scope 全 적용**:

step (a) 1+ probe 실패 시 Orchestrator 는 다음 action:

1. **Codex worker spawn 자체 skip** — codex CLI 미가용 / sandbox network-block 영역, dispatch 자체 무의미.
2. **`network_scope: offline_substitution_declared` 4-tier enum value declare** — ADR-081 Amendment 4 §결정 D1.D body 정합 (boolean equivalent 부재 영역, strict ratchet-up). spawn-prompt body 가 사후 audit trail 용도로 declare 보유 (실제 spawn 미발생, declaration retain).
3. **Orchestrator inline 단독 substitution path 진입** — substitution path 3-enum `fallback_skip_with_marker` (ADR-052 Amendment 8 / ADR-070 Amendment 3 §결정 1 expansion 정합). Codex finding evidence ground truth 를 own working directory file Read / Glob / Grep 로 단독 verify (ADR-070 §결정 D1 무조건 적용).
4. **verify-before-trust 5 sub-scope 全 적용** — substitution = "Codex worker substitution" 이지 verify-before-trust 면제 아님 ([ADR-081 §결정 D2](../archive/adr/ADR-081-codex-worker-prompt-boilerplate.md) 5 sub-scope 무조건 적용):
   - D2.A file scope verify (single file 안 grep count)
   - D2.B dir scope verify (recursive grep)
   - D2.C cross-repo scope verify (gh api / git fetch origin — enterprise_blocked 영역은 본 sub-scope 자체 실패 가능, ADR-073 §결정 D1 정합 fallback)
   - D2.D grep count claim verify (active vs historical 차원)
   - D2.E ADR §결정 번호 정확성 verify

**step (c) — Story §10 marker + §14 `network_scope_actual` field**:

substitution path activation 시 Orchestrator 는 다음 audit trail 의무:

1. **Story §10 marker (1 회/spawn)**: `[codex-sandbox-fallback: <fail-mode>]` row append — fail-mode 8-enum 안 정확 1 value 보유 의무 (api_missing / version_skew / enterprise_blocked / gh_api_network_blocked / manual_substitution_declared / inline_orchestrator_verify_only / subagent_recursion_blocked / dispatch_stall_or_stream_timeout). fix-event-v1 contract 정합 (Orchestrator monopoly, CFP-32). `codex-network-scope-presence` lint (ADR-060 Amendment 14 §결정 28 / CFP-963 Phase 2 carrier) 가 marker enum 정합 membership check 검증.
2. **§14 Lane Evidence row 의 `network_scope_actual` field** (optional 13번째 field — evidence-check-registry-v1 v1.3 신규 schema, ADR-031 §14 12 field 영향 0 backward-compat): 본 lane row 의 actual scope (`offline_substitution_declared`) 기록. Codex dispatch 아닌 lane row = omit (omit-on-N/A pattern). present 시 4-tier enum 안 정확 1 value 보유 의무 (offline / repo-fetch-only / web-fetch / offline_substitution_declared). `codex-network-scope-presence` lint 가 §14 row 안 본 field membership check 검증.
3. **PMOAgent retro trigger 영역 carry-over** (선택): substitution 발화 누적 ≥3 occurrence within Story = ADR-045 §D-9 cross-Story pattern threshold reach 후보 (PMO retro carrier evaluation 영역).

**ratchet trigger (사용자/PMO escalation)**: 본 step pair (a)(b)(c) 의 `[codex-sandbox-fallback: <fail-mode>]` marker 누적 count 가 운영 중 ≥10 회 reach 시 ADR-052 Amendment 4 (touchpoint #2 mandatory) 의 codex CLI 가용 영역 가정 자체 재평가 후보. 본 정책 변경 = 별도 follow-up CFP 의무 (ADR-064 §결정 1 scope unitary 정합).

#### §3.10.1-ter Graceful degradation step pair (a)(b)(c) — reactive variant (CFP-1003 / [ADR-052 Amendment 9](../archive/adr/ADR-052-codex-proactive-check-touchpoints.md) + [ADR-070 Amendment 5](../archive/adr/ADR-070-codex-verify-before-trust.md) + [ADR-081 Amendment 5](../archive/adr/ADR-081-codex-worker-prompt-boilerplate.md))

§3.10.1-bis = proactive 6 touchpoint scope 한정 (codeforge 강제 invariant). 본 sub-section = reactive `codex:rescue` 채널 (사용자 ad-hoc invocation, ADR-022 Deprecated default 영역, ADR-070 D1 L110 `사용자 책임 영역 (적용 외)`) 의 best-effort 가이드 anchor — codeforge 강제 미발효, 사용자 자율 선택 영역.

**적용 trigger**: 사용자가 직접 `codex:rescue` subagent 를 ad-hoc invoke 한 경우 (proactive 6 touchpoint 자동 dispatch 영역 아님, ADR-052 D1 L84/L90 분리 invariant 정합).

**best-effort 가이드 anchor (사용자 자율 선택, codeforge 강제 0)**:

| step | proactive 변형 (§3.10.1-bis) | reactive 변형 (본 sub-section) |
|---|---|---|
| **step (a) detect** | Orchestrator Codex spawn 직전 3 detect probe 의무 (codeforge 강제 invariant) | 사용자 ad-hoc invocation 직전 3 detect probe 권장 (사용자 자율 선택) — `codex --help / --version / gh api /rate_limit` 동일 mechanism |
| **step (b) declare + verify-before-trust 5 sub-scope** | Orchestrator `network_scope: offline_substitution_declared` declare + verify-before-trust 5 sub-scope 全 적용 (codeforge 강제) | 사용자 자율 선택 — ad-hoc invocation prompt 본문 안 `network_scope: <4-tier enum>` declare 권장 + ADR-070 verify-before-trust pattern 채택 권장 (codeforge 강제 0, ADR-081 Amendment 5 A2 SSOT) |
| **step (c) Story §10 marker + §14 `network_scope_actual` field** | Orchestrator audit trail 의무 (`[codex-sandbox-fallback: <fail-mode>]` row + `network_scope_actual` field) | reactive 변형 marker = `[codex-rescue-fallback: <fail-mode>]` 권장 (사용자 자율 선택, Wave 2 mechanical lint scope 확장 시 marker enum value codify 결정 영역) — 사용자 ad-hoc invocation 시 codeforge 강제 0 |

**mechanical lint scope 확장 (Wave 2)**: `codex-network-scope-presence` lint (evidence-checks-registry entry, ADR-060 Amendment 14 §결정 28 carrier) 의 mechanical detection scope = proactive 6 touchpoint spawn prompt 한정 (CFP-1003 / ADR-052 Amendment 9 + ADR-070 Amendment 5 + ADR-081 Amendment 5 — proactive/reactive disjoint codify). reactive 영역 mechanical lint 확장 = 별도 CFP carrier 분리 (Wave 2, ADR-064 §결정 1 unitary 정합).

**사용자 책임 영역 invariant 보존**: 본 sub-section 의 4-anchor best-effort 가이드 = 사용자 ad-hoc invocation 시점에 anchor 채택 / 비채택 = 사용자 책임 영역. codeforge 측 강제 미발효 invariant retain (ADR-070 D1 L110 + ADR-022 Deprecated 정합). proactive 6 touchpoint scope 강제 invariant 와 disjoint axis.

#### §3.10.1 Pre-question Review (iterative reformulation — CFP-446 / [ADR-052 Amendment 2](../archive/adr/ADR-052-codex-proactive-check-touchpoints.md))

| 항목 | 내용 |
|---|---|
| 트리거 | `AskUserQuestion` 호출 직전 (항상, 전 레인). ADR-064 §결정 3 룰 5 정합 — `AskUserQuestion` 발화 자체 결정 (가치 판단 / 미공개 컨텍스트 2 종 한정) 통과 후 진입 |
| artifacts | 질문 초안 + 옵션 목록 (round 별도 갱신) |
| task | "아래 질문 초안을 검토해 (1) ambiguity / context-external 영역 = 표현 애매 또는 답 추론 정보 컨텍스트 부재 (2) verbosity 영역 = 핵심 결정 대비 장황. 2 기준 모두 통과 = `accept` / 1 종이라도 검출 = `reject` + reformulation 제안. reformulation 결과도 brevity 준수 의무" |
| 출력 적용 (iterative) | Codex `accept` → 그대로 `AskUserQuestion` 발화 / Codex `reject` → reformulation 반영 후 다음 round dispatch / 최대 3 rounds / fall-through 시 round 3 reformulation 그대로 `AskUserQuestion` 발화 |

**Round 흐름 (max 3 + fall-through)**:

```
Round 1: Codex dispatch (질문 초안 v1)
  ├─ accept → AskUserQuestion(v1) [early termination]
  └─ reject → reformulation v2
       ↓
Round 2: Codex dispatch (질문 초안 v2)
  ├─ accept → AskUserQuestion(v2)
  └─ reject → reformulation v3
       ↓
Round 3: Codex dispatch (질문 초안 v3)
  ├─ accept → AskUserQuestion(v3)
  └─ reject (fall-through) → AskUserQuestion(v3) [그대로]
```

사용자 발화 directive verbatim (CFP-446 §1 — Story file SSOT): "이 리뷰는 최대 3회 반복할 수 있고 3회를 채우면 그냥 사용자에게 질문하라" — fall-through 정책 SSOT.

**Codex reject 기준 (2 종)**:

| 기준 | 운영적 정의 |
|---|---|
| `ambiguity` / `context-external` | 질문 표현 애매 또는 답 추론 정보 컨텍스트 부재 (사용자가 답할 수 없는 질문) |
| `verbosity` | 질문 본문이 핵심 결정 영역 대비 장황 — 사용자 발화 directive: "질문의 내용이 길수록 좋지 않은 질문" |

**Brevity 행동 규범 (질문자 + 리뷰어)**:

- **질문자 (Orchestrator)** — 질문 초안 작성 시 1 문장 단위 + numbered list (max 3 항목). 컨텍스트 길이 < 핵심 질문 길이 비율 유지. ADR-064 §결정 3 룰 4 정합
- **리뷰어 (Codex)** — `verbosity` reject 시 reformulation 결과도 brevity 준수 의무. round N+1 입력이 round N 보다 길어지면 Orchestrator 가 reformulation 거부 후 round N+1 skip → fall-through 조기 진입 가능 (자기모순 차단)

**debate-protocol-v1 미사용 결정 (ADR-052 Amendment 2 A5)**:

본 iterative reformulation 은 `debate-protocol-v1` (§3.13) 의 multi-round adversarial debate 와 영역 분리. 본 영역은 단일 agent (Codex) self-iteration 으로 충분 — role_lock / anti-sycophancy / anchor 재발 / transcript Story §9 영속화 모두 불필요. 사용자 발화 directive ("Codex 에 리뷰 요청 … 다시 재구성하여 리뷰") 가 self-iteration 패턴 정합.

| 영역 | debate-protocol-v1 (ADR-059) | §3.10.1 iterative reformulation |
|---|---|---|
| 참여자 | 2 agent adversarial | 1 agent (Codex) self-iteration |
| Trigger | finding severity / recommendation divergence | Codex reject (ambiguity / verbosity) |
| Round 영속화 | Story §9 transcript 의무 | Orchestrator turn 내 transient (영속화 불필요) |
| FIX 흐름 | §10 ledger + reasoning carryover | N/A — verdict producer 영역 외 |

#### §3.10.2 Design Synthesis Check (**mandatory** — CFP-532 / [ADR-052 Amendment 4](../archive/adr/ADR-052-codex-proactive-check-touchpoints.md))

| 항목 | 내용 |
|---|---|
| 트리거 | ArchitectAgent Change Plan §3 초안 완료 → ArchitectPLAgent 전달 직전 (항상) |
| **mandatory: true** | **Orchestrator 가 dispatch 결과 P0 + P1 finding 모두 inline FIX 의무 (skip 영역 차단). P2-only 만 Orchestrator 판단으로 Story §10 deferred 기록 가능. 6 sample success rate 100% sentinel: CFP-426 + CFP-427 + CFP-428 + CFP-429 + 2 carry-over Story — 모든 review lane FIX 회피 evidence** |
| artifacts | §3 Change Plan 초안 + 6 SubAgent 산출물 요약 |
| task | "6 SubAgent 산출물이 §3에 균형 있게 반영됐는지 검증. 모순·누락·순환 논리 포착" |
| 출력 적용 | ADDRESS_FIRST 시 ArchitectAgent §3 수정 후 재전달 (P0 + P1 inline FIX 의무, P2-only deferred 가능) |

#### §3.10.3 Development Rescue

| 항목 | 내용 |
|---|---|
| 트리거 | DeveloperPLAgent FIX 2+ 반복 동일 이슈 감지 시 |
| artifacts | 구현 블로커 설명 + 관련 코드/로그 |
| task | "구현 블로커를 독립적으로 진단하고 root cause 및 해결 경로를 제시" |
| 출력 적용 | DeveloperPLAgent 진단 결과 적용 |

#### §3.10.4 Requirements Output Review (multi-round debate 격상 — CFP-411 / ADR-052 Amendment 1)

| 항목 | 내용 |
|---|---|
| 트리거 | RequirementsPLAgent §1-§6 통합 완료 → `phase:설계` 진입 직전 (항상) |
| artifacts | Story §1-§6 전체 내용 |
| task | "§1-§6 요구사항 완전성 검증. 테스트 불가능한 AC, 누락 엣지케이스, 모호한 표현, 상충 요구사항 포착" |
| 출력 적용 (default 흐름) | Codex `recommendation = PROCEED` 또는 RequirementsPL 의미 비교 결과 divergence 없음 → 그대로 `phase:설계` 진입 |
| 출력 적용 (divergence 흐름 — Amendment 1) | RequirementsPL 이 Codex `{findings, recommendation, rationale}` vs 자기 synthesis (§2/§5/§6) 의 의미적 차이 (AC / Edge Case / why 해석) 검출 시 `debate-protocol-v1` (§3.13) 자동 발동. lane-agnostic 패턴 정합. 합의 시 §5/§6 보강 후 `phase:설계` 진입, max 5 미합의 시 사용자 escalation, FIX verdict 시 **RequirementsPL 자체 재spawn** (transcript 입력 — ArchitectAgent 미관여) |

**Divergence detection (Requirements lane — semantic, structured surface 부재)**:

```
PL LLM judgment:
  - compare(codex_findings vs §2/§5/§6 self-synthesis)
  - criteria: ac_semantic_diff | edge_case_semantic_diff | why_interpretation_diff
  - anchor_id assignment: §<section-ref> (review-verdict-v4 패턴 재사용)
    예: §5-AC-3, §5.2-EC-2, §2-bound-1, §6-source-2
  - 모호 시 가장 광범위한 anchor 채택 (debate 진입 결정 우선)
```

DesignReview lane (review-verdict-v4 `findings[]` structured 비교) 과 달리 Requirements lane 은 PL LLM 의미 판정 위임. false positive 차단 = `codeforge-requirements/agents/RequirementsPLAgent.md` sibling sync 의 prompt engineering 영역 (ADR-010 follow-up).

**FIX 흐름 redo 대상 분기 (ADR-052 Amendment 1 A4)**:

- DesignReview lane debate FIX → ArchitectAgent re-run (§3.13 정합, ADR-059 §결정 3)
- Requirements lane debate FIX → **RequirementsPL 자체 redo** (§2/§5/§6 재합성). ArchitectAgent 미관여 — lane scope 분리. transcript verbatim 주입.

#### §3.10.5 FIX Root Cause 2nd Opinion

| 항목 | 내용 |
|---|---|
| 트리거 | ArchitectPLAgent "설계 vs 구현" root cause 판정 완료 직후 (항상) |
| artifacts | 판정 결과 + evidence pack (Change Plan 버전 + 리뷰 findings + 테스트 로그) |
| task | "root cause 판정에 독립적 2nd opinion 제시. 동의/불동의 + 근거" |
| 출력 적용 | 동의 → 기존 판정 진행 / 불동의 → **사용자 에스컬레이션** (최종 판정 사용자) |

#### §3.10.6 ADR Draft Review

| 항목 | 내용 |
|---|---|
| 트리거 | ArchitectAgent ADR 초안 완료 직후 (항상) |
| artifacts | ADR 초안 전체 |
| task | "ADR 결정 논거 검토. 순환 논리, 약한 근거, 대안 미검토, §결정 ↔ §컨텍스트 불일치 포착" |
| 출력 적용 | ADDRESS_FIRST 시 ArchitectAgent ADR 수정 후 설계리뷰 진입 |

> **ADR-082 cross-ref (CFP-776)**: Codex proactive check 의 finding evidence 신뢰는 외부 worker output verify layer (ADR-070). lane agent 가 §9 evidence / corpus enumeration write 시점 source/value verify 누락은 별 disjoint layer ([ADR-082 §결정 2](../archive/adr/ADR-082-write-time-self-write-verification-mandate.md)) — Codex proactive check 와 verify 대상 disjoint (Codex output ↔ lane self-write write-time).

---

### §3.13 Multi-round Adversarial Debate (debate-protocol-v1, CFP-391 / [ADR-059](../archive/adr/ADR-059-debate-protocol-v1.md))

debate-protocol-v1 = lane-agnostic registry (ADR-059 §결정 5). 현재 두 lane 에 적용:

| Lane | Story | Divergence surface | Divergence 판정자 | FIX redo 대상 |
|---|---|---|---|---|
| DesignReview | CFP-391 (deployed) | review-verdict-v4 `findings[]` 동일 `anchor_id` 의 severity OR recommendation | DesignReviewPL structured 검사 | ArchitectAgent re-run (ADR-059 §결정 3) |
| Requirements | CFP-411 (ADR-052 Amendment 1) | RequirementsPL synthesis (§2/§5/§6) vs Codex proactive check 의미 차이 | RequirementsPL LLM 의미 판정 | **RequirementsPL 자체 redo** (§2/§5/§6 재합성) |

DesignReview lane 에서 Claude worker 와 Codex worker 가 review-verdict-v4 finding 불일치를 산출했을 때 Orchestrator (또는 DesignReviewPL via Orchestrator self-write delegate) 가 `debate-protocol-v1` 을 자동 발동한다. Requirements lane 에서 RequirementsPL 이 Codex proactive check 결과와 자기 synthesis 의 semantic divergence 를 검출할 때 동일 protocol 발동 (touchpoint #4, ADR-052 Amendment 1). 본 protocol = ADR-022 deprecation (CFP-134) 이후 ad-hoc Codex review 자동 발동 무효 정책과 정합 — 자동 발동은 debate 한정 (사용자 explicit Codex request 시 활성된 워커들 사이의 divergence 해소).

#### Trigger surface (divergence detection)

DesignReviewPLAgent 가 review-verdict-v4 packet 합성 직전 surface 검사:

```
for anchor_id in union(claude_findings.anchor_id, codex_findings.anchor_id):
    claude_f = claude_findings.get(anchor_id)
    codex_f  = codex_findings.get(anchor_id)
    if claude_f and not codex_f:
        divergence = "recommendation"  # 한쪽 FIX, 다른쪽 silent = PASS
    elif claude_f.severity != codex_f.severity:
        divergence = "severity"
    elif claude_f.recommendation != codex_f.recommendation:
        divergence = "recommendation"
    else:
        divergence = None  # 합의 — debate 미발동
    if divergence:
        debate_triggers.append({anchor_id, anchor_text, claude_pos, codex_pos, divergence_type: divergence})
```

debate_triggers 비어있지 않으면 각 trigger 별로 debate 발동 (multi-anchor 동시 debate 가능 — anchor 별도 독립 라운드 카운터).

#### Round 실행 흐름 (사이클 1회)

| 단계 | 책임자 | 행위 |
|---|---|---|
| Round 0 init | DesignReviewPL | `anchor_text` + 양측 initial position 추출. role_lock 명시. system_prompt_appendix 주입 |
| Round 1 ~ N | Claude / Codex worker | role-lock 유지 prompt + `anchor` 입력 최상단 강제 prepend + transcript carryover. `remaining_disagreements` + `position_change` flag 출력 |
| Round N 종료 판정 | DesignReviewPL | `remaining_disagreements` 검사 + `position_change` reason 검증 + LLM 합의 판정 |
| min 3 미달 합의 | DesignReviewPL | `force_continue` + adversarial prompt 재주입 — 가짜 합의 검증 (EC-2) |
| max 5 미합의 | Orchestrator | `AskUserQuestion` packet 발화 (escalation_packet schema 정합) — 사용자 dialog 응답이 최종 verdict |
| anchor 재발 검출 | DesignReviewPL | Story §9 scan → `anchor_recurrence_count >= 2` 시 debate 진입 없이 즉시 사용자 escalation |

#### Anti-sycophancy 강제 directive (매 라운드 system prompt 주입)

> "당신의 Round 0 입장을 유지하라. 상대 주장의 근거가 결정적일 때만 입장 변경 허용. 입장 변경 시 출력에 `position_change: true` + `position_change_reason` 명시 의무. `remaining_disagreements` 미해결 쟁점을 빠짐없이 나열하라. 비어 있으면 가짜 합의로 간주된다."

#### Transcript 영속화 (Story §9 inline append)

- 위치: codeforge family Story = `<internal-docs-clone>/<plugin-folder>/stories/<KEY>.md §9`. Consumer Story = `docs/stories/<KEY>.md §9`
- Section header format: `### Debate transcript: <anchor_id>`
- Schema: debate-protocol-v1 registry 정의 준수 (trigger / rounds[] / termination)
- Writer: DesignReviewPL via Orchestrator self-write delegate (ADR-039 Amendment 정합)

#### FIX verdict 처리 (reasoning carryover)

```
debate_verdict == FIX
  ↓
transcript Story §9 append (### Debate transcript: <anchor_id>)
  ↓
§10 FIX Ledger row append (Orchestrator self-write)
  ├─ debate_artifact_ref = #debate-transcript-<anchor_id>
  └─ fix-event-v1 1.1 contract (CFP-391 MINOR bump)
  ↓
[lane 분기]
  ├─ DesignReview lane → ArchitectPLAgent re-spawn
  │   ├─ prompt 에 debate transcript verbatim 주입 (요약 금지)
  │   └─ ArchitectAgent re-run instruction:
  │      "양측 입장의 reasoning trail 을 반영해 redesign 하라"
  │   ↓
  │   DesignReview re-entry (FIX-N+1, 카운터 정합)
  │
  └─ Requirements lane (CFP-411 / ADR-052 Amendment 1 A4) → RequirementsPLAgent 자체 re-spawn
      ├─ prompt 에 debate transcript verbatim 주입 (요약 금지)
      ├─ ArchitectAgent 미관여 (lane scope 분리)
      └─ re-run instruction:
         "transcript 의 양측 입장을 반영해 §2/§5/§6 재합성하라.
          AC / Edge Case / why 해석 영역의 미해결 disagreement 모두 검토."
      ↓
      Requirements re-synthesis → §1~§6 재완료 → touchpoint #4 재발화 (FIX-N+1)
```

#### env=0 / env=1 동작 차이

| 환경 | Round dispatch | 토큰 비용 |
|---|---|---|
| `env=1` (agent teams 활성) | `SendMessage(to=worker, body=round_N_input)` continuous dialog | round 간 cache 가능 (5 min TTL) |
| `env=0` (default subagent context) | Orchestrator round-trip polyfill — 매 라운드 Claude worker / Codex worker 각각 `Agent` tool one-shot spawn (transcript 누적 입력 첨부). 라운드 카운터 PL 자체 관리 | 매 라운드 cold start (cache 미적용) — 비용 증가 |

양쪽 동일 protocol schema 준수. env=0 fallback 시 토큰 비용 증가는 사용자 인식 의무 (consumer-guide §1f).

#### Token budget cap (operational risk 완화)

매 라운드 worker 출력 권고 cap (PL 이 enforce):

- `statement`: <= 2000 token
- `rationale`: <= 3000 token
- 총 ~5000 token / round / worker
- 5 라운드 × 2 worker × 5K = 50K token (Opus PL 200K context 한도 내 안전)

초과 시 PL 이 worker 에게 condensation 요청 (1회 한정) 후 invalid 처리. max 5 라운드 cap = 비용 폭증 차단 forcing function.

#### Wave 4 — DesignLane blanket trigger (CFP-582 / [ADR-059 Amendment 2](../archive/adr/ADR-059-debate-protocol-v1.md))

cross-module Story 의 ArchitectAgent 산출물 (Change Plan §3 / ADR / Story §3/§7/§11) 에 대한 blanket Codex worker 검증 — divergence 발생 시 다시 multi-round debate 흐름 진입. dispatch_mode `blanket_cross_module_designlane` 자동 활성 조건 + 6 step 진입 절차:

1. **touched_top_level_paths 산정**: Story §1 spec_links + Change Plan §2 영향 영역 union 의 top-level path (예: `src/foo/` / `docs/` / `templates/`). 중복 dedup 후 distinct count.
2. **touched_lanes 산정**: 같은 union 에서 codeforge lane plugin folder mapping (codeforge-{requirements,design,develop,review,pmo,test}) 의 distinct lane count.
3. **판정**: `touched_top_level_paths >= 2` OR `touched_lanes >= 2` 시 dispatch_mode = `blanket_cross_module_designlane` 활성 (단일 module Story 는 활성 안 함, 기존 `auto_on_divergence` 분기 유지).
4. **spawn prompt 갱신**: ArchitectPLAgent 가 Codex worker spawn 시 prompt `artifacts` 필드에 Change Plan §3 + 신규 ADR draft + Story §3/§7/§11 mirroring content verbatim 첨부 (ADR-070 verify-before-trust 정합).
5. **§14 row append**: Lane Evidence 에 spawn 직전 row 추가 (`dispatch_mode=blanket_cross_module_designlane`, `touched_top_level_paths=N`, `touched_lanes=M`). end column = Codex return 시 outcome (`agreement_reached` / `divergence_detected` / `escalated`).
6. **verdict 처리**: agreement 시 정상 PASS (FIX 없음). divergence detected 시 다시 §3.13 multi-round debate 진입 (`auto_on_divergence` flow + `convergence_quality_invariant` 3 marker 의무). PL verdict 작성 시 `prior_codex_findings[]` (Touchpoint #2 carry-over, §결정 9) 가 transcript Round 0 input 으로 verbatim 첨부.

**non-blanket 케이스**: `touched_top_level_paths < 2` AND `touched_lanes < 2` (single-module Story) — Wave 4 trigger 미활성, 기존 `auto_on_divergence` (Codex single-shot vs Claude finding 비교) flow 유지. dispatch_mode 4-value enum precedence `auto_on_divergence > blanket_cross_module_designlane > mechanical_fast_path_inline > user_request_only` 정합.

**EC-1 (Codex 미가용 fallback)**: codex CLI 미설치 / authentication fail / network unavailable 시 ArchitectPLAgent 가 blanket trigger skip + Story §10 row append (`reason: "codex unavailable - blanket trigger skipped"`). 사용자 통지 후 정상 PASS 진행 — DesignReviewPL lane (CFP-391 기존 flow) 가 후속 검증 channel.

#### lane-agnostic 적용

본 §3.13 = DesignReview lane scope (Story 1 / CFP-391). Story 2 (Requirements lane — CFP-392) 진입 시 동일 protocol contract 재사용 + lane-specific `semantic` divergence_type 정의 (ADR-052 touchpoint #4 격상 Amendment 와 동행). CodeReview / SecurityTest lane 은 deferred CFP-C scope.

---

### §3.14 Orchestrator-user dialog convergence (CFP-612 / [ADR-071](../archive/adr/ADR-071-orchestrator-user-dialog-convergence.md))

debate-protocol-v1 (§3.13) = **agent ↔ agent** debate domain. 본 §3.14 = **Orchestrator ↔ user** dialog domain. 두 sub-section 은 "수렴 dialog 가 본질" 1 점 conceptual common ground 만 공유 — schema 재사용 금지 (§3.13 의 3 marker pattern 은 debate transcript verification, §3.14 는 turn-by-turn cognitive frame). 본 §3.14 는 매 user-facing turn 의 Orchestrator 행동 본문 SSOT.

> **본질 anchor**: Orchestrator 가 사용자와 대화할 때, mechanical rule 추종이 아니라 진짜 수렴 대화에 참여하도록 codeforge SSOT 를 영구적으로 바꾸는 변화. 본 anchor 가 충족되지 않으면 아래 mechanism 을 몇 개 쌓든 의미 없다 — 모든 mechanism 은 본질을 보조하는 scaffolding (가설 E 의 mechanical 규칙 자체 한계 trap 회피 forcing function).

> **ADR-082 cross-ref (CFP-776)**: 본 §3.14 = Orchestrator ↔ user 대화 표현 layer. lane agent §9 evidence / corpus enumeration write-time source/value verify 는 별 disjoint layer ([ADR-082 §결정 1](../archive/adr/ADR-082-write-time-self-write-verification-mandate.md) 4-layer 표) — 사실 verify layer ↔ 대화 표현 layer 분리 (ADR-073 ↔ ADR-071 분리 패턴과 동형). schema 재사용 금지.

#### 호출 시점 + skill 호출

매 user-facing turn 직전 (= [ADR-039](../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) inline whitelist 1번 entry = 사용자 dialog turn) Orchestrator 가 `codeforge:user-dialog-mode` skill 호출 — frame mode 진입 4 step + 4 layer 검증 + sub-mechanism 2 종 lookup. skill SSOT mirror 만, 본 §3.14 = 본문 SSOT.

#### frame mode 진입 4 step (ADR-071 §결정 1)

| step | 행위 | self-check |
|---|---|---|
| 1 | codeforge 내부 어휘 "내부 메모" 분류 격리 | 사용자 발화 본문에 ADR-NNN / CFP-NNN / lane plugin name / hook name / inter-plugin contract name 직접 등장 안 함 (식별자 인용 시 사전 요약 의무, [ADR-064 §결정 3 룰 3](../archive/adr/ADR-064-decision-principle-mandate.md) 정합) |
| 2 | 사용자 지금까지 무엇 알고 있는지 정리 | 사용자 mental model 추정 — 이전 turn 발화 기준 + 미공개 컨텍스트 분리 |
| 3 | 사용자 이 turn 무엇 답·결정해야 하는지 한 문장 | turn 의 사용자 action item 이 1 문장으로 명확. 한 문장 안 되면 step 미완 (메시지 발화 차단) |
| 4 | 위 셋 바탕으로 메시지 작성 | step 1+2+3 통합 위에 본문 작성 |

**frame mode marker 형식 (visible vs hidden cognitive layer)**: 본 §3.14 derived default = **hidden cognitive layer** (Orchestrator 자체 thinking 단계 — 사용자 visible 영역 marker 미발화). Layer 1 가시적 preamble 이 visible signal 충당. visible cognitive marker 추가 (예: "[frame mode 진입]" 사용자 prefix) 가 필요한 영역은 별도 follow-up CFP.

#### frame mode 안 세부 룰 3 종 (ADR-071 §결정 2)

**(a) 메시지 직전 self-check 3 문항** — 사용자가 답해야 할 것이 한 문장으로 명확한가 / 비-codeforge 맥락 사람이 이해 가능한가 / 답하는 데 필요한 배경 (왜 / trade-off / 걸려있는 것) 충분한가. 3 문항 모두 PASS 후 발화.

**(b) 사실/가치 분리** — 사실 → derived default 적용. 가치 → `AskUserQuestion` 발화. 모호 → 가치 측 (safe direction). [§결정 5 결정 트리 참조](../archive/adr/ADR-071-orchestrator-user-dialog-convergence.md).

**(c) sub-agent 결과 평이 번역** — raw packet 노출 금지, codeforge 내부 용어 평이한 한글, **3 줄 제약 거부** (길이 자유), "왜 / trade-off / 걸려있는 것" 배경 포함, 원본 packet 은 사용자 요청 시 별도.

#### 4 layer 검증 (ADR-071 §결정 3)

| Layer | 동작 | 위치 / 발화 시점 | trivial turn 면제 |
|---|---|---|:-:|
| **Layer 1 — 가시적 preamble** | 메시지 맨 위 "지금 답해주실 것" 1 문장 가시 | 매 user-facing turn 맨 윗줄 | ✅ (응답 ≤ 1 줄 + 의문/결정 부재 시) |
| **Layer 2 — 자기 declare** | turn 끝 "주의한 가설" 1 줄 declare (보조 신호) | 매 turn 맨 아랫줄 | ✅ |
| **Layer 3 — keyword "추상" 즉시 halt** | 사용자 메시지 본문 "추상" 한글 token 등장 시 immediate halt + 재작성 | 사용자 token detection 시점 | ❌ (trivial turn 에서도 active) |
| **Layer 4 — 누적 detection** | N=1 즉시 halt (같은 양상 다음 turn 재발) / M=5 max threshold `AskUserQuestion` escalation | 매 turn 끝 incident 검사 | ❌ |

**Layer 3 stem vs exact match 결정** (E2 — 본 §3.14 결정 영역): derived default = **stem match** (substring "추상" 등장 모두 trigger — "추상" / "추상적" / "추상화" 등). false positive risk (예: 도메인 어휘 "추상 미술") 인지 + 사용자 explicit override 시 incident row append 후 dialog 재개. **Hanja form "抽象" 면제** + **영문 alias ("abstract") = trigger 아님** (한글 token 만 anchor).

**Layer 4 file rotate / archive 정책** (E3 — 본 §3.14 결정 영역): derived default = **no auto reset** + **manual archive only** (사용자 explicit reset request 시 archive). yearly file rotate vs 별도 row delineator marker 선택은 첫 archive 시점 사용자 결정 영역.

**trivial turn 정의 3 criteria AND** (E12 — 본 §3.14 결정 영역): (1) 응답 ≤ 1 줄 + (2) 의문 부재 + (3) 결정 부재. 3 criteria 모두 충족 시 Layer 1 + Layer 2 면제. Layer 3 / Layer 4 는 trivial turn 에서도 active.

**Turn-shape derived defaults** (E9 / E10 / E11 — 본 §3.14 결정 영역, Story §5.3 turn-shape edge 4 종 중 E12 제외 3 종. Codex Proactive Check #2 FIX-1 carrier):

| Edge | 정의 | Layer 1 (preamble) | Layer 2 (declare) | Layer 3 ("추상" halt) | Layer 4 (누적 detection) |
|---|---|---|---|---|---|
| **E9 streaming token** | Orchestrator 가 token stream 단계로 응답 (incremental flush) | **final flush 시 적용** — incremental token stream 단계는 preamble 의미 없음, 사용자 시점 = 1 turn 완료 (final flush) | final flush 시 적용 | active (streaming 중 사용자 추가 input 가능) | active (turn 끝 incident 검사) |
| **E10 tool-call-only** | 사용자 화면에 prose 없는 turn (순수 file read / Bash 단발 호출 / mcp__* call 만) | **면제** (no user-facing prose = preamble 의미 없음) | **면제** | active | active (단 incident 영역은 prose turn 만 — tool-call-only turn 자체는 incident 분류 외) |
| **E11 AskUserQuestion popup** | `AskUserQuestion` structured popup 발화 turn | **preamble = "AskUserQuestion 으로 답해주실 것:" 1 문장** (popup 이 본 발화의 결정 영역 cover — preamble 은 popup 진입 시그널만, popup 본문 verbatim 인용 불요) | popup 본문이 declare 충당 — separate Layer 2 줄 면제 | active (popup option_text 안 "추상" 등장 가능) | active |
| **E12 trivial answer** | 응답 ≤ 1 줄 + 의문 부재 + 결정 부재 (3 criteria AND) | **면제** (trivial turn 자체가 preamble cognitive overhead 정당화 불가) | **면제** | active (1 줄 안 "추상" 등장 시 trigger) | active (trivial turn 도 pattern_dimension 분류 영역) |

E10 tool-call-only 의 정량 정의 = **(a) 사용자 화면 prose 0 줄 + (b) cosmetic 1-줄 미만 (예: "잠시만요" / 빈 status report)**. (a) AND (b) 충족 시 tool-call-only 분류 — 정의 외 turn = E9 streaming 또는 일반 turn (Layer 1+2 적용).

[empirical-source: derived default (analytical reasoning from Claude Code turn-shape model, no external corpus yet, frustration evidence carrier = CFP-612 §1 사용자 directive verbatim). circular self-citation 인정 + 후속 corpus 누적 후 ratchet 강화 영역 — [ADR-068 Amendment 1](../archive/adr/ADR-068-boundary-completeness-invariants.md) I-5 정합 (cognitive layer 영역의 derived default 첫 empirical annotation 사례).]

E11 popup turn 의 Layer 2 면제 사유 = popup 본문 자체가 declare semantic 충당 — preamble + popup option_text + popup body = 3 channel 의 user-facing signal 이미 충분, Layer 2 추가 시 cognitive redundancy.

#### Sub-mechanism 2 종 (수렴 보장, ADR-071 §결정 4)

**Sub-mechanism 1** — 매 halt 후 (Layer 3 / Layer 4 N=1) 재작성 메시지 맨 아랫줄 (Layer 2 declare 와 별도 줄) 에 `이전과 다르게 한 점:` prefix + 1 줄 본문. 단순 표현 다듬기 (어휘 변경 / 문장 길이 압축) 가 아닌 **차원 전환** 의무.

**Sub-mechanism 2** — 같은 양상 재발 시 (Layer 4 file row count ≥ 2) 단순 표현 다듬기 금지. **4 차원 enum** 중 다른 차원 강제 전환:

| 차원 | 의미 | 전환 예시 |
|---|---|---|
| **표현** | 어휘 / 문장 길이 / 구조 | "ADR-064 §결정 3" → "결정 제시 5 룰" |
| **결정 구조** | 옵션 제시 방식 / derived default / AskUserQuestion 형식 | numbered list → 권장 1 + 대안 1 |
| **보고 형식** | sub-agent 결과 표시 / 평이 번역 / 길이 | raw JSON → 평이 한글 (3 줄 제약 거부) |
| **질문 자체** | 어떤 결정을 사용자에게 묻는지 자체 변경 | "방향 X / Y 중 어느 것" → "본 결정의 user value 우선순위는?" |

#### Layer 4 영속 file (ADR-071 §결정 6)

- **path**: `docs/orchestrator-communication-incidents.md` (wrapper repo). consumer 측은 자기 repo 의 동일 path 별도 lifecycle.
- **owner**: Orchestrator 단독 monopoly (FIX Ledger / Git Ops Log / ADR-RESERVATION 패턴 정합 — wrapper repo 안 4번째 cross-Story append-only file 패턴).
- **lifecycle**: append-only, cross-Story 영속 (Story 종료 시 reset 없음), M=5 lifetime counter, manual reset only.
- **schema**: 8-column (iter / timestamp / story_key / pattern_dimension / pattern_summary / trigger / different_dimension_after_halt / escalation_outcome). [ADR-071 §결정 6](../archive/adr/ADR-071-orchestrator-user-dialog-convergence.md) verbatim.
- **사용자 escalation 후 다음 incident**: pattern_dimension 강제 전환 (sub-mechanism 2 정합).

#### 사실/가치 판단 결정 트리 (ADR-071 §결정 5)

```
결정 후보 발화 직전:
  is_factual?
    YES → derived default 적용 (컨텍스트로 추론 가능 시)
                   ↓
                  declare default + 결과 보고 + 사용자 정정 의무
    NO (가치 판단 영역) → AskUserQuestion 발화 의무
    AMBIGUOUS → 가치 측 분류 (safe direction)
                   ↓
                  AskUserQuestion 발화 의무
```

**사실 예시**: 파일 존재 / `wc -l` 결과 / `git log` 출력 / SHA / `grep` 결과
**가치 예시**: 사용자 선호 (UX / 보고 길이) / 정책 강화 방향 / scope 결정 / brainstorm 채택안
**모호 예시**: derived default 추론 가능 + future 작업 영향 큼 → 가치 측 (사용자 확인 후 진행)

#### 3 memory entry normative 승격 mapping (ADR-071 §결정 8)

| memory entry | 정책 위치 SSOT 이전 | unchanged scope |
|---|---|---|
| `feedback_explain_before_ask` | 본 §3.14 frame 본문 + ADR-071 §결정 1 step 4 + §결정 4 sub-mechanism 1 | — |
| `feedback_question_quality` | 본 §3.14 frame 본문 + ADR-071 §결정 2 (b) + §결정 5 결정 트리 | — |
| `feedback_subagent_driven_auto_select` | **변경 없음** — §3.0.5 기존 정책 유지 | codeforge wrapper side SSOT 변경 0 (사용자 personal memory side entry 자체 영향 없음 — 사용자 영역, codeforge wrapper scope 외) |

**승격 시점**: 본 Story (CFP-612) Phase 2 PR merge 시점. PMOAgent retro ([ADR-045](../archive/adr/ADR-045-story-retro-mandatory-trigger.md) mandate) 의제로 사용자 personal memory entry 삭제 제안 (사용자 결정 영역).

#### CFP-582 conceptual cross-ref (schema fit 부적합 — ADR-071 §결정 9)

[§3.13 debate-protocol-v1](../archive/adr/ADR-059-debate-protocol-v1.md) Amendment 2 (CFP-582) 의 3 marker pattern (`counterargument_present` / `alternative_proposed` / `debate_purpose_statement_present`) = **debate transcript verification schema** (multi-round adversarial debate 의 convergence_quality_invariant 검증용).

본 §3.14 = **turn-by-turn Orchestrator-user dialog** (single-turn cognitive frame + cross-Story 누적 detection). 두 sub-section 의 schema 직접 mapping **부적합**. 본 §3.14 의 frame mode + 4 layer + sub-mechanism 어느 항목도 §3.13 의 3 marker schema 를 import 하지 않는다. CFP-582 의 본질 (수렴 dialog) 만 conceptual cross-ref. **schema 재사용 절대 금지**.

#### env=0 / env=1 동작 동일

`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env 무관 — 본 §3.14 = Orchestrator (top-level Claude 세션) 의 cognitive frame, agent teams platform capability 와 무관. env=0 default subagent context / env=1 agent teams enabled context 모두 동일 행동.

#### scope 외 (ADR-071 §결정 10)

- **Layer 1 preamble mechanical lint** — 별도 follow-up CFP (Wave 5 = cognitive + persistence layer 만, lint 별도 CFP 분리)
- **agent ↔ agent debate** (§3.13 cover 완료)
- **코드 품질 / 보안 / 성능**
- **사용자 personal memory entry 자체 삭제** (사용자 영역 — codeforge wrapper scope 외)
- **consumer overlay 영역 customization** (overlay 가 정책 축소 불허)
- **debate-protocol-v1 3 marker import** (schema 직접 채택 절대 금지)
- **frame mode marker visible vs hidden** = 본 §3.14 derived default hidden cognitive layer, visible 추가 = 별도 CFP
- **Layer 3 false positive 처리 advanced policy** = 첫 incident 시점 사용자 결정 영역
- **Layer 4 file rotate / archive 자동화** = 별도 CFP

#### DialogFidelityAgent verifier auxiliary (ADR-071 Amendment 1 / CFP-777, Amendment 2 / CFP-818)

DialogFidelityAgent = codeforge-pmo **cross-cutting read-only verifier** (additive auxiliary, **5번째 cognitive layer 신설 금지** — Layer 1-4 enum 보존 invariant, ADR-071 §결정 12).

**Spawn trigger 3-anchor** (ADR-039 §결정 2 inline whitelist 보존, 자동 hook 부재 → Orchestrator 자율 채택):
- `post_user_turn`: 사용자 turn 응답 직후 (Layer 3 "추상" detect / numbered list 발화 / AskUserQuestion 직전)
- `pre_architectpl_synthesis`: ArchitectPL synthesis 완료 직전 (Codex TP#2 augment)
- `pre_fix_rootcause`: FIX 루프 root cause 판정 직전 (Codex TP#3 augment)

**3-anchor 발화 형태 매핑 표 (ADR-071 §결정 13.2, CFP-818)**: 각 anchor 가 어떤 turn shape 직전 활성하는지 + Codex touchpoint dedup:

| anchor | 발동 시점 | 발화 형태 매핑 (UC) | Codex touchpoint dedup |
|---|---|---|---|
| `post_user_turn` | 사용자 turn 응답 직후 (Layer 3 "추상" detect / numbered list 발화 / `AskUserQuestion` 직전) | UC-1 (`AskUserQuestion` 발화 직전) / UC-2 (numbered list 또는 dialog format 발화 직전) / Layer 3 "추상" stem detect 직후 | 없음 (Codex 6 touchpoint 와 disjoint) |
| `pre_architectpl_synthesis` | ArchitectPL synthesis 완료 직전 (사용자 보고 발화 직전) | UC-3 (Orchestrator 가 ArchitectPL synthesis 결과 사용자 보고 발화 직전) | **Codex TP#2 (mandatory, [ADR-052](../archive/adr/ADR-052-codex-proactive-check-touchpoints.md) Amendment 4) 와 동일 위치** — 양 verifier 활성 (EC-6 dedup: Codex = P0/P1 inline FIX mandatory, DialogFidelityAgent = correction_action_hint 5-enum 권고) |
| `pre_fix_rootcause` | FIX 루프 root cause 판정 직전 (ArchitectPL 1차 진단 후 최종 판정 직전) | UC-4 (Orchestrator 가 FIX 루프 root cause 판정 직전) | **Codex TP#3 (FIX 2+ 감지 시) 와 동일 위치** — 양 verifier 활성 (EC-5 dedup: Codex = P0/P1 single-shot 검토, DialogFidelityAgent = ledger drift detection 권고) |

dedup 패턴 (EC-5/EC-6): 동일 위치 활성 시 Orchestrator 가 양 verdict 통합 (verify-before-trust [ADR-070](../archive/adr/ADR-070-codex-verify-before-trust.md) 의무).

**turn-shape edge × 3-anchor 12 cell 활성 표 (ADR-071 §결정 13.3, CFP-818)**: 위 "Turn-shape derived defaults" 표 의 E9/E10/E11/E12 edge × 3-anchor cross-product 활성 매핑:

| anchor \ edge | E9 streaming token | E10 tool-call-only | E11 AskUserQuestion popup | E12 trivial answer |
|---|---|---|---|---|
| `post_user_turn` | **final flush 시 활성** (mid-stream spawn 금지 — idempotency, EC-4 derived default) | **면제** (사용자 발화 직접 미발생, EC-3 derived default) | **active** (popup 본문 자체가 dialog convergence anchor — popup option_text/body Layer 3 "추상" detect 영역, EC-2 derived default) | **면제** (cost > benefit, trivial turn 3-criteria AND 충족 시 cognitive overhead 정당화 불가, EC-1 derived default) |
| `pre_architectpl_synthesis` | active (edge-independent — Story 1회 발동, ArchitectPL synthesis 완료 직전 fixed timepoint) | active | active | active |
| `pre_fix_rootcause` | active (edge-independent — FIX 발동 시점 fixed, [ADR-067](../archive/adr/ADR-067-fix-ledger-implementability-escalation.md) FIX 3 카운터 범위 안 ≤ 3/Story) | active | active | active |

cell 값 enum: `active` (spawn 의무) / `면제` (spawn 금지) / `final flush 시 활성` (E9 streaming 의 final flush 단계 1회만 spawn — mid-stream 금지).

**Output Port closed enum**: `verify_result: fidelity_ok | drift_detected | ledger_gap` + `correction_action_hint: rescan_ledger | escalate_user | self_correct | no_action | null` (free-form 차단, generator 역할 침범 금지).

**Orchestrator dispatch**: verifier output 수신 후 `correction_action_hint` enum (rescan_ledger / escalate_user / self_correct / no_action / null) 에 따라 Orchestrator 가 직접 action 분기 — verifier 는 권고만, 실제 메시지 변경 / ledger append / 사용자 escalation 은 Orchestrator monopoly.

**verify-before-trust 의무** ([ADR-070](../archive/adr/ADR-070-codex-verify-before-trust.md)): `evidence_path[]` direct Read verify 의무, mismatch 시 verdict reject + Story §10 tally + override rationale 명시.

**Inline whitelist 1번 entry 정합 cross-ref (ADR-071 §결정 13.4 / CFP-818)**: DialogFidelityAgent spawn (subagent 형태) 자체는 [ADR-039 §결정 2](../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) inline whitelist 4-entry 1번 entry (사용자 dialog) 의 scope **안** cognitive 보강 — 사용자 dialog 본 발화는 inline 유지 + 직전/직후 verifier spawn 은 ADR-039 §결정 1 default subagent spawn 정합. 5번째 entry 신설 아님 (closed enumeration 보존).

**Q-3check disjoint scope cross-ref (ADR-071 §결정 13.5 / CFP-818)**: [ADR-064 §결정 9](../archive/adr/ADR-064-decision-principle-mandate.md) Question quality 3-check = Orchestrator self-check (proposing/stop-time). DialogFidelityAgent = 외부 verifier (발화 entity ≠ 검증 entity 분리, self-referential trap 회피). disjoint scope — 양자 cross-cutting 보강 (3-check 가 cover 못하는 누적 결정 ledger drift / 세션 개시 요건 일관성 = DialogFidelityAgent cover, DialogFidelityAgent 가 cover 못하는 turn-internal cognitive frame / 7 anti-pattern P1-P7 = 3-check cover).

**closed enum 확장 시 별도 CFP 의무 (ADR-071 §결정 13.6 / CFP-818)**: 3-anchor enum closed enumeration 보존. 확장 후보 3종 (`pre_lane_spawn` / `pre_phase_transition` / `pre_pause_decision`) 발생 시 별도 CFP 신설 의무 ([ADR-064 §결정 7](../archive/adr/ADR-064-decision-principle-mandate.md) top-down ratchet + [ADR-058 §결정 5](../archive/adr/ADR-058-adr-sunset-criteria-mandate.md) sunset_justification 정합).

#### Conversational reporting frequency suppression (ADR-071 §결정 15 / CFP-851 / Amendment 4)

Orchestrator 가 사용자에게 **말 거는 시점·빈도** (frequency / timing) 의 closed enumeration 계약. 본질 anchor = **frequency vs richness 분리 invariant** — 본 정책이 좁히는 것은 발화 횟수·시점 만, **말할 때의 풍부함은 §결정 2(c) "3 줄 제약 거부 · 길이 자유 · 배경 포함" 그대로 보존**. SSOT = [ADR-071 §결정 15](../archive/adr/ADR-071-orchestrator-user-dialog-convergence.md), 본 §3.14 = lookup mirror.

**3 touchpoint closed enumeration** — Orchestrator 사용자 발화 허용 시점:

| touchpoint | 발화 사유 | scope |
|---|---|---|
| **(a) 결과-명세 확인** | 사용자가 선언한 결과 자체가 모호 + 잘못 추측 시 rollback 비싼 경우 (verifiable outcome surface 안전판 — wrong-dataset risk 차단) | 가치 / 명세 판단 — `AskUserQuestion` 발화 (§결정 5 결정 트리 — 모호 → 가치 측 분류) |
| **(b) 사용자만 풀 수 있는 차단** | 인증·권한 등 codeforge 자체 해소 불가, 사용자 행동 필요 | ADR-039 inline whitelist 1번 entry (사용자 dialog) scope 안 |
| **(c) 최종 완료 보고 1회** | 요청한 작업 단위 전체 완료 (산출물 = 최종 결과 자체) | ADR-039 inline whitelist 4번 entry (Status report) scope 안 |

그 외 진행·중간 결정·근거·중간 결과 = **산출물 channel** 전용 기록 (대화 turn 아님): `docs/stories/<KEY>.md` / `docs/change-plans/<slug>.md` / `docs/adr/ADR-NNN-<slug>.md` / PR description / GitHub Issue comment / TodoWrite panel ([ADR-038](../archive/adr/ADR-038-progress-visualization-todowrite.md) progress visualization).

**무약화 invariant** — 3 touchpoint 발화 시:
- Layer 1 가시적 preamble + Layer 2 자기 declare 의무 — turn-shape edge derived default (E9/E10/E11/E12 표) 무변경
- §결정 2(c) richness 보존 — raw packet 노출 금지, 평이한 한글, 3 줄 제약 거부, "왜 / trade-off / 걸려있는 것" 배경 포함
- DialogFidelityAgent auxiliary 3-anchor spawn 보존 — §결정 12/13 family pattern 정합
- §결정 14 incident append-rate measurement 보존

**closed enum 확장 패턴** — 4번째 touchpoint 신설 시 별도 CFP 의무 (ADR-064 §결정 7 top-down ratchet + ADR-058 §결정 5 sunset_justification + Story §1 사용자 explicit 승인 의무). 본 ADR-071 안 3번째 closed enumeration 인스턴스 (3-anchor enum / 4 차원 enum / 3 touchpoint enum 동형).

**mechanical lint = 별도 follow-up CFP** (§결정 10 패턴 정합 — behavioral directive only, advisory warning tier 첫 도입 시 evidence-checks-registry entry append + dialog-fidelity-effect precedent 동형 runtime cron measurement).

---

### §3.15 Action-blocked fallback decision tree (CFP-658 / [ADR-027 Amendment 2](../archive/adr/ADR-027-consumer-adoption-protocol.md))

enterprise org-level `default_workflow_permissions: read` 차단 환경 또는 일반 Action failure 시 codeforge 의무 사용 + ADR-039 inline whitelist 외 영역 modification 금지 의무 충돌 해소. Orchestrator 가 매 lane spawn 직전 본 decision tree 수행.

#### Trigger detection 절차 (lane spawn 직전 의무)

```
매 lane spawn 직전:
  ┌─ Step 1: Issue label `fallback:manual` 부착 여부 확인 (Trigger C)
  │     YES → fallback path 활성 (per-Issue override)
  │     NO → Step 2
  │
  └─ Step 2: `.claude/_overlay/project.yaml` 의 `bootstrap.fallback_mode` 확인 (Trigger A)
        == "action_blocked" → fallback path 활성 (environment default)
        == "auto" or absent → 정상 workflow path (story-init.yml 자동 실행 가정)
```

우선순위 (C) > (A). per-Issue 명시 의지 > environment default. (A) 활성 환경에서도 (C) label 없는 Issue 는 정상 workflow 시도 후 fail 시 사용자 escalate.

**Option (B) Outage detection 폐기**: workflow run conclusion + N분 timeout 자동 감지 = workflow self-fail detection 불가 (silent failure, Researcher 위험 1) → 폐기.

#### Fallback path 활성 시 Orchestrator 행동

| Step | 행동 | Owner |
|---|---|---|
| 1 | RequirementsPLAgent spawn (mctrader-hub MCT-135 패턴 시 skip 가능 — ADR-064 §결정 3 룰 1 derived default) | Orchestrator |
| 2 | ArchitectPLAgent spawn — Phase 1 PR manual `gh pr create` 책임 + Codex Touchpoint #2 dispatch (ADR-052 Amendment 4 mandatory) | Orchestrator |
| 3 | `templates/scripts/manual-story-init-fallback.sh <ISSUE_NUMBER>` 호출 (Phase 2 carrier 신설 후 활성) | ArchitectPLAgent or RequirementsPLAgent |
| 4 | phase label 수동 전이 (`codeforge:lane-self-write-boundary` skill 정합) | Orchestrator self-write |
| 5 | Story §14 Lane Evidence row append (ADR-031) | Orchestrator |
| 6 | Trigger (C) PR description 의 manual fallback checklist 6 항목 검증 | Orchestrator |

#### Governance ratchet 약화 mitigation 3종 (자동 발화)

| Invariant | Mitigation | Tier |
|---|---|---|
| §1 verbatim immutable | post-merge lint `section-1-verbatim-postmerge.yml` (Phase 2 carrier) warning tier | ADR-060 framework |
| phase-label transition | Orchestrator 수동 의무 (본 §3.15 Step 4) | governance |
| 4 required check | manual PR 도 phase-gate-mergeable + doc frontmatter + doc section + invariant-check 통과 의무 (`enforce_admins:true` ratchet 유지, CFP-70) | blocking |

#### Codex Touchpoint #2 mandatory (ADR-052 Amendment 4)

manual fallback path 활성 시에도 ArchitectAgent §3 직후 Codex proactive check dispatch 의무. `artifacts` 필드 verbatim attach (ADR-070) — manual write 영역의 governance ratchet 약화 vector 차단 forcing function.

#### env=0 / env=1 동작 동일

`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env 무관. agent teams platform capability 와 별도 — fallback path 활성화는 Orchestrator detection 수준 결정.

상세 SSOT:
- [ADR-027 §결정 6](../archive/adr/ADR-027-consumer-adoption-protocol.md) — fallback path normative SSOT
- [domain-knowledge `workflow-blocked-manual-fallback.md`](../docs/domain-knowledge/domain/github-actions/workflow-blocked-manual-fallback.md) — recovery runbook
- [consumer-guide §1h](consumer-guide.md) — consumer runbook
- [project-config-schema](project-config-schema.md) — `bootstrap.fallback_mode` schema

---

### §3.19 Admin merge pre-flight gate (CFP-1522 / [ADR-113](../archive/adr/ADR-113-admin-merge-preflight-gate.md))

Orchestrator 가 `gh pr merge --admin <PR-N>` attempt 시점 직전 5-step pre-flight gate 의무. ADR-073 §결정 1 verify-before-assert transition trigger `admin_merge_attempt` sub-domain instantiation. ADR-045 §D-9 pattern_count 3 reach Mandatory ADR escalation 산물 (CFP-1334 retro + CFP-1318 retro + CFP-1495 PR #1505 close evacuation 3-incident super-class `admin_merge_action_required_force_attempt`).

#### §3.19.1 5-step procedure

**Step 1 — required check state enum fetch**

```bash
gh pr checks <PR-N> --json name,state,conclusion --jq '.[] | select(.state != "completed" or .conclusion != "success") | "\(.name): \(.state)/\(.conclusion)"'
```

empty output (모든 required check `state=completed AND conclusion=success`) → admin merge 진행. non-empty → Step 2.

**Step 2 — ACTION_REQUIRED detection + abort (10-value closed_enum)**

```yaml
abort_states_enum:  # closed-set, open_extension: false
  - action_required        # primary block — manual approval needed
  - failure                # explicit fail
  - cancelled              # workflow cancelled
  - timed_out              # CI timeout
  - stale                  # stale check, fresh commit re-trigger needed
  - pending                # in-progress
  - in_progress            # in-progress alias
  - skipped                # workflow conditional skip
  - neutral                # neutral state, Orchestrator manual judgment
  - unknown                # closed-set 외 value → fail-closed semantic (admin merge 차단)
```

1+ check 의 state 가 위 10-value enum 영역에 속하면 abort + Step 3 진입. `unknown` value (closed-set enum 외) = **fail-closed** (admin merge 차단 + 사용자 escalation).

**Step 3 — fresh commit trigger recovery**

ACTION_REQUIRED 잔존 시 fresh commit (empty 또는 trailing whitespace amendment commit) 으로 workflow re-trigger:

```bash
git -C "<worktree_abs_path>" commit --allow-empty -m "[CFP-NNN] re-trigger required checks (admin-merge preflight Step 3)"
git -C "<worktree_abs_path>" push origin <branch>
```

`phase-gate-mergeable.yml` `on:` block = `pull_request: [opened, synchronize, labeled, unlabeled, edited]` only — `workflow_dispatch` entry 부재 (verified). manual re-trigger 경로 부재 영역에서 fresh commit = primary recovery. Wave 4 brainstorm carrier 영역 = `workflow_dispatch` entry 보완 검토 (별도 follow-on CFP, ADR-113 §결정 8).

**Step 4 — re-verify (≤ 60s wait + re-fetch)**

```bash
sleep 60   # workflow propagation grace (CI dispatch latency typical 30-60s, Anthropic infra-independent)
gh pr checks <PR-N> --json name,state,conclusion --jq '.[] | select(.state != "completed" or .conclusion != "success")'
```

empty → admin merge 진행. non-empty → Step 5 (attempt cap check).

**Step 5 — attempt cap = 3 STOP + escalate**

Step 1-4 cycle 의 attempt count 가 **3 회** reach 시 STOP + 사용자 escalation 의무. Workflow log direct verify:

```bash
gh run list --workflow="phase-gate-mergeable.yml" --branch=<branch> --limit 10 --json databaseId,conclusion,createdAt
gh run view <latest-id> --log
```

Workflow self-error (workflow code bug / dependency outage) 추정 시 사용자 escalation. **`auto-retry` 무한 loop 차단** (Threat A: counter reset abuse mitigation).

#### §3.19.2 Attempt cap dual scope (per-PR + per-Story)

attempt cap=3 = **dual scope AND** (Threat A counter reset abuse — close+reopen / PR 재생성 / attempt 분산 차단):

- **per-PR scope**: 동일 PR-N 안 `gh pr merge --admin` 시도 누적 ≥ 3 → STOP
- **per-Story scope**: 동일 carrier_story (CFP-NNN) 안 모든 PR 의 admin-merge 시도 누적 ≥ 3 → STOP (close+reopen / PR 재생성 우회 차단)

**dual carrier 조건**: 둘 중 1+ trigger 시 STOP + 사용자 escalation 의무.

#### §3.19.3 진단 flow (failure mode enum 4-fail)

| Fail mode | 진단 | 대응 |
|---|---|---|
| **fail-1** API call failure (network / token expiry / Anthropic infra 429) | `gh` exit code ≠ 0 + stderr 분석 | retry exp-backoff 3회 + `codeforge:rate-limit-429-mitigation` skill + ADR-066 PAT 만료 check (90d rotation) |
| **fail-2** state enum unknown | `gh pr checks` output 안 10-value enum 외 state value detect | **fail-closed semantic** (admin merge 차단 + 사용자 escalation, 10-value enum invariant 보존) |
| **fail-3** re-trigger 후 ACTION_REQUIRED 잔존 | Step 3 fresh commit trigger 후 Step 4 re-verify 에서 동일 ACTION_REQUIRED | workflow self-error 추정 → attempt cap 카운트 + Step 5 STOP escalation |
| **fail-4** silent bypass attempt | Orchestrator/subagent 가 5-step skip + `gh pr merge --admin` 직접 호출 | ADR-024 Amendment 6/8 §결정 6.A 5 lint chain 자동 covered (별도 mechanism 0) |

#### §3.19.4 우회 mechanism enum (a-d)

**ADR-113 §결정 3/4 cross-ref** — 다음 4 우회 시도 mitigation:

- (a) **Counter reset abuse** (Threat A) — close+reopen / PR 재생성 / attempt 분산 → **per-PR + per-Story dual scope** (§3.19.2 AND condition)
- (b) **`enforce_admins` toggle abuse** (Threat B) — `gh api -X PATCH /repos/<org>/<repo>/branches/main/protection` 안 `enforce_admins.enabled: false` toggle → **explicit forbid** (audit-trailed exception channel 외 금지, ADR-113 §결정 3)
- (c) **Pre-flight gate script bypass** — Orchestrator instrumentation 우회 + 직접 `gh pr merge --admin` → Wave 2 mechanical wire carrier (`scripts/check-admin-merge-preflight.sh` 3-layer self-block: pre-commit + pre-push + Orchestrator instrumentation, 별 sub-Story carrier)
- (d) **Bypass-as-norm-mutation** — `hotfix-bypass:admin-merge-preflight-gate` norm mutation → ADR-024 Amendment 6/8 §결정 6.A 4 lint chain 자동 covered (`bypass-label-counter` + `per-plugin-cumulative-counter` + `bypass-justification-marker` + `check-bypass-audit-comment.sh`) + `[bypass-justification]` PR comment marker 의무 (`comment-prefix-registry-v1` 14번째 prefix)

#### §3.19.5 Fallback path (CFP-1495 carrier 재진입)

CFP-1495 PR #1505 close evacuation (산출 8 file headRefOid `13b958eb` 보존) recovery procedure (ADR-113 §결정 7 §7.4.1 DR):

```bash
git -C "<new-worktree>" fetch origin 13b958eb
git -C "<new-worktree>" checkout -b cfp-1495-redo origin/main
git -C "<new-worktree>" cherry-pick 13b958eb
git -C "<new-worktree>" push -u origin cfp-1495-redo
gh pr create --title "[CFP-1495] Confluence drift detection cron — REDO" --body "Recovery from closed PR #1505 (headRefOid 13b958eb). post-CFP-1522 ADR-113 admin-merge pre-flight gate active 후 재진입."
```

branch naming `cfp-1495-redo` 권장 (ADR-024 cfp-NNN 정합, 간결 — `cfp-1495` 동일 branch 재사용 시 origin ref dangle 위험). post-CFP-1522 merge 후 활성.

#### §3.19.6 evidence-checks-registry binding

- entry name: `admin-merge-preflight-gate`
- current_tier: `warning` (deferred-followup Wave 1 declaration-only)
- bypass_label: `hotfix-bypass:admin-merge-preflight-gate` (label-registry-v2 v2.70 95번째 family member)
- carrier_adr: ADR-060 (4-tier framework)
- owner_adr: ADR-113 (5-step procedure SSOT)
- paired_owner_adr: ADR-073 §결정 1 (verify-before-assert transition trigger `admin_merge_attempt` sub-domain)

Wave 2 mechanical wire (`scripts/check-admin-merge-preflight.sh` + workflow + bats fixture) = 별 sub-Story carrier (`status: Active` 전환 시점).

---

## 3B. Preflight 체크 (lane 진입 직전)

**doc-only fast-path 분기 (ADR-054)**: Story 분류 판정 직후, Orchestrator가 §결정 1 분류 표 적용. `doc-only fast-path` 해당 시: 설계 lane → 경량 설계리뷰 → 단일 PR close (구현 lane spawn 금지). `full-lane` 해당 시: 기존 5-lane 전체. 모호 시 full-lane 강제. 판정 표 SSOT: [ADR-054](../archive/adr/ADR-054-doc-only-story-fast-path.md).

Orchestrator가 **각 레인 진입 직전에 의무 수행**. 3개 체크 중 하나라도 FAIL이면 **block + report**: 에이전트 스폰 없이 사용자에게 실패 사유 반환.

### 3B.1 3개 체크 항목

| # | 체크 | PASS 조건 |
|---|------|-----------|
| 1 | **phase 라벨 정합성** | Story Issue `phase:*` 라벨이 진입할 레인과 일치 (예: 설계 레인 진입 시 `phase:설계`) |
| 2 | **Story file 선행 섹션 채움** | 진입할 레인이 요구하는 이전 섹션이 존재 (예: 설계 진입 시 §1-6, 설계 리뷰 진입 시 §7, 구현 진입 시 §7 + §8 Test Contract) |
| 3 | **외부 의존성 가용** | Codex 리뷰/Analyst 레인 진입 시 `codex --version` 성공 확인. GitHub MCP `mcp__github__issue_read` ping 성공 |
| 4 | **TodoWrite 스키마 가용** (non-blocking) | `ToolSearch("select:TodoWrite")` 성공 여부. 미로드 시 재시도 1회. 재시도 실패 시 **PASS** (lane 미차단 — ADR-038 §결정 7) + `⚠️ TodoWrite 스키마 미로드` 경고 출력. ADR-038 Amendment 2 §결정 9 (SessionStart hook tier (b) PRIMARY, runtime ToolSearch (c) FALLBACK retain — §1.1 0i 참조). |

### 3B.2 FAIL 시 동작

- **스폰 중단**
- 아래 형식으로 사용자 ESCALATE (§2.3 ESCALATE 프롬프트와 유사):

```
⛔ Preflight FAIL — {레인} 진입 차단
- Story: <KEY>
- 실패 체크: {항목 번호 + 사유}
- 현재 상태 스냅샷: {phase 라벨 / §진입 선행 섹션 상태 / 의존성 ping 결과}
- 권장 복구: {해당 lane plugin 으로 §X 보강 / GitHub label 수정 / Codex 재설치 안내}
```

사용자 응답 수령 전까지 레인 진입 금지.

> 체크 4(TodoWrite 스키마)는 non-blocking — FAIL 이어도 스폰 미차단, 경고만 출력 (ADR-038 §결정 7).

### 3B.3 적용 레인별 세부

- **요구사항**: (1) `phase:요구사항` / (2) §1 사용자 원문 존재 + **공통 입력 패키지 준비** (관련 ADR 목록 §3 선제 fetch via `Glob(docs/adr/ADR-*.md)`, 관련 코드 경로 §4 식별, Project Config Packet slice 확보) / (3) `codex` CLI 가용 + GitHub MCP 가용 (DomainAgent·Researcher 호출 포함)
- **설계**: (1) `phase:설계` / (2) §1-6 모두 채움 + "사용자 확인 필요" 해소 + **공통 입력 패키지 준비** (변경 대상 코드 경로 확정, 관련 ADR verbatim fetch, Change Plan 초안 메모 준비) / (3) GitHub MCP 가용
- **설계 리뷰**: (1) `phase:설계-리뷰` / (2) §7 채움 + `docs/change-plans/<slug>.md` 존재 + §7 보안 설계 섹션 작성 여부 (또는 §7.6 N/A 사유 명시 여부) / (3) Codex 플러그인 가용
- **구현**: (1) `phase:구현` / (2) §7 완료 + Change Plan §8 Test Contract 존재 (§8.3 `N/A` 허용) + Phase 1 PR merged / (3) 필요 Dev 전원 스폰 가능
- **구현 리뷰**: (1) `phase:구현-리뷰` / (2) §8 Impl Manifest 기록 + ArchitectPLAgent 매핑표 감사 PASS / (3) Codex 플러그인 가용
- **구현 테스트**: (1) `phase:구현-테스트` / (2) §9.2 구현 리뷰 PASS 기록 / (3) CI (`gh pr checks`) 접근 가능 (ADR-048 CI gate)
- **통합 테스트**: (1) `phase:통합-테스트` / (2) §9.3 CI gate PASS 기록 / (3) `docker-compose.test.yml` 존재 여부 확인 (§8.6 환경 의존성 Story) + IntegrationTestAgent spawn 가능 (ADR-055)
- **보안 테스트**: (1) `phase:보안-테스트` / (2) §9.4 통합 테스트 PASS 기록 / (3) Codex 플러그인 가용 + 의존성 매니페스트 존재 + Dependabot/CodeQL 결과 접근 가능 (lanes.security_ai: true 시만)

### 3B.4 Preflight 결과 기록 (PMO 감사 trail · 의무)

PASS·FAIL 무관, **모든 Preflight 실행 결과**는 Orchestrator 가 직접 GitHub Issue 코멘트에 기록한다 (PMO 회고 §13.2의 "Preflight 실행 근거" 감사 항목 충족).

Orchestrator 가 Preflight 직후 직접 `mcp__github__add_issue_comment` 호출:

```
Issue: #<N>
Phase: <진입 레인>
Agent: Orchestrator
TL;DR: Preflight {PASS | FAIL} — {레인} 진입 {허용 | 차단}
Body: |
  체크 1 (phase 라벨 정합성): {PASS | FAIL — 사유}
  체크 2 (Story file 선행 섹션): {PASS | FAIL — 사유}
  체크 3 (외부 의존성): {PASS | FAIL — 사유}
  (FAIL 시) 권장 복구 / 사용자 ESCALATE 여부
Source: <자동 — Orchestrator §3B Preflight>
Timestamp: <YYYY-MM-DDTHH:MM:SS+09:00>  # KST zoned (display layer — ADR-079 §결정 2)
```

코멘트 prefix는 `[<phase>] Orchestrator: Preflight {PASS|FAIL}`. 기록 누락 시 PMO 완료 회고에서 P1 결함으로 감사 보고됨.

### 3B.5 plugin-meta-na PR pre-push 자가 검증 (Codex audit closure sprint 회고 §5 운영 개선 #1)

ADR-005 plugin-meta-na 패턴(§8/§9 lane 게이트 면제)으로 진행되는 plugin 자기 적용 PR은 일반 lane 리뷰를 우회하므로 **author가 push 직전 로컬 invariant-check 자가 검증 의무**.

**의무 절차** (push 직전):
1. 변경 대상 SSOT 식별 (CLAUDE.md / `agents/**` / `templates/**` / `.claude-plugin/plugin.json` / `CHANGELOG.md` / `docs/migration-guide.md` 등)
2. 영향 받는 invariant-check Step (3 agent count / 6 category enum / 7 migration-guide BREAKING parity / 8 severity_overrides count)을 [`.github/workflows/invariant-check.yml`](../.github/workflows/invariant-check.yml)에서 직접 grep으로 확인
3. 로컬 dry-run: 해당 step의 핵심 grep·python 로직 1-2줄을 직접 실행해 본 PR 변경 후 PASS 여부 확인 (예: `grep -c "data-migration" templates/change-plan.md docs/inter-plugin-contracts/review-verdict-v1.md` — review subsystem 자체 검증은 codeforge-review plugin (plugins/codeforge-review/) 에서)
4. drift 발견 시 push 전 fix commit 추가, drift 부재 시 push 진행

**근거**: [`docs/retros/2026-04-28-codex-audit-closure-sprint.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/retros/2026-04-28-codex-audit-closure-sprint.md) §5. CFP-21 (migration-guide BREAKING regex 미일치) / CFP-22 (DesignReviewPL severity_overrides P1 3건 누락) 모두 push 후 CI fail로 발견 — plan 작성 단계에서 잡혔어야.

**적용 범위**: plugin-meta-na PR만 (production code Story는 일반 lane Preflight + DesignReview/CodeReview/SecurityTest가 자동 검증). consumer overlay 적용 PR은 본 절차 비대상.

---

### §3.16 UpgradeAgent dispatch protocol (CFP-743 Wave 2 Story-3 / [ADR-076](../archive/adr/ADR-076-declarative-reconciliation-upgrade.md) §결정 5 + [reconcile-protocol-v1 v1.2](../docs/inter-plugin-contracts/reconcile-protocol-v1.md))

codeforge family upgrade 의 선언적 reconciliation 실행 주체. **3 책임 분리** (ADR-076 §결정 5): SessionStart hook (detect only — filesystem touch 0 / network 0) ≠ UpgradeAgent (Plan + Apply) ≠ CLI (`scripts/codeforge-upgrade.{sh,ps1}` 단일 진입점).

**Dispatch 절차** (Phase 2 carrier — CLI/UpgradeAgent 실 구현 후 활성):

```
사용자 → bash scripts/codeforge-upgrade.{sh|ps1} <mode>
  mode = --dry-run | --apply | --rollback <version>   # CLI argument fix, 사용자 결정 분기 0
  │
  └─ Orchestrator → UpgradeAgent spawn (ADR-039 default subagent one-shot, 재귀 spawn 금지 platform inherent)
       │
       ├─ --dry-run  : 9 desired_state_domains diff preview (filesystem touch 0, network call 가능)
       ├─ --apply    : snapshot 생성 → 9 영역 reconcile → 사후 sanity check 단일 transaction
       │                (partial 실패 / sanity 실패 = automatic_rollback_to_snapshot, 사용자 prompt 0)
       │                consumer .github/ 영역 reconcile = PR open (자동 merge 0, PR review gate 보존)
       └─ --rollback <version> : 해당 version snapshot restore
       │
       └─ transaction 완료 → event log artifact docs/upgrade-events/<date>-<version>.md 자동 생성 (C2)
```

**핵심 invariant**: ① SessionStart hook detect 책임 침범 0 (ADR-038 Amendment 3 §결정 12) ② `user_decision_branches: 0` (Epic CFP-699 §1 WHY "0 자리" verbatim) ③ transaction completion = ADR-053 §D2 3조건 AND (marketplace sync PR merged + consumer install 완료 + drift check PASS) ④ reconcile PR scope = ADR-066 Amendment 3 (reconcile-target-repos contents:write + pull_requests:write, target/action 한정 least-privilege) ⑤ path-form 정규화 의무 (MSYS2 `/c/` — CFP-702 normalize_path bug precedent 회피). 상세 SSOT = reconcile-protocol-v1 v1.2 `mechanical_implementation_binding` block.

> **CLAUDE.md cross-ref 부재 사유 (ArchitectPL 설계 결정)**: CLAUDE.md 가 line cap (≤320, ADR-012 Amendment 1 §결정 6) 을 이미 초과 (334 lines, pre-existing warning) — UpgradeAgent dispatch 는 operational reference-tier (anchor-tier 아님 — Orchestrator 가 매 turn 자기검열 대상 아님, ADR-051 Amendment 1 판정자 기준) 이므로 본 playbook §3.16 + consumer-guide 가 SSOT. CLAUDE.md line-delta 0 (over-cap 악화 회피).

### §3.16.1 Consumer natural-language upgrade trigger (CFP-1104 carrier / [ADR-071 Amendment 5](../archive/adr/ADR-071-orchestrator-user-dialog-convergence.md) §결정 16 + [ADR-076](../archive/adr/ADR-076-declarative-reconciliation-upgrade.md) invariant carrier)

consumer 가 자연어 token `codeforge upgrade` (또는 한글 변형) 발화 시 Orchestrator 가 dialog reflex 없이 즉시 §3.16 UpgradeAgent dispatch 호출. ADR-076 invariant `user_decision_branches: 0` 의 **dialog 진입 단계 enforcement** carrier — base ADR-071 §결정 5 사실/가치 분리 원칙의 dialog reflex 차단 first applied case.

**closed enumeration 보존 invariant**: 본 trigger lookup table = ADR-071 §16.2 closed enumeration 1 entry. 2번째 trigger token 확장 시 별도 CFP 의무 (ADR-064 §결정 7 top-down ratchet + ADR-058 §결정 5 sunset_justification null 보존 + Story §1 사용자 explicit 승인 + SecurityArch consult — trust boundary 영역).

#### Trigger token (closed enumeration, 1 entry)

| Trigger phrase regex (case-insensitive) | Mapped action |
|---|---|
| `\b(codeforge\s+upgrade\|codeforge\s+업그레이드)\b` | `scripts/codeforge-upgrade.sh` invocation per §3.16 (7 차원 derived default 자동 적용) |

#### 5 의무 step

1. **token detect** — Orchestrator 가 사용자 발화 turn 에서 위 regex match 확인 → 매치 시 `codeforge:user-dialog-mode` skill frame mode 진입 4 step 적용 (anchor / drift / declare / verify) per ADR-071 §결정 1
2. **derived default declare (Layer 1 preamble)** — 1 turn 사용자에게 declare 1 문장: "발화하신 `codeforge upgrade` → 다음 default 로 즉시 수행: repo=$(pwd) / mode=dry-run→apply 자동 / channel=overlay resolve→stable / scope=single plugin / dirty tree=abort / 실패 시 자동 rollback. 정정 필요 시 발화 의무." (사용자 정정 의무, AskUserQuestion 0)
3. **derived default 추론** — cwd + consumer overlay `.claude/_overlay/project.yaml::codeforge.channel.tier` resolve + ADR-076 default → CLI arg 합성. consumer overlay 부재 시 fallback `--channel stable`. cwd ≠ consumer repo (overlay 부재) 시 abort + 사실 보고 (AC-7)
4. **immediate invocation** — `bash scripts/codeforge-upgrade.sh --dry-run --repo $(pwd) --channel <resolved>` 즉시 실행 (E10 tool-call-only edge — AskUserQuestion 0, ADR-039 inline whitelist 1번 entry scope 안)
5. **evidence verify + apply 자동 + 1 turn 보고** — dry-run exit code + ImpactReport diff verify → apply 자동 (`--apply --repo $(pwd) --channel <resolved>`) → result enum 4-value 1 turn 보고 (SUCCESS / SUCCESS_WITH_DEGRADATION / PARTIAL_FAILURE / FAILED). ADR-071 §결정 15 frequency suppression touchpoint (c) "최종 완료 보고 1회" 정합.

#### Result enum 4-value (1 turn 보고 정합)

| result enum | 발생 조건 | 보고 형식 |
|---|---|---|
| `SUCCESS` | dry-run + apply 모두 PASS, drift 0 또는 reconcile 완료 | 1 turn 보고 + event log artifact `docs/upgrade-events/<date>-<version>.md` 경로 명시 |
| `SUCCESS_WITH_DEGRADATION` | apply PASS 단 sanity check warning (PR open 등 후속 action 필요) | 1 turn 보고 + sanity check warning 항목 명시 + follow-up action 1 줄 |
| `PARTIAL_FAILURE` | apply 일부 영역 실패 + 자동 rollback 부분 적용 | 1 turn 보고 + 실패 영역 명시 + rollback 상태 명시 + 사용자 정정 의무 declare |
| `FAILED` | dry-run 실패 또는 apply 전체 실패 + 자동 rollback | 1 turn 보고 + 실패 사유 + rollback 완료 명시 + 사용자 정정 의무 declare |

#### Edge cases (CFP-1104 §8 verbatim 발췌)

1. **dirty working tree** (AC-3): abort + 사실 보고 ("dirty working tree — `--force-dirty` 미지원, commit/stash 후 재시도"). [InfraOperationalArch §7.4.5 env containment consult]
2. **cwd ≠ consumer repo** (AC-7): abort + 사실 보고 ("현재 cwd 가 consumer repo 아님, `.claude/_overlay/project.yaml` 부재")
3. **사용자가 `codeforge upgrade beta` 처럼 channel 명시 발화**: regex 확장 fallback — `\bcodeforge\s+upgrade(\s+(stable\|beta\|canary))?\b`. channel 명시 = override → overlay resolve 무시. **본 §3.16.1 scope 안 (closed enum 확장 아님 — 동일 entry 의 optional argument)**
4. **사용자가 `codeforge family upgrade` 명시 발화** (AC-6): closed enum 동일 entry scope 안 single plugin → family 분기. `atomic-upgrade-7-plugins.sh` entrypoint 대체 — single plugin 아님
5. **이미 최신 버전 (no-op)** (AC-4): dry-run 결과 drift=0 → apply 단계 skip + result enum `SUCCESS` + 1 turn 보고 (no-op 명시)
6. **사용자가 `codeforge rollback` 발화**: 본 §3.16.1 closed enum 외 (2번째 trigger token 확장 영역) — 별도 CFP 의무. 본 §3.16.1 미cover, AskUserQuestion 발화 OK
7. **사용자가 `업그레이드해줘` 자연어 (codeforge token 부재)**: trigger 0 — ambiguous, AskUserQuestion 발화 OK (closed enum 외 영역)

#### invariant 요약

- **inv-1** (`user_decision_branches: 0` dialog 단계 확장): step 2 declare 발화 외 AskUserQuestion 0. derived default 자명 영역 (cwd + overlay resolve + ADR-076 default).
- **inv-2** (closed enumeration 1 entry): 2번째 trigger token 신설 = 별도 CFP 의무 + ADR-071 Amendment + SecurityArch consult.
- **inv-3** (ADR-039 inline whitelist 1번 entry scope 안): 5번째 entry 신설 0, 기존 1번 entry "사용자 dialog 허용 영역" 의 derived default 자명성 명문화.
- **inv-4** (ADR-071 §결정 15 frequency suppression 정합): step 5 result enum 보고 = touchpoint (c) "최종 완료 보고 1회".
- **inv-5** (ADR-076 §결정 5 SSOT carrier): CLI 진입점 `scripts/codeforge-upgrade.{sh,ps1}` 변경 0. 본 §3.16.1 = orchestrator 발화 → CLI invocation 단계 mapping carrier.

### §3.17 Orchestrator-authored Issue body pre-publish verify mandate (CFP-1016 / [ADR-082 Amendment 2](../archive/adr/ADR-082-write-time-self-write-verification-mandate.md))

**적용 trigger**: Orchestrator 가 Issue body 를 author 할 때 — 즉 사용자 GitHub Issue Form submit 이 아닌 **Orchestrator-initiated** body authorship:

1. **retro time follow-up Issue** — PMOAgent retro 완료 후 codeforge-improvement / from-cfp-NNN-retro 등 follow-up Issue body 작성
2. **brainstorm Phase 0 후속 Issue** — `codeforge:codeforge-brainstorm` Phase 2 후 별 carrier Story 발의
3. **ADR amendment carrier reservation Issue** — ADR-RESERVATION row 점유 + carrier Story Issue 발의
4. **pattern_count escalation forcing function 산물** — ADR-045 §D-9 pattern_count ≥ threshold 2 → escalation_action `escalate_user` → ADR strengthening carrier Issue 발의

위 4 trigger 중 1+ 시 본 §3.17 mandate 적용.

**verify-before-trust 의무** (Wave 1 behavioral mandate, ADR-082 §결정 1 layer 1 sub-scope (1-B)):

Orchestrator 가 Issue body 안 fact claim 마다 source direct verify 후 author. 모든 fact citation (file path / registry value / lint output / cross-repo state / ADR frontmatter value / amendment count / 카운터 / file existence 등) 을 다음 mechanism 으로 verify:

| claim 종류 | verify mechanism (Orchestrator inline 또는 subagent delegate) |
|---|---|
| local file path / existence | `Bash: ls <path>` 또는 `Read <abs-path>` |
| local file content / line | `Read <abs-path>` 또는 `Grep` |
| origin/main state (cross-repo state assertion) | `git fetch origin && git show origin/main:<path>` (ADR-073 §결정 1 정합) |
| GitHub Issue state | `gh issue view <N> --repo <org>/<repo>` 또는 `mcp__github__issue_read` |
| GitHub file content (cross-repo, 권한 영역) | `mcp__github__get_file_contents` |
| registry value / yaml field | `Read <yaml path>` + 수동 verify |
| ADR frontmatter value | `Read docs/adr/ADR-NNN-*.md` (offset/limit 활용, 첫 50줄) |
| amendment count / amendment_id | `Read docs/adr/ADR-NNN-*.md` frontmatter `amendments[]` array length verify |
| lint output verbatim 인용 | lint output 의 source state 자체 verify (lint regex FP 가능성 — citation ≠ assertion 분리, ADR-082 §결정 4) |

**Issue body 작성 절차** (4-step):

1. **claim enumerate** — Issue body 초안에 포함된 모든 fact claim 을 1-line 단위 분해
2. **verify per claim** — 위 mechanism 표로 claim 각각 verify
3. **verified-via annotation** — Issue body 안 fact citation 옆에 `[verified: <mechanism> <timestamp KST>]` annotation 부착 (또는 verify 결과 본문 통합)
4. **publish** — `mcp__github__issue_write` 또는 `gh issue create` 발화

**Story-level forcing function** (Wave 1 mechanical, ADR-082 Amendment 2 alternative (a)):

본 §3.17 trigger 4종 1+ 충족 시 Orchestrator 가 Story file frontmatter `issue_origin: orchestrator_authored_followup` 부착 의무 → RequirementsPL 이 Story §2.1 verified state table 작성 의무 (story-page-structure.md §2 template 정합). §2.1 = Issue body verbatim claim ↔ verified state ↔ Pivot 판정 4-column schema.

**precedent**:
- **CFP-1000 §2.1** (9-row drift mapping) — 3 inversions catch: `prod-cutover-deputy-evidence` registry presence INVERTED + baseline label-registry 개수 stale (42→44) + `.claude-work/label-registry-bootstrap.json` inexistent
- **CFP-1001 §2.1** (4 claim verify) — L189 lint regex `±5-line context window` cross-paired L185 ADR-040 ↔ L189 ADR-038 → cross-context FALSE POSITIVE catch (Pivot 1 진단)
- **CFP-1002 §2.1** (2 row verify) — ADR-054 filename `-fast-path.md` cited but actual `-story-fast-path.md` catch (1-character-level edit)
- **CFP-1016 §2.1** (META self-application) — 본 ADR-082 Amendment 2 carrier Story, Issue body 4 claims 검증

**Bypass**: 본 mandate 는 behavioral mandate (Wave 1). 응급 fast-publish 영역 (hotfix Issue 등) 에서 `BYPASS_ISSUE_BODY_VERIFY=1` env (Wave 2 mechanical lint 도입 후) → audit trail 보존. Wave 1 = audit trail prose-only (Story §2.1 표 자체).

**Wave 2 progression** (deferred-followup): `scripts/check-story-section-issue-origin.sh` (warning tier, ADR-060 §결정 5 정합) — `issue_origin: orchestrator_authored_followup` 시 §2.1 verified state table 존재 + 4-column schema 정합 lint. 별도 CFP carrier (brainstorm 단계 결정).

**Wave 3 progression** (후순위 ratchet, CFP-1002 precedent 정합): RequirementsPL spawn prompt template (`plugins/codeforge-requirements/` in-tree) explicit verify-before-trust mandate — 별도 CFP carrier 분리.

### §3.18 Multi-session collaboration protocol — lane-entry sentinel ownership verify (CFP-1041 / [ADR-085](../archive/adr/ADR-085-multi-session-collaboration-protocol.md))

#### Trigger

복수 Claude Code session 이 동일 repository / Story / Epic / branch 동시 작업 시 — **모든 lane entry 직전 의무**.

#### 4-step polling subprocess (ADR-085 §결정 3)

lane 진입 직전 Orchestrator (또는 lane PL agent spawn 전) 가 다음 4-step polling 의무 실행:

1. **memory rule 6** (title-based search) — `gh issue list --search "<EPIC>-* in:title parent:CFP-<N>"` (label-based 부재 시 title fallback). 신규 sub-issue 가 다른 session 에 의해 발의되었는가 확인.
2. **memory rule 7** (Epic state poll) — `gh issue view <EPIC> --json state,labels`. Epic 이 다른 session 에 의해 CLOSED 되었는가 확인.
3. **active_sessions[] field check** — Story Issue body `<!-- active_sessions -->` HTML comment block + Story file frontmatter `active_sessions:` array 모두 verify (ADR-085 §결정 2 dual carrier). 본 session 의 entry 가 등록되어 있는가 확인.
4. **lane-entry sentinel** — `gh pr list --search "head:<branch>"` PR existence check. 다른 session 이 이미 PR open 했는가 확인.

위 4-step 모두 통과 시에만 lane entry. 1+ failure → 사용자 dialog 발화 (Inline whitelist 1번 entry, `codeforge:user-dialog-mode` skill 경유) — "parallel session detected, defer / takeover / abandon" 결정.

#### ADR-073 Amendment 2 polling enum cross-ref

본 §3.18 의 4-step polling 은 ADR-073 Amendment 2 §결정 1 transition trigger polling enum 3종 (`lane_spawn` / `pr_open` / `merge_transition`) 의 **4번째 source** (`active_sessions_check`) cross-ref append — ADR-073 Amendment 4 (CFP-1041) cross-ref-only Amendment 정합 (ADR-073 본문 0건 변경 invariant, Amendment 3 = CFP-689 PR #1043 worktree-first self-ownership 3-tuple, #1038 escalation carrier — post-rebase sequence [1,2,3,4] consecutive).

#### Rebase merge 우선 (ADR-085 §결정 4)

lane re-spawn / FIX iter / handoff 시 `git pull --rebase origin main` 우선 (force-push 회피). force-push 필수 영역 = `--force-with-lease=branch:sha` + HEAD-pin pre-flight gate 의무 (`gh api repos/<owner>/<repo>/commits/<branch> --jq .sha` fresh 재고정 후 push). memory `feedback_verify_pin_head_sha` carrier 정합.

#### Handoff baton transfer (ADR-085 §결정 5)

In-flight FIX baton transfer (Session A → Session B handoff) 시 의무:

1. **Session A** — §10 FIX Ledger row append (Orchestrator monopoly, fix-event-v1 contract) + active_sessions[] entry update `last_heartbeat_kst` + Story §9 evidence write + `git push origin <branch>`.
2. **Session A** — handoff comment to Story Issue `[handoff:CFP-NNNN]` (comment-prefix-registry-v1 14번째 entry — 별 sub-CFP carrier).
3. **Session B** — lane entry 4-step polling 통과 후 `git pull --rebase origin <branch>` + active_sessions[] entry append + fix_iter_ownership populate (handoff_from / handoff_to / fix_iter_number / handoff_at_kst / handoff_reason).

handoff_reason enum: `context-budget-exhausted` / `user-redirect` / `structural-restart-ADR-053` / `other`.

#### Wave 1 vs Wave 2 progression

- **Wave 1 (현재)**: declarative-only (ADR-082 §결정 6 + ADR-070 §D5 retain pattern 답습). Orchestrator self-discipline + lane PL spawn 직전 manual 4-step polling.
- **Wave 2 (별 sub-CFP carrier)**: mechanical wire — `templates/scripts/check-active-sessions-presence.{sh,py}` + `templates/scripts/check-lane-entry-ownership.{sh,py}` + `templates/github-workflows/active-sessions-presence.yml` + `templates/github-workflows/lane-entry-ownership-verify.yml` + bats test suite (evidence-checks-registry `active-sessions-presence` + `lane-entry-ownership-verify` 2 entry warning tier deferred-followup, ADR-060 §결정 5 정합).

#### Cross-ref

- ADR-085 §결정 1 5-layer disjoint 표 (ADR-082 §결정 1 4-layer 표 verbatim 답습 + 5번째 row Multi-session coordination 신설) — coordination axis disjoint complement.
- ADR-073 Amendment 4 + ADR-082 Amendment 3 cross-ref-only Amendment (본문 0건 변경 invariant).
- 8 parallel race incidents single session lineage evidence (CFP-953/946/949/932/954/991/967/1014, 2026-05-18 ~ 2026-05-19 KST) — ADR-045 §D-9 cross_story_pattern_adr_trigger pattern_count ≥ 8 reach escalation_action `adr_draft_emitted` 산물.

---

## 4. 병렬 스폰 판단

### 4.1 병렬 가능 조건 (AND)

1. **경로 분리**: 쓰기 대상 파일 경로가 겹치지 않음 (path-scoped 권한으로 보장)
2. **입력 독립**: 한쪽 산출물이 다른 쪽 입력이 아님
3. **완료 대기 가능**: 모든 병렬 에이전트 완료 후 종합 판단 가능

### 4.1.1 결정 원칙 mandate — parallel default + sequential 강제 3 사유 (ADR-064)

[ADR-064](../archive/adr/ADR-064-decision-principle-mandate.md) §결정 4 가 §4.1 의 normative 강화 — multi-task spawn default 는 **parallel** (단일 메시지 다중 Agent tool call). sequential 선택은 다음 3 사유 중 1 종 명시 의무. 3 사유 모두 부재 = default parallel.

| Sequential 강제 사유 | 운영 사례 |
|---|---|
| **state dependency** | task N+1 이 task N 출력 (Story file section / ADR 번호 / 합의 결과) 입력 의존 — 예: ArchitectAgent §3 ADR 결정 → §7 설계 서사 |
| **shared resource** | 동일 file write / 동일 GitHub label 변경 / 동일 branch commit / ADR 번호 sequential append — 예: ADR-RESERVATION row append |
| **ordering invariant** | 출력 ordering 자체가 의미 — 예: FIX Ledger row append (시간 순), commit chain |

본 룰은 ADR-039 §결정 7 `policy_violation_subdecision` 결정 영역 확장 — sequential 선택 시 spawn prompt 또는 commit message 에 사유 1 종 명시. derived default 가 부재한 영역 = AskUserQuestion 발화 의무 (ADR-064 §결정 3 룰 5 정합).

#### 결정 제안 시점 self-check checklist

Orchestrator 가 결정 제안 (brainstorm Phase 1 / writing-plans / Issue Form 제출 / lane spawn prompt 작성) 직전 다음 5 항목 self-check:

1. **forbid-list 어휘 회피** — 결정 menu 후보 텍스트에 ADR-064 §결정 2 dictionary 8 어휘 등장 여부 확인 (dictionary 본문 / 외부 인용 영역 제외). 등장 시 대체 어휘로 reformulation.
2. **Derived default 도출** — 컨텍스트 (사용자 명시 + memory + Story file + ADR 인용) 로 합리적 default 도출 가능 시 `AskUserQuestion` 생략, derived default 직접 declare.
3. **식별자 사전 요약** — ADR / CFP / 코드 식별자 인용 시 핵심 결정 1 문장 요약 사전 제시.
4. **옵션 수 제한** — 후보가 2+ 이면 권장 1 + 대안 1 (최대 2). 3+ 후보 = brainstorm Phase 0 영역으로 격상.
5. **CFP scope unitary 확인** — 한 CFP 안 "경량 → full" 단계 분기 회피. 별개 CFP 분리 채택.

### 4.2 표준 병렬 패턴

| 패턴 | 구성 | 조건 충족 |
|------|------|----------|
| **요구사항 레인** | DomainAgent ∥ Analyst ∥ Researcher | 셋 모두 공통 입력만 수신, 타 산출물 미참조 → 입력 독립. PL이 통합 단계에서 dedup·상충 조정 |
| **설계 레인** | CodebaseMapper ∥ Refactor ∥ SecurityArchitect ∥ TestContractArch ∥ ModuleArchitect | 다섯 다 원 소스(코드·ADR·Change Plan 초안) 직접 독해, 타 산출물 미참조 → 입력 독립. ArchitectAgent (chief author)가 교차 검토 → ArchitectPLAgent 검수 |
| **설계 리뷰** | ClaudeReviewAgent ∥ CodexReviewAgent (lane=design packet) | 읽기 전용, 정규화 스키마 동일 |
| **구현 리뷰** | ClaudeReviewAgent ∥ CodexReviewAgent (lane=code packet) | 동일 |
| **보안 테스트** | ClaudeReviewAgent ∥ CodexReviewAgent (lane=security packet) | 동일. 워커는 lane-agnostic, PL이 packet으로 도메인 분기 |
| **구현** | DevPL(`role: dev` roster 병렬) + QADev(tests/**) | 쓰기 경로 분리 — roster 전체 의존성 없는 한 병렬 |

### 4.3 병렬 일부 실패 시

- **모두 완료 대기**가 원칙 — iteration 낭비 방지
- 예외: ClaudeReview가 [P0]를 즉시 내면 Codex 대기 없이 FIX 진입 가능 — 단 Codex 완료 후 결과 병합해 Story file §9에 기록

### 4.4 Clarification 재조사 채널 (요구사항·설계 레인 공통)

#### 4.4.0 4-layer counter disjoint 표 (ADR-077 §결정 5)

4개의 별개 반복 카운터가 codeforge에 병존한다. 카운터 간 합산·cap 공유는 cross-pollinate 금지 normative (ADR-077 §결정 5 + ADR-067 cross-lane 합산 금지 정합).

| layer | 채널 | 카운터/한도 | owner | §10 합산 |
|---|---|---|---|---|
| 1. scope 정교화 | 재조사 카운터 | `recheck_counter_cap = 5` (ADR-077 §결정 4, ESCALATE 초과) | RequirementsPL (§9.0) | 금지 |
| 2. 품질 게이트 | §10 FIX Ledger | lane 당 max 3 (ADR-067) | Orchestrator monopoly (fix-event-v1) | — (본 채널) |
| 3. PL재량 재스폰 | §4.4.2 2회 한도 | 동일 에이전트 2회 (초과 시 ESCALATE §2.3) | PL (RequirementsPL/ArchitectPL) | 금지 |
| 4. adversarial 합의 | debate round counter | min 3 / max 5 (ADR-059 debate-protocol-v1) | DesignReviewPL | 금지 |

본 표 = ADR-077 §결과 절 4-layer cross-declare 의 2번째 cross-declare 위치 (1번째 = ADR-077 §결정 5/§결과 절, 3번째 = requirements-output contract schema = Story-4 carrier).

#### 4.4.1 사용자 clarification 답변 수령 시 강제 fan-out 6 절차 (ADR-077 §결정 1/2/7/10)

사용자가 "사용자 확인 필요" 답변을 제공한 시점 = dirty 이벤트. 다음 절차를 **무조건 실행** (PL 재량 분기 · "변화없음 → 통합만" skip 금지):

1. clarification 답변 수령 = dirty 이벤트 (**value-equality skip 비차용 invariant** — 답변 내용이 이전과 의미상 동치여도 skip 금지, ADR-077 §결정 1).
2. envelope coalesce: 답변 burst → debounce (P-1) → max-wait ceiling 도달 시 강제 → 단일 fan-out (coalesce 단위 1). **정량값 = ADR-077 §결정 4 정량 표 cross-ref (본문 평문 기재 금지 — TBD marker 정합, ADR-068 Amendment 1 I-5)**.
3. 6 sub-agent **parallel always-executable** fan-out (ADR-077 §결정 10 / ADR-064 §결정 4 parallel default — sequential 3 사유 [state dependency / shared resource / ordering invariant] 부재 시 default parallel): DomainAgent(§2) + RequirementsAnalyst(§5) + Researcher(§6) + FeasibilityAgent(§4.2) + ContinuityAgent(§4.3) + ChangeImpactAgent(§4.1).
4. **조건부 PMO 가산**: 답변 영향이 Epic/Story 구조 도달 시 PMOAgent 합류 (재분해). contrapositive invariant "PMO 합류 미발동 = Epic 구조 무변경" (ADR-077 §결정 2 P-5 closed enum SSOT). ADR-045 retro trigger와 origin disjoint.
5. **정보 무결성 invariant (ADR-077 §결정 7 — SecurityArch P1)**: 재조사 sub-agent는 `prior_output_ref` 의 fact-check marker 4종 (`[verified]` / `[hypothesis]` / `[fact-check-pending]` / `[user-input]`) + reverse-explicit `[verification-out-of-scope: <사유>]` 를 **verbatim 보존**. `[hypothesis]` / `[fact-check-pending]` → `[verified]` **무검증 승격 금지** (ADR-052 Amendment 3 무손상). marker 부재 = 암묵 `[hypothesis]` default 유지.
6. PL 재종합 (ADR-056 합성 순서: §5 Analyst → §2 Domain → §6 Researcher → PL) + 재조사 카운터 §9.0 기록 (§10 FIX Ledger 합산 금지 — §4.4.0 layer 1).

#### 4.4.2 PL 재량 재스폰 절차 (layer 3 — §4.4.1 clarification-driven fan-out과 trigger origin disjoint)

서브 에이전트는 one-shot 실행이라 PL↔서브 continuous dialog 불가. PL(RequirementsPL 또는 ArchitectPLAgent)이 병렬 결과 통합 중 추가 질의가 필요하면:

1. PL이 Orchestrator에 재스폰 요청 페이로드 전달:
   - 대상 에이전트명
   - 이전 본인 출력 pointer (Story file 참조 또는 메모리 slice)
   - clarification context (무엇을 추가로 묻는가, 왜)
   - 범위 제한 (전면 재분석 vs 특정 섹션 보강)
2. Orchestrator가 해당 에이전트를 **신규 스폰** — frontmatter에 `rspawn_reason` + `prior_output_ref` 기록
3. 에이전트가 이전 출력을 참조 + 추가 범위만 분석해 보강 산출물 반환
4. PL이 재수령 후 통합 단계 반복
5. 재스폰 이력은 **Story file §9.0 "Clarification 재스폰 이력"** 에 append (RequirementsPL 직접 §9.0 append — codeforge-requirements self-write). §10 FIX Ledger와 분리 — 재스폰은 게이트 실패 아니며 GitHub `fix:*` 라벨 미추가

**무제한 재스폰 금지** — 동일 에이전트 2회 재스폰 이후에도 미해소면 사용자 ESCALATE로 전환 (§2.3).

---

## 5. docs/stories file 동기화

### 5.1 Lane plugin self-write 체크리스트

ζ arc decomposition (CFP-31~CFP-40) 후 write 책임은 lane plugin 별로 분산. 아래 표는 각 트리거 시점에 어떤 agent 가 어디에 직접 write 하는지 정리.

| 트리거 | 갱신 path | 책임 agent |
|--------|----------|------------|
| Issue Form 제출 | Story §1 verbatim + Phase 1 PR | story-init.yml Action 자동 |
| RequirementsPL 통합 완료 | Story §2/§5/§6 | RequirementsPLAgent (codeforge-requirements) |
| DomainAgent 지식 공백 발견 시 | `docs/domain-knowledge/<area>/<topic>.md` | DomainAgent (codeforge-requirements) |
| RequirementsPL 통합 후 ADR / 코드 경로 갱신 | Story §3/§4 | RequirementsPLAgent (codeforge-requirements) |
| ArchitectAgent Change Plan + ADR 확정 | `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md` + Story §3/§7/§11 | ArchitectAgent (codeforge-design) |
| 설계 리뷰 iteration 종료 (ReviewPL packet return) | (no direct write — packet only) | DesignReviewPLAgent (codeforge-review, review-verdict-v3 pl_recommendation) |
| 설계 리뷰 PASS/FIX verdict final write | Story §9.1 + GitHub comment [설계-리뷰] + gate:design-review-pass label + phase transition + Story §12 row | **Orchestrator 단독** (CFP-61 / ADR-022 review-verdict 5-step step 4) |
| 구현 완료 | Story §8 + §8.5 Impl Manifest + Phase 2 PR creation | DeveloperPLAgent (codeforge-develop) |
| 구현 리뷰 iteration 종료 (ReviewPL packet return) | (no direct write — packet only) | CodeReviewPLAgent (codeforge-review, review-verdict-v3 pl_recommendation) |
| 구현 리뷰 PASS/FIX verdict final write | Story §9.2 + GitHub comment [구현-리뷰] + phase transition + Story §12 row | **Orchestrator 단독** (CFP-61 / ADR-022 review-verdict 5-step step 4) |
| 구현 테스트 종료 (CI gate) | Story §9.3 (`gh pr checks` 결과 — Orchestrator 직접 기록) | **Orchestrator 단독** (ADR-048 CI gate inline) |
| 통합 테스트 종료 (IntegrationTestAgent) | Story §9 통합 테스트 섹션 append + `phase:보안-테스트` 전환 | Orchestrator 단독 |
| 보안 테스트 iteration 종료 (ReviewPL packet return) | (no direct write — packet only, lanes.security_ai: true 시만) | SecurityTestPLAgent (codeforge-review, review-verdict-v3 pl_recommendation) |
| 보안 테스트 PASS/FIX verdict final write | Story §9.4 + GitHub comment [보안-테스트] + gate:security-test-pass label + phase transition + Story §12 row | **Orchestrator 단독** (CFP-61 / ADR-022 review-verdict 5-step step 4) |
| FIX 발생 | Story §10 FIX Ledger append | **Orchestrator 단독** (CFP-32 fix-event-v1 monopoly) |
| PMOAgent 회고 | `docs/retros/<sprint>.md` + Story §11 + Epic Milestone close | PMOAgent (codeforge-pmo) |
| 단계별 상태 변화 | GitHub Issue comment `[<phase>] <Agent>: <한 줄>` | review-verdict 영역 → Orchestrator (CFP-61); 기타 → 각 lane plugin

### 5.2 Story file 읽기 규약

- **필요한 섹션만 읽기**: 프롬프트에 `§X, §Y 참조` 명시 → 에이전트가 `Read(docs/stories/<KEY>.md)` 후 해당 섹션만 참조
- 전체 file 읽기는 ArchitectAgent (chief author) 설계 진입 1회만 허용 (§1-6 전체 필요)
- file 변경 권한 분담 (CFP-26 Phase 0a 이후):
  - `docs/change-plans/**` + `docs/adr/**` → **ArchitectAgent direct**
  - `docs/domain-knowledge/**` → **DomainAgent direct**
  - `docs/retros/**` → **PMOAgent direct**
  - `docs/stories/**` 각 섹션 → 해당 lane plugin self-write (§5.1 표 참조). §10 FIX Ledger → **Orchestrator 단독** (CFP-32 fix-event-v1). §9 (review-verdict) + §12 (Sonnet Decision Log) → **Orchestrator 단독** (CFP-61 / ADR-022 review-verdict final write)
  - `docs/**` general (orchestrator-playbook, plugin-design, consumer-guide 등) → Orchestrator 또는 수동
  - GitHub Issue/PR/comment + label → review-verdict 영역 ([설계-리뷰] / [구현-리뷰] / [보안-테스트] comment + gate/phase label) → **Orchestrator 단독** (CFP-61 / ADR-022). 기타 → 각 lane plugin self-write (codeforge-{review,pmo,requirements,test,develop,design} CLAUDE.md self-write 표)
  - 그 외 모든 에이전트는 자기 owner section 에만 직접 write — 4 single-owner type(`change-plan`/`adr`/`domain-knowledge`/`retro`)은 owner agent direct write (CFP-26 Phase 0a)

### 5.3 GitHub Issue body vs Story file

| 위치 | 내용 |
|------|------|
| Story Issue body | "Story SSOT: `docs/stories/<KEY>.md`" 한 줄 링크 (story-init.yml이 자동 변환) |
| docs/stories/<KEY>.md | 전체 컨텍스트·서사 (§1-11 규격) |
| Story Issue comments | 단계별 이벤트 로그 (각 lane plugin 이 자기 phase prefix `[<phase>] <AgentName>: <한 줄>` 형식으로 직접 기록) |

GitHub Issue는 워크플로우 상태·이벤트, docs file은 구조화 영속 — 역할 분리.

---

## 6. FIX 루프 상태 머신

### 6.1 카운터 SSOT = `docs/stories/<KEY>.md` §10 "FIX Ledger"

**GitHub 라벨은 대시보드용 보조 지표**. 카운터 판정·리셋 해석은 반드시 §10 기반.

```python
# 의사 코드
content = Read(f"docs/stories/{KEY}.md")
ledger = parse_section(content, "## 10. FIX Ledger")
rows = parse_ledger_rows(ledger)

# "현재 사이클" = 가장 최근 RESET 마커 이후 행들
for lane in ["설계-리뷰", "구현-리뷰", "구현-테스트", "보안-테스트"]:
    last_reset_idx = max(i for i, r in enumerate(rows) if r.reset == lane)
    current_cycle_count = sum(1 for r in rows[last_reset_idx+1:] if r.lane == lane)
```

§10 스키마·Orchestrator 갱신 절차: Orchestrator 단독 append-only 관리 (CFP-32 monopoly · fix-event-v1 contract).

§10에 새 행 commit 시 `fix-ledger-sync.yml` Action이 자동:
1. Story Issue에 `[FIX #N]` 코멘트 mirror
2. `fix:<레인>-retry` 라벨 자동 부착

### 6.1.1 Lighter mode — CI iteration 통계 가 §10 alternate evidence (CFP-92, P2-8)

mctrader debut audit Issue [#181](https://github.com/mclayer/plugin-codeforge/issues/181) P2-8 finding: §10 FIX Ledger 사용이 sparse — early Stories (MCT-1/2/3) 만, 최근 Stories (MCT-25 등) §10 부재. mctrader 실제 패턴 = `EPIC-RESULTS-<KEY>.md` §9 CI iteration 통계 가 §10 alternate 역할 (CI failure 별도 root cause 표).

본 lighter mode 정책:

- **§10 row append 의무 = lane verdict 기반 (review FIX / test FAIL)** — 변경 없음 (fix-event-v1 contract 유지)
- **CI failure (mechanical fix-up, push-fail-fix iteration)** = §10 row 의무 **없음** — EPIC-RESULTS §9 CI iteration 통계 표 가 evidence
- 즉 **review-verdict 기반 FIX (lane gate FAIL)** vs **CI iteration (mechanical push retry)** 가 분리된 추적 mechanism 보유
- PMOAgent 가 Story 완료 시 두 source 모두 evidence pack 으로 회고

**§10 vs §9 CI iteration 구분 표**:

| 발생 사건 | §10 row 의무 | EPIC-RESULTS §9 CI iteration |
|---|:-:|:-:|
| DesignReviewPL FIX verdict | ✅ | (Phase 1 PR 의 push retry 별도) |
| CodeReviewPL FIX verdict | ✅ | (Phase 2 PR 의 push retry 별도) |
| CI gate FAIL (구현 테스트 — ADR-048) | ✅ | — |
| SecurityTestPL FIX verdict (lanes.security_ai: true 시만) | ✅ | — |
| CI ruff / pyright / lint failure → push retry | ❌ | ✅ (PR # / pushes / failures / root cause 표) |
| Mechanical fix-up (typo / formatting / minor naming) | ❌ (CFP-19 R11 mechanical fast-path) | ✅ |

**효과**:
- Story §10 = "lane gate verdict" 의 audit trail 만 carry — high-signal
- EPIC-RESULTS §9 = "CI iteration mechanical retry" 의 audit trail — low-signal but completeness
- 기존 §10 의무 retain (CFP-32 contract 유지) — Implementation Story 의 review FIX 추적 source 동일

### 6.2 트리거 → 상태 전이

| 현재 phase | 트리거 | 전이 후 phase | §10 행 추가 | 라벨 동작 (자동) |
|-----------|--------|---------------|-------------|-----------|
| 설계-리뷰 | DesignReviewPL FIX | 설계 | Iter N / 설계-리뷰 / 원인=설계 / 재실행 범위 | `fix:설계-리뷰-retry` |
| 설계-리뷰 | DesignReviewPL PASS | 구현 | — | `gate:design-review-pass` 부착 + phase 라벨 변경 |
| 구현-리뷰 | CodeReviewPL FIX (원인=구현) | 구현 | Iter N / 구현-리뷰 / 원인=구현 / 재구현 | `fix:구현-리뷰-retry` |
| 구현-리뷰 | CodeReviewPL FIX (원인=설계) | 설계 (Phase 1 follow-up PR) | Iter N / 구현-리뷰 / 원인=설계 / Change Plan 갱신 | `fix:구현-리뷰-retry` (§10 행의 `lane` 컬럼 기준 — fix-ledger-sync.yml은 single-label 부착. 설계 회귀는 원인 판정 컬럼으로 식별, 이후 설계 리뷰 재실행 시 별도 §10 행 추가되어 `fix:설계-리뷰-retry` 라벨 자동 부착) |
| 구현-리뷰 | CodeReviewPL PASS | 구현-테스트 (CI gate) | — | (phase 전이만) |
| 구현-테스트 | CI gate FAIL (원인=구현) | 구현 | Iter N / 구현-테스트 / 원인=구현 / 재구현 + **RESET 구현-리뷰** | `fix:구현-테스트-retry` |
| 구현-테스트 | CI gate FAIL (원인=설계) | 설계 (Phase 1 follow-up PR) | Iter N / 구현-테스트 / 원인=설계 / Change Plan 갱신 + **RESET 구현-리뷰** | `fix:구현-테스트-retry` |
| 구현-테스트 | CI gate ALL PASS + lanes.security_ai: false | 완료 (merge gate) | — | (phase 전이만) |
| 구현-테스트 | CI gate ALL PASS + lanes.security_ai: true | 보안-테스트 | — | (phase 전이만) |
| 보안-테스트 | SecurityTestPL FIX (원인=구현) (lanes.security_ai: true 시만) | 구현 | Iter N / 보안-테스트 / 원인=구현 / 재구현 + **RESET 구현-리뷰** | `fix:보안-테스트-retry` |
| 보안-테스트 | SecurityTestPL FIX (원인=설계) (lanes.security_ai: true 시만) | 설계 (Phase 1 follow-up PR) | Iter N / 보안-테스트 / 원인=설계 / Change Plan 갱신 + **RESET 구현-리뷰** | `fix:보안-테스트-retry` |
| 보안-테스트 | SecurityTestPL PASS (lanes.security_ai: true 시만) | 완료 | — | `gate:security-test-pass` 부착 → Phase 2 PR mergeable → merge → Issue auto-close |

### 6.3 RESET 마커 규칙

- 구현 테스트 FAIL 또는 보안 테스트 FAIL → 구현 복귀 시 §10 마지막 행의 `RESET?` 컬럼에 `RESET 구현-리뷰` 기입
- 이후 구현 리뷰 카운터는 RESET 행 이후 iteration만 카운트 (이전 iteration은 감사 이력으로 유지)
- 설계 리뷰·구현 리뷰 내부 루프는 RESET 없음

### 6.4 Max FIX counter implementability reassessment (CFP-526 / ADR-067)

설계-리뷰 카운터 3/3 또는 구현-리뷰 카운터 3/3 도달 시, OR cross-lane cumulative_P0≥2 OR cumulative_P1≥5 OR reviewer_divergence_count≥2 (ADR-067 §결정 6 dual metric — MCT-150 §10 row 1-4 corroboration evidence) 시 ArchitectPL 재량 implementability reassessment 수행 의무.

**3 escalation trigger (i/ii/iii) 중 1+ 충족 시 사용자 escalation 의무** (ADR-067 §결정 3):

- (i) ESCALATE root cause = "design granularity inadequate"
- (ii) cross-module invariant 위반 without convergence path
- (iii) DeveloperPL ↔ ArchitectPL N+1 round divergence 유지

**0 충족 시 RESET path 선택 가능** (사용자 escalation 생략).

사용자 escalation 시 다음 Option A/B/C 표면 의무:

- **Option A**: RESET — design 또는 code 카운터 재시작
- **Option B**: 요건 자체 재정의 — Story 분할 또는 scope 축소
- **Option C**: Wave delegation — cross-Wave dependency 처리 후 본 Story 재진입

사용자 directive 2026-05-13 cross-ref: "타협이 어려웠던 부분을 기준으로 보수적으로 평가" — ArchitectPL reassessment 시 수렴 가능성 판단에 적용. SSOT: [ADR-067](../archive/adr/ADR-067-fix-ledger-implementability-escalation.md).

### 6.5 Cross-lane RESET 정책 (Pause-and-resume, CFP-526 / ADR-067)

각 lane별도 독립 카운터 (각 max=3):

- 설계-리뷰 카운터: 설계-리뷰 lane FIX iteration 전용
- 구현-리뷰 카운터: 구현-리뷰 lane FIX iteration 전용
- 보안-테스트 카운터: 무제한 (§6.7 fix-event-v1 schema 정합)

**cross-lane FIX 발생 시 합산 금지** (decision noise 회피):

- escalation lane (예: 보안-테스트) 에서 FIX 처리 시 design/code lane 카운터를 보존
- escalation lane FIX 완료 후 보존된 design/code lane 카운터 resume (Pause-and-resume)
- 사용자 directive Edge Case #2 처리 (Analyst): escalation 중 신규 lane (예: 보안-테스트) FIX 발생 시 design/code 카운터 보존 의무

SSOT: [ADR-067 §결정 4](../archive/adr/ADR-067-fix-ledger-implementability-escalation.md).

### 6.6 §10 FIX Ledger reasoning_carryover field (CFP-526 / ADR-067)

fix-event-v1 v1.2 (ADR-067 §결정 5) — §10 row 9번째 optional column. ArchitectPL re-spawn 시 직전 row의 reasoning_carryover full-text를 입력으로 전달 의무 (architectural amnesia 차단).

**3-part structured YAML schema**:

```yaml
reasoning_carryover:
  invariant_summary: "<50자 이내, immutable boundary 요약 — 변경 차단 영역>"
  disputed_claims: "<100자 이내, FIX iter 내 unresolved 영역 — 다음 cycle input>"
  transcript_ref: "<Story §9 anchor link — 예: #debate-transcript-F-001>"
```

**ArchitectPL re-spawn 절차**:

1. 직전 §10 row에서 reasoning_carryover 추출 (null 시 skip — 첫 iter 또는 미사용 iter)
2. ArchitectPL spawn 시 reasoning_carryover full-text를 spawn 입력에 포함
3. ArchitectPL이 reasoning_carryover 기반으로 설계 검토 (invariant_summary 영역 변경 차단 / disputed_claims 영역 집중 검토)

debate-protocol-v1 v1.1 의 debate_artifact_ref pattern과 직교 — debate 발동 여부와 무관하게 독립 적용. backward-compat: 기존 row null 또는 column 생략 모두 valid. SSOT: [fix-event-v1 v1.2](../docs/inter-plugin-contracts/fix-event-v1.md) + [ADR-067](../archive/adr/ADR-067-fix-ledger-implementability-escalation.md).

### 6.7 §10 관리 세부

- **Orchestrator가 단독 갱신** (CFP-32 ζ arc F1부터 — fix-event-v1 monopoly). append-only, 행 삭제·수정 금지
- Schema SSOT: [`docs/inter-plugin-contracts/fix-event-v1.md`](../docs/inter-plugin-contracts/fix-event-v1.md) — row 필드 + append 규칙 + RESET 시맨틱스. **현재 schema = v1.3 (CFP-842 — depth-aware scope optional fields, 11 column)**.
- Stale-read 방지: Orchestrator가 Edit 직전 `git pull --rebase` 또는 file mtime 비교 후 append. 충돌 시 fail-fast + 사용자 ESCALATE (자동 재시도 금지 — append-only ledger 손상 위험)
- Lane plugin은 FIX event를 Orchestrator에 verdict로 보고 (status=FIX 또는 test FAIL). lane plugin이 §10 직접 Edit 금지 — CFP-34 deliverable `story-section-write-guard.yml`이 enforce
- §10 조회 실패(파일 부재 등) → ArchitectPLAgent 판정 정지 → 사용자 판단 요청
- GitHub 라벨은 `fix-ledger-sync.yml` Action이 §10 commit 감지 시 자동 부착 — 단방향 mirror (§10 → label/comment). 대시보드 search syntax 필터용

**v1.3 depth-aware scope 필드 의무 (CFP-842, broken-link/path 정정 FIX 한정)**:

`affected_paths_with_depth` 필드는 broken-link / path 정정 FIX (cross-module relative path adjust / doc-location-registry move / link target 갱신 등) 시 **의무**. 그 외 FIX (logic bug / API change / perf regression / wording desync 등) = optional. 누락 시 `fix-event-depth-scope-presence` warning-tier lint (advisory only, blocking-on-pr 미승격) 적발.

기록 형식:
```yaml
affected_paths_with_depth:
  - {path: "docs/adr/ADR-067.md", depth: 2}
  - {path: "templates/github-workflows/fix-ledger-sync.yml", depth: 2}
  - {path: "CLAUDE.md", depth: 0}
```

`depth` = repo root 기준 dir depth (root level file = 0, depth 1 dir 안 file = 1, ...). 정정 규칙 적용 범위 (예: `depth >= 2 then path adjust = '../../'`) 의 mechanical reasoning trace 보존 — CFP-770 §8 CR-005→CR-006→CR-007 over-correction regression chain lesson directly 차단 carrier. broken-link/path FIX 시 depth 정보 부재가 directly carrier 였음.

`affected_scope` 필드 (enum: single-file / cross-module / cross-repo / cross-plugin) 는 broken-link/path FIX 영역과 무관하게 **모든 FIX** 에서 optional — RESET 범위 결정 input. cross-module / cross-repo / cross-plugin scope = ArchitectPL 가 cross-lane RESET 적극 검토 (ADR-067 §결정 4 Amendment 1). single-file scope = 동일 lane FIX iter 유지 (RESET 회피).

### 6.8 원인 판정 decision table

[CLAUDE.md](../CLAUDE.md) "원인 판정 decision table" 섹션이 SSOT — 본 playbook은 표를 inline 복제하지 않는다 (drift 방지). Orchestrator는 FIX 트리거 시 CLAUDE.md 표를 직접 참조해 DeveloperPL/ArchitectPLAgent 전달용 evidence pack을 구성.

**ArchitectPLAgent 최종 판정 + evidence pack(Change Plan 버전 + 리뷰 findings + 테스트 로그) 첨부 의무**.

#### 6.8.1 Mechanical reconciliation pattern — grep BEFORE sed (CFP-464, CFP-500 FIX-2/3 학습)

ArchitectPL re-spawn FIX 처리 시 reconciliation 의무 4-step (partial reconciliation anti-pattern 차단):

1. **COMPREHENSIVE grep BEFORE sed** — target keyword/pattern 양 worktree 전수 검색 (file scope full, not just self-report)
2. **Report grep results** — 발견된 모든 occurrence enumerate 보고 후 처리 결정 (partial 적용 금지)
3. **sed applied** — 발견된 모든 occurrence 정정 (audit trail 예외 명시)
4. **Re-grep verify** — sed 후 잔존 0건 확인 (audit trail 제외)

evidence: CFP-500 설계 lane FIX iter 2/3 partial reconciliation (self-report 영역만 정정, sweep 누락 → recurrence). Iter 4 grep sweep mandate 후 단번에 해소.

본 단계는 codeforge-design plugin ArchitectPLAgent template 의 mechanical reconciliation 영역으로 본 playbook §6.8 의 augmentation. cross-plugin enforcement 자체는 별도 follow-up (codeforge-design plugin version bump 동반).

### 6.9 Parallel diagnosis (R4, [CFP-19 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

review·테스트 FIX (구현 리뷰·구현 테스트·보안 테스트) 시 DeveloperPL 1차 진단과 ArchitectPL 최종 판정을 **병렬 spawn**한다 (한 메시지에 dispatch).

**절차**:
1. Orchestrator가 FIX verdict 수령
2. 한 메시지에 두 에이전트 동시 spawn:
   - DeveloperPL: 1차 원인 진단 (구현 / 설계) — 결과 typed return (CFP-32부터 §10 직접 write 안 함, Orchestrator가 받아서 §10 append)
   - ArchitectPL: 최종 판정 — review findings + Change Plan + ADR 정합성 평가 (DeveloperPL 결과 미수신, 독립 판단)
3. 두 결과 수령 후 비교:
   - **일치 (양쪽 동일 원인)**: 해당 원인 그대로 진행 (구현 commit append 또는 Change Plan 갱신)
   - **불일치**: ArchitectPL verdict 우선 (chief judge 책무 보존). DeveloperPL 진단을 §10 row 비고에 archive

**낙관적 가속 가정**: 80% 케이스 일치 → 직렬 5-10분을 병렬 2-3분으로 단축. 20% 불일치 시 ArchitectPL 우선이라 retry overhead 없음.

**제약**: 설계 리뷰 FIX는 본 절 범위 외 — DeveloperPL 미개입 (기존 절차: ArchitectPL 직접 회귀).

### 6.10 Mechanical fast-path (R11, [CFP-19 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

ReviewPL verdict packet의 `mechanical_category` 필드 (typo / broken-link / minor-naming / comment-only / none — SSOT codeforge-review plugin (plugins/codeforge-review/) 의 `templates/review-pl-base.md` §3 R11 절) + severity 조합으로 fast-path 자격 판정:

**자격 조건**: `mechanical_category != none` AND (severity = P2 OR (severity = P1 AND 영향 파일 수 = 1))

**자격 충족 시 절차**:
1. Orchestrator가 §6.6 parallel diagnosis 건너뛰고 DeveloperPL 직접 spawn (fix-only 모드)
2. DeveloperPL이 fix commit
3. **same-iteration internal verify** — 다음 review iteration이 동일 finding 검출 안 하면 PASS, 검출 시 Iter row append (정상 cycle 회복)
4. §10 ledger 신규 row 안 매김 (fast-path는 카운터 증가 안 함)

**자격 미충족 또는 분류 잘못**: 다음 review iteration이 P0/P1 검출 → 정상 §6.6 cycle.

**제약**: 보안 lane의 injection / credential / CVE / trust-boundary 카테고리는 항상 `mechanical_category = none`이라 fast-path 자격 없음 (codeforge-review plugin (plugins/codeforge-review/) 의 `templates/review-pl-base.md` §3 R11 SSOT).

### 6.11 Spec amendment loop (CFP-87)

mctrader debut audit Issue [#181](https://github.com/mclayer/plugin-codeforge/issues/181) P1-7 finding (Opus 자체 발견): mctrader-hub PR [#72](https://github.com/mclayer/mctrader-hub/pull/72) (`[MCT-50/51] Spec amendments — Codex push-back 6건`) — Phase 3 implementation 진행 중 Codex review 가 발견한 push-back 6건 → spec doc 수정 PR (Story file `MCT-50.md` + `MCT-51.md` amendment) 으로 캡처 후 implementation 재개. 매우 가치 있는 패턴이나 codeforge SSOT 미정의 — 본 §6.8 codify.

#### 6.11.1 Trigger

다음 중 하나 발생 시 Spec amendment loop 진입 (FIX 루프 §6.1-§6.7 와 별도):

- **Codex push-back during implementation**: Phase N implementation (Phase 2~N PR 작업) 중 Codex review 또는 자율 검토 시 spec gap 발견 (Story file §1-§7 unspecified / inconsistent)
- **사용자 mid-implementation requirement clarification**: 구현 중 사용자가 새 AC 제시 또는 기존 §1 의미 재해석
- **Spec drift 발견**: implementation 진행 중 §7 설계 결정과 코드 사이 drift 발견 (코드 측 fix 만으로 해결 안 되는 경우)

§6.1-§6.7 FIX 루프 와 구분:
- FIX 루프 = review verdict FAIL → 코드 / 설계 변경
- Spec amendment = review verdict 무관 → spec doc (Story file / Change Plan / ADR) 변경

#### 6.11.2 Output

`[<KEY>] Spec amendment — <reason>` PR (1+ Story file edit, doc-only):

- Story file §1-§7 / §11 / §13 amendment 시 PR title prefix `[<KEY>] Spec amendment`
- amendment 동반 의무:
  - Story file frontmatter `status:` field 유지 (현재 phase 변경 없음 — amendment 는 phase progression 아님)
  - Story file §10 FIX Ledger row 추가 = N/A (FIX 가 아니므로)
  - Story file §12 Sonnet Decision Log row 추가 (substantive choice 발생 시)
  - PR labels = `audit:spec-amendment` + `phase:<현재 phase>` (CFP-86 label registry 확장 candidate)

#### 6.11.3 Limit

per Story max **2 spec amendment PR**. 3+ amendment 발생 시 = 설계 결함 신호 → 설계 lane 재실행 trigger (§6.5 decision table 의 "설계 원인 판정" 적용).

#### 6.11.4 Audit trail

- Story file §11 = amendment PR list (link + reason summary)
- EPIC-RESULTS-<EPIC_KEY>.md §6 Codex review aggregate = amendment 발생 row 명시 (PR # + reason)

#### 6.11.5 mctrader 사례 (CFP-87 source)

| Story | Amendment PR | Reason | Trigger |
|---|---|---|---|
| MCT-50 / MCT-51 | mctrader-hub#72 | Codex push-back 6건 (Signal handler ownership / RunStatus minimal v1 / HTTP edge case / "11 tables" 재정의 / MarketDataFreshnessEvent deferred / ClosedBarEvent.source_hash) | Phase 3 implementation 중 Codex review |

#### 6.11.6 §6.11 ↔ §6.8 (원인 판정 decision table) cross-ref

§6.11 spec amendment 가 결과적으로 spec drift 가 코드 / 설계 사이 발생 시 → §6.8 decision table 의 "설계 원인 판정" 적용 → 설계 lane 재실행. 즉 spec amendment → FIX 루프 conversion path 존재.

---

## 7. 세션 재개(resume) 복원 절차

> **절차 본문 (§7.1 활성 Story 조회 / §7.2 Story file 섹션 판독 / §7.3 phase label ↔ 재진입 에이전트 매핑 / §7.5 사용자 통보 / §7.6 fallback) = `codeforge:session-recovery` skill 로 이전** (CFP-2198 / ADR-120 §결정 1 cold×guide). resume 진입 시 해당 skill 호출. 아래 §7.4 는 gate — 본문 잔류 (ADR-120 §결정 3, skill 이전 금지).

### 7.4 FIX 카운터 복원 (세션 개시/압축 재개 시 의무)

세션 개시 시점 또는 컨텍스트 압축 후 재개 시 Orchestrator는 **반드시** 아래를 수행:

1. 활성 Story file `Read(docs/stories/<KEY>.md)` 호출
2. §10 "FIX Ledger" 파싱 → 마지막 `RESET 구현-리뷰` 이후 행으로 각 레인 카운터 산출 (설계-리뷰 / 구현-리뷰 / 구현-테스트 / 보안-테스트 4개)
3. 파일 read 실패 시 **사용자 ESCALATE** (카운터 불명 상태 진행 금지)

GitHub 라벨 count는 감사 이력으로 보존되나 복원 source of truth 아님 (§10 기준). 이 절차 없이 ArchitectPLAgent 판정 진행 금지.

---

## 8. 토큰 예산 모니터링 + 세션 회고

### 8.1 추적 지표

- 레인별 input/output 토큰 (요구사항 / 설계 / 설계 리뷰 / 구현 / 구현 리뷰 / 구현 테스트 / 보안 테스트)
- 에이전트별 누적 토큰 (0 core in wrapper + 23 distributed across 6 lane plugins + preset/overlay-only `role: dev` 에이전트)
- FIX iteration별도 추가 토큰
- **ArchitectPLAgent + ArchitectAgent (chief author) stateless 재스폰 overhead**: PL 재스폰 당 ~5k + chief author 재스폰 당 ~10k (Story file §1-8 fetch). FIX 3회 가정 시 ~45k

### 8.2 레인별 사전 예산·중단 임계

두 지표로 추적:
- **Total**: 레인 전체 누적 (병렬·순차 합산, 에이전트별 input+output)
- **Peak concurrent**: 같은 시점에 동시 실행되는 에이전트의 현재 context 합계 — 병렬 모델에서 실제 비용 지표. v0.7.0 병렬화로 요구사항·설계 peak이 크게 증가

| 경로 | Total 사전 예산 | Total 중단 임계 | Peak concurrent (동시 컨텍스트 합) | 비고 |
|------|-----------------|-----------------|------------------------------------|------|
| 요구사항 | 80k | 150k | ~60k (Domain ∥ Analyst ∥ Researcher, 각 ~20k 풀 컨텍스트) | v0.6 순차 대비 total +30k / peak 3× |
| 설계 | 280k | 400k | ~175k (Mapper ∥ Refactor ∥ ArchitectAnalyst ∥ SecurityArchitect ∥ InfraOperationalArchitect ∥ TestContractArchitect ∥ DataArchitect ∥ ModuleArchitect ∥ APIContractArchitect, 각 ~20-25k) + ArchitectAgent (chief author) 10k + ArchitectPLAgent 5k | CFP-1086 / ADR-042 Amd 8 + CFP-1126 / ADR-042 Amd 10 — 6 permanent + 3 sub-tuple = 9 SubAgent parallel spawn (AggregateArch deprecated, ModuleArch 통합). ModuleArch CONDITIONAL applicability false 시 8 SubAgent = total +25k / peak +20k 감소 |
| 설계 리뷰 | 50k | 120k | ~40k (Claude ∥ Codex) | 기존 유지 |
| 구현 | 200k | 400k | roster size × ~20k + QADev 20k | 기존 유지 (`role: dev` 병렬 수에 비례) |
| 구현 리뷰 | 60k | 150k | ~40k (Claude ∥ Codex) | 기존 유지 |
| 구현 테스트 | 0k (CI native) | — | Orchestrator inline `gh pr checks` | ADR-048 CI gate — 토큰 비용 없음 |
| 보안 테스트 | 60k | 150k | ~40k (Claude ∥ Codex 보안 focus) | 기존 유지 (1차 layer는 GitHub native, 토큰 비용 없음) |
| Clarification 재스폰 (per instance) | 10-20k 추가 | — | 단일 에이전트 재실행 | 2회 한도 (§4.4.2 PL재량 layer). clarification 강제 fan-out = §4.4.1 (6+조건부 PMO, 정량 envelope = ADR-077 §결정 4 표 cross-ref). per-instance 정량 = [empirical-source: TBD] (Story-3 §8.3 Perf Baseline carry) |
| FIX 루프 (per iteration) | 50k + ArchitectPLAgent 재스폰 5k + chief author 재스폰 10k | 150k | FIX 트리거 레인 동일 | 기존 유지 |

**Peak 고려 이유**: 병렬 스폰은 순차보다 wall-clock 단축하나 **동시 활성 context 총량** 증가 → session memory pressure. Peak이 임계 접근 시 순차 fallback 또는 에이전트 범위 축소 검토.

**중단 임계 초과 시**: 진행 중단 → §2.3 형식으로 "토큰 한계 도달, 계속 진행 결정" 에스컬레이션.

### 8.3 세션 회고 보고 (완료 시 필수)

#### 에이전트별 작업 요약 (23 distributed agent across 6 lane plugins + 스폰된 preset/overlay-only role:dev, 미참여 "-")

| Agent | 수행 내용 |
|-------|-----------|
| Orchestrator | |
| PMOAgent | |
| RequirementsPLAgent | |
| DomainAgent | |
| *(DocsAgent — 부재, CFP-40)* | — |
| ResearcherAgent | |
| RequirementsAnalystAgent | |
| ArchitectPLAgent | |
| ArchitectAgent | (chief author) |
| CodebaseMapperAgent | |
| RefactorAgent | |
| SecurityArchitectAgent | |
| TestContractArchitectAgent | |
| ModuleArchitectAgent | (aggregate-level 포함 — 구 AggregateArch + DataMigrationArch §11 RDB OLTP 통합) |
| DesignReviewPLAgent | |
| DeveloperPLAgent | |
| DeveloperAgent | |
| DataEngineerAgent | |
| InfraEngineerAgent | |
| <추가 role:dev 에이전트들> | |
| QADeveloperAgent | |
| CodeReviewPLAgent | |
| SecurityTestPLAgent | (lanes.security_ai: true 시만) |
| ClaudeReviewAgent | (3 lane 합산) |
| CodexReviewAgent | (3 lane 합산) |

#### 토큰 사용량 (전체 스폰된 에이전트, 0 허용)

| Agent | Input Tokens | Output Tokens | 합계 |
|-------|-------------|---------------|------|
| Orchestrator | | | |
| ... (20개 전체) | | | |
| **합계** | | | |

Orchestrator 자체 토큰 = 세션 전체 - 20 서브에이전트 합계.

### 8.4 성능 베이스라인 정책 (Issue #306 / NF-T5)

구현 테스트 레인의 성능 측정에 사용하는 **baseline 측정·비교·회귀 판정** 정책 SSOT.

**정책 요약**:
- **최초 실행 값 = baseline**: Story 의 첫 성능 테스트 실행 결과를 baseline 으로 기록 (`.claude-work/progress/<KEY>.md` 의 `perf_baseline` 필드 또는 Story file §9.3 성능 섹션).
- **+20% 초과 = P2 회귀**: 이후 실행에서 mean latency / throughput 등 주요 지표가 baseline 대비 **+20% 이상 악화** 시 → TestAgent 가 P2 회귀 finding 으로 보고.
- **판정 기준 단일화**: `mean` 지표 기준 (p50/p95 는 보조 정보). Change Plan §8.3 에 지표 명시된 경우 해당 지표를 우선 사용.
- **re-baseline 조건**: 설계 의도적 변경 (Change Plan §3 갱신 동반 PR merge 후) 이 성능 특성을 변경한 경우에만 Orchestrator 가 re-baseline 승인 (FIX 루프 §6.5 "성능 test FAIL" decision table 과 연동).

| 시나리오 | 판정 | 대응 |
|---|---|---|
| 최초 실행 | — | baseline 기록 (P2 판정 없음) |
| 재실행 mean ≤ baseline × 1.20 | PASS | — |
| 재실행 mean > baseline × 1.20 | P2 회귀 | TestAgent 가 finding 포함 verdict 반환 → FIX 루프 진입 |
| 설계 변경 동반 재실행 | re-baseline | Orchestrator 승인 후 baseline 갱신, 직전 값 archive |

**TestAgent 적용**: 구현 테스트 레인 성능 subset (R9) 의 종료 조건과 통합. `baseline 비교 임계 mean:10%` (§3.2 TestAgent 행) 는 **본 §8.4 정책으로 대체 — +20% 기준이 공식 SSOT**. §3.2 TestAgent 행의 `mean:10%` 는 참조 편의를 위한 구 수치로, 신규 Story 부터 본 §8.4 적용.

---

## 9. 트러블슈팅 플레이북

> **§9.1-§9.5 (에이전트 스폰 실패 / GitHub MCP 연결 장애 / Codex CLI·플러그인 미설치 / Story file stale / CodebaseMapper stale) = `codeforge:session-recovery` skill 로 이전** (CFP-2198 / ADR-120 §결정 1 cold×guide). 장애 발생 시 해당 skill 호출. 아래 §9.6-§9.7.1 은 gate (PR keyword 정책 + phase×gate label 매핑) — 본문 잔류 (ADR-120 §결정 3).

### 9.6 Phase 1 / Phase 2 PR 모델 트러블슈팅

#### PR description `Closes/Fixes/Resolves` keyword 정책 (CFP-292 / Issue #299)

- **Phase 1 PR MUST NOT** use `Closes #NNN`, `Fixes #NNN`, `Resolves #NNN` in PR description.  
  GitHub 이 PR merge 시 이 keyword 를 자동 감지하여 Issue 를 close 하므로, Phase 2 merge 전에 Story Issue 가 premature close 됨.
- Phase 1 PR 에서는 `Related: #NNN` 사용.
- **Phase 2 PR** 에서만 `Closes #NNN` 사용 (정상 auto-close 트리거).
- `story-init.yml` 이 자동 open 하는 Phase 1 PR 에는 `Related:` keyword 를 사용하도록 workflow 를 유지해야 함.

#### Cross-PR conflict resolution (CFP-292 / Issue #299)

동일 Story 의 복수 PR (Phase 1 + follow-up spec amendment 등) 이 merge 순서 충돌 또는 git conflict 발생 시:

1. **base PR (가장 먼저 merge 할 PR) 을 먼저 merge** (Phase 1 PR → spec amendment 순서 유지).
2. 충돌 PR 의 브랜치에서 `git rebase origin/main` 으로 merged base 위로 rebase.
3. Conflict 해소 후 force-push → PR CI 재통과 → merge.
4. `git merge` 방향 역전 금지 (base 브랜치에 feature 브랜치를 merge 하는 방향 유지).

| 증상 | 원인 | 대응 |
|------|------|------|
| Phase 1 PR mergeable 아님 (label OK인데 Action fail) | `phase-gate-mergeable.yml` Action이 status check fail | Action 로그 확인. `gate:design-review-pass` 라벨 누락 검증 |
| Phase 2 PR open 안 되는 상태 | Phase 1 PR이 main에 merge 안 됨 | Phase 1 PR review 완료 + merge 후 Phase 2 PR open |
| §1 변경 PR이 reject됨 | `story-section-1-immutable.yml` Action이 §1 line range 변경 감지 | 정당한 정정 필요 시 architect team에 bypass approval 요청 |
| Sub-issue가 자동 생성 안 됨 | `subissue-from-impl-manifest.yml` Action 미실행 또는 §8.5 매핑표 형식 오류 | Action 로그 + §8.5 markdown table 형식 검증 |
| Phase 1 PR merge 후 Story Issue 가 자동 close 됨 | Phase 1 PR description 에 `Closes/Fixes/Resolves` 사용 | `Related: #NNN` 으로 수정 후 PR reopen — 본 §9.6 keyword 정책 참조 |
| 복수 PR 간 git conflict | 동일 Story 내 Phase 1 + follow-up 병렬 open | base PR 먼저 merge → 충돌 PR rebase on main → conflict 해소 |

### 9.7 phase-gate-mergeable label mapping (CFP-479)

`templates/github-workflows/phase-gate-mergeable.yml` Action 이 PR mergeable status 를 판정할 때 적용하는 정식 phase × gate 매핑 표. **workflow yml line 195-208 의 inline comment 가 1차 SSOT** — 본 단락은 narrative drift 방지를 위한 doc 미러 (CFP-455 retro action_item #5 origin).

| Phase label (PR 부착) | Required gate label | 근거 (CFP) | 비고 |
|---|---|---|---|
| `phase:설계` | `gate:design-review-pass` | CFP-113 | Phase 1 PR — design lane 진행 중 |
| `phase:설계-리뷰` | `gate:design-review-pass` | CFP-113 | Phase 1 PR — DesignReviewPL verdict 부착 후 |
| `phase:구현` | **`gate:design-review-pass`** | CFP-342 | Phase 2 PR — code-review-pass 아님 (intuitive naming 어긋남) |
| `phase:구현-리뷰` | **`gate:design-review-pass`** | CFP-342 | Phase 2 PR — code-review-pass 아님 (동일) |
| `phase:구현-테스트` | (gate 무) | CFP-317 / ADR-048 | CI gate inline polling, gate label 미부착 |
| `phase:보안-테스트` | `gate:security-test-pass` | (consumer `lanes.security_ai: true` opt-in 시에만) | (Epic 묶음 종료 직전) — 배포 lane prerequisite (CFP-1059 후) |
| **`phase:배포`** (신설 — CFP-1059) | **`gate:deploy-pass`** | CFP-1059 / ADR-087 | Epic 묶음 완료 후 DeployPLAgent spawn 진행 중 (Phase 1 declarative) |
| **`phase:배포-리뷰`** (신설 — CFP-1059) | **`gate:deploy-review-pass`** | CFP-1059 / ADR-088 | terminal gate — production smoke / 성능 비교 / cutover 사후 검증 PASS 후 Epic close (Phase 1 declarative) |
| (Story binding 부재 / 그 외) | `gate:design-review-pass` (legacy heuristic) | workflow line 207 | No Story binding fallback |

**핵심 anomaly (CFP-342 fix)**:

- `phase:구현` / `phase:구현-리뷰` 에서 **`gate:design-review-pass`** 요구 — 직관적으로 기대되는 `gate:code-review-pass` 아님 (CFP-342 verbatim: "Phase 2 PR 도 gate:design-review-pass 요구 — gate:code-review-pass 가 아닌").
- 이유: codeforge 는 별도 `gate:code-review-pass` label 미도입. 구현 리뷰 PASS = phase progression only (gate label 무부착). 설계 리뷰 gate label 가 Phase 1 → Phase 2 전 구간 단일 mergeable 게이트 역할 수행.

**Orchestrator 가 라벨 결정 시 참조 path**:

1. Story file frontmatter `phase:` field (cross-repo binding, workflow line 75-92 fetch) — 1차 SSOT
2. PR label `phase:*` (Story binding 부재 시 PR labels fallback, workflow line 122-134)
3. 본 표 매핑에 따라 required gate label 결정 (workflow line 195-208)
4. `gate:live-entry-pass` = Live touching Story 의 보안-테스트 phase 에 추가 요구 (ADR-030, workflow line 262-281)

**Cross-ref 동기화 의무**: 본 표는 3 doc 동시 갱신 의무 — `docs/orchestrator-playbook.md` (정식 SSOT) · `CLAUDE.md` "Branch protection" 단락 (link only) · `docs/consumer-guide.md` §2e Branch protection (consumer mirror). 향후 phase / gate label taxonomy 변경 시 workflow yml line 195-208 + 본 표 + 3 doc 동시 갱신.

**CFP-1302 추가 (phase-gate-auto-cleanup.yml + multi-gate explicit shape)**: phase 전환 시 prior gate label 자동 cleanup 은 신규 workflow `templates/github-workflows/phase-gate-auto-cleanup.yml` (CFP-1302 / CFP-604 retro F6 Wave 2) 가 담당 (SRP 분리, `phase-gate-mergeable.yml` 와 concurrency.group namespace 분리). multi-gate `required` shape = `{phase, gates: string[]}` array (semantic 변경 0, syntactic 강화 — `every()` AND invariant + B-1 empty-array fail-loud guard). `liveEntryOk` 별도 변수 보존 (ADR-030 conditional gate semantics — `required.gates[]` unconditional array semantics 와 axis disjoint, CFP-1302 D-1 결정).

#### 9.7.1 Phase label transition timing (CFP-1577 / CFP-1539+CFP-1540 batch retro §4.1 #1)

§9.7 표 = **static label × gate snapshot mapping** (PR open 시점 mergeable 판정 기준). 본 §9.7.1 표 = **dynamic transition timing forcing function** — Orchestrator 가 *언제 어떤* phase label add/remove + gate label attach 의무인지 codify. axis disjoint (snapshot 판정 ↔ transition timing). CFP-1539+CFP-1540 batch merge incident (premature `phase:완료` attach → workflow ACTION_REQUIRED → manual recovery) 가 forcing function source.

| Phase (target) | Add label | Remove label | Add gate | Timing signal (event) | Source |
|---|---|---|---|---|---|
| `phase:대기` | `phase:대기` | — | — | Issue Forms submission 직후 `story-init.yml` Action 자동 부착 | story-init.yml (mechanical) |
| `phase:요구사항` | `phase:요구사항` | `phase:대기` | — | RequirementsPLAgent spawn 직전 (Orchestrator lane entry trigger) | Orchestrator |
| `phase:설계` | `phase:설계` | `phase:요구사항` | — | RequirementsPL verdict PASS + ArchitectPLAgent spawn 직전 | Orchestrator |
| `phase:설계-리뷰` | `phase:설계-리뷰` | `phase:설계` | — (verdict 후 부착) | ArchitectAgent verdict 후 DesignReviewPLAgent spawn 직전 | Orchestrator |
| `phase:구현` | `phase:구현` | `phase:설계-리뷰` | `gate:design-review-pass` (DesignReview PASS 시점 부착) | DesignReviewPL verdict PASS 직후 + DeveloperPLAgent spawn 직전 | Orchestrator (gate label = codeforge-review self-write) |
| `phase:구현-리뷰` | `phase:구현-리뷰` | `phase:구현` | (`gate:design-review-pass` retain — 별도 code-review gate 미도입) | DeveloperPL ready + CodeReviewPLAgent spawn 직전 | Orchestrator |
| `phase:구현-테스트` | `phase:구현-테스트` | `phase:구현-리뷰` | — (gate 무 — CI gate inline polling) | CodeReview PASS + CI gate `gh pr checks --watch` polling 진입 직전 | Orchestrator |
| `phase:보안-테스트` (opt-in) | `phase:보안-테스트` | `phase:구현-테스트` | `gate:security-test-pass` | 통합테스트 PASS + SecurityTestPLAgent spawn 직전 (consumer `lanes.security_ai: true` 시에만) | Orchestrator |
| `phase:배포` (CFP-1059) | `phase:배포` | `phase:보안-테스트` (또는 `phase:구현-테스트` if security 미활성) | `gate:deploy-pass` | Epic 묶음 완료 후 DeployPLAgent spawn 직전 (Phase 1 declarative) | Orchestrator |
| `phase:배포-리뷰` (CFP-1059) | `phase:배포-리뷰` | `phase:배포` | `gate:deploy-review-pass` | DeployPL PASS + DeployReviewPLAgent spawn 직전 (Phase 1 declarative) | Orchestrator |
| **`phase:완료`** | `phase:완료` | `phase:구현-리뷰` (또는 `phase:배포-리뷰` if deploy lane 활성) | **precondition AND**: `gate:design-review-pass` (또는 활성 lane 의 terminal gate) + `gate:retro-complete` (label-registry-v2 line 558, ADR-045) | **Phase 2 PR merge 후 + retro write 완료 후** (PMOAgent `gate:retro-complete` 부착 확인 후) | Orchestrator (phase 전환) + PMOAgent (`gate:retro-complete` self-write) |

**핵심 invariant (CFP-1577 — `phase:완료` premature attach 차단)**:

- `phase:완료` 부착은 **2 gate AND** 의무: (a) Phase 2 PR merge 후 활성 lane 의 terminal gate label (`gate:design-review-pass` default, deploy lane 활성 시 `gate:deploy-review-pass`) (b) `gate:retro-complete` (PMOAgent self-write 후). 양 gate 부재 시 `phase-gate-mergeable.yml` ACTION_REQUIRED 발생 (workflow line 391-404 default fallback path = `phaseOk = (phaseLabel === required.phase)` mismatch).
- `phase:완료` attach precondition 위반 = `phase:구현-리뷰` (또는 적용 가능한 직전 phase) + 해당 gate 재부착으로 정정 후 PASS (CFP-1539+CFP-1540 batch incident resolution pattern).
- `gate:retro-complete` 부재 시 `retro-mandatory.yml` (ADR-045) 가 Story Issue close 차단 (auto-reopen) — `phase:완료` attach 와 함께 retro write 완료 확인 의무.

**Cross-ref (transition timing 의무)**:

- `codeforge:story-epic-flow-preflight` skill = lane entry preflight 3-check (phase 라벨 정합 / docs file 선행 섹션 / 외부 의존성). 본 §9.7.1 = preflight 의 *phase label 정합* 항목 source SSOT (skill body 1-row cross-ref append per CFP-1577 AC-3).
- ADR-026 Amendment 4 (CFP-795) = `phase-gate-mergeable.yml` post-merge fix exemption (axis disjoint — workflow logic expansion vs. 본 §9.7.1 = Orchestrator timing codification layer).
- workflow yml `phase-gate-mergeable.yml` 본문 변경 0건 (CFP-1577 Out of scope §3) — 본 §9.7.1 = documentation layer only.

---

## 10. Hotfix 경로 (운영 장애 대응)

정상 7-레인 full flow 는 Story 1건당 반나절~수일 소요. 운영 장애로 즉시 대응 필요한 경우 **Minimal Path** (`severity:bug`, ≤30 lines) 또는 **Medium Path** (`severity:critical`, multi-file) 중 하나 선택. 어느 경로든 **사후 감사 (next working session 자동 수행) 의무**.

상세 = [`docs/hotfix-playbook.md`](hotfix-playbook.md) (CFP-93, P2-9 follow-up — cognitive overhead reduction 목적으로 별도 분리). mctrader debut audit (Issue #181 P2-9) 까지 사용 사례 0 — 본 경로는 첫 운영 장애 발생 시 활성화.

---

## 11. Cross-agent write coordination

ζ arc decomposition (CFP-31~CFP-40) 후 wrapper repo 에는 agent 0개. write 책임은 6 lane plugin 으로 분산 (§5.1 표 참조). 결과적으로 wrapper-side `.claude-work/doc-queue/**` 기반 write queue 는 **사용 안 함**. 대신:

- **각 lane plugin 자기 owner section 직접 write** — `Edit` 또는 GitHub MCP 도구 호출 직접 수행
- **Multi-writer 영역의 자연 직렬화** — `docs/stories/<KEY>.md` 의 §1 → §2-§6 → §7 → §8 → §9 → §11 등 phase 진행 순서가 자연 직렬화 보장. concurrent write 충돌은 phase-label-invariant.yml + branch protection 으로 차단
- **§10 FIX Ledger 예외** — Orchestrator 단독 write (CFP-32 monopoly). lane plugin 은 verdict.status=FIX 만 반환 — §10 직접 write 안 함 (`fix-event-v1` contract)

Pre-CFP-32 의 deprecated write queue type (`adr-draft`, `change-plan`, `domain-knowledge`, `ledger-append`) 가 코드에 잔존하면 silent skip — 사용 안 함.

---

## 12. Orchestrator 컨텍스트 패킷 (Story file 섹션 캐시)

에이전트 스폰마다 `Read(docs/stories/<KEY>.md)` 반복 호출은 토큰 낭비. Orchestrator가 세션 메모리에 섹션 캐시를 유지해 **context packet** 형태로 에이전트 프롬프트에 주입.

### 12.1 캐시 구조 (Orchestrator 세션 메모리)

```
story_cache[<story-key>] = {
  "file_path": "docs/stories/<KEY>.md",
  "mtime": <unix timestamp>,
  "fetched_at": <ISO 8601>,             # KST `+09:00` zoned (display layer — ADR-079 §결정 2)
  "sections": {
    "§1": {body, updated_at},
    "§2": {body, updated_at},
    ...
  }
}
```

### 12.2 캐시 갱신 규칙

- **무효화 트리거**: lane plugin 이 Story file update 완료를 보고하면 해당 섹션 캐시 invalidate (또는 file mtime 변경 감지 시 자동 invalidate)
- **fetch 규칙**: 에이전트 스폰 직전 Orchestrator가 필요 섹션이 캐시에 없거나 invalidated 상태면 fetch
- **섹션 단위 fetch**: `Read(docs/stories/<KEY>.md)` 결과에서 필요 섹션만 파싱 저장 — 전체 file body 메모리에 유지하지 않음

### 12.3 Context Packet 주입 형식

에이전트 프롬프트 `[컨텍스트]` 블록에 아래 packet 삽입:

```
[Story Context Packet — <KEY> (mtime: {ISO}, fetched {ISO})]
## §1 사용자 원문
{body}

## §3 관련 ADR
{body}

## §7 설계 서사
{body}

[End Packet]
```

에이전트는 prompt 내 packet을 SSOT로 사용 — 추가 `Read` 호출 생략 (packet 외 섹션 필요 시 명시 요청).

> **Worktree-membership directive (ADR-040 Amendment 6 / CFP-843)**: Context Packet 주입 시 packet 외 1줄 추가 — "All file operations MUST target `<worktree_abs_path>` (git = `git -C <abs>`, Write/Edit = absolute path, forward-slash 정규형)". harness cwd reset gap 차단 — §3.5 sub-agent spawn 표준 SSOT 정합.

### 12.4 Packet vs path-only 선택

- **Packet 주입**: 설계/구현/리뷰 레인처럼 여러 섹션 깊이 참조 필요할 때 (§1-8 범위)
- **Path만 전달**: 단발성 조회, 섹션 캐시 미정의 부분
- **설계 lane packet recipient**: ArchitectPLAgent (Phase 2에서 ArchitectAgent (chief author) + 6 permanent SubAgent (SecurityArch / InfraOperationalArch / TestContractArch / DataArch / ModuleArch (aggregate-level 포함 — 구 AggregateArch, CFP-1126 통합) / APIContractArch) + 3 sub-tuple (Mapper / Refactor / ArchitectAnalyst) 에 forward — PL이 packet 분배 책임. CFP-1086 / ADR-042 Amd 8, CFP-1126 / ADR-042 Amd 10 정합.)

### 12.5 Project Config Packet (project.yaml 슬라이스)

Story file Context Packet과 병행해 **`.claude/_overlay/project.yaml`의 objective SSOT 상수**도 sub-agent 프롬프트에 주입. GitHub 호출하는 에이전트가 매번 `Read` 호출 없이 곧바로 활용.

#### 캐시 구조

```
project_config_cache = {
  "loaded_at": <ISO 8601>,                   # 세션 시작 시 1회 로드 — KST `+09:00` zoned (display layer — ADR-079 §결정 2)
  "raw": {
    "project": {name},
    "github": {org, repo, default_branch, pr_title_prefix_template, story_key_prefix, codeowners, discussions, milestone},
    "labels": {components},
  },
}
```

#### 로드·무효화

- **로드**: 세션 개시 시 1회 `Read(.claude/_overlay/project.yaml)` + yaml.safe_load
- **검증**: validate_config.py 통과 (SessionStart hook에서 이미 검증됨 — Orchestrator는 신뢰하고 read만)
- **무효화**: consumer가 세션 중 project.yaml 편집하면 next agent spawn 직전 재로드 (파일 mtime 비교)
- **Missing file 처리**: validator가 WARN만 했으므로 Orchestrator는 packet 주입 생략 + 에이전트에 "project.yaml 없음 — GitHub 호출 전 사용자 확인" 지시

#### Packet 주입 형식

GitHub 상수가 필요한 에이전트 프롬프트에 삽입:

```
[Project Config Packet — loaded at {ISO}]
project.name: <name>
github.org: <org>
github.repo: <repo>
github.default_branch: <main>
github.pr_title_prefix_template: <template>
github.story_key_prefix: <prefix>
github.codeowners.architect_team: <@org/team>
github.codeowners.domain_expert_team: <@org/team>
github.discussions.domain_kb_category: <category>
github.milestone.epic_naming_pattern: <pattern>
labels.components: [...]
[End Project Config Packet]
```

에이전트는 위 값을 그대로 GitHub 호출 인자에 사용. project.yaml `Read` 생략 가능 (packet SSOT).

#### Packet 주입 대상 에이전트

| 에이전트 | 사용하는 slice |
|----------|----------------|
| **RequirementsPLAgent** | `github.story_key_prefix` (Story KEY 결정), `github.org`, `github.repo` (search·list_issues 호출) |
| **각 lane plugin** | 자기 phase prefix GitHub 호출에 필요한 org/repo/story_key_prefix slice |
| **DomainAgent** | `github.discussions.domain_kb_category` (Discussions Q&A) + `Glob(docs/domain-knowledge/**)` |
| **PMOAgent** | `github` 전체 (회고·패턴 search 호출) |
| **ArchitectPLAgent** | `github.codeowners.architect_team` (Phase 1 PR architect review 매핑 확인), `github.org`, `github.repo` (Issue/PR cross-reference). 설계 lane 전체에 packet forward 책임 |

기타 에이전트 (설계·구현·리뷰·테스트 레인 대부분)는 GitHub 호출 없음 → packet 주입 불필요.

#### Fallback: Read로 직접 접근

Packet 주입은 Orchestrator의 토큰 최적화 수단이지 필수 규약 아님. Packet 누락 또는 일부 필드만 필요할 때 에이전트는 여전히 `Read(.claude/_overlay/project.yaml)`로 직접 접근 가능 (agent md `Read` 권한 보장).

### 12.6 Warm cache (R6, [CFP-19 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

매 spawn마다 `Read(docs/stories/<KEY>.md)` → 섹션 추출 → packet 재구성 비용을 cache로 amortize.

**Cache 위치**: `.claude-work/cache/<KEY>-sections.json` (Story 1건당 1 파일)

**Cache 스키마**:

```json
{
  "story_key": "<KEY>",
  "story_file_commit": "<git rev-parse HEAD on docs/stories/<KEY>.md>",
  "cached_at": "<ISO 8601>",
  "sections": {
    "1": "<§1 본문 hash>",
    "3": "<§3 본문 hash>",
    "7": "<§7 본문 hash>",
    "...": "..."
  },
  "section_bodies": {
    "1": "<§1 verbatim>",
    "3": "<§3 verbatim>",
    "...": "..."
  }
}
```

**Cache 사용 절차**:
1. Orchestrator가 spawn 직전 packet 조립
2. cache 파일 존재 + `story_file_commit` 일치 확인:
   - **hit**: `section_bodies`에서 필요 섹션 reuse → 재 Read 없음
   - **miss (commit drift)**: `Read(docs/stories/<KEY>.md)` → 새 cache write
3. 1 Story 평균 6 lane × 4 spawn = 24회 spawn 중 **14-18회 cache hit 기대** (lane 경계마다 1회만 commit drift)

**Invalidation**:
- lane plugin 이 Story file edit 후 `git rev-parse HEAD:docs/stories/<KEY>.md` 변경 → 자동 cache miss
- Story 완료 시 cache 파일 cleanup (선택)

**보안**: cache 파일에 §1 사용자 원문 포함 → `.gitignore`에 `.claude-work/cache/` 추가 의무 (Group F).

---

### 12.7 Orchestrator 통신 표준 (normative — wrapper + all consumers)

**매 메시지 첫 줄 = 단계 메타 라벨 의무**:

| 상황 | 첫 줄 형식 |
|---|---|
| 레인 진행 중 | `현재 단계: <레인명> — <에이전트명> <동작>` |
| Skill 절차 진행 중 | `<Skill명> Step N/<전체> — <현재 동작>` |
| ADR / spec / 코드 블록 제시 | `다음은 [무엇] — 사용자가 [무엇] 검토` |
| 결정 선택지 제시 | `결정 대상: <무엇> — 아래 N개 선택지` |
| 약어 첫 등장 | 첫 등장 시 풀어쓰기 (예: `CFP-274 (TodoWrite 진행 시각화 Story)`) |

**Cold-start readability 의무**: 각 메시지가 대화 누적 컨텍스트 없이도 이해 가능해야 한다. 약어·코드 블록·ADR ref 가 맥락 설명 없이 갑자기 등장하는 것은 `communication_violation`.

**적용 범위**: wrapper + 모든 consumer project Orchestrator 세션.

### 12.8 Deputy 영역별 specialized flat spawn Context Packet 4종 spec (CFP-681 / W1 S2 — CFP-1026 design lane 재편)

설계 lane 에서 Orchestrator 가 4-tuple sub-tuple (CodebaseMapper / RefactorAgent / ArchitectAnalyst + ArchitectAgent chief author) 및 deputy 를 spawn 할 때 주입하는 영역별 specialized Context Packet spec. deputy mandate 매트릭스 SSOT = `skills/deputy-mandate/SKILL.md` (5 permanent + 3 CONDITIONAL — ADR-042 Amendment 7 / ADR-014 Amendment 4). 본 §12.8 은 그 매트릭스의 spawn-time 주입 mechanism.

#### (a) Orchestrator flat spawn (재귀 spawn 금지 / nested team 금지 / sub-lead 격상 0건)

- spawn 주체 = **Orchestrator** (top-level Claude 세션). 4 component (chief author + Mapper + Refactor + ArchitectAnalyst) 모두 Orchestrator 가 직접 flat spawn. ArchitectPLAgent 는 PL synthesizer 역할 (산출물 통합 검수) — sub-agent 를 재귀 spawn 하지 않는다.
- **재귀 spawn 금지** = platform inherent (Lead 와 teammate 모두 Agent tool 추가 spawn 불가, env=0 default subagent context). **nested team 금지** = team-of-teams 불가. **sub-lead 격상 0건** = 4-tuple 안 어느 component 도 다른 component 의 spawn 주체가 되지 않음.
- 근거 SSOT: 본 nested team 금지 / flat spawn 원칙은 ADR-044 (phase-scoped sequential team — 대안검토표 + 결론 단락의 nested team 금지 SSOT) + ADR-009 §결정 1 (wrapper-only decomposition) + ADR-039 (Orchestrator subagent default) 정합. CFP-676 CX-676-TP4-3 reaffirm 정합 (S1 ADR-044 reaffirm 단락 cross-ref).

#### (b) "4-tuple = 논리적 그룹핑" — 물리적 spawn 계층 아님

4-tuple 은 **어느 sub-agent 가 어느 deputy 영역 Context Packet 으로 spawn 됐는지를 표기하는 논리적 그룹핑**이다. 물리적 spawn 계층 (4-level nested) 이 아니다. 모든 component 는 동일 평면(flat)에서 Orchestrator 로부터 spawn 되며 서로의 상위/하위가 아니다. "4-tuple" 의 "4" 가 4단계 nested spawn 으로 오해되는 것을 명시적으로 차단 (CFP-681 EC-6 — Story §1 deliverable 3 verbatim).

| 4-tuple component | spawn 주체 | deputy 영역 packet | model tier |
|---|---|---|---|
| ArchitectAgent (chief author) | Orchestrator (flat) | 전 deputy + 3 sub-tuple 산출물 multi-source synthesis | Opus |
| CodebaseMapper | Orchestrator (flat) | existing codebase fact (as-is) | Sonnet |
| RefactorAgent | Orchestrator (flat) | decoupling / pattern advocacy (to-be) | Sonnet |
| ArchitectAnalyst (PriorArtAgent rename) | Orchestrator (flat) | 변경 전 기존 설계 (ADR / Change Plan / Story) 분석 단일 축 | Sonnet |

#### (c) 정적 overlay 메커니즘 vs 동적 spawn-time Context Packet — 명시적 대비

| 축 | 정적 overlay 메커니즘 | 동적 spawn-time Context Packet |
|---|---|---|
| 주입 시점 | consumer SessionStart merge hook (세션 개시 1회) | **매 spawn** (Orchestrator 가 sub-agent 프롬프트에 주입) |
| 내용 | `.claude/_overlay/project.yaml` objective SSOT 상수 + `.claude/_overlay/CLAUDE.md` narrative (도메인 해설) | Story file 섹션 캐시 (§12.1-§12.3) + deputy 영역별 specialized slice (본 §12.8) |
| 성격 | desired state (Helm-style 정적 — 프로젝트 불변 상수) | 동적 (Story·spawn 마다 달라지는 컨텍스트) |
| SSOT | §12.5 Project Config Packet (project.yaml 슬라이스) | §12.3 Context Packet 주입 형식 + 본 §12.8 deputy 영역별 specialization |

> **혼동 차단 (CFP-681 §2.5 / Researcher disambiguation)**: 정적 overlay (consumer SessionStart merge — Helm-style desired state) 와 동적 spawn-time Context Packet (매 spawn 주입) 은 별개 메커니즘이다. deputy 영역별 specialized packet 은 후자 — Story·spawn 마다 어느 deputy 영역 slice 를 주입할지 동적으로 결정. overlay 의 정적 상수 (project.yaml) 와 cross-pollinate 금지.

#### (d) ADR-039 §결정 1 cross-ref

본 §12.8 의 모든 spawn 은 [ADR-039](../archive/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) §결정 1 (codeforge 수정 작업 = Orchestrator default subagent spawn) 정합. inline 수행은 §결정 2 의 4-entry whitelist (사용자 dialog / TodoWrite scratchpad / Read-only Q&A / Status report) 외 영역 금지. 4-tuple flat spawn = ADR-039 default subagent context 의 design lane instantiation (env=0 = one-shot Agent tool spawn, env=1 = phase-scoped sequential team — ADR-044, 단 nested team 금지 동일).

---

## 13. PMOAgent 프로젝트 관리 (Cross-cutting)

PMOAgent는 단일 Story 레인 게이트 밖에서 cross-cutting 감사·회고·패턴 분석을 전담. 요구사항 해석은 RequirementsPLAgent 영역으로 분리됨.

### 13.1 스폰 타이밍 4종 (CFP-316 / ADR-047 — Version Delta Review 추가)

| 트리거 | 시점 | 입력 | 산출물 |
|--------|------|------|--------|
| **Epic 창설** | Orchestrator가 Epic 생성 직후, Story 분해 직전 | 사용자 원문·관련 ADR·기존 Epic 이력·코드 구조 | Story 분해 자문 (의존성·우선순위·**병렬/순차 판정**) — 상세 규칙 [PMOAgent.md §1](../plugins/codeforge-pmo/agents/PMOAgent.md) |
| **Story 완료** | CI gate PASS → (lanes.security_ai: true 시 보안 테스트 PASS →) Phase 2 PR merge 직후 | 해당 Story file §1-11 + FIX Ledger + GitHub Issue 코멘트 이력 + 토큰 사용량 | 회고 감사 보고 (Preflight 누락·§8/§8.5 매핑·FIX evidence 완성도·예산) |
| **사용자 요청** | `/pmo-audit` 혹은 명시 요청 | 최근 N Story (기본 5) file·Ledger·ADR 변경 이력 | Cross-Story 패턴 보고 + ADR 후보 발의 |
| **Version Delta Review** | Framework Delta Event 발생 후 5분 이내 (또는 사용자 수동 trigger `/pmo version-delta-review`) | Framework Delta Event 종류 + 진행 중 Story 목록 + 관련 ADR + consumer overlay 상태 | Migration Epic Issue (material drift 시) 또는 "no action" 보고서 → Story §11 기록 |

### 13.1a Version Delta Review 프로세스 (CFP-316 / ADR-047)

PMOAgent의 4번째 trigger — codeforge framework 진화(신규 SubAgent 추가, §section 변경, ADR 변경 등) 시 기존 진행 중 Stories/Change Plans의 구조 재편 필요 여부를 자동 평가한다.

**Framework Delta Event 4-Type 정의**:

| Type | 설명 | PMOAgent 반응 |
|------|------|---------------|
| **Type A — Version bump** | consumer 프로젝트의 codeforge version bump | patch: advisory review 보고서 / minor·major: Migration Epic 후보 평가 |
| **Type B — ADR 변경** | Story 구조/lane 동작에 영향을 주는 신규·실질적 ADR 변경 (inter-plugin contract schema MAJOR bump, GitHub workflow fixture 변경 등) | 영향 범위 평가 후 Migration Epic 여부 결정 |
| **Type C — Deputy 변경** | 신규 SubAgent 추가 또는 SubAgent mandate 변경 (새 필수 §section 발생) | 진행 중 Story에 새 §section 추가 Migration Story 생성 |
| **Type D — Bootstrap 변경** | ADR-027/ADR-032 enforcement 변경 | consumer-guide 업데이트 + bootstrap 재검증 Migration Story |

**Version Delta Review 프로세스 (4단계)**:

1. Framework Delta Event 종류 판별 (Type A/B/C/D)
2. 진행 중인 Stories/Change Plans의 §section 구조 점검 (영향 범위 평가)
3. Material drift 판별:
   - patch bump / advisory-only ADR: "no migration needed" 보고서 → Story §11 기록
   - minor/major bump 또는 신규 SubAgent 또는 §section 신설: Migration Epic 후보 평가
4. Migration Epic 생성 또는 "no action" 결정

**2차 detection / fallback** (누락 방지):
- (2차) PMOAgent Story 완료 회고 trigger 시 직전 5분 grace 내 Delta Event 미처리 자동 점검
- (3차 fallback) 사용자 수동 trigger `/pmo version-delta-review` skill 호출
- (장기) SessionStart hook 에 version bump 감지 추가 — 별도 CFP 후속

상세 Migration Epic Pattern 및 tiered template → [consumer-guide.md §5.2](consumer-guide.md#52-framework-migration-epic-pattern-cfp-316--adr-047).

### 13.2 감사 체크리스트 (Story 완료 회고 기본 세트)

1. **Preflight 실행 근거**: 각 레인 진입 시 Issue 코멘트에 `[<phase>] <AgentName>: Preflight PASS` 또는 failure 보고가 존재하는가
2. **§8 Test Contract ↔ tests/** 매핑**: QADev 매핑표의 모든 항목이 실제 tests/ 파일로 구현됐는가
3. **§8.5 Impl Manifest ↔ git diff**: 기록된 파일 목록이 PR의 실제 변경 파일과 일치하는가 (누락·추가 없이). subissue Action이 자동 생성한 sub-issue 목록과 대조
4. **FIX Ledger evidence pack**: 각 FIX iteration 행에 ArchitectPLAgent 판정 근거(Change Plan 버전 + 리뷰 findings + 테스트 로그)가 코멘트로 기록됐는가
5. **토큰 예산 준수**: 레인별 사전 예산(§8.2) 대비 실제 사용량, 중단 임계 접근 여부
6. **RESET 마커 타당성**: 테스트 FAIL 후 구현 리뷰 RESET이 올바른 조건에서 기록됐는가
7. **Phase/Gate 라벨 invariant**: phase-label-invariant·phase-gate-mergeable·story-section-1-immutable Action 모두 PASS 했는가

### 13.3 Cross-Story 패턴 검출 알고리즘 (사용자 요청 시)

```
inputs:
  - 최근 N Story (기본 5, 사용자 지정 가능)
  - 각 Story의 §10 FIX Ledger + ADR 변경 이력

outputs:
  - 반복 FIX 원인 분포 (설계 vs 구현, 레인별)
  - ESCALATE 발생 단계 히트맵
  - 성능 게이트 실패 트렌드 (baseline 갱신 Story vs 성능 회귀 Story)
  - 파일 핫스팟 (3+ Story에 걸쳐 수정된 파일)
  - ADR 후보 (패턴이 "설계 지침 부재"로 해석될 때)
```

### 13.4 ADR 후보 발의 절차

PMOAgent가 반복 패턴을 식별해 ADR draft 제안 (`pmo_output v1.adr_proposal` inline content) 을 Orchestrator에 전달하면, Orchestrator가 codeforge-design 의 ArchitectAgent를 스폰해 `status=Proposed` ADR 파일(`docs/adr/ADR-NNN-<slug>.md`)을 직접 write (CFP-26 Phase 0a). 다음 Story 설계 진입 시 ArchitectAgent (chief author)가 검토해 `status=Accepted` 전이 또는 기각.

```
# 경로:
# PMOAgent → (Orchestrator 경유) → ArchitectAgent (codeforge-design) → docs/adr/ADR-NNN-<slug>.md 직접 write
# ※ pre-CFP-32 write queue adr-draft type 은 사용 안 함 — Orchestrator가 ArchitectAgent 직접 스폰
```

ArchitectAgent가 write하는 ADR 파일 본문 구조는 PMOAgent.md의 "ADR 후보 발의" 템플릿을 따른다 (status=Proposed로 신설).

### 13.5 PMOAgent 보고 기록

모든 PMOAgent 산출물은 `[PMO]` phase prefix로 GitHub Issue 코멘트 직접 기록. Story 회고는 Story file §11 직접 self-write (codeforge-pmo), Cross-Story 감사는 **별도 Issue** (label: `type:audit`, 제목: `PMO Audit / <YYYY-MM-DD>`) PMOAgent 가 직접 생성.

### 13.6 범위 외

PMOAgent가 **하지 않는** 것:
- 단일 Story 요구사항 해석 (RequirementsPLAgent)
- Change Plan 작성·검토 (ArchitectPLAgent / ArchitectAgent / DesignReviewPL)
- 코드 수정 (Dev)
- 테스트 실행 (CI gate — Orchestrator inline)
- 사용자 직접 상호작용 (Orchestrator 경유 보고만)

---

## 14. §0 Live Progress (CFP-20)

`.claude-work/progress/<KEY>.md` 파일에 Orchestrator가 7-lane × phase 진행 상황을 M3 hierarchical + S3 completion snippet 형식으로 기록한다. PR diff에 노출 X (gitignored), GitHub Issue body 미러링 X (lane plugin self-write 영역과 분리). 사용자 원문 "todolist 처럼 매 진행 때마다 수시로 보여" 의도 충족.

### 14.1 권한·소유

| 컴포넌트 | Writer | Reader |
|---|---|---|
| `.claude-work/progress/<KEY>.md` | **Orchestrator 단독** | Orchestrator (resume), PMOAgent (회고), 사용자 (수동) |
| `.claude-work/progress/index.md` | Orchestrator 단독 | Orchestrator (multi-Story 분기) |
| `.claude-work/progress/_archive/<KEY>.md` | Orchestrator (Story 완료 시 mv) | PMOAgent (Cross-Story 패턴) |

doc-queue (사용 안 함 — ζ arc 완료) / docs/stories/<KEY>.md 직접 write (lane plugin self-write) / GitHub Issue body: **progress file 과 무관**.

### 14.2 State source vs Derivative cache (핵심 invariant)

```
State source (committed, durable):
  - docs/stories/<KEY>.md §10 FIX Ledger    → FIX 카운터 + RESET 마커
  - docs/stories/<KEY>.md §-fill state      → 완료 lane 추론
  - GitHub Issue phase label                → 현재 lane

Derivative cache (ephemeral, gitignored):
  - .claude-work/progress/<KEY>.md          → rendered §0
```

- 정상 흐름: 매 이벤트마다 cache 직접 patch (read-patch-write, 저비용)
- 세션 재개 / 손상 / 모순 감지 시: state source에서 재 derive 후 cache 재기록
- cache는 항상 source로부터 재구성 가능 → 손실/손상이 데이터 손실이 아님

### 14.3 §0 file 포맷

```markdown
# Live Progress — <KEY>

last_updated: <ISO8601>
last_processed_seq: <N>
current_lane: <한국어 lane 이름>
fix_cycle: <N>

✅ 요구사항 — <S3 snippet>
⏳ 설계 — 진행 중 (6/6 deputies, chief author 통합 중)
   ├─ ✅ CodebaseMapperAgent
   ├─ ✅ RefactorAgent
   ├─ ✅ SecurityArchitectAgent
   ├─ ✅ InfraOperationalArchitectAgent
   ├─ ✅ TestContractArchitectAgent
   ├─ ✅ ModuleArchitectAgent
   └─ ⏳ ArchitectAgent (chief author) — Change Plan §3 author 중
⬜ 설계 리뷰
⬜ 구현
⬜ 구현 리뷰
⬜ 구현 테스트
⬜ 보안 테스트
```

- frontmatter 없이 plain markdown + yaml-style 메타 4줄
- Story 시작 시 모든 lane `⬜` init (CFP-707 Amendment 4 — `⏸` deprecated, `⬜` empty checkbox 통일)
- Story 완료 시 `_archive/<KEY>.md` 로 mv (PMO Cross-Story 분석 input 보존)

### 14.4 Status enum (ADR-041, 4 marker — CFP-707 Amendment 4 vocabulary swap)

| 마커 | 의미 | TodoWrite native state | 사용 위치 |
|---|---|---|---|
| `⬜` | pending — 시작 안 됨 (empty checkbox) | `pending` | Lane row, agent sub-row |
| `⏳` | in_progress — 진행 중 (모래시계 시간 흐름) | `in_progress` | Lane row, agent sub-row |
| `✅` | completed — PASS / N/A / 검출 성공 / FIX 원인 lane (content suffix `FIX-N 원인 · <판정>`) | `completed` | Lane row, agent sub-row |
| `🔄` | FIX 검출 lane — retry trigger (회전 = 다시 시작) | `in_progress` (content `FIX-N detected (cause: <원인 lane>)`) | Lane row only |

**검출 label 정규화**: review/test lane 의 terminal detection 이 FAIL 인 경우에도 TodoWrite content label 은 `FAIL detected` 를 쓰지 않고 `FIX-N detected` 로 정규화한다. RESET 이 필요한 경우에도 `FIX-N detected (cause: <원인 lane>, RESET-N)` 형식. `FAIL` 은 review/test 판정 흐름의 terminal outcome vocabulary 로만 남고, TodoWrite row label 은 `FIX-N detected` 가 canonical.

**N/A**: ✅ marker + content prefix `N/A · <사유>`. PASS 와 시각 차별 (텍스트 차이).
**RESET**: ✅ marker (원인 lane content suffix `FIX-N 원인 · <판정>` 보존) + 새 lane row append (`(재진입 RESET-N)` suffix).
**blocked / waiting**: 4-marker vocabulary 범위 밖. 대기 상태는 ⬜ pending 으로 표현, 진행 중 차단성 작업은 ⏳ in_progress row 의 content 1줄 설명으로 표현.

기존 8 marker (⏸ ⏳-blocked 🔄 ✅ ❌ FIX-N ❌ FIX-N(fast-path) ⊘ 🔁) 폐기. **CFP-707 Amendment 4 vocab swap**: `⏳ pending` → `⬜` / `🔄 in_progress` → `⏳` / `❌ FIX 원인 lane` → `🔄 FIX 검출 lane` (semantic 정정 동반 — §결정 3). file / TodoWrite 두 channel 동일 어휘.

활성 lane row 라인에 inline qualifier (예: `⏳ 설계` content 미동반, sub-row 가 detail 표현. PASS 시 `✅ 설계 - PASS · Change Plan v1 + ADR-NNN`).

### 14.5 트리거 SSOT

**Verbosity policy (CFP-114 / ADR-029)** — `terminal narration` 컬럼은 `progress_narration_verbosity` 값 기반 적용:
- `full` (default, ADR-029 §결정 1+4) — 모든 ✅ 표기 항목 narrate (sub-step 포함)
- `lane_only` — lane-level event 만 narrate (CFP-20 기존 동작, sub-step 표기는 file-only 로 fallback)

| 이벤트 | 영향 라인 | 갱신 동작 | terminal narration | TodoWrite 갱신 (ADR-041 — CFP-707 Amendment 4) | full/lane_only |
|---|---|---|---|---|---|
| Story 개시 | 전체 | file create, 7 lane `⬜` | ✅ | 7 lane row ⬜ seed | both |
| Lane 진입 | top | `⬜` → `⏳ 진행 중`, current_lane 갱신 | ✅ | lane row ⬜ → ⏳ + agent sub-row 펼침 | both |
| Deputy spawn | active sub-tree | `⏳ <Deputy>` 추가, qualifier 갱신 | ✅ | agent sub-row 추가 (status=in_progress) | full only |
| Deputy return | active sub-tree | `⏳` → `✅`, qualifier 갱신 | ✅ | agent sub-row status=completed | full only |
| 병렬 dispatch (R3·R4·R7·R9) | active sub-tree | 두 SubAgent 동시 `⏳` 라인 추가 | ✅ | agent sub-row 다수 동시 in_progress (multi-row deviation) | full only |
| CI gate 시작 | 구현 테스트 | inline qualifier `(gh pr checks ⏳)` | ✅ | CI gate sub-row inline qualifier | both |
| CI gate 완료 | 구현 테스트 | qualifier 갱신 | ✅ | CI gate sub-row 갱신 | full only |
| R11 fast-path | 해당 lane | `🔄 FIX-N (fast-path)` 마커 | ✅ | lane row → ✅ collapsed, content "PASS · R11 mechanical fast-path" | both |
| Lane PASS | top | `⏳` → `✅ — <S3 snippet>`, sub-tree 접음 | ✅ | lane row → ✅ + S3 snippet, agent sub-row 제거 | both |
| Lane FIX | top | 검출 lane `⏳` → `🔄 FIX-N — <evidence 1줄>`, fix_cycle 갱신 | ✅ | 검출 lane → 🔄 + content "FIX-N detected (cause: X, retry trigger)" + 원인 lane → ✅ 유지 + content suffix "FIX-N 원인 · <판정>" + 재진입 lane row append | both |
| Lane 재진입 (FIX 후) | top | 재진입 lane row append `⏳ 진행 중 (FIX-N 재진입)` | ✅ | 재진입 lane row → ⏳ + agent sub-row 펼침 | both |
| RESET 마커 | 구현 리뷰 | `✅` → `🔁 RESET-N` | ✅ | 재진입 lane row append (suffix "(재진입 RESET-N)") | both |
| Lane N/A (plugin meta) | top | `⬜` → `⊘ N/A — <사유>` | ✅ | lane row → ✅ + content "N/A · <사유>" | both |
| 사용자 "진행상황 보여줘" | — | file 변경 없이 현재 §0 전체 emit | ✅ (SubAgent 포함 full) | TodoWrite 도 emit (file + TodoWrite 동시) | both |
| Story 완료 | 전체 | 모두 `✅`, archive mv, index 갱신 | ✅ | 7 lane row 모두 ✅, 최종 state | both |

R10 prefetch (security 1차 layer cache) 같은 사용자 무관 메타 이벤트는 **의도적 skip** (verbosity 무관).

**TodoWrite 시도 의무 + 실패 non-blocking 원칙 (ADR-041 + ADR-038 Amendment 1 §결정 8)**: 두 속성을 명확히 분리한다.

- **시도 의무 (non-skippable)**: 위 표의 TodoWrite 갱신 컬럼에 표시된 이벤트 각각에서 Orchestrator 는 TodoWrite 갱신을 **반드시 시도**해야 한다. 시도 자체를 건너뛰는 것은 ADR-038 §결정 8 위반이다.
- **실패 처리 (non-blocking)**: 시도 후 갱신 실패 시 — lane primary work 미차단. lane 은 계속 진행하고, TodoWrite discrepancy 는 warning 으로 surface 한다. 사용자 confirmation / polling / acknowledgment wait 도입 없음 (ADR-029 stop discipline 정책 무영향).

"시도를 건너뛰는 것" 과 "시도했으나 실패한 것" 은 별개의 위반이다.

**Single-Story collision rule (ADR-041)**: single-Story 모드에서도 두 concurrent lane spawn 이 같은 Story 의 TodoWrite 를 동시에 write 할 수 있다. collision 발생 시:
1. canonical §14 Lane Evidence table state 에서 todo list 전체를 재구성
2. TodoWrite hard-reset 수행: 기존 todo list 를 부분 수정하지 않고 full rewrite
3. rewrite 후 active lane / agent sub-row 는 canonical state 에 남아 있는 evidence 만 반영
4. hard-reset 결과와 collision warning 을 terminal narration / wrapper warning 으로 surface
5. lane primary work 는 중단하지 않고 계속 진행

incremental patch 금지 — collision 의심 시 항상 full rewrite.

**Narration format (ADR-029 §결정 2)** — `[<lane-한국어>] <event>: <detail>` 1 sentence stderr line. 예시:

```
[설계] Deputy spawn 6/6 병렬 (CodebaseMapper / Refactor / SecurityArch / InfraOperationalArch / TestContractArch / ModuleArch)
[설계] ModuleArchitectAgent return — §11 Migration 전략 + Rollback 경로 author 완료
[설계 리뷰] R7 병렬 dispatch — DesignReviewPL ∥ DeveloperPL Phase 2 PR 준비
[구현 테스트] CI gate 실행 중 — `gh pr checks` watching (timeout 30분)
```

세부 rule: 한국어 lane 이름, 멀티라인 금지, stderr only (file-write 와 격리). Stop discipline 정책은 ADR-022 §결정 2 + ADR-025 SSOT (본 §14.5 는 visibility 만 다룸).

### 14.6 S3 snippet 7-lane 표 (Lane PASS 시 1줄)

| Lane | snippet 템플릿 | source |
|---|---|---|
| 요구사항 | `통합 명세 §3-6 + 도메인 공백 <N>건` | RequirementsPL 통합 + DomainAgent |
| 설계 | `Change Plan v<N> + ADR-<NNN> <신규\|변경> (SubAgent <M>인)` | ArchitectPL + ADR file mtime |
| 설계 리뷰 | `PASS — Claude/Codex 종합, 코멘트 #<id>` | DesignReviewPL packet |
| 구현 | `Phase 2 PR #<num> · <commit>건 · §8.5 manifest <file>건` | DeveloperPL + git log |
| 구현 리뷰 | `PASS — Claude/Codex 종합, 코멘트 #<id>` | CodeReviewPL packet |
| 구현 테스트 | `CI gate <PASS\|FAIL> — checks <N>건` | `gh pr checks` 출력 |
| 보안 테스트 | `1차 alerts <N> / 2차 P0:<N> P1:<N>` | SecurityTestPL packet |

미정 데이터는 `?` placeholder (예: `Change Plan v? + ADR-? 신규 (SubAgent 6인)`).

### 14.7 Render flow

```
[Lane/Deputy event 발생]
  └→ Orchestrator 1차 수신
       ├→ 1) Read(.claude-work/progress/<KEY>.md)  (cache)
       ├→ 2) parse → 해당 lane sub-tree patch
       ├→ 3) Write(.claude-work/progress/<KEY>.md) — full rewrite, last_processed_seq 증가
       ├→ 4) terminal narration emit (ADR-029)
       ├→ 5) ★ TodoWrite update — non-skippable 시도 (ADR-038 §결정 8) / failure non-blocking (ADR-038 §결정 7)
       └→ 6) Story 완료 시 _archive/<KEY>.md 로 mv + index.md 갱신
```

**TodoWrite update (step 5) detail (ADR-041 — CFP-707 Amendment 4)**:
- Lane 진입: lane row → ⏳ + agent sub-row 펼침 (PL → workers/deputies → chief 순)
- Agent return: 해당 agent sub-row 의 status=completed + content 갱신 (1-line 활동 결과)
- Lane PASS: agent sub-row 제거, lane row content = `PASS · <S3 snippet>`
- Lane FIX (검출 후): 검출 lane → 🔄 + content `FIX-N detected (cause: <원인 lane>, retry trigger)`, 원인 lane → ✅ 유지 + content suffix `FIX-N 원인 · <원인 판정 1줄>` (lane PASS evidence 보존, FIX trigger origin 은 content text 로 책임 추적), 재진입 lane row append (⏳ 시작)
- Multi-row in_progress 의도적 허용 (TodoWrite "ONE in_progress" 가이드 deviation, codeforge 병렬 agent 모델)
- Single-Story 모드 — `[KEY]` prefix drop (모든 row 에서)
- 시도 의무: step 5 건너뛰기는 ADR-038 §결정 8 위반 (시도 후 실패는 §결정 7 — non-blocking)
- 실패 처리: TodoWrite update 실패 시 warning, lane primary work 미차단 (§14.5 원칙)

### 14.8 Resume / corruption 처리

세션 재개 / 압축 재개 시:

1. `.claude-work/progress/<KEY>.md` 존재 여부 확인
2. **존재해도 신뢰하지 않음** — state source(Story §10 + GitHub Issue phase label + Story §-fill state)에서 재 derive
3. 재 derive 결과를 cache 재기록, last_processed_seq 갱신
4. **★ TodoWrite re-build (ADR-041 NEW — CFP-707 Amendment 4 vocab)**: §0 file 의 lane 별도 status 로 TodoWrite full rewrite
   - active lane 의 agent sub-row 는 빈 상태 (SubAgent 활성 정보 손실 허용 — 다음 SubAgent 이벤트에서 자동 충족)
   - 4 marker (⬜ ⏳ ✅ 🔄) 어휘로 변환
   - Single-Story 모드 — `[KEY]` prefix drop
   - best-effort — TodoWrite re-build 실패 시 아래 경고 출력 후 file-only 상태로 lane work 진행 (ADR-038 §결정 7):
     `⚠️ TodoWrite 재빌드 실패 — 진행상황 표시가 부정확할 수 있습니다. 현재 상태: <§14 Lane Evidence 최신 row>`
5. SubAgent sub-tree 는 비워둠 (file + TodoWrite 동일 — 다음 SubAgent 이벤트에서 자동 충족)

손상 시: parse 실패 → backup(`<KEY>.md.bak`) → state source에서 재 derive.

### 14.9 Multi-Story index

`.claude-work/progress/index.md`:

```markdown
# Active Stories Index

last_updated: <ISO8601>

- CFP-20 (phase: 설계, fix_cycle: 0)
- CFP-21 (phase: 구현 리뷰, fix_cycle: 1)
```

- Orchestrator가 모든 active Story KEY + 현재 phase만 기록
- "always latest" pointer로 사용 (다음 작업 분기 시 어느 Story가 활성인지 파악)
- SSOT 아님 — 진실은 각 `<KEY>.md` 와 state source

### 14.10 Story 완료 archive

Story Phase 2 PR merge 후:

```bash
mv .claude-work/progress/<KEY>.md .claude-work/progress/_archive/<KEY>.md
```

Orchestrator는 `_archive/` 디렉토리 부재 시 `mkdir -p` 후 mv. PMOAgent Cross-Story 분석은 `_archive/**` glob 으로 누적 progress 참조.

Story 중도 폐기 시: `_archive/<KEY>-aborted.md` 로 mv, 사용자 narration "Story 폐기".

### 14.11 Spawn ID 대장 mini-table (Issue #312)

Orchestrator 는 매 agent spawn 시 **Spawn ID 대장**을 `.claude-work/progress/<KEY>.md` 에 실시간 갱신한다. 목적: SendMessage target 모호성 해소 + 병렬 spawn 추적.

**포맷**:

```markdown
## Spawn ID 대장

| spawn_id | agent_type | lane | spawn_at |
|---|---|---|---|
| spawn-001 | RequirementsPLAgent | 요구사항 | 2026-05-09T10:00:00Z |
| spawn-002 | DomainAgent | 요구사항 | 2026-05-09T10:00:05Z |
| spawn-003 | ArchitectPLAgent | 설계 | 2026-05-09T10:15:00Z |
```

**갱신 의무**:
- spawn 직전 (spawn_at 기록 시점) 에 row 추가 — return 대기 없이 즉시 기록.
- spawn_id 형식: `spawn-NNN` (전역 단조 증가, Story 전체 통합 카운터).
- `agent_type` = agent file 식별자 (예: `ArchitectAgent`, `role:dev:SoftwareDeveloperAgent`).
- `lane` = 해당 spawn 의 진입 레인 (예: 설계, 구현, 구현-리뷰).
- `spawn_at` = ISO 8601 UTC. **§14 본문 markdown 표 Start/End column = KST `+09:00` (display layer — ADR-079 §결정 9 dual-layer co-existence)**. schema field `spawned_at`/`returned_at` = UTC strict 보존 (contract field layer).

**팀 컨텍스트 (env=1)**:
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 시 SendMessage 대상 지정에 spawn_id 를 사용 (teammate 이름 중복 시 spawn_id 로 disambiguate).
- TeamCreate 전·후로 스폰된 PL / teammate 모두 동일 대장에 기록.

**위치**: `.claude-work/progress/<KEY>.md` 의 `## Spawn ID 대장` 섹션 (14.3 §0 file 포맷 뒤에 append). gitignored — ephemeral cache.

### 14.12 Spawn-level token telemetry mini-table (Issue #300)

Orchestrator 는 매 spawn 결과 수령 후 **Spawn token telemetry 대장**을 `.claude-work/progress/<KEY>.md` 에 갱신한다. 목적: 레인별·에이전트별 token quota 분석 + §8.2 예산 대비 실적 추적.

**포맷**:

```markdown
## Spawn Token Telemetry

| spawn_id | agent_type | lane | spawn_at | input_tokens | output_tokens |
|---|---|---|---|---|---|
| spawn-001 | RequirementsPLAgent | 요구사항 | 2026-05-09T10:00:00Z | 12340 | 3210 |
| spawn-002 | DomainAgent | 요구사항 | 2026-05-09T10:00:05Z | 8900 | 1540 |
| spawn-003 | ArchitectPLAgent | 설계 | 2026-05-09T10:15:00Z | 21000 | 7800 |
```

**기록 규칙**:
- `input_tokens` / `output_tokens` = spawn return 시 플랫폼이 노출하는 값. 미노출 시 `?` placeholder.
- §8.3 세션 회고 보고 "토큰 사용량" 표 는 본 대장의 집계값으로 채움 (에이전트별 행 일치).
- 레인 합계 = 해당 레인 spawn row 의 `input_tokens + output_tokens` 합산 → §8.2 Total 사전 예산 비교 input.

**관계 (§15 4-channel observability)**:
- 본 대장은 Tier 1 ephemeral 채널 (`.claude-work/progress/<KEY>.md` cache 와 동일 파일). gitignored.
- stop-event-v1 (Tier 3) 과 이중 기록 금지 — quota 분석용 로컬 계산 전용.
- spawn-event-v1 (§15.2 boundary note, ADR-042 §결정 3 보류) 신설 전까지 본 대장이 spawn 단위 token 추적 유일 source.

---

### 14.11 완료 시각 + 소요 시간 reporting (normative — wrapper + all consumers)

Orchestrator 는 substantive milestone 마다 완료 시각 + 소요 시간을 final report 또는 단계 마무리 메시지에 명시한다.

**Reporting 의무 트리거**:
- Phase 1 PR open / merge
- Phase 2 PR open / merge
- Story close (Phase 2 PR merge + Issue auto-close)
- Lane gate transition (설계 리뷰 PASS / 구현 리뷰 PASS / CI PASS)
- 사용자 가시 milestone (ad-hoc 요청 완료 / FIX loop 완료)

**형식**:
```
Phase 2 PR merged (14:23, 이 단계 37분 / 세션 시작부터 1h 12m)
```
- 시각: `HH:MM`
- 소요 시간: incremental (해당 단계 시작부터) + cumulative (세션 시작부터) 모두 명시
- Trivial 작업 (1 commit, 1 file edit) = skip OK. Substantive milestone = 의무.

**TodoWrite 연동**: §14.7 render flow step 5 의 lane row content 에 완료 시각 suffix 포함 권장 (`✅ 구현 레인 PASS · 14:23`). TodoWrite update best-effort 정책(ADR-038 §결정 7) 유지 — TodoWrite 실패 시에도 메시지 내 시간 명시는 이 §14.11 normative 규칙으로 유지.

---

## 15. 4-channel observability boundary (ADR-042 §결정 1, CFP-283)

Codeforge observability stack 의 channel 별도 책임 분리 normative SSOT. Tier 1 (ephemeral) / Tier 2 (committed lane-coarse) / Tier 3 (persistent measurement) 으로 stratify, 각 channel 의 Granularity / Storage / Owner / Lifecycle 명시 — boundary race + double-count 차단 invariant.

### 15.1 7-channel boundary table

| Channel | Tier | Granularity | Storage | Owner | Lifecycle |
|---|---|---|---|---|---|
| **stderr narration** ([ADR-029](../archive/adr/ADR-029-phase-execution-visibility-expansion.md)) | 1 ephemeral | sub-step | scrollback | Orchestrator | session-only |
| **TodoWrite scratchpad** ([ADR-038](../archive/adr/ADR-038-progress-visualization-todowrite.md)) | 1 ephemeral | meta-cognitive | tool surface | Orchestrator | turn-only |
| **`.claude-work/progress/<KEY>.md` cache** (CFP-20) | 1 ephemeral | per-Story coarse | fs cache | Orchestrator | Story-only (post-merge mv `_archive/`) |
| **Story §10 FIX Ledger** (CFP-32 / [fix-event-v1](inter-plugin-contracts/fix-event-v1.md)) | 2 committed | discrete FIX event | git commit | Orchestrator monopoly | persistent (append-only) |
| **Story §14 Lane Evidence** ([ADR-031](../archive/adr/ADR-031-lane-spawn-evidence-trail.md)) | 2 committed | lane spawn coarse | git commit | Orchestrator monopoly | persistent (append-only) |
| **post-merge-counters.jsonl** ([ADR-026](../archive/adr/ADR-026-post-merge-automation.md)) | 3 persistent | post-merge action outcome | git commit | post-merge-followup.yml | persistent (append-only, opt-in) |
| **stop-event-v1 ledger** ([ADR-042 §결정 2](../archive/adr/ADR-042-codeforge-measurement-channel-architecture.md), [stop-event-v1](inter-plugin-contracts/stop-event-v1.md)) | 3 persistent | discrete stop event | hot tier (sqlite/JSONL) + cold tier (markdown) | Orchestrator-owned delegate subagent | hot 7-30d / cold persistent / opt-in default false |

### 15.2 Boundary 차단 invariant (3)

- **TodoWrite ↔ stop-event-v1 boundary**: TodoWrite 호출은 stop-event-v1 ledger record 대상 아님 ([ADR-038](../archive/adr/ADR-038-progress-visualization-todowrite.md) standalone 정당화 — meta-cognitive scratchpad, file system / GitHub state mutation 미발화). boundary 차단.
- **§14 ↔ spawn-event-v1 boundary**: spawn-event-v1 신설 보류 ([ADR-042 §결정 3](../archive/adr/ADR-042-codeforge-measurement-channel-architecture.md)) — 본 boundary race 회피. Phase 2 spawn-event land 시 dedup script 신설 의무 (§14 row count 와 spawn-event lane=spawn type count 정합 검증).
- **§10 ↔ stop-event-v1 boundary**: stop-event-v1 의 `reason_class: policy_violation` row 가 §10 FIX Ledger row append 의 proxy. dedup 책임 = aggregate script (Phase 2). cold tier 별도 file 신설 안 함 — §10 가 cold tier proxy.

### 15.3 5번째 measurement channel 추가 invariant

5번째 measurement channel (Tier 3) 추가 = [ADR-042](../archive/adr/ADR-042-codeforge-measurement-channel-architecture.md) amendment 의무. 본 closed enumeration 가 future "X tool 호출도 ledger record" 류 압박을 차단 — 모두 7-channel 의 어느 하나로 routing 또는 ADR amendment 발의.

### 15.4 Privacy / opt-in 정책 SSOT

stop-event-v1 ledger 의 privacy / opt-in / sanitize 정책 = [ADR-043 (codeforge telemetry privacy policy)](../archive/adr/ADR-043-codeforge-telemetry-privacy-policy.md) SSOT. 핵심 invariant 3:

- **opt-in default false** (consumer overlay `telemetry.enabled: false` default)
- **Allow-list ONLY 16 field whitelist** (capture 시점 — stop-event-v1 schema 16 field 외 capture 금지)
- **Deny-list regex 6 pattern** (capture 통과 후 2차 안전망 — API key / GitHub PAT / 한국 주민번호 / email / hex≥32 / GitHub fine-grained PAT)

### 15.5 0 API call constraint + measurement-vs-fix scope boundary

- **0 API call constraint** ([ADR-042 §결정 8](../archive/adr/ADR-042-codeforge-measurement-channel-architecture.md)) — telemetry instrumentation = local I/O only. Anthropic API / GitHub API / external service 호출 금지. measurement = measure 대상 amplify 금지 (CRITICAL invariant).
- **measurement-vs-fix scope boundary** ([ADR-042 §결정 10](../archive/adr/ADR-042-codeforge-measurement-channel-architecture.md)) — CFP-283 scope = measurement only. throttling / backoff / circuit breaker / rule-based hook = 별도 후속 CFP.
- **ROI gating** ([ADR-042 §결정 11](../archive/adr/ADR-042-codeforge-measurement-channel-architecture.md)) — Phase 2 enforcement 발동 prerequisite = post-merge-counters.jsonl 30+ run 누적 ([ADR-026 §결정 3](../archive/adr/ADR-026-post-merge-automation.md) 패턴 정합).

### 15.6 Cross-references

- [ADR-042](../archive/adr/ADR-042-codeforge-measurement-channel-architecture.md) — measurement channel architecture (본 §15 SSOT)
- [ADR-043](../archive/adr/ADR-043-codeforge-telemetry-privacy-policy.md) — telemetry privacy policy (sibling)
- [stop-event-v1](inter-plugin-contracts/stop-event-v1.md) — kind:registry 16-field schema
- [project-config-schema.md](project-config-schema.md) — telemetry block schema (opt-in default false)
- [consumer-guide.md](consumer-guide.md) § "Telemetry opt-in" — consumer 측 안내
- [docs/domain-knowledge/domain/orchestrator-discipline/measurement-channel.md](domain-knowledge/domain/orchestrator-discipline/measurement-channel.md) — 도메인 정의 + cross-ADR boundary 설명

---

## 16. Post-merge automation flow (ADR-026 + CFP-74)

ADR-026 의무 — wrapper Orchestrator 가 PR merge event 시 4 action 자동 처리.

> **절차 본문 (§16.1 Trigger / §16.2 Disable-by-flag / §16.3 4 Action sequence / §16.4 Telemetry counter / §16.6 Idempotency / §16.7 Boundary) = `codeforge:post-merge-closure` skill 로 이전** (CFP-2198 / ADR-120 §결정 1 cold×guide). PR merge 후처리 확인 시 해당 skill 호출. 아래 §16.5 는 gate — 본문 잔류 (ADR-120 §결정 3).

### 16.5 main 직접 push 금지 invariant

internal-docs cross-repo write 는 항상 branch (`<key>-post-merge-followup-prN`) + PR open 패턴. 사용자 admin merge 패턴 유지. 본 invariant 위반 시 ADR-024 위반 = policy_violation defect.

---

## 17. Inter-plugin contract 갱신 절차 (단일 원본 — CFP-2158 / ADR-118 D5)

구 sibling sync 절차 (CFP-408 / ADR-010 Amendment 3) 는 **Superseded** (ADR-010 Amendment 5) — monorepo 통합 (ADR-118 S1) 으로 canonical/sibling 이중체계가 소멸했다.

### 17.1 단일 원본 절차

- **contract version bump** = wrapper `docs/inter-plugin-contracts/<file>` + `MANIFEST.yaml` row **동시 갱신 (atomic, 같은 PR)**. cross-repo sync PR 불요.
- **신규 contract 추가** = 2단계: ① wrapper `docs/inter-plugin-contracts/` 직접 작성 ② MANIFEST entry 추가 (같은 PR).
- versioning 룰 = ADR-008 불변 (MAJOR/MINOR/PATCH SemVer).
- 구 `scripts/sync-contract-bump.sh` 호출 지시는 폐지 — script 자체가 S3 (CFP-2159, 구현 PR #2164) 에서 삭제됨.

### 17.2 Confluence derived mirror

본 §17 의 Confluence mirror (page 2131113) 는 **derived** — 본 절 갱신 후 Confluence 후속 sync 의무 (ADR-103 채널).

---

## 18. PMOAgent retro batch closure operating sequence (CFP-1680 / ADR-045 §D-11)

PMOAgent 가 누적 LOW/MEDIUM follow-up Issue (≥ 3) 의 batch closure 진행 시 본 §18 5 sub-section 적용 의무. ADR-045 §D-11 paired sibling SSOT — normative wording = ADR-045 §D-11, 본 §18 = Orchestrator/PMOAgent 운영 절차 codify.

> **운영 절차 (§D-9/§D-10/§D-11 axis 분리 / §18.1 trigger 조건 / §18.2 4-option decision tree / §18.4 closure summary table / §18.5 retro PR auto-merge sequence) = `codeforge:post-merge-closure` skill 로 이전** (CFP-2198 / ADR-120 §결정 1 cold×guide). batch closure 진입 시 해당 skill 호출. normative wording SSOT = ADR-045 §D-11 (불변). 아래 §18.3 verify-before-trust mandate 는 gate — 본문 잔류 (ADR-120 §결정 3).

### 18.3 Verify-before-trust mandate workflow (5 sub-scope)

PMOAgent batch closure write-time 각 Issue 에 다음 5 sub-scope 의무 (ADR-045 §D-11 (2) 정합):

| sub-scope | verify 대상 | command / source | cross-ref |
|---|---|---|---|
| (a) per-Issue body verbatim cite | Issue body wording 직접 인용 | `mcp__github__issue_read method=get` body field verbatim | ADR-082 §결정 1 layer 1 sub-scope (1-C) USER-UTTERANCE-VERBATIM block 패턴 답습 |
| (b) recent merge state direct verify | carrier PR merge state | `gh api repos/<owner>/<repo>/pulls/<N>` + `git log --oneline <SHA>` | ADR-073 verify-before-assert primitive 답습 |
| (c) axis disjoint discrimination | "비슷한 carrier 가 cover 한다" false-positive obviation | manual axis enumeration + Issue body intent ↔ carrier scope diff verify | ADR-082 §결정 12 retro-time verify-before-trust 정합 batch closure 영역 |
| (d) sibling carrier cross-link via PR number | closure rationale 안 PR/Issue 번호 explicit cite | comment body 안 #NNN explicit cite + `mcp__github__pull_request_read` verify | ADR-082 §결정 9 verify-before-cite 양방향 답습 batch closure 영역 |
| (e) sub-scope alphabet sequential verify | 본 §18.3 sub-scope (a)~(e) pre-write 위치 확인 | manual sub-scope alphabet sequential check before each verify step | ADR-082 §결정 1 sub-scope codify 패턴 답습 |

**1+ sub-scope failure** = closure 중단 + 본 §18.2 decision tree 재진입 (DEFER 또는 PROMOTE 으로 re-classify).

---

## 부록 A. 관련 문서

- `CLAUDE.md` — 에이전트 목록·레인·권한·GitHub Workflow·ADR 규약 ("무엇")
- 각 `agents/<Name>.md` — 에이전트별 역할·포지션·제약 (SSOT)
- 각 lane plugin `CLAUDE.md` self-write 표 — 문서화 표준 SSOT (Issue 코멘트 phase prefix, Story file 섹션 책임 분담) — codeforge-{review,pmo,requirements,test,develop,design}
- `.claude/_overlay/project.yaml` — 프로젝트 SSOT 상수 (GitHub·labels). Schema: `docs/project-config-schema.md`
- `docs/stories/<KEY>.md` — Story 11섹션 single-file SSOT
- `docs/adr/ADR-NNN-<slug>.md` — 설계 결정 아카이브 (flat, frontmatter category)
- `docs/change-plans/<slug>.md` — Change Plan 실행 명세 (Git-versioned)
- `templates/github-workflows/` — 6 GitHub Actions SSOT (consumer가 .github/workflows/로 복사)
- `templates/github-issue-forms/` — story.yml / bug.yml / audit.yml
- `templates/CODEOWNERS.template`, `templates/github-pr-template.md`

## 부록 B. 개정 이력

- 2026-04-23: 초기 작성 (18 에이전트 · 4 레인)
- 2026-04-24: v2 개편 (21 에이전트 · 6 레인) — EngineerPL 제거, CodebaseMapper·DesignReviewPL·ClaudeDesignReview·CodexDesignReview 신설, Review/Test 리네임, DocsAgent 단독 writer 원칙, FIX 카운터 Jira 라벨 단일, Fast-path/Codex 효용 평가 미도입
- 2026-04-24: v3 플러그인 pivot (범용 SW 개발 플러그인 `codeforge`로 재편, 22 에이전트 · 6 레인) — crypto 정체성 제거, overlay 메커니즘 β 도입
- 2026-04-24: v4 보안 테스트 레인 추가 (25 에이전트 · 7 레인) — SecurityTestPLAgent + ClaudeSecurityTestAgent + CodexSecurityTestAgent 신설, "테스트" 레인을 "구현 테스트"로 개편 후 "보안 테스트" 레인 추가, templates/ 디렉토리 도입
- 2026-04-24: v5 generic Dev roster + preset 시스템 (23 core 에이전트 + `role: dev` 동적 roster · 7 레인) — BackendDev·FrontendDev를 `presets/webapp/`으로 이동, core에 generic `DeveloperAgent` 신설, ServerEng를 `InfraEngineerAgent`로 리네임(범위 확장), DevPL이 `role: dev` frontmatter 태그로 런타임 roster discovery
- 2026-04-24: v6 Stage 2 `project.yaml` 구조화 SSOT 상수 도입
- 2026-04-26: **v8 Atlassian 제거 + GitHub 전환 (BREAKING)** — Confluence/Jira backend 완전 제거, GitHub primitive (Issues / PR / Milestones / Sub-issues / Projects v2 / Discussions / Actions / repo files / CODEOWNERS) 단일 backend화. Story 페이지 → `docs/stories/<KEY>.md` single-file SSOT. ADR → `docs/adr/ADR-NNN-<slug>.md` flat. Domain KB → `docs/domain-knowledge/<area>/<topic>.md` 계층. 1 Story = 2 PRs (Phase 1 docs / Phase 2 code+docs append). 6 GitHub Actions 자동화 (story-init / phase-label-invariant / story-section-1-immutable / subissue-from-impl-manifest / phase-gate-mergeable / fix-ledger-sync). 보안 테스트 1차 layer = Dependabot/CodeQL/Secret Scanning/Push Protection. project.yaml schema `atlassian.*` → `github.*`. `gh` CLI 필수 추가, `github@claude-plugins-official` 플러그인 필수 격상.
- 2026-04-26: **v9 Review/Test 워커 통합 (BREAKING)** — [ADR-001](../archive/adr/ADR-001-review-agent-unification.md). 3 lane × 2 vendor = 6 워커(Claude/Codex × Design/Code/Security)를 lane-agnostic 2 워커(`ClaudeReviewAgent` / `CodexReviewAgent`)로 통합. 도메인은 호출 PL이 review packet으로 주입(checklist_path · scope_globs · category_enum · severity_overrides). 공통 base SSOT = `templates/review-pl-base.md`, 체크리스트 SSOT = `templates/review-checklists/{design,code,security}.md`. 25 → **20 core agents**. SecurityTestPL에 `Bash(gh api repos/*)` 권한 부여(1차 layer alerts fetch). 워커 packet 누락 시 `ESCALATE_PACKET_INCOMPLETE` 강제 — generic fallback 금지.

- 2026-05-09: **v10 CFP-293** — §8.4 성능 베이스라인 정책 (Issue #306 / NF-T5) 신설 + §14.11 Spawn ID 대장 mini-table (Issue #312) 신설 + §14.12 Spawn-level token telemetry mini-table (Issue #300) 신설.
- 2026-06-13: **v11 CFP-2198** — §7/§9/§16/§18 의 cold×guide 절차 본문을 on-demand skill 2종 (`codeforge:session-recovery` = §7.1-§7.3+§7.5-§7.6+§9.1-§9.5 / `codeforge:post-merge-closure` = §16.1-§16.4+§16.6-§16.7+§18.1-§18.2+§18.4-§18.5) 으로 이전 — ADR-120 첫 실집행 (Epic #2189 S2). gate 명제 (§7.4 / §9.6-§9.7.1 / §16.5 / §18.3) 는 본문 잔류. §14 = hot×gate INELIGIBLE 확정 (ADR-031 §결정 3 + 참조 21건).

본 playbook은 에이전트 구조·규약 변경 시 PR과 함께 갱신. git log로 변경 추적.
