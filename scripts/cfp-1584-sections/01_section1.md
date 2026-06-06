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

   **0a-prime. SessionStart hook — worktree-gc (CFP-427 / ADR-040 §결정 5)**

   wrapper repo `.claude/settings.json` `hooks.SessionStart[]` array 두 번째 entry = `bash "${CLAUDE_PROJECT_DIR}/templates/scripts/check-worktree-stale.sh" || true` (CFP-427 Story 2 merge 후 effective). 매 wrapper repo Claude Code session 시작 시 stale worktree (mtime ≥ 7 days + origin branch absent) 자동 prune. session 차단 0 (`|| true` postfix). bypass = `BYPASS_WORKTREE_GC=1` env (rare debugging only). 폐쇄루프 안전망 = `scripts/check-session-start-hook-presence.sh` (CFP-427 warning tier). prereq-check entry (CFP-500, 1번째 entry) 와 disjoint scope — 양쪽 entry 모두 sequential 실행.

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

   **0ii. Windows external session auto-resume (CFP-1355 / [ADR-110](adr/ADR-110-external-runtime-wrapper-ssot-boundary.md))**

   **Consumer opt-in** — Windows Task Scheduler wrapper (PowerShell `codeforge-session-resume.ps1` + `codeforge-auto-resume.xml` template) 자동 session 재개. rate-limit 도달로 session 종료 후, reset window 만료 시 `claude --resume` 자동 invoke. `scripts/install-codeforge-resume.ps1` (admin) 로 설치, `.claude/_overlay/project.yaml` `runtime.auto_resume.enabled: true` toggle 로 활성. Linux/macOS = Phase 2 sub-CFP carrier. docs/consumer-guide.md §1j 참조.

   **Wrapper dogfooding** — wrapper repo 자체 `.claude/settings.json` 에 본 hook 등록 의무 (Story §5.2 AC-1a / AC-8 (4)). consumer 측 등록 절차는 `docs/consumer-guide.md` § "Session start hooks" 참조.

1. **메모리 로드**: `~/.claude/projects/<workspace-hash>/memory/MEMORY.md` — 이전 세션 feedback·project·reference 기록 확인
2. **활성 Story 조회**: `mcp__github__list_issues(state='open', labels=['type:story'])`
3. **ADR 목록 확인**: 세션 내 첫 설계 결정 직전에만 `Glob(docs/adr/ADR-*.md)` + `Grep` (frontmatter category·status 필터)
4. **태스크 분류**:
   - 신규 요구사항 → §1.2 신규 세션 플로우 (또는 §1.2.0 Stage 0 옵션)
   - resume (활성 Story 존재) → §7 세션 재개 복원 절차

### 1.2.0 Stage 0 (선택, recommended for non-trivial Story) — pre-Issue brainstorming

복잡한 요구사항 (cross-cutting / 새 도메인 / 모호한 scope) 인 경우 Issue Form 제출 전 `superpowers:brainstorming` skill 로 사전 scoping 가능. **옵션 — CI 강제 없음** ([ADR-034](adr/ADR-034-pre-issue-brainstorming-stage.md)).

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
  └─ PMOAgent 스폰 (회고 감사 + FIX Ledger 리뷰 + ADR 후보 검토)
```

### 1.3 세션 종료 조건

- **정상 완료**: 보안 테스트 레인 PASS → PMOAgent 가 Story file §11 직접 self-write (codeforge-pmo) + Phase 2 PR `Closes #N` 머지 → Issue 자동 close → 세션 회고 (§8.3) → 종료
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

