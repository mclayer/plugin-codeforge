# CFP-44 Implementation Plan: Wrapper CLAUDE.md SSOT Compression

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wrapper CLAUDE.md 705 → ~330줄 압축 (53% 절감, ~9k tokens 매 세션 절약). 3 lane plugin CLAUDE.md backfill 후 wrapper compression. ADR-012 신설.

**Architecture:** 4 PR (3 cross-repo backfill + 1 wrapper). Cross-repo 머지 후 wrapper. CFP-43 plan precedent 답습 — mcp__github MCP 도구로 cross-repo 작업 (local clone 불필요), wrapper 는 local feature branch.

**Tech Stack:** Markdown editing via Edit/Write + mcp__github MCP (cross-repo) + bash grep verification.

**Spec reference:** [docs/superpowers/specs/2026-04-30-cfp-44-wrapper-claudemd-ssot-compression-design.md](../specs/2026-04-30-cfp-44-wrapper-claudemd-ssot-compression-design.md)

**Note (cross-repo workflow):** Cross-repo PR (Tasks 1-3) 은 mcp__github MCP 도구 사용. 6 lane plugin 각자 main branch 가 base. PR merge 권한 가정 (admin merge 또는 자체 dogfooded workflow follow).

---

## File Structure (per PR)

| PR | Repo | Files modified |
|---|---|---|
| PR-1 | mclayer/plugin-codeforge-test | `CLAUDE.md` |
| PR-2 | mclayer/plugin-codeforge-design | `CLAUDE.md` |
| PR-3 | mclayer/plugin-codeforge-requirements | `CLAUDE.md` |
| PR-4 | mclayer/plugin-codeforge (wrapper) | `CLAUDE.md`, `docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md` (NEW) |

---

## Cross-repo PR pattern (Tasks 1-3)

각 cross-repo PR 의 공통 흐름 (CFP-43 plan precedent):

1. `mcp__github__get_file_contents` — 대상 파일 fetch (현재 main 본문 확인, line ref 매핑)
2. `mcp__github__create_branch` — `cfp-44-<slug>` branch 생성 (from main)
3. 본문 분석·신규 절 위치 결정 (보통 "Self-write 책임" 표 직후 또는 lane 별 의미 영역)
4. `mcp__github__create_or_update_file` — 수정된 본문 push (자동 commit)
5. `mcp__github__create_pull_request` — PR 생성 (base: main, head: cfp-44-<slug>)
6. `mcp__github__merge_pull_request` — merge (admin 또는 자체 dogfooded workflow)
7. Verify: `mcp__github__get_file_contents` (main branch) 로 재 fetch + grep verification

---

## Task 1: PR-1 codeforge-test — MISSING gap 해소

**Repo:** `mclayer/plugin-codeforge-test`
**Branch:** `cfp-44-test-claude-md-backfill`
**File:** `CLAUDE.md`

**Gap fix scope** (audit MISSING):
- functional/performance subset 병렬 spawn 규약 전무
- baseline 10% mean threshold 전무
- sequential fallback (`tests.performance.depends_on_functional: true`) 전무
- consumer overlay runner config delegation 전무

- [ ] **Step 1: Fetch current CLAUDE.md**

```
mcp__github__get_file_contents:
  owner=mclayer, repo=plugin-codeforge-test, path=CLAUDE.md
```

Identify: 적절한 삽입 위치 — 보통 `## TestAgent 동작` 또는 `## Self-write 책임` 절 부근. 헤더 구조 파악.

- [ ] **Step 2: Add new section "## 구현 테스트 lane 동작"**

다음 내용을 적절한 위치에 삽입 (헤더 위치는 fetch 결과에 따라 결정):

````markdown
## 구현 테스트 lane 동작

Orchestrator 가 TestAgent 를 **subset 병렬** 로 spawn (R9 — [CFP-19 spec](https://github.com/mclayer/plugin-codeforge/blob/main/docs/superpowers/specs/2026-04-27-cfp-19-orchestration-parallelization.md)):

- `TestAgent(subset: functional)` ∥ `TestAgent(subset: performance)` — 한 메시지에 dispatch
- 두 subset 모두 PASS → 보안 lane 진입

### Subset 1: functional

단위 / 통합 / 인프라 테스트. consumer overlay 가 러너·경로 지정.

### Subset 2: performance

baseline 대비 mean 10% 이상 악화 시 FAIL. consumer overlay 가 baseline 위치 지정.

### Sequential fallback

consumer overlay `tests.performance.depends_on_functional: true` 시 sequential 실행 (functional → performance). 기본은 parallel.

### Consumer overlay 위임

- 러너 (pytest / npm test / cargo test 등) · 테스트 경로 · baseline 파일 위치 · performance 의존성 모두 consumer overlay (`.claude/_overlay/project.yaml` `tests.*` slice) 지정
- TestAgent 는 overlay 명시값 follow — hardcoded path/runner 없음

### FAIL → 진단

FAIL 시 Orchestrator 경유 DeveloperPL 1차 진단 → ArchitectPLAgent 최종 판정. 본 lane plugin 은 `verdict.status=FAIL` 반환만 — 진단 logic 미보유.
````

- [ ] **Step 3: Create branch**

```
mcp__github__create_branch:
  owner=mclayer, repo=plugin-codeforge-test, branch=cfp-44-test-claude-md-backfill, from_branch=main
```

- [ ] **Step 4: Push edited file**

```
mcp__github__create_or_update_file:
  owner=mclayer, repo=plugin-codeforge-test, branch=cfp-44-test-claude-md-backfill,
  path=CLAUDE.md, content=<edited body with new "구현 테스트 lane 동작" section>,
  message="fix(cfp-44): backfill 구현 테스트 lane 동작 — functional/performance subset + 10% baseline + sequential fallback"
```

- [ ] **Step 5: Open PR**

```
mcp__github__create_pull_request:
  owner=mclayer, repo=plugin-codeforge-test, base=main, head=cfp-44-test-claude-md-backfill,
  title="fix(cfp-44): backfill 구현 테스트 lane 동작 (MISSING gap)",
  body="""
## Summary
codeforge-test CLAUDE.md 에 다음 누락 항목 추가:
- functional / performance subset 병렬 spawn (R9, CFP-19)
- baseline 10% mean threshold
- sequential fallback (tests.performance.depends_on_functional)
- consumer overlay runner config delegation

## Source
[CFP-44 spec](https://github.com/mclayer/plugin-codeforge/blob/main/docs/superpowers/specs/2026-04-30-cfp-44-wrapper-claudemd-ssot-compression-design.md) — A1' (audit-driven minimum)

## Audit
codeforge-test SSOT coverage = MISSING (audit @ CFP-44 brainstorming). wrapper PR-4 가 본 절 삭제 예정 — 본 PR 머지 후 wrapper 정보 손실 0 보장.
"""
```

- [ ] **Step 6: Merge PR**

```
mcp__github__merge_pull_request:
  owner=mclayer, repo=plugin-codeforge-test, pullNumber=<from-step-5>, merge_method=merge
```

required status check 차단 시: `gh pr merge <N> --admin --merge` (admin override).

- [ ] **Step 7: Verify (post-merge)**

```
mcp__github__get_file_contents:
  owner=mclayer, repo=plugin-codeforge-test, path=CLAUDE.md, ref=main
```

Expected: body 에 "functional", "performance", "10%", "subset", "depends_on_functional" 모두 등장.

```bash
# Local verification (사용자가 직접 실행 가능)
curl -s https://raw.githubusercontent.com/mclayer/plugin-codeforge-test/main/CLAUDE.md | grep -c "functional\|performance\|10%\|depends_on_functional"
# Expected: ≥ 5
```

---

## Task 2: PR-2 codeforge-design — 4-way + lifecycle + Freshness backfill

**Repo:** `mclayer/plugin-codeforge-design`
**Branch:** `cfp-44-design-claude-md-backfill`
**File:** `CLAUDE.md`

**Gap fix scope** (audit PARTIAL critical):
- "4-way 이념 대립" 헤더만 있고 body 미작성 — body 채움
- ArchitectPL stateless re-spawn lifecycle 누락
- Deputy Freshness rule 누락

- [ ] **Step 1: Fetch current CLAUDE.md**

```
mcp__github__get_file_contents:
  owner=mclayer, repo=plugin-codeforge-design, path=CLAUDE.md
```

Identify: "4-way 이념 대립" 헤더 (또는 동등 headerb). 그 직하 빈 body 영역 확인.

- [ ] **Step 2: Replace empty body with 4-way ideology section**

다음 내용으로 "4-way 이념 대립" 절의 body 를 채움:

````markdown
## 4-way 이념 대립 — 5 deputy 의 독립 관점

ArchitectPLAgent 가 5 deputy 를 **병렬 spawn** — 넷은 4-way 이념 대립 (Mapper ↔ Refactor ↔ SecurityArch ↔ DataMigrationArch), TestContractArch 는 §8 author input contributor (대립 비참여).

| Deputy | 입장 | 핵심 질문 |
|---|---|---|
| **CodebaseMapperAgent** | 보수 — as-is 변호자 | "기존 패턴 유지, 변경 영향 최소화" |
| **RefactorAgent** | 혁신 — to-be 옹호자 | "결합도 감소, 인터페이스 분리, 패턴화" |
| **SecurityArchitectAgent** | 위협 — 공격자 관점 | "어디서 외부 입력이 들어오는가, 누가 무엇을 신뢰하는가" |
| **DataMigrationArchitectAgent** | 데이터 무결성 — 변호자 | "schema 가 어떻게 변하는가, 기존 데이터는 어떻게 처리되는가, 실패 시 어떻게 복구하는가" |
| TestContractArchitectAgent | QA perspective contributor | §8 커버리지 후보·경계·invariant — 대립 비참여 |

**독립 관점 유지**: 5 deputy 모두 원 소스 (코드 + ADR + Change Plan 초안 + Story §1-7) 직접 읽기. 한쪽이 다른 쪽의 요약에 의존하지 않음 — 서로 산출물에 오염되지 않도록 독립.

**충돌 해소**: 4 관점 충돌 시 ArchitectAgent (chief author) 가 결정 근거와 함께 Change Plan §2 (현재 구조) · §3 (도입할 설계) · §7 (보안 설계) · §11 (데이터 마이그레이션) 에 명시. 수용·반박은 chief author 가 조정 후 기록 (deputy 간 상호 대응 방식 아님). ArchitectPLAgent 는 통합 결과 검수.

**DesignReviewPL 교차 체크**: ArchitectAgent 통합 판정 + ArchitectPLAgent 검수가 각 변호 근거를 근거 있게 일축·수용했는가 / 요건 범위를 넘지 않았는가 / §7 보안 설계와 §11 데이터 마이그레이션이 충실히 반영되었는가 — 병렬 모델에서는 deputy 간 상호 대응하지 않으므로, 대립 해소 품질 평가는 chief author + PL 통합 결과 대상.
````

- [ ] **Step 3: Add ArchitectPL stateless re-spawn lifecycle section**

다음 절을 적절한 위치에 추가 (보통 "ArchitectPLAgent" 관련 섹션 후 또는 "Self-write 책임" 표 부근):

````markdown
## ArchitectPLAgent 라이프사이클 (stateless 재스폰)

- 매 트리거마다 Orchestrator 가 신규 spawn — 세션 유지 없음
- Story file §1-8 재로딩으로 컨텍스트 복원
- 토큰 비용: 재스폰 당 ~5-10k tokens. FIX 3회 가정 시 15-30k overhead ([codeforge wrapper playbook §8](https://github.com/mclayer/plugin-codeforge/blob/main/docs/orchestrator-playbook.md) 참조)
- **ArchitectAgent (chief author)** 도 각 설계 lane 진입마다 stateless 재스폰 — 5 deputy 산출물 입력 수령 후 Change Plan §1-§11 author. ArchitectPLAgent RETURN 시에도 재스폰
````

- [ ] **Step 4: Add Deputy Freshness rule section**

다음 절을 추가:

````markdown
## 설계 lane Deputy Freshness

모든 deputy (CodebaseMapperAgent · RefactorAgent · SecurityArchitectAgent · TestContractArchitectAgent · DataMigrationArchitectAgent) 공통:
- **매 설계 lane 진입 시 재스폰** (이전 Story 산출물 재사용 금지)
- 리뷰·테스트에서 설계 lane 복귀 시에도 재스폰 (구현 lane 에서 코드 변경 전제)
- base_sha / scope_paths frontmatter 갱신 의무
````

- [ ] **Step 5: Create branch + push**

```
mcp__github__create_branch:
  owner=mclayer, repo=plugin-codeforge-design, branch=cfp-44-design-claude-md-backfill, from_branch=main

mcp__github__create_or_update_file:
  owner=mclayer, repo=plugin-codeforge-design, branch=cfp-44-design-claude-md-backfill,
  path=CLAUDE.md, content=<edited body>,
  message="fix(cfp-44): backfill 4-way ideology body + ArchitectPL stateless lifecycle + Deputy Freshness"
```

- [ ] **Step 6: Open PR**

```
mcp__github__create_pull_request:
  owner=mclayer, repo=plugin-codeforge-design, base=main, head=cfp-44-design-claude-md-backfill,
  title="fix(cfp-44): backfill 4-way ideology + ArchitectPL lifecycle + Deputy Freshness (PARTIAL critical)",
  body="""
## Summary
codeforge-design CLAUDE.md 에 다음 누락 항목 추가:
- "4-way 이념 대립" 절 body 채움 (Mapper conservative ↔ Refactor innovator ↔ SecurityArch threat ↔ DataMigration integrity)
- ArchitectPL stateless re-spawn lifecycle (token cost ~5-10k per spawn, FIX 3× = 15-30k overhead)
- Deputy Freshness rule (매 설계 lane 진입 시 재스폰, 이전 Story 산출물 재사용 금지)

## Source
[CFP-44 spec](https://github.com/mclayer/plugin-codeforge/blob/main/docs/superpowers/specs/2026-04-30-cfp-44-wrapper-claudemd-ssot-compression-design.md) — A1' (audit-driven minimum)

## Audit
codeforge-design SSOT coverage = PARTIAL critical. wrapper PR-4 가 본 3 절 삭제 예정.
"""
```

- [ ] **Step 7: Merge + Verify**

```
mcp__github__merge_pull_request:
  owner=mclayer, repo=plugin-codeforge-design, pullNumber=<from-step-6>, merge_method=merge

mcp__github__get_file_contents:
  owner=mclayer, repo=plugin-codeforge-design, path=CLAUDE.md, ref=main
```

Expected: "4-way", "stateless 재스폰", "Deputy Freshness", "Mapper", "Refactor", "SecurityArch", "DataMigration" 모두 등장.

---

## Task 3: PR-3 codeforge-requirements — Clarification + Domain Knowledge schema backfill

**Repo:** `mclayer/plugin-codeforge-requirements`
**Branch:** `cfp-44-req-claude-md-backfill`
**File:** `CLAUDE.md`

**Gap fix scope** (audit PARTIAL critical):
- Clarification 재스폰 패턴 누락
- Domain Knowledge page schema reference 누락

- [ ] **Step 1: Fetch current CLAUDE.md**

```
mcp__github__get_file_contents:
  owner=mclayer, repo=plugin-codeforge-requirements, path=CLAUDE.md
```

- [ ] **Step 2: Add Clarification 재스폰 section**

다음 절을 적절한 위치에 추가 (RequirementsPL 동작 절 인근 권장):

````markdown
## Clarification 재스폰 패턴

서브에이전트 (DomainAgent · RequirementsAnalyst · Researcher) 는 one-shot 이라 PL ↔ 서브 continuous dialog 불가. PL 이 통합 중 추가 질의가 필요하면:

1. PL → Orchestrator 에 "<에이전트> 재스폰 요청 + clarification context + 이전 출력 pointer" 전달
2. Orchestrator 가 해당 에이전트를 신규 spawn (이전 출력 + 재질의 context 포함)
3. 재 spawn 결과를 PL 이 통합 재시도

**의미**: "각 책임 종료 전까지 보조" 메커니즘의 실제 구현 — 서브에이전트는 stateless 라 재 spawn 이 유일한 "clarification" 메커니즘.

**적용 lane**: 요구사항 (3 sub-agent) · 설계 (5 deputy) 양쪽 동일 패턴 — wrapper Orchestrator 가 routing.
````

- [ ] **Step 3: Add Domain Knowledge page schema section**

다음 절을 추가 (DomainAgent 동작 절 부근):

````markdown
## Domain Knowledge page schema

- **위치**: `docs/domain-knowledge/<area>/<topic>.md` (계층 구조). Consumer overlay 가 area 자유 정의
- **owner write**: DomainAgent 직접 (CFP-26 Phase 0a 후 wrapper write queue 미경유)
- **CODEOWNERS**: `docs/domain-knowledge/**` → `@org/domain-experts` 자동 review
- **template**: [`templates/domain-knowledge.md`](templates/domain-knowledge.md) (CFP-27 신설)

**Schema** (frontmatter + 본문 sections):

```yaml
---
title: <표시용 제목>
area: <area 이름>
topic_slug: <kebab-case topic>
status: Draft | Active | Deprecated
sources:
  - <file path or URL>
related_adrs:
  - ADR-NNN
related_stories:
  - <KEY>-N
updated: YYYY-MM-DD
---
```

본문 섹션:
- `## 정의`
- `## 컨텍스트`
- `## 핵심 규칙`
- `## 경계`
- `## 관련 ADR`
- `## 변경 이력`

**검증**: `scripts/check-doc-frontmatter.sh` + `scripts/check-doc-section-schema.sh` (warning 모드 — CFP-28 strict 전환 후 fail).
````

- [ ] **Step 4: Create branch + push**

```
mcp__github__create_branch:
  owner=mclayer, repo=plugin-codeforge-requirements, branch=cfp-44-req-claude-md-backfill, from_branch=main

mcp__github__create_or_update_file:
  owner=mclayer, repo=plugin-codeforge-requirements, branch=cfp-44-req-claude-md-backfill,
  path=CLAUDE.md, content=<edited body>,
  message="fix(cfp-44): backfill Clarification 재스폰 pattern + Domain Knowledge page schema"
```

- [ ] **Step 5: Open PR**

```
mcp__github__create_pull_request:
  owner=mclayer, repo=plugin-codeforge-requirements, base=main, head=cfp-44-req-claude-md-backfill,
  title="fix(cfp-44): backfill Clarification 재스폰 + Domain Knowledge schema (PARTIAL critical)",
  body="""
## Summary
codeforge-requirements CLAUDE.md 에 다음 누락 항목 추가:
- Clarification 재스폰 패턴 (서브에이전트 one-shot → PL → Orchestrator 재 spawn)
- Domain Knowledge page schema (frontmatter + 본문 sections, CFP-27 SSOT)

## Source
[CFP-44 spec](https://github.com/mclayer/plugin-codeforge/blob/main/docs/superpowers/specs/2026-04-30-cfp-44-wrapper-claudemd-ssot-compression-design.md) — A1' (audit-driven minimum)

## Audit
codeforge-requirements SSOT coverage = PARTIAL critical. wrapper PR-4 가 본 2 절 삭제 예정.
"""
```

- [ ] **Step 6: Merge + Verify**

```
mcp__github__merge_pull_request:
  owner=mclayer, repo=plugin-codeforge-requirements, pullNumber=<from-step-5>, merge_method=merge

mcp__github__get_file_contents:
  owner=mclayer, repo=plugin-codeforge-requirements, path=CLAUDE.md, ref=main
```

Expected: "Clarification 재스폰", "domain-knowledge.md", "topic_slug", "정의", "컨텍스트", "핵심 규칙" 모두 등장.

---

## Task 4: PR-4 wrapper — CLAUDE.md compression + ADR-012

**Repo:** `mclayer/plugin-codeforge` (current local repo)
**Branch:** `cfp-44-wrapper-claudemd-compression` (이미 존재 — spec/plan commit 후 push)
**Files:**
- `CLAUDE.md` (UPDATE — 705 → ~330줄)
- `docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md` (NEW)

**Pre-condition**: Tasks 1-3 모두 머지 완료. 그래야 wrapper 의 lane plugin 참조 cross-link 가 정합.

### Sub-task 4a: ADR-012 file 생성

- [ ] **Step 1: Write ADR-012**

`docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md` 생성:

````markdown
---
adr_number: 12
title: Wrapper CLAUDE.md SSOT Boundary
status: Adopted
category: Team & Process
date: 2026-04-30
related_files:
  - CLAUDE.md (본 ADR 의 enforcement 대상 + 5-line summary inline)
  - docs/superpowers/specs/2026-04-30-cfp-44-wrapper-claudemd-ssot-compression-design.md (parent CFP)
---

## 상태

Adopted (2026-04-30) — CFP-44 PR-4 머지 시점.

## 컨텍스트

CFP-43 (X2 cleanup) 후 wrapper CLAUDE.md 가 705줄로 잔존. 사용자 진단:

> "분리를 수행했지만 부속 사항이 너무 많이 남아있는 것 같다."

증상: ζ arc decomposition (ADR-009) 으로 6 lane plugin 추출 완료됐지만, wrapper CLAUDE.md 에 lane 내부 디테일 (agent 역할 · spawn sequence · ideology · lifecycle · severity rule 등) 잔존. 의도된 SSOT 분업이 아니라 추출 시 미처 옮기지 못한 부속.

CFP-44 brainstorming 단계의 audit 결과:
- 1 MISSING (codeforge-test) + 2 PARTIAL critical (design, requirements) — backfill 의무
- 3 PARTIAL safe (review, pmo, develop) — wrapper 압축 무손실
- 3 wrapper-must-keep (cross-lane scope, single-plugin home 없음): 책임 매트릭스 + 원인 판정 decision table + FIX Ledger §10 schema

Codex (gpt-5.4) 두 번째 의견 — A1' (audit-driven minimum + explicit boundary statement) 권고: "process symmetry 만 사고 risk reduction 못 사는 거래" 회피.

## 결정

Wrapper plugin (codeforge) CLAUDE.md content scope 는 다음으로 strictly limited:

1. **Plugin identity** — 인트로, marketplace cross-repo sync 의무, 세션 개시 dependency check
2. **Cross-cutting policy** — dogfood Story 작성 의무, write boundary table (Lane plugin self-write boundary), inter-plugin contract index, ADR list
3. **3 named SSOT exceptions** (cross-lane scope, no single-plugin home):
   - Design / Code / Security 책임 매트릭스
   - 원인 판정 decision table
   - FIX Ledger §10 schema + Orchestrator monopoly + RESET 룰

**Excluded** (lane plugin SSOT 또는 playbook 으로 위임):
- per-lane spawn detail · agent role description
- lane-internal ideology · lifecycle · Freshness rule
- severity rule detail (codeforge-review templates SSOT)
- 병렬 스폰 권장 (spawn sequence 중복)
- GitHub workflow subsection 상세 (consumer-guide.md + label-registry-v1.md SSOT)

CLAUDE.md 본문 top (intro 직후) 에 본 ADR 의 5-line summary + ADR link inline 명시 — drift detection anchor.

## 결과

**달성**:
- CLAUDE.md 705 → ~330줄 (53% 절감, 매 세션 ~9k tokens 절약)
- "wrapper-only" 정체성 명확화 — composition + cross-cutting policy only
- 3 SSOT 예외 명시로 cross-lane 콘텐츠의 단일 출처 보장
- 미래 wrapper drift 의 anchor — boundary 위반 PR 의 review 시 ADR-012 reference

**비용**:
- 3 cross-repo backfill PR (codeforge-{test, design, requirements}) — audit gap 해소
- ADR-012 자동 강제 수단 부재 (linter 후속 CFP)
- documentation-quality asymmetry — lane plugin 별 self-contained 깊이 차이 (review/pmo/develop 는 agent md 영역 의존)

**검증**:
- 압축 후 CLAUDE.md line count ≤ 380 (target 330)
- §5.2 grep test (CFP-44 spec): 압축 대상 헤더 잔존 0
- ADR-012 frontmatter + section schema PASS

## 거부된 대안

- **A2 symmetric refresh** (CFP-43 패턴 답습, 6 cross-repo PR) — Codex 명시 reject: "process symmetry 만 사고 risk reduction 못 사는 거래"
- **A3 wrapper-only quick-win** (1 PR, lane plugin gap deferral) — ADR 급 결정 의도 (사용자 (2') 선택) 미달성, 결과 ~500줄 (target 미달)
- **Linter-first ratchet** (boundary 정의 없이 자동 강제만 도입) — 강제할 boundary 가 정의돼 있어야 lint rule 작성 가능. 후속 CFP 에서 도입 가능

## 다이어그램

```
Before (CFP-43 후, 본 ADR 결정 전):
codeforge wrapper CLAUDE.md (705 lines)
├── Plugin identity
├── 세션 개시 의무
├── Development Agent Team tree (52 lines, lane internal)
├── 레인 정의
├── 스폰 시퀀스 (91 lines, lane internal)
├── FIX 루프 + 원인 판정 table
├── 책임 매트릭스
├── 4-way 이념 (lane internal)
├── ArchitectPL 라이프사이클 (lane internal)
├── Deputy Freshness (lane internal)
├── Lane plugin self-write boundary
├── 병렬 스폰 권장 (duplicates spawn sequence)
├── Inter-plugin Contract index
├── ADR list
├── GitHub Workflow (89 lines, mostly in consumer-guide)
├── Story 작성 의무 (dogfood policy)
└── Domain Knowledge (lane internal)

After (CFP-44 머지 후):
codeforge wrapper CLAUDE.md (~330 lines)
├── Plugin identity (KEEP)
├── ## SSOT Boundary (NEW — ADR-012 5-line + link)
├── 세션 개시 의무 (compressed — checklist 만)
├── Lane → plugin → agent count (10-line table, replaces 52-line tree)
├── 레인 정의 (compressed)
├── Spawn sequence pointer → playbook §3
├── FIX 루프 (trigger/counter/§10 schema only)
├── 원인 판정 decision table (KEEP — SSOT 예외 #2)
├── 책임 매트릭스 (KEEP — SSOT 예외 #1)
├── PMOAgent Cross-cutting trigger (compressed)
├── Lane plugin self-write boundary (KEEP)
├── Inter-plugin Contract index (KEEP)
├── ADR list (compressed)
├── GitHub Workflow (compressed listing only)
├── Story 작성 의무 (KEEP — dogfood policy)
└── docs/stories markdown 규약 (KEEP)
```

## 관련 파일

- 본 ADR
- [CFP-44 spec](../superpowers/specs/2026-04-30-cfp-44-wrapper-claudemd-ssot-compression-design.md)
- CLAUDE.md (본 ADR 의 enforcement 대상)
- [ADR-009 Wrapper-only Decomposition](ADR-009-wrapper-only-decomposition.md) — parent ζ arc 결정
- [ADR-010 Inter-plugin Contract Sibling Sync](ADR-010-inter-plugin-contract-sibling-sync.md) — sibling cleanup arc
````

- [ ] **Step 2: Verify ADR-012 schema lint**

```bash
bash scripts/check-doc-frontmatter.sh docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md
bash scripts/check-doc-section-schema.sh docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md
```

Expected: warning 모드 PASS (또는 strict 모드 PASS 시 더 좋음).

- [ ] **Step 3: Commit ADR-012**

```bash
git add docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md
git commit -m "docs(cfp-44): add ADR-012 — Wrapper CLAUDE.md SSOT Boundary

Boundary 정의: wrapper CLAUDE.md = composition + cross-cutting policy + 3
named SSOT exceptions. lane internal · per-lane spawn detail · severity rule
detail · GitHub workflow subsection 상세는 lane plugin SSOT 또는 playbook
위임. Future linter ratchet 후속 CFP.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

### Sub-task 4b: CLAUDE.md compression

압축 표 (CFP-44 spec §3.4) 따라 section-by-section 처리. 각 section 별로 Edit (또는 큰 영역은 Read 후 Write).

**Compression 작업 순서** (top-down, 각 step 별 commit):

- [ ] **Step 4: ADD "## SSOT Boundary" 절 (top, after Plugin intro)**

`CLAUDE.md` line ~9 (Plugin intro 끝) 직후에 다음 삽입:

```markdown

## SSOT Boundary (ADR-012)

본 wrapper CLAUDE.md content scope 는 [ADR-012](docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md) 에 따라 strictly limited:
1. **Plugin identity** (composition · marketplace sync · dependency check)
2. **Cross-cutting policy** (dogfood Story 작성 의무 · write boundary table · inter-plugin contract index · ADR list)
3. **3 SSOT 예외** (cross-lane scope, no single-plugin home): 책임 매트릭스 · 원인 판정 decision table · FIX Ledger §10 schema

Lane internal · per-lane spawn detail · severity rule detail · GitHub workflow subsection 상세는 각 lane plugin CLAUDE.md SSOT 또는 [playbook](docs/orchestrator-playbook.md) 위임.
```

Edit:
```
old: "## 세션 개시 의무"
new: "## SSOT Boundary (ADR-012)\n\n본 wrapper CLAUDE.md content scope 는 [ADR-012](docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md) 에 따라 strictly limited:\n1. **Plugin identity** (composition · marketplace sync · dependency check)\n2. **Cross-cutting policy** (dogfood Story 작성 의무 · write boundary table · inter-plugin contract index · ADR list)\n3. **3 SSOT 예외** (cross-lane scope, no single-plugin home): 책임 매트릭스 · 원인 판정 decision table · FIX Ledger §10 schema\n\nLane internal · per-lane spawn detail · severity rule detail · GitHub workflow subsection 상세는 각 lane plugin CLAUDE.md SSOT 또는 [playbook](docs/orchestrator-playbook.md) 위임.\n\n## 세션 개시 의무"
```

Commit:
```bash
git add CLAUDE.md
git commit -m "feat(cfp-44): add SSOT Boundary section (ADR-012 anchor)"
```

- [ ] **Step 5: Compress "Development Agent Team" tree (lines 73-124, 52→10)**

현재 52줄 ASCII tree 를 다음 6행 표로 대체:

```markdown
## Development Agent Team

Wrapper agent **0개** (ζ arc 완료, ADR-009). Orchestrator (top-level Claude 세션) 가 6 lane plugin 의 agent 를 spawn.

| Lane | Plugin | Agent count | SSOT |
|---|---|---|---|
| 요구사항 | codeforge-requirements | 4 (PL + DomainAgent + RequirementsAnalyst + Researcher) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-requirements/blob/main/CLAUDE.md) |
| 설계 | codeforge-design | 7 (PL + ArchitectAgent chief + 5 deputy) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-design/blob/main/CLAUDE.md) |
| 설계리뷰 / 구현리뷰 / 보안테스트 | codeforge-review | 5 (3 PL + 2 worker) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-review/blob/main/CLAUDE.md) |
| 구현 | codeforge-develop | 5 (PL + QADev + 3 role:dev core) + preset/overlay 동적 | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-develop/blob/main/CLAUDE.md) |
| 구현테스트 | codeforge-test | 1 (TestAgent) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-test/blob/main/CLAUDE.md) |
| Cross-cutting | codeforge-pmo | 1 (PMOAgent) | [CLAUDE.md](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/CLAUDE.md) |

각 lane plugin 의 agent 역할·동작은 해당 plugin CLAUDE.md SSOT. 본 표는 composition map 만.
```

Edit `## Development Agent Team` 헤더 line ~73 부터 다음 헤더 (`## 레인 7개` line ~125) 직전까지 전체 대체.

Commit:
```bash
git add CLAUDE.md
git commit -m "refactor(cfp-44): compress Development Agent Team tree (52→10 lines)

ASCII tree of 23 agents → 6-row composition map. Agent role detail lives
in each lane plugin CLAUDE.md (SSOT)."
```

- [ ] **Step 6: Compress "스폰 시퀀스" (lines 185-275, 91→10)**

현재 91줄 detailed spawn pseudo-code 를 다음으로 대체:

```markdown
### 스폰 시퀀스

각 lane 별 상세 스폰 흐름·branch logic 은 [playbook §3 스폰 시퀀스](docs/orchestrator-playbook.md) SSOT. 요약:

```
요구사항 → 설계 → 설계리뷰 → 구현 → 구현리뷰 → 구현테스트 → 보안테스트
```

각 lane 진입 시 Orchestrator 가 해당 lane plugin 의 PL agent 를 spawn → PL 이 sub-agent 병렬 spawn (요구사항 3개 / 설계 5 deputy / 리뷰 2 worker / 구현 N role:dev). PL 산출물 종합 후 Orchestrator 에 verdict return → 다음 lane 라우팅.

**Clarification 재스폰**: 서브에이전트 one-shot 이라 PL ↔ 서브 continuous dialog 불가 → PL 이 Orchestrator 에 재 spawn 의뢰 (각 lane plugin CLAUDE.md SSOT).

**Track 병렬** (R7 — 설계리뷰 PASS 시): Track A (DesignReviewPL self-write merge gate) ∥ Track B (DeveloperPL Phase 2 PR 준비). 상세 [playbook §3.1](docs/orchestrator-playbook.md).
```

Edit `### 스폰 시퀀스` 헤더 line ~185 부터 `### FIX 루프` 헤더 line ~277 직전까지 대체.

Commit:
```bash
git add CLAUDE.md
git commit -m "refactor(cfp-44): compress 스폰 시퀀스 (91→10 lines)

Detailed lane-by-lane spawn pseudo-code → playbook §3 SSOT pointer + 
high-level lane sequence. CLAUDE.md ↔ playbook bidirectional SSOT 의 
playbook 측이 spawn detail 의 SSOT (already established in §3.1 line 237)."
```

- [ ] **Step 7: Compress "FIX 루프" detail (lines 277-311, 35→18)**

trigger / counter / §10 schema 만 잔류, "최대 FIX 횟수 / 카운터 리셋 / 수평 호출 금지" 등 세부 룰은 playbook §6 SSOT 위임:

```markdown
### FIX 루프

**판정 SSOT**: codeforge-review 의 [`templates/review-pl-base.md`](https://github.com/mclayer/plugin-codeforge-review/blob/main/templates/review-pl-base.md) §3 — severity 종합·dedup·종합 판정. codeforge core 입장에서는 [`docs/inter-plugin-contracts/review-verdict-v2.md`](docs/inter-plugin-contracts/review-verdict-v2.md) §3.2 review_verdict.status 필드 (PASS / FIX / FIX_DISCRETIONARY) 가 contract surface.

**트리거** (review-pl-base.md §3 결과 FIX 또는 FIX 재량):
- 설계 리뷰 → ArchitectPLAgent 회귀
- 구현 리뷰 / 구현 테스트 / 보안 테스트 FAIL → DeveloperPL 1차 진단 + ArchitectPLAgent 최종 판정 (parallel diagnosis, R4)

**카운터 SSOT** = `docs/stories/<KEY>.md` §10 "FIX Ledger" — Orchestrator 단독 관리 (CFP-32 monopoly · `fix-event-v1` contract). GitHub Issue 라벨은 보조 지표 (fix-ledger-sync.yml Action 자동 mirror).

**§10 FIX Ledger 스키마**:
```
| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1    | ISO8601 | 설계-리뷰   | DesignReviewPL P0 × 2 | 설계 | Change Plan §3 재작성 | — |
| 2    | ISO8601 | 구현-테스트 | 성능 mean +15% | 설계 | Change Plan §3 재작성 | **RESET 구현-리뷰** |
```

상세 룰 (max FIX 횟수 / RESET marker / parallel diagnosis / mechanical fast-path) 은 [playbook §6](docs/orchestrator-playbook.md) SSOT.
```

Edit lines 277-311.

Commit:
```bash
git add CLAUDE.md
git commit -m "refactor(cfp-44): compress FIX 루프 (35→18 lines)

KEEP: trigger taxonomy + §10 schema (CFP-32 Orchestrator monopoly, SSOT 예외 #3).
DELEGATE: max FIX 횟수 + RESET marker + parallel diagnosis + mechanical 
fast-path → playbook §6 SSOT."
```

- [ ] **Step 8: DELETE 4-way + Freshness + ArchitectPL lifecycle (lines 416-440, 11+5+7=23 lines → 0)**

3 절 모두 삭제 — codeforge-design CLAUDE.md (PR-2 머지 후) SSOT.

Edit:
```
old: "### CodebaseMapper ↔ Refactor ↔ SecurityArchitect ↔ DataMigrationArchitect 4-way 이념 대립\n\n[lines 417-426 본문]\n\nTestContractArchitectAgent는 §8 author input contributor (도형 대립 비참여 — Mapper/Refactor/SecurityArch/DataMigrationArch 4-way와 별개 영역). ArchitectPLAgent 메타-규칙 1번이 §8 TestContractArch input + §11 DataMigrationArch input 통합 정합성을 감사.\n\n### 설계 lane deputy Freshness\n\n[lines 429-432 본문]\n\n### ArchitectPLAgent 라이프사이클 (stateless 재스폰)\n\n[lines 435-440 본문]\n\n### Write 권한"
new: "### Write 권한"
```

(Note: `### Write 권한` 절도 다음 step 에서 삭제 예정)

Commit:
```bash
git add CLAUDE.md
git commit -m "refactor(cfp-44): delete 4-way + Freshness + ArchitectPL lifecycle (23 lines)

3 lane-internal sections moved to codeforge-design CLAUDE.md SSOT (PR-2).
wrapper-only end-state per ADR-012."
```

- [ ] **Step 9: DELETE Write 권한 section (lines 441-451, 11→0)**

본문이 자인하듯 wrapper agent 0개 — listing 자체가 redundant. wrapper-owned write paths 는 § Lane plugin self-write boundary 에 이미 포함.

Edit:
```
old: "### Write 권한 (path-scoped — 각 agent md frontmatter가 SSOT)\n\n[lines 442-451 본문]\n\n### Lane plugin self-write boundary"
new: "### Lane plugin self-write boundary"
```

Commit:
```bash
git add CLAUDE.md
git commit -m "refactor(cfp-44): delete Write 권한 section (11 lines)

post-CFP-40 wrapper agent 0개 — listing self-acknowledged 'wrapper agent
0개 (ζ arc 완료) — 본 listing 비어있음'. Live wrapper-owned write paths
covered in 'Lane plugin self-write boundary' section."
```

- [ ] **Step 10: DELETE Codex CLI / 플러그인 필수 + 병렬 스폰 권장 (lines 479-490, 4+7=11→0)**

§필수 의존성 SSOT (lines 27-43) + §스폰 시퀀스 와 중복.

Edit (delete both adjacent sections):
```
old: "### Codex CLI / 플러그인 필수\n[lines 480-482]\n\n### 병렬 스폰 권장\n[lines 485-490]\n\n**Clarification 재스폰 공통 절차**"
new: "**Clarification 재스폰 공통 절차**"
```

Then:
```
old: "**Clarification 재스폰 공통 절차** (요구사항·설계 레인): 서브에이전트는 one-shot이라 PL↔서브 continuous dialog 불가. PL이 통합 중 추가 질의가 필요하면 → Orchestrator에 \"<에이전트> 재스폰 요청 + clarification context + 이전 출력 pointer\" 전달 → Orchestrator가 해당 에이전트를 신규 스폰. 이것이 \"각 책임 종료 전까지 보조\" 메커니즘의 실제 구현."
new: ""
```

(Clarification 재스폰 도 codeforge-requirements + codeforge-design CLAUDE.md SSOT 후 wrapper 잔류 불필요.)

Commit:
```bash
git add CLAUDE.md
git commit -m "refactor(cfp-44): delete Codex CLI 필수 + 병렬 스폰 권장 + Clarification (~17 lines)

- Codex CLI 필수: §필수 의존성 SSOT (lines 27-43) duplicate
- 병렬 스폰 권장: §스폰 시퀀스 duplicate
- Clarification 재스폰: codeforge-{requirements,design} CLAUDE.md SSOT (PR-2/PR-3)"
```

- [ ] **Step 11: Compress PMOAgent 프로젝트 관리 (lines 400-414, 15→3)**

trigger 요약 + codeforge-pmo link 만 잔류:

```markdown
### PMOAgent (Cross-cutting)

스폰 트리거: Epic 창설 / Story 완료 회고 / 사용자 요청. 단일 Story lane 게이트에 개입 없음. 상세 동작·산출물 schema 는 [codeforge-pmo CLAUDE.md](https://github.com/mclayer/plugin-codeforge-pmo/blob/main/CLAUDE.md) SSOT.
```

Edit `### PMOAgent 프로젝트 관리 (Cross-cutting)` 헤더 line 400 부터 다음 절 (`### CodebaseMapper ↔ Refactor` line ~416, 이미 step 8 에서 삭제됨) 직전까지 대체.

Commit:
```bash
git add CLAUDE.md
git commit -m "refactor(cfp-44): compress PMOAgent (15→3 lines)

Trigger 요약 + codeforge-pmo CLAUDE.md SSOT pointer. Detailed 산출물·역할 
description → lane plugin SSOT."
```

- [ ] **Step 12: Compress 세션 개시 의무 (lines 23-72, 50→25)**

확인·복구 절차 verbose body 를 checklist + playbook §1.1 link 형태로:

다음으로 대체 (헤더 + 의존성 SSOT 표 KEEP, 절차 압축):

```markdown
## 세션 개시 의무 (필수 의존성 자동 확인 + 복구 or 요구)

세션 시작 직후, 모든 작업보다 먼저 의존성의 노출·설치·인증 상태 확인. 자동 복구 가능한 것은 즉시 복구, 불가능한 것은 사용자에게 설치·재인증 요구. 복구 완료 전까지 모든 작업 중단.

### 필수 의존성 SSOT

**MCP 서버 (1종)**:
- `github` — Issue/PR/sub-issue/comment·label·milestone 는 각 lane plugin self-write; `docs/{change-plans,adr,domain-knowledge,retros}/**` 직접 write 는 owner agent (CFP-26 Phase 0a)

**필수 플러그인 (9종)**:
- `codeforge-{review,pmo,requirements,test,develop,design}@mclayer` — 6 lane plugin
- `codex@openai-codex` — codeforge-review 의 CodexReviewAgent + codex CLI dependency
- `superpowers@claude-plugins-official` — agent md skill 의존
- `github@claude-plugins-official` — GitHub MCP 도구 노출

**필수 CLI (2종)**: `codex`, `gh`

**권장 플러그인 (4종, 미설치 시 권유만)**: `pyright-lsp`, `context7`, `commit-commands`, `pr-review-toolkit`

### 확인·복구 절차

상세 절차는 [playbook §1.1](docs/orchestrator-playbook.md) checklist 0번 SSOT. 요약:
1. **노출 확인** — MCP `ToolSearch` / 플러그인 `~/.claude/settings.json` enabledPlugins / CLI `which` + `gh auth status`
2. **자동 복구 시도** — 플러그인 cache 있으나 disabled → settings.json 직접 토글
3. **사용자 요구** (자동 불가 · blocking wait) — `/mcp` 재인증 / `/plugins install <name>@<marketplace>` / CLI 설치 / `gh auth login`
4. **추가 검증** (consumer repo) — `.github/workflows/` 권장 6개 + ISSUE_TEMPLATE + PULL_REQUEST_TEMPLATE + CODEOWNERS 부재 시 알림 (자동 복사 안 함)
```

Edit `## 세션 개시 의무` 헤더 line 23 부터 `## Development Agent Team` 헤더 line 73 직전까지 대체.

Commit:
```bash
git add CLAUDE.md
git commit -m "refactor(cfp-44): compress 세션 개시 의무 (50→~25 lines)

KEEP: 의존성 SSOT (MCP/plugin/CLI 명시 — wrapper boot critical).
DELEGATE: verbose 확인·복구 절차 → playbook §1.1 SSOT."
```

- [ ] **Step 13: Compress 컨텍스트 전달 + Never-skippable (lines 154-183, 17+12=29→8)**

Story file SSOT + Self-write 표 1줄로:

```markdown
### 컨텍스트 전달

각 Story 마다 `docs/stories/<KEY>.md` 가 SSOT. 에이전트 프롬프트는 docs file 경로 주입, 본문은 에이전트 자체 fetch. Context Packet · §0 Live Progress · Project Config Packet 상세는 [playbook §12 + §14](docs/orchestrator-playbook.md) SSOT.

각 lane plugin 이 자기 owned section 직접 self-write — § Lane plugin self-write boundary 표 SSOT.

### Never-skippable 에이전트

각 lane plugin 의 PL agent + non-skippable sub-agent 는 해당 plugin CLAUDE.md SSOT. wrapper Orchestrator 는 lane 진입 시 PL agent 1개만 spawn — PL 이 sub-agent fan-out 책임. `role: dev` 만 조건부 생략 (Change Plan 경로 매핑 따라).
```

Edit lines 154-183 (3 sub-section: 컨텍스트 전달 / Never-skippable).

Commit:
```bash
git add CLAUDE.md
git commit -m "refactor(cfp-44): compress 컨텍스트 전달 + Never-skippable (29→8 lines)

DELEGATE: Context Packet detail / §0 Live Progress / Project Config Packet 
→ playbook §12 + §14 SSOT. Never-skippable agent enumeration → each lane 
plugin CLAUDE.md SSOT."
```

- [ ] **Step 14: Compress GitHub Workflow subsections (lines 561-649, 89→25)**

`템플릿 + workflow 자동화 6종 + Branch protection` KEEP (wrapper-owned), `계층 / 상태 + Phase Label / FIX 루프 라벨 / 코멘트 규칙 / Labels / 대시보드 / 원문 위치` 는 consumer-guide.md + label-registry-v1.md SSOT 위임:

```markdown
## GitHub Workflow

사용자 요구사항 접수부터 PR merge 까지의 워크플로우 자동화. wrapper 가 templates/github-workflows/ 6종 fixture 제공:

- `story-init.yml` — Issue Forms (story.yml) 제출 → docs file 생성 + Phase 1 PR 자동 open
- `phase-label-invariant.yml` — `phase:*` single-active 강제
- `story-section-1-immutable.yml` — §1 line range 변경 PR 자동 reject
- `subissue-from-impl-manifest.yml` — §8.5 매핑표 → file 단위 sub-issue 자동 생성
- `phase-gate-mergeable.yml` — required status check (linked Story Issue 의 phase + gate 라벨 검사)
- `fix-ledger-sync.yml` — §10 FIX Ledger commit 감지 → Issue `[FIX #N]` mirror + `fix:<레인>-retry` 라벨 자동

상세 hierarchy (Epic / Story / sub-issue / Audit) · phase / gate / fix label 분류 · 코멘트 규칙 · 대시보드 search syntax 는 [docs/consumer-guide.md](docs/consumer-guide.md) §1.3 + [docs/inter-plugin-contracts/label-registry-v1.md](docs/inter-plugin-contracts/label-registry-v1.md) + [docs/inter-plugin-contracts/comment-prefix-registry-v1.md](docs/inter-plugin-contracts/comment-prefix-registry-v1.md) SSOT.

### Branch protection + Required status checks

- Main 브랜치: `phase-gate-mergeable` required status check + CODEOWNERS review 필수
- CODEOWNERS template: [`templates/CODEOWNERS.template`](templates/CODEOWNERS.template)
```

Edit `## GitHub Workflow` 헤더 line 561 부터 `## Story 작성 의무` 헤더 line 651 직전까지 대체.

Commit:
```bash
git add CLAUDE.md
git commit -m "refactor(cfp-44): compress GitHub Workflow (89→25 lines)

KEEP: wrapper-owned templates/github-workflows/ fixture listing + Branch 
protection. DELEGATE: hierarchy / phase&label taxonomy / 코멘트 규칙 / 
대시보드 → consumer-guide.md + label-registry-v1 + comment-prefix-registry."
```

- [ ] **Step 15: Compress ADR section (lines 530-555, 26→12)**

위치 / 생성 기준만 KEEP, DesignReview ADR 정합성 체크는 codeforge-design SSOT 위임:

```markdown
## ADR (`docs/adr/` SSOT)

- **위치**: `docs/adr/ADR-NNN-<slug>.md` (flat). frontmatter `category:` 필드로 분류
- **목록**: `Glob(docs/adr/ADR-*.md)` + `Grep` frontmatter category·status 필터
- **상세**: `Read(docs/adr/ADR-NNN-<slug>.md)`
- **CODEOWNERS** 가 `docs/adr/**` 을 architect team review 강제 → ADR 변경은 Phase 1 PR 로 architect 결재 필수

### 생성 기준

라이브러리·프레임워크 선택 / 아키텍처 패턴 / 데이터 저장·처리 / 인프라·배포 / 도메인 핵심 개념 (consumer overlay 가 도메인 특화 기준 추가)

DesignReview 의 ADR 정합성 체크 (Change Plan §3·§7 ↔ ADR 위반 검출) 는 [codeforge-review CLAUDE.md](https://github.com/mclayer/plugin-codeforge-review/blob/main/CLAUDE.md) SSOT.

### 페이지 템플릿

[`templates/adr.md`](https://github.com/mclayer/plugin-codeforge-design/blob/main/templates/adr.md) 참조 (CFP-40 으로 codeforge-design 추출 후 SSOT 위치).
```

Edit lines 530-555.

Commit:
```bash
git add CLAUDE.md
git commit -m "refactor(cfp-44): compress ADR section (26→12 lines)

KEEP: location / 생성 기준 / template pointer.
DELEGATE: DesignReview ADR 정합성 체크 → codeforge-review CLAUDE.md SSOT."
```

- [ ] **Step 16: DELETE Domain Knowledge section (lines 699-705, 7→0)**

codeforge-requirements CLAUDE.md (PR-3 머지 후) SSOT.

Edit:
```
old: "## Domain Knowledge\n\n[lines 700-705 본문]"
new: ""
```

Commit:
```bash
git add CLAUDE.md
git commit -m "refactor(cfp-44): delete Domain Knowledge section (7 lines)

Moved to codeforge-requirements CLAUDE.md SSOT (PR-3)."
```

### Sub-task 4c: Verification

- [ ] **Step 17: Run all wrapper lint chains**

```bash
bash scripts/check-doc-frontmatter.sh
bash scripts/check-doc-section-schema.sh
bash scripts/check-inter-plugin-contracts.sh
bash scripts/check-doc-links.sh
bash scripts/check-write-permission-redistribution.sh
```

Expected: 모든 lint PASS (또는 warning 만, error 없음).

- [ ] **Step 18: Wrapper grep test (CFP-44 spec §5.2)**

```bash
# Negative — 압축 대상 헤더 잔존 0
test "$(grep -c '^### .*4-way 이념\|^### .*Deputy Freshness\|^### .*ArchitectPL 라이프사이클' CLAUDE.md)" = "0"
test "$(grep -c '^### .*병렬 스폰 권장\|^### .*Codex CLI / 플러그인 필수' CLAUDE.md)" = "0"
test "$(grep -c '^## Domain Knowledge' CLAUDE.md)" = "0"
test "$(grep -c '^### Write 권한' CLAUDE.md)" = "0"

# Positive — boundary 절 존재
test "$(grep -c 'SSOT Boundary\|ADR-012' CLAUDE.md)" -ge "2"

# Line count
LINE_COUNT=$(wc -l < CLAUDE.md)
echo "Current line count: $LINE_COUNT"
test "$LINE_COUNT" -le "380"
```

Expected: 모든 test 통과. line count 380 이하 (target 330, buffer 까지 380).

만약 380 초과 시: 추가 압축 시도 — 책임 매트릭스 (52줄) 또는 Story 작성 의무 (38줄) trim 검토. 그래도 380 초과 시 design 재검토.

- [ ] **Step 19: Cross-link 정합 spot-check**

수동 검증:
- CLAUDE.md "lane plugin 참조" pointer 가 실제 lane plugin CLAUDE.md 의 갱신된 절을 가리킴
  - codeforge-test → "구현 테스트 lane 동작" 절 존재
  - codeforge-design → "4-way 이념 대립" body / ArchitectPL lifecycle / Deputy Freshness 절 존재
  - codeforge-requirements → "Clarification 재스폰" / "Domain Knowledge schema" 절 존재
- ADR-012 의 "3 SSOT 예외" 가 CLAUDE.md 본문의 책임 매트릭스 + 원인 판정 table + FIX Ledger schema 와 일치

### Sub-task 4d: PR creation + merge

- [ ] **Step 20: Push branch to origin**

```bash
git push -u origin cfp-44-wrapper-claudemd-compression
```

- [ ] **Step 21: Open PR**

```bash
gh pr create \
  --base main \
  --head cfp-44-wrapper-claudemd-compression \
  --title "fix(cfp-44): wrapper CLAUDE.md compression (705→~330 lines) + ADR-012" \
  --body "$(cat <<'EOF'
## Summary

CFP-43 후 잔존 부속 사항 진단. wrapper CLAUDE.md = composition + cross-cutting policy only 로 compression.

- 705 → ~330줄 (53% 절감, ~9k tokens 매 세션 절약)
- 신규 ADR-012 "Wrapper CLAUDE.md SSOT Boundary" 도입 — 미래 drift anchor
- 3 SSOT 예외 잔류 (책임 매트릭스 + 원인 판정 decision table + FIX Ledger §10 schema)
- lane internal · per-lane spawn detail · severity rule detail · GitHub workflow subsection 상세는 lane plugin SSOT 또는 playbook 위임

## Pre-condition (모두 머지 완료)

- PR-1 codeforge-test (MISSING gap 해소): #<N1>
- PR-2 codeforge-design (4-way + lifecycle + Freshness): #<N2>
- PR-3 codeforge-requirements (Clarification + Domain Knowledge schema): #<N3>

## Source

[CFP-44 spec](docs/superpowers/specs/2026-04-30-cfp-44-wrapper-claudemd-ssot-compression-design.md) — A1' (audit-driven minimum + Codex (gpt-5.4) boundary statement 보강안)

## Test plan

- [x] wrapper lint chain PASS (frontmatter / section-schema / inter-plugin-contracts / doc-links / write-permission)
- [x] §5.2 grep test (압축 대상 헤더 잔존 0, ADR-012 reference ≥ 2)
- [x] line count ≤ 380 (target 330)
- [x] cross-link spot-check (lane plugin 참조 → 실제 절 존재)
- [x] ADR-012 schema 검증 (frontmatter + section-schema)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 22: Merge PR**

```bash
gh pr merge <N> --merge
```

required status check 차단 시: `gh pr merge <N> --admin --merge`.

- [ ] **Step 23: Post-merge verification**

```bash
git fetch origin main && git checkout main && git pull
wc -l CLAUDE.md
grep -c "ADR-012\|SSOT Boundary" CLAUDE.md
ls docs/adr/ADR-012-wrapper-claudemd-ssot-boundary.md
```

Expected: line count ≤ 380, ADR-012 reference ≥ 2, ADR-012 file 존재.

---

## Self-review checklist

본 plan 작성 후 self-review 결과:

- **Spec coverage**: 
  - §2 결정 사항 D1-D5 → Tasks 1-4 covered ✓
  - §3 산출물 (4 PR matrix) → Tasks 1-4 1:1 ✓
  - §4 ordering (cross-repo 우선) → Task 4 pre-condition 명시 ✓
  - §5 test contract (PR 별 테스트 + grep + line count) → Sub-task 4c steps 17-19 ✓
  - §6 Phase 1/2 split (single-PR pattern) → 각 Task 의 Step 5/Step 21 PR creation ✓
  - §7 OOS (linter 후속 / playbook 재구조화 / agent md / migration-guide / symmetric backfill) → 본 plan scope 밖 명시적 ✓
  - §8 risks (line count / playbook drift / PARTIAL safe gap) → Step 18 fallback + Step 19 spot-check ✓
- **Placeholder scan**: TBD/TODO/"implement later" 0건. 모든 step 에 actual content (markdown body / mcp__github 명령 / git commit 명령). PR number `<N1>` 등은 user-fillable runtime value (PR creation 시점에 결정).
- **Type consistency**: branch name (cfp-44-{test,design,req,wrapper}-claude-md-{backfill,compression}) 일관. ADR 번호 12 일관. line count target 330 / buffer 380 일관.

---

## Plan complete and saved to `docs/superpowers/plans/2026-04-30-cfp-44-wrapper-claudemd-ssot-compression.md`.

Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, review between, fast iteration

**2. Inline Execution** — execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
