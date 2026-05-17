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
amendment_log:
  - amendment: 1
    date: 2026-05-17
    cfp: CFP-906
    summary: "§결정 9 신설 — 3-tier channel taxonomy declaration (Wave 4 sub-Epic #1 Story-1, Epic CFP-882). codeforge family plugin distribution 의 release channel 1st-class 정의 anchor. 3-tier enum (stable / beta / canary) closed-enum invariant + per-tier semantic (LOW / MEDIUM / HIGH risk class) + production-impact awareness (canary tier admin tier 권장 advisory) + channel selection authority asymmetry (SecurityArch §2 T-2.1 silent canary uptake 차단) + sensitive data exposure tier asymmetry (canary tier production features = HIGH exposure, ProductionEvidenceDeputy Story-3 spawn trigger) + disjoint invariant (codeforge.channel.tier release tier ≠ codeforge.version_pin.version specifier — 독립 차원, 동일 block embedding 금지). project-config-schema codeforge.channel field 신설 (peer block, version_pin sibling) + reconcile-protocol-v1 v1.6 → v1.7 §4.3 (i) trigger 발동 + §4.10 multi_version_channel_pin_binding block carrier 동반. ADR-016 Amendment 3 (family_7_plugin_atomic × channel pin invariant) + ADR-063 Amendment 6 §결정 17 (mirrored field × channel matrix) + label-registry-v2 v2.29 → v2.30 (3 channel:* label + 신규 category enum channel) sibling cross-ref. Strengthening direction only — ADR-064 §self-application top-down ratchet 정합 (channel taxonomy = scope 확장, weakening 0). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과 (is_transitional: false 보존)."
    is_transitional: false
    sunset_justification: "N/A — permanent governance invariant. ADR-064 §self-application top-down ratchet 정합 (Amendment 1 = 3-tier channel taxonomy 강화 방향 only, scope 확장 — codeforge family plugin distribution 의 release channel 1st-class declare). ADR-058 §결정 5 약화 방향 발의 차단 logic 통과 (channel taxonomy 축소 / disjoint invariant 합치 = sunset_justification 3-tuple 의무)."
  - amendment: 2
    date: 2026-05-17
    carrier_story: CFP-898  # Wave 4 sub-Epic CFP-858 base layer (S1 — S2 CFP-899 / S3 CFP-900 prerequisite)
    description: |
      §결정 2 enumeration 표 11번째 row append (`scripts/` workflow_dependency_closure, `mode: bundled_with_referencing_workflow`)
      + §결정 6 본문 Amendment 2 sub-section 추가 (의미 invariant `marker_block_absent_behavior: wholesale_mirror_with_user_visible_loss_report` 무변경 + dependency_missing → fail-closed sub-clause). reconcile-protocol-v1 v1.6 → v1.7 MINOR bump (§4.3 (i) trigger + §4.10 `dependency_bundle_integrity_binding` block) 동반.
      Architect lane derived default (ADR-064 §결정 3 룰 1 정합): AM-1 = regex_primary (stdlib only) / AM-2 = transitive_depth_limit=1 / AM-3 = templates/scripts/ location (self-app 면제) / AM-4 = self-loop 0 invariant.
      ratchet 강화 only (ADR-058 §결정 5 + ADR-064 §self-application 정합) — 약화 0건. `mechanical_enforcement_actions: []` declaration-only retain (ADR-082 §결정 6 + ADR-070 §D5 패턴 답습 — Phase 2 PR 시점 `templates/scripts/mirror-dependency-closure.py` self-test 가 mechanical detection 책임).
      `is_transitional: false` 무변경. sunset_justification N/A (permanent governance invariant).
      mctrader-data#81 14 failing checks evidence (Epic CFP-858 §1 motivation verbatim) — wholesale_mirror 시 silent partial bundle 의 real harm 사례.
related_stories:
  - CFP-701  # 본 Story carrier — Wave 1 Story-1 (A1+B1 scope)
  - CFP-702  # Wave 1 Story-2 (D4 customization marker — sequential prerequisite for Wave 2)
  - CFP-743  # Wave 2 Story-3 (UpgradeAgent + CLI runtime carrier) — KEY 정정 CFP-703→CFP-743 (CFP-743, Wave 1 작성 시점 placeholder drift / 동일 Story / fact 영향 0)
  - CFP-906  # Amendment 1 carrier — Wave 4 sub-Epic #1 Story-1 (channel schema SSOT 3-tier taxonomy declare layer, Epic CFP-882)
  - CFP-898  # Amendment 2 carrier — Wave 4 sub-Epic CFP-858 base layer (S1) (§결정 2 11번째 row + §결정 6 fail-closed clause + reconcile-protocol-v1 v1.7 §4.3 (i) trigger 동반)
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
  - ADR-061  # Python script-writing convention (Amendment 1 carrier — 외부 .py 의무)
  - ADR-065  # ArchitectAgent Phase 1 mechanical sync self-check
  - ADR-068  # Boundary completeness invariants (4 semantic + Amendment 1 I-5 dimensional)
  - ADR-070  # Codex verify-before-trust (Touchpoint #2 carry-over)
  - ADR-073  # Orchestrator verify-before-assert (fact claim marker 5종)
  - ADR-063  # Marketplace ↔ plugin.json atomic invariant (Amendment 6 §결정 17 mirrored field × channel matrix carrier sibling — CFP-906 Amendment 1)
  - ADR-72  # ProductionEvidenceDeputy spawn (§결정 1 canary tier production-impact trigger — CFP-906 §결정 9 canary tier semantic cross-ref)
  - ADR-082  # Write-time self-write verification mandate (Amendment 2 / CFP-898 ratchet 강화 패턴 답습)
related_files:
  - docs/inter-plugin-contracts/reconcile-protocol-v1.md  # 본 ADR 의 schema carrier (kind:registry)
  - docs/inter-plugin-contracts/MANIFEST.yaml             # registries[] row append
  - docs/domain-knowledge/domain/upgrade-flow/declarative-reconciliation.md  # narrative SSOT anchor
  - CLAUDE.md                                              # GitHub Workflow + ADR 단락 cross-ref
  - docs/orchestrator-playbook.md                          # §3 Lane 실행 cross-ref
  - templates/scripts/mirror-dependency-closure.py        # Amendment 1 carrier — Phase 2 신설 (closure resolver script, ADR-061 외부 .py 의무 정합)
  - scripts/reconcile-overlay.sh                           # Amendment 1 carrier — Phase 2 hook insertion (line 437 직전, MARKER_NONE branch first-line)
mechanical_enforcement_actions: []
# declarative SSOT only — mechanical lint (snapshot file schema lint / contract schema 정합 / 
# upgrade event log artifact lint) = Wave 2 carrier (Story-3 UpgradeAgent + CLI 영역).
# ADR-040 Amendment 3 §결정 7.D self-application invariant 정합 — 빈 list `[]` 가 declarative 
# only Story 영역의 valid declaration.
# Amendment 2 (CFP-898) declaration-only retain (ADR-082 §결정 6 + ADR-070 §D5 패턴 답습) —
# Phase 2 PR 시점 `templates/scripts/mirror-dependency-closure.py` self-test 가 mechanical detection 책임.
---

# ADR-076: 선언적 reconciliation upgrade flow SSOT

## 상태

**Active (2026-05-15)** — CFP-701 (Wave 1 Story-1) carrier. parent_epic CFP-699 (declarative reconciliation upgrade Epic).

**Amendment 2 (2026-05-17)** — CFP-898 carrier (Wave 4 sub-Epic CFP-858 S1, base layer for S2 CFP-899 / S3 CFP-900). §결정 2 11번째 row + §결정 6 fail-closed clause. ratchet 강화 only — 약화 0건.

`is_transitional: false` — permanent architecture invariant. codeforge family upgrade 도메인의 1st-class 정의 anchor.

**Amendment 1 (2026-05-17) — CFP-906**: §결정 9 신설 — 3-tier channel taxonomy declaration (Wave 4 sub-Epic #1 Story-1, Epic CFP-882). codeforge family plugin distribution 의 **release channel** 1st-class 정의 anchor. 3-tier enum (`stable` / `beta` / `canary`) closed-enum invariant + per-tier semantic (LOW / MEDIUM / HIGH risk class) + production-impact awareness (canary tier admin tier 권장 advisory) + channel selection authority asymmetry sub-§ (silent canary uptake 차단) + sensitive data exposure tier asymmetry sub-§ (canary tier production features = HIGH exposure, ProductionEvidenceDeputy Story-3 spawn trigger) + disjoint invariant (channel tier ≠ version specifier — 독립 차원). `project-config-schema.md codeforge.channel` field 신설 (peer block, `version_pin` sibling) + `reconcile-protocol-v1` v1.6 → v1.7 §4.3 (i) trigger 발동 + §4.10 `multi_version_channel_pin_binding` block carrier 동반. ADR-016 Amendment 3 (`family_7_plugin_atomic × channel pin invariant`) + ADR-063 Amendment 6 §결정 17 (`mirrored field × channel matrix`) + label-registry-v2 v2.29 → v2.30 (3 `channel:*` label + 신규 category enum `channel`) sibling cross-ref. Strengthening direction only — ADR-064 §self-application top-down ratchet 정합. Story-1 = declare layer SSOT only (runtime UpgradeAgent multi-channel dispatch = Wave 4 sub-Epic #1 Story-2 carrier / ProductionEvidence canary tier activation = Story-3 carrier / promotion criteria = Story-4 carrier / downgrade invariant = Story-5 carrier).

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

위 partial cover 가 Epic §1 WHY 의 "빠짐" 증상의 mechanical 원인. 1st-class 도메인 정의 부재 → `결정 트리 박제` (CFP-699 §1 WHY verbatim — 결정 분기 명문화) 불가 → 사용자 결정 분기가 매번 다르게 surfacing.

**Amendment 2 동인 (CFP-898)**: ADR-076 Wave 1 / Wave 2 / Wave 3 후 6 Story 진행 결과 — wholesale_mirror fallback 의 dependency closure gap 이 mctrader-data#81 14 failing checks 영역에서 surfacing. workflow yml 만 mirror, 의존 `scripts/check-*.sh` 미동반 → consumer exit 127. `wholesale_mirror_with_user_visible_loss_report` invariant 의 silent skip 0 강도 강화 필요 (§결정 6 sub-clause 추가) + 영역 11 `scripts/` workflow_dependency_closure enumeration ratchet 강화 (§결정 2 row append).

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
- **Wave 4 sub-Epic CFP-858 base layer (S1) Amendment 2**: dependency bundle integrity — workflow yml + 의존 closure atomic bundle (CFP-898 carrier) ← **본 Amendment 2 신설 영역**

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
| **PR template** | `templates/.github/PULL_REQUEST_TEMPLATE.md` (현 `.github/PULL_REQUEST_TEMPLATE.md` byte-identical mirror) | template export — consumer overlay 시점 byte-identical mirror (Wave 3 Story-7 CFP-821 D1 carrier — Issue templates row 동형 enumeration 확장. ADR-027 Amendment 5 §결정 9 + reconcile-protocol-v1 v1.6 §4.9 동반) |
| **Branch protection** | `.github/branch-protection-manifest.json` (declarative) | API call required — consumer `gh api` apply (Story-3 carrier 영역) |
| **plugin.json mirrored field** | `name` / `version` / `description` / `author` 4종 (ADR-063 atomic invariant) | atomic — marketplace sync PR 선행 merge 의무 |
| **CHANGELOG.md** | wrapper repo SSOT | append-only — version bump 동반 |
| **scripts/ (workflow_dependency_closure)** | `templates/github-workflows/*.yml` (영역 1 `github_workflow`) 안 `run:` block 의 의존 `scripts/check-*.sh` / `python3 templates/scripts/*.py` closure | **bundled_with_referencing_workflow** — 본 영역 자체는 별 mirror target 아님 (영역 1 byte_identical_mirror 의 atomic bundle 단위로 동반). closure resolver (`templates/scripts/mirror-dependency-closure.py`) 가 wholesale_mirror 진입 전 dependency closure resolve + missing 시 fail-closed (Amendment 2 / CFP-898 — Wave 4 sub-Epic CFP-858 S1 carrier. reconcile-protocol-v1 v1.7 §4.3 (i) trigger + §4.10 `dependency_bundle_integrity_binding` block 동반. ADR-064 §self-application ratchet 강화 only) |

위 11 영역이 wrapper plugin 의 declarative SSOT 단위 (旧 "9 영역" = Story-1 작성 시점 → CFP-821 D1 carrier 가 `PR template` row 1행 append → 10 영역 정정 → **Amendment 2 / CFP-898 이 `scripts/` workflow_dependency_closure row 1행 append → 11 영역 ratchet**. 표 row append = ratchet 강화 방향 only, ADR-064 §self-application 정합, fact 영향 0 추적성/count 정정만 — ADR-068 I-4 wording SSOT). 본 enumeration 이 Story-3 carrier (UpgradeAgent + CLI) 의 reconcile target 정의 의 input. 6 lane plugin (codeforge-{requirements,design,review,develop,test,pmo}) 의 self 영역 enumeration 은 ADR-016 family scope 정합 후속 carrier 영역 (본 Story-1 scope 외, Wave 2 Story-4 atomic upgrade carrier).

### 결정 3 — dry-run / snapshot / transaction 3 enum 정의

본 결정이 Epic §1 WHY 의 `결정 트리 박제` (CFP-699 §1 WHY verbatim) 직접 carrier. 3 enum = CLI argument fix 로 사용자 결정 분기 0:

#### dry-run
- **Semantic**: desired state diff current state 계산 + 결과 preview (실 변경 0).
- **Behavior**: 3-way merge (base / wrapper-new / consumer-current) preview 출력 + drift summary report. filesystem touch 0. network call 가능 (Helm-inspired `helm diff` pattern).
- **Scope**: 11 영역 (결정 2 verbatim 정합 — Amendment 2 / CFP-898 후 ratchet) 모두 dry-run 가능. consumer customization marker block 안 영역 = preserve 표기. marker block 밖 영역 = wholesale mirror 표기. dependency missing 시 `[dry-run] missing deps: <list>` 표기 (return 0 preview only, reconcile-protocol-v1 v1.7 §4.10 `dry_run_behavior` 정합).
- **Invariant**: 사용자 결정 분기 0 (정보 제공만). dry-run 결과 보고 후 사용자가 별도 명령 (`--apply` / `--rollback` / abort) 으로 진행.

#### snapshot
- **Semantic**: upgrade transaction 의 pre-state sentinel — rollback 의 입력 state.
- **Behavior**: `--apply` 직전 자동 생성. consumer-side `.claude/_snapshots/<UTC-timestamp>-<version-pre>.tar.gz` (또는 동등 archival) + upgrade event log artifact (`docs/upgrade-events/<date>-<version>.md` — Wave 2 Story-3 영역 file schema).
- **Granularity**: 11 영역 (결정 2 Amendment 1 정합) union — wrapper SSOT 영역 + consumer customization marker block 외 영역. marker block 안 customization 영역은 snapshot scope 외 (consumer responsibility preserve).
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

#### Amendment 2 — Dependency missing fail-closed sub-clause (CFP-898 Wave 4 sub-Epic CFP-858 S1 carrier)

**의미 invariant 무변경** (`marker_block_absent_behavior: wholesale_mirror_with_user_visible_loss_report` 자체는 그대로). **ratchet 강화 방향** sub-clause 1개 추가:

> wholesale_mirror branch 진입 전 의존 closure resolve 의무 — workflow yml (영역 1 `github_workflow`) 의 `run:` block 안 `bash scripts/check-*.sh` / `python3 templates/scripts/*.py` 패턴이 wrapper-side 에서 enumerate (영역 11 `scripts/` workflow_dependency_closure) 가능한 경우, mirror 전 closure 가 모두 resolve 되어야 한다. **dependency missing 시 fail-closed** (exit 1 + visible error log `[ERR] Dependency missing: scripts/check-XXX.sh (referenced by: .github/workflows/YYY.yml)` + 부분 mirror 산출물 commit 금지). silent skip 0 invariant 강화 (의미 invariant `wholesale_mirror_with_user_visible_loss_report` 안 dependency missing 영역 fallback 명세 — user_visible_loss_report scope 확장: 旧 consumer customization overwrite 보고 only → 신 + dependency missing fail-closed report).

**rationale (Amendment 1)**: 의미 invariant 자체는 무변경 (`wholesale_mirror_with_user_visible_loss_report` 의 두 단어 그대로) — 단 invariant 안 fallback behavior scope 가 silent skip → fail-closed 방향으로 강화. ratchet weakening 0건 (ADR-064 §self-application 정합 + ADR-058 §결정 5 sunset_justification 의무 회피 — 강화 방향만).

**mechanical carrier**: reconcile-protocol-v1 v1.7 §4.10 `dependency_bundle_integrity_binding` block (`fail_closed_behavior.on_dependency_missing: exit_1_with_error_log` field). 본 ADR §결정 6 Amendment 1 = semantic declare / contract §4.10 = mechanical declare 분리 (CFP-743/744/745/820/821 §결정 본문 vs §4.5/§4.6/§4.7/§4.8/§4.9 binding block 분리 패턴 답습).

**Architect lane derived default (ADR-064 §결정 3 룰 1 정합)**:
- AM-1 `closure_resolve_algorithm` = `regex_primary` (stdlib only, pyyaml 의존 0 — consumer 측 가용성 미보장 영역 cover)
- AM-2 `transitive_depth_limit` = `1` (wrapper-side script.sh 내부 sub-script 호출은 wrapper SSOT 가 보장, depth 2+ false-positive 폭증 회피)
- AM-3 `closure_resolver_location` = `templates/scripts/mirror-dependency-closure.py` (consumer-distributable, ADR-005 self-app 면제 영역 — wrapper-side `scripts/` mirror 부재 정합)
- AM-4 `self_loop_invariant` = `본 file 자체가 workflow yml 안 의존되지 않음` (self-loop 0 invariant, Phase 2 TC-DEP-14 검증 의무)

**evidence**: mctrader-data#81 14 failing checks (Epic CFP-858 §1 motivation verbatim) — wholesale_mirror 시 silent partial bundle 의 real harm 사례. consumer (`mctrader-data`) 44개 workflow `bash: scripts/check-XXX.sh: No such file or directory` (exit 127).

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

### 결정 9 — 3-tier channel taxonomy declaration (Wave 4 sub-Epic #1 carrier, Story-1 schema SSOT only) (Amendment 1, CFP-906)

codeforge family plugin distribution 에서 **release channel** 은 **version specifier 와 독립적인 차원**. 본 결정이 channel taxonomy 의 1st-class 선언 carrier (Wave 4 sub-Epic #1 Story-1, Epic CFP-882).

#### 9.1 3-tier channel taxonomy

| Channel tier | 정의 | Risk class | Production impact | consumer 사용 시점 | empirical anchor |
|---|---|---|---|---|---|
| **stable** | 현재 활성 stable release (기본값) | LOW | none | 대부분의 consumer (default) | npm `dist-tag: latest` / Chrome stable channel |
| **beta** | opt-in incremental track | MEDIUM | observable but reversible | mid-trust consumer | npm `dist-tag: beta` / Chrome beta channel (4주 cycle) |
| **canary** | preview + production-impact tier | **HIGH (production cutover)** | production cutover (canary deployment semantic) | early adopter / dogfood consumer (admin tier 권장) | Chrome canary channel / K8s alpha→beta→GA precedent |

3-tier enum (`stable | beta | canary`) = **closed-enum strict invariant**. undeclared 값 = validator FAIL (warning-first, ADR-027 Amendment 2 `bootstrap.fallback_mode` 패턴 답습).

#### 9.2 본 결정 scope (Story-1)

- **channel taxonomy declare** (3-tier enum 정의 + per-tier semantic SSOT)
- **`project-config-schema.md` `codeforge.channel` field 신설** (peer block, `codeforge.version_pin` sibling — disjoint invariant 보존)
- **`reconcile-protocol-v1` v1.7 §4.10 `multi_version_channel_pin_binding` block** carrier (3-tier closed-enum + family_7_plugin_atomic × channel pin invariant + per-channel marketplace.json channels[] matrix + 3-way channel invariant)
- **ADR-016 Amendment 3** (family_7_plugin_atomic × channel pin invariant declare) sibling
- **ADR-063 Amendment 6 §결정 17** (mirrored field × channel matrix declare) sibling
- **label-registry-v2 v2.30** (3 `channel:*` label + 신규 category enum `channel`) sibling

본 결정 scope **외** (Wave 4 sub-Epic #1 후속 Story carrier 분리, ADR-067 §결정 4 sequential ordering 정합):

- **Story-2 carrier**: runtime UpgradeAgent multi-channel dispatch + CLI `--channel` flag + channel-drift-detection workflow + `scripts/check-3way-version-parity.sh` 의 channel 차원 확장
- **Story-3 carrier**: ProductionEvidenceDeputy canary tier activation (ADR-72 §결정 1 trigger) + IntegrationTestAgent Epic-level reactivation
- **Story-4 carrier**: promotion criteria quantitative declare + canary coord + `gate:channel-*-promotion` label scheme (Story-4 carrier 영역, Story-1 영역 외)
- **Story-5 carrier**: downgrade invariant declare (canary → beta → stable demotion 시 feature regression warning) + Wave 4 sub-Epic #1 close + retro

#### 9.3 Disjoint invariant — channel ≠ version specifier

`codeforge.channel.tier` (release tier) ≠ `codeforge.version_pin.version` (version specifier) — 두 field 는 **독립 차원**, 동일 block 내 embedding 금지. `version_pin` 안 `channel` sub-field 형태 (`version_pin.channel: stable`) 는 SRP 위배:

| Block | 책임 축 | 변경 trigger |
|---|---|---|
| `codeforge.version_pin.version` | **version specifier** — 어떤 특정 버전 (semver string) 을 사용하는가 | 버전 업그레이드 시 |
| `codeforge.channel` (CFP-906 신설) | **release tier** — 어떤 채널 (stable/beta/canary) 을 추적하는가 | 채널 정책 변경 시 |

두 변경 축 (axis of change) 이 서로 다르므로, 독립 peer block 으로 분리 의무. 결합 시 (a) consumer 가 채널만 바꾸고 싶은 경우 version_pin block 전체 맥락을 읽어야 함 (불필요한 coupling) + (b) version_pin.version 이 고정값인 동안 channel 은 drift detection 에서 독립적으로 움직이는 개념 — 같은 block 에 두면 validator 로직의 orthogonality 파괴.

#### 9.4 Channel selection authority asymmetry (canary tier production-impact)

| Tier | Risk class | Default behavior | Selection authority |
|---|---|---|---|
| `stable` | LOW | default | developer self-service OK |
| `beta` | MEDIUM | explicit opt-in | developer + reviewer awareness 충분 |
| `canary` | **HIGH (production-impact)** | explicit opt-in + production-impact awareness | **admin tier 권장** (consumer-side 책임, codeforge wrapper 영역 외 — CODEOWNERS auto-review path 권장 advisory) |

**Mitigation hook** (Story-1 declare scope):
- (M-1) `project-config-schema.md codeforge.channel` field description 안 `production_impact` semantic 명시 (canary tier 한정)
- (M-2) `reconcile-protocol-v1` §4.10 `multi_version_channel_pin_binding.canary_tier_authority: admin_review_recommended` field 명시 — semantic advisory only
- (M-3) consumer CODEOWNERS auto-review path 권장 (consumer-side 책임, codeforge wrapper enforcement 0 — Story-2 carrier 시점 consumer-guide 안 권장 단락)

**위협 시나리오** (SecurityArch §1 T-1.1.a): silent canary uptake — consumer A 가 `codeforge.channel: stable` 선언 (의도: 보수적 보존), 동일 consumer 의 다른 contributor B 가 PR 로 `codeforge.channel: canary` 변경, PR review 시 channel 변경 자체의 의미가 reviewer 에게 surfaced 되지 않음, merge 후 다음 upgrade 에서 family 7 plugin = canary tier install, consumer org 가 production-impact 변경을 "stable 의도" 컨텍스트로 흡수.

#### 9.5 Sensitive data exposure tier asymmetry

| Data class | Owner | Tier-aware exposure | Marking obligation |
|---|---|---|---|
| `codeforge.channel` field value | consumer overlay | low | none |
| consumer `installed_plugins.json` channel pin state | consumer install dir | low | none |
| canary tier 가 enable 하는 production features | **consumer domain layer** | **HIGH** | ProductionEvidence deputy spawn time mandatory (Wave 4 sub-Epic #1 Story-3 carrier) |

**Story-1 declaration-level**:
- ProductionEvidenceDeputy = **NOT-spawn** (Story-1 declare-only — Live touching = FALSE, ADR-72 §결정 1 정합. canary tier semantic = declare only / canary tier 실 activation = Wave 4 sub-Epic #1 Story-3 carrier 시점 ProductionEvidenceDeputy spawn trigger)
- IntegrationTestAgent Epic-level reactivation = Story-3 carrier (Story-1 영역 외)

#### 9.6 Empirical anchor — 3-tier channel pattern industry precedent

3-tier release channel pattern 의 empirical grounding (ADR-068 I-5 dimensional empirical grounding 정합):

| Industry exemplar | 3-tier mapping | empirical-source |
|---|---|---|
| **npm dist-tag** | `latest` (stable) / `next` (beta) / `canary` | npm cli docs (`dist-tag` field semantic) |
| **Chrome release channels** | Stable (대다수 user) / Beta (4주 cycle) / Canary (daily) | Google Chrome release schedule (chromium.org) |
| **Rust release channels** | stable (6주) / beta (6주 pre-stable) / nightly | rust-lang.org release model |
| **Kubernetes feature stages** | GA / Beta / Alpha | K8s API versioning convention |

`[empirical-source: 4 industry exemplars verified — npm dist-tag / Chrome 3-channel / Rust 3-channel / K8s 3-stage]`. 본 ADR-076 §결정 9 의 3-tier (stable/beta/canary) = industry-standard pattern 직접 transplant (CFP-906 RequirementsPL §1-§6 fact source 정합 — Wave 4 sub-Epic brainstorm Phase 1 confirmation 시점 사용자 derived default).

#### 9.7 Sequential ordering (Wave 4 sub-Epic #1 Story 1 → 5)

본 §결정 9 = Wave 4 sub-Epic #1 (multi-version channel pin) carrier 의 첫 sequential entry. Wave 4 sub-Epic #1 의 5-Story sequential carrier:

| Story | scope | trigger |
|---|---|---|
| **Story-1 (CFP-906, 본 carrier)** | schema SSOT — declare layer (channel taxonomy + binding block + sibling ADR Amendment) | Wave 4 sub-Epic #1 entry, Live touching = FALSE |
| Story-2 (별 CFP) | runtime — UpgradeAgent multi-channel dispatch + CLI + channel-drift-detection workflow | Story-1 merge 후 sequential prerequisite |
| Story-3 (별 CFP) | ProductionEvidenceDeputy canary tier activation + IntegrationTestAgent Epic-level reactivation | Live touching = TRUE (canary tier production cutover) |
| Story-4 (별 CFP) | promotion criteria quantitative declare + canary coord + gate:channel-*-promotion label scheme | Story-1+2+3 merge 후 |
| Story-5 (별 CFP) | downgrade invariant declarative carrier + Wave 4 sub-Epic #1 close + retro | sequential terminus |

ADR-067 §결정 4 sequential ordering 정합 (Story 간 cross-pollinate 차단).

#### 9.8 Cross-references

- `docs/inter-plugin-contracts/reconcile-protocol-v1.md` v1.7 §4.10 `multi_version_channel_pin_binding` (본 §결정 9 의 contract carrier)
- `docs/project-config-schema.md codeforge.channel` (본 §결정 9 의 schema carrier, peer block)
- `docs/adr/ADR-016-marketplace-registration-policy.md` Amendment 3 (family_7_plugin_atomic × channel pin invariant)
- `docs/adr/ADR-063-marketplace-atomic-invariant.md` Amendment 6 §결정 17 (mirrored field × channel matrix + 3-way channel invariant)
- `docs/adr/ADR-72-production-evidence-deputy-and-epic-cutover-gate.md` §결정 1 (canary tier production-impact = ProductionEvidenceDeputy spawn trigger, Story-3 carrier 영역)
- `docs/inter-plugin-contracts/label-registry-v2.md` v2.30 (3 `channel:*` label + 신규 category enum `channel`)
- `<internal-docs>/wrapper/stories/CFP-906.md` (본 ADR Amendment 1 carrier Story)
- `<internal-docs>/wrapper/change-plans/cfp-906-channel-schema-ssot.md` (Phase 1 PR change plan)

## 결과

### 즉각적 결과

1. **`docs/inter-plugin-contracts/reconcile-protocol-v1.md` 신규** — kind:registry, schema field 6종 (`customization_preservation_entry` / `marker_block_absent_behavior` / `version_handshake` / `reconcile_strategy` enum / `snapshot_semantic` / `atomicity_boundary`) + dry-run/snapshot/transaction 3 mode enum + placeholder reserve 영역 (Wave 4 carrier). **Amendment 2 (CFP-898)**: v1.6 → v1.7 MINOR bump (§4.3 (i) trigger + §4.10 `dependency_bundle_integrity_binding` block 신설).
2. **`docs/domain-knowledge/domain/upgrade-flow/declarative-reconciliation.md` 신설** — RequirementsPL self-write 이미 완료 (CFP-26 Phase 0a owner agent direct write). 본 ADR § narrative SSOT anchor.
3. **`docs/inter-plugin-contracts/MANIFEST.yaml` registries[] row append** — `reconcile_protocol` entry (v1.0 Active, sibling sync 면제 ADR-010 §결정 2). **Amendment 2 (CFP-898)**: row 갱신 (v1.6 → v1.7).
4. **`CLAUDE.md` 2 단락 cross-ref** — "GitHub Workflow" + "ADR (`docs/adr/` SSOT)" 단락 ADR-076 1-line cross-ref. **Amendment 2 (CFP-898)**: "Inter-plugin Contract" 단락 reconcile-protocol-v1 v1.7 + Amendment 2 reference 추가.
5. **`docs/orchestrator-playbook.md` cross-ref** — §3 Lane 실행 영역 narrative anchor 1-2 line.
6. **`docs/adr/ADR-RESERVATION.md` row 76 append** — CFP-701 carrier, status active, reserved_at 2026-05-15. ADR-050 §결정 1 정합 (ArchitectAgent inline carrier, ADR-070 / CFP-578 precedent — chief author scope 영역).
7. **Amendment 2 (CFP-898) 추가 carrier**: `docs/parallel-work/section-ownership.yaml` row append (reconcile-protocol-v1 §4.10 + ADR-076 §결정 영역 lock — parallel session collision 회피, ADR-050 §결정 4 정합).

### 후속 carrier dependency 명시

- **Wave 1 Story-2 (CFP-702)**: customization marker block 도입 — 본 ADR §결정 6 의 sequential prerequisite. 본 Story-1 merge 완료 의무.
- **Wave 2 Story-3 (CFP-743)**: UpgradeAgent + CLI runtime carrier — 본 ADR §결정 5 의 reconcile execution responsibility 분리 정합. (KEY 정정: Wave 1 작성 시점 placeholder `CFP-703` → 실제 발의 Issue `CFP-743`. 동일 Story, fact 영향 0, 추적성만 정정 — ADR-068 I-4 wording SSOT 정합.)
- **Wave 2 Story-4**: 7 plugin atomic upgrade runtime — 본 ADR §결정 8 의 atomicity boundary `runtime implementation` 영역 ratchet carrier (의미 invariant `family_7_plugin_atomic` 자체는 ADR-016 §결정 1 SSOT, 본 carrier 가 runtime catch-up).
- **Wave 2 Story-5**: overlay 3-way merge runtime — 본 ADR §결정 1 의 Kustomize-inspired customization layer reconcile.
- **Wave 4 E1/E2/E3**: multi-version channel / codemod registry / uninstall — 본 ADR `reconcile-protocol-v1` 의 `version_handshake` + `reconcile_strategy` enum placeholder 영역 활용.
- **Wave 4 sub-Epic CFP-858 S2 (CFP-899)**: repo-kind detection truth-table (`.claude-plugin/plugin.json` 부재 → consumer signal). Amendment 2 (CFP-898) merge 후 진입.
- **Wave 4 sub-Epic CFP-858 S3 (CFP-900)**: upgrade-event log result enum 확장 (`SUCCESS_WITH_DEGRADATION` / `PARTIAL_FAILURE`) + phase-gate-mergeable fast-pass content sanity. S1 + S2 merge 후 진입.

### 검증 영역

- **AC-1 (frontmatter + section schema)**: 본 ADR file `check-doc-frontmatter.sh` + `check-doc-section-schema.sh` PASS.
- **AC-2 (reconcile-protocol-v1 MANIFEST entry)**: `check-inter-plugin-contracts.sh` PASS.
- **AC-3 (3 enum 정의 + 외부 reference)**: 본 §결정 3 + Helm/Kustomize/Terraform cross-ref verbatim.
- **AC-4 (snapshot ↔ ADR-067 RESET disjoint phrasing)**: 본 §결정 4 verbatim "disjoint" + "layer" phrasing 보유. 3 곳 cross-ref (ADR / contract / domain-knowledge) 완성.
- **AC-5 (ADR-053 D2 compliance)**: 본 §결정 7 verbatim cross-ref. dogfood-out 영역 면제 분기 명시.
- **Amendment 2 (CFP-898) AC**: Story CFP-898 §2 AC-5 verbatim — §결정 2 표 11번째 row append (workflow_dependency_closure / scripts/ + bundled_with_referencing_workflow, 10→11 영역 ratchet) + §결정 6 Amendment 2 sub-section (fail-closed clause) + amendment_log entry 2 + `is_transitional: false` 무변경 + `mechanical_enforcement_actions: []` declaration-only retain (ADR-082 §결정 6 + ADR-070 §D5 패턴 답습).

## 해소 기준

**N/A — permanent governance invariant** (`is_transitional: false`).

본 ADR 은 codeforge family upgrade 도메인의 1st-class 정의 anchor — codeforge plugin family 가 deprecate 되지 않는 한 영구 유효. Amendment 는 강화 방향만 허용 (ADR-058 §결정 5 + ADR-064 top-down self-application 정합):

- 새 영역 enumeration 추가 (결정 2 표 row append) — **Amendment 2 / CFP-898 = `scripts/` workflow_dependency_closure row append (11번째 row, 10 → 11 영역 ratchet 강화)**
- 새 reconcile_strategy enum 값 추가 (결정 3 placeholder 활성)
- atomicity_boundary runtime implementation ratchet (per-plugin → family_7_plugin — Wave 2 Story-4 carrier 시점, 의미 invariant 변경 0)
- snapshot retention policy 추가 (per-MAJOR-version — Wave 4 E1 carrier 시점)
- **결정 6 fallback behavior scope 확장 (Amendment 2 / CFP-898 = silent skip → fail-closed sub-clause 추가, `marker_block_absent_behavior: wholesale_mirror_with_user_visible_loss_report` 의미 invariant 무변경)**

약화 방향 (예: 사용자 결정 분기 0 invariant 약화 / disjoint layer 합치 / dependency missing 시 silent skip 허용) = ADR-058 §결정 5 sunset_justification 3-tuple (metric / who / how) 정량 명시 없이 차단. 본 ADR 의 사용자 directive verbatim (CFP-699 Epic §1 WHY `결정 트리 박제`) 정합.

## 관련 파일

- `docs/inter-plugin-contracts/reconcile-protocol-v1.md` — 본 ADR 의 schema carrier (kind:registry, v1.7 Amendment 1 후 Active)
- `docs/inter-plugin-contracts/MANIFEST.yaml` — registries[] `reconcile_protocol` row (Amendment 1 후 v1.7)
- `docs/domain-knowledge/domain/upgrade-flow/declarative-reconciliation.md` — narrative SSOT anchor (RequirementsPL self-write)
- `docs/adr/ADR-027-consumer-adoption-protocol.md` — boundary disjoint (detection layer vs upgrade transaction layer)
- `docs/adr/ADR-053-structural-change-restart-prerequisite.md` — transaction completion prerequisite (§결정 7 cross-ref)
- `docs/adr/ADR-067-fix-ledger-implementability-escalation.md` — Story progression layer RESET (§결정 4 disjoint cross-ref)
- `docs/adr/ADR-038-progress-visualization-todowrite.md` — Amendment 3 §결정 12 SessionStart hook static invariant (§결정 5 cross-ref)
- `docs/adr/ADR-016-marketplace-registration-policy.md` — codeforge family scope 7 plugin atomic (§결정 8 cross-ref)
- `docs/adr/ADR-008-inter-plugin-contract-versioning.md` — reconcile-protocol-v1 v1.0 / v1.7 MINOR bump (Amendment 1 정합)
- `docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md` — kind:registry sibling sync 면제 정합
- `docs/adr/ADR-058-adr-sunset-criteria-mandate.md` — is_transitional: false 정합 (해소 기준 § verbatim)
- `docs/adr/ADR-061-python-script-writing-convention.md` — Amendment 1 carrier `templates/scripts/mirror-dependency-closure.py` 신설 (외부 .py 의무 정합)
- `docs/adr/ADR-064-decision-principle-mandate.md` — derived default + forbid-list + parallel default 정합 (Amendment 1 AM-1/2/3/4 derived default 정합)
- `docs/adr/ADR-040-worktree-convention.md` — Amendment 3 §결정 7.D self-app invariant (frontmatter `mechanical_enforcement_actions: []` 정합)
- `docs/adr/ADR-050-parallel-epic-conflict-coordination.md` — ADR-RESERVATION row 76 append 의 회피 mechanism + Amendment 1 section-ownership.yaml row append 정합
- `docs/adr/ADR-065-architect-phase1-mechanical-self-check.md` — ArchitectAgent Phase 1 commit-time 7-item self-check 정합
- `docs/adr/ADR-068-boundary-completeness-invariants.md` — 4 semantic invariants + Amendment 1 I-5 dimensional empirical grounding 정합
- `docs/adr/ADR-070-codex-verify-before-trust.md` — Touchpoint #2 (ArchitectAgent §3 직후) carry-over 정합 + Amendment 1 mechanical_enforcement_actions [] declaration-only retain 패턴 답습 (§D5 precedent)
- `docs/adr/ADR-073-orchestrator-verify-before-assert.md` — fact claim marker 5종 정합
- `docs/adr/ADR-082-write-time-self-write-verification-mandate.md` — Amendment 1 ratchet 강화 패턴 답습 (§결정 6 mechanical_enforcement_actions 정합)
- `CLAUDE.md` — "GitHub Workflow" + "ADR" + "Inter-plugin Contract" 단락 cross-ref (Amendment 1 후 추가)
- `docs/orchestrator-playbook.md` — §3 Lane 실행 cross-ref
- `templates/scripts/mirror-dependency-closure.py` — **Amendment 1 carrier — Phase 2 신설** (closure resolver script, ADR-061 외부 .py 의무 정합, consumer-distributable AM-3 derived default location)
- `scripts/reconcile-overlay.sh` — **Amendment 1 carrier — Phase 2 hook insertion** (line 437 직전, MARKER_NONE branch first-line, `MIRROR_DEP_PY` env 가용 시 invocation + return 2 abort on missing dependency)
- `<internal-docs>/wrapper/stories/CFP-701.md` — 본 ADR carrier Story (Wave 1 Story-1)
- `<internal-docs>/wrapper/change-plans/cfp-701-reconciliation-contract.md` — Phase 1 PR change plan (Wave 1)
- `<internal-docs>/wrapper/stories/CFP-898.md` — Amendment 2 carrier Story (Wave 4 sub-Epic CFP-858 S1)
- `<internal-docs>/wrapper/change-plans/cfp-898-dependency-bundle-integrity.md` — Amendment 2 Phase 1 PR change plan
