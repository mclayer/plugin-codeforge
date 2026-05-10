---
title: Orchestrator Playbook
status: active
owner: Orchestrator (= 최상위 Claude 세션)
created: 2026-04-23
updated: 2026-04-26
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

# Orchestrator Playbook

최상위 Claude 세션(이하 **Orchestrator**)의 행동 SSOT. 사용자(Human)가 제공한 요구사항을 받아 **0 core 에이전트 (wrapper-only)** + 6 lane plugin (codeforge-{review,pmo,requirements,test,develop,design}) + role:dev roster를 조정하는 모든 규약을 담는다.

**CFP-29 Phase 1 (BREAKING v0.17.0) 이후**: 5 review agent (Design/Code/SecurityTest PL + Claude/Codex worker)는 별도 plugin [codeforge-review](https://github.com/mclayer/plugin-codeforge-review)로 추출됨. Orchestrator는 본 playbook의 관점에서 이들을 **외부 plugin agent**로 spawn하며, 결과는 `review_verdict v3` typed contract ([`docs/inter-plugin-contracts/review-verdict-v3.md`](inter-plugin-contracts/review-verdict-v3.md))로 수령한다 (v2 는 CFP-61 / ADR-022 시점 Archived, v1 은 CFP-D 시점 Archived — historical records).

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

   [블로커 X건 — 복구 완료 전 대기]
   ```

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
| `phase:구현-테스트` | → `phase:보안-테스트` (lanes.security_ai: true 시만) 또는 terminal | **Orchestrator** (ADR-048 CI gate inline) |
| `phase:보안-테스트` | terminal (Issue close 시점) | **Orchestrator** + `gate:security-test-pass` 부착 |

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

### 2.3 사용자 ESCALATE 프롬프트 표준 형식

```
⚠️ 사용자 판단 요청 (ESCALATE)

[상황]
- Story: <KEY> — {한 줄 요약}
- 현재 단계: {phase:설계-리뷰 / phase:구현-리뷰 / phase:구현-테스트 / phase:보안-테스트}
- 트리거: {설계 리뷰 3회 FIX / 구현 리뷰 3회 FIX / 테스트 반복 FAIL / ADR 충돌 / breaking change}

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

#### §3.0.5 구현 실행 방식 — Subagent-Driven 자동 선택 (CFP-358)

`superpowers:executing-plans` 또는 `superpowers:subagent-driven-development` 스킬 실행 중 "구현 실행 방식 선택" 프롬프트(Subagent-Driven vs Inline Execution)가 발생하면, `AskUserQuestion`으로 사용자에게 묻지 않고 **자동으로 Subagent-Driven 경로를 선택**해 진행한다.

이 정책은 wrapper + 모든 consumer에 동일 적용. behavioral directive → memory 저장 금지 (normative) 케이스 — playbook이 enforcement SSOT.

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

- **Policy SSOT**: [ADR-039](../docs/adr/ADR-039-orchestrator-subagent-default-for-codeforge-modification-work.md) (amends ADR-009)
- **Motivation**: [ADR-025](../docs/adr/ADR-025-stop-discipline-non-whitelist-as-defect.md) §결정 7 (`policy_violation_subdecision`)
- **Narration interaction**: [ADR-029](../docs/adr/ADR-029-phase-execution-visibility-expansion.md) (매 spawn / return narrate 의무)
- **§14 evidence**: [ADR-031](../docs/adr/ADR-031-lane-spawn-evidence-trail.md) Amendment 1 (Orchestrator-owned delegate inclusion)
- **§10 FIX Ledger**: [fix-event-v1](../docs/inter-plugin-contracts/fix-event-v1.md) Amendment (Orchestrator-owned delegate inclusion)
- **TodoWrite scratchpad**: TodoWrite tool surface 자체 standalone 정당화 (file write 아님 — meta progress channel). ADR-041 = informational reference, normative dep 아님 (PR #277 머지 order 무관).
- **Subagent semantics 분기**: [ADR-035](../docs/adr/ADR-035-codeforge-agent-teams-epic-architecture.md) (default subagent context 의 one-shot subagent — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0`)
- **Consumer scope**: [consumer-guide.md § "Subagent default (codeforge orchestration)"](consumer-guide.md)
- **Hotfix scope**: [hotfix-playbook.md](hotfix-playbook.md) (exception 없음 — 사용자 verbatim "무조건")

#### §3.0.9 Pre-action fact verification (normative — wrapper + all consumers)

Orchestrator 가 사용자에게 substantive path 를 제시하거나 외부 system 동작을 인용하기 전, 아래 5-item self-audit 의무:

| 항목 | verify 도구 | skip 금지 조건 |
|---|---|---|
| 인용 file / 디렉터리 실제 존재 여부 | `Glob` / `Bash ls` | path 를 사용자에게 제시하는 모든 경우 |
| workflow / Action trigger 조건 | `Read` | "자동으로 X 가 일어남" 주장 전 |
| schema / config 실제 fields | `Read` | structured contract 인용 전 |
| GitHub Issue / state | `mcp__github__issue_read` | Issue 상태 주장 전 |
| 사용자 환경 state | `Read ~/.claude/settings.json` 또는 `Bash which` | 설치 여부·인증 상태 주장 전 |

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
- **Subagent spawn 시**: prompt 에 `Working dir: <worktree-path>` 명시 — lane spawn (§3.5) 과 ad-hoc spawn 동일
- **Ad-hoc 작업 포함**: lane spawn 외 일반 subagent spawn, 사용자 직접 작업 모두 동일 적용
- **Consumer 동일 적용**: consumer project 에서 codeforge 사용 시 동일 rule
- **위반 판정**: 원본 working directory 에서 file edit/write/bash 수행 = stop discipline 위반 (ADR-025 §결정 2 `policy_violation`)

인프라 SSOT: ADR-040 (CFP-136). Script: `bash templates/scripts/worktree-create.sh <branch> <base-ref>`.

### 3.1 7 레인 + Cross-cutting 스폰 순서 (요약)

```
[Cross-cutting 트리거]
Epic 창설:  Orchestrator → PMOAgent (Scope 분해 자문)
Story 완료: Orchestrator → PMOAgent (회고 감사 + ADR 후보 검토)

[Story 내부 7 레인]
요구사항:    Orchestrator → RequirementsPLAgent(DomainAgent ∥ Analyst ∥ Researcher 병렬, 셋 다 non-skippable) → PL dedup·상충 조정 → Story file §3-6 갱신
설계:        Orchestrator → ArchitectPLAgent → (CodebaseMapper ∥ Refactor ∥ SecurityArchitect ∥ TestContractArch ∥ DataMigrationArchitect 병렬) → ArchitectAgent (chief author) 통합 → ArchitectPLAgent 검수 → Change Plan 확정
                         → ArchitectAgent direct write (docs/change-plans/<slug>.md + docs/adr/ADR-NNN-<slug>.md) + ArchitectAgent 가 Story file §3/§7/§11 직접 self-write (codeforge-design self-write 표)
설계 리뷰:   Orchestrator → DesignReviewPLAgent (lane=design packet 작성) → packet return (no writes — CFP-61 / ADR-022)
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
             → Orchestrator가 한 메시지에 (ClaudeReviewAgent ∥ CodexReviewAgent) dispatch → PL 종합 → PASS/FIX (R3, R2)
             → PASS/FIX 결정: review-verdict 5-step algorithm 적용 (위 설계-리뷰 동일 흐름, lane=code, [구현-리뷰] prefix)
                         FIX 시 mechanical_category 자격 확인 → fast-path 또는 정상 cycle (R11)
구현 테스트: CI gate (ADR-048) — Orchestrator inline 수행:
                         `gh pr checks <PR_NUMBER> --watch` (timeout 30분)
                         → PASS + lanes.security_ai: false (default): merge gate 진입
                         → PASS + lanes.security_ai: true: SecurityTestPL spawn
                         → FAIL: `gh run view --log-failed` 수집 → FIX loop (DeveloperPL 1차 진단 → ArchitectPL 최종 판정)
보안 테스트: Orchestrator → SecurityTestPLAgent (lanes.security_ai: true 시만, lane=security packet 작성, 1차 layer cache hit/miss 확인)
             1차 layer: .claude-work/cache/<KEY>-sec1.json hit 시 inline 첨부 (R10) / miss 시 PL이 직접 fetch
             2차 layer: PL이 packet return → Orchestrator가 한 메시지에 (ClaudeReviewAgent ∥ CodexReviewAgent) dispatch → PL 종합 → PASS/FIX (R3, R2)
                         → PASS/FIX 결정: review-verdict 5-step algorithm 적용 (위 설계-리뷰 동일 흐름, lane=security)
                         → PASS 시 Orchestrator post-Sonnet self-write (gate:security-test-pass 라벨 부착) → Phase 2 PR mergeable
완료:        Phase 2 PR merge (`Closes #<Story Issue>`) → Issue 자동 close → PMOAgent 가 Story §11 직접 self-write (codeforge-pmo)
             → PMOAgent (회고)
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
| **ArchitectPLAgent** | 설계 lane PL. 6 deputy(CodebaseMapper ∥ Refactor ∥ SecurityArchitect ∥ OperationalRiskArchitect ∥ TestContractArchitect ∥ DataMigrationArchitect) 병렬 스폰 후 ArchitectAgent (chief author) 통합 의뢰 → draft 검수. FIX 최종 판정자 (구현 리뷰·구현 테스트·보안 테스트 FAIL 시). Stateless 재스폰. write queue 의뢰 권한 |
| **ArchitectAgent** | Change Plan §1-§11 chief author + ADR draft author + §8 Test Contract author + §11 데이터 마이그레이션 author. ArchitectPLAgent 산하 deputy. 입력 = 6 deputy 산출물(Mapper / Refactor / SecurityArchitect / OperationalRiskArchitect / TestContractArchitect / DataMigrationArchitect) + Story §1-7. `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md` + Story §3/§7/§11 **직접 write** (CFP-26 Phase 0a + codeforge-design self-write 표). Clarification 재스폰 의뢰 권한 |
| **CodebaseMapperAgent** | as-is 변호 역할. 매 설계 레인 진입 시 Refactor·SecurityArchitect·OperationalRiskArchitect·TestContractArchitect·DataMigrationArchitect와 병렬 재스폰, base_sha/scope_paths frontmatter. 타 deputy 산출물 미수신 — 원 소스 직접 독해 |
| **DataMigrationArchitectAgent** | 데이터 무결성 advocate. 매 설계 레인 진입 시 Mapper·Refactor·SecurityArchitect·OperationalRiskArchitect·TestContractArchitect와 병렬 재스폰. trust boundary와 별개 영역 — schema 진화·rollback·integrity invariant·backfill 결정 산출 → chief author가 Change Plan §11 (§11.1-§11.5; DB 무관 시 §11.7 N/A — §11.6 Idempotency CONDITIONAL은 OpRiskArch consult) 에 통합 |
| **RefactorAgent** | to-be 혁신 역할. 타 deputy 산출물 미수신, 원 소스 직접 독해. "잠재 변호 논리 예상" 섹션으로 self-identify한 충돌 지점 제출 (chief author가 Mapper 실제 변호와 대조) |
| **SecurityArchitectAgent** | 설계 lane 보안 deputy (보안 boundary·auth·credential·crypto 전담; 운영 리스크는 OpRiskArch). 타 deputy 산출물 미수신, 원 소스 직접 독해. trust boundary·auth 모델·credential 흐름·암호학 결정에 대한 보안 설계 권고 산출 → chief author가 Change Plan §7 (보안 설계 섹션, §7.1-§7.3·§7.5-§7.6; 외부 입력 무관 시 §7.7 N/A) 에 통합 |
| **OperationalRiskArchitectAgent** | 설계 lane 운영 deputy (CFP-46 신설 — DR / cancel-on-disconnect / clock sync / rate limit / env isolation 전담). 타 deputy 산출물 미수신, 원 소스 직접 독해. 운영 리스크 결정 산출 → chief author가 Change Plan §7.4 (5 sub-items) 에 통합 + §11.6 Idempotency CONDITIONAL 에 DataMigrationArch와 consult |
| **QADeveloperAgent** | Change Plan §8 Test Contract 입력. 매핑표 반환 의무 |
| **`role: dev` 에이전트** (DeveloperAgent·DataEng·InfraEng·preset·overlay) | 계획서 변경 금지 — 결함 발견 시 즉시 DevPL→ArchitectPLAgent 에스컬레이션 |
| **DesignReviewPLAgent** (codeforge-review plugin) | lane=design packet 작성 (codeforge-review repo의 `templates/review-checklists/design.md` 인용 + scope_globs + category_enum + severity_overrides). Claude/Codex 통합 워커 병렬 스폰 후 종합. ADR 정합성 체크 P0 고정 |
| **CodeReviewPLAgent** | lane=code packet 작성. Claude/Codex 통합 워커 병렬 스폰 후 종합. DesignReviewPL과 공통 severity 규칙 (base 템플릿 SSOT) |
| **SecurityTestPLAgent** | (lanes.security_ai: true 시만) 1차 layer = Dependabot/CodeQL/Secret Scanning 결과 `gh api repos/*` 로 fetch → packet에 inline 첨부. 2차 layer = lane=security packet으로 Claude/Codex 통합 워커 병렬 스폰 후 종합. CI gate PASS 이후 진입 |
| **ClaudeReviewAgent / CodexReviewAgent** | lane-agnostic 워커 ([ADR-001](../docs/adr/ADR-001-review-agent-unification.md)). 호출 PL이 review packet으로 도메인(체크리스트·스코프·category enum·severity 자동 룰) 주입. packet 누락 시 ESCALATE 반환 — generic fallback 금지. 정규화 스키마 P0/P1/P2/P3 + lane 필드 반환. CodexReviewAgent는 codex-companion.mjs 실행 |
| *(DocsAgent — 부재, CFP-40 final delete. ζ arc 완료 후 각 lane plugin self-write 로 분산)* | — |

### 3.3 컨텍스트 주입 정책

- **Story file 경로 + 참조 섹션 번호**가 기본 — verbatim 복사 지양
- ADR **직접 제약**인 경우에만 프롬프트에 verbatim 포함
- 배경 참조 ADR은 Story file §3 링크로 충분
- 코드 경로는 Story file §4에 요약, 구체 내용은 `Read`/`Glob`/`Grep` 도구로 직접 접근

### 3.4 Cross-repo Epic 패턴 ([ADR-020](../docs/adr/ADR-020-cross-repo-epic-pattern.md) + Amendment 1 + 2)

mctrader 등 multi-repo consumer 의 cross-repo Epic 진행 시.

#### Epic 시작
1. consumer 가 Epic owner repo 결정 (doc-only hub repo 권장 — 예: mctrader-hub)
2. **Centralization mode 결정** ([ADR-020 Amendment 1](../docs/adr/ADR-020-cross-repo-epic-pattern.md) + Amendment 2 CFP-122):
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
5. Change Plan §3 에 `consumes: { <producer>: <SemVer> }` pin 의무

#### Epic 진행
- **Topological merge order**: dependency graph 따라 producer 먼저 → consumer 나중
- `hard_block` 위반 detected 시 Epic 차단 (PMOAgent enforce)
- `design_parallel` / `impl_parallel` = 동시 진행 허용
- **Joint-phase PR 허용** (ADR-020 Amendment 1 §결정 9): 단일 Story 가 1 phase 안에서 multi-repo joint PR 보유 가능 (예: foundation Story 의 data + engine 동시 변경). 모든 PR 가 동일 Story key reference + dependency graph topological merge.

#### Epic Rollback
producer merge 후 consumer break 시:
1. Producer revert PR open
2. 모든 affected consumer 의 contract pin downgrade PR
3. Producer fix → 새 minor SemVer release
4. Consumer pin upgrade

#### Epic close — `EPIC-RESULTS-<EPIC_KEY>.md` artifact 의무 (CFP-83)

Epic close PR (Phase N+1) 동반 작성:

- **위치**: [`docs/doc-locations.yaml`](doc-locations.yaml) `epic_results` row 참조 ([ADR-041](adr/ADR-041-doc-location-registry.md)) — Mode A/B/C → `<scope>/docs/retros/` / dogfood → `<internal-docs>/<plugin-folder>/retros/` (Amendment 1 — CFP-288)
- **Template**: [`templates/epic-results.md`](../templates/epic-results.md) — 14 섹션 의무 (§1 child Story summary / §2 Phase decomposition / §3 Blocking AC / §4 Calibration AC / §5 Demonstration AC / §6 Codex review aggregate / §7 자율 결정 요약 (Sonnet decider) / §8 Out-of-scope / §9 CI iteration 통계 + 사용자 stop trigger 횟수 / §10 PR gate evidence / §11 후속 candidate 우선순위 / §12 debut-audit metric / §13 통계 / §14 결론)
- **작성자**: PMOAgent self-write (codeforge-pmo lane plugin owner)
- **mctrader 사례**: `mctrader-hub/docs/retros/EPIC-RESULTS-MCT-*.md` (Amendment 1 — root → docs/retros/)
- **§9 stop trigger 횟수** = ADR-025 + Amendment 1 (CFP-73 / CFP-80) stop discipline metric. 합법 stop whitelist 5종 외 stop = `policy_violation` defect 추적.
- **§10 PR gate evidence** = 향후 audit 시 GitHub API 라벨 verify fall-back evidence (Issue #181 P1-5 partial 해소)

#### Cross-references
- [ADR-020](../docs/adr/ADR-020-cross-repo-epic-pattern.md) + Amendment 1 + 2 (cross-repo Epic 패턴 SSOT — Mode A / B / C + Joint-phase narrow form)
- [requirements-output-v1.1](../docs/inter-plugin-contracts/requirements-output-v1.md) (Story §1 epic_dependencies field schema)
- [`consumer-guide.md`](consumer-guide.md) §5.1 (consumer 측 mode 선택 안내 — Mode A/B 비교표)

### §3.4.1 Multi-repo Story Routing (CFP-342 / ADR-050)

`project.yaml`의 `codeforge.stories.repos[]` 블록이 선언된 consumer에서 Orchestrator가 Story 작업 대상 repo를 결정하는 절차. [ADR-050](../docs/adr/ADR-050-multi-repo-story-key-system.md) §결정 4 SSOT.

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
- [ADR-050](../docs/adr/ADR-020-cross-repo-epic-pattern.md) §결정 4 (Agent target repo 결정 priority SSOT)
- [ADR-020](../docs/adr/ADR-020-cross-repo-epic-pattern.md) Amendment 3 (본 시스템 = Mode B automation layer)
- [`consumer-guide.md`](consumer-guide.md) §3 (multi-repo story key 활성화 가이드)
- [`overlay/_overlay/project.yaml.example`](../overlay/_overlay/project.yaml.example) (codeforge.stories 블록 예시)

### §3.5 Worktree dispatch (CFP-136 / ADR-040)

매 lane spawn 시 Orchestrator 가 worktree 생성 후 sub-agent 에 cwd 주입. file 충돌 0 보장.

**Lifecycle**:

1. **lane spawn 직전**:
   ```bash
   bash templates/scripts/worktree-create.sh cfp-NNN/<lane> origin/main
   # → returns worktree path: $HOME/.claude/worktrees/<repo>/cfp-NNN-<lane>
   ```
   하위 sub-task (deputy / role:dev) 가 있으면 sub-worktree 추가:
   ```bash
   bash templates/scripts/worktree-create.sh cfp-NNN/<lane>/<sub> cfp-NNN/<lane>
   ```

2. **sub-agent spawn 시**: prompt 에 `Working dir: <worktree-path>` 명시. sub-agent 가 cd 해서 작업.

3. **sub-agent return 후**: Orchestrator 또는 sub-agent 가 자기 sub-branch 에 commit. Sequential merge:
   ```bash
   bash templates/scripts/worktree-merge.sh cfp-NNN/<lane> cfp-NNN/<lane>/<sub1> cfp-NNN/<lane>/<sub2>
   ```

4. **lane 완료 후**: parent (story root) branch 으로 merge:
   ```bash
   bash templates/scripts/worktree-merge.sh cfp-NNN cfp-NNN/<lane>
   ```

5. **Story 완료 후**: 모든 sub-worktree prune:
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
- Orchestrator 가 conflict 받으면 chief author / 충돌 deputy sub-agent 재 spawn (cwd = parent worktree)
- 또는 PMOAgent escalation (CFP-139 GitOpsAgent 도입 후)

**SessionStart hook**:
- `bash templates/scripts/check-worktree-stale.sh` 자동 호출
- 7일 이상 + origin 부재 worktree 자동 prune

**Cross-platform**:
- Windows: `${HOME}\.claude\worktrees\<repo>\<branch-flat>` (PowerShell or Bash via Git for Windows)
- macOS / Linux: `~/.claude/worktrees/<repo>/<branch-flat>`
- Path 변환은 `worktree-path-util.sh` 함수 (`is_windows`, `to_posix_path`).

**의존성**:
- ADR-024 amendment 1 (hierarchical branch convention)
- ADR-040 (worktree convention SSOT)
- CFP-137 (agent teams 적극 도입) — 본 §3.5 의 use case full
- CFP-139 (GitOpsAgent) — Orchestrator 의 worktree management 책임을 GitOpsAgent 로 이관 (Wave 3)

### §3.6 TeamCreate / TeamDelete protocol (CFP-137 / [ADR-044](../docs/adr/ADR-044-phase-scoped-sequential-team.md))

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

### §3.10 Codex Proactive Check (CFP-354 / [ADR-052](../docs/adr/ADR-052-codex-proactive-check-touchpoints.md))

Orchestrator가 6개 touchpoint에서 `codex:codex-rescue` subagent를 **proactive check** 용도로 자동 dispatch. 기존 `codex:rescue`(사후 대응 — stuck 시) 채널과 분리.

**Dispatch 패턴**:

```text
Agent(subagent_type="codex:codex-rescue", prompt=<ProactiveCheckPacket>)
```

**ProactiveCheckPacket 스키마**:

```yaml
touchpoint: <1|2|3|4|5|6>
purpose: <한 줄 목적>
context:
  lane: <requirements|design|develop|orchestrator>
  story_key: <CFP-NNN>
  artifacts: <첨부 산출물>
task: <Codex에게 요청할 구체적 작업>
```

**결과 처리**:

| recommendation | findings | 처리 |
|---|---|---|
| PROCEED | — | 그대로 다음 단계 |
| ADDRESS_FIRST | P0 포함 | 해당 agent findings 반영 후 재진행 (blocking) |
| ADDRESS_FIRST | P1-only | Orchestrator 판단으로 skip 가능 → story §10 기록 |
| 판정 불일치 (#5 전용) | — | 사용자 에스컬레이션 |

#### §3.10.1 Pre-question Review

| 항목 | 내용 |
|---|---|
| 트리거 | `AskUserQuestion` 호출 직전 (항상, 전 레인) |
| artifacts | 질문 초안 + 옵션 목록 |
| task | "아래 질문 초안을 검토해 더 명확한 표현과 더 풍부한 옵션을 제안하라. 편향·누락·모호성 포착" |
| 출력 적용 | Codex 제안으로 질문/옵션 교체 후 `AskUserQuestion` 호출 |

#### §3.10.2 Design Synthesis Check

| 항목 | 내용 |
|---|---|
| 트리거 | ArchitectAgent Change Plan §3 초안 완료 → ArchitectPLAgent 전달 직전 (항상) |
| artifacts | §3 Change Plan 초안 + 6 deputy 산출물 요약 |
| task | "6 deputy 산출물이 §3에 균형 있게 반영됐는지 검증. 모순·누락·순환 논리 포착" |
| 출력 적용 | ADDRESS_FIRST 시 ArchitectAgent §3 수정 후 재전달 |

#### §3.10.3 Development Rescue

| 항목 | 내용 |
|---|---|
| 트리거 | DeveloperPLAgent FIX 2+ 반복 동일 이슈 감지 시 |
| artifacts | 구현 블로커 설명 + 관련 코드/로그 |
| task | "구현 블로커를 독립적으로 진단하고 root cause 및 해결 경로를 제시" |
| 출력 적용 | DeveloperPLAgent 진단 결과 적용 |

#### §3.10.4 Requirements Output Review

| 항목 | 내용 |
|---|---|
| 트리거 | RequirementsPLAgent §1-§6 통합 완료 → `phase:설계` 진입 직전 (항상) |
| artifacts | Story §1-§6 전체 내용 |
| task | "§1-§6 요구사항 완전성 검증. 테스트 불가능한 AC, 누락 엣지케이스, 모호한 표현, 상충 요구사항 포착" |
| 출력 적용 | ADDRESS_FIRST 시 RequirementsPLAgent §5-§6 보완 후 재검증 |

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

---

## 3B. Preflight 체크 (lane 진입 직전)

**doc-only fast-path 분기 (ADR-054)**: Story 분류 판정 직후, Orchestrator가 §결정 1 분류 표 적용. `doc-only fast-path` 해당 시: 설계 lane → 경량 설계리뷰 → 단일 PR close (구현 lane spawn 금지). `full-lane` 해당 시: 기존 5-lane 전체. 모호 시 full-lane 강제. 판정 표 SSOT: [ADR-054](../docs/adr/ADR-054-doc-only-story-fast-path.md).

Orchestrator가 **각 레인 진입 직전에 의무 수행**. 3개 체크 중 하나라도 FAIL이면 **block + report**: 에이전트 스폰 없이 사용자에게 실패 사유 반환.

### 3B.1 3개 체크 항목

| # | 체크 | PASS 조건 |
|---|------|-----------|
| 1 | **phase 라벨 정합성** | Story Issue `phase:*` 라벨이 진입할 레인과 일치 (예: 설계 레인 진입 시 `phase:설계`) |
| 2 | **Story file 선행 섹션 채움** | 진입할 레인이 요구하는 이전 섹션이 존재 (예: 설계 진입 시 §1-6, 설계 리뷰 진입 시 §7, 구현 진입 시 §7 + §8 Test Contract) |
| 3 | **외부 의존성 가용** | Codex 리뷰/Analyst 레인 진입 시 `codex --version` 성공 확인. GitHub MCP `mcp__github__issue_read` ping 성공 |

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

### 3B.3 적용 레인별 세부

- **요구사항**: (1) `phase:요구사항` / (2) §1 사용자 원문 존재 + **공통 입력 패키지 준비** (관련 ADR 목록 §3 선제 fetch via `Glob(docs/adr/ADR-*.md)`, 관련 코드 경로 §4 식별, Project Config Packet slice 확보) / (3) `codex` CLI 가용 + GitHub MCP 가용 (DomainAgent·Researcher 호출 포함)
- **설계**: (1) `phase:설계` / (2) §1-6 모두 채움 + "사용자 확인 필요" 해소 + **공통 입력 패키지 준비** (변경 대상 코드 경로 확정, 관련 ADR verbatim fetch, Change Plan 초안 메모 준비) / (3) GitHub MCP 가용
- **설계 리뷰**: (1) `phase:설계-리뷰` / (2) §7 채움 + `docs/change-plans/<slug>.md` 존재 + §7 보안 설계 섹션 작성 여부 (또는 §7.6 N/A 사유 명시 여부) / (3) Codex 플러그인 가용
- **구현**: (1) `phase:구현` / (2) §7 완료 + Change Plan §8 Test Contract 존재 (§8.3 `N/A` 허용) + Phase 1 PR merged / (3) 필요 Dev 전원 스폰 가능
- **구현 리뷰**: (1) `phase:구현-리뷰` / (2) §8 Impl Manifest 기록 + ArchitectPLAgent 매핑표 감사 PASS / (3) Codex 플러그인 가용
- **구현 테스트**: (1) `phase:구현-테스트` / (2) §9.2 구현 리뷰 PASS 기록 / (3) CI (`gh pr checks`) 접근 가능 (ADR-048 CI gate)
- **보안 테스트**: (1) `phase:보안-테스트` / (2) §9.3 CI gate PASS 기록 / (3) Codex 플러그인 가용 + 의존성 매니페스트 존재 + Dependabot/CodeQL 결과 접근 가능 (lanes.security_ai: true 시만)

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
```

코멘트 prefix는 `[<phase>] Orchestrator: Preflight {PASS|FAIL}`. 기록 누락 시 PMO 완료 회고에서 P1 결함으로 감사 보고됨.

### 3B.5 plugin-meta-na PR pre-push 자가 검증 (Codex audit closure sprint 회고 §5 운영 개선 #1)

ADR-005 plugin-meta-na 패턴(§8/§9 lane 게이트 면제)으로 진행되는 plugin 자기 적용 PR은 일반 lane 리뷰를 우회하므로 **author가 push 직전 로컬 invariant-check 자가 검증 의무**.

**의무 절차** (push 직전):
1. 변경 대상 SSOT 식별 (CLAUDE.md / `agents/**` / `templates/**` / `.claude-plugin/plugin.json` / `CHANGELOG.md` / `docs/migration-guide.md` 등)
2. 영향 받는 invariant-check Step (3 agent count / 6 category enum / 7 migration-guide BREAKING parity / 8 severity_overrides count)을 [`.github/workflows/invariant-check.yml`](../.github/workflows/invariant-check.yml)에서 직접 grep으로 확인
3. 로컬 dry-run: 해당 step의 핵심 grep·python 로직 1-2줄을 직접 실행해 본 PR 변경 후 PASS 여부 확인 (예: `grep -c "data-migration" templates/change-plan.md docs/inter-plugin-contracts/review-verdict-v1.md` — review subsystem 자체 검증은 codeforge-review repo에서)
4. drift 발견 시 push 전 fix commit 추가, drift 부재 시 push 진행

**근거**: [`docs/retros/2026-04-28-codex-audit-closure-sprint.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/retros/2026-04-28-codex-audit-closure-sprint.md) §5. CFP-21 (migration-guide BREAKING regex 미일치) / CFP-22 (DesignReviewPL severity_overrides P1 3건 누락) 모두 push 후 CI fail로 발견 — plan 작성 단계에서 잡혔어야.

**적용 범위**: plugin-meta-na PR만 (production code Story는 일반 lane Preflight + DesignReview/CodeReview/SecurityTest가 자동 검증). consumer overlay 적용 PR은 본 절차 비대상.

---

## 4. 병렬 스폰 판단

### 4.1 병렬 가능 조건 (AND)

1. **경로 분리**: 쓰기 대상 파일 경로가 겹치지 않음 (path-scoped 권한으로 보장)
2. **입력 독립**: 한쪽 산출물이 다른 쪽 입력이 아님
3. **완료 대기 가능**: 모든 병렬 에이전트 완료 후 종합 판단 가능

### 4.2 표준 병렬 패턴

| 패턴 | 구성 | 조건 충족 |
|------|------|----------|
| **요구사항 레인** | DomainAgent ∥ Analyst ∥ Researcher | 셋 모두 공통 입력만 수신, 타 산출물 미참조 → 입력 독립. PL이 통합 단계에서 dedup·상충 조정 |
| **설계 레인** | CodebaseMapper ∥ Refactor ∥ SecurityArchitect ∥ TestContractArch ∥ DataMigrationArchitect | 다섯 다 원 소스(코드·ADR·Change Plan 초안) 직접 독해, 타 산출물 미참조 → 입력 독립. ArchitectAgent (chief author)가 교차 검토 → ArchitectPLAgent 검수 |
| **설계 리뷰** | ClaudeReviewAgent ∥ CodexReviewAgent (lane=design packet) | 읽기 전용, 정규화 스키마 동일 |
| **구현 리뷰** | ClaudeReviewAgent ∥ CodexReviewAgent (lane=code packet) | 동일 |
| **보안 테스트** | ClaudeReviewAgent ∥ CodexReviewAgent (lane=security packet) | 동일. 워커는 lane-agnostic, PL이 packet으로 도메인 분기 |
| **구현** | DevPL(`role: dev` roster 병렬) + QADev(tests/**) | 쓰기 경로 분리 — roster 전체 의존성 없는 한 병렬 |

### 4.3 병렬 일부 실패 시

- **모두 완료 대기**가 원칙 — iteration 낭비 방지
- 예외: ClaudeReview가 [P0]를 즉시 내면 Codex 대기 없이 FIX 진입 가능 — 단 Codex 완료 후 결과 병합해 Story file §9에 기록

### 4.4 Clarification 재스폰 절차 (요구사항·설계 레인 공통)

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

mctrader debut audit Issue [#181](https://github.com/mclayer/plugin-codeforge/issues/181) P2-8 finding: §10 FIX Ledger 사용이 sparse — early Stories (MCT-1/2/3) 만, 최근 Stories (MCT-25 등) §10 부재. mctrader 실제 패턴 = `EPIC-RESULTS-<KEY>.md` §9 CI iteration 통계 가 §10 alternate 역할 (CI failure 별 root cause 표).

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

### 6.4 §10 관리 세부

- **Orchestrator가 단독 갱신** (CFP-32 ζ arc F1부터 — fix-event-v1 monopoly). append-only, 행 삭제·수정 금지
- Schema SSOT: [`docs/inter-plugin-contracts/fix-event-v1.md`](../docs/inter-plugin-contracts/fix-event-v1.md) — row 필드 + append 규칙 + RESET 시맨틱스
- Stale-read 방지: Orchestrator가 Edit 직전 `git pull --rebase` 또는 file mtime 비교 후 append. 충돌 시 fail-fast + 사용자 ESCALATE (자동 재시도 금지 — append-only ledger 손상 위험)
- Lane plugin은 FIX event를 Orchestrator에 verdict로 보고 (status=FIX 또는 test FAIL). lane plugin이 §10 직접 Edit 금지 — CFP-34 deliverable `story-section-write-guard.yml`이 enforce
- §10 조회 실패(파일 부재 등) → ArchitectPLAgent 판정 정지 → 사용자 판단 요청
- GitHub 라벨은 `fix-ledger-sync.yml` Action이 §10 commit 감지 시 자동 부착 — 단방향 mirror (§10 → label/comment). 대시보드 search syntax 필터용

### 6.5 원인 판정 decision table

[CLAUDE.md](../CLAUDE.md) "원인 판정 decision table" 섹션이 SSOT — 본 playbook은 표를 inline 복제하지 않는다 (drift 방지). Orchestrator는 FIX 트리거 시 CLAUDE.md 표를 직접 참조해 DeveloperPL/ArchitectPLAgent 전달용 evidence pack을 구성.

**ArchitectPLAgent 최종 판정 + evidence pack(Change Plan 버전 + 리뷰 findings + 테스트 로그) 첨부 의무**.

### 6.6 Parallel diagnosis (R4, [CFP-19 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

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

### 6.7 Mechanical fast-path (R11, [CFP-19 spec](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-04-27-cfp-19-orchestration-parallelization.md))

ReviewPL verdict packet의 `mechanical_category` 필드 (typo / broken-link / minor-naming / comment-only / none — SSOT codeforge-review repo의 `templates/review-pl-base.md` §3 R11 절) + severity 조합으로 fast-path 자격 판정:

**자격 조건**: `mechanical_category != none` AND (severity = P2 OR (severity = P1 AND 영향 파일 수 = 1))

**자격 충족 시 절차**:
1. Orchestrator가 §6.6 parallel diagnosis 건너뛰고 DeveloperPL 직접 spawn (fix-only 모드)
2. DeveloperPL이 fix commit
3. **same-iteration internal verify** — 다음 review iteration이 동일 finding 검출 안 하면 PASS, 검출 시 Iter row append (정상 cycle 회복)
4. §10 ledger 신규 row 안 매김 (fast-path는 카운터 증가 안 함)

**자격 미충족 또는 분류 잘못**: 다음 review iteration이 P0/P1 검출 → 정상 §6.6 cycle.

**제약**: 보안 lane의 injection / credential / CVE / trust-boundary 카테고리는 항상 `mechanical_category = none`이라 fast-path 자격 없음 (codeforge-review repo의 `templates/review-pl-base.md` §3 R11 SSOT).

### 6.8 Spec amendment loop (CFP-87)

mctrader debut audit Issue [#181](https://github.com/mclayer/plugin-codeforge/issues/181) P1-7 finding (Opus 자체 발견): mctrader-hub PR [#72](https://github.com/mclayer/mctrader-hub/pull/72) (`[MCT-50/51] Spec amendments — Codex push-back 6건`) — Phase 3 implementation 진행 중 Codex review 가 발견한 push-back 6건 → spec doc 수정 PR (Story file `MCT-50.md` + `MCT-51.md` amendment) 으로 캡처 후 implementation 재개. 매우 가치 있는 패턴이나 codeforge SSOT 미정의 — 본 §6.8 codify.

#### 6.8.1 Trigger

다음 중 하나 발생 시 Spec amendment loop 진입 (FIX 루프 §6.1-§6.7 와 별도):

- **Codex push-back during implementation**: Phase N implementation (Phase 2~N PR 작업) 중 Codex review 또는 자율 검토 시 spec gap 발견 (Story file §1-§7 unspecified / inconsistent)
- **사용자 mid-implementation requirement clarification**: 구현 중 사용자가 새 AC 제시 또는 기존 §1 의미 재해석
- **Spec drift 발견**: implementation 진행 중 §7 설계 결정과 코드 사이 drift 발견 (코드 측 fix 만으로 해결 안 되는 경우)

§6.1-§6.7 FIX 루프 와 구분:
- FIX 루프 = review verdict FAIL → 코드 / 설계 변경
- Spec amendment = review verdict 무관 → spec doc (Story file / Change Plan / ADR) 변경

#### 6.8.2 Output

`[<KEY>] Spec amendment — <reason>` PR (1+ Story file edit, doc-only):

- Story file §1-§7 / §11 / §13 amendment 시 PR title prefix `[<KEY>] Spec amendment`
- amendment 동반 의무:
  - Story file frontmatter `status:` field 유지 (현재 phase 변경 없음 — amendment 는 phase progression 아님)
  - Story file §10 FIX Ledger row 추가 = N/A (FIX 가 아니므로)
  - Story file §12 Sonnet Decision Log row 추가 (substantive choice 발생 시)
  - PR labels = `audit:spec-amendment` + `phase:<현재 phase>` (CFP-86 label registry 확장 candidate)

#### 6.8.3 Limit

per Story max **2 spec amendment PR**. 3+ amendment 발생 시 = 설계 결함 신호 → 설계 lane 재실행 trigger (§6.5 decision table 의 "설계 원인 판정" 적용).

#### 6.8.4 Audit trail

- Story file §11 = amendment PR list (link + reason summary)
- EPIC-RESULTS-<EPIC_KEY>.md §6 Codex review aggregate = amendment 발생 row 명시 (PR # + reason)

#### 6.8.5 mctrader 사례 (CFP-87 source)

| Story | Amendment PR | Reason | Trigger |
|---|---|---|---|
| MCT-50 / MCT-51 | mctrader-hub#72 | Codex push-back 6건 (Signal handler ownership / RunStatus minimal v1 / HTTP edge case / "11 tables" 재정의 / MarketDataFreshnessEvent deferred / ClosedBarEvent.source_hash) | Phase 3 implementation 중 Codex review |

#### 6.8.6 §6.8 ↔ §6.5 (원인 판정 decision table) cross-ref

§6.8 spec amendment 가 결과적으로 spec drift 가 코드 / 설계 사이 발생 시 → §6.5 decision table 의 "설계 원인 판정" 적용 → 설계 lane 재실행. 즉 spec amendment → FIX 루프 conversion path 존재.

---

## 7. 세션 재개(resume) 복원 절차

### 7.1 활성 Story 조회

```
mcp__github__list_issues(state='open', labels=['type:story'])
```

또는 `Bash(gh issue list --label "type:story" --state open --json number,title,labels)`.

- 0건: 신규 세션
- 1건: 자동 resume — §7.3 매핑
- 2건 이상: 사용자에게 확인

### 7.2 Story file 최신 섹션 판독

`Read(docs/stories/<KEY>.md)` → 어느 섹션까지 채워졌는지 확인해 재진입 지점 보정.

### 7.3 phase label ↔ 재진입 에이전트 매핑

| phase 라벨 | Story file 섹션 | 재진입 에이전트 |
|-----------|-----|-----------------|
| phase:요구사항 | §1만 채움 | RequirementsPLAgent 재스폰 → Domain·Analyst·Researcher **병렬 재스폰** (Never-skippable 3종 전원) |
| phase:요구사항 | §2·§5·§6 **일부만** 채움 (부분 완료 resume) | 비어있는 섹션의 에이전트만 **선택 재스폰** + 이미 채워진 섹션은 PL 통합 단계에서 재활용. §9.0에 "Resume 부분 재스폰" 행 append |
| phase:요구사항 | §2·§5·§6 모두 채움 | RequirementsPLAgent 통합 명세서 재확정 단계 재진입 ("사용자 확인 필요" 해소 여부 체크). 일부 관점 재보강 필요 시 clarification 재스폰 |
| phase:설계 | §7 + §11 초안만 | ArchitectPLAgent — Mapper·Refactor·SecurityArchitect·TestContractArchitect·DataMigrationArchitect **병렬 재스폰** + ArchitectAgent (chief author) 통합 의뢰 (이전 산출물 세션 외 유지 불가, §7/§11 Change Plan 초안만 복원됨) |
| phase:설계 | §7/§11에 6 deputy 일부만 반영 (부분 완료 resume) | 미반영 쪽 deputy만 **선택 재스폰** + 반영된 쪽은 재활용. §9.0에 "Resume 부분 재스폰" 행 append |
| phase:설계 | §7 완료 | ArchitectAgent 가 Change Plan 저장 완료 보고 + Story §3/§7/§11 self-write 완료 확인 → 설계 리뷰 진입 |
| phase:설계-리뷰 | §9.1 블록 없음 | DesignReviewPLAgent 재스폰 (Claude/Codex 병렬) |
| phase:설계-리뷰 | §9.1 블록 FIX | ArchitectPLAgent → ArchitectAgent (chief author) 재스폰, Change Plan 갱신 |
| phase:구현 | §7 완료, §8 비어있음 | Phase 2 PR open 여부 확인. 없으면 DeveloperPL 직접 mcp__github__create_pull_request 호출. 있으면 DevPL + QADev 병렬 스폰 |
| phase:구현 | §8 일부 | 마지막 구현 에이전트 (§8에서 확인) 재스폰 |
| phase:구현-리뷰 | §9.2 블록 없음 | CodeReviewPLAgent 재스폰 |
| phase:구현-리뷰 | §9.2 블록 FIX | DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 |
| phase:구현-테스트 | §9.3 블록 없음 | `gh pr checks <PR_NUMBER> --watch` 재실행 (CI gate 재확인) |
| phase:구현-테스트 | §9.3 블록 FAIL | DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 |
| phase:보안-테스트 | §9.4 블록 없음 | SecurityTestPLAgent 재스폰 (Claude/Codex 병렬, lanes.security_ai: true 시만) |
| phase:보안-테스트 | §9.4 블록 FIX | DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정 |

### 7.4 FIX 카운터 복원 (세션 개시/압축 재개 시 의무)

세션 개시 시점 또는 컨텍스트 압축 후 재개 시 Orchestrator는 **반드시** 아래를 수행:

1. 활성 Story file `Read(docs/stories/<KEY>.md)` 호출
2. §10 "FIX Ledger" 파싱 → 마지막 `RESET 구현-리뷰` 이후 행으로 각 레인 카운터 산출 (설계-리뷰 / 구현-리뷰 / 구현-테스트 / 보안-테스트 4개)
3. 파일 read 실패 시 **사용자 ESCALATE** (카운터 불명 상태 진행 금지)

GitHub 라벨 count는 감사 이력으로 보존되나 복원 source of truth 아님 (§10 기준). 이 절차 없이 ArchitectPLAgent 판정 진행 금지.

### 7.5 사용자 통보

```
🔄 세션 재개

[복원된 상태]
- Story: <KEY> — {제목}
- phase: {현재 라벨}
- 재진입 지점: {에이전트 이름} 스폰
- FIX 카운터: 설계 리뷰 {n}/3, 구현 리뷰 {m}/3, 구현 테스트 {k}, 보안 테스트 {s}
- Story file 마지막 갱신 섹션: §{X}

[이어서 진행합니다. 문제 있으면 알려주세요.]
```

### 7.6 Fallback (자동 판정 실패)

- 활성 Story 2건 이상 → 사용자에게 어느 Story resume 질문
- Story file 접근 불가 → §9.4
- phase 라벨과 Story file 섹션 불일치 → 사용자 판단 요청

---

## 8. 토큰 예산 모니터링 + 세션 회고

### 8.1 추적 지표

- 레인별 input/output 토큰 (요구사항 / 설계 / 설계 리뷰 / 구현 / 구현 리뷰 / 구현 테스트 / 보안 테스트)
- 에이전트별 누적 토큰 (0 core in wrapper + 23 distributed across 6 lane plugins + preset/overlay-only `role: dev` 에이전트)
- FIX iteration별 추가 토큰
- **ArchitectPLAgent + ArchitectAgent (chief author) stateless 재스폰 overhead**: PL 재스폰 당 ~5k + chief author 재스폰 당 ~10k (Story file §1-8 fetch). FIX 3회 가정 시 ~45k

### 8.2 레인별 사전 예산·중단 임계

두 지표로 추적:
- **Total**: 레인 전체 누적 (병렬·순차 합산, 에이전트별 input+output)
- **Peak concurrent**: 같은 시점에 동시 실행되는 에이전트의 현재 context 합계 — 병렬 모델에서 실제 비용 지표. v0.7.0 병렬화로 요구사항·설계 peak이 크게 증가

| 경로 | Total 사전 예산 | Total 중단 임계 | Peak concurrent (동시 컨텍스트 합) | 비고 |
|------|-----------------|-----------------|------------------------------------|------|
| 요구사항 | 80k | 150k | ~60k (Domain ∥ Analyst ∥ Researcher, 각 ~20k 풀 컨텍스트) | v0.6 순차 대비 total +30k / peak 3× |
| 설계 | 225k | 345k | ~150k (Mapper ∥ Refactor ∥ SecurityArchitect ∥ OperationalRiskArchitect ∥ TestContractArch ∥ DataMigrationArchitect, 각 ~25k) + ArchitectAgent (chief author) 10k + ArchitectPLAgent 5k | OperationalRiskArchitect deputy 추가로 total +25k / peak +25k (CFP-46 / ADR-014) |
| 설계 리뷰 | 50k | 120k | ~40k (Claude ∥ Codex) | 기존 유지 |
| 구현 | 200k | 400k | roster size × ~20k + QADev 20k | 기존 유지 (`role: dev` 병렬 수에 비례) |
| 구현 리뷰 | 60k | 150k | ~40k (Claude ∥ Codex) | 기존 유지 |
| 구현 테스트 | 0k (CI native) | — | Orchestrator inline `gh pr checks` | ADR-048 CI gate — 토큰 비용 없음 |
| 보안 테스트 | 60k | 150k | ~40k (Claude ∥ Codex 보안 focus) | 기존 유지 (1차 layer는 GitHub native, 토큰 비용 없음) |
| Clarification 재스폰 (per instance) | 10-20k 추가 | — | 단일 에이전트 재실행 | 2회 한도 (§4.4), 초과 시 ESCALATE |
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
| DataMigrationArchitectAgent | |
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

### 9.1 에이전트 스폰 실패

| 증상 | 원인 | 대응 |
|------|------|------|
| Agent 툴 호출 실패 | subagent_type 철자 오류 | `agents/` 목록과 대조 후 재시도 |
| 권한 거부 | path-scoped 권한 불일치 | 대상 에이전트 md frontmatter 확인, 담당 에이전트 재선택 |
| 무한 스폰 | 서브에이전트가 Agent 툴 호출 시도 | 플랫폼 제약 위반 — 해당 에이전트 md에 "직접 스폰 불가" 명시 확인 |

### 9.2 GitHub MCP 연결 장애

GitHub Issue/PR 갱신·코멘트 기록·sub-issue 생성 불가 시:

1. 세션 내 임시 로그로 전환 — Orchestrator 메모리에 갱신 내용 누적
2. 사용자에게 "GitHub MCP 장애" 통보. 가능한 fallback: `gh issue ...` Bash CLI
3. 복구 후 각 lane plugin 재스폰으로 backlog 동기화 (lane plugin self-write 재실행)
4. **FIX 카운터 조회 불가 시** (docs file은 로컬 file이라 read는 보통 가능): 그래도 실패하면 ArchitectPLAgent 판정 정지 → 사용자 판단 요청

### 9.3 Codex CLI / 플러그인 미설치

- **CodexReviewAgent**: 미설치 시 3 리뷰 레인(설계 리뷰·구현 리뷰·보안 테스트) **모두 진입 불가** → 설치 안내 + 세션 중단
- **RequirementsAnalyst**: `codex` CLI 미설치 시 요구사항 레인 **진입 불가** → 동일
- `SKIPPED` 경로 허용 안 됨

### 9.4 Story file stale 감지

에이전트 보고에서 "Story file에 없는 컨텍스트" 또는 "현재 코드와 불일치" 감지 시:

1. Orchestrator 가 해당 lane plugin 재스폰 → 최신 상태로 Story file 갱신 (lane plugin self-write)
2. 갱신 완료 후 해당 에이전트 재스폰

### 9.5 CodebaseMapper 산출물 stale 감지

- Mapper는 **매 설계 레인 진입 시 재스폰** — 이전 Story 산출물 재사용 금지
- 리뷰·테스트에서 설계 레인 복귀 시에도 재스폰 (구현 레인에서 코드 변경 가능성)
- 재사용 감지 시 ArchitectAgent (chief author) 단독 설계 결정 금지 (§2 설계 공동작업자 부재 상태)

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
  "fetched_at": <ISO 8601>,
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

### 12.4 Packet vs path-only 선택

- **Packet 주입**: 설계/구현/리뷰 레인처럼 여러 섹션 깊이 참조 필요할 때 (§1-8 범위)
- **Path만 전달**: 단발성 조회, 섹션 캐시 미정의 부분
- **설계 lane packet recipient**: ArchitectPLAgent (Phase 2에서 ArchitectAgent (chief author) + 6 deputy(Mapper/Refactor/SecurityArchitect/OperationalRiskArchitect/TestContractArch/DataMigrationArchitect)에 forward — PL이 packet 분배 책임)

### 12.5 Project Config Packet (project.yaml 슬라이스)

Story file Context Packet과 병행해 **`.claude/_overlay/project.yaml`의 objective SSOT 상수**도 sub-agent 프롬프트에 주입. GitHub 호출하는 에이전트가 매번 `Read` 호출 없이 곧바로 활용.

#### 캐시 구조

```
project_config_cache = {
  "loaded_at": <ISO 8601>,                   # 세션 시작 시 1회 로드
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

---

## 13. PMOAgent 프로젝트 관리 (Cross-cutting)

PMOAgent는 단일 Story 레인 게이트 밖에서 cross-cutting 감사·회고·패턴 분석을 전담. 요구사항 해석은 RequirementsPLAgent 영역으로 분리됨.

### 13.1 스폰 타이밍 4종 (CFP-316 / ADR-047 — Version Delta Review 추가)

| 트리거 | 시점 | 입력 | 산출물 |
|--------|------|------|--------|
| **Epic 창설** | Orchestrator가 Epic 생성 직후, Story 분해 직전 | 사용자 원문·관련 ADR·기존 Epic 이력·코드 구조 | Story 분해 자문 (의존성·우선순위·**병렬/순차 판정**) — 상세 규칙 [PMOAgent.md §1](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/agents/PMOAgent.md) |
| **Story 완료** | CI gate PASS → (lanes.security_ai: true 시 보안 테스트 PASS →) Phase 2 PR merge 직후 | 해당 Story file §1-11 + FIX Ledger + GitHub Issue 코멘트 이력 + 토큰 사용량 | 회고 감사 보고 (Preflight 누락·§8/§8.5 매핑·FIX evidence 완성도·예산) |
| **사용자 요청** | `/pmo-audit` 혹은 명시 요청 | 최근 N Story (기본 5) file·Ledger·ADR 변경 이력 | Cross-Story 패턴 보고 + ADR 후보 발의 |
| **Version Delta Review** | Framework Delta Event 발생 후 5분 이내 (또는 사용자 수동 trigger `/pmo version-delta-review`) | Framework Delta Event 종류 + 진행 중 Story 목록 + 관련 ADR + consumer overlay 상태 | Migration Epic Issue (material drift 시) 또는 "no action" 보고서 → Story §11 기록 |

### 13.1a Version Delta Review 프로세스 (CFP-316 / ADR-047)

PMOAgent의 4번째 trigger — codeforge framework 진화(신규 deputy 추가, §section 변경, ADR 변경 등) 시 기존 진행 중 Stories/Change Plans의 구조 재편 필요 여부를 자동 평가한다.

**Framework Delta Event 4-Type 정의**:

| Type | 설명 | PMOAgent 반응 |
|------|------|---------------|
| **Type A — Version bump** | consumer 프로젝트의 codeforge version bump | patch: advisory review 보고서 / minor·major: Migration Epic 후보 평가 |
| **Type B — ADR 변경** | Story 구조/lane 동작에 영향을 주는 신규·실질적 ADR 변경 (inter-plugin contract schema MAJOR bump, GitHub workflow fixture 변경 등) | 영향 범위 평가 후 Migration Epic 여부 결정 |
| **Type C — Deputy 변경** | 신규 deputy 추가 또는 deputy mandate 변경 (새 필수 §section 발생) | 진행 중 Story에 새 §section 추가 Migration Story 생성 |
| **Type D — Bootstrap 변경** | ADR-027/ADR-032 enforcement 변경 | consumer-guide 업데이트 + bootstrap 재검증 Migration Story |

**Version Delta Review 프로세스 (4단계)**:

1. Framework Delta Event 종류 판별 (Type A/B/C/D)
2. 진행 중인 Stories/Change Plans의 §section 구조 점검 (영향 범위 평가)
3. Material drift 판별:
   - patch bump / advisory-only ADR: "no migration needed" 보고서 → Story §11 기록
   - minor/major bump 또는 신규 deputy 또는 §section 신설: Migration Epic 후보 평가
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
🔄 설계 — 진행 중 (6/6 deputies, chief author 통합 중)
   ├─ ✅ CodebaseMapperAgent
   ├─ ✅ RefactorAgent
   ├─ ✅ SecurityArchitectAgent
   ├─ ✅ OperationalRiskArchitectAgent
   ├─ ✅ TestContractArchitectAgent
   ├─ ✅ DataMigrationArchitectAgent
   └─ 🔄 ArchitectAgent (chief author) — Change Plan §3 author 중
⏸ 설계 리뷰
⏸ 구현
⏸ 구현 리뷰
⏸ 구현 테스트
⏸ 보안 테스트
```

- frontmatter 없이 plain markdown + yaml-style 메타 4줄
- Story 시작 시 모든 lane `⏸` init
- Story 완료 시 `_archive/<KEY>.md` 로 mv (PMO Cross-Story 분석 input 보존)

### 14.4 Status enum (ADR-041, 4 marker)

| 마커 | 의미 | TodoWrite native state | 사용 위치 |
|---|---|---|---|
| `⏳` | pending — 진행 예정 (모래시계) | `pending` | Lane row, agent sub-row |
| `🔄` | in_progress — 진행 중 | `in_progress` | Lane row, agent sub-row |
| `✅` | completed — PASS / N/A / 검출 성공 | `completed` | Lane row, agent sub-row |
| `❌` | 원인 작업 — 통과 못해 새 단계 추가의 cause | `in_progress` (content prefix `❌`) | Lane row only |

**검출 label 정규화**: review/test lane 의 terminal detection 이 FAIL 인 경우에도 TodoWrite content label 은 `FAIL detected` 를 쓰지 않고 `FIX-N detected` 로 정규화한다. RESET 이 필요한 경우에도 `FIX-N detected (cause: <원인 lane>, RESET-N)` 형식. `FAIL` 은 review/test 판정 흐름의 terminal outcome vocabulary 로만 남고, TodoWrite row label 은 `FIX-N detected` 가 canonical.

**N/A**: ✅ marker + content prefix `N/A · <사유>`. PASS 와 시각 차별 (텍스트 차이).
**RESET**: ✅ marker (검출 lane) + 새 lane row append (`(재진입 RESET-N)` suffix).
**blocked / waiting**: 4-marker vocabulary 범위 밖. 대기 상태는 ⏳ pending 으로 표현, 진행 중 차단성 작업은 🔄 in_progress row 의 content 1줄 설명으로 표현.

기존 8 marker (⏸ ⏳-blocked 🔄 ✅ ❌ FIX-N ❌ FIX-N(fast-path) ⊘ 🔁) 폐기. ⏳ semantic 변경 (blocked → pending). file / TodoWrite 두 channel 동일 어휘.

활성 lane row 라인에 inline qualifier (예: `🔄 설계` content 미동반, sub-row 가 detail 표현. PASS 시 `✅ 설계 - PASS · Change Plan v1 + ADR-NNN`).

### 14.5 트리거 SSOT

**Verbosity policy (CFP-114 / ADR-029)** — `terminal narration` 컬럼은 `progress_narration_verbosity` 값 기반 적용:
- `full` (default, ADR-029 §결정 1+4) — 모든 ✅ 표기 항목 narrate (sub-step 포함)
- `lane_only` — lane-level event 만 narrate (CFP-20 기존 동작, sub-step 표기는 file-only 로 fallback)

| 이벤트 | 영향 라인 | 갱신 동작 | terminal narration | TodoWrite 갱신 (ADR-041) | full/lane_only |
|---|---|---|---|---|---|
| Story 개시 | 전체 | file create, 7 lane `⏸` | ✅ | 7 lane row ⏳ seed | both |
| Lane 진입 | top | `⏸` → `🔄 진행 중`, current_lane 갱신 | ✅ | lane row ⏳ → 🔄 + agent sub-row 펼침 | both |
| Deputy spawn | active sub-tree | `🔄 <Deputy>` 추가, qualifier 갱신 | ✅ | agent sub-row 추가 (status=in_progress) | full only |
| Deputy return | active sub-tree | `🔄` → `✅`, qualifier 갱신 | ✅ | agent sub-row status=completed | full only |
| 병렬 dispatch (R3·R4·R7·R9) | active sub-tree | 두 deputy 동시 `🔄` 라인 추가 | ✅ | agent sub-row 다수 동시 in_progress (multi-row deviation) | full only |
| CI gate 시작 | 구현 테스트 | inline qualifier `(gh pr checks 🔄)` | ✅ | CI gate sub-row inline qualifier | both |
| CI gate 완료 | 구현 테스트 | qualifier 갱신 | ✅ | CI gate sub-row 갱신 | full only |
| R11 fast-path | 해당 lane | `❌ FIX-N (fast-path)` 마커 | ✅ | lane row → ✅ collapsed, content "PASS · R11 mechanical fast-path" | both |
| Lane PASS | top | `🔄` → `✅ — <S3 snippet>`, sub-tree 접음 | ✅ | lane row → ✅ + S3 snippet, agent sub-row 제거 | both |
| Lane FIX | top | `🔄` → `❌ FIX-N — <evidence 1줄>`, fix_cycle 갱신 | ✅ | 검출 lane → ✅ + content "FIX-N detected (cause: X)" + 원인 lane → ❌ flip + 재진입 lane row append | both |
| Lane 재진입 (FIX 후) | top | `❌ FIX-N` → `🔄 진행 중 (FIX-N)` | ✅ | 재진입 lane row → 🔄 + agent sub-row 펼침 | both |
| RESET 마커 | 구현 리뷰 | `✅` → `🔁 RESET-N` | ✅ | 재진입 lane row append (suffix "(재진입 RESET-N)") | both |
| Lane N/A (plugin meta) | top | `⏸` → `⊘ N/A — <사유>` | ✅ | lane row → ✅ + content "N/A · <사유>" | both |
| 사용자 "진행상황 보여줘" | — | file 변경 없이 현재 §0 전체 emit | ✅ (deputy 포함 full) | TodoWrite 도 emit (file + TodoWrite 동시) | both |
| Story 완료 | 전체 | 모두 `✅`, archive mv, index 갱신 | ✅ | 7 lane row 모두 ✅, 최종 state | both |

R10 prefetch (security 1차 layer cache) 같은 사용자 무관 메타 이벤트는 **의도적 skip** (verbosity 무관).

**TodoWrite best-effort 원칙 (ADR-041)**: lane event 로 trigger 되는 TodoWrite 갱신은 best-effort / non-blocking 이다. TodoWrite update 가 실패하거나 skipped 되어도 lane 의 primary work 를 block 하지 않는다. lane 은 계속 진행하고, TodoWrite discrepancy 는 error 가 아니라 warning 으로 surface 한다. 사용자 confirmation / polling / acknowledgment wait 도입 없음 (ADR-029 stop discipline 정책 무영향).

**Single-Story collision rule (ADR-041)**: single-Story 모드에서도 두 concurrent lane spawn 이 같은 Story 의 TodoWrite 를 동시에 write 할 수 있다. collision 발생 시:
1. canonical §14 Lane Evidence table state 에서 todo list 전체를 재구성
2. TodoWrite hard-reset 수행: 기존 todo list 를 부분 수정하지 않고 full rewrite
3. rewrite 후 active lane / agent sub-row 는 canonical state 에 남아 있는 evidence 만 반영
4. hard-reset 결과와 collision warning 을 terminal narration / wrapper warning 으로 surface
5. lane primary work 는 중단하지 않고 계속 진행

incremental patch 금지 — collision 의심 시 항상 full rewrite.

**Narration format (ADR-029 §결정 2)** — `[<lane-한국어>] <event>: <detail>` 1 sentence stderr line. 예시:

```
[설계] Deputy spawn 6/6 병렬 (CodebaseMapper / Refactor / SecurityArch / OpRiskArch / TestContractArch / DataMigrationArch)
[설계] DataMigrationArchitectAgent return — §11 Migration 전략 + Rollback 경로 author 완료
[설계 리뷰] R7 병렬 dispatch — DesignReviewPL ∥ DeveloperPL Phase 2 PR 준비
[구현 테스트] CI gate 실행 중 — `gh pr checks` watching (timeout 30분)
```

세부 rule: 한국어 lane 이름, 멀티라인 금지, stderr only (file-write 와 격리). Stop discipline 정책은 ADR-022 §결정 2 + ADR-025 SSOT (본 §14.5 는 visibility 만 다룸).

### 14.6 S3 snippet 7-lane 표 (Lane PASS 시 1줄)

| Lane | snippet 템플릿 | source |
|---|---|---|
| 요구사항 | `통합 명세 §3-6 + 도메인 공백 <N>건` | RequirementsPL 통합 + DomainAgent |
| 설계 | `Change Plan v<N> + ADR-<NNN> <신규\|변경> (deputy <M>인)` | ArchitectPL + ADR file mtime |
| 설계 리뷰 | `PASS — Claude/Codex 종합, 코멘트 #<id>` | DesignReviewPL packet |
| 구현 | `Phase 2 PR #<num> · <commit>건 · §8.5 manifest <file>건` | DeveloperPL + git log |
| 구현 리뷰 | `PASS — Claude/Codex 종합, 코멘트 #<id>` | CodeReviewPL packet |
| 구현 테스트 | `CI gate <PASS\|FAIL> — checks <N>건` | `gh pr checks` 출력 |
| 보안 테스트 | `1차 alerts <N> / 2차 P0:<N> P1:<N>` | SecurityTestPL packet |

미정 데이터는 `?` placeholder (예: `Change Plan v? + ADR-? 신규 (deputy 6인)`).

### 14.7 Render flow

```
[Lane/Deputy event 발생]
  └→ Orchestrator 1차 수신
       ├→ 1) Read(.claude-work/progress/<KEY>.md)  (cache)
       ├→ 2) parse → 해당 lane sub-tree patch
       ├→ 3) Write(.claude-work/progress/<KEY>.md) — full rewrite, last_processed_seq 증가
       ├→ 4) terminal narration emit (ADR-029)
       ├→ 5) ★ TodoWrite update (ADR-041 NEW) — best-effort, hierarchical render rule
       └→ 6) Story 완료 시 _archive/<KEY>.md 로 mv + index.md 갱신
```

**TodoWrite update (step 5) detail (ADR-041)**:
- Lane 진입: lane row → 🔄 + agent sub-row 펼침 (PL → workers/deputies → chief 순)
- Agent return: 해당 agent sub-row 의 status=completed + content 갱신 (1-line 활동 결과)
- Lane PASS: agent sub-row 제거, lane row content = `PASS · <S3 snippet>`
- Lane FIX (검출 후): 검출 lane → ✅ + content `FIX-N detected (cause: <원인 lane>)`, 원인 lane → ❌ + content `FIX-N 원인 · <원인 판정 1줄>`, 재진입 lane row append (⏳ 시작)
- Multi-row in_progress 의도적 허용 (TodoWrite "ONE in_progress" 가이드 deviation, codeforge 병렬 agent 모델)
- Single-Story 모드 — `[KEY]` prefix drop (모든 row 에서)
- best-effort: TodoWrite update 실패 시 warning, lane primary work 미차단 (§14.5 best-effort 원칙)

### 14.8 Resume / corruption 처리

세션 재개 / 압축 재개 시:

1. `.claude-work/progress/<KEY>.md` 존재 여부 확인
2. **존재해도 신뢰하지 않음** — state source(Story §10 + GitHub Issue phase label + Story §-fill state)에서 재 derive
3. 재 derive 결과를 cache 재기록, last_processed_seq 갱신
4. **★ TodoWrite re-build (ADR-041 NEW)**: §0 file 의 lane 별 status 로 TodoWrite full rewrite
   - active lane 의 agent sub-row 는 빈 상태 (deputy 활성 정보 손실 허용 — 다음 deputy 이벤트에서 자동 충족)
   - 4 marker (⏳ 🔄 ✅ ❌) 어휘로 변환
   - Single-Story 모드 — `[KEY]` prefix drop
   - best-effort — TodoWrite re-build 실패 시 warning, file-only 상태로 lane work 진행 (§14.5 best-effort 원칙)
5. deputy sub-tree 는 비워둠 (file + TodoWrite 동일 — 다음 deputy 이벤트에서 자동 충족)

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
- `spawn_at` = ISO 8601 UTC.

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

Codeforge observability stack 의 channel 별 책임 분리 normative SSOT. Tier 1 (ephemeral) / Tier 2 (committed lane-coarse) / Tier 3 (persistent measurement) 으로 stratify, 각 channel 의 Granularity / Storage / Owner / Lifecycle 명시 — boundary race + double-count 차단 invariant.

### 15.1 7-channel boundary table

| Channel | Tier | Granularity | Storage | Owner | Lifecycle |
|---|---|---|---|---|---|
| **stderr narration** ([ADR-029](adr/ADR-029-phase-execution-visibility-expansion.md)) | 1 ephemeral | sub-step | scrollback | Orchestrator | session-only |
| **TodoWrite scratchpad** ([ADR-038](adr/ADR-038-progress-visualization-todowrite.md)) | 1 ephemeral | meta-cognitive | tool surface | Orchestrator | turn-only |
| **`.claude-work/progress/<KEY>.md` cache** (CFP-20) | 1 ephemeral | per-Story coarse | fs cache | Orchestrator | Story-only (post-merge mv `_archive/`) |
| **Story §10 FIX Ledger** (CFP-32 / [fix-event-v1](inter-plugin-contracts/fix-event-v1.md)) | 2 committed | discrete FIX event | git commit | Orchestrator monopoly | persistent (append-only) |
| **Story §14 Lane Evidence** ([ADR-031](adr/ADR-031-lane-spawn-evidence-trail.md)) | 2 committed | lane spawn coarse | git commit | Orchestrator monopoly | persistent (append-only) |
| **post-merge-counters.jsonl** ([ADR-026](adr/ADR-026-post-merge-automation.md)) | 3 persistent | post-merge action outcome | git commit | post-merge-followup.yml | persistent (append-only, opt-in) |
| **stop-event-v1 ledger** ([ADR-042 §결정 2](adr/ADR-042-codeforge-measurement-channel-architecture.md), [stop-event-v1](inter-plugin-contracts/stop-event-v1.md)) | 3 persistent | discrete stop event | hot tier (sqlite/JSONL) + cold tier (markdown) | Orchestrator-owned delegate subagent | hot 7-30d / cold persistent / opt-in default false |

### 15.2 Boundary 차단 invariant (3)

- **TodoWrite ↔ stop-event-v1 boundary**: TodoWrite 호출은 stop-event-v1 ledger record 대상 아님 ([ADR-038](adr/ADR-038-progress-visualization-todowrite.md) standalone 정당화 — meta-cognitive scratchpad, file system / GitHub state mutation 미발화). boundary 차단.
- **§14 ↔ spawn-event-v1 boundary**: spawn-event-v1 신설 보류 ([ADR-042 §결정 3](adr/ADR-042-codeforge-measurement-channel-architecture.md)) — 본 boundary race 회피. Phase 2 spawn-event land 시 dedup script 신설 의무 (§14 row count 와 spawn-event lane=spawn type count 정합 검증).
- **§10 ↔ stop-event-v1 boundary**: stop-event-v1 의 `reason_class: policy_violation` row 가 §10 FIX Ledger row append 의 proxy. dedup 책임 = aggregate script (Phase 2). cold tier 별도 file 신설 안 함 — §10 가 cold tier proxy.

### 15.3 5번째 measurement channel 추가 invariant

5번째 measurement channel (Tier 3) 추가 = [ADR-042](adr/ADR-042-codeforge-measurement-channel-architecture.md) amendment 의무. 본 closed enumeration 가 future "X tool 호출도 ledger record" 류 압박을 차단 — 모두 7-channel 의 어느 하나로 routing 또는 ADR amendment 발의.

### 15.4 Privacy / opt-in 정책 SSOT

stop-event-v1 ledger 의 privacy / opt-in / sanitize 정책 = [ADR-043 (codeforge telemetry privacy policy)](adr/ADR-043-codeforge-telemetry-privacy-policy.md) SSOT. 핵심 invariant 3:

- **opt-in default false** (consumer overlay `telemetry.enabled: false` default)
- **Allow-list ONLY 16 field whitelist** (capture 시점 — stop-event-v1 schema 16 field 외 capture 금지)
- **Deny-list regex 6 pattern** (capture 통과 후 2차 안전망 — API key / GitHub PAT / 한국 주민번호 / email / hex≥32 / GitHub fine-grained PAT)

### 15.5 0 API call constraint + measurement-vs-fix scope boundary

- **0 API call constraint** ([ADR-042 §결정 8](adr/ADR-042-codeforge-measurement-channel-architecture.md)) — telemetry instrumentation = local I/O only. Anthropic API / GitHub API / external service 호출 금지. measurement = measure 대상 amplify 금지 (CRITICAL invariant).
- **measurement-vs-fix scope boundary** ([ADR-042 §결정 10](adr/ADR-042-codeforge-measurement-channel-architecture.md)) — CFP-283 scope = measurement only. throttling / backoff / circuit breaker / rule-based hook = 별도 후속 CFP.
- **ROI gating** ([ADR-042 §결정 11](adr/ADR-042-codeforge-measurement-channel-architecture.md)) — Phase 2 enforcement 발동 prerequisite = post-merge-counters.jsonl 30+ run 누적 ([ADR-026 §결정 3](adr/ADR-026-post-merge-automation.md) 패턴 정합).

### 15.6 Cross-references

- [ADR-042](adr/ADR-042-codeforge-measurement-channel-architecture.md) — measurement channel architecture (본 §15 SSOT)
- [ADR-043](adr/ADR-043-codeforge-telemetry-privacy-policy.md) — telemetry privacy policy (sibling)
- [stop-event-v1](inter-plugin-contracts/stop-event-v1.md) — kind:registry 16-field schema
- [project-config-schema.md](project-config-schema.md) — telemetry block schema (opt-in default false)
- [consumer-guide.md](consumer-guide.md) § "Telemetry opt-in" — consumer 측 안내
- [docs/domain-knowledge/orchestrator-discipline/measurement-channel.md](domain-knowledge/orchestrator-discipline/measurement-channel.md) — 도메인 정의 + cross-ADR boundary 설명

---

## 16. Post-merge automation flow (ADR-026 + CFP-74)

ADR-026 의무 — wrapper Orchestrator 가 PR merge event 시 4 action 자동 처리. 사용자 admin merge 후 manual stops 4-5건/merge 자동 처리 → stop 빈도 직접 감소.

### 16.1 Trigger

GitHub Actions workflow `templates/github-workflows/post-merge-followup.yml`. trigger = `pull_request closed event + merged == true`. 사용자 admin merge / squash merge / rebase merge 모두 cover.

### 16.2 Disable-by-flag safety

`.codeforge/post-merge-automation.disabled` file 추가 시 workflow 즉시 skip. 운영 emergency 안전망.

### 16.3 4 Action sequence

| Order | Action | Script | Auth |
|-------|--------|--------|------|
| 1 | Phase label transition | `scripts/next-phase.sh` + `gh issue edit` | GITHUB_TOKEN (current repo) |
| 2 | Story §9 writer (cross-repo) | `scripts/post-merge-story-writer.sh` | CODEFORGE_CROSS_REPO_PAT (internal-docs contents:write) |
| 3 | Carrier Issue close (Phase 2 only) | `gh issue close` | GITHUB_TOKEN |
| 4 | Sibling PR auto-close (archive marker) | `scripts/post-merge-sibling-close.sh` | GITHUB_TOKEN |

각 action `continue-on-error: true` — 일부 실패 시 telemetry outcome=partial 기록 + 사용자 manual fallback.

### 16.4 Telemetry counter

`<internal-docs>/wrapper/post-merge-counters.jsonl` (JSONL append-only, contract_version 1.0). schema:
- `timestamp` / `story_key` / `pr` / `outcome` (auto_completed | partial | manual_only) / `actions_completed[]` / `actions_failed[]` / `decider` / `workflow_run_id`

PMOAgent retro 시 30+ run 누적 후 ROI report 생성 의무. ADR-022 §결정 8 Phase 2 transition gate input.

### 16.5 main 직접 push 금지 invariant

internal-docs cross-repo write 는 항상 branch (`<key>-post-merge-followup-prN`) + PR open 패턴. 사용자 admin merge 패턴 유지. 본 invariant 위반 시 ADR-024 위반 = policy_violation defect.

### 16.6 Idempotency

- Story §9 writer: 본 PR ref 의 row 이미 존재 시 skip (grep 기반 dedup)
- Telemetry counter: workflow_run_id 별 unique entry (재실행 시 별도 entry)
- Phase label transition: 현재 phase == next phase 시 no-op

### 16.7 Boundary (Phase 1 scope, ADR-026 §결정 3)

- ✅ wrapper Orchestrator post-merge automation (4 action + telemetry)
- ✅ disable-by-flag + main 직접 push 금지
- ❌ Enforcement (whitelist 외 stop refusal) — Phase 2 ROI 평가 후 별도 CFP
- ❌ Consumer overlay path support — Phase 2 PMOAgent retro 후

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
- 2026-04-26: **v9 Review/Test 워커 통합 (BREAKING)** — [ADR-001](../docs/adr/ADR-001-review-agent-unification.md). 3 lane × 2 vendor = 6 워커(Claude/Codex × Design/Code/Security)를 lane-agnostic 2 워커(`ClaudeReviewAgent` / `CodexReviewAgent`)로 통합. 도메인은 호출 PL이 review packet으로 주입(checklist_path · scope_globs · category_enum · severity_overrides). 공통 base SSOT = `templates/review-pl-base.md`, 체크리스트 SSOT = `templates/review-checklists/{design,code,security}.md`. 25 → **20 core agents**. SecurityTestPL에 `Bash(gh api repos/*)` 권한 부여(1차 layer alerts fetch). 워커 packet 누락 시 `ESCALATE_PACKET_INCOMPLETE` 강제 — generic fallback 금지.

- 2026-05-09: **v10 CFP-293** — §8.4 성능 베이스라인 정책 (Issue #306 / NF-T5) 신설 + §14.11 Spawn ID 대장 mini-table (Issue #312) 신설 + §14.12 Spawn-level token telemetry mini-table (Issue #300) 신설.

본 playbook은 에이전트 구조·규약 변경 시 PR과 함께 갱신. git log로 변경 추적.
