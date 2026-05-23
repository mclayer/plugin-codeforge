---
kind: domain_fact
type: domain-knowledge
area: test-discipline
topic_slug: red-green-stash-proof-pattern
title: "RED→GREEN stash proof pattern — Discriminating fixture mandate"
status: Active
created: 2026-05-24
updated: 2026-05-24
carrier_story: CFP-1334
tags:
  - test-discipline
  - tdd
  - red-green
  - discriminating-fixture
  - bats
  - vacuous-green
  - mutation-testing
related_adrs:
  - ADR-060   # framework primary anchor (warning-tier entry)
  - ADR-061   # production-scale invariant sibling axis (Amendment 2 §결정 9)
  - ADR-068   # boundary completeness invariants cross-ref (6-invariant axis 분석)
  - ADR-082   # write-time self-write verification mandate cross-ref (§결정 7 per-area 분할 거부)
  - ADR-086   # deputy creation decision framework (chief tie-break ladder Step 3 5-checklist)
related_stories:
  - CFP-1334  # 본 entry carrier
  - CFP-750   # memory feedback origin (2026-05-16 first applied instance)
  - CFP-1302  # F-CR-1302-2 P2 finding (vacuous green 차단 motivation)
related_files:
  - templates/impl-manifest.md  # Change Plan §8 schema field `red_green_proof_evidence_artifact`
  - skills/deputy-mandate/SKILL.md  # TestContractArch mandate body (RACI matrix §8.5 row)
  - docs/evidence-checks-registry.yaml  # bats-red-green-proof-presence warning-tier entry
---

# RED→GREEN stash proof pattern — Discriminating fixture mandate

본 entry = codeforge governance 어휘 **"discriminating fixture mandate"** 의 첫 narrative SSOT. memory `feedback_tdd_red_proof_via_stash` (사용자 사전 승인 패턴, CFP-750 2026-05-16 applied evidence) 의 codeforge 정식 governance 어휘 promotion.

## 정의

**Discriminating fixture mandate**: bats fixture (또는 일반 test) 가 production code 의 신규 동작을 실제로 검출(discriminate)하는지 사후 입증하는 mechanism — production code 부재 시 절대 PASS 되지 않아야 한다 (anti-vacuous-green invariant). RED→GREEN stash proof 는 본 mandate 의 단일 mutant manual subset — `git stash` 로 GREEN 구현을 일시 격리한 후 fixture 가 genuine FAIL (RED) 함을 입증하는 패턴.

**Evidence artifact** = stash sequence + pre-impl SHA pin + per-assertion classification + cross-platform marker 의 declarative record.

## 컨텍스트

codeforge 의 test discipline 은 ADR-068 boundary completeness invariants + ADR-061 production-scale invariant 영역 정합. 본 patterm motivation:

1. **CFP-750 (2026-05-16)** — cross-layer TDD (QADeveloperAgent RED ∥ DeveloperAgent GREEN, 별도 session working-tree drift) 에서 GREEN 구현이 RED fixture commit 보다 먼저 working tree 에 도착하는 사례 발견. RED-then-GREEN 순서 가 깨져 fixture authenticity 사후 입증 메커니즘 필요. `git stash push -- <impl>` 으로 pre-GREEN HEAD 노출 → fixture 실행 → genuine FAIL 확인 → `git stash pop` 으로 GREEN 복원 → full suite GREEN 확증 패턴 발견.
2. **CFP-1302 retro F4 (2026-05-23)** — CodeReviewPL F-CR-1302-2 P2 finding: 신규 33 bats TC (test_phase_gate_mergeable_yml.bats 13 + test_phase_gate_auto_cleanup_yml.bats 20) 모두 grep-presence heuristic 만 사용 — discriminating proof 부재. vacuous green 위험 (production code 부재여도 PASS 가능).
3. **CFP-1334 (2026-05-24)** — 본 entry carrier. TestContract deputy mandate 영역에서 discriminating fixture mandate codification. chief tie-break ladder 3 단계 적용 후 Option C convergence (declaration-only Wave 1, ADR 신설 0건, evidence-checks-registry warning-tier entry).

산업 표준 인접 영역: mutation testing (PIT/Stryker/mutmut) 의 simplified manual subset — 단일 mutant ("production code 이전 버전") + manual kill verification ("fixture FAIL 확인"). Kent Beck *Test-Driven Development by Example* (2002) 의 RED→GREEN→REFACTOR canonical cycle 의 post-hoc recovery variant.

## 핵심 규칙

### 1. Stash sequence (memory verbatim)

```bash
# pre-GREEN HEAD 확보
PRE_IMPL_SHA="$(git rev-parse HEAD)"

# GREEN 구현 일시 격리 (--include-untracked 필수 — 신규 파일 기반 fixture 영역)
git stash push --include-untracked -- <impl-file>

# pre-impl state 에서 fixture 실행 → genuine FAIL 확인
bats <fixture-file>   # 또는 cd worktree && bash <test-runner>
# Expected: discriminating @test FAIL + regression_guard @test PASS

# GREEN 구현 복원
git stash pop

# full suite 재실행 → GREEN 확증
bats <fixture-file>
# Expected: 전 @test PASS
```

### 2. Per-assertion classification (multi-@test fixture)

bats fixture 안 multiple `@test` 영역 — role 3-enum closed-set:

- **discriminating**: pre-impl 에서 FAIL + post-impl 에서 PASS (구현 가능성을 실제로 입증)
- **regression_guard**: pre-impl 에서 PASS + post-impl 에서 PASS (의도된 보존 영역 — vacuous 아님)
- **bootstrap**: pre-impl 에서 SKIP + post-impl 에서 PASS (초기 환경 의존 영역, advisory)

`assertion_classification[]` field 안 per-@test role + pre/post outcome 명시 의무. discriminating role 이 1+ 존재 시 mandate 충족.

### 3. Change Plan §8 schema field

신규 bats fixture 작성 시 Change Plan §8.5 `bats_fixtures[]` array 안 row 별 `red_green_proof_evidence_artifact` nested object declare 의무:

```yaml
red_green_proof_evidence_artifact:
  method: stash | pre_impl_checkout | branch_revert   # 3-value closed-set
  pre_impl_sha: <git SHA pinned via git rev-parse HEAD before stash>
  fixture_file: <path>
  assertion_classification:
    - test_name: <@test name verbatim>
      role: discriminating | regression_guard | bootstrap   # 3-value closed-set
      pre_impl_outcome: PASS | FAIL | SKIP
      post_impl_outcome: PASS | FAIL | SKIP
  platform_verified: [linux, macos, windows-git-bash, msys2, wsl]   # 5-value closed-set, ≥1 required
  stash_evidence_excerpt: <stdout/stderr verbatim 또는 path-line ref>
```

null 명시 시 `red_green_proof_evidence_artifact_null_reason` 4-enum closed-set 의무: `regression_guard_only | cross_platform_constraint | pre_impl_unavailable | na_doc_only` (ADR-068 I-3 unconditional vs conditional guard placement intent 패턴 답습).

### 4. TestContract deputy mandate 영역

본 mandate 의 owner = TestContractArchitectAgent (codeforge-design deputy primary). `skills/deputy-mandate/SKILL.md` L80 + RACI matrix L115 §8.5 sub-section "discriminating fixture mandate (RED→GREEN proof)" row 정합. chief tie-break ladder Step 1 RACI lookup 결과.

### 5. evidence-checks-registry warning-tier entry

`bats-red-green-proof-presence` warning-tier deferred-followup entry (owner_adr ADR-060 / carrier_adr ADR-060, recurrence count 1 / threshold 3). 5-marker grep-presence heuristic (`pre_impl_sha` / `git stash push` OR `git stash pop` / `discriminating` OR `regression_guard` / `RED.{1,5}GREEN` OR `pre-impl HEAD` / `platform_verified`) ≥3/5 → PASS. <3/5 → warning. Phase 2 mechanical wire (lint script + workflow + META self-app bats fixture) 후 warning 전환.

## 경계

### 1. Scope 포함 영역

- bats fixture (shell test runner, codeforge dogfood + 일반 codeforge consumer)
- declaration-only Wave 1 (Change Plan §8 schema field + TestContractArch mandate + evidence-registry warning entry + 본 narrative SSOT) — Phase 2 mechanical wire 별 sub-carrier

### 2. Scope 외 영역

- **Python pytest / Node jest 영역** — language-agnostic pattern 으로 generalize 가능하나 cross-platform stash 검증 별 axis. 별 carrier CFP-FU-N.
- **CFP-1302 retroactive 33 TC 영역** — forward-only normative ratchet (ADR-068 Amendment 3 retroactive 면제 precedent 답습). 33 TC retroactive 부착은 별 carrier **CFP-FU-1** (sibling Story).
- **mutation testing 자동화 도구 도입** — PIT / Stryker / mutmut 등 자동 mutant 주입 도구. bats stash proof 는 단일 mutant manual subset. 자동화 도구 도입은 별 영역.

### 3. Cross-platform 제한

`git stash` cross-platform 비대칭:
- Linux / macOS: 안정
- Windows Git Bash + MSYS2: bats-core (`#!/usr/bin/env bats`) shebang + CRLF/LF 변환 위험 + `--include-untracked` flag 필수
- WSL: 안정 (Linux 동등)
- Windows native cmd / PowerShell: bats-core 비호환

self-contained fixture (외부 state — tmp dir / env var / DB connection 의존 0) 영역 한정. 외부 state 의존 시 false-RED (구현 부재 ≠ 환경 부재) 위험.

### 4. CFP scope unitary 정합 (ADR-064 §결정 5)

- "mandate 도입" + "33 TC backfill" 양 결정 1 CFP 통합 불가 (CFP-1334 + CFP-FU-1 분리 carrier)
- "ADR layer 결정" (Option A/B/C/D) chief tie-break ladder 3 단계 적용 영역 — RACI lookup → ADR-068 invariant lookup → chief judgement + ADR-086 5-checklist self-app

## 관련 ADR

- **ADR-060** — Evidence-enforceable promotion framework (warning-tier entry primary anchor)
- **ADR-061** Amendment 2 §결정 9 — Production-scale invariant (sibling axis, bash script `set -uo pipefail` + pipe + 가변 input 3-조건 AND)
- **ADR-068** — Boundary completeness invariants (6 invariant cross-ref, chief tie-break ladder Step 2 axis 분석)
- **ADR-068 Amendment 2** — Chief tie-break ladder 3 단계 (Step 1 RACI → Step 2 ADR-068 invariant → Step 3 chief judgement)
- **ADR-068 Amendment 3** — I-6 audit-gate-pointer-existence (retroactive 면제 precedent verbatim)
- **ADR-082 §결정 7** — Per-area 분할 거부 invariant (Option B reject 근거)
- **ADR-086** — Deputy creation decision framework (5-checklist self-app, chief tie-break ladder Step 3)

## 변경 이력

| 일자 (KST) | CFP | 변경 사항 | 작성자 |
|---|---|---|---|
| 2026-05-24 | CFP-1334 | 본 entry 신설 — codeforge governance 어휘 "discriminating fixture mandate" 첫 narrative SSOT (memory `feedback_tdd_red_proof_via_stash` 일반화) | ArchitectAgent (chief author) |

## 참조

- **Carrier Story**: [mclayer/codeforge-internal-docs/blob/main/plugin-codeforge/stories/CFP-1334.md](https://github.com/mclayer/codeforge-internal-docs/blob/main/plugin-codeforge/stories/CFP-1334.md) (post-merge)
- **Change Plan**: [mclayer/codeforge-internal-docs/blob/main/plugin-codeforge/change-plans/cfp-1334-bats-red-green-proof.md](https://github.com/mclayer/codeforge-internal-docs/blob/main/plugin-codeforge/change-plans/cfp-1334-bats-red-green-proof.md) (post-merge)
- **Memory source**: `feedback_tdd_red_proof_via_stash` (CFP-750 2026-05-16 applied evidence, single instance pattern_count = 1)
- **Sibling retro source**: [mclayer/codeforge-internal-docs/blob/main/plugin-codeforge/retros/2026-05-23-cfp-1302.md §5 F4](https://github.com/mclayer/codeforge-internal-docs/blob/main/plugin-codeforge/retros/2026-05-23-cfp-1302.md)
- **외부 vocabulary**:
  - Kent Beck, *Test-Driven Development by Example* (2002) — RED → GREEN → REFACTOR canonical cycle
  - Google Testing Blog "How to Write a Test (and What Not to Do)" — Vacuous green anti-pattern reference
  - SE@Google book ch.11 Test Doubles — Test discipline foundation
  - Pro Git book §7.3 — `git stash` mechanism cross-platform semantics
  - Mutation testing tools: mutmut (Python) / PIT (Java) / Stryker (JavaScript) — discriminating fixture industry parallel
