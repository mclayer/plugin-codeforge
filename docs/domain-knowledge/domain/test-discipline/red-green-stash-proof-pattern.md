---
key: RGS-001
title: "RED→GREEN stash proof pattern — Discriminating fixture mandate"
type: domain-knowledge
domain: test-discipline
status: Active
date: 2026-05-24
carrier_story: CFP-1334
authors:
  - ArchitectAgent (chief author)
related_stories:
  - CFP-1334
  - CFP-750   # memory feedback origin
  - CFP-1302  # F-CR-1302-2 P2 finding (origin)
related_adrs:
  - ADR-060   # framework primary anchor (warning-tier entry)
  - ADR-061   # production-scale invariant sibling axis
  - ADR-068   # boundary completeness invariants cross-ref
  - ADR-082   # write-time self-write verification mandate cross-ref
  - ADR-086   # deputy creation decision framework
---

# RED→GREEN stash proof pattern — Discriminating fixture mandate

본 entry = codeforge governance 어휘 "discriminating fixture mandate" 의 첫 narrative SSOT. memory `feedback_tdd_red_proof_via_stash` (사용자 사전 승인 패턴, CFP-750 2026-05-16 applied evidence) 의 codeforge 정식 governance 어휘 promotion.

## 1. 핵심 개념

### 1.1 Discriminating fixture

**정의**: 테스트가 production code 의 신규 동작을 실제로 구별(discriminate)하는지 입증하는 fixture. 즉 "production code 가 부재했다면 본 fixture 가 정말 RED 였는가" 를 사후 입증.

**대조 anti-pattern — Vacuous green / always-green test**:
- fixture 가 production code 부재여도 PASS — 영구 regression silent 통과 위험
- 산업 vocabulary: Google Testing Blog "How to Write a Test (and What Not to Do)", SE@Google book ch.11 Test Doubles
- 산업 mitigation: Mutation testing (mutmut Python / PIT Java / Stryker JavaScript) — 본 패턴 = mutation testing 의 simplified instance (mutant = pre-impl HEAD state)

### 1.2 RED→GREEN proof

**정의**: TDD canonical 순서 (RED 우선 → GREEN → REFACTOR) 의 사후 입증 기법. cross-layer working-tree drift (DeveloperAgent GREEN 선착, QADeveloperAgent RED 후착) 시점에 적용.

**적용 시점**: bats fixture (또는 일반 test fixture) 작성 시. 신규 fixture 가 production code 의 신규 동작을 어떻게 구별하는지 evidence artifact 동반.

## 2. Method 3-enum (closed set)

### 2.1 `stash` (PRIMARY method, memory feedback 패턴 verbatim)

```bash
# Step 1: production impl stash
git stash push --include-untracked -- <impl_paths>
# pre-impl HEAD 상태 노출

# Step 2: pre-GREEN HEAD 에서 fixture 실행
bats tests/<path>/<name>.bats
# 기대: 신규 case 가 RED (FAIL) — discriminating 입증
# regression-guard case 는 양 regime 모두 GREEN — 구분 보고

# Step 3: stash pop
git stash pop
# production impl 복원

# Step 4: full GREEN 재확인
bats tests/<path>/<name>.bats
# 기대: 전체 PASS
```

**evidence artifact**: stash output stdout/stderr + `git stash list` + per-@test result mapping.

### 2.2 `pre_impl_checkout`

```bash
# Step 1: pre-impl SHA pin
PRE_IMPL_SHA=$(git rev-parse HEAD@{N})   # 또는 명시적 commit SHA

# Step 2: pre-impl HEAD checkout (detached)
git checkout "$PRE_IMPL_SHA"
bats tests/<path>/<name>.bats
# 기대: 신규 case RED

# Step 3: 복원
git checkout -
bats tests/<path>/<name>.bats
# 기대: full GREEN
```

**evidence artifact**: pre_impl_sha + 양 시점 result.

**적용 제한**: branch state preserve 필요 시 detached HEAD 위험 (uncommitted change loss). stash 가 안전.

### 2.3 `branch_revert`

```bash
# Step 1: impl commit revert (no-commit)
git revert --no-commit <impl_commit_sha>
bats tests/<path>/<name>.bats
# 기대: 신규 case RED

# Step 2: revert abort
git revert --abort
bats tests/<path>/<name>.bats
# 기대: full GREEN
```

**적용 제한**: merge commit revert 시 mainline branch 명시 (`-m 1`) 필요. multi-commit impl 시 sequential revert 의무.

## 3. assertion classification 3-enum (multi-@test fixture per-@test 분류)

한 fixture 안 multiple `@test` 시 각각 분류 의무:

| role | pre_impl_outcome | post_impl_outcome | 의미 |
|---|---|---|---|
| `discriminating` | FAIL | PASS | **Genuine RED→GREEN** — 신규 동작 구별 입증 |
| `regression_guard` | PASS | PASS | 양 regime green — 기존 behavior 보호 |
| `bootstrap` | (assertion 0 — N/A) | PASS | Fixture infrastructure setup 만 (`setup_file` / `teardown_file` / helper) |

**의무**: multi-@test fixture 에 각 `@test` 분류 표 명시 (Change Plan §8 안 `red_green_proof_evidence_artifact.assertion_classification[]` field).

**memory 패턴 verbatim**: "regression-guard case(양 regime green) 와 discriminating case(pre-GREEN fail) 구분 보고"

## 4. Cross-platform 비대칭 (Researcher Unknown 1)

`git stash` 동작은 환경 마다 비대칭:

| 환경 | 알려진 문제 |
|---|---|
| Windows Git Bash | `--include-untracked` 필수 (untracked 변경 누락 차단). CRLF/LF 행 종료자 `.gitattributes` `text=auto` 충돌 시 stash 가 LF 변환 후 pop 시 CRLF 복원 — byte-identical assertion 깨짐 |
| MSYS2 | Windows Git Bash 동형 |
| WSL | Linux 동형 but path separator 충돌 가능 |
| Linux | baseline |
| macOS | BSD `sed` / `grep` 동작 차이 — fixture 안 GNU 의존 시 false-RED |

**mitigation**:
- Change Plan §8 schema 안 `platform_verified[]` 5-enum field (linux / macos / windows_git_bash / wsl / msys2) — 작성자가 검증 환경 명시 의무
- self-contained fixture scope 제한 (외부 state 차단 — `tempfile -d` / `mktemp -d` patterns)
- cross-platform marker check (`uname -s` enum) advisory

## 5. memory ↔ codeforge governance 어휘 매핑

| memory `feedback_tdd_red_proof_via_stash` 어휘 | codeforge governance 어휘 (본 entry) | Change Plan §8 field |
|---|---|---|
| "pre-GREEN HEAD" | pre-impl HEAD | `pre_impl_sha` |
| "genuine fail" | discriminating RED | `assertion_classification.role: discriminating` |
| "stash push → bats → stash pop" | stash method | `method: stash` |
| "regression-guard case" | regression_guard role | `assertion_classification.role: regression_guard` |
| "fixture infrastructure setup" | bootstrap role | `assertion_classification.role: bootstrap` |

## 6. ADR layer governance (chief tie-break ladder Option C convergence)

**현 상태**: ADR 신설 0건. declaration-only Wave 1:
- Change Plan §8 schema field (`templates/impl-manifest.md` SSOT)
- TestContractArch deputy mandate body (`skills/deputy-mandate/SKILL.md` L80 + RACI matrix L115)
- evidence-checks-registry warning-tier entry `bats-red-green-proof-presence`
- 본 narrative SSOT (codeforge governance 어휘 promotion)

**ADR 승격 carrier (deferred)**: pattern_count ≥ 2 reach 시 (Phase 2 mechanical wire 후 evidence 누적) — CFP-FU-3 (ADR-068 Amendment 4 또는 ADR-082 Amendment N 별 carrier).

**axis 분석** (chief tie-break ladder Step 3 — ADR-086 §결정 1):
- ADR-068 (boundary completeness invariants) = design-level scope → axis mismatch (bats fixture = test-authoring scope)
- ADR-082 (write-time self-write verification mandate) = §결정 7 explicit reject of per-area split → infeasible
- ADR-061 (Python script-writing convention) = bash + workflow yml only scope → bats 미포함
- → **Option C convergence** (declaration-only Wave 1, ADR 신설 0건)

## 7. CFP-1302 retroactive 적용 (CFP-FU-1 별 carrier)

CFP-1302 의 33 TC (test_phase_gate_mergeable_yml 13 + test_phase_gate_auto_cleanup_yml 20) retroactive RED→GREEN proof 부착 = **별 CFP carrier 분리** (CFP-FU-1).

**분리 사유**:
- ADR-068 Amendment retroactive 면제 패턴 답습 (Amendment 3 발효 후 신규 finding 한정)
- 본 mandate forcing function 활성 시점부터 영구 적용 — retroactive backfill 은 audit Story 영역
- CFP scope unitary (ADR-064 §결정 5) — "mandate 도입" + "33 TC backfill" 양 결정 1 CFP 통합 불가

## 참조

- Carrier Story: [CFP-1334](../../../stories/CFP-1334.md)
- Change Plan: [cfp-1334-bats-red-green-proof.md](../../../change-plans/cfp-1334-bats-red-green-proof.md)
- memory source: `feedback_tdd_red_proof_via_stash` (CFP-750 2026-05-16 applied evidence)
- 선행 retro: [`2026-05-23-cfp-1302.md §5 F4`](../../../retros/2026-05-23-cfp-1302.md)
- ADR cross-ref: ADR-060 / ADR-061 / ADR-068 / ADR-082 / ADR-086
- 외부 vocabulary:
  - Kent Beck, *Test-Driven Development by Example* (2002) — RED → GREEN → REFACTOR canonical
  - Google Testing Blog "How to Write a Test (and What Not to Do)" — Vacuous green anti-pattern
  - SE@Google book ch.11 Test Doubles — Test discipline
  - Pro Git book §7.3 — `git stash` mechanism cross-platform
  - Mutation testing tools: mutmut (Python) / PIT (Java) / Stryker (JavaScript)
