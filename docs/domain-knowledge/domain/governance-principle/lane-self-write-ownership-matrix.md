---
kind: domain_fact
type: domain-knowledge
area: governance-principle
topic_slug: lane-self-write-ownership-matrix
title: Lane Self-Write Ownership Matrix — Story file per-section 소유권 SSOT 해설
status: Active
tags:
  - lane-self-write
  - story-section-ownership
  - orchestrator-monopoly
  - delegate-subagent
  - cfp-722
related_adrs:
  - ADR-031   # Lane Evidence §14 monopoly + Amendment 1 delegate rule
  - ADR-013   # codeforge family dogfood-out policy
  - ADR-060   # evidence-enforceable promotion framework (Amendment 13 §결정 27 carrier)
  - ADR-061   # Python script-writing convention (lint Python SSOT 모체)
  - ADR-062   # carrier-Story bootstrap exemption (EC-4)
related_stories:
  - CFP-32    # fix-event-v1 §10 FIX Ledger monopoly contract
  - CFP-275   # ADR-031 Amendment 1 delegate subagent rule
  - CFP-441   # PR incident signature (+216/-850 deletion-dominant)
  - CFP-722   # introducing Story (본 페이지 carrier)
yaml_ssot: lane-self-write-ownership-matrix.yaml
skill_mirror: skills/lane-self-write-boundary/SKILL.md
created: 2026-05-16
updated: 2026-05-16
---

# Lane Self-Write Ownership Matrix — Story file per-section 소유권 SSOT 해설

> **SSOT**: `lane-self-write-ownership-matrix.yaml` (same directory). 본 문서는 yaml SSOT 의 human-readable 해설.
> **Drift-sync**: yaml ↔ SKILL.md ↔ `templates/story-page-structure.md` headings ↔ `scripts/lib/check_story_section_ownership.py` regex. 3-way sync-check = follow-up CFP (Change Plan §13.B).

## 정의

**Lane Self-Write Ownership Matrix** 는 `docs/stories/<KEY>.md` Story file 의 per-section 소유권을 기계 판독 가능한 형태로 기록한 SSOT 다. 각 lane plugin (codeforge-requirements / codeforge-design / codeforge-develop / codeforge-pmo) 의 owner section 과 Orchestrator monopoly section (§10 / §10.5 / §13 / §14) 을 분리해 정의하며, lint (`scripts/lib/check_story_section_ownership.py`) 가 본 matrix 의 yaml 형태를 SECTION_OWNERS + MONOPOLY_SECTIONS 로 import 해 PR diff 위반을 감지한다.

## 컨텍스트

본 SSOT 는 다음 4 요인의 수렴체다:

1. **PR #441 incident** (deletion-dominant +216/-850): lane plugin 이 non-owner section 을 token-level 삭제하면서 다중 섹션 침범 발생. INV-DI-1 mechanical detection 필요성 표면화.
2. **§10 FIX Ledger monopoly** (CFP-32 / fix-event-v1 contract): Orchestrator 단독 append 독점이 lane self-write 와 충돌 검사 영역 분리 의무.
3. **ADR-031 Amendment 1 delegate subagent rule** (CFP-275): Orchestrator-owned delegate 가 monopoly section 수정 시 PASS attribution — branch proxy (`cfp-NNN` flat) 로 판정.
4. **CFP-722 carrier**: 본 Story 가 mechanical lint (`story-section-ownership-check.yml` + Python SSOT) 도입 시 reference matrix 필요. yaml machine-readable SSOT + md human-readable 해설 + skill mirror 3-way.

본 페이지는 yaml SSOT 의 motivation / 위반 분류 / delegate 예외 / bootstrap exemption / drift-sync 운영 룰을 해설 layer 로 풀어낸다.

## 핵심 규칙

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

### 위반 알고리즘

#### INV-DI-1 (lane-owned, non-owner destructive write)

```
semantic-normalize(base_section) → base_tokens
semantic-normalize(head_section) → head_tokens
token_deletion = base_tokens - head_tokens (meaningful tokens only)
if token_deletion AND lane != owner_lane → VIOLATION
```

PR #441 incident signature: +216/-850 (deletion-dominant = INV-DI-1 다중 섹션 동시 침범).

#### INV-DI-2 (monopoly, unauthorized mutation)

```
if section ∈ {§10, §10.5, §13, §14}:
  if content_changed(base, head):
    if branch != cfp-NNN-flat (Orchestrator pattern):
      → VIOLATION (monopoly-unauthorized)
```

### Delegate subagent rule (ADR-031 Amendment 1 / fix-event-v1 Amendment, CFP-275)

Orchestrator-owned delegate subagent 가 monopoly section 수정 시 PASS attribution. 판정 = branch proxy:

- **Orchestrator pattern**: `cfp-NNN` (flat, no `/lane` suffix) → PASS
- **Lane plugin pattern**: `cfp-NNN/<lane>` (hierarchical) → violation candidate
- **Ambiguous / conflicting**: fail-OPEN — violation still reported (content-diff 근거)

### Carrier-Story bootstrap exemption (ADR-062 EC-4)

Story frontmatter 에 아래 조건 충족 시 모든 ownership check FIRST short-circuit:

```yaml
carrier_story: <own_story_key>
bootstrap_exempt_protocols:
  - "policy:lane-self-write-boundary-mechanical"
```

매 exemption 적용 시 `::notice::` audit log 발화 의무.

## 경계

본 SSOT 의 scope 밖 영역:

- **§1 (개요) section immutability**: `story-section-1-immutable.yml` Action 영역 — 중복 codification 금지. 본 matrix 는 cross-ref only.
- **Story 외 doc 의 ownership**: ADR / Change Plan / Retro / domain-knowledge 의 owner = CODEOWNERS + ADR-013 dogfood-out policy 영역. 본 matrix 는 Story file 한정.
- **Non-Story commit (chore / typo / link fix)**: ADR-013 면제 대상 Story file 미생성 영역. 본 lint 활성 영역 외.
- **Branch protection / required check enforcement**: ADR-024 영역. 본 matrix 는 detection layer 만 정의.

## 관련 ADR

- [ADR-031](../../../adr/ADR-031-lane-spawn-evidence-trail.md): Lane Evidence §14 monopoly mandate (§결정 1 + Amendment 1 delegate rule)
- [ADR-013](../../../adr/ADR-013-codeforge-family-dogfood-out-policy.md): codeforge family dogfood-out — Story file storage policy
- [ADR-060](../../../adr/ADR-060-evidence-enforceable-promotion-framework.md): evidence-enforceable promotion framework — Amendment 13 §결정 27 (`story-section-ownership` warning-tier entry carrier)
- [ADR-061](../../../adr/ADR-061-python-script-writing-convention.md): Python script-writing convention — lint Python SSOT 외부 .py 의무 모체
- [ADR-062](../../../adr/ADR-062-carrier-bootstrap-dependency-rule.md): carrier-Story bootstrap exemption (EC-4)
- `fix-event-v1` contract: §10 FIX Ledger Orchestrator monopoly (CFP-32)
- yaml SSOT: [`lane-self-write-ownership-matrix.yaml`](lane-self-write-ownership-matrix.yaml) (same dir)
- Skill mirror: [`skills/lane-self-write-boundary/SKILL.md`](../../../../skills/lane-self-write-boundary/SKILL.md)
- Lint script: [`scripts/lib/check_story_section_ownership.py`](../../../../scripts/lib/check_story_section_ownership.py)
- Lint workflow: [`templates/github-workflows/story-section-ownership-check.yml`](../../../../templates/github-workflows/story-section-ownership-check.yml)
- Evidence registry entry: `story-section-ownership` (`docs/evidence-checks-registry.yaml`)

## 변경 이력

- **2026-05-16** (CFP-722, FIX iter 2): 초기 작성 — yaml SSOT human-readable 해설로 신규 추가. domain-knowledge schema (frontmatter 6 필드 + 6 섹션) 준수. PR #441 incident + Orchestrator monopoly + delegate rule + bootstrap exemption 통합 카탈로그.
