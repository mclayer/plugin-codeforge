---
spec_id: cfp-42
title: Inter-plugin contract sibling backfill — 5 lane output contract wrapper sibling 추가 + ADR-010 sync 정책 + lint 확장
status: Draft
date: 2026-04-29
authors:
  - User (Codex 분석 검증 중 wrapper sibling 부재 가설 제기 — Codex 1차 분석의 잘못된 분류 교정)
  - Claude (Opus 4.7) — synthesis · design author
  - Codex (GPT-5.4 via codex-rescue) — 1 round wrapper-only 정합성 분석 (raw findings 의 부분만 채택)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning — versioning 룰. 모든 contract 의 backward-compat 계약 표면)
  - ADR-009 (Wrapper-only Decomposition — ζ arc 결과. 본 CFP 가 추격하는 미해결 P0 gap 의 출처)
  - ADR-010-NEW (Inter-plugin Contract Sibling Sync — 본 spec 의 결정 ADR 후보)
related_files:
  - docs/inter-plugin-contracts/requirements-output-v1.md (NEW — kind:contract sibling, canonical: codeforge-requirements)
  - docs/inter-plugin-contracts/design-output-v1.md (NEW — kind:contract sibling, canonical: codeforge-design)
  - docs/inter-plugin-contracts/develop-output-v1.md (NEW — kind:contract sibling, canonical: codeforge-develop)
  - docs/inter-plugin-contracts/test-verdict-v1.md (NEW — kind:contract sibling, canonical: codeforge-test)
  - docs/inter-plugin-contracts/pmo-output-v1.md (NEW — kind:contract sibling, canonical: codeforge-pmo)
  - docs/inter-plugin-contracts/review-verdict-v1.md (UPDATE — frontmatter related_adrs 에 ADR-010 추가)
  - docs/inter-plugin-contracts/review-verdict-v2.md (UPDATE — frontmatter related_adrs 에 ADR-010 추가)
  - docs/inter-plugin-contracts/MANIFEST.yaml (NEW — kind:contract registry SSOT, 6 entry / 7 file)
  - docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md (NEW — sync 정책 + drift 처리 결정)
  - scripts/check-inter-plugin-contracts.sh (UPDATE — manifest completeness + frontmatter schema 검증)
  - CLAUDE.md (UPDATE — "Inter-plugin Contract" 섹션 9 contract listing + ADR-010 참조)
  - docs/stories/CFP-42.md (NEW via story-init.yml Action — §1-11 Story SSOT)
  - docs/change-plans/cfp-42-inter-plugin-contract-sibling-backfill.md (NEW — Phase 1 PR ArchitectAgent 산출물)
related_canonicals:
  - mclayer/plugin-codeforge-requirements/docs/inter-plugin-contracts/requirements-output-v1.md
  - mclayer/plugin-codeforge-design/docs/inter-plugin-contracts/design-output-v1.md
  - mclayer/plugin-codeforge-develop/docs/inter-plugin-contracts/develop-output-v1.md
  - mclayer/plugin-codeforge-test/docs/inter-plugin-contracts/test-verdict-v1.md
  - mclayer/plugin-codeforge-pmo/docs/inter-plugin-contracts/pmo-output-v1.md
---

## 0. 사용자 원문 (verbatim)

라운드별 핵심 발화 4건:

> 1. (분석 의뢰) "codeforge와 기반 plugin을 codex와 함께 분석해라."
> 2. (Codex 분석 비판) "이 레포에 다른 문서 내용이 남아있다는 것은 필요한 repo에 해당 내용이 없다는걸 의미하지 않나"
> 3. (수정 의사 표명) "이 부분 수정하자"
> 4. (옵션 선택) "a" — A 옵션 (CFP-42 정식 Story full 7-lane)
> 5. (기술 범위) "ㅇㅋ" — A2 (Standard: sibling + ADR + lint 확장) 권장안 수락
> 6. (지속 진행 위임) "ㅇㅋ 이것도 마찬가지로 승인받을거 받고 이후에는 끝까지 진행해" — 추가 design 섹션 일괄 승인 + 끝까지 진행 위임

추가 정렬:
- Codex 1차 분석은 wrapper 의 stale 흔적 모두를 "wrapper cleanup 필요" 로 일괄 분류했지만, **사용자 가설** ("destination 에 없으면 wrapper 에 남아있는 것 아닌가") 검증 결과:
  - Category A/B (DocsAgent ghost text · 19 agent listing 등): destination 이 SSOT, wrapper 본문이 stale → 별도 cleanup CFP 영역
  - **Category C (5 lane output contract sibling 부재)**: destination 에 canonical 존재하지만 wrapper sibling 미작성 → **본 CFP 의 범위**
- Codex 가 Category C 를 "wrapper cleanup" 으로 잘못 분류한 부분을 사용자가 정확히 짚어 design intent 를 교정함

## 1. 컨텍스트

### 1.1 ζ arc 의 미해결 P0 gap

CFP-31 (2026-04-29 ζ arc parent design) 이 5 신규 contract 도입을 계획 — `requirements-output-v1`, `design-output-v1`, `develop-output-v1`, `test-verdict-v1`, `pmo-output-v1`. ζ arc 추출 PR 시리즈 (CFP-29 / CFP-36 / CFP-37 / CFP-38 / CFP-39 / CFP-40) 에서 각 lane plugin 의 canonical contract 파일은 작성·머지 완료. 그러나 **wrapper 측 sibling reference 5종 backfill 은 누락** 상태로 ζ arc 가 종료됨 (CFP-41 retrospective).

CFP-41 retro ([docs/retros/2026-04-29-zeta-arc-completion.md](../../retros/2026-04-29-zeta-arc-completion.md)) 가 "Migration-guide BREAKING parity" 는 follow-up cleanup 으로 명시했으나 **sibling backfill 자체는 lessons-learned 에 누락**. ADR-009 본문 §51 에 "Inter-plugin contract 6종 보유" 라고 단언되었지만, 로컬 [docs/inter-plugin-contracts/](../../inter-plugin-contracts/) 실제 파일은 5개 — 그중 3개 (`comment-prefix-registry-v1`, `fix-event-v1`, `label-registry-v1`) 는 **`kind: registry`** (cross-cutting protocol — 별도 schema·별도 lint chain) 이고, 2개 (`review-verdict-v1`, `review-verdict-v2`) 만 **`kind: contract`** (typed inter-plugin schema, [scripts/check-inter-plugin-contracts.sh](../../../scripts/check-inter-plugin-contracts.sh) lint 대상). "6종 contract 보유" 는 사실상 2 contract + 3 registry 의 합산. 본 CFP 의 sibling backfill 범위는 **`kind: contract` 표면만** — 5 lane plugin canonical 을 wrapper sibling 으로 backfill 하면 contract 표면이 2 → 7 로 확장되고 registry 표면은 3 으로 불변.

본 CFP 는 이 누락을 backfill 하면서, 동일 누락이 향후 7번째·8번째 contract 추가 시 재발하지 않도록 ADR-010 정책 + lint 확장으로 차단한다.

### 1.2 review-verdict-v2 가 만든 선례

CFP-35 (review subsystem 으로의 self-write retrofit) 에서 `review-verdict-v2.md` 가 **canonical at codeforge-review repo + sibling at wrapper repo** 패턴을 처음 도입 ([docs/inter-plugin-contracts/review-verdict-v2.md:19-22](../../inter-plugin-contracts/review-verdict-v2.md#L19-L22)):

```
**상위 SSOT 위치**:
- mclayer/plugin-codeforge-review/docs/inter-plugin-contracts/review-verdict-v2.md: canonical (codeforge-review repo)
- 본 file (codeforge wrapper repo): sibling reference (canonical 변경 시 sync 의무 — CFP-24 marketplace sync 정책 유사)
- ADR-001 (review-agent-unification — lane-agnostic worker): codeforge-review repo의 docs/adr/ADR-001 참조
```

본 CFP 는 이 선례를 5 lane output contract 에 일반화 + ADR 로 정책 동결.

### 1.3 Categorization — 사용자 가설 검증 결과

| Category | 항목 | wrapper 상태 | destination 상태 | 본 CFP 범위 |
|---|---|---|---|---|
| A1 | 19 agent .md SSOT 주장 | CLAUDE.md 본문 stale | 6 plugin 에 23 agent 분산 owned | ❌ (별도 CFP) |
| A2 | change-plan/adr template wrapper-local 인용 | wrapper 인용 stale | codeforge-design templates/ canonical | ❌ (별도 CFP) |
| A3 | presets/ wrapper-local 인용 | wrapper 인용 stale | codeforge-develop presets/ canonical | ❌ (이미 분리 인지) |
| B | DocsAgent active writer 묘사 | 100% stale (entity 부재) | 어느 plugin 에도 없음 (의도적 해체) | ❌ (별도 CFP) |
| **C** | **5 lane output contract sibling** | **wrapper sibling 부재** | **destination canonical 존재** | **✅ 본 CFP** |
| D | review_verdict v1 archive | wrapper sibling 잔존 | (review repo 동일) | ❌ (CFP-D 후속, retro:75) |

A/B 카테고리는 본 CFP 직후 별도 dogfooding cleanup CFP 로 분리 처리 (사용자가 그 시점에 별도 의뢰 시 진행).

## 2. 결정 사항 (key decisions)

### 2.1 D1. Backfill 방식 = canonical verbatim mirror + sibling marker 섹션

각 sibling file 본문은 destination canonical 과 verbatim 일치. wrapper sibling 만의 부가 정보는 본문 시작의 "**상위 SSOT 위치**" 섹션 (review-verdict-v2 패턴). 이유:
- Drift 검증 가능성: 미래 lint 또는 CI 가 canonical hash vs sibling hash 비교 가능
- 의미 변경 0: 사용자 명시 ("destination 에 있고 wrapper sibling 이 없는 것")
- ADR-008 versioning 룰 준수: contract 의미는 canonical 이 단독 결정, sibling 은 reference

대안 (D1-Alt): wrapper sibling 에 wrapper-specific commentary 추가 → **반려**. 의미 분기 위험 + drift 검증 어려움.

### 2.2 D2. MANIFEST.yaml = 명시적 contract registry

contract 완결성 검증을 위해 별도 manifest file 도입. 이유:
- ADR-010 본문에 manifest 를 박으면 ADR 변경 = contract 추가 가 되어 ADR 의 immutability 와 충돌
- 별도 yaml 은 lint 가 parse 하기 쉽고, contract 추가 절차가 "ADR 본문 변경 없이 MANIFEST entry 만 추가" 로 단순화
- review-verdict-v1+v2 처럼 동일 contract 의 복수 version 도 자연스럽게 표현

대안 (D2-Alt): ADR-010 frontmatter 에 manifest 박기 → **반려**. ADR 의 결정 vs 상태 데이터 분리 원칙 위배.

### 2.3 D3. MANIFEST 범위 = `kind: contract` 표면만

wrapper repo 의 [docs/inter-plugin-contracts/](../../inter-plugin-contracts/) 디렉터리는 두 종류 파일을 보유:
- **`kind: contract`** — typed inter-plugin schema (lane plugin → core 단방향 verdict/output). [scripts/check-inter-plugin-contracts.sh](../../../scripts/check-inter-plugin-contracts.sh) 가 frontmatter+본문 sanity 검증
- **`kind: registry`** — wrapper-owned cross-cutting protocol (comment prefix · fix-event · label registry). `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` 가 검증

본 CFP 의 MANIFEST.yaml 은 **`kind: contract` 파일만 등록**. 이유:
- 두 kind 는 frontmatter schema 가 다름 (`contract_version` vs `version`, `related_plugins` 필수 vs 부재). 하나의 MANIFEST 에 섞으면 검증 분기 복잡
- 기존 lint chain 분리 모델 유지 (separation of concerns)
- 향후 wrapper-canonical `kind: contract` (예: cross-cutting typed schema 신설) 가 등장하면 그때 role 필드 도입

현재 MANIFEST 등록 6 entries 모두 sibling (lane plugin canonical 의 mirror). `role` 필드는 MANIFEST schema 에서 생략 — 나중 필요 시 ADR 갱신과 함께 추가.

### 2.4 D4. Drift 검출 정책 = 본 CFP 는 manifest completeness 까지

본문 verbatim drift 검출 (canonical SHA vs sibling SHA 비교) 은 후속 CFP 로 분리. 이유:
- GitHub API rate limit 고려 (6 plugin × main branch fetch)
- 본 CFP 의 가치는 "현재 5 누락 즉시 해소 + 향후 누락 차단" 이고 drift 는 부차적
- A2 권장안 채택 (사용자 round 5)

후속 CFP 분리 표면: `.github/workflows/contract-drift-check.yml` + cron + token 정책.

### 2.5 D5. Sync 트리거 = canonical PR merge 직후 wrapper sibling sync PR

CFP-24 marketplace cross-repo sync 정책과 동질:
- canonical 변경 PR merge → 즉시 wrapper sibling sync PR open · merge
- canonical PR body 또는 Story file §11 에 "wrapper sibling sync PR 후속 의무" 명시
- 정식 CI 자동 차단은 후속 CFP (drift detection 과 동일 시점) — 본 CFP 까지는 author 의무

## 3. 산출물 + 책임

### 3.1 신규 파일 (5 sibling + 1 manifest + 1 ADR + 1 spec)

| 파일 | 책임 (Phase 1/2) | Author lane |
|---|---|---|
| [docs/inter-plugin-contracts/requirements-output-v1.md](../../inter-plugin-contracts/requirements-output-v1.md) | Phase 2 | DeveloperPL (mechanical mirror) |
| [docs/inter-plugin-contracts/design-output-v1.md](../../inter-plugin-contracts/design-output-v1.md) | Phase 2 | DeveloperPL |
| [docs/inter-plugin-contracts/develop-output-v1.md](../../inter-plugin-contracts/develop-output-v1.md) | Phase 2 | DeveloperPL |
| [docs/inter-plugin-contracts/test-verdict-v1.md](../../inter-plugin-contracts/test-verdict-v1.md) | Phase 2 | DeveloperPL |
| [docs/inter-plugin-contracts/pmo-output-v1.md](../../inter-plugin-contracts/pmo-output-v1.md) | Phase 2 | DeveloperPL |
| [docs/inter-plugin-contracts/MANIFEST.yaml](../../inter-plugin-contracts/MANIFEST.yaml) | Phase 2 | DeveloperPL |
| [docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md](../../adr/ADR-010-inter-plugin-contract-sibling-sync.md) | Phase 1 | ArchitectAgent (chief author) |
| 본 spec (현재 파일) | brainstorming 산출물 (이미 작성) | Claude (Orchestrator) |

### 3.2 수정 파일

| 파일 | Phase | 변경 |
|---|---|---|
| [scripts/check-inter-plugin-contracts.sh](../../../scripts/check-inter-plugin-contracts.sh) | Phase 2 | manifest completeness + orphan + frontmatter schema + sibling marker 검증 추가 |
| [CLAUDE.md](../../../CLAUDE.md) | Phase 2 | "Inter-plugin Contract" 섹션 — kind:contract 6 / kind:registry 3 분리 listing + ADR-010 참조 |
| `docs/stories/CFP-42.md` (생성 예정 — story-init.yml Action) | Phase 1 + Phase 2 | Issue Form → story-init.yml 자동 §1 + 수동 §2-11 |
| [docs/change-plans/cfp-42-inter-plugin-contract-sibling-backfill.md](../../change-plans/cfp-42-inter-plugin-contract-sibling-backfill.md) | Phase 1 | Phase 1 PR ArchitectAgent 산출물 |
| [docs/inter-plugin-contracts/review-verdict-v1.md](../../inter-plugin-contracts/review-verdict-v1.md) | Phase 2 | frontmatter `related_adrs` 에 ADR-010 추가 (sibling marker 강제 통과) |
| [docs/inter-plugin-contracts/review-verdict-v2.md](../../inter-plugin-contracts/review-verdict-v2.md) | Phase 2 | frontmatter `related_adrs` 에 ADR-010 추가 (sibling marker 강제 통과) |
| [scripts/test-check-inter-plugin-contracts.sh](../../../scripts/test-check-inter-plugin-contracts.sh) | Phase 2 | NEW — lint 회귀 테스트 harness (T1-T6 시나리오) |

## 4. ADR-010 핵심 내용 (Phase 1 ArchitectAgent draft 입력)

### 4.1 결정

- **Canonical 위치 룰**: contract 의 producer plugin (해당 contract 가 산출되는 lane plugin) 의 `docs/inter-plugin-contracts/<contract-name>-v<N>.md`. wrapper 자체가 producer 인 cross-cutting protocol 은 wrapper 자체가 canonical
- **Sibling 위치 룰**: codeforge wrapper 의 `docs/inter-plugin-contracts/` (consumer 1차 진입점). canonical 인 contract 도 동일 디렉터리 (role 만 frontmatter 로 구분)
- **Sync 트리거**: canonical 변경 PR merge 직후 wrapper sibling sync PR open·merge 의무 (CFP-24 marketplace sync 정책 동질). canonical PR body 에 후속 의무 명시
- **Drift 검출**: 본 ADR 시점은 manifest completeness + frontmatter schema lint 까지. 본문 verbatim drift 검출은 후속 ADR 에서 결정

### 4.2 결과

- 새 contract 추가 절차: ① lane plugin canonical 작성 (ADR-008 versioning 준수) ② wrapper MANIFEST.yaml entry 추가 ③ wrapper sibling file 작성 ④ ADR-010 본문 불변, MANIFEST 만 갱신
- 새 contract 제거 절차 (drop 또는 plugin 추출): ① lane plugin canonical 보존 ② wrapper MANIFEST role 변경 또는 entry 제거 ③ sibling file deprecate 또는 삭제
- ADR-008 versioning 과의 관계: 본 ADR 은 sync 정책, ADR-008 은 contract 자체 versioning 룰. 두 ADR 모두 frontmatter `related_adrs` 에 함께 인용 의무

### 4.3 위배 시 처리

- lint FAIL: PR merge 차단
- canonical 변경 후 sibling sync PR 누락: 다음 wrapper PR 가 lint manifest mismatch 로 차단됨 (간접 강제)
- 후속 CFP 에서 drift detection workflow 도입 시 직접 강제 가능

## 5. MANIFEST.yaml schema

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
      - { file: review-verdict-v1.md, contract_version: "1.0", status: Archived }
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

**검증 의미**:
- `contracts[].name`: snake_case identifier
- `contracts[].canonical_repo`: GitHub `<org>/<repo>` 형식
- `contracts[].canonical_path`: canonical file 의 destination repo 내 디렉터리 (slash 종결)
- `contracts[].files[].file`: `docs/inter-plugin-contracts/` 내 파일명 (basename)
- `contracts[].files[].contract_version`: ADR-008 SemVer (major.minor)
- `contracts[].files[].status ∈ {Active, Deprecated, Archived}` (Archived 는 CFP-D 시점 추가)

**Total**: 6 entry / 7 file (review_verdict 가 v1+v2 두 파일 보유, 나머지 5 entry 는 각 1 file).

## 6. Sibling file 형식

[docs/inter-plugin-contracts/review-verdict-v2.md:1-22](../../inter-plugin-contracts/review-verdict-v2.md#L1-L22) 패턴 적용. 5 신규 sibling file 모두 다음 구조:

```markdown
---
kind: contract
contract_version: "1.0"
status: Active
related_plugins:
  - codeforge (wrapper, consumer)
  - codeforge-<lane> (canonical owner, producer)
related_adrs:
  - ADR-008 (Inter-plugin Contract Versioning)
  - ADR-010 (Inter-plugin Contract Sibling Sync — sync 정책)
authors:
  - CFP-42 sibling backfill (2026-04-29) — wrapper sibling 첫 작성, canonical 본문 verbatim mirror
---

# <contract_name> v<N> — Inter-plugin Contract

`codeforge-<lane>` plugin → `codeforge` core (Orchestrator) 단방향 schema.

**상위 SSOT 위치**:
- `mclayer/plugin-codeforge-<lane>/docs/inter-plugin-contracts/<contract-name>-v<N>.md`: **canonical**
- 본 file (codeforge wrapper repo): sibling reference (canonical 변경 시 sync 의무 — ADR-010 + CFP-24 marketplace sync 정책 동질)
- ADR-008 (versioning 룰): codeforge wrapper repo `docs/adr/ADR-008-inter-plugin-contract-versioning.md`

[... canonical 본문 verbatim mirror ...]
```

**Phase 2 PR 작성 절차** (DeveloperPL):
1. `gh api repos/mclayer/plugin-codeforge-<lane>/contents/docs/inter-plugin-contracts/<contract>-v1.md` 또는 mcp__github__get_file_contents 로 raw fetch
2. canonical 본문 verbatim 보존 + 위 frontmatter + "상위 SSOT 위치" 섹션을 wrapper-specific prefix 로 prepend
3. lint 통과 확인 후 commit

## 7. Lint 확장 (`scripts/check-inter-plugin-contracts.sh`)

기존 검사 (frontmatter/body sanity) 유지 + 신규 4종 추가:

### 7.1 Manifest completeness (positive)

```
For each entry in MANIFEST.yaml.contracts[].files[]:
  IF NOT EXISTS docs/inter-plugin-contracts/<entry.file>:
    FAIL "manifest entry <name> v<version> missing sibling file <file>"
```

### 7.2 Orphan 차단 (negative)

```
For each *.md in docs/inter-plugin-contracts/ (excluding MANIFEST.yaml + readme/index):
  Read frontmatter
  IF kind == "contract":
    IF NOT registered in any MANIFEST.yaml.contracts[].files[]:
      FAIL "orphan kind:contract file <file> not registered in MANIFEST.yaml"
  # kind:registry files: skip (managed by other lint chain)
```

### 7.3 Frontmatter schema (sibling — ADR-010 reference)

```
For each kind:contract file (existing check-inter-plugin-contracts 가 kind/version/status/related_plugins/related_adrs/authors 검증중):
  ADD: Required: related_adrs (string-cast 후) ∋ "ADR-008"
  ADD: Required: related_adrs (string-cast 후) ∋ "ADR-010"
       (현재 MANIFEST 등록 6 entry 모두 sibling. 향후 wrapper-canonical kind:contract 추가 시 분기 도입)
```

### 7.4 Sibling marker

```
For each kind:contract file (현재 MANIFEST 의 모든 entry — 모두 sibling):
  Required: 본문에 "상위 SSOT 위치" 헤딩 또는 동등 마커 (regex: /\*\*상위 SSOT 위치\*\*:/) 존재
```

### 7.5 실행 통합

- 기존 lint script 의 main 진입점에 위 4 검사 chain
- exit code: 위배 시 non-zero (CI block)
- consumer-facing 사용 표면 변화 없음 (script 인터페이스 동일)

## 8. Test contract preview (Story §8 입력)

| ID | Type | Setup | Expected |
|---|---|---|---|
| T1 | functional negative | sibling file 1개 임시 삭제 | lint exit 1 + "manifest entry ... missing sibling/canonical file" 메시지 |
| T2 | functional negative | MANIFEST 미등록 신규 .md 추가 | lint exit 1 + "orphan contract file ... not registered" |
| T3 | functional negative | 기존 sibling 의 frontmatter 에서 `related_adrs` 제거 | lint exit 1 + "missing required frontmatter field" |
| T4 | functional negative | sibling file 의 "상위 SSOT 위치" 섹션 제거 | lint exit 1 + "sibling marker section missing" |
| T5 | functional positive | 정합 상태 (모든 7 sibling file + 6 MANIFEST entry × 본문 정상) | lint exit 0 |
| T6 | functional positive (regression) | 기존 review-verdict v1+v2 (frontmatter 에 ADR-010 추가 후) + 3 kind:registry 파일은 본 lint 무시 | lint exit 0 |
| Performance | N/A | 순수 shell lint, baseline 무관 | — |

## 9. Phase 1 / Phase 2 PR split

### 9.1 Phase 1 PR — 요구사항 + 설계 + 설계리뷰 lane

**Files**:
- `docs/stories/CFP-42.md` (story-init.yml Action 자동 §1 + 수동 §2-7)
- `docs/change-plans/cfp-42-inter-plugin-contract-sibling-backfill.md` (ArchitectAgent chief author)
- `docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md` (ArchitectAgent direct write — CFP-26 Phase 0a 권한)

**Lane 흐름**:
- Issue Form (story.yml) 제출 → story-init.yml Action 자동 KEY 할당 + Phase 1 PR open + §1 verbatim
- Requirements lane: 본 spec § 0 사용자 원문 + § 1 컨텍스트 → §2-6 채움
  - DomainAgent: contract 도메인 (Inter-plugin schema 진화) — 사실상 §0/§1 에 충분히 정의됨, "null 결과" 가능
  - RequirementsAnalyst: 모호 항목 — drift 검출 향후 분리, sync PR 자동화 향후 분리 (이미 본 spec §2.4·§2.5 에 명시)
  - Researcher: 외부 선례 — review-verdict-v2 (내부) + CFP-24 marketplace sync (내부). 외부 web 조사 가치 낮음
- Design lane: ArchitectPL 5 deputy 병렬
  - CodebaseMapper: 기존 review-verdict-v2 + 5 lane plugin canonical 파일 분석
  - Refactor: lint script 구조 (manifest completeness 추가의 영향 범위)
  - SecurityArchitect: 본문 verbatim mirror 의 supply-chain 영향 (canonical repo 가 손상되면 sibling 도 손상 — 다만 wrapper-only 모델에서 sibling 은 reference 라 직접 실행 영향 없음)
  - TestContractArchitect: §8 Test contract 6 케이스 author input
  - DataMigrationArchitect: schema 변경 없음 — "null 결과" valid
- ArchitectAgent (chief author): Change Plan §1-§11 + ADR-010 작성
- DesignReviewPL: ADR-008/ADR-009/ADR-010 정합성 + Change Plan 완결성 + §7 보안 설계 (verbatim mirror 의 trust boundary) + §11 데이터 마이그레이션 N/A 사유

**Gate**: `gate:design-review-pass` 부착 → Phase 1 PR mergeable → merge

### 9.2 Phase 2 PR — 구현 + 구현리뷰 + 구현테스트 + 보안테스트 lane

**Files**:
- 5 sibling file (각 destination canonical 의 verbatim mirror + frontmatter + 상위 SSOT 위치 섹션)
- `docs/inter-plugin-contracts/MANIFEST.yaml`
- `scripts/check-inter-plugin-contracts.sh` (확장)
- `CLAUDE.md` "Inter-plugin Contract" 섹션 (6 kind:contract listing + 3 kind:registry 분리 명시 + ADR-010 인용)
- `docs/stories/CFP-42.md` §8-11 append (Test Contract + Impl Manifest + 리뷰 결과 + FIX Ledger)

**Lane 흐름**:
- DeveloperPL: role:dev roster discovery → DeveloperAgent 단독 충분 (DataEng·InfraEng 적용 경로 없음)
- QADev: §8 6 케이스 테스트 코드 (shell test harness 사용 — 기존 `scripts/check-*.sh` test 패턴 따름)
- CodeReviewPL: lint 확장 코드 품질 + sibling file 본문 verbatim 일치성 spot-check
- TestAgent: shell lint 실행 (기능 테스트). 성능 테스트 N/A
- SecurityTestPL: 1차 layer (Dependabot/CodeQL/Secret Scanning) + 2차 layer (Claude/Codex). 본 PR 은 새 의존성 0, 새 외부 입력 0 → injection / credential / CVE 표면 변경 없음

**Gate**: `gate:security-test-pass` 부착 → Phase 2 PR mergeable → merge → Story Issue 자동 close

## 10. Out of scope (본 CFP 비대상)

| 항목 | 분리 사유 | 후속 CFP 후보 |
|---|---|---|
| Category A1/A2/A3 (DocsAgent ghost text · agent listing · template/preset stale) | 의미 변경 (wrapper SSOT 본문 정리), Category C 와 독립 | CFP-A (Codex 분석 §5.1 후보) |
| Category B (DocsAgent active writer 묘사) | A 와 동일 cleanup 성격 | CFP-A 통합 가능 |
| Category D (review-verdict-v1 archive) | retro:75 후속 | CFP-D (Codex §5.4) |
| Canonical ↔ sibling 본문 verbatim drift detection (GitHub Actions) | A2 권장안 채택 (사용자 round 5) | 별도 후속 CFP — A3 영역 |
| Canonical PR merge 후 wrapper sibling sync PR auto-open (CI 자동화) | 본 CFP 는 author 의무까지. 자동화는 drift detection 과 동일 시점 | drift detection CFP 동시 |
| Migration guide v0.22 → v5 BREAKING parity backfill | retro:77 follow-up | CFP-E (Codex §5.5) |

## 11. Open questions / risks

### 11.1 Question — Manifest 위치

**Q**: `MANIFEST.yaml` 을 `docs/inter-plugin-contracts/MANIFEST.yaml` 에 둘 것인가, 아니면 `.claude-plugin/inter-plugin-contracts.yaml` 처럼 manifest 디렉터리에 둘 것인가?

**현재 결정**: `docs/inter-plugin-contracts/MANIFEST.yaml` — contract 디렉터리 내부에 두면 lint 가 같은 dir scan 으로 찾기 쉬움. ADR-010 본문에서 위치 SSOT.

**Open**: ArchitectPL 가 Phase 1 설계 리뷰에서 위치 변경 제안 가능. 변경 시 본 spec §3·§5·§7 의 path reference 갱신 필요.

### 11.2 Risk — canonical 본문 변경 누락

**Risk**: lane plugin 측 canonical 변경 후 wrapper sibling sync PR 을 누락하는 author 실수.

**Mitigation (본 CFP)**: ADR-010 §4.3 "위배 시 처리" — 다음 wrapper PR 가 lint manifest mismatch 로 차단 (간접 강제).

**Residual**: lint 는 file 존재 여부만 검사하고 본문 drift 는 검출 못 함. canonical 만 변경되고 sibling 은 옛날 본문이어도 lint pass. → 후속 drift detection CFP 에서 정식 차단.

### 11.3 Risk — 6번째 lane plugin 추출 시 sibling 누락 재발

**Risk**: 본 CFP 가 종료되어도 미래의 7번째·8번째 contract 추가 시 동일 누락 가능.

**Mitigation**: ADR-010 본문에 "신규 contract 추가 4단계 절차" 명시 + lint manifest completeness 가 sibling file 부재 즉시 차단. 절차 명시 + 자동 차단의 이중 안전망.

### 11.4 Risk — sibling 본문이 canonical 의 일부만 mirror

**Risk**: Phase 2 PR 시 5 sibling 작성자 (DeveloperAgent) 가 canonical 의 일부 섹션만 미러링하고 누락.

**Mitigation**: §8 T6 (regression positive) 가 기존 review-verdict v2 패턴과 비교. 추가로 Phase 2 CodeReviewPL 이 sibling vs canonical raw 본문 diff spot-check 의무 (Change Plan §6 에 포함).

## 12. 참조

### 12.1 ADR

- [ADR-008 Inter-plugin Contract Versioning](../../adr/ADR-008-inter-plugin-contract-versioning.md) — versioning SemVer 룰 (모든 contract 표면)
- [ADR-009 Wrapper-only Decomposition](../../adr/ADR-009-wrapper-only-decomposition.md) — ζ arc 결과. 본 CFP 가 추격하는 P0 gap 의 출처
- ADR-010 (NEW, Phase 1 author) — 본 CFP 결정 ADR

### 12.2 관련 CFP

- [CFP-24 Marketplace cross-repo sync rule](2026-04-28-cfp-24-marketplace-cross-repo-sync-rule-design.md) — sync 정책 동질 패턴 출처
- [CFP-29 codeforge-review extraction](2026-04-28-cfp-29-codeforge-review-extraction-design.md) — review-verdict v1 first contract
- [CFP-31 ζ arc parent design](2026-04-29-cfp-31-wrapper-only-decomposition-design.md) — 5 lane output contract 도입 계획. 본 CFP 가 그 계획의 wrapper sibling 부분 backfill
- CFP-35 review-verdict v2 retrofit — sibling 패턴 첫 도입 선례
- CFP-41 ζ arc retro — sibling backfill 누락이 lessons-learned 에 잡히지 않은 origin

### 12.3 기존 sibling 선례

- [docs/inter-plugin-contracts/review-verdict-v2.md](../../inter-plugin-contracts/review-verdict-v2.md) — 본 CFP 가 일반화하는 pattern 출처

### 12.4 Destination canonical (Phase 2 mirror source)

- mclayer/plugin-codeforge-requirements `docs/inter-plugin-contracts/requirements-output-v1.md` (5124 bytes)
- mclayer/plugin-codeforge-design `docs/inter-plugin-contracts/design-output-v1.md` (4957 bytes)
- mclayer/plugin-codeforge-develop `docs/inter-plugin-contracts/develop-output-v1.md` (4075 bytes)
- mclayer/plugin-codeforge-test `docs/inter-plugin-contracts/test-verdict-v1.md` (4816 bytes)
- mclayer/plugin-codeforge-pmo `docs/inter-plugin-contracts/pmo-output-v1.md` (4678 bytes)

### 12.5 Codex 분석 (간접 입력)

본 spec 작성 직전 codex-rescue 로 받은 wrapper-only 정합성 분석. Category C 식별의 대부분 출처. 단 Codex 는 Category C 를 "wrapper cleanup 필요" 로 잘못 분류했고, 사용자가 그 분류를 교정 ("이 레포에 다른 문서 내용이 남아있다는 것은 필요한 repo에 해당 내용이 없다는걸 의미하지 않나"). 본 CFP 의 design intent 는 사용자 교정 후의 정확한 분류에 기반.
