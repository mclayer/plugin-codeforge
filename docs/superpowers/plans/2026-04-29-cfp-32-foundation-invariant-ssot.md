# CFP-32 (F1) — Foundation: Invariant SSOT 3종 + §10 Orchestrator 단독 owner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ζ arc 첫 foundation step. 3 invariant SSOT(comment-prefix · label · fix-event)을 `docs/inter-plugin-contracts/`에 신설하고 lint로 강제, §10 FIX Ledger 단독 owner를 DocsAgent → Orchestrator로 이관. 후속 CFP-35~40 lane plugin 추출의 contract surface 준비.

**Architecture:** 3 markdown SSOT 파일 신설 + 2 lint script 확장 + playbook §6.4 갱신 + DocsAgent.md 권한 회수 표시. Runtime 변경 없음 — schema·문서 변경만.

**Tech Stack:** YAML frontmatter, Bash + Python (lint scripts), markdown.

---

## Spec 참조

본 plan은 [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](../specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) **§5.2 CFP-32 (F1)** 만 구현. 후속 단계(CFP-33 contract harness · CFP-34 workflow tests + marketplace sync · CFP-35 review v2 retrofit · CFP-36~40 lane plugin 추출)는 별도 plan.

Codex round 2 조건 #2 직접 대응: "Phase prefix · Story section 소유권 · label명 · gate명 · FIX event 필드에 대한 machine-readable shared contract 완성 후 첫 번째 non-review 추출 시작."

## File Structure

| 파일 | 책임 | 변경 종류 |
|---|---|---|
| `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` | 11종 phase prefix SSOT | NEW |
| `docs/inter-plugin-contracts/label-registry-v1.md` | 20종 GitHub label SSOT | NEW |
| `docs/inter-plugin-contracts/fix-event-v1.md` | §10 FIX Ledger row schema | NEW |
| `scripts/check-doc-frontmatter.sh` | inter-plugin-contracts/ 신규 path 검증 + legacy allowlist | extend |
| `scripts/check-doc-section-schema.sh` | inter-plugin-contracts/ 신규 path 본문 섹션 검증 + legacy allowlist | extend |
| `docs/orchestrator-playbook.md` | §6.4 §10 갱신 owner = Orchestrator 명시 + 3 SSOT cross-ref | edit |
| `agents/DocsAgent.md` | ζ arc 단계적 해체 표시 + comment-prefix-registry SSOT 참조 + §10 권한 회수 narrative | edit |
| `.claude-plugin/plugin.json` | v0.18.0 → v0.19.0 | bump |
| `CHANGELOG.md` | v0.19.0 entry | append |

---

## Task 1: Extend `check-doc-frontmatter.sh` for inter-plugin-contracts/

새 path 검증 추가 + 기존 `review-verdict-v1.md`는 legacy allowlist (CFP-33 contract harness에서 backfill 예정).

**Files:**
- Modify: `scripts/check-doc-frontmatter.sh`

- [ ] **Step 1.1: Add path rule + legacy allowlist**

Edit `scripts/check-doc-frontmatter.sh` — add `docs/inter-plugin-contracts` to `REQUIRED` dict and add `LEGACY_INTER_PLUGIN_CONTRACTS` allowlist.

Replace the `REQUIRED = {...}` block (around lines 26-31) with:

```python
REQUIRED = {
    "docs/change-plans": {"title", "slug", "status", "author", "created", "story"},
    "docs/adr":          {"adr_number", "title", "status", "category", "date"},
    "docs/domain-knowledge": {"title", "area", "topic_slug", "status", "updated"},
    "docs/retros":       {"title", "date", "sprint_period", "cfp_keys", "authors"},
    "docs/inter-plugin-contracts": {"kind", "registry", "version", "status", "authors"},
}

# Legacy allowlist — CFP-29 review-verdict-v1.md는 본 schema 도입 이전 산출물.
# CFP-33 contract harness에서 backfill 후 allowlist 제거.
LEGACY_INTER_PLUGIN_CONTRACTS = {
    "review-verdict-v1.md",
}
```

Inside the `for md in sorted(path.rglob("*.md")):` loop, after the README/index.md skip (around line 41), add:

```python
        # Legacy inter-plugin-contracts allowlist (path-scoped)
        if prefix == "docs/inter-plugin-contracts":
            if md.name in LEGACY_INTER_PLUGIN_CONTRACTS:
                continue
```

Update header comment (around lines 1-12) to include the new path:

```bash
#!/usr/bin/env bash
# CFP-27 Phase 0b — 도입 (warning 모드)
# CFP-28 Phase 0c — strict 전환 (exit=1 on warnings)
# CFP-32 (ζ arc F1) — docs/inter-plugin-contracts/ 신규 path 추가
# 검사: 5 owner doc path 의 frontmatter 필수 필드
#
# Path / 필수 frontmatter 필드 source:
#   - docs/change-plans/**            templates/change-plan.md frontmatter
#   - docs/adr/**                     templates/adr.md
#   - docs/domain-knowledge/**        templates/domain-knowledge.md
#   - docs/retros/**                  templates/retro.md
#   - docs/inter-plugin-contracts/**  registry kind: {kind, registry, version, status, authors}
#                                     ※ review-verdict-v1.md는 CFP-29 legacy — allowlist 면제
#                                       (CFP-33 contract harness에서 backfill)
#
# Strict 모드: warning 발견 시 exit 1 → CI에서 PR 차단.
```

- [ ] **Step 1.2: Run script — expect PASS**

```bash
bash scripts/check-doc-frontmatter.sh
```

Expected output:
```
✓ CFP-28 doc-frontmatter: 4 owner path 전부 schema 충족
```

(`review-verdict-v1.md`는 allowlist로 skip; 다른 inter-plugin-contracts 파일은 아직 없음. 메시지의 "4 owner path"는 Step 1.3의 message text 갱신 시 "5 owner path"로 변경 예정 — 현 단계는 통과만 확인)

- [ ] **Step 1.3: Update success message**

In the script's success print (around line 66), update:

```python
print("✓ CFP-32 doc-frontmatter: 5 owner path 전부 schema 충족")
```

Replace previous `"✓ CFP-28 doc-frontmatter: 4 owner path 전부 schema 충족"`.

Re-run:
```bash
bash scripts/check-doc-frontmatter.sh
```

Expected: `✓ CFP-32 doc-frontmatter: 5 owner path 전부 schema 충족`

- [ ] **Step 1.4: Commit**

```bash
git add scripts/check-doc-frontmatter.sh
git commit -m "feat(cfp-32): check-doc-frontmatter.sh — inter-plugin-contracts path rule + review-verdict-v1.md allowlist"
```

---

## Task 2: Extend `check-doc-section-schema.sh` for inter-plugin-contracts/

**Files:**
- Modify: `scripts/check-doc-section-schema.sh`

- [ ] **Step 2.1: Add path rule + legacy allowlist**

Edit `scripts/check-doc-section-schema.sh` — add `docs/inter-plugin-contracts` to `REQUIRED_SECTIONS` and add `LEGACY_INTER_PLUGIN_CONTRACTS` allowlist.

Replace the `REQUIRED_SECTIONS = {...}` block (around lines 21-56) — add the new path entry before the closing brace:

```python
    "docs/inter-plugin-contracts": [
        r"^## 1\. 목적",
        r"^## 2\. Schema",
        r"^## 3\. 항목",
        r"^## 4\. 변경 규칙",
    ],
```

After the `LEGACY_CHANGE_PLAN_CFPS = {...}` block (around line 61), add:

```python
# Legacy inter-plugin-contracts allowlist — CFP-29 산출물.
# CFP-33 contract harness에서 backfill 후 allowlist 제거.
LEGACY_INTER_PLUGIN_CONTRACTS = {
    "review-verdict-v1.md",
}
```

Inside the `for md in sorted(path.rglob("*.md")):` loop, after the existing `LEGACY_CHANGE_PLAN_CFPS` check (around lines 73-75), add:

```python
        # Legacy inter-plugin-contracts allowlist (path-scoped)
        if prefix == "docs/inter-plugin-contracts":
            if md.name in LEGACY_INTER_PLUGIN_CONTRACTS:
                continue
```

Update header comment to mention the new path:

```bash
#!/usr/bin/env bash
# CFP-27 Phase 0b — 도입 (warning 모드)
# CFP-28 Phase 0c — strict 전환 (exit=1 on warnings)
# CFP-32 (ζ arc F1) — docs/inter-plugin-contracts/ 신규 path 추가
# 검사: 5 owner doc path 의 본문 필수 섹션 헤딩
#
# Section schema source:
#   - docs/change-plans/**            templates/change-plan.md  §1-§11 (legacy allowlist for pre-CFP-19)
#   - docs/adr/**                     templates/adr.md
#   - docs/domain-knowledge/**        templates/domain-knowledge.md
#   - docs/retros/**                  templates/retro.md
#   - docs/inter-plugin-contracts/**  registry kind: ## 1. 목적 / ## 2. Schema / ## 3. 항목 / ## 4. 변경 규칙
#                                     ※ review-verdict-v1.md는 CFP-29 legacy — allowlist 면제
```

Update success message (around line 96):

```python
print("✓ CFP-32 doc-section-schema: 5 owner path 전부 schema 충족")
```

- [ ] **Step 2.2: Run script — expect PASS**

```bash
bash scripts/check-doc-section-schema.sh
```

Expected: `✓ CFP-32 doc-section-schema: 5 owner path 전부 schema 충족`

- [ ] **Step 2.3: Commit**

```bash
git add scripts/check-doc-section-schema.sh
git commit -m "feat(cfp-32): check-doc-section-schema.sh — inter-plugin-contracts path rule + review-verdict-v1.md allowlist"
```

---

## Task 3: Create `comment-prefix-registry-v1.md` (TDD — deliberate break first)

먼저 의도적으로 frontmatter 필드 1개를 누락한 상태로 작성해 lint가 catch 하는 걸 검증, 그 후 수정.

**Files:**
- Create: `docs/inter-plugin-contracts/comment-prefix-registry-v1.md`

- [ ] **Step 3.1: Write file with deliberately missing `version` field**

Create `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` — frontmatter에 `version` 필드 일부러 누락:

```markdown
---
kind: registry
registry: comment-prefix
status: Active
authors:
  - Claude (CFP-32 codification — CFP-31 ζ arc parent design 기반)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-009 (Wrapper-only core + writer-distributed lane plugins, CFP-31 신설 예정)
related_files:
  - agents/DocsAgent.md (이전 narrative SSOT — 본 registry 신설 후 cross-ref로 변경)
  - docs/orchestrator-playbook.md
---

# comment-prefix-registry v1

## 1. 목적

(... 후속 step에서 작성)
```

- [ ] **Step 3.2: Run lint — expect FAIL on missing version**

```bash
bash scripts/check-doc-frontmatter.sh
```

Expected:
```
::error::CFP-28 doc-frontmatter (STRICT): 1 건
  - docs/inter-plugin-contracts/comment-prefix-registry-v1.md: 필수 필드 누락 — ['version']
```

(또는 message text는 CFP-32 갱신 후 "CFP-32 ..."로 출력될 수도 있음 — 핵심은 `version` 필드 누락이 catch 되는지)

- [ ] **Step 3.3: Add `version` field + write full file content**

Replace file with complete content:

```markdown
---
kind: registry
registry: comment-prefix
version: "1.0"
status: Active
authors:
  - Claude (CFP-32 codification — CFP-31 ζ arc parent design 기반)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-009 (Wrapper-only core + writer-distributed lane plugins, CFP-31 신설 예정)
related_files:
  - agents/DocsAgent.md (이전 narrative SSOT — 본 registry 신설 후 cross-ref로 변경)
  - docs/orchestrator-playbook.md
---

# comment-prefix-registry v1

## 1. 목적

GitHub Issue 코멘트의 phase prefix (10종 + Orchestrator Preflight 1종 = 총 11종) machine-readable SSOT. ζ arc 진행에 따라 lane plugin이 자기 lane prefix로 직접 코멘트 게시 시점에 단일 형식·시맨틱·posters 보장.

## 2. Schema

각 prefix entry:

| 필드 | 타입 | 설명 |
|---|---|---|
| prefix | string | Bracket 형식 (예: `[설계]`) |
| phase | string | 레인 식별자 (requirements / design / design-review / implementation / code-review / test / security-test / pmo / fix / completed / preflight) |
| current_owner | string | CFP-32 시점 코멘트 게시 주체 |
| target_owner_plugin | string | ζ arc 완료 후 owner plugin (또는 "core wrapper 잔류") |
| posters | array<string> | 본 prefix 사용 권한이 있는 agent 또는 Action |
| auto_mirror | bool | CI Action이 자동 mirror 하는가 (true: `[FIX #N]`만) |

## 3. 항목

```yaml
prefixes:
  - prefix: "[요구사항]"
    phase: requirements
    current_owner: DocsAgent
    target_owner_plugin: codeforge-requirements (CFP-37 후)
    posters:
      - RequirementsPLAgent
      - DomainAgent
      - RequirementsAnalystAgent
      - ResearcherAgent
    auto_mirror: false

  - prefix: "[설계]"
    phase: design
    current_owner: DocsAgent
    target_owner_plugin: codeforge-design (CFP-40 후)
    posters:
      - ArchitectPLAgent
      - ArchitectAgent
      - CodebaseMapperAgent
      - RefactorAgent
      - SecurityArchitectAgent
      - TestContractArchitectAgent
      - DataMigrationArchitectAgent
    auto_mirror: false

  - prefix: "[설계-리뷰]"
    phase: design-review
    current_owner: DocsAgent
    target_owner_plugin: codeforge-review (CFP-35 v2 retrofit 후)
    posters:
      - DesignReviewPLAgent
      - ClaudeReviewAgent
      - CodexReviewAgent
    auto_mirror: false

  - prefix: "[구현]"
    phase: implementation
    current_owner: DocsAgent
    target_owner_plugin: codeforge-develop (CFP-39 후)
    posters:
      - DeveloperPLAgent
      - DeveloperAgent
      - DataEngineerAgent
      - InfraEngineerAgent
      - QADeveloperAgent
      - "<role:dev overlay/preset 에이전트>"
    auto_mirror: false

  - prefix: "[구현-리뷰]"
    phase: code-review
    current_owner: DocsAgent
    target_owner_plugin: codeforge-review (CFP-35 v2 retrofit 후)
    posters:
      - CodeReviewPLAgent
      - ClaudeReviewAgent
      - CodexReviewAgent
    auto_mirror: false

  - prefix: "[구현-테스트]"
    phase: test
    current_owner: DocsAgent
    target_owner_plugin: codeforge-test (CFP-38 후)
    posters:
      - TestAgent
    auto_mirror: false

  - prefix: "[보안-테스트]"
    phase: security-test
    current_owner: DocsAgent
    target_owner_plugin: codeforge-review (CFP-35 v2 retrofit 후)
    posters:
      - SecurityTestPLAgent
      - ClaudeReviewAgent
      - CodexReviewAgent
    auto_mirror: false

  - prefix: "[PMO]"
    phase: pmo
    current_owner: DocsAgent
    target_owner_plugin: codeforge-pmo (CFP-36 후)
    posters:
      - PMOAgent
    auto_mirror: false

  - prefix: "[FIX #N]"
    phase: fix
    current_owner: "fix-ledger-sync.yml CI Action (자동 mirror)"
    target_owner_plugin: "(CI Action 유지 — plugin 무관)"
    posters:
      - "fix-ledger-sync.yml (자동)"
      - "DocsAgent (fallback only — Action 실패 시)"
    auto_mirror: true

  - prefix: "[완료]"
    phase: completed
    current_owner: DocsAgent
    target_owner_plugin: "(CI 위임 가능 — CFP-34 검증 후 결정)"
    posters:
      - DocsAgent
    auto_mirror: false

  - prefix: "[<진입 레인>] Orchestrator: Preflight {PASS|FAIL}"
    phase: preflight
    current_owner: Orchestrator
    target_owner_plugin: "(core wrapper 잔류 — Orchestrator 직접 게시)"
    posters:
      - Orchestrator
    auto_mirror: false
```

## 4. 변경 규칙

- **Append-only for v1.x**: 새 prefix 추가는 minor bump (v1.0 → v1.1). 기존 prefix 삭제 또는 이름 변경은 v2.0 BREAKING (ADR-008 versioning 룰)
- **Owner transition**: ζ arc 진행에 따라 `current_owner` (DocsAgent) → `target_owner_plugin`으로 이전. 이전 시점은 해당 lane plugin 추출 CFP에 명시 (예: `[설계]` prefix는 CFP-40에서 codeforge-design으로 이전)
- **Posters 갱신**: 기존 prefix에 새 agent 추가는 minor (v1.1). agent 이름 변경(예: rename)도 minor — alias 매핑으로 호환성 유지
- **`[FIX #N]` 자동 mirror**: `fix-ledger-sync.yml` CI Action이 §10 commit 감지 시 자동. agent는 직접 게시 금지 (fallback 시 DocsAgent 사용)
- **Format 위반 enforcement**: lane plugin이 본 registry 외 prefix 또는 형식으로 게시 시 향후 CFP-33 contract harness가 lint catch
```

- [ ] **Step 3.4: Run both lint scripts — expect PASS**

```bash
bash scripts/check-doc-frontmatter.sh
bash scripts/check-doc-section-schema.sh
```

Expected for both:
```
✓ CFP-32 doc-frontmatter: 5 owner path 전부 schema 충족
✓ CFP-32 doc-section-schema: 5 owner path 전부 schema 충족
```

- [ ] **Step 3.5: Commit**

```bash
git add docs/inter-plugin-contracts/comment-prefix-registry-v1.md
git commit -m "feat(cfp-32): comment-prefix-registry v1 — 11 phase prefix machine-readable SSOT"
```

---

## Task 4: Create `label-registry-v1.md`

20종 GitHub label SSOT (`bootstrap-labels.sh` 현재 hardcoded source — 향후 SSOT 역전 예정).

**Files:**
- Create: `docs/inter-plugin-contracts/label-registry-v1.md`

- [ ] **Step 4.1: Write full file**

Create `docs/inter-plugin-contracts/label-registry-v1.md`:

````markdown
---
kind: registry
registry: label
version: "1.0"
status: Active
authors:
  - Claude (CFP-32 codification — bootstrap-labels.sh 추출 + ζ arc owner 매핑)
related_adrs:
  - ADR-008
  - ADR-009 (CFP-31)
related_files:
  - scripts/bootstrap-labels.sh (현재 hardcoded source — CFP-33 contract harness에서 SSOT 역전 후 본 registry → script 자동 생성)
  - .github/workflows/phase-label-invariant.yml
  - .github/workflows/phase-gate-mergeable.yml
  - .github/workflows/fix-ledger-sync.yml
  - .github/workflows/subissue-from-impl-manifest.yml
  - .github/workflows/story-init.yml
---

# label-registry v1

## 1. 목적

`bootstrap-labels.sh`가 생성하는 GitHub label 20종 machine-readable SSOT. ζ arc 진행 후 각 lane plugin이 자기 phase·gate·fix label을 attach·detach 시 통일된 이름·색상·의미 보장. CI Actions(`phase-label-invariant.yml` 등)도 본 registry를 참조해 invariant enforce.

## 2. Schema

각 label entry:

| 필드 | 타입 | 설명 |
|---|---|---|
| name | string | label 이름 (예: `phase:설계`) |
| category | enum | type / phase / gate / fix / hotfix / audit |
| color | string | 6자리 hex (gh label spec) |
| description | string | label 설명 (gh label create --description 인자) |
| single_active | bool | 같은 category에서 1개만 active 가능 (phase만 true) |
| attach_owner_plugin | string | CFP-32 시점 + ζ arc 완료 후 부착 권한 plugin / Action |

## 3. 항목

```yaml
labels:
  # type:* (4종)
  - name: type:epic
    category: type
    color: "5319e7"
    description: "Epic (사용자 요구사항 1건 = Milestone + Issue)"
    single_active: false
    attach_owner_plugin: "codeforge-pmo (CFP-36 후) / DocsAgent (CFP-32 시점)"

  - name: type:story
    category: type
    color: "0e8a16"
    description: "Story (PR 1쌍 = Phase 1 + Phase 2)"
    single_active: false
    attach_owner_plugin: "story-init.yml CI Action (자동)"

  - name: type:bug
    category: type
    color: "d73a4a"
    description: "Bug"
    single_active: false
    attach_owner_plugin: "DocsAgent (CFP-32 시점) / 사용자 직접"

  - name: impl-manifest
    category: type
    color: "fbca04"
    description: "Sub-issue (Impl Manifest 파일 단위)"
    single_active: false
    attach_owner_plugin: "subissue-from-impl-manifest.yml CI Action (자동)"

  # phase:* (7종, single-active enforced by phase-label-invariant.yml)
  - name: phase:요구사항
    category: phase
    color: "1d76db"
    description: "Phase: 요구사항"
    single_active: true
    attach_owner_plugin: "codeforge-requirements (CFP-37 후) / DocsAgent (CFP-32 시점) / story-init.yml (초기 부착)"

  - name: phase:설계
    category: phase
    color: "1d76db"
    description: "Phase: 설계"
    single_active: true
    attach_owner_plugin: "codeforge-design (CFP-40 후) / DocsAgent (CFP-32 시점)"

  - name: phase:설계-리뷰
    category: phase
    color: "1d76db"
    description: "Phase: 설계-리뷰"
    single_active: true
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점)"

  - name: phase:구현
    category: phase
    color: "1d76db"
    description: "Phase: 구현"
    single_active: true
    attach_owner_plugin: "codeforge-develop (CFP-39 후) / DocsAgent (CFP-32 시점)"

  - name: phase:구현-리뷰
    category: phase
    color: "1d76db"
    description: "Phase: 구현-리뷰"
    single_active: true
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점)"

  - name: phase:구현-테스트
    category: phase
    color: "1d76db"
    description: "Phase: 구현-테스트"
    single_active: true
    attach_owner_plugin: "codeforge-test (CFP-38 후) / DocsAgent (CFP-32 시점)"

  - name: phase:보안-테스트
    category: phase
    color: "1d76db"
    description: "Phase: 보안-테스트"
    single_active: true
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점)"

  # gate:* (2종)
  - name: gate:design-review-pass
    category: gate
    color: "0e8a16"
    description: "Design review PASS"
    single_active: false
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점)"

  - name: gate:security-test-pass
    category: gate
    color: "0e8a16"
    description: "Security test PASS"
    single_active: false
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점)"

  # fix:* (4종, 누적 가능)
  - name: fix:설계-리뷰-retry
    category: fix
    color: "e99695"
    description: "FIX retry: 설계-리뷰"
    single_active: false
    attach_owner_plugin: "fix-ledger-sync.yml CI Action (자동)"

  - name: fix:구현-리뷰-retry
    category: fix
    color: "e99695"
    description: "FIX retry: 구현-리뷰"
    single_active: false
    attach_owner_plugin: "fix-ledger-sync.yml CI Action (자동)"

  - name: fix:구현-테스트-retry
    category: fix
    color: "e99695"
    description: "FIX retry: 구현-테스트"
    single_active: false
    attach_owner_plugin: "fix-ledger-sync.yml CI Action (자동)"

  - name: fix:보안-테스트-retry
    category: fix
    color: "e99695"
    description: "FIX retry: 보안-테스트"
    single_active: false
    attach_owner_plugin: "fix-ledger-sync.yml CI Action (자동)"

  # hotfix:* (2종) + audit (1종)
  - name: hotfix:minimal
    category: hotfix
    color: "ff9999"
    description: "Hotfix minimal"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix 경로)"

  - name: hotfix:critical
    category: hotfix
    color: "ff0000"
    description: "Hotfix critical"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix 경로)"

  - name: audit:post-hotfix
    category: audit
    color: "fef2c0"
    description: "Post-hotfix audit Story"
    single_active: false
    attach_owner_plugin: "Orchestrator (hotfix merge 다음 세션 자동 부착)"
```

## 4. 변경 규칙

- **Append-only for v1.x**: 새 label 추가는 minor (v1.1). 기존 label 삭제 또는 이름 변경은 v2.0 BREAKING (ADR-008)
- **`single_active: true` invariant**: phase:* 카테고리만 single-active. CI Action `phase-label-invariant.yml`이 enforce — 두 phase:* 동시 부착 PR reject
- **Color drift 방지**: 본 registry color 값은 `bootstrap-labels.sh`가 idempotent edit (`gh label edit --color`)로 강제 동기화. consumer가 manual로 색상 변경 시 다음 bootstrap 실행에 복원
- **Owner transition**: ζ arc 진행에 따라 `attach_owner_plugin` 좌측(현재 owner) → 우측(target plugin)으로 이전. fix:* / impl-manifest / type:story / audit:* 는 CI Action 또는 Orchestrator 유지 (lane plugin 무관)
- **`bootstrap-labels.sh` SSOT 역전 (CFP-33 contract harness 후)**: 현재 script가 hardcoded source. CFP-33에서 본 registry → script 자동 생성으로 전환
````

- [ ] **Step 4.2: Run both lint scripts — expect PASS**

```bash
bash scripts/check-doc-frontmatter.sh
bash scripts/check-doc-section-schema.sh
```

Expected: both pass.

- [ ] **Step 4.3: Commit**

```bash
git add docs/inter-plugin-contracts/label-registry-v1.md
git commit -m "feat(cfp-32): label-registry v1 — 20 GitHub label machine-readable SSOT"
```

---

## Task 5: Create `fix-event-v1.md`

§10 FIX Ledger row schema + Orchestrator append rules.

**Files:**
- Create: `docs/inter-plugin-contracts/fix-event-v1.md`

- [ ] **Step 5.1: Write full file**

Create `docs/inter-plugin-contracts/fix-event-v1.md`:

````markdown
---
kind: registry
registry: fix-event
version: "1.0"
status: Active
authors:
  - Claude (CFP-32 codification — playbook §6.4 추출 + Orchestrator monopoly enforcement)
related_adrs:
  - ADR-008
  - ADR-009 (CFP-31 — §10 Orchestrator 단독 owner 결정)
related_files:
  - docs/orchestrator-playbook.md (§6.4 narrative SSOT — 본 registry와 cross-ref)
  - .github/workflows/fix-ledger-sync.yml (§10 행 commit 감지 → label/comment mirror)
  - templates/story-page-structure.md (Story §10 표 schema)
---

# fix-event v1

## 1. 목적

`docs/stories/<KEY>.md` §10 "FIX Ledger" 표의 row schema machine-readable SSOT. ζ arc CFP-32부터 §10 갱신 권한이 **Orchestrator 단독**으로 이관 — lane plugin은 FIX event를 보고할 뿐 §10에 직접 append 금지. 본 registry는 row 필드 + append 규칙 + RESET 시맨틱스를 명시.

## 2. Schema

각 §10 row entry:

| 필드 | 타입 | 설명 |
|---|---|---|
| Iter | int (1-indexed) | iteration 누적 카운터. 같은 Story 안에서 단조 증가 (RESET 무관) |
| 시각 | ISO8601 string | UTC, `2026-04-29T12:34:56Z` 형식 |
| 레인 | enum | 요구사항 / 설계 / 설계-리뷰 / 구현 / 구현-리뷰 / 구현-테스트 / 보안-테스트 |
| 트리거 | string | 실패 원문 요약 (예: "DesignReviewPL P0 × 2", "성능 mean +15%", "SecurityTestPL P0 × 1 (SQL injection)") |
| 원인 판정 | enum | 설계 / 구현 (ArchitectPL 최종 판정. CLAUDE.md "원인 판정 decision table" SSOT) |
| 재실행 범위 | string | 어떤 산출물·step부터 다시 진행하는지 (예: "Change Plan §3 재작성", "DeveloperAgent 재스폰") |
| RESET? | string | "—" (RESET 없음) 또는 "RESET <레인>" (해당 lane 카운터 리셋) |

§10 행 markdown 형식 예시:

```markdown
| Iter | 시각 | 레인 | 트리거 | 원인 판정 | 재실행 범위 | RESET? |
|------|------|------|--------|-----------|-------------|--------|
| 1    | 2026-04-29T10:15:00Z | 설계-리뷰   | DesignReviewPL P0 × 2 | 설계 | Change Plan §3 재작성 | — |
| 2    | 2026-04-29T14:22:00Z | 구현-테스트 | 성능 mean +15% | 설계 | Change Plan §3 재작성 | RESET 구현-리뷰 |
| 3    | 2026-04-30T09:00:00Z | 보안-테스트 | SecurityTestPL P0 × 1 (SQL injection) | 구현 | DeveloperAgent 재스폰 | — |
```

## 3. 항목

```yaml
fix_event_schema:
  Iter:
    type: int
    constraints:
      - "monotonically increasing within a single Story file"
      - "1-indexed"
      - "RESET 마커는 카운터 자체에 영향 없음 — RESET 행 자체도 Iter+1"

  "시각":
    type: ISO8601
    constraints:
      - "UTC (timezone Z 또는 +00:00)"
      - "millisecond precision optional"

  "레인":
    type: enum
    values:
      - 요구사항    # 발생 드묾 — clarification 재스폰은 §10 미사용 (§9.0 별도)
      - 설계
      - 설계-리뷰
      - 구현
      - 구현-리뷰
      - 구현-테스트
      - 보안-테스트

  "트리거":
    type: string
    constraints:
      - "review verdict findings 요약 또는 test failure 원문 요약"
      - "free-form, but ≤120자 권장"

  "원인 판정":
    type: enum
    values:
      - 설계      # → Change Plan 갱신, 설계 리뷰부터 재실행
      - 구현      # → Change Plan 유지, 구현 commit append
    decision_rule_ssot: CLAUDE.md "원인 판정 decision table" 섹션
    decided_by: ArchitectPLAgent (chief judge — DeveloperPL 1차 진단과 병렬)

  "재실행 범위":
    type: string
    constraints:
      - "구체 산출물·step 명시 (Change Plan §N 재작성 / agent 재스폰 / commit append 등)"

  "RESET?":
    type: string
    values:
      - "—"                        # 평소
      - "RESET 구현-리뷰"           # 구현-테스트/보안-테스트 FAIL 시 구현 복귀 → 구현-리뷰 카운터 리셋
    rule: "구현-테스트 또는 보안-테스트 FAIL → 구현 복귀 시 마지막 행에 RESET 기입. 설계-리뷰·구현-리뷰 내부 루프는 RESET 없음"

append_rules:
  writer:
    - "Orchestrator 단독 (CFP-32 ζ arc F1부터)"
    - "DocsAgent §10 write 권한 회수 — fallback 없음"
  ordering:
    - "append-only — 행 삭제·수정·재정렬 금지"
    - "stale-read 체크: Edit 직전 git pull --rebase 또는 file mtime 비교"
  trigger_sources:
    - "lane plugin이 FIX event 보고 (verdict.status == FIX 또는 test FAIL)"
    - "Orchestrator가 보고 수령 → 원인 판정 (ArchitectPL 최종) → §10 행 작성"
  fix-ledger-sync.yml_action:
    - "§10 commit 감지 → Story Issue에 [FIX #N] 코멘트 mirror + fix:<레인>-retry 라벨 자동 부착"
    - "단방향 (§10 → label/comment). 라벨 변경에서 §10 자동 생성 안 함 (Codex 권고)"

counter_semantics:
  current_cycle:
    rule: "마지막 RESET <레인> 행 이후 같은 lane row count"
    pseudo_code: |
      rows = parse_section10(story_file)
      for lane in [설계-리뷰, 구현-리뷰, 구현-테스트, 보안-테스트]:
          last_reset_idx = max(i for i,r in enumerate(rows) if r.reset == lane, default=-1)
          current_count = sum(1 for r in rows[last_reset_idx+1:] if r.lane == lane)

  max_fix_per_cycle:
    설계-리뷰: 3       # 초과 시 ESCALATE
    구현-리뷰: 3       # 초과 시 ESCALATE
    구현-테스트: ∞      # 무제한 (테스트 family)
    보안-테스트: ∞      # 무제한
```

## 4. 변경 규칙

- **Append-only for v1.x**: 새 필드 추가는 minor (v1.0 → v1.1). 기존 필드 삭제 또는 enum 값 제거는 v2.0 BREAKING (ADR-008)
- **§10 마크다운 표 형식 변경 금지 (v1.x)**: `fix-ledger-sync.yml` Action regex가 현 표 형식에 의존 — column 순서·헤더 텍스트 변경 시 BREAKING. CFP-34에서 workflow yaml regex test 추가 후에야 변경 안전
- **Writer monopoly v1**: Orchestrator 단독. lane plugin이 §10 직접 Edit 시 CI Action `story-section-write-guard.yml` (CFP-34 deliverable)이 catch
- **RESET 시맨틱스 변경**: lane scope 또는 시점 변경은 minor (v1.1) — `current_cycle` 알고리즘 영향. ESCALATE 임계값 변경은 minor (v1.1)
- **§10 schema 검증**: CFP-33 contract harness가 본 registry → Story file §10 매칭 lint 추가
````

- [ ] **Step 5.2: Run both lint scripts — expect PASS**

```bash
bash scripts/check-doc-frontmatter.sh
bash scripts/check-doc-section-schema.sh
```

Expected: both pass.

- [ ] **Step 5.3: Commit**

```bash
git add docs/inter-plugin-contracts/fix-event-v1.md
git commit -m "feat(cfp-32): fix-event v1 — §10 FIX Ledger row schema + Orchestrator monopoly"
```

---

## Task 6: Update `orchestrator-playbook.md` §6.4 — Orchestrator §10 단독 owner

§6.4 "§10 관리 세부" 섹션에서 DocsAgent → Orchestrator 이관 명시 + 3 SSOT cross-ref 추가.

**Files:**
- Modify: `docs/orchestrator-playbook.md`

- [ ] **Step 6.1: Update §6.4 narrative**

Find lines 505-510 (currently):

```markdown
### 6.4 §10 관리 세부

- DocsAgent가 단독 갱신 (append-only, 행 삭제·수정 금지)
- Orchestrator는 `Read(docs/stories/<KEY>.md)`로 §10 read-only 조회 후 count 산출
- §10 조회 실패(파일 부재 등) → ArchitectPLAgent 판정 정지 → 사용자 판단 요청
- GitHub 라벨은 fix-ledger-sync.yml Action이 §10 commit 감지 시 자동 부착 — 대시보드 search syntax 필터용
```

Replace with:

```markdown
### 6.4 §10 관리 세부

- **Orchestrator가 단독 갱신** (CFP-32 ζ arc F1부터 — DocsAgent에서 이관). append-only, 행 삭제·수정 금지
- Schema SSOT: [`docs/inter-plugin-contracts/fix-event-v1.md`](../docs/inter-plugin-contracts/fix-event-v1.md) — row 필드 + append 규칙 + RESET 시맨틱스
- Stale-read 방지: Orchestrator가 Edit 직전 `git pull --rebase` 또는 file mtime 비교 후 append. 충돌 시 fail-fast + 사용자 ESCALATE (자동 재시도 금지 — append-only ledger 손상 위험)
- Lane plugin은 FIX event를 Orchestrator에 verdict로 보고 (status=FIX 또는 test FAIL). lane plugin이 §10 직접 Edit 금지 — CFP-34 deliverable `story-section-write-guard.yml`이 enforce
- §10 조회 실패(파일 부재 등) → ArchitectPLAgent 판정 정지 → 사용자 판단 요청
- GitHub 라벨은 `fix-ledger-sync.yml` Action이 §10 commit 감지 시 자동 부착 — 단방향 mirror (§10 → label/comment). 대시보드 search syntax 필터용
```

- [ ] **Step 6.2: Update §6.6 parallel diagnosis flow note**

Find lines 524-526 (DeveloperPL ledger-append):

```markdown
2. 한 메시지에 두 에이전트 동시 spawn:
   - DeveloperPL: 1차 원인 진단 (구현 / 설계) — 결과를 Story file §10 row append로 ledger-append (mode: blocking)
   - ArchitectPL: 최종 판정 — review findings + Change Plan + ADR 정합성 평가 (DeveloperPL 결과 미수신, 독립 판단)
```

Replace with:

```markdown
2. 한 메시지에 두 에이전트 동시 spawn:
   - DeveloperPL: 1차 원인 진단 (구현 / 설계) — 결과 typed return (CFP-32부터 §10 직접 write 안 함, Orchestrator가 받아서 §10 append)
   - ArchitectPL: 최종 판정 — review findings + Change Plan + ADR 정합성 평가 (DeveloperPL 결과 미수신, 독립 판단)
```

- [ ] **Step 6.3: Update other DocsAgent-§10 references**

Search for `Edit(docs/stories/<KEY>.md)` near "ledger-append" mentions.

Around line 866:
```markdown
   - `ledger-append` → `Edit(docs/stories/<KEY>.md)` §10 append (fix-ledger-sync.yml가 자동 mirror+label)
```

Replace with:

```markdown
   - `ledger-append` → Orchestrator 직접 `Edit(docs/stories/<KEY>.md)` §10 append (CFP-32부터 — fix-ledger-sync.yml가 자동 mirror+label)
```

- [ ] **Step 6.4: Run check-doc-links.sh**

```bash
python3 -c "
import re
from pathlib import Path
LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
md = Path('docs/orchestrator-playbook.md').read_text(encoding='utf-8')
errors = []
for lineno, line in enumerate(md.splitlines(), start=1):
    for match in LINK_RE.finditer(line):
        target = match.group(1).strip()
        if target.startswith(('http://', 'https://', '#', 'mailto:')):
            continue
        if '<' in target or '\$' in target or target.startswith('{'):
            continue
        file_part = target.split('#', 1)[0]
        if not file_part:
            continue
        resolved = (Path('docs') / file_part).resolve()
        if not resolved.exists():
            errors.append(f'orchestrator-playbook.md:{lineno}: broken link -> {target}')
print('\n'.join(errors) if errors else '✓ playbook links OK')
"
```

Expected: `✓ playbook links OK`

- [ ] **Step 6.5: Commit**

```bash
git add docs/orchestrator-playbook.md
git commit -m "feat(cfp-32): playbook §6.4 — Orchestrator 단독 §10 owner + fix-event-v1 cross-ref"
```

---

## Task 7: Update `agents/DocsAgent.md` — ζ arc 단계적 해체 표시

DocsAgent에 §10 권한 회수 + 3 SSOT cross-ref 명시.

**Files:**
- Modify: `agents/DocsAgent.md`

- [ ] **Step 7.1: Add ζ arc 단계적 해체 header note**

Find line 61 (current opening narrative):

```markdown
**GitHub lifecycle (Issue/PR/comment·sub-issue·label) 단독 writer + Story file 직렬화 owner + 문서화 표준 SSOT**. CFP-26 Phase 0a부터 single-author docs(`docs/{change-plans,adr,domain-knowledge,retros}/**`)는 ArchitectAgent · DomainAgent · PMOAgent가 owner direct write — 그 외 docs/** 일반 문서·Story file·GitHub lifecycle은 본 에이전트 단독 유지. 다른 에이전트 중 owner agent가 아닌 경우는 GitHub Issue/PR/Story §·comment 작업을 Orchestrator 경유 본 에이전트에 의뢰한다.
```

Insert before this paragraph (as new opening note):

```markdown
> **ζ arc 단계적 해체 진행 중 (CFP-31 parent design ~ CFP-40)**: 본 agent는 [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](../docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5에 따라 단계적 권한 회수 후 CFP-40 시점에 file 최종 삭제 예정. **CFP-32 시점 회수 사항**: §10 FIX Ledger 갱신 권한 → Orchestrator 단독 (schema SSOT [`docs/inter-plugin-contracts/fix-event-v1.md`](../docs/inter-plugin-contracts/fix-event-v1.md)). 11 phase prefix narrative SSOT → [`docs/inter-plugin-contracts/comment-prefix-registry-v1.md`](../docs/inter-plugin-contracts/comment-prefix-registry-v1.md). 20 GitHub label narrative SSOT → [`docs/inter-plugin-contracts/label-registry-v1.md`](../docs/inter-plugin-contracts/label-registry-v1.md).

```

- [ ] **Step 7.2: Update §1 phase prefix list to reference registry**

Find lines 108-118 (the 10-prefix list):

```markdown
**Phase prefix 10종 + Orchestrator Preflight 1종 = 총 11종** (현재 레인·이벤트에 맞는 것 선택):
- `[요구사항]` — RequirementsPLAgent·DomainAgent·RequirementsAnalyst·Researcher
- `[설계]` — ArchitectPLAgent·ArchitectAgent (chief author)·CodebaseMapperAgent·RefactorAgent·SecurityArchitectAgent·TestContractArchitectAgent
- `[설계-리뷰]` — DesignReviewPLAgent·ClaudeReviewAgent·CodexReviewAgent (워커는 lane=design packet 수령)
- `[구현]` — DeveloperPLAgent·`role: dev` 에이전트들 (DeveloperAgent·DataEng·InfraEng·preset·overlay)·QADev
- `[구현-리뷰]` — CodeReviewPLAgent·ClaudeReviewAgent·CodexReviewAgent (워커는 lane=code packet 수령)
- `[구현-테스트]` — TestAgent
- `[보안-테스트]` — SecurityTestPLAgent·ClaudeReviewAgent·CodexReviewAgent (워커는 lane=security packet 수령)
- `[PMO]` — PMOAgent 감사·회고·ADR 후보 발의
- `[FIX #N]` — FIX 루프 iteration 기록 (N = 누적 횟수). 단, fix-ledger-sync.yml Action이 §10 commit 시 자동 mirror 하므로 DocsAgent가 직접 기록할 일은 드물다 (fallback만)
- `[완료]` — Phase 2 PR merged · Issue auto-close 시 종료 보고
```

Replace with:

```markdown
**Phase prefix 10종 + Orchestrator Preflight 1종 = 총 11종** — **machine-readable SSOT**: [`docs/inter-plugin-contracts/comment-prefix-registry-v1.md`](../docs/inter-plugin-contracts/comment-prefix-registry-v1.md) (CFP-32부터). 본 narrative는 요약만:

- `[요구사항]` · `[설계]` · `[설계-리뷰]` · `[구현]` · `[구현-리뷰]` · `[구현-테스트]` · `[보안-테스트]` · `[PMO]` · `[FIX #N]` · `[완료]` — 각 prefix의 posters / current owner / target plugin / auto_mirror 여부는 registry yaml `## 3. 항목` 참조
- `[FIX #N]`은 `fix-ledger-sync.yml` Action이 자동 mirror — DocsAgent 직접 기록은 fallback만
```

- [ ] **Step 7.3: Add §10 FIX Ledger ownership transfer note**

Find lines 65-74 (소유 영역 list — currently shows "9. GitHub Label"). Add a new closing item:

After the "9. GitHub Label — phase·gate·fix·type·component·adr·hotfix·audit·impl-manifest 부착·제거" line, add:

```markdown

> **§10 FIX Ledger 갱신 — CFP-32부터 Orchestrator로 이관**: 이전에는 본 agent가 단독 갱신 (`docs/stories/<KEY>.md` §10 row append). ζ arc F1 (CFP-32) 시점부터 Orchestrator 직접 Edit. 본 agent는 §10 read-only. 자세한 schema·append 규칙은 [`docs/inter-plugin-contracts/fix-event-v1.md`](../docs/inter-plugin-contracts/fix-event-v1.md) 참조.
```

- [ ] **Step 7.4: Run check-agent-frontmatter.sh + check-doc-links.sh**

```bash
# agent frontmatter still valid (no permission changes — narrative only)
python3 -c "
import yaml
from pathlib import Path
md = Path('agents/DocsAgent.md')
raw = md.read_text(encoding='utf-8')
assert raw.startswith('---\n'), 'no frontmatter'
fm_text = raw.split('\n---\n', 1)[0][4:]
fm = yaml.safe_load(fm_text)
assert 'name' in fm and 'description' in fm
print('✓ DocsAgent.md frontmatter still valid')
"

# Check the new links resolve
python3 -c "
import re
from pathlib import Path
md = Path('agents/DocsAgent.md').read_text(encoding='utf-8')
LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
for line_no, line in enumerate(md.splitlines(), 1):
    for m in LINK_RE.finditer(line):
        target = m.group(1).strip()
        if target.startswith(('http://', 'https://', '#', 'mailto:')):
            continue
        file_part = target.split('#', 1)[0]
        if not file_part:
            continue
        resolved = (Path('agents') / file_part).resolve()
        if not resolved.exists():
            print(f'BROKEN: {line_no}: {target} -> {resolved}')
print('✓ DocsAgent.md links checked')
"
```

Expected: both pass / no broken links.

- [ ] **Step 7.5: Commit**

```bash
git add agents/DocsAgent.md
git commit -m "feat(cfp-32): DocsAgent.md — ζ arc 단계적 해체 표시 + §10 권한 회수 + 3 SSOT cross-ref"
```

---

## Task 8: Bump `.claude-plugin/plugin.json` v0.18.0 → v0.19.0 + CHANGELOG entry

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `CHANGELOG.md`

- [ ] **Step 8.1: Bump plugin.json version**

Edit `.claude-plugin/plugin.json` — change `version: "0.18.0"` to `version: "0.19.0"`. Description은 그대로 유지 (CFP-31 spec 합의 — wrapper-only는 ζ arc 완료 후 description 변경).

```json
{
  "name": "codeforge",
  "version": "0.19.0",
  "description": "Claude Code 범용 SW 개발 오케스트레이션 플러그인 — 19 core 에이전트 + role:dev 동적 roster · 7 레인 구조로 요구사항부터 보안 테스트까지 자율 실행. Review subsystem은 별도 plugin codeforge-review로 추출 (CFP-29 Phase 1, BREAKING) · Inter-plugin Contract review_verdict v1 (ADR-008) · Plugin self-application dogfooding · Overlay + preset · project.yaml structured 상수 (SessionStart hook schema 검증 + Project Config Packet 자동 주입) · GitHub Actions CI.",
  "author": {
    "name": "Josh"
  },
  "keywords": [
    "orchestration",
    "agents",
    "software-development",
    "tdd",
    "code-review",
    "security-testing",
    "overlay",
    "preset",
    "structured-config"
  ]
}
```

- [ ] **Step 8.2: Append CHANGELOG entry**

Edit `CHANGELOG.md` — insert new entry above existing v0.18.0 entry (i.e., right after the header text lines):

```markdown
## [0.19.0] - 2026-04-29

### CFP-32 (ζ arc F1) — Foundation: Invariant SSOT 3종 + §10 Orchestrator 단독 owner (Non-BREAKING)

ζ arc 첫 foundation step. 3 invariant SSOT(`comment-prefix-registry-v1` · `label-registry-v1` · `fix-event-v1`)을 `docs/inter-plugin-contracts/`에 신설하고 lint로 강제. §10 FIX Ledger 갱신 권한을 DocsAgent → Orchestrator 단독으로 이관. 후속 CFP-35~40 lane plugin 추출의 contract surface 준비 완료.

설계 SSOT: [`docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md`](docs/superpowers/specs/2026-04-29-cfp-31-wrapper-only-decomposition-design.md) §5.2. Codex round 2 조건 #2(machine-readable shared contract 사전 구축) 직접 대응.

### Added
- `docs/inter-plugin-contracts/comment-prefix-registry-v1.md` — 11종 phase prefix machine-readable SSOT (kind: registry)
- `docs/inter-plugin-contracts/label-registry-v1.md` — 20종 GitHub label machine-readable SSOT
- `docs/inter-plugin-contracts/fix-event-v1.md` — §10 FIX Ledger row schema + append 규칙 + RESET 시맨틱스
- `docs/superpowers/plans/2026-04-29-cfp-32-foundation-invariant-ssot.md` — 본 implementation plan

### Changed
- `scripts/check-doc-frontmatter.sh` — `docs/inter-plugin-contracts/**` path 규칙 추가 (필수: kind/registry/version/status/authors). `review-verdict-v1.md` legacy allowlist
- `scripts/check-doc-section-schema.sh` — `docs/inter-plugin-contracts/**` 본문 섹션 규칙 추가 (## 1-4. 목적/Schema/항목/변경 규칙). 같은 legacy allowlist
- `docs/orchestrator-playbook.md` §6.4 — DocsAgent → Orchestrator §10 단독 갱신자 이관 명시 + 3 SSOT cross-ref
- `agents/DocsAgent.md` — ζ arc 단계적 해체 진행 표시 + §10 권한 회수 + 11 phase prefix narrative → registry SSOT cross-ref
- `.claude-plugin/plugin.json` version 0.18.0 → 0.19.0

### Why
ζ arc parent spec(CFP-31)이 정의한 9 CFP 로드맵의 첫 단계. Codex round 2 명시: lane plugin 추출 시작 전 phase prefix · label · FIX event 필드 contract를 machine-readable로 fix해야 split-brain 위험 회피. 본 CFP는 "추출"이 아닌 "추출 전 invariant 동결" — 추출 자체는 CFP-35부터.

거부된 대안: F1+F2+F3 압축 1 CFP (Codex 명시 거부 — 검증 신호 분리 불가), F1을 review-verdict-v1.md 백필 포함 확장 (scope creep — CFP-33 contract harness 영역).

### Migration
**Non-BREAKING** — 본 CFP는 schema 도입 + 권한 narrative 갱신만. 기존 Story file·GitHub Issue·CI Action 동작 변화 없음.

- consumer overlay 영향 없음
- agent permission frontmatter 변화 없음 (DocsAgent narrative만 갱신)
- §10 갱신 주체가 Orchestrator로 명시되었으나 실제 mechanics는 동일 (Orchestrator → DocsAgent 의뢰 → §10 Edit이 → Orchestrator 직접 Edit으로 변경 — Orchestrator는 top-level 세션이라 path-scoped 권한 무관)

### Validation
- `scripts/check-doc-frontmatter.sh` (strict) — 5 owner path 통과
- `scripts/check-doc-section-schema.sh` (strict) — 5 owner path 통과
- `scripts/check-doc-links.sh` — 신규 cross-ref 무결
- `scripts/check-agent-frontmatter.sh` — DocsAgent 변경분 통과
- 1-2 dogfood Story (CFP-33 또는 다음 real Story)에서 Orchestrator §10 직접 Edit 동작 확인 (본 CFP scope 외 — 다음 PR 검증)

### Followups (CFP-33+)
- CFP-33: contract lint harness 신설 — `docs/inter-plugin-contracts/**` 의 cross-contract 의존성 + example 유효성 검증. `review-verdict-v1.md` frontmatter 백필 (allowlist 제거)
- CFP-34: workflow yaml syntax test + marketplace sync auto + `story-section-write-guard.yml`
- CFP-35: codeforge-review v2 retrofit (verdict 반환 → self-write)
```

- [ ] **Step 8.3: Verify CHANGELOG well-formed**

```bash
head -45 CHANGELOG.md
```

Expected: v0.19.0 entry 정상 위치, 헤더 구조 문제 없음.

- [ ] **Step 8.4: Commit**

```bash
git add .claude-plugin/plugin.json CHANGELOG.md
git commit -m "chore(cfp-32): bump v0.18.0 → v0.19.0 + CHANGELOG entry"
```

---

## Task 9: Add this plan file to git + final lint sweep + push + open PR

- [ ] **Step 9.1: Add the plan file itself**

```bash
git add docs/superpowers/plans/2026-04-29-cfp-32-foundation-invariant-ssot.md
git commit -m "docs(cfp-32): implementation plan saved"
```

- [ ] **Step 9.2: Run all lint scripts — expect ALL PASS**

```bash
echo "=== check-doc-frontmatter ===" && bash scripts/check-doc-frontmatter.sh && \
echo "=== check-doc-section-schema ===" && bash scripts/check-doc-section-schema.sh && \
echo "=== check-write-permission-redistribution ===" && bash scripts/check-write-permission-redistribution.sh && \
echo "=== check-no-atlassian ===" && bash scripts/check-no-atlassian.sh && \
echo "=== check-doc-links ===" && bash scripts/check-doc-links.sh && \
echo "=== ALL PASS ==="
```

Expected: ALL PASS. 만약 한 단계 fail 시 그 단계의 root cause 진단 (예: broken link → 해당 markdown link 수정 후 재실행).

- [ ] **Step 9.3: Verify branch state**

```bash
git status && git log --oneline -10
```

Expected: clean working tree, 8 commits on `cfp-32-foundation-invariant-ssot` branch (Tasks 1-8 + plan).

- [ ] **Step 9.4: Push branch to origin**

```bash
git push -u origin cfp-32-foundation-invariant-ssot
```

- [ ] **Step 9.5: Open PR**

```bash
gh pr create --base main --head cfp-32-foundation-invariant-ssot \
  --title "feat(cfp-32): ζ arc F1 — invariant SSOT 3종 + §10 Orchestrator 단독 owner (v0.19.0)" \
  --body "$(cat <<'EOF'
## Summary
- ζ arc 첫 foundation step (CFP-31 §5.2 구현)
- 3 invariant SSOT 신설: comment-prefix-registry-v1 · label-registry-v1 · fix-event-v1
- §10 FIX Ledger 갱신 권한 DocsAgent → Orchestrator 단독 이관
- 2 lint script 확장 (frontmatter + section schema for `docs/inter-plugin-contracts/**`)

## 핵심
- **Codex round 2 조건 #2 직접 대응**: lane plugin 추출 시작 전 phase prefix · label · FIX event 필드 machine-readable contract 사전 구축
- **Non-BREAKING**: schema 도입 + narrative 갱신만. 기존 Story file·GitHub Issue·CI Action 동작 변화 없음
- **DocsAgent 단계적 해체**: agent file 삭제는 CFP-40. 본 CFP는 §10 권한만 회수 + cross-ref 갱신
- **legacy allowlist**: `review-verdict-v1.md`는 CFP-29 산출물 — CFP-33 contract harness에서 backfill 후 allowlist 제거

## 후속
- CFP-33: contract lint harness (cross-contract 의존성 + example 유효성). review-verdict-v1.md frontmatter backfill
- CFP-34: workflow yaml syntax test + marketplace sync auto + story-section-write-guard.yml
- CFP-35: codeforge-review v2 retrofit (첫 lane self-write 검증)

## Test plan
- [x] `scripts/check-doc-frontmatter.sh` strict — 5 owner path 통과
- [x] `scripts/check-doc-section-schema.sh` strict — 5 owner path 통과
- [x] `scripts/check-doc-links.sh` — 신규 cross-ref 무결
- [x] `scripts/check-agent-frontmatter.sh` — DocsAgent 변경분 통과
- [x] `scripts/check-write-permission-redistribution.sh` — CFP-26 invariant 유지
- [x] `scripts/check-no-atlassian.sh` 통과
- [ ] CI green (push 후 확인)
- [ ] User 검토 — 9 CFP 로드맵 다음 단계 (CFP-33) 진행 시점·범위 합의

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 9.6: Verify CI green + user review**

```bash
gh pr checks $(gh pr view --json number -q '.number') 2>&1 | head -30
```

Expected: 모든 CI job green. 1건이라도 fail 시 그 job log 분석 후 수정 → push.

---

## Self-Review Checklist (Plan completion)

작성자 (Claude)가 본 plan을 검토했음을 표시:

- [x] **Spec coverage** — CFP-31 §5.2 deliverable 9개 모두 task 매핑됨:
  - 3 SSOT 파일 신설 → Task 3, 4, 5
  - 2 lint script 확장 → Task 1, 2
  - playbook §6.4 갱신 → Task 6
  - DocsAgent.md 갱신 → Task 7
  - plugin.json + CHANGELOG → Task 8
  - 1-2 dogfood Story 검증 → CFP-33 또는 다음 real Story (본 plan scope 외 — CHANGELOG Followups에 명시)
- [x] **Placeholder scan** — 모든 step의 코드/명령은 완전. TBD/TODO/"적절히" 등 표현 없음
- [x] **Type consistency** — frontmatter 필드명 일관 (kind/registry/version/status/authors). lint script 변수명 일관 (`LEGACY_INTER_PLUGIN_CONTRACTS`). label color 6자리 hex 일관
- [x] **Scope check** — 본 plan은 CFP-32 단일 구현. CFP-31 parent spec의 다른 8개 CFP는 명시 제외 (Spec 참조 섹션 + CHANGELOG Followups에 후속 cross-ref)

## Execution Handoff

**Plan 작성 + 저장 완료**: [`docs/superpowers/plans/2026-04-29-cfp-32-foundation-invariant-ssot.md`](2026-04-29-cfp-32-foundation-invariant-ssot.md)

다음 실행 옵션 2가지:

1. **Subagent-Driven (recommended)** — Task 1부터 fresh subagent per task로 dispatch. 각 task 완료 사이 review 가능. 빠른 iteration
2. **Inline Execution** — 본 세션에서 task 직접 실행. checkpoint마다 review

어느 쪽으로 갈까?
