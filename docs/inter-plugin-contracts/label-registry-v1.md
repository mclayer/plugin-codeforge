---
kind: registry
registry: label
version: "1.2"
status: Active
authors:
  - Claude (CFP-32 codification — bootstrap-labels.sh 추출 + ζ arc owner 매핑)
related_adrs:
  - ADR-008
  - ADR-009 (CFP-31)
related_files:
  - scripts/bootstrap-labels.sh (현재 hardcoded source — CFP-33 contract harness에서 SSOT 역전 후 본 registry → script 자동 생성)
  - .github/workflows/phase-label-invariant.yml
  - .github/workflows/phase-gate-mergeable.yml
  - .github/workflows/fix-ledger-sync.yml
  - .github/workflows/subissue-from-impl-manifest.yml
  - .github/workflows/story-init.yml
---

# label-registry v1

## 1. 목적

`bootstrap-labels.sh`가 생성하는 GitHub label 20종 machine-readable SSOT. ζ arc 진행 후 각 lane plugin이 자기 phase·gate·fix label을 attach·detach 시 통일된 이름·색상·의미 보장. CI Actions(`phase-label-invariant.yml` 등)도 본 registry를 참조해 invariant enforce.

## 2. Schema

각 label entry:

| 필드 | 타입 | 설명 |
|---|---|---|
| name | string | label 이름 (예: `phase:설계`) |
| category | enum | type / phase / gate / fix / hotfix / audit |
| color | string | 6자리 hex (gh label spec) |
| description | string | label 설명 (gh label create --description 인자) |
| single_active | bool | 같은 category에서 1개만 active 가능 (phase만 true) |
| attach_owner_plugin | string | CFP-32 시점 + ζ arc 완료 후 부착 권한 plugin / Action |

## 3. 항목

```yaml
labels:
  # type:* (4종)
  - name: type:epic
    category: type
    color: "5319e7"
    description: "Epic (사용자 요구사항 1건 = Milestone + Issue)"
    single_active: false
    attach_owner_plugin: "codeforge-pmo (CFP-36 후) / DocsAgent (CFP-32 시점)"

  - name: type:story
    category: type
    color: "0e8a16"
    description: "Story (PR 1쌍 = Phase 1 + Phase 2)"
    single_active: false
    attach_owner_plugin: "story-init.yml CI Action (자동)"

  - name: type:bug
    category: type
    color: "d73a4a"
    description: "Bug"
    single_active: false
    attach_owner_plugin: "DocsAgent (CFP-32 시점) / 사용자 직접"

  - name: impl-manifest
    category: type
    color: "fbca04"
    description: "Sub-issue (Impl Manifest 파일 단위)"
    single_active: false
    attach_owner_plugin: "subissue-from-impl-manifest.yml CI Action (자동)"

  # phase:* (7종, single-active enforced by phase-label-invariant.yml)
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

  # gate:* (2종)
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

  # hotfix:* (2종) + audit (1종)
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

  # audit:debut-* (2종) — CFP-60 / ADR-021 introduced (v1.1 minor bump)
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

  # audit:spec-amendment (1종) — CFP-87 / playbook §6.8 introduced (v1.2 minor bump, CFP-88)
  - name: audit:spec-amendment
    category: audit
    color: "fbca04"
    description: "Mid-implementation spec doc 수정 PR (Codex push-back / 사용자 mid-impl clarification / spec drift 발견 시)"
    single_active: false
    attach_owner_plugin: "wrapper Orchestrator (playbook §6.8 spec amendment loop)"

  # early-close:* (3종 권장 + freeform) — CFP-90 / phase-label-invariant Issue close validation (v1.2 minor bump, CFP-90)
  # phase progression 미완 채로 close 정당화 시 의무 — phase-label-invariant.yml workflow 가 PASS 조건 검증
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

  # category:* (7종) — CFP-60 / debut-audit-triage-v1 introduced (v1.1 minor bump)
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
```

## 4. 변경 규칙

- **Append-only for v1.x**: 새 label 추가는 minor (v1.1). 기존 label 삭제 또는 이름 변경은 v2.0 BREAKING (ADR-008)
- **`single_active: true` invariant**: phase:* 카테고리만 single-active. CI Action `phase-label-invariant.yml`이 enforce — 두 phase:* 동시 부착 PR reject
- **Color drift 방지**: 본 registry color 값은 `bootstrap-labels.sh`가 idempotent edit (`gh label edit --color`)로 강제 동기화. consumer가 manual로 색상 변경 시 다음 bootstrap 실행에 복원
- **Owner transition**: ζ arc 진행에 따라 `attach_owner_plugin` 좌측(현재 owner) → 우측(target plugin)으로 이전. fix:* / impl-manifest / type:story / audit:* 는 CI Action 또는 Orchestrator 유지 (lane plugin 무관)
- **`bootstrap-labels.sh` SSOT 역전 (CFP-33 contract harness 후)**: 현재 script가 hardcoded source. CFP-33에서 본 registry → script 자동 생성으로 전환
