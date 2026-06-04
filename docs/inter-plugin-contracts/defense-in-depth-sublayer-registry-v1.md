---
kind: registry
registry: defense-in-depth-sublayer-registry
contract_name: defense-in-depth-sublayer-registry
version: "1.0"
status: Active
date: 2026-05-14
authors:
  - ArchitectAgent (CFP-709)
owner_adr: ADR-075
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/defense-in-depth-sublayer-registry-v1.md
sibling_sync_exempt: true  # ADR-010 §결정 2 정합 — kind:registry sibling sync 면제
carrier_story: CFP-709
related_adrs:
  - ADR-075  # 본 registry SSOT carrier
  - ADR-063  # marketplace atomic invariant — §결정 5 본문 표 sublayer enumeration source
  - ADR-008  # inter-plugin contract versioning
  - ADR-010  # sibling sync 면제 정합
  - ADR-060  # evidence-enforceable promotion framework — enforce_tier enum 정합
---

# Defense-in-depth sublayer registry v1.0

## 상태

`Active` (2026-05-14). ADR-075 §결정 1 carrier.

## 1. 목적

codeforge plugin family 의 marketplace ↔ plugin.json atomic invariant (ADR-063) defense-in-depth 의 **sublayer enumeration SSOT**. ADR-063 §결정 5 본문 표 의 sublayer enumeration 영역 의 registry pattern 분리 (ADR-075 §결정 5).

### 적용 영역

- sublayer = ADR-063 atomic invariant 의 defense layer 안 작동하는 작성/PR/local hook 단위 (proactive + reactive)
- sublayer 정보 (id / name / cfp_origin / stage / mechanism / trigger_event / enforce_tier / file_path / env_opt_in_flag / bypass_label / status) = 본 registry SSOT
- ADR-063 §결정 5 본문 표 의 비-sublayer 2 row (atomic invariant 정보) 는 ADR-063 본문 유지

### 4-layer defense 의 sublayer 분포 (ADR-063 §결정 13 정합)

| Layer | 시점 | sublayer registry 영역 |
|---|---|---|
| 1 (proactive) | ArchitectAgent §3 commit 직전 | ADR-063 §결정 9 (본 registry 영역 외 — ArchitectAgent self-check 단일 mechanism) |
| 2 (proactive) | Change Plan §13 declarative declare | ADR-063 §결정 9 (본 registry 영역 외 — declarative mandate) |
| 3 (proactive) | PR-time `pull_request` event | **본 registry 영역** (id=1 PR-time CI atomic = CFP-441) + ADR-063 §결정 11 description verbatim lint |
| 4 (reactive) | 24h scheduled cron | ADR-063 §결정 13 (Phase 2 carrier 영역 — 본 registry 와 별도 mechanism) |
| 추가 (local) | local pre-push hook | **본 registry 영역** (id=2 local pre-push advisory = CFP-447 / id=3 local pre-push auto-rebase guidance = CFP-477) |

## 2. Schema

| Field | Type | Required | 설명 |
|---|---|---|---|
| `id` | int | yes | sublayer registry 안 unique id (1부터 sequential) |
| `name` | string | yes | sublayer 명 1-line summary |
| `cfp_origin` | string | yes | sublayer 도입 carrier Story key (예: `CFP-441`) |
| `stage` | enum | yes | `pre_commit` / `pre_push` / `pull_request_event` / `post_merge` / `scheduled_cron` |
| `mechanism` | string | yes | sublayer 작동 방식 1-line summary |
| `trigger_event` | string | yes | sublayer 발화 trigger (예: "git push" / "pull_request open" / "24h cron") |
| `enforce_tier` | enum | yes | `advisory` / `warning` / `blocking-on-pr` / `blocking-on-merge` (ADR-060 4-tier enum 정합) |
| `file_path` | list[string] | yes | sublayer artifact file path (script + workflow + hook sample 등) |
| `env_opt_in_flag` | string | no | opt-in env var (예: `PRE_PUSH_AUTO_REBASE=1`) — opt-in sublayer 만 |
| `bypass_label` | string | no | bypass channel label (ADR-024 Amendment 3 §결정 6.A family member) — blocking tier 만 의무 |
| `status` | enum | yes | `active` / `deprecated` / `superseded` |

### enum 정의

- **`stage`** = sublayer 가 작동하는 lifecycle stage. 5-value enum:
  - `pre_commit` — git commit 직전 local hook
  - `pre_push` — git push 직전 local hook
  - `pull_request_event` — GitHub `pull_request` event (open / synchronize)
  - `post_merge` — PR merge 후
  - `scheduled_cron` — GitHub Actions schedule (cron)

- **`enforce_tier`** = sublayer enforcement 강도. ADR-060 4-tier enum 정합 + `advisory` (opt-in local hook 영역):
  - `advisory` — opt-in local hook, fail 시 warning print 만 (blocking 분기 env 미선언 시)
  - `warning` — workflow `continue-on-error: true`, fail 시 audit
  - `blocking-on-pr` — pull_request event 시 required check, fail 시 PR 차단
  - `blocking-on-merge` — branch protection required check, fail 시 merge 차단

## 3. 항목

### Entry 1: PR-time CI atomic

```yaml
- id: 1
  name: "PR-time CI atomic (3-file atomic 강제)"
  cfp_origin: CFP-441
  stage: pull_request_event
  mechanism: "PR open 시 plugin.json + CHANGELOG.md + marketplace.json mirrored field byte-identical verify, mismatch 시 PR 차단"
  trigger_event: "pull_request:opened / pull_request:synchronize"
  enforce_tier: blocking-on-pr
  file_path:
    - scripts/check-version-bump-atomic.sh
    - templates/github-workflows/version-bump-atomic-check.yml
    - .github/workflows/version-bump-atomic-check.yml  # self-app byte-identical mirror (ADR-005)
  env_opt_in_flag: null  # mandatory PR-time enforce, opt-in 영역 외
  bypass_label: hotfix-bypass:marketplace-atomic  # ADR-063 §결정 4 / ADR-024 Amendment 3
  status: active
```

### Entry 2: local pre-push advisory

```yaml
- id: 2
  name: "local pre-push advisory (BEHIND-rebase awareness + atomic local check)"
  cfp_origin: CFP-447
  stage: pre_push
  mechanism: "git push 직전 local hook 가 plugin.json + CHANGELOG.md + marketplace.json drift 사전 감지, advisory mode default + PRE_PUSH_BLOCKING=1 env 시 blocking 분기"
  trigger_event: "git push (local pre-push hook)"
  enforce_tier: advisory  # PRE_PUSH_BLOCKING=1 env 시 blocking-on-pr 분기
  file_path:
    - templates/.claude/hooks/pre-push.sh.sample
  env_opt_in_flag: PRE_PUSH_BLOCKING  # =1 시 blocking 분기
  bypass_label: null  # opt-in local hook 영역 — bypass label 영역 외
  status: active
```

### Entry 3: local pre-push auto-rebase guidance

```yaml
- id: 3
  name: "local pre-push auto-rebase guidance (BEHIND-rebase auto-detect + 4-line guidance)"
  cfp_origin: CFP-477
  stage: pre_push
  mechanism: "git push 직전 local hook 가 BEHIND main 자동 감지, advisory abort + 4-line `git pull --rebase origin main` guidance print (hook 안 직접 rebase 실행 금지 — git-scm hook semantics 정합)"
  trigger_event: "git push (local pre-push hook)"
  enforce_tier: advisory
  file_path:
    - templates/.claude/hooks/pre-push-auto-rebase.sh.sample
  env_opt_in_flag: PRE_PUSH_AUTO_REBASE  # =1 시 active
  bypass_label: null  # opt-in local hook 영역
  status: active
```

## 4. 변경 규칙

신규 sublayer (4th / 5th / ...) 도입 시:

1. **carrier Story 생성** — `codeforge-improvement` label + sublayer 도입 motivation 명시
2. **registry row append** — 본 file 의 `Sublayer entries` 섹션 아래 신규 entry append (id sequential)
3. **MANIFEST.yaml version bump** — `registries:` 블록 안 `defense-in-depth-sublayer-registry-v1` entry 의 version PATCH (entry 추가만) / MINOR (schema 변경 동반)
4. **ADR-063 본문 영향 0건** — §결정 5 본문 표 의 sublayer enumeration row 가 registry cross-ref 형식 이므로 본문 영향 없이 registry row append 만으로 sublayer 추가 완료

### Version bump 정책 (ADR-008 §결정 2 정합)

- **PATCH** (예: 1.0 → 1.1) — sublayer entry append 만 (schema 변경 0건)
- **MINOR** (예: 1.0 → 2.0 미해당, 1.0 → 1.1 PATCH 만) — schema 안 신규 optional field 추가
- **MAJOR** (예: 1.0 → 2.0) — schema breaking change (field rename / 의무화 / enum 값 제거)

(주의: kind:registry 의 PATCH/MINOR/MAJOR 정의 = ADR-008 §결정 2 정합. version field 1.0 = 첫 도입.)

## sibling sync exemption rationale (ADR-010 §결정 2 정합)

본 registry = kind:registry. sibling sync 면제 근거:

- **enumeration / lookup 영역** — sublayer metadata 검색 SSOT, inter-plugin handoff schema 아님
- **wrapper internal governance** — codeforge family 6 lane plugin 참조 영역 외 (wrapper plugin self-write boundary)
- **sibling repo mirror copy 의무 없음** — wrapper repo SSOT only

ADR-010 §결정 2 verbatim 정합 (kind:registry sibling sync 면제 정책).

## 관련 파일

- [`docs/adr/ADR-075-defense-in-depth-sublayer-registry.md`](../../archive/adr/ADR-075-defense-in-depth-sublayer-registry.md) — 본 registry carrier SSOT
- [`docs/adr/ADR-063-marketplace-atomic-invariant.md`](../../archive/adr/ADR-063-marketplace-atomic-invariant.md) — §결정 5 본문 표 sublayer enumeration source
- [`docs/inter-plugin-contracts/MANIFEST.yaml`](MANIFEST.yaml) — registries 블록 7번째 entry
- [`docs/adr/ADR-008-inter-plugin-contract-versioning.md`](../../archive/adr/ADR-008-inter-plugin-contract-versioning.md) — versioning policy
- [`docs/adr/ADR-010-inter-plugin-contract-sibling-sync.md`](../../archive/adr/ADR-010-inter-plugin-contract-sibling-sync.md) — sibling sync 면제
- [`docs/adr/ADR-060-evidence-enforceable-promotion-framework.md`](../../archive/adr/ADR-060-evidence-enforceable-promotion-framework.md) — enforce_tier enum 정합
