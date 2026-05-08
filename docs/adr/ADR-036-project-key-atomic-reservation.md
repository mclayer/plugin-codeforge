---
adr_number: 36
title: Project key atomic reservation — KEY = PREFIX-Issue#
status: Accepted
category: process
date: 2026-05-08
related_files:
  - templates/github-workflows/story-init.yml
  - templates/github-issue-forms/cfp-reserve.yml
  - templates/github-workflows/reservation-cleanup.yml
  - docs/inter-plugin-contracts/label-registry-v1.md
  - scripts/bootstrap-labels.sh
  - docs/orchestrator-playbook.md
  - docs/consumer-guide.md
  - docs/adr/ADR-024-story-scoped-branch-policy.md
related_stories:
  - CFP-260 (carrier)
  - CFP-259 (parent Epic)
---

# ADR-036: Project key atomic reservation — KEY = PREFIX-Issue#

## 상태

`Accepted` (2026-05-08, CFP-260 carrier — Phase 1 PR #266 + Phase 2 PR #269 merged).

## 컨텍스트

CFP-259 Epic Wave 1 첫 작업. `templates/github-workflows/story-init.yml` (line 70-81) 의 KEY 발급 로직 race condition + brainstorming 시점 KEY 사전 확보 수단 부재.

**현재 (story-init.yml line 70-81)**:

```bash
LAST=$(find docs/stories -maxdepth 1 -name "${PREFIX}-*.md" | sort -n | tail -1)
NEXT=$(( ${LAST:-0} + 1 ))
echo "key=${PREFIX}-${NEXT}" >> "$GITHUB_OUTPUT"
```

**3 결함**:

1. `concurrency:` group 미정의 → 동시 Issue Form 제출 시 race
2. main snapshot 만 보고 max 계산 → 미 merged feature branch 의 docs/stories/ 무시 → cross-branch 충돌
3. brainstorming 시점에 KEY 사전 확보 수단 부재 → spec 작성자가 manual 추측 → cross-session collision

**실제 사고 (2026-05-08)**: 두 세션이 동시 작업 중 — A 세션이 CFP-134~CFP-139 6 Issue 발의 (Issue #251~#256), B 세션이 같은 시간에 CFP-135 / CFP-136 추정으로 작업 시도 → KEY collision 검출 + 정정 via 본 ADR 발의.

## 결정

### 결정 1: KEY 형식 = `<PREFIX>-<Issue#>` (Option B)

GitHub Issue numbering 의 atomic guarantee 위임. Issue 생성 = key 확정 단일 모멘트. race window 0.

`templates/github-workflows/story-init.yml` 갱신:

```bash
echo "key=${PREFIX}-${ISSUE_NUMBER}" >> "$GITHUB_OUTPUT"
```

(line 70-81 의 find / sort / max+1 4 lines 제거)

**근거**: GitHub 의 Issue numbering 은 repo 단위 atomic + monotonic + immutable. POST `/repos/{owner}/{repo}/issues` API 가 server-side increment, race-free. 외부 lock / counter file 불필요.

### 결정 2: Reservation Issue Form `cfp-reserve.yml` 신설

`templates/github-issue-forms/cfp-reserve.yml` (1-line title 만 받음):

```yaml
name: CFP key reservation (1-line)
description: Brainstorming 시점 KEY 사전 확보. 30 일 미진행 시 자동 close.
title: "[reservation] CFP-? — <theme>"
labels: ["phase:reservation"]
body:
  - type: markdown
    attributes:
      value: |
        ## Reservation
        Issue 생성 직후 발급되는 # 가 KEY 가 됩니다 (`CFP-<#>`).
        spec 작성 후 `phase:reservation` → `phase:요구사항` + `type:story` 로 promote.
        30 일 미진행 시 reservation-cleanup.yml 이 자동 close.
  - type: textarea
    id: theme
    attributes:
      label: Theme (optional, 1-2 sentences)
      description: brainstorming 주제 — spec 작성 시 갱신
    validations:
      required: false
```

### 결정 3: `phase:reservation` label 신설

`docs/inter-plugin-contracts/label-registry-v1.md` MINOR bump (v1.4 → v1.5). `scripts/bootstrap-labels.sh` 에 entry 추가 (color #ededed, attach_owner: Orchestrator).

### 결정 4: `templates/github-workflows/reservation-cleanup.yml` 신설

30 일 미진행 reservation 자동 close. `schedule:` daily cron `0 2 * * *` UTC + GraphQL query 로 `phase:reservation` label + `created_at < 30 days ago` filter + comment + close.

```yaml
on:
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    permissions:
      issues: write
    steps:
      - name: Close stale reservations
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # gh api search → label phase:reservation + state:open + created:<30d ago
          # for each: gh issue comment + gh issue close --reason "not_planned"
```

### 결정 5: story-init.yml `concurrency:` 안전망

```yaml
concurrency:
  group: story-init-${{ github.event.issue.number }}
  cancel-in-progress: false
```

per-Issue group → 같은 Issue 의 reopen / re-trigger race 만 직렬화. 병렬 Issue (다른 #) 는 영향 없음.

### 결정 6: Migration — 기존 KEY 그대로

기존 `docs/stories/CFP-1.md` ~ `CFP-133.md` (merged) + `CFP-134~CFP-139` (in-flight) + `CFP-259~CFP-262` (본 Epic, Issue # 와 align — 이미 Option B 적용) 는 **rename 안 함**. 본 ADR Accepted 후 신규 Story (Issue #263+) 부터 적용.

**Historical KEY ↔ Issue# misalignment 표** (audit trail):

| KEY | Issue # | Misalignment? |
|---|---|---|
| CFP-1 ~ CFP-133 | #1 ~ #239 (산재) | YES (sequential KEY ≠ Issue#) |
| CFP-134 (Epic) | #251 | YES |
| CFP-135 ~ CFP-139 (children) | #252 ~ #256 | YES |
| **CFP-259 (Epic, Option B 적용)** | **#259** | **NO (aligned)** |
| **CFP-260 ~ CFP-262** | **#260 ~ #262** | **NO (aligned)** |
| CFP-263+ (future) | #263+ | NO (aligned) |

기존 misaligned KEY 는 historical artifact 로 보존. retrospective rename 금지 (commit history / Issue body / PR title 등 cross-reference 의 일관성 위배).

## 결과

### 긍정

- KEY race condition 0 (GitHub atomic numbering 위임)
- brainstorming 시점에 KEY 인용 가능 (reservation Issue 발의 → KEY 즉시 echo)
- story-init.yml 단순화 (4 lines 제거)
- cross-session work 시 KEY collision 사고 방지

### 부정 / Trade-off

- KEY 점프 (CFP-260 → CFP-300 등) — sequential KEY 의 직관성 손상. 그러나 GitHub UI 에서 Issue # 와 KEY 동일 매핑 → 별도 cognitive load 적음
- 기존 KEY ↔ Issue# misalignment 가 검색 시 confusion (예: "CFP-133" grep 시 Issue#239 결과 mix). Migration 표가 audit trail 제공
- `phase:reservation` label 누락 시 reservation-cleanup 미동작 → bootstrap-labels.sh idempotent 강제

### 영향

- **wrapper plugin**: story-init.yml + new files 추가. 본 ADR Accepted 후 자체 next bump 시 ADR-037 (CFP-261) bump rule 적용 (template 추가 = MINOR or required workflow 추가 = MAJOR — ADR-037 §3.1 (d) 행 판단)
- **6 lane plugin**: 영향 없음 (lane plugin 은 자체 story-init.yml 미보유)
- **consumer**: consumer-guide.md §2 갱신 — 자체 Issue Form 사용 시 본 패턴 권장 + project.yaml `story_key_prefix` 로 prefix override 가능

## 다이어그램

```
brainstorming 시작
   │
   ▼
GitHub Issue Form `cfp-reserve.yml` 발의 (1-line title)
   │
   │ POST /repos/.../issues  ← GitHub atomic
   │
   ▼
Issue #N 생성 = key 확정 모멘트
   │
   │ KEY = <PREFIX>-<N> echo (Issue body comment via cleanup workflow on creation)
   │
   ▼
spec / Phase 1 PR / Phase 2 PR 모두 KEY 인용 (race-free)
   │
   ├── (promote 시) phase:reservation → phase:요구사항 + type:story
   │     └── story-init.yml fires → branch + Phase 1 PR + docs/stories/<KEY>.md
   │
   └── (30 일 미진행 시) reservation-cleanup.yml → 자동 close
```

## 관련 파일

- [`templates/github-workflows/story-init.yml`](../../templates/github-workflows/story-init.yml) — 갱신 대상
- `templates/github-issue-forms/cfp-reserve.yml` — 신설 (Phase 2 spillover, 본 PR 에는 부재)
- `templates/github-workflows/reservation-cleanup.yml` — 신설 (Phase 2 spillover, 본 PR 에는 부재)
- [`docs/inter-plugin-contracts/label-registry-v1.md`](../inter-plugin-contracts/label-registry-v1.md) — MINOR bump
- [`scripts/bootstrap-labels.sh`](../../scripts/bootstrap-labels.sh) — `phase:reservation` entry
- [`docs/adr/ADR-024-story-scoped-branch-policy.md`](ADR-024-story-scoped-branch-policy.md) — branch governance cross-ref
- [Internal-docs Change Plan: CFP-260](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/change-plans/cfp-260-project-key-atomic-reservation.md)
- [Internal-docs Epic spec: CFP-259](https://github.com/mclayer/codeforge-internal-docs/blob/main/wrapper/specs/2026-05-08-cfp-259-plugin-version-key-governance-epic-design.md)
