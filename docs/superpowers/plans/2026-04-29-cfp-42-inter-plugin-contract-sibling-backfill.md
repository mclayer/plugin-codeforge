# CFP-42 Implementation Plan: Inter-plugin Contract Sibling Backfill

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ζ arc 가 만든 5 lane plugin canonical contract 의 wrapper sibling reference 를 backfill 하고, ADR-010 sync 정책 + lint 확장으로 향후 누락 차단.

**Architecture:** [review-verdict-v2](../../inter-plugin-contracts/review-verdict-v2.md) 의 sibling 패턴을 5 신규 contract 에 일반화. `MANIFEST.yaml` 으로 `kind: contract` registry 명시화 + lint 4 종 신규 검사 (manifest completeness · orphan · ADR-010 reference · sibling marker). `kind: registry` 파일 (comment-prefix-registry/fix-event/label-registry) 은 기존 lint chain 유지로 분리.

**Tech Stack:** Markdown + YAML manifest + Bash/Python lint script (`pyyaml`) + GitHub MCP (`mcp__github__get_file_contents`) for canonical fetch.

**Note (workflow ↔ artifacts):** CFP-42 의 [docs/stories/CFP-42.md](../../stories/CFP-42.md) Story file 은 `story-init.yml` GitHub Action 이 Issue Form (story.yml) 제출 시점에 자동 생성합니다. 본 plan 은 **기술 산출물** (ADR + Change Plan + MANIFEST + 5 sibling + review-verdict frontmatter update + lint + test harness + CLAUDE.md) 에 집중합니다. Story file 의 §1 verbatim · §2-7 (Phase 1) · §8-11 (Phase 2) 채움은 codeforge 7-lane 워크플로우의 lane plugin 들이 self-write 합니다.

**Spec reference:** [docs/superpowers/specs/2026-04-29-cfp-42-inter-plugin-contract-sibling-backfill-design.md](../specs/2026-04-29-cfp-42-inter-plugin-contract-sibling-backfill-design.md)

---

## File Structure

| Path | Action | Phase |
|---|---|---|
| `docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md` | NEW | Phase 1 |
| `docs/change-plans/cfp-42-inter-plugin-contract-sibling-backfill.md` | NEW | Phase 1 |
| `docs/inter-plugin-contracts/MANIFEST.yaml` | NEW | Phase 2 |
| `docs/inter-plugin-contracts/requirements-output-v1.md` | NEW | Phase 2 |
| `docs/inter-plugin-contracts/design-output-v1.md` | NEW | Phase 2 |
| `docs/inter-plugin-contracts/develop-output-v1.md` | NEW | Phase 2 |
| `docs/inter-plugin-contracts/test-verdict-v1.md` | NEW | Phase 2 |
| `docs/inter-plugin-contracts/pmo-output-v1.md` | NEW | Phase 2 |
| `docs/inter-plugin-contracts/review-verdict-v1.md` | UPDATE (frontmatter) | Phase 2 |
| `docs/inter-plugin-contracts/review-verdict-v2.md` | UPDATE (frontmatter) | Phase 2 |
| `scripts/test-check-inter-plugin-contracts.sh` | NEW (test harness) | Phase 2 |
| `scripts/check-inter-plugin-contracts.sh` | UPDATE (4 new checks) | Phase 2 |
| `CLAUDE.md` | UPDATE ("Inter-plugin Contract" 섹션) | Phase 2 |

---

## Task 1: Author ADR-010

**Files:**
- Create: `docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md`

- [ ] **Step 1: Write ADR-010**

Create file with the following content (replacing nothing — full file body):

```markdown
---
adr_number: 10
title: Inter-plugin Contract Sibling Sync — canonical/sibling 책임 + sync 트리거 + drift 처리 정책
status: Proposed
category: Team & Process
date: 2026-04-29
related_files:
  - docs/superpowers/specs/2026-04-29-cfp-42-inter-plugin-contract-sibling-backfill-design.md (parent CFP)
  - docs/adr/ADR-008-inter-plugin-contract-versioning.md (versioning 룰 — 본 ADR 과 함께 모든 contract frontmatter 에 인용 의무)
  - docs/adr/ADR-009-wrapper-only-decomposition.md (ζ arc 결과 — 본 ADR 의 P0 gap 출처)
  - docs/inter-plugin-contracts/MANIFEST.yaml (contract 완결성 SSOT)
  - docs/inter-plugin-contracts/review-verdict-v2.md (선례 패턴)
---

## 상태

Proposed (2026-04-29) — CFP-42 Phase 1 PR merge 시 Accepted 전환. CFP-42 Phase 2 PR merge 시 Adopted 전환.

## 컨텍스트

ζ arc (CFP-31 parent · CFP-29~CFP-40 추출) 가 6 lane plugin 으로 분리되며 5 신규 inter-plugin `kind: contract` 표면을 lane plugin 들의 `docs/inter-plugin-contracts/` 에 canonical 로 신설:
- `requirements-output-v1` (codeforge-requirements)
- `design-output-v1` (codeforge-design)
- `develop-output-v1` (codeforge-develop)
- `test-verdict-v1` (codeforge-test)
- `pmo-output-v1` (codeforge-pmo)

ADR-009 본문 §51 은 "Inter-plugin contract 6종 보유" 라고 단언하지만, 실제 wrapper repo 의 [docs/inter-plugin-contracts/](../inter-plugin-contracts/) 에는 5 파일 — 그중 3 은 `kind: registry`, 2 는 `kind: contract` (review-verdict v1+v2). 즉 5 lane output sibling reference 가 wrapper 에 backfill 안 된 상태로 ζ arc 종료.

CFP-35 (review-verdict v2 retrofit) 는 이미 "**canonical at lane plugin repo + sibling at wrapper repo**" 패턴을 도입 ([review-verdict-v2.md:19-22](../inter-plugin-contracts/review-verdict-v2.md#L19-L22)) — 본 ADR 은 이 패턴을 5 신규 contract 에 일반화하고, 향후 누락이 재발하지 않도록 명시적 정책으로 동결.

## 결정

### 1. Canonical 위치 룰

- `kind: contract` 의 canonical 은 **producer plugin** repo 의 `docs/inter-plugin-contracts/<contract-name>-v<N>.md`
- 현재 producer 분포: 5 lane output 은 각 lane plugin, review_verdict 는 codeforge-review

### 2. Sibling 위치 룰

- wrapper repo `docs/inter-plugin-contracts/<contract-name>-v<N>.md` 가 sibling reference (consumer 1차 진입점)
- sibling 본문은 canonical 과 verbatim 일치. 부가 정보는 본문 시작의 "**상위 SSOT 위치**" 섹션 (review-verdict-v2 패턴)
- sibling frontmatter 에 `related_adrs ∋ "ADR-008"` (versioning 룰) + `related_adrs ∋ "ADR-010"` (본 ADR) 의무

### 3. MANIFEST.yaml = kind:contract registry SSOT

wrapper repo `docs/inter-plugin-contracts/MANIFEST.yaml` 가 모든 `kind: contract` 파일을 enumerate. 신규 contract 추가 절차:

1. lane plugin 에 canonical 작성 (ADR-008 versioning 룰 준수)
2. wrapper MANIFEST.yaml 에 entry 추가
3. wrapper sibling file 작성 (canonical 본문 verbatim mirror + 상위 SSOT 위치 섹션 + 본 ADR 인용 frontmatter)
4. 본 ADR 본문 불변 — MANIFEST 만 갱신

`kind: registry` 파일 (cross-cutting protocol — comment-prefix-registry, fix-event, label-registry) 은 본 MANIFEST 범위 밖. 기존 `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` 가 검증.

### 4. Sync 트리거

- canonical 변경 PR merge 직후 wrapper sibling sync PR open · merge 의무 (CFP-24 marketplace cross-repo sync 정책 동질)
- canonical PR body 또는 Story §11 에 "wrapper sibling sync PR 후속 의무" 명시
- author 의무 (본 ADR 시점) — CI 자동 차단은 후속 ADR (drift detection 도입 시점)

### 5. Drift 검출 정책

- 본 ADR 시점: manifest completeness + orphan + frontmatter schema (ADR-010 reference 포함) + sibling marker — `scripts/check-inter-plugin-contracts.sh` lint
- 본문 verbatim drift 검출 (canonical SHA vs sibling SHA 비교) 은 후속 ADR 에서 결정

## 결과

### 위배 시 처리

- lint FAIL: PR merge 차단 (필수 status check — wrapper repo CI)
- canonical 변경 후 sibling sync PR 누락: 다음 wrapper PR 가 lint manifest mismatch 로 차단 (간접 강제)
- 후속 ADR 에서 drift detection workflow 도입 시 직접 강제 가능

### 선례·관계 ADR

- ADR-008: 모든 contract frontmatter 에 함께 인용 의무. 본 ADR 은 ADR-008 의 versioning 룰을 전제로 한 sync 정책 layer
- ADR-009: ζ arc decomposition 결과 → 본 ADR 의 P0 gap 출처

### 후속 영향

- 7번째·8번째 contract 추가 시 4단계 절차 + lint 자동 차단의 이중 안전망 작동
- 향후 wrapper-canonical `kind: contract` (cross-cutting typed schema) 등장 시 MANIFEST schema 에 `role` 필드 도입 — 본 ADR 갱신 또는 신규 ADR

## 관련 파일

- [docs/inter-plugin-contracts/MANIFEST.yaml](../inter-plugin-contracts/MANIFEST.yaml) — registry SSOT
- [docs/inter-plugin-contracts/review-verdict-v2.md](../inter-plugin-contracts/review-verdict-v2.md) — 선례 패턴
- [scripts/check-inter-plugin-contracts.sh](../../scripts/check-inter-plugin-contracts.sh) — 본 ADR 강제 lint
- [docs/adr/ADR-008-inter-plugin-contract-versioning.md](ADR-008-inter-plugin-contract-versioning.md)
- [docs/adr/ADR-009-wrapper-only-decomposition.md](ADR-009-wrapper-only-decomposition.md)
```

- [ ] **Step 2: Run frontmatter lint**

Run: `bash scripts/check-doc-frontmatter.sh 2>&1 | tail -20`
Expected: PASS (ADR frontmatter schema 충족)

- [ ] **Step 3: Commit**

```bash
git add docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md
git commit -m "feat(cfp-42): add ADR-010 inter-plugin contract sibling sync policy"
```

---

## Task 2: Author Change Plan (Phase 1 산출물)

**Files:**
- Create: `docs/change-plans/cfp-42-inter-plugin-contract-sibling-backfill.md`

- [ ] **Step 1: Write Change Plan**

Create file with the following content:

```markdown
---
change_plan: cfp-42
title: Inter-plugin contract sibling backfill (5 lane output + MANIFEST + lint 확장)
story_key: CFP-42
status: Phase-1-Design
date: 2026-04-29
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-009 (Wrapper-only Decomposition)
  - ADR-010 (Inter-plugin Contract Sibling Sync — 본 CFP author)
---

## 1. 목표

ζ arc 가 도입한 5 lane plugin canonical `kind: contract` 의 wrapper sibling reference backfill + MANIFEST.yaml registry SSOT 신설 + lint 4 신규 검사로 향후 sibling 누락 차단.

## 2. 현재 구조 (As-is)

- `docs/inter-plugin-contracts/`: 5 파일 (3 kind:registry + 2 kind:contract — review-verdict v1+v2)
- `scripts/check-inter-plugin-contracts.sh`: kind:contract frontmatter+본문 sanity 검증 (manifest completeness 검증 없음)
- 5 lane plugin 의 canonical contract 는 각 plugin repo 의 `docs/inter-plugin-contracts/` 에 존재 — 각 plugin CLAUDE.md 가 자기 lane self-write 책임 명시

## 3. 도입할 설계 (To-be)

- `MANIFEST.yaml`: kind:contract registry SSOT (6 entry / 7 file — review_verdict v1+v2 + 5 신규)
- 5 신규 sibling file: review-verdict-v2 패턴 (frontmatter + "상위 SSOT 위치" 섹션 + canonical 본문 verbatim mirror)
- 기존 review-verdict v1+v2 frontmatter `related_adrs` 에 ADR-010 추가
- `check-inter-plugin-contracts.sh` 에 4 신규 검사 (manifest completeness · orphan · ADR-010 reference · sibling marker)
- `scripts/test-check-inter-plugin-contracts.sh` 신규 — lint 회귀 테스트 harness
- `CLAUDE.md` "Inter-plugin Contract" 섹션 — kind:contract 6 / kind:registry 3 분리 명시 + ADR-010 인용

## 4. 영향받는 컴포넌트

- wrapper repo `docs/inter-plugin-contracts/` 표면 (file 7 추가/갱신)
- wrapper repo `scripts/` (lint 1 갱신, harness 1 신규)
- consumer 사용 표면: lint 인터페이스 변경 없음 — 내부 검증 강화만

## 5. 마이그레이션 경로

본 CFP 는 wrapper repo 자체 self-application. 다른 plugin 또는 consumer 에 BREAKING 영향 없음. 선언:
- 5 lane plugin canonical 은 변경 없음
- review-verdict v1+v2 frontmatter 의 `related_adrs` array 에 항목 추가만 (consumer 로 노출되는 schema 의미 변경 없음)

## 6. 리팩터링 선행 항목

없음. 본 CFP 는 신규 file 추가 + 기존 lint 확장 + 메타데이터 갱신만.

## 7. 보안 설계

### 7.1 Trust boundary

- canonical 본문 verbatim mirror 의 supply-chain 영향: lane plugin canonical 이 손상되면 sibling 도 손상 가능. 다만 wrapper-only 모델에서 sibling 은 reference 문서 (실행 코드 아님) 라 직접 실행 영향 없음
- mirror 시점: Phase 2 PR 작성 시 1회 — `mcp__github__get_file_contents` 로 fetch, sha 기록은 본 CFP 시점에는 보존 안 함 (drift detection 후속 CFP 의 영역)

### 7.2 Threat model (STRIDE-LITE)

- Spoofing: lane plugin canonical 이 적대적으로 변경된 경우 → wrapper sibling sync PR 시 review 의 책임. 본 CFP 자동 검출 안 함
- Tampering: wrapper sibling file 이 변경된 경우 → wrapper repo CODEOWNERS + PR review 가 1차 방어
- Repudiation: N/A
- Information disclosure: contract 표면은 모두 public. 민감 데이터 부재
- Denial of service: lint 가 외부 API 호출 0 → DoS 표면 없음
- Elevation of privilege: N/A

### 7.3 Auth/authz

N/A — 본 CFP 는 문서·lint 만.

### 7.4 민감 데이터 분류·흐름

N/A.

### 7.5 위협↔완화 매핑

| 위협 | 완화 |
|---|---|
| canonical 손상 후 sibling 자동 mirror | 본 CFP 시점은 author 의무 (수동 PR 작성). 후속 CFP 에서 drift detection 도입 |
| sibling 누락 (sync PR 깜빡) | lint manifest mismatch 로 다음 wrapper PR 가 차단 (간접 강제) |

## 8. Test Contract

§8 의 자세한 케이스는 spec [§8 Test contract preview](../superpowers/specs/2026-04-29-cfp-42-inter-plugin-contract-sibling-backfill-design.md) 참조. 6 케이스 (T1-T6) 가 `scripts/test-check-inter-plugin-contracts.sh` 에 구현됨.

### 8.1 기능 테스트

- T1 manifest mismatch (negative)
- T2 orphan (negative)
- T3 frontmatter ADR-010 누락 (negative)
- T4 sibling marker section 누락 (negative)
- T5 정합 상태 (positive)
- T6 review-verdict v1+v2 + 3 kind:registry 회귀 (positive)

### 8.2 성능 테스트

N/A — 순수 shell+python lint, baseline 무관.

### 8.3 통합 테스트

`bash scripts/check-inter-plugin-contracts.sh` 가 wrapper main branch 상태에서 exit 0 반환.

## 9. 리뷰 결과

(Phase 1 설계 리뷰 시 채움)

## 10. FIX Ledger

(필요 시 FIX 발생할 때 채움)

## 11. 데이터 마이그레이션

N/A — schema 변경 없음. 기존 review-verdict v1+v2 frontmatter `related_adrs` array 에 ADR-010 항목 추가만 (additive, lossless). Migration / rollback / integrity invariant 모두 N/A.
```

- [ ] **Step 2: Run change-plan section schema lint**

Run: `bash scripts/check-doc-section-schema.sh 2>&1 | tail -20`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add docs/change-plans/cfp-42-inter-plugin-contract-sibling-backfill.md
git commit -m "feat(cfp-42): add change plan for inter-plugin contract sibling backfill"
```

---

## Task 3: Create MANIFEST.yaml

**Files:**
- Create: `docs/inter-plugin-contracts/MANIFEST.yaml`

- [ ] **Step 1: Write MANIFEST.yaml**

```yaml
# docs/inter-plugin-contracts/MANIFEST.yaml
# SSOT for kind:contract files completeness — referenced by ADR-010
# Owner: codeforge wrapper repo. Updated when adding/removing kind:contract.
# Scope: kind:contract files only. kind:registry files (comment-prefix-registry,
# fix-event, label-registry) are managed by check-doc-frontmatter.sh chain.
contracts:
  - name: review_verdict
    canonical_repo: mclayer/plugin-codeforge-review
    canonical_path: docs/inter-plugin-contracts/
    files:
      - { file: review-verdict-v1.md, contract_version: "1.0", status: Deprecated }
      - { file: review-verdict-v2.md, contract_version: "2.0", status: Active }

  - name: requirements_output
    canonical_repo: mclayer/plugin-codeforge-requirements
    canonical_path: docs/inter-plugin-contracts/
    files:
      - { file: requirements-output-v1.md, contract_version: "1.0", status: Active }

  - name: design_output
    canonical_repo: mclayer/plugin-codeforge-design
    canonical_path: docs/inter-plugin-contracts/
    files:
      - { file: design-output-v1.md, contract_version: "1.0", status: Active }

  - name: develop_output
    canonical_repo: mclayer/plugin-codeforge-develop
    canonical_path: docs/inter-plugin-contracts/
    files:
      - { file: develop-output-v1.md, contract_version: "1.0", status: Active }

  - name: test_verdict
    canonical_repo: mclayer/plugin-codeforge-test
    canonical_path: docs/inter-plugin-contracts/
    files:
      - { file: test-verdict-v1.md, contract_version: "1.0", status: Active }

  - name: pmo_output
    canonical_repo: mclayer/plugin-codeforge-pmo
    canonical_path: docs/inter-plugin-contracts/
    files:
      - { file: pmo-output-v1.md, contract_version: "1.0", status: Active }
```

- [ ] **Step 2: Validate YAML syntax**

Run: `python3 -c "import yaml; yaml.safe_load(open('docs/inter-plugin-contracts/MANIFEST.yaml'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add docs/inter-plugin-contracts/MANIFEST.yaml
git commit -m "feat(cfp-42): add MANIFEST.yaml for kind:contract registry SSOT"
```

---

## Task 4: Mirror requirements-output-v1.md sibling

**Files:**
- Create: `docs/inter-plugin-contracts/requirements-output-v1.md`

- [ ] **Step 1: Fetch canonical content**

Use the `mcp__github__get_file_contents` tool with these arguments:
```json
{
  "owner": "mclayer",
  "repo": "plugin-codeforge-requirements",
  "path": "docs/inter-plugin-contracts/requirements-output-v1.md"
}
```

Save the returned body content to a temp variable for the next step.

- [ ] **Step 2: Assemble sibling file**

Compose the file with this structure: frontmatter (CFP-42 spec §6 template) + "## 0. 상위 SSOT 위치" section + canonical body verbatim. Concrete content:

```markdown
---
kind: contract
contract_version: "1.0"
status: Active
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-requirements (lane plugin, producer + self-writer)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-010 (Inter-plugin Contract Sibling Sync — sync 정책)
authors:
  - CFP-42 sibling backfill (2026-04-29) — wrapper sibling 첫 작성, canonical 본문 verbatim mirror
---

# requirements_output v1 — Inter-plugin Contract

`codeforge-requirements` plugin → `codeforge` core (Orchestrator) 단방향 schema.

## 0. 상위 SSOT 위치

**상위 SSOT 위치**:
- `mclayer/plugin-codeforge-requirements/docs/inter-plugin-contracts/requirements-output-v1.md`: **canonical** (codeforge-requirements repo)
- 본 file (codeforge wrapper repo): sibling reference (canonical 변경 시 sync 의무 — ADR-010 + CFP-24 marketplace sync 정책 동질)
- ADR-008 (versioning 룰): codeforge wrapper repo `docs/adr/ADR-008-inter-plugin-contract-versioning.md`
- ADR-010 (본 contract 의 sibling sync 정책): codeforge wrapper repo `docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md`

[paste canonical body from Step 1 — strip canonical's own frontmatter, keep all content from first `# ` heading onwards. If canonical's first heading duplicates the title above, drop that one duplicate heading]
```

- [ ] **Step 3: Validate frontmatter**

Run: `bash scripts/check-doc-frontmatter.sh 2>&1 | tail -10`
Expected: PASS (kind:contract frontmatter 충족)

- [ ] **Step 4: Commit**

```bash
git add docs/inter-plugin-contracts/requirements-output-v1.md
git commit -m "feat(cfp-42): add requirements-output-v1 wrapper sibling"
```

---

## Task 5: Mirror design-output-v1.md sibling

**Files:**
- Create: `docs/inter-plugin-contracts/design-output-v1.md`

- [ ] **Step 1: Fetch canonical content**

Use `mcp__github__get_file_contents` with:
```json
{
  "owner": "mclayer",
  "repo": "plugin-codeforge-design",
  "path": "docs/inter-plugin-contracts/design-output-v1.md"
}
```

- [ ] **Step 2: Assemble sibling file**

Same template as Task 4 Step 2, replacing `requirements` with `design` in:
- `related_plugins[1]`: `codeforge-design (lane plugin, producer + self-writer)`
- title heading: `# design_output v1 — Inter-plugin Contract`
- producer plugin descriptor: `codeforge-design`
- canonical path in "상위 SSOT 위치": `mclayer/plugin-codeforge-design/docs/inter-plugin-contracts/design-output-v1.md`

- [ ] **Step 3: Validate frontmatter**

Run: `bash scripts/check-doc-frontmatter.sh 2>&1 | tail -10`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add docs/inter-plugin-contracts/design-output-v1.md
git commit -m "feat(cfp-42): add design-output-v1 wrapper sibling"
```

---

## Task 6: Mirror develop-output-v1.md sibling

**Files:**
- Create: `docs/inter-plugin-contracts/develop-output-v1.md`

- [ ] **Step 1: Fetch canonical content**

Use `mcp__github__get_file_contents` with:
```json
{
  "owner": "mclayer",
  "repo": "plugin-codeforge-develop",
  "path": "docs/inter-plugin-contracts/develop-output-v1.md"
}
```

- [ ] **Step 2: Assemble sibling file**

Same template as Task 4 Step 2, with substitutions:
- `related_plugins[1]`: `codeforge-develop (lane plugin, producer + self-writer)`
- title heading: `# develop_output v1 — Inter-plugin Contract`
- producer plugin descriptor: `codeforge-develop`
- canonical path: `mclayer/plugin-codeforge-develop/docs/inter-plugin-contracts/develop-output-v1.md`

- [ ] **Step 3: Validate frontmatter**

Run: `bash scripts/check-doc-frontmatter.sh 2>&1 | tail -10`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add docs/inter-plugin-contracts/develop-output-v1.md
git commit -m "feat(cfp-42): add develop-output-v1 wrapper sibling"
```

---

## Task 7: Mirror test-verdict-v1.md sibling

**Files:**
- Create: `docs/inter-plugin-contracts/test-verdict-v1.md`

- [ ] **Step 1: Fetch canonical content**

Use `mcp__github__get_file_contents` with:
```json
{
  "owner": "mclayer",
  "repo": "plugin-codeforge-test",
  "path": "docs/inter-plugin-contracts/test-verdict-v1.md"
}
```

- [ ] **Step 2: Assemble sibling file**

Same template as Task 4 Step 2, with substitutions:
- `related_plugins[1]`: `codeforge-test (lane plugin, producer + self-writer)`
- title heading: `# test_verdict v1 — Inter-plugin Contract`
- producer plugin descriptor: `codeforge-test`
- canonical path: `mclayer/plugin-codeforge-test/docs/inter-plugin-contracts/test-verdict-v1.md`

- [ ] **Step 3: Validate frontmatter**

Run: `bash scripts/check-doc-frontmatter.sh 2>&1 | tail -10`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add docs/inter-plugin-contracts/test-verdict-v1.md
git commit -m "feat(cfp-42): add test-verdict-v1 wrapper sibling"
```

---

## Task 8: Mirror pmo-output-v1.md sibling

**Files:**
- Create: `docs/inter-plugin-contracts/pmo-output-v1.md`

- [ ] **Step 1: Fetch canonical content**

Use `mcp__github__get_file_contents` with:
```json
{
  "owner": "mclayer",
  "repo": "plugin-codeforge-pmo",
  "path": "docs/inter-plugin-contracts/pmo-output-v1.md"
}
```

- [ ] **Step 2: Assemble sibling file**

Same template as Task 4 Step 2, with substitutions:
- `related_plugins[1]`: `codeforge-pmo (Cross-cutting plugin, producer + self-writer)`
- title heading: `# pmo_output v1 — Inter-plugin Contract`
- producer plugin descriptor: `codeforge-pmo`
- canonical path: `mclayer/plugin-codeforge-pmo/docs/inter-plugin-contracts/pmo-output-v1.md`

- [ ] **Step 3: Validate frontmatter**

Run: `bash scripts/check-doc-frontmatter.sh 2>&1 | tail -10`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add docs/inter-plugin-contracts/pmo-output-v1.md
git commit -m "feat(cfp-42): add pmo-output-v1 wrapper sibling"
```

---

## Task 9: Update review-verdict v1 + v2 frontmatter (add ADR-010 reference)

**Files:**
- Modify: `docs/inter-plugin-contracts/review-verdict-v1.md` (frontmatter only)
- Modify: `docs/inter-plugin-contracts/review-verdict-v2.md` (frontmatter only)

- [ ] **Step 1: Edit review-verdict-v1.md**

In `docs/inter-plugin-contracts/review-verdict-v1.md`, find this block:

```yaml
related_adrs:
  - ADR-001 (review-agent-unification — lane-agnostic worker)
  - ADR-008 (Inter-plugin Contract Versioning)
```

Replace with:

```yaml
related_adrs:
  - ADR-001 (review-agent-unification — lane-agnostic worker)
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-010 (Inter-plugin Contract Sibling Sync — sync 정책)
```

- [ ] **Step 2: Edit review-verdict-v2.md**

In `docs/inter-plugin-contracts/review-verdict-v2.md`, find:

```yaml
related_adrs:
  - ADR-001 (review-agent-unification — lane-agnostic worker)
  - ADR-008 (Inter-plugin Contract Versioning)
```

Replace with:

```yaml
related_adrs:
  - ADR-001 (review-agent-unification — lane-agnostic worker)
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-010 (Inter-plugin Contract Sibling Sync — sync 정책)
```

- [ ] **Step 3: Validate frontmatter**

Run: `bash scripts/check-inter-plugin-contracts.sh 2>&1 | tail -10`
Expected: PASS (existing 검사 + 추가된 related_adrs entry 가 list 형식 유지)

- [ ] **Step 4: Commit**

```bash
git add docs/inter-plugin-contracts/review-verdict-v1.md docs/inter-plugin-contracts/review-verdict-v2.md
git commit -m "feat(cfp-42): add ADR-010 reference to existing review-verdict siblings"
```

---

## Task 10: Create lint test harness

**Files:**
- Create: `scripts/test-check-inter-plugin-contracts.sh`

- [ ] **Step 1: Write test harness**

```bash
#!/usr/bin/env bash
# CFP-42 — Test harness for check-inter-plugin-contracts.sh
#
# 6 test cases (T1-T6 per CFP-42 spec §8). Each case:
#   1. Snapshot wrapper docs/inter-plugin-contracts/ + MANIFEST.yaml to tmp dir
#   2. Apply test-specific mutation
#   3. Run lint with cwd pointed at tmp dir
#   4. Assert expected exit code
#   5. Restore (no mutation to actual repo files)
#
# Usage: bash scripts/test-check-inter-plugin-contracts.sh
# Exit: 0 if all pass, 1 if any fail.

set -euo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
LINT_SCRIPT="$REPO_ROOT/scripts/check-inter-plugin-contracts.sh"

PASS=0
FAIL=0

run_test() {
  local name="$1"
  local expected_exit="$2"
  local mutation_fn="$3"

  local tmp
  tmp=$(mktemp -d)
  trap "rm -rf '$tmp'" RETURN

  # Mirror minimum repo structure to tmp
  mkdir -p "$tmp/docs/inter-plugin-contracts" "$tmp/scripts"
  cp "$REPO_ROOT/docs/inter-plugin-contracts/"*.md "$tmp/docs/inter-plugin-contracts/"
  cp "$REPO_ROOT/docs/inter-plugin-contracts/MANIFEST.yaml" "$tmp/docs/inter-plugin-contracts/"
  cp "$REPO_ROOT/scripts/check-inter-plugin-contracts.sh" "$tmp/scripts/"

  # Apply mutation in tmp
  ( cd "$tmp" && eval "$mutation_fn" )

  # Run lint with cwd at tmp
  local actual_exit=0
  ( cd "$tmp" && bash scripts/check-inter-plugin-contracts.sh ) >/dev/null 2>&1 || actual_exit=$?

  if [ "$actual_exit" = "$expected_exit" ]; then
    echo "✓ $name (exit $actual_exit)"
    PASS=$((PASS+1))
  else
    echo "✗ $name (expected exit $expected_exit, got $actual_exit)"
    FAIL=$((FAIL+1))
  fi
}

# T1: manifest mismatch — delete one sibling file
run_test "T1 manifest mismatch (sibling delete)" 1 \
  "rm docs/inter-plugin-contracts/requirements-output-v1.md"

# T2: orphan — add unregistered kind:contract file
run_test "T2 orphan (unregistered kind:contract)" 1 \
  "cat > docs/inter-plugin-contracts/orphan-v1.md <<'EOF'
---
kind: contract
contract_version: \"1.0\"
status: Active
related_plugins: [codeforge, codeforge-orphan]
related_adrs: [ADR-008, ADR-010]
authors: [test]
---
# orphan v1 — Inter-plugin Contract
**상위 SSOT 위치**:
- canonical: nowhere
## 1. body
## 2. body
## 3. body
EOF"

# T3: ADR-010 reference 누락 (sibling)
run_test "T3 sibling without ADR-010 reference" 1 \
  "python3 -c '
import re, pathlib
p = pathlib.Path(\"docs/inter-plugin-contracts/requirements-output-v1.md\")
text = p.read_text(encoding=\"utf-8\")
text = re.sub(r\"  - ADR-010.*\\n\", \"\", text, count=1)
p.write_text(text, encoding=\"utf-8\")
'"

# T4: sibling marker section 누락
run_test "T4 sibling without 상위 SSOT 위치 marker" 1 \
  "python3 -c '
import re, pathlib
p = pathlib.Path(\"docs/inter-plugin-contracts/requirements-output-v1.md\")
text = p.read_text(encoding=\"utf-8\")
text = re.sub(r\"\\*\\*상위 SSOT 위치\\*\\*:.*?(?=\\n##|\\Z)\", \"\", text, flags=re.DOTALL, count=1)
p.write_text(text, encoding=\"utf-8\")
'"

# T5: positive — no mutation
run_test "T5 정합 상태" 0 ":"

# T6: regression — review-verdict v1+v2 + 3 kind:registry exist (default state)
# (T5 already covers 정합 상태, T6 verifies kind:registry files don't trigger orphan)
run_test "T6 kind:registry files coexist (regression)" 0 \
  "test -f docs/inter-plugin-contracts/comment-prefix-registry-v1.md && \
   test -f docs/inter-plugin-contracts/fix-event-v1.md && \
   test -f docs/inter-plugin-contracts/label-registry-v1.md"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" = "0" ]
```

- [ ] **Step 2: Make executable + run (will fail until lint extension done)**

```bash
chmod +x scripts/test-check-inter-plugin-contracts.sh
bash scripts/test-check-inter-plugin-contracts.sh 2>&1 | tail -20
```

Expected: T1, T2, T3, T4 will FAIL (lint doesn't yet have these checks — exit 0 instead of 1). T5, T6 will PASS. This is intentional — TDD red state for upcoming Tasks 11-14.

- [ ] **Step 3: Commit**

```bash
git add scripts/test-check-inter-plugin-contracts.sh
git commit -m "test(cfp-42): add lint test harness (T1-T6 currently red for T1-T4)"
```

---

## Task 11: Lint check 1 — manifest completeness (T1)

**Files:**
- Modify: `scripts/check-inter-plugin-contracts.sh`

- [ ] **Step 1: Verify T1 currently fails**

```bash
bash scripts/test-check-inter-plugin-contracts.sh 2>&1 | grep "T1"
```
Expected: `✗ T1 manifest mismatch (sibling delete) (expected exit 1, got 0)` — confirming red state.

- [ ] **Step 2: Add manifest completeness check to lint**

In `scripts/check-inter-plugin-contracts.sh`, find this line (Python heredoc):

```python
contracts_dir = Path("docs/inter-plugin-contracts")
if not contracts_dir.exists():
    print("✓ CFP-33 inter-plugin-contracts: 디렉토리 부재 — skip")
    sys.exit(0)
```

Immediately after that block (before `errors = []`), insert:

```python
# CFP-42: Manifest completeness — every MANIFEST.yaml entry must exist as a file
manifest_path = contracts_dir / "MANIFEST.yaml"
manifest_files = set()  # set of basenames declared in MANIFEST
if manifest_path.exists():
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"::error::CFP-42 MANIFEST.yaml parse 실패: {e}")
        sys.exit(1)
    for entry in (manifest or {}).get("contracts", []):
        for fent in entry.get("files", []):
            fname = fent.get("file")
            if fname:
                manifest_files.add(fname)
                if not (contracts_dir / fname).exists():
                    print(f"::error::CFP-42 manifest entry {entry.get('name')} v{fent.get('contract_version')} missing sibling file {fname}")
                    sys.exit(1)
```

- [ ] **Step 3: Run test harness**

```bash
bash scripts/test-check-inter-plugin-contracts.sh 2>&1 | grep "T1"
```
Expected: `✓ T1 manifest mismatch (sibling delete) (exit 1)` — green.

- [ ] **Step 4: Run full lint to ensure no regression**

```bash
bash scripts/check-inter-plugin-contracts.sh 2>&1 | tail -5
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/check-inter-plugin-contracts.sh
git commit -m "feat(cfp-42): add manifest completeness check to inter-plugin-contracts lint"
```

---

## Task 12: Lint check 2 — orphan (T2)

**Files:**
- Modify: `scripts/check-inter-plugin-contracts.sh`

- [ ] **Step 1: Verify T2 currently fails**

```bash
bash scripts/test-check-inter-plugin-contracts.sh 2>&1 | grep "T2"
```
Expected: `✗ T2 orphan (unregistered kind:contract) (expected exit 1, got 0)`.

- [ ] **Step 2: Add orphan check**

In `scripts/check-inter-plugin-contracts.sh` Python heredoc, find this block (the per-file iteration loop):

```python
for md in sorted(contracts_dir.rglob("*.md")):
    if md.name.lower() in {"readme.md", "index.md"}:
        continue
```

Inside the loop body, after the `kind` check that determines `if not isinstance(fm, dict) or fm.get("kind") != "contract": continue`, add:

```python
    # CFP-42: orphan check — kind:contract must be registered in MANIFEST
    if md.name not in manifest_files:
        errors.append(f"{md}: orphan kind:contract file (not registered in MANIFEST.yaml)")
```

- [ ] **Step 3: Run test harness**

```bash
bash scripts/test-check-inter-plugin-contracts.sh 2>&1 | grep -E "T1|T2"
```
Expected: T1 ✓, T2 ✓.

- [ ] **Step 4: Run full lint**

```bash
bash scripts/check-inter-plugin-contracts.sh 2>&1 | tail -5
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/check-inter-plugin-contracts.sh
git commit -m "feat(cfp-42): add orphan check (kind:contract must be in MANIFEST)"
```

---

## Task 13: Lint check 3 — ADR-010 reference required (T3)

**Files:**
- Modify: `scripts/check-inter-plugin-contracts.sh`

- [ ] **Step 1: Verify T3 currently fails**

```bash
bash scripts/test-check-inter-plugin-contracts.sh 2>&1 | grep "T3"
```
Expected: `✗ T3 sibling without ADR-010 reference (expected exit 1, got 0)`.

- [ ] **Step 2: Add ADR-010 reference check**

In `scripts/check-inter-plugin-contracts.sh` Python heredoc, find the per-file frontmatter validation block (where `for list_field in ("related_plugins", "related_adrs", "authors"):` exists). After that block, add:

```python
    # CFP-42: sibling must reference ADR-008 + ADR-010
    related_adrs_str = " ".join(str(x) for x in (fm.get("related_adrs") or []))
    if "ADR-008" not in related_adrs_str:
        errors.append(f"{md}: related_adrs must reference ADR-008 (versioning rule)")
    if "ADR-010" not in related_adrs_str:
        errors.append(f"{md}: related_adrs must reference ADR-010 (sibling sync policy)")
```

- [ ] **Step 3: Run test harness**

```bash
bash scripts/test-check-inter-plugin-contracts.sh 2>&1 | grep -E "T1|T2|T3"
```
Expected: T1 ✓, T2 ✓, T3 ✓.

- [ ] **Step 4: Run full lint**

```bash
bash scripts/check-inter-plugin-contracts.sh 2>&1 | tail -5
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/check-inter-plugin-contracts.sh
git commit -m "feat(cfp-42): require ADR-008/ADR-010 references in kind:contract files"
```

---

## Task 14: Lint check 4 — sibling marker section (T4)

**Files:**
- Modify: `scripts/check-inter-plugin-contracts.sh`

- [ ] **Step 1: Verify T4 currently fails**

```bash
bash scripts/test-check-inter-plugin-contracts.sh 2>&1 | grep "T4"
```
Expected: `✗ T4 sibling without 상위 SSOT 위치 marker (expected exit 1, got 0)`.

- [ ] **Step 2: Add sibling marker check**

In `scripts/check-inter-plugin-contracts.sh` Python heredoc, find the body section count check:

```python
    # 5. 본문 구조화 sanity — 최소 3개 ## 섹션
    body = text.split("\n---\n", 1)[1] if "\n---\n" in text else text
    section_count = len(re.findall(r"^## ", body, re.MULTILINE))
    if section_count < 3:
        errors.append(f"{md}: 본문 ## 섹션 부족 ({section_count} < 3) — 구조화 강제")
```

After that block, add:

```python
    # CFP-42: sibling marker section — every kind:contract in MANIFEST is sibling for now
    if not re.search(r"\*\*상위 SSOT 위치\*\*:", body):
        errors.append(f"{md}: sibling marker section missing (need '**상위 SSOT 위치**:' in body)")
```

- [ ] **Step 3: Run test harness — all 6 should pass**

```bash
bash scripts/test-check-inter-plugin-contracts.sh 2>&1 | tail -10
```
Expected: `Results: 6 passed, 0 failed`

- [ ] **Step 4: Run full lint**

```bash
bash scripts/check-inter-plugin-contracts.sh 2>&1 | tail -5
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/check-inter-plugin-contracts.sh
git commit -m "feat(cfp-42): require '상위 SSOT 위치' sibling marker in kind:contract body"
```

---

## Task 15: Update CLAUDE.md "Inter-plugin Contract" 섹션

**Files:**
- Modify: `CLAUDE.md` (the "Inter-plugin Contract" section, currently around line 492)

- [ ] **Step 1: Locate current section**

Find in `CLAUDE.md` the section starting with `## Inter-plugin Contract` (or the equivalent header — search for the text `review_verdict v1`).

- [ ] **Step 2: Replace with updated listing**

Replace the entire "Inter-plugin Contract" section content (heading remaining) with:

```markdown
## Inter-plugin Contract (CFP-29 Phase 1 후 + CFP-42 sibling backfill)

codeforge core 가 외부 plugin과 통신할 때의 typed schema. wrapper repo 의 [docs/inter-plugin-contracts/](docs/inter-plugin-contracts/) 디렉터리는 두 종류 보유:

### kind:contract (typed inter-plugin schema, 6 entry / 7 file)

[docs/inter-plugin-contracts/MANIFEST.yaml](docs/inter-plugin-contracts/MANIFEST.yaml) 가 SSOT. lint 는 [scripts/check-inter-plugin-contracts.sh](scripts/check-inter-plugin-contracts.sh).

| Contract | Producer plugin | Files (wrapper sibling) |
|---|---|---|
| `review_verdict` | codeforge-review | review-verdict-v1.md (Deprecated) · review-verdict-v2.md (Active) |
| `requirements_output` | codeforge-requirements | requirements-output-v1.md (Active) |
| `design_output` | codeforge-design | design-output-v1.md (Active) |
| `develop_output` | codeforge-develop | develop-output-v1.md (Active) |
| `test_verdict` | codeforge-test | test-verdict-v1.md (Active) |
| `pmo_output` | codeforge-pmo | pmo-output-v1.md (Active) |

각 wrapper sibling 은 lane plugin canonical 의 verbatim mirror + "**상위 SSOT 위치**" 섹션. canonical 변경 시 wrapper sibling sync PR 후속 의무 ([ADR-010](docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md)).

### kind:registry (cross-cutting protocol, 3 file)

wrapper-owned. 본 lint scope 밖 — `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` 가 검증.

- [comment-prefix-registry-v1.md](docs/inter-plugin-contracts/comment-prefix-registry-v1.md) — 11 phase prefix taxonomy
- [fix-event-v1.md](docs/inter-plugin-contracts/fix-event-v1.md) — Story §10 FIX Ledger writer monopoly
- [label-registry-v1.md](docs/inter-plugin-contracts/label-registry-v1.md) — phase/gate/fix label taxonomy

### Versioning + sync 정책

- [ADR-008 Inter-plugin Contract Versioning](docs/adr/ADR-008-inter-plugin-contract-versioning.md): SemVer 룰 (v1.x backward-compat, v2.0 BREAKING + 양쪽 plugin 동시 bump + 새 ADR)
- [ADR-010 Inter-plugin Contract Sibling Sync](docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md): canonical/sibling 책임 + sync 트리거 + 신규 contract 추가 4단계 절차

### Write boundary

각 lane plugin 이 자기 contract 의 producer + self-writer. wrapper Orchestrator 는 contract verdict 에 응답해 다음 lane 라우팅·Story §10 FIX Ledger 만 처리. 상세 흐름은 [docs/orchestrator-playbook.md](docs/orchestrator-playbook.md) 참조.
```

- [ ] **Step 3: Validate CLAUDE.md still parses**

Run: `bash scripts/check-inter-plugin-contracts.sh && bash scripts/check-doc-section-schema.sh 2>&1 | tail -10`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "feat(cfp-42): update CLAUDE.md Inter-plugin Contract section (kind:contract 6 / kind:registry 3)"
```

---

## Task 16: Final integration verification

**Files:** (none — verification only)

- [ ] **Step 1: Run full lint chain**

```bash
bash scripts/check-doc-frontmatter.sh && \
bash scripts/check-doc-section-schema.sh && \
bash scripts/check-inter-plugin-contracts.sh && \
bash scripts/test-check-inter-plugin-contracts.sh && \
bash scripts/check-doc-links.sh
echo "exit: $?"
```
Expected: all pass, `exit: 0`.

- [ ] **Step 2: Verify file inventory**

```bash
ls docs/inter-plugin-contracts/ | wc -l && echo "---" && grep -c "file:" docs/inter-plugin-contracts/MANIFEST.yaml
```
Expected:
- First line: `11` (10 .md files + 1 MANIFEST.yaml). Files: `comment-prefix-registry-v1.md` · `design-output-v1.md` · `develop-output-v1.md` · `fix-event-v1.md` · `label-registry-v1.md` · `pmo-output-v1.md` · `requirements-output-v1.md` · `review-verdict-v1.md` · `review-verdict-v2.md` · `test-verdict-v1.md` · `MANIFEST.yaml`
- Second line: `7` — MANIFEST.yaml `file:` line count (review-verdict v1+v2 + 5 lane outputs)

- [ ] **Step 3: Git log review**

```bash
git log --oneline main..HEAD | head -20
```
Expected: ~16 commits (Task 1-15 = 15 commits + spec update if any).

- [ ] **Step 4: Done — final note**

본 plan 완료 시점에서 wrapper repo 는:
- kind:contract 6 entry / 7 file 가 MANIFEST 에 등록되고 lint 가 강제
- ADR-010 이 sibling sync 정책을 동결
- 향후 7번째·8번째 contract 추가는 4단계 절차 (canonical 작성 → MANIFEST entry → sibling file → 본 ADR 불변) + lint 자동 차단의 이중 안전망 적용

CFP-42 의 codeforge dogfooded workflow (Story Issue Form → story-init.yml → Phase 1 PR → Phase 2 PR) 는 본 plan 실행과 별개로 진행. 본 plan 의 산출물이 Phase 1+2 PR 의 commits 가 됨.

---

## Out-of-plan tasks (handled by codeforge dogfooded workflow)

다음 task 들은 본 plan 의 직접 task 아님 — codeforge 의 7-lane workflow 가 처리:
- Story file `docs/stories/CFP-42.md` §1-11 채움 (story-init.yml Action + lane plugin self-write)
- GitHub Issue / PR phase label 전환
- Phase 1 design review (DesignReviewPL)
- Phase 2 code review (CodeReviewPL) · 구현 테스트 (TestAgent) · 보안 테스트 (SecurityTestPL)
- gate:design-review-pass / gate:security-test-pass 라벨 부착
- PR merge + Issue auto-close

본 plan 의 산출물 + commit 은 Phase 1+2 PR 의 실질적 내용물을 구성하며, 위 workflow steps 는 그것에 대해 lane plugin들이 reactive 하게 수행.
