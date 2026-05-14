---
adr_number: 20
title: Cross-repo Epic 패턴
date: 2026-05-02
status: Accepted
category: orchestration
carrier_story: CFP-60
supersedes: null
superseded_by: null
is_transitional: false
---

# ADR-020: Cross-repo Epic 패턴

## 상태

Accepted (2026-05-02)

## 컨텍스트

mctrader 6-repo 의 첫 cross-repo Epic (MCT-12) 진행 시 현재 wrapper SSOT (CLAUDE.md "1 Story = 2 PRs" + playbook §3) 가 단일 repo 가정 — cross-repo PR sequencing / contract version sync / Story file location / merge 순서 / rollback 절차 부재.

Codex audit (2026-05-02, gpt-5.5 high) #6 FAIL: "retrospective 발견은 계약 불일치와 임시방편 PR 순서를 초래함. proactive 권장 — CFP-60 선행".

## 결정

### 결정 1: Epic owner repo 자유 결정 + 도메인 ADR collocate

cross-repo Epic 의 parent Issue 위치 = consumer 가 명시. wrapper 강제 X.

- doc-only hub repo 권장 (예: mctrader-hub)
- consumer 가 `epic_owner_repo` field 로 명시 의무
- **Epic owner repo = consumer 의 doc-only hub 일 경우, 도메인 ADR 도 같은 repo 에 collocate** (single source of truth — cross-repo 도메인 결정의 분산 방지)
- **EPIC-RESULTS 파일 canonical location** = [ADR-041](ADR-041-doc-location-registry.md) / [`docs/doc-locations.yaml`](../doc-locations.yaml) `epic_results` row 참조 (Mode A → owner / Mode B/C → hub / dogfood → internal-docs `<plugin-folder>/retros/`).

### 결정 2: Child Story 위치 = 작업 repo 자체 + Epic Issue body link 수집

각 작업 repo 의 `docs/stories/<KEY>.md` 자체 보유 (consumer default). dogfood-out 정책 (ADR-013) 은 codeforge family 만 적용 — consumer 자유.

- **Parent Epic Issue body** = child Story Issue 들의 `<owner>/<repo>#<issue>` link 모음 보유 (Epic 진행 추적의 single entry point)
- 예: `mclayer/mctrader-hub#11` (Epic) body 에 `mclayer/mctrader-market#1`, `mclayer/mctrader-market-bithumb#1`, ... link 5 개

### 결정 3: Story §1 메타 에 `epic_dependencies` field 추가 (optional)

Format:

```yaml
epic_dependencies:
  - type: hard_block | design_parallel | impl_parallel
    target: <KEY>
    repo: <owner/repo>
```

Type 정의:
- `hard_block`: blocking dependency (target merge 전 본 Story 작업 불가)
- `design_parallel`: 설계 동시 진행 가능 (구현은 target 후)
- `impl_parallel`: 구현 동시 진행 가능 (target merge 와 무관)

### 결정 4: Change Plan §3 contract 버전 고정 의무

Consumer Story 의 Change Plan §3 에 명시:

```yaml
consumes:
  <producer-repo-or-package>: <SemVer-range>
```

예: `mctrader-market: ^1.0.0`. Producer repo 의 SemVer release tag 와 align.

### 결정 5: Topological merge order (PMOAgent enforce)

Dependency graph 의 topological order 따라 merge. PMOAgent Epic 진행 시 enforce — `hard_block` 위반 detected 시 Epic 차단.

### 결정 6: Rollback 룰

Producer repo merge 후 consumer 가 break 시:
1. Producer revert PR open
2. 모든 affected consumer 의 contract 버전 하향 고정 PR open
3. Producer 가 fix 후 새 minor SemVer release
4. Consumer 버전 고정 갱신

### 결정 7: 단일 repo Story (cross-repo 아닌) 적용 룰

본 결정들 모두 backward compatible — 단일 repo Story (예: CFP-1 ~ CFP-59) 는 `epic_dependencies: []` + `epic_owner_repo: null` 명시 (또는 omit, default 동일 효과).

## 거부된 대안

### 대안 A: 1 Story = N PR across N repos

- 단일 Story 가 N repo 의 PR 모두 reference
- 거부 사유: codeforge wrapper 의 "1 Story = 2 PRs" 패턴 깨짐. 기존 lane progression 메커니즘과 충돌. PR scope 분리 어려움

### 대안 B: Cross-repo Story 통합 monorepo 강제

- 모든 cross-repo 작업을 monorepo 로 강제
- 거부 사유: consumer 자유 침해. mctrader 의 6 repo 분리 의도 (market interface 별도 repo 등) 와 충돌

### 대안 C: PR sequencing 자동화 (GitHub Actions)

- Producer PR merge 시 consumer PR 자동 업데이트 / merge
- 거부 사유: 본 CFP-60 scope 초과. 향후 별도 CFP 후보 (CFP-NN — auto-sequencing)

## 결과

- mctrader Epic MCT-12 진행 가능 (5 child Story MCT-13 ~ MCT-17)
- 단일 repo Story 영향 없음 (backward compatible)
- 향후 plugin family 외 consumer 도 cross-repo Epic 진행 가능

## Amendment 1: Centralization mode 명시 (CFP-81, 2026-05-04)

### 컨텍스트

mctrader debut audit (Issue [#181](https://github.com/mclayer/plugin-codeforge/issues/181) P1-2) 발견:

- ADR-020 v1 §결정 2 default = "각 작업 repo 의 `docs/stories/<KEY>.md` 자체 보유"
- mctrader 실제 = `mctrader-hub` 가 모든 Story file 보유 (MCT-1 ~ MCT-54). implementation repo (`mctrader-engine` / `mctrader-web` / `mctrader-market-bithumb`) 의 `docs/stories/` 디렉터리 부재
- 즉 mctrader 는 **hub-centralized Story 모드** 채택 — ADR-020 v1 default 와 정반대 패턴 운영 중

ADR-020 v1 §결정 2 가 single mode 만 가정 → 다음 cross-repo consumer 가 잘못된 default 채택 risk.

또한 §거부된 대안 A "1 Story = N PR across N repos" narrow form (MCT-26 의 data#1 + engine#1 joint Phase 2) 가 실제 현장 사용 — 거부 사유 부분 reconsider 필요.

### 결정 8: Centralization mode 명시 (Mode A vs Mode B)

cross-repo Epic 진행 시 child Story file 위치 = 두 모드 중 consumer 가 명시:

#### Mode A: Repo-local (per-repo Story) — ADR-020 v1 default

- 각 작업 repo 의 `docs/stories/<KEY>.md` 자체 보유
- 채택 조건:
  - Implementation repo 가 자체 storyboard / governance lifecycle 운영
  - Repo 별 자율 release cycle 유지 의도
  - Hub repo 가 별도 존재하지 않거나 doc 책임 미가짐
- backward compat 유지 — CFP-1 ~ CFP-59 + 단일 repo Story 모두 본 모드

#### Mode B: Hub-centralized (governance hub Story)

- 1 governance hub repo 가 모든 child Story file 보유
- Implementation repo 는 code PR 만 보유 — `docs/stories/` 디렉터리 부재
- 채택 조건:
  - Hub 가 doc-only governance repo (예: `mctrader-hub`)
  - Cross-repo 도메인 ADR collocate (§결정 1 hub-centralize 권장과 자연스러운 pair)
  - Story 단위가 multi-repo 영향을 frequent — 단일 location 추적 가치 큼
- mctrader 실제 채택 패턴 (MCT-1 ~ MCT-54)

#### Mode 선택 기준

| 상황 | 권장 모드 |
|---|---|
| Doc-only hub repo 존재 + 도메인 ADR collocate | **Mode B** |
| Implementation repo 가 N (3+) 개이며 모두 활성 | **Mode B** (단일 truth) |
| Implementation repo 가 ≤ 2개이며 자체 doc 책임 보유 | Mode A |
| Plugin family 자체 dogfood (CFP-* Story) — internal-docs SSOT | (별도 ADR-013 dogfood-out 우선, 본 결정 미적용) |

**조건 충돌 시 우선순위** (예: doc-only hub 존재 + impl repo ≤ 2개):
1. **Mode B 우선** — Doc-only hub 존재 자체가 governance ownership 명시. Impl repo 수와 무관하게 hub 가 single truth 역할 수행.
2. Mode B 채택해도 impl repo 가 자체 doc 책임 추가 보유 시 ADR-013 dogfood-out 정책 별도 검토 (codeforge family 만 적용).

#### Mixed-mode 금지

단일 Epic 내 mode 혼합 (일부 child Story = Mode A + 일부 = Mode B) **불허**. Epic owner repo 결정 시 함께 mode 결정 + 모든 child 일관 적용. 다른 Epic 은 다른 mode 가능.

#### Mid-Epic 신규 repo 추가 시 처리 (Codex P1 #2 응답)

Epic 진행 중 (Phase 1 PR merged 후) 신규 repo 가 child Story scope 에 추가될 경우:

- **기존 mode 유지 의무** (default): Epic 가 Mode B 면 신규 repo 도 hub 에 Story file 작성 (자체 `docs/stories/` 신설 X). Epic 가 Mode A 면 신규 repo 자체 `docs/stories/` 신설.
- **Mode 전환 절차**: 기존 mode 와 양립 불가능한 경우 (예: 신규 repo 가 자체 governance 책임 보유 의무) — 다음 중 택 1, **consumer 명시 ESCALATE 의무**:
  1. **Epic 분할** (권장): 기존 mode child Story 까지 close + 신규 repo 포함 신규 Epic open (다른 mode)
  2. **Epic 재시작**: Epic Issue close + 신규 mode 로 새 Epic — 기존 진행 분 archive
- Default = mode 유지. ESCALATE = consumer 가 mid-Epic restructure 명시 결정.

#### §결정 8 ↔ §결정 7 backward compat 검증 (Codex P2 응답)

§결정 7 ("단일 repo Story 적용 룰" — `epic_dependencies: []` + `epic_owner_repo: null`) 은 **Mode A의 single-Story sub-case** 에 해당. §결정 8 도입으로 변경 없음 — 단일 repo Story 는 amendment 1 영향 0 (Mode 결정 trivial = `null`).

### 결정 9: §거부된 대안 A — Joint-phase narrow form 허용

§거부된 대안 A "1 Story = N PR across N repos" 의 narrow form 재허용:

- **Joint-phase 패턴**: 단일 Story 가 1 phase 안에서 multiple repo 의 joint PR 보유 가능
- 조건:
  - 모든 PR 가 동일 Story key reference (PR title / commit footer)
  - Phase 1 PR 1개 (doc, hub 또는 owner repo) 단일 — 변경 없음
  - Phase N implementation PR 가 multi-repo 가능 (foundation Story 의 data + engine 동시 변경 등)
  - PR merge 순서는 dependency graph topological order
- mctrader MCT-26 (data#1 + engine#1 joint Phase 2) = 본 narrow form 사용 사례

#### Narrow form vs Full form — §대안 A 거부 사유 ("PR scope 분리 어려움") 의 재해석 (Codex P1 #3 응답)

§대안 A v1 거부 사유 "PR scope 분리 어려움" 은 **monolithic Story** 가정 하 정확:
- 1 Story 가 **wide scope** (예: 5 repo 의 모든 변경 1 Story 에 cluster) → reviewer 가 어떤 PR 를 어떤 lane 으로 review 할지 모호 → lane progression 추적 불가
- PR scope = "이 PR 가 어떤 Story 의 어떤 phase 를 진행하나" — 모호하면 lane gate 적용 못함

**Narrow form 은 본 거부 사유 해소**:
- 1 Story = 단일 logical scope (foundation / kill-switch / dashboard 등 single concern)
- Joint Phase N PR 들 = **모두 동일 Story key + 동일 phase 라벨** — lane gate 동일 적용
- topological merge order = dependency graph 명시 → reviewer 가 merge 순서 deterministic
- PR scope 모호성 = 0 (각 PR 가 독립 review 가능, joint = 단일 Story 의 multi-repo joint 임을 명시)

따라서 narrow form (single-scope Story 의 multi-repo PR) 은 §대안 A 거부 사유와 양립.

§거부된 대안 A **full form** ("Story 가 모든 repo 의 PR 1개씩 가지는 monolith Story") = 여전히 거부:
- Wide-scope Story 는 child Story 분할 권장 (예: MCT-25 → MCT-26~30 5 child 분할)
- 1 Story 안의 PR 이 5+ repo = lane progression 추적 불가
- 본 거부 = full form / wide-scope 만 적용. narrow form / single-scope 은 결정 9 로 허용.

### 결정 10: 영향 받는 doc 갱신

- `docs/consumer-guide.md` §3.4 = mode 선택 안내 추가 (본 amendment 동반 PR)
- 본 ADR §관련 파일 = consumer-guide §3.4 mode 안내 명시
- `requirements-output-v1` schema = **변경 없음** (mode 는 Epic Issue body / Story file 위치 자체로 observable, frontmatter 새 필드 불필요)

### Backward compatibility

- ADR-020 v1 default = Mode A — 기존 Story (CFP-1 ~ CFP-59 + 단일 repo) 영향 없음
- mctrader 는 사후 Mode B 명시 (본 amendment merge 후 hub README / governance doc update)
- 기존 §대안 A 거부 사유 narrow form 만 reconsider — full form 거부 유지

## 해소 기준

N/A — permanent policy

## 관련 파일

- [`CLAUDE.md`](../../CLAUDE.md) (cross-references update)
- [`docs/consumer-guide.md`](../consumer-guide.md) §3.4 (mode 선택 안내 — Amendment 1)
- [`docs/orchestrator-playbook.md`](../orchestrator-playbook.md) §3 (cross-repo Epic 섹션 신설)
- [`docs/inter-plugin-contracts/requirements-output-v1.md`](../inter-plugin-contracts/requirements-output-v1.md) (epic_dependencies field 추가)
- [`docs/inter-plugin-contracts/label-registry-v1.md`](../inter-plugin-contracts/label-registry-v1.md) (audit:* + category:* label 추가)
- [ADR-013](ADR-013-codeforge-family-dogfood-out-policy.md) (dogfood-out policy — consumer 자유 결정 root)
- [ADR-021](ADR-021-phase-gap-measurable-signal.md) (phase-gap measurable signal — debut-audit triage 의 한 축)

## Amendment 2 (2026-05-05, CFP-122) — Mechanical Epic mode

### 컨텍스트

CFP-120 (`.gitattributes` standard + `bootstrap-codeforge-family.sh`) 회고에서 발견 — codeforge family 의 일부 wrapper-driven Epic 은 Phase 2-7 가 **mechanical batch** (모든 lane 동일 content apply) 로 진행. CFP-120 Phase 2-7 = 단일 `cfp-120-gitattributes` branch 6 lane plugin apply, 동일 commit message, child Story Issue 별도 발행 안 함. CFP-121 Phase 2 = 단일 lane (codeforge-review) typo fix, child Story Issue 없음. ADR-020 v1 + Amendment 1 의 Mode A / Mode B 가 본 패턴 cover 안 함.

### 결정

#### Mode C: Mechanical Epic (NEW Amendment 2)

본 mode 는 Mode B (hub-centralized) 의 special case 로:

1. **wrapper repo (또는 owner repo) = Epic owner** (Mode B 와 동일)
2. **Phase 2-N child PR 가 동일 mechanical content** — 모든 lane plugin 에 같은 file copy + 동일 commit message + 동일 acceptance criteria
3. **별도 child Story Issue 미발행** — parent Epic Story 가 Phase 2-N 모두 cover (단일 Story §11 에 N PR link 모음)
4. **별도 child spec / plan / change-plan 미발행** — parent Epic 의 spec/plan/change-plan 가 Phase 2-N 변경 enumerate (§5 변경 영향 표에 모든 lane row 명시)
5. **Sonnet decider 무발화** — substantive choice 없음, mechanical apply 만

#### Mode C 적용 기준 (4 조건 AND)

본 mode 로 진행 가능 한 기준:
- (a) Phase 2-N 모든 PR 의 file content 동일 (mechanical copy)
- (b) Phase 2-N 모든 PR 의 acceptance criteria 동일
- (c) substantive choice / option-formulation / FIX root-cause 없음 (Sonnet decider trigger 5종 어디에도 해당 없음)
- (d) parent Epic 의 §5 변경 영향 표에 모든 lane row enumerate (transparency)

위 4 조건 중 1 개라도 불충족 시 Mode B 사용 (각 lane child Story Issue + 별도 spec/plan).

#### Mode 식별 marker

Phase 2-N PR body / Story file frontmatter 에 명시:
```yaml
mode: mechanical
parent_epic: <CFP-NNN>
mechanical_apply: true
```

PR title 에 `(Phase X of <CFP-NNN> Epic)` 명시 (Mode B 와 동일 형식).

#### Mode C 의 advantage

- **Token / time saving**: child Story Issue 5-7개 발행 + close 절차 생략. CFP-120 = 6 child Story 생략으로 ~15분 절약 (estimate).
- **단일 Story = 단일 truth**: Phase 2-N 진행 상황 추적이 1 Story §9 에 누적, 분산 추적 부담 감소.
- **Mechanical 명시**: substantive 결정 없음을 marker 로 명시 → 향후 Sonnet decider 무발화 audit trail 보존.

#### Mode C 의 risk

- **부주의로 substantive 차이 발생** — mechanical 가정으로 진행했는데 한 lane 만 다른 행동 필요한 경우. 완화: Mode C 검증 시점 = parent Epic 의 §3 도입할 설계 작성 직후 (Sonnet 무발화 직전 PL 가 4 조건 (a)~(d) 점검 의무).
- **Audit trail thin** — child Story 부재로 Phase 2-N 별 review log 분산 보존 안 됨. 완화: parent Story §9 에 N row 누적 (lane 별 1 row), §11 에 N PR link 모음.

### 적용 사례 (post-hoc, Amendment 2 ratification)

본 Amendment 가 land 되기 전에 이미 Mode C 로 진행된 사례:
- **CFP-120 Phase 2-7**: 6 lane × `.gitattributes` mechanical copy. 본 Amendment 2 가 사후 SSOT 화.
- **CFP-121 Phase 2**: codeforge-review 단일 lane typo fix. parent Epic 의 §5 표에 lane row 1 명시. condensed Mode C.

### 거부된 대안

- **Per-lane sub-CFP 강제 (Mode B strict)** — 모든 lane 작업 = 별도 CFP. CFP-120 같은 mechanical Epic 에 child Story Issue 6+ 발행 → token / time waste. 단일 truth 보존 어려움.
- **Mode 자유 (no mode marker)** — Mode A vs B vs C 명시 안 함. drift / audit difficulty.

### Backward compatibility

- ADR-020 v1 + Amendment 1 의 Mode A / Mode B 영향 없음 — Mode C 는 new addition.
- 기존 mechanical CFP (CFP-120, CFP-121) post-hoc Mode C ratification — Amendment 2 merge 후 EPIC-RESULTS doc 의 mode marker 갱신 가능 (선택).

### 결정 11: ADR-020 Amendment 2 effective date

본 Amendment 2 = CFP-122 Phase 1 PR merge 직후 effective. 향후 mechanical Epic 은 Mode C 명시 + 4 조건 점검 의무.

## Amendment 3 (2026-05-09 — CFP-342)

### 컨텍스트

[ADR-069](ADR-069-multi-repo-story-key-system.md) (Multi-Repo Hierarchical Story Key System) 가 본 ADR Mode B (hub-centralized) 의 **implementation backbone** 역할 도입. ADR-020 Amendment 1 §결정 8 Mode B 가 manual 운영하던 Story file 위치 결정 / counter 발급 / hub-impl bidirectional linking 을 codeforge plugin 의 `project.yaml` 단일 블록 declare 로 자동화.

### Cross-reference

- **Mode B 활성화 = `project.yaml` 의 `codeforge.stories.repos[]` 블록 선언** (ADR-069 §결정 1)
- **`delegates[]` frontmatter = Mode B 의 hub story → impl repo story 위임 링크** (ADR-069 §결정 2)
- **Counter 메커니즘 = Mode B 의 자동 번호 발급 layer** (`.codeforge/counters.json`, ADR-069 §결정 3)
- **§결정 9 Joint-phase narrow form** = ADR-069 hub story `delegates[]` 다중 entry 로 자연스럽게 표현 (예: `mctrader-data#MCT-001` + `mctrader-engine#MCT-002` 가 hub `mctrader-hub#MCT-112` 의 joint Phase 2)

### 영향

- 본 ADR-020 §결정 1-11 본문 변경 **0** (단순 cross-ref 단락)
- Mode A (repo-local) default 유지 — ADR-069 opt-in 으로 single-repo consumer / 기존 CFP-1~CFP-59 영향 0
- Mode C (mechanical Epic) 와 직교 — ADR-069 hub story 는 substantive carrier, Mode C 는 child Story Issue 미발행 mechanical batch
- 상세: [ADR-069](ADR-069-multi-repo-story-key-system.md)

