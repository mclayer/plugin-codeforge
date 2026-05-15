---
kind: registry
registry: label
version: "2.17"
status: Active
supersedes: label-registry-v1.md
created_by: CFP-140
created_date: 2026-05-09
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/label-registry-v2.md
date: 2026-05-15  # CFP-688 v2.17 — hotfix-bypass:actionlint 24번째 + hotfix-bypass:post-merge-followup-success-rate 25번째 family member (ADR-026 Amendment 3 §결정 5.G.b + §결정 5.G.d carriers — actionlint prevention layer + KPI detection sentinel, CFP-688 Phase 2 sub-PR (c)) | CFP-708 Phase 2 v2.16 back-ref: hotfix-bypass:claude-md-amendment-ref 23번째 family member (see below) | CFP-685 v2.16 — hotfix-bypass:auto-phase-label-sibling-parity 22번째 family member (ADR-065 §결정 1 row 3 carrier — templates ↔ self-app byte-identical parity warning-tier entry, CFP-609 retro Finding D carrier) | CFP-662 v2.15 — hotfix-bypass:bootstrap-labels 21번째 family member (ADR-060 Amendment 10 §결정 24 carrier — PR-time precondition check pattern 의 첫 baseline, RETRO-MCT-104 carrier 정합) | CFP-660 v2.14 — hotfix-bypass:workflow-version-drift 20번째 family member (ADR-032 Amendment 2 §결정 6 carrier — strict-eligible 5번째 drift consumer workflow version drift, CFP-660 Wave 2 of Epic CFP-431) | CFP-658 v2.13 — fallback:* family 신설 (fallback:manual + fallback:rate-limited, ADR-027 Amendment 2 §결정 6 carrier — Action-blocked agent direct write fallback path normative SSOT, post-CFP-627 v2.12 atomic rebase) | CFP-627 v2.12 — hotfix-bypass:marketplace-drift-detection 19번째 family member (ADR-063 Amendment 3 §결정 13 carrier — marketplace reactive scheduled drift detection 4th defense layer, post-CFP-638 base) | CFP-638 v2.11 — hotfix-bypass:stop-time-continuous-confirm 18번째 family member (ADR-064 Amendment 3 §결정 9 sister carrier — Continuous '진행해' 패턴 mechanical detect advisory channel) | CFP-631 v2.10 — hotfix-bypass:marketplace-description-verbatim 17번째 family member (ADR-063 Amendment 2 carrier — description proactive PR-time lint blocking-on-pr 직접 시작) | CFP-628 v2.9 — hotfix-bypass:retro-alert-pickup 16번째 family member (ADR-045 §D-5 retro alert pickup KPI warning-tier sentinel) | CFP-619 v2.8 — hotfix-bypass:retro-mandatory-deployed 15번째 family member (ADR-045 mandate restoration carrier) | CFP-610 v2.6 sub-entry — hotfix-bypass:wording-dictionary 13번째 (ADR-064 Amendment 2) | CFP-582 v2.6 sub-entry — hotfix-bypass:debate-convergence-quality 12번째 (ADR-059 Amendment 2 §결정 8) | CFP-583 v2.6 sub-entry — hotfix-bypass:workflow-yaml-parse 11번째 | CFP-530 v2.5 sub-entry — hotfix-bypass:workflow-permissions 10번째 | CFP-429 v2.5 — from-cfp-425-followup provenance label | CFP-521 v2.4 sub-entry — hotfix-bypass:sibling-pr-author-check 9번째 | CFP-506 v2.4 sub-entry — hotfix-bypass:claude-md-line-cap 8번째 | CFP-481 v2.4 — phase:* attach_owner_plugin field 갱신
authors:
  - Claude (CFP-140 — ADR-049 type:* → native Issue Types cutover)
related_adrs:
  - ADR-008 (contract versioning — MAJOR bump = label hack removal)
  - ADR-049 (CFP-140 — Issue Types native migration)
  - ADR-009 (CFP-31 — wrapper agent 0 invariant)
  - ADR-030 (CFP-123 — gate:live-entry-pass v1.3)
  - ADR-036 (CFP-260 — phase:reservation v1.4)
  - ADR-045 (CFP-138 — gate:retro-complete v1.5)
  - ADR-050 (CFP-344 — conflict:* + merge-order:* labels v2.1)
  - ADR-057 (CFP-393 — codeforge-kpi-alert + monitoring tier v2.2)
  - ADR-060 (CFP-393 — framework first non-sunset application + CFP-481 Amendment 4 — 3rd warning-tier entry auto-phase-label carrier)
  - ADR-005 (CFP-451 — self-application byte-identical .github/workflows copy)
  - ADR-024 (CFP-481 Amendment 4 — branch → phase mapping 표 SSOT + hotfix-bypass:auto-phase-label 7번째 family member)
  - ADR-012 (CFP-506 Amendment 1 — cap ratchet ≤320 + §3 scope 4-층 재해석)
  - ADR-051 (CFP-506 Amendment 1 — Draft → Accepted + anchor vs reference 판정자)
  - ADR-060 Amendment 5 (CFP-506 — 4th warning-tier entry claude-md-line-cap + hotfix-bypass:claude-md-line-cap 8번째 family member)
  - ADR-010 (CFP-521 Amendment 4 §결정 5 anti-misuse 안전망 — 5th warning-tier entry sibling-pr-label-author-check + hotfix-bypass:sibling-pr-author-check 9번째 family member)
  - ADR-040 Amendment 4 (CFP-429 — worktree-first enforcement closing the loop declaration carrier, gate FAIL 분기 후속 carrier `from-cfp-425-followup` provenance label 신설)
  - ADR-060 §결정 6 (CFP-429 — promotion gate 평가 FAIL = warning tier 유지 + actual 승격 follow-up CFP open mandate)
  - ADR-060 Amendment 8 (CFP-530 — N번째 warning-tier entry workflow-permissions-block-presence + hotfix-bypass:workflow-permissions 10번째 family member)
  - ADR-060 Amendment 9 (CFP-583 — 7th warning-tier entry workflow-yaml-parse + hotfix-bypass:workflow-yaml-parse 11번째 family member + 6 workflow yml BODY heredoc anti-pattern 정정 + framework zero-coverage sentinel 회복)
  - ADR-059 Amendment 2 (CFP-582 — convergence_quality_invariant 3 marker mechanical enforcement + debate-convergence-quality-marker-presence warning-tier entry + hotfix-bypass:debate-convergence-quality 12번째 family member)
  - ADR-024 Amendment 5 (CFP-582 — §결정 6.A per-entry namespace 의 12번째 family member hotfix-bypass:debate-convergence-quality 추가)
  - ADR-064 Amendment 2 (CFP-610 — wording-dictionary lint warning-tier entry + hotfix-bypass:wording-dictionary 13번째 family member)
  - ADR-045 §D-5 (CFP-628 Story 2 — retro alert pickup KPI warning-tier entry + hotfix-bypass:retro-alert-pickup 16번째 family member, ADR-060 framework 42번째 entry)
  - ADR-045 (CFP-619 — retro-mandatory.yml workflow byte-identical mirror deployment mandate restoration carrier + hotfix-bypass:retro-mandatory-deployed 15번째 family member, ADR-060 framework 41번째 entry)
  - ADR-005 (CFP-619 — templates/** ↔ .github/workflows/** byte-identical self-application invariant SSOT, retro-mandatory.yml mirror anchor)
  - ADR-063 Amendment 2 (CFP-631 — marketplace description verbatim PR-time proactive lint blocking-on-pr 직접 시작 carrier + hotfix-bypass:marketplace-description-verbatim 16번째 family member)
  - ADR-032 Amendment 2 (CFP-660 — strict-eligible 5번째 drift consumer workflow version drift, check 10 NEW carrier + hotfix-bypass:workflow-version-drift 20번째 family member, Wave 2 of Epic CFP-431)
  - ADR-060 Amendment 10 (CFP-662 — 10번째 warning-tier entry bootstrap-labels-precondition + hotfix-bypass:bootstrap-labels 21번째 family member + PR-time precondition check pattern 의 첫 baseline + RETRO-MCT-104 carrier)
  - ADR-065 §결정 1 row 3 (CFP-685 — templates ↔ self-app byte-identical parity warning-tier entry auto-phase-label-sibling-parity + hotfix-bypass:auto-phase-label-sibling-parity 22번째 family member, CFP-609 retro Finding D carrier)
related_files:
  - scripts/bootstrap-labels.sh (type:* 3 entry removed — CFP-140)
  - templates/issue-types.yaml (native Issue Types SSOT — CFP-140)
  - scripts/migrate-label-to-issue-type.sh (migration tool — CFP-140)
  - .github/workflows/phase-label-invariant.yml
  - .github/workflows/phase-gate-mergeable.yml
  - .github/workflows/fix-ledger-sync.yml
  - .github/workflows/subissue-from-impl-manifest.yml
  - .github/workflows/story-init.yml
---

# label-registry v2

## 변경 이력

**v2.17 (CFP-688 / ADR-026 Amendment 3 §결정 5.G.b + §결정 5.G.d, 2026-05-15)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 24번째 + 25번째 family member append, combined single version bump per Change Plan §2.3 coordination directive).
- **추가**: `hotfix-bypass:actionlint` (color `fef2c0` audit tier) — `templates/github-workflows/actionlint-check.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **24번째 hotfix-bypass:* family member** — 기존 23: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed / retro-alert-pickup / marketplace-description-verbatim / stop-time-continuous-confirm / marketplace-drift-detection / workflow-version-drift / bootstrap-labels / auto-phase-label-sibling-parity / claude-md-amendment-ref). ADR-026 Amendment 3 §결정 5.G.b carrier — actionlint prevention layer (born-broken 재발 차단 forcing function, CFP-688 P0 incident evidence).
- **추가**: `hotfix-bypass:post-merge-followup-success-rate` (color `fef2c0` audit tier) — `templates/github-workflows/post-merge-followup-success-rate-kpi.yml` KPI sentinel breach Issue auto-create conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **25번째 hotfix-bypass:* family member**). ADR-026 Amendment 3 §결정 5.G.d carrier — rolling 14-day success rate ≥ 90% sentinel, 9번째 warning-tier entry (ADR-026 §5.G.d 명시).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-23rd entry 동일). PR description `### Bypass reason` 섹션 기재 필수.
- `scripts/bootstrap-labels.sh` dynamic read 자동 흡수 (CFP-598 parse-hotfix-bypass-labels.py 분기 — yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.16 (CFP-685 / ADR-065 §결정 1 row 3, 2026-05-15)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 22번째 family member append).
- **추가**: `hotfix-bypass:auto-phase-label-sibling-parity` (color `fef2c0` audit tier) — `templates/github-workflows/sibling-workflow-parity.yml` (Phase 1 sub-PR (b) carrier) warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **22번째 hotfix-bypass:* family member** — 기존 21: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed / retro-alert-pickup / marketplace-description-verbatim / stop-time-continuous-confirm / marketplace-drift-detection / workflow-version-drift / bootstrap-labels).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-21st entry 동일). PR description `### Bypass reason` 섹션 기재 필수.
- ADR-065 §결정 1 row 3 carrier — templates/github-workflows/*.yml ↔ .github/workflows/*.yml SHA-256 byte-identical parity 검증 (warning tier, weekly cron + workflow_dispatch). CFP-609 retro Finding D (sibling workflow parity enforcement gap) 의 mechanical enforcement.
- `scripts/bootstrap-labels.sh` dynamic read 자동 흡수 (CFP-598 parse-hotfix-bypass-labels.py 분기 — yaml row 추가만으로 bootstrap 자동 반영, script 변경 0건).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.15 (CFP-662 / ADR-060 Amendment 10, 2026-05-14)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 21번째 family member append).
- **추가**: `hotfix-bypass:bootstrap-labels` (color `fef2c0` audit tier) — `templates/github-workflows/bootstrap-labels.yml` (Phase 2 carrier) warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **21번째 hotfix-bypass:* family member** — 기존 20: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed / retro-alert-pickup / marketplace-description-verbatim / stop-time-continuous-confirm / marketplace-drift-detection / workflow-version-drift).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-20th entry 동일). PR description `### Bypass reason` 섹션 기재 필수.
- ADR-060 Amendment 10 §결정 24 evidence-enforceable warning-tier entry `bootstrap-labels-precondition` carrier 동반 — consumer repo PR open 시 codeforge 필수 label set 부재 자동 감지 + bootstrap-labels.sh idempotent 호출 (RETRO-MCT-104 carrier, mctrader-data MCT-104 Phase 2 PR #14 2026-05-09 replay sentinel). PR-time precondition check pattern 의 첫 baseline (CFP-583 retro 후 framework legitimacy 회복 후 신규 entry 도입).
- `scripts/bootstrap-labels.sh` 무변경 (workflow body 가 본 script 외부 호출, ADR-061 §결정 1 외부 script convention reuse — multi-line shell embed 회피, CFP-583 BODY heredoc anti-pattern 차단). `hotfix-bypass:bootstrap-labels` row 는 CFP-598 dynamic read 분기 (parse-hotfix-bypass-labels.py) 가 자동 흡수 — script 변경 0건.
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.14 (CFP-660 / ADR-032 Amendment 2, 2026-05-14)**: MINOR bump (schema 무변경 — §3 yaml hotfix-bypass:* 20번째 family member append).
- **추가**: `hotfix-bypass:workflow-version-drift` (color `fef2c0` audit tier) — `overlay/hooks/check_bootstrap.py` check 10 runtime detection conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **20번째 hotfix-bypass:* family member** — 기존 19: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed / retro-alert-pickup / marketplace-description-verbatim / stop-time-continuous-confirm / marketplace-drift-detection).
- ADR-032 Amendment 2 §결정 6 carrier — strict-eligible drift 4 → 5종 확장 (consumer `.github/workflows/<name>.yml` SHA / 핵심 line drift vs wrapper templates). lane orchestration semantics divergence vector 차단 forcing function.
- evidence-checks-registry 45번째 entry `workflow-version-drift` (warning tier, owner_adr ADR-032 / carrier_adr ADR-060, status active).
- plugin.json MINOR bump 동반 (5.57.0 → 5.58.0) — marketplace.json sync required (ADR-063 §결정 1 atomic invariant, 별 sibling PR).

**v2.13 (CFP-658 / ADR-027 Amendment 2, 2026-05-14)**: MINOR bump (신규 `fallback` category enum + 2 entry first-class).
- **추가**: `fallback:manual` (color `c5def5` audit-trailed) — per-Issue ad-hoc override marker. Orchestrator 가 부착 시 `bootstrap.fallback_mode: action_blocked` (declarative trigger A) 와 무관 fallback path 활성. 우선순위 (C) > (A). ADR-027 Amendment 2 §결정 6.A carrier — Action 차단 환경 또는 일반 Action failure 시 manual agent direct write path 진입 의무.
- **추가**: `fallback:rate-limited` (color `c5def5` audit-trailed) — `manual-story-init-fallback.sh` (Phase 2 carrier) 의 exponential backoff (1s/2s/4s) max 3 retry 초과 시 silent skip + 자동 부착 label. OpRiskArch 조건 4 carrier (rate-limit detection + audit-trailed channel).
- **신규 category enum**: `fallback` — 기존 7 category (type / phase / gate / fix / hotfix / audit / hotfix-bypass / monitoring / conflict) 와 별 axis. ADR-008 §결정 1 BREAKING enum 추가 아님 — namespace 정합 (label name `fallback:` prefix 가 self-distinguishing). consumer overlay 영역 외, canonical-only.
- `comment-prefix-registry-v1` `[SECURITY-FALLBACK]` prefix 신설 (SecurityArch 조건 4 carrier) — 본 entry 와 동행, separate PR.
- `scripts/bootstrap-labels.sh` sync 동반 의무 (Phase 1 PR scope — fallback:* 2 entry 직접 hardcoded append, ADR-065 §결정 1 #1 self-check PASS gate).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
- ADR-063 §결정 18 정합: plugin.json MINOR bump 동반 (5.56.0 → 5.57.0) → marketplace.json sync required (별 PR, mclayer/marketplace repo, 선행 merge 의무).

**v2.10 (CFP-631 / ADR-063 Amendment 2, 2026-05-14)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 17번째 family member append). rebase race 4th sample 반영 (버전 재산정: 5.48.0 → 5.50.0).
- **추가**: `hotfix-bypass:marketplace-description-verbatim` (color `fef2c0` audit tier) — `templates/github-workflows/marketplace-description-verbatim.yml` (Phase 2 carrier) blocking-on-pr lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **17번째 hotfix-bypass:* family member** — CFP-598 backfill 12 entry + CFP-610 wording-dictionary 14th + CFP-619 retro-mandatory-deployed 15th + CFP-628 retro-alert-pickup 16th + 본 entry 17th. ADR-063 Amendment 2 §결정 11 mandate carrier — description PR-time mechanical proactive lint, blocking-on-pr 직접 시작 근거 = ADR-060 §결정 5 default warning explicit exception + §결정 19 Amendment 6 (CFP-509) auto_blocking manual gate path + 사용자 directive Story §1 verbatim).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.9 (CFP-628 / ADR-045 §D-5 + ADR-060 framework, 2026-05-14)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 16번째 family member append).
- **추가**: `hotfix-bypass:retro-alert-pickup` (color `fef2c0` audit tier) — retro-alert-pickup-rate KPI warning-tier entry 조건부 skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **16번째 hotfix-bypass:* family member** — 기존 15: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary / retro-mandatory-deployed).
- evidence-checks-registry.yaml entry `retro-alert-pickup-rate` (ADR-060 framework 42번째 entry, owner_adr: ADR-045, introduced_by: CFP-628, current_tier: warning) bypass_label 필드 정합.
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.8 (CFP-619 / ADR-045 + ADR-060 framework, 2026-05-14)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 15번째 family member append).
- **추가**: `hotfix-bypass:retro-mandatory-deployed` (color `fef2c0` audit tier) — `templates/github-workflows/retro-mandatory.yml` ↔ `.github/workflows/retro-mandatory.yml` byte-identical mirror deployment lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **15번째 hotfix-bypass:* family member** — CFP-598 backfill 12 entry + CFP-610 wording-dictionary 14th + 본 entry 15th. 기존 14: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality / wording-dictionary).
- evidence-checks-registry.yaml entry `retro-mandatory-deployed` (ADR-060 framework 41번째 entry, owner_adr: ADR-045, introduced_by: CFP-619, current_tier: warning) 의 `bypass_label` field 와 SSOT 양방향 정합 회복 (pre-existing CFP-619 Phase 1 leak — ArchitectAgent §5.5 self-check item #1 N/A 표기, 실제 FAIL. DesignReview F-3 P1 boundary-completeness finding 가 검출, FIX-1 resolution carrier).
- ADR-065 §결정 1 #1 self-check (label-registry sync) PASS gate 충족 — ArchitectPL verdict packet `mechanical_self_check_passed: true` 재발화 가능.
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-14th entry 동일). PR description `### Bypass reason` 섹션 기재 필수.
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row append = PATCH bump.

**v2.7 (CFP-598 / ADR-024 Amendment 3/5 §결정 6.A, 2026-05-14)**: PATCH bump (schema 무변경 — §3 yaml hotfix-bypass:* 12 row first-class backfill, 기존 prose-only entry 의 yaml 정규화).
- **추가**: `hotfix-bypass:*` 12종 §3 yaml first-class entry — adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality. pre-existing state: 12개 모두 §변경 이력 prose 에만 기록, §3 yaml row 부재 (bootstrap-labels.sh --dry-run 에서 hotfix-bypass:* 생성 불가 = pre-existing leak). backfill 로 DRY status 해소.
- `scripts/parse-hotfix-bypass-labels.py` 신설 — label-registry-v2.md §3 yaml block 안 `category: hotfix-bypass` row 동적 parse (ADR-061 외부 .py 정합).
- `scripts/bootstrap-labels.sh` hotfix-bypass:* dynamic read 분기 신설 (라인 125 component:* 직전 삽입).
- `scripts/check-bootstrap-labels-count.sh` 3-way parity 확장 (기존 2-way + §3 yaml hotfix-bypass:* row count 추가).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).
- ADR-008 §결정 3 SSOT: schema 무변경 yaml row backfill = PATCH bump.

**v2.6 추가 entry (CFP-610 / ADR-064 Amendment 2, 2026-05-13)**: same MINOR sub-entry append (frontmatter `version: "2.5"` 미변경, sub-row only — ADR-008 §결정 SemVer rule 안 same MINOR 안 additive sub-entry 허용).
- **추가**: `hotfix-bypass:wording-dictionary` (color `fef2c0` audit) — `templates/github-workflows/wording-dictionary.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **13번째 hotfix-bypass:* family member** — 기존 12: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse / debate-convergence-quality).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-12th entry 동일). PR description `### Bypass reason` 섹션 기재 필수.
- ADR-064 Amendment 2 wording-dictionary lint carrier 동반 — 카테고리 (a) forbid 어휘 (박제 / 못 박기 / pin / freezing) grep + 카테고리 (b) 어휘 (normative / sibling sync / kind:contract / ratchet / mirrored field) 평문 정의 동반 의무 advisory (ADR-060 framework warning-tier entry, 5 scope: docs/adr/** / docs/change-plans/** / CLAUDE.md / docs/orchestrator-playbook.md / templates/**).
- `scripts/bootstrap-labels.sh` sync 동반 의무 (Phase 2 PR scope — bootstrap labels 데이터 row append, ADR-065 §결정 1 #1 self-check PASS gate).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.6 추가 entry (CFP-582 / ADR-059 Amendment 2 §결정 8 / ADR-024 Amendment 5, 2026-05-13)**: same MINOR sub-entry append (frontmatter `version: "2.5"` 미변경, sub-row only — ADR-008 §결정 SemVer rule 안 same MINOR 안 additive sub-entry 허용).
- **추가**: `hotfix-bypass:debate-convergence-quality` (color `fef2c0` audit) — `templates/github-workflows/debate-convergence-quality.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 5 §결정 6.A per-entry namespace 정합, **12번째 hotfix-bypass:* family member** — 기존 11: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions / workflow-yaml-parse).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-11th entry 동일).
- ADR-059 Amendment 2 §결정 8 convergence_quality_invariant carrier 동반 — Story §9 debate transcript 내 3 marker (`[COUNTERARGUMENT]` / `[ALTERNATIVE_PROPOSED]` / `[DEBATE_PURPOSE_STATEMENT]`) section header 존재 여부 mechanical lint (debate-protocol-v1 v1.2 convergence_quality_invariant block 과 cross-validate, ADR-060 framework 첫 debate 영역 warning-tier entry).
- `scripts/bootstrap-labels.sh` sync 동반 의무 (Phase 2 PR scope — bootstrap labels 데이터 row append, ADR-065 §결정 1 #1 self-check PASS gate).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.6 추가 entry (CFP-583 / ADR-060 Amendment 9 §결정 22, 2026-05-13)**: same MINOR sub-entry append (frontmatter `version: "2.5"` 미변경, sub-row only — ADR-008 §결정 SemVer rule 안 same MINOR 안 additive sub-entry 허용. v2.5 → v2.6 marker 는 본 sub-entry append carrier 의 chronological provenance, frontmatter version bump 아님).
- **추가**: `hotfix-bypass:workflow-yaml-parse` (color `fef2c0` audit) — `templates/github-workflows/workflow-yaml-parse.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **11번째 hotfix-bypass:* family member** — 기존 10: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check / workflow-permissions).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-10th entry 동일).
- ADR-060 Amendment 9 §결정 22 evidence-enforceable warning-tier entry `workflow-yaml-parse` carrier 동반 — workflow yml PyYAML safe_load + actionlint dual validation mechanical lint (CFP-578 retro 후속 audit 결과 6 broken workflow file 의 yaml ScannerError sentinel 회복 + framework legitimacy 회복 carrier).
- §결정 23 (BODY heredoc anti-pattern + 정상 패턴 SSOT) 신설 cross-ref — printf format / ANSI-C bash quoting / external script 3 정상 패턴.
- `scripts/bootstrap-labels.sh` sync 동반 의무 (Phase 2 PR scope — bootstrap labels 데이터 row append, ADR-065 §결정 1 #1 self-check PASS gate).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.5 추가 entry (CFP-530 / ADR-060 Amendment 8 §결정 21, 2026-05-13)**: same MINOR sub-entry append (frontmatter `version: "2.5"` 미변경, sub-row only — ADR-008 §결정 SemVer rule 안 same MINOR 안 additive sub-entry 허용).
- **추가**: `hotfix-bypass:workflow-permissions` (color `fef2c0` audit) — `templates/github-workflows/workflow-permissions-check.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **10번째 hotfix-bypass:* family member** — 기존 9: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap / sibling-pr-author-check).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-9th entry 동일).
- ADR-060 Amendment 8 §결정 21 evidence-enforceable warning-tier entry `workflow-permissions-block-presence` carrier 동반 — workflow yml top-level `permissions:` block 부재 mechanical lint (CFP-506 PR #519 CodeQL 권고 + CFP-506 §11.1 entry 5 carrier 의무 + CFP-520 retro carrier reference 종합 해소).
- `scripts/bootstrap-labels.sh` sync 동반 의무 (Phase 2 PR scope — bootstrap labels 데이터 row append, ADR-065 §결정 1 #1 self-check PASS gate).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.5 (CFP-429 / ADR-040 Amendment 4 / ADR-060 §결정 6, 2026-05-13)**: MINOR bump.
- **추가**: `from-cfp-425-followup` (color `fbca04` yellow provenance) — Epic CFP-425 (worktree-first mechanical enforcement 영구화) gate FAIL 분기 후속 carrier marker. ADR-060 §결정 6 promotion gate (b) bypass 외 failure > 0 FAIL → 4 entry `current_tier: warning` 유지 + actual `warning → blocking-on-pr` 승격 follow-up Story open carrier 표식.
- ADR-040 Amendment 4 §결정 7.H (CFP-429 Phase 1) self-application closing the loop declaration 의 evidence row.
- `scripts/bootstrap-labels.sh` sync 동반 의무 (Phase 2 PR scope — provenance category data row append, ADR-065 §결정 1 #1 self-check PASS gate).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.4 추가 entry (CFP-521 / ADR-010 Amendment 4 §결정 5 / ADR-060, 2026-05-13)**: same MINOR sub-entry append (frontmatter `version: "2.4"` 미변경, sub-row only — ADR-008 §결정 SemVer rule 안 same MINOR 안 additive sub-entry 허용).
- **추가**: `hotfix-bypass:sibling-pr-author-check` (color `fef2c0` audit) — `templates/github-workflows/sibling-pr-label-author-check.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **9번째 hotfix-bypass:* family member** — 기존 8: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd} / claude-md-line-cap).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st-8th entry 동일).
- ADR-010 Amendment 4 §결정 5 anti-misuse 안전망 mechanical enforcement — EPIC-RESULTS-CFP-462 §6 carrier #2.
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.4 (CFP-481 / ADR-060 Amendment 4 / ADR-024 Amendment 4, 2026-05-12)**: MINOR bump.
- **갱신**: phase:* 8 label entry 의 `attach_owner_plugin` field — `auto-phase-label.yml` Action 자동 부착 owner 추가 (PR open 시 1순위 inference fallback chain 으로 부착, ADR-024 Amendment 4 §결정 6.A.1 branch → phase mapping 표 verbatim 사용).
- 기존 lane plugin self-write 영역 invariant 보전 — `auto-phase-label.yml` 가 `if: !contains(...labels.*.name, 'phase:')` 가드로 story-init.yml 가 만든 PR (이미 phase label 부착) skip → 책임 분리.
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.4 추가 entry (CFP-506 / ADR-012 Amendment 1 / ADR-060 Amendment 5, 2026-05-13)**: same MINOR sub-entry append (frontmatter `version: "2.4"` 미변경, sub-row only — ADR-008 §결정 SemVer rule 안 same MINOR 안 additive sub-entry 허용).
- **추가**: `hotfix-bypass:claude-md-line-cap` (color `fef2c0` audit) — `templates/github-workflows/claude-md-line-cap.yml` warning-tier mechanical lint conditional skip + audit comment 자동 발의 channel (ADR-024 Amendment 3 §결정 6.A per-entry namespace 정합, **8번째 hotfix-bypass:* family member** — 기존 7: adr-sunset / decision-principle-vocab / auto-phase-label / marketplace-atomic / worktree-first-{session-start-wire, pre-checkout, pre-commit-main-block, spawn-evidence-cwd}).
- bypass 사용 시 `check-bypass-audit-comment.sh` 가 audit comment 발의 (reuse 패턴, 1st/2nd/3rd entry 동일).
- `scripts/bootstrap-labels.sh` sync 동반 의무 (Phase 1 PR scope, ADR-065 §결정 1 #1 self-check PASS gate).
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.3 (CFP-451 / ADR-057 Amendment 2 / ADR-060 / ADR-005, 2026-05-12)**: MINOR bump.
- **추가**: `codeforge-kpi-infra-error` (color `d73a4a` red — severity / oncall) — rate-limit-fallback-kpi.yml workflow infrastructure failure (clone fail / aggregator script error / auto-PR fail). measurement alert (`codeforge-kpi-alert`) 와 분리된 channel — audience-based routing (oncall vs 정책 의사결정자).
- **추가**: `codeforge-kpi-update` (color `0e8a16` green — info / data refresh marker) — rate-limit-fallback-kpi.yml workflow 가 monthly cron 으로 발의하는 data-only refresh PR. **pre-existing leak 정정** (Codex F-451-001 (a)) — CFP-393 workflow line 237 에서 `gh pr create --label codeforge-kpi-update` 사용 중이었으나 registry / bootstrap 부재 (sub-issue carrier 미발의 leak).
- **monitoring tier sub-axis 다축 완결** (v2.2 의 "sub-axis 확장 자연" 선언 첫 다축 사례):
  - `codeforge-kpi-alert` (orange `f29513`) = severity:warn — measurement threshold violation
  - `codeforge-kpi-infra-error` (red `d73a4a`) = severity:error — infrastructure failure
  - `codeforge-kpi-update` (green `0e8a16`) = severity:info — data-only refresh marker
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.2 (CFP-393 / ADR-057 Amendment 2 / ADR-060, 2026-05-11)**: MINOR bump.
- **추가**: `codeforge-kpi-alert` — codeforge KPI threshold violation alert (CFP-393 ADR-057 fallback rate KPI dashboard, rate-limit-fallback-kpi.yml CI Action 자동 부착)
- **신규 tier**: `monitoring` — KPI / metric / dashboard / alert 영역. 기존 `audit` (후처리 분류) 와 분리. 향후 sub-axis (info / warn / error) 확장 자연.
- canonical-only (kind:registry — sibling sync scope 외 per ADR-010).

**v2.1 (CFP-344 / ADR-050, 2026-05-09)**: MINOR bump.
- **추가**: `conflict:file-overlap`, `conflict:adr-number`, `conflict:section-locked` — 병렬 에픽 충돌 감지 레이블 (parallel-epic-conflict-check.yml Actions 부착)
- **추가**: `merge-order:1`, `merge-order:2` — 충돌 시 merge 순서 프로토콜 (GitOpsAgent 부착)

**v2.0 (CFP-140 / ADR-049, 2026-05-09)**: MAJOR bump.
- **제거**: `type:epic`, `type:story`, `type:bug` — native GitHub Issue Types 로 대체
  - See: `templates/issue-types.yaml`, `scripts/migrate-label-to-issue-type.sh`
- **유지**: `impl-manifest` (별도 axis — sub-issue visual marker, non-breaking)
- **유지**: phase:* / gate:* / fix:* / hotfix:* / audit:* / category:* (전부 유지)

## 1. 목적

`bootstrap-labels.sh`가 생성하는 GitHub label SSOT (v2.3 시점 35+ 종 — type 1 / phase 8 / gate 4 / fix 4 / hotfix 2 / audit 12+ / category 7 / conflict 5 / monitoring 3).
`type:epic` / `type:story` / `type:bug` 는 native Issue Types 로 대체 (ADR-049).

## 2. Schema

각 label entry:

| 필드 | 타입 | 설명 |
|---|---|---|
| name | string | label 이름 (예: `phase:설계`) |
| category | enum | type / phase / gate / fix / hotfix / audit |
| color | string | 6자리 hex (gh label spec) |
| description | string | label 설명 |
| single_active | bool | 같은 category에서 1개만 active 가능 (phase만 true) |
| attach_owner_plugin | string | 부착 권한 plugin / Action |

## 3. 항목

```yaml
labels:
  # type:* — v2.0 변경사항
  # type:epic / type:story / type:bug = REMOVED (native Issue Types — ADR-049)
  # impl-manifest = RETAINED (sub-issue axis, non-breaking)

  - name: impl-manifest
    category: type
    color: "fbca04"
    description: "Sub-issue (Impl Manifest 파일 단위)"
    single_active: false
    attach_owner_plugin: "subissue-from-impl-manifest.yml CI Action (자동)"

  # phase:* (8종 — phase:reservation 포함, single-active enforced by phase-label-invariant.yml)
  - name: phase:요구사항
    category: phase
    color: "1d76db"
    description: "Phase: 요구사항"
    single_active: true
    attach_owner_plugin: "codeforge-requirements (CFP-37 후) / DocsAgent (CFP-32 시점) / story-init.yml (초기 부착) / auto-phase-label.yml (CFP-481 — PR open 시 branch=cfp-NNN/requirements 1순위 inference)"

  - name: phase:설계
    category: phase
    color: "1d76db"
    description: "Phase: 설계"
    single_active: true
    attach_owner_plugin: "codeforge-design (CFP-40 후) / DocsAgent (CFP-32 시점) / auto-phase-label.yml (CFP-481 — PR open 시 branch=cfp-NNN/design 1순위 inference)"

  - name: phase:설계-리뷰
    category: phase
    color: "1d76db"
    description: "Phase: 설계-리뷰"
    single_active: true
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점) / auto-phase-label.yml (CFP-481 — PR open 시 branch=cfp-NNN/design-review 1순위 inference + doc-only fast-path 3순위 terminal default)"

  - name: phase:구현
    category: phase
    color: "1d76db"
    description: "Phase: 구현"
    single_active: true
    attach_owner_plugin: "codeforge-develop (CFP-39 후) / DocsAgent (CFP-32 시점) / auto-phase-label.yml (CFP-481 — PR open 시 branch=cfp-NNN/develop 1순위 inference)"

  - name: phase:구현-리뷰
    category: phase
    color: "1d76db"
    description: "Phase: 구현-리뷰"
    single_active: true
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점) / auto-phase-label.yml (CFP-481 — PR open 시 branch=cfp-NNN/code-review 1순위 inference)"

  - name: phase:구현-테스트
    category: phase
    color: "1d76db"
    description: "Phase: 구현-테스트"
    single_active: true
    attach_owner_plugin: "codeforge-test (CFP-38 후) / DocsAgent (CFP-32 시점)"

  - name: phase:보안-테스트
    category: phase
    color: "1d76db"
    description: "Phase: 보안-테스트"
    single_active: true
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점) / auto-phase-label.yml (CFP-481 — PR open 시 branch=cfp-NNN/security-test 1순위 inference)"

  - name: phase:reservation
    category: phase
    color: "ededed"
    description: "Phase: reservation (CFP-260 / ADR-036 — brainstorming 시점 KEY 사전 확보, 30 일 미진행 시 reservation-cleanup.yml 자동 close. promote 시 phase:요구사항 으로 변경)"
    single_active: true
    attach_owner_plugin: "cfp-reserve.yml Issue Form (자동 첨부) / Orchestrator (수동 promote 시 detach) / auto-phase-label.yml (CFP-481 — Epic Phase N+1 close PR 3순위 terminal default)"

  # gate:* (4종) — gate:live-entry-pass added v1.3 (CFP-123 / ADR-030)
  - name: gate:design-review-pass
    category: gate
    color: "0e8a16"
    description: "Design review PASS"
    single_active: false
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점)"

  - name: gate:security-test-pass
    category: gate
    color: "0e8a16"
    description: "Security test PASS"
    single_active: false
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점)"

  - name: gate:live-entry-pass
    category: gate
    color: "0e8a16"
    description: "Live Epic lane-entry pass — 3-condition AND (mode==live + --confirm-live + isolated runtime) 충족"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (post-review-verdict step 4) / consumer CI 부착 (3-condition 검증 통과 시)"

  - name: gate:retro-complete
    category: gate
    color: "0e8a16"
    description: "Story 완료 회고 작성됨 (PMOAgent self-write — CFP-138 / ADR-045). 미부착 시 retro-mandatory.yml 가 Story Issue close 차단 (auto-reopen)."
    single_active: false
    attach_owner_plugin: "codeforge-pmo (PMOAgent self-write) — Phase 2 PR merge 후 retro write 완료 시 부착"

  # fix:* (4종, 누적 가능)
  - name: fix:설계-리뷰-retry
    category: fix
    color: "e99695"
    description: "FIX retry: 설계-리뷰"
    single_active: false
    attach_owner_plugin: "fix-ledger-sync.yml CI Action (자동)"

  - name: fix:구현-리뷰-retry
    category: fix
    color: "e99695"
    description: "FIX retry: 구현-리뷰"
    single_active: false
    attach_owner_plugin: "fix-ledger-sync.yml CI Action (자동)"

  - name: fix:구현-테스트-retry
    category: fix
    color: "e99695"
    description: "FIX retry: 구현-테스트"
    single_active: false
    attach_owner_plugin: "fix-ledger-sync.yml CI Action (자동)"

  - name: fix:보안-테스트-retry
    category: fix
    color: "e99695"
    description: "FIX retry: 보안-테스트"
    single_active: false
    attach_owner_plugin: "fix-ledger-sync.yml CI Action (자동)"

  # hotfix:* (2종)
  - name: hotfix:minimal
    category: hotfix
    color: "ff9999"
    description: "Hotfix minimal"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix 경로)"

  - name: hotfix:critical
    category: hotfix
    color: "ff0000"
    description: "Hotfix critical"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix 경로)"

  - name: audit:post-hotfix
    category: audit
    color: "fef2c0"
    description: "Post-hotfix audit Story"
    single_active: false
    attach_owner_plugin: "Orchestrator (hotfix merge 다음 세션 자동 부착)"

  # audit:debut-* (2종)
  - name: audit:debut-eval
    category: audit
    color: "fbca04"
    description: "데뷔 평가 (consumer 첫 사용 사례) 발견 사항"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (CFP-60 ADR-021 detection)"

  - name: audit:from-mctrader-debut
    category: audit
    color: "fef2c0"
    description: "mctrader 데뷔 평가에서 발견된 codeforge gap (첫 사례)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (CFP-60 mctrader 데뷔 평가)"

  - name: from-cfp-425-followup
    category: audit
    color: "fbca04"
    description: "Epic CFP-425 (worktree-first mechanical enforcement 영구화) gate FAIL 분기 후속 carrier marker. ADR-060 §결정 6 promotion gate (b) bypass 외 failure > 0 FAIL → 4 entry current_tier: warning 유지 + actual warning → blocking-on-pr 승격 follow-up Story open. 본 label 부착 Story = CFP-429 Amendment 4 declaration 후속 carrier 책임 (4 entry tier 승격 + 4 workflow continue-on-error: false + required_status_checks.contexts 부착 + plugin.json MINOR bump 등 evidence 6 산출물 i~vi 충족)."
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (CFP-429 Phase 2 PR description 안 conditional step gate FAIL 분기 자동 trigger) / GitOpsAgent (Issue create 위임)"

  - name: audit:spec-amendment
    category: audit
    color: "fbca04"
    description: "Mid-implementation spec doc 수정 PR (Codex push-back / 사용자 mid-impl clarification / spec drift 발견 시)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (playbook §6.8 spec amendment loop)"

  # early-close:* (3종 권장)
  - name: early-close:duplicate
    category: audit
    color: "d4c5f9"
    description: "다른 Story 와 중복 — early-close 정당화"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (CFP-90 phase invariant)"

  - name: early-close:reclassified
    category: audit
    color: "d4c5f9"
    description: "Out-of-scope 재분류 — 다른 Epic / 별도 Story 로 이전"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (CFP-90 phase invariant)"

  - name: early-close:epic-rolled-up
    category: audit
    color: "d4c5f9"
    description: "Epic 종료 시 child Story 일괄 close — Epic close PR 가 absorbing"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (CFP-90 phase invariant)"

  # category:* (7종) — CFP-60 debut-audit-triage-v1
  - name: category:lane-progression
    category: audit
    color: "0e8a16"
    description: "#1 — 7 lane 통과 / 막힘 (owner: PMOAgent)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (debut-audit-triage)"

  - name: category:agent-gap
    category: audit
    color: "d93f0b"
    description: "#2 — phase 별 gap + 과부하 (owner: ArchitectPL, ADR-021 R1-R4)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (scripts/check-debut-audit-signals.sh detection)"

  - name: category:decision-table
    category: audit
    color: "1d76db"
    description: "#3 — 원인 판정 row 모호 / 신규 (owner: wrapper Orchestrator)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator"

  - name: category:deputy-mandate
    category: audit
    color: "5319e7"
    description: "#4 — 6 deputy mandate 부족 (owner: ArchitectPL)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator"

  - name: category:workflow-invariant
    category: audit
    color: "bfd4f2"
    description: "#5 — GitHub Actions 강제 누락 (owner: wrapper Orchestrator)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator"

  - name: category:template
    category: audit
    color: "c5def5"
    description: "#6 — Story / Change Plan / ADR 필드 부족 (owner: per-template)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator"

  - name: category:contract-schema
    category: audit
    color: "bfdadc"
    description: "#7 — inter-plugin contract schema 부족 (owner: producer lane plugin)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator"

  # conflict:* (3종 — 병렬 에픽 충돌 감지, ADR-050)
  - name: conflict:file-overlap
    category: conflict
    color: "e4e669"
    description: "다른 open PR과 변경 파일 중복 (parallel-epic-conflict-check.yml 자동 감지)"
    single_active: false
    attach_owner_plugin: "parallel-epic-conflict-check.yml CI Action (자동)"

  - name: conflict:adr-number
    category: conflict
    color: "e4e669"
    description: "ADR-RESERVATION.md 동시 수정 감지 — ADR 번호 충돌 위험"
    single_active: false
    attach_owner_plugin: "parallel-epic-conflict-check.yml CI Action (자동)"

  - name: conflict:section-locked
    category: conflict
    color: "d93f0b"
    description: "section-ownership.yaml locked 섹션 동시 수정 감지 — merge 순서 조율 필요"
    single_active: false
    attach_owner_plugin: "parallel-epic-conflict-check.yml CI Action (자동)"

  # merge-order:* (2종 — 충돌 시 merge 순서 프로토콜, ADR-050)
  - name: merge-order:1
    category: conflict
    color: "0075ca"
    description: "병렬 에픽 충돌 시 먼저 merge해야 하는 PR (낮은 CFP 번호)"
    single_active: false
    attach_owner_plugin: "GitOpsAgent"

  - name: merge-order:2
    category: conflict
    color: "e4e669"
    description: "병렬 에픽 충돌 시 merge-order:1 완료 후 git rebase main 의무"
    single_active: false
    attach_owner_plugin: "GitOpsAgent"

  # monitoring:* (3종 — CFP-451 v2.3 sub-axis 다축 완결 / CFP-393 v2.2 신설 tier)
  # KPI / metric / dashboard / alert 영역. 기존 `audit` (후처리 분류) 와 분리.
  # sub-axis: info (data refresh) / warn (measurement alert) / error (infra failure).
  - name: codeforge-kpi-alert
    category: monitoring
    color: "f29513"
    description: "codeforge KPI threshold violation alert (CFP-393 ADR-057 fallback rate KPI dashboard). rate-limit-fallback-kpi.yml workflow 가 sample_size_sufficient=true AND fallback_rate_percent >= 1.0% 시 Issue auto-open. ADR-060 evidence-enforceable framework 첫 non-sunset application."
    single_active: false
    attach_owner_plugin: "rate-limit-fallback-kpi.yml CI Action (자동)"

  - name: codeforge-kpi-infra-error
    category: monitoring
    color: "d73a4a"
    description: "KPI workflow infrastructure failure — oncall investigation required. rate-limit-fallback-kpi.yml workflow 가 clone fail / aggregator script error / auto-PR fail detect 시 Issue auto-open. measurement alert (`codeforge-kpi-alert`) 와 분리된 channel — audience routing (oncall vs 정책 의사결정자). CFP-451 v2.3 sub-axis 다축 완결."
    single_active: false
    attach_owner_plugin: "rate-limit-fallback-kpi.yml CI Action (자동)"

  - name: codeforge-kpi-update
    category: monitoring
    color: "0e8a16"
    description: "KPI workflow data refresh PR — auto-merge eligible. rate-limit-fallback-kpi.yml workflow 가 monthly cron 으로 발의하는 docs/kpi/rate-limit-fallback.json 데이터 갱신 PR marker. CFP-451 v2.3 sub-axis 다축 완결 (pre-existing CFP-393 leak 정정 — Codex F-451-001 (a))."
    single_active: false
    attach_owner_plugin: "rate-limit-fallback-kpi.yml CI Action (자동)"

  # hotfix-bypass:* (16종 — ADR-024 Amendment 3/5 §결정 6.A per-entry namespace)
  # CFP-598 v2.7 PATCH backfill — §변경 이력 prose-only 상태에서 §3 yaml first-class 정규화.
  # color: fef2c0 (audit tier 동일 — bypass channel 은 audit 계열 색상 공유)
  # single_active: false (누적 가능 — 여러 entry bypass 동시 활성)
  # category: hotfix-bypass (별도 category enum — ADR-024 Amendment 3 §결정 6.A namespace)
  - name: hotfix-bypass:adr-sunset
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: adr-sunset-criteria lint 조건부 skip + audit comment 자동 발의 (CFP-389 / ADR-024 Amendment 3 §결정 6.A / ADR-060 §결정 7 — templates/github-workflows/adr-sunset-criteria.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:decision-principle-vocab
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: decision-principle-vocabulary lint 조건부 skip + audit comment 자동 발의 (CFP-449 / ADR-024 Amendment 3 §결정 6.A / ADR-060 §결정 5 — templates/github-workflows/decision-principle-vocabulary.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:auto-phase-label
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: auto-phase-label 조건부 skip + audit comment 자동 발의 (CFP-481 / ADR-024 Amendment 4 §결정 6.A.1 / ADR-060 Amendment 4 — templates/github-workflows/auto-phase-label.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:marketplace-atomic
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: marketplace ↔ plugin.json atomic invariant check 조건부 skip + audit comment 자동 발의 (CFP-441 / ADR-063 §결정 4 — templates/github-workflows/version-bump-atomic-check.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:worktree-session-start-wire
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: worktree-first-session-start-wire blocking-on-pr check 조건부 skip (CFP-427 / ADR-040 Amendment 3 §결정 7.D — templates/github-workflows/worktree-first-session-start-wire.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:worktree-pre-checkout
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: worktree-first-pre-checkout blocking-on-pr check 조건부 skip (CFP-428 / ADR-040 Amendment 3 §결정 7.D — templates/github-workflows/worktree-first-pre-checkout.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:worktree-pre-commit-main-block
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: worktree-first-pre-commit-main-block blocking-on-pr check 조건부 skip (CFP-428 / ADR-040 Amendment 3 §결정 7.D — templates/github-workflows/worktree-first-pre-commit-main-block.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:worktree-spawn-evidence-cwd
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: worktree-first-spawn-evidence-cwd blocking-on-pr check 조건부 skip (CFP-427 / ADR-040 Amendment 3 §결정 7.D — templates/github-workflows/worktree-first-spawn-evidence-cwd.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:claude-md-line-cap
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: CLAUDE.md ≤320줄 cap lint 조건부 skip + audit comment 자동 발의 (CFP-506 / ADR-012 Amendment 1 / ADR-060 Amendment 5 — templates/github-workflows/claude-md-line-cap.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:sibling-pr-author-check
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: sibling-pr-label-author-check lint 조건부 skip + audit comment 자동 발의 (CFP-521 / ADR-010 Amendment 4 §결정 5 — templates/github-workflows/sibling-pr-label-author-check.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:workflow-permissions
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: workflow permissions block presence lint 조건부 skip + audit comment 자동 발의 (CFP-530 / ADR-060 Amendment 8 §결정 21 — templates/github-workflows/workflow-permissions-check.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:workflow-yaml-parse
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: workflow yaml parse lint 조건부 skip + audit comment 자동 발의 (CFP-583 / ADR-060 Amendment 9 §결정 22 — templates/github-workflows/workflow-yaml-parse.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:debate-convergence-quality
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: debate convergence_quality_invariant 3 marker lint 조건부 skip + audit comment 자동 발의 (CFP-582 / ADR-059 Amendment 2 §결정 8 / ADR-024 Amendment 5 — templates/github-workflows/debate-convergence-quality.yml)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:wording-dictionary
    category: hotfix-bypass
    color: "fef2c0"
    description: "wording-dictionary lint warning 예외 채널 (ADR-064 Amendment 2 / CFP-610). PR description ### Bypass reason 섹션 기재 필수."
    single_active: false
    attach_owner_plugin: "wording-dictionary.yml CI Action (조건부 skip + audit comment 자동)"

  - name: hotfix-bypass:retro-mandatory-deployed
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: retro-mandatory.yml workflow byte-identical mirror deployment lint 조건부 skip + audit comment 자동 발의 (CFP-619 / ADR-045 mandate restoration / ADR-060 framework 41번째 entry / ADR-005 self-application invariant — templates/github-workflows/retro-mandatory.yml ↔ .github/workflows/retro-mandatory.yml diff sentinel)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:retro-alert-pickup
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: retro-alert-pickup-rate KPI sentinel 조건부 skip + audit comment 자동 발의 (CFP-628 Story 2 / ADR-045 §D-5 / ADR-060 framework 42번째 entry — retro alert pickup KPI warning-tier entry 예외 채널). PR description ### Bypass reason 섹션 기재 필수."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:marketplace-description-verbatim
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: marketplace description verbatim PR-time proactive lint 조건부 skip + audit comment 자동 발의 (CFP-631 / ADR-063 Amendment 2 §결정 11 / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/marketplace-description-verbatim.yml Phase 2 carrier — blocking-on-pr tier 직접 시작 근거 = ADR-060 §결정 5 default warning explicit exception + §결정 19 Amendment 6 CFP-509 auto_blocking manual gate + 사용자 directive Story §1)"
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:stop-time-continuous-confirm
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: Continuous '진행해' 패턴 mechanical detect advisory channel skip + audit comment 자동 발의 (CFP-638 / ADR-064 Amendment 3 §결정 9 sister carrier / ADR-060 framework 44번째 entry — Orchestrator self-check behavioral directive advisory only, turn-final hook 부재 platform 한계 + PMOAgent retro file §over-questioning 표 audit signal SSOT). 18번째 hotfix-bypass:* family member (post-CFP-631 atomic realignment)."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:marketplace-drift-detection
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: marketplace ↔ wrapper plugin.json reactive scheduled drift detection workflow skip + audit comment 자동 발의 (CFP-627 / ADR-063 Amendment 3 §결정 13 / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/marketplace-drift-detection.yml Phase 2 carrier — warning tier 신규 entry, 4th defense layer reactive scheduled cron channel). 19번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:workflow-version-drift
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: consumer .github/workflows/<name>.yml ↔ wrapper templates/github-workflows/<name>.yml SHA / 핵심 line drift detection skip + audit comment 자동 발의 (CFP-660 / ADR-032 Amendment 2 §결정 6 / ADR-024 Amendment 3 §결정 6.A — overlay/hooks/check_bootstrap.py check 10 runtime detection, warning tier 신규 entry, lane orchestration semantics divergence vector 차단). strict-eligible 5번째 drift (ADR-032 §결정 2 4 → 5 확장). 20번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:bootstrap-labels
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: bootstrap-labels precondition workflow skip + audit comment 자동 발의 (CFP-662 / ADR-060 Amendment 10 §결정 24 / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/bootstrap-labels.yml Phase 2 carrier — warning tier 신규 entry, PR-time precondition check pattern 의 첫 baseline, RETRO-MCT-104 carrier). 21번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:auto-phase-label-sibling-parity
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: templates/github-workflows/*.yml ↔ .github/workflows/*.yml SHA-256 byte-identical parity warning-tier lint skip + audit comment 자동 발의 (CFP-685 / ADR-065 §결정 1 row 3 / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/sibling-workflow-parity.yml carrier — weekly cron + workflow_dispatch 검증 채널, CFP-609 retro Finding D enforcement). 22번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:claude-md-amendment-ref
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: CLAUDE.md Amendment ref drift detection lint skip + audit comment 자동 발의 (CFP-708 / ADR-074 / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/claude-md-amendment-ref-drift.yml carrier — CLAUDE.md 안 Amendment N (CFP-NNN) 참조 + ADR frontmatter amendment_log/amendments 길이 비교, warning tier 신규 entry, cross-section coherence lint CFP-263 lineage 답습). 23번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # hotfix-bypass:actionlint + hotfix-bypass:post-merge-followup-success-rate (2종 — CFP-688 / ADR-026 Amendment 3 §결정 5.G.b + §결정 5.G.d carrier)
  # actionlint prevention layer + KPI detection layer. canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
  # plugin.json PATCH bump 동반 (5.72.0 → 5.73.0) — marketplace.json sync required (ADR-063 §결정 18).
  - name: hotfix-bypass:actionlint
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: actionlint workflow syntax validation lint skip + audit comment 자동 발의 (CFP-688 / ADR-026 Amendment 3 §결정 5.G.b / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/actionlint-check.yml carrier — .github/workflows/*.yml YAML parse + syntax validation, actionlint v1.7.12, warning tier 신규 entry, born-broken 재발 차단 forcing function). ADR-026 §5.G.b 승격 target = blocking-on-pr (tier reconciliation: 첫 도입 warning, ADR-060 §결정 5). 24번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  - name: hotfix-bypass:post-merge-followup-success-rate
    category: hotfix-bypass
    color: "fef2c0"
    description: "hotfix-bypass: post-merge-followup.yml rolling 14-day success rate KPI sentinel breach Issue auto-create skip + audit comment 자동 발의 (CFP-688 / ADR-026 Amendment 3 §결정 5.G.d / ADR-024 Amendment 3 §결정 6.A — templates/github-workflows/post-merge-followup-success-rate-kpi.yml carrier — weekly cron + workflow_dispatch 측정, sentinel ≥ 90%, 9번째 warning-tier entry ADR-026 §5.G.d 명시). 25번째 hotfix-bypass:* family member."
    single_active: false
    attach_owner_plugin: "사용자 직접 / Orchestrator (hotfix-bypass 경로)"

  # fallback:* (2종 — CFP-658 / ADR-027 Amendment 2 §결정 6.A carrier — Action 차단 환경 manual agent direct write path)
  # 신규 category enum: fallback (별 axis). canonical-only (kind:registry — sibling sync scope 외 per ADR-010 §결정 2).
  # plugin.json MINOR bump 동반 (5.56.0 → 5.57.0) — marketplace.json sync required (ADR-063 §결정 18).
  - name: fallback:manual
    category: fallback
    color: "c5def5"
    description: "fallback: per-Issue ad-hoc override marker (CFP-658 / ADR-027 Amendment 2 §결정 6.A). Orchestrator 가 부착 시 bootstrap.fallback_mode: action_blocked (declarative Trigger A) 와 무관 manual agent direct write path 활성. 우선순위 (C) > (A) — Issue 발의자 또는 Orchestrator 의 일시 outage / 사용자 explicit 선택 영역. RequirementsPL / ArchitectPL 의 manual `bash templates/scripts/manual-story-init-fallback.sh <ISSUE_NUMBER>` 호출 의무 (Phase 2 carrier 신설 후 활성). 4 required check + enforce_admins:true ratchet 유지."
    single_active: false
    attach_owner_plugin: "Orchestrator / 사용자 직접 (Issue 발의 시 또는 fallback path 진입 시점)"

  - name: fallback:rate-limited
    category: fallback
    color: "c5def5"
    description: "fallback: rate-limited skip audit marker (CFP-658 / ADR-027 Amendment 2 §결정 6.G). manual-story-init-fallback.sh (Phase 2 carrier) 의 exponential backoff (1s/2s/4s) max 3 retry 초과 시 silent skip + 자동 부착. OpRiskArch 조건 4 carrier — GitHub secondary content-creation rate-limit (503/429) 영역 audit-trailed channel."
    single_active: false
    attach_owner_plugin: "manual-story-init-fallback.sh (자동) / Orchestrator (수동 audit 시)"
```

## 4. 변경 규칙

- **v2.x append-only**: 새 label 추가는 minor (v2.1). 기존 label 삭제 또는 이름 변경은 v3.0 BREAKING (ADR-008)
- **`single_active: true` invariant**: phase:* 카테고리만 single-active
- **`bootstrap-labels.sh` SSOT 역전 (CFP-33 contract harness 후)**: 현재 script 가 hardcoded source. CFP-33 에서 본 registry → script 자동 생성으로 전환
