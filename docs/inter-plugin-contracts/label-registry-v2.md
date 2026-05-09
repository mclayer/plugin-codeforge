---
kind: registry
registry: label
version: "2.1"
status: Active
supersedes: label-registry-v1.md
created_by: CFP-140
created_date: 2026-05-09
authors:
  - Claude (CFP-140 — ADR-049 type:* → native Issue Types cutover)
related_adrs:
  - ADR-008 (contract versioning — MAJOR bump = label hack removal)
  - ADR-049 (CFP-140 — Issue Types native migration)
  - ADR-009 (CFP-31 — wrapper agent 0 invariant)
  - ADR-030 (CFP-123 — gate:live-entry-pass v1.3)
  - ADR-036 (CFP-260 — phase:reservation v1.4)
  - ADR-045 (CFP-138 — gate:retro-complete v1.5)
  - ADR-050 (CFP-XXX — conflict:* + merge-order:* labels v2.1)
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

**v2.1 (CFP-XXX / ADR-050, 2026-05-09)**: MINOR bump.
- **추가**: `conflict:file-overlap`, `conflict:adr-number`, `conflict:section-locked` — 병렬 에픽 충돌 감지 레이블 (parallel-epic-conflict-check.yml Actions 부착)
- **추가**: `merge-order:1`, `merge-order:2` — 충돌 시 merge 순서 프로토콜 (GitOpsAgent 부착)

**v2.0 (CFP-140 / ADR-049, 2026-05-09)**: MAJOR bump.
- **제거**: `type:epic`, `type:story`, `type:bug` — native GitHub Issue Types 로 대체
  - See: `templates/issue-types.yaml`, `scripts/migrate-label-to-issue-type.sh`
- **유지**: `impl-manifest` (별도 axis — sub-issue visual marker, non-breaking)
- **유지**: phase:* / gate:* / fix:* / hotfix:* / audit:* / category:* (전부 유지)

## 1. 목적

`bootstrap-labels.sh`가 생성하는 GitHub label SSOT (v2.1 시점 32+ 종 — type 1 / phase 8 / gate 4 / fix 4 / hotfix 2 / audit 12+ / category 7 / conflict 5).
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
    attach_owner_plugin: "codeforge-requirements (CFP-37 후) / DocsAgent (CFP-32 시점) / story-init.yml (초기 부착)"

  - name: phase:설계
    category: phase
    color: "1d76db"
    description: "Phase: 설계"
    single_active: true
    attach_owner_plugin: "codeforge-design (CFP-40 후) / DocsAgent (CFP-32 시점)"

  - name: phase:설계-리뷰
    category: phase
    color: "1d76db"
    description: "Phase: 설계-리뷰"
    single_active: true
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점)"

  - name: phase:구현
    category: phase
    color: "1d76db"
    description: "Phase: 구현"
    single_active: true
    attach_owner_plugin: "codeforge-develop (CFP-39 후) / DocsAgent (CFP-32 시점)"

  - name: phase:구현-리뷰
    category: phase
    color: "1d76db"
    description: "Phase: 구현-리뷰"
    single_active: true
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점)"

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
    attach_owner_plugin: "codeforge-review (CFP-35 v2 후) / DocsAgent (CFP-32 시점)"

  - name: phase:reservation
    category: phase
    color: "ededed"
    description: "Phase: reservation (CFP-260 / ADR-036 — brainstorming 시점 KEY 사전 확보, 30 일 미진행 시 reservation-cleanup.yml 자동 close. promote 시 phase:요구사항 으로 변경)"
    single_active: true
    attach_owner_plugin: "cfp-reserve.yml Issue Form (자동 첨부) / Orchestrator (수동 promote 시 detach)"

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
```

## 4. 변경 규칙

- **v2.x append-only**: 새 label 추가는 minor (v2.1). 기존 label 삭제 또는 이름 변경은 v3.0 BREAKING (ADR-008)
- **`single_active: true` invariant**: phase:* 카테고리만 single-active
- **`bootstrap-labels.sh` SSOT 역전 (CFP-33 contract harness 후)**: 현재 script 가 hardcoded source. CFP-33 에서 본 registry → script 자동 생성으로 전환
