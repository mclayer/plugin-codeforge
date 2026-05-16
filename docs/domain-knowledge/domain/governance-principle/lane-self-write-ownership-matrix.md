---
title: Lane Self-Write Ownership Matrix
category: governance-principle
introduced_by: CFP-722
date: 2026-05-16
yaml_ssot: lane-self-write-ownership-matrix.yaml
skill_mirror: skills/lane-self-write-boundary/SKILL.md
---

# Lane Self-Write Ownership Matrix

> **SSOT**: `lane-self-write-ownership-matrix.yaml` (same directory). 본 문서는 yaml SSOT 의 human-readable 해설.
> **Drift-sync**: yaml ↔ SKILL.md ↔ `templates/story-page-structure.md` headings ↔ `scripts/lib/check_story_section_ownership.py` regex. 3-way sync-check = follow-up CFP (Change Plan §13.B).

## 목적

Story file 의 per-section 소유권을 기계 판독 가능한 형태로 기록. 두 용도로 소비됨:

1. **소유권 lookup** (skill `codeforge:lane-self-write-boundary`): Orchestrator 가 lane 진입 직전 소유 영역 확인
2. **heading enumeration** (`scripts/lib/check_story_section_ownership.py`): lint 가 section regex pattern 을 yaml SSOT 에서 유도

## 소유권 분류

### Lane-owned sections (INV-DI-1 적용)

| 섹션 | 제목 | 소유 lane |
|---|---|---|
| §2 | 도메인 컨텍스트 | RequirementsPL |
| §3 | ADR 결정 매트릭스 | ArchitectAgent / DesignLane |
| §4, §4.0-§4.3 | 요구사항 분석 | RequirementsPL |
| §5 | 요구사항 확장 해석 | RequirementsPL |
| §6 | 외부 지식 | RequirementsPL |
| §7 | 설계 서사 | ArchitectAgent / DesignLane |
| §8, §8.5 | 개발 서사 / Impl Manifest | DeveloperPL |
| §9 | 리뷰 결과 | 각 Review PL (§9.1-§9.4 sub-section 각 lane) |
| §11 | PMO | ArchitectAgent (Change Plan) + PMOAgent (Retro) |
| §12 | 회고 | PMOAgent |

**INV-DI-1**: semantic-normalize 후 token-level deletion 존재 + non-owner lane 작성 = violation.

### Orchestrator monopoly sections (INV-DI-2 적용)

| 섹션 | 제목 | 독점 근거 |
|---|---|---|
| §10 | FIX Ledger | fix-event-v1 contract (CFP-32 monopoly) |
| §10.5 | GitOps | GitOpsAgent Orchestrator-delegate (ADR-031 Amd1) |
| §13 | ArchitectPL Verdict | ArchitectPLAgent review-verdict-v4 packet |
| §14 | Lane Evidence | ADR-031 §결정 1 + Amendment 1 |

**INV-DI-2**: ANY base-row mutation without Orchestrator/delegate attribution = violation.

### §1 제외 영역

§1 (개요) = `story-section-1-immutable.yml` territory — 중복 codification 금지. 본 lint cross-ref only.

## 위반 분류

### INV-DI-1 (lane-owned, non-owner destructive write)

```
semantic-normalize(base_section) → base_tokens
semantic-normalize(head_section) → head_tokens
token_deletion = base_tokens - head_tokens (meaningful tokens only)
if token_deletion AND lane != owner_lane → VIOLATION
```

PR #441 incident signature: +216/-850 (deletion-dominant = INV-DI-1 다중 섹션 동시 침범).

### INV-DI-2 (monopoly, unauthorized mutation)

```
if section ∈ {§10, §10.5, §13, §14}:
  if content_changed(base, head):
    if branch != cfp-NNN-flat (Orchestrator pattern):
      → VIOLATION (monopoly-unauthorized)
```

## Delegate subagent rule (ADR-031 Amendment 1 / fix-event-v1 Amendment, CFP-275)

Orchestrator-owned delegate subagent 가 monopoly section 수정 시 PASS attribution. 판정 = branch proxy:

- **Orchestrator pattern**: `cfp-NNN` (flat, no `/lane` suffix) → PASS
- **Lane plugin pattern**: `cfp-NNN/<lane>` (hierarchical) → violation candidate
- **Ambiguous / conflicting**: fail-OPEN — violation still reported (content-diff 근거)

## Carrier-Story bootstrap exemption (ADR-062 EC-4)

Story frontmatter 에 아래 조건 충족 시 모든 ownership check FIRST short-circuit:

```yaml
carrier_story: <own_story_key>
bootstrap_exempt_protocols:
  - "policy:lane-self-write-boundary-mechanical"
```

매 exemption 적용 시 `::notice::` audit log.

## Drift-sync rationale

3-way drift:

```
story-page-structure.md headings
    ↕
lane-self-write-ownership-matrix.yaml (SSOT)
    ↕
scripts/lib/check_story_section_ownership.py (SECTION_OWNERS + MONOPOLY_SECTIONS)
    ↕
skills/lane-self-write-boundary/SKILL.md (human mirror)
```

- yaml 변경 시 → script SECTION_OWNERS 갱신 의무
- story-page-structure.md heading 변경 시 → yaml + script 동반 갱신 의무
- 3-way sync-check script = follow-up CFP §13.B (본 Story scope 외 — ADR-064 §결정 1 CFP-scope-unitary)

## Cross-references

- yaml SSOT: `lane-self-write-ownership-matrix.yaml` (same dir)
- Skill: `skills/lane-self-write-boundary/SKILL.md` (human mirror)
- Lint script: `scripts/lib/check_story_section_ownership.py`
- Lint workflow: `templates/github-workflows/story-section-ownership-check.yml`
- Evidence registry: `docs/evidence-checks-registry.yaml` entry `story-section-ownership`
- ADR-031: Lane Evidence §14 monopoly mandate
- fix-event-v1: §10 FIX Ledger monopoly contract
- ADR-062: carrier-Story bootstrap exemption
- ADR-060 Amendment 13 §결정 27: warning-tier entry carrier
- CFP-722: introducing Story
