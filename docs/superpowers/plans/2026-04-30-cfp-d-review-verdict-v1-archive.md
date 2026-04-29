# review_verdict v1 Deprecated → Archived 전환 (CFP-D) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** review_verdict v1 contract status를 `Deprecated` → `Archived` 로 전환 + 21 wrapper files 의 v1 references 갱신 + ADR-008 §5.1 보강.

**Architecture (revision 2026-04-30 — option α):** 1 PR (wrapper 단독). canonical (codeforge-review) repo 에 v1 file 부재 확인 — wrapper 가 v1 단독 SSOT. status enum "Archived" 는 lint 이 이미 인정 (CFP-42, line 103) — schema 변경 없음. file 자체 보존 (ADR-008 §5 historical record 룰).

**Tech Stack:** git/Edit (wrapper PR), bash scripts/check-inter-plugin-contracts.sh + scripts/test-check-inter-plugin-contracts.sh (lint 검증).

---

## Task 별 컨텍스트

본 plan은 spec [`docs/superpowers/specs/2026-04-30-cfp-d-review-verdict-v1-archive-design.md`](../specs/2026-04-30-cfp-d-review-verdict-v1-archive-design.md) 의 §4-§5 를 task 화. 모든 wrapper 변경은 branch `cfp-d-v1-archive` (이미 spec commit 9fa7256 존재).

**전체 작업 범위 (21 files, wrapper 단독 — revision 2026-04-30 option α)**:
- wrapper (본 repo): 21 files (Task 1-7)
- canonical (codeforge-review repo): **N/A — v1 file 부재 확인** (원안 Task 1 폐기)

---

### ~~Task 1 (원안): canonical PR (codeforge-review repo)~~ — **폐기 (2026-04-30 revision option α)**

**폐기 사유**: 실행 시점 (2026-04-30) `mcp__github__get_file_contents(owner=mclayer, repo=plugin-codeforge-review, path=docs/inter-plugin-contracts/)` 결과 v1 file 부재. v2 만 존재. v1 은 wrapper repo 단독 SSOT (CFP-29 시점 wrapper 신설 후 canonical 으로 이동된 적 없음). canonical 작업 N/A.

**아래 원안 Task 1 step 들은 실행 안 함**. Task 2-8 → Task 1-7 로 renumber.

<details>
<summary>원안 Task 1 (참조용 보존)</summary>

### Task 1 (원안): canonical PR (codeforge-review repo)

**Files:**
- Modify (canonical, via mcp__github): `mclayer/plugin-codeforge-review` `docs/inter-plugin-contracts/review-verdict-v1.md`

**Branch (canonical):** `cfp-d-v1-archive`

- [ ] **Step 1: canonical 현재 file 확인**

```
mcp__github__get_file_contents(
  owner="mclayer",
  repo="plugin-codeforge-review",
  path="docs/inter-plugin-contracts/review-verdict-v1.md"
)
```

Expected: frontmatter `status: Deprecated`, body line 18 `# review_verdict v1 — Inter-plugin Contract (DEPRECATED)`.

- [ ] **Step 2: canonical branch 생성**

```
mcp__github__create_branch(
  owner="mclayer",
  repo="plugin-codeforge-review",
  branch="cfp-d-v1-archive",
  from_branch="main"
)
```

- [ ] **Step 3: canonical file 수정 (frontmatter status + authors entry + body header + warning)**

수정할 부분 (canonical file 의 line numbers는 wrapper sibling 과 동일하지 않을 수 있음 — sibling 만 "**상위 SSOT 위치**:" section 가짐):

frontmatter:
```yaml
status: Deprecated   →   status: Archived
```

`authors:` array 끝에 한 항목 추가:
```yaml
authors:
  - CFP-29 동결 (2026-04-28)
  - CFP-33 frontmatter backfill (2026-04-29)
  - CFP-35 status Active → Deprecated (v2 신설, 2026-04-29)
  - CFP-D status Deprecated → Archived (consumer 부재 확신, 2026-04-30)   # NEW
```

body header line:
```
# review_verdict v1 — Inter-plugin Contract (DEPRECATED)
   → 
# review_verdict v1 — Inter-plugin Contract (ARCHIVED)
```

body warning paragraph (canonical 의 corresponding line — Deprecated 시점 안내):
```
> **CFP-35 (2026-04-29) 이후 Deprecated**: codeforge-review plugin v1.0.0+ 부터 [`review-verdict-v2.md`](review-verdict-v2.md) self-write contract 사용. v1 contract surface (DocsAgent 경유 write 위임)는 codeforge v0.22.0 + codeforge-review v1.0.0 짝 부터 더 이상 호환 처리 안 함. 본 file은 audit·archive 목적으로 유지 (6 CFP 무사고 후 별도 cleanup CFP에서 file 삭제 예정).
```
   →
```
> **CFP-D (2026-04-30) 이후 Archived**: consumer 부재 확신 시점 (사용자 명시) Deprecated → Archived 전환. codeforge-review plugin v1.0.0+ 부터 [`review-verdict-v2.md`](review-verdict-v2.md) self-write contract 사용. v1 contract surface (DocsAgent 경유 write 위임)는 codeforge v0.22.0 + codeforge-review v1.0.0 짝 부터 호환 처리 안 함. 본 file은 historical record 로 영구 보존 (ADR-008 §5 룰 — 삭제 금지). lint scope 에 동일 schema 검증 적용 (status enum 만 다름).
```

```
mcp__github__create_or_update_file(
  owner="mclayer",
  repo="plugin-codeforge-review",
  path="docs/inter-plugin-contracts/review-verdict-v1.md",
  content="<full updated file content>",
  message="docs(cfp-d): review_verdict v1 status Deprecated → Archived\n\nconsumer 부재 확신 (사용자 명시 2026-04-30) 으로 grace period 불필요. Archived\n전환은 ADR-008 §5 historical record 보존 룰 준수 — file 자체 유지, status\n전환만. wrapper sibling sync PR 후속 (codeforge repo cfp-d-v1-archive).\n\nCo-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>",
  branch="cfp-d-v1-archive",
  sha="<sha from Step 1>"
)
```

- [ ] **Step 4: canonical PR 생성**

```
mcp__github__create_pull_request(
  owner="mclayer",
  repo="plugin-codeforge-review",
  title="docs(cfp-d): review_verdict v1 status Deprecated → Archived",
  body="(see body template below)",
  head="cfp-d-v1-archive",
  base="main"
)
```

PR body:
```markdown
## Summary
- review_verdict v1 contract 의 frontmatter `status: Deprecated` → `Archived` 전환
- body header `(DEPRECATED)` → `(ARCHIVED)` + warning paragraph 갱신
- authors array 에 CFP-D entry 추가

## 배경
consumer 부재 확신 (사용자 명시 2026-04-30) 으로 v1 grace period 불필요. wrapper repo CFP-D 에서 ADR-008 §5 보강 + 21 wrapper files 갱신 후속. 본 PR 은 sync 의 canonical 측 (PR 1/2). wrapper sibling sync PR 은 [codeforge#TBD] 에서 처리.

## ADR 정합성
- ADR-008 §5 (historical record 보존 룰): file 자체 유지 — 위반 0
- ADR-010 (sibling sync): 본 PR + wrapper sync PR 양쪽으로 enforce
- ADR-001 (review agent unification): v1 attribution 보존 — file 유지로 satisfied

## Test plan
- [ ] canonical lint regression: codeforge-review repo 의 frontmatter validator (해당 시) PASS
- [ ] wrapper sync PR 후 양쪽 status 일치 확인
- [ ] file 본문 mirror 일관성 (wrapper sibling 도 동일 status 갱신)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

- [ ] **Step 5: canonical PR 머지**

merge mode: rebase 또는 admin (codeforge-review repo 의 branch protection 정책에 따라):

```
mcp__github__merge_pull_request(
  owner="mclayer",
  repo="plugin-codeforge-review",
  pullNumber=<from Step 4>,
  merge_method="merge"
)
```

차단 시 admin merge 시도 (gh CLI fallback): `gh pr merge <num> --merge --admin --repo mclayer/plugin-codeforge-review --delete-branch`

Expected: PR merged, branch `cfp-d-v1-archive` 삭제됨.

</details>

---

### Task 1: wrapper v1 status transition (file 1)

**Files:**
- Modify: `docs/inter-plugin-contracts/review-verdict-v1.md` (wrapper 단독 SSOT — canonical 부재 확인 후)

**Branch:** `cfp-d-v1-archive` (현재 작업 중)

- [ ] **Step 1: wrapper frontmatter status 전환**

[`docs/inter-plugin-contracts/review-verdict-v1.md`](../../inter-plugin-contracts/review-verdict-v1.md) line 4:

`status: Deprecated`
   →
`status: Archived`

- [ ] **Step 2: wrapper sibling authors entry 추가**

[`docs/inter-plugin-contracts/review-verdict-v1.md`](../../inter-plugin-contracts/review-verdict-v1.md) line 12-15. 끝에 한 항목 추가:

```yaml
authors:
  - CFP-29 동결 (2026-04-28)
  - CFP-33 frontmatter backfill (2026-04-29)
  - CFP-35 status Active → Deprecated (v2 신설, 2026-04-29)
  - CFP-D status Deprecated → Archived (consumer 부재 확신, 2026-04-30)
```

- [ ] **Step 3: wrapper sibling body header line 18**

`# review_verdict v1 — Inter-plugin Contract (DEPRECATED)`
   →
`# review_verdict v1 — Inter-plugin Contract (ARCHIVED)`

- [ ] **Step 4: wrapper sibling body warning paragraph (line 20)**

기존:
```
> **CFP-35 (2026-04-29) 이후 Deprecated**: codeforge-review plugin v1.0.0+ 부터 [`review-verdict-v2.md`](review-verdict-v2.md) self-write contract 사용. v1 contract surface (DocsAgent 경유 write 위임)는 codeforge v0.22.0 + codeforge-review v1.0.0 짝 부터 더 이상 호환 처리 안 함. 본 file은 audit·archive 목적으로 유지 (6 CFP 무사고 후 별도 cleanup CFP에서 file 삭제 예정).
```

대체:
```
> **CFP-D (2026-04-30) 이후 Archived**: consumer 부재 확신 시점 (사용자 명시) Deprecated → Archived 전환. codeforge-review plugin v1.0.0+ 부터 [`review-verdict-v2.md`](review-verdict-v2.md) self-write contract 사용. v1 contract surface (DocsAgent 경유 write 위임)는 codeforge v0.22.0 + codeforge-review v1.0.0 짝 부터 호환 처리 안 함. 본 file은 historical record 로 영구 보존 (ADR-008 §5 룰 — 삭제 금지). lint scope 에 동일 schema 검증 적용 (status enum 만 다름).
```

- [ ] **Step 5: lint 사전 점검**

Run: `bash scripts/check-inter-plugin-contracts.sh`

Expected: exit 0 (status enum "Archived" 인정 — line 103 의 enum set 에 이미 포함).

- [ ] **Step 6: Commit**

```bash
git add docs/inter-plugin-contracts/review-verdict-v1.md
git commit -m "docs(cfp-d): wrapper sibling review-verdict-v1 status Deprecated → Archived

frontmatter status + authors entry + body header + warning paragraph 갱신.
canonical (codeforge-review) PR 1 와 verbatim 일치 (sibling sync 의무 — ADR-010).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: SSOT registry update (MANIFEST.yaml + CLAUDE.md table)

**Files:**
- Modify: `docs/inter-plugin-contracts/MANIFEST.yaml`
- Modify: `CLAUDE.md`

- [ ] **Step 1: MANIFEST.yaml v1 entry status 갱신**

[`docs/inter-plugin-contracts/MANIFEST.yaml`](../../inter-plugin-contracts/MANIFEST.yaml) line 11:

기존:
```yaml
      - { file: review-verdict-v1.md, contract_version: "1.0", status: Deprecated }
```

대체:
```yaml
      - { file: review-verdict-v1.md, contract_version: "1.0", status: Archived }
```

- [ ] **Step 2: CLAUDE.md "Inter-plugin Contract" 표 갱신**

[`CLAUDE.md`](../../../CLAUDE.md) line 502:

기존:
```
| `review_verdict` | codeforge-review | review-verdict-v1.md (Deprecated) · review-verdict-v2.md (Active) |
```

대체:
```
| `review_verdict` | codeforge-review | review-verdict-v1.md (Archived) · review-verdict-v2.md (Active) |
```

- [ ] **Step 3: lint 회귀 점검**

Run: `bash scripts/check-inter-plugin-contracts.sh`

Expected: exit 0.

- [ ] **Step 4: Commit**

```bash
git add docs/inter-plugin-contracts/MANIFEST.yaml CLAUDE.md
git commit -m "docs(cfp-d): MANIFEST + CLAUDE.md 표에서 v1 status Archived 반영

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: ADR-008 §5.1 보강

**Files:**
- Modify: `docs/adr/ADR-008-inter-plugin-contract-versioning.md`

- [ ] **Step 1: ADR-008 §5 끝에 §5.1 단락 추가**

[`docs/adr/ADR-008-inter-plugin-contract-versioning.md`](../../adr/ADR-008-inter-plugin-contract-versioning.md) line 70 다음 (§5 끝, §6 시작 전) 에 추가:

기존 (line 67-72):
```markdown
### 5. SSOT 위치 룰

- `docs/inter-plugin-contracts/review-verdict-v<MAJOR>.md` — 상세 schema 본문 (현재 v1)
- `CLAUDE.md` "## Inter-plugin Contract" 섹션 — 요약 + cross-ref
- 새 MAJOR 시점에 `review-verdict-v<NEW>.md` 신설, 이전 file은 historical record로 유지 (삭제 금지)

### 6. enforcement (현재 상태 + 향후)
```

대체 (5.1 단락 추가):
```markdown
### 5. SSOT 위치 룰

- `docs/inter-plugin-contracts/review-verdict-v<MAJOR>.md` — 상세 schema 본문 (현재 v1)
- `CLAUDE.md` "## Inter-plugin Contract" 섹션 — 요약 + cross-ref
- 새 MAJOR 시점에 `review-verdict-v<NEW>.md` 신설, 이전 file은 historical record로 유지 (삭제 금지)

### 5.1 Deprecated → Archived 전환 트리거 (CFP-D 보강, 2026-04-30)

`Deprecated` 상태의 contract file 은 다음 조건 모두 충족 시 `Archived` 로 전환:

1. consumer 부재 확신 (author 가 release / install metric 또는 사용자 confirm 으로 검증)
2. 후속 MAJOR 가 1개 이상 release 후 일정 grace period 경과 (case-by-case, default 6 CFP)
3. 전환 시 canonical + sibling 양쪽 frontmatter `status` 동시 갱신 (ADR-010 sync 의무)

`Archived` 상태도 file 자체는 유지 — historical record 보존 의무는 §5 본문 룰 그대로. lint (kind:contract) 은 status 값과 무관하게 동일 schema 강제 (`scripts/check-inter-plugin-contracts.sh` 의 status enum `{Draft, Active, Deprecated, Archived}` 모두 통과). consumer 가 재출현하면 author 가 즉시 Active 또는 새 MAJOR 발의 결정 (Archived → Active 직접 전환 금지 — historical record 일관성 위배).

**최초 적용**: review_verdict v1 (CFP-D, 2026-04-30) — codeforge-review canonical + codeforge wrapper sibling 양쪽 동기화.

### 6. enforcement (현재 상태 + 향후)
```

- [ ] **Step 2: Commit**

```bash
git add docs/adr/ADR-008-inter-plugin-contract-versioning.md
git commit -m "docs(cfp-d): ADR-008 §5.1 보강 — Deprecated → Archived 전환 트리거 정의

3 조건: consumer 부재 확신 + 후속 MAJOR 1+ release + canonical/sibling 동시 sync.
최초 적용 사례 review_verdict v1 (CFP-D, 2026-04-30) 명시.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Active narrative 갱신 (orchestrator-playbook + migration-guide)

**Files:**
- Modify: `docs/orchestrator-playbook.md`
- Modify: `docs/migration-guide.md`

**Context:** 두 file 모두 "Deprecated" literal 은 부재. 그러나 stale narrative ("review_verdict v1 typed contract" 류 — 현재 active 는 v2) 가 있어 spec §4.4 의 "Active narrative 갱신" intent 충족 위해 v2 로 update.

- [ ] **Step 1: orchestrator-playbook.md line 26 narrative 갱신**

기존:
```markdown
**CFP-29 Phase 1 (BREAKING v0.17.0) 이후**: 5 review agent (Design/Code/SecurityTest PL + Claude/Codex worker)는 별도 plugin [codeforge-review](https://github.com/mclayer/plugin-codeforge-review)로 추출됨. Orchestrator는 본 playbook의 관점에서 이들을 **외부 plugin agent**로 spawn하며, 결과는 `review_verdict v1` typed contract ([`docs/inter-plugin-contracts/review-verdict-v1.md`](inter-plugin-contracts/review-verdict-v1.md))로 수령한다.
```

대체:
```markdown
**CFP-29 Phase 1 (BREAKING v0.17.0) 이후**: 5 review agent (Design/Code/SecurityTest PL + Claude/Codex worker)는 별도 plugin [codeforge-review](https://github.com/mclayer/plugin-codeforge-review)로 추출됨. Orchestrator는 본 playbook의 관점에서 이들을 **외부 plugin agent**로 spawn하며, 결과는 `review_verdict v2` typed contract ([`docs/inter-plugin-contracts/review-verdict-v2.md`](inter-plugin-contracts/review-verdict-v2.md))로 수령한다 (v1 은 CFP-D 시점 Archived).
```

- [ ] **Step 2: migration-guide.md line 98 narrative 갱신**

기존 (line 97-99):
```markdown
- consumer overlay에 5 review agent 중 어느 것이라도 override 하던 경우 (드뭄): overlay 파일을 codeforge-review repo의 동일 path 구조로 이동
- review packet/verdict schema는 v1 contract — overlay 호환성 영향 없음
```

대체:
```markdown
- consumer overlay에 5 review agent 중 어느 것이라도 override 하던 경우 (드뭄): overlay 파일을 codeforge-review repo의 동일 path 구조로 이동
- review packet/verdict schema는 v2 contract (v1 은 CFP-D 시점 Archived) — overlay 호환성 영향 없음
```

- [ ] **Step 3: migration-guide.md line 109 narrative 갱신**

기존:
```markdown
- codeforge-review (PL) → codeforge core: `review_verdict v1` 반환 (typed)
```

대체:
```markdown
- codeforge-review (PL) → codeforge core: `review_verdict v2` 반환 (typed, v1 은 CFP-D 시점 Archived)
```

- [ ] **Step 4: migration-guide.md line 112 schema reference 갱신**

기존:
```markdown
상세 schema: codeforge core repo의 [`docs/inter-plugin-contracts/review-verdict-v1.md`](inter-plugin-contracts/review-verdict-v1.md). Versioning 룰: [ADR-008](adr/ADR-008-inter-plugin-contract-versioning.md).
```

대체:
```markdown
상세 schema: codeforge core repo의 [`docs/inter-plugin-contracts/review-verdict-v2.md`](inter-plugin-contracts/review-verdict-v2.md) (active). v1 (Archived, historical record): [`docs/inter-plugin-contracts/review-verdict-v1.md`](inter-plugin-contracts/review-verdict-v1.md). Versioning + archive 룰: [ADR-008](adr/ADR-008-inter-plugin-contract-versioning.md) §5/§5.1.
```

- [ ] **Step 5: Commit**

```bash
git add docs/orchestrator-playbook.md docs/migration-guide.md
git commit -m "docs(cfp-d): active narrative — v1 references → v2 (v1 Archived 명시)

orchestrator-playbook line 26: review_verdict v1 → v2 + Archived 안내
migration-guide line 98/109/112: 현재 active schema v2 + v1 Archived 명시

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: History 14 files 일괄 치환

**Files (14):**
1. `docs/superpowers/specs/2026-04-28-cfp-29-codeforge-review-extraction-design.md`
2. `docs/superpowers/specs/2026-04-28-docsagent-scope-reduction-and-review-extraction-design.md`
3. `docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`
4. `docs/superpowers/specs/2026-04-29-cfp-42-inter-plugin-contract-sibling-backfill-design.md`
5. `docs/superpowers/specs/2026-04-30-cfp-43-wrapper-only-docs-cleanup-design.md`
6. `docs/superpowers/plans/2026-04-28-cfp-29-phase-1-codeforge-review-extract.md`
7. `docs/superpowers/plans/2026-04-29-cfp-32-foundation-invariant-ssot.md`
8. `docs/superpowers/plans/2026-04-29-cfp-42-inter-plugin-contract-sibling-backfill.md`
9. `docs/superpowers/plans/2026-04-30-cfp-43-wrapper-only-docs-cleanup.md`
10. `docs/change-plans/cfp-42-inter-plugin-contract-sibling-backfill.md`
11. `docs/stories/CFP-28.md`
12. `docs/retros/2026-04-29-zeta-arc-completion.md`
13. `docs/retros/2026-04-29-staged-epsilon-completion.md`
14. `docs/adr/ADR-009-wrapper-only-decomposition.md`

**전략 (Risk 완화):**
- per-file Edit (sed -i 일괄 금지 — 의도 외 매치 회피)
- 정확한 pattern 만 매치: `(Deprecated)` literal 또는 `status: Deprecated` literal 옆에 review-verdict-v1 가 있는 행
- 단순 `v1` 또는 `review-verdict-v1.md` path 참조는 그대로 유지 (file 보존됨)

- [ ] **Step 1: per-file pre-grep으로 정확 line 식별**

Run (각 파일별로 Grep 사용):
```
Grep("(Deprecated|status: Deprecated)", path="<each file>", output_mode="content", -n=true)
```

Expected hits per file (사전 확인된 결과):
- File 1 (cfp-29 design spec): "v1 contract" 류 narrative — Deprecated literal 매치 0 가능. **수정 불필요** 시 skip
- File 3 (cfp-31 design spec): line 376 "archived (deprecated 표시)" — 수정 검토
- File 4 (cfp-42 design spec): line 199 MANIFEST 예시 `status: Deprecated` 
- File 5 (cfp-43 design spec): "v1 (Deprecated)" 류
- File 8 (cfp-42 plan): line 308 MANIFEST 예시 `status: Deprecated`, line 1017 표 `(Deprecated)`
- File 11 (CFP-28 Story): "(Deprecated)" 류 가능
- File 12 (zeta-arc retro): line 75 "현재 Deprecated status 표기만"
- File 14 (ADR-009): line 12 + line 95 `(Deprecated)`

- [ ] **Step 2: File별 Edit (정확 매치만)**

각 file 의 매치된 line 에 대해 다음 변환 패턴 적용:

| Found pattern | Replace with |
|---|---|
| `review-verdict-v1.md (Deprecated)` | `review-verdict-v1.md (Archived)` |
| `review-verdict-v1.md, contract_version: "1.0", status: Deprecated` | `review-verdict-v1.md, contract_version: "1.0", status: Archived` |
| `현재 Deprecated status 표기만` (zeta-arc retro 맥락) | `현재 Archived status 표기 (CFP-D, 2026-04-30 전환)` |
| `archived (deprecated 표시)` (cfp-31 spec 맥락) | `archived (Archived status 표시 — CFP-D, 2026-04-30 전환)` |

단, **history file 의 retroactive update 원칙**:
- 그 시점 이후 발생한 사건을 retroactively narrative 에 끼워넣지 않음
- 단순한 status label literal 만 update (위 표 패턴)

- [ ] **Step 3: history 14 files 변경 후 grep verification**

Run:
```bash
grep -rn "review-verdict-v1.*Deprecated" docs/superpowers/ docs/change-plans/ docs/stories/ docs/retros/ docs/adr/
```

Expected: 0 hits. (CHANGELOG.md 의 line 205, 217 은 v0.22 시점 record — 본 task scope 밖, Task 7 에서 처리)

Run:
```bash
grep -rn "(deprecated 표시)" docs/superpowers/
```

Expected: 0 hits.

- [ ] **Step 4: lint 회귀 점검**

Run: `bash scripts/check-inter-plugin-contracts.sh`

Expected: exit 0.

Run: `bash scripts/test-check-inter-plugin-contracts.sh`

Expected: T1-T6 모두 PASS, exit 0.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/ docs/change-plans/ docs/stories/ docs/retros/ docs/adr/
git commit -m "docs(cfp-d): history 14 files — 'v1 (Deprecated)' literal → 'v1 (Archived)'

per-file Edit 로 정확 매치만 치환 (sed -i 금지 — 의도 외 매치 회피).
단순 path reference (review-verdict-v1.md) 는 그대로 유지 (file 보존, link 작동).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: CHANGELOG entry append + final lint

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: CHANGELOG line 1 (또는 가장 최근 entry 위) 에 새 entry append**

기존 line 1-5 (대략):
```markdown
# Changelog

All notable changes ... (헤더)

## [Unreleased]
```

대체 (`## [Unreleased]` 다음 또는 첫 entry 가 어디 있던 그 위치 의 next entry):
```markdown
## [Unreleased] — CFP-D (2026-04-30)

### Changed
- review_verdict v1 contract status `Deprecated` → `Archived` (consumer 부재 확신, 사용자 명시 2026-04-30)
- ADR-008 §5.1 보강 — `Deprecated → Archived` 전환 트리거 정의 (3 조건: consumer 부재 + 후속 MAJOR 1+ release + canonical/sibling sync)
- canonical (codeforge-review) + wrapper sibling 양쪽 동기화 (ADR-010 sync 의무)
- 21 wrapper files v1 references 갱신 (status registry + ADR-008 + active narrative + history 14 files)

### Migration
- consumer 부재 — 액션 불필요
- v1 file 자체는 historical record 로 영구 보존 (ADR-008 §5 룰)
- 향후 v1 schema 참조하던 코드 (없음 — v2 active 부터 v1 사용 0) 는 v2 로 migrate 필요
```

- [ ] **Step 2: 최종 lint full pass**

Run: `bash scripts/check-inter-plugin-contracts.sh`

Expected: exit 0.

Run: `bash scripts/test-check-inter-plugin-contracts.sh`

Expected: T1-T6 모두 PASS.

Run (잔재 확인):
```bash
grep -rn "review-verdict-v1.*Deprecated" CLAUDE.md docs/inter-plugin-contracts/MANIFEST.yaml docs/adr/ docs/orchestrator-playbook.md docs/migration-guide.md
```

Expected: 0 hits (active SSOT 잔재 0 확인).

Run (history 잔재 확인):
```bash
grep -rn "review-verdict-v1.*Deprecated" docs/superpowers/ docs/change-plans/ docs/stories/ docs/retros/ docs/adr/ADR-009-wrapper-only-decomposition.md
```

Expected: 0 hits.

Run (Archived 적용 확인):
```bash
grep -rn "review-verdict-v1.*Archived" docs/inter-plugin-contracts/MANIFEST.yaml CLAUDE.md
```

Expected: ≥ 2 hits.

- [ ] **Step 3: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs(cfp-d): CHANGELOG entry — review_verdict v1 Deprecated → Archived

CFP-D 변경 사항 unreleased 항목으로 기록.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: wrapper PR open + admin merge

**Branch:** `cfp-d-v1-archive` (commits 누적: spec + plan + Task 1-6)

**Pre-condition:** Task 1-6 모두 commit 완료 (canonical PR 사전조건 폐기 — option α).

- [ ] **Step 1: branch push**

```bash
git push -u origin cfp-d-v1-archive
```

- [ ] **Step 2: wrapper PR 생성**

```bash
gh pr create --title "docs(cfp-d): review_verdict v1 status Deprecated → Archived (22 files)" --body "$(cat <<'EOF'
## Summary
- review_verdict v1 contract status `Deprecated` → `Archived` 전환
- canonical (codeforge-review) + wrapper sibling 양쪽 동기화 (ADR-010)
- ADR-008 §5.1 보강 — 전환 트리거 3 조건 정의
- 21 wrapper files v1 references 갱신 (active SSOT + history)

## 배경
consumer 부재 확신 (사용자 명시 2026-04-30) 으로 v1 grace period 불필요. ADR-008 §5 historical record 보존 룰 준수 — file 자체 유지, status 전환만.

## Files (22 = canonical 1 + wrapper 21)

**A. status 전환** (2): canonical (separate PR) + wrapper sibling
**B. SSOT registry** (2): MANIFEST.yaml + CLAUDE.md
**C. ADR-008 §5.1 보강** (1): docs/adr/ADR-008-*.md
**D. Active narrative** (2): orchestrator-playbook + migration-guide (v1 → v2 references)
**E. History** (14): superpowers spec/plan + change-plans + retros + ADR-009
**F. CHANGELOG** (1)

## ADR 정합성
- ADR-008: §5 보강 (위반 0)
- ADR-009: 무영향
- ADR-010: canonical + sibling 동시 sync 준수
- ADR-001: v1 attribution 보존 — file 유지로 satisfied

## Test plan
- [ ] `bash scripts/check-inter-plugin-contracts.sh` exit 0
- [ ] `bash scripts/test-check-inter-plugin-contracts.sh` T1-T6 모두 PASS
- [ ] `grep -rn "review-verdict-v1.*Deprecated"` 본 PR scope 안에서 0 hits
- [ ] canonical PR (codeforge-review#TBD) 머지 후 양쪽 status 일치

## Linked
- canonical PR: mclayer/plugin-codeforge-review#TBD (먼저 merge)
- spec: docs/superpowers/specs/2026-04-30-cfp-d-review-verdict-v1-archive-design.md
- plan: docs/superpowers/plans/2026-04-30-cfp-d-review-verdict-v1-archive.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 3: PR phase-gate-mergeable 차단 확인 (meta-CFP 패턴)**

본 PR 은 docs/stories/CFP-D.md 부재 — phase-gate-mergeable required check 차단 예상. CFP-42, CFP-43 와 동일.

- [ ] **Step 4: admin merge**

```bash
gh pr merge <PR#> --merge --admin --delete-branch
```

Expected: PR merged, remote branch 삭제됨.

- [ ] **Step 5: local main sync**

```bash
git checkout main
git pull origin main
git branch -d cfp-d-v1-archive
```

Expected: cfp-d-v1-archive local 도 삭제됨.

- [ ] **Step 6: post-merge 정합성 확인**

Run: `bash scripts/check-inter-plugin-contracts.sh`

Expected: exit 0.

Run (final state 확인):
```bash
grep -E "v1\.0.*Archived" docs/inter-plugin-contracts/MANIFEST.yaml
```

Expected: 1 hit (`status: Archived` in v1 entry).

```bash
mcp__github__get_file_contents(
  owner="mclayer",
  repo="plugin-codeforge-review",
  path="docs/inter-plugin-contracts/review-verdict-v1.md"
)
```

Expected: frontmatter `status: Archived` (canonical PR 머지된 상태).

---

## 검증 종합

본 plan 실행 후 spec §8 Test Contract:
- T-1: `bash scripts/check-inter-plugin-contracts.sh` exit 0 ✓
- T-2: `bash scripts/test-check-inter-plugin-contracts.sh` T1-T6 모두 PASS ✓
- T-3: MANIFEST entry `Archived` 1 hit ✓
- T-4: **N/A — canonical 부재 확인 (option α)**
- T-5: active SSOT "Deprecated" 잔재 0 ✓
- T-6: history 14 files 치환 0 hit (Deprecated literal) ✓

총 변경 (revision 2026-04-30 option α):
- wrapper PR: 21 files (Task 1: 1 + Task 2: 2 + Task 3: 1 + Task 4: 2 + Task 5: 14 + Task 6: 1)
- canonical PR: N/A
- 총 21 files ✓ (spec §4 revised 일치)
