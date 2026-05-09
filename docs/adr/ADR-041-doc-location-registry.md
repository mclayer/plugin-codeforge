---
adr_number: 41
title: Doc Location Registry — codeforge plugin doc taxonomy 통합 SSOT
date: 2026-05-08
status: Proposed
category: Team & Process
carrier_story: CFP-276
supersedes:
  - ADR-002
superseded_by: null
related_files:
  - docs/doc-locations.yaml
  - docs/doc-location-registry.md
  - scripts/check-doc-locations.sh
  - scripts/test-check-doc-locations.sh
  - .github/workflows/doc-locations-check.yml
---

# ADR-041: Doc Location Registry — codeforge plugin doc taxonomy 통합 SSOT

## 상태

Proposed (2026-05-08, CFP-276 — issue #276 carrier).

## 컨텍스트

[Issue #276](https://github.com/mclayer/plugin-codeforge/issues/276) 에서 EPIC-RESULTS-`<KEY>`.md 위치가 3 SSOT 문서에서 모순:
- `templates/epic-results.md:16` — "Epic owner repo root **또는** hub repo root" (OR)
- `docs/orchestrator-playbook.md:436` — "Epic owner repo root" (owner only)
- `templates/story-page-structure.md:350` — `[EPIC-RESULTS-<EPIC_KEY>.md](../../EPIC-RESULTS-<EPIC_KEY>.md)` (root 가정)

추가 인지 drift 위험: codeforge dogfood (`<internal-docs>/<plugin-folder>/retros/`) 가 ADR-013 logical 결과이지만 SSOT 미문서화. mctrader (consumer) 는 12 file 이 3 위치 (root / docs/ / docs/results/) 분산.

사용자 요구: "이 문서 규약은 codeforge 의 업그레이드로 인해 변경될 때마다 반영될 수 있도록 하자" — single yaml row 갱신만으로 doc location 정책 갱신 가능한 mechanism.

ADR-002 ("DocsAgent inherit footer pattern", 2026-04-27) 는 [ADR-009](ADR-009-wrapper-only-decomposition.md) (wrapper 0-agent, 2026-04-29) 이후 referenced agent files 전부 부재 → zombie ADR. 본 결정 채택 시 ADR-002 → Superseded by ADR-041.

## 결정

### 결정 1: 단일 yaml SSOT + auto-generated markdown

`docs/doc-locations.yaml` (machine-readable, 10 doc_type entries 1차 등록) + `docs/doc-location-registry.md` (auto-generated from yaml). 다른 모든 SSOT 문서는 1줄 참조.

10 entries (1차): `epic_results`, `story_file`, `adr`, `change_plan`, `retro`, `domain_knowledge`, `spec`, `plan`, `decision_packet`, `inter_plugin_contract`.

향후 추가 후보 (별도 CFP follow-up — yaml row 추가만으로 처리): `hotfix_playbook`, `consumer_guide`, `orchestrator_playbook`.

### 결정 2: EPIC-RESULTS canonical location

Phase N+1 close PR repo root. ADR-020 Mode A → owner / Mode B/C → hub. ADR-013 codeforge family override → `<internal-docs>/<plugin-folder>/retros/`. EPIC-RESULTS = retro-like artifact (Codex round 1 verdict, gpt-5.5 high).

### 결정 3: Lint + CI fail-closed

`scripts/check-doc-locations.sh` 6 validation + `--regen` + `--check-freshness` + `--full` modes (총 [7/7] freshness 포함). `.github/workflows/doc-locations-check.yml` = branch protection required check (5번째).

검증 항목:
1. Top-level shape (schema_version / allowed_variants / allowed_placeholders / dogfood_scope / doc_types)
2. Per-doc-type required fields (name / variants / owner_agent / introduced_by)
3. Variant key allowlist
4. Placeholder allowlist
5. No absolute paths
6. Doc_type name uniqueness
7. Markdown freshness (round-trip diff)

### 결정 4: 4-layer enforcement

1. **DesignReview lane checklist** (codeforge-review templates) — 새 doc artifact 도입 시 yaml row 갱신 의무
2. **ADR template** (templates/adr.md) — frontmatter 또는 본문에 1줄: `**Doc location impact**: 없음 / doc-locations.yaml <doc_type> row 갱신 (PR commit X)`
3. **CI lint** (Phase 1 PR 시) — branch protection required check
4. **Pre-commit hook** (선택)

### 결정 5: Schema versioning (registry 자체)

- Field 추가 (backward compat) → MINOR (1.0 → 1.1)
- Field 제거 / 의미 변경 → MAJOR (1.x → 2.0)
- Row 추가/수정 (정상 운영) → bump 없음 (`last_updated` 만)

[ADR-037](ADR-037-plugin-version-bump-rule.md) plugin version bump rule 과 별도 주기.

### 결정 6: Codeforge upgrade reflection trigger 5종

| # | Upgrade 종류 | Yaml 변경 | ADR 의무 |
|---|---|---|---|
| 1 | 새 doc type 도입 | `doc_types[]` row 추가 | ADR-NNN 가 yaml row 추가 commit 동반 |
| 2 | 기존 doc location 변경 | row 의 variants 갱신 | ADR amendment + migration 가이드 |
| 3 | 새 mode 추가 (ADR-020 amendment) | `allowed_variants[]` 추가 + 영향 row 갱신 | ADR-020 Amendment + ADR-041 cross-ref |
| 4 | doc type deprecate | row 의 `status: Deprecated` field | ADR-NNN deprecate 명시 |
| 5 | 새 lane plugin (ADR-023) | `dogfood_scope.plugin_folders[]` 추가 | ADR-023 lifecycle 절차 + ADR-041 minor cross-ref |

## 결과

### 긍정
- Issue #276 SSOT 모순 3건 해소
- codeforge upgrade 마다 yaml row 1줄 갱신 + regen 1회 = 자연스러운 evolution mechanism
- ADR-002 zombie 정리

### 부정 / 트레이드오프
- yaml + generated md = 2 file. drift 가능성 → CI freshness check 가 강제
- 신규 ADR 작성 시 doc location impact 1줄 의무 (인지 부하 ↑)

## 거부된 대안

| 대안 | 기각 사유 |
|------|----------|
| Markdown table only | parser 고장 위험, machine-readable 손실 |
| Inter-plugin contract 식 registry | semantic mismatch — doc location 은 wrapper-only 관심 |
| DocsAgent 부활 | ADR-009 wrapper 0-agent invariant 위반, 사용자 명시 거부 |
| EPIC-RESULTS Phase N+1 close PR repo root 외 4 옵션 | Codex round 1 (gpt-5.5 high) verdict — superior 옵션 없음 |
| `mode_*` 고정 field schema | Mode D/E 추가 시 schema breaking. Codex round 2 권고로 generic `variants: { key: path }` 채택 |

## Codex 검토 round (2회)

- **Round 1** (gpt-5.5 high, EPIC-RESULTS canonical): Option 1 (Phase N+1 close PR repo root + ADR-013 dogfood override) verdict 채택. mctrader 12 file 중 5 file mechanical move guidance.
- **Round 2** (gpt-5.5 high, YAML schema): generic `variants: { key: path }` + angle-bracket placeholder + dogfood scope as data + 10 entries (consumer-guide / decision-packet / inter-plugin-contracts / hotfix-playbook 포함) + hybrid markdown + lint 7 validation. 모든 7 권고 채택.

## Migration

### plugin-codeforge (Phase 1 PR — 본 ADR 동반)

3 SSOT 문서 1줄 참조화 + ADR-002 supersede + ADR-013 Amendment 2 + ADR-020 cross-ref. 상세 [`wrapper/specs/2026-05-08-issue-276-doc-location-registry-design.md`](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-05-08-issue-276-doc-location-registry-design.md) §5.

### consumer (mctrader, follow-up Phase 2 PR — 별도 issue)

12 file 중 7 no-op (이미 root) + 5 mechanical move:

```
mctrader-hub/docs/EPIC-RESULTS-MCT-{48,55,63,70}.md → mctrader-hub/EPIC-RESULTS-MCT-{48,55,63,70}.md
mctrader-hub/docs/results/EPIC-RESULTS-MCT-89.md → mctrader-hub/EPIC-RESULTS-MCT-89.md
```

추가 작업:
- inbound link scan (`grep -rn "docs/EPIC-RESULTS\|docs/results/EPIC-RESULTS"` mctrader-hub 전체)
- 빈 디렉터리 정리: `mctrader-hub/docs/results/` 삭제
- PR description 에 ADR-041 링크 + "Mode B 정합" 명시

## 다이어그램

```
codeforge upgrade (e.g., 새 doc type 도입)
   │
   ▼
docs/doc-locations.yaml (row 추가)
   │
   ▼ ($ ./scripts/check-doc-locations.sh --regen)
docs/doc-location-registry.md (auto-regenerated)
   │
   ▼ (CI lint pass)
3 SSOT 문서 (epic-results.md / orchestrator-playbook.md / story-page-structure.md)
   = 1줄 참조 ("위치: docs/doc-locations.yaml <doc_type> row")
```

## 관련 파일

- [`docs/doc-locations.yaml`](../doc-locations.yaml) — machine SSOT
- [`docs/doc-location-registry.md`](../doc-location-registry.md) — generated
- [`scripts/check-doc-locations.sh`](../../scripts/check-doc-locations.sh) — lint
- [`scripts/test-check-doc-locations.sh`](../../scripts/test-check-doc-locations.sh) — TDD harness
- [`.github/workflows/doc-locations-check.yml`](../../.github/workflows/doc-locations-check.yml) — CI

## 관련 ADR

- [ADR-002](ADR-002-docsagent-inherit-footer-pattern.md) — Superseded by 본 ADR (zombie 정리)
- [ADR-009](ADR-009-wrapper-only-decomposition.md) — wrapper 0-agent invariant
- [ADR-013](ADR-013-codeforge-family-dogfood-out-policy.md) — Amendment 2 (EPIC-RESULTS classification)
- [ADR-017](ADR-017-skill-override-path-enforcement.md) — spec/plan dogfood path enforcement
- [ADR-020](ADR-020-cross-repo-epic-pattern.md) — cross-repo Epic Mode A/B/C
- [ADR-023](ADR-023-lane-plugin-lifecycle.md) — 새 lane plugin → dogfood_scope 갱신 trigger
- [ADR-037](ADR-037-plugin-version-bump-rule.md) — plugin version bump rule (yaml schema_version 과 별도 주기)

---

## Amendment 1 (2026-05-09) — CFP-288 — EPIC-RESULTS mode_a/b/c → `<scope>/docs/retros/` (consumer root clutter 해소)

### 컨텍스트

[Issue #288](https://github.com/mclayer/plugin-codeforge/issues/288) — ADR-041 채택 (2026-05-08) 후 mctrader-hub PR #175 (Phase 2 consumer migration, 2026-05-09 02:36Z) merge 1시간 후 사용자 평가:

> "루트가 너무 더러운데"

검증: mctrader-hub root 17 entries 중 13 (76%) 가 `EPIC-RESULTS-MCT-*.md`. README/docs/out/scripts 4 항목만 non-EPIC. Epic 누적 시 비율 악화.

추가로 ADR-041 채택안의 의도치 않은 비대칭 식별:
- **dogfood**: `<internal-docs>/<plugin>/retros/EPIC-RESULTS-<KEY>.md` (subdir)
- **consumer mode_a/b/c**: `<scope>/EPIC-RESULTS-<KEY>.md` (root)
- registry §epic_results notes: "EPIC-RESULTS = retro-like artifact"

dogfood ↔ consumer 의 path 패턴이 의미적 정합과 맞지 않음 (둘 다 retro-like artifact 인데 위치 룰 다름).

Codex round 3 (gpt-5.5 high) 검토 verdict (Q1-Q7 7/7 ADOPT): `<scope>/docs/retros/` 가 best — registry consistency, root clutter 해소, dogfood 패턴 대칭, naming collision 무. 1일 후 amendment 는 "구체적 consumer evidence 기반 합리적 iteration".

### 결정

`epic_results` row 의 mode_a/b/c variant 를 `<scope>/EPIC-RESULTS-<KEY>.md` 에서 `<scope>/docs/retros/EPIC-RESULTS-<KEY>.md` 로 갱신. dogfood variant 는 변경 없음 (이미 `<plugin>/retros/`).

| 변종 | 변경 전 | 변경 후 |
|---|---|---|
| mode_a | `<owner-repo>/EPIC-RESULTS-<KEY>.md` | `<owner-repo>/docs/retros/EPIC-RESULTS-<KEY>.md` |
| mode_b | `<hub-repo>/EPIC-RESULTS-<KEY>.md` | `<hub-repo>/docs/retros/EPIC-RESULTS-<KEY>.md` |
| mode_c | `<hub-repo>/EPIC-RESULTS-<KEY>.md` | `<hub-repo>/docs/retros/EPIC-RESULTS-<KEY>.md` |
| dogfood | `<internal-docs>/<plugin>/retros/EPIC-RESULTS-<KEY>.md` | (변경 없음) |

§결정 2 의 표현은 "Phase N+1 close PR 이 merge 되는 repo 의 `docs/retros/`" 로 갱신 (root → docs/retros/). dogfood override 별도 문구는 자연스럽게 흡수 — mode_a/b/c + dogfood 모두 `<scope>/[docs/]retros/` 단일 패턴.

§8.1 표 의 Option 1 verdict 는 1일 운영 후 consumer evidence 로 invalidate. Option 4 (collocation) 의 "root 종합 artifact 관습 깨짐" 우려는 docs/retros/ 가 retro doc type 과 의미적 sibling 이므로 해소 (Story file collocation 과 다름).

### 결과

#### 긍정
- Consumer root clutter 해소 (mctrader 13 file → docs/retros/ 이동)
- dogfood ↔ consumer 패턴 대칭 (`<scope>/[docs/]retros/` 단일 룰)
- retro doc type ↔ epic_results 동일 디렉터리 (의미적 정합)
- "단일 grep target" 보존 — `docs/retros/EPIC-RESULTS-*.md` 한 패턴

#### 부정 / 트레이드오프
- Codex round 1 verdict (2026-05-08) 1일 후 번복 — process 측면 빠른 iteration
- mctrader-hub Phase 2 PR (#175) 작업의 역방향 PR 필요 — 13 file root → docs/retros/

### Migration

#### plugin-codeforge (본 PR — CFP-288)
- doc-locations.yaml `epic_results` row mode_a/b/c paths 갱신 + last_updated: 2026-05-09
- doc-locations.yaml `retro` row notes 갱신 (collision 명시 + Amendment 1 cross-ref)
- doc-location-registry.md regenerate (auto-generated round-trip)
- 본 ADR-041 Amendment 1 block (이 섹션)

#### consumer (mctrader-hub follow-up PR)
13 file root → docs/retros/ + inbound link 재갱신:

```
mctrader-hub/EPIC-RESULTS-MCT-{12,18,25,32,37,48,55,63,70,89,90,97,98}.md
   → mctrader-hub/docs/retros/EPIC-RESULTS-MCT-{...}.md
```

추가:
- `docs/retros/` 디렉터리 신설
- inbound link 재갱신 — PR #175 의 12 link 가 `EPIC-RESULTS-<KEY>.md` (root) 로 갱신되어 있으므로 다시 `docs/retros/EPIC-RESULTS-<KEY>.md` 로 갱신
- PR description 에 ADR-041 Amendment 1 link + "consumer root clutter 해소" 명시

### Codex 검토 round 3 (Amendment 1)

gpt-5.5 high. 7 decision points (Q1-Q7) 모두 ADOPT:
- Q1: docs/retros/ best subdir (registry consistency, dogfood 대칭)
- Q2: mode_a/b/c uniform (split 시 root clutter 잔존)
- Q3: 명명 충돌 우려 무 (`EPIC-RESULTS-*.md` vs `<sprint>.md` 명확히 구분)
- Q4: §결정 2 표현 갱신 — `<scope>/docs/retros/`, dogfood 별도 override 불요
- Q5: rapid iteration 합리적 (구체적 consumer evidence 기반)
- Q6: 50+ file 시 docs/retros/ partition 별도 CFP 후보 (이번 scope 외)
- Q7: amendment = right call, 더 나은 third option 무
