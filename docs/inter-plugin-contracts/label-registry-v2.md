---
kind: registry
registry: label
version: "2.5"
status: Active
supersedes: label-registry-v1.md
created_by: CFP-140
created_date: 2026-05-09
canonical_repo: mclayer/plugin-codeforge
canonical_path: docs/inter-plugin-contracts/label-registry-v2.md
date: 2026-05-13  # CFP-429 v2.5 — from-cfp-425-followup provenance label append (Epic CFP-425 gate FAIL 분기 후속 carrier) | CFP-521 v2.4 sub-entry — hotfix-bypass:sibling-pr-author-check 9번째 family member (ADR-010 Amendment 4 §결정 5 anti-misuse 안전망) | CFP-506 v2.4 sub-entry — hotfix-bypass:claude-md-line-cap 8번째 | CFP-481 v2.4 — phase:* attach_owner_plugin field 갱신 (auto-phase-label.yml 명시)
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
```

## 4. 변경 규칙

- **v2.x append-only**: 새 label 추가는 minor (v2.1). 기존 label 삭제 또는 이름 변경은 v3.0 BREAKING (ADR-008)
- **`single_active: true` invariant**: phase:* 카테고리만 single-active
- **`bootstrap-labels.sh` SSOT 역전 (CFP-33 contract harness 후)**: 현재 script 가 hardcoded source. CFP-33 에서 본 registry → script 자동 생성으로 전환
