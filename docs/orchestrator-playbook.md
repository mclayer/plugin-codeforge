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
  - agents/DesignReviewPLAgent.md
  - agents/CodeReviewPLAgent.md
  - agents/DeveloperPLAgent.md
  - agents/TestAgent.md
  - agents/DocsAgent.md
---

# Orchestrator Playbook

최상위 Claude 세션(이하 **Orchestrator**)의 행동 SSOT. 사용자(Human)가 제공한 요구사항을 받아 20 core 에이전트 + role:dev roster를 조정하는 모든 규약을 담는다.

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

   **0f. 확인 결과 사용자 통보 형식**
   ```
   🔍 세션 개시 의존성 점검
   - GitHub MCP: ✅ 노출 / ❌ 미인증 → /mcp 재인증 필요
   - codex 플러그인: ✅ / ❌ cache 부재 → /plugins install codex@openai-codex
   - superpowers 플러그인: ✅
   - claude-md-management 플러그인: ✅
   - github 플러그인: ✅
   - codex CLI: ✅ /opt/homebrew/bin/codex / ❌ 미설치 → brew install 권장
   - gh CLI: ✅ + 인증 OK / ❌ → gh auth login 안내
   - consumer 리포 .github/ 셋업: 6 워크플로우 / 3 forms / PR template / CODEOWNERS — N개 누락 (안내만)
   - (권장 플러그인: 4/4 활성 / 일부 비활성 — 진행에 영향 없음)

   [블로커 X건 — 복구 완료 전 대기]
   ```

1. **메모리 로드**: `~/.claude/projects/<workspace-hash>/memory/MEMORY.md` — 이전 세션 feedback·project·reference 기록 확인
2. **활성 Story 조회**: `mcp__github__list_issues(state='open', labels=['type:story'])`
3. **ADR 목록 확인**: 세션 내 첫 설계 결정 직전에만 `Glob(docs/adr/ADR-*.md)` + `Grep` (frontmatter category·status 필터)
4. **태스크 분류**:
   - 신규 요구사항 → §1.2 신규 세션 플로우
   - resume (활성 Story 존재) → §7 세션 재개 복원 절차

### 1.2 신규 세션 플로우

```
사용자 요구사항 접수
  ↓
Orchestrator 태스크 분류 (Epic/Story 단위 분해)
  ↓
DocsAgent 경유 GitHub Milestone 생성 (Epic — 사용자 요구사항 1건 단위)
  + DocsAgent 경유 Epic Issue 생성 (label: type:epic, body: narrative description, milestone 매핑)
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
  ├─ DocsAgent 경유 GitHub Issue 생성 (label: type:story + phase:요구사항, milestone)
  ├─ DocsAgent가 docs/stories/<KEY>.md 생성 + Phase 1 PR 수동 open
  └─ RequirementsPLAgent 스폰

Story 완료 직후:
  └─ PMOAgent 스폰 (회고 감사 + FIX Ledger 리뷰 + ADR 후보 검토)
```

### 1.3 세션 종료 조건

- **정상 완료**: 보안 테스트 레인 PASS → DocsAgent로 Story file §11 회고 작성 + Phase 2 PR `Closes #N` 머지 → Issue 자동 close → 세션 회고 (§8.3) → 종료
- **blocking wait**: PMOAgent "사용자 확인 필요" 체크박스 미해소 → 사용자 질문 제시 후 세션 대기 (§2)
- **ESCALATE**: 설계 리뷰·구현 리뷰 FIX 3회 초과 또는 Architect 판단 근본 한계 → 구조화된 에스컬레이션 보고 후 판단 대기

---

## 2. 사용자(Human) 상호작용 규약

### 2.1 blocking wait 진입 기준

다음 중 하나 이상 충족 시 Orchestrator는 **즉시 진행 중단**하고 사용자 응답 대기 상태로 전이:

- RequirementsPLAgent 통합 명세서에 "사용자 확인 필요" 체크박스 미해소 항목 존재 (Story file §5.5)
- RequirementsPLAgent 상충 조정 실패 (Domain·Analyst·Researcher 세 관점 결론 충돌, ADR 위반 혐의 등)
- ArchitectAgent가 "기존 API의 breaking change 불가피" 보고
- DesignReviewPL ESCALATE 판정 (설계 리뷰 FIX 3회 초과)
- CodeReviewPL ESCALATE 판정 (구현 리뷰 FIX 3회 초과)
- Architect가 "테스트 반복 FAIL — 근본 원인 재분석 후에도 해소 불가" 보고
- 사용자 요구사항 범위·우선순위·예산이 프롬프트에서 해석 불가

### 2.2 사용자 응답 수령 시 재스폰 대상 판정

| 응답 종류 | 재스폰 대상 | 전달할 컨텍스트 |
|-----------|------------|----------------|
| "사용자 확인 필요" 답변 | RequirementsPLAgent | 답변 내용 + 기존 Story file 경로 |
| ADR 갱신 승인 | DocsAgent → RequirementsPLAgent | DocsAgent가 ADR 업데이트 후 RequirementsPLAgent 재호출 |
| breaking change 승인 | ArchitectAgent | ADR 후보 추가 지시 + Change Plan 재수립 |
| 설계 리뷰 ESCALATE 후 judgment | ArchitectAgent (재진입) | 사용자 지시를 Change Plan 갱신 입력으로 전달. 설계 리뷰 카운터 **리셋** |
| 구현 리뷰 ESCALATE 후 judgment | ArchitectAgent | 동일 — 구현 리뷰 카운터 리셋 |
| 테스트 반복 FAIL 판단 | ArchitectAgent | 사용자 지시 근본 원인 가설 + Change Plan 대폭 수정 허가 |
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

### 3.1 7 레인 + Cross-cutting 스폰 순서 (요약)

```
[Cross-cutting 트리거]
Epic 창설:  Orchestrator → PMOAgent (Scope 분해 자문)
Story 완료: Orchestrator → PMOAgent (회고 감사 + ADR 후보 검토)

[Story 내부 7 레인]
요구사항:    Orchestrator → RequirementsPLAgent(DomainAgent ∥ Analyst ∥ Researcher 병렬, 셋 다 non-skippable) → PL dedup·상충 조정 → Story file §3-6 갱신
설계:        Orchestrator → ArchitectAgent → (CodebaseMapper ∥ Refactor 병렬) → Architect 대립 조정 → Change Plan 확정
                         → DocsAgent (docs/change-plans/<slug>.md commit + Story file §7 미러링)
설계 리뷰:   Orchestrator → DesignReviewPLAgent (lane=design packet) → (ClaudeReviewAgent ∥ CodexReviewAgent) → PASS/FIX
                         → PASS 시 DocsAgent가 gate:design-review-pass 라벨 부착 → Phase 1 PR mergeable
구현:        Phase 1 PR merge 후 Phase 2 PR open (DeveloperPL → DocsAgent → mcp__github__create_pull_request)
             Orchestrator → (DeveloperPLAgent(role:dev roster 병렬) ∥ QADev) → 완료 보고
                         → Orchestrator가 Architect stateless 재스폰 → 매핑표 감사
                         → §8.5 Impl Manifest commit 시 subissue-from-impl-manifest.yml 자동 sub-issue 생성
구현 리뷰:   Orchestrator → CodeReviewPLAgent (lane=code packet) → (ClaudeReviewAgent ∥ CodexReviewAgent) → PASS/FIX
구현 테스트: Orchestrator → TestAgent (기능 → 성능 순차) → ALL PASS/FAIL
보안 테스트: Orchestrator → SecurityTestPLAgent (lane=security packet + 1차 layer fetch 의무)
             1차 layer (자동): Dependabot + CodeQL + Secret Scanning + Push Protection 결과 fetch (`gh api repos/*`)
             2차 layer (병렬): ClaudeReviewAgent ∥ CodexReviewAgent → PASS/FIX
                         → PASS 시 DocsAgent가 gate:security-test-pass 라벨 부착 → Phase 2 PR mergeable
완료:        Phase 2 PR merge (`Closes #<Story Issue>`) → Issue 자동 close → DocsAgent (Story file §11 + status:completed)
             → PMOAgent (회고)
```

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
- GitHub Issue 코멘트 기록 의뢰: Orchestrator 경유 DocsAgent가 수행 (본 에이전트는 직접 기록 불가)
  · 기록 요청 형식: `[<phase>] <AgentName>: <요약>` + 상세 본문 + 원문 링크
- 산출물 경로: {파일 경로 또는 Story file 섹션 N 갱신 의뢰}

[제약]
- 문서화 표준은 DocsAgent.md 참조 — GitHub Issue/PR/docs 직접 write 금지
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
| **ArchitectAgent** | Change Plan 저장 경로 + §8 Test Contract 작성 의무 + DocsAgent 이중 저장 (`docs/change-plans/<slug>.md` + Story file §7 미러링). Mapper·Refactor **병렬** 스폰 지시. Clarification 재스폰 의뢰 권한 |
| **CodebaseMapperAgent** | as-is 변호 역할. 매 설계 레인 진입 시 Refactor와 병렬 재스폰, base_sha/scope_paths frontmatter. Refactor 산출물 미수신 — 원 소스 직접 독해 |
| **RefactorAgent** | to-be 혁신 역할. Mapper 산출물 미수신, 원 소스 직접 독해. "잠재 변호 논리 예상" 섹션으로 self-identify한 충돌 지점 제출 (Architect가 Mapper 실제 변호와 대조) |
| **QADeveloperAgent** | Change Plan §8 Test Contract 입력. 매핑표 반환 의무 |
| **`role: dev` 에이전트** (DeveloperAgent·DataEng·InfraEng·preset·overlay) | 계획서 변경 금지 — 결함 발견 시 즉시 DevPL→Architect 에스컬레이션 |
| **DesignReviewPLAgent** | lane=design packet 작성 (`templates/review-checklists/design.md` 인용 + scope_globs + category_enum + severity_overrides). Claude/Codex 통합 워커 병렬 스폰 후 종합. ADR 정합성 체크 P0 고정 |
| **CodeReviewPLAgent** | lane=code packet 작성. Claude/Codex 통합 워커 병렬 스폰 후 종합. DesignReviewPL과 공통 severity 규칙 (base 템플릿 SSOT) |
| **TestAgent** | 구현 테스트 레인 — 기능 → 성능 순차, baseline 비교 임계 mean:10% |
| **SecurityTestPLAgent** | 1차 layer = Dependabot/CodeQL/Secret Scanning 결과 `gh api repos/*` 로 fetch → packet에 inline 첨부. 2차 layer = lane=security packet으로 Claude/Codex 통합 워커 병렬 스폰 후 종합. 구현 테스트 PASS 이후 진입 |
| **ClaudeReviewAgent / CodexReviewAgent** | lane-agnostic 워커 ([ADR-001](../docs/adr/ADR-001-review-agent-unification.md)). 호출 PL이 review packet으로 도메인(체크리스트·스코프·category enum·severity 자동 룰) 주입. packet 누락 시 ESCALATE 반환 — generic fallback 금지. 정규화 스키마 P0/P1/P2/P3 + lane 필드 반환. CodexReviewAgent는 codex-companion.mjs 실행 |
| **DocsAgent** | 단독 writer — GitHub Issue/PR/comment + docs/** 모든 write 요청 수령. 작업 유형·섹션 번호 명시 |

### 3.3 컨텍스트 주입 정책

- **Story file 경로 + 참조 섹션 번호**가 기본 — verbatim 복사 지양
- ADR **직접 제약**인 경우에만 프롬프트에 verbatim 포함
- 배경 참조 ADR은 Story file §3 링크로 충분
- 코드 경로는 Story file §4에 요약, 구체 내용은 `Read`/`Glob`/`Grep` 도구로 직접 접근

---

## 3B. Preflight 체크 (lane 진입 직전)

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
- 권장 복구: {DocsAgent로 §X 보강 / GitHub label 수정 / Codex 재설치 안내}
```

사용자 응답 수령 전까지 레인 진입 금지.

### 3B.3 적용 레인별 세부

- **요구사항**: (1) `phase:요구사항` / (2) §1 사용자 원문 존재 + **공통 입력 패키지 준비** (관련 ADR 목록 §3 선제 fetch via `Glob(docs/adr/ADR-*.md)`, 관련 코드 경로 §4 식별, Project Config Packet slice 확보) / (3) `codex` CLI 가용 + GitHub MCP 가용 (DomainAgent·Researcher 호출 포함)
- **설계**: (1) `phase:설계` / (2) §1-6 모두 채움 + "사용자 확인 필요" 해소 + **공통 입력 패키지 준비** (변경 대상 코드 경로 확정, 관련 ADR verbatim fetch, Change Plan 초안 메모 준비) / (3) GitHub MCP 가용
- **설계 리뷰**: (1) `phase:설계-리뷰` / (2) §7 채움 + `docs/change-plans/<slug>.md` 존재 / (3) Codex 플러그인 가용
- **구현**: (1) `phase:구현` / (2) §7 완료 + Change Plan §8 Test Contract 존재 (§8.3 `N/A` 허용) + Phase 1 PR merged / (3) 필요 Dev 전원 스폰 가능
- **구현 리뷰**: (1) `phase:구현-리뷰` / (2) §8 Impl Manifest 기록 + Architect 매핑표 감사 PASS / (3) Codex 플러그인 가용
- **구현 테스트**: (1) `phase:구현-테스트` / (2) §9.2 구현 리뷰 PASS 기록 / (3) 프로젝트 테스트 러너 환경 가용
- **보안 테스트**: (1) `phase:보안-테스트` / (2) §9.3 구현 테스트 PASS 기록 / (3) Codex 플러그인 가용 + 의존성 매니페스트 존재 + Dependabot/CodeQL 결과 접근 가능

### 3B.4 Preflight 결과 기록 (PMO 감사 trail · 의무)

PASS·FAIL 무관, **모든 Preflight 실행 결과**는 DocsAgent 경유로 GitHub Issue 코멘트에 기록한다 (PMO 회고 §13.2의 "Preflight 실행 근거" 감사 항목 충족).

Orchestrator가 Preflight 직후 DocsAgent에 아래 형식으로 의뢰:

```
[DocsAgent 요청: Issue 코멘트]
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

DocsAgent는 `mcp__github__add_issue_comment` 1회 호출. 코멘트 prefix는 `[<phase>] Orchestrator: Preflight {PASS|FAIL}`. 기록 누락 시 PMO 완료 회고에서 P1 결함으로 감사 보고됨.

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
| **설계 레인** | CodebaseMapper ∥ Refactor | 둘 다 원 소스(코드·ADR·Change Plan 초안) 직접 독해, 타 산출물 미참조 → 입력 독립. Architect가 교차 검토 |
| **설계 리뷰** | ClaudeReviewAgent ∥ CodexReviewAgent (lane=design packet) | 읽기 전용, 정규화 스키마 동일 |
| **구현 리뷰** | ClaudeReviewAgent ∥ CodexReviewAgent (lane=code packet) | 동일 |
| **보안 테스트** | ClaudeReviewAgent ∥ CodexReviewAgent (lane=security packet) | 동일. 워커는 lane-agnostic, PL이 packet으로 도메인 분기 |
| **구현** | DevPL(`role: dev` roster 병렬) + QADev(tests/**) | 쓰기 경로 분리 — roster 전체 의존성 없는 한 병렬 |

### 4.3 병렬 일부 실패 시

- **모두 완료 대기**가 원칙 — iteration 낭비 방지
- 예외: ClaudeReview가 [P0]를 즉시 내면 Codex 대기 없이 FIX 진입 가능 — 단 Codex 완료 후 결과 병합해 Story file §9에 기록

### 4.4 Clarification 재스폰 절차 (요구사항·설계 레인 공통)

서브 에이전트는 one-shot 실행이라 PL↔서브 continuous dialog 불가. PL(RequirementsPL 또는 Architect)이 병렬 결과 통합 중 추가 질의가 필요하면:

1. PL이 Orchestrator에 재스폰 요청 페이로드 전달:
   - 대상 에이전트명
   - 이전 본인 출력 pointer (Story file 참조 또는 메모리 slice)
   - clarification context (무엇을 추가로 묻는가, 왜)
   - 범위 제한 (전면 재분석 vs 특정 섹션 보강)
2. Orchestrator가 해당 에이전트를 **신규 스폰** — frontmatter에 `rspawn_reason` + `prior_output_ref` 기록
3. 에이전트가 이전 출력을 참조 + 추가 범위만 분석해 보강 산출물 반환
4. PL이 재수령 후 통합 단계 반복
5. 재스폰 이력은 **Story file §9.0 "Clarification 재스폰 이력"** 에 append (DocsAgent 단독 갱신). §10 FIX Ledger와 분리 — 재스폰은 게이트 실패 아니며 GitHub `fix:*` 라벨 미추가

**무제한 재스폰 금지** — 동일 에이전트 2회 재스폰 이후에도 미해소면 사용자 ESCALATE로 전환 (§2.3).

---

## 5. docs/stories file 동기화

### 5.1 단계 종료 시 DocsAgent 스폰 체크리스트

| 트리거 | 갱신 섹션 | Orchestrator가 DocsAgent에 전달할 내용 |
|--------|----------|---------------------------------------|
| 신규 Story Issue 생성 직후 | docs/stories/<KEY>.md 신규 생성 + §1-2 (또는 story-init.yml Action이 자동) | 사용자 원문 verbatim + DomainAgent 도메인 해석 |
| RequirementsPLAgent 통합 명세서 확정 | §3-6 | 관련 ADR / 코드 경로 / Analyst / Researcher / 상충 분석 |
| Architect Change Plan 확정 | §7 + `docs/change-plans/<slug>.md` 신규 commit | Change Plan 요약 + Mapper/Refactor 대립 결론 |
| 설계 리뷰 iteration 종료 | §9.1 "설계 리뷰 Iteration N" | Claude/Codex severity counts + 주요 findings 3-5건 + DesignReviewPL 판정 |
| 설계 리뷰 PASS | label `gate:design-review-pass` 부착 + Phase 1 PR mergeable | (라벨만, 본문 변경 없음) |
| Dev/Engineer 구현 완료 | §8 + §8.5 Impl Manifest commit (subissue Action 트리거) | QADev 매핑표 요약 + 담당 에이전트 + 변경 파일 경로 |
| 구현 리뷰 iteration 종료 | §9.2 "구현 리뷰 Iteration N" | 동일 형식 |
| 구현 테스트 레인 종료 | §9.3 "구현 테스트 레인" | 기능 통과/실패 + 성능 baseline 대비 변동 |
| 보안 테스트 iteration 종료 | §9.4 "보안 테스트 Iteration N" | Claude/Codex severity counts + 보안 findings + SecurityTestPL 판정 + 1차 layer 결과 (Dependabot/CodeQL/Secret Scanning) |
| 보안 테스트 PASS | label `gate:security-test-pass` 부착 + Phase 2 PR mergeable | (라벨만) |
| FIX 발생 (iteration 단위) | §10 "Iteration N" commit (fix-ledger-sync.yml Action이 자동 mirror+label) | 트리거 · 원인 판정(구현 vs 설계) · 수정 방향 · 결과 |
| Phase 2 PR merged (최종) | §11 + Issue auto-close | PR 링크 + `status:completed` |

### 5.2 Story file 읽기 규약

- **필요한 섹션만 읽기**: 프롬프트에 `§X, §Y 참조` 명시 → 에이전트가 `Read(docs/stories/<KEY>.md)` 후 해당 섹션만 참조
- 전체 file 읽기는 Architect 설계 진입 1회만 허용 (§1-6 전체 필요)
- file 변경은 **DocsAgent 독점**

### 5.3 GitHub Issue body vs Story file

| 위치 | 내용 |
|------|------|
| Story Issue body | "Story SSOT: `docs/stories/<KEY>.md`" 한 줄 링크 (story-init.yml이 자동 변환) |
| docs/stories/<KEY>.md | 전체 컨텍스트·서사 (§1-11 규격) |
| Story Issue comments | 단계별 이벤트 로그 (DocsAgent가 `[<phase>] <AgentName>: <한 줄>` 형식 기록) |

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

§10 스키마·DocsAgent 갱신 절차는 [DocsAgent.md](../agents/DocsAgent.md) §9 참조.

§10에 새 행 commit 시 `fix-ledger-sync.yml` Action이 자동:
1. Story Issue에 `[FIX #N]` 코멘트 mirror
2. `fix:<레인>-retry` 라벨 자동 부착

### 6.2 트리거 → 상태 전이

| 현재 phase | 트리거 | 전이 후 phase | §10 행 추가 | 라벨 동작 (자동) |
|-----------|--------|---------------|-------------|-----------|
| 설계-리뷰 | DesignReviewPL FIX | 설계 | Iter N / 설계-리뷰 / 원인=설계 / 재실행 범위 | `fix:설계-리뷰-retry` |
| 설계-리뷰 | DesignReviewPL PASS | 구현 | — | `gate:design-review-pass` 부착 + phase 라벨 변경 |
| 구현-리뷰 | CodeReviewPL FIX (원인=구현) | 구현 | Iter N / 구현-리뷰 / 원인=구현 / 재구현 | `fix:구현-리뷰-retry` |
| 구현-리뷰 | CodeReviewPL FIX (원인=설계) | 설계 (Phase 1 follow-up PR) | Iter N / 구현-리뷰 / 원인=설계 / Change Plan 갱신 | `fix:구현-리뷰-retry` (§10 행의 `lane` 컬럼 기준 — fix-ledger-sync.yml은 single-label 부착. 설계 회귀는 원인 판정 컬럼으로 식별, 이후 설계 리뷰 재실행 시 별도 §10 행 추가되어 `fix:설계-리뷰-retry` 라벨 자동 부착) |
| 구현-리뷰 | CodeReviewPL PASS | 구현-테스트 | — | (phase 전이만) |
| 구현-테스트 | TestAgent FAIL (원인=구현) | 구현 | Iter N / 구현-테스트 / 원인=구현 / 재구현 + **RESET 구현-리뷰** | `fix:구현-테스트-retry` |
| 구현-테스트 | TestAgent FAIL (원인=설계) | 설계 (Phase 1 follow-up PR) | Iter N / 구현-테스트 / 원인=설계 / Change Plan 갱신 + **RESET 구현-리뷰** | `fix:구현-테스트-retry` |
| 구현-테스트 | TestAgent ALL PASS | 보안-테스트 | — | (phase 전이만) |
| 보안-테스트 | SecurityTestPL FIX (원인=구현) | 구현 | Iter N / 보안-테스트 / 원인=구현 / 재구현 + **RESET 구현-리뷰** | `fix:보안-테스트-retry` |
| 보안-테스트 | SecurityTestPL FIX (원인=설계) | 설계 (Phase 1 follow-up PR) | Iter N / 보안-테스트 / 원인=설계 / Change Plan 갱신 + **RESET 구현-리뷰** | `fix:보안-테스트-retry` |
| 보안-테스트 | SecurityTestPL PASS | 완료 | — | `gate:security-test-pass` 부착 → Phase 2 PR mergeable → merge → Issue auto-close |

### 6.3 RESET 마커 규칙

- 구현 테스트 FAIL 또는 보안 테스트 FAIL → 구현 복귀 시 §10 마지막 행의 `RESET?` 컬럼에 `RESET 구현-리뷰` 기입
- 이후 구현 리뷰 카운터는 RESET 행 이후 iteration만 카운트 (이전 iteration은 감사 이력으로 유지)
- 설계 리뷰·구현 리뷰 내부 루프는 RESET 없음

### 6.4 §10 관리 세부

- DocsAgent가 단독 갱신 (append-only, 행 삭제·수정 금지)
- Orchestrator는 `Read(docs/stories/<KEY>.md)`로 §10 read-only 조회 후 count 산출
- §10 조회 실패(파일 부재 등) → Architect 판정 정지 → 사용자 판단 요청
- GitHub 라벨은 fix-ledger-sync.yml Action이 §10 commit 감지 시 자동 부착 — 대시보드 search syntax 필터용

### 6.5 원인 판정 decision table

[CLAUDE.md](../CLAUDE.md) "원인 판정 decision table" 섹션이 SSOT — 본 playbook은 표를 inline 복제하지 않는다 (drift 방지). Orchestrator는 FIX 트리거 시 CLAUDE.md 표를 직접 참조해 DeveloperPL/Architect 전달용 evidence pack을 구성.

**Architect 최종 판정 + evidence pack(Change Plan 버전 + 리뷰 findings + 테스트 로그) 첨부 의무**.

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
| phase:설계 | §7 초안만 | ArchitectAgent — Mapper·Refactor **병렬 재스폰** (이전 산출물 세션 외 유지 불가, §7 Change Plan 초안만 복원됨) |
| phase:설계 | §7에 Mapper/Refactor 한쪽만 반영 (부분 완료 resume) | 미반영 쪽 에이전트만 **선택 재스폰** + 반영된 쪽은 재활용. §9.0에 "Resume 부분 재스폰" 행 append |
| phase:설계 | §7 완료 | DocsAgent가 Change Plan 저장 완료 확인 → 설계 리뷰 진입 |
| phase:설계-리뷰 | §9.1 블록 없음 | DesignReviewPLAgent 재스폰 (Claude/Codex 병렬) |
| phase:설계-리뷰 | §9.1 블록 FIX | ArchitectAgent 재진입, Change Plan 갱신 |
| phase:구현 | §7 완료, §8 비어있음 | Phase 2 PR open 여부 확인. 없으면 DocsAgent 경유 PR open. 있으면 DevPL + QADev 병렬 스폰 |
| phase:구현 | §8 일부 | 마지막 구현 에이전트 (§8에서 확인) 재스폰 |
| phase:구현-리뷰 | §9.2 블록 없음 | CodeReviewPLAgent 재스폰 |
| phase:구현-리뷰 | §9.2 블록 FIX | DeveloperPL 1차 진단 → Architect 최종 판정 |
| phase:구현-테스트 | §9.3 블록 없음 | TestAgent 재스폰 |
| phase:구현-테스트 | §9.3 블록 FAIL | DeveloperPL 1차 진단 → Architect 최종 판정 |
| phase:보안-테스트 | §9.4 블록 없음 | SecurityTestPLAgent 재스폰 (Claude/Codex 병렬) |
| phase:보안-테스트 | §9.4 블록 FIX | DeveloperPL 1차 진단 → Architect 최종 판정 |

### 7.4 FIX 카운터 복원 (세션 개시/압축 재개 시 의무)

세션 개시 시점 또는 컨텍스트 압축 후 재개 시 Orchestrator는 **반드시** 아래를 수행:

1. 활성 Story file `Read(docs/stories/<KEY>.md)` 호출
2. §10 "FIX Ledger" 파싱 → 마지막 `RESET 구현-리뷰` 이후 행으로 각 레인 카운터 산출 (설계-리뷰 / 구현-리뷰 / 구현-테스트 / 보안-테스트 4개)
3. 파일 read 실패 시 **사용자 ESCALATE** (카운터 불명 상태 진행 금지)

GitHub 라벨 count는 감사 이력으로 보존되나 복원 source of truth 아님 (§10 기준). 이 절차 없이 Architect 판정 진행 금지.

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
- 에이전트별 누적 토큰 (20 core + preset/overlay-only `role: dev` 에이전트)
- FIX iteration별 추가 토큰
- **Architect stateless 재스폰 overhead**: 재스폰 당 ~5-10k tokens (Story file §1-8 fetch). FIX 3회 가정 시 15-30k

### 8.2 레인별 사전 예산·중단 임계

두 지표로 추적:
- **Total**: 레인 전체 누적 (병렬·순차 합산, 에이전트별 input+output)
- **Peak concurrent**: 같은 시점에 동시 실행되는 에이전트의 현재 context 합계 — 병렬 모델에서 실제 비용 지표. v0.7.0 병렬화로 요구사항·설계 peak이 크게 증가

| 경로 | Total 사전 예산 | Total 중단 임계 | Peak concurrent (동시 컨텍스트 합) | 비고 |
|------|-----------------|-----------------|------------------------------------|------|
| 요구사항 | 80k | 150k | ~60k (Domain ∥ Analyst ∥ Researcher, 각 ~20k 풀 컨텍스트) | v0.6 순차 대비 total +30k / peak 3× |
| 설계 | 120k | 220k | ~50k (Mapper ∥ Refactor, 각 ~25k) + Architect 5-10k | v0.6 순차 대비 total +20k / peak 2× |
| 설계 리뷰 | 50k | 120k | ~40k (Claude ∥ Codex) | 기존 유지 |
| 구현 | 200k | 400k | roster size × ~20k + QADev 20k | 기존 유지 (`role: dev` 병렬 수에 비례) |
| 구현 리뷰 | 60k | 150k | ~40k (Claude ∥ Codex) | 기존 유지 |
| 구현 테스트 | 50k | 120k | TestAgent 단일 | 기존 유지 |
| 보안 테스트 | 60k | 150k | ~40k (Claude ∥ Codex 보안 focus) | 기존 유지 (1차 layer는 GitHub native, 토큰 비용 없음) |
| Clarification 재스폰 (per instance) | 10-20k 추가 | — | 단일 에이전트 재실행 | 2회 한도 (§4.4), 초과 시 ESCALATE |
| FIX 루프 (per iteration) | 50k + Architect 재스폰 5-10k | 150k | FIX 트리거 레인 동일 | 기존 유지 |

**Peak 고려 이유**: 병렬 스폰은 순차보다 wall-clock 단축하나 **동시 활성 context 총량** 증가 → session memory pressure. Peak이 임계 접근 시 순차 fallback 또는 에이전트 범위 축소 검토.

**중단 임계 초과 시**: 진행 중단 → §2.3 형식으로 "토큰 한계 도달, 계속 진행 결정" 에스컬레이션.

### 8.3 세션 회고 보고 (완료 시 필수)

#### 에이전트별 작업 요약 (20 core + 스폰된 preset/overlay-only role:dev, 미참여 "-")

| Agent | 수행 내용 |
|-------|-----------|
| Orchestrator | |
| PMOAgent | |
| RequirementsPLAgent | |
| DomainAgent | |
| DocsAgent | |
| ResearcherAgent | |
| RequirementsAnalystAgent | |
| ArchitectAgent | |
| CodebaseMapperAgent | |
| RefactorAgent | |
| DesignReviewPLAgent | |
| DeveloperPLAgent | |
| DeveloperAgent | |
| DataEngineerAgent | |
| InfraEngineerAgent | |
| <추가 role:dev 에이전트들> | |
| QADeveloperAgent | |
| CodeReviewPLAgent | |
| TestAgent | |
| SecurityTestPLAgent | |
| ClaudeReviewAgent | (3 lane 합산) |
| CodexReviewAgent | (3 lane 합산) |

#### 토큰 사용량 (전체 스폰된 에이전트, 0 허용)

| Agent | Input Tokens | Output Tokens | 합계 |
|-------|-------------|---------------|------|
| Orchestrator | | | |
| ... (20개 전체) | | | |
| **합계** | | | |

Orchestrator 자체 토큰 = 세션 전체 - 20 서브에이전트 합계.

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
3. 복구 후 DocsAgent 일괄 스폰으로 backlog 동기화 (write queue drain)
4. **FIX 카운터 조회 불가 시** (docs file은 로컬 file이라 read는 보통 가능): 그래도 실패하면 Architect 판정 정지 → 사용자 판단 요청

### 9.3 Codex CLI / 플러그인 미설치

- **CodexReviewAgent**: 미설치 시 3 리뷰 레인(설계 리뷰·구현 리뷰·보안 테스트) **모두 진입 불가** → 설치 안내 + 세션 중단
- **RequirementsAnalyst**: `codex` CLI 미설치 시 요구사항 레인 **진입 불가** → 동일
- `SKIPPED` 경로 허용 안 됨

### 9.4 Story file stale 감지

에이전트 보고에서 "Story file에 없는 컨텍스트" 또는 "현재 코드와 불일치" 감지 시:

1. Orchestrator가 즉시 DocsAgent 스폰 → 최신 상태로 Story file 갱신
2. 갱신 완료 후 해당 에이전트 재스폰

### 9.5 CodebaseMapper 산출물 stale 감지

- Mapper는 **매 설계 레인 진입 시 재스폰** — 이전 Story 산출물 재사용 금지
- 리뷰·테스트에서 설계 레인 복귀 시에도 재스폰 (구현 레인에서 코드 변경 가능성)
- 재사용 감지 시 Architect 단독 설계 결정 금지 (§2 설계 공동작업자 부재 상태)

### 9.6 Phase 1 / Phase 2 PR 모델 트러블슈팅

| 증상 | 원인 | 대응 |
|------|------|------|
| Phase 1 PR mergeable 아님 (label OK인데 Action fail) | `phase-gate-mergeable.yml` Action이 status check fail | Action 로그 확인. `gate:design-review-pass` 라벨 누락 검증 |
| Phase 2 PR open 안 되는 상태 | Phase 1 PR이 main에 merge 안 됨 | Phase 1 PR review 완료 + merge 후 Phase 2 PR open |
| §1 변경 PR이 reject됨 | `story-section-1-immutable.yml` Action이 §1 line range 변경 감지 | 정당한 정정 필요 시 architect team에 bypass approval 요청 |
| Sub-issue가 자동 생성 안 됨 | `subissue-from-impl-manifest.yml` Action 미실행 또는 §8.5 매핑표 형식 오류 | Action 로그 + §8.5 markdown table 형식 검증 |

---

## 10. Hotfix 경로 (운영 장애 대응)

정상 7-레인 full flow는 Story 1건당 반나절~수일 소요. 운영 장애로 즉시 대응 필요한 경우 아래 2경로 중 하나 선택. **어느 경로든 사후 감사는 동일하게 수행**.

### 10.1 Minimal Path (`severity:bug` — 기본 hotfix)

단일 파일·함수 범위 버그 수정, 계획·리뷰 생략.

```
Orchestrator → (사용자 승인) → 관련 `role: dev` 에이전트 단독 → 수정 + 테스트 실행
 · Change Plan 생략 (Story Issue body에 버그 근거 1-3줄만)
 · 설계 리뷰 생략, 구현 리뷰 생략
 · 구현 테스트 게이트는 유지 (TestAgent 기능 모드만, 성능 게이트 생략)
 · 보안 테스트는 Codex peer만 실행 (credential/injection 스팟 체크 — Claude peer 생략)
 · GitHub 라벨: `type:bug` + `hotfix:minimal`
 · 단일 PR (Phase 1+2 분할 없이)
```

**적용 조건** (모두 충족):
- 변경 라인 수 ≤ 30
- 설계 결정 없음 (기존 인터페이스·계약 그대로)
- 단일 파일 수정
- 운영 장애 복구 목적 (사용자가 명시)
- **보안 경계 변경 없음** (auth·권한·trust boundary 미변경) — 있으면 Medium Path 강제

### 10.2 Medium Path (`severity:critical` — 심각 hotfix)

여러 파일 걸친 운영 장애, 설계·구현 리뷰 축약.

```
Orchestrator → (사용자 승인) → Architect 빠른 Change Plan (§1·§5·§8 축약) → DevPL 구현 → TestAgent → SecurityTestPL
 · CodebaseMapper·Refactor 생략, Architect 단독
 · 설계 리뷰 생략
 · 구현 리뷰는 **Claude만** 실행 (Codex 생략 — 시간 절약)
 · 구현 테스트 게이트는 기능 + 성능 모두 수행
 · 보안 테스트는 Claude + Codex 둘 다 필수 (hotfix라도 보안 우회 금지)
 · GitHub 라벨: `type:bug` + `hotfix:critical`
 · 단일 PR
```

**적용 조건**: 사용자가 `severity:critical` 명시 + 운영 장애 복구 목적.

### 10.3 사후 감사 (X 경로 — 양 hotfix 공통 의무)

Hotfix merge 완료 후 **next working session** 초두에 Orchestrator가 자동 수행:

1. **Audit Issue 자동 생성**: GitHub Issue Forms (audit.yml) 자동 생성 — DocsAgent 경유. label `audit:post-hotfix` + `phase:요구사항`
2. **Change Plan 소급 작성**: Architect가 hotfix 변경 diff를 소급해 Change Plan 작성 (§1-10 전부, 단 실구현은 이미 존재 상태). docs/change-plans/ commit
3. **구현 리뷰 소급**: CodeReviewPL이 hotfix 변경사항 대상 소급 리뷰 (Claude + Codex 모두)
4. **보안 테스트 소급** (Minimal Path에서 Claude peer 생략한 경우에 한함): SecurityTestPL이 hotfix 대상 보안 리뷰 전체 재수행
5. **ADR 영향 검토**: 변경이 ADR 결정을 위반/변경하는지 Architect 검토, 필요 시 ADR 갱신
6. Audit Issue는 PR 없이 close 가능 (문서·ADR 갱신만 필요한 경우 → docs PR 1건으로 close)

**사후 감사 생략 금지** — hotfix는 "빠르게 대응 후 반드시 감사"가 원칙.

---

## 11. DocsAgent File-based Write Queue

DocsAgent는 단독 writer이므로 다중 에이전트 동시 write 의뢰 시 SPOF. 파일 기반 큐로 완충.

### 11.1 큐 위치 및 스키마

- **디렉토리**: `.claude-work/doc-queue/<story-key>/`
- **파일명**: `<seq>-<type>.md` (예: `001-issue-comment.md`, `002-story-section.md`, `003-change-plan.md`)
- **seq**: 3자리 0-padded 정수, 의뢰 순서. 중복 방지 위해 각 에이전트가 `ls` 후 max+1 선택

### 11.2 파일 포맷 (각 에이전트가 작성)

**파일명**: 기본 `<seq>-<type>.md`. `type=story-section`인 경우 atomic per-agent 갱신을 위해 `<seq>-story-section-<N>.md` (N = §N 섹션 번호)를 사용하며 frontmatter `section` 필드 필수. `type=domain-knowledge`인 경우 `<seq>-domain-knowledge.md`.

**Frontmatter (전체 type 공통 필수)**:

```markdown
---
type: issue-comment | story-section | change-plan | adr | adr-draft | domain-knowledge | ledger-append | label-update | pr-create
story: <KEY>                # 필수 — 디렉토리 이름과 일치
requester: <AgentName>      # 필수 — 의뢰 에이전트 식별
issued_at: <ISO 8601>       # 필수 — 큐 진입 시각
priority: normal | high     # 필수 — drain 우선순위
section: "<N>"              # type=story-section 인 경우 필수 (§N), 기타 type 생략
---

{DocsAgent.md §"작업 요청 인터페이스" 의 해당 템플릿 본문}
```

### 11.3 에이전트 측 의뢰 절차

1. `mkdir -p .claude-work/doc-queue/<story>/`
2. `ls` 후 next seq 계산
3. 템플릿 포맷으로 `<seq>-<type>.md` 작성
4. 반환 (DocsAgent 스폰 여부·시점 신경 쓰지 않음)

### 11.4 DocsAgent 측 drain 절차

Orchestrator가 DocsAgent를 스폰하면 DocsAgent는:

1. `.claude-work/doc-queue/<story>/` ls → seq 순으로 모든 파일 처리
2. 파일 frontmatter type 별로 해당 처리:
   - `issue-comment` → `mcp__github__add_issue_comment`
   - `story-section` → `Edit(docs/stories/<KEY>.md)`
   - `change-plan` → `Write(docs/change-plans/<slug>.md)` 또는 `Edit`
   - `adr` → `Write(docs/adr/ADR-NNN-<slug>.md)`
   - `adr-draft` → `Write(docs/adr/ADR-NNN-<slug>.md)` with `status: Proposed` (PMOAgent 발의)
   - `domain-knowledge` → `Write` 또는 `Edit(docs/domain-knowledge/<area>/<topic>.md)` (frontmatter `area`·`topic` 필드 사용)
   - `ledger-append` → `Edit(docs/stories/<KEY>.md)` §10 append (fix-ledger-sync.yml가 자동 mirror+label)
   - `label-update` → `mcp__github__issue_write` (label 추가/제거; phase-label-invariant.yml가 single-active 강제)
   - `pr-create` → `mcp__github__create_pull_request`
3. 처리 완료 파일 rm
4. drain 완료 후 Orchestrator에 처리 요약 반환

### 11.5 Orchestrator 측 스폰 트리거

- 레인 경계 (레인 종료 시점)
- FIX 판정 직후
- 사용자 ESCALATE 직전 (상태 영속화 목적)
- Story 완료 직전 (§11 최종 참조 기록)

### 11.6 fail-safe

- 큐 파일 파싱 실패 시 DocsAgent가 해당 파일만 skip + Orchestrator에 보고
- 세션 압축·재개 후에도 큐 파일 유지 — DocsAgent가 다음 스폰 시 이어서 drain
- 세션 종료 시점에 큐 비어있지 않으면 경고 보고

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

- **무효화 트리거**: DocsAgent가 Story file update 완료를 보고하면 해당 섹션 캐시 invalidate (또는 file mtime 변경 감지 시 자동 invalidate)
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
- **Path만 전달**: 단발성 조회 (DocsAgent 의뢰 포맷 등), 섹션 캐시 미정의 부분

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
| **DocsAgent** | 전체 (Issue create/comment/label·sub-issue·PR 생성·Milestone API + PR 제목 + CODEOWNERS 참조) |
| **RequirementsPLAgent** | `github.story_key_prefix` (Story KEY 결정), `github.org`, `github.repo` (search·list_issues 호출) |
| **DomainAgent** | `github.discussions.domain_kb_category` (Discussions Q&A) + `Glob(docs/domain-knowledge/**)` |
| **PMOAgent** | `github` 전체 (회고·패턴 search 호출) |

기타 에이전트 (설계·구현·리뷰·테스트 레인 대부분)는 GitHub 호출 없음 → packet 주입 불필요.

#### Fallback: Read로 직접 접근

Packet 주입은 Orchestrator의 토큰 최적화 수단이지 필수 규약 아님. Packet 누락 또는 일부 필드만 필요할 때 에이전트는 여전히 `Read(.claude/_overlay/project.yaml)`로 직접 접근 가능 (agent md `Read` 권한 보장).

---

## 13. PMOAgent 프로젝트 관리 (Cross-cutting)

PMOAgent는 단일 Story 레인 게이트 밖에서 cross-cutting 감사·회고·패턴 분석을 전담. 요구사항 해석은 RequirementsPLAgent 영역으로 분리됨.

### 13.1 스폰 타이밍 3종

| 트리거 | 시점 | 입력 | 산출물 |
|--------|------|------|--------|
| **Epic 창설** | Orchestrator가 Epic 생성 직후, Story 분해 직전 | 사용자 원문·관련 ADR·기존 Epic 이력·코드 구조 | Story 분해 자문 (의존성·우선순위·**병렬/순차 판정**) — 상세 규칙 [PMOAgent.md §1](../agents/PMOAgent.md) |
| **Story 완료** | TestAgent PASS → 보안 테스트 PASS → Phase 2 PR merge 직후 | 해당 Story file §1-11 + FIX Ledger + GitHub Issue 코멘트 이력 + 토큰 사용량 | 회고 감사 보고 (Preflight 누락·§8/§8.5 매핑·FIX evidence 완성도·예산) |
| **사용자 요청** | `/pmo-audit` 혹은 명시 요청 | 최근 N Story (기본 5) file·Ledger·ADR 변경 이력 | Cross-Story 패턴 보고 + ADR 후보 발의 |

### 13.2 감사 체크리스트 (Story 완료 회고 기본 세트)

1. **Preflight 실행 근거**: 각 레인 진입 시 Issue 코멘트에 `[<phase>] <AgentName>: Preflight PASS` 또는 failure 보고가 존재하는가
2. **§8 Test Contract ↔ tests/** 매핑**: QADev 매핑표의 모든 항목이 실제 tests/ 파일로 구현됐는가
3. **§8.5 Impl Manifest ↔ git diff**: 기록된 파일 목록이 PR의 실제 변경 파일과 일치하는가 (누락·추가 없이). subissue Action이 자동 생성한 sub-issue 목록과 대조
4. **FIX Ledger evidence pack**: 각 FIX iteration 행에 Architect 판정 근거(Change Plan 버전 + 리뷰 findings + 테스트 로그)가 코멘트로 기록됐는가
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

PMOAgent가 반복 패턴을 식별해 ADR draft를 write queue에 제출하면, DocsAgent가 `status=Proposed` ADR 파일(`docs/adr/ADR-NNN-<slug>.md`)을 신설. 다음 Story 설계 진입 시 Architect가 검토해 `status=Accepted` 전이 또는 기각.

```
write queue 파일: .claude-work/doc-queue/<epic>/<seq>-adr-draft.md
frontmatter type: adr-draft
body: PMOAgent.md의 "ADR 후보 발의" 템플릿 따름
```

### 13.5 PMOAgent 보고 기록

모든 PMOAgent 산출물은 `[PMO]` phase prefix로 GitHub Issue 코멘트 기록. Story 회고는 Story file §11에, Cross-Story 감사는 **별도 Issue** (label: `type:audit`, 제목: `PMO Audit / <YYYY-MM-DD>`)에 DocsAgent가 생성.

### 13.6 범위 외

PMOAgent가 **하지 않는** 것:
- 단일 Story 요구사항 해석 (RequirementsPLAgent)
- Change Plan 작성·검토 (Architect/DesignReviewPL)
- 코드 수정 (Dev)
- 테스트 실행 (TestAgent)
- 사용자 직접 상호작용 (Orchestrator 경유 보고만)

---

## 부록 A. 관련 문서

- `CLAUDE.md` — 에이전트 목록·레인·권한·GitHub Workflow·ADR 규약 ("무엇")
- 각 `agents/<Name>.md` — 에이전트별 역할·포지션·제약 (SSOT)
- `agents/DocsAgent.md` — 문서화 표준 SSOT (Issue 코멘트 phase prefix, Story file 섹션, Change Plan 템플릿, ADR 템플릿)
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
- 2026-04-24: v5 generic Dev roster + preset 시스템 (24 core 에이전트 + `role: dev` 동적 roster · 7 레인) — BackendDev·FrontendDev를 `presets/webapp/`으로 이동, core에 generic `DeveloperAgent` 신설, ServerEng를 `InfraEngineerAgent`로 리네임(범위 확장), DevPL이 `role: dev` frontmatter 태그로 런타임 roster discovery
- 2026-04-24: v6 Stage 2 `project.yaml` 구조화 SSOT 상수 도입
- 2026-04-26: **v8 Atlassian 제거 + GitHub 전환 (BREAKING)** — Confluence/Jira backend 완전 제거, GitHub primitive (Issues / PR / Milestones / Sub-issues / Projects v2 / Discussions / Actions / repo files / CODEOWNERS) 단일 backend화. Story 페이지 → `docs/stories/<KEY>.md` single-file SSOT. ADR → `docs/adr/ADR-NNN-<slug>.md` flat. Domain KB → `docs/domain-knowledge/<area>/<topic>.md` 계층. 1 Story = 2 PRs (Phase 1 docs / Phase 2 code+docs append). 6 GitHub Actions 자동화 (story-init / phase-label-invariant / story-section-1-immutable / subissue-from-impl-manifest / phase-gate-mergeable / fix-ledger-sync). 보안 테스트 1차 layer = Dependabot/CodeQL/Secret Scanning/Push Protection. project.yaml schema `atlassian.*` → `github.*`. `gh` CLI 필수 추가, `github@claude-plugins-official` 플러그인 필수 격상.
- 2026-04-26: **v9 Review/Test 워커 통합 (BREAKING)** — [ADR-001](../docs/adr/ADR-001-review-agent-unification.md). 3 lane × 2 vendor = 6 워커(Claude/Codex × Design/Code/Security)를 lane-agnostic 2 워커(`ClaudeReviewAgent` / `CodexReviewAgent`)로 통합. 도메인은 호출 PL이 review packet으로 주입(checklist_path · scope_globs · category_enum · severity_overrides). 공통 base SSOT = `templates/review-pl-base.md`, 체크리스트 SSOT = `templates/review-checklists/{design,code,security}.md`. 25 → **20 core agents**. SecurityTestPL에 `Bash(gh api repos/*)` 권한 부여(1차 layer alerts fetch). 워커 packet 누락 시 `ESCALATE_PACKET_INCOMPLETE` 강제 — generic fallback 금지.

본 playbook은 에이전트 구조·규약 변경 시 PR과 함께 갱신. git log로 변경 추적.
