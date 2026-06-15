---
adr_number: 49
title: Issue Types + Sub-issues Native Migration (label hack → 1st-class)
status: Proposed
category: Team & Process
date: 2026-05-09
related_files:
  - templates/issue-types.yaml
  - templates/github-issue-forms/audit.yml
  - templates/github-issue-forms/bug.yml
  - templates/github-issue-forms/story.yml
  - templates/github-issue-forms/cfp-reserve.yml
  - templates/github-workflows/story-init.yml
  - templates/github-workflows/subissue-from-impl-manifest.yml
  - scripts/migrate-label-to-issue-type.sh
  - scripts/bootstrap-labels.sh
  - docs/inter-plugin-contracts/label-registry-v1.md
  - docs/inter-plugin-contracts/label-registry-v2.md
related_stories:
  - CFP-140
  - CFP-2251  # Amendment 1 carrier — type:* → native Issue Type 실 org cutover (additive)
amends:
  - ADR-008
supersedes: null
is_transitional: false
amendment_log:
  - amendment: 1
    date: 2026-06-15
    story: CFP-2251
    scope: "Amendment 1 — type:* → native Issue Type 실 org cutover (ADR-049 Phase 2 실행 결정, 완료). org 재구성 = ADDITIVE: 기존 org type [Task, Bug, Feature] 보존 + Story(id 34327613)/Epic(id 34327614) 신설 + Bug(id 28762364) 재사용 (type:bug 매핑). Audit 은 본 cutover 미포함 (deferred). 마이그레이션 = type:* 라벨 부착 전체 487 이슈 (story 415 + epic 46 + bug 26, open+closed) → native Issue Type --apply + --verify PASS (0 불일치). 실측 결함 정정: REST 이슈 type 부착 payload = `-f type=<이름>` (type_id 는 silent 무시 — story-init.yml L556 동일 결함, S4 #2252 FU). label deprecate 타이밍 = type:* 라벨 물리 삭제 + story-init.yml trigger native-type 전환을 S4 로 sequencing (라벨 선삭제 시 story-init 깨짐 — transient dual-state 허용, §결정 11 정합). 본 Story 는 deprecated 마킹까지. 본문 §결정 1 의 4-type 안 중 Audit 만 deferred 로 조정 (additive 방향 — 기존 결정 축소 0, 실행 결정 추가)."
    sunset_justification: "본 Amendment 는 weakening/reversal 이 아니라 ADR-049 본문 §결정 4/9 (migration script + migration timing) 의 실 실행 결정 추가 — additive ratchet. 기존 §결정 1-12 본문 변경 0 (Audit 만 deferred 조정 = 범위 축소가 아니라 실행 단계 분리). 따라서 sunset/원복 trigger 부재 — cutover 완료 후 영구. (additive amendment 의 sunset_justification = additive 방향 명시. ADR-058 §결정 5 self-application — Amendment 시 본 필드 의무 정합.)"
---

# ADR-049: Issue Types + Sub-issues Native Migration

## 상태

Proposed (2026-05-09) — CFP-140 carrier.
Amendment 1 (2026-06-15) — CFP-2251 carrier: type:* → native Issue Type 실 org cutover (additive 재구성). 아래 "## Amendment 1" 참조.

## 컨텍스트

codeforge 의 Issue 분류 = label hack `type:epic / type:story / type:bug` (3 entry, label-registry-v1) + impl-manifest sub-issue 표지 별도 axis. 그러나:

1. **GitHub Issue Types GA** (2025 Q4, org-level) — native type 부착 (REST `POST /repos/.../issues body {type: "Story"}`). 4 type max ~30 per org.
2. **GitHub Sub-issues GA** (2025) — parent-child 관계 + 1 parent only + max depth 8 levels.
3. **Projects v2 Hierarchy view GA** (2026-01) — roll-up + group by parent.
4. label `type:*` 와 native Issue Types 공존 가능하나 → drift / inconsistency 유발 (수동 label 부착 누락 / native type 부재 시 ambiguous). 이론적으로 cutover 가 자연스러운 evolution.

본 결정 = label hack → native Issue Types + sub-issues cutover. label-registry-v1 → v2 MAJOR bump. ADR-048 (governance-as-code) 와 별개 axis — Issue Types 의 schema 변경 + migration mechanism + label-registry contract version bump 가 core 결정.

**CFP 운영 의도** (Story §5.5 Q-3 사용자 확인 resolved): CFP 는 Story sub-category 로 유지 — 별도 native Issue Type 으로 분리하지 않음. label `type:cfp` 는 본 Story 시점 부재 (label-registry-v1 type 4 entry: epic/story/bug + impl-manifest sub-issue axis). CFP Issue 는 Story Issue Type 의 sub-category 로 운영 (Issue title prefix `[CFP-NNN]` + Story Issue Type 부착).

**Migration timing** (Story §5.5 Q-4 사용자 확인 resolved): mctrader debut audit complete 후 defer. Phase 1 PR = ADR + spec + skeleton + plan only (실 migration 0). Phase 2 PR step 2 = 사용자 explicit confirm 후 100+ Issue 일괄 변환.

## 결정

**1. native Issue Types 4 type 도입** — `templates/issue-types.yaml` 신설. org-level 정의:
   - `Epic` (사용자 요구사항 1건 = Milestone + Issue, 기존 label `type:epic` 대체)
   - `Story` (PR 1쌍 = Phase 1 + Phase 2, 기존 label `type:story` 대체. CFP 도 본 type 의 sub-category)
   - `Bug` (기존 label `type:bug` 대체)
   - `Audit` (CFP-140 신규 — governance audit Issue, 기존 label `audit` axis 와 별도)

   `impl-manifest` label 은 sub-issue 표지 별도 axis 로 잔존 (label-registry-v2 에 entry 유지).

**2. Sub-issues hierarchy 도입** — 3-level: Epic → Story → CFP/Sub-issue. `POST /repos/{owner}/{repo}/issues/{number}/sub_issues` API 활용. 1 parent only 원칙 (GitHub native enforcement). Projects v2 Hierarchy view 활용.

**3. label-registry-v1 → v2 MAJOR bump** — `docs/inter-plugin-contracts/label-registry-v1.md` `status: Active → Archived`, `docs/inter-plugin-contracts/label-registry-v2.md` 신설. v2 변경:
   - type:* 3 entry deprecate (epic / story / bug) — native Issue Types 로 대체
   - impl-manifest sub-issue 표지 axis 잔존
   - 신규 metadata: `replaced_by_native_issue_type: <type_name>` field (deprecate entry 명시)
   - phase / gate / fix / hotfix / audit / category label 영역 무변경

**4. migration script 신설** — `scripts/migrate-label-to-issue-type.sh`:
   - Mode: `--dry-run` (default) / `--apply` / `--rollback --batch-id <N>` / `--verify`
   - Idempotent: 2회 `--apply` = 1회 결과 (이미 변환 Issue skip)
   - Batch: `--batch-size 50` (rate limit 안전 마진 — 5000 pt/hr GraphQL 의 ~100 batch/hr cap 대비 50 batch + sleep 1s 적용)
   - Audit trail: 매 batch 결과 → audit Issue (label `migration-batch-<N>`)
   - Rollback: batch-id 단위만 (per-Issue rollback 미지원 — over-engineering 회피)

**5. story-init.yml Action 갱신** — Issue Form 제출 시 native Issue Types API 호출:
   - `POST /repos/{owner}/{repo}/issues body {type: "Story"}` (또는 Epic / Bug / Audit)
   - 기존 label `type:story` 미부착 (label-registry-v2)
   - org Issue Types 미활성 시 graceful fallback (label hack 사용 + warning log)

**6. github-issue-forms/*.yml 4 file 갱신** — `issue_type` field 추가 (audit / bug / story / cfp-reserve):
   - `audit.yml` → `issue_type: Audit`
   - `bug.yml` → `issue_type: Bug`
   - `story.yml` → `issue_type: Story`
   - `cfp-reserve.yml` → `issue_type: Story` (CFP = Story sub-category, sub-issue 로 parent Story 에 attach)

**7. subissue-from-impl-manifest.yml Action 갱신** — sub-issue API (`POST /repos/.../issues/{number}/sub_issues`) 사용. impl-manifest label 은 sub-issue 의 visual 표지 axis 유지.

**8. bootstrap-labels.sh 갱신** — type:* 3 entry 제거 (script 가 label-registry-v2 mirror).

**9. Migration timing** — mctrader debut audit complete 직후. Phase 1 PR = doc-only (label-registry-v2 신설 + ADR + spec). Phase 2 PR step 2 = 사용자 explicit confirm 후 실 migration 실행 (`--dry-run` → review → `--apply --batch-size 50` → `--verify`).

**10. Rollback 경로** — batch-id 단위. label-registry-v2 → v1 rollback = sibling sync revert PR (ADR-010 정합).

**11. ADR-008 amendment**: contract version bump (label-registry MAJOR bump) ≠ codeforge plugin SemVer MAJOR bump. label-registry-v1 → v2 = contract version-only bump (ADR-037 plugin version bump rule 와 별도 axis). 본 ADR 이 명시.

**12. consumer-side migration 면제** (본 Story scope):
   - mclayer org 만 본 Story 에서 migration. 다른 consumer org (mctrader 등) = audit complete 후 별도 migration CFP.
   - consumer-guide.md 에 label-registry MAJOR bump 영향 + migration plan 안내 (Phase 2 종료 후).

## Amendment 1 (CFP-2251, 2026-06-15) — type:* → native Issue Type 실 org cutover (additive)

ADR-049 본문 §결정 4 (migration script) + §결정 9 (migration timing) 의 **실 실행 결정**. 본문 §결정 1-12 본문 변경 0 (additive ratchet — 기존 결정 축소 없음). mctrader debut audit 후 defer 였던 실 cutover 를 mclayer org 에서 실행한다.

### A1-1. org 재구성 = ADDITIVE (사용자 결정 2026-06-15)

org Issue Type 실측 (2026-06-15, `gh api /orgs/mclayer/issue-types`):

| 기존 org type | id | 처리 |
|---|---|---|
| Task | 28762363 | 보존 (GitHub 기본, cutover 무관) |
| Bug | 28762364 | **재사용** (type:bug 매핑 — 신설 0) |
| Feature | 28762365 | 보존 (GitHub 기본, cutover 무관) |

신설 대상:

| 신설 type | 매핑 label | 처리 |
|---|---|---|
| Story | type:story | org POST 신설 |
| Epic | type:epic | org POST 신설 |

**Audit = deferred** — ADR-049 §결정 1 의 4-type 안 중 Audit 은 본 cutover 미포함 (사용자 결정). 별 CFP carrier 에서 신설. `templates/issue-types.yaml` `_deferred` block 에 박제.

### A1-2. 마이그레이션 대상 = type:* 부착 전체 487 이슈 (open+closed)

`scripts/migrate-label-to-issue-type.sh --dry-run` 실측 (2026-06-15):

| 매핑 | count |
|---|---|
| type:epic → Epic | 46 |
| type:story → Story | 415 |
| type:bug → Bug | 26 |
| **총 대상** | **487** |
| 이미 native type 보유 (skip) | 0 |

PR 은 제외 (REST issues endpoint `.pull_request == null` 필터). idempotent — 재실행 시 이미 변환된 이슈 skip.

### A1-3. label deprecate 타이밍 (transient dual-state — 물리 삭제는 S4 sequencing)

native Issue Type 부착 + `--verify` PASS 완료 (아래 A1-5 실행 결과). **단 type:* 라벨 물리 삭제는 본 Story 에서 하지 않는다** — `story-init.yml` 이 `type:story` 라벨로 트리거되므로 (Issue Form → label → workflow), 라벨을 선삭제하면 story-init 가 깨진다. 따라서:

1. org Story/Epic Issue Type 신설 (Bug 재사용) — **완료**
2. `migrate-label-to-issue-type.sh --apply --batch-size 50` — **완료**
3. `migrate-label-to-issue-type.sh --verify` (불일치 0) — **완료 (PASS)**
4. type:epic / type:story / type:bug 라벨 정의 물리 삭제 + `story-init.yml` 트리거의 native-type 전환 — **S4 (#2252, story-init.yml owner) 로 sequencing.**

**Transient dual-state 허용** (deprecated label + native type 공존) — ADR-049 §결정 11 의 "org Issue Types 미활성 시 graceful fallback = transient dual-state 허용" 과 정합. story-init.yml 의 trigger 가 native type 기준으로 전환 완료될 때까지 type:* 라벨은 존속한다. S4 종료 시점에 비로소 라벨 물리 삭제 + DI-1 invariant (native type + type:* label 동시 존재 금지) 완전 충족.

registry 는 본 Amendment 에서 type:epic/story/bug 에 `replaced_by_native_issue_type` + `deprecated: true` 마킹 추가 (신규 부착 금지 신호). **물리 삭제 ≠ deprecated 마킹** — 마킹은 본 Story 에서, 삭제는 S4 에서.

### A1-4. 실행 권한 경계

- **도구 빌드 + dry-run** = 구현 레인 (본 Amendment + script).
- **org Issue Type 신설 + --apply + (S4 의) label 물리 삭제** = Orchestrator 실행 영역 (org-mutating).

### A1-5. 실행 결과 (2026-06-15, Orchestrator 실행 — 기록용)

| 항목 | 결과 |
|---|---|
| org Story Issue Type 신설 | **완료** — id=34327613 |
| org Epic Issue Type 신설 | **완료** — id=34327614 |
| org Bug Issue Type 재사용 | id=28762364 (신설 0) |
| org type set (실행 후) | [Task, Bug, Feature, Story, Epic] (5-type, additive — 기존 3 보존) |
| migration `--apply` | 487 이슈 변환 (epic 46 / story 415 / bug 26) |
| migration `--verify` | **PASS — 487 정합, 0 불일치** |

**실측 결함 정정 (S4 evidence)**: 빌드 시 `apply_one` 의 부착 payload 가 `--field type_id=<id>` 였으나, REST 가 이를 **silent 무시** (HTTP 2xx 반환하나 type 미설정). 첫 `--apply` 가 487 "성공" 보고 후 `--verify` 가 487 MISMATCH 로 발각. payload 를 `-f type=<TypeName>` (이름 기반) 으로 정정 → 재apply → verify PASS. **동일 결함이 `story-init.yml` L556 (`--field type_id=`) 에도 존재** — 신규 Issue 의 native type 부착이 여태 silent 실패해 왔음. → **S4 (#2252, story-init.yml owner) 에서 정정 대상** (라벨 물리 삭제 + trigger native-type 전환과 동반).

## 결과

### 긍정

- Issue 분류의 native type 보장 (label drift 차단)
- Projects v2 Hierarchy view 활용 가능 (Epic / Story / Sub-issue rollup)
- label-registry contract scope 축소 (type:* 3 entry deprecate → registry 더 명확)
- migration script idempotent + dry-run + rollback = production-grade migration ops 패턴

### 부정 / Trade-off

- label-registry-v1 → v2 MAJOR bump = contract version bump (sibling sync per ADR-010 의무)
- migration timing dependency = mctrader debut audit complete 의무 (사용자 directive)
- org Issue Types 미활성 시 graceful fallback (label hack 사용) = transient dual-state 허용
- Issue Type "Audit" 신규 도입 = 기존 audit label axis 와 명칭 중복 가능성 — `templates/issue-types.yaml` 의 description 명시 의무
- CFP 가 Story sub-category 유지 = sub-issue API 의존 (parent Story 에 attach) — Sub-issues GA 정합

### 영향 받는 영역

- `mclayer/plugin-codeforge` (wrapper):
  - `templates/issue-types.yaml` (신규)
  - `templates/github-issue-forms/{audit,bug,story,cfp-reserve}.yml` (4 file 갱신)
  - `templates/github-workflows/story-init.yml` (갱신)
  - `templates/github-workflows/subissue-from-impl-manifest.yml` (갱신)
  - `scripts/migrate-label-to-issue-type.sh` (신규)
  - `scripts/bootstrap-labels.sh` (갱신 — type:* 3 entry 제거)
  - `docs/inter-plugin-contracts/label-registry-v1.md` (status: Active → Archived)
  - `docs/inter-plugin-contracts/label-registry-v2.md` (신규)
  - `docs/inter-plugin-contracts/MANIFEST.yaml` (label-registry version bump entry 추가)

- `mclayer/plugin-codeforge-pmo` (sibling sync — ADR-010 정합. 현 `plugins/codeforge-pmo/`, 구 repo 삭제됨 2026-06-12):
  - `docs/inter-plugin-contracts/label-registry-v1.md` mirror sync (Active → Archived)
  - `docs/inter-plugin-contracts/label-registry-v2.md` mirror 신설

- consumer projects (mctrader 등):
  - 본 Story scope 0건 (audit complete 후 별도 migration CFP)
  - consumer-guide.md 안내 (Phase 2 종료 후 갱신)

### Migration data integrity (§11 정합)

- **DI-1**: 변환 후 Issue Type + label `type:*` 동시 존재 금지 (cutover invariant)
- **DI-2**: Sub-issue parent 1개 only (GitHub native enforcement)
- **DI-3**: Custom Properties allowed_values change 시 schema breaking — migration script + warning + validation period 의무 (ADR-048 정합)
- **DI-4**: ruleset name uniqueness (ADR-048 정합)

## 해소 기준

N/A — permanent policy



```mermaid
graph TD
    OrgAdmin[Org admin] -->|create| EpicType[Epic Issue Type]
    OrgAdmin -->|create| StoryType[Story Issue Type]
    OrgAdmin -->|create| BugType[Bug Issue Type]
    OrgAdmin -->|create| AuditType[Audit Issue Type]
    EpicIssue[Epic Issue] -->|sub-issue| StoryIssue[Story Issue]
    StoryIssue -->|sub-issue| CFPIssue[CFP Issue<br/>Story sub-category]
    StoryIssue -->|sub-issue| SubIssue[Impl Manifest sub-issue<br/>label: impl-manifest]
    Migration[migrate-label-to-issue-type.sh] -->|dry-run| AuditReview[Audit Issue<br/>label: migration-dry-run-result]
    AuditReview -->|user confirm| Migration
    Migration -->|apply batch 50| Issues[100+ existing Issues]
    Migration -->|rollback batch-id| Issues
    Migration -->|verify| ZeroLabel[type:* 0 잔여 검증]
```

## 관련 파일

- `docs/stories/CFP-140.md` (Story file SSOT — internal-docs `wrapper/stories/CFP-140.md`)
- `docs/change-plans/cfp-140-ghec-governance.md` (Change Plan, internal-docs `wrapper/change-plans/cfp-140-ghec-governance.md`)
- `docs/adr/ADR-048-ghec-governance-as-code.md` (sibling — Rulesets / Required Workflows / Audit log)
- `docs/adr/ADR-008-inter-plugin-contract-versioning.md` (amended by 본 ADR — contract version bump 의 plugin SemVer 와 분리 명시)
- `docs/inter-plugin-contracts/label-registry-v1.md` → `label-registry-v2.md`
