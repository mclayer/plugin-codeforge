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
