---
adr_number: 83
title: Consumer-applicability filter — repo-kind detection truth-table + positive whitelist (Epic CFP-858 결함 2)
status: Accepted
category: governance
date: 2026-05-18
carrier_story: CFP-899
parent_epic: CFP-858
supersedes: null
amends: null
amendments: []
amendment_log: []
related_stories:
  - CFP-899  # carrier (Wave 4 sub-Epic CFP-858 S2 base layer — S3 CFP-900 prerequisite)
  - CFP-898  # sibling S1 (dependency bundle integrity binding — closure resolver hook pattern 답습)
  - CFP-900  # sibling S3 (upgrade-event result enum — repo-kind detection 결과의 upgrade event log carrier)
related_adrs:
  - ADR-076  # declarative reconciliation upgrade flow (본 ADR = §결정 2 11 영역 wholesale_mirror semantic 의 consumer-applicability gating layer)
  - ADR-027  # consumer adoption protocol (boundary disjoint — ADR-027 = consumer-side template adoption SSOT, ADR-083 = wrapper-side filter SSOT, sibling Amendment 6 §결정 10 carrier)
  - ADR-040  # mechanical_enforcement_actions[] frontmatter 의무 (governance category)
  - ADR-058  # is_transitional + 해소 기준 의무 (false 정합 = permanent architecture invariant)
  - ADR-064  # CFP scope unitary (단일 filter SSOT — repo-kind + whitelist 영역별 분할 아님)
  - ADR-068  # I-1 API contract semantic completeness (4-way enum) + I-4 wording SSOT (consumer/plugin/mixed/unknown term)
  - ADR-070  # Codex verify-before-trust (본 ADR = consumer signal trust 영역 정의)
  - ADR-082  # Write-time self-write verification mandate (`mechanical_enforcement_actions: []` known-limitation declaration-only retain pattern 답습)
  - ADR-005  # dual-channel template ↔ live byte-identical mirror (consumer-applicability filter = `templates/` 영역 ↔ `.github/` self-app dual-channel 의 filtering layer)
  - ADR-016  # marketplace family scope (consumer-applicability filter scope 가 family 7 plugin atomic 범위 정합)
related_files:
  - docs/adr/ADR-RESERVATION.md  # row 83 reserved → active (CFP-899)
  - docs/adr/ADR-027-consumer-adoption-protocol.md  # Amendment 6 §결정 10 sibling carrier (consumer adoption signal SSOT cross-ref)
  - docs/adr/ADR-076-declarative-reconciliation-upgrade.md  # §결정 2 11 영역 enumeration 의 wholesale_mirror branch gating layer
  - docs/inter-plugin-contracts/reconcile-protocol-v1.md  # v1.9 §4.12 consumer_applicability_filter_binding block carrier
  - docs/inter-plugin-contracts/MANIFEST.yaml  # reconcile-protocol-v1 v1.8 → v1.9 row update
  - docs/parallel-work/section-ownership.yaml  # ADR-083 + reconcile-protocol-v1 §4.12 lock row append
  - CLAUDE.md  # ADR-083 cross-ref + reconcile-protocol-v1 v1.8 → v1.9 stale text 정정
  - templates/consumer_applicable_workflows.txt  # Phase 2 carrier (positive whitelist SSOT, append-only — DataMigrationArch §11 schema)
  - templates/scripts/detect-repo-kind.py  # Phase 2 carrier (ADR-061 외부 .py file 의무 — repo-kind detection truth-table 실 구현)
  - templates/scripts/mirror-dependency-closure.py  # CFP-898 §4.11 closure resolver — 본 ADR §결정 5 filter hook 과 sequential composition (filter 먼저 → closure 다음)
  - scripts/reconcile-overlay.sh  # MARKER_NONE branch line 437 직전 filter hook insertion (CFP-898 closure resolver hook pattern 답습, layer 1 추가 algorithm 재구현 0)
is_transitional: false   # ADR-058 §결정 5 — permanent architecture invariant. consumer-applicability filter = codeforge family upgrade flow 의 영구 구조 결정 (Epic CFP-858 결함 2 = wholesale_mirror branch 무차별 유입 의 super-class 차단). 약화 방향 (whitelist 축소 / fail-closed unknown → fail-open) = ADR-058 §결정 5 sunset_justification 차단 (top-down ratchet 강화 only — ADR-064 §self-application 정합).
mechanical_enforcement_actions:
  - action: consumer-applicability-filter-detection
    decision_binding: "§결정 5 — reconcile-overlay.sh MARKER_NONE branch filter hook (consumer signal detect → whitelist filter → fail-closed unknown). evidence-checks-registry warning tier entry (Phase 2 carrier — `templates/scripts/detect-repo-kind.py` 실 구현 + tests/test_detect_repo_kind.py 18 TC + tests/integration/test_reconcile_overlay_consumer_filter.bats integration after Phase 2 PR)"
    status: declaration-only-Wave-1   # ADR-082 §결정 6 declaration-only retain pattern 답습 (ADR-RESERVATION row 81 CFP-819 / row 82 CFP-776 동일 패턴)
    progress_note: "ADR-083 Phase 1 신설 시점 — 신규 lint script 신설 0건 (Phase 2 PR 영역). evidence-checks-registry yaml row append + lint script 실 wire = Phase 2 Develop lane carrier. Wave 1 = behavioral mandate (ArchitectAgent / DesignReviewPL self-check + reconcile-overlay.sh hook 의무) + Phase 2 = mechanical enforcement (test suite + workflow yml + drift detection). status 승격 trigger = Phase 2 PR merge + Wave 4 sub-Epic CFP-858 S3 (CFP-900) closure (upgrade-event result enum 의 SUCCESS_FILTERED branch report)."
sunset_justification: "N/A — permanent governance policy 의 architecture invariant. ADR-064 §self-application top-down ratchet 정합 — consumer-applicability filter 영구화는 wholesale_mirror branch 의 silent harm (mctrader-data#81 14 failing checks evidence) 차단 의 super-class. 약화 방향 (filter 약화 / fail-open default / whitelist 축소) 발의 차단."
---

## Context — wholesale_mirror 무차별 유입 의 silent harm

Epic CFP-858 (Wave 4 sub-Epic) = `reconcile-protocol-v1` v1.7 §4.11 (CFP-898 S1) dependency bundle integrity binding 으로 **closure missing** 영역은 fail-closed 차단. 그러나 **closure 가 full 인 wrapper-only workflow yml 가 consumer repo 로 무차별 유입** 시 silent harm 의 별 super-class 가 존속 — mctrader-data#81 14 failing checks evidence (Epic CFP-858 §1 motivation verbatim).

### 결함 2 evidence (mctrader-data#81 14 failing checks)

| Failing check | 원인 | 결함 분류 |
|---|---|---|
| `phase-gate-mergeable` | wrapper-only workflow (codeforge dogfood self-app — phase:* label invariant) 가 consumer repo 로 유입 → consumer repo 에 phase 라벨 없음 → 무조건 fail | 무차별 유입 — closure full 이나 consumer-side semantic gap |
| `lane-evidence-check` | wrapper-only workflow (codeforge Story §14 Lane Evidence SSOT) → consumer repo Story 없음 → fail | 동일 |
| `parallel-epic-conflict-check` | wrapper-only (codeforge Epic open 사이 conflict 검출) | 동일 |
| `worktree-first-*` (4종) | wrapper-only (codeforge worktree 의무) | 동일 |
| `marketplace-drift-detection` | wrapper-only (codeforge plugin family marketplace sync) | 동일 |
| ... (remaining 7) | wrapper-only 패턴 동형 | 동일 |

**Root cause**: `reconcile-overlay.sh` MARKER_NONE branch = wholesale_mirror — wrapper `.github/workflows/*.yml` 전체 byte-identical copy. consumer-applicability 판단 0 → wrapper dogfood workflow (76 .yml 중 N개 consumer-non-applicable) 가 consumer repo 에 silent 유입 → consumer repo 의 GitHub Actions 매번 fail.

**super-class**: 본 결함 = closure missing 의 dual — closure full but **consumer semantic incompatible**. ADR-076 §결정 2 11 영역 enumeration 자체가 wrapper SSOT desired state 단위 — 그러나 consumer-applicability 차원은 enumeration 영역 외 (orthogonal axis).

### 기존 SSOT 의 한계

- ADR-076 §결정 2 11 영역 = wrapper SSOT desired state enumeration (consumer-applicability 차원 0)
- ADR-027 §결정 1 + Amendment 3 §결정 7 = consumer adoption D4 marker (consumer customization preserve — wrapper-side filter 0)
- ADR-076 §결정 6 + Amendment 1 = MARKER_NONE wholesale_mirror_with_user_visible_loss_report (loss report only — filter 0)
- reconcile-protocol-v1 v1.7 §4.11 (CFP-898) = dependency bundle integrity (closure missing 차단 only — closure full 무차별 유입 영역 외)
- CFP-898 closure resolver = workflow yml ↔ scripts/ closure (vertical bundle) — consumer-applicability filter = wrapper-only vs consumer-applicable (horizontal axis), disjoint super-class

본 ADR-083 = **horizontal filter layer 1단 신설** (CFP-898 §4.11 vertical closure 위에 sequential composition).

## 결정

### 결정 1 — 4-way repo-kind detection truth-table

`templates/scripts/detect-repo-kind.py` (Phase 2 carrier, ADR-061 외부 .py file 의무) 가 consumer / plugin / mixed / unknown 4-way enum 분류.

| Signal A: `.claude-plugin/plugin.json` 존재 | Signal B: `.claude/_overlay/project.yaml` 존재 | repo_kind | rationale |
|---|---|---|---|
| ✅ | ❌ | `plugin` | wrapper-only repo (codeforge family plugin 자체) — full workflow set 적용 |
| ❌ | ✅ | `consumer` | consumer repo — positive whitelist 만 적용 (filter active) |
| ✅ | ✅ | `mixed` | dogfood repo (codeforge wrapper repo 자체 — `.claude-plugin/plugin.json` + 자기 자신의 `.claude/_overlay/project.yaml`) — full workflow set 적용 (plugin 영역 우선, self-app exemption) |
| ❌ | ❌ | `unknown` | signal 부재 — fail-closed (no copy, abort with error log) |

**4-way enum closed-set**: `plugin` / `consumer` / `mixed` / `unknown`. open-set 확장 (예: `library` / `monorepo` 등) = 별 ADR carrier 영역 — 본 ADR scope 외.

**Signal filesystem-only invariant** (SecurityArch deputy primary recommendation): 두 signal 모두 consumer-side filesystem 안 — network call 0, gh api 0, marketplace.json membership check 0. 이유 = (a) offline-first invariant (ADR-066 PAT scope 최소화) / (b) trust boundary 명확 (filesystem-only = consumer 권한 area only, cross-repo trust 영역 0) / (c) primary signal 단일 read 비용 (file existence check) — `marketplace.json` 영역 cross-repo gh api 는 본 ADR scope 외 (별 ADR carrier).

### 결정 2 — Positive whitelist `consumer_applicable_workflows.txt`

`templates/consumer_applicable_workflows.txt` (Phase 2 carrier — DataMigrationArch §11 schema):

**Format**: plain text, 1-per-line, `#` prefix = comment, blank line = skip. 각 line = wrapper `.github/workflows/<filename>.yml` 의 relative filename (디렉토리 prefix 0). UTF-8 LF.

**예시 (declarative — Phase 2 PR 영역, 본 Phase 1 PR 시점 = schema declare only)**:

```text
# consumer-applicable workflows (CFP-899 §결정 2 SSOT)
# 각 line = wrapper .github/workflows/<filename>.yml relative filename
# `#` prefix = comment, blank = skip, UTF-8 LF

# === Consumer-applicable: codeforge Issue / PR / Story scaffolding ===
story-init.yml
phase-label-invariant.yml
auto-phase-label.yml
fix-ledger-sync.yml

# === Consumer-applicable: 일반 governance gate ===
phase-gate-mergeable.yml
post-merge-followup.yml

# (... Phase 2 PR 영역에서 76 wrapper workflows 검수 후 consumer-applicable subset 결정)
```

**Positive list invariant**: whitelist 안 = consumer copy / whitelist 밖 = consumer skip (wrapper-only). default = skip (fail-closed unknown semantic 동형 — 새 workflow yml 신설 시 whitelist 부재 = consumer-non-applicable default). **반대 (blacklist) 금지** — 새 workflow 신설 시 blacklist 부재 = consumer silent 유입 silent harm 재발 (Epic CFP-858 결함 2 root cause 재발).

### 결정 3 — Mixed repo handling (wrapper self-app exemption)

`repo_kind == "mixed"` (= codeforge wrapper repo 자체 — `.claude-plugin/plugin.json` + 자기 자신의 `.claude/_overlay/project.yaml` 양 존재) = **full workflow set 적용** (filter skip). 이유:

- wrapper self-app = ADR-005 dual-channel byte-identical mirror 의 self 영역 — wrapper 자체 `.github/workflows/*.yml` 76개 모두 적용 (codeforge dogfood self-app 의무)
- `mixed` 분류는 `plugin` 우선 적용 (filter 0) — 본 결정 = 분류 우선순위 invariant
- consumer signal (`.claude/_overlay/project.yaml`) 존재만으로 filter 활성 시 codeforge wrapper repo 자체가 self-filter → 자신의 dogfood workflow 손실 (self-loop bug)

**OpRiskArch deputy verify**: 본 wrapper repo (`mclayer/plugin-codeforge`) = mixed repo 검증 — `.claude-plugin/plugin.json` 존재 (codeforge plugin 자체) + `.claude/_overlay/project.yaml` 존재 (consumer overlay self-app dogfood) — `mixed` 분류 → full workflow set → 본 .github/workflows/76개 모두 적용 (현 상태 보존).

### 결정 4 — Fail-closed unknown (signal 부재 차단)

`repo_kind == "unknown"` (Signal A + Signal B 모두 부재) = **fail-closed** (no copy, abort with error log):

```text
[ERR] Consumer-applicability filter: repo_kind=unknown (.claude-plugin/plugin.json absent + .claude/_overlay/project.yaml absent)
[ERR] Reconcile-overlay aborted. Initialize consumer overlay (codeforge bootstrap) or run from a known repo kind.
[ERR] Exit code 1.
```

이유 = (a) silent default → wrapper-only 무차별 유입 silent harm 재발 (Epic CFP-858 결함 2 root cause) / (b) 명시적 fail = consumer-side 명시적 bootstrap 의무 (ADR-027 consumer adoption protocol 정합) / (c) ADR-076 §결정 6 Amendment 1 fail-closed clause 패턴 답습 (CFP-898 closure resolver `silent_skip_invariant: 0`).

**예외 0 invariant**: `--force-unknown-as-consumer` flag 신설 금지 (`hotfix-bypass:consumer-applicability-filter-detection` label 영역 외 — bypass label 은 PR-time mechanical enforcement 회피용, runtime fail-closed 회피는 위배 vector). 사용자가 unknown 영역에 reconcile 강제 적용 필요 시 = `.claude/_overlay/project.yaml` minimal bootstrap (consumer signal 활성) 의무.

### 결정 5 — Filter hook insertion point (CFP-898 closure resolver pattern 답습)

`scripts/reconcile-overlay.sh` MARKER_NONE branch (line 437 직전) = CFP-898 closure resolver hook 직후, cp 직전 추가 layer. **Sequential composition order**:

1. **CFP-898 closure resolver hook** (line 437 직전, 기존) — workflow yml + scripts/ closure missing 시 fail-closed
2. **CFP-899 consumer-applicability filter hook** (line 437 직전 추가, 본 ADR §결정 5) — closure full but consumer-non-applicable 시 skip (wholesale_mirror 영역 한정)
3. **cp 실행** (line 437~, 기존)

**Hook pattern** (CFP-898 §4.11 hook_integration verbatim 답습):

```bash
# CFP-899 §결정 5 — consumer-applicability filter hook (MARKER_NONE branch first-line after closure)
if [[ -n "${FILTER_REPO_KIND_PY:-}" ]] && [[ -x "${FILTER_REPO_KIND_PY}" || -f "${FILTER_REPO_KIND_PY}" ]]; then
  repo_kind=$(python3 "${FILTER_REPO_KIND_PY}" --target "${CONSUMER_ROOT}")
  case "${repo_kind}" in
    plugin|mixed)
      # full workflow set — filter skip, proceed to cp
      :
      ;;
    consumer)
      # positive whitelist filter — wrapper/.github/workflows/*.yml 각 file 에 대해 whitelist 검사 후 skip 결정
      filename=$(basename "${file}")
      if ! grep -qxF "${filename}" "${CONSUMER_APPLICABLE_WHITELIST}"; then
        echo "[INFO] Filter skip (consumer-non-applicable): ${filename}"
        continue   # skip cp for this file
      fi
      ;;
    unknown)
      echo "[ERR] Consumer-applicability filter: repo_kind=unknown" >&2
      return 1   # fail-closed (ABORT — caller patterns 1 / 2 답습)
      ;;
    *)
      echo "[ERR] Consumer-applicability filter: unknown repo_kind enum value '${repo_kind}'" >&2
      return 1
      ;;
  esac
fi
```

**Exit code contract** (CFP-898 §4.11 hook_integration `exit_code_contract` 답습):
- `0` = filter OK + proceed to cp
- `1` = filter abort (unknown repo_kind / detect-repo-kind.py error) → return 1 (ABORT) from reconcile-overlay.sh (CFP-898 MARKER_LINT return 2 와 분리 — filter 는 return 1, closure 는 return 2)
- `2` = filter warning (degraded — Phase 2 reserve, e.g., malformed whitelist file) → exit 0 from caller + warning log

**Env passthrough**:
- `FILTER_REPO_KIND_PY`: `templates/scripts/detect-repo-kind.py` absolute path
- `CONSUMER_APPLICABLE_WHITELIST`: `templates/consumer_applicable_workflows.txt` absolute path
- `CONSUMER_ROOT`: reconcile-overlay.sh detected consumer repo root

**Self-app exemption**: `templates/scripts/detect-repo-kind.py` = ADR-005 dual-channel template ↔ live byte-identical mirror rule 면제 영역 (CFP-898 `mirror-dependency-closure.py` 동형) — consumer-distributable, wrapper-side `scripts/` mirror 부재. Self-loop 0 invariant — 본 .py file 자체가 workflow yml 안 의존되지 않음 (Phase 2 TC 검증 의무).

### 결정 6 — Wrapper self-app verify (mixed repo 정합)

본 wrapper repo (`mclayer/plugin-codeforge`) = §결정 1 truth-table 적용 시 `mixed` 분류 → full workflow set 적용 → 현 76 .github/workflows/*.yml 모두 보존 (self-app 변경 0 invariant). Phase 2 TC 검증 의무 (TC-CAF-MIXED-1: 본 wrapper repo 에서 detect-repo-kind.py 실행 → `mixed` 출력 + reconcile-overlay.sh 실행 → 76 .yml 모두 적용 + 0 file skip).

**self-loop bug 차단**: `consumer` 분류 (consumer signal 활성 + plugin signal 부재) 가 wrapper repo 에 false-positive 적용되면 wrapper dogfood workflow 손실 — 본 wrapper repo `.claude-plugin/plugin.json` (codeforge plugin SSOT) 존재 보장으로 `mixed` 우선 분류 (§결정 3) 가 self-loop 차단.

## Decision

본 ADR-083 은 codeforge family upgrade flow 의 **horizontal consumer-applicability filter layer** 신설로 채택한다. CFP-898 §4.11 vertical closure resolver 와 sequential composition (filter 먼저 → closure 다음) 으로 reconcile-overlay.sh MARKER_NONE branch 의 silent harm super-class (wrapper-only 무차별 유입) 차단. 4-way truth-table + positive whitelist + mixed repo self-app exemption + fail-closed unknown 의 4-tuple invariant.

## Consequences

### Positive

- Epic CFP-858 결함 2 (mctrader-data#81 14 failing checks) silent harm super-class 차단
- ADR-076 §결정 2 11 영역 wrapper SSOT desired state 의 consumer-applicability gating layer 신설 (orthogonal axis 분리)
- CFP-898 closure resolver pattern 답습 — algorithm 재구현 0, hook layer 1 추가만
- Consumer offline-first invariant (filesystem-only signal, network call 0)
- Wrapper self-app dogfood 보존 (mixed repo full workflow set 적용)

### Negative

- Whitelist 유지 비용 — 새 workflow yml 신설 시 consumer-applicable 여부 명시 의무 (positive list invariant)
- 분류 우선순위 invariant (`mixed` = plugin 우선) 위배 시 wrapper self-app 손실 risk
- detect-repo-kind.py self-app exemption (ADR-005 면제 영역) 의 self-loop 0 invariant 위배 시 무한 재귀 risk (Phase 2 TC 검증 의무)

### Neutral

- 본 ADR Phase 1 = SSOT 등재 + schema declare only. Phase 2 = 실 구현 (`templates/scripts/detect-repo-kind.py` 신설 + `templates/consumer_applicable_workflows.txt` populate + reconcile-overlay.sh hook insertion + test suite + evidence-checks-registry warning tier entry wire)
- ADR-027 Amendment 6 §결정 10 sibling carrier (consumer adoption signal SSOT cross-ref — boundary disjoint 보존, ADR-083 = wrapper-side filter / ADR-027 = consumer-side template adoption)

## Cross-references

- **ADR-076** §결정 2 11 영역 enumeration = wrapper SSOT desired state — 본 ADR-083 = consumer-applicability gating layer 1단 추가 (orthogonal axis, ADR-076 본문 변경 0)
- **ADR-027 Amendment 6 §결정 10** = consumer adoption signal SSOT 정합 cross-ref (sibling carrier)
- **reconcile-protocol-v1 v1.9 §4.12** = `consumer_applicability_filter_binding` block (본 ADR carrier contract — 6 field schema)
- **CFP-898 §4.11 dependency bundle integrity binding** = vertical closure resolver layer (본 ADR-083 = horizontal filter layer, sequential composition)
- **ADR-082 §결정 6** `mechanical_enforcement_actions: []` declaration-only Wave 1 retain pattern 답습 (Phase 2 carrier deferred)
- **ADR-040 Amendment 3 §결정 7.C** governance category `mechanical_enforcement_actions[]` 의무 정합 — `consumer-applicability-filter-detection` entry (status: declaration-only-Wave-1)
