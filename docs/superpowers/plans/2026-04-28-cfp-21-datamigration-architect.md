# CFP-21 DataMigrationArchitectAgent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 6번째 deputy `DataMigrationArchitectAgent` 신설 — Codex audit #2 ("데이터 layer 결정 누락 위험") 직접 적용. ADR-006 (TestContractArch) 패턴 그대로 차용. BREAKING v0.14.0.

**Architecture:** SecurityArchitectAgent를 base로 DataMigration 도메인으로 substitute. agent md 신설 + 7 SSOT 동기화 (CLAUDE.md / playbook / change-plan template / design.md checklist / Claude·CodexReview category enum / ADR-007 / CHANGELOG + migration-guide). plugin-meta-na 패턴 — §8/§9 N/A.

**Tech Stack:** Markdown (SSOT 문서) · YAML frontmatter · invariant-check.yml CI parity · ripgrep verify · git heredoc commit.

**파일 책임 매핑** (Task → File → 변경 유형):
- Task 1: `agents/DataMigrationArchitectAgent.md` (신설)
- Task 2: `agents/{ArchitectPLAgent,ArchitectAgent}.md` (deputy 4→5 references, Phase 1.5 sanity check 1 항목 추가)
- Task 3: 4 deputy md (cross-ref 1줄) + `templates/change-plan.md` (§11 신설)
- Task 4: `templates/review-checklists/design.md` (§11 P0 차단 룰) + `agents/{ClaudeReview,CodexReview}Agent.md` (category enum +1)
- Task 5: `docs/orchestrator-playbook.md` (스폰 시퀀스 4→5) + `CLAUDE.md` (다이어그램·매트릭스·FIX decision table·Never-skippable·"23 core"→"24 core")
- Task 6: `docs/adr/ADR-007-datamigration-architect.md` (신설) + `CHANGELOG.md` (v0.14.0 BREAKING) + `.claude-plugin/plugin.json` (0.13.0→0.14.0) + `docs/migration-guide.md` (v0.13.0→v0.14.0 절)
- Task 7: invariant-check 8 step verify + Story doc + PR open + admin merge

**plugin-meta-na 처리**: 본 CFP 자기 적용 안 함 (paradox). 13-15 commit이 모두 markdown SSOT. 단일 PR + admin override merge (CFP-19 패턴).

---

## Task 1: agents/DataMigrationArchitectAgent.md 신설

**Files:**
- Create: `agents/DataMigrationArchitectAgent.md`

SecurityArchitectAgent를 base로 DataMigration 도메인 substitute.

- [ ] **Step 1: Write file** — frontmatter (permissions SecurityArch 동일) + 본문 (포지션·핵심 미션·입력·산출물 §11.1-11.6·deputy 관계·null 결과 권한·제약·도구·스킬·문서화 표준).

내용은 `agents/SecurityArchitectAgent.md` 구조 그대로 mirror하되:
- 도메인: 보안 → 데이터 무결성/마이그레이션
- §7.x → §11.x
- OWASP/CWE → DB migration patterns (online schema migration, blue-green deploy, pt-online-schema-change, gh-ost, dual-write, expand-contract pattern)
- "공격자 관점" → "데이터 무결성 advocate 관점"
- "trust boundary" → "schema 진화 boundary"
- Trust boundary와 SecurityTest의 시점 분리 → DataMigration과 구현/구현테스트 lane의 시점 분리

- [ ] **Step 2: Verify**

```bash
ls -la agents/DataMigrationArchitectAgent.md && grep -c "## " agents/DataMigrationArchitectAgent.md
```

Expected: file exists, ≥10 sections.

- [ ] **Step 3: Commit**

```
feat(cfp-21): DataMigrationArchitectAgent 신설 — 6번째 deputy (1/7)
```

---

## Task 2: ArchitectPLAgent + ArchitectAgent deputy 4→5

**Files:**
- Modify: `agents/ArchitectPLAgent.md`
- Modify: `agents/ArchitectAgent.md`

- [ ] **Step 1: ArchitectPLAgent.md** — 다음 행 모두 4→5 deputy:
  - "4 deputy 모두 병렬 수령 없이 단독 설계 결정 금지" → "5 deputy 모두 병렬 수령..."
  - Phase 1 spawn diagram에 `└─ spawn → DataMigrationArchitectAgent → §11 데이터 마이그레이션 input` 추가
  - Phase 3 검수 메타-규칙 1번 (§섹션별 deputy author input 통합 정합성)에 `§11 → DataMigrationArchitectAgent 마이그레이션 안전성 매핑 반영 완결성` 1행 추가
  - Phase 1.5 sanity check 항목 1 (§섹션 author input 표면 형식)에 `DataMigrationArchitectAgent → §11 데이터 마이그레이션 input (§11.1-11.5 또는 §11.6 N/A)` 1행 추가

- [ ] **Step 2: ArchitectAgent.md** — 다음 행 모두 4→5 deputy:
  - "deputy 4인 산출물" → "deputy 5인 산출물"
  - 입력 list에 `DataMigrationArchitectAgent` 추가
  - §11 author input 라인 추가 (§7 동형 보강)

- [ ] **Step 3: Verify**

```bash
grep -c "5 deputy\|deputy 5인\|DataMigrationArchitect" agents/ArchitectPLAgent.md agents/ArchitectAgent.md
```

- [ ] **Step 4: Commit**

```
feat(cfp-21): ArchitectPLAgent + ArchitectAgent — deputy 4→5 (2/7)
```

---

## Task 3: 4 deputy cross-ref + change-plan template §11

**Files:**
- Modify: `agents/CodebaseMapperAgent.md`
- Modify: `agents/RefactorAgent.md`
- Modify: `agents/SecurityArchitectAgent.md`
- Modify: `agents/TestContractArchitectAgent.md`
- Modify: `templates/change-plan.md`

- [ ] **Step 1: 4 deputy md cross-ref 1줄 추가** — 각 md의 "도형 대립 비참여" 1줄 절에 DataMigrationArchitectAgent 추가:

기존 (예시):
> TestContractArchitectAgent는 §8 author input contributor (도형 대립 비참여 — Mapper/Refactor/SecurityArch 3-way와 별개 영역).

변경:
> TestContractArchitectAgent는 §8 author input contributor (도형 대립 비참여 — Mapper/Refactor/SecurityArch 3-way와 별개 영역). DataMigrationArchitectAgent는 §11 author input contributor (동일 비참여).

- [ ] **Step 2: templates/change-plan.md** — §10 다음에 신규 §11 추가:

§10 끝 anchor + `## DocsAgent 저장·미러링 의무` 헤더 직전에 §11 절 삽입 (spec §2.2 §11.1-11.6 구조).

- [ ] **Step 3: Verify**

```bash
grep -c "DataMigrationArchitect" agents/CodebaseMapperAgent.md agents/RefactorAgent.md agents/SecurityArchitectAgent.md agents/TestContractArchitectAgent.md && grep -n "§11" templates/change-plan.md
```

- [ ] **Step 4: Commit**

```
feat(cfp-21): 4 deputy cross-ref + change-plan §11 데이터 마이그레이션 (3/7)
```

---

## Task 4: design.md checklist + Claude/Codex category enum

**Files:**
- Modify: `templates/review-checklists/design.md`
- Modify: `agents/ClaudeReviewAgent.md`
- Modify: `agents/CodexReviewAgent.md`

- [ ] **Step 1: design.md** — Category enum에 `data-migration` 추가 + Severity 자동 룰에 §11 차단 룰 3건 추가:
  - **§11 데이터 마이그레이션 누락** → P0 강제 (`data-migration`)
  - **§11.6 N/A 사유 부재** → P0 강제 (`data-migration`)
  - **Architect 통합 판정에서 DataMigrationArch 마이그레이션 안전성 매핑 미반영** → P0 강제 (`data-migration`)
  - "## §11 데이터 마이그레이션 감사" 섹션 신설 (§7 보안 설계 감사 패턴 동일)

- [ ] **Step 2: ClaudeReviewAgent.md / CodexReviewAgent.md** — lane=design category enum list에 `data-migration` 추가 (기존 7개 → 8개).

- [ ] **Step 3: Verify invariant-check Step 6 + Step 8**

```bash
# Category enum parity
grep "data-migration" templates/review-checklists/design.md agents/ClaudeReviewAgent.md agents/CodexReviewAgent.md agents/DesignReviewPLAgent.md | wc -l
# Expected: ≥4 (1 SSOT + 3 mirrors)

# Severity overrides count parity
grep -c "→ \*\*P0\*\*\|→ P0 강제" templates/review-checklists/design.md
```

- [ ] **Step 4: Commit**

```
feat(cfp-21): design.md checklist + Claude/Codex category enum data-migration (4/7)
```

---

## Task 5: orchestrator-playbook + CLAUDE.md 동기화

**Files:**
- Modify: `docs/orchestrator-playbook.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: orchestrator-playbook.md** — 모든 "4 deputy" / "deputy 4인" → "5 deputy" / "deputy 5인". §3.1 스폰 시퀀스 [설계] block에 DataMigrationArchitectAgent line 추가. §3.2 에이전트별 특이 블록 표에 DataMigrationArchitectAgent 행 추가.

- [ ] **Step 2: CLAUDE.md** — 다음 항목 갱신:
  - 첫 단락 "23 core 에이전트" → "24 core 에이전트"
  - 다이어그램 [설계] lane에 DataMigrationArchitectAgent 추가
  - Never-skippable 설계 lane 목록에 DataMigrationArchitectAgent 추가
  - 책임 매트릭스 (Design / DesignReview / CodeReview / SecurityTest)에 신규 행:
    * `§11 Schema 변경 영향` / `§11 Migration 전략` / `§11 Rollback 경로` / `§11 Data integrity invariant` / `§11 누락 / N/A 사유 부재`
  - FIX decision table 1행 추가:
    * `Migration FAIL · data integrity 위반 · rollback 실패` → 1차 가정 **설계** (§11 부재·모순)
  - 스폰 시퀀스 [설계] block 갱신 (4→5 deputy)
  - 3-way 대립 절 → 4-way (Mapper/Refactor/SecurityArch + DataMigrationArch as parallel advocates) **재명명**: "CodebaseMapper ↔ Refactor ↔ SecurityArchitect ↔ DataMigrationArchitect 4-way 이념 대립" (TestContractArch는 별도 도형, 이전과 동일하게 비참여)
  - Plugin Meta 적용 절: "병렬 스폰 권장 / 설계: 5 deputy 병렬"

- [ ] **Step 3: Verify**

```bash
grep -c "24 core\|deputy 5인\|5 deputy\|DataMigrationArchitect" CLAUDE.md docs/orchestrator-playbook.md
```

- [ ] **Step 4: Commit**

```
feat(cfp-21): orchestrator-playbook + CLAUDE.md — 5 deputy + 24 core sync (5/7)
```

---

## Task 6: ADR-007 + CHANGELOG v0.14.0 + plugin.json + migration-guide

**Files:**
- Create: `docs/adr/ADR-007-datamigration-architect.md`
- Modify: `CHANGELOG.md`
- Modify: `.claude-plugin/plugin.json`
- Modify: `docs/migration-guide.md`

- [ ] **Step 1: ADR-007 작성** — ADR-006 (TestContractArch) 본문 구조 그대로 mirror, 도메인만 DataMigration으로 substitute. status=Accepted, category=Team & Process, date=2026-04-28.

- [ ] **Step 2: CHANGELOG.md** — `## [0.13.0]` 위에 새 entry:

```
## [0.14.0] - 2026-04-28 (BREAKING)

### CFP-21 — DataMigrationArchitectAgent (Codex audit #2)

**BREAKING**. ADR-004 §"후속 조치" #2 직접 적용. ADR-006 패턴 (TestContractArch precedent) 그대로 차용.

### Added
- agents/DataMigrationArchitectAgent.md (NEW)
- ADR-007 (Accepted)
- templates/change-plan.md §11 데이터 마이그레이션 (§11.1-11.6)
- design.md checklist §11 audit 절 + 3 P0 차단 룰
- lane=design category enum: data-migration

### Changed
- agent count: 23 → 24
- ArchitectPLAgent deputy 4 → 5 (Phase 1.5 sanity check 1 항목 추가)
- ArchitectAgent: deputy 5인 산출물 통합 + §11 author input
- 4 deputy md cross-ref (DataMigrationArch 도형 비참여 1줄)
- CLAUDE.md: 24 core, 다이어그램, Never-skippable, 책임 매트릭스 5행, FIX decision table 1행, 4-way 대립 재명명

### Migration
- Consumer 액션: 기존 Story는 §11 N/A 사유 명시 의무. 자세한 절차는 [docs/migration-guide.md](docs/migration-guide.md) v0.13.0 → v0.14.0 절
```

- [ ] **Step 3: plugin.json** — `0.13.0` → `0.14.0`

- [ ] **Step 4: migration-guide.md** — v0.13.0 → v0.14.0 절 추가:

```
## v0.13.0 → v0.14.0 (BREAKING — DataMigrationArchitectAgent)

### What changed
- Agent count 23 → 24 (DataMigrationArchitectAgent added as 6th deputy)
- Change Plan template: §1-§10 → §1-§11 (new §11 데이터 마이그레이션)
- DesignReview checklist: 3 P0 rules added for §11 (누락 / N/A 사유 부재 / mapping 미반영)

### Consumer action
- 진행 중 Story (phase: 설계 / 설계 리뷰): Change Plan §11 추가 후 ArchitectPLAgent 검수 재실행. plugin meta / docs-only / pure UI Story는 §11.6 N/A 사유 1줄 명시 (예: "본 Story는 데이터 layer 변경 없음 — migration 분석 N/A").
- 신규 Story: 자동 적용 (story-init.yml Action이 신규 template 사용).

### Why
- Codex audit #2 (High severity) — 데이터 layer 결정 누락 위험.
- ADR-006 (TestContractArch) 패턴 그대로 차용 — shift-left 안전성 advocate.
- 자세한 사항: [ADR-007](adr/ADR-007-datamigration-architect.md).
```

- [ ] **Step 5: Verify**

```bash
jq -r '.version' .claude-plugin/plugin.json
grep -oE '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' CHANGELOG.md | head -1
ls docs/adr/ADR-007-*.md
grep "v0.13.0 → v0.14.0" docs/migration-guide.md
```

- [ ] **Step 6: Commit**

```
feat(cfp-21): ADR-007 + v0.14.0 BREAKING release + migration-guide (6/7)
```

---

## Task 7: invariant + Story doc + PR + merge

**Files:**
- Create: `docs/stories/CFP-21.md`
- Verify: invariant-check 8 step PASS

- [ ] **Step 1: Story doc 작성** — CFP-19/CFP-20 패턴 (plugin-meta-na). §1 사용자 verbatim, §2-7 spec 인용, §8/§9 N/A.

- [ ] **Step 2: invariant 8 step verify locally**

```bash
# Step 3 — agent count parity
ls agents/*.md | wc -l                    # Expected: 24
grep -oE '[0-9]+ core 에이전트' CLAUDE.md | head -1  # Expected: 24 core 에이전트

# Step 2 — version match
jq -r '.version' .claude-plugin/plugin.json && grep -oE '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' CHANGELOG.md | head -1
# Expected: 0.14.0 / [0.14.0]

# Step 6 — category enum parity (data-migration in 4 places)
grep "data-migration" templates/review-checklists/design.md agents/DesignReviewPLAgent.md agents/ClaudeReviewAgent.md agents/CodexReviewAgent.md | wc -l
# Expected: ≥4

# Step 8 — severity overrides count
grep -c "→ \*\*P0\*\*\|→ P0 강제" templates/review-checklists/design.md
# Expected: count = previous + 3 (3 new §11 P0 rules)

# Step 7 — migration guide BREAKING parity
grep "v0.13.0 → v0.14.0" docs/migration-guide.md
# Expected: at least 1 occurrence
```

- [ ] **Step 3: Push + PR open + admin merge**

- [ ] **Step 4: Final commit (Task 7 + Story doc)**

```
docs(cfp-21): Story doc + invariant verify (7/7)
```

---

## Self-Review

### 1. Spec coverage

- BREAKING agent count → Task 5 (CLAUDE.md "24 core")
- 신규 §11 → Task 3 (change-plan.md) + Task 4 (design.md checklist) + Task 5 (CLAUDE.md 매트릭스)
- 4 deputy cross-ref → Task 3
- ADR-007 → Task 6
- v0.14.0 release → Task 6
- migration-guide → Task 6
- invariant 검증 → Task 7
- ALL ✓

### 2. Placeholder scan

없음 — 모든 Task에 정확한 anchor·내용 명시.

### 3. 일관성

- enum: `data-migration` (4 곳 동일)
- 버전: 0.13.0 → 0.14.0 (3 곳 동일)
- agent count: 23 → 24 (4 곳: CLAUDE.md narrative + 다이어그램 + Never-skippable + invariant CI)
- deputy: 4 → 5 (ArchitectPL/ArchitectAgent/playbook/CLAUDE.md)

### 4. plugin-meta-na 일관성

- §8/§9 N/A 처리 (CFP-19/CFP-20 동일 패턴)
- 13-15 commit이 모두 markdown SSOT (production code 0)
- invariant-check.yml 자동 검증 → CI PASS 시 admin override merge
