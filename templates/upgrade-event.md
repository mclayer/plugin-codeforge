---
# CFP-743 C2 event log schema — upgrade-event.md
# 사용: docs/upgrade-events/<YYYY-MM-DD>-<version>.md 자동 생성 시 본 template 준수
# doc type: upgrade_events (docs/doc-locations.yaml SSOT)
doc_type: upgrade_event
version_pre: ""          # upgrade 전 plugin version (semver)
version_post: ""         # upgrade 후 plugin version (semver)
mode: ""                 # dry_run | transaction | snapshot_restore
timestamp_kst: ""        # 이벤트 발생 시각 KST (YYYY-MM-DDTHH:MM:SS+09:00)
result: ""               # SUCCESS | ABORT | ROLLBACK | DRY_RUN_ONLY
snapshot_path: ""        # consumer .claude/_snapshots/<UTC-ts>-<version-pre>.tar.gz (apply mode 만)
snapshot_checksum: ""    # SHA-256 hex (apply mode 만)
---

# codeforge Upgrade Event — `<version_pre>` → `<version_post>`

**발생 시각**: `<timestamp_kst>` (KST)
**모드**: `<mode>`
**결과**: `<result>`

## 스냅샷 정보 (apply mode)

| 항목 | 값 |
|---|---|
| snapshot 경로 | `<snapshot_path>` |
| checksum (SHA-256) | `<snapshot_checksum>` |
| retention (N=5) | `<snapshot_retention_status>` |

## 9 영역 reconcile 결과

| 도메인 | desired state source | result | 비고 |
|---|---|---|---|
| github_workflow | `templates/github-workflows/*.yml` | PASS/CHANGED/SKIP/ABORT | |
| session_start_hook | `hooks/hooks.json + hooks/session-start` | PASS/CHANGED/SKIP/ABORT | |
| label_taxonomy | `docs/inter-plugin-contracts/label-registry-v2.md` | PASS/CHANGED/SKIP/ABORT | |
| settings_json_toggle | `templates/.claude/settings.json.sample` | PASS/CHANGED/SKIP/ABORT | |
| codeowners | `templates/CODEOWNERS.template` | PASS/CHANGED/SKIP/ABORT | |
| issue_templates | `templates/.github/ISSUE_TEMPLATE/*.yml` | PASS/CHANGED/SKIP/ABORT | |
| branch_protection | `.github/branch-protection-manifest.json` | PASS/CHANGED/SKIP/ABORT | |
| plugin_json_mirrored | `.claude-plugin/plugin.json [mirrored fields]` | PASS/CHANGED/SKIP/ABORT | |
| changelog | `CHANGELOG.md` | PASS/CHANGED/SKIP/ABORT | |

## 사후 sanity check 결과 (C3)

| 검사 | 결과 | 비고 |
|---|---|---|
| (a) workflow lint | PASS/FAIL | `scripts/check-workflow-yaml.sh` |
| (b) hook signature | PASS/FAIL | filesystem touch 0 / network 0 invariant |
| (c) label registry 정합 | PASS/FAIL | `scripts/check-label-registry.sh` |
| version drift check | PASS/FAIL | `scripts/check-codeforge-version-drift.sh` |

**사후 sanity check 실패 시**: automatic_rollback_to_snapshot (prompt 0 — reconcile-protocol-v1 Rule 3.1.3)

## 실패/중단 이력 (존재 시)

| 이벤트 | 상세 | 처리 결과 |
|---|---|---|
| `<event_type>` | `<detail>` | `<action_taken>` |

<!-- event_type 예시:
  path_normalization_failure — §4.5 abort-before-touch
  snapshot_creation_failure — disk-space 부족 등, abort
  pat_scope_insufficient — PAT scope 부족, PR-open-failure → abort+restore
  github_api_failure — 5xx/rate-limit, abort+restore
  sanity_check_failure — 사후 검증 실패, automatic_rollback
  toctou_drift_detected — dry-run↔apply state drift (§7.4.1(d))
  transaction_interrupted — SIGKILL/power-loss, next-invocation rollback
-->

## Wholesale mirror losses (marker block 부재 consumer)

<!-- reconcile-protocol-v1 Rule 3.2.2: marker block 부재 시 wholesale mirror 후 본 섹션 기록 의무 -->
<!-- marker block 이 정상 도입된 consumer 는 본 섹션 N/A -->

해당 없음 (marker block 정상 도입)

<!-- marker block 부재 시 아래 형식으로 기록:
## Wholesale mirror losses

다음 파일은 consumer customization 이 wrapper SSOT 로 wholesale mirror 되었습니다.
`scripts/migrate-existing-customization.sh` 를 사용해 retroactive marker wrap 가능합니다.

| 파일 | 이전 consumer 내용 요약 | wholesale mirror 후 상태 |
|---|---|---|
| `.github/workflows/example.yml` | consumer customization 존재 | wrapper SSOT 로 덮어씀 |
-->

## 참조

- reconcile-protocol-v1 v1.2: `docs/inter-plugin-contracts/reconcile-protocol-v1.md`
- ADR-076 §결정 1-8: `docs/adr/ADR-076-declarative-reconciliation-upgrade.md`
- UpgradeAgent: `templates/agents/UpgradeAgent.md`
- CLI: `scripts/codeforge-upgrade.sh` / `scripts/codeforge-upgrade.ps1`
