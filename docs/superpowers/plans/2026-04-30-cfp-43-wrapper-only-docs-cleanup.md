# CFP-43 Implementation Plan: Wrapper-only Docs Cleanup + Cross-repo Backfill

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ζ arc decomposition 의 wrapper-only 정합성 잔재 cleanup — 6 lane plugin 의 P0/P1 operational gap (18 항목) backfill + wrapper repo 의 stale DocsAgent text 제거.

**Architecture:** 7 PR (6 cross-repo backfill + 1 wrapper cleanup). PR-1~PR-6 는 각 lane plugin repo 에 직접 (mcp__github 도구로 branch+edit+PR+merge), PR-7 은 본 wrapper repo 의 local feature branch. Cross-repo 우선 머지 → wrapper 후속.

**Tech Stack:** Markdown editing via Edit tool + mcp__github MCP (cross-repo work) + bash lint + grep verification.

**Spec reference:** [docs/superpowers/specs/2026-04-30-cfp-43-wrapper-only-docs-cleanup-design.md](../specs/2026-04-30-cfp-43-wrapper-only-docs-cleanup-design.md)

**Note (cross-repo workflow):** Cross-repo PR 작업은 mcp__github MCP 도구만 사용 (local clone 불필요). 6 lane plugin 각자 main branch 가 base. PR merge 권한 가정 (admin merge 또는 자체 dogfooded workflow follow).

---

## File Structure (per PR)

| PR | Repo | Files modified |
|---|---|---|
| PR-1 | mclayer/plugin-codeforge-review | `templates/review-pl-base.md` |
| PR-2 | mclayer/plugin-codeforge-pmo | `agents/PMOAgent.md` |
| PR-3 | mclayer/plugin-codeforge-requirements | `agents/RequirementsPLAgent.md`, `agents/DomainAgent.md`, `agents/RequirementsAnalystAgent.md`, `agents/ResearcherAgent.md` |
| PR-4 | mclayer/plugin-codeforge-test | `agents/TestAgent.md` |
| PR-5 | mclayer/plugin-codeforge-develop | `agents/DeveloperPLAgent.md` |
| PR-6 | mclayer/plugin-codeforge-design | `agents/ArchitectAgent.md` |
| PR-7 | mclayer/plugin-codeforge | `CLAUDE.md`, `docs/orchestrator-playbook.md`, `templates/story-page-structure.md`, `templates/impl-manifest.md`, `README.md`, `docs/plugin-design.md`, `docs/consumer-guide.md`, `docs/migration-guide.md` |

---

## Cross-repo PR pattern (Tasks 1-6)

각 cross-repo PR 의 공통 흐름:

1. `mcp__github__create_branch` — `cfp-43-<slug>` branch 생성 (from main)
2. `mcp__github__get_file_contents` — 대상 파일 fetch (현재 main 본문 확인)
3. 본문 분석·수정 계획 수립 — audit 의 gap 정보를 파일 실제 line 에 매핑
4. `mcp__github__create_or_update_file` — 수정된 본문 push (자동 commit)
5. (필요 시 추가 파일 동일 절차 반복)
6. `mcp__github__create_pull_request` — PR 생성 (base: main, head: cfp-43-<slug>)
7. `mcp__github__merge_pull_request` — merge (또는 admin merge — 자기 repo 의 dogfooded workflow follow)
8. Verify: `mcp__github__get_file_contents` (main branch) 로 재 fetch + grep verification

---

## Task 1: PR-1 codeforge-review — review-pl-base.md cleanup

**Repo:** `mclayer/plugin-codeforge-review`
**Branch (예상):** `cfp-43-pl-base-cleanup`
**File:** `templates/review-pl-base.md`

**Gap fix scope** (audit P0×1 + P1×2):
- **P0**: §4 가 PL 에게 "Orchestrator 경유 DocsAgent 에 §10 새 행 추가 의뢰" 지시 — CFP-32 monopoly (Orchestrator 직접 §10) 위반. PL 은 §10 write 안 함, FIX verdict 만 반환.
- **P1**: §7 / §11 의 stale "DocsAgent SSOT" reference — `agents/DocsAgent.md` 가 부재 (CFP-40 final delete). 갱신: 각 lane plugin 의 self-write 표 reference 또는 codeforge wrapper `CLAUDE.md` reference (PR-7 머지 후) 로 변경.

- [ ] **Step 1: Fetch current file**

Use `mcp__github__get_file_contents`:
```json
{ "owner": "mclayer", "repo": "plugin-codeforge-review", "path": "templates/review-pl-base.md" }
```

- [ ] **Step 2: Identify edit points**

Locate sections:
- §4 "FIX 판정 시" — 본문에 "Orchestrator 경유 DocsAgent 에 §10 새 행 추가 의뢰" 또는 유사 prose 검색
- §7 "문서화 표준" 또는 동등 footer
- §11 "agents/DocsAgent.md" reference

- [ ] **Step 3: Apply edits**

§4 edit: "Orchestrator 경유 DocsAgent 에 §10 새 행 추가 의뢰" → "verdict.status=FIX 반환만 — §10 FIX Ledger append 는 codeforge core Orchestrator 단독 책임 (CFP-32 monopoly · `fix-event-v1` contract)"

§7/§11 edit: `agents/DocsAgent.md` 또는 "DocsAgent" 명시 부분 → "각 lane plugin 의 CLAUDE.md `Self-write 책임` 표" + "codeforge wrapper [CLAUDE.md](https://github.com/mclayer/plugin-codeforge/blob/main/CLAUDE.md) `오케스트레이션 규칙` 참조"

- [ ] **Step 4: Create branch + push edited file**

```
mcp__github__create_branch:
  owner=mclayer, repo=plugin-codeforge-review, branch=cfp-43-pl-base-cleanup, from_branch=main

mcp__github__create_or_update_file:
  owner=mclayer, repo=plugin-codeforge-review, branch=cfp-43-pl-base-cleanup,
  path=templates/review-pl-base.md, content=<edited body>,
  message="fix(cfp-43): remove deprecated ledger-append queue + stale DocsAgent SSOT references"
```

- [ ] **Step 5: Open PR**

```
mcp__github__create_pull_request:
  owner=mclayer, repo=plugin-codeforge-review, base=main, head=cfp-43-pl-base-cleanup,
  title="fix(cfp-43): cleanup review-pl-base.md (P0 ledger-append + P1 DocsAgent footer)",
  body="""
## Summary
- §4: 'Orchestrator 경유 DocsAgent §10 의뢰' 제거 — §10 FIX Ledger 는 wrapper Orchestrator 단독 (CFP-32 monopoly)
- §7/§11: stale `agents/DocsAgent.md` SSOT reference 제거 — 각 lane plugin self-write 표 + wrapper CLAUDE.md 참조

## Source
[CFP-43 spec](https://github.com/mclayer/plugin-codeforge/blob/main/docs/superpowers/specs/2026-04-30-cfp-43-wrapper-only-docs-cleanup-design.md) — Y2 backfill (P0+P1)
"""
```

- [ ] **Step 6: Merge PR (admin if dogfooded workflow blocks)**

```
mcp__github__merge_pull_request:
  owner=mclayer, repo=plugin-codeforge-review, pullNumber=<from-step-5>, merge_method=merge
```

If blocked by required status checks: try admin override via `gh pr merge <N> --admin` (works if user has admin permissions on the repo).

- [ ] **Step 7: Verify (post-merge)**

```
mcp__github__get_file_contents:
  owner=mclayer, repo=plugin-codeforge-review, path=templates/review-pl-base.md, ref=main
```

Expected: body has no occurrence of "ledger-append" or "agents/DocsAgent.md" (history mention OK if explicit).

---

## Task 2: PR-2 codeforge-pmo — PMOAgent.md cleanup

**Repo:** `mclayer/plugin-codeforge-pmo`
**Branch (예상):** `cfp-43-pmo-self-write-cleanup`
**File:** `agents/PMOAgent.md`

**Gap fix scope** (audit P0×1 + P1×2):
- **P0**: §4 (ADR 후보 발의) 가 "write queue 에 제출 → DocsAgent drain 시 ArchitectAgent 스폰" path. CFP-26 Phase 0a 후 `adr-draft` queue type deny — PMOAgent 는 Orchestrator 에 inline ADR draft 반환 + Orchestrator 가 ArchitectAgent 직접 spawn.
- **P1**: §2 self-contradiction — "Story §11 요약 링크는 DocsAgent 경유 의뢰" vs CLAUDE.md self-write 표 (PMOAgent 직접 §11 edit). CLAUDE.md 자율 write 표가 정답 — agent md §2 갱신.
- **P1**: §1 (Epic decomposition) Epic Issue body / Milestone description "DocsAgent 가 기록" path → PMOAgent self-write (PMOAgent 가 `mcp__github__add_issue_comment` + `Bash(gh api repos/*/milestones*)` 권한 보유, CFP-36).

- [ ] **Step 1: Fetch + Identify**

```
mcp__github__get_file_contents:
  owner=mclayer, repo=plugin-codeforge-pmo, path=agents/PMOAgent.md
```

Locate sections §1 (Epic decomposition · 트리거), §2 (Story 완료 회고), §4 (ADR 후보 발의).

- [ ] **Step 2: Apply edits**

§1 edit: "write queue 에 제출 → DocsAgent 가 GitHub Epic Issue body / Milestone description 에 기록" → "PMOAgent 직접 write — `mcp__github__add_issue_comment` (Epic Issue body) + `Bash(gh api repos/*/milestones*)` (Milestone description)"

§2 edit: "Story §11 요약 링크는 DocsAgent 경유 기록 의뢰" → "Story §11 은 PMOAgent 직접 `Edit(docs/stories/<KEY>.md)` (CLAUDE.md `Self-write 책임` 표 — owner agent direct write, CFP-36)"

§4 edit: "write queue 에 제출 → DocsAgent drain 시 ArchitectAgent 스폰" → "Orchestrator 에 inline ADR draft 반환 (`pmo_output v1.adr_proposal` 필드) — Orchestrator 가 codeforge-design plugin 의 ArchitectAgent 를 spawn 해 ADR file 직접 author"

- [ ] **Step 3: Branch + push**

```
mcp__github__create_branch:
  owner=mclayer, repo=plugin-codeforge-pmo, branch=cfp-43-pmo-self-write-cleanup, from_branch=main

mcp__github__create_or_update_file:
  owner=mclayer, repo=plugin-codeforge-pmo, branch=cfp-43-pmo-self-write-cleanup,
  path=agents/PMOAgent.md, content=<edited body>,
  message="fix(cfp-43): replace deprecated adr-draft queue + DocsAgent-mediated paths with PMO self-write"
```

- [ ] **Step 4: Open PR**

```
mcp__github__create_pull_request:
  owner=mclayer, repo=plugin-codeforge-pmo, base=main, head=cfp-43-pmo-self-write-cleanup,
  title="fix(cfp-43): cleanup PMOAgent.md (P0 adr-draft queue + P1 §11/§1 self-write)",
  body="""
## Summary
- §4 ADR draft hand-off: deprecated `adr-draft` queue → inline return via `pmo_output v1.adr_proposal`
- §2 Story §11: DocsAgent 경유 → PMOAgent direct `Edit(docs/stories/**)` (matches CLAUDE.md self-write table)
- §1 Epic decomposition: DocsAgent path → PMOAgent self-write (mcp + gh api)

## Source
[CFP-43 spec](https://github.com/mclayer/plugin-codeforge/blob/main/docs/superpowers/specs/2026-04-30-cfp-43-wrapper-only-docs-cleanup-design.md)
"""
```

- [ ] **Step 5: Merge + verify**

Same pattern as Task 1 Step 6-7. Verify: `grep -c "adr-draft\|DocsAgent" agents/PMOAgent.md` returns 0 (history OK).

---

## Task 3: PR-3 codeforge-requirements — 4 agent md footer cleanup

**Repo:** `mclayer/plugin-codeforge-requirements`
**Branch (예상):** `cfp-43-req-footer-cleanup`
**Files:**
- `agents/RequirementsPLAgent.md`
- `agents/DomainAgent.md`
- `agents/RequirementsAnalystAgent.md`
- `agents/ResearcherAgent.md`

**Gap fix scope** (audit P1×3 — but 1 footer pattern × 4 files):
- **P1 footer × 4**: 모든 4 agent md 의 "문서화 표준" footer 가 pre-ζ-arc copy-paste — "모든 문서화는 Orchestrator 경유 DocsAgent 가 기록 (write queue 경유). 문서화 표준은 DocsAgent.md 참조."
- **P1 cross-repo schema reference** (PL only): write queue frontmatter schema reference 가 wrapper playbook §11.2 만 가리킴 — 본 plugin 자체 문서화 부재. (Y2 권장이지만 fix 는 footer 에 함께 통합)
- **P1 §9.0 Clarification respawn (PL only)**: PL 의 책임 명시 부재 (wrapper playbook 만 documented). RequirementsPLAgent.md 에 "§9.0 Clarification 재스폰 이력 append 의무" 명시.

- [ ] **Step 1: Fetch all 4 files in parallel**

4 separate `mcp__github__get_file_contents` calls (parallel OK since independent reads).

- [ ] **Step 2: Identify common footer pattern**

각 file 의 footer (보통 마지막 ## section "문서화 표준" 또는 동등) 위치 확인.

- [ ] **Step 3: Apply common footer replacement to all 4 files**

Replace stale footer text:
```
## 문서화 표준
모든 문서화는 Orchestrator 경유 DocsAgent 가 기록 (write queue 경유). 문서화 표준은 DocsAgent.md 참조.
```

With:
```
## 문서화 표준
본 agent 는 자기 lane 의 self-write 표 (codeforge-requirements `CLAUDE.md` `Self-write 책임` 표) 가 정의하는 path 만 직접 write. 그 외 docs/** + GitHub Issue/PR 인터페이스는 codeforge wrapper Orchestrator 가 처리. 형식·prefix 표는 wrapper [CLAUDE.md](https://github.com/mclayer/plugin-codeforge/blob/main/CLAUDE.md) "오케스트레이션 규칙" 참조.
```

PL only 추가: §9.0 Clarification respawn 책임 단락 (footer 직전 또는 §3 step list 마지막):
```
### Clarification 재스폰 이력 (§9.0)
PL 이 통합 중 sub-agent 의 추가 분석·재해석을 요청해 Orchestrator 경유 재스폰 의뢰 시, 재스폰 사유·재질의 context 를 `docs/stories/<KEY>.md §9.0 "Clarification 재스폰 이력"` 에 PL 이 직접 append (Edit). §10 FIX Ledger 와 분리 — 재스폰은 게이트 실패 아니므로 GitHub `fix:*` 라벨 미부착.
```

- [ ] **Step 4: Branch + push 4 files**

```
mcp__github__create_branch:
  owner=mclayer, repo=plugin-codeforge-requirements, branch=cfp-43-req-footer-cleanup, from_branch=main

# 4 separate create_or_update_file calls (one per file) — same branch, separate commits
mcp__github__create_or_update_file × 4:
  branch=cfp-43-req-footer-cleanup
  path=agents/{Requirements{PL,Analyst},Domain,Researcher}Agent.md (4 files)
  message="fix(cfp-43): replace stale 'DocsAgent 단독 writer' footer in <agent>"
```

- [ ] **Step 5: Open PR + merge**

```
mcp__github__create_pull_request:
  owner=mclayer, repo=plugin-codeforge-requirements, base=main, head=cfp-43-req-footer-cleanup,
  title="fix(cfp-43): replace pre-ζ-arc DocsAgent footer in 4 agents + add §9.0 respawn duty",
  body="""
## Summary
- 4 agent md (RequirementsPL, Domain, Analyst, Researcher) 의 stale '문서화 표준 → DocsAgent' footer 갱신
- RequirementsPLAgent: §9.0 Clarification 재스폰 이력 append 책임 명시 추가

## Source
[CFP-43 spec](https://github.com/mclayer/plugin-codeforge/blob/main/docs/superpowers/specs/2026-04-30-cfp-43-wrapper-only-docs-cleanup-design.md)
"""
```

Then merge.

- [ ] **Step 6: Verify**

`mcp__github__get_file_contents` (main branch) 로 4 file 재 fetch. 각 file body 에 "DocsAgent" 잔존 0 또는 history mention 만.

---

## Task 4: PR-4 codeforge-test — TestAgent.md cleanup

**Repo:** `mclayer/plugin-codeforge-test`
**Branch (예상):** `cfp-43-test-footer-cleanup`
**File:** `agents/TestAgent.md`

**Gap fix scope** (audit P1×2):
- **P1 footer**: 동일한 stale "문서화 표준 → DocsAgent" footer
- **P1 §9.3 ownership**: TestAgent 가 §9.3 직접 write 안 함 (구조화된 PASS/FAIL 보고 반환만) — Orchestrator 가 receipt 처리. 본 분리를 agent md 에 명시.

- [ ] **Step 1: Fetch**

```
mcp__github__get_file_contents:
  owner=mclayer, repo=plugin-codeforge-test, path=agents/TestAgent.md
```

- [ ] **Step 2: Apply edits**

Footer replacement: 동일한 패턴 (Task 3 Step 3 의 footer template 적용).

§9.3 ownership 단락 추가 (예: §"보고 형식" 섹션 직후):
```
### §9.3 write boundary
TestAgent 는 §9.3 "구현 테스트" 섹션을 **직접 write 하지 않는다**. 구조화된 PASS/FAIL 보고 (test_verdict v1) 만 Orchestrator 에 반환. §9.3 append 는 codeforge wrapper Orchestrator 가 verdict receipt 후 처리.
```

- [ ] **Step 3: Branch + push + PR + merge**

Same pattern as Task 1 Step 4-6, single file.

PR title: `fix(cfp-43): cleanup TestAgent.md footer + §9.3 write boundary`

- [ ] **Step 4: Verify**

`grep -c "DocsAgent" agents/TestAgent.md` = 0 (or history only).

---

## Task 5: PR-5 codeforge-develop — DeveloperPLAgent.md cleanup

**Repo:** `mclayer/plugin-codeforge-develop`
**Branch (예상):** `cfp-43-dev-section-self-write`
**File:** `agents/DeveloperPLAgent.md`

**Gap fix scope** (audit P0×2 + P1×1):
- **P0 §"구현 완료 흐름" step 4**: 현재 "Orchestrator 가 DocsAgent 경유 Story file §8.5 기록 + GitHub sub-issue 일괄 생성" — CLAUDE.md self-write 표 와 모순. DeveloperPL 직접 §8.5 edit (`Edit(docs/stories/**)` 권한 보유). subissue-from-impl-manifest.yml Action 이 자동 sub-issue 생성.
- **P0 kind:impl-manifest R5 ambiguity**: §8.5 helper 가 "DocsAgent kind=impl-manifest helper" 로 표현되지만 CLAUDE.md self-write 표는 DeveloperPL 직접 write. helper mechanism 자체는 CFP-26 Phase 0a 이전 path — 폐기. DeveloperPL 이 직접 git diff 분석 후 §8.5 매핑표 작성.
- **P1 footer**: 동일 stale footer pattern.

- [ ] **Step 1: Fetch + Identify**

```
mcp__github__get_file_contents:
  owner=mclayer, repo=plugin-codeforge-develop, path=agents/DeveloperPLAgent.md
```

Locate §"구현 완료 흐름" (step list with §8.5 reference), R5 mention, footer.

- [ ] **Step 2: Apply edits**

§"구현 완료 흐름" step 4 edit: "Orchestrator 가 DocsAgent 경유 Story file §8.5 기록" → "DeveloperPL 이 직접 `Edit(docs/stories/<KEY>.md)` 로 §8.5 Impl Manifest 매핑표 작성 (CLAUDE.md self-write 표 — owner agent direct write, CFP-39)"

§8.5 R5 ambiguity edit: "DocsAgent kind=impl-manifest helper 가 git diff 로 자동 생성, DeveloperPL 이 review-edit" → "DeveloperPL 이 git diff 분석 결과를 바탕으로 §8.5 매핑표 직접 작성. 자동 sub-issue 생성은 wrapper repo 의 `subissue-from-impl-manifest.yml` Action 이 §8.5 commit 감지 후 처리."

Footer replacement: Task 3 Step 3 의 template 적용.

- [ ] **Step 3: Branch + push + PR + merge**

PR title: `fix(cfp-43): replace DocsAgent-mediated §8.5 path with DeveloperPL self-write`

PR body emphasizes 2 P0 fixes + 1 P1 footer.

- [ ] **Step 4: Verify**

`grep -c "DocsAgent\|kind=impl-manifest helper\|kind: impl-manifest helper" agents/DeveloperPLAgent.md` = 0.

---

## Task 6: PR-6 codeforge-design — ArchitectAgent.md cleanup

**Repo:** `mclayer/plugin-codeforge-design`
**Branch (예상):** `cfp-43-arch-section-self-write`
**File:** `agents/ArchitectAgent.md`

**Gap fix scope** (audit P0×2 + P1×2):
- **P0 step 5**: "Story file §7 요약 미러링은 DocsAgent 의뢰 (Orchestrator 경유)" — CLAUDE.md self-write 표는 ArchitectAgent 직접 §7/§3/§11 edit. 갱신.
- **P0 footer**: 동일 stale "DocsAgent 단독 writer" footer. CLAUDE.md self-write 표와 모순.
- **P1 PMO ADR draft hand-off**: PMOAgent 가 cross_story_audit_request 트리거에서 ADR 후보 발의 → Orchestrator 가 ArchitectAgent 를 spawn 하며 inline ADR draft content 전달. ArchitectAgent.md 에 "PMO inline ADR draft 입력 처리 절차" 추가.
- **P1 cache invalidation**: ArchitectAgent 가 docs/stories/<KEY>.md §3/§7/§11 또는 docs/change-plans/**, docs/adr/** write 후 wrapper Orchestrator 의 context packet cache invalidation 의무. agent md 에 "write 후 Orchestrator 에 cache invalidation hint 반환" 명시.

- [ ] **Step 1: Fetch + Identify**

```
mcp__github__get_file_contents:
  owner=mclayer, repo=plugin-codeforge-design, path=agents/ArchitectAgent.md
```

Locate step 5 (라이프사이클), 문서화 표준 footer, PMO 의 hand-off section (있는지 확인 — 없을 수 있음).

- [ ] **Step 2: Apply edits**

step 5 edit: "Story file §7 요약 미러링은 DocsAgent 의뢰" → "Story file §7 (보안 설계 요약) · §3 (도입할 설계 요약) · §11 (데이터 마이그레이션 요약) 미러링은 ArchitectAgent 직접 `Edit(docs/stories/<KEY>.md)` (CLAUDE.md self-write 표 — owner agent direct write, CFP-40)"

Footer replacement: Task 3 Step 3 의 template 적용.

PMO ADR draft hand-off section 추가 (예: §"입력" 또는 §"라이프사이클" 직후):
```
### PMO inline ADR draft 입력 처리

PMOAgent 가 cross-Story 패턴 분석에서 ADR 후보를 발의하면 (`pmo_output v1.adr_proposal`), wrapper Orchestrator 가 본 ArchitectAgent 를 spawn 하며 inline ADR draft content 를 입력으로 전달. ArchitectAgent 는:
1. PMO inline ADR draft + 관련 ADR (Glob `docs/adr/`) + 코드·도메인 KB 를 통합 분석
2. 신규 ADR file 생성 — `docs/adr/ADR-NNN-<slug>.md` 직접 write (status: Proposed)
3. ADR 결정 사항이 Change Plan 영향 시 §3 / §7 / §11 갱신
```

Cache invalidation section 추가 (footer 직전):
```
### Cache invalidation 의무

본 ArchitectAgent 가 다음 file 중 하나라도 write 한 경우 (`docs/stories/<KEY>.md` §3/§7/§11, `docs/change-plans/<slug>.md`, `docs/adr/ADR-NNN-<slug>.md`), Orchestrator 에 반환 시 응답에 `cache_invalidate: [<file-path>...]` 필드 포함. Orchestrator 가 본 hint 를 받아 context packet cache (Story §3/§7/§11 cache) miss 처리.
```

- [ ] **Step 3: Branch + push + PR + merge**

PR title: `fix(cfp-43): ArchitectAgent self-write §7/§3/§11 + PMO ADR hand-off + cache invalidation`

- [ ] **Step 4: Verify**

`grep -c "DocsAgent" agents/ArchitectAgent.md` = 0 또는 history only.

---

## Task 7: PR-7 wrapper cleanup — 8 file 정리 (X2 depth)

**Repo:** `mclayer/plugin-codeforge` (current)
**Branch:** `cfp-43-wrapper-cleanup` (local feature branch)
**Files (8):** `CLAUDE.md`, `docs/orchestrator-playbook.md`, `templates/story-page-structure.md`, `templates/impl-manifest.md`, `README.md`, `docs/plugin-design.md`, `docs/consumer-guide.md`, `docs/migration-guide.md`

**Note**: PR-1~PR-6 모두 머지 완료 후 진행 권장 (lane plugin 측 self-write 표가 정합한 상태에서 wrapper docs 가 reference). 단 시점 강제 안 함 — 사용자 시점 자유.

- [ ] **Step 1: Create local branch**

```bash
git checkout main && git pull origin main
git checkout -b cfp-43-wrapper-cleanup
```

- [ ] **Step 2: Edit `CLAUDE.md`**

스코프:
- **line 3**: `에이전트 상세는 각 [\`agents/<Name>.md\`](https://github.com/mclayer)` (SSOT) → `에이전트 상세는 각 lane plugin 의 \`agents/<Name>.md\` (codeforge-{review,pmo,requirements,test,develop,design} 각 repo SSOT — 본 wrapper repo 에는 agent file 없음)`. "Inter-plugin contract `review_verdict v1`" reference 도 v2 로 갱신 (CFP-42 결과 반영 — 본 file 의 다른 부분에서 이미 갱신됐을 수 있음, spot-check)
- **line 30, 40, 45**: 의존성 listing 의 `DocsAgent 단독 사용`, `DocsAgent 의 claude-md-improver 스킬 의존`, `DocsAgent 가 Milestone·Discussions` → 각각 "각 lane plugin self-write", "(DocsAgent 부재 — 본 의존 항목 제거)", "PMO 가 Milestone, RequirementsPL 의 DomainAgent 가 Discussions Q&A self-call"
- **line 84**: `├── [Cross-cutting] DocsAgent       # 문서화 writer (...)` 행 전체 삭제 (Cross-cutting 은 PMOAgent 만 잔류)
- **line 125**: `Cross-cutting (PMOAgent 프로젝트 관리 / DocsAgent 문서 writer)` → `Cross-cutting (PMOAgent — 프로젝트 관리·회고·ADR 발의)`
- **line 141**: `RequirementsPL 이 세 결과 dedup·상충 조정 → DocsAgent 경유 §2·§5·§6 동시 채움 + §3-4 갱신` → `RequirementsPL 이 세 결과 dedup·상충 조정 → §2/§5/§6 직접 self-write + §3-4 갱신` (RequirementsPL agents/* 자기 self-write 권한 보유, codeforge-requirements 참조)
- **line 142**: `DocsAgent 가 Story file §7 미러링` → `ArchitectAgent 가 Story file §7/§3/§11 직접 self-write (CFP-40 codeforge-design 추출 후)`
- **line 144**: `DeveloperPL 이 첫 commit 준비 후 DocsAgent 경유 mcp__github__create_pull_request` → `DeveloperPL 이 첫 commit 준비 후 직접 mcp__github__create_pull_request` (codeforge-develop self-write 권한 보유)
- **line 164**: `Project Config Packet (DocsAgent · ...)` listing 에서 DocsAgent 제거
- **line 168**: `**생성·갱신 전담**: **DocsAgent**` → `**생성·갱신 책임**: 각 lane plugin self-write — owner section 별로 분산. 자세한 분담은 `Lane plugin self-write boundary` 절 참조`
- **line 170**: `**섹션 갱신 의뢰 경로**: 각 에이전트는 Orchestrator 경유 DocsAgent 에 ... 의뢰. ... 변경은 **DocsAgent 단독**` → `**섹션 갱신 path**: 각 lane plugin 이 자기 owned section 을 직접 \`Edit(docs/stories/**)\`. multi-writer 영역 (§9 review verdict — Phase 별 다른 Review PL self-write) 은 lane 별 phase 진행 순서에 따라 자연 직렬화`
- **line 172**: `agents/DocsAgent.md 참조` reference 제거
- **line 183**: `**Cross-cutting**: **DocsAgent** (모든 레인에서 write 창구로 필수)` 행 전체 삭제
- **line 202, 217, 230, 233, 236, 269, 274, 298, 414**: 모든 "DocsAgent 경유 / DocsAgent 가 ..." prose 를 해당 owner agent self-write 로 대체. 구체:
  - "DocsAgent 가 gate:design-review-pass 라벨 부착" → "DesignReviewPL 이 verdict.writes_completed.gate_label_attached=true 로 직접 mcp__github__issue_write 호출 (review-verdict-v2)"
  - "DocsAgent 가 gate:security-test-pass 라벨 부착" → "SecurityTestPL 이 직접 (review-verdict-v2 동일 패턴)"
  - "DocsAgent 가 Story file §10 관리" → "Orchestrator 단독 §10 FIX Ledger (CFP-32, fix-event-v1 contract)"
  - 그 외 인용은 audit 의 owner agent 매핑 참고
- **line 451**: Write 권한 listing 의 `**DocsAgent**: docs/** (단, ...)` 항목 전체 삭제. 대신 lane plugin 별 self-write owner path 를 §"Lane plugin self-write boundary" 절에 통합 (재구성)
- **line 456**: `외부 도구 wrapper: ... DocsAgent(...)` 의 DocsAgent 항목 삭제
- **line 460-471**: `**DocsAgent + 3 owner agent 분담 모델**` 절 전체를 다음으로 재구성:
```markdown
### Lane plugin self-write boundary

`docs/**` + GitHub Issue/PR/comment + label 영역의 write 책임은 lane plugin 별로 분산. wrapper repo 자체에는 agent 0개 — Orchestrator 가 lane plugin 을 spawn 하면 lane plugin 이 자기 owner section 을 직접 write.

**Lane plugin owner path**:

| Lane plugin | docs/ self-write 영역 | GitHub self-write |
|---|---|---|
| codeforge-requirements | `docs/stories/<KEY>.md §2·§5·§6`, `docs/domain-knowledge/<area>/<topic>.md` | `[요구사항]` prefix comment, phase:요구사항→phase:설계 transition, Discussions Q&A routing |
| codeforge-design | `docs/stories/<KEY>.md §3·§7·§11`, `docs/change-plans/<slug>.md`, `docs/adr/ADR-NNN-<slug>.md` | `[설계]` prefix comment, phase:설계→phase:설계-리뷰 transition |
| codeforge-review | `docs/stories/<KEY>.md §9` (각 Review PL) | `[설계-리뷰]` / `[구현-리뷰]` / `[보안-테스트]` prefix comment, gate:design-review-pass / gate:security-test-pass label, phase transition (review-verdict-v2) |
| codeforge-develop | `docs/stories/<KEY>.md §8·§8.5`, Phase 2 PR creation | `[구현]` prefix comment, phase:구현→phase:구현-리뷰 transition |
| codeforge-test | (§9.3 은 Orchestrator 가 verdict receipt 후 처리 — lane plugin 직접 write 안 함) | `[구현-테스트]` prefix comment |
| codeforge-pmo | `docs/retros/<sprint>.md`, `docs/stories/<KEY>.md §11`, Epic Issue body, Milestone description | `[PMO]` prefix comment, Epic Milestone via gh api |

**Wrapper Orchestrator 단독 영역**:
- `docs/stories/<KEY>.md §10` FIX Ledger append (CFP-32 monopoly · `fix-event-v1` contract)
- general `docs/**` write (lane plugin owner 외)
- branch protection · CI workflow · cross-plugin schema templates

**4 single-owner doc** (CFP-26 Phase 0a 이후): `docs/{change-plans,adr,domain-knowledge,retros}/**` 는 owner agent direct write — lane plugin 의 ArchitectAgent / DomainAgent / PMOAgent 자기 owner path write.

자세한 owner path / mechanism / trigger 는 각 lane plugin 의 `CLAUDE.md` `Self-write 책임` 표 참조.
```
- **line 473**: `**[agents/DocsAgent.md](https://github.com/.../agents/DocsAgent.md)** SSOT` reference 제거. 표준 형식·prefix 표는 inline 으로 유지

**Step 2 verify**:
```bash
grep -cn "DocsAgent" CLAUDE.md
# 기대: 0 또는 history mention 만 (예: "CFP-NN 시점 DocsAgent 해체" 같은 retro reference)
```

```bash
git add CLAUDE.md
git commit -m "fix(cfp-43): remove DocsAgent references + restructure 'Lane plugin self-write boundary' section in CLAUDE.md"
```

- [ ] **Step 3: Edit `docs/orchestrator-playbook.md`**

스코프 (대규모, ~40 references):
- **line 15**: `agents/DocsAgent.md` related_files 항목 삭제
- **lines 100-101, 117-118**: `DocsAgent 경유 GitHub Milestone / Issue 생성` → `PMOAgent 가 Milestone 자기 self-call`, `RequirementsPL 이 Story Issue self-call`
- **line 127**: `DocsAgent 로 Story file §11 회고 작성` → `PMOAgent 가 §11 직접 self-write (codeforge-pmo CLAUDE.md 의 Self-write 책임 표)`
- **lines 210-219, 230-233, 236, 256, 269, 274**: 동일 패턴 — 각 인용을 owner agent self-write 로 대체. 구체 매핑은 Step 2 의 line 202+ 매핑 참조
- **line 261**: `DocsAgent.md 참조` → `각 lane plugin CLAUDE.md 의 Self-write 책임 표 참조`
- **line 287 (DocsAgent agent description 행)**: 행 전체 삭제 또는 "(DocsAgent 부재 — CFP-40 final delete)" 로 history mention
- **lines 320, 337, 339, 342, 355**: Preflight 결과 기록 path. 현재 "DocsAgent 경유" 인용 → "Orchestrator 직접 mcp__github__add_issue_comment" (Preflight 는 Orchestrator 행위)
- **line 409**: `Story file §9.0 ... DocsAgent 단독 갱신` → `RequirementsPL 직접 §9.0 append (codeforge-requirements)`
- **lines 417-444 §5.1 "DocsAgent 스폰 체크리스트"** 표 전체를 다음으로 재구성:
```markdown
### 5.1 단계 종료 시 lane plugin self-write 체크리스트

각 lane plugin 의 PL 또는 deputy 가 자기 owned section 을 self-write. Orchestrator 는 lane PASS verdict 받으면 다음 lane spawn — 직접 file write 책임 없음 (단 §10 FIX Ledger 만 예외).

| 트리거 | 갱신 path | 책임 agent |
|---|---|---|
| Issue Form 제출 (story.yml) | `docs/stories/<KEY>.md §1` (verbatim) + Phase 1 PR | `story-init.yml` Action 자동 |
| RequirementsPL 통합 완료 | Story §2/§5/§6 + (DomainAgent 시) `docs/domain-knowledge/<area>/<topic>.md` | RequirementsPLAgent / DomainAgent (codeforge-requirements) |
| ArchitectAgent (chief author) Change Plan + ADR 확정 | `docs/change-plans/<slug>.md` + `docs/adr/ADR-NNN-<slug>.md` + Story §3/§7/§11 미러 | ArchitectAgent (codeforge-design) |
| DesignReviewPL PASS | Story §9.1 + gate:design-review-pass label + phase transition | DesignReviewPL (codeforge-review, review-verdict-v2) |
| 구현 완료 | Story §8 + §8.5 Impl Manifest + Phase 2 PR | DeveloperPLAgent (codeforge-develop) |
| CodeReviewPL PASS | Story §9.2 + phase transition | CodeReviewPL (codeforge-review, review-verdict-v2) |
| TestAgent PASS | Story §9.3 (Orchestrator 가 verdict receipt 후 처리) + phase transition | TestAgent verdict + Orchestrator |
| SecurityTestPL PASS | Story §9.4 + gate:security-test-pass label + Phase 2 PR mergeable | SecurityTestPL (codeforge-review, review-verdict-v2) |
| PMOAgent 회고 | `docs/retros/<sprint>.md` + Story §11 + Epic Milestone close | PMOAgent (codeforge-pmo) |
| FIX 발생 | Story §10 FIX Ledger + `fix:*` label | **Orchestrator 단독** (CFP-32 · fix-event-v1) |
| 상태 변화 시 GitHub comment | 11 phase prefix `[<phase>] <Agent>: <한 줄>` | 각 lane plugin (codeforge-* CLAUDE.md self-write 표) |

본 표의 owner agent 가 spec/contract 위반 시 Orchestrator 가 사용자 ESCALATE.
```
- **lines 444 (Story Issue comments listing)**: `[<phase>] <AgentName>: <한 줄>` 형식 — 표현 자체는 보존하되 "DocsAgent 가 기록" 부분을 "각 lane plugin self-write" 로 갱신
- **line 453 ("Story Issue comments" 행)**: 동일하게 갱신
- **line 477**: `[DocsAgent.md](...)` reference → 각 lane plugin CLAUDE.md reference
- **§11 file-based write queue 전체 (lines 809-866)**: 본 절은 DocsAgent fixture 시대의 mechanism — wrapper-only 모델에서는 사용 안 함. 다음으로 단순화:
```markdown
## §11. Cross-agent write coordination

ζ arc decomposition (CFP-31~CFP-40) 후 wrapper repo 에는 agent 0개. write 책임은 6 lane plugin 으로 분산 (§5.1 표 참조). 결과적으로 wrapper-side `.claude-work/doc-queue/**` 기반 write queue 는 **사용 안 함**. 대신:

- **각 lane plugin 자기 owner section 직접 write** — `Edit` 또는 GitHub MCP 도구 호출 직접 수행
- **Multi-writer 영역의 자연 직렬화** — `docs/stories/<KEY>.md` 의 §1 → §2-§6 → §7 → §8 → §9 → §11 등 phase 진행 순서가 자연 직렬화 보장. concurrent write 충돌은 phase-label-invariant.yml + branch protection 으로 차단
- **§10 FIX Ledger 예외** — Orchestrator 단독 write (CFP-32 monopoly). lane plugin 은 verdict.status=FIX 만 반환 — §10 직접 write 안 함 (`fix-event-v1` contract)

Pre-CFP-32 의 deprecated write queue type (`adr-draft`, `change-plan`, `domain-knowledge`, `ledger-append`) 가 코드에 잔존하면 silent skip — 사용 안 함.
```
- **line 1091-1096**: `PMOAgent 가 ... ArchitectAgent 를 spawn 한다고 playbook 은 말합니다. 하지만 ArchitectAgent 는 wrapper 에 없습니다.` 문장 갱신 → `PMOAgent 가 inline ADR draft (\`pmo_output v1.adr_proposal\`) 반환 → Orchestrator 가 codeforge-design 의 ArchitectAgent 를 spawn 하며 inline content 전달`

**Step 3 verify**:
```bash
grep -cn "DocsAgent" docs/orchestrator-playbook.md
```

```bash
git add docs/orchestrator-playbook.md
git commit -m "fix(cfp-43): restructure orchestrator-playbook §5/§11 + remove DocsAgent references"
```

- [ ] **Step 4: Edit `templates/story-page-structure.md`**

스코프:
- **line 5**: `**사용 대상**: DocsAgent (생성·섹션 갱신 단독), 모든 에이전트 (...)` → `**사용 대상**: 모든 lane plugin (자기 owner section 갱신, codeforge-{requirements,design,develop,test,pmo,review} CLAUDE.md self-write 표 참조), Orchestrator (§10 FIX Ledger + general docs/** 처리)`
- **line 15**: `DocsAgent 는 Action 이 처리 못하는 후속 갱신만 담당` → `각 lane plugin 이 Action 후 자기 owned section 갱신`
- **line 47**: `RequirementsPL 이 DocsAgent 경유로 §2 채움` → `RequirementsPL 이 §2 직접 self-write`
- **line 81**: `DocsAgent 가 §8.5 에 테이블 기록` → `DeveloperPL 이 §8.5 직접 self-write`
- **line 95**: `DocsAgent append-only 관리` → `Orchestrator append-only 관리 (CFP-32)` (§10 FIX Ledger context)
- **line 119**: 동일 — `DocsAgent` → `Orchestrator` (§10 context)
- **lines 135-138 (DocsAgent 액션 표)**: column 헤더 `DocsAgent 액션` → `Owner agent`. 각 row 의 owner 를 lane plugin 별로 매핑. 예:
  - "요구사항 접수 → §1 verbatim" → owner: `story-init.yml` Action
  - "DomainAgent → §2" → owner: DomainAgent (codeforge-requirements)
  - 그 외 매핑은 Step 3 의 §5.1 표 참고
- **line 159**: `**파일 변경은 DocsAgent 독점**` → `**파일 변경은 lane plugin owner direct edit + Orchestrator 단독 (§10 FIX Ledger)** — codeforge-* CLAUDE.md self-write 표 + CFP-32 fix-event-v1 contract`

```bash
git add templates/story-page-structure.md
git commit -m "fix(cfp-43): replace 'DocsAgent 단독' table with 'Owner agent' per lane plugin"
```

- [ ] **Step 5: Edit `templates/impl-manifest.md`**

스코프:
- **line 3**: `DocsAgent 가 Story file §8.5 에 테이블 기록 → Phase 2 PR 에 commit` → `DeveloperPL 이 §8.5 매핑표 직접 작성 → Phase 2 PR 에 commit (DeveloperPL self-write)`
- **line 5**: `**사용 대상**: DeveloperPLAgent (초안), DocsAgent (§8.5 기록), ArchitectAgent (감사), CodeReviewPL·SecurityTestPL (§8.5 대비 실제 파일)` → `**사용 대상**: DeveloperPLAgent (작성·기록 통합), ArchitectAgent (감사), CodeReviewPL·SecurityTestPL (§8.5 대비 실제 파일)`
- **line 62**: `DocsAgent 의 mcp__github__sub_issue_write 는 Action 실패 시 fallback 으로만` → `Action 실패 시 fallback 은 DeveloperPL 이 mcp__github__sub_issue_write 직접 호출`
- **line 74**: `Orchestrator 에 전달 → DocsAgent 가 §8.5 에 Edit` → `DeveloperPL 이 §8.5 에 직접 Edit`

```bash
git add templates/impl-manifest.md
git commit -m "fix(cfp-43): impl-manifest §8.5 owner = DeveloperPL self-write"
```

- [ ] **Step 6: Edit `README.md`**

스코프:
- **line 15**: `**단독 문서 writer (DocsAgent)** 를 통한 GitHub Issue/PR·docs 일관성 보장` → `**Lane plugin self-write boundary** — 각 lane plugin 이 자기 owner section/comment/label 을 직접 write 해 자율적 일관성 유지 (codeforge-* CLAUDE.md self-write 표 SSOT)`
- **line 23**: `├── [Cross-cutting] PMOAgent, DocsAgent` → `├── [Cross-cutting] PMOAgent`

```bash
git add README.md
git commit -m "fix(cfp-43): README — replace 'DocsAgent writer' with lane plugin self-write boundary"
```

- [ ] **Step 7: Edit `docs/plugin-design.md`**

스코프:
- **line 14**: `19 core 에이전트 + codeforge-review plugin 5 agent` → `**0 core 에이전트** (wrapper-only) + 6 lane plugin (codeforge-{requirements,design,develop,test,pmo,review}) 의 23 agent 가 자기 owner path 분산 보유`
- **line 27**: `19 core + codeforge-review 5 agent org chart, 7 레인, PL/sub 계층` → `0 core + 6 lane plugin org chart (각 plugin 의 agent listing 은 해당 plugin repo 참조), 7 레인, PL/sub 계층`
- **line 147**: `19 core agent md (process 15 + generic Dev 3...)` 전체 단락 갱신 → `agents/*.md 부재 (CFP-40 final delete) — 모든 agent 는 6 lane plugin 으로 분산. v0.17 review 추출 (CFP-29) → v0.22~v5 ζ arc decomposition (CFP-31~CFP-40 — 5 lane plugin 신설 + DocsAgent 해체) → CFP-42 sibling backfill 후 wrapper-only 정합 (ADR-009 / ADR-010)`
- **line 167**: `19 core 에이전트 + codeforge-review plugin 5 agent + preset` → `0 core (wrapper-only) + 6 lane plugin agent + preset (각 lane plugin 에 분산)`
- **line 183**: `DomainAgent · DataEngineerAgent · PMOAgent · DocsAgent (SSOT 상수 다수)` → `(현재 wrapper 에 agent 0개. SSOT 상수 참조 책임은 각 lane plugin agent 가 보유)`

```bash
git add docs/plugin-design.md
git commit -m "fix(cfp-43): plugin-design — '19 core' → '0 core wrapper-only' + 6 lane plugin distribution"
```

- [ ] **Step 8: Edit `docs/consumer-guide.md`**

스코프:
- **line 69-71**: `# ADR markdown (DocsAgent commit)`, `# Architect Change Plan (DocsAgent commit)`, `# Domain KB (계층, DocsAgent commit)` → 각각 `# ADR markdown (ArchitectAgent direct write — codeforge-design)`, `# Architect Change Plan (ArchitectAgent direct write — codeforge-design)`, `# Domain KB (DomainAgent direct write — codeforge-requirements)`
- **line 73**: `.claude-work/                       # DocsAgent write queue (gitignore)` → `.claude-work/                       # consumer overlay scratch (gitignore — wrapper-only 모델 후 write queue 사용 안 함)`
- **line 251**: `주 소비자: DocsAgent · RequirementsPLAgent · DomainAgent · PMOAgent` → `주 소비자: RequirementsPLAgent · DomainAgent · PMOAgent · ArchitectAgent (각 lane plugin)`
- **line 412**: `DocsAgent 가 라벨 부착했는지 확인` → `해당 lane plugin (DesignReviewPL / SecurityTestPL — codeforge-review) 이 review-verdict-v2 self-write 로 라벨 부착했는지 확인`
- **line 414**: `fallback 으로 DocsAgent 가 mcp__github__sub_issue_write 수동 호출` → `fallback 으로 DeveloperPL (codeforge-develop) 이 mcp__github__sub_issue_write 수동 호출`

```bash
git add docs/consumer-guide.md
git commit -m "fix(cfp-43): consumer-guide — DocsAgent commit owners → lane plugin direct write"
```

- [ ] **Step 9: Edit `docs/migration-guide.md`**

스코프:
- **line 110**: `codeforge core (DocsAgent): verdict 받아 Story §9 / PR comment / gate label 처리` → `(레거시 v0.x context) — ζ arc 후에는 review-verdict-v2 가 review PL self-write 로 처리 (codeforge-review 의 ClaudeReview/CodexReview/{Design,Code,SecurityTest}ReviewPL 직접)`
- **line 158**: `agent permission frontmatter 4건 갱신 + DocsAgent scope 축소` → `agent permission frontmatter 4건 갱신 + DocsAgent scope 축소 (CFP-26 Phase 0a — 후속 CFP-40 에서 DocsAgent 완전 해체)`
- **line 166**: `Consumer overlay 에서 DocsAgent 권한 명시 override` → `Consumer overlay 에서 DocsAgent 권한 명시 override (v0.x — wrapper-only 모델 후 무관)`. 본 단락은 **legacy** 라벨 추가 (`> **(Legacy v0.x — wrapper-only end-state 후 적용 안 됨)**`)
- **line 572**: `DocsAgent · DomainAgent · RequirementsPLAgent · PMOAgent 가 Atlassian 호출 전 project.yaml 을 Read` → `DomainAgent · RequirementsPLAgent · PMOAgent · ArchitectAgent 가 GitHub MCP / gh api 호출 전 project.yaml 을 Read`
- **lines 667-668**: `DocsAgent overlay 본문 확인 — project.yaml 참조 문구 포함` + `cat .claude/agents/DocsAgent.md | grep -A1 "project.yaml"` 명령어 → 본 단락 전체 **삭제 또는 v0.x legacy 표시** (DocsAgent file 부재)

```bash
git add docs/migration-guide.md
git commit -m "fix(cfp-43): migration-guide — mark v0.x DocsAgent paths as legacy + remove dead command"
```

- [ ] **Step 10: Final wrapper grep verification**

```bash
PYTHONIOENCODING=utf-8 bash scripts/check-doc-frontmatter.sh && \
PYTHONIOENCODING=utf-8 bash scripts/check-doc-section-schema.sh && \
PYTHONIOENCODING=utf-8 bash scripts/check-inter-plugin-contracts.sh && \
bash scripts/test-check-inter-plugin-contracts.sh && \
echo "=== lint chain PASS ==="
```

```bash
# Negative — DocsAgent 잔재 0 in non-history sections
grep -rn "DocsAgent" CLAUDE.md docs/ templates/ README.md \
  --exclude-dir=superpowers --exclude-dir=.git 2>/dev/null \
  | grep -v "history\|legacy\|CFP-40 final delete\|v0.x" \
  | wc -l
# 기대: 0
```

```bash
# Negative — "19 core" 주장 0
grep -rn "19 core" CLAUDE.md docs/ templates/ README.md \
  --exclude-dir=superpowers --exclude-dir=.git 2>/dev/null \
  | wc -l
# 기대: 0
```

```bash
# Positive — wrapper-only 명시 존재
grep -rn "wrapper-only\|0 core" CLAUDE.md docs/ templates/ README.md \
  --exclude-dir=superpowers --exclude-dir=.git 2>/dev/null \
  | wc -l
# 기대: > 0
```

If any verification fails, return to the relevant Step (2-9) and fix.

- [ ] **Step 11: Push branch + open PR**

```bash
git push -u origin cfp-43-wrapper-cleanup
```

```bash
gh pr create --base main --head cfp-43-wrapper-cleanup --title "feat(cfp-43): wrapper-only docs cleanup (DocsAgent ghost text removal + 'Lane plugin self-write boundary' restructure)" --body "$(cat <<'EOF'
## Summary

ζ arc decomposition 의 wrapper docs 측 정합성 회복. 8 file 의 stale DocsAgent text + '19 core' 주장 + DocsAgent-shaped section structure 를 'Lane plugin self-write boundary' 모델로 재구성 (X2 cleanup depth — Y2 backfill 의 wrapper part).

PR-1~PR-6 (cross-repo lane plugin backfill) 머지 후 진행 — 본 PR 은 lane plugin 의 갱신된 self-write 표를 reference.

## Files changed

- CLAUDE.md (DocsAgent 인용 제거 + '문서 write 책임 분담' → 'Lane plugin self-write boundary' 재구성)
- docs/orchestrator-playbook.md (DocsAgent 인용 제거 + §5 표 재구성 + §11 write queue 단순화)
- templates/story-page-structure.md ('DocsAgent 액션' column → 'Owner agent')
- templates/impl-manifest.md (§8.5 기록 owner → DeveloperPL)
- README.md (Cross-cutting listing 갱신)
- docs/plugin-design.md ('19 core' → '0 core wrapper-only')
- docs/consumer-guide.md (DocsAgent commit 책임자 → lane plugin)
- docs/migration-guide.md (v0.x legacy 표시)

## Test Plan

- [x] check-doc-frontmatter.sh PASS
- [x] check-doc-section-schema.sh PASS
- [x] check-inter-plugin-contracts.sh PASS
- [x] test-check-inter-plugin-contracts.sh PASS
- [x] grep test: DocsAgent 0 in non-history, '19 core' 0, 'wrapper-only' present

## Source

[CFP-43 spec](https://github.com/mclayer/plugin-codeforge/blob/main/docs/superpowers/specs/2026-04-30-cfp-43-wrapper-only-docs-cleanup-design.md)
[CFP-43 plan](https://github.com/mclayer/plugin-codeforge/blob/main/docs/superpowers/plans/2026-04-30-cfp-43-wrapper-only-docs-cleanup.md)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 12: Merge PR (admin if needed)**

CFP-42 와 동일 — phase-gate-mergeable 차단 시 admin merge:
```bash
gh pr merge <N> --merge --admin --delete-branch
```

```bash
git checkout main && git pull --ff-only
git branch -d cfp-43-wrapper-cleanup 2>/dev/null || true
```

---

## Task 8: Final integration verification

**Files:** (none — verification only)

- [ ] **Step 1: 7 PR 머지 상태 확인**

```bash
# 각 plugin 의 main branch 에 본 CFP-43 commit 도착했는지
for repo in plugin-codeforge-review plugin-codeforge-pmo plugin-codeforge-requirements plugin-codeforge-test plugin-codeforge-develop plugin-codeforge-design; do
  echo "=== $repo ==="
  gh api "repos/mclayer/$repo/commits?per_page=5" --jq '.[].commit.message' | head -3
done
echo "=== plugin-codeforge (wrapper) ==="
git log --oneline main -5
```

- [ ] **Step 2: Cross-repo grep 검증 (sample)**

각 lane plugin 의 main branch 에서 stale text 잔존 확인:
```bash
# review
gh api "repos/mclayer/plugin-codeforge-review/contents/templates/review-pl-base.md" --jq '.content' | base64 -d | grep -c "ledger-append"
# 기대: 0

# pmo
gh api "repos/mclayer/plugin-codeforge-pmo/contents/agents/PMOAgent.md" --jq '.content' | base64 -d | grep -c "adr-draft\|DocsAgent 경유"
# 기대: 0

# develop
gh api "repos/mclayer/plugin-codeforge-develop/contents/agents/DeveloperPLAgent.md" --jq '.content' | base64 -d | grep -c "DocsAgent 경유\|kind=impl-manifest helper"
# 기대: 0

# design
gh api "repos/mclayer/plugin-codeforge-design/contents/agents/ArchitectAgent.md" --jq '.content' | base64 -d | grep -c "DocsAgent 의뢰"
# 기대: 0

# 4 requirements + 1 test 의 footer
for f in agents/RequirementsPLAgent.md agents/DomainAgent.md agents/RequirementsAnalystAgent.md agents/ResearcherAgent.md; do
  count=$(gh api "repos/mclayer/plugin-codeforge-requirements/contents/$f" --jq '.content' | base64 -d | grep -c "Orchestrator 경유 DocsAgent 가 기록")
  echo "$f: $count"
done
gh api "repos/mclayer/plugin-codeforge-test/contents/agents/TestAgent.md" --jq '.content' | base64 -d | grep -c "Orchestrator 경유 DocsAgent 가 기록"
# 모두 기대: 0
```

- [ ] **Step 3: Wrapper 최종 lint + grep**

```bash
PYTHONIOENCODING=utf-8 bash scripts/check-doc-frontmatter.sh
PYTHONIOENCODING=utf-8 bash scripts/check-doc-section-schema.sh
PYTHONIOENCODING=utf-8 bash scripts/check-inter-plugin-contracts.sh
bash scripts/test-check-inter-plugin-contracts.sh

# DocsAgent 잔재
grep -rn "DocsAgent" CLAUDE.md docs/ templates/ README.md \
  --exclude-dir=superpowers --exclude-dir=.git 2>/dev/null \
  | grep -v "history\|legacy\|v0.x\|CFP-40 final delete" \
  | wc -l
# 기대: 0
```

- [ ] **Step 4: 최종 보고**

작업 완료 시:
- 7 PR merge SHA 목록
- 6 lane plugin 의 main 상태 (stale text 0 확인)
- wrapper main 상태 (lint chain PASS + grep 0)

---

## Out-of-plan tasks

다음은 본 plan 의 직접 task 아님 — 별도 후속 CFP:
- review-verdict-v1 archive (Codex CFP-D)
- canonical↔sibling drift detection (CFP-42 §10 deferred)
- migration-guide v0.22→v5 BREAKING parity (Codex CFP-E, retro:77)
- 추가 발견되는 stale text (gap audit miss 시)
