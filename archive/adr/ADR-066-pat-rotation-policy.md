---
adr_number: 66
title: CODEFORGE_CROSS_REPO_PAT rotation policy (lifetime / scope / compromise response / audit)
status: Accepted
category: security
date: 2026-05-13
is_transitional: false
related_files:
  - docs/consumer-guide.md
  - docs/security/pat-rotation-log.md
  - CLAUDE.md
  - templates/github-workflows/phase-gate-mergeable.yml
  - templates/github-workflows/rate-limit-fallback-kpi.yml
related_stories:
  - CFP-450
  - CFP-521
  - CFP-627
  - CFP-743  # Amendment 3 — reconcile PR cross-repo write scope 추가 (Wave 2 Story-3, UpgradeAgent + CLI consumer .github/workflows/ 자동 생성 PR 인증 carrier)
  - CFP-1336  # Amendment 4 — cross-repo label endpoint write scope 추가
  - CFP-2101  # Amendment 5 — classic No-expiration evidence-gated exception (첫 약화 방향 amendment, #2053 outage 복구 정합화)
related_adrs:
  - ADR-013
  - ADR-016
  - ADR-024
  - ADR-037
  - ADR-058
  - ADR-063
  - ADR-064
  - ADR-073  # CFP-627 FIX iter 3 — PAT scope verify discipline 자매 (cross-repo state + assumption verify)
amendments:
  - amendment: 2
    date: 2026-05-14
    cfp: CFP-627
    summary: "§결정 2 scope minimum 3종 → 4종 갱신 — marketplace `contents:read` grant 추가. ADR-063 Amendment 3 §결정 13 (post-rebase — CFP-631 occupied Amendment 2 §결정 11+12) reactive scheduled detection 의 `marketplace-drift-detection.yml` workflow 가 `mclayer/marketplace/.claude-plugin/marketplace.json` fetch 의무 → least-privilege 정합 신규 scope 의무. Strengthening direction only (scope 확장 = consolidation 정합) — ADR-064 top-down ratchet 정합. ADR-013 Amendment 4 단일 PAT consolidation 정책 무변경. Audit log row append placeholder (`docs/security/pat-rotation-log.md` Phase 1 placeholder + Phase 2 actual grant date — Phase 2 PR description checklist forcing function 의무, DesignReview FIX iter 1 F-DR-004 option b)."
    is_transitional: false
    sunset_justification: "N/A — permanent security policy. ADR-058 §결정 7 security ADR default presumption 정합 (is_transitional: false). ADR-064 §self-application top-down ratchet 정합 (Amendment 2 = scope 확장 강화 방향 only). 약화 방향 (scope 축소 / lifetime 연장 / rotation cadence 약화) 발의 차단."
  - amendment: 3
    date: 2026-05-15
    cfp: CFP-743
    summary: "§결정 2 scope minimum 4종 → 5종 갱신 — `reconcile-target-repos contents:write + pull_requests:write` grant 추가. CFP-743 (Wave 2 Story-3) UpgradeAgent + `scripts/codeforge-upgrade.{sh,ps1}` CLI 의 reconcile 가 9 desired_state_domains 중 `github_workflow` / `issue_templates` / `codeowners` 영역 reconcile 시 consumer repo `.github/` 영역에 자동 생성 PR 을 open 해야 함 (reconcile-protocol-v1 §2 desired_state_domains `byte_identical_mirror` / `template_export_manual_instantiate` mode). 현재 4 scope 는 cross-repo Issue comment / sub-issue / marketplace contents:read 만 — consumer repo content write + PR open 권한 부재 (FeasibilityAgent §4.2 MEDIUM 장벽). least-privilege 정합 — scope target = consumer reconcile 대상 repo 한정 (org-wide write 금지), action = `contents:write` (file mirror) + `pull_requests:write` (PR open) 2종만. Strengthening direction only (scope 확장 = ADR-064 top-down ratchet 정합 — weakening 아님). ADR-013 Amendment 4 단일 PAT consolidation 정책 무변경 (별도 PAT 신설 X — 단일 PAT scope 확장). Audit log placeholder row append (`docs/security/pat-rotation-log.md` Phase 1 placeholder + Phase 2 actual grant date — Phase 2 PR description checklist forcing function 의무, Amendment 2 F-DR-004 option b precedent 답습)."
    is_transitional: false
    sunset_justification: "N/A — permanent security policy. ADR-058 §결정 7 security ADR default presumption 정합 (is_transitional: false). ADR-064 §self-application top-down ratchet 정합 (Amendment 3 = scope 확장 강화 방향 only — reconcile target 한정 least-privilege). 약화 방향 (scope 축소 / org-wide write 확대 / lifetime 연장 / rotation cadence 약화) 발의 차단."
  - amendment: 4
    date: 2026-05-24
    cfp: CFP-1336
    summary: "§결정 2 scope minimum 5종 → 6종 갱신 — `cross-repo-target-repos issues:write (label endpoint)` grant 추가. CFP-1336 (Cross-repo bidirectional label sync — wrapper Story Issue ↔ impl repo PR labels) 의 `templates/github-workflows/cross-repo-label-sync.yml` (Wave 2 carrier) workflow 가 cross-repo label state mutation (write) 권한을 요구 — wrapper repo Story Issue label change event 수신 → impl repo PR label sync write + impl repo PR label change event 수신 → wrapper Story Issue label sync write (bidirectional). 현재 5 scope (repo:read / repo:write / metadata:read / marketplace contents:read / reconcile-target-repos contents:write + pull_requests:write) 안 cross-repo label endpoint write 권한 부재 — least-privilege 정합 신규 scope 의무. scope target = `mclayer/plugin-codeforge` (wrapper) ↔ impl repo (consumer Phase 2 PR repo) 한정 (fine-grained PAT repository access list 강제, org-wide write 절대 금지). action = `issues:write` (label endpoint) 1종만 — `contents:write` / `workflows:write` / `admin:*` / `delete_repo` 등 escalation scope 미부여 (self-modification escalation 차단). Strengthening direction only (scope 확장 = ADR-064 top-down ratchet 정합 — weakening 아님). ADR-013 Amendment 4 단일 PAT consolidation 정책 무변경 (별도 PAT 신설 X — 단일 CODEFORGE_CROSS_REPO_PAT scope 확장, 6번째 consumer workflow phase-gate-mergeable.yml / rate-limit-fallback-kpi.yml / marketplace-drift-detection.yml / UpgradeAgent reconcile / 신규 cross-repo-label-sync.yml). paired sibling ADR-073 Amendment 9 §결정 1 (transition trigger `label_change` 9번째 entry, verify subject layer) + ADR-082 Amendment 14 §결정 1 layer 1 sub-scope (1-D) cross-repo label-write authority (write authority layer) — 3 ADR Amendment 동시 발의 (CFP-1336 carrier, axis disjoint complement 3-set: verify subject ↔ write authority ↔ PAT scope grant, ADR-064 §결정 1 CFP scope unitary 정합). Audit log placeholder row append (`docs/security/pat-rotation-log.md` 4번째 row Phase 1 placeholder + Phase 2 actual grant date — Amendment 2/3 precedent 답습, Phase 2 PR description checklist forcing function 의무). CFP-1302 D-4 chief tie-break dissent carry-over F2 carrier — sentinel-driven 아닌 ratchet 확장 carrier."
    is_transitional: false
    sunset_justification: "N/A — permanent security policy. ADR-058 §결정 7 security ADR default presumption 정합 (is_transitional: false). ADR-064 §self-application top-down ratchet 정합 (Amendment 4 = scope 확장 강화 방향 only — cross-repo-target-repos 한정 least-privilege + action 1종만 issues:write label endpoint). 약화 방향 (scope 축소 / org-wide write 확대 / action escalation contents:write 또는 admin / lifetime 연장 / rotation cadence 약화) 발의 차단."
  - amendment: 5
    date: 2026-06-09
    cfp: CFP-2101
    direction: weaken
    summary: "§결정 1 (cadence 90일 권장 / 180일 최대) + §결정 2 (fine-grained 6 scope least-privilege, classic/org-wide 금지) 에 evidence-gated exception clause 추가 — 단일 family dogfood 운영 PAT 의 classic No-expiration + repo/workflow scope 허용 (보상통제 3종 의무). 본 ADR 첫 약화 방향 amendment. §결정 1/2 의 기존 mandate 본문은 폐기 없이 보존 (default 강화 정책 유지) + exception clause 만 append. 약화 대상 = (a) lifetime 무한대 (No-expiration, §결정 1 90/180일 위배) + (b) scope 광역화 (classic `repo`+`workflow`, §결정 2 fine-grained 6 scope + org-wide contents:write 금지 위배) — 2 방향 동시 약화. evidence: #2053 outage — fine-grained ≤90일 회전 friction 이 `story-init` cross-repo write 전면 404 유발 (모든 신규 Story scaffold 차단). 사용자 2026-06-09 classic No-expiration (repo+workflow) 11 repo set 으로 교체 + 검증 완료. 보상통제 3종: (1) §결정 4 leak 즉시 revoke 절차 유지 (무만료라도 compromise 시 T+0 revoke + T+1h rotation 의무 불변) (2) 단일 consolidated PAT (ADR-013 Amendment 4 — 회전/노출 대상 토큰 1개) (3) single-owner dogfood 컨텍스트 (multi-tenant production 아님, 토큰 소유자 = 유일 운영자). §결정 4 (compromise response) / §결정 5 (audit log SSOT) 보존. §결정 7 consumer overlay 강화-only 정책 무변경 — 본 약화는 family 단일 dogfood PAT 한정 exception, consumer 약화 channel 로 전파 금지 (weakening scope 격리 의무). ADR-064 §결정 7 Amendment 8 evidence-gated symmetric ratchet 정합 (약화도 evidence 동반 시 1급) + ADR-058 §결정 5 (재정의 후 — sunset_justification = 약화 evidence requirement, 차단 logic 아님) 정합. Audit log row append (`docs/security/pat-rotation-log.md` 2026-06-09 actual grant row — placeholder 아님, 실 교체 완료) + 이전 active row (2026-05-14 fine-grained PAT) revoked_at 갱신. expiration 계약 3곳(§결정 3 step1 절대형 expiration ≤90일 / §결정 6 reminder workflow expiration parse / audit-log Schema expiration 필드) No-expiration sentinel 정합화 포함 — exception clause 가 lifetime mandate 만 패치하고 No-expiration sentinel 의 데이터 계약 전파를 누락하면 reminder 오발의 / 절차 자기모순 / Schema 위반 발생 (DR FIX iter 1 F-DR-2101-1/2/3 정합)."
    is_transitional: false
    sunset_justification: |
      약화 방향 amendment — ADR-058 §결정 5 (CFP-1149 재정의 후 — sunset_justification = 약화 evidence requirement, 강화 방향 evidence 와 동등 1급 절차) + ADR-064 §결정 7 Amendment 8 (evidence-gated symmetric ratchet — 약화도 evidence 동반 시 1급 허용, 비대칭 제거) 정합. is_transitional: false 유지 (security policy permanent — exception clause 자체가 영구 정책, 안전망 transitional 아님).

      약화 evidence (metric / incident — 강화 방향의 pattern_count / incident 와 동등 1급):
      1. **#2053 outage (incident evidence)** — fine-grained PAT 의 ≤90일 회전 + repository-access-list 관리 friction 이 `CODEFORGE_CROSS_REPO_PAT` 만료/scope 누락 시 cross-repo write 전면 HTTP 404 를 유발. `story-init` 등 모든 신규 Story scaffold cross-repo write 가 차단되어 codeforge dogfood 파이프라인 전면 중단. fine-grained 회전 cadence 의 운영 가용성 비용이 보안 이득을 압도한 실측 사례.
      2. **운영 환경 변화 (environment evidence)** — codeforge family = single-owner dogfood (유일 운영자 `mccho@mclayer.it`, multi-tenant production 아님). multi-tenant 환경이라면 No-expiration + 광역 scope = 부적격이나, single-owner dogfood 의 blast radius 는 운영자 1인으로 bounded — fine-grained 회전의 한계 보안 이득이 단일 운영자 컨텍스트에서 marginal.

      blast radius 보상통제 3종 (약화의 잔존 risk 를 bounded 로 유지 — 무제한 약화 아님):
      1. **§결정 4 leak 즉시 revoke 절차 유지** — No-expiration 이라도 compromise (실수 commit / log 노출 / 운영자 자격 변동) 감지 시 T+0 즉시 revoke + T+1h rotation 의무 불변. 무만료의 무한 compromise window 를 detection→revoke 절차로 상쇄. compromise response 가 lifetime 만료를 대체하는 1차 통제.
      2. **단일 consolidated PAT (ADR-013 Amendment 4)** — 회전/노출 대상 토큰 1개. 광역 classic scope 의 blast radius 가 토큰 다수가 아닌 단일 토큰에 집중 → revoke 시 단일 action 으로 전 표면 무효화 가능 (분산 토큰 대비 incident response 단순).
      3. **single-owner dogfood 컨텍스트** — multi-tenant production 아님. classic `repo` 광역 scope 의 노출 대상 = 운영자 본인 접근 가능 repo (family 11 repo set) 한정, 외부 tenant / 3rd-party 노출 0.

      scope 격리 (약화 전파 차단 — INV): 본 약화는 codeforge family 단일 dogfood PAT 한정 exception. §결정 7 consumer overlay `security.pat_rotation_cadence_days` 강화-only 정책 무변경 — consumer 측은 No-expiration / classic scope 약화 channel 비전파 (weakening scope 격리 의무, consumer-guide cross-ref).

      scope 완결성 (No-expiration sentinel 데이터 계약 전파): 본 약화는 expiration 계약 3곳(§결정 3 step1 rotation 절차 절대형 / §결정 6 자동 만료 reminder workflow parse / audit-log Schema `expiration` 필드 정의)에 No-expiration sentinel 허용 + 처리 규약(reminder skip + §결정 4 revoke 대체 통제 의존) 정합화를 포함한다 — sentinel 을 lifetime mandate 에만 패치하고 데이터 계약 전파를 누락하면 reminder 오발의 / 절차 자기모순 / Schema 위반이 발생 (DR FIX iter 1 F-DR-2101-1/2/3).
mechanical_enforcement_actions: []
---

# ADR-066: CODEFORGE_CROSS_REPO_PAT rotation policy

## 상태

`Accepted` (2026-05-13). CFP-450 (ADR-013 Amendment 4) PAT consolidation 의 lifetime / rotation / compromise response 후속 정책. EPIC-RESULTS CFP-462 §6 carrier #3.

## 컨텍스트

CFP-450 (ADR-013 Amendment 4) 가 `CODEFORGE_CROSS_REPO_PAT` 단일 PAT consolidation 도입. 이 PAT 는 다음 wrapper workflow 에서 사용:

- `phase-gate-mergeable.yml` (cross-repo Story binding sync — internal-docs Story ↔ plugin repo Issue bidirectional link 검증)
- `rate-limit-fallback-kpi.yml` (internal-docs clone, ADR-013 Amendment 4 §결정 — 단일 PAT 재사용 정책)

CFP-450 이 도입한 consolidation 자체는 secret governance 의 첫 단계 (Option B). 그러나 다음 3 영역 미정의:

1. **Rotation policy 부재** — PAT lifetime / rotation schedule / 자동 만료 reminder 미정의 → PAT 가 무기한 사용될 위험
2. **Audit trail 부재** — rotation 시점 / 만료 일자 추적 어려움 → compromise 분석 시 영향 범위 산정 불가
3. **Compromise response 부재** — leak / suspected leak 시 immediate rotation 절차 명문화 안됨 → 사고 시 ad-hoc 대응

본 ADR 이 3 영역 SSOT.

## 결정

### 결정 1 — Rotation cadence (lifetime)

- **권장 rotation cadence**: 90 days (분기별 회전)
- **최대 lifetime**: 180 days (반기 회전 강제 — 본 lifetime 초과 PAT 는 의무 rotation)
- **자동 만료 reminder**: GitHub Actions cron 으로 만료 30 days 전 warning Issue 자동 발의 (Phase 2 carrier — 별도 CFP, 본 ADR `mechanical_enforcement_actions: []` 정합)

90 days 는 GitHub 권장 best practice + codeforge family 의 cross-repo 활성 활동 기간 (CFP cycle 평균 1-2 weeks × 8-10 Story = 분기 1회 회전이 정상 사용 cycle 과 align).

**Exception clause (Amendment 5, CFP-2101 — evidence-gated weakening)**: 위 권장/최대 cadence 는 default mandate 로 유지하되, **단일 family dogfood 운영 PAT 는 classic No-expiration (무만료) 을 허용**한다 — 단 §결정 4 leak 즉시 revoke 절차 유지 + 단일 consolidated PAT + single-owner dogfood 컨텍스트 3 보상통제 동시 충족 시에 한함 (3종 중 1+ 부재 시 본 exception 무효, default cadence 적용). evidence = #2053 outage (fine-grained ≤90일 회전 friction 이 cross-repo write 전면 404 → Story scaffold 전면 차단). ADR-064 §결정 7 Amendment 8 evidence-gated symmetric ratchet + ADR-058 §결정 5 (약화 evidence requirement) 정합. **본 exception 은 codeforge family 단일 dogfood PAT 한정** — §결정 7 consumer overlay (강화-only) 로 전파 금지. 무만료라도 §결정 5 audit log row append + compromise 시 §결정 4 4-step 의무는 불변 (lifetime 만료를 detection→revoke 통제가 대체).

### 결정 2 — Scope minimum (least privilege) (Amendment 4, CFP-1336 — 5종 → 6종 갱신)

PAT 발급 시 다음 6 scope 만 부여:

| Scope | 사용처 | 도입 carrier |
|---|---|---|
| `repo:read` | internal-docs read scan (KPI workflow `rate-limit-fallback-kpi.yml`) | CFP-521 (initial) |
| `repo:write` | cross-repo Issue comment / sub-issue link (`phase-gate-mergeable.yml`) | CFP-521 (initial) |
| `metadata:read` | basic repo access | CFP-521 (initial) |
| **`marketplace contents:read`** | **`marketplace-drift-detection.yml` (CFP-627) — `mclayer/marketplace/.claude-plugin/marketplace.json` fetch** | **CFP-627 ADR-066 Amendment 2 (binds ADR-063 Amendment 3 §결정 13 — post-rebase shift)** |
| **`reconcile-target-repos contents:write + pull_requests:write`** | **`scripts/codeforge-upgrade.{sh,ps1}` + UpgradeAgent (CFP-743) — reconcile 가 9 desired_state_domains 중 `github_workflow` / `issue_templates` / `codeowners` 영역 reconcile 시 consumer reconcile 대상 repo `.github/` 영역에 자동 생성 PR open. scope target = consumer reconcile 대상 repo 한정 (org-wide write 금지), action = `contents:write` (file mirror) + `pull_requests:write` (PR open) 2종만** | **CFP-743 ADR-066 Amendment 3 (binds reconcile-protocol-v1 §2 desired_state_domains `byte_identical_mirror` / `template_export_manual_instantiate` mode)** |
| **`cross-repo-target-repos issues:write (label endpoint)`** | **`cross-repo-label-sync.yml` (CFP-1336 / ADR-073 Amendment 9 + ADR-082 Amendment 14 sub-scope 1-D paired sibling Wave 2 carrier) — cross-repo bidirectional label sync workflow (wrapper repo Story Issue label change event 수신 → impl repo PR label sync write + impl repo PR label change event 수신 → wrapper Story Issue label sync write). scope target = `mclayer/plugin-codeforge` (wrapper) ↔ impl repo (consumer Phase 2 PR repo) 한정 (fine-grained PAT repository access list 강제, org-wide write 절대 금지). action = `issues:write` (label endpoint) 1종만 — `contents:write` / `workflows:write` / `admin:*` / `delete_repo` 등 escalation scope 미부여 (self-modification escalation 차단)** | **CFP-1336 ADR-066 Amendment 4 (binds ADR-073 Amendment 9 §결정 1-A 9번째 entry `label_change` + ADR-082 Amendment 14 §결정 1 layer 1 sub-scope 1-D cross-repo label-write authority — 3 ADR Amendment 동시 발의 axis disjoint complement 3-set)** |

`admin:org` / `delete_repo` / `workflow` / `gist` / org-wide `contents:write` / 기타 광역 scope 부여 금지. `reconcile-target-repos contents:write + pull_requests:write` 는 **fine-grained PAT 의 repository access 를 reconcile 대상 consumer repo 로 명시 제한** (org-wide 금지 — least-privilege 핵심 invariant). 향후 신규 workflow 가 추가 scope 필요 시 별도 ADR 보완 의무.

**Exception clause (Amendment 5, CFP-2101 — evidence-gated weakening)**: 위 fine-grained 6 scope least-privilege 는 default mandate 로 유지하되, **단일 family dogfood 운영 PAT 는 classic PAT 의 `repo` + `workflow` 2 scope 를 허용**한다 — 단 §결정 1 exception clause 와 동일 3 보상통제 (§결정 4 leak 즉시 revoke + 단일 consolidated PAT + single-owner dogfood) 동시 충족 시에 한함. classic `repo` = 운영자 접근 가능 전 repo read/write (org 광역) 로, 본래 §결정 2 가 금지한 "org-wide `contents:write`" 영역에 해당 — least-privilege 의 정면 약화임을 명시 인지. 약화 정당화: #2053 outage 가 fine-grained repository-access-list 누락 (scope 관리 friction) 을 cross-repo write 전면 404 원인 후보로 demonstrate → classic `repo` 광역화가 운영 단순성으로 friction 회피. blast radius 보상 = 단일 토큰 (revoke 1 action 전 표면 무효화) + single-owner (외부 tenant 노출 0) + 즉시 revoke 절차. **본 exception 은 codeforge family 단일 dogfood PAT 한정** — consumer overlay (§결정 7) 비전파. exception 무효 조건 (보상통제 1+ 부재) 시 fine-grained 6 scope default 복귀. ADR-064 §결정 7 Amendment 8 + ADR-058 §결정 5 정합.

**Amendment 2 (CFP-627) rationale**: ADR-063 Amendment 3 §결정 13 (post-rebase — CFP-631 Amendment 2 §결정 11+12 occupied) reactive scheduled detection (`marketplace-drift-detection.yml`) 가 `mclayer/marketplace` repo 의 `marketplace.json` fetch 의무 → least-privilege 정합 신규 scope grant. ADR-013 Amendment 4 (PAT consolidation) 정책 무변경 — 단일 PAT scope 확장 (별도 PAT 신설 X).

**Amendment 3 (CFP-743) rationale (SecurityArch SubAgent perspective primary owner)**:

CFP-743 (Wave 2 Story-3) 가 `scripts/codeforge-upgrade.{sh,ps1}` CLI + UpgradeAgent 를 신설. reconcile-protocol-v1 §2 의 9 desired_state_domains 중 다음 3 영역이 consumer repo `.github/` content write + PR open 을 요구:

- `github_workflow` (`templates/github-workflows/*.yml` → consumer `.github/workflows/*.yml`, `byte_identical_mirror` mode)
- `issue_templates` (`templates/.github/ISSUE_TEMPLATE/*.yml` → consumer `.github/ISSUE_TEMPLATE/*.yml`, `byte_identical_mirror` mode)
- `codeowners` (`templates/CODEOWNERS.template` → consumer `.github/CODEOWNERS`, `template_export_manual_instantiate` mode)

reconcile 의 `--apply` 가 silent direct push 가 아닌 **PR open 경유** (ADR-024 branch governance + ADR-027 consumer adoption 정합 — direct main push 금지, 사용자 review gate 보존). PR open 에는 consumer repo `contents:write` (file mirror to feature branch) + `pull_requests:write` (PR 생성) 2 action 필요. 현재 4 scope (Amendment 2 까지) 는 cross-repo Issue comment / sub-issue / marketplace contents:read 만 — consumer repo content write + PR open 권한 부재 (FeasibilityAgent §4.2 MEDIUM 장벽 — Spec line 120).

**Least-privilege 핵심 결정 (보안 변호자 입장)**:

1. **Scope target 한정** — `reconcile-target-repos` = consumer 가 reconcile 대상으로 명시 등록한 repo 만 (fine-grained PAT 의 repository access list 로 강제). org-wide `contents:write` 절대 금지 — reconcile 무관 repo 노출 차단.
2. **Action 한정 2종** — `contents:write` (file mirror) + `pull_requests:write` (PR open) 만. `workflows:write` / `admin` / `secrets` 등 escalation scope 미부여 — consumer workflow 가 자기 자신을 수정하는 self-modification escalation 차단 (consumer 가 PR review 로 최종 gate).
3. **PR review gate 보존** — reconcile PR 은 자동 merge 아님. consumer 가 PR review 후 merge 결정 (사용자 결정 분기 0 invariant 와 무충돌 — reconcile-protocol-v1 `user_decision_branches: 0` 은 codeforge-upgrade CLI 내부 결정 분기 0 의미이지, consumer governance gate 제거 아님. §7.4 / §7.6 위협↔완화 매핑 참조).
4. **ADR-064 top-down ratchet 정합** — scope 확장은 강화 방향. 단 target/action 한정으로 blast radius 최소화 (scope 확장 ≠ 무제한 권한).

ADR-013 Amendment 4 (PAT consolidation) 정책 무변경 — 단일 PAT scope 확장 (별도 PAT 신설 X — single-PAT consolidation invariant 보존).

**Grant 절차**: 본 ADR-066 §결정 3 5-step rotation 절차 inline trigger (사용자 manual blocker, Phase 2 진입 전 pre-clear). Phase 1 PR audit log entry placeholder (`docs/security/pat-rotation-log.md`) + Phase 2 진입 전 actual grant date 갱신 의무.

**Amendment 4 (CFP-1336) rationale (SecurityArchitectAgent + InfraOperationalArchitectAgent + ArchitectAnalyst integration)**:

CFP-1336 (Cross-repo bidirectional label sync — wrapper Story Issue ↔ impl repo PR labels) 가 cross-repo write 영역의 **두 번째 PAT consumer workflow** 신설 (Amendment 3 의 `reconcile-target-repos contents:write + pull_requests:write` UpgradeAgent reconcile 직후 sequential). `cross-repo-label-sync.yml` (Wave 2 carrier) workflow 는 bidirectional label state mutation 권한 요구 — wrapper repo Story Issue label change event 수신 → impl repo PR label sync write + impl repo PR label change event 수신 → wrapper Story Issue label sync write.

현재 5 scope (Amendment 3 까지) 는 다음 영역 cover:
- `repo:read` (KPI workflow internal-docs scan)
- `repo:write` (cross-repo Issue comment / sub-issue link)
- `metadata:read` (basic repo access)
- `marketplace contents:read` (marketplace.json fetch)
- `reconcile-target-repos contents:write + pull_requests:write` (UpgradeAgent reconcile PR open)

**Cross-repo label endpoint write 권한 부재** — `repo:write` scope 는 same-repo label write 만 (cross-repo Issue comment 영역). cross-repo label endpoint = 별 grant 영역 (GitHub fine-grained PAT scope schema 정합 — `issues:write` permission per-repo grant).

**Least-privilege 핵심 결정 (보안 변호자 입장)**:

1. **Scope target 한정** — `cross-repo-target-repos` = `mclayer/plugin-codeforge` (wrapper, source-of-truth Story Issue) + impl repo (consumer Phase 2 PR repo, bidirectional sync target) 2-repo 한정 (fine-grained PAT 의 repository access list 로 강제). org-wide `issues:write` 절대 금지 — sync 무관 repo 노출 차단.
2. **Action 한정 1종** — `issues:write` (label endpoint) 만. `contents:write` / `workflows:write` / `admin` / `secrets` 등 escalation scope 미부여 — workflow self-modification escalation 차단 (cross-repo-label-sync.yml workflow 가 자기 자신을 수정 / 다른 workflow file 을 수정 / repo 설정 변경하는 escalation 차단). label endpoint = GitHub REST API `POST/DELETE /repos/{owner}/{repo}/issues/{issue_number}/labels` 의 minimum-required scope subset.
3. **4-pattern T-2 self-trigger guard AND invariant 정합** — Amendment 4 scope grant 자체가 T-2 self-trigger loop risk 영역 진입 (cross-repo PAT write = trigger 발화). ADR-073 Amendment 9 §결정 1-N (paired sibling) 의 4-pattern AND guard invariant (sender.type / actor-allowlist / `[skip-cross-repo-sync]` marker / idempotent diff) 가 본 scope grant 의 trigger loop 차단 invariant 보장 — scope grant 자체는 least-privilege 영역, T-2 차단은 별 layer (ADR-082 Amendment 14 sub-scope 1-D + ADR-073 Amendment 9 §결정 1-N 정합).
4. **ADR-064 top-down ratchet 정합** — scope 확장은 강화 방향. 단 target/action 한정으로 blast radius 최소화 (scope 확장 ≠ 무제한 권한, action 1종만 가장 narrow). Amendment 2/3 precedent 답습 (4종 → 5종 → 6종, 각 Amendment 마다 target/action 한정 verify-via design lane review).

**Paired sibling 3 ADR Amendment 동시 발의** (CFP-1336 carrier, axis disjoint complement 3-set):

- 본 Amendment 4 (ADR-066) = **PAT scope grant layer** (least-privilege scope minimum 6번째 entry, fine-grained PAT repository access list 강제)
- ADR-073 Amendment 9 = **verify subject layer** (Orchestrator self-assertion verify, transition trigger `label_change` 9번째 entry)
- ADR-082 Amendment 14 = **write authority layer** (internal lane agent self-write authority 4-tuple verify, sub-scope 1-D)

3 layer disjoint codify — 단일 super-class "cross-repo bidirectional label sync" 의 3 layer 분리 (ADR-064 §결정 1 CFP scope unitary 정합).

ADR-013 Amendment 4 (PAT consolidation) 정책 무변경 — 단일 PAT scope 확장 (별도 PAT 신설 X — single-PAT consolidation invariant 보존, 6번째 consumer workflow `cross-repo-label-sync.yml` 추가).

**Grant 절차 (Amendment 4)**: 본 ADR-066 §결정 3 5-step rotation 절차 inline trigger (사용자 manual blocker, Phase 2 (CFP-1336 Wave 2 carrier) 진입 전 pre-clear). Phase 1 PR audit log entry placeholder (`docs/security/pat-rotation-log.md` 4번째 row) + Phase 2 진입 전 actual grant date 갱신 의무 (Amendment 2/3 placeholder pattern verbatim 답습).

### 결정 3 — Rotation 절차 (5-step)

1. **New PAT 발급** — GitHub Personal access tokens (classic 또는 fine-grained), 위 §결정 2 scope, expiration ≤ 90 days. 단 단일 family dogfood 운영 PAT 가 §결정 1/§결정 2 exception clause (classic No-expiration + `repo`/`workflow` scope) 를 적용하는 경우 expiration = `No-expiration` 허용 (Amendment 5, CFP-2101 — 보상통제 3종 §결정 4 leak 즉시 revoke + 단일 consolidated PAT + single-owner dogfood 동시 충족 조건). 이 경우 step 5 revoke 는 lifetime 만료가 아닌 §결정 4 compromise response 가 대체 통제 (만료 없음 → 정기 rotation step 면제, leak 시 revoke 의무만 불변).
2. **mclayer org secrets 갱신** — `Settings > Secrets > Actions > CODEFORGE_CROSS_REPO_PAT` (org level)
3. **sibling repo verification** — 7 repo 의 org secret 가시성 확인 (`codeforge-{requirements,design,develop,test,review,pmo}` + `marketplace` + `codeforge-internal-docs`). org level secret 이므로 개별 repo 갱신 불필요 (org → repo 자동 inherit).
4. **1-2 PR 테스트** — `phase-gate-mergeable.yml` 또는 KPI workflow 가 active 한 1 PR 에서 동작 확인 (workflow run success).
5. **이전 PAT revoke** — GitHub Personal access tokens settings 에서 이전 PAT 즉시 revoke. 동시에 §결정 5 audit log row append.

### 결정 4 — Compromise response (leak / suspected leak 시 4-step)

PAT leak / suspected leak (e.g., 실수 commit / log 노출 / org member 이탈) 감지 시:

1. **Immediate revoke** — GitHub UI > Personal access tokens > Revoke 즉시 실행 (시간 = T+0).
2. **Within 1h rotation** — New PAT 발급 + §결정 3 절차 5-step 실행 (T+1h 까지 완료).
3. **Audit 영향 범위 검토** — 영향 받은 workflow run / Issue comment / PR comment / sub-issue link 검토 (`gh api` 활용). 의심 활동 1차 식별.
4. **Disclosure 판단** — 영향 범위에 따라 사용자 / 외부 통보 (private repo data leak 가능성 시 즉시 disclosure 의무).

### 결정 5 — Audit log SSOT

- **Audit log 위치**: `docs/security/pat-rotation-log.md` (본 PR 신설).
- **Schema**: rotation history 표 — `rotated_at (KST) | by | reason | expiration | revoked_at`.
- **Write 책임**: 사용자 manual entry 의무 — PAT 발급 절차 자체가 GitHub UI 의존 (자동화 불가).
- **Rotation 시점**: 위 §결정 3 step 5 직후 새 row append + 이전 row 의 `revoked_at` 갱신 의무.
- **첫 row**: CFP-450 initial issuance 시점 (2026-05-12, expiration TBD 사용자 확인 의무).

### 결정 6 — 자동화 carrier (Phase 2 후속)

본 ADR 은 **정책 SSOT 만**. Mechanical enforcement (자동 만료 reminder workflow + audit log lint) 는 Phase 2 carrier (별도 CFP):

- **자동 만료 reminder workflow**: GitHub Actions cron (weekly) 가 `docs/security/pat-rotation-log.md` 최신 row 의 `expiration` 필드 parse → 30 days 이내 warning Issue 자동 발의. Phase 2 carrier 도입 시 본 ADR `mechanical_enforcement_actions[]` row append (ADR-040 Amendment 3 §결정 7 정합).
  - **No-expiration sentinel 처리 규약 (Amendment 5, CFP-2101)**: 최신 row 의 `expiration` 이 sentinel `No-expiration` (§결정 1/§결정 2 evidence-gated exception 적용 row) 인 경우 reminder parse 에서 **skip** (만료 없음 → 30 days reminder 대상 아님 — date parse 실패로 인한 오발의 / 침묵 차단). 단 No-expiration 활성 동안 compromise 미탐지 보상 = §결정 4 leak 즉시 revoke (T+0) + T+1h rotation 절차에 의존함을 명시 (lifetime 만료가 제공하던 compromise window 상한을 detection→revoke 통제가 대체). Phase 2 carrier 는 본 skip 분기 + sentinel 인지 로직을 상속 의무 (§결정 6 = Phase 2 미빌드 carrier 가 상속할 계약 정의).
- **Audit log schema lint**: `scripts/check-pat-rotation-log.sh` (Phase 2) — row format / KST timezone / 정렬 순서 검증.

본 ADR `mechanical_enforcement_actions: []` (Phase 2 carrier 도입 전까지 빈 array). evidence-enforceable framework (ADR-060) warning tier 첫 entry 는 Phase 2 PR 에서 추가.

### 결정 7 — Consumer overlay 영향

본 ADR 정책은 codeforge family 의 `CODEFORGE_CROSS_REPO_PAT` 에 한정 (wrapper + 6 lane plugin + marketplace + internal-docs). Consumer project 가 자체 cross-repo PAT 사용 시:

- Consumer overlay (`.claude/_overlay/project.yaml`) `security.pat_rotation_cadence_days` 필드로 cadence override 가능 (강화 방향만 — 90 days 미만 short rotation 허용, 90 days 초과 weaken 금지).
- Consumer 자체 PAT 의 audit log 는 consumer repo `docs/security/` (overlay 영역, codeforge 가 강제 안 함).
- 본 ADR §결정 4 compromise response 4-step 은 normative — consumer 도 동일 절차 권장 (consumer-guide cross-ref).

## 대안

- **무한 lifetime PAT** (현재 상태) — rotation 부재. compromise 영향 범위 산정 불가. 기각 (CFP-450 consolidation 의 본래 목적과 충돌).
- **30 days short rotation** — GitHub best practice 더 보수적. 기각 (codeforge family 활성 활동 cycle 분기 1회 align 우선 — sustainability vs security tradeoff, 90 days 가 derived default).
- **Per-workflow PAT** (consolidation 무효화) — CFP-450 (ADR-013 Amendment 4) 와 정면 충돌. 기각.
- **Automated rotation via GitHub API** — GitHub fine-grained PAT 가 API rotation 미지원 (2026-05 시점). 기각 (Phase 2 carrier 도 manual + reminder hybrid).

## 결과

### 도입 효과

- `CODEFORGE_CROSS_REPO_PAT` lifetime 명시 (90 days 권장 / 180 days 최대) → compromise 영향 범위 bounded.
- Audit log SSOT (`docs/security/pat-rotation-log.md`) 신설 → rotation 시점 추적 가능.
- Compromise response 4-step 명문화 → 사고 시 ad-hoc 대응 → 정형 절차.
- Consumer overlay 강화 방향 허용 (cadence override) → security 강화 channel.

### 영향 범위

- wrapper repo (본 ADR carrier).
- 6 lane plugin + marketplace + internal-docs (PAT 사용 영역 — workflow 변경 0건, 정책 SSOT 만).
- Consumer project (consumer-guide cross-ref + overlay schema 확장 channel).

### 후속 carrier

- **Phase 2 CFP-TBD**: 자동 만료 reminder workflow + audit log lint script + evidence-checks-registry warning tier entry.
- **Consumer overlay schema 갱신**: `docs/project-config-schema.md` `security.pat_rotation_cadence_days` field 추가 (별도 CFP).

## ADR-073 cross-ref (Orchestrator verify-before-assert)

본 ADR 의 `CODEFORGE_CROSS_REPO_PAT` 영역 = **external service auth state verify 영역**. ADR-073 (Orchestrator verify-before-assert, CFP-622) §결정 1 cross-repo state 단정 의무 + assumption verify 의무 적용 — Orchestrator 가 PAT scope / 만료 일자 / 활성 상태 단정 시 GitHub PAT settings 또는 audit log SSOT (`docs/security/pat-rotation-log.md`) direct verify + `verified-via` annotation 의무.

본 ADR 영역 적용 예:
- "PAT 만료 일자 = 2026-08-12" 단정 시 → `git show origin/main:docs/security/pat-rotation-log.md` direct verify + `verified-via: pat-rotation-log.md row N` annotation
- "PAT scope = `repo` + `workflow` + `read:org` + `marketplace:contents:read`" 단정 시 → GitHub PAT settings UI screenshot 또는 audit log latest row verify

ADR-073 §결정 1 self-application = 본 ADR Amendment 2 §결정 2 scope minimum 4종 verify 의무 영역. PAT 발급 시점 ↔ Phase 2 carrier scheduled cron 활성 시점 사이 audit log placeholder row append 의무 (Phase 1 → Phase 2 carrier 동기화 시).

## 해소 기준


N/A — permanent policy
N/A — `is_transitional: false` (permanent policy, ADR-058 보안 default presumption 정합).

본 정책은 codeforge family 가 `CODEFORGE_CROSS_REPO_PAT` 를 사용하는 한 영구 유지. 단 다음 2 사유 발생 시 amendment 의무:

- GitHub PAT 모델 자체 변경 (e.g., fine-grained PAT 의 API rotation 지원 도입 시) → §결정 6 자동화 carrier 절차 갱신.
- PAT consolidation 정책 변경 (CFP-450 / ADR-013 Amendment 4 revoke) → 본 ADR scope 축소 / archive.

## 관련 파일

- [`docs/consumer-guide.md`](../consumer-guide.md) §1.f — Consumer-facing 정책 mirror
- [`docs/security/pat-rotation-log.md`](../security/pat-rotation-log.md) — Audit log SSOT
- [`CLAUDE.md`](../../CLAUDE.md) — wrapper Orchestrator 인지용 cross-ref
- [`templates/github-workflows/phase-gate-mergeable.yml`](../../templates/github-workflows/phase-gate-mergeable.yml) — PAT 사용 workflow 1
- [`templates/github-workflows/rate-limit-fallback-kpi.yml`](../../templates/github-workflows/rate-limit-fallback-kpi.yml) — PAT 사용 workflow 2
- [`ADR-013 Amendment 4`](ADR-013-codeforge-family-dogfood-out-policy.md) — PAT consolidation carrier (CFP-450)
- [`ADR-058`](ADR-058-adr-sunset-criteria-mandate.md) — security default `is_transitional: false`
- [`ADR-063`](ADR-063-marketplace-atomic-invariant.md) — `hotfix-bypass:marketplace-atomic` (본 PR 적용)
- [`ADR-064`](ADR-064-decision-principle-mandate.md) — derived default 적용 근거
