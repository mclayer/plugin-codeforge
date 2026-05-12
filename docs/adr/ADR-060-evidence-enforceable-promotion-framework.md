---
adr_number: 60
title: Evidence-enforceable promotion framework — declaration → warning → enforce 점진 적용 SSOT
status: Accepted
category: governance
date: 2026-05-11
is_transitional: false
carrier_story: CFP-389
supersedes: []
amends: []
amendment_log:
  - amendment: 1
    carrier_story: CFP-390
    date: 2026-05-11
    summary: |
      4 정정 + Codex Proactive Check #2/#6 FIX iter 1 4 P1 해소 —
      §결정 6 (c) `sibling_dependencies` CFP-391 → CFP-412 verbatim 정정 (원본 inline strikethrough + Mermaid 동기) +
      §결정 12 후속 carrier 목록 CFP-391 폐기 + CFP-412 재예약 정정 +
      신설 §결정 13 인벤토리 backfill SSOT — Phase 1 (SSOT only) / Phase 2 (row append) scope split + 그룹 A final 18 entry (owner_adr 정합 ADR 명확 entry 만, 8 entry 그룹 B 강등) + tier 재계산 (manifest 부착 2 entry 만 blocking, 나머지 warning) +
      신설 §결정 14 메타 anomaly lint 후속 carrier 의무 명시 (Codex P2-B 정합)
  - amendment: 2
    carrier_story: CFP-455
    date: 2026-05-12
    summary: |
      4-tier enforcement 정식 amendment + schema MINOR bump (v1.0 → v1.1) —
      §결정 3 `current_tier` 필드 optional → required 전환 명시 + retroactive 분류 검증 의무 표기 (22/22 entry 모두 현행 `current_tier` 보유 verified, mechanical regression 0건) +
      §결정 6 (c) `sibling_dependencies` field back-substitution 결정 (append `[CFP-390, CFP-412, CFP-455]` — CFP-412 폐기 history 보존 + sibling 의도 보존) +
      §결정 14 메타 anomaly lint 와 본 Story 의 메타 schema validation lint 분리 결정 (별도 entry 2종, scope 차이 — anomaly = inventory detection / schema validation = field schema 정합) +
      신설 §결정 15 메타 lint exit-code 3-tier semantics (0=PASS / 1=validation FAIL / 2=meta-error) — Codex AREA 1 정합 +
      신설 §결정 16 warning-tier bypass_label policy (warning = non-blocking, bypass 의미 부적용 → optional + 본 메타 lint entry 자체 omit) — Codex AREA 2 (a) 정합 +
      신설 §결정 17 retroactive reclassification failure handling (immediate fail exit 1 + PR block) — Codex AREA 2 (b) 정합 +
      신설 §결정 18 marketplace/sibling sync necessity 명시 (registry yaml = wrapper-owned, ADR-010 scope 외, marketplace sync 불필요) — Codex AREA 2 (c) 정합 +
      Mermaid 다이어그램 sibling_dependencies 표기 갱신 (CFP-455 carrier 반영) — Codex AREA 4 정합
  - amendment: 3
    carrier_story: CFP-449
    date: 2026-05-12
    summary: |
      `hotfix-bypass:*` channel 의미 sharpening — §결정 7 본문에 "audit 전용 채널 — 정책 회피 등록 차단 (ADR-064 §결정 5 ratchet 정합)" 한 줄 명시 (운영 안전망 통로, 정책 회피 등록 channel 아님) +
      ADR-064 §결정 2 forbid-list 8 어휘 mechanical lint entry (`decision-principle-vocab`) 신설 cross-ref +
      evidence-checks-registry.yaml 2nd warning-tier entry 도입 = framework multi-entry 운영 검증 cross-validation 신호 (1st entry `adr-sunset-criteria` 와 schema 정합 검증) +
      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작 변경 없음, 의미 sharpening only (ADR-058 §결정 5 sunset_justification 의무 통과 — 강화 방향 amendment).
  - amendment: 4
    carrier_story: CFP-481
    date: 2026-05-12
    summary: |
      3rd warning-tier entry `auto-phase-label` 등록 carrier amendment — PR open 시 phase label 자동 부착 workflow (CFP-455 + CFP-449 retro sentinel 2 재현 → mechanical enforcement 도입 timing 도달) +
      registry yaml row append (Phase 2 PR scope) — schema 변경 0건 (Amendment 2 schema v1.1 정합, `current_tier: warning` + `bypass_label: hotfix-bypass:auto-phase-label` per-entry namespace) +
      ADR-024 Amendment 4 동반 (`hotfix-bypass:auto-phase-label` 7번째 family member + branch → phase mapping 표 SSOT 신설) +
      label-registry-v2 v2.3 MINOR 동반 (phase:* 8 label entry attach_owner_plugin field 갱신 — `auto-phase-label.yml` 명시) +
      ratchet 위반 0건 — enum 값 / tier 추가 / bypass channel 동작 변경 없음, framework 의 자연스러운 사용 사례 entry 추가 only (ADR-058 §결정 5 sunset_justification 의무 통과 — 강화 방향 amendment, framework SSOT permanent governance) +
      sibling_dependencies append `[CFP-390, CFP-412, CFP-455, CFP-449, CFP-481]` (Amendment 2 §결정 6 (c) chain 정합 — CFP-449 / CFP-481 모두 framework 운영 검증 entry).
related_stories:
  - CFP-389
  - CFP-390  # Amendment 1 carrier — 인벤토리 backfill (CFP-388 Epic Story-2)
  - CFP-388  # parent Epic
  - CFP-449  # Amendment 3 carrier — 2nd warning-tier entry `decision-principle-vocab` + bypass channel 의미 sharpening
  - CFP-481  # Amendment 4 carrier — 3rd warning-tier entry `auto-phase-label` + ADR-024 Amendment 4 동반 + label-registry-v2 v2.3 MINOR 동반
related_adrs:
  - ADR-008   # versioning (kind:registry 도 minor/major SemVer 정합)
  - ADR-010   # contract sibling sync (kind:registry scope 외 명시)
  - ADR-013   # dogfood-out (Story file path internal-docs)
  - ADR-016   # marketplace registration
  - ADR-024   # branch policy (Amendment 3 의 audit-trailed exception channel 도입)
  - ADR-037   # plugin version bump (MINOR)
  - ADR-041   # doc-locations
  - ADR-050   # parallel epic + warning mode prior art
  - ADR-053   # structural change restart
  - ADR-054   # doc-only fast-path (본 Story 는 full-lane)
  - ADR-057   # 첫 amendment 후보 (별도 carrier)
  - ADR-058   # 직접 동인 — sunset criteria mandate
related_files:
  - docs/inter-plugin-contracts/evidence-check-registry-v1.md
  - docs/inter-plugin-contracts/MANIFEST.yaml
  - docs/evidence-checks-registry.yaml
  - docs/doc-locations.yaml
  - docs/parallel-work/section-ownership.yaml
  - scripts/check-adr-sunset-criteria.sh
  - scripts/check-bypass-audit-comment.sh
  - templates/github-workflows/adr-sunset-criteria.yml
  - docs/adr/ADR-024-story-scoped-branch-policy.md
  - CLAUDE.md
---

# ADR-060: Evidence-enforceable promotion framework — declaration → warning → enforce 점진 적용 SSOT

## 상태

Accepted (2026-05-11). carrier_story = CFP-389. parent Epic = CFP-388.

## 컨텍스트

ADR-058 (CFP-387, merged 2026-05-11 — internal-docs main `a59fc8a`) 가 ADR `## 해소 기준` 섹션과 `is_transitional` frontmatter 를 의무화했으나 **declaration only** 단계에 머물렀다. §결정 8 명시:

> 본 ADR 은 정책 declaration only. 기계적 강제 (CI lint) 는 CFP-B (잠정) / 정책 첫 적용 사례 (ADR-057 amendment + KPI) 는 CFP-C (잠정) / 기존 안전망 ADR retroactive backfill 은 CFP-D (잠정) 별도 carrier 분리.

본 ADR (ADR-060) 가 **CFP-B 잠정의 carrier** — declaration 의 첫 evidence-enforceable mechanical check 도입 + 모든 후속 evidence check 가 따를 **점진 적용 framework SSOT**.

### 직접 동인

1. **ADR-058 declaration 의 moral governance 한계**: 정책 선언 → 작성자 자발 준수 + DesignReview 1차 안전망 의존. CI mechanical enforcement 부재 시 ADR-057 같은 직접 동인 ADR 의 측정 기준 부재 위험이 재발.

2. **codeforge wrapper repo 의 governance 진화 패턴**: ADR-050 (parallel-epic-conflict-check.yml = warning mode prior art) / ADR-024 Amendment 2 (CFP-280 — branch protection drift detection) / ADR-041 (doc-locations.yaml SSOT) 가 모두 "선언 → 점진 enforce" 패턴 채택. 본 framework 가 패턴을 정형화.

3. **사용자 brainstorming 합의** (Opus×Codex 3-round, 2026-05-11): "안전망 측정가능 종료" 원칙 5 + "evidence-enforceable 점진 적용" 원칙 + "velocity-normalized metric" (throughput 가변 환경에서 sprint-주기 metric 회피).

4. **CFP-388 Epic 3 child Story 의 framework 정합 요구**: CFP-389 (본 framework SSOT) → CFP-390 (인벤토리 backfill = registry yaml row append) → CFP-391 (4-tier 정식 분류 amendment) 의 순차 의존. 3 Story 모두 본 framework registry 위에서 동작.

5. **Hotfix bypass channel 의 필요성**: enforce mode 진입 후 운영 장애 hotfix 가 정책 위반을 강제하는 경우, ADR-024 §결정 6 ("emergency hotfix 도 PR 경유 의무, no exception") + `enforce_admins: true` (CFP-70) 와 호환되는 **audit-trailed exception channel** 부재. 사용자 ESCALATE 결정 (CFP-389 iteration 2) = Option A — `hotfix-bypass:*` label family 도입 + ADR-024 Amendment 3 동반.

### 선행 연구 / prior art

- **Feature flag sunset (LaunchDarkly / Optimizely 운영 가이드)**: 도입 시 sunset criteria + owner + date 의무화. 측정성 3-tuple 패턴 차용.
- **입법 sunset clause 패턴**: 명시적 종료 조건 미충족 시 자동 expire. warning → enforce mode 전환 (=evidence check 의 sunset transition) 으로 변형.
- **CI/CD progressive enforcement (Spotify / Shopify code health migration 가이드)**: 신규 lint 도입 시 advisory → blocking on changed lines → blocking on full repo 3 단계 점진. 본 framework 의 4-tier 분류 (warning / blocking-on-PR / blocking-on-merge / hotfix-bypass) 의 직접 모델.
- **codeforge 내부 prior art**: ADR-050 parallel-epic-conflict-check.yml (non-blocking warning + PR comment + label) / ADR-024 Amendment 2 branch-protection-drift-check.yml (drift detection schedule + workflow_dispatch) 모두 본 framework workflow 양식의 1차 reference.

## 결정

### 결정 1 — Framework SSOT 위치 = `docs/inter-plugin-contracts/evidence-check-registry-v1.md`

evidence-enforceable framework 의 schema doc + 운영 룰 = **kind:registry** entry. 위치 = `docs/inter-plugin-contracts/evidence-check-registry-v1.md`. 분류 근거:

- ADR-058 §결정 8 의 framework declaration 을 mechanical 검증 가능한 **cross-cutting protocol** 로 변환 → kind:contract (lane plugin 간 typed schema) 아닌 kind:registry (wrapper-owned cross-cutting protocol) 정합.
- 기존 3 kind:registry (`comment-prefix-registry-v1` / `fix-event-v1` / `label-registry-v2`) 와 동일 위치 + 동일 lint chain (`check-doc-frontmatter.sh` + `check-doc-section-schema.sh`).
- `inter-plugin-contracts/MANIFEST.yaml` 의 `registries:` 블록에 entry 추가 (label_registry 패턴) — kind:contract `check-inter-plugin-contracts.sh` scope 외 (MANIFEST header `kind:contract files only` 명시 정합).

(§5.5 CL-1 — 권고 채택)

### 결정 2 — Registry data = `docs/evidence-checks-registry.yaml` (single SSOT)

본 framework 의 모든 evidence check entry 는 단일 yaml file `docs/evidence-checks-registry.yaml` 에 정의. schema 는 `evidence-check-registry-v1.md` SSOT. MANIFEST.yaml `registries:` 블록은 **versioning 추적 only** (label-registry-v1 → v2 패턴 reference, version bump 시 row append). data 자체는 yaml.

(§5.5 CL-1 추가 명시 — MANIFEST = versioning, yaml = data)

### 결정 3 — 4-tier enforcement enum (정식 도입)

evidence-checks-registry.yaml 의 각 entry 는 `current_tier` 필드 보유. enum:

| tier | 동작 | branch protection 영향 |
|---|---|---|
| `warning` | continue-on-error 또는 non-required check. PR comment / job summary 경고만. | required_status_checks.contexts 미부착 |
| `blocking-on-pr` | required check. PR merge 차단. | required_status_checks.contexts 부착 |
| `blocking-on-merge` | post-merge guard (예: phase-gate-mergeable). PR open 단계는 통과, merge 시점 차단. | required_status_checks.contexts 부착 |
| `hotfix-bypass` | bypass label 적용 PR 만 skip + audit comment 의무. label 부재 시 blocking-on-pr 등가. | required_status_checks.contexts 부착 (+ bypass workflow) |

본 ADR (CFP-389) 의 첫 entry = `warning` tier. 후속 Story (CFP-391) 가 본 enum 을 정식 명시 + 기존 entry retroactive 분류. 본 ADR 시점에서는 enum 정의만 제공, registry yaml 의 `current_tier` 필드는 optional (CFP-391 시점 required 전환 = MINOR bump).

### 결정 4 — 첫 entry = ADR sunset criteria lint (`scripts/check-adr-sunset-criteria.sh`)

evidence-checks-registry.yaml 의 첫 entry:

```yaml
- name: adr-sunset-criteria
  description: ADR-058 §결정 1-3 mechanical verification (is_transitional frontmatter + ## 해소 기준 섹션 + 측정성 3-tuple + 모달 어휘 1차 사전)
  detect_command: bash scripts/check-adr-sunset-criteria.sh
  workflow: templates/github-workflows/adr-sunset-criteria.yml
  current_tier: warning
  bypass_label: hotfix-bypass:adr-sunset
  bypass_audit_lint: bash scripts/check-bypass-audit-comment.sh
  promotion_criteria:
    pr_cumulative_min: 20
    failure_threshold: 0
    sibling_dependencies:
      - CFP-390
      - CFP-391
    evidence_artifacts:
      - github_actions_run_history_url
      - lint_failure_count_zero_proof
      - pr_cumulative_count_proof
  modal_anti_pattern_dictionary:
    version: "1.0"
    dictionary:
      - "안정화되면"
      - "임시"
      - "한시적"
      - "until further notice"
  introduced_by: CFP-389
  owner_adr: ADR-058
  carrier_adr: ADR-060
```

lint script 책임 4건 (Story §5.1 AC-4 정합):
- (a) ADR file 의 `is_transitional: true|false` frontmatter 필드 존재 검증
- (b) `## 해소 기준` 섹션 존재 검증
- (c) is_transitional=false 시 "N/A — permanent policy" 1줄 또는 동등 형식 허용
- (d) is_transitional=true 시 측정성 3-tuple (metric / who / how) 존재 검증 + 모달 어휘 1차 사전 4 표현 매치 검사

본 lint exit code = 0 (PASS) / 1 (FAIL — violation 1건 이상). bypass label 적용 PR 의 경우 workflow 가 lint 실행 자체를 skip (continue-on-error 무관, label 기반 conditional skip).

### 결정 5 — 첫 적용 = warning mode (continue-on-error)

`templates/github-workflows/adr-sunset-criteria.yml` 는 다음 양식:

- trigger: `pull_request` (opened / synchronize / reopened) — paths filter `docs/adr/**.md`
- 실행: `bash scripts/check-adr-sunset-criteria.sh <changed-ADR-files>`
- step: `pip install --user pyyaml` (default ubuntu-latest runner = python3 + pip 사전 설치, pyyaml 별도 install 의무 — lint script python yaml 의존성)
- `continue-on-error: true` 적용 → lint fail 이 PR merge 차단하지 않음
- branch protection `required_status_checks.contexts` 미부착 (ADR-024 Amendment 2 manifest 갱신 불필요)
- PR comment 자동 게시 — violation 발견 시 job summary + sticky comment 형태 (parallel-epic-conflict-check.yml 패턴 차용)
- `hotfix-bypass:adr-sunset` label 적용 PR = lint skip + audit comment 자동 발의 (별도 step)

운영 가이드 (§6.1.2 EC-B 정합):
- 첫 warning 출현 ≤ 14 days 동안 false positive ≥ 5건 발생 시 → workflow 일시 정지 (admin only) + ADR-060 §결정 보완 carrier 발의.
- solo-dev 환경 (CFP-72 reviewer count=0) → 사용자 본인 적극 체크 의무 (PR review 단계 GitHub Actions warning manual 확인).

### 결정 6 — 승격 gate (binary, AND condition)

warning → blocking-on-pr (또는 blocking-on-merge) 승격 조건 = **3 condition AND** (§5.1 AC-6 정합):

- **(a) PR 누적 ≥ 20**: ADR-060 merge 후 첫 main PR merge 일자부터 카운트 시작. `hotfix-bypass:adr-sunset` label 적용 PR 도 throughput metric 에 포함 (EC-C 정합).
- **(b) bypass label 외 failure count = 0**: warning mode 운영 기간 동안 `scripts/check-adr-sunset-criteria.sh` violation 카운트 = 0. bypass label 적용 PR 의 lint 결과 skip (failure 미카운트). 시뮬레이션 실패와 enforce failure 는 동일 의미로 통합 (별도 카운터 없음).
  - **measurement 방식**: failure count = **각 PR 의 final commit (= PR branch 의 최종 commit, merge 전략 squash/rebase/merge-commit 무관) 의 lint 결과** 기준 (PR 전체 commit history 또는 individual workflow run 누적 아님). PR 작성자가 warning manual 확인 → 다음 commit append 로 warning 해소 → PR merge 시점 final state = PASS = failure 미카운트. 정합: 운영 가이드 §결정 5 "사용자 본인 적극 체크 의무". P1-A `continue-on-error: true` × `failure_threshold=0` 잠재 deadlock 해소 — final commit 기준이면 warning mode 의 의도 (PR 진행 차단 X + final 정합 측정) 양립.
    - **final commit 정의 (merge 전략별 정합)**: GitHub PR UI 기준 PR branch 의 최종 commit (≈ `gh pr view --json commits | jq '.commits[-1].oid'` 결과). squash merge = 압축 전 PR head 기준 / rebase merge = PR head 기준 / merge-commit = PR head 기준 (생성된 merge commit 아님). main branch 의 post-merge commit 과 무관.
    - **workflow trigger 시점**: `pull_request` (synchronize / opened / reopened / labeled / unlabeled) — PR approval phase 에서만 실행. merge 후 재실행 X. 별도 post-merge lint 는 본 Story scope 외 (enforce 승격 carrier 또는 별도 carrier).
- **(c) sibling Story merged**: CFP-390 (인벤토리 backfill) + ~~CFP-391 (4-tier 정식 amendment)~~ → **CFP-412 (4-tier amendment 재예약 carrier, Amendment 1, 2026-05-11)** 모두 main merge 완료. 본 framework 가 multi-entry registry 로 운영되는 시점 정합. (see Amendment 1 — CFP-391 Issue #396 closed without delivery 2026-05-11, CFP-412 Issue #412 substitution)

승격 carrier (별도 CFP-NNN, 본 Story scope 외) 의 evidence 4 산출물 의무:
- (i) GitHub Actions 누적 run 결과 page URL (warning workflow 실행 이력)
- (ii) bypass label 외 failure count = 0 lint 출력 (gh CLI / API 결과 첨부)
- (iii) PR 누적 ≥ 20 카운트 (gh CLI / API 결과 첨부)
- (iv) **GitHub Actions outage runbook**: warning mode = `continue-on-error: true` 덕에 outage 시 PR 차단 X. enforce mode 진입 시점 = outage 발생 시 PR block / hotfix-bypass label 활용 / workflow manual disable 등 대응 절차 산출물 의무. 외부 의존 (GitHub Actions 가용성) 의 enforce mode 영향 분석 + manual fallback path 명시. (§7.4.1 DR 분석의 enforce 진입 시 후속 carrier scope.)
- (v) **Audit comment author 검증 lint 증거** (§결정 8 cross-ref): enforce 승격 carrier 가 `audit_comment_author_verification_lint` 의 실행 결과 (gh CLI / API 출력) 첨부 의무. comment author = `github-actions[bot]` 검증 lint 가 bypass label 적용 PR 의 audit comment spoofing 차단 — §7.2 STRIDE-LITE S1 강화 enforce 의무.
- (vi) **Sticky comment pattern 구현 증거** (§결정 8 cross-ref): enforce 승격 carrier 가 audit comment workflow 의 sticky pattern (기존 `[hotfix-bypass-audit]` comment update 또는 marker 기반 dedup) 도입 + 단일 PR 동일 workflow run 다회 시 at-most-once 보장 증거 (workflow yaml diff + test 출력) 첨부 의무.

본 6 산출물 부재 시 승격 carrier PR block. **자동화 카운터 인프라는 후속 carrier 책임** — 본 ADR 는 gate 정의만 제공.

### 결정 7 — Hotfix bypass channel = `hotfix-bypass:*` label family (audit-trailed exception)

운영 장애 hotfix 가 정책 위반을 강제하는 경우의 **audit-trailed exception channel**:

- **label naming**: `hotfix-bypass:<entry-name>` family. 첫 entry = `hotfix-bypass:adr-sunset` (본 Story).
- **권한자**: repo admin only. solo-dev 환경 = 사용자 본인 (mccho8865). contributor 추가 시 재논의.
- **PR 경유 의무 유지**: bypass label = lint skip only. push/merge 경로는 PR 경유 유지 — ADR-024 §결정 6 (`emergency hotfix 도 PR 경유, no exception`) + `restrictions: {users:[], teams:[], apps:[]}` (CFP-66) + `enforce_admins: true` (CFP-70) 와 호환.
- **label scope**: per-entry 한정. 본 entry (`adr-sunset`) bypass label 은 sunset criteria 관련 긴급 hotfix only. 다른 evidence check (CFP-390 인벤토리 추가) 는 자체 bypass label 정의 (registry entry `bypass_label` 필드 per-entry).
- **ADR-024 Amendment 3 동반 의무**: 본 ADR-060 §결정 7 = ADR-024 Amendment 3 (`hotfix-bypass:*` label family 가 ADR-024 §결정 6 의 audit-trailed exception channel 임을 명시) 의 carrier. Phase 1 PR 동반 (scope cohesion).
- **label-registry-v2 entry 추가**: `hotfix-bypass:adr-sunset` label = label-registry-v2 의 신규 entry. taxonomy = `bypass` tier (신규 tier 도입). label-registry MINOR bump (v2.0 → v2.1) — 별도 PR 또는 본 Phase 1 PR 동반 (ArchitectAgent 판단 — 본 Story scope 동반 권고). **본 결정은 label-registry-v2 의 `bypass` tier 신설 결정 carrier 역할 — label-registry sibling sync (ADR-010) 별도 follow-up 가능**.
- **(Amendment 3, CFP-449)** **audit 전용 채널 — 정책 회피 등록 차단 (ADR-064 §결정 5 ratchet 정합)**: `hotfix-bypass:*` label 은 운영 장애 hotfix 의 일회성 exception 통로이며, 정책 위반을 회피하는 영구 등록 채널이 아님. label 부착 PR 마다 audit comment 자동 발의 + quarterly merge audit log 집계 의무 (§결정 8 schema 정합). 사용한 entry 가 enforce 승격 carrier (별도 CFP-NNN) 진입 시 bypass label 적용 PR 누적 회수가 evidence 산출물 (`bypass_pr_count`) 검토 영역. dictionary 회피 의도 등록 시 sunset_justification 의무 (ADR-058 §결정 5 정합) — bypass channel = 운영 안전망, 정책 회피 통로 아님.

(§5.5 CL-4 RESOLVED — 사용자 Option A 채택 verbatim 반영)

### 결정 8 — Audit trail schema (P0-1 정합)

bypass label 적용 PR 마다 GitHub Actions bot 가 PR comment 1개 자동 append. comment body schema (단일 textual form, CI-parsable):

```
[hotfix-bypass-audit] PR=<number> label_applied_by=<user> reason=<bypass_reason_textbox> ADR_files=<comma-separated-paths> timestamp=<ISO8601>
```

- `PR` = PR number (정수)
- `label_applied_by` = label 적용한 GitHub user login (admin only — solo-dev = 사용자 본인)
- `reason` = PR description 내 `### Bypass reason` 섹션 textbox 본문 (workflow 가 추출, 부재 시 PR block 의무 — workflow level 검증)
- `ADR_files` = 본 PR 에서 변경된 `docs/adr/*.md` 경로 list (comma-separated)
- `timestamp` = ISO8601 UTC (Z suffix 의무 — fix-event-v1 schema clarification 정합)

**Re-entry 안전망 (EC-D 정합)**: bypass PR 의 변경 ADR 가 sunset criteria 누락 상태 (재귀 시나리오) 일 시 audit comment 에 `[sunset-criteria-deferred]` 태그 자동 추가 + 후속 보완 의무 자동 Issue 발의 (CFP-390 인벤토리 backfill scope 또는 별도 carrier).

**Audit log 집계**: bypass label 적용 PR list 가 `docs/audit/hotfix-bypass-log.md` (quarterly merge 시 자동 append) — 별도 carrier scope (CFP-390 인벤토리 또는 신규 carrier). 본 ADR 는 schema + bot comment 양식만.

**Audit assertion lint**: `scripts/check-bypass-audit-comment.sh` (본 Story Phase 2 PR 범위 내 신설 — §5.5 CL-A 권고 채택). bypass label 부착 PR 의 audit comment 1개 이상 존재 검증. 부재 시 PR block (workflow level conditional).

**Audit comment author 검증 (enforce 승격 carrier 의무)**: warning mode 단계 = 본 lint 가 comment 존재만 검증 (author = `github-actions[bot]` 검증 미수행 — advisory). enforce mode 승격 carrier (별도 CFP-NNN) 의 `evidence_artifacts` 에 `audit_comment_author_verification_lint` 항목 추가 의무 — author = `github-actions[bot]` 강화 검증 lint 신설. 수동 audit comment 위조 (PR submitter spoofing) 차단을 위한 enforce 진입 전 mandatory 조건.

**Sticky comment pattern (enforce 승격 carrier 의무)**: warning mode 단계 = audit comment automation 가 동일 PR 의 multiple workflow run 시 multiple comment 발의 가능 (at-least-once). enforce mode 승격 carrier 의 의무: sticky comment pattern 도입 (workflow 가 기존 `[hotfix-bypass-audit]` comment 1개 update 또는 marker 기반 dedup) — at-least-once → at-most-once 보장. warning mode 단계는 advisory only 정합 (Change Plan §11.6 / OpRiskArch consult 결과 acceptable).

### 결정 9 — 모달 어휘 1차 사전 = ADR-058 §결정 8 의 4 표현 only

evidence-checks-registry.yaml 의 `modal_anti_pattern_dictionary.version: "1.0"` 의 4 표현 verbatim:

- "안정화되면"
- "임시"
- "한시적"
- "until further notice"

확장 어휘 ("충분히" / "조만간" / "soon" / "TBD" 등) 는 본 Story scope 외. 별도 carrier (CFP-391 4-tier amendment 또는 신규 carrier) 가 `dictionary_version: "1.1"` 으로 MINOR bump 시 확장.

**Amendment chain SSOT 위치 (v1.1 carrier 의무)**: dictionary 확장 carrier (CFP-391 등) 가 어느 ADR 를 amendment 할지 분기:
- **추천 (default)**: **ADR-058 amendment** — ADR-058 §결정 8 이 declaration SSOT 의 owner. 4 표현 dictionary 자체는 ADR-058 원본. ADR-060 는 mechanical carrier (사전 verbatim 재인용 — 본 §결정 9 본문). v1.1 확장 = ADR-058 §결정 8 amendment N.
- **선택 (대안)**: **ADR-060 amendment** — framework SSOT (4-tier / 승격 gate / bypass channel) 자체 변경 동반 시 일체화. 단일 ADR amendment 로 처리.
- **registry yaml = version 추적 only**: `evidence-checks-registry.yaml` 의 `modal_anti_pattern_dictionary.version` field 는 추적 만 — 언어 정의 SSOT 아님. amendment chain 의 단일 진실 = ADR-058 (default) 또는 ADR-060 (대안 — framework 변경 동반 시).

**Substring → word boundary 전환 의무 (v1.1 도입 carrier)**: v1.0 시점 = substring match (예: `임시` 가 `임시저장` 부분 일치 → FAIL = false positive). 의도된 conservative direction (anti-pattern bias). v1.1 확장 어휘 도입 시점 = substring → word boundary regex 전환 의무 (한국어 morpheme-aware tokenizer 또는 `\b modal \b` ASCII fallback). false positive 누적 시 운영 가이드 (§결정 5 EC-B 14d/5건 trigger) 통한 manual disable 가능.

(§5.5 CL-5 ARCHITECT-RESOLVABLE — 4 표현 only 확정. EC-2 P0-3 ADR-058 모순 해소 verbatim.)

### 결정 10 — velocity-normalized metric (throughput 독립)

승격 gate 의 metric = "20+ PR 누적 무사고" — Story 수 / 일자 / sprint 의존 X.

근거:
- codeforge wrapper repo throughput 가변 (solo-dev, dogfood + consumer 작업 혼재).
- sprint-주기 metric (예: "2 sprint 안정 후 enforce") 은 throughput 변동 시 의도와 어긋남.
- PR 누적 = 변경 누적의 직접 신호 — false positive 검증 표본 수 보장.
- bypass label PR 도 throughput 카운트 (EC-C 정합) → bypass 빈도 자체가 throughput 의 일부, 별도 metric 분리 불필요.

### 결정 11 — Framework SSOT 자체는 영구 정책 (sunset 불가)

본 ADR (ADR-060) 자체 분류 = `is_transitional: false` (permanent policy carrier). ADR-058 §결정 6 self-defeat 회피 패턴 정합. 

본 ADR 의 효력 종료 조건 = 본 ADR 의 supersede 또는 codeforge 의 evidence-enforceable governance 자체 폐지. recursive sunset 의 무한 후행 회피.

단 본 framework 의 **개별 evidence check entry** (registry yaml row) 는 individual 하게 sunset 가능:
- warning tier 운영 중 lint script 자체가 deprecate 결정 → registry yaml row `status: deprecated` 또는 row 삭제.
- enforce mode 진입 후 framework 가 영구 운영 상태 진입 (= individual entry 의 mode transition, framework SSOT 자체 sunset 아님).

### 결정 12 — Declaration + first mechanical check 일체화 (CFP-B carrier)

본 ADR 는 ADR-058 §결정 8 의 CFP-B (잠정) carrier 역할:
- declaration (framework SSOT) + first mechanical check (ADR sunset lint) 일체 도입.
- 후속 carrier 분리:
  - **CFP-390 (인벤토리 backfill)** = registry yaml 의 추가 entry 도입 (도메인 추가).
  - **CFP-391 (4-tier 정식 amendment)** = `current_tier` 필드 required 전환 + tier enum 정식 분류 (schema MINOR bump).
  - **CFP-C 잠정 (ADR-057 amendment)** = ADR-057 sunset criteria 본문 backfill + KPI dashboard. 본 framework 위에서 운영 — 첫 적용 사례.
  - **CFP-D 잠정 (retroactive backfill)** = 기존 Active 잠재 안전망 ADR sunset criteria 본문 추가.

## 결과

### 긍정

- ADR-058 declaration 의 moral governance 단계 → mechanical enforcement 점진 진입 — framework SSOT 가 forcing function 제공.
- velocity-normalized metric 로 throughput 가변 환경 (solo-dev) 친화 + sprint-주기 회피.
- 4-tier enum 으로 향후 evidence check 도입 시 mode 표현력 확보 (warning → blocking-on-pr → blocking-on-merge → hotfix-bypass).
- hotfix bypass label 채널이 ADR-024 §결정 6 + `enforce_admins: true` 와 호환 — audit-trailed exception channel 정식 도입.
- audit trail 3중 안전망 (audit comment + audit log + audit lint assertion) 이 bypass 악용 차단 (EC-A 정합).
- kind:registry SSOT 분류로 wrapper-owned cross-cutting protocol 패턴 정합 — 기존 3 entry (`comment-prefix-registry-v1` / `fix-event-v1` / `label-registry-v2`) 와 일관성.

### 부정

- registry yaml 의 첫 entry 만 보유 (sunset criteria lint) — multi-entry 운영 시 schema 유효성은 CFP-390 / CFP-391 이후 확정.
- velocity-normalized metric "20+ PR 누적 무사고" 의 측정 자동화 인프라 미도입 — 승격 carrier 가 evidence 3 산출물 manual 제출 의무 (자동화는 별도 carrier).
- warning mode false positive 폭증 시 운영 가이드 (EC-B) 가 manual disable 의존 — admin 적극 개입 필요.
- solo-dev 환경 (CFP-72 reviewer count=0) 에서 warning mode 시각적 표시만 의존 (EC-F) — 사용자 본인 적극 체크 의무.
- audit log quarterly merge 자동화 부재 (별도 carrier) — 본 Story 는 schema + bot comment 양식만.
- ADR-024 Amendment 3 동반으로 governance ADR 변경 surface 확대 (label-registry MINOR bump 동반 시).

### Trade-off

- **declaration vs enforcement 단계 분리 (ADR-058 §결정 8 패턴)**: 한 Story 에서 declaration + enforcement + retroactive backfill 일체 도입 시 risk 분산 부족 + review burden 폭증. 본 ADR 는 declaration + first mechanical check 일체화, 후속 (CFP-390 / CFP-391) 가 incremental 확장 — 단계 분리의 cost (multi-Story 의존) vs visibility (각 Story 의 결정 surface 명확화) trade-off 에서 visibility 우선.
- **warning vs blocking 첫 도입 mode**: blocking 즉시 도입 시 mechanical enforcement 효과 즉시 발현 / false positive 영향 즉시 발현. warning 시작 + 승격 gate (= ADR-050 prior art 패턴) 채택 — 효과 지연 vs false positive risk mitigation 의 trade-off 에서 위험 회피 우선.
- **bypass label per-entry vs global**: 단일 global bypass label (e.g., `evidence-bypass:*`) 도입 시 사용 단순 / 악용 위험 확대. per-entry (`hotfix-bypass:adr-sunset` 등) → namespace 분리 + 권한 분리 가능 — 사용 복잡도 vs scope 통제 trade-off 에서 통제 우선.

## 대안

### 대안 B (거부) — bypass label 미도입

bypass 채널 부재 → 운영 장애 hotfix 시 ADR-024 `enforce_admins: true` + required check 통과 의무 = deadlock. 직접 push 금지 + bypass 부재 = hotfix 불가능. **거부 사유**: 실운영 시 deadlock 위험 + ADR-024 §결정 6 (emergency hotfix 도 PR 경유 의무) 가 hotfix 채널 자체 부정 아님 — bypass channel 정식 도입 = §결정 6 정합 + audit-trailed 보장.

### 대안 C (거부) — warning mode 영구 (enforce 미승격)

declaration → warning 까지만 도입, enforce mode 영구 미도입. **거부 사유**: warning mode = continue-on-error → mechanical enforcement 실효성 부재. ADR-058 declaration 의 moral governance 단계와 본질적으로 동일 — 점진 적용 의도 미충족. 승격 gate 정의 + 자동 승격 carrier path 가 framework 의 핵심.

### 대안 D (거부) — sprint-주기 metric (예: "2 sprint 안정")

sprint 주기 기반 promotion gate. **거부 사유**: codeforge wrapper repo throughput 가변 (solo-dev). sprint 정의 자체 모호 (별도 governance 부재). PR 누적 = 변경 누적의 직접 신호 + throughput 독립 — velocity-normalized 우위.

### 대안 E (거부) — 단일 global bypass label

`evidence-bypass:*` 단일 label 모든 evidence check skip 가능. **거부 사유**: scope 통제 부재 → 한 entry hotfix 가 모든 entry bypass 우회 위험. per-entry namespace 분리 + 권한 분리 (registry entry `bypass_label` 필드) 우위.

## 다이어그램

```mermaid
graph TD
    A[ADR-058 declaration] -->|CFP-B carrier| B[ADR-060 framework SSOT]
    B --> C[evidence-check-registry-v1.md schema]
    B --> D[evidence-checks-registry.yaml data]
    D --> E[entry 1: adr-sunset-criteria<br/>tier=warning]
    E --> F[scripts/check-adr-sunset-criteria.sh]
    E --> G[adr-sunset-criteria.yml workflow<br/>continue-on-error: true]
    E --> H[hotfix-bypass:adr-sunset label]
    H --> I[scripts/check-bypass-audit-comment.sh]
    H --> J[ADR-024 Amendment 3]
    
    K[승격 gate AND] -->|PR 누적 ≥ 20| L[promote]
    K -->|failure = 0| L
    K -->|"CFP-390 + CFP-412 + CFP-455 merged<br/>(Amendment 2: CFP-412 폐기 → CFP-455 carrier)"| L
    L --> M[blocking-on-pr / blocking-on-merge]
    M --> N[required_status_checks.contexts 부착]
    N --> O[ADR-024 Amendment 2 manifest 갱신]
```

## 해소 기준

N/A — permanent policy. 본 ADR 은 `is_transitional: false` (permanent policy carrier — framework SSOT). §결정 11 self-defeat 회피.

단 본 framework 의 **개별 evidence check entry** 는 individual sunset 가능 — entry level 의 mode transition (warning → enforce) 은 framework 운영의 정상 동작이며 framework SSOT 자체 sunset 이 아님.

## 관련 파일

- `docs/inter-plugin-contracts/evidence-check-registry-v1.md` — framework SSOT (kind:registry schema doc, 결정 1)
- `docs/inter-plugin-contracts/MANIFEST.yaml` — `registries:` 블록 entry 추가 (결정 1)
- `docs/evidence-checks-registry.yaml` — registry data, 첫 entry = adr-sunset-criteria (결정 2 + 결정 4)
- `docs/doc-locations.yaml` — 신규 doc type `evidence_check_registry` row 추가 (ADR-041 §결정 정합, §5.5 CL-2)
- `docs/parallel-work/section-ownership.yaml` — 신규 entry: `evidence-checks-registry.yaml` parallel_edit=append-only (ADR-050 정합)
- `scripts/check-adr-sunset-criteria.sh` — lint 첫 구체 (결정 4)
- `scripts/check-bypass-audit-comment.sh` — audit assertion lint (결정 8)
- `templates/github-workflows/adr-sunset-criteria.yml` — warning mode workflow (결정 5)
- `docs/adr/ADR-024-story-scoped-branch-policy.md` — Amendment 3 동반 (결정 7)
- `CLAUDE.md` — 3 섹션 갱신 (ADR / GitHub Workflow / Inter-plugin Contract)
- `docs/adr/ADR-RESERVATION.md` — ADR-060 row reserved (CFP-389, 2026-05-11)
- 후속 carrier:
  - CFP-390 (인벤토리 backfill — registry yaml row append, ADR-060 **Amendment 1 carrier — 이미 발효**)
  - **CFP-391 (Issue #396, 2026-05-11 closed without delivery — 폐기 처리)** → **CFP-412 (Issue #412, 재예약 carrier)** 가 4-tier 정식 amendment 책임 (ADR-060 Amendment 2 + schema v1.0 → v1.1 MINOR bump)
  - **CFP-TBD (메타 anomaly lint carrier — Amendment 1 §결정 14 명시 의무, Codex P2-B 정합)**: 인벤토리 누락 시 anomaly 감지 메타 lint (`scripts/check-evidence-registry.sh` 또는 동등) 발의. CFP-390 Phase 1 PR merge 후 별도 CFP/Issue 발의.
  - CFP-C 잠정 (ADR-057 amendment + KPI dashboard — 첫 적용 사례)
  - CFP-D 잠정 (retroactive backfill — 기존 안전망 ADR sunset criteria 본문 추가)

## Amendment 1 (CFP-390, 2026-05-11)

본 Amendment 는 CFP-390 (인벤토리 backfill, Issue #395) 의 Phase 1 carrier 산출물.

ADR-060 framework SSOT 의 4 정정:

### Amendment 1-결정 6 (c) 정정 — `sibling_dependencies` CFP-391 → CFP-412 verbatim 정정

본 ADR §결정 6 (c) `sibling_dependencies` 의 의미 = warning → enforce 승격 전 main merge 의무 sibling Story. 원본 항목 `CFP-391` (Issue #396, 4-tier 정식 amendment 예상 carrier) 는 2026-05-11 시점 **closed without delivery** (Issue #396 close, 4-tier amendment 작업 미실행). 후속 carrier 재예약 = **CFP-412** (Issue #412 — 4-tier amendment 재예약 carrier).

따라서 `docs/evidence-checks-registry.yaml` 의 `entries[name=adr-sunset-criteria].promotion_criteria.sibling_dependencies` 다음과 같이 정정 의무 (본 Amendment 1 carrier PR 동반):

```yaml
sibling_dependencies:            # ADR-060 §결정 6 (c) — Amendment 1 정정
  - CFP-390  # 인벤토리 backfill — 본 Amendment 1 carrier (이미 발효)
  - CFP-412  # 4-tier amendment 재예약 carrier (CFP-391 #396 폐기 처리)
```

### Amendment 1-결정 12 정정 — 후속 carrier 목록 정정

본 ADR §결정 12 의 후속 carrier 목록 4 항목 중 CFP-391 항목 정정:

- **CFP-391 (4-tier 정식 amendment)** (원본 표기) →
- **CFP-391 (Issue #396 closed without delivery, 2026-05-11) → CFP-412 (Issue #412) 가 4-tier 정식 amendment carrier 재예약** (`current_tier` required 전환 + tier enum 정식 분류 + schema v1.0 → v1.1 MINOR bump)

본 정정은 ADR-058 §결정 9 amendment chain 정책 (framework SSOT 변경 동반 시 framework ADR amendment 정합) 정합. 4-tier amendment 자체는 framework SSOT 의 schema field semantic 변경 (`current_tier` optional → required) 동반 → ADR-060 amendment 가 정합 carrier.

### Amendment 1-결정 13 (신설) — 인벤토리 backfill SSOT (18 entry 그룹 A 등록 — FIX iter 1 정정 후)

> **Scope 한정**: 본 표는 CFP-389 / CFP-390 작업 시점 "기존 ad-hoc evidence check" 인벤토리만 포함. 후속 framework entry (예: CFP-393 가 추가한 `rate-limit-fallback-rate`) 는 표 scope 외 — 각 carrier ADR / Story 가 자체 registry row 등록을 책임진다.

본 CFP-390 = ADR-060 framework 의 첫 multi-entry registry 운영 진입. CodebaseMapper deputy perspective 통합 정밀 verify (scripts/check-*.sh 33개 + .github/workflows/ 20개 + templates/github-workflows/ 24개 전수 inspect) 결과 4-criteria (detect_command + workflow + owner_adr/contract + tier signal) PASS entry 18개 그룹 A 등록 (Codex Proactive Check #2/#6 FIND-3 정정 후 — owner_adr 정합 ADR/contract 명확 entry 만).

**Scope split 명시 (FIND-2 정정)**:
- **Phase 1 PR (본 carrier) = SSOT 만**: 본 §결정 13 표 + 그룹 B/C 분류 + sibling_dependencies field substitution (CFP-391 → CFP-412) + CLAUDE.md cross-ref. registry yaml 의 실제 row append 는 **수행하지 않음**.
- **Phase 2 PR scope = 본 §결정 13 표의 18 entry 실제 row append**: `docs/evidence-checks-registry.yaml` 의 schema v1.0 정합 row 작성. doc-only fast-path 적용 가능성 ArchitectAgent / DeveloperPL 후속 판단 (ADR-054 정합, 모호 시 full-lane).
- **tier 재계산 (FIND-4 정정)**: 실제 `templates/branch-protection-manifest.yaml` 부착 entry 만 `blocking-on-pr` / `blocking-on-merge` 분류. 미부착 entry = `warning` 일괄 하향. manifest 부착 = 2 entry (invariant-check / phase-gate-mergeable). doc-frontmatter-schema / doc-section-schema 는 manifest 부착 (row 3/4) 이나 owner_adr 모호로 FIND-3 그룹 B 강등.

**그룹 A — 18 entry SSOT (Phase 2 PR row append target)**:

| # | name | detect_command | workflow | owner_adr/contract | tier (final) |
|---|---|---|---|---|---|
| 1 | `lane-evidence-trail` | `bash scripts/check-lane-evidence.sh` | `.github/workflows/lane-evidence-check.yml` | ADR-031 §결정 3 + fix-event-v1 | `warning` (manifest 미부착) |
| 2 | `doc-locations-registry` | `bash scripts/check-doc-locations.sh --full` | `.github/workflows/doc-locations-check.yml` | ADR-041 | `warning` (manifest 미부착 — CLAUDE.md "5번째" narrative 와 drift, 별도 Issue 권고) |
| 3 | `marketplace-parity` | `bash scripts/check-marketplace-parity.sh` | `.github/workflows/marketplace-parity.yml` | ADR-016 / ADR-023 §결정 5 | `warning` |
| 4 | `invariant-check` | (workflow inline — 5 invariant 직접) | `.github/workflows/invariant-check.yml` | ADR-002 (footer pattern) + 다중 CFP (5/7/8/10) | `blocking-on-pr` (branch-protection-manifest row 2) |
| 5 | `phase-gate-mergeable` | (workflow inline — cross-repo Story fetch) | `.github/workflows/phase-gate-mergeable.yml` | ADR-031 §결정 3 + label-registry-v2 | `blocking-on-merge` (branch-protection-manifest row 1, dynamic checks.create) |
| 6 | `inter-plugin-contracts` | `bash scripts/check-inter-plugin-contracts.sh` | `.github/workflows/contract-lint.yml` job:`inter-plugin-contracts` | ADR-008 / ADR-010 / MANIFEST.yaml | `warning` |
| 7 | `inter-plugin-drift` | `bash scripts/check-inter-plugin-drift.sh` | `.github/workflows/contract-lint.yml` job:`inter-plugin-drift` | ADR-011 | `warning` |
| 8 | `comment-prefix-registry` | `bash scripts/check-comment-prefix.sh` | `.github/workflows/contract-lint.yml` job:`comment-prefix-registry` | comment-prefix-registry-v1 (kind:registry) | `warning` |
| 9 | `label-registry-sync` | `bash scripts/check-label-registry.sh` | `.github/workflows/contract-lint.yml` job:`label-registry-sync` | label-registry-v2 (kind:registry) | `warning` |
| 10 | ~~`marketplace-sync`~~ (retired CFP-457) | ~~`bash scripts/check-marketplace-sync.sh`~~ | ~~`.github/workflows/contract-lint.yml` job:`marketplace-sync`~~ | ~~ADR-016~~ | ~~`warning`~~ — see entry #5 `marketplace-parity` (CFP-50 / ADR-023) for SSOT |
| 11 | `dogfood-artifact-paths` | `bash scripts/check-dogfood-artifact-paths.sh` | `.github/workflows/dogfood-artifact-paths.yml` | ADR-013 / ADR-017 | `warning` |
| 12 | `superpowers-integration` | `bash scripts/check-superpowers-integration.sh` | `.github/workflows/superpowers-integration.yml` | ADR-028 / CFP-113 | `warning` |
| 13 | `superpowers-schema-drift` | `bash scripts/check-superpowers-schema-drift.sh` | `.github/workflows/superpowers-schema-drift.yml` | ADR-028 / CFP-121 | `warning` (scheduled quarterly + PR:paths) |
| 14 | `parallel-epic-conflict` | (workflow inline — PR file 교집합) | `.github/workflows/parallel-epic-conflict-check.yml` | ADR-050 | `warning` (continue-on-error prior art) |
| 15 | `branch-protection-drift` | (workflow inline — gh api + manifest diff) | `.github/workflows/branch-protection-drift-check.yml` | ADR-024 Amendment 2 | `warning` (weekly Mon 09:00 UTC cron) |
| 16 | `required-workflow-drift` | (workflow inline + `check-enterprise-admin.sh`) | `.github/workflows/required-workflow-drift-check.yml` | ADR-048 §결정 3 | `warning` (weekly Mon 10:00 UTC cron) |
| 17 | `rulesets-drift` | (workflow inline + `check-enterprise-admin.sh`) | `.github/workflows/rulesets-drift-check.yml` | ADR-048 §결정 1 | `warning` (daily 09:00 UTC cron) |
| 18 | `write-permission-redistribution` | `bash scripts/check-write-permission-redistribution.sh` | `.github/workflows/lint.yml` job:`write-permission-redistribution` | CFP-26 / ADR-009 (write 권한 invariant) | `warning` |

**tier 최종 분포**: `blocking-on-merge` 1 (phase-gate-mergeable) + `blocking-on-pr` 1 (invariant-check) + `warning` 16. manifest 부착 entry 만 blocking 분류.

**그룹 B — 보류 (별도 carrier 책임, 14 entry — FIND-3 강등 8 + 기존 6)**:

| name | 미충족 / 모호 | 처리 |
|---|---|---|
| `story-section-schema` | (c) **owner_adr 정합 ADR 미존재** — CFP-91 / CFP-94 비-ADR (FIND-3 강등) | 등록 보류 — CFP-412 schema v1.1 또는 별도 carrier 가 `owner_adr=null` 또는 `owner_contract` enum 도입 후 등록 |
| `doc-frontmatter-schema` | (c) **owner_adr 정합 ADR 미존재** — CFP-28 비-ADR (FIND-3 강등, manifest row 3 부착이나 owner_adr governance integrity 약함) | 동일 — schema v1.1 owner_adr=null 도입 후 등록 + 부착된 manifest row 와 tier 정합 별도 검토 |
| `doc-section-schema` | (c) **owner_adr 정합 ADR 미존재** — CFP-28 비-ADR (FIND-3 강등, manifest row 4 부착이나 owner_adr governance integrity 약함) | 동일 |
| `workflow-yaml-syntax` | (c) **owner_adr 정합 ADR 미존재** — CFP-34 비-ADR (FIND-3 강등) | 동일 |
| `consumer-scripts-manifest` | (c) **owner_adr 정합 ADR 미존재** — CFP-109 비-ADR (FIND-3 강등) | 동일 |
| `script-exec-bit` | (c) **owner_adr 정합 ADR 미존재** — CFP-74 invariant 비-ADR (FIND-3 강등) | 동일 |
| `markdown-internal-links` | (c) **owner_adr 정합 ADR 미존재** — CFP 미명시 (FIND-3 강등) | 동일 |
| `agent-frontmatter` | (c) ADR-042 = agent **model selection** policy 이지 agent frontmatter contract 의 owner 아님 — owner_adr 정합 ADR 미존재 (FIND-3 강등) | 동일 |
| `check-fix-evidence` | (b) workflow trigger 부재 (CFP-298 carrier 책임 — wrapper repo 미배치 가능성) | 등록 보류 — Phase 2 또는 별도 carrier 에서 workflow 도입 후 등록 |
| `check-no-atlassian` | (c) owner_adr 부재 (meta-governance) BUT detect_command 보유. workflow trigger 명확치 않음 | 등록 보류 — owner_adr 도입 후속 carrier 발의 권고 |
| `check-container-strategy` | (c) ADR-033 명확 BUT (b) workflow trigger 부재 — `container-image-scan.yml` consumer-only | 등록 보류 — consumer-only entry 분류 정책 명확화 후 |
| `check-domain-knowledge-schema` | (b) workflow trigger 명확치 않음 | 등록 보류 — workflow trigger 검증 후 |
| `check-review-verdict-v4` | (b) workflow trigger 명확치 않음 | 등록 보류 — workflow trigger 추가 도입 후 (CFP-137 후속) |
| `check-team-spec-schema` | (b) workflow trigger 명확치 않음 | 등록 보류 — workflow trigger 추가 도입 후 (CFP-137 후속) |

**그룹 C — 등록 제외 (4-criteria 미충족 / consumer-only / sub-utility)**:

- `check-codeforge-version-drift` — workflow 부재 (session-start CLI script, CLAUDE.md 세션 개시 의무 0번)
- `check-enterprise-admin` — sub-utility (rulesets-drift-check + required-workflow-drift-check 의 step, 단독 workflow 없음)
- `check-debut-audit-signals` / `check-debut-readiness` — consumer-specific (ADR-021 mctrader debut audit, wrapper governance scope 외)
- `check-doc-links` — `markdown-internal-links` (lint.yml inline) 와 중복
- bootstrap-*.sh / test-*.sh (30+) / audit-trail-fetch.sh / next-phase.sh / migrate-*.sh / post-merge-*.sh / sync-*.sh / retro-retry-helper.sh / check-lint.sh — not lint / helper / migration
- consumer-only workflow: live-test-guard.yml / live-deploy-approval.yml / live-secret-policy.yml / kill-switch-integration-test.yml / story-init.yml / story-section-1-immutable.yml / fix-ledger-sync.yml / subissue-from-impl-manifest.yml / reservation-cleanup.yml / check-plugin-version-bump.yml / container-image-scan.yml / retro-mandatory.yml / test.yml (CONSUMER_ONLY_WORKFLOWS 명시, invariant-check.yml SSOT)

본 그룹 A **18 entry** (FIX iter 1 정정 후 — owner_adr 정합 ADR/contract 명확 entry 만, 8 entry 그룹 B 강등) 의 registry yaml row append 는 **CFP-390 Phase 2 PR scope** (본 Amendment 1 = Phase 1 ADR 갱신 + 후속 carrier 정정 + 인벤토리 SSOT 확정). Phase 2 PR 진행 여부 = doc-only fast-path 가능성 ArchitectAgent / DeveloperPL 판단 (ADR-054 모호 시 full-lane).

### Amendment 1-결정 14 (신설) — 메타 anomaly lint 후속 carrier 의무 명시 (Codex P2-B 정합)

본 CFP-390 인벤토리 backfill = manual sweep. 후속 신규 evidence-enforceable 패턴 (script + workflow) 도입 시 registry 등록 누락 = governance drift 위험. Codex Proactive Check #4 P2-B (사전 수렴 시점 raised) finding 정합 — 본 Amendment 1 가 메타 anomaly lint 후속 carrier 의무 명시:

- **carrier 발의 의무**: CFP-390 Phase 1 PR merge 후 별도 CFP/Issue 발의. 본 Story scope 외.
- **carrier scope**: `scripts/check-evidence-registry.sh` (또는 동등) 신설 — registry yaml 미등록 신규 evidence-enforceable 패턴 (예: 신규 `.github/workflows/*.yml` + `scripts/check-*.sh` 동반 도입 PR) 자동 발견 lint.
- **trigger 추정**: `.github/workflows/evidence-registry-anomaly.yml` (pull_request:paths) — script/workflow file 변경 시 registry yaml 등록 누락 lint.
- **tier 추정**: `warning` (false positive 위험 — 새 lint script 가 production 정합 의제로 즉시 인식 부담).
- **owner_adr 후보**: ADR-060 (본 framework SSOT — meta lint 가 framework 의 안전망 강화 측면).

본 carrier 부재 시 = manual inventory sweep 정합 유지 (반복 CFP 비용). 본 Amendment 14 명시 = CFP-390 retro (§11) 의 reminder 1 항목 + 후속 발의 의무 SSOT 화.

## Amendment 2 (CFP-455, 2026-05-12)

본 Amendment 는 CFP-455 (4-tier enforcement 분류 정식화, Issue #455) 의 Phase 1 carrier 산출물. CFP-391 (Issue #396, closed without delivery 2026-05-11) / CFP-412 (Issue #412, post-merge-followup workflow false-positive close 2026-05-11) 의 재재예약 carrier — 4-tier amendment 정식 deliver.

### Amendment 2-결정 3 (변경) — `current_tier` 필드 optional → required 전환 명시

본 ADR §결정 3 의 4-tier enum 본문 "본 ADR (CFP-389) 의 첫 entry = `warning` tier. 후속 Story (CFP-391) 가 본 enum 을 정식 명시 + 기존 entry retroactive 분류. 본 ADR 시점에서는 enum 정의만 제공, registry yaml 의 `current_tier` 필드는 optional (CFP-391 시점 required 전환 = MINOR bump)." → **본 CFP-455 (4-tier 정식 amendment carrier, CFP-391 #396 / CFP-412 #412 폐기 후 재예약) 가 `current_tier` 필드 optional → required 전환을 정식 deliver**. schema doc `docs/inter-plugin-contracts/evidence-check-registry-v1.md` v1.0 → v1.1 MINOR bump 동반 + registry yaml `schema_version: "1.0"` → `"1.1"` header 갱신 동반.

**retroactive 분류 검증 의무**: 본 Amendment 2 시점 = 22/22 entry 모두 현행 `current_tier` 보유 verified (CodebaseMapper deputy perspective 정밀 verify, 2026-05-12). mechanical regression 0건 — 신규 메타 lint (`scripts/check-evidence-registry.sh`, Phase 2 PR scope) 가 schema 정합 mechanical 강제.

### Amendment 2-결정 6 (c) 정정 — `sibling_dependencies` field back-substitution (append)

본 ADR §결정 6 (c) 의 `sibling_dependencies` 의미 = warning → enforce 승격 전 main merge 의무 sibling Story. Amendment 1 시점 = `[CFP-390, CFP-412]` (CFP-391 → CFP-412 정정). CFP-412 Issue #412 도 closed without delivery (2026-05-11T15:41:42Z, post-merge-followup workflow false-positive close — PR #421 = CFP-393 rate-limit-fallback 작업, "Closes #412" reference 없음) — 4-tier amendment 0 commits. 본 Amendment 2 의 결정:

```yaml
sibling_dependencies:            # ADR-060 §결정 6 (c) — Amendment 2 정정 (CFP-455)
  - CFP-390  # 인벤토리 backfill — 본 Amendment 1 carrier (이미 발효)
  - CFP-412  # 4-tier amendment 재예약 carrier (CFP-391 #396 폐기 처리) — Amendment 1 정정 / CFP-412 자체도 #412 closed without delivery
  - CFP-455  # 4-tier 정식 amendment carrier (재재예약) — 본 Amendment 2 deliver
```

**append 결정 근거** (DataMigrationArch deputy + RequirementsPL Q2 권고 verbatim 채택):
- CFP-412 의 폐기 history 가 registry yaml 에서 visible 보존 (replace 시 invisible 위험).
- sibling 의도 ("4-tier amendment 가 main merge 의무") 보존 — append 로 chain 가시화.
- 폐기 carrier 의 trail 이 framework SSOT 의 governance integrity 강화.

### Amendment 2-결정 14 (정정) — 메타 anomaly lint 와 메타 schema validation lint 분리 (별도 entry 2종)

Amendment 1 §결정 14 의 메타 anomaly lint (인벤토리 누락 감지) 와 본 Amendment 2 가 도입 명시하는 메타 schema validation lint (`scripts/check-evidence-registry.sh`, 본 Story Phase 2 PR scope) 는 **scope 가 다른 별도 lint 2종**:

| lint | scope | trigger | tier |
|---|---|---|---|
| **메타 schema validation** (본 Story 도입) | registry yaml 자체 schema/일관성 검증 — 6 검증 (schema_version / entry required field / current_tier enum / bypass pair / name uniq / owner_adr+carrier_adr ADR file cross-ref) | `pull_request:paths` (registry yaml + contract md + lint script 변경 시) | `warning` (continue-on-error) |
| **메타 anomaly detection** (§결정 14 후속 carrier, 본 Story scope 외) | registry yaml 미등록 신규 evidence-enforceable 패턴 자동 발견 (신규 `.github/workflows/*.yml` + `scripts/check-*.sh` 동반 도입 PR) | `pull_request:paths` (workflows + scripts 변경 시) | `warning` (false positive 위험) |

**분리 근거** (RequirementsPL Q6 권고 verbatim 채택): 통합 시 lint script 복잡도 증가 + trigger paths 모호. 분리 시 각자 carrier 별도 (메타 schema validation = 본 Story CFP-455 / 메타 anomaly = §결정 14 후속 carrier).

### Amendment 2-결정 15 (신설) — 메타 lint exit-code 3-tier semantics (Codex AREA 1 정합)

`scripts/check-evidence-registry.sh` (Phase 2 PR scope) 의 exit code 의미:

| exit code | 의미 | 처리 |
|---|---|---|
| **0** | PASS — 모든 검증 통과 | normal continuation |
| **1** | validation FAIL — 1+ entry 가 schema 위반 (current_tier 부재 / enum 외 값 / bypass pair 위반 / name 중복 / owner_adr+carrier_adr ADR file 부재 등) | warning mode = continue-on-error (PR merge 가능) / blocking mode 승격 시 PR block |
| **2** | meta-error — tooling 오류 (yaml 파싱 실패 / pyyaml 미설치 / registry yaml 자체 file 부재 / ADR file glob unreadable 등) | warning / blocking 무관 = 명확한 error message 출력 + workflow job step fail (lint logic 실행 불가 상황 분리 명시) |

**근거**: validation FAIL 과 meta-error 의 semantic 분리 — meta-error 가 false-positive validation FAIL 로 위장되면 운영 신뢰도 추적 (ADR-060 §결정 5 EC-B 14d/5건 trigger) 가 왜곡. 3-tier semantics 도입 = false positive rate 측정의 무결성 보장.

### Amendment 2-결정 16 (신설) — warning-tier bypass_label policy (Codex AREA 2 (a) 정합)

본 ADR §결정 7 의 `bypass_label` 정책 명세화:

- **warning tier** = continue-on-error / non-blocking. bypass_label 적용은 의미 부적용 (skip 의미 없음 — 이미 PR block X). → `bypass_label` field = **optional** (omit 권고).
- **blocking-on-pr / blocking-on-merge / hotfix-bypass tier** = required check. bypass_label 의무 분리:
  - `blocking-on-pr` / `blocking-on-merge` = bypass_label optional (운영 장애 hotfix 시 도입 가능, 미도입 시 emergency-channel 부재 risk 분리 평가).
  - `hotfix-bypass` = bypass_label **required** (정의상 bypass channel SSOT).

**본 Story 의 메타 lint self-application entry** (Phase 2 PR scope) = warning tier → bypass_label omit. 정합: SecurityArch deputy spoofing 차단 invariant 강화 (bypass field 의 잘못된 의미 부여 회피).

### Amendment 2-결정 17 (신설) — Retroactive reclassification failure handling (Codex AREA 2 (b) 정합)

본 Amendment 2 의 `current_tier` required 전환 시점 = 22/22 entry 모두 현행 `current_tier` 보유 verified (CodebaseMapper deputy 정밀 verify). 단 future drift / human error 로 enum membership 위반 발견 시 (예: 신규 entry 가 `current_tier: hard_block` 사용자 alias 주입, registry yaml 의 retroactive corruption):

- **처리**: `scripts/check-evidence-registry.sh` exit 1 (validation FAIL) + PR block (blocking mode 승격 시) — **immediate fail**.
- **근거**: required tier 도입 의의 정합 — schema 정합 mechanical 강제가 framework SSOT 의 핵심. tolerant mode (warning continuation) 도입 시 required 의 mechanical 효력 무력화.
- **본 Story 단계 (warning mode)** = continue-on-error → PR merge 가능 but lint output 의 violation 명확 표시 + 운영 가이드 ADR-060 §결정 5 EC-B 14d/5건 trigger 적용. 실제 PR block 효과는 promotion carrier 시점 (별도 CFP-NNN, evidence 6 산출물 제출 시).

### Amendment 2-결정 18 (신설) — Marketplace/sibling sync necessity 명시 (Codex AREA 2 (c) 정합)

본 Amendment 2 의 schema v1.0 → v1.1 MINOR bump 시 sibling sync 의무 분석:

- **registry yaml** (`docs/evidence-checks-registry.yaml`) = wrapper-owned cross-cutting protocol (kind:registry, ADR-010 scope 외 = sibling sync 불필요).
- **schema doc** (`docs/inter-plugin-contracts/evidence-check-registry-v1.md`) = wrapper-owned canonical (ADR-010 scope 외 = sibling sync 불필요).
- **MANIFEST.yaml** = wrapper-owned cross-cutting registry list (sibling sync 불필요).
- **marketplace.json mirrored field sync**: schema v1.1 bump 동반 plugin.json MINOR bump (5.18.0 → 5.19.0, ADR-037 정합 — CFP-500 이 main 에서 5.18.0 차지 후 rebase 시 5.19.0 으로 re-bump) → ADR-063 §결정 1 atomic invariant (plugin.json + CHANGELOG.md + marketplace.json 동시 처리) 발효 → marketplace sync PR **의무** (별도 PR, codeforge PR merge 후 즉시 open·merge — ADR-063 §결정 2 chicken-and-egg 회피).

**정리**: kind:registry schema 변경 자체는 sibling sync 불필요 (Codex AREA 2 (c) 권고 정합). 단 plugin version MINOR bump 동반 시 marketplace.json mirrored field sync 가 ADR-063 invariant 로 의무. 본 Story Phase 2 PR (또는 Phase 1 PR) 의 plugin.json MINOR bump 와 같은 PR 안 처리.

### Mermaid 다이어그램 동기화 (Amendment 2 — Codex AREA 4 정합)

본 ADR `## 다이어그램` Mermaid 의 `K -->|"CFP-390 + CFP-412 merged<br/>(Amendment 1: CFP-391 폐기 → CFP-412)"|` row 갱신 의무 (Amendment 2 시점 CFP-412 도 폐기 → CFP-455 carrier append):

본 Amendment 2 carrier PR 안에서 `## 다이어그램` 본문의 해당 row 를 `K -->|"CFP-390 + CFP-412 + CFP-455 merged<br/>(Amendment 2: CFP-412 폐기 → CFP-455 carrier)"|` 으로 갱신 (carrier PR 본 §결정 동반 직접 edit). Mermaid stale 차단 — diagram 이 §결정 6 (c) sibling_dependencies 의 SSOT 와 verbatim 정합.

