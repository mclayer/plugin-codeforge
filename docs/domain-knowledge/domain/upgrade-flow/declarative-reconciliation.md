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
  - CFP-703  # Wave 2 Story-3 (UpgradeAgent + CLI — runtime carrier)
created: 2026-05-15
updated: 2026-05-15
---

# codeforge upgrade flow 의 선언적 reconciliation 개념 정의

## Summary

codeforge upgrade 의 architecture 패턴 = **선언적 reconciliation** (Helm `helm upgrade` / Kubernetes Kustomize / Terraform plan-apply 패턴 차용). wrapper SSOT = desired state, consumer 측 overlay + plugin install = current state, upgrade 명령 = converge. 사용자 결정 분기 0 자리 (CLI argument 로 dry-run / rollback / apply fix, prompt 없음).

본 entry = ADR-076 §결정 본문의 narrative SSOT — codeforge 도메인 1st-class 정의 anchor. ArchitectAgent / DeveloperAgent / Researcher / DomainAgent / 후속 Wave carrier 가 참조하는 단일 정의.

## Conceptual model

### 3-layer state representation

| Layer | 정의 | 위치 | 책임 주체 |
|---|---|---|---|
| **Desired state** | wrapper SSOT 영역 enumeration (workflow / hook / label / overlay / settings.json / CODEOWNERS / Issue templates / branch protection) | `mclayer/plugin-codeforge` repo + 6 lane plugin repos | wrapper / lane plugin author |
| **Current state** | consumer `.claude/_overlay/` + `.claude/plugins/installed_plugins.json` + `.github/workflows/` + `.github/ISSUE_TEMPLATE/` 등 | consumer repo working tree + plugin install dir | consumer (정상) / drift detector (감지) |
| **Customization layer** | consumer 의 wrapper-managed marker block 밖 영역 — preserved patch layer | consumer overlay / hook / workflow file 안 `# BEGIN/END wrapper-managed` block 외 | consumer (preserve) |

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

## Cross-reference

- **Carrier ADR**: `docs/adr/ADR-076-declarative-reconciliation-upgrade.md` (ArchitectAgent 신설 — Phase 1 PR scope)
- **Contract**: `docs/inter-plugin-contracts/reconcile-protocol-v1.md` (kind:registry, sibling sync 면제 — ADR-010 §결정 2)
- **Parent Epic Issue**: https://github.com/mclayer/plugin-codeforge/issues/699
- **본 Story Issue**: https://github.com/mclayer/plugin-codeforge/issues/701 (Wave 1 Story-1)
- **Sequential prerequisite Story**: CFP-702 (Wave 1 Story-2 — D4 customization marker)
- **Runtime carrier Story**: CFP-703 (Wave 2 Story-3 — UpgradeAgent + CLI)
- **Atomicity carrier Story**: (Wave 2 Story-4 — 7 plugin atomic upgrade)
- **3-way merge carrier Story**: (Wave 2 Story-5 — overlay 영역 reconcile 통합)

## 알려진 한계 (본 v1 정의 영역 외)

- **Multi-version coexistence** (LTS / latest 분리 발행) — Wave 4 sub-Epic E1 영역. 본 entry = single linear version progression scope.
- **Breaking change codemod registry** (MAJOR bump 시 사용자 코드 자동 변환 — npm/Next.js 패턴) — Wave 4 sub-Epic E2 영역.
- **Plugin uninstall protocol** (반대 방향 cleanup) — Wave 4 sub-Epic E3 영역.
- **3-way merge binary file 영역** — git merge-file 차용 가능하나 binary (image / pdf) 영역 불가. Wave 2 Story-5 carrier 의 fallback behavior 결정 영역.

## Update history

- 2026-05-15 — Initial creation (CFP-701 carrier, RequirementsPL self-write — CFP-26 Phase 0a owner agent direct write 정합)
