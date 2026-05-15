---
kind: domain_fact
type: domain-knowledge
area: upgrade-flow
topic_slug: declarative-reconciliation
title: codeforge upgrade flow 의 선언적 reconciliation 개념 정의
status: Active
tags:
  - upgrade-flow
  - declarative-reconciliation
  - helm-pattern
  - snapshot-semantic
  - reconcile-protocol-v1
  - adr-076
related_adrs:
  - ADR-076  # 본 entry 의 carrier ADR (선언적 reconciliation upgrade flow SSOT)
  - ADR-027  # consumer adoption protocol (boundary disjoint)
  - ADR-053  # 구조적 변경 재구동 (transaction completion prerequisite)
  - ADR-067  # FIX ledger RESET (disjoint layer anchor)
  - ADR-016  # marketplace registration (codeforge family scope)
  - ADR-038  # SessionStart hook static invariant (hook = detect, UpgradeAgent = execute boundary)
related_stories:
  - CFP-699  # parent Epic
  - CFP-701  # 본 carrier Story (Wave 1 Story-1)
  - CFP-702  # Wave 1 Story-2 (D4 marker — sequential prerequisite)
  - CFP-743  # Wave 2 Story-3 (UpgradeAgent + CLI — runtime carrier) — KEY 정정 CFP-703→CFP-743 (Wave 1 placeholder drift / 동일 Story / fact 영향 0)
created: 2026-05-15
updated: 2026-05-15
---

# codeforge upgrade flow 의 선언적 reconciliation 개념 정의

## 정의

codeforge upgrade 의 architecture 패턴 = **선언적 reconciliation** (Helm `helm upgrade` / Kubernetes Kustomize / Terraform plan-apply 패턴 차용). wrapper SSOT = desired state, consumer 측 overlay + plugin install = current state, upgrade 명령 = converge. 사용자 결정 분기 0 자리 (CLI argument 로 dry-run / rollback / apply fix, prompt 없음).

본 entry = ADR-076 §결정 본문의 narrative SSOT — codeforge 도메인 1st-class 정의 anchor. ArchitectAgent / DeveloperAgent / Researcher / DomainAgent / 후속 Wave carrier 가 참조하는 단일 정의.

## 컨텍스트

codeforge family upgrade 도메인이 ADR / domain-knowledge 어디에도 1st-class 로 정의되어 있지 않은 상태가 carrier Story CFP-701 의 직접 동인. 현 self-app partial cover 영역 4건 (regen-agents.sh / merge.py / check_bootstrap.py / hooks/session-start) 모두 detection only 또는 partial propagate — 선언적 reconciliation 1st-class 정의 부재 = "결정 트리 박제" (CFP-699 Epic §1 WHY) 불가의 mechanical 원인. 본 entry = CFP-699 Epic Wave 1 Story-1 (CFP-701) 의 narrative SSOT carrier — ADR-076 §결정 본문 + reconcile-protocol-v1.md schema 와 함께 3-SSOT 분리 (Governance + Schema + Narrative) 구조 정합.

## 핵심 규칙

1. **Desired state** = wrapper SSOT 9 영역 (github_workflow / session_start_hook / label_taxonomy / settings_json_toggle / codeowners / issue_templates / branch_protection / plugin_json_mirrored / changelog — ADR-076 §결정 2 verbatim)
2. **Current state** = consumer overlay + plugin install state (consumer `.claude/_overlay/` + `.claude/plugins/installed_plugins.json` + `.github/workflows/` 등)
3. **Customization layer** = wrapper-managed marker block 밖 영역 (preserved patch layer). marker syntax = `# BEGIN wrapper-managed` / `# END wrapper-managed` pair (Ansible blockinfile-inspired, comment prefix per-filetype = ADR-027 Amendment 3 결정 영역). marker 안 = wrapper SSOT wins, 밖 = consumer wins. 부재 시 = wholesale_mirror_with_user_visible_loss_report. 상세 = §"Customization marker (D4)" + ADR-027 Amendment 3 (CFP-702 carrier)
4. **3 mode CLI argument fix** — `--dry-run` (preview, filesystem touch 0) / `--apply` (transaction atomic unit) / `--rollback <version>` (snapshot restore)
5. **사용자 결정 분기 = 0** (정해진 자리에서만, 매번 다르게 묻지 않음)
6. **Snapshot ↔ ADR-067 RESET disjoint layer** (같은 단어 RESET 이 다른 layer 에서 다른 의미 — 본 entry Invariant 2 verbatim)
7. **Family scope 7 plugin atomic unit** (ADR-016 §결정 1 정합 — wrapper + 6 lane plugin)

상세 4-stage upgrade flow / 4 invariants / external pattern reference / conceptual boundary 표 = 본 entry 본문 § 참조.

## 경계

본 entry 영역 (in scope):
- 선언적 reconciliation 의 1st-class 도메인 정의 (3 layer / 3 mode / 4-stage flow / 4 invariants)
- 외부 패턴 reference (Helm / Terraform / Kustomize / Ansible)
- conceptual boundary (다른 도메인 영역과의 disjoint)

본 entry 영역 외 (out of scope):
- ADR-074 / ADR-075 (CFP-708 / CFP-709 carrier 영역) — 본 entry = CFP-701 carrier 단일 영역
- ADR-076 §결정 본문 자체 (governance SSOT — ADR file SSOT)
- reconcile-protocol-v1.md schema (schema SSOT — contract file SSOT)
- ADR-027 Amendment 3 §결정 본문 자체 (D4 marker 의무 enforcement governance SSOT — ADR file SSOT, CFP-702 carrier). 본 entry §"Customization marker (D4)" = narrative anchor only
- D4 marker lint / migration script 실 구현 (`scripts/check-wrapper-managed-block.sh` / `scripts/migrate-existing-customization.sh` — CFP-702 Phase 2 carrier)
- Wave 2/3/4 carrier 의 runtime implementation (UpgradeAgent / CLI / atomic upgrade / 3-way merge / multi-version channel / codemod / uninstall)

## Conceptual model

### 3-layer state representation

| Layer | 정의 | 위치 | 책임 주체 |
|---|---|---|---|
| **Desired state** | wrapper SSOT 영역 enumeration (workflow / hook / label / overlay / settings.json / CODEOWNERS / Issue templates / branch protection) | `mclayer/plugin-codeforge` repo + 6 lane plugin repos | wrapper / lane plugin author |
| **Current state** | consumer `.claude/_overlay/` + `.claude/plugins/installed_plugins.json` + `.github/workflows/` + `.github/ISSUE_TEMPLATE/` 등 | consumer repo working tree + plugin install dir | consumer (정상) / drift detector (감지) |
| **Customization layer** | consumer 의 wrapper-managed marker block 밖 영역 — preserved patch layer | consumer overlay / hook / workflow file 안 `# BEGIN/END wrapper-managed` block 외 | consumer (preserve) |

#### Customization marker (D4 — CFP-702 carrier)

Story-1 (CFP-701) contract `reconcile-protocol-v1.md` 의 `customization_preservation_entry: "marker_block"` + `marker_block_syntax_carrier: "CFP-702"` 가 영역 declare. 실 marker syntax + lint + migration = Wave 1 Story-2 (CFP-702) carrier — ADR-027 Amendment 3 SSOT.

- **marker pair syntax**: `# BEGIN wrapper-managed` ... `# END wrapper-managed` block (comment prefix per-filetype = ADR-027 Amendment 3 §결정 영역 — yaml/sh `#` / md `<!-- -->` / settings.json marker-incapable sidecar 분기)
- **ownership 모델 (npm/Helm 과 reverse)**: marker block **안** = wrapper SSOT wins (upgrade 시 mirror), **밖** = consumer wins (preserve). npm/Helm 의 "consumer wins" default 와 **reverse** — codeforge 는 SSOT-driven 모델이므로 marker 안에서 wrapper 우선이 안전 (Spec §3.2 Unknown unknowns "ownership boundary declaration 부재" 의 mechanical 실체)
- **부재 시 fallback**: consumer 가 marker 미도입 상태에서 customize → `wholesale_mirror_with_user_visible_loss_report` (Story-1 contract `marker_block_absent_behavior` verbatim — silent overwrite 0, EPIC-AC-4 정합). retroactive mitigation = `scripts/migrate-existing-customization.sh` (mctrader 5 repo idempotent auto-wrap, CFP-702 Phase 2 carrier)
- **외부 prior art**: Ansible `blockinfile` module (`# BEGIN ANSIBLE MANAGED BLOCK` / `# END ...` marker-pair idempotent replace) 가 가장 정합 — migration script idempotency + lint malformed detection 동형. Kustomize overlay (base + overlay 분리) = conceptual layer 분리 동형
- **downstream 의존**: Wave 2 Story-5 (overlay reconcile 통합 — 3-way merge) 가 본 marker syntax 를 input 으로 받음 (Spec §8 "Story-2 marker 부재 시 Story-5 reconcile 시 customization loss" verbatim — sequential prerequisite)

### 4-stage upgrade flow

```
[Stage 1: Detect]
  SessionStart hook (check_bootstrap.py + check-codeforge-version-drift.sh)
  → workflow SHA drift / plugin version drift / overlay drift 감지
  → detection only (filesystem touch 0 + network call 0 invariant — ADR-038 Amendment 3 §결정 12)

[Stage 2: Plan (dry-run)]
  UpgradeAgent + scripts/codeforge-upgrade.sh --dry-run (Story-3 carrier)
  → desired state diff current state 계산
  → 3-way merge (base/wrapper-new/consumer-current) 결과 preview
  → 사용자 결정 분기 0 (정보 제공만)

[Stage 3: Apply (transaction)]
  scripts/codeforge-upgrade.sh --apply
  → snapshot 생성 (pre-state sentinel)
  → wrapper SSOT mirror (customization marker block 외 영역)
  → 사후 sanity check (workflow lint / hook signature / label registry 정합)
  → upgrade event log artifact 생성 (docs/upgrade-events/<date>-<version>.md)

[Stage 4: Rollback (optional)]
  scripts/codeforge-upgrade.sh --rollback <version>
  → snapshot 로 state revert
  → 동일 명령, 사용자 결정 분기 0
```

## Key invariants

### Invariant 1 — User decision branch = 0

사용자 directive verbatim (CFP-699 Epic §1 WHY): **"한 번 명령 = 끝까지 자동 + 사용자 결정은 정해진 자리에서만 (= 0 자리)"**.

- dry-run preview = 결정 분기 아님 (실행 직전 정보 제공만)
- rollback = 동일 명령의 `--rollback <version>` flag (사용자 prompt 없음)
- 충돌 / 실패 / 차단 시 명시적 보고 + 사용자 escalation (silent skip 0 — EPIC-AC-4 의 "silent overwrite 0" invariant)

### Invariant 2 — Snapshot ↔ ADR-067 RESET disjoint layer

**같은 단어 "RESET" 이 다른 layer 에서 다른 의미**. 본 invariant 가 boundary completeness gap (ADR-068 I-2 cross-module propagation completeness) 회피의 핵심 anchor.

| Concept | Layer | 정의 | 위치 |
|---|---|---|---|
| **ADR-067 RESET** | Story progression layer | Story §10 FIX Ledger 의 `RESET?` column 마커 (`RESET <lane>` / `cross-lane-pause:<lane>`) — lane FIX cycle 의 cycle 재시작 표기 | Story file §10 row |
| **본 ADR-076 snapshot** | Upgrade transaction layer | upgrade 의 pre-state sentinel — rollback 의 입력 state | consumer `.claude/_snapshots/` 또는 wrapper `docs/upgrade-events/` (ADR-076 §결정 영역) |

**두 개념 disjoint** — cross-pollinate 금지. ADR-076 §결정 본문 + reconcile-protocol-v1 contract schema + 본 domain-knowledge entry 3 곳 모두 명시적 분리 declare 의무.

### Invariant 3 — Codeforge family scope = 7 plugin atomic

ADR-016 §결정 1 정합. wrapper + 6 lane plugin (codeforge-{requirements, design, review, develop, test, pmo}) = 7 plugin 전체가 단일 upgrade transaction 의 atomicity unit. 부분 upgrade (예: wrapper 만 5.65.0, codeforge-design 만 5.64.0) = drift = stale version install = 단일 진입점 의미 무너짐.

본 invariant 의 atomic upgrade 실 implementation = Wave 2 Story-4 carrier (`scripts/atomic-upgrade-7-plugins.sh`). 본 Story-1 = atomicity semantic axis declare only.

### Invariant 4 — Reconcile execution responsibility 분리

SessionStart hook ≠ UpgradeAgent ≠ CLI. 3 책임 분리 (ADR-038 Amendment 3 §결정 12 + ADR-039 정합):

| 책임 주체 | 역할 | 위치 |
|---|---|---|
| **SessionStart hook** (`check_bootstrap.py` + `check-codeforge-version-drift.sh`) | **Detect only** — filesystem touch 0 + network call 0 invariant | `hooks/session-start` (plain stdout SSOT) |
| **UpgradeAgent** (Wave 2 Story-3 carrier) | **Plan + Apply** — dry-run preview + state reconciliation execution + sanity check + event log artifact | `templates/agents/UpgradeAgent.md` |
| **CLI** (`scripts/codeforge-upgrade.{sh,ps1}`) | **단일 진입점** — POSIX + PowerShell cross-platform user-facing command | `scripts/codeforge-upgrade.sh` + `.ps1` |

## External pattern reference

| System | Desired state | Current state | Diff | Apply | Snapshot |
|---|---|---|---|---|---|
| **Helm** | Chart values.yaml | Cluster K8s resource | `helm diff` | `helm upgrade` | release history (revision N) |
| **Terraform** | `.tf` files | State file | `terraform plan` | `terraform apply` | state versioning (S3 backend) |
| **Kustomize** | base + overlay | Manifests | `kustomize build` | `kubectl apply` | git tag |
| **Ansible** | playbook | inventory state | `--check` mode | `ansible-playbook` | (없음 — idempotent only) |
| **codeforge (ADR-076)** | wrapper SSOT 영역 enumeration | consumer overlay + plugin install state | `--dry-run` | `--apply` | upgrade event log + snapshot file |

**가장 정합한 reference = Helm 패턴** (release history revision N = rollback sentinel). Terraform state file 패턴 = too heavy (codeforge 는 file-system declarative, state cache 불필요). Kustomize overlay = customization marker block (D4) 와 conceptually 가장 가까움.

## Conceptual boundary (다른 도메인 영역과의 disjoint)

| 도메인 | Boundary 시점 | 본 entry 와의 관계 |
|---|---|---|
| **ADR-027 consumer adoption protocol** | bootstrap detection + 3-trigger enforcement | trigger 시점 disjoint (ADR-027 = bootstrap + Story phase / ADR-076 = upgrade event). Layer disjoint (ADR-027 = detection layer / ADR-076 = execution layer). |
| **ADR-053 구조적 변경 재구동** | 다음 작업 진입 blocking 조건 | ADR-053 D2 (marketplace sync + consumer install + version drift PASS) = 본 ADR-076 transaction completion criterion prerequisite. 정합 (sequential dependency). |
| **ADR-067 FIX ledger RESET** | Story §10 lane FIX cycle 재시작 | snapshot ↔ RESET disjoint layer (Invariant 2 verbatim). |
| **ADR-038 SessionStart hook static invariant** | filesystem touch 0 + network call 0 | hook = detect / UpgradeAgent = execute 분리 (Invariant 4 verbatim). |
| **ADR-016 marketplace registration policy** | codeforge family 7 plugin 등록 + mirrored field sync | family scope unit = 7 plugin atomic (Invariant 3 verbatim). |
| **ADR-039 subagent default** | Orchestrator 의 모든 work = subagent spawn (inline whitelist 외) | UpgradeAgent = subagent 등록 정합 (Story-3 carrier 영역). |

## 관련 ADR

- **Carrier ADR**: `docs/adr/ADR-076-declarative-reconciliation-upgrade.md` (ArchitectAgent 신설 — Phase 1 PR scope)
- **Contract SSOT**: `docs/inter-plugin-contracts/reconcile-protocol-v1.md` (kind:registry, sibling sync 면제 — ADR-010 §결정 2)
- **Parent Epic Issue**: https://github.com/mclayer/plugin-codeforge/issues/699
- **본 Story Issue**: https://github.com/mclayer/plugin-codeforge/issues/701 (Wave 1 Story-1)
- **Sequential prerequisite Story**: CFP-702 (Wave 1 Story-2 — D4 customization marker)
- **Runtime carrier Story**: CFP-743 (Wave 2 Story-3 — UpgradeAgent + CLI). KEY 정정: Wave 1 작성 시점 placeholder `CFP-703` → 실제 발의 Issue `CFP-743` (동일 Story, fact 영향 0, 추적성만 정정 — ADR-068 I-4 wording SSOT 정합)
- **Atomicity carrier Story**: (Wave 2 Story-4 — 7 plugin atomic upgrade)
- **3-way merge carrier Story**: (Wave 2 Story-5 — overlay 영역 reconcile 통합)

직접 cross-ref ADR 목록: ADR-076 / ADR-027 / ADR-053 / ADR-067 / ADR-038 / ADR-016 / ADR-008 / ADR-010 / ADR-058 / ADR-064 / ADR-039 / ADR-040 / ADR-073.

## 알려진 한계 (본 v1 정의 영역 외)

- **Multi-version coexistence** (LTS / latest 분리 발행) — Wave 4 sub-Epic E1 영역. 본 entry = single linear version progression scope.
- **Breaking change codemod registry** (MAJOR bump 시 사용자 코드 자동 변환 — npm/Next.js 패턴) — Wave 4 sub-Epic E2 영역.
- **Plugin uninstall protocol** (반대 방향 cleanup) — Wave 4 sub-Epic E3 영역.
- **3-way merge binary file 영역** — git merge-file 차용 가능하나 binary (image / pdf) 영역 불가. Wave 2 Story-5 carrier 의 fallback behavior 결정 영역.

## 변경 이력

- 2026-05-15 — Initial creation (CFP-701 carrier, RequirementsPL self-write — CFP-26 Phase 0a owner agent direct write 정합)
- 2026-05-15 — ADR-074 → ADR-076 swap (parallel session anomaly resolution — CFP-708 / CFP-709 chronological precedence per PR #712 verbatim, user-confirmed Branch A via codeforge:user-dialog-mode skill)
- 2026-05-15 — Section schema rename (Summary → 정의 / Conceptual model + Key invariants 분리 → 컨텍스트 + 핵심 규칙 + 경계 / Cross-reference → 관련 ADR / Update history → 변경 이력, CFP-701 ArchitectPL Phase 3 self-check 결과 — schema lint PASS prerequisite)
- 2026-05-15 — Customization marker (D4) detail 보강 (CFP-702 Wave 1 Story-2 carrier, RequirementsPL self-write — Customization layer 영역 marker pair syntax / ownership 모델 / 부재 fallback / Ansible blockinfile prior art / Story-5 downstream 의존 추가. Story-1 placeholder → CFP-702 narrative anchor 전환. 실 ADR-027 Amendment 3 §결정 본문 = ADR file SSOT)
