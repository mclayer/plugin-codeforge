---
adr_number: 76
title: 선언적 reconciliation upgrade flow SSOT
status: Active
category: governance
date: 2026-05-15
is_transitional: false
carrier_story: CFP-701
parent_epic: CFP-699
supersedes: []
amends: []
amendment_log: []
related_stories:
  - CFP-701  # 본 Story carrier — Wave 1 Story-1 (A1+B1 scope)
  - CFP-702  # Wave 1 Story-2 (D4 customization marker — sequential prerequisite for Wave 2)
  - CFP-743  # Wave 2 Story-3 (UpgradeAgent + CLI runtime carrier) — KEY 정정 CFP-703→CFP-743 (CFP-743, Wave 1 작성 시점 placeholder drift / 동일 Story / fact 영향 0)
related_adrs:
  - ADR-027  # Consumer adoption protocol (boundary disjoint — detection layer)
  - ADR-053  # 구조적 변경 재구동 + consumer 배포 (transaction completion prerequisite)
  - ADR-067  # FIX ledger RESET (disjoint layer — Story progression layer vs upgrade transaction layer)
  - ADR-038  # SessionStart hook static invariant (detect/execute boundary)
  - ADR-016  # Marketplace registration policy (codeforge family 7 plugin atomic unit)
  - ADR-008  # Inter-plugin contract versioning (reconcile-protocol-v1 v1.0 신규)
  - ADR-010  # Inter-plugin contract sibling sync (kind:registry sibling sync 면제)
  - ADR-058  # ADR sunset criteria mandate (is_transitional: false 정합)
  - ADR-064  # Decision principle mandate (derived default + forbid-list + parallel)
  - ADR-039  # Orchestrator subagent default (UpgradeAgent Story-3 영역 정합)
  - ADR-040  # Worktree convention + Amendment 3 §결정 7.D self-app invariant
  - ADR-050  # Parallel epic conflict coordination (ADR-RESERVATION row 76)
  - ADR-065  # ArchitectAgent Phase 1 mechanical sync self-check
  - ADR-068  # Boundary completeness invariants (4 semantic + Amendment 1 I-5 dimensional)
  - ADR-070  # Codex verify-before-trust (Touchpoint #2 carry-over)
  - ADR-073  # Orchestrator verify-before-assert (fact claim marker 5종)
related_files:
  - docs/inter-plugin-contracts/reconcile-protocol-v1.md  # 본 ADR 의 schema carrier (kind:registry)
  - docs/inter-plugin-contracts/MANIFEST.yaml             # registries[] row append
  - docs/domain-knowledge/domain/upgrade-flow/declarative-reconciliation.md  # narrative SSOT anchor
  - CLAUDE.md                                              # GitHub Workflow + ADR 단락 cross-ref
  - docs/orchestrator-playbook.md                          # §3 Lane 실행 cross-ref
mechanical_enforcement_actions: []
# declarative SSOT only — mechanical lint (snapshot file schema lint / contract schema 정합 / 
# upgrade event log artifact lint) = Wave 2 carrier (Story-3 UpgradeAgent + CLI 영역).
# ADR-040 Amendment 3 §결정 7.D self-application invariant 정합 — 빈 list `[]` 가 declarative 
# only Story 영역의 valid declaration.
---

# ADR-076: 선언적 reconciliation upgrade flow SSOT

## 상태

**Active (2026-05-15)** — CFP-701 (Wave 1 Story-1) carrier. parent_epic CFP-699 (declarative reconciliation upgrade Epic).

`is_transitional: false` — permanent architecture invariant. codeforge family upgrade 도메인의 1st-class 정의 anchor.

## 컨텍스트

### 직접 동인 (CFP-699 Epic §1 WHY verbatim)

사용자 directive (2026-05-14 KST):

> 핵심 통증 2가지: (1) 빠짐 — codeforge upgrade 후 consumer 측 영역 누락. (2) 일관성 없음 — 그냥 수행하면 될 만한 것도 어쩔 때는 사용자에게 묻고 어쩔 때는 안 묻고. 진짜 WHY: 두 통증을 하나로 묶으면 = "한 번 명령 = 끝까지 자동 + 사용자 결정은 정해진 자리에서만 (= 0 자리)". 단순 누락 방지가 아니라 결정 트리 자체를 박제 해서 매번 다르게 묻지 않게 하는 일.

### 도메인 갭

codeforge plugin family upgrade 의 architecture pattern 이 ADR / domain-knowledge 어디에도 1st-class 로 정의되어 있지 않다. 현재 self-app partial cover 영역 (CFP-701 Story §2.1 사실 2 verbatim):

- `regen-agents.sh` = agent md `cp -n` (no-clobber) — wrapper 변경분 자동 propagate **불가** (기존 file skip)
- `merge.py` = agent frontmatter deep merge **only** (workflow / hook / label 영역 미적용)
- `check_bootstrap.py` check 10 (CFP-660) = workflow SHA drift **detection only**, propagation 0
- `hooks/session-start` = plain stdout SSOT (filesystem touch 0 + network call 0 invariant, ADR-038 Amendment 3 §결정 12) — hook 자체가 reconcile execution 책임 **불가**

위 partial cover 가 Epic §1 WHY 의 "빠짐" 증상의 mechanical 원인. 1st-class 도메인 정의 부재 → 결정 트리 박제 불가 → 사용자 결정 분기가 매번 다르게 surfacing.

### 본 ADR 영역 (A1 + B1)

- **A1 (self-app SSOT)**: wrapper 자체 영역 enumeration (workflow / hook / label / overlay / settings.json / CODEOWNERS / Issue templates / branch protection) + declarative reconcile 의 자기 적용 semantic
- **B1 (snapshot semantic)**: upgrade transaction 의 pre/post state record semantic SSOT

본 ADR scope 외 (후속 Wave carrier 분리, ADR-067 §결정 4 sequential ordering 정합):

- A2 (7 plugin family atomic upgrade) — Wave 2 Story-4
- A3 (overlay 영역 reconcile 통합 — 3-way merge runtime) — Wave 2 Story-5
- B2 (3-way version atomic invariant 확장) — Wave 3 Story-6
- C1/C2/C3 (dry-run preview runtime / event log artifact / 사후 sanity check) — Wave 2 Story-3
- D1/D2/D3 (Issue/PR template fan-out / branch protection / script boundary) — Wave 3 Story-7
- D4 (customization marker 의무화) — Wave 1 Story-2 (본 Story sequential prerequisite 분리)
- E1/E2/E3 (multi-version channel / codemod registry / uninstall protocol) — Wave 4 sub-Epic

## 결정

### 결정 1 — 선언적 reconciliation 패턴 채택 (Helm-inspired)

codeforge family upgrade = **선언적 reconciliation**. wrapper SSOT = desired state, consumer overlay + plugin install = current state, upgrade 명령 = converge.

3-layer state representation (`docs/domain-knowledge/domain/upgrade-flow/declarative-reconciliation.md` SSOT narrative anchor verbatim):

| Layer | 정의 | 위치 | 책임 주체 |
|---|---|---|---|
| **Desired state** | wrapper SSOT 영역 enumeration | `mclayer/plugin-codeforge` repo + 6 lane plugin repos | wrapper / lane plugin author |
| **Current state** | consumer `.claude/_overlay/` + `.claude/plugins/installed_plugins.json` + `.github/workflows/` + `.github/ISSUE_TEMPLATE/` 등 | consumer repo working tree + plugin install dir | consumer (정상) / drift detector (감지) |
| **Customization layer** | consumer 의 wrapper-managed marker block 밖 영역 — preserved patch layer | consumer overlay / hook / workflow file 안 `# BEGIN/END wrapper-managed` block 외 | consumer (preserve) |

외부 패턴 reference: **Helm** `helm upgrade` (release history revision N pattern, 가장 정합), **Kustomize** overlay (customization layer = marker block 와 conceptually 유사), **Terraform** plan-apply (3-way merge 분기 패턴), **Ansible** `--check` mode (dry-run 패턴). 자세한 비교 표 = domain-knowledge entry `## External pattern reference` § verbatim.

### 결정 2 — Wrapper SSOT 영역 enumeration scheme

wrapper plugin (codeforge) self 영역의 desired state 단위 enumeration (Story-1 A1 scope):

| 영역 | desired state 표현 | reconcile responsibility |
|---|---|---|
| **GitHub workflow** | `templates/github-workflows/*.yml` (template) + `.github/workflows/*.yml` (self-app byte-identical) | mirror — wrapper SSOT 변경 시 byte-identical 갱신 |
| **SessionStart hook** | `hooks/hooks.json` + `hooks/session-start` (plain stdout SSOT, ADR-038 Amendment 3 §결정 12) | template export — consumer overlay 시점 byte-identical mirror |
| **Label taxonomy** | `docs/inter-plugin-contracts/label-registry-v2.md` (SSOT) + `scripts/bootstrap-labels.sh` (consumer-side application) | declare-only — consumer side `bootstrap-labels.sh` 호출 이 mechanical action |
| **Settings.json toggle** | `templates/.claude/settings.json.sample` (consumer reference) + wrapper repo `.claude/settings.json` (dogfood self-app) | template export — consumer overlay merge 시점 적용 |
| **CODEOWNERS** | `templates/CODEOWNERS.template` | template export — consumer 측 manual instantiate (org-specific team list 영역) |
| **Issue templates** | `templates/.github/ISSUE_TEMPLATE/*.yml` | template export — consumer overlay 시점 byte-identical mirror |
| **Branch protection** | `.github/branch-protection-manifest.json` (declarative) | API call required — consumer `gh api` apply (Story-3 carrier 영역) |
| **plugin.json mirrored field** | `name` / `version` / `description` / `author` 4종 (ADR-063 atomic invariant) | atomic — marketplace sync PR 선행 merge 의무 |
| **CHANGELOG.md** | wrapper repo SSOT | append-only — version bump 동반 |

위 9 영역이 wrapper plugin 의 declarative SSOT 단위. 본 enumeration 이 Story-3 carrier (UpgradeAgent + CLI) 의 reconcile target 정의 의 input. 6 lane plugin (codeforge-{requirements,design,review,develop,test,pmo}) 의 self 영역 enumeration 은 ADR-016 family scope 정합 후속 carrier 영역 (본 Story-1 scope 외, Wave 2 Story-4 atomic upgrade carrier).

### 결정 3 — dry-run / snapshot / transaction 3 enum 정의

본 결정이 Epic §1 WHY 의 "결정 트리 박제" 직접 carrier. 3 enum = CLI argument fix 로 사용자 결정 분기 0:

#### dry-run
- **Semantic**: desired state diff current state 계산 + 결과 preview (실 변경 0).
- **Behavior**: 3-way merge (base / wrapper-new / consumer-current) preview 출력 + drift summary report. filesystem touch 0. network call 가능 (Helm-inspired `helm diff` pattern).
- **Scope**: 9 영역 (결정 2 verbatim) 모두 dry-run 가능. consumer customization marker block 안 영역 = preserve 표기. marker block 밖 영역 = wholesale mirror 표기.
- **Invariant**: 사용자 결정 분기 0 (정보 제공만). dry-run 결과 보고 후 사용자가 별도 명령 (`--apply` / `--rollback` / abort) 으로 진행.

#### snapshot
- **Semantic**: upgrade transaction 의 pre-state sentinel — rollback 의 입력 state.
- **Behavior**: `--apply` 직전 자동 생성. consumer-side `.claude/_snapshots/<UTC-timestamp>-<version-pre>.tar.gz` (또는 동등 archival) + upgrade event log artifact (`docs/upgrade-events/<date>-<version>.md` — Wave 2 Story-3 영역 file schema).
- **Granularity**: 9 영역 (결정 2) union — wrapper SSOT 영역 + consumer customization marker block 외 영역. marker block 안 customization 영역은 snapshot scope 외 (consumer responsibility preserve).
- **Persistence location**: consumer `.claude/_snapshots/` (primary) + wrapper `docs/upgrade-events/<date>.md` (event log mirror, audit trail). git tag 영역 보조 (Wave 4 multi-version channel E1 carrier).
- **Lifecycle / retention**: N most-recent (default `N=5` `[empirical-source: derived default — Helm release history N=10 보다 보수적, codeforge family scope 7 plugin × N=5 = 35 file 보존 비용 vs rollback 가용성 절충, FIX iter 1 / Codex TP#2 F-002 annotation]`, configurable via consumer `.claude/_overlay/project.yaml` `upgrade.snapshot_retention_count`). per-MAJOR-version retention 영역은 Wave 4 E1 carrier.
- **Invariant**: `--rollback <version>` 시 동일 snapshot scope re-application. snapshot 자체 = state migration unit (data migration 영역, ADR-007 정합).

#### transaction
- **Semantic**: upgrade 의 atomic unit. snapshot 생성 → apply → 사후 sanity check 까지 단일 unit.
- **Behavior**: `--apply` 명령의 atomicity boundary. 부분 실패 시 자동 rollback (snapshot 복원). 사후 sanity check 실패 시 자동 rollback.
- **Atomicity boundary — 의미 invariant vs runtime implementation 분리** (FIX iter 1 / Codex TP#2 F-001 re-frame, 2026-05-15 KST):
  - **의미 invariant**: `family_7_plugin_atomic` — ADR-016 §결정 1 정합 (wrapper + 6 lane plugin = 7 plugin atomic unit). 본 invariant 자체는 본 ADR-076 신설 영역 외 (ADR-016 이미 SSOT). 본 ADR-076 = 위 invariant 의 reconcile-protocol 시점 declare carrier. domain-knowledge `upgrade-flow/declarative-reconciliation.md` Invariant 3 verbatim 정합.
  - **runtime v1.0 implementation**: `per_plugin` (Story-1 scope semantic SSOT only). 실 runtime carrier = Wave 2 Story-3 (UpgradeAgent + CLI) — per-plugin atomic unit. 본 Story-1 = invariant declare + per-plugin runtime semantic 분리 명시.
  - **runtime future (Wave 2 Story-4 ratchet — CFP-744 ACTIVE)**: `family_7_plugin` runtime carrier (`scripts/atomic-upgrade-7-plugins.sh` 신설 시점) — 의미 invariant 와 runtime 일치점. 본 시점 reconcile-protocol-v1.md MINOR bump **v1.2 → v1.3 (Wave 2 Story-4, CFP-744)** + ADR-037 Amendment 1 (atomic upgrade 후 0 drift invariant) carrier 동반. [stale placeholder 정정: 旧 text "v1.0 → v1.1 의무" = Wave 1 (CFP-701) 작성 시점 placeholder (v1.1 CFP-702 / v1.2 CFP-743 신설 전 작성된 stale text) → 실제 v1.2 → v1.3 정정. CFP-743 CFP-703→CFP-743 정정 패턴 답습, fact 영향 0 추적성만 — ADR-068 I-4 wording SSOT 정합. 의미 invariant `family_7_plugin_atomic` 변경 0 (ADR-016 §결정 1 SSOT — runtime catch-up only).]
  - per-file atomicity = too granular (rollback 빈번) — runtime 영역 제외.
- **Completion criterion**: ADR-053 §D2 cross-ref. **verbatim quote** (FIX iter 1 / Codex TP#2 F-004 re-frame, 2026-05-15 KST):

  > 해당 구조적 변경이 codeforge plugin 자체의 변경인 경우, 재구동 범위에 consumer 배포 완료가 포함된다. consumer 배포 완료 전에는 consumer Story 작업 진입이 차단된다.

  **본 ADR-076 interpretation note** (verbatim ≠ interpretation 분리): "consumer 배포 완료" 의 mechanical 충족 = (a) marketplace sync PR open · merge 완료 (ADR-016 mirrored field 4종 atomic — ADR-063 §결정 5) AND (b) consumer install 완료 (`/plugins install codeforge@mclayer` verbatim 명령 또는 동등 effect UI / script — 예: VSCode `Claude Code: Install Plugin` UI / npm `install` script 등) AND (c) `bash scripts/check-codeforge-version-drift.sh` PASS (no drift). 본 3 조건 AND 충족 = transaction 의 atomic unit 완결.
- **Invariant**: 사용자 결정 분기 0. `--apply` 단일 명령으로 snapshot + apply + sanity 모두 자동 진행.

### 결정 4 — Snapshot ↔ ADR-067 RESET disjoint layer invariant (AC-4 carrier)

**같은 단어 "RESET" 이 다른 layer 에서 다른 의미**. 본 invariant 가 boundary completeness gap (ADR-068 §결정 1 I-2 cross-module propagation completeness) 회피의 핵심 anchor.

| Concept | Layer | 정의 | 위치 |
|---|---|---|---|
| **ADR-067 RESET** | Story progression layer | Story §10 FIX Ledger 의 `RESET?` column 마커 (`RESET <lane>` / `cross-lane-pause:<lane>`) — lane FIX cycle 의 cycle 재시작 표기 | `<internal-docs>/wrapper/stories/<KEY>.md §10` row |
| **본 ADR-076 snapshot** | Upgrade transaction layer | upgrade 의 pre-state sentinel — rollback 의 입력 state | consumer `.claude/_snapshots/` + wrapper `docs/upgrade-events/` |

**두 개념 disjoint** — cross-pollinate 금지. 본 ADR §결정 본문 + `reconcile-protocol-v1` contract schema + `docs/domain-knowledge/domain/upgrade-flow/declarative-reconciliation.md` Invariant 2 verbatim — 3 곳 모두 명시적 분리 declare 의무. AC-4 의 PASS criterion 다층화.

ADR-067 §결정 4 cross-lane RESET 정책 (Pause-and-resume) = Story progression 영역의 FIX cycle artifact. 본 ADR-076 snapshot = Story 외 layer, lane progress 무관, codeforge plugin self/consumer state 의 sentinel.

### 결정 5 — Reconcile execution 책임 SSOT 분리 (SessionStart hook ≠ UpgradeAgent ≠ CLI)

3 책임 분리 (ADR-038 Amendment 3 §결정 12 + ADR-039 default subagent context 정합):

| 책임 주체 | 역할 | 위치 |
|---|---|---|
| **SessionStart hook** (`check_bootstrap.py` + `check-codeforge-version-drift.sh`) | **Detect only** — filesystem touch 0 + network call 0 invariant | `hooks/session-start` (plain stdout SSOT) |
| **UpgradeAgent** (Wave 2 Story-3 carrier) | **Plan + Apply** — dry-run preview + state reconciliation execution + sanity check + event log artifact | `templates/agents/UpgradeAgent.md` (Story-3 carrier 영역) |
| **CLI** (`scripts/codeforge-upgrade.{sh,ps1}`) | **단일 진입점** — POSIX + PowerShell cross-platform user-facing command | `scripts/codeforge-upgrade.sh` + `.ps1` (Wave 2 Story-3 carrier) |

본 결정 = Story-3 carrier prerequisite cross-ref. 본 Story-1 = semantic SSOT only — UpgradeAgent md / CLI script 자체는 Wave 2 carrier (src/tests 변경 0건 의무).

### 결정 6 — Customization preservation entry = marker block (Story-2 prerequisite cross-ref)

consumer customization preservation 의 entry = `# BEGIN wrapper-managed` / `# END wrapper-managed` marker block (D4, Wave 1 Story-2 carrier).

**본 ADR scope (Story-1)**: contract `reconcile-protocol-v1` 안 `customization_preservation_entry: marker_block` field declare + marker block 부재 영역 fallback behavior 명세 (`marker_block_absent_behavior: wholesale_mirror_with_user_visible_loss_report`).

**Story-2 carrier scope**: marker syntax 정의 + lint script + migration script (retroactive marker wrap) + workflow.

본 Story-1 의 contract field declare = Story-2 의 sequential prerequisite. Story-2 진입 시점 본 Story-1 merge 완료 의무 (Wave 1 sequential ordering, Epic spec §8 의존 순서).

### 결정 7 — Transaction completion criterion = ADR-053 D2 prerequisite (verbatim quote + interpretation note 분리)

본 ADR §결정 3 transaction completion (atomic unit 완결) = ADR-053 §D2 (codeforge 변경 시 consumer 배포 포함) 의 prerequisite 가 충족된 시점.

**ADR-053 §D2 verbatim quote** (FIX iter 1 / Codex TP#2 F-004 — verbatim quote 우선, 동등 phrasing weakening 차단):

> 해당 구조적 변경이 codeforge plugin 자체의 변경인 경우, 재구동 범위에 consumer 배포 완료가 포함된다. consumer 배포 완료 전에는 consumer Story 작업 진입이 차단된다.

**본 ADR-076 interpretation note** (verbatim ≠ interpretation 분리 — Codex TP#2 F-004 mitigation):

"consumer 배포 완료" 의 mechanical 충족 = 다음 3 조건 AND:
- (a) marketplace sync PR open · merge 완료 (ADR-016 mirrored field 4종 atomic — ADR-063 §결정 5)
- (b) consumer install 완료 — verbatim 명령 `/plugins install codeforge@mclayer` 또는 동등 effect (예: VSCode `Claude Code: Install Plugin` UI / npm `install` script 등 동일 effect)
- (c) `bash scripts/check-codeforge-version-drift.sh` PASS (no drift)

위 3 조건 모두 AND 충족 = transaction 의 atomic unit 완결. 미충족 시 다음 Story 작업 진입 차단 (ADR-053 §D2 의 blocking semantic 보존).

**dogfood-out 영역 (codeforge 자체 변경)** = consumer 배포 후 transaction completion detection. 본 wrapper plugin Story (예: CFP-701) Phase 1 PR merge 후 marketplace sync PR + consumer install + drift check 3 prerequisite 가 transaction completion criterion 으로 작동. 이는 CFP-701 Story §5 AC-5 의 PASS criterion 정합.

### 결정 8 — Atomicity unit semantic invariant vs runtime implementation 분리 (Story-1 scope)

ADR-016 §결정 1 정합 — wrapper + 6 lane plugin = 7 plugin atomic unit (의미 invariant SSOT). 본 ADR-076 §결정 3 transaction 영역 atomicity_boundary 는 **의미 invariant vs runtime implementation 두 영역 분리 declare** (FIX iter 1 / Codex TP#2 F-001 re-frame):

| 영역 | 정의 | 본 Story-1 시점 | Wave 2 Story-4 시점 |
|---|---|---|---|
| **의미 invariant** | `family_7_plugin_atomic` (ADR-016 §결정 1 SSOT) | invariant declare (변경 0) | invariant 유지 (변경 0) |
| **runtime implementation** | atomic unit 의 실 mechanical action | `per_plugin` (Story-3 UpgradeAgent + CLI carrier 영역) | `family_7_plugin` (`scripts/atomic-upgrade-7-plugins.sh` 신설 시점) |

**rationale**: 본 Story-1 = semantic SSOT only, runtime 0건. 의미 invariant 자체는 본 ADR-076 신설 영역 외 (ADR-016 이미 SSOT) — 본 §결정 8 = 위 invariant 의 reconcile-protocol 시점 declare carrier. runtime per-plugin / per-family 분리 = Wave별 carrier 분리 (ADR-067 §결정 4 sequential ordering 정합). per-family runtime carrier = Wave 2 Story-4 진입 시점 본 ADR Amendment trigger (ratchet 강화, ADR-058 §결정 5 정합) — 단 ratchet 자체는 invariant 변경 아님 (이미 family_7_plugin invariant, Wave 2 = runtime catch-up).

domain-knowledge `upgrade-flow/declarative-reconciliation.md` Invariant 3 verbatim 정합 — "Codeforge family scope = 7 plugin atomic" 의 reconcile-protocol layer 시점 declare 영역.

## 결과

### 즉각적 결과

1. **`docs/inter-plugin-contracts/reconcile-protocol-v1.md` 신규** — kind:registry, schema field 6종 (`customization_preservation_entry` / `marker_block_absent_behavior` / `version_handshake` / `reconcile_strategy` enum / `snapshot_semantic` / `atomicity_boundary`) + dry-run/snapshot/transaction 3 mode enum + placeholder reserve 영역 (Wave 4 carrier).
2. **`docs/domain-knowledge/domain/upgrade-flow/declarative-reconciliation.md` 신설** — RequirementsPL self-write 이미 완료 (CFP-26 Phase 0a owner agent direct write). 본 ADR § narrative SSOT anchor.
3. **`docs/inter-plugin-contracts/MANIFEST.yaml` registries[] row append** — `reconcile_protocol` entry (v1.0 Active, sibling sync 면제 ADR-010 §결정 2).
4. **`CLAUDE.md` 2 단락 cross-ref** — "GitHub Workflow" + "ADR (`docs/adr/` SSOT)" 단락 ADR-076 1-line cross-ref.
5. **`docs/orchestrator-playbook.md` cross-ref** — §3 Lane 실행 영역 narrative anchor 1-2 line.
6. **`docs/adr/ADR-RESERVATION.md` row 76 append** — CFP-701 carrier, status active, reserved_at 2026-05-15. ADR-050 §결정 1 정합 (ArchitectAgent inline carrier, ADR-070 / CFP-578 precedent — chief author scope 영역).

### 후속 carrier dependency 명시

- **Wave 1 Story-2 (CFP-702)**: customization marker block 도입 — 본 ADR §결정 6 의 sequential prerequisite. 본 Story-1 merge 완료 의무.
- **Wave 2 Story-3 (CFP-743)**: UpgradeAgent + CLI runtime carrier — 본 ADR §결정 5 의 reconcile execution responsibility 분리 정합. (KEY 정정: Wave 1 작성 시점 placeholder `CFP-703` → 실제 발의 Issue `CFP-743`. 동일 Story, fact 영향 0, 추적성만 정정 — ADR-068 I-4 wording SSOT 정합.)
- **Wave 2 Story-4**: 7 plugin atomic upgrade runtime — 본 ADR §결정 8 의 atomicity boundary `runtime implementation` 영역 ratchet carrier (의미 invariant `family_7_plugin_atomic` 자체는 ADR-016 §결정 1 SSOT, 본 carrier 가 runtime catch-up).
- **Wave 2 Story-5**: overlay 3-way merge runtime — 본 ADR §결정 1 의 Kustomize-inspired customization layer reconcile.
- **Wave 4 E1/E2/E3**: multi-version channel / codemod registry / uninstall — 본 ADR `reconcile-protocol-v1` 의 `version_handshake` + `reconcile_strategy` enum placeholder 영역 활용.

### 검증 영역

- **AC-1 (frontmatter + section schema)**: 본 ADR file `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` PASS.
- **AC-2 (reconcile-protocol-v1 MANIFEST entry)**: `check-inter-plugin-contracts.sh` PASS.
- **AC-3 (3 enum 정의 + 외부 reference)**: 본 §결정 3 + Helm/Kustomize/Terraform cross-ref verbatim.
- **AC-4 (snapshot ↔ ADR-067 RESET disjoint phrasing)**: 본 §결정 4 verbatim "disjoint" + "layer" phrasing 보유. 3 곳 cross-ref (ADR / contract / domain-knowledge) 완성.
- **AC-5 (ADR-053 D2 compliance)**: 본 §결정 7 verbatim cross-ref. dogfood-out 영역 면제 분기 명시.

## 해소 기준

**N/A — permanent governance invariant** (`is_transitional: false`).

본 ADR 은 codeforge family upgrade 도메인의 1st-class 정의 anchor — codeforge plugin family 가 deprecate 되지 않는 한 영구 유효. Amendment 는 강화 방향만 허용 (ADR-058 §결정 5 + ADR-064 top-down self-application 정합):

- 새 영역 enumeration 추가 (결정 2 표 row append)
- 새 reconcile_strategy enum 값 추가 (결정 3 placeholder 활성)
- atomicity_boundary runtime implementation ratchet (per-plugin → family_7_plugin — Wave 2 Story-4 carrier 시점, 의미 invariant 변경 0)
- snapshot retention policy 추가 (per-MAJOR-version — Wave 4 E1 carrier 시점)

약화 방향 (예: 사용자 결정 분기 0 invariant 약화 / disjoint layer 합치) = ADR-058 §결정 5 sunset_justification 3-tuple (metric / who / how) 정량 명시 없이 차단. 본 ADR 의 사용자 directive verbatim (CFP-699 Epic §1 WHY "결정 트리 박제") 정합.

## 관련 파일

- `docs/inter-plugin-contracts/reconcile-protocol-v1.md` — 본 ADR 의 schema carrier (kind:registry, v1.0, Active)
- `docs/inter-plugin-contracts/MANIFEST.yaml` — registries[] `reconcile_protocol` row
- `docs/domain-knowledge/domain/upgrade-flow/declarative-reconciliation.md` — narrative SSOT anchor (RequirementsPL self-write)
- `docs/adr/ADR-027-consumer-adoption-protocol.md` — boundary disjoint (detection layer vs upgrade transaction layer)
- `docs/adr/ADR-053-structural-change-restart-prerequisite.md` — transaction completion prerequisite (§결정 7 cross-ref)
- `docs/adr/ADR-067-fix-ledger-implementability-escalation.md` — Story progression layer RESET (§결정 4 disjoint cross-ref)
- `docs/adr/ADR-038-progress-visualization-todowrite.md` — Amendment 3 §결정 12 SessionStart hook static invariant (§결정 5 cross-ref)
- `docs/adr/ADR-016-marketplace-registration-policy.md` — codeforge family scope 7 plugin atomic (§결정 8 cross-ref)
- `docs/adr/ADR-008-inter-plugin-contract-versioning.md` — reconcile-protocol-v1 v1.0 신규 정합
- `docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md` — kind:registry sibling sync 면제 정합
- `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` — is_transitional: false 정합 (해소 기준 § verbatim)
- `docs/adr/ADR-064-decision-principle-mandate.md` — derived default + forbid-list + parallel default 정합
- `docs/adr/ADR-040-worktree-convention.md` — Amendment 3 §결정 7.D self-app invariant (frontmatter `mechanical_enforcement_actions: []` 정합)
- `docs/adr/ADR-050-parallel-epic-conflict-coordination.md` — ADR-RESERVATION row 76 append 의 회피 mechanism
- `docs/adr/ADR-065-architect-phase1-mechanical-self-check.md` — ArchitectAgent Phase 1 commit-time 7-item self-check 정합
- `docs/adr/ADR-068-boundary-completeness-invariants.md` — 4 semantic invariants + Amendment 1 I-5 dimensional empirical grounding 정합
- `docs/adr/ADR-070-codex-verify-before-trust.md` — Touchpoint #2 (ArchitectAgent §3 직후) carry-over 정합
- `docs/adr/ADR-073-orchestrator-verify-before-assert.md` — fact claim marker 5종 정합
- `CLAUDE.md` — "GitHub Workflow" + "ADR" 단락 cross-ref
- `docs/orchestrator-playbook.md` — §3 Lane 실행 cross-ref
- `<internal-docs>/wrapper/stories/CFP-701.md` — 본 ADR carrier Story (Wave 1 Story-1)
- `<internal-docs>/wrapper/change-plans/cfp-701-reconciliation-contract.md` — Phase 1 PR change plan
