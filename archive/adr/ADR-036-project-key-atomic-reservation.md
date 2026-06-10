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
  - CFP-671 (Amendment 1 — title regex precedence)
is_transitional: false
amendment_log:
  - amendment_id: 1
    date: 2026-05-14
    carrier: CFP-671
    summary: "Title regex precedence over Issue# fallback — cfp-reserve.yml reservation pattern 정합 보존"
    sunset_justification: "ratchet 강화 (race-free guarantee 보존 + title pattern precedence 추가). 약화 방향 아님."
  - amendment_id: 2
    date: 2026-06-10
    carrier: CFP-2116
    summary: "대괄호 필수 regex 정밀화 — reservation(bracketed) vs reference(bare) 구분으로 title 참조 prior-CFP 오추출 차단"
    sunset_justification: "ratchet 강화 (reference 차단 추가 + race-free/prefix-guard/title-precedence 보존). 약화 아님."
    is_transitional: false
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

## 해소 기준

N/A — permanent policy



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

## CFP-658 cross-ref

ADR-027 Amendment 2 (CFP-658, Wave 1 of Epic CFP-431) §결정 6.H = 본 ADR-036 §결정 1 (`KEY = PREFIX-${ISSUE_NUMBER}` atomic) invariant manual write 영역 보존 — `manual-story-init-fallback.sh` (Phase 2 carrier) 안 `templates/github-workflows/story-init.yml` L107-124 existence_check step verbatim port 로 race-condition 보호 활성. brainstorming 시점 KEY 사전 추측 금지 invariant 동일하게 manual fallback path 에서도 enforce.

## Amendment 1 — Title regex precedence (CFP-671, 2026-05-14)

### 발견된 영역

ADR-036 결정 1 (`KEY = PREFIX-${ISSUE_NUMBER}` race-free) 와 결정 2 (cfp-reserve.yml reservation Issue Form) 가 별도 영역에서 conflict — 사용자가 reservation Issue 발의 후 별도 시간 격차로 Story Issue 를 발의하면 (다른 Issue #) title 의 `[CFP-NNN]` reservation pattern 과 Issue # 가 mismatch.

**실제 사고 (RETRO-CFP-662, 2026-05-14)**: CFP-662 reservation 사전 확보 후 Story Issue #670 발의. Story title = `[STORY] [CFP-662] bootstrap-labels workflow 신설 ...`. story-init.yml workflow 가 KEY = `CFP-670` (Issue # only) 발급 → reservation pattern 무시. 사용자는 `CFP-662` 기대 → mismatch.

### 결정 1 — Title pattern 우선 + Issue # fallback (race-free guarantee 보존)

`Compute story key` step 갱신 logic:

```python
import os, re

title = os.environ.get("ISSUE_TITLE", "")
prefix = os.environ.get("PREFIX", "")
issue_number = os.environ.get("ISSUE_NUMBER", "")

title_clean = re.sub(r"^\[STORY\]\s*", "", title).strip()

# Title pattern `[<PREFIX>-<N>]` or `<PREFIX>-<N>` 우선 추출
m = re.search(r'\[?([A-Z]+-\d+)\]?', title_clean)
key_from_title = m.group(1) if m else ""

# Prefix guard — cross-project KEY injection 차단
if key_from_title and key_from_title.startswith(prefix + "-"):
    key = key_from_title
else:
    # Fallback to Issue # — ADR-036 결정 1 race-free guarantee 보존
    key = f"{prefix}-{issue_number}"
```

**3 변경 영역**:
1. **Title pattern matched + prefix matched** → title KEY 우선 (cfp-reserve.yml reservation 정합)
2. **Title pattern absent** → Issue # fallback (race-free guarantee 보존 — ADR-036 결정 1 invariant)
3. **Title pattern matched + prefix MISMATCH** (예: `[ABC-123]` 에 PREFIX=CFP) → Issue # fallback (cross-project KEY injection 차단 — security guard)

### 결정 1 의 race-free guarantee 보존 근거

본 Amendment 의 fallback path (`key = f"{prefix}-{issue_number}"`) 가 ADR-036 결정 1 의 atomic guarantee 동일 — GitHub Issue numbering 의 server-side atomic monotonic increment 위임.

Title pattern matched 영역에서도 race-free — title 자체는 Issue 생성 시점에 immutable input (사용자 input). 같은 title 입력 → 같은 KEY 결정 (deterministic).

### 결정 2 — Cross-project KEY injection 차단 (security guard)

Title `[ABC-123] ...` (외부 project KEY) 에 PREFIX=CFP 인 repo 에서 발의 시 KEY = `CFP-${ISSUE_NUMBER}` fallback. cross-project KEY 의 wrapper repo 진입 차단.

### 영향

- consumer 영향 0 — title pattern 부재 시 기존 동작 (Issue # fallback) 그대로
- codeforge family Story (reservation pattern 사용 시) = title KEY 정상 발급
- Historical KEY ↔ Issue# misalignment 표 (결정 6) 무관 — 본 Amendment 는 going-forward only

### Sunset justification

ratchet 강화 (race-free guarantee 보존 + title pattern precedence 추가). 약화 방향 아님. ADR-058 §결정 5 정합.

## Amendment 2 — Bracket-mandatory title KEY (CFP-2116, 2026-06-10)

### 발견된 영역

Amendment 1 §결정 1 의 regex `r'\[?([A-Z]+-\d+)\]?'` 가 대괄호를 **optional** 로 둬, title 본문의 bare reference (`CFP-2104 후속`) 도 reservation KEY 로 오추출하는 결손.

**실제 사고 (CFP-2111, 2026-06-09)**: Story title = `[STORY] CFP-2104 후속 — self-test CI 가시성 ...`. story-init 가 KEY = `CFP-2104` 오추출 → 이미 존재하는 KEY 와 충돌 + existence_check HTTP 400 → 자동 scaffold 전면 실패(수동 우회).

**판별 신호 실측**:

| 개념 | title 출현 형태 | 예시 |
|---|---|---|
| **reservation** (예약 KEY) | `[CFP-NNNN]` 대괄호 필수 | `[STORY] [CFP-662] bootstrap-labels workflow 신설 ...` |
| **reference** (참조 prior CFP) | `CFP-NNNN` bare (대괄호 없음) | `[STORY] CFP-2104 후속 — ...` |

→ **단일 판별 신호 = 대괄호 형태** (위치 단독으로는 bare 선두 출현 시 구분 불충분).

### 결정 1 — 대괄호 필수 regex (Amendment 1 §결정 1 supersede)

`compute_key()` 순수 함수의 KEY 추출 regex 를 대괄호 **필수**로 정밀화:

```python
# Amendment 1 §결정 1 (historical — Amd 2 가 supersede):
m = re.search(r'\[?([A-Z]+-\d+)\]?', title_clean)

# Amendment 2 §결정 1 (현재 active):
m = re.search(r'\[([A-Z]+-\d+)\]', title_clean)
```

**변경 축**: 대괄호 optional(`\[?`…`\]?`) → 필수(`\[`…`\]`). capture group `([A-Z]+-\d+)` (prefix-generalized) 는 불변.

**2-layer 방어 보존**: regex 는 대괄호 형태만 검증 (layer-1) + prefix guard(`startswith`) 는 cross-project 차단 유지 (layer-2, ADR-036 Amd 1 §결정 2 불변). prefix-literal 미채택 근거 = prefix guard 가 살아있는 코드 경로로 남아야 AC-4 security fixture 실행.

### 무회귀 논증

신·구 regex 동작 차이는 **bare 토큰 입력에서만** 발생. 대괄호 존재 입력은 신·구 byte-identical 매치:

| 입력 형태 | 구 regex 결과 | 신 regex 결과 | 무회귀? |
|---|---|---|---|
| `[CFP-662] ...` (reservation) | `CFP-662` | `CFP-662` | ✅ 동일 |
| `[ABC-123] ...` (대괄호 + prefix MISMATCH) | `ABC-123` → fallback | `ABC-123` → fallback | ✅ 동일 |
| `story-init KEY 계산 버그 ...` (토큰 부재) | no match → fallback | no match → fallback | ✅ 동일 |
| `CFP-2104 후속 ...` (bare reference) | `CFP-2104` (오추출!) | no match → fallback | ✅ **버그만 정정** |

reservation 정상 흐름(`cfp-reserve`→promote 가 항상 `[CFP-NNNN]` 대괄호 산출) 은 수학적으로 무회귀.

### 결정 2 — `compute_key()` 순수 함수 추출 (testability)

기존 `main()` 안 inline KEY 계산부를 `compute_key(title, prefix, issue_number) -> str` 순수 함수로 추출. `main()` 은 env read → `compute_key()` → slug 계산 → print. **3-line stdout 출력 계약(key/slug/title_clean) 불변** — workflow sed 파싱 무손상.

### 결정 3 — `--self-test` fixture F1-F8

`argparse --self-test` + `run_self_test()` 인라인 fixture (sibling `check_adr_citation_slug.py` CFP-2104 패턴 복제). 8 fixture = AC-1~4 + E1/E2/E4 + P2-2 전수 커버. de-bloat 정합 (bats 신규 0, ADR-061 .py SSOT).

CI wire: `adr-citation-slug.yml` 선례대로 적정 워크플로에 `--self-test` step 추가.

### 영향

- **consumer 영향 0** — PREFIX-agnostic generalized capture 유지, env 계약 불변
- `.github/workflows/story-init.yml` + `templates/github-workflows/story-init.yml` **무변경** (`.py` 호출만)
- going-forward ratchet 강화 (reference 차단 추가). 기존 misaligned KEY 遡及 적용 금지 (Amd 1 §결정 6 동일)

### Sunset justification

ratchet 강화 (reference 차단 추가 + race-free/prefix-guard/title-precedence 보존). 약화 방향 아님. ADR-058 §결정 5 정합. `is_transitional: false`.
