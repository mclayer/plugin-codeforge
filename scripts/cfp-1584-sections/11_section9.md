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

**CFP-1302 추가 (phase-gate-auto-cleanup.yml + multi-gate explicit shape)**: phase 전환 시 prior gate label 자동 cleanup 은 신규 workflow `templates/github-workflows/phase-gate-auto-cleanup.yml` (CFP-1302 / CFP-604 retro F6 Wave 2) 가 담당 (SRP 분리, `phase-gate-mergeable.yml` 와 concurrency.group namespace 분리). multi-gate `required` shape = `{phase, gates: string[]}` array (semantic 변경 0, syntactic 강화 — `every()` AND invariant + B-1 empty-array fail-loud guard). `liveEntryOk` 별 변수 보존 (ADR-030 conditional gate semantics — `required.gates[]` unconditional array semantics 와 axis disjoint, CFP-1302 D-1 결정).

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

